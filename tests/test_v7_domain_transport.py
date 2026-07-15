from __future__ import annotations

import hashlib
from pathlib import Path

from suica_core.v7_domain_transport import validate_domain_transport_manifest


def _payload(bundle: Path) -> dict[str, object]:
    return {
        "mode": "LOCAL_REFERENCE_ONLY",
        "source_geometry_bundle": {"path": str(bundle), "sha256": hashlib.sha256(bundle.read_bytes()).hexdigest()},
        "target_schema": {
            "author_id": {"field": "author", "availability": "AVAILABLE"},
            "document_id": {"field": "document", "availability": "AVAILABLE"},
            "occasion_id": {"field": "occasion", "availability": "AVAILABLE"},
            "rind_id": {"field": "rind", "availability": "AVAILABLE"},
            "timestamp": {"field": "timestamp", "availability": "AVAILABLE"},
            "language": {"field": "language", "availability": "AVAILABLE"},
        },
        "target_reference_population": {"reference_id": "target", "sampling_frame": "declared", "n_authors": 20, "frozen_before_outcome_access": True},
        "target_runtime": {"representation_hash": "rep", "operator_registry_hash": "op", "embedding_runtime": "runtime", "tokenizer_or_segmenter": "tokenizer"},
        "target_local_reference_plan": {"build_target_reference": True, "reuse_source_numerical_norms": False},
        "measurement_stage_only": True,
        "market_prediction": False,
        "outcome_labels_accessed": False,
        "source_reference_reused": False,
    }


def test_local_reference_mode_forbids_numeric_cross_domain_comparison(tmp_path: Path) -> None:
    bundle = tmp_path / "geometry.json"
    bundle.write_text("{}", encoding="utf-8")
    result = validate_domain_transport_manifest(_payload(bundle))
    assert result["status"] == "DOMAIN_TRANSPORT_LOCAL_REFERENCE_READY"
    assert result["cross_domain_numeric_comparison_authorized"] is False


def test_measurement_prediction_conflation_refuses(tmp_path: Path) -> None:
    bundle = tmp_path / "geometry.json"
    bundle.write_text("{}", encoding="utf-8")
    payload = _payload(bundle)
    payload["market_prediction"] = True
    assert validate_domain_transport_manifest(payload)["status"] == "REFUSE_MEASUREMENT_TO_PREDICTION_CONFLATION"


def test_paired_alignment_requires_heldout_evidence_before_comparison(tmp_path: Path) -> None:
    bundle = tmp_path / "geometry.json"
    bundle.write_text("{}", encoding="utf-8")
    payload = _payload(bundle)
    payload["mode"] = "PAIRED_ALIGNMENT"
    payload["paired_alignment"] = {
        "bridge_type": "parallel_items",
        "map_class": "orthogonal_procrustes",
        "anchor_training_id": "train",
        "anchor_confirmation_id": "test",
        "alignment_frozen_before_outcome_access": True,
        "heldout_metrics": ["retrieval"],
        "predeclared_thresholds": {"retrieval": 0.7},
    }
    result = validate_domain_transport_manifest(payload)
    assert result["status"] == "PAIRED_ALIGNMENT_PROTOCOL_READY_NOT_YET_EVALUATED"
    assert result["cross_domain_numeric_comparison_authorized"] is False
