"""Signed generalized concordance spectrum on the V8 M background quotient."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
import pandas as pd

from suica_core.v8_event_set_composition_knockout import (
    EventTensor,
    pseudo_set_reallocation,
)
from suica_core.v8_marginal_background_quotient import (
    MarginalQuotientSpec,
    fit_marginal_background,
    quotient_blocks,
    quotient_views,
    tensor_feature_blocks,
)
from suica_core.v8_realtext_relation_field import (
    RealTextRelationSpec,
    frozen_random_directions,
    stable_bucket,
)


SPECTRUM_VIEWS = ("M_all", "strict_shape")


@dataclass(frozen=True)
class ConcordanceSpectrumSpec:
    """Frozen D0 spectrum and D1/D2 audit settings."""

    background_draws: int = 499
    spectrum_null_draws: int = 499
    test_null_draws: int = 1999
    bootstrap_draws: int = 999
    bootstrap_reference_worlds: int = 64
    local_length_block: int = 16
    gamma_grid: tuple[float, ...] = (0.01, 0.03, 0.10, 0.30, 0.50)
    maximum_condition: float = 100.0
    spectrum_quantile: float = 0.95
    maximum_rank: int = 12
    minimum_half_authors: int = 20
    seed: int = 20260818

    def __post_init__(self) -> None:
        if min(
            self.background_draws,
            self.spectrum_null_draws,
        ) < 49:
            raise ValueError("D0 background and spectrum budgets must be >=49.")
        if self.test_null_draws < 99 or self.bootstrap_draws < 99:
            raise ValueError("Test null and bootstrap budgets must be >=99.")
        if self.bootstrap_reference_worlds < 8:
            raise ValueError("At least eight bootstrap pseudo worlds are needed.")
        if not self.gamma_grid or any(
            value <= 0.0 or value >= 1.0 for value in self.gamma_grid
        ):
            raise ValueError("gamma_grid values must lie in (0, 1).")
        if not 0.5 < self.spectrum_quantile < 1.0:
            raise ValueError("spectrum_quantile must lie in (0.5, 1).")
        if self.maximum_rank < 1:
            raise ValueError("maximum_rank must be positive.")


def _center(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    return matrix - matrix.mean(axis=0, keepdims=True)


def _block_slices(view: str) -> list[slice]:
    if view == "M_all":
        dimensions = (64, 64, 16, 24)
    elif view == "strict_shape":
        # Mean-free by construction: variance plus centered RFF only.
        dimensions = (64, 16)
    else:
        raise ValueError(f"Unknown spectrum view {view}.")
    result = []
    start = 0
    for dimension in dimensions:
        result.append(slice(start, start + dimension))
        start += dimension
    return result


def signed_operators(
    values: np.ndarray,
    *,
    block_slices: list[slice],
) -> tuple[np.ndarray, np.ndarray]:
    """Return signed cross-replicate B and complete within-energy W."""
    array = np.asarray(values, dtype=float)
    first = _center(array[:, 0])
    second = _center(array[:, 1])
    count = max(len(array), 1)
    cross = first.T @ second / count
    between = 0.5 * (cross + cross.T)
    covered = sum(block.stop - block.start for block in block_slices)
    if covered != first.shape[1]:
        raise ValueError("block_slices do not cover the complete feature view.")
    within = 0.5 * (
        first.T @ first / count + second.T @ second / count
    )
    return between, within


def _regularized_within(
    within: np.ndarray,
    gamma: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    matrix = 0.5 * (within + within.T)
    dimension = matrix.shape[0]
    average = max(float(np.trace(matrix)) / max(dimension, 1), 1e-12)
    # Additive ridge preserves W_gamma >= W, so the signed generalized
    # concordance spectrum remains bounded by Cauchy-Schwarz.
    regularized = matrix + gamma * average * np.eye(dimension)
    values, vectors = np.linalg.eigh(regularized)
    floor = 1e-10 * max(float(np.max(values)), average)
    values = np.maximum(values, floor)
    inverse_sqrt = (vectors * (1.0 / np.sqrt(values))) @ vectors.T
    sqrt = (vectors * np.sqrt(values)) @ vectors.T
    condition = float(np.max(values) / max(float(np.min(values)), 1e-15))
    return regularized, inverse_sqrt, sqrt, condition


def generalized_spectrum(
    between: np.ndarray,
    within: np.ndarray,
    *,
    gamma: float,
) -> dict[str, np.ndarray | float]:
    """Solve the signed generalized concordance eigenproblem."""
    regularized, inverse_sqrt, sqrt, condition = _regularized_within(
        within,
        gamma,
    )
    operator = inverse_sqrt @ between @ inverse_sqrt
    operator = 0.5 * (operator + operator.T)
    values, loadings = np.linalg.eigh(operator)
    order = np.argsort(values)[::-1]
    values = values[order]
    loadings = loadings[:, order]
    generalized = inverse_sqrt @ loadings
    return {
        "eigenvalues": values,
        "loadings": loadings,
        "generalized": generalized,
        "within": regularized,
        "within_sqrt": sqrt,
        "condition": condition,
    }


def projected_concordance(
    between: np.ndarray,
    within: np.ndarray,
    vectors: np.ndarray,
    *,
    sign: float = 1.0,
) -> float:
    """Score one frozen generalized subspace on a new panel."""
    if vectors.size == 0:
        return float("nan")
    numerator = float(np.trace(vectors.T @ between @ vectors))
    denominator = max(float(np.trace(vectors.T @ within @ vectors)), 1e-12)
    return float(sign * numerator / denominator)


def subspace_affinity(first: np.ndarray, second: np.ndarray) -> float:
    """Return mean squared principal-angle cosine for two loading spaces."""
    if first.size == 0 or second.size == 0:
        return 0.0
    left, _ = np.linalg.qr(first)
    right, _ = np.linalg.qr(second)
    singular = np.linalg.svd(left.T @ right, compute_uv=False)
    return float(np.mean(singular**2))


def _d0_half_masks(metadata: pd.DataFrame, *, corpus: str, seed: int) -> tuple[np.ndarray, np.ndarray]:
    d0 = metadata["split"].eq("D0").to_numpy()
    ids = metadata["author_id"].astype(str).to_numpy()
    half = np.asarray(
        [
            stable_bucket(
                author,
                salt=f"v8-ccs-{corpus}-{seed}",
                modulus=2,
            )
            for author in ids
        ]
    )
    return d0 & (half == 0), d0 & (half == 1)


def _all_quotient_views(
    vectors: np.ndarray,
    tensor: EventTensor,
    *,
    marginal_directions: np.ndarray,
    background: Any,
) -> dict[str, np.ndarray]:
    features = tensor_feature_blocks(
        vectors,
        marginal_directions=marginal_directions,
    )
    contexts = tensor.metadata["context"].astype(str).to_numpy()
    quotient = quotient_blocks(features, contexts, background)
    return quotient_views(
        quotient,
        marginal_directions=marginal_directions,
    )


def _choose_gamma(
    condition_rows: list[dict[str, float]],
    natural_withins: tuple[np.ndarray, np.ndarray],
    *,
    spec: ConcordanceSpectrumSpec,
) -> tuple[float | None, pd.DataFrame]:
    frame = pd.DataFrame(condition_rows)
    summaries = []
    selected = None
    for gamma in spec.gamma_grid:
        values = frame.loc[frame["gamma"].eq(gamma), "condition"].to_numpy()
        q95 = float(np.quantile(values, 0.95))
        natural_conditions = [
            _regularized_within(within, gamma)[3]
            for within in natural_withins
        ]
        summaries.append(
            {
                "gamma": gamma,
                "condition_q95": q95,
                "condition_max": float(values.max()),
                "natural_condition_a": natural_conditions[0],
                "natural_condition_b": natural_conditions[1],
            }
        )
        if (
            selected is None
            and q95 <= spec.maximum_condition
            and max(natural_conditions) <= spec.maximum_condition
        ):
            selected = gamma
    return selected, pd.DataFrame(summaries)


def _bootstrap_projected_delta(
    natural: np.ndarray,
    pseudo_worlds: list[np.ndarray],
    vectors: np.ndarray,
    *,
    block_slices: list[slice],
    pseudo_mean: float,
    draws: int,
    rng: np.random.Generator,
) -> tuple[float, float]:
    samples = np.empty(draws, dtype=float)
    for draw in range(draws):
        indices = rng.integers(0, len(natural), size=len(natural))
        pseudo = pseudo_worlds[draw % len(pseudo_worlds)]
        natural_b, natural_w = signed_operators(
            natural[indices],
            block_slices=block_slices,
        )
        pseudo_b, pseudo_w = signed_operators(
            pseudo[indices],
            block_slices=block_slices,
        )
        samples[draw] = (
            projected_concordance(natural_b, natural_w, vectors)
            - projected_concordance(pseudo_b, pseudo_w, vectors)
        )
    observed_b, observed_w = signed_operators(
        natural,
        block_slices=block_slices,
    )
    observed_delta = (
        projected_concordance(observed_b, observed_w, vectors) - pseudo_mean
    )
    centered = samples - samples.mean()
    lower = float(observed_delta + np.quantile(centered, 0.025))
    return float(samples.mean()), lower


def evaluate_conditional_concordance_spectrum(
    tensors: dict[str, EventTensor],
    *,
    feature_spec: RealTextRelationSpec,
    spec: ConcordanceSpectrumSpec,
    reallocator: Callable[..., tuple[np.ndarray, pd.DataFrame]] = (
        pseudo_set_reallocation
    ),
) -> dict[str, Any]:
    """Fit D0 signed spectra and audit frozen directions in D1/D2."""
    event_dimension = next(iter(tensors.values())).vectors.shape[-1]
    marginal_directions = frozen_random_directions(
        event_dimensions=event_dimension,
        count=feature_spec.random_directions,
        seed=feature_spec.seed + 17,
    )[0]
    runtime: dict[str, dict[str, Any]] = {}
    spectrum_rows = []
    gamma_rows = []
    loading_rows = []

    for corpus, tensor in tensors.items():
        background_rng = np.random.default_rng(
            spec.seed
            + stable_bucket(
                corpus,
                salt="v8-ccs-background",
                modulus=2**31 - 1,
            )
        )
        background_spec = MarginalQuotientSpec(
            background_draws=spec.background_draws,
            null_draws=99,
            diagnostic_null_draws=99,
            bootstrap_draws=99,
            bootstrap_reference_worlds=8,
            local_length_block=spec.local_length_block,
            seed=spec.seed,
        )
        background, _ = fit_marginal_background(
            tensor,
            marginal_directions=marginal_directions,
            spec=background_spec,
            rng=background_rng,
            reallocator=reallocator,
        )
        half_a, half_b = _d0_half_masks(
            tensor.metadata,
            corpus=corpus,
            seed=spec.seed,
        )
        if min(int(half_a.sum()), int(half_b.sum())) < spec.minimum_half_authors:
            runtime[corpus] = {"status": "D0_HALF_UNDERRESOLVED"}
            continue
        d0 = tensor.metadata["split"].eq("D0").to_numpy()
        natural_all = _all_quotient_views(
            tensor.vectors,
            tensor,
            marginal_directions=marginal_directions,
            background=background,
        )
        natural_views = {
            view: {
                "D0": natural_all[view][d0],
                "A": natural_all[view][half_a],
                "B": natural_all[view][half_b],
            }
            for view in SPECTRUM_VIEWS
        }

        condition_rows: dict[str, list[dict[str, float]]] = {
            view: [] for view in SPECTRUM_VIEWS
        }
        condition_rng = np.random.default_rng(
            spec.seed
            + stable_bucket(
                corpus,
                salt="v8-ccs-condition",
                modulus=2**31 - 1,
            )
        )
        for _ in range(spec.spectrum_null_draws):
            pseudo, _ = reallocator(
                tensor,
                block_size=spec.local_length_block,
                rng=condition_rng,
            )
            pseudo_views = _all_quotient_views(
                pseudo,
                tensor,
                marginal_directions=marginal_directions,
                background=background,
            )
            for view in SPECTRUM_VIEWS:
                for mask in (half_a, half_b):
                    values = pseudo_views[view][mask]
                    _, within = signed_operators(
                        values,
                        block_slices=_block_slices(view),
                    )
                    for gamma in spec.gamma_grid:
                        condition = _regularized_within(within, gamma)[3]
                        condition_rows[view].append(
                            {"gamma": gamma, "condition": condition}
                        )

        corpus_runtime = {
            "status": "READY",
            "background": background,
            "natural": natural_views,
            "views": {},
        }
        for view in SPECTRUM_VIEWS:
            blocks = _block_slices(view)
            natural_half_withins = []
            for key in ("A", "B"):
                _, half_within = signed_operators(
                    natural_views[view][key],
                    block_slices=blocks,
                )
                natural_half_withins.append(half_within)
            gamma, summary = _choose_gamma(
                condition_rows[view],
                tuple(natural_half_withins),
                spec=spec,
            )
            summary["corpus"] = corpus
            summary["view"] = view
            gamma_rows.append(summary)
            if gamma is None:
                corpus_runtime["views"][view] = {
                    "status": "WITHIN_OPERATOR_UNDERRESOLVED"
                }
                continue
            natural_full_b, natural_full_w = signed_operators(
                natural_views[view]["D0"],
                block_slices=blocks,
            )
            natural_half_conditions = [
                _regularized_within(within, gamma)[3]
                for within in natural_half_withins
            ]
            natural_spectrum = generalized_spectrum(
                natural_full_b,
                natural_full_w,
                gamma=gamma,
            )
            pseudo_positive = []
            pseudo_negative = []
            pseudo_affinity_positive: dict[int, list[float]] = {
                rank: [] for rank in range(1, spec.maximum_rank + 1)
            }
            pseudo_affinity_negative: dict[int, list[float]] = {
                rank: [] for rank in range(1, spec.maximum_rank + 1)
            }
            spectrum_rng = np.random.default_rng(
                spec.seed
                + stable_bucket(
                    f"{corpus}-{view}",
                    salt="v8-ccs-spectrum",
                    modulus=2**31 - 1,
                )
            )
            for _ in range(spec.spectrum_null_draws):
                pseudo, _ = reallocator(
                    tensor,
                    block_size=spec.local_length_block,
                    rng=spectrum_rng,
                )
                pseudo_views = _all_quotient_views(
                    pseudo,
                    tensor,
                    marginal_directions=marginal_directions,
                    background=background,
                )
                values_full = pseudo_views[view][d0]
                values_a = pseudo_views[view][half_a]
                values_b = pseudo_views[view][half_b]
                spectra = []
                for values in (values_full, values_a, values_b):
                    between, within = signed_operators(
                        values,
                        block_slices=blocks,
                    )
                    spectra.append(
                        generalized_spectrum(
                            between,
                            within,
                            gamma=gamma,
                        )
                    )
                eigenvalues = spectra[0]["eigenvalues"]
                pseudo_positive.append(float(eigenvalues[0]))
                pseudo_negative.append(float(-eigenvalues[-1]))
                for rank in range(1, spec.maximum_rank + 1):
                    pseudo_affinity_positive[rank].append(
                        subspace_affinity(
                            spectra[1]["loadings"][:, :rank],
                            spectra[2]["loadings"][:, :rank],
                        )
                    )
                    pseudo_affinity_negative[rank].append(
                        subspace_affinity(
                            spectra[1]["loadings"][:, -rank:],
                            spectra[2]["loadings"][:, -rank:],
                        )
                    )
            positive_threshold = float(
                np.quantile(pseudo_positive, spec.spectrum_quantile)
            )
            negative_threshold = float(
                np.quantile(pseudo_negative, spec.spectrum_quantile)
            )
            eigenvalues = np.asarray(natural_spectrum["eigenvalues"])
            positive_rank = min(
                int(np.sum(eigenvalues > positive_threshold)),
                spec.maximum_rank,
            )
            negative_rank = min(
                int(np.sum(eigenvalues < -negative_threshold)),
                spec.maximum_rank,
            )
            half_spectra = []
            for key in ("A", "B"):
                between, within = signed_operators(
                    natural_views[view][key],
                    block_slices=blocks,
                )
                half_spectra.append(
                    generalized_spectrum(
                        between,
                        within,
                        gamma=gamma,
                    )
                )

            def stable_side(
                rank: int,
                *,
                positive: bool,
            ) -> tuple[bool, float, float, float, float]:
                if rank == 0:
                    return (
                        False,
                        0.0,
                        float("nan"),
                        float("nan"),
                        float("nan"),
                    )
                if positive:
                    left_u = half_spectra[0]["loadings"][:, :rank]
                    right_u = half_spectra[1]["loadings"][:, :rank]
                    left_v = half_spectra[0]["generalized"][:, :rank]
                    right_v = half_spectra[1]["generalized"][:, :rank]
                    null_affinity = pseudo_affinity_positive[rank]
                    sign = 1.0
                else:
                    left_u = half_spectra[0]["loadings"][:, -rank:]
                    right_u = half_spectra[1]["loadings"][:, -rank:]
                    left_v = half_spectra[0]["generalized"][:, -rank:]
                    right_v = half_spectra[1]["generalized"][:, -rank:]
                    null_affinity = pseudo_affinity_negative[rank]
                    sign = -1.0
                affinity = subspace_affinity(left_u, right_u)
                threshold = float(
                    np.quantile(null_affinity, spec.spectrum_quantile)
                )
                b_a, w_a = signed_operators(
                    natural_views[view]["A"],
                    block_slices=blocks,
                )
                b_b, w_b = signed_operators(
                    natural_views[view]["B"],
                    block_slices=blocks,
                )
                held_ab = projected_concordance(
                    b_b,
                    w_b,
                    left_v,
                    sign=sign,
                )
                held_ba = projected_concordance(
                    b_a,
                    w_a,
                    right_v,
                    sign=sign,
                )
                return (
                    bool(
                        affinity > threshold
                        and held_ab > 0.0
                        and held_ba > 0.0
                    ),
                    affinity,
                    threshold,
                    held_ab,
                    held_ba,
                )

            (
                positive_stable,
                positive_affinity,
                positive_affinity_threshold,
                positive_ab,
                positive_ba,
            ) = stable_side(positive_rank, positive=True)
            (
                negative_stable,
                negative_affinity,
                negative_affinity_threshold,
                negative_ab,
                negative_ba,
            ) = stable_side(negative_rank, positive=False)
            positive_vectors = (
                np.asarray(natural_spectrum["generalized"])[:, :positive_rank]
                if positive_stable
                else np.empty((len(eigenvalues), 0))
            )
            negative_vectors = (
                np.asarray(natural_spectrum["generalized"])[:, -negative_rank:]
                if negative_stable
                else np.empty((len(eigenvalues), 0))
            )
            view_status = (
                "POSITIVE_CONCORDANCE_SUBSPACE_RESOLVED"
                if positive_stable
                else "POSITIVE_CONCORDANCE_SUBSPACE_UNDERRESOLVED"
            )
            spectrum_rows.append(
                {
                    "corpus": corpus,
                    "view": view,
                    "status": view_status,
                    "gamma": gamma,
                    "positive_threshold": positive_threshold,
                    "negative_threshold": negative_threshold,
                    "positive_rank": positive_rank,
                    "negative_rank": negative_rank,
                    "positive_stable": positive_stable,
                    "negative_stable": negative_stable,
                    "natural_condition_a": natural_half_conditions[0],
                    "natural_condition_b": natural_half_conditions[1],
                    "positive_affinity": positive_affinity,
                    "positive_affinity_threshold": positive_affinity_threshold,
                    "negative_affinity": negative_affinity,
                    "negative_affinity_threshold": negative_affinity_threshold,
                    "positive_held_ab": positive_ab,
                    "positive_held_ba": positive_ba,
                    "negative_held_ab": negative_ab,
                    "negative_held_ba": negative_ba,
                    "positive_mass": float(
                        eigenvalues[eigenvalues > positive_threshold].sum()
                    ),
                    "negative_mass": float(
                        -eigenvalues[eigenvalues < -negative_threshold].sum()
                    ),
                    "trace": float(eigenvalues.sum()),
                    "frobenius": float(np.linalg.norm(eigenvalues)),
                }
            )
            if positive_stable:
                loadings = np.asarray(natural_spectrum["loadings"])[
                    :,
                    :positive_rank,
                ]
                for axis in range(positive_rank):
                    total = max(
                        float(np.sum(loadings[:, axis] ** 2)),
                        1e-12,
                    )
                    for block_index, block in enumerate(blocks):
                        loading_rows.append(
                            {
                                "corpus": corpus,
                                "view": view,
                                "axis": axis,
                                "block": block_index,
                                "attribution": float(
                                    np.sum(loadings[block, axis] ** 2) / total
                                ),
                            }
                        )
            corpus_runtime["views"][view] = {
                "status": view_status,
                "gamma": gamma,
                "blocks": blocks,
                "positive_vectors": positive_vectors,
                "negative_vectors": negative_vectors,
            }
        runtime[corpus] = corpus_runtime

    observed: dict[tuple[str, str, str], float] = {}
    null: dict[tuple[str, str, str], list[float]] = {}
    bootstrap_pseudo: dict[tuple[str, str, str], list[np.ndarray]] = {}
    natural_test: dict[tuple[str, str, str], np.ndarray] = {}
    for corpus, tensor in tensors.items():
        if runtime.get(corpus, {}).get("status") != "READY":
            continue
        all_natural_test_views = _all_quotient_views(
            tensor.vectors,
            tensor,
            marginal_directions=marginal_directions,
            background=runtime[corpus]["background"],
        )
        for view in SPECTRUM_VIEWS:
            view_runtime = runtime[corpus]["views"].get(view, {})
            vectors = view_runtime.get("positive_vectors")
            if vectors is None or vectors.size == 0:
                continue
            for split in ("D1", "D2"):
                mask = tensor.metadata["split"].eq(split).to_numpy()
                values = all_natural_test_views[view][mask]
                between, within = signed_operators(
                    values,
                    block_slices=view_runtime["blocks"],
                )
                key = (corpus, split, view)
                observed[key] = projected_concordance(
                    between,
                    within,
                    vectors,
                )
                natural_test[key] = values
                null[key] = []
                bootstrap_pseudo[key] = []

    test_rngs = {
        corpus: np.random.default_rng(
            spec.seed
            + stable_bucket(
                corpus,
                salt="v8-ccs-test",
                modulus=2**31 - 1,
            )
        )
        for corpus in tensors
    }
    for draw in range(spec.test_null_draws):
        for corpus, tensor in tensors.items():
            active_views = [
                view
                for view in SPECTRUM_VIEWS
                if runtime.get(corpus, {}).get("views", {}).get(view, {}).get(
                    "positive_vectors",
                    np.empty((0, 0)),
                ).size
            ]
            if not active_views:
                continue
            pseudo, _ = reallocator(
                tensor,
                block_size=spec.local_length_block,
                rng=test_rngs[corpus],
            )
            pseudo_views = _all_quotient_views(
                pseudo,
                tensor,
                marginal_directions=marginal_directions,
                background=runtime[corpus]["background"],
            )
            for view in active_views:
                view_runtime = runtime[corpus]["views"][view]
                for split in ("D1", "D2"):
                    mask = tensor.metadata["split"].eq(split).to_numpy()
                    values = pseudo_views[view][mask]
                    between, within = signed_operators(
                        values,
                        block_slices=view_runtime["blocks"],
                    )
                    key = (corpus, split, view)
                    null[key].append(
                        projected_concordance(
                            between,
                            within,
                            view_runtime["positive_vectors"],
                        )
                    )
                    if draw < spec.bootstrap_reference_worlds:
                        bootstrap_pseudo[key].append(
                            values.astype(np.float32, copy=True)
                        )

    primary_keys = [key for key in observed if key[2] == "M_all"]
    if primary_keys:
        standardized = []
        z_observed = []
        for key in primary_keys:
            values = np.asarray(null[key])
            standard = max(float(values.std(ddof=1)), 1e-12)
            standardized.append((values - values.mean()) / standard)
            z_observed.append(
                (observed[key] - values.mean()) / standard
            )
        maximum = np.max(np.vstack(standardized), axis=0)
    else:
        maximum = np.empty(0)
        z_observed = []
    lookup = {key: index for index, key in enumerate(primary_keys)}
    cell_rows = []
    null_rows = []
    bootstrap_rng = np.random.default_rng(spec.seed + 991)
    for key, score in observed.items():
        corpus, split, view = key
        values = np.asarray(null[key])
        pseudo_mean = float(values.mean())
        bootstrap_mean, bootstrap_lcb = _bootstrap_projected_delta(
            natural_test[key],
            bootstrap_pseudo[key],
            runtime[corpus]["views"][view]["positive_vectors"],
            block_slices=runtime[corpus]["views"][view]["blocks"],
            pseudo_mean=pseudo_mean,
            draws=spec.bootstrap_draws,
            rng=bootstrap_rng,
        )
        row = {
            "corpus": corpus,
            "split": split,
            "view": view,
            "observed": score,
            "pseudo_mean": pseudo_mean,
            "delta": score - pseudo_mean,
            "raw_p": float(
                (1 + np.sum(values >= score)) / (len(values) + 1)
            ),
            "bootstrap_mean": bootstrap_mean,
            "bootstrap_lcb": bootstrap_lcb,
            "max_t_p": float("nan"),
        }
        if view == "M_all":
            index = lookup[key]
            row["max_t_p"] = float(
                (1 + np.sum(maximum >= z_observed[index]))
                / (len(maximum) + 1)
            )
        cell_rows.append(row)
        null_rows.extend(
            {
                "draw": draw,
                "corpus": corpus,
                "split": split,
                "view": view,
                "score": value,
            }
            for draw, value in enumerate(values)
        )
    cells = pd.DataFrame(
        cell_rows,
        columns=[
            "corpus",
            "split",
            "view",
            "observed",
            "pseudo_mean",
            "delta",
            "raw_p",
            "bootstrap_mean",
            "bootstrap_lcb",
            "max_t_p",
        ],
    )
    corpus_status = {}
    for corpus in tensors:
        selected = cells.loc[
            cells["corpus"].eq(corpus) & cells["view"].eq("M_all")
        ]
        if len(selected) != 2:
            corpus_status[corpus] = "POSITIVE_SPECTRUM_UNDERRESOLVED"
        elif (
            selected["delta"].gt(0).all()
            and selected["max_t_p"].le(0.05).all()
            and selected["bootstrap_lcb"].gt(0).all()
        ):
            corpus_status[corpus] = "FROZEN_POSITIVE_SPECTRUM_REPLICATED"
        else:
            corpus_status[corpus] = "FROZEN_POSITIVE_SPECTRUM_NOT_REPLICATED"
    replicated = [
        corpus
        for corpus, value in corpus_status.items()
        if value == "FROZEN_POSITIVE_SPECTRUM_REPLICATED"
    ]
    status = (
        "MULTI_CORPUS_LOCAL_POSITIVE_SPECTRA_REPLICATED"
        if len(replicated) >= 2
        else (
            "ONE_CORPUS_LOCAL_POSITIVE_SPECTRUM_REPLICATED"
            if replicated
            else "SIGNED_CONCORDANCE_NOT_LOW_DIMENSIONALLY_RESOLVED"
        )
    )
    return {
        "status": status,
        "corpus_status": corpus_status,
        "spectrum": pd.DataFrame(spectrum_rows),
        "gamma_diagnostics": (
            pd.concat(gamma_rows, ignore_index=True)
            if gamma_rows
            else pd.DataFrame()
        ),
        "loadings": pd.DataFrame(loading_rows),
        "cells": cells,
        "null_scores": pd.DataFrame(null_rows),
    }
