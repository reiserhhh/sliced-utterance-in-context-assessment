"""Event-set composition knockout for permutation-susceptibility geometry."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from suica_core.v8_order_statistic_null import PERMUTATIONS_4
from suica_core.v8_orientation_overlap import _eigensystem, orientation_metrics
from suica_core.v8_realtext_relation_field import (
    RealTextRelationSpec,
    assign_d0_d1_d2,
    frozen_event_vector,
    frozen_random_directions,
)
from suica_core.v8_support_containment import _stable_indices


@dataclass(frozen=True)
class EventTensor:
    """Eight ordered event vectors and lengths for each eligible author."""

    metadata: pd.DataFrame
    vectors: np.ndarray
    lengths: np.ndarray


@dataclass(frozen=True)
class CompositionKnockoutSpec:
    """Frozen pseudo-set and randomization settings."""

    draws: int = 199
    rank: int = 10
    local_length_block: int = 16
    reference_orbit_seed: int = 20260813
    seed: int = 20260815

    def __post_init__(self) -> None:
        if self.draws < 99:
            raise ValueError("At least 99 pseudo-set worlds are required.")
        if self.rank < 2:
            raise ValueError("rank must be at least two.")
        if self.local_length_block < 4:
            raise ValueError("local_length_block must be at least four.")


def build_event_tensor(
    event_rows: pd.DataFrame,
    *,
    corpus: str,
    feature_spec: RealTextRelationSpec,
    expected_events: int = 8,
) -> EventTensor:
    """Convert selected text events into one author x order vector tensor."""
    required = {"author_id", "context", "order", "text"}
    if not required.issubset(event_rows.columns):
        raise ValueError(f"event_rows must contain {sorted(required)}")
    if expected_events < 4 or expected_events % 2:
        raise ValueError("expected_events must be an even integer >= 4.")
    split_map = assign_d0_d1_d2(
        event_rows["author_id"].astype(str).unique(),
        salt=f"v8rt-{corpus}-{feature_spec.seed}",
    )
    metadata = []
    vectors = []
    lengths = []
    grouped = event_rows.sort_values(
        ["author_id", "order"],
        kind="stable",
    ).groupby("author_id", observed=True, sort=False)
    for author, group in grouped:
        if (
            len(group) != expected_events
            or group["context"].astype(str).nunique() != 1
        ):
            continue
        metadata.append(
            {
                "corpus": corpus,
                "author_id": str(author),
                "context": str(group.iloc[0]["context"]),
                "split": split_map[str(author)],
            }
        )
        texts = group["text"].astype(str).tolist()
        vectors.append(
            np.vstack(
                [
                    frozen_event_vector(
                        text,
                        dimensions=feature_spec.hash_dimensions,
                    )
                    for text in texts
                ]
            )
        )
        lengths.append([len(text.split()) for text in texts])
    if not vectors:
        raise ValueError(
            f"No {expected_events}-event authors available for {corpus}."
        )
    return EventTensor(
        metadata=pd.DataFrame(metadata),
        vectors=np.stack(vectors).astype(np.float32),
        lengths=np.asarray(lengths, dtype=np.int32),
    )


def permuted_k_features_batch(
    paths: np.ndarray,
    *,
    directions: tuple[np.ndarray, np.ndarray, np.ndarray],
) -> np.ndarray:
    """Compute K for every permutation of a batch of four-event paths."""
    values = np.asarray(paths, dtype=float)
    if values.ndim != 3 or values.shape[1] != 4:
        raise ValueError("paths must have shape author x 4 x event_dimension.")
    ordered = values[:, PERMUTATIONS_4, :]
    previous = ordered[:, :, :-1, :]
    following = ordered[:, :, 1:, :]
    delta = following - previous
    lag_product = np.mean(previous * following, axis=2)
    delta_variance = np.mean(
        (delta - delta.mean(axis=2, keepdims=True)) ** 2,
        axis=2,
    )
    pairs = np.concatenate([previous, following], axis=-1)
    transition_phase = pairs @ directions[1].T
    transition_rff = np.concatenate(
        [
            np.mean(np.cos(transition_phase), axis=2),
            np.mean(np.sin(transition_phase), axis=2),
        ],
        axis=-1,
    )
    previous_first = previous @ directions[2][:, 0, :].T
    previous_second = previous @ directions[2][:, 1, :].T
    following_first = following @ directions[2][:, 0, :].T
    following_second = following @ directions[2][:, 1, :].T
    currents = np.mean(
        np.tanh(previous_first) * np.tanh(following_second)
        - np.tanh(previous_second) * np.tanh(following_first),
        axis=2,
    )
    result = np.concatenate(
        [lag_product, delta_variance, transition_rff, currents],
        axis=-1,
    )
    return result - result.mean(axis=1, keepdims=True)


def pseudo_set_reallocation(
    tensor: EventTensor,
    *,
    block_size: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, pd.DataFrame]:
    """Reassign each order slot within split/context/local-length blocks."""
    result = np.empty_like(tensor.vectors)
    diagnostics = []
    metadata = tensor.metadata.reset_index(drop=True)
    for split in ("D0", "D1", "D2"):
        for context in metadata.loc[
            metadata["split"].eq(split),
            "context",
        ].unique():
            indices = metadata.index[
                metadata["split"].eq(split)
                & metadata["context"].eq(context)
            ].to_numpy()
            if len(indices) < 2:
                raise ValueError("Pseudo-set stratum cannot be deranged.")
            for order in range(tensor.vectors.shape[1]):
                ordered = indices[
                    np.argsort(tensor.lengths[indices, order], kind="stable")
                ]
                block_count = max(1, len(ordered) // int(block_size))
                for block in np.array_split(ordered, block_count):
                    if len(block) < 2:
                        raise ValueError("Local length block cannot be deranged.")
                    shift = int(rng.integers(1, len(block)))
                    donors = np.roll(block, shift)
                    result[block, order] = tensor.vectors[donors, order]
                    diagnostics.append(
                        {
                            "split": split,
                            "context": str(context),
                            "order": order,
                            "block_size": len(block),
                            "same_author": int(np.sum(block == donors)),
                            "mean_absolute_length_difference": float(
                                np.mean(
                                    np.abs(
                                        tensor.lengths[block, order]
                                        - tensor.lengths[donors, order]
                                    )
                                )
                            ),
                        }
                    )
    return result, pd.DataFrame(diagnostics)


def _split_set_covariance(
    vectors: np.ndarray,
    metadata: pd.DataFrame,
    split: str,
    *,
    directions: tuple[np.ndarray, np.ndarray, np.ndarray],
    feature_scale: np.ndarray,
) -> np.ndarray:
    mask = metadata["split"].eq(split).to_numpy()
    selected = vectors[mask]
    features = [
        permuted_k_features_batch(
            selected[:, offset::2, :],
            directions=directions,
        ) / feature_scale[None, None, :]
        for offset in (0, 1)
    ]
    stacked = np.concatenate(features, axis=0)
    flattened = stacked.reshape(-1, stacked.shape[-1])
    return flattened.T @ flattened / max(1, len(flattened))


def _matched_tensors(
    left: EventTensor,
    right: EventTensor,
    split: str,
    *,
    salt: str,
) -> tuple[EventTensor, EventTensor]:
    left_mask = left.metadata["split"].eq(split).to_numpy()
    right_mask = right.metadata["split"].eq(split).to_numpy()
    left_ids = left.metadata.loc[left_mask, "author_id"].astype(str).to_numpy()
    right_ids = right.metadata.loc[right_mask, "author_id"].astype(str).to_numpy()
    count = min(len(left_ids), len(right_ids))
    left_indices = np.flatnonzero(left_mask)[
        _stable_indices(left_ids, count, salt=f"{salt}-left")
    ]
    right_indices = np.flatnonzero(right_mask)[
        _stable_indices(right_ids, count, salt=f"{salt}-right")
    ]

    def selected(tensor: EventTensor, indices: np.ndarray) -> EventTensor:
        return EventTensor(
            metadata=tensor.metadata.iloc[indices].reset_index(drop=True),
            vectors=tensor.vectors[indices],
            lengths=tensor.lengths[indices],
        )

    return selected(left, left_indices), selected(right, right_indices)


def _metrics_from_covariances(
    left: np.ndarray,
    right: np.ndarray,
    *,
    rank: int,
    weights: np.ndarray,
) -> dict[str, float]:
    left_values, left_vectors = _eigensystem(left)
    right_values, right_vectors = _eigensystem(right)
    if min(
        int(np.sum(left_values > 1e-12)),
        int(np.sum(right_values > 1e-12)),
    ) < rank:
        raise ValueError("COMPOSITION_GEOMETRY_RANK_UNDERRESOLVED")
    return orientation_metrics(
        left_vectors[:, :rank],
        right_vectors[:, :rank],
        weights,
        weights,
    )


def evaluate_composition_knockout(
    left: EventTensor,
    right: EventTensor,
    *,
    feature_spec: RealTextRelationSpec,
    feature_scale: np.ndarray,
    spec: CompositionKnockoutSpec,
) -> dict[str, Any]:
    """Compare natural event sets with matched pseudo-set reallocations."""
    feature_scale = np.asarray(feature_scale, dtype=float)
    directions = frozen_random_directions(
        event_dimensions=left.vectors.shape[-1],
        count=feature_spec.random_directions,
        seed=feature_spec.seed + 17,
    )
    expected_features = (
        2 * left.vectors.shape[-1] + 3 * feature_spec.random_directions
    )
    if feature_scale.shape != (expected_features,):
        raise ValueError("feature_scale does not match the K feature dimension.")
    aligned = {
        split: _matched_tensors(
            left,
            right,
            split,
            salt=f"v8-orbit-set-{split}-{spec.reference_orbit_seed}",
        )
        for split in ("D0", "D1", "D2")
    }
    d0_left = _split_set_covariance(
        aligned["D0"][0].vectors,
        aligned["D0"][0].metadata,
        "D0",
        directions=directions,
        feature_scale=feature_scale,
    )
    d0_right = _split_set_covariance(
        aligned["D0"][1].vectors,
        aligned["D0"][1].metadata,
        "D0",
        directions=directions,
        feature_scale=feature_scale,
    )
    left_values, _ = _eigensystem(d0_left)
    right_values, _ = _eigensystem(d0_right)
    weights = np.sqrt(
        np.clip(left_values[: spec.rank], 0.0, None)
        * np.clip(right_values[: spec.rank], 0.0, None)
    )
    if len(weights) < spec.rank or float(weights.sum()) <= 1e-12:
        return {
            "status": "COMPOSITION_GEOMETRY_RANK_UNDERRESOLVED",
            "cells": pd.DataFrame(),
            "null_scores": pd.DataFrame(),
            "diagnostics": pd.DataFrame(),
        }
    weights /= weights.sum()
    observed = {}
    for split in ("D1", "D2"):
        left_tensor, right_tensor = aligned[split]
        observed[split] = _metrics_from_covariances(
            _split_set_covariance(
                left_tensor.vectors,
                left_tensor.metadata,
                split,
                directions=directions,
                feature_scale=feature_scale,
            ),
            _split_set_covariance(
                right_tensor.vectors,
                right_tensor.metadata,
                split,
                directions=directions,
                feature_scale=feature_scale,
            ),
            rank=spec.rank,
            weights=weights,
        )

    rng = np.random.default_rng(spec.seed)
    null_rows = []
    diagnostic_rows = []
    for draw in range(spec.draws):
        for corpus, tensor_by_split in (
            ("left", {key: value[0] for key, value in aligned.items()}),
            ("right", {key: value[1] for key, value in aligned.items()}),
        ):
            for split, tensor in tensor_by_split.items():
                pseudo, diagnostic = pseudo_set_reallocation(
                    tensor,
                    block_size=spec.local_length_block,
                    rng=rng,
                )
                tensor_by_split[split] = EventTensor(
                    tensor.metadata,
                    pseudo,
                    tensor.lengths,
                )
                diagnostic_rows.append(
                    {
                        "draw": draw,
                        "corpus": corpus,
                        "split": split,
                        "same_author": int(diagnostic["same_author"].sum()),
                        "mean_absolute_length_difference": float(
                            np.average(
                                diagnostic["mean_absolute_length_difference"],
                                weights=diagnostic["block_size"],
                            )
                        ),
                    }
                )
            if corpus == "left":
                pseudo_left = tensor_by_split
            else:
                pseudo_right = tensor_by_split
        for split in ("D1", "D2"):
            metrics = _metrics_from_covariances(
                _split_set_covariance(
                    pseudo_left[split].vectors,
                    pseudo_left[split].metadata,
                    split,
                    directions=directions,
                    feature_scale=feature_scale,
                ),
                _split_set_covariance(
                    pseudo_right[split].vectors,
                    pseudo_right[split].metadata,
                    split,
                    directions=directions,
                    feature_scale=feature_scale,
                ),
                rank=spec.rank,
                weights=weights,
            )
            for metric in ("hs", "fidelity"):
                null_rows.append(
                    {
                        "draw": draw,
                        "split": split,
                        "metric": metric,
                        "score": metrics[metric],
                    }
                )
    null_scores = pd.DataFrame(null_rows)
    rows = []
    standardized_nulls = []
    observed_z = []
    keys = []
    for split in ("D1", "D2"):
        for metric in ("hs", "fidelity"):
            values = null_scores.loc[
                null_scores["split"].eq(split)
                & null_scores["metric"].eq(metric),
                "score",
            ].to_numpy()
            score = float(observed[split][metric])
            mean = float(values.mean())
            standard = max(float(values.std(ddof=1)), 1e-12)
            standardized_nulls.append((values - mean) / standard)
            observed_z.append((score - mean) / standard)
            keys.append((split, metric))
            rows.append(
                {
                    "split": split,
                    "metric": metric,
                    "rank": spec.rank,
                    "observed": score,
                    "pseudo_mean": mean,
                    "observed_minus_pseudo": score - mean,
                    "raw_p": float(
                        (1 + np.sum(values >= score)) / (len(values) + 1)
                    ),
                }
            )
    maxima = np.max(np.vstack(standardized_nulls), axis=0)
    cells = pd.DataFrame(rows)
    cells["max_t_p"] = [
        float((1 + np.sum(maxima >= value)) / (len(maxima) + 1))
        for value in observed_z
    ]
    if (
        cells["observed_minus_pseudo"].gt(0).all()
        and cells["max_t_p"].le(0.05).all()
    ):
        status = "NATURAL_EVENT_SET_COMPOSITION_EXCESS_DETECTED"
    else:
        status = "NATURAL_EVENT_SET_COMPOSITION_EXCESS_NOT_DETECTED"
    return {
        "status": status,
        "cells": cells,
        "null_scores": null_scores,
        "diagnostics": pd.DataFrame(diagnostic_rows),
    }
