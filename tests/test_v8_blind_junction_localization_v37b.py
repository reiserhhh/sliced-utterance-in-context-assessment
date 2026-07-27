"""Tests for V3.7B geometry-only blind junction localization."""
from __future__ import annotations

import inspect

import numpy as np

from suica_core.v8_blind_junction_localization import (
    BlindJunctionSpec,
    estimate_masked_packet_profile,
    infer_route_branches,
    localization_panel_metrics,
    localize_trajectories,
    simulate_junction_trajectories,
    simulate_no_junction_trajectories,
)
from suica_core.v8_author_routing_operator import (
    AuthorRoutingSpec,
    simulate_author_routing_world,
)


def test_locator_api_cannot_read_routing_or_identity_metadata() -> None:
    parameters = inspect.signature(localize_trajectories).parameters
    for forbidden in (
        "cue",
        "author",
        "group",
        "outgoing",
        "context",
        "session",
    ):
        assert forbidden not in parameters


def test_true_junctions_are_localized_and_routes_recovered() -> None:
    spec = BlindJunctionSpec(threshold=0.45)
    incoming = np.tile(np.arange(4), 100)
    outgoing = np.roll(incoming, 1)
    cue = np.roll(incoming, 2)
    sample = simulate_junction_trajectories(
        incoming,
        outgoing,
        cue,
        seed=9_101,
        spec=spec,
    )
    located = localize_trajectories(
        sample["trajectory"],
        window=spec.locator_window,
        threshold=spec.threshold,
    )
    assert located["detected"].mean() > 0.90
    error = np.abs(located["location"] - sample["junction"])
    assert np.mean(error[located["detected"]] <= 1) > 0.95
    inferred_in, inferred_out = infer_route_branches(
        sample["trajectory"],
        located["location"],
        window=spec.locator_window,
        branches=4,
    )
    valid = located["detected"]
    assert np.mean(inferred_in[valid] == incoming[valid]) > 0.95
    assert np.mean(inferred_out[valid] == outgoing[valid]) > 0.95


def test_negative_attacks_have_low_false_junction_rate() -> None:
    spec = BlindJunctionSpec(threshold=0.45)
    negative = simulate_no_junction_trajectories(
        seed=9_201,
        count=5_000,
        spec=spec,
    )
    located = localize_trajectories(
        negative["trajectory"],
        window=spec.locator_window,
        threshold=spec.threshold,
    )
    assert 1000.0 * located["detected"].mean() <= 5.0


def test_panel_metrics_pass_directional_smoke_gate() -> None:
    spec = BlindJunctionSpec(threshold=0.45)
    rng = np.random.default_rng(9_301)
    positive = simulate_junction_trajectories(
        rng.integers(0, 4, size=1_000),
        rng.integers(0, 4, size=1_000),
        rng.integers(0, 4, size=1_000),
        seed=9_302,
        spec=spec,
    )
    negative = simulate_no_junction_trajectories(
        seed=9_303,
        count=2_000,
        spec=spec,
    )
    metrics = localization_panel_metrics(
        positive,
        negative,
        window=spec.locator_window,
        threshold=spec.threshold,
    )
    assert metrics["precision"] > 0.85
    assert metrics["recall"] > 0.75
    assert metrics["f1"] > 0.80
    assert metrics["false_junctions_per_1000"] <= 5.0


def test_masked_profile_retains_partial_cells_but_refuses_no_overlap() -> None:
    sample = simulate_author_routing_world(
        seed=9_401,
        world="stable_author",
        spec=AuthorRoutingSpec(
            authors=16,
            groups=4,
            discovery_contexts=6,
            confirmation_contexts=4,
            extrapolation_contexts=2,
        ),
    )
    sample["counts"][0, 0, 0, 0] = 0
    sample["trials"][0, 0, 0, 0] = 0
    estimate = estimate_masked_packet_profile(
        sample,
        np.arange(6),
    )
    assert not estimate["refused"]
    assert np.isfinite(estimate["profile"]).all()

    sample["counts"][0, :, :6, 0] = 0
    sample["trials"][0, :, :6, 0] = 0
    refused = estimate_masked_packet_profile(
        sample,
        np.arange(6),
    )
    assert refused["status"] == "REFUSE_NONOVERLAP"
