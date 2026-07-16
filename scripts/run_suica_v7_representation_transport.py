#!/usr/bin/env python3
"""Calibrate when V7 geometry procedures can and cannot cross a domain map."""
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
from suica_sim.v7_representation_transport import run_transport_matrix  # noqa: E402


def _summary(frame: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "paired_relative_distance_spearman", "naive_coordinate_r2", "naive_retrieval_accuracy",
        "procrustes_coordinate_r2", "procrustes_retrieval_accuracy", "affine_coordinate_r2",
        "affine_retrieval_accuracy", "separate_whitened_distance_spearman",
        "source_target_covariance_frobenius_gap",
    ]
    rows: list[dict[str, float | str | int]] = []
    for world, group in frame.groupby("world", observed=True, sort=True):
        for metric in metrics:
            values = pd.to_numeric(group[metric], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().to_numpy(float)
            if len(values):
                rows.append({"world": str(world), "metric": metric, "n": int(len(values)), "mean": float(values.mean()), "q025": float(np.quantile(values, 0.025)), "q975": float(np.quantile(values, 0.975))})
    return pd.DataFrame(rows)


def _value(summary: pd.DataFrame, world: str, metric: str, field: str) -> float:
    values = summary.loc[summary["world"].eq(world) & summary["metric"].eq(metric), field]
    return float(values.iloc[0]) if len(values) else float("nan")


def _decision(summary: pd.DataFrame, gates: dict[str, float]) -> dict[str, object]:
    checks = {
        "common_coordinate_naive_retrieval": _value(summary, "common_coordinate", "naive_retrieval_accuracy", "q025") >= float(gates["min_common_coordinate_retrieval"]),
        "rotation_requires_paired_alignment": (
            _value(summary, "unknown_rotation", "naive_retrieval_accuracy", "q975") <= float(gates["max_rotation_naive_retrieval"])
            and _value(summary, "unknown_rotation", "procrustes_retrieval_accuracy", "q025") >= float(gates["min_paired_alignment_retrieval"])
        ),
        "affine_requires_paired_alignment": (
            _value(summary, "unknown_affine", "naive_coordinate_r2", "q975") <= float(gates["max_affine_naive_r2"])
            and _value(summary, "unknown_affine", "affine_retrieval_accuracy", "q025") >= float(gates["min_paired_alignment_retrieval"])
        ),
        "unpaired_orientation_refusal_declared": True,
    }
    return {
        "status": "REPRESENTATION_TRANSPORT_CALIBRATION_PASS" if all(checks.values()) else "REFUSE_TRANSPORT_CALIBRATION",
        "checks": checks,
        "claim_boundary": (
            "Synthetic transport calibration only. A frozen SUICA procedure may be reused in a target domain, "
            "but source numerical coordinates, landmarks, norms and factor labels are not transferable without "
            "the appropriate paired or independently validated alignment evidence."
        ),
    }


def _report(path: Path, *, summary: pd.DataFrame, decision: dict[str, object], output_dir: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    checks = "\n".join(f"- {name}: {value}" for name, value in decision["checks"].items())
    path.write_text(
        "# SUICA V7 Representation Transport Calibration\n\n"
        "## Scope\n\n"
        "This synthetic matrix distinguishes reuse of a frozen geometry procedure from identification of a source-to-target coordinate map. It contains no language, market, personality or clinical labels.\n\n"
        f"## Results\n\n{summary.to_markdown(index=False, floatfmt='.4f')}\n\n"
        f"## Gates\n\nStatus: {decision['status']}\n\n{checks}\n\n"
        "## Interpretation\n\n"
        "Pairwise within-domain geometry can survive an unknown rotation while naive source-coordinate retrieval fails. Paired anchors recover an orthogonal or affine map only in the world where those anchors are supplied. An unpaired isotropic target can have the same distribution under multiple rotations, so no numerical source-coordinate comparison is identified from unpaired target text alone. This fixes the later market/language boundary: reuse the V7 procedure with a target-local reference, or collect a declared bridge and test it on held-out anchors.\n\n"
        f"Artifacts: {output_dir}\n",
        encoding="utf-8",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "sim_v7" / "representation_transport_full.json")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help=(
            "Report destination. Defaults to an untracked path inside the run's results/ "
            "output directory so a rerun never dirties the tracked reports/ tree (which "
            "would flip the release closure ruling). Pass this flag explicitly to publish "
            "into tracked reports/."
        ),
    )
    parser.add_argument("--quick", action="store_true")
    return parser


def _default_report_path(output_dir: Path) -> Path:
    """Untracked default report location (results/ is gitignored)."""
    return output_dir / "V7_REPRESENTATION_TRANSPORT_CALIBRATION.md"


def main() -> int:
    args = _build_parser().parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if args.quick:
        config["repetitions"] = min(20, int(config["repetitions"]))
        config["persons"] = min(120, int(config["persons"]))
    run_id = datetime.now(UTC).strftime("w7_transport_%Y%m%d_%H%M%S")
    output_dir = args.output_dir or ROOT / "results" / "v7_representation_transport" / run_id
    report = args.report or _default_report_path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = write_run_manifest(
        output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[args.config],
        config_path=args.config,
        code_paths=[Path(__file__), ROOT / "suica_sim" / "v7_representation_transport.py"],
        estimand_id="V7.4-representation-transport-calibration",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    rows = pd.DataFrame(run_transport_matrix(config))
    summary = _summary(rows)
    decision = _decision(summary, config["gates"])
    rows.to_csv(output_dir / "per_trial.csv", index=False)
    summary.to_csv(output_dir / "summary.csv", index=False)
    (output_dir / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _report(report, summary=summary, decision=decision, output_dir=output_dir)
    append_ledger_event(output_dir / "evidence_ledger.jsonl", {"estimand_id": manifest["estimand_id"], "status": decision["status"], "claim_boundary": decision["claim_boundary"]})
    write_artifact_inventory(output_dir, output_dir / "artifact_inventory.json")
    print(json.dumps({"status": decision["status"], "output_dir": str(output_dir), "report": str(report)}, ensure_ascii=False, indent=2))
    return 0 if decision["status"] == "REPRESENTATION_TRANSPORT_CALIBRATION_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
