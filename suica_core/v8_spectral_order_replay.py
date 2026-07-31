"""Shared-gauge spectral-order replay for replicated real-text densities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from suica_core.v8_support_containment import (
    _robust_standardizer,
    _stable_indices,
    replicated_density,
)
from suica_core.v8_support_resolution_v2 import (
    build_spectral_bank,
    gains,
)


@dataclass(frozen=True)
class SpectralOrderSpec:
    """Frozen replay design and uncertainty budgets."""

    bootstrap_draws: int = 199
    sharpness: tuple[float, ...] = (0.10, 0.25, 0.50, 0.75, 1.00)
    minimum_authors: int = 48
    seed: int = 20260809

    def __post_init__(self) -> None:
        if self.bootstrap_draws < 19:
            raise ValueError("bootstrap_draws must be at least 19.")
        if not self.sharpness or any(
            not 0 < value <= 1 for value in self.sharpness
        ):
            raise ValueError("sharpness values must lie in (0, 1].")
        if sorted(set(self.sharpness)) != list(self.sharpness):
            raise ValueError("sharpness values must be unique and increasing.")
        if self.minimum_authors < 16:
            raise ValueError("minimum_authors is too small.")


@dataclass(frozen=True)
class SharedGauge:
    """Pair-symmetric robust gauge fitted on equal D0 author counts."""

    center: np.ndarray
    scale: np.ndarray
    left_d0: np.ndarray
    right_d0: np.ndarray
    left_d0_a: np.ndarray
    left_d0_b: np.ndarray
    right_d0_a: np.ndarray
    right_d0_b: np.ndarray


def _select(
    raw: np.ndarray,
    ids: np.ndarray,
    count: int,
    *,
    salt: str,
) -> np.ndarray:
    return raw[_stable_indices(ids, count, salt=salt)]


def fit_shared_gauge(
    left_raw: np.ndarray,
    left_ids: np.ndarray,
    right_raw: np.ndarray,
    right_ids: np.ndarray,
    *,
    salt: str,
) -> SharedGauge:
    """Fit one diagonal gauge and deterministic D0 technical halves."""
    count = min(len(left_raw), len(right_raw))
    if count < 4:
        raise ValueError("At least four D0 authors per corpus are required.")
    if count % 2:
        count -= 1
    left = _select(left_raw, left_ids, count, salt=f"{salt}-left")
    right = _select(right_raw, right_ids, count, salt=f"{salt}-right")
    center, scale = _robust_standardizer(np.concatenate([left, right], axis=0))
    midpoint = count // 2
    return SharedGauge(
        center=center,
        scale=scale,
        left_d0=left,
        right_d0=right,
        left_d0_a=left[:midpoint],
        left_d0_b=left[midpoint:],
        right_d0_a=right[:midpoint],
        right_d0_b=right[midpoint:],
    )


def lorenz_excess(density: np.ndarray) -> np.ndarray:
    """Return cumulative spectral mass above the isotropic Lorenz line."""
    values = np.clip(
        np.linalg.eigvalsh(0.5 * (density + density.T)),
        0.0,
        None,
    )[::-1]
    total = float(values.sum())
    if total <= 1e-12:
        raise ValueError("density has no positive mass.")
    values /= total
    dimension = len(values)
    return np.cumsum(values)[:-1] - np.arange(1, dimension) / dimension


def spectral_signature(
    density: np.ndarray,
    *,
    sharpness: tuple[float, ...],
) -> pd.DataFrame:
    """Return the complete capacity-sharpness support-function signature."""
    bank = build_spectral_bank(density, sharpness=sharpness)
    return pd.DataFrame(
        {
            "capacity": bank.capacities,
            "capacity_fraction": bank.capacity_fraction,
            "sharpness": bank.sharpness,
            "achieved_sharpness": bank.achieved_sharpness,
            "gain": gains(bank, density),
        }
    )


def _density(
    raw: np.ndarray,
    center: np.ndarray,
    scale: np.ndarray,
) -> np.ndarray:
    return replicated_density(raw, center=center, scale=scale)[0]


def _oriented_difference(
    left_density: np.ndarray,
    right_density: np.ndarray,
    *,
    direction: str,
) -> np.ndarray:
    left = lorenz_excess(left_density)
    right = lorenz_excess(right_density)
    if direction == "right_minus_left":
        difference = right - left
    elif direction == "left_minus_right":
        difference = left - right
    else:
        raise ValueError(f"Unknown direction: {direction}")
    difference[np.abs(difference) < 1e-12] = 0.0
    return difference


def _resample(
    raw: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    return raw[rng.integers(0, len(raw), size=len(raw))]


def _bootstrap_stage(
    gauge: SharedGauge,
    left_stage: np.ndarray,
    right_stage: np.ndarray,
    *,
    direction: str,
    draws: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Bootstrap D0 gauge and stage authors jointly."""
    dimension = left_stage.shape[-1]
    result = np.empty((draws, dimension - 1), dtype=float)
    for draw in range(draws):
        left_d0 = _resample(gauge.left_d0, rng)
        right_d0 = _resample(gauge.right_d0, rng)
        center, scale = _robust_standardizer(
            np.concatenate([left_d0, right_d0], axis=0)
        )
        left_density = _density(_resample(left_stage, rng), center, scale)
        right_density = _density(_resample(right_stage, rng), center, scale)
        result[draw] = _oriented_difference(
            left_density,
            right_density,
            direction=direction,
        )
    return result


