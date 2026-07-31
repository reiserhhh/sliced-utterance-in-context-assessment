"""Spectrum-matched approximate orientation overlap for replicated densities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from suica_core.v8_spectral_order_replay import (
    SharedGauge,
    _density,
    _resample,
    _select,
    fit_shared_gauge,
)
from suica_core.v8_support_containment import _robust_standardizer


@dataclass(frozen=True)
class OrientationOverlapSpec:
    """Frozen exploratory orientation-overlap settings."""

    calibration_draws: int = 99
    bootstrap_draws: int = 199
    rotation_draws: int = 499
    maximum_rank: int = 48
    minimum_rank: int = 2
    seed: int = 20260810

    def __post_init__(self) -> None:
        if min(
            self.calibration_draws,
            self.bootstrap_draws,
            self.rotation_draws,
        ) < 19:
            raise ValueError("All resampling budgets must be at least 19.")
        if self.minimum_rank < 2 or self.maximum_rank < self.minimum_rank:
            raise ValueError("Invalid orientation-rank bounds.")


@dataclass(frozen=True)
class OrientationTemplate:
    """D0-frozen rank and matched anisotropy spectrum."""

    epsilon: float
    rank: int
    weights: np.ndarray
    left_d0_density: np.ndarray
    right_d0_density: np.ndarray


def _eigensystem(density: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    values, vectors = np.linalg.eigh(0.5 * (density + density.T))
    order = np.argsort(values)[::-1]
    return np.clip(values[order], 0.0, None), vectors[:, order]


def _anisotropy_strength(
    density: np.ndarray,
    epsilon: float,
) -> tuple[np.ndarray, np.ndarray]:
    values, vectors = _eigensystem(density)
    return np.clip(values - 1.0 / len(values) - epsilon, 0.0, None), vectors


def calibrate_epsilon(
    gauge: SharedGauge,
    *,
    draws: int,
    rng: np.random.Generator,
) -> tuple[float, np.ndarray]:
    """Calibrate sorted-spectrum instability from D0 technical halves."""
    maxima = np.empty(draws, dtype=float)
    for draw in range(draws):
        left_a = _resample(gauge.left_d0_a, rng)
        left_b = _resample(gauge.left_d0_b, rng)
        right_a = _resample(gauge.right_d0_a, rng)
        right_b = _resample(gauge.right_d0_b, rng)
        center, scale = _robust_standardizer(
            np.concatenate([left_a, left_b, right_a, right_b], axis=0)
        )
        spectra = [
            _eigensystem(_density(values, center, scale))[0]
            for values in (left_a, left_b, right_a, right_b)
        ]
        maxima[draw] = max(
            float(np.max(np.abs(spectra[0] - spectra[1]))),
            float(np.max(np.abs(spectra[2] - spectra[3]))),
        )
    return float(np.quantile(maxima, 0.95)), maxima


def _pool_degenerate_blocks(
    strengths: np.ndarray,
    *,
    tolerance: float,
) -> np.ndarray:
    pooled = np.asarray(strengths, dtype=float).copy()
    start = 0
    for stop in range(1, len(pooled) + 1):
        if stop == len(pooled) or pooled[start] - pooled[stop] > tolerance:
            pooled[start:stop] = float(np.mean(pooled[start:stop]))
            start = stop
    return pooled


def fit_orientation_template(
    gauge: SharedGauge,
    epsilon: float,
    *,
    maximum_rank: int,
    minimum_rank: int,
) -> OrientationTemplate:
    """Freeze a common identifiable rank and geometric-mean spectrum."""
    left_density = _density(gauge.left_d0, gauge.center, gauge.scale)
    right_density = _density(gauge.right_d0, gauge.center, gauge.scale)
    left_strength, _ = _anisotropy_strength(left_density, epsilon)
    right_strength, _ = _anisotropy_strength(right_density, epsilon)
    rank = min(
        int(np.sum(left_strength > 0)),
        int(np.sum(right_strength > 0)),
        int(maximum_rank),
    )
    if rank < minimum_rank:
        raise ValueError("ORIENTATION_RANK_UNDERRESOLVED")
    geometric = np.sqrt(left_strength[:rank] * right_strength[:rank])
    if float(geometric.sum()) <= 1e-12:
        raise ValueError("ORIENTATION_SPECTRUM_UNDERRESOLVED")
    geometric = _pool_degenerate_blocks(
        geometric,
        tolerance=min(float(epsilon), 0.05 * float(geometric.max())),
    )
    weights = geometric / geometric.sum()
    return OrientationTemplate(
        epsilon=float(epsilon),
        rank=rank,
        weights=weights,
        left_d0_density=left_density,
        right_d0_density=right_density,
    )


def _matched_weights_for_rank(
    template: OrientationTemplate,
    rank: int,
) -> np.ndarray:
    left_strength, _ = _anisotropy_strength(
        template.left_d0_density,
        template.epsilon,
    )
    right_strength, _ = _anisotropy_strength(
        template.right_d0_density,
        template.epsilon,
    )
    geometric = np.sqrt(left_strength[:rank] * right_strength[:rank])
    geometric = _pool_degenerate_blocks(
        geometric,
        tolerance=min(
            float(template.epsilon),
            0.05 * float(max(geometric.max(), 1e-12)),
        ),
    )
    return geometric / geometric.sum()


def orientation_metrics(
    left_vectors: np.ndarray,
    right_vectors: np.ndarray,
    left_weights: np.ndarray,
    right_weights: np.ndarray,
) -> dict[str, float]:
    """Compute weighted HS, root fidelity, and principal-angle affinity."""
    cross = np.asarray(left_vectors).T @ np.asarray(right_vectors)
    left_weights = np.asarray(left_weights, dtype=float)
    right_weights = np.asarray(right_weights, dtype=float)
    weighted_cross = (
        np.sqrt(left_weights)[:, None]
        * cross
        * np.sqrt(right_weights)[None, :]
    )
    numerator = float(
        np.sum(
            cross**2
            * left_weights[:, None]
            * right_weights[None, :]
        )
    )
    denominator = float(
        np.sqrt(np.sum(left_weights**2) * np.sum(right_weights**2))
    )
    singular_values = np.linalg.svd(weighted_cross, compute_uv=False)
    principal = np.linalg.svd(cross, compute_uv=False)
    return {
        "hs": numerator / max(denominator, 1e-12),
        "fidelity": float(singular_values.sum()),
        "principal_affinity": float(np.mean(principal**2)),
        "exact_intersection_rank": int(np.sum(principal >= 1.0 - 1e-8)),
    }


def _stage_system(
    density: np.ndarray,
    template: OrientationTemplate,
    *,
    matched: bool,
) -> tuple[np.ndarray, np.ndarray]:
    strengths, vectors = _anisotropy_strength(density, template.epsilon)
    vectors = vectors[:, : template.rank]
    if matched:
        return vectors, template.weights
    weights = strengths[: template.rank]
    if float(weights.sum()) <= 1e-12:
        raise ValueError("STAGE_ANISOTROPY_UNDERRESOLVED")
    return vectors, weights / weights.sum()


def _haar_null(
    left_vectors: np.ndarray,
    left_weights: np.ndarray,
    right_weights: np.ndarray,
    *,
    draws: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    dimension, rank = left_vectors.shape
    result = {
        "hs": np.empty(draws, dtype=float),
        "fidelity": np.empty(draws, dtype=float),
        "principal_affinity": np.empty(draws, dtype=float),
    }
    for draw in range(draws):
        random_frame, _ = np.linalg.qr(
            rng.normal(size=(dimension, rank)),
            mode="reduced",
        )
        metrics = orientation_metrics(
            left_vectors,
            random_frame,
            left_weights,
            right_weights,
        )
        for name in result:
            result[name][draw] = metrics[name]
    return result


def _bootstrap_stage_metrics(
    gauge: SharedGauge,
    left_stage: np.ndarray,
    right_stage: np.ndarray,
    template: OrientationTemplate,
    *,
    matched: bool,
    draws: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    result = {
        "hs": np.empty(draws, dtype=float),
        "fidelity": np.empty(draws, dtype=float),
        "principal_affinity": np.empty(draws, dtype=float),
    }
    for draw in range(draws):
        left_d0 = _resample(gauge.left_d0, rng)
        right_d0 = _resample(gauge.right_d0, rng)
        center, scale = _robust_standardizer(
            np.concatenate([left_d0, right_d0], axis=0)
        )
        left_density = _density(_resample(left_stage, rng), center, scale)
        right_density = _density(_resample(right_stage, rng), center, scale)
        left_vectors, left_weights = _stage_system(
            left_density,
            template,
            matched=matched,
        )
        right_vectors, right_weights = _stage_system(
            right_density,
            template,
            matched=matched,
        )
        metrics = orientation_metrics(
            left_vectors,
            right_vectors,
            left_weights,
            right_weights,
        )
        for name in result:
            result[name][draw] = metrics[name]
    return result


def _bootstrap_rank_metrics(
    gauge: SharedGauge,
    left_stage: np.ndarray,
    right_stage: np.ndarray,
    template: OrientationTemplate,
    *,
    rank: int,
    weights: np.ndarray,
    draws: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Bootstrap one frozen matched-spectrum rank sensitivity."""
    result = {
        "hs": np.empty(draws, dtype=float),
        "fidelity": np.empty(draws, dtype=float),
        "principal_affinity": np.empty(draws, dtype=float),
    }
    for draw in range(draws):
        left_d0 = _resample(gauge.left_d0, rng)
        right_d0 = _resample(gauge.right_d0, rng)
        center, scale = _robust_standardizer(
            np.concatenate([left_d0, right_d0], axis=0)
        )
        left_density = _density(_resample(left_stage, rng), center, scale)
        right_density = _density(_resample(right_stage, rng), center, scale)
        _, left_vectors = _eigensystem(left_density)
        _, right_vectors = _eigensystem(right_density)
        metrics = orientation_metrics(
            left_vectors[:, :rank],
            right_vectors[:, :rank],
            weights,
            weights,
        )
        for name in result:
            result[name][draw] = metrics[name]
    return result


