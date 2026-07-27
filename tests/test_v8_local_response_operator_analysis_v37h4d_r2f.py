from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.analyze_suica_v8_local_response_operator_v37h4d_r2f import (
    _principal_angle,
    _probability_table,
)


def test_probability_table_uses_disjoint_equal_halves() -> None:
    rows = []
    for replicate in range(8):
        rows.append({
            "parent_id": "p0",
            "noise_mode": "gaussian",
            "geometry_id": "baseline",
            "arm": "baseline",
            "magnitude": 0.0,
            "sign": 0,
            "axis_left": -1,
            "axis_right": -1,
            "sign_left": 0,
            "sign_right": 0,
            "outcome_replicate": replicate,
            "crc_or_hc_detected": replicate >= 2,
        })
    table = _probability_table(pd.DataFrame(rows), outcome_replicates=8)
    assert len(table) == 2
    observed = dict(zip(table["half"], table["probability"], strict=True))
    assert observed == {"A": 0.5, "B": 1.0}


def test_principal_angle_ignores_axis_sign() -> None:
    left = np.asarray([1.0, 2.0, -1.0])
    assert np.isclose(_principal_angle(left, left), 0.0)
    assert np.isclose(_principal_angle(left, -left), 0.0)
    assert np.isclose(
        _principal_angle(left, np.asarray([2.0, -1.0, 0.0])),
        90.0,
    )
