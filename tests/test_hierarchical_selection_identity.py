"""Tests for the M4-T hierarchical selection-identity mechanism."""

from __future__ import annotations

import numpy as np

from suica_core.hierarchical_selection_identity import (
    cross_fitted_hierarchical_identity,
    fit_selection_tree,
    hellinger_rows,
    simulate_hierarchical_choices,
)


def test_tree_increments_telescope_to_leaf_centroid():
    early, _, _ = simulate_hierarchical_choices(
        n_authors=180,
        n_contexts=24,
        depth=3,
        events_per_half=300,
        seed=11,
    )
    transformed = hellinger_rows(early)
    tree = fit_selection_tree(
        transformed,
        max_depth=3,
        min_leaf=15,
        random_state=7,
    )
    for row in transformed[:20]:
        path = tree.route(row)
        reconstructed = tree.nodes[path[0]].centroid + tree.increment_sum(path)
        assert np.allclose(reconstructed, tree.nodes[path[-1]].centroid)

    # Every training assignment must be exactly replayable by the frozen
    # spherical-centroid routing rule used on held-out authors.
    paths = tree.route_many(transformed)
    for node_id, node in tree.nodes.items():
        observed = sum(node_id in path for path in paths)
        assert observed == node.n_train


def test_planted_hierarchy_replays_in_held_out_authors():
    early, late, _ = simulate_hierarchical_choices(
        n_authors=300,
        n_contexts=32,
        depth=3,
        events_per_half=450,
        strength=1.35,
        seed=23,
    )
    result = cross_fitted_hierarchical_identity(
        early,
        late,
        n_splits=3,
        max_depth=3,
        min_leaf=18,
        random_state=31,
        n_permutations=39,
        n_bootstrap=100,
    )
    summary = result["summary"]
    depth_rows = result["metrics_by_depth"]
    assert summary["flat_auc"] > 0.85
    assert summary["hierarchical_path_auc"] > 0.75
    assert depth_rows[0]["gain_mean"] > depth_rows[0]["gain_null_mean"]
    assert depth_rows[0]["branch_excess"] > 0.20
    assert depth_rows[0]["information_excess_bits"] > 0.10
    assert depth_rows[0]["information_permutation_p"] <= 0.05
    assert sum(row["gain_mean"] > 0 for row in depth_rows) >= 2


def test_author_null_does_not_create_branch_identity():
    early, late, _ = simulate_hierarchical_choices(
        n_authors=270,
        n_contexts=30,
        depth=3,
        events_per_half=350,
        seed=47,
        author_null=True,
    )
    result = cross_fitted_hierarchical_identity(
        early,
        late,
        n_splits=3,
        max_depth=3,
        min_leaf=18,
        random_state=53,
        n_permutations=39,
        n_bootstrap=100,
    )
    summary = result["summary"]
    depth_rows = result["metrics_by_depth"]
    assert 0.44 <= summary["flat_auc"] <= 0.56
    assert 0.44 <= summary["hierarchical_path_auc"] <= 0.56
    assert max(abs(row["branch_excess"]) for row in depth_rows) < 0.12
    assert max(abs(row["information_excess_bits"]) for row in depth_rows) < 0.06


def test_hellinger_rows_reject_negative_inputs():
    values = np.array([[0.5, 0.5], [0.2, -0.1]])
    try:
        hellinger_rows(values)
    except ValueError as error:
        assert "non-negative" in str(error)
    else:
        raise AssertionError("negative frequencies must be rejected")
