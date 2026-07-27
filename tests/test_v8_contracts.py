from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import jsonschema
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from suica_core.v8_aggregation import aggregate_semantic_observations
from suica_core.v8_contracts import (
    CONTROLLED_RENDERER_TEMPLATES,
    canonical_sha256,
    validate_assessment_contract,
    validate_explanation_certificate,
)


ROOT = Path(__file__).resolve().parents[1]
SMOKE_ACTIVE_SHA256 = "22f71780a9eb4da8ac8d50a9fb2ba84a689d692e23b1de1064203d9634f398ba"
SMOKE_AUTHORITIES = json.loads(
    (ROOT / "configs" / "v8_trusted_authorities.smoke.json").read_text(encoding="utf-8")
)
TEST_AUTHORITY_ID = "test-independent-authority"
TEST_PRIVATE_KEY = Ed25519PrivateKey.from_private_bytes(bytes.fromhex("42" * 32))
TEST_PUBLIC_KEY_HEX = TEST_PRIVATE_KEY.public_key().public_bytes(
    Encoding.Raw,
    PublicFormat.Raw,
).hex()
TEST_AUTHORITIES = {
    TEST_AUTHORITY_ID: {
        "public_key_hex": TEST_PUBLIC_KEY_HEX,
        "purposes": [
            "language_license",
            "evidence_status_ledger",
            "clinical_signoff",
        ],
        "authorized_signer_ids": ["licensed-human-reviewer"],
    }
}


def valid_contract() -> dict:
    return json.loads(
        (ROOT / "configs" / "v8_assessment_contract.smoke.json").read_text(encoding="utf-8")
    )


def checked_contract(payload: dict) -> dict:
    return validate_assessment_contract(
        payload,
        base_dir=ROOT,
        expected_active_sha256=SMOKE_ACTIVE_SHA256,
        trusted_authorities=SMOKE_AUTHORITIES,
    )


def checked_certificate(payload: dict, base_dir: Path) -> dict:
    return validate_explanation_certificate(
        payload,
        base_dir=base_dir,
        trusted_authorities=TEST_AUTHORITIES,
        expected_contract_id="SU8-CONTRACT-0001",
        expected_bundle_id="SU8-BUNDLE-0001",
    )


def _write_artifact(root: Path, name: str, value: object) -> tuple[str, str]:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, (dict, list)):
        rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    else:
        rendered = str(value)
    path.write_text(rendered, encoding="utf-8")
    return str(path.relative_to(root)), hashlib.sha256(path.read_bytes()).hexdigest()


def _signed_document(value: dict, purpose: str) -> dict:
    document = {
        **value,
        "issuer_authority_id": TEST_AUTHORITY_ID,
        "purpose": purpose,
    }
    message = json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    document["signature_hex"] = TEST_PRIVATE_KEY.sign(message).hex()
    return document


def _hashed_node(
    node_id: str,
    kind: str,
    artifact_path: str,
    artifact_hash: str,
    observed_value: float,
) -> dict:
    node = {
        "node_id": node_id,
        "kind": kind,
        "artifact_path": artifact_path,
        "artifact_hash": artifact_hash,
        "source_span_ids": [f"span-{node_id}"],
        "measurement_field": "relative_geometry.coordinate_1",
        "observed_value": observed_value,
        "node_sha256": "",
    }
    node["node_sha256"] = canonical_sha256(node, omit_keys={"node_sha256"})
    return node


def _rehash_claim(claim: dict) -> None:
    for binding in claim["sentence_bindings"]:
        binding["binding_sha256"] = canonical_sha256(
            binding,
            omit_keys={"binding_sha256"},
        )
    claim["claim_sha256"] = canonical_sha256(claim, omit_keys={"claim_sha256"})


