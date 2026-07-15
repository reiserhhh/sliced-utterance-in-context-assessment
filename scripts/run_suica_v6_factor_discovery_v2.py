#!/usr/bin/env python
"""Raw-comment, opportunity-conditioned SUICA V6 factor discovery.

The run discovers stable text-behavior structure without Big Five, MBTI,
Enneagram or the frozen SUICA construct inventory.  It uses a discovery-only
TF-IDF/SVD representation, author-cross-fitted nuisance prediction, one
opportunity axis built from surface/format profiles (never from text outcomes),
and three conditionally ordered author objects:

    Static S = author residual level under shared opportunity control
    Hybrid H = author response to the opportunity axis, conditional on S
    Dynamic D = real chronological within-condition motion, conditional on S,H
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.factor_discovery import (  # noqa: E402
    fit_stable_crossview,
    safe_corr,
    stable_user_split,
    subspace_similarity,
    transform_stable_crossview,
)
from suica_core.suica import PERSONALITY_LEAK_RE  # noqa: E402

TOKEN_RE = re.compile(r"[A-Za-z0-9']+|[^\w\s]", re.UNICODE)
Q_COLS = [
    "log_tokens", "log_chars", "url_rate", "quote_rate", "list_rate",
    "code_rate", "digit_rate", "question_rate", "exclamation_rate",
    "punctuation_rate",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=ROOT / "data_sets/prepared/suica_tiers_v2/tier_u_comments.parquet")
    parser.add_argument("--config", type=Path, default=ROOT / "configs/v6_factor_discovery_raw.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/v6_factor_discovery_raw")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/V6_FACTOR_DISCOVERY_REPORT.md")
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def stable_fold(user: str, folds: int) -> int:
    digest = hashlib.sha256(f"v6-nuisance::{user}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % folds


def surface_features(text: str) -> dict[str, float]:
    tokens = TOKEN_RE.findall(text or "")
    n = max(1, len(tokens))
    chars = max(1, len(text or ""))
    punct = sum(1 for t in tokens if len(t) == 1 and not t.isalnum())
    lines = (text or "").splitlines() or [""]
    return {
        "log_tokens": float(np.log1p(n)),
        "log_chars": float(np.log1p(chars)),
        "url_rate": float(len(re.findall(r"https?://|www\.", text or "", re.I)) / n),
        "quote_rate": float(sum(line.lstrip().startswith(">") for line in lines) / len(lines)),
        "list_rate": float(sum(bool(re.match(r"\s*(?:[-*]|\d+[.)])\s", line)) for line in lines) / len(lines)),
        "code_rate": float(((text or "").count("`") + (text or "").count("    ")) / chars),
        "digit_rate": float(sum(ch.isdigit() for ch in (text or "")) / chars),
        "question_rate": float((text or "").count("?") / n),
        "exclamation_rate": float((text or "").count("!") / n),
        "punctuation_rate": float(punct / n),
    }


def _even_indices(n: int, cap: int) -> set[int]:
    if n <= cap:
        return set(range(n))
    return set(np.unique(np.round(np.linspace(0, n - 1, cap)).astype(int)).tolist())


def prepare_units(comments: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Sample representative comments while preserving long real runs."""
    rows = []
    comments = comments.sort_values(["author", "created_utc"]).copy()
    comments["body"] = comments["body"].fillna("").astype(str)
    comments["subreddit"] = comments["subreddit"].fillna("__missing__").astype(str)
    for user, group in comments.groupby("author", sort=False):
        if len(group) < 30:
            continue
        t40, t60 = np.quantile(group["created_utc"].to_numpy(float), [0.4, 0.6])
        if (t60 - t40) / 86400.0 < cfg["min_gap_days"]:
            continue
        for half, part in (("early", group.loc[group["created_utc"] <= t40]),
                           ("late", group.loc[group["created_utc"] >= t60])):
            part = part.reset_index(drop=True)
            conditions = part["subreddit"].to_numpy(str)
            starts = np.r_[0, 1 + np.flatnonzero(conditions[1:] != conditions[:-1])]
            ends = np.r_[starts[1:], len(part)]
            run_meta: dict[int, tuple[int, int, int]] = {}
            long_runs = []
            for run_id, (start, end) in enumerate(zip(starts, ends)):
                for pos, idx in enumerate(range(int(start), int(end))):
                    run_meta[idx] = (run_id, pos, int(end - start))
                if end - start >= cfg["dynamic_min_run_length"]:
                    long_runs.append((int(end - start), int(start), int(end)))
            long_runs.sort(reverse=True)
            dynamic_idx: set[int] = set()
            for _, start, end in long_runs:
                if len(dynamic_idx) + end - start > cfg["max_dynamic_comments_per_half"]:
                    continue
                dynamic_idx.update(range(start, end))
            representative = _even_indices(len(part), cfg["max_comments_per_half"])
            keep = dynamic_idx | representative
            for idx in sorted(keep):
                row = part.iloc[idx]
                text = str(row["body"])
                if len(text.strip()) < 10 or PERSONALITY_LEAK_RE.search(text):
                    continue
                run_id, run_pos, run_len = run_meta[idx]
                q = surface_features(text)
                rows.append({
                    "user_id": str(user), "half": half, "condition": str(row["subreddit"]),
                    "created_utc": float(row["created_utc"]), "order": int(idx),
                    "run_id": f"{user}::{half}::{run_id}", "run_pos": run_pos,
                    "run_len": run_len, "text": text, **q,
                })
    return pd.DataFrame(rows)


