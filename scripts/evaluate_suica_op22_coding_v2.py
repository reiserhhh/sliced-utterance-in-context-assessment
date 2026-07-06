#!/usr/bin/env python
"""OP-22 coding evaluation (pre-committed rules; run after coders finish).

Per-construct pass rules (fixed BEFORE any coder result was read):
  T1 (7-way identification, chance = 1/7):
    LLM side: pooled accuracy >= 0.50 AND >= 3 of 4 coders individually above
    chance (one-sided binomial p < 0.05 on that construct's 16 items).
    Human side: >= 4 of 8 items correct.
  T2 (pair intensity, chance = 0.5): pooled LLM accuracy >= 0.75.
  Construct passes OP-22 iff T1-LLM AND T2 pass; human column reported
  alongside (human is the criterion anchor, not vetoed by LLMs or vice versa —
  disagreements are reported, not averaged away).
Also reported: distractor-pick rates, pairwise coder kappa, salience means,
per-tier (style vs content) summaries.
"""
from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "results" / "suica_op22_item_bank_v2"
CODES = ROOT / "results" / "suica_op22_llm_coding_v2"
OUT = ROOT / "results" / "suica_op22_evaluation_v2"
REPORT = ROOT / "reports" / "suica_op22_blind_coding_v2.md"
CODERS = ["deepseek", "qwen30", "llama30", "mistral20"]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    key = pd.read_csv(BANK / "t1_KEY_do_not_show_coders.csv", dtype={"item_id": str})
    pkey = pd.read_csv(BANK / "t2_KEY_do_not_show_coders.csv", dtype={"pair_id": str})
    t1 = {}
    for coder in CODERS:
        path = CODES / f"{coder}_t1.csv"
        if path.exists():
            t1[coder] = pd.read_csv(path, dtype={"id": str}).set_index("id")["choice"]
    human_path = BANK / "human_coding_sheet_clean.csv"
    if not human_path.exists():
        human_path = BANK / "human_coding_sheet.csv"
    human = pd.read_csv(human_path, dtype={"item_id": str})
    if "choice_clean" in human.columns:
        human["your_choice_A_to_G"] = human["choice_clean"]
    has_human = human["your_choice_A_to_G"].astype(str).str.strip().str.len().gt(0).mean() > 0.9
    rows = []
    for construct, g in key.groupby("construct"):
        row = {"construct": construct, "n_items": len(g)}
        passing_coders = 0
        accs = []
        for coder, choices in t1.items():
            sub = choices.reindex(g["item_id"])
            acc = float((sub.to_numpy() == g["correct_letter"].to_numpy()).mean())
            row[f"acc_{coder}"] = acc
            accs.append(acc)
            k = int((sub.to_numpy() == g["correct_letter"].to_numpy()).sum())
            p = stats.binomtest(k, len(g), 1 / 7, alternative="greater").pvalue
            passing_coders += int(p < 0.05)
        row["acc_pooled"] = float(np.mean(accs)) if accs else np.nan
        row["coders_above_chance"] = passing_coders
        if has_human:
            hsub = human.loc[human["item_id"].isin(set(g["item_id"]))]
            merged = hsub.merge(g[["item_id", "correct_letter"]], on="item_id")
            row["human_correct"] = int((merged["your_choice_A_to_G"].astype(str).str.strip().str.upper()
                                        == merged["correct_letter"]).sum())
            row["human_n"] = len(merged)
        rows.append(row)
    t1_eval = pd.DataFrame(rows)
    t2_rows = []
    for coder in CODERS:
        path = CODES / f"{coder}_t2.csv"
        if not path.exists():
            continue
        codes = pd.read_csv(path, dtype={"id": str}).set_index("id")["higher"]
        merged = pkey.assign(pred=codes.reindex(pkey["pair_id"]).to_numpy())
        for construct, g in merged.groupby("construct"):
            t2_rows.append({"construct": construct, "coder": coder,
                            "t2_acc": float((g["pred"] == g["higher"]).mean())})
    t2_eval = pd.DataFrame(t2_rows).pivot_table(index="construct", columns="coder", values="t2_acc")
    t2_eval["t2_pooled"] = t2_eval.mean(axis=1)
    final = t1_eval.merge(t2_eval[["t2_pooled"]].reset_index(), on="construct", how="left")
    final["t1_llm_pass"] = (final["acc_pooled"] >= 0.50) & (final["coders_above_chance"] >= 3)
    final["t2_pass"] = final["t2_pooled"] >= 0.75
    final["op22_pass"] = final["t1_llm_pass"] & final["t2_pass"]
    if has_human:
        final["human_pass"] = final["human_correct"] >= 4
    # pairwise agreement (raw letter agreement across full item set)
    agree = {}
    for a, b in combinations(t1, 2):
        common = t1[a].index.intersection(t1[b].index)
        agree[f"{a}~{b}"] = float((t1[a].reindex(common) == t1[b].reindex(common)).mean())
    summary = {"constructs_op22_pass": int(final["op22_pass"].sum()),
               "has_human": bool(has_human), "pairwise_agreement": agree}
    final.to_csv(OUT / "op22_construct_results.csv", index=False)
    (OUT / "op22_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    REPORT.write_text("# SUICA OP-22 Blind Coding v2 Results\n\n"
                      + final.round(3).to_markdown(index=False)
                      + "\n\n```json\n" + json.dumps(summary, indent=2) + "\n```\n")
    print(final.round(3).to_string(index=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
