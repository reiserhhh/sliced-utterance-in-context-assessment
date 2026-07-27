from __future__ import annotations

import numpy as np

from suica_core.v8_local_response_operator import (
    ambient_probe_frame,
    constrained_probe_basis,
    cross_fitted_response_operators,
    ordered_eigensystem,
    richardson_gradient_hessian,
    tangent_geodesic,
)
from suica_core.v8_minority_information_frontier import (
    complete_double_center,
)


def _frame() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(7)
    core = complete_double_center(rng.normal(size=(8, 6, 3)))
    core /= np.linalg.norm(core)
    halo = complete_double_center(rng.normal(size=core.shape))
    halo -= np.sum(halo * core) * core
    halo /= np.linalg.norm(halo)
    return core, halo


def test_constrained_basis_is_orthogonal_and_in_jacobian_kernel() -> None:
    core, halo = _frame()
    probes = ambient_probe_frame(core, halo, seed=11, count=10)
    jacobian = np.zeros((3, 10))
    jacobian[0, 0] = 1.0
    jacobian[1, 1] = 1.0
    jacobian[2, 2] = 1.0
    basis, coefficients, audit = constrained_probe_basis(
        probes,
        jacobian,
        dimensions=4,
    )
    assert basis.shape == (4, *core.shape)
    assert np.allclose(coefficients.T @ coefficients, np.eye(4))
    assert np.linalg.norm(jacobian @ coefficients) < 1e-12
    assert audit["jacobian_rank"] == 3
    assert audit["jacobian_nullity"] == 7
    assert max(abs(np.sum(axis * core)) for axis in basis) < 1e-12
    assert max(abs(np.sum(axis * halo)) for axis in basis) < 1e-12


def test_tangent_geodesic_preserves_norm_and_core_share() -> None:
    core, halo = _frame()
    probes = ambient_probe_frame(core, halo, seed=12, count=4)
    theta = float(np.arcsin(np.sqrt(0.01)))
    q = tangent_geodesic(
        core,
        halo,
        probes,
        np.asarray([0.2, -0.1, 0.0, 0.1]),
        theta=theta,
    )
    assert np.isclose(np.linalg.norm(q), 1.0)
    assert np.isclose(np.sum(q * core) ** 2, 0.99)


def test_richardson_stencil_recovers_quadratic_derivatives() -> None:
    dimensions = 3
    gradient = np.asarray([0.2, -0.1, 0.05])
    hessian = np.asarray([
        [0.4, 0.1, -0.2],
        [0.1, -0.3, 0.05],
        [-0.2, 0.05, 0.2],
    ])
    baseline = 0.4

    def probability(x: np.ndarray) -> float:
        return float(
            baseline
            + gradient @ x
            + 0.5 * x @ hessian @ x
        )

    step = 0.1
    axes: dict[tuple[int, float, int], float] = {}
    corners: dict[tuple[int, int, int, int], float] = {}
    for axis in range(dimensions):
        for magnitude in (step, 2.0 * step):
            for sign in (-1, 1):
                x = np.zeros(dimensions)
                x[axis] = sign * magnitude
                axes[(axis, magnitude, sign)] = probability(x)
    for left in range(dimensions):
        for right in range(left + 1, dimensions):
            for left_sign in (-1, 1):
                for right_sign in (-1, 1):
                    x = np.zeros(dimensions)
                    x[left] = left_sign * step
                    x[right] = right_sign * step
                    corners[(left, right, left_sign, right_sign)] = (
                        probability(x)
                    )
    observed_gradient, observed_hessian = richardson_gradient_hessian(
        baseline,
        axes,
        corners,
        dimensions=dimensions,
        step=step,
    )
    assert np.allclose(observed_gradient, gradient)
    assert np.allclose(observed_hessian, hessian)


def test_cross_fitted_operator_removes_independent_additive_noise() -> None:
    rng = np.random.default_rng(23)
    true_gradient = rng.normal(size=(20000, 3))
    gradient_a = true_gradient + rng.normal(size=true_gradient.shape)
    gradient_b = true_gradient + rng.normal(size=true_gradient.shape)
    true_hessian = rng.normal(size=(20000, 3, 3))
    true_hessian = 0.5 * (
        true_hessian + true_hessian.transpose(0, 2, 1)
    )
    hessian_a = true_hessian + rng.normal(size=true_hessian.shape)
    hessian_b = true_hessian + rng.normal(size=true_hessian.shape)
    observed_g, observed_h = cross_fitted_response_operators(
        gradient_a,
        gradient_b,
        hessian_a,
        hessian_b,
    )
    expected_g = np.mean(
        np.einsum("ni,nj->nij", true_gradient, true_gradient),
        axis=0,
    )
    expected_h = np.mean(
        np.einsum("nki,nkj->nij", true_hessian, true_hessian),
        axis=0,
    )
    assert np.allclose(observed_g, expected_g, atol=0.05)
    assert np.allclose(observed_h, expected_h, atol=0.12)
    values, vectors = ordered_eigensystem(observed_g)
    assert np.all(np.diff(values) <= 0.0)
    for vector in vectors.T:
        assert vector[np.argmax(np.abs(vector))] >= 0.0
