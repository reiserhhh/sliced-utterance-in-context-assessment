"""Tests for the V3.2 matched strong-chain counterfactual."""
from __future__ import annotations

import numpy as np

from suica_core.v8_incidence_incremental import IncrementalSpec
from suica_core.v8_incidence_strong_chain import (
    STRONG_CHAIN_BLOCKS,
    analyze_strong_chain_pair,
    condition_aligned_pair_matrix,
    simulate_strong_chain_pair,
    strong_chain_block_counts,
)


def _graph_config() -> dict[str, float | int]:
    return {
        "graph_edge_threshold": 0.04,
        "spectral_k_min": 2,
        "spectral_k_max": 8,
        "spectral_min_eigengap": 0.05,
        "spectral_min_silhouette": 0.10,
    }


def test_balanced_triplet_design_matches_author_pairs() -> None:
    author_counts, pair_counts = strong_chain_block_counts()
    assert len(STRONG_CHAIN_BLOCKS) == 10
    assert np.all(author_counts == 5)
    upper = np.triu_indices(6, 1)
    assert np.all(pair_counts[upper] == 2)


def test_strong_chain_matches_opportunity_pair_counts_and_whole_map() -> None:
    spec = IncrementalSpec()
    pair = simulate_strong_chain_pair(seed=131, spec=spec)
    assert pair["oracle_pair_matrix_max_error"] == 0.0
    assert np.all(
        pair["positive_opportunity"].sum(axis=1) == 25
    )
    assert np.array_equal(
        pair["positive_opportunity"].sum(axis=1),
        pair["negative_opportunity"].sum(axis=1),
    )
    assert pair["oracle_distance_relative_error"] < 1e-10
    assert pair["fitted_distance_relative_error"] < 1e-10


def test_observed_aggregate_pair_graphs_are_matched() -> None:
    spec = IncrementalSpec()
    pair = simulate_strong_chain_pair(seed=137, spec=spec)
    positive = condition_aligned_pair_matrix(
        pair["positive_views"],
        spec=spec,
    )
    chain = condition_aligned_pair_matrix(
        pair["negative_views"],
        spec=spec,
    )
    assert np.mean(np.abs(positive - chain)) <= 0.02
    upper = np.triu_indices(spec.authors, 1)
    assert np.corrcoef(positive[upper], chain[upper])[0, 1] >= 0.95


def test_hypergraph_refuses_strong_chain_while_graphs_merge() -> None:
    spec = IncrementalSpec()
    pair = simulate_strong_chain_pair(seed=139, spec=spec)
    result = analyze_strong_chain_pair(
        pair,
        spec=spec,
        candidate_closure_cap=5_000,
        graph_config=_graph_config(),
        seed=139,
    )
    assert result["status"] == "ESTIMATE_READY"
    assert result["positive"]["group_claim"]
    assert result["positive"]["group_f1"] == 1.0
    assert not result["chain"]["group_claim"]
    assert result["chain"]["status"] == "REFUSE_CORE_AMBIGUITY"
    assert result["chain_all_triplets_pass"]
    for method in ("single_link", "complete_link", "spectral"):
        assert result["positive_graphs"][method]["six_group_claim"]
        assert result["chain_graphs"][method]["six_group_claim"]
