#!/usr/bin/env python
"""Build a selective condition policy for SUICA scoring.

The previous experiment showed that condition-centering is not universally
helpful. This script converts that finding into a scoring policy: keep raw
scores by default, but allow condition-centered scores where they clearly
increase person or person-by-condition clarity without increasing residual
instability.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


RELEASE_CLARITY_DELTA = 0.05
CANDIDATE_CLARITY_DELTA = 0.02
CANDIDATE_RESIDUAL_DELTA = -0.005
DEGRADATION_CLARITY_DELTA = -0.02
DEGRADATION_RESIDUAL_DELTA = 0.01


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SUICA selective condition policy v3.")
    parser.add_argument(
        "--comparison",
        default="results/suica_condition_normalized_g_theory_v2/raw_vs_centered_comparison.csv",
    )
    parser.add_argument("--raw-readiness", default="results/suica_g_theory_v1/measurement_readiness.csv")
    parser.add_argument(
        "--centered-readiness",
        default="results/suica_condition_normalized_g_theory_v2/centered_measurement_readiness.csv",
    )
    parser.add_argument(
        "--anchor-summary",
        default="results/suica_corpus_balanced_manual_v2/anchor_invariance_summary.csv",
    )
    parser.add_argument("--output-dir", default="results/suica_selective_condition_policy_v3")
    parser.add_argument("--report-path", default="reports/suica_selective_condition_policy_v3.md")
    return parser.parse_args()


def load_readiness(path: Path, prefix: str) -> pd.DataFrame:
    """Load readiness metrics and prefix score-specific columns."""
    frame = pd.read_csv(path)
    keep = [
        "scenario",
        "factor",
        "relative_g_3x4",
        "absolute_g_3x4",
        "readiness",
    ]
    keep = [col for col in keep if col in frame.columns]
    out = frame[keep].copy()
    return out.rename(
        columns={
            "relative_g_3x4": f"{prefix}_relative_g_3x4",
            "absolute_g_3x4": f"{prefix}_absolute_g_3x4",
            "readiness": f"{prefix}_readiness",
        }
    )


def choose_policy(row: pd.Series) -> tuple[str, str, str]:
    """Choose raw or centered scoring for one scenario-factor cell."""
    clarity = float(row["clarity_delta"])
    residual_delta = float(row["delta_prop_residual"])
    signal_delta = float(row["delta_prop_person"] + row["delta_prop_person_condition"])
    if clarity >= RELEASE_CLARITY_DELTA and residual_delta <= CANDIDATE_RESIDUAL_DELTA and signal_delta >= 0:
        return (
            "condition_centered",
            "centered_release",
            "Condition-centering clearly improves signal clarity and lowers residual variance.",
        )
    if clarity >= CANDIDATE_CLARITY_DELTA and residual_delta <= CANDIDATE_RESIDUAL_DELTA and signal_delta >= 0:
        return (
            "condition_centered",
            "centered_candidate",
            "Condition-centering is promising but below release threshold.",
        )
    if clarity <= DEGRADATION_CLARITY_DELTA or residual_delta >= DEGRADATION_RESIDUAL_DELTA:
        return (
            "raw",
            "raw_due_to_centering_degradation",
            "Condition-centering removes useful signal or increases residual instability.",
        )
    return (
        "raw",
        "raw_default_neutral",
        "Condition-centering has no material measurement advantage.",
    )


def selected_value(row: pd.Series, metric: str) -> float:
    """Return the raw or centered value selected by policy."""
    prefix = "centered" if row["selected_variant"] == "condition_centered" else "raw"
    return float(row[f"{prefix}_{metric}"])


def classify_score_role(row: pd.Series) -> str:
    """Classify the selected score into a SUICA measurement role."""
    person = selected_value(row, "prop_person")
    condition = selected_value(row, "prop_condition")
    person_condition = selected_value(row, "prop_person_condition")
    residual = selected_value(row, "prop_residual")
    if person >= 0.18 and person >= 2.0 * person_condition:
        return "base_score_candidate"
    if person_condition >= 0.05 and person_condition >= 0.25 * max(person, 1e-9):
        return "reaction_signature_candidate"
    if condition >= 0.04:
        return "choice_condition_sensitive"
    if person + person_condition >= 0.18:
        return "mixed_base_reaction_candidate"
    if residual >= 0.82:
        return "residual_sensitive_item_bank_repair"
    return "weak_measurement_candidate"


def residual_quality(row: pd.Series) -> str:
    """Classify residual burden for one selected scenario-factor cell."""
    residual = selected_value(row, "prop_residual")
    if residual >= 0.84:
        return "high_residual"
    if residual >= 0.76:
        return "moderate_residual"
    return "lower_residual"


def release_recommendation(row: pd.Series) -> str:
    """Convert anchor invariance, policy, and reliability into an action label."""
    verdict = str(row.get("v2_verdict", ""))
    role = str(row["score_role"])
    selected_g = float(row["selected_relative_g_3x4"])
    policy = str(row["policy_class"])
    anchor_ok = verdict == "anchor_invariant_candidate"
    anchor_partial = verdict == "partial_invariance_candidate"
    if policy == "centered_release" and selected_g >= 0.65 and (anchor_ok or anchor_partial):
        return "release_centered_cell"
    if anchor_ok and role == "base_score_candidate" and selected_g >= 0.70:
        return "scale_like_candidate"
    if anchor_ok and role in {"reaction_signature_candidate", "mixed_base_reaction_candidate"} and selected_g >= 0.60:
        return "projective_signature_candidate"
    if anchor_partial and role in {"base_score_candidate", "reaction_signature_candidate", "mixed_base_reaction_candidate"}:
        return "manual_review_before_release"
    if row["residual_quality"] == "high_residual":
        return "item_bank_repair_first"
    return "exploratory_only"


def build_policy(
    comparison: pd.DataFrame,
    raw_readiness: pd.DataFrame,
    centered_readiness: pd.DataFrame,
    anchor_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Build the scenario-factor scoring policy table."""
    policy = comparison.copy()
    choices = policy.apply(choose_policy, axis=1, result_type="expand")
    choices.columns = ["selected_variant", "policy_class", "policy_rationale"]
    policy = pd.concat([policy, choices], axis=1)
    policy = policy.merge(raw_readiness, on=["scenario", "factor"], how="left")
    policy = policy.merge(centered_readiness, on=["scenario", "factor"], how="left")
    if not anchor_summary.empty:
        anchor_cols = [
            col
            for col in [
                "factor",
                "provisional_name",
                "measurement_role",
                "anchor_profile_r",
                "anchor_direction_agreement",
                "max_abs_anchor_delta",
                "v2_verdict",
            ]
            if col in anchor_summary.columns
        ]
        policy = policy.merge(anchor_summary[anchor_cols], on="factor", how="left")
    for metric in ["prop_person", "prop_condition", "prop_person_condition", "prop_residual"]:
        policy[f"selected_{metric}"] = policy.apply(lambda row, m=metric: selected_value(row, m), axis=1)
    policy["selected_relative_g_3x4"] = np.where(
        policy["selected_variant"].eq("condition_centered"),
        policy["centered_relative_g_3x4"],
        policy["raw_relative_g_3x4"],
    )
    policy["selected_absolute_g_3x4"] = np.where(
        policy["selected_variant"].eq("condition_centered"),
        policy["centered_absolute_g_3x4"],
        policy["raw_absolute_g_3x4"],
    )
    policy["selected_readiness"] = np.where(
        policy["selected_variant"].eq("condition_centered"),
        policy["centered_readiness"],
        policy["raw_readiness"],
    )
    policy["score_role"] = policy.apply(classify_score_role, axis=1)
    policy["residual_quality"] = policy.apply(residual_quality, axis=1)
    policy["release_recommendation"] = policy.apply(release_recommendation, axis=1)
    order = [
        "scenario",
        "factor",
        "provisional_name",
        "selected_variant",
        "policy_class",
        "score_role",
        "residual_quality",
        "release_recommendation",
        "clarity_delta",
        "selected_prop_person",
        "selected_prop_condition",
        "selected_prop_person_condition",
        "selected_prop_residual",
        "selected_relative_g_3x4",
        "selected_absolute_g_3x4",
        "v2_verdict",
        "anchor_profile_r",
        "anchor_direction_agreement",
        "max_abs_anchor_delta",
        "policy_rationale",
    ]
    order = [col for col in order if col in policy.columns]
    rest = [col for col in policy.columns if col not in order]
    return policy[order + rest].sort_values(["factor", "scenario"]).reset_index(drop=True)


