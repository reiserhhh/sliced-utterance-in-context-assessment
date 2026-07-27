"""Tests for V3.3 condition-aware pairwise fairness baselines."""
from __future__ import annotations

from suica_core.v8_incidence_graph_fairness import (
    analyze_condition_pair_baselines,
)
from suica_core.v8_incidence_incremental import IncrementalSpec
from suica_core.v8_incidence_strong_chain import simulate_strong_chain_pair


def test_condition_aware_pairwise_methods_resolve_strong_chain() -> None:
    spec = IncrementalSpec()
    pair = simulate_strong_chain_pair(seed=163, spec=spec)
    positive = analyze_condition_pair_baselines(
        pair["positive_views"],
        pair["labels"],
        spec=spec,
        node_cap=25_000,
        candidate_cap=5_000,
    )
    chain = analyze_condition_pair_baselines(
        pair["negative_views"],
        pair["labels"],
        spec=spec,
        node_cap=25_000,
        candidate_cap=5_000,
    )
    for method in positive:
        assert positive[method]["group_claim"]
        assert positive[method]["group_f1"] == 1.0
        assert not chain[method]["group_claim"]
    assert chain["persistent_maximal_clique"]["refused"]
    assert chain["condition_complete_link"]["refused"]
    assert (
        chain["persistent_maximal_clique"]["maximum_passing_size"]
        == 3
    )
