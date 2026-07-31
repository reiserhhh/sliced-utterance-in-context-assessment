"""Tests for the post-hoc C3.3 mechanism decomposition."""
from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.analyze_suica_m4_c33_mechanism import (
    _cluster_interval,
    _paired_repetition_values,
)


def test_paired_repetition_values_preserve_world_pairing() -> None:
    rows = []
    for repetition in range(3):
        for world_offset, world in enumerate(("a", "b")):
            for k, intervention, value in (
                (1, "passive", 0.2 + world_offset),
                (8, "excitation", 0.5 + world_offset + repetition),
            ):
                rows.append(
                    {
                        "repetition": repetition,
                        "world": world,
                        "k": k,
                        "intervention": intervention,
                        "geometry": value,
                    }
                )
    values = _paired_repetition_values(
        pd.DataFrame(rows),
        "geometry",
        high=(8, "excitation"),
        low=(1, "passive"),
    )
    assert np.allclose(values, [0.3, 1.3, 2.3])


def test_cluster_interval_is_deterministic_and_contains_mean() -> None:
    values = np.array([0.1, 0.2, 0.3, 0.4])
    first = _cluster_interval(values, seed=17, repetitions=2_000)
    second = _cluster_interval(values, seed=17, repetitions=2_000)
    assert first == second
    assert first[0] < values.mean() < first[1]
