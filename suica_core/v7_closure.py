"""Machine-auditable closure logic for the SUICA V7 theoretical core."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from suica_core.v7_governance import git_revision, verify_artifact_inventory, verify_run_manifest
from suica_core.v7_release import verify_lockbox_manifest, verify_release_identity


def audit_v7_theory_closure(config: dict[str, Any], *, repository_root: str | Path) -> dict[str, Any]:
    """Verify registered evidence and protocols without upgrading empirical claims."""
    root = Path(repository_root).resolve()
    failures: list[dict[str, str]] = []
    evidence_rows: list[dict[str, Any]] = []

    for relative in config.get("required_files", []):
        path = root / str(relative)
        if not path.is_file():
            failures.append({"item": str(relative), "reason": "required_file_missing"})

    release_manifest_result: dict[str, Any] | None = None
    release_identity_result: dict[str, Any] | None = None
    if config.get("release_manifest"):
        manifest_path = root / str(config["release_manifest"])
        if not manifest_path.is_file():
            failures.append({"item": "release_manifest", "reason": "release_manifest_missing"})
        else:
            release_manifest_result = verify_lockbox_manifest(manifest_path, repository_root=root)
            if release_manifest_result["status"] != "LOCKBOX_MANIFEST_PASS":
                failures.append({"item": "release_manifest", "reason": "release_manifest_failed"})
            if config.get("release_tag"):
                release_identity_result = verify_release_identity(
                    root,
                    manifest_path,
                    tag=str(config["release_tag"]),
                )

    for item in config.get("evidence", []):
        evidence_id = str(item["id"])
        decision_path = root / str(item["decision"])
        if not decision_path.is_file():
            failures.append({"item": evidence_id, "reason": "decision_missing"})
            continue
        decision = json.loads(decision_path.read_text(encoding="utf-8"))
        status = str(decision.get("status"))
        allowed = {str(value) for value in item.get("allowed_statuses", [])}
        if status not in allowed:
            failures.append({"item": evidence_id, "reason": f"unexpected_status:{status}"})

        manifest_result: dict[str, Any] | None = None
        inventory_result: dict[str, Any] | None = None
        if item.get("run_manifest"):
            manifest_result = verify_run_manifest(root / str(item["run_manifest"]))
            if manifest_result["status"] != "RUN_MANIFEST_PASS":
                failures.append({"item": evidence_id, "reason": "run_manifest_failed"})
        if item.get("artifact_inventory"):
            inventory_result = verify_artifact_inventory(root / str(item["artifact_inventory"]))
            if inventory_result["status"] != "INVENTORY_PASS":
                failures.append({"item": evidence_id, "reason": "artifact_inventory_failed"})
        evidence_rows.append({
            "id": evidence_id,
            "status": status,
            "run_manifest_status": None if manifest_result is None else manifest_result["status"],
            "artifact_inventory_status": None if inventory_result is None else inventory_result["status"],
        })

    revision = git_revision(root)
    if failures:
        closure_status = "REFUSE_V7_THEORY_CLOSURE_AUDIT_FAILURE"
    elif (
        revision.get("status") != "GIT_AVAILABLE"
        or revision.get("dirty") is not False
        or release_identity_result is None
        or release_identity_result.get("status") != "RELEASE_IDENTITY_PASS"
    ):
        closure_status = "V7_THEORETICAL_CORE_IMPLEMENTED_DURABLE_SNAPSHOT_PENDING"
    else:
        closure_status = "V7_THEORETICAL_CORE_CLOSED_WITH_EMPIRICAL_GATES"

    return {
        "status": closure_status,
        "n_failures": len(failures),
        "failures": failures,
        "evidence": evidence_rows,
        "repository": revision,
        "release_manifest": release_manifest_result,
        "release_identity": release_identity_result,
        "evidence_lattice": {
            "geometry": "IMPLEMENTED_AND_HELDOUT_SMOKED",
            "conditional_uncertainty": "PROTOCOL_IMPLEMENTED_EMPIRICAL_JOINT_ESTIMATE_PENDING",
            "repeated_measurement_reliability": "FUTURE_DATA_REQUIRED",
            "external_construct_validity": "FUTURE_DATA_REQUIRED",
            "cross_domain_transport": "LOCAL_REFERENCE_ONLY_PAIRED_ALIGNMENT_PENDING",
        },
        "claim_boundary": (
            "Closure applies to the executable theoretical and refusal framework. "
            "It does not establish personality factors, reliability, clinical validity, "
            "universal language invariance, or market prediction."
        ),
    }
