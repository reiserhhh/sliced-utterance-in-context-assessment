"""Tests for fixed-coverage directional applicability interventions."""
from __future__ import annotations

import numpy as np
import pytest

from suica_core.m4_boundary_ecology import support_geometry
from suica_core.m4_chart_ecology_generator import (
    M4ChartEcologySpec,
    generate_m4_pre_response_condition,
)
from suica_core.m4_directional_applicability import (
    DIRECTION_MODES,
    intervene_evaluation_direction,
)
from suica_core.m4_response_safe_rcca_chart import (
    fit_response_safe_rcca_chart,
)


@pytest.fixture(scope="module")
def chart_and_observed():
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


@pytest.mark.parametrize("mode", DIRECTION_MODES)
def test_directional_interventions_share_exact_support_count(
    chart_and_observed,
    mode: str,
) -> None:
    chart, observed = chart_and_observed
    native = support_geometry(chart, observed)
    native_count = int(np.sum(
        native.role_masks["mechanism_evaluation"]
    ))
    result = intervene_evaluation_direction(
        observed,
        chart,
        target_count=native_count - 2,
        mode=mode,
    )
    assert result.realized_count == native_count - 2
    assert len(result.selected_conditions) == 2
    assert np.array_equal(
        result.observed.mechanism_evaluation.response,
        observed.mechanism_evaluation.response,
    )
    assert np.array_equal(
        result.observed.mechanism_selection.pre_context,
        observed.mechanism_selection.pre_context,
    )


def test_directional_modes_are_not_identical(chart_and_observed) -> None:
    chart, observed = chart_and_observed
    native = support_geometry(chart, observed)
    target = int(np.sum(
        native.role_masks["mechanism_evaluation"]
    )) - 3
    tensors = [
        intervene_evaluation_direction(
            observed,
            chart,
            target_count=target,
            mode=mode,
        ).observed.mechanism_evaluation.pre_context
        for mode in DIRECTION_MODES
    ]
    assert all(
        not np.array_equal(tensors[0], current)
        for current in tensors[1:]
    )


def test_directional_intervention_requires_actual_departure(
    chart_and_observed,
) -> None:
    chart, observed = chart_and_observed
    native = support_geometry(chart, observed)
    native_count = int(np.sum(
        native.role_masks["mechanism_evaluation"]
    ))
    with pytest.raises(ValueError, match="above target"):
        intervene_evaluation_direction(
            observed,
            chart,
            target_count=native_count,
            mode="radial_dispersed",
        )
