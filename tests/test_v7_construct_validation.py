from __future__ import annotations

import hashlib
from pathlib import Path

from suica_core.v7_construct_validation import validate_construct_validation_manifest


def _payload(bundle: Path) -> dict[str, object]:
    return {
        "bundle_path": str(bundle),
        "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(),
        "pre_freeze_label_access": False,
        "score_cohort_id": "scores",
        "anchor_cohort_id": "anchors",
        "cohort_overlap_count": 0,
        "multiplicity_plan": {"primary": "omnibus"},
        "hypotheses": [{"id": "base"}],
        "convergence_hypotheses": [{"id": "criterion"}],
        "discriminant_artifact_controls": ["text_length", "format_or_structure", "prompt_or_condition"],
        "score_perturbation_plan": {
            "scorer_or_embedding_runtime": "alternate_runtime",
            "window_or_operator": "registered_window_perturbation",
            "predeclared_stability_rule": "concordance",
        },
        "anchor_method_independent": True,
        "score_cohort_membership_commitment": "score-membership-sha",
        "anchor_cohort_membership_commitment": "anchor-membership-sha",
        "anchor_reliability_plan": {
            "estimate_or_source": "independent",
            "attenuation_handling": "separate",
        },
        "effect_size_thresholds": {
            "convergent_minimum": 0.1,
            "incremental_minimum": 0.02,
            "uncertainty_rule": "ci",
        },
        "incremental_validity_plan": {"comparison": "nested"},
        "independent_replication_plan": {"population": "new"},
        "confirmation_decision_rule": {"convergence": "max_t"},
    }


def test_construct_validation_requires_anchor_and_mtmm_controls(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle.json"
    bundle.write_text("{}", encoding="utf-8")
    payload = _payload(bundle)
    assert validate_construct_validation_manifest(payload)["status"] == "CONSTRUCT_VALIDATION_PROTOCOL_READY"
    payload.pop("score_perturbation_plan")
    assert validate_construct_validation_manifest(payload)["status"] == "REFUSE_CONSTRUCT_VALIDATION_PLAN"


def test_construct_validation_refuses_same_membership_commitment(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle.json"
    bundle.write_text("{}", encoding="utf-8")
    payload = _payload(bundle)
    payload["anchor_cohort_membership_commitment"] = payload["score_cohort_membership_commitment"]
    result = validate_construct_validation_manifest(payload)
    assert result["status"] == "REFUSE_CONSTRUCT_VALIDATION_PLAN"
