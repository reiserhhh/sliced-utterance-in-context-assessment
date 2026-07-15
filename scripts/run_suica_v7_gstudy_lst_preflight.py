#!/usr/bin/env python3
"""Screen a future repeated SUICA study for G-study/LST eligibility.

No score model is fitted. The script creates a privacy-safe design audit and
refuses historical text that lacks randomized, repeated, frozen-runtime cells.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import append_ledger_event, write_artifact_inventory, write_run_manifest  # noqa: E402
from suica_core.v7_measurement_preflight import validate_repeated_measurement_design  # noqa: E402


def _read(path: Path) -> pd.DataFrame:
    """Load a supported local measurement-design table."""
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=True)
    return pd.read_csv(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[args.input],
        config_path=Path(__file__),
        code_paths=[Path(__file__), ROOT / "suica_core" / "v7_measurement_preflight.py"],
        estimand_id="V7.4-W5-repeated-measurement-design-preflight",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    summary, coverage, plan = validate_repeated_measurement_design(_read(args.input))
    (args.output_dir / "measurement_design_preflight.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    coverage.to_csv(args.output_dir / "component_design_coverage.csv", index=False)
    (args.output_dir / "variance_component_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest.update({
        "external_labels_read": False,
        "raw_identifiers_persisted": False,
        "preflight_status": summary["status"],
        "claim_boundary": summary["claim_boundary"],
    })
    (args.output_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    append_ledger_event(args.output_dir / "evidence_ledger.jsonl", {"estimand_id": manifest["estimand_id"], "status": summary["status"], "claim_boundary": summary["claim_boundary"]})
    inventory = write_artifact_inventory(args.output_dir, args.output_dir / "artifact_inventory.json")
    print(json.dumps({"status": summary["status"], "output_dir": str(args.output_dir), "artifact_files": inventory["n_files"]}, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "REPEATED_MEASUREMENT_DESIGN_READY_FOR_GSTUDY_LST" else 2


if __name__ == "__main__":
    raise SystemExit(main())
