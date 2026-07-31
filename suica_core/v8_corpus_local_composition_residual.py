"""Corpus-local stable composition residual after marginal-orbit calibration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from suica_core.v8_event_set_composition_knockout import (
    EventTensor,
    permuted_k_features_batch,
    pseudo_set_reallocation,
)
from suica_core.v8_orientation_overlap import _eigensystem
from suica_core.v8_realtext_relation_field import (
    RealTextRelationSpec,
    frozen_random_directions,
    replicated_covariance,
)


@dataclass(frozen=True)
class LocalCompositionSpec:
    """Frozen D0 calibration and corpus-local pseudo-world budgets."""

    baseline_draws: int = 99
    null_draws: int = 199
    rank: int = 10
    local_length_block: int = 16
    seed: int = 20260816

    def __post_init__(self) -> None:
        if self.baseline_draws < 49 or self.null_draws < 99:
            raise ValueError("Insufficient composition-residual null budget.")
        if self.rank < 2:
            raise ValueError("rank must be at least two.")
        if self.local_length_block < 4:
            raise ValueError("local_length_block must be at least four.")


def _feature_batches(
    vectors: np.ndarray,
    *,
    directions: tuple[np.ndarray, np.ndarray, np.ndarray],
    feature_scale: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    return tuple(
        permuted_k_features_batch(
            vectors[:, offset::2, :],
            directions=directions,
        )
        / feature_scale[None, None, :]
        for offset in (0, 1)
    )


def fit_corpus_basis(
    tensor: EventTensor,
    *,
    split: str,
    directions: tuple[np.ndarray, np.ndarray, np.ndarray],
    feature_scale: np.ndarray,
    rank: int,
) -> np.ndarray:
    """Fit a corpus-local K susceptibility basis on natural D0 sets."""
    mask = tensor.metadata["split"].eq(split).to_numpy()
    features = _feature_batches(
        tensor.vectors[mask],
        directions=directions,
        feature_scale=feature_scale,
    )
    flattened = np.concatenate(features, axis=0).reshape(
        -1,
        features[0].shape[-1],
    )
    covariance = flattened.T @ flattened / max(1, len(flattened))
    values, vectors = _eigensystem(covariance)
    if int(np.sum(values > 1e-12)) < rank:
        raise ValueError("LOCAL_COMPOSITION_BASIS_UNDERRESOLVED")
    return vectors[:, :rank]


def _symmetric_coordinates(projected: np.ndarray) -> np.ndarray:
    covariance = np.einsum(
        "npi,npj->nij",
        projected,
        projected,
        optimize=True,
    ) / projected.shape[1]
    rank = covariance.shape[-1]
    rows, columns = np.triu_indices(rank)
    result = covariance[:, rows, columns]
    off_diagonal = rows != columns
    result[:, off_diagonal] *= np.sqrt(2.0)
    return result


def operator_coordinates(
    tensor: EventTensor,
    *,
    split: str,
    basis: np.ndarray,
    directions: tuple[np.ndarray, np.ndarray, np.ndarray],
    feature_scale: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return per-author, per-replicate signed-operator coordinates."""
    mask = tensor.metadata["split"].eq(split).to_numpy()
    features = _feature_batches(
        tensor.vectors[mask],
        directions=directions,
        feature_scale=feature_scale,
    )
    coordinates = np.stack(
        [
            _symmetric_coordinates(values @ basis)
            for values in features
        ],
        axis=1,
    )
    contexts = tensor.metadata.loc[mask, "context"].astype(str).to_numpy()
    return coordinates, contexts


def fit_pseudo_baseline(
    tensor: EventTensor,
    *,
    basis: np.ndarray,
    directions: tuple[np.ndarray, np.ndarray, np.ndarray],
    feature_scale: np.ndarray,
    spec: LocalCompositionSpec,
    rng: np.random.Generator,
) -> dict[tuple[str, int], np.ndarray]:
    """Estimate context/replicate marginal-orbit means from D0 pseudo sets."""
    totals: dict[tuple[str, int], np.ndarray] = {}
    counts: dict[tuple[str, int], int] = {}
    for _ in range(spec.baseline_draws):
        pseudo, _ = pseudo_set_reallocation(
            tensor,
            block_size=spec.local_length_block,
            rng=rng,
        )
        pseudo_tensor = EventTensor(tensor.metadata, pseudo, tensor.lengths)
        coordinates, contexts = operator_coordinates(
            pseudo_tensor,
            split="D0",
            basis=basis,
            directions=directions,
            feature_scale=feature_scale,
        )
        for context in np.unique(contexts):
            mask = contexts == context
            for replicate in range(2):
                key = (str(context), replicate)
                value = coordinates[mask, replicate].sum(axis=0)
                totals[key] = totals.get(key, np.zeros_like(value)) + value
                counts[key] = counts.get(key, 0) + int(np.sum(mask))
    return {key: totals[key] / counts[key] for key in totals}


def residual_coordinates(
    coordinates: np.ndarray,
    contexts: np.ndarray,
    baseline: dict[tuple[str, int], np.ndarray],
) -> np.ndarray:
    """Subtract the D0 pseudo marginal baseline without PSD projection."""
    result = coordinates.copy()
    for row, context in enumerate(contexts):
        for replicate in range(2):
            key = (str(context), replicate)
            if key not in baseline:
                raise ValueError(f"No D0 pseudo baseline for context {context}.")
            result[row, replicate] -= baseline[key]
    return result


