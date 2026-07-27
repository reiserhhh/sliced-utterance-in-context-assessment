"""Tests for the R2G cross-view residual-completion frontier."""
from __future__ import annotations

import numpy as np

from suica_core.v8_residual_completion_frontier import (
    ResidualCompletionSpec,
    cross_view_residual_phi,
    evaluate_residual_arm,
    fit_completion_family,
    fit_scaling_models,
    make_world_parameters,
    overfit_trap_metrics,
    predict_completion,
    select_completion_candidate,
    simulate_completion_panel,
)


def _spec() -> ResidualCompletionSpec:
    return ResidualCompletionSpec(
        dimensions=8,
        latent_rank=2,
        units_per_group=32,
        opportunities_per_observation=4,
        common_fraction=0.8,
    )


def _panel(
    world: str,
    *,
    seed: int,
    groups: int = 24,
) -> dict[str, np.ndarray]:
    spec = _spec()
    parameters = make_world_parameters(
        seed=71_100,
        spec=spec,
        effect_share=0.30,
    )
    return simulate_completion_panel(
        seed=seed,
        world=world,
        groups=groups,
        spec=spec,
        parameters=parameters,
        noise_mode="gaussian",
    )


def test_oracle_removes_completable_common_floor() -> None:
    panel = _panel("common_low_rank", seed=71_101, groups=96)
    raw = evaluate_residual_arm(
        panel["target_a"],
        panel["target_b"],
        sizes=(4, 8, 16, 32),
        seed=71_102,
    )
    oracle = evaluate_residual_arm(
        panel["target_a"] - panel["predictable_target_a"],
        panel["target_b"] - panel["predictable_target_b"],
        sizes=(4, 8, 16, 32),
        seed=71_102,
    )
    assert raw["cross_floor_ratio"] > 0.05
    assert abs(oracle["cross_floor_ratio"]) < 0.03
    assert oracle["phi_cross_view"] < raw["phi_cross_view"]


def test_zero_score_opportunities_is_noiseless_limit() -> None:
    spec = _spec()
    parameters = make_world_parameters(
        seed=71_140,
        spec=spec,
        effect_share=0.30,
    )
    panel = simulate_completion_panel(
        seed=71_141,
        world="common_low_rank",
        groups=8,
        spec=spec,
        parameters=parameters,
        noise_mode="gaussian",
        score_opportunities=0,
    )
    assert np.array_equal(panel["score_a"], panel["score_b"])


def test_author_omission_can_have_zero_social_floor() -> None:
    panel = _panel("author_low_rank", seed=71_103, groups=128)
    result = evaluate_residual_arm(
        panel["target_a"],
        panel["target_b"],
        sizes=(4, 8, 16, 32),
        seed=71_104,
    )
    assert result["phi_cross_view"] > 0.02
    assert abs(result["cross_floor_ratio"]) < 0.05


def test_linear_completion_is_selected_for_linear_world() -> None:
    training = _panel("common_low_rank", seed=71_105)
    calibration = _panel("common_low_rank", seed=71_106)
    model = fit_completion_family(
        training,
        family="linear",
        ridge_alpha=1.0,
        maximum_rank=4,
        rff_components=32,
        rff_gamma=0.125,
        quadratic_input_rank=4,
        seed=71_107,
    )
    selected, rows = select_completion_candidate(
        calibration,
        {"linear": model},
        ranks=(1, 2, 4),
        minimum_gain=0.005,
    )
    assert len(rows) == 4
    assert selected["family"] == "linear"
    prediction = predict_completion(
        model,
        calibration["score_a"],
        rank=int(selected["rank"]),
    )
    assert prediction.shape == calibration["target_a"].shape


def test_rff_accepts_seedsequence_uint64_seed() -> None:
    training = _panel("nonlinear_common", seed=71_120, groups=8)
    model = fit_completion_family(
        training,
        family="rff",
        ridge_alpha=1.0,
        maximum_rank=2,
        rff_components=16,
        rff_gamma=0.125,
        quadratic_input_rank=4,
        seed=2**63 + 71_121,
    )
    prediction = predict_completion(
        model,
        training["score_a"],
        rank=2,
    )
    assert np.isfinite(prediction).all()


def test_irreducible_target_shock_is_not_score_predictable() -> None:
    training = _panel("irreducible_common_shock", seed=71_108)
    confirmation = _panel(
        "irreducible_common_shock",
        seed=71_109,
        groups=96,
    )
    model = fit_completion_family(
        training,
        family="linear",
        ridge_alpha=1.0,
        maximum_rank=4,
        rff_components=32,
        rff_gamma=0.125,
        quadratic_input_rank=4,
        seed=71_110,
    )
    prediction_a = predict_completion(
        model,
        confirmation["score_a"],
        rank=4,
    )
    residual_a = confirmation["target_a"] - prediction_a
    residual_b = confirmation["target_b"] - predict_completion(
        model,
        confirmation["score_b"],
        rank=4,
    )
    assert cross_view_residual_phi(residual_a, residual_b) > 0.02


def test_quadratic_completion_detects_registered_nonlinearity() -> None:
    spec = _spec()
    parameters = make_world_parameters(
        seed=71_130,
        spec=spec,
        effect_share=0.40,
    )
    training = simulate_completion_panel(
        seed=71_131,
        world="nonlinear_common",
        groups=48,
        spec=spec,
        parameters=parameters,
        noise_mode="gaussian",
    )
    calibration = simulate_completion_panel(
        seed=71_132,
        world="nonlinear_common",
        groups=48,
        spec=spec,
        parameters=parameters,
        noise_mode="gaussian",
    )
    model = fit_completion_family(
        training,
        family="quadratic",
        ridge_alpha=1.0,
        maximum_rank=4,
        rff_components=16,
        rff_gamma=0.125,
        quadratic_input_rank=4,
        seed=71_133,
    )
    selected, _ = select_completion_candidate(
        calibration,
        {"quadratic": model},
        ranks=(1, 2, 4),
        minimum_gain=0.005,
    )
    assert selected["family"] == "quadratic"
    assert selected["relative_gain"] > 0.02


def test_scaling_fit_recovers_registered_floor() -> None:
    sizes = np.asarray([4, 8, 16, 32, 64, 128], dtype=float)
    rows = [
        {
            "size": int(size),
            "self_energy": 0.07 + 1.5 / size,
            "cross_energy": 0.07 + 0.8 / size,
        }
        for size in sizes
    ]
    result = fit_scaling_models(rows, energy_key="cross_energy")
    fitted = result["models"]["floor_plus_a_over_n"]
    assert abs(fitted["floor"] - 0.07) < 1e-10
    assert abs(fitted["amplitude"] - 0.8) < 1e-10


def test_overfit_trap_is_training_only() -> None:
    training = _panel("overfit_null", seed=71_111, groups=8)
    confirmation = _panel("overfit_null", seed=71_112, groups=24)
    result = overfit_trap_metrics(
        training,
        confirmation,
        seed=2**63 + 71_113,
    )
    assert result["training_r2"] > 0.99
    assert result["confirmation_r2"] < 0.1
