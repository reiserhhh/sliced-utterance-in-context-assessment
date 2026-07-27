"""Machine-enforced contracts for the SUICA V8 LLM-native measurement layer."""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import jsonschema

from suica_core.v8_aggregation import ALLOWED_EVENT_FIELDS


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_ISO_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

MEASUREMENT_COMPONENTS = {
    "relative_geometry",
    "stable_author_configuration",
    "session_state",
    "free_selection_q",
    "fixed_response_B",
    "interaction_history",
}

CLAIM_TYPES = {
    "technical_measurement_object",
    "exploratory_text_behavior",
    "psychological_construct",
    "clinical_interpretation",
}

UNCERTAINTY_COMPONENTS = {
    "source_cluster",
    "representation",
    "llm_run",
    "prompt",
    "reference_norm",
    "model",
}

ROLE_NAMES = {
    "builder",
    "auditor",
    "semantic_transducer",
    "interpreter",
    "adaptation_agent",
}

ROLE_FIELDS = {
    "agent_id",
    "session_id",
    "model_revision",
    "runtime_sha256",
    "implementation_sha256",
}

CONTROLLED_RENDERER_TEMPLATES = {
    "technical_reference_difference_v1": (
        "technical_measurement_object",
        "This profile differs from its declared reference on a text-behavior coordinate.",
    ),
    "exploratory_text_behavior_v1": (
        "exploratory_text_behavior",
        "This text-behavior pattern is exploratory and has no established psychological meaning.",
    ),
    "psychological_association_v1": (
        "psychological_construct",
        "This repeated text-behavior pattern is associated with the licensed external construct "
        "within the declared validation scope.",
    ),
    "clinical_human_review_v1": (
        "clinical_interpretation",
        "This validated text-behavior indicator warrants human review within the licensed "
        "clinical scope; it is not a diagnosis.",
    ),
}

EVIDENCE_STATUS_VALUES = {
    "repeated_measurement": {"UNTESTED", "ESTIMATED"},
    "external_construct_validity": {"UNTESTED", "INDEPENDENTLY_REPLICATED"},
    "clinical_validation": {"UNTESTED", "INDEPENDENTLY_REPLICATED"},
}


def strict_json_loads(text: str) -> Any:
    """Parse standards-compliant JSON and reject NaN/Infinity extensions."""
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-standard JSON constant: {value}")

    return json.loads(text, parse_constant=reject_constant)


