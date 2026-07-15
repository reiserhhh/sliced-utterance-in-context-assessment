#!/usr/bin/env python3
"""Run SUICA V7's first label-free observation-operator bake-off.

The runner consumes only raw/provenance text records.  It does not load Big
Five, MBTI or any other external criterion.  It writes frozen local artifacts
for each operator, then applies them to author-disjoint calibration and
confirmation users without refitting.
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

from suica_core.v7_observations import (  # noqa: E402
    ObservationSpec,
    build_observations,
    canonicalize_comments,
    observation_manifest,
    select_reference_authors,
)
from suica_core.v7_psychometric import (  # noqa: E402
    RepresentationSpec,
    author_features_from_embeddings,
    bundle_sha256,
    combine_nested_author_features,
    confirmation_subspace_similarity,
    fit_factor_bundle,
    fit_representation,
    read_factor_bundle,
    score_author_features,
    technical_view_consistency,
    unit_bootstrap_sem,
)


DEFAULT_INPUT = ROOT / "data_sets" / "prepared" / "suica_tiers_v2" / "tier_u_comments.parquet"
DEFAULT_CONFIG = ROOT / "configs" / "v7_operator_smoke.json"


def parse_args() -> argparse.Namespace:
    """Parse an explicitly local, no-label V7 execution request."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Parquet/CSV raw comment table.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--quick", action="store_true", help="Use a small deterministic reference cohort.")
    parser.add_argument("--max-users", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--user-col", default=None)
    parser.add_argument("--text-col", default=None)
    parser.add_argument("--order-col", default=None)
    parser.add_argument("--condition-col", default=None)
    return parser.parse_args()


def _load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"V7 config not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _read_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Raw V7 input not found: {path}. Supply --input with a local table containing author/user and text columns."
        )
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if path.suffix.lower() in {".csv", ".tsv"}:
        return pd.read_csv(path, sep="\t" if path.suffix.lower() == ".tsv" else ",")
    raise ValueError(f"Unsupported input format: {path.suffix}; use parquet, csv, or tsv.")


def _infer_column(columns: list[str], candidates: list[str], explicit: str | None, *, required: bool) -> str | None:
    if explicit:
        if explicit not in columns:
            raise ValueError(f"Requested column not present: {explicit}; available={columns}")
        return explicit
    lower = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate.lower() in lower:
            return lower[candidate.lower()]
    if required:
        raise ValueError(f"Could not infer a required column from {candidates}; available={columns}")
    return None


def _operator_specs(config: dict[str, Any]) -> list[ObservationSpec]:
    defaults = {
        "min_tokens": int(config["min_tokens_per_unit"]),
        "max_units_per_user": int(config["max_comments_per_user"]),
    }
    specs: list[ObservationSpec] = []
    for raw in config["operators"]:
        merged = {**defaults, **raw}
        if "members" in merged:
            merged["members"] = tuple(merged["members"])
        specs.append(ObservationSpec(**merged))
    return specs


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _schema_report(
    path: Path,
    *,
    source: Path,
    raw: pd.DataFrame,
    column_map: dict[str, str | None],
    canonical: pd.DataFrame,
    selected: pd.DataFrame,
    mask_personality_terms: bool,
    min_comments_per_user: int,
    max_comments_per_user: int,
) -> None:
    rows = [
        "# V7 Raw Data Schema Report",
        "",
        f"- Source: `{source}`",
        f"- Raw rows: `{len(raw):,}`",
        f"- Raw columns: `{', '.join(str(column) for column in raw.columns)}`",
        f"- User column: `{column_map['user']}`",
        f"- Text column: `{column_map['text']}`",
        f"- Ordering column: `{column_map['order'] or '<source row>'}`",
        f"- Condition/provenance column: `{column_map['condition'] or '<unknown>'}`",
        f"- Canonical rows after minimum-text eligibility: `{len(canonical):,}`",
        f"- Eligible reference authors: `{selected['user_id'].nunique():,}`",
        f"- Selected comments: `{len(selected):,}`",
        f"- Reference-cohort eligibility: at least `{min_comments_per_user}` eligible comments per author",
        f"- Operator-level observation cap: at most `{max_comments_per_user}` source comments per author",
        f"- Personality-term occurrence in selected raw comments: `{selected['has_personality_term'].mean():.3%}`",
        f"- Personality-term masking enabled: `{mask_personality_terms}`",
        "",
        "This report records inferred fields only. It does not export raw text or user content.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def _summary_row(
    *,
    spec: ObservationSpec,
    features: pd.DataFrame,
    scores: pd.DataFrame,
    sem: pd.DataFrame | None,
    consistency: pd.DataFrame | None,
    transport: dict[str, float],
    status: str,
    note: str,
) -> dict[str, Any]:
    confirmation = scores.loc[scores["split"].eq("confirmation")]
    coverage = float(confirmation["score_status"].eq("SCORED").mean()) if len(confirmation) else float("nan")
    sem_columns = [] if sem is None else [column for column in sem if column.endswith("_sem")]
    sem_values = np.array([], dtype=float) if not sem_columns else sem[sem_columns].to_numpy(float).ravel()
    sem_values = sem_values[np.isfinite(sem_values)]
    correlations = [] if consistency is None else consistency["correlation"].to_numpy(float)
    correlations = np.asarray(correlations, float)
    correlations = correlations[np.isfinite(correlations)]
    return {
        "operator": spec.name,
        "kind": spec.kind,
        "n_authors": int(features["user_id"].nunique()),
        "n_features": int(sum("::" in column and not column.startswith(("n_units::", "n_tokens::")) for column in features)),
        "n_factors": int(sum(column.startswith("SU7-FC-") and column.endswith("@v1") for column in scores)),
        "confirmation_authors": int(confirmation["user_id"].nunique()),
        "confirmation_scoreable_coverage": coverage,
        "median_unit_bootstrap_sem": float(np.median(sem_values)) if len(sem_values) else float("nan"),
        "mean_technical_view_consistency": float(np.mean(correlations)) if len(correlations) else float("nan"),
        **transport,
        "evidence_status": status,
        "note": note,
    }


