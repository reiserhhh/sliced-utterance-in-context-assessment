"""Identification and refusal tests for V8 planted worlds."""
from __future__ import annotations

from suica_core.v8_simulation import (
    SimulationSpec,
    estimate_world,
    run_simulation_repetition,
    simulate_world,
)


def _small_spec() -> SimulationSpec:
    return SimulationSpec(
        persons=80,
        sessions=4,
        units_per_session=8,
        choice_opportunities=48,
        noise_sd=0.20,
    )


def test_identified_world_recovers_declared_components() -> None:
    result = run_simulation_repetition(seed=41, world="identified_independent", spec=_small_spec())
    assert result["theta_status"] == "READY"
    assert result["theta_geometry_r"] > 0.70
    assert result["state_r"] > 0.60
    assert result["choice_probability_r"] > 0.55
    assert result["response_operator_r"] > 0.70
    assert result["history_operator_r"] > 0.70


def test_wrong_design_worlds_refuse_only_unidentified_components() -> None:
    missing_menu = estimate_world(
        simulate_world(seed=1, world="missing_menu", spec=_small_spec()),
        ridge=0.25,
    )
    assert missing_menu["status"]["choice"] == "REFUSE_MENU_UNOBSERVED"
    assert missing_menu["status"]["theta"] == "READY"

    nonrandom = estimate_world(
        simulate_world(seed=2, world="nonrandom_condition", spec=_small_spec()),
        ridge=0.25,
    )
    assert nonrandom["status"]["response"] == "REFUSE_CONDITION_NOT_RANDOMIZED"
    assert nonrandom["status"]["history"] == "READY"

    hidden = estimate_world(
        simulate_world(seed=3, world="hidden_history", spec=_small_spec()),
        ridge=0.25,
    )
    assert hidden["status"]["history"] == "REFUSE_HISTORY_UNOBSERVED"


def test_single_occasion_and_model_drift_refuse_person_components() -> None:
    for world in ("single_occasion", "model_drift"):
        estimate = estimate_world(
            simulate_world(seed=7, world=world, spec=_small_spec()),
            ridge=0.25,
        )
        assert all(status.startswith("REFUSE_") for status in estimate["status"].values())
