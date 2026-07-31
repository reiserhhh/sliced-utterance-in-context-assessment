"""Machine-enforced pre-experiment contracts for the SUICA method foundation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "suica_foundation_study.schema.json"

LAYERS = (
    "L0_human_process",
    "L1_expression_behavior",
    "L2_text_record",
    "L3_representation",
    "L4_technical_object",
    "L5_measurement_score",
    "L6_psychological_construct",
    "L7_use_decision",
)

EDGE_BY_TRANSITION = {
    (0, 1): "E01_production",
    (1, 2): "E12_capture",
    (2, 3): "E23_representation",
    (3, 4): "E34_estimation",
    (4, 5): "E45_reference_scoring",
    (5, 6): "E56_construct_mapping",
    (6, 7): "E67_use_decision",
}

GENERALIZATION_FACETS = (
    "target_population",
    "reference_population",
    "context",
    "opportunity",
    "occasion_time",
    "operator",
    "language_culture",
    "interaction_partner",
    "administration",
    "response_process",
)

_INACTIVE_WORDS = {
    "not applicable",
    "not_applicable",
    "none",
    "inactive",
    "disabled",
    "n/a",
}


def strict_json_loads(text: str) -> Any:
    """Parse standards-compliant JSON and reject NaN/Infinity extensions."""

    def reject_constant(value: str) -> None:
        raise ValueError(f"non-standard JSON constant: {value}")

    return json.loads(text, parse_constant=reject_constant)


def _placeholder_paths(value: Any, path: str = "contract") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            found.extend(_placeholder_paths(nested, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            found.extend(_placeholder_paths(nested, f"{path}[{index}]"))
    elif isinstance(value, str) and (
        "DECLARE_" in value or "TODO_" in value
    ):
        found.append(path)
    return found


def _inactive(value: Any) -> bool:
    normalized = str(value).strip().lower()
    return normalized in _INACTIVE_WORDS or normalized.startswith(
        ("not applicable", "not_applicable", "n/a")
    )


def _add(
    collection: list[dict[str, str]],
    code: str,
    detail: str,
) -> None:
    collection.append({"code": code, "detail": detail})


def _schema_errors(
    payload: Any,
    schema_path: str | Path,
) -> list[dict[str, str]]:
    schema = strict_json_loads(Path(schema_path).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors: list[dict[str, str]] = []
    for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.path)):
        location = ".".join(map(str, error.absolute_path)) or "contract"
        _add(errors, "SCHEMA_VIOLATION", f"{location}: {error.message}")
    return errors


def _check_bounded_openings(
    payload: dict[str, Any],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> set[str]:
    targeted = set(payload["study_question"]["targeted_openings"])
    observed: set[str] = set()

    for facet_name in GENERALIZATION_FACETS:
        facet = payload["generalization_universe"][facet_name]
        if facet["status"] != "bounded_open":
            continue
        opening_id = facet.get("opening_id", "")
        if not opening_id:
            _add(
                errors,
                "OPENING_ID_REQUIRED",
                f"generalization_universe.{facet_name}: bounded_open requires opening_id",
            )
            continue
        observed.add(opening_id)
        if opening_id not in targeted:
            _add(
                errors,
                "UNROUTED_OPEN_FACET",
                f"{facet_name}: {opening_id} is open but not targeted by this study",
            )
        else:
            _add(
                warnings,
                "BOUNDED_GENERALIZATION_FACET",
                f"{facet_name}: promotion remains blocked until {opening_id} closes",
            )

    for license_row in payload["claim"]["edge_licenses"]:
        if license_row["status"] != "bounded_open":
            continue
        opening_id = license_row.get("opening_id", "")
        if not opening_id:
            _add(
                errors,
                "OPENING_ID_REQUIRED",
                f"{license_row['edge']}: bounded_open requires opening_id",
            )
            continue
        observed.add(opening_id)
        if opening_id not in targeted:
            _add(
                errors,
                "UNROUTED_OPEN_EDGE",
                f"{license_row['edge']}: {opening_id} is open but not targeted",
            )
        else:
            _add(
                warnings,
                "BOUNDED_INFERENCE_EDGE",
                f"{license_row['edge']}: target-layer promotion remains blocked",
            )

    untethered = targeted.difference(observed)
    for opening_id in sorted(untethered):
        _add(
            errors,
            "UNKNOWN_TARGETED_OPENING",
            f"{opening_id}: no bounded facet or edge declares this opening",
        )
    return observed


def _required_edges(source_index: int, target_index: int) -> list[str]:
    return [
        EDGE_BY_TRANSITION[(index, index + 1)]
        for index in range(source_index, target_index)
    ]


def _check_layer_path(
    payload: dict[str, Any],
    errors: list[dict[str, str]],
) -> tuple[list[str], str]:
    claim = payload["claim"]
    source_index = LAYERS.index(claim["source_layer"])
    target_index = LAYERS.index(claim["target_layer"])
    if target_index < source_index:
        _add(
            errors,
            "REVERSED_INFERENCE_PATH",
            f"{claim['source_layer']} cannot infer backward to {claim['target_layer']}",
        )
        return [], claim["source_layer"]

    license_rows = claim["edge_licenses"]
    license_edges = [row["edge"] for row in license_rows]
    duplicate_edges = sorted(
        edge for edge in set(license_edges) if license_edges.count(edge) > 1
    )
    for edge in duplicate_edges:
        _add(
            errors,
            "DUPLICATE_EDGE_LICENSE",
            f"{edge}: each inference edge must have exactly one license",
        )
    licenses = {row["edge"]: row for row in license_rows}
    required = _required_edges(source_index, target_index)
    maximum_index = source_index
    still_supported = True
    for edge in required:
        row = licenses.get(edge)
        if row is None:
            _add(errors, "HIDDEN_INFERENCE_JUMP", f"{edge}: license missing")
            still_supported = False
            continue
        if row["status"] == "not_applicable":
            _add(
                errors,
                "INVALID_EDGE_EXEMPTION",
                f"{edge}: a crossed inference edge cannot be not_applicable",
            )
            still_supported = False
            continue
        if still_supported and row["status"] == "supported":
            maximum_index += 1
        else:
            still_supported = False

    extra = sorted(set(licenses).difference(required))
    for edge in extra:
        if licenses[edge]["status"] != "not_applicable":
            _add(
                errors,
                "OUT_OF_PATH_LICENSE",
                f"{edge}: supported/open license is outside the declared path",
            )
    return required, LAYERS[maximum_index]


def _check_semantics(
    payload: dict[str, Any],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    claim = payload["claim"]
    target_index = LAYERS.index(claim["target_layer"])
    source_index = LAYERS.index(claim["source_layer"])
    boundary = payload["interpretation_boundary"]
    universe = payload["generalization_universe"]
    chain = payload["transformation_chain"]
    error = payload["error_theory"]
    validation = payload["validation_route"]
    application = payload["application_overlay"]
    forensic = payload["forensic_overlay"]
    governance = payload["governance"]
    reference_measurement = payload.get("reference_measurement")

    if chain["llm_role"] == "final_scorer":
        _add(
            errors,
            "LLM_FINAL_SCORER_FORBIDDEN",
            "LLM output may observe or render evidence but cannot be the final score",
        )
    if target_index >= 4 and not chain["deterministic_scoring"]:
        _add(
            errors,
            "DETERMINISTIC_SCORER_REQUIRED",
            "L4 or higher claims require deterministic final scoring",
        )
    if not error["event_count_and_composition_separated"]:
        _add(
            errors,
            "EVENT_COMPOSITION_COLLAPSED",
            "event count and event composition must be separate error facets",
        )

    if payload["observation_design"]["context_role"] == "both_separated":
        if _inactive(payload["observation_design"]["choice_channel"]) or _inactive(
            payload["observation_design"]["response_channel"]
        ):
            _add(
                errors,
                "CHOICE_RESPONSE_NOT_SEPARATED",
                "both_separated context role requires explicit choice and response channels",
            )

    if source_index <= 1 and universe["response_process"]["status"] == "not_applicable":
        _add(
            errors,
            "RESPONSE_PROCESS_REQUIRED",
            "claims beginning before the text record must model the response process",
        )

    if target_index >= 5:
        if universe["reference_population"]["status"] != "declared":
            _add(
                errors,
                "REFERENCE_POPULATION_REQUIRED",
                "L5 or higher requires a declared, versioned reference population",
            )
        if _inactive(chain["reference_operator"]):
            _add(
                errors,
                "REFERENCE_OPERATOR_REQUIRED",
                "L5 or higher requires a reference-relative scoring operator",
            )
        if _inactive(error["reference_uncertainty"]):
            _add(
                errors,
                "REFERENCE_UNCERTAINTY_REQUIRED",
                "L5 or higher requires uncertainty from the reference population",
            )
        if (
            not isinstance(reference_measurement, dict)
            or not reference_measurement.get("active", False)
        ):
            _add(
                errors,
                "REFERENCE_MEASUREMENT_CONTRACT_REQUIRED",
                "L5 or higher requires an active reference_measurement contract",
            )
        else:
            required_declarations = {
                "reference_frame_id": "REFERENCE_FRAME_ID_REQUIRED",
                "reference_population_version": (
                    "REFERENCE_POPULATION_VERSION_REQUIRED"
                ),
                "target_facet_measure": "TARGET_FACET_MEASURE_REQUIRED",
                "representation_operator_version": (
                    "REFERENCE_OPERATOR_VERSION_REQUIRED"
                ),
                "chart_version": "REFERENCE_CHART_VERSION_REQUIRED",
                "occasion_universe": "OCCASION_UNIVERSE_REQUIRED",
                "support_positivity_rule": "REFERENCE_SUPPORT_RULE_REQUIRED",
                "effective_sample_size_rule": "REFERENCE_ESS_RULE_REQUIRED",
                "selection_identification_rule": (
                    "SELECTION_IDENTIFICATION_RULE_REQUIRED"
                ),
            }
            for field, code in required_declarations.items():
                if _inactive(reference_measurement[field]):
                    _add(
                        errors,
                        code,
                        f"reference_measurement.{field} must be operational",
                    )
            if not all(
                reference_measurement["panel_separation"].values()
            ):
                _add(
                    errors,
                    "REFERENCE_PANEL_SEPARATION_REQUIRED",
                    "reference, fit/calibration, and scored panels must be disjoint",
                )
            if not all(reference_measurement["joint_resampling"].values()):
                _add(
                    errors,
                    "JOINT_REFERENCE_RESAMPLING_REQUIRED",
                    "L5 uncertainty must resample reference, event, and occasion/operator facets",
                )
            required_error_facets = {
                "reference_population",
                "event_sampling",
                "occasion_time",
                "operator_method",
            }
            missing_facets = required_error_facets.difference(
                error["facets"]
            )
            if missing_facets:
                _add(
                    errors,
                    "REFERENCE_ERROR_FACETS_REQUIRED",
                    "L5 error theory is missing: "
                    + ", ".join(sorted(missing_facets)),
                )

    if claim["individual_score_claim"]:
        if target_index < 5 or not boundary["person_score_allowed"]:
            _add(
                errors,
                "INDIVIDUAL_SCORE_LICENSE_MISMATCH",
                "individual scores require L5+ and person_score_allowed=true",
            )
        for field in ("individual_sem", "minimum_detectable_difference"):
            if _inactive(error[field]):
                _add(
                    errors,
                    "INDIVIDUAL_ERROR_THEORY_REQUIRED",
                    f"error_theory.{field} is required for an individual score",
                )
    elif boundary["person_score_allowed"]:
        _add(
            errors,
            "PERSON_SCORE_BOUNDARY_MISMATCH",
            "person_score_allowed=true conflicts with individual_score_claim=false",
        )

    construct_requested = target_index >= 6 or claim["personality_claim"]
    if construct_requested:
        if target_index < 6:
            _add(
                errors,
                "PERSONALITY_LAYER_MISMATCH",
                "a personality claim cannot terminate below L6",
            )
        if not boundary["construct_naming_allowed"]:
            _add(
                errors,
                "CONSTRUCT_NAMING_LICENSE_REQUIRED",
                "L6 claims require construct_naming_allowed=true",
            )
        if claim["evidence_level"] not in {
            "E4_construct_validation",
            "E5_applied_validation",
        }:
            _add(
                errors,
                "EXTERNAL_CONSTRUCT_EVIDENCE_REQUIRED",
                "psychological naming requires E4 or E5 evidence",
            )
        if _inactive(validation["external_construct_evidence"]):
            _add(
                errors,
                "EXTERNAL_CONSTRUCT_PLAN_REQUIRED",
                "a construct claim requires independent external evidence",
            )
    elif boundary["construct_naming_allowed"]:
        _add(
            errors,
            "CONSTRUCT_BOUNDARY_MISMATCH",
            "construct naming is open below L6",
        )

    decision_requested = target_index >= 7 or claim["decision_claim"]
    if decision_requested:
        if target_index < 7:
            _add(
                errors,
                "DECISION_LAYER_MISMATCH",
                "a decision claim cannot terminate below L7",
            )
        if not application["active"] or not application["decisions_enabled"]:
            _add(
                errors,
                "APPLICATION_OVERLAY_REQUIRED",
                "L7 claims require an active application overlay",
            )
        if not boundary["decision_allowed"]:
            _add(
                errors,
                "DECISION_LICENSE_REQUIRED",
                "L7 claims require interpretation_boundary.decision_allowed=true",
            )
        if claim["evidence_level"] != "E5_applied_validation":
            _add(
                errors,
                "APPLICATION_VALIDATION_REQUIRED",
                "decision claims require E5 applied validation",
            )
        for field in ("consequences_analysis", "fairness_analysis", "human_authority"):
            if _inactive(application[field]):
                _add(
                    errors,
                    "DECISION_SAFEGUARD_REQUIRED",
                    f"application_overlay.{field} is required",
                )
    elif boundary["decision_allowed"] or application["decisions_enabled"]:
        _add(
            errors,
            "DECISION_BOUNDARY_MISMATCH",
            "decision use is enabled below L7",
        )

    forensic_requested = claim["forensic_claim"] or forensic["active"]
    if forensic_requested:
        if not claim["forensic_claim"] or not forensic["active"]:
            _add(
                errors,
                "FORENSIC_OVERLAY_MISMATCH",
                "forensic claim and forensic overlay must be enabled together",
            )
        if not decision_requested:
            _add(
                errors,
                "FORENSIC_DECISION_LAYER_REQUIRED",
                "forensic use belongs to the L7 use/decision layer",
            )
        for field, value in forensic.items():
            if field != "active" and _inactive(value):
                _add(
                    errors,
                    "FORENSIC_SAFEGUARD_REQUIRED",
                    f"forensic_overlay.{field} is required",
                )

    if payload["stage"] == "sealed_confirmation":
        required_flags = {
            "preregistered": governance["preregistered"],
            "operator_frozen": governance["operator_frozen"],
            "builder_auditor_separation": governance["builder_auditor_separation"],
            "provenance_complete": governance["provenance_complete"],
        }
        for field, enabled in required_flags.items():
            if not enabled:
                _add(
                    errors,
                    "CONFIRMATION_GOVERNANCE_REQUIRED",
                    f"governance.{field}=true is required for sealed confirmation",
                )
        if _inactive(validation["fresh_confirmation_rule"]):
            _add(
                errors,
                "FRESH_CONFIRMATION_REQUIRED",
                "sealed confirmation requires a fresh-data rule",
            )

    if len(payload["identification"]["alias_or_counterworlds"]) < 2:
        _add(
            errors,
            "ALIAS_WORLD_PAIR_REQUIRED",
            "identification requires at least two rival or null worlds",
        )

    if payload["stage"] == "application_validation":
        if payload["methodology_role"] != "application_validation":
            _add(
                errors,
                "APPLICATION_STAGE_ROLE_MISMATCH",
                "application_validation stage requires the application_validation role",
            )
    elif payload["methodology_role"] == "application_validation":
        _add(
            errors,
            "APPLICATION_STAGE_ROLE_MISMATCH",
            "application_validation role requires the application_validation stage",
        )

    if decision_requested and payload["methodology_role"] != "application_validation":
        _add(
            errors,
            "DECISION_ROLE_MISMATCH",
            "decision claims belong to a downstream application-validation study",
        )

    if payload["methodology_role"] == "foundation_research" and application["active"]:
        _add(
            warnings,
            "FOUNDATION_APPLICATION_OVERLAY",
            "application evidence must remain a downstream interface, not redefine SUICA",
        )


def validate_foundation_study(
    payload: Any,
    *,
    schema_path: str | Path = DEFAULT_SCHEMA,
) -> dict[str, Any]:
    """Validate ontology, inference licenses, and experiment-start readiness."""
    errors = _schema_errors(payload, schema_path)
    warnings: list[dict[str, str]] = []
    if not isinstance(payload, dict) or errors:
        return {
            "status": "REFUSE_EXPERIMENT_START",
            "study_id": payload.get("study_id", "") if isinstance(payload, dict) else "",
            "maximum_licensed_layer": "",
            "required_edges": [],
            "bounded_openings": [],
            "promotion_blocked": True,
            "refusal_codes": sorted({row["code"] for row in errors}),
            "errors": errors,
            "warnings": warnings,
        }

    placeholders = _placeholder_paths(payload)
    for path in placeholders:
        _add(errors, "UNRESOLVED_DECLARATION", f"{path}: placeholder remains")

    bounded_openings = _check_bounded_openings(payload, errors, warnings)
    required_edges, maximum_layer = _check_layer_path(payload, errors)
    _check_semantics(payload, errors, warnings)

    if errors:
        status = "REFUSE_EXPERIMENT_START"
    elif bounded_openings:
        status = "READY_FOR_BOUNDED_FOUNDATION_TEST"
    else:
        status = "FOUNDATION_CONTRACT_READY"

    return {
        "status": status,
        "study_id": payload["study_id"],
        "methodology_role": payload["methodology_role"],
        "declared_source_layer": payload["claim"]["source_layer"],
        "requested_target_layer": payload["claim"]["target_layer"],
        "maximum_licensed_layer": maximum_layer,
        "required_edges": required_edges,
        "bounded_openings": sorted(bounded_openings),
        "promotion_blocked": bool(bounded_openings),
        "refusal_codes": sorted({row["code"] for row in errors}),
        "errors": errors,
        "warnings": warnings,
        "claim_boundary": payload["interpretation_boundary"]["claim_boundary"],
    }
