from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.technical_replicates import (
    aggregate_static_replicates,
    assign_within_condition_replicates,
)


def _units() -> pd.DataFrame:
    return pd.DataFrame({
        "user_id": ["u1"] * 5 + ["u2"] * 3,
        "half": ["early"] * 8,
        "condition": ["a"] * 3 + ["b"] * 2 + ["a"] * 3,
        "created_utc": np.arange(8, dtype=float),
        "order": np.arange(8, dtype=int),
    })


def test_replicates_keep_both_halves_of_each_supported_condition() -> None:
    assigned = assign_within_condition_replicates(_units(), scheme="interleaved")
    counts = assigned.groupby(["user_id", "condition", "technical_replica"], observed=True).size()
    assert counts.loc[("u1", "a", 0)] > 0
    assert counts.loc[("u1", "a", 1)] > 0
    assert counts.loc[("u1", "b", 0)] > 0
    assert counts.loc[("u1", "b", 1)] > 0


def test_static_aggregation_returns_one_point_per_user_replica() -> None:
    assigned = assign_within_condition_replicates(_units(), scheme="blocked")
    residual = np.column_stack([np.arange(len(assigned)), np.ones(len(assigned))])
    frame = aggregate_static_replicates(assigned, residual)
    assert {"static_00", "static_01", "n_comments", "n_conditions"}.issubset(frame.columns)
    assert len(frame) == 4
