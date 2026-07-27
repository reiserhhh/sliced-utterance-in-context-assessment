"""Tests for V3.6.1 path-level scope correction."""
from __future__ import annotations

import numpy as np

from suica_core.v8_spacetime_junction_flow import (
    JunctionFlowSpec,
    _branch_estimates,
    simulate_junction_world,
)
from suica_core.v8_spacetime_path_audit import (
    conditional_path_information_permutation,
    heldout_local_route_accuracy,
    path_information,
)


def _metrics(policy: str) -> tuple[dict[str, float], dict[str, float]]:
    spec = JunctionFlowSpec()
    sample = simulate_junction_world(seed=181, policy=policy, spec=spec)
    branch = _branch_estimates(
        sample["observations"],
        sample["cues"],
        sample["labels"],
        spec=spec,
    )
    outgoing = branch["outgoing_labels"][0]
    incoming = branch["incoming_labels"][0]
    information = path_information(
        outgoing,
        sample["cues"],
        incoming,
        sample["labels"],
        branches=spec.branches,
    )
    prediction = heldout_local_route_accuracy(
        outgoing,
        sample["cues"],
        incoming,
        sample["labels"],
        branches=spec.branches,
    )
    return information, prediction


def test_whole_path_entropy_separates_random_residual() -> None:
    guided, _ = _metrics("cue_guided")
    random, _ = _metrics("random_branch")
    assert guided["path_entropy_given_cue"] == 0.0
    assert random["path_entropy_given_cue"] > 0.80


def test_local_tables_generalize_deterministic_composition_only() -> None:
    _, guided = _metrics("cue_guided")
    _, passthrough = _metrics("pass_through")
    _, random = _metrics("random_branch")
    assert guided["heldout_exact_path_accuracy"] == 1.0
    assert passthrough["heldout_exact_path_accuracy"] == 1.0
    assert random["heldout_exact_path_accuracy"] < 0.15


def test_exact_leaf_fraction_is_bounded() -> None:
    for policy in ("cue_guided", "pass_through", "random_branch"):
        information, _ = _metrics(policy)
        assert 0.0 <= information["effective_leaf_fraction_exact"] <= 1.0
        assert (
            0.0
            <= information["cue_conditional_leaf_fraction_exact"]
            <= 1.0
        )


def test_path_mi_permutation_separates_guided_from_random_bias() -> None:
    spec = JunctionFlowSpec()
    corrected = {}
    for policy in ("cue_guided", "random_branch"):
        sample = simulate_junction_world(
            seed=193,
            policy=policy,
            spec=spec,
        )
        branch = _branch_estimates(
            sample["observations"],
            sample["cues"],
            sample["labels"],
            spec=spec,
        )
        corrected[policy] = conditional_path_information_permutation(
            branch["outgoing_labels"][0],
            sample["cues"],
            branch["incoming_labels"][0],
            sample["labels"],
            branches=spec.branches,
            seed=991,
            permutations=49,
        )
    assert corrected["cue_guided"]["path_conditional_mi_bias_adjusted"] > 0.20
    assert abs(
        corrected["random_branch"]["path_conditional_mi_bias_adjusted"]
    ) < 0.05
