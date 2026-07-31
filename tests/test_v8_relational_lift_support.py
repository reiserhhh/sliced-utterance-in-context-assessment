"""Tests for the V8-HJIC-1A replicated relation-support battery."""
from __future__ import annotations

import numpy as np

from suica_core.v8_relational_lift_support import (
    RelationSupportSpec,
    audit_relation_truth,
    estimate_replicated_support,
    observable_relation_diagnostics,
    relation_shift_statistics,
    run_relation_support_repetition,
    simulate_relation_world,
)


def _test_spec() -> RelationSupportSpec:
    return RelationSupportSpec(
        authors=2400,
        repeated_splits=32,
        bootstrap_draws=120,
        permutations=199,
        anchor_private_noise=0.8,
    )


def test_replicated_support_is_observable_and_nonempty() -> None:
    spec = _test_spec()
    world = simulate_relation_world("SHARED_LATENT", seed=11, spec=spec)
    support = estimate_replicated_support(
        world["big5_first"],
        world["big5_second"],
        world["mbti_first"],
        world["mbti_second"],
        rng=np.random.default_rng(12),
        permutations=spec.permutations,
    )
    assert support.big5_rank > 0
    assert support.mbti_rank > 0
    assert support.big5_eigenvalues.max() > support.big5_null_q99
    assert support.mbti_eigenvalues.max() > support.mbti_null_q99


def test_truth_is_opened_only_after_observable_license() -> None:
    spec = _test_spec()
    world = simulate_relation_world("SHARED_LATENT", seed=21, spec=spec)
    observable = observable_relation_diagnostics(
        world,
        seed=22,
        spec=spec,
    )
    assert "truth_fidelity" not in observable
    truth = audit_relation_truth(world, observable)
    assert truth["truth_fidelity"] > 0.8


def test_relation_shift_is_symmetric_and_detects_local_change() -> None:
    spec = _test_spec()
    first = np.zeros((5, 4))
    second = first.copy()
    second[2, 3] = 0.25
    forward = relation_shift_statistics(first, second, spec=spec)
    backward = relation_shift_statistics(second, first, spec=spec)
    assert forward == backward
    assert forward["maximum_cell_shift"] == 0.25
    assert forward["max_statistic"] >= 2.5


def test_relation_and_mode_licenses_separate_breaking_worlds() -> None:
    rows = run_relation_support_repetition(
        0,
        seed=20260729,
        spec=_test_spec(),
    )
    by_world = {row["world"]: row for row in rows}
    assert by_world["SHARED_LATENT"]["licensed"] == 1
    assert by_world["SHARED_LATENT"]["mode_licensed"] == 1
    assert by_world["SHARED_LATENT"]["truth_fidelity"] >= 0.8
    assert by_world["LOW_SINGULAR_GAP"]["licensed"] == 1
    assert by_world["LOW_SINGULAR_GAP"]["mode_licensed"] == 0
    assert by_world["NULL_HIGH_DIM_NUISANCE"]["licensed"] == 1
    assert by_world["NULL_HIGH_DIM_NUISANCE"]["nuisance_instability"] == 0
    assert by_world["LOCALIZED_SIMPSON"]["nuisance_instability"] == 1
    assert by_world["WEAK_RELATION"]["licensed"] == 0
    assert by_world["WEAK_RELATION"]["nuisance_instability"] == 0
    assert by_world["COLLIDER_OR_DESCENDANT_Z"]["licensed"] == 0
    assert by_world["COLLIDER_OR_DESCENDANT_Z"][
        "nuisance_instability"
    ] == 1
    for name in (
        "COMMON_NUISANCE",
        "CORRELATED_REPLICATE_ERROR",
        "SIMPSON_MIXTURE",
        "LOCALIZED_SIMPSON",
        "PRIVATE_AXES",
        "WEAK_RELATION",
        "COLLIDER_OR_DESCENDANT_Z",
    ):
        assert by_world[name]["licensed"] == 0
    assert all(not row["truth_used_by_license"] for row in rows)
