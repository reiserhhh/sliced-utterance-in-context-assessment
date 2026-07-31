"""Tests for M4-C.2 chart-covariant opportunity ecology."""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from suica_core.m4_chart_ecology_audit import audit_m4_chart_ecology
from suica_core.m4_chart_ecology_contracts import (
    validate_chart_ecology_observed,
)
from suica_core.m4_chart_ecology_estimator import (
    build_m4_discovered_basis,
    fit_m4_chart_ecology,
    fit_m4_chart_ecology_route,
    rotate_whitened_basis,
    route_action_max_difference,
)
from suica_core.m4_chart_ecology_generator import (
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)


SPEC = M4ChartEcologySpec(
    reference_authors=10,
    mechanism_authors=8,
    reference_calibration_points=32,
    reference_selection_points=24,
    categories=16,
    calibration_occasions=2,
    selection_occasions=1,
    evaluation_occasions=2,
    events=40,
)

CANDIDATES = (
    {
        "family": "linear_pca",
        "dimensions": 2,
        "neighbors": 6,
        "landmarks": 10,
    },
    {
        "family": "landmark_atlas",
        "dimensions": 2,
        "neighbors": 6,
        "landmarks": 10,
    },
)

ROUTE = {
    "ridge_grid": (0.001, 0.01),
    "hazard_ridge": 0.01,
    "logistic_iterations": 8,
    "complexity_penalty": 0.00001,
    "alias_match_threshold": 0.999,
}


def _fit(world: str, seed: int = 811):
    observed, truth = generate_m4_chart_ecology_world(
        world=world,
        spec=SPEC,
        seed=seed,
    )
    estimate = fit_m4_chart_ecology(
        observed,
        candidates=CANDIDATES,
        minimum_coverage=0.45,
        minimum_evaluation_coverage=0.45,
        route_parameters=ROUTE,
    )
    return observed, truth, estimate


def test_generator_is_reproducible_and_reference_authors_are_disjoint() -> None:
    first, first_truth = generate_m4_chart_ecology_world(
        world="linear_exogenous_selection",
        spec=SPEC,
        seed=801,
    )
    second, second_truth = generate_m4_chart_ecology_world(
        world="linear_exogenous_selection",
        spec=SPEC,
        seed=801,
    )
    assert not (
        set(first.reference_calibration_author_ids)
        & set(first.reference_selection_author_ids)
    )
    assert np.allclose(
        first.condition.reference_calibration.pre_context,
        second.condition.reference_calibration.pre_context,
    )
    assert np.allclose(
        first_truth.oracle_basis["evaluation"],
        second_truth.oracle_basis["evaluation"],
    )


def test_matched_worlds_share_the_exact_union_menu_envelope() -> None:
    selection, _ = generate_m4_chart_ecology_world(
        world="linear_exogenous_selection",
        spec=SPEC,
        seed=807,
    )
    creation, _ = generate_m4_chart_ecology_world(
        world="endogenous_source_partition_matched",
        spec=SPEC,
        seed=807,
    )
    for name in (
        "train_calibration",
        "train_selection",
        "train_evaluation",
        "test_calibration",
        "test_selection",
        "test_evaluation",
    ):
        assert np.array_equal(
            getattr(selection.ecology, name).menu,
            getattr(creation.ecology, name).menu,
        )
        assert np.array_equal(
            getattr(selection.ecology, name).environment,
            getattr(creation.ecology, name).environment,
        )
    for name in (
        "reference_calibration",
        "reference_selection",
        "mechanism_calibration",
        "mechanism_selection",
        "mechanism_evaluation",
    ):
        assert np.array_equal(
            getattr(selection.condition, name).pre_context,
            getattr(creation.condition, name).pre_context,
        )


def test_reference_author_overlap_is_rejected() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="linear_null_ecology",
        spec=SPEC,
        seed=802,
    )
    invalid = replace(
        observed,
        reference_selection_author_ids=(
            observed.reference_calibration_author_ids
        ),
    )
    with pytest.raises(ValueError, match="must be disjoint"):
        validate_chart_ecology_observed(invalid)


def test_frozen_transform_does_not_read_separate_response_tensor() -> None:
    observed, _, estimate = _fit(
        "linear_exogenous_selection",
        seed=803,
    )
    changed_condition = replace(
        observed.condition,
        mechanism_evaluation=replace(
            observed.condition.mechanism_evaluation,
            response=np.zeros_like(
                observed.condition.mechanism_evaluation.response
            ),
        ),
    )
    changed = replace(observed, condition=changed_condition)
    changed_estimate = fit_m4_chart_ecology(
        changed,
        candidates=CANDIDATES,
        minimum_coverage=0.45,
        minimum_evaluation_coverage=0.45,
        route_parameters=ROUTE,
    )
    assert estimate.transform_hash == changed_estimate.transform_hash
    assert estimate.chart.selected_family == changed_estimate.chart.selected_family
    assert estimate.chart.selected_parameters == (
        changed_estimate.chart.selected_parameters
    )


def test_whitened_basis_refit_is_physically_gauge_invariant() -> None:
    observed, _, estimate = _fit(
        "linear_exogenous_selection",
        seed=804,
    )
    _, basis = build_m4_discovered_basis(observed, estimate.chart)
    rotated = fit_m4_chart_ecology_route(
        observed.ecology,
        rotate_whitened_basis(basis, seed=991),
        basis_name="rotated",
        **ROUTE,
    )
    assert route_action_max_difference(estimate.discovered, rotated) < 1e-4


def test_hidden_source_alias_is_refused() -> None:
    _, _, estimate = _fit(
        "hidden_opportunity_source_alias",
        seed=805,
    )
    assert estimate.refused is True
    assert "hidden_opportunity_source_alias" in estimate.refusal_reasons
    assert np.mean(
        estimate.discovered.train_refusal
        & estimate.discovered.test_refusal
    ) >= 0.95


def test_condition_alias_is_underresolved_after_oracle_check() -> None:
    observed, truth, estimate = _fit(
        "condition_alias_ecology",
        seed=806,
    )
    oracle = fit_m4_chart_ecology_route(
        observed.ecology,
        truth.oracle_basis,
        basis_name="oracle",
        **ROUTE,
    )
    result = audit_m4_chart_ecology(
        estimate,
        oracle,
        truth,
        selection_threshold=0.20,
        creation_threshold=0.01,
        gate_threshold=0.08,
        return_threshold=0.08,
        minimum_conditional_skill=0.50,
        minimum_alias_oracle_skill=0.50,
        minimum_alias_skill_gap=0.20,
        maximum_alias_retained_ratio=0.70,
        alias_bootstrap_repetitions=500,
        alias_bootstrap_seed=97531,
        basis_action_invariant=True,
        response_perturbation_invariant=True,
    )
    assert result["alias_oracle_skill"] >= 0.50
    assert result["alias_skill_gap"] >= 0.20
    assert result["alias_retained_ratio"] <= 0.70
    assert result["alias_skill_gap_lcb"] > 0.0
    assert result["truth_open_alias_information_loss"] == 1.0
