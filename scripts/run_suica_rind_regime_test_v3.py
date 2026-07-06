#!/usr/bin/env python
"""Rind regime test v3 — empirical check of SUICA_RIND_THEORY_BASE_V3 predictions.

PRED-1  (PANDORA, paired): fixed-rind split-half > mixed-rind split-half,
        same users, same slice counts.
PRED-1b (cross-corpus, descriptive): Essays >= X >= PANDORA-mixed at matched
        ~8-slice budget.
PRED-2  (X): symbol-choice distribution early/late AUC >= 0.65.
PRED-3  (structure invariance): off-diagonal correlation vectors of the 23
        anchor-rate features agree across corpora (pairwise r >= 0.70).

Governance: Essays — dev half only (stable-hash split), text column only,
label columns never loaded. Frozen v3 formulas; no tuning on results.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.suica import PERSONALITY_LEAK_RE, fixed_token_slices_for_text  # noqa: E402
from scripts.suica_v2_lib import fast_anchor_rates, score_slices_v2, spearman_brown  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
X_POSTS = ROOT / "data_sets" / "x_fullmarkettext" / "memory_semis_3m_20260318_20260617_merged" / "x_posts.csv"
ESSAYS = ROOT / "data_sets" / "prepared" / "big5" / "essays_original_prepared.csv"
OUT_DIR = ROOT / "results" / "suica_rind_regime_test_v3"
REPORT = ROOT / "reports" / "suica_rind_regime_test_v3.md"
STYLE = ["first_person_usage_v2", "directive_action_v2", "tension_core_v2", "novelty_play_v2"]
SLICE_TOKENS = 128
BUDGET = 8  # slices per half-pair budget (~1024 tokens)
SEED = 42


def stable_fraction(value: str) -> float:
    return int(hashlib.sha1(str(value).encode()).hexdigest()[:12], 16) / float(16**12 - 1)


def slices_from_texts(user_id: str, texts: list[str], *, max_slices: int = 64) -> list[dict]:
    rows = []
    text = "\n".join(texts)
    for row in fixed_token_slices_for_text(text, slice_tokens=SLICE_TOKENS, stride=SLICE_TOKENS,
                                           min_slice_tokens=24, max_slices=max_slices):
        if PERSONALITY_LEAK_RE.search(row["slice_text"]):
            continue
        rows.append({"user_id": user_id, "slice_index": row["slice_index"],
                     "token_count": row["token_count"], "slice_text": row["slice_text"]})
    return rows


def split_half_r(scored: pd.DataFrame, construct: str, *, k: int = BUDGET) -> tuple[float, int]:
    """Even/odd split-half over the first 2k slices per user."""
    vals = []
    for user, g in scored.groupby("user_id"):
        g = g.sort_values("slice_index").head(2 * k)
        if len(g) < 2 * k:
            continue
        v = g[construct].to_numpy(float)
        vals.append((v[0::2].mean(), v[1::2].mean()))
    if len(vals) < 50:
        return float("nan"), len(vals)
    arr = np.asarray(vals)
    return float(np.corrcoef(arr[:, 0], arr[:, 1])[0, 1]), len(vals)


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results: dict = {}

    # ---------- PRED-1: paired fixed-rind vs mixed-rind (PANDORA) ----------
    comments = pd.read_parquet(TIER_DIR / "tier_u_comments.parquet")
    comments["author"] = comments["author"].astype(str)
    comments["subreddit"] = comments["subreddit"].fillna("__m__").astype(str)
    comments = comments.sort_values(["author", "created_utc"])
    paired_rows = []
    per_user_pairs = []
    for user, g in comments.groupby("author"):
        counts = g["subreddit"].value_counts()
        top = counts.index[0]
        g_top = g.loc[g["subreddit"].eq(top)]
        others = g.loc[~g["subreddit"].eq(top)]
        n_other_subs = others["subreddit"].nunique()
        if len(g_top) < 20 or len(others) < 20 or n_other_subs < 4:
            continue
        fixed_slices = slices_from_texts(user, g_top["body"].astype(str).tolist(), max_slices=2 * BUDGET)
        # mixed: interleave subreddits round-robin to maximize rind mixing
        mixed_texts = []
        buckets = [sub_g["body"].astype(str).tolist() for _, sub_g in others.groupby("subreddit")]
        idx = 0
        while len(mixed_texts) < 60 and any(buckets):
            b = buckets[idx % len(buckets)]
            if b:
                mixed_texts.append(b.pop(0))
            idx += 1
            buckets = [b for b in buckets if b]
        mixed_slices = slices_from_texts(user, mixed_texts, max_slices=2 * BUDGET)
        if len(fixed_slices) >= 2 * BUDGET and len(mixed_slices) >= 2 * BUDGET:
            per_user_pairs.append((user, fixed_slices, mixed_slices))
    print(f"PRED-1 eligible users: {len(per_user_pairs)}")
    fixed_frame = pd.DataFrame([s for _, f, _ in per_user_pairs for s in f])
    mixed_frame = pd.DataFrame([s for _, _, m in per_user_pairs for s in m])
    fixed_scored = score_slices_v2(fixed_frame)
    mixed_scored = score_slices_v2(mixed_frame)
    users_arr = np.array([u for u, _, _ in per_user_pairs])

    def halves(scored: pd.DataFrame, construct: str) -> pd.DataFrame:
        rows = {}
        for user, g in scored.groupby("user_id"):
            v = g.sort_values("slice_index").head(2 * BUDGET)[construct].to_numpy(float)
            if len(v) == 2 * BUDGET:
                rows[user] = (v[0::2].mean(), v[1::2].mean())
        return pd.DataFrame(rows, index=["a", "b"]).T

    pred1_rows = []
    for construct in STYLE:
        hf = halves(fixed_scored, construct)
        hm = halves(mixed_scored, construct)
        joined = hf.join(hm, lsuffix="_f", rsuffix="_m").dropna()
        rf = float(np.corrcoef(joined["a_f"], joined["b_f"])[0, 1])
        rm = float(np.corrcoef(joined["a_m"], joined["b_m"])[0, 1])
        n = len(joined)
        deltas = np.empty(600)
        ids = np.arange(n)
        for i in range(600):
            t = rng.choice(ids, size=n, replace=True)
            deltas[i] = (np.corrcoef(joined["a_f"].to_numpy()[t], joined["b_f"].to_numpy()[t])[0, 1]
                         - np.corrcoef(joined["a_m"].to_numpy()[t], joined["b_m"].to_numpy()[t])[0, 1])
        lo, hi = np.percentile(deltas, [2.5, 97.5])
        pred1_rows.append({"construct": construct, "n_users": n, "r_fixed_rind": rf, "r_mixed_rind": rm,
                           "delta": rf - rm, "ci_lo": float(lo), "ci_hi": float(hi)})
    pred1 = pd.DataFrame(pred1_rows)
    results["PRED1_pass_count"] = int((pred1["ci_lo"] > 0).sum())
    results["PRED1_verdict"] = "pass" if (pred1["ci_lo"] > 0).sum() >= 3 else (
        "fail" if (pred1["ci_hi"] < 0).sum() >= 3 else "inconclusive")

    # ---------- Essays (dev half only, text column only) ----------
    essays = pd.read_csv(ESSAYS, usecols=["user_id", "text"], dtype={"user_id": str})
    essays["h"] = essays["user_id"].map(stable_fraction)
    dev = essays.loc[essays["h"] < 0.5]
    pd.DataFrame({"user_id": sorted(dev["user_id"])}).to_csv(TIER_DIR / "essays_regime_dev_half.csv", index=False)
    ess_slices = pd.DataFrame([s for _, row in dev.iterrows()
                               for s in slices_from_texts(row["user_id"], [str(row["text"])], max_slices=2 * BUDGET)])
    ess_scored = score_slices_v2(ess_slices)

    # ---------- X (domain-fixed) ----------
    x = pd.read_csv(X_POSTS)
    x = x.loc[x["lang"].astype(str).eq("en")].copy()
    x["user_id"] = x["account_id"].astype(str)
    x["timestamp"] = pd.to_datetime(x["timestamp"], errors="coerce", utc=True)
    x["text"] = x["text"].fillna("").astype(str)
    x = x.loc[x["timestamp"].notna() & x["text"].str.len().gt(0)]
    x["norm"] = x["text"].str.lower().str.replace(r"https?://\S+", " ", regex=True).str.replace(r"\s+", " ", regex=True)
    x = x.drop_duplicates(["user_id", "norm"]).sort_values(["user_id", "timestamp"])
    x_slices = pd.DataFrame([s for user, g in x.groupby("user_id")
                             for s in slices_from_texts(user, g["text"].tolist(), max_slices=2 * BUDGET)])
    x_scored = score_slices_v2(x_slices)

    pred1b_rows = []
    for construct in STYLE:
        for corpus, scored in [("essays_fixed_prompt", ess_scored), ("x_domain_fixed", x_scored),
                               ("pandora_mixed", mixed_scored), ("pandora_top_subreddit", fixed_scored)]:
            r, n = split_half_r(scored, construct, k=3)
            pred1b_rows.append({"corpus": corpus, "construct": construct, "split_half_r": r,
                                "sb_full": spearman_brown(r) if np.isfinite(r) else np.nan, "n_users": n})
    pred1b = pd.DataFrame(pred1b_rows)

    # ---------- PRED-2: X micro-choice (symbol distribution) ----------
    sym = x.dropna(subset=["symbol"]).copy()
    sym["symbol"] = sym["symbol"].astype(str)
    top_syms = sym["symbol"].value_counts().head(60).index
    sym = sym.loc[sym["symbol"].isin(top_syms)]
    pairs = {}
    for user, g in sym.groupby("user_id"):
        if len(g) < 20:
            continue
        t = g["timestamp"].astype("int64").to_numpy(float)
        t40, t60 = np.quantile(t, [0.4, 0.6])
        e = g.loc[g["timestamp"].astype("int64") <= t40, "symbol"].value_counts()
        l = g.loc[g["timestamp"].astype("int64") >= t60, "symbol"].value_counts()
        if e.sum() < 8 or l.sum() < 8:
            continue
        pairs[user] = (e, l)
    spos = {s: i for i, s in enumerate(top_syms)}

    def svec(counts: pd.Series) -> np.ndarray:
        v = np.zeros(len(top_syms))
        for s, n in counts.items():
            v[spos[s]] = n
        return v / max(1, v.sum())

    users_x = sorted(pairs)
    E = np.array([svec(pairs[u][0]) for u in users_x])
    L = np.array([svec(pairs[u][1]) for u in users_x])

    def cosim(a, b):
        d = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
        return np.where(d > 0, (a * b).sum(axis=1) / d, np.nan)

    same = cosim(E, L)
    rand = cosim(E, L[rng.permutation(len(users_x))])
    auc = float((same[:, None] > np.sort(rand)[None, :]).mean()) if len(users_x) else float("nan")
    results["PRED2"] = {"n_users": len(users_x), "same_median_cos": float(np.nanmedian(same)) if len(users_x) else None,
                        "random_median_cos": float(np.nanmedian(rand)) if len(users_x) else None,
                        "symbol_choice_auc": auc, "verdict": "pass" if auc >= 0.65 else "fail"}

    # ---------- PRED-3: structure invariance over 23 anchor-rate features ----------
    def user_rate_matrix(scored: pd.DataFrame) -> pd.DataFrame:
        rate_cols = [c for c in scored.columns if c.endswith("_rate") and c != "token_count_anchor"]
        return scored.groupby("user_id")[rate_cols].mean()

    mats = {"pandora": user_rate_matrix(pd.concat([fixed_scored, mixed_scored])),
            "essays": user_rate_matrix(ess_scored), "x_market": user_rate_matrix(x_scored)}
    offdiags = {}
    for name, m in mats.items():
        c = m.corr().to_numpy()
        offdiags[name] = c[np.triu_indices_from(c, k=1)]
    pred3 = {}
    for a, b in [("pandora", "essays"), ("pandora", "x_market"), ("essays", "x_market")]:
        mask = np.isfinite(offdiags[a]) & np.isfinite(offdiags[b])
        pred3[f"{a}_vs_{b}"] = float(np.corrcoef(offdiags[a][mask], offdiags[b][mask])[0, 1])
    results["PRED3"] = {**pred3, "verdict": "pass" if all(v >= 0.70 for v in pred3.values()) else (
        "fail" if any(v < 0.5 for v in pred3.values()) else "partial")}

    pred1.to_csv(OUT_DIR / "pred1_paired_rind.csv", index=False)
    pred1b.to_csv(OUT_DIR / "pred1b_cross_corpus.csv", index=False)
    (OUT_DIR / "rind_regime_results.json").write_text(json.dumps(results, indent=2, default=float) + "\n")
    REPORT.write_text(
        "# SUICA Rind Regime Test v3\n\n## PRED-1 paired fixed vs mixed rind (PANDORA, same users)\n\n"
        + pred1.round(4).to_markdown(index=False)
        + "\n\n## PRED-1b cross-corpus split-half at matched budget\n\n"
        + pred1b.pivot(index="construct", columns="corpus", values="split_half_r").round(3).to_markdown()
        + "\n\n## PRED-2 / PRED-3\n\n```json\n" + json.dumps(results, indent=2, default=float) + "\n```\n"
    )
    print(pred1.round(4).to_string(index=False))
    print("\ncross-corpus split-half:\n",
          pred1b.pivot(index="construct", columns="corpus", values="split_half_r").round(3).to_string())
    print("\n", json.dumps(results, indent=2, default=float))


if __name__ == "__main__":
    main()
