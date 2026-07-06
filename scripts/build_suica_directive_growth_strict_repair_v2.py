#!/usr/bin/env python
"""Build strict redemptive-growth repair package for SUICA directive-growth.

v1 local coupling still selected instrumental learning. v2 narrows growth to
redemptive/self-transformational language and excludes academic/task-learning
contexts before building a 2x2 blind package.
"""

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
from scripts.build_suica_construct_expansion_readiness_v1 import (  # noqa: E402
    assign_author_split,
    clean_excerpt,
    source_family_from_scenario,
    top_token_share,
)
from scripts.build_suica_directive_growth_coupled_repair_v1 import (  # noqa: E402
    DIRECTIVE_BIGRAMS,
    DIRECTIVE_TERMS,
    QUADRANTS,
    build_coder_order,
    phrase_positions,
    tokenize_with_sentence_ids,
)
from scripts.build_suica_independent_blind_validation_batch_v1 import mask_personality_terms, write_rubric  # noqa: E402


ANCHORS_PATH = ROOT / "results" / "suica_narrative_projective_anchor_validation_v2" / "slice_narrative_projective_anchors.csv"
OUT_DIR = ROOT / "results" / "suica_directive_growth_strict_repair_v2"
REPORT_PATH = ROOT / "reports" / "suica_directive_growth_strict_repair_v2.md"
DEFAULT_SOURCE_FAMILIES = ["pandora", "essays"]

