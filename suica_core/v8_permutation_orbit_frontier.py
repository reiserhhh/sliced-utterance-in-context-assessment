"""Permutation-orbit primitives for the H4D-R2C mechanism frontier."""
from __future__ import annotations

from typing import Any

import numpy as np

from suica_core.v8_minority_information_frontier import (
    local_double_center,
)
from suica_core.v8_reference_measure_frontier import (
    ReferenceFrontierSpec,
    cross_low_rank_ratio,
    higher_criticism_stat,
)
from suica_core.v8_misspecification_transport import residual_correlation


def residualize_masked(
    values: np.ndarray,
    valid: np.ndarray,
) -> np.ndarray:
    """Apply the frozen author/condition residualization to a fixed mask."""
    result = np.asarray(values, dtype=float).copy()
    mask = np.asarray(valid, dtype=bool)
    result[~mask] = np.nan
    result -= np.nanmean(result, axis=1, keepdims=True)
    result -= np.nanmean(result, axis=0, keepdims=True)
    result[~mask] = 0.0
    return result


def author_contribution_spectrum(
    left: np.ndarray,
    right: np.ndarray,
    left_mask: np.ndarray,
    right_mask: np.ndarray,
) -> dict[str, float]:
    """Return observable Hill support numbers of author contributions."""
    shared = np.asarray(left_mask, dtype=bool) & np.asarray(
        right_mask,
        dtype=bool,
    )
    left_used = residualize_masked(left, shared)
    right_used = residualize_masked(right, shared)
    contribution = np.sum(left_used * right_used, axis=(1, 2))
    mass = np.abs(contribution)
    total = float(mass.sum())
    if total <= 1e-12:
        return {
            "n1": 0.0,
            "n2": 0.0,
            "n_inf": 0.0,
            "sign_coherence": 0.0,
            "positive_fraction": 0.0,
        }
    probability = mass / total
    positive = probability[probability > 0.0]
    n1 = float(np.exp(-np.sum(positive * np.log(positive))))
    n2 = float(1.0 / np.sum(probability**2))
    n_inf = float(1.0 / np.max(probability))
    return {
        "n1": n1,
        "n2": n2,
        "n_inf": n_inf,
        "sign_coherence": float(
            abs(float(contribution.sum())) / total
        ),
        "positive_fraction": float(np.mean(contribution > 0.0)),
    }


def holm_adjust_rows(raw_p: np.ndarray) -> np.ndarray:
    """Vectorized Holm adjustment for rows of three diagnostic p-values."""
    values = np.asarray(raw_p, dtype=float)
    if values.ndim != 2 or values.shape[1] != 3:
        raise ValueError("raw_p must have shape (draws, 3)")
    order = np.argsort(values, axis=1)
    ordered = np.take_along_axis(values, order, axis=1)
    multiplier = np.asarray([3.0, 2.0, 1.0])
    adjusted_ordered = np.maximum.accumulate(
        ordered * multiplier[None, :],
        axis=1,
    )
    adjusted_ordered = np.minimum(adjusted_ordered, 1.0)
    inverse = np.argsort(order, axis=1)
    return np.take_along_axis(adjusted_ordered, inverse, axis=1)


def orbit_rejection_probability(
    left: np.ndarray,
    right: np.ndarray,
    left_mask: np.ndarray,
    right_mask: np.ndarray,
    *,
    seed: int,
    orbit_draws: int,
    detector_permutations: int,
    resamples: int,
    alpha: float,
    rank: int = 3,
) -> dict[str, float]:
    """Estimate finite-draw CRC-or-HC rejection over a wild-sign orbit."""
    if orbit_draws < detector_permutations:
        raise ValueError("orbit_draws must cover detector_permutations")
    shared = np.asarray(left_mask, dtype=bool) & np.asarray(
        right_mask,
        dtype=bool,
    )
    left_used = residualize_masked(left, shared)
    right_used = residualize_masked(right, shared)
    observed = np.asarray([
        residual_correlation(left_used, right_used),
        cross_low_rank_ratio(left_used, right_used, rank=rank),
        higher_criticism_stat(left_used, right_used, shared),
    ])
    root = np.random.SeedSequence(int(seed))
    orbit_stream, resample_stream = root.spawn(2)
    orbit_rng = np.random.default_rng(orbit_stream)
    exceedance = np.empty((int(orbit_draws), 3), dtype=np.uint8)
    for draw in range(int(orbit_draws)):
        signs = orbit_rng.choice(
            [-1.0, 1.0],
            size=(len(right_used), 1, 1),
        )
        wild_right = residualize_masked(right_used * signs, shared)
        null = np.asarray([
            residual_correlation(left_used, wild_right),
            cross_low_rank_ratio(left_used, wild_right, rank=rank),
            higher_criticism_stat(left_used, wild_right, shared),
        ])
        exceedance[draw] = null >= observed

    category = (
        exceedance[:, 0]
        + 2 * exceedance[:, 1]
        + 4 * exceedance[:, 2]
    )
    probability = np.bincount(category, minlength=8).astype(float)
    probability /= probability.sum()
    bit_table = np.asarray([
        [(category_id >> bit) & 1 for bit in range(3)]
        for category_id in range(8)
    ])
    resample_rng = np.random.default_rng(resample_stream)
    category_counts = resample_rng.multinomial(
        int(detector_permutations),
        probability,
        size=int(resamples),
    )
    exceedance_counts = category_counts @ bit_table
    raw_p = (1.0 + exceedance_counts) / (
        int(detector_permutations) + 1.0
    )
    adjusted = holm_adjust_rows(raw_p)
    rejected = (
        (adjusted[:, 0] < float(alpha))
        | (adjusted[:, 2] < float(alpha))
    )
    point = float(rejected.mean())
    standard_error = float(
        np.sqrt(point * (1.0 - point) / max(int(resamples), 1))
    )
    reservoir_raw_p = (
        1.0 + exceedance.sum(axis=0)
    ) / (int(orbit_draws) + 1.0)
    return {
        "orbit_rejection_probability": point,
        "orbit_monte_carlo_se": standard_error,
        "orbit_crc_raw_p": float(reservoir_raw_p[0]),
        "orbit_low_rank_raw_p": float(reservoir_raw_p[1]),
        "orbit_hc_raw_p": float(reservoir_raw_p[2]),
        "observed_crc": float(observed[0]),
        "observed_low_rank": float(observed[1]),
        "observed_hc": float(observed[2]),
    }


