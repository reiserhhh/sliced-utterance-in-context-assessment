"""Protocol-level eligibility for a future SUICA error decomposition.

This module does not estimate reliability. It validates that the design
metadata are explicit enough to distinguish relative and absolute decisions,
occasion effects, carryover, scoring-runtime perturbations, and multivariate
geometry uncertainty before a G-study or latent-state-trait model is fitted.
"""
from __future__ import annotations

from typing import Any


REQUIRED_FIELDS = {
    "occasion_scope",
    "session_order_plan",
    "carryover_control",
    "bundle_sha256",
    "d_study_target",
    "variance_estimator_ci_method",
    "multivariate_geometry_outcome",
    "scoring_perturbation_plan",
}

ALLOWED_OCCASION_SCOPES = {"global_calendar_occasion", "nested_within_participant"}
ALLOWED_D_STUDY_TARGETS = {"relative_rank_order", "absolute_level", "both_separately"}


def validate_error_protocol_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate a design contract without claiming an empirical error model."""
    missing = sorted(REQUIRED_FIELDS.difference(payload))
    if missing:
        return {"status": "REFUSE_ERROR_PROTOCOL_MISSING_FIELDS", "missing_fields": missing}

    if str(payload["occasion_scope"]) not in ALLOWED_OCCASION_SCOPES:
        return {
            "status": "REFUSE_ERROR_PROTOCOL_OCCASION_SCOPE",
            "allowed": sorted(ALLOWED_OCCASION_SCOPES),
        }
    if str(payload["d_study_target"]) not in ALLOWED_D_STUDY_TARGETS:
        return {
            "status": "REFUSE_ERROR_PROTOCOL_DECISION_TARGET",
            "allowed": sorted(ALLOWED_D_STUDY_TARGETS),
        }
    for field in ("session_order_plan", "carryover_control", "variance_estimator_ci_method"):
        if not isinstance(payload[field], dict) or not payload[field]:
            return {"status": "REFUSE_ERROR_PROTOCOL_INCOMPLETE_PLAN", "field": field}

    outcome = payload["multivariate_geometry_outcome"]
    required_outcome = {"estimand", "distance_or_kernel", "summary_rule"}
    if not isinstance(outcome, dict) or not required_outcome.issubset(outcome):
        return {
            "status": "REFUSE_ERROR_PROTOCOL_MULTIVARIATE_OUTCOME",
            "required_fields": sorted(required_outcome),
        }

    perturbation = payload["scoring_perturbation_plan"]
    required_perturbation = {
        "scorer_or_embedding_runtime",
        "window_or_operator",
        "reference_norm",
        "dependency_resampling",
    }
    if not isinstance(perturbation, dict) or not required_perturbation.issubset(perturbation):
        return {
            "status": "REFUSE_ERROR_PROTOCOL_PERTURBATION_PLAN",
            "required_fields": sorted(required_perturbation),
        }

    bundle_hash = str(payload["bundle_sha256"]).strip()
    if len(bundle_hash) != 64 or any(character not in "0123456789abcdefABCDEF" for character in bundle_hash):
        return {"status": "REFUSE_ERROR_PROTOCOL_BUNDLE_HASH"}

    return {
        "status": "ERROR_DECOMPOSITION_PROTOCOL_READY",
        "occasion_scope": str(payload["occasion_scope"]),
        "d_study_target": str(payload["d_study_target"]),
        "claim_boundary": (
            "Protocol eligibility only. Reliability, state-trait separation, "
            "minimum detectable difference, and personality validity remain unestimated."
        ),
    }