def _status_for_base(sem: pd.DataFrame, consistency: pd.DataFrame, scores: pd.DataFrame) -> tuple[str, str]:
    confirmation = scores.loc[scores["split"].eq("confirmation")]
    coverage = confirmation["score_status"].eq("SCORED").mean() if len(confirmation) else 0.0
    has_sem = bool(sem.get("sem_status", pd.Series(dtype=str)).eq("BOOTSTRAP_SEM").any())
    correlations = pd.to_numeric(consistency.get("correlation", pd.Series(dtype=float)), errors="coerce")
    has_view = bool(np.isfinite(correlations.to_numpy(float)).any())
    if coverage > 0 and has_sem and has_view:
        return "L2_SCOREABLE_CANDIDATE", "Frozen score, local reference norms, and technical unit-resampling diagnostics saved."
    return "L1_POPULATION_STRUCTURE", "Score mapping exists, but this operator lacks adequate repeated-unit error evidence in this smoke run."


def _write_report(path: Path, *, config: dict[str, Any], schema_path: Path, summary: pd.DataFrame, output_dir: Path) -> None:
    table = summary.to_markdown(index=False, floatfmt=".3f") if not summary.empty else "No operator completed."
    text = f"""# SUICA V7 Observation-Operator Smoke Report

## Scope

This is a **label-free construction smoke test**. It compares observation
operators on a local PANDORA Tier-U reference cohort. Big Five, MBTI, external
criteria, old V3/V4 lockbox results, and raw user text were not used in factor
selection or scoring.

The report establishes only whether each operator can construct a frozen,
author-relative text-structure score with declared support conditions. It does
not name factors or claim personality, clinical, behavioural, or cross-domain
validity.

The four anonymous coordinates shown below are an **operational factor-count
probe** fixed in the run configuration. They are not a discovered factor
inventory or evidence that the underlying psychological object has four
dimensions. The reference cohort is a local eligibility-filtered sample, not
a PANDORA population norm.

## Run

- Config version: `{config['version']}`
- Seed: `{config['seed']}`
- Schema report: `{schema_path}`
- Artifact directory: `{output_dir}`

## Operator Summary

{table}

## Interpretation Rules

- `L2_SCOREABLE_CANDIDATE` means only that discovery-fit representation,
  aggregation, factor loadings and calibration norms can score confirmation
  authors without refitting, with local technical diagnostics saved.
- Technical view consistency is an even/odd observation comparison, **not**
  cross-day, cross-scenario, or personality reliability.
- `median_unit_bootstrap_sem` is uncertainty under resampling of the observed
  text units. It is unavailable by design for a one-unit whole-text operator.
- `subspace_similarity` is an author-disjoint within-corpus transport
  diagnostic, not a universality claim.

## Next Evidence Step

Freeze any executable L2 operator bundle, then compare it on independent
observation occasions or matched fixed/free text from the same people. Only
after that should external scales be joined as anchors.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    config = _load_config(args.config)
    if args.seed is not None:
        config["seed"] = int(args.seed)
    if args.max_users is not None:
        config["max_users"] = int(args.max_users)
    if args.quick:
        config["max_users"] = min(int(config["max_users"]), 90)
        config["max_comments_per_user"] = min(int(config["max_comments_per_user"]), 16)
        config["representation"]["max_features"] = min(int(config["representation"]["max_features"]), 2500)
        config["representation"]["bootstrap_repetitions"] = min(int(config["representation"]["bootstrap_repetitions"]), 12)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_dir = args.output_dir or ROOT / "results" / "v7_operator_smoke" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.report or ROOT / "reports" / "V7_OPERATOR_PSYCHOMETRIC_SMOKE.md"

    raw = _read_table(args.input)
    columns = [str(column) for column in raw.columns]
    column_map = {
        "user": _infer_column(columns, ["author", "user_id", "participant_id", "user", "id"], args.user_col, required=True),
        "text": _infer_column(columns, ["body", "text", "comment", "content", "message"], args.text_col, required=True),
        "order": _infer_column(columns, ["created_utc", "timestamp", "time", "date", "created_at"], args.order_col, required=False),
        "condition": _infer_column(columns, ["subreddit", "condition", "platform", "task", "forum"], args.condition_col, required=False),
    }
    canonical = canonicalize_comments(
        raw, user_col=str(column_map["user"]), text_col=str(column_map["text"]),
        order_col=column_map["order"], condition_col=column_map["condition"],
        min_tokens=int(config["min_tokens_per_unit"]), mask_personality_terms=bool(config["mask_personality_terms"]),
    )
    selected = select_reference_authors(
        canonical, min_comments_per_user=int(config["min_comments_per_user"]),
        max_users=int(config["max_users"]), seed=int(config["seed"]),
    )
    split_counts = selected.groupby("split", observed=True)["user_id"].nunique().to_dict()
    if any(int(split_counts.get(name, 0)) < 12 for name in ("discovery", "calibration", "confirmation")):
        raise RuntimeError(f"Reference cohort cannot support V7 3-way author split: {split_counts}")
    schema_path = output_dir / "data_schema.md"
    _schema_report(
        schema_path, source=args.input, raw=raw, column_map=column_map, canonical=canonical,
        selected=selected, mask_personality_terms=bool(config["mask_personality_terms"]),
        min_comments_per_user=int(config["min_comments_per_user"]),
        max_comments_per_user=int(config["max_comments_per_user"]),
    )
    _write_json(output_dir / "run_manifest.json", {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "config": config,
        "input": str(args.input),
        "column_map": column_map,
        "author_split_counts": {key: int(value) for key, value in split_counts.items()},
        "claim_boundary": "No external labels were loaded or used in this V7 smoke run.",
    })

    representation_spec = RepresentationSpec(
        max_features=int(config["representation"]["max_features"]),
        ngram_min=int(config["representation"]["ngram_range"][0]),
        ngram_max=int(config["representation"]["ngram_range"][1]),
        svd_dimensions=int(config["representation"]["svd_dimensions"]),
        factor_count=int(config["representation"]["factor_count"]),
        seed=int(config["seed"]),
    )
    specs = _operator_specs(config)
    base_specs = [spec for spec in specs if spec.kind != "nested"]
    all_features: dict[str, pd.DataFrame] = {}
    completed: dict[str, dict[str, Any]] = {}
    summary_rows: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []

    for spec in base_specs:
        units = build_observations(selected, spec).reset_index(drop=True)
        manifest = observation_manifest(selected, units, spec)
        _write_json(output_dir / f"observation_manifest_{spec.name}.json", manifest)
        discovery_units = units.loc[units["split"].eq("discovery")].reset_index(drop=True)
        representation = fit_representation(discovery_units, representation_spec)
        runtime_path = output_dir / "artifacts" / f"{spec.name}_representation.joblib"
        runtime_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(representation, runtime_path)
        embeddings = representation.transform(units["text"])
        features = author_features_from_embeddings(units, embeddings)
        all_features[spec.name] = features
        runtime_artifact = {
            "representation_path": str(runtime_path.relative_to(output_dir)),
            "representation_sha256": bundle_sha256(runtime_path),
            "storage": "local joblib; not a public data artifact",
        }
        minimum_support = 1 if spec.kind == "whole" else 2
        fitted = fit_factor_bundle(
            features, operator=spec.to_dict(), representation=representation_spec,
            runtime_artifact=runtime_artifact, min_units_for_score=minimum_support, seed=int(config["seed"]),
        )
        bundle_path = output_dir / "bundles" / f"{spec.name}_factor_bundle.json"
        fitted.bundle.write_json(bundle_path)
        persisted_runtime = joblib.load(runtime_path)
        persisted_bundle = read_factor_bundle(bundle_path)
        replay_embeddings = persisted_runtime.transform(units["text"])
        replay_features = author_features_from_embeddings(units, replay_embeddings)
        scores = score_author_features(persisted_bundle, replay_features)
        original_scores = score_author_features(fitted.bundle, features)
        score_columns = [column for column in scores if column.startswith("SU7-FC-")]
        replay_max_abs_diff = float(np.max(np.abs(
            scores[score_columns].to_numpy(float) - original_scores[score_columns].to_numpy(float)
        )))
        if replay_max_abs_diff > 1e-10:
            raise RuntimeError(f"Frozen bundle replay drift for {spec.name}: max abs diff={replay_max_abs_diff}")
        sem = unit_bootstrap_sem(
            units, replay_embeddings, persisted_bundle,
            repetitions=int(config["representation"]["bootstrap_repetitions"]), seed=int(config["seed"]),
        )
        scores = scores.merge(sem, on="user_id", how="left")
        confirmation_mask = units["split"].eq("confirmation").to_numpy()
        consistency = technical_view_consistency(
            units.loc[confirmation_mask].reset_index(drop=True), replay_embeddings[confirmation_mask], persisted_bundle,
        )
        transport = confirmation_subspace_similarity(persisted_bundle, replay_features, seed=int(config["seed"]))
        transport["frozen_replay_max_abs_diff"] = replay_max_abs_diff
        status, note = _status_for_base(sem, consistency, scores)
        scores.to_csv(output_dir / f"scores_{spec.name}.csv", index=False)
        consistency.to_csv(output_dir / f"technical_view_consistency_{spec.name}.csv", index=False)
        summary_rows.append(_summary_row(
            spec=spec, features=features, scores=scores, sem=sem, consistency=consistency,
            transport=transport, status=status, note=note,
        ))
        completed[spec.name] = {"bundle": persisted_bundle, "scores": scores, "status": status}
        for index in range(len(persisted_bundle.factor_loadings)):
            ledger.append({
                "timestamp_utc": datetime.now(UTC).isoformat(),
                "candidate_id": f"SU7-FC-{index + 1:04d}@v1::{spec.name}",
                "operator": spec.name,
                "status": status,
                "claim_boundary": persisted_bundle.claim_boundary,
                "author_split": {key: int(value) for key, value in split_counts.items()},
                "bundle_path": str(bundle_path.relative_to(output_dir)),
                "bundle_sha256": bundle_sha256(bundle_path),
                "technical_view_consistency": consistency.loc[consistency["factor"].eq(f"SU7-FC-{index + 1:04d}@v1"), "correlation"].tolist(),
            })

    for spec in (spec for spec in specs if spec.kind == "nested"):
        features = combine_nested_author_features(all_features, spec.members)
        runtime_artifact = {
            "nested_members": list(spec.members),
            "storage": "uses the frozen member representation artifacts recorded in this run",
        }
        fitted = fit_factor_bundle(
            features, operator=spec.to_dict(), representation=representation_spec,
            runtime_artifact=runtime_artifact, min_units_for_score=2, seed=int(config["seed"]),
        )
        bundle_path = output_dir / "bundles" / f"{spec.name}_factor_bundle.json"
        fitted.bundle.write_json(bundle_path)
        scores = score_author_features(fitted.bundle, features)
        scores["sem_status"] = "SEM_PENDING_MULTIVIEW_BOOTSTRAP"
        scores.to_csv(output_dir / f"scores_{spec.name}.csv", index=False)
        transport = confirmation_subspace_similarity(fitted.bundle, features, seed=int(config["seed"]))
        note = "Nested feature-level scoring is frozen; paired multi-view resampling is deferred to the next V7 experiment."
        summary_rows.append(_summary_row(
            spec=spec, features=features, scores=scores, sem=None, consistency=None,
            transport=transport, status="L1_POPULATION_STRUCTURE", note=note,
        ))
        for index in range(len(fitted.bundle.factor_loadings)):
            ledger.append({
                "timestamp_utc": datetime.now(UTC).isoformat(),
                "candidate_id": f"SU7-FC-{index + 1:04d}@v1::{spec.name}",
                "operator": spec.name,
                "status": "L1_POPULATION_STRUCTURE",
                "claim_boundary": fitted.bundle.claim_boundary,
                "author_split": {key: int(value) for key, value in split_counts.items()},
                "bundle_path": str(bundle_path.relative_to(output_dir)),
                "bundle_sha256": bundle_sha256(bundle_path),
                "technical_view_consistency": [],
            })

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(output_dir / "operator_summary.csv", index=False)
    with (output_dir / "discovery_ledger.jsonl").open("w", encoding="utf-8") as handle:
        for row in ledger:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    _write_report(report_path, config=config, schema_path=schema_path, summary=summary, output_dir=output_dir)
    print(json.dumps({
        "output_dir": str(output_dir), "report": str(report_path),
        "operators": summary[["operator", "evidence_status"]].to_dict(orient="records"),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
