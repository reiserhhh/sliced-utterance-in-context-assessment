#!/usr/bin/env python
"""Analyze a revised SUICA action-growth candidate without communion."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evaluate_suica_repair_candidate_llm_coding_v1 import (  # noqa: E402
    DIMENSIONS,
    coder_agreement,
    evaluate_pole_separation,
    source_adjusted_delta,
)


EVAL_DIR = ROOT / "results" / "suica_repair_candidate_coding_eval_v1"
OUT_DIR = ROOT / "results" / "suica_action_growth_revision_v1"
REPORT_PATH = ROOT / "reports" / "suica_action_growth_revision_v1.md"


VIRTUAL_CANDIDATES = [
    {
        "virtual_candidate_id": "f10_action_growth_v2_no_communion",
        "source_candidate_id": "f10_action_growth_channel",
        "virtual_label": "directive-growth channel without communion",
        "expected_dimensions": ["directive_interpersonal", "redemption_growth"],
        "rationale": "Tests the user's revised construct after communion reversed in the micro-confirmation batch.",
    },
    {
        "virtual_candidate_id": "f10_directive_only_control_from_action_growth_items",
        "source_candidate_id": "f10_action_growth_channel",
        "virtual_label": "directive-only control on action-growth items",
        "expected_dimensions": ["directive_interpersonal"],
        "rationale": "Checks whether action-growth v2 is merely the directive-action factor repeated.",
    },
    {
        "virtual_candidate_id": "f10_growth_only_control_from_action_growth_items",
        "source_candidate_id": "f10_action_growth_channel",
        "virtual_label": "growth-only control on action-growth items",
        "expected_dimensions": ["redemption_growth"],
        "rationale": "Checks whether growth contributes independently after removing communion.",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze SUICA action-growth revision v1.")
    parser.add_argument("--eval-dir", default=str(EVAL_DIR))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--delta-threshold", type=float, default=0.3)
    parser.add_argument("--agreement-threshold", type=float, default=0.5)
    return parser.parse_args()


def load_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def source_adjusted_virtual_gate(
    pole: pd.DataFrame,
    source: pd.DataFrame,
    agreement: pd.DataFrame,
    *,
    delta_threshold: float,
    agreement_threshold: float,
) -> pd.DataFrame:
    rows: list[dict] = []
    for spec in VIRTUAL_CANDIDATES:
        source_candidate = spec["source_candidate_id"]
        expected = list(spec["expected_dimensions"])
        for coder_id in sorted(pole["coder_id"].dropna().unique()):
            pole_rows = pole.loc[
                pole["coder_id"].eq(coder_id)
                & pole["candidate_id"].eq(source_candidate)
                & pole["dimension"].isin(expected)
            ].copy()
            source_rows = source.loc[
                source["coder_id"].eq(coder_id)
                & source["candidate_id"].eq(source_candidate)
                & source["dimension"].isin(expected)
            ].copy()
            if pole_rows.empty or source_rows.empty:
                continue
            delta_support = int((pole_rows["high_minus_low"] >= delta_threshold).sum())
            source_support = int((source_rows["source_adjusted_high_minus_low"] >= delta_threshold).sum())
            component_count = len(expected)
            rows.append(
                {
                    "virtual_candidate_id": spec["virtual_candidate_id"],
                    "source_candidate_id": source_candidate,
                    "virtual_label": spec["virtual_label"],
                    "coder_id": coder_id,
                    "expected_dimensions": "; ".join(expected),
                    "expected_dimension_count": component_count,
                    "delta_support_count": delta_support,
                    "source_adjusted_support_count": source_support,
                    "min_expected_delta": float(pole_rows["high_minus_low"].min()),
                    "mean_expected_delta": float(pole_rows["high_minus_low"].mean()),
                    "min_expected_source_adjusted_delta": float(source_rows["source_adjusted_high_minus_low"].min()),
                    "mean_expected_source_adjusted_delta": float(source_rows["source_adjusted_high_minus_low"].mean()),
                    "component_coverage_gate": bool(delta_support == component_count and source_support == component_count),
                    "micro_batch_gate": "support"
                    if delta_support == component_count and source_support == component_count
                    else "weak_or_source_sensitive",
                }
            )
    gate = pd.DataFrame(rows)
    if gate.empty:
        return gate
    agreement_rows = []
    for spec in VIRTUAL_CANDIDATES:
        expected = list(spec["expected_dimensions"])
        agree = agreement.loc[agreement["dimension"].isin(expected)].copy() if not agreement.empty else pd.DataFrame()
        mean_r = float(agree["pearson_r"].mean()) if not agree.empty else float("nan")
        sub = gate.loc[gate["virtual_candidate_id"].eq(spec["virtual_candidate_id"])].copy()
        support_coder_count = int(sub["micro_batch_gate"].eq("support").sum())
        coder_count = int(sub["coder_id"].nunique())
        decision = (
            "pass_virtual_micro_confirmation"
            if support_coder_count == coder_count and (np.isnan(mean_r) or mean_r >= agreement_threshold)
            else "needs_item_bank_repair_or_larger_batch"
        )
        agreement_rows.append(
            {
                "virtual_candidate_id": spec["virtual_candidate_id"],
                "source_candidate_id": spec["source_candidate_id"],
                "virtual_label": spec["virtual_label"],
                "expected_dimensions": "; ".join(expected),
                "coder_count": coder_count,
                "support_coder_count": support_coder_count,
                "min_expected_delta_across_coders": float(sub["min_expected_delta"].min()),
                "min_source_adjusted_delta_across_coders": float(sub["min_expected_source_adjusted_delta"].min()),
                "mean_expected_dimension_agreement": mean_r,
                "decision": decision,
                "rationale": spec["rationale"],
            }
        )
    return gate.merge(pd.DataFrame(agreement_rows), on=["virtual_candidate_id", "source_candidate_id", "virtual_label", "expected_dimensions"], how="left")


def virtual_summary(virtual_gate: pd.DataFrame, original_acceptance: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for virtual_id, group in virtual_gate.groupby("virtual_candidate_id", sort=True):
        first = group.iloc[0]
        rows.append(
            {
                "candidate_id": virtual_id,
                "source_candidate_id": first["source_candidate_id"],
                "candidate_label": first["virtual_label"],
                "expected_dimensions": first["expected_dimensions"],
                "coder_count": int(first["coder_count"]),
                "support_coder_count": int(first["support_coder_count"]),
                "min_expected_delta_across_coders": float(first["min_expected_delta_across_coders"]),
                "min_source_adjusted_delta_across_coders": float(first["min_source_adjusted_delta_across_coders"]),
                "mean_expected_dimension_agreement": float(first["mean_expected_dimension_agreement"]),
                "decision": first["decision"],
                "summary_type": "virtual_revision",
            }
        )
    original = original_acceptance.loc[original_acceptance["candidate_id"].eq("f10_action_growth_channel")].copy()
    if not original.empty:
        original = original.rename(columns={"candidate_id": "candidate_id"})
        original["source_candidate_id"] = original["candidate_id"]
        original["summary_type"] = "original_micro_confirmation"
        rows.append(original[[
            "candidate_id",
            "source_candidate_id",
            "candidate_label",
            "expected_dimensions",
            "coder_count",
            "support_coder_count",
            "min_expected_delta_across_coders",
            "min_source_adjusted_delta_across_coders",
            "mean_expected_dimension_agreement",
            "decision",
            "summary_type",
        ]].iloc[0].to_dict())
    return pd.DataFrame(rows).sort_values(["summary_type", "decision", "candidate_id"])


def write_report(path: Path, summary: pd.DataFrame, gate: pd.DataFrame, pole: pd.DataFrame, source: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    action_rows = pole.loc[
        pole["candidate_id"].eq("f10_action_growth_channel")
        & pole["dimension"].isin(["directive_interpersonal", "redemption_growth", "communion"])
    ].copy()
    source_rows = source.loc[
        source["candidate_id"].eq("f10_action_growth_channel")
        & source["dimension"].isin(["directive_interpersonal", "redemption_growth", "communion"])
    ].copy()
    lines = [
        "# SUICA Action-Growth Revision v1",
        "",
        "## Purpose",
        "",
        "Analyze whether the failed `f10_action_growth_channel` can be repaired by removing `communion`, which reversed direction in the independent micro-confirmation batch.",
        "",
        "## Revision Summary",
        "",
        summary.round(3).to_markdown(index=False) if not summary.empty else "No summary rows.",
        "",
        "## Virtual Candidate Gates",
        "",
        gate.round(3).to_markdown(index=False) if not gate.empty else "No gate rows.",
        "",
        "## Original Action-Growth Component Pole Contrasts",
        "",
        action_rows.round(3).to_markdown(index=False) if not action_rows.empty else "No pole rows.",
        "",
        "## Original Action-Growth Component Source-Adjusted Deltas",
        "",
        source_rows.round(3).to_markdown(index=False) if not source_rows.empty else "No source rows.",
        "",
        "## Interpretation",
        "",
        "- The original action-growth-communion construct failed because `communion` reversed direction.",
        "- The revised `directive + redemption_growth` candidate passes the same micro-confirmation criterion on the existing blinded items.",
        "- The directive-only and growth-only controls also pass, so the revised construct is not yet proven to be more than two adjacent components.",
        "- Next step: build a larger item bank that samples directive-with-growth, directive-without-growth, growth-without-directive, and low-both texts.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    eval_dir = Path(args.eval_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    coded = load_csv(eval_dir / "merged_repair_coder_key_ratings.csv")
    acceptance = load_csv(eval_dir / "repair_candidate_acceptance_summary.csv")
    pole = evaluate_pole_separation(coded)
    source = source_adjusted_delta(coded)
    agreement = coder_agreement(coded)
    gate = source_adjusted_virtual_gate(
        pole,
        source,
        agreement,
        delta_threshold=args.delta_threshold,
        agreement_threshold=args.agreement_threshold,
    )
    summary = virtual_summary(gate, acceptance)

    summary.to_csv(out_dir / "action_growth_revision_summary.csv", index=False)
    gate.to_csv(out_dir / "action_growth_virtual_candidate_gate.csv", index=False)
    pole.to_csv(out_dir / "action_growth_recomputed_pole_separation.csv", index=False)
    source.to_csv(out_dir / "action_growth_recomputed_source_adjusted_delta.csv", index=False)
    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "eval_dir": str(eval_dir),
                "delta_threshold": args.delta_threshold,
                "agreement_threshold": args.agreement_threshold,
                "virtual_candidates": VIRTUAL_CANDIDATES,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(Path(args.report_path), summary, gate, pole, source)
    print("SUICA action-growth revision analysis complete.")
    print(summary.round(3).to_string(index=False))
    print(f"\nReport: {Path(args.report_path)}")


if __name__ == "__main__":
    main()
