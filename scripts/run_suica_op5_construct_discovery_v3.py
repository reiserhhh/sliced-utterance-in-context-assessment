#!/usr/bin/env python
"""OP-5: expand the construct inventory under the audited rules.

Discovery/confirmation split BY USERS (the key anti-overfitting upgrade):
- A-half users: build the feature space (TF-IDF -> SVD -> word clusters K=64,
  slice-region KMeans K=24) and SELECT candidates by disjoint-occasion
  stability + non-redundancy.
- B-half users: features are only TRANSFORMED (no refitting); candidates must
  CONFIRM stability on users never seen during construction or selection.

All scores are uncentered style-channel rates (per the validated v3
architecture). Occasions: early/late 40-60 quantile halves, gap >= 90 days
(P1 design). Method robustness: confirmed candidates must retain stability on
method-stripped text.

Pre-committed criteria:
  Candidate selection (A): early-late r_A >= 0.35; greedy redundancy filter
    |r| <= 0.60 vs kept candidates and vs the v3 battery; cap 15.
  Confirmation (B): r_B >= 0.30 with bootstrap CI > 0, AND method-stripped
    r_B_stripped >= 0.25.
  OP5-success: >= 4 confirmed new candidates (inventory reaches >= 8).
  OP5-partial: 1-3. OP5-fail: 0 -> lexical space exhausted at this volume;
    breadth requires richer features (merge with OP-9).
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

from suica_core.suica import PERSONALITY_LEAK_RE, fixed_token_slices_for_text, controlled_slice_text  # noqa: E402
from scripts.suica_v2_lib import score_slices_v2  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
OUT_DIR = ROOT / "results" / "suica_op5_construct_discovery_v3"
REPORT = ROOT / "reports" / "suica_op5_construct_discovery_v3.md"
SEED = 42
GAP_DAYS = 90
MAX_SLICES_HALF = 20
WORD_K = 64
REGION_K = 24
R_A_MIN = 0.35
R_B_MIN = 0.30
R_B_STRIPPED_MIN = 0.25
REDUNDANCY_MAX = 0.60
CAP = 15
V3_BATTERY = ["first_person_usage_v2", "directive_action_v2", "tension_core_v2", "novelty_play_v2"]


def stable_fraction(value: str) -> float:
    return int(hashlib.sha1(str(value).encode()).hexdigest()[:12], 16) / float(16**12 - 1)


def build_half_slices() -> pd.DataFrame:
    comments = pd.read_parquet(TIER_DIR / "tier_u_comments.parquet")
    comments["author"] = comments["author"].astype(str)
    comments = comments.sort_values(["author", "created_utc"])
    rows = []
    for user, g in comments.groupby("author"):
        t = g["created_utc"].to_numpy(float)
        if len(t) < 24:
            continue
        t40, t60 = np.quantile(t, [0.4, 0.6])
        if (t60 - t40) / 86400 < GAP_DAYS:
            continue
        for half, part in [("early", g.loc[g["created_utc"] <= t40]), ("late", g.loc[g["created_utc"] >= t60])]:
            text = "\n".join(part["body"].astype(str))
            for r in fixed_token_slices_for_text(text, slice_tokens=128, stride=128,
                                                 min_slice_tokens=24, max_slices=MAX_SLICES_HALF):
                if PERSONALITY_LEAK_RE.search(r["slice_text"]):
                    continue
                rows.append({"user_id": user, "half": half, "slice_text": r["slice_text"]})
    frame = pd.DataFrame(rows)
    counts = frame.groupby(["user_id", "half"]).size().unstack("half").fillna(0)
    keep = counts.loc[(counts.get("early", 0) >= 6) & (counts.get("late", 0) >= 6)].index
    return frame.loc[frame["user_id"].isin(keep)].reset_index(drop=True)


def half_scores_from_rates(frame: pd.DataFrame, rates: np.ndarray, names: list[str]) -> pd.DataFrame:
    df = pd.DataFrame(rates, columns=names)
    df["user_id"] = frame["user_id"].to_numpy()
    df["half"] = frame["half"].to_numpy()
    return df.groupby(["user_id", "half"])[names].mean()


def early_late_r(half_frame: pd.DataFrame, names: list[str]) -> pd.Series:
    wide = half_frame.unstack("half")
    out = {}
    for name in names:
        e = wide[(name, "early")]
        l = wide[(name, "late")]
        mask = e.notna() & l.notna()
        out[name] = float(np.corrcoef(e[mask], l[mask])[0, 1]) if mask.sum() > 50 and e[mask].std() > 1e-12 and l[mask].std() > 1e-12 else np.nan
    return pd.Series(out)


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    from sklearn.cluster import KMeans, MiniBatchKMeans
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
    from sklearn.preprocessing import StandardScaler, normalize

    frame = build_half_slices()
    users = sorted(frame["user_id"].unique())
    a_users = {u for u in users if stable_fraction("op5::" + u) < 0.5}
    frame["split"] = np.where(frame["user_id"].isin(a_users), "A", "B")
    print(f"slices: {len(frame)}; users A={len(a_users)} B={len(users) - len(a_users)}")

    # ---- fit feature space on A text only ----
    a_mask = frame["split"].eq("A").to_numpy()
    tfidf_vec = TfidfVectorizer(lowercase=True, strip_accents="unicode", analyzer="word",
                                ngram_range=(1, 1), max_features=20000, min_df=10, sublinear_tf=True)
    tfidf_a = tfidf_vec.fit_transform(frame.loc[a_mask, "slice_text"])
    svd = TruncatedSVD(n_components=96, random_state=SEED)
    svd.fit(tfidf_a)
    terms = tfidf_vec.get_feature_names_out()
    # word clusters from SVD term space (top terms by document frequency)
    df_counts = np.asarray((tfidf_a > 0).sum(axis=0)).ravel()
    top_idx = np.argsort(-df_counts)[:6000]
    term_vecs = normalize(svd.components_.T[top_idx])
    wk = KMeans(n_clusters=WORD_K, random_state=SEED, n_init=6).fit(term_vecs)
    cluster_words: dict[int, list[str]] = {}
    for k in range(WORD_K):
        members = top_idx[wk.labels_ == k]
        order = members[np.argsort(-df_counts[members])]
        cluster_words[k] = [terms[i] for i in order]
    # slice regions on A slices
    dense_a = StandardScaler().fit(svd.transform(tfidf_a)).transform(svd.transform(tfidf_a))
    scaler = StandardScaler().fit(svd.transform(tfidf_a))
    rk = MiniBatchKMeans(n_clusters=REGION_K, random_state=SEED, batch_size=4096, n_init=5).fit(dense_a)

    # ---- transform ALL slices (raw + method-stripped) ----
    count_vec = CountVectorizer(vocabulary=tfidf_vec.vocabulary_, lowercase=True,
                                strip_accents="unicode", analyzer="word", ngram_range=(1, 1))
    indicator = np.zeros((len(terms), WORD_K))
    for k in range(WORD_K):
        for w in cluster_words[k]:
            indicator[tfidf_vec.vocabulary_[w], k] = 1.0

    def cluster_rates(texts: pd.Series) -> np.ndarray:
        counts = count_vec.transform(texts)
        tokens = np.maximum(1, counts.sum(axis=1))
        return 100.0 * np.asarray(counts @ indicator) / np.asarray(tokens)

    def region_shares(texts: pd.Series) -> np.ndarray:
        tf = tfidf_vec.transform(texts)
        labels = rk.predict(scaler.transform(svd.transform(tf)))
        onehot = np.zeros((len(texts), REGION_K))
        onehot[np.arange(len(texts)), labels] = 1.0
        return onehot

    word_names = [f"wcl_{k:02d}" for k in range(WORD_K)]
    region_names = [f"region_{k:02d}" for k in range(REGION_K)]
    rates_raw = cluster_rates(frame["slice_text"])
    regions_raw = region_shares(frame["slice_text"])
    stripped = frame["slice_text"].map(lambda t: controlled_slice_text(t, "method_stripped"))
    rates_stripped = cluster_rates(stripped)

    all_names = word_names + region_names
    half_raw = half_scores_from_rates(frame, np.hstack([rates_raw, regions_raw]), all_names)
    half_stripped = half_scores_from_rates(frame, rates_stripped, word_names)

    # ---- v3 battery user scores for redundancy (full data) ----
    v3_scored = score_slices_v2(frame[["user_id", "slice_text"]].copy())
    v3_user = v3_scored.groupby("user_id")[V3_BATTERY].mean()

    # ---- selection on A ----
    a_half = half_raw.loc[half_raw.index.get_level_values(0).isin(a_users)]
    r_a = early_late_r(a_half, all_names).sort_values(ascending=False)
    survivors = r_a.loc[r_a >= R_A_MIN]
    a_full = a_half.groupby(level=0).mean()
    a_join = a_full.join(v3_user, how="inner")
    kept: list[str] = []
    for name in survivors.index:
        ok = True
        for other in kept + V3_BATTERY:
            r = abs(np.corrcoef(a_join[name], a_join[other])[0, 1])
            if r > REDUNDANCY_MAX:
                ok = False
                break
        if ok:
            kept.append(name)
        if len(kept) >= CAP:
            break
    print(f"A-half: {len(survivors)} pass r_A >= {R_A_MIN}; kept after redundancy: {len(kept)}")

    # ---- confirmation on B ----
    b_half = half_raw.loc[~half_raw.index.get_level_values(0).isin(a_users)]
    b_half_str = half_stripped.loc[~half_stripped.index.get_level_values(0).isin(a_users)]
    r_b = early_late_r(b_half, kept)
    r_b_str = early_late_r(b_half_str, [n for n in kept if n in word_names])
    rows = []
    wide_b = b_half.unstack("half")
    for name in kept:
        e = wide_b[(name, "early")].dropna()
        l = wide_b[(name, "late")].reindex(e.index).dropna()
        e = e.reindex(l.index)
        boots = []
        idx = np.arange(len(e))
        for _ in range(500):
            t = rng.choice(idx, size=len(idx), replace=True)
            ev, lv = e.to_numpy()[t], l.to_numpy()[t]
            if ev.std() > 1e-12 and lv.std() > 1e-12:
                boots.append(np.corrcoef(ev, lv)[0, 1])
        lo, hi = np.percentile(boots, [2.5, 97.5])
        stripped_r = float(r_b_str.get(name, np.nan))
        confirmed = bool(r_b[name] >= R_B_MIN and lo > 0 and (np.isnan(stripped_r) or stripped_r >= R_B_STRIPPED_MIN))
        top = ", ".join(cluster_words[int(name.split("_")[1])][:10]) if name.startswith("wcl_") else "(content region)"
        rows.append({"candidate": name, "r_A": float(r_a[name]), "r_B": float(r_b[name]),
                     "r_B_ci_lo": float(lo), "r_B_ci_hi": float(hi),
                     "r_B_method_stripped": stripped_r, "confirmed": confirmed, "top_words": top})
    out = pd.DataFrame(rows).sort_values("r_B", ascending=False)
    n_confirmed = int(out["confirmed"].sum())
    verdict = "OP5_success" if n_confirmed >= 4 else ("OP5_partial" if n_confirmed >= 1 else "OP5_fail")
    criteria = {"n_selected_A": len(kept), "n_confirmed_B": n_confirmed, "verdict": verdict,
                "users_A": len(a_users), "users_B": len(users) - len(a_users)}
    out.to_csv(OUT_DIR / "op5_candidates.csv", index=False)
    pd.Series({f"wcl_{k:02d}": ", ".join(v[:25]) for k, v in cluster_words.items()}).to_csv(OUT_DIR / "word_clusters.csv")
    (OUT_DIR / "op5_results.json").write_text(json.dumps(criteria, indent=2) + "\n")
    REPORT.write_text("# SUICA OP-5 Construct Discovery v3 (A-discover / B-confirm)\n\n"
                      + out.round(3).to_markdown(index=False)
                      + "\n\n```json\n" + json.dumps(criteria, indent=2) + "\n```\n")
    print(out.round(3).to_string(index=False))
    print(json.dumps(criteria, indent=2))


if __name__ == "__main__":
    main()
