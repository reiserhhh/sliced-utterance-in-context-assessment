#!/usr/bin/env python
"""Evaluate SUICA expanded construct blind-coding results.

The expansion package contains both pole-contrast constructs and a 2x2
directive-growth interaction construct. This evaluator is intentionally
role-aware: run it on development first, freeze rules, then run heldout once.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
KEY_PATH = ROOT / "results" / "suica_construct_expansion_readiness_v1" / "expanded_item_bank_key.csv"
OUT_DIR = ROOT / "results" / "suica_construct_expansion_coding_eval_v1"
REPORT_PATH = ROOT / "reports" / "suica_construct_expansion_coding_eval_v1.md"

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
POLE_EXPECTED_PRIMARY = {
    "f05_novelty_play_core": ["novelty_play"],
    "f10_directive_action_core": ["directive_interpersonal"],
    "suica_adversity_recovery_core": ["redemption_growth"],
}
POLE_EXPECTED_SECONDARY = {
    "f05_novelty_play_core": [],
    "f10_directive_action_core": ["agency"],
    "suica_adversity_recovery_core": [],
}
INTERACTION_CONSTRUCT = "f10_directive_growth_interaction"
INTERACTION_CELLS = ["directive_growth", "directive_only", "growth_only", "low_both"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate SUICA expanded construct coding v1.")
    parser.add_argument("--key", default=str(KEY_PATH))
    parser.add_argument("--coder-file", action="append", default=[], help="Coder rating CSV. Repeatable.")
    parser.add_argument("--coder-id", action="append", default=[], help="Optional coder id matching --coder-file order.")
    parser.add_argument("--sample-role", default="development", choices=["development", "heldout", "all"])
    parser.add_argument("--interaction-construct", default=INTERACTION_CONSTRUCT)
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--pole-delta-threshold", type=float, default=0.3)
    parser.add_argument("--marginal-threshold", type=float, default=0.5)
    parser.add_argument("--fused-threshold", type=float, default=0.5)
    parser.add_argument("--interaction-threshold", type=float, default=0.25)
    parser.add_argument("--agreement-threshold", type=float, default=0.5)
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


def cohen_d(high: pd.Series, low: pd.Series) -> float:
    high = pd.to_numeric(high, errors="coerce").dropna()
    low = pd.to_numeric(low, errors="coerce").dropna()
    if len(high) < 2 or len(low) < 2:
        return float("nan")
    pooled = np.sqrt((high.var(ddof=1) + low.var(ddof=1)) / 2.0)
    if pooled < 1e-12:
        return float("nan")
    return float((high.mean() - low.mean()) / pooled)


def add_fused_scores(coded: pd.DataFrame) -> pd.DataFrame:
    out = coded.copy()
    directive = pd.to_numeric(out["directive_interpersonal_0_to_3"], errors="coerce")
    growth = pd.to_numeric(out["redemption_growth_0_to_3"], errors="coerce")
    out["directive_growth_min_score"] = np.minimum(directive, growth)
    out["directive_growth_product_score"] = directive * growth / 3.0
    return out


def filter_role(key: pd.DataFrame, sample_role: str) -> pd.DataFrame:
    if sample_role == "all":
        return key.copy()
    if "sample_role" not in key.columns:
        raise ValueError("key file missing sample_role")
    return key.loc[key["sample_role"].eq(sample_role)].copy()


def merge_coder_key(key: pd.DataFrame, coder: pd.DataFrame, sample_role: str) -> pd.DataFrame:
    role_key = filter_role(key, sample_role)
    coded = coder.merge(role_key, on="blind_item_id", how="inner", validate="many_to_one")
    missing = sorted(set(coder["blind_item_id"].astype(str)).difference(set(coded["blind_item_id"].astype(str))))
    if missing:
        raise ValueError(f"{len(missing)} coder items were not found in {sample_role} key; examples={missing[:5]}")
    for col in rating_columns(coded):
        coded[col] = pd.to_numeric(coded[col], errors="coerce")
    return add_fused_scores(coded)


def pole_separation(coded: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    pole_rows = coded.loc[coded["construct_type"].eq("pole_contrast")].copy()
    columns = [
        "coder_id",
        "construct_id",
        "construct_label",
        "dimension",
        "high_n",
        "low_n",
        "high_mean",
        "low_mean",
        "high_minus_low",
        "cohen_d",
    ]
    if pole_rows.empty:
        return pd.DataFrame(columns=columns)
    for (coder_id, construct_id), group in pole_rows.groupby(["coder_id", "construct_id"], sort=True):
        for dimension in DIMENSIONS:
            col = f"{dimension}_0_to_3"
            high = pd.to_numeric(group.loc[group["cell"].eq("high"), col], errors="coerce")
            low = pd.to_numeric(group.loc[group["cell"].eq("low"), col], errors="coerce")
            rows.append(
                {
                    "coder_id": coder_id,
                    "construct_id": construct_id,
                    "construct_label": group["construct_label"].iloc[0],
                    "dimension": dimension,
                    "high_n": int(high.notna().sum()),
                    "low_n": int(low.notna().sum()),
                    "high_mean": float(high.mean()),
                    "low_mean": float(low.mean()),
                    "high_minus_low": float(high.mean() - low.mean()),
                    "cohen_d": cohen_d(high, low),
                }
            )
    return pd.DataFrame(rows, columns=columns).sort_values(
        ["coder_id", "construct_id", "high_minus_low"], ascending=[True, True, False]
    )


def pole_source_adjusted(coded: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    pole_rows = coded.loc[coded["construct_type"].eq("pole_contrast")].copy()
    columns = [
        "coder_id",
        "construct_id",
        "construct_label",
        "dimension",
        "source_family_count",
        "source_adjusted_high_minus_low",
    ]
    if pole_rows.empty:
        return pd.DataFrame(columns=columns)
    for (coder_id, construct_id), group in pole_rows.groupby(["coder_id", "construct_id"], sort=True):
        for dimension in DIMENSIONS:
            col = f"{dimension}_0_to_3"
            deltas: list[float] = []
            for _source, source_rows in group.groupby("source_family", sort=True):
                high = pd.to_numeric(source_rows.loc[source_rows["cell"].eq("high"), col], errors="coerce")
                low = pd.to_numeric(source_rows.loc[source_rows["cell"].eq("low"), col], errors="coerce")
                if high.empty or low.empty:
                    continue
                deltas.append(float(high.mean() - low.mean()))
            rows.append(
                {
                    "coder_id": coder_id,
                    "construct_id": construct_id,
                    "construct_label": group["construct_label"].iloc[0],
                    "dimension": dimension,
                    "source_family_count": int(group["source_family"].nunique()),
                    "source_adjusted_high_minus_low": float(np.mean(deltas)) if deltas else float("nan"),
                }
            )
    return pd.DataFrame(rows, columns=columns).sort_values(
        ["coder_id", "construct_id", "source_adjusted_high_minus_low"], ascending=[True, True, False]
    )


def pole_expected_gate(pole: pd.DataFrame, source: pd.DataFrame, *, delta_threshold: float) -> pd.DataFrame:
    rows: list[dict] = []
    columns = [
        "coder_id",
        "construct_id",
        "construct_label",
        "dimension_role",
        "expected_dimensions",
        "expected_dimension_count",
        "delta_support_count",
        "source_adjusted_support_count",
        "min_expected_delta",
        "mean_expected_delta",
        "min_expected_source_adjusted_delta",
        "mean_expected_source_adjusted_delta",
        "hard_gate",
        "component_gate",
    ]
    if pole.empty:
        return pd.DataFrame(columns=columns)
    for (coder_id, construct_id), group in pole.groupby(["coder_id", "construct_id"], sort=True):
        primary = POLE_EXPECTED_PRIMARY.get(construct_id, [])
        secondary = POLE_EXPECTED_SECONDARY.get(construct_id, [])
        for role_name, dimensions, hard_gate in [("primary", primary, True), ("secondary", secondary, False)]:
            if not dimensions:
                continue
            expected_rows = group.loc[group["dimension"].isin(dimensions)]
            source_rows = source.loc[
                source["coder_id"].eq(coder_id)
                & source["construct_id"].eq(construct_id)
                & source["dimension"].isin(dimensions)
            ]
            support = int((expected_rows["high_minus_low"] >= delta_threshold).sum())
            source_support = int((source_rows["source_adjusted_high_minus_low"] >= delta_threshold).sum())
            rows.append(
                {
                    "coder_id": coder_id,
                    "construct_id": construct_id,
                    "construct_label": group["construct_label"].iloc[0],
                    "dimension_role": role_name,
                    "expected_dimensions": "; ".join(dimensions),
                    "expected_dimension_count": len(dimensions),
                    "delta_support_count": support,
                    "source_adjusted_support_count": source_support,
                    "min_expected_delta": float(expected_rows["high_minus_low"].min()),
                    "mean_expected_delta": float(expected_rows["high_minus_low"].mean()),
                    "min_expected_source_adjusted_delta": float(source_rows["source_adjusted_high_minus_low"].min()),
                    "mean_expected_source_adjusted_delta": float(source_rows["source_adjusted_high_minus_low"].mean()),
                    "hard_gate": hard_gate,
                    "component_gate": bool(support == len(dimensions) and source_support == len(dimensions)),
                }
            )
    return pd.DataFrame(rows, columns=columns).sort_values(["construct_id", "dimension_role", "coder_id"])


def interaction_source_adjusted_marginals(coded: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    work = coded.loc[coded["construct_id"].eq(INTERACTION_CONSTRUCT)].copy()
    columns = [
        "coder_id",
        "construct_id",
        "metric",
        "contrast",
        "source_adjusted_delta",
        "source_count",
    ]
    if work.empty:
        return pd.DataFrame(columns=columns)
    for coder_id, coder_rows in work.groupby("coder_id", sort=True):
        metrics = {
            "directive_interpersonal": "directive_interpersonal_0_to_3",
            "redemption_growth": "redemption_growth_0_to_3",
            "fused_min": "directive_growth_min_score",
            "fused_product": "directive_growth_product_score",
        }
        for metric, col in metrics.items():
            for contrast_name, high_cells, low_cells in [
                ("directive_flag", ["directive_growth", "directive_only"], ["growth_only", "low_both"]),
                ("growth_flag", ["directive_growth", "growth_only"], ["directive_only", "low_both"]),
            ]:
                deltas: list[float] = []
                for _source, source_rows in coder_rows.groupby("source_family", sort=True):
                    high = pd.to_numeric(source_rows.loc[source_rows["cell"].isin(high_cells), col], errors="coerce")
                    low = pd.to_numeric(source_rows.loc[source_rows["cell"].isin(low_cells), col], errors="coerce")
                    if high.empty or low.empty:
                        continue
                    deltas.append(float(high.mean() - low.mean()))
                rows.append(
                    {
                        "coder_id": coder_id,
                        "construct_id": INTERACTION_CONSTRUCT,
                        "metric": metric,
                        "contrast": contrast_name,
                        "source_adjusted_delta": float(np.mean(deltas)) if deltas else float("nan"),
                        "source_count": len(deltas),
                    }
                )
    return pd.DataFrame(rows, columns=columns).sort_values(["coder_id", "metric", "contrast"])


def interaction_effects(coded: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    work = coded.loc[coded["construct_id"].eq(INTERACTION_CONSTRUCT)].copy()
    columns = [
        "coder_id",
        "construct_id",
        "metric",
        "source_adjusted_interaction",
        "directive_growth_vs_max_control",
        "source_count",
    ]
    if work.empty:
        return pd.DataFrame(columns=columns)
    metrics = {
        "directive_interpersonal": "directive_interpersonal_0_to_3",
        "redemption_growth": "redemption_growth_0_to_3",
        "fused_min": "directive_growth_min_score",
        "fused_product": "directive_growth_product_score",
    }
    for coder_id, coder_rows in work.groupby("coder_id", sort=True):
        for metric, col in metrics.items():
            source_interactions: list[float] = []
            dg_vs_controls: list[float] = []
            for _source, source_rows in coder_rows.groupby("source_family", sort=True):
                means = source_rows.groupby("cell")[col].mean()
                if not set(INTERACTION_CELLS).issubset(set(means.index)):
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
                    "construct_id": INTERACTION_CONSTRUCT,
                    "metric": metric,
                    "source_adjusted_interaction": float(np.mean(source_interactions)) if source_interactions else float("nan"),
                    "directive_growth_vs_max_control": float(np.mean(dg_vs_controls)) if dg_vs_controls else float("nan"),
                    "source_count": len(source_interactions),
                }
            )
    return pd.DataFrame(rows, columns=columns).sort_values(["coder_id", "metric"])


def interaction_cell_means(coded: pd.DataFrame) -> pd.DataFrame:
    work = coded.loc[coded["construct_id"].eq(INTERACTION_CONSTRUCT)].copy()
    columns = [
        "coder_id",
        "source_family",
        "cell",
        "items",
        "directive_interpersonal_mean",
        "redemption_growth_mean",
        "directive_growth_min_score_mean",
        "directive_growth_product_score_mean",
    ]
    if work.empty:
        return pd.DataFrame(columns=columns)
    value_cols = [
        "directive_interpersonal_0_to_3",
        "redemption_growth_0_to_3",
        "directive_growth_min_score",
        "directive_growth_product_score",
    ]
    rows: list[dict] = []
    for (coder_id, source, cell), group in work.groupby(["coder_id", "source_family", "cell"], sort=True):
        row = {"coder_id": coder_id, "source_family": source, "cell": cell, "items": int(len(group))}
        for col in value_cols:
            row[col.replace("_0_to_3", "") + "_mean"] = float(pd.to_numeric(group[col], errors="coerce").mean())
        rows.append(row)
    return pd.DataFrame(rows, columns=columns).sort_values(["coder_id", "source_family", "cell"])


def coder_agreement(coded: pd.DataFrame) -> pd.DataFrame:
    coder_ids = sorted(coded["coder_id"].dropna().unique())
    if len(coder_ids) < 2:
        return pd.DataFrame()
    rows: list[dict] = []
    value_cols = [f"{dimension}_0_to_3" for dimension in DIMENSIONS] + [
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
    pole_gate: pd.DataFrame,
    interaction_marginals: pd.DataFrame,
    interactions: pd.DataFrame,
    agreement: pd.DataFrame,
    *,
    marginal_threshold: float,
    fused_threshold: float,
    interaction_threshold: float,
    agreement_threshold: float,
) -> pd.DataFrame:
    rows: list[dict] = []
    for construct_id, group in pole_gate.loc[pole_gate["hard_gate"]].groupby("construct_id", sort=True):
        expected_dims = POLE_EXPECTED_PRIMARY.get(construct_id, [])
        agree_rows = agreement.loc[agreement["metric"].isin(expected_dims)] if not agreement.empty else pd.DataFrame()
        mean_agreement = float(agree_rows["pearson_r"].mean()) if not agree_rows.empty else float("nan")
        support = int(group["component_gate"].sum())
        decision = (
            "pass_development_gate"
            if support == group["coder_id"].nunique() and (np.isnan(mean_agreement) or mean_agreement >= agreement_threshold)
            else "do_not_freeze_needs_repair"
        )
        rows.append(
            {
                "construct_id": construct_id,
                "construct_type": "pole_contrast",
                "coder_count": int(group["coder_id"].nunique()),
                "support_coder_count": support,
                "expected_dimensions": "; ".join(expected_dims),
                "min_expected_delta": float(group["min_expected_delta"].min()),
                "min_source_adjusted_delta": float(group["min_expected_source_adjusted_delta"].min()),
                "mean_expected_agreement": mean_agreement,
                "decision": decision,
            }
        )

    for coder_id in sorted(interaction_marginals["coder_id"].dropna().unique()):
        directive_delta = interaction_marginals.loc[
            interaction_marginals["coder_id"].eq(coder_id)
            & interaction_marginals["metric"].eq("directive_interpersonal")
            & interaction_marginals["contrast"].eq("directive_flag"),
            "source_adjusted_delta",
        ].iloc[0]
        growth_delta = interaction_marginals.loc[
            interaction_marginals["coder_id"].eq(coder_id)
            & interaction_marginals["metric"].eq("redemption_growth")
            & interaction_marginals["contrast"].eq("growth_flag"),
            "source_adjusted_delta",
        ].iloc[0]
        fused_row = interactions.loc[interactions["coder_id"].eq(coder_id) & interactions["metric"].eq("fused_min")].iloc[0]
        rows.append(
            {
                "construct_id": INTERACTION_CONSTRUCT,
                "construct_type": "interaction_2x2",
                "coder_id": coder_id,
                "directive_marginal_delta": float(directive_delta),
                "growth_marginal_delta": float(growth_delta),
                "fused_min_dg_vs_max_control": float(fused_row["directive_growth_vs_max_control"]),
                "fused_min_interaction_delta": float(fused_row["source_adjusted_interaction"]),
                "marginal_gate": bool(directive_delta >= marginal_threshold and growth_delta >= marginal_threshold),
                "interaction_gate": bool(
                    float(fused_row["directive_growth_vs_max_control"]) >= fused_threshold
                    and float(fused_row["source_adjusted_interaction"]) >= interaction_threshold
                ),
            }
        )

    out = pd.DataFrame(rows)
    for col in ["construct_id", "construct_type", "coder_id"]:
        if col not in out.columns:
            out[col] = np.nan
    if INTERACTION_CONSTRUCT in set(out["construct_id"]):
        interaction_mask = out["construct_id"].eq(INTERACTION_CONSTRUCT)
        focal = agreement.loc[
            agreement["metric"].isin(["directive_interpersonal", "redemption_growth", "directive_growth_min_score"])
        ]
        mean_agreement = float(focal["pearson_r"].mean()) if not focal.empty else float("nan")
        all_support = bool(out.loc[interaction_mask, "marginal_gate"].all() and out.loc[interaction_mask, "interaction_gate"].all())
        decision = (
            "pass_development_gate"
            if all_support and (np.isnan(mean_agreement) or mean_agreement >= agreement_threshold)
            else "do_not_freeze_needs_repair"
        )
        out.loc[interaction_mask, "mean_expected_agreement"] = mean_agreement
        out.loc[interaction_mask, "decision"] = decision
    return out.sort_values(["construct_id", "construct_type", "coder_id"], na_position="last")


def write_report(
    path: Path,
    *,
    sample_role: str,
    coded: pd.DataFrame,
    acceptance: pd.DataFrame,
    pole_gate: pd.DataFrame,
    pole: pd.DataFrame,
    source: pd.DataFrame,
    interaction_marginals: pd.DataFrame,
    interactions: pd.DataFrame,
    cell_means: pd.DataFrame,
    agreement: pd.DataFrame,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    expected_dims = ["novelty_play", "directive_interpersonal", "agency", "redemption_growth"]
    top_pole = pole.loc[pole["dimension"].isin(expected_dims)].copy()
    top_source = source.loc[source["dimension"].isin(expected_dims)].copy()
    lines = [
        "# SUICA Construct Expansion Coding Evaluation v1",
        "",
        "## Purpose",
        "",
        "Evaluate the expanded SUICA construct item bank. Development results may be used to freeze scoring rules; heldout results must only be evaluated after freezing.",
        "",
        "## Run Scope",
        "",
        f"- sample_role: `{sample_role}`",
        f"- coded rows: `{len(coded)}`",
        f"- constructs: `{coded['construct_id'].nunique() if not coded.empty else 0}`",
        "",
        "## Acceptance Summary",
        "",
        acceptance.round(3).to_markdown(index=False) if not acceptance.empty else "No acceptance rows.",
        "",
        "## Pole Construct Expected Gates",
        "",
        pole_gate.round(3).to_markdown(index=False) if not pole_gate.empty else "No pole gate rows.",
        "",
        "## Pole Construct Contrasts",
        "",
        top_pole.round(3).to_markdown(index=False) if not top_pole.empty else "No pole rows.",
        "",
        "## Pole Source-Adjusted Contrasts",
        "",
        top_source.round(3).to_markdown(index=False) if not top_source.empty else "No source-adjusted rows.",
        "",
        "## Interaction Marginals",
        "",
        interaction_marginals.round(3).to_markdown(index=False) if not interaction_marginals.empty else "No interaction marginal rows.",
        "",
        "## Interaction Effects",
        "",
        interactions.round(3).to_markdown(index=False) if not interactions.empty else "No interaction rows.",
        "",
        "## Interaction Cell Means",
        "",
        cell_means.round(3).to_markdown(index=False) if not cell_means.empty else "No cell means.",
        "",
        "## Inter-Coder Agreement",
        "",
        agreement.round(3).to_markdown(index=False) if not agreement.empty else "Only one coder present.",
        "",
        "## Interpretation Rules",
        "",
        "- `pass_development_gate` means the development package supports freezing this construct's coding/scoring rule for heldout testing.",
        "- `do_not_freeze_needs_repair` means item selection or construct definition should be repaired before touching heldout.",
        "- Big5/MBTI are intentionally absent from this evaluator; they remain external validity anchors only.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    global INTERACTION_CONSTRUCT
    INTERACTION_CONSTRUCT = args.interaction_construct
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    key = load_csv(args.key)
    coder = load_coder_frames(args.coder_file, args.coder_id)
    coded = merge_coder_key(key, coder, args.sample_role)
    pole = pole_separation(coded)
    source = pole_source_adjusted(coded)
    pole_gate = pole_expected_gate(pole, source, delta_threshold=args.pole_delta_threshold)
    interaction_marginals = interaction_source_adjusted_marginals(coded)
    interactions = interaction_effects(coded)
    cell_means = interaction_cell_means(coded)
    agreement = coder_agreement(coded)
    acceptance = acceptance_summary(
        pole_gate,
        interaction_marginals,
        interactions,
        agreement,
        marginal_threshold=args.marginal_threshold,
        fused_threshold=args.fused_threshold,
        interaction_threshold=args.interaction_threshold,
        agreement_threshold=args.agreement_threshold,
    )
    if args.sample_role == "heldout" and "decision" in acceptance.columns:
        acceptance["decision"] = acceptance["decision"].replace({"pass_development_gate": "pass_heldout_gate"})

    coded.to_csv(out_dir / f"{args.sample_role}_merged_coder_key_ratings.csv", index=False)
    pole.to_csv(out_dir / f"{args.sample_role}_pole_separation.csv", index=False)
    source.to_csv(out_dir / f"{args.sample_role}_pole_source_adjusted.csv", index=False)
    pole_gate.to_csv(out_dir / f"{args.sample_role}_pole_expected_gate.csv", index=False)
    interaction_marginals.to_csv(out_dir / f"{args.sample_role}_interaction_marginals.csv", index=False)
    interactions.to_csv(out_dir / f"{args.sample_role}_interaction_effects.csv", index=False)
    cell_means.to_csv(out_dir / f"{args.sample_role}_interaction_cell_means.csv", index=False)
    agreement.to_csv(out_dir / f"{args.sample_role}_inter_coder_agreement.csv", index=False)
    acceptance.to_csv(out_dir / f"{args.sample_role}_acceptance_summary.csv", index=False)
    (out_dir / f"{args.sample_role}_run_config.json").write_text(
        json.dumps(
            {
                "key": str(Path(args.key)),
                "coder_files": args.coder_file,
                "coder_ids": args.coder_id,
                "sample_role": args.sample_role,
                "pole_expected_primary": POLE_EXPECTED_PRIMARY,
                "pole_expected_secondary": POLE_EXPECTED_SECONDARY,
                "interaction_construct": INTERACTION_CONSTRUCT,
                "thresholds": {
                    "pole_delta": args.pole_delta_threshold,
                    "marginal": args.marginal_threshold,
                    "fused": args.fused_threshold,
                    "interaction": args.interaction_threshold,
                    "agreement": args.agreement_threshold,
                },
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(
        Path(args.report_path),
        sample_role=args.sample_role,
        coded=coded,
        acceptance=acceptance,
        pole_gate=pole_gate,
        pole=pole,
        source=source,
        interaction_marginals=interaction_marginals,
        interactions=interactions,
        cell_means=cell_means,
        agreement=agreement,
    )
    print("SUICA construct expansion coding evaluation complete.")
    print(acceptance.round(3).to_string(index=False))
    print(f"\nReport: {Path(args.report_path)}")


if __name__ == "__main__":
    main()
