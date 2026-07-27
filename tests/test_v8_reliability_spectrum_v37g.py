"""Tests for V3.7G reliability-spectrum measurement mechanics."""
from __future__ import annotations

import numpy as np

from suica_core.v8_reliability_spectrum import (
    ReliabilitySpectrumWorldSpec,
    apply_spectrum_operator,
    default_spectrum_candidates,
    estimate_external_origin,
    fit_reliability_spectrum,
    minimum_risk_hard_candidate,
    model_assisted_conditional_region,
    one_se_hard_candidate,
    select_spectrum_candidate,
    simulate_reliability_spectrum_world,
    spectrum_operator,
    spectrum_weights,
    stable_variance_spectrum,
    unresolved_channel,
)
from suica_core.v8_reliability_spectrum import _tolerance_order


def test_registered_spectra_separate_exact_dense_and_broken() -> None:
    exact = stable_variance_spectrum("exact_rank12", 48)
    dense = stable_variance_spectrum("dense_tail48", 48)
    broken = stable_variance_spectrum("broken_spectrum48", 48)
    assert np.count_nonzero(exact) == 12
    assert np.all(dense > 0.0)
    assert np.all(np.diff(dense) < 0.0)
    assert np.isclose(
        dense[-1],
        (1.0 + 48.0 / 4.0) ** -1.50,
    )
    assert len(np.unique(broken)) >= 5


def test_score_and_unresolved_channels_reconstruct_profile() -> None:
    rng = np.random.default_rng(37_801)
    stable = rng.normal(size=(96, 12))
    left = stable + rng.normal(scale=0.3, size=stable.shape)
    right = stable + rng.normal(scale=0.3, size=stable.shape)
    zero = np.zeros(12)
    spectrum = fit_reliability_spectrum(
        left,
        right,
        external_zero=zero,
    )
    candidate = {"family": "wiener", "tau": 1.0, "name": "w"}
    fitted = spectrum_operator(spectrum, candidate)
    score = apply_spectrum_operator(left, fitted)
    unresolved = unresolved_channel(left, fitted)
    assert np.allclose(score + unresolved, left)


def test_spectrum_uses_external_origin_second_moment_with_n_denominator() -> None:
    left = np.asarray([[1.0, 0.0], [0.0, 2.0]])
    right = left.copy()
    fitted = fit_reliability_spectrum(
        left,
        right,
        external_zero=np.zeros(2),
    )
    expected = left.T @ right / len(left)
    assert np.allclose(fitted["stable_second_moment"], expected)
    assert np.allclose(fitted["event_second_moment"], 0.0)


def test_spectrum_weights_are_bounded_and_monotone() -> None:
    eta = np.geomspace(100.0, 1e-4, 48)
    for candidate in default_spectrum_candidates(48):
        weights = spectrum_weights(eta, candidate)
        assert np.all((0.0 <= weights) & (weights <= 1.0))
        assert np.all(np.diff(weights) <= 1e-10)


def test_registered_95_95_tolerance_order_is_exact() -> None:
    order, achieved = _tolerance_order(
        192,
        content=0.95,
        confidence=0.95,
    )
    assert order == 188
    assert 0.95 <= achieved < 0.97


def test_world_panels_are_disjoint_shapes_and_external_origin_is_finite() -> None:
    spec = ReliabilitySpectrumWorldSpec(
        reference_authors=32,
        calibration_authors=28,
        interval_authors=24,
        evaluation_authors=20,
        event_budget=64,
    )
    world = simulate_reliability_spectrum_world(
        latent_seed=37_802,
        event_seed=37_803,
        spec=spec,
    )
    assert world["panels"]["reference"].shape == (32, 4, 48)
    assert world["panels"]["evaluation"].shape == (20, 4, 48)
    origin = estimate_external_origin(world["panels"]["reference"])
    assert np.isfinite(origin).all()


