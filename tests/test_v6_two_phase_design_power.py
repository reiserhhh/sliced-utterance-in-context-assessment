from __future__ import annotations

import pytest

from suica_sim.two_phase_design_power import run_two_phase_design_calibration


def _config() -> dict:
    return {
        "profile": "test",
        "seed": 42,
        "repetitions": 10,
        "persons": 140,
        "features": 5,
        "conditions_grid": [2, 4],
        "fixed_repeats_grid": [1, 2],
        "free_trials_grid": [8, 16],
        "reference_conditions": 4,
        "reference_free_trials": 16,
        "reference_fixed_repeats": 2,
        "minimum_condition_breadth": 4,
        "selection_strength": 1.8,
        "condition_scale": 0.0,
        "noise_scale": 0.28,
        "minimum_fixed_level_recovery_r": 0.80,
        "minimum_fixed_response_recovery_r": 0.60,
        "minimum_free_selection_profile_r": 0.60,
    }


def test_two_phase_grid_reports_separate_free_and_fixed_estimands() -> None:
    result = run_two_phase_design_calibration(_config())
    assert len(result["fixed_grid"]) == 4
    assert len(result["free_grid"]) == 2
    assert all(row["summary"]["fixed_response_support"]["q025"] >= .99 for row in result["fixed_grid"])
    assert result["selection"]["minimum_numerically_adequate_fixed_design"] is not None
    assert result["selection"]["minimum_breadth_qualified_fixed_design"] is not None
    assert result["selection"]["minimum_qualified_free_design"] is not None


def test_invalid_condition_grid_refuses_one_condition_response_design() -> None:
    config = _config()
    config["conditions_grid"] = [1]
    with pytest.raises(ValueError, match="conditions_grid"):
        run_two_phase_design_calibration(config)
