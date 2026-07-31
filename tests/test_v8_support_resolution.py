"""Tests for the V8 local support-resolution frontier."""
from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v8_support_resolution import (
    SupportResolutionSpec,
    _bank,
    _cell_values,
    classify_frontier,
)


def test_oracle_objective_dominates_frozen_filter_on_same_density() -> None:
    density = np.diag(np.asarray([12, 8, 5, 3, 2, 1, 1, 1], dtype=float))
    density /= np.trace(density)
    bank = _bank(
        density,
        capacities=(2, 4),
        tau_multipliers=(0.5, 1.0),
    )
    rows = _cell_values(bank, density)
    assert all(row["oracle_excess"] >= row["native_excess"] - 1e-10 for row in rows)
    assert all(np.isclose(row["resolution_ratio"], 1.0) for row in rows)


def test_frontier_requires_both_confirmation_splits() -> None:
    rows = pd.DataFrame(
        [
            {
                "capacity": 8,
                "split": "D1",
                "status": "RESOLUTION_ESTIMATED",
                "native_excess_ci_low": 0.1,
                "rotation_q": 0.01,
                "d0_internal_p": 0.01,
            }
        ]
    )
    result = classify_frontier(rows)
    assert result["confirmed_capacities"] == []


def test_frontier_confirms_only_double_replicated_capacity() -> None:
    rows = pd.DataFrame(
        [
            {
                "capacity": capacity,
                "split": split,
                "status": "RESOLUTION_ESTIMATED",
                "native_excess_ci_low": 0.1 if capacity == 16 else -0.01,
                "rotation_q": 0.01,
                "d0_internal_p": 0.01,
            }
            for capacity in (8, 16)
            for split in ("D1", "D2")
        ]
    )
    result = classify_frontier(rows)
    assert result["decision"] == "REPLICATED_CAPACITY_FRONTIER"
    assert result["confirmed_capacities"] == [16]


def test_resolution_spec_rejects_invalid_tau_grid() -> None:
    try:
        SupportResolutionSpec(tau_multipliers=(0.0,))
    except ValueError as exc:
        assert "tau_multipliers" in str(exc)
    else:
        raise AssertionError("Invalid tau grid was accepted.")
