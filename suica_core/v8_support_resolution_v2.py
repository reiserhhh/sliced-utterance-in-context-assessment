"""Scale-free local resolution regions for replicated text densities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from suica_core.v8_realtext_relation_field import CorpusFeaturePanel, stable_bucket
from suica_core.v8_support_containment import (
    _robust_standardizer,
    _rotation_p,
    _split_raw,
    _stable_indices,
    replicated_density,
)


@dataclass(frozen=True)
class ScaleFreeResolutionSpec:
    """Frozen capacity/sharpness path and uncertainty budgets."""

    sharpness: tuple[float, ...] = (0.10, 0.25, 0.50, 0.75, 1.00)
    bootstrap_draws: int = 199
    rotation_draws: int = 99
    minimum_d0_half_authors: int = 24
    minimum_confirmation_authors: int = 48
    seed: int = 20260808

    def __post_init__(self) -> None:
        if not self.sharpness or any(
            not 0 < value <= 1 for value in self.sharpness
        ):
            raise ValueError("sharpness values must lie in (0, 1].")
        if sorted(set(self.sharpness)) != list(self.sharpness):
            raise ValueError("sharpness values must be unique and increasing.")
        if self.bootstrap_draws < 19 or self.rotation_draws < 19:
            raise ValueError("Uncertainty budgets must be at least 19.")
        if self.minimum_confirmation_authors < 16:
            raise ValueError("minimum_confirmation_authors is too small.")


@dataclass(frozen=True)
class SpectralBank:
    """Filters represented by eigenweights in one frozen eigenbasis."""

    eigenvectors: np.ndarray
    capacities: np.ndarray
    capacity_fraction: np.ndarray
    sharpness: np.ndarray
    achieved_sharpness: np.ndarray
    weights: np.ndarray


def _weights_for_mu(
    eigenvalues: np.ndarray,
    capacity_fraction: float,
    tau: float,
) -> np.ndarray:
    dimension = len(eigenvalues)
    capacity = capacity_fraction * dimension

    def weights(mu: float) -> np.ndarray:
        return np.clip(
            capacity_fraction + (eigenvalues - mu) / tau,
            0.0,
            1.0,
        )

    lower = float(eigenvalues.min() - tau)
    upper = float(eigenvalues.max() + tau)
    for _ in range(100):
        midpoint = 0.5 * (lower + upper)
        if float(weights(midpoint).sum()) > capacity:
            lower = midpoint
        else:
            upper = midpoint
    return weights(0.5 * (lower + upper))


def sharp_capacity_weights(
    eigenvalues: np.ndarray,
    capacity: int,
    sharpness: float,
) -> np.ndarray:
    """Return the maximum-alignment filter at fixed trace and sharpness.

    Sharpness is an upper bound on the fraction of the hard-projector squared
    distance from the isotropic filter:

        ||P - cI||_F^2 <= q * c d (1-c).

    The inequality matters when the spectrum is degenerate. In that case the
    invariant optimizer may not exhaust the budget; arbitrarily splitting a
    tied eigenspace would manufacture a coordinate-dependent hard axis.
    """
    values = np.asarray(eigenvalues, dtype=float)
    dimension = len(values)
    k = int(capacity)
    q = float(sharpness)
    if not 0 < k < dimension:
        raise ValueError("capacity must lie in (0, dimension).")
    if not 0 <= q <= 1:
        raise ValueError("sharpness must lie in [0, 1].")
    c = k / dimension
    if q <= 1e-12:
        return np.full(dimension, c)
    target_norm = q * k * (1.0 - c)
    spectral_scale = max(float(np.ptp(values)), float(np.max(np.abs(values))), 1e-8)
    tie_tolerance = max(1e-12, spectral_scale * 1e-10)
    canonical_values = values.copy()
    order = np.argsort(values)
    sorted_values = values[order].copy()
    start = 0
    for stop in range(1, dimension + 1):
        if (
            stop == dimension
            or sorted_values[stop] - sorted_values[start] > tie_tolerance
        ):
            sorted_values[start:stop] = float(np.mean(sorted_values[start:stop]))
            start = stop
    canonical_values[order] = sorted_values
    threshold = sorted_values[-k]
    hard_weights = np.zeros(dimension, dtype=float)
    above = canonical_values > threshold + tie_tolerance
    tied = np.abs(canonical_values - threshold) <= tie_tolerance
    hard_weights[above] = 1.0
    hard_weights[tied] = (k - int(above.sum())) / int(tied.sum())
    maximum_norm = float(np.sum((hard_weights - c) ** 2))
    if maximum_norm <= target_norm + 1e-9:
        return hard_weights
    lower = spectral_scale * 1e-12
    upper = max(spectral_scale, 1e-6)

    def norm_at(tau: float) -> tuple[float, np.ndarray]:
        weights = _weights_for_mu(canonical_values, c, tau)
        return float(np.sum((weights - c) ** 2)), weights

    while norm_at(upper)[0] > target_norm:
        upper *= 2.0
        if upper > 1e8:
            raise ValueError("Could not bracket the sharpness dual variable.")
    for _ in range(100):
        midpoint = 0.5 * (lower + upper)
        norm, _ = norm_at(midpoint)
        if norm > target_norm:
            lower = midpoint
        else:
            upper = midpoint
    weights = norm_at(0.5 * (lower + upper))[1]
    if not np.isclose(float(weights.sum()), k, atol=1e-7):
        raise ValueError("Sharpness filter failed its trace constraint.")
    if float(np.sum((weights - c) ** 2)) > target_norm + 1e-7:
        raise ValueError("Sharpness filter exceeded its norm constraint.")
    return weights


def build_spectral_bank(
    density: np.ndarray,
    *,
    sharpness: tuple[float, ...],
) -> SpectralBank:
    """Build the complete k=1,...,d-1 scale-free filter path."""
    values, vectors = np.linalg.eigh(0.5 * (density + density.T))
    capacities = []
    fractions = []
    sharpness_rows = []
    achieved_sharpness_rows = []
    weights = []
    dimension = len(values)
    for capacity in range(1, dimension):
        for value in sharpness:
            capacities.append(capacity)
            fractions.append(capacity / dimension)
            sharpness_rows.append(float(value))
            row = sharp_capacity_weights(values, capacity, float(value))
            weights.append(row)
            denominator = capacity * (1.0 - capacity / dimension)
            achieved_sharpness_rows.append(
                float(np.sum((row - capacity / dimension) ** 2) / denominator)
            )
    return SpectralBank(
        eigenvectors=vectors,
        capacities=np.asarray(capacities, dtype=int),
        capacity_fraction=np.asarray(fractions, dtype=float),
        sharpness=np.asarray(sharpness_rows, dtype=float),
        achieved_sharpness=np.asarray(achieved_sharpness_rows, dtype=float),
        weights=np.vstack(weights),
    )


def density_diagonal_in_basis(
    density: np.ndarray,
    eigenvectors: np.ndarray,
) -> np.ndarray:
    """Return diag(U.T density U) without forming the full product."""
    return np.sum(eigenvectors * (density @ eigenvectors), axis=0)


def gains(bank: SpectralBank, density: np.ndarray) -> np.ndarray:
    """Evaluate all filters above their isotropic capacity baselines."""
    diagonal = density_diagonal_in_basis(density, bank.eigenvectors)
    return np.einsum(
        "nd,d->n",
        bank.weights - bank.capacity_fraction[:, None],
        diagonal,
    )


def cross_oracle_gains(
    fitted_density: np.ndarray,
    evaluated_density: np.ndarray,
    *,
    sharpness: tuple[float, ...],
) -> np.ndarray:
    """Fit filters in one panel and evaluate them in another."""
    bank = build_spectral_bank(fitted_density, sharpness=sharpness)
    return gains(bank, evaluated_density)


def _simultaneous_band(
    observed: np.ndarray,
    bootstrap: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float]:
    standard_error = bootstrap.std(axis=0, ddof=1)
    safe = np.where(standard_error > 1e-12, standard_error, 1.0)
    standardized = np.abs((bootstrap - observed[None, :]) / safe[None, :])
    standardized[:, standard_error <= 1e-12] = 0.0
    critical = float(np.quantile(np.max(standardized, axis=1), 0.95))
    return (
        observed - critical * standard_error,
        observed + critical * standard_error,
        critical,
    )


def _max_rotation_p(
    observed: np.ndarray,
    rotation_values: np.ndarray,
) -> np.ndarray:
    maxima = np.max(rotation_values, axis=1)
    return np.asarray(
        [
            (1 + np.sum(maxima >= value)) / (len(maxima) + 1)
            for value in observed
        ],
        dtype=float,
    )


def _fit_d0(
    raw: np.ndarray,
    ids: np.ndarray,
    *,
    seed: int,
) -> dict[str, Any]:
    order = _stable_indices(ids, len(ids), salt=f"v8-resolution-v2-{seed}")
    midpoint = len(order) // 2
    fit = raw[order[:midpoint]]
    calibration = raw[order[midpoint:]]
    center, scale = _robust_standardizer(fit)
    fit_density, fit_rank, _ = replicated_density(
        fit,
        center=center,
        scale=scale,
    )
    calibration_density, calibration_rank, _ = replicated_density(
        calibration,
        center=center,
        scale=scale,
    )
    return {
        "center": center,
        "scale": scale,
        "fit_density": fit_density,
        "calibration_density": calibration_density,
        "fit_effective_rank": fit_rank,
        "calibration_effective_rank": calibration_rank,
        "fit_authors": len(fit),
        "calibration_authors": len(calibration),
    }


def _bootstrap_gains(
    raw: np.ndarray,
    bank: SpectralBank,
    *,
    center: np.ndarray,
    scale: np.ndarray,
    draws: int,
    rng: np.random.Generator,
) -> np.ndarray:
    result = np.empty((int(draws), len(bank.capacities)), dtype=float)
    for draw in range(int(draws)):
        sampled = raw[rng.integers(0, len(raw), size=len(raw))]
        density, _, _ = replicated_density(
            sampled,
            center=center,
            scale=scale,
        )
        result[draw] = gains(bank, density)
    return result


def _rotation_gains(
    density: np.ndarray,
    bank: SpectralBank,
    *,
    draws: int,
    rng: np.random.Generator,
) -> np.ndarray:
    result = np.empty((int(draws), len(bank.capacities)), dtype=float)
    for draw in range(int(draws)):
        rotation, _ = np.linalg.qr(
            rng.normal(size=(density.shape[0], density.shape[0]))
        )
        result[draw] = gains(
            bank,
            rotation @ density @ rotation.T,
        )
    return result


def evaluate_scale_free_resolution(
    corpus: str,
    panel: CorpusFeaturePanel,
    family: str,
    *,
    spec: ScaleFreeResolutionSpec,
) -> dict[str, Any]:
    """Discover a D1 resolution region and confirm it once in D2."""
    d0_raw, d0_ids = _split_raw(panel, family, "D0")
    d1_raw, _ = _split_raw(panel, family, "D1")
    d2_raw, _ = _split_raw(panel, family, "D2")
    d0 = _fit_d0(
        d0_raw,
        d0_ids,
        seed=spec.seed
        + stable_bucket(corpus, salt=f"resolution-v2-{family}", modulus=100_000),
    )
    if (
        d0["fit_authors"] < spec.minimum_d0_half_authors
        or d0["calibration_authors"] < spec.minimum_d0_half_authors
    ):
        return {
            "status": "D0_SAMPLE_UNDERPOWERED",
            "cells": pd.DataFrame(),
            "frontier": pd.DataFrame(),
        }
    if (
        len(d1_raw) < spec.minimum_confirmation_authors
        or len(d2_raw) < spec.minimum_confirmation_authors
    ):
        return {
            "status": "CONFIRMATION_SAMPLE_UNDERPOWERED",
            "cells": pd.DataFrame(),
            "frontier": pd.DataFrame(),
            "n_d1": int(len(d1_raw)),
            "n_d2": int(len(d2_raw)),
        }
    alignment, alignment_p = _rotation_p(
        d0["fit_density"],
        d0["calibration_density"],
        draws=spec.rotation_draws,
        seed=spec.seed
        + stable_bucket(
            corpus,
            salt=f"resolution-v2-d0-{family}",
            modulus=100_000,
        ),
    )
    bank = build_spectral_bank(
        d0["fit_density"],
        sharpness=spec.sharpness,
    )
    d1_density, d1_rank, _ = replicated_density(
        d1_raw,
        center=d0["center"],
        scale=d0["scale"],
    )
    d2_density, d2_rank, _ = replicated_density(
        d2_raw,
        center=d0["center"],
        scale=d0["scale"],
    )
    observed_d1 = gains(bank, d1_density)
    observed_d2 = gains(bank, d2_density)
    rng = np.random.default_rng(
        spec.seed
        + stable_bucket(
            corpus,
            salt=f"resolution-v2-bootstrap-{family}",
            modulus=2**31 - 1,
        )
    )
    bootstrap_d1 = _bootstrap_gains(
        d1_raw,
        bank,
        center=d0["center"],
        scale=d0["scale"],
        draws=spec.bootstrap_draws,
        rng=rng,
    )
    bootstrap_d2 = _bootstrap_gains(
        d2_raw,
        bank,
        center=d0["center"],
        scale=d0["scale"],
        draws=spec.bootstrap_draws,
        rng=rng,
    )
    d1_low, d1_high, d1_critical = _simultaneous_band(
        observed_d1,
        bootstrap_d1,
    )
    d2_low, d2_high, d2_critical = _simultaneous_band(
        observed_d2,
        bootstrap_d2,
    )
    rotation_d1 = _rotation_gains(
        d1_density,
        bank,
        draws=spec.rotation_draws,
        rng=rng,
    )
    rotation_d2 = _rotation_gains(
        d2_density,
        bank,
        draws=spec.rotation_draws,
        rng=rng,
    )
    p_d1 = _max_rotation_p(observed_d1, rotation_d1)
    p_d2 = _max_rotation_p(observed_d2, rotation_d2)
    d0_replicated = bool(alignment_p <= 0.05)
    discovery = d0_replicated & (d1_low > 0) & (p_d1 <= 0.05)
    confirmation = discovery & (d2_low > 0) & (p_d2 <= 0.05)

    # Descriptive cross-panel oracles avoid same-panel oracle optimism.
    d1_oracle = cross_oracle_gains(
        d2_density,
        d1_density,
        sharpness=spec.sharpness,
    )
    d2_oracle = cross_oracle_gains(
        d1_density,
        d2_density,
        sharpness=spec.sharpness,
    )
    ratio_d1 = np.divide(
        observed_d1,
        d1_oracle,
        out=np.full_like(observed_d1, np.nan),
        where=d1_oracle > 1e-12,
    )
    ratio_d2 = np.divide(
        observed_d2,
        d2_oracle,
        out=np.full_like(observed_d2, np.nan),
        where=d2_oracle > 1e-12,
    )
    cells = pd.DataFrame(
        {
            "corpus": corpus,
            "family": family,
            "capacity": bank.capacities,
            "capacity_fraction": bank.capacity_fraction,
            "sharpness": bank.sharpness,
            "achieved_sharpness": bank.achieved_sharpness,
            "d1_gain": observed_d1,
            "d1_simultaneous_low": d1_low,
            "d1_simultaneous_high": d1_high,
            "d1_max_rotation_p": p_d1,
            "d1_cross_oracle_gain": d1_oracle,
            "d1_cross_oracle_ratio": ratio_d1,
            "d1_discovery": discovery.astype(int),
            "d2_gain": observed_d2,
            "d2_simultaneous_low": d2_low,
            "d2_simultaneous_high": d2_high,
            "d2_max_rotation_p": p_d2,
            "d2_cross_oracle_gain": d2_oracle,
            "d2_cross_oracle_ratio": ratio_d2,
            "d2_confirmation": confirmation.astype(int),
        }
    )
    frontier_rows = []
    for capacity, group in cells.groupby("capacity", sort=True):
        discovered = group.loc[group["d1_discovery"].eq(1)]
        confirmed = group.loc[group["d2_confirmation"].eq(1)]
        frontier_rows.append(
            {
                "corpus": corpus,
                "family": family,
                "capacity": int(capacity),
                "capacity_fraction": float(group["capacity_fraction"].iloc[0]),
                "discovered_sharpness_count": int(len(discovered)),
                "confirmed_sharpness_count": int(len(confirmed)),
                "minimum_confirmed_sharpness": (
                    float(confirmed["sharpness"].min())
                    if len(confirmed)
                    else float("nan")
                ),
                "maximum_confirmed_sharpness": (
                    float(confirmed["sharpness"].max())
                    if len(confirmed)
                    else float("nan")
                ),
            }
        )
    return {
        "status": (
            "D0_REPLICATED_DENSITY_NOT_CONFIRMED"
            if not d0_replicated
            else (
                "SCALE_FREE_RESOLUTION_REGION_CONFIRMED"
                if confirmation.any()
                else (
                    "D1_REGION_NOT_CONFIRMED"
                    if discovery.any()
                    else "NO_D1_RESOLUTION_REGION"
                )
            )
        ),
        "cells": cells,
        "frontier": pd.DataFrame(frontier_rows),
        "n_d0_fit": int(d0["fit_authors"]),
        "n_d0_calibration": int(d0["calibration_authors"]),
        "n_d1": int(len(d1_raw)),
        "n_d2": int(len(d2_raw)),
        "d0_internal_hs": alignment,
        "d0_internal_p": alignment_p,
        "d0_fit_effective_rank": d0["fit_effective_rank"],
        "d0_calibration_effective_rank": d0["calibration_effective_rank"],
        "d1_effective_rank": d1_rank,
        "d2_effective_rank": d2_rank,
        "d1_band_critical": d1_critical,
        "d2_band_critical": d2_critical,
        "confirmed_cell_count": int(confirmation.sum()),
        "discovered_cell_count": int(discovery.sum()),
    }
