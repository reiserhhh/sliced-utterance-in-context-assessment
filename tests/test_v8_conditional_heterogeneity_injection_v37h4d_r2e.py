"""Protocol tests for the H4D-R2E injection runner."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from scripts.run_suica_v8_conditional_heterogeneity_injection_v37h4d_r2e import (
    _geometry_plan,
    _paired_total_variance,
    _read,
    _source_lock,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = (
    ROOT
    / "configs"
    / "v8_conditional_heterogeneity_injection_v37h4d_r2e.json"
)


def test_geometry_plan_has_one_baseline_and_twelve_crossover_arms() -> None:
    config = _read(CONFIG)
    plan = _geometry_plan(config)
    assert len(plan) == 13
    assert sum(row["arm"] == "baseline" for row in plan) == 1
    for arm in ["normal", "tangent"]:
        assert sum(row["arm"] == arm for row in plan) == 6
        for magnitude in config[
            "normal_tau_grid"
            if arm == "normal"
            else "tangent_phi_grid"
        ]:
            signs = {
                row["sign"]
                for row in plan
                if row["arm"] == arm
                and np.isclose(row["magnitude"], magnitude)
            }
            assert signs == {-1, 1}


def test_frozen_sources_match_before_outcome_run() -> None:
    assert _source_lock(_read(CONFIG))["pass"]


def test_paired_total_variance_decomposes_midpoint_and_direction() -> None:
    plus = np.ones((5, 8))
    minus = np.zeros((5, 8))
    result = _paired_total_variance(plus, minus)
    assert result["direction_sensitivity_j"] == 0.25
    assert result["midpoint_variance"] == 0.0
    assert result["total_side_variance"] == 0.25
    assert result["plus_minus_rate_gap"] == 1.0
