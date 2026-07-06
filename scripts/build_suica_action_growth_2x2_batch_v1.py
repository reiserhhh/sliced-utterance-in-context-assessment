#!/usr/bin/env python
"""Build a 2x2 blind item bank for SUICA directive-growth interaction testing."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_suica_blind_construct_coding_package_v1 import CODING_DIMENSIONS, stable_text_hash  # noqa: E402
from scripts.build_suica_independent_blind_validation_batch_v1 import mask_personality_terms, write_rubric  # noqa: E402


ANCHORS_PATH = ROOT / "results" / "suica_narrative_projective_anchor_validation_v2" / "slice_narrative_projective_anchors.csv"
OUT_DIR = ROOT / "results" / "suica_action_growth_2x2_batch_v1"
REPORT_PATH = ROOT / "reports" / "suica_action_growth_2x2_batch_v1.md"

DEFAULT_SOURCE_FAMILIES = ["pandora", "essays"]
QUADRANT_ORDER = ["directive_growth", "directive_only", "growth_only", "low_both"]
WORD_RE = re.compile(r"[A-Za-z']+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SUICA action-growth 2x2 blind batch v1.")
    parser.add_argument("--anchors", default=str(ANCHORS_PATH))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--source-family", action="append", default=[])
    parser.add_argument("--examples-per-source-cell", type=int, default=2)
    parser.add_argument("--directive-column", default="directive_interpersonal_blend")
    parser.add_argument("--growth-column", default="redemption_growth_rate")
    parser.add_argument("--min-token-count", type=int, default=40)
    parser.add_argument("--max-top-token-share", type=float, default=0.18)
    parser.add_argument("--max-excerpt-chars", type=int, default=520)
    parser.add_argument("--seed", type=int, default=6262)
    return parser.parse_args()


def load_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def source_family_from_scenario(scenario: str) -> str:
    text = str(scenario)
    if text.startswith("pandora"):
        return "pandora"
    if text.startswith("essays"):
        return "essays"
    if text.startswith("x_market"):
        return "x_market"
    return "other"


def top_token_share(text: str) -> float:
    tokens = [tok.lower() for tok in WORD_RE.findall(str(text))]
    if not tokens:
        return 1.0
    counts: dict[str, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1
    return max(counts.values()) / len(tokens)


def prepare_anchor_frame(
    anchors: pd.DataFrame,
    *,
    directive_column: str,
    growth_column: str,
    min_token_count: int,
    max_top_token_share: float,
) -> pd.DataFrame:
    required = {"scenario", "slice_obs_id", "user_id", "condition", "slice_index", "token_count", "slice_text", directive_column, growth_column}
    missing = required.difference(anchors.columns)
    if missing:
        raise ValueError(f"missing required anchor columns: {sorted(missing)}")
    frame = anchors.copy()
    frame["source_family"] = frame["scenario"].map(source_family_from_scenario)
    frame["text_hash"] = frame["slice_text"].map(stable_text_hash)
    frame["top_token_share"] = frame["slice_text"].map(top_token_share)
    frame["directive_signal"] = pd.to_numeric(frame[directive_column], errors="coerce").fillna(0.0)
    frame["growth_signal"] = pd.to_numeric(frame[growth_column], errors="coerce").fillna(0.0)
    frame["directive_flag"] = frame["directive_signal"].gt(0.0)
    frame["growth_flag"] = frame["growth_signal"].gt(0.0)
    frame["quadrant"] = np.select(
        [
            frame["directive_flag"] & frame["growth_flag"],
            frame["directive_flag"] & ~frame["growth_flag"],
            ~frame["directive_flag"] & frame["growth_flag"],
            ~frame["directive_flag"] & ~frame["growth_flag"],
        ],
        QUADRANT_ORDER,
        default="unclassified",
    )
    frame = frame.loc[
        pd.to_numeric(frame["token_count"], errors="coerce").fillna(0).ge(min_token_count)
        & frame["slice_text"].fillna("").astype(str).str.len().gt(0)
        & frame["top_token_share"].le(max_top_token_share)
    ].copy()
    frame = frame.drop_duplicates("text_hash", keep="first").reset_index(drop=True)
    return frame


def add_selection_scores(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["_directive_pct"] = out.groupby("source_family")["directive_signal"].rank(pct=True, method="average")
    out["_growth_pct"] = out.groupby("source_family")["growth_signal"].rank(pct=True, method="average")
    out["_low_directive_pct"] = 1.0 - out["_directive_pct"]
    out["_low_growth_pct"] = 1.0 - out["_growth_pct"]
    out["cell_score"] = np.select(
        [
            out["quadrant"].eq("directive_growth"),
            out["quadrant"].eq("directive_only"),
            out["quadrant"].eq("growth_only"),
            out["quadrant"].eq("low_both"),
        ],
        [
            np.minimum(out["_directive_pct"], out["_growth_pct"]),
            out["_directive_pct"] + out["_low_growth_pct"],
            out["_growth_pct"] + out["_low_directive_pct"],
            out["_low_directive_pct"] + out["_low_growth_pct"],
        ],
        default=0.0,
    )
    return out


def select_2x2_examples(
    frame: pd.DataFrame,
    *,
    source_families: list[str],
    examples_per_source_cell: int,
    seed: int,
    max_excerpt_chars: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[pd.DataFrame] = []
    gap_rows: list[dict] = []
    used_hashes: set[str] = set()
    rng = np.random.default_rng(seed)
    for source in source_families:
        source_rows = frame.loc[frame["source_family"].eq(source)].copy()
        for quadrant in QUADRANT_ORDER:
            group = source_rows.loc[source_rows["quadrant"].eq(quadrant) & ~source_rows["text_hash"].isin(used_hashes)].copy()
            available = len(group)
            if not group.empty:
                group["_jitter"] = rng.uniform(0, 1e-6, size=len(group))
                selected = group.sort_values(["cell_score", "_jitter"], ascending=[False, True]).head(examples_per_source_cell)
            else:
                selected = group
            gap_rows.append(
                {
                    "source_family": source,
                    "quadrant": quadrant,
                    "available_rows": int(available),
                    "selected_rows": int(len(selected)),
                    "required_rows": int(examples_per_source_cell),
                    "selection_complete": bool(len(selected) >= examples_per_source_cell),
                }
            )
            if len(selected) < examples_per_source_cell:
                continue
            used_hashes.update(selected["text_hash"].astype(str))
            rows.append(selected)
    if not rows:
        return pd.DataFrame(), pd.DataFrame(gap_rows)
    selected = pd.concat(rows, ignore_index=True)
    selected["excerpt"] = selected["slice_text"].fillna("").astype(str).map(
        lambda text: text[: max_excerpt_chars - 1].rstrip() + "..." if len(text) > max_excerpt_chars else text
    )
    return selected, pd.DataFrame(gap_rows)


def build_blind_items(examples: pd.DataFrame, *, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    shuffled = examples.sample(frac=1.0, random_state=seed).reset_index(drop=True).copy()
    shuffled["blind_item_id"] = [f"SUICA-AG2X2-{idx:04d}" for idx in range(1, len(shuffled) + 1)]
    masked_texts: list[str] = []
    mask_rows: list[dict] = []
    for row in shuffled.itertuples(index=False):
        masked, count = mask_personality_terms(getattr(row, "excerpt", ""))
        masked_texts.append(masked)
        mask_rows.append(
            {
                "blind_item_id": row.blind_item_id,
                "source_family": row.source_family,
                "quadrant": row.quadrant,
                "slice_obs_id": row.slice_obs_id,
                "text_hash": row.text_hash,
                "masked_term_count": count,
                "was_masked": bool(count > 0),
            }
        )
    shuffled["text_excerpt"] = masked_texts
    coder = shuffled[["blind_item_id", "text_excerpt"]].copy()
    for dimension, _description in CODING_DIMENSIONS:
        coder[f"{dimension}_0_to_3"] = ""
    coder["coder_notes"] = ""
    key_cols = [
        "blind_item_id",
        "quadrant",
        "source_family",
        "scenario",
        "user_id",
        "condition",
        "slice_obs_id",
        "slice_index",
        "token_count",
        "directive_signal",
        "growth_signal",
        "directive_flag",
        "growth_flag",
        "cell_score",
        "communion_rate",
        "redemption_growth_rate",
        "directive_interpersonal_blend",
        "growth_after_tension_blend",
        "text_hash",
        "top_token_share",
        "text_excerpt",
    ]
    key = shuffled[[col for col in key_cols if col in shuffled.columns]].copy()
    return coder, key, pd.DataFrame(mask_rows)


def build_coder_order(coder_items: pd.DataFrame, *, coder_id: str, seed: int) -> pd.DataFrame:
    ordered = coder_items.sample(frac=1.0, random_state=seed).reset_index(drop=True).copy()
    ordered.insert(0, "coder_id", coder_id)
    ordered.insert(1, "coder_order", range(1, len(ordered) + 1))
    return ordered


def count_table(key: pd.DataFrame) -> pd.DataFrame:
    if key.empty:
        return pd.DataFrame()
    return (
        key.groupby(["source_family", "quadrant"], as_index=False)
        .size()
        .rename(columns={"size": "items"})
        .sort_values(["source_family", "quadrant"])
    )


def signal_summary(key: pd.DataFrame) -> pd.DataFrame:
    if key.empty:
        return pd.DataFrame()
    return (
        key.groupby(["quadrant"], as_index=False)
        .agg(
            items=("blind_item_id", "count"),
            directive_mean=("directive_signal", "mean"),
            directive_min=("directive_signal", "min"),
            growth_mean=("growth_signal", "mean"),
            growth_min=("growth_signal", "min"),
            top_token_share_max=("top_token_share", "max"),
        )
        .sort_values("quadrant")
    )


def write_report(
    path: Path,
    key: pd.DataFrame,
    counts: pd.DataFrame,
    gaps: pd.DataFrame,
    signals: pd.DataFrame,
    mask_audit: pd.DataFrame,
    *,
    directive_column: str,
    growth_column: str,
    examples_per_source_cell: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SUICA Action-Growth 2x2 Batch v1",
        "",
        "## Purpose",
        "",
        "Build a balanced item bank to test whether `directive-growth` is an interaction construct rather than only directive-action or growth language.",
        "",
        "## Design",
        "",
        f"- directive signal column: `{directive_column}`",
        f"- growth signal column: `{growth_column}`",
        f"- examples per source x quadrant cell: `{examples_per_source_cell}`",
        "- quadrants: `directive_growth`, `directive_only`, `growth_only`, `low_both`",
        "- source families: PANDORA and Essays by default",
        f"- blind items: `{len(key)}`",
        f"- unique text hashes: `{key['text_hash'].nunique() if not key.empty else 0}`",
        "",
        "## Source x Quadrant Counts",
        "",
        counts.to_markdown(index=False) if not counts.empty else "No counts.",
        "",
        "## Selection Gaps",
        "",
        gaps.to_markdown(index=False) if not gaps.empty else "No gaps.",
        "",
        "## Signal Summary",
        "",
        signals.round(3).to_markdown(index=False) if not signals.empty else "No signal summary.",
        "",
        "## Personality-Term Mask Audit",
        "",
        mask_audit.groupby(["quadrant", "was_masked"], as_index=False)
        .size()
        .rename(columns={"size": "items"})
        .to_markdown(index=False)
        if not mask_audit.empty
        else "No mask audit.",
        "",
        "## Interpretation",
        "",
        "- This is an item-bank construction step, not evidence that the interaction exists.",
        "- The decisive evaluation is whether independent coders recover both directive and growth marginal effects, and whether the `directive_growth` cell has higher fused/min-composite scores than directive-only and growth-only controls.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    sources = args.source_family or DEFAULT_SOURCE_FAMILIES

    anchors = load_csv(args.anchors)
    frame = prepare_anchor_frame(
        anchors,
        directive_column=args.directive_column,
        growth_column=args.growth_column,
        min_token_count=args.min_token_count,
        max_top_token_share=args.max_top_token_share,
    )
    frame = frame.loc[frame["source_family"].isin(sources)].copy()
    frame = add_selection_scores(frame)
    examples, gaps = select_2x2_examples(
        frame,
        source_families=sources,
        examples_per_source_cell=args.examples_per_source_cell,
        seed=args.seed,
        max_excerpt_chars=args.max_excerpt_chars,
    )
    coder_items, key, mask_audit = build_blind_items(examples, seed=args.seed)
    coder_a = build_coder_order(coder_items, coder_id="coder_A", seed=args.seed + 101)
    coder_b = build_coder_order(coder_items, coder_id="coder_B", seed=args.seed + 202)
    counts = count_table(key)
    signals = signal_summary(key)

    coder_items.to_csv(out_dir / "action_growth_2x2_blind_items.csv", index=False)
    coder_a.to_csv(out_dir / "coder_A_items.csv", index=False)
    coder_b.to_csv(out_dir / "coder_B_items.csv", index=False)
    key.to_csv(out_dir / "action_growth_2x2_key.csv", index=False)
    counts.to_csv(out_dir / "action_growth_2x2_counts.csv", index=False)
    gaps.to_csv(out_dir / "action_growth_2x2_selection_gaps.csv", index=False)
    signals.to_csv(out_dir / "action_growth_2x2_signal_summary.csv", index=False)
    mask_audit.to_csv(out_dir / "action_growth_2x2_mask_audit.csv", index=False)
    write_rubric(out_dir / "action_growth_2x2_coding_rubric.md")
    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "anchors": str(Path(args.anchors)),
                "source_families": sources,
                "examples_per_source_cell": args.examples_per_source_cell,
                "directive_column": args.directive_column,
                "growth_column": args.growth_column,
                "min_token_count": args.min_token_count,
                "max_top_token_share": args.max_top_token_share,
                "max_excerpt_chars": args.max_excerpt_chars,
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
        key,
        counts,
        gaps,
        signals,
        mask_audit,
        directive_column=args.directive_column,
        growth_column=args.growth_column,
        examples_per_source_cell=args.examples_per_source_cell,
    )
    print("SUICA action-growth 2x2 batch created.")
    print(counts.to_string(index=False))
    print(f"\nReport: {Path(args.report_path)}")


if __name__ == "__main__":
    main()