def fit_representation(units: pd.DataFrame, discovery_users: set[str], cfg: dict):
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer

    mask = units["user_id"].isin(discovery_users)
    vectorizer = TfidfVectorizer(
        lowercase=True, strip_accents="unicode", ngram_range=(1, 2),
        max_features=cfg["tfidf_max_features"], min_df=cfg["tfidf_min_df"],
        max_df=0.98, sublinear_tf=True, dtype=np.float32,
    )
    tf_d = vectorizer.fit_transform(units.loc[mask, "text"])
    svd = TruncatedSVD(n_components=cfg["representation_dimensions"], random_state=cfg["seed"])
    svd.fit(tf_d)
    x = svd.transform(vectorizer.transform(units["text"])).astype(np.float64)
    return vectorizer, svd, x


@dataclass
class NuisanceModel:
    q_mean: np.ndarray
    q_sd: np.ndarray
    coef: np.ndarray
    condition_half_mean: dict[tuple[str, str], np.ndarray]
    supported: set[str]


def _fit_nuisance(rows: pd.DataFrame, x: np.ndarray, supported: set[str], alpha: float) -> NuisanceModel:
    from sklearn.linear_model import Ridge

    q = rows[Q_COLS].to_numpy(float)
    q_mean, q_sd = q.mean(axis=0), q.std(axis=0, ddof=1)
    q_sd[q_sd < 1e-8] = 1.0
    half = rows["half"].eq("late").to_numpy(float)[:, None]
    design = np.column_stack([np.ones(len(rows)), (q - q_mean) / q_sd, half,
                              ((q - q_mean) / q_sd) * half])
    ridge = Ridge(alpha=alpha, fit_intercept=False).fit(design, x)
    base = ridge.predict(design)
    temp = rows[["user_id", "condition", "half"]].copy()
    for j in range(x.shape[1]):
        temp[f"r{j}"] = x[:, j] - base[:, j]
    rcols = [f"r{j}" for j in range(x.shape[1])]
    cells = temp.groupby(["user_id", "condition", "half"], observed=True)[rcols].mean()
    means = cells.groupby(["condition", "half"], observed=True)[rcols].mean()
    condition_half_mean = {
        (str(c), str(h)): means.loc[(c, h)].to_numpy(float)
        for c, h in means.index if str(c) in supported
    }
    return NuisanceModel(q_mean, q_sd, ridge.coef_.T, condition_half_mean, supported)


def _predict_nuisance(model: NuisanceModel, rows: pd.DataFrame) -> np.ndarray:
    q = rows[Q_COLS].to_numpy(float)
    half = rows["half"].eq("late").to_numpy(float)[:, None]
    design = np.column_stack([np.ones(len(rows)), (q - model.q_mean) / model.q_sd, half,
                              ((q - model.q_mean) / model.q_sd) * half])
    pred = design @ model.coef
    for i, (condition, h) in enumerate(zip(rows["condition"], rows["half"])):
        pred[i] += model.condition_half_mean.get((str(condition), str(h)), 0.0)
    return pred


def crossfit_residuals(units: pd.DataFrame, x: np.ndarray, discovery_users: set[str], cfg: dict):
    support = (units.loc[units["user_id"].isin(discovery_users)]
               .drop_duplicates(["user_id", "condition", "half"])
               .groupby(["condition", "half"])["user_id"].nunique().unstack(fill_value=0))
    supported = set(support.loc[(support.get("early", 0) >= cfg["min_condition_users_per_half"])
                                & (support.get("late", 0) >= cfg["min_condition_users_per_half"])
                                & (support.sum(axis=1) >= cfg["min_condition_users_total"])].index.astype(str))
    residual = np.full_like(x, np.nan)
    users = units["user_id"].to_numpy(str)
    discovery_mask = np.isin(users, list(discovery_users))
    models = []
    for fold in range(cfg["nuisance_folds"]):
        hold_users = {u for u in discovery_users if stable_fold(u, cfg["nuisance_folds"]) == fold}
        train = discovery_mask & ~np.isin(users, list(hold_users))
        hold = np.isin(users, list(hold_users))
        model = _fit_nuisance(units.loc[train], x[train], supported, cfg["nuisance_ridge_alpha"])
        models.append(model)
        residual[hold] = x[hold] - _predict_nuisance(model, units.loc[hold])
    confirmation = ~discovery_mask
    # Match discovery training exposure: confirmation nuisance predictions are
    # averaged over the same five 80%-author models, not a stronger 100% fit.
    confirmation_pred = np.mean(
        [_predict_nuisance(model, units.loc[confirmation]) for model in models], axis=0
    )
    residual[confirmation] = x[confirmation] - confirmation_pred
    return residual, supported


def opportunity_axis(units: pd.DataFrame, discovery_users: set[str], supported: set[str]):
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    d = units.loc[units["user_id"].isin(discovery_users) & units["condition"].isin(supported)]
    cell = d.groupby(["user_id", "condition"], observed=True)[Q_COLS].mean()
    profile = cell.groupby(level="condition")[Q_COLS].mean()
    scaled = StandardScaler().fit_transform(profile)
    pca = PCA(n_components=1, random_state=0).fit(scaled)
    z = pca.transform(scaled)[:, 0]
    z = (z - z.mean()) / max(z.std(ddof=1), 1e-8)
    return {str(c): float(z[i]) for i, c in enumerate(profile.index)}, pca.components_[0]


