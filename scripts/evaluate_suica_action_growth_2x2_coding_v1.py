#!/usr/bin/env python
"""Evaluate SUICA action-growth 2x2 blind coding results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
KEY_PATH = ROOT / "results" / "suica_action_growth_2x2_batch_v1" / "action_growth_2x2_key.csv"
OUT_DIR = ROOT / "results" / "suica_action_growth_2x2_coding_eval_v1"
REPORT_PATH = ROOT / "reports" / "suica_action_growth_2x2_coding_eval_v1.md"

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
FOCAL_DIMENSIONS = ["directive_interpersonal", "redemption_growth", "communion"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate SUICA action-growth 2x2 coding v1.")
    parser.add_argument("--key", default=str(KEY_PATH))
    parser.add_argument("--coder-file", action="append", default=[], help="Coder rating CSV. Repeatable.")
    parser.add_argument("--coder-id", action="append", default=[], help="Optional coder id matching --coder-file order.")
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--marginal-threshold", type=float, default=0.5)
    parser.add_argument("--fused-threshold", type=float, default=0.5)
    parser.add_argument("--interaction-threshold", type=float, default=0.25)
    return parser.parse_args()


def load_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def rating_columns(frame: pd.DataFrame) -> list[str]:
    return [col for col in frame.columns if col.endswith("_0_to_3")]


def load_coder_frames(coder_files: list[str], coder_ids: list[str]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for idx, path in enumerate(coder_files):
        coder_id = coder_ids[idx] if idx < len(coder_ids) else Path(path).stem
        frame = load_csv(path)
        if "blind_item_id" not in frame.columns:
            raise ValueError(f"missing blind_item_id in coder file: {path}")
        cols = ["blind_item_id", *rating_columns(frame)]
        out = frame[cols].copy()
        out.insert(0, "coder_id", coder_id)
        frames.append(out)
    if not frames:
        raise ValueError("at least one --coder-file is required")
    return pd.concat(frames, ignore_index=True)


def pearson_r(left: pd.Series, right: pd.Series) -> float:
    left = pd.to_numeric(left, errors="coerce")
    right = pd.to_numeric(right, errors="coerce")
    mask = left.notna() & right.notna()
    if int(mask.sum()) < 4 or left[mask].std() < 1e-12 or right[mask].std() < 1e-12:
        return float("nan")
    return float(np.corrcoef(left[mask], right[mask])[0, 1])


def add_fused_scores(coded: pd.DataFrame) -> pd.DataFrame:
    out = coded.copy()
    directive = pd.to_numeric(out["directive_interpersonal_0_to_3"], errors="coerce")
    growth = pd.to_numeric(out["redemption_growth_0_to_3"], errors="coerce")
    out["directive_growth_min_score"] = np.minimum(directive, growth)
    out["directive_growth_product_score"] = directive * growth / 3.0
    return out


def cell_means(coded: pd.DataFrame) -> pd.DataFrame:
    value_cols = [f"{dim}_0_to_3" for dim in DIMENSIONS] + [
        "directive_growth_min_score",
        "directive_growth_product_score",
    ]
    rows: list[dict] = []
    for (coder_id, source_family, quadrant), group in coded.groupby(["coder_id", "source_family", "quadrant"], sort=True):
        row = {
            "coder_id": coder_id,
            "source_family": source_family,
            "quadrant": quadrant,
            "items": int(len(group)),
            "directive_flag": bool(group["directive_flag"].iloc[0]),
            "growth_flag": bool(group["growth_flag"].iloc[0]),
        }
        for col in value_cols:
            row[col.replace("_0_to_3", "") + "_mean"] = float(pd.to_numeric(group[col], errors="coerce").mean())
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["coder_id", "source_family", "quadrant"])


def source_adjusted_marginals(coded: pd.DataFrame) -> pd.DataFrame:
    value_cols = {
        "directive_interpersonal": "directive_interpersonal_0_to_3",
        "redemption_growth": "redemption_growth_0_to_3",
        "communion": "communion_0_to_3",
        "fused_min": "directive_growth_min_score",
        "fused_product": "directive_growth_product_score",
    }
    rows: list[dict] = []
    for coder_id, coder_rows in coded.groupby("coder_id", sort=True):
        for metric, col in value_cols.items():
            for flag_name, flag_col in [("directive_flag", "directive_flag"), ("growth_flag", "growth_flag")]:
                deltas: list[float] = []
                for _source, source_rows in coder_rows.groupby("source_family", sort=True):
                    high = pd.to_numeric(source_rows.loc[source_rows[flag_col].astype(bool), col], errors="coerce")
                    low = pd.to_numeric(source_rows.loc[~source_rows[flag_col].astype(bool), col], errors="coerce")
                    if high.empty or low.empty:
                        continue
                    deltas.append(float(high.mean() - low.mean()))
                rows.append(
                    {
                        "coder_id": coder_id,
                        "metric": metric,
                        "contrast": flag_name,
                        "source_adjusted_delta": float(np.mean(deltas)) if deltas else float("nan"),
                        "source_count": len(deltas),
                    }
                )
    return pd.DataFrame(rows).sort_values(["coder_id", "metric", "contrast"])


def interaction_effects(coded: pd.DataFrame) -> pd.DataFrame:
    value_cols = {
        "directive_interpersonal": "directive_interpersonal_0_to_3",
        "redemption_growth": "redemption_growth_0_to_3",
        "communion": "communion_0_to_3",
        "fused_min": "directive_growth_min_score",
        "fused_product": "directive_growth_product_score",
    }
    rows: list[dict] = []
    for coder_id, coder_rows in coded.groupby("coder_id", sort=True):
        for metric, col in value_cols.items():
            source_interactions: list[float] = []
            dg_vs_controls: list[float] = []
            for _source, source_rows in coder_rows.groupby("source_family", sort=True):
                means = source_rows.groupby("quadrant")[col].mean()
                required = {"directive_growth", "directive_only", "growth_only", "low_both"}
                if not required.issubset(set(means.index)):
                    continue
                interaction = (
                    float(means["directive_growth"])
                    - float(means["directive_only"])
                    - float(means["growth_only"])
                    + float(means["low_both"])
                )
                contrast = float(means["directive_growth"]) - max(
                    float(means["directive_only"]),
                    float(means["growth_only"]),
                    float(means["low_both"]),
                )
                source_interactions.append(interaction)
                dg_vs_controls.append(contrast)
            rows.append(
                {
                    "coder_id": coder_id,
                    "metric": metric,
                    "source_adjusted_interaction": float(np.mean(source_interactions)) if source_interactions else float("nan"),
                    "directive_growth_vs_max_control": float(np.mean(dg_vs_controls)) if dg_vs_controls else float("nan"),
                    "source_count": len(source_interactions),
                }
            )
    return pd.DataFrame(rows).sort_values(["coder_id", "metric"])


def coder_agreement(coded: pd.DataFrame) -> pd.DataFrame:
    coder_ids = sorted(coded["coder_id"].dropna().unique())
    if len(coder_ids) < 2:
        return pd.DataFrame()
    rows: list[dict] = []
    value_cols = [f"{dim}_0_to_3" for dim in DIMENSIONS] + [
        "directive_growth_min_score",
        "directive_growth_product_score",
    ]
    for i, coder_a in enumerate(coder_ids):
        a = coded.loc[coded["coder_id"].eq(coder_a)].copy()
        for coder_b in coder_ids[i + 1 :]:
            b = coded.loc[coded["coder_id"].eq(coder_b)].copy()
            merged = a.merge(b, on="blind_item_id", suffixes=("_a", "_b"))
            for col in value_cols:
                rows.append(
                    {
                        "metric": col.replace("_0_to_3", ""),
                        "coder_a": coder_a,
                        "coder_b": coder_b,
                        "n": int(len(merged)),
                        "pearson_r": pearson_r(merged[f"{col}_a"], merged[f"{col}_b"]),
                        "mean_abs_diff": float(
                            (
                                pd.to_numeric(merged[f"{col}_a"], errors="coerce")
                                - pd.to_numeric(merged[f"{col}_b"], errors="coerce")
                            )
                            .abs()
                            .mean()
                        ),
                    }
                )
    return pd.DataFrame(rows)


def acceptance_summary(
    marginals: pd.DataFrame,
    interactions: pd.DataFrame,
    agreement: pd.DataFrame,
    *,
    marginal_threshold: float,
    fused_threshold: float,
    interaction_threshold: float,
) -> pd.DataFrame:
    rows: list[dict] = []
    for coder_id in sorted(marginals["coder_id"].dropna().unique()):
        directive_delta = marginals.loc[
            marginals["coder_id"].eq(coder_id)
            & marginals["metric"].eq("directive_interpersonal")
            & marginals["contrast"].eq("directive_flag"),
            "source_adjusted_delta",
        ].iloc[0]
        growth_delta = marginals.loc[
            marginals["coder_id"].eq(coder_id)
            & marginals["metric"].eq("redemption_growth")
            & marginals["contrast"].eq("growth_flag"),
            "source_adjusted_delta",
        ].iloc[0]
        fused_row = interactions.loc[interactions["coder_id"].eq(coder_id) & interactions["metric"].eq("fused_min")].iloc[0]
        fused_contrast = float(fused_row["directive_growth_vs_max_control"])
        fused_interaction = float(fused_row["source_adjusted_interaction"])
        rows.append(
            {
                "coder_id": coder_id,
                "directive_marginal_delta": float(directive_delta),
                "growth_marginal_delta": float(growth_delta),
                "fused_min_dg_vs_max_control": fused_contrast,
                "fused_min_interaction_delta": fused_interaction,
                "marginal_gate": bool(directive_delta >= marginal_threshold and growth_delta >= marginal_threshold),
                "interaction_gate": bool(fused_contrast >= fused_threshold and fused_interaction >= interaction_threshold),
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    focal_agreement = agreement.loc[
        agreement["metric"].isin(["directive_interpersonal", "redemption_growth", "directive_growth_min_score"])
    ].copy()
    mean_agreement = float(focal_agreement["pearson_r"].mean()) if not focal_agreement.empty else float("nan")
    out["mean_focal_agreement"] = mean_agreement
    marginal_support = int(out["marginal_gate"].sum())
    interaction_support = int(out["interaction_gate"].sum())
    if marginal_support == len(out) and interaction_support == len(out):
        decision = "supports_directive_growth_interaction"
    elif marginal_support == len(out):
        decision = "supports_marginals_not_interaction"
    else:
        decision = "does_not_recover_required_marginals"
    out["overall_decision"] = decision
    return out


def write_report(
    path: Path,
    acceptance: pd.DataFrame,
    cells: pd.DataFrame,
    marginals: pd.DataFrame,
    interactions: pd.DataFrame,
    agreement: pd.DataFrame,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    focal_cells = [
        "coder_id",
        "source_family",
        "quadrant",
        "items",
        "directive_interpersonal_mean",
        "redemption_growth_mean",
        "directive_growth_min_score_mean",
        "directive_growth_product_score_mean",
    ]
    lines = [
        "# SUICA Action-Growth 2x2 Coding Evaluation v1",
        "",
        "## Purpose",
        "",
        "Evaluate whether the 2x2 action-growth item bank supports a fused directive-growth interaction beyond directive-only and growth-only marginal effects.",
        "",
        "## Acceptance Summary",
        "",
        acceptance.round(3).to_markdown(index=False) if not acceptance.empty else "No acceptance rows.",
        "",
        "## Cell Means",
        "",
        cells[[col for col in focal_cells if col in cells.columns]].round(3).to_markdown(index=False)
        if not cells.empty
        else "No cell means.",
        "",
        "## Source-Adjusted Marginals",
        "",
        marginals.loc[marginals["metric"].isin(["directive_interpersonal", "redemption_growth", "fused_min"])]
        .round(3)
        .to_markdown(index=False)
        if not marginals.empty
        else "No marginal rows.",
        "",
        "## Interaction Effects",
        "",
        interactions.loc[interactions["metric"].isin(["directive_interpersonal", "redemption_growth", "fused_min", "fused_product"])]
        .round(3)
        .to_markdown(index=False)
        if not interactions.empty
        else "No interaction rows.",
        "",
        "## Coder Agreement",
        "",
        agreement.loc[agreement["metric"].isin(["directive_interpersonal", "redemption_growth", "directive_growth_min_score", "directive_growth_product_score"])]
        .round(3)
        .to_markdown(index=False)
        if not agreement.empty
        else "Only one coder present.",
        "",
        "## Interpretation",
        "",
        "- `supports_directive_growth_interaction` requires both coders to recover directive and growth marginals, plus a fused score advantage for the directive-growth cell.",
        "- `supports_marginals_not_interaction` means coders see directive and growth separately, but the combined cell is not stronger than single-component controls.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    key = load_csv(args.key)
    coder = load_coder_frames(args.coder_file, args.coder_id)
    coded = coder.merge(key, on="blind_item_id", how="inner", validate="many_to_one")
    for col in rating_columns(coded):
        coded[col] = pd.to_numeric(coded[col], errors="coerce")
    coded = add_fused_scores(coded)
    cells = cell_means(coded)
    marginals = source_adjusted_marginals(coded)
    interactions = interaction_effects(coded)
    agreement = coder_agreement(coded)
    acceptance = acceptance_summary(
        marginals,
        interactions,
        agreement,
        marginal_threshold=args.marginal_threshold,
        fused_threshold=args.fused_threshold,
        interaction_threshold=args.interaction_threshold,
    )

    coded.to_csv(out_dir / "action_growth_2x2_merged_coder_key_ratings.csv", index=False)
    cells.to_csv(out_dir / "action_growth_2x2_cell_means.csv", index=False)
    marginals.to_csv(out_dir / "action_growth_2x2_source_adjusted_marginals.csv", index=False)
    interactions.to_csv(out_dir / "action_growth_2x2_interaction_effects.csv", index=False)
    agreement.to_csv(out_dir / "action_growth_2x2_inter_coder_agreement.csv", index=False)
    acceptance.to_csv(out_dir / "action_growth_2x2_acceptance_summary.csv", index=False)
    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "key": str(Path(args.key)),
                "coder_files": args.coder_file,
                "coder_ids": args.coder_id,
                "marginal_threshold": args.marginal_threshold,
                "fused_threshold": args.fused_threshold,
                "interaction_threshold": args.interaction_threshold,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(Path(args.report_path), acceptance, cells, marginals, interactions, agreement)
    print("SUICA action-growth 2x2 coding evaluation complete.")
    print(acceptance.round(3).to_string(index=False))
    print(f"\nReport: {Path(args.report_path)}")


if __name__ == "__main__":
    main()