def summarize_factor_policy(policy: pd.DataFrame) -> pd.DataFrame:
    """Summarize selected scoring behavior by factor."""
    rows: list[dict[str, Any]] = []
    for factor, group in policy.groupby("factor", sort=True):
        role_mode = group["score_role"].mode()
        release_mode = group["release_recommendation"].mode()
        rows.append(
            {
                "factor": factor,
                "provisional_name": group["provisional_name"].dropna().iloc[0] if group["provisional_name"].notna().any() else "",
                "n_cells": int(len(group)),
                "centered_cells": int(group["selected_variant"].eq("condition_centered").sum()),
                "centered_release_cells": int(group["policy_class"].eq("centered_release").sum()),
                "centered_candidate_cells": int(group["policy_class"].eq("centered_candidate").sum()),
                "raw_default_cells": int(group["policy_class"].eq("raw_default_neutral").sum()),
                "raw_degradation_cells": int(group["policy_class"].eq("raw_due_to_centering_degradation").sum()),
                "mean_selected_person": float(group["selected_prop_person"].mean()),
                "mean_selected_person_condition": float(group["selected_prop_person_condition"].mean()),
                "mean_selected_residual": float(group["selected_prop_residual"].mean()),
                "mean_selected_relative_g_3x4": float(group["selected_relative_g_3x4"].mean()),
                "dominant_score_role": str(role_mode.iloc[0]) if not role_mode.empty else "",
                "dominant_release_recommendation": str(release_mode.iloc[0]) if not release_mode.empty else "",
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["centered_release_cells", "centered_candidate_cells", "mean_selected_relative_g_3x4"],
        ascending=[False, False, False],
    )


def summarize_scenario_policy(policy: pd.DataFrame) -> pd.DataFrame:
    """Summarize selected scoring behavior by scenario."""
    rows: list[dict[str, Any]] = []
    for scenario, group in policy.groupby("scenario", sort=True):
        rows.append(
            {
                "scenario": scenario,
                "n_cells": int(len(group)),
                "centered_cells": int(group["selected_variant"].eq("condition_centered").sum()),
                "raw_degradation_cells": int(group["policy_class"].eq("raw_due_to_centering_degradation").sum()),
                "mean_clarity_delta": float(group["clarity_delta"].mean()),
                "mean_selected_person": float(group["selected_prop_person"].mean()),
                "mean_selected_person_condition": float(group["selected_prop_person_condition"].mean()),
                "mean_selected_residual": float(group["selected_prop_residual"].mean()),
                "mean_selected_relative_g_3x4": float(group["selected_relative_g_3x4"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("mean_clarity_delta", ascending=False)


def write_json_rules(path: Path, policy: pd.DataFrame) -> None:
    """Write compact scoring rules for downstream scorers."""
    rules: dict[str, Any] = {"version": "suica_selective_condition_policy_v3", "rules": {}}
    for _, row in policy.iterrows():
        factor = str(row["factor"])
        scenario = str(row["scenario"])
        rules["rules"].setdefault(factor, {})[scenario] = {
            "selected_variant": row["selected_variant"],
            "policy_class": row["policy_class"],
            "score_role": row["score_role"],
            "residual_quality": row["residual_quality"],
            "release_recommendation": row["release_recommendation"],
            "clarity_delta": float(row["clarity_delta"]),
            "selected_relative_g_3x4": float(row["selected_relative_g_3x4"]),
        }
    path.write_text(json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")


def write_report(path: Path, policy: pd.DataFrame, factor_summary: pd.DataFrame, scenario_summary: pd.DataFrame) -> None:
    """Write a compact decision report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    policy_counts = policy["policy_class"].value_counts().rename_axis("policy_class").reset_index(name="count")
    role_counts = policy["score_role"].value_counts().rename_axis("score_role").reset_index(name="count")
    recommendation_counts = (
        policy["release_recommendation"].value_counts().rename_axis("release_recommendation").reset_index(name="count")
    )
    selected_centered = policy.loc[policy["selected_variant"].eq("condition_centered")].copy()
    lines = [
        "# SUICA Selective Condition Policy v3",
        "",
        "## Purpose",
        "",
        "This report turns the condition-normalized G-theory v2 finding into an executable scoring policy. Raw SUICA scores are kept by default. Condition-centered scores are selected only when they improve measurement clarity and reduce residual instability.",
        "",
        "## Selection Rule",
        "",
        "- `centered_release`: `clarity_delta >= 0.05`, residual decreases by at least `0.005`, and person/person-condition signal does not decrease.",
        "- `centered_candidate`: `clarity_delta >= 0.02`, residual decreases by at least `0.005`, and person/person-condition signal does not decrease.",
        "- `raw_due_to_centering_degradation`: centering reduces clarity by at least `0.02` or increases residual by at least `0.01`.",
        "- `raw_default_neutral`: all other cells.",
        "",
        "## Policy Counts",
        "",
        policy_counts.to_markdown(index=False),
        "",
        "## Score Role Counts",
        "",
        role_counts.to_markdown(index=False),
        "",
        "## Release Recommendation Counts",
        "",
        recommendation_counts.to_markdown(index=False),
        "",
        "## Selected Condition-Centered Cells",
        "",
        selected_centered[
            [
                "scenario",
                "factor",
                "provisional_name",
                "policy_class",
                "score_role",
                "clarity_delta",
                "selected_prop_person",
                "selected_prop_person_condition",
                "selected_prop_residual",
                "release_recommendation",
            ]
        ]
        .round(4)
        .to_markdown(index=False)
        if not selected_centered.empty
        else "None.",
        "",
        "## Factor Policy Summary",
        "",
        factor_summary.round(4).to_markdown(index=False),
        "",
        "## Scenario Policy Summary",
        "",
        scenario_summary.round(4).to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        "The v3 policy preserves condition as a measurement facet. It does not treat topic/situation as removable noise. Most cells remain raw because centering is neutral or harmful; a small number become centered candidates where condition pressure clearly obscures a reusable person or person-by-condition signal.",
        "",
        "## Artifacts",
        "",
        "- `results/suica_selective_condition_policy_v3/selective_condition_policy.csv`",
        "- `results/suica_selective_condition_policy_v3/factor_policy_summary.csv`",
        "- `results/suica_selective_condition_policy_v3/scenario_policy_summary.csv`",
        "- `results/suica_selective_condition_policy_v3/scoring_rules.json`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    comparison = pd.read_csv(args.comparison)
    raw_readiness = load_readiness(Path(args.raw_readiness), "raw")
    centered_readiness = load_readiness(Path(args.centered_readiness), "centered")
    anchor_path = Path(args.anchor_summary)
    anchor_summary = pd.read_csv(anchor_path) if anchor_path.exists() else pd.DataFrame()
    policy = build_policy(comparison, raw_readiness, centered_readiness, anchor_summary)
    factor_summary = summarize_factor_policy(policy)
    scenario_summary = summarize_scenario_policy(policy)
    policy.to_csv(output_dir / "selective_condition_policy.csv", index=False)
    factor_summary.to_csv(output_dir / "factor_policy_summary.csv", index=False)
    scenario_summary.to_csv(output_dir / "scenario_policy_summary.csv", index=False)
    write_json_rules(output_dir / "scoring_rules.json", policy)
    run_config = {
        "comparison": args.comparison,
        "raw_readiness": args.raw_readiness,
        "centered_readiness": args.centered_readiness,
        "anchor_summary": args.anchor_summary,
        "release_clarity_delta": RELEASE_CLARITY_DELTA,
        "candidate_clarity_delta": CANDIDATE_CLARITY_DELTA,
        "candidate_residual_delta": CANDIDATE_RESIDUAL_DELTA,
        "degradation_clarity_delta": DEGRADATION_CLARITY_DELTA,
        "degradation_residual_delta": DEGRADATION_RESIDUAL_DELTA,
    }
    (output_dir / "run_config.json").write_text(json.dumps(run_config, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(Path(args.report_path), policy, factor_summary, scenario_summary)
    print(json.dumps({"output_dir": str(output_dir), "rows": int(len(policy))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
