#!/usr/bin/env python
"""Build policy-aware SUICA author profiles.

This scorer consumes slice-level SUICA factor scores plus the selective
condition policy. It outputs author-level base, reaction, choice, and residual
profiles without treating condition as a nuisance to erase.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build policy-aware SUICA author profiles.")
    parser.add_argument("--slice-scores", default="results/suica_item_bank_v1/slice_scores_with_text.csv")
    parser.add_argument("--policy", default="results/suica_selective_condition_policy_v3/selective_condition_policy.csv")
    parser.add_argument("--output-dir", default="results/suica_policy_profile_scorer_v1")
    parser.add_argument("--report-path", default="reports/suica_policy_profile_scorer_v1.md")
    parser.add_argument("--min-slices", type=int, default=4)
    parser.add_argument("--min-conditions", type=int, default=2)
    parser.add_argument("--recommended-g", type=float, default=0.65)
    parser.add_argument("--recommended-residual-sd", type=float, default=1.25)
    return parser.parse_args()


def factor_cols(frame: pd.DataFrame) -> list[str]:
    """Return raw SUICA factor columns."""
    return [
        col
        for col in frame.columns
        if col.startswith("suica_factor_")
        and not col.endswith("_centered")
        and not col.endswith("_condition_mean")
    ]


def entropy_norm(counts: pd.Series) -> float:
    """Normalized entropy of observed condition counts."""
    total = float(counts.sum())
    if total <= 0:
        return float("nan")
    probs = counts.to_numpy(float) / total
    if len(probs) <= 1:
        return 0.0
    ent = float(-(probs * np.log2(probs + 1e-12)).sum())
    return ent / float(np.log2(len(probs)))


def selected_score_column(factor: str, variant: str) -> str:
    """Return the slice score column selected by policy."""
    if variant == "condition_centered":
        return f"{factor}_centered"
    return factor


def build_selected_long(slice_scores: pd.DataFrame, policy: pd.DataFrame) -> pd.DataFrame:
    """Build a long table of policy-selected slice scores."""
    required = {"scenario", "factor", "selected_variant"}
    missing = required.difference(policy.columns)
    if missing:
        raise ValueError(f"Policy is missing required columns: {sorted(missing)}")
    base_cols = ["scenario", "user_id", "condition", "slice_obs_id", "slice_index", "token_count"]
    available_base = [col for col in base_cols if col in slice_scores.columns]
    rows: list[pd.DataFrame] = []
    raw_factors = set(factor_cols(slice_scores))
    for _, rule in policy.iterrows():
        scenario = str(rule["scenario"])
        factor = str(rule["factor"])
        variant = str(rule["selected_variant"])
        if factor not in raw_factors:
            continue
        score_col = selected_score_column(factor, variant)
        if score_col not in slice_scores.columns:
            continue
        subset = slice_scores.loc[slice_scores["scenario"].astype(str).eq(scenario), [*available_base, score_col]].copy()
        if subset.empty:
            continue
        subset = subset.rename(columns={score_col: "selected_score"})
        subset["factor"] = factor
        subset["selected_variant"] = variant
        for col in [
            "policy_class",
            "score_role",
            "residual_quality",
            "release_recommendation",
            "selected_relative_g_3x4",
            "selected_absolute_g_3x4",
            "provisional_name",
        ]:
            subset[col] = rule.get(col, np.nan)
        rows.append(subset)
    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True)
    out["user_id"] = out["user_id"].astype(str)
    out["condition"] = out["condition"].astype(str)
    return out


def build_choice_profiles(selected: pd.DataFrame) -> pd.DataFrame:
    """Build user-scenario choice profiles from observed slice conditions."""
    counts = (
        selected[["scenario", "user_id", "condition", "slice_obs_id"]]
        .drop_duplicates()
        .groupby(["scenario", "user_id", "condition"])
        .size()
        .rename("slice_count")
        .reset_index()
    )
    rows: list[dict[str, Any]] = []
    for (scenario, user_id), group in counts.groupby(["scenario", "user_id"], sort=True):
        total = int(group["slice_count"].sum())
        top = group.sort_values(["slice_count", "condition"], ascending=[False, True]).iloc[0]
        rows.append(
            {
                "scenario": scenario,
                "user_id": user_id,
                "n_conditions": int(group["condition"].nunique()),
                "n_slices": total,
                "choice_entropy_norm": entropy_norm(group["slice_count"]),
                "top_condition": str(top["condition"]),
                "top_condition_share": float(top["slice_count"] / max(1, total)),
            }
        )
    return pd.DataFrame(rows)


def quality_label(row: pd.Series, *, min_slices: int, min_conditions: int, recommended_g: float, recommended_residual_sd: float) -> str:
    """Assign a practical score quality label."""
    if int(row.get("n_slices", 0)) < min_slices or int(row.get("n_conditions", 0)) < min_conditions:
        return "insufficient_text"
    if str(row.get("release_recommendation", "")) == "item_bank_repair_first":
        return "item_bank_repair"
    if str(row.get("residual_quality", "")) == "high_residual":
        return "high_residual_exploratory"
    rel_g = float(row.get("selected_relative_g_3x4", np.nan))
    residual_sd = float(row.get("median_within_condition_sd", np.nan))
    if np.isfinite(rel_g) and rel_g >= recommended_g and np.isfinite(residual_sd) and residual_sd <= recommended_residual_sd:
        return "recommended"
    return "exploratory"


def build_profiles(
    selected: pd.DataFrame,
    *,
    min_slices: int,
    min_conditions: int,
    recommended_g: float,
    recommended_residual_sd: float,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build user-factor profiles, condition reactions, and choice profiles."""
    if selected.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    choice = build_choice_profiles(selected)
    cell = (
        selected.groupby(["scenario", "user_id", "factor", "condition"], as_index=False)
        .agg(
            condition_score_mean=("selected_score", "mean"),
            condition_score_sd=("selected_score", "std"),
            condition_n_slices=("selected_score", "size"),
            mean_token_count=("token_count", "mean"),
        )
        .fillna({"condition_score_sd": 0.0})
    )
    base_rows: list[dict[str, Any]] = []
    react_rows: list[dict[str, Any]] = []
    meta_cols = [
        "selected_variant",
        "policy_class",
        "score_role",
        "residual_quality",
        "release_recommendation",
        "selected_relative_g_3x4",
        "selected_absolute_g_3x4",
        "provisional_name",
    ]
    meta = selected.groupby(["scenario", "factor"], as_index=False)[meta_cols].first()
    for (scenario, user_id, factor), group in cell.groupby(["scenario", "user_id", "factor"], sort=True):
        base_score = float(group["condition_score_mean"].mean())
        weighted_score = float(np.average(group["condition_score_mean"], weights=group["condition_n_slices"]))
        react_values = group["condition_score_mean"] - base_score
        react_amplitude = float(react_values.std(ddof=0)) if len(react_values) > 1 else 0.0
        max_idx = int(np.argmax(np.abs(react_values.to_numpy(float)))) if len(group) else 0
        dominant = group.iloc[max_idx]
        median_within = float(group["condition_score_sd"].median())
        mean_within = float(group["condition_score_sd"].mean())
        residual_quality_score = float(1.0 / (1.0 + max(0.0, median_within)))
        base_rows.append(
            {
                "scenario": scenario,
                "user_id": user_id,
                "factor": factor,
                "base_score": base_score,
                "observed_weighted_score": weighted_score,
                "choice_influence_delta": weighted_score - base_score,
                "react_amplitude": react_amplitude,
                "max_abs_react": float(abs(react_values.iloc[max_idx])) if len(react_values) else 0.0,
                "dominant_react_condition": str(dominant["condition"]),
                "dominant_react_score": float(react_values.iloc[max_idx]) if len(react_values) else 0.0,
                "median_within_condition_sd": median_within,
                "mean_within_condition_sd": mean_within,
                "residual_quality_score": residual_quality_score,
                "factor_condition_count": int(group["condition"].nunique()),
                "factor_slice_count": int(group["condition_n_slices"].sum()),
            }
        )
        for idx, row in group.reset_index(drop=True).iterrows():
            react_rows.append(
                {
                    "scenario": scenario,
                    "user_id": user_id,
                    "factor": factor,
                    "condition": row["condition"],
                    "condition_score_mean": float(row["condition_score_mean"]),
                    "base_score": base_score,
                    "react_score": float(react_values.iloc[idx]),
                    "condition_score_sd": float(row["condition_score_sd"]),
                    "condition_n_slices": int(row["condition_n_slices"]),
                    "mean_token_count": float(row["mean_token_count"]),
                }
            )
    profiles = pd.DataFrame(base_rows)
    react = pd.DataFrame(react_rows)
    profiles = profiles.merge(meta, on=["scenario", "factor"], how="left")
    profiles = profiles.merge(choice, on=["scenario", "user_id"], how="left")
    profiles["score_quality"] = profiles.apply(
        quality_label,
        axis=1,
        min_slices=min_slices,
        min_conditions=min_conditions,
        recommended_g=recommended_g,
        recommended_residual_sd=recommended_residual_sd,
    )
    return profiles, react, choice


