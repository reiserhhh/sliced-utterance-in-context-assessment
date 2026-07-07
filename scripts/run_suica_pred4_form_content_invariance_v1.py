#!/usr/bin/env python
"""PRED-4: form/content structure invariance across rind REGIMES (document
types) — the covariate question made falsifiable.

User question (2026-07-07): free documents (PANDORA) vs fixed-format
documents (Essays prompt, X market) — what exactly differs, and can the
difference be CONTROLLED AS A COVARIATE?

Theory position (F4): naive covariate adjustment for document type repeats
the condition-centering mistake whenever type is self-selected (type is a
mediator of person -> text). Legitimate control routes are (a) design
(within-person multi-regime collection), (b) regime-relative norms, and
(c) restricting measurement to regime-INVARIANT coordinates. Route (c) is
testable TODAY: the v4 finding "flesh lives in FORM, rind carries CONTENT"
predicts that the inter-feature correlation STRUCTURE transports across
regimes much better for FORM (closed-class/function) features than for
CONTENT (open-class/topical) features.

PRE-COMMITTED (before execution):
  Feature split of the 23 anchors by linguistic class (documented; the two
  judgment calls — causal_meaning to CONTENT (majority lexical), agency to
  CONTENT (lexical verbs) — are fixed here, before any numbers):
    FORM (10): self_focus, second_person, third_person, general_people,
               directive, uncertainty, certainty, past_temporal,
               future_temporal, temporal_sequence
    CONTENT (13): the rest.
  PRED-4 pass rule: within-block structure-transport correlation
  (off-diagonal vectors, PRED-3 machinery) is HIGHER for FORM than CONTENT
  in 3/3 corpus pairs, with a user-bootstrap CI (300 reps) on the
  difference excluding 0 in >= 2/3 pairs. Fail => the form/content
  division does NOT buy cross-regime invariance and route (c) is dead.
  Secondary (reported, no bar): the same contrast using v4 families
  (F-family constructs vs C-family) at the construct level.

Corpora and loaders replicate run_suica_rind_regime_test_v3 exactly
(PANDORA fixed+mixed PRED-1 sample; Essays dev-half text only; X en
posts). Tier-U / dev-half / unlabeled X only — no label contact.
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

from scripts.run_suica_rind_regime_test_v3 import (  # noqa: E402
    slices_from_texts, stable_fraction, BUDGET, ESSAYS, X_POSTS, TIER_DIR)
from scripts.suica_v2_lib import score_slices_v2  # noqa: E402

OUT_DIR = ROOT / "results" / "suica_pred4_form_content_invariance_v1"
REPORT = ROOT / "reports" / "suica_pred4_form_content_invariance_v1.md"
SEED = 42
N_BOOT = 300

FORM = ["self_focus", "second_person", "third_person", "general_people",
        "directive", "uncertainty", "certainty", "past_temporal",
        "future_temporal", "temporal_sequence"]
CONTENT = ["achievement_order", "agency", "causal_meaning", "communion",
           "conflict_threat", "contamination_loss", "mentalization",
           "moral_norm", "negative_affect", "novelty_play", "positive_affect",
           "redemption_growth", "social_evaluation"]


def load_corpora() -> dict[str, pd.DataFrame]:
    comments = pd.read_parquet(TIER_DIR / "tier_u_comments.parquet")
    comments["author"] = comments["author"].astype(str)
    comments["subreddit"] = comments["subreddit"].fillna("__m__").astype(str)
    comments = comments.sort_values(["author", "created_utc"])
    slices = []
    for user, g in comments.groupby("author"):
        counts = g["subreddit"].value_counts()
        top = counts.index[0]
        g_top = g.loc[g["subreddit"].eq(top)]
        others = g.loc[~g["subreddit"].eq(top)]
        if len(g_top) < 20 or len(others) < 20 or others["subreddit"].nunique() < 4:
            continue
        slices += slices_from_texts(user, g_top["body"].astype(str).tolist(), max_slices=2 * BUDGET)
        mixed_texts = []
        buckets = [sg["body"].astype(str).tolist() for _, sg in others.groupby("subreddit")]
        idx = 0
        while len(mixed_texts) < 60 and any(buckets):
            b = buckets[idx % len(buckets)]
            if b:
                mixed_texts.append(b.pop(0))
            idx += 1
            buckets = [b for b in buckets if b]
        slices += slices_from_texts(user, mixed_texts, max_slices=2 * BUDGET)
    pandora = score_slices_v2(pd.DataFrame(slices))

    essays = pd.read_csv(ESSAYS, usecols=["user_id", "text"], dtype={"user_id": str})
    essays = essays.loc[essays["user_id"].map(stable_fraction) < 0.5]
    ess = score_slices_v2(pd.DataFrame(
        [s for _, row in essays.iterrows()
         for s in slices_from_texts(row["user_id"], [str(row["text"])], max_slices=2 * BUDGET)]))

    x = pd.read_csv(X_POSTS)
    x = x.loc[x["lang"].astype(str).eq("en")].copy()
    x["user_id"] = x["account_id"].astype(str)
    x["text"] = x["text"].fillna("").astype(str)
    x = x.loc[x["text"].str.len().gt(0)]
    x["norm"] = x["text"].str.lower().str.replace(r"https?://\S+", " ", regex=True).str.replace(r"\s+", " ", regex=True)
    x = x.drop_duplicates(["user_id", "norm"])
    xs = score_slices_v2(pd.DataFrame(
        [s for user, g in x.groupby("user_id")
         for s in slices_from_texts(user, g["text"].tolist(), max_slices=2 * BUDGET)]))
    return {"pandora": pandora, "essays": ess, "x_market": xs}


def user_rates(scored: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rc = [f"{c}_rate" for c in cols]
    return scored.groupby("user_id")[rc].mean()


def offdiag(m: pd.DataFrame) -> np.ndarray:
    c = m.corr().to_numpy()
    return c[np.triu_indices_from(c, k=1)]


def transport(mat_a: pd.DataFrame, mat_b: pd.DataFrame) -> float:
    a, b = offdiag(mat_a), offdiag(mat_b)
    mask = np.isfinite(a) & np.isfinite(b)
    return float(np.corrcoef(a[mask], b[mask])[0, 1])


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    corpora = load_corpora()
    for k, v in corpora.items():
        print(f"{k}: {v['user_id'].nunique()} users, {len(v)} slices")
    rates = {name: {"FORM": user_rates(sc, FORM), "CONTENT": user_rates(sc, CONTENT)}
             for name, sc in corpora.items()}

    pairs = [("pandora", "essays"), ("pandora", "x_market"), ("essays", "x_market")]
    rows, ok_ci = [], 0
    for a, b in pairs:
        t_form = transport(rates[a]["FORM"], rates[b]["FORM"])
        t_cont = transport(rates[a]["CONTENT"], rates[b]["CONTENT"])
        diffs = np.empty(N_BOOT)
        ua, ub = rates[a]["FORM"].index.to_numpy(), rates[b]["FORM"].index.to_numpy()
        for i in range(N_BOOT):
            ia = rng.integers(0, len(ua), len(ua)); ib = rng.integers(0, len(ub), len(ub))
            tf = transport(rates[a]["FORM"].iloc[ia], rates[b]["FORM"].iloc[ib])
            tc = transport(rates[a]["CONTENT"].iloc[ia], rates[b]["CONTENT"].iloc[ib])
            diffs[i] = tf - tc
        lo, hi = np.percentile(diffs, [2.5, 97.5])
        ci_excl = bool(lo > 0)
        ok_ci += int(ci_excl)
        rows.append({"pair": f"{a}_vs_{b}", "transport_FORM": round(t_form, 4),
                     "transport_CONTENT": round(t_cont, 4), "diff": round(t_form - t_cont, 4),
                     "ci_lo": round(float(lo), 4), "ci_hi": round(float(hi), 4),
                     "form_gt_content": bool(t_form > t_cont), "ci_excludes_0": ci_excl})
    df = pd.DataFrame(rows)
    all_dir = bool(df["form_gt_content"].all())
    verdict = "pass" if (all_dir and ok_ci >= 2) else ("fail" if not all_dir else "partial")
    res = {"pairs": rows, "direction_3of3": all_dir, "ci_excl_count": ok_ci,
           "PRED4_verdict": verdict,
           "criterion": "FORM > CONTENT in 3/3 pairs AND CI excludes 0 in >= 2/3"}
    (OUT_DIR / "pred4_results.json").write_text(json.dumps(res, indent=2) + "\n")
    REPORT.write_text("# PRED-4 form/content structure invariance across rind regimes\n\n"
                      + df.to_markdown(index=False)
                      + f"\n\n**verdict: {verdict}** (criterion: {res['criterion']})\n\n"
                      "Implication if pass: cross-regime deployment rides on FORM coordinates\n"
                      "+ regime-relative norms (route c); document type is NOT a legitimate\n"
                      "covariate when self-selected (F4).\n")
    print(df.to_string(index=False))
    print("PRED4:", verdict)


if __name__ == "__main__":
    main()
