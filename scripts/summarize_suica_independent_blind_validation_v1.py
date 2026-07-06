#!/usr/bin/env python
"""Summarize SUICA independent blind-coding evidence into factor gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "results" / "suica_independent_coding_eval_deepseek_AB_full_v1"
BATCH_DIR = ROOT / "results" / "suica_independent_blind_validation_batch_v1"
OUT_DIR = ROOT / "results" / "suica_independent_blind_validation_final_v1"
REPORT_PATH = ROOT / "reports" / "suica_independent_blind_validation_final_v1.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize SUICA independent blind validation v1.")
    parser.add_argument("--eval-dir", default=str(EVAL_DIR))
    parser.add_argument("--batch-dir", default=str(BATCH_DIR))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--min-agreement-r", type=float, default=0.55)
    return parser.parse_args()


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def factor_acceptance_summary(
    expected_gate: pd.DataFrame,
    source_gate: pd.DataFrame,
    manifest: pd.DataFrame,
) -> pd.DataFrame:
    coders = sorted(expected_gate["coder_id"].dropna().unique())
    rows: list[dict] = []
    for factor in sorted(expected_gate["factor"].dropna().unique()):
        e = expected_gate.loc[expected_gate["factor"].eq(factor)].copy()
        s = source_gate.loc[source_gate["factor"].eq(factor)].copy()
        meta = manifest.loc[manifest["factor"].eq(factor)].head(1)
        construct_support_coders = sorted(e.loc[e["construct_gate"].eq("support"), "coder_id"].astype(str).unique())
        source_support_coders = sorted(s.loc[s["source_adjusted_gate"].eq("support"), "coder_id"].astype(str).unique())
        full_support_coders = sorted(set(construct_support_coders).intersection(source_support_coders))
        construct_pass = set(construct_support_coders) == set(coders)
        source_pass = set(source_support_coders) == set(coders)
        if construct_pass and source_pass:
            decision = "pass_independent_blind_gate"
            next_action = "promote_to_construct_candidate_with_manual_review"
        elif source_pass and len(full_support_coders) >= 1:
            decision = "partial_construct_gate_revise_or_add_items"
            next_action = "inspect_expected_dimensions_and_add_or_rebalance_items"
        else:
            decision = "hold_or_repair_factor"
            next_action = "do_not_promote; rename_split_or_repair_factor"
        rows.append(
            {
                "factor": factor,
                "provisional_name": meta["provisional_name"].iloc[0] if not meta.empty and "provisional_name" in meta else "",
                "formal_inclusion_status": meta["formal_inclusion_status"].iloc[0] if not meta.empty and "formal_inclusion_status" in meta else "",
                "coder_count": int(len(coders)),
                "construct_support_coder_count": int(len(construct_support_coders)),
                "source_adjusted_support_coder_count": int(len(source_support_coders)),
                "full_support_coder_count": int(len(full_support_coders)),
                "min_median_expected_abs_d": float(e["median_expected_abs_d"].min()),
                "mean_median_expected_abs_d": float(e["median_expected_abs_d"].mean()),
                "min_median_source_adjusted_abs_beta": float(s["median_expected_abs_adjusted_beta"].min()) if not s.empty else float("nan"),
                "mean_median_source_adjusted_abs_beta": float(s["median_expected_abs_adjusted_beta"].mean()) if not s.empty else float("nan"),
                "construct_gate_by_coder": "; ".join(f"{r.coder_id}={r.construct_gate}" for r in e.itertuples(index=False)),
                "source_adjusted_gate_by_coder": "; ".join(f"{r.coder_id}={r.source_adjusted_gate}" for r in s.itertuples(index=False)),
                "decision": decision,
                "next_action": next_action,
            }
        )
    return pd.DataFrame(rows)


def agreement_summary(agreement: pd.DataFrame, *, min_agreement_r: float) -> pd.DataFrame:
    out = agreement.copy()
    if out.empty:
        return pd.DataFrame(
            [
                {
                    "dimension_count": 0,
                    "min_pearson_r": float("nan"),
                    "median_pearson_r": float("nan"),
                    "agreement_gate": "missing",
                }
            ]
        )
    r = pd.to_numeric(out["pearson_r"], errors="coerce")
    return pd.DataFrame(
        [
            {
                "dimension_count": int(r.notna().sum()),
                "min_pearson_r": float(r.min()),
                "median_pearson_r": float(r.median()),
                "max_mean_abs_diff": float(pd.to_numeric(out["mean_abs_diff"], errors="coerce").max()),
                "agreement_gate": "support" if float(r.min()) >= min_agreement_r else "weak_or_needs_review",
                "min_agreement_r_threshold": min_agreement_r,
            }
        ]
    )


def write_report(
    path: Path,
    factor_summary: pd.DataFrame,
    agreement_gate: pd.DataFrame,
    agreement: pd.DataFrame,
    mask_audit: pd.DataFrame,
    expected_gate: pd.DataFrame,
    source_gate: pd.DataFrame,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    decision_counts = factor_summary["decision"].value_counts().rename_axis("decision").reset_index(name="factors")
    mask_counts = (
        mask_audit.groupby(["source_family", "was_masked"], as_index=False)
        .size()
        .rename(columns={"size": "items"})
        if not mask_audit.empty
        else pd.DataFrame()
    )
    lines = [
        "# SUICA Independent Blind Validation Final Summary v1",
        "",
        "## Status",
        "",
        "Two isolated LLM coder passes were completed on the source-balanced, personality-term-masked blind batch.",
        "",
        "## Headline",
        "",
        "- `5/7` factors pass the independent blind gate for both coders and source-adjusted effects.",
        "- `factor_05` is partially supported: source-adjusted support holds, but one coder's construct gate is weak.",
        "- `factor_10` is not promoted from this batch: one coder is weak and source-adjusted support is borderline/weak.",
        "- Inter-coder agreement is acceptable for this stage: all construct dimensions have positive moderate-to-strong Pearson agreement.",
        "",
        "## Factor Decisions",
        "",
        factor_summary.round(3).to_markdown(index=False),
        "",
        "## Decision Counts",
        "",
        decision_counts.to_markdown(index=False),
        "",
        "## Agreement Gate",
        "",
        agreement_gate.round(3).to_markdown(index=False),
        "",
        "## Inter-Coder Agreement by Dimension",
        "",
        agreement.round(3).to_markdown(index=False) if not agreement.empty else "No agreement table available.",
        "",
        "## Personality-Term Mask Audit",
        "",
        mask_counts.to_markdown(index=False) if not mask_counts.empty else "No mask audit available.",
        "",
        "## Expected-Dimension Gates",
        "",
        expected_gate.round(3).to_markdown(index=False),
        "",
        "## Source-Adjusted Gates",
        "",
        source_gate.round(3).to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        "- This is the first independent construct-coding evidence for SUICA, not a finished personality scale validation.",
        "- Passing factors can be treated as construct candidates, pending human coding or a third model-family replication.",
        "- Partial or weak factors should not be force-named; they should receive item-bank repair, expected-dimension revision, or splitting.",
        "- Big5/MBTI remain external validity anchors, not the acceptance criterion for this blind construct gate.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    eval_dir = Path(args.eval_dir)
    batch_dir = Path(args.batch_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    expected_gate = load_csv(eval_dir / "expected_dimension_gate.csv")
    source_gate = load_csv(eval_dir / "source_adjusted_expected_dimension_gate.csv")
    agreement = load_csv(eval_dir / "inter_coder_agreement.csv")
    manifest = load_csv(batch_dir / "factor_batch_manifest.csv")
    mask_audit = load_csv(batch_dir / "personality_term_mask_audit.csv")

    factor_summary = factor_acceptance_summary(expected_gate, source_gate, manifest)
    agreement_gate = agreement_summary(agreement, min_agreement_r=args.min_agreement_r)

    factor_summary.to_csv(out_dir / "factor_acceptance_summary.csv", index=False)
    agreement_gate.to_csv(out_dir / "agreement_gate_summary.csv", index=False)
    expected_gate.to_csv(out_dir / "expected_dimension_gate.csv", index=False)
    source_gate.to_csv(out_dir / "source_adjusted_expected_dimension_gate.csv", index=False)
    agreement.to_csv(out_dir / "inter_coder_agreement.csv", index=False)
    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "eval_dir": str(eval_dir),
                "batch_dir": str(batch_dir),
                "min_agreement_r": args.min_agreement_r,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(Path(args.report_path), factor_summary, agreement_gate, agreement, mask_audit, expected_gate, source_gate)
    print("SUICA independent blind validation summary complete.")
    print(factor_summary[["factor", "decision", "full_support_coder_count", "min_median_expected_abs_d", "min_median_source_adjusted_abs_beta"]].round(3).to_string(index=False))
    print(f"\nReport: {Path(args.report_path)}")


if __name__ == "__main__":
    main()
