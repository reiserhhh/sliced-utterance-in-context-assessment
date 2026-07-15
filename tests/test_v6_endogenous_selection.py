from __future__ import annotations

from suica_sim.endogenous_selection import (
    evaluate_endogenous_selection_world,
    generate_endogenous_selection_world,
    run_endogenous_selection_design,
)


def test_fixed_phase_has_complete_condition_support_while_free_phase_can_fail() -> None:
    world = generate_endogenous_selection_world(
        4,
        persons=120,
        features=4,
        conditions=4,
        free_trials=6,
        fixed_repeats=2,
        selection_strength=2.0,
        condition_scale=0.0,
        noise_scale=0.25,
    )
    metrics = evaluate_endogenous_selection_world(world)
    assert metrics["fixed_response_support"] == 1.0
    assert metrics["free_response_support"] < 1.0


def test_selection_linked_centering_changes_the_author_level_estimand() -> None:
    world = generate_endogenous_selection_world(
        8,
        persons=300,
        features=6,
        conditions=4,
        free_trials=24,
        fixed_repeats=3,
        selection_strength=2.0,
        condition_scale=0.0,
        noise_scale=0.20,
    )
    metrics = evaluate_endogenous_selection_world(world)
    assert metrics["selection_holdout_logscore_gain"] > 0.0
    assert metrics["raw_free_level_recovery_r"] > metrics["free_condition_centered_level_recovery_r"]


def test_condition_only_world_can_benefit_from_centering() -> None:
    world = generate_endogenous_selection_world(
        11,
        persons=300,
        features=6,
        conditions=4,
        free_trials=24,
        fixed_repeats=3,
        selection_strength=0.0,
        condition_scale=1.0,
        noise_scale=0.20,
    )
    metrics = evaluate_endogenous_selection_world(world)
    assert metrics["free_condition_centered_level_recovery_r"] > metrics["raw_free_level_recovery_r"]
    assert metrics["fixed_response_recovery_r"] > .60


def test_full_design_gates_hold_in_planted_worlds() -> None:
    config = {
        "profile": "test", "seed": 20, "repetitions": 8, "persons": 140,
        "features": 5, "conditions": 4, "free_trials": 18, "fixed_repeats": 3,
        "noise_scale": .28, "selection_signal_strength": 1.8,
        "selection_signal_condition_scale": 0.0,
        "condition_nuisance_selection_strength": 0.0,
        "condition_nuisance_condition_scale": .9,
        "minimum_fixed_response_recovery": .55,
        "maximum_free_response_support": .95,
    }
    result = run_endogenous_selection_design(config)
    assert all(result["gates"].values())