def build_objects(units: pd.DataFrame, residual: np.ndarray, z_map: dict[str, float], cfg: dict):
    from sklearn.decomposition import PCA

    p = residual.shape[1]
    work = units.drop(columns="text").copy()
    rcols = [f"svd_{j + 1:02d}" for j in range(p)]
    work[rcols] = residual
    static_rows, hybrid_rows = [], []
    for (user, half), group in work.groupby(["user_id", "half"], sort=False, observed=True):
        cell = group.groupby("condition", observed=True)[rcols].mean()
        a = cell.mean(axis=0).to_numpy(float)
        z = np.array([z_map.get(str(c), np.nan) for c in cell.index], float)
        static_rows.append({"user_id": user, "half": half,
                            "meta_comments": int(len(group)), "meta_conditions": int(len(cell)),
                            **{f"static::{name}": a[j] for j, name in enumerate(rcols)},
                            "meta_opportunity_choice": float(np.nanmean(z)) if np.isfinite(z).any() else np.nan})
        counts = group["condition"].value_counts()
        valid = np.isfinite(z)
        if (len(group) < cfg["hybrid_min_comments"] or valid.sum() < cfg["hybrid_min_conditions"]
                or counts.iloc[0] / len(group) > cfg["hybrid_max_condition_share"]):
            continue
        zv = z[valid]
        y = cell.to_numpy(float)[valid] - a
        zc = zv - zv.mean()
        info = float(np.sum(zc ** 2) / (np.sum(zc ** 2) + cfg["hybrid_ridge_alpha"]))
        if info < cfg["hybrid_min_information"]:
            continue
        slope = (zc[:, None] * y).sum(axis=0) / (np.sum(zc ** 2) + cfg["hybrid_ridge_alpha"])
        hybrid_rows.append({"user_id": user, "half": half, "hybrid_information": info,
                            "meta_comments": int(len(group)), "meta_conditions": int(len(cell)),
                            **{f"hybrid::{name}": slope[j] for j, name in enumerate(rcols)}})
    static = pd.DataFrame(static_rows)
    hybrid = pd.DataFrame(hybrid_rows)

    discovery_mask = work["user_id"].map(stable_user_split).eq("discovery").to_numpy()
    dyn_pca = PCA(n_components=cfg["dynamic_dimensions"], random_state=cfg["seed"]).fit(residual[discovery_mask])
    dyn_coords = dyn_pca.transform(residual)
    work[[f"dyn_{j + 1}" for j in range(cfg["dynamic_dimensions"])]] = dyn_coords
    dynamic_rows = []
    dcols = [f"dyn_{j + 1}" for j in range(cfg["dynamic_dimensions"])]
    for (user, half), group in work.groupby(["user_id", "half"], sort=False, observed=True):
        seqs = []
        transitions = 0
        for _, run in group.sort_values("order").groupby("run_id", sort=False):
            run = run.sort_values("run_pos")
            positions = run["run_pos"].to_numpy(int)
            cuts = np.r_[0, 1 + np.flatnonzero(np.diff(positions) != 1), len(run)]
            for start, end in zip(cuts[:-1], cuts[1:]):
                if end - start >= cfg["dynamic_min_run_length"]:
                    seq = run.iloc[start:end][dcols].to_numpy(float)
                    seqs.append(seq)
                    transitions += len(seq) - 1
        if len(seqs) < cfg["dynamic_min_runs"] or transitions < cfg["dynamic_min_transitions"]:
            continue
        centered = [s - s.mean(axis=0, keepdims=True) for s in seqs]
        gamma0 = sum(s.T @ s for s in centered) / sum(len(s) for s in centered)
        gamma1 = sum(s[1:].T @ s[:-1] for s in centered) / transitions
        phi = gamma1 @ np.linalg.inv(gamma0 + 0.10 * np.eye(gamma0.shape[0]))
        eig = np.log(np.maximum(np.linalg.eigvalsh(gamma0), 1e-8))[::-1]
        rough = np.sqrt(sum((np.diff(s, axis=0) ** 2).sum(axis=0) for s in centered) / transitions)
        cp = np.median(np.vstack([
            np.max(np.abs(np.cumsum(s, axis=0)[:-1]), axis=0) / np.sqrt(len(s)) for s in centered
        ]), axis=0)
        row = {"user_id": user, "half": half, "dynamic_runs": len(seqs),
               "dynamic_transitions": transitions, "meta_comments": int(len(group)),
               "meta_conditions": int(group["condition"].nunique())}
        row.update({f"dynamic::log_variance_{j + 1}": eig[j] for j in range(len(eig))})
        row.update({f"dynamic::phi_{i + 1}_{j + 1}": phi[i, j]
                    for i in range(phi.shape[0]) for j in range(phi.shape[1])})
        row.update({f"dynamic::roughness_{j + 1}": rough[j] for j in range(len(rough))})
        row.update({f"dynamic::changepoint_{j + 1}": cp[j] for j in range(len(cp))})
        dynamic_rows.append(row)
    return static, hybrid, pd.DataFrame(dynamic_rows), dyn_pca


