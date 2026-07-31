"""Tests for M4-C.3.5-R2C applicability and fallback routing."""
from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.m4_abstention_routing import (
    add_frozen_policy_arm,
    rcca_coverage_profile,
    verify_frozen_policy_identity,
)
from suica_core.m4_chart_ecology_generator import (
    M4ChartEcologySpec,
    generate_m4_pre_response_condition,
)
from suica_core.m4_response_safe_rcca_chart import (
    fit_response_safe_rcca_chart,
)


def test_coverage_profile_reproduces_frozen_chart_coverage() -> None:
    spec = M4ChartEcologySpec(
        reference_authors=8,
        mechanism_authors=8,
        reference_calibration_points=16,
        reference_selection_points=16,
        categories=16,
        events=24,
    )
    observed = generate_m4_pre_response_condition(
        world="endogenous_creation_expansion",
        spec=spec,
        seed=470_017,
    )
    chart = fit_response_safe_rcca_chart(
        observed,
        support_permutation_repetitions=19,
        support_bootstrap_repetitions=19,
        canonical_permutation_repetitions=19,
        canonical_bootstrap_repetitions=19,
        null_trials=5,
        minimum_support_stability_lcb=0.0,
        minimum_consensus_eigenvalue=0.0,
        minimum_native_consensus_affinity=0.0,
        minimum_projector_affinity=0.0,
        minimum_heldout_cka=0.0,
        minimum_coverage=0.0,
        seed=470_017,
    )
    profile = rcca_coverage_profile(
        chart,
        observed,
        minimum_coverage=0.0,
    )
    assert np.isclose(profile.minimum_coverage, chart.coverage)
    assert np.isclose(profile.minimum_margin, profile.minimum_coverage)
    assert len(profile.role_coverage) == 4


def test_policy_arm_routes_accepted_to_r_and_refused_to_b0() -> None:
    metrics = pd.DataFrame(
        [
            {
                "repetition": repetition,
                "world": world,
                "world_type": "main",
                "view": view,
                "arm": arm,
                "geometry": value,
            }
            for repetition, world, accepted in (
                (0, "accepted", True),
                (0, "refused", False),
            )
            for view in ("train", "test")
            for arm, value in (
                ("B0", 0.2),
                ("R", 0.8),
                ("Oest", 1.0),
            )
        ]
    )
    policy = pd.DataFrame(
        [
            {"repetition": 0, "world": "accepted", "accepted": True},
            {"repetition": 0, "world": "refused", "accepted": False},
        ]
    )
    output = add_frozen_policy_arm(metrics, policy)
    routed = output[output["arm"].eq("Pi")].set_index(["world", "view"])
    assert np.allclose(routed.loc["accepted", "geometry"], 0.8)
    assert np.allclose(routed.loc["refused", "geometry"], 0.2)
    assert verify_frozen_policy_identity(metrics, policy) == 0.0
