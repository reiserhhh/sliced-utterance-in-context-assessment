from __future__ import annotations

from suica_sim.opportunity_structure import (estimate_person_operators,
    generate_opportunity_world, individual_dynamics_world, operator_metrics,
    single_context_refusal)

import numpy as np


def test_operator_requires_condition_excitation():
    world = generate_opportunity_world(1, persons=40)
    assert single_context_refusal(world) == 1.0


def test_person_operator_is_recovered_and_generalizes():
    world = generate_opportunity_world(2, persons=100, occasions=15)
    metrics = operator_metrics(world, True)
    assert metrics["operator_recovery_r"] > .60
    assert metrics["person_prediction_delta"] > .05


def test_opportunity_only_does_not_create_conditioned_person_operator():
    world = generate_opportunity_world(3, persons=100, occasions=15,
                                       author_response=False)
    metrics = operator_metrics(world, True)
    assert abs(metrics["person_prediction_delta"]) < .05


def test_all_users_are_identifiable_under_free_design():
    world = generate_opportunity_world(4, persons=50)
    _, identifiable = estimate_person_operators(world)
    assert identifiable.all()


def test_individual_inertia_and_recovery_are_recovered_with_repeated_excitation():
    result = individual_dynamics_world(np.random.default_rng(5), 100)
    assert result["operator_relative_error"] < .15
    assert result["half_life_relative_error"] < .15
    assert result["own_prediction_delta"] > 0
    assert result["single_session_refusal_rate"] == 1.0
