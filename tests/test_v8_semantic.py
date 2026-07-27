"""Tests for the frozen V8 semantic transducer."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from suica_core.v8_semantic import (
    CallableSemanticProvider,
    load_semantic_spec,
    semantic_event_vector,
    transduce_segments,
)


ROOT = Path(__file__).resolve().parents[1]


def _spec():
    return load_semantic_spec(
        prompt_path=ROOT / "prompts" / "v8_semantic_observer_v1.txt",
        schema_path=ROOT / "schemas" / "v8_semantic_observation.schema.json",
        provider="fixture",
        model="fixture-v1",
        model_revision="fixture-revision",
        prompt_id="v8-semantic-observer-v1",
    )


def _segments():
    return [{
        "segment_id": "seg-1",
        "spans": [{"span_id": "span-1", "text": "I propose that we try a new route."}],
    }]


def test_valid_semantic_transduction_and_vector() -> None:
    payload = {
        "observations": [{
            "observation_id": "obs-1",
            "segment_id": "seg-1",
            "event_type": "novelty_expression",
            "source_span_ids": ["span-1"],
            "polarity": 0.3,
            "intensity": 0.8,
            "confidence": 0.9,
            "abstain": False,
        }],
    }
    provider = CallableSemanticProvider(lambda _spec, _payload: json.dumps(payload))
    result = transduce_segments(provider, _spec(), _segments(), run_id="test-valid")
    assert result["status"] == "SEMANTIC_OBSERVATIONS_READY"
    vector = semantic_event_vector(result["observations"], segment_id="seg-1")
    assert vector.ndim == 1
    assert np.isfinite(vector).all()
    assert vector.sum() > 0


def test_person_level_or_unknown_output_is_refused() -> None:
    payload = {
        "observations": [{
            "observation_id": "obs-1",
            "segment_id": "seg-1",
            "event_type": "novelty_expression",
            "source_span_ids": ["span-unknown"],
            "polarity": 0.3,
            "intensity": 0.8,
            "confidence": 0.9,
            "abstain": False,
            "personality": "creative",
        }],
    }
    provider = CallableSemanticProvider(lambda _spec, _payload: json.dumps(payload))
    result = transduce_segments(provider, _spec(), _segments(), run_id="test-refuse")
    assert result["status"] == "REFUSE_SEMANTIC_TRANSDUCTION"
    assert result["observations"] == []


def test_abstention_invariants_are_enforced() -> None:
    payload = {
        "observations": [{
            "observation_id": "obs-1",
            "segment_id": "seg-1",
            "event_type": "abstain",
            "source_span_ids": ["span-1"],
            "polarity": 0.4,
            "intensity": 0.0,
            "confidence": 0.8,
            "abstain": True,
        }],
    }
    provider = CallableSemanticProvider(lambda _spec, _payload: json.dumps(payload))
    result = transduce_segments(provider, _spec(), _segments(), run_id="test-abstain")
    assert result["status"] == "REFUSE_SEMANTIC_TRANSDUCTION"


def test_nonstandard_json_constants_are_refused() -> None:
    provider = CallableSemanticProvider(
        lambda _spec, _payload: (
            '{"observations":[{"observation_id":"o","segment_id":"seg-1",'
            '"event_type":"self_reference","source_span_ids":["span-1"],'
            '"polarity":NaN,"intensity":0.2,"confidence":0.8,"abstain":false}]}'
        )
    )
    result = transduce_segments(provider, _spec(), _segments(), run_id="test-nan")
    assert result["status"] == "REFUSE_SEMANTIC_TRANSDUCTION"

