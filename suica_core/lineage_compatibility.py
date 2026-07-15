"""Small text-blind numerical primitives for the V6 lineage audit.

The functions here deliberately separate a technical-replicate constructor,
paired reliability contrast, and discovery-only condition subtraction.  None
defines a personality score or consumes external labels.
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from suica_core.suica import tokenize


def span_spread_disjoint_views(
    events: pd.DataFrame,
    *,
    block_size: int,
    blocks_per_view: int,
    time_col: str = "created_utc",
    tie_col: str = "_source_index",
) -> pd.DataFrame:
    """Split one event collection into two time-spread, disjoint block views.

    The method deliberately selects blocks across the whole available timeline,
    then alternates them between technical views.  It prevents an accidental
    early-versus-late comparison while never pretending the views are separate
    human occasions.
    """
    if block_size < 1 or blocks_per_view < 1:
        raise ValueError("block_size and blocks_per_view must be positive")
    required = {time_col, tie_col}
    missing = required.difference(events.columns)
    if missing:
        raise ValueError(f"events lack columns: {sorted(missing)}")
    ordered = events.sort_values([time_col, tie_col], kind="stable").reset_index(drop=True)
    total_blocks = 2 * int(blocks_per_view)
    available_blocks = len(ordered) // int(block_size)
    if available_blocks < total_blocks:
        return pd.DataFrame(columns=[*events.columns, "technical_view", "technical_block", "within_block_index"])
    positions = np.rint(np.linspace(0, available_blocks - 1, total_blocks)).astype(int)
    if len(np.unique(positions)) != total_blocks:
        raise RuntimeError("technical-block positions unexpectedly overlap")
    rows: list[pd.DataFrame] = []
    for chosen, position in enumerate(positions):
        block = ordered.iloc[int(position * block_size):int((position + 1) * block_size)].copy()
        block["technical_view"] = "left" if chosen % 2 == 0 else "right"
        block["technical_block"] = chosen // 2
        block["within_block_index"] = np.arange(len(block), dtype=int)
        rows.append(block)
    return pd.concat(rows, ignore_index=True)


def paired_correlation_delta(
    fixed_left: Sequence[float],
    fixed_right: Sequence[float],
    mixed_left: Sequence[float],
    mixed_right: Sequence[float],
    *,
    bootstrap_iterations: int,
    seed: int,
) -> dict[str, float]:
    """Return the paired fixed-minus-mixed correlation contrast with CI."""
    values = [np.asarray(value, dtype=float) for value in (fixed_left, fixed_right, mixed_left, mixed_right)]
    if len({len(value) for value in values}) != 1 or len(values[0]) < 8:
        raise ValueError("paired correlation contrast requires at least eight aligned authors")

    def corr(left: np.ndarray, right: np.ndarray) -> float:
        if np.std(left) < 1e-12 or np.std(right) < 1e-12:
            return float("nan")
        return float(np.corrcoef(left, right)[0, 1])

    r_fixed = corr(values[0], values[1])
    r_mixed = corr(values[2], values[3])
    rng = np.random.default_rng(seed)
    draws = np.full(int(bootstrap_iterations), np.nan)
    for index in range(int(bootstrap_iterations)):
        take = rng.integers(0, len(values[0]), len(values[0]))
        draws[index] = corr(values[0][take], values[1][take]) - corr(values[2][take], values[3][take])
    return {
        "r_fixed": r_fixed,
        "r_mixed": r_mixed,
        "delta": float(r_fixed - r_mixed),
        "ci_lo": float(np.nanquantile(draws, 0.025)),
        "ci_hi": float(np.nanquantile(draws, 0.975)),
        "bootstrap_finite_fraction": float(np.isfinite(draws).mean()),
    }


def paired_reliability_change(
    first_left: Sequence[float],
    first_right: Sequence[float],
    second_left: Sequence[float],
    second_right: Sequence[float],
    *,
    bootstrap_iterations: int,
    seed: int,
) -> dict[str, float]:
    """Compare two aligned split-half correlations with author bootstrap CI.

    The second-minus-first direction is explicit so callers cannot mistake a
    multivariate retrieval improvement for a scalar reliability improvement.
    """
    values = [np.asarray(value, dtype=float) for value in (first_left, first_right, second_left, second_right)]
    if len({len(value) for value in values}) != 1 or len(values[0]) < 8:
        raise ValueError("paired reliability change requires at least eight aligned authors")

    def corr(left: np.ndarray, right: np.ndarray) -> float:
        if np.std(left) < 1e-12 or np.std(right) < 1e-12:
            return float("nan")
        return float(np.corrcoef(left, right)[0, 1])

    first_r = corr(values[0], values[1])
    second_r = corr(values[2], values[3])
    rng = np.random.default_rng(seed)
    draws = np.full(int(bootstrap_iterations), np.nan)
    for index in range(int(bootstrap_iterations)):
        take = rng.integers(0, len(values[0]), len(values[0]))
        draws[index] = corr(values[2][take], values[3][take]) - corr(values[0][take], values[1][take])
    return {
        "first_r": first_r,
        "second_r": second_r,
        "second_minus_first": float(second_r - first_r),
        "ci_lo": float(np.nanquantile(draws, 0.025)),
        "ci_hi": float(np.nanquantile(draws, 0.975)),
        "bootstrap_finite_fraction": float(np.isfinite(draws).mean()),
    }


def evenly_spread_token_views(
    text: str,
    *,
    slice_tokens: int,
    slices_per_view: int,
) -> list[dict[str, object]]:
    """Make two token-disjoint, timeline-spread views from one text stream.

    This is deliberately a token-slice constructor, not an event-disjoint
    constructor. It is appropriate for the historical PRED-1 token-level
    estimand, but not for evidence about event dynamics or human occasions.
    """
    if slice_tokens < 1 or slices_per_view < 1:
        raise ValueError("slice_tokens and slices_per_view must be positive")
    tokens = tokenize(str(text))
    available = len(tokens) // int(slice_tokens)
    required = 2 * int(slices_per_view)
    if available < required:
        return []
    positions = np.rint(np.linspace(0, available - 1, required)).astype(int)
    if len(np.unique(positions)) != required:
        raise RuntimeError("token-window positions unexpectedly overlap")
    rows: list[dict[str, object]] = []
    for index, position in enumerate(positions):
        start = int(position * slice_tokens)
        end = int(start + slice_tokens)
        rows.append({
            "technical_view": "left" if index % 2 == 0 else "right",
            "slice_index": int(index // 2),
            "token_start": start,
            "token_end": end,
            "slice_text": " ".join(tokens[start:end]),
        })
    return rows


def reference_condition_residuals(
    values: np.ndarray,
    conditions: Sequence[str],
    reference_mask: Sequence[bool],
    *,
    min_reference_events: int,
) -> tuple[np.ndarray, dict[str, int]]:
    """Subtract frozen discovery-only condition means from a feature matrix.

    Unsupported or unseen conditions receive the discovery grand mean.  This
    makes the exposure explicit and prevents confirmation rows from fitting
    their own condition subtraction.
    """
    matrix = np.asarray(values, dtype=float)
    labels = np.asarray([str(value) for value in conditions], dtype=object)
    ref = np.asarray(reference_mask, dtype=bool)
    if matrix.ndim != 2 or len(matrix) != len(labels) or len(ref) != len(labels):
        raise ValueError("values, conditions, and reference_mask must align")
    if not ref.any():
        raise ValueError("reference condition residualization requires reference rows")
    grand_mean = matrix[ref].mean(axis=0)
    means: dict[str, np.ndarray] = {}
    for condition in np.unique(labels[ref]):
        mask = ref & (labels == condition)
        if int(mask.sum()) >= int(min_reference_events):
            means[str(condition)] = matrix[mask].mean(axis=0)
    baseline = np.vstack([means.get(str(condition), grand_mean) for condition in labels])
    metadata = {
        "reference_conditions_supported": int(len(means)),
        "rows_using_global_fallback": int(sum(str(condition) not in means for condition in labels)),
        "reference_rows": int(ref.sum()),
    }
    return matrix - baseline, metadata
