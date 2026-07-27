"""Local constrained-response operators for the H4D-R2F frontier."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from suica_core.v8_minority_information_frontier import (
    complete_double_center,
)


def _unit(values: np.ndarray) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    norm = float(np.linalg.norm(result))
    if norm <= 1e-12:
        raise ValueError("cannot normalize a zero geometry")
    return result / norm


def ambient_probe_frame(
    core: np.ndarray,
    halo: np.ndarray,
    *,
    seed: int,
    count: int,
    maximum_attempts: int = 1000,
) -> np.ndarray:
    """Generate deterministic orthonormal probes tangent to core and halo."""
    c = _unit(np.asarray(core, dtype=float))
    h = _unit(np.asarray(halo, dtype=float))
    rng = np.random.default_rng(int(seed))
    axes: list[np.ndarray] = []
    for _ in range(int(maximum_attempts)):
        candidate = complete_double_center(rng.normal(size=c.shape))
        candidate -= float(np.sum(candidate * c)) * c
        candidate -= float(np.sum(candidate * h)) * h
        for axis in axes:
            candidate -= float(np.sum(candidate * axis)) * axis
        norm = float(np.linalg.norm(candidate))
        if norm <= 1e-10:
            continue
        axes.append(candidate / norm)
        if len(axes) == int(count):
            return np.stack(axes, axis=0)
    raise RuntimeError("failed to generate the requested probe frame")


def central_coordinate_jacobian(
    evaluate: Callable[[np.ndarray], np.ndarray],
    probes: np.ndarray,
    *,
    epsilon: float,
    coordinate_scales: np.ndarray,
) -> np.ndarray:
    """Estimate the standardized coordinate Jacobian in probe coefficients."""
    frame = np.asarray(probes, dtype=float)
    scales = np.asarray(coordinate_scales, dtype=float)
    if frame.ndim < 2:
        raise ValueError("probes must be probe x geometry")
    if np.any(scales <= 0.0) or not np.isfinite(scales).all():
        raise ValueError("coordinate scales must be finite and positive")
    columns = []
    for probe in frame:
        positive = np.asarray(
            evaluate(float(epsilon) * probe),
            dtype=float,
        )
        negative = np.asarray(
            evaluate(-float(epsilon) * probe),
            dtype=float,
        )
        if positive.shape != scales.shape or negative.shape != scales.shape:
            raise ValueError("coordinate callback returned an invalid shape")
        columns.append(
            (positive - negative)
            / (2.0 * float(epsilon) * scales)
        )
    return np.column_stack(columns)


def constrained_probe_basis(
    probes: np.ndarray,
    jacobian: np.ndarray,
    *,
    dimensions: int,
    relative_rank_tolerance: float = 1e-8,
    minimum_projected_norm: float = 1e-8,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Project shared probes into the Jacobian kernel deterministically."""
    frame = np.asarray(probes, dtype=float)
    derivative = np.asarray(jacobian, dtype=float)
    if derivative.ndim != 2 or derivative.shape[1] != len(frame):
        raise ValueError("jacobian and probe counts are incompatible")
    _, singular, right = np.linalg.svd(
        derivative,
        full_matrices=True,
    )
    threshold = (
        float(relative_rank_tolerance) * float(singular.max())
        if singular.size
        else 0.0
    )
    rank = int(np.sum(singular > threshold))
    row_space = right[:rank]
    projector = np.eye(len(frame)) - row_space.T @ row_space

    coefficient_axes: list[np.ndarray] = []
    source_indices: list[int] = []
    projected_norms: list[float] = []
    for index in range(len(frame)):
        coefficient = projector[:, index].copy()
        for axis in coefficient_axes:
            coefficient -= float(np.dot(coefficient, axis)) * axis
        norm = float(np.linalg.norm(coefficient))
        if norm <= float(minimum_projected_norm):
            continue
        coefficient_axes.append(coefficient / norm)
        source_indices.append(index)
        projected_norms.append(norm)
        if len(coefficient_axes) == int(dimensions):
            break
    if len(coefficient_axes) != int(dimensions):
        raise RuntimeError("constraint kernel cannot supply enough axes")

    coefficients = np.column_stack(coefficient_axes)
    ambient = np.einsum("pk,p...->k...", coefficients, frame)
    gram = coefficients.T @ coefficients
    residual = derivative @ coefficients
    audit = {
        "jacobian_rank": rank,
        "jacobian_nullity": int(len(frame) - rank),
        "maximum_constraint_residual": float(
            np.linalg.norm(residual, ord=2)
        ),
        "maximum_basis_gram_error": float(
            np.max(np.abs(gram - np.eye(int(dimensions))))
        ),
        "minimum_source_projection_norm": float(min(projected_norms)),
        "source_probe_indices": source_indices,
        "jacobian_singular_values": singular.tolist(),
    }
    return ambient, coefficients, audit


