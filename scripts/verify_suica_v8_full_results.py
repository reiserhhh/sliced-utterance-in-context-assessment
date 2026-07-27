#!/usr/bin/env python3
"""Verify the frozen inputs, code, artifacts, and decisions of V8.1-V8.4."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


EXPECTED = {
    "v8_1_semantic": "V8_1_DOWNGRADE_RENDERER_ONLY",
    "v8_1_semantic_attempt1_8192": "V8_1_DOWNGRADE_RENDERER_ONLY",
    "v8_2_evidence": "V8_2_EXPLANATION_FIDELITY_PASS",
    "v8_3_simulation": "V8_3_ORACLE_IDENTIFICATION_PASS",
    "v8_4_realtext": "V8_4_SEMANTIC_CANDIDATE_RENDERER_ONLY",
}

CONFIG_SNAPSHOTS = {
    "v8_1_semantic_attempt1_8192": (
        ROOT
        / "configs"
        / "archive"
        / "v8_full_experiment_v8_1_attempt1_4a99f85cd0.json"
    ),
    "v8_2_evidence": (
        ROOT
        / "configs"
        / "archive"
        / "v8_full_experiment_v8_2_v8_3_e1450c4692.json"
    ),
    "v8_3_simulation": (
        ROOT
        / "configs"
        / "archive"
        / "v8_full_experiment_v8_2_v8_3_e1450c4692.json"
    ),
}


def _sha256(path: Path) -> str:
    """Hash one file without loading it into an experiment runtime."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _manifest_path(
    phase: str,
    row: dict[str, Any],
    *,
    phase_dir: Path,
) -> Path:
    """Resolve a manifest row, substituting an exact historical config snapshot."""
    if row["path"] == "configs/v8_full_experiment.json" and phase in CONFIG_SNAPSHOTS:
        return CONFIG_SNAPSHOTS[phase]
    if row.get("path_base") == "repository_root":
        return ROOT / row["path"]
    return phase_dir / row["path"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "results" / "v8_full",
    )
    args = parser.parse_args()
    output_root = (
        args.output_root.resolve()
        if args.output_root.is_absolute()
        else (ROOT / args.output_root).resolve()
    )
    rows: list[dict[str, Any]] = []
    phase_rows: list[dict[str, Any]] = []
    for phase, expected_status in EXPECTED.items():
        phase_dir = output_root / phase
        manifest = json.loads((phase_dir / "manifest.json").read_text(encoding="utf-8"))
        decision = json.loads((phase_dir / "decision.json").read_text(encoding="utf-8"))
        status_ok = (
            decision.get("status") == expected_status
            and manifest.get("status") == expected_status
        )
        phase_rows.append({
            "phase": phase,
            "expected_status": expected_status,
            "decision_status": decision.get("status", "MISSING"),
            "manifest_status": manifest.get("status", "MISSING"),
            "status_ok": status_ok,
        })
        for group in ("inputs", "code"):
            for item in manifest.get(group, []):
                resolved = _manifest_path(
                    phase,
                    item,
                    phase_dir=phase_dir,
                )
                observed = _sha256(resolved) if resolved.exists() else ""
                rows.append({
                    "phase": phase,
                    "kind": group,
                    "declared_path": item["path"],
                    "resolved_path": str(resolved.relative_to(ROOT))
                    if resolved.is_relative_to(ROOT)
                    else str(resolved),
                    "expected_sha256": item["sha256"],
                    "observed_sha256": observed,
                    "ok": observed == item["sha256"],
                })
        inventory = json.loads(
            (phase_dir / "artifact_inventory.json").read_text(encoding="utf-8")
        )
        for item in inventory.get("files", []):
            resolved = phase_dir / item["path"]
            observed = _sha256(resolved) if resolved.exists() else ""
            rows.append({
                "phase": phase,
                "kind": "artifact",
                "declared_path": item["path"],
                "resolved_path": str(resolved.relative_to(ROOT)),
                "expected_sha256": item["sha256"],
                "observed_sha256": observed,
                "ok": observed == item["sha256"],
            })
    details = pd.DataFrame(rows)
    phases = pd.DataFrame(phase_rows)
    final = json.loads(
        (output_root / "final_decision.json").read_text(encoding="utf-8")
    )
    final_ok = final.get("status") == "V8_TECHNICAL_CORE_NOT_CLOSED"
    passed = bool(details["ok"].all() and phases["status_ok"].all() and final_ok)
    decision = {
        "status": "V8_FULL_PROVENANCE_PASS" if passed else "V8_FULL_PROVENANCE_FAIL",
        "checked_files": int(len(details)),
        "failed_files": int((~details["ok"]).sum()),
        "phase_statuses_ok": bool(phases["status_ok"].all()),
        "final_decision_ok": final_ok,
    }
    details.to_csv(output_root / "provenance_checks.csv", index=False)
    (output_root / "provenance_audit.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = (
        "# SUICA V8 Full Provenance Audit\n\n"
        f"Status: `{decision['status']}`\n\n"
        f"Checked frozen inputs, code, and inventoried artifacts: "
        f"{decision['checked_files']}; failures: {decision['failed_files']}.\n\n"
        "Historical shared-config commitments are resolved through exact "
        "content-addressed snapshots in `configs/archive/`.\n\n"
        f"{phases.to_markdown(index=False)}\n"
    )
    (ROOT / "reports" / "V8_FULL_PROVENANCE_AUDIT.md").write_text(
        report,
        encoding="utf-8",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
