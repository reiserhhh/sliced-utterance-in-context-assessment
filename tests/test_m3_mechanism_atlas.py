"""Tests for mechanism-selective SUICA M3 discovery."""
from __future__ import annotations

import numpy as np

from suica_core.m3_mechanism_audit import audit_m3_mechanism_atlas
from suica_core.m3_mechanism_estimator import fit_m3_mechanism_atlas
from suica_core.m3_mechanism_generator import (
    M3MechanismWorldSpec,
    generate_m3_mechanism_world,
)


def _audit(world: str, seed: int) -> dict[str, dict[str, float | str | bool]]:
    observed, truth = generate_m3_mechanism_world(
        world=world,
        spec=M3MechanismWorldSpec(
            authors=24,
            occasions=5,
            events=72,
            noise=0.12,
        ),
        seed=seed,
    )
    estimate = fit_m3_mechanism_atlas(observed, seed=seed + 1)
    return {
        str(row["family"]): row
        for row in audit_m3_mechanism_atlas(estimate, truth)
    }


def test_train_and_test_share_truth_but_not_events() -> None:
    observed, truth = generate_m3_mechanism_world(
        world="conditional_response_operator",
        spec=M3MechanismWorldSpec(authors=16, occasions=3, events=24),
        seed=41,
    )
    assert truth.author_parameter.shape[0] == 16
    assert not np.allclose(observed.response_train, observed.response_test)
    assert not np.allclose(observed.condition_train, observed.condition_test)


def test_conditional_operator_recovers_if_then_geometry() -> None:
    rows = _audit("conditional_response_operator", 51)
    assert float(rows["conditional_operator"]["same_author_auc"]) > 0.75
    assert float(rows["conditional_operator"]["truth_geometry_spearman"]) > 0.70
    assert (
        float(rows["conditional_operator"]["same_author_auc"])
        > float(rows["mean_position"]["same_author_auc"]) + 0.15
    )


def test_higher_order_path_is_not_reduced_to_first_order_mode() -> None:
    rows = _audit("higher_order_path", 61)
    assert float(rows["higher_order_path"]["same_author_auc"]) > 0.65
    assert (
        float(rows["higher_order_path"]["same_author_auc"])
        > float(rows["koopman_spectrum"]["same_author_auc"])
    )


def test_opportunity_world_is_removed_from_response_residual() -> None:
    rows = _audit("opportunity_only", 71)
    assert float(rows["opportunity_profile"]["same_author_auc"]) > 0.80
    assert float(rows["distribution_kme"]["same_author_auc"]) < 0.62
    assert float(rows["higher_order_path"]["same_author_auc"]) < 0.62


def test_null_world_does_not_create_strong_author_identity() -> None:
    rows = _audit("null_author", 81)
    assert max(
        float(row["same_author_auc"])
        for family, row in rows.items()
        if family != "union"
    ) < 0.62