def summarize_profiles(profiles: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Summarize generated profiles by factor, scenario, and quality class."""
    if profiles.empty:
        empty = pd.DataFrame()
        return empty, empty, empty
    factor_summary = (
        profiles.groupby("factor", as_index=False)
        .agg(
            users=("user_id", "nunique"),
            mean_base_sd=("base_score", "std"),
            mean_react_amplitude=("react_amplitude", "mean"),
            mean_choice_influence_abs=("choice_influence_delta", lambda x: float(np.mean(np.abs(x)))),
            median_residual_quality=("residual_quality_score", "median"),
            recommended_rate=("score_quality", lambda x: float(pd.Series(x).eq("recommended").mean())),
            exploratory_or_better_rate=(
                "score_quality",
                lambda x: float(pd.Series(x).isin(["recommended", "exploratory", "high_residual_exploratory"]).mean()),
            ),
        )
        .sort_values(["recommended_rate", "mean_base_sd"], ascending=[False, False])
    )
    scenario_summary = (
        profiles.groupby("scenario", as_index=False)
        .agg(
            users=("user_id", "nunique"),
            profile_rows=("user_id", "size"),
            median_n_conditions=("n_conditions", "median"),
            median_n_slices=("n_slices", "median"),
            mean_base_sd=("base_score", "std"),
            mean_react_amplitude=("react_amplitude", "mean"),
            median_residual_quality=("residual_quality_score", "median"),
            recommended_rate=("score_quality", lambda x: float(pd.Series(x).eq("recommended").mean())),
        )
        .sort_values(["recommended_rate", "mean_base_sd"], ascending=[False, False])
    )
    quality_summary = (
        profiles.groupby(["scenario", "score_quality"], as_index=False)
        .size()
        .rename(columns={"size": "profile_rows"})
        .sort_values(["scenario", "profile_rows"], ascending=[True, False])
    )
    return factor_summary, scenario_summary, quality_summary


def write_report(
    path: Path,
    profiles: pd.DataFrame,
    react: pd.DataFrame,
    choice: pd.DataFrame,
    factor_summary: pd.DataFrame,
    scenario_summary: pd.DataFrame,
    quality_summary: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Write the profile scorer report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    top_release = profiles.loc[profiles["release_recommendation"].eq("release_centered_cell")]
    quality_counts = profiles["score_quality"].value_counts().rename_axis("score_quality").reset_index(name="rows")
    role_counts = profiles["score_role"].value_counts().rename_axis("score_role").reset_index(name="rows")
    lines = [
        "# SUICA Policy-Aware Profile Scorer v1",
        "",
        "## Purpose",
        "",
        "This scorer operationalizes the v3 selective condition policy. It outputs author-level SUICA profiles with four components: base position, reaction signature, choice pattern, and residual quality.",
        "",
        "## Score Definitions",
        "",
        "```text",
        "selected_score(u,c,i,k) = raw or condition-centered slice score chosen by v3 policy",
        "base_score(u,k)        = unweighted mean of condition means, so frequent condition choice does not dominate the base score",
        "react_score(u,c,k)     = condition mean minus base_score",
        "choice(u,c)            = observed condition distribution for the author",
        "residual_quality       = inverse of within-condition slice instability",
        "```",
        "",
        "## Coverage",
        "",
        f"- Profile rows: `{len(profiles)}`",
        f"- React rows: `{len(react)}`",
        f"- Choice rows: `{len(choice)}`",
        f"- Scenarios: `{profiles['scenario'].nunique() if not profiles.empty else 0}`",
        f"- Users: `{profiles['user_id'].nunique() if not profiles.empty else 0}`",
        "",
        "## Score Quality Counts",
        "",
        quality_counts.to_markdown(index=False),
        "",
        "## Score Role Counts",
        "",
        role_counts.to_markdown(index=False),
        "",
        "## Factor Summary",
        "",
        factor_summary.round(4).to_markdown(index=False),
        "",
        "## Scenario Summary",
        "",
        scenario_summary.round(4).to_markdown(index=False),
        "",
        "## Quality by Scenario",
        "",
        quality_summary.to_markdown(index=False),
        "",
        "## Release-Centered Cell Profiles",
        "",
        top_release[
            [
                "scenario",
                "factor",
                "user_id",
                "base_score",
                "react_amplitude",
                "residual_quality_score",
                "n_conditions",
                "n_slices",
                "score_quality",
            ]
        ]
        .head(20)
        .round(4)
        .to_markdown(index=False)
        if not top_release.empty
        else "None.",
        "",
        "## Interpretation",
        "",
        "- `base_score` is now protected from simple condition-choice frequency by averaging condition means equally.",
        "- `choice_influence_delta` is retained instead of erased; it measures how much the author's actual condition distribution moves the observed score away from the condition-balanced base.",
        "- `react_amplitude` is the current projective/CAPS-like signature strength.",
        "- `residual_quality_score` marks whether a profile row is stable enough for measurement use or should return to item-bank repair.",
        "",
        "## Artifacts",
        "",
        f"- `{output_dir / 'user_factor_profiles.csv'}`",
        f"- `{output_dir / 'react_condition_scores.csv'}`",
        f"- `{output_dir / 'choice_profiles.csv'}`",
        f"- `{output_dir / 'factor_profile_summary.csv'}`",
        f"- `{output_dir / 'scenario_profile_summary.csv'}`",
        f"- `{output_dir / 'quality_summary.csv'}`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    slice_scores = pd.read_csv(args.slice_scores, dtype={"user_id": str, "slice_obs_id": str})
    policy = pd.read_csv(args.policy)
    selected = build_selected_long(slice_scores, policy)
    profiles, react, choice = build_profiles(
        selected,
        min_slices=args.min_slices,
        min_conditions=args.min_conditions,
        recommended_g=args.recommended_g,
        recommended_residual_sd=args.recommended_residual_sd,
    )
    factor_summary, scenario_summary, quality_summary = summarize_profiles(profiles)
    profiles.to_csv(output_dir / "user_factor_profiles.csv", index=False)
    react.to_csv(output_dir / "react_condition_scores.csv", index=False)
    choice.to_csv(output_dir / "choice_profiles.csv", index=False)
    factor_summary.to_csv(output_dir / "factor_profile_summary.csv", index=False)
    scenario_summary.to_csv(output_dir / "scenario_profile_summary.csv", index=False)
    quality_summary.to_csv(output_dir / "quality_summary.csv", index=False)
    run_config = {
        "slice_scores": args.slice_scores,
        "policy": args.policy,
        "min_slices": args.min_slices,
        "min_conditions": args.min_conditions,
        "recommended_g": args.recommended_g,
        "recommended_residual_sd": args.recommended_residual_sd,
    }
    (output_dir / "run_config.json").write_text(json.dumps(run_config, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(Path(args.report_path), profiles, react, choice, factor_summary, scenario_summary, quality_summary, output_dir)
    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "profile_rows": int(len(profiles)),
                "react_rows": int(len(react)),
                "choice_rows": int(len(choice)),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
