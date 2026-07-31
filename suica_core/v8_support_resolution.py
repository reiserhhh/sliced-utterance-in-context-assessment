"""Corpus-local replicated-support resolution frontier for SUICA V8."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from suica_core.v8_realtext_relation_field import (
    CorpusFeaturePanel,
    stable_bucket,
)
from suica_core.v8_support_containment import (
    _objective,
    _robust_standardizer,
    _rotation_p,
    _spectral_scale,
    _split_raw,
    _stable_indices,
    replicated_density,
    soft_capacity_filter,
)


@dataclass(frozen=True)
class SupportResolutionSpec:
    """Frozen grid and uncertainty budgets for the local frontier."""

    capacities: tuple[int, ...] = (2, 4, 8, 16, 24, 32, 48, 64, 96, 128)
    tau_multipliers: tuple[float, ...] = (0.25, 0.5, 1.0, 2.0, 4.0)
    bootstrap_draws: int = 199
    rotation_draws: int = 99
    minimum_fit_authors: int = 24
    minimum_confirmation_authors: int = 32
    minimum_admissible_tau_fraction: float = 0.40
    denominator_floor: float = 1e-6
    seed: int = 20260807

    def __post_init__(self) -> None:
        if not self.capacities or any(value < 1 for value in self.capacities):
            raise ValueError("capacities must be positive.")
        if not self.tau_multipliers or any(
            value <= 0 for value in self.tau_multipliers
        ):
            raise ValueError("tau_multipliers must be positive.")
        if self.bootstrap_draws < 19 or self.rotation_draws < 19:
            raise ValueError("Uncertainty budgets must be at least 19.")
        if not 0 < self.minimum_admissible_tau_fraction <= 1:
            raise ValueError("minimum_admissible_tau_fraction must be in (0, 1].")


def _fit_local_support(
    raw: np.ndarray,
    ids: np.ndarray,
    *,
    seed: int,
) -> dict[str, Any]:
    order = _stable_indices(ids, len(ids), salt=f"v8-resolution-d0-{seed}")
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
        "fit_authors": int(len(fit)),
        "calibration_authors": int(len(calibration)),
    }


def _bank(
    density: np.ndarray,
    *,
    capacities: tuple[int, ...],
    tau_multipliers: tuple[float, ...],
) -> list[dict[str, Any]]:
    dimension = density.shape[0]
    spectral_scale = _spectral_scale(density, density)
    result = []
    for capacity in capacities:
        if capacity >= dimension:
            continue
        for multiplier in tau_multipliers:
            tau = float(multiplier * spectral_scale)
            result.append(
                {
                    "capacity": int(capacity),
                    "tau_multiplier": float(multiplier),
                    "tau": tau,
                    "filter": soft_capacity_filter(density, capacity, tau),
                }
            )
    return result


def _cell_values(
    bank: list[dict[str, Any]],
    density: np.ndarray,
) -> list[dict[str, float]]:
    rows = []
    for cell in bank:
        capacity = int(cell["capacity"])
        tau = float(cell["tau"])
        baseline = capacity / density.shape[0]
        native_excess = (
            _objective(
                cell["filter"],
                density,
                capacity=capacity,
                tau=tau,
            )
            - baseline
        )
        oracle_filter = soft_capacity_filter(density, capacity, tau)
        oracle_excess = (
            _objective(
                oracle_filter,
                density,
                capacity=capacity,
                tau=tau,
            )
            - baseline
        )
        rows.append(
            {
                "capacity": capacity,
                "tau_multiplier": float(cell["tau_multiplier"]),
                "tau": tau,
                "native_excess": native_excess,
                "oracle_excess": oracle_excess,
                "resolution_ratio": (
                    float(native_excess / oracle_excess)
                    if oracle_excess > 1e-12
                    else float("nan")
                ),
            }
        )
    return rows


def _native_excess(
    cells: list[dict[str, Any]],
    density: np.ndarray,
) -> np.ndarray:
    values = np.empty(len(cells), dtype=float)
    for index, cell in enumerate(cells):
        capacity = int(cell["capacity"])
        values[index] = (
            _objective(
                cell["filter"],
                density,
                capacity=capacity,
                tau=float(cell["tau"]),
            )
            - capacity / density.shape[0]
        )
    return values


def _interval(values: list[float]) -> tuple[float, float]:
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if len(finite) < 10:
        return float("nan"), float("nan")
    return tuple(np.quantile(finite, (0.025, 0.975)).astype(float))


def evaluate_local_resolution(
    corpus: str,
    panel: CorpusFeaturePanel,
    family: str,
    *,
    spec: SupportResolutionSpec,
) -> dict[str, list[dict[str, Any]]]:
    """Estimate D0-calibrated local support resolution on D1 and D2."""
    d0_raw, d0_ids = _split_raw(panel, family, "D0")
    local = _fit_local_support(
        d0_raw,
        d0_ids,
        seed=spec.seed
        + stable_bucket(corpus, salt=f"resolution-{family}", modulus=100_000),
    )
    if (
        local["fit_authors"] < spec.minimum_fit_authors
        or local["calibration_authors"] < spec.minimum_fit_authors
    ):
        return {
            "cells": [],
            "frontier": [
                {
                    "corpus": corpus,
                    "family": family,
                    "split": "D0",
                    "status": "D0_RESOLUTION_UNDERRESOLVED",
                }
            ],
        }
    alignment, alignment_p = _rotation_p(
        local["fit_density"],
        local["calibration_density"],
        draws=spec.rotation_draws,
        seed=spec.seed
        + stable_bucket(corpus, salt=f"resolution-null-{family}", modulus=100_000),
    )
    bank = _bank(
        local["fit_density"],
        capacities=spec.capacities,
        tau_multipliers=spec.tau_multipliers,
    )
    calibration_cells = _cell_values(bank, local["calibration_density"])
    calibration_lookup = {
        (row["capacity"], row["tau_multiplier"]): row
        for row in calibration_cells
    }
    cell_rows: list[dict[str, Any]] = []
    frontier_rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(
        spec.seed
        + stable_bucket(corpus, salt=f"resolution-bootstrap-{family}", modulus=2**31 - 1)
    )
    for split in ("D1", "D2"):
        raw, _ids = _split_raw(panel, family, split)
        if len(raw) < spec.minimum_confirmation_authors:
            frontier_rows.append(
                {
                    "corpus": corpus,
                    "family": family,
                    "split": split,
                    "status": "CONFIRMATION_RESOLUTION_UNDERRESOLVED",
                    "n_authors": int(len(raw)),
                }
            )
            continue
        density, confirmation_rank, _ = replicated_density(
            raw,
            center=local["center"],
            scale=local["scale"],
        )
        observed_cells = _cell_values(bank, density)
        for row in observed_cells:
            calibration = calibration_lookup[
                (row["capacity"], row["tau_multiplier"])
            ]
            cell_rows.append(
                {
                    "corpus": corpus,
                    "family": family,
                    "split": split,
                    "n_authors": int(len(raw)),
                    "fit_effective_rank": local["fit_effective_rank"],
                    "calibration_effective_rank": local[
                        "calibration_effective_rank"
                    ],
                    "confirmation_effective_rank": confirmation_rank,
                    "d0_internal_hs": alignment,
                    "d0_internal_p": alignment_p,
                    "d0_calibration_native_excess": calibration[
                        "native_excess"
                    ],
                    "d0_admissible": int(
                        calibration["native_excess"] > spec.denominator_floor
                    ),
                    **row,
                }
            )
        bootstrap_by_capacity = {
            capacity: []
            for capacity in spec.capacities
            if capacity < density.shape[0]
        }
        for _ in range(spec.bootstrap_draws):
            draw = raw[rng.integers(0, len(raw), size=len(raw))]
            draw_density, _, _ = replicated_density(
                draw,
                center=local["center"],
                scale=local["scale"],
            )
            draw_values = _native_excess(bank, draw_density)
            for capacity in bootstrap_by_capacity:
                indices = [
                    index
                    for index, cell in enumerate(bank)
                    if cell["capacity"] == capacity
                    and calibration_lookup[
                        (cell["capacity"], cell["tau_multiplier"])
                    ]["native_excess"]
                    > spec.denominator_floor
                ]
                bootstrap_by_capacity[capacity].append(
                    float(np.mean(draw_values[indices]))
                    if indices
                    else float("nan")
                )

        rotation_by_capacity = {
            capacity: []
            for capacity in bootstrap_by_capacity
        }
        observed_by_capacity = {}
        rng_rotation = np.random.default_rng(
            spec.seed
            + stable_bucket(
                f"{corpus}-{family}-{split}",
                salt="resolution-rotation",
                modulus=2**31 - 1,
            )
        )
        for capacity in rotation_by_capacity:
            selected = [
                row
                for row in observed_cells
                if row["capacity"] == capacity
                and calibration_lookup[
                    (row["capacity"], row["tau_multiplier"])
                ]["native_excess"]
                > spec.denominator_floor
            ]
            observed_by_capacity[capacity] = (
                float(np.mean([row["native_excess"] for row in selected]))
                if selected
                else float("nan")
            )
        for _ in range(spec.rotation_draws):
            rotation, _ = np.linalg.qr(
                rng_rotation.normal(size=(density.shape[0], density.shape[0]))
            )
            rotated = rotation @ density @ rotation.T
            rotated_values = _native_excess(bank, rotated)
            for capacity in rotation_by_capacity:
                indices = [
                    index
                    for index, cell in enumerate(bank)
                    if cell["capacity"] == capacity
                    and calibration_lookup[
                        (cell["capacity"], cell["tau_multiplier"])
                    ]["native_excess"]
                    > spec.denominator_floor
                ]
                rotation_by_capacity[capacity].append(
                    float(np.mean(rotated_values[indices]))
                    if indices
                    else float("nan")
                )

        required_tau = int(
            np.ceil(
                spec.minimum_admissible_tau_fraction
                * len(spec.tau_multipliers)
            )
        )
        null_columns = [
            np.asarray(rotation_by_capacity[capacity], dtype=float)
            for capacity in sorted(rotation_by_capacity)
        ]
        max_null = (
            np.nanmax(np.column_stack(null_columns), axis=1)
            if null_columns
            else np.asarray([], dtype=float)
        )
        max_null = max_null[np.isfinite(max_null)]
        for capacity in bootstrap_by_capacity:
            selected = [
                row
                for row in observed_cells
                if row["capacity"] == capacity
                and calibration_lookup[
                    (row["capacity"], row["tau_multiplier"])
                ]["native_excess"]
                > spec.denominator_floor
            ]
            interval = _interval(bootstrap_by_capacity[capacity])
            observed = observed_by_capacity[capacity]
            rotation_p = (
                float(
                    (1 + np.sum(max_null >= observed))
                    / (len(max_null) + 1)
                )
                if len(max_null) and np.isfinite(observed)
                else float("nan")
            )
            frontier_rows.append(
                {
                    "corpus": corpus,
                    "family": family,
                    "split": split,
                    "status": (
                        "RESOLUTION_ESTIMATED"
                        if len(selected) >= required_tau
                        else "TAU_GRID_UNDERRESOLVED"
                    ),
                    "n_authors": int(len(raw)),
                    "capacity": int(capacity),
                    "capacity_fraction": float(capacity / density.shape[0]),
                    "admissible_tau_count": int(len(selected)),
                    "required_tau_count": int(required_tau),
                    "native_excess": observed,
                    "native_excess_ci_low": interval[0],
                    "native_excess_ci_high": interval[1],
                    "resolution_ratio": (
                        float(
                            np.mean(
                                [
                                    row["resolution_ratio"]
                                    for row in selected
                                    if np.isfinite(row["resolution_ratio"])
                                ]
                            )
                        )
                        if selected
                        else float("nan")
                    ),
                    "rotation_p": rotation_p,
                    "rotation_scope": "WITHIN_CORPUS_FAMILY_SPLIT_MAX_CAPACITY",
                    "d0_internal_hs": alignment,
                    "d0_internal_p": alignment_p,
                    "fit_effective_rank": local["fit_effective_rank"],
                    "confirmation_effective_rank": confirmation_rank,
                }
            )
    return {"cells": cell_rows, "frontier": frontier_rows}


def classify_frontier(rows: pd.DataFrame) -> dict[str, Any]:
    """Summarize capacities confirmed in both D1 and D2."""
    if rows.empty:
        return {
            "decision": "LOCAL_RESOLUTION_UNDERRESOLVED",
            "confirmed_capacities": [],
        }
    confirmed = []
    for capacity, group in rows.groupby("capacity", sort=True):
        if (
            len(group) == 2
            and set(group["split"]) == {"D1", "D2"}
            and group["status"].eq("RESOLUTION_ESTIMATED").all()
            and (group["native_excess_ci_low"] > 0).all()
            and (group["rotation_q"] <= 0.05).all()
            and (group["d0_internal_p"] <= 0.05).all()
        ):
            confirmed.append(int(capacity))
    if not confirmed:
        decision = "DISTRIBUTED_SUPPORT_NOT_CAPACITY_RESOLVED"
    else:
        decision = "REPLICATED_CAPACITY_FRONTIER"
    return {
        "decision": decision,
        "confirmed_capacities": confirmed,
        "minimum_confirmed_capacity": min(confirmed) if confirmed else None,
        "maximum_confirmed_capacity": max(confirmed) if confirmed else None,
    }
