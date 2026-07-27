"""Tests for the V3.7H nested-resolution filtration mechanics."""
from __future__ import annotations

import numpy as np

from suica_core.v8_reliability_spectrum import (
    _tolerance_order,
    apply_spectrum_operator,
    unresolved_channel,
)
from suica_core.v8_resolution_filtration import (
    CORE_WORLDS,
    ResolutionFiltrationWorldSpec,
    coherence_kappa,
    decompose_score_update,
    fit_coherence_predictor,
    fit_joint_resolution_family,
    fit_resolution_spectra,
    history_features,
    oscillating_assay_scores,
    predict_coherence_update,
    resolution_candidates,
    resolution_operator,
    simulate_resolution_filtration_world,
    update_mean_energy_ratio,
)


def _small_world(
    world: str = "dense_tail48_nested_gaussian",
    *,
    seed: int = 38_001,
) -> dict[str, object]:
    return simulate_resolution_filtration_world(
        latent_seed=seed,
        event_seed=seed + 1,
        spec=ResolutionFiltrationWorldSpec(
            world=world,
            dimension=8,
            budgets=(8, 16, 32),
            reference_authors=40,
            calibration_authors=48,
            probe_authors=44,
            interval_authors=40,
            evaluation_authors=42,
            opportunity_shift_start=8,
        ),
    )


def test_nested_world_has_registered_panels_and_prefix_identity() -> None:
    world = _small_world()
    panels = world["panels"]
    assert tuple(world["budgets"]) == (8, 16, 32)
    assert panels["reference_a"].shape == (40, 4, 3, 8)
    assert panels["evaluation"].shape == (42, 4, 3, 8)
    assert world["maximum_prefix_identity_error"] < 1e-10
    assert np.isfinite(panels["evaluation"]).all()


def test_nested_prefixes_share_latent_author_truth() -> None:
    world = _small_world()
    truth = world["truths"]["evaluation"]
    panel = world["panels"]["evaluation"]
    assert truth.shape == (42, 8)
    assert not np.array_equal(panel[:, :, 0], panel[:, :, 1])
    assert not np.array_equal(panel[:, :, 1], panel[:, :, 2])


def test_world_metadata_separates_core_state_and_opportunity() -> None:
    core = _small_world(CORE_WORLDS[0], seed=38_010)
    state = _small_world("state_alias_single_occasion", seed=38_020)
    opportunity = _small_world("opportunity_schedule_drift", seed=38_030)
    assert core["design"]["core_world"]
    assert state["design"]["single_occasion_state_alias"]
    assert opportunity["design"]["opportunity_schedule_drift"]


def test_fixed_stable_moment_is_shared_across_budget_spectra() -> None:
    world = _small_world(seed=38_040)
    panels = world["panels"]
    zero = panels["reference_a"][:, :, -1].mean(axis=(0, 1))
    spectra = fit_resolution_spectra(
        panels["calibration_a"],
        budgets=world["budgets"],
        external_zero=zero,
    )
    stable = [value["stable_second_moment"] for value in spectra.values()]
    for value in stable[1:]:
        assert np.array_equal(stable[0], value)


def test_joint_selection_returns_one_rule_for_all_budgets() -> None:
    world = _small_world(seed=38_050)
    panels = world["panels"]
    zero = panels["reference_a"][:, :, -1].mean(axis=(0, 1))
    fitted, selected, table = fit_joint_resolution_family(
        panels["calibration_a"],
        budgets=world["budgets"],
        external_zero=zero,
        candidates=resolution_candidates(),
        folds=3,
        seed=38_052,
        noise_shrinkage=0.25,
    )
    assert table["selected"].sum() == 1
    assert selected["name"] in set(table["name"])
    assert set(fitted) == set(world["budgets"])
    assert {
        value["candidate"]["name"] for value in fitted.values()
    } == {selected["name"]}


def test_wiener_rule_activates_with_higher_signal_to_noise() -> None:
    dimension = 4
    candidate = {
        "family": "wiener",
        "tau": 1.0,
        "name": "wiener_tau_1",
    }
    common = {
        "external_zero": np.zeros(dimension),
        "stable_second_moment": np.eye(dimension),
        "event_second_moment": np.eye(dimension),
        "event_regularized": np.eye(dimension),
        "event_root": np.eye(dimension),
        "event_inverse": np.eye(dimension),
        "modes": np.eye(dimension),
    }
    low = resolution_operator({**common, "eta": np.ones(dimension)}, candidate)
    high = resolution_operator(
        {**common, "eta": np.full(dimension, 4.0)},
        candidate,
    )
    assert high["effective_df"] > low["effective_df"]


