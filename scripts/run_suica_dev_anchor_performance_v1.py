#!/usr/bin/env python
"""Dev-tier anchor performance for the worked-example manual (Section 2).

LOCKBOX REMAINS SEALED. Anchors used here are development-tier by design:
- MBTI (EI/SN/TF/JP continuous): Tier-D labels — the 9,042-user MBTI axis
  labels restricted to Tier-U members (lockbox users excluded by
  construction). Plan section 2 designates these "dev orientation".
- Big5: Essays DEV-HALF labels (essays_regime_dev_half.csv). The confirm
  half stays untouched for P5. First label contact of the dev half is logged
  in the ledger.

Battery: 19 style constructs (uncentered) + 12 choice axes (ax_11 excluded
as MBTI-community leakage; PANDORA only). Analyses per target: univariate
Pearson r with BH-FDR within target, and 5-fold ridge CV multivariate r.
All outputs are T2 development-tier orientation — NOT confirmatory numbers.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.suica import PERSONALITY_LEAK_RE, fixed_token_slices_for_text, bh_fdr  # noqa: E402
from scripts.run_suica_op9_embedding_baseline_v3 import OP5_KEPT, V3_BATTERY  # noqa: E402
from scripts.run_suica_op5_construct_discovery_v3 import stable_fraction  # noqa: E402
from scripts.suica_v2_lib import score_slices_v2  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
CHOICE = ROOT / "results" / "suica_e3_e4_choice_class_v2_s128" / "choice_axis_scores.csv"
OUT_DIR = ROOT / "results" / "suica_dev_anchor_performance_v1"
REPORT = ROOT / "reports" / "suica_dev_anchor_performance_v1.md"
SEED = 42
MBTI_AXES = ["EI_cont", "SN_cont", "TF_cont", "JP_cont"]
BIG5 = ["Extraversion", "Neuroticism", "Agreeableness", "Conscientiousness", "Openness"]


def pandora_style_fit_and_battery():
    """PANDORA style scores + a frozen transform for transporting wcl to Essays."""
    from sklearn.cluster import KMeans
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
    from sklearn.preprocessing import normalize
    frame = pd.read_parquet(TIER_DIR / "op9_half_slices.parquet")
    users = sorted(frame["user_id"].unique())
    a_users = {u for u in users if stable_fraction("op5::" + u) < 0.5}
    a_mask = frame["user_id"].isin(a_users).to_numpy()
    tv = TfidfVectorizer(lowercase=True, strip_accents="unicode", analyzer="word",
                         ngram_range=(1, 1), max_features=20000, min_df=10, sublinear_tf=True)
    ta = tv.fit_transform(frame.loc[a_mask, "slice_text"])
    svd = TruncatedSVD(n_components=96, random_state=SEED).fit(ta)
    dfc = np.asarray((ta > 0).sum(axis=0)).ravel()
    top_idx = np.argsort(-dfc)[:6000]
    wk = KMeans(n_clusters=64, random_state=SEED, n_init=6).fit(normalize(svd.components_.T[top_idx]))
    indicator = np.zeros((len(tv.get_feature_names_out()), 64))
    for pos, term_i in enumerate(top_idx):
        indicator[term_i, wk.labels_[pos]] = 1.0
    cv = CountVectorizer(vocabulary=tv.vocabulary_, lowercase=True, strip_accents="unicode",
                         analyzer="word", ngram_range=(1, 1))

    def wcl_scores(texts: pd.Series) -> pd.DataFrame:
        counts = cv.transform(texts)
        tokens = np.maximum(1, counts.sum(axis=1))
        rates = 100.0 * np.asarray(counts @ indicator) / np.asarray(tokens)
        return pd.DataFrame(rates, columns=[f"wcl_{k:02d}" for k in range(64)])[OP5_KEPT]

    v3 = score_slices_v2(frame[["user_id", "slice_text"]])
    style = v3.groupby("user_id")[V3_BATTERY].mean().join(
        pd.concat([frame[["user_id"]], wcl_scores(frame["slice_text"])], axis=1).groupby("user_id").mean())
    return style, wcl_scores


def univariate(features: pd.DataFrame, target: pd.Series) -> pd.DataFrame:
    rows = []
    for col in features.columns:
        mask = features[col].notna() & target.notna()
        r, p = stats.pearsonr(features.loc[mask, col], target.loc[mask])
        rows.append({"feature": col, "r": float(r), "p": float(p), "n": int(mask.sum())})
    out = pd.DataFrame(rows)
    out["q_bh"] = bh_fdr(out["p"].tolist())
    return out.sort_values("r", key=abs, ascending=False)


def ridge_cv_r(features: pd.DataFrame, target: pd.Series, seed: int = SEED) -> float:
    from sklearn.linear_model import RidgeCV
    from sklearn.model_selection import KFold
    from sklearn.preprocessing import StandardScaler
    mask = features.notna().all(axis=1) & target.notna()
    x, y = features.loc[mask].to_numpy(float), target.loc[mask].to_numpy(float)
    preds = np.zeros(len(y))
    for tr, te in KFold(5, shuffle=True, random_state=seed).split(x):
        sc = StandardScaler().fit(x[tr])
        m = RidgeCV(alphas=np.logspace(-1, 3, 9)).fit(sc.transform(x[tr]), y[tr])
        preds[te] = m.predict(sc.transform(x[te]))
    return float(np.corrcoef(preds, y)[0, 1])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    style, wcl_transform = pandora_style_fit_and_battery()
    choice = pd.read_csv(CHOICE, dtype={"user_id": str}).set_index("user_id")
    choice = choice[[c for c in choice.columns if c.startswith("choice_ax_") and c != "choice_ax_11"]]
    battery = style.join(choice, how="left")
    tier_u = set(pd.read_csv(TIER_DIR / "tier_u_users.csv")["user_id"].astype(str))

    uni_frames, summary_rows = [], []
    for axis in MBTI_AXES:
        lab = pd.read_csv(ROOT / f"data_sets/prepared/pandora_official/mbti_axes/pandora_official_{axis.split('_')[0]}_cont_prepared.csv",
                          usecols=["user_id", "positive_probability"], dtype={"user_id": str})
        lab = (lab.loc[lab["user_id"].isin(tier_u)].set_index("user_id")["positive_probability"]
               .rename(axis))
        joined = battery.join(lab, how="inner")
        uni = univariate(joined[battery.columns], joined[axis]).assign(target=axis, source="pandora_tierD_mbti")
        uni_frames.append(uni)
        cvr_full = ridge_cv_r(joined[battery.columns].fillna(joined[battery.columns].mean()), joined[axis])
        cvr_style = ridge_cv_r(joined[style.columns], joined[axis])
        summary_rows.append({"target": axis, "n": int(len(joined)), "ridge_cv_r_full_battery": cvr_full,
                             "ridge_cv_r_style_only": cvr_style,
                             "best_univariate": uni.iloc[0]["feature"], "best_r": float(uni.iloc[0]["r"]),
                             "q_lt_05_count": int((uni["q_bh"] < 0.05).sum())})

    # ---- Essays dev half (Big5) ----
    dev = set(pd.read_csv(TIER_DIR / "essays_regime_dev_half.csv")["user_id"].astype(str))
    ess = pd.read_csv(ROOT / "data_sets/prepared/big5/essays_original_prepared.csv",
                      dtype={"user_id": str})
    ess = ess.loc[ess["user_id"].isin(dev)]
    rows = []
    for _, row in ess.iterrows():
        for r in fixed_token_slices_for_text(str(row["text"]), slice_tokens=128, stride=128,
                                             min_slice_tokens=24, max_slices=20):
            if PERSONALITY_LEAK_RE.search(r["slice_text"]):
                continue
            rows.append({"user_id": row["user_id"], "slice_text": r["slice_text"]})
    ef = pd.DataFrame(rows)
    ev3 = score_slices_v2(ef[["user_id", "slice_text"]])
    estyle = ev3.groupby("user_id")[V3_BATTERY].mean().join(
        pd.concat([ef[["user_id"]], wcl_transform(ef["slice_text"])], axis=1).groupby("user_id").mean())
    elab = ess.set_index("user_id")[BIG5].apply(pd.to_numeric, errors="coerce")
    ejoined = estyle.join(elab, how="inner")
    for trait in BIG5:
        uni = univariate(ejoined[estyle.columns], ejoined[trait]).assign(target=trait, source="essays_devhalf_big5")
        uni_frames.append(uni)
        cvr = ridge_cv_r(ejoined[estyle.columns], ejoined[trait])
        summary_rows.append({"target": trait, "n": int(ejoined[trait].notna().sum()),
                             "ridge_cv_r_full_battery": np.nan, "ridge_cv_r_style_only": cvr,
                             "best_univariate": uni.iloc[0]["feature"], "best_r": float(uni.iloc[0]["r"]),
                             "q_lt_05_count": int((uni["q_bh"] < 0.05).sum())})

    summary = pd.DataFrame(summary_rows)
    uni_all = pd.concat(uni_frames, ignore_index=True)
    summary.to_csv(OUT_DIR / "dev_anchor_summary.csv", index=False)
    uni_all.to_csv(OUT_DIR / "dev_anchor_univariate.csv", index=False)
    REPORT.write_text(
        "# SUICA Dev-Tier Anchor Performance (T2 orientation; LOCKBOX SEALED)\n\n"
        "MBTI = Tier-D labels (lockbox users excluded); Big5 = Essays dev-half labels\n"
        "(confirm half untouched). These numbers are development-tier orientation for\n"
        "the worked-example manual, NOT confirmatory external validity.\n\n"
        + summary.round(3).to_markdown(index=False)
        + "\n\n## Top univariate edges per target (q_BH < 0.05)\n\n"
        + uni_all.loc[uni_all["q_bh"] < 0.05].groupby("target").head(5).round(3).to_markdown(index=False) + "\n")
    print(summary.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
