"""Paired chart-replacement helpers for SUICA M4-C.3.5-R2."""
from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.covariance import LedoitWolf

from .m4_creation_residual_attribution import (
    M4CreationAttributionRoute,
    _current_attribution_route,
    _replace_dynamic,
)
from .m4_fisher_wiener_creation import (
    fit_fixed_hazard_route,
    split_opportunity_occasions,
)
from .m4_opportunity_contracts import M4OpportunityObserved


def truncate_whitened_basis(
    basis: dict[str, np.ndarray],
    *,
    rank: int,
) -> dict[str, np.ndarray]:
    """Keep the mass column and the first ``rank`` whitened coordinates."""
    if rank < 0:
        raise ValueError("rank must be nonnegative")
    output: dict[str, np.ndarray] = {}
    for role, values in basis.items():
        matrix = np.asarray(values, dtype=float)
        if matrix.ndim != 2 or matrix.shape[1] < 1:
            raise ValueError(f"{role} basis must be a nonempty matrix")
        retained = min(int(rank), matrix.shape[1] - 1)
        output[role] = np.column_stack(
            [matrix[:, 0], matrix[:, 1 : retained + 1]]
        )
    return output


def match_nonmass_trace(
    basis: dict[str, np.ndarray],
    target: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Scale each role to the target's centered non-mass trace."""
    output: dict[str, np.ndarray] = {}
    for role, values in basis.items():
        current = np.asarray(values, dtype=float)
        reference = np.asarray(target[role], dtype=float)
        centered = current[:, 1:] - np.mean(
            current[:, 1:],
            axis=0,
            keepdims=True,
        )
        target_centered = reference[:, 1:] - np.mean(
            reference[:, 1:],
            axis=0,
            keepdims=True,
        )
        current_trace = float(np.sum(centered**2))
        target_trace = float(np.sum(target_centered**2))
        if current_trace <= 1e-15 or target_trace <= 1e-15:
            raise ValueError("non-mass trace must be positive")
        scale = np.sqrt(target_trace / current_trace)
        output[role] = np.column_stack(
            [current[:, 0], current[:, 1:] * scale]
        )
    return output


def repeatability_projected_basis(
    transform: Any,
    observed: Any,
    basis: dict[str, np.ndarray],
    *,
    rank: int,
    author_blocks: int = 4,
) -> dict[str, np.ndarray]:
    """Select a fixed-rank repeatable subspace inside the old chart."""
    values = np.asarray(
        observed.reference_calibration.pre_context,
        dtype=float,
    )
    if values.ndim != 4 or values.shape[1] < author_blocks:
        raise ValueError("reference panel cannot support author blocks")
    blocks = np.array_split(np.arange(values.shape[1]), author_blocks)
    coordinates = []
    for indices in blocks:
        current = transform.transform_prototypes(values[:, indices])[:, 1:]
        coordinates.append(
            current - np.mean(current, axis=0, keepdims=True)
        )
    width = coordinates[0].shape[1]
    retained = min(int(rank), width)
    if retained < 1:
        raise ValueError("repeatability control requires positive rank")
    total = np.mean(
        [
            current.T @ current / max(len(current) - 1, 1)
            for current in coordinates
        ],
        axis=0,
    )
    shrinkage = float(
        LedoitWolf().fit(np.vstack(coordinates)).shrinkage_
    )
    trace = float(np.trace(total)) / max(width, 1)
    total = (
        (1.0 - shrinkage) * total
        + shrinkage * trace * np.eye(width)
    )
    cross = []
    for first in range(author_blocks):
        for second in range(first + 1, author_blocks):
            value = (
                coordinates[first].T @ coordinates[second]
                / max(len(coordinates[first]) - 1, 1)
            )
            cross.append(0.5 * (value + value.T))
    repeatable = np.mean(cross, axis=0)
    eigenvalues, eigenvectors = np.linalg.eigh(
        0.5 * (total + total.T)
    )
    inverse = (
        eigenvectors
        @ np.diag(1.0 / np.sqrt(np.maximum(eigenvalues, 1e-10)))
        @ eigenvectors.T
    )
    operator = inverse @ repeatable @ inverse
    values_r, vectors_r = np.linalg.eigh(0.5 * (operator + operator.T))
    selected = vectors_r[:, np.argsort(values_r)[::-1][:retained]]
    projection = inverse @ selected
    return {
        role: np.column_stack(
            [values[:, 0], values[:, 1:] @ projection]
        )
        for role, values in basis.items()
    }


def nonmass_rank_and_trace(
    basis: dict[str, np.ndarray],
) -> dict[str, tuple[int, float]]:
    """Return numerical rank and centered trace for every role."""
    output = {}
    for role, values in basis.items():
        centered = np.asarray(values, dtype=float)[:, 1:]
        centered = centered - np.mean(centered, axis=0, keepdims=True)
        output[role] = (
            int(np.linalg.matrix_rank(centered, tol=1e-10)),
            float(np.sum(centered**2)),
        )
    return output


def rotate_spectral_block_basis(
    basis: dict[str, np.ndarray],
    blocks: tuple[tuple[int, int], ...],
    *,
    seed: int,
) -> dict[str, np.ndarray]:
    """Rotate each non-mass spectral block by one shared orthogonal gauge."""
    width = next(iter(basis.values())).shape[1] - 1
    transform = np.eye(width)
    rng = np.random.default_rng(seed)
    for start, stop in blocks:
        if not (0 <= start < stop <= width):
            raise ValueError("spectral block is outside the basis")
        q, _ = np.linalg.qr(rng.normal(size=(stop - start, stop - start)))
        transform[start:stop, start:stop] = q
    return {
        role: np.column_stack(
            [values[:, 0], values[:, 1:] @ transform]
        )
        for role, values in basis.items()
    }


def linear_cka(first: np.ndarray, second: np.ndarray) -> float:
    """Return centered linear CKA for two condition-coordinate matrices."""
    left = np.asarray(first, dtype=float)
    right = np.asarray(second, dtype=float)
    if left.ndim != 2 or right.ndim != 2 or len(left) != len(right):
        raise ValueError("CKA inputs must be same-row matrices")
    left = left - np.mean(left, axis=0, keepdims=True)
    right = right - np.mean(right, axis=0, keepdims=True)
    cross = left.T @ right
    left_gram = left.T @ left
    right_gram = right.T @ right
    denominator = np.sqrt(
        float(np.sum(left_gram**2)) * float(np.sum(right_gram**2))
    )
    if denominator <= 1e-15:
        return 0.0
    return float(np.sum(cross**2) / denominator)


def basis_oracle_cka(
    basis: dict[str, np.ndarray],
    oracle_basis: dict[str, np.ndarray],
) -> dict[str, float]:
    """Compare every non-mass chart Gram with the oracle condition Gram."""
    return {
        role: linear_cka(
            np.asarray(values, dtype=float)[:, 1:],
            np.asarray(oracle_basis[role], dtype=float)[:, 1:],
        )
        for role, values in basis.items()
    }


def build_current_pooled_attribution_route(
    observed: M4OpportunityObserved,
    basis: dict[str, np.ndarray],
    *,
    model: str = "gate",
    ridge: float = 0.005,
    iterations: int = 30,
    epsilon_scale: float = 1e-6,
    second_permutation: np.ndarray | None = None,
) -> M4CreationAttributionRoute:
    """Fit only the frozen C3.4 ``S=0, P=0`` creation route."""
    parameters: dict[str, Any] = {
        "model": model,
        "ridge": ridge,
        "iterations": iterations,
    }
    full = fit_fixed_hazard_route(observed, basis, **parameters)
    first_observed, second_observed = split_opportunity_occasions(observed)
    first = fit_fixed_hazard_route(first_observed, basis, **parameters)
    second = fit_fixed_hazard_route(second_observed, basis, **parameters)
    pooled = _replace_dynamic(
        full,
        first,
        second,
        epsilon_scale=epsilon_scale,
        second_permutation=second_permutation,
    )
    return _current_attribution_route(pooled, observed, basis)
