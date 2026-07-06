#!/usr/bin/env python
"""Evaluate narrowed or split SUICA repair candidates from existing blind ratings."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "results" / "suica_independent_coding_eval_deepseek_AB_full_v1"
WEAK_DIR = ROOT / "results" / "suica_weak_factor_diagnosis_v1"
OUT_DIR = ROOT / "results" / "suica_repair_candidate_rescoring_v1"
REPORT_PATH = ROOT / "reports" / "suica_repair_candidate_rescoring_v1.md"


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


@dataclass(frozen=True)
class CandidateSpec:
    """A repair candidate expressed as a signed composite of coder dimensions."""

    candidate_id: str
    parent_factor: str
    label: str
    weights: dict[str, float]
    rationale: str


CANDIDATES = [
    CandidateSpec(
        candidate_id="f05_original_expected_play_agency",
        parent_factor="suica_factor_05",
        label="original broad playful agency expectation",
        weights={"novelty_play": 0.5, "agency": 0.5},
        rationale="Old factor_05 expectation used for comparison only.",
    ),
    CandidateSpec(
        candidate_id="f05_novelty_play_core",
        parent_factor="suica_factor_05",
        label="novelty-play core",
        weights={"novelty_play": 1.0},
        rationale="Repair hypothesis: factor_05 is narrower than agency and mainly captures playful exploratory engagement.",
    ),
    CandidateSpec(
        candidate_id="f05_play_minus_social_norm",
        parent_factor="suica_factor_05",
        label="playful exploration minus social-norm evaluation",
        weights={"novelty_play": 1.0, "social_evaluation": -0.35, "communion": -0.25},
        rationale="Tests whether factor_05 is a contrast between exploratory play and norm/communion language.",
    ),
    CandidateSpec(
        candidate_id="f10_original_expected_action_mind",
        parent_factor="suica_factor_10",
        label="original action plus mentalization expectation",
        weights={"directive_interpersonal": 1 / 3, "agency": 1 / 3, "mentalization": 1 / 3},
        rationale="Old factor_10 expectation used for comparison only.",
    ),
    CandidateSpec(
        candidate_id="f10_directive_action_core",
        parent_factor="suica_factor_10",
        label="directive action core",
        weights={"directive_interpersonal": 1.0},
        rationale="Split hypothesis: the strongest readable subfactor is direct advice/action orientation.",
    ),
    CandidateSpec(
        candidate_id="f10_action_growth_channel",
        parent_factor="suica_factor_10",
        label="directive action-growth channel",
        weights={"directive_interpersonal": 0.5, "redemption_growth": 0.25, "communion": 0.25},
        rationale="Tests a higher-order action-help-growth composite while retaining interpersonal warmth.",
    ),
    CandidateSpec(
        candidate_id="f10_growth_communion_residue",
        parent_factor="suica_factor_10",
        label="growth-communion residue",
        weights={"redemption_growth": 0.4, "communion": 0.35, "temporal_integration": 0.25},
        rationale="Tests whether a non-directive growth/communion residue exists after separating action advice.",
    ),
    CandidateSpec(
        candidate_id="f10_agency_mentalization_residue",
        parent_factor="suica_factor_10",
        label="agency-mentalization residue",
        weights={"agency": 0.5, "mentalization": 0.5},
        rationale="Explicitly tests the weak original residual claim.",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate SUICA weak-factor repair candidates v1.")
    parser.add_argument("--eval-dir", default=str(EVAL_DIR))
    parser.add_argument("--weak-dir", default=str(WEAK_DIR))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--d-threshold", type=float, default=0.5)
    parser.add_argument("--source-beta-threshold", type=float, default=0.3)
    parser.add_argument("--agreement-threshold", type=float, default=0.5)
    return parser.parse_args()


def load_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    norm = sum(abs(value) for value in weights.values())
    if norm == 0:
        raise ValueError("candidate weights cannot sum to zero")
    return {key: value / norm for key, value in weights.items()}


def composite_score(frame: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """Compute a signed dimension composite from 0-3 coder ratings."""

    normalized = normalize_weights(weights)
    score = pd.Series(0.0, index=frame.index)
    for dimension, weight in normalized.items():
        col = f"{dimension}_0_to_3"
        if col not in frame.columns:
            raise KeyError(col)
        score = score + pd.to_numeric(frame[col], errors="coerce").fillna(0.0) * weight
    return score


def cohen_d(high: pd.Series, low: pd.Series) -> float:
    """Cohen's d for high-minus-low separation with safe zero-variance handling."""

    high = pd.to_numeric(high, errors="coerce").dropna()
    low = pd.to_numeric(low, errors="coerce").dropna()
    if high.empty or low.empty:
        return float("nan")
    n_high = len(high)
    n_low = len(low)
    var_high = high.var(ddof=1) if n_high > 1 else 0.0
    var_low = low.var(ddof=1) if n_low > 1 else 0.0
    denom = ((n_high - 1) * var_high + (n_low - 1) * var_low) / max(1, n_high + n_low - 2)
    pooled = float(np.sqrt(max(0.0, denom)))
    diff = float(high.mean() - low.mean())
    if pooled == 0:
        if diff == 0:
            return 0.0
        return float(np.sign(diff) * np.inf)
    return diff / pooled


