"""Contract tests for the M4-C.3.5-R1 response-safe RCCA chart."""
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
)
from suica_core.m4_response_safe_rcca_chart import (
    build_response_safe_rcca_basis,
    fit_response_safe_rcca_chart,
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
        events=32,
    )


def _parameters(seed: int) -> dict[str, object]:
    return {
        "support_permutation_repetitions": 19,
        "support_bootstrap_repetitions": 19,
        "canonical_permutation_repetitions": 19,
        "canonical_bootstrap_repetitions": 19,
        "null_trials": 5,
        "minimum_projector_affinity": 0.0,
        "minimum_heldout_cka": 0.0,
        "minimum_coverage": 0.0,
        "maximum_negative_mass": 1.0,
        "maximum_asymmetric_mass": 1.0,
        "seed": seed,
    }


def _map_panels(
    observed: M4ConditionObserved,
    function: object,
) -> M4ConditionObserved:
    values = {
        name: function(getattr(observed, name))
        for name in (
            "reference_calibration",
            "reference_selection",
            "mechanism_calibration",
            "mechanism_selection",
            "mechanism_evaluation",
        )
    }
    return M4ConditionObserved(**values, design=dict(observed.design))


def test_rcca_identifies_a_bounded_shared_spectral_block() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="endogenous_source_partition_matched",
        spec=_spec(),
        seed=201,
    )
    chart = fit_response_safe_rcca_chart(
        observed.condition,
        **_parameters(401),
    )
    assert chart.shared_rank_lower == chart.shared_rank_upper
    assert chart.shared_rank >= 1
    assert chart.spectral_blocks[-1][1] == chart.shared_rank
    assert np.max(chart.canonical_singular_values) <= 1.0 + 1e-8
    assert max(chart.condition_numbers) <= 100.0


def test_rcca_ignores_all_response_bytes() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="endogenous_source_partition_matched",
        spec=_spec(),
        seed=202,
    )
    rng = np.random.default_rng(777)
    mutated = _map_panels(
        observed.condition,
        lambda panel: replace(
            panel,
            response=rng.normal(size=panel.response.shape),
        ),
    )
    first = fit_response_safe_rcca_chart(
        observed.condition,
        **_parameters(402),
    )
    second = fit_response_safe_rcca_chart(
        mutated,
        **_parameters(402),
    )
    assert first.provenance_hash == second.provenance_hash
    assert np.array_equal(
        build_response_safe_rcca_basis(
            first,
            observed.condition,
        )["evaluation"],
        build_response_safe_rcca_basis(
            second,
            mutated,
        )["evaluation"],
    )


def test_rcca_is_orthogonal_gauge_invariant_in_distance() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="source_rotated_feedback",
        spec=_spec(),
        seed=203,
    )
    rng = np.random.default_rng(778)
    width = observed.condition.reference_calibration.pre_context.shape[-1]
    rotations = [
        np.linalg.qr(rng.normal(size=(width, width)))[0]
        for _ in range(2)
    ]

    def rotate(panel: object) -> object:
        pre = panel.pre_context.copy()
        for source in range(2):
            pre[source] = pre[source] @ rotations[source]
        return replace(panel, pre_context=pre)

    rotated = _map_panels(observed.condition, rotate)
    first = fit_response_safe_rcca_chart(
        observed.condition,
        **_parameters(403),
    )
    second = fit_response_safe_rcca_chart(
        rotated,
        **_parameters(403),
    )
    left = build_response_safe_rcca_basis(
        first,
        observed.condition,
    )["evaluation"][:, 1:]
    right = build_response_safe_rcca_basis(
        second,
        rotated,
    )["evaluation"][:, 1:]
    assert np.max(np.abs(pdist(left) - pdist(right))) < 1e-7


def test_rcca_is_common_shift_invariant_in_distance() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="endogenous_creation_expansion",
        spec=_spec(),
        seed=204,
    )
    shifted = _map_panels(
        observed.condition,
        lambda panel: replace(
            panel,
            pre_context=panel.pre_context + 19.25,
        ),
    )
    first = fit_response_safe_rcca_chart(
        observed.condition,
        **_parameters(404),
    )
    second = fit_response_safe_rcca_chart(
        shifted,
        **_parameters(404),
    )
    left = build_response_safe_rcca_basis(
        first,
        observed.condition,
    )["evaluation"][:, 1:]
    right = build_response_safe_rcca_basis(
        second,
        shifted,
    )["evaluation"][:, 1:]
    assert np.max(np.abs(pdist(left) - pdist(right))) < 1e-10


def test_rcca_refuses_forbidden_provenance() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="author_leakage",
        spec=_spec(),
        seed=205,
    )
    chart = fit_response_safe_rcca_chart(
        observed.condition,
        **_parameters(405),
    )
    assert chart.refused
    assert any(
        reason.startswith("FORBIDDEN_PROVENANCE:author_id")
        for reason in chart.refusal_reasons
    )


def test_rcca_source_shuffle_has_no_confirmed_shared_rank() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="endogenous_source_partition_matched",
        spec=_spec(),
        seed=206,
    )
    chart = fit_response_safe_rcca_chart(
        observed.condition,
        shuffle_source_two=True,
        **_parameters(406),
    )
    assert chart.shared_rank_lower == 0
    assert chart.refused
    assert "NO_SHARED_CROSS_SOURCE_BLOCK" in chart.refusal_reasons


def test_rcca_keeps_exact_observable_aliases_identical() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="condition_alias_ecology",
        spec=_spec(),
        seed=207,
    )
    panel = observed.condition.mechanism_evaluation
    pre = panel.pre_context.copy()
    pre[:, :, 1] = pre[:, :, 0]
    aliased = replace(
        observed.condition,
        mechanism_evaluation=replace(panel, pre_context=pre),
    )
    chart = fit_response_safe_rcca_chart(
        aliased,
        **_parameters(407),
    )
    basis = build_response_safe_rcca_basis(chart, aliased)["evaluation"]
    assert np.array_equal(basis[0], basis[1])
