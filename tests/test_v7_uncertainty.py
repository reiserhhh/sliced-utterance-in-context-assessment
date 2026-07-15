from __future__ import annotations

import numpy as np

from suica_core.v7_uncertainty import summarize_geometry_uncertainty


def _kwargs() -> dict[str, object]:
    return {
        "source_cluster_draws": np.array([0.1, 0.2, 0.3]),
        "model_refit_draws": np.array([0.1, 0.15, 0.25]),
        "reference_norm_draws": np.array([0.2, 0.25, 0.3]),
        "support_status": "GEOMETRY_PROFILE_READY",
    }


def test_total_uncertainty_refuses_without_joint_draws_or_assumption() -> None:
    result = summarize_geometry_uncertainty(**_kwargs())
    assert result["status"] == "REFUSE_TOTAL_GEOMETRY_UNCERTAINTY_DEPENDENCE_UNMODELED"


def test_joint_uncertainty_returns_conditional_interval() -> None:
    result = summarize_geometry_uncertainty(**_kwargs(), joint_nested_draws=np.array([0.1, 0.2, 0.4, 0.3]))
    assert result["status"] == "CONDITIONAL_GEOMETRY_UNCERTAINTY_READY"
    assert result["total_interval_95"][0] <= result["total_interval_95"][1]


def test_out_of_support_row_refuses_precision() -> None:
    kwargs = _kwargs()
    kwargs["support_status"] = "GEOMETRY_REFUSE_OUTSIDE_REFERENCE_RADIAL_ENVELOPE"
    result = summarize_geometry_uncertainty(**kwargs)
    assert result["status"] == "REFUSE_GEOMETRY_UNCERTAINTY_OUT_OF_SUPPORT"
