#!/usr/bin/env python
"""OP-33: co-selection (character n-gram) construct discovery — chasing the
~32% of person-identifiable signal that escapes the word-rate battery
(OP-9 M3), where the stylome/idiolect literature says individuality lives
(Wright 2017 co-selection; van Halteren 2005 stylome).

Design (A-discover / B-confirm by USER, exactly the OP-5 discipline;
round-10 rule: features are BOUND TO THEIR FIT, so the char-ngram->SVD->
cluster transform fitted on A is TRANSPORTED to B, never refit):
  1. Char 3-4 gram TF-IDF on A-half slices; SVD 96; cluster the top-DF
     n-grams into K=48 co-selection axes (KMeans).
  2. A-half disjoint-occasion retest (>=90-day-gap early/late) per axis;
     keep axes with r_A >= 0.30 AND incremental over the 19-word battery
     (partial-out battery, residual retest still >= 0.20) — the
     non-redundancy gate that makes these NEW signal, not restated words.
  3. B-half confirmation with the TRANSPORTED transform: r_B reported.
  4. Flesh-purity gate (v4) on confirmed axes (class-disjoint retest +
     choice-mediated share) to place them F/C/composite.
  5. M3 shrinkage: does adding confirmed co-selection axes to the 19-word
     battery raise identification AUC / lower the embedding-subsumption gap?

PRE-COMMITTED (before run):
  R_A_MIN 0.30; incremental residual retest >= 0.20; confirm bar r_B >= 0.25;
  SUCCESS = >= 3 confirmed non-redundant co-selection axes.
Tier-U only; label-free.
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

from scripts.run_suica_op9_embedding_baseline_v3 import rederive_op5_scores, OP5_KEPT, V3_BATTERY  # noqa: E402
from scripts.suica_v2_lib import score_slices_v2  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
OUT_DIR = ROOT / "results" / "suica_op33_coselection_discovery_v1"
REPORT = ROOT / "reports" / "suica_op33_coselection_discovery_v1.md"
SEED = 42
K_AXES = 48
R_A_MIN = 0.30
RESID_MIN = 0.20
R_B_MIN = 0.25
import hashlib


def stable_fraction(v: str) -> float:
    return int(hashlib.sha1(("op33::" + str(v)).encode()).hexdigest()[:12], 16) / float(16**12 - 1)


def retest(vals: pd.DataFrame) -> float:
    j = vals.dropna()
    return float(j["early"].corr(j["late"])) if len(j) >= 30 and j["early"].std() and j["late"].std() else np.nan


def main() -> None:
    from sklearn.cluster import KMeans
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.preprocessing import normalize
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = pd.read_parquet(TIER_DIR / "op9_half_slices.parquet")
    users = sorted(frame["user_id"].unique())
    a_users = {u for u in users if stable_fraction(u) < 0.5}
    a_mask = frame["user_id"].isin(a_users).to_numpy()

    # ---- fit co-selection space on A ----
    tv = TfidfVectorizer(lowercase=True, analyzer="char_wb", ngram_range=(3, 4),
                         min_df=25, max_features=40000, sublinear_tf=True)
    ta = tv.fit_transform(frame.loc[a_mask, "slice_text"])
    svd = TruncatedSVD(n_components=96, random_state=SEED).fit(ta)
    dfc = np.asarray((ta > 0).sum(axis=0)).ravel()
    top = np.argsort(-dfc)[:8000]
    km = KMeans(n_clusters=K_AXES, random_state=SEED, n_init=6).fit(normalize(svd.components_.T[top]))
    indicator = np.zeros((len(tv.get_feature_names_out()), K_AXES))
    for pos, term_i in enumerate(top):
        indicator[term_i, km.labels_[pos]] = 1.0
    cv = CountVectorizer(vocabulary=tv.vocabulary_, lowercase=True, analyzer="char_wb", ngram_range=(3, 4))

    def cos_scores(texts: pd.Series) -> pd.DataFrame:
        counts = cv.transform(texts)
        tot = np.maximum(1, counts.sum(axis=1))
        rates = 100.0 * np.asarray(counts @ indicator) / np.asarray(tot)
        return pd.DataFrame(rates, columns=[f"cos_{k:02d}" for k in range(K_AXES)], index=texts.index)

    cos = cos_scores(frame["slice_text"])
    both = pd.concat([frame[["user_id", "half"]], cos], axis=1)
    battery = pd.concat([frame[["user_id", "half"]],
                         score_slices_v2(frame[["user_id", "slice_text"]])[V3_BATTERY].reset_index(drop=True),
                         rederive_op5_scores(frame)[OP5_KEPT].reset_index(drop=True)], axis=1)

    def half_means(df, cols):
        return df.groupby(["user_id", "half"])[cols].mean()

    cos_hm = half_means(both, list(cos.columns))
    bat_hm = half_means(battery, V3_BATTERY + OP5_KEPT)
    cos_e = cos_hm.xs("early", level="half"); cos_l = cos_hm.xs("late", level="half")
    bat_e = bat_hm.xs("early", level="half"); bat_l = bat_hm.xs("late", level="half")
    common = cos_e.index.intersection(cos_l.index)
    aset = [u for u in common if u in a_users]; bset = [u for u in common if u not in a_users]

    rows = []
    for k in range(K_AXES):
        col = f"cos_{k:02d}"
        vA = pd.DataFrame({"early": cos_e.loc[aset, col], "late": cos_l.loc[aset, col]})
        rA = retest(vA)
        if not (rA >= R_A_MIN):
            continue
        # incremental: residualize the axis on the 19 battery (per half) on A, retest residual
        from numpy.linalg import lstsq
        XeA = np.c_[np.ones(len(aset)), bat_e.loc[aset, V3_BATTERY + OP5_KEPT].fillna(0).to_numpy()]
        XlA = np.c_[np.ones(len(aset)), bat_l.loc[aset, V3_BATTERY + OP5_KEPT].fillna(0).to_numpy()]
        be = cos_e.loc[aset, col].to_numpy() - XeA @ lstsq(XeA, cos_e.loc[aset, col].to_numpy(), rcond=None)[0]
        bl = cos_l.loc[aset, col].to_numpy() - XlA @ lstsq(XlA, cos_l.loc[aset, col].to_numpy(), rcond=None)[0]
        resid_r = float(np.corrcoef(be, bl)[0, 1])
        vB = pd.DataFrame({"early": cos_e.loc[bset, col], "late": cos_l.loc[bset, col]})
        rB = retest(vB)
        rows.append({"axis": col, "r_A": round(rA, 4), "residual_retest_A": round(resid_r, 4),
                     "r_B": round(rB, 4),
                     "confirmed": bool(resid_r >= RESID_MIN and rB >= R_B_MIN)})
    df = pd.DataFrame(rows).sort_values("r_B", ascending=False)
    confirmed = df.loc[df["confirmed"]]

    # top n-grams for confirmed axes (interpretability)
    feats = np.array(tv.get_feature_names_out())
    tops = {}
    for col in confirmed["axis"]:
        k = int(col.split("_")[1])
        members = np.where(km.labels_ == k)[0]
        gram_idx = top[members]
        tops[col] = [feats[i].replace(" ", "_") for i in gram_idx[np.argsort(-dfc[gram_idx])[:12]]]

    res = {"K_axes": K_AXES, "n_users_A": len(aset), "n_users_B": len(bset),
           "n_pass_A": int(len(df)), "n_confirmed": int(len(confirmed)),
           "SUCCESS": bool(len(confirmed) >= 3),
           "confirmed_axes": confirmed.to_dict(orient="records"),
           "top_ngrams": tops}
    df.to_csv(OUT_DIR / "op33_axes.csv", index=False)
    (OUT_DIR / "op33_results.json").write_text(json.dumps(res, indent=2, default=float) + "\n")
    REPORT.write_text("# OP-33 co-selection (char n-gram) construct discovery\n\n"
                      + df.round(3).to_markdown(index=False)
                      + "\n\n## Confirmed axis top n-grams\n\n"
                      + "\n".join(f"- **{k}**: {', '.join(v)}" for k, v in tops.items())
                      + f"\n\n```json\n{json.dumps({k: res[k] for k in ['n_confirmed','SUCCESS']}, indent=2)}\n```\n")
    print(df.round(3).to_string(index=False))
    print(json.dumps({k: res[k] for k in ["n_pass_A", "n_confirmed", "SUCCESS"]}, indent=2))


if __name__ == "__main__":
    main()
