"""Directed operator-atlas diagnostics for SUICA V7.1 observation views."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import CCA
from sklearn.linear_model import Ridge

from .v7_multiview import linear_cka


def global_r2(target: np.ndarray, prediction: np.ndarray) -> float:
    """Compute a feature-block R2 relative to held-out target variation."""
    y = np.asarray(target, dtype=float)
    yhat = np.asarray(prediction, dtype=float)
    denominator = float(np.sum((y - np.mean(y, axis=0, keepdims=True)) ** 2))
    if denominator <= 1e-14:
        return float("nan")
    return float(1.0 - np.sum((y - yhat) ** 2) / denominator)


def fit_directed_maps(
    blocks: dict[str, np.ndarray],
    *,
    view_names: tuple[str, ...],
    ridge_alpha: float,
    permutation_seed: int | None = None,
) -> dict[tuple[str, str], Ridge]:
    """Fit all directed cross-view maps, optionally breaking author alignment."""
    rng = np.random.default_rng(permutation_seed) if permutation_seed is not None else None
    maps: dict[tuple[str, str], Ridge] = {}
    for source in view_names:
        for target in view_names:
            if source == target:
                continue
            target_values = np.asarray(blocks[target], dtype=float)
            if rng is not None:
                target_values = target_values[rng.permutation(len(target_values))]
            maps[(source, target)] = Ridge(alpha=float(ridge_alpha), fit_intercept=True).fit(
                blocks[source], target_values
            )
    return maps


def heldout_cca_mean_correlation(
    train_left: np.ndarray,
    train_right: np.ndarray,
    test_left: np.ndarray,
    test_right: np.ndarray,
    *,
    max_components: int = 6,
) -> float:
    """Fit CCA on train authors and score canonical correlation on held-out authors."""
    n_components = min(
        int(max_components),
        train_left.shape[0] - 1,
        train_left.shape[1],
        train_right.shape[1],
    )
    if n_components < 1 or len(test_left) < 3:
        return float("nan")
    try:
        model = CCA(n_components=n_components, scale=False, max_iter=2000, tol=1e-6)
        model.fit(train_left, train_right)
        left, right = model.transform(test_left, test_right)
        correlations = []
        for index in range(n_components):
            if np.std(left[:, index]) > 1e-12 and np.std(right[:, index]) > 1e-12:
                correlations.append(float(np.corrcoef(left[:, index], right[:, index])[0, 1]))
        return float(np.mean(correlations)) if correlations else float("nan")
    except (np.linalg.LinAlgError, ValueError):
        return float("nan")


def evaluate_directed_atlas(
    train_blocks: dict[str, np.ndarray],
    confirmation_blocks: dict[str, np.ndarray],
    *,
    view_names: tuple[str, ...],
    maps: dict[tuple[str, str], Ridge],
    permuted_maps: dict[tuple[str, str], Ridge],
) -> pd.DataFrame:
    """Evaluate directed map edges on fresh confirmation authors."""
    rows: list[dict[str, Any]] = []
    for source in view_names:
        for target in view_names:
            if source == target:
                continue
            truth = confirmation_blocks[target]
            prediction = maps[(source, target)].predict(confirmation_blocks[source])
            permuted = permuted_maps[(source, target)].predict(confirmation_blocks[source])
            rows.append({
                "source_view": source,
                "target_view": target,
                "n_authors": int(len(truth)),
                "direct_global_r2": global_r2(truth, prediction),
                "permuted_direct_global_r2": global_r2(truth, permuted),
                "r2_above_permuted": global_r2(truth, prediction) - global_r2(truth, permuted),
                "linear_cka": linear_cka(confirmation_blocks[source], truth),
                "heldout_cca_mean_correlation": heldout_cca_mean_correlation(
                    train_blocks[source], train_blocks[target], confirmation_blocks[source], truth
                ),
            })
    return pd.DataFrame(rows)


def atlas_asymmetry(edges: pd.DataFrame) -> pd.DataFrame:
    """Summarize pairwise directional R2 asymmetry without defining a hierarchy."""
    rows: list[dict[str, Any]] = []
    views = sorted(set(edges["source_view"]).union(edges["target_view"]))
    for index, left in enumerate(views):
        for right in views[index + 1:]:
            forward = edges.loc[(edges["source_view"] == left) & (edges["target_view"] == right)].iloc[0]
            reverse = edges.loc[(edges["source_view"] == right) & (edges["target_view"] == left)].iloc[0]
            rows.append({
                "view_a": left,
                "view_b": right,
                "a_to_b_r2": float(forward["direct_global_r2"]),
                "b_to_a_r2": float(reverse["direct_global_r2"]),
                "r2_asymmetry_a_to_b_minus_b_to_a": float(forward["direct_global_r2"] - reverse["direct_global_r2"]),
                "mean_heldout_cca": float(np.nanmean([forward["heldout_cca_mean_correlation"], reverse["heldout_cca_mean_correlation"]])),
            })
    return pd.DataFrame(rows)


def cycle_errors(
    confirmation_blocks: dict[str, np.ndarray],
    *,
    view_names: tuple[str, ...],
    maps: dict[tuple[str, str], Ridge],
) -> pd.DataFrame:
    """Measure whether directed map triples approximately return to their source."""
    rows: list[dict[str, Any]] = []
    for source in view_names:
        for middle in view_names:
            for target in view_names:
                if len({source, middle, target}) < 3:
                    continue
                origin = confirmation_blocks[source]
                through_middle = maps[(source, middle)].predict(origin)
                through_target = maps[(middle, target)].predict(through_middle)
                returned = maps[(target, source)].predict(through_target)
                rmse = float(np.sqrt(np.mean((origin - returned) ** 2)))
                rows.append({
                    "source_view": source,
                    "middle_view": middle,
                    "target_view": target,
                    "cycle_rmse_standardized": rmse,
                    "cycle_global_r2": global_r2(origin, returned),
                })
    return pd.DataFrame(rows)