def valid_certificate(
    root: Path,
    *,
    claim_type: str = "technical_measurement_object",
    validated: bool = False,
) -> dict:
    template_by_type = {
        value[0]: (template_id, value[1])
        for template_id, value in CONTROLLED_RENDERER_TEMPLATES.items()
    }
    template_id, statement = template_by_type[claim_type]
    support_path, support_hash = _write_artifact(
        root,
        "artifacts/support.json",
        {
            "source_spans": {"span-E-positive-1": {"text_sha256": "a" * 64}},
            "measurements": {"relative_geometry.coordinate_1": {"value": 0.4}},
        },
    )
    counter_path, counter_hash = _write_artifact(
        root,
        "artifacts/counter.json",
        {
            "source_spans": {"span-E-negative-1": {"text_sha256": "b" * 64}},
            "measurements": {"relative_geometry.coordinate_1": {"value": 0.1}},
        },
    )
    assert support_path and counter_path

    license_payload = _signed_document({
        "license_id": f"license-{claim_type}",
        "license_type": claim_type,
        "contract_id": "SU8-CONTRACT-0001",
        "bundle_id": "SU8-BUNDLE-0001",
        "allowed_claim_types": [claim_type],
        "allowed_renderer_templates": [template_id],
        "issued_by": "independent-fixture-authority",
    }, "language_license")
    license_path, license_hash = _write_artifact(root, "licenses/license.json", license_payload)
    statuses = {
        "repeated_measurement": "ESTIMATED" if validated else "UNTESTED",
        "external_construct_validity": (
            "INDEPENDENTLY_REPLICATED" if validated else "UNTESTED"
        ),
        "clinical_validation": (
            "INDEPENDENTLY_REPLICATED"
            if validated and claim_type == "clinical_interpretation"
            else "UNTESTED"
        ),
    }
    evidence_graph = {
        "E-positive-1": _hashed_node(
            "E-positive-1",
            "supporting",
            support_path,
            support_hash,
            0.4,
        ),
        "E-negative-1": _hashed_node(
            "E-negative-1",
            "counterevidence",
            counter_path,
            counter_hash,
            0.1,
        ),
    }
    evidence_root_sha256 = canonical_sha256(evidence_graph)
    counterfactual = {
        "performed": True,
        "paired_delta": 0.3,
        "matched_random_delta": 0.05,
        "ci_lower": 0.15,
        "ci_upper": 0.45,
    }
    binding = {
        "sentence_id": "S1",
        "claim_id": "C1",
        "evidence_ids": ["E-positive-1", "E-negative-1"],
        "binding_sha256": "",
    }
    claim = {
        "claim_id": "C1",
        "statement": statement,
        "claim_type": claim_type,
        "renderer_template_id": template_id,
        "evidence_ids": ["E-positive-1"],
        "counterevidence_ids": ["E-negative-1"],
        "necessity_test": deepcopy(counterfactual),
        "sufficiency_test": deepcopy(counterfactual),
        "sentence_bindings": [binding],
        "artifact_hashes": [
            support_hash,
            counter_hash,
            evidence_graph["E-positive-1"]["node_sha256"],
            evidence_graph["E-negative-1"]["node_sha256"],
        ],
        "claim_sha256": "",
    }
    _rehash_claim(claim)
    ledger_payload = _signed_document(
        {
            "ledger_id": "ledger-1",
            "contract_id": "SU8-CONTRACT-0001",
            "bundle_id": "SU8-BUNDLE-0001",
            "evidence_root_sha256": evidence_root_sha256,
            "claim_hashes": [claim["claim_sha256"]],
            "statuses": statuses,
        },
        "evidence_status_ledger",
    )
    ledger_path, ledger_hash = _write_artifact(root, "ledgers/evidence.json", ledger_payload)

    provenance_hashes = [
        support_hash,
        counter_hash,
        evidence_graph["E-positive-1"]["node_sha256"],
        evidence_graph["E-negative-1"]["node_sha256"],
        claim["claim_sha256"],
        license_hash,
        ledger_hash,
    ]
    certificate = {
        "certificate_id": "SU8-CERT-0001",
        "contract_id": "SU8-CONTRACT-0001",
        "measurement_status": "MEASUREMENT_READY",
        "support_status": "IN_SUPPORT",
        "evidence_graph": evidence_graph,
        "claims": [claim],
        "uncertainty": {"combination_method": "joint_nested", "interval": [-0.2, 0.6]},
        "provenance": {
            "artifact_hashes": provenance_hashes,
            "bundle_id": "SU8-BUNDLE-0001",
        },
        "language_license": {
            "path": license_path,
            "sha256": license_hash,
            "license_id": license_payload["license_id"],
        },
        "evidence_status_ledger": {"path": ledger_path, "sha256": ledger_hash},
    }
    if claim_type == "clinical_interpretation" and validated:
        signoff = _signed_document({
            "signoff_id": "signoff-1",
            "status": "OBTAINED",
            "signer_id": "licensed-human-reviewer",
            "signed_at": "2026-07-24T12:00:00Z",
            "scope": "synthetic fixture only",
            "contract_id": "SU8-CONTRACT-0001",
            "bundle_id": "SU8-BUNDLE-0001",
            "certificate_id": "SU8-CERT-0001",
            "evidence_root_sha256": evidence_root_sha256,
            "claim_hashes": [claim["claim_sha256"]],
        }, "clinical_signoff")
        signoff_path, signoff_hash = _write_artifact(root, "signoffs/signoff.json", signoff)
        certificate["human_signoff"] = {"path": signoff_path, "sha256": signoff_hash}
        certificate["provenance"]["artifact_hashes"].append(signoff_hash)
    return certificate