def pearson_r(left: pd.Series, right: pd.Series) -> float:
    left = pd.to_numeric(left, errors="coerce")
    right = pd.to_numeric(right, errors="coerce")
    mask = left.notna() & right.notna()
    if int(mask.sum()) < 3 or left[mask].nunique() < 2 or right[mask].nunique() < 2:
        return float("nan")
    return float(np.corrcoef(left[mask], right[mask])[0, 1])


def score_candidate_rows(coded: pd.DataFrame, candidates: list[CandidateSpec]) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for spec in candidates:
        subset = coded.loc[coded["factor"].eq(spec.parent_factor)].copy()
        if subset.empty:
            continue
        subset["candidate_id"] = spec.candidate_id
        subset["candidate_label"] = spec.label
        subset["candidate_score"] = composite_score(subset, spec.weights)
        subset["candidate_rationale"] = spec.rationale
        rows.append(subset)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def source_adjusted_effect(group: pd.DataFrame) -> float:
    """Average high-minus-low within source families to avoid source imbalance."""

    deltas: list[float] = []
    for _source, source_rows in group.groupby("source_family", sort=True):
        high = source_rows.loc[source_rows["pole"].eq("high"), "candidate_score"]
        low = source_rows.loc[source_rows["pole"].eq("low"), "candidate_score"]
        if high.empty or low.empty:
            continue
        deltas.append(float(high.mean() - low.mean()))
    if not deltas:
        return float("nan")
    return float(np.mean(deltas))


