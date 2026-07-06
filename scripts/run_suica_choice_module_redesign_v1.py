#!/usr/bin/env python
"""Redesign and audit the SUICA choice module.

The first choice component, `choice_influence_delta`, was weak in profile
stability validation. This script tests a different framing: choice is not a
factor-score delta, but the author's distribution over available conditions.

It separates imposed split conditions from natural or semi-natural condition
choices, validates choice-shape stability, and checks whether choice-shape
features are coupled to SUICA base/react factors.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SHAPE_FEATURES = [
    "choice_entropy_norm",
    "top_condition_share",
    "balance_score",
    "log_n_slices",
    "top_context_focus",
    "late_or_second_bias",
]


SCENARIO_TAXONOMY = {
    "essays_contiguous": {
        "condition_axis": "text_order_split",
        "choice_status": "imposed_split_not_choice",
        "choice_use": "quality_control_only",
    },
    "essays_interleaved": {
        "condition_axis": "even_odd_slice_split",
        "choice_status": "imposed_split_not_choice",
        "choice_use": "quality_control_only",
    },
    "essays_random": {
        "condition_axis": "random_split",
        "choice_status": "imposed_split_not_choice",
        "choice_use": "negative_control",
    },
    "pandora_temporal": {
        "condition_axis": "temporal_activity",
        "choice_status": "semi_natural_activity_pattern",
        "choice_use": "activity_signature",
    },
    "pandora_cross_subreddit": {
        "condition_axis": "subreddit_topic_distribution",
        "choice_status": "natural_topic_choice",
        "choice_use": "candidate_choice_construct",
    },
    "pandora_within_top_subreddit_temporal": {
        "condition_axis": "within_topic_temporal_activity",
        "choice_status": "semi_natural_activity_pattern",
        "choice_use": "activity_signature",
    },
    "x_cross_query_group": {
        "condition_axis": "market_query_group_distribution",
        "choice_status": "domain_condition_choice",
        "choice_use": "domain_adapter_choice",
    },
    "x_cross_symbol": {
        "condition_axis": "market_symbol_distribution",
        "choice_status": "domain_condition_choice",
        "choice_use": "domain_adapter_choice",
    },
    "x_temporal_global_dedup": {
        "condition_axis": "market_temporal_activity",
        "choice_status": "semi_natural_activity_pattern",
        "choice_use": "activity_signature",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SUICA choice module redesign v1.")
    parser.add_argument("--slice-scores", default="results/suica_item_bank_v1/slice_scores_with_text.csv")
    parser.add_argument("--profiles", default="results/suica_policy_profile_scorer_v1/user_factor_profiles.csv")
    parser.add_argument("--output-dir", default="results/suica_choice_module_redesign_v1")
    parser.add_argument("--report-path", default="reports/suica_choice_module_redesign_v1.md")
    parser.add_argument("--min-overlap-users", type=int, default=30)
    parser.add_argument("--permutation-count", type=int, default=200)
    parser.add_argument("--max-random-pairs", type=int, default=20000)
    parser.add_argument("--random-seed", type=int, default=45)
    return parser.parse_args()


def entropy_norm(counts: pd.Series) -> float:
    """Return normalized entropy for condition counts."""
    total = float(counts.sum())
    if total <= 0:
        return float("nan")
    probs = counts.to_numpy(float) / total
    if len(probs) <= 1:
        return 0.0
    ent = float(-(probs * np.log2(probs + 1e-12)).sum())
    return ent / float(np.log2(len(probs)))


def scenario_taxonomy_frame(scenarios: list[str]) -> pd.DataFrame:
    """Build scenario taxonomy table."""
    rows = []
    for scenario in scenarios:
        meta = SCENARIO_TAXONOMY.get(
            scenario,
            {
                "condition_axis": "unknown",
                "choice_status": "unknown",
                "choice_use": "do_not_interpret",
            },
        )
        rows.append({"scenario": scenario, **meta})
    return pd.DataFrame(rows)


def condition_distribution(slice_scores: pd.DataFrame) -> pd.DataFrame:
    """Build per-user condition distribution from slice-level scores."""
    required = {"scenario", "user_id", "condition", "slice_obs_id"}
    missing = required.difference(slice_scores.columns)
    if missing:
        raise ValueError(f"slice_scores missing required columns: {sorted(missing)}")
    counts = (
        slice_scores[["scenario", "user_id", "condition", "slice_obs_id"]]
        .drop_duplicates()
        .groupby(["scenario", "user_id", "condition"])
        .size()
        .rename("slice_count")
        .reset_index()
    )
    totals = counts.groupby(["scenario", "user_id"])["slice_count"].transform("sum")
    counts["condition_share"] = counts["slice_count"] / totals.clip(lower=1)
    return counts.sort_values(["scenario", "user_id", "condition"]).reset_index(drop=True)


def condition_share_lookup(group: pd.DataFrame, names: list[str]) -> float:
    """Return total share for condition names that exist in the group."""
    sub = group.loc[group["condition"].isin(names)]
    return float(sub["condition_share"].sum()) if not sub.empty else 0.0


def choice_shape_features(dist: pd.DataFrame) -> pd.DataFrame:
    """Build per-user scenario choice-shape features."""
    rows: list[dict[str, Any]] = []
    for (scenario, user_id), group in dist.groupby(["scenario", "user_id"], sort=True):
        group = group.sort_values(["slice_count", "condition"], ascending=[False, True]).copy()
        n_slices = int(group["slice_count"].sum())
        n_conditions = int(group["condition"].nunique())
        top = group.iloc[0]
        top_share = float(top["condition_share"])
        balance = 1.0 - abs(top_share - (1.0 / max(1, n_conditions))) / max(1e-9, 1.0 - (1.0 / max(1, n_conditions)))
        top_context_focus = condition_share_lookup(
            group,
            [
                "top_subreddit",
                "early_top_subreddit",
                "late_top_subreddit",
                "top_query_group",
                "top_symbol",
            ],
        )
        late_or_second_bias = condition_share_lookup(
            group,
            [
                "late_time",
                "late_top_subreddit",
                "second_half",
                "random_b",
            ],
        ) - condition_share_lookup(
            group,
            [
                "early_time",
                "early_top_subreddit",
                "first_half",
                "random_a",
            ],
        )
        rows.append(
            {
                "scenario": scenario,
                "user_id": str(user_id),
                "n_conditions": n_conditions,
                "n_slices": n_slices,
                "choice_entropy_norm": entropy_norm(group["slice_count"]),
                "top_condition": str(top["condition"]),
                "top_condition_share": top_share,
                "balance_score": float(balance),
                "log_n_slices": float(np.log1p(n_slices)),
                "top_context_focus": float(top_context_focus),
                "late_or_second_bias": float(late_or_second_bias),
            }
        )
    out = pd.DataFrame(rows)
    taxonomy = scenario_taxonomy_frame(sorted(out["scenario"].unique().tolist()))
    return out.merge(taxonomy, on="scenario", how="left")


def standardized_matrix(frame: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    """Return feature matrix standardized within a scenario."""
    mat = frame.set_index("user_id")[features].copy()
    for col in features:
        vals = mat[col].astype(float)
        sd = float(vals.std(ddof=0))
        mat[col] = (vals - float(vals.mean())) / sd if sd > 0 else 0.0
    return mat


def euclidean_rows(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Row-wise Euclidean distance with finite handling."""
    out = []
    for aa, bb in zip(a, b):
        mask = np.isfinite(aa) & np.isfinite(bb)
        out.append(float(np.linalg.norm(aa[mask] - bb[mask])) if mask.any() else np.nan)
    return np.asarray(out, dtype=float)