def test_valid_v8_contract_is_ready() -> None:
    assert (
        checked_contract(valid_contract())["status"]
        == "V8_ASSESSMENT_CONTRACT_READY"
    )


def test_repository_template_refuses_unresolved_placeholders() -> None:
    payload = json.loads(
        (ROOT / "configs" / "v8_assessment_contract.template.json").read_text(encoding="utf-8")
    )
    result = checked_contract(payload)
    assert result["status"] == "REFUSE_V8_ASSESSMENT_CONTRACT"
    assert "UNRESOLVED_PLACEHOLDER" in result["refusal_codes"]


def test_contract_refuses_without_actual_artifact_verification() -> None:
    result = validate_assessment_contract(valid_contract())
    assert "ARTIFACT_BINDING_UNVERIFIED" in result["refusal_codes"]


def test_llm_copy_through_personality_score_is_refused() -> None:
    payload = valid_contract()
    payload["semantic_transducer"]["output_fields"].append("personality_score")
    payload["measurement_bundle"]["allowed_input_fields"].append("personality_score")
    result = checked_contract(payload)
    assert "LLM_PERSON_LEVEL_OUTPUT_FORBIDDEN" in result["refusal_codes"]


def test_unfrozen_aggregator_entrypoint_is_refused() -> None:
    payload = valid_contract()
    payload["measurement_bundle"]["aggregator_entrypoint"] = "malicious:copy_personality_score"
    result = checked_contract(payload)
    assert "UNFROZEN_AGGREGATOR" in result["refusal_codes"]


def test_active_bundle_cannot_be_changed_by_declaration() -> None:
    payload = valid_contract()
    payload["adaptation_policy"]["active_sha256_after"] = "f" * 64
    result = checked_contract(payload)
    assert "ACTIVE_BUNDLE_MUTATED" in result["refusal_codes"]


def test_external_active_root_rejects_internally_consistent_replacement() -> None:
    result = validate_assessment_contract(
        valid_contract(),
        base_dir=ROOT,
        expected_active_sha256="f" * 64,
        trusted_authorities=SMOKE_AUTHORITIES,
    )
    assert "EXTERNAL_TRUST_ROOT_MISMATCH" in result["refusal_codes"]


def test_auditor_alias_cannot_mask_same_runtime_and_session() -> None:
    payload = valid_contract()
    builder = payload["role_separation"]["builder"]
    auditor = payload["role_separation"]["auditor"]
    auditor.update({
        "agent_id": "auditor-alias",
        "session_id": builder["session_id"],
        "runtime_sha256": builder["runtime_sha256"],
        "implementation_sha256": builder["implementation_sha256"],
    })
    result = checked_contract(payload)
    assert "LLM_SELF_AUDIT_FORBIDDEN" in result["refusal_codes"]
    assert "AUDITOR_ATTESTATION_MISMATCH" in result["refusal_codes"]


