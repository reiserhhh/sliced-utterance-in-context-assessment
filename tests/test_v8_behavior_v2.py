"""Tests for the high-resolution SUICA V8 behavior observer."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from suica_core.v8_behavior_v2 import (
    consensus_frame,
    event_macro_f1,
    fit_leave_one_author_out_baseline,
    fit_opportunity_event_baseline,
    normalize_behavior_v2_payload,
    observation_frame,
    pairwise_event_f1,
    profile_rate_features,
    validate_behavior_v2_payload,
)
from suica_core.v8_human_coding import (
    binary_metrics,
    gwet_ac1_binary,
    span_set_f1,
)


ROOT = Path(__file__).resolve().parents[1]


def _profiles() -> list[dict]:
    return [{
        "profile_id": "P1",
        "author_id": "A1",
        "side": "left",
        "cohort_split": "discovery",
        "segments": [{
            "segment_id": "S1",
            "segment_index": 0,
            "condition": "C1",
            "token_count": 12,
            "spans": [
                {"span_id": "X1", "text": "I thought it was red."},
                {"span_id": "X2", "text": "More precisely, it was orange."},
            ],
        }],
    }]


def _payload() -> dict:
    return {
        "profiles": [{
            "profile_id": "P1",
            "segments": [{
                "segment_id": "S1",
                "opportunities": [
                    {
                        "opportunity_code": "self_report_opportunity",
                        "evidence_span_ids": ["X1"],
                    },
                    {
                        "opportunity_code": "self_repair_opportunity",
                        "evidence_span_ids": ["X2"],
                    },
                ],
                "events": [
                    {
                        "event_id": "S1::self_state_report",
                        "event_code": "self_state_report",
                        "evidence_span_ids": ["X1"],
                        "antecedent_span_ids": [],
                        "relation_type": "none",
                    },
                    {
                        "event_id": "S1::self_repair",
                        "event_code": "self_repair",
                        "evidence_span_ids": ["X2"],
                        "antecedent_span_ids": ["X1"],
                        "relation_type": "self_revision",
                    },
                ],
                "abstain": False,
            }],
        }],
    }


def test_behavior_v2_validates_exact_repair_provenance() -> None:
    schema = json.loads(
        (ROOT / "schemas" / "v8_behavior_observation_v2.schema.json").read_text()
    )
    assert validate_behavior_v2_payload(
        _payload(),
        schema=schema,
        profiles=_profiles(),
    )["profiles"][0]["profile_id"] == "P1"


def test_behavior_v2_rejects_event_without_opportunity() -> None:
    schema = json.loads(
        (ROOT / "schemas" / "v8_behavior_observation_v2.schema.json").read_text()
    )
    payload = _payload()
    payload["profiles"][0]["segments"][0]["opportunities"] = []
    with pytest.raises(ValueError, match="required opportunity"):
        validate_behavior_v2_payload(
            payload,
            schema=schema,
            profiles=_profiles(),
        )


def test_behavior_v2_consensus_and_rate_residuals() -> None:
    outputs = [_payload(), _payload()]
    repeated = observation_frame(_profiles(), outputs)
    assert pairwise_event_f1(repeated) == 1.0
    consensus = consensus_frame(repeated)
    baseline = fit_opportunity_event_baseline(consensus)
    features = profile_rate_features(consensus, baseline, resolution=1)
    assert features.loc[0, "opportunities::self_state_report"] == 1
    assert np.isfinite(features.loc[0, "residual::self_state_report"])


def test_behavior_v2_consensus_requires_registered_fraction() -> None:
    second = _payload()
    second["profiles"][0]["segments"][0]["events"] = []
    second["profiles"][0]["segments"][0]["abstain"] = True
    repeated = observation_frame(_profiles(), [_payload(), second])
    strict = consensus_frame(repeated, required_fraction=1.0)
    majority = consensus_frame(repeated, required_fraction=0.5)
    assert strict.loc[0, "event::self_state_report"] == 0
    assert majority.loc[0, "event::self_state_report"] == 1


def test_event_macro_f1_does_not_reward_jointly_absent_events() -> None:
    first = observation_frame(_profiles(), [_payload()])
    second_payload = _payload()
    second_payload["profiles"][0]["segments"][0]["events"] = []
    second_payload["profiles"][0]["segments"][0]["abstain"] = True
    second = observation_frame(_profiles(), [second_payload])
    assert event_macro_f1(first, second) == 0.0


def test_behavior_v2_normalizer_merges_duplicates_and_drops_bad_repair() -> None:
    payload = _payload()
    segment = payload["profiles"][0]["segments"][0]
    segment["events"].append({
        "event_id": "duplicate",
        "event_code": "self_state_report",
        "evidence_span_ids": ["X2"],
        "antecedent_span_ids": [],
        "relation_type": "none",
    })
    segment["events"].append({
        "event_id": "bad-repair",
        "event_code": "self_repair",
        "evidence_span_ids": ["X1"],
        "antecedent_span_ids": ["X2"],
        "relation_type": "self_revision",
    })
    normalized, counts = normalize_behavior_v2_payload(
        payload,
        profiles=_profiles(),
    )
    events = normalized["profiles"][0]["segments"][0]["events"]
    state = [row for row in events if row["event_code"] == "self_state_report"]
    repair = [row for row in events if row["event_code"] == "self_repair"]
    assert len(state) == 1
    assert state[0]["evidence_span_ids"] == ["X1", "X2"]
    assert len(repair) == 1
    assert counts["merged_duplicate_events"] == 1
    assert counts["dropped_invalid_self_repairs"] == 1


def test_behavior_v2_normalizer_closes_event_opportunity_implication() -> None:
    payload = _payload()
    segment = payload["profiles"][0]["segments"][0]
    segment["opportunities"] = [{
        "opportunity_code": "self_state_report",
        "evidence_span_ids": ["X1"],
    }]
    normalized, counts = normalize_behavior_v2_payload(
        payload,
        profiles=_profiles(),
    )
    opportunities = {
        row["opportunity_code"]
        for row in normalized["profiles"][0]["segments"][0]["opportunities"]
    }
    assert opportunities == {
        "self_report_opportunity",
        "self_repair_opportunity",
    }
    assert counts["dropped_invalid_opportunities"] == 1
    assert counts["added_implied_opportunities"] == 2


def test_leave_one_author_out_baseline_excludes_target_outcome() -> None:
    rows = []
    for author_id, outcome in (("A", 1), ("B", 0)):
        row = {
            "author_id": author_id,
            "condition": "C",
        }
        for code in (
            "stance_opportunity",
            "affect_opportunity",
            "self_report_opportunity",
            "action_guidance_opportunity",
            "generativity_opportunity",
            "self_repair_opportunity",
        ):
            row[f"opportunity::{code}"] = 0
        for code in (
            "assertion_commitment",
            "epistemic_qualification",
            "explicit_acceptance",
            "explicit_rejection",
            "positive_affect_expression",
            "negative_affect_expression",
            "self_state_report",
            "self_action_report",
            "request_action",
            "recommend_action",
            "alternative_generation",
            "causal_explanation",
            "evidence_example",
            "self_repair",
        ):
            row[f"event::{code}"] = 0
        row["opportunity::stance_opportunity"] = 1
        row["event::assertion_commitment"] = outcome
        rows.append(row)
    baseline = fit_leave_one_author_out_baseline(
        pd.DataFrame(rows),
        target_authors=["A", "B"],
        shrinkage=0.0,
    )
    assert baseline.probability("assertion_commitment", "C", "A") == 0.0
    assert baseline.probability("assertion_commitment", "C", "B") == 1.0


def test_human_coding_metrics_are_bounded_and_exact() -> None:
    assert gwet_ac1_binary([1, 0, 1, 0], [1, 0, 1, 0]) == 1.0
    metrics = binary_metrics([1, 1, 0, 0], [1, 0, 1, 0])
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5
    assert metrics["f1"] == 0.5
    assert span_set_f1(["A", "B"], ["B", "C"]) == 0.5
