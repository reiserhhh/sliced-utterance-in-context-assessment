"""Tests for V3.7E adaptive rank and fixed reference mechanics."""
from __future__ import annotations

import numpy as np

from suica_core.v8_adaptive_rank_reference import (
    AdaptiveReferenceWorldSpec,
    apply_opportunity_shift,
    apply_population_shift,
    cross_validated_rank_selection,
    population_shift_direction,
    simulate_adaptive_reference_world,
    subset_authors,
    with_event_budget,
)


def test_author_subsets_are_disjoint_views() -> None:
    sample = simulate_adaptive_reference_world(
        seed=83_701,
        spec=AdaptiveReferenceWorldSpec(authors=48),
    )
    left = subset_authors(sample, np.arange(16))
    right = subset_authors(sample, np.arange(16, 32))
    assert left["probability"].shape[0] == 16
    assert right["probability"].shape[0] == 16
    assert not np.shares_memory(
        left["probability"],
        sample["probability"],
    )


def test_opportunity_shift_changes_trials_not_probabilities() -> None:
    sample = simulate_adaptive_reference_world(
        seed=83_702,
        spec=AdaptiveReferenceWorldSpec(authors=24),
    )
    shifted = apply_opportunity_shift(sample, strength=1.5)
    assert shifted["probability"] is sample["probability"]
    assert not np.array_equal(shifted["trials"], sample["trials"])
    assert np.min(shifted["trials"]) >= 1


def test_population_shift_changes_only_selected_authors() -> None:
    sample = simulate_adaptive_reference_world(
        seed=83_703,
        spec=AdaptiveReferenceWorldSpec(authors=24),
    )
    indices = np.arange(12, 24)
    shift = population_shift_direction(sample, rms=0.1)
    shifted = apply_population_shift(
        sample,
        indices=indices,
        shift_ilr=shift,
    )
    assert np.array_equal(
        shifted["probability"][:12],
        sample["probability"][:12],
    )
    assert not np.array_equal(
        shifted["probability"][12:],
        sample["probability"][12:],
    )


def test_one_se_selector_rejects_unpaired_signal() -> None:
    rng = np.random.default_rng(83_704)
    left = rng.normal(size=(96, 24))
    right = left + rng.normal(scale=0.2, size=left.shape)
    selected, table = cross_validated_rank_selection(
        left,
        right,
        candidates=[0, 2, 4, 8, 12, 24],
        folds=4,
        seed=83_705,
    )
    permuted, _ = cross_validated_rank_selection(
        left,
        right[rng.permutation(len(right))],
        candidates=[0, 2, 4, 8, 12, 24],
        folds=4,
        seed=83_705,
    )
    assert selected > 0
    assert permuted <= 2
    assert int(table["selected"].sum()) == 1


def test_rank_worlds_share_basis_and_budget_reuses_probability() -> None:
    common = dict(
        authors=32,
        maximum_latent_rank=16,
        events_per_context_session=128,
    )
    rank4 = simulate_adaptive_reference_world(
        seed=83_706,
        spec=AdaptiveReferenceWorldSpec(latent_rank=4, **common),
    )
    rank12 = simulate_adaptive_reference_world(
        seed=83_706,
        spec=AdaptiveReferenceWorldSpec(latent_rank=12, **common),
    )
    assert np.array_equal(
        rank4["components"]["author_loading"],
        rank12["components"]["author_loading"],
    )
    low = with_event_budget(rank12, 64)
    assert low["probability"] is rank12["probability"]
    assert np.all(low["trials"] == 4)
