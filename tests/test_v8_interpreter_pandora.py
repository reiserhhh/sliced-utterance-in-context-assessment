"""Synthetic tests for the PANDORA interpreter gate math."""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import run_suica_v8_interpreter_pandora as pandora  # noqa: E402
import run_suica_v8_interpreter_stability as planted  # noqa: E402
from suica_core.v8_semantic import (  # noqa: E402
    CallableSemanticProvider,
    SemanticTransducerSpec,
)


def test_empty_interpretations_are_not_similarity_evidence() -> None:
    assert pandora._information_jaccard(set(), set()) == 0.0
    assert pandora._information_jaccard({"a"}, {"a"}) == 1.0


def test_uncertainty_distance_is_symmetric() -> None:
    means = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 2.0]])
    uncertainty = np.full_like(means, 0.05)
    distance = pandora._pairwise_uncertainty_distance(
        means,
        uncertainty,
        means,
    )
    assert np.allclose(distance, distance.T)
    assert np.allclose(np.diag(distance), 0.0)
    assert np.all(distance[np.triu_indices(3, 1)] > 0)


def test_negative_registered_link_compiles_reduced_candidate() -> None:
    profile = {
        "segments": [{"segment_id": "S1"}, {"segment_id": "S2"}],
        "suica_packet": {
            "dimensions": [{
                "dimension_id": "D001",
                "reference_band": "lower_reference_band",
                "support_status": "supported",
            }],
        },
        "registered_links": [{
            "dimension_id": "D001",
            "event_code": "self_reference",
            "association_direction": "negative",
            "event_rate_threshold": 0.50,
        }],
    }
    events = [{
        "event_id": "S1::self_reference",
        "segment_id": "S1",
        "event_code": "self_reference",
        "evidence_span_ids": ["X1"],
    }]
    candidate = planted._candidate_atoms(profile, events)
    assert len(candidate) == 1
    assert candidate[0]["relation"] == "reduced"
    assert candidate[0]["direction"] == "negative"


def test_candidate_diagnostics_exposes_deterministic_passthrough() -> None:
    profile = {
        "profile_id": "P1",
        "cohort_split": "confirmation",
        "segments": [{"segment_id": "S1"}, {"segment_id": "S2"}],
        "suica_packet": {
            "dimensions": [{
                "dimension_id": "D001",
                "reference_band": "upper_reference_band",
                "support_status": "supported",
            }],
        },
        "registered_links": [{
            "dimension_id": "D001",
            "event_code": "self_reference",
            "association_direction": "positive",
            "event_rate_threshold": 0.50,
        }],
    }
    events = {
        "P1": [{
            "event_id": "S1::self_reference",
            "segment_id": "S1",
            "event_code": "self_reference",
            "evidence_span_ids": ["X1"],
        }],
    }
    interpretation = {
        "profile_id": "P1",
        "assessment_status": "interpreted",
        "interpretation_atoms": [{
            "atom_id": "C::D001::self_reference",
            "target_dimension_ids": ["D001"],
            "scope": "author_relative",
            "relation": "elevated",
            "direction": "positive",
            "qualifier": "supported",
            "evidence_event_ids": ["S1::self_reference"],
        }],
    }
    run = {
        "interpretation": {"P1": interpretation},
        "critique": {
            "P1": {
                "atom_verdicts": [{
                    "atom_id": "C::D001::self_reference",
                    "verdict": "pass",
                }],
            },
        },
    }
    metrics, frame = pandora._candidate_diagnostics(
        [profile],
        events,
        [run],
    )
    assert len(frame) == 1
    assert metrics["candidate_eligible_profile_rate"] == 1.0
    assert metrics["candidate_retention_rate"] == 1.0
    assert metrics["exact_candidate_set_rate"] == 1.0
    assert metrics["critic_pass_rate"] == 1.0


def test_nuisance_match_prefers_condition_overlap_before_length() -> None:
    source = {
        "author_id": "source",
        "nuisance_signature": {
            "condition_hashes": ["A", "B"],
            "mean_segment_tokens": 80.0,
        },
    }
    condition_match = {
        "author_id": "condition",
        "nuisance_signature": {
            "condition_hashes": ["A"],
            "mean_segment_tokens": 40.0,
        },
    }
    length_match = {
        "author_id": "length",
        "nuisance_signature": {
            "condition_hashes": ["C"],
            "mean_segment_tokens": 80.0,
        },
    }
    selected, overlap, token_delta = pandora._nuisance_match(
        source,
        [length_match, condition_match],
    )
    assert selected["author_id"] == "condition"
    assert overlap == 0.5
    assert token_delta == 0.5


