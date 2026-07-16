#!/usr/bin/env python3
"""Fit and replay the V7 geometry bundle on frozen author-feature splits.

The script reads an existing identifier-bearing feature table but persists
only an identifier-free bundle and aggregate split summaries.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_geometry import fit_geometry_bundle, score_geometry_bundle  # noqa: E402
from suica_core.v7_governance import (  # noqa: E402
    append_ledger_event,
    sha256_file,
    write_artifact_inventory,
    write_run_manifest,
)


def _summary(split: str, result: dict[str, object]) -> tuple[dict[str, object], list[dict[str, object]]]:
    statuses = np.asarray(result["status"], dtype=object)
    ready = statuses == "GEOMETRY_PROFILE_READY"
    support = {
        "split": split,
        "n_rows": int(len(statuses)),
        "n_ready": int(ready.sum()),
        "ready_rate": float(ready.mean()) if len(ready) else 0.0,
        "n_outside_reference_radial_envelope": int(
            (statuses == "GEOMETRY_REFUSE_OUTSIDE_REFERENCE_RADIAL_ENVELOPE").sum()
        ),
        "n_insufficient_observation_support": int((statuses == "GEOMETRY_REFUSE_INSUFFICIENT_OBSERVATION_SUPPORT").sum()),
    }
    rows: list[dict[str, object]] = []
    for metric in ("nearest_landmark_distance", "mean_landmark_distance", "reference_radius"):
        values = np.asarray(result[metric], dtype=float)[ready]
        row: dict[str, object] = {"split": split, "metric": metric, "n_ready": int(len(values))}
        for quantile in (0.05, 0.25, 0.5, 0.75, 0.95):
            row[f"q{int(quantile * 100):02d}"] = float(np.quantile(values, quantile)) if len(values) else np.nan
        rows.append(row)
    return support, rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--upstream-manifest", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "v7_geometry_smoke.json")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    frame = pd.read_csv(args.input)
    required = {"split", "n_units"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Author-feature table missing columns: {missing}")
    feature_names = [
        str(column)
        for column in frame.columns
        if any(str(column).startswith(prefix) for prefix in config["feature_prefixes"])
    ]
    if not feature_names:
        raise ValueError("No configured numeric feature columns were found.")
    discovery = frame.loc[frame["split"].astype(str).eq("discovery")].copy()
    if len(discovery) < 2:
        raise ValueError("At least two discovery authors are required.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[args.input, args.upstream_manifest],
        config_path=args.config,
        code_paths=[Path(__file__), ROOT / "suica_core" / "v7_geometry.py"],
        estimand_id="V7-relative-landmark-geometry-real-data-smoke",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    bundle = fit_geometry_bundle(
        discovery[feature_names].to_numpy(float),
        feature_names=feature_names,
        operator={"id": str(config["operator_id"]), "source": "frozen_upstream_author_features"},
        representation={"id": str(config["representation_id"]), "feature_count": len(feature_names)},
        runtime_artifact={"upstream_manifest_sha256": sha256_file(args.upstream_manifest)},
        reference_population={
            "cohort_commitment": sha256_file(args.input),
            "n_authors": int(len(discovery)),
            "role": "discovery_reference_only",
        },
        min_units_for_score=int(config["min_units_for_score"]),
        landmark_count=int(config["landmark_count"]),
        regularization=float(config["regularization"]),
        support_radius_quantile=float(config["support_radius_quantile"]),
        version=str(config["version"]),
    )
    bundle.write_json(args.output_dir / "geometry_bundle.json")

    support_rows: list[dict[str, object]] = []
    distribution_rows: list[dict[str, object]] = []
    for split in ("discovery", "calibration", "confirmation"):
        panel = frame.loc[frame["split"].astype(str).eq(split)]
        result = score_geometry_bundle(
            bundle,
            panel[feature_names].to_numpy(float),
            unit_counts=panel["n_units"].to_numpy(int),
        )
        support, distributions = _summary(split, result)
        support_rows.append(support)
        distribution_rows.extend(distributions)
    support_table = pd.DataFrame(support_rows)
    distribution_table = pd.DataFrame(distribution_rows)
    support_table.to_csv(args.output_dir / "support_summary.csv", index=False)
    distribution_table.to_csv(args.output_dir / "profile_distribution_summary.csv", index=False)
    heldout = support_table.loc[support_table["split"].isin(["calibration", "confirmation"])]
    decision = {
        "status": "GEOMETRY_BUNDLE_REAL_DATA_SMOKE_COMPLETE",
        "bundle_id": bundle.bundle_id,
        "heldout_ready_rate_min": float(heldout["ready_rate"].min()),
        "identifiers_persisted": False,
        "external_labels_read": False,
        "claim_boundary": (
            "Executable held-out reference-relative geometry only. No factor, "
            "reliability, personality, clinical, or cross-domain validity claim."
        ),
    }
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    manifest.update(decision)
    (args.output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    append_ledger_event(
        args.output_dir / "evidence_ledger.jsonl",
        {"estimand_id": manifest["estimand_id"], **decision},
    )
    inventory = write_artifact_inventory(args.output_dir, args.output_dir / "artifact_inventory.json")
    print(json.dumps({"status": decision["status"], "artifact_files": inventory["n_files"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
