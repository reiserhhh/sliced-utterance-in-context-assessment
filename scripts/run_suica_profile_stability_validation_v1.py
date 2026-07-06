#!/usr/bin/env python
"""Validate policy-aware SUICA profiles across scenario splits.

The profile scorer creates author-level base/react/choice/residual profiles.
This script asks whether the same author's profile is more similar across
independent scenario designs than a random author's profile.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


COMPONENTS = {
    "base": "base_score",
    "react": "react_amplitude",
    "choice_influence": "choice_influence_delta",
    "residual_quality": "residual_quality_score",
}

QUALITY_SCOPES = {
    "all": None,
    "recommended_or_exploratory": {"recommended", "exploratory"},
    "recommended_only": {"recommended"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SUICA profile stability validation v1.")
    parser.add_argument("--profiles", default="results/suica_policy_profile_scorer_v1/user_factor_profiles.csv")
    parser.add_argument("--output-dir", default="results/suica_profile_stability_validation_v1")
    parser.add_argument("--report-path", default="reports/suica_profile_stability_validation_v1.md")
    parser.add_argument("--min-overlap-users", type=int, default=30)
    parser.add_argument("--min-dimensions", type=int, default=3)
    parser.add_argument("--permutation-count", type=int, default=200)
    parser.add_argument("--max-random-pairs", type=int, default=20000)
    parser.add_argument("--random-seed", type=int, default=44)
    return parser.parse_args()


def scenario_family(scenario: str) -> str:
    """Classify a scenario into a coarse corpus/source family."""
    scenario = str(scenario)
    if scenario.startswith("essays_"):
        return "essays"
    if scenario.startswith("pandora_"):
        return "pandora"
    if scenario.startswith("x_"):
        return "x_market"
    return "other"


def safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    """Pearson correlation on finite entries."""
    mask = np.isfinite(a) & np.isfinite(b)
    if int(mask.sum()) < 3:
        return float("nan")
    aa = a[mask]
    bb = b[mask]
    aa = aa - float(np.mean(aa))
    bb = bb - float(np.mean(bb))
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if denom <= 0.0:
        return float("nan")
    return float(np.dot(aa, bb) / denom)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity on finite entries."""
    mask = np.isfinite(a) & np.isfinite(b)
    if int(mask.sum()) < 1:
        return float("nan")
    aa = a[mask]
    bb = b[mask]
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if denom <= 0:
        return float("nan")
    return float(np.dot(aa, bb) / denom)


def auc_probability(actual: np.ndarray, random_values: np.ndarray) -> float:
    """Return P(actual > random) + 0.5 P(tie), equivalent to AUC."""
    actual = actual[np.isfinite(actual)]
    random_values = random_values[np.isfinite(random_values)]
    if len(actual) == 0 or len(random_values) == 0:
        return float("nan")
    sorted_random = np.sort(random_values)
    left = np.searchsorted(sorted_random, actual, side="left")
    right = np.searchsorted(sorted_random, actual, side="right")
    wins = left
    ties = right - left
    return float((wins.sum() + 0.5 * ties.sum()) / (len(actual) * len(sorted_random)))


def make_wide(profiles: pd.DataFrame, scenario: str, component: str, quality_scope: str) -> pd.DataFrame:
    """Build user x factor matrix for one scenario/component/scope."""
    work = profiles.loc[profiles["scenario"].astype(str).eq(str(scenario))].copy()
    allowed = QUALITY_SCOPES[quality_scope]
    if allowed is not None:
        work = work.loc[work["score_quality"].isin(allowed)].copy()
    if work.empty:
        return pd.DataFrame()
    value_col = COMPONENTS[component]
    wide = work.pivot_table(index="user_id", columns="factor", values=value_col, aggfunc="mean")
    return wide.sort_index(axis=0).sort_index(axis=1)


def row_metrics(a: pd.DataFrame, b: pd.DataFrame, *, min_dimensions: int) -> pd.DataFrame:
    """Compute same-row profile cosine/correlation for aligned wide matrices."""
    users = sorted(set(a.index.astype(str)).intersection(set(b.index.astype(str))))
    factors = sorted(set(a.columns.astype(str)).intersection(set(b.columns.astype(str))))
    rows: list[dict[str, Any]] = []
    if not users or not factors:
        return pd.DataFrame()
    aa = a.loc[users, factors].to_numpy(float)
    bb = b.loc[users, factors].to_numpy(float)
    for idx, user_id in enumerate(users):
        valid_dims = int((np.isfinite(aa[idx]) & np.isfinite(bb[idx])).sum())
        if valid_dims < min_dimensions:
            continue
        rows.append(
            {
                "user_id": user_id,
                "valid_dimensions": valid_dims,
                "profile_cosine": cosine(aa[idx], bb[idx]),
                "profile_pearson_r": safe_corr(aa[idx], bb[idx]),
            }
        )
    return pd.DataFrame(rows)


