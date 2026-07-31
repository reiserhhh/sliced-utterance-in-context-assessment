"""Tests for the response-safe cross-view EIV chart."""
from __future__ import annotations

from dataclasses import replace

import numpy as np
from scipy.spatial.distance import pdist

from suica_core.m4_chart_ecology_generator import (
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_condition_manifold_contracts import (
    M4ConditionObserved,
    M4ConditionPanel,
)
from suica_core.m4_response_safe_eiv_chart import (
    build_response_safe_basis,
    fit_response_safe_eiv_chart,
    fit_single_view_pca_chart,
)


def _spec() -> M4ChartEcologySpec:
    return M4ChartEcologySpec(
        reference_authors=16,
        mechanism_authors=8,
        reference_calibration_points=40,
        reference_selection_points=32,
        categories=16,
        calibration_occasions=4,
        selection_occasions=2,
        evaluation_occasions=4,
        events=48,
    )


def _mutate_response(
    observed: M4ConditionObserved,
    seed: int,
) -> M4ConditionObserved:
    rng = np.random.default_rng(seed)
    values = {}
    for name in (
        "reference_calibration",
        "reference_selection",
        "mechanism_calibration",
        "mechanism_selection",
        "mechanism_evaluation",
    ):
        panel = getattr(observed, name)
        values[name] = M4ConditionPanel(
            pre_context=panel.pre_context.copy(),
            response=rng.normal(size=panel.response.shape),
            provenance_fields=panel.provenance_fields,
        )
    return M4ConditionObserved(**values, design=dict(observed.design))


def _rotate_pre(
    observed: M4ConditionObserved,
    seed: int,
) -> M4ConditionObserved:
    rng = np.random.default_rng(seed)
    width = observed.reference_calibration.pre_context.shape[-1]
    rotations = []
    for _ in range(2):
        q, _ = np.linalg.qr(rng.normal(size=(width, width)))
        rotations.append(q)
    values = {}
    for name in (
        "reference_calibration",
        "reference_selection",
        "mechanism_calibration",
        "mechanism_selection",
        "mechanism_evaluation",
    ):
        panel = getattr(observed, name)
        pre = panel.pre_context.copy()
        for source in range(2):
            pre[source] = pre[source] @ rotations[source]
        values[name] = replace(panel, pre_context=pre)
    return M4ConditionObserved(**values, design=dict(observed.design))


def _shift_pre(
    observed: M4ConditionObserved,
    shift: float,
) -> M4ConditionObserved:
    values = {}
    for name in (
        "reference_calibration",
        "reference_selection",
        "mechanism_calibration",
        "mechanism_selection",
        "mechanism_evaluation",
    ):
        panel = getattr(observed, name)
        values[name] = replace(
            panel,
            pre_context=panel.pre_context + shift,
        )
    return M4ConditionObserved(**values, design=dict(observed.design))


def test_eiv_chart_ignores_response_bytes() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="endogenous_creation_expansion",
        spec=_spec(),
        seed=101,
    )
    first = fit_response_safe_eiv_chart(
        observed.condition,
        permutation_repetitions=19,
        permutation_seed=303,
        maximum_principal_angle_degrees=90.0,
    )
    second = fit_response_safe_eiv_chart(
        _mutate_response(observed.condition, 707),
        permutation_repetitions=19,
        permutation_seed=303,
        maximum_principal_angle_degrees=90.0,
    )
    assert first.provenance_hash == second.provenance_hash
    assert np.array_equal(
        build_response_safe_basis(first, observed.condition)["evaluation"],
        build_response_safe_basis(second, observed.condition)["evaluation"],
    )


def test_eiv_chart_is_orthogonal_gauge_invariant_in_distance() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="source_rotated_feedback",
        spec=_spec(),
        seed=102,
    )
    rotated = _rotate_pre(observed.condition, 404)
    first = fit_response_safe_eiv_chart(
        observed.condition,
        permutation_repetitions=19,
        permutation_seed=304,
        maximum_principal_angle_degrees=90.0,
    )
    second = fit_response_safe_eiv_chart(
        rotated,
        permutation_repetitions=19,
        permutation_seed=304,
        maximum_principal_angle_degrees=90.0,
    )
    left = build_response_safe_basis(
        first,
        observed.condition,
    )["evaluation"][:, 1:]
    right = build_response_safe_basis(
        second,
        rotated,
    )["evaluation"][:, 1:]
    assert np.max(np.abs(pdist(left) - pdist(right))) < 1e-7


def test_eiv_chart_is_common_shift_invariant_in_distance() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="endogenous_creation_expansion",
        spec=_spec(),
        seed=106,
    )
    shifted = _shift_pre(observed.condition, 13.25)
    first = fit_response_safe_eiv_chart(
        observed.condition,
        permutation_repetitions=19,
        permutation_seed=308,
        maximum_principal_angle_degrees=90.0,
    )
    second = fit_response_safe_eiv_chart(
        shifted,
        permutation_repetitions=19,
        permutation_seed=308,
        maximum_principal_angle_degrees=90.0,
    )
    left = build_response_safe_basis(
        first,
        observed.condition,
    )["evaluation"][:, 1:]
    right = build_response_safe_basis(
        second,
        shifted,
    )["evaluation"][:, 1:]
    assert np.max(np.abs(pdist(left) - pdist(right))) < 1e-10


def test_eiv_chart_refuses_forbidden_provenance() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="author_leakage",
        spec=_spec(),
        seed=103,
    )
    transform = fit_response_safe_eiv_chart(
        observed.condition,
        permutation_repetitions=19,
        permutation_seed=305,
        maximum_principal_angle_degrees=90.0,
    )
    assert transform.refused
    assert any(
        reason.startswith("forbidden_provenance:author_id")
        for reason in transform.refusal_reasons
    )


def test_source_shuffle_does_not_share_the_native_hash() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="endogenous_creation_expansion",
        spec=_spec(),
        seed=104,
    )
    native = fit_response_safe_eiv_chart(
        observed.condition,
        permutation_repetitions=19,
        permutation_seed=306,
        maximum_principal_angle_degrees=90.0,
    )
    shuffled = fit_response_safe_eiv_chart(
        observed.condition,
        permutation_repetitions=19,
        permutation_seed=306,
        maximum_principal_angle_degrees=90.0,
        shuffle_source_two=True,
    )
    assert native.provenance_hash != shuffled.provenance_hash


def test_single_view_control_matches_selected_rank() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="endogenous_creation_expansion",
        spec=_spec(),
        seed=105,
    )
    eiv = fit_response_safe_eiv_chart(
        observed.condition,
        permutation_repetitions=19,
        permutation_seed=307,
        maximum_principal_angle_degrees=90.0,
    )
    control = fit_single_view_pca_chart(
        observed.condition,
        rank=eiv.effective_rank,
    )
    basis = build_response_safe_basis(control, observed.condition)
    assert basis["evaluation"].shape == (
        _spec().categories,
        control.rank + 1,
    )
