"""Privacy-preserving statistics for the MEPS fixed-condition vector pilot.

The functions in this module receive only aligned numeric similarity matrices
and text-length metadata.  They never receive raw text, participant IDs, or
questionnaire data.  The measured object is deliberately narrow: whether a
frozen embedding represents the *same participant's* responses to two shared
MEPS prompts as more similar than responses from other participants.

This is neither a personality score nor a cross-language equivalence test.
"""
from __future__ import annotations

from typing import Any

import numpy as np


def auc_probability(positive: np.ndarray, negative: np.ndarray) -> float:
    """Return P(positive > negative) + 0.5 P(tie), the rank AUC.

    The input arrays can have unequal sizes.  Non-finite entries are excluded
    rather than silently converted to zeros.
    """
    positive = np.asarray(positive, dtype=float)
    negative = np.asarray(negative, dtype=float)
    positive = positive[np.isfinite(positive)]
    negative = negative[np.isfinite(negative)]
    if not len(positive) or not len(negative):
        return float("nan")
    ordered = np.sort(negative)
    left = np.searchsorted(ordered, positive, side="left")
    right = np.searchsorted(ordered, positive, side="right")
    return float((left.sum() + 0.5 * (right - left).sum()) / (len(positive) * len(ordered)))


def _validate_similarity(similarity: np.ndarray) -> np.ndarray:
    matrix = np.asarray(similarity, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("similarity must be a square aligned participant matrix")
    if len(matrix) < 4:
        raise ValueError("at least four aligned participants are required")
    if not np.isfinite(matrix).all():
        raise ValueError("similarity must be finite")
    return matrix


def _off_diagonal_values(matrix: np.ndarray) -> np.ndarray:
    return matrix[~np.eye(len(matrix), dtype=bool)]


def _derangement(rng: np.random.Generator, size: int) -> np.ndarray:
    """Generate a derangement so a null draw never accidentally keeps a link."""
    base = np.arange(size)
    for _ in range(100):
        candidate = rng.permutation(size)
        if not np.any(candidate == base):
            return candidate
    # Deterministic fallback is still a valid complete unlinking operation.
    return np.roll(base, 1)


def _length_matched_negatives(
    similarity: np.ndarray,
    right_characters: np.ndarray,
    *,
    log_tolerance: float,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Return positives and length-matched strangers for each left participant.

    Matching only the right-side condition holds the available response volume
    in that prompt approximately fixed.  It is a sensitivity analysis, not a
    fitted residualization or a replacement for experimental opportunity
    control.
    """
    n = len(similarity)
    logs = np.log1p(np.asarray(right_characters, dtype=float))
    positives: list[float] = []
    negatives: list[float] = []
    covered = 0
    for row in range(n):
        candidate = np.flatnonzero(np.abs(logs - logs[row]) <= log_tolerance)
        candidate = candidate[candidate != row]
        if not len(candidate):
            continue
        covered += 1
        positives.append(float(similarity[row, row]))
        negatives.extend(similarity[row, candidate].astype(float).tolist())
    return np.asarray(positives), np.asarray(negatives), covered / n


def _cluster_bootstrap_auc(
    similarity: np.ndarray,
    *,
    bootstrap_draws: int,
    seed: int,
    log_tolerance: float | None = None,
    right_characters: np.ndarray | None = None,
) -> tuple[float, float]:
    """Participant-cluster bootstrap CI for a matched-vs-stranger AUC.

    Each resampled participant contributes one matched value and its permitted
    stranger set from the original matrix.  This avoids treating all n*(n-1)
    pairs as independent observations.
    """
    n = len(similarity)
    rng = np.random.default_rng(seed)
    values: list[float] = []
    if log_tolerance is not None:
        if right_characters is None:
            raise ValueError("right_characters is required for length-matched bootstrap")
        logs = np.log1p(np.asarray(right_characters, dtype=float))
        candidate_sets = [
            np.array([j for j in range(n) if j != i and abs(logs[j] - logs[i]) <= log_tolerance], dtype=int)
            for i in range(n)
        ]
    else:
        candidate_sets = [np.array([j for j in range(n) if j != i], dtype=int) for i in range(n)]
    for _ in range(bootstrap_draws):
        rows = rng.integers(0, n, size=n)
        positive = similarity[rows, rows]
        negatives = [similarity[row, candidate_sets[row]] for row in rows if len(candidate_sets[row])]
        if not negatives:
            continue
        values.append(auc_probability(positive, np.concatenate(negatives)))
    if not values:
        return float("nan"), float("nan")
    return tuple(float(value) for value in np.quantile(values, [0.025, 0.975]))


def _cluster_bootstrap_gap(
    individual_gaps: np.ndarray,
    *,
    bootstrap_draws: int,
    seed: int,
) -> tuple[float, float]:
    """Participant-cluster bootstrap CI for a mean matched-minus-stranger gap."""
    values = np.asarray(individual_gaps, dtype=float)
    values = values[np.isfinite(values)]
    if not len(values):
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    draws = np.array([np.mean(values[rng.integers(0, len(values), len(values))]) for _ in range(bootstrap_draws)])
    return tuple(float(value) for value in np.quantile(draws, [0.025, 0.975]))


def paired_embedding_summary(
    similarity: np.ndarray,
    right_characters: np.ndarray,
    *,
    bootstrap_draws: int = 1999,
    permutation_draws: int = 4999,
    log_length_tolerance: float = 0.25,
    seed: int = 20260714,
) -> dict[str, Any]:
    """Summarize one frozen, aligned condition-pair comparison.

    The primary statistic is a same-person versus stranger AUC.  A row-linkage
    permutation tests the mean matched cosine, while the participant bootstrap
    provides an uncertainty interval that respects participant clustering.
    """
    matrix = _validate_similarity(similarity)
    right_characters = np.asarray(right_characters, dtype=float)
    if right_characters.shape != (len(matrix),):
        raise ValueError("right_characters must contain one value per aligned participant")
    positive = np.diag(matrix)
    strangers = _off_diagonal_values(matrix)
    individual_stranger_means = np.array(
        [np.mean(matrix[row, np.arange(len(matrix)) != row]) for row in range(len(matrix))], dtype=float
    )
    gaps = positive - individual_stranger_means
    auc_ci_low, auc_ci_high = _cluster_bootstrap_auc(
        matrix, bootstrap_draws=bootstrap_draws, seed=seed
    )
    gap_ci_low, gap_ci_high = _cluster_bootstrap_gap(
        gaps, bootstrap_draws=bootstrap_draws, seed=seed + 1
    )
    matched_lengths, matched_strangers, length_coverage = _length_matched_negatives(
        matrix, right_characters, log_tolerance=log_length_tolerance
    )
    length_auc_ci_low, length_auc_ci_high = _cluster_bootstrap_auc(
        matrix,
        bootstrap_draws=bootstrap_draws,
        seed=seed + 2,
        log_tolerance=log_length_tolerance,
        right_characters=right_characters,
    )
    rng = np.random.default_rng(seed + 3)
    observed_mean = float(np.mean(positive))
    null = np.array([
        np.mean(matrix[np.arange(len(matrix)), _derangement(rng, len(matrix))])
        for _ in range(permutation_draws)
    ])
    return {
        "n_participants": int(len(matrix)),
        "matched_mean_cosine": observed_mean,
        "stranger_mean_cosine": float(np.mean(strangers)),
        "matched_minus_stranger": float(np.mean(gaps)),
        "matched_minus_stranger_ci_low": gap_ci_low,
        "matched_minus_stranger_ci_high": gap_ci_high,
        "same_person_auc": auc_probability(positive, strangers),
        "same_person_auc_ci_low": auc_ci_low,
        "same_person_auc_ci_high": auc_ci_high,
        "linkage_permutation_p": float((1 + np.sum(null >= observed_mean)) / (permutation_draws + 1)),
        "length_matched_coverage": float(length_coverage),
        "length_matched_same_person_auc": auc_probability(matched_lengths, matched_strangers),
        "length_matched_auc_ci_low": length_auc_ci_low,
        "length_matched_auc_ci_high": length_auc_ci_high,
        "log_length_tolerance": float(log_length_tolerance),
        "bootstrap_draws": int(bootstrap_draws),
        "permutation_draws": int(permutation_draws),
    }
