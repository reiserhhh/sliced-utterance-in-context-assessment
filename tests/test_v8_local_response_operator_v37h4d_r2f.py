from __future__ import annotations

import numpy as np

from scripts.run_suica_v8_local_response_operator_v37h4d_r2f import (
    _geometry_plan,
)


def _config() -> dict:
    return {
        "tangent_dimensions": 4,
        "finite_difference_step": 0.1,
        "normal_tau": 0.09,
        "registered_null_phi": 0.4,
    }


def test_geometry_plan_is_complete_and_unique() -> None:
    plan = _geometry_plan(_config())
    assert len(plan) == 45
    assert len({item["geometry_id"] for item in plan}) == 45
    counts = {}
    for item in plan:
        counts[item["arm"]] = counts.get(item["arm"], 0) + 1
    assert counts == {
        "baseline": 1,
        "axis": 16,
        "corner": 24,
        "normal": 2,
        "registered_null": 2,
    }


def test_all_local_coefficients_have_registered_radius() -> None:
    plan = _geometry_plan(_config())
    for item in plan:
        coefficients = np.asarray(item["coefficients"])
        if item["arm"] == "axis":
            assert np.isclose(
                np.linalg.norm(coefficients),
                item["magnitude"],
            )
        elif item["arm"] == "corner":
            assert np.isclose(np.linalg.norm(coefficients), np.sqrt(0.02))
        else:
            assert np.allclose(coefficients, 0.0)