def test_auditor_attestation_cannot_replay_to_another_contract() -> None:
    payload = valid_contract()
    payload["contract_id"] = "SU8-CONTRACT-REPLAY-TARGET"
    result = checked_contract(payload)
    assert "AUDITOR_ATTESTATION_MISMATCH" in result["refusal_codes"]


def test_q_and_B_refuse_without_identifying_design() -> None:
    payload = valid_contract()
    payload["data_requirements"]["opportunity_menu_logging"] = False
    payload["data_requirements"]["randomized_repeated_conditions"] = False
    result = checked_contract(payload)
    assert "FREE_SELECTION_Q_NOT_IDENTIFIED" in result["refusal_codes"]
    assert "FIXED_RESPONSE_B_NOT_IDENTIFIED" in result["refusal_codes"]


def test_deterministic_aggregator_rejects_person_level_field() -> None:
    row = {
        "observation_id": "o1",
        "segment_id": "s1",
        "event_type": "self_reference",
        "source_span_ids": ["span-1"],
        "polarity": 0.1,
        "intensity": 0.4,
        "confidence": 0.9,
        "abstain": False,
        "diagnosis": "forbidden",
    }
    with pytest.raises(ValueError, match="forbidden fields"):
        aggregate_semantic_observations([row])


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_span_ids", []),
        ("polarity", 999.0),
        ("intensity", 999.0),
        ("confidence", float("nan")),
    ],
)
def test_deterministic_aggregator_enforces_frozen_schema_ranges(
    field: str,
    value: object,
) -> None:
    row = {
        "observation_id": "o1",
        "segment_id": "s1",
        "event_type": "self_reference",
        "source_span_ids": ["span-1"],
        "polarity": 0.1,
        "intensity": 0.4,
        "confidence": 0.9,
        "abstain": False,
    }
    row[field] = value
    with pytest.raises(ValueError):
        aggregate_semantic_observations([row])


def test_valid_technical_explanation_certificate_is_ready(tmp_path: Path) -> None:
    certificate = valid_certificate(tmp_path)
    result = checked_certificate(certificate, tmp_path)
    assert result["status"] == "V8_EXPLANATION_CERTIFICATE_READY"


def test_certificate_cannot_swap_contract_or_bundle(tmp_path: Path) -> None:
    certificate = valid_certificate(tmp_path)
    certificate["contract_id"] = "attacker-contract"
    certificate["provenance"]["bundle_id"] = "attacker-bundle"
    result = checked_certificate(certificate, tmp_path)
    assert "EXTERNAL_TRUST_ROOT_MISMATCH" in result["refusal_codes"]


def test_signed_authorizations_cannot_replay_across_contract_or_bundle(tmp_path: Path) -> None:
    certificate = valid_certificate(
        tmp_path,
        claim_type="clinical_interpretation",
        validated=True,
    )
    certificate["contract_id"] = "SU8-CONTRACT-REPLAY-TARGET"
    certificate["provenance"]["bundle_id"] = "SU8-BUNDLE-REPLAY-TARGET"
    result = validate_explanation_certificate(
        certificate,
        base_dir=tmp_path,
        trusted_authorities=TEST_AUTHORITIES,
        expected_contract_id="SU8-CONTRACT-REPLAY-TARGET",
        expected_bundle_id="SU8-BUNDLE-REPLAY-TARGET",
    )
    assert "LANGUAGE_LICENSE_SCOPE_MISMATCH" in result["refusal_codes"]
    assert "EVIDENCE_LEDGER_SCOPE_MISMATCH" in result["refusal_codes"]
    assert "CLINICAL_SIGNOFF_SCOPE_MISMATCH" in result["refusal_codes"]


def test_deleted_evidence_artifact_is_refused(tmp_path: Path) -> None:
    certificate = valid_certificate(tmp_path)
    (tmp_path / certificate["evidence_graph"]["E-positive-1"]["artifact_path"]).unlink()
    result = checked_certificate(certificate, tmp_path)
    assert "BOUND_ARTIFACT_MISSING" in result["refusal_codes"]


