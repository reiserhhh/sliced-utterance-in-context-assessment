#!/usr/bin/env python
"""Build a source-balanced blind batch for SUICA repair candidates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_suica_blind_construct_coding_package_v1 import CODING_DIMENSIONS  # noqa: E402
from scripts.build_suica_independent_blind_validation_batch_v1 import (  # noqa: E402
    mask_examples_for_blind_coding,
    write_rubric,
)


REPAIR_DIR = ROOT / "results" / "suica_repair_candidate_rescoring_v1"
OUT_DIR = ROOT / "results" / "suica_repair_candidate_blind_batch_v1"
REPORT_PATH = ROOT / "reports" / "suica_repair_candidate_blind_batch_v1.md"

DEFAULT_SOURCES = ["pandora", "essays"]
DEFAULT_CANDIDATES = [
    "f05_novelty_play_core",
    "f10_directive_action_core",
    "f10_action_growth_channel",
]
ROLE_PRIORITY = {
    "retain_high_anchor": 0,
    "retain_low_anchor": 0,
    "middle_or_secondary_item": 1,
    "high_pole_misfit_or_residual": 2,
    "low_pole_misfit_or_residual": 2,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SUICA repair-candidate blind batch v1.")
    parser.add_argument("--repair-dir", default=str(REPAIR_DIR))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--candidate-id", action="append", default=[], help="Candidate id to include. Repeatable.")
    parser.add_argument("--source-family", action="append", default=[], help="Source family to balance. Repeatable.")
    parser.add_argument("--examples-per-source-pole", type=int, default=1)
    parser.add_argument("--target-formal-examples-per-source-pole", type=int, default=2)
    parser.add_argument("--seed", type=int, default=5151)
    return parser.parse_args()


def load_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def selected_candidate_ids(summary: pd.DataFrame, requested: list[str]) -> list[str]:
    if requested:
        return requested
    promoted = summary.loc[
        summary["repair_rescoring_decision"].eq("repair_candidate_promote_for_new_blind_batch"),
        "candidate_id",
    ].tolist()
    return [candidate for candidate in DEFAULT_CANDIDATES if candidate in promoted]


def candidate_manifest(summary: pd.DataFrame, candidates: list[str]) -> pd.DataFrame:
    cols = [
        "candidate_id",
        "parent_factor",
        "candidate_label",
        "mean_cohen_d",
        "min_abs_cohen_d",
        "min_abs_source_adjusted_beta",
        "inter_coder_pearson",
        "component_coverage_ratio",
        "repair_rescoring_decision",
    ]
    return summary.loc[summary["candidate_id"].isin(candidates), [col for col in cols if col in summary.columns]].copy()


def score_sort_key(frame: pd.DataFrame) -> pd.Series:
    scores = pd.to_numeric(frame["candidate_score_mean"], errors="coerce")
    return scores


def select_candidate_examples(
    item_roles: pd.DataFrame,
    *,
    candidates: list[str],
    source_families: list[str],
    examples_per_source_pole: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Select balanced examples, allowing fallback rows while recording gaps."""

    rows: list[pd.DataFrame] = []
    gap_rows: list[dict] = []
    used_ids: set[str] = set()
    for candidate_id in candidates:
        candidate_rows = item_roles.loc[item_roles["candidate_id"].eq(candidate_id)].copy()
        for source in source_families:
            for pole in ["high", "low"]:
                group = candidate_rows.loc[
                    candidate_rows["source_family"].eq(source) & candidate_rows["pole"].eq(pole)
                ].copy()
                group = group.loc[~group["blind_item_id"].isin(used_ids)].copy()
                if group.empty:
                    selected = group
                else:
                    group["_role_rank"] = group["item_repair_role"].map(ROLE_PRIORITY).fillna(9).astype(int)
                    group["_score"] = score_sort_key(group)
                    ascending = [True, False] if pole == "high" else [True, True]
                    selected = group.sort_values(["_role_rank", "_score"], ascending=ascending).head(examples_per_source_pole)
                required = examples_per_source_pole
                gap_rows.append(
                    {
                        "candidate_id": candidate_id,
                        "source_family": source,
                        "pole": pole,
                        "available_rows": int(len(group)),
                        "selected_rows": int(len(selected)),
                        "required_rows": required,
                        "selection_complete": bool(len(selected) >= required),
                        "used_fallback_rows": bool(
                            not selected.empty and selected["item_repair_role"].ne(f"retain_{pole}_anchor").any()
                        ),
                    }
                )
                if len(selected) < required:
                    continue
                used_ids.update(selected["blind_item_id"].astype(str))
                rows.append(selected)
    if not rows:
        return pd.DataFrame(), pd.DataFrame(gap_rows)
    out = pd.concat(rows, ignore_index=True)
    out = out.drop(columns=[col for col in ["_role_rank", "_score"] if col in out.columns])
    return out, pd.DataFrame(gap_rows)


