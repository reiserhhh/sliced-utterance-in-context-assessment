"""Tests for C3.4 shard aggregation helpers."""
from __future__ import annotations

import pandas as pd

from scripts.aggregate_suica_m4_creation_residual_attribution import (
    _coerce,
)


def test_coerce_preserves_world_labels_and_converts_numeric_cells() -> None:
    frame = pd.DataFrame(
        {
            "world_type": ["null", "main"],
            "value": ["0.25", ""],
        }
    )
    converted = _coerce(frame, ("value",))
    assert converted["world_type"].tolist() == ["null", "main"]
    assert converted["value"].iloc[0] == 0.25
    assert pd.isna(converted["value"].iloc[1])
