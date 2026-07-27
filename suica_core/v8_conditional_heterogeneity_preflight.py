"""Repeated-outcome primitives for the R2D Gate-0 preflight."""
from __future__ import annotations

from typing import Any

import numpy as np

from suica_core.v8_reference_measure_frontier import (
    _noise,
    additive_residual,
)


def resample_outcome_pair(
    world: dict[str, Any],
    *,
    test_authors: np.ndarray,
    seed: int,
    noise_mode: str,
    opportunity_prefixes: tuple[int, ...],
    primary_opportunities: int,
    panel_noise_amplitude: float,
    technical_noise_amplitude: float,
    student_df: float,
    heteroskedastic_strength: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Draw a fresh panel-2/3 pair while holding latent world and Q fixed."""
    prefixes = tuple(
        prefix
        for prefix in sorted(map(int, opportunity_prefixes))
        if prefix <= int(primary_opportunities)
    )
    if not prefixes or prefixes[-1] != int(primary_opportunities):
        raise ValueError("primary opportunity must be a registered prefix")
    increments = np.diff((0, *prefixes))
    rng = np.random.default_rng(int(seed))
    cell_truth = np.asarray(world["cell_truth"], dtype=float)
    probabilities = np.asarray(world["probabilities"], dtype=float)[2:4]
    author_covariate = np.asarray(world["author_covariate"], dtype=float)
    panels = 2
    authors, conditions, dimensions = cell_truth.shape
    panel_shock = rng.normal(
        scale=float(panel_noise_amplitude),
        size=(panels, authors, conditions, dimensions),
    )
    hetero = 1.0 + float(heteroskedastic_strength) * (
        0.5
        + np.abs(author_covariate[:, None])
        + np.linspace(0.0, 1.0, conditions)[None, :]
    ) / 2.5
    counts = np.zeros((panels, authors, conditions), dtype=int)
    sums = np.zeros(
        (panels, authors, conditions, dimensions),
        dtype=float,
    )
    for increment in increments:
        for panel in range(panels):
            added = rng.multinomial(
                int(increment),
                probabilities[panel],
            )
            technical = _noise(
                rng,
                (authors, conditions, dimensions),
                mode=str(noise_mode),
                student_df=float(student_df),
            )
            noise_scale = (
                float(technical_noise_amplitude)
                * hetero[:, :, None]
                / np.sqrt(2.0)
            )
            noise_sum = (
                np.sqrt(added[:, :, None])
                * noise_scale
                * technical
            )
            sums[panel] += (
                added[:, :, None]
                * (cell_truth + panel_shock[panel])
                + noise_sum
            )
            counts[panel] += added
    means = np.full_like(sums, np.nan)
    valid = counts > 0
    means[valid] = sums[valid] / counts[valid][:, None]
    left, left_mask = additive_residual(
        means[0],
        counts[0],
        np.asarray(test_authors, dtype=int),
    )
    right, right_mask = additive_residual(
        means[1],
        counts[1],
        np.asarray(test_authors, dtype=int),
    )
    return left, right, left_mask, right_mask


def conditional_variance(
    success_count: np.ndarray,
    *,
    replicates: int,
) -> float:
    """Estimate within-cell Var(p_i) after removing binomial noise."""
    count = np.asarray(success_count, dtype=float)
    if len(count) < 2 or int(replicates) < 2:
        raise ValueError("variance requires multiple bases and replicates")
    proportion = count / float(replicates)
    observed_variance = float(np.var(proportion, ddof=1))
    binomial_variance = count * (
        float(replicates) - count
    ) / (
        float(replicates) ** 2
        * (float(replicates) - 1.0)
    )
    return observed_variance - float(binomial_variance.mean())


def half_split_probabilities(
    success_a: np.ndarray,
    *,
    half_replicates: int,
) -> np.ndarray:
    """Return the frozen Jeffreys estimate from the A outcome half."""
    return (
        np.asarray(success_a, dtype=float) + 0.5
    ) / (float(half_replicates) + 1.0)