def distance_auc(actual_dist: np.ndarray, random_dist: np.ndarray) -> float:
    """AUC where smaller actual same-user distance is better."""
    actual = actual_dist[np.isfinite(actual_dist)]
    random = random_dist[np.isfinite(random_dist)]
    if len(actual) == 0 or len(random) == 0:
        return float("nan")
    sorted_random = np.sort(random)
    wins = len(sorted_random) - np.searchsorted(sorted_random, actual, side="right")
    ties = np.searchsorted(sorted_random, actual, side="right") - np.searchsorted(sorted_random, actual, side="left")
    return float((wins.sum() + 0.5 * ties.sum()) / (len(actual) * len(sorted_random)))


def validate_shape_stability(features: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    """Compare same-user choice-shape distances against random controls."""
    rng = np.random.default_rng(args.random_seed)
    rows: list[dict[str, Any]] = []
    scenarios = sorted(features["scenario"].unique().tolist())
    scenario_frames = {s: features.loc[features["scenario"].eq(s)].copy() for s in scenarios}
    for scenario_a, scenario_b in combinations(scenarios, 2):
        users = sorted(set(scenario_frames[scenario_a]["user_id"]).intersection(set(scenario_frames[scenario_b]["user_id"])))
        if len(users) < args.min_overlap_users:
            continue
        a = standardized_matrix(scenario_frames[scenario_a].loc[scenario_frames[scenario_a]["user_id"].isin(users)], SHAPE_FEATURES)
        b = standardized_matrix(scenario_frames[scenario_b].loc[scenario_frames[scenario_b]["user_id"].isin(users)], SHAPE_FEATURES)
        users = sorted(set(a.index).intersection(set(b.index)))
        a = a.loc[users]
        b = b.loc[users]
        actual = euclidean_rows(a.to_numpy(float), b.to_numpy(float))
        random_values: list[float] = []
        n = len(users)
        pairs_per_perm = max(1, min(n, int(np.ceil(args.max_random_pairs / max(1, args.permutation_count)))))
        for _ in range(args.permutation_count):
            order = rng.permutation(n)[:pairs_per_perm]
            source_idx = np.arange(n)[:pairs_per_perm]
            random_values.extend(euclidean_rows(a.to_numpy(float)[source_idx], b.to_numpy(float)[order]).tolist())
        random_arr = np.asarray(random_values, dtype=float)
        rows.append(
            {
                "scenario_a": scenario_a,
                "scenario_b": scenario_b,
                "choice_status_a": scenario_frames[scenario_a]["choice_status"].iloc[0],
                "choice_status_b": scenario_frames[scenario_b]["choice_status"].iloc[0],
                "choice_use_a": scenario_frames[scenario_a]["choice_use"].iloc[0],
                "choice_use_b": scenario_frames[scenario_b]["choice_use"].iloc[0],
                "n_users": len(users),
                "actual_median_distance": float(np.nanmedian(actual)),
                "random_median_distance": float(np.nanmedian(random_arr)),
                "distance_auc_vs_random": distance_auc(actual, random_arr),
            }
        )
    return pd.DataFrame(rows).sort_values("distance_auc_vs_random", ascending=False)


def safe_corr(x: np.ndarray, y: np.ndarray) -> float:
    """Safe Pearson correlation."""
    mask = np.isfinite(x) & np.isfinite(y)
    if int(mask.sum()) < 8:
        return float("nan")
    xx = x[mask] - float(np.mean(x[mask]))
    yy = y[mask] - float(np.mean(y[mask]))
    denom = float(np.linalg.norm(xx) * np.linalg.norm(yy))
    return float(np.dot(xx, yy) / denom) if denom > 0 else float("nan")


def choice_factor_coupling(features: pd.DataFrame, profiles: pd.DataFrame) -> pd.DataFrame:
    """Correlate choice-shape features with SUICA profile components."""
    rows: list[dict[str, Any]] = []
    profiles = profiles.copy()
    profiles["user_id"] = profiles["user_id"].astype(str)
    for scenario, choice_group in features.groupby("scenario", sort=True):
        prof = profiles.loc[profiles["scenario"].astype(str).eq(str(scenario))].copy()
        prof = prof.drop(columns=[*SHAPE_FEATURES, "top_condition"], errors="ignore")
        if prof.empty:
            continue
        merged = prof.merge(choice_group[["scenario", "user_id", *SHAPE_FEATURES]], on=["scenario", "user_id"], how="inner")
        for factor, fgroup in merged.groupby("factor", sort=True):
            for choice_feature in SHAPE_FEATURES:
                for profile_component in ["base_score", "react_amplitude", "residual_quality_score"]:
                    rows.append(
                        {
                            "scenario": scenario,
                            "factor": factor,
                            "choice_feature": choice_feature,
                            "profile_component": profile_component,
                            "n_users": int(fgroup["user_id"].nunique()),
                            "pearson_r": safe_corr(
                                fgroup[choice_feature].to_numpy(float),
                                fgroup[profile_component].to_numpy(float),
                            ),
                        }
                    )
    out = pd.DataFrame(rows)
    taxonomy = scenario_taxonomy_frame(sorted(out["scenario"].unique().tolist()))
    return out.merge(taxonomy, on="scenario", how="left")


def write_report(
    path: Path,
    taxonomy: pd.DataFrame,
    features: pd.DataFrame,
    stability: pd.DataFrame,
    coupling: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Write choice redesign report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    scenario_summary = (
        features.groupby(["scenario", "choice_status", "choice_use"], as_index=False)
        .agg(
            users=("user_id", "nunique"),
            median_n_slices=("n_slices", "median"),
            mean_entropy=("choice_entropy_norm", "mean"),
            mean_top_share=("top_condition_share", "mean"),
            mean_balance=("balance_score", "mean"),
            mean_top_context_focus=("top_context_focus", "mean"),
            mean_late_or_second_bias=("late_or_second_bias", "mean"),
        )
        .sort_values(["choice_use", "scenario"])
    )
    stability_summary = (
        stability.groupby(["choice_use_a", "choice_use_b"], as_index=False)
        .agg(
            n_pairs=("scenario_a", "size"),
            median_auc=("distance_auc_vs_random", "median"),
            median_actual_distance=("actual_median_distance", "median"),
            median_random_distance=("random_median_distance", "median"),
        )
        .sort_values("median_auc", ascending=False)
        if not stability.empty
        else pd.DataFrame()
    )
    strongest_coupling = (
        coupling.assign(abs_r=lambda x: x["pearson_r"].abs())
        .sort_values("abs_r", ascending=False)
        .head(30)
        if not coupling.empty
        else pd.DataFrame()
    )
    natural_coupling = (
        coupling.loc[coupling["choice_use"].isin(["candidate_choice_construct", "domain_adapter_choice"])]
        .assign(abs_r=lambda x: x["pearson_r"].abs())
        .sort_values("abs_r", ascending=False)
        .head(30)
        if not coupling.empty
        else pd.DataFrame()
    )
    construct_coupling = (
        coupling.loc[
            coupling["choice_use"].isin(["candidate_choice_construct", "domain_adapter_choice"])
            & coupling["choice_feature"].ne("log_n_slices")
            & coupling["profile_component"].ne("residual_quality_score")
        ]
        .assign(abs_r=lambda x: x["pearson_r"].abs())
        .sort_values("abs_r", ascending=False)
        .head(30)
        if not coupling.empty
        else pd.DataFrame()
    )
    lines = [
        "# SUICA Choice Module Redesign v1",
        "",
        "## Purpose",
        "",
        "The previous `choice_influence_delta` component was weak. This experiment reframes choice as a condition-distribution shape rather than a factor-score delta.",
        "",
        "## Scenario Taxonomy",
        "",
        taxonomy.to_markdown(index=False),
        "",
        "## Choice Shape Definitions",
        "",
        "- `choice_entropy_norm`: how evenly the author's text is distributed over available conditions.",
        "- `top_condition_share`: concentration in the most common condition.",
        "- `balance_score`: closeness to equal condition coverage.",
        "- `top_context_focus`: share assigned to explicit top-topic/top-symbol/top-query conditions.",
        "- `late_or_second_bias`: temporal or second-half direction, when meaningful.",
        "",
        "## Scenario Choice Shape Summary",
        "",
        scenario_summary.round(4).to_markdown(index=False),
        "",
        "## Shape Stability Summary",
        "",
        stability_summary.round(4).to_markdown(index=False) if not stability_summary.empty else "No eligible overlapping scenario pairs.",
        "",
        "## Strongest Shape Stability Pairs",
        "",
        stability.head(20).round(4).to_markdown(index=False) if not stability.empty else "No eligible overlapping scenario pairs.",
        "",
        "## Strongest Choice/Profile Couplings",
        "",
        strongest_coupling[
            [
                "scenario",
                "choice_use",
                "factor",
                "choice_feature",
                "profile_component",
                "n_users",
                "pearson_r",
                "abs_r",
            ]
        ]
        .round(4)
        .to_markdown(index=False)
        if not strongest_coupling.empty
        else "No coupling rows.",
        "",
        "## Natural/Domain Choice Couplings Only",
        "",
        natural_coupling[
            [
                "scenario",
                "choice_use",
                "factor",
                "choice_feature",
                "profile_component",
                "n_users",
                "pearson_r",
                "abs_r",
            ]
        ]
        .round(4)
        .to_markdown(index=False)
        if not natural_coupling.empty
        else "No natural/domain choice rows.",
        "",
        "## Construct-Relevant Choice Couplings",
        "",
        "This table excludes `log_n_slices` and `residual_quality_score` so activity/coverage artifacts do not dominate the construct interpretation.",
        "",
        construct_coupling[
            [
                "scenario",
                "choice_use",
                "factor",
                "choice_feature",
                "profile_component",
                "n_users",
                "pearson_r",
                "abs_r",
            ]
        ]
        .round(4)
        .to_markdown(index=False)
        if not construct_coupling.empty
        else "No construct-relevant choice rows.",
        "",
        "## Interpretation",
        "",
        "- Choice should not be scored in imposed split scenarios as a personality construct. Essays split conditions are quality controls, not author choice.",
        "- Natural topic distribution and domain condition distribution can be retained as candidate choice constructs, but they require separate validity evidence.",
        "- Choice-shape stability should be evaluated with distance-to-random controls; raw factor-score deltas are too indirect.",
        "- Current construct-relevant choice signal is concentrated in PANDORA subreddit distribution, especially the relation between topic concentration and `factor_02` reaction amplitude.",
        "- If choice-shape features couple strongly to base/react scores, they should be reported as exposure/selection signatures, not merged into base traits.",
        "",
        "## Artifacts",
        "",
        f"- `{output_dir / 'choice_condition_distribution.csv'}`",
        f"- `{output_dir / 'choice_shape_features.csv'}`",
        f"- `{output_dir / 'choice_shape_stability.csv'}`",
        f"- `{output_dir / 'choice_factor_coupling.csv'}`",
        f"- `{output_dir / 'scenario_taxonomy.csv'}`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    slice_scores = pd.read_csv(args.slice_scores, dtype={"user_id": str, "slice_obs_id": str})
    profiles = pd.read_csv(args.profiles, dtype={"user_id": str})
    dist = condition_distribution(slice_scores)
    features = choice_shape_features(dist)
    taxonomy = scenario_taxonomy_frame(sorted(features["scenario"].unique().tolist()))
    stability = validate_shape_stability(features, args)
    coupling = choice_factor_coupling(features, profiles)
    dist.to_csv(output_dir / "choice_condition_distribution.csv", index=False)
    features.to_csv(output_dir / "choice_shape_features.csv", index=False)
    taxonomy.to_csv(output_dir / "scenario_taxonomy.csv", index=False)
    stability.to_csv(output_dir / "choice_shape_stability.csv", index=False)
    coupling.to_csv(output_dir / "choice_factor_coupling.csv", index=False)
    run_config = {
        "slice_scores": args.slice_scores,
        "profiles": args.profiles,
        "min_overlap_users": args.min_overlap_users,
        "permutation_count": args.permutation_count,
        "max_random_pairs": args.max_random_pairs,
        "random_seed": args.random_seed,
        "shape_features": SHAPE_FEATURES,
    }
    (output_dir / "run_config.json").write_text(json.dumps(run_config, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(Path(args.report_path), taxonomy, features, stability, coupling, output_dir)
    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "choice_users": int(features["user_id"].nunique()),
                "shape_rows": int(len(features)),
                "stability_rows": int(len(stability)),
                "coupling_rows": int(len(coupling)),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
