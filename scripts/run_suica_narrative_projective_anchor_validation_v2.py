#!/usr/bin/env python
"""Validate SUICA profiles against narrative/projective text anchors.

This audit treats Big5/MBTI as external anchors, not as the target construct.
It tests whether frozen SUICA author profiles align with interpretable
narrative/projective dimensions such as agency, communion, mentalization,
temporal integration, directive stance, and conflict/redemption language.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Iterable
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
SLICE_SCORES = ROOT / "results" / "suica_item_bank_v1" / "slice_scores_with_text.csv"
PROFILE_SCORES = ROOT / "results" / "suica_policy_profile_scorer_v1" / "user_factor_profiles.csv"
FACTOR_STATUS = ROOT / "results" / "suica_measurement_framework_v1" / "factor_status_table.csv"
OUT_DIR = ROOT / "results" / "suica_narrative_projective_anchor_validation_v2"
REPORT_PATH = ROOT / "reports" / "suica_narrative_projective_anchor_validation_v2.md"


TOKEN_RE = re.compile(r"[a-zA-Z']+|\?")

ANCHOR_LEXICONS: dict[str, set[str]] = {
    "self_focus": {"i", "me", "my", "mine", "myself", "i'm", "im", "i've", "ive", "i'll"},
    "second_person": {"you", "your", "yours", "yourself", "you're", "youre", "you'll", "u"},
    "third_person": {"he", "him", "his", "she", "her", "hers", "they", "them", "their", "theirs"},
    "general_people": {"people", "person", "someone", "everyone", "anyone", "others", "men", "women", "guy", "girl"},
    "agency": {
        "can",
        "could",
        "able",
        "make",
        "made",
        "do",
        "did",
        "try",
        "tried",
        "choose",
        "chose",
        "control",
        "decide",
        "decided",
        "act",
        "build",
        "start",
        "change",
    },
    "communion": {
        "friend",
        "friends",
        "family",
        "relationship",
        "together",
        "help",
        "support",
        "care",
        "love",
        "kind",
        "thanks",
        "thank",
        "share",
        "community",
    },
    "mentalization": {
        "think",
        "thought",
        "feel",
        "felt",
        "believe",
        "know",
        "understand",
        "realize",
        "realized",
        "want",
        "need",
        "hope",
        "worry",
        "remember",
        "imagine",
    },
    "past_temporal": {"was", "were", "had", "been", "ago", "before", "then", "when", "years", "used", "remember"},
    "future_temporal": {"will", "future", "soon", "later", "plan", "plans", "planning", "going", "gonna", "next"},
    "temporal_sequence": {"before", "after", "then", "when", "while", "during", "until", "again", "eventually"},
    "directive": {"should", "must", "need", "have", "try", "recommend", "advice", "advise", "please", "let", "don't"},
    "causal_meaning": {"because", "why", "therefore", "since", "reason", "means", "meaning", "cause", "caused", "explain"},
    "positive_affect": {"happy", "good", "great", "love", "like", "hope", "better", "nice", "fun", "enjoy", "glad"},
    "negative_affect": {
        "bad",
        "sad",
        "angry",
        "hate",
        "fear",
        "worried",
        "worry",
        "worse",
        "hurt",
        "annoyed",
        "depressed",
        "stress",
    },
    "uncertainty": {"maybe", "perhaps", "probably", "guess", "seems", "seem", "might", "could", "unsure", "possibly"},
    "certainty": {"know", "sure", "definitely", "always", "never", "clearly", "obvious", "must", "certainly"},
    "conflict_threat": {
        "problem",
        "difficult",
        "hard",
        "conflict",
        "fight",
        "argue",
        "risk",
        "fail",
        "failed",
        "loss",
        "lost",
        "danger",
    },
    "redemption_growth": {"improve", "overcome", "recover", "better", "learn", "grow", "growth", "heal", "progress", "success"},
    "contamination_loss": {"worse", "ruined", "failed", "lost", "betrayed", "disaster", "broken", "hurt", "damage", "regret"},
    "social_evaluation": {"judge", "judged", "criticize", "compare", "better", "worse", "best", "worst", "status", "normal"},
    "achievement_order": {"work", "job", "school", "study", "finish", "schedule", "plan", "order", "goal", "task"},
    "novelty_play": {"new", "novel", "creative", "game", "play", "fun", "idea", "interesting", "explore", "different"},
    "moral_norm": {"right", "wrong", "fair", "unfair", "should", "must", "deserve", "moral", "ethics", "rule"},
}


PROFILE_COMPONENTS = [
    "base_score",
    "react_amplitude",
    "residual_quality_score",
    "choice_entropy_norm",
    "top_condition_share",
    "choice_influence_delta",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SUICA narrative/projective anchor validation v2.")
    parser.add_argument("--slice-scores", default=str(SLICE_SCORES))
    parser.add_argument("--profile-scores", default=str(PROFILE_SCORES))
    parser.add_argument("--factor-status", default=str(FACTOR_STATUS))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--include-x", action="store_true", help="Include X market scenarios in the primary audit.")
    parser.add_argument("--min-n", type=int, default=80)
    return parser.parse_args()


def tokenize(text: str) -> list[str]:
    return [tok.lower() for tok in TOKEN_RE.findall(str(text or ""))]


def _rate(tokens: list[str], lexicon: set[str], denom: int) -> float:
    return 100.0 * sum(tok in lexicon for tok in tokens) / max(1, denom)


def score_text_anchors(text: str) -> dict[str, float]:
    """Return lightweight narrative/projective anchor rates for one text slice."""
    toks = tokenize(text)
    word_count = max(1, sum(tok != "?" for tok in toks))
    out = {f"{name}_rate": _rate(toks, words, word_count) for name, words in ANCHOR_LEXICONS.items()}
    out["question_mark_rate"] = 100.0 * toks.count("?") / word_count
    out["token_count_anchor"] = float(word_count)

    other_rate = out["second_person_rate"] + out["third_person_rate"] + out["general_people_rate"]
    out["self_other_balance"] = out["self_focus_rate"] - other_rate
    out["agency_communion_balance"] = out["agency_rate"] - out["communion_rate"]
    out["affect_balance"] = out["positive_affect_rate"] - out["negative_affect_rate"]
    out["temporal_balance"] = out["past_temporal_rate"] - out["future_temporal_rate"]
    out["certainty_balance"] = out["certainty_rate"] - out["uncertainty_rate"]
    out["narrative_integration_rate"] = (
        out["mentalization_rate"] + out["temporal_sequence_rate"] + out["causal_meaning_rate"]
    )
    out["projective_tension_rate"] = (
        out["negative_affect_rate"] + out["conflict_threat_rate"] + out["uncertainty_rate"]
    )
    out["directive_interpersonal_blend"] = np.sqrt(max(0.0, out["directive_rate"]) * max(0.0, out["second_person_rate"]))
    out["growth_after_tension_blend"] = np.sqrt(
        max(0.0, out["redemption_growth_rate"]) * max(0.0, out["conflict_threat_rate"] + out["negative_affect_rate"])
    )
    return out


def anchor_columns(frame: pd.DataFrame) -> list[str]:
    return [
        col
        for col in frame.columns
        if col.endswith("_rate") or col.endswith("_balance") or col.endswith("_blend") or col == "token_count_anchor"
    ]


def safe_corr(x: Iterable[float], y: Iterable[float]) -> tuple[float, float, int]:
    xv = pd.to_numeric(pd.Series(x), errors="coerce")
    yv = pd.to_numeric(pd.Series(y), errors="coerce")
    mask = xv.notna() & yv.notna()
    n = int(mask.sum())
    if n < 4:
        return float("nan"), float("nan"), n
    xa = xv.loc[mask].to_numpy(float)
    ya = yv.loc[mask].to_numpy(float)
    if np.std(xa) < 1e-12 or np.std(ya) < 1e-12:
        return float("nan"), float("nan"), n
    result = stats.pearsonr(xa, ya)
    return float(result.statistic), float(result.pvalue), n


def benjamini_hochberg(p_values: pd.Series) -> pd.Series:
    p = pd.to_numeric(p_values, errors="coerce")
    q = pd.Series(np.nan, index=p.index, dtype=float)
    valid = p.dropna().sort_values()
    m = len(valid)
    if m == 0:
        return q
    ranks = np.arange(1, m + 1, dtype=float)
    adjusted = valid.to_numpy(float) * m / ranks
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    q.loc[valid.index] = np.clip(adjusted, 0.0, 1.0)
    return q


def build_slice_anchor_frame(slice_scores: pd.DataFrame) -> pd.DataFrame:
    anchor_frame = pd.DataFrame([score_text_anchors(text) for text in slice_scores["slice_text"].fillna("")])
    keep = ["scenario", "user_id", "condition", "slice_obs_id", "slice_index", "token_count", "slice_text"]
    keep = [col for col in keep if col in slice_scores.columns]
    return pd.concat([slice_scores[keep].reset_index(drop=True), anchor_frame], axis=1)


def aggregate_user_anchor_profiles(slice_anchors: pd.DataFrame) -> pd.DataFrame:
    anchors = anchor_columns(slice_anchors)
    mean_part = (
        slice_anchors.groupby(["scenario", "user_id"], as_index=False)[anchors]
        .mean(numeric_only=True)
        .rename(columns={col: f"{col}_mean" for col in anchors})
    )
    std_part = (
        slice_anchors.groupby(["scenario", "user_id"], as_index=False)[anchors]
        .std(numeric_only=True)
        .fillna(0.0)
        .rename(columns={col: f"{col}_sd" for col in anchors})
    )
    cond_means = slice_anchors.groupby(["scenario", "user_id", "condition"], as_index=False)[anchors].mean(numeric_only=True)
    amp_part = (
        cond_means.groupby(["scenario", "user_id"], as_index=False)[anchors]
        .std(numeric_only=True)
        .fillna(0.0)
        .rename(columns={col: f"{col}_condition_amp" for col in anchors})
    )
    count_part = (
        slice_anchors.groupby(["scenario", "user_id"], as_index=False)
        .agg(n_slices=("slice_obs_id", "count"), n_conditions=("condition", "nunique"))
    )
    return mean_part.merge(std_part, on=["scenario", "user_id"], how="outer").merge(
        amp_part, on=["scenario", "user_id"], how="outer"
    ).merge(count_part, on=["scenario", "user_id"], how="left")


def correlate_profiles(profile_scores: pd.DataFrame, anchor_profiles: pd.DataFrame, min_n: int) -> pd.DataFrame:
    merged = profile_scores.merge(anchor_profiles, on=["scenario", "user_id"], how="inner")
    anchor_cols = [
        col
        for col in anchor_profiles.columns
        if col not in {"scenario", "user_id", "n_slices", "n_conditions"}
    ]
    profile_cols = [col for col in PROFILE_COMPONENTS if col in merged.columns]
    rows: list[dict] = []
    for scenario, group in merged.groupby("scenario", sort=True):
        for factor, factor_group in group.groupby("factor", sort=True):
            for component in profile_cols:
                if component not in factor_group.columns:
                    continue
                for anchor in anchor_cols:
                    r, p, n = safe_corr(factor_group[component], factor_group[anchor])
                    if n < min_n or not np.isfinite(r):
                        continue
                    rows.append(
                        {
                            "scenario": scenario,
                            "factor": factor,
                            "profile_component": component,
                            "anchor": anchor,
                            "pearson_r": r,
                            "pearson_p": p,
                            "n": n,
                            "abs_r": abs(r),
                        }
                    )
    corr = pd.DataFrame(rows)
    if corr.empty:
        return corr
    corr["q_all"] = benjamini_hochberg(corr["pearson_p"])
    return corr.sort_values(["abs_r", "n"], ascending=[False, False])


def summarize_factor_anchors(corr: pd.DataFrame, factor_status: pd.DataFrame) -> pd.DataFrame:
    if corr.empty:
        return corr
    rows: list[dict] = []
    for (factor, component, anchor), group in corr.groupby(["factor", "profile_component", "anchor"], sort=True):
        signs = np.sign(group["pearson_r"].to_numpy(float))
        nonzero_signs = signs[signs != 0]
        dominant_sign = float(np.sign(group["pearson_r"].median()))
        direction_agreement = float((nonzero_signs == dominant_sign).mean()) if len(nonzero_signs) else np.nan
        best = group.sort_values("abs_r", ascending=False).iloc[0]
        rows.append(
            {
                "factor": factor,
                "profile_component": component,
                "anchor": anchor,
                "scenario_count": int(group["scenario"].nunique()),
                "mean_r": float(group["pearson_r"].mean()),
                "median_r": float(group["pearson_r"].median()),
                "median_abs_r": float(group["abs_r"].median()),
                "max_abs_r": float(group["abs_r"].max()),
                "direction_agreement": direction_agreement,
                "min_q_all": float(group["q_all"].min()),
                "best_scenario": best["scenario"],
                "best_r": float(best["pearson_r"]),
                "best_n": int(best["n"]),
                "support_score": float(group["abs_r"].median() * (direction_agreement if np.isfinite(direction_agreement) else 0.0)),
            }
        )
    summary = pd.DataFrame(rows).sort_values(["support_score", "max_abs_r"], ascending=False)
    meta_cols = ["factor", "provisional_name", "measurement_role", "class", "top_node_terms"]
    meta_cols = [col for col in meta_cols if col in factor_status.columns]
    return summary.merge(factor_status[meta_cols], on="factor", how="left")


def top_factor_summary(stable: pd.DataFrame, top_k: int = 6) -> pd.DataFrame:
    if stable.empty:
        return stable
    filtered = stable.loc[stable["profile_component"].isin(["base_score", "react_amplitude"])].copy()
    if filtered.empty:
        filtered = stable.copy()
    return filtered.sort_values(["factor", "support_score"], ascending=[True, False]).groupby("factor").head(top_k)


def display_path(path: Path) -> str:
    resolved = path if path.is_absolute() else ROOT / path
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def write_report(
    path: Path,
    out_dir: Path,
    slice_anchors: pd.DataFrame,
    user_anchors: pd.DataFrame,
    corr: pd.DataFrame,
    stable: pd.DataFrame,
    factor_top: pd.DataFrame,
    include_x: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    top = corr.head(25) if not corr.empty else pd.DataFrame()
    stable_top = stable.head(25) if not stable.empty else pd.DataFrame()
    lines = [
        "# SUICA Narrative/Projective Anchor Validation v2",
        "",
        "## Purpose",
        "",
        "This audit adds a non-Big5/MBTI validity layer for SUICA. It asks whether frozen author-level SUICA profiles align with narrative and projective-method anchors such as agency, communion, mentalization, temporal integration, directive stance, conflict, and redemption language.",
        "",
        "This is not a training step and not a personality-label benchmark. It is construct interpretation for a text-behavior scale candidate.",
        "",
        "## Data",
        "",
        f"- slice rows scored: `{len(slice_anchors)}`",
        f"- user-scenario anchor profiles: `{len(user_anchors)}`",
        f"- X market scenarios included: `{include_x}`",
        "",
        "## Strongest Profile-Anchor Correlations",
        "",
    ]
    if top.empty:
        lines.append("No correlations met the minimum sample-size gate.")
    else:
        lines.append(top[["scenario", "factor", "profile_component", "anchor", "pearson_r", "q_all", "n"]].round(4).to_markdown(index=False))
    lines.extend(["", "## Stable Anchor Summary", ""])
    if stable_top.empty:
        lines.append("No stable factor-anchor summary rows were produced.")
    else:
        lines.append(
            stable_top[
                [
                    "factor",
                    "profile_component",
                    "anchor",
                    "scenario_count",
                    "median_r",
                    "median_abs_r",
                    "direction_agreement",
                    "support_score",
                    "best_scenario",
                    "best_r",
                ]
            ]
            .round(4)
            .to_markdown(index=False)
        )
    lines.extend(["", "## Factor-Level Reading", ""])
    if factor_top.empty:
        lines.append("No factor-level anchor profile is available.")
    else:
        for factor, group in factor_top.groupby("factor", sort=True):
            meta = group.iloc[0]
            lines.extend(
                [
                    f"### {factor}: {meta.get('provisional_name', '')}",
                    "",
                    f"- measurement role: `{meta.get('measurement_role', '')}`",
                    f"- top node terms: `{meta.get('top_node_terms', '')}`",
                    "",
                    group[
                        [
                            "profile_component",
                            "anchor",
                            "scenario_count",
                            "median_r",
                            "direction_agreement",
                            "support_score",
                            "best_scenario",
                            "best_r",
                        ]
                    ]
                    .round(4)
                    .to_markdown(index=False),
                    "",
                ]
            )
    lines.extend(
        [
            "## Interpretation",
            "",
            "- `base_score` anchor mappings are scale-like construct clues.",
            "- `react_amplitude` anchor mappings are projective/CAPS-like response-signature clues.",
            "- `residual_quality_score`, `choice_entropy_norm`, and `top_condition_share` mappings are treated as measurement-condition or exposure signals unless replicated by content components.",
            "- A strong lexical anchor is not a final construct name. It is a coding hypothesis that should be checked with high/low text examples and, later, human or LLM-assisted blind coding.",
            "",
            "## Artifacts",
            "",
            f"- `{display_path(out_dir / 'slice_narrative_projective_anchors.csv')}`",
            f"- `{display_path(out_dir / 'user_narrative_projective_anchor_profiles.csv')}`",
            f"- `{display_path(out_dir / 'suica_profile_anchor_correlations.csv')}`",
            f"- `{display_path(out_dir / 'factor_anchor_summary.csv')}`",
            f"- `{display_path(out_dir / 'factor_top_anchor_reading.csv')}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    slice_scores = pd.read_csv(args.slice_scores, dtype={"user_id": str})
    if not args.include_x:
        slice_scores = slice_scores.loc[~slice_scores["scenario"].astype(str).str.startswith("x_")].copy()
    profile_scores = pd.read_csv(args.profile_scores, dtype={"user_id": str})
    if not args.include_x:
        profile_scores = profile_scores.loc[~profile_scores["scenario"].astype(str).str.startswith("x_")].copy()
    factor_status = pd.read_csv(args.factor_status)

    slice_anchors = build_slice_anchor_frame(slice_scores)
    user_anchors = aggregate_user_anchor_profiles(slice_anchors)
    corr = correlate_profiles(profile_scores, user_anchors, min_n=args.min_n)
    stable = summarize_factor_anchors(corr, factor_status)
    factor_top = top_factor_summary(stable)

    slice_anchors.to_csv(out_dir / "slice_narrative_projective_anchors.csv", index=False)
    user_anchors.to_csv(out_dir / "user_narrative_projective_anchor_profiles.csv", index=False)
    corr.to_csv(out_dir / "suica_profile_anchor_correlations.csv", index=False)
    stable.to_csv(out_dir / "factor_anchor_summary.csv", index=False)
    factor_top.to_csv(out_dir / "factor_top_anchor_reading.csv", index=False)
    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "slice_scores": str(Path(args.slice_scores)),
                "profile_scores": str(Path(args.profile_scores)),
                "factor_status": str(Path(args.factor_status)),
                "include_x": bool(args.include_x),
                "min_n": int(args.min_n),
                "anchor_count": len(anchor_columns(slice_anchors)),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(Path(args.report_path), out_dir, slice_anchors, user_anchors, corr, stable, factor_top, args.include_x)

    print("Top stable narrative/projective anchors:")
    if stable.empty:
        print("No rows passed gates.")
    else:
        print(
            stable[
                [
                    "factor",
                    "profile_component",
                    "anchor",
                    "scenario_count",
                    "median_r",
                    "direction_agreement",
                    "support_score",
                    "best_scenario",
                    "best_r",
                ]
            ]
            .head(20)
            .round(4)
            .to_string(index=False)
        )
    print(f"\nReport: {display_path(Path(args.report_path))}")


if __name__ == "__main__":
    main()
