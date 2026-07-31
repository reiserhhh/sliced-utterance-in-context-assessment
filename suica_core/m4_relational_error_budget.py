"""Relational error coordinates for M4-C.3.1."""
from __future__ import annotations

from itertools import combinations
import math

import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import rankdata, spearmanr

from .m4_physical_edge_composition import EDGE_NAMES


def centered_author_vectors(values: np.ndarray) -> np.ndarray:
    """Flatten physical actions and quotient their common author mode."""
    matrix = np.asarray(values, dtype=float).reshape(len(values), -1)
    return matrix - np.mean(matrix, axis=0, keepdims=True)


def relational_distance(values: np.ndarray) -> np.ndarray:
    """Return the upper-triangle author-distance vector."""
    return pdist(centered_author_vectors(values))


def standardized_midranks(distance: np.ndarray) -> np.ndarray:
    """Map distances to the unit midrank sphere used by Spearman geometry."""
    ranks = rankdata(np.asarray(distance, dtype=float), method="average")
    centered = ranks - np.mean(ranks)
    norm = np.linalg.norm(centered)
    if norm <= 1e-12:
        return np.zeros_like(centered)
    return centered / norm


def spearman_loss(
    oracle_distance: np.ndarray,
    candidate_distance: np.ndarray,
) -> float:
    """Return one minus Spearman relation geometry."""
    if (
        np.std(oracle_distance) <= 1e-12
        or np.std(candidate_distance) <= 1e-12
    ):
        return 1.0
    value = float(
        spearmanr(oracle_distance, candidate_distance).statistic
    )
    return 1.0 - (value if np.isfinite(value) else 0.0)


def spearman_loss_identity_error(
    oracle_distance: np.ndarray,
    candidate_distance: np.ndarray,
) -> float:
    """Check the exact midrank-sphere representation of Spearman loss."""
    first = standardized_midranks(oracle_distance)
    second = standardized_midranks(candidate_distance)
    represented = 0.5 * float(np.sum((first - second) ** 2))
    return abs(
        spearman_loss(oracle_distance, candidate_distance)
        - represented
    )


def normalized_gram(values: np.ndarray) -> np.ndarray:
    """Return a trace-normalized centered author Gram matrix."""
    centered = centered_author_vectors(values)
    gram = centered @ centered.T
    trace = float(np.trace(gram))
    return gram / trace if trace > 1e-12 else np.zeros_like(gram)


def gram_diagnostics(
    oracle: np.ndarray,
    candidate: np.ndarray,
) -> tuple[float, float]:
    """Return normalized Gram distortion and centered-kernel alignment."""
    first = normalized_gram(oracle)
    second = normalized_gram(candidate)
    distortion = float(np.linalg.norm(first - second))
    denominator = max(
        float(np.linalg.norm(first) * np.linalg.norm(second)),
        1e-12,
    )
    cka = float(np.sum(first * second) / denominator)
    return distortion, cka


def _subset_key(subset: frozenset[str]) -> str:
    return "".join(
        "D" if edge in subset else "O"
        for edge in EDGE_NAMES
    )


def shapley_relational_loss(
    losses: dict[str, float],
) -> dict[str, float]:
    """Allocate a complete three-edge relational loss game."""
    edges = tuple(EDGE_NAMES)
    count = len(edges)
    values = {
        frozenset(subset): losses[_subset_key(frozenset(subset))]
        for size in range(count + 1)
        for subset in combinations(edges, size)
    }
    output = {}
    for edge in edges:
        value = 0.0
        remaining = [candidate for candidate in edges if candidate != edge]
        for size in range(count):
            for subset_values in combinations(remaining, size):
                subset = frozenset(subset_values)
                weight = (
                    math.factorial(size)
                    * math.factorial(count - size - 1)
                    / math.factorial(count)
                )
                value += weight * (
                    values[subset | {edge}] - values[subset]
                )
        output[edge] = float(value)
    return output


def relational_mobius_budget(
    loops: dict[str, np.ndarray],
) -> dict[str, float | np.ndarray]:
    """Decompose distance change through second order without using DDD."""
    distances = {
        key: relational_distance(values)
        for key, values in loops.items()
    }
    baseline = distances["OOO"]
    single = {
        "creation": distances["DOO"] - baseline,
        "response": distances["ODO"] - baseline,
        "choice": distances["OOD"] - baseline,
    }
    pair = {
        "creation_response": (
            distances["DDO"]
            - distances["DOO"]
            - distances["ODO"]
            + baseline
        ),
        "creation_choice": (
            distances["DOD"]
            - distances["DOO"]
            - distances["OOD"]
            + baseline
        ),
        "response_choice": (
            distances["ODD"]
            - distances["ODO"]
            - distances["OOD"]
            + baseline
        ),
    }
    predicted = (
        baseline
        + sum(single.values())
        + sum(pair.values())
    )
    actual = distances["DDD"]
    third_order = actual - predicted
    actual_loss = spearman_loss(baseline, actual)
    predicted_loss = spearman_loss(baseline, predicted)
    losses = {
        key: spearman_loss(baseline, distance)
        for key, distance in distances.items()
    }
    shapley = shapley_relational_loss(losses)
    gram_distortion, gram_cka = gram_diagnostics(
        loops["OOO"],
        loops["DDD"],
    )
    denominator = max(float(np.linalg.norm(actual - baseline)), 1e-12)
    return {
        "actual_loss": actual_loss,
        "predicted_second_order_loss": predicted_loss,
        "prediction_absolute_error": abs(predicted_loss - actual_loss),
        "third_order_relative_norm": (
            float(np.linalg.norm(third_order)) / denominator
        ),
        "mobius_reconstruction_error": float(
            np.max(np.abs(predicted + third_order - actual))
        ),
        "spearman_identity_error": max(
            spearman_loss_identity_error(baseline, distance)
            for distance in distances.values()
        ),
        "shapley_efficiency_error": abs(
            sum(shapley.values()) - actual_loss
        ),
        "gram_distortion": gram_distortion,
        "gram_cka": gram_cka,
        "oracle_distance_iqr": float(
            np.subtract(*np.quantile(baseline, [0.75, 0.25]))
        ),
        "distance_perturbation_median": float(
            np.median(np.abs(actual - baseline))
        ),
        **{
            f"shapley_loss_{edge}": value
            for edge, value in shapley.items()
        },
        **{
            f"single_norm_{edge}": float(np.linalg.norm(value))
            for edge, value in single.items()
        },
        **{
            f"pair_norm_{edge}": float(np.linalg.norm(value))
            for edge, value in pair.items()
        },
    }


def relational_invariance_error(
    values: np.ndarray,
    *,
    seed: int,
) -> float:
    """Check translation, positive scale, and shared orthogonal invariance."""
    matrix = np.asarray(values, dtype=float).reshape(len(values), -1)
    rng = np.random.default_rng(seed)
    q, _ = np.linalg.qr(rng.normal(size=(matrix.shape[1], matrix.shape[1])))
    translation = rng.normal(size=(1, matrix.shape[1]))
    transformed = 3.7 * (matrix @ q) + translation
    first = standardized_midranks(relational_distance(matrix))
    second = standardized_midranks(relational_distance(transformed))
    return float(np.max(np.abs(first - second)))
