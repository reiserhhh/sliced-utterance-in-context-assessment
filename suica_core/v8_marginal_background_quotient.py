"""Conditional marginal-background quotient for the order-free V8 M family.

The quotient compares natural author event sets with pseudo-author sets built
from the same corpus, context, event slot, and local length neighborhood. It
does not delete text components or assign psychological meaning.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from suica_core.v8_event_set_composition_knockout import (
    EventTensor,
    pseudo_set_reallocation,
)
from suica_core.v8_realtext_relation_field import (
    RealTextRelationSpec,
    frozen_random_directions,
    replicated_covariance,
)


BLOCK_NAMES = ("mean", "variance", "rff", "quantiles")
VIEW_NAMES = (
    "M_all",
    "location_mean",
    "strict_shape",
    "dispersion_variance",
    "higher_shape",
)


@dataclass(frozen=True)
class MarginalQuotientSpec:
    """Frozen budgets and numerical choices for the M-family quotient."""

    background_draws: int = 499
    null_draws: int = 1999
    diagnostic_null_draws: int = 199
    bootstrap_draws: int = 999
    bootstrap_reference_worlds: int = 64
    local_length_block: int = 16
    covariance_shrinkage: float = 0.10
    covariance_ridge: float = 1e-7
    minimum_coverage: float = 0.90
    seed: int = 20260817

    def __post_init__(self) -> None:
        if self.background_draws < 49:
            raise ValueError("background_draws must be at least 49.")
        if self.null_draws < 99:
            raise ValueError("null_draws must be at least 99.")
        if not 49 <= self.diagnostic_null_draws <= self.null_draws:
            raise ValueError(
                "diagnostic_null_draws must lie between 49 and null_draws."
            )
        if self.bootstrap_draws < 99:
            raise ValueError("bootstrap_draws must be at least 99.")
        if self.bootstrap_reference_worlds < 8:
            raise ValueError("bootstrap_reference_worlds must be at least eight.")
        if self.local_length_block < 4:
            raise ValueError("local_length_block must be at least four.")
        if not 0.0 <= self.covariance_shrinkage <= 1.0:
            raise ValueError("covariance_shrinkage must lie in [0, 1].")
        if self.covariance_ridge <= 0:
            raise ValueError("covariance_ridge must be positive.")
        if not 0.0 < self.minimum_coverage <= 1.0:
            raise ValueError("minimum_coverage must lie in (0, 1].")


@dataclass(frozen=True)
class FrozenMarginalBackground:
    """D0-frozen conditional centers and blockwise whitening maps."""

    centers: dict[tuple[str, int, str], np.ndarray]
    whiteners: dict[str, np.ndarray]
    block_dimensions: dict[str, int]
    coverage: float
    condition_numbers: dict[str, float]


def marginal_feature_blocks_batch(
    paths: np.ndarray,
    *,
    marginal_directions: np.ndarray,
) -> dict[str, np.ndarray]:
    """Vectorize the exact order-free M feature map for four-event paths."""
    values = np.asarray(paths, dtype=float)
    if values.ndim != 3 or values.shape[1] < 2:
        raise ValueError(
            "paths must have shape author x events x event_dimension "
            "with at least two events."
        )
    mean = values.mean(axis=1)
    centered = values - mean[:, None, :]
    variance = np.mean(centered**2, axis=1)
    phase = centered @ marginal_directions.T
    rff = np.concatenate(
        [
            np.mean(np.cos(phase), axis=1),
            np.mean(np.sin(phase), axis=1),
        ],
        axis=1,
    )
    projections = values @ marginal_directions.T
    quantiles = np.quantile(
        projections,
        (0.25, 0.50, 0.75),
        axis=1,
    ).transpose(1, 0, 2).reshape(len(values), -1)
    return {
        "mean": mean,
        "variance": variance,
        "rff": rff,
        "quantiles": quantiles,
    }


def tensor_feature_blocks(
    vectors: np.ndarray,
    *,
    marginal_directions: np.ndarray,
) -> dict[str, np.ndarray]:
    """Return M blocks as author x technical-replicate x dimensions."""
    return {
        block: np.stack(
            [
                marginal_feature_blocks_batch(
                    vectors[:, offset::2, :],
                    marginal_directions=marginal_directions,
                )[block]
                for offset in (0, 1)
            ],
            axis=1,
        )
        for block in BLOCK_NAMES
    }


def _inverse_sqrt_covariance(
    covariance: np.ndarray,
    *,
    shrinkage: float,
    ridge: float,
) -> tuple[np.ndarray, float]:
    matrix = 0.5 * (np.asarray(covariance, dtype=float) + covariance.T)
    dimension = matrix.shape[0]
    average = max(float(np.trace(matrix)) / max(dimension, 1), ridge)
    regularized = (
        (1.0 - shrinkage) * matrix
        + shrinkage * average * np.eye(dimension)
        + ridge * average * np.eye(dimension)
    )
    values, vectors = np.linalg.eigh(regularized)
    floor = ridge * max(float(np.max(values)), average)
    values = np.maximum(values, floor)
    condition = float(np.max(values) / max(float(np.min(values)), 1e-15))
    return (vectors * (1.0 / np.sqrt(values))) @ vectors.T, condition


def fit_marginal_background(
    tensor: EventTensor,
    *,
    marginal_directions: np.ndarray,
    spec: MarginalQuotientSpec,
    rng: np.random.Generator,
    reallocator: Callable[..., tuple[np.ndarray, pd.DataFrame]] = (
        pseudo_set_reallocation
    ),
) -> tuple[FrozenMarginalBackground, pd.DataFrame]:
    """Fit conditional pseudo-author centers and block covariance on D0 only."""
    metadata = tensor.metadata.reset_index(drop=True)
    mask = metadata["split"].eq("D0").to_numpy()
    contexts = metadata.loc[mask, "context"].astype(str).to_numpy()
    expected_cells = {
        (str(context), replicate, block)
        for context in np.unique(contexts)
        for replicate in range(2)
        for block in BLOCK_NAMES
    }
    totals: dict[tuple[str, int, str], np.ndarray] = {}
    counts: dict[tuple[str, int, str], int] = {}
    second_moments: dict[str, np.ndarray] = {}
    block_counts: dict[str, int] = {block: 0 for block in BLOCK_NAMES}
    diagnostic_rows = []
    for draw in range(spec.background_draws):
        pseudo, diagnostics = reallocator(
            tensor,
            block_size=spec.local_length_block,
            rng=rng,
        )
        features = tensor_feature_blocks(
            pseudo[mask],
            marginal_directions=marginal_directions,
        )
        diagnostic_rows.append(
            {
                "stage": "background",
                "draw": draw,
                "same_author": int(diagnostics["same_author"].sum()),
                "total_assignments": int(diagnostics["block_size"].sum()),
                "identity_blocks": int(
                    diagnostics.get(
                        "identity_block",
                        pd.Series(dtype=int),
                    ).sum()
                ),
                "mean_absolute_length_difference": float(
                    np.average(
                        diagnostics["mean_absolute_length_difference"],
                        weights=diagnostics["block_size"],
                    )
                ),
            }
        )
        for block, values in features.items():
            flattened = values.reshape(-1, values.shape[-1])
            second_moments[block] = second_moments.get(
                block,
                np.zeros((values.shape[-1], values.shape[-1]), dtype=float),
            ) + flattened.T @ flattened
            block_counts[block] += len(flattened)
            for context in np.unique(contexts):
                context_mask = contexts == context
                for replicate in range(2):
                    key = (str(context), replicate, block)
                    value = values[context_mask, replicate]
                    totals[key] = totals.get(
                        key,
                        np.zeros(values.shape[-1], dtype=float),
                    ) + value.sum(axis=0)
                    counts[key] = counts.get(key, 0) + len(value)
    centers = {key: totals[key] / counts[key] for key in totals}
    observed_cells = set(centers)
    coverage = len(observed_cells & expected_cells) / max(len(expected_cells), 1)
    whiteners = {}
    condition_numbers = {}
    block_dimensions = {}
    for block in BLOCK_NAMES:
        centered_second = second_moments[block].copy()
        for key, center in centers.items():
            if key[2] != block:
                continue
            centered_second -= counts[key] * np.outer(center, center)
        covariance = centered_second / max(block_counts[block] - 1, 1)
        whiteners[block], condition_numbers[block] = _inverse_sqrt_covariance(
            covariance,
            shrinkage=spec.covariance_shrinkage,
            ridge=spec.covariance_ridge,
        )
        block_dimensions[block] = covariance.shape[0]
    return (
        FrozenMarginalBackground(
            centers=centers,
            whiteners=whiteners,
            block_dimensions=block_dimensions,
            coverage=float(coverage),
            condition_numbers=condition_numbers,
        ),
        pd.DataFrame(diagnostic_rows),
    )


def quotient_blocks(
    features: dict[str, np.ndarray],
    contexts: np.ndarray,
    background: FrozenMarginalBackground,
) -> dict[str, np.ndarray]:
    """Map M blocks to their D0-frozen conditional background quotient."""
    result: dict[str, np.ndarray] = {}
    for block, values in features.items():
        quotient = np.empty_like(values, dtype=float)
        for row, context in enumerate(map(str, contexts)):
            for replicate in range(2):
                key = (context, replicate, block)
                if key not in background.centers:
                    raise ValueError(f"No D0 background center for {key}.")
                quotient[row, replicate] = (
                    values[row, replicate] - background.centers[key]
                ) @ background.whiteners[block]
        result[block] = quotient
    return result


def quotient_views(
    blocks: dict[str, np.ndarray],
    *,
    marginal_directions: np.ndarray,
) -> dict[str, np.ndarray]:
    """Build omnibus, location, and mean-free shape views."""
    mean = blocks["mean"]
    if marginal_directions.shape[0] * 3 != blocks["quantiles"].shape[-1]:
        raise ValueError("Quantile block does not match marginal directions.")
    # Whitened quantiles cannot be algebraically centered by the raw mean.
    # The strict shape view therefore excludes the raw quantile block.
    higher = blocks["rff"]
    strict_shape = np.concatenate([blocks["variance"], higher], axis=-1)
    return {
        "M_all": np.concatenate([blocks[name] for name in BLOCK_NAMES], axis=-1),
        "location_mean": mean,
        "strict_shape": strict_shape,
        "dispersion_variance": blocks["variance"],
        "higher_shape": higher,
    }


def _row_normalize(values: np.ndarray) -> np.ndarray:
    centered = np.asarray(values, dtype=float)
    centered = centered - centered.mean(axis=1, keepdims=True)
    return centered / np.maximum(
        np.linalg.norm(centered, axis=1, keepdims=True),
        1e-12,
    )


def quotient_statistics(
    values: np.ndarray,
    *,
    compute_auc: bool = True,
) -> dict[str, float]:
    """Measure signed replicated structure and same-author concordance."""
    array = np.asarray(values, dtype=float)
    if array.ndim != 3 or array.shape[1] != 2:
        raise ValueError("values must be author x 2 x dimensions.")
    first = array[:, 0]
    second = array[:, 1]
    covariance = replicated_covariance(first, second)
    frobenius = float(np.linalg.norm(covariance, ord="fro"))
    operator = float(np.linalg.norm(covariance, ord=2))
    effective_rank = (
        float((frobenius / operator) ** 2) if operator > 1e-12 else 0.0
    )
    first_centered = first - first.mean(axis=0, keepdims=True)
    second_centered = second - second.mean(axis=0, keepdims=True)
    same = np.einsum("ij,ij->i", first_centered, second_centered)
    all_products = first_centered @ second_centered.T
    stranger = all_products[~np.eye(len(array), dtype=bool)]
    denominator = np.sqrt(
        max(float(np.mean(np.sum(first_centered**2, axis=1))), 1e-12)
        * max(float(np.mean(np.sum(second_centered**2, axis=1))), 1e-12)
    )
    link = float((same.mean() - stranger.mean()) / denominator)
    auc = float("nan")
    if compute_auc:
        similarity = _row_normalize(first) @ _row_normalize(second).T
        labels = np.eye(len(array), dtype=int).ravel()
        auc = float(roc_auc_score(labels, similarity.ravel()))
    return {
        "frobenius": frobenius,
        "operator_norm": operator,
        "effective_rank": effective_rank,
        "link": link,
        "same_author_auc": auc,
    }


def _paired_bootstrap_contrasts(
    natural: np.ndarray,
    pseudo_worlds: list[np.ndarray],
    *,
    draws: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    if not pseudo_worlds:
        raise ValueError("At least one pseudo world is required.")
    samples = {
        "frobenius": np.empty(draws, dtype=float),
        "link": np.empty(draws, dtype=float),
    }
    for draw in range(draws):
        indices = rng.integers(0, len(natural), size=len(natural))
        pseudo = pseudo_worlds[draw % len(pseudo_worlds)]
        natural_stat = quotient_statistics(
            natural[indices],
            compute_auc=False,
        )
        pseudo_stat = quotient_statistics(
            pseudo[indices],
            compute_auc=False,
        )
        for metric in samples:
            samples[metric][draw] = natural_stat[metric] - pseudo_stat[metric]
    return samples


def centered_bootstrap_lower_bound(
    observed_delta: float,
    bootstrap_delta: np.ndarray,
    *,
    alpha: float = 0.05,
) -> float:
    """Return a centered one-sided bound for paired norm contrasts."""
    samples = np.asarray(bootstrap_delta, dtype=float)
    centered = samples - samples.mean()
    return float(observed_delta + np.quantile(centered, alpha))


def evaluate_marginal_background_quotient(
    tensors: dict[str, EventTensor],
    *,
    feature_spec: RealTextRelationSpec,
    spec: MarginalQuotientSpec,
    reallocator: Callable[..., tuple[np.ndarray, pd.DataFrame]] = (
        pseudo_set_reallocation
    ),
) -> dict[str, Any]:
    """Evaluate natural author M structure against conditional pseudo worlds."""
    event_dimension = next(iter(tensors.values())).vectors.shape[-1]
    directions = frozen_random_directions(
        event_dimensions=event_dimension,
        count=feature_spec.random_directions,
        seed=feature_spec.seed + 17,
    )
    rng = np.random.default_rng(spec.seed)
    runtime: dict[str, tuple[FrozenMarginalBackground, dict[str, np.ndarray]]] = {}
    background_rows = []
    reallocation_rows = []
    observed: dict[tuple[str, str, str], dict[str, float]] = {}
    null: dict[tuple[str, str, str], list[dict[str, float]]] = {}
    bootstrap_pseudo: dict[tuple[str, str, str], list[np.ndarray]] = {}
    for corpus, tensor in tensors.items():
        background, diagnostics = fit_marginal_background(
            tensor,
            marginal_directions=directions[0],
            spec=spec,
            rng=rng,
            reallocator=reallocator,
        )
        diagnostics["corpus"] = corpus
        reallocation_rows.append(diagnostics)
        natural_blocks = tensor_feature_blocks(
            tensor.vectors,
            marginal_directions=directions[0],
        )
        runtime[corpus] = (background, natural_blocks)
        background_rows.extend(
            {
                "corpus": corpus,
                "block": block,
                "dimension": background.block_dimensions[block],
                "condition_number": background.condition_numbers[block],
                "coverage": background.coverage,
            }
            for block in BLOCK_NAMES
        )
        for split in ("D1", "D2"):
            mask = tensor.metadata["split"].eq(split).to_numpy()
            contexts = tensor.metadata.loc[mask, "context"].astype(str).to_numpy()
            quotient = quotient_blocks(
                {block: values[mask] for block, values in natural_blocks.items()},
                contexts,
                background,
            )
            views = quotient_views(quotient, marginal_directions=directions[0])
            for view, values in views.items():
                key = (corpus, split, view)
                observed[key] = quotient_statistics(values)
                null[key] = []
                if view == "M_all":
                    bootstrap_pseudo[key] = []

    for draw in range(spec.null_draws):
        for corpus, tensor in tensors.items():
            background, _ = runtime[corpus]
            pseudo, diagnostics = reallocator(
                tensor,
                block_size=spec.local_length_block,
                rng=rng,
            )
            reallocation_rows.append(
                pd.DataFrame(
                    [
                        {
                            "stage": "test_null",
                            "draw": draw,
                            "corpus": corpus,
                            "same_author": int(diagnostics["same_author"].sum()),
                            "total_assignments": int(
                                diagnostics["block_size"].sum()
                            ),
                            "identity_blocks": int(
                                diagnostics.get(
                                    "identity_block",
                                    pd.Series(dtype=int),
                                ).sum()
                            ),
                            "mean_absolute_length_difference": float(
                                np.average(
                                    diagnostics[
                                        "mean_absolute_length_difference"
                                    ],
                                    weights=diagnostics["block_size"],
                                )
                            ),
                        }
                    ]
                )
            )
            pseudo_blocks = tensor_feature_blocks(
                pseudo,
                marginal_directions=directions[0],
            )
            for split in ("D1", "D2"):
                mask = tensor.metadata["split"].eq(split).to_numpy()
                contexts = (
                    tensor.metadata.loc[mask, "context"].astype(str).to_numpy()
                )
                quotient = quotient_blocks(
                    {
                        block: values[mask]
                        for block, values in pseudo_blocks.items()
                    },
                    contexts,
                    background,
                )
                views = quotient_views(
                    quotient,
                    marginal_directions=directions[0],
                )
                for view, values in views.items():
                    key = (corpus, split, view)
                    if view != "M_all" and draw >= spec.diagnostic_null_draws:
                        continue
                    null[key].append(
                        quotient_statistics(values, compute_auc=False)
                    )
                    if (
                        view == "M_all"
                        and draw < spec.bootstrap_reference_worlds
                    ):
                        bootstrap_pseudo[key].append(
                            values.astype(np.float32, copy=True)
                        )

    primary_keys = [
        key for key in observed if key[2] == "M_all"
    ]
    maximum_null: dict[str, np.ndarray] = {}
    observed_z: dict[str, list[float]] = {}
    for metric in ("frobenius", "link"):
        standardized_nulls = []
        observed_z[metric] = []
        for key in primary_keys:
            values = np.asarray([row[metric] for row in null[key]])
            standard = max(float(values.std(ddof=1)), 1e-12)
            standardized_nulls.append((values - values.mean()) / standard)
            observed_z[metric].append(
                (observed[key][metric] - values.mean()) / standard
            )
        maximum_null[metric] = np.max(
            np.vstack(standardized_nulls),
            axis=0,
        )

    rows = []
    null_rows = []
    block_rows = []
    primary_lookup = {
        key: index for index, key in enumerate(primary_keys)
    }
    for key, observed_metrics in observed.items():
        corpus, split, view = key
        tested_metrics = (
            "frobenius",
            "operator_norm",
            "effective_rank",
            "link",
        )
        metric_null = {
            metric: np.asarray([row[metric] for row in null[key]])
            for metric in tested_metrics
        }
        row = {
            "corpus": corpus,
            "split": split,
            "view": view,
            **{f"observed_{name}": value for name, value in observed_metrics.items()},
            **{
                f"pseudo_mean_{name}": (
                    float(metric_null[name].mean())
                    if name in metric_null
                    else float("nan")
                )
                for name in observed_metrics
            },
            "frobenius_delta": (
                observed_metrics["frobenius"]
                - float(metric_null["frobenius"].mean())
            ),
            "link_delta": (
                observed_metrics["link"] - float(metric_null["link"].mean())
            ),
            "frobenius_raw_p": float(
                (
                    1
                    + np.sum(
                        metric_null["frobenius"]
                        >= observed_metrics["frobenius"]
                    )
                )
                / (len(metric_null["frobenius"]) + 1)
            ),
            "link_raw_p": float(
                (
                    1
                    + np.sum(metric_null["link"] >= observed_metrics["link"])
                )
                / (len(metric_null["link"]) + 1)
            ),
            "auc_raw_p": float("nan"),
        }
        if view == "M_all":
            index = primary_lookup[key]
            row["frobenius_max_t_p"] = float(
                (
                    1
                    + np.sum(
                        maximum_null["frobenius"]
                        >= observed_z["frobenius"][index]
                    )
                )
                / (len(maximum_null["frobenius"]) + 1)
            )
            row["link_max_t_p"] = float(
                (
                    1
                    + np.sum(
                        maximum_null["link"] >= observed_z["link"][index]
                    )
                )
                / (len(maximum_null["link"]) + 1)
            )
            tensor = tensors[corpus]
            mask = tensor.metadata["split"].eq(split).to_numpy()
            contexts = tensor.metadata.loc[mask, "context"].astype(str).to_numpy()
            natural_quotient = quotient_blocks(
                {
                    block: values[mask]
                    for block, values in runtime[corpus][1].items()
                },
                contexts,
                runtime[corpus][0],
            )
            natural_values = quotient_views(
                natural_quotient,
                marginal_directions=directions[0],
            )[view]
            bootstrap = _paired_bootstrap_contrasts(
                natural_values,
                bootstrap_pseudo[key],
                draws=spec.bootstrap_draws,
                rng=rng,
            )
            row["frobenius_bootstrap_lcb"] = centered_bootstrap_lower_bound(
                row["frobenius_delta"],
                bootstrap["frobenius"],
            )
            row["frobenius_bootstrap_mean"] = float(
                bootstrap["frobenius"].mean()
            )
            row["link_bootstrap_lcb"] = centered_bootstrap_lower_bound(
                row["link_delta"],
                bootstrap["link"],
            )
            row["link_bootstrap_mean"] = float(bootstrap["link"].mean())
        else:
            row["frobenius_max_t_p"] = float("nan")
            row["link_max_t_p"] = float("nan")
            row["frobenius_bootstrap_lcb"] = float("nan")
            row["frobenius_bootstrap_mean"] = float("nan")
            row["link_bootstrap_lcb"] = float("nan")
            row["link_bootstrap_mean"] = float("nan")
        rows.append(row)
        if view != "M_all":
            block_rows.append(row.copy())
        for draw, metrics in enumerate(null[key]):
            null_rows.append(
                {
                    "draw": draw,
                    "corpus": corpus,
                    "split": split,
                    "view": view,
                    **metrics,
                }
            )

    cells = pd.DataFrame(rows)
    primary = cells["view"].eq("M_all")
    corpus_status: dict[str, str] = {}
    for corpus in tensors:
        selected = cells.loc[primary & cells["corpus"].eq(corpus)]
        background = runtime[corpus][0]
        full_gate = bool(
            selected["frobenius_delta"].gt(0).all()
            and selected["frobenius_max_t_p"].le(0.05).all()
            and selected["frobenius_bootstrap_lcb"].gt(0).all()
            and selected["observed_link"].gt(0).all()
        )
        signed_gate = bool(
            selected["link_delta"].gt(0).all()
            and selected["link_max_t_p"].le(0.05).all()
            and selected["link_bootstrap_lcb"].gt(0).all()
        )
        if background.coverage < spec.minimum_coverage:
            corpus_status[corpus] = "BACKGROUND_QUOTIENT_UNDERRESOLVED"
        elif full_gate:
            corpus_status[corpus] = "CORPUS_LOCAL_GROUPING_RESIDUAL_DETECTED"
        elif (
            selected["frobenius_delta"].gt(0).all()
            and selected["frobenius_max_t_p"].le(0.05).all()
            and selected["observed_link"].le(0).any()
        ):
            corpus_status[corpus] = "RELATION_WITHOUT_CONCORDANCE"
        elif signed_gate:
            corpus_status[corpus] = "SIGNED_CONCORDANCE_RESIDUAL_DETECTED"
        elif (
            selected["frobenius_delta"].gt(0).all()
            and selected["frobenius_max_t_p"].le(0.05).all()
            and selected["frobenius_bootstrap_lcb"].le(0).any()
        ):
            corpus_status[corpus] = "GROUPING_RESIDUAL_INCONCLUSIVE_BOOTSTRAP"
        else:
            corpus_status[corpus] = "GROUPING_RESIDUAL_NOT_DETECTED"
    detected = [
        corpus
        for corpus, status in corpus_status.items()
        if status == "CORPUS_LOCAL_GROUPING_RESIDUAL_DETECTED"
    ]
    signed = [
        corpus
        for corpus, value in corpus_status.items()
        if value
        in {
            "CORPUS_LOCAL_GROUPING_RESIDUAL_DETECTED",
            "SIGNED_CONCORDANCE_RESIDUAL_DETECTED",
        }
    ]
    status = (
        "MULTI_CORPUS_LOCAL_GROUPING_RESIDUAL_DETECTED"
        if len(detected) >= 2
        else (
            "ONE_CORPUS_LOCAL_GROUPING_RESIDUAL_DETECTED"
            if detected
            else (
                "MULTI_CORPUS_SIGNED_CONCORDANCE_DETECTED"
                if len(signed) >= 2
                else (
                    "ONE_CORPUS_SIGNED_CONCORDANCE_DETECTED"
                    if signed
                    else (
                        "MARGINAL_GROUPING_RESIDUAL_INCONCLUSIVE"
                        if any(
                            value
                            == "GROUPING_RESIDUAL_INCONCLUSIVE_BOOTSTRAP"
                            for value in corpus_status.values()
                        )
                        else "MARGINAL_BACKGROUND_EXPLAINS_CURRENT_M_GEOMETRY"
                    )
                )
            )
        )
    )
    return {
        "status": status,
        "corpus_status": corpus_status,
        "cells": cells,
        "block_diagnostics": pd.DataFrame(block_rows),
        "null_scores": pd.DataFrame(null_rows),
        "background_diagnostics": pd.DataFrame(background_rows),
        "reallocation_diagnostics": pd.concat(
            reallocation_rows,
            ignore_index=True,
        ),
    }
