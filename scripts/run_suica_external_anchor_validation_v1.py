#!/usr/bin/env python
"""Validate frozen SUICA profiles against external personality anchors.

This is an external validity audit, not a predictor training script. Big5 and
MBTI labels are used only after SUICA scores are frozen, and results are
reported as anchor correlations rather than proof that SUICA equals those
scales.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:  # scipy is optional in this repo.
    from scipy import stats  # type: ignore
except Exception:  # pragma: no cover - fallback covered by correlation outputs.
    stats = None


BIG5 = ["Extraversion", "Neuroticism", "Agreeableness", "Conscientiousness", "Openness"]
MBTI = ["EI_cont", "SN_cont", "TF_cont", "JP_cont"]
PROFILE_COMPONENTS = ["base_score", "react_amplitude", "residual_quality_score"]
CHOICE_FEATURES = [
    "choice_entropy_norm",
    "top_condition_share",
    "balance_score",
    "log_n_slices",
    "top_context_focus",
    "late_or_second_bias",
]
QUALITY_SCOPES = {
    "all": None,
    "recommended_or_exploratory": {"recommended", "exploratory"},
    "recommended_only": {"recommended"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SUICA external anchor validation v1.")
    parser.add_argument("--profiles", default="results/suica_policy_profile_scorer_v1/user_factor_profiles.csv")
    parser.add_argument("--choice-features", default="results/suica_choice_module_redesign_v1/choice_shape_features.csv")
    parser.add_argument("--pandora-big5", default="data_sets/prepared/pandora_official/pandora_official_big5_prepared.csv")
    parser.add_argument("--essays-big5", default="data_sets/prepared/big5/essays_original_prepared.csv")
    parser.add_argument("--bridge-strict", default="data_sets/prepared/pandora_official/bridge/pandora_official_bridge_strict377.csv")
    parser.add_argument(
        "--bridge-supplementary",
        default="data_sets/prepared/pandora_official/bridge/pandora_official_bridge_supplementary393.csv",
    )
    parser.add_argument("--output-dir", default="results/suica_external_anchor_validation_v1")
    parser.add_argument("--report-path", default="reports/suica_external_anchor_validation_v1.md")
    parser.add_argument("--min-n", type=int, default=80)
    return parser.parse_args()


def safe_corr(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Pearson correlation and p-value when enough finite data exist."""
    mask = np.isfinite(x) & np.isfinite(y)
    n = int(mask.sum())
    if n < 3:
        return float("nan"), float("nan")
    xx = x[mask]
    yy = y[mask]
    if float(np.std(xx)) == 0.0 or float(np.std(yy)) == 0.0:
        return float("nan"), float("nan")
    if stats is not None:
        res = stats.pearsonr(xx, yy)
        return float(res.statistic), float(res.pvalue)
    xx = xx - float(np.mean(xx))
    yy = yy - float(np.mean(yy))
    denom = float(np.linalg.norm(xx) * np.linalg.norm(yy))
    return (float(np.dot(xx, yy) / denom), float("nan")) if denom > 0 else (float("nan"), float("nan"))


