"""Tests for the exchangeable V8 background reallocation."""
from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v8_event_set_composition_knockout import EventTensor
from suica_core.v8_exchangeable_background_audit import (
    exchangeable_set_reallocation,
)


def _tensor() -> EventTensor:
    authors = 8
    events = 4
    vectors = np.arange(authors * events * 3, dtype=float).reshape(
        authors,
        events,
        3,
    )
    return EventTensor(
        metadata=pd.DataFrame(
            {
                "author_id": [f"u{index}" for index in range(authors)],
                "context": ["c"] * authors,
                "split": ["D0"] * authors,
            }
        ),
        vectors=vectors,
        lengths=np.tile(np.arange(events), (authors, 1)),
    )


class _IdentityRng:
    def permutation(self, values: np.ndarray) -> np.ndarray:
        return np.asarray(values).copy()


def test_identity_assignment_is_in_randomization_support() -> None:
    tensor = _tensor()
    observed, diagnostics = exchangeable_set_reallocation(
        tensor,
        block_size=8,
        rng=_IdentityRng(),  # type: ignore[arg-type]
    )
    assert np.array_equal(observed, tensor.vectors)
    assert diagnostics["identity_block"].eq(1).all()
    assert diagnostics["fixed_point_fraction"].eq(1.0).all()


def test_uniform_permutation_preserves_slot_marginals_and_allows_fixed_points() -> None:
    tensor = _tensor()
    rng = np.random.default_rng(4)
    fixed_points = 0
    for _ in range(100):
        permuted, diagnostics = exchangeable_set_reallocation(
            tensor,
            block_size=8,
            rng=rng,
        )
        for order in range(tensor.vectors.shape[1]):
            expected = np.sort(tensor.vectors[:, order, 0])
            observed = np.sort(permuted[:, order, 0])
            assert np.array_equal(observed, expected)
        fixed_points += int(diagnostics["same_author"].sum())
    assert fixed_points > 0
