#!/usr/bin/env python
"""Build a locally coupled directive-growth repair package for SUICA.

The failed expanded interaction package showed that simple co-occurrence of
directive and growth anchors is too weak. This script adds a local discourse
coupling score: directive language and growth/recovery language must appear in
the same sentence-like span or within a small token window.
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
from scripts.build_suica_independent_blind_validation_batch_v1 import mask_personality_terms, write_rubric  # noqa: E402


ANCHORS_PATH = ROOT / "results" / "suica_narrative_projective_anchor_validation_v2" / "slice_narrative_projective_anchors.csv"
OUT_DIR = ROOT / "results" / "suica_directive_growth_coupled_repair_v1"
REPORT_PATH = ROOT / "reports" / "suica_directive_growth_coupled_repair_v1.md"

DEFAULT_SOURCE_FAMILIES = ["pandora", "essays"]
QUADRANTS = ["directive_growth", "directive_only", "growth_only", "low_both"]
WORD_RE = re.compile(r"[A-Za-z']+|[.!?;]")

DIRECTIVE_TERMS = {
    "advise",
    "advice",
    "ask",
    "avoid",
    "consider",
    "do",
    "don't",
    "dont",
    "find",
    "go",
    "help",
    "keep",
    "learn",
    "let",
    "make",
    "must",
    "need",
    "recommend",
    "remember",
    "should",
    "start",
    "stop",
    "take",
    "tell",
    "try",
    "use",
}
DIRECTIVE_BIGRAMS = {
    ("you", "should"),
    ("you", "need"),
    ("you", "can"),
    ("you", "could"),
    ("you", "must"),
    ("have", "to"),
    ("try", "to"),
    ("make", "sure"),
    ("don't", "be"),
    ("dont", "be"),
    ("let", "yourself"),
}
GROWTH_TERMS = {
    "aware",
    "better",
    "change",
    "develop",
    "fix",
    "grow",
    "growth",
    "heal",
    "help",
    "improve",
    "improvement",
    "learn",
    "overcome",
    "recover",
    "recovery",
    "progress",
    "realize",
    "understand",
    "work",
}
GROWTH_BIGRAMS = {
    ("get", "better"),
    ("feel", "better"),
    ("move", "on"),
    ("work", "through"),
    ("learn", "from"),
    ("figure", "out"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SUICA directive-growth coupled repair v1.")
    parser.add_argument("--anchors", default=str(ANCHORS_PATH))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--source-family", action="append", default=[])
    parser.add_argument("--examples-per-source-role-cell", type=int, default=3)
    parser.add_argument("--dev-share", type=float, default=0.5)
    parser.add_argument("--high-quantile", type=float, default=0.75)
    parser.add_argument("--low-quantile", type=float, default=0.25)
    parser.add_argument("--coupling-window", type=int, default=18)
    parser.add_argument("--min-token-count", type=int, default=40)
    parser.add_argument("--max-top-token-share", type=float, default=0.18)
    parser.add_argument("--max-excerpt-chars", type=int, default=520)
    parser.add_argument("--seed", type=int, default=8181)
    return parser.parse_args()


def load_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def tokenize_with_sentence_ids(text: str) -> list[tuple[str, int, int]]:
    """Return `(token, token_index, sentence_id)` tuples."""

    output: list[tuple[str, int, int]] = []
    sentence_id = 0
    token_index = 0
    for raw in WORD_RE.findall(str(text).lower()):
        if raw in {".", "!", "?", ";"}:
            sentence_id += 1
            continue
        output.append((raw, token_index, sentence_id))
        token_index += 1
    return output


def phrase_positions(tokens: list[tuple[str, int, int]], terms: set[str], bigrams: set[tuple[str, str]]) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []
    words = [token for token, _idx, _sent in tokens]
    for idx, (token, token_index, sentence_id) in enumerate(tokens):
        if token in terms:
            positions.append((token_index, sentence_id))
        if idx + 1 < len(tokens) and (words[idx], words[idx + 1]) in bigrams:
            positions.append((token_index, sentence_id))
    return sorted(set(positions))


def coupling_features(text: str, *, window: int = 18) -> dict[str, float]:
    """Compute local directive-growth coupling features from raw text."""

    tokens = tokenize_with_sentence_ids(text)
    directive_positions = phrase_positions(tokens, DIRECTIVE_TERMS, DIRECTIVE_BIGRAMS)
    growth_positions = phrase_positions(tokens, GROWTH_TERMS, GROWTH_BIGRAMS)
    if not tokens:
        return {
            "coupling_token_count": 0,
            "directive_term_count": 0,
            "growth_term_count": 0,
            "coupled_pair_count": 0,
            "same_sentence_pair_count": 0,
            "min_directive_growth_distance": np.nan,
            "local_coupling_score": 0.0,
        }
    coupled = 0
    same_sentence = 0
    distances: list[int] = []
    for d_idx, d_sent in directive_positions:
        for g_idx, g_sent in growth_positions:
            distance = abs(d_idx - g_idx)
            distances.append(distance)
            if distance <= window:
                coupled += 1
            if d_sent == g_sent:
                same_sentence += 1
    min_distance = min(distances) if distances else np.nan
    raw_score = coupled + 1.5 * same_sentence
    normalized = raw_score / max(1.0, np.sqrt(len(tokens)))
    return {
        "coupling_token_count": int(len(tokens)),
        "directive_term_count": int(len(directive_positions)),
        "growth_term_count": int(len(growth_positions)),
        "coupled_pair_count": int(coupled),
        "same_sentence_pair_count": int(same_sentence),
        "min_directive_growth_distance": float(min_distance) if not pd.isna(min_distance) else np.nan,
        "local_coupling_score": float(normalized),
    }


def prepare_frame(
    anchors: pd.DataFrame,
    *,
    dev_share: float,
    min_token_count: int,
    max_top_token_share: float,
    max_excerpt_chars: int,
    coupling_window: int,
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
    feature_rows = [coupling_features(text, window=coupling_window) for text in frame["slice_text"].fillna("")]
    features = pd.DataFrame(feature_rows, index=frame.index)
    frame = pd.concat([frame, features], axis=1)
    frame = frame.drop_duplicates("text_hash", keep="first").reset_index(drop=True)
    return frame


def add_quantiles_and_cells(frame: pd.DataFrame, *, high_quantile: float, low_quantile: float) -> pd.DataFrame:
    out = frame.copy()
    group_cols = ["source_family", "sample_role"]
    for col in ["directive_signal", "growth_signal", "local_coupling_score"]:
        out[f"{col}_pct"] = out.groupby(group_cols)[col].rank(pct=True, method="average")
    directive_high = out["directive_signal"].gt(0) & out["directive_signal_pct"].ge(high_quantile)
    directive_low = out["directive_signal"].le(0) | out["directive_signal_pct"].le(low_quantile)
    growth_high = out["growth_signal"].gt(0) & out["growth_signal_pct"].ge(high_quantile)
    growth_low = out["growth_signal"].le(0) | out["growth_signal_pct"].le(low_quantile)
    coupling_high = out["local_coupling_score"].gt(0) & out["local_coupling_score_pct"].ge(high_quantile)
    coupling_low = out["local_coupling_score"].le(0) | out["local_coupling_score_pct"].le(low_quantile)
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
            np.minimum.reduce([out["directive_signal_pct"], out["growth_signal_pct"], out["local_coupling_score_pct"]]),
            out["directive_signal_pct"] + (1.0 - out["growth_signal_pct"]) + (1.0 - out["local_coupling_score_pct"]),
            out["growth_signal_pct"] + (1.0 - out["directive_signal_pct"]) + (1.0 - out["local_coupling_score_pct"]),
            (1.0 - out["directive_signal_pct"]) + (1.0 - out["growth_signal_pct"]) + (1.0 - out["local_coupling_score_pct"]),
        ],
        default=0.0,
    )
    return out


def select_items(
    frame: pd.DataFrame,
    *,
    source_families: list[str],
    examples_per_source_role_cell: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
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
                selected["construct_id"] = "f10_directive_growth_coupled_repair"
                selected["construct_label"] = "directive-growth local coupling repair"
                selected["construct_type"] = "interaction_2x2"
                selected["target_score"] = selected["cell_score"]
                rows.append(selected)
                used_hashes.update(selected["text_hash"].astype(str))
    return (pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(), pd.DataFrame(gaps))


def build_blind_package(items: pd.DataFrame, *, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    shuffled = items.sample(frac=1.0, random_state=seed).reset_index(drop=True).copy()
    shuffled["blind_item_id"] = [f"SUICA-DGCR-{idx:04d}" for idx in range(1, len(shuffled) + 1)]
    mask_rows: list[dict] = []
    masked_texts: list[str] = []
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
        "local_coupling_score",
        "directive_term_count",
        "growth_term_count",
        "coupled_pair_count",
        "same_sentence_pair_count",
        "min_directive_growth_distance",
        "text_hash",
        "top_token_share",
        "text_excerpt",
        "text_excerpt_masked",
    ]
    return coder, shuffled[[col for col in key_cols if col in shuffled.columns]].copy(), pd.DataFrame(mask_rows)


def build_coder_order(coder_items: pd.DataFrame, *, coder_id: str, seed: int) -> pd.DataFrame:
    ordered = coder_items.sample(frac=1.0, random_state=seed).reset_index(drop=True).copy()
    ordered.insert(0, "coder_id", coder_id)
    ordered.insert(1, "coder_order", range(1, len(ordered) + 1))
    return ordered


def split_role_files(coder: pd.DataFrame, key: pd.DataFrame, out_dir: Path, *, seed: int) -> None:
    coder_with_role = coder.merge(key[["blind_item_id", "sample_role"]], on="blind_item_id", how="left", validate="one_to_one")
    for role in ["development", "heldout"]:
        role_coder = coder_with_role.loc[coder_with_role["sample_role"].eq(role)].drop(columns=["sample_role"]).reset_index(drop=True)
        role_coder.to_csv(out_dir / f"{role}_blind_items.csv", index=False)
        build_coder_order(role_coder, coder_id=f"{role}_coder_A", seed=seed + 11).to_csv(
            out_dir / f"{role}_coder_A_items.csv",
            index=False,
        )
        build_coder_order(role_coder, coder_id=f"{role}_coder_B", seed=seed + 12).to_csv(
            out_dir / f"{role}_coder_B_items.csv",
            index=False,
        )


def capacity_counts(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.loc[frame["cell"].isin(QUADRANTS)]
        .groupby(["sample_role", "source_family", "cell"], as_index=False)
        .agg(
            available_items=("slice_obs_id", "count"),
            unique_users=("user_id", "nunique"),
            conditions=("condition", "nunique"),
            coupling_mean=("local_coupling_score", "mean"),
            directive_mean=("directive_signal", "mean"),
            growth_mean=("growth_signal", "mean"),
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
            coupling_mean=("local_coupling_score", "mean"),
            same_sentence_pairs=("same_sentence_pair_count", "mean"),
            coupled_pairs=("coupled_pair_count", "mean"),
        )
        .sort_values(["sample_role", "source_family", "cell"])
    )


def write_report(path: Path, *, prepared: pd.DataFrame, key: pd.DataFrame, gaps: pd.DataFrame, capacity: pd.DataFrame, selected: pd.DataFrame, args: argparse.Namespace) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SUICA Directive-Growth Coupled Repair v1",
        "",
        "## Purpose",
        "",
        "Repair the failed directive-growth interaction by requiring local discourse coupling, not only slice-level co-occurrence.",
        "",
        "## Input",
        "",
        f"- anchors: `{args.anchors}`",
        f"- prepared rows after filters: `{len(prepared)}`",
        f"- unique users: `{prepared['user_id'].nunique()}`",
        f"- coupling window: `{args.coupling_window}` tokens",
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
        "- `directive_growth` now requires directive signal, growth signal, and local coupling signal.",
        "- Controls require the non-target signals and local coupling to be low.",
        "- This package should be evaluated on development items first. Heldout items must remain untouched unless development passes.",
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
    scored.to_csv(out_dir / "coupled_scored_anchor_rows.csv", index=False)
    capacity.to_csv(out_dir / "capacity_counts.csv", index=False)
    gaps.to_csv(out_dir / "selection_gap_audit.csv", index=False)
    key.to_csv(out_dir / "coupled_repair_key.csv", index=False)
    coder.to_csv(out_dir / "coupled_repair_blind_items.csv", index=False)
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
                "high_quantile": float(args.high_quantile),
                "low_quantile": float(args.low_quantile),
                "seed": int(args.seed),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    write_report(Path(args.report_path), prepared=prepared, key=key, gaps=gaps, capacity=capacity, selected=selected_stats, args=args)
    print("SUICA directive-growth coupled repair package complete.")
    print(f"prepared_rows={len(prepared)} selected_items={len(key)}")
    print(f"report={Path(args.report_path)}")


if __name__ == "__main__":
    main()
