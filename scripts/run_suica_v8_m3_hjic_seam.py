#!/usr/bin/env python3
"""Run V8-M3-HJIC-SEAM-1 end-to-end synthetic confirmation."""
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
from suica_core.v8_m3_hjic_seam import (  # noqa: E402
    M3HJICSeamSpec,
    run_m3_hjic_seam_repetition,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_m3_hjic_seam.json"
DEFAULT_OUTPUT = ROOT / "results" / "v8_m3_hjic_seam" / "seam1_20260802"
DEFAULT_REPORT = ROOT / "reports" / "V8_M3_HJIC_SEAM_REPORT.md"


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
    return run_m3_hjic_seam_repetition(
        repetition,
        seed=seed,
        spec=M3HJICSeamSpec(**spec_payload),
    )


def _rate(frame: pd.DataFrame, column: str) -> float:
    return float(frame[column].fillna(0).astype(float).mean())


def _evaluate(
    tables: dict[str, pd.DataFrame],
    gates: dict[str, float],
) -> dict[str, Any]:
    licenses = tables["licenses"]
    truth = tables["truth_audit"]
    attenuation = tables["attenuation_diagnostics"]
    alias = tables["alias_invariance"]
    coverage = tables["uncertainty_coverage"]
    commutation = tables["aggregation_commutation"]

    def rows(frame: pd.DataFrame, world: str) -> pd.DataFrame:
        return frame.loc[frame["world"].eq(world)]

    clean_license = rows(licenses, "GLOBAL_INVARIANT")
    clean_truth = rows(truth, "GLOBAL_INVARIANT")
    alias_license = rows(licenses, "MICRO_GAUGE_ALIAS")
    alias_rows = rows(alias, "MICRO_GAUGE_ALIAS")
    attenuation_rows = rows(
        attenuation,
        "ESTIMATION_ATTENUATION",
    )
    cancellation = rows(
        licenses,
        "BALANCED_CONTEXT_CANCELLATION",
    )
    ecological = rows(licenses, "ECOLOGICAL_ONLY")
    mismatch = rows(licenses, "MECHANISM_FAMILY_MISMATCH")
    heldout_null = rows(licenses, "HELDOUT_D0_NULL")
    within_support_gauge = rows(licenses, "WITHIN_SUPPORT_GAUGE")
    drift_global = rows(
        licenses,
        "MEASUREMENT_SUPPORT_DRIFT_GLOBAL",
    )
    drift_ecological = rows(
        licenses,
        "MEASUREMENT_SUPPORT_DRIFT_ECOLOGICAL",
    )
    support_underresolved = rows(
        licenses,
        "SUPPORT_UNDERRESOLVED",
    )

    coverage_total = int(coverage["total"].sum())
    coverage_success = int(coverage["covered"].sum())
    nested_total = int(coverage["nested_total"].sum())
    nested_success = int(coverage["nested_covered"].sum())
    diagnostics = {
        "clean_seam_license_rate": _rate(
            clean_license,
            "final_seam_license",
        ),
        "clean_relation_fidelity_q05": float(
            clean_truth["relation_fidelity"].quantile(0.05)
        ),
        "clean_relative_frobenius_q95": float(
            clean_truth["relative_frobenius_error"].quantile(0.95)
        ),
        "decomposition_error_q95": float(
            commutation["decomposition_error"].quantile(0.95)
        ),
        "pooled_coverage": coverage_success / coverage_total,
        "coverage_cells": coverage_success,
        "coverage_total": coverage_total,
        "nested_pooled_coverage": nested_success / nested_total,
        "nested_coverage_cells": nested_success,
        "nested_coverage_total": nested_total,
        "alias_output_difference_q95": float(
            alias_rows["relative_output_difference"].quantile(0.95)
        ),
        "alias_mechanism_identity_rate": _rate(
            alias_rows,
            "mechanism_identity_license",
        ),
        "alias_seam_license_rate": _rate(
            alias_license,
            "final_seam_license",
        ),
        "attenuation_correction_win_rate": _rate(
            attenuation_rows,
            "corrected_better",
        ),
        "attenuation_median_error_reduction": float(
            attenuation_rows["relative_error_reduction"].median()
        ),
        "cancellation_detection_rate": _rate(
            cancellation,
            "cancellation_detected",
        ),
        "cancellation_global_license_rate": _rate(
            cancellation,
            "global_invariant_license",
        ),
        "ecological_detection_rate": _rate(
            ecological,
            "ecological_between_detected",
        ),
        "ecological_relation_license_rate": _rate(
            ecological,
            "relation_license",
        ),
        "mismatch_detection_rate": _rate(
            mismatch,
            "mismatch_detected",
        ),
        "mismatch_seam_license_rate": _rate(
            mismatch,
            "final_seam_license",
        ),
        "mismatch_false_ecological_rate": _rate(
            mismatch,
            "ecological_between_detected",
        ),
        "heldout_null_false_ecological_rate": (
            _rate(heldout_null, "ecological_between_detected")
            if not heldout_null.empty
            else 0.0
        ),
        "clean_support_refusal_rate": float(
            1.0 - _rate(clean_license, "support_adequate")
        ),
        "ecological_support_refusal_rate": float(
            1.0 - _rate(ecological, "support_adequate")
        ),
        "within_support_gauge_refusal_rate": (
            float(
                1.0
                - _rate(within_support_gauge, "support_adequate")
            )
            if not within_support_gauge.empty
            else 0.0
        ),
        "drift_global_detection_rate": (
            _rate(drift_global, "support_noninvariant")
            if not drift_global.empty
            else 1.0
        ),
        "drift_ecological_detection_rate": (
            _rate(drift_ecological, "support_noninvariant")
            if not drift_ecological.empty
            else 1.0
        ),
        "drift_global_seam_license_rate": (
            _rate(drift_global, "final_seam_license")
            if not drift_global.empty
            else 0.0
        ),
        "drift_ecological_seam_license_rate": (
            _rate(drift_ecological, "final_seam_license")
            if not drift_ecological.empty
            else 0.0
        ),
        "support_underresolution_detection_rate": (
            _rate(support_underresolved, "support_underresolved")
            if not support_underresolved.empty
            else 1.0
        ),
        "support_underresolved_seam_license_rate": (
            _rate(support_underresolved, "final_seam_license")
            if not support_underresolved.empty
            else 0.0
        ),
        "support_d1_d2_decision_agreement_rate": _rate(
            licenses,
            "support_d1_d2_decision_agreement",
        ),
        "heldout_null_false_support_drift_rate": (
            _rate(heldout_null, "support_noninvariant")
            if not heldout_null.empty
            else 0.0
        ),
        "d1_d2_decision_agreement_rate": _rate(
            licenses,
            "d1_d2_decision_agreement",
        ),
        "truth_usage_rate": _rate(
            licenses,
            "truth_used_by_license",
        ),
    }
    checks = {
        "clean_end_to_end_recovery": bool(
            diagnostics["clean_seam_license_rate"]
            >= gates["minimum_clean_seam_license_rate"]
            and diagnostics["clean_relation_fidelity_q05"]
            >= gates["minimum_clean_relation_fidelity_q05"]
            and diagnostics["clean_relative_frobenius_q95"]
            <= gates["maximum_clean_relative_frobenius_q95"]
        ),
        "aggregation_commutation": bool(
            diagnostics["decomposition_error_q95"]
            <= gates["maximum_decomposition_error_q95"]
        ),
        "population_uncertainty_coverage": bool(
            gates["minimum_pooled_coverage"]
            <= diagnostics["pooled_coverage"]
            <= gates["maximum_pooled_coverage"]
        ),
        "gauge_alias_refusal": bool(
            diagnostics["alias_output_difference_q95"]
            <= gates["maximum_alias_output_difference_q95"]
            and diagnostics["alias_mechanism_identity_rate"]
            <= gates["maximum_alias_mechanism_identity_rate"]
            and diagnostics["alias_seam_license_rate"]
            >= gates["minimum_alias_seam_license_rate"]
        ),
        "attenuation_correction": bool(
            diagnostics["attenuation_correction_win_rate"]
            >= gates["minimum_attenuation_correction_win_rate"]
            and diagnostics["attenuation_median_error_reduction"]
            >= gates["minimum_attenuation_median_error_reduction"]
        ),
        "balanced_context_cancellation": bool(
            diagnostics["cancellation_detection_rate"]
            >= gates["minimum_cancellation_detection_rate"]
            and diagnostics["cancellation_global_license_rate"]
            <= gates["maximum_cancellation_global_license_rate"]
        ),
        "ecological_only_refusal": bool(
            diagnostics["ecological_detection_rate"]
            >= gates["minimum_ecological_detection_rate"]
            and diagnostics["ecological_relation_license_rate"]
            <= gates["maximum_ecological_relation_license_rate"]
        ),
        "mechanism_family_mismatch_refusal": bool(
            diagnostics["mismatch_detection_rate"]
            >= gates["minimum_mismatch_detection_rate"]
            and diagnostics["mismatch_seam_license_rate"]
            <= gates["maximum_mismatch_seam_license_rate"]
            and diagnostics["mismatch_false_ecological_rate"]
            <= gates.get("maximum_mismatch_false_ecological_rate", 1.0)
        ),
        "heldout_between_null_safety": bool(
            diagnostics["heldout_null_false_ecological_rate"]
            <= gates.get(
                "maximum_heldout_null_false_ecological_rate",
                1.0,
            )
        ),
        "measurement_support_invariance": bool(
            diagnostics["clean_support_refusal_rate"]
            <= gates.get("maximum_clean_support_refusal_rate", 1.0)
            and diagnostics["ecological_support_refusal_rate"]
            <= gates.get(
                "maximum_ecological_support_refusal_rate",
                1.0,
            )
            and diagnostics["within_support_gauge_refusal_rate"]
            <= gates.get(
                "maximum_within_support_gauge_refusal_rate",
                1.0,
            )
            and diagnostics["drift_global_detection_rate"]
            >= gates.get("minimum_drift_global_detection_rate", 0.0)
            and diagnostics["drift_ecological_detection_rate"]
            >= gates.get(
                "minimum_drift_ecological_detection_rate",
                0.0,
            )
            and diagnostics["drift_global_seam_license_rate"]
            <= gates.get("maximum_drift_global_seam_license_rate", 1.0)
            and diagnostics["drift_ecological_seam_license_rate"]
            <= gates.get(
                "maximum_drift_ecological_seam_license_rate",
                1.0,
            )
            and diagnostics["support_d1_d2_decision_agreement_rate"]
            >= gates.get(
                "minimum_support_d1_d2_decision_agreement_rate",
                0.0,
            )
            and diagnostics["heldout_null_false_support_drift_rate"]
            <= gates.get(
                "maximum_heldout_null_false_support_drift_rate",
                1.0,
            )
        ),
        "support_underresolution_refusal": bool(
            diagnostics["support_underresolution_detection_rate"]
            >= gates.get(
                "minimum_support_underresolution_detection_rate",
                0.0,
            )
            and diagnostics["support_underresolved_seam_license_rate"]
            <= gates.get(
                "maximum_support_underresolved_seam_license_rate",
                1.0,
            )
        ),
        "independent_confirmation_agreement": bool(
            diagnostics["d1_d2_decision_agreement_rate"]
            >= gates["minimum_d1_d2_decision_agreement_rate"]
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
        .groupby("world", as_index=False)
        .agg(
            relation_license_rate=("relation_license", "mean"),
            seam_license_rate=("final_seam_license", "mean"),
            cancellation_rate=("cancellation_detected", "mean"),
            ecological_rate=("ecological_between_detected", "mean"),
            mismatch_rate=("mismatch_detected", "mean"),
            d1_d2_agreement=("d1_d2_decision_agreement", "mean"),
        )
    )
    lines = [
        "# V8-M3-HJIC-SEAM-1 Formal Report",
        "",
        f"Status: `{decision['status']}`",
        "",
        "This battery tests the complete registered arrow from synthetic raw "
        "event paths through a frozen generator-blind M3 quotient to an HJIC "
        "context relation field and its explicit refusal modes.",
        "",
        "## World summary",
        "",
        summary.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Headline diagnostics",
        "",
        f"- Clean seam license: "
        f"{diagnostics['clean_seam_license_rate']:.4f}.",
        f"- Clean relation fidelity q05 / relative error q95: "
        f"{diagnostics['clean_relation_fidelity_q05']:.4f} / "
        f"{diagnostics['clean_relative_frobenius_q95']:.4f}.",
        f"- Covariance decomposition error q95: "
        f"{diagnostics['decomposition_error_q95']:.3e}.",
        f"- Primary population 95% coverage: "
        f"{diagnostics['pooled_coverage']:.4f} "
        f"({diagnostics['coverage_cells']}/"
        f"{diagnostics['coverage_total']}); nested sensitivity "
        f"{diagnostics['nested_pooled_coverage']:.4f}.",
        f"- Gauge output q95 / identity license / seam license: "
        f"{diagnostics['alias_output_difference_q95']:.3e} / "
        f"{diagnostics['alias_mechanism_identity_rate']:.4f} / "
        f"{diagnostics['alias_seam_license_rate']:.4f}.",
        f"- Attenuation correction win rate / median error reduction: "
        f"{diagnostics['attenuation_correction_win_rate']:.4f} / "
        f"{diagnostics['attenuation_median_error_reduction']:.4f}.",
        f"- Cancellation detect / false global: "
        f"{diagnostics['cancellation_detection_rate']:.4f} / "
        f"{diagnostics['cancellation_global_license_rate']:.4f}.",
        f"- Ecological detect / false individual relation: "
        f"{diagnostics['ecological_detection_rate']:.4f} / "
        f"{diagnostics['ecological_relation_license_rate']:.4f}.",
        f"- Mechanism mismatch detect / false seam license: "
        f"{diagnostics['mismatch_detection_rate']:.4f} / "
        f"{diagnostics['mismatch_seam_license_rate']:.4f}.",
        f"- Held-out-null / mismatch false ecological classification: "
        f"{diagnostics['heldout_null_false_ecological_rate']:.4f} / "
        f"{diagnostics['mismatch_false_ecological_rate']:.4f}.",
        f"- Clean/ecological/within-gauge support refusal: "
        f"{diagnostics['clean_support_refusal_rate']:.4f} / "
        f"{diagnostics['ecological_support_refusal_rate']:.4f} / "
        f"{diagnostics['within_support_gauge_refusal_rate']:.4f}.",
        f"- Global/ecological support-drift detection: "
        f"{diagnostics['drift_global_detection_rate']:.4f} / "
        f"{diagnostics['drift_ecological_detection_rate']:.4f}.",
        f"- Support-underresolution detection / false seam: "
        f"{diagnostics['support_underresolution_detection_rate']:.4f} / "
        f"{diagnostics['support_underresolved_seam_license_rate']:.4f}.",
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
        "The licensed object is an observable event-to-relation procedure, "
        "not a unique hidden mechanism. A stable out-of-family periodic "
        "signal is reported as estimator-family mismatch rather than erased "
        "or relabelled as absence.",
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
    spec = M3HJICSeamSpec(**dict(config["spec"]))
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
            ROOT / "suica_core" / "v8_m3_hjic_seam.py",
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
    tables = {
        name: pd.DataFrame(
            row
            for output in outputs
            for row in output[name]
        )
        for name in outputs[0]
    }
    for name, frame in tables.items():
        frame.to_csv(output / f"{name}.csv", index=False)

    evaluated = _evaluate(tables, dict(config["gates"]))
    status = (
        str(config.get("pass_status", "V8_M3_HJIC_SEAM1_PASS"))
        if evaluated["all_pass"]
        else str(
            config.get(
                "partial_status",
                "V8_M3_HJIC_SEAM1_PARTIAL",
            )
        )
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
    (output / "REPORT.md").write_text(
        _report(decision, tables),
        encoding="utf-8",
    )
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
