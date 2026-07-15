from __future__ import annotations

from suica_core.v7_error_protocol import validate_error_protocol_manifest


def _payload() -> dict[str, object]:
    return {
        "occasion_scope": "global_calendar_occasion",
        "session_order_plan": {"order_source": "timestamp"},
        "carryover_control": {"counterbalanced": True},
        "bundle_sha256": "a" * 64,
        "d_study_target": "both_separately",
        "variance_estimator_ci_method": {"estimator": "REML", "ci": "cluster_bootstrap"},
        "multivariate_geometry_outcome": {
            "estimand": "profile",
            "distance_or_kernel": "mahalanobis",
            "summary_rule": "registered",
        },
        "scoring_perturbation_plan": {
            "scorer_or_embedding_runtime": "alternate",
            "window_or_operator": "registered",
            "reference_norm": "resampled",
            "dependency_resampling": "nested",
        },
    }


def test_error_protocol_accepts_explicit_design() -> None:
    result = validate_error_protocol_manifest(_payload())
    assert result["status"] == "ERROR_DECOMPOSITION_PROTOCOL_READY"


def test_error_protocol_refuses_ambiguous_occasion() -> None:
    payload = _payload()
    payload["occasion_scope"] = "occasion"
    assert validate_error_protocol_manifest(payload)["status"] == "REFUSE_ERROR_PROTOCOL_OCCASION_SCOPE"


def test_error_protocol_refuses_missing_reference_resampling() -> None:
    payload = _payload()
    del payload["scoring_perturbation_plan"]["reference_norm"]  # type: ignore[index]
    assert validate_error_protocol_manifest(payload)["status"] == "REFUSE_ERROR_PROTOCOL_PERTURBATION_PLAN"
