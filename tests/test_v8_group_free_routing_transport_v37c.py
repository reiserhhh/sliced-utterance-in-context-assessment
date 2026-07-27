"""Tests for V3.7C group-free routing transport."""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd

from scripts.run_suica_v8_group_free_routing_transport_v37c import _summaries
from suica_core.v8_author_routing_operator import (
    AuthorRoutingSpec,
    fit_reference_router,
    simulate_author_routing_world,
)
from suica_core.v8_group_free_routing_transport import (
    TransportPathSpec,
    apply_group_free_denoiser,
    apply_registered_missingness,
    estimate_fixed_reference_profile,
    fit_group_free_denoiser,
    group_free_pairing_metrics,
    resample_routing_counts,
    transport_localization_metrics,
)


def _sample(seed: int = 91_101) -> dict:
    return simulate_author_routing_world(
        seed=seed,
        world="stable_author",
        spec=AuthorRoutingSpec(
            authors=16,
            groups=4,
            discovery_contexts=6,
            confirmation_contexts=4,
            extrapolation_contexts=2,
            author_rank=4,
            group_rms=0.0,
        ),
    )


def test_group_free_denoiser_has_no_group_or_label_parameter() -> None:
    parameters = inspect.signature(fit_group_free_denoiser).parameters
    assert "groups" not in parameters
    assert "labels" not in parameters


def test_group_free_denoiser_recovers_shared_cross_half_direction() -> None:
    rng = np.random.default_rng(91_201)
    truth = rng.normal(size=(64, 3)) @ rng.normal(size=(3, 12))
    left = truth + rng.normal(scale=0.25, size=truth.shape)
    right = truth + rng.normal(scale=0.25, size=truth.shape)
    denoiser = fit_group_free_denoiser(left, right, rank=3)
    cleaned = apply_group_free_denoiser(0.5 * (left + right), denoiser)
    raw_error = np.mean((0.5 * (left + right) - truth) ** 2)
    clean_error = np.mean((cleaned - truth) ** 2)
    assert denoiser["rank"] == 3
    assert clean_error < raw_error


def test_independent_count_panels_do_not_reuse_events() -> None:
    sample = _sample()
    left = resample_routing_counts(
        sample,
        np.random.default_rng(91_301),
    )
    right = resample_routing_counts(
        sample,
        np.random.default_rng(91_302),
    )
    assert not np.array_equal(left["counts"], right["counts"])
    assert np.array_equal(left["probability"], right["probability"])


def test_fixed_reference_profile_uses_external_reference() -> None:
    sample = _sample()
    discovery = np.arange(6)
    reference_fit = fit_reference_router(sample, discovery)
    estimate = estimate_fixed_reference_profile(
        sample,
        discovery,
        reference_fit=reference_fit,
    )
    assert not estimate["refused"]
    assert estimate["profile"].shape == (16, 48)
    assert np.isfinite(estimate["profile"]).all()


def test_mar_ipw_and_aipw_profiles_are_finite() -> None:
    sample = _sample()
    masked = apply_registered_missingness(
        sample,
        rng=np.random.default_rng(91_401),
        kind="mar",
        base_probability=0.72,
        floor=0.50,
        ceiling=0.95,
        gamma=0.0,
    )
    discovery = np.arange(6)
    reference_fit = fit_reference_router(sample, discovery)
    for method in ("available", "ipw", "aipw"):
        estimate = estimate_fixed_reference_profile(
            masked,
            discovery,
            reference_fit=reference_fit,
            method=method,
        )
        assert not estimate["refused"]
        assert np.isfinite(estimate["profile"]).all()
    assert 0.50 <= masked["observation_probability"].min()
    assert masked["observation_probability"].max() <= 0.95


def test_local_pairing_uses_hard_negative_candidates() -> None:
    rng = np.random.default_rng(91_501)
    left = rng.normal(size=(32, 8))
    right = left + rng.normal(scale=0.05, size=left.shape)
    metrics = group_free_pairing_metrics(
        left,
        right,
        neighbor_count=8,
    )
    assert metrics["same_author_auc"] > 0.95
    assert metrics["local_neighbor_auc"] > 0.90


def test_unconditional_location_error_penalizes_misses() -> None:
    metrics = transport_localization_metrics(
        rng=np.random.default_rng(91_601),
        spec=TransportPathSpec(threshold=10.0),
        mechanism="core",
        positive_count=300,
        negative_count=600,
    )
    assert metrics["recall"] == 0.0
    assert metrics["unconditional_median_error"] == 25.0
    assert metrics["unconditional_p95_error"] == 25.0


def test_observationally_isomorphic_labels_are_refused() -> None:
    metrics = transport_localization_metrics(
        rng=np.random.default_rng(91_701),
        spec=TransportPathSpec(threshold=0.30),
        mechanism="core",
        positive_count=1000,
        negative_count=1000,
    )
    assert 0.45 <= metrics["isomorphic_auc"] <= 0.55
    assert metrics["isomorphic_refusal"]


def test_gain_retention_is_undefined_when_oracle_gain_is_nonpositive() -> None:
    frame = pd.DataFrame({
        "arm": ["low_budget", "low_budget"],
        "numeric_output": [True, True],
        "isomorphic_refusal": [True, True],
        "blind_log_loss_gain": [-0.01, -0.02],
        "oracle_log_loss_gain": [-0.005, -0.006],
    })
    ratio = _summaries(frame, seed=91_801)["low_budget"][
        "gain_retention_ratio"
    ]
    assert ratio["status"] == "UNDEFINED_NONPOSITIVE_ORACLE_GAIN"
    assert ratio["mean"] is None
