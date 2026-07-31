"""Low-dimensional spectrum test after D0-frozen nuisance filtration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from suica_core.v8_conditional_concordance_spectrum import (
    generalized_spectrum,
    projected_concordance,
    signed_operators,
    subspace_affinity,
)
from suica_core.v8_realtext_relation_field import stable_bucket


@dataclass(frozen=True)
class FilteredSpectrumSpec:
    """Frozen budgets for residual low-dimensional spectrum falsification."""

    d0_null_draws: int = 999
    test_null_draws: int = 1999
    bootstrap_draws: int = 999
    maximum_rank: int = 12
    spectrum_quantile: float = 0.95
    minimum_half_authors: int = 20
    seed: int = 20260826

    def __post_init__(self) -> None:
        if self.d0_null_draws < 99 or self.test_null_draws < 99:
            raise ValueError("Null budgets must be at least 99.")
        if self.bootstrap_draws < 99:
            raise ValueError("bootstrap_draws must be at least 99.")
        if self.maximum_rank < 1:
            raise ValueError("maximum_rank must be positive.")


def _half_masks(
    metadata: pd.DataFrame,
    *,
    corpus: str,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    d0 = metadata["split"].eq("D0").to_numpy()
    halves = np.asarray(
        [
            stable_bucket(
                str(author),
                salt=f"v8-filtered-spectrum-{corpus}-{seed}",
                modulus=2,
            )
            for author in metadata["author_id"]
        ]
    )
    return d0 & (halves == 0), d0 & (halves == 1)


def _permute_second(
    values: np.ndarray,
    metadata: pd.DataFrame,
    mask: np.ndarray,
    *,
    rng: np.random.Generator,
) -> np.ndarray:
    selected = np.asarray(values[mask], dtype=float).copy()
    contexts = metadata.loc[mask, "context"].astype(str).to_numpy()
    order = np.arange(len(selected))
    for context in np.unique(contexts):
        indices = np.flatnonzero(contexts == context)
        order[indices] = rng.permutation(indices)
    selected[:, 1] = selected[order, 1]
    return selected


def _operators(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return signed_operators(
        values,
        block_slices=[slice(0, values.shape[-1])],
    )


def _spectrum(values: np.ndarray, *, gamma: float) -> dict[str, Any]:
    between, within = _operators(values)
    return generalized_spectrum(between, within, gamma=gamma)


def _bootstrap_projected_excess(
    values: np.ndarray,
    metadata: pd.DataFrame,
    mask: np.ndarray,
    vectors: np.ndarray,
    *,
    null_mean: float,
    draws: int,
    rng: np.random.Generator,
) -> float:
    selected = values[mask]
    contexts = metadata.loc[mask, "context"].astype(str).to_numpy()
    groups = {
        context: np.flatnonzero(contexts == context)
        for context in np.unique(contexts)
    }
    observed_b, observed_w = _operators(selected)
    observed = projected_concordance(
        observed_b,
        observed_w,
        vectors,
    )
    samples = np.empty(draws, dtype=float)
    for draw in range(draws):
        indices = np.concatenate(
            [
                rng.choice(group, size=len(group), replace=True)
                for group in groups.values()
            ]
        )
        between, within = _operators(selected[indices])
        samples[draw] = projected_concordance(
            between,
            within,
            vectors,
        ) - null_mean
    observed_excess = observed - null_mean
    centered = samples - samples.mean()
    return float(observed_excess + np.quantile(centered, 0.025))


def evaluate_filtered_spectrum(
    panels: dict[str, tuple[pd.DataFrame, np.ndarray]],
    *,
    gamma_by_corpus: dict[str, float],
    spec: FilteredSpectrumSpec,
) -> dict[str, Any]:
    """Discover D0 residual axes and test them without inspecting D1/D2."""
    runtime: dict[str, dict[str, Any]] = {}
    discovery_rows = []
    null_top: dict[str, np.ndarray] = {}
    null_affinity: dict[str, dict[int, np.ndarray]] = {}
    for corpus, (metadata, values) in panels.items():
        if corpus not in gamma_by_corpus:
            raise ValueError(f"No frozen gamma for {corpus}.")
        d0 = metadata["split"].eq("D0").to_numpy()
        half_a, half_b = _half_masks(
            metadata,
            corpus=corpus,
            seed=spec.seed,
        )
        if min(int(half_a.sum()), int(half_b.sum())) < spec.minimum_half_authors:
            runtime[corpus] = {"status": "D0_HALF_UNDERRESOLVED"}
            continue
        gamma = float(gamma_by_corpus[corpus])
        natural_full = _spectrum(values[d0], gamma=gamma)
        natural_halves = (
            _spectrum(values[half_a], gamma=gamma),
            _spectrum(values[half_b], gamma=gamma),
        )
        top = np.empty(spec.d0_null_draws, dtype=float)
        affinities = {
            rank: np.empty(spec.d0_null_draws, dtype=float)
            for rank in range(1, spec.maximum_rank + 1)
        }
        rng = np.random.default_rng(
            spec.seed
            + stable_bucket(
                corpus,
                salt="v8-filtered-spectrum-d0",
                modulus=2**31 - 1,
            )
        )
        for draw in range(spec.d0_null_draws):
            full = _spectrum(
                _permute_second(values, metadata, d0, rng=rng),
                gamma=gamma,
            )
            left = _spectrum(
                _permute_second(values, metadata, half_a, rng=rng),
                gamma=gamma,
            )
            right = _spectrum(
                _permute_second(values, metadata, half_b, rng=rng),
                gamma=gamma,
            )
            top[draw] = float(full["eigenvalues"][0])
            for rank in affinities:
                affinities[rank][draw] = subspace_affinity(
                    left["loadings"][:, :rank],
                    right["loadings"][:, :rank],
                )
        null_top[corpus] = top
        null_affinity[corpus] = affinities
        runtime[corpus] = {
            "status": "READY",
            "gamma": gamma,
            "d0": d0,
            "half_a": half_a,
            "half_b": half_b,
            "natural_full": natural_full,
            "natural_halves": natural_halves,
        }

    ready = [
        corpus
        for corpus, result in runtime.items()
        if result["status"] == "READY"
    ]
    if not ready:
        return {
            "status": "FILTERED_SPECTRUM_UNDERRESOLVED",
            "discovery": pd.DataFrame(),
            "cells": pd.DataFrame(),
        }
    standardized = np.vstack(
        [
            (null_top[corpus] - null_top[corpus].mean())
            / max(float(null_top[corpus].std(ddof=1)), 1e-12)
            for corpus in ready
        ]
    )
    maximum_z = standardized.max(axis=0)
    maximum_threshold = float(
        np.quantile(maximum_z, spec.spectrum_quantile)
    )
    for corpus in ready:
        result = runtime[corpus]
        eigenvalues = np.asarray(result["natural_full"]["eigenvalues"])
        threshold = float(
            null_top[corpus].mean()
            + maximum_threshold * null_top[corpus].std(ddof=1)
        )
        rank = min(
            int(np.sum(eigenvalues > threshold)),
            spec.maximum_rank,
        )
        stable = False
        affinity = float("nan")
        affinity_threshold = float("nan")
        held_ab = float("nan")
        held_ba = float("nan")
        vectors = np.empty((len(eigenvalues), 0))
        if rank:
            left, right = result["natural_halves"]
            affinity = subspace_affinity(
                left["loadings"][:, :rank],
                right["loadings"][:, :rank],
            )
            affinity_threshold = float(
                np.quantile(
                    null_affinity[corpus][rank],
                    spec.spectrum_quantile,
                )
            )
            left_b, left_w = _operators(
                panels[corpus][1][result["half_a"]]
            )
            right_b, right_w = _operators(
                panels[corpus][1][result["half_b"]]
            )
            held_ab = projected_concordance(
                right_b,
                right_w,
                left["generalized"][:, :rank],
            )
            held_ba = projected_concordance(
                left_b,
                left_w,
                right["generalized"][:, :rank],
            )
            stable = bool(
                affinity > affinity_threshold
                and held_ab > 0
                and held_ba > 0
            )
            if stable:
                vectors = np.asarray(
                    result["natural_full"]["generalized"]
                )[:, :rank]
        positive = np.maximum(eigenvalues, 0.0)
        effective_rank = float(
            positive.sum() ** 2 / max(float(np.sum(positive**2)), 1e-12)
        )
        discovery_rows.append(
            {
                "corpus": corpus,
                "status": (
                    "FILTERED_LOW_DIMENSIONAL_AXIS_RESOLVED"
                    if stable
                    else "FILTERED_LOW_DIMENSIONAL_AXIS_UNDERRESOLVED"
                ),
                "gamma": result["gamma"],
                "positive_threshold": threshold,
                "candidate_rank": rank,
                "stable": stable,
                "affinity": affinity,
                "affinity_threshold": affinity_threshold,
                "held_ab": held_ab,
                "held_ba": held_ba,
                "positive_effective_rank": effective_rank,
                "top1_positive_mass_fraction": float(
                    positive[0] / max(float(positive.sum()), 1e-12)
                ),
            }
        )
        result["vectors"] = vectors

    observed: dict[tuple[str, str], float] = {}
    null: dict[tuple[str, str], np.ndarray] = {}
    for corpus in ready:
        vectors = runtime[corpus]["vectors"]
        if not vectors.size:
            continue
        metadata, values = panels[corpus]
        for split in ("D1", "D2"):
            mask = metadata["split"].eq(split).to_numpy()
            between, within = _operators(values[mask])
            key = (corpus, split)
            observed[key] = projected_concordance(
                between,
                within,
                vectors,
            )
            null[key] = np.empty(spec.test_null_draws, dtype=float)
            rng = np.random.default_rng(
                spec.seed
                + stable_bucket(
                    f"{corpus}-{split}",
                    salt="v8-filtered-spectrum-test",
                    modulus=2**31 - 1,
                )
            )
            for draw in range(spec.test_null_draws):
                permuted = _permute_second(
                    values,
                    metadata,
                    mask,
                    rng=rng,
                )
                pseudo_b, pseudo_w = _operators(permuted)
                null[key][draw] = projected_concordance(
                    pseudo_b,
                    pseudo_w,
                    vectors,
                )

    cell_rows = []
    if observed:
        standardized_null = []
        observed_z = []
        keys = list(observed)
        for key in keys:
            standard = max(float(null[key].std(ddof=1)), 1e-12)
            standardized_null.append(
                (null[key] - null[key].mean()) / standard
            )
            observed_z.append(
                (observed[key] - null[key].mean()) / standard
            )
        maximum = np.max(np.vstack(standardized_null), axis=0)
        for index, key in enumerate(keys):
            corpus, split = key
            metadata, values = panels[corpus]
            mask = metadata["split"].eq(split).to_numpy()
            null_mean = float(null[key].mean())
            lcb = _bootstrap_projected_excess(
                values,
                metadata,
                mask,
                runtime[corpus]["vectors"],
                null_mean=null_mean,
                draws=spec.bootstrap_draws,
                rng=np.random.default_rng(
                    spec.seed
                    + stable_bucket(
                        f"{corpus}-{split}",
                        salt="v8-filtered-spectrum-bootstrap",
                        modulus=2**31 - 1,
                    )
                ),
            )
            cell_rows.append(
                {
                    "corpus": corpus,
                    "split": split,
                    "observed": observed[key],
                    "null_mean": null_mean,
                    "excess": observed[key] - null_mean,
                    "max_t_p": float(
                        (1 + np.sum(maximum >= observed_z[index]))
                        / (len(maximum) + 1)
                    ),
                    "bootstrap_lcb": lcb,
                }
            )
    cells = pd.DataFrame(
        cell_rows,
        columns=(
            "corpus",
            "split",
            "observed",
            "null_mean",
            "excess",
            "max_t_p",
            "bootstrap_lcb",
        ),
    )
    discovery = pd.DataFrame(discovery_rows)
    replicated = []
    for corpus in ready:
        selected = cells.loc[cells["corpus"].eq(corpus)]
        replicated.append(
            bool(
                len(selected) == 2
                and selected["excess"].gt(0).all()
                and selected["max_t_p"].le(0.05).all()
                and selected["bootstrap_lcb"].gt(0).all()
            )
        )
    return {
        "status": (
            "FILTERED_LOW_DIMENSIONAL_SPECTRUM_REPLICATED"
            if any(replicated)
            else "FILTERED_CONCORDANCE_HIGH_DIMENSIONAL_OR_UNDERRESOLVED"
        ),
        "discovery": discovery,
        "cells": cells,
    }