def test_score_and_unresolved_reconstruct_at_every_budget() -> None:
    world = _small_world(seed=38_060)
    panels = world["panels"]
    zero = panels["reference_a"][:, :, -1].mean(axis=(0, 1))
    fitted, _, _ = fit_joint_resolution_family(
        panels["calibration_a"],
        budgets=world["budgets"],
        external_zero=zero,
        candidates=resolution_candidates(),
        folds=3,
        seed=38_062,
        noise_shrinkage=0.25,
    )
    for index, budget in enumerate(world["budgets"]):
        profile = panels["evaluation"][:, :2, index].mean(axis=1)
        score = apply_spectrum_operator(profile, fitted[budget])
        residual = unresolved_channel(profile, fitted[budget])
        assert np.allclose(score + residual, profile)


def test_update_decomposition_reconstructs_direct_score_change() -> None:
    world = _small_world(seed=38_070)
    panels = world["panels"]
    zero = panels["reference_a"][:, :, -1].mean(axis=(0, 1))
    fitted, _, _ = fit_joint_resolution_family(
        panels["calibration_a"],
        budgets=world["budgets"],
        external_zero=zero,
        candidates=resolution_candidates(),
        folds=3,
        seed=38_072,
        noise_shrinkage=0.25,
    )
    left = panels["evaluation"][:, :2, 0].mean(axis=1)
    right = panels["evaluation"][:, :2, 1].mean(axis=1)
    result = decompose_score_update(
        left,
        right,
        fitted[8],
        fitted[16],
    )
    assert result["reconstruction_error"] < 1e-10
    assert np.isclose(
        result["event_energy_ratio"]
        + result["operator_energy_ratio"]
        + result["cross_energy_ratio"],
        1.0,
    )


def test_coherence_predictor_detects_predictable_but_not_random_update() -> None:
    rng = np.random.default_rng(38_080)
    probe_x = rng.normal(size=(160, 12))
    evaluation_x = rng.normal(size=(120, 12))
    matrix = rng.normal(size=(12, 5))
    probe_predictable = probe_x @ matrix
    evaluation_predictable = evaluation_x @ matrix
    fitted = fit_coherence_predictor(
        probe_x,
        probe_predictable,
        seed=38_081,
    )
    prediction = predict_coherence_update(fitted, evaluation_x)
    assert coherence_kappa(evaluation_predictable, prediction) > 0.90

    probe_random = rng.normal(size=(160, 5))
    evaluation_random = rng.normal(size=(120, 5))
    null_fit = fit_coherence_predictor(
        probe_x,
        probe_random,
        seed=38_082,
    )
    null_prediction = predict_coherence_update(null_fit, evaluation_x)
    assert coherence_kappa(evaluation_random, null_prediction) < 0.20


def test_history_features_are_observable_and_expand_with_budget() -> None:
    world = _small_world(seed=38_090)
    values = world["panels"]["probe"]
    zero = values[:, :, -1].mean(axis=(0, 1))
    scores = [
        values[:, :2, index].mean(axis=1)
        for index in range(values.shape[2])
    ]
    residuals = [np.zeros_like(value) for value in scores]
    early = history_features(
        values,
        scores,
        residuals,
        0,
        external_zero=zero,
    )
    later = history_features(
        values,
        scores,
        residuals,
        1,
        external_zero=zero,
    )
    assert early.shape[0] == later.shape[0] == 44
    assert later.shape[1] > early.shape[1]


def test_registered_95_99_order_supports_five_budget_union_bound() -> None:
    order, achieved = _tolerance_order(
        192,
        content=0.95,
        confidence=0.99,
    )
    assert order == 190
    assert achieved >= 0.99
    assert 1.0 - 5.0 * (1.0 - 0.99) >= 0.95 - 1e-12


def test_update_mean_energy_and_oscillating_assay_are_finite() -> None:
    rng = np.random.default_rng(38_100)
    scores = [rng.normal(size=(32, 8)) for _ in range(3)]
    assay = oscillating_assay_scores(
        scores,
        external_zero=np.zeros(8),
        amplitude=0.08,
    )
    assert len(assay) == 3
    assert not np.array_equal(assay[0], scores[0])
    ratio = update_mean_energy_ratio(assay[1] - assay[0])
    assert np.isfinite(ratio)
    assert ratio >= 0.0
