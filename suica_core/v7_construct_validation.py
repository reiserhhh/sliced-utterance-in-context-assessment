"""Stricter post-freeze construct-validation eligibility for SUICA V7.

The validator builds on the existing anchor freeze gate. It does not read a
label or compute an association; it verifies that a future anchor study can
separate convergence, method artifacts, and scoring-runtime perturbations.
"""
from __future__ import annotations

from typing import Any

from suica_core.v7_validation import validate_external_anchor_manifest


REQUIRED_CONSTRUCT_FIELDS = {
    "convergence_hypotheses",
    "discriminant_artifact_controls",
    "score_perturbation_plan",
    "anchor_method_independent",
    "confirmation_decision_rule",
    "score_cohort_membership_commitment",
    "anchor_cohort_membership_commitment",
    "anchor_reliability_plan",
    "effect_size_thresholds",
    "incremental_validity_plan",
    "independent_replication_plan",
}


def validate_construct_validation_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    """Require a frozen MTMM-style plan before any external criterion is read."""
    anchor = validate_external_anchor_manifest(payload)
    if anchor["status"] != "EXTERNAL_ANCHOR_PROTOCOL_READY":
        return {"status": "REFUSE_CONSTRUCT_VALIDATION_ANCHOR_GATE", "anchor_gate": anchor}
    missing = sorted(REQUIRED_CONSTRUCT_FIELDS.difference(payload))
    if missing:
        return {"status": "REFUSE_CONSTRUCT_VALIDATION_PLAN", "missing_fields": missing}
    if not isinstance(payload["convergence_hypotheses"], list) or not payload["convergence_hypotheses"]:
        return {"status": "REFUSE_CONSTRUCT_VALIDATION_PLAN", "reason": "convergence_hypotheses_must_be_nonempty_list"}
    controls = payload["discriminant_artifact_controls"]
    if not isinstance(controls, list) or not {"text_length", "format_or_structure", "prompt_or_condition"}.issubset({str(value) for value in controls}):
        return {
            "status": "REFUSE_CONSTRUCT_VALIDATION_PLAN",
            "reason": "missing_required_method_artifact_controls",
            "required_controls": ["text_length", "format_or_structure", "prompt_or_condition"],
        }
    perturbation = payload["score_perturbation_plan"]
    required_perturbations = {"scorer_or_embedding_runtime", "window_or_operator", "predeclared_stability_rule"}
    if not isinstance(perturbation, dict) or not required_perturbations.issubset(set(perturbation)):
        return {
            "status": "REFUSE_CONSTRUCT_VALIDATION_PLAN",
            "reason": "missing_score_perturbation_plan",
            "required_perturbations": sorted(required_perturbations),
        }
    if bool(payload["anchor_method_independent"]) is not True:
        return {"status": "REFUSE_CONSTRUCT_VALIDATION_PLAN", "reason": "anchor_method_independence_not_declared"}
    if not isinstance(payload["confirmation_decision_rule"], dict) or not payload["confirmation_decision_rule"]:
        return {"status": "REFUSE_CONSTRUCT_VALIDATION_PLAN", "reason": "missing_confirmation_decision_rule"}
    if str(payload["score_cohort_membership_commitment"]) == str(payload["anchor_cohort_membership_commitment"]):
        return {"status": "REFUSE_CONSTRUCT_VALIDATION_PLAN", "reason": "cohort_membership_commitments_must_differ"}
    for field in (
        "anchor_reliability_plan",
        "effect_size_thresholds",
        "incremental_validity_plan",
        "independent_replication_plan",
    ):
        if not isinstance(payload[field], dict) or not payload[field]:
            return {"status": "REFUSE_CONSTRUCT_VALIDATION_PLAN", "reason": f"missing_or_invalid_{field}"}
    reliability = payload["anchor_reliability_plan"]
    if not {"estimate_or_source", "attenuation_handling"}.issubset(reliability):
        return {
            "status": "REFUSE_CONSTRUCT_VALIDATION_PLAN",
            "reason": "anchor_reliability_plan_incomplete",
        }
    thresholds = payload["effect_size_thresholds"]
    if not {"convergent_minimum", "incremental_minimum", "uncertainty_rule"}.issubset(thresholds):
        return {
            "status": "REFUSE_CONSTRUCT_VALIDATION_PLAN",
            "reason": "effect_size_thresholds_incomplete",
        }
    return {
        "status": "CONSTRUCT_VALIDATION_PROTOCOL_READY",
        "n_convergence_hypotheses": len(payload["convergence_hypotheses"]),
        "claim_boundary": (
            "Protocol eligibility only. Passing it does not establish a trait, "
            "personality construct, clinical score, or external association."
        ),
    }
