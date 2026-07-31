"""Tests for outcome-blind M4 boundary support interventions."""
from __future__ import annotations

import numpy as np

from suica_core.m4_boundary_ecology import (
    intervene_evaluation_support,
    support_geometry,
)
from suica_core.m4_chart_ecology_generator import (
    M4ChartEcologySpec,
    generate_m4_pre_response_condition,
)
from suica_core.m4_response_safe_rcca_chart import (
    fit_response_safe_rcca_chart,
)


def _chart_and_observed():
    spec = M4ChartEcologySpec(
        reference_authors=8,
        mechanism_authors=8,
        reference_calibration_points=24,
        reference_selection_points=16,
        categories=16,
        events=24,
    )
    observed = generate_m4_pre_response_condition(
        world="endogenous_creation_expansion",
        spec=spec,
        seed=571_901,
    )
    chart = fit_response_safe_rcca_chart(
        observed,
        support_permutation_repetitions=19,
        support_bootstrap_repetitions=19,
        canonical_permutation_repetitions=19,
        canonical_bootstrap_repetitions=19,
        null_trials=5,
        minimum_support_stability_lcb=0.0,
        minimum_consensus_eigenvalue=0.0,
        minimum_native_consensus_affinity=0.0,
        minimum_projector_affinity=0.0,
        minimum_heldout_cka=0.0,
        minimum_coverage=0.0,
        seed=571_901,
    )
    return chart, observed


def test_support_geometry_replays_native_coverage() -> None:
    chart, observed = _chart_and_observed()
    geometry = support_geometry(chart, observed)
    assert np.isclose(geometry.minimum_coverage, chart.coverage)
    assert len(geometry.role_masks) == 4


def test_intervention_changes_only_evaluation_pre_context() -> None:
    chart, observed = _chart_and_observed()
    native = support_geometry(chart, observed)
    native_count = int(
        np.sum(native.role_masks["mechanism_evaluation"])
    )
    target = max(native_count - 2, 0)
    intervention = intervene_evaluation_support(
        observed,
        chart,
        target_count=target,
    )
    assert intervention.realized_count == target
    assert len(intervention.selected_conditions) == native_count - target
    assert np.array_equal(
        intervention.observed.mechanism_evaluation.response,
        observed.mechanism_evaluation.response,
    )
    assert np.array_equal(
        intervention.observed.mechanism_calibration.pre_context,
        observed.mechanism_calibration.pre_context,
    )
    assert not np.array_equal(
        intervention.observed.mechanism_evaluation.pre_context,
        observed.mechanism_evaluation.pre_context,
    )
