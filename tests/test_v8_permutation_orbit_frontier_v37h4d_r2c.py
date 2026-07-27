"""Protocol tests for the H4D-R2C permutation-orbit runner."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.run_suica_v8_permutation_orbit_frontier_v37h4d_r2c import (
    _geometry_plan,
    _read,
    _source_lock,
    _spectrum_retest,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/v8_permutation_orbit_frontier_v37h4d_r2c.json"


def test_geometry_plan_has_one_core_and_eight_halo_cells() -> None:
    config = _read(CONFIG)
    for m in [4, 8]:
        plan = _geometry_plan(config, active_test_authors=m)
        assert len(plan) == 9
        core = [row for row in plan if row["halo_lambda"] == 0.0]
        assert core == [{
            "halo_lambda": 0.0,
            "halo_author_support": m,
            "support_label": "core_only",
        }]
        assert sum(row["support_label"] == "bounded_8" for row in plan) == 4
        assert sum(row["support_label"] == "all_test" for row in plan) == 4


def test_frozen_sources_and_comparator_match() -> None:
    assert _source_lock(_read(CONFIG))["pass"]


def test_spectrum_retest_reports_within_cell_correlation() -> None:
    rows = []
    for cell in [0, 1]:
        for repetition in range(5):
            rows.append({
                "noise_mode": "gaussian",
                "active_test_authors": 4,
                "halo_lambda": float(cell),
                "halo_author_support": 8,
                "support_label": f"cell-{cell}",
                "mechanism_n1": 100 * cell + repetition,
                "outcome_n1": 100 * cell - repetition,
                "mechanism_n2": 100 * cell + repetition,
                "outcome_n2": 100 * cell - repetition,
                "mechanism_n_inf": 100 * cell + repetition,
                "outcome_n_inf": 100 * cell - repetition,
            })
    result = _spectrum_retest(pd.DataFrame(rows))
    assert result["overall"]["n1"] > 0.9
    assert result["within_cell"]["n1"] < -0.99
