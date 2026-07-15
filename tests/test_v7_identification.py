from __future__ import annotations

from suica_sim.v7_identification import evaluate_world, generate_world, run_identification_matrix


def test_axis_rotation_world_is_observationally_equivalent() -> None:
    world = generate_world("axis_rotation_equivalence", seed=7, persons=40, features=8, shared_rank=3, context_rank=2, noise_scale=0.2)
    assert world.rotation_error is not None
    assert world.rotation_error < 1e-10


def test_null_world_has_near_chance_alignment() -> None:
    world = generate_world("null", seed=8, persons=160, features=12, shared_rank=3, context_rank=2, noise_scale=0.2)
    result = evaluate_world(world, seed=8, shared_rank=3)
    assert 0.4 <= float(result["alignment_auc"]) <= 0.6


def test_omitted_context_can_survive_observed_context_residualization() -> None:
    world = generate_world("omitted_context_counterexample", seed=9, persons=120, features=10, shared_rank=3, context_rank=2, noise_scale=0.15)
    result = evaluate_world(world, seed=9, shared_rank=3)
    assert float(result["residual_alignment_auc"]) > 0.65


def test_context_adjustment_recovers_shared_subspace_when_context_is_observed() -> None:
    world = generate_world("shared_linear", seed=11, persons=120, features=12, shared_rank=3, context_rank=2, noise_scale=0.18)
    result = evaluate_world(world, seed=11, shared_rank=3)
    assert float(result["context_adjusted_subspace_congruence"]) > 0.75
    assert float(result["context_adjusted_subspace_congruence"]) > float(result["raw_subspace_congruence"])


def test_endogenous_context_can_make_residualization_overadjust() -> None:
    world = generate_world("endogenous_context_overadjustment_counterexample", seed=17, persons=180, features=12, shared_rank=3, context_rank=2, noise_scale=0.18)
    result = evaluate_world(world, seed=17, shared_rank=3)
    assert float(result["context_adjusted_subspace_congruence"]) < float(result["raw_subspace_congruence"])


def test_measurement_error_in_context_can_leave_residual_alignment() -> None:
    world = generate_world("measurement_error_context_counterexample", seed=18, persons=160, features=12, shared_rank=3, context_rank=2, noise_scale=0.18)
    result = evaluate_world(world, seed=18, shared_rank=3)
    assert float(result["residual_alignment_auc"]) > 0.65


def test_nonlinear_world_retains_relative_geometry_without_linear_transport() -> None:
    world = generate_world("nonlinear_metric_without_linear_coordinate", seed=31, persons=120, features=12, shared_rank=3, context_rank=2, noise_scale=0.18)
    result = evaluate_world(world, seed=31, shared_rank=3)
    assert float(result["relative_distance_spearman"]) > 0.25
    assert float(result["linear_transport_r2"]) < 0.35


def test_identification_matrix_runs_all_declared_worlds() -> None:
    rows = run_identification_matrix({
        "seed": 10, "repetitions": 2, "persons": 60, "features": 8, "shared_rank": 2,
        "context_rank": 2, "noise_scale": 0.18, "ridge_alpha": 10.0,
        "worlds": ["shared_linear", "null"],
    })
    assert len(rows) == 4
    assert {str(row["world"]) for row in rows} == {"shared_linear", "null"}