def test_builder_cannot_self_issue_replicated_evidence_ledger(tmp_path: Path) -> None:
    certificate = valid_certificate(tmp_path, claim_type="psychological_construct")
    ledger_path = tmp_path / certificate["evidence_status_ledger"]["path"]
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    old_hash = certificate["evidence_status_ledger"]["sha256"]
    ledger["statuses"]["repeated_measurement"] = "ESTIMATED"
    ledger["statuses"]["external_construct_validity"] = "INDEPENDENTLY_REPLICATED"
    ledger_path.write_text(
        json.dumps(ledger, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    new_hash = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    certificate["evidence_status_ledger"]["sha256"] = new_hash
    provenance = certificate["provenance"]["artifact_hashes"]
    provenance[provenance.index(old_hash)] = new_hash
    result = checked_certificate(certificate, tmp_path)
    assert "TRUSTED_SIGNATURE_INVALID" in result["refusal_codes"]


def test_freeform_clinical_language_cannot_hide_as_technical(tmp_path: Path) -> None:
    certificate = valid_certificate(tmp_path)
    certificate["claims"][0]["statement"] = "This person has depression and a neurotic personality."
    _rehash_claim(certificate["claims"][0])
    result = checked_certificate(certificate, tmp_path)
    assert "FREEFORM_INTERPRETATION_FORBIDDEN" in result["refusal_codes"]


def test_evidence_shell_and_dangling_sentence_binding_are_refused(tmp_path: Path) -> None:
    certificate = valid_certificate(tmp_path)
    certificate["evidence_graph"]["E-positive-1"].pop("observed_value")
    binding = certificate["claims"][0]["sentence_bindings"][0]
    binding["evidence_ids"] = ["E-does-not-exist"]
    _rehash_claim(certificate["claims"][0])
    result = checked_certificate(certificate, tmp_path)
    assert "EVIDENCE_NODE_INVALID" in result["refusal_codes"]
    assert "SENTENCE_BINDING_INVALID" in result["refusal_codes"]


def test_counterfactual_requires_paired_interval_excluding_zero(tmp_path: Path) -> None:
    certificate = valid_certificate(tmp_path)
    certificate["claims"][0]["sufficiency_test"]["ci_lower"] = -0.01
    _rehash_claim(certificate["claims"][0])
    result = checked_certificate(certificate, tmp_path)
    assert "COUNTERFACTUAL_FIDELITY_NOT_DEMONSTRATED" in result["refusal_codes"]


def test_psychological_language_requires_bound_replicated_ledger(tmp_path: Path) -> None:
    unlicensed = valid_certificate(tmp_path / "unlicensed", claim_type="psychological_construct")
    result = checked_certificate(unlicensed, tmp_path / "unlicensed")
    assert "PSYCHOLOGICAL_INTERPRETATION_UNLICENSED" in result["refusal_codes"]

    licensed = valid_certificate(
        tmp_path / "licensed",
        claim_type="psychological_construct",
        validated=True,
    )
    assert (
        checked_certificate(licensed, tmp_path / "licensed")["status"]
        == "V8_EXPLANATION_CERTIFICATE_READY"
    )


def test_clinical_language_requires_bound_human_signoff(tmp_path: Path) -> None:
    no_signoff = valid_certificate(
        tmp_path / "no-signoff",
        claim_type="clinical_interpretation",
        validated=False,
    )
    result = checked_certificate(no_signoff, tmp_path / "no-signoff")
    assert "CLINICAL_INTERPRETATION_UNLICENSED" in result["refusal_codes"]

    signed = valid_certificate(
        tmp_path / "signed",
        claim_type="clinical_interpretation",
        validated=True,
    )
    assert (
        checked_certificate(signed, tmp_path / "signed")["status"]
        == "V8_EXPLANATION_CERTIFICATE_READY"
    )

    signoff_path = tmp_path / "signed" / signed["human_signoff"]["path"]
    signoff = json.loads(signoff_path.read_text(encoding="utf-8"))
    old_hash = signed["human_signoff"]["sha256"]
    signoff["signer_id"] = "claim-producing-builder"
    signoff = _signed_document(
        {
            key: value
            for key, value in signoff.items()
            if key not in {"issuer_authority_id", "purpose", "signature_hex"}
        },
        "clinical_signoff",
    )
    signoff_path.write_text(
        json.dumps(signoff, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    new_hash = hashlib.sha256(signoff_path.read_bytes()).hexdigest()
    signed["human_signoff"]["sha256"] = new_hash
    hashes = signed["provenance"]["artifact_hashes"]
    hashes[hashes.index(old_hash)] = new_hash
    result = checked_certificate(signed, tmp_path / "signed")
    assert "UNTRUSTED_AUTHORITY" in result["refusal_codes"]


def test_json_schemas_and_python_validator_reject_same_structural_attacks(
    tmp_path: Path,
) -> None:
    assessment_schema = json.loads(
        (ROOT / "schemas" / "v8_assessment_contract.schema.json").read_text(encoding="utf-8")
    )
    explanation_schema = json.loads(
        (ROOT / "schemas" / "v8_explanation_certificate.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.Draft202012Validator.check_schema(assessment_schema)
    jsonschema.Draft202012Validator.check_schema(explanation_schema)
    jsonschema.validate(valid_contract(), assessment_schema)
    certificate = valid_certificate(tmp_path)
    jsonschema.validate(certificate, explanation_schema)

    attacked_contract = valid_contract()
    attacked_contract["semantic_transducer"]["output_fields"].append("diagnosis")
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(attacked_contract, assessment_schema)
    assert (
        checked_contract(attacked_contract)["status"]
        == "REFUSE_V8_ASSESSMENT_CONTRACT"
    )

    unknown_contract = valid_contract()
    unknown_contract["self_declared_override"] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(unknown_contract, assessment_schema)
    assert checked_contract(unknown_contract)["status"] == "REFUSE_V8_ASSESSMENT_CONTRACT"

    geometry_only = valid_contract()
    geometry_only["measurement_components"] = ["relative_geometry"]
    geometry_only["data_requirements"] = {
        "opportunity_menu_logging": False,
        "selection_flag": False,
        "randomized_repeated_conditions": False,
        "minimum_sessions_per_person_condition": 0,
        "state_occasion_defined": False,
    }
    jsonschema.validate(geometry_only, assessment_schema)
    assert checked_contract(geometry_only)["status"] == "V8_ASSESSMENT_CONTRACT_READY"

    attacked_certificate = valid_certificate(tmp_path / "attack")
    attacked_certificate["evidence_graph"]["E-positive-1"]["untyped_payload"] = "shell"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(attacked_certificate, explanation_schema)
    assert (
        checked_certificate(attacked_certificate, tmp_path / "attack")["status"]
        == "REFUSE_V8_EXPLANATION_CERTIFICATE"
    )


@pytest.mark.parametrize(
    "mutator",
    [
        lambda payload: payload["semantic_transducer"]["decoding"].update({"top_p": 2.0}),
        lambda payload: payload["uncertainty_policy"]["components"].append("unregistered_noise"),
        lambda payload: payload["data_requirements"].update(
            {"minimum_sessions_per_person_condition": "2"}
        ),
    ],
)
def test_cli_validator_enforces_canonical_json_schema(mutator) -> None:
    payload = valid_contract()
    mutator(payload)
    result = checked_contract(payload)
    assert "JSON_SCHEMA_INVALID" in result["refusal_codes"]


def test_nonfinite_top_p_is_refused_by_direct_validator() -> None:
    payload = valid_contract()
    payload["semantic_transducer"]["decoding"]["top_p"] = float("nan")
    result = checked_contract(payload)
    assert "UNVERSIONED_SEMANTIC_TRANSDUCER" in result["refusal_codes"]


def test_cli_rejects_nonstandard_nan_json(tmp_path: Path) -> None:
    contract = tmp_path / "nan-contract.json"
    contract.write_text('{"top_p": NaN}\n', encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "validate_suica_v8_contract.py"),
            "--contract",
            str(contract),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 2
    assert '"INVALID_JSON"' in completed.stdout
