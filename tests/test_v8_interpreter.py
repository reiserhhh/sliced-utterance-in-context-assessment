"""Tests for the non-scoring V8 interpreter pipeline."""
from __future__ import annotations

import numpy as np
import pytest

from suica_core.v8_interpreter import (
    bootstrap_mean_interval,
    consensus_set,
    fleiss_kappa_multilabel,
    geometry_interpretation_alignment,
    interpretation_forbidden_count,
    mean_pairwise_set_f1,
    mean_pairwise_weighted_jaccard,
    mean_pairwise_jaccard,
    pairwise_nominal_kappa,
    run_structured_stage,
    set_jaccard,
    validate_behavior_payload,
    validate_interpretation_payload,
)
from suica_core.v8_semantic import (
    CallableSemanticProvider,
    SemanticTransducerSpec,
)


def test_set_stability_metrics_reward_identical_codes() -> None:
    runs = [{"a", "b"}, {"a", "b"}, {"a", "b"}]
    assert set_jaccard(runs[0], runs[1]) == 1.0
    assert mean_pairwise_jaccard(runs) == 1.0
    assert consensus_set(runs) == {"a", "b"}


def test_fleiss_kappa_multilabel_detects_repeat_agreement() -> None:
    profiles = {
        "p1": [{"a"}, {"a"}, {"a"}],
        "p2": [{"b"}, {"b"}, {"b"}],
    }
    assert fleiss_kappa_multilabel(profiles, universe={"a", "b"}) == 1.0


def test_geometry_interpretation_alignment_detects_neighbor_codes() -> None:
    geometry = np.array([
        [1.0, 0.0],
        [0.99, 0.01],
        [0.95, 0.05],
        [0.0, 1.0],
        [0.01, 0.99],
        [0.05, 0.95],
        [-1.0, 0.0],
        [-0.99, 0.01],
    ])
    sets = [
        {"a"},
        {"a"},
        {"a"},
        {"b"},
        {"b"},
        {"b"},
        {"c"},
        {"c"},
    ]
    result = geometry_interpretation_alignment(
        geometry,
        sets,
        neighbor_count=1,
        permutations=100,
        seed=4,
    )
    assert result["neighbor_similarity_auc"] > 0.75
    assert result["distance_spearman"] > 0.3


def test_behavior_validation_requires_deterministic_profile_local_event_id() -> None:
    schema = {
        "type": "object",
        "required": ["profiles"],
        "properties": {"profiles": {"type": "array"}},
    }
    payload = {
        "profiles": [{
            "profile_id": "P1",
            "events": [{
                "event_id": "S1::self_reference",
                "segment_id": "S1",
                "event_code": "self_reference",
                "evidence_span_ids": ["X1"],
            }],
            "abstain": False,
        }],
    }
    assert validate_behavior_payload(
        payload,
        schema=schema,
        expected_profiles={"P1"},
        spans_by_segment={"S1": {"X1"}},
        segments_by_profile={"P1": {"S1"}},
    ) == payload
    payload["profiles"][0]["events"][0]["event_id"] = "free-form-id"
    normalized, audit = validate_behavior_payload(
        payload,
        schema=schema,
        expected_profiles={"P1"},
        spans_by_segment={"S1": {"X1"}},
        segments_by_profile={"P1": {"S1"}},
        return_audit=True,
    )
    assert normalized["profiles"][0]["events"][0]["event_id"] == (
        "S1::self_reference"
    )
    assert audit["canonicalized_event_ids"] == 1


def test_behavior_bookkeeping_merges_duplicates_and_drops_abstain_marker() -> None:
    schema = {
        "type": "object",
        "required": ["profiles"],
        "properties": {"profiles": {"type": "array"}},
    }
    payload = {
        "profiles": [{
            "profile_id": "P1",
            "events": [
                {
                    "event_id": "first",
                    "segment_id": "S1",
                    "event_code": "self_reference",
                    "evidence_span_ids": ["X1"],
                },
                {
                    "event_id": "second",
                    "segment_id": "S1",
                    "event_code": "self_reference",
                    "evidence_span_ids": ["X2"],
                },
                {
                    "event_id": "abstain",
                    "segment_id": "S1",
                    "event_code": "abstain",
                    "evidence_span_ids": [],
                },
            ],
            "abstain": True,
        }],
    }
    normalized, audit = validate_behavior_payload(
        payload,
        schema=schema,
        expected_profiles={"P1"},
        spans_by_segment={"S1": {"X1", "X2"}},
        segments_by_profile={"P1": {"S1"}},
        return_audit=True,
    )
    events = normalized["profiles"][0]["events"]
    assert len(events) == 1
    assert events[0]["evidence_span_ids"] == ["X1", "X2"]
    assert normalized["profiles"][0]["abstain"] is False
    assert audit["merged_duplicate_events"] == 1
    assert audit["dropped_abstain_markers"] == 1


