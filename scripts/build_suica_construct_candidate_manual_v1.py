#!/usr/bin/env python
"""Build a construct-candidate manual from SUICA independent blind evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FINAL_DIR = ROOT / "results" / "suica_independent_blind_validation_final_v1"
EVAL_DIR = ROOT / "results" / "suica_independent_coding_eval_deepseek_AB_full_v1"
ANCHOR_PATH = ROOT / "results" / "suica_narrative_projective_anchor_validation_v2" / "factor_anchor_summary.csv"
BATCH_DIR = ROOT / "results" / "suica_independent_blind_validation_batch_v1"
OUT_DIR = ROOT / "results" / "suica_construct_candidate_manual_v1"
REPORT_PATH = ROOT / "reports" / "suica_construct_candidate_manual_v1.md"


DIMENSION_LABELS = {
    "agency": "agency / active choice",
    "communion": "communion / relational warmth",
    "mentalization": "mentalization / mental-state language",
    "temporal_integration": "temporal integration / autobiographical sequencing",
    "directive_interpersonal": "directive interpersonal stance",
    "self_focus": "self-focus / self-positioning",
    "other_focus": "other-focus / third-person social attention",
    "affect_tension": "affect tension / conflict or distress",
    "redemption_growth": "redemption-growth / recovery framing",
    "social_evaluation": "social evaluation / norm comparison",
    "novelty_play": "novelty-play / exploratory engagement",
}


CONSTRUCT_INTERPRETATION_NOTES = {
    "suica_factor_01": {
        "candidate_label": "comparative abstraction vs situated narrative immersion",
        "manual_note": "High scores read as more abstract/comparative or playful framing and less situated temporal-affective narration.",
    },
    "suica_factor_02": {
        "candidate_label": "self-cognitive evaluative response channel",
        "manual_note": "High scores read as more self-focused, mentalizing, evaluative, and agentic response language.",
    },
    "suica_factor_03": {
        "candidate_label": "self-continuity and exploratory self-positioning",
        "manual_note": "High scores read as more self-focused temporal continuity and exploratory/playful self-positioning, with less other-directed social evaluation.",
    },
    "suica_factor_04": {
        "candidate_label": "third-person relational narrative focus",
        "manual_note": "High scores read as more third-person/social-relational narrative attention, often with affective or evaluative interpersonal content.",
    },
    "suica_factor_05": {
        "candidate_label": "playful task/interest engagement",
        "manual_note": "High scores primarily read as novelty/play engagement, but the construct is not yet stable enough across coders.",
    },
    "suica_factor_06": {
        "candidate_label": "direct conditional advising stance",
        "manual_note": "High scores read as more directive, second-person, conditional interpersonal guidance, with less self-immersed temporal narration.",
    },
    "suica_factor_10": {
        "candidate_label": "desire-intention action channel",
        "manual_note": "Current evidence is unstable across coders; hold this label until item repair or splitting clarifies the construct.",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SUICA construct candidate manual v1.")
    parser.add_argument("--final-dir", default=str(FINAL_DIR))
    parser.add_argument("--eval-dir", default=str(EVAL_DIR))
    parser.add_argument("--anchor-summary", default=str(ANCHOR_PATH))
    parser.add_argument("--batch-dir", default=str(BATCH_DIR))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--dimension-effect-threshold", type=float, default=0.5)
    parser.add_argument("--top-k-anchors", type=int, default=5)
    parser.add_argument("--top-k-dimensions", type=int, default=5)
    parser.add_argument("--example-chars", type=int, default=260)
    return parser.parse_args()


def load_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def evidence_tier(decision: str) -> str:
    if decision == "pass_independent_blind_gate":
        return "construct_candidate"
    if decision == "partial_construct_gate_revise_or_add_items":
        return "repair_candidate"
    return "hold_or_split"


def build_dimension_contrast(pole: pd.DataFrame, *, effect_threshold: float) -> pd.DataFrame:
    rows: list[dict] = []
    for (factor, dimension), group in pole.groupby(["factor", "dimension"], sort=True):
        d = pd.to_numeric(group["cohen_d"], errors="coerce")
        delta = pd.to_numeric(group["high_minus_low"], errors="coerce")
        mean_d = float(d.mean())
        mean_delta = float(delta.mean())
        min_abs_d = float(d.abs().min())
        supporting = int((d.abs() >= effect_threshold).sum())
        if mean_d >= effect_threshold:
            direction = "high_pole"
        elif mean_d <= -effect_threshold:
            direction = "low_pole"
        else:
            direction = "weak_or_mixed"
        rows.append(
            {
                "factor": factor,
                "dimension": dimension,
                "dimension_label": DIMENSION_LABELS.get(dimension, dimension),
                "mean_high_minus_low": mean_delta,
                "mean_cohen_d": mean_d,
                "min_abs_cohen_d_across_coders": min_abs_d,
                "supporting_coder_count_abs_d_ge_threshold": supporting,
                "direction": direction,
            }
        )
    out = pd.DataFrame(rows)
    return out.sort_values(["factor", "mean_cohen_d"], ascending=[True, False])


def signed_dimension_phrase(dimensions: pd.DataFrame, *, direction: str, top_k: int) -> str:
    rows = dimensions.loc[dimensions["direction"].eq(direction)].copy()
    if rows.empty:
        return "none above threshold"
    rows = rows.reindex(rows["mean_cohen_d"].abs().sort_values(ascending=False).index).head(top_k)
    return "; ".join(
        f"{row.dimension_label} (d={row.mean_cohen_d:+.2f})"
        for row in rows.itertuples(index=False)
    )


def top_anchor_phrase(anchor: pd.DataFrame, factor: str, *, top_k: int) -> str:
    rows = anchor.loc[(anchor["factor"].eq(factor)) & (anchor["profile_component"].eq("base_score"))].copy()
    if rows.empty:
        return "no anchor summary"
    rows = rows.sort_values("support_score", ascending=False).head(top_k)
    return "; ".join(
        f"{row.anchor} (median r={row.median_r:+.3f}, scenarios={int(row.scenario_count)})"
        for row in rows.itertuples(index=False)
    )


def build_example_table(coded: pd.DataFrame, acceptance: pd.DataFrame, *, example_chars: int) -> pd.DataFrame:
    factors = acceptance["factor"].tolist()
    rows: list[dict] = []
    key = coded.drop_duplicates("blind_item_id").copy()
    key = key.loc[key["factor"].isin(factors)]
    for factor in factors:
        subset = key.loc[key["factor"].eq(factor)].copy()
        for pole in ["high", "low"]:
            candidates = subset.loc[subset["pole"].eq(pole)].copy()
            if candidates.empty:
                continue
            candidates["_abs_score"] = pd.to_numeric(candidates["factor_score"], errors="coerce").abs()
            row = candidates.sort_values("_abs_score", ascending=False).iloc[0]
            text = str(row["text_excerpt"]).replace("\n", " ")
            if len(text) > example_chars:
                text = text[: example_chars - 1].rstrip() + "..."
            rows.append(
                {
                    "factor": factor,
                    "pole": pole,
                    "blind_item_id": row["blind_item_id"],
                    "source_family": row["source_family"],
                    "scenario": row["scenario"],
                    "factor_score": float(row["factor_score"]),
                    "excerpt": text,
                }
            )
    return pd.DataFrame(rows)


def build_construct_cards(
    acceptance: pd.DataFrame,
    dimension_contrast: pd.DataFrame,
    anchor: pd.DataFrame,
    examples: pd.DataFrame,
    *,
    top_k_anchors: int,
    top_k_dimensions: int,
) -> pd.DataFrame:
    rows: list[dict] = []
    for row in acceptance.itertuples(index=False):
        factor = row.factor
        notes = CONSTRUCT_INTERPRETATION_NOTES.get(factor, {})
        dims = dimension_contrast.loc[dimension_contrast["factor"].eq(factor)].copy()
        high_desc = signed_dimension_phrase(dims, direction="high_pole", top_k=top_k_dimensions)
        low_desc = signed_dimension_phrase(dims, direction="low_pole", top_k=top_k_dimensions)
        top_dims = dims.reindex(dims["mean_cohen_d"].abs().sort_values(ascending=False).index).head(top_k_dimensions)
        top_dim_phrase = "; ".join(
            f"{dim.dimension_label} (d={dim.mean_cohen_d:+.2f})"
            for dim in top_dims.itertuples(index=False)
        )
        high_example = examples.loc[(examples["factor"].eq(factor)) & (examples["pole"].eq("high"))]
        low_example = examples.loc[(examples["factor"].eq(factor)) & (examples["pole"].eq("low"))]
        rows.append(
            {
                "factor": factor,
                "evidence_tier": evidence_tier(row.decision),
                "current_provisional_name": row.provisional_name,
                "recommended_construct_label": notes.get("candidate_label", row.provisional_name),
                "manual_note": notes.get("manual_note", ""),
                "decision": row.decision,
                "next_action": row.next_action,
                "high_pole_coder_signature": high_desc,
                "low_pole_coder_signature": low_desc,
                "strongest_blind_dimensions": top_dim_phrase,
                "narrative_projective_anchors": top_anchor_phrase(anchor, factor, top_k=top_k_anchors),
                "coder_count": int(row.coder_count),
                "full_support_coder_count": int(row.full_support_coder_count),
                "min_median_expected_abs_d": float(row.min_median_expected_abs_d),
                "min_median_source_adjusted_abs_beta": float(row.min_median_source_adjusted_abs_beta),
                "high_example_id": high_example["blind_item_id"].iloc[0] if not high_example.empty else "",
                "high_example_excerpt": high_example["excerpt"].iloc[0] if not high_example.empty else "",
                "low_example_id": low_example["blind_item_id"].iloc[0] if not low_example.empty else "",
                "low_example_excerpt": low_example["excerpt"].iloc[0] if not low_example.empty else "",
            }
        )
    return pd.DataFrame(rows)


def build_repair_queue(cards: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for row in cards.itertuples(index=False):
        if row.evidence_tier == "construct_candidate":
            action = "manual_review_then_external_validity"
            priority = "medium"
            rationale = "passed two-coder blind and source-adjusted gates"
        elif row.evidence_tier == "repair_candidate":
            action = "add_items_and_retest_expected_dimensions"
            priority = "high"
            rationale = "partial support; one coder construct gate weak"
        else:
            action = "split_rename_or_hold_before_retesting"
            priority = "high"
            rationale = "failed full two-coder/source-adjusted promotion gate"
        rows.append(
            {
                "factor": row.factor,
                "evidence_tier": row.evidence_tier,
                "recommended_construct_label": row.recommended_construct_label,
                "priority": priority,
                "action": action,
                "rationale": rationale,
            }
        )
    return pd.DataFrame(rows)


def write_markdown_report(
    path: Path,
    cards: pd.DataFrame,
    repair_queue: pd.DataFrame,
    dimension_contrast: pd.DataFrame,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = cards["evidence_tier"].value_counts().rename_axis("evidence_tier").reset_index(name="factors")
    lines = [
        "# SUICA Construct Candidate Manual v1",
        "",
        "## Purpose",
        "",
        "This manual converts SUICA independent blind-coding evidence into construct-candidate cards. It is a scale-development artifact, not a final clinical/personality assessment manual.",
        "",
        "## Evidence Tiers",
        "",
        counts.to_markdown(index=False),
        "",
        "## Candidate Cards",
        "",
    ]
    for row in cards.itertuples(index=False):
        lines.extend(
            [
                f"### {row.factor}: {row.recommended_construct_label}",
                "",
                f"- evidence tier: `{row.evidence_tier}`",
                f"- previous provisional name: `{row.current_provisional_name}`",
                f"- decision: `{row.decision}`",
                f"- support: `{row.full_support_coder_count}/{row.coder_count}` coders passed both construct and source-adjusted gates",
                f"- minimum blind effect: `d={row.min_median_expected_abs_d:.3f}`",
                f"- minimum source-adjusted effect: `beta={row.min_median_source_adjusted_abs_beta:.3f}`",
                f"- interpretation note: {row.manual_note}",
                f"- high-pole coder signature: {row.high_pole_coder_signature}",
                f"- low-pole coder signature: {row.low_pole_coder_signature}",
                f"- narrative/projective anchors: {row.narrative_projective_anchors}",
                f"- next action: `{row.next_action}`",
                "",
                "High-pole example:",
                "",
                f"> `{row.high_example_id}` {row.high_example_excerpt}",
                "",
                "Low-pole example:",
                "",
                f"> `{row.low_example_id}` {row.low_example_excerpt}",
                "",
            ]
        )
    lines.extend(
        [
            "## Repair Queue",
            "",
            repair_queue.to_markdown(index=False),
            "",
            "## Dimension Contrast Table",
            "",
            dimension_contrast.round(3).to_markdown(index=False),
            "",
            "## Use Limits",
            "",
            "- Treat the five passed factors as construct candidates, not final validated personality dimensions.",
            "- `factor_05` and `factor_10` must not be promoted without item repair and retesting.",
            "- Big5/MBTI are external validity anchors only; they are not the acceptance rule for this manual.",
            "- Human coding or third-model-family replication is still needed before stronger psychometric claims.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    acceptance = load_csv(Path(args.final_dir) / "factor_acceptance_summary.csv")
    pole = load_csv(Path(args.eval_dir) / "pole_separation_by_factor_dimension.csv")
    coded = load_csv(Path(args.eval_dir) / "merged_coder_key_ratings.csv")
    anchor = load_csv(args.anchor_summary)

    dimension_contrast = build_dimension_contrast(pole, effect_threshold=args.dimension_effect_threshold)
    examples = build_example_table(coded, acceptance, example_chars=args.example_chars)
    cards = build_construct_cards(
        acceptance,
        dimension_contrast,
        anchor,
        examples,
        top_k_anchors=args.top_k_anchors,
        top_k_dimensions=args.top_k_dimensions,
    )
    repair_queue = build_repair_queue(cards)

    cards.to_csv(out_dir / "construct_candidate_cards.csv", index=False)
    dimension_contrast.to_csv(out_dir / "dimension_contrast_summary.csv", index=False)
    examples.to_csv(out_dir / "construct_example_excerpts.csv", index=False)
    repair_queue.to_csv(out_dir / "construct_repair_queue.csv", index=False)
    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "final_dir": str(Path(args.final_dir)),
                "eval_dir": str(Path(args.eval_dir)),
                "anchor_summary": str(Path(args.anchor_summary)),
                "dimension_effect_threshold": args.dimension_effect_threshold,
                "top_k_anchors": args.top_k_anchors,
                "top_k_dimensions": args.top_k_dimensions,
                "example_chars": args.example_chars,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_markdown_report(Path(args.report_path), cards, repair_queue, dimension_contrast)
    print("SUICA construct candidate manual complete.")
    print(cards[["factor", "evidence_tier", "recommended_construct_label", "decision"]].to_string(index=False))
    print(f"\nReport: {Path(args.report_path)}")


if __name__ == "__main__":
    main()
