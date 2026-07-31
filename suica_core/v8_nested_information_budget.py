"""Paired inference for nested text-information budgets.

The module operates on already-built author relation matrices.  Every budget
must contain the same authors in the same order, and lower-budget event sets
must be literal subsets of the higher-budget event sets.  Synchronized
permutations and bootstraps preserve that pairing across the full budget
curve.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
import pandas as pd

from suica_core.v8_context_geometry_transport import (
    COMPONENTS,
    _observed_components,
    _recenter_sample,
)
from suica_core.v8_residual_geometry_correspondence import _alignment


WITHIN_COMPONENTS = ("within_a", "within_b")


@dataclass(frozen=True)
class NestedInformationBudgetSpec:
    """Frozen nested-budget design and inference settings."""

    budgets: tuple[int, ...] = (4, 6, 8, 10, 12)
    primary_low_budget: int = 8
    primary_high_budget: int = 12
    null_draws: int = 1999
    bootstrap_draws: int = 1999
    rbf_scale: float = 0.5
    material_delta_reference: float = 0.03
    seed: int = 20260831

    def __post_init__(self) -> None:
        budgets = tuple(map(int, self.budgets))
        if tuple(sorted(set(budgets))) != budgets:
            raise ValueError("budgets must be unique and strictly increasing.")
        if any(budget < 4 or budget % 2 for budget in budgets):
            raise ValueError("Every budget must be an even integer >= 4.")
        if self.primary_low_budget not in budgets:
            raise ValueError("primary_low_budget must occur in budgets.")
        if self.primary_high_budget not in budgets:
            raise ValueError("primary_high_budget must occur in budgets.")
        if self.primary_low_budget >= self.primary_high_budget:
            raise ValueError("Primary low budget must be smaller than high.")
        if min(self.null_draws, self.bootstrap_draws) < 99:
            raise ValueError("Inference budgets must be at least 99.")
        if self.rbf_scale <= 0:
            raise ValueError("rbf_scale must be positive.")
        if self.material_delta_reference < 0:
            raise ValueError("material_delta_reference cannot be negative.")


def nested_event_indices(
    *,
    event_count: int,
    budgets: tuple[int, ...],
    pair_reveal_order: tuple[int, ...],
) -> dict[int, tuple[int, ...]]:
    """Return parity-preserving nested event indices for each total budget.

    Events are treated as adjacent pairs.  Adding one pair adds one source
    event to each alternating technical replicate, so both replicate streams
    remain literal subsets of their higher-budget versions.
    """
    if event_count < 4 or event_count % 2:
        raise ValueError("event_count must be an even integer >= 4.")
    pairs = event_count // 2
    if tuple(sorted(pair_reveal_order)) != tuple(range(pairs)):
        raise ValueError(
            "pair_reveal_order must be a permutation of every event pair."
        )
    result: dict[int, tuple[int, ...]] = {}
    for budget in budgets:
        if budget > event_count:
            raise ValueError("A budget cannot exceed event_count.")
        selected_pairs = pair_reveal_order[: budget // 2]
        indices = sorted(
            index
            for pair in selected_pairs
            for index in (2 * pair, 2 * pair + 1)
        )
        result[int(budget)] = tuple(indices)
    ordered = sorted(result)
    for low, high in zip(ordered[:-1], ordered[1:], strict=True):
        if not set(result[low]).issubset(result[high]):
            raise RuntimeError("Generated event budgets are not nested.")
        for parity in (0, 1):
            low_stream = set(result[low][parity::2])
            high_stream = set(result[high][parity::2])
            if not low_stream.issubset(high_stream):
                raise RuntimeError(
                    "Technical-replicate event streams are not nested."
                )
    return result


def relation_discrepancy(left: np.ndarray, right: np.ndarray) -> float:
    """Return normalized squared technical-replicate disagreement."""
    first = np.asarray(left, dtype=float)
    second = np.asarray(right, dtype=float)
    denominator = float(
        np.linalg.norm(first, ord="fro") ** 2
        + np.linalg.norm(second, ord="fro") ** 2
    )
    if denominator <= 1e-12:
        return float("nan")
    return float(np.linalg.norm(first - second, ord="fro") ** 2 / denominator)


def discrepancy_components(
    matrices: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> dict[str, float]:
    """Return within-context technical disagreement for A and B."""
    a0, a1, b0, b1 = matrices
    return {
        "within_a": relation_discrepancy(a0, a1),
        "within_b": relation_discrepancy(b0, b1),
    }


def synchronized_null_components(
    matrices_by_budget: Mapping[
        int,
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    ],
    *,
    draws: int,
    rng: np.random.Generator,
) -> dict[int, dict[str, np.ndarray]]:
    """Use the same author permutations at every nested budget."""
    budgets = tuple(sorted(matrices_by_budget))
    if not budgets:
        raise ValueError("At least one budget is required.")
    count = len(matrices_by_budget[budgets[0]][0])
    for budget in budgets:
        matrices = matrices_by_budget[budget]
        if any(matrix.shape != (count, count) for matrix in matrices):
            raise ValueError("All budgets must contain the same authors.")
    result = {
        budget: {
            component: np.empty(draws, dtype=float)
            for component in COMPONENTS
        }
        for budget in budgets
    }
    for draw in range(draws):
        order_a = rng.permutation(count)
        order_b = rng.permutation(count)
        order_cross = rng.permutation(count)
        for budget in budgets:
            a0, a1, b0, b1 = matrices_by_budget[budget]
            values = {
                "within_a": _alignment(
                    a0,
                    a1[np.ix_(order_a, order_a)],
                ),
                "within_b": _alignment(
                    b0,
                    b1[np.ix_(order_b, order_b)],
                ),
                "cross": 0.5
                * (
                    _alignment(
                        a0,
                        b1[np.ix_(order_cross, order_cross)],
                    )
                    + _alignment(
                        a1,
                        b0[np.ix_(order_cross, order_cross)],
                    )
                ),
            }
            for component, value in values.items():
                result[budget][component][draw] = value
    return result


def synchronized_bootstrap_components(
    matrices_by_budget: Mapping[
        int,
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    ],
    *,
    draws: int,
    rng: np.random.Generator,
) -> tuple[
    dict[int, dict[str, np.ndarray]],
    dict[int, dict[str, np.ndarray]],
]:
    """Bootstrap the same authors at every budget and return W and Q draws."""
    budgets = tuple(sorted(matrices_by_budget))
    if not budgets:
        raise ValueError("At least one budget is required.")
    count = len(matrices_by_budget[budgets[0]][0])
    observed = {
        budget: {
            component: np.empty(draws, dtype=float)
            for component in COMPONENTS
        }
        for budget in budgets
    }
    discrepancy = {
        budget: {
            component: np.empty(draws, dtype=float)
            for component in WITHIN_COMPONENTS
        }
        for budget in budgets
    }
    for draw in range(draws):
        indices = rng.integers(0, count, size=count)
        for budget in budgets:
            sampled = tuple(
                _recenter_sample(matrix, indices)
                for matrix in matrices_by_budget[budget]
            )
            w_values = _observed_components(*sampled)
            q_values = discrepancy_components(sampled)
            for component, value in w_values.items():
                observed[budget][component][draw] = value
            for component, value in q_values.items():
                discrepancy[budget][component][draw] = value
    return observed, discrepancy


def centered_interval(
    point: float,
    samples: np.ndarray,
    *,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Return a centered percentile interval around a point estimate."""
    values = np.asarray(samples, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < 20:
        return float("nan"), float("nan")
    centered = values - values.mean()
    return (
        float(point + np.quantile(centered, alpha / 2)),
        float(point + np.quantile(centered, 1 - alpha / 2)),
    )


def simultaneous_intervals(
    points: Mapping[str, float],
    samples: Mapping[str, np.ndarray],
    *,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Return studentized simultaneous bootstrap bands for one family."""
    names = tuple(points)
    if set(names) != set(samples):
        raise ValueError("Point and bootstrap cells must match.")
    centered_rows = []
    standards = {}
    draw_count: int | None = None
    for name in names:
        values = np.asarray(samples[name], dtype=float)
        if draw_count is None:
            draw_count = len(values)
        elif len(values) != draw_count:
            raise ValueError("All bootstrap cells must share draw count.")
        center = values - np.nanmean(values)
        standard = max(float(np.nanstd(center, ddof=1)), 1e-12)
        standards[name] = standard
        centered_rows.append(np.abs(center / standard))
    maximum = np.nanmax(np.vstack(centered_rows), axis=0)
    critical = float(np.nanquantile(maximum, 1 - alpha))
    rows = []
    for name in names:
        point = float(points[name])
        low, high = centered_interval(point, samples[name], alpha=alpha)
        width = critical * standards[name]
        rows.append(
            {
                "cell_id": name,
                "point": point,
                "pointwise_lcb": low,
                "pointwise_ucb": high,
                "simultaneous_lcb": float(point - width),
                "simultaneous_ucb": float(point + width),
                "simultaneous_critical": critical,
            }
        )
    return pd.DataFrame(rows)


def summarize_nested_budget_panel(
    matrices_by_budget: Mapping[
        int,
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
    ],
    *,
    split: str,
    arm: str,
    spec: NestedInformationBudgetSpec,
    seed: int,
) -> dict[str, object]:
    """Summarize one split and estimator arm over the nested budget curve."""
    budgets = tuple(sorted(matrices_by_budget))
    null = synchronized_null_components(
        matrices_by_budget,
        draws=spec.null_draws,
        rng=np.random.default_rng(seed),
    )
    bootstrap_w, bootstrap_q = synchronized_bootstrap_components(
        matrices_by_budget,
        draws=spec.bootstrap_draws,
        rng=np.random.default_rng(seed + 1),
    )
    rows = []
    for budget in budgets:
        observed = _observed_components(*matrices_by_budget[budget])
        discrepancy = discrepancy_components(matrices_by_budget[budget])
        for component in COMPONENTS:
            null_mean = float(np.mean(null[budget][component]))
            excess = float(observed[component] - null_mean)
            samples = bootstrap_w[budget][component] - null_mean
            lower, upper = centered_interval(excess, samples)
            rows.append(
                {
                    "arm": arm,
                    "split": split,
                    "budget": budget,
                    "component": component,
                    "metric": "relation_excess_w",
                    "point": excess,
                    "observed": observed[component],
                    "null_mean": null_mean,
                    "pointwise_lcb": lower,
                    "pointwise_ucb": upper,
                }
            )
        for component in WITHIN_COMPONENTS:
            point = discrepancy[component]
            lower, upper = centered_interval(
                point,
                bootstrap_q[budget][component],
            )
            rows.append(
                {
                    "arm": arm,
                    "split": split,
                    "budget": budget,
                    "component": component,
                    "metric": "technical_disagreement_q",
                    "point": point,
                    "observed": point,
                    "null_mean": float("nan"),
                    "pointwise_lcb": lower,
                    "pointwise_ucb": upper,
                }
            )
    low = spec.primary_low_budget
    high = spec.primary_high_budget
    w_points: dict[str, float] = {}
    w_samples: dict[str, np.ndarray] = {}
    for component in COMPONENTS:
        low_null = float(np.mean(null[low][component]))
        high_null = float(np.mean(null[high][component]))
        name = f"{arm}::{split}::{component}::W::{high}-{low}"
        w_points[name] = float(
            (
                _observed_components(*matrices_by_budget[high])[component]
                - high_null
            )
            - (
                _observed_components(*matrices_by_budget[low])[component]
                - low_null
            )
        )
        w_samples[name] = (
            bootstrap_w[high][component]
            - high_null
            - bootstrap_w[low][component]
            + low_null
        )
    q_points: dict[str, float] = {}
    q_samples: dict[str, np.ndarray] = {}
    low_q = discrepancy_components(matrices_by_budget[low])
    high_q = discrepancy_components(matrices_by_budget[high])
    for component in WITHIN_COMPONENTS:
        name = f"{arm}::{split}::{component}::Q::{low}-{high}"
        q_points[name] = float(low_q[component] - high_q[component])
        q_samples[name] = (
            bootstrap_q[low][component]
            - bootstrap_q[high][component]
        )
    return {
        "curve": pd.DataFrame(rows),
        "w_points": w_points,
        "w_samples": w_samples,
        "q_points": q_points,
        "q_samples": q_samples,
    }
