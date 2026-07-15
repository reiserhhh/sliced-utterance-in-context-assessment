#!/usr/bin/env python3
"""Calibrate V7 geometry estimators in declared synthetic identification worlds."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import append_ledger_event, write_artifact_inventory, write_run_manifest  # noqa: E402
from suica_sim.v7_identification import run_identification_matrix  # noqa: E402


def _summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize every world with means and empirical 95 percent intervals."""
    metrics = [
        "alignment_auc", "relative_distance_spearman", "linear_transport_r2",
        "residual_alignment_auc", "raw_subspace_congruence",
        "context_adjusted_subspace_congruence", "rotation_max_abs_error",
    ]
    rows: list[dict[str, float | str | int]] = []
    for world, group in frame.groupby("world", observed=True, sort=True):
        for metric in metrics:
            values = group[metric].replace([np.inf, -np.inf], np.nan).dropna().to_numpy(float)
            if not len(values):
                continue
            rows.append({
                "world": str(world), "metric": metric, "n": int(len(values)),
                "mean": float(np.mean(values)), "q025": float(np.quantile(values, 0.025)),
                "q975": float(np.quantile(values, 0.975)),
            })
    return pd.DataFrame(rows)


def _value(summary: pd.DataFrame, world: str, metric: str, field: str) -> float:
    rows = summary.loc[summary["world"].eq(world) & summary["metric"].eq(metric), field]
    return float(rows.iloc[0]) if len(rows) else float("nan")


def _decision(summary: pd.DataFrame, gates: dict[str, float]) -> dict[str, object]:
    """Apply simulation-only calibration gates without interpreting human text."""
    checks = {
        "rotation_equivalence_exact": _value(summary, "axis_rotation_equivalence", "rotation_max_abs_error", "q975") <= float(gates["max_rotation_error"]),
        "shared_context_adjusted_subspace_recovery": (
            _value(summary, "shared_linear", "context_adjusted_subspace_congruence", "q025")
            >= float(gates["min_shared_context_adjusted_subspace_congruence"])
        ),
        "null_alignment_control": _value(summary, "null", "alignment_auc", "q975") <= float(gates["max_null_alignment_auc"]),
        "nonlinear_relative_geometry_linear_separation": (
            _value(summary, "nonlinear_metric_without_linear_coordinate", "relative_distance_spearman", "q025")
            >= float(gates["min_nonlinear_relative_distance_spearman"])
            and _value(summary, "nonlinear_metric_without_linear_coordinate", "linear_transport_r2", "q975") <= float(gates["max_nonlinear_linear_r2"])
        ),
        "omitted_context_counterexample": _value(summary, "omitted_context_counterexample", "residual_alignment_auc", "q025") >= float(gates["min_omitted_context_residual_auc"]),
        "endogenous_context_overadjustment_counterexample": (
            _value(summary, "endogenous_context_overadjustment_counterexample", "context_adjusted_subspace_congruence", "q975")
            <= _value(summary, "endogenous_context_overadjustment_counterexample", "raw_subspace_congruence", "q025")
        ),
        "measurement_error_context_counterexample": (
            _value(summary, "measurement_error_context_counterexample", "residual_alignment_auc", "q025")
            >= float(gates["min_measurement_error_context_residual_auc"])
        ),
    }
    return {
        "status": "IDENTIFICATION_CALIBRATION_PASS" if all(checks.values()) else "REFUSE_ESTIMATOR_UNCALIBRATED",
        "checks": checks,
        "claim_boundary": "Synthetic calibration only. Counterexamples demonstrate non-identifiability boundaries; they do not describe human personality or PANDORA authors.",
    }


def _write_report(path: Path, *, config: dict, summary: pd.DataFrame, decision: dict, output_dir: Path) -> None:
    """Write a compact human-readable calibration report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    checks = "\n".join(f"- `{name}`: `{value}`" for name, value in decision["checks"].items())
    path.write_text(
        "# SUICA V7 Identification Calibration Matrix\n\n"
        "## Scope\n\n"
        "This is a synthetic calibration. It tests when V7-style subspace, linear-map, residual, and own-vs-stranger statistics recover or fail under known data-generating worlds. It contains no human text or psychological labels.\n\n"
        "## Results\n\n"
        f"{summary.to_markdown(index=False, floatfmt='.4f')}\n\n"
        "## Gates\n\n"
        f"Status: `{decision['status']}`\n\n{checks}\n\n"
        "## Interpretation\n\n"
        "Exact rotation equivalence is a mathematical non-identifiability certificate: stable subspaces do not identify named axes. Recovery truth is transformed into the same standardized feature coordinates used by the estimator. The raw cross-view subspace is reported separately because shared observed context can displace the true shared subspace; the train-fitted context-adjusted estimate only recovers it in the declared exogenous-context world. Omitted, noisy, and endogenous context worlds demonstrate why residual author alignment is not sufficient to identify an author core and why there is no unconditional residualization rule. The nonlinear world demonstrates that pairwise relative geometry and fixed linear coordinate transport are separate estimands.\n\n"
        f"Artifacts: `{output_dir}`\n",
        encoding="utf-8",
    )


def main() -> int:
    """Run a fully declared V7 synthetic calibration matrix."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "sim_v7" / "identification_full.json")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if args.quick:
        config["repetitions"] = min(16, int(config["repetitions"]))
        config["persons"] = min(120, int(config["persons"]))
    run_id = datetime.now(UTC).strftime("w2_%Y%m%d_%H%M%S")
    output_dir = args.output_dir or ROOT / "results" / "v7_identification" / run_id
    report = args.report or ROOT / "reports" / "V7_IDENTIFICATION_CALIBRATION.md"
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = write_run_manifest(
        output_dir / "run_manifest.json", repository_root=ROOT, input_paths=[args.config], config_path=args.config,
        code_paths=[Path(__file__), ROOT / "suica_sim" / "v7_identification.py"],
        estimand_id="V7.3-W2-identification-calibration", external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    rows = pd.DataFrame(run_identification_matrix(config))
    summary = _summary(rows)
    decision = _decision(summary, config["gates"])
    rows.to_csv(output_dir / "per_trial.csv", index=False)
    summary.to_csv(output_dir / "summary.csv", index=False)
    (output_dir / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_report(report, config=config, summary=summary, decision=decision, output_dir=output_dir)
    append_ledger_event(output_dir / "evidence_ledger.jsonl", {
        "estimand_id": manifest["estimand_id"], "status": decision["status"],
        "claim_boundary": decision["claim_boundary"],
    })
    inventory = write_artifact_inventory(output_dir, output_dir / "artifact_inventory.json")
    print(json.dumps({"output_dir": str(output_dir), "report": str(report), "status": decision["status"], "artifact_files": inventory["n_files"]}, ensure_ascii=False, indent=2))
    return 0 if decision["status"] == "IDENTIFICATION_CALIBRATION_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
