"""Tests for V8 incremental incidence geometry."""
from __future__ import annotations

import numpy as np

from suica_core.v8_incidence_incremental import (
    IncrementalSpec,
    analyze_counterfactual_pair,
    exact_maximal_hyperedges,
    exhaustive_maximal_hyperedges,
    pairwise_whole_map_distances,
    simulate_counterfactual_pair,
)
from suica_core.v8_incidence_multiplicity import verified_hyperedges


def test_gram_reservoir_matches_all_whole_map_distances() -> None:
    spec = IncrementalSpec()
    pair = simulate_counterfactual_pair(
        seed=71,
        pair_id="CF1",
        spec=spec,
    )
    assert pair["oracle_distance_relative_error"] < 1e-10
    assert pair["fitted_distance_relative_error"] < 1e-10
    assert pair["orthogonal_mapping_error"] < 1e-10
    positive = pairwise_whole_map_distances(
        pair["positive_views"].mean(axis=0)
    )
    negative = pairwise_whole_map_distances(
        pair["negative_views"].mean(axis=0)
    )
    assert np.allclose(positive, negative, atol=1e-10)


def test_exact_enumerator_matches_exhaustive_random_small_sets() -> None:
    rng = np.random.default_rng(73)
    for authors in (8, 10, 12):
        for radius in (0.45, 0.75, 1.10):
            points = rng.normal(size=(authors, 2))
            exact, _ = exact_maximal_hyperedges(
                points,
                radius=radius,
                node_cap=100_000,
            )
            exhaustive = exhaustive_maximal_hyperedges(
                points,
                radius=radius,
            )
            assert exact == exhaustive


def test_exact_enumerator_matches_exhaustive_in_three_dimensions() -> None:
    rng = np.random.default_rng(74)
    points = rng.normal(size=(9, 3))
    for radius in (0.75, 1.15):
        exact, _ = exact_maximal_hyperedges(
            points,
            radius=radius,
            node_cap=100_000,
        )
        exhaustive = exhaustive_maximal_hyperedges(
            points,
            radius=radius,
        )
        assert exact == exhaustive


def test_exact_enumerator_recovers_overlapping_hyperedges_missed_by_partition() -> None:
    points = np.asarray([
        [0.0, 0.0],
        [0.9, 0.0],
        [1.8, 0.0],
        [2.7, 0.0],
    ])
    exact, _ = exact_maximal_hyperedges(
        points,
        radius=1.0,
        node_cap=10_000,
    )
    approximate = verified_hyperedges(points, epsilon=1.0)
    assert set(exact) == {(0, 1, 2), (1, 2, 3)}
    assert set(exact) != set(approximate)


def test_sync_counterfactual_has_incremental_incidence() -> None:
    spec = IncrementalSpec()
    pair = simulate_counterfactual_pair(
        seed=79,
        pair_id="CF1",
        spec=spec,
    )
    result = analyze_counterfactual_pair(
        pair,
        spec=spec,
        permutation_seed=101,
    )
    assert result["positive"]["group_claim"]
    assert result["positive"]["incidence_auc"] >= 0.95
    assert result["positive"]["group_f1"] >= 0.95
    assert not result["negative"]["group_claim"]


def test_chain_counterfactual_is_not_merged_transitively() -> None:
    spec = IncrementalSpec()
    pair = simulate_counterfactual_pair(
        seed=83,
        pair_id="CF2",
        spec=spec,
    )
    result = analyze_counterfactual_pair(
        pair,
        spec=spec,
        permutation_seed=103,
    )
    assert result["positive"]["group_claim"]
    assert not result["negative"]["group_claim"]
    assert not result["chaining_error"]


def test_rotating_multiplicity_is_not_persistent_core() -> None:
    spec = IncrementalSpec()
    pair = simulate_counterfactual_pair(
        seed=89,
        pair_id="CF3",
        spec=spec,
    )
    result = analyze_counterfactual_pair(
        pair,
        spec=spec,
        permutation_seed=107,
    )
    assert result["positive"]["group_claim"]
    assert not result["negative"]["group_claim"]
    assert result["negative"]["incidence_auc"] <= 0.60
