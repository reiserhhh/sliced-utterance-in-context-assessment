"""Tests for V3.1 persistent subset and condition alignment."""
from __future__ import annotations

from suica_core.v8_incidence_incremental import (
    IncrementalSpec,
    simulate_counterfactual_pair,
)
from suica_core.v8_incidence_incremental_v31 import (
    analyze_counterfactual_pair_v31,
    condition_aligned_core_scores,
    intersection_closed_candidates,
)


def test_intersection_closure_recovers_hidden_stable_subset() -> None:
    grids = [
        [
            [[(0, 1, 2, 3)]],
            [[]],
        ],
        [
            [[(0, 1, 2, 4)]],
            [[]],
        ],
    ]
    candidates = intersection_closed_candidates(grids, cap=100)
    assert frozenset({0, 1, 2}) in candidates
    scores, _ = condition_aligned_core_scores(
        grids,
        authors=6,
        closure_cap=100,
        threshold=0.04,
    )
    assert scores[frozenset({0, 1, 2})] > 0.0


def test_cross_view_support_must_occur_at_same_condition() -> None:
    shifted = [
        [
            [[(0, 1, 2)]],
            [[]],
        ],
        [
            [[]],
            [[(0, 1, 2)]],
        ],
    ]
    scores, per_view = condition_aligned_core_scores(
        shifted,
        authors=6,
        closure_cap=100,
        threshold=0.04,
    )
    core = frozenset({0, 1, 2})
    assert per_view[0][core] > 0.0
    assert per_view[1][core] > 0.0
    assert scores[core] == 0.0


def test_v31_retains_incremental_recovery_and_rejects_chain() -> None:
    spec = IncrementalSpec()
    pair = simulate_counterfactual_pair(
        seed=109,
        pair_id="CF2",
        spec=spec,
    )
    result = analyze_counterfactual_pair_v31(
        pair,
        spec=spec,
        candidate_closure_cap=5_000,
        permutation_seed=113,
    )
    assert result["positive"]["group_claim"]
    assert result["positive"]["incidence_auc"] == 1.0
    assert result["positive"]["cross_view_core_jaccard"] == 1.0
    assert not result["negative"]["group_claim"]
    assert not result["chaining_error"]
