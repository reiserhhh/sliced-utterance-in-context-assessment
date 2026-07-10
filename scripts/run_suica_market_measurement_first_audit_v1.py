#!/usr/bin/env python
"""Measurement-first SUICA audit on the trading-agent X archive.

This research harness deliberately separates two questions:

1. Does the frozen SUICA v4 scorer produce stable author coordinates when
   rind and occasion boundaries are preserved?
2. Do population aggregates of those coordinates contain contemporaneous or
   forward market information beyond collection volume?

The script is read-only with respect to the trading databases. It never writes
predictions, runtime state, or broker intents. Outputs contain aggregate data
only; raw post text and account identifiers are never exported.
"""
from __future__ import annotations

import argparse
import json
import math
import sqlite3
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.suica_v4_lib import (  # noqa: E402
    ANCHOR_LEXICONS_V4,
    score_text_anchors_v4,
    tokenize,
)


DEFAULT_INTELLIGENCE_DB = Path(
    "/Volumes/projects/trading-agent/trading-agent-main/data/private/intelligence_store.sqlite"
)
DEFAULT_MARKET_DB = Path(
    "/Volumes/projects/trading-agent/trading-agent-main/data/private/market_data.sqlite"
)
DEFAULT_OUTPUT_DIR = ROOT / "results" / "suica_market_measurement_first_v1"

SCORE_COLUMNS = (
    "first_person_usage_v2",
    "directive_action_v2",
    "novelty_play_v2",
    "tension_core_v2",
    "negative_affect_rate",
    "positive_affect_rate",
    "uncertainty_rate",
    "certainty_rate",
    "conflict_threat_rate",
    "affect_balance",
    "certainty_balance",
)

STATE_COLUMNS = (
    "tension_core_v2",
    "negative_affect_rate",
    "positive_affect_rate",
    "uncertainty_rate",
    "certainty_rate",
    "conflict_threat_rate",
    "affect_balance",
    "certainty_balance",
)

PROVIDER_PRIORITY = {
    "yfinance": 0,
    "jquants": 1,
    "eodhd": 2,
}


@dataclass(frozen=True)
class AuditConfig:
    language: str = "en"
    slice_tokens: int = 128
    min_slice_tokens: int = 24
    min_posts_per_cell: int = 1
    min_prior_occasions: int = 2
    min_common_rinds: int = 1
    min_reliability_authors: int = 30
    min_market_authors: int = 10
    min_symbols_per_week: int = 5
    permutation_trials: int = 2000
    random_seed: int = 20260710


def connect_readonly(path: Path) -> sqlite3.Connection:
    """Open SQLite in read-only mode without creating sidecar files."""
    if not path.exists():
        raise FileNotFoundError(path)
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def week_start(values: pd.Series) -> pd.Series:
    ts = pd.to_datetime(values, utc=True, errors="coerce", format="mixed")
    return (ts.dt.normalize() - pd.to_timedelta(ts.dt.weekday, unit="D")).dt.strftime("%Y-%m-%d")


def collector_regime(timestamp: pd.Series) -> pd.Series:
    """Known collection-design phases recovered from the archive audit."""
    ts = pd.to_datetime(timestamp, utc=True, errors="coerce", format="mixed")
    out = pd.Series("phase_18symbol", index=timestamp.index, dtype="object")
    out.loc[ts >= pd.Timestamp("2026-05-18", tz="UTC")] = "phase_expanded"
    out.loc[ts >= pd.Timestamp("2026-06-22", tz="UTC")] = "phase_highvolume"
    return out