def conditional_residual(target: pd.DataFrame, predictors: list[pd.DataFrame], prefix: str,
                         discovery_users: set[str]) -> pd.DataFrame:
    from sklearn.linear_model import Ridge
    keys = ["user_id", "half"]
    merged = target.copy()
    target_cols = [c for c in merged if c.startswith(prefix)]
    predictor_cols = []
    for i, pred in enumerate(predictors):
        cols = [c for c in pred if "::" in c]
        renamed = {c: f"p{i}::{c}" for c in cols}
        merged = merged.merge(pred[keys + cols].rename(columns=renamed), on=keys, how="inner")
        predictor_cols.extend(renamed.values())
    if not predictor_cols or merged.empty:
        return merged[keys + target_cols]
    d = merged["user_id"].isin(discovery_users)
    x_mean = merged.loc[d, predictor_cols].mean().to_numpy()
    x_sd = merged.loc[d, predictor_cols].std().replace(0, 1).to_numpy()
    x = (merged[predictor_cols].to_numpy() - x_mean) / x_sd
    # Conditional innovation is a projection, not a predictive shrinkage
    # target. A near-zero ridge only stabilizes collinear pseudoinversion.
    model = Ridge(alpha=1e-6).fit(x[d], merged.loc[d, target_cols])
    prediction = np.asarray(model.predict(x))
    if prediction.ndim == 1:
        prediction = prediction[:, None]
    merged[target_cols] = merged[target_cols].to_numpy() - prediction
    meta_cols = [c for c in target if c.startswith("meta_")]
    return merged[keys + meta_cols + target_cols]


def paired_views(frame: pd.DataFrame, feature_cols: list[str], users: set[str]):
    part = frame.loc[frame["user_id"].isin(users), ["user_id", "half", *feature_cols]]
    early = part.loc[part["half"].eq("early")].set_index("user_id")
    late = part.loc[part["half"].eq("late")].set_index("user_id")
    common = sorted(set(early.index) & set(late.index))
    return early.loc[common, feature_cols].to_numpy(float), late.loc[common, feature_cols].to_numpy(float), common


def permutation_strata(frame: pd.DataFrame, users: list[str]) -> np.ndarray:
    """Bin authors by text volume and condition support for label permutation."""
    meta_cols = [c for c in ("meta_comments", "meta_conditions") if c in frame]
    if not meta_cols:
        return np.zeros(len(users), dtype=int)
    meta = frame.groupby("user_id", observed=True)[meta_cols].mean().reindex(users)
    codes = np.zeros(len(meta), dtype=int)
    multiplier = 1
    for col in meta_cols:
        rank = meta[col].rank(method="average", pct=True).fillna(0.5).to_numpy()
        bin_code = np.minimum((rank * 3).astype(int), 2)
        codes += multiplier * bin_code
        multiplier *= 3
    # Merge thin cells so every permutation stratum has useful support.
    counts = pd.Series(codes).value_counts()
    thin = set(counts.loc[counts < 30].index)
    return np.array([-1 if c in thin else c for c in codes], dtype=int)


def bootstrap_r(x: np.ndarray, y: np.ndarray, seed: int, iterations: int = 500):
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(iterations):
        idx = rng.integers(0, len(x), len(x))
        values.append(safe_corr(x[idx], y[idx], min_n=20))
    return np.nanquantile(values, [0.025, 0.975])


def identity_diagnostics(early: np.ndarray, late: np.ndarray, seed: int,
                         n_derangements: int = 20,
                         bootstrap_iterations: int = 100) -> dict[str, float]:
    """Quantify distributed same-author information with author-bootstrap uncertainty."""
    from sklearn.metrics import roc_auc_score

    if len(early) != len(late) or len(early) < 2:
        raise ValueError("identity diagnostics require at least two paired authors")
    rng = np.random.default_rng(seed)
    own = np.linalg.norm(early - late, axis=1)
    stranger = np.empty((len(early), n_derangements), dtype=float)
    base = np.arange(len(late))
    for j in range(n_derangements):
        # A cyclic shift of a random permutation is not guaranteed to be a
        # derangement. Resample until no author's own late view is a negative.
        for _ in range(1000):
            stranger_idx = rng.permutation(len(late))
            if np.all(stranger_idx != base):
                break
        else:
            stranger_idx = np.roll(base, j % (len(base) - 1) + 1)
        stranger[:, j] = np.linalg.norm(early - late[stranger_idx], axis=1)

    def auc_for(indices: np.ndarray) -> float:
        own_sample = own[indices]
        stranger_sample = stranger[indices].reshape(-1)
        labels = np.r_[np.ones(len(own_sample)), np.zeros(len(stranger_sample))]
        scores = -np.r_[own_sample, stranger_sample]
        return float(roc_auc_score(labels, scores))

    auc = auc_for(base)
    boot = np.array([
        auc_for(rng.integers(0, len(base), len(base)))
        for _ in range(bootstrap_iterations)
    ])
    auc_lo, auc_hi = np.quantile(boot, [0.025, 0.975])
    e = early / np.maximum(np.linalg.norm(early, axis=1, keepdims=True), 1e-12)
    l = late / np.maximum(np.linalg.norm(late, axis=1, keepdims=True), 1e-12)
    similarity = e @ l.T
    own_similarity = np.diag(similarity)
    rank = 1 + np.sum(similarity > own_similarity[:, None], axis=1)
    return {
        "own_vs_stranger_auc": auc,
        "own_vs_stranger_auc_ci_lo": float(auc_lo),
        "own_vs_stranger_auc_ci_hi": float(auc_hi),
        "n_stranger_derangements": int(n_derangements),
        "bootstrap_iterations": int(bootstrap_iterations),
        "retrieval_top1": float(np.mean(rank <= 1)),
        "retrieval_top10": float(np.mean(rank <= 10)),
        "retrieval_mrr": float(np.mean(1.0 / rank)),
    }


