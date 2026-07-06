#!/usr/bin/env python
"""Evaluate independent LLM coding for SUICA repair-candidate blind batches."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
KEY_PATH = ROOT / "results" / "suica_repair_candidate_blind_batch_v1" / "repair_blind_coding_key.csv"
OUT_DIR = ROOT / "results" / "suica_repair_candidate_coding_eval_v1"
REPORT_PATH = ROOT / "reports" / "suica_repair_candidate_coding_eval_v1.md"


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


CANDIDATE_EXPECTED_DIMENSIONS = {
    "f05_novelty_play_core": ["novelty_play"],
    "f10_directive_action_core": ["directive_interpersonal"],
    "f10_action_growth_channel": ["directive_interpersonal", "redemption_growth", "communion"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate SUICA repair-candidate LLM coding v1.")
    parser.add_argument("--key", default=str(KEY_PATH))
    parser.add_argument("--coder-file", action="append", default=[], help="Coder rating CSV. Repeatable.")
    parser.add_argument("--coder-id", action="append", default=[], help="Optional coder id matching --coder-file order.")
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--delta-threshold", type=float, default=0.3)
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
            raise ValueError(f"missing blind_item_id in {path}")
        cols = ["blind_item_id", *rating_columns(frame)]
        out = frame[cols].copy()
        out.insert(0, "coder_id", coder_id)
        frames.append(out)
    if not frames:
        raise ValueError("at least one --coder-file is required")
    return pd.concat(frames, ignore_index=True)


def cohen_d(high: pd.Series, low: pd.Series) -> float:
    high = pd.to_numeric(high, errors="coerce").dropna()
    low = pd.to_numeric(low, errors="coerce").dropna()
    if len(high) < 2 or len(low) < 2:
        return float("nan")
    pooled = np.sqrt((high.var(ddof=1) + low.var(ddof=1)) / 2.0)
    if pooled < 1e-12:
        return float("nan")
    return float((high.mean() - low.mean()) / pooled)


def pearson_r(left: pd.Series, right: pd.Series) -> float:
    left = pd.to_numeric(left, errors="coerce")
    right = pd.to_numeric(right, errors="coerce")
    mask = left.notna() & right.notna()
    if int(mask.sum()) < 4 or left[mask].std() < 1e-12 or right[mask].std() < 1e-12:
        return float("nan")
    return float(np.corrcoef(left[mask], right[mask])[0, 1])


def evaluate_pole_separation(coded: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for (coder_id, candidate_id), group in coded.groupby(["coder_id", "candidate_id"], sort=True):
        for dimension in DIMENSIONS:
            col = f"{dimension}_0_to_3"
            high = pd.to_numeric(group.loc[group["pole"].eq("high"), col], errors="coerce")
            low = pd.to_numeric(group.loc[group["pole"].eq("low"), col], errors="coerce")
            rows.append(
                {
                    "coder_id": coder_id,
                    "candidate_id": candidate_id,
                    "candidate_label": group["candidate_label"].iloc[0],
                    "dimension": dimension,
                    "high_n": int(high.notna().sum()),
                    "low_n": int(low.notna().sum()),
                    "high_mean": float(high.mean()),
                    "low_mean": float(low.mean()),
                    "high_minus_low": float(high.mean() - low.mean()),
                    "cohen_d": cohen_d(high, low),
                }
            )
    return pd.DataFrame(rows).sort_values(["coder_id", "candidate_id", "high_minus_low"], ascending=[True, True, False])


def source_adjusted_delta(coded: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for (coder_id, candidate_id), group in coded.groupby(["coder_id", "candidate_id"], sort=True):
        for dimension in DIMENSIONS:
            col = f"{dimension}_0_to_3"
            deltas: list[float] = []
            for source, source_rows in group.groupby("source_family", sort=True):
                high = pd.to_numeric(source_rows.loc[source_rows["pole"].eq("high"), col], errors="coerce")
                low = pd.to_numeric(source_rows.loc[source_rows["pole"].eq("low"), col], errors="coerce")
                if high.empty or low.empty:
                    continue
                deltas.append(float(high.mean() - low.mean()))
            rows.append(
                {
                    "coder_id": coder_id,
                    "candidate_id": candidate_id,
                    "candidate_label": group["candidate_label"].iloc[0],
                    "dimension": dimension,
                    "source_family_count": int(group["source_family"].nunique()),
                    "source_adjusted_high_minus_low": float(np.mean(deltas)) if deltas else float("nan"),
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["coder_id", "candidate_id", "source_adjusted_high_minus_low"], ascending=[True, True, False]
    )


def expected_gate(
    pole: pd.DataFrame,
    source_adjusted: pd.DataFrame,
    *,
    delta_threshold: float,
) -> pd.DataFrame:
    rows: list[dict] = []
    for (coder_id, candidate_id), group in pole.groupby(["coder_id", "candidate_id"], sort=True):
        expected = CANDIDATE_EXPECTED_DIMENSIONS.get(candidate_id, [])
        expected_rows = group.loc[group["dimension"].isin(expected)].copy()
        source_rows = source_adjusted.loc[
            source_adjusted["coder_id"].eq(coder_id)
            & source_adjusted["candidate_id"].eq(candidate_id)
            & source_adjusted["dimension"].isin(expected)
        ].copy()
        if expected_rows.empty:
            continue
        delta_support = int((expected_rows["high_minus_low"] >= delta_threshold).sum())
        source_support = int((source_rows["source_adjusted_high_minus_low"] >= delta_threshold).sum())
        component_count = len(expected)
        all_components_supported = delta_support == component_count and source_support == component_count
        rows.append(
            {
                "coder_id": coder_id,
                "candidate_id": candidate_id,
                "candidate_label": expected_rows["candidate_label"].iloc[0],
                "expected_dimensions": "; ".join(expected),
                "expected_dimension_count": component_count,
                "delta_support_count": delta_support,
                "source_adjusted_support_count": source_support,
                "min_expected_delta": float(expected_rows["high_minus_low"].min()),
                "mean_expected_delta": float(expected_rows["high_minus_low"].mean()),
                "min_expected_source_adjusted_delta": float(source_rows["source_adjusted_high_minus_low"].min()),
                "mean_expected_source_adjusted_delta": float(source_rows["source_adjusted_high_minus_low"].mean()),
                "component_coverage_gate": bool(all_components_supported),
                "micro_batch_gate": "support" if all_components_supported else "weak_or_source_sensitive",
            }
        )
    return pd.DataFrame(rows).sort_values(["candidate_id", "coder_id"])


def coder_agreement(coded: pd.DataFrame) -> pd.DataFrame:
    coder_ids = sorted(coded["coder_id"].dropna().unique())
    if len(coder_ids) < 2:
        return pd.DataFrame()
    rows: list[dict] = []
    for i, coder_a in enumerate(coder_ids):
        a = coded.loc[coded["coder_id"].eq(coder_a)].copy()
        for coder_b in coder_ids[i + 1 :]:
            b = coded.loc[coded["coder_id"].eq(coder_b)].copy()
            merged = a.merge(b, on="blind_item_id", suffixes=("_a", "_b"))
            for dimension in DIMENSIONS:
                col_a = f"{dimension}_0_to_3_a"
                col_b = f"{dimension}_0_to_3_b"
                rows.append(
                    {
                        "dimension": dimension,
                        "coder_a": coder_a,
                        "coder_b": coder_b,
                        "n": int(len(merged)),
                        "pearson_r": pearson_r(merged[col_a], merged[col_b]),
                        "mean_abs_diff": float(
                            (pd.to_numeric(merged[col_a], errors="coerce") - pd.to_numeric(merged[col_b], errors="coerce")).abs().mean()
                        ),
                    }
                )
    return pd.DataFrame(rows)


def candidate_acceptance(gate: pd.DataFrame, agreement: pd.DataFrame, *, agreement_threshold: float) -> pd.DataFrame:
    rows: list[dict] = []
    for candidate_id, group in gate.groupby("candidate_id", sort=True):
        expected = CANDIDATE_EXPECTED_DIMENSIONS.get(candidate_id, [])
        if agreement.empty or "dimension" not in agreement.columns:
            agree_rows = pd.DataFrame()
        else:
            agree_rows = agreement.loc[agreement["dimension"].isin(expected)].copy()
        mean_agreement = float(agree_rows["pearson_r"].mean()) if not agree_rows.empty else float("nan")
        support_coders = int(group["micro_batch_gate"].eq("support").sum())
        decision = (
            "pass_micro_confirmation"
            if support_coders == group["coder_id"].nunique() and (np.isnan(mean_agreement) or mean_agreement >= agreement_threshold)
            else "needs_item_bank_repair_or_larger_batch"
        )
        rows.append(
            {
                "candidate_id": candidate_id,
                "candidate_label": group["candidate_label"].iloc[0],
                "expected_dimensions": "; ".join(expected),
                "coder_count": int(group["coder_id"].nunique()),
                "support_coder_count": support_coders,
                "min_expected_delta_across_coders": float(group["min_expected_delta"].min()),
                "min_source_adjusted_delta_across_coders": float(group["min_expected_source_adjusted_delta"].min()),
                "mean_expected_dimension_agreement": mean_agreement,
                "decision": decision,
            }
        )
    return pd.DataFrame(rows).sort_values(["decision", "candidate_id"])


def write_report(
    path: Path,
    acceptance: pd.DataFrame,
    gate: pd.DataFrame,
    pole: pd.DataFrame,
    source_adjusted: pd.DataFrame,
    agreement: pd.DataFrame,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    top_pole = pole.loc[pole["dimension"].isin(["novelty_play", "directive_interpersonal", "redemption_growth", "communion"])].copy()
    top_source = source_adjusted.loc[
        source_adjusted["dimension"].isin(["novelty_play", "directive_interpersonal", "redemption_growth", "communion"])
    ].copy()
    lines = [
        "# SUICA Repair Candidate Coding Evaluation v1",
        "",
        "## Purpose",
        "",
        "Evaluate the source-balanced repair-candidate micro-batch using candidate-specific expected dimensions. This is a confirmation/triage gate, not final psychometric validation.",
        "",
        "## Candidate Acceptance",
        "",
        acceptance.round(3).to_markdown(index=False) if not acceptance.empty else "No acceptance rows.",
        "",
        "## Candidate Expected-Dimension Gate",
        "",
        gate.round(3).to_markdown(index=False) if not gate.empty else "No gate rows.",
        "",
        "## Expected-Dimension Pole Contrasts",
        "",
        top_pole.round(3).to_markdown(index=False) if not top_pole.empty else "No pole rows.",
        "",
        "## Expected-Dimension Source-Adjusted Deltas",
        "",
        top_source.round(3).to_markdown(index=False) if not top_source.empty else "No source-adjusted rows.",
        "",
        "## Inter-Coder Agreement",
        "",
        agreement.round(3).to_markdown(index=False) if not agreement.empty else "Only one coder present.",
        "",
        "## Interpretation",
        "",
        "- Passing this micro-batch means a repair candidate survived a small blinded confirmation check.",
        "- Failing this micro-batch does not kill the candidate; it means the item bank is too small or source-sensitive.",
        "- Release-grade validation still requires larger balanced item banks and preferably human or third-model coding.",
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

    pole = evaluate_pole_separation(coded)
    source = source_adjusted_delta(coded)
    gate = expected_gate(pole, source, delta_threshold=args.delta_threshold)
    agreement = coder_agreement(coded)
    acceptance = candidate_acceptance(gate, agreement, agreement_threshold=args.agreement_threshold)

    coded.to_csv(out_dir / "merged_repair_coder_key_ratings.csv", index=False)
    pole.to_csv(out_dir / "repair_pole_separation_by_candidate_dimension.csv", index=False)
    source.to_csv(out_dir / "repair_source_adjusted_candidate_dimension.csv", index=False)
    gate.to_csv(out_dir / "repair_expected_dimension_gate.csv", index=False)
    agreement.to_csv(out_dir / "repair_inter_coder_agreement.csv", index=False)
    acceptance.to_csv(out_dir / "repair_candidate_acceptance_summary.csv", index=False)
    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "key": str(Path(args.key)),
                "coder_files": args.coder_file,
                "coder_ids": args.coder_id,
                "delta_threshold": args.delta_threshold,
                "agreement_threshold": args.agreement_threshold,
                "candidate_expected_dimensions": CANDIDATE_EXPECTED_DIMENSIONS,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(Path(args.report_path), acceptance, gate, pole, source, agreement)
    print("SUICA repair candidate coding evaluation complete.")
    print(acceptance.round(3).to_string(index=False))
    print(f"\nReport: {Path(args.report_path)}")


if __name__ == "__main__":
    main()
