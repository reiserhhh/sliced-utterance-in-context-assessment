#!/usr/bin/env python3
"""Run the V8-HJIC-1 synthetic typed-graph battery."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import UTC, datetime
import json
from pathlib import Path
import shutil
import sys
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_hierarchical_identifiability import (  # noqa: E402
    HJICSpec,
    run_hjic_repetition,
)


DEFAULT_CONFIG = (
    ROOT / "configs" / "v8_hierarchical_joint_identifiability.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_hierarchical_joint_identifiability"
    / "hjic1_20260729"
)
DEFAULT_REPORT = (
    ROOT / "reports" / "V8_HIERARCHICAL_IDENTIFIABILITY_REPORT.md"
)


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
    return run_hjic_repetition(
        repetition,
        seed=seed,
        spec=HJICSpec(**spec_payload),
    )


def _quantile(values: pd.Series, probability: float) -> float:
    finite = pd.to_numeric(values, errors="coerce").dropna()
    return (
        float(np.quantile(finite.to_numpy(float), probability))
        if len(finite)
        else float("nan")
    )


def _aggregate(
    outputs: list[dict[str, list[dict[str, Any]]]],
    *,
    seed: int,
) -> dict[str, pd.DataFrame]:
    tables: dict[str, list[dict[str, Any]]] = {
        key: []
        for key in (
            "component",
            "commutation",
            "coverage",
            "refusal",
            "information",
            "route",
            "relation",
            "reference",
        )
    }
    for repetition, output in enumerate(outputs):
        for key, rows in output.items():
            for row in rows:
                tables[key].append({
                    "repetition": repetition,
                    "seed": int(seed + repetition * 1_000_003),
                    **row,
                })
    return {
        key: pd.DataFrame(rows)
        for key, rows in tables.items()
    }


def _evaluate_gates(
    tables: dict[str, pd.DataFrame],
    gates: dict[str, float],
) -> tuple[dict[str, Any], dict[str, pd.DataFrame]]:
    component = tables["component"]
    component_summary = (
        component.groupby("component", as_index=False)
        .agg(
            mean_correlation=("truth_correlation", "mean"),
            q05_correlation=(
                "truth_correlation",
                lambda value: _quantile(value, 0.05),
            ),
        )
    )
    commutation = tables["commutation"]
    commutation_summary = (
        commutation.groupby("component", as_index=False)
        .agg(
            mean_defect=("standardized_commutation_defect", "mean"),
            q95_defect=(
                "standardized_commutation_defect",
                lambda value: _quantile(value, 0.95),
            ),
        )
    )
    refusal = tables["refusal"]
    refusal_summary = (
        refusal.groupby(["world", "component"], as_index=False)
        .agg(
            refusal_rate=("refusal", "mean"),
            false_point_rate=("false_point_identification", "mean"),
            mean_auc=("observational_auc", "mean"),
            minimum_auc=("observational_auc", "min"),
            maximum_auc=("observational_auc", "max"),
            minimum_latent_separation=("latent_separation", "min"),
            maximum_observed_difference=("observed_max_difference", "max"),
        )
    )
    coverage = tables["coverage"]
    pooled_coverage = float(
        np.average(
            coverage["coverage"],
            weights=coverage["interval_cells"],
        )
    )
    information = tables["information"]
    route = tables["route"]
    relation = tables["relation"]
    reference = tables["reference"]
    shared = relation.loc[relation["world"].eq("SHARED_LATENT")]
    nuisance = relation.loc[relation["world"].eq("COMMON_NUISANCE")]

    checks = {
        "component_recovery": bool(
            component_summary["q05_correlation"].min()
            >= gates["minimum_component_q05_correlation"]
        ),
        "commutation": bool(
            commutation_summary["q95_defect"].max()
            <= gates["maximum_commutation_q95_defect"]
        ),
        "coverage": bool(
            gates["minimum_interval_coverage"]
            <= pooled_coverage
            <= gates["maximum_interval_coverage"]
        ),
        "alias_refusal": bool(
            refusal_summary["refusal_rate"].min()
            >= gates["minimum_alias_refusal_rate"]
            and refusal_summary["false_point_rate"].max()
            <= gates["maximum_alias_false_point_rate"]
            and refusal_summary["minimum_auc"].min()
            >= gates["minimum_alias_auc"]
            and refusal_summary["maximum_auc"].max()
            <= gates["maximum_alias_auc"]
        ),
        "information_order": bool(
            information["dpi_violation_bits"].max()
            <= gates["maximum_dpi_violation_bits"]
            and information[
                "conditional_covariance_order_min_eigenvalue"
            ].min()
            >= gates["minimum_loewner_order_eigenvalue"]
            and information["bayes_risk_violation"].max() <= 1e-10
        ),
        "route_nonontology": bool(
            route["licensed_specialization_claim"].mean()
            <= gates["maximum_route_false_ontology_rate"]
            and route["naive_specialization_claim"].mean()
            >= gates["minimum_naive_route_heterogeneity_rate"]
        ),
        "shared_relational_lift": bool(
            _quantile(
                shared["raw_relation_element_correlation"],
                0.05,
            )
            >= gates["minimum_shared_relation_q05"]
            and _quantile(
                shared["mean_individual_correlation"],
                0.95,
            )
            <= gates["maximum_shared_mean_individual_q95"]
            and shared["licensed_structural_connection"].mean()
            >= gates["minimum_shared_relation_license_rate"]
        ),
        "confound_refusal": bool(
            nuisance["licensed_structural_connection"].mean()
            <= gates["maximum_confound_relation_license_rate"]
        ),
        "reference_specificity": bool(
            _quantile(
                reference["fixed_origin_shift_cosine"],
                0.05,
            )
            >= gates["minimum_reference_shift_cosine_q05"]
            and _quantile(
                reference["fixed_origin_amplitude_error"],
                0.95,
            )
            <= gates["maximum_reference_amplitude_error_q95"]
            and _quantile(
                reference["population_relation_shift_frobenius"],
                0.05,
            )
            >= gates["minimum_population_relation_shift_q05"]
            and reference["reference_mismatch_refusal"].mean()
            >= gates["minimum_reference_mismatch_refusal_rate"]
        ),
    }
    diagnostics = {
        "pooled_coverage": pooled_coverage,
        "naive_route_heterogeneity_rate": float(
            route["naive_specialization_claim"].mean()
        ),
        "licensed_route_false_ontology_rate": float(
            route["licensed_specialization_claim"].mean()
        ),
        "shared_relation_q05": _quantile(
            shared["raw_relation_element_correlation"],
            0.05,
        ),
        "shared_individual_q95": _quantile(
            shared["mean_individual_correlation"],
            0.95,
        ),
        "shared_license_rate": float(
            shared["licensed_structural_connection"].mean()
        ),
        "confound_license_rate": float(
            nuisance["licensed_structural_connection"].mean()
        ),
        "max_dpi_violation_bits": float(
            information["dpi_violation_bits"].max()
        ),
        "minimum_loewner_eigenvalue": float(
            information[
                "conditional_covariance_order_min_eigenvalue"
            ].min()
        ),
        "reference_shift_cosine_q05": _quantile(
            reference["fixed_origin_shift_cosine"],
            0.05,
        ),
        "reference_amplitude_error_q95": _quantile(
            reference["fixed_origin_amplitude_error"],
            0.95,
        ),
        "population_relation_shift_q05": _quantile(
            reference["population_relation_shift_frobenius"],
            0.05,
        ),
    }
    summaries = {
        "component": component_summary,
        "commutation": commutation_summary,
        "refusal": refusal_summary,
    }
    return {
        "checks": checks,
        "diagnostics": diagnostics,
        "all_pass": bool(all(checks.values())),
    }, summaries


def _markdown_table(frame: pd.DataFrame) -> str:
    return frame.to_markdown(index=False, floatfmt=".4f")


def _build_report(
    *,
    config: dict[str, Any],
    repetitions: int,
    decision: dict[str, Any],
    summaries: dict[str, pd.DataFrame],
) -> str:
    status = decision["status"]
    diagnostics = decision["diagnostics"]
    checks = decision["checks"]
    lines = [
        "# V8-HJIC-1 Hierarchical Identifiability Report",
        "",
        f"Status: `{status}`",
        "",
        "## Scope",
        "",
        "This synthetic battery tests the typed SUICA graph without reading "
        "human text or external personality labels. Latent author-process "
        "objects, measurement estimates, uncertainty/refusal, population "
        "lifts, and external readouts remain separate object types.",
        "",
        f"Repetitions: {repetitions}.",
        "",
        "## Component recovery",
        "",
        _markdown_table(summaries["component"]),
        "",
        "## Commutation",
        "",
        _markdown_table(summaries["commutation"]),
        "",
        "## Alias refusal",
        "",
        _markdown_table(summaries["refusal"]),
        "",
        "## Key diagnostics",
        "",
        f"- Pooled nominal-95% coverage: "
        f"{diagnostics['pooled_coverage']:.4f}.",
        f"- Naive route-heterogeneity rate: "
        f"{diagnostics['naive_route_heterogeneity_rate']:.4f}; licensed "
        f"false-ontology rate: "
        f"{diagnostics['licensed_route_false_ontology_rate']:.4f}.",
        f"- Shared-latent relation-pattern q05: "
        f"{diagnostics['shared_relation_q05']:.4f}; individual-correlation "
        f"q95: {diagnostics['shared_individual_q95']:.4f}.",
        f"- Shared-latent license rate: "
        f"{diagnostics['shared_license_rate']:.4f}; common-nuisance license "
        f"rate: {diagnostics['confound_license_rate']:.4f}.",
        f"- Maximum frozen-map DPI violation: "
        f"{diagnostics['max_dpi_violation_bits']:.6g} bits.",
        f"- Reference-shift cosine q05: "
        f"{diagnostics['reference_shift_cosine_q05']:.4f}; amplitude-error "
        f"q95: {diagnostics['reference_amplitude_error_q95']:.4f}.",
        "",
        "## Gates",
        "",
    ]
    lines.extend(
        f"- `{name}`: {'PASS' if passed else 'FAIL'}"
        for name, passed in checks.items()
    )
    lines.extend([
        "",
        "## Ruling",
        "",
        "Passing this battery licenses only a synthetic typed-graph "
        "implementation. It shows recovery in an identifiable design, "
        "refusal under observational equivalence, correct frozen-map "
        "information ordering, and separation of route behavior from "
        "ontology. It does not establish that any technical component is "
        "personality or that the graph transports to human language.",
        "",
        f"Claim boundary: {config['claim_boundary']}",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--jobs", type=int)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    config_path = args.config.resolve()
    config = _read_json(config_path)
    repetitions = int(args.repetitions or config["repetitions"])
    jobs = int(args.jobs or config["jobs"])
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)

    script_path = Path(__file__).resolve()
    core_path = (
        ROOT / "suica_core" / "v8_hierarchical_identifiability.py"
    )
    write_run_manifest(
        output / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=config_path,
        code_paths=[script_path, core_path],
        estimand_id=str(config["estimand_id"]),
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )

    payloads = [
        (repetition, int(config["seed"]), dict(config["spec"]))
        for repetition in range(repetitions)
    ]
    if jobs == 1:
        outputs = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as pool:
            outputs = list(pool.map(_worker, payloads))
    tables = _aggregate(outputs, seed=int(config["seed"]))

    file_map = {
        "component": "component_recovery.csv",
        "commutation": "commutation_defects.csv",
        "coverage": "uncertainty_coverage.csv",
        "refusal": "refusal_calibration.csv",
        "information": "information_order.csv",
        "route": "route_nonontology.csv",
        "relation": "relational_lift.csv",
        "reference": "reference_drift.csv",
    }
    for key, filename in file_map.items():
        tables[key].to_csv(output / filename, index=False)

    gate_result, summaries = _evaluate_gates(
        tables,
        dict(config["gates"]),
    )
    status = (
        "V8_HJIC1_SYNTHETIC_TYPED_GRAPH_PASS"
        if gate_result["all_pass"]
        else "V8_HJIC1_SYNTHETIC_TYPED_GRAPH_PARTIAL"
    )
    decision = {
        "version": str(config["version"]),
        "estimand_id": str(config["estimand_id"]),
        "status": status,
        "completed_utc": datetime.now(UTC).isoformat(),
        "repetitions": repetitions,
        "external_labels_read": False,
        **gate_result,
        "claim_boundary": str(config["claim_boundary"]),
    }
    _write_json(output / "decision.json", decision)
    report_text = _build_report(
        config=config,
        repetitions=repetitions,
        decision=decision,
        summaries=summaries,
    )
    (output / "REPORT.md").write_text(report_text, encoding="utf-8")
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
