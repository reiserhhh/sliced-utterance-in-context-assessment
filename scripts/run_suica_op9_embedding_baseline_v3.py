#!/usr/bin/env python
"""OP-9: embedding baseline — does a modern encoder subsume the SUICA layer?

Reviewer-proofing comparison on the SAME disjoint-occasion battery (early/late
halves, gap >= 90d) used for the construct inventory:

  M1 identification: same-user early-late cosine AUC vs shuffled pairs, for
     (a) bge-large mean vectors, (b) the 19-construct SUICA profile.
  M2 stability: early-late retest r of the top embedding PCs (PCA fit on early
     vectors) vs the SUICA constructs' r_B range.
  M3 subsumption: ridge CV R^2 of user-level embeddings -> each of the 19
     construct scores (and the reverse for symmetry).

Pre-committed interpretive rules:
  - Subsumption is MATERIAL if CV R^2 >= 0.80 for a majority of constructs ->
    SUICA must be reframed as a convenience layer over embeddings.
  - Identification gap is NOTED if embedding AUC - construct AUC > 0.10.
  - Otherwise: SUICA = interpretable, frozen, model-free measurement layer;
    embeddings = stronger representation but version-dependent and opaque —
    complementary, not competing.

The 15 OP-5 candidate scorers are re-derived deterministically (same seed,
same A-user fit rule; round-6 audit verified deterministic reproduction).
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

from scripts.run_suica_op5_construct_discovery_v3 import build_half_slices, stable_fraction  # noqa: E402
from scripts.suica_v2_lib import score_slices_v2  # noqa: E402

OUT_DIR = ROOT / "results" / "suica_op9_embedding_baseline_v3"
REPORT = ROOT / "reports" / "suica_op9_embedding_baseline_v3.md"
SEED = 42
MODEL = "BAAI/bge-large-en-v1.5"
V3_BATTERY = ["first_person_usage_v2", "directive_action_v2", "tension_core_v2", "novelty_play_v2"]
OP5_KEPT = ["wcl_60", "wcl_03", "wcl_36", "wcl_11", "wcl_45", "wcl_25", "wcl_02", "wcl_07",
            "wcl_54", "wcl_22", "wcl_13", "wcl_35", "wcl_15", "wcl_23", "wcl_20"]


def cv_r2(x: np.ndarray, y: np.ndarray, *, alphas=(10.0, 100.0), folds: int = 5) -> float:
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import KFold
    from sklearn.preprocessing import StandardScaler
    best = -np.inf
    for alpha in alphas:
        kf = KFold(n_splits=folds, shuffle=True, random_state=SEED)
        ss_res, ss_tot = 0.0, 0.0
        for tr, te in kf.split(x):
            sc = StandardScaler().fit(x[tr])
            m = Ridge(alpha=alpha).fit(sc.transform(x[tr]), y[tr])
            pred = m.predict(sc.transform(x[te]))
            ss_res += float(np.sum((y[te] - pred) ** 2))
            ss_tot += float(np.sum((y[te] - np.mean(y[tr])) ** 2))
        best = max(best, 1.0 - ss_res / max(1e-12, ss_tot))
    return best


def rederive_op5_scores(frame: pd.DataFrame) -> pd.DataFrame:
    """Deterministic re-fit of the OP-5 feature space (A users only) + transform all."""
    from sklearn.cluster import KMeans
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
    from sklearn.preprocessing import normalize
    users = sorted(frame["user_id"].unique())
    a_users = {u for u in users if stable_fraction("op5::" + u) < 0.5}
    a_mask = frame["user_id"].isin(a_users).to_numpy()
    tv = TfidfVectorizer(lowercase=True, strip_accents="unicode", analyzer="word",
                         ngram_range=(1, 1), max_features=20000, min_df=10, sublinear_tf=True)
    ta = tv.fit_transform(frame.loc[a_mask, "slice_text"])
    svd = TruncatedSVD(n_components=96, random_state=SEED).fit(ta)
    terms = tv.get_feature_names_out()
    dfc = np.asarray((ta > 0).sum(axis=0)).ravel()
    top_idx = np.argsort(-dfc)[:6000]
    wk = KMeans(n_clusters=64, random_state=SEED, n_init=6).fit(normalize(svd.components_.T[top_idx]))
    indicator = np.zeros((len(terms), 64))
    for pos, term_i in enumerate(top_idx):
        indicator[term_i, wk.labels_[pos]] = 1.0
    cv = CountVectorizer(vocabulary=tv.vocabulary_, lowercase=True, strip_accents="unicode",
                         analyzer="word", ngram_range=(1, 1))
    counts = cv.transform(frame["slice_text"])
    tokens = np.maximum(1, counts.sum(axis=1))
    rates = 100.0 * np.asarray(counts @ indicator) / np.asarray(tokens)
    out = pd.DataFrame(rates, columns=[f"wcl_{k:02d}" for k in range(64)])
    out["user_id"] = frame["user_id"].to_numpy()
    out["half"] = frame["half"].to_numpy()
    return out[["user_id", "half"] + OP5_KEPT]


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = build_half_slices()
    print(f"slices: {len(frame)} users={frame['user_id'].nunique()}")

    # ---- SUICA 19-construct half scores ----
    v3 = score_slices_v2(frame[["user_id", "slice_text"]].assign(half=frame["half"]))
    v3_half = v3.groupby(["user_id", "half"])[V3_BATTERY].mean()
    op5_half = rederive_op5_scores(frame).groupby(["user_id", "half"]).mean()
    suica_half = v3_half.join(op5_half)
    all_constructs = V3_BATTERY + OP5_KEPT

    # ---- embeddings (local MPS/CPU, or --precomputed <dir> from the CUDA box) ----
    if "--precomputed" in sys.argv:
        pre = Path(sys.argv[sys.argv.index("--precomputed") + 1])
        mat = np.load(pre / "emb_userhalf.npy")
        index = pd.read_csv(pre / "userhalf_index.csv", dtype={"user_id": str})
        emb_half = pd.DataFrame(mat, index=pd.MultiIndex.from_frame(index[["user_id", "half"]]))
        half_counts = pd.Series(index["n_slices"].to_numpy(),
                                index=pd.MultiIndex.from_frame(index[["user_id", "half"]]))
        print(f"embeddings (precomputed): {mat.shape}")
    else:
        import torch
        from sentence_transformers import SentenceTransformer
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        model = SentenceTransformer(MODEL, device=device)
        emb = model.encode(frame["slice_text"].tolist(), batch_size=128, show_progress_bar=False,
                           normalize_embeddings=True, convert_to_numpy=True).astype(np.float32)
        emb_df = pd.DataFrame(emb)
        emb_df["user_id"] = frame["user_id"].to_numpy()
        emb_df["half"] = frame["half"].to_numpy()
        emb_half = emb_df.groupby(["user_id", "half"]).mean()
        half_counts = emb_df.groupby(["user_id", "half"]).size()
        print(f"embeddings: {emb.shape} device={device}")

    # ---- M1 identification AUC ----
    def profile_auc(half_frame: pd.DataFrame, standardize: bool) -> float:
        wide_e = half_frame.xs("early", level="half")
        wide_l = half_frame.xs("late", level="half")
        common = wide_e.index.intersection(wide_l.index)
        e, l = wide_e.loc[common].to_numpy(float), wide_l.loc[common].to_numpy(float)
        if standardize:
            for m_ in (e, l):
                m_ -= m_.mean(axis=0)
                sd = m_.std(axis=0)
                sd[sd < 1e-12] = 1.0
                m_ /= sd
        def cos(a, b):
            d = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
            return np.where(d > 0, (a * b).sum(axis=1) / d, np.nan)
        same = cos(e, l)
        rand = cos(e, l[rng.permutation(len(l))])
        return float((same[:, None] > np.sort(rand)[None, :]).mean())

    auc_emb = profile_auc(emb_half, standardize=False)
    auc_suica = profile_auc(suica_half, standardize=True)

    # ---- M2 embedding-PC retest ----
    from sklearn.decomposition import PCA
    wide_e = emb_half.xs("early", level="half")
    wide_l = emb_half.xs("late", level="half")
    common = wide_e.index.intersection(wide_l.index)
    pca = PCA(n_components=30, random_state=SEED).fit(wide_e.loc[common])
    pe, pl = pca.transform(wide_e.loc[common]), pca.transform(wide_l.loc[common])
    pc_r = [float(np.corrcoef(pe[:, j], pl[:, j])[0, 1]) for j in range(30)]

    # ---- M3 subsumption ----
    weights = half_counts.reindex(emb_half.index).to_numpy(float)
    weighted = emb_half.mul(weights, axis=0)
    emb_user_frame = weighted.groupby(level=0).sum().div(
        pd.Series(weights, index=emb_half.index).groupby(level=0).sum(), axis=0)
    emb_user = emb_user_frame.loc[common].to_numpy(float)
    suica_user = suica_half.groupby(level=0).mean().loc[common]
    rows = []
    for c in all_constructs:
        y = suica_user[c].to_numpy(float)
        rows.append({"construct": c, "emb_to_construct_cv_r2": cv_r2(emb_user, y)})
    sub = pd.DataFrame(rows).sort_values("emb_to_construct_cv_r2", ascending=False)
    x_c = suica_user[all_constructs].to_numpy(float)
    pc_user = pca.transform(emb_user)
    rev = [cv_r2(x_c, pc_user[:, j]) for j in range(5)]

    material = bool((sub["emb_to_construct_cv_r2"] >= 0.80).mean() > 0.5)
    criteria = {
        "model": MODEL, "n_users": int(len(common)),
        "M1_auc_embedding": auc_emb, "M1_auc_suica19": auc_suica,
        "M1_gap": auc_emb - auc_suica, "M1_gap_material_gt_010": bool(auc_emb - auc_suica > 0.10),
        "M2_pc_retest_top5": [round(v, 3) for v in pc_r[:5]],
        "M2_pc_retest_max": max(pc_r), "M2_pc_retest_median_top30": float(np.median(pc_r)),
        "M3_subsumption_material": material,
        "M3_max_r2": float(sub["emb_to_construct_cv_r2"].max()),
        "M3_median_r2": float(sub["emb_to_construct_cv_r2"].median()),
        "M3_reverse_construct_to_pc_r2_top5": [round(v, 3) for v in rev],
    }
    sub.to_csv(OUT_DIR / "op9_subsumption.csv", index=False)
    pd.DataFrame({"pc": range(30), "retest_r": pc_r}).to_csv(OUT_DIR / "op9_pc_retest.csv", index=False)
    (OUT_DIR / "op9_results.json").write_text(json.dumps(criteria, indent=2, default=float) + "\n")
    REPORT.write_text("# SUICA OP-9 Embedding Baseline (bge-large)\n\n"
                      + sub.round(3).to_markdown(index=False)
                      + "\n\n```json\n" + json.dumps(criteria, indent=2, default=float) + "\n```\n")
    print(sub.round(3).to_string(index=False))
    print(json.dumps(criteria, indent=2, default=float))


if __name__ == "__main__":
    main()
