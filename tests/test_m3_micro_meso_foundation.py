"""Tests for the SUICA M3 micro-meso-macro synthetic foundation."""
from __future__ import annotations

import inspect

import numpy as np

from suica_core.m3_contracts import (
    coarse_grain_homogeneous_replicates,
)
from suica_core.m3_meso_estimator import fit_m3_meso
from suica_core.m3_micro_generator import (
    M3WorldSpec,
    generate_m3_world,
    same_occupancy_different_transition,
    stable_state_alias_counterexample,
)
from suica_core.m3_truth_audit import (
    audit_m3_invariance,
    audit_m3_truth,
    packet_has_truth_leakage,
)


def _small_spec(**overrides: object) -> M3WorldSpec:
    values: dict[str, object] = {
        "authors": 40,
        "reference_authors": 80,
        "conditions": 8,
        "condition_dimensions": 3,
        "response_dimensions": 5,
        "occasions": 4,
        "fixed_repeats_train": 4,
        "fixed_repeats_test": 4,
        "free_events_train": 120,
        "free_events_test": 120,
    }
    values.update(overrides)
    return M3WorldSpec(**values)


def test_estimator_is_physically_separated_from_generator() -> None:
    import suica_core.m3_meso_estimator as estimator

    source = inspect.getsource(estimator)
    assert "m3_micro_generator" not in source


def test_observed_packet_exposes_no_truth_like_fields() -> None:
    observed, _, _ = generate_m3_world(
        spec=_small_spec(),
        seed=10_101,
    )
    assert not packet_has_truth_leakage(observed)


def test_positive_world_recovers_registered_meso_objects() -> None:
    observed, truth, manifest = generate_m3_world(
        spec=_small_spec(heavy_tail=True, nonlinear=True),
        seed=10_102,
    )
    estimate = fit_m3_meso(observed, manifest)
    audit = audit_m3_truth(estimate, truth)
    assert estimate.response_status == "RESPONSE_OK"
    assert estimate.state_status == "STATE_OK"
    assert audit["choice_js_median"] < 0.08
    assert audit["position_distance_spearman"] > 0.70
    assert audit["operator_correlation"] > 0.60
    assert audit["nonlinear_correlation"] > 0.40
    assert audit["state_correlation"] > 0.45


def test_linear_and_nonlinear_fields_are_q0_orthogonal() -> None:
    _, truth, manifest = generate_m3_world(
        spec=_small_spec(nonlinear=True),
        seed=10_103,
    )
    q0 = manifest.reference_measure
    features = manifest.condition_features
    h = truth.nonlinear_field
    assert np.max(np.abs(np.einsum("c,ucp->up", q0, h))) < 1e-10
    cross = np.einsum("c,cq,ucp->upq", q0, features, h)
    assert np.max(np.abs(cross)) < 1e-10


def test_affine_and_homogeneous_coarse_invariance() -> None:
    observed, _, manifest = generate_m3_world(
        spec=_small_spec(),
        seed=10_104,
    )
    audit = audit_m3_invariance(observed, manifest, seed=10_105)
    assert audit["rotation_position_max_abs"] < 1e-10
    assert audit["rotation_operator_max_abs"] < 1e-10
    assert audit["translation_position_max_abs"] < 1e-10
    assert audit["coarse_position_max_abs"] < 1e-10
    assert audit["rotation_position_geometry"] > 0.999999
    assert audit["rotation_operator_geometry"] > 0.999999
    coarse = coarse_grain_homogeneous_replicates(
        observed,
        block_size=2,
    )
    assert coarse.fixed_responses_train.shape[-2] == 2


def test_design_failures_trigger_refusal() -> None:
    missing, _, manifest_missing = generate_m3_world(
        spec=_small_spec(missing_common_support=True),
        seed=10_106,
    )
    rank, _, manifest_rank = generate_m3_world(
        spec=_small_spec(rank_deficient=True),
        seed=10_107,
    )
    occasion, _, manifest_occasion = generate_m3_world(
        spec=_small_spec(occasions=1),
        seed=10_108,
    )
    assert (
        fit_m3_meso(missing, manifest_missing).response_status
        == "RESPONSE_REFUSED_NO_COMMON_SUPPORT"
    )
    assert (
        fit_m3_meso(rank, manifest_rank).response_status
        == "RESPONSE_REFUSED_RANK_DEFICIENT"
    )
    assert (
        fit_m3_meso(occasion, manifest_occasion).state_status
        == "STATE_REFUSED_SINGLE_OCCASION"
    )


def test_same_occupancy_does_not_identify_transition_dynamics() -> None:
    stationary = np.asarray([0.10, 0.20, 0.30, 0.40])
    first, second = same_occupancy_different_transition(
        stationary,
        first_inertia=0.10,
        second_inertia=0.80,
    )
    assert np.max(np.abs(stationary @ first - stationary)) < 1e-12
    assert np.max(np.abs(stationary @ second - stationary)) < 1e-12
    assert np.linalg.norm(first - second) > 0.50


def test_single_occasion_position_state_alias_is_exact() -> None:
    alias = stable_state_alias_counterexample(seed=10_109)
    assert np.array_equal(
        alias["observed_world_a"],
        alias["observed_world_b"],
    )
    assert np.linalg.norm(
        alias["position_world_a"] - alias["position_world_b"]
    ) > 0.50
    assert np.linalg.norm(
        alias["state_world_a"] - alias["state_world_b"]
    ) > 0.50
