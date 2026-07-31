"""Adversarial checks for the SUICA pre-experiment foundation contract."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from suica_core.foundation_contracts import validate_foundation_study


ROOT = Path(__file__).resolve().parents[1]
SMOKE_PATH = ROOT / "configs" / "suica_foundation_study.smoke.json"
TEMPLATE_PATH = ROOT / "configs" / "suica_foundation_study.template.json"
CLI_PATH = ROOT / "scripts" / "validate_suica_foundation_study.py"


@pytest.fixture()
def smoke() -> dict:
    return json.loads(SMOKE_PATH.read_text(encoding="utf-8"))


def refusal_codes(payload: dict) -> set[str]:
    return set(validate_foundation_study(payload)["refusal_codes"])


def l45_contract(smoke: dict) -> dict:
    """Promote the smoke contract to one bounded E45 discovery contract."""
    payload = copy.deepcopy(smoke)
    opening_id = "F05-L45-REFERENCE-FRAME"
    payload["study_id"] = "SUICA-L45-REFERENCE-FRAME-OPENED-DISCOVERY-V1"
    payload["study_question"]["targeted_openings"] = [opening_id]
    payload["claim"]["target_layer"] = "L5_measurement_score"
    payload["claim"]["edge_licenses"].append({
        "edge": "E45_reference_scoring",
        "status": "bounded_open",
        "assumptions": [
            "Reference, fit, and scored panels are disjoint.",
            "The target facet measure and reference chart are frozen."
        ],
        "evidence_or_test": (
            "Ten synthetic positive, shift, alias, and refusal worlds."
        ),
        "refusal_rule": "Retain L4 when any E45 gate fails.",
        "opening_id": opening_id,
    })
    payload["generalization_universe"]["reference_population"] = {
        "status": "declared",
        "definition": "Balanced synthetic target population version l45-v1.",
        "sampling_rule": "Independent reference-panel author draws.",
        "scope_limit": "Synthetic registered generator only.",
        "refusal_consequence": "Refuse after population definition drift.",
    }
    payload["transformation_chain"]["reference_operator"] = (
        "frozen-lambda weighted center and covariance chart l45-v1"
    )
    payload["error_theory"]["facets"] = sorted(set(
        payload["error_theory"]["facets"]
        + [
            "occasion_time",
            "reference_population",
        ]
    ))
    payload["error_theory"]["reference_uncertainty"] = (
        "Nested observed-only reference-author and event resampling."
    )
    payload["reference_measurement"] = {
        "active": True,
        "reference_frame_id": "synthetic-balanced-reference-l45-v1",
        "reference_population_version": "synthetic-l45-v1",
        "target_facet_measure": "uniform-lambda-over-16-facets-v1",
        "representation_operator_version": "l4-vector-operator-v1",
        "chart_version": "weighted-whitened-chart-v1",
        "occasion_universe": "four independent registered occasions",
        "support_positivity_rule": "lambda support must be observed in every occasion",
        "effective_sample_size_rule": "report minimum importance-weight ESS ratio",
        "selection_identification_rule": "facet provenance and opportunity support required",
        "panel_separation": {
            "reference_fit_disjoint": True,
            "reference_score_disjoint": True,
            "fit_score_disjoint": True,
        },
        "joint_resampling": {
            "reference_population": True,
            "event_sampling": True,
            "occasion_or_operator": True,
        },
        "gauge_output_policy": "reference_coordinates_with_transport_audit",
        "reference_drift_action": "register_new_version_and_recalibrate",
        "event_count_and_composition_separated": True,
    }
    payload["interpretation_boundary"]["licensed_labels"] = [
        "anonymous technical relation",
        "synthetic reference-relative score candidate",
    ]
    payload["interpretation_boundary"]["claim_boundary"] = (
        "Bounded synthetic E45 test; L5 promotion remains blocked."
    )
    return payload


def test_smoke_contract_closes_only_the_declared_l2_to_l4_path(smoke: dict) -> None:
    result = validate_foundation_study(smoke)

    assert result["status"] == "FOUNDATION_CONTRACT_READY"
    assert result["maximum_licensed_layer"] == "L4_technical_object"
    assert result["promotion_blocked"] is False
    assert result["refusal_codes"] == []


def test_template_is_not_an_executable_protocol() -> None:
    payload = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    result = validate_foundation_study(payload)

    assert result["status"] == "REFUSE_EXPERIMENT_START"
    assert "UNRESOLVED_DECLARATION" in result["refusal_codes"]
    assert result["maximum_licensed_layer"] == "L3_representation"


def test_embedded_placeholder_is_rejected(smoke: dict) -> None:
    smoke["claim"]["claim_statement"] = "Observed only; DECLARE_SCOPE_BEFORE_USE"

    assert "UNRESOLVED_DECLARATION" in refusal_codes(smoke)


def test_hidden_edge_jump_is_rejected(smoke: dict) -> None:
    smoke["claim"]["edge_licenses"] = smoke["claim"]["edge_licenses"][:1]
    result = validate_foundation_study(smoke)

    assert result["status"] == "REFUSE_EXPERIMENT_START"
    assert "HIDDEN_INFERENCE_JUMP" in result["refusal_codes"]
    assert result["maximum_licensed_layer"] == "L3_representation"


def test_duplicate_edge_license_is_rejected(smoke: dict) -> None:
    duplicate = copy.deepcopy(smoke["claim"]["edge_licenses"][0])
    duplicate["assumptions"] = ["A different assertion for the same edge."]
    smoke["claim"]["edge_licenses"].append(duplicate)

    assert "DUPLICATE_EDGE_LICENSE" in refusal_codes(smoke)


def test_targeted_bounded_edge_permits_only_the_lower_layer(smoke: dict) -> None:
    edge = smoke["claim"]["edge_licenses"][1]
    edge["status"] = "bounded_open"
    edge["opening_id"] = "OPEN-E34-IDENTIFICATION"
    smoke["study_question"]["targeted_openings"] = ["OPEN-E34-IDENTIFICATION"]
    result = validate_foundation_study(smoke)

    assert result["status"] == "READY_FOR_BOUNDED_FOUNDATION_TEST"
    assert result["maximum_licensed_layer"] == "L3_representation"
    assert result["promotion_blocked"] is True


def test_untargeted_bounded_edge_is_rejected(smoke: dict) -> None:
    edge = smoke["claim"]["edge_licenses"][1]
    edge["status"] = "bounded_open"
    edge["opening_id"] = "OPEN-E34-IDENTIFICATION"

    assert "UNROUTED_OPEN_EDGE" in refusal_codes(smoke)


def test_reference_score_requires_reference_population_and_uncertainty(
    smoke: dict,
) -> None:
    smoke["claim"]["target_layer"] = "L5_measurement_score"
    smoke["claim"]["edge_licenses"].append(
        {
            "edge": "E45_reference_scoring",
            "status": "supported",
            "assumptions": ["Reference scoring is declared."],
            "evidence_or_test": "Reference transport is tested.",
            "refusal_rule": "Refuse on reference drift.",
        }
    )

    codes = refusal_codes(smoke)
    assert "REFERENCE_POPULATION_REQUIRED" in codes
    assert "REFERENCE_UNCERTAINTY_REQUIRED" in codes
    assert "REFERENCE_MEASUREMENT_CONTRACT_REQUIRED" in codes


def test_bounded_l45_contract_is_ready_but_stays_at_l4(
    smoke: dict,
) -> None:
    result = validate_foundation_study(l45_contract(smoke))

    assert result["status"] == "READY_FOR_BOUNDED_FOUNDATION_TEST"
    assert result["maximum_licensed_layer"] == "L4_technical_object"
    assert result["bounded_openings"] == ["F05-L45-REFERENCE-FRAME"]
    assert result["promotion_blocked"] is True
    assert result["refusal_codes"] == []


def test_l45_requires_disjoint_reference_fit_and_score_panels(
    smoke: dict,
) -> None:
    payload = l45_contract(smoke)
    payload["reference_measurement"]["panel_separation"][
        "reference_score_disjoint"
    ] = False

    assert "REFERENCE_PANEL_SEPARATION_REQUIRED" in refusal_codes(payload)


def test_l45_requires_joint_observable_resampling(smoke: dict) -> None:
    payload = l45_contract(smoke)
    payload["reference_measurement"]["joint_resampling"][
        "reference_population"
    ] = False

    assert "JOINT_REFERENCE_RESAMPLING_REQUIRED" in refusal_codes(payload)


def test_l45_requires_reference_error_facets(smoke: dict) -> None:
    payload = l45_contract(smoke)
    payload["error_theory"]["facets"].remove("operator_method")

    assert "REFERENCE_ERROR_FACETS_REQUIRED" in refusal_codes(payload)


def test_context_choice_and_response_channels_cannot_be_collapsed(
    smoke: dict,
) -> None:
    smoke["observation_design"]["choice_channel"] = "not applicable"

    assert "CHOICE_RESPONSE_NOT_SEPARATED" in refusal_codes(smoke)


def test_human_expression_claim_requires_response_process(smoke: dict) -> None:
    smoke["claim"]["source_layer"] = "L1_expression_behavior"
    smoke["claim"]["edge_licenses"].insert(
        0,
        {
            "edge": "E12_capture",
            "status": "supported",
            "assumptions": ["The record captures the declared behavior."],
            "evidence_or_test": "Capture provenance is audited.",
            "refusal_rule": "Refuse when attribution or capture is incomplete.",
        },
    )

    assert "RESPONSE_PROCESS_REQUIRED" in refusal_codes(smoke)


def test_llm_cannot_be_final_scorer(smoke: dict) -> None:
    smoke["transformation_chain"]["llm_role"] = "final_scorer"

    assert "LLM_FINAL_SCORER_FORBIDDEN" in refusal_codes(smoke)


def test_individual_score_requires_l5_and_error_interval(smoke: dict) -> None:
    smoke["claim"]["individual_score_claim"] = True

    codes = refusal_codes(smoke)
    assert "INDIVIDUAL_SCORE_LICENSE_MISMATCH" in codes
    assert "INDIVIDUAL_ERROR_THEORY_REQUIRED" in codes


def test_decision_claim_requires_l7_boundary_and_application_role(
    smoke: dict,
) -> None:
    smoke["claim"]["decision_claim"] = True

    codes = refusal_codes(smoke)
    assert "DECISION_LAYER_MISMATCH" in codes
    assert "DECISION_LICENSE_REQUIRED" in codes
    assert "DECISION_ROLE_MISMATCH" in codes


def test_event_count_cannot_stand_in_for_event_composition(smoke: dict) -> None:
    smoke["error_theory"]["event_count_and_composition_separated"] = False

    assert "EVENT_COMPOSITION_COLLAPSED" in refusal_codes(smoke)


def test_one_alias_world_is_insufficient(smoke: dict) -> None:
    smoke["identification"]["alias_or_counterworlds"] = ["Only one rival world"]

    assert "SCHEMA_VIOLATION" in refusal_codes(smoke)


def test_personality_claim_cannot_terminate_at_technical_object(smoke: dict) -> None:
    smoke["claim"]["personality_claim"] = True

    codes = refusal_codes(smoke)
    assert "PERSONALITY_LAYER_MISMATCH" in codes
    assert "EXTERNAL_CONSTRUCT_EVIDENCE_REQUIRED" in codes


def test_sealed_confirmation_requires_governance_and_fresh_rule(
    smoke: dict,
) -> None:
    smoke["stage"] = "sealed_confirmation"
    smoke["governance"]["preregistered"] = False
    smoke["validation_route"]["fresh_confirmation_rule"] = "not applicable"

    codes = refusal_codes(smoke)
    assert "CONFIRMATION_GOVERNANCE_REQUIRED" in codes
    assert "FRESH_CONFIRMATION_REQUIRED" in codes


@pytest.mark.parametrize(
    ("contract", "expected_code"),
    [
        (SMOKE_PATH, 0),
        (TEMPLATE_PATH, 2),
    ],
)
def test_cli_exit_code_matches_readiness(
    contract: Path,
    expected_code: int,
) -> None:
    completed = subprocess.run(
        [sys.executable, str(CLI_PATH), "--contract", str(contract)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == expected_code
    assert json.loads(completed.stdout)["status"]
