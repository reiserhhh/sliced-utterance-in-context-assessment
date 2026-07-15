"""Label-free summaries of observable text-expression opportunity.

These helpers deliberately describe only what a sampled text view made
observable: volume, formatting affordances, and sampling cadence.  They do not
encode lexical content, external labels, author identifiers, or subreddit names
as numeric features.  Community overlap is retained separately as a matching
constraint because observed subreddit selection is part of the natural text
process, not a nuisance score to subtract.
"""
from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd


SURFACE_COLUMNS = (
    "log_tokens",
    "log_chars",
    "url_rate",
    "quote_rate",
    "list_rate",
    "code_rate",
    "digit_rate",
    "question_rate",
    "exclamation_rate",
    "punctuation_rate",
)

_COARSE_COLUMNS = ("profile_log_comments", "profile_log_conditions")
_TIME_COLUMNS = (
    "profile_log_span_days",
    "profile_log_median_gap_hours",
    "profile_log_max_gap_days",
    "profile_long_run_share",
)


def profile_columns(layer: str) -> list[str]:
    """Return the frozen numeric matching coordinates for an audit layer."""
    mean = [f"profile_mean::{name}" for name in SURFACE_COLUMNS]
    spread = [f"profile_sd::{name}" for name in SURFACE_COLUMNS]
    layers = {
        "coarse": list(_COARSE_COLUMNS),
        "surface_mean": [*_COARSE_COLUMNS, *mean],
        "surface_distribution": [*_COARSE_COLUMNS, *mean, *spread],
        "surface_time": [*_COARSE_COLUMNS, *mean, *spread, *_TIME_COLUMNS],
    }
    if layer not in layers:
        raise ValueError(f"Unknown opportunity-profile layer: {layer}")
    return layers[layer]


def _safe_log1p(value: float) -> float:
    return float(np.log1p(max(float(value), 0.0)))


def build_opportunity_profiles(
    units: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[tuple[str, str], set[str]]]:
    """Aggregate visible expression-opportunity profiles by author and view.

    ``units`` is the already-filtered technical sample used by the V6 raw-factor
    procedure.  The output is intentionally aggregate-only and is suitable for
    matching a late target to a different author's late text.  It must not be
    interpreted as a psychological score.
    """
    required = {
        "user_id", "half", "condition", "created_utc", "run_len", *SURFACE_COLUMNS,
    }
    missing = sorted(required.difference(units.columns))
    if missing:
        raise ValueError(f"Opportunity profiles require columns: {', '.join(missing)}")

    rows: list[dict[str, float | str]] = []
    condition_sets: dict[tuple[str, str], set[str]] = {}
    for (user_id, half), group in units.groupby(["user_id", "half"], observed=True, sort=False):
        ordered = group.sort_values("created_utc")
        timestamps = ordered["created_utc"].to_numpy(float)
        gaps = np.diff(timestamps)
        positive_gaps = gaps[gaps >= 0.0]
        span_days = (timestamps[-1] - timestamps[0]) / 86400.0 if len(timestamps) > 1 else 0.0
        median_gap_hours = float(np.median(positive_gaps) / 3600.0) if len(positive_gaps) else 0.0
        max_gap_days = float(np.max(positive_gaps) / 86400.0) if len(positive_gaps) else 0.0
        row: dict[str, float | str] = {
            "user_id": str(user_id),
            "half": str(half),
            "profile_log_comments": _safe_log1p(len(ordered)),
            "profile_log_conditions": _safe_log1p(ordered["condition"].nunique()),
            "profile_log_span_days": _safe_log1p(span_days),
            "profile_log_median_gap_hours": _safe_log1p(median_gap_hours),
            "profile_log_max_gap_days": _safe_log1p(max_gap_days),
            "profile_long_run_share": float(np.mean(ordered["run_len"].to_numpy(float) >= 4.0)),
        }
        for column in SURFACE_COLUMNS:
            values = ordered[column].to_numpy(float)
            row[f"profile_mean::{column}"] = float(np.nanmean(values))
            row[f"profile_sd::{column}"] = float(np.nanstd(values, ddof=1)) if len(values) > 1 else 0.0
        rows.append(row)
        condition_sets[(str(user_id), str(half))] = set(ordered["condition"].astype(str))
    return pd.DataFrame(rows), condition_sets


def paired_profile_matrices(
    profiles: pd.DataFrame,
    users: Iterable[str],
    layer: str,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Return aligned early/late profile matrices with nonfitting median fill.

    The caller owns the supplied ``users`` ordering, normally the confirmation
    authors already aligned to a text-representation matrix.  Median filling is
    only a technical guard for degenerate fields and is followed by standardizing
    inside the stranger-matching routine; no outcome or identity information is
    fitted here.
    """
    columns = profile_columns(layer)
    wanted = [str(user) for user in users]
    index = profiles.set_index(["user_id", "half"])
    early = index.reindex([(user, "early") for user in wanted])[columns]
    late = index.reindex([(user, "late") for user in wanted])[columns]
    if early.isna().all(axis=None) or late.isna().all(axis=None):
        raise ValueError("No complete early/late opportunity profiles for requested users")
    combined = np.vstack([early.to_numpy(float), late.to_numpy(float)])
    median = np.nanmedian(combined, axis=0)
    median[~np.isfinite(median)] = 0.0
    early_values = np.where(np.isfinite(early.to_numpy(float)), early.to_numpy(float), median)
    late_values = np.where(np.isfinite(late.to_numpy(float)), late.to_numpy(float), median)
    return early_values, late_values, columns
