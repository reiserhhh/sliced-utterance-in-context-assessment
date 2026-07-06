#!/usr/bin/env python
"""Evaluate blind construct-coding results for SUICA.

The evaluator merges coder-facing ratings with the hidden answer key, estimates
high-vs-low pole separation for each factor and construct dimension, and reports
coder agreement when two or more independent coding files are provided.

When no coder file is supplied, the script can run an automatic lexical precode
control. That control validates the evaluation pipeline and expected directions,
but it is not independent human/LLM evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "results" / "suica_blind_construct_coding_package_v1"
KEY_PATH = PACKAGE_DIR / "blind_coding_key.csv"
AUTO_PRECODE_PATH = PACKAGE_DIR / "auto_anchor_scores_by_item.csv"
ALIGNMENT_PATH = PACKAGE_DIR / "factor_construct_alignment_summary.csv"
OUT_DIR = ROOT / "results" / "suica_blind_construct_coding_evaluation_v1"
REPORT_PATH = ROOT / "reports" / "suica_blind_construct_coding_evaluation_v1.md"


DIMENSIONS = [
    "agency",
    "communion",
    "mentalization",
    "temporal_integration",
    "directive_interpersonal",
    "self_focus",
    "other_focus",
    "affect_tension",
    "redemption_growth",
    "social_evaluation",
    "novelty_play",
]


AUTO_DIMENSION_FORMULAS = {
    "agency": ["agency_rate"],
    "communion": ["communion_rate"],
    "mentalization": ["mentalization_rate"],
    "temporal_integration": ["past_temporal_rate", "future_temporal_rate", "temporal_sequence_rate"],
    "directive_interpersonal": ["directive_rate", "second_person_rate", "directive_interpersonal_blend"],
    "self_focus": ["self_focus_rate"],
    "other_focus": ["second_person_rate", "third_person_rate", "general_people_rate"],
    "affect_tension": ["negative_affect_rate", "uncertainty_rate", "conflict_threat_rate", "projective_tension_rate"],
    "redemption_growth": ["redemption_growth_rate", "growth_after_tension_blend"],
    "social_evaluation": ["social_evaluation_rate"],
    "novelty_play": ["novelty_play_rate"],
}


FACTOR_EXPECTED_DIMENSIONS = {
    "suica_factor_01": ["social_evaluation", "temporal_integration"],
    "suica_factor_02": ["mentalization", "self_focus", "directive_interpersonal"],
    "suica_factor_03": ["self_focus", "other_focus", "temporal_integration"],
    "suica_factor_04": ["other_focus", "temporal_integration"],
    "suica_factor_05": ["novelty_play", "agency"],
    "suica_factor_06": ["directive_interpersonal", "other_focus", "self_focus"],
    "suica_factor_07": ["other_focus", "social_evaluation"],
    "suica_factor_08": ["directive_interpersonal", "other_focus"],
    "suica_factor_09": ["self_focus", "mentalization", "affect_tension"],
    "suica_factor_10": ["mentalization", "directive_interpersonal", "agency"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate SUICA blind construct coding.")
    parser.add_argument("--key", default=str(KEY_PATH))
    parser.add_argument("--alignment-summary", default=str(ALIGNMENT_PATH))
    parser.add_argument("--auto-precode", default=str(AUTO_PRECODE_PATH))
    parser.add_argument("--coder-file", action="append", default=[], help="Coder CSV. Can be passed multiple times.")
    parser.add_argument("--coder-id", action="append", default=[], help="Optional coder id matching --coder-file order.")
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument(
        "--no-auto-control",
        action="store_true",
        help="Do not run lexical auto-precode control when no coder files are supplied.",
    )
    return parser.parse_args()


def rating_columns(frame: pd.DataFrame) -> list[str]:
    return [col for col in frame.columns if col.endswith("_0_to_3")]


def cohen_d(high: pd.Series, low: pd.Series) -> float:
    high_v = pd.to_numeric(high, errors="coerce").dropna().to_numpy(float)
    low_v = pd.to_numeric(low, errors="coerce").dropna().to_numpy(float)
    if len(high_v) < 2 or len(low_v) < 2:
        return float("nan")
    pooled = np.sqrt((np.var(high_v, ddof=1) + np.var(low_v, ddof=1)) / 2.0)
    if pooled < 1e-12:
        return float("nan")
    return float((np.mean(high_v) - np.mean(low_v)) / pooled)


def safe_ttest(high: pd.Series, low: pd.Series) -> float:
    high_v = pd.to_numeric(high, errors="coerce").dropna().to_numpy(float)
    low_v = pd.to_numeric(low, errors="coerce").dropna().to_numpy(float)
    if len(high_v) < 2 or len(low_v) < 2:
        return float("nan")
    if np.std(high_v) < 1e-12 and np.std(low_v) < 1e-12:
        return float("nan")
    return float(stats.ttest_ind(high_v, low_v, equal_var=False).pvalue)


def source_adjusted_pole_effects(coded: pd.DataFrame) -> pd.DataFrame:
    """Estimate rating ~ high_pole + source_family fixed effects by OLS."""
    rows: list[dict] = []
    for (coder_id, factor), group in coded.groupby(["coder_id", "factor"], sort=True):
        for dimension in DIMENSIONS:
            col = f"{dimension}_0_to_3"
            if col not in group.columns:
                continue
            work = group[["pole", "source_family", col]].copy()
            work[col] = pd.to_numeric(work[col], errors="coerce")
            work = work.dropna(subset=[col, "pole", "source_family"])
            if work["pole"].nunique() < 2 or len(work) < 6:
                continue
            y = work[col].to_numpy(float)
            high = work["pole"].eq("high").astype(float).to_numpy()
            families = sorted(work["source_family"].astype(str).unique())
            family_cols = []
            for family in families[1:]:
                family_cols.append(work["source_family"].astype(str).eq(family).astype(float).to_numpy())
            x = np.column_stack([np.ones(len(work)), high, *family_cols])
            rank = np.linalg.matrix_rank(x)
            if rank < x.shape[1] or len(work) <= x.shape[1] + 1:
                continue
            coef, *_ = np.linalg.lstsq(x, y, rcond=None)
            residual = y - x @ coef
            df = len(y) - x.shape[1]
            sigma2 = float(np.sum(residual**2) / df)
            xtx_inv = np.linalg.inv(x.T @ x)
            se = float(np.sqrt(max(0.0, sigma2 * xtx_inv[1, 1])))
            beta = float(coef[1])
            if se < 1e-12:
                t_value = np.nan
                p_value = np.nan
            else:
                t_value = beta / se
                p_value = float(2.0 * stats.t.sf(abs(t_value), df=df))
            rows.append(
                {
                    "coder_id": coder_id,
                    "factor": factor,
                    "dimension": dimension,
                    "n": int(len(work)),
                    "source_family_count": int(work["source_family"].nunique()),
                    "high_minus_low_source_adjusted": beta,
                    "standard_error": se,
                    "t_value": float(t_value) if np.isfinite(t_value) else np.nan,
                    "p_value": p_value,
                }
            )
    columns = [
        "coder_id",
        "factor",
        "dimension",
        "n",
        "source_family_count",
        "high_minus_low_source_adjusted",
        "standard_error",
        "t_value",
        "p_value",
    ]
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(rows, columns=columns).sort_values(
        ["coder_id", "factor", "high_minus_low_source_adjusted"], ascending=[True, True, False]
    )


def scale_rank_to_0_3(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.notna().sum() == 0:
        return numeric
    return numeric.rank(method="average", pct=True) * 3.0


def build_auto_control(auto_precode: pd.DataFrame) -> pd.DataFrame:
    coder = pd.DataFrame({"blind_item_id": auto_precode["blind_item_id"]})
    for dimension, source_cols in AUTO_DIMENSION_FORMULAS.items():
        available = [col for col in source_cols if col in auto_precode.columns]
        if not available:
            coder[f"{dimension}_0_to_3"] = np.nan
            continue
        raw = auto_precode[available].apply(pd.to_numeric, errors="coerce").mean(axis=1)
        coder[f"{dimension}_0_to_3"] = scale_rank_to_0_3(raw)
    coder["coder_notes"] = "auto lexical precode control; not independent evidence"
    return coder


def load_coder_frames(args: argparse.Namespace) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    coder_files = list(args.coder_file)
    coder_ids = list(args.coder_id)
    if coder_files:
        for idx, path in enumerate(coder_files):
            coder_id = coder_ids[idx] if idx < len(coder_ids) else Path(path).stem
            frame = pd.read_csv(path)
            if "blind_item_id" not in frame.columns:
                raise ValueError(f"missing blind_item_id in coder file: {path}")
            cols = ["blind_item_id", *rating_columns(frame)]
            if len(cols) == 1:
                raise ValueError(f"no *_0_to_3 rating columns in coder file: {path}")
            out = frame[cols].copy()
            out.insert(0, "coder_id", coder_id)
            frames.append(out)
    elif not args.no_auto_control:
        auto = pd.read_csv(args.auto_precode)
        out = build_auto_control(auto)
        out.insert(0, "coder_id", "auto_lexical_control")
        frames.append(out)
    if not frames:
        return pd.DataFrame(columns=["coder_id", "blind_item_id"])
    return pd.concat(frames, ignore_index=True)


def evaluate_pole_separation(coded: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for (coder_id, factor), group in coded.groupby(["coder_id", "factor"], sort=True):
        for dimension in DIMENSIONS:
            col = f"{dimension}_0_to_3"
            if col not in group.columns:
                continue
            high = group.loc[group["pole"].eq("high"), col]
            low = group.loc[group["pole"].eq("low"), col]
            rows.append(
                {
                    "coder_id": coder_id,
                    "factor": factor,
                    "dimension": dimension,
                    "high_n": int(pd.to_numeric(high, errors="coerce").notna().sum()),
                    "low_n": int(pd.to_numeric(low, errors="coerce").notna().sum()),
                    "high_mean": float(pd.to_numeric(high, errors="coerce").mean()),
                    "low_mean": float(pd.to_numeric(low, errors="coerce").mean()),
                    "high_minus_low": float(pd.to_numeric(high, errors="coerce").mean() - pd.to_numeric(low, errors="coerce").mean()),
                    "cohen_d": cohen_d(high, low),
                    "p_value": safe_ttest(high, low),
                }
            )
    return pd.DataFrame(rows).sort_values(["coder_id", "factor", "cohen_d"], ascending=[True, True, False])


def expected_dimension_summary(pole_results: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for (coder_id, factor), group in pole_results.groupby(["coder_id", "factor"], sort=True):
        expected = FACTOR_EXPECTED_DIMENSIONS.get(factor, [])
        if not expected:
            continue
        expected_rows = group.loc[group["dimension"].isin(expected)].copy()
        if expected_rows.empty:
            continue
        strongest = expected_rows.reindex(expected_rows["cohen_d"].abs().sort_values(ascending=False).index).iloc[0]
        direction_hits = int((expected_rows["cohen_d"].abs() >= 0.5).sum())
        rows.append(
            {
                "coder_id": coder_id,
                "factor": factor,
                "expected_dimensions": "; ".join(expected),
                "expected_dimensions_checked": int(len(expected_rows)),
                "expected_large_effect_count_abs_d_ge_0p5": direction_hits,
                "median_expected_abs_d": float(expected_rows["cohen_d"].abs().median()),
                "max_expected_abs_d": float(expected_rows["cohen_d"].abs().max()),
                "strongest_expected_dimension": strongest["dimension"],
                "strongest_expected_d": float(strongest["cohen_d"]),
                "construct_gate": "support" if direction_hits >= 1 and float(expected_rows["cohen_d"].abs().median()) >= 0.5 else "weak_or_needs_review",
            }
        )
    return pd.DataFrame(rows).sort_values(["coder_id", "construct_gate", "median_expected_abs_d"], ascending=[True, True, False])


def expected_source_adjusted_summary(source_adjusted: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    if source_adjusted.empty:
        return pd.DataFrame(
            columns=[
                "coder_id",
                "factor",
                "expected_dimensions",
                "expected_source_adjusted_checked",
                "median_expected_abs_adjusted_beta",
                "max_expected_abs_adjusted_beta",
                "source_adjusted_gate",
            ]
        )
    for (coder_id, factor), group in source_adjusted.groupby(["coder_id", "factor"], sort=True):
        expected = FACTOR_EXPECTED_DIMENSIONS.get(factor, [])
        if not expected:
            continue
        expected_rows = group.loc[group["dimension"].isin(expected)].copy()
        if expected_rows.empty:
            continue
        abs_beta = expected_rows["high_minus_low_source_adjusted"].abs()
        rows.append(
            {
                "coder_id": coder_id,
                "factor": factor,
                "expected_dimensions": "; ".join(expected),
                "expected_source_adjusted_checked": int(len(expected_rows)),
                "median_expected_abs_adjusted_beta": float(abs_beta.median()),
                "max_expected_abs_adjusted_beta": float(abs_beta.max()),
                "source_adjusted_large_effect_count_abs_beta_ge_0p3": int((abs_beta >= 0.3).sum()),
                "source_adjusted_gate": "support"
                if int((abs_beta >= 0.3).sum()) >= 1 and float(abs_beta.median()) >= 0.3
                else "weak_or_source_sensitive",
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["coder_id", "source_adjusted_gate", "median_expected_abs_adjusted_beta"], ascending=[True, True, False]
    )


def inter_coder_agreement(coded: pd.DataFrame) -> pd.DataFrame:
    coder_ids = sorted(coded["coder_id"].dropna().unique())
    if len(coder_ids) < 2:
        return pd.DataFrame(
            columns=[
                "dimension",
                "coder_a",
                "coder_b",
                "n",
                "pearson_r",
                "mean_abs_diff",
            ]
        )
    rows: list[dict] = []
    for i, coder_a in enumerate(coder_ids):
        a = coded.loc[coded["coder_id"].eq(coder_a)].copy()
        for coder_b in coder_ids[i + 1 :]:
            b = coded.loc[coded["coder_id"].eq(coder_b)].copy()
            merged = a.merge(b, on="blind_item_id", suffixes=("_a", "_b"))
            for dimension in DIMENSIONS:
                col_a = f"{dimension}_0_to_3_a"
                col_b = f"{dimension}_0_to_3_b"
                if col_a not in merged.columns or col_b not in merged.columns:
                    continue
                x = pd.to_numeric(merged[col_a], errors="coerce")
                y = pd.to_numeric(merged[col_b], errors="coerce")
                mask = x.notna() & y.notna()
                n = int(mask.sum())
                if n < 4 or x.loc[mask].std() < 1e-12 or y.loc[mask].std() < 1e-12:
                    r = float("nan")
                else:
                    r = float(stats.pearsonr(x.loc[mask], y.loc[mask]).statistic)
                rows.append(
                    {
                        "dimension": dimension,
                        "coder_a": coder_a,
                        "coder_b": coder_b,
                        "n": n,
                        "pearson_r": r,
                        "mean_abs_diff": float((x.loc[mask] - y.loc[mask]).abs().mean()) if n else np.nan,
                    }
                )
    return pd.DataFrame(rows)


def display_path(path: Path) -> str:
    resolved = path if path.is_absolute() else ROOT / path
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def write_report(
    path: Path,
    coded: pd.DataFrame,
    pole_results: pd.DataFrame,
    expected_summary: pd.DataFrame,
    source_adjusted: pd.DataFrame,
    source_adjusted_summary: pd.DataFrame,
    agreement: pd.DataFrame,
    alignment: pd.DataFrame,
    auto_control: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    coverage = (
        coded.groupby("coder_id", as_index=False)
        .agg(items=("blind_item_id", "nunique"), factors=("factor", "nunique"))
        .sort_values("coder_id")
    )
    top_effects = pole_results.reindex(pole_results["cohen_d"].abs().sort_values(ascending=False).index).head(25)
    top_adjusted = (
        source_adjusted.reindex(source_adjusted["high_minus_low_source_adjusted"].abs().sort_values(ascending=False).index).head(25)
        if not source_adjusted.empty
        else pd.DataFrame()
    )
    alignment_cols = [
        "factor",
        "checked_anchors",
        "direction_match_rate",
        "median_abs_cohen_d",
        "mean_abs_cohen_d",
        "top_expected_anchors",
        "top_observed_directions",
    ]
    compatible_alignment = (
        alignment[alignment_cols].copy()
        if not alignment.empty and set(alignment_cols).issubset(alignment.columns)
        else pd.DataFrame()
    )
    lines = [
        "# SUICA Blind Construct Coding Evaluation v1",
        "",
        "## Purpose",
        "",
        "This evaluator tests whether blind construct ratings separate SUICA high/low factor poles. It is designed for human or LLM coder files. If only the automatic lexical precode is used, results are a pipeline smoke/control and not independent validity evidence.",
        "",
        "## Mode",
        "",
        f"- auto lexical control only: `{auto_control}`",
        "",
        "## Coverage",
        "",
        coverage.to_markdown(index=False),
        "",
        "## Expected-Dimension Gate",
        "",
        expected_summary.round(3).to_markdown(index=False) if not expected_summary.empty else "No expected-dimension summary available.",
        "",
        "## Source-Adjusted Expected-Dimension Gate",
        "",
        source_adjusted_summary.round(3).to_markdown(index=False)
        if not source_adjusted_summary.empty
        else "No source-adjusted expected-dimension summary available.",
        "",
        "## Largest High-vs-Low Rating Contrasts",
        "",
        top_effects[["coder_id", "factor", "dimension", "high_mean", "low_mean", "high_minus_low", "cohen_d", "p_value"]]
        .round(4)
        .to_markdown(index=False)
        if not top_effects.empty
        else "No pole results available.",
        "",
        "## Largest Source-Adjusted Pole Effects",
        "",
        top_adjusted[
            [
                "coder_id",
                "factor",
                "dimension",
                "n",
                "source_family_count",
                "high_minus_low_source_adjusted",
                "standard_error",
                "p_value",
            ]
        ]
        .round(4)
        .to_markdown(index=False)
        if not top_adjusted.empty
        else "No source-adjusted effects available.",
        "",
        "## Inter-Coder Agreement",
        "",
        agreement.round(3).to_markdown(index=False) if not agreement.empty else "Only one coder/control is present; inter-coder agreement is not estimable.",
        "",
        "## Prior Automatic Full-Pole Alignment",
        "",
        compatible_alignment.round(3).to_markdown(index=False)
        if not compatible_alignment.empty
        else "No compatible prior alignment summary found.",
        "",
        "## Interpretation Rules",
        "",
        "- `support` means at least one expected construct dimension separates high/low poles with `|d| >= 0.5`, and the median expected `|d|` is also at least `0.5`.",
        "- Source-adjusted support uses a conservative rating scale threshold of `|beta| >= 0.3` after source-family fixed effects.",
        "- A factor should not graduate to a stronger construct name until this result is reproduced by at least two independent coders or coder models.",
        "- The auto lexical control is expected to perform well because it shares the same lexical basis as the anchor audit. It mainly catches broken joins, inverted poles, or unusable dimensions.",
        "",
        "## Artifacts",
        "",
        "- `results/suica_blind_construct_coding_evaluation_v1/merged_coder_key_ratings.csv`",
        "- `results/suica_blind_construct_coding_evaluation_v1/pole_separation_by_factor_dimension.csv`",
        "- `results/suica_blind_construct_coding_evaluation_v1/expected_dimension_gate.csv`",
        "- `results/suica_blind_construct_coding_evaluation_v1/source_adjusted_pole_effects.csv`",
        "- `results/suica_blind_construct_coding_evaluation_v1/source_adjusted_expected_dimension_gate.csv`",
        "- `results/suica_blind_construct_coding_evaluation_v1/inter_coder_agreement.csv`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    key = pd.read_csv(args.key)
    coder_frames = load_coder_frames(args)
    if coder_frames.empty:
        raise ValueError("No coder ratings found. Provide --coder-file or allow auto-control.")
    coded = coder_frames.merge(key, on="blind_item_id", how="inner", validate="many_to_one")
    rating_cols = rating_columns(coded)
    for col in rating_cols:
        coded[col] = pd.to_numeric(coded[col], errors="coerce")

    pole_results = evaluate_pole_separation(coded)
    expected_summary = expected_dimension_summary(pole_results)
    source_adjusted = source_adjusted_pole_effects(coded)
    source_adjusted_summary = expected_source_adjusted_summary(source_adjusted)
    agreement = inter_coder_agreement(coded)
    alignment = pd.read_csv(args.alignment_summary) if Path(args.alignment_summary).exists() else pd.DataFrame()
    auto_control = (not args.coder_file) and not args.no_auto_control

    coded.to_csv(out_dir / "merged_coder_key_ratings.csv", index=False)
    pole_results.to_csv(out_dir / "pole_separation_by_factor_dimension.csv", index=False)
    expected_summary.to_csv(out_dir / "expected_dimension_gate.csv", index=False)
    source_adjusted.to_csv(out_dir / "source_adjusted_pole_effects.csv", index=False)
    source_adjusted_summary.to_csv(out_dir / "source_adjusted_expected_dimension_gate.csv", index=False)
    agreement.to_csv(out_dir / "inter_coder_agreement.csv", index=False)
    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "key": str(Path(args.key)),
                "coder_files": args.coder_file,
                "coder_ids": args.coder_id,
                "auto_control": auto_control,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(
        Path(args.report_path),
        coded,
        pole_results,
        expected_summary,
        source_adjusted,
        source_adjusted_summary,
        agreement,
        alignment,
        auto_control,
    )
    print("SUICA blind construct coding evaluation complete.")
    print(expected_summary.round(3).to_string(index=False))
    print(f"\nReport: {display_path(Path(args.report_path))}")


if __name__ == "__main__":
    main()
