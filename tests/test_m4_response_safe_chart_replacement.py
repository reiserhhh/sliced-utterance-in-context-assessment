"""Tests for the M4-C.3.5-R2 chart-replacement helpers."""
from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.run_suica_m4_response_safe_chart_replacement import _decision
from suica_core.m4_chart_ecology_generator import (
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_creation_residual_attribution import (
    build_creation_attribution_grid,
)
from suica_core.m4_response_safe_chart_replacement import (
    basis_oracle_cka,
    build_current_pooled_attribution_route,
    linear_cka,
    match_nonmass_trace,
    nonmass_rank_and_trace,
    rotate_spectral_block_basis,
    truncate_whitened_basis,
)


def _basis(seed: int = 17) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    return {
        role: np.column_stack([np.ones(16), rng.normal(size=(16, 6))])
        for role in ("calibration", "selection", "evaluation")
    }


def test_truncation_preserves_mass_and_requested_rank() -> None:
    basis = _basis()
    truncated = truncate_whitened_basis(basis, rank=3)
    for role in basis:
        assert truncated[role].shape == (16, 4)
        assert np.array_equal(truncated[role][:, 0], basis[role][:, 0])
        assert np.array_equal(
            truncated[role][:, 1:],
            basis[role][:, 1:4],
        )


def test_linear_cka_is_orthogonal_and_translation_invariant() -> None:
    rng = np.random.default_rng(29)
    values = rng.normal(size=(32, 5))
    q, _ = np.linalg.qr(rng.normal(size=(5, 5)))
    transformed = values @ q + np.linspace(-2.0, 2.0, 5)
    assert np.isclose(linear_cka(values, transformed), 1.0, atol=1e-12)


def test_spectral_block_rotation_preserves_oracle_gram_alignment() -> None:
    basis = _basis()
    rotated = rotate_spectral_block_basis(
        basis,
        ((0, 2), (2, 6)),
        seed=31,
    )
    native = basis_oracle_cka(basis, basis)
    gauged = basis_oracle_cka(rotated, basis)
    for role in basis:
        assert np.isclose(native[role], 1.0, atol=1e-12)
        assert np.isclose(gauged[role], 1.0, atol=1e-12)


def test_trace_matching_preserves_rank_and_matches_target_energy() -> None:
    basis = _basis()
    target = {
        role: np.column_stack([values[:, 0], 2.5 * values[:, 1:]])
        for role, values in basis.items()
    }
    matched = match_nonmass_trace(basis, target)
    matched_stats = nonmass_rank_and_trace(matched)
    target_stats = nonmass_rank_and_trace(target)
    for role in basis:
        assert matched_stats[role][0] == target_stats[role][0]
        assert np.isclose(
            matched_stats[role][1],
            target_stats[role][1],
            atol=1e-10,
        )


def test_current_pooled_route_matches_frozen_c34_baseline() -> None:
    spec = M4ChartEcologySpec(
        reference_authors=8,
        mechanism_authors=8,
        reference_calibration_points=16,
        reference_selection_points=16,
        categories=16,
        calibration_occasions=4,
        selection_occasions=2,
        evaluation_occasions=2,
        events=24,
    )
    observed, truth = generate_m4_chart_ecology_world(
        world="endogenous_creation_expansion",
        spec=spec,
        seed=71_903,
    )
    grid = build_creation_attribution_grid(
        observed.ecology,
        truth.oracle_basis,
        iterations=8,
    )
    route = build_current_pooled_attribution_route(
        observed.ecology,
        truth.oracle_basis,
        iterations=8,
    )
    for view_name in ("train", "test"):
        expected = getattr(grid.current_pooled, view_name)
        actual = getattr(route, view_name)
        assert np.allclose(actual.creation, expected.creation)
        assert np.allclose(actual.evaluation_loss, expected.evaluation_loss)
        assert np.allclose(
            actual.comparable_hazard_loss,
            expected.comparable_hazard_loss,
        )


def _conditional_decision_fixture() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    dict,
]:
    worlds = {
        "eligible": "main",
        "history": "main",
        "compensation": "main",
        "null__draw_00": "null",
    }
    geometry = {
        "eligible": {
            "B0": 0.40,
            "Br_var": 0.45,
            "Br_rep": 0.44,
            "R": 0.552,
            "Oest": 0.56,
        },
        "history": {
            "B0": 0.50,
            "Br_var": 0.46,
            "Br_rep": 0.45,
            "R": 0.50,
            "Oest": 0.50,
        },
        "compensation": {
            "B0": 0.50,
            "Br_var": 0.46,
            "Br_rep": 0.45,
            "R": 0.495,
            "Oest": 0.50,
        },
        "null__draw_00": {
            arm: 0.50
            for arm in ("B0", "Br_var", "Br_rep", "R", "Oest")
        },
    }
    rows = []
    for repetition in range(4):
        for world, world_type in worlds.items():
            for view in ("train", "test"):
                for arm, value in geometry[world].items():
                    rows.append(
                        {
                            "repetition": repetition,
                            "world": world,
                            "world_type": world_type,
                            "view": view,
                            "arm": arm,
                            "geometry": value,
                            "oracle_swap_geometry": (
                                0.60 if world == "eligible" else 0.50
                            ),
                            "evaluation_loss": 1.0,
                            "comparable_hazard_loss": 1.0,
                            "oracle_cka_calibration": (
                                0.8 if arm == "R" else 0.4
                            ),
                            "oracle_cka_selection": (
                                0.8 if arm == "R" else 0.4
                            ),
                            "oracle_cka_evaluation": (
                                0.8
                                if arm == "R"
                                else 0.5
                                if arm in {"Br_var", "Br_rep"}
                                else 0.4
                            ),
                            "oracle_cka_mean": 0.8 if arm == "R" else 0.4,
                            "old_rank": 3,
                            "rcca_support_rank_1": 2,
                            "rcca_support_rank_2": 2,
                            "rcca_shared_rank_lower": 2,
                            "rcca_shared_rank_upper": 2,
                            "rcca_shared_rank": 2,
                            "rcca_refused": False,
                            "rcca_refusal_reasons": "",
                        }
                    )
    controls = []
    for repetition in range(4):
        for world in worlds:
            controls.append(
                {
                    "repetition": repetition,
                    "world": world,
                    "control": "basis_contract",
                    "value": 0.0,
                    "passed": True,
                }
            )
        for world in ("eligible", "history", "compensation"):
            controls.extend(
                [
                    {
                        "repetition": repetition,
                        "world": world,
                        "control": "author_permutation",
                        "value": -0.1,
                        "passed": True,
                    },
                    {
                        "repetition": repetition,
                        "world": world,
                        "control": "source_shuffle",
                        "value": 0.0,
                        "passed": True,
                    },
                    {
                        "repetition": repetition,
                        "world": world,
                        "control": "cka_permutation",
                        "value": 0.005,
                        "passed": True,
                    },
                ]
            )
        controls.extend(
            [
                {
                    "repetition": repetition,
                    "world": "eligible",
                    "control": "block_gauge",
                    "value": 0.0,
                    "passed": True,
                },
                {
                    "repetition": repetition,
                    "world": "eligible",
                    "control": "common_shift",
                    "value": 0.0,
                    "passed": True,
                },
                {
                    "repetition": repetition,
                    "world": "evaluation_support_shift",
                    "control": "support_shift",
                    "value": 1.0,
                    "passed": True,
                },
                {
                    "repetition": repetition,
                    "world": "condition_alias_ecology",
                    "control": "latent_alias",
                    "value": 0.0,
                    "passed": True,
                },
            ]
        )
    targets = {
        "minimum_oracle_headroom": 0.05,
        "minimum_oracle_estimator_recovery": 0.65,
        "minimum_rcca_gain": 0.05,
        "minimum_same_rank_control_coverage": 1.0,
        "minimum_rcca_recovery": 0.60,
        "minimum_rcca_recovery_lcb": 0.35,
        "minimum_ratio_valid_bootstrap_rate": 0.975,
        "minimum_accessible_efficiency": 0.80,
        "minimum_accessible_efficiency_lcb": 0.50,
        "maximum_oracle_noninferiority_margin": 0.01,
        "minimum_positive_repetitions": 4,
        "minimum_positive_repetitions_per_eligible_world": 4,
        "minimum_high_headroom_world_recovery": 0.30,
        "maximum_sentinel_world_degradation": 0.01,
        "maximum_boundary_oracle_degradation": 0.01,
        "maximum_cka_permutation_p": 0.01,
        "maximum_hazard_relative_degradation": 0.02,
        "maximum_author_permutation_gain": 0.01,
        "null_gain_threshold": 0.03,
        "maximum_null_false_success_wilson_upper": 1.0,
        "maximum_native_rcca_refusal_rate": 0.0,
        "minimum_source_shuffle_rate": 0.95,
        "minimum_support_shift_refusal_rate": 1.0,
        "maximum_alias_false_recovery_rate": 0.0,
        "maximum_downstream_gauge_error": 1e-6,
        "maximum_downstream_common_shift_error": 1e-10,
    }
    config = {
        "estimand_id": "conditional-test",
        "estimand_variant": "conditional",
        "phase": "confirmation",
        "eligible_worlds": ["eligible"],
        "sentinel_worlds": ["history"],
        "boundary_worlds": ["compensation"],
        "bootstrap_seed": 31,
        "bootstrap_repetitions": 200,
        "targets": targets,
    }
    return pd.DataFrame(rows), pd.DataFrame(controls), config


def test_conditional_decision_uses_oracle_fidelity_at_boundary() -> None:
    metrics, controls, config = _conditional_decision_fixture()
    decision = _decision(metrics, controls, config=config)
    assert decision["decision"] == (
        "M4_C35_R2B_CONDITIONAL_CHART_EFFECT_GO"
    )
    assert decision["checks"]["world_consistency"]
    assert np.isclose(
        decision["diagnostics"]["boundary_worlds"]["compensation"][
            "oracle_fidelity_lcb"
        ],
        -0.005,
    )

    failed = metrics.copy()
    mask = (
        (failed["world"] == "compensation")
        & (failed["arm"] == "R")
    )
    failed.loc[mask, "geometry"] = 0.45
    decision = _decision(failed, controls, config=config)
    assert not decision["checks"]["world_consistency"]
