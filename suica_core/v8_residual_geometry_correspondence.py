"""Axis-free correspondence tests for opportunity-filtered V8 residuals.

The module compares two technical text replicates through author-by-author
relation matrices. It deliberately avoids factor rotation and construct names:
the estimand is whether the same author set induces reproducible relational
geometry after a frozen opportunity filtration.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from suica_core.v8_realtext_relation_field import stable_bucket


@dataclass(frozen=True)
class ResidualGeometrySpec:
    """Frozen budgets and scales for residual geometry correspondence."""

    d0_null_draws: int = 999
    test_null_draws: int = 1999
    bootstrap_draws: int = 999
    bandwidth_multipliers: tuple[float, ...] = (0.5, 1.0, 2.0)
    neighborhood_fractions: tuple[float, ...] = (0.05, 0.10, 0.20)
    nuisance_kernel_ridge: float = 0.10
    minimum_context_authors: int = 8
    seed: int = 20260827

    def __post_init__(self) -> None:
        if min(self.d0_null_draws, self.test_null_draws) < 99:
            raise ValueError("Null budgets must be at least 99.")
        if self.bootstrap_draws < 99:
            raise ValueError("bootstrap_draws must be at least 99.")
        if not self.bandwidth_multipliers or any(
            value <= 0 for value in self.bandwidth_multipliers
        ):
            raise ValueError("bandwidth multipliers must be positive.")
        if not self.neighborhood_fractions or any(
            value <= 0 or value >= 1
            for value in self.neighborhood_fractions
        ):
            raise ValueError("neighborhood fractions must lie in (0, 1).")
        if self.nuisance_kernel_ridge <= 0:
            raise ValueError("nuisance_kernel_ridge must be positive.")
        if self.minimum_context_authors < 4:
            raise ValueError("minimum_context_authors must be at least four.")


def _squared_distances(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    norms = np.sum(matrix**2, axis=1, keepdims=True)
    return np.maximum(norms + norms.T - 2.0 * matrix @ matrix.T, 0.0)


def _center_kernel(kernel: np.ndarray) -> np.ndarray:
    matrix = np.asarray(kernel, dtype=float)
    return (
        matrix
        - matrix.mean(axis=0, keepdims=True)
        - matrix.mean(axis=1, keepdims=True)
        + matrix.mean()
    )


def _u_center_kernel(kernel: np.ndarray) -> np.ndarray:
    """U-center a relation matrix so self-similarity cannot drive alignment."""
    matrix = np.asarray(kernel, dtype=float).copy()
    count = len(matrix)
    if count < 4:
        raise ValueError("U-centering requires at least four observations.")
    np.fill_diagonal(matrix, 0.0)
    row_sum = matrix.sum(axis=1)
    total = float(row_sum.sum())
    result = (
        matrix
        - row_sum[:, None] / (count - 2)
        - row_sum[None, :] / (count - 2)
        + total / ((count - 1) * (count - 2))
    )
    np.fill_diagonal(result, 0.0)
    return 0.5 * (result + result.T)


def _kernel_residual_maker(
    nuisance: np.ndarray,
    *,
    ridge: float,
) -> np.ndarray:
    profile = np.asarray(nuisance, dtype=float)
    count = len(profile)
    dimensions = max(profile.shape[1], 1)
    kernel = _center_kernel(profile @ profile.T / dimensions)
    regularized = kernel + ridge * count * np.eye(count)
    return np.eye(count) - kernel @ np.linalg.solve(
        regularized,
        np.eye(count),
    )


def _conditioned_kernel(
    values: np.ndarray,
    nuisance: np.ndarray,
    *,
    kind: str,
    bandwidth: float | None,
    ridge: float,
) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    if kind == "linear":
        kernel = matrix @ matrix.T / max(matrix.shape[1], 1)
    elif kind == "rbf":
        if bandwidth is None or bandwidth <= 0:
            raise ValueError("RBF kernels require a positive bandwidth.")
        kernel = np.exp(
            -_squared_distances(matrix) / (2.0 * bandwidth**2)
        )
    else:
        raise ValueError(f"Unknown kernel kind: {kind}")
    centered = _center_kernel(kernel)
    maker = _kernel_residual_maker(nuisance, ridge=ridge)
    result = maker @ centered @ maker
    return 0.5 * (result + result.T)


def _kernel_distances(kernel: np.ndarray) -> np.ndarray:
    diagonal = np.diag(kernel)
    return np.sqrt(
        np.maximum(
            diagonal[:, None] + diagonal[None, :] - 2.0 * kernel,
            0.0,
        )
    )


def _neighbor_adjacency(
    distances: np.ndarray,
    *,
    fraction: float,
) -> np.ndarray:
    count = len(distances)
    neighbors = min(max(int(round(fraction * (count - 1))), 1), count - 1)
    work = np.asarray(distances, dtype=float).copy()
    np.fill_diagonal(work, np.inf)
    selected = np.argpartition(
        work,
        kth=neighbors - 1,
        axis=1,
    )[:, :neighbors]
    adjacency = np.zeros((count, count), dtype=float)
    adjacency[np.arange(count)[:, None], selected] = 1.0
    return adjacency


def _neighborhood_signature(
    contexts: np.ndarray,
    *,
    fraction: float,
    minimum_context_authors: int,
) -> str:
    labels = np.asarray(contexts).astype(str)
    values = []
    for context in np.unique(labels):
        count = int(np.sum(labels == context))
        if count < minimum_context_authors:
            continue
        neighbors = min(
            max(int(round(fraction * (count - 1))), 1),
            count - 1,
        )
        values.append(f"{context}:{neighbors}")
    return "|".join(values)


def _block_center(
    matrix: np.ndarray,
    contexts: np.ndarray,
) -> np.ndarray:
    result = np.zeros_like(matrix, dtype=float)
    labels = np.asarray(contexts).astype(str)
    for context in np.unique(labels):
        indices = np.flatnonzero(labels == context)
        block = matrix[np.ix_(indices, indices)]
        result[np.ix_(indices, indices)] = _center_kernel(block)
    return result


def _block_u_center(
    matrix: np.ndarray,
    contexts: np.ndarray,
) -> np.ndarray:
    result = np.zeros_like(matrix, dtype=float)
    labels = np.asarray(contexts).astype(str)
    for context in np.unique(labels):
        indices = np.flatnonzero(labels == context)
        block = matrix[np.ix_(indices, indices)]
        result[np.ix_(indices, indices)] = _u_center_kernel(block)
    return result


def _alignment(left: np.ndarray, right: np.ndarray) -> float:
    denominator = float(
        np.linalg.norm(left, ord="fro")
        * np.linalg.norm(right, ord="fro")
    )
    if denominator <= 1e-12:
        return float("nan")
    return float(np.sum(left * right) / denominator)


def frozen_bandwidth(
    values: np.ndarray,
    metadata: pd.DataFrame,
    *,
    split: str = "D0",
) -> float:
    """Return the pooled within-context D0 median residual distance."""
    mask = metadata["split"].eq(split).to_numpy()
    labels = metadata.loc[mask, "context"].astype(str).to_numpy()
    selected = np.asarray(values[mask], dtype=float)
    distances: list[np.ndarray] = []
    for context in np.unique(labels):
        indices = np.flatnonzero(labels == context)
        if len(indices) < 2:
            continue
        for replicate in range(2):
            matrix = np.sqrt(
                _squared_distances(selected[indices, replicate])
            )
            upper = matrix[np.triu_indices(len(matrix), k=1)]
            distances.append(upper[upper > 1e-12])
    pooled = np.concatenate([item for item in distances if len(item)])
    if not len(pooled):
        raise ValueError("No positive D0 within-context distances.")
    return float(np.median(pooled))


def relational_matrices(
    values: np.ndarray,
    nuisance: np.ndarray,
    contexts: np.ndarray,
    *,
    bandwidth: float,
    spec: ResidualGeometrySpec,
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Build conditioned global kernels and local graphs per replicate."""
    residual = np.asarray(values, dtype=float)
    profiles = np.asarray(nuisance, dtype=float)
    labels = np.asarray(contexts).astype(str)
    if residual.ndim != 3 or residual.shape[1] != 2:
        raise ValueError("values must have shape author x 2 x dimensions.")
    if profiles.ndim != 3 or profiles.shape[:2] != residual.shape[:2]:
        raise ValueError("nuisance must align with values.")
    result: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    linear = [np.zeros((len(residual), len(residual))) for _ in range(2)]
    rbfs = {
        multiplier: [
            np.zeros((len(residual), len(residual)))
            for _ in range(2)
        ]
        for multiplier in spec.bandwidth_multipliers
    }
    local = {
        fraction: [
            np.zeros((len(residual), len(residual)))
            for _ in range(2)
        ]
        for fraction in spec.neighborhood_fractions
    }
    for context in np.unique(labels):
        indices = np.flatnonzero(labels == context)
        if len(indices) < spec.minimum_context_authors:
            continue
        conditioned_linear = []
        for replicate in range(2):
            kernel = _conditioned_kernel(
                residual[indices, replicate],
                profiles[indices, replicate],
                kind="linear",
                bandwidth=None,
                ridge=spec.nuisance_kernel_ridge,
            )
            linear[replicate][np.ix_(indices, indices)] = (
                _u_center_kernel(kernel)
            )
            conditioned_linear.append(kernel)
            for multiplier in spec.bandwidth_multipliers:
                rbf = _conditioned_kernel(
                    residual[indices, replicate],
                    profiles[indices, replicate],
                    kind="rbf",
                    bandwidth=bandwidth * multiplier,
                    ridge=spec.nuisance_kernel_ridge,
                )
                rbfs[multiplier][replicate][np.ix_(indices, indices)] = (
                    _u_center_kernel(rbf)
                )
        for fraction in spec.neighborhood_fractions:
            for replicate in range(2):
                adjacency = _neighbor_adjacency(
                    _kernel_distances(conditioned_linear[replicate]),
                    fraction=fraction,
                )
                local[fraction][replicate][
                    np.ix_(indices, indices)
                ] = adjacency
    result["linear_krc"] = (linear[0], linear[1])
    for multiplier, matrices in rbfs.items():
        result[f"rbf_krc_{multiplier:g}"] = (
            matrices[0],
            matrices[1],
        )
    for fraction, matrices in local.items():
        result[f"local_overlap_{fraction:g}"] = (
            matrices[0],
            matrices[1],
        )
    return result


