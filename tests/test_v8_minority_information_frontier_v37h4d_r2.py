"""Tests for the V3.7H.4D R2 minority information frontier."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from scripts.run_suica_v8_minority_information_frontier_v37h4d_r2 import (
    _evaluate,
    _logistic_information_slope,
)
from scripts.run_suica_v8_reference_measure_frontier_v37h4d import (
    _read,
    _spec,
)
from suica_core.v8_minority_information_frontier import (
    complete_double_center,
    local_double_center,
    plant_minority_interaction,
    residual_precision_energy,
)
from suica_core.v8_reference_measure_frontier import simulate_reference_world


ROOT = Path(__file__).resolve().parents[1]


def _config() -> dict:
    config = _read(
        ROOT
        / "configs/v8_minority_information_frontier_v37h4d_r2.json"
    )
    config["_active_permutations"] = 19
    return config


def _additive_world(seed: int) -> dict:
    config = _config()
    spec = _spec(config)
    return simulate_reference_world(
        seed=seed,
        world="additive",
        effect_share=0.0,
        reference_jsd=0.15,
        support_coverage=1.0,
        near_kernel_fraction=0.02,
        noise_mode="gaussian",
        opportunity_prefixes=(64, 128, 256),
        author_tilt=float(config["author_tilt"]),
        author_amplitude=float(config["author_amplitude"]),
        condition_amplitude=float(config["condition_amplitude"]),
        society_amplitude=float(config["society_amplitude"]),
        group_amplitude=float(config["group_amplitude"]),
        panel_noise_amplitude=float(config["panel_noise_amplitude"]),
        technical_noise_amplitude=float(
            config["technical_noise_amplitude"]
        ),
        student_df=float(config["student_df"]),
        heteroskedastic_strength=float(
            config["heteroskedastic_strength"]
        ),
        minority_author_fraction=0.1,
        minority_condition_fraction=0.25,
        spec=spec,
        acquisition_reference_shift=True,
    )


def test_local_double_center_preserves_zero_margins() -> None:
    rng = np.random.default_rng(602_001)
    block = local_double_center(rng.normal(size=(8, 4, 6)))
    assert np.max(np.abs(block.sum(axis=0))) < 1e-12
    assert np.max(np.abs(block.sum(axis=1))) < 1e-12


def test_sparse_plant_does_not_spread_support() -> None:
    config = _config()
    spec = _spec(config)
    world, audit = plant_minority_interaction(
        _additive_world(602_002),
        spec=spec,
        seed=602_003,
        active_test_authors=4,
        active_conditions=4,
        support_scheme="fixed",
        interaction_shape="iid_block",
        scaling_arm="global_share",
        global_effect_share=0.20,
        active_cell_snr=15.0,
        primary_opportunities=128,
        panel_noise_amplitude=float(config["panel_noise_amplitude"]),
        technical_noise_amplitude=float(
            config["technical_noise_amplitude"]
        ),
        heteroskedastic_strength=float(
            config["heteroskedastic_strength"]
        ),
    )
    expected_active_authors = 2 * 4 + 4 + 4
    expected_fraction = (
        expected_active_authors * 4
        / (spec.authors * spec.conditions)
    )
    assert np.isclose(audit["intended_support_fraction"], expected_fraction)
    assert np.isclose(audit["realized_global_effect_share"], 0.20)
    assert np.count_nonzero(
        np.any(np.abs(world["interaction"]) > 1e-15, axis=-1)
    ) == expected_active_authors * 4


def test_active_snr_arm_hits_registered_snr() -> None:
    config = _config()
    spec = _spec(config)
    _, audit = plant_minority_interaction(
        _additive_world(602_004),
        spec=spec,
        seed=602_005,
        active_test_authors=8,
        active_conditions=4,
        support_scheme="fixed",
        interaction_shape="iid_block",
        scaling_arm="active_snr",
        global_effect_share=0.20,
        active_cell_snr=15.0,
        primary_opportunities=128,
        panel_noise_amplitude=float(config["panel_noise_amplitude"]),
        technical_noise_amplitude=float(
            config["technical_noise_amplitude"]
        ),
        heteroskedastic_strength=float(
            config["heteroskedastic_strength"]
        ),
    )
    assert np.isclose(audit["registered_active_cell_snr"], 15.0)
    assert 10.0 < audit["realized_active_cell_snr"] < 20.0
    assert audit["information_budget_residual"] > 0
    assert audit["observed_active_cells_both_panels"] > 0
    assert audit["projection_grand_mean_compatibility_error"] < 1e-12


def test_information_budget_grows_with_support_at_fixed_snr() -> None:
    config = _config()
    spec = _spec(config)
    budgets = []
    for index, m in enumerate((2, 4, 8, 16)):
        _, audit = plant_minority_interaction(
            _additive_world(602_010 + index),
            spec=spec,
            seed=602_020 + index,
            active_test_authors=m,
            active_conditions=4,
            support_scheme="fixed",
            interaction_shape="iid_block",
            scaling_arm="active_snr",
            global_effect_share=0.20,
            active_cell_snr=15.0,
            primary_opportunities=128,
            panel_noise_amplitude=float(
                config["panel_noise_amplitude"]
            ),
            technical_noise_amplitude=float(
                config["technical_noise_amplitude"]
            ),
            heteroskedastic_strength=float(
                config["heteroskedastic_strength"]
            ),
        )
        budgets.append(audit["information_budget_residual"])
    assert all(right > left for left, right in zip(budgets, budgets[1:]))


def test_r2_evaluate_uses_frozen_detector_schema() -> None:
    config = _config()
    row = _evaluate(
        definition={
            "cell_kind": "smoke",
            "scaling_arm": "active_snr",
            "support_scheme": "fixed",
            "interaction_shape": "iid_block",
            "noise_mode": "gaussian",
            "active_test_authors": 8,
        },
        repetition=0,
        world_seed=602_101,
        plant_seed=602_102,
        diagnostic_seed=602_103,
        config=config,
    )
    assert {
        "crc_p_holm",
        "cross_low_rank_p_holm",
        "hc_p_holm",
        "structure_detected",
        "crc_or_hc_detected",
    } <= set(row)
    assert row["active_test_authors"] == 8


def test_residual_information_matches_explicit_pseudoinverse() -> None:
    rng = np.random.default_rng(602_151)
    authors, conditions, dimensions = 4, 3, 2
    raw = rng.normal(size=(authors, conditions, dimensions))
    residual = complete_double_center(raw)
    variance = rng.uniform(0.2, 1.5, size=(authors, conditions))
    author_projection = (
        np.eye(authors) - np.ones((authors, authors)) / authors
    )
    condition_projection = (
        np.eye(conditions)
        - np.ones((conditions, conditions)) / conditions
    )
    projection = np.kron(author_projection, condition_projection)
    covariance = (
        projection
        @ np.diag(variance.reshape(-1))
        @ projection
    )
    precision = np.linalg.pinv(covariance)
    explicit = sum(
        residual[:, :, dimension].reshape(-1)
        @ precision
        @ residual[:, :, dimension].reshape(-1)
        for dimension in range(dimensions)
    )
    assert np.isclose(
        residual_precision_energy(residual, variance),
        explicit,
        rtol=1e-8,
        atol=1e-8,
    )


def test_intrinsic_zero_sum_prevents_centering_leakage() -> None:
    config = _config()
    spec = _spec(config)
    _, audit = plant_minority_interaction(
        _additive_world(602_160),
        spec=spec,
        seed=602_161,
        active_test_authors=8,
        active_conditions=4,
        support_scheme="fixed",
        interaction_shape="intrinsic_zero_sum",
        scaling_arm="active_snr",
        global_effect_share=0.20,
        active_cell_snr=15.0,
        primary_opportunities=128,
        panel_noise_amplitude=float(config["panel_noise_amplitude"]),
        technical_noise_amplitude=float(
            config["technical_noise_amplitude"]
        ),
        heteroskedastic_strength=float(
            config["heteroskedastic_strength"]
        ),
    )
    assert np.isclose(audit["centering_retention_ratio"], 1.0)
    assert audit["centering_leakage_ratio"] < 1e-20


def test_logistic_information_slope_is_positive_for_planted_curve() -> None:
    rng = np.random.default_rng(602_201)
    information = np.exp(np.linspace(1.0, 8.0, 400))
    probability = 1.0 / (
        1.0 + np.exp(-(np.log(information) - 4.5))
    )
    detected = rng.random(len(information)) < probability
    result = _logistic_information_slope(information, detected)
    assert result["information_logistic_slope_lower_95"] > 0