def test_interpreter_agreement_helpers() -> None:
    runs = [{"a", "b"}, {"a", "b"}, {"a"}]
    weights = {"a": 1.0, "b": 2.0}
    assert 0.5 < mean_pairwise_weighted_jaccard(runs, weights=weights) < 1.0
    assert 0.7 < mean_pairwise_set_f1(runs) < 1.0
    assert pairwise_nominal_kappa([
        {"p1": "pass", "p2": "reject"},
        {"p1": "pass", "p2": "reject"},
    ]) == 1.0
    mean, lower, upper = bootstrap_mean_interval([0.7, 0.8, 0.9], draws=200, seed=4)
    assert lower <= mean <= upper


def test_forbidden_interpretation_language_is_counted() -> None:
    payload = {
        "profiles": [{
            "interpretation_atoms": [{
                "human_readable_sentence": "This proves a Big Five personality trait.",
            }],
        }],
    }
    assert interpretation_forbidden_count(payload) >= 1


def test_interpretation_requires_registered_event_link() -> None:
    schema = {
        "type": "object",
        "required": ["profiles"],
        "properties": {"profiles": {"type": "array"}},
    }
    payload = {
        "profiles": [{
            "profile_id": "P1",
            "assessment_status": "interpreted",
            "interpretation_atoms": [{
                "atom_id": "A1",
                "target_dimension_ids": ["D001"],
                "scope": "author_relative",
                "relation": "elevated",
                "direction": "positive",
                "evidence_event_ids": ["S1::self_reference"],
                "counterevidence_event_ids": [],
            }],
            "refusal_codes": [],
        }],
    }
    kwargs = {
        "schema": schema,
        "expected_profiles": {"P1"},
        "event_ids_by_profile": {"P1": {"S1::self_reference"}},
        "event_codes_by_profile": {
            "P1": {"S1::self_reference": "self_reference"},
        },
        "registered_links_by_profile": {
            "P1": {("D001", "self_reference")},
        },
        "candidate_atoms_by_profile": {
            "P1": {
                "A1": {
                    "target_dimension_ids": ["D001"],
                    "scope": "author_relative",
                    "relation": "elevated",
                    "direction": "positive",
                    "evidence_event_ids": ["S1::self_reference"],
                },
            },
        },
    }
    assert validate_interpretation_payload(payload, **kwargs) == payload
    kwargs["registered_links_by_profile"] = {
        "P1": {("D001", "affect_expression")},
    }
    with pytest.raises(ValueError, match="registered dimension-event"):
        validate_interpretation_payload(payload, **kwargs)


def test_structured_stage_retries_validation_failure() -> None:
    calls = {"count": 0}

    def callback(_spec: SemanticTransducerSpec, _payload: str) -> str:
        calls["count"] += 1
        return "{" if calls["count"] == 1 else '{"ready": true}'

    spec = SemanticTransducerSpec(
        provider="fixture",
        model="fixture",
        model_revision="fixture",
        prompt_id="fixture",
        prompt_text="json",
        schema_id="fixture",
        schema={"type": "object"},
        max_validation_retries=2,
    )
    result = run_structured_stage(
        CallableSemanticProvider(callback),
        spec,
        {"input": 1},
        run_id="retry-test",
        validator=lambda payload: payload,
    )
    assert result["status"] == "STRUCTURED_STAGE_READY"
    assert result["ledger"]["validation_attempts"] == 2
    assert [row["status"] for row in result["ledger"]["attempt_history"]] == [
        "INVALID",
        "VALID",
    ]
