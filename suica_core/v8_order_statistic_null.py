"""Exact-inner, statistic-level order null for K-family orientation."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from typing import Any

import numpy as np
import pandas as pd

from suica_core.v8_orientation_overlap import (
    OrientationOverlapSpec,
    _eigensystem,
    calibrate_epsilon,
    fit_orientation_template,
    orientation_metrics,
)
from suica_core.v8_realtext_relation_field import (
    RealTextRelationSpec,
    assign_d0_d1_d2,
    family_features,
    frozen_event_vector,
    frozen_random_directions,
)
from suica_core.v8_spectral_order_replay import fit_shared_gauge
from suica_core.v8_support_containment import (
    _stable_indices,
    replicated_density,
)


PERMUTATIONS_4 = np.asarray(list(permutations(range(4))), dtype=np.int8)


@dataclass(frozen=True)
class ExactPermutationPanel:
    """Per-author exact-centered K features for all 4! path permutations."""

    metadata: pd.DataFrame
    residuals: np.ndarray

    @property
    def native(self) -> np.ndarray:
        return self.residuals[:, :, 0, :]


@dataclass(frozen=True)
class OrderStatisticNullSpec:
    """Frozen exact-inner and outer randomization budgets."""

    calibration_draws: int = 99
    outer_draws: int = 1999
    rank: int = 10
    maximum_underresolved_fraction: float = 0.05
    seed: int = 20260812

    def __post_init__(self) -> None:
        if self.calibration_draws < 19 or self.outer_draws < 99:
            raise ValueError("Insufficient order-null resampling budget.")
        if self.rank < 2:
            raise ValueError("rank must be at least two.")
        if not 0 <= self.maximum_underresolved_fraction < 1:
            raise ValueError("Invalid underresolved fraction.")


def build_exact_permutation_panel(
    event_rows: pd.DataFrame,
    *,
    corpus: str,
    feature_spec: RealTextRelationSpec,
) -> ExactPermutationPanel:
    """Precompute exact-centered K for every within-replicate permutation."""
    required = {"author_id", "context", "order", "text"}
    if not required.issubset(event_rows.columns):
        raise ValueError(f"event_rows must contain {sorted(required)}")
    directions = frozen_random_directions(
        event_dimensions=2 * feature_spec.hash_dimensions,
        count=feature_spec.random_directions,
        seed=feature_spec.seed + 17,
    )
    split_map = assign_d0_d1_d2(
        event_rows["author_id"].astype(str).unique(),
        salt=f"v8rt-{corpus}-{feature_spec.seed}",
    )
    metadata_rows = []
    residual_rows = []
    grouped = event_rows.sort_values(
        ["author_id", "order"],
        kind="stable",
    ).groupby("author_id", observed=True, sort=False)
    for author, group in grouped:
        if len(group) != 8:
            continue
        contexts = group["context"].astype(str).unique()
        if len(contexts) != 1:
            continue
        vectors = np.vstack(
            [
                frozen_event_vector(
                    text,
                    dimensions=feature_spec.hash_dimensions,
                )
                for text in group["text"].astype(str)
            ]
        )
        replicate_rows = []
        for offset in (0, 1):
            path = vectors[offset::2]
            if len(path) != 4:
                break
            features = np.stack(
                [
                    family_features(
                        path[order],
                        marginal_directions=directions[0],
                        transition_directions=directions[1],
                        current_directions=directions[2],
                    )["K"]
                    for order in PERMUTATIONS_4
                ]
            )
            replicate_rows.append(features - features.mean(axis=0, keepdims=True))
        if len(replicate_rows) != 2:
            continue
        metadata_rows.append(
            {
                "corpus": corpus,
                "author_id": str(author),
                "context": str(contexts[0]),
                "split": split_map[str(author)],
            }
        )
        residual_rows.append(np.stack(replicate_rows).astype(np.float32))
    if not residual_rows:
        raise ValueError(f"No exact permutation paths for {corpus}.")
    return ExactPermutationPanel(
        metadata=pd.DataFrame(metadata_rows),
        residuals=np.stack(residual_rows),
    )


def _split_panel(
    panel: ExactPermutationPanel,
    split: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mask = panel.metadata["split"].eq(split).to_numpy()
    return (
        panel.native[mask],
        panel.residuals[mask],
        panel.metadata.loc[mask, "author_id"].astype(str).to_numpy(),
    )


def _select_aligned(
    left: tuple[np.ndarray, np.ndarray, np.ndarray],
    right: tuple[np.ndarray, np.ndarray, np.ndarray],
    *,
    salt: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    count = min(len(left[0]), len(right[0]))
    left_indices = _stable_indices(left[2], count, salt=f"{salt}-left")
    right_indices = _stable_indices(right[2], count, salt=f"{salt}-right")
    return (
        left[0][left_indices],
        left[1][left_indices],
        right[0][right_indices],
        right[1][right_indices],
    )


def _matched_metrics(
    left_raw: np.ndarray,
    right_raw: np.ndarray,
    *,
    center: np.ndarray,
    scale: np.ndarray,
    rank: int,
    weights: np.ndarray,
) -> tuple[dict[str, float], bool]:
    left_density, _, left_rank = replicated_density(
        left_raw,
        center=center,
        scale=scale,
    )
    right_density, _, right_rank = replicated_density(
        right_raw,
        center=center,
        scale=scale,
    )
    underresolved = left_rank < rank or right_rank < rank
    _, left_vectors = _eigensystem(left_density)
    _, right_vectors = _eigensystem(right_density)
    return (
        orientation_metrics(
            left_vectors[:, :rank],
            right_vectors[:, :rank],
            weights,
            weights,
        ),
        underresolved,
    )


def evaluate_statistic_level_order_null(
    left: ExactPermutationPanel,
    right: ExactPermutationPanel,
    *,
    spec: OrderStatisticNullSpec,
) -> dict[str, Any]:
    """Evaluate native order against the complete statistic-level null."""
    left_d0 = _split_panel(left, "D0")
    right_d0 = _split_panel(right, "D0")
    gauge = fit_shared_gauge(
        left_d0[0],
        left_d0[2],
        right_d0[0],
        right_d0[2],
        salt=f"v8-order-statistic-null-{spec.seed}",
    )
    rng = np.random.default_rng(spec.seed)
    epsilon, _ = calibrate_epsilon(
        gauge,
        draws=spec.calibration_draws,
        rng=rng,
    )
    try:
        template = fit_orientation_template(
            gauge,
            epsilon,
            maximum_rank=spec.rank,
            minimum_rank=spec.rank,
        )
    except ValueError as error:
        return {
            "status": str(error),
            "epsilon": epsilon,
            "rank": None,
            "cells": pd.DataFrame(),
            "null_scores": pd.DataFrame(),
        }

    stages = {}
    native_rows = []
    for split in ("D1", "D2"):
        stages[split] = _select_aligned(
            _split_panel(left, split),
            _split_panel(right, split),
            salt=f"v8-order-statistic-null-{split}",
        )
        metrics, underresolved = _matched_metrics(
            stages[split][0],
            stages[split][2],
            center=gauge.center,
            scale=gauge.scale,
            rank=spec.rank,
            weights=template.weights,
        )
        if underresolved:
            return {
                "status": "NATIVE_ORDER_DENSITY_UNDERRESOLVED",
                "epsilon": epsilon,
                "rank": spec.rank,
                "cells": pd.DataFrame(),
                "null_scores": pd.DataFrame(),
            }
        for metric in ("hs", "fidelity"):
            native_rows.append(
                {
                    "split": split,
                    "metric": metric,
                    "native": metrics[metric],
                }
            )
    native = pd.DataFrame(native_rows)
    native_lookup = {
        (row["split"], row["metric"]): float(row["native"])
        for _, row in native.iterrows()
    }

    null_rows = []
    underresolved = {(split, metric): 0 for split in ("D1", "D2") for metric in ("hs", "fidelity")}
    for draw in range(spec.outer_draws):
        for split in ("D1", "D2"):
            left_native, left_residuals, right_native, right_residuals = stages[split]
            if draw == 0:
                left_raw = left_native
                right_raw = right_native
            else:
                left_choices = rng.integers(
                    0,
                    len(PERMUTATIONS_4),
                    size=(len(left_residuals), 2),
                )
                right_choices = rng.integers(
                    0,
                    len(PERMUTATIONS_4),
                    size=(len(right_residuals), 2),
                )
                author_index_left = np.arange(len(left_residuals))[:, None]
                author_index_right = np.arange(len(right_residuals))[:, None]
                replicate_index = np.arange(2)[None, :]
                left_raw = left_residuals[
                    author_index_left,
                    replicate_index,
                    left_choices,
                ]
                right_raw = right_residuals[
                    author_index_right,
                    replicate_index,
                    right_choices,
                ]
            metrics, unresolved = _matched_metrics(
                left_raw,
                right_raw,
                center=gauge.center,
                scale=gauge.scale,
                rank=spec.rank,
                weights=template.weights,
            )
            for metric in ("hs", "fidelity"):
                underresolved[(split, metric)] += int(unresolved)
                null_rows.append(
                    {
                        "draw": draw,
                        "split": split,
                        "metric": metric,
                        "score": metrics[metric],
                        "underresolved": int(unresolved),
                    }
                )
    null_scores = pd.DataFrame(null_rows)
    cells = []
    standardized_nulls = []
    standardized_native = []
    keys = []
    for split in ("D1", "D2"):
        for metric in ("hs", "fidelity"):
            values = null_scores.loc[
                null_scores["split"].eq(split)
                & null_scores["metric"].eq(metric),
                "score",
            ].to_numpy()
            observed = native_lookup[(split, metric)]
            mean = float(values.mean())
            standard = max(float(values.std(ddof=1)), 1e-12)
            standardized_nulls.append((values - mean) / standard)
            standardized_native.append((observed - mean) / standard)
            keys.append((split, metric, observed, mean, standard))
    maxima = np.max(np.vstack(standardized_nulls), axis=0)
    for key, z_value in zip(keys, standardized_native):
        split, metric, observed, mean, standard = key
        values = null_scores.loc[
            null_scores["split"].eq(split)
            & null_scores["metric"].eq(metric),
            "score",
        ].to_numpy()
        cells.append(
            {
                "split": split,
                "metric": metric,
                "rank": spec.rank,
                "native": observed,
                "null_mean": mean,
                "native_minus_null": observed - mean,
                "raw_randomization_p": float(
                    (1 + np.sum(values >= observed)) / (len(values) + 1)
                ),
                "max_t_p": float(
                    (1 + np.sum(maxima >= z_value)) / (len(maxima) + 1)
                ),
                "null_standard_deviation": standard,
                "underresolved_fraction": (
                    underresolved[(split, metric)] / spec.outer_draws
                ),
            }
        )
    cells_frame = pd.DataFrame(cells)
    if cells_frame["underresolved_fraction"].max() > spec.maximum_underresolved_fraction:
        status = "ORDER_NULL_DENSITY_UNDERRESOLVED"
    elif (
        cells_frame["native_minus_null"].gt(0).all()
        and cells_frame["max_t_p"].le(0.05).all()
    ):
        status = "STATISTIC_LEVEL_ORDER_EXCESS_DETECTED"
    else:
        status = "STATISTIC_LEVEL_ORDER_EXCESS_NOT_DETECTED"
    return {
        "status": status,
        "epsilon": epsilon,
        "rank": spec.rank,
        "cells": cells_frame,
        "null_scores": null_scores,
    }