def test_latent_truth_is_fixed_while_event_noise_changes_across_budgets() -> None:
    shared = dict(
        world="dense_tail48",
        reference_authors=32,
        calibration_authors=28,
        interval_authors=24,
        evaluation_authors=20,
    )
    low_budget = simulate_reliability_spectrum_world(
        latent_seed=37_812,
        event_seed=37_813,
        spec=ReliabilitySpectrumWorldSpec(
            event_budget=64,
            **shared,
        ),
    )
    high_budget = simulate_reliability_spectrum_world(
        latent_seed=37_812,
        event_seed=37_814,
        spec=ReliabilitySpectrumWorldSpec(
            event_budget=256,
            **shared,
        ),
    )
    for panel in ("reference", "calibration", "interval", "evaluation"):
        assert np.array_equal(
            low_budget["truths"][panel],
            high_budget["truths"][panel],
        )
        assert not np.array_equal(
            low_budget["panels"][panel],
            high_budget["panels"][panel],
        )


def test_unidentified_state_and_reference_transport_refuse_intervals() -> None:
    common = dict(
        reference_authors=24,
        calibration_authors=24,
        interval_authors=24,
        evaluation_authors=24,
    )
    core = simulate_reliability_spectrum_world(
        latent_seed=37_815,
        event_seed=37_816,
        spec=ReliabilitySpectrumWorldSpec(
            world="dense_tail48",
            **common,
        ),
    )
    state = simulate_reliability_spectrum_world(
        latent_seed=37_817,
        event_seed=37_818,
        spec=ReliabilitySpectrumWorldSpec(
            world="dense_state_alias",
            **common,
        ),
    )
    shifted = simulate_reliability_spectrum_world(
        latent_seed=37_819,
        event_seed=37_820,
        spec=ReliabilitySpectrumWorldSpec(
            world="reference_shift_dense",
            **common,
        ),
    )
    assert core["design"]["interval_claim_allowed"]
    assert not state["design"]["interval_claim_allowed"]
    assert not shifted["design"]["interval_claim_allowed"]
    assert "STATE" in state["design"]["interval_claim_status"]
    assert "REFERENCE_TRANSPORT" in shifted["design"]["interval_claim_status"]


def test_candidate_selection_uses_later_sessions() -> None:
    world = simulate_reliability_spectrum_world(
        latent_seed=37_804,
        event_seed=37_805,
        spec=ReliabilitySpectrumWorldSpec(
            world="exact_rank12",
            reference_authors=48,
            calibration_authors=64,
            interval_authors=32,
            evaluation_authors=32,
            event_budget=128,
        ),
    )
    zero = estimate_external_origin(world["panels"]["reference"])
    selected, table = select_spectrum_candidate(
        world["panels"]["calibration"],
        external_zero=zero,
        candidates=default_spectrum_candidates(48),
        folds=4,
        seed=37_806,
        noise_shrinkage=0.25,
    )
    assert selected["name"] in set(table["name"])
    assert table["selected"].sum() == 1
    assert np.isfinite(table["mean_loss"]).all()


def test_hard_comparator_uses_one_se_lowest_capacity() -> None:
    import pandas as pd

    table = pd.DataFrame([
        {
            "name": "hard_r4",
            "family": "hard",
            "mean_loss": 0.21,
            "se_loss": 0.02,
            "mean_effective_df": 4.0,
        },
        {
            "name": "hard_r8",
            "family": "hard",
            "mean_loss": 0.20,
            "se_loss": 0.02,
            "mean_effective_df": 8.0,
        },
        {
            "name": "hard_r12",
            "family": "hard",
            "mean_loss": 0.19,
            "se_loss": 0.03,
            "mean_effective_df": 12.0,
        },
    ])
    assert minimum_risk_hard_candidate(table) == "hard_r12"
    assert one_se_hard_candidate(table) == "hard_r4"


