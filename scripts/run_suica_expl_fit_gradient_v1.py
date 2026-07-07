#!/usr/bin/env python
"""EXPL-1 — post-opening fit-gradient baseline. EXPLORATORY, NON-CONFIRMATORY.

Custody status
--------------
PANDORA Big5 labels for the Tier-L cohort were unsealed at lockbox opening #1
(git cd63d13, 2026-07-06) and are SPENT for confirmatory use. This script
re-reads those labels for a clearly-labeled exploratory analysis. Results are
recorded in the claims ledger as EXPL-1 and must be reported as exploratory
wherever they appear. Essays confirm-half labels are NOT touched.

Question
--------
On the same 1,058 eligible users, what does fitting to the labels buy?

  Rung 1 (full fit)   ridge over tf-idf 1-grams of each user's aggregated
                      text — the model family of the official PANDORA
                      baselines (Ridge/Lasso over tf-idf n-grams).
  Rung 2 (weight fit) ridge over the 16 frozen preregistered features
                      (4 style constructs + 11 log-ratio choice axes +
                      choice entropy); only combination weights are fitted.
  Rung 3 (no fit)     preregistered single constructs with fixed direction —
                      the published opening #1 values (H2 r=.1114,
                      H6 r=.0959); recomputed here only as a consistency
                      check on the eligibility-gate replication.

External anchor: official PANDORA baselines, reproduced bit-near in
results/pandora_paper_baseline_reproduction (LR-N mean r=.246 on n=1,402;
LR-NP mean r=.293 on n=1,386; different user set, folds, and eligibility).

Frozen conventions replicated verbatim from scripts/run_suica_lockbox_opening_1.py:
  eligibility gate  L301   (n_conditions >= 4) & (n_slices >= 12)
  finalize_axes     L232-239 (log-ratio vs eligible-cohort mean, EPS=1e-4)
  label loading     L439   read_csv(...).set_index("user_id")
  battery columns   L330   STYLE + choice_ax_{k}, k != 11 + choice_entropy
Runtime asserts require n_eligible == 1058 and exact agreement of the
rung-3 recomputation with OPENING_REPORT.json before anything else runs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
BIG5_LABELS = ROOT / "data_sets" / "prepared" / "pandora_official" / "pandora_official_big5_prepared.csv"
PREDICTORS = ROOT / "results" / "suica_lockbox_opening_1" / "predictors.parquet"
OPENING_REPORT = ROOT / "results" / "suica_lockbox_opening_1" / "OPENING_REPORT.json"
LOCKBOX_COMMENTS = TIER_DIR / "tier_l_comments.parquet"
ANCHOR_CSV = ROOT / "results" / "pandora_paper_baseline_reproduction" / "paper_baseline_reproduction_summary.csv"
OUT_DIR = ROOT / "results" / "suica_expl_fit_gradient"

SEED = 42          # same as opening-internal CV
EPS = 1e-4         # opening L104
N_CLASSES = 12
EXCLUDED_AXIS = 11
STYLE = ["tension_core_v2", "directive_action_v2", "first_person_usage_v2", "novelty_play_v2"]
TRAITS = ["Extraversion", "Neuroticism", "Agreeableness", "Conscientiousness", "Openness"]
ALPHAS_DENSE = np.logspace(-2, 3, 11)
ALPHAS_SPARSE = [1.0, 10.0, 100.0, 1000.0]

BANNER = "EXPLORATORY / NON-CONFIRMATORY — post-opening reuse of spent labels (EXPL-1)"


def finalize_axes(pred: pd.DataFrame, eligible_idx: pd.Index) -> pd.DataFrame:
    """Verbatim replication of opening L232-239."""
    shares = pred.loc[eligible_idx, [f"share_{k}" for k in range(N_CLASSES)]]
    pop = shares.mean(axis=0)
    for k in range(N_CLASSES):
        pred.loc[eligible_idx, f"choice_ax_{k:02d}"] = np.log(
            (shares[f"share_{k}"] + EPS) / (pop[f"share_{k}"] + EPS))
    return pred


def fisher_ci(r: float, n: int) -> tuple[float, float]:
    z = np.arctanh(r)
    se = 1.0 / np.sqrt(n - 3)
    return float(np.tanh(z - 1.959963984540054 * se)), float(np.tanh(z + 1.959963984540054 * se))


def oof_pearson(y: np.ndarray, preds: np.ndarray) -> dict:
    r, p = stats.pearsonr(preds, y)
    lo, hi = fisher_ci(float(r), len(y))
    return {"r": float(r), "p": float(p), "ci_lo": lo, "ci_hi": hi, "n": int(len(y))}


def rung2_weight_fit(pred: pd.DataFrame, big5: pd.DataFrame, users: list[str],
                     battery_cols: list[str]) -> dict:
    from sklearn.linear_model import RidgeCV
    from sklearn.model_selection import KFold
    from sklearn.preprocessing import StandardScaler

    X = pred.loc[users, battery_cols].to_numpy(float)
    out = {}
    kf = KFold(n_splits=5, shuffle=True, random_state=SEED)
    splits = list(kf.split(X))
    for trait in TRAITS:
        y = big5.loc[users, trait].to_numpy(float)
        preds = np.empty_like(y)
        for tr, te in splits:
            sc = StandardScaler().fit(X[tr])
            m = RidgeCV(alphas=ALPHAS_DENSE).fit(sc.transform(X[tr]), y[tr])
            preds[te] = m.predict(sc.transform(X[te]))
        out[trait] = oof_pearson(y, preds)
    out["MEAN_BIG5"] = {"r": float(np.mean([out[t]["r"] for t in TRAITS]))}
    return out


def rung1_full_fit(big5: pd.DataFrame, users: list[str]) -> dict:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import KFold

    comments = pd.read_parquet(LOCKBOX_COMMENTS, columns=["author", "body"])
    comments = comments.loc[comments["author"].astype(str).isin(set(users))]
    text = comments.groupby("author")["body"].apply(" ".join)
    docs = text.reindex(users).fillna("").tolist()

    Y = big5.loc[users, TRAITS].to_numpy(float)
    kf = KFold(n_splits=5, shuffle=True, random_state=SEED)
    preds = np.empty_like(Y)
    chosen_alphas: dict[str, list[float]] = {t: [] for t in TRAITS}
    inner = KFold(n_splits=3, shuffle=True, random_state=7)

    for tr, te in kf.split(np.zeros(len(users))):
        vec = TfidfVectorizer(lowercase=True, min_df=5, max_features=30000,
                              sublinear_tf=True)
        Xtr = vec.fit_transform([docs[i] for i in tr])
        Xte = vec.transform([docs[i] for i in te])
        for j, trait in enumerate(TRAITS):
            ytr = Y[tr, j]
            # alpha by inner 3-fold on the outer-train split (vectorizer shared
            # across inner folds — alpha-selection optimism only; exploratory)
            best_alpha, best_score = None, -np.inf
            for alpha in ALPHAS_SPARSE:
                scores = []
                for itr, ite in inner.split(np.zeros(len(tr))):
                    m = Ridge(alpha=alpha, solver="sparse_cg").fit(Xtr[itr], ytr[itr])
                    ip = m.predict(Xtr[ite])
                    scores.append(stats.pearsonr(ip, ytr[ite])[0] if np.std(ip) > 0 else 0.0)
                sc = float(np.mean(scores))
                if sc > best_score:
                    best_alpha, best_score = alpha, sc
            chosen_alphas[trait].append(best_alpha)
            m = Ridge(alpha=best_alpha, solver="sparse_cg").fit(Xtr, ytr)
            preds[te, j] = m.predict(Xte)

    out = {trait: oof_pearson(Y[:, j], preds[:, j]) for j, trait in enumerate(TRAITS)}
    out["MEAN_BIG5"] = {"r": float(np.mean([out[t]["r"] for t in TRAITS]))}
    out["_chosen_alphas"] = chosen_alphas
    return out


def main() -> None:
    print(BANNER)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pred = pd.read_parquet(PREDICTORS)
    pred.index = pred.index.astype(str)
    big5 = pd.read_csv(BIG5_LABELS).set_index("user_id")          # opening L439
    big5.index = big5.index.astype(str)

    gate = (pred["n_conditions"] >= 4) & (pred["n_slices"] >= 12)  # opening L301
    inter_b5 = pred.index.intersection(big5.index)
    big5_elig = inter_b5[gate.loc[inter_b5].fillna(False).to_numpy(bool)]
    assert len(big5_elig) == 1058, f"eligibility replication failed: {len(big5_elig)}"

    pred = finalize_axes(pred, big5_elig)
    users = sorted(big5_elig)  # fixed ordering => identical folds across rungs

    # ---- Rung 3 consistency check against the published opening ----
    rep = json.loads(OPENING_REPORT.read_text())
    published = {h["id"]: h["r"] for h in rep["hypotheses"]}
    r_h2 = float(pred.loc[users, "first_person_usage_v2"].corr(big5.loc[users, "Neuroticism"]))
    r_h6 = float(pred.loc[users, "choice_ax_06"].corr(big5.loc[users, "Openness"]))
    assert abs(r_h2 - published["H2"]) < 1e-9, (r_h2, published["H2"])
    assert abs(r_h6 - published["H6"]) < 1e-9, (r_h6, published["H6"])
    print(f"rung-3 consistency: H2 {r_h2:.10f} H6 {r_h6:.10f} — match published")

    battery_cols = STYLE + [f"choice_ax_{k:02d}" for k in range(N_CLASSES)
                            if k != EXCLUDED_AXIS] + ["choice_entropy"]   # opening L330

    print("rung 2 (weight fit, 16 frozen features) ...")
    rung2 = rung2_weight_fit(pred, big5, users, battery_cols)
    for t in TRAITS + ["MEAN_BIG5"]:
        print(f"  {t:18s} r={rung2[t]['r']:+.4f}")

    print("rung 1 (full fit, tf-idf 1-grams) ...")
    rung1 = rung1_full_fit(big5, users)
    for t in TRAITS + ["MEAN_BIG5"]:
        print(f"  {t:18s} r={rung1[t]['r']:+.4f}")

    anchor = pd.read_csv(ANCHOR_CSV)
    anchor_rows = anchor.loc[anchor["source"] == "official_precomputed",
                             ["variant", "trait", "mean_pearson", "n_total"]]

    result = {
        "banner": BANNER,
        "custody": {
            "labels": "PANDORA Big5 Tier-L labels, spent at opening #1 (git cd63d13)",
            "essays_confirm_half": "untouched",
            "ledger_row": "EXPL-1",
        },
        "eligibility": {"n": int(len(users)), "gate": "n_conditions>=4 & n_slices>=12"},
        "folds": {"outer": "KFold(5, shuffle, rs=42)", "ordering": "sorted(user_id)"},
        "rung3_no_fit_published": {
            "H2_first_person_to_N": published["H2"],
            "H6_politics_choice_to_O": published["H6"],
            "consistency_check": "recomputed to <1e-9",
        },
        "rung2_weight_fit": rung2,
        "rung1_full_fit": rung1,
        "external_anchor_official": anchor_rows.to_dict(orient="records"),
    }
    (OUT_DIR / "EXPL_FIT_GRADIENT.json").write_text(json.dumps(result, indent=2))

    lines = [
        "# EXPL-1 — Fit-gradient baseline (EXPLORATORY, NON-CONFIRMATORY)", "",
        f"> {BANNER}", ">",
        "> Labels spent at opening #1; reuse here is exploratory. Same 1,058",
        "> eligible users, same gate, fixed folds (KFold 5, shuffle, rs=42).", "",
        "| rung | model | E | N | A | C | O | mean |",
        "|---|---|---|---|---|---|---|---|",
    ]
    def row(name, model, d):
        cells = " | ".join(f"{d[t]['r']:+.3f}" for t in TRAITS)
        lines.append(f"| {name} | {model} | {cells} | {d['MEAN_BIG5']['r']:+.3f} |")
    row("1 full fit", "ridge over tf-idf 1-grams", rung1)
    row("2 weight fit", "ridge over 16 frozen features", rung2)
    lines += [
        f"| 3 no fit | preregistered single constructs | — | +{published['H2']:.3f} (first person) | — | — | +{published['H6']:.3f} (politics choice) | — |",
        "",
        "External anchor (different user set/protocol): official LR-N mean r = .246 (n=1,402), LR-NP mean r = .293 (n=1,386),",
        "reproduced in results/pandora_paper_baseline_reproduction (delta <= .0014).", "",
    ]
    (OUT_DIR / "EXPL_FIT_GRADIENT.md").write_text("\n".join(lines))
    print("written:", OUT_DIR / "EXPL_FIT_GRADIENT.json")


if __name__ == "__main__":
    main()
