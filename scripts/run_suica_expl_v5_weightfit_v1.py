#!/usr/bin/env python
"""EXPL-2 — v5-ported form features on the spent-label cohort. EXPLORATORY.

Custody: identical to EXPL-1/EXPL-1b — PANDORA Big5 labels were spent at
opening #1; this reuse is non-confirmatory, ledger row EXPL-2. Same
eligibility gate (replicated verbatim), same folds, and the run refuses to
proceed unless H2 reproduces the published opening value to <1e-9.

Question: do the trading-side v5 form features carry criterion signal that
the v4 committed features (16, mean r=.090 weight-fit) do not?
  Arm A  v4 frozen 16 features (sanity: must reproduce EXPL-1 rung 2)
  Arm B  v5 form features only (per-comment scoring = v5's native unit;
         per-user means; plus length habits)
  Arm C  union (A + B)
Plus per-feature Pearson r against each Big Five percentile (context only).
"""
from __future__ import annotations

import json
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v5port_form_battery_pandora_v1 import v5_slice_features  # noqa: E402
from project_persona.suica import TOKEN_RE  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
BIG5_LABELS = ROOT / "data_sets" / "prepared" / "pandora_official" / "pandora_official_big5_prepared.csv"
PREDICTORS = ROOT / "results" / "suica_lockbox_opening_1" / "predictors.parquet"
OPENING_REPORT = ROOT / "results" / "suica_lockbox_opening_1" / "OPENING_REPORT.json"
LOCKBOX_COMMENTS = TIER_DIR / "tier_l_comments.parquet"
OUT_DIR = ROOT / "results" / "suica_expl_v5_weightfit"

SEED = 42
N_CLASSES = 12
EXCLUDED_AXIS = 11
STYLE = ["tension_core_v2", "directive_action_v2", "first_person_usage_v2", "novelty_play_v2"]
TRAITS = ["Extraversion", "Neuroticism", "Agreeableness", "Conscientiousness", "Openness"]
EPS = 1e-4
BANNER = "EXPLORATORY / NON-CONFIRMATORY — EXPL-2 v5-feature weight-fit (labels spent at opening #1)"


def finalize_axes(pred: pd.DataFrame, eligible_idx: pd.Index) -> pd.DataFrame:
    shares = pred.loc[eligible_idx, [f"share_{k}" for k in range(N_CLASSES)]]
    pop = shares.mean(axis=0)
    for k in range(N_CLASSES):
        pred.loc[eligible_idx, f"choice_ax_{k:02d}"] = np.log(
            (shares[f"share_{k}"] + EPS) / (pop[f"share_{k}"] + EPS))
    return pred


def ridge_arm(X: np.ndarray, Y: np.ndarray, label: str) -> dict:
    # per-trait RidgeCV (per-trait alpha), exactly the EXPL-1 rung-2 protocol —
    # a first draft passed Y as a matrix (one shared alpha across traits) and
    # failed the arm-A sanity anchor (.0863 vs .0903); kept per-trait since.
    from sklearn.linear_model import RidgeCV
    from sklearn.model_selection import KFold
    from sklearn.preprocessing import StandardScaler
    kf = KFold(n_splits=5, shuffle=True, random_state=SEED)
    splits = list(kf.split(X))
    out = {}
    for j, trait in enumerate(TRAITS):
        y = Y[:, j]
        preds = np.empty_like(y)
        for tr, te in splits:
            sc = StandardScaler().fit(X[tr])
            m = RidgeCV(alphas=np.logspace(-2, 3, 11)).fit(sc.transform(X[tr]), y[tr])
            preds[te] = m.predict(sc.transform(X[te]))
        r, p = stats.pearsonr(preds, y)
        out[trait] = round(float(r), 4)
    out["MEAN_BIG5"] = round(float(np.mean([out[t] for t in TRAITS])), 4)
    print(f"[{label}] " + " ".join(f"{t[:1]}={out[t]:+.3f}" for t in TRAITS)
          + f" mean={out['MEAN_BIG5']:+.4f}")
    return out


