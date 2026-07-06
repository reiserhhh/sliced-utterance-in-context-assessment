#!/usr/bin/env python
"""Build a blind construct-coding package for SUICA factor validation.

The package separates coder-facing text examples from the answer key. Coders
rate narrative/projective dimensions without seeing SUICA factor names, poles,
or scores. The hidden key and automatic anchor contrasts are used afterward to
test whether blind ratings reconstruct the factor interpretations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_narrative_projective_anchor_validation_v2 import score_text_anchors  # noqa: E402

SLICE_SCORES = ROOT / "results" / "suica_item_bank_v1" / "slice_scores_with_text.csv"
FACTOR_STATUS = ROOT / "results" / "suica_measurement_framework_v1" / "factor_status_table.csv"
ANCHOR_SUMMARY = ROOT / "results" / "suica_narrative_projective_anchor_validation_v2" / "factor_anchor_summary.csv"
OUT_DIR = ROOT / "results" / "suica_blind_construct_coding_package_v1"
REPORT_PATH = ROOT / "reports" / "suica_blind_construct_coding_package_v1.md"


CODING_DIMENSIONS = [
    ("agency", "Degree of active choice, control, goal pursuit, or self-directed action."),
    ("communion", "Degree of warmth, care, affiliation, support, or relationship orientation."),
    ("mentalization", "Degree of explicit mental-state language: think, feel, know, want, understand."),
    ("temporal_integration", "Degree of past/future sequencing and autobiographical continuity."),
    ("directive_interpersonal", "Degree of direct advice, second-person guidance, or instruction."),
    ("self_focus", "Degree of first-person self-reference and self-positioning."),
    ("other_focus", "Degree of focus on other people, groups, or third-person social actors."),
    ("affect_tension", "Degree of negative affect, uncertainty, conflict, or threat."),
    ("redemption_growth", "Degree of improvement, learning, recovery, or growth after difficulty."),
    ("social_evaluation", "Degree of comparison, judgment, status, norm, or social evaluation."),
    ("novelty_play", "Degree of play, exploration, novelty, creative/task engagement."),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SUICA blind construct-coding package v1.")
    parser.add_argument("--slice-scores", default=str(SLICE_SCORES))
    parser.add_argument("--factor-status", default=str(FACTOR_STATUS))
    parser.add_argument("--anchor-summary", default=str(ANCHOR_SUMMARY))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--examples-per-pole", type=int, default=8)
    parser.add_argument("--max-per-scenario", type=int, default=3)
    parser.add_argument("--max-excerpt-chars", type=int, default=520)
    parser.add_argument("--quantile", type=float, default=0.10)
    parser.add_argument("--seed", type=int, default=314)
    parser.add_argument("--include-x", action="store_true")
    return parser.parse_args()


def factor_cols(frame: pd.DataFrame) -> list[str]:
    return [
        col
        for col in frame.columns
        if col.startswith("suica_factor_")
        and not col.endswith("_condition_mean")
        and not col.endswith("_centered")
    ]


def clean_excerpt(text: str, *, max_chars: int) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    text = text.replace("|", "/")
    if len(text) > max_chars:
        return text[: max_chars - 1].rstrip() + "..."
    return text


def stable_text_hash(text: str) -> str:
    normalized = re.sub(r"\s+", " ", str(text or "").strip().lower())
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]


def source_family(scenario: str) -> str:
    if str(scenario).startswith("pandora"):
        return "pandora"
    if str(scenario).startswith("essays"):
        return "essays"
    if str(scenario).startswith("x_"):
        return "x_market"
    return "other"


def anchor_base_name(anchor: str) -> str:
    name = str(anchor)
    for suffix in ["_condition_amp", "_mean", "_sd"]:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def select_extreme_examples(
    frame: pd.DataFrame,
    factors: list[str],
    status: pd.DataFrame,
    *,
    examples_per_pole: int,
    max_per_scenario: int,
    max_excerpt_chars: int,
) -> pd.DataFrame:
    status_lookup = status.set_index("factor").to_dict(orient="index")
    rows: list[dict] = []
    for factor in factors:
        score_col = f"{factor}_centered" if f"{factor}_centered" in frame.columns else factor
        factor_seen_hashes: set[str] = set()
        for pole, ascending in [("low", True), ("high", False)]:
            ranked = frame.sort_values(score_col, ascending=ascending).copy()
            scenario_counts: dict[str, int] = {}
            selected: list[pd.Series] = []
            for _, row in ranked.iterrows():
                scenario = str(row["scenario"])
                text_hash = stable_text_hash(row.get("slice_text", ""))
                if text_hash in factor_seen_hashes:
                    continue
                if scenario_counts.get(scenario, 0) >= max_per_scenario:
                    continue
                selected.append(row)
                scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
                factor_seen_hashes.add(text_hash)
                if len(selected) >= examples_per_pole:
                    break
            if len(selected) < examples_per_pole:
                for _, row in ranked.iterrows():
                    text_hash = stable_text_hash(row.get("slice_text", ""))
                    if text_hash in factor_seen_hashes:
                        continue
                    selected.append(row)
                    factor_seen_hashes.add(text_hash)
                    if len(selected) >= examples_per_pole:
                        break
            for rank, row in enumerate(selected, start=1):
                meta = status_lookup.get(factor, {})
                score = row.get(score_col)
                rows.append(
                    {
                        "factor": factor,
                        "provisional_name": meta.get("provisional_name", ""),
                        "measurement_role": meta.get("measurement_role", ""),
                        "pole": pole,
                        "rank_within_factor_pole": rank,
                        "scenario": row.get("scenario"),
                        "source_family": source_family(row.get("scenario")),
                        "user_id": row.get("user_id"),
                        "condition": row.get("condition"),
                        "slice_obs_id": row.get("slice_obs_id"),
                        "slice_index": row.get("slice_index"),
                        "token_count": row.get("token_count"),
                        "factor_score": float(score) if pd.notna(score) else np.nan,
                        "text_hash": stable_text_hash(row.get("slice_text", "")),
                        "text_excerpt": clean_excerpt(row.get("slice_text", ""), max_chars=max_excerpt_chars),
                    }
                )
    return pd.DataFrame(rows)


def build_blind_items(examples: pd.DataFrame, *, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    shuffled = examples.sample(frac=1.0, random_state=seed).reset_index(drop=True).copy()
    shuffled["blind_item_id"] = [f"SUICA-BC-{idx:04d}" for idx in range(1, len(shuffled) + 1)]
    coder = shuffled[["blind_item_id", "text_excerpt"]].copy()
    for dimension, _description in CODING_DIMENSIONS:
        coder[f"{dimension}_0_to_3"] = ""
    coder["coder_notes"] = ""
    key_cols = [
        "blind_item_id",
        "factor",
        "provisional_name",
        "measurement_role",
        "pole",
        "rank_within_factor_pole",
        "scenario",
        "source_family",
        "user_id",
        "condition",
        "slice_obs_id",
        "slice_index",
        "token_count",
        "factor_score",
        "text_hash",
    ]
    return coder, shuffled[key_cols + ["text_excerpt"]]


def score_selected_items(key: pd.DataFrame) -> pd.DataFrame:
    anchor_rows = []
    for row in key.itertuples(index=False):
        anchors = score_text_anchors(row.text_excerpt)
        anchors["blind_item_id"] = row.blind_item_id
        anchor_rows.append(anchors)
    return key.merge(pd.DataFrame(anchor_rows), on="blind_item_id", how="left")


def full_pole_anchor_contrast(frame: pd.DataFrame, factors: list[str], *, quantile: float) -> pd.DataFrame:
    anchor_frame = pd.DataFrame([score_text_anchors(text) for text in frame["slice_text"].fillna("")])
    source = pd.concat([frame.reset_index(drop=True), anchor_frame], axis=1)
    anchors = [
        col
        for col in anchor_frame.columns
        if col.endswith("_rate") or col.endswith("_balance") or col.endswith("_blend") or col == "token_count_anchor"
    ]
    rows: list[dict] = []
    for factor in factors:
        score_col = f"{factor}_centered" if f"{factor}_centered" in source.columns else factor
        low_cut = source[score_col].quantile(quantile)
        high_cut = source[score_col].quantile(1.0 - quantile)
        low = source.loc[source[score_col].le(low_cut)].copy()
        high = source.loc[source[score_col].ge(high_cut)].copy()
        for anchor in anchors:
            low_values = pd.to_numeric(low[anchor], errors="coerce").dropna().to_numpy(float)
            high_values = pd.to_numeric(high[anchor], errors="coerce").dropna().to_numpy(float)
            if len(low_values) < 3 or len(high_values) < 3:
                continue
            pooled_sd = np.sqrt((np.var(low_values) + np.var(high_values)) / 2.0)
            delta = float(np.mean(high_values) - np.mean(low_values))
            rows.append(
                {
                    "factor": factor,
                    "anchor": anchor,
                    "low_n": int(len(low_values)),
                    "high_n": int(len(high_values)),
                    "low_mean": float(np.mean(low_values)),
                    "high_mean": float(np.mean(high_values)),
                    "high_minus_low": delta,
                    "cohen_d": float(delta / pooled_sd) if pooled_sd > 1e-12 else np.nan,
                    "quantile": quantile,
                }
            )
    return pd.DataFrame(rows).sort_values(["factor", "cohen_d"], ascending=[True, False])


def build_alignment_summary(contrast: pd.DataFrame, anchor_summary: pd.DataFrame, *, top_k: int = 6) -> pd.DataFrame:
    expected = (
        anchor_summary.loc[anchor_summary["profile_component"].eq("base_score")]
        .sort_values(["factor", "support_score"], ascending=[True, False])
        .groupby("factor")
        .head(top_k)
        .copy()
    )
    expected["anchor_base"] = expected["anchor"].map(anchor_base_name)
    contrast = contrast.copy()
    contrast["anchor_base"] = contrast["anchor"].map(anchor_base_name)
    merged = expected.merge(contrast, on=["factor", "anchor_base"], how="left", suffixes=("_expected", "_observed"))
    merged["expected_direction"] = np.sign(merged["median_r"])
    merged["observed_direction"] = np.sign(merged["high_minus_low"])
    merged["direction_match"] = merged["expected_direction"].eq(merged["observed_direction"])
    rows: list[dict] = []
    for factor, group in merged.groupby("factor", sort=True):
        usable = group.dropna(subset=["high_minus_low"]).copy()
        if usable.empty:
            continue
        top = usable.sort_values("support_score", ascending=False).head(top_k)
        rows.append(
            {
                "factor": factor,
                "checked_anchors": int(len(top)),
                "direction_match_rate": float(top["direction_match"].mean()),
                "median_abs_cohen_d": float(top["cohen_d"].abs().median()),
                "mean_abs_cohen_d": float(top["cohen_d"].abs().mean()),
                "top_expected_anchors": "; ".join(top["anchor_expected"].astype(str).tolist()),
                "top_observed_directions": "; ".join(
                    f"{row.anchor_expected}->{row.anchor_observed}:{row.high_minus_low:+.3f}"
                    for row in top.itertuples(index=False)
                ),
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=[
                "factor",
                "checked_anchors",
                "direction_match_rate",
                "median_abs_cohen_d",
                "mean_abs_cohen_d",
                "top_expected_anchors",
                "top_observed_directions",
            ]
        )
    return pd.DataFrame(rows).sort_values(["direction_match_rate", "median_abs_cohen_d"], ascending=False)


def write_rubric(path: Path) -> None:
    lines = [
        "# SUICA Blind Construct Coding Rubric v1",
        "",
        "## Coder Task",
        "",
        "Rate each text excerpt without using any SUICA factor name, pole, score, Big5 label, or MBTI label. Use the text alone.",
        "",
        "Scale for each dimension:",
        "",
        "- `0`: absent or not inferable",
        "- `1`: weak / incidental",
        "- `2`: clear but not dominant",
        "- `3`: dominant feature of the excerpt",
        "",
        "## Dimensions",
        "",
    ]
    for dimension, description in CODING_DIMENSIONS:
        lines.append(f"- `{dimension}`: {description}")
    lines.extend(
        [
            "",
            "## Validation Logic",
            "",
            "After coding, merge coder ratings with `blind_coding_key.csv`. A factor interpretation is supported if high-vs-low poles differ in the theoretically expected dimensions while source family and text length do not fully explain the effect.",
            "",
            "Do not rename a factor from one impressive excerpt. A factor name should be based on repeated high/low contrast across multiple users and scenarios.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(
    path: Path,
    coder_items: pd.DataFrame,
    key: pd.DataFrame,
    alignment: pd.DataFrame,
    selected_anchor_scores: pd.DataFrame,
    contrast: pd.DataFrame,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pole_counts = key.groupby(["factor", "pole"], as_index=False).size()
    source_counts = key.groupby(["source_family"], as_index=False).size()
    top_alignment = alignment.head(12).copy()
    top_selected = (
        selected_anchor_scores.groupby(["factor", "pole"], as_index=False)
        .agg(
            items=("blind_item_id", "count"),
            agency=("agency_rate", "mean"),
            mentalization=("mentalization_rate", "mean"),
            second_person=("second_person_rate", "mean"),
            third_person=("third_person_rate", "mean"),
            directive_blend=("directive_interpersonal_blend", "mean"),
            narrative_integration=("narrative_integration_rate", "mean"),
        )
        .round(3)
    )
    top_contrast = contrast.reindex(contrast["cohen_d"].abs().sort_values(ascending=False).index).head(20)
    lines = [
        "# SUICA Blind Construct Coding Package v1",
        "",
        "## Purpose",
        "",
        "This package converts SUICA factor interpretation into a blind construct-coding workflow. The coder-facing file contains text only plus empty rating columns; factor, pole, score, and source metadata are isolated in a hidden key.",
        "",
        "## Package Size",
        "",
        f"- blind coder items: `{len(coder_items)}`",
        f"- keyed examples: `{len(key)}`",
        f"- factors covered: `{key['factor'].nunique()}`",
        "",
        "## Pole Coverage",
        "",
        pole_counts.to_markdown(index=False),
        "",
        "## Source Coverage",
        "",
        source_counts.to_markdown(index=False),
        "",
        "## Full-Pole Anchor Alignment",
        "",
        top_alignment.round(3).to_markdown(index=False),
        "",
        "## Selected-Item Automatic Precode Summary",
        "",
        top_selected.to_markdown(index=False),
        "",
        "## Largest Full-Pole Anchor Contrasts",
        "",
        top_contrast[["factor", "anchor", "low_mean", "high_mean", "high_minus_low", "cohen_d"]]
        .round(3)
        .to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        "- This is the next measurement-development gate after narrative/projective anchor correlation.",
        "- Human or LLM blind ratings should be merged back through the hidden key to test whether factor names survive without revealing the model's labels.",
        "- If coder ratings fail to separate high/low poles, the factor name should be downgraded even if lexical correlations are strong.",
        "",
        "## Artifacts",
        "",
        "- `results/suica_blind_construct_coding_package_v1/blind_coding_items.csv`",
        "- `results/suica_blind_construct_coding_package_v1/blind_coding_key.csv`",
        "- `results/suica_blind_construct_coding_package_v1/construct_coding_rubric.md`",
        "- `results/suica_blind_construct_coding_package_v1/auto_anchor_scores_by_item.csv`",
        "- `results/suica_blind_construct_coding_package_v1/full_pole_anchor_contrast.csv`",
        "- `results/suica_blind_construct_coding_package_v1/factor_construct_alignment_summary.csv`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(args.slice_scores, dtype={"user_id": str})
    if not args.include_x:
        frame = frame.loc[~frame["scenario"].astype(str).str.startswith("x_")].copy()
    status = pd.read_csv(args.factor_status)
    anchor_summary = pd.read_csv(args.anchor_summary)
    factors = factor_cols(frame)

    examples = select_extreme_examples(
        frame,
        factors,
        status,
        examples_per_pole=args.examples_per_pole,
        max_per_scenario=args.max_per_scenario,
        max_excerpt_chars=args.max_excerpt_chars,
    )
    coder_items, key = build_blind_items(examples, seed=args.seed)
    selected_anchor_scores = score_selected_items(key)
    contrast = full_pole_anchor_contrast(frame, factors, quantile=args.quantile)
    alignment = build_alignment_summary(contrast, anchor_summary)

    coder_items.to_csv(out_dir / "blind_coding_items.csv", index=False)
    key.to_csv(out_dir / "blind_coding_key.csv", index=False)
    selected_anchor_scores.to_csv(out_dir / "auto_anchor_scores_by_item.csv", index=False)
    contrast.to_csv(out_dir / "full_pole_anchor_contrast.csv", index=False)
    alignment.to_csv(out_dir / "factor_construct_alignment_summary.csv", index=False)
    write_rubric(out_dir / "construct_coding_rubric.md")
    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "slice_scores": str(Path(args.slice_scores)),
                "factor_status": str(Path(args.factor_status)),
                "anchor_summary": str(Path(args.anchor_summary)),
                "examples_per_pole": int(args.examples_per_pole),
                "max_per_scenario": int(args.max_per_scenario),
                "max_excerpt_chars": int(args.max_excerpt_chars),
                "quantile": float(args.quantile),
                "seed": int(args.seed),
                "include_x": bool(args.include_x),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(Path(args.report_path), coder_items, key, alignment, selected_anchor_scores, contrast)
    print("Blind construct coding package created.")
    print(alignment.round(3).to_string(index=False))
    print(f"\nReport: {Path(args.report_path).resolve().relative_to(ROOT)}")


if __name__ == "__main__":
    main()