def build_blind_items(examples: pd.DataFrame, *, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    shuffled = examples.sample(frac=1.0, random_state=seed).reset_index(drop=True).copy()
    shuffled["source_blind_item_id"] = shuffled["blind_item_id"]
    shuffled["blind_item_id"] = [f"SUICA-RC-{idx:04d}" for idx in range(1, len(shuffled) + 1)]
    shuffled["text_hash"] = shuffled["source_blind_item_id"]
    shuffled["slice_obs_id"] = shuffled["source_blind_item_id"]
    shuffled["text_excerpt"] = shuffled["excerpt"]
    masked, mask_audit = mask_examples_for_blind_coding(
        shuffled.rename(columns={"candidate_id": "factor"})
    )
    masked = masked.rename(columns={"factor": "candidate_id"})
    coder = masked[["blind_item_id", "text_excerpt"]].copy()
    for dimension, _description in CODING_DIMENSIONS:
        coder[f"{dimension}_0_to_3"] = ""
    coder["coder_notes"] = ""
    key_cols = [
        "blind_item_id",
        "candidate_id",
        "parent_factor",
        "candidate_label",
        "source_blind_item_id",
        "pole",
        "source_family",
        "scenario",
        "factor_score",
        "candidate_score_mean",
        "candidate_score_std",
        "item_repair_role",
        "text_excerpt_original_hash",
        "text_excerpt",
    ]
    key = masked[[col for col in key_cols if col in masked.columns]].copy()
    mask_audit = mask_audit.rename(columns={"factor": "candidate_id", "slice_obs_id": "source_blind_item_id"})
    mask_audit["blind_item_id"] = masked["blind_item_id"].to_numpy()
    return coder, key, mask_audit


def build_coder_order(coder_items: pd.DataFrame, *, coder_id: str, seed: int) -> pd.DataFrame:
    ordered = coder_items.sample(frac=1.0, random_state=seed).reset_index(drop=True).copy()
    ordered.insert(0, "coder_id", coder_id)
    ordered.insert(1, "coder_order", range(1, len(ordered) + 1))
    return ordered


def source_pole_counts(key: pd.DataFrame) -> pd.DataFrame:
    if key.empty:
        return pd.DataFrame()
    return (
        key.groupby(["candidate_id", "candidate_label", "source_family", "pole"], as_index=False)
        .size()
        .rename(columns={"size": "items"})
        .sort_values(["candidate_id", "source_family", "pole"])
    )


def formal_feasibility(item_roles: pd.DataFrame, candidates: list[str], source_families: list[str], target: int) -> pd.DataFrame:
    rows: list[dict] = []
    for candidate_id in candidates:
        for source in source_families:
            for pole in ["high", "low"]:
                role = f"retain_{pole}_anchor"
                group = item_roles.loc[
                    item_roles["candidate_id"].eq(candidate_id)
                    & item_roles["source_family"].eq(source)
                    & item_roles["pole"].eq(pole)
                    & item_roles["item_repair_role"].eq(role)
                ]
                rows.append(
                    {
                        "candidate_id": candidate_id,
                        "source_family": source,
                        "pole": pole,
                        "retain_anchor_rows": int(len(group)),
                        "formal_target_rows": target,
                        "needs_item_bank_expansion": bool(len(group) < target),
                    }
                )
    return pd.DataFrame(rows)


def write_report(
    path: Path,
    manifest: pd.DataFrame,
    counts: pd.DataFrame,
    gaps: pd.DataFrame,
    feasibility: pd.DataFrame,
    mask_audit: pd.DataFrame,
    *,
    examples_per_source_pole: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SUICA Repair Candidate Blind Batch v1",
        "",
        "## Purpose",
        "",
        "Create a small source-balanced confirmation batch for repair candidates that passed re-scoring. This is a bridge from internal repair diagnostics to a new independent coding run; it is not a final scale-release batch.",
        "",
        "## Batch Rule",
        "",
        f"- examples per candidate/source/pole: `{examples_per_source_pole}`",
        "- source families: PANDORA and Essays by default",
        "- hidden from coders: candidate id, parent factor, pole, source family, and repair decision",
        "- coder task: rate the same 11 SUICA narrative/projective dimensions on 0-3 scale",
        "",
        "## Candidate Manifest",
        "",
        manifest.round(3).to_markdown(index=False) if not manifest.empty else "No manifest.",
        "",
        "## Source x Pole Counts",
        "",
        counts.to_markdown(index=False) if not counts.empty else "No selected items.",
        "",
        "## Selection Gaps",
        "",
        gaps.to_markdown(index=False) if not gaps.empty else "No gap rows.",
        "",
        "## Formal Batch Feasibility",
        "",
        feasibility.to_markdown(index=False) if not feasibility.empty else "No feasibility rows.",
        "",
        "## Personality-Term Mask Audit",
        "",
        mask_audit.groupby(["candidate_id", "was_masked"], as_index=False)
        .size()
        .rename(columns={"size": "items"})
        .to_markdown(index=False)
        if not mask_audit.empty
        else "No mask audit.",
        "",
        "## Interpretation",
        "",
        "- If this micro-batch passes independent coding, the next step is larger item-bank expansion, not immediate release.",
        "- If any source/pole cell relies on fallback rows, that cell is a priority for new item collection.",
        "- Formal validation should target at least 2 retained anchors per candidate/source/pole before release claims.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    repair_dir = Path(args.repair_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = load_csv(repair_dir / "repair_candidate_summary.csv")
    item_roles = load_csv(repair_dir / "repair_candidate_item_roles.csv")
    candidates = selected_candidate_ids(summary, args.candidate_id)
    sources = args.source_family or DEFAULT_SOURCES
    manifest = candidate_manifest(summary, candidates)

    examples, gaps = select_candidate_examples(
        item_roles,
        candidates=candidates,
        source_families=sources,
        examples_per_source_pole=args.examples_per_source_pole,
    )
    coder_items, key, mask_audit = build_blind_items(examples, seed=args.seed)
    coder_a = build_coder_order(coder_items, coder_id="coder_A", seed=args.seed + 101)
    coder_b = build_coder_order(coder_items, coder_id="coder_B", seed=args.seed + 202)
    counts = source_pole_counts(key)
    feasibility = formal_feasibility(item_roles, candidates, sources, args.target_formal_examples_per_source_pole)

    coder_items.to_csv(out_dir / "repair_blind_coding_items.csv", index=False)
    coder_a.to_csv(out_dir / "coder_A_items.csv", index=False)
    coder_b.to_csv(out_dir / "coder_B_items.csv", index=False)
    key.to_csv(out_dir / "repair_blind_coding_key.csv", index=False)
    manifest.to_csv(out_dir / "repair_candidate_manifest.csv", index=False)
    counts.to_csv(out_dir / "repair_source_pole_counts.csv", index=False)
    gaps.to_csv(out_dir / "repair_selection_gaps.csv", index=False)
    feasibility.to_csv(out_dir / "repair_formal_batch_feasibility.csv", index=False)
    mask_audit.to_csv(out_dir / "repair_personality_term_mask_audit.csv", index=False)
    write_rubric(out_dir / "repair_construct_coding_rubric.md")
    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "repair_dir": str(repair_dir),
                "candidate_ids": candidates,
                "source_families": sources,
                "examples_per_source_pole": args.examples_per_source_pole,
                "target_formal_examples_per_source_pole": args.target_formal_examples_per_source_pole,
                "seed": args.seed,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(
        Path(args.report_path),
        manifest,
        counts,
        gaps,
        feasibility,
        mask_audit,
        examples_per_source_pole=args.examples_per_source_pole,
    )
    print("SUICA repair candidate blind batch created.")
    print(counts.to_string(index=False))
    print(f"\nReport: {Path(args.report_path)}")


if __name__ == "__main__":
    main()
