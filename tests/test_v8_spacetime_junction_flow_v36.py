"""Tests for V3.6 spacetime common-junction routing."""
from __future__ import annotations

import numpy as np

from suica_core.v8_spacetime_junction_flow import (
    JunctionFlowSpec,
    analyze_junction_world,
    simulate_junction_world,
    static_marginal_features,
)


def test_primary_routing_regimes_are_separated() -> None:
    spec = JunctionFlowSpec()
    for policy in ("pass_through", "random_branch", "cue_guided"):
        sample = simulate_junction_world(
            seed=127,
            policy=policy,
            spec=spec,
        )
        result = analyze_junction_world(sample, spec=spec)
        assert result["status"] == "ESTIMATE_READY"
        assert result["predicted_policy"] == policy
        assert result["group_claim"]
        assert result["group_f1"] == 1.0


def test_primary_worlds_match_static_branch_marginals() -> None:
    spec = JunctionFlowSpec()
    features = []
    for policy in ("pass_through", "random_branch", "cue_guided"):
        sample = simulate_junction_world(
            seed=131,
            policy=policy,
            spec=spec,
        )
        features.append(static_marginal_features(sample, spec=spec))
    for feature in features[1:]:
        assert np.allclose(features[0][:9], feature[:9])


def test_time_and_tangent_attacks_refuse() -> None:
    spec = JunctionFlowSpec()
    time = analyze_junction_world(
        simulate_junction_world(
            seed=137,
            policy="cue_guided",
            attack="time_shuffle",
            spec=spec,
        ),
        spec=spec,
    )
    tangent = analyze_junction_world(
        simulate_junction_world(
            seed=139,
            policy="cue_guided",
            attack="tangent_view_shuffle",
            spec=spec,
        ),
        spec=spec,
    )
    assert time["status"] == "REFUSE_TIME_ORDER"
    assert tangent["status"] == "REFUSE_VIEW_INSTABILITY"


def test_intersection_is_neither_sufficient_nor_necessary_for_routing() -> None:
    spec = JunctionFlowSpec()
    random = analyze_junction_world(
        simulate_junction_world(
            seed=149,
            policy="random_branch",
            spec=spec,
        ),
        spec=spec,
    )
    near_miss = analyze_junction_world(
        simulate_junction_world(
            seed=151,
            policy="cue_guided",
            attack="near_miss",
            spec=spec,
        ),
        spec=spec,
    )
    assert random["group_claim"]
    assert not random["cue_guided_claim"]
    assert near_miss["status"] == "REFUSE_NO_JUNCTION"
    assert near_miss["predicted_policy"] == "cue_guided"
    assert near_miss["cue_information"] >= 0.80


def test_time_axis_and_tree_routing_add_distinct_information() -> None:
    spec = JunctionFlowSpec()
    guided = analyze_junction_world(
        simulate_junction_world(
            seed=157,
            policy="cue_guided",
            spec=spec,
        ),
        spec=spec,
    )
    shuffled = analyze_junction_world(
        simulate_junction_world(
            seed=157,
            policy="cue_guided",
            attack="cue_shuffle",
            spec=spec,
        ),
        spec=spec,
    )
    assert guided["x_only_stage_accuracy"] <= 0.50
    assert guided["spacetime_stage_accuracy"] >= 0.95
    assert guided["goal_path_accuracy"] >= 0.95
    assert guided["addressable_leaves"] == spec.branches**spec.depth
    assert shuffled["cue_information"] <= 0.10
    assert not shuffled["cue_guided_claim"]