def canonical_sha256(value: Any, *, omit_keys: set[str] | None = None) -> str:
    """Return a stable SHA-256 over canonical JSON, optionally omitting keys."""
    omitted = omit_keys or set()

    def strip(item: Any) -> Any:
        if isinstance(item, dict):
            return {
                key: strip(nested)
                for key, nested in sorted(item.items())
                if key not in omitted
            }
        if isinstance(item, list):
            return [strip(nested) for nested in item]
        return item

    encoded = json.dumps(
        strip(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _present(value: Any) -> bool:
    return value is not None and value != "" and value != [] and value != {}


def _numeric(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _valid_sha(value: Any) -> bool:
    text = str(value)
    return bool(_SHA256.fullmatch(text)) and text != "0" * 64


def _placeholder_paths(value: Any, path: str = "contract") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            found.extend(_placeholder_paths(nested, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            found.extend(_placeholder_paths(nested, f"{path}[{index}]"))
    elif isinstance(value, str) and (value.startswith("DECLARE_") or value == "0" * 64):
        found.append(path)
    return found


def _error(errors: list[dict[str, str]], code: str, detail: str) -> None:
    errors.append({"code": code, "detail": detail})


def _mapping(
    payload: dict[str, Any],
    key: str,
    required: set[str],
    errors: list[dict[str, str]],
) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        _error(errors, "UNDECLARED_SECTION", f"{key}: mapping required")
        return {}
    for field in sorted(required):
        if not _present(value.get(field)):
            _error(errors, "UNDECLARED_FIELD", f"{key}.{field}: declared value required")
    unknown = sorted(set(value).difference(required))
    if unknown:
        _error(errors, "UNDECLARED_FIELD", f"{key}: unsupported fields {unknown}")
    return value


def _bound_path(
    base_dir: str | Path | None,
    relative_path: Any,
    expected_sha256: Any,
    prefix: str,
    errors: list[dict[str, str]],
) -> Path | None:
    if base_dir is None:
        _error(
            errors,
            "ARTIFACT_BINDING_UNVERIFIED",
            f"{prefix}: repository root required to verify bound artifact",
        )
        return None
    if not isinstance(relative_path, str) or not relative_path:
        _error(errors, "INVALID_ARTIFACT_BINDING", f"{prefix}.path: relative path required")
        return None
    if not _valid_sha(expected_sha256):
        _error(errors, "INVALID_ARTIFACT_BINDING", f"{prefix}.sha256: lowercase SHA-256 required")
        return None

    root = Path(base_dir).resolve()
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        _error(errors, "INVALID_ARTIFACT_BINDING", f"{prefix}: path escapes repository root")
        return None
    if not candidate.is_file():
        _error(errors, "BOUND_ARTIFACT_MISSING", f"{prefix}: {relative_path} not found")
        return None
    observed = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if observed != expected_sha256:
        _error(
            errors,
            "BOUND_ARTIFACT_HASH_MISMATCH",
            f"{prefix}: expected {expected_sha256}, observed {observed}",
        )
        return None
    return candidate


def _bound_json(
    base_dir: str | Path | None,
    binding: Any,
    prefix: str,
    errors: list[dict[str, str]],
    allowed_binding_fields: set[str] | None = None,
) -> dict[str, Any]:
    if not isinstance(binding, dict):
        _error(errors, "INVALID_ARTIFACT_BINDING", f"{prefix}: mapping required")
        return {}
    allowed = allowed_binding_fields or {"path", "sha256"}
    unknown = sorted(set(binding).difference(allowed))
    if unknown:
        _error(errors, "INVALID_ARTIFACT_BINDING", f"{prefix}: unsupported fields {unknown}")
    path = _bound_path(
        base_dir,
        binding.get("path"),
        binding.get("sha256"),
        prefix,
        errors,
    )
    if path is None:
        return {}
    try:
        value = strict_json_loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        _error(errors, "BOUND_ARTIFACT_INVALID_JSON", f"{prefix}: valid JSON required")
        return {}
    if not isinstance(value, dict):
        _error(errors, "BOUND_ARTIFACT_INVALID_JSON", f"{prefix}: JSON object required")
        return {}
    return value


def _verify_signed_document(
    document: dict[str, Any],
    purpose: str,
    trusted_authorities: dict[str, Any] | None,
    prefix: str,
    errors: list[dict[str, str]],
) -> None:
    """Verify an Ed25519-signed artifact against a caller-supplied trust registry."""
    if not trusted_authorities:
        _error(errors, "EXTERNAL_AUTHORITY_REQUIRED", f"{prefix}: trusted authority registry required")
        return
    issuer = str(document.get("issuer_authority_id", ""))
    authority = trusted_authorities.get(issuer)
    if not isinstance(authority, dict):
        _error(errors, "UNTRUSTED_AUTHORITY", f"{prefix}: issuer is not trusted")
        return
    if purpose not in set(map(str, authority.get("purposes", []))):
        _error(errors, "UNTRUSTED_AUTHORITY", f"{prefix}: authority is not licensed for {purpose}")
        return
    if purpose == "clinical_signoff":
        authorized_signers = set(map(str, authority.get("authorized_signer_ids", [])))
        if document.get("signer_id") not in authorized_signers:
            _error(errors, "UNTRUSTED_AUTHORITY", f"{prefix}: signer is not authorized")
            return
    if document.get("purpose") != purpose:
        _error(errors, "TRUSTED_SIGNATURE_INVALID", f"{prefix}: signed purpose mismatch")
        return
    try:
        public_key = bytes.fromhex(str(authority.get("public_key_hex", "")))
        signature = bytes.fromhex(str(document.get("signature_hex", "")))
        message = json.dumps(
            {key: value for key, value in document.items() if key != "signature_hex"},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        Ed25519PublicKey.from_public_bytes(public_key).verify(signature, message)
    except (ValueError, InvalidSignature):
        _error(errors, "TRUSTED_SIGNATURE_INVALID", f"{prefix}: Ed25519 signature invalid")


def _validate_repository_schema(
    payload: dict[str, Any],
    base_dir: str | Path | None,
    relative_schema_path: str,
    errors: list[dict[str, str]],
) -> None:
    """Apply the canonical repository JSON Schema before semantic validation."""
    if base_dir is None:
        return
    schema_path = (Path(base_dir).resolve() / relative_schema_path).resolve()
    try:
        schema_path.relative_to(Path(base_dir).resolve())
        schema = strict_json_loads(schema_path.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
    except (OSError, ValueError, json.JSONDecodeError, jsonschema.SchemaError) as exc:
        _error(errors, "CANONICAL_SCHEMA_UNAVAILABLE", f"{relative_schema_path}: {type(exc).__name__}")
        return
    for violation in sorted(validator.iter_errors(payload), key=lambda item: list(item.absolute_path)):
        location = ".".join(map(str, violation.absolute_path)) or "root"
        _error(errors, "JSON_SCHEMA_INVALID", f"{location}: {violation.message}")


def validate_assessment_contract(
    payload: dict[str, Any],
    *,
    base_dir: str | Path | None = None,
    expected_active_sha256: str | None = None,
    trusted_authorities: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate one V8 contract before model calls or participant data access."""
    if not isinstance(payload, dict):
        return {
            "status": "REFUSE_V8_ASSESSMENT_CONTRACT",
            "contract_id": "",
            "refusal_codes": ["CONTRACT_NOT_OBJECT"],
            "errors": [{"code": "CONTRACT_NOT_OBJECT", "detail": "contract: object required"}],
        }

    errors: list[dict[str, str]] = []
    _validate_repository_schema(
        payload,
        _REPOSITORY_ROOT,
        "schemas/v8_assessment_contract.schema.json",
        errors,
    )
    if not _valid_sha(expected_active_sha256):
        _error(
            errors,
            "EXTERNAL_TRUST_ROOT_REQUIRED",
            "caller must supply the previously trusted active-bundle SHA-256",
        )
    contract_fields = {
        "contract_id",
        "version",
        "measurement_components",
        "observation_bundle",
        "representation_bundle",
        "semantic_transducer",
        "measurement_bundle",
        "role_separation",
        "data_requirements",
        "explanation_policy",
        "uncertainty_policy",
        "adaptation_policy",
        "claim_boundary",
    }
    unknown_contract_fields = sorted(set(payload).difference(contract_fields))
    if unknown_contract_fields:
        _error(
            errors,
            "UNDECLARED_FIELD",
            f"contract: unsupported fields {unknown_contract_fields}",
        )
    for path in _placeholder_paths(payload):
        _error(errors, "UNRESOLVED_PLACEHOLDER", f"{path}: replace placeholder before execution")
    for field in ("contract_id", "version", "measurement_components", "claim_boundary"):
        if not _present(payload.get(field)):
            _error(errors, "UNDECLARED_FIELD", f"{field}: declared value required")

    components = payload.get("measurement_components", [])
    if not isinstance(components, list) or not components:
        _error(errors, "INVALID_MEASUREMENT_COMPONENTS", "non-empty component list required")
        components = []
    unsupported = sorted(set(map(str, components)).difference(MEASUREMENT_COMPONENTS))
    if unsupported:
        _error(errors, "INVALID_MEASUREMENT_COMPONENTS", f"unsupported components: {unsupported}")

    observation = _mapping(
        payload,
        "observation_bundle",
        {"operator_registry_id", "occasion_definition", "context_fields", "support_rule"},
        errors,
    )
    if observation and not isinstance(observation.get("context_fields"), list):
        _error(errors, "INVALID_OBSERVATION_BUNDLE", "context_fields: list required")

    representation = _mapping(
        payload,
        "representation_bundle",
        {"representation_id", "runtime_revision", "frozen_before_confirmation"},
        errors,
    )
    if representation and representation.get("frozen_before_confirmation") is not True:
        _error(errors, "UNFROZEN_REPRESENTATION", "representation must be frozen before confirmation")

    transducer = _mapping(
        payload,
        "semantic_transducer",
        {
            "enabled",
            "role",
            "provider",
            "model_id",
            "model_revision",
            "prompt_path",
            "prompt_sha256",
            "output_schema_id",
            "output_schema_path",
            "schema_sha256",
            "output_fields",
            "decoding",
            "repetitions",
        },
        errors,
    )
    transducer_fields: set[str] = set()
    if transducer:
        if transducer.get("enabled") is not True:
            _error(errors, "SEMANTIC_TRANSDUCER_DISABLED", "semantic transducer must be enabled")
        if transducer.get("role") != "observation_semantic_transducer":
            _error(errors, "LLM_FINAL_SCORER_FORBIDDEN", "LLM role must remain observation-level")
        if transducer.get("output_schema_id") != "suica.v8.semantic_observation.v1":
            _error(errors, "SEMANTIC_SCHEMA_FORBIDDEN", "frozen observation schema ID required")
        output_fields = transducer.get("output_fields")
        if isinstance(output_fields, list):
            transducer_fields = set(map(str, output_fields))
        if transducer_fields != set(ALLOWED_EVENT_FIELDS):
            _error(
                errors,
                "LLM_PERSON_LEVEL_OUTPUT_FORBIDDEN",
                "semantic output fields must exactly match the frozen observation event fields",
            )
        _bound_path(
            base_dir,
            transducer.get("prompt_path"),
            transducer.get("prompt_sha256"),
            "semantic_transducer.prompt",
            errors,
        )
        _bound_path(
            base_dir,
            transducer.get("output_schema_path"),
            transducer.get("schema_sha256"),
            "semantic_transducer.output_schema",
            errors,
        )
        decoding = transducer.get("decoding")
        if not isinstance(decoding, dict):
            _error(errors, "UNVERSIONED_SEMANTIC_TRANSDUCER", "decoding mapping required")
        else:
            if not _numeric(decoding.get("temperature")):
                _error(errors, "UNVERSIONED_SEMANTIC_TRANSDUCER", "finite temperature required")
            top_p = decoding.get("top_p")
            if not _numeric(top_p) or not 0.0 <= float(top_p) <= 1.0:
                _error(
                    errors,
                    "UNVERSIONED_SEMANTIC_TRANSDUCER",
                    "top_p must be finite in [0, 1]",
                )
        try:
            repetitions = int(transducer.get("repetitions", 0))
        except (TypeError, ValueError):
            repetitions = 0
        if repetitions < 2:
            _error(errors, "LLM_RUN_VARIANCE_UNMEASURED", "at least two repetitions required")

    measurement = _mapping(
        payload,
        "measurement_bundle",
        {
            "aggregation_runtime",
            "aggregator_entrypoint",
            "aggregator_path",
            "aggregator_sha256",
            "allowed_input_fields",
            "reference_population",
            "support_refusal_active",
        },
        errors,
    )
    if measurement:
        if measurement.get("aggregation_runtime") != "deterministic_code":
            _error(errors, "LLM_FINAL_SCORER_FORBIDDEN", "deterministic aggregation required")
        if (
            measurement.get("aggregator_entrypoint")
            != "suica_core.v8_aggregation:aggregate_semantic_observations"
        ):
            _error(errors, "UNFROZEN_AGGREGATOR", "frozen V8 aggregator entrypoint required")
        _bound_path(
            base_dir,
            measurement.get("aggregator_path"),
            measurement.get("aggregator_sha256"),
            "measurement_bundle.aggregator",
            errors,
        )
        allowed_inputs = measurement.get("allowed_input_fields")
        input_fields = set(map(str, allowed_inputs)) if isinstance(allowed_inputs, list) else set()
        if not input_fields or input_fields != transducer_fields:
            _error(
                errors,
                "AGGREGATOR_INPUT_ALLOWLIST_INVALID",
                "aggregator inputs must exactly match frozen semantic event fields",
            )
        if measurement.get("support_refusal_active") is not True:
            _error(errors, "SUPPORT_REFUSAL_DISABLED", "support refusal must be active")

    roles = _mapping(
        payload,
        "role_separation",
        ROLE_NAMES | {"human_authority", "auditor_attestation"},
        errors,
    )
    if roles:
        parsed_roles: dict[str, dict[str, Any]] = {}
        for role_name in sorted(ROLE_NAMES):
            role = roles.get(role_name)
            if not isinstance(role, dict):
                _error(errors, "ROLE_IDENTITY_INCOMPLETE", f"role_separation.{role_name}: mapping required")
                continue
            if set(role) != ROLE_FIELDS:
                _error(
                    errors,
                    "ROLE_IDENTITY_INCOMPLETE",
                    f"role_separation.{role_name}: exact identity fields required",
                )
            parsed_roles[role_name] = role
            for field in sorted(ROLE_FIELDS):
                if not _present(role.get(field)):
                    _error(
                        errors,
                        "ROLE_IDENTITY_INCOMPLETE",
                        f"role_separation.{role_name}.{field}: required",
                    )
            for field in ("runtime_sha256", "implementation_sha256"):
                if not _valid_sha(role.get(field)):
                    _error(
                        errors,
                        "ROLE_IDENTITY_INCOMPLETE",
                        f"role_separation.{role_name}.{field}: SHA-256 required",
                    )
        human = roles.get("human_authority")
        if (
            not isinstance(human, dict)
            or set(human) != {"authority_id"}
            or not _present(human.get("authority_id"))
        ):
            _error(errors, "ROLE_IDENTITY_INCOMPLETE", "human_authority.authority_id required")
        elif not trusted_authorities or human.get("authority_id") not in trusted_authorities:
            _error(errors, "UNTRUSTED_AUTHORITY", "human authority must resolve externally")
        auditor = parsed_roles.get("auditor", {})
        for role_name, role in parsed_roles.items():
            if role_name == "auditor":
                continue
            for field in ("agent_id", "session_id", "runtime_sha256", "implementation_sha256"):
                if auditor.get(field) == role.get(field):
                    _error(
                        errors,
                        "LLM_SELF_AUDIT_FORBIDDEN",
                        f"auditor.{field} must be independent of {role_name}.{field}",
                    )
        attestation = roles.get("auditor_attestation")
        attested = _bound_json(base_dir, attestation, "role_separation.auditor_attestation", errors)
        if attested and (
            attested.get("auditor_agent_id") != auditor.get("agent_id")
            or attested.get("auditor_session_id") != auditor.get("session_id")
        ):
            _error(errors, "AUDITOR_ATTESTATION_MISMATCH", "attestation must bind auditor identity")
        if attested:
            builder = parsed_roles.get("builder", {})
            expected_attestation = {
                "contract_id": payload.get("contract_id"),
                "active_bundle_sha256": (
                    (payload.get("adaptation_policy") or {}).get("active_bundle") or {}
                ).get("sha256"),
                "candidate_bundle_sha256": (
                    (payload.get("adaptation_policy") or {}).get("candidate_bundle") or {}
                ).get("sha256"),
                "auditor_agent_id": auditor.get("agent_id"),
                "auditor_session_id": auditor.get("session_id"),
                "auditor_runtime_sha256": auditor.get("runtime_sha256"),
                "auditor_implementation_sha256": auditor.get("implementation_sha256"),
                "builder_agent_id": builder.get("agent_id"),
                "builder_session_id": builder.get("session_id"),
            }
            if any(attested.get(field) != value for field, value in expected_attestation.items()):
                _error(
                    errors,
                    "AUDITOR_ATTESTATION_MISMATCH",
                    "attestation must bind builder and auditor execution identities",
                )
            _verify_signed_document(
                attested,
                "auditor_attestation",
                trusted_authorities,
                "role_separation.auditor_attestation",
                errors,
            )

    requirements = _mapping(
        payload,
        "data_requirements",
        {
            "opportunity_menu_logging",
            "selection_flag",
            "randomized_repeated_conditions",
            "minimum_sessions_per_person_condition",
            "state_occasion_defined",
        },
        errors,
    )
    if "free_selection_q" in components and requirements:
        if (
            requirements.get("opportunity_menu_logging") is not True
            or requirements.get("selection_flag") is not True
        ):
            _error(errors, "FREE_SELECTION_Q_NOT_IDENTIFIED", "q requires menus and selection flags")
    if "fixed_response_B" in components and requirements:
        try:
            minimum_sessions = int(requirements.get("minimum_sessions_per_person_condition", 0))
        except (TypeError, ValueError):
            minimum_sessions = 0
        if requirements.get("randomized_repeated_conditions") is not True or minimum_sessions < 2:
            _error(errors, "FIXED_RESPONSE_B_NOT_IDENTIFIED", "B requires randomized repeats")
    if "session_state" in components and requirements.get("state_occasion_defined") is not True:
        _error(errors, "SESSION_STATE_NOT_IDENTIFIED", "state requires an occasion boundary")

    explanation = _mapping(
        payload,
        "explanation_policy",
        {
            "evidence_graph_required",
            "positive_and_counterevidence_required",
            "necessity_test_required",
            "sufficiency_test_required",
            "sentence_binding_required",
            "interpreter_input",
            "renderer",
        },
        errors,
    )
    if explanation:
        guards = {
            "evidence_graph_required",
            "positive_and_counterevidence_required",
            "necessity_test_required",
            "sufficiency_test_required",
            "sentence_binding_required",
        }
        if any(explanation.get(flag) is not True for flag in guards):
            _error(errors, "EVIDENCE_CERTIFICATE_INCOMPLETE", "all evidence guards must be enabled")
        if explanation.get("interpreter_input") != "evidence_graph_only":
            _error(errors, "FREEFORM_INTERPRETATION_FORBIDDEN", "evidence-graph-only input required")
        if explanation.get("renderer") != "controlled_templates_v1":
            _error(errors, "FREEFORM_INTERPRETATION_FORBIDDEN", "controlled renderer required")

    uncertainty = _mapping(
        payload,
        "uncertainty_policy",
        {"components", "combination_method", "refuse_without_joint_draws"},
        errors,
    )
    if uncertainty:
        declared = set(map(str, uncertainty.get("components", [])))
        missing = sorted(UNCERTAINTY_COMPONENTS.difference(declared))
        if missing:
            _error(errors, "UNCERTAINTY_COMPONENTS_MISSING", f"missing components: {missing}")
        if (
            uncertainty.get("combination_method") != "joint_nested"
            or uncertainty.get("refuse_without_joint_draws") is not True
        ):
            _error(errors, "INDEPENDENCE_SUM_FORBIDDEN", "joint nested draws are mandatory")

    adaptation = _mapping(
        payload,
        "adaptation_policy",
        {
            "active_bundle_immutable",
            "candidate_status_only",
            "confirmation_hidden",
            "independent_audit_required",
            "human_authorization_required",
            "promotion_status",
            "active_bundle",
            "candidate_bundle",
            "candidate_parent_sha256",
            "active_sha256_before",
            "active_sha256_after",
            "promotion_ledger",
        },
        errors,
    )
    if adaptation:
        flags = {
            "active_bundle_immutable",
            "candidate_status_only",
            "confirmation_hidden",
            "independent_audit_required",
            "human_authorization_required",
        }
        if any(adaptation.get(field) is not True for field in flags):
            _error(errors, "SELF_MODIFYING_MEASUREMENT_FORBIDDEN", "immutable audited candidates required")
        if adaptation.get("promotion_status") != "CANDIDATE_ONLY":
            _error(errors, "UNAUTHORIZED_PROMOTION", "development contract must remain candidate-only")
        active = _bound_json(base_dir, adaptation.get("active_bundle"), "adaptation.active_bundle", errors)
        candidate = _bound_json(
            base_dir,
            adaptation.get("candidate_bundle"),
            "adaptation.candidate_bundle",
            errors,
        )
        ledger = _bound_json(
            base_dir,
            adaptation.get("promotion_ledger"),
            "adaptation.promotion_ledger",
            errors,
        )
        active_sha = (adaptation.get("active_bundle") or {}).get("sha256")
        candidate_sha = (adaptation.get("candidate_bundle") or {}).get("sha256")
        if (
            adaptation.get("active_sha256_before") != active_sha
            or adaptation.get("active_sha256_after") != active_sha
        ):
            _error(errors, "ACTIVE_BUNDLE_MUTATED", "before/after hashes must equal active artifact")
        if active_sha != expected_active_sha256:
            _error(
                errors,
                "EXTERNAL_TRUST_ROOT_MISMATCH",
                "contract active bundle does not match caller-supplied trust root",
            )
        if adaptation.get("candidate_parent_sha256") != active_sha:
            _error(errors, "CANDIDATE_PARENT_MISMATCH", "candidate must descend from active hash")
        if candidate and candidate.get("parent_active_sha256") != active_sha:
            _error(errors, "CANDIDATE_PARENT_MISMATCH", "candidate manifest parent mismatch")
        if active and active.get("status") != "ACTIVE_IMMUTABLE":
            _error(errors, "ACTIVE_BUNDLE_MUTATED", "active manifest must be immutable")
        if ledger and (
            ledger.get("status") != "CANDIDATE_ONLY"
            or ledger.get("active_bundle_sha256") != active_sha
            or ledger.get("candidate_bundle_sha256") != candidate_sha
            or ledger.get("human_authorization_event") is not None
        ):
            _error(errors, "UNAUTHORIZED_PROMOTION", "promotion ledger must record no promotion")

    codes = list(dict.fromkeys(error["code"] for error in errors))
    return {
        "status": "V8_ASSESSMENT_CONTRACT_READY" if not errors else "REFUSE_V8_ASSESSMENT_CONTRACT",
        "contract_id": str(payload.get("contract_id", "")),
        "measurement_components": list(map(str, components)),
        "refusal_codes": codes,
        "errors": errors,
        "claim_boundary": str(payload.get("claim_boundary", "")),
    }


def _validate_counterfactual(
    test: Any,
    prefix: str,
    errors: list[dict[str, str]],
) -> None:
    required = {"performed", "paired_delta", "matched_random_delta", "ci_lower", "ci_upper"}
    if not isinstance(test, dict) or test.get("performed") is not True:
        _error(errors, "COUNTERFACTUAL_TEST_MISSING", f"{prefix}.performed must be true")
        return
    if not required.issubset(test) or not all(
        _numeric(test.get(field)) for field in required.difference({"performed"})
    ):
        _error(errors, "COUNTERFACTUAL_TEST_MISSING", f"{prefix}: finite paired statistics required")
        return
    delta = float(test["paired_delta"])
    lower = float(test["ci_lower"])
    upper = float(test["ci_upper"])
    if lower <= 0 or upper < lower or not lower <= delta <= upper:
        _error(
            errors,
            "COUNTERFACTUAL_FIDELITY_NOT_DEMONSTRATED",
            f"{prefix}: paired-delta interval must be ordered, contain delta, and exclude zero",
        )


def validate_explanation_certificate(
    payload: dict[str, Any],
    *,
    base_dir: str | Path | None = None,
    trusted_authorities: dict[str, Any] | None = None,
    expected_contract_id: str | None = None,
    expected_bundle_id: str | None = None,
) -> dict[str, Any]:
    """Validate evidence closure and language licensing for one V8 explanation."""
    if not isinstance(payload, dict):
        return {
            "status": "REFUSE_V8_EXPLANATION_CERTIFICATE",
            "certificate_id": "",
            "refusal_codes": ["CERTIFICATE_NOT_OBJECT"],
            "errors": [{"code": "CERTIFICATE_NOT_OBJECT", "detail": "certificate: object required"}],
        }

    errors: list[dict[str, str]] = []
    _validate_repository_schema(
        payload,
        _REPOSITORY_ROOT,
        "schemas/v8_explanation_certificate.schema.json",
        errors,
    )
    if not _present(expected_contract_id) or not _present(expected_bundle_id):
        _error(
            errors,
            "EXTERNAL_TRUST_ROOT_REQUIRED",
            "caller must supply expected contract and active bundle IDs",
        )
    certificate_fields = {
        "certificate_id",
        "contract_id",
        "measurement_status",
        "support_status",
        "evidence_graph",
        "claims",
        "uncertainty",
        "provenance",
        "language_license",
        "evidence_status_ledger",
        "human_signoff",
    }
    unknown_certificate_fields = sorted(set(payload).difference(certificate_fields))
    if unknown_certificate_fields:
        _error(
            errors,
            "UNDECLARED_FIELD",
            f"certificate: unsupported fields {unknown_certificate_fields}",
        )
    for field in (
        "certificate_id",
        "contract_id",
        "measurement_status",
        "support_status",
        "evidence_graph",
        "claims",
        "provenance",
        "uncertainty",
        "language_license",
        "evidence_status_ledger",
    ):
        if not _present(payload.get(field)):
            _error(errors, "UNDECLARED_FIELD", f"{field}: declared value required")
    if payload.get("measurement_status") != "MEASUREMENT_READY":
        _error(errors, "MEASUREMENT_NOT_READY", "measurement must be ready")
    if payload.get("support_status") != "IN_SUPPORT":
        _error(errors, "MEASUREMENT_OUT_OF_SUPPORT", "measurement must be in support")
    if payload.get("contract_id") != expected_contract_id:
        _error(errors, "EXTERNAL_TRUST_ROOT_MISMATCH", "certificate contract ID mismatch")

    provenance = _mapping(payload, "provenance", {"artifact_hashes", "bundle_id"}, errors)
    provenance_hashes: set[str] = set()
    if provenance:
        hashes = provenance.get("artifact_hashes")
        if isinstance(hashes, list) and hashes and all(_valid_sha(value) for value in hashes):
            provenance_hashes = set(map(str, hashes))
        else:
            _error(errors, "INVALID_ARTIFACT_PROVENANCE", "valid provenance hashes required")
        if provenance.get("bundle_id") != expected_bundle_id:
            _error(errors, "EXTERNAL_TRUST_ROOT_MISMATCH", "certificate bundle ID mismatch")
    evidence_root_sha256 = canonical_sha256(payload.get("evidence_graph", {}))

    uncertainty = _mapping(payload, "uncertainty", {"combination_method", "interval"}, errors)
    if uncertainty:
        interval = uncertainty.get("interval")
        if uncertainty.get("combination_method") != "joint_nested":
            _error(errors, "UNLICENSED_UNCERTAINTY", "joint nested uncertainty required")
        if (
            not isinstance(interval, list)
            or len(interval) != 2
            or not all(_numeric(value) for value in interval)
            or float(interval[1]) < float(interval[0])
        ):
            _error(errors, "UNLICENSED_UNCERTAINTY", "ordered finite interval required")

    license_binding = payload.get("language_license")
    language_license = _bound_json(
        base_dir,
        license_binding,
        "language_license",
        errors,
        {"path", "sha256", "license_id"},
    )
    license_hash = license_binding.get("sha256") if isinstance(license_binding, dict) else None
    if license_hash not in provenance_hashes:
        _error(errors, "LANGUAGE_LICENSE_UNBOUND", "license hash must be in provenance")
    if language_license and isinstance(license_binding, dict):
        if language_license.get("license_id") != license_binding.get("license_id"):
            _error(errors, "LANGUAGE_LICENSE_UNBOUND", "license ID mismatch")
        _verify_signed_document(
            language_license,
            "language_license",
            trusted_authorities,
            "language_license",
            errors,
        )
        if (
            language_license.get("contract_id") != expected_contract_id
            or language_license.get("bundle_id") != expected_bundle_id
        ):
            _error(errors, "LANGUAGE_LICENSE_SCOPE_MISMATCH", "license contract/bundle scope mismatch")

    ledger_binding = payload.get("evidence_status_ledger")
    ledger = _bound_json(base_dir, ledger_binding, "evidence_status_ledger", errors)
    ledger_hash = ledger_binding.get("sha256") if isinstance(ledger_binding, dict) else None
    if ledger_hash not in provenance_hashes:
        _error(errors, "EVIDENCE_LEDGER_UNBOUND", "evidence ledger hash must be in provenance")
    statuses = ledger.get("statuses", {}) if ledger else {}
    if ledger:
        _verify_signed_document(
            ledger,
            "evidence_status_ledger",
            trusted_authorities,
            "evidence_status_ledger",
            errors,
        )
        if (
            ledger.get("contract_id") != expected_contract_id
            or ledger.get("bundle_id") != expected_bundle_id
            or ledger.get("evidence_root_sha256") != evidence_root_sha256
        ):
            _error(errors, "EVIDENCE_LEDGER_SCOPE_MISMATCH", "ledger scope/evidence root mismatch")
    if not isinstance(statuses, dict):
        statuses = {}
        _error(errors, "EVIDENCE_LEDGER_INVALID", "ledger statuses must be a mapping")
    for status_name, allowed in EVIDENCE_STATUS_VALUES.items():
        if statuses.get(status_name) not in allowed:
            _error(errors, "EVIDENCE_LEDGER_INVALID", f"{status_name}: controlled status required")

    evidence_graph = payload.get("evidence_graph", {})
    if not isinstance(evidence_graph, dict) or not evidence_graph:
        evidence_graph = {}
        _error(errors, "EVIDENCE_GRAPH_MISSING", "non-empty evidence graph required")
    valid_nodes: dict[str, dict[str, Any]] = {}
    node_fields = {
        "node_id",
        "kind",
        "artifact_path",
        "artifact_hash",
        "source_span_ids",
        "measurement_field",
        "observed_value",
        "node_sha256",
    }
    for node_key, node in evidence_graph.items():
        prefix = f"evidence_graph.{node_key}"
        if not isinstance(node, dict) or set(node) != node_fields:
            _error(errors, "EVIDENCE_NODE_INVALID", f"{prefix}: exact typed node fields required")
            continue
        if node.get("node_id") != node_key or node.get("kind") not in {"supporting", "counterevidence"}:
            _error(errors, "EVIDENCE_NODE_INVALID", f"{prefix}: node identity or kind invalid")
        spans = node.get("source_span_ids")
        if not isinstance(spans, list) or not spans or not all(_present(value) for value in spans):
            _error(errors, "EVIDENCE_NODE_INVALID", f"{prefix}: source span IDs required")
        if not _present(node.get("measurement_field")):
            _error(errors, "EVIDENCE_NODE_INVALID", f"{prefix}: measurement field required")
        evidence_artifact = _bound_json(
            base_dir,
            {"path": node.get("artifact_path"), "sha256": node.get("artifact_hash")},
            f"{prefix}.artifact",
            errors,
        )
        source_spans = evidence_artifact.get("source_spans", {}) if evidence_artifact else {}
        measurements = evidence_artifact.get("measurements", {}) if evidence_artifact else {}
        if (
            not isinstance(source_spans, dict)
            or any(str(span_id) not in source_spans for span_id in spans)
        ):
            _error(errors, "EVIDENCE_SOURCE_SPAN_UNRESOLVED", f"{prefix}: source span not in artifact")
        measurement_record = (
            measurements.get(str(node.get("measurement_field")))
            if isinstance(measurements, dict)
            else None
        )
        if not isinstance(measurement_record, dict) or "value" not in measurement_record:
            _error(errors, "EVIDENCE_MEASUREMENT_UNRESOLVED", f"{prefix}: field not in artifact")
        elif measurement_record.get("value") != node.get("observed_value"):
            _error(errors, "EVIDENCE_MEASUREMENT_MISMATCH", f"{prefix}: observed value mismatch")
        if node.get("artifact_hash") not in provenance_hashes:
            _error(errors, "EVIDENCE_PROVENANCE_OPEN", f"{prefix}: artifact not in provenance")
        expected_node_hash = canonical_sha256(node, omit_keys={"node_sha256"})
        if node.get("node_sha256") != expected_node_hash:
            _error(errors, "EVIDENCE_NODE_HASH_MISMATCH", f"{prefix}: canonical hash mismatch")
        valid_nodes[str(node_key)] = node

    claims = payload.get("claims", [])
    if not isinstance(claims, list) or not claims:
        _error(errors, "NO_EXPLANATION_CLAIMS", "non-empty claims required")
        claims = []
    allowed_claim_types = set(map(str, language_license.get("allowed_claim_types", [])))
    allowed_templates = set(map(str, language_license.get("allowed_renderer_templates", [])))
    claim_fields = {
        "claim_id",
        "statement",
        "claim_type",
        "renderer_template_id",
        "evidence_ids",
        "counterevidence_ids",
        "necessity_test",
        "sufficiency_test",
        "sentence_bindings",
        "artifact_hashes",
        "claim_sha256",
    }
    has_clinical_claim = False
    certificate_claim_hashes: list[str] = []
    for index, claim in enumerate(claims):
        prefix = f"claims[{index}]"
        if not isinstance(claim, dict) or set(claim) != claim_fields:
            _error(errors, "INVALID_CLAIM", f"{prefix}: exact typed claim fields required")
            continue
        claim_type = str(claim.get("claim_type", ""))
        template_id = str(claim.get("renderer_template_id", ""))
        controlled = CONTROLLED_RENDERER_TEMPLATES.get(template_id)
        if claim_type not in CLAIM_TYPES or controlled is None:
            _error(errors, "INVALID_CLAIM_TYPE", f"{prefix}: controlled claim type/template required")
        elif controlled != (claim_type, claim.get("statement")):
            _error(errors, "FREEFORM_INTERPRETATION_FORBIDDEN", f"{prefix}: statement must use template")
        if claim_type not in allowed_claim_types or template_id not in allowed_templates:
            _error(errors, "LANGUAGE_LICENSE_UNBOUND", f"{prefix}: claim not allowed by license")

        evidence_ids = claim.get("evidence_ids")
        counter_ids = claim.get("counterevidence_ids")
        if not isinstance(evidence_ids, list) or not evidence_ids:
            _error(errors, "EVIDENCE_CLAIM_INCOMPLETE", f"{prefix}.evidence_ids required")
            evidence_ids = []
        if not isinstance(counter_ids, list) or not counter_ids:
            _error(errors, "EVIDENCE_CLAIM_INCOMPLETE", f"{prefix}.counterevidence_ids required")
            counter_ids = []
        for node_id in evidence_ids:
            node = valid_nodes.get(str(node_id))
            if node is None:
                _error(errors, "EVIDENCE_REFERENCE_UNRESOLVED", f"{prefix}: evidence node missing")
            elif node.get("kind") != "supporting":
                _error(errors, "EVIDENCE_KIND_MISMATCH", f"{prefix}: supporting node required")
        for node_id in counter_ids:
            node = valid_nodes.get(str(node_id))
            if node is None:
                _error(errors, "EVIDENCE_REFERENCE_UNRESOLVED", f"{prefix}: counter node missing")
            elif node.get("kind") != "counterevidence":
                _error(errors, "EVIDENCE_KIND_MISMATCH", f"{prefix}: counterevidence node required")

        referenced_ids = set(map(str, evidence_ids + counter_ids))
        referenced_hashes = {
            value
            for node_id in referenced_ids
            if node_id in valid_nodes
            for value in (
                str(valid_nodes[node_id]["artifact_hash"]),
                str(valid_nodes[node_id]["node_sha256"]),
            )
        }
        claim_hashes = claim.get("artifact_hashes")
        if (
            not isinstance(claim_hashes, list)
            or set(map(str, claim_hashes)) != referenced_hashes
            or not referenced_hashes.issubset(provenance_hashes)
        ):
            _error(errors, "EVIDENCE_PROVENANCE_OPEN", f"{prefix}: claim artifact chain is open")

        bindings = claim.get("sentence_bindings")
        bound_ids: set[str] = set()
        if not isinstance(bindings, list) or not bindings:
            _error(errors, "SENTENCE_BINDING_MISSING", f"{prefix}: sentence bindings required")
            bindings = []
        for binding_index, binding in enumerate(bindings):
            binding_prefix = f"{prefix}.sentence_bindings[{binding_index}]"
            binding_fields = {"sentence_id", "claim_id", "evidence_ids", "binding_sha256"}
            if not isinstance(binding, dict) or set(binding) != binding_fields:
                _error(errors, "SENTENCE_BINDING_INVALID", f"{binding_prefix}: exact fields required")
                continue
            ids = binding.get("evidence_ids")
            if (
                binding.get("claim_id") != claim.get("claim_id")
                or not isinstance(ids, list)
                or not ids
                or not set(map(str, ids)).issubset(referenced_ids)
            ):
                _error(errors, "SENTENCE_BINDING_INVALID", f"{binding_prefix}: unresolved binding")
            else:
                bound_ids.update(map(str, ids))
            expected_binding_hash = canonical_sha256(binding, omit_keys={"binding_sha256"})
            if binding.get("binding_sha256") != expected_binding_hash:
                _error(errors, "SENTENCE_BINDING_HASH_MISMATCH", f"{binding_prefix}: hash mismatch")
        if bound_ids != referenced_ids:
            _error(errors, "SENTENCE_BINDING_INCOMPLETE", f"{prefix}: all evidence must bind")

        _validate_counterfactual(claim.get("necessity_test"), f"{prefix}.necessity_test", errors)
        _validate_counterfactual(claim.get("sufficiency_test"), f"{prefix}.sufficiency_test", errors)
        expected_claim_hash = canonical_sha256(claim, omit_keys={"claim_sha256"})
        certificate_claim_hashes.append(str(claim.get("claim_sha256", "")))
        if claim.get("claim_sha256") != expected_claim_hash:
            _error(errors, "CLAIM_HASH_MISMATCH", f"{prefix}: canonical hash mismatch")
        if claim.get("claim_sha256") not in provenance_hashes:
            _error(errors, "EVIDENCE_PROVENANCE_OPEN", f"{prefix}: claim hash not in provenance")

        if claim_type == "psychological_construct":
            if (
                statuses.get("repeated_measurement") != "ESTIMATED"
                or statuses.get("external_construct_validity") != "INDEPENDENTLY_REPLICATED"
            ):
                _error(errors, "PSYCHOLOGICAL_INTERPRETATION_UNLICENSED", f"{prefix}: evidence insufficient")
        if claim_type == "clinical_interpretation":
            has_clinical_claim = True
            if (
                statuses.get("repeated_measurement") != "ESTIMATED"
                or statuses.get("external_construct_validity") != "INDEPENDENTLY_REPLICATED"
                or statuses.get("clinical_validation") != "INDEPENDENTLY_REPLICATED"
            ):
                _error(errors, "CLINICAL_INTERPRETATION_UNLICENSED", f"{prefix}: evidence insufficient")

    if ledger and sorted(map(str, ledger.get("claim_hashes", []))) != sorted(
        certificate_claim_hashes
    ):
        _error(
            errors,
            "EVIDENCE_LEDGER_SCOPE_MISMATCH",
            "ledger must bind the complete certificate claim-hash set",
        )

    if has_clinical_claim:
        signoff_binding = payload.get("human_signoff")
        signoff = _bound_json(base_dir, signoff_binding, "human_signoff", errors)
        signoff_hash = signoff_binding.get("sha256") if isinstance(signoff_binding, dict) else None
        if signoff_hash not in provenance_hashes:
            _error(errors, "CLINICAL_INTERPRETATION_UNLICENSED", "signoff hash not in provenance")
        required_signoff = {"signoff_id", "status", "signer_id", "signed_at", "scope"}
        if (
            not required_signoff.issubset(signoff)
            or signoff.get("status") != "OBTAINED"
            or not _ISO_TIMESTAMP.fullmatch(str(signoff.get("signed_at", "")))
        ):
            _error(errors, "CLINICAL_INTERPRETATION_UNLICENSED", "obtained signed event required")
        if signoff:
            _verify_signed_document(
                signoff,
                "clinical_signoff",
                trusted_authorities,
                "human_signoff",
                errors,
            )
            if (
                signoff.get("contract_id") != expected_contract_id
                or signoff.get("bundle_id") != expected_bundle_id
                or signoff.get("certificate_id") != payload.get("certificate_id")
                or signoff.get("evidence_root_sha256") != evidence_root_sha256
                or sorted(map(str, signoff.get("claim_hashes", [])))
                != sorted(certificate_claim_hashes)
            ):
                _error(
                    errors,
                    "CLINICAL_SIGNOFF_SCOPE_MISMATCH",
                    "signoff must bind certificate, claims, evidence root, contract, and bundle",
                )

    codes = list(dict.fromkeys(error["code"] for error in errors))
    return {
        "status": "V8_EXPLANATION_CERTIFICATE_READY" if not errors else "REFUSE_V8_EXPLANATION_CERTIFICATE",
        "certificate_id": str(payload.get("certificate_id", "")),
        "n_claims": len(claims),
        "refusal_codes": codes,
        "errors": errors,
    }