def build_controlled_halo_interaction(
    anchor_interaction: np.ndarray,
    *,
    spec: ReferenceFrontierSpec,
    test_authors: np.ndarray,
    active_test_authors: np.ndarray,
    active_conditions: np.ndarray,
    halo_lambda: float,
    halo_author_support: int,
    seed: int,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Construct orthogonal core/halo geometry with controlled author support."""
    if not 0.0 <= float(halo_lambda) <= 1.0:
        raise ValueError("halo_lambda must be in [0, 1]")
    test = np.asarray(test_authors, dtype=int)
    active = np.asarray(active_test_authors, dtype=int)
    conditions = np.asarray(active_conditions, dtype=int)
    support = int(halo_author_support)
    if support < len(active) or support > len(test):
        raise ValueError("halo author support is outside valid bounds")
    rng = np.random.default_rng(int(seed))
    lookup = {int(author): index for index, author in enumerate(test)}
    active_local = np.asarray([lookup[int(author)] for author in active])
    inactive_local = np.asarray(
        [index for index in range(len(test)) if index not in active_local]
    )
    additional = support - len(active)
    halo_local = np.concatenate([
        active_local,
        (
            rng.choice(inactive_local, size=additional, replace=False)
            if additional
            else np.asarray([], dtype=int)
        ),
    ])
    dimensions = np.arange(spec.dimensions)
    core = np.zeros((len(test), spec.conditions, spec.dimensions))
    core_block = local_double_center(
        rng.normal(
            size=(len(active), len(conditions), spec.dimensions)
        )
    )
    core[np.ix_(active_local, conditions, dimensions)] = core_block
    core /= max(float(np.linalg.norm(core)), 1e-12)

    if float(halo_lambda) == 0.0:
        test_geometry = core
    else:
        halo = np.zeros_like(core)
        halo_block = local_double_center(
            rng.normal(
                size=(len(halo_local), spec.conditions, spec.dimensions)
            )
        )
        halo[np.ix_(
            halo_local,
            np.arange(spec.conditions),
            dimensions,
        )] = halo_block
        halo -= float(np.sum(halo * core)) * core
        halo /= max(float(np.linalg.norm(halo)), 1e-12)
        test_geometry = (
            np.sqrt(1.0 - float(halo_lambda)) * core
            + np.sqrt(float(halo_lambda)) * halo
        )

    interaction = np.asarray(anchor_interaction, dtype=float).copy()
    interaction[test] = test_geometry
    return interaction, {
        "halo_author_support": support,
        "core_author_support": int(len(active)),
        "realized_halo_author_indices": halo_local.tolist(),
    }


def frozen_logistic_probability(
    features: np.ndarray,
    artifact: dict[str, Any],
) -> np.ndarray:
    """Apply a JSON-frozen standardized logistic model."""
    values = np.asarray(features, dtype=float)
    mean = np.asarray(artifact["scaler_mean"], dtype=float)
    scale = np.asarray(artifact["scaler_scale"], dtype=float)
    coefficient = np.asarray(
        artifact["logistic_coefficient"],
        dtype=float,
    )
    standardized = (values - mean) / np.maximum(scale, 1e-12)
    linear = standardized @ coefficient + float(
        artifact["logistic_intercept"]
    )
    return 1.0 / (1.0 + np.exp(-linear))
