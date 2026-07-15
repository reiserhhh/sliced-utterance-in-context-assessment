from __future__ import annotations

import numpy as np

from suica_sim.v7_representation_transport import evaluate_transport_world, generate_transport_world, run_transport_matrix


def test_rotation_preserves_within_geometry_but_needs_paired_alignment() -> None:
    world = generate_transport_world("unknown_rotation", seed=10, persons=140, features=8, noise_scale=0.03, anchor_fraction=0.5)
    result = evaluate_transport_world(world)
    assert float(result["paired_relative_distance_spearman"]) > 0.95
    assert float(result["procrustes_retrieval_accuracy"]) > float(result["naive_retrieval_accuracy"])
    assert float(result["procrustes_coordinate_r2"]) > 0.8


def test_unpaired_isotropic_world_refuses_coordinate_transport() -> None:
    world = generate_transport_world("unpaired_isotropic_orientation_ambiguity", seed=11, persons=120, features=8, noise_scale=0.04, anchor_fraction=0.5)
    result = evaluate_transport_world(world)
    assert result["paired_available"] is False
    assert result["cross_domain_coordinate_status"] == "REFUSE_UNPAIRED_ORIENTATION_NOT_IDENTIFIED"
    assert np.isnan(float(result["naive_coordinate_r2"]))


def test_transport_matrix_runs_all_declared_worlds() -> None:
    rows = run_transport_matrix({
        "seed": 1,
        "repetitions": 2,
        "persons": 60,
        "features": 5,
        "noise_scale": 0.05,
        "anchor_fraction": 0.5,
        "worlds": ["common_coordinate", "unknown_rotation"],
    })
    assert len(rows) == 4
