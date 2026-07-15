"""Estimand declarations for auditable SUICA V7 experiments.

The module intentionally validates declared measurement objects before any
text or external labels are loaded.  It does not decide whether an object is
psychological; it only prevents incompatible questions from being merged into
one numerical result.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


TARGET_OBJECTS = {
    "relative_geometry",
    "shared_subspace",
    "fixed_coordinate",
    "free_selection_q",
    "fixed_response_B",
    "external_anchor",
}

_BASE_FIELDS = {
    "estimand_id",
    "version",
    "target_object",
    "reference_population",
    "occasion_definition",
    "operator_registry",
    "representation",
    "null_hypothesis",
    "minimum_detectable_effect",
    "decision_rule",
    "claim_boundary",
}


def _present(value: Any) -> bool:
    """Return whether a manifest field has a non-empty declared value."""
    return value is not None and value != "" and value != [] and value != {}


def _require_mapping(payload: dict[str, Any], key: str, fields: set[str], errors: list[str]) -> dict[str, Any]:
    """Validate a nested mapping and return it for target-specific checks."""
    value = payload.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key}: mapping required")
        for field in sorted(fields):
            errors.append(f"{key}.{field}: declared value required")
        return {}
    for field in sorted(fields):
        if not _present(value.get(field)):
            errors.append(f"{key}.{field}: declared value required")
    return value


def validate_estimand(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate one V7 estimand declaration without reading study data.

    A passing declaration only means the question is formally stated.  It does
    not make the estimator identified, the data sufficient, or the result a
    psychological construct.
    """
    errors: list[str] = []
    if not isinstance(payload, dict):
        return {"status": "REFUSE_ESTIMAND_UNDECLARED", "errors": ["manifest: object required"]}
    for field in sorted(_BASE_FIELDS):
        if not _present(payload.get(field)):
            errors.append(f"{field}: declared value required")

    target = str(payload.get("target_object", ""))
    if target not in TARGET_OBJECTS:
        errors.append(f"target_object: unsupported value {target!r}")

    _require_mapping(payload, "reference_population", {"id", "sampling_frame", "decision_scope"}, errors)
    _require_mapping(payload, "occasion_definition", {"unit", "replication_rule", "source_provenance"}, errors)
    operators = _require_mapping(payload, "operator_registry", {"registry_id", "operators"}, errors)
    if operators and not isinstance(operators.get("operators"), list):
        errors.append("operator_registry.operators: list required")
    representation = _require_mapping(payload, "representation", {"id", "frozen_before_confirmation"}, errors)
    if representation and not isinstance(representation.get("frozen_before_confirmation"), bool):
        errors.append("representation.frozen_before_confirmation: boolean required")
    mde = _require_mapping(payload, "minimum_detectable_effect", {"metric", "value", "direction"}, errors)
    if mde:
        try:
            if float(mde["value"]) < 0.0:
                errors.append("minimum_detectable_effect.value: must be non-negative")
        except (TypeError, ValueError):
            errors.append("minimum_detectable_effect.value: numeric value required")
    decision = _require_mapping(payload, "decision_rule", {"alpha", "multiplicity", "pass_status", "refuse_status"}, errors)
    if decision:
        try:
            alpha = float(decision["alpha"])
            if not 0.0 < alpha <= 1.0:
                errors.append("decision_rule.alpha: must be in (0, 1]")
        except (TypeError, ValueError):
            errors.append("decision_rule.alpha: numeric value required")

    if target == "fixed_coordinate":
        coordinate = _require_mapping(payload, "coordinate_identification", {"symmetry_breaker", "anchor_design", "repetition_rule"}, errors)
        if coordinate and str(coordinate.get("symmetry_breaker", "")).lower() in {"", "none", "post_hoc_rotation"}:
            errors.append("coordinate_identification.symmetry_breaker: predeclared non-post-hoc constraint required")
    elif target == "free_selection_q":
        requirements = _require_mapping(payload, "data_requirements", {"opportunity_menu_logging", "selection_flag"}, errors)
        if requirements and (requirements.get("opportunity_menu_logging") is not True or requirements.get("selection_flag") is not True):
            errors.append("data_requirements: q requires logged menus and selection flags")
    elif target == "fixed_response_B":
        requirements = _require_mapping(payload, "data_requirements", {"randomized_assignment", "minimum_sessions_per_person_condition"}, errors)
        if requirements:
            if requirements.get("randomized_assignment") is not True:
                errors.append("data_requirements.randomized_assignment: fixed response requires true")
            try:
                if int(requirements["minimum_sessions_per_person_condition"]) < 2:
                    errors.append("data_requirements.minimum_sessions_per_person_condition: must be >= 2")
            except (TypeError, ValueError):
                errors.append("data_requirements.minimum_sessions_per_person_condition: integer required")
    elif target == "external_anchor":
        _require_mapping(payload, "anchor_freeze", {"independent_cohort", "bundle_hash_required", "multiplicity_plan"}, errors)

    return {
        "status": "ESTIMAND_READY" if not errors else "REFUSE_ESTIMAND_UNDECLARED",
        "estimand_id": str(payload.get("estimand_id", "")),
        "target_object": target,
        "errors": errors,
        "claim_boundary": str(payload.get("claim_boundary", "")),
    }


def validate_estimand_registry(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate a versioned registry of independent V7 estimand manifests."""
    manifests = payload.get("manifests") if isinstance(payload, dict) else None
    if not isinstance(manifests, list) or not manifests:
        return {
            "status": "REFUSE_ESTIMAND_UNDECLARED",
            "errors": ["manifests: non-empty list required"],
            "results": [],
        }
    identifiers: set[str] = set()
    results: list[dict[str, Any]] = []
    for index, manifest in enumerate(manifests):
        result = validate_estimand(manifest if isinstance(manifest, dict) else {})
        identifier = result["estimand_id"]
        if not identifier:
            result["errors"].append(f"manifests[{index}].estimand_id: declared value required")
            result["status"] = "REFUSE_ESTIMAND_UNDECLARED"
        elif identifier in identifiers:
            result["errors"].append(f"estimand_id: duplicate {identifier!r}")
            result["status"] = "REFUSE_ESTIMAND_UNDECLARED"
        identifiers.add(identifier)
        results.append(result)
    failed = [item for item in results if item["status"] != "ESTIMAND_READY"]
    return {
        "status": "ESTIMAND_REGISTRY_READY" if not failed else "REFUSE_ESTIMAND_UNDECLARED",
        "registry_version": str(payload.get("registry_version", "")),
        "n_manifests": len(results),
        "n_refused": len(failed),
        "results": results,
    }


def load_estimand_registry(path: str | Path) -> dict[str, Any]:
    """Load and validate one JSON estimand registry."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Estimand registry must be a JSON object.")
    return validate_estimand_registry(payload)
