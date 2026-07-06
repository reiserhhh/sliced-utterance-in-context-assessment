#!/usr/bin/env python
"""Fit a frozen SUICA scorer and test cross-corpus measurement portability.

The scorer is fit once on PANDORA SUICA training slices, then applied without
refitting to PANDORA temporal halves, Essays split halves, and X market text.
This is a same-scale measurement invariance test, not a Big5/MBTI prediction
benchmark.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from joblib import dump
from scipy import stats
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.suica import (  # noqa: E402
    BIG5_TRAITS,
    SuicaFactorConfig,
    controlled_slice_text,
    fixed_token_slices_for_text,
    split_half_reliability,
    top_terms_for_soft_nodes,
    varimax_rotation,
)


@dataclass
class FrozenSuicaScorer:
    """Frozen SUICA same-scale scorer."""

    vectorizer: TfidfVectorizer
    svd: TruncatedSVD
    vector_scaler: StandardScaler
    gmm: GaussianMixture
    node_ids: list[str]
    pop_share: np.ndarray
    node_mean: np.ndarray
    node_std: np.ndarray
    selected_node_features: list[str]
    node_feature_names: list[str]
    node_scaler: StandardScaler
    pca: PCA
    rotation: np.ndarray
    factor_signs: np.ndarray
    factor_scaler: StandardScaler
    factor_names: list[str]
    config: dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run frozen SUICA portability validation.")
    parser.add_argument(
        "--source-slices",
        default="results/suica_strategy_search_v3_svd32_method_stripped/fixed_128__gmm_soft__method_stripped/slices.csv",
    )
    parser.add_argument("--big5-prepared", default="data_sets/prepared/pandora_official/pandora_official_big5_prepared.csv")
    parser.add_argument("--pandora-comments", default="data_sets/PANDORA_official/all_comments_since_2015.csv")
    parser.add_argument("--essays-prepared", default="data_sets/prepared/big5/essays_original_prepared.csv")
    parser.add_argument("--x-posts", default="data_sets/x_fullmarkettext/memory_semis_3m_20260318_20260617_merged/x_posts.csv")
    parser.add_argument("--output-dir", default="results/suica_portability_validation_v1")
    parser.add_argument("--report-path", default="reports/suica_portability_validation_v1.md")
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
    parser.add_argument("--max-pandora-comments-per-user", type=int, default=80)
    parser.add_argument("--max-essays-users", type=int, default=1000)
    parser.add_argument("--max-x-users", type=int, default=500)
    parser.add_argument("--min-x-posts-per-user", type=int, default=4)
    parser.add_argument("--x-lang", default="en")
    return parser.parse_args()


def safe_corr(x: pd.Series | np.ndarray, y: pd.Series | np.ndarray) -> tuple[float, float, int]:
    xv = pd.to_numeric(pd.Series(x), errors="coerce")
    yv = pd.to_numeric(pd.Series(y), errors="coerce")
    mask = xv.notna() & yv.notna()
    n = int(mask.sum())
    if n < 4:
        return float("nan"), float("nan"), n
    xa = xv.loc[mask].to_numpy(float)
    ya = yv.loc[mask].to_numpy(float)
    if np.std(xa) < 1e-12 or np.std(ya) < 1e-12:
        return float("nan"), float("nan"), n
    result = stats.pearsonr(xa, ya)
    return float(result.statistic), float(result.pvalue), n


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom < 1e-12:
        return float("nan")
    return float(np.dot(a, b) / denom)


def factor_cols(frame: pd.DataFrame) -> list[str]:
    return [col for col in frame.columns if col.startswith("suica_factor_")]


def load_source_slices(path: Path) -> pd.DataFrame:
    slices = pd.read_csv(path)
    required = {"user_id", "slice_text", "slice_index"}
    missing = sorted(required - set(slices.columns))
    if missing:
        raise ValueError(f"source slices missing columns: {missing}")
    slices["user_id"] = slices["user_id"].astype(str)
    slices["slice_index"] = pd.to_numeric(slices["slice_index"], errors="coerce").fillna(0).astype(int)
    return slices.reset_index(drop=True)


def raw_soft_node_scores(
    slices: pd.DataFrame,
    probs: np.ndarray,
    node_ids: list[str],
    *,
    pop_share: np.ndarray,
    eps: float = 1e-4,
) -> pd.DataFrame:
    users = sorted(slices["user_id"].astype(str).unique().tolist())
    user_pos = {user_id: idx for idx, user_id in enumerate(users)}
    sums = np.zeros((len(users), len(node_ids)), dtype=float)
    totals = np.zeros(len(users), dtype=float)
    for idx, user_id in enumerate(slices["user_id"].astype(str)):
        pos = user_pos[user_id]
        totals[pos] += 1.0
        sums[pos, :] += probs[idx]
    totals = np.maximum(totals, 1.0)
    user_share = sums / totals[:, None]
    scores = np.log((user_share + eps) / (pop_share[None, :] + eps))
    out = pd.DataFrame(scores, columns=[f"suica_node::{node_id}" for node_id in node_ids])
    out.insert(0, "user_id", users)
    out.insert(1, "token_slice_count", totals.astype(int))
    return out


def zscore_node_scores(raw_scores: pd.DataFrame, mean: np.ndarray, std: np.ndarray, node_features: list[str]) -> pd.DataFrame:
    values = raw_scores[node_features].to_numpy(float)
    safe_std = np.where(std < 1e-12, 1.0, std)
    z = (values - mean[None, :]) / safe_std[None, :]
    out = pd.DataFrame(z, columns=node_features)
    out.insert(0, "user_id", raw_scores["user_id"].astype(str).to_numpy())
    out.insert(1, "token_slice_count", raw_scores["token_slice_count"].to_numpy())
    return out


def fit_frozen_scorer(source_slices: pd.DataFrame, args: argparse.Namespace) -> tuple[FrozenSuicaScorer, pd.DataFrame, pd.DataFrame]:
    texts = source_slices["slice_text"].fillna("").astype(str).map(lambda text: controlled_slice_text(text, "method_stripped"))
    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        analyzer="word",
        ngram_range=(1, 2),
        max_features=args.tfidf_max_features,
        min_df=args.tfidf_min_df,
        sublinear_tf=True,
    )
    tfidf = vectorizer.fit_transform(texts)
    dims = int(min(args.svd_dims, max(2, tfidf.shape[0] - 1), max(2, tfidf.shape[1] - 1)))
    svd = TruncatedSVD(n_components=dims, random_state=args.random_seed)
    dense = svd.fit_transform(tfidf)
    vector_scaler = StandardScaler()
    vectors = vector_scaler.fit_transform(dense)
    gmm = GaussianMixture(
        n_components=args.gmm_k,
        covariance_type="diag",
        random_state=args.random_seed,
        max_iter=120,
        reg_covar=1e-5,
    )
    gmm.fit(vectors)
    probs = gmm.predict_proba(vectors)
    node_ids = [f"gmm_{idx:02d}" for idx in range(args.gmm_k)]
    pop_share = probs.mean(axis=0)
    raw_nodes = raw_soft_node_scores(source_slices, probs, node_ids, pop_share=pop_share)
    node_features = [col for col in raw_nodes.columns if col.startswith("suica_node::")]
    node_mean = raw_nodes[node_features].to_numpy(float).mean(axis=0)
    node_std = raw_nodes[node_features].to_numpy(float).std(axis=0)
    node_scores = zscore_node_scores(raw_nodes, node_mean, node_std, node_features)
    even_mask = source_slices["slice_index"].astype(int).mod(2).eq(0).to_numpy()
    odd_mask = ~even_mask
    rel_even_raw = raw_soft_node_scores(source_slices.loc[even_mask].reset_index(drop=True), probs[even_mask], node_ids, pop_share=pop_share)
    rel_odd_raw = raw_soft_node_scores(source_slices.loc[odd_mask].reset_index(drop=True), probs[odd_mask], node_ids, pop_share=pop_share)
    reliability = split_half_reliability(
        zscore_node_scores(rel_even_raw, node_mean, node_std, node_features),
        zscore_node_scores(rel_odd_raw, node_mean, node_std, node_features),
    )
    rel_map = reliability.set_index("feature")["split_half_r"].to_dict()
    selected = [feature for feature in node_features if float(rel_map.get(feature, 0.0) or 0.0) >= args.factor_min_reliability]
    if len(selected) < args.factor_min_features:
        selected = sorted(node_features, key=lambda feature: float(rel_map.get(feature, 0.0) or 0.0), reverse=True)[
            : min(len(node_features), max(args.factor_min_features, args.factor_count + 1))
        ]
    n_components = int(min(args.factor_count, len(selected), max(1, len(node_scores) - 1)))
    node_scaler = StandardScaler()
    x = node_scaler.fit_transform(node_scores[selected].to_numpy(float))
    pca = PCA(n_components=n_components, random_state=args.random_seed)
    raw_scores = pca.fit_transform(x)
    loadings = pca.components_.T * np.sqrt(np.maximum(pca.explained_variance_, 0.0))[None, :]
    rotation = varimax_rotation(loadings) if n_components > 1 else np.eye(n_components)
    rotated_loadings = loadings @ rotation
    raw_scores = raw_scores @ rotation
    signs = np.ones(n_components, dtype=float)
    for idx in range(n_components):
        strongest = int(np.nanargmax(np.abs(rotated_loadings[:, idx])))
        if rotated_loadings[strongest, idx] < 0:
            signs[idx] = -1.0
            rotated_loadings[:, idx] *= -1.0
            raw_scores[:, idx] *= -1.0
    factor_scaler = StandardScaler()
    factor_values = factor_scaler.fit_transform(raw_scores)
    factor_names = [f"suica_factor_{idx + 1:02d}" for idx in range(n_components)]
    factor_scores = pd.DataFrame(factor_values, columns=factor_names)
    factor_scores.insert(0, "user_id", node_scores["user_id"].astype(str).to_numpy())
    node_terms = top_terms_for_soft_nodes(tfidf, vectorizer, probs, node_ids)
    scorer = FrozenSuicaScorer(
        vectorizer=vectorizer,
        svd=svd,
        vector_scaler=vector_scaler,
        gmm=gmm,
        node_ids=node_ids,
        pop_share=pop_share,
        node_mean=node_mean,
        node_std=node_std,
        selected_node_features=selected,
        node_feature_names=node_features,
        node_scaler=node_scaler,
        pca=pca,
        rotation=rotation,
        factor_signs=signs,
        factor_scaler=factor_scaler,
        factor_names=factor_names,
        config={
            "slice_tokens": args.slice_tokens,
            "min_slice_tokens": args.min_slice_tokens,
            "tfidf_max_features": args.tfidf_max_features,
            "tfidf_min_df": args.tfidf_min_df,
            "svd_dims": dims,
            "gmm_k": args.gmm_k,
            "factor_count": n_components,
            "text_control": "method_stripped",
        },
    )
    return scorer, factor_scores, reliability.merge(node_terms, on="node_id", how="left")


def score_slices(slices: pd.DataFrame, scorer: FrozenSuicaScorer) -> tuple[pd.DataFrame, pd.DataFrame]:
    if slices.empty:
        return pd.DataFrame(columns=["user_id", *scorer.factor_names]), pd.DataFrame()
    texts = slices["slice_text"].fillna("").astype(str).map(lambda text: controlled_slice_text(text, "method_stripped"))
    tfidf = scorer.vectorizer.transform(texts)
    vectors = scorer.vector_scaler.transform(scorer.svd.transform(tfidf))
    probs = scorer.gmm.predict_proba(vectors)
    raw_nodes = raw_soft_node_scores(slices, probs, scorer.node_ids, pop_share=scorer.pop_share)
    node_scores = zscore_node_scores(raw_nodes, scorer.node_mean, scorer.node_std, scorer.node_feature_names)
    x = scorer.node_scaler.transform(node_scores[scorer.selected_node_features].to_numpy(float))
    raw = scorer.pca.transform(x) @ scorer.rotation
    raw = raw * scorer.factor_signs[None, :]
    values = scorer.factor_scaler.transform(raw)
    factor_scores = pd.DataFrame(values, columns=scorer.factor_names)
    factor_scores.insert(0, "user_id", node_scores["user_id"].astype(str).to_numpy())
    factor_scores.insert(1, "token_slice_count", node_scores["token_slice_count"].to_numpy())
    return factor_scores, node_scores


def slices_from_text(user_id: str, text: str, *, split_prefix: str, args: argparse.Namespace) -> list[dict[str, Any]]:
    rows = []
    for row in fixed_token_slices_for_text(
        text,
        slice_tokens=args.slice_tokens,
        stride=args.slice_tokens,
        min_slice_tokens=args.min_slice_tokens,
        max_slices=args.max_slices_per_user_split,
    ):
        row["user_id"] = str(user_id)
        row["score_split"] = split_prefix
        rows.append(row)
    return rows


def make_essays_slices(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    data = pd.read_csv(args.essays_prepared)
    data["user_id"] = data["user_id"].astype(str)
    if args.max_essays_users:
        data = data.sort_values("user_id").head(args.max_essays_users)
    rows: list[dict[str, Any]] = []
    for row in data.itertuples(index=False):
        all_slices = fixed_token_slices_for_text(
            str(row.text),
            slice_tokens=args.slice_tokens,
            stride=args.slice_tokens,
            min_slice_tokens=args.min_slice_tokens,
            max_slices=args.max_slices_per_user_split * 2,
        )
        for item in all_slices:
            item["user_id"] = str(row.user_id)
            item["score_split"] = "even_slice" if int(item["slice_index"]) % 2 == 0 else "odd_slice"
            rows.append(item)
    slices = pd.DataFrame(rows)
    labels = data[["user_id", *[trait for trait in BIG5_TRAITS if trait in data.columns]]].copy()
    return slices, labels


def make_x_slices(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    posts = pd.read_csv(args.x_posts)
    required = {"account_id", "text", "timestamp"}
    missing = sorted(required - set(posts.columns))
    if missing:
        raise ValueError(f"X posts missing columns: {missing}")
    if "lang" in posts.columns and args.x_lang:
        posts = posts.loc[posts["lang"].astype(str).eq(args.x_lang)].copy()
    posts["user_id"] = posts["account_id"].astype(str)
    posts["timestamp"] = pd.to_datetime(posts["timestamp"], errors="coerce", utc=True)
    posts["text"] = posts["text"].fillna("").astype(str)
    posts = posts.loc[posts["timestamp"].notna() & posts["text"].str.len().gt(0)].sort_values(["user_id", "timestamp"])
    counts = posts.groupby("user_id").size().sort_values(ascending=False)
    users = counts.loc[counts >= args.min_x_posts_per_user].index.tolist()
    if args.max_x_users:
        users = users[: args.max_x_users]
    posts = posts.loc[posts["user_id"].isin(users)].copy()
    rows: list[dict[str, Any]] = []
    meta_rows: list[dict[str, Any]] = []
    for user_id, group in posts.groupby("user_id", sort=True):
        group = group.sort_values("timestamp")
        midpoint = max(1, len(group) // 2)
        parts = [("early_time", group.iloc[:midpoint]), ("late_time", group.iloc[midpoint:])]
        for split, part in parts:
            text = "\n".join(part["text"].astype(str).tolist())
            split_rows = slices_from_text(user_id, text, split_prefix=split, args=args)
            rows.extend(split_rows)
            meta_rows.append(
                {
                    "user_id": user_id,
                    "score_split": split,
                    "post_count": int(len(part)),
                    "first_timestamp": part["timestamp"].min().isoformat() if len(part) else "",
                    "last_timestamp": part["timestamp"].max().isoformat() if len(part) else "",
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(meta_rows)


def make_pandora_temporal_slices(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame]:
    labels = pd.read_csv(args.big5_prepared)
    labels["user_id"] = labels["user_id"].astype(str)
    target_users = set(labels.sort_values("user_id").head(args.max_pandora_users)["user_id"].tolist())
    comments: list[pd.DataFrame] = []
    usecols = ["author", "body", "created_utc", "lang"]
    for chunk in pd.read_csv(args.pandora_comments, usecols=usecols, chunksize=200000):
        chunk = chunk.loc[chunk["author"].astype(str).isin(target_users)].copy()
        if chunk.empty:
            continue
        if "lang" in chunk.columns:
            chunk = chunk.loc[chunk["lang"].fillna("en").astype(str).eq("en")]
        chunk["body"] = chunk["body"].fillna("").astype(str)
        chunk = chunk.loc[chunk["body"].str.len().gt(0)]
        comments.append(chunk)
    if not comments:
        return pd.DataFrame(), labels[["user_id", *BIG5_TRAITS]]
    data = pd.concat(comments, ignore_index=True)
    data["user_id"] = data["author"].astype(str)
    data["created_utc"] = pd.to_numeric(data["created_utc"], errors="coerce")
    data = data.loc[data["created_utc"].notna()].sort_values(["user_id", "created_utc"])
    rows: list[dict[str, Any]] = []
    meta_rows: list[dict[str, Any]] = []
    for user_id, group in data.groupby("user_id", sort=True):
        group = group.head(args.max_pandora_comments_per_user)
        if len(group) < 4:
            continue
        midpoint = max(1, len(group) // 2)
        for split, part in [("early_time", group.iloc[:midpoint]), ("late_time", group.iloc[midpoint:])]:
            text = "\n".join(part["body"].astype(str).tolist())
            rows.extend(slices_from_text(user_id, text, split_prefix=split, args=args))
            meta_rows.append(
                {
                    "user_id": user_id,
                    "score_split": split,
                    "comment_count": int(len(part)),
                    "first_created_utc": float(part["created_utc"].min()) if len(part) else np.nan,
                    "last_created_utc": float(part["created_utc"].max()) if len(part) else np.nan,
                }
            )
    return pd.DataFrame(rows), labels[["user_id", *BIG5_TRAITS]].copy().merge(pd.DataFrame(meta_rows), on="user_id", how="left")


def score_by_split(dataset: str, slices: pd.DataFrame, scorer: FrozenSuicaScorer) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    if slices.empty:
        return pd.DataFrame()
    slices = slices.copy().reset_index(drop=True)
    slices["global_slice_id"] = np.arange(len(slices))
    for split, group in slices.groupby("score_split", sort=True):
        scores, _nodes = score_slices(group.reset_index(drop=True), scorer)
        if scores.empty:
            continue
        scores.insert(0, "dataset", dataset)
        scores.insert(2, "score_split", split)
        rows.append(scores)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def split_reliability(scores: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if scores.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    factor_names = factor_cols(scores)
    splits = sorted(scores["score_split"].unique().tolist())
    if len(splits) < 2:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    left, right = splits[:2]
    a = scores.loc[scores["score_split"].eq(left), ["user_id", *factor_names]].copy()
    b = scores.loc[scores["score_split"].eq(right), ["user_id", *factor_names]].copy()
    merged = a.merge(b, on="user_id", suffixes=("_a", "_b"))
    factor_rows: list[dict[str, Any]] = []
    for factor in factor_names:
        r, p, n = safe_corr(merged[f"{factor}_a"], merged[f"{factor}_b"])
        factor_rows.append({"factor": factor, "split_a": left, "split_b": right, "split_half_r": r, "split_half_p": p, "n": n})
    profile_rows: list[dict[str, Any]] = []
    for row in merged.itertuples(index=False):
        avec = np.array([getattr(row, f"{factor}_a") for factor in factor_names], dtype=float)
        bvec = np.array([getattr(row, f"{factor}_b") for factor in factor_names], dtype=float)
        profile_rows.append({"user_id": row.user_id, "profile_cosine": cosine(avec, bvec), "profile_pearson_r": safe_corr(avec, bvec)[0]})
    wide = merged
    return pd.DataFrame(factor_rows), pd.DataFrame(profile_rows), wide


def random_control(wide: pd.DataFrame, factor_names: list[str], *, seed: int, permutation_count: int) -> pd.DataFrame:
    if wide.empty:
        return pd.DataFrame()
    rng = np.random.default_rng(seed)
    a = wide[[f"{factor}_a" for factor in factor_names]].to_numpy(float)
    b = wide[[f"{factor}_b" for factor in factor_names]].to_numpy(float)
    actual = np.array([cosine(avec, bvec) for avec, bvec in zip(a, b)], dtype=float)
    perm_medians = []
    for _ in range(permutation_count):
        order = rng.permutation(len(b))
        perm_medians.append(float(np.nanmedian([cosine(avec, b[j]) for avec, j in zip(a, order)])))
    actual_median = float(np.nanmedian(actual))
    return pd.DataFrame(
        [
            {
                "actual_median_profile_cosine": actual_median,
                "actual_mean_profile_cosine": float(np.nanmean(actual)),
                "permutation_median_mean": float(np.mean(perm_medians)),
                "permutation_median_sd": float(np.std(perm_medians)),
                "p_perm_median_ge_actual": float((np.asarray(perm_medians) >= actual_median).mean()),
                "permutation_count": int(permutation_count),
            }
        ]
    )


def external_big5(scores: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    if scores.empty or labels.empty:
        return pd.DataFrame()
    factor_names = factor_cols(scores)
    agg = scores.groupby("user_id", as_index=False)[factor_names].mean()
    merged = agg.merge(labels[["user_id", *[trait for trait in BIG5_TRAITS if trait in labels.columns]]], on="user_id", how="inner")
    rows: list[dict[str, Any]] = []
    for trait in [trait for trait in BIG5_TRAITS if trait in merged.columns]:
        for factor in factor_names:
            r, p, n = safe_corr(merged[factor], merged[trait])
            rows.append({"trait": trait, "factor": factor, "pearson_r": r, "pearson_p": p, "n": n, "abs_pearson_r": abs(r) if np.isfinite(r) else np.nan})
    if not rows:
        return pd.DataFrame(columns=["trait", "factor", "pearson_r", "pearson_p", "n", "abs_pearson_r"])
    return pd.DataFrame(rows).sort_values(["trait", "abs_pearson_r"], ascending=[True, False])


def summarize_dataset(dataset: str, slices: pd.DataFrame, scores: pd.DataFrame, factor_rel: pd.DataFrame, profile_rel: pd.DataFrame, control: pd.DataFrame, big5: pd.DataFrame) -> dict[str, Any]:
    out: dict[str, Any] = {
        "dataset": dataset,
        "slice_count": int(len(slices)),
        "scored_users": int(scores["user_id"].nunique()) if not scores.empty else 0,
        "splits": ",".join(sorted(scores["score_split"].unique().tolist())) if not scores.empty else "",
        "mean_factor_split_half_r": float(pd.to_numeric(factor_rel.get("split_half_r", pd.Series(dtype=float)), errors="coerce").mean()) if not factor_rel.empty else np.nan,
        "median_profile_cosine": float(profile_rel["profile_cosine"].median()) if not profile_rel.empty else np.nan,
        "mean_profile_cosine": float(profile_rel["profile_cosine"].mean()) if not profile_rel.empty else np.nan,
        "random_p": float(control["p_perm_median_ge_actual"].iloc[0]) if not control.empty else np.nan,
        "top_big5_abs_r": float(pd.to_numeric(big5.get("abs_pearson_r", pd.Series(dtype=float)), errors="coerce").max()) if not big5.empty else np.nan,
    }
    return out


def write_report(path: Path, *, out_dir: Path, summary: pd.DataFrame, model_reliability: pd.DataFrame) -> None:
    lines = [
        "# SUICA Portability Validation v1",
        "",
        "## Purpose",
        "",
        "This report tests whether a SUICA scale fitted once on PANDORA can score other text environments without refitting. The goal is general measurement stability across text, situation, platform, and time.",
        "",
        "## Method",
        "",
        "1. Fit frozen SUICA cells/factors on PANDORA `fixed_128 + gmm_soft + method_stripped` source slices.",
        "2. Score PANDORA temporal halves, Essays split slices, and English X market account halves with the same frozen scorer.",
        "3. Evaluate split-half factor reliability, same-user profile cosine, random-pair controls, and external Big5 anchors where labels exist.",
        "",
        "## Source Model Reliability",
        "",
        model_reliability.head(18).to_markdown(index=False),
        "",
        "## Dataset Summary",
        "",
        summary.to_markdown(index=False),
        "",
        "## Interpretation",
        "",
    ]
    for row in summary.itertuples(index=False):
        if getattr(row, "random_p") <= 0.01 and getattr(row, "median_profile_cosine") > 0.20:
            lines.append(f"- `{row.dataset}`: same-user profile stability is above random; SUICA has portable author-level measurement signal here.")
        elif getattr(row, "scored_users") < 50:
            lines.append(f"- `{row.dataset}`: too few scored users for a firm portability claim.")
        else:
            lines.append(f"- `{row.dataset}`: portability is weak; this corpus likely needs better text segmentation, language handling, or domain-specific calibration.")
    lines.extend(
        [
            "",
            "## Theoretical Consequence",
            "",
            "The main SUICA theory should distinguish two layers:",
            "",
            "- universal scoring layer: frozen shared cells/factors that should retain same-user geometry across corpora;",
            "- domain adaptation layer: optional corpus-specific calibration for topic, language, task, and platform without changing the underlying factor definitions.",
            "",
            "A finished SUICA scale requires the universal layer to pass repeated portability tests before domain-specific optimization is allowed.",
            "",
            "## Artifacts",
            "",
            f"- Results directory: `{out_dir}`",
            "- `frozen_suica_model.joblib`",
            "- `source_model_factor_scores.csv`",
            "- `source_model_node_reliability.csv`",
            "- `portability_summary.csv`",
            "- per-dataset `*_split_scores.csv`, `*_factor_reliability.csv`, `*_profile_reliability.csv`, `*_random_control.csv`, `*_big5_external_validity.csv`",
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
    dump(scorer, out_dir / "frozen_suica_model.joblib")
    source_scores.to_csv(out_dir / "source_model_factor_scores.csv", index=False)
    source_reliability.to_csv(out_dir / "source_model_node_reliability.csv", index=False)

    datasets: list[tuple[str, pd.DataFrame, pd.DataFrame]] = []
    pandora_slices, pandora_labels = make_pandora_temporal_slices(args)
    datasets.append(("pandora_temporal", pandora_slices, pandora_labels))
    essays_slices, essays_labels = make_essays_slices(args)
    datasets.append(("essays_split", essays_slices, essays_labels))
    x_slices, x_meta = make_x_slices(args)
    datasets.append(("x_market_en_temporal", x_slices, x_meta))

    summary_rows: list[dict[str, Any]] = []
    for dataset, slices, labels in datasets:
        slices.to_csv(out_dir / f"{dataset}_slices.csv", index=False)
        scores = score_by_split(dataset, slices, scorer)
        scores.to_csv(out_dir / f"{dataset}_split_scores.csv", index=False)
        factor_rel, profile_rel, wide = split_reliability(scores)
        factor_rel.to_csv(out_dir / f"{dataset}_factor_reliability.csv", index=False)
        profile_rel.to_csv(out_dir / f"{dataset}_profile_reliability.csv", index=False)
        factors = factor_cols(scores)
        control = random_control(wide, factors, seed=args.random_seed, permutation_count=args.permutation_count) if factors else pd.DataFrame()
        control.to_csv(out_dir / f"{dataset}_random_control.csv", index=False)
        big5 = external_big5(scores, labels)
        big5.to_csv(out_dir / f"{dataset}_big5_external_validity.csv", index=False)
        summary_rows.append(summarize_dataset(dataset, slices, scores, factor_rel, profile_rel, control, big5))
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(out_dir / "portability_summary.csv", index=False)
    (out_dir / "run_config.json").write_text(json.dumps(vars(args), ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(Path(args.report_path), out_dir=out_dir, summary=summary, model_reliability=source_reliability)
    print(summary.to_string(index=False))
    print(f"\nReport: {args.report_path}")


if __name__ == "__main__":
    main()