def safe_spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman correlation using scipy or rank fallback."""
    mask = np.isfinite(x) & np.isfinite(y)
    if int(mask.sum()) < 3:
        return float("nan")
    xx = x[mask]
    yy = y[mask]
    if float(np.std(xx)) == 0.0 or float(np.std(yy)) == 0.0:
        return float("nan")
    if stats is not None:
        return float(stats.spearmanr(xx, yy).statistic)
    return safe_corr(pd.Series(xx).rank().to_numpy(float), pd.Series(yy).rank().to_numpy(float))[0]


def benjamini_hochberg(p_values: pd.Series) -> pd.Series:
    """Benjamini-Hochberg FDR q-values preserving index order."""
    p = pd.to_numeric(p_values, errors="coerce")
    q = pd.Series(np.nan, index=p.index, dtype=float)
    valid = p.dropna()
    if valid.empty:
        return q
    order = valid.sort_values().index.to_list()
    m = len(order)
    prev = 1.0
    for rank, idx in reversed(list(enumerate(order, start=1))):
        val = min(prev, float(valid.loc[idx]) * m / rank)
        q.loc[idx] = val
        prev = val
    return q.clip(upper=1.0)


def load_label_sources(args: argparse.Namespace) -> list[dict[str, Any]]:
    """Load external anchor tables with source metadata."""
    specs = [
        {
            "label_source": "pandora_big5",
            "path": args.pandora_big5,
            "targets": BIG5,
            "anchor_type": "Big5_continuous",
            "evidence_strength": "primary_pandora_big5",
        },
        {
            "label_source": "essays_big5_binary",
            "path": args.essays_big5,
            "targets": BIG5,
            "anchor_type": "Big5_binary",
            "evidence_strength": "external_binary_big5",
        },
        {
            "label_source": "bridge_strict_big5_mbti",
            "path": args.bridge_strict,
            "targets": [*BIG5, *MBTI],
            "anchor_type": "Bridge_Big5_MBTI",
            "evidence_strength": "small_matched_bridge_primary",
        },
        {
            "label_source": "bridge_supplementary_big5_mbti",
            "path": args.bridge_supplementary,
            "targets": [*BIG5, *MBTI],
            "anchor_type": "Bridge_Big5_MBTI",
            "evidence_strength": "small_matched_bridge_supplementary",
        },
    ]
    sources: list[dict[str, Any]] = []
    for spec in specs:
        path = Path(spec["path"])
        if not path.exists():
            continue
        frame = pd.read_csv(path, dtype={"user_id": str})
        targets = [target for target in spec["targets"] if target in frame.columns]
        if not targets:
            continue
        sources.append({**spec, "frame": frame[["user_id", *targets]].copy(), "targets": targets})
    return sources


def scenario_label_compatibility(scenario: str, label_source: str) -> bool:
    """Restrict label sources to matching corpora."""
    if scenario.startswith("essays_"):
        return label_source == "essays_big5_binary"
    if scenario.startswith("pandora_"):
        return label_source.startswith("pandora_") or label_source.startswith("bridge_")
    return False


def apply_quality_scope(frame: pd.DataFrame, scope: str) -> pd.DataFrame:
    """Filter profile rows by quality scope."""
    allowed = QUALITY_SCOPES[scope]
    if allowed is None:
        return frame
    return frame.loc[frame["score_quality"].isin(allowed)].copy()


def correlate_profile_components(profiles: pd.DataFrame, label_sources: list[dict[str, Any]], min_n: int) -> pd.DataFrame:
    """Correlate SUICA factor components with external anchors."""
    rows: list[dict[str, Any]] = []
    profiles = profiles.copy()
    profiles["user_id"] = profiles["user_id"].astype(str)
    for scenario, scenario_profiles in profiles.groupby("scenario", sort=True):
        for source in label_sources:
            label_source = str(source["label_source"])
            if not scenario_label_compatibility(str(scenario), label_source):
                continue
            labels = source["frame"]
            for scope in QUALITY_SCOPES:
                scoped = apply_quality_scope(scenario_profiles, scope)
                if scoped.empty:
                    continue
                merged = scoped.merge(labels, on="user_id", how="inner")
                if merged.empty:
                    continue
                for factor, fgroup in merged.groupby("factor", sort=True):
                    for component in PROFILE_COMPONENTS:
                        if component not in fgroup.columns:
                            continue
                        for target in source["targets"]:
                            sub = fgroup[[component, target]].dropna()
                            n = int(len(sub))
                            if n < min_n:
                                continue
                            pearson_r, p_value = safe_corr(sub[component].to_numpy(float), sub[target].to_numpy(float))
                            rows.append(
                                {
                                    "scenario": scenario,
                                    "label_source": label_source,
                                    "anchor_type": source["anchor_type"],
                                    "evidence_strength": source["evidence_strength"],
                                    "quality_scope": scope,
                                    "factor": factor,
                                    "component": component,
                                    "target": target,
                                    "n": n,
                                    "pearson_r": pearson_r,
                                    "spearman_rho": safe_spearman(sub[component].to_numpy(float), sub[target].to_numpy(float)),
                                    "p_value": p_value,
                                }
                            )
    out = pd.DataFrame(rows)
    if not out.empty:
        out["abs_pearson_r"] = out["pearson_r"].abs()
        out["q_value_global"] = benjamini_hochberg(out["p_value"])
    return out.sort_values("abs_pearson_r", ascending=False) if not out.empty else out


def correlate_choice_features(choice: pd.DataFrame, label_sources: list[dict[str, Any]], min_n: int) -> pd.DataFrame:
    """Correlate user-level choice-shape features with external anchors."""
    rows: list[dict[str, Any]] = []
    choice = choice.copy()
    choice["user_id"] = choice["user_id"].astype(str)
    for scenario, scenario_choice in choice.groupby("scenario", sort=True):
        for source in label_sources:
            label_source = str(source["label_source"])
            if not scenario_label_compatibility(str(scenario), label_source):
                continue
            merged = scenario_choice.merge(source["frame"], on="user_id", how="inner")
            if merged.empty:
                continue
            for feature in CHOICE_FEATURES:
                if feature not in merged.columns:
                    continue
                for target in source["targets"]:
                    sub = merged[[feature, target]].dropna()
                    n = int(len(sub))
                    if n < min_n:
                        continue
                    pearson_r, p_value = safe_corr(sub[feature].to_numpy(float), sub[target].to_numpy(float))
                    rows.append(
                        {
                            "scenario": scenario,
                            "label_source": label_source,
                            "anchor_type": source["anchor_type"],
                            "evidence_strength": source["evidence_strength"],
                            "choice_use": merged["choice_use"].iloc[0] if "choice_use" in merged.columns else "",
                            "choice_feature": feature,
                            "target": target,
                            "n": n,
                            "pearson_r": pearson_r,
                            "spearman_rho": safe_spearman(sub[feature].to_numpy(float), sub[target].to_numpy(float)),
                            "p_value": p_value,
                        }
                    )
    out = pd.DataFrame(rows)
    if not out.empty:
        out["abs_pearson_r"] = out["pearson_r"].abs()
        out["q_value_global"] = benjamini_hochberg(out["p_value"])
    return out.sort_values("abs_pearson_r", ascending=False) if not out.empty else out


def coverage_table(profiles: pd.DataFrame, choice: pd.DataFrame, label_sources: list[dict[str, Any]]) -> pd.DataFrame:
    """Report merge coverage for each scenario and label source."""
    rows: list[dict[str, Any]] = []
    profile_sets = {s: set(g["user_id"].astype(str)) for s, g in profiles.groupby("scenario")}
    choice_sets = {s: set(g["user_id"].astype(str)) for s, g in choice.groupby("scenario")}
    for scenario in sorted(set(profile_sets) | set(choice_sets)):
        for source in label_sources:
            label_source = str(source["label_source"])
            if not scenario_label_compatibility(str(scenario), label_source):
                continue
            label_users = set(source["frame"]["user_id"].astype(str))
            rows.append(
                {
                    "scenario": scenario,
                    "label_source": label_source,
                    "anchor_type": source["anchor_type"],
                    "profile_users": len(profile_sets.get(scenario, set())),
                    "choice_users": len(choice_sets.get(scenario, set())),
                    "label_users": len(label_users),
                    "profile_label_overlap": len(profile_sets.get(scenario, set()).intersection(label_users)),
                    "choice_label_overlap": len(choice_sets.get(scenario, set()).intersection(label_users)),
                }
            )
    return pd.DataFrame(rows)


def summarize_by_component(profile_corr: pd.DataFrame) -> pd.DataFrame:
    """Summarize strongest profile external anchors by component and source."""
    if profile_corr.empty:
        return pd.DataFrame()
    return (
        profile_corr.groupby(["component", "label_source", "quality_scope"], as_index=False)
        .agg(
            rows=("target", "size"),
            median_abs_r=("abs_pearson_r", "median"),
            max_abs_r=("abs_pearson_r", "max"),
            n_q05=("q_value_global", lambda x: int((pd.Series(x) <= 0.05).sum())),
            median_n=("n", "median"),
        )
        .sort_values(["n_q05", "max_abs_r"], ascending=[False, False])
    )


def write_report(
    path: Path,
    coverage: pd.DataFrame,
    profile_corr: pd.DataFrame,
    choice_corr: pd.DataFrame,
    component_summary: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Write markdown report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    top_profile = profile_corr.head(40) if not profile_corr.empty else pd.DataFrame()
    top_profile_q = (
        profile_corr.loc[profile_corr["q_value_global"].le(0.05)].head(40) if not profile_corr.empty else pd.DataFrame()
    )
    construct_profile_q = (
        profile_corr.loc[profile_corr["q_value_global"].le(0.05) & profile_corr["component"].ne("residual_quality_score")]
        .head(40)
        if not profile_corr.empty
        else pd.DataFrame()
    )
    provisional_bridge = (
        profile_corr.loc[
            profile_corr["label_source"].str.startswith("bridge_")
            & profile_corr["component"].ne("residual_quality_score")
        ]
        .head(30)
        if not profile_corr.empty
        else pd.DataFrame()
    )
    top_choice = choice_corr.head(40) if not choice_corr.empty else pd.DataFrame()
    construct_choice = (
        choice_corr.loc[choice_corr["choice_feature"].ne("log_n_slices")]
        .head(30)
        if not choice_corr.empty
        else pd.DataFrame()
    )
    lines = [
        "# SUICA External Anchor Validation v1",
        "",
        "## Purpose",
        "",
        "This is an external validity audit for frozen SUICA profiles. Big5 and MBTI labels are anchors, not training targets and not definitions of the SUICA construct.",
        "",
        "## Evidence Strength",
        "",
        "- `pandora_big5`: continuous PANDORA Big5, same source as PANDORA SUICA scenarios.",
        "- `essays_big5_binary`: binary Essays Big5, external corpus but binary labels.",
        "- `bridge_strict_big5_mbti`: small matched Big5+MBTI bridge set; useful for direction, not broad estimation.",
        "- `bridge_supplementary_big5_mbti`: slightly larger robustness supplement.",
        "",
        "## Coverage",
        "",
        coverage.to_markdown(index=False) if not coverage.empty else "No label coverage.",
        "",
        "## Component Summary",
        "",
        component_summary.round(4).to_markdown(index=False) if not component_summary.empty else "No profile correlations.",
        "",
        "## Strongest Profile Anchors",
        "",
        top_profile[
            [
                "scenario",
                "label_source",
                "quality_scope",
                "factor",
                "component",
                "target",
                "n",
                "pearson_r",
                "spearman_rho",
                "q_value_global",
            ]
        ]
        .round(4)
        .to_markdown(index=False)
        if not top_profile.empty
        else "No profile correlations.",
        "",
        "## FDR-Surviving Profile Anchors",
        "",
        top_profile_q[
            [
                "scenario",
                "label_source",
                "quality_scope",
                "factor",
                "component",
                "target",
                "n",
                "pearson_r",
                "spearman_rho",
                "q_value_global",
            ]
        ]
        .round(4)
        .to_markdown(index=False)
        if not top_profile_q.empty
        else "No profile anchors survive global FDR q <= 0.05.",
        "",
        "## Construct-Relevant FDR Profile Anchors",
        "",
        "This table excludes `residual_quality_score`, which is a measurement-quality component rather than personality content.",
        "",
        construct_profile_q[
            [
                "scenario",
                "label_source",
                "quality_scope",
                "factor",
                "component",
                "target",
                "n",
                "pearson_r",
                "spearman_rho",
                "q_value_global",
            ]
        ]
        .round(4)
        .to_markdown(index=False)
        if not construct_profile_q.empty
        else "No construct-relevant profile anchors survive global FDR q <= 0.05.",
        "",
        "## Provisional Bridge Patterns",
        "",
        "These are the strongest Big5/MBTI matched-bridge associations after excluding residual quality. They are directional clues because bridge overlap is small and these rows do not necessarily survive global FDR.",
        "",
        provisional_bridge[
            [
                "scenario",
                "label_source",
                "quality_scope",
                "factor",
                "component",
                "target",
                "n",
                "pearson_r",
                "spearman_rho",
                "q_value_global",
            ]
        ]
        .round(4)
        .to_markdown(index=False)
        if not provisional_bridge.empty
        else "No bridge rows.",
        "",
        "## Strongest Choice Anchors",
        "",
        top_choice[
            [
                "scenario",
                "label_source",
                "choice_use",
                "choice_feature",
                "target",
                "n",
                "pearson_r",
                "spearman_rho",
                "q_value_global",
            ]
        ]
        .round(4)
        .to_markdown(index=False)
        if not top_choice.empty
        else "No choice correlations.",
        "",
        "## Construct-Relevant Choice Anchors",
        "",
        "This table excludes `log_n_slices`, which mainly reflects activity/coverage rather than choice content.",
        "",
        construct_choice[
            [
                "scenario",
                "label_source",
                "choice_use",
                "choice_feature",
                "target",
                "n",
                "pearson_r",
                "spearman_rho",
                "q_value_global",
            ]
        ]
        .round(4)
        .to_markdown(index=False)
        if not construct_choice.empty
        else "No construct-relevant choice correlations.",
        "",
        "## Interpretation Rules",
        "",
        "- Treat Big5/MBTI correlations as convergent/discriminant validity evidence only.",
        "- A strong SUICA factor with weak Big5/MBTI correlation may still be valid if it is stable and interpretable; it may measure a construct not covered by those low-dimensional scales.",
        "- A correlation found only in the bridge set is provisional because bridge overlap is small.",
        "- `residual_quality_score` correlations usually indicate measurement conditions, not personality content.",
        "- `log_n_slices` choice correlations usually indicate activity/coverage, not choice content.",
        "",
        "## Artifacts",
        "",
        f"- `{output_dir / 'label_coverage.csv'}`",
        f"- `{output_dir / 'profile_external_correlations.csv'}`",
        f"- `{output_dir / 'choice_external_correlations.csv'}`",
        f"- `{output_dir / 'component_external_summary.csv'}`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    profiles = pd.read_csv(args.profiles, dtype={"user_id": str})
    choice = pd.read_csv(args.choice_features, dtype={"user_id": str})
    label_sources = load_label_sources(args)
    coverage = coverage_table(profiles, choice, label_sources)
    profile_corr = correlate_profile_components(profiles, label_sources, args.min_n)
    choice_corr = correlate_choice_features(choice, label_sources, args.min_n)
    component_summary = summarize_by_component(profile_corr)
    coverage.to_csv(output_dir / "label_coverage.csv", index=False)
    profile_corr.to_csv(output_dir / "profile_external_correlations.csv", index=False)
    choice_corr.to_csv(output_dir / "choice_external_correlations.csv", index=False)
    component_summary.to_csv(output_dir / "component_external_summary.csv", index=False)
    run_config = {
        "profiles": args.profiles,
        "choice_features": args.choice_features,
        "min_n": args.min_n,
        "label_sources": [
            {"label_source": source["label_source"], "path": source["path"], "targets": source["targets"]}
            for source in label_sources
        ],
    }
    (output_dir / "run_config.json").write_text(json.dumps(run_config, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(Path(args.report_path), coverage, profile_corr, choice_corr, component_summary, output_dir)
    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "coverage_rows": int(len(coverage)),
                "profile_corr_rows": int(len(profile_corr)),
                "choice_corr_rows": int(len(choice_corr)),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
