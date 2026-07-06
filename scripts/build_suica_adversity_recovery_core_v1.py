#!/usr/bin/env python
"""Build an independent SUICA adversity-recovery pole construct package.

Directive-growth failed as an interaction because directive language replicated
but growth did not. This builder splits out the growth side as its own pole
construct: high texts show adversity followed by recovery/self-transformation;
low texts lack recovery-growth language.
"""

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

from scripts.build_suica_blind_construct_coding_package_v1 import CODING_DIMENSIONS, stable_text_hash  # noqa: E402
from scripts.build_suica_construct_expansion_readiness_v1 import (  # noqa: E402
    assign_author_split,
    clean_excerpt,
    select_diverse_items,
    source_family_from_scenario,
    top_token_share,
)
from scripts.build_suica_directive_growth_coupled_repair_v1 import build_coder_order, tokenize_with_sentence_ids  # noqa: E402
from scripts.build_suica_directive_growth_strict_repair_v2 import (  # noqa: E402
    ADVERSITY_TERMS,
    INSTRUMENTAL_CONTEXT_TERMS,
    strict_growth_positions,
)
from scripts.build_suica_independent_blind_validation_batch_v1 import mask_personality_terms, write_rubric  # noqa: E402


ANCHORS_PATH = ROOT / "results" / "suica_narrative_projective_anchor_validation_v2" / "slice_narrative_projective_anchors.csv"
OUT_DIR = ROOT / "results" / "suica_adversity_recovery_core_v1"
REPORT_PATH = ROOT / "reports" / "suica_adversity_recovery_core_v1.md"
DEFAULT_SOURCE_FAMILIES = ["pandora", "essays"]
CONSTRUCT_ID = "suica_adversity_recovery_core"
CONSTRUCT_LABEL = "adversity-recovery core"
POLES = ["high", "low"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SUICA adversity-recovery core package v1.")
    parser.add_argument("--anchors", default=str(ANCHORS_PATH))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--source-family", action="append", default=[])
    parser.add_argument("--examples-per-source-role-pole", type=int, default=6)
    parser.add_argument("--dev-share", type=float, default=0.5)
    parser.add_argument("--high-quantile", type=float, default=0.75)
    parser.add_argument("--low-quantile", type=float, default=0.25)
    parser.add_argument("--context-window", type=int, default=10)
    parser.add_argument("--min-token-count", type=int, default=40)
    parser.add_argument("--max-top-token-share", type=float, default=0.18)
    parser.add_argument("--max-excerpt-chars", type=int, default=520)
    parser.add_argument("--seed", type=int, default=8383)
    return parser.parse_args()


def load_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def adversity_recovery_features(text: str, *, context_window: int) -> dict[str, float]:
    """Score redemptive recovery cues while penalizing instrumental contexts."""

    tokens = tokenize_with_sentence_ids(text)
    if not tokens:
        return {
            "ar_token_count": 0,
            "ar_strict_growth_term_count": 0,
            "ar_adversity_context_count": 0,
            "ar_instrumental_context_count": 0,
            "adversity_recovery_score": 0.0,
        }
    strict_positions = strict_growth_positions(tokens, context_window=context_window)
    adversity_count = sum(1 for token, _idx, _sent in tokens if token in ADVERSITY_TERMS)
    instrumental_count = sum(1 for token, _idx, _sent in tokens if token in INSTRUMENTAL_CONTEXT_TERMS)
    # Recovery is only interpretable as a construct when a recovery cue exists.
    # Adversity terms sharpen the score, but do not create it by themselves.
    raw_score = (2.0 * len(strict_positions)) + (0.35 * adversity_count if strict_positions else 0.0)
    penalty = 1.0 / (1.0 + 0.25 * instrumental_count)
    score = raw_score * penalty / max(1.0, np.sqrt(len(tokens)))
    return {
        "ar_token_count": int(len(tokens)),
        "ar_strict_growth_term_count": int(len(strict_positions)),
        "ar_adversity_context_count": int(adversity_count),
        "ar_instrumental_context_count": int(instrumental_count),
        "adversity_recovery_score": float(score),
    }


def prepare_frame(
    anchors: pd.DataFrame,
    *,
    dev_share: float,
    min_token_count: int,
    max_top_token_share: float,
    max_excerpt_chars: int,
    context_window: int,
) -> pd.DataFrame:
    required = {
        "scenario",
        "user_id",
        "condition",
        "slice_obs_id",
        "slice_index",
        "token_count",
        "slice_text",
        "redemption_growth_rate",
    }
    missing = required.difference(anchors.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")
    frame = anchors.copy()
    frame["source_family"] = frame["scenario"].map(source_family_from_scenario)
    frame["sample_role"] = assign_author_split(frame, dev_share=dev_share)
    frame["text_hash"] = frame["slice_text"].map(stable_text_hash)
    frame["top_token_share"] = frame["slice_text"].map(top_token_share)
    frame["text_excerpt"] = frame["slice_text"].map(lambda text: clean_excerpt(text, max_chars=max_excerpt_chars))
    frame["redemption_growth_signal"] = pd.to_numeric(frame["redemption_growth_rate"], errors="coerce").fillna(0.0)
    frame = frame.loc[
        pd.to_numeric(frame["token_count"], errors="coerce").fillna(0).ge(min_token_count)
        & frame["slice_text"].fillna("").astype(str).str.len().gt(0)
        & frame["top_token_share"].le(max_top_token_share)
    ].copy()
    features = pd.DataFrame(
        [adversity_recovery_features(text, context_window=context_window) for text in frame["slice_text"].fillna("")],
        index=frame.index,
    )
    frame = pd.concat([frame, features], axis=1)
    frame = frame.drop_duplicates("text_hash", keep="first").reset_index(drop=True)
    return frame


def add_scores_and_poles(frame: pd.DataFrame, *, high_quantile: float, low_quantile: float) -> pd.DataFrame:
    out = frame.copy()
    group_cols = ["source_family", "sample_role"]
    for col in ["redemption_growth_signal", "adversity_recovery_score"]:
        out[f"{col}_pct"] = out.groupby(group_cols)[col].rank(pct=True, method="average")
    high_mask = (
        out["ar_strict_growth_term_count"].gt(0)
        & out["adversity_recovery_score"].gt(0)
        & (
            out["adversity_recovery_score_pct"].ge(high_quantile)
            | out["redemption_growth_signal_pct"].ge(high_quantile)
        )
    )
    low_mask = (
        out["ar_strict_growth_term_count"].le(0)
        & (
            out["adversity_recovery_score"].le(0)
            | out["adversity_recovery_score_pct"].le(low_quantile)
        )
        & (
            out["redemption_growth_signal"].le(0)
            | out["redemption_growth_signal_pct"].le(low_quantile)
        )
    )
    out["ar_cell"] = np.select([high_mask, low_mask], ["high", "low"], default="middle")
    out["ar_positive_score"] = 0.5 * out["adversity_recovery_score_pct"] + 0.5 * out["redemption_growth_signal_pct"]
    out["ar_negative_score"] = 1.0 - out[["adversity_recovery_score_pct", "redemption_growth_signal_pct"]].max(axis=1)
    return out


def select_items(
    frame: pd.DataFrame,
    *,
    source_families: list[str],
    examples_per_source_role_pole: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[pd.DataFrame] = []
    gaps: list[dict] = []
    used_hashes: set[str] = set()
    for role in ["development", "heldout"]:
        for source in source_families:
            source_role = frame.loc[frame["source_family"].eq(source) & frame["sample_role"].eq(role)].copy()
            for pole, score_col in [("high", "ar_positive_score"), ("low", "ar_negative_score")]:
                group = source_role.loc[source_role["ar_cell"].eq(pole) & ~source_role["text_hash"].isin(used_hashes)].copy()
                available = len(group)
                chosen = select_diverse_items(
                    group,
                    score_col=score_col,
                    n=examples_per_source_role_pole,
                    seed=seed + (0 if pole == "high" else 1),
                )
                gaps.append(
                    {
                        "sample_role": role,
                        "source_family": source,
                        "cell": pole,
                        "available_items_after_dedupe": int(available),
                        "selected_items": int(len(chosen)),
                        "required_items": int(examples_per_source_role_pole),
                        "selection_complete": bool(len(chosen) >= examples_per_source_role_pole),
                    }
                )
                if len(chosen) < examples_per_source_role_pole:
                    continue
                chosen = chosen.copy()
                chosen["construct_id"] = CONSTRUCT_ID
                chosen["construct_label"] = CONSTRUCT_LABEL
                chosen["construct_type"] = "pole_contrast"
                chosen["cell"] = pole
                chosen["target_score"] = chosen[score_col]
                rows.append(chosen)
                used_hashes.update(chosen["text_hash"].astype(str))
    return (pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(), pd.DataFrame(gaps))


def build_blind_package(items: pd.DataFrame, *, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    shuffled = items.sample(frac=1.0, random_state=seed).reset_index(drop=True).copy()
    shuffled["blind_item_id"] = [f"SUICA-AR-{idx:04d}" for idx in range(1, len(shuffled) + 1)]
    masked_texts: list[str] = []
    mask_rows: list[dict] = []
    for row in shuffled.itertuples(index=False):
        masked, count = mask_personality_terms(getattr(row, "text_excerpt", ""))
        masked_texts.append(masked)
        mask_rows.append(
            {
                "blind_item_id": row.blind_item_id,
                "sample_role": row.sample_role,
                "source_family": row.source_family,
                "cell": row.cell,
                "slice_obs_id": row.slice_obs_id,
                "text_hash": row.text_hash,
                "masked_term_count": int(count),
                "was_masked": bool(count > 0),
            }
        )
    shuffled["text_excerpt_masked"] = masked_texts
    coder = shuffled[["blind_item_id", "text_excerpt_masked"]].rename(columns={"text_excerpt_masked": "text_excerpt"})
    for dimension, _description in CODING_DIMENSIONS:
        coder[f"{dimension}_0_to_3"] = ""
    coder["coder_notes"] = ""
    key_cols = [
        "blind_item_id",
        "construct_id",
        "construct_label",
        "construct_type",
        "sample_role",
        "source_family",
        "cell",
        "scenario",
        "user_id",
        "condition",
        "slice_obs_id",
        "slice_index",
        "token_count",
        "target_score",
        "redemption_growth_signal",
        "adversity_recovery_score",
        "ar_strict_growth_term_count",
        "ar_adversity_context_count",
        "ar_instrumental_context_count",
        "text_hash",
        "top_token_share",
        "text_excerpt",
        "text_excerpt_masked",
    ]
    key = shuffled[[col for col in key_cols if col in shuffled.columns]].copy()
    return coder, key, pd.DataFrame(mask_rows)


def split_role_files(coder: pd.DataFrame, key: pd.DataFrame, out_dir: Path, *, seed: int) -> None:
    coder_with_role = coder.merge(key[["blind_item_id", "sample_role"]], on="blind_item_id", how="left", validate="one_to_one")
    for role in ["development", "heldout"]:
        role_coder = coder_with_role.loc[coder_with_role["sample_role"].eq(role)].drop(columns=["sample_role"]).reset_index(drop=True)
        role_coder.to_csv(out_dir / f"{role}_blind_items.csv", index=False)
        build_coder_order(role_coder, coder_id=f"{role}_coder_A", seed=seed + 11).to_csv(out_dir / f"{role}_coder_A_items.csv", index=False)
        build_coder_order(role_coder, coder_id=f"{role}_coder_B", seed=seed + 12).to_csv(out_dir / f"{role}_coder_B_items.csv", index=False)


def capacity_counts(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.loc[frame["ar_cell"].isin(POLES)]
        .groupby(["sample_role", "source_family", "ar_cell"], as_index=False)
        .agg(
            available_items=("slice_obs_id", "count"),
            unique_users=("user_id", "nunique"),
            conditions=("condition", "nunique"),
            recovery_score_mean=("adversity_recovery_score", "mean"),
            growth_signal_mean=("redemption_growth_signal", "mean"),
            strict_growth_terms=("ar_strict_growth_term_count", "mean"),
            adversity_context=("ar_adversity_context_count", "mean"),
            instrumental_context=("ar_instrumental_context_count", "mean"),
        )
        .rename(columns={"ar_cell": "cell"})
        .sort_values(["sample_role", "source_family", "cell"])
    )


def selected_summary(key: pd.DataFrame) -> pd.DataFrame:
    return (
        key.groupby(["sample_role", "source_family", "cell"], as_index=False)
        .agg(
            items=("blind_item_id", "count"),
            unique_users=("user_id", "nunique"),
            target_score_mean=("target_score", "mean"),
            recovery_score_mean=("adversity_recovery_score", "mean"),
            growth_signal_mean=("redemption_growth_signal", "mean"),
            strict_growth_terms=("ar_strict_growth_term_count", "mean"),
            adversity_context=("ar_adversity_context_count", "mean"),
            instrumental_context=("ar_instrumental_context_count", "mean"),
        )
        .sort_values(["sample_role", "source_family", "cell"])
    )


def write_report(
    path: Path,
    *,
    prepared: pd.DataFrame,
    gaps: pd.DataFrame,
    capacity: pd.DataFrame,
    selected: pd.DataFrame,
    args: argparse.Namespace,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SUICA Adversity-Recovery Core v1",
        "",
        "## Purpose",
        "",
        "Split the failed directive-growth interaction into an independent redemptive/adversity-recovery pole construct.",
        "",
        "## Input",
        "",
        f"- anchors: `{args.anchors}`",
        f"- prepared rows after filters: `{len(prepared)}`",
        f"- unique users: `{prepared['user_id'].nunique()}`",
        f"- context window: `{args.context_window}` tokens",
        "",
        "## Selection Gaps",
        "",
        gaps.to_markdown(index=False) if not gaps.empty else "_No gap rows._",
        "",
        "## Capacity Counts",
        "",
        capacity.round(3).to_markdown(index=False) if not capacity.empty else "_No capacity rows._",
        "",
        "## Selected Item Summary",
        "",
        selected.round(3).to_markdown(index=False) if not selected.empty else "_No selected rows._",
        "",
        "## Interpretation",
        "",
        "- This package tests recovery/growth without requiring directive language.",
        "- Development coding must pass before heldout is touched.",
        "- If this passes, the failed directive-growth interaction should be replaced by two separate SUICA constructs: directive-action and adversity-recovery.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    source_families = args.source_family or DEFAULT_SOURCE_FAMILIES
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    anchors = load_csv(args.anchors)
    prepared = prepare_frame(
        anchors,
        dev_share=args.dev_share,
        min_token_count=args.min_token_count,
        max_top_token_share=args.max_top_token_share,
        max_excerpt_chars=args.max_excerpt_chars,
        context_window=args.context_window,
    )
    prepared = prepared.loc[prepared["source_family"].isin(source_families)].copy()
    scored = add_scores_and_poles(prepared, high_quantile=args.high_quantile, low_quantile=args.low_quantile)
    selected, gaps = select_items(
        scored,
        source_families=source_families,
        examples_per_source_role_pole=args.examples_per_source_role_pole,
        seed=args.seed,
    )
    coder, key, mask_audit = build_blind_package(selected, seed=args.seed)
    capacity = capacity_counts(scored)
    selected_stats = selected_summary(key) if not key.empty else pd.DataFrame()
    scored.to_csv(out_dir / "adversity_recovery_scored_anchor_rows.csv", index=False)
    capacity.to_csv(out_dir / "capacity_counts.csv", index=False)
    gaps.to_csv(out_dir / "selection_gap_audit.csv", index=False)
    key.to_csv(out_dir / "adversity_recovery_key.csv", index=False)
    coder.to_csv(out_dir / "adversity_recovery_blind_items.csv", index=False)
    build_coder_order(coder, coder_id="coder_A", seed=args.seed + 1).to_csv(out_dir / "coder_A_items.csv", index=False)
    build_coder_order(coder, coder_id="coder_B", seed=args.seed + 2).to_csv(out_dir / "coder_B_items.csv", index=False)
    split_role_files(coder, key, out_dir, seed=args.seed)
    mask_audit.to_csv(out_dir / "masking_audit.csv", index=False)
    selected_stats.to_csv(out_dir / "selected_item_summary.csv", index=False)
    write_rubric(out_dir / "coding_rubric.md")
    (out_dir / "manifest.json").write_text(
        json.dumps(
            {
                "anchors": args.anchors,
                "source_families": source_families,
                "prepared_rows": int(len(prepared)),
                "selected_items": int(len(key)),
                "context_window": int(args.context_window),
                "seed": int(args.seed),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(Path(args.report_path), prepared=prepared, gaps=gaps, capacity=capacity, selected=selected_stats, args=args)
    print("SUICA adversity-recovery core package complete.")
    print(f"prepared_rows={len(prepared)} selected_items={len(key)}")
    print(f"report={Path(args.report_path)}")


if __name__ == "__main__":
    main()
