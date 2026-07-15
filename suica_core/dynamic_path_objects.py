"""Frozen primitives for V6 Dynamic Path Stage V1.

The functions here are deliberately agnostic to text and author labels.  They
operate on complete within-condition runs and numeric residual coordinates.  A
caller remains responsible for discovery/endpoint separation and for keeping
whole runs intact.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

import numpy as np


PartitionMode = Literal["transition_balanced", "time_balanced"]


@dataclass(frozen=True)
class RunSegment:
    """Metadata for one complete same-condition chronological run."""

    run_id: str
    condition: str
    start_time: float
    end_time: float
    transitions: int


def _validate_runs(runs: Iterable[RunSegment]) -> list[RunSegment]:
    """Return runs sorted by time and reject malformed transition metadata."""
    ordered = sorted(runs, key=lambda item: (item.start_time, item.end_time, item.run_id))
    if any(item.transitions < 1 for item in ordered):
        raise ValueError("every complete run must contain at least one transition")
    return ordered


def split_complete_runs(
    runs: Iterable[RunSegment],
    *,
    mode: PartitionMode,
) -> tuple[list[RunSegment], list[RunSegment]] | None:
    """Split ordered complete runs once without cutting any run.

    ``transition_balanced`` maximizes the weaker transition total.  ``time_balanced``
    chooses the run boundary closest to the calendar midpoint.  Ties are resolved
    by the earliest boundary, making the operation deterministic.
    """
    ordered = _validate_runs(runs)
    if len(ordered) < 2:
        return None
    candidates = range(1, len(ordered))
    if mode == "transition_balanced":
        total = sum(run.transitions for run in ordered)
        cumulative = np.cumsum([run.transitions for run in ordered])
        cut = max(candidates, key=lambda index: (min(int(cumulative[index - 1]), total - int(cumulative[index - 1])), -index))
    elif mode == "time_balanced":
        midpoint = (ordered[0].start_time + ordered[-1].end_time) / 2.0
        cut = min(candidates, key=lambda index: (abs(ordered[index - 1].end_time - midpoint), index))
    else:
        raise ValueError(f"unknown partition mode: {mode}")
    return ordered[:cut], ordered[cut:]


def has_minimum_support(
    runs: Iterable[RunSegment],
    *,
    min_runs: int,
    min_transitions: int,
) -> bool:
    """Return whether a run collection satisfies frozen support criteria."""
    materialized = list(runs)
    return len(materialized) >= min_runs and sum(run.transitions for run in materialized) >= min_transitions


def condition_jaccard(left: Iterable[RunSegment], right: Iterable[RunSegment]) -> float:
    """Return set-level condition overlap without using text or author identity."""
    a = {run.condition for run in left}
    b = {run.condition for run in right}
    union = a | b
    return float(len(a & b) / len(union)) if union else 0.0


def split_four_subepochs(
    early_runs: Iterable[RunSegment],
    late_runs: Iterable[RunSegment],
    *,
    mode: PartitionMode,
    whole_half_min_runs: int,
    whole_half_min_transitions: int,
    subepoch_min_runs: int,
    subepoch_min_transitions: int,
) -> dict[str, list[RunSegment]] | None:
    """Create four disjoint subepochs or return ``None`` when support fails."""
    early = _validate_runs(early_runs)
    late = _validate_runs(late_runs)
    if not has_minimum_support(early, min_runs=whole_half_min_runs, min_transitions=whole_half_min_transitions):
        return None
    if not has_minimum_support(late, min_runs=whole_half_min_runs, min_transitions=whole_half_min_transitions):
        return None
    split_early = split_complete_runs(early, mode=mode)
    split_late = split_complete_runs(late, mode=mode)
    if split_early is None or split_late is None:
        return None
    subepochs = {
        "early_0": split_early[0], "early_1": split_early[1],
        "late_0": split_late[0], "late_1": split_late[1],
    }
    if not all(has_minimum_support(value, min_runs=subepoch_min_runs,
                                   min_transitions=subepoch_min_transitions)
               for value in subepochs.values()):
        return None
    return subepochs


def lagged_pairs(path: np.ndarray, lag: int) -> tuple[np.ndarray, np.ndarray]:
    """Return non-overlapping-coordinate lagged source and target observations."""
    array = np.asarray(path, dtype=float)
    if array.ndim != 2 or len(array) <= lag or lag < 1:
        raise ValueError("path must be two-dimensional and longer than positive lag")
    if not np.isfinite(array).all():
        raise ValueError("path contains non-finite values")
    return array[:-lag], array[lag:]


def equal_run_weighted_mean(vectors: Iterable[np.ndarray]) -> np.ndarray:
    """Average numeric run summaries so prolific runs do not dominate an author."""
    values = [np.asarray(value, dtype=float) for value in vectors]
    if not values:
        raise ValueError("at least one run summary is required")
    if any(value.ndim != 1 or not np.isfinite(value).all() for value in values):
        raise ValueError("run summaries must be finite one-dimensional vectors")
    width = values[0].shape[0]
    if any(value.shape[0] != width for value in values):
        raise ValueError("run summaries have inconsistent widths")
    return np.mean(np.vstack(values), axis=0)


def second_order_run_summary(path: np.ndarray, lag: int) -> np.ndarray:
    """Return the lagged second-moment matrix flattened in row-major order."""
    source, target = lagged_pairs(path, lag)
    delta = target - source
    return (delta.T @ delta / len(delta)).ravel()


def standardized_norm(values: np.ndarray, mean: np.ndarray, covariance: np.ndarray) -> np.ndarray:
    """Return Mahalanobis norms with a numerically safe symmetric inverse root."""
    array = np.asarray(values, dtype=float)
    centre = np.asarray(mean, dtype=float)
    cov = np.asarray(covariance, dtype=float)
    if array.ndim != 2 or centre.shape != (array.shape[1],) or cov.shape != (array.shape[1], array.shape[1]):
        raise ValueError("values, mean, and covariance shapes are incompatible")
    eigenvalues, eigenvectors = np.linalg.eigh((cov + cov.T) / 2.0)
    eigenvalues = np.maximum(eigenvalues, 1e-8)
    inverse_root = (eigenvectors / np.sqrt(eigenvalues)) @ eigenvectors.T
    return np.linalg.norm((array - centre) @ inverse_root, axis=1)


def top_quantile_event_mask(
    values: np.ndarray,
    *,
    quantile: float,
) -> np.ndarray:
    """Mark values at or above a fixed discovery-derived quantile threshold."""
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or not np.isfinite(array).all():
        raise ValueError("values must be a finite one-dimensional array")
    if not 0.0 < quantile < 1.0:
        raise ValueError("quantile must lie strictly between zero and one")
    return array >= float(np.quantile(array, quantile))