def effective_rank(matrix: np.ndarray) -> float:
    """Entropy effective rank of the symmetrized cross-view covariance."""
    vals = np.linalg.svd(matrix, compute_uv=False)
    vals = vals[vals > 1e-12]
    if not len(vals):
        return 0.0
    p = vals / vals.sum()
    return float(np.exp(-np.sum(p * np.log(p))))


def _regularized_inverse_sqrt(covariance: np.ndarray, ridge: float = 0.10) -> np.ndarray:
    values, vectors = np.linalg.eigh((covariance + covariance.T) / 2.0)
    positive = values[values > 1e-10]
    floor = ridge * (float(np.median(positive)) if len(positive) else 1.0)
    return (vectors * (1.0 / np.sqrt(np.maximum(values, floor)))) @ vectors.T


def _standardize_blocks(*blocks: np.ndarray):
    combined = np.vstack(blocks)
    center = np.nanmean(combined, axis=0)
    scale = np.nanstd(combined, axis=0, ddof=1)
    scale[~np.isfinite(scale) | (scale < 1e-8)] = 1.0
    median = np.nanmedian(combined, axis=0)
    out = [((np.where(np.isfinite(x), x, median) - center) / scale) for x in blocks]
    return out, center, scale


def analyze_shared_hybrid(static: pd.DataFrame, dynamic: pd.DataFrame,
                          discovery_users: set[str], confirmation_users: set[str], cfg: dict):
    """Find factors sharing one author score across Static and Dynamic blocks."""
    s_cols = [c for c in static if c.startswith("static::")]
    d_cols = [c for c in dynamic if c.startswith("dynamic::")]

    def views(users: set[str]):
        se, sl, su = paired_views(static, s_cols, users)
        de, dl, du = paired_views(dynamic, d_cols, users)
        common = sorted(set(su) & set(du))
        si, di = {u: i for i, u in enumerate(su)}, {u: i for i, u in enumerate(du)}
        return (se[[si[u] for u in common]], sl[[si[u] for u in common]],
                de[[di[u] for u in common]], dl[[di[u] for u in common]], common)

    se, sl, de, dl, du = views(discovery_users)
    ce, cl, cde, cdl, cu = views(confirmation_users)
    if len(du) < 300 or len(cu) < 300:
        return {"family": "shared_hybrid", "status": "UNDECIDED_SAMPLE",
                "n_discovery_paired": len(du), "n_confirmation_paired": len(cu)}, []
    (s_blocks, s_center, s_scale) = _standardize_blocks(se, sl)
    (d_blocks, d_center, d_scale) = _standardize_blocks(de, dl)
    se, sl = s_blocks
    de, dl = d_blocks
    ws = _regularized_inverse_sqrt(np.cov(np.vstack([se, sl]).T))
    wd = _regularized_inverse_sqrt(np.cov(np.vstack([de, dl]).T))

    def decompose(ae: np.ndarray, al: np.ndarray, be: np.ndarray, bl: np.ndarray):
        cross = (ae.T @ bl + al.T @ be) / (2.0 * max(len(ae) - 1, 1))
        u, singular, vh = np.linalg.svd(ws @ cross @ wd)
        return singular, ws @ u, wd @ vh.T

    singular, s_dir, d_dir = decompose(se, sl, de, dl)
    rng = np.random.default_rng(cfg["seed"] + 7777)
    permutations = 50 if cfg.get("quick") else cfg["factor_permutations"]
    null = np.empty((permutations, len(singular)))
    for b in range(permutations):
        perm = rng.permutation(len(de))
        null[b] = decompose(se, sl, de[perm], dl[perm])[0]
    threshold = np.quantile(null, 0.95, axis=0)
    share = singular / max(singular.sum(), 1e-12)
    k = min(cfg["factor_max_per_family"], int(np.sum(
        (singular > threshold) & (share >= cfg["factor_min_stable_share"])
    )))
    if k == 0:
        return {"family": "shared_hybrid", "status": "NO_DISCOVERY",
                "n_discovery_paired": len(du), "n_confirmation_paired": len(cu)}, []
    s_dir, d_dir = s_dir[:, :k], d_dir[:, :k]
    s_dir /= np.maximum(np.linalg.norm(s_dir, axis=0, keepdims=True), 1e-12)
    d_dir /= np.maximum(np.linalg.norm(d_dir, axis=0, keepdims=True), 1e-12)

    cs = (np.where(np.isfinite(np.vstack([ce, cl])), np.vstack([ce, cl]), s_center) - s_center) / s_scale
    cd = (np.where(np.isfinite(np.vstack([cde, cdl])), np.vstack([cde, cdl]), d_center) - d_center) / d_scale
    ce, cl = cs[:len(ce)], cs[len(ce):]
    cde, cdl = cd[:len(cde)], cd[len(cde):]
    ss_e, ss_l = ce @ s_dir, cl @ s_dir
    ds_e, ds_l = cde @ d_dir, cdl @ d_dir

    # Confirmation subspaces are fitted independently with discovery rank frozen.
    vcs = _regularized_inverse_sqrt(np.cov(np.vstack([ce, cl]).T))
    vcd = _regularized_inverse_sqrt(np.cov(np.vstack([cde, cdl]).T))
    cross_c = (ce.T @ cdl + cl.T @ cde) / (2.0 * max(len(ce) - 1, 1))
    uc, _, vhc = np.linalg.svd(vcs @ cross_c @ vcd)
    sim_s, angle_s = subspace_similarity(s_dir, vcs @ uc[:, :k])
    sim_d, angle_d = subspace_similarity(d_dir, vcd @ vhc.T[:, :k])

    rows = []
    combined_e, combined_l = [], []
    for j in range(k):
        # Orient dynamic expression to positive cross-lag relation.
        cross_lag = np.nanmean([safe_corr(ss_e[:, j], ds_l[:, j]),
                                safe_corr(ss_l[:, j], ds_e[:, j])])
        if cross_lag < 0:
            ds_e[:, j] *= -1
            ds_l[:, j] *= -1
            d_dir[:, j] *= -1
            cross_lag *= -1
        h_e = (ss_e[:, j] + ds_e[:, j]) / 2.0
        h_l = (ss_l[:, j] + ds_l[:, j]) / 2.0
        r = safe_corr(h_e, h_l)
        lo, hi = bootstrap_r(h_e, h_l, cfg["seed"] + 8000 + j,
                             100 if cfg.get("quick") else 500)
        top_s = np.argsort(-np.abs(s_dir[:, j]))[:4]
        top_d = np.argsort(-np.abs(d_dir[:, j]))[:4]
        rows.append({
            "factor_id": f"shared_hybrid_F{j + 1}", "family": "shared_hybrid",
            "stable_singular_value": float(singular[j]), "stable_share": float(share[j]),
            "cross_lag_relation": float(cross_lag), "confirmation_reliability": r,
            "reliability_ci_lo": float(lo), "reliability_ci_hi": float(hi),
            "static_signature": "; ".join(f"{s_cols[i]} ({s_dir[i, j]:+.3f})" for i in top_s),
            "dynamic_signature": "; ".join(f"{d_cols[i]} ({d_dir[i, j]:+.3f})" for i in top_d),
            "axis_confirmed": bool(r >= cfg["confirmation_min_reliability"]
                                   and lo >= cfg["confirmation_reliability_ci_floor"]
                                   and cross_lag >= 0.10),
        })
        combined_e.append(h_e)
        combined_l.append(h_l)
    identity = identity_diagnostics(np.column_stack(combined_e), np.column_stack(combined_l),
                                    cfg["seed"] + 9000)
    supported = (sim_s >= cfg["confirmation_min_subspace_similarity"]
                 and sim_d >= cfg["confirmation_min_subspace_similarity"]
                 and angle_s <= cfg["confirmation_max_principal_angle"]
                 and angle_d <= cfg["confirmation_max_principal_angle"]
                 and identity["own_vs_stranger_auc"] >= cfg["confirmation_min_own_stranger_auc"]
                 and any(row["axis_confirmed"] for row in rows))
    return {
        "family": "shared_hybrid", "status": "SUPPORTED_INTERNAL" if supported else "REJECTED_VALIDATION",
        "n_discovery_paired": len(du), "n_confirmation_paired": len(cu), "n_factors": k,
        "static_subspace_similarity": sim_s, "static_max_angle_deg": angle_s,
        "dynamic_subspace_similarity": sim_d, "dynamic_max_angle_deg": angle_d,
        "own_vs_stranger_auc": identity["own_vs_stranger_auc"],
        "own_vs_stranger_auc_ci_lo": identity["own_vs_stranger_auc_ci_lo"],
        "own_vs_stranger_auc_ci_hi": identity["own_vs_stranger_auc_ci_hi"],
        "n_axes_confirmed": int(sum(row["axis_confirmed"] for row in rows)),
    }, rows


