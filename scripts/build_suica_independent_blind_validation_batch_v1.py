#!/usr/bin/env python
"""Build the formal independent blind-validation batch for SUICA factors.

This script promotes the repaired SUICA item-bank workflow from local
auto-control to an external coding package. It selects high and low examples
within each source family, hides factor/pole metadata from coders, and writes
two counterbalanced coder order files plus the hidden key.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_suica_blind_construct_coding_package_v1 import (  # noqa: E402
    CODING_DIMENSIONS,
    score_selected_items,
    stable_text_hash,
)
from scripts.build_suica_rebalanced_repair_package_v1 import (  # noqa: E402
    add_source_family,
    anchor_precode_summary,
    load_status,
    score_range_summary,
    select_within_source_pole,
    source_balance_summary,
    source_pole_counts,
)


SLICE_SCORES = ROOT / "results" / "suica_item_bank_v1" / "slice_scores_with_text.csv"
FACTOR_STATUS = ROOT / "results" / "suica_measurement_framework_v1" / "factor_status_table.csv"
REPAIR_DECISIONS = ROOT / "results" / "suica_factor_repair_audit_v1" / "factor_repair_decisions.csv"
OUT_DIR = ROOT / "results" / "suica_independent_blind_validation_batch_v1"
REPORT_PATH = ROOT / "reports" / "suica_independent_blind_validation_batch_v1.md"


DEFAULT_TARGET_FACTORS = [
    "suica_factor_01",
    "suica_factor_02",
    "suica_factor_03",
    "suica_factor_04",
    "suica_factor_05",
    "suica_factor_06",
    "suica_factor_10",
]
DEFAULT_SOURCE_FAMILIES = ["pandora", "essays"]
FORMAL_INCLUSION_STATUS = {
    "suica_factor_01": "priority_independent_blind_coding",
    "suica_factor_02": "source_balanced_repair_passed",
    "suica_factor_03": "priority_independent_blind_coding",
    "suica_factor_04": "priority_independent_blind_coding",
    "suica_factor_05": "source_balanced_repair_passed",
    "suica_factor_06": "priority_independent_blind_coding",
    "suica_factor_10": "priority_independent_blind_coding",
}
PERSONALITY_TERM_PATTERNS = [
    re.compile(r"(?i)(?<![A-Za-z])(?:INTJ|INTP|ENTJ|ENTP|INFJ|INFP|ENFJ|ENFP|ISTJ|ISFJ|ESTJ|ESFJ|ISTP|ISFP|ESTP|ESFP)(?![A-Za-z])"),
    re.compile(r"(?i)\b(?:MBTI|Myers[- ]?Briggs|Big\s*Five|Big\s*5|OCEAN|Enneagram)\b"),
    re.compile(r"(?i)\b(?:openness|conscientiousness|extraversion|extroversion|agreeableness|neuroticism)\b"),
    re.compile(r"(?i)\b(?:introvert|introverted|introversion|extrovert|extravert|extroverted|extraverted)\b"),
    re.compile(r"(?i)\b(?:personality\s+test|personality\s+type|typing\s+test|type\s+me|typology)\b"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SUICA independent blind-validation batch v1.")
    parser.add_argument("--slice-scores", default=str(SLICE_SCORES))
    parser.add_argument("--factor-status", default=str(FACTOR_STATUS))
    parser.add_argument("--repair-decisions", default=str(REPAIR_DECISIONS))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--target-factor", action="append", default=[], help="Target SUICA factor. Repeatable.")
    parser.add_argument("--source-family", action="append", default=[], help="Source family to balance. Repeatable.")
    parser.add_argument("--examples-per-source-pole", type=int, default=5)
    parser.add_argument("--max-per-scenario", type=int, default=3)
    parser.add_argument("--max-excerpt-chars", type=int, default=520)
    parser.add_argument("--seed", type=int, default=4242)
    parser.add_argument("--include-x", action="store_true", help="Allow x_market source family if selected.")
    return parser.parse_args()


def load_status_with_repair(factor_status: str | Path, repair_decisions: str | Path) -> pd.DataFrame:
    status = load_status(factor_status)
    repair_path = Path(repair_decisions)
    if repair_path.exists():
        decisions = pd.read_csv(repair_path)
        keep = [
            col
            for col in [
                "factor",
                "repair_decision",
                "decision_reason",
                "construct_gate",
                "source_adjusted_gate",
                "stable_anchor_count",
            ]
            if col in decisions.columns
        ]
        status = status.merge(decisions[keep], on="factor", how="left")
    return status


def mask_personality_terms(text: str) -> tuple[str, int]:
    """Mask explicit scale/type clues in coder-facing excerpts."""

    masked = str(text)
    total = 0
    for pattern in PERSONALITY_TERM_PATTERNS:
        masked, count = pattern.subn("[PERSONALITY_TERM]", masked)
        total += count
    return masked, total


def mask_examples_for_blind_coding(examples: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply personality-term masking and return an audit table."""

    out = examples.copy()
    audit_rows: list[dict] = []
    masked_texts: list[str] = []
    for row in out.itertuples(index=False):
        original = str(getattr(row, "text_excerpt", ""))
        masked, count = mask_personality_terms(original)
        masked_texts.append(masked)
        audit_rows.append(
            {
                "factor": getattr(row, "factor", ""),
                "pole": getattr(row, "pole", ""),
                "source_family": getattr(row, "source_family", ""),
                "slice_obs_id": getattr(row, "slice_obs_id", ""),
                "text_hash": getattr(row, "text_hash", ""),
                "masked_term_count": count,
                "was_masked": bool(count > 0),
            }
        )
    out["text_excerpt_original_hash"] = out["text_hash"]
    out["text_excerpt"] = masked_texts
    return out, pd.DataFrame(audit_rows)


