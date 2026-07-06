#!/usr/bin/env python
"""Audit SUICA factors for repair, promotion, or downgrade decisions.

This script turns the current validation artifacts into a scale-development
queue. It does not rename factors automatically. It identifies which factors
are ready for independent blind coding, which need mixed-method audits, and
which should be repaired or downgraded before being treated as constructs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FACTOR_STATUS = ROOT / "results" / "suica_measurement_framework_v1" / "factor_status_table.csv"
ANCHOR_SUMMARY = ROOT / "results" / "suica_narrative_projective_anchor_validation_v2" / "factor_anchor_summary.csv"
BLIND_GATE = ROOT / "results" / "suica_blind_construct_coding_evaluation_v1" / "expected_dimension_gate.csv"
SOURCE_GATE = ROOT / "results" / "suica_blind_construct_coding_evaluation_v1" / "source_adjusted_expected_dimension_gate.csv"
POLE_RESULTS = ROOT / "results" / "suica_blind_construct_coding_evaluation_v1" / "pole_separation_by_factor_dimension.csv"
SOURCE_EFFECTS = ROOT / "results" / "suica_blind_construct_coding_evaluation_v1" / "source_adjusted_pole_effects.csv"
BLIND_KEY = ROOT / "results" / "suica_blind_construct_coding_package_v1" / "blind_coding_key.csv"
OUT_DIR = ROOT / "results" / "suica_factor_repair_audit_v1"
REPORT_PATH = ROOT / "reports" / "suica_factor_repair_audit_v1.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit SUICA factors for repair/development decisions.")
    parser.add_argument("--factor-status", default=str(FACTOR_STATUS))
    parser.add_argument("--anchor-summary", default=str(ANCHOR_SUMMARY))
    parser.add_argument("--blind-gate", default=str(BLIND_GATE))
    parser.add_argument("--source-gate", default=str(SOURCE_GATE))
    parser.add_argument("--pole-results", default=str(POLE_RESULTS))
    parser.add_argument("--source-effects", default=str(SOURCE_EFFECTS))
    parser.add_argument("--blind-key", default=str(BLIND_KEY))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--stable-anchor-threshold", type=float, default=0.30)
    parser.add_argument("--source-support-threshold", type=float, default=0.30)
    return parser.parse_args()


def read_optional(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def top_anchor_summary(anchor_summary: pd.DataFrame, threshold: float) -> pd.DataFrame:
    if anchor_summary.empty:
        return pd.DataFrame(columns=["factor"])
    base = anchor_summary.loc[anchor_summary["profile_component"].eq("base_score")].copy()
    base["stable_anchor_flag"] = (
        base["support_score"].ge(threshold)
        & base["direction_agreement"].ge(0.8)
        & base["scenario_count"].ge(3)
    )
    rows: list[dict] = []
    for factor, group in base.groupby("factor", sort=True):
        stable = group.loc[group["stable_anchor_flag"]].sort_values("support_score", ascending=False)
        top = group.sort_values("support_score", ascending=False).head(6)
        rows.append(
            {
                "factor": factor,
                "stable_anchor_count": int(len(stable)),
                "top_anchor": str(top.iloc[0]["anchor"]) if not top.empty else "",
                "top_anchor_support": float(top.iloc[0]["support_score"]) if not top.empty else np.nan,
                "top_anchor_direction_agreement": float(top.iloc[0]["direction_agreement"]) if not top.empty else np.nan,
                "top_anchors": "; ".join(top["anchor"].astype(str).tolist()),
                "has_length_anchor_risk": bool(top["anchor"].astype(str).str.contains("token_count", regex=False).any()),
                "has_method_or_adapter_status": bool(
                    str(group["measurement_role"].iloc[0]).lower().find("adapter") >= 0
                    or str(group["class"].iloc[0]).lower().find("adapter") >= 0
                ),
            }
        )
    return pd.DataFrame(rows)


def blind_key_summary(blind_key: pd.DataFrame) -> pd.DataFrame:
    if blind_key.empty:
        return pd.DataFrame(columns=["factor"])
    rows = []
    for factor, group in blind_key.groupby("factor", sort=True):
        source_counts = group.groupby(["pole", "source_family"]).size().unstack(fill_value=0)
        pole_source_detail = []
        for pole, pole_group in group.groupby("pole"):
            counts = pole_group["source_family"].value_counts().sort_index()
            pole_source_detail.append(f"{pole}: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
        rows.append(
            {
                "factor": factor,
                "blind_item_count": int(len(group)),
                "source_family_count": int(group["source_family"].nunique()),
                "source_families": "; ".join(sorted(map(str, group["source_family"].dropna().unique()))),
                "pole_source_detail": " | ".join(pole_source_detail),
                "has_two_source_families": bool(group["source_family"].nunique() >= 2),
            }
        )
    return pd.DataFrame(rows)


def strongest_dimension_summary(pole_results: pd.DataFrame, source_effects: pd.DataFrame) -> pd.DataFrame:
    factors = sorted(set(pole_results.get("factor", pd.Series(dtype=str))).union(set(source_effects.get("factor", pd.Series(dtype=str)))))
    rows: list[dict] = []
    for factor in factors:
        pole_group = pole_results.loc[pole_results["factor"].eq(factor)].copy() if not pole_results.empty else pd.DataFrame()
        source_group = source_effects.loc[source_effects["factor"].eq(factor)].copy() if not source_effects.empty else pd.DataFrame()
        row: dict[str, object] = {"factor": factor}
        if not pole_group.empty:
            best = pole_group.reindex(pole_group["cohen_d"].abs().sort_values(ascending=False).index).iloc[0]
            row.update(
                {
                    "strongest_blind_dimension": best["dimension"],
                    "strongest_blind_d": float(best["cohen_d"]),
                    "strongest_blind_p": float(best["p_value"]) if pd.notna(best["p_value"]) else np.nan,
                }
            )
        if not source_group.empty:
            best_s = source_group.reindex(
                source_group["high_minus_low_source_adjusted"].abs().sort_values(ascending=False).index
            ).iloc[0]
            row.update(
                {
                    "strongest_source_adjusted_dimension": best_s["dimension"],
                    "strongest_source_adjusted_beta": float(best_s["high_minus_low_source_adjusted"]),
                    "strongest_source_adjusted_p": float(best_s["p_value"]) if pd.notna(best_s["p_value"]) else np.nan,
                }
            )
        rows.append(row)
    columns = [
        "factor",
        "strongest_blind_dimension",
        "strongest_blind_d",
        "strongest_blind_p",
        "strongest_source_adjusted_dimension",
        "strongest_source_adjusted_beta",
        "strongest_source_adjusted_p",
    ]
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(rows, columns=columns)


def classify_factor(row: pd.Series, source_support_threshold: float) -> tuple[str, str]:
    blind_support = str(row.get("construct_gate", "")).lower() == "support"
    source_support = str(row.get("source_adjusted_gate", "")).lower() == "support"
    source_missing = pd.isna(row.get("source_adjusted_gate")) or str(row.get("source_adjusted_gate", "")) == ""
    stable_anchor_count = int(row.get("stable_anchor_count", 0) or 0)
    length_risk = bool(row.get("has_length_anchor_risk", False))
    adapter_risk = bool(row.get("has_method_or_adapter_status", False))
    two_sources = bool(row.get("has_two_source_families", False))
    median_abs_d = float(row.get("median_expected_abs_d", np.nan)) if pd.notna(row.get("median_expected_abs_d")) else 0.0
    median_abs_beta = (
        float(row.get("median_expected_abs_adjusted_beta", np.nan))
        if pd.notna(row.get("median_expected_abs_adjusted_beta"))
        else 0.0
    )

    if not blind_support and not source_support:
        return (
            "repair_or_downgrade",
            "expected blind dimensions are weak and source-adjusted support is weak/missing; repair item bank before construct naming",
        )
    if source_missing or not two_sources:
        return (
            "mixed_or_source_limited_audit",
            "blind gate is positive but source-family control is missing or underidentified; rebalance examples across corpora/sources",
        )
    if length_risk or adapter_risk:
        return (
            "mixed_method_audit",
            "construct signal is present but length/method/adapter risk appears in top anchors or factor status",
        )
    if blind_support and source_support and stable_anchor_count >= 2 and median_abs_d >= 0.5 and median_abs_beta >= source_support_threshold:
        return (
            "priority_independent_blind_coding",
            "stable narrative anchors plus blind/source-adjusted support; send to independent human/LLM coding next",
        )
    if blind_support or source_support:
        return (
            "provisional_keep_and_retest",
            "some construct support exists but stability or adjusted effect is not strong enough for promotion",
        )
    return ("manual_review", "falls between decision rules; inspect examples and source balance")


def build_repair_decisions(
    factor_status: pd.DataFrame,
    anchors: pd.DataFrame,
    blind_gate: pd.DataFrame,
    source_gate: pd.DataFrame,
    blind_key: pd.DataFrame,
    pole_results: pd.DataFrame,
    source_effects: pd.DataFrame,
    *,
    stable_anchor_threshold: float,
    source_support_threshold: float,
) -> pd.DataFrame:
    base = factor_status.copy()
    anchor_top = top_anchor_summary(anchors, stable_anchor_threshold)
    key_summary = blind_key_summary(blind_key)
    dim_summary = strongest_dimension_summary(pole_results, source_effects)

    blind_cols = [
        "factor",
        "construct_gate",
        "expected_dimensions",
        "median_expected_abs_d",
        "max_expected_abs_d",
        "strongest_expected_dimension",
        "strongest_expected_d",
    ]
    blind = blind_gate[[col for col in blind_cols if col in blind_gate.columns]].copy() if not blind_gate.empty else pd.DataFrame(columns=["factor"])
    source_cols = [
        "factor",
        "source_adjusted_gate",
        "median_expected_abs_adjusted_beta",
        "max_expected_abs_adjusted_beta",
        "source_adjusted_large_effect_count_abs_beta_ge_0p3",
    ]
    source = source_gate[[col for col in source_cols if col in source_gate.columns]].copy() if not source_gate.empty else pd.DataFrame(columns=["factor"])

    merged = (
        base.merge(anchor_top, on="factor", how="left")
        .merge(blind, on="factor", how="left")
        .merge(source, on="factor", how="left")
        .merge(key_summary, on="factor", how="left")
        .merge(dim_summary, on="factor", how="left")
    )
    decisions = merged.apply(lambda row: classify_factor(row, source_support_threshold), axis=1)
    merged["repair_decision"] = [decision for decision, _reason in decisions]
    merged["decision_reason"] = [reason for _decision, reason in decisions]
    order = {
        "priority_independent_blind_coding": 0,
        "mixed_method_audit": 1,
        "mixed_or_source_limited_audit": 2,
        "provisional_keep_and_retest": 3,
        "repair_or_downgrade": 4,
        "manual_review": 5,
    }
    merged["decision_priority"] = merged["repair_decision"].map(order).fillna(9).astype(int)
    return merged.sort_values(["decision_priority", "factor"])


def build_anchor_conflicts(decisions: pd.DataFrame, anchors: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    if anchors.empty:
        return pd.DataFrame()
    for factor, group in anchors.loc[anchors["profile_component"].eq("base_score")].groupby("factor", sort=True):
        top = group.sort_values("support_score", ascending=False).head(10)
        positive = top.loc[top["median_r"].gt(0), "anchor"].astype(str).tolist()
        negative = top.loc[top["median_r"].lt(0), "anchor"].astype(str).tolist()
        rows.append(
            {
                "factor": factor,
                "positive_top_anchors": "; ".join(positive[:5]),
                "negative_top_anchors": "; ".join(negative[:5]),
                "anchor_polarity_mix": bool(positive and negative),
                "token_count_in_top10": bool(top["anchor"].astype(str).str.contains("token_count", regex=False).any()),
                "top10": "; ".join(f"{r.anchor}:{r.median_r:+.3f}" for r in top.itertuples(index=False)),
            }
        )
    return pd.DataFrame(rows).merge(decisions[["factor", "repair_decision"]], on="factor", how="left")


def write_report(path: Path, decisions: pd.DataFrame, conflicts: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    queue_counts = decisions["repair_decision"].value_counts().rename_axis("repair_decision").reset_index(name="count")
    display_cols = [
        "factor",
        "provisional_name",
        "repair_decision",
        "construct_gate",
        "source_adjusted_gate",
        "stable_anchor_count",
        "median_expected_abs_d",
        "median_expected_abs_adjusted_beta",
        "top_anchor",
        "decision_reason",
    ]
    display_cols = [col for col in display_cols if col in decisions.columns]
    priority = decisions[display_cols].copy()
    lines = [
        "# SUICA Factor Repair Audit v1",
        "",
        "## Purpose",
        "",
        "This audit converts current SUICA validation evidence into a construct-development queue. It decides which factors should move to independent blind coding, which require mixed-method/source audits, and which should be repaired or downgraded before naming.",
        "",
        "## Queue Counts",
        "",
        queue_counts.to_markdown(index=False),
        "",
        "## Factor Decisions",
        "",
        priority.round(3).to_markdown(index=False),
        "",
        "## Anchor Conflict / Risk Summary",
        "",
        conflicts.head(20).to_markdown(index=False) if not conflicts.empty else "No anchor conflict rows available.",
        "",
        "## Interpretation",
        "",
        "- `priority_independent_blind_coding`: ready to send to two independent coders or coder models.",
        "- `mixed_method_audit`: construct signal exists, but method/length/adapter risk needs separation before promotion.",
        "- `mixed_or_source_limited_audit`: current blind examples do not support source-family control; rebalance item bank.",
        "- `repair_or_downgrade`: do not promote; repair item bank or split/downgrade factor.",
        "",
        "## Artifacts",
        "",
        "- `results/suica_factor_repair_audit_v1/factor_repair_decisions.csv`",
        "- `results/suica_factor_repair_audit_v1/factor_anchor_conflicts.csv`",
        "- `results/suica_factor_repair_audit_v1/repair_queue_counts.csv`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    factor_status = pd.read_csv(args.factor_status)
    anchors = read_optional(args.anchor_summary)
    blind_gate = read_optional(args.blind_gate)
    source_gate = read_optional(args.source_gate)
    pole_results = read_optional(args.pole_results)
    source_effects = read_optional(args.source_effects)
    blind_key = read_optional(args.blind_key)

    decisions = build_repair_decisions(
        factor_status,
        anchors,
        blind_gate,
        source_gate,
        blind_key,
        pole_results,
        source_effects,
        stable_anchor_threshold=args.stable_anchor_threshold,
        source_support_threshold=args.source_support_threshold,
    )
    conflicts = build_anchor_conflicts(decisions, anchors)
    queue_counts = decisions["repair_decision"].value_counts().rename_axis("repair_decision").reset_index(name="count")

    decisions.to_csv(out_dir / "factor_repair_decisions.csv", index=False)
    conflicts.to_csv(out_dir / "factor_anchor_conflicts.csv", index=False)
    queue_counts.to_csv(out_dir / "repair_queue_counts.csv", index=False)
    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "factor_status": str(Path(args.factor_status)),
                "anchor_summary": str(Path(args.anchor_summary)),
                "blind_gate": str(Path(args.blind_gate)),
                "source_gate": str(Path(args.source_gate)),
                "pole_results": str(Path(args.pole_results)),
                "source_effects": str(Path(args.source_effects)),
                "blind_key": str(Path(args.blind_key)),
                "stable_anchor_threshold": args.stable_anchor_threshold,
                "source_support_threshold": args.source_support_threshold,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(Path(args.report_path), decisions, conflicts)
    print(queue_counts.to_string(index=False))
    print()
    print(
        decisions[
            [
                "factor",
                "provisional_name",
                "repair_decision",
                "construct_gate",
                "source_adjusted_gate",
                "stable_anchor_count",
                "decision_reason",
            ]
        ].to_string(index=False)
    )
    print(f"\nReport: {Path(args.report_path).resolve().relative_to(ROOT)}")


if __name__ == "__main__":
    main()