def analyze_family(name: str, frame: pd.DataFrame, discovery_users: set[str], confirmation_users: set[str],
                   cfg: dict, seed_offset: int):
    feature_cols = [c for c in frame if c.startswith(f"{name}::")]
    de, dl, du = paired_views(frame, feature_cols, discovery_users)
    ce, cl, cu = paired_views(frame, feature_cols, confirmation_users)
    if len(du) < max(300, 10 * len(feature_cols)) or len(cu) < max(300, 10 * len(feature_cols)):
        return {"family": name, "status": "UNDECIDED_SAMPLE", "features": len(feature_cols),
                "n_discovery_paired": len(du), "n_confirmation_paired": len(cu)}, [], None
    bins_n = permutation_strata(frame, du)
    permutations = 50 if cfg.get("quick") else cfg["factor_permutations"]
    fit = fit_stable_crossview(
        de, dl, n_permutations=permutations, max_factors=cfg["factor_max_per_family"],
        min_stable_share=cfg["factor_min_stable_share"], strata=np.asarray(bins_n),
        seed=cfg["seed"] + seed_offset,
    )
    if fit.n_factors == 0:
        return {"family": name, "status": "NO_DISCOVERY", "features": len(feature_cols),
                "n_discovery_paired": len(du), "n_confirmation_paired": len(cu)}, [], fit
    validation = fit_stable_crossview(ce, cl, n_permutations=0, forced_factors=fit.n_factors,
                                      max_factors=fit.n_factors, seed=cfg["seed"] + seed_offset + 100)
    similarity, angle = subspace_similarity(fit.directions, validation.directions)
    se, sl = transform_stable_crossview(ce, fit), transform_stable_crossview(cl, fit)
    factor_identity = identity_diagnostics(se, sl, cfg["seed"] + seed_offset)
    ce_z = (np.where(np.isfinite(ce), ce, fit.center) - fit.center) / fit.scale
    cl_z = (np.where(np.isfinite(cl), cl, fit.center) - fit.center) / fit.scale
    full_identity = identity_diagnostics(ce_z, cl_z, cfg["seed"] + seed_offset + 17)
    projector = fit.rotated_directions @ np.linalg.pinv(fit.rotated_directions)
    re, rl = ce_z @ (np.eye(ce_z.shape[1]) - projector), cl_z @ (np.eye(cl_z.shape[1]) - projector)
    residual_identity = identity_diagnostics(re, rl, cfg["seed"] + seed_offset + 31)
    residual_cross = (re.T @ rl + rl.T @ re) / (2.0 * max(len(re) - 1, 1))
    residual_rank = effective_rank(residual_cross)
    meta_cols = [c for c in ("meta_comments", "meta_conditions", "meta_opportunity_choice") if c in frame]
    meta = (frame.loc[frame["user_id"].isin(confirmation_users)]
            .groupby("user_id", observed=True)[meta_cols].mean().reindex(cu)) if meta_cols else pd.DataFrame(index=cu)
    rows = []
    for j in range(fit.n_factors):
        r = safe_corr(se[:, j], sl[:, j])
        lo, hi = bootstrap_r(se[:, j], sl[:, j], cfg["seed"] + seed_offset + j,
                             iterations=100 if cfg.get("quick") else 500)
        top = np.argsort(-np.abs(fit.rotated_directions[:, j]))[:6]
        rows.append({"factor_id": f"{name}_F{j + 1}", "family": name,
                     "stable_eigenvalue": float(fit.stable_eigenvalues[j]),
                     "stable_share": float(fit.stable_share[j]),
                     "confirmation_reliability": r, "reliability_ci_lo": float(lo),
                     "reliability_ci_hi": float(hi),
                     "operational_signature": "; ".join(
                         f"{feature_cols[i]} ({fit.rotated_directions[i, j]:+.3f})" for i in top),
                     **{f"corr_{col}": safe_corr((se[:, j] + sl[:, j]) / 2.0, meta[col])
                        for col in meta_cols},
                     "axis_confirmed": bool(r >= cfg["confirmation_min_reliability"] and lo >= cfg["confirmation_reliability_ci_floor"]),
                     })
    supported = (similarity >= cfg["confirmation_min_subspace_similarity"]
                 and angle <= cfg["confirmation_max_principal_angle"]
                 and factor_identity["own_vs_stranger_auc"] >= cfg["confirmation_min_own_stranger_auc"])
    summary = {"family": name, "status": "SUPPORTED_INTERNAL" if supported else "REJECTED_VALIDATION",
               "features": len(feature_cols), "n_discovery_paired": len(du),
               "n_confirmation_paired": len(cu), "n_factors": fit.n_factors,
               "subspace_similarity": similarity, "max_principal_angle_deg": angle,
               "own_vs_stranger_auc": factor_identity["own_vs_stranger_auc"],
               "factor_auc_ci_lo": factor_identity["own_vs_stranger_auc_ci_lo"],
               "factor_auc_ci_hi": factor_identity["own_vs_stranger_auc_ci_hi"],
               "factor_retrieval_top10": factor_identity["retrieval_top10"],
               "full_space_own_vs_stranger_auc": full_identity["own_vs_stranger_auc"],
               "full_space_auc_ci_lo": full_identity["own_vs_stranger_auc_ci_lo"],
               "full_space_auc_ci_hi": full_identity["own_vs_stranger_auc_ci_hi"],
               "residual_own_vs_stranger_auc": residual_identity["own_vs_stranger_auc"],
               "residual_auc_ci_lo": residual_identity["own_vs_stranger_auc_ci_lo"],
               "residual_auc_ci_hi": residual_identity["own_vs_stranger_auc_ci_hi"],
               "residual_retrieval_top10": residual_identity["retrieval_top10"],
               "residual_effective_rank": residual_rank,
               "n_axes_confirmed": int(sum(r["axis_confirmed"] for r in rows))}
    return summary, rows, fit


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    args = parse_args()
    cfg = json.loads(args.config.read_text())
    cfg["quick"] = args.quick
    if not args.input.exists():
        raise FileNotFoundError(f"Missing {args.input}; see docs/DATA_ACCESS.md or pass --input.")
    comments = pd.read_parquet(args.input, columns=["author", "body", "created_utc", "subreddit"])
    units = prepare_units(comments, cfg)
    users = sorted(units["user_id"].unique())
    discovery_users = {u for u in users if stable_user_split(u) == "discovery"}
    confirmation_users = set(users) - discovery_users
    vectorizer, svd, x = fit_representation(units, discovery_users, cfg)
    residual, supported_conditions = crossfit_residuals(units, x, discovery_users, cfg)
    z_map, z_loading = opportunity_axis(units, discovery_users, supported_conditions)
    static, hybrid, dynamic, dyn_pca = build_objects(units, residual, z_map, cfg)
    dynamic_raw = dynamic.copy()
    hybrid = conditional_residual(hybrid, [static], "hybrid::", discovery_users)
    dynamic_predictors = [static] + ([hybrid] if len(hybrid) else [])
    dynamic = conditional_residual(dynamic, dynamic_predictors, "dynamic::", discovery_users)

    family_summaries, catalog_rows, fits = [], [], {}
    for offset, (name, frame) in enumerate((("static", static), ("hybrid", hybrid), ("dynamic", dynamic))):
        summary, rows, fit = analyze_family(name, frame, discovery_users, confirmation_users, cfg, 1000 * offset)
        if name == "hybrid":
            summary["family"] = "opportunity_response"
            for row in rows:
                row["family"] = "opportunity_response"
                row["factor_id"] = row["factor_id"].replace("hybrid_F", "opportunity_response_F")
        family_summaries.append(summary)
        catalog_rows.extend(rows)
        fits[name] = fit
    shared_summary, shared_rows = analyze_shared_hybrid(
        static, dynamic_raw, discovery_users, confirmation_users, cfg
    )
    family_summaries.append(shared_summary)
    catalog_rows.extend(shared_rows)

    terms = vectorizer.get_feature_names_out()
    component_terms = []
    for j, component in enumerate(svd.components_):
        top = np.argsort(-np.abs(component))[:12]
        component_terms.append({"component": f"svd_{j + 1:02d}",
                                "top_terms": "; ".join(f"{terms[i]} ({component[i]:+.3f})" for i in top)})
    summary = {
        "run": "SUICA_V6_FACTOR_DISCOVERY_V2_RAW",
        "input_sha256": sha256_file(args.input), "n_input_comments": int(len(comments)),
        "n_sampled_comments": int(len(units)), "n_users": len(users),
        "n_discovery_users": len(discovery_users), "n_confirmation_users": len(confirmation_users),
        "n_supported_conditions": len(supported_conditions), "representation_dimensions": x.shape[1],
        "personality_labels_used": False, "old_suica_constructs_used": False,
        "families": family_summaries,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(catalog_rows).to_csv(args.output_dir / "factor_catalog.csv", index=False)
    pd.DataFrame(component_terms).to_csv(args.output_dir / "representation_component_terms.csv", index=False)
    pd.DataFrame({"surface_feature": Q_COLS, "opportunity_axis_loading": z_loading}).to_csv(
        args.output_dir / "opportunity_axis.csv", index=False)
    pd.DataFrame(family_summaries).to_csv(args.output_dir / "family_acceptance.csv", index=False)
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    catalog = pd.DataFrame(catalog_rows)
    table = catalog.to_markdown(index=False, floatfmt=".3f") if len(catalog) else "No stable axes discovered."
    family_table = pd.DataFrame(family_summaries).to_markdown(index=False, floatfmt=".3f")
    accepted_families = [row["family"] for row in family_summaries
                         if row["status"] == "SUPPORTED_INTERNAL"]
    verdict = (f"SUPPORTED-INTERNAL families: {', '.join(accepted_families)}."
               if accepted_families else
               "NO NEW FACTOR FAMILY CONFIRMED. Discovery-side axes are retained only as rejected diagnostics.")
    args.report.write_text(f"""# SUICA V6 Raw-Text Factor Discovery v2

## Design

- Real PANDORA comments: {len(comments):,} input; {len(units):,} sampled while preserving
  consecutive same-subreddit runs; {len(users):,} eligible authors.
- Discovery/confirmation authors: {len(discovery_users):,}/{len(confirmation_users):,}.
- Representation: discovery-only word/bigram TF-IDF -> {x.shape[1]} SVD coordinates.
- Shared opportunity nuisance: surface/format variables plus supported subreddit × half,
  author-cross-fitted in discovery. Opportunity response axis uses surface/format profiles
  only, never text outcomes.
- Dynamic transitions cross neither subreddit nor broken run boundaries.
- Ordered discovery: Static; Hybrid conditional on Static; Dynamic conditional on both.
- `opportunity_response` is the author x opportunity slope object. The separate
  `shared_hybrid` row tests the user's stronger meaning: one author score visible
  in both the unresidualized Static and Dynamic blocks.
- No personality labels and no frozen SUICA constructs were read.

## Family acceptance

{family_table}

## Final verdict

**{verdict}** This factor-level verdict is not a no-signal verdict. Bootstrap
intervals for full-space, factor-space, and post-factor residual identity are
reported separately. A lower confidence bound above .50 licenses only a
distributed same-author signature under this corpus and distance rule, not a
personality construct. No axis is promoted or psychologically named in this run.

## Factor catalog

{table}

## Claim boundary

`SUPPORTED_INTERNAL` means reproducible PANDORA text-behavior structure under this
opportunity model. It does not mean a personality dimension. `UNDECIDED_SAMPLE`
means the author-specific object is too thin for the registered factor-space gate;
it is not evidence of absence. External labels may only be joined after this catalog
is frozen. A rejected discrete axis also does not imply absence of distributed
author information: full-space and post-factor residual AUC/effective-rank values
are reported separately. `static-only` or `dynamic-only` is not licensed until the
other block passes an equivalence test; current wording is static-dominant or
dynamic-dominant only.
""")
    print(json.dumps(summary, indent=2))
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