def _permutation_order(
    contexts: np.ndarray,
    *,
    rng: np.random.Generator,
) -> np.ndarray:
    labels = np.asarray(contexts).astype(str)
    order = np.arange(len(labels))
    for context in np.unique(labels):
        indices = np.flatnonzero(labels == context)
        order[indices] = rng.permutation(indices)
    return order


def _metric_values(
    matrices: dict[str, tuple[np.ndarray, np.ndarray]],
    *,
    order: np.ndarray | None = None,
) -> dict[str, float]:
    result = {}
    for name, (left, right) in matrices.items():
        candidate = (
            right
            if order is None
            else right[np.ix_(order, order)]
        )
        result[name] = _alignment(left, candidate)
    return result


def _bootstrap_metrics(
    matrices: dict[str, tuple[np.ndarray, np.ndarray]],
    contexts: np.ndarray,
    *,
    draws: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    labels = np.asarray(contexts).astype(str)
    groups = {
        context: np.flatnonzero(labels == context)
        for context in np.unique(labels)
    }
    samples = {
        name: np.empty(draws, dtype=float)
        for name in matrices
    }
    for draw in range(draws):
        indices = np.concatenate(
            [
                rng.choice(group, size=len(group), replace=True)
                for group in groups.values()
            ]
        )
        sampled_contexts = labels[indices]
        for name, (left, right) in matrices.items():
            sampled_left = left[np.ix_(indices, indices)]
            sampled_right = right[np.ix_(indices, indices)]
            if not name.startswith("local_overlap"):
                sampled_left = _block_u_center(
                    sampled_left,
                    sampled_contexts,
                )
                sampled_right = _block_u_center(
                    sampled_right,
                    sampled_contexts,
                )
            samples[name][draw] = _alignment(
                sampled_left,
                sampled_right,
            )
    return samples


def _null_metrics(
    matrices: dict[str, tuple[np.ndarray, np.ndarray]],
    contexts: np.ndarray,
    *,
    draws: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    null = {
        name: np.empty(draws, dtype=float)
        for name in matrices
    }
    for draw in range(draws):
        order = _permutation_order(contexts, rng=rng)
        values = _metric_values(matrices, order=order)
        for name, value in values.items():
            null[name][draw] = value
    return null


def _maximum_t(
    rows: pd.DataFrame,
    nulls: dict[str, np.ndarray],
) -> pd.DataFrame:
    output = rows.copy()
    output["max_t_p"] = np.nan
    selected = output.loc[output["split"].isin(["D1", "D2"])]
    if selected.empty:
        return output
    standardized = []
    observed_z = []
    for row in selected.itertuples():
        values = nulls[str(row.cell_id)]
        standard = max(float(values.std(ddof=1)), 1e-12)
        standardized.append((values - values.mean()) / standard)
        observed_z.append((float(row.observed) - values.mean()) / standard)
    maximum = np.max(np.vstack(standardized), axis=0)
    for cell_id, value in zip(
        selected["cell_id"],
        observed_z,
        strict=True,
    ):
        output.loc[output["cell_id"].eq(cell_id), "max_t_p"] = float(
            (1 + np.sum(maximum >= value)) / (len(maximum) + 1)
        )
    return output


def _maximum_t_delta(
    rows: pd.DataFrame,
    delta_nulls: dict[str, np.ndarray],
) -> pd.DataFrame:
    output = rows.copy()
    output["delta_max_t_p"] = np.nan
    selected = output.loc[
        output["split"].isin(["D1", "D2"])
        & output["metric"].str.startswith("rbf_krc")
    ]
    if selected.empty:
        return output
    standardized = []
    observed_z = []
    for row in selected.itertuples():
        values = delta_nulls[str(row.cell_id)]
        standard = max(float(values.std(ddof=1)), 1e-12)
        standardized.append((values - values.mean()) / standard)
        observed_z.append(
            float(row.delta_excess_vs_linear) / standard
        )
    maximum = np.max(np.vstack(standardized), axis=0)
    for cell_id, value in zip(
        selected["cell_id"],
        observed_z,
        strict=True,
    ):
        output.loc[output["cell_id"].eq(cell_id), "delta_max_t_p"] = float(
            (1 + np.sum(maximum >= value)) / (len(maximum) + 1)
        )
    return output


def _corpus_status(cells: pd.DataFrame, corpus: str) -> str:
    selected = cells.loc[
        cells["corpus"].eq(corpus)
        & cells["split"].isin(["D1", "D2"])
    ]

    def passes(metric: str, *, delta: bool = False) -> bool:
        rows = selected.loc[selected["metric"].eq(metric)]
        if len(rows) != 2:
            return False
        columns = (
            (
                "delta_excess_vs_linear",
                "delta_max_t_p",
                "delta_bootstrap_lcb",
            )
            if delta
            else ("excess", "max_t_p", "bootstrap_lcb")
        )
        return bool(
            rows[columns[0]].gt(0).all()
            and rows[columns[1]].le(0.05).all()
            and rows[columns[2]].gt(0).all()
        )

    nonlinear = [
        metric
        for metric in selected["metric"].unique()
        if metric.startswith("rbf_krc")
        and passes(metric)
        and passes(metric, delta=True)
    ]
    if nonlinear:
        return "NONLINEAR_RESIDUAL_GEOMETRY"
    if passes("linear_krc"):
        return "DISTRIBUTED_LINEAR_GEOMETRY"
    passed_rbf = sorted(
        float(metric.rsplit("_", 1)[-1])
        for metric in selected["metric"].unique()
        if metric.startswith("rbf_krc") and passes(metric)
    )
    if len(passed_rbf) >= 2:
        return "AXIS_FREE_MULTI_SCALE_KERNEL_CORRESPONDENCE"
    if passed_rbf:
        return (
            "AXIS_FREE_SHORT_SCALE_KERNEL_CORRESPONDENCE"
            if passed_rbf[0] < 1.0
            else "AXIS_FREE_SINGLE_SCALE_KERNEL_CORRESPONDENCE"
        )
    fractions = list(
        sorted(
            {
                float(metric.rsplit("_", 1)[-1])
                for metric in selected["metric"].unique()
                if metric.startswith("local_overlap")
                and passes(metric)
            }
        )
    )
    registered = list(sorted(set(map(float, fractions))))
    all_fractions = list(
        sorted(
            {
                float(metric.rsplit("_", 1)[-1])
                for metric in selected["metric"].unique()
                if metric.startswith("local_overlap")
            }
        )
    )
    for left, right in zip(all_fractions, all_fractions[1:]):
        if left in registered and right in registered:
            distinct = True
            for split in ("D1", "D2"):
                signatures = selected.loc[
                    selected["split"].eq(split)
                    & selected["metric"].isin(
                        [
                            f"local_overlap_{left:g}",
                            f"local_overlap_{right:g}",
                        ]
                    ),
                    "scale_signature",
                ].astype(str)
                if len(signatures) != 2 or signatures.nunique() != 2:
                    distinct = False
                    break
            if distinct:
                return "PERSISTENT_LOCAL_RESIDUAL_GEOMETRY"
    return "SCALAR_CONCORDANCE_ONLY"


def evaluate_residual_geometry(
    panels: dict[
        str,
        tuple[pd.DataFrame, np.ndarray, np.ndarray],
    ],
    *,
    bandwidth_by_corpus: dict[str, float],
    spec: ResidualGeometrySpec,
) -> dict[str, Any]:
    """Evaluate axis-free residual geometry on D0, D1, and D2."""
    rows: list[dict[str, Any]] = []
    nulls: dict[str, np.ndarray] = {}
    delta_nulls: dict[str, np.ndarray] = {}
    for corpus, (metadata, residual, nuisance) in panels.items():
        for split in ("D0", "D1", "D2"):
            mask = metadata["split"].eq(split).to_numpy()
            contexts = metadata.loc[mask, "context"].astype(str).to_numpy()
            if len(contexts) < spec.minimum_context_authors:
                continue
            matrices = relational_matrices(
                residual[mask],
                nuisance[mask],
                contexts,
                bandwidth=bandwidth_by_corpus[corpus],
                spec=spec,
            )
            observed = _metric_values(matrices)
            draws = (
                spec.d0_null_draws
                if split == "D0"
                else spec.test_null_draws
            )
            seed = (
                spec.seed
                + stable_bucket(
                    f"{corpus}-{split}",
                    salt="v8-residual-geometry-null",
                    modulus=2**31 - 1,
                )
            )
            null = _null_metrics(
                matrices,
                contexts,
                draws=draws,
                rng=np.random.default_rng(seed),
            )
            bootstrap = (
                {}
                if split == "D0"
                else _bootstrap_metrics(
                    matrices,
                    contexts,
                    draws=spec.bootstrap_draws,
                    rng=np.random.default_rng(seed + 1),
                )
            )
            linear_excess = (
                observed["linear_krc"] - null["linear_krc"].mean()
            )
            for metric, value in observed.items():
                cell_id = f"{corpus}::{split}::{metric}"
                nulls[cell_id] = null[metric]
                null_mean = float(null[metric].mean())
                excess = float(value - null_mean)
                lower = float("nan")
                delta = float("nan")
                delta_lower = float("nan")
                if split != "D0":
                    samples = bootstrap[metric]
                    finite = samples[np.isfinite(samples)]
                    if len(finite) >= max(20, int(0.90 * len(samples))):
                        centered = finite - finite.mean()
                        lower = float(
                            excess + np.quantile(centered, 0.025)
                        )
                if metric.startswith("rbf_krc"):
                    delta = float(excess - linear_excess)
                    delta_null = null[metric] - null["linear_krc"]
                    delta_nulls[cell_id] = delta_null
                    if split != "D0":
                        samples = (
                            bootstrap[metric] - bootstrap["linear_krc"]
                        )
                        finite = samples[np.isfinite(samples)]
                        if len(finite) >= max(
                            20,
                            int(0.90 * len(samples)),
                        ):
                            centered_delta = finite - finite.mean()
                            delta_lower = float(
                                delta
                                + np.quantile(centered_delta, 0.025)
                            )
                rows.append(
                    {
                        "cell_id": cell_id,
                        "corpus": corpus,
                        "split": split,
                        "metric": metric,
                        "scale_signature": (
                            _neighborhood_signature(
                                contexts,
                                fraction=float(metric.rsplit("_", 1)[-1]),
                                minimum_context_authors=(
                                    spec.minimum_context_authors
                                ),
                            )
                            if metric.startswith("local_overlap")
                            else ""
                        ),
                        "authors": int(mask.sum()),
                        "observed": value,
                        "null_mean": null_mean,
                        "excess": excess,
                        "raw_p": float(
                            (1 + np.sum(null[metric] >= value))
                            / (len(null[metric]) + 1)
                        ),
                        "bootstrap_lcb": lower,
                        "delta_excess_vs_linear": delta,
                        "delta_bootstrap_lcb": delta_lower,
                    }
                )
    cells = _maximum_t(pd.DataFrame(rows), nulls)
    cells = _maximum_t_delta(cells, delta_nulls)
    status = {
        corpus: _corpus_status(cells, corpus)
        for corpus in panels
    }
    return {
        "status": status,
        "cells": cells,
    }
