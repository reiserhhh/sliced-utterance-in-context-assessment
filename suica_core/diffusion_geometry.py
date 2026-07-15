"""Nonlinear, text-blind geometry diagnostics for paired SUICA numeric clouds.

The routines operate solely on numeric author-by-coordinate matrices. They use
a self-tuning diffusion map to test the narrow alternative that a relational
configuration is curved rather than well represented by stable linear axes.
They do not discover or name psychological constructs.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

from suica_core.residual_geometry import (
    _validate_aligned_rows,
    aligned_geometry_permutation_test,
    neighbour_lookup,
    pairwise_distances,
    top_k_neighbours,
)


@dataclass(frozen=True)
class DiffusionEmbedding:
    """A numeric diffusion embedding and graph diagnostics for one point cloud."""

    coordinates: np.ndarray
    eigenvalues: np.ndarray
    connected_components: int
    eigengap: float


def diffusion_embedding(
    values: np.ndarray,
    *,
    neighbours: int = 25,
    dimensions: int = 3,
    density_alpha: float = 0.5,
    diffusion_time: int = 1,
) -> DiffusionEmbedding:
    """Construct a self-tuning diffusion map from an unlabeled numeric cloud.

    Let ``sigma_i`` be row ``i``'s distance to its kth nearest neighbour. The
    symmetric local affinity is

    ``W_ij = exp(-||x_i-x_j||^2 / (sigma_i sigma_j))``

    on the symmetrized kNN graph. Density normalization uses exponent ``alpha``
    before the symmetric diffusion operator is diagonalized. The leading
    nontrivial coordinates are returned. A disconnected graph is reported so a
    caller can reject a false manifold conclusion.
    """
    values = np.asarray(values, dtype=float)
    if values.ndim != 2 or len(values) < 12:
        raise ValueError("diffusion embedding needs a finite 2-D matrix with at least 12 rows")
    if not np.isfinite(values).all():
        raise ValueError("diffusion embedding requires finite numeric values")
    if not 2 <= neighbours < len(values):
        raise ValueError("neighbours must be between 2 and n_rows - 1")
    if not 1 <= dimensions < len(values) - 1:
        raise ValueError("dimensions must be between 1 and n_rows - 2")
    if not 0.0 <= density_alpha <= 1.0:
        raise ValueError("density_alpha must lie in [0, 1]")
    if diffusion_time < 1:
        raise ValueError("diffusion_time must be positive")

    distances = pairwise_distances(values)
    neighbour_ids = top_k_neighbours(distances, neighbours)
    graph = neighbour_lookup(neighbour_ids)
    graph = graph | graph.T
    components, _ = connected_components(csr_matrix(graph), directed=False, return_labels=True)
    local_scale = np.take_along_axis(distances, neighbour_ids[:, -1:], axis=1).ravel()
    fallback = float(np.median(local_scale[local_scale > 1e-12])) if np.any(local_scale > 1e-12) else 1.0
    local_scale = np.maximum(local_scale, max(fallback, 1e-12))
    denominator = local_scale[:, None] * local_scale[None, :]
    affinity = np.exp(-(distances ** 2) / np.maximum(denominator, 1e-12))
    affinity = np.where(graph, affinity, 0.0)
    np.fill_diagonal(affinity, 0.0)

    density = np.maximum(affinity.sum(axis=1), 1e-12)
    normalized = affinity / ((density[:, None] * density[None, :]) ** density_alpha)
    degree = np.maximum(normalized.sum(axis=1), 1e-12)
    symmetric_operator = normalized / np.sqrt(degree[:, None] * degree[None, :])
    eigenvalues, eigenvectors = np.linalg.eigh(symmetric_operator)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues, eigenvectors = eigenvalues[order], eigenvectors[:, order]
    nontrivial = np.maximum(eigenvalues[1:dimensions + 1], 0.0)
    coordinates = eigenvectors[:, 1:dimensions + 1] * (nontrivial ** diffusion_time)
    eigengap = float(eigenvalues[dimensions] - eigenvalues[dimensions + 1])
    return DiffusionEmbedding(
        coordinates=coordinates,
        eigenvalues=eigenvalues[:dimensions + 2],
        connected_components=int(components),
        eigengap=eigengap,
    )


def diffusion_geometry_audit(
    early: np.ndarray,
    late: np.ndarray,
    *,
    neighbours: int,
    dimensions: int,
    density_alpha: float = 0.5,
    diffusion_time: int = 1,
    permutation_iterations: int = 999,
    seed: int = 0,
) -> tuple[dict[str, float], list[dict[str, float]]]:
    """Test whether a diffusion-coordinate geometry reproduces under row linkage.

    The raw coordinate dimension may differ across calls, but early/late rows
    must align. Results only establish or reject this restricted nonlinear
    geometry under the stated kernel settings.
    """
    early, late = _validate_aligned_rows(early, late)
    early_map = diffusion_embedding(
        early, neighbours=neighbours, dimensions=dimensions,
        density_alpha=density_alpha, diffusion_time=diffusion_time,
    )
    late_map = diffusion_embedding(
        late, neighbours=neighbours, dimensions=dimensions,
        density_alpha=density_alpha, diffusion_time=diffusion_time,
    )
    metrics, null = aligned_geometry_permutation_test(
        early_map.coordinates,
        late_map.coordinates,
        neighbourhood_k=min(10, len(early) - 1),
        iterations=permutation_iterations,
        seed=seed,
    )
    return {
        **metrics,
        "diffusion_neighbours": float(neighbours),
        "diffusion_dimensions": float(dimensions),
        "diffusion_density_alpha": float(density_alpha),
        "diffusion_time": float(diffusion_time),
        "early_connected_components": float(early_map.connected_components),
        "late_connected_components": float(late_map.connected_components),
        "early_eigengap": early_map.eigengap,
        "late_eigengap": late_map.eigengap,
    }, null
