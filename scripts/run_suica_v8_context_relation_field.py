#!/usr/bin/env python3
"""Run V8-HJIC-1C context-fibered relation and aggregation tests."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from datetime import UTC, datetime
import json
from pathlib import Path
import shutil
import sys
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_context_relation_field import (  # noqa: E402
    ContextRelationSpec,
    run_context_relation_repetition,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_context_relation_field.json"
DEFAULT_OUTPUT = (
    ROOT / "results" / "v8_context_relation_field" / "hjic1c_20260801"
)
DEFAULT_REPORT = ROOT / "reports" / "V8_CONTEXT_RELATION_FIELD_REPORT.md"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _worker(
    payload: tuple[int, int, dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    repetition, seed, spec_payload = payload
    return run_context_relation_repetition(
        repetition,
        seed=seed,
        spec=ContextRelationSpec(**spec_payload),
    )


def _rate(frame: pd.DataFrame, column: str) -> float:
    if frame.empty:
        return 0.0
    return float(frame[column].fillna(0).astype(float).mean())


def _evaluate(
    tables: dict[str, pd.DataFrame],
    gates: dict[str, float],
) -> dict[str, Any]:
    licenses = tables["licenses"]
    heterogeneity = tables["heterogeneity_cancellation"]
    ecological = tables["ecological_failure_modes"]
    commutation = tables["aggregation_commutation"]
    coverage = tables["uncertainty_coverage"]
    frontier = tables["context_reliability_frontier"]

    def license_world(name: str) -> pd.DataFrame:
        return licenses.loc[licenses["world"].eq(name)]

    def heterogeneity_world(name: str) -> pd.DataFrame:
        return heterogeneity.loc[heterogeneity["world"].eq(name)]

    global_world = license_world("GLOBAL_INVARIANT")
    sign_world = license_world("BALANCED_SIGN_REVERSAL")
    moderation_world = license_world("TRUE_CONTEXT_MODERATION")
    ecological_world = license_world("ECOLOGICAL_ONLY")
    composition_world = license_world("COMPOSITION_REWEIGHT")
    in_sieve = license_world("NONLINEAR_SIMPSON_IN_SIEVE")
    out_sieve = license_world("NONLINEAR_SIMPSON_OUT_OF_SIEVE")
    local_null = license_world("LOCAL_NULL_MULTIPLE_STRATA")
    low_gap = license_world("LOCAL_LOW_SINGULAR_GAP")
    collider = license_world("COLLIDER_OR_DESCENDANT_Z")

    sign_heterogeneity = heterogeneity_world("BALANCED_SIGN_REVERSAL")
    moderation_heterogeneity = heterogeneity_world(
        "TRUE_CONTEXT_MODERATION"
    )
    composition_ecological = ecological.loc[
        ecological["world"].eq("COMPOSITION_REWEIGHT")
    ]
    coverage_total = int(coverage["total_cells"].sum())
    coverage_success = int(coverage["covered_cells"].sum())
    pooled_coverage = (
        coverage_success / coverage_total if coverage_total else 0.0
    )
    high_reliability = frontier.loc[
        frontier["context_reliability"].ge(0.8)
    ]
    low_reliability = frontier.loc[
        frontier["context_reliability"].le(0.4)
    ]

    diagnostics = {
        "decomposition_error_q95": float(
            commutation["decomposition_error"].quantile(0.95)
        ),
        "pooled_coverage": float(pooled_coverage),
        "coverage_cells": coverage_success,
        "coverage_total": coverage_total,
        "global_invariant_license_rate": _rate(
            global_world,
            "global_invariant_license",
        ),
        "global_invariant_heterogeneity_rate": _rate(
            global_world,
            "local_atlas_license",
        ),
        "sign_reversal_local_atlas_rate": _rate(
            sign_world,
            "local_atlas_license",
        ),
        "sign_reversal_heterogeneity_rate": float(
            sign_heterogeneity["heterogeneity"].ge(0.12).mean()
        ),
        "sign_reversal_cancellation_rate": _rate(
            sign_world,
            "cancellation_detected",
        ),
        "sign_reversal_global_license_rate": _rate(
            sign_world,
            "global_invariant_license",
        ),
        "moderation_local_atlas_rate": _rate(
            moderation_world,
            "local_atlas_license",
        ),
        "moderation_heterogeneity_rate": float(
            moderation_heterogeneity["heterogeneity"].ge(0.12).mean()
        ),
        "moderation_global_license_rate": _rate(
            moderation_world,
            "global_invariant_license",
        ),
        "ecological_between_detection_rate": _rate(
            ecological_world,
            "ecological_between_detected",
        ),
        "ecological_individual_license_rate": _rate(
            ecological_world,
            "final_relation_license",
        ),
        "composition_attribution_rate": _rate(
            composition_world,
            "composition_reweight_detected",
        ),
        "composition_field_drift_failure_rate": float(
            composition_ecological["composition_attribution"].lt(0.70).mean()
        ),
        "in_sieve_false_relation_rate": _rate(
            in_sieve,
            "final_relation_license",
        ),
        "out_of_sieve_misspecification_rate": _rate(
            out_sieve,
            "residualizer_misspecified",
        ),
        "out_of_sieve_final_relation_rate": _rate(
            out_sieve,
            "final_relation_license",
        ),
        "local_null_familywise_license_rate": _rate(
            local_null,
            "final_relation_license",
        ),
        "low_gap_relation_license_rate": _rate(
            low_gap,
            "final_relation_license",
        ),
        "low_gap_mode_license_rate": _rate(low_gap, "mode_license"),
        "high_reliability_relation_rate": _rate(
            high_reliability,
            "final_relation_license",
        ),
        "low_reliability_underresolution_rate": _rate(
            low_reliability,
            "context_underresolved",
        ),
        "collider_role_refusal_rate": _rate(
            collider,
            "causal_role_refusal",
        ),
        "collider_final_relation_rate": _rate(
            collider,
            "final_relation_license",
        ),
        "truth_usage_rate": float(
            licenses["truth_used_by_license"].astype(float).mean()
        ),
    }
    checks = {
        "covariance_decomposition": bool(
            diagnostics["decomposition_error_q95"]
            <= gates["maximum_decomposition_error_q95"]
        ),
        "uncertainty_coverage": bool(
            gates["minimum_pooled_coverage"]
            <= diagnostics["pooled_coverage"]
            <= gates["maximum_pooled_coverage"]
        ),
        "global_invariant": bool(
            diagnostics["global_invariant_license_rate"]
            >= gates["minimum_global_invariant_license_rate"]
            and diagnostics["global_invariant_heterogeneity_rate"]
            <= gates["maximum_global_invariant_heterogeneity_rate"]
        ),
        "balanced_sign_reversal": bool(
            diagnostics["sign_reversal_local_atlas_rate"]
            >= gates["minimum_sign_reversal_local_atlas_rate"]
            and diagnostics["sign_reversal_heterogeneity_rate"]
            >= gates["minimum_sign_reversal_heterogeneity_rate"]
            and diagnostics["sign_reversal_cancellation_rate"]
            >= gates["minimum_sign_reversal_cancellation_rate"]
            and diagnostics["sign_reversal_global_license_rate"]
            <= gates["maximum_sign_reversal_global_license_rate"]
        ),
        "true_context_moderation": bool(
            diagnostics["moderation_local_atlas_rate"]
            >= gates["minimum_moderation_local_atlas_rate"]
            and diagnostics["moderation_heterogeneity_rate"]
            >= gates["minimum_moderation_heterogeneity_rate"]
            and diagnostics["moderation_global_license_rate"]
            <= gates["maximum_moderation_global_license_rate"]
        ),
        "ecological_only": bool(
            diagnostics["ecological_between_detection_rate"]
            >= gates["minimum_ecological_between_detection_rate"]
            and diagnostics["ecological_individual_license_rate"]
            <= gates["maximum_ecological_individual_license_rate"]
        ),
        "composition_reweight": bool(
            diagnostics["composition_attribution_rate"]
            >= gates["minimum_composition_attribution_rate"]
            and diagnostics["composition_field_drift_failure_rate"]
            <= gates["maximum_composition_field_drift_failure_rate"]
        ),
        "residualizer_specification": bool(
            diagnostics["in_sieve_false_relation_rate"]
            <= gates["maximum_in_sieve_false_relation_rate"]
            and diagnostics["out_of_sieve_misspecification_rate"]
            >= gates["minimum_out_of_sieve_misspecification_rate"]
            and diagnostics["out_of_sieve_final_relation_rate"]
            <= gates["maximum_out_of_sieve_final_relation_rate"]
        ),
        "local_familywise_null": bool(
            diagnostics["local_null_familywise_license_rate"]
            <= gates["maximum_local_null_familywise_license_rate"]
        ),
        "relation_without_unique_mode": bool(
            diagnostics["low_gap_relation_license_rate"]
            >= gates["minimum_low_gap_relation_license_rate"]
            and diagnostics["low_gap_mode_license_rate"]
            <= gates["maximum_low_gap_mode_license_rate"]
        ),
        "context_reliability_frontier": bool(
            diagnostics["high_reliability_relation_rate"]
            >= gates["minimum_high_reliability_relation_rate"]
            and diagnostics["low_reliability_underresolution_rate"]
            >= gates["minimum_low_reliability_underresolution_rate"]
        ),
        "collider_role_refusal": bool(
            diagnostics["collider_role_refusal_rate"]
            >= gates["minimum_collider_role_refusal_rate"]
            and diagnostics["collider_final_relation_rate"]
            <= gates["maximum_collider_final_relation_rate"]
        ),
        "truth_isolation": bool(
            diagnostics["truth_usage_rate"]
            <= gates["maximum_truth_usage_rate"]
        ),
    }
    return {
        "checks": checks,
        "diagnostics": diagnostics,
        "all_pass": bool(all(checks.values())),
    }


def _report(
    decision: dict[str, Any],
    tables: dict[str, pd.DataFrame],
) -> str:
    diagnostics = decision["diagnostics"]
    summary = (
        tables["licenses"]
        .groupby(["world", "context_reliability"], as_index=False)
        .agg(
            relation_license_rate=("final_relation_license", "mean"),
            global_license_rate=("global_invariant_license", "mean"),
            local_atlas_rate=("local_atlas_license", "mean"),
            mode_license_rate=("mode_license", "mean"),
            context_refusal_rate=("context_underresolved", "mean"),
            misspecification_rate=("residualizer_misspecified", "mean"),
        )
    )
    lines = [
        "# V8-HJIC-1C Context-Fibered Relation Field Report",
        "",
        f"Status: `{decision['status']}`",
        "",
        "This experiment estimates context-indexed technical relation fields "
        "from two replicated readout families. It computes every aggregate in "
        "covariance space before one calibration-frozen whitening map, so the "
        "within/between/total decomposition is directly auditable.",
        "",
        "## World summary",
        "",
        summary.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Headline diagnostics",
        "",
        f"- Covariance-decomposition q95 error: "
        f"{diagnostics['decomposition_error_q95']:.6g}.",
        f"- Pooled cell-wise 95% coverage: "
        f"{diagnostics['pooled_coverage']:.4f} "
        f"({diagnostics['coverage_cells']}/"
        f"{diagnostics['coverage_total']}).",
        f"- Global-invariant license/heterogeneity false alarm: "
        f"{diagnostics['global_invariant_license_rate']:.4f} / "
        f"{diagnostics['global_invariant_heterogeneity_rate']:.4f}.",
        f"- Sign-reversal local/cancellation/global license: "
        f"{diagnostics['sign_reversal_local_atlas_rate']:.4f} / "
        f"{diagnostics['sign_reversal_cancellation_rate']:.4f} / "
        f"{diagnostics['sign_reversal_global_license_rate']:.4f}.",
        f"- Ecological-only between detection/individual false license: "
        f"{diagnostics['ecological_between_detection_rate']:.4f} / "
        f"{diagnostics['ecological_individual_license_rate']:.4f}.",
        f"- Composition attribution: "
        f"{diagnostics['composition_attribution_rate']:.4f}.",
        f"- Out-of-sieve misspecification detection/final false relation: "
        f"{diagnostics['out_of_sieve_misspecification_rate']:.4f} / "
        f"{diagnostics['out_of_sieve_final_relation_rate']:.4f}.",
        f"- Low-gap relation/mode license: "
        f"{diagnostics['low_gap_relation_license_rate']:.4f} / "
        f"{diagnostics['low_gap_mode_license_rate']:.4f}.",
        f"- High-reliability relation / low-reliability refusal: "
        f"{diagnostics['high_reliability_relation_rate']:.4f} / "
        f"{diagnostics['low_reliability_underresolution_rate']:.4f}.",
        "",
        "## Gates",
        "",
    ]
    lines.extend(
        f"- `{name}`: {'PASS' if passed else 'FAIL'}"
        for name, passed in decision["checks"].items()
    )
    lines.extend([
        "",
        "## Ruling",
        "",
        "A total relation is not an average of context correlations. The "
        "licensed object is a context-indexed technical field plus separate "
        "within-context, between-context, and composition components. A "
        "between-context relation cannot be promoted to an individual "
        "relation, and a local mode is withheld when its singular direction "
        "is underresolved.",
        "",
        f"Claim boundary: {decision['claim_boundary']}",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--jobs", type=int)
    parser.add_argument("--permutations", type=int)
    parser.add_argument("--bootstrap-draws", type=int)
    args = parser.parse_args()

    config_path = args.config.resolve()
    config = _read_json(config_path)
    repetitions = int(args.repetitions or config["repetitions"])
    jobs = int(args.jobs or config["jobs"])
    spec = ContextRelationSpec(**dict(config["spec"]))
    if args.permutations is not None:
        spec = replace(spec, permutations=int(args.permutations))
    if args.bootstrap_draws is not None:
        spec = replace(spec, bootstrap_draws=int(args.bootstrap_draws))
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    write_run_manifest(
        output / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=config_path,
        code_paths=[
            Path(__file__).resolve(),
            ROOT / "suica_core" / "v8_context_relation_field.py",
        ],
        estimand_id=str(config["estimand_id"]),
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )

    payloads = [
        (repetition, int(config["seed"]), dict(spec.__dict__))
        for repetition in range(repetitions)
    ]
    if jobs == 1:
        outputs = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as pool:
            outputs = list(pool.map(_worker, payloads))

    names = tuple(outputs[0])
    tables = {
        name: pd.DataFrame(
            row
            for output in outputs
            for row in output[name]
        )
        for name in names
    }
    for name, frame in tables.items():
        frame.to_csv(output / f"{name}.csv", index=False)
    evaluated = _evaluate(tables, dict(config["gates"]))
    status = (
        "V8_HJIC1C_CONTEXT_RELATION_FIELD_PASS"
        if evaluated["all_pass"]
        else "V8_HJIC1C_CONTEXT_RELATION_FIELD_PARTIAL"
    )
    decision = {
        "version": str(config["version"]),
        "estimand_id": str(config["estimand_id"]),
        "status": status,
        "completed_utc": datetime.now(UTC).isoformat(),
        "repetitions": repetitions,
        "permutations": spec.permutations,
        "bootstrap_draws": spec.bootstrap_draws,
        "external_labels_read": False,
        **evaluated,
        "claim_boundary": str(config["claim_boundary"]),
    }
    _write_json(output / "decision.json", decision)
    report = _report(decision, tables)
    (output / "REPORT.md").write_text(report, encoding="utf-8")
    args.report.resolve().parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(output / "REPORT.md", args.report.resolve())
    write_artifact_inventory(
        output,
        output / "artifact_inventory.json",
        exclude_relative_paths=("artifact_inventory.json",),
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