def tangent_geodesic(
    core: np.ndarray,
    halo: np.ndarray,
    tangent_basis: np.ndarray,
    coefficients: np.ndarray,
    *,
    theta: float,
) -> np.ndarray:
    """Move on the fixed-halo-share sphere in local tangent coordinates."""
    c = np.asarray(core, dtype=float)
    h = np.asarray(halo, dtype=float)
    basis = np.asarray(tangent_basis, dtype=float)
    x = np.asarray(coefficients, dtype=float)
    if basis.shape[0] != len(x):
        raise ValueError("coefficient count does not match tangent basis")
    radius = float(np.linalg.norm(x))
    if radius <= 1e-15:
        rotated_halo = h
    else:
        direction = np.einsum("k,k...->...", x / radius, basis)
        rotated_halo = (
            np.cos(radius) * h
            + np.sin(radius) * direction
        )
    return np.cos(float(theta)) * c + np.sin(float(theta)) * rotated_halo


def richardson_gradient_hessian(
    baseline: float,
    axis_probabilities: dict[tuple[int, float, int], float],
    corner_probabilities: dict[tuple[int, int, int, int], float],
    *,
    dimensions: int,
    step: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Estimate local gradient and Hessian from a frozen symmetric stencil."""
    p0 = float(baseline)
    h = float(step)
    gradient = np.zeros(int(dimensions), dtype=float)
    hessian = np.zeros((int(dimensions), int(dimensions)), dtype=float)
    for axis in range(int(dimensions)):
        p_h_plus = float(axis_probabilities[(axis, h, 1)])
        p_h_minus = float(axis_probabilities[(axis, h, -1)])
        p_2h_plus = float(axis_probabilities[(axis, 2.0 * h, 1)])
        p_2h_minus = float(axis_probabilities[(axis, 2.0 * h, -1)])
        derivative_h = (p_h_plus - p_h_minus) / (2.0 * h)
        derivative_2h = (p_2h_plus - p_2h_minus) / (4.0 * h)
        gradient[axis] = (
            4.0 * derivative_h - derivative_2h
        ) / 3.0
        curvature_h = (
            p_h_plus - 2.0 * p0 + p_h_minus
        ) / (h**2)
        curvature_2h = (
            p_2h_plus - 2.0 * p0 + p_2h_minus
        ) / ((2.0 * h) ** 2)
        hessian[axis, axis] = (
            4.0 * curvature_h - curvature_2h
        ) / 3.0
    for left in range(int(dimensions)):
        for right in range(left + 1, int(dimensions)):
            mixed = (
                float(corner_probabilities[(left, right, 1, 1)])
                - float(corner_probabilities[(left, right, 1, -1)])
                - float(corner_probabilities[(left, right, -1, 1)])
                + float(corner_probabilities[(left, right, -1, -1)])
            ) / (4.0 * h**2)
            hessian[left, right] = mixed
            hessian[right, left] = mixed
    return gradient, hessian


def cross_fitted_response_operators(
    gradient_a: np.ndarray,
    gradient_b: np.ndarray,
    hessian_a: np.ndarray,
    hessian_b: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return A/B cross-fitted first- and second-order response operators."""
    g_a = np.asarray(gradient_a, dtype=float)
    g_b = np.asarray(gradient_b, dtype=float)
    h_a = np.asarray(hessian_a, dtype=float)
    h_b = np.asarray(hessian_b, dtype=float)
    if g_a.shape != g_b.shape or g_a.ndim != 2:
        raise ValueError("gradient halves must be parent x dimension")
    if h_a.shape != h_b.shape or h_a.ndim != 3:
        raise ValueError("hessian halves must be parent x dimension x dimension")
    if h_a.shape[0] != g_a.shape[0] or h_a.shape[1:] != (
        g_a.shape[1],
        g_a.shape[1],
    ):
        raise ValueError("gradient and Hessian shapes are incompatible")
    gradient_operator = np.mean(
        0.5
        * (
            np.einsum("ni,nj->nij", g_a, g_b)
            + np.einsum("ni,nj->nij", g_b, g_a)
        ),
        axis=0,
    )
    curvature_operator = np.mean(
        0.5
        * (
            np.einsum("nki,nkj->nij", h_a, h_b)
            + np.einsum("nki,nkj->nij", h_b, h_a)
        ),
        axis=0,
    )
    return gradient_operator, curvature_operator


def ordered_eigensystem(operator: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return descending signed eigenvalues and deterministically signed axes."""
    values, vectors = np.linalg.eigh(np.asarray(operator, dtype=float))
    order = np.argsort(values)[::-1]
    values = values[order]
    vectors = vectors[:, order]
    for column in range(vectors.shape[1]):
        vector = vectors[:, column]
        pivot = int(np.argmax(np.abs(vector)))
        if vector[pivot] < 0.0:
            vectors[:, column] *= -1.0
    return values, vectors
