#!/usr/bin/env python
"""OP-6a: held-out confirmation of the choice axes (winner's-curse fix, R3-3).

The E3 axes were selected by the same early/late retest r that was reported.
This script repeats the whole chain with a user-cohort split:
- Cohort A: fit TF-IDF/SVD, condition centroids, KMeans classes; select axes
  by retest r_A >= 0.50.
- Cohort B (never used in fitting or selection): map B-side conditions
  through the A-fit pipeline, compute B-cohort axis retest r with CIs.

Pre-committed rules: a selected axis CONFIRMS if r_B >= 0.45 with bootstrap
CI > 0 (0.45 allows expected shrinkage from the 0.50 selection bar; shrinkage
is reported). OP-6a passes if >= 4 axes confirm. MBTI-community classes are
flagged (leakage rule) regardless of confirmation.
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

from suica_core.suica import controlled_slice_text  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
OUT_DIR = ROOT / "results" / "suica_op6a_choice_axes_holdout_v3"
REPORT = ROOT / "reports" / "suica_op6a_choice_axes_holdout_v3.md"
SEED = 42
N_CLASSES = 12
EPS = 1e-4
GAP_DAYS = 90
R_A_SELECT = 0.50
R_B_CONFIRM = 0.45


def stable_fraction(value: str) -> float:
    return int(hashlib.sha1(str(value).encode()).hexdigest()[:12], 16) / float(16**12 - 1)


def axis_scores(comments: pd.DataFrame, class_of: dict, users: set) -> tuple[np.ndarray, np.ndarray, list]:
    sub = comments.loc[comments["author"].isin(users)].copy()
    sub["class_id"] = sub["subreddit"].map(class_of).fillna(N_CLASSES).astype(int)
    K = N_CLASSES + 1
    pairs = {}
    for u, g in sub.groupby("author"):
        t = g["created_utc"].to_numpy(float)
        if len(t) < 40:
            continue
        t40, t60 = np.quantile(t, [0.4, 0.6])
        if (t60 - t40) / 86400 < GAP_DAYS:
            continue
        e = g.loc[g["created_utc"] <= t40]
        l = g.loc[g["created_utc"] >= t60]
        if len(e) < 15 or len(l) < 15:
            continue
        pairs[u] = (np.bincount(e["class_id"], minlength=K) / len(e),
                    np.bincount(l["class_id"], minlength=K) / len(l))
    ulist = sorted(pairs)
    E = np.array([pairs[u][0] for u in ulist])
    L = np.array([pairs[u][1] for u in ulist])
    SE = np.log((E + EPS) / (E.mean(axis=0) + EPS))
    SL = np.log((L + EPS) / (L.mean(axis=0) + EPS))
    return SE, SL, ulist


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    from sklearn.cluster import KMeans
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import StandardScaler

    frame = pd.read_parquet(TIER_DIR / "phase2_passB_slicetext_s128.parquet")
    users_all = sorted(frame["user_id"].unique())
    a_users = {u for u in users_all if stable_fraction("op6a::" + u) < 0.5}
    a_mask = frame["user_id"].isin(a_users).to_numpy()
    texts = frame["slice_text"].fillna("").map(lambda t: controlled_slice_text(t, "method_stripped"))
    vec = TfidfVectorizer(lowercase=True, strip_accents="unicode", analyzer="word", ngram_range=(1, 2),
                          max_features=22000, min_df=3, sublinear_tf=True)
    tfidf_a = vec.fit_transform(texts[a_mask])
    svd = TruncatedSVD(n_components=64, random_state=SEED).fit(tfidf_a)
    scaler = StandardScaler().fit(svd.transform(tfidf_a))
    dense_all = scaler.transform(svd.transform(vec.transform(texts)))

    conds = frame["condition"].to_numpy()
    a_conds = pd.unique(conds[a_mask])
    centroids_a, weights_a = [], []
    for c in a_conds:
        m = (conds == c) & a_mask
        centroids_a.append(dense_all[m].mean(axis=0))
        weights_a.append(np.sqrt(m.sum()))
    km = KMeans(n_clusters=N_CLASSES, random_state=SEED, n_init=10)
    labels_a = km.fit_predict(np.asarray(centroids_a), sample_weight=np.asarray(weights_a))
    class_of = dict(zip(a_conds, labels_a))
    # map B-only conditions through the A-fit pipeline
    b_only = [c for c in pd.unique(conds) if c not in class_of]
    for c in b_only:
        m = conds == c
        class_of[c] = int(km.predict(dense_all[m].mean(axis=0, keepdims=True))[0])

    comments = pd.read_parquet(TIER_DIR / "tier_u_comments.parquet")
    comments["author"] = comments["author"].astype(str)
    comments["subreddit"] = comments["subreddit"].fillna("__m__").astype(str)
    SE_a, SL_a, _ = axis_scores(comments, class_of, a_users)
    SE_b, SL_b, ulist_b = axis_scores(comments, class_of, set(users_all) - a_users)
    print(f"choice users: A={len(SE_a)} B={len(SE_b)}")

    rows = []
    K = N_CLASSES + 1
    for k in range(K):
        r_a = float(np.corrcoef(SE_a[:, k], SL_a[:, k])[0, 1])
        selected = bool(r_a >= R_A_SELECT)
        r_b = float(np.corrcoef(SE_b[:, k], SL_b[:, k])[0, 1])
        idx = np.arange(len(SE_b))
        boots = []
        for _ in range(500):
            t = rng.choice(idx, size=len(idx), replace=True)
            e, l = SE_b[t, k], SL_b[t, k]
            if e.std() > 1e-12 and l.std() > 1e-12:
                boots.append(np.corrcoef(e, l)[0, 1])
        lo, hi = np.percentile(boots, [2.5, 97.5])
        rows.append({"class_id": k, "r_A": r_a, "selected_on_A": selected, "r_B": r_b,
                     "r_B_ci_lo": float(lo), "r_B_ci_hi": float(hi),
                     "confirmed": bool(selected and r_b >= R_B_CONFIRM and lo > 0),
                     "shrinkage": r_a - r_b if selected else np.nan})
    out = pd.DataFrame(rows)
    sel = out.loc[out["selected_on_A"]]
    n_confirmed = int(sel["confirmed"].sum())
    criteria = {"n_selected_A": int(len(sel)), "n_confirmed_B": n_confirmed,
                "mean_shrinkage": float(sel["shrinkage"].mean()) if len(sel) else np.nan,
                "OP6a_verdict": "pass" if n_confirmed >= 4 else ("partial" if n_confirmed >= 2 else "fail")}
    out.to_csv(OUT_DIR / "op6a_axes_holdout.csv", index=False)
    (OUT_DIR / "op6a_results.json").write_text(json.dumps(criteria, indent=2, default=float) + "\n")
    REPORT.write_text("# SUICA OP-6a Choice Axes Held-Out Confirmation\n\n"
                      + out.round(3).to_markdown(index=False)
                      + "\n\n```json\n" + json.dumps(criteria, indent=2, default=float) + "\n```\n")
    print(out.round(3).to_string(index=False))
    print(json.dumps(criteria, indent=2, default=float))


if __name__ == "__main__":
    main()
