"""Tests for the V8 nested information-budget experiment."""
from __future__ import annotations

import numpy as np

from suica_core.v8_nested_information_budget import (
    NestedInformationBudgetSpec,
    nested_event_indices,
    relation_discrepancy,
    simultaneous_intervals,
    summarize_nested_budget_panel,
)


def test_nested_schedule_preserves_both_replicate_streams() -> None:
    indices = nested_event_indices(
        event_count=12,
        budgets=(4, 6, 8, 10, 12),
        pair_reveal_order=(0, 5, 2, 3, 1, 4),
    )
    assert indices[4] == (0, 1, 10, 11)
    assert set(indices[8]).issubset(indices[12])
    for low, high in ((4, 6), (6, 8), (8, 10), (10, 12)):
        assert set(indices[low][0::2]).issubset(indices[high][0::2])
        assert set(indices[low][1::2]).issubset(indices[high][1::2])


def test_relation_discrepancy_is_zero_for_identical_geometry() -> None:
    matrix = np.random.default_rng(3).normal(size=(20, 20))
    assert np.isclose(relation_discrepancy(matrix, matrix), 0.0)


def test_simultaneous_intervals_are_wider_than_pointwise() -> None:
    rng = np.random.default_rng(5)
    points = {"a": 0.2, "b": 0.3}
    samples = {
        "a": rng.normal(0.2, 0.04, size=499),
        "b": rng.normal(0.3, 0.05, size=499),
    }
    intervals = simultaneous_intervals(points, samples)
    pointwise_width = (
        intervals["pointwise_ucb"] - intervals["pointwise_lcb"]
    )
    simultaneous_width = (
        intervals["simultaneous_ucb"] - intervals["simultaneous_lcb"]
    )
    assert simultaneous_width.ge(pointwise_width).all()


def _matrices(signal: float, *, seed: int) -> tuple[np.ndarray, ...]:
    rng = np.random.default_rng(seed)
    latent = rng.normal(size=(48, 8))
    second = latent + rng.normal(scale=signal, size=latent.shape)
    other = latent @ np.linalg.qr(rng.normal(size=(8, 8)))[0]

    def kernel(values: np.ndarray) -> np.ndarray:
        centered = values - values.mean(axis=0)
        result = centered @ centered.T
        np.fill_diagonal(result, 0.0)
        return result

    return (
        kernel(latent),
        kernel(second),
        kernel(other),
        kernel(other + rng.normal(scale=signal, size=other.shape)),
    )


def test_summary_detects_improvement_under_nested_precision_gain() -> None:
    panels = {
        4: _matrices(1.4, seed=7),
        8: _matrices(0.9, seed=7),
        12: _matrices(0.15, seed=7),
    }
    spec = NestedInformationBudgetSpec(
        budgets=(4, 8, 12),
        null_draws=99,
        bootstrap_draws=99,
        seed=11,
    )
    result = summarize_nested_budget_panel(
        panels,
        split="D1",
        arm="fixed",
        spec=spec,
        seed=13,
    )
    assert all(value > 0 for value in result["w_points"].values())
    assert all(value > 0 for value in result["q_points"].values())