def test_permuted_sessions_select_less_information_than_exact_world() -> None:
    spec = dict(
        reference_authors=64,
        calibration_authors=96,
        interval_authors=48,
        evaluation_authors=48,
        event_budget=128,
    )
    exact = simulate_reliability_spectrum_world(
        latent_seed=37_807,
        event_seed=37_808,
        spec=ReliabilitySpectrumWorldSpec(
            world="exact_rank12",
            **spec,
        ),
    )
    permuted = simulate_reliability_spectrum_world(
        latent_seed=37_807,
        event_seed=37_808,
        spec=ReliabilitySpectrumWorldSpec(
            world="author_permutation",
            **spec,
        ),
    )
    candidates = default_spectrum_candidates(48)

    def selected_df(world: dict[str, object]) -> float:
        panels = world["panels"]
        zero = estimate_external_origin(panels["reference"])
        selected, _ = select_spectrum_candidate(
            panels["calibration"],
            external_zero=zero,
            candidates=candidates,
            folds=4,
            seed=37_809,
            noise_shrinkage=0.25,
        )
        spectrum = fit_reliability_spectrum(
            panels["calibration"][:, 0],
            panels["calibration"][:, 1],
            external_zero=zero,
        )
        return float(spectrum_operator(
            spectrum,
            selected,
        )["effective_df"])

    assert selected_df(permuted) < selected_df(exact)


def test_conditional_region_has_no_truth_or_coverage_interface() -> None:
    world = simulate_reliability_spectrum_world(
        latent_seed=37_810,
        event_seed=37_811,
        spec=ReliabilitySpectrumWorldSpec(
            world="dense_tail48",
            dimension=8,
            reference_authors=64,
            calibration_authors=72,
            interval_authors=128,
            evaluation_authors=48,
            event_budget=128,
        ),
    )
    panels = world["panels"]
    zero = estimate_external_origin(panels["reference"])
    spectrum = fit_reliability_spectrum(
        panels["calibration"][:, 0],
        panels["calibration"][:, 1],
        external_zero=zero,
    )
    fitted = spectrum_operator(
        spectrum,
        {"family": "wiener", "tau": 1.0, "name": "w"},
    )
    region = model_assisted_conditional_region(
        interval_sessions=panels["interval"],
        evaluation_sessions=panels["evaluation"],
        fitted=fitted,
        bootstrap_replicates=100,
        bootstrap_seed=37_821,
        minimum_bootstrap_replicates=100,
        maximum_bootstrap_radius_cv=0.50,
        maximum_bootstrap_radius_quantile_ratio=2.0,
    )
    assert region["status"] == "ME_TOLERANCE_BALL_95_95"
    assert "coverage" not in region
    assert "truth" not in region
    assert region["threshold"] > 0.0
    assert region["maximum_axis"] >= region["minimum_axis"] > 0.0


def test_conditional_region_refuses_insufficient_fit_panel() -> None:
    world = simulate_reliability_spectrum_world(
        latent_seed=37_822,
        event_seed=37_823,
        spec=ReliabilitySpectrumWorldSpec(
            world="dense_tail48",
            reference_authors=32,
            calibration_authors=32,
            interval_authors=64,
            evaluation_authors=24,
        ),
    )
    panels = world["panels"]
    zero = estimate_external_origin(panels["reference"])
    spectrum = fit_reliability_spectrum(
        panels["calibration"][:, 0],
        panels["calibration"][:, 1],
        external_zero=zero,
    )
    fitted = spectrum_operator(
        spectrum,
        {"family": "wiener", "tau": 1.0, "name": "w"},
    )
    region = model_assisted_conditional_region(
        interval_sessions=panels["interval"],
        evaluation_sessions=panels["evaluation"],
        fitted=fitted,
        bootstrap_replicates=20,
        minimum_bootstrap_replicates=20,
    )
    assert region["status"] == "UNRESOLVED_INTERVAL_FIT_TOO_SMALL"
