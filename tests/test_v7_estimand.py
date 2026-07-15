from __future__ import annotations

from suica_core.v7_estimand import validate_estimand, validate_estimand_registry


def _relative_manifest() -> dict:
    return {
        "estimand_id": "example-relative",
        "version": "v1",
        "target_object": "relative_geometry",
        "reference_population": {"id": "r", "sampling_frame": "s", "decision_scope": "relative"},
        "occasion_definition": {"unit": "comment", "replication_rule": "disjoint", "source_provenance": "rows"},
        "operator_registry": {"registry_id": "ops", "operators": ["native"]},
        "representation": {"id": "rep", "frozen_before_confirmation": True},
        "null_hypothesis": "null",
        "minimum_detectable_effect": {"metric": "auc", "value": 0.1, "direction": "greater"},
        "decision_rule": {"alpha": 0.05, "multiplicity": "holm", "pass_status": "PASS", "refuse_status": "REFUSE"},
        "claim_boundary": "technical only",
    }


def test_valid_relative_estimand_is_ready() -> None:
    result = validate_estimand(_relative_manifest())
    assert result["status"] == "ESTIMAND_READY"
    assert not result["errors"]


def test_fixed_coordinate_requires_a_symmetry_breaker() -> None:
    manifest = _relative_manifest() | {"target_object": "fixed_coordinate"}
    result = validate_estimand(manifest)
    assert result["status"] == "REFUSE_ESTIMAND_UNDECLARED"
    assert any("symmetry_breaker" in value for value in result["errors"])


def test_fixed_response_requires_two_randomized_sessions() -> None:
    manifest = _relative_manifest() | {
        "target_object": "fixed_response_B",
        "data_requirements": {"randomized_assignment": True, "minimum_sessions_per_person_condition": 1},
    }
    result = validate_estimand(manifest)
    assert result["status"] == "REFUSE_ESTIMAND_UNDECLARED"
    assert any(">= 2" in value for value in result["errors"])


def test_registry_refuses_duplicate_ids() -> None:
    manifest = _relative_manifest()
    result = validate_estimand_registry({"registry_version": "v1", "manifests": [manifest, manifest]})
    assert result["status"] == "REFUSE_ESTIMAND_UNDECLARED"
    assert result["n_refused"] == 1
