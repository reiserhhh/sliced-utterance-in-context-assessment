"""Tests for M4-C.3 physical-edge composition diagnostics."""
from __future__ import annotations

import numpy as np

from suica_core.m4_chart_ecology_estimator import (
    fit_m4_chart_ecology_route,
    rotate_whitened_basis,
)
from suica_core.m4_chart_ecology_generator import (
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_physical_edge_composition import (
    fit_m4_physical_edge_route,
    inject_physical_edge_fault,
    mixed_physical_loops,
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

ROUTE = {
    "ridge_grid": (0.001, 0.01),
    "hazard_ridge": 0.01,
    "logistic_iterations": 8,
    "complexity_penalty": 0.00001,
    "alias_match_threshold": 0.999,
}


def _routes(seed: int = 901):
    observed, truth = generate_m4_chart_ecology_world(
        world="history_gated_ecology",
        spec=SPEC,
        seed=seed,
    )
    legacy = fit_m4_chart_ecology_route(
        observed.ecology,
        truth.oracle_basis,
        basis_name="oracle",
        **ROUTE,
    )
    physical = fit_m4_physical_edge_route(
        observed.ecology,
        truth.oracle_basis,
        basis_name="oracle",
        **ROUTE,
    )
    return observed, truth, legacy, physical


def test_physical_product_reproduces_registered_loop() -> None:
    _, _, legacy, physical = _routes()
    assert np.allclose(
        physical.train.jacobian_loop,
        legacy.train_metrics["loop_kernel"],
        atol=1e-10,
        rtol=1e-10,
    )
    assert np.allclose(
        physical.test.jacobian_loop,
        legacy.test_metrics["loop_kernel"],
        atol=1e-10,
        rtol=1e-10,
    )
    assert np.max(physical.train.projection_error) < 1e-10
    assert np.max(physical.train.legacy_loop_difference) < 1e-10


def test_physical_edges_are_invariant_to_orthogonal_chart_gauge() -> None:
    observed, truth, _, physical = _routes(seed=902)
    rotated_basis = rotate_whitened_basis(
        truth.oracle_basis,
        seed=9902,
    )
    rotated = fit_m4_physical_edge_route(
        observed.ecology,
        rotated_basis,
        basis_name="rotated",
        **ROUTE,
    )
    for name in (
        "creation",
        "response",
        "choice",
        "jacobian_loop",
        "finite_loop",
    ):
        assert np.allclose(
            getattr(physical.train, name),
            getattr(rotated.train, name),
            atol=1e-7,
            rtol=1e-7,
        )


def test_mixed_loop_endpoints_equal_supplied_routes() -> None:
    _, _, _, oracle = _routes(seed=903)
    fault = inject_physical_edge_fault(
        oracle.train,
        edge="response",
        strength=0.3,
        seed=1903,
    )
    loops = mixed_physical_loops(oracle.train, fault)
    assert np.allclose(loops["OOO"], oracle.train.jacobian_loop)
    assert np.allclose(loops["DDD"], fault.jacobian_loop)
    assert np.allclose(loops["ODO"], fault.jacobian_loop)
    assert not np.allclose(
        loops["DOO"],
        fault.jacobian_loop,
    )
