#!/usr/bin/env python3
"""Build the deidentified SUICA v0.2.1 evidence bundle and lockbox manifest.

Minimal adaptation of scripts/build_suica_v020_release_bundle.py for the
v0.2.1 remediation release (2026-07-17 process-audit corrections). It writes
ONLY under release/v0.2.1/ — release/v0.2.0/ is an immutable historical
record and is never touched. The v0.2.0 manifest, test report, and evidence
snapshots are additionally SEALED (hashed) inside the v0.2.1 manifest so any
future modification of the historical record fails v0.2.1 verification.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_release import build_lockbox_manifest, sha256_file  # noqa: E402

RELEASE_VERSION = "0.2.1"
RELEASE_ROOT = ROOT / "release" / "v0.2.1"
EVIDENCE_ROOT = RELEASE_ROOT / "evidence"

# Same frozen source runs as v0.2.0: the remediation cycle corrected process,
# labels, and documentation; no evidence artifact was recomputed.
EVIDENCE_SPECS = {
    "W2_IDENTIFICATION": {
        "root": ROOT / "results" / "v7_identification" / "w2_corrected_full_20260715",
        "decision": "decision.json",
        "tables": ["summary.csv"],
    },
    "W3_TEMPORAL_RANDOM": {
        "root": ROOT / "results" / "v7_temporal_geometry" / "w3_temporal_random_corrected_full_20260715",
        "decision": "decision.json",
        "tables": ["temporal_random_contrast.csv"],
    },
    "W4_MULTIVIEW_METHODS": {
        "root": ROOT / "results" / "v7_multiview_benchmark" / "w4b_corrected_full_20260715",
        "decision": "decision.json",
        "tables": ["confirmation_method_summary.csv", "paired_method_differences.csv"],
    },
    "W4B_EFFECTIVE_RANK": {
        "root": ROOT / "results" / "v7_multiview_spectrum" / "w4b_effective_rank_corrected_20260715",
        "decision": "decision.json",
        "tables": ["effective_rank_profiles.csv"],
    },
    "W7_REPRESENTATION_TRANSPORT": {
        "root": ROOT / "results" / "v7_representation_transport" / "w7_full_20260715",
        "decision": "decision.json",
        "tables": ["summary.csv"],
    },
    "G1_REAL_DATA_GEOMETRY": {
        "root": ROOT / "results" / "v7_geometry" / "g1_corrected_v2_full_20260715",
        "decision": "decision.json",
        "tables": ["support_summary.csv"],
    },
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _evidence_snapshot(evidence_id: str, spec: dict[str, Any]) -> dict[str, Any]:
    source_root = Path(spec["root"])
    decision_path = source_root / str(spec["decision"])
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    tables: dict[str, list[dict[str, str]]] = {}
    source_sha256: dict[str, str] = {decision_path.name: sha256_file(decision_path)}
    for table_name in spec["tables"]:
        table_path = source_root / str(table_name)
        tables[str(table_name)] = _read_csv(table_path)
        source_sha256[str(table_name)] = sha256_file(table_path)
    return {
        "schema_version": "suica-v7-deidentified-evidence-1",
        "release_version": RELEASE_VERSION,
        "evidence_id": evidence_id,
        "status": decision["status"],
        "decision": decision,
        "aggregate_tables": tables,
        "source_artifact_sha256": source_sha256,
        "privacy": {
            "raw_text_included": False,
            "raw_identifiers_included": False,
            "per_person_scores_included": False,
        },
        "replay_scope": (
            "This snapshot verifies the released aggregate claim and source-artifact identity. "
            "Recomputing it from restricted corpora requires separately obtained source data."
        ),
    }


def _critical_paths() -> list[str]:
    patterns = (
        "suica_core/v7_*.py",
        "suica_sim/v7*.py",
        "scripts/*v7*.py",
        "configs/v7*.json",
        "schemas/v7*.json",
        "tests/test_v7*.py",
        "tests/test_v6_pipeline_power.py",
        "docs/V7*.md",
        "reports/V7*.md",
        "release/v0.2.1/evidence/*.json",
        # Seal the immutable v0.2.0 historical record inside this release.
        "release/v0.2.0/evidence/*.json",
    )
    paths: set[str] = set()
    for pattern in patterns:
        paths.update(
            str(path.relative_to(ROOT))
            for path in ROOT.glob(pattern)
            if path.is_file() and not path.name.startswith("._")
        )
    paths.update({
        "CITATION.cff",
        "README.md",
        "README.ja.md",
        "README.zh.md",
        "requirements-lock-v0.2.0.txt",
        ".gitignore",
        ".github/workflows/ci.yml",
        "release/v0.2.0/LOCKBOX_MANIFEST.json",
        "release/v0.2.0/TEST_REPORT.md",
        "release/v0.2.1/TEST_REPORT.md",
        "reports/README.md",
        "scripts/build_suica_v020_release_bundle.py",
        "scripts/verify_suica_v020_lockbox.py",
        "scripts/build_suica_v021_release_bundle.py",
        "scripts/verify_suica_v021_lockbox.py",
        "suica_core/__init__.py",
        "docs/CLAIMS_LEDGER.md",
        "docs/OPEN_PROBLEMS.md",
        "docs/PREREGISTRATION.md",
        "docs/PAPER2_MOTION_SKELETON.md",
        "docs/THEORY_FORMAL_NOTES_V3.md",
        "docs/THEORY_V6.md",
        "docs/WORKED_EXAMPLE_MANUAL.md",
        "docs/V7_LOCKBOX_V020.md",
        "docs/RELEASE_NOTES_V020.md",
        "docs/RELEASE_NOTES_V021.md",
    })
    return sorted(paths)


def main() -> None:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    for evidence_id, spec in EVIDENCE_SPECS.items():
        snapshot = _evidence_snapshot(evidence_id, spec)
        destination = EVIDENCE_ROOT / f"{evidence_id.lower()}.json"
        destination.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = build_lockbox_manifest(ROOT, _critical_paths(), release_version=RELEASE_VERSION)
    destination = RELEASE_ROOT / "LOCKBOX_MANIFEST.json"
    destination.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "BUILT", "manifest": str(destination), "n_files": manifest["n_files"]}))


if __name__ == "__main__":
    main()
