#!/usr/bin/env python
"""E3/E4: pivot exploration — choice as a scale, react at situation-class level.

E3 (choice scale): cluster subreddit conditions into ~12 content classes
(TF-IDF/SVD centroids + KMeans), then turn each user's condition-choice
distribution over classes into log-ratio axis scores. Test per-axis temporal
stability (early vs late, >= 90-day gap) and axis redundancy.
  Adoption rule (pre-committed): axes with early-late r >= 0.50 and
  |inter-axis r| <= 0.60 enter the SUICA v3 battery.

E4 (class react, CAPS-faithful): react computed ipsatively (user's own class
profile: class mean minus the user's overall mean) at class granularity, where
cells are much thicker than raw subreddits. Signature stability early vs late
over shared classes; within-half even/odd split gives a reliability estimate
and a disattenuated signature.
  Revival rule (pre-committed): observed median signature r >= 0.30 for >= 2
  constructs revives react; if only disattenuated values clear 0.30, react is
  'volume-limited, design-fixable'; otherwise it stays retired.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.suica_v2_lib import V2_CONSTRUCTS  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
TAG = "s128"
N_CLASSES = 12
EPS = 1e-4
SEED = 42
GAP_DAYS = 90


def build_condition_classes() -> tuple[pd.DataFrame, pd.DataFrame]:
    from sklearn.cluster import KMeans
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import StandardScaler
    from suica_core.suica import controlled_slice_text

    frame = pd.read_parquet(TIER_DIR / f"phase2_passB_slicetext_{TAG}.parquet")
    texts = frame["slice_text"].fillna("").map(lambda t: controlled_slice_text(t, "method_stripped"))
    vec = TfidfVectorizer(lowercase=True, strip_accents="unicode", analyzer="word", ngram_range=(1, 2),
                          max_features=22000, min_df=3, sublinear_tf=True)
    tfidf = vec.fit_transform(texts)
    dense = StandardScaler().fit_transform(TruncatedSVD(n_components=64, random_state=SEED).fit_transform(tfidf))
    conds = frame["condition"].to_numpy()
    cond_names = pd.unique(conds)
    centroids, weights = [], []
    for cond in cond_names:
        mask = conds == cond
        centroids.append(dense[mask].mean(axis=0))
        weights.append(np.sqrt(mask.sum()))
    km = KMeans(n_clusters=N_CLASSES, random_state=SEED, n_init=10)
    classes = km.fit_predict(np.asarray(centroids), sample_weight=np.asarray(weights))
    cmap = pd.DataFrame({"condition": cond_names, "class_id": classes})
    frame = frame.merge(cmap, on="condition")
    terms = np.asarray(vec.get_feature_names_out())
    overall = np.asarray(tfidf.mean(axis=0)).ravel()
    rows = []
    for k in range(N_CLASSES):
        mask = frame["class_id"].to_numpy() == k
        local = np.asarray(tfidf[mask].mean(axis=0)).ravel()
        top = np.argsort(local - overall)[-12:][::-1]
        sub_top = frame.loc[mask, "condition"].value_counts().head(6).index.tolist()
        rows.append({"class_id": k, "n_slices": int(mask.sum()),
                     "n_conditions": int(cmap.loc[cmap['class_id'].eq(k)].shape[0]),
                     "top_terms": ", ".join(terms[top]), "top_subreddits": ", ".join(map(str, sub_top))})
    return cmap, pd.DataFrame(rows)


def choice_axis_scores(cmap: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    rng = np.random.default_rng(SEED)
    c = pd.read_parquet(TIER_DIR / "tier_u_comments.parquet")
    c["author"] = c["author"].astype(str)
    c["subreddit"] = c["subreddit"].fillna("__m__").astype(str)
    class_of = dict(zip(cmap["condition"], cmap["class_id"]))
    c["class_id"] = c["subreddit"].map(class_of).fillna(N_CLASSES).astype(int)  # N_CLASSES = "other"
    K = N_CLASSES + 1
    half_rows = {}
    for u, g in c.groupby("author"):
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
        half_rows[u] = (np.bincount(e["class_id"], minlength=K) / len(e),
                        np.bincount(l["class_id"], minlength=K) / len(l))
    users = sorted(half_rows)
    E = np.array([half_rows[u][0] for u in users])
    L = np.array([half_rows[u][1] for u in users])
    pop_e, pop_l = E.mean(axis=0), L.mean(axis=0)
    SE = np.log((E + EPS) / (pop_e + EPS))
    SL = np.log((L + EPS) / (pop_l + EPS))
    ax_rows = []
    for k in range(K):
        r = float(np.corrcoef(SE[:, k], SL[:, k])[0, 1])
        ax_rows.append({"class_id": k, "axis_retest_r": r})
    S_full = (SE + SL) / 2.0
    inter = np.corrcoef(S_full.T)
    off = np.abs(inter[~np.eye(K, dtype=bool)])
    # profile AUC same-user vs random
    def cosim(a, b):
        d = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
        return np.where(d > 0, (a * b).sum(axis=1) / d, np.nan)
    same = cosim(SE, SL)
    perm = rng.permutation(len(users))
    rand = cosim(SE, SL[perm])
    auc = float((same[:, None] > np.sort(rand)[None, :]).mean())
    meta = {"n_users": len(users), "profile_auc_logratio": auc,
            "mean_abs_interaxis_r": float(off.mean()), "max_abs_interaxis_r": float(off.max())}
    scores = pd.DataFrame(S_full, columns=[f"choice_ax_{k:02d}" for k in range(K)])
    scores.insert(0, "user_id", users)
    return pd.DataFrame(ax_rows), scores, meta


def class_react(cmap: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    passa = pd.read_parquet(TIER_DIR / f"phase2_passA_scored_{TAG}.parquet")
    passa = passa.merge(cmap, on="condition", how="inner")
    rows = []
    for construct in V2_CONSTRUCTS:
        cell = passa.groupby(["user_id", "class_id", "half"], as_index=False).agg(
            m=(construct, "mean"), n=(construct, "size"))
        cell = cell.loc[cell["n"] >= 3]
        wide = cell.pivot_table(index=["user_id", "class_id"], columns="half", values="m").dropna()
        sigs, nulls, disatt = [], [], []
        # within-half even/odd reliability for disattenuation
        eo = passa.assign(par=passa["slice_index"].astype(int) % 2).groupby(
            ["user_id", "class_id", "half", "par"], as_index=False)[construct].mean()
        eo_wide = eo.pivot_table(index=["user_id", "class_id", "half"], columns="par", values=construct)
        for user, g in wide.groupby(level=0):
            if len(g) < 4:
                continue
            e = g["early"].to_numpy(float).copy(); l = g["late"].to_numpy(float).copy()
            e = e - e.mean(); l = l - l.mean()
            if np.std(e) < 1e-12 or np.std(l) < 1e-12:
                continue
            obs = float(np.corrcoef(e, l)[0, 1])
            sigs.append(obs)
            nulls.append(float(np.corrcoef(e, rng.permutation(l))[0, 1]))
            rels = []
            for half in ("early", "late"):
                try:
                    sub = eo_wide.loc[(user, slice(None), half)].dropna()
                except KeyError:
                    sub = pd.DataFrame()
                if len(sub) >= 4 and sub.shape[1] == 2:
                    a = sub[0].to_numpy(float) - sub[0].mean()
                    b = sub[1].to_numpy(float) - sub[1].mean()
                    if np.std(a) > 1e-12 and np.std(b) > 1e-12:
                        half_r = float(np.corrcoef(a, b)[0, 1])
                        rels.append(max(0.0, 2 * half_r / (1 + half_r)) if half_r > -1 else 0.0)
            if len(rels) == 2 and min(rels) > 0.05:
                disatt.append(min(1.0, obs / np.sqrt(rels[0] * rels[1])))
        rows.append({"construct": construct, "n_users": len(sigs),
                     "median_signature_r": float(np.median(sigs)) if sigs else np.nan,
                     "null_median": float(np.median(nulls)) if nulls else np.nan,
                     "n_disattenuable": len(disatt),
                     "median_disattenuated": float(np.median(disatt)) if disatt else np.nan})
    return pd.DataFrame(rows)


def main() -> None:
    out_dir = ROOT / "results" / f"suica_e3_e4_choice_class_v2_{TAG}"
    out_dir.mkdir(parents=True, exist_ok=True)
    cmap, class_table = build_condition_classes()
    cmap.to_csv(out_dir / "condition_class_map.csv", index=False)
    class_table.to_csv(out_dir / "class_table.csv", index=False)
    axes, scores, meta = choice_axis_scores(cmap)
    axes = axes.merge(class_table[["class_id", "top_terms", "top_subreddits"]], on="class_id", how="left")
    axes.to_csv(out_dir / "choice_axis_stability.csv", index=False)
    scores.to_csv(out_dir / "choice_axis_scores.csv", index=False)
    react = class_react(cmap)
    react.to_csv(out_dir / "class_react_signatures.csv", index=False)
    adopted = axes.loc[axes["axis_retest_r"] >= 0.50, "class_id"].tolist()
    criteria = {
        "choice_axes_adopted_r_ge_050": adopted,
        "n_axes_adopted": len(adopted),
        "profile_auc": meta["profile_auc_logratio"],
        "react_observed_ge_030_count": int((react["median_signature_r"] >= 0.30).sum()),
        "react_disattenuated_ge_030_count": int((react["median_disattenuated"] >= 0.30).sum()),
        **meta,
    }
    (out_dir / "e3_e4_results.json").write_text(json.dumps(criteria, indent=2, default=float) + "\n")
    report = ROOT / "reports" / f"suica_e3_e4_choice_class_v2_{TAG}.md"
    report.write_text(
        "# SUICA E3/E4 Choice Scale + Class React (exploration)\n\n## Condition classes\n\n"
        + class_table.to_markdown(index=False)
        + "\n\n## Choice axis stability (early vs late)\n\n" + axes.round(3).to_markdown(index=False)
        + "\n\n## Class-level react signatures\n\n" + react.round(3).to_markdown(index=False)
        + "\n\n```json\n" + json.dumps(criteria, indent=2, default=float) + "\n```\n"
    )
    print(class_table[["class_id", "n_slices", "top_subreddits"]].to_string(index=False))
    print("\naxes:\n", axes[["class_id", "axis_retest_r"]].round(3).to_string(index=False))
    print("\nreact:\n", react.round(3).to_string(index=False))
    print(json.dumps({k: v for k, v in criteria.items() if k != "choice_axes_adopted_r_ge_050"}, indent=2, default=float))


if __name__ == "__main__":
    main()
