from __future__ import annotations

import pandas as pd

from suica_core.v7_measurement_preflight import validate_repeated_measurement_design


def _balanced_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for participant in ("p1", "p2", "p3"):
        for condition in ("c1", "c2"):
            for occasion in ("o1", "o2"):
                rows.append({
                    "participant_id": participant,
                    "condition_id": condition,
                    "occasion_id": occasion,
                    "session_id": occasion,
                    "assignment_randomized": True,
                    "scorer_hash": "scorer-v1",
                    "operator_registry_version": "operators-v1",
                    "window_operator_id": "native",
                    "representation_hash": "repr-v1",
                    "component_id": "SU7-FC-0001@v1",
                    "score_value": float(len(participant) + len(condition) + len(occasion)),
                })
    return rows


def test_repeated_measurement_preflight_accepts_complete_frozen_crossing() -> None:
    summary, coverage, plan = validate_repeated_measurement_design(pd.DataFrame(_balanced_rows()))
    assert summary["status"] == "REPEATED_MEASUREMENT_DESIGN_READY_FOR_GSTUDY_LST"
    assert coverage.loc[0, "coverage"] == 1.0
    assert "PC" in plan["g_study_model"]


def test_repeated_measurement_preflight_refuses_runtime_drift() -> None:
    data = pd.DataFrame(_balanced_rows())
    data.loc[0, "scorer_hash"] = "scorer-v2"
    summary, _, _ = validate_repeated_measurement_design(data)
    assert summary["status"] == "REFUSE_GSTUDY_UNFROZEN_SCORING_RUNTIME"


def test_repeated_measurement_preflight_refuses_missing_occasion_replication() -> None:
    data = pd.DataFrame(_balanced_rows()).query("occasion_id == 'o1'").copy()
    summary, coverage, _ = validate_repeated_measurement_design(data)
    assert summary["status"] == "REFUSE_GSTUDY_INSUFFICIENT_CROSSED_REPLICATION"
    assert int(coverage.loc[0, "min_occasions_per_person_condition"]) == 1
