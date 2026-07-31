"""Within-replicate order-shuffle knockout for K-family orientation overlap."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from suica_core.v8_orientation_overlap import (
    OrientationOverlapSpec,
    _eigensystem,
    _haar_null,
    calibrate_epsilon,
    fit_orientation_template,
    orientation_metrics,
)
from suica_core.v8_realtext_relation_field import stable_bucket
from suica_core.v8_spectral_order_replay import (
    _density,
    _resample,
    fit_shared_gauge,
)
from suica_core.v8_support_containment import _robust_standardizer, _stable_indices


@dataclass(frozen=True)
class OrderKnockoutSpec:
    """Frozen paired order-knockout budgets."""

    calibration_draws: int = 99
    bootstrap_draws: int = 199
    rotation_draws: int = 499
    maximum_rank: int = 48
    minimum_rank: int = 2
    seed: int = 20260811

    def orientation_spec(self) -> OrientationOverlapSpec:
        return OrientationOverlapSpec(
            calibration_draws=self.calibration_draws,
            bootstrap_draws=self.bootstrap_draws,
            rotation_draws=self.rotation_draws,
            maximum_rank=self.maximum_rank,
            minimum_rank=self.minimum_rank,
            seed=self.seed,
        )


def shuffle_within_replicate(
    events: pd.DataFrame,
    *,
    seed: int,
    corpus: str,
) -> pd.DataFrame:
    """Shuffle order within even/odd technical replicates for every author."""
    result = events.sort_values(["author_id", "order"], kind="stable").copy()
    for author, indices in result.groupby(
        "author_id",
        observed=True,
        sort=False,
    ).groups.items():
        ordered = np.asarray(list(indices))
        rng = np.random.default_rng(
            seed
            + stable_bucket(
                f"{corpus}-{author}",
                salt="v8-orientation-order-knockout",
                modulus=2**31 - 1,
            )
        )
        for offset in (0, 1):
            positions = ordered[offset::2]
            values = result.loc[positions, "text"].to_numpy(copy=True)
            result.loc[positions, "text"] = values[rng.permutation(len(values))]
    return result


def _aligned_stage(
    native: tuple[np.ndarray, np.ndarray],
    shuffled: tuple[np.ndarray, np.ndarray],
    count: int,
    *,
    salt: str,
) -> tuple[np.ndarray, np.ndarray]:
    native_raw, native_ids = native
    shuffled_raw, shuffled_ids = shuffled
    shuffled_index = {
        str(author): index for index, author in enumerate(shuffled_ids)
    }
    common_mask = np.asarray(
        [str(author) in shuffled_index for author in native_ids],
        dtype=bool,
    )
    common_raw = native_raw[common_mask]
    common_ids = native_ids[common_mask]
    selected = _stable_indices(common_ids, count, salt=salt)
    selected_ids = common_ids[selected]
    return (
        common_raw[selected],
        np.stack([shuffled_raw[shuffled_index[str(value)]] for value in selected_ids]),
    )


def _matched_metrics(
    left_density: np.ndarray,
    right_density: np.ndarray,
    *,
    rank: int,
    weights: np.ndarray,
) -> dict[str, float]:
    _, left_vectors = _eigensystem(left_density)
    _, right_vectors = _eigensystem(right_density)
    return orientation_metrics(
        left_vectors[:, :rank],
        right_vectors[:, :rank],
        weights,
        weights,
    )


def evaluate_order_knockout(
    native_left: dict[str, tuple[np.ndarray, np.ndarray]],
    native_right: dict[str, tuple[np.ndarray, np.ndarray]],
    shuffled_left: dict[str, tuple[np.ndarray, np.ndarray]],
    shuffled_right: dict[str, tuple[np.ndarray, np.ndarray]],
    *,
    spec: OrderKnockoutSpec,
) -> dict[str, Any]:
    """Compare native K orientation with a paired within-replicate shuffle."""
    orientation_spec = spec.orientation_spec()
    gauge = fit_shared_gauge(
        *native_left["D0"],
        *native_right["D0"],
        salt=f"v8-order-knockout-{spec.seed}",
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
            maximum_rank=spec.maximum_rank,
            minimum_rank=spec.minimum_rank,
        )
    except ValueError as error:
        return {
            "status": str(error),
            "epsilon": epsilon,
            "rank": None,
            "cells": pd.DataFrame(),
        }
    rows = []
    for split in ("D1", "D2"):
        count = min(
            len(native_left[split][0]),
            len(native_right[split][0]),
            len(shuffled_left[split][0]),
            len(shuffled_right[split][0]),
        )
        left_native, left_shuffled = _aligned_stage(
            native_left[split],
            shuffled_left[split],
            count,
            salt=f"v8-order-knockout-{split}-left",
        )
        right_native, right_shuffled = _aligned_stage(
            native_right[split],
            shuffled_right[split],
            count,
            salt=f"v8-order-knockout-{split}-right",
        )
        native_metrics = _matched_metrics(
            _density(left_native, gauge.center, gauge.scale),
            _density(right_native, gauge.center, gauge.scale),
            rank=template.rank,
            weights=template.weights,
        )
        shuffled_left_density = _density(
            left_shuffled,
            gauge.center,
            gauge.scale,
        )
        shuffled_right_density = _density(
            right_shuffled,
            gauge.center,
            gauge.scale,
        )
        shuffled_metrics = _matched_metrics(
            shuffled_left_density,
            shuffled_right_density,
            rank=template.rank,
            weights=template.weights,
        )
        _, shuffled_left_vectors = _eigensystem(shuffled_left_density)
        shuffled_null = _haar_null(
            shuffled_left_vectors[:, : template.rank],
            template.weights,
            template.weights,
            draws=spec.rotation_draws,
            rng=rng,
        )
        bootstrap = {
            "hs": np.empty(spec.bootstrap_draws, dtype=float),
            "fidelity": np.empty(spec.bootstrap_draws, dtype=float),
        }
        for draw in range(spec.bootstrap_draws):
            left_d0 = _resample(gauge.left_d0, rng)
            right_d0 = _resample(gauge.right_d0, rng)
            center, scale = _robust_standardizer(
                np.concatenate([left_d0, right_d0], axis=0)
            )
            left_indices = rng.integers(0, count, size=count)
            right_indices = rng.integers(0, count, size=count)
            native_draw = _matched_metrics(
                _density(left_native[left_indices], center, scale),
                _density(right_native[right_indices], center, scale),
                rank=template.rank,
                weights=template.weights,
            )
            shuffled_draw = _matched_metrics(
                _density(left_shuffled[left_indices], center, scale),
                _density(right_shuffled[right_indices], center, scale),
                rank=template.rank,
                weights=template.weights,
            )
            for metric in bootstrap:
                bootstrap[metric][draw] = (
                    native_draw[metric] - shuffled_draw[metric]
                )
        for metric in ("hs", "fidelity"):
            shuffled_p = float(
                (
                    1
                    + np.sum(shuffled_null[metric] >= shuffled_metrics[metric])
                )
                / (spec.rotation_draws + 1)
            )
            rows.append(
                {
                    "split": split,
                    "metric": metric,
                    "rank": template.rank,
                    "native": native_metrics[metric],
                    "shuffled": shuffled_metrics[metric],
                    "native_minus_shuffled": (
                        native_metrics[metric] - shuffled_metrics[metric]
                    ),
                    "paired_bootstrap_low": float(
                        np.quantile(bootstrap[metric], 0.025)
                    ),
                    "shuffled_null_mean": float(
                        shuffled_null[metric].mean()
                    ),
                    "shuffled_rotation_p": shuffled_p,
                }
            )
    cells = pd.DataFrame(rows)
    passed = bool(
        cells["paired_bootstrap_low"].gt(0).all()
        and cells["native_minus_shuffled"].gt(0).all()
    )
    return {
        "status": (
            "ORDER_SENSITIVE_ORIENTATION_KNOCKOUT_SUPPORTED"
            if passed
            else "ORDER_SENSITIVE_ORIENTATION_KNOCKOUT_NOT_SUPPORTED"
        ),
        "epsilon": epsilon,
        "rank": template.rank,
        "cells": cells,
    }
