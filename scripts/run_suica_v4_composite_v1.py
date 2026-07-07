#!/usr/bin/env python
"""v4 composite builder — dev-anchor performance by channel family + frozen
weights for the opening-#2 candidate predictors.

Feature sets (families from results/suica_c2_purity_all19_v1/all19_purity.csv):
  FULL31   19 constructs + choice axes (ex ax_11) — the v3 baseline set
           (expected to reproduce TF ~0.346)
  F_ONLY   flesh-gate passers only (channel-pure trait battery)
  C_ONLY   choice axes + C-family venue-signature constructs
  F_PLUS_C channel-clean battery: F_ONLY + C_ONLY (composites excluded)

Targets: Tier-D MBTI axes (EI/SN/TF/JP; lockbox excluded by tier
construction) and Essays dev-half Big5 (style-transport; Essays has no
venue channel — single-prompt essays — so only construct features apply).

Conventions: EXACTLY run_suica_dev_anchor_performance_v1 (RidgeCV alphas
logspace(-1,3,9), KFold(5, shuffle, seed 42), per-fold scaler; the style/
wcl feature builder is IMPORTED from that module, not reimplemented).

Frozen-weights artifact: for each target and each of {FULL31, F_PLUS_C},
fit scaler+RidgeCV on ALL dev rows and save {features, scaler mean/scale,
alpha, coef, intercept, cv_r} — the candidate predictors to be sealed in
the opening-#2 preregistration. Freezing happens at git commit; nothing
here touches any lockbox data (Tier-D orientation only, disclosure
per the sealed prereg's precedent).
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

import scripts.run_suica_dev_anchor_performance_v1 as dav  # noqa: E402
from scripts.run_suica_op9_embedding_baseline_v3 import OP5_KEPT, V3_BATTERY  # noqa: E402
from suica_core.suica import PERSONALITY_LEAK_RE, fixed_token_slices_for_text  # noqa: E402
from scripts.suica_v2_lib import score_slices_v2  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
PURITY = ROOT / "results" / "suica_c2_purity_all19_v1" / "all19_purity.csv"
OUT_DIR = ROOT / "results" / "suica_v4_composite_v1"
REPORT = ROOT / "reports" / "suica_v4_composite_v1.md"
SEED = 42
MBTI_AXES = ["EI_cont", "SN_cont", "TF_cont", "JP_cont"]
BIG5 = ["Extraversion", "Neuroticism", "Agreeableness", "Conscientiousness", "Openness"]


def frozen_fit(features: pd.DataFrame, target: pd.Series) -> dict:
    from sklearn.linear_model import RidgeCV
    from sklearn.preprocessing import StandardScaler
    j = features.join(target.rename("y"), how="inner").dropna(subset=["y"])
    x = j[features.columns].fillna(j[features.columns].mean()).to_numpy(float)
    y = j["y"].to_numpy(float)
    sc = StandardScaler().fit(x)
    m = RidgeCV(alphas=np.logspace(-1, 3, 9)).fit(sc.transform(x), y)
    return {"features": list(features.columns), "n": int(len(j)),
            "scaler_mean": sc.mean_.tolist(), "scaler_scale": sc.scale_.tolist(),
            "alpha": float(m.alpha_), "coef": m.coef_.tolist(), "intercept": float(m.intercept_)}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fam = pd.read_csv(PURITY).set_index("construct")["v4_family"]
    F_CONS = [c for c in fam.index if fam[c].startswith("F-")]
    C_CONS = [c for c in fam.index if fam[c].startswith("C-")]
    print(f"F-family: {F_CONS}\nC-family constructs: {C_CONS}")

    style, wcl_transform = dav.pandora_style_fit_and_battery()
    choice = pd.read_csv(dav.CHOICE, dtype={"user_id": str}).set_index("user_id")
    axes_cols = [c for c in choice.columns if c.startswith("choice_ax_") and c != "choice_ax_11"]
    battery = style.join(choice[axes_cols], how="left")
    tier_u = set(pd.read_csv(TIER_DIR / "tier_u_users.csv")["user_id"].astype(str))

    SETS = {
        "FULL31": list(style.columns) + axes_cols,
        "F_ONLY": F_CONS,
        "C_ONLY": axes_cols + C_CONS,
        "F_PLUS_C": F_CONS + axes_cols + C_CONS,
    }

    rows, weights = [], {}
    for axis in MBTI_AXES:
        lab = pd.read_csv(ROOT / f"data_sets/prepared/pandora_official/mbti_axes/pandora_official_{axis.split('_')[0]}_cont_prepared.csv",
                          usecols=["user_id", "positive_probability"], dtype={"user_id": str})
        lab = (lab.loc[lab["user_id"].isin(tier_u)].set_index("user_id")["positive_probability"].rename(axis))
        joined = battery.join(lab, how="inner")
        for set_name, cols in SETS.items():
            feats = joined[cols].fillna(joined[cols].mean())
            r = dav.ridge_cv_r(feats, joined[axis])
            rows.append({"target": axis, "set": set_name, "n_features": len(cols),
                         "n": int(len(joined)), "ridge_cv_r": r})
        for set_name in ("FULL31", "F_PLUS_C"):
            weights[f"{axis}::{set_name}"] = frozen_fit(joined[SETS[set_name]], joined[axis])

    # Essays dev half (transport; construct features only — no venue channel)
    dev = set(pd.read_csv(TIER_DIR / "essays_regime_dev_half.csv")["user_id"].astype(str))
    ess = pd.read_csv(ROOT / "data_sets/prepared/big5/essays_original_prepared.csv", dtype={"user_id": str})
    ess = ess.loc[ess["user_id"].isin(dev)]
    erows = []
    for _, row in ess.iterrows():
        for r in fixed_token_slices_for_text(str(row["text"]), slice_tokens=128, stride=128,
                                             min_slice_tokens=24, max_slices=20):
            if PERSONALITY_LEAK_RE.search(r["slice_text"]):
                continue
            erows.append({"user_id": row["user_id"], "slice_text": r["slice_text"]})
    ef = pd.DataFrame(erows)
    ev3 = score_slices_v2(ef[["user_id", "slice_text"]])
    estyle = ev3.groupby("user_id")[V3_BATTERY].mean().join(
        pd.concat([ef[["user_id"]], wcl_transform(ef["slice_text"])], axis=1).groupby("user_id").mean())
    elab = ess.set_index("user_id")[BIG5].apply(pd.to_numeric, errors="coerce")
    ejoined = estyle.join(elab, how="inner")
    ESETS = {"STYLE19": list(estyle.columns), "F_ONLY": F_CONS,
             "F_PLUS_Ccons": F_CONS + C_CONS}
    for trait in BIG5:
        for set_name, cols in ESETS.items():
            r = dav.ridge_cv_r(ejoined[cols].fillna(ejoined[cols].mean()), ejoined[trait])
            rows.append({"target": trait, "set": set_name, "n_features": len(cols),
                         "n": int(ejoined[trait].notna().sum()), "ridge_cv_r": r})

    df = pd.DataFrame(rows)
    df.round(4).to_csv(OUT_DIR / "v4_composite_performance.csv", index=False)
    (OUT_DIR / "v4_frozen_weights.json").write_text(json.dumps(weights, indent=2) + "\n")
    piv = df.pivot_table(index="target", columns="set", values="ridge_cv_r")
    REPORT.write_text("# v4 composite — channel-family dev performance + frozen weights\n\n"
                      + piv.round(3).to_markdown()
                      + "\n\nF-family = " + ", ".join(F_CONS)
                      + "\nC-family constructs = " + ", ".join(C_CONS)
                      + "\n\nWeights for {FULL31, F_PLUS_C} x MBTI axes frozen in "
                        "v4_frozen_weights.json (opening-#2 candidates; sealed at commit).\n"
                        "Conventions identical to dev_anchor v1 (RidgeCV logspace(-1,3,9), "
                        "KFold5 seed42). Tier-D orientation only; no lockbox contact.\n")
    print(piv.round(3).to_string())


if __name__ == "__main__":
    main()
