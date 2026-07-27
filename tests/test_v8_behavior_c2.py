"""Tests for the V8 behavior C2 planted-world estimator."""
from __future__ import annotations

import numpy as np

from suica_core.v8_behavior_c2 import (
    C2SimulationSpec,
    evaluate_c2_pipeline,
    factorial_condition_basis,
    fit_c2_pipeline,
    identification_status,
    simulate_c2_world,
)


def test_c2_identification_requires_shared_ranked_conditions() -> None:
    basis = factorial_condition_basis()
    opportunity = np.ones((8, 5), dtype=bool)
    ready = identification_status(
        basis,
        opportunity,
        np.ones(8, dtype=bool),
        condition_identity_shared=True,
    )
    sparse = identification_status(
        basis,
        opportunity,
        np.arange(8) < 4,
        condition_identity_shared=True,
    )
    private = identification_status(
        basis,
        opportunity,
        np.ones(8, dtype=bool),
        condition_identity_shared=False,
    )
    assert ready["status"] == "C2_IDENTIFIABLE"
    assert sparse["status"] == "REFUSE_INSUFFICIENT_COMMON_SUPPORT_OR_RANK"
    assert private["status"] == "REFUSE_CONDITION_IDENTITY_NOT_SHARED"


def test_c2_pipeline_recovers_shapes_and_refuses_private_coordinates() -> None:
    spec = C2SimulationSpec(
        discovery_authors=15,
        calibration_authors=8,
        confirmation_authors=12,
        extra_repeats=24,
    )
    world = simulate_c2_world(
        seed=17,
        world="shared_c2",
        observation="soft",
        snr=1.0,
        overlap=1.0,
        spec=spec,
    )
    estimate = fit_c2_pipeline(
        world,
        cell_mean_key="fixed_mean",
        ridge_candidates=(0.0, 1.0),
    )
    result = evaluate_c2_pipeline(
        world,
        estimate,
        seed=18,
        bootstrap_draws=49,
        permutations=49,
    )
    assert estimate["status"] == "C2_ESTIMATE_READY"
    assert estimate["surface"].shape[:2] == (spec.authors, 2)
    assert estimate["oracle_surface"].shape == estimate["surface"].shape
    assert estimate["response_se"].shape == estimate["surface"].shape
    assert np.all(estimate["response_se"] >= 0)
    assert result["c2_numeric_output"] is True
    assert 0.0 <= result["response_pointwise_ci_coverage"] <= 1.0
    assert np.isnan(result["moment_same_author_auc"])

    private = simulate_c2_world(
        seed=19,
        world="private_stable_coordinates",
        observation="soft",
        snr=1.0,
        overlap=1.0,
        spec=spec,
    )
    refused = fit_c2_pipeline(
        private,
        cell_mean_key="fixed_mean",
        ridge_candidates=(0.0, 1.0),
    )
    assert refused["status"] == "REFUSE_CONDITION_IDENTITY_NOT_SHARED"


def test_binary_c2_uses_link_operator_and_reports_moment_sensitivity() -> None:
    spec = C2SimulationSpec(
        discovery_authors=15,
        calibration_authors=8,
        confirmation_authors=12,
        extra_repeats=24,
    )
    world = simulate_c2_world(
        seed=23,
        world="shared_c2",
        observation="binary",
        snr=1.0,
        overlap=1.0,
        spec=spec,
    )
    estimate = fit_c2_pipeline(
        world,
        cell_mean_key="fixed_mean",
        ridge_candidates=(0.0, 1.0),
    )
    result = evaluate_c2_pipeline(
        world,
        estimate,
        seed=24,
        bootstrap_draws=49,
        permutations=49,
        binary_ci_bootstrap_draws=7,
        binary_ci_bootstrap_authors=4,
    )
    assert estimate["estimand"] == "C2_LOGIT_OPERATOR"
    assert estimate["inference_method"] == "FIRTH_BINOMIAL_LINK"
    assert estimate["oracle_surface"].shape == estimate["surface"].shape
    assert np.isfinite(result["moment_same_author_auc"])
    assert np.isfinite(result["moment_response_surface_cosine"])
    assert np.isfinite(result["probability_incidence_same_author_auc"])
    assert np.isfinite(result["binary_parametric_ci_coverage"])


def test_binary_primary_score_uses_fixed_quota_under_c1_imbalance() -> None:
    spec = C2SimulationSpec(
        discovery_authors=15,
        calibration_authors=8,
        confirmation_authors=12,
        forced_repeats=6,
        extra_repeats=24,
    )
    world = simulate_c2_world(
        seed=29,
        world="c1_information_imbalance",
        observation="binary",
        snr=0.5,
        overlap=1.0,
        spec=spec,
    )
    fixed_trials = world["data"]["fixed_trials"]
    all_trials = world["data"]["all_trials"]
    assert np.array_equal(
        np.unique(fixed_trials),
        np.asarray([spec.forced_repeats]),
    )
    assert float(np.std(all_trials)) > 0.0


def test_extreme_prevalence_preserves_score_and_refuses_inference() -> None:
    spec = C2SimulationSpec(
        discovery_authors=15,
        calibration_authors=8,
        confirmation_authors=12,
        extra_repeats=24,
    )
    world = simulate_c2_world(
        seed=31,
        world="extreme_prevalence",
        observation="binary",
        snr=0.5,
        overlap=1.0,
        spec=spec,
    )
    estimate = fit_c2_pipeline(
        world,
        cell_mean_key="fixed_mean",
        ridge_candidates=(0.0, 1.0),
    )
    result = evaluate_c2_pipeline(
        world,
        estimate,
        seed=32,
        bootstrap_draws=19,
        permutations=19,
    )
    assert result["c2_numeric_output"] is True
    assert np.isfinite(result["same_author_auc"])
    assert result["inference_author_half_refusal_rate"] >= 0.95
    assert np.isnan(result["response_pointwise_ci_coverage"])
