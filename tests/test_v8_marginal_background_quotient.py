"""Tests for the V8 conditional marginal-background quotient."""
from __future__ import annotations

import numpy as np

from suica_core.v8_marginal_background_quotient import (
    centered_bootstrap_lower_bound,
    marginal_feature_blocks_batch,
    quotient_statistics,
    tensor_feature_blocks,
)
from suica_core.v8_realtext_relation_field import (
    family_features,
    frozen_random_directions,
)


def test_vectorized_m_blocks_match_scalar_family_features() -> None:
    rng = np.random.default_rng(4)
    paths = rng.normal(size=(5, 4, 16))
    directions = frozen_random_directions(
        event_dimensions=16,
        count=4,
        seed=7,
    )
    blocks = marginal_feature_blocks_batch(
        paths,
        marginal_directions=directions[0],
    )
    vectorized = np.concatenate(
        [
            blocks["mean"],
            blocks["variance"],
            blocks["rff"],
            blocks["quantiles"],
        ],
        axis=1,
    )
    scalar = np.stack(
        [
            family_features(
                path,
                marginal_directions=directions[0],
                transition_directions=directions[1],
                current_directions=directions[2],
            )["M"]
            for path in paths
        ]
    )
    assert np.allclose(vectorized, scalar, atol=1e-10)


def test_tensor_blocks_preserve_even_odd_technical_replicates() -> None:
    rng = np.random.default_rng(8)
    vectors = rng.normal(size=(3, 8, 12))
    directions = frozen_random_directions(
        event_dimensions=12,
        count=3,
        seed=11,
    )
    blocks = tensor_feature_blocks(
        vectors,
        marginal_directions=directions[0],
    )
    expected = marginal_feature_blocks_batch(
        vectors[:, 0::2],
        marginal_directions=directions[0],
    )
    for block in expected:
        assert np.allclose(blocks[block][:, 0], expected[block])


def test_quotient_statistics_detect_replicated_author_structure() -> None:
    rng = np.random.default_rng(12)
    author = rng.normal(size=(80, 14))
    values = np.stack(
        [
            author + rng.normal(scale=0.15, size=author.shape),
            author + rng.normal(scale=0.15, size=author.shape),
        ],
        axis=1,
    )
    linked = quotient_statistics(values)
    shuffled_values = values.copy()
    shuffled_values[:, 1] = shuffled_values[rng.permutation(len(values)), 1]
    shuffled = quotient_statistics(shuffled_values)
    assert linked["frobenius"] > shuffled["frobenius"]
    assert linked["link"] > shuffled["link"]
    assert linked["same_author_auc"] > 0.9


def test_link_is_normalized_cross_covariance_trace() -> None:
    rng = np.random.default_rng(13)
    values = rng.normal(size=(40, 2, 9))
    result = quotient_statistics(values, compute_auc=False)
    first = values[:, 0] - values[:, 0].mean(axis=0)
    second = values[:, 1] - values[:, 1].mean(axis=0)
    cross = first.T @ second / len(values)
    denominator = np.sqrt(
        np.mean(np.sum(first**2, axis=1))
        * np.mean(np.sum(second**2, axis=1))
    )
    expected = (
        len(values)
        / (len(values) - 1)
        * np.trace(cross)
        / denominator
    )
    assert np.isclose(result["link"], expected)


def test_centered_bootstrap_lower_bound_uses_contrast_spread() -> None:
    observed = 0.2
    draws = np.asarray([-0.1, 0.0, 0.1, 0.2, 0.3])
    lower = centered_bootstrap_lower_bound(observed, draws)
    assert lower < observed
    assert np.isclose(lower, observed + np.quantile(draws - draws.mean(), 0.05))
