"""Regression tests for C3.3 report rendering."""
from __future__ import annotations

import pandas as pd

from scripts.render_suica_m4_opportunity_excitation_report import (
    REPORT_NUMERIC_COLUMNS,
    coerce_report_numeric_columns,
)


def test_report_columns_survive_mixed_null_world_serialization() -> None:
    frame = pd.DataFrame(
        {
            column: ["0.25", "not_applicable"]
            for column in REPORT_NUMERIC_COLUMNS
        }
    )

    coerced = coerce_report_numeric_columns(frame)

    for column in REPORT_NUMERIC_COLUMNS:
        assert coerced[column].iloc[0] == 0.25
        assert pd.isna(coerced[column].iloc[1])
