"""Tests for M4-C.3.3 frontier aggregation statistics."""
from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.run_suica_m4_opportunity_excitation_frontier import (
    _dose_slopes,
    _paired_endpoint_values,
)


def _frame() -> pd.DataFrame:
    rows = []
    for repetition in range(3):
        for world in ("first", "second"):
            for k, intervention, information in (
                (1, "passive", 1.0),
                (2, "passive", 2.0),
                (1, "excitation", 3.0),
                (2, "excitation", 6.0),
            ):
                rows.append(
                    {
                        "repetition": repetition,
                        "world": world,
                        "k": k,
                        "intervention": intervention,
                        "fisher_minimum_information": information,
                        "fisher_geometry": (
                            0.4 + 0.1 * np.log(information)
                        ),
                    }
                )
    return pd.DataFrame(rows)


def test_endpoint_ratio_and_delta_are_repetition_clustered() -> None:
    frame = _frame()
    ratio = _paired_endpoint_values(
        frame,
        "fisher_minimum_information",
        low=(1, "passive"),
        high=(2, "excitation"),
        ratio=True,
    )
    delta = _paired_endpoint_values(
        frame,
        "fisher_geometry",
        low=(1, "passive"),
        high=(2, "excitation"),
    )
    assert np.allclose(ratio, 6.0)
    assert np.allclose(delta, 0.1 * np.log(6.0))


def test_fixed_world_dose_slope_recovers_planted_relation() -> None:
    slopes = _dose_slopes(_frame())
    assert np.allclose(slopes, 0.1)