def load_posts(
    path: Path,
    language: str,
    *,
    parquet_path: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load the minimum X fields needed for measurement and audit the funnel."""
    if parquet_path is not None:
        posts = pd.read_parquet(parquet_path)
        snapshot_rows = int(len(posts))
        manifest_path = parquet_path.with_name("snapshot_manifest.json")
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            total = int(manifest.get("database_total_posts", snapshot_rows))
        else:
            total = snapshot_rows
    else:
        con = connect_readonly(path)
        try:
            total = int(con.execute("SELECT COUNT(*) FROM x_posts").fetchone()[0])
            sql = """
            SELECT post_id,
                   account_id AS user_id,
                   timestamp,
                   COALESCE(symbol, '') AS symbol,
                   COALESCE(query_group, '') AS query_group,
                   COALESCE(lang, '') AS lang,
                   text,
                   source_run_id
            FROM x_posts
            WHERE lang = ?
              AND account_id IS NOT NULL
              AND timestamp IS NOT NULL
              AND text IS NOT NULL
              AND LENGTH(TRIM(text)) > 0
              AND LENGTH(TRIM(COALESCE(symbol, ''))) > 0
              AND LENGTH(TRIM(COALESCE(query_group, ''))) > 0
            ORDER BY timestamp, post_id
            """
            posts = pd.read_sql_query(sql, con, params=[language])
        finally:
            con.close()

    loaded = len(posts)
    posts["user_id"] = posts["user_id"].astype(str)
    posts["post_id"] = posts["post_id"].astype(str)
    posts["symbol"] = posts["symbol"].astype(str).str.strip().str.upper()
    posts["query_group"] = posts["query_group"].astype(str).str.strip()
    posts["timestamp"] = pd.to_datetime(
        posts["timestamp"], utc=True, errors="coerce", format="mixed"
    )
    posts = posts.dropna(subset=["timestamp"])
    posts["normalized_text"] = (
        posts["text"].astype(str).str.lower().str.replace(r"\s+", " ", regex=True).str.strip()
    )
    duplicate_mask = posts.duplicated(["user_id", "normalized_text"], keep="first")
    duplicate_rows = int(duplicate_mask.sum())
    posts = posts.loc[~duplicate_mask].copy()
    posts = posts.drop(columns="normalized_text")
    posts["week_start"] = week_start(posts["timestamp"])
    posts["collector_regime"] = collector_regime(posts["timestamp"])
    # Collector rules are not participant-selected psychological conditions.
    # Keep them as strict slice boundaries, but use symbol as the primary rind.
    posts["collector_context_id"] = posts["symbol"] + "|" + posts["query_group"]
    posts["measurement_rind_id"] = posts["symbol"]

    query_counts = posts["query_group"].value_counts()

    audit = {
        "database_total_posts": total,
        "snapshot_rows_loaded": loaded,
        "language": language,
        "eligible_rows_before_dedup": loaded,
        "exact_within_author_text_duplicates_removed": duplicate_rows,
        "eligible_rows_after_dedup": int(len(posts)),
        "distinct_authors": int(posts["user_id"].nunique()),
        "distinct_symbols": int(posts["symbol"].nunique()),
        "distinct_measurement_rinds": int(posts["measurement_rind_id"].nunique()),
        "distinct_collector_contexts": int(posts["collector_context_id"].nunique()),
        "distinct_query_groups": int(posts["query_group"].nunique()),
        "singleton_query_groups": int((query_counts == 1).sum()),
        "combined_query_group_rows": int(posts["query_group"].str.contains(r"\|\|", regex=True).sum()),
        "min_timestamp": posts["timestamp"].min().isoformat() if not posts.empty else None,
        "max_timestamp": posts["timestamp"].max().isoformat() if not posts.empty else None,
        "collector_regime_rows": {str(k): int(v) for k, v in posts["collector_regime"].value_counts().items()},
    }
    return posts, audit


def pack_cell_posts(
    group: pd.DataFrame,
    *,
    slice_tokens: int,
    min_slice_tokens: int,
) -> list[dict[str, Any]]:
    """Pack complete posts into slices without crossing a rind/occasion cell."""
    slices: list[dict[str, Any]] = []
    current: list[str] = []
    current_post_ids: list[str] = []

    def flush() -> None:
        nonlocal current, current_post_ids
        if len(current) >= min_slice_tokens:
            slices.append(
                {
                    "slice_text": " ".join(current),
                    "token_count": len(current),
                    "source_post_count": len(set(current_post_ids)),
                }
            )
        current = []
        current_post_ids = []

    for row in group.sort_values(["timestamp", "post_id"]).itertuples(index=False):
        tokens = tokenize(str(row.text))
        if not tokens:
            continue
        for start in range(0, len(tokens), slice_tokens):
            part = tokens[start : start + slice_tokens]
            if current and len(current) + len(part) > slice_tokens:
                flush()
            if len(part) >= slice_tokens:
                if current:
                    flush()
                slices.append(
                    {
                        "slice_text": " ".join(part),
                        "token_count": len(part),
                        "source_post_count": 1,
                    }
                )
                continue
            current.extend(part)
            current_post_ids.append(str(row.post_id))
    flush()
    return slices


def build_slices(posts: pd.DataFrame, config: AuditConfig) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build slices inside author x collector-context x week boundaries."""
    rows: list[dict[str, Any]] = []
    group_cols = [
        "user_id",
        "measurement_rind_id",
        "collector_context_id",
        "symbol",
        "query_group",
        "week_start",
        "collector_regime",
    ]
    groups_seen = 0
    groups_with_slices = 0
    for keys, group in posts.groupby(group_cols, sort=False):
        groups_seen += 1
        if len(group) < config.min_posts_per_cell:
            continue
        packed = pack_cell_posts(
            group,
            slice_tokens=config.slice_tokens,
            min_slice_tokens=config.min_slice_tokens,
        )
        if not packed:
            continue
        groups_with_slices += 1
        metadata = dict(zip(group_cols, keys))
        for slice_index, item in enumerate(packed):
            rows.append({**metadata, "slice_index": slice_index, **item})
    slices = pd.DataFrame(rows)
    if slices.empty:
        raise RuntimeError("No eligible SUICA slices were produced")
    audit = {
        "author_rind_week_cells_seen": groups_seen,
        "author_rind_week_cells_with_slices": groups_with_slices,
        "slice_count": int(len(slices)),
        "authors_with_slices": int(slices["user_id"].nunique()),
        "symbols_with_slices": int(slices["symbol"].nunique()),
        "measurement_rinds_with_slices": int(slices["measurement_rind_id"].nunique()),
        "collector_contexts_with_slices": int(slices["collector_context_id"].nunique()),
        "median_tokens_per_slice": float(slices["token_count"].median()),
        "median_source_posts_per_slice": float(slices["source_post_count"].median()),
    }
    return slices, audit


_WORD_TO_CATEGORY = {
    word: category
    for category, words in ANCHOR_LEXICONS_V4.items()
    for word in words
}


def score_anchor_fast(text: str) -> dict[str, float]:
    """Exact fast path for the disjoint SUICA v4 anchor dictionary."""
    toks = tokenize(text)
    word_count = max(1, sum(tok != "?" for tok in toks))
    counts = Counter(_WORD_TO_CATEGORY.get(tok) for tok in toks)
    out = {
        f"{category}_rate": 100.0 * counts.get(category, 0) / word_count
        for category in ANCHOR_LEXICONS_V4
    }
    out["question_mark_rate"] = 100.0 * toks.count("?") / word_count
    out["token_count_anchor"] = float(word_count)
    other = out["second_person_rate"] + out["third_person_rate"] + out["general_people_rate"]
    out["self_other_balance"] = out["self_focus_rate"] - other
    out["agency_communion_balance"] = out["agency_rate"] - out["communion_rate"]
    out["affect_balance"] = out["positive_affect_rate"] - out["negative_affect_rate"]
    out["temporal_balance"] = out["past_temporal_rate"] - out["future_temporal_rate"]
    out["certainty_balance"] = out["certainty_rate"] - out["uncertainty_rate"]
    out["narrative_integration_rate"] = (
        out["mentalization_rate"] + out["temporal_sequence_rate"] + out["causal_meaning_rate"]
    )
    out["projective_tension_rate"] = (
        out["negative_affect_rate"] + out["conflict_threat_rate"] + out["uncertainty_rate"]
    )
    out["directive_interpersonal_blend"] = math.sqrt(
        max(0.0, out["directive_rate"]) * max(0.0, out["second_person_rate"])
    )
    out["growth_after_tension_blend"] = math.sqrt(
        max(0.0, out["redemption_growth_rate"])
        * max(0.0, out["conflict_threat_rate"] + out["negative_affect_rate"])
    )
    return out


def score_slices(slices: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Score aggregate slices with the frozen v4 equations."""
    sample = slices["slice_text"].head(25).tolist()
    max_diff = 0.0
    for text in sample:
        reference = score_text_anchors_v4(text)
        fast = score_anchor_fast(text)
        max_diff = max(max_diff, max(abs(reference[k] - fast[k]) for k in reference))
    if max_diff > 1e-12:
        raise AssertionError(f"Fast v4 scorer mismatch: {max_diff}")

    rates = pd.DataFrame([score_anchor_fast(text) for text in slices["slice_text"]], index=slices.index)
    out = pd.concat([slices.drop(columns="slice_text"), rates], axis=1)
    out["first_person_usage_v2"] = out["self_focus_rate"]
    out["directive_action_v2"] = out["directive_interpersonal_blend"]
    out["novelty_play_v2"] = out["novelty_play_rate"]
    out["tension_core_v2"] = (
        0.40 * out["projective_tension_rate"]
        + 0.35 * out["uncertainty_rate"]
        + 0.25 * out["conflict_threat_rate"]
    )
    return out, {"official_fast_scorer_max_abs_diff": max_diff, "scorer_version": "SUICA v4"}


def fisher_ci(r: float, n: int) -> tuple[float, float]:
    if n <= 3 or not np.isfinite(r) or abs(r) >= 1:
        return float("nan"), float("nan")
    z = np.arctanh(r)
    width = 1.96 / math.sqrt(n - 3)
    return float(np.tanh(z - width)), float(np.tanh(z + width))


def safe_corr(x: Iterable[float], y: Iterable[float]) -> tuple[float, int]:
    frame = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(frame) < 4 or frame["x"].nunique() < 2 or frame["y"].nunique() < 2:
        return float("nan"), len(frame)
    return float(stats.pearsonr(frame["x"], frame["y"]).statistic), len(frame)


def permutation_p_correlation(
    x: np.ndarray,
    y: np.ndarray,
    *,
    trials: int,
    seed: int,
) -> float:
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 4 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    observed = abs(float(np.corrcoef(x, y)[0, 1]))
    rng = np.random.default_rng(seed)
    exceed = 0
    for _ in range(trials):
        perm = rng.permutation(y)
        candidate = abs(float(np.corrcoef(x, perm)[0, 1]))
        exceed += candidate >= observed
    return float((exceed + 1) / (trials + 1))


def reliability_rows(scored: pd.DataFrame, config: AuditConfig) -> pd.DataFrame:
    """Estimate disjoint-occasion reliability under three context licenses."""
    cell = (
        scored.groupby(
            [
                "collector_regime",
                "week_start",
                "user_id",
                "measurement_rind_id",
                "collector_context_id",
            ],
            as_index=False,
        )
        .agg(**{column: (column, "mean") for column in SCORE_COLUMNS}, n_slices=("slice_index", "size"))
    )
    rows: list[dict[str, Any]] = []
    for regime, group in cell.groupby("collector_regime"):
        weeks = sorted(group["week_start"].unique())
        if len(weeks) < 6:
            continue
        half = max(2, (len(weeks) - 1) // 2)
        early_weeks = set(weeks[:half])
        late_weeks = set(weeks[-half:])
        for column in SCORE_COLUMNS:
            early = group.loc[group["week_start"].isin(early_weeks)]
            late = group.loc[group["week_start"].isin(late_weeks)]

            early_mixed = early.groupby("user_id")[column].mean().rename("early")
            late_mixed = late.groupby("user_id")[column].mean().rename("late")
            mixed = pd.concat([early_mixed, late_mixed], axis=1).dropna()

            matched_frames: list[tuple[str, pd.DataFrame]] = [("mixed_rind", mixed)]
            for design, rind_column in (
                ("matched_symbol_rind", "measurement_rind_id"),
                ("matched_collector_context", "collector_context_id"),
            ):
                early_rind = early.groupby(["user_id", rind_column])[column].mean().rename("early")
                late_rind = late.groupby(["user_id", rind_column])[column].mean().rename("late")
                matched = pd.concat([early_rind, late_rind], axis=1).dropna().reset_index()
                matched_user = (
                    matched.groupby("user_id")
                    .agg(
                        early=("early", "mean"),
                        late=("late", "mean"),
                        common_rinds=(rind_column, "nunique"),
                    )
                    .query("common_rinds >= @config.min_common_rinds")
                )
                matched_frames.append((design, matched_user))

            for design, frame in matched_frames:
                r, n = safe_corr(frame.get("early", []), frame.get("late", []))
                sb = 2 * r / (1 + r) if np.isfinite(r) and r > -1 else float("nan")
                lo, hi = fisher_ci(r, n)
                p = permutation_p_correlation(
                    frame.get("early", pd.Series(dtype=float)).to_numpy(float),
                    frame.get("late", pd.Series(dtype=float)).to_numpy(float),
                    trials=config.permutation_trials,
                    seed=config.random_seed + len(rows),
                )
                rows.append(
                    {
                        "collector_regime": regime,
                        "design": design,
                        "construct": column,
                        "early_weeks": ",".join(sorted(early_weeks)),
                        "late_weeks": ",".join(sorted(late_weeks)),
                        "n_authors": n,
                        "pearson_r": r,
                        "pearson_ci_low": lo,
                        "pearson_ci_high": hi,
                        "spearman_brown": sb,
                        "permutation_p": p,
                        "measurement_gate": bool(
                            n >= config.min_reliability_authors and np.isfinite(sb) and sb >= 0.60
                        ),
                    }
                )
    return pd.DataFrame(rows)


def build_weekly_features(scored: pd.DataFrame, config: AuditConfig) -> pd.DataFrame:
    """Build C2 level/composition and C3 within-author state by symbol-week."""
    cell = (
        scored.groupby(
            ["collector_regime", "symbol", "week_start", "user_id", "measurement_rind_id"],
            as_index=False,
        )
        .agg(**{column: (column, "mean") for column in STATE_COLUMNS}, n_slices=("slice_index", "size"))
        .sort_values(["user_id", "measurement_rind_id", "week_start"])
    )
    group_keys = ["user_id", "measurement_rind_id"]
    cell["prior_occasion_count"] = cell.groupby(group_keys).cumcount()
    for column in STATE_COLUMNS:
        cell[f"prior__{column}"] = cell.groupby(group_keys)[column].transform(
            lambda values: values.expanding().mean().shift(1)
        )
        cell[f"state__{column}"] = cell[column] - cell[f"prior__{column}"]
    valid_prior = cell["prior_occasion_count"] >= config.min_prior_occasions
    prior_and_state = [
        column
        for column in cell.columns
        if column.startswith(("prior__", "state__"))
    ]
    cell.loc[~valid_prior, prior_and_state] = np.nan

    author_week = (
        cell.groupby(["collector_regime", "symbol", "week_start", "user_id"], as_index=False)
        .agg(
            **{f"level__{column}": (column, "mean") for column in STATE_COLUMNS},
            **{f"composition__{column}": (f"prior__{column}", "mean") for column in STATE_COLUMNS},
            **{f"state__{column}": (f"state__{column}", "mean") for column in STATE_COLUMNS},
            n_slices=("n_slices", "sum"),
            n_rinds=("measurement_rind_id", "nunique"),
            has_prior=("prior_occasion_count", lambda values: bool((values >= config.min_prior_occasions).any())),
        )
    )
    rows: list[dict[str, Any]] = []
    feature_cols = [column for column in author_week.columns if column.startswith(("level__", "composition__", "state__"))]
    for keys, group in author_week.groupby(["collector_regime", "symbol", "week_start"], sort=True):
        regime, symbol, week = keys
        prior_group = group.loc[group["has_prior"]]
        row: dict[str, Any] = {
            "collector_regime": regime,
            "symbol": symbol,
            "week_start": week,
            "n_authors": int(group["user_id"].nunique()),
            "n_prior_authors": int(prior_group["user_id"].nunique()),
            "n_slices": int(group["n_slices"].sum()),
            "prior_author_coverage": float(len(prior_group) / max(1, len(group))),
        }
        for column in feature_cols:
            source = prior_group if column.startswith(("composition__", "state__")) else group
            row[column] = float(source[column].mean()) if not source.empty else float("nan")
        rows.append(row)
    weekly = pd.DataFrame(rows)
    weekly["level_market_gate"] = weekly["n_authors"] >= config.min_market_authors
    weekly["state_market_gate"] = (
        weekly["level_market_gate"]
        & (weekly["n_prior_authors"] >= config.min_market_authors)
    )
    return weekly


def load_weekly_market(
    path: Path,
    symbols: list[str],
    *,
    parquet_path: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if not symbols:
        return pd.DataFrame(), {"symbols_requested": 0}
    if parquet_path is not None:
        bars = pd.read_parquet(parquet_path)
        bars = bars.loc[bars["symbol"].astype(str).str.upper().isin(symbols)].copy()
    else:
        con = connect_readonly(path)
        try:
            marks = ",".join("?" for _ in symbols)
            sql = f"""
            SELECT symbol, date, datetime, open, high, low, close, volume, provider, updated_at
            FROM price_bars
            WHERE interval = '1d'
              AND symbol IN ({marks})
              AND date >= '2026-03-01'
              AND open IS NOT NULL
              AND close IS NOT NULL
            ORDER BY symbol, date, updated_at
            """
            bars = pd.read_sql_query(sql, con, params=symbols)
        finally:
            con.close()
    if bars.empty:
        return bars, {"symbols_requested": len(symbols), "rows_loaded": 0}
    bars["symbol"] = bars["symbol"].astype(str).str.upper()
    bars["provider_priority"] = bars["provider"].astype(str).str.lower().map(PROVIDER_PRIORITY).fillna(99)
    bars = bars.sort_values(["symbol", "date", "provider_priority", "updated_at"])
    before = len(bars)
    bars = bars.drop_duplicates(["symbol", "date"], keep="first")
    bars["date"] = pd.to_datetime(bars["date"], utc=True, errors="coerce", format="mixed")
    bars = bars.dropna(subset=["date", "open", "close"])
    bars["week_start"] = week_start(bars["date"])
    bars = bars.sort_values(["symbol", "date"])
    bars["daily_return"] = bars.groupby("symbol")["close"].pct_change()
    weekly = (
        bars.groupby(["symbol", "week_start"], as_index=False)
        .agg(
            open_first=("open", "first"),
            close_last=("close", "last"),
            weekly_vol=("daily_return", "std"),
            trading_days=("date", "nunique"),
            provider_count=("provider", "nunique"),
        )
        .sort_values(["symbol", "week_start"])
    )
    weekly["weekly_return"] = weekly.groupby("symbol")["close_last"].pct_change()
    weekly["weekly_abs_return"] = weekly["weekly_return"].abs()
    latest_week = weekly["week_start"].max()
    weekly["complete_week"] = weekly["week_start"] < latest_week
    for target in ("weekly_return", "weekly_abs_return", "weekly_vol"):
        weekly.loc[~weekly["complete_week"], target] = np.nan
    for target in ("weekly_return", "weekly_abs_return", "weekly_vol"):
        weekly[f"prev__{target}"] = weekly.groupby("symbol")[target].shift(1)
        weekly[f"next__{target}"] = weekly.groupby("symbol")[target].shift(-1)
    weekly["next__weekly_abs_return_change"] = (
        weekly["next__weekly_abs_return"] - weekly["weekly_abs_return"]
    )
    weekly["next__weekly_vol_change"] = weekly["next__weekly_vol"] - weekly["weekly_vol"]
    audit = {
        "symbols_requested": len(symbols),
        "symbols_with_bars": int(weekly["symbol"].nunique()),
        "provider_rows_loaded": before,
        "canonical_symbol_date_rows": int(len(bars)),
        "weekly_rows": int(len(weekly)),
        "latest_week_excluded_as_incomplete": latest_week,
    }
    return weekly, audit


def weekly_ic(frame: pd.DataFrame, feature: str, target: str, min_symbols: int) -> pd.DataFrame:
    rows = []
    for week, group in frame.groupby("week_start"):
        sample = group[["symbol", feature, target]].dropna()
        if len(sample) < min_symbols or sample[feature].nunique() < 2 or sample[target].nunique() < 2:
            continue
        rho = float(stats.spearmanr(sample[feature], sample[target]).statistic)
        rows.append({"week_start": week, "n_symbols": len(sample), "rho": rho})
    return pd.DataFrame(rows)


def sign_flip_p(values: np.ndarray, trials: int, seed: int) -> float:
    values = values[np.isfinite(values)]
    if len(values) < 3:
        return float("nan")
    observed = abs(float(np.mean(values)))
    rng = np.random.default_rng(seed)
    exceed = 0
    for _ in range(trials):
        signs = rng.choice([-1.0, 1.0], size=len(values))
        exceed += abs(float(np.mean(values * signs))) >= observed
    return float((exceed + 1) / (trials + 1))


def bh_fdr(p_values: pd.Series) -> pd.Series:
    values = pd.to_numeric(p_values, errors="coerce").to_numpy(float)
    out = np.full(len(values), np.nan)
    valid = np.flatnonzero(np.isfinite(values))
    if not len(valid):
        return pd.Series(out, index=p_values.index)
    order = valid[np.argsort(values[valid])]
    adjusted = values[order] * len(order) / np.arange(1, len(order) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    out[order] = np.minimum(adjusted, 1.0)
    return pd.Series(out, index=p_values.index)


def market_information_tests(panel: pd.DataFrame, config: AuditConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Cross-sectional weekly information tests with week-level inference."""
    eligible = panel.copy()
    features = [
        column
        for column in eligible.columns
        if column.startswith(("level__", "composition__", "state__"))
        and any(axis in column for axis in STATE_COLUMNS)
    ]
    eligible["log_n_authors"] = np.log1p(eligible["n_authors"])
    eligible["log_n_slices"] = np.log1p(eligible["n_slices"])
    features.extend(["log_n_authors", "log_n_slices"])
    for baseline in ("weekly_return", "weekly_abs_return", "weekly_vol"):
        column = f"market_baseline__{baseline}"
        eligible[column] = eligible[baseline]
        features.append(column)
    targets = [
        "prev__weekly_return",
        "prev__weekly_abs_return",
        "prev__weekly_vol",
        "weekly_return",
        "weekly_abs_return",
        "weekly_vol",
        "next__weekly_return",
        "next__weekly_abs_return",
        "next__weekly_vol",
        "next__weekly_abs_return_change",
        "next__weekly_vol_change",
    ]
    rows: list[dict[str, Any]] = []
    ic_rows: list[pd.DataFrame] = []
    for feature in features:
        feature_class = (
            "market_baseline"
            if feature.startswith("market_baseline__")
            else "collection_baseline"
            if feature.startswith("log_n_")
            else "suica"
        )
        gate_column = (
            "state_market_gate"
            if feature.startswith(("composition__", "state__"))
            else "level_market_gate"
        )
        feature_frame = eligible.loc[eligible[gate_column]].copy()
        for target in targets:
            if feature_class == "market_baseline" and not target.startswith("next__"):
                continue
            if target not in feature_frame:
                continue
            ic = weekly_ic(feature_frame, feature, target, config.min_symbols_per_week)
            if ic.empty:
                continue
            ic["feature"] = feature
            ic["target"] = target
            ic_rows.append(ic)
            mean_ic = float(ic["rho"].mean())
            rows.append(
                {
                    "feature": feature,
                    "feature_class": feature_class,
                    "target": target,
                    "lag_class": (
                        "past_placebo"
                        if target.startswith("prev__")
                        else "future"
                        if target.startswith("next__")
                        else "contemporaneous"
                    ),
                    "n_independent_weeks": int(len(ic)),
                    "median_symbols_per_week": float(ic["n_symbols"].median()),
                    "mean_weekly_spearman_ic": mean_ic,
                    "median_weekly_spearman_ic": float(ic["rho"].median()),
                    "positive_week_share": float((ic["rho"] > 0).mean()),
                    "week_sign_flip_p": sign_flip_p(
                        ic["rho"].to_numpy(float),
                        config.permutation_trials,
                        config.random_seed + len(rows),
                    ),
                }
            )
    results = pd.DataFrame(rows)
    if not results.empty:
        results["bh_q_within_audit"] = bh_fdr(results["week_sign_flip_p"])
        results["bh_q_within_feature_family"] = results.groupby("feature_class", group_keys=False)[
            "week_sign_flip_p"
        ].transform(bh_fdr)
        results["exploratory_signal"] = (
            results["feature_class"].eq("suica")
            &
            (results["n_independent_weeks"] >= 6)
            & (results["mean_weekly_spearman_ic"].abs() >= 0.10)
            & (results["bh_q_within_feature_family"] < 0.10)
        )
    ic_detail = pd.concat(ic_rows, ignore_index=True) if ic_rows else pd.DataFrame()
    return results, ic_detail


def market_regime_robustness(ic_detail: pd.DataFrame, weekly: pd.DataFrame) -> pd.DataFrame:
    """Summarize weekly IC direction by collection regime without pooling rows."""
    if ic_detail.empty:
        return pd.DataFrame()
    week_regime = (
        weekly.groupby("week_start")["collector_regime"]
        .agg(lambda values: ",".join(sorted(set(map(str, values)))))
        .rename("collector_regime")
    )
    merged = ic_detail.merge(week_regime, left_on="week_start", right_index=True, how="left")
    return (
        merged.groupby(["feature", "target", "collector_regime"], as_index=False)
        .agg(
            n_independent_weeks=("week_start", "nunique"),
            mean_weekly_spearman_ic=("rho", "mean"),
            median_weekly_spearman_ic=("rho", "median"),
            positive_week_share=("rho", lambda values: float((values > 0).mean())),
            median_symbols_per_week=("n_symbols", "median"),
        )
    )


def report_lines(
    config: AuditConfig,
    audits: dict[str, Any],
    reliability: pd.DataFrame,
    market_tests: pd.DataFrame,
) -> list[str]:
    passed = reliability.loc[reliability.get("measurement_gate", False)] if not reliability.empty else pd.DataFrame()
    signals = market_tests.loc[market_tests.get("exploratory_signal", False)] if not market_tests.empty else pd.DataFrame()
    future = (
        market_tests.loc[
            market_tests.get("lag_class", "").eq("future")
            & market_tests.get("feature_class", "").eq("suica")
        ]
        if not market_tests.empty
        else pd.DataFrame()
    )
    baseline_future = (
        market_tests.loc[
            market_tests.get("lag_class", "").eq("future")
            & market_tests.get("feature_class", "").ne("suica")
        ]
        if not market_tests.empty
        else pd.DataFrame()
    )
    best_future = future.reindex(future["mean_weekly_spearman_ic"].abs().sort_values(ascending=False).index).head(10)
    lines = [
        "# SUICA Market Measurement-First Audit v1",
        "",
        "Research-only, read-only database analysis. No runtime prediction or broker state was written.",
        "",
        "## Design",
        "",
        "- Scorer: frozen SUICA v4 English anchor dictionary and equations.",
        "- Slice boundary: author x symbol/query-group collector-context x ISO week; no slice crosses those boundaries.",
        "- Primary measurement rind: symbol. Exact query-group context is retained as a stricter sensitivity design, not treated as psychological ground truth.",
        "- C1 choice: not estimated because archive symbol/query assignment is collector-mediated.",
        "- C2 evidence: disjoint-week matched-rind and mixed-rind author reliability.",
        "- C3 evidence: current author/rind score minus strictly-prior author/rind mean.",
        "- Market information: cross-sectional weekly Spearman IC; inference uses independent weeks, not author-week rows.",
        "",
        "## Data funnel",
        "",
        f"- eligible posts after language/rind/dedup filters: {audits['posts']['eligible_rows_after_dedup']:,}",
        f"- authors: {audits['posts']['distinct_authors']:,}",
        f"- slices: {audits['slices']['slice_count']:,}",
        f"- authors with slices: {audits['slices']['authors_with_slices']:,}",
        f"- symbols with slices: {audits['slices']['symbols_with_slices']:,}",
        f"- collector query-group strings: {audits['posts']['distinct_query_groups']:,} ({audits['posts']['singleton_query_groups']:,} singleton groups)",
        "",
        "## Measurement gate",
        "",
        f"- passing construct x regime x design cells: {len(passed)} / {len(reliability)}",
    ]
    if not passed.empty:
        for row in passed.sort_values("spearman_brown", ascending=False).head(12).itertuples(index=False):
            lines.append(
                f"- PASS {row.collector_regime}/{row.design}/{row.construct}: "
                f"SB={row.spearman_brown:.3f}, r={row.pearson_r:.3f}, n={row.n_authors}"
            )
    else:
        lines.append("- No cell passed the pre-specified audit gate (SB >= .60, n >= floor).")
    lines.extend(["", "## Market information gate", "", f"- exploratory signals after within-audit BH: {len(signals)}"])
    if not signals.empty:
        for row in signals.sort_values("bh_q_within_feature_family").head(12).itertuples(index=False):
            lines.append(
                f"- CANDIDATE {row.lag_class}: {row.feature} -> {row.target}: "
                f"mean weekly IC={row.mean_weekly_spearman_ic:.3f}, weeks={row.n_independent_weeks}, q-family={row.bh_q_within_feature_family:.3g}"
            )
    else:
        lines.append("- No market-information test cleared the exploratory gate.")
    lines.extend(["", "## Strongest forward associations (descriptive, not promoted)", ""])
    for row in best_future.itertuples(index=False):
        lines.append(
            f"- {row.feature} -> {row.target}: mean IC={row.mean_weekly_spearman_ic:.3f}, "
            f"weeks={row.n_independent_weeks}, p={row.week_sign_flip_p:.3g}, q-family={row.bh_q_within_feature_family:.3g}"
        )
    lines.extend(["", "## Market/collection control baselines", ""])
    for row in baseline_future.reindex(
        baseline_future["mean_weekly_spearman_ic"].abs().sort_values(ascending=False).index
    ).head(8).itertuples(index=False):
        lines.append(
            f"- CONTROL {row.feature} -> {row.target}: mean IC={row.mean_weekly_spearman_ic:.3f}, "
            f"weeks={row.n_independent_weeks}, p={row.week_sign_flip_p:.3g}"
        )
    lines.extend(
        [
            "",
            "## Interpretation limits",
            "",
            "- Collection policy changes at 2026-05-18 and 2026-06-22; regimes are reported separately for measurement.",
            "- The archive spans roughly four months, so forward market inference remains week-limited.",
            "- English-only v1 avoids pretending that the unvalidated multilingual market port inherits SUICA v4 meaning.",
            "- A contemporaneous association is market-state sensitivity, not forecasting.",
            "- A future association must also exceed past-placebo, collection-volume, and market-persistence baselines before model training is justified.",
        ]
    )
    return lines


def write_handoff(path: Path, output_dir: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "# Trading-agent handoff: SUICA measurement-first audit",
                "",
                "Do not merge this analysis into NS-2 or runtime prediction code.",
                "",
                "## Required review order",
                "",
                "1. Inspect `data_quality.json` and confirm collection-phase boundaries.",
                "2. Inspect `measurement_reliability.csv`; only passed cells may be interpreted as stable measurements.",
                "3. Inspect `market_information_tests.csv`; distinguish past-placebo, contemporaneous, and future targets.",
                "4. Treat `weekly_features.csv` as aggregate research data only; no account IDs or raw text are exported.",
                "5. Do not train or tune a predictor unless a future association survives BH, volume baselines, and independent-week inference.",
                "",
                "## Re-run architecture",
                "",
                "1. On Windows, run the read-only snapshot exporter from `trading-agent-codex`.",
                "2. Run this audit from the independent SUICA repository so the current frozen scorer, not the stale trading vendor copy, is imported.",
                "",
                "```powershell",
                "python scripts\\export_suica_measurement_first_snapshot.py",
                "```",
                "",
                "```bash",
                "python scripts/run_suica_market_measurement_first_audit_v1.py \\",
                "  --posts-parquet /path/to/suica_measurement_first_input_v1/x_posts_en.parquet \\",
                "  --market-parquet /path/to/suica_measurement_first_input_v1/price_bars_daily.parquet \\",
                f"  --output-dir {output_dir}",
                "```",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intelligence-db", type=Path, default=DEFAULT_INTELLIGENCE_DB)
    parser.add_argument("--market-db", type=Path, default=DEFAULT_MARKET_DB)
    parser.add_argument("--posts-parquet", type=Path, default=None)
    parser.add_argument("--market-parquet", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--language", default="en")
    parser.add_argument("--permutation-trials", type=int, default=2000)
    parser.add_argument("--smoke", action="store_true", help="Use the first 20k eligible posts and 200 permutations.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = AuditConfig(
        language=args.language,
        permutation_trials=200 if args.smoke else args.permutation_trials,
    )
    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    posts, posts_audit = load_posts(
        args.intelligence_db,
        config.language,
        parquet_path=args.posts_parquet,
    )
    if args.smoke:
        posts = posts.head(20_000).copy()
        posts_audit["smoke_rows_used"] = int(len(posts))
    slices, slice_audit = build_slices(posts, config)
    scored, scorer_audit = score_slices(slices)
    reliability = reliability_rows(scored, config)
    weekly = build_weekly_features(scored, config)
    market, market_audit = load_weekly_market(
        args.market_db,
        sorted(weekly["symbol"].unique().tolist()),
        parquet_path=args.market_parquet,
    )
    panel = weekly.merge(market, on=["symbol", "week_start"], how="inner")
    market_tests, ic_detail = market_information_tests(panel, config)
    regime_robustness = market_regime_robustness(ic_detail, weekly)

    audits = {
        "config": asdict(config),
        "posts": posts_audit,
        "slices": slice_audit,
        "scorer": scorer_audit,
        "market": market_audit,
        "joined_panel_rows": int(len(panel)),
        "joined_panel_symbols": int(panel["symbol"].nunique()) if not panel.empty else 0,
        "joined_panel_weeks": int(panel["week_start"].nunique()) if not panel.empty else 0,
    }
    (output_dir / "data_quality.json").write_text(json.dumps(audits, indent=2) + "\n", encoding="utf-8")
    reliability.to_csv(output_dir / "measurement_reliability.csv", index=False)
    weekly.drop(columns=[column for column in weekly if column.startswith("user_id")], errors="ignore").to_csv(
        output_dir / "weekly_features.csv", index=False
    )
    market_tests.to_csv(output_dir / "market_information_tests.csv", index=False)
    ic_detail.to_csv(output_dir / "weekly_ic_detail.csv", index=False)
    regime_robustness.to_csv(output_dir / "market_regime_robustness.csv", index=False)
    (output_dir / "REPORT.md").write_text(
        "\n".join(report_lines(config, audits, reliability, market_tests)) + "\n",
        encoding="utf-8",
    )
    write_handoff(output_dir / "HANDOFF_FOR_TRADING_AGENT.md", output_dir)
    print(json.dumps({"output_dir": str(output_dir), **audits}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
