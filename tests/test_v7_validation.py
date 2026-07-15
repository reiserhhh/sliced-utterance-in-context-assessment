from __future__ import annotations

import hashlib
from tempfile import TemporaryDirectory

import pandas as pd

from suica_core.v7_validation import (
    validate_external_anchor_manifest,
    validate_fixed_free_observations,
)


def test_fixed_free_validator_refuses_unobserved_free_opportunity() -> None:
    frame = pd.DataFrame([
        {"participant_id": "p1", "phase": "free", "session_id": "s1", "condition_id": "c1"},
        {"participant_id": "p1", "phase": "fixed", "session_id": "s1", "condition_id": "c1", "assignment_randomized": True},
    ])
    summary, q_table, b_table = validate_fixed_free_observations(frame)
    assert summary["q_status"] == "REFUSE_Q_OPPORTUNITY_UNOBSERVED"
    assert summary["b_status"] == "REFUSE_B_INSUFFICIENT_INDEPENDENT_REPLICATION"
    assert q_table.empty
    assert not b_table.empty


def test_fixed_free_validator_accepts_logged_q_and_repeated_randomized_fixed_design() -> None:
    rows = []
    for participant in ("p1", "p2"):
        for condition in ("c1", "c2"):
            for opportunity in range(3):
                rows.append({
                    "participant_id": participant, "phase": "free", "session_id": f"free-{opportunity}",
                    "condition_id": condition, "opportunity_id": f"{participant}-{condition}-{opportunity}",
                    "exposure_recorded": True, "selected": opportunity % 2 == 0,
                })
            for session in ("fixed-1", "fixed-2"):
                rows.append({
                    "participant_id": participant, "phase": "fixed", "session_id": session,
                    "condition_id": condition, "assignment_randomized": True,
                })
    summary, q_table, b_table = validate_fixed_free_observations(pd.DataFrame(rows))
    assert summary["status"] == "FIXED_FREE_DESIGN_READY_FOR_FUTURE_ESTIMATION"
    assert not q_table.empty
    assert b_table["b_eligible"].all()


def test_external_anchor_validator_requires_hash_freeze_and_independent_cohort() -> None:
    with TemporaryDirectory() as directory:
        bundle = __import__("pathlib").Path(directory) / "bundle.json"
        bundle.write_text("{}", encoding="utf-8")
        digest = hashlib.sha256(bundle.read_bytes()).hexdigest()
        payload = {
            "bundle_path": str(bundle), "bundle_sha256": digest,
            "pre_freeze_label_access": False,
            "score_cohort_id": "development", "anchor_cohort_id": "anchor",
            "cohort_overlap_count": 0,
            "multiplicity_plan": {"method": "max_t"},
            "hypotheses": [{"id": "H1", "score": "SU7-FC-0001@v7"}],
        }
        assert validate_external_anchor_manifest(payload)["status"] == "EXTERNAL_ANCHOR_PROTOCOL_READY"
        payload["cohort_overlap_count"] = 1
        assert validate_external_anchor_manifest(payload)["status"] == "REFUSE_ANCHOR_COHORT_OVERLAP"