def select_formal_examples(
    frame: pd.DataFrame,
    targets: list[str],
    status_lookup: dict[str, dict],
    *,
    source_families: list[str],
    examples_per_source_pole: int,
    max_per_scenario: int,
    max_excerpt_chars: int,
) -> pd.DataFrame:
    """Select source-balanced high/low examples with global text de-duplication."""

    rows: list[pd.DataFrame] = []
    used_hashes: set[str] = set()
    work = frame.copy()
    work["_text_hash_for_dedupe"] = work["slice_text"].map(stable_text_hash)
    for factor in targets:
        available = work.loc[~work["_text_hash_for_dedupe"].isin(used_hashes)].copy()
        selected = select_within_source_pole(
            available,
            factor,
            status_lookup,
            source_families=source_families,
            examples_per_source_pole=examples_per_source_pole,
            max_per_scenario=max_per_scenario,
            max_excerpt_chars=max_excerpt_chars,
        )
        required = len(source_families) * 2 * examples_per_source_pole
        if len(selected) < required:
            raise RuntimeError(f"{factor} selected {len(selected)} rows, expected {required}")
        meta = status_lookup.get(factor, {})
        for col in ["decision_reason", "construct_gate", "source_adjusted_gate", "stable_anchor_count"]:
            selected[col] = meta.get(col, "")
        selected["formal_inclusion_status"] = FORMAL_INCLUSION_STATUS.get(factor, "included_for_independent_blind_validation")
        used_hashes.update(selected["text_hash"].astype(str))
        rows.append(selected)
    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True)
    out["validation_stage"] = "formal_independent_blind_validation"
    return out


