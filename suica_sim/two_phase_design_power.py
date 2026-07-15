"""Synthetic design calibration for the V6 two-phase collection architecture.

This module does not calculate a human-study sample size.  It calibrates, inside
the registered endogenous-selection generator, the distinct information budgets
for two estimands:

* a free-phase selection profile over conditions; and
* a balanced fixed-phase author-by-condition response contrast.

The calibration deliberately keeps free choice and fixed assignment separate.
It therefore cannot be read as a generic recommendation to condition-centre
text, nor as evidence for a psychological construct.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np

from suica_sim.endogenous_selection import (
    evaluate_endogenous_selection_world,
    generate_endogenous_selection_world,
)


def _validate_positive_grid(name: str, values: Iterable[int], *, minimum: int) -> tuple[int, ...]:
    """Return a sorted, unique positive integer grid or raise a clear error."""
    parsed = tuple(sorted({int(value) for value in values}))
    if not parsed or parsed[0] < minimum:
        raise ValueError(f"{name} must contain integers >= {minimum}")
    return parsed


def _summary(rows: list[dict[str, float]], metrics: tuple[str, ...]) -> dict[str, dict[str, float]]:
    """Summarize simulation rows with central 95% simulation intervals."""
    return {
        metric: {
            "mean": float(np.nanmean([row[metric] for row in rows])),
            "q025": float(np.nanquantile([row[metric] for row in rows], 0.025)),
            "q975": float(np.nanquantile([row[metric] for row in rows], 0.975)),
        }
        for metric in metrics
    }


def _world_metrics(
    seed: int,
    *,
    persons: int,
    features: int,
    conditions: int,
    free_trials: int,
    fixed_repeats: int,
    selection_strength: float,
    condition_scale: float,
    noise_scale: float,
) -> dict[str, float]:
    """Generate one planted world and return author-disjoint estimator metrics."""
    world = generate_endogenous_selection_world(
        seed,
        persons=persons,
        features=features,
        conditions=conditions,
        free_trials=free_trials,
        fixed_repeats=fixed_repeats,
        selection_strength=selection_strength,
        condition_scale=condition_scale,
        noise_scale=noise_scale,
    )
    return evaluate_endogenous_selection_world(world)


def _fixed_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Calibrate fixed-condition response recovery over breadth and repeats."""
    output: list[dict[str, Any]] = []
    for conditions in _validate_positive_grid("conditions_grid", config["conditions_grid"], minimum=2):
        for repeats in _validate_positive_grid("fixed_repeats_grid", config["fixed_repeats_grid"], minimum=1):
            rows = [
                _world_metrics(
                    config["seed"] + 10_000_000 + conditions * 100_000 + repeats * 1_000 + replicate,
                    persons=config["persons"],
                    features=config["features"],
                    conditions=conditions,
                    free_trials=config["reference_free_trials"],
                    fixed_repeats=repeats,
                    selection_strength=config["selection_strength"],
                    condition_scale=config["condition_scale"],
                    noise_scale=config["noise_scale"],
                )
                for replicate in range(config["repetitions"])
            ]
            summary = _summary(
                rows,
                (
                    "fixed_condition_level_recovery_r",
                    "fixed_response_recovery_r",
                    "fixed_response_support",
                ),
            )
            qualified = (
                summary["fixed_condition_level_recovery_r"]["q025"]
                >= config["minimum_fixed_level_recovery_r"]
                and summary["fixed_response_recovery_r"]["q025"]
                >= config["minimum_fixed_response_recovery_r"]
                and summary["fixed_response_support"]["q025"] >= 0.99
            )
            output.append(
                {
                    "conditions": conditions,
                    "fixed_repeats_per_condition": repeats,
                    "fixed_total_observations": conditions * repeats,
                    "summary": summary,
                    "qualified": qualified,
                }
            )
    return output


def _free_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Calibrate free selection-profile recovery as a function of free exposure."""
    conditions = int(config["reference_conditions"])
    output: list[dict[str, Any]] = []
    for trials in _validate_positive_grid("free_trials_grid", config["free_trials_grid"], minimum=4):
        rows = [
            _world_metrics(
                config["seed"] + 20_000_000 + trials * 10_000 + replicate,
                persons=config["persons"],
                features=config["features"],
                conditions=conditions,
                free_trials=trials,
                fixed_repeats=config["reference_fixed_repeats"],
                selection_strength=config["selection_strength"],
                condition_scale=config["condition_scale"],
                noise_scale=config["noise_scale"],
            )
            for replicate in range(config["repetitions"])
        ]
        summary = _summary(
            rows,
            (
                "selection_profile_truth_r",
                "selection_holdout_logscore_gain",
                "free_response_support",
            ),
        )
        qualified = (
            summary["selection_profile_truth_r"]["q025"]
            >= config["minimum_free_selection_profile_r"]
            and summary["selection_holdout_logscore_gain"]["q025"] > 0.0
        )
        output.append(
            {
                "conditions": conditions,
                "free_trials": trials,
                "summary": summary,
                "qualified": qualified,
            }
        )
    return output


def _select_minimum(rows: list[dict[str, Any]], *keys: str) -> dict[str, Any] | None:
    """Select the smallest qualified row, breaking ties deterministically."""
    qualified = [row for row in rows if row["qualified"]]
    return min(qualified, key=lambda row: tuple(row[key] for key in keys)) if qualified else None


def run_two_phase_design_calibration(config: dict[str, Any]) -> dict[str, Any]:
    r"""Run the frozen two-phase information-budget calibration.

    Let \(\pi_u\) be the free choice profile and \(B_u\) the fixed-condition
    response contrast.  The two grids report separate recovery quantities:

    \[
    R_\pi = \operatorname{corr}(\operatorname{vec}\hat\pi_u,
                                  \operatorname{vec}\pi_u),\qquad
    R_B = \operatorname{corr}(\operatorname{vec}\hat B_u,
                               \operatorname{vec}B_u).
    \]

    Qualification is defined entirely in the planted generator by lower 2.5%
    simulation quantiles.  It is not a human study power calculation.
    """
    if int(config["repetitions"]) < 2:
        raise ValueError("repetitions must be at least 2")
    if int(config["reference_conditions"]) < 2:
        raise ValueError("reference_conditions must be at least 2")
    fixed = _fixed_rows(config)
    free = _free_rows(config)
    minimum_fixed = _select_minimum(
        fixed,
        "fixed_total_observations",
        "conditions",
        "fixed_repeats_per_condition",
    )
    preferred_fixed = _select_minimum(
        [
            row
            for row in fixed
            if row["conditions"] >= int(config["minimum_condition_breadth"])
        ],
        "fixed_total_observations",
        "conditions",
        "fixed_repeats_per_condition",
    )
    minimum_free = _select_minimum(free, "free_trials")
    return {
        "profile": config["profile"],
        "config": config,
        "fixed_grid": fixed,
        "free_grid": free,
        "selection": {
            "minimum_numerically_adequate_fixed_design": minimum_fixed,
            "minimum_breadth_qualified_fixed_design": preferred_fixed,
            "minimum_qualified_free_design": minimum_free,
        },
        "gates": {
            "at_least_one_fixed_design_qualified": minimum_fixed is not None,
            "at_least_one_breadth_qualified_fixed_design": preferred_fixed is not None,
            "at_least_one_free_design_qualified": minimum_free is not None,
        },
    }
