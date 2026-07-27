"""Tests for the paired V3.7D confirmation design."""
from __future__ import annotations

import numpy as np

from suica_core.v8_dimension_density_budget import (
    DensityWorldSpec,
    random_neighbor_auc,
    simulate_group_free_density_world,
    with_event_budget,
)


def test_nested_rank_worlds_share_non_author_design() -> None:
    common = dict(
        authors=48,
        author_basis_rank=12,
        events_per_context_session=128,
    )
    rank2 = simulate_group_free_density_world(
        seed=73_701,
        spec=DensityWorldSpec(latent_rank=2, **common),
    )
    rank8 = simulate_group_free_density_world(
        seed=73_701,
        spec=DensityWorldSpec(latent_rank=8, **common),
    )
    assert np.array_equal(
        rank2["contexts"]["all"],
        rank8["contexts"]["all"],
    )
    assert not np.array_equal(rank2["probability"], rank8["probability"])


def test_event_budget_reuses_probability_but_changes_trials() -> None:
    latent = simulate_group_free_density_world(
        seed=73_702,
        spec=DensityWorldSpec(
            authors=24,
            latent_rank=4,
            author_basis_rank=12,
            events_per_context_session=128,
        ),
    )
    low = with_event_budget(latent, 64)
    assert low["probability"] is latent["probability"]
    assert np.all(low["trials"] == 4)
    assert np.all(latent["trials"] == 8)


def test_random_neighbor_auc_is_finite_and_nonmutating() -> None:
    rng = np.random.default_rng(73_703)
    left = rng.normal(size=(32, 8))
    right = left + rng.normal(scale=0.2, size=left.shape)
    left_before = left.copy()
    right_before = right.copy()
    auc = random_neighbor_auc(
        left,
        right,
        neighbor_count=8,
        rng=np.random.default_rng(73_704),
    )
    assert 0.0 <= auc <= 1.0
    assert np.array_equal(left, left_before)
    assert np.array_equal(right, right_before)