def _bootstrap_d0_tolerance(
    gauge: SharedGauge,
    *,
    draws: int,
    rng: np.random.Generator,
) -> tuple[float, np.ndarray]:
    """Calibrate the D0 split-replication sup-norm discrepancy."""
    maxima = np.empty(draws, dtype=float)
    for draw in range(draws):
        left_a = _resample(gauge.left_d0_a, rng)
        left_b = _resample(gauge.left_d0_b, rng)
        right_a = _resample(gauge.right_d0_a, rng)
        right_b = _resample(gauge.right_d0_b, rng)
        center, scale = _robust_standardizer(
            np.concatenate([left_a, left_b, right_a, right_b], axis=0)
        )
        left_delta = np.abs(
            lorenz_excess(_density(left_a, center, scale))
            - lorenz_excess(_density(left_b, center, scale))
        )
        right_delta = np.abs(
            lorenz_excess(_density(right_a, center, scale))
            - lorenz_excess(_density(right_b, center, scale))
        )
        maxima[draw] = max(float(left_delta.max()), float(right_delta.max()))
    return float(np.quantile(maxima, 0.95)), maxima


def simultaneous_sup_band(
    observed: np.ndarray,
    bootstrap: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Return a non-studentized simultaneous bootstrap sup-norm band.

    Spectral Lorenz curves often contain exact zero-variance plateaus caused
    by replicated-density rank deficiency. Pointwise studentization is
    undefined there and can make a max-t critical value explode.
    """
    errors = np.asarray(bootstrap, dtype=float) - np.asarray(observed)[None, :]
    critical = float(np.quantile(np.max(np.abs(errors), axis=1), 0.95))
    return observed - critical, observed + critical, critical


def evaluate_spectral_order_replay(
    family: str,
    left_raw: dict[str, tuple[np.ndarray, np.ndarray]],
    right_raw: dict[str, tuple[np.ndarray, np.ndarray]],
    *,
    direction: str,
    left_name: str,
    right_name: str,
    spec: SpectralOrderSpec,
) -> dict[str, Any]:
    """Replay one post-hoc spectral-order hypothesis in a shared gauge."""
    for split in ("D0", "D1", "D2"):
        if min(len(left_raw[split][0]), len(right_raw[split][0])) < spec.minimum_authors:
            return {
                "family": family,
                "status": "SAMPLE_UNDERPOWERED",
                "split": split,
                "n_left": int(len(left_raw[split][0])),
                "n_right": int(len(right_raw[split][0])),
            }
    gauge = fit_shared_gauge(
        *left_raw["D0"],
        *right_raw["D0"],
        salt=f"v8-spectral-order-{spec.seed}-{family}",
    )
    stage_count = {
        split: min(len(left_raw[split][0]), len(right_raw[split][0]))
        for split in ("D1", "D2")
    }
    selected: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for split in ("D1", "D2"):
        selected[split] = (
            _select(
                *left_raw[split],
                stage_count[split],
                salt=f"v8-spectral-order-{family}-{split}-left",
            ),
            _select(
                *right_raw[split],
                stage_count[split],
                salt=f"v8-spectral-order-{family}-{split}-right",
            ),
        )

    rng = np.random.default_rng(spec.seed + (0 if family == "M" else 10_000))
    epsilon, epsilon_draws = _bootstrap_d0_tolerance(
        gauge,
        draws=spec.bootstrap_draws,
        rng=rng,
    )
    curves = []
    stage_results: dict[str, Any] = {}
    stage_bootstrap: dict[str, np.ndarray] = {}
    densities: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for split in ("D1", "D2"):
        left_stage, right_stage = selected[split]
        left_density = _density(left_stage, gauge.center, gauge.scale)
        right_density = _density(right_stage, gauge.center, gauge.scale)
        densities[split] = (left_density, right_density)
        observed = _oriented_difference(
            left_density,
            right_density,
            direction=direction,
        )
        bootstrap = _bootstrap_stage(
            gauge,
            left_stage,
            right_stage,
            direction=direction,
            draws=spec.bootstrap_draws,
            rng=rng,
        )
        low, high, critical = simultaneous_sup_band(observed, bootstrap)
        stage_bootstrap[split] = bootstrap
        stage_results[split] = {
            "minimum_difference": float(observed.min()),
            "maximum_difference": float(observed.max()),
            "minimum_simultaneous_low": float(low.min()),
            "maximum_simultaneous_low": float(low.max()),
            "positive_fraction": float(np.mean(observed > 1e-12)),
            "approximate_majorization": bool(
                low.min() > -epsilon and low.max() > 0
            ),
            "band_critical": float(critical),
        }
        dimension = len(observed) + 1
        for capacity, values in enumerate(zip(observed, low, high), start=1):
            curves.append(
                {
                    "family": family,
                    "split": split,
                    "capacity": capacity,
                    "capacity_fraction": capacity / dimension,
                    "difference": values[0],
                    "simultaneous_low": values[1],
                    "simultaneous_high": values[2],
                    "d0_tolerance": epsilon,
                }
            )

    d1_frame = pd.DataFrame(curves)
    discovery_region = d1_frame.loc[
        d1_frame["split"].eq("D1") & d1_frame["simultaneous_low"].gt(0),
        "capacity",
    ].to_numpy(dtype=int)
    if len(discovery_region):
        indices = discovery_region - 1
        d2_integral = float(
            np.mean(
                d1_frame.loc[
                    d1_frame["split"].eq("D2"), "difference"
                ].to_numpy()[indices]
            )
        )
        integral_bootstrap = stage_bootstrap["D2"][:, indices].mean(axis=1)
        d2_integral_low = float(np.quantile(integral_bootstrap, 0.025))
    else:
        d2_integral = float("nan")
        d2_integral_low = float("nan")
    replay_supported = bool(
        stage_results["D1"]["approximate_majorization"]
        and stage_results["D2"]["approximate_majorization"]
        and len(discovery_region)
        and d2_integral_low > 0
    )

    soft_rows = []
    for split, (left_density, right_density) in densities.items():
        left_signature = spectral_signature(
            left_density,
            sharpness=spec.sharpness,
        )
        right_signature = spectral_signature(
            right_density,
            sharpness=spec.sharpness,
        )
        if not np.array_equal(
            left_signature[["capacity", "sharpness"]].to_numpy(),
            right_signature[["capacity", "sharpness"]].to_numpy(),
        ):
            raise ValueError("Spectral signature grids do not match.")
        if direction == "right_minus_left":
            difference = right_signature["gain"] - left_signature["gain"]
        else:
            difference = left_signature["gain"] - right_signature["gain"]
        for index, row in left_signature.iterrows():
            soft_rows.append(
                {
                    "family": family,
                    "split": split,
                    "capacity": int(row["capacity"]),
                    "capacity_fraction": float(row["capacity_fraction"]),
                    "sharpness": float(row["sharpness"]),
                    "left_achieved_sharpness": float(
                        left_signature.loc[index, "achieved_sharpness"]
                    ),
                    "right_achieved_sharpness": float(
                        right_signature.loc[index, "achieved_sharpness"]
                    ),
                    "oriented_difference": float(difference.loc[index]),
                }
            )
    soft = pd.DataFrame(soft_rows)
    soft_consistency = {
        split: float(
            np.mean(
                soft.loc[soft["split"].eq(split), "oriented_difference"] > 1e-12
            )
        )
        for split in ("D1", "D2")
    }
    return {
        "family": family,
        "status": (
            "SHARED_GAUGE_SPECTRAL_ORDER_REPLAY_SUPPORTED"
            if replay_supported
            else "SHARED_GAUGE_SPECTRAL_ORDER_REPLAY_NOT_SUPPORTED"
        ),
        "direction": direction,
        "left_corpus": left_name,
        "right_corpus": right_name,
        "d0_equal_authors": int(len(gauge.left_d0)),
        "d1_equal_authors": int(stage_count["D1"]),
        "d2_equal_authors": int(stage_count["D2"]),
        "d0_tolerance": epsilon,
        "d0_tolerance_draw_mean": float(epsilon_draws.mean()),
        "d1": stage_results["D1"],
        "d2": stage_results["D2"],
        "discovery_region_count": int(len(discovery_region)),
        "discovery_region_min_capacity": (
            int(discovery_region.min()) if len(discovery_region) else None
        ),
        "discovery_region_max_capacity": (
            int(discovery_region.max()) if len(discovery_region) else None
        ),
        "d2_discovery_region_integral": d2_integral,
        "d2_discovery_region_integral_low": d2_integral_low,
        "soft_positive_fraction": soft_consistency,
        "curves": pd.DataFrame(curves),
        "soft_signature": soft,
    }