def signed_replicate_strength(residuals: np.ndarray) -> float:
    """Frobenius norm of signed cross-replicate covariance."""
    covariance = replicated_covariance(residuals[:, 0], residuals[:, 1])
    return float(np.linalg.norm(covariance, ord="fro"))


def evaluate_corpus_local_composition(
    tensors: dict[str, EventTensor],
    *,
    feature_spec: RealTextRelationSpec,
    feature_scale: np.ndarray,
    spec: LocalCompositionSpec,
) -> dict[str, Any]:
    """Test stable composition residuals separately within each corpus."""
    feature_scale = np.asarray(feature_scale, dtype=float)
    event_dimension = next(iter(tensors.values())).vectors.shape[-1]
    expected_features = 2 * event_dimension + 3 * feature_spec.random_directions
    if feature_scale.shape != (expected_features,):
        raise ValueError("feature_scale does not match the K feature dimension.")
    directions = frozen_random_directions(
        event_dimensions=event_dimension,
        count=feature_spec.random_directions,
        seed=feature_spec.seed + 17,
    )
    rng = np.random.default_rng(spec.seed)
    observed: dict[tuple[str, str], float] = {}
    null_values: dict[tuple[str, str], list[float]] = {}
    diagnostic_rows = []
    runtime = {}
    for corpus, tensor in tensors.items():
        basis = fit_corpus_basis(
            tensor,
            split="D0",
            directions=directions,
            feature_scale=feature_scale,
            rank=spec.rank,
        )
        baseline = fit_pseudo_baseline(
            tensor,
            basis=basis,
            directions=directions,
            feature_scale=feature_scale,
            spec=spec,
            rng=rng,
        )
        runtime[corpus] = (basis, baseline)
        for split in ("D1", "D2"):
            coordinates, contexts = operator_coordinates(
                tensor,
                split=split,
                basis=basis,
                directions=directions,
                feature_scale=feature_scale,
            )
            observed[(corpus, split)] = signed_replicate_strength(
                residual_coordinates(coordinates, contexts, baseline)
            )
            null_values[(corpus, split)] = []

    for draw in range(spec.null_draws):
        for corpus, tensor in tensors.items():
            basis, baseline = runtime[corpus]
            pseudo, diagnostics = pseudo_set_reallocation(
                tensor,
                block_size=spec.local_length_block,
                rng=rng,
            )
            pseudo_tensor = EventTensor(tensor.metadata, pseudo, tensor.lengths)
            diagnostic_rows.append(
                {
                    "draw": draw,
                    "corpus": corpus,
                    "same_author": int(diagnostics["same_author"].sum()),
                    "mean_absolute_length_difference": float(
                        np.average(
                            diagnostics["mean_absolute_length_difference"],
                            weights=diagnostics["block_size"],
                        )
                    ),
                }
            )
            for split in ("D1", "D2"):
                coordinates, contexts = operator_coordinates(
                    pseudo_tensor,
                    split=split,
                    basis=basis,
                    directions=directions,
                    feature_scale=feature_scale,
                )
                null_values[(corpus, split)].append(
                    signed_replicate_strength(
                        residual_coordinates(coordinates, contexts, baseline)
                    )
                )

    rows = []
    standardized_nulls = []
    observed_z = []
    keys = []
    null_rows = []
    for key, values_list in null_values.items():
        corpus, split = key
        values = np.asarray(values_list)
        score = observed[key]
        mean = float(values.mean())
        standard = max(float(values.std(ddof=1)), 1e-12)
        standardized_nulls.append((values - mean) / standard)
        observed_z.append((score - mean) / standard)
        keys.append(key)
        rows.append(
            {
                "corpus": corpus,
                "split": split,
                "rank": spec.rank,
                "observed_signed_frobenius": score,
                "pseudo_mean": mean,
                "observed_minus_pseudo": score - mean,
                "raw_p": float(
                    (1 + np.sum(values >= score)) / (len(values) + 1)
                ),
            }
        )
        null_rows.extend(
            {
                "draw": draw,
                "corpus": corpus,
                "split": split,
                "score": value,
            }
            for draw, value in enumerate(values)
        )
    maxima = np.max(np.vstack(standardized_nulls), axis=0)
    cells = pd.DataFrame(rows)
    cells["max_t_p"] = [
        float((1 + np.sum(maxima >= value)) / (len(maxima) + 1))
        for value in observed_z
    ]
    corpus_status = {}
    for corpus in tensors:
        rows_for_corpus = cells["corpus"].eq(corpus)
        corpus_status[corpus] = bool(
            cells.loc[rows_for_corpus, "observed_minus_pseudo"].gt(0).all()
            and cells.loc[rows_for_corpus, "max_t_p"].le(0.05).all()
        )
    if all(corpus_status.values()):
        status = "BOTH_CORPORA_LOCAL_COMPOSITION_RESIDUAL_DETECTED"
    elif any(corpus_status.values()):
        status = "ONE_CORPUS_LOCAL_COMPOSITION_RESIDUAL_DETECTED"
    else:
        status = "CORPUS_LOCAL_COMPOSITION_RESIDUAL_NOT_DETECTED"
    return {
        "status": status,
        "corpus_status": corpus_status,
        "cells": cells,
        "null_scores": pd.DataFrame(null_rows),
        "diagnostics": pd.DataFrame(diagnostic_rows),
    }
