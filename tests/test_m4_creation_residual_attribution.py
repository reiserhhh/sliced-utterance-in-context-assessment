"""Tests for M4-C.3.4 creation residual attribution."""
from __future__ import annotations

import numpy as np

from suica_core.m4_chart_ecology_estimator import (
    _hazard_design,
    _hazard_probability,
)
from suica_core.m4_chart_ecology_generator import (
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_creation_residual_attribution import (
    _stratified_creation,
    build_creation_attribution_grid,
    dynamic_indices,
    mobius_effects,
    shapley_effects,
)


def test_dynamic_indices_can_include_gate_block() -> None:
    names = ("intercept", "feedback_0_0", "gate_0_0", "return")
    assert np.array_equal(
        dynamic_indices(names, include_gate=False),
        np.asarray([1]),
    )
    assert np.array_equal(
        dynamic_indices(names, include_gate=True),
        np.asarray([1, 2]),
    )


def test_mobius_and_shapley_recover_additive_cube() -> None:
    values = {
        (c, s, p): 0.2 + 0.1 * c + 0.2 * s - 0.05 * p
        for c in (0, 1)
        for s in (0, 1)
        for p in (0, 1)
    }
    mobius = mobius_effects(values)
    shapley = shapley_effects(values)
    assert np.isclose(mobius["C"], 0.1)
    assert np.isclose(mobius["S"], 0.2)
    assert np.isclose(mobius["P"], -0.05)
    assert np.isclose(mobius["CS"], 0.0)
    assert np.isclose(sum(shapley.values()), values[(1, 1, 1)] - values[(0, 0, 0)])
    assert np.isclose(shapley["S"], 0.2)


def test_source_partition_routes_to_at_risk_creation_law() -> None:
    spec = M4ChartEcologySpec(
        reference_authors=8,
        mechanism_authors=8,
        reference_calibration_points=16,
        reference_selection_points=16,
        categories=16,
        calibration_occasions=4,
        selection_occasions=2,
        evaluation_occasions=2,
        events=24,
    )
    observed, truth = generate_m4_chart_ecology_world(
        world="endogenous_source_partition_matched",
        spec=spec,
        seed=910_247,
    )
    grid = build_creation_attribution_grid(
        observed.ecology,
        truth.oracle_basis,
        iterations=8,
    )
    assert grid.complete_local.source_route_used
    assert not grid.current_local.source_route_used
    expected = (spec.mechanism_authors, spec.categories, spec.response_dimensions)
    assert grid.complete_local.test.creation.shape == expected
    assert np.isfinite(grid.complete_local.test.creation).all()
    assert np.mean(grid.complete_local.test.source_at_risk_valid) >= 0.80


def test_hurdle_derivative_matches_finite_product_difference() -> None:
    basis = np.column_stack(
        [
            np.ones(4),
            np.linspace(-0.8, 0.8, 4),
            np.asarray([0.4, -0.2, 0.6, -0.5]),
        ]
    )
    rows = {
        "choice": np.zeros(3, dtype=int),
        "response_next": np.zeros((3, 2)),
        "history": np.zeros((3, 2)),
        "generated": np.zeros((3, 4), dtype=bool),
        "duration": np.zeros((3, 4)),
    }
    design, names = _hazard_design(rows, basis, model="feedback")
    rng = np.random.default_rng(41)
    risk = rng.normal(scale=0.15, size=design.shape[1])
    allocation = rng.normal(scale=0.15, size=design.shape[1])
    coefficients = {
        "risk_g0": risk[None],
        "risk_g1": risk[None],
        "allocation_g0": allocation[None],
        "allocation_g1": allocation[None],
    }
    analytic = _stratified_creation(
        coefficients,
        names,
        basis,
        2,
        source_route=True,
    )[0]
    finite = np.empty_like(analytic)
    epsilon = 0.05
    for dimension in range(2):
        positive = np.zeros((1, 2))
        negative = np.zeros((1, 2))
        positive[0, dimension] = epsilon
        negative[0, dimension] = -epsilon
        positive_probability = (
            _hazard_probability(
                risk,
                names,
                basis,
                positive,
                np.zeros(1),
            )[0]
            * _hazard_probability(
                allocation,
                names,
                basis,
                positive,
                np.zeros(1),
            )[0]
        )
        negative_probability = (
            _hazard_probability(
                risk,
                names,
                basis,
                negative,
                np.zeros(1),
            )[0]
            * _hazard_probability(
                allocation,
                names,
                basis,
                negative,
                np.zeros(1),
            )[0]
        )
        finite[:, dimension] = (
            positive_probability - negative_probability
        ) / (2.0 * epsilon)
    assert np.allclose(analytic, finite, atol=2e-4)