STRICT_GROWTH_TERMS = {
    "heal",
    "healed",
    "healing",
    "recover",
    "recovered",
    "recovering",
    "recovery",
    "overcome",
    "overcame",
    "growth",
    "redemption",
    "resilience",
}
STRICT_GROWTH_BIGRAMS = {
    ("move", "on"),
    ("work", "through"),
    ("learn", "from"),
    ("get", "better"),
    ("feel", "better"),
    ("grow", "up"),
    ("change", "myself"),
    ("change", "yourself"),
    ("better", "person"),
}
ADVERSITY_TERMS = {
    "abuse",
    "afraid",
    "anxiety",
    "bad",
    "breakup",
    "conflict",
    "depressed",
    "depression",
    "difficult",
    "difficulty",
    "fail",
    "failed",
    "failure",
    "fear",
    "hurt",
    "issue",
    "loss",
    "mistake",
    "mistakes",
    "pain",
    "problem",
    "problems",
    "sad",
    "struggle",
    "struggling",
    "trauma",
    "wrong",
}
INSTRUMENTAL_CONTEXT_TERMS = {
    "assignment",
    "book",
    "class",
    "exam",
    "grade",
    "grades",
    "homework",
    "lyrics",
    "music",
    "paper",
    "practice",
    "prepare",
    "prepared",
    "sat",
    "school",
    "score",
    "scores",
    "song",
    "study",
    "teacher",
    "test",
    "tests",
    "textbook",
    "textbooks",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SUICA directive-growth strict repair v2.")
    parser.add_argument("--anchors", default=str(ANCHORS_PATH))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--source-family", action="append", default=[])
    parser.add_argument("--examples-per-source-role-cell", type=int, default=3)
    parser.add_argument("--dev-share", type=float, default=0.5)
    parser.add_argument("--high-quantile", type=float, default=0.75)
    parser.add_argument("--low-quantile", type=float, default=0.25)
    parser.add_argument("--coupling-window", type=int, default=18)
    parser.add_argument("--context-window", type=int, default=10)
    parser.add_argument("--min-token-count", type=int, default=40)
    parser.add_argument("--max-top-token-share", type=float, default=0.18)
    parser.add_argument("--max-excerpt-chars", type=int, default=520)
    parser.add_argument("--seed", type=int, default=8282)
    return parser.parse_args()


def load_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def nearby(tokens: list[tuple[str, int, int]], idx: int, terms: set[str], *, window: int) -> bool:
    for token, token_idx, _sent in tokens:
        if abs(token_idx - idx) <= window and token in terms:
            return True
    return False


def strict_growth_positions(tokens: list[tuple[str, int, int]], *, context_window: int) -> list[tuple[int, int]]:
    """Find growth positions that look redemptive/self-transformational."""

    positions: list[tuple[int, int]] = []
    words = [token for token, _idx, _sent in tokens]
    for idx, (token, token_idx, sentence_id) in enumerate(tokens):
        prev_next = (words[idx], words[idx + 1]) if idx + 1 < len(words) else ("", "")
        lexical_hit = token in STRICT_GROWTH_TERMS or prev_next in STRICT_GROWTH_BIGRAMS
        if not lexical_hit:
            continue
        has_adversity = nearby(tokens, token_idx, ADVERSITY_TERMS, window=context_window)
        instrumental = nearby(tokens, token_idx, INSTRUMENTAL_CONTEXT_TERMS, window=context_window)
        inherently_redemptive = token in {"heal", "healed", "healing", "recover", "recovered", "recovering", "recovery", "overcome", "overcame"}
        phrase_redemptive = prev_next in {("move", "on"), ("work", "through"), ("better", "person"), ("change", "myself"), ("change", "yourself")}
        if instrumental and not inherently_redemptive:
            continue
        if inherently_redemptive or phrase_redemptive or has_adversity:
            positions.append((token_idx, sentence_id))
    return sorted(set(positions))


def strict_coupling_features(text: str, *, coupling_window: int, context_window: int) -> dict[str, float]:
    tokens = tokenize_with_sentence_ids(text)
    directive_positions = phrase_positions(tokens, DIRECTIVE_TERMS - {"learn", "help"}, DIRECTIVE_BIGRAMS)
    growth_positions = strict_growth_positions(tokens, context_window=context_window)
    instrumental_count = sum(1 for token, _idx, _sent in tokens if token in INSTRUMENTAL_CONTEXT_TERMS)
    adversity_count = sum(1 for token, _idx, _sent in tokens if token in ADVERSITY_TERMS)
    if not tokens:
        return {
            "strict_token_count": 0,
            "strict_directive_term_count": 0,
            "strict_growth_term_count": 0,
            "strict_coupled_pair_count": 0,
            "strict_same_sentence_pair_count": 0,
            "strict_min_distance": np.nan,
            "instrumental_context_count": 0,
            "adversity_context_count": 0,
            "strict_redemptive_coupling_score": 0.0,
        }
    coupled = 0
    same_sentence = 0
    distances: list[int] = []
    for d_idx, d_sent in directive_positions:
        for g_idx, g_sent in growth_positions:
            distance = abs(d_idx - g_idx)
            distances.append(distance)
            if distance <= coupling_window:
                coupled += 1
            if d_sent == g_sent:
                same_sentence += 1
    min_distance = min(distances) if distances else np.nan
    raw_score = coupled + 1.5 * same_sentence
    penalty = 1.0 / (1.0 + 0.25 * instrumental_count)
    normalized = raw_score * penalty / max(1.0, np.sqrt(len(tokens)))
    return {
        "strict_token_count": int(len(tokens)),
        "strict_directive_term_count": int(len(directive_positions)),
        "strict_growth_term_count": int(len(growth_positions)),
        "strict_coupled_pair_count": int(coupled),
        "strict_same_sentence_pair_count": int(same_sentence),
        "strict_min_distance": float(min_distance) if not pd.isna(min_distance) else np.nan,
        "instrumental_context_count": int(instrumental_count),
        "adversity_context_count": int(adversity_count),
        "strict_redemptive_coupling_score": float(normalized),
    }


def prepare_frame(
    anchors: pd.DataFrame,
    *,
    dev_share: float,
    min_token_count: int,
    max_top_token_share: float,
    max_excerpt_chars: int,
    coupling_window: int,
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
        "directive_interpersonal_blend",
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
    frame["directive_signal"] = pd.to_numeric(frame["directive_interpersonal_blend"], errors="coerce").fillna(0.0)
    frame["growth_signal"] = pd.to_numeric(frame["redemption_growth_rate"], errors="coerce").fillna(0.0)
    frame = frame.loc[
        pd.to_numeric(frame["token_count"], errors="coerce").fillna(0).ge(min_token_count)
        & frame["slice_text"].fillna("").astype(str).str.len().gt(0)
        & frame["top_token_share"].le(max_top_token_share)
    ].copy()
    features = pd.DataFrame(
        [
            strict_coupling_features(text, coupling_window=coupling_window, context_window=context_window)
            for text in frame["slice_text"].fillna("")
        ],
        index=frame.index,
    )
    frame = pd.concat([frame, features], axis=1)
    frame = frame.drop_duplicates("text_hash", keep="first").reset_index(drop=True)
    return frame


def add_quantiles_and_cells(frame: pd.DataFrame, *, high_quantile: float, low_quantile: float) -> pd.DataFrame:
    out = frame.copy()
    group_cols = ["source_family", "sample_role"]
    for col in ["directive_signal", "growth_signal", "strict_redemptive_coupling_score"]:
        out[f"{col}_pct"] = out.groupby(group_cols)[col].rank(pct=True, method="average")
    directive_high = out["directive_signal"].gt(0) & out["directive_signal_pct"].ge(high_quantile)
    directive_low = out["directive_signal"].le(0) | out["directive_signal_pct"].le(low_quantile)
    strict_growth_high = out["strict_growth_term_count"].gt(0)
    growth_high = out["growth_signal"].gt(0) & out["growth_signal_pct"].ge(high_quantile) & strict_growth_high
    growth_low = out["strict_growth_term_count"].le(0) | out["growth_signal"].le(0) | out["growth_signal_pct"].le(low_quantile)
    coupling_high = out["strict_redemptive_coupling_score"].gt(0) & out["strict_redemptive_coupling_score_pct"].ge(high_quantile)
    coupling_low = out["strict_redemptive_coupling_score"].le(0) | out["strict_redemptive_coupling_score_pct"].le(low_quantile)
    out["cell"] = np.select(
        [
            directive_high & growth_high & coupling_high,
            directive_high & growth_low & coupling_low,
            directive_low & growth_high & coupling_low,
            directive_low & growth_low & coupling_low,
        ],
        QUADRANTS,
        default="middle",
    )
    out["cell_score"] = np.select(
        [
            out["cell"].eq("directive_growth"),
            out["cell"].eq("directive_only"),
            out["cell"].eq("growth_only"),
            out["cell"].eq("low_both"),
        ],
        [
            np.minimum.reduce([out["directive_signal_pct"], out["growth_signal_pct"], out["strict_redemptive_coupling_score_pct"]]),
            out["directive_signal_pct"] + (1.0 - out["growth_signal_pct"]) + (1.0 - out["strict_redemptive_coupling_score_pct"]),
            out["growth_signal_pct"] + (1.0 - out["directive_signal_pct"]) + (1.0 - out["strict_redemptive_coupling_score_pct"]),
            (1.0 - out["directive_signal_pct"]) + (1.0 - out["growth_signal_pct"]) + (1.0 - out["strict_redemptive_coupling_score_pct"]),
        ],
        default=0.0,
    )
    return out


def select_items(frame: pd.DataFrame, *, source_families: list[str], examples_per_source_role_cell: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[pd.DataFrame] = []
    gaps: list[dict] = []
    used_hashes: set[str] = set()
    rng = np.random.default_rng(seed)
    for role in ["development", "heldout"]:
        for source in source_families:
            source_role = frame.loc[frame["source_family"].eq(source) & frame["sample_role"].eq(role)].copy()
            for cell in QUADRANTS:
                group = source_role.loc[source_role["cell"].eq(cell) & ~source_role["text_hash"].isin(used_hashes)].copy()
                available = len(group)
                if not group.empty:
                    group["_jitter"] = rng.uniform(0, 1e-6, size=len(group))
                    group = group.sort_values(["cell_score", "_jitter"], ascending=[False, True])
                    selected = group.drop_duplicates("user_id", keep="first").head(examples_per_source_role_cell)
                    if len(selected) < examples_per_source_role_cell:
                        more = group.loc[~group["text_hash"].isin(selected["text_hash"])].head(
                            examples_per_source_role_cell - len(selected)
                        )
                        selected = pd.concat([selected, more], ignore_index=True)
                else:
                    selected = group
                gaps.append(
                    {
                        "sample_role": role,
                        "source_family": source,
                        "cell": cell,
                        "available_items_after_dedupe": int(available),
                        "selected_items": int(len(selected)),
                        "required_items": int(examples_per_source_role_cell),
                        "selection_complete": bool(len(selected) >= examples_per_source_role_cell),
                    }
                )
                if len(selected) < examples_per_source_role_cell:
                    continue
                selected = selected.copy()
                selected["construct_id"] = "f10_directive_growth_strict_repair_v2"
                selected["construct_label"] = "directive strict redemptive-growth repair"
                selected["construct_type"] = "interaction_2x2"
                selected["target_score"] = selected["cell_score"]
                rows.append(selected)
                used_hashes.update(selected["text_hash"].astype(str))
    return (pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(), pd.DataFrame(gaps))


def build_blind_package(items: pd.DataFrame, *, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    shuffled = items.sample(frac=1.0, random_state=seed).reset_index(drop=True).copy()
    shuffled["blind_item_id"] = [f"SUICA-DGSR2-{idx:04d}" for idx in range(1, len(shuffled) + 1)]
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
        "directive_signal",
        "growth_signal",
        "strict_redemptive_coupling_score",
        "strict_directive_term_count",
        "strict_growth_term_count",
        "strict_coupled_pair_count",
        "strict_same_sentence_pair_count",
        "strict_min_distance",
        "instrumental_context_count",
        "adversity_context_count",
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
        frame.loc[frame["cell"].isin(QUADRANTS)]
        .groupby(["sample_role", "source_family", "cell"], as_index=False)
        .agg(
            available_items=("slice_obs_id", "count"),
            unique_users=("user_id", "nunique"),
            conditions=("condition", "nunique"),
            strict_coupling_mean=("strict_redemptive_coupling_score", "mean"),
            strict_growth_terms=("strict_growth_term_count", "mean"),
            instrumental_context=("instrumental_context_count", "mean"),
            adversity_context=("adversity_context_count", "mean"),
        )
        .sort_values(["sample_role", "source_family", "cell"])
    )


def selected_summary(key: pd.DataFrame) -> pd.DataFrame:
    return (
        key.groupby(["sample_role", "source_family", "cell"], as_index=False)
        .agg(
            items=("blind_item_id", "count"),
            unique_users=("user_id", "nunique"),
            target_score_mean=("target_score", "mean"),
            directive_mean=("directive_signal", "mean"),
            growth_mean=("growth_signal", "mean"),
            strict_coupling_mean=("strict_redemptive_coupling_score", "mean"),
            strict_growth_terms=("strict_growth_term_count", "mean"),
            strict_same_sentence_pairs=("strict_same_sentence_pair_count", "mean"),
            instrumental_context=("instrumental_context_count", "mean"),
            adversity_context=("adversity_context_count", "mean"),
        )
        .sort_values(["sample_role", "source_family", "cell"])
    )


def write_report(path: Path, *, prepared: pd.DataFrame, gaps: pd.DataFrame, capacity: pd.DataFrame, selected: pd.DataFrame, args: argparse.Namespace) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SUICA Directive-Growth Strict Repair v2",
        "",
        "## Purpose",
        "",
        "Repair directive-growth by filtering growth to redemptive/self-transformational language and penalizing instrumental academic/task contexts.",
        "",
        "## Input",
        "",
        f"- anchors: `{args.anchors}`",
        f"- prepared rows after filters: `{len(prepared)}`",
        f"- unique users: `{prepared['user_id'].nunique()}`",
        f"- coupling window: `{args.coupling_window}` tokens",
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
        "- v2 excludes generic academic/task learning from growth unless a stronger redemptive cue is present.",
        "- If development still fails, the project should stop trying to rescue directive-growth as a single interaction factor and split it into separate directive-action and adversity-recovery constructs.",
        "- Heldout items must remain untouched unless development passes.",
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
        coupling_window=args.coupling_window,
        context_window=args.context_window,
    )
    prepared = prepared.loc[prepared["source_family"].isin(source_families)].copy()
    scored = add_quantiles_and_cells(prepared, high_quantile=args.high_quantile, low_quantile=args.low_quantile)
    selected, gaps = select_items(
        scored,
        source_families=source_families,
        examples_per_source_role_cell=args.examples_per_source_role_cell,
        seed=args.seed,
    )
    coder, key, mask_audit = build_blind_package(selected, seed=args.seed)
    capacity = capacity_counts(scored)
    selected_stats = selected_summary(key) if not key.empty else pd.DataFrame()
    scored.to_csv(out_dir / "strict_scored_anchor_rows.csv", index=False)
    capacity.to_csv(out_dir / "capacity_counts.csv", index=False)
    gaps.to_csv(out_dir / "selection_gap_audit.csv", index=False)
    key.to_csv(out_dir / "strict_repair_key.csv", index=False)
    coder.to_csv(out_dir / "strict_repair_blind_items.csv", index=False)
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
                "coupling_window": int(args.coupling_window),
                "context_window": int(args.context_window),
                "seed": int(args.seed),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    write_report(Path(args.report_path), prepared=prepared, gaps=gaps, capacity=capacity, selected=selected_stats, args=args)
    print("SUICA directive-growth strict repair v2 package complete.")
    print(f"prepared_rows={len(prepared)} selected_items={len(key)}")
    print(f"report={Path(args.report_path)}")


if __name__ == "__main__":
    main()
