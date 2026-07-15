from __future__ import annotations

import json
from pathlib import Path

from suica_core.v7_closure import audit_v7_theory_closure


def test_closure_refuses_missing_registered_evidence(tmp_path: Path) -> None:
    config = {
        "required_files": ["missing.md"],
        "evidence": [
            {
                "id": "missing",
                "decision": "decision.json",
                "allowed_statuses": ["PASS"],
            }
        ],
    }
    result = audit_v7_theory_closure(config, repository_root=tmp_path)
    assert result["status"] == "REFUSE_V7_THEORY_CLOSURE_AUDIT_FAILURE"
    assert result["n_failures"] == 2


def test_closure_accepts_decision_but_keeps_empirical_gates(tmp_path: Path) -> None:
    (tmp_path / "required.md").write_text("ok", encoding="utf-8")
    (tmp_path / "decision.json").write_text(json.dumps({"status": "PASS"}), encoding="utf-8")
    result = audit_v7_theory_closure(
        {
            "required_files": ["required.md"],
            "evidence": [{"id": "one", "decision": "decision.json", "allowed_statuses": ["PASS"]}],
        },
        repository_root=tmp_path,
    )
    assert result["n_failures"] == 0
    assert result["evidence_lattice"]["repeated_measurement_reliability"] == "FUTURE_DATA_REQUIRED"
