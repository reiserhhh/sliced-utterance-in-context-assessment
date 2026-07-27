"""Tests for V3.7H.1 projection and cumulative-path diagnostics."""
from __future__ import annotations

import numpy as np

from suica_core.v8_resolution_filtration_h1 import (
    PairedScheduleSpec,
    cumulative_kappa,
    fit_fixed_linear_cumulative_predictor,
    fit_joint_cumulative_predictor,
    initial_observable_history,
    paired_schedule_excess,
    predict_joint_cumulative,
    score_space_response_ratio,
    score_paired_schedule_panel,
    scorer_projection_metrics,
    simulate_paired_schedule_panel,
    simulate_schedule_calibration_context,
)
from suica_core.v8_resolution_filtration import (
    fit_joint_resolution_family,
    resolution_candidates,
)


def test_projection_identity_is_algebraically_exact() -> None:
    rng = np.random.default_rng(38_110)
    truth = rng.normal(size=(64, 8))
    left = truth + rng.normal(scale=0.4, size=truth.shape)
    right = truth + rng.normal(scale=0.2, size=truth.shape)
    metrics = scorer_projection_metrics(
        truth,
        left,
        right,
        origin=np.zeros(8),
    )
    assert metrics["projection_algebra_error"] < 1e-12
    assert np.isclose(
        metrics["projection_defect"],
        metrics["posterior_orthogonality"],
    )


def test_initial_history_has_three_nonredundant_views() -> None:
    rng = np.random.default_rng(38_120)
    sessions = rng.normal(size=(32, 4, 3, 6))
    score = rng.normal(size=(32, 6))
    unresolved = rng.normal(size=(32, 6))
    history = initial_observable_history(
        sessions,
        score,
        unresolved,
        external_zero=np.zeros(6),
    )
    assert history.shape == (32, 18)
    assert np.array_equal(history[:, :6], score)
    assert np.array_equal(history[:, 6:12], unresolved)
    assert np.array_equal(
        history[:, 12:],
        sessions[:, 0, 0] - sessions[:, 1, 0],
    )


def test_joint_cumulative_predictor_detects_shared_path_rule() -> None:
    rng = np.random.default_rng(38_130)
    probe_x = rng.normal(size=(180, 12))
    evaluation_x = rng.normal(size=(120, 12))
    maps = [rng.normal(size=(12, 5)) for _ in range(3)]
    probe_targets = [probe_x @ value for value in maps]
    evaluation_targets = [evaluation_x @ value for value in maps]
    fitted = fit_joint_cumulative_predictor(
        probe_x,
        probe_targets,
        seed=38_131,
        folds=3,
        alphas=(1.0, 10.0),
        ranks=(4, 8),
        rff_components=64,
    )
    predictions = predict_joint_cumulative(fitted, evaluation_x)
    kappas = [
        cumulative_kappa(target, prediction)
        for target, prediction in zip(
            evaluation_targets,
            predictions,
            strict=True,
        )
    ]
    assert len(predictions) == 3
    assert min(kappas) > 0.90
    assert np.isfinite(fitted["table"]["cv_kappa_pooled"]).all()

    fixed = fit_fixed_linear_cumulative_predictor(
        probe_x,
        probe_targets,
        alpha=1.0,
    )
    fixed_predictions = predict_joint_cumulative(fixed, evaluation_x)
    assert min(
        cumulative_kappa(target, prediction)
        for target, prediction in zip(
            evaluation_targets,
            fixed_predictions,
            strict=True,
        )
    ) > 0.90


def test_joint_cumulative_predictor_does_not_invent_random_path() -> None:
    rng = np.random.default_rng(38_140)
    probe_x = rng.normal(size=(180, 10))
    evaluation_x = rng.normal(size=(120, 10))
    probe_targets = [rng.normal(size=(180, 4)) for _ in range(2)]
    evaluation_targets = [rng.normal(size=(120, 4)) for _ in range(2)]
    fitted = fit_joint_cumulative_predictor(
        probe_x,
        probe_targets,
        seed=38_141,
        folds=3,
        alphas=(10.0, 100.0),
        ranks=(4,),
        rff_components=48,
    )
    predictions = predict_joint_cumulative(fitted, evaluation_x)
    kappas = [
        cumulative_kappa(target, prediction)
        for target, prediction in zip(
            evaluation_targets,
            predictions,
            strict=True,
        )
    ]
    assert max(kappas) < 0.20


def test_paired_schedule_excess_separates_null_and_drift() -> None:
    spec = PairedScheduleSpec(
        dimension=8,
        budgets=(8, 16, 32),
        reference_authors=160,
        calibration_authors=180,
        panel_authors=400,
        opportunity_start=8,
    )
    context = simulate_schedule_calibration_context(seed=38_150, spec=spec)
    zero = context["reference"][:, :, -1].mean(axis=(0, 1))
    fitted, _, _ = fit_joint_resolution_family(
        context["calibration"],
        budgets=spec.budgets,
        external_zero=zero,
        candidates=resolution_candidates(),
        folds=3,
        seed=38_151,
        noise_shrinkage=0.25,
    )
    null = simulate_paired_schedule_panel(
        context,
        seed=38_152,
        geometry="random_rotation",
        eta=0.0,
        drift_schedule_b=False,
    )
    drift = simulate_paired_schedule_panel(
        context,
        seed=38_153,
        geometry="random_rotation",
        eta=0.10,
        drift_schedule_b=True,
    )
    null_scores = score_paired_schedule_panel(
        null["values"],
        fitted,
        budgets=spec.budgets,
    )
    drift_scores = score_paired_schedule_panel(
        drift["values"],
        fitted,
        budgets=spec.budgets,
    )
    null_q = paired_schedule_excess(
        null_scores,
        fitted,
        budget_index=2,
        budget=32,
    )["schedule_excess_q"]
    drift_q = paired_schedule_excess(
        drift_scores,
        fitted,
        budget_index=2,
        budget=32,
    )["schedule_excess_q"]
    score_eta = score_space_response_ratio(
        drift["response"],
        fitted[32],
        fraction=float(drift["fractions"][-1]),
    )
    assert context["maximum_prefix_identity_error"] < 1e-10
    assert null["prefix_identity_error"] < 1e-10
    assert abs(drift["achieved_eta"] - 0.10) < 0.03
    # Q is an untruncated variance-component estimate, so a finite null panel
    # may be negative. The registered refusal rule is one-sided.
    assert null_q < 0.01
    assert drift_q > 0.01
    assert drift_q > null_q + 0.03
    assert 0.03 < score_eta < 0.12
