"""Tests for the K-family within-replicate order knockout."""
from __future__ import annotations

from collections import Counter

import pandas as pd

from suica_core.v8_orientation_order_knockout import shuffle_within_replicate


def test_shuffle_preserves_each_replicate_multiset() -> None:
    events = pd.DataFrame(
        {
            "author_id": ["u"] * 8,
            "context": ["c"] * 8,
            "order": list(range(8)),
            "text": [f"t{index}" for index in range(8)],
        }
    )
    shuffled = shuffle_within_replicate(events, seed=7, corpus="test")
    for offset in (0, 1):
        original = events.sort_values("order").iloc[offset::2]["text"]
        candidate = shuffled.sort_values("order").iloc[offset::2]["text"]
        assert Counter(original) == Counter(candidate)


def test_shuffle_is_deterministic() -> None:
    events = pd.DataFrame(
        {
            "author_id": ["u"] * 8,
            "context": ["c"] * 8,
            "order": list(range(8)),
            "text": [f"t{index}" for index in range(8)],
        }
    )
    first = shuffle_within_replicate(events, seed=7, corpus="test")
    second = shuffle_within_replicate(events, seed=7, corpus="test")
    assert first.equals(second)
