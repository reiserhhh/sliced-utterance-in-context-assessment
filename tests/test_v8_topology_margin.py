"""Tests for the V8 C2 topology-margin experiment."""
from __future__ import annotations

import numpy as np

from suica_core.v8_topology_margin import (
    TopologySpec,
    apply_stable_projection,
    author_matching_auc,
    classify_topology,
    farthest_point_landmarks,
    fit_stable_projection,
    ordinal_distance_matrix,
    simulate_topology_world,
    topology_features,
)


def test_ordinal_distance_has_common_empirical_cdf() -> None:
    rng = np.random.default_rng(7)
    left = ordinal_distance_matrix(rng.normal(size=(30, 3)))
    right = ordinal_distance_matrix(rng.standard_t(3, size=(30, 3)))
    upper = np.triu_indices(30, 1)
    assert np.allclose(
        np.sort(left[upper]),
        np.sort(right[upper]),
    )
    assert np.allclose(np.diag(left), 0.0)


def test_ordinal_distance_is_permutation_equivariant() -> None:
    rng = np.random.default_rng(9)
    values = rng.normal(size=(25, 4))
    permutation = rng.permutation(len(values))
    original = ordinal_distance_matrix(values)
    permuted = ordinal_distance_matrix(values[permutation])
    assert np.allclose(
        permuted,
        original[np.ix_(permutation, permutation)],
    )


def test_farthest_landmarks_are_unique_and_deterministic() -> None:
    rng = np.random.default_rng(11)
    distance = ordinal_distance_matrix(rng.normal(size=(40, 3)))
    first = farthest_point_landmarks(distance, 16)
    second = farthest_point_landmarks(distance, 16)
    assert len(np.unique(first)) == 16
    assert np.array_equal(first, second)


def test_ring_has_longer_h1_bar_than_gaussian() -> None:
    spec = TopologySpec(
        confirmation_authors=80,
        landmarks=64,
        noise_ratio=0.05,
    )
    ring = simulate_topology_world(
        seed=13,
        world="continuous_ring",
        spec=spec,
    )
    null = simulate_topology_world(
        seed=17,
        world="null_gaussian",
        spec=spec,
    )
    ring_discovery = ring["splits"] == "discovery"
    null_discovery = null["splits"] == "discovery"
    ring_projected = apply_stable_projection(
        ring["views"],
        fit_stable_projection(ring["views"], ring_discovery),
    )
    null_projected = apply_stable_projection(
        null["views"],
        fit_stable_projection(null["views"], null_discovery),
    )
    ring_values = ring_projected[
        ring["splits"] == "confirmation", 0, 0
    ]
    null_values = null_projected[
        null["splits"] == "confirmation", 0, 0
    ]
    ring_feature = topology_features(
        ring_values,
        neighbors=12,
        landmarks=64,
    )
    null_feature = topology_features(
        null_values,
        neighbors=12,
        landmarks=64,
    )
    assert ring_feature["h1_max_lifetime"] > null_feature["h1_max_lifetime"]


def test_half_shuffle_breaks_author_matching() -> None:
    spec = TopologySpec(
        confirmation_authors=80,
        noise_ratio=0.1,
    )
    stable = simulate_topology_world(
        seed=19,
        world="separated_mixture",
        spec=spec,
    )
    shuffled = simulate_topology_world(
        seed=19,
        world="half_shuffled",
        spec=spec,
    )
    mask = stable["splits"] == "confirmation"
    stable_auc = author_matching_auc(
        stable["views"][mask, 0, 0],
        stable["views"][mask, 1, 0],
    )
    shuffled_auc = author_matching_auc(
        shuffled["views"][mask, 0, 0],
        shuffled["views"][mask, 1, 0],
    )
    assert stable_auc > 0.75
    assert shuffled_auc < 0.6


def _classification_fixture() -> tuple[dict[str, float], dict[str, float]]:
    features = {
        "h0_bottleneck": 0.1,
        "h1_bottleneck": 0.1,
        "neighborhood_jaccard": 0.7,
        "author_matching_auc": 0.51,
        "h0_k_gap": 0.0,
        "laplacian_k4_eigengap": 0.0,
        "minimum_conductance": 0.5,
        "density_tree_k4_longest": 0.0,
        "k4_silhouette": 0.2,
        "hdbscan_k4_supported": 0.0,
        "h1_max_lifetime": 0.2,
        "cycle_eigenpair_similarity": 0.0,
        "local_linearity": 0.8,
    }
    thresholds = {
        "maximum_h0_bottleneck": 0.5,
        "maximum_h1_bottleneck": 0.5,
        "minimum_neighborhood_jaccard": 0.4,
        "minimum_author_matching_auc": 0.9,
        "h0_k_gap": 1.0,
        "laplacian_k4_eigengap": 1.0,
        "maximum_conductance": 0.0,
        "density_tree_k4_longest": 10.0,
        "k4_silhouette": 0.9,
        "curve_h1_ceiling": 0.1,
        "ring_h1_floor": 0.3,
        "h1_max_lifetime": 0.3,
        "cycle_eigenpair_similarity": 0.9,
        "local_linearity": 0.6,
    }
    return features, thresholds


def test_h1_open_set_gray_zone_refuses() -> None:
    features, thresholds = _classification_fixture()
    decision = classify_topology(
        features,
        thresholds,
        matching_pass=True,
        bridge_count=-1,
    )
    assert decision["predicted_class"] == "TOPOLOGY_NOT_IDENTIFIABLE"
    assert decision["h1_open_set_region"] == "GRAY_REFUSAL"


def test_population_topology_does_not_require_high_author_auc() -> None:
    features, thresholds = _classification_fixture()
    features["h1_max_lifetime"] = 0.4
    decision = classify_topology(
        features,
        thresholds,
        matching_pass=True,
        bridge_count=-1,
    )
    assert decision["predicted_class"] == "CONTINUOUS_RING"
    assert features["author_matching_auc"] < thresholds[
        "minimum_author_matching_auc"
    ]
