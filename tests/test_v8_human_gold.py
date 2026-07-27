"""Unit tests for the V8 behavior-v2.1 human-gold gate."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "v8_human_gold_evaluator",
    ROOT / "scripts" / "evaluate_suica_v8_behavior_v21_human_gold.py",
)
assert SPEC is not None and SPEC.loader is not None
EVALUATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVALUATOR)


def test_human_gold_prediction_coarsens_atomic_evidence() -> None:
    groups = {
        "stance": [
            "assertion_commitment",
            "epistemic_qualification",
        ],
    }
    payload = {
        "opportunities": [{
            "opportunity_code": "stance_opportunity",
            "evidence_span_ids": ["x1"],
        }],
        "events": [{
            "event_code": "assertion_commitment",
            "evidence_span_ids": ["x1"],
        }],
    }
    prediction = EVALUATOR._prediction(payload, groups=groups)
    assert prediction["opportunity__stance_opportunity"] == 1
    assert prediction["event__assertion_commitment"] == 1
    assert prediction["coarse__stance"] == 1
    assert prediction["coarse_evidence__stance"] == {"x1"}


def test_adjudication_queue_includes_all_disagreements() -> None:
    first = pd.DataFrame([{
        "blind_item_id": "item-1",
        "coarse__stance": "1",
        "coarse_evidence__stance": "x1",
        "abstain": "0",
    }])
    second = pd.DataFrame([{
        "blind_item_id": "item-1",
        "coarse__stance": "0",
        "coarse_evidence__stance": "",
        "abstain": "1",
    }])
    hidden = pd.DataFrame([{
        "blind_item_id": "item-1",
        "spans_json": '[{"span_id":"x1","text":"text"}]',
    }])
    queue = EVALUATOR._adjudication_queue(
        first,
        second,
        hidden,
        labels=["coarse__stance"],
        evidence=["coarse_evidence__stance"],
        seed=7,
        review_fraction=0.0,
    )
    assert len(queue) == 1
    assert queue.loc[0, "review_reason"] == "coder_disagreement"
    assert queue.loc[0, "final__coarse__stance"] == ""
