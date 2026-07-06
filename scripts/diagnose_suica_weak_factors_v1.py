#!/usr/bin/env python
"""Diagnose SUICA factors that failed or partially passed blind validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "results" / "suica_independent_coding_eval_deepseek_AB_full_v1"
FINAL_DIR = ROOT / "results" / "suica_independent_blind_validation_final_v1"
MANUAL_DIR = ROOT / "results" / "suica_construct_candidate_manual_v1"
OUT_DIR = ROOT / "results" / "suica_weak_factor_diagnosis_v1"
REPORT_PATH = ROOT / "reports" / "suica_weak_factor_diagnosis_v1.md"


DIMENSIONS = [
    "agency",
    "communion",
    "mentalization",
    "temporal_integration",
    "directive_interpersonal",
    "self_focus",
    "other_focus",
    "affect_tension",
    "redemption_growth",
    "social_evaluation",
    "novelty_play",
]


EXPECTED_DIMENSIONS = {
    "suica_factor_05": ["novelty_play", "agency"],
    "suica_factor_10": ["mentalization", "directive_interpersonal", "agency"],
}


TARGET_FACTORS = ["suica_factor_05", "suica_factor_10"]


REPAIR_NOTES = {
    "suica_factor_05": {
        "diagnosis": "expected_dimension_overbroad",
        "recommended_change": "treat as novelty-play / structured interest engagement; remove agency as a required gate dimension for now",
        "repair_action": "expand high/low item bank around novelty_play while balancing source, then retest with expected dimensions novelty_play plus optional redemption_growth",
    },
    "suica_factor_10": {
        "diagnosis": "mixed_or_overlapping_construct",
        "recommended_change": "do not promote desire-intention label; split directive-interpersonal action from mentalization/agency-growth residue",
        "repair_action": "split high-pole items into directive advice vs agency-growth/mentalization subsets and test against factor_06 overlap before renaming",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Diagnose weak SUICA factors v1.")
    parser.add_argument("--eval-dir", default=str(EVAL_DIR))
    parser.add_argument("--final-dir", default=str(FINAL_DIR))
    parser.add_argument("--manual-dir", default=str(MANUAL_DIR))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--target-factor", action="append", default=[])
    parser.add_argument("--blind-d-threshold", type=float, default=0.5)
    parser.add_argument("--source-beta-threshold", type=float, default=0.3)
    parser.add_argument("--top-disagreement-items", type=int, default=8)
    return parser.parse_args()


def load_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def load_inputs(eval_dir: Path, final_dir: Path, manual_dir: Path) -> dict[str, pd.DataFrame]:
    return {
        "coded": load_csv(eval_dir / "merged_coder_key_ratings.csv"),
        "pole": load_csv(eval_dir / "pole_separation_by_factor_dimension.csv"),
        "source_adjusted": load_csv(eval_dir / "source_adjusted_pole_effects.csv"),
        "expected_gate": load_csv(eval_dir / "expected_dimension_gate.csv"),
        "source_gate": load_csv(eval_dir / "source_adjusted_expected_dimension_gate.csv"),
        "acceptance": load_csv(final_dir / "factor_acceptance_summary.csv"),
        "cards": load_csv(manual_dir / "construct_candidate_cards.csv"),
        "dimension_contrast": load_csv(manual_dir / "dimension_contrast_summary.csv"),
    }


def dimension_repair_diagnostics(
    pole: pd.DataFrame,
    source_adjusted: pd.DataFrame,
    *,
    targets: list[str],
    blind_d_threshold: float,
    source_beta_threshold: float,
) -> pd.DataFrame:
    source_adjusted = source_adjusted.rename(columns={"high_minus_low_source_adjusted": "source_adjusted_beta"})
    rows: list[dict] = []
    for factor in targets:
        expected = set(EXPECTED_DIMENSIONS.get(factor, []))
        for dimension in DIMENSIONS:
            p = pole.loc[(pole["factor"].eq(factor)) & (pole["dimension"].eq(dimension))].copy()
            s = source_adjusted.loc[(source_adjusted["factor"].eq(factor)) & (source_adjusted["dimension"].eq(dimension))].copy()
            if p.empty:
                continue
            d = pd.to_numeric(p["cohen_d"], errors="coerce")
            beta = pd.to_numeric(s["source_adjusted_beta"], errors="coerce") if not s.empty else pd.Series(dtype=float)
            blind_support = int((d.abs() >= blind_d_threshold).sum())
            source_support = int((beta.abs() >= source_beta_threshold).sum()) if not beta.empty else 0
            if blind_support == 2 and source_support == 2:
                status = "stable_candidate_dimension"
            elif dimension in expected and (blind_support < 2 or source_support < 2):
                status = "expected_dimension_weak"
            elif blind_support >= 1 or source_support >= 1:
                status = "secondary_or_coder_specific"
            else:
                status = "not_supported"
            rows.append(
                {
                    "factor": factor,
                    "dimension": dimension,
                    "was_expected_dimension": bool(dimension in expected),
                    "blind_support_coder_count": blind_support,
                    "source_adjusted_support_coder_count": source_support,
                    "mean_cohen_d": float(d.mean()),
                    "min_abs_cohen_d": float(d.abs().min()),
                    "mean_source_adjusted_beta": float(beta.mean()) if not beta.empty else float("nan"),
                    "min_abs_source_adjusted_beta": float(beta.abs().min()) if not beta.empty else float("nan"),
                    "status": status,
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["factor", "status", "blind_support_coder_count", "source_adjusted_support_coder_count", "min_abs_cohen_d"],
        ascending=[True, True, False, False, False],
    )


def source_pole_dimension_contrasts(coded: pd.DataFrame, *, targets: list[str]) -> pd.DataFrame:
    rows: list[dict] = []
    subset = coded.loc[coded["factor"].isin(targets)].copy()
    for factor in targets:
        factor_rows = subset.loc[subset["factor"].eq(factor)].copy()
        for coder_id in sorted(factor_rows["coder_id"].dropna().unique()):
            coder_rows = factor_rows.loc[factor_rows["coder_id"].eq(coder_id)]
            for source_family in sorted(coder_rows["source_family"].dropna().unique()):
                source_rows = coder_rows.loc[coder_rows["source_family"].eq(source_family)]
                for dimension in DIMENSIONS:
                    col = f"{dimension}_0_to_3"
                    high = pd.to_numeric(source_rows.loc[source_rows["pole"].eq("high"), col], errors="coerce")
                    low = pd.to_numeric(source_rows.loc[source_rows["pole"].eq("low"), col], errors="coerce")
                    if high.empty or low.empty:
                        continue
                    rows.append(
                        {
                            "factor": factor,
                            "coder_id": coder_id,
                            "source_family": source_family,
                            "dimension": dimension,
                            "high_n": int(high.notna().sum()),
                            "low_n": int(low.notna().sum()),
                            "high_mean": float(high.mean()),
                            "low_mean": float(low.mean()),
                            "high_minus_low": float(high.mean() - low.mean()),
                        }
                    )
    return pd.DataFrame(rows).sort_values(["factor", "coder_id", "source_family", "high_minus_low"], ascending=[True, True, True, False])


def item_disagreement_diagnostics(coded: pd.DataFrame, *, targets: list[str], top_n: int) -> pd.DataFrame:
    rows: list[dict] = []
    rating_cols = [f"{dimension}_0_to_3" for dimension in DIMENSIONS]
    expected_cols = {factor: [f"{dim}_0_to_3" for dim in EXPECTED_DIMENSIONS.get(factor, [])] for factor in targets}
    for factor in targets:
        factor_rows = coded.loc[coded["factor"].eq(factor)].copy()
        for blind_id, group in factor_rows.groupby("blind_item_id", sort=True):
            if group["coder_id"].nunique() < 2:
                continue
            a = group.iloc[0]
            b = group.iloc[1]
            all_diff = (pd.to_numeric(a[rating_cols], errors="coerce") - pd.to_numeric(b[rating_cols], errors="coerce")).abs()
            expected = expected_cols.get(factor, [])
            expected_diff = (
                (pd.to_numeric(a[expected], errors="coerce") - pd.to_numeric(b[expected], errors="coerce")).abs()
                if expected
                else pd.Series(dtype=float)
            )
            text = str(a.get("text_excerpt", "")).replace("\n", " ")
            if len(text) > 240:
                text = text[:239].rstrip() + "..."
            rows.append(
                {
                    "factor": factor,
                    "blind_item_id": blind_id,
                    "pole": a.get("pole", ""),
                    "source_family": a.get("source_family", ""),
                    "scenario": a.get("scenario", ""),
                    "mean_abs_diff_all_dimensions": float(all_diff.mean()),
                    "max_abs_diff_all_dimensions": float(all_diff.max()),
                    "mean_abs_diff_expected_dimensions": float(expected_diff.mean()) if len(expected_diff) else float("nan"),
                    "factor_score": float(a.get("factor_score", float("nan"))),
                    "excerpt": text,
                }
            )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return (
        out.sort_values(["factor", "mean_abs_diff_expected_dimensions", "mean_abs_diff_all_dimensions"], ascending=[True, False, False])
        .groupby("factor", as_index=False)
        .head(top_n)
    )


def factor_repair_plan(diagnostics: pd.DataFrame, acceptance: pd.DataFrame, cards: pd.DataFrame, *, targets: list[str]) -> pd.DataFrame:
    rows: list[dict] = []
    for factor in targets:
        diag = diagnostics.loc[diagnostics["factor"].eq(factor)].copy()
        stable_dims = diag.loc[diag["status"].eq("stable_candidate_dimension"), "dimension"].tolist()
        weak_expected = diag.loc[diag["status"].eq("expected_dimension_weak"), "dimension"].tolist()
        acc = acceptance.loc[acceptance["factor"].eq(factor)].head(1)
        card = cards.loc[cards["factor"].eq(factor)].head(1)
        note = REPAIR_NOTES.get(factor, {})
        rows.append(
            {
                "factor": factor,
                "current_decision": acc["decision"].iloc[0] if not acc.empty else "",
                "current_label": card["recommended_construct_label"].iloc[0] if not card.empty else "",
                "diagnosis": note.get("diagnosis", ""),
                "stable_candidate_dimensions": "; ".join(stable_dims) if stable_dims else "none",
                "weak_expected_dimensions": "; ".join(weak_expected) if weak_expected else "none",
                "recommended_change": note.get("recommended_change", ""),
                "repair_action": note.get("repair_action", ""),
            }
        )
    return pd.DataFrame(rows)


def write_report(
    path: Path,
    plan: pd.DataFrame,
    diagnostics: pd.DataFrame,
    source_contrasts: pd.DataFrame,
    disagreement: pd.DataFrame,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    top_source = source_contrasts.loc[source_contrasts["dimension"].isin(["novelty_play", "agency", "mentalization", "directive_interpersonal", "redemption_growth"])].copy()
    lines = [
        "# SUICA Weak Factor Diagnosis v1",
        "",
        "## Purpose",
        "",
        "Diagnose why `factor_05` and `factor_10` did not cleanly pass the two-coder independent blind gate, without rerunning LLM coding.",
        "",
        "## Repair Plan",
        "",
        plan.to_markdown(index=False),
        "",
        "## Dimension Diagnostics",
        "",
        diagnostics.round(3).to_markdown(index=False),
        "",
        "## Source x Pole Contrasts for Target Dimensions",
        "",
        top_source.round(3).to_markdown(index=False) if not top_source.empty else "No source-pole contrasts.",
        "",
        "## High-Disagreement Items",
        "",
        disagreement.round(3).to_markdown(index=False) if not disagreement.empty else "No item disagreement rows.",
        "",
        "## Interpretation",
        "",
        "- `factor_05` is not a broad agency/interest construct yet; the stable signal is narrower and mainly novelty-play.",
        "- `factor_10` overlaps with directive interpersonal/action framing and is not stable as a mentalization/agency residual factor.",
        "- Both repairs should happen at the item-bank and expected-dimension level before any further external validity claims.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    targets = args.target_factor or TARGET_FACTORS
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    inputs = load_inputs(Path(args.eval_dir), Path(args.final_dir), Path(args.manual_dir))
    diagnostics = dimension_repair_diagnostics(
        inputs["pole"],
        inputs["source_adjusted"],
        targets=targets,
        blind_d_threshold=args.blind_d_threshold,
        source_beta_threshold=args.source_beta_threshold,
    )
    source_contrasts = source_pole_dimension_contrasts(inputs["coded"], targets=targets)
    disagreement = item_disagreement_diagnostics(inputs["coded"], targets=targets, top_n=args.top_disagreement_items)
    plan = factor_repair_plan(diagnostics, inputs["acceptance"], inputs["cards"], targets=targets)

    diagnostics.to_csv(out_dir / "dimension_repair_diagnostics.csv", index=False)
    source_contrasts.to_csv(out_dir / "source_pole_dimension_contrasts.csv", index=False)
    disagreement.to_csv(out_dir / "high_disagreement_items.csv", index=False)
    plan.to_csv(out_dir / "factor_repair_plan.csv", index=False)
    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "eval_dir": str(Path(args.eval_dir)),
                "final_dir": str(Path(args.final_dir)),
                "manual_dir": str(Path(args.manual_dir)),
                "targets": targets,
                "blind_d_threshold": args.blind_d_threshold,
                "source_beta_threshold": args.source_beta_threshold,
                "top_disagreement_items": args.top_disagreement_items,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(Path(args.report_path), plan, diagnostics, source_contrasts, disagreement)
    print("SUICA weak factor diagnosis complete.")
    print(plan.to_string(index=False))
    print(f"\nReport: {Path(args.report_path)}")


if __name__ == "__main__":
    main()
