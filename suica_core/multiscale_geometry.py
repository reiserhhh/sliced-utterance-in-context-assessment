"""Multiscale, numeric-only neighbourhood diagnostics for paired point clouds."""
from __future__ import annotations

import numpy as np

from suica_core.residual_geometry import (
    _validate_paired,
    neighbour_jaccard_from_lookup,
    neighbour_lookup,
    pairwise_distances,
    top_k_neighbours,
)


def multiscale_neighbour_profile(
    early: np.ndarray,
    late: np.ndarray,
    *,
    scales: tuple[int, ...] = (5, 10, 25, 50, 100, 200),
    iterations: int = 999,
    seed: int = 0,
) -> tuple[list[dict[str, float]], list[dict[str, float]]]:
    """Measure whether local-to-global author neighbourhoods reproduce.

    For each scale ``k``, the statistic is the mean author-wise Jaccard overlap
    between early and late ``k``-nearest-neighbour sets.  The linkage null keeps
    both clouds intact and only permutes which late row belongs to each early row.
    This is a multiscale geometry test, not a clustering or construct test.
    """
    early, late = _validate_paired(early, late)
    if iterations < 99:
        raise ValueError("at least 99 permutations are required")
    n = len(early)
    scales = tuple(sorted({int(k) for k in scales if 1 <= int(k) < n}))
    if not scales:
        raise ValueError("no valid neighbourhood scales")
    early_distance = pairwise_distances(early)
    late_distance = pairwise_distances(late)
    early_neighbours = {k: top_k_neighbours(early_distance, k) for k in scales}
    late_neighbours = {k: top_k_neighbours(late_distance, k) for k in scales}
    early_lookup = {k: neighbour_lookup(early_neighbours[k], n) for k in scales}
    observed = {k: neighbour_jaccard_from_lookup(early_lookup[k], late_neighbours[k], k=k) for k in scales}

    rng = np.random.default_rng(seed)
    base = np.arange(n)
    null_values = {k: [] for k in scales}
    null_rows: list[dict[str, float]] = []
    for draw in range(iterations):
        permutation = rng.permutation(n)
        if np.array_equal(permutation, base):
            permutation = np.roll(permutation, 1)
        inverse = np.empty(n, dtype=int)
        inverse[permutation] = base
        for k in scales:
            # Reindexing gives the neighbour graph of late[permutation] without
            # recomputing any distances inside the permutation loop.
            late_permuted = inverse[late_neighbours[k][permutation]]
            value = neighbour_jaccard_from_lookup(early_lookup[k], late_permuted, k=k)
            null_values[k].append(value)
            null_rows.append({"draw": float(draw), "k": float(k), "neighbour_jaccard": value})

    rows: list[dict[str, float]] = []
    for k in scales:
        null = np.asarray(null_values[k], dtype=float)
        value = observed[k]
        baseline = float(np.mean(null))
        rows.append({
            "k": float(k),
            "neighbour_jaccard": value,
            "null_mean": baseline,
            "null_q95": float(np.quantile(null, 0.95)),
            "permutation_p": float((1 + np.sum(null >= value)) / (iterations + 1)),
            "absolute_excess": float(value - baseline),
            "normalized_excess": float((value - baseline) / max(1.0 - baseline, 1e-12)),
        })
    return rows, null_rows
