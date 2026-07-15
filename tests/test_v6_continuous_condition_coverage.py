from __future__ import annotations

import pytest

from suica_sim.continuous_condition_coverage import run_continuous_condition_coverage


def _config() -> dict:
    return {
        "profile": "test",
        "seed": 17,
        "repetitions": 10,
        "persons": 120,
        "text_features": 4,
        "grid_side": 4,
        "basis_side": 3,
        "rbf_width": .65,
        "test_contexts": 36,
        "fixed_repeats": 2,
        "noise_scale": .22,
        "ridge_alpha": .10,
        "minimum_wide_response_recovery_r": .50,
        "material_response_gap": .01,
    }


def test_full_condition_coverage_beats_narrow_and_coarse_arms_in_planted_world() -> None:
    result = run_continuous_condition_coverage(_config())
    assert all(result["gates"].values())
    wide = result["scenarios"]["wide_exact"]
    narrow = result["scenarios"]["narrow_exact_same_budget"]
    coarse = result["scenarios"]["wide_coarse_proxy"]
    assert wide["fixed_total_observations"]["mean"] == narrow["fixed_total_observations"]["mean"]
    assert wide["response_function_recovery_r"]["mean"] > narrow["response_function_recovery_r"]["mean"]
    assert wide["response_function_recovery_r"]["mean"] > coarse["response_function_recovery_r"]["mean"]


def test_invalid_too_small_condition_grid_is_refused() -> None:
    config = _config()
    config["grid_side"] = 2
    with pytest.raises(ValueError, match="grid_side"):
        run_continuous_condition_coverage(config)
