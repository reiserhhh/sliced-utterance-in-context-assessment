"""Unit tests for R2E geometry and estimands."""
from __future__ import annotations

import numpy as np

from suica_core.v8_conditional_heterogeneity_injection import (
    frame_audit,
    geometry_audit,
    injection_geometry,
    orthonormal_geometry_frame,
    paired_direction_sensitivity,
)
from suica_core.v8_minority_information_frontier import (
    complete_double_center,
)


def _frame() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(17)
    core = complete_double_center(rng.normal(size=(16, 8, 3)))
    halo = complete_double_center(rng.normal(size=(16, 8, 3)))
    return orthonormal_geometry_frame(core, halo, seed=29)


def test_frame_is_orthonormal_and_double_centered() -> None:
    audit = frame_audit(*_frame())
    assert audit["maximum_axis_norm_error"] < 1e-12
    assert audit["maximum_axis_inner_product"] < 1e-12
    assert audit["maximum_double_centering_marginal_error"] < 1e-12


def test_normal_and_tangent_have_registered_halo_share() -> None:
    core, halo, tangent = _frame()
    theta = float(np.arcsin(np.sqrt(0.01)))
    tangent_q = injection_geometry(
        core,
        halo,
        tangent,
        theta=theta,
        arm="tangent",
        magnitude=0.4,
        sign=1,
    )
    tangent_audit = geometry_audit(
        tangent_q,
        core,
        expected_halo_share=0.01,
    )
    assert tangent_audit["geometry_norm_error"] < 1e-12
    assert tangent_audit["halo_share_error"] < 1e-12
    assert tangent_audit["realized_author_support"] == len(core)

    normal_q = injection_geometry(
        core,
        halo,
        tangent,
        theta=theta,
        arm="normal",
        magnitude=0.09,
        sign=-1,
    )
    expected = float(np.sin(theta - 0.09) ** 2)
    normal_audit = geometry_audit(
        normal_q,
        core,
        expected_halo_share=expected,
    )
    assert normal_audit["halo_share_error"] < 1e-12


def test_direction_sensitivity_is_untruncated() -> None:
    plus = np.ones((4, 8))
    minus = np.zeros((4, 8))
    assert paired_direction_sensitivity(plus, minus) == 0.25
    alternating = np.tile([0.0, 1.0], (4, 4))
    assert paired_direction_sensitivity(
        alternating,
        1.0 - alternating,
    ) < 0.0