def main() -> None:
    print(BANNER)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pred = pd.read_parquet(PREDICTORS)
    pred.index = pred.index.astype(str)
    big5 = pd.read_csv(BIG5_LABELS).set_index("user_id")
    big5.index = big5.index.astype(str)
    gate = (pred["n_conditions"] >= 4) & (pred["n_slices"] >= 12)   # opening L301
    inter = pred.index.intersection(big5.index)
    elig = inter[gate.loc[inter].fillna(False).to_numpy(bool)]
    assert len(elig) == 1058, len(elig)
    pred = finalize_axes(pred, elig)
    users = sorted(elig)

    rep = json.loads(OPENING_REPORT.read_text())
    published = {h["id"]: h["r"] for h in rep["hypotheses"]}
    r_h2 = float(pred.loc[users, "first_person_usage_v2"].corr(big5.loc[users, "Neuroticism"]))
    assert abs(r_h2 - published["H2"]) < 1e-9
    print("gate + H2 consistency ok")

    cache = OUT_DIR / "v5u_tier_l_features.parquet"
    if cache.exists():
        v5u = pd.read_parquet(cache).reindex(users)
        print("v5 features loaded from cache")
    else:
        print("scoring v5 features per comment on Tier-L ...")
        com = pd.read_parquet(LOCKBOX_COMMENTS, columns=["author", "body"])
        com["author"] = com["author"].astype(str)
        com = com.loc[com["author"].isin(set(users))].reset_index(drop=True)
        feats = v5_slice_features(com["body"])
        feats["author"] = com["author"].to_numpy()
        v5u = feats.groupby("author").mean()
        tokc = com["body"].astype(str).apply(lambda s: len(TOKEN_RE.findall(s))).astype(float)
        lh = pd.DataFrame({"author": com["author"], "tok": tokc})
        g = lh.groupby("author")["tok"]
        v5u["v5_log_tokens_mean"] = g.apply(lambda x: float(np.log1p(x).mean()))
        v5u["v5_post_len_cv"] = g.apply(lambda x: float(x.std() / x.mean()) if x.mean() > 0 else 0.0)
        v5u.to_parquet(cache)
        v5u = v5u.reindex(users)

    keep = [c for c in v5u.columns if v5u[c].std() > 1e-9]
    dropped = sorted(set(v5u.columns) - set(keep))
    print("v5 features kept:", len(keep), "| dropped (no variance):", dropped)

    battery_cols = STYLE + [f"choice_ax_{k:02d}" for k in range(N_CLASSES)
                            if k != EXCLUDED_AXIS] + ["choice_entropy"]     # opening L330
    Xa = pred.loc[users, battery_cols].to_numpy(float)
    Xb = v5u[keep].to_numpy(float)
    Xc = np.hstack([Xa, Xb])
    Y = big5.loc[users, TRAITS].to_numpy(float)

    arm_a = ridge_arm(Xa, Y, "A v4-16")
    arm_b = ridge_arm(Xb, Y, f"B v5-{len(keep)}")
    arm_c = ridge_arm(Xc, Y, f"C union-{Xc.shape[1]}")

    singles = {}
    for c in keep:
        singles[c] = {t: round(float(stats.pearsonr(v5u[c], big5.loc[users, t])[0]), 3)
                      for t in TRAITS}

    result = {"banner": BANNER,
              "custody": {"labels": "spent at opening #1; exploratory reuse",
                          "ledger_row": "EXPL-2"},
              "n": len(users), "v5_features_kept": keep, "dropped_no_variance": dropped,
              "arm_A_v4_16": arm_a, "arm_B_v5_only": arm_b, "arm_C_union": arm_c,
              "v5_single_feature_r": singles,
              "reference": {"EXPL1_rung2_v4_16_mean": 0.0903,
                            "EXPL1_full_fit_mean": 0.2724}}
    (OUT_DIR / "EXPL2_V5_WEIGHTFIT.json").write_text(json.dumps(result, indent=2))
    lines = ["# EXPL-2 — v5 form features, weight-fit vs v4 (EXPLORATORY)", "",
             f"> {BANNER}", "",
             "| arm | E | N | A | C | O | mean |", "|---|---|---|---|---|---|---|"]
    for name, arm in [("A: v4 frozen 16", arm_a), (f"B: v5 only ({len(keep)})", arm_b),
                      (f"C: union ({Xc.shape[1]})", arm_c)]:
        lines.append("| " + name + " | " + " | ".join(f"{arm[t]:+.3f}" for t in TRAITS)
                     + f" | {arm['MEAN_BIG5']:+.4f} |")
    lines += ["", "Arm A must reproduce EXPL-1 rung 2 (.0903). Full-fit ceiling .2724.", ""]
    (OUT_DIR / "EXPL2_V5_WEIGHTFIT.md").write_text("\n".join(lines))
    print("written:", OUT_DIR / "EXPL2_V5_WEIGHTFIT.md")


if __name__ == "__main__":
    main()