def _evaluate_pair(
    left_density: np.ndarray,
    right_density: np.ndarray,
    template: OrientationTemplate,
    *,
    arm: str,
    rotation_draws: int,
    rng: np.random.Generator,
) -> tuple[dict[str, float], dict[str, np.ndarray]]:
    matched = arm == "matched_spectrum"
    left_vectors, left_weights = _stage_system(
        left_density,
        template,
        matched=matched,
    )
    right_vectors, right_weights = _stage_system(
        right_density,
        template,
        matched=matched,
    )
    observed = orientation_metrics(
        left_vectors,
        right_vectors,
        left_weights,
        right_weights,
    )
    null = _haar_null(
        left_vectors,
        left_weights,
        right_weights,
        draws=rotation_draws,
        rng=rng,
    )
    return observed, null


def evaluate_orientation_family(
    family: str,
    left_raw: dict[str, tuple[np.ndarray, np.ndarray]],
    right_raw: dict[str, tuple[np.ndarray, np.ndarray]],
    *,
    spec: OrientationOverlapSpec,
) -> dict[str, Any]:
    """Run one family in a shared gauge; all conclusions remain exploratory."""
    for split in ("D0", "D1", "D2"):
        if min(len(left_raw[split][0]), len(right_raw[split][0])) < 48:
            return {
                "family": family,
                "status": "SAMPLE_UNDERPOWERED",
                "cells": pd.DataFrame(),
                "nulls": {},
            }
    gauge = fit_shared_gauge(
        *left_raw["D0"],
        *right_raw["D0"],
        salt=f"v8-orientation-{spec.seed}-{family}",
    )
    rng = np.random.default_rng(spec.seed + (0 if family == "M" else 20_000))
    epsilon, epsilon_draws = calibrate_epsilon(
        gauge,
        draws=spec.calibration_draws,
        rng=rng,
    )
    try:
        template = fit_orientation_template(
            gauge,
            epsilon,
            maximum_rank=spec.maximum_rank,
            minimum_rank=spec.minimum_rank,
        )
    except ValueError as error:
        return {
            "family": family,
            "status": str(error),
            "epsilon": epsilon,
            "cells": pd.DataFrame(),
            "nulls": {},
        }

    d0_internal = []
    for corpus, first, second in (
        ("pandora", gauge.left_d0_a, gauge.left_d0_b),
        ("essays", gauge.right_d0_a, gauge.right_d0_b),
    ):
        first_density = _density(first, gauge.center, gauge.scale)
        second_density = _density(second, gauge.center, gauge.scale)
        observed, null = _evaluate_pair(
            first_density,
            second_density,
            template,
            arm="matched_spectrum",
            rotation_draws=spec.rotation_draws,
            rng=rng,
        )
        p = (1 + np.sum(null["hs"] >= observed["hs"])) / (
            spec.rotation_draws + 1
        )
        d0_internal.append(
            {
                "corpus": corpus,
                "hs": observed["hs"],
                "hs_null_mean": float(null["hs"].mean()),
                "hs_p": float(p),
            }
        )
    d0_resolved = all(row["hs_p"] <= 0.05 for row in d0_internal)

    cells = []
    rank_sensitivity_rows = []
    rank_nulls: dict[tuple[str, int, str], np.ndarray] = {}
    nulls: dict[tuple[str, str, str], np.ndarray] = {}
    for split in ("D1", "D2"):
        count = min(len(left_raw[split][0]), len(right_raw[split][0]))
        left_stage = _select(
            *left_raw[split],
            count,
            salt=f"v8-orientation-{family}-{split}-left",
        )
        right_stage = _select(
            *right_raw[split],
            count,
            salt=f"v8-orientation-{family}-{split}-right",
        )
        left_density = _density(left_stage, gauge.center, gauge.scale)
        right_density = _density(right_stage, gauge.center, gauge.scale)
        sensitivity_ranks = sorted(
            {
                max(spec.minimum_rank, template.rank - offset)
                for offset in (6, 4, 2, 0)
                if template.rank - offset >= spec.minimum_rank
            }
        )
        left_values, left_vectors_all = _eigensystem(left_density)
        right_values, right_vectors_all = _eigensystem(right_density)
        del left_values, right_values
        for rank in sensitivity_ranks:
            weights = _matched_weights_for_rank(template, rank)
            observed_sensitivity = orientation_metrics(
                left_vectors_all[:, :rank],
                right_vectors_all[:, :rank],
                weights,
                weights,
            )
            null_sensitivity = _haar_null(
                left_vectors_all[:, :rank],
                weights,
                weights,
                draws=spec.rotation_draws,
                rng=rng,
            )
            bootstrap_sensitivity = _bootstrap_rank_metrics(
                gauge,
                left_stage,
                right_stage,
                template,
                rank=rank,
                weights=weights,
                draws=spec.bootstrap_draws,
                rng=rng,
            )
            for metric in ("hs", "fidelity", "principal_affinity"):
                null_mean = float(null_sensitivity[metric].mean())
                rank_sensitivity_rows.append(
                    {
                        "family": family,
                        "split": split,
                        "rank": rank,
                        "metric": metric,
                        "observed": observed_sensitivity[metric],
                        "null_mean": null_mean,
                        "delta": float(
                            observed_sensitivity[metric] - null_mean
                        ),
                        "bootstrap_delta_low": float(
                            np.quantile(
                                bootstrap_sensitivity[metric] - null_mean,
                                0.025,
                            )
                        ),
                        "raw_rotation_p": float(
                            (
                                1
                                + np.sum(
                                    null_sensitivity[metric]
                                    >= observed_sensitivity[metric]
                                )
                            )
                            / (spec.rotation_draws + 1)
                        ),
                    }
                )
                rank_nulls[(split, rank, metric)] = null_sensitivity[metric]
        for arm in ("native_spectrum", "matched_spectrum"):
            observed, null = _evaluate_pair(
                left_density,
                right_density,
                template,
                arm=arm,
                rotation_draws=spec.rotation_draws,
                rng=rng,
            )
            bootstrap = _bootstrap_stage_metrics(
                gauge,
                left_stage,
                right_stage,
                template,
                matched=arm == "matched_spectrum",
                draws=spec.bootstrap_draws,
                rng=rng,
            )
            for metric in ("hs", "fidelity", "principal_affinity"):
                null_mean = float(null[metric].mean())
                delta = float(observed[metric] - null_mean)
                delta_low = float(
                    np.quantile(bootstrap[metric] - null_mean, 0.025)
                )
                raw_p = float(
                    (1 + np.sum(null[metric] >= observed[metric]))
                    / (spec.rotation_draws + 1)
                )
                cells.append(
                    {
                        "family": family,
                        "split": split,
                        "arm": arm,
                        "metric": metric,
                        "rank": template.rank,
                        "observed": observed[metric],
                        "null_mean": null_mean,
                        "delta": delta,
                        "bootstrap_delta_low": delta_low,
                        "raw_rotation_p": raw_p,
                        "exact_intersection_rank": observed[
                            "exact_intersection_rank"
                        ],
                    }
                )
                nulls[(split, arm, metric)] = null[metric]
    rank_sensitivity = pd.DataFrame(rank_sensitivity_rows)
    rank_sensitivity["max_rank_haar_p"] = np.nan
    for (split, metric), group in rank_sensitivity.groupby(
        ["split", "metric"],
        sort=False,
    ):
        standardized_nulls = []
        standardized_observed = []
        row_indices = []
        for index, row in group.iterrows():
            null = rank_nulls[(split, int(row["rank"]), metric)]
            standard = max(float(null.std(ddof=1)), 1e-12)
            standardized_nulls.append((null - float(null.mean())) / standard)
            standardized_observed.append(
                (float(row["observed"]) - float(null.mean())) / standard
            )
            row_indices.append(index)
        maxima = np.max(np.vstack(standardized_nulls), axis=0)
        for index, value in zip(row_indices, standardized_observed):
            rank_sensitivity.loc[index, "max_rank_haar_p"] = float(
                (1 + np.sum(maxima >= value)) / (len(maxima) + 1)
            )
    return {
        "family": family,
        "status": (
            "ORIENTATION_AUDIT_READY"
            if d0_resolved
            else "D0_ORIENTATION_UNDERRESOLVED"
        ),
        "epsilon": epsilon,
        "epsilon_draw_mean": float(epsilon_draws.mean()),
        "rank": template.rank,
        "effective_rank_template": float(
            1.0 / np.sum(template.weights**2)
        ),
        "d0_internal": d0_internal,
        "cells": pd.DataFrame(cells),
        "rank_sensitivity": rank_sensitivity,
        "nulls": nulls,
    }


def add_max_haar_adjustment(
    family_results: list[dict[str, Any]],
) -> pd.DataFrame:
    """Add max-Haar p-values across families and registered arms/metrics."""
    frames = [result["cells"] for result in family_results if not result["cells"].empty]
    if not frames:
        return pd.DataFrame()
    cells = pd.concat(frames, ignore_index=True)
    cells["max_haar_p"] = np.nan
    for split in ("D1", "D2"):
        subset = cells.loc[cells["split"].eq(split)]
        z_nulls = []
        row_indices = []
        z_observed = []
        for index, row in subset.iterrows():
            result = next(
                value for value in family_results if value["family"] == row["family"]
            )
            null = result["nulls"][(split, row["arm"], row["metric"])]
            standard = max(float(null.std(ddof=1)), 1e-12)
            z_nulls.append((null - float(null.mean())) / standard)
            z_observed.append(
                (float(row["observed"]) - float(null.mean())) / standard
            )
            row_indices.append(index)
        maxima = np.max(np.vstack(z_nulls), axis=0)
        for index, value in zip(row_indices, z_observed):
            cells.loc[index, "max_haar_p"] = float(
                (1 + np.sum(maxima >= value)) / (len(maxima) + 1)
            )
    return cells
