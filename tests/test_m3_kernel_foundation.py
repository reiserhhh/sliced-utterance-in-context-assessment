"""Tests for the out-of-family SUICA M3 event-kernel battery."""
from __future__ import annotations

import inspect

import numpy as np

from suica_core.m3_kernel_audit import (
    audit_m3_kernel_invariance,
    audit_m3_kernel_truth,
    audit_same_occupancy_different_transition,
    audit_single_occasion_state_alias,
    packet_has_hidden_kernel_fields,
)
from suica_core.m3_kernel_estimator import fit_m3_kernel
from suica_core.m3_kernel_generator import (
    M3KernelWorldSpec,
    generate_m3_kernel_world,
)


def _small_spec(**overrides: object) -> M3KernelWorldSpec:
    values: dict[str, object] = {
        "authors": 36,
        "reference_authors": 60,
        "conditions": 36,
        "train_occasions": 10,
        "test_occasions": 10,
        "fixed_repeats": 3,
        "free_events": 60,
        "condition_frequency": 1.0,
        "nonlinear_scale": 0.7,
    }
    values.update(overrides)
    return M3KernelWorldSpec(**values)


def test_kernel_estimator_has_no_generator_import() -> None:
    import suica_core.m3_kernel_estimator as estimator

    assert "m3_kernel_generator" not in inspect.getsource(estimator)


def test_public_packets_hide_micro_kernel_objects() -> None:
    observed, _, design = generate_m3_kernel_world(
        spec=_small_spec(authors=12, reference_authors=20),
        seed=21_001,
    )
    assert not packet_has_hidden_kernel_fields(observed)
    assert not packet_has_hidden_kernel_fields(design)


def test_event_kernel_recovers_unseen_mesoscopic_structure() -> None:
    observed, truth, design = generate_m3_kernel_world(
        spec=_small_spec(heavy_tail=True, heteroskedastic=True),
        seed=10_102,
    )
    estimate = fit_m3_kernel(observed, design)
    audit = audit_m3_kernel_truth(
        estimate,
        truth,
        observed,
        design,
    )
    assert estimate.response_status == "RESPONSE_OK"
    assert estimate.state_status == "STATE_WITHIN_AUTHOR_RELATIVE_OK"
    assert audit["occupancy_correlation"] > 0.85
    assert audit["transition_order_gain"] > 0.01
    assert audit["heldout_personal_transition_skill"] > 0.01
    assert audit["heldout_shared_transition_skill"] > 0.10
    assert audit["heldout_field_r2"] > 0.0
    assert audit["projection_correlation"] > 0.55
    assert audit["nonlinear_heldout_correlation"] > 0.25
    assert audit["same_author_response_auc"] > 0.70
    assert audit["state_relative_correlation"] > 0.65


def test_truth_projection_is_q0_orthogonal() -> None:
    _, truth, design = generate_m3_kernel_world(
        spec=_small_spec(authors=16, reference_authors=24),
        seed=21_003,
    )
    q0 = design.reference_measure
    coordinates = design.condition_coordinates
    remainder = truth.nonlinear_field
    assert np.max(np.abs(
        np.einsum("c,ucp->up", q0, remainder)
    )) < 1e-10
    assert np.max(np.abs(
        np.einsum("c,cd,ucp->upd", q0, coordinates, remainder)
    )) < 1e-10


def test_protocol_failures_refuse_the_right_claim() -> None:
    cases = {
        "missing_common_support": (
            {"missing_common_support": True},
            "response_status",
            "RESPONSE_REFUSED_NO_COMMON_SUPPORT",
        ),
        "single_occasion": (
            {"single_occasion": True},
            "state_status",
            "STATE_REFUSED_SINGLE_OCCASION",
        ),
        "rank_deficient": (
            {"rank_deficient": True},
            "response_status",
            "RESPONSE_REFUSED_RANK_DEFICIENT",
        ),
        "representation_drift": (
            {"representation_drift": True},
            "response_status",
            "RESPONSE_REFUSED_REPRESENTATION_VERSION",
        ),
        "reference_mismatch": (
            {"reference_mismatch": True},
            "response_status",
            "RESPONSE_REFUSED_REFERENCE_VERSION",
        ),
        "unknown_missingness": (
            {"missingness_mechanism": "UNKNOWN"},
            "response_status",
            "RESPONSE_REFUSED_UNKNOWN_MISSINGNESS",
        ),
    }
    for index, (_, (override, field, expected)) in enumerate(
        cases.items()
    ):
        observed, _, design = generate_m3_kernel_world(
            spec=M3KernelWorldSpec(
                authors=12,
                reference_authors=20,
                train_occasions=3,
                test_occasions=3,
                free_events=20,
                **override,
            ),
            seed=21_100 + index,
        )
        estimate = fit_m3_kernel(observed, design)
        assert getattr(estimate, field) == expected


def test_order_estimator_separates_transition_alias() -> None:
    audit = audit_same_occupancy_different_transition(
        seed=21_200,
        authors_per_group=12,
        occasions=5,
        events=60,
    )
    assert audit["occupancy_centroid_distance"] < 0.10
    assert audit["occupancy_group_accuracy"] <= 0.65
    assert audit["transition_centroid_distance"] > 0.75
    assert audit["transition_group_accuracy"] >= 0.95


def test_null_author_world_does_not_create_identity_signal() -> None:
    observed, truth, design = generate_m3_kernel_world(
        spec=_small_spec(
            authors=36,
            reference_authors=48,
            conditions=25,
            train_occasions=8,
            test_occasions=8,
            fixed_repeats=3,
            free_events=50,
            null_authors=True,
        ),
        seed=101,
    )
    audit = audit_m3_kernel_truth(
        fit_m3_kernel(observed, design),
        truth,
        observed,
        design,
    )
    assert 0.43 <= audit["same_author_response_auc"] <= 0.57
    assert abs(audit["heldout_personal_transition_skill"]) < 0.005


def test_single_occasion_alias_passes_through_and_refuses() -> None:
    observed, _, design = generate_m3_kernel_world(
        spec=_small_spec(
            authors=20,
            reference_authors=32,
            conditions=16,
            single_occasion=True,
        ),
        seed=21_250,
    )
    audit = audit_single_occasion_state_alias(
        observed,
        design,
        seed=21_251,
    )
    assert audit["alias_observable_error"] < 1e-12
    assert audit["alias_stable_truth_difference"] > 0.5
    assert audit["alias_state_truth_difference"] > 0.5
    assert audit["estimator_response_difference"] < 1e-12
    assert audit["state_status_a"] == "STATE_REFUSED_SINGLE_OCCASION"
    assert audit["state_status_b"] == "STATE_REFUSED_SINGLE_OCCASION"


def test_response_geometry_is_rotation_and_translation_invariant() -> None:
    observed, _, design = generate_m3_kernel_world(
        spec=_small_spec(authors=20, reference_authors=32),
        seed=21_300,
    )
    audit = audit_m3_kernel_invariance(
        observed,
        design,
        seed=21_301,
    )
    assert max(
        value
        for key, value in audit.items()
        if key.endswith("_max_abs")
    ) < 1e-10
    assert min(
        value
        for key, value in audit.items()
        if key.endswith("_geometry")
    ) > 0.999999
