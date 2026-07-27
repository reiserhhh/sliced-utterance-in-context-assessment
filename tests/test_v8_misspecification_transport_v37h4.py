"""Tests for the V3.7H.4 misspecification and transport battery."""
from __future__ import annotations

import numpy as np

from suica_core.v8_misspecification_transport import (
    MisspecificationSpec,
    cell_means,
    crc_permutation_p,
    crossfit_additive_prediction,
    crossfit_residual,
    crossfit_structured_prediction,
    holm_adjust,
    main_component_recovery,
    operation_gap,
    residual_correlation,
    select_structured_rank,
    simulate_misspecification_world,
)


def _world(
    *,
    seed: int,
    world: str,
    effect_share: float,
) -> tuple[dict, MisspecificationSpec]:
    spec = MisspecificationSpec()
    result = simulate_misspecification_world(
        seed=seed,
        world=world,
        effect_share=effect_share,
        noise_mode="gaussian",
        spec=spec,
        main_effect_amplitude=0.4,
        opportunity_amplitude=0.35,
        technical_amplitude=0.25,
        nonlinear_saturation=1.25,
        nonergodic_author_correlation=0.5,
        nonergodic_stable_fraction=0.5,
        nonergodic_regime_persistence=0.95,
    )
    return result, spec


def _transport_metrics(world: dict, spec: MisspecificationSpec) -> dict:
    train, calibration, test = spec.condition_split
    fit = np.concatenate([train, calibration])
    cells = cell_means(world["observations"], opportunities=8)
    labels = world["registered_group_labels"]
    rank, _ = select_structured_rank(
        cells[0],
        cells[1],
        registered_group_labels=labels,
        train_conditions=train,
        calibration_conditions=calibration,
        rank_candidates=(1, 2, 3, 4, 6),
    )
    additive = crossfit_additive_prediction(
        cells[2],
        cells[3],
        registered_group_labels=labels,
        fit_conditions=fit,
        eval_conditions=test,
    )
    structured = crossfit_structured_prediction(
        cells[2],
        cells[3],
        registered_group_labels=labels,
        fit_conditions=fit,
        eval_conditions=test,
        rank=rank,
    )
    truth = cells[3][:, test]
    residual_3 = crossfit_residual(
        cells[0],
        cells[2],
        registered_group_labels=labels,
        fit_conditions=fit,
        eval_conditions=test,
    )
    residual_4 = crossfit_residual(
        cells[1],
        cells[3],
        registered_group_labels=labels,
        fit_conditions=fit,
        eval_conditions=test,
    )
    return {
        "rank": rank,
        "gain": float(
            np.mean((truth - additive) ** 2)
            - np.mean((truth - structured) ** 2)
        ),
        "crc": residual_correlation(residual_3, residual_4),
        "residual_3": residual_3,
        "residual_4": residual_4,
    }


def test_additive_positive_control_recovers_and_does_not_refuse() -> None:
    world, spec = _world(seed=92_101, world="additive", effect_share=0.0)
    recovery = main_component_recovery(
        world["observations"],
        world["main_components"],
        opportunities=4,
    )
    assert min(float(row["recovery_r2"]) for row in recovery) > 0.95
    assert min(
        float(row["split_panel_correlation"]) for row in recovery
    ) > 0.9
    metrics = _transport_metrics(world, spec)
    _, p_value = crc_permutation_p(
        metrics["residual_3"],
        metrics["residual_4"],
        world["registered_group_labels"],
        seed=92_102,
        permutations=19,
    )
    assert abs(float(metrics["crc"])) < 0.05
    assert p_value > 0.05
    assert float(metrics["gain"]) < 0.02


def test_nonlinear_world_has_replicated_residual_and_transport_gain() -> None:
    world, spec = _world(seed=92_103, world="nonlinear", effect_share=0.20)
    metrics = _transport_metrics(world, spec)
    assert float(metrics["crc"]) > 0.5
    assert float(metrics["gain"]) > 0.05


def test_latent_hierarchy_is_detectable_without_naming_the_cause() -> None:
    world, spec = _world(
        seed=92_104,
        world="latent_hierarchy",
        effect_share=0.20,
    )
    metrics = _transport_metrics(world, spec)
    assert float(metrics["crc"]) > 0.3
    assert float(metrics["gain"]) > 0.02


def test_nonergodic_component_persists_with_k_and_aliases_cause() -> None:
    world, spec = _world(
        seed=92_105,
        world="nonergodic",
        effect_share=0.20,
    )
    train, calibration, test = spec.condition_split
    fit = np.concatenate([train, calibration])
    energies = {}
    for opportunities in (2, 8):
        cells = cell_means(
            world["observations"],
            opportunities=opportunities,
        )
        left = crossfit_residual(
            cells[0],
            cells[2],
            registered_group_labels=world["registered_group_labels"],
            fit_conditions=fit,
            eval_conditions=test,
        )
        right = crossfit_residual(
            cells[1],
            cells[3],
            registered_group_labels=world["registered_group_labels"],
            fit_conditions=fit,
            eval_conditions=test,
        )
        energies[opportunities] = float(np.mean(left * right))
    assert energies[8] / energies[2] > 0.5
    assert world["alias_identity_error"] == 0.0


def test_linear_projection_operations_commute() -> None:
    world, _ = _world(seed=92_106, world="nonlinear", effect_share=0.20)
    assert operation_gap(world["observations"], opportunities=4) < 1e-12


def test_holm_adjustment_controls_family_order() -> None:
    adjusted = holm_adjust({"crc": 0.01, "rank": 0.04, "gain": 0.20})
    assert adjusted["crc"] == 0.03
    assert adjusted["rank"] == 0.08
    assert adjusted["gain"] == 0.20
