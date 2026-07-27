"""Tests for restricted vector queries and evidence fidelity."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from suica_core.v8_evidence import (
    evidence_node,
    evaluate_evidence_fidelity,
    matched_neighbor,
    nearest_neighbors,
    simulate_evidence_world,
    validate_evidence_graph,
    write_evidence_artifact,
)


def test_restricted_neighbor_queries() -> None:
    reference = np.eye(4)
    nearest = nearest_neighbors(reference[0], reference, count=2, exclude_index=0)
    assert len(nearest) == 2
    assert all(row["reference_index"] != 0 for row in nearest)
    matched = matched_neighbor(np.array([0.1, 0.2]), np.array([[0.1, 0.2], [2.0, 2.0]]))
    assert matched["reference_index"] == 0


def test_planted_evidence_is_recovered_and_faithful() -> None:
    world = simulate_evidence_world(seed=8, authors=120)
    summary, _rows = evaluate_evidence_fidelity(world, seed=9, bootstrap_draws=300)
    assert summary["evidence_precision_ci_lower"] > 0.75
    assert summary["evidence_recall_ci_lower"] > 0.75
    assert summary["necessity_advantage_ci_lower"] > 0
    assert summary["sufficiency_ratio_ci_lower"] > 0.70
    assert summary["paraphrase_change_sem_q95"] < 0.25
    assert summary["mechanism_flip_detection_rate"] > 0.80


def test_evidence_graph_detects_tampering(tmp_path: Path) -> None:
    artifact = tmp_path / "evidence.json"
    digest = write_evidence_artifact(
        artifact,
        source_span_ids=["s1"],
        measurements={"technical_score": 0.4},
    )
    node = evidence_node(
        node_id="E1",
        kind="supporting",
        artifact_path="evidence.json",
        artifact_hash=digest,
        source_span_ids=["s1"],
        measurement_field="technical_score",
        observed_value=0.4,
    )
    assert validate_evidence_graph({"E1": node}, repository_root=tmp_path) == []
    node["observed_value"] = 0.8
    errors = validate_evidence_graph({"E1": node}, repository_root=tmp_path)
    assert any("node_hash_mismatch" in error for error in errors)
    assert any("measurement_mismatch" in error for error in errors)
