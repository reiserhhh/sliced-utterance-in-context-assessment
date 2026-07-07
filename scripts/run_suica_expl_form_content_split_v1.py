#!/usr/bin/env python
"""EXPL-1b — form/content split of the full-fit rung. EXPLORATORY.

Purpose: the v4 manuscript claims the open-vocabulary advantage over the
committed feature set "is concentrated in content features". EXPL-1
established full-fit tf-idf ridge mean r = .272 on the sealed cohort but
did not decompose it. This script measures the claim directly, on the
same 1,058 users, same folds:

  rung 1a (function words only)  tf-idf ridge with the vocabulary
                                 RESTRICTED to sklearn's English stop-word
                                 list (~318 function words) — a crude but
                                 standard operationalization of form.
  rung 1b (content only)         tf-idf ridge with stop words REMOVED
                                 (stop_words='english'), same caps as
                                 EXPL-1's full rung.

Custody identical to EXPL-1: labels spent at opening #1; exploratory;
ledger row EXPL-1b. Same gate replication + H2/H6 consistency asserts.
Disclosure: the default sklearn tokenizer splits contractions ("don't" ->
"don"), so apostrophe-form habits are only partially visible to rung 1a.
"""
from __future__ import annotations

import json
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
OUT_DIR = ROOT / "results" / "suica_expl_fit_gradient"

SEED = 42
TRAITS = ["Extraversion", "Neuroticism", "Agreeableness", "Conscientiousness", "Openness"]
ALPHAS = [1.0, 10.0, 100.0, 1000.0]
BANNER = "EXPLORATORY / NON-CONFIRMATORY — EXPL-1b form/content split (labels spent at opening #1)"


def fisher_ci(r: float, n: int) -> tuple[float, float]:
    z = np.arctanh(r); se = 1.0 / np.sqrt(n - 3)
    return float(np.tanh(z - 1.959963984540054 * se)), float(np.tanh(z + 1.959963984540054 * se))


def run_rung(docs, Y, vec_kwargs, label):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import KFold

    kf = KFold(n_splits=5, shuffle=True, random_state=SEED)
    inner = KFold(n_splits=3, shuffle=True, random_state=7)
    preds = np.empty_like(Y)
    for tr, te in kf.split(np.zeros(len(docs))):
        vec = TfidfVectorizer(lowercase=True, sublinear_tf=True, **vec_kwargs)
        Xtr = vec.fit_transform([docs[i] for i in tr])
        Xte = vec.transform([docs[i] for i in te])
        for j in range(Y.shape[1]):
            ytr = Y[tr, j]
            best_alpha, best = None, -np.inf
            for alpha in ALPHAS:
                scores = []
                for itr, ite in inner.split(np.zeros(len(tr))):
                    m = Ridge(alpha=alpha, solver="sparse_cg").fit(Xtr[itr], ytr[itr])
                    ip = m.predict(Xtr[ite])
                    scores.append(stats.pearsonr(ip, ytr[ite])[0] if np.std(ip) > 0 else 0.0)
                s = float(np.mean(scores))
                if s > best:
                    best_alpha, best = alpha, s
            m = Ridge(alpha=best_alpha, solver="sparse_cg").fit(Xtr, ytr)
            preds[te, j] = m.predict(Xte)
    out = {}
    for j, trait in enumerate(TRAITS):
        r, p = stats.pearsonr(preds[:, j], Y[:, j])
        lo, hi = fisher_ci(float(r), Y.shape[0])
        out[trait] = {"r": float(r), "p": float(p), "ci_lo": lo, "ci_hi": hi}
    out["MEAN_BIG5"] = {"r": float(np.mean([out[t]["r"] for t in TRAITS]))}
    print(f"[{label}] " + " ".join(f"{t[:1]}={out[t]['r']:+.3f}" for t in TRAITS)
          + f" mean={out['MEAN_BIG5']['r']:+.3f}")
    return out


def main() -> None:
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    print(BANNER)

    pred = pd.read_parquet(PREDICTORS)
    pred.index = pred.index.astype(str)
    big5 = pd.read_csv(BIG5_LABELS).set_index("user_id")
    big5.index = big5.index.astype(str)
    gate = (pred["n_conditions"] >= 4) & (pred["n_slices"] >= 12)   # opening L301
    inter = pred.index.intersection(big5.index)
    elig = inter[gate.loc[inter].fillna(False).to_numpy(bool)]
    assert len(elig) == 1058, len(elig)

    # consistency: H2 recompute must match the published opening exactly
    rep = json.loads(OPENING_REPORT.read_text())
    published = {h["id"]: h["r"] for h in rep["hypotheses"]}
    users = sorted(elig)
    r_h2 = float(pred.loc[users, "first_person_usage_v2"].corr(big5.loc[users, "Neuroticism"]))
    assert abs(r_h2 - published["H2"]) < 1e-9
    print("gate + H2 consistency ok")

    comments = pd.read_parquet(LOCKBOX_COMMENTS, columns=["author", "body"])
    comments = comments.loc[comments["author"].astype(str).isin(set(users))]
    text = comments.groupby("author")["body"].apply(" ".join)
    docs = text.reindex(users).fillna("").tolist()
    Y = big5.loc[users, TRAITS].to_numpy(float)

    fw = run_rung(docs, Y, {"vocabulary": sorted(ENGLISH_STOP_WORDS)}, "function words only (~318)")
    ct = run_rung(docs, Y, {"stop_words": "english", "min_df": 5, "max_features": 30000}, "content only (stop words removed)")

    result = {
        "banner": BANNER,
        "note": "same users/folds as EXPL-1 full rung (mean r=.272); tokenizer splits contractions — apostrophe habits partially invisible to the function-word rung (disclosed)",
        "function_words_only": fw,
        "content_only": ct,
    }
    (OUT_DIR / "EXPL_FORM_CONTENT_SPLIT.json").write_text(json.dumps(result, indent=2))
    print("written:", OUT_DIR / "EXPL_FORM_CONTENT_SPLIT.json")


if __name__ == "__main__":
    main()
