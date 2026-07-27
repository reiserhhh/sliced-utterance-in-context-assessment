"""Tests for the V3.7A anonymous author-routing operator."""
from __future__ import annotations

import inspect

import numpy as np

from suica_core.v8_author_routing_operator import (
    AuthorRoutingSpec,
    analyze_author_routing_world,
    estimate_packet_profile,
    ilr,
    ilr_basis,
    ilr_inverse,
    pairing_metrics,
    simulate_author_routing_world,
)


CLAIM_THRESHOLDS = {
    "minimum_within_group_auc": 0.65,
    "minimum_multivariate_reliability": 0.60,
    "minimum_log_loss_gain": 0.005,
}


def _spec() -> AuthorRoutingSpec:
    return AuthorRoutingSpec(
        authors=48,
        groups=4,
        discovery_contexts=8,
        confirmation_contexts=6,
        extrapolation_contexts=2,
        events_per_context_session=64,
    )


def test_ilr_round_trip_is_exact_on_simplex() -> None:
    probability = np.asarray([
        [0.10, 0.20, 0.30, 0.40],
        [0.40, 0.30, 0.20, 0.10],
    ])
    basis = ilr_basis(4)
    assert np.allclose(
        ilr_inverse(ilr(probability, basis), basis),
        probability,
    )


def test_estimator_api_has_no_identity_or_group_input() -> None:
    parameters = inspect.signature(estimate_packet_profile).parameters
    assert "author_id" not in parameters
    assert "labels" not in parameters
    assert "groups" not in parameters


def test_stable_author_world_recovers_anonymous_operator() -> None:
    sample = simulate_author_routing_world(
        seed=8_101,
        world="stable_author",
        spec=_spec(),
    )
    result = analyze_author_routing_world(
        sample,
        selected_lambda=30.0,
        selected_rank=6,
        denoiser_seed=8_102,
        claim_thresholds=CLAIM_THRESHOLDS,
    )
    assert result["status"] == "AUTHOR_ROUTING_OPERATOR_EVALUATED"
    assert result["truth_correlation"] > 0.65
    assert result["subspace_score"] > 0.70
    assert result["within_group_auc"] > 0.90
    assert result["log_loss_gain"] > 0.01
    assert result["author_claim"]


def test_group_only_world_does_not_fake_individuality() -> None:
    sample = simulate_author_routing_world(
        seed=8_201,
        world="group_only",
        spec=_spec(),
    )
    result = analyze_author_routing_world(
        sample,
        selected_lambda=30.0,
        selected_rank=6,
        denoiser_seed=8_202,
        claim_thresholds=CLAIM_THRESHOLDS,
    )
    assert result["same_author_auc"] > 0.70
    assert result["within_group_auc"] < 0.60
    assert not result["author_claim"]


def test_opportunity_only_world_does_not_create_author_claim() -> None:
    sample = simulate_author_routing_world(
        seed=8_301,
        world="opportunity_only",
        spec=_spec(),
    )
    result = analyze_author_routing_world(
        sample,
        selected_lambda=30.0,
        selected_rank=6,
        denoiser_seed=8_302,
        claim_thresholds=CLAIM_THRESHOLDS,
    )
    assert not result["author_claim"]
    assert result["within_group_auc"] < 0.60
    assert result["log_loss_gain"] < 0.01


def test_nonoverlap_world_refuses_numeric_score() -> None:
    sample = simulate_author_routing_world(
        seed=8_401,
        world="opportunity_nonoverlap",
        spec=_spec(),
    )
    discovery = np.arange(_spec().discovery_contexts)
    estimate = estimate_packet_profile(sample, discovery)
    assert estimate["status"] == "REFUSE_NONOVERLAP"
    result = analyze_author_routing_world(
        sample,
        selected_lambda=30.0,
        selected_rank=6,
        denoiser_seed=8_402,
        claim_thresholds=CLAIM_THRESHOLDS,
    )
    assert result["status"] == "REFUSE_NONOVERLAP"
    assert not result["numeric_output"]


def test_pairing_scorer_opens_labels_only_after_profiles_exist() -> None:
    left = np.eye(8)
    right = left.copy()
    labels = np.repeat(np.arange(2), 4)
    metrics = pairing_metrics(left, right, labels)
    assert metrics["same_author_auc"] == 1.0
    assert metrics["within_group_auc"] == 1.0
    assert metrics["within_group_top1"] == 1.0


def test_full_rank_information_limit_requires_higher_budget() -> None:
    low = simulate_author_routing_world(
        seed=8_501,
        world="stable_author",
        spec=AuthorRoutingSpec(
            authors=48,
            groups=4,
            discovery_contexts=8,
            confirmation_contexts=6,
            extrapolation_contexts=2,
            author_rank=48,
            events_per_context_session=32,
        ),
    )
    high = simulate_author_routing_world(
        seed=8_501,
        world="stable_author",
        spec=AuthorRoutingSpec(
            authors=48,
            groups=4,
            discovery_contexts=8,
            confirmation_contexts=6,
            extrapolation_contexts=2,
            author_rank=48,
            events_per_context_session=128,
        ),
    )
    low_result = analyze_author_routing_world(
        low,
        selected_lambda=3.0,
        selected_rank=48,
        denoiser_seed=8_502,
        claim_thresholds=CLAIM_THRESHOLDS,
    )
    high_result = analyze_author_routing_world(
        high,
        selected_lambda=3.0,
        selected_rank=48,
        denoiser_seed=8_502,
        claim_thresholds=CLAIM_THRESHOLDS,
    )
    assert low_result["split_session_reliability"] < 0.60
    assert high_result["split_session_reliability"] > 0.60
    assert (
        high_result["split_session_reliability"]
        - low_result["split_session_reliability"]
        > 0.15
    )
