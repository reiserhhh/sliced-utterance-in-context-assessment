"""Refusal-first transport eligibility for SUICA V7 relative geometry."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


_MODES = {"LOCAL_REFERENCE_ONLY", "PAIRED_ALIGNMENT", "PRETRAINED_ALIGNMENT"}
_SCHEMA_FIELDS = {"author_id", "document_id", "occasion_id", "rind_id", "timestamp", "language"}
_OPTIONAL_DOCUMENTED = {"occasion_id", "rind_id", "timestamp", "language"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_ready(artifact: Any, *, label: str) -> tuple[bool, str]:
    if not isinstance(artifact, dict) or not isinstance(artifact.get("path"), str) or not isinstance(artifact.get("sha256"), str):
        return False, f"{label}_MISSING_PATH_OR_SHA256"
    path = Path(artifact["path"])
    if not path.is_file():
        return False, f"{label}_MISSING_FILE"
    if _sha256(path) != artifact["sha256"]:
        return False, f"{label}_SHA256_MISMATCH"
    return True, "READY"


def _schema_status(schema: Any) -> tuple[bool, dict[str, str], list[str]]:
    if not isinstance(schema, dict):
        return False, {}, sorted(_SCHEMA_FIELDS)
    missing = sorted(_SCHEMA_FIELDS.difference(schema))
    statuses: dict[str, str] = {}
    for field in _SCHEMA_FIELDS.intersection(schema):
        value = schema[field]
        if not isinstance(value, dict) or not isinstance(value.get("availability"), str):
            missing.append(field)
            continue
        availability = str(value["availability"]).upper()
        if availability not in {"AVAILABLE", "UNAVAILABLE_DOCUMENTED"}:
            missing.append(field)
            continue
        if availability == "AVAILABLE" and not isinstance(value.get("field"), str):
            missing.append(field)
            continue
        if availability == "UNAVAILABLE_DOCUMENTED" and field not in _OPTIONAL_DOCUMENTED:
            missing.append(field)
            continue
        statuses[field] = availability
    return not missing, statuses, sorted(set(missing))


def _base_gate(payload: dict[str, Any]) -> dict[str, Any] | None:
    required = {
        "mode", "source_geometry_bundle", "target_schema", "target_reference_population",
        "target_runtime", "target_local_reference_plan", "measurement_stage_only",
        "market_prediction", "source_reference_reused", "outcome_labels_accessed",
    }
    missing = sorted(required.difference(payload))
    if missing:
        return {"status": "REFUSE_DOMAIN_TRANSPORT_SCHEMA", "missing_fields": missing}
    if str(payload["mode"]) not in _MODES:
        return {"status": "REFUSE_DOMAIN_TRANSPORT_MODE", "allowed_modes": sorted(_MODES)}
    if bool(payload["measurement_stage_only"]) is not True or bool(payload["market_prediction"]) or bool(payload["outcome_labels_accessed"]):
        return {
            "status": "REFUSE_MEASUREMENT_TO_PREDICTION_CONFLATION",
            "reason": "Domain geometry measurement must freeze before market/outcome prediction or outcome-label access.",
        }
    if bool(payload["source_reference_reused"]):
        return {
            "status": "REFUSE_SOURCE_REFERENCE_REUSE",
            "reason": "A target domain may reuse the procedure, never source numerical norms or landmarks by default.",
        }
    ready, artifact_status = _artifact_ready(payload["source_geometry_bundle"], label="SOURCE_GEOMETRY_BUNDLE")
    if not ready:
        return {"status": "REFUSE_SOURCE_GEOMETRY_BUNDLE", "reason": artifact_status}
    schema_ready, schema_flags, schema_missing = _schema_status(payload["target_schema"])
    if not schema_ready:
        return {"status": "REFUSE_TARGET_SCHEMA", "missing_or_invalid_schema_fields": schema_missing}
    reference = payload["target_reference_population"]
    if not isinstance(reference, dict) or not {"reference_id", "sampling_frame", "n_authors", "frozen_before_outcome_access"}.issubset(reference):
        return {"status": "REFUSE_TARGET_REFERENCE_PLAN", "reason": "missing_target_reference_population_fields"}
    if int(reference["n_authors"]) < 2 or bool(reference["frozen_before_outcome_access"]) is not True:
        return {"status": "REFUSE_TARGET_REFERENCE_PLAN", "reason": "target_reference_must_have_two_authors_and_freeze_before_outcomes"}
    runtime = payload["target_runtime"]
    runtime_required = {"representation_hash", "operator_registry_hash", "embedding_runtime", "tokenizer_or_segmenter"}
    if not isinstance(runtime, dict) or not runtime_required.issubset(runtime):
        return {"status": "REFUSE_TARGET_RUNTIME", "missing_fields": sorted(runtime_required.difference(runtime if isinstance(runtime, dict) else set()))}
    local = payload["target_local_reference_plan"]
    if not isinstance(local, dict) or bool(local.get("build_target_reference")) is not True or bool(local.get("reuse_source_numerical_norms")) is not False:
        return {"status": "REFUSE_TARGET_LOCAL_REFERENCE_POLICY", "reason": "target_local_reference_required_and_source_numerical_norms_forbidden"}
    return {"schema_flags": schema_flags}


def validate_domain_transport_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate a later domain handoff without authorizing unjustified transport."""
    if not isinstance(payload, dict):
        return {"status": "REFUSE_DOMAIN_TRANSPORT_SCHEMA", "reason": "manifest_must_be_object"}
    base = _base_gate(payload)
    if base is not None and "status" in base:
        return base
    assert base is not None
    mode = str(payload["mode"])
    boundary = (
        "Passing this validator licenses only the declared measurement protocol. It does not establish "
        "personality, emotion, clinical state, market prediction, cross-language equivalence, or a universal coordinate system."
    )
    if mode == "LOCAL_REFERENCE_ONLY":
        return {
            "status": "DOMAIN_TRANSPORT_LOCAL_REFERENCE_READY",
            "cross_domain_numeric_comparison_authorized": False,
            "schema_flags": base["schema_flags"],
            "claim_boundary": boundary,
        }
    if mode == "PAIRED_ALIGNMENT":
        alignment = payload.get("paired_alignment")
        required = {
            "bridge_type", "map_class", "anchor_training_id", "anchor_confirmation_id",
            "alignment_frozen_before_outcome_access", "heldout_metrics", "predeclared_thresholds",
        }
        if not isinstance(alignment, dict) or not required.issubset(alignment):
            return {"status": "REFUSE_PAIRED_ALIGNMENT_PROTOCOL", "missing_fields": sorted(required.difference(alignment if isinstance(alignment, dict) else set()))}
        if bool(alignment["alignment_frozen_before_outcome_access"]) is not True:
            return {"status": "REFUSE_PAIRED_ALIGNMENT_PROTOCOL", "reason": "alignment_not_frozen_before_outcomes"}
        if str(alignment["anchor_training_id"]) == str(alignment["anchor_confirmation_id"]):
            return {"status": "REFUSE_PAIRED_ALIGNMENT_PROTOCOL", "reason": "anchor_training_and_confirmation_must_be_disjoint"}
        evidence = alignment.get("heldout_result")
        if evidence is None:
            return {
                "status": "PAIRED_ALIGNMENT_PROTOCOL_READY_NOT_YET_EVALUATED",
                "cross_domain_numeric_comparison_authorized": False,
                "schema_flags": base["schema_flags"],
                "claim_boundary": boundary,
            }
        if not isinstance(evidence, dict) or bool(evidence.get("passed")) is not True:
            return {"status": "REFUSE_PAIRED_ALIGNMENT_HELDOUT_EVIDENCE", "reason": "heldout_alignment_not_passed"}
        return {
            "status": "PAIRED_ALIGNMENT_HELDOUT_SUPPORTED",
            "cross_domain_numeric_comparison_authorized": True,
            "schema_flags": base["schema_flags"],
            "claim_boundary": boundary,
        }
    artifact = payload.get("independent_validation_artifact")
    ready, artifact_status = _artifact_ready(artifact, label="INDEPENDENT_ALIGNMENT_VALIDATION")
    if not ready or not isinstance(artifact, dict) or bool(artifact.get("population_independent")) is not True:
        return {"status": "REFUSE_PRETRAINED_ALIGNMENT_EVIDENCE", "reason": artifact_status}
    return {
        "status": "PRETRAINED_ALIGNMENT_INDEPENDENTLY_VALIDATED",
        "cross_domain_numeric_comparison_authorized": True,
        "schema_flags": base["schema_flags"],
        "claim_boundary": boundary,
    }