def random_profile_values(
    a: pd.DataFrame,
    b: pd.DataFrame,
    users: list[str],
    factors: list[str],
    *,
    min_dimensions: int,
    rng: np.random.Generator,
    permutation_count: int,
    max_random_pairs: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build random-pair cosine and Pearson distributions."""
    aa = a.loc[users, factors].to_numpy(float)
    bb = b.loc[users, factors].to_numpy(float)
    cos_values: list[float] = []
    corr_values: list[float] = []
    random_medians: list[float] = []
    n = len(users)
    pairs_per_permutation = max(1, min(n, int(np.ceil(max_random_pairs / max(1, permutation_count)))))
    for _ in range(permutation_count):
        order = rng.permutation(n)
        perm_cos: list[float] = []
        for i, j in enumerate(order[:pairs_per_permutation]):
            valid_dims = int((np.isfinite(aa[i]) & np.isfinite(bb[j])).sum())
            if valid_dims < min_dimensions:
                continue
            cos_val = cosine(aa[i], bb[j])
            cos_values.append(cos_val)
            perm_cos.append(cos_val)
            corr_values.append(safe_corr(aa[i], bb[j]))
        if perm_cos:
            random_medians.append(float(np.nanmedian(np.asarray(perm_cos, dtype=float))))
    return np.asarray(cos_values, dtype=float), np.asarray(corr_values, dtype=float), np.asarray(random_medians, dtype=float)


def factor_correlations(a: pd.DataFrame, b: pd.DataFrame, users: list[str], factors: list[str]) -> pd.DataFrame:
    """Compute factor-wise cross-scenario correlations over shared users."""
    rows: list[dict[str, Any]] = []
    for factor in factors:
        x = a.loc[users, factor].to_numpy(float)
        y = b.loc[users, factor].to_numpy(float)
        mask = np.isfinite(x) & np.isfinite(y)
        rows.append(
            {
                "factor": factor,
                "n_users": int(mask.sum()),
                "factor_pearson_r": safe_corr(x, y),
            }
        )
    return pd.DataFrame(rows)


def compare_pair(
    profiles: pd.DataFrame,
    scenario_a: str,
    scenario_b: str,
    component: str,
    quality_scope: str,
    *,
    min_dimensions: int,
    permutation_count: int,
    max_random_pairs: int,
    rng: np.random.Generator,
) -> tuple[dict[str, Any] | None, pd.DataFrame, pd.DataFrame]:
    """Compare one scenario pair for one component and quality scope."""
    wide_a = make_wide(profiles, scenario_a, component, quality_scope)
    wide_b = make_wide(profiles, scenario_b, component, quality_scope)
    if wide_a.empty or wide_b.empty:
        return None, pd.DataFrame(), pd.DataFrame()
    users = sorted(set(wide_a.index.astype(str)).intersection(set(wide_b.index.astype(str))))
    factors = sorted(set(wide_a.columns.astype(str)).intersection(set(wide_b.columns.astype(str))))
    if not users or len(factors) < min_dimensions:
        return None, pd.DataFrame(), pd.DataFrame()
    actual = row_metrics(wide_a, wide_b, min_dimensions=min_dimensions)
    if actual.empty:
        return None, pd.DataFrame(), pd.DataFrame()
    actual["scenario_a"] = scenario_a
    actual["scenario_b"] = scenario_b
    actual["component"] = component
    actual["quality_scope"] = quality_scope
    actual_cos = actual["profile_cosine"].to_numpy(float)
    actual_corr = actual["profile_pearson_r"].to_numpy(float)
    random_cos, random_corr, random_medians_arr = random_profile_values(
        wide_a,
        wide_b,
        users=actual["user_id"].astype(str).tolist(),
        factors=factors,
        min_dimensions=min_dimensions,
        rng=rng,
        permutation_count=permutation_count,
        max_random_pairs=max_random_pairs,
    )
    random_p = (
        float((np.sum(random_medians_arr >= np.nanmedian(actual_cos)) + 1) / (len(random_medians_arr) + 1))
        if len(random_medians_arr)
        else float("nan")
    )
    factor_corr = factor_correlations(wide_a, wide_b, actual["user_id"].astype(str).tolist(), factors)
    factor_corr["scenario_a"] = scenario_a
    factor_corr["scenario_b"] = scenario_b
    factor_corr["component"] = component
    factor_corr["quality_scope"] = quality_scope
    summary = {
        "scenario_a": scenario_a,
        "scenario_b": scenario_b,
        "scenario_family": scenario_family(scenario_a),
        "component": component,
        "quality_scope": quality_scope,
        "n_users": int(len(actual)),
        "n_factors": int(len(factors)),
        "median_valid_dimensions": float(actual["valid_dimensions"].median()),
        "actual_median_cosine": float(np.nanmedian(actual_cos)),
        "actual_mean_cosine": float(np.nanmean(actual_cos)),
        "actual_median_pearson_r": float(np.nanmedian(actual_corr)),
        "actual_mean_pearson_r": float(np.nanmean(actual_corr)),
        "random_median_cosine_mean": float(np.nanmean(random_medians_arr)) if len(random_medians_arr) else np.nan,
        "random_median_cosine_sd": float(np.nanstd(random_medians_arr)) if len(random_medians_arr) else np.nan,
        "random_p_median_cosine": random_p,
        "cosine_auc_vs_random": auc_probability(actual_cos, random_cos),
        "pearson_auc_vs_random": auc_probability(actual_corr, random_corr),
        "mean_factor_pearson_r": float(factor_corr["factor_pearson_r"].mean(skipna=True)),
        "median_factor_pearson_r": float(factor_corr["factor_pearson_r"].median(skipna=True)),
    }
    return summary, actual, factor_corr


def run_validation(profiles: pd.DataFrame, args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run all eligible scenario-pair validations."""
    rng = np.random.default_rng(args.random_seed)
    scenarios = sorted(profiles["scenario"].dropna().astype(str).unique().tolist())
    summaries: list[dict[str, Any]] = []
    actual_rows: list[pd.DataFrame] = []
    factor_rows: list[pd.DataFrame] = []
    user_sets = {scenario: set(profiles.loc[profiles["scenario"].astype(str).eq(scenario), "user_id"].astype(str)) for scenario in scenarios}
    for scenario_a, scenario_b in combinations(scenarios, 2):
        overlap = len(user_sets[scenario_a].intersection(user_sets[scenario_b]))
        if overlap < args.min_overlap_users:
            continue
        for component in COMPONENTS:
            for quality_scope in QUALITY_SCOPES:
                summary, actual, factor_corr = compare_pair(
                    profiles,
                    scenario_a,
                    scenario_b,
                    component,
                    quality_scope,
                    min_dimensions=args.min_dimensions,
                    permutation_count=args.permutation_count,
                    max_random_pairs=args.max_random_pairs,
                    rng=rng,
                )
                if summary is None:
                    continue
                summaries.append(summary)
                actual_rows.append(actual)
                factor_rows.append(factor_corr)
    return (
        pd.DataFrame(summaries),
        pd.concat(actual_rows, ignore_index=True) if actual_rows else pd.DataFrame(),
        pd.concat(factor_rows, ignore_index=True) if factor_rows else pd.DataFrame(),
    )


def write_report(path: Path, pair_summary: pd.DataFrame, actual: pd.DataFrame, factor_corr: pd.DataFrame, output_dir: Path) -> None:
    """Write a compact validation report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if pair_summary.empty:
        path.write_text("# SUICA Profile Stability Validation v1\n\nNo eligible scenario pairs.\n", encoding="utf-8")
        return
    main = pair_summary.loc[pair_summary["quality_scope"].eq("all")].copy()
    scope_summary = (
        pair_summary.groupby(["component", "quality_scope"], as_index=False)
        .agg(
            n_pairs=("scenario_a", "size"),
            median_actual_cosine=("actual_median_cosine", "median"),
            median_random_cosine=("random_median_cosine_mean", "median"),
            median_auc=("cosine_auc_vs_random", "median"),
            median_factor_r=("median_factor_pearson_r", "median"),
        )
        .sort_values(["quality_scope", "median_auc"], ascending=[True, False])
    )
    family_summary = (
        main.groupby(["scenario_family", "component"], as_index=False)
        .agg(
            n_pairs=("scenario_a", "size"),
            median_actual_cosine=("actual_median_cosine", "median"),
            median_auc=("cosine_auc_vs_random", "median"),
            median_factor_r=("median_factor_pearson_r", "median"),
        )
        .sort_values(["scenario_family", "median_auc"], ascending=[True, False])
    )
    strongest = pair_summary.sort_values(["cosine_auc_vs_random", "actual_median_cosine"], ascending=[False, False]).head(20)
    weakest = pair_summary.sort_values(["cosine_auc_vs_random", "actual_median_cosine"], ascending=[True, True]).head(20)
    factor_summary = (
        factor_corr.groupby(["component", "quality_scope", "factor"], as_index=False)
        .agg(mean_factor_r=("factor_pearson_r", "mean"), median_n_users=("n_users", "median"))
        .sort_values(["quality_scope", "component", "mean_factor_r"], ascending=[True, True, False])
    )
    lines = [
        "# SUICA Profile Stability Validation v1",
        "",
        "## Purpose",
        "",
        "This validates whether policy-aware SUICA author profiles are stable across independent scenario/split designs. The test compares same-user profile similarity against random-user controls.",
        "",
        "## Components Tested",
        "",
        "- `base`: condition-balanced author position.",
        "- `react`: amplitude of condition-specific response signatures.",
        "- `choice_influence`: how observed condition choice shifts the score away from condition-balanced base.",
        "- `residual_quality`: profile stability / item-bank quality signal.",
        "",
        "## Scope Summary",
        "",
        scope_summary.round(4).to_markdown(index=False),
        "",
        "## Corpus/Scenario-Family Summary (`quality_scope=all`)",
        "",
        family_summary.round(4).to_markdown(index=False),
        "",
        "## Strongest Same-User Signals",
        "",
        strongest[
            [
                "scenario_a",
                "scenario_b",
                "component",
                "quality_scope",
                "n_users",
                "actual_median_cosine",
                "random_median_cosine_mean",
                "cosine_auc_vs_random",
                "median_factor_pearson_r",
                "random_p_median_cosine",
            ]
        ]
        .round(4)
        .to_markdown(index=False),
        "",
        "## Weakest / Problem Cases",
        "",
        weakest[
            [
                "scenario_a",
                "scenario_b",
                "component",
                "quality_scope",
                "n_users",
                "actual_median_cosine",
                "random_median_cosine_mean",
                "cosine_auc_vs_random",
                "median_factor_pearson_r",
                "random_p_median_cosine",
            ]
        ]
        .round(4)
        .to_markdown(index=False),
        "",
        "## Factor-Level Stability Summary",
        "",
        factor_summary.head(80).round(4).to_markdown(index=False),
        "",
        "## Interpretation",
        "",
        "- Same-user AUC above random supports author-level measurement signal.",
        "- High cosine with weak factor-wise correlation means profile geometry is stable but the factor scale still needs calibration.",
        "- `recommended_only` can be unstable when too few factors/users survive; treat it as a conservative stress test, not the main estimate.",
        "- The next development target is to improve weak components without inflating same-user similarity through topic/domain routine.",
        "",
        "## Artifacts",
        "",
        f"- `{output_dir / 'pair_component_stability.csv'}`",
        f"- `{output_dir / 'profile_similarity_rows.csv'}`",
        f"- `{output_dir / 'factor_component_stability.csv'}`",
        f"- `{output_dir / 'run_config.json'}`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    profiles = pd.read_csv(args.profiles, dtype={"user_id": str})
    pair_summary, actual, factor_corr = run_validation(profiles, args)
    pair_summary.to_csv(output_dir / "pair_component_stability.csv", index=False)
    actual.to_csv(output_dir / "profile_similarity_rows.csv", index=False)
    factor_corr.to_csv(output_dir / "factor_component_stability.csv", index=False)
    run_config = {
        "profiles": args.profiles,
        "min_overlap_users": args.min_overlap_users,
        "min_dimensions": args.min_dimensions,
        "permutation_count": args.permutation_count,
        "max_random_pairs": args.max_random_pairs,
        "random_seed": args.random_seed,
        "components": COMPONENTS,
        "quality_scopes": {key: sorted(val) if val is not None else None for key, val in QUALITY_SCOPES.items()},
    }
    (output_dir / "run_config.json").write_text(json.dumps(run_config, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(Path(args.report_path), pair_summary, actual, factor_corr, output_dir)
    print(json.dumps({"output_dir": str(output_dir), "pair_rows": int(len(pair_summary)), "actual_rows": int(len(actual))}, indent=2))


if __name__ == "__main__":
    main()
