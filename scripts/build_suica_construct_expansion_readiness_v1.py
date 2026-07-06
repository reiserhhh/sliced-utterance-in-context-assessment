#!/usr/bin/env python
"""Build a SUICA construct expansion readiness package.

This script is a scale-development step, not a Big5/MBTI prediction step. It
checks whether micro-confirmed SUICA constructs have enough source-balanced,
author-heldout slice items to support a larger blind coding round.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_suica_blind_construct_coding_package_v1 import CODING_DIMENSIONS, stable_text_hash  # noqa: E402
from scripts.build_suica_independent_blind_validation_batch_v1 import mask_personality_terms, write_rubric  # noqa: E402


ANCHORS_PATH = ROOT / "results" / "suica_narrative_projective_anchor_validation_v2" / "slice_narrative_projective_anchors.csv"
OUT_DIR = ROOT / "results" / "suica_construct_expansion_readiness_v1"
REPORT_PATH = ROOT / "reports" / "suica_construct_expansion_readiness_v1.md"

DEFAULT_SOURCE_FAMILIES = ["pandora", "essays"]
WORD_RE = re.compile(r"[A-Za-z']+")
POLES = ["high", "low"]
QUADRANTS = ["directive_growth", "directive_only", "growth_only", "low_both"]


@dataclass(frozen=True)
class ConstructSpec:
    construct_id: str
    construct_label: str
    construct_type: str
    high_columns: tuple[str, ...]
    low_columns: tuple[str, ...] = ()
    description: str = ""


CONSTRUCT_SPECS = [
    ConstructSpec(
        construct_id="f05_novelty_play_core",
        construct_label="novelty-play core",
        construct_type="pole_contrast",
        high_columns=("novelty_play_rate",),
        description="Play, novelty, exploration, creative or task-interest engagement.",
    ),
    ConstructSpec(
        construct_id="f10_directive_action_core",
        construct_label="directive action core",
        construct_type="pole_contrast",
        high_columns=("directive_interpersonal_blend", "directive_rate", "agency_rate"),
        description="Direct interpersonal guidance plus active/action-oriented stance.",
    ),
    ConstructSpec(
        construct_id="f10_directive_growth_interaction",
        construct_label="directive-growth interaction",
        construct_type="interaction_2x2",
        high_columns=("directive_interpersonal_blend", "redemption_growth_rate"),
        description="Directive guidance that is specifically combined with recovery, learning, or growth framing.",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SUICA construct expansion readiness package v1.")
    parser.add_argument("--anchors", default=str(ANCHORS_PATH))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--source-family", action="append", default=[])
    parser.add_argument("--examples-per-source-role-pole", type=int, default=6)
    parser.add_argument("--interaction-examples-per-source-role-cell", type=int, default=3)
    parser.add_argument("--dev-share", type=float, default=0.5)
    parser.add_argument("--high-quantile", type=float, default=0.75)
    parser.add_argument("--low-quantile", type=float, default=0.25)
    parser.add_argument("--min-token-count", type=int, default=40)
    parser.add_argument("--max-top-token-share", type=float, default=0.18)
    parser.add_argument("--max-excerpt-chars", type=int, default=520)
    parser.add_argument("--min-unique-users-per-construct-role", type=int, default=10)
    parser.add_argument("--min-conditions-per-construct-role", type=int, default=3)
    parser.add_argument("--seed", type=int, default=7171)
    return parser.parse_args()


def load_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def source_family_from_scenario(scenario: str) -> str:
    scenario = str(scenario)
    if scenario.startswith("pandora"):
        return "pandora"
    if scenario.startswith("essays"):
        return "essays"
    if scenario.startswith("x_market") or scenario.startswith("x_"):
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


def stable_fraction(value: str) -> float:
    digest = hashlib.sha1(str(value).encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(16**12 - 1)


def assign_author_split(frame: pd.DataFrame, *, dev_share: float) -> pd.Series:
    if not 0.0 < dev_share < 1.0:
        raise ValueError("--dev-share must be in (0, 1)")
    keys = frame["source_family"].astype(str) + "::" + frame["user_id"].astype(str)
    return keys.map(lambda key: "development" if stable_fraction(key) < dev_share else "heldout")


def clean_excerpt(text: str, *, max_chars: int) -> str:
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(text) > max_chars:
        return text[: max_chars - 1].rstrip() + "..."
    return text


def prepare_anchor_frame(
    anchors: pd.DataFrame,
    *,
    min_token_count: int,
    max_top_token_share: float,
    max_excerpt_chars: int,
    dev_share: float,
) -> pd.DataFrame:
    required = {"scenario", "user_id", "condition", "slice_obs_id", "slice_index", "token_count", "slice_text"}
    for spec in CONSTRUCT_SPECS:
        required.update(spec.high_columns)
        required.update(spec.low_columns)
    missing = required.difference(anchors.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")

    frame = anchors.copy()
    frame["source_family"] = frame["scenario"].map(source_family_from_scenario)
    frame["text_hash"] = frame["slice_text"].map(stable_text_hash)
    frame["top_token_share"] = frame["slice_text"].map(top_token_share)
    frame["sample_role"] = assign_author_split(frame, dev_share=dev_share)
    frame["text_excerpt"] = frame["slice_text"].map(lambda text: clean_excerpt(text, max_chars=max_excerpt_chars))
    frame = frame.loc[
        pd.to_numeric(frame["token_count"], errors="coerce").fillna(0).ge(min_token_count)
        & frame["slice_text"].fillna("").astype(str).str.len().gt(0)
        & frame["top_token_share"].le(max_top_token_share)
    ].copy()
    frame = frame.drop_duplicates("text_hash", keep="first").reset_index(drop=True)
    return frame


def add_group_percentiles(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = frame.copy()
    group_cols = ["source_family", "sample_role"]
    for col in columns:
        values = pd.to_numeric(out[col], errors="coerce").fillna(0.0)
        out[col] = values
        out[f"{col}_pct"] = out.groupby(group_cols)[col].rank(pct=True, method="average")
    return out


def required_signal_columns() -> list[str]:
    columns: list[str] = []
    for spec in CONSTRUCT_SPECS:
        columns.extend(spec.high_columns)
        columns.extend(spec.low_columns)
    return sorted(set(columns))


def add_construct_scores(frame: pd.DataFrame, *, high_quantile: float, low_quantile: float) -> pd.DataFrame:
    out = add_group_percentiles(frame, required_signal_columns())
    for spec in CONSTRUCT_SPECS:
        if spec.construct_type == "pole_contrast":
            pct_cols = [f"{col}_pct" for col in spec.high_columns]
            out[f"{spec.construct_id}_positive_score"] = out[pct_cols].mean(axis=1)
            out[f"{spec.construct_id}_negative_score"] = 1.0 - out[f"{spec.construct_id}_positive_score"]
        elif spec.construct_type == "interaction_2x2":
            directive_raw = spec.high_columns[0]
            growth_raw = spec.high_columns[1]
            directive = f"{spec.high_columns[0]}_pct"
            growth = f"{spec.high_columns[1]}_pct"
            out[f"{spec.construct_id}_directive_pct"] = out[directive]
            out[f"{spec.construct_id}_growth_pct"] = out[growth]
            directive_high = out[directive_raw].gt(0.0) & out[directive].ge(high_quantile)
            growth_high = out[growth_raw].gt(0.0) & out[growth].ge(high_quantile)
            directive_low = out[directive_raw].le(0.0) | out[directive].le(low_quantile)
            growth_low = out[growth_raw].le(0.0) | out[growth].le(low_quantile)
            out[f"{spec.construct_id}_quadrant"] = np.select(
                [
                    directive_high & growth_high,
                    directive_high & growth_low,
                    directive_low & growth_high,
                    directive_low & growth_low,
                ],
                QUADRANTS,
                default="middle",
            )
            out[f"{spec.construct_id}_cell_score"] = np.select(
                [
                    out[f"{spec.construct_id}_quadrant"].eq("directive_growth"),
                    out[f"{spec.construct_id}_quadrant"].eq("directive_only"),
                    out[f"{spec.construct_id}_quadrant"].eq("growth_only"),
                    out[f"{spec.construct_id}_quadrant"].eq("low_both"),
                ],
                [
                    np.minimum(out[directive], out[growth]),
                    out[directive] + (1.0 - out[growth]),
                    out[growth] + (1.0 - out[directive]),
                    (1.0 - out[directive]) + (1.0 - out[growth]),
                ],
                default=0.0,
            )
        else:
            raise ValueError(f"unknown construct_type: {spec.construct_type}")
    return out


def source_role_pole_capacity(frame: pd.DataFrame, specs: list[ConstructSpec]) -> pd.DataFrame:
    rows: list[dict] = []
    for spec in specs:
        if spec.construct_type != "pole_contrast":
            continue
        for pole, score_col in [
            ("high", f"{spec.construct_id}_positive_score"),
            ("low", f"{spec.construct_id}_negative_score"),
        ]:
            eligible = frame.loc[frame[score_col].notna()].copy()
            for (source, role), group in eligible.groupby(["source_family", "sample_role"], sort=True):
                rows.append(
                    {
                        "construct_id": spec.construct_id,
                        "construct_label": spec.construct_label,
                        "construct_type": spec.construct_type,
                        "sample_role": role,
                        "source_family": source,
                        "cell": pole,
                        "available_items": int(len(group)),
                        "unique_users": int(group["user_id"].nunique()),
                        "conditions": int(group["condition"].nunique()),
                    }
                )
    return pd.DataFrame(rows)


def source_role_quadrant_capacity(frame: pd.DataFrame, specs: list[ConstructSpec]) -> pd.DataFrame:
    rows: list[dict] = []
    for spec in specs:
        if spec.construct_type != "interaction_2x2":
            continue
        q_col = f"{spec.construct_id}_quadrant"
        eligible = frame.loc[frame[q_col].isin(QUADRANTS)].copy()
        for (source, role, quadrant), group in eligible.groupby(["source_family", "sample_role", q_col], sort=True):
            rows.append(
                {
                    "construct_id": spec.construct_id,
                    "construct_label": spec.construct_label,
                    "construct_type": spec.construct_type,
                    "sample_role": role,
                    "source_family": source,
                    "cell": quadrant,
                    "available_items": int(len(group)),
                    "unique_users": int(group["user_id"].nunique()),
                    "conditions": int(group["condition"].nunique()),
                }
            )
    return pd.DataFrame(rows)


def select_diverse_items(
    group: pd.DataFrame,
    *,
    score_col: str,
    n: int,
    seed: int,
) -> pd.DataFrame:
    if group.empty or n <= 0:
        return group.head(0).copy()
    work = group.copy()
    rng = np.random.default_rng(seed)
    work["_jitter"] = rng.uniform(0, 1e-6, size=len(work))
    work = work.sort_values([score_col, "_jitter"], ascending=[False, True])
    first_pass = work.drop_duplicates("user_id", keep="first").head(n)
    if len(first_pass) >= n:
        return first_pass.drop(columns=["_jitter"], errors="ignore")
    remaining = work.loc[~work["text_hash"].isin(first_pass["text_hash"])].head(n - len(first_pass))
    selected = pd.concat([first_pass, remaining], ignore_index=True)
    return selected.drop(columns=["_jitter"], errors="ignore")


def select_expanded_item_bank(
    frame: pd.DataFrame,
    specs: list[ConstructSpec],
    *,
    source_families: list[str],
    examples_per_source_role_pole: int,
    interaction_examples_per_source_role_cell: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected_rows: list[pd.DataFrame] = []
    gap_rows: list[dict] = []
    used_hashes: set[str] = set()

    for spec_idx, spec in enumerate(specs):
        for role in ["development", "heldout"]:
            for source in source_families:
                source_role = frame.loc[frame["source_family"].eq(source) & frame["sample_role"].eq(role)].copy()
                if spec.construct_type == "pole_contrast":
                    for pole, score_col in [
                        ("high", f"{spec.construct_id}_positive_score"),
                        ("low", f"{spec.construct_id}_negative_score"),
                    ]:
                        group = source_role.loc[~source_role["text_hash"].isin(used_hashes)].copy()
                        available = len(group)
                        chosen = select_diverse_items(
                            group,
                            score_col=score_col,
                            n=examples_per_source_role_pole,
                            seed=seed + spec_idx,
                        )
                        chosen = chosen.copy()
                        chosen["construct_id"] = spec.construct_id
                        chosen["construct_label"] = spec.construct_label
                        chosen["construct_type"] = spec.construct_type
                        chosen["cell"] = pole
                        chosen["target_score"] = chosen[score_col]
                        gap_rows.append(
                            {
                                "construct_id": spec.construct_id,
                                "sample_role": role,
                                "source_family": source,
                                "cell": pole,
                                "available_items_after_dedupe": int(available),
                                "selected_items": int(len(chosen)),
                                "required_items": int(examples_per_source_role_pole),
                                "selection_complete": bool(len(chosen) >= examples_per_source_role_pole),
                            }
                        )
                        selected_rows.append(chosen)
                        used_hashes.update(chosen["text_hash"].astype(str))
                elif spec.construct_type == "interaction_2x2":
                    q_col = f"{spec.construct_id}_quadrant"
                    score_col = f"{spec.construct_id}_cell_score"
                    for quadrant in QUADRANTS:
                        group = source_role.loc[
                            source_role[q_col].eq(quadrant) & ~source_role["text_hash"].isin(used_hashes)
                        ].copy()
                        available = len(group)
                        chosen = select_diverse_items(
                            group,
                            score_col=score_col,
                            n=interaction_examples_per_source_role_cell,
                            seed=seed + spec_idx,
                        )
                        chosen = chosen.copy()
                        chosen["construct_id"] = spec.construct_id
                        chosen["construct_label"] = spec.construct_label
                        chosen["construct_type"] = spec.construct_type
                        chosen["cell"] = quadrant
                        chosen["target_score"] = chosen[score_col]
                        gap_rows.append(
                            {
                                "construct_id": spec.construct_id,
                                "sample_role": role,
                                "source_family": source,
                                "cell": quadrant,
                                "available_items_after_dedupe": int(available),
                                "selected_items": int(len(chosen)),
                                "required_items": int(interaction_examples_per_source_role_cell),
                                "selection_complete": bool(len(chosen) >= interaction_examples_per_source_role_cell),
                            }
                        )
                        selected_rows.append(chosen)
                        used_hashes.update(chosen["text_hash"].astype(str))
                else:
                    raise ValueError(f"unknown construct_type: {spec.construct_type}")
    selected = pd.concat(selected_rows, ignore_index=True) if selected_rows else pd.DataFrame()
    return selected, pd.DataFrame(gap_rows)


def build_blind_package(item_bank: pd.DataFrame, *, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if item_bank.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    shuffled = item_bank.sample(frac=1.0, random_state=seed).reset_index(drop=True).copy()
    shuffled["blind_item_id"] = [f"SUICA-EXP-{idx:04d}" for idx in range(1, len(shuffled) + 1)]
    masked_texts: list[str] = []
    mask_rows: list[dict] = []
    for row in shuffled.itertuples(index=False):
        masked, count = mask_personality_terms(getattr(row, "text_excerpt", ""))
        masked_texts.append(masked)
        mask_rows.append(
            {
                "blind_item_id": row.blind_item_id,
                "construct_id": row.construct_id,
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
        "text_hash",
        "top_token_share",
        "text_excerpt",
        "text_excerpt_masked",
    ]
    key = shuffled[[col for col in key_cols if col in shuffled.columns]].copy()
    return coder, key, pd.DataFrame(mask_rows)


def build_coder_order(coder_items: pd.DataFrame, *, coder_id: str, seed: int) -> pd.DataFrame:
    ordered = coder_items.sample(frac=1.0, random_state=seed).reset_index(drop=True).copy()
    ordered.insert(0, "coder_id", coder_id)
    ordered.insert(1, "coder_order", range(1, len(ordered) + 1))
    return ordered


def readiness_summary(
    key: pd.DataFrame,
    gaps: pd.DataFrame,
    *,
    min_unique_users: int,
    min_conditions: int,
) -> pd.DataFrame:
    rows: list[dict] = []
    for construct_id, group in key.groupby("construct_id", sort=True):
        gap_group = gaps.loc[gaps["construct_id"].eq(construct_id)]
        for role, role_rows in group.groupby("sample_role", sort=True):
            role_gaps = gap_group.loc[gap_group["sample_role"].eq(role)]
            unique_users = int(role_rows["user_id"].nunique())
            conditions = int(role_rows["condition"].nunique())
            source_conditions = role_rows.groupby("source_family")["condition"].nunique()
            min_source_conditions = int(source_conditions.min()) if not source_conditions.empty else 0
            complete = bool(role_gaps["selection_complete"].all()) if not role_gaps.empty else False
            enough_users = unique_users >= min_unique_users
            enough_conditions = conditions >= min_conditions
            source_condition_warning = min_source_conditions < min_conditions
            decision = (
                "ready_for_blind_coding_role"
                if complete and enough_users and enough_conditions
                else "not_ready_expand_or_relax_sampling"
            )
            rows.append(
                {
                    "construct_id": construct_id,
                    "sample_role": role,
                    "selected_items": int(len(role_rows)),
                    "source_families": int(role_rows["source_family"].nunique()),
                    "cells": int(role_rows["cell"].nunique()),
                    "unique_users": unique_users,
                    "conditions": conditions,
                    "min_conditions_within_source": min_source_conditions,
                    "selection_complete": complete,
                    "enough_unique_users": bool(enough_users),
                    "enough_conditions": bool(enough_conditions),
                    "source_condition_warning": bool(source_condition_warning),
                    "readiness_decision": decision,
                }
            )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    construct_decisions = []
    for construct_id, group in out.groupby("construct_id", sort=True):
        role_ready = group["readiness_decision"].eq("ready_for_blind_coding_role")
        final = "ready_for_development_and_heldout_blind_coding" if bool(role_ready.all()) else "not_ready"
        construct_decisions.append({"construct_id": construct_id, "construct_readiness_decision": final})
    return out.merge(pd.DataFrame(construct_decisions), on="construct_id", how="left")


def author_split_summary(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby(["source_family", "sample_role"], as_index=False)
        .agg(
            rows=("slice_obs_id", "count"),
            unique_users=("user_id", "nunique"),
            conditions=("condition", "nunique"),
            scenarios=("scenario", "nunique"),
        )
        .sort_values(["source_family", "sample_role"])
    )


def write_report(
    path: Path,
    *,
    args: argparse.Namespace,
    prepared: pd.DataFrame,
    readiness: pd.DataFrame,
    gaps: pd.DataFrame,
    capacity: pd.DataFrame,
    key: pd.DataFrame,
    mask_audit: pd.DataFrame,
) -> None:
    lines = [
        "# SUICA Construct Expansion Readiness v1",
        "",
        "## Purpose",
        "",
        "Build an expanded, source-balanced, author-heldout item-bank package for micro-confirmed SUICA construct candidates.",
        "",
        "This is a measurement-construction step. Big5/MBTI are not used as optimization targets here.",
        "",
        "## Input",
        "",
        f"- anchors: `{args.anchors}`",
        f"- prepared rows after text filters: `{len(prepared)}`",
        f"- unique users after filters: `{prepared['user_id'].nunique()}`",
        f"- source families: `{', '.join(args.source_family or DEFAULT_SOURCE_FAMILIES)}`",
        f"- development share: `{args.dev_share}`",
        "",
        "## Construct Readiness",
        "",
        readiness.to_markdown(index=False) if not readiness.empty else "_No readiness rows._",
        "",
        "## Selection Gaps",
        "",
        gaps.to_markdown(index=False) if not gaps.empty else "_No gap rows._",
        "",
        "## Capacity Snapshot",
        "",
        capacity.head(80).to_markdown(index=False) if not capacity.empty else "_No capacity rows._",
        "",
        "## Masking Audit",
        "",
        (
            mask_audit.groupby(["construct_id", "sample_role", "source_family"], as_index=False)
            .agg(items=("blind_item_id", "count"), masked_items=("was_masked", "sum"), masked_terms=("masked_term_count", "sum"))
            .to_markdown(index=False)
            if not mask_audit.empty
            else "_No mask audit rows._"
        ),
        "",
        "## Interpretation",
        "",
        "- `ready_for_development_and_heldout_blind_coding` means the construct has enough selected items for a larger blind coding package under the current source/author split.",
        "- This does not prove psychometric validity; it proves the next validation package is feasible.",
        "- Heldout rows are author-disjoint from development rows within each source family and should be reserved for confirmation after coding rules are fixed.",
        "- `source_condition_warning=True` means at least one source family has fewer condition designs than the global condition gate; this is expected for Essays here and should be treated as a generalization caveat rather than a selection failure.",
        "- If a construct passes this readiness gate, the next step is independent coding on development items, freezing scoring rules, then applying the same rules once to heldout items.",
        "",
        "## Artifacts",
        "",
        f"- `results/suica_construct_expansion_readiness_v1/construct_expansion_readiness_summary.csv`",
        f"- `results/suica_construct_expansion_readiness_v1/expanded_item_bank_key.csv`",
        f"- `results/suica_construct_expansion_readiness_v1/expanded_blind_items.csv`",
        f"- `results/suica_construct_expansion_readiness_v1/coder_A_items.csv`",
        f"- `results/suica_construct_expansion_readiness_v1/coder_B_items.csv`",
        f"- `results/suica_construct_expansion_readiness_v1/development_coder_A_items.csv`",
        f"- `results/suica_construct_expansion_readiness_v1/development_coder_B_items.csv`",
        f"- `results/suica_construct_expansion_readiness_v1/heldout_coder_A_items.csv`",
        f"- `results/suica_construct_expansion_readiness_v1/heldout_coder_B_items.csv`",
        f"- `results/suica_construct_expansion_readiness_v1/selection_gap_audit.csv`",
        f"- `results/suica_construct_expansion_readiness_v1/capacity_counts.csv`",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    source_families = args.source_family or DEFAULT_SOURCE_FAMILIES
    out_dir = Path(args.output_dir)
    report_path = Path(args.report_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    anchors = load_csv(args.anchors)
    prepared = prepare_anchor_frame(
        anchors,
        min_token_count=args.min_token_count,
        max_top_token_share=args.max_top_token_share,
        max_excerpt_chars=args.max_excerpt_chars,
        dev_share=args.dev_share,
    )
    prepared = prepared.loc[prepared["source_family"].isin(source_families)].copy()
    scored = add_construct_scores(prepared, high_quantile=args.high_quantile, low_quantile=args.low_quantile)

    capacity = pd.concat(
        [
            source_role_pole_capacity(scored, CONSTRUCT_SPECS),
            source_role_quadrant_capacity(scored, CONSTRUCT_SPECS),
        ],
        ignore_index=True,
    )
    item_bank, gaps = select_expanded_item_bank(
        scored,
        CONSTRUCT_SPECS,
        source_families=source_families,
        examples_per_source_role_pole=args.examples_per_source_role_pole,
        interaction_examples_per_source_role_cell=args.interaction_examples_per_source_role_cell,
        seed=args.seed,
    )
    coder, key, mask_audit = build_blind_package(item_bank, seed=args.seed)
    readiness = readiness_summary(
        key,
        gaps,
        min_unique_users=args.min_unique_users_per_construct_role,
        min_conditions=args.min_conditions_per_construct_role,
    )
    split_summary = author_split_summary(scored)

    scored_sample_cols = [
        "scenario",
        "user_id",
        "condition",
        "sample_role",
        "source_family",
        "slice_obs_id",
        "token_count",
        "text_hash",
        "f05_novelty_play_core_positive_score",
        "f10_directive_action_core_positive_score",
        "f10_directive_growth_interaction_quadrant",
        "f10_directive_growth_interaction_cell_score",
    ]
    scored[[col for col in scored_sample_cols if col in scored.columns]].to_csv(out_dir / "construct_scored_anchor_sample.csv", index=False)
    capacity.to_csv(out_dir / "capacity_counts.csv", index=False)
    gaps.to_csv(out_dir / "selection_gap_audit.csv", index=False)
    key.to_csv(out_dir / "expanded_item_bank_key.csv", index=False)
    coder.to_csv(out_dir / "expanded_blind_items.csv", index=False)
    build_coder_order(coder, coder_id="coder_A", seed=args.seed + 1).to_csv(out_dir / "coder_A_items.csv", index=False)
    build_coder_order(coder, coder_id="coder_B", seed=args.seed + 2).to_csv(out_dir / "coder_B_items.csv", index=False)
    coder_with_role = coder.merge(key[["blind_item_id", "sample_role"]], on="blind_item_id", how="left", validate="one_to_one")
    for role in ["development", "heldout"]:
        role_coder = coder_with_role.loc[coder_with_role["sample_role"].eq(role)].drop(columns=["sample_role"]).reset_index(drop=True)
        role_coder.to_csv(out_dir / f"{role}_blind_items.csv", index=False)
        build_coder_order(role_coder, coder_id=f"{role}_coder_A", seed=args.seed + 11).to_csv(
            out_dir / f"{role}_coder_A_items.csv",
            index=False,
        )
        build_coder_order(role_coder, coder_id=f"{role}_coder_B", seed=args.seed + 12).to_csv(
            out_dir / f"{role}_coder_B_items.csv",
            index=False,
        )
    mask_audit.to_csv(out_dir / "masking_audit.csv", index=False)
    readiness.to_csv(out_dir / "construct_expansion_readiness_summary.csv", index=False)
    split_summary.to_csv(out_dir / "author_split_summary.csv", index=False)
    write_rubric(out_dir / "coding_rubric.md")

    manifest = {
        "anchors": args.anchors,
        "source_families": source_families,
        "constructs": [spec.__dict__ for spec in CONSTRUCT_SPECS],
        "prepared_rows": int(len(prepared)),
        "selected_items": int(len(key)),
        "seed": int(args.seed),
        "dev_share": float(args.dev_share),
        "high_quantile": float(args.high_quantile),
        "low_quantile": float(args.low_quantile),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    write_report(
        report_path,
        args=args,
        prepared=prepared,
        readiness=readiness,
        gaps=gaps,
        capacity=capacity,
        key=key,
        mask_audit=mask_audit,
    )

    print("SUICA construct expansion readiness package complete.")
    print(f"prepared_rows={len(prepared)} selected_items={len(key)}")
    print(f"report={report_path}")


if __name__ == "__main__":
    main()
