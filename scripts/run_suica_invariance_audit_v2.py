#!/usr/bin/env python
"""Audit where SUICA-base invariance comes from.

This is a detail-oriented follow-up to portability v1. It keeps a frozen
PANDORA-fitted SUICA-base scorer, then varies split definitions and nuisance
controls to locate whether stability comes from author-level behavior,
topic/query/symbol context, duplicated text, or task artifacts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_portability_validation import (  # noqa: E402
    BIG5_TRAITS,
    external_big5,
    factor_cols,
    fit_frozen_scorer,
    load_source_slices,
    random_control,
    score_by_split,
    slices_from_text,
    split_reliability,
)


URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
SPACE_RE = re.compile(r"\s+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SUICA invariance audit v2.")
    parser.add_argument("--source-slices", default="results/suica_strategy_search_v3_svd32_method_stripped/fixed_128__gmm_soft__method_stripped/slices.csv")
    parser.add_argument("--big5-prepared", default="data_sets/prepared/pandora_official/pandora_official_big5_prepared.csv")
    parser.add_argument("--pandora-comments", default="data_sets/PANDORA_official/all_comments_since_2015.csv")
    parser.add_argument("--essays-prepared", default="data_sets/prepared/big5/essays_original_prepared.csv")
    parser.add_argument("--x-posts", default="data_sets/x_fullmarkettext/memory_semis_3m_20260318_20260617_merged/x_posts.csv")
    parser.add_argument("--output-dir", default="results/suica_invariance_audit_v2")
    parser.add_argument("--report-path", default="reports/suica_invariance_audit_v2.md")
    parser.add_argument("--slice-tokens", type=int, default=128)
    parser.add_argument("--min-slice-tokens", type=int, default=24)
    parser.add_argument("--max-slices-per-user-split", type=int, default=18)
    parser.add_argument("--tfidf-max-features", type=int, default=22000)
    parser.add_argument("--tfidf-min-df", type=int, default=3)
    parser.add_argument("--svd-dims", type=int, default=32)
    parser.add_argument("--gmm-k", type=int, default=18)
    parser.add_argument("--factor-count", type=int, default=10)
    parser.add_argument("--factor-min-reliability", type=float, default=0.10)
    parser.add_argument("--factor-min-features", type=int, default=12)
    parser.add_argument("--random-seed", type=int, default=42)
    parser.add_argument("--permutation-count", type=int, default=200)
    parser.add_argument("--max-pandora-users", type=int, default=500)
    parser.add_argument("--max-pandora-comments-per-user", type=int, default=120)
    parser.add_argument("--min-pandora-comments-per-split", type=int, default=4)
    parser.add_argument("--max-essays-users", type=int, default=1200)
    parser.add_argument("--max-x-users", type=int, default=500)
    parser.add_argument("--min-x-posts-per-user", type=int, default=4)
    parser.add_argument("--min-x-posts-per-split", type=int, default=2)
    parser.add_argument("--x-lang", default="en")
    return parser.parse_args()


def normalize_text(text: str) -> str:
    text = URL_RE.sub(" ", str(text or "").lower())
    text = re.sub(r"[@#$]\w+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return SPACE_RE.sub(" ", text).strip()


def entropy(values: pd.Series) -> float:
    counts = values.fillna("__missing__").astype(str).value_counts()
    probs = counts / max(1, counts.sum())
    return float(-(probs * np.log2(probs + 1e-12)).sum())


def dataset_audit(name: str, frame: pd.DataFrame, *, user_col: str, text_col: str, context_cols: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "dataset": name,
        "rows": int(len(frame)),
        "users": int(frame[user_col].astype(str).nunique()) if user_col in frame.columns else 0,
    }
    if text_col in frame.columns and len(frame):
        text = frame[text_col].fillna("").astype(str)
        norm = text.map(normalize_text)
        out["exact_duplicate_rate"] = float(1.0 - text.nunique() / max(1, len(text)))
        out["normalized_duplicate_rate"] = float(1.0 - norm.nunique() / max(1, len(norm)))
        out["median_text_chars"] = float(text.str.len().median())
        out["short_text_rate_lt_40"] = float(text.str.len().lt(40).mean())
    if user_col in frame.columns and len(frame):
        counts = frame[user_col].astype(str).value_counts()
        out["median_rows_per_user"] = float(counts.median())
        out["p90_rows_per_user"] = float(counts.quantile(0.90))
    for col in context_cols:
        if col in frame.columns:
            out[f"{col}_nunique"] = int(frame[col].fillna("__missing__").astype(str).nunique())
            out[f"{col}_entropy"] = entropy(frame[col])
            out[f"{col}_top"] = str(frame[col].fillna("__missing__").astype(str).value_counts().index[0]) if len(frame) else ""
    return out


def make_slices_for_parts(user_id: str, parts: list[tuple[str, pd.DataFrame, str]], args: argparse.Namespace) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split, part, text_col in parts:
        text = "\n".join(part[text_col].fillna("").astype(str).tolist())
        rows.extend(slices_from_text(str(user_id), text, split_prefix=split, args=args))
    return rows


def load_x_posts(args: argparse.Namespace, *, dedup: str = "none") -> pd.DataFrame:
    posts = pd.read_csv(args.x_posts)
    posts = posts.loc[:, [col for col in ["post_id", "account_id", "timestamp", "symbol", "text", "lang", "query_group"] if col in posts.columns]].copy()
    if args.x_lang and "lang" in posts.columns:
        posts = posts.loc[posts["lang"].astype(str).eq(args.x_lang)].copy()
    posts["user_id"] = posts["account_id"].astype(str)
    posts["timestamp"] = pd.to_datetime(posts["timestamp"], errors="coerce", utc=True)
    posts["text"] = posts["text"].fillna("").astype(str)
    posts = posts.loc[posts["timestamp"].notna() & posts["text"].str.len().gt(0)].copy()
    posts["normalized_text"] = posts["text"].map(normalize_text)
    if dedup == "global":
        posts = posts.drop_duplicates("normalized_text")
    elif dedup == "per_user":
        posts = posts.drop_duplicates(["user_id", "normalized_text"])
    counts = posts.groupby("user_id").size().sort_values(ascending=False)
    users = counts.loc[counts >= args.min_x_posts_per_user].index.tolist()
    if args.max_x_users:
        users = users[: args.max_x_users]
    return posts.loc[posts["user_id"].isin(users)].sort_values(["user_id", "timestamp"]).reset_index(drop=True)


def x_temporal_slices(posts: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for user_id, group in posts.groupby("user_id", sort=True):
        group = group.sort_values("timestamp")
        midpoint = max(1, len(group) // 2)
        if len(group.iloc[:midpoint]) < args.min_x_posts_per_split or len(group.iloc[midpoint:]) < args.min_x_posts_per_split:
            continue
        rows.extend(make_slices_for_parts(user_id, [("early_time", group.iloc[:midpoint], "text"), ("late_time", group.iloc[midpoint:], "text")], args))
    return pd.DataFrame(rows)


def x_context_slices(posts: pd.DataFrame, args: argparse.Namespace, *, context_col: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if context_col not in posts.columns:
        return pd.DataFrame()
    work = posts.copy()
    work[context_col] = work[context_col].fillna("__missing__").astype(str)
    for user_id, group in work.groupby("user_id", sort=True):
        counts = group[context_col].value_counts()
        if len(counts) < 2:
            continue
        top = counts.index[0]
        a = group.loc[group[context_col].eq(top)]
        b = group.loc[~group[context_col].eq(top)]
        if len(a) < args.min_x_posts_per_split or len(b) < args.min_x_posts_per_split:
            continue
        rows.extend(make_slices_for_parts(user_id, [(f"top_{context_col}", a, "text"), (f"other_{context_col}", b, "text")], args))
    return pd.DataFrame(rows)


def x_within_context_temporal_slices(posts: pd.DataFrame, args: argparse.Namespace, *, context_col: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if context_col not in posts.columns:
        return pd.DataFrame()
    work = posts.copy()
    work[context_col] = work[context_col].fillna("__missing__").astype(str)
    for user_id, group in work.groupby("user_id", sort=True):
        top = group[context_col].value_counts().index[0]
        sub = group.loc[group[context_col].eq(top)].sort_values("timestamp")
        if len(sub) < args.min_x_posts_per_user:
            continue
        midpoint = max(1, len(sub) // 2)
        a = sub.iloc[:midpoint]
        b = sub.iloc[midpoint:]
        if len(a) < args.min_x_posts_per_split or len(b) < args.min_x_posts_per_split:
            continue
        rows.extend(make_slices_for_parts(user_id, [(f"early_top_{context_col}", a, "text"), (f"late_top_{context_col}", b, "text")], args))
    return pd.DataFrame(rows)


def load_pandora_comments(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    labels = pd.read_csv(args.big5_prepared)
    labels["user_id"] = labels["user_id"].astype(str)
    target_users = set(labels.sort_values("user_id").head(args.max_pandora_users)["user_id"].tolist())
    chunks: list[pd.DataFrame] = []
    usecols = ["author", "body", "created_utc", "lang", "subreddit"]
    for chunk in pd.read_csv(args.pandora_comments, usecols=usecols, chunksize=200000):
        chunk = chunk.loc[chunk["author"].astype(str).isin(target_users)].copy()
        if chunk.empty:
            continue
        chunk = chunk.loc[chunk["lang"].fillna("en").astype(str).eq("en")]
        chunk["body"] = chunk["body"].fillna("").astype(str)
        chunk = chunk.loc[chunk["body"].str.len().gt(0)]
        chunks.append(chunk)
    if not chunks:
        return pd.DataFrame(), labels[["user_id", *BIG5_TRAITS]]
    comments = pd.concat(chunks, ignore_index=True)
    comments["user_id"] = comments["author"].astype(str)
    comments["created_utc"] = pd.to_numeric(comments["created_utc"], errors="coerce")
    comments = comments.loc[comments["created_utc"].notna()].sort_values(["user_id", "created_utc"])
    comments = comments.groupby("user_id", group_keys=False).head(args.max_pandora_comments_per_user).reset_index(drop=True)
    return comments, labels[["user_id", *BIG5_TRAITS]]


def pandora_temporal_slices(comments: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for user_id, group in comments.groupby("user_id", sort=True):
        group = group.sort_values("created_utc")
        midpoint = max(1, len(group) // 2)
        a = group.iloc[:midpoint]
        b = group.iloc[midpoint:]
        if len(a) < args.min_pandora_comments_per_split or len(b) < args.min_pandora_comments_per_split:
            continue
        rows.extend(make_slices_for_parts(user_id, [("early_time", a, "body"), ("late_time", b, "body")], args))
    return pd.DataFrame(rows)


def pandora_subreddit_slices(comments: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for user_id, group in comments.groupby("user_id", sort=True):
        counts = group["subreddit"].fillna("__missing__").astype(str).value_counts()
        if len(counts) < 2:
            continue
        top = counts.index[0]
        a = group.loc[group["subreddit"].fillna("__missing__").astype(str).eq(top)]
        b = group.loc[~group["subreddit"].fillna("__missing__").astype(str).eq(top)]
        if len(a) < args.min_pandora_comments_per_split or len(b) < args.min_pandora_comments_per_split:
            continue
        rows.extend(make_slices_for_parts(user_id, [("top_subreddit", a, "body"), ("other_subreddit", b, "body")], args))
    return pd.DataFrame(rows)


def pandora_within_subreddit_temporal_slices(comments: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for user_id, group in comments.groupby("user_id", sort=True):
        top = group["subreddit"].fillna("__missing__").astype(str).value_counts().index[0]
        sub = group.loc[group["subreddit"].fillna("__missing__").astype(str).eq(top)].sort_values("created_utc")
        if len(sub) < args.min_pandora_comments_per_split * 2:
            continue
        midpoint = max(1, len(sub) // 2)
        rows.extend(make_slices_for_parts(user_id, [("early_top_subreddit", sub.iloc[:midpoint], "body"), ("late_top_subreddit", sub.iloc[midpoint:], "body")], args))
    return pd.DataFrame(rows)


def essays_slices(args: argparse.Namespace, *, mode: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    data = pd.read_csv(args.essays_prepared)
    data["user_id"] = data["user_id"].astype(str)
    if args.max_essays_users:
        data = data.sort_values("user_id").head(args.max_essays_users)
    rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(args.random_seed)
    for row in data.itertuples(index=False):
        all_slices = slices_from_text(str(row.user_id), str(row.text), split_prefix="tmp", args=args)
        if len(all_slices) < 2:
            continue
        if mode == "contiguous":
            midpoint = max(1, len(all_slices) // 2)
            groups = [("first_half", all_slices[:midpoint]), ("second_half", all_slices[midpoint:])]
        elif mode == "interleaved":
            groups = [("even_slice", all_slices[::2]), ("odd_slice", all_slices[1::2])]
        else:
            order = rng.permutation(len(all_slices))
            left = set(order[: len(order) // 2].tolist())
            groups = [
                ("random_a", [item for idx, item in enumerate(all_slices) if idx in left]),
                ("random_b", [item for idx, item in enumerate(all_slices) if idx not in left]),
            ]
        for split, items in groups:
            for item in items:
                item = dict(item)
                item["score_split"] = split
                rows.append(item)
    labels = data[["user_id", *[trait for trait in BIG5_TRAITS if trait in data.columns]]].copy()
    return pd.DataFrame(rows), labels


def split_balance(slices: pd.DataFrame) -> dict[str, Any]:
    if slices.empty or "score_split" not in slices:
        return {}
    counts = slices.groupby("score_split").size()
    users = slices.groupby("score_split")["user_id"].nunique()
    return {
        "split_slice_counts": json.dumps(counts.to_dict(), ensure_ascii=False),
        "split_user_counts": json.dumps(users.to_dict(), ensure_ascii=False),
        "min_split_users": int(users.min()) if len(users) else 0,
        "max_split_users": int(users.max()) if len(users) else 0,
    }


def evaluate_scenario(name: str, slices: pd.DataFrame, labels: pd.DataFrame, scorer: Any, args: argparse.Namespace, out_dir: Path) -> dict[str, Any]:
    prefix = out_dir / name
    if slices.empty:
        return {"scenario": name, "slice_count": 0, "scored_users": 0, "status": "skipped_empty"}
    slices = slices.copy().reset_index(drop=True)
    slices["global_slice_id"] = np.arange(len(slices))
    scores = score_by_split(name, slices, scorer)
    factor_rel, profile_rel, wide = split_reliability(scores)
    factors = factor_cols(scores)
    control = random_control(wide, factors, seed=args.random_seed, permutation_count=args.permutation_count) if factors else pd.DataFrame()
    big5 = external_big5(scores, labels)
    slices.to_csv(f"{prefix}_slices.csv", index=False)
    scores.to_csv(f"{prefix}_split_scores.csv", index=False)
    factor_rel.to_csv(f"{prefix}_factor_reliability.csv", index=False)
    profile_rel.to_csv(f"{prefix}_profile_reliability.csv", index=False)
    control.to_csv(f"{prefix}_random_control.csv", index=False)
    big5.to_csv(f"{prefix}_big5_external_validity.csv", index=False)
    row = {
        "scenario": name,
        "status": "ok",
        "slice_count": int(len(slices)),
        "scored_users": int(scores["user_id"].nunique()) if not scores.empty else 0,
        "mean_factor_split_half_r": float(pd.to_numeric(factor_rel.get("split_half_r", pd.Series(dtype=float)), errors="coerce").mean()) if not factor_rel.empty else np.nan,
        "median_factor_split_half_r": float(pd.to_numeric(factor_rel.get("split_half_r", pd.Series(dtype=float)), errors="coerce").median()) if not factor_rel.empty else np.nan,
        "median_profile_cosine": float(profile_rel["profile_cosine"].median()) if not profile_rel.empty else np.nan,
        "q10_profile_cosine": float(profile_rel["profile_cosine"].quantile(0.10)) if not profile_rel.empty else np.nan,
        "q90_profile_cosine": float(profile_rel["profile_cosine"].quantile(0.90)) if not profile_rel.empty else np.nan,
        "random_p": float(control["p_perm_median_ge_actual"].iloc[0]) if not control.empty else np.nan,
        "top_big5_abs_r": float(pd.to_numeric(big5.get("abs_pearson_r", pd.Series(dtype=float)), errors="coerce").max()) if not big5.empty else np.nan,
    }
    row.update(split_balance(slices))
    return row


def write_report(path: Path, *, out_dir: Path, data_audit: pd.DataFrame, summary: pd.DataFrame) -> None:
    lines = [
        "# SUICA Invariance Audit v2",
        "",
        "## Purpose",
        "",
        "This audit searches for the source of SUICA-base stability. It keeps the same frozen scorer and changes only the text split/control condition.",
        "",
        "## Data Detail Audit",
        "",
        data_audit.to_markdown(index=False),
        "",
        "## Scenario Results",
        "",
        summary.sort_values("median_profile_cosine", ascending=False).to_markdown(index=False),
        "",
        "## Breakthrough-Oriented Interpretation",
        "",
    ]
    ok = summary.loc[summary["status"].eq("ok")].copy()
    if not ok.empty:
        x_rows = ok.loc[ok["scenario"].str.startswith("x_")]
        if not x_rows.empty:
            lines.append("- X stability should not be accepted at face value until duplicate/topic controls are compared. Very high profile cosine with high query/symbol concentration indicates domain-routine signal may be inflating author stability.")
        pandora_cross = ok.loc[ok["scenario"].eq("pandora_cross_subreddit")]
        if not pandora_cross.empty:
            val = pandora_cross["median_profile_cosine"].iloc[0]
            lines.append(f"- PANDORA cross-subreddit median profile cosine is {val:.3f}; this is the key test of whether SUICA measures response style beyond topic choice.")
        essays_contig = ok.loc[ok["scenario"].eq("essays_contiguous")]
        essays_inter = ok.loc[ok["scenario"].eq("essays_interleaved")]
        if not essays_contig.empty and not essays_inter.empty:
            lines.append(
                f"- Essays contiguous vs interleaved profile cosine: {essays_contig['median_profile_cosine'].iloc[0]:.3f} vs {essays_inter['median_profile_cosine'].iloc[0]:.3f}. A large gap means local narrative continuity is part of the measured signal."
            )
    lines.extend(
        [
            "",
            "## SUICA-base vs Domain Adapter Rule",
            "",
            "- Base factors should pass temporal, cross-context, and duplicate-controlled stability without refitting.",
            "- Domain adapters may improve a platform/task only after the base result survives these controls.",
            "- If a factor is stable only inside one query/topic/symbol condition, it belongs to the domain adapter layer, not the universal SUICA-base.",
            "",
            "## Artifacts",
            "",
            f"- Results directory: `{out_dir}`",
            "- `data_detail_audit.csv`",
            "- `scenario_summary.csv`",
            "- per-scenario slices/scores/reliability/random-control/external-validity files",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    source_slices = load_source_slices(Path(args.source_slices))
    scorer, source_scores, source_reliability = fit_frozen_scorer(source_slices, args)
    source_scores.to_csv(out_dir / "source_model_factor_scores.csv", index=False)
    source_reliability.to_csv(out_dir / "source_model_node_reliability.csv", index=False)

    data_audits: list[dict[str, Any]] = []
    scenario_rows: list[dict[str, Any]] = []

    x_raw = load_x_posts(args, dedup="none")
    x_user_dedup = load_x_posts(args, dedup="per_user")
    x_global_dedup = load_x_posts(args, dedup="global")
    data_audits.extend(
        [
            dataset_audit("x_raw_en", x_raw, user_col="user_id", text_col="text", context_cols=["query_group", "symbol"]),
            dataset_audit("x_per_user_dedup_en", x_user_dedup, user_col="user_id", text_col="text", context_cols=["query_group", "symbol"]),
            dataset_audit("x_global_dedup_en", x_global_dedup, user_col="user_id", text_col="text", context_cols=["query_group", "symbol"]),
        ]
    )
    empty_labels = pd.DataFrame(columns=["user_id"])
    x_scenarios = {
        "x_temporal_raw": x_temporal_slices(x_raw, args),
        "x_temporal_user_dedup": x_temporal_slices(x_user_dedup, args),
        "x_temporal_global_dedup": x_temporal_slices(x_global_dedup, args),
        "x_cross_query_group": x_context_slices(x_raw, args, context_col="query_group"),
        "x_within_top_query_group_temporal": x_within_context_temporal_slices(x_raw, args, context_col="query_group"),
        "x_cross_symbol": x_context_slices(x_raw, args, context_col="symbol"),
        "x_within_top_symbol_temporal": x_within_context_temporal_slices(x_raw, args, context_col="symbol"),
    }
    for name, slices in x_scenarios.items():
        scenario_rows.append(evaluate_scenario(name, slices, empty_labels, scorer, args, out_dir))

    pandora_comments, pandora_labels = load_pandora_comments(args)
    data_audits.append(dataset_audit("pandora_raw_comments_sample", pandora_comments, user_col="user_id", text_col="body", context_cols=["subreddit"]))
    pandora_scenarios = {
        "pandora_temporal": pandora_temporal_slices(pandora_comments, args),
        "pandora_cross_subreddit": pandora_subreddit_slices(pandora_comments, args),
        "pandora_within_top_subreddit_temporal": pandora_within_subreddit_temporal_slices(pandora_comments, args),
    }
    for name, slices in pandora_scenarios.items():
        scenario_rows.append(evaluate_scenario(name, slices, pandora_labels, scorer, args, out_dir))

    essay_frame = pd.read_csv(args.essays_prepared)
    if args.max_essays_users:
        essay_frame = essay_frame.sort_values("user_id").head(args.max_essays_users)
    data_audits.append(dataset_audit("essays_prepared_sample", essay_frame, user_col="user_id", text_col="text", context_cols=["essay_fold"]))
    for mode in ["contiguous", "interleaved", "random"]:
        slices, labels = essays_slices(args, mode=mode)
        scenario_rows.append(evaluate_scenario(f"essays_{mode}", slices, labels, scorer, args, out_dir))

    data_audit = pd.DataFrame(data_audits)
    summary = pd.DataFrame(scenario_rows)
    data_audit.to_csv(out_dir / "data_detail_audit.csv", index=False)
    summary.to_csv(out_dir / "scenario_summary.csv", index=False)
    (out_dir / "run_config.json").write_text(json.dumps(vars(args), ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(Path(args.report_path), out_dir=out_dir, data_audit=data_audit, summary=summary)
    print(summary.sort_values("median_profile_cosine", ascending=False).to_string(index=False))
    print(f"\nReport: {args.report_path}")


if __name__ == "__main__":
    main()