def build_independent_blind_items(examples: pd.DataFrame, *, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    shuffled = examples.sample(frac=1.0, random_state=seed).reset_index(drop=True).copy()
    shuffled["blind_item_id"] = [f"SUICA-IB-{idx:04d}" for idx in range(1, len(shuffled) + 1)]
    coder = shuffled[["blind_item_id", "text_excerpt"]].copy()
    for dimension, _description in CODING_DIMENSIONS:
        coder[f"{dimension}_0_to_3"] = ""
    coder["coder_notes"] = ""
    key_cols = [
        "blind_item_id",
        "factor",
        "provisional_name",
        "measurement_role",
        "repair_decision",
        "formal_inclusion_status",
        "decision_reason",
        "construct_gate",
        "source_adjusted_gate",
        "stable_anchor_count",
        "pole",
        "source_family",
        "rank_within_factor_source_pole",
        "scenario",
        "user_id",
        "condition",
        "slice_obs_id",
        "slice_index",
        "token_count",
        "factor_score",
        "text_hash",
        "text_excerpt_original_hash",
        "validation_stage",
    ]
    key_cols = [col for col in key_cols if col in shuffled.columns]
    return coder, shuffled[key_cols + ["text_excerpt"]]


def build_coder_order(coder_items: pd.DataFrame, *, coder_id: str, seed: int) -> pd.DataFrame:
    ordered = coder_items.sample(frac=1.0, random_state=seed).reset_index(drop=True).copy()
    ordered.insert(0, "coder_id", coder_id)
    ordered.insert(1, "coder_order", range(1, len(ordered) + 1))
    return ordered


def build_factor_manifest(key: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for factor, group in key.groupby("factor", sort=True):
        rows.append(
            {
                "factor": factor,
                "provisional_name": group["provisional_name"].dropna().iloc[0] if group["provisional_name"].notna().any() else "",
                "measurement_role": group["measurement_role"].dropna().iloc[0] if group["measurement_role"].notna().any() else "",
                "repair_decision": group["repair_decision"].dropna().iloc[0] if "repair_decision" in group and group["repair_decision"].notna().any() else "",
                "formal_inclusion_status": group["formal_inclusion_status"].dropna().iloc[0] if "formal_inclusion_status" in group and group["formal_inclusion_status"].notna().any() else "",
                "construct_gate": group["construct_gate"].dropna().iloc[0] if "construct_gate" in group and group["construct_gate"].notna().any() else "",
                "source_adjusted_gate": group["source_adjusted_gate"].dropna().iloc[0] if "source_adjusted_gate" in group and group["source_adjusted_gate"].notna().any() else "",
                "items": int(len(group)),
                "source_families": "; ".join(sorted(group["source_family"].astype(str).unique())),
                "poles": "; ".join(sorted(group["pole"].astype(str).unique())),
                "unique_text_hashes": int(group["text_hash"].nunique()),
            }
        )
    return pd.DataFrame(rows)


def write_rubric(path: Path) -> None:
    lines = [
        "# SUICA Independent Construct Coding Rubric v1",
        "",
        "Rate each text excerpt on every dimension from `0` to `3`.",
        "",
        "- `0`: absent or negligible",
        "- `1`: weak or implicit",
        "- `2`: clear and repeated",
        "- `3`: dominant or highly salient",
        "",
        "Coders must not infer hidden factor names, pole labels, source family, dataset, author identity, Big5, or MBTI.",
        "",
        "## Dimensions",
        "",
    ]
    for dimension, description in CODING_DIMENSIONS:
        lines.append(f"- `{dimension}`: {description}")
    lines.extend(
        [
            "",
            "## Coding Discipline",
            "",
            "- Score the excerpt as text behavior, not whether you agree with the content.",
            "- Use the full 0-3 range across the batch.",
            "- Leave `coder_notes` only for ambiguity, off-topic excerpts, or suspected artifacts.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(
    path: Path,
    key: pd.DataFrame,
    counts: pd.DataFrame,
    balance: pd.DataFrame,
    ranges: pd.DataFrame,
    precode: pd.DataFrame,
    manifest: pd.DataFrame,
    mask_audit: pd.DataFrame,
    targets: list[str],
    sources: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SUICA Independent Blind Validation Batch v1",
        "",
        "## Purpose",
        "",
        "This is the formal independent construct-coding batch for the SUICA text-behavior scale route. It is not a repair package and not a Big5/MBTI prediction benchmark. Its purpose is to test whether blinded coders recover the expected narrative/projective construct differences from source-balanced high/low SUICA factor examples.",
        "",
        "## Inclusion Rule",
        "",
        "- Included: factors with prior auto-control support or successful source-balanced repair.",
        "- Excluded: factor_07/factor_08 mixed-method or domain-audit factors, and factor_09 after failed/weak repair.",
        f"- target factors: `{', '.join(targets)}`",
        f"- source families: `{', '.join(sources)}`",
        f"- blind items: `{len(key)}`",
        f"- unique text hashes: `{key['text_hash'].nunique()}`",
        f"- items with masked explicit personality terms: `{int(mask_audit['was_masked'].sum()) if not mask_audit.empty else 0}`",
        "",
        "## Factor Manifest",
        "",
        manifest.to_markdown(index=False) if not manifest.empty else "No factor manifest available.",
        "",
        "## Source x Pole Balance",
        "",
        counts.to_markdown(index=False) if not counts.empty else "No counts available.",
        "",
        "## Balance Summary",
        "",
        balance.to_markdown(index=False) if not balance.empty else "No balance summary available.",
        "",
        "## Score Range Summary",
        "",
        ranges.round(3).to_markdown(index=False) if not ranges.empty else "No score range summary available.",
        "",
        "## Automatic Anchor Precode Summary",
        "",
        precode.round(3).to_markdown(index=False) if not precode.empty else "No precode summary available.",
        "",
        "## Personality-Term Mask Audit",
        "",
        mask_audit.groupby(["source_family", "was_masked"], as_index=False)
        .size()
        .rename(columns={"size": "items"})
        .to_markdown(index=False)
        if not mask_audit.empty
        else "No mask audit available.",
        "",
        "## Acceptance Use",
        "",
        "- The auto-precode output is only a pipeline check.",
        "- Construct validation requires at least two independent coders or two independent LLM coders run without hidden key exposure.",
        "- The next evidence gate is coder agreement plus hidden high/low pole separation on expected dimensions, including source-adjusted effects.",
        "",
        "## Artifacts",
        "",
        "- `results/suica_independent_blind_validation_batch_v1/independent_blind_coding_items.csv`",
        "- `results/suica_independent_blind_validation_batch_v1/coder_A_items.csv`",
        "- `results/suica_independent_blind_validation_batch_v1/coder_B_items.csv`",
        "- `results/suica_independent_blind_validation_batch_v1/independent_blind_coding_key.csv`",
        "- `results/suica_independent_blind_validation_batch_v1/independent_auto_anchor_scores_by_item.csv`",
        "- `results/suica_independent_blind_validation_batch_v1/personality_term_mask_audit.csv`",
        "- `results/suica_independent_blind_validation_batch_v1/independent_construct_coding_rubric.md`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    targets = args.target_factor or DEFAULT_TARGET_FACTORS
    sources = args.source_family or DEFAULT_SOURCE_FAMILIES
    if not args.include_x:
        sources = [source for source in sources if source != "x_market"]

    frame = add_source_family(pd.read_csv(args.slice_scores, dtype={"user_id": str}))
    frame = frame.loc[frame["source_family"].isin(sources)].copy()
    status = load_status_with_repair(args.factor_status, args.repair_decisions)
    status_lookup = status.set_index("factor").to_dict(orient="index")

    examples = select_formal_examples(
        frame,
        targets,
        status_lookup,
        source_families=sources,
        examples_per_source_pole=args.examples_per_source_pole,
        max_per_scenario=args.max_per_scenario,
        max_excerpt_chars=args.max_excerpt_chars,
    )
    examples, mask_audit = mask_examples_for_blind_coding(examples)
    coder_items, key = build_independent_blind_items(examples, seed=args.seed)
    coder_a = build_coder_order(coder_items, coder_id="coder_A", seed=args.seed + 101)
    coder_b = build_coder_order(coder_items, coder_id="coder_B", seed=args.seed + 202)
    anchor_scores = score_selected_items(key)
    counts = source_pole_counts(key)
    balance = source_balance_summary(counts)
    ranges = score_range_summary(examples)
    precode = anchor_precode_summary(anchor_scores)
    manifest = build_factor_manifest(key)

    coder_items.to_csv(out_dir / "independent_blind_coding_items.csv", index=False)
    coder_a.to_csv(out_dir / "coder_A_items.csv", index=False)
    coder_b.to_csv(out_dir / "coder_B_items.csv", index=False)
    key.to_csv(out_dir / "independent_blind_coding_key.csv", index=False)
    anchor_scores.to_csv(out_dir / "independent_auto_anchor_scores_by_item.csv", index=False)
    mask_audit.to_csv(out_dir / "personality_term_mask_audit.csv", index=False)
    counts.to_csv(out_dir / "source_pole_counts.csv", index=False)
    balance.to_csv(out_dir / "source_balance_summary.csv", index=False)
    ranges.to_csv(out_dir / "independent_score_range_summary.csv", index=False)
    precode.to_csv(out_dir / "independent_anchor_precode_summary.csv", index=False)
    manifest.to_csv(out_dir / "factor_batch_manifest.csv", index=False)
    write_rubric(out_dir / "independent_construct_coding_rubric.md")
    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "target_factors": targets,
                "source_families": sources,
                "examples_per_source_pole": args.examples_per_source_pole,
                "max_per_scenario": args.max_per_scenario,
                "max_excerpt_chars": args.max_excerpt_chars,
                "seed": args.seed,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(Path(args.report_path), key, counts, balance, ranges, precode, manifest, mask_audit, targets, sources)
    print("Independent blind validation batch created.")
    print(balance.to_string(index=False))
    print(f"\nReport: {Path(args.report_path).resolve().relative_to(ROOT)}")


if __name__ == "__main__":
    main()