def candidate_coder_metrics(scored: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for (candidate_id, coder_id), group in scored.groupby(["candidate_id", "coder_id"], sort=True):
        high = group.loc[group["pole"].eq("high"), "candidate_score"]
        low = group.loc[group["pole"].eq("low"), "candidate_score"]
        rows.append(
            {
                "candidate_id": candidate_id,
                "parent_factor": group["factor"].iloc[0],
                "candidate_label": group["candidate_label"].iloc[0],
                "coder_id": coder_id,
                "high_n": int(high.notna().sum()),
                "low_n": int(low.notna().sum()),
                "high_mean": float(high.mean()),
                "low_mean": float(low.mean()),
                "high_minus_low": float(high.mean() - low.mean()),
                "cohen_d": cohen_d(high, low),
                "source_adjusted_beta": source_adjusted_effect(group),
            }
        )
    return pd.DataFrame(rows)


def candidate_source_metrics(scored: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for (candidate_id, coder_id, source_family), group in scored.groupby(["candidate_id", "coder_id", "source_family"], sort=True):
        high = group.loc[group["pole"].eq("high"), "candidate_score"]
        low = group.loc[group["pole"].eq("low"), "candidate_score"]
        if high.empty or low.empty:
            continue
        rows.append(
            {
                "candidate_id": candidate_id,
                "parent_factor": group["factor"].iloc[0],
                "candidate_label": group["candidate_label"].iloc[0],
                "coder_id": coder_id,
                "source_family": source_family,
                "high_n": int(high.notna().sum()),
                "low_n": int(low.notna().sum()),
                "high_mean": float(high.mean()),
                "low_mean": float(low.mean()),
                "high_minus_low": float(high.mean() - low.mean()),
                "cohen_d": cohen_d(high, low),
            }
        )
    return pd.DataFrame(rows)


def candidate_agreement(scored: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for candidate_id, group in scored.groupby("candidate_id", sort=True):
        pivot = group.pivot_table(index="blind_item_id", columns="coder_id", values="candidate_score", aggfunc="mean")
        coders = list(pivot.columns)
        if len(coders) < 2:
            r = float("nan")
            mean_abs_diff = float("nan")
        else:
            r = pearson_r(pivot[coders[0]], pivot[coders[1]])
            mean_abs_diff = float((pivot[coders[0]] - pivot[coders[1]]).abs().mean())
        rows.append(
            {
                "candidate_id": candidate_id,
                "parent_factor": group["factor"].iloc[0],
                "candidate_label": group["candidate_label"].iloc[0],
                "coder_pair_count": max(0, len(coders) - 1),
                "inter_coder_pearson": r,
                "mean_abs_coder_diff": mean_abs_diff,
                "n_blind_items": int(pivot.shape[0]),
            }
        )
    return pd.DataFrame(rows)


def signature_vectors(pole: pd.DataFrame) -> pd.DataFrame:
    """Average factor signatures across coders in the 11-dimensional coding space."""

    return (
        pole.pivot_table(index="factor", columns="dimension", values="cohen_d", aggfunc="mean")
        .reindex(columns=DIMENSIONS)
        .fillna(0.0)
    )


def cosine(left: np.ndarray, right: np.ndarray) -> float:
    denom = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denom == 0:
        return float("nan")
    return float(np.dot(left, right) / denom)


def candidate_overlap(candidates: list[CandidateSpec], pole: pd.DataFrame, reference_factor: str = "suica_factor_06") -> pd.DataFrame:
    signatures = signature_vectors(pole)
    if reference_factor not in signatures.index:
        return pd.DataFrame()
    ref = signatures.loc[reference_factor].to_numpy(float)
    rows: list[dict] = []
    for spec in candidates:
        weights = normalize_weights(spec.weights)
        candidate_vec = np.array([weights.get(dim, 0.0) for dim in DIMENSIONS], dtype=float)
        parent_vec = signatures.loc[spec.parent_factor].to_numpy(float) if spec.parent_factor in signatures.index else np.zeros(len(DIMENSIONS))
        rows.append(
            {
                "candidate_id": spec.candidate_id,
                "parent_factor": spec.parent_factor,
                "candidate_label": spec.label,
                "reference_factor": reference_factor,
                "candidate_weight_cosine_to_reference": cosine(candidate_vec, ref),
                "parent_signature_cosine_to_reference": cosine(parent_vec, ref),
            }
        )
    return pd.DataFrame(rows)


def candidate_component_diagnostics(
    candidates: list[CandidateSpec],
    pole: pd.DataFrame,
    source_adjusted: pd.DataFrame,
    *,
    d_threshold: float,
    source_beta_threshold: float,
) -> pd.DataFrame:
    """Check whether each named candidate component is independently supported.

    This catches composite masking: a broad score can separate high/low items
    because one component is strong while another claimed component is weak.
    """

    beta = source_adjusted.rename(columns={"high_minus_low_source_adjusted": "source_adjusted_beta"})
    rows: list[dict] = []
    for spec in candidates:
        for dimension, raw_weight in normalize_weights(spec.weights).items():
            direction = float(np.sign(raw_weight))
            p = pole.loc[(pole["factor"].eq(spec.parent_factor)) & (pole["dimension"].eq(dimension))].copy()
            s = beta.loc[(beta["factor"].eq(spec.parent_factor)) & (beta["dimension"].eq(dimension))].copy()
            if p.empty:
                continue
            aligned_d = pd.to_numeric(p["cohen_d"], errors="coerce") * direction
            aligned_beta = pd.to_numeric(s["source_adjusted_beta"], errors="coerce") * direction if not s.empty else pd.Series(dtype=float)
            d_support = int((aligned_d >= d_threshold).sum())
            beta_support = int((aligned_beta >= source_beta_threshold).sum()) if not aligned_beta.empty else 0
            component_supported = d_support == p["coder_id"].nunique() and beta_support == p["coder_id"].nunique()
            rows.append(
                {
                    "candidate_id": spec.candidate_id,
                    "parent_factor": spec.parent_factor,
                    "candidate_label": spec.label,
                    "dimension": dimension,
                    "weight": raw_weight,
                    "expected_direction": "positive_high_minus_low" if raw_weight > 0 else "negative_high_minus_low",
                    "mean_aligned_cohen_d": float(aligned_d.mean()),
                    "min_aligned_cohen_d": float(aligned_d.min()),
                    "mean_aligned_source_beta": float(aligned_beta.mean()) if not aligned_beta.empty else float("nan"),
                    "min_aligned_source_beta": float(aligned_beta.min()) if not aligned_beta.empty else float("nan"),
                    "aligned_d_support_coder_count": d_support,
                    "aligned_source_support_coder_count": beta_support,
                    "component_supported": bool(component_supported),
                }
            )
    return pd.DataFrame(rows)


def summarize_candidates(
    coder_metrics: pd.DataFrame,
    agreement: pd.DataFrame,
    overlap: pd.DataFrame,
    component_diagnostics: pd.DataFrame,
    *,
    d_threshold: float,
    source_beta_threshold: float,
    agreement_threshold: float,
) -> pd.DataFrame:
    rows: list[dict] = []
    for candidate_id, group in coder_metrics.groupby("candidate_id", sort=True):
        row = {
            "candidate_id": candidate_id,
            "parent_factor": group["parent_factor"].iloc[0],
            "candidate_label": group["candidate_label"].iloc[0],
            "mean_high_minus_low": float(group["high_minus_low"].mean()),
            "mean_cohen_d": float(group["cohen_d"].replace([np.inf, -np.inf], np.nan).mean()),
            "min_abs_cohen_d": float(group["cohen_d"].replace([np.inf, -np.inf], np.nan).abs().min()),
            "mean_source_adjusted_beta": float(group["source_adjusted_beta"].mean()),
            "min_abs_source_adjusted_beta": float(group["source_adjusted_beta"].abs().min()),
            "coder_count": int(group["coder_id"].nunique()),
        }
        agr = agreement.loc[agreement["candidate_id"].eq(candidate_id)].head(1)
        if not agr.empty:
            row.update(
                {
                    "inter_coder_pearson": float(agr["inter_coder_pearson"].iloc[0]),
                    "mean_abs_coder_diff": float(agr["mean_abs_coder_diff"].iloc[0]),
                    "n_blind_items": int(agr["n_blind_items"].iloc[0]),
                }
            )
        ov = overlap.loc[overlap["candidate_id"].eq(candidate_id)].head(1)
        if not ov.empty:
            row.update(
                {
                    "candidate_weight_cosine_to_factor_06": float(ov["candidate_weight_cosine_to_reference"].iloc[0]),
                    "parent_signature_cosine_to_factor_06": float(ov["parent_signature_cosine_to_reference"].iloc[0]),
                }
            )
        components = component_diagnostics.loc[component_diagnostics["candidate_id"].eq(candidate_id)].copy()
        if components.empty:
            coverage_ratio = float("nan")
            unsupported = ""
        else:
            coverage_ratio = float(components["component_supported"].mean())
            unsupported = "; ".join(components.loc[~components["component_supported"], "dimension"].tolist())
        row["component_coverage_ratio"] = coverage_ratio
        row["unsupported_components"] = unsupported
        d_pass = row["min_abs_cohen_d"] >= d_threshold
        beta_pass = row["min_abs_source_adjusted_beta"] >= source_beta_threshold
        agreement_pass = row.get("inter_coder_pearson", float("nan")) >= agreement_threshold
        component_pass = bool(coverage_ratio == 1.0)
        if d_pass and beta_pass and agreement_pass and component_pass:
            decision = "repair_candidate_promote_for_new_blind_batch"
        elif d_pass and beta_pass and agreement_pass:
            decision = "composite_support_but_component_masking"
        elif d_pass and beta_pass:
            decision = "metric_support_but_coder_agreement_watch"
        elif d_pass or beta_pass:
            decision = "partial_support_needs_item_bank_repair"
        else:
            decision = "hold_or_drop_candidate"
        row["d_gate"] = bool(d_pass)
        row["source_adjusted_gate"] = bool(beta_pass)
        row["agreement_gate"] = bool(agreement_pass)
        row["component_coverage_gate"] = bool(component_pass)
        row["repair_rescoring_decision"] = decision
        rows.append(row)
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(
        ["parent_factor", "repair_rescoring_decision", "min_abs_cohen_d", "min_abs_source_adjusted_beta", "inter_coder_pearson"],
        ascending=[True, True, False, False, False],
    )


def item_recommendations(scored: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    grouped = (
        scored.groupby(["candidate_id", "blind_item_id"], sort=True)
        .agg(
            parent_factor=("factor", "first"),
            candidate_label=("candidate_label", "first"),
            pole=("pole", "first"),
            source_family=("source_family", "first"),
            scenario=("scenario", "first"),
            factor_score=("factor_score", "first"),
            candidate_score_mean=("candidate_score", "mean"),
            candidate_score_std=("candidate_score", "std"),
            excerpt=("text_excerpt", "first"),
        )
        .reset_index()
    )
    for candidate_id, group in grouped.groupby("candidate_id", sort=True):
        q25 = float(group["candidate_score_mean"].quantile(0.25))
        q75 = float(group["candidate_score_mean"].quantile(0.75))
        for row in group.itertuples(index=False):
            if row.pole == "high" and row.candidate_score_mean >= q75:
                role = "retain_high_anchor"
            elif row.pole == "low" and row.candidate_score_mean <= q25:
                role = "retain_low_anchor"
            elif row.pole == "high" and row.candidate_score_mean <= q25:
                role = "high_pole_misfit_or_residual"
            elif row.pole == "low" and row.candidate_score_mean >= q75:
                role = "low_pole_misfit_or_residual"
            else:
                role = "middle_or_secondary_item"
            excerpt = str(row.excerpt).replace("\n", " ")
            if len(excerpt) > 220:
                excerpt = excerpt[:219].rstrip() + "..."
            rows.append(
                {
                    "candidate_id": candidate_id,
                    "parent_factor": row.parent_factor,
                    "candidate_label": row.candidate_label,
                    "blind_item_id": row.blind_item_id,
                    "pole": row.pole,
                    "source_family": row.source_family,
                    "scenario": row.scenario,
                    "factor_score": float(row.factor_score),
                    "candidate_score_mean": float(row.candidate_score_mean),
                    "candidate_score_std": float(row.candidate_score_std) if pd.notna(row.candidate_score_std) else 0.0,
                    "item_repair_role": role,
                    "excerpt": excerpt,
                }
            )
    return pd.DataFrame(rows).sort_values(["candidate_id", "item_repair_role", "candidate_score_mean"], ascending=[True, True, False])


def write_report(
    path: Path,
    summary: pd.DataFrame,
    coder_metrics: pd.DataFrame,
    component_diagnostics: pd.DataFrame,
    item_roles: pd.DataFrame,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    promoted = summary.loc[summary["repair_rescoring_decision"].eq("repair_candidate_promote_for_new_blind_batch")]
    partial = summary.loc[~summary["repair_rescoring_decision"].eq("repair_candidate_promote_for_new_blind_batch")]
    retain = item_roles.loc[item_roles["item_repair_role"].isin(["retain_high_anchor", "retain_low_anchor"])].copy()
    lines = [
        "# SUICA Repair Candidate Re-scoring v1",
        "",
        "## Purpose",
        "",
        "Re-score `factor_05` and `factor_10` repair hypotheses using the existing two-coder blind ratings, without new LLM calls.",
        "",
        "## Candidate Summary",
        "",
        summary.round(3).to_markdown(index=False) if not summary.empty else "No candidate summary.",
        "",
        "## Promoted Candidates",
        "",
        promoted.round(3).to_markdown(index=False) if not promoted.empty else "No candidate passes all repair re-scoring gates.",
        "",
        "## Remaining Partial/Hold Candidates",
        "",
        partial.round(3).to_markdown(index=False) if not partial.empty else "No partial candidates.",
        "",
        "## Coder-Level Metrics",
        "",
        coder_metrics.round(3).to_markdown(index=False) if not coder_metrics.empty else "No coder metrics.",
        "",
        "## Component Coverage Diagnostics",
        "",
        component_diagnostics.round(3).to_markdown(index=False) if not component_diagnostics.empty else "No component diagnostics.",
        "",
        "## Candidate Item Anchors",
        "",
        retain.head(40).round(3).to_markdown(index=False) if not retain.empty else "No retained item anchors.",
        "",
        "## Interpretation",
        "",
        "- A broad composite is not enough for construct promotion: every named component must independently support the high/low direction.",
        "- `factor_05` should be treated as a narrow novelty/play construct if the novelty-only candidate passes while play-agency shows component masking.",
        "- `factor_10` should be split if directive/action candidates pass while agency/mentalization residue remains weaker or masked.",
        "- Any candidate promoted here still needs a new source-balanced blind batch before release as a SUICA scale dimension.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    eval_dir = Path(args.eval_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    coded = load_csv(eval_dir / "merged_coder_key_ratings.csv")
    pole = load_csv(eval_dir / "pole_separation_by_factor_dimension.csv")

    scored = score_candidate_rows(coded, CANDIDATES)
    coder_metrics = candidate_coder_metrics(scored)
    source_metrics = candidate_source_metrics(scored)
    agreement = candidate_agreement(scored)
    overlap = candidate_overlap(CANDIDATES, pole, reference_factor="suica_factor_06")
    source_adjusted = load_csv(eval_dir / "source_adjusted_pole_effects.csv")
    component_diagnostics = candidate_component_diagnostics(
        CANDIDATES,
        pole,
        source_adjusted,
        d_threshold=args.d_threshold,
        source_beta_threshold=args.source_beta_threshold,
    )
    summary = summarize_candidates(
        coder_metrics,
        agreement,
        overlap,
        component_diagnostics,
        d_threshold=args.d_threshold,
        source_beta_threshold=args.source_beta_threshold,
        agreement_threshold=args.agreement_threshold,
    )
    item_roles = item_recommendations(scored)

    summary.to_csv(out_dir / "repair_candidate_summary.csv", index=False)
    coder_metrics.to_csv(out_dir / "repair_candidate_coder_metrics.csv", index=False)
    source_metrics.to_csv(out_dir / "repair_candidate_source_metrics.csv", index=False)
    agreement.to_csv(out_dir / "repair_candidate_coder_agreement.csv", index=False)
    overlap.to_csv(out_dir / "repair_candidate_factor06_overlap.csv", index=False)
    component_diagnostics.to_csv(out_dir / "repair_candidate_component_diagnostics.csv", index=False)
    item_roles.to_csv(out_dir / "repair_candidate_item_roles.csv", index=False)
    (out_dir / "run_config.json").write_text(
        json.dumps(
            {
                "eval_dir": str(eval_dir),
                "output_dir": str(out_dir),
                "d_threshold": args.d_threshold,
                "source_beta_threshold": args.source_beta_threshold,
                "agreement_threshold": args.agreement_threshold,
                "candidates": [
                    {
                        "candidate_id": spec.candidate_id,
                        "parent_factor": spec.parent_factor,
                        "label": spec.label,
                        "weights": spec.weights,
                        "rationale": spec.rationale,
                    }
                    for spec in CANDIDATES
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(Path(args.report_path), summary, coder_metrics, component_diagnostics, item_roles)
    print("SUICA repair candidate re-scoring complete.")
    print(summary.to_string(index=False))
    print(f"\nReport: {Path(args.report_path)}")


if __name__ == "__main__":
    main()
