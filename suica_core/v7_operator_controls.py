"""Source-level controls for SUICA V7.1 operator boundary audits.

The functions here operate before observation units are built.  This matters
because a fixed-width unit can overlap several comments: resampling or splitting
already-built units would otherwise create artificial agreement through shared
source text.  These diagnostics estimate text-sampling uncertainty only; they
do not establish personality or clinical reliability.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .v7_observations import ObservationSpec, build_observations
from .v7_psychometric import (
    FactorBundle,
    RepresentationRuntime,
    author_features_from_embeddings,
    score_author_features,
)


def _z_factor_columns(scores: pd.DataFrame) -> list[str]:
    """Return frozen factor z-score columns, excluding raw-score coordinates."""
    return [
        column
        for column in scores.columns
        if column.startswith("SU7-FC-") and column.endswith("@v1_z")
    ]


def _source_id_set(frame: pd.DataFrame) -> set[int]:
    """Extract a source-ID set from a canonical source-comment frame."""
    if frame.empty or "source_row" not in frame:
        return set()
    return {int(value) for value in frame["source_row"].dropna().astype(int).tolist()}


def source_disjoint_partition(comments: pd.DataFrame, *, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split each author's source comments into source-disjoint A/B panels.

    The split happens at the raw source-comment level, before slice formation.
    A comment may never contribute to both panels.  This is stricter than the
    previous even/odd-unit check for cross-comment fixed windows.
    """
    if comments.empty:
        return comments.copy(), comments.copy()
    rng = np.random.default_rng(seed)
    left_rows: list[pd.DataFrame] = []
    right_rows: list[pd.DataFrame] = []
    for _, group in comments.groupby("user_id", sort=False, observed=True):
        ordered = group.sort_values(["order", "source_row"], kind="stable").reset_index(drop=True)
        if len(ordered) < 2:
            continue
        order = rng.permutation(len(ordered))
        left_indices = np.sort(order[::2])
        right_indices = np.sort(order[1::2])
        left_rows.append(ordered.iloc[left_indices].copy())
        right_rows.append(ordered.iloc[right_indices].copy())
    if not left_rows or not right_rows:
        return comments.iloc[0:0].copy(), comments.iloc[0:0].copy()
    left = pd.concat(left_rows, ignore_index=True)
    right = pd.concat(right_rows, ignore_index=True)
    overlap = _source_id_set(left).intersection(_source_id_set(right))
    if overlap:
        raise RuntimeError(f"Source-disjoint partition leaked {len(overlap)} source comments.")
    sort_columns = [column for column in ("user_id", "order", "source_row") if column in left]
    return (
        left.sort_values(sort_columns, kind="stable").reset_index(drop=True),
        right.sort_values(sort_columns, kind="stable").reset_index(drop=True),
    )


def bootstrap_source_comments(comments: pd.DataFrame, *, seed: int) -> pd.DataFrame:
    """Cluster-bootstrap source comments within author before operator slicing.

    Draws preserve a `source_origin` column but receive a unique `source_row`
    ID.  Thus duplicate draws do not collapse into one provenance record when a
    fixed-window operator subsequently crosses comment boundaries.
    """
    if comments.empty:
        return comments.copy()
    rng = np.random.default_rng(seed)
    rows: list[pd.DataFrame] = []
    next_source_row = 0
    for _, group in comments.groupby("user_id", sort=False, observed=True):
        ordered = group.sort_values(["order", "source_row"], kind="stable").reset_index(drop=True)
        draw_indices = rng.integers(0, len(ordered), size=len(ordered))
        sampled = ordered.iloc[draw_indices].copy().reset_index(drop=True)
        sampled["source_origin"] = sampled["source_row"].astype(int)
        sampled["source_draw_index"] = np.arange(len(sampled), dtype=int)
        sampled["source_row"] = np.arange(next_source_row, next_source_row + len(sampled), dtype=int)
        next_source_row += len(sampled)
        rows.append(sampled)
    output = pd.concat(rows, ignore_index=True)
    return output.sort_values(["user_id", "order", "source_draw_index"], kind="stable").reset_index(drop=True)