def test_cached_stage_invalidates_when_payload_changes(tmp_path: Path) -> None:
    calls = {"count": 0}

    def callback(_spec: SemanticTransducerSpec, payload: str) -> str:
        import json

        calls["count"] += 1
        value = json.loads(payload)["value"]
        return json.dumps({"value": value})

    spec = SemanticTransducerSpec(
        provider="fixture",
        model="fixture",
        model_revision="fixture",
        prompt_id="fixture",
        prompt_text="json",
        schema_id="fixture",
        schema={"type": "object"},
    )
    cache_path = tmp_path / "stage.json"
    first = planted._cached_stage(
        cache_path=cache_path,
        provider=CallableSemanticProvider(callback),
        spec=spec,
        payload={"value": 1},
        run_id="cache-identity",
        validator=lambda value: value,
    )
    second = planted._cached_stage(
        cache_path=cache_path,
        provider=CallableSemanticProvider(callback),
        spec=spec,
        payload={"value": 2},
        run_id="cache-identity",
        validator=lambda value: value,
    )
    assert first["output"]["value"] == 1
    assert second["output"]["value"] == 2
    assert calls["count"] == 2


def test_candidate_compiler_caps_dense_profiles_at_schema_limit() -> None:
    dimensions = []
    links = []
    events = []
    segments = [{"segment_id": "S1"}, {"segment_id": "S2"}]
    for index in range(10):
        dimension_id = f"D{index + 1:03d}"
        event_code = planted.EVENT_ORDER[index % len(planted.EVENT_ORDER)]
        dimensions.append({
            "dimension_id": dimension_id,
            "reference_band": "upper_reference_band",
            "uncertainty_band": "clear",
            "support_status": "supported",
        })
        links.append({
            "dimension_id": dimension_id,
            "event_code": event_code,
            "association_direction": "positive",
            "event_rate_threshold": 0.50,
            "discovery_spearman_r": 0.2 + index / 100,
        })
        events.append({
            "event_id": f"S1::{event_code}",
            "segment_id": "S1",
            "event_code": event_code,
            "evidence_span_ids": ["X1"],
        })
    profile = {
        "segments": segments,
        "suica_packet": {"dimensions": dimensions},
        "registered_links": links,
    }
    candidates = planted._candidate_atoms(profile, events)
    assert len(candidates) == 8


def test_target_deletion_keeps_other_atoms_sharing_event_out_of_nontarget() -> None:
    def atom(dimension: str, event_code: str) -> dict:
        return {
            "atom_id": f"C::{dimension}::{event_code}",
            "target_dimension_ids": [dimension],
            "scope": "author_relative",
            "relation": "elevated",
            "direction": "positive",
            "qualifier": "supported",
            "evidence_event_ids": [f"S1::{event_code}"],
            "counterevidence_event_ids": [],
        }

    shared_first = atom("D001", "self_reference")
    shared_second = atom("D002", "self_reference")
    unaffected = atom("D003", "affect_expression")

    def interpretation(atoms: list[dict]) -> dict:
        return {
            "assessment_status": "interpreted",
            "interpretation_atoms": atoms,
        }

    def run(atoms: list[dict]) -> dict:
        return {
            "interpretation": {"P1": interpretation(atoms)},
            "critique": {"P1": {"atom_verdicts": []}},
        }

    metrics, frame = pandora._variant_metrics(
        [{
            "profile_id": "P1",
            "cohort_split": "confirmation",
            "target_dimension_id": "D001",
            "target_event_code": "self_reference",
        }],
        run([shared_first, shared_second, unaffected]),
        run([shared_first, shared_second, unaffected]),
        run([unaffected]),
        run([shared_first, shared_second]),
        config={
            "seed": 1,
            "real_text": {"bootstrap_draws": 100},
        },
    )
    assert len(frame) == 1
    assert metrics["key_evidence_nontarget_retention"] == 1.0
