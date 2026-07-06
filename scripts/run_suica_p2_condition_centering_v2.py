#!/usr/bin/env python
"""P2: does condition-fixed deviation add measurement value? (plan v2)

Design: each user's qualifying subreddit conditions are split into two
disjoint sets A/B. Base scores are computed from A and from B, either with
LOO condition centering (SUICA mechanism) or raw (no centering). If the
condition-fixed-deviation idea is right, centered cross-set stability should
beat raw stability, because centering removes condition-composition effects.

P2a: frozen v2 lexicon constructs. P2b: node-occupancy scores (MCD-style,
TF-IDF/SVD/KMeans regions discovered label-free on the same slices).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.suica_v2_lib import V2_CONSTRUCTS, loo_condition_center  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
EPS = 1e-4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="s128")
    parser.add_argument("--min-conditions", type=int, default=4)
    parser.add_argument("--min-slices-per-condition", type=int, default=3)
    parser.add_argument("--min-users-per-condition", type=int, default=3)
    parser.add_argument("--n-boot", type=int, default=1000)
    parser.add_argument("--n-boot-nodes", type=int, default=500)
    parser.add_argument("--kmeans-k", type=int, default=24)
    parser.add_argument("--svd-dims", type=int, default=64)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-p2b", action="store_true")
    return parser.parse_args()


def assign_condition_sets(frame: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    counts = frame.groupby(["user_id", "condition"]).size().rename("n").reset_index()
    counts = counts.loc[counts["n"] >= args.min_slices_per_condition]
    keep_users = counts.groupby("user_id").size()
    keep_users = set(keep_users.loc[keep_users >= args.min_conditions].index)
    counts = counts.loc[counts["user_id"].isin(keep_users)].copy()
    counts["rank"] = counts.sort_values(["user_id", "n", "condition"], ascending=[True, False, True]).groupby("user_id").cumcount()
    counts["cset"] = np.where(counts["rank"] % 2 == 0, "A", "B")
    return counts[["user_id", "condition", "cset"]]


def paired_bases(work: pd.DataFrame, value_col: str, *, centered: bool) -> pd.DataFrame:
    sub = work.copy()
    col = value_col
    if centered:
        sub["_v"] = loo_condition_center(sub, value_col, group_cols=("condition",))
        col = "_v"
    cell = sub.groupby(["user_id", "cset", "condition"], as_index=False)[col].mean()
    base = cell.groupby(["user_id", "cset"])[col].mean().unstack("cset")
    return base.dropna()


def corr_cols(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Column-wise Pearson r for matched matrices (users x nodes)."""
    az = a - a.mean(axis=0)
    bz = b - b.mean(axis=0)
    denom = np.sqrt((az**2).sum(axis=0) * (bz**2).sum(axis=0))
    denom[denom < 1e-12] = np.nan
    return (az * bz).sum(axis=0) / denom


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(args.seed)
    frame = pd.read_parquet(TIER_DIR / f"phase2_passB_scored_{args.tag}.parquet")
    users_per_cond = frame.groupby("condition")["user_id"].nunique()
    frame = frame.loc[frame["condition"].map(users_per_cond).ge(args.min_users_per_condition)]
    sets = assign_condition_sets(frame, args)
    work = frame.merge(sets, on=["user_id", "condition"])
    users = sorted(work["user_id"].unique())
    print(f"P2 eligible users: {len(users)}; slices: {len(work)}")

    # ---------- P2a: lexicon constructs ----------
    rows = []
    boot_store: dict[str, np.ndarray] = {}
    for construct in V2_CONSTRUCTS:
        cent = paired_bases(work, construct, centered=True)
        raw = paired_bases(work, construct, centered=False)
        joined = cent.join(raw, lsuffix="_c", rsuffix="_r").dropna()
        ac, bc = joined["A_c"].to_numpy(float), joined["B_c"].to_numpy(float)
        ar, br = joined["A_r"].to_numpy(float), joined["B_r"].to_numpy(float)
        r_c = float(np.corrcoef(ac, bc)[0, 1])
        r_r = float(np.corrcoef(ar, br)[0, 1])
        idx = np.arange(len(joined))
        deltas = np.empty(args.n_boot)
        for i in range(args.n_boot):
            take = rng.choice(idx, size=len(idx), replace=True)
            deltas[i] = np.corrcoef(ac[take], bc[take])[0, 1] - np.corrcoef(ar[take], br[take])[0, 1]
        boot_store[construct] = deltas
        lo, hi = np.percentile(deltas, [2.5, 97.5])
        rows.append({"construct": construct, "n_users": int(len(joined)), "r_centered": r_c, "r_raw": r_r,
                     "delta": r_c - r_r, "delta_ci_lo": float(lo), "delta_ci_hi": float(hi)})
    p2a = pd.DataFrame(rows)
    pooled = np.mean(np.column_stack([boot_store[c] for c in V2_CONSTRUCTS]), axis=1)
    pooled_point = float(p2a["delta"].mean())
    pooled_lo, pooled_hi = np.percentile(pooled, [2.5, 97.5])

    # ---------- P2b: node-occupancy scores ----------
    p2b_summary: dict[str, float] = {}
    if not args.skip_p2b:
        from sklearn.cluster import MiniBatchKMeans
        from sklearn.decomposition import TruncatedSVD
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.preprocessing import StandardScaler
        from suica_core.suica import controlled_slice_text

        texts_frame = pd.read_parquet(TIER_DIR / f"phase2_passB_slicetext_{args.tag}.parquet")
        texts_frame = texts_frame.merge(sets, on=["user_id", "condition"])
        texts = texts_frame["slice_text"].fillna("").map(lambda t: controlled_slice_text(t, "method_stripped"))
        vec = TfidfVectorizer(lowercase=True, strip_accents="unicode", analyzer="word", ngram_range=(1, 2),
                              max_features=22000, min_df=3, sublinear_tf=True)
        tfidf = vec.fit_transform(texts)
        svd = TruncatedSVD(n_components=args.svd_dims, random_state=args.seed)
        dense = StandardScaler().fit_transform(svd.fit_transform(tfidf))
        km = MiniBatchKMeans(n_clusters=args.kmeans_k, random_state=args.seed, batch_size=4096, n_init=5, max_iter=120)
        labels = km.fit_predict(dense)
        texts_frame = texts_frame.reset_index(drop=True)
        texts_frame["node"] = labels
        K = args.kmeans_k

        def occupancy(sub: pd.DataFrame) -> np.ndarray:
            counts = np.bincount(sub["node"].to_numpy(int), minlength=K).astype(float)
            return counts / max(1.0, counts.sum())

        pop_global = occupancy(texts_frame)
        pop_by_cond = {c: occupancy(g) for c, g in texts_frame.groupby("condition")}
        users_b = sorted(texts_frame["user_id"].unique())
        raw_mats = {"A": np.full((len(users_b), K), np.nan), "B": np.full((len(users_b), K), np.nan)}
        cent_mats = {"A": np.full((len(users_b), K), np.nan), "B": np.full((len(users_b), K), np.nan)}
        upos = {u: i for i, u in enumerate(users_b)}
        for (user, cset), sub in texts_frame.groupby(["user_id", "cset"]):
            i = upos[user]
            p_u = occupancy(sub)
            raw_mats[cset][i] = np.log((p_u + EPS) / (pop_global + EPS))
            cond_scores = []
            for cond, csub in sub.groupby("condition"):
                p_uc = occupancy(csub)
                cond_scores.append(np.log((p_uc + EPS) / (pop_by_cond[cond] + EPS)))
            cent_mats[cset][i] = np.mean(cond_scores, axis=0)
        ok = ~(np.isnan(raw_mats["A"]).any(axis=1) | np.isnan(raw_mats["B"]).any(axis=1)
               | np.isnan(cent_mats["A"]).any(axis=1) | np.isnan(cent_mats["B"]).any(axis=1))
        ra, rb = raw_mats["A"][ok], raw_mats["B"][ok]
        ca, cb = cent_mats["A"][ok], cent_mats["B"][ok]
        r_raw_nodes = corr_cols(ra, rb)
        r_cent_nodes = corr_cols(ca, cb)
        point_raw = float(np.nanmean(r_raw_nodes))
        point_cent = float(np.nanmean(r_cent_nodes))
        n_ok = int(ok.sum())
        deltas_b = np.empty(args.n_boot_nodes)
        idx = np.arange(n_ok)
        for i in range(args.n_boot_nodes):
            take = rng.choice(idx, size=n_ok, replace=True)
            deltas_b[i] = np.nanmean(corr_cols(ca[take], cb[take])) - np.nanmean(corr_cols(ra[take], rb[take]))
        blo, bhi = np.percentile(deltas_b, [2.5, 97.5])
        p2b_summary = {"n_users": n_ok, "mean_node_r_centered": point_cent, "mean_node_r_raw": point_raw,
                       "delta": point_cent - point_raw, "delta_ci_lo": float(blo), "delta_ci_hi": float(bhi)}

    out_dir = ROOT / "results" / f"suica_p2_condition_centering_v2_{args.tag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    p2a.to_csv(out_dir / "p2a_constructs.csv", index=False)
    criteria = {
        "p2a_pooled_delta": pooled_point,
        "p2a_pooled_ci": [float(pooled_lo), float(pooled_hi)],
        "P2a_verdict": "pass" if pooled_lo > 0 else ("fail" if pooled_hi < 0 else "inconclusive_or_neutral"),
        "p2b": p2b_summary,
        "P2b_verdict": (
            "pass" if p2b_summary and p2b_summary["delta_ci_lo"] > 0
            else ("fail" if p2b_summary and p2b_summary["delta_ci_hi"] < 0 else "inconclusive_or_neutral")
        ) if p2b_summary else "not_run",
    }
    (out_dir / "p2_results.json").write_text(json.dumps({"criteria": criteria, "p2a_rows": p2a.to_dict("records")}, indent=2) + "\n")
    report = ROOT / "reports" / f"suica_p2_condition_centering_v2_{args.tag}.md"
    report.write_text(
        "# SUICA P2 Condition-Centering Value (v2)\n\n## P2a lexicon constructs\n\n"
        + p2a.round(4).to_markdown(index=False)
        + f"\n\npooled delta = {pooled_point:.4f}, CI [{pooled_lo:.4f}, {pooled_hi:.4f}]\n\n## P2b node occupancy\n\n"
        + json.dumps(p2b_summary, indent=2)
        + "\n\n```json\n" + json.dumps(criteria, indent=2) + "\n```\n"
    )
    print(p2a.round(4).to_string(index=False))
    print(json.dumps(criteria, indent=2))


if __name__ == "__main__":
    main()