def score_operator_from_comments(
    comments: pd.DataFrame,
    *,
    spec: ObservationSpec,
    representation: RepresentationRuntime,
    bundle: FactorBundle,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build an operator view and score it with frozen representation/bundle."""
    units = build_observations(comments, spec).reset_index(drop=True)
    if units.empty:
        return units, pd.DataFrame(columns=["user_id", "split", "n_units", "n_tokens"]), pd.DataFrame()
    embeddings = representation.transform(units["text"])
    features = author_features_from_embeddings(units, embeddings)
    scores = score_author_features(bundle, features)
    return units, features, scores


def source_disjoint_score_consistency(
    comments: pd.DataFrame,
    *,
    spec: ObservationSpec,
    representation: RepresentationRuntime,
    bundle: FactorBundle,
    seed: int,
    replicate: int,
) -> pd.DataFrame:
    """Score source-disjoint author halves and return factor-level agreement."""
    left_comments, right_comments = source_disjoint_partition(comments, seed=seed)
    left_units, _, left_scores = score_operator_from_comments(
        left_comments, spec=spec, representation=representation, bundle=bundle
    )
    right_units, _, right_scores = score_operator_from_comments(
        right_comments, spec=spec, representation=representation, bundle=bundle
    )
    overlap = _source_id_set(left_comments).intersection(_source_id_set(right_comments))
    if overlap:
        raise RuntimeError("Source overlap found after source-disjoint scoring.")
    factor_columns = _z_factor_columns(left_scores)
    if not factor_columns or right_scores.empty:
        return pd.DataFrame(columns=["operator", "replicate", "factor", "n_users", "correlation"])
    left = left_scores.loc[
        left_scores["split"].eq("confirmation") & left_scores["score_status"].eq("SCORED"),
        ["user_id", *factor_columns],
    ]
    right = right_scores.loc[
        right_scores["split"].eq("confirmation") & right_scores["score_status"].eq("SCORED"),
        ["user_id", *factor_columns],
    ]
    merged = left.merge(right, on="user_id", suffixes=("_left", "_right"))
    rows: list[dict[str, Any]] = []
    for column in factor_columns:
        left_values = merged[f"{column}_left"].to_numpy(float)
        right_values = merged[f"{column}_right"].to_numpy(float)
        valid = np.isfinite(left_values) & np.isfinite(right_values)
        correlation = float("nan")
        if valid.sum() >= 8 and np.std(left_values[valid]) > 1e-12 and np.std(right_values[valid]) > 1e-12:
            correlation = float(np.corrcoef(left_values[valid], right_values[valid])[0, 1])
        rows.append({
            "operator": spec.name,
            "replicate": int(replicate),
            "seed": int(seed),
            "factor": column.removesuffix("_z"),
            "n_users": int(valid.sum()),
            "correlation": correlation,
            "source_overlap_count": int(len(overlap)),
            "left_units": int(len(left_units)),
            "right_units": int(len(right_units)),
        })
    return pd.DataFrame(rows)


def correspondence_permutation_test(
    comments: pd.DataFrame,
    *,
    spec: ObservationSpec,
    representation: RepresentationRuntime,
    bundle: FactorBundle,
    seed: int,
    repetitions: int,
) -> pd.DataFrame:
    """Test whether source-disjoint agreement exceeds random author matching."""
    left_comments, right_comments = source_disjoint_partition(comments, seed=seed)
    _, _, left_scores = score_operator_from_comments(left_comments, spec=spec, representation=representation, bundle=bundle)
    _, _, right_scores = score_operator_from_comments(right_comments, spec=spec, representation=representation, bundle=bundle)
    factor_columns = _z_factor_columns(left_scores)
    left = left_scores.loc[
        left_scores["split"].eq("confirmation") & left_scores["score_status"].eq("SCORED"),
        ["user_id", *factor_columns],
    ]
    right = right_scores.loc[
        right_scores["split"].eq("confirmation") & right_scores["score_status"].eq("SCORED"),
        ["user_id", *factor_columns],
    ]
    merged = left.merge(right, on="user_id", suffixes=("_left", "_right"))
    rng = np.random.default_rng(seed + 1)
    rows: list[dict[str, Any]] = []
    for column in factor_columns:
        left_values = merged[f"{column}_left"].to_numpy(float)
        right_values = merged[f"{column}_right"].to_numpy(float)
        valid = np.isfinite(left_values) & np.isfinite(right_values)
        observed = float("nan")
        null = np.array([], dtype=float)
        if valid.sum() >= 8 and np.std(left_values[valid]) > 1e-12 and np.std(right_values[valid]) > 1e-12:
            observed = float(np.corrcoef(left_values[valid], right_values[valid])[0, 1])
            null = np.asarray([
                np.corrcoef(left_values[valid], rng.permutation(right_values[valid]))[0, 1]
                for _ in range(int(repetitions))
            ])
        empirical_p = float("nan")
        if len(null) and np.isfinite(observed):
            empirical_p = float((1 + np.sum(np.abs(null) >= abs(observed))) / (len(null) + 1))
        rows.append({
            "operator": spec.name,
            "factor": column.removesuffix("_z"),
            "n_users": int(valid.sum()),
            "observed_correlation": observed,
            "null_mean": float(np.mean(null)) if len(null) else float("nan"),
            "null_q025": float(np.quantile(null, 0.025)) if len(null) else float("nan"),
            "null_q975": float(np.quantile(null, 0.975)) if len(null) else float("nan"),
            "empirical_p_two_sided": empirical_p,
            "permutations": int(repetitions),
        })
    return pd.DataFrame(rows)


def source_cluster_bootstrap_z_sem(
    comments: pd.DataFrame,
    *,
    spec: ObservationSpec,
    representation: RepresentationRuntime,
    bundle: FactorBundle,
    repetitions: int,
    seed: int,
) -> pd.DataFrame:
    """Estimate source-comment sampling error of frozen normalized scores.

    Each repetition redraws comments inside author, rebuilds the operator view,
    aggregates author features, then applies the same frozen score map.  It is
    therefore valid for overlapping cross-comment windows and comparable only
    on calibration-normalized (`_z`) coordinates.
    """
    if int(repetitions) < 2:
        raise ValueError("Source-cluster bootstrap needs at least two repetitions.")
    factor_columns = [f"SU7-FC-{index + 1:04d}@v1_z" for index in range(len(bundle.factor_loadings))]
    confirmation_users = comments.loc[comments["split"].eq("confirmation"), "user_id"].astype(str).unique().tolist()
    values: dict[tuple[str, str], list[float]] = {
        (str(user_id), column): [] for user_id in confirmation_users for column in factor_columns
    }
    for replicate in range(int(repetitions)):
        sampled = bootstrap_source_comments(comments, seed=seed + replicate)
        _, _, scores = score_operator_from_comments(sampled, spec=spec, representation=representation, bundle=bundle)
        if scores.empty:
            continue
        confirmation = scores.loc[
            scores["split"].eq("confirmation") & scores["score_status"].eq("SCORED"),
            ["user_id", *factor_columns],
        ]
        for _, row in confirmation.iterrows():
            for column in factor_columns:
                value = float(row[column])
                if np.isfinite(value):
                    values[(str(row["user_id"]), column)].append(value)
    rows: list[dict[str, Any]] = []
    for (user_id, column), draws in values.items():
        array = np.asarray(draws, dtype=float)
        rows.append({
            "operator": spec.name,
            "user_id": user_id,
            "factor": column.removesuffix("_z"),
            "bootstrap_repetitions_observed": int(len(array)),
            "bootstrap_z_sem": float(np.std(array, ddof=1)) if len(array) >= 2 else float("nan"),
            "bootstrap_z_variance": float(np.var(array, ddof=1)) if len(array) >= 2 else float("nan"),
            "sem_status": "SOURCE_CLUSTER_BOOTSTRAP" if len(array) >= 2 else "INSUFFICIENT_BOOTSTRAP_COVERAGE",
        })
    return pd.DataFrame(rows)


def bootstrap_mean_ci(values: np.ndarray | pd.Series, *, seed: int, repetitions: int = 300) -> dict[str, float]:
    """Return a nonparametric CI for a mean without assuming normal errors."""
    array = np.asarray(values, dtype=float)
    array = array[np.isfinite(array)]
    if not len(array):
        return {"mean": float("nan"), "ci_low": float("nan"), "ci_high": float("nan"), "n": 0.0}
    rng = np.random.default_rng(seed)
    draws = np.asarray([
        np.mean(rng.choice(array, size=len(array), replace=True)) for _ in range(int(repetitions))
    ])
    return {
        "mean": float(np.mean(array)),
        "ci_low": float(np.quantile(draws, 0.025)),
        "ci_high": float(np.quantile(draws, 0.975)),
        "n": float(len(array)),
    }


def operator_provenance_qc(comments: pd.DataFrame, units: pd.DataFrame, *, spec: ObservationSpec) -> dict[str, Any]:
    """Summarize source coverage and cross-boundary behavior without raw text."""
    if units.empty:
        return {"operator": spec.name, "n_users": 0, "n_units": 0}
    parsed = units["source_rows"].fillna("").map(
        lambda value: {int(token) for token in str(value).split(",") if token != ""}
    )
    unit_sources = parsed.map(len)
    unit_counts = units.groupby("user_id", observed=True).size()
    unit_tokens = units.groupby("user_id", observed=True)["token_count"].sum()
    input_sources = comments.groupby("user_id", observed=True)["source_row"].apply(lambda values: set(values.astype(int)))
    covered_by_user: dict[str, float] = {}
    for user_id, group in units.assign(_source_set=parsed).groupby("user_id", observed=True):
        used: set[int] = set()
        for value in group["_source_set"]:
            used.update(value)
        denominator = input_sources.get(user_id, set())
        covered_by_user[str(user_id)] = float(len(used) / len(denominator)) if denominator else float("nan")
    return {
        "operator": spec.name,
        "source_boundary_mode": spec.source_boundary_mode if spec.kind == "fixed" else "not_applicable",
        "offset_strategy": spec.offset_strategy if spec.kind == "fixed" else "not_applicable",
        "offset_tokens": int(spec.offset_tokens) if spec.kind == "fixed" else 0,
        "n_users": int(units["user_id"].nunique()),
        "n_units": int(len(units)),
        "median_unit_tokens": float(units["token_count"].median()),
        "median_units_per_user": float(unit_counts.median()),
        "median_operator_tokens_per_user": float(unit_tokens.median()),
        "median_source_rows_per_unit": float(unit_sources.median()),
        "boundary_crossing_rate": float((unit_sources > 1).mean()),
        "median_unique_source_coverage": float(np.nanmedian(list(covered_by_user.values()))),
        "boundary_marker_unit_rate": float(units["text"].str.contains("SUICA_BOUNDARY", regex=False).mean()),
    }
