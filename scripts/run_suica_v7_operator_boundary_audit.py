#!/usr/bin/env python3
"""Audit SUICA V7.1 slice boundaries with source-level technical controls.

This runner intentionally reads only raw text/provenance columns.  It does not
load Big Five, MBTI, clinical labels, or any other external criterion.  It
tests whether an apparent fixed-slice precision advantage survives exact source
provenance, source-disjoint views, phase perturbations, and source-cluster
bootstrap uncertainty.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v7_operator_smoke import (  # noqa: E402
    DEFAULT_INPUT,
    _infer_column,
    _load_config,
    _read_table,
    _schema_report,
    _write_json,
)
from suica_core.v7_observations import (  # noqa: E402
    ObservationSpec,
    build_observations,
    canonicalize_comments,
    observation_manifest,
    prepare_source_panel,
    select_reference_authors,
)
from suica_core.v7_operator_controls import (  # noqa: E402
    bootstrap_mean_ci,
    correspondence_permutation_test,
    operator_provenance_qc,
    score_operator_from_comments,
    source_cluster_bootstrap_z_sem,
    source_disjoint_score_consistency,
)
from suica_core.v7_psychometric import (  # noqa: E402
    RepresentationSpec,
    author_features_from_embeddings,
    bundle_sha256,
    fit_factor_bundle,
    fit_representation,
    read_factor_bundle,
    score_author_features,
)


DEFAULT_CONFIG = ROOT / "configs" / "v7_operator_boundary_audit.json"


def parse_args() -> argparse.Namespace:
    """Parse a local, label-free V7.1 boundary-audit request."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--quick", action="store_true", help="Run a bounded engineering smoke audit.")
    parser.add_argument("--reuse-cohort", action="store_true", help="Explicitly mark the selected cohort as engineering-only.")
    parser.add_argument("--max-users", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--user-col", default=None)
    parser.add_argument("--text-col", default=None)
    parser.add_argument("--order-col", default=None)
    parser.add_argument("--condition-col", default=None)
    return parser.parse_args()


def _operator_specs(config: dict[str, Any]) -> list[ObservationSpec]:
    """Build declared operator specs while enforcing the common source panel."""
    defaults = {
        "min_tokens": int(config["min_tokens_per_unit"]),
        "max_units_per_user": int(config["max_units_per_user"]),
        "max_source_comments_per_user": int(config["max_source_comments_per_user"]),
        "max_source_tokens_per_user": int(config["max_source_tokens_per_user"]),
    }
    return [ObservationSpec(**{**defaults, **raw}) for raw in config["operators"]]


def _factor_raw_columns(scores: pd.DataFrame) -> list[str]:
    return [
        column
        for column in scores.columns
        if column.startswith("SU7-FC-") and column.endswith("@v1")
    ]


def _long_precision(
    scores: pd.DataFrame,
    bootstrap: pd.DataFrame,
    *,
    operator: str,
) -> pd.DataFrame:
    """Join normalized bootstrap error to confirmation score spread."""
    confirmation = scores.loc[
        scores["split"].eq("confirmation") & scores["score_status"].eq("SCORED")
    ].copy()
    rows: list[dict[str, Any]] = []
    for factor in _factor_raw_columns(scores):
        z_column = f"{factor}_z"
        values = confirmation[z_column].to_numpy(float)
        between_sd = float(np.std(values[np.isfinite(values)], ddof=1)) if np.isfinite(values).sum() >= 2 else float("nan")
        sem = bootstrap.loc[bootstrap["factor"].eq(factor), ["user_id", "bootstrap_z_sem", "sem_status"]]
        for row in sem.itertuples(index=False):
            sem_value = float(row.bootstrap_z_sem)
            ratio = float("nan")
            if np.isfinite(sem_value) and np.isfinite(between_sd) and between_sd > 1e-12:
                ratio = float((sem_value**2) / (between_sd**2))
            rows.append({
                "operator": operator,
                "user_id": str(row.user_id),
                "factor": factor,
                "bootstrap_z_sem": sem_value,
                "between_author_z_sd": between_sd,
                "error_to_between_variance_ratio": ratio,
                "sem_status": str(row.sem_status),
            })
    return pd.DataFrame(rows)


def _precision_comparisons(precision: pd.DataFrame, *, seed: int, repetitions: int) -> pd.DataFrame:
    """Compare aggregate z-scale source-sampling precision to native comments.

    Factor axes are independently rotated per operator, so this compares each
    author's mean normalized uncertainty across anonymous coordinates rather
    than treating Factor 1 from different operators as the same construct.
    """
    if precision.empty or "native" not in set(precision["operator"]):
        return pd.DataFrame()
    summary = precision.groupby(["operator", "user_id"], observed=True)["bootstrap_z_sem"].mean().reset_index()
    native = summary.loc[summary["operator"].eq("native"), ["user_id", "bootstrap_z_sem"]].rename(
        columns={"bootstrap_z_sem": "native_mean_z_sem"}
    )
    rows: list[dict[str, Any]] = []
    for operator in sorted(set(summary["operator"])):
        if operator == "native":
            continue
        candidate = summary.loc[summary["operator"].eq(operator), ["user_id", "bootstrap_z_sem"]].rename(
            columns={"bootstrap_z_sem": "operator_mean_z_sem"}
        )
        merged = native.merge(candidate, on="user_id", how="inner")
        delta = merged["native_mean_z_sem"].to_numpy(float) - merged["operator_mean_z_sem"].to_numpy(float)
        stats = bootstrap_mean_ci(delta, seed=seed + len(rows), repetitions=repetitions)
        rows.append({
            "operator": operator,
            "comparison": "native_mean_z_sem_minus_operator",
            "delta_mean": stats["mean"],
            "delta_ci_low": stats["ci_low"],
            "delta_ci_high": stats["ci_high"],
            "n_paired_authors": int(stats["n"]),
            "interpretation": "positive means lower aggregate calibration-z sampling SEM than native",
        })
    return pd.DataFrame(rows)


def _boundary_verdict(comparisons: pd.DataFrame, disjoint: pd.DataFrame, permutations: pd.DataFrame) -> dict[str, Any]:
    """Apply the predeclared boundary-control rule without reading labels."""
    required = [
        "fixed_128_within_comment",
        "fixed_128_boundary_marker",
        "fixed_128_offset64",
        "fixed_128_hash_offset",
    ]
    evidence: list[dict[str, Any]] = []
    missing = False
    all_positive = True
    for operator in required:
        comparison = comparisons.loc[comparisons["operator"].eq(operator)] if not comparisons.empty else pd.DataFrame()
        disjoint_operator = disjoint.loc[disjoint["operator"].eq(operator)] if not disjoint.empty else pd.DataFrame()
        permutation_operator = permutations.loc[permutations["operator"].eq(operator)] if not permutations.empty else pd.DataFrame()
        if comparison.empty or disjoint_operator.empty or permutation_operator.empty:
            missing = True
            evidence.append({"operator": operator, "status": "missing"})
            continue
        ci_low = float(comparison["delta_ci_low"].iloc[0])
        mean_disjoint = float(disjoint_operator["correlation"].mean())
        mean_p = float(permutation_operator["empirical_p_two_sided"].mean())
        positive = bool(np.isfinite(ci_low) and ci_low > 0 and np.isfinite(mean_disjoint) and mean_disjoint > 0)
        all_positive = all_positive and positive
        evidence.append({
            "operator": operator,
            "delta_ci_low": ci_low,
            "mean_source_disjoint_correlation": mean_disjoint,
            "mean_permutation_p": mean_p,
            "status": "supports_precision" if positive else "does_not_support_precision",
        })
    if missing:
        verdict = "INCONCLUSIVE"
        explanation = "At least one required source-boundary control lacked scoreable evidence."
    elif all_positive:
        verdict = "ROBUST_FIXED_PRECISION_ADVANTAGE"
        explanation = "All required no-cross, marker, and offset controls retained positive precision deltas."
    else:
        verdict = "FIXED_ADVANTAGE_NOT_ROBUST"
        explanation = "The observed fixed-window precision pattern did not survive every required boundary control."
    return {
        "verdict": verdict,
        "explanation": explanation,
        "required_controls": required,
        "evidence": evidence,
        "claim_boundary": "Engineering audit on a reused cohort; not a psychological or fresh-confirmation result.",
    }


def _write_report(
    path: Path,
    *,
    config: dict[str, Any],
    output_dir: Path,
    summary: pd.DataFrame,
    comparisons: pd.DataFrame,
    verdict: dict[str, Any],
) -> None:
    """Write a compact audit narrative with explicit measurement boundaries."""
    summary_table = summary.to_markdown(index=False, floatfmt=".3f") if not summary.empty else "No operator completed."
    comparison_table = comparisons.to_markdown(index=False, floatfmt=".3f") if not comparisons.empty else "No native comparison available."
    controls = "\n".join(
        f"- `{row['operator']}`: `{row['status']}`"
        for row in verdict.get("evidence", [])
    ) or "- No required control evidence."
    text = f"""# SUICA V7.1 Operator Boundary Audit

## Scope

This is a label-free engineering audit on the reused V7 reference cohort. It
does not read Big Five, MBTI, clinical labels, or other external criteria. It
does not identify a personality factor. It asks only whether fixed slicing has
a technically robust source-text sampling precision advantage after provenance
corrections.

All operators used the same capped source-comment panel and source-token budget
with one discovery-fitted TF-IDF/SVD representation. Factor bundles were fit
without confirmation authors and were scored with frozen calibration norms.

## Verdict

- Result: **{verdict['verdict']}**
- Reason: {verdict['explanation']}

### Required Controls

{controls}

## Operator Summary

{summary_table}

## Precision vs Native

`delta_mean = native mean calibration-z SEM - operator mean calibration-z SEM`.
A positive value indicates lower aggregate source-sampling uncertainty, but it
does not equate factor axes across separately fitted operators.

{comparison_table}

## Interpretation Boundary

- Source-cluster bootstrap SEM estimates finite observed-text sampling error.
- Source-disjoint correlations are technical within-corpus agreement, not
  cross-day or psychological trait reliability.
- Factor IDs are anonymous operational coordinates. Their rotations are not
  treated as aligned between operators.
- Any result here is an engineering result on a reused cohort. E1 must use a
  fresh author cohort or be labelled exploratory.

## Artifacts

- Config and cohort manifest: `{output_dir / 'run_manifest.json'}`
- Boundary decision: `{output_dir / 'boundary_audit.json'}`
- Normalized precision: `{output_dir / 'normalized_precision.csv'}`
- Source-disjoint agreement: `{output_dir / 'source_disjoint_consistency.csv'}`
- Provenance QC: `{output_dir / 'provenance_qc.csv'}`
- Operator bundles: `{output_dir / 'operator_bundles'}`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    """Execute the V7.1 E0 boundary audit."""
    args = parse_args()
    config = _load_config(args.config)
    if args.seed is not None:
        config["seed"] = int(args.seed)
    if args.max_users is not None:
        config["max_users"] = int(args.max_users)
    if args.quick:
        # A three-way author split needs at least 12 authors in each fit/norm/
        # confirmation arm. The deterministic cohort allocation makes 60 too
        # small for that guarantee on the current Tier-U source.
        config["max_users"] = min(int(config["max_users"]), 90)
        config["max_source_comments_per_user"] = min(int(config["max_source_comments_per_user"]), 16)
        config["max_source_tokens_per_user"] = min(int(config["max_source_tokens_per_user"]), 2048)
        config["max_units_per_user"] = min(int(config["max_units_per_user"]), 64)
        config["source_bootstrap_repetitions"] = min(int(config["source_bootstrap_repetitions"]), 4)
        config["source_disjoint_repetitions"] = min(int(config["source_disjoint_repetitions"]), 3)
        config["permutation_repetitions"] = min(int(config["permutation_repetitions"]), 50)
        config["metric_bootstrap_repetitions"] = min(int(config["metric_bootstrap_repetitions"]), 80)
        config["representation"]["max_features"] = min(int(config["representation"]["max_features"]), 2000)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_dir = args.output_dir or ROOT / "results" / "v7_operator_boundary_audit" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.report or ROOT / "reports" / "V7_OPERATOR_BOUNDARY_AUDIT.md"

    raw = _read_table(args.input)
    columns = [str(column) for column in raw.columns]
    column_map = {
        "user": _infer_column(columns, ["author", "user_id", "participant_id", "user", "id"], args.user_col, required=True),
        "text": _infer_column(columns, ["body", "text", "comment", "content", "message"], args.text_col, required=True),
        "order": _infer_column(columns, ["created_utc", "timestamp", "time", "date", "created_at"], args.order_col, required=False),
        "condition": _infer_column(columns, ["subreddit", "condition", "platform", "task", "forum"], args.condition_col, required=False),
    }
    canonical = canonicalize_comments(
        raw,
        user_col=str(column_map["user"]),
        text_col=str(column_map["text"]),
        order_col=column_map["order"],
        condition_col=column_map["condition"],
        min_tokens=int(config["min_tokens_per_unit"]),
        mask_personality_terms=bool(config["mask_personality_terms"]),
    )
    selected = select_reference_authors(
        canonical,
        min_comments_per_user=int(config["min_comments_per_user"]),
        max_users=int(config["max_users"]),
        seed=int(config["seed"]),
    )
    specs = _operator_specs(config)
    panel_spec = specs[0]
    source_panel = prepare_source_panel(selected, panel_spec)
    split_counts = source_panel.groupby("split", observed=True)["user_id"].nunique().to_dict()
    if any(int(split_counts.get(name, 0)) < 12 for name in ("discovery", "calibration", "confirmation")):
        raise RuntimeError(f"Reference cohort cannot support V7.1 3-way author split: {split_counts}")
    schema_path = output_dir / "data_schema.md"
    _schema_report(
        schema_path,
        source=args.input,
        raw=raw,
        column_map=column_map,
        canonical=canonical,
        selected=source_panel,
        mask_personality_terms=bool(config["mask_personality_terms"]),
        min_comments_per_user=int(config["min_comments_per_user"]),
        max_comments_per_user=int(config["max_source_comments_per_user"]),
    )
    _write_json(output_dir / "run_manifest.json", {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "config": config,
        "input": str(args.input),
        "column_map": column_map,
        "author_split_counts": {key: int(value) for key, value in split_counts.items()},
        "cohort_status": "ENGINEERING_AUDIT_REUSED_COHORT" if args.reuse_cohort else "ENGINEERING_AUDIT_COHORT",
        "claim_boundary": "No external labels were loaded or used. This is not fresh confirmation evidence.",
    })

    representation_spec = RepresentationSpec(
        max_features=int(config["representation"]["max_features"]),
        ngram_min=int(config["representation"]["ngram_range"][0]),
        ngram_max=int(config["representation"]["ngram_range"][1]),
        svd_dimensions=int(config["representation"]["svd_dimensions"]),
        factor_count=int(config["representation"]["factor_count"]),
        seed=int(config["seed"]),
    )
    discovery_source = source_panel.loc[source_panel["split"].eq("discovery")].reset_index(drop=True)
    representation = fit_representation(discovery_source, representation_spec)
    runtime_path = output_dir / "artifacts" / "common_source_comment_representation.joblib"
    runtime_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(representation, runtime_path)
    runtime_hash = bundle_sha256(runtime_path)
    representation = joblib.load(runtime_path)

    precision_frames: list[pd.DataFrame] = []
    disjoint_frames: list[pd.DataFrame] = []
    permutation_frames: list[pd.DataFrame] = []
    qc_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    bundle_dir = output_dir / "operator_bundles"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    for index, spec in enumerate(specs):
        units = build_observations(source_panel, spec).reset_index(drop=True)
        if units.empty:
            raise RuntimeError(f"Operator produced no units: {spec.name}")
        _write_json(output_dir / f"observation_manifest_{spec.name}.json", observation_manifest(source_panel, units, spec))
        embeddings = representation.transform(units["text"])
        features = author_features_from_embeddings(units, embeddings)
        bundle_path = bundle_dir / f"{spec.name}_factor_bundle.json"
        fitted = fit_factor_bundle(
            features,
            operator=spec.to_dict(),
            representation=representation_spec,
            runtime_artifact={
                "representation_path": str(runtime_path.relative_to(output_dir)),
                "representation_sha256": runtime_hash,
                "representation_fit_source": "discovery source comments, common across E0 operators",
            },
            min_units_for_score=1 if spec.kind == "whole" else 2,
            seed=int(config["seed"]),
            version=str(config["version"]),
        )
        fitted.bundle.write_json(bundle_path)
        bundle = read_factor_bundle(bundle_path)
        scores = score_author_features(bundle, features)
        replay_units, replay_features, replay_scores = score_operator_from_comments(
            source_panel, spec=spec, representation=representation, bundle=bundle
        )
        factor_columns = _factor_raw_columns(scores)
        replay_diff = float(np.max(np.abs(
            scores[factor_columns].to_numpy(float) - replay_scores[factor_columns].to_numpy(float)
        )))
        if replay_diff > 1e-10 or len(replay_units) != len(units) or len(replay_features) != len(features):
            raise RuntimeError(f"Frozen operator replay failed for {spec.name}: max_diff={replay_diff}")
        scores.to_csv(output_dir / f"scores_{spec.name}.csv", index=False)
        bootstrap = source_cluster_bootstrap_z_sem(
            source_panel,
            spec=spec,
            representation=representation,
            bundle=bundle,
            repetitions=int(config["source_bootstrap_repetitions"]),
            seed=int(config["seed"]) + index * 10_000,
        )
        precision = _long_precision(scores, bootstrap, operator=spec.name)
        precision_frames.append(precision)
        disjoint = pd.concat([
            source_disjoint_score_consistency(
                source_panel,
                spec=spec,
                representation=representation,
                bundle=bundle,
                seed=int(config["seed"]) + index * 10_000 + replicate,
                replicate=replicate,
            )
            for replicate in range(int(config["source_disjoint_repetitions"]))
        ], ignore_index=True)
        disjoint_frames.append(disjoint)
        permutation = correspondence_permutation_test(
            source_panel,
            spec=spec,
            representation=representation,
            bundle=bundle,
            seed=int(config["seed"]) + index * 10_000 + 9_000,
            repetitions=int(config["permutation_repetitions"]),
        )
        permutation_frames.append(permutation)
        qc = operator_provenance_qc(source_panel, units, spec=spec)
        qc["frozen_replay_max_abs_diff"] = replay_diff
        qc_rows.append(qc)
        confirmation = scores.loc[scores["split"].eq("confirmation")]
        disjoint_mean = float(disjoint["correlation"].mean()) if not disjoint.empty else float("nan")
        summary_rows.append({
            "operator": spec.name,
            "kind": spec.kind,
            "confirmation_authors": int(confirmation["user_id"].nunique()),
            "confirmation_scoreable_coverage": float(confirmation["score_status"].eq("SCORED").mean()),
            "mean_bootstrap_z_sem": float(precision["bootstrap_z_sem"].mean()),
            "mean_error_to_between_variance_ratio": float(precision["error_to_between_variance_ratio"].mean()),
            "mean_source_disjoint_correlation": disjoint_mean,
            "mean_permutation_p": float(permutation["empirical_p_two_sided"].mean()) if not permutation.empty else float("nan"),
            "frozen_replay_max_abs_diff": replay_diff,
            "bundle_path": str(bundle_path.relative_to(output_dir)),
        })

    precision_all = pd.concat(precision_frames, ignore_index=True)
    disjoint_all = pd.concat(disjoint_frames, ignore_index=True)
    permutations_all = pd.concat(permutation_frames, ignore_index=True)
    provenance = pd.DataFrame(qc_rows)
    comparisons = _precision_comparisons(
        precision_all,
        seed=int(config["seed"]),
        repetitions=int(config["metric_bootstrap_repetitions"]),
    )
    verdict = _boundary_verdict(comparisons, disjoint_all, permutations_all)
    summary = pd.DataFrame(summary_rows).merge(provenance, on="operator", how="left", suffixes=("", "_qc"))

    precision_all.to_csv(output_dir / "normalized_precision.csv", index=False)
    disjoint_all.to_csv(output_dir / "source_disjoint_consistency.csv", index=False)
    permutations_all.to_csv(output_dir / "author_correspondence_permutation.csv", index=False)
    provenance.to_csv(output_dir / "provenance_qc.csv", index=False)
    comparisons.to_csv(output_dir / "precision_comparison_vs_native.csv", index=False)
    summary.to_csv(output_dir / "operator_summary.csv", index=False)
    _write_json(output_dir / "boundary_audit.json", verdict)
    _write_report(
        report_path,
        config=config,
        output_dir=output_dir,
        summary=summary,
        comparisons=comparisons,
        verdict=verdict,
    )
    print(json.dumps({
        "output_dir": str(output_dir),
        "report": str(report_path),
        "verdict": verdict["verdict"],
        "operators": summary[["operator", "mean_bootstrap_z_sem"]].to_dict(orient="records"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
