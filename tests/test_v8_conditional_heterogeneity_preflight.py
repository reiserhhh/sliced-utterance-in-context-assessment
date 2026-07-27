"""Unit tests for repeated-outcome R2D Gate-0 primitives."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from scripts.run_suica_v8_geometry_information_operator_v37h4d_r2b import (
    _simulate_base_world,
)
from scripts.run_suica_v8_reference_measure_frontier_v37h4d import (
    _read,
    _spec,
)
from suica_core.v8_conditional_heterogeneity_preflight import (
    conditional_variance,
    half_split_probabilities,
    resample_outcome_pair,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = (
    ROOT / "configs/v8_conditional_heterogeneity_gate0_v37h4d_r2d.json"
)


def test_conditional_variance_is_untruncated() -> None:
    assert conditional_variance(
        np.asarray([0, 16]),
        replicates=16,
    ) == 0.5
    assert conditional_variance(
        np.asarray([8, 8]),
        replicates=16,
    ) < 0.0


def test_half_split_uses_registered_jeffreys_estimator() -> None:
    observed = half_split_probabilities(
        np.asarray([0, 8, 16]),
        half_replicates=16,
    )
    np.testing.assert_allclose(
        observed,
        np.asarray([0.5, 8.5, 16.5]) / 17.0,
    )


def test_resampled_outcome_pair_is_seeded_and_fresh() -> None:
    config = _read(CONFIG)
    world = _simulate_base_world(
        config,
        noise_mode="gaussian",
        seed=171,
    )
    _, _, test = _spec(config).author_split
    kwargs = {
        "test_authors": test,
        "noise_mode": "gaussian",
        "opportunity_prefixes": tuple(config["opportunity_prefixes"]),
        "primary_opportunities": config["primary_opportunities"],
        "panel_noise_amplitude": config["panel_noise_amplitude"],
        "technical_noise_amplitude": config[
            "technical_noise_amplitude"
        ],
        "student_df": config["student_df"],
        "heteroskedastic_strength": config[
            "heteroskedastic_strength"
        ],
    }
    first = resample_outcome_pair(world, seed=23, **kwargs)
    replay = resample_outcome_pair(world, seed=23, **kwargs)
    fresh = resample_outcome_pair(world, seed=24, **kwargs)
    for observed, expected in zip(first, replay, strict=True):
        np.testing.assert_array_equal(observed, expected)
    assert any(
        not np.array_equal(left, right)
        for left, right in zip(first[:2], fresh[:2], strict=True)
    )
    assert first[0].shape == (
        len(test),
        config["spec"]["conditions"],
        config["spec"]["dimensions"],
    )
