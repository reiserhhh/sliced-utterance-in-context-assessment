"""Tests for the event-set composition knockout."""
from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v8_event_set_composition_knockout import (
    EventTensor,
    permuted_k_features_batch,
    pseudo_set_reallocation,
)
from suica_core.v8_order_statistic_null import PERMUTATIONS_4
from suica_core.v8_realtext_relation_field import (
    family_features,
    frozen_random_directions,
)


def test_vectorized_permutation_features_match_scalar_operator() -> None:
    rng = np.random.default_rng(2)
    paths = rng.normal(size=(3, 4, 16))
    directions = frozen_random_directions(
        event_dimensions=16,
        count=4,
        seed=9,
    )
    batch = permuted_k_features_batch(paths, directions=directions)
    scalar = np.stack(
        [
            np.stack(
                [
                    family_features(
                        path[order],
                        marginal_directions=directions[0],
                        transition_directions=directions[1],
                        current_directions=directions[2],
                    )["K"]
                    for order in PERMUTATIONS_4
                ]
            )
            for path in paths
        ]
    )
    scalar -= scalar.mean(axis=1, keepdims=True)
    assert np.allclose(batch, scalar, atol=1e-10)


def test_pseudo_reallocation_preserves_slot_marginals_without_self_donors() -> None:
    authors = 12
    vectors = np.arange(authors * 8 * 3).reshape(authors, 8, 3).astype(float)
    tensor = EventTensor(
        metadata=pd.DataFrame(
            {
                "corpus": ["x"] * authors,
                "author_id": [f"u{index}" for index in range(authors)],
                "context": ["c"] * authors,
                "split": ["D0"] * authors,
            }
        ),
        vectors=vectors,
        lengths=np.tile(np.arange(8), (authors, 1))
        + np.arange(authors)[:, None],
    )
    pseudo, diagnostic = pseudo_set_reallocation(
        tensor,
        block_size=6,
        rng=np.random.default_rng(5),
    )
    for order in range(8):
        assert np.array_equal(
            np.sort(pseudo[:, order, 0]),
            np.sort(vectors[:, order, 0]),
        )
    assert diagnostic["same_author"].sum() == 0
