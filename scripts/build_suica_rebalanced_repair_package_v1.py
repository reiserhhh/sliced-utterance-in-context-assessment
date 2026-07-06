#!/usr/bin/env python
"""Build a source-balanced repair coding package for weak/mixed SUICA factors.

The first blind package exposed source/pole confounds for factor_02, factor_05,
and factor_09. This script repairs the item bank by selecting high and low pole
examples within each source family, instead of selecting global extremes that
can make "high" equal PANDORA and "low" equal Essays.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_suica_blind_construct_coding_package_v1 import (  # noqa: E402
    CODING_DIMENSIONS,
    clean_excerpt,
    score_selected_items,
    source_family,
    stable_text_hash,
)


SLICE_SCORES = ROOT / "results" / "suica_item_bank_v1" / "slice_scores_with_text.csv"
FACTOR_STATUS = ROOT / "results" / "suica_measurement_framework_v1" / "factor_status_table.csv"
REPAIR_DECISIONS = ROOT / "results" / "suica_factor_repair_audit_v1" / "factor_repair_decisions.csv"
OUT_DIR = ROOT / "results" / "suica_rebalanced_repair_package_v1"
REPORT_PATH = ROOT / "reports" / "suica_rebalanced_repair_package_v1.md"


DEFAULT_TARGET_FACTORS = ["suica_factor_02", "suica_factor_05", "suica_factor_09"]
DEFAULT_SOURCE_FAMILIES = ["pandora", "essays"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build source-balanced SUICA repair package v1.")
    parser.add_argument("--slice-scores", default=str(SLICE_SCORES))
    parser.add_argument("--factor-status", default=str(FACTOR_STATUS))
    parser.add_argument("--repair-decisions", default=str(REPAIR_DECISIONS))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--target-factor", action="append", default=[], help="Target SUICA factor. Repeatable.")
    parser.add_argument("--source-family", action="append", default=[], help="Source family to balance. Repeatable.")
    parser.add_argument("--examples-per-source-pole", type=int, default=6)
    parser.add_argument("--max-per-scenario", type=int, default=3)
    parser.add_argument("--max-excerpt-chars", type=int, default=520)
    parser.add_argument("--seed", type=int, default=2718)
    parser.add_argument("--include-x", action="store_true", help="Allow x_market source family if selected.")
    return parser.parse_args()


def factor_score_col(frame: pd.DataFrame, factor: str) -> str:
    centered = f"{factor}_centered"
    if centered in frame.columns:
        return centered
    if factor in frame.columns:
        return factor
    raise KeyError(f"Missing factor score column for {factor}")


def add_source_family(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["source_family"] = out["scenario"].map(source_family)
    return out


def load_status(path: str | Path) -> pd.DataFrame:
    status = pd.read_csv(path)
    if "factor" not in status.columns:
        raise ValueError(f"missing factor column in {path}")
    return status


def select_within_source_pole(
    frame: pd.DataFrame,
    factor: str,
    status_lookup: dict[str, dict],
    *,
    source_families: list[str],
    examples_per_source_pole: int,
    max_per_scenario: int,
    max_excerpt_chars: int,
) -> pd.DataFrame:
    score_col = factor_score_col(frame, factor)
    rows: list[dict] = []
    used_hashes: set[str] = set()
    meta = status_lookup.get(factor, {})
    for family in source_families:
        family_frame = frame.loc[frame["source_family"].eq(family)].copy()
        if family_frame.empty:
            continue
        for pole, ascending in [("low", True), ("high", False)]:
            ranked = family_frame.sort_values(score_col, ascending=ascending)
            scenario_counts: dict[str, int] = {}
            selected = []
            for _, row in ranked.iterrows():
                text_hash = stable_text_hash(row.get("slice_text", ""))
                scenario = str(row.get("scenario", ""))
                if text_hash in used_hashes:
                    continue
                if scenario_counts.get(scenario, 0) >= max_per_scenario:
                    continue
                selected.append(row)
                used_hashes.add(text_hash)
                scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
                if len(selected) >= examples_per_source_pole:
                    break
            if len(selected) < examples_per_source_pole:
                for _, row in ranked.iterrows():
                    text_hash = stable_text_hash(row.get("slice_text", ""))
                    if text_hash in used_hashes:
                        continue
                    selected.append(row)
                    used_hashes.add(text_hash)
                    if len(selected) >= examples_per_source_pole:
                        break
            for rank, row in enumerate(selected, start=1):
                rows.append(
                    {
                        "factor": factor,
                        "provisional_name": meta.get("provisional_name", ""),
                        "measurement_role": meta.get("measurement_role", ""),
                        "repair_decision": meta.get("repair_decision", ""),
                        "pole": pole,
                        "source_family": family,
                        "rank_within_factor_source_pole": rank,
                        "scenario": row.get("scenario"),
                        "user_id": row.get("user_id"),
                        "condition": row.get("condition"),
                        "slice_obs_id": row.get("slice_obs_id"),
                        "slice_index": row.get("slice_index"),
                        "token_count": row.get("token_count"),
                        "factor_score": float(row.get(score_col)),
                        "text_hash": stable_text_hash(row.get("slice_text", "")),
                        "text_excerpt": clean_excerpt(row.get("slice_text", ""), max_chars=max_excerpt_chars),
                    }
                )
    return pd.DataFrame(rows)


def build_repair_blind_items(examples: pd.DataFrame, *, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    shuffled = examples.sample(frac=1.0, random_state=seed).reset_index(drop=True).copy()
    shuffled["blind_item_id"] = [f"SUICA-RP-{idx:04d}" for idx in range(1, len(shuffled) + 1)]
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
    ]
    return coder, shuffled[key_cols + ["text_excerpt"]]


def source_pole_counts(key: pd.DataFrame) -> pd.DataFrame:
    if key.empty:
        return pd.DataFrame(columns=["factor", "source_family", "pole", "count"])
    return (
        key.groupby(["factor", "source_family", "pole"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
        .sort_values(["factor", "source_family", "pole"])
    )


def source_balance_summary(counts: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for factor, group in counts.groupby("factor", sort=True):
        pivot = group.pivot_table(index="source_family", columns="pole", values="count", fill_value=0, aggfunc="sum")
        min_cell = int(pivot.min(axis=None)) if not pivot.empty else 0
        max_cell = int(pivot.max(axis=None)) if not pivot.empty else 0
        rows.append(
            {
                "factor": factor,
                "source_family_count": int(pivot.shape[0]),
                "min_source_pole_cell": min_cell,
                "max_source_pole_cell": max_cell,
                "balanced_source_pole": bool(min_cell > 0 and min_cell == max_cell),
                "source_pole_detail": "; ".join(
                    f"{idx}: high={int(row.get('high', 0))}, low={int(row.get('low', 0))}"
                    for idx, row in pivot.iterrows()
                ),
            }
        )
    return pd.DataFrame(rows)


def anchor_precode_summary(anchor_scores: pd.DataFrame) -> pd.DataFrame:
    dimensions = {
        "agency": "agency_rate",
        "mentalization": "mentalization_rate",
        "self_focus": "self_focus_rate",
        "other_focus": "third_person_rate",
        "second_person": "second_person_rate",
        "directive_blend": "directive_interpersonal_blend",
        "novelty_play": "novelty_play_rate",
        "token_count": "token_count_anchor",
        "narrative_integration": "narrative_integration_rate",
        "projective_tension": "projective_tension_rate",
    }
    available = {name: col for name, col in dimensions.items() if col in anchor_scores.columns}
    rows: list[dict] = []
    for (factor, source, pole), group in anchor_scores.groupby(["factor", "source_family", "pole"], sort=True):
        row = {"factor": factor, "source_family": source, "pole": pole, "items": int(len(group))}
        for name, col in available.items():
            row[name] = float(pd.to_numeric(group[col], errors="coerce").mean())
        rows.append(row)
    return pd.DataFrame(rows)


def score_range_summary(examples: pd.DataFrame) -> pd.DataFrame:
    if examples.empty:
        return pd.DataFrame(columns=["factor", "source_family", "pole"])
    return (
        examples.groupby(["factor", "source_family", "pole"], as_index=False)
        .agg(
            items=("text_excerpt", "count"),
            min_score=("factor_score", "min"),
            mean_score=("factor_score", "mean"),
            max_score=("factor_score", "max"),
            scenarios=("scenario", lambda x: ", ".join(sorted(set(map(str, x))))),
        )
        .sort_values(["factor", "source_family", "pole"])
    )


def write_report(
    path: Path,
    key: pd.DataFrame,
    counts: pd.DataFrame,
    balance: pd.DataFrame,
    ranges: pd.DataFrame,
    precode: pd.DataFrame,
    targets: list[str],
    sources: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SUICA Rebalanced Repair Package v1",
        "",
        "## Purpose",
        "",
        "This package repairs the first blind item bank for weak or mixed SUICA factors by selecting high and low examples within each source family. The goal is to separate construct-pole effects from corpus/source effects.",
        "",
        "## Targets",
        "",
        f"- factors: `{', '.join(targets)}`",
        f"- source families: `{', '.join(sources)}`",
        f"- blind items: `{len(key)}`",
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
        "## Interpretation",
        "",
        "- This is a repair package, not a promotion package.",
        "- If source-adjusted effects recover expected dimensions, the factor can return to the blind-coding queue.",
        "- If effects vanish inside source-balanced samples, the original factor was likely source/method dependent.",
        "- `factor_09` is the critical repair target; failure here should trigger downgrade or factor splitting.",
        "",
        "## Artifacts",
        "",
        "- `results/suica_rebalanced_repair_package_v1/repair_blind_coding_items.csv`",
        "- `results/suica_rebalanced_repair_package_v1/repair_blind_coding_key.csv`",
        "- `results/suica_rebalanced_repair_package_v1/repair_auto_anchor_scores_by_item.csv`",
        "- `results/suica_rebalanced_repair_package_v1/source_pole_counts.csv`",
        "- `results/suica_rebalanced_repair_package_v1/source_balance_summary.csv`",
        "- `results/suica_rebalanced_repair_package_v1/repair_anchor_precode_summary.csv`",
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
    status = load_status(args.factor_status)
    if Path(args.repair_decisions).exists():
        decisions = pd.read_csv(args.repair_decisions)
        status = status.merge(
            decisions[["factor", "repair_decision"]],
            on="factor",
            how="left",
        )
    status_lookup = status.set_index("factor").to_dict(orient="index")

    examples = pd.concat(
        [
            select_within_source_pole(
                frame,
                factor,
                status_lookup,
                source_families=sources,
                examples_per_source_pole=args.examples_per_source_pole,
                max_per_scenario=args.max_per_scenario,
                max_excerpt_chars=args.max_excerpt_chars,
            )
            for factor in targets
        ],
        ignore_index=True,
    )
    coder_items, key = build_repair_blind_items(examples, seed=args.seed)
    anchor_scores = score_selected_items(key)
    counts = source_pole_counts(key)
    balance = source_balance_summary(counts)
    ranges = score_range_summary(examples)
    precode = anchor_precode_summary(anchor_scores)

    coder_items.to_csv(out_dir / "repair_blind_coding_items.csv", index=False)
    key.to_csv(out_dir / "repair_blind_coding_key.csv", index=False)
    anchor_scores.to_csv(out_dir / "repair_auto_anchor_scores_by_item.csv", index=False)
    counts.to_csv(out_dir / "source_pole_counts.csv", index=False)
    balance.to_csv(out_dir / "source_balance_summary.csv", index=False)
    ranges.to_csv(out_dir / "repair_score_range_summary.csv", index=False)
    precode.to_csv(out_dir / "repair_anchor_precode_summary.csv", index=False)
    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "target_factors": targets,
                "source_families": sources,
                "examples_per_source_pole": args.examples_per_source_pole,
                "max_per_scenario": args.max_per_scenario,
                "seed": args.seed,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(Path(args.report_path), key, counts, balance, ranges, precode, targets, sources)
    print("Repair package created.")
    print(balance.to_string(index=False))
    print(f"\nReport: {Path(args.report_path).resolve().relative_to(ROOT)}")


if __name__ == "__main__":
    main()
