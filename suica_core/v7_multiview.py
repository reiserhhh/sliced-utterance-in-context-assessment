"""Label-free shared/private multiview analysis for SUICA V7.1.

This is a deliberately modest, JIVE-inspired consensus decomposition. It does
not claim that operator views are coordinate charts or that its latent columns
are psychological traits. It estimates a shared author subspace only from
cross-view covariance, then retains operator-specific residual geometry.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge


@dataclass
class BlockScaler:
    """Discovery-fitted centering/scaling for one operator feature block."""

    feature_names: list[str]
    center: np.ndarray
    scale: np.ndarray


@dataclass
class ConsensusModel:
    """Frozen shared author subspace plus operator-specific decoders."""

    rank: int
    view_names: tuple[str, ...]
    shared_scores: np.ndarray
    eigenvalues: np.ndarray
    decoders: dict[str, np.ndarray]
    encoders: dict[str, Ridge]
    shared_variance_ratio: dict[str, float]
    private_effective_rank: dict[str, float]


def numeric_feature_columns(frame: pd.DataFrame) -> list[str]:
    """Return the common V7 author features, excluding support metadata."""
    return [
        column for column in frame.columns
        if "::" in column and not column.startswith(("n_units::", "n_tokens::"))
    ]


def common_feature_columns(feature_frames: dict[str, pd.DataFrame], view_names: tuple[str, ...]) -> list[str]:
    """Find feature coordinates present in every requested observation view."""
    if not view_names:
        raise ValueError("At least one multiview operator is required.")
    common = set(numeric_feature_columns(feature_frames[view_names[0]]))
    for view in view_names[1:]:
        common.intersection_update(numeric_feature_columns(feature_frames[view]))
    columns = [column for column in numeric_feature_columns(feature_frames[view_names[0]]) if column in common]
    if len(columns) < 2:
        raise ValueError("Multiview decomposition requires at least two common author features.")
    return columns


def fit_block_scalers(
    feature_frames: dict[str, pd.DataFrame],
    *,
    view_names: tuple[str, ...],
    feature_names: list[str],
    discovery_user_ids: list[str],
    allow_missing: bool = False,
) -> dict[str, BlockScaler]:
    """Fit separate block scalers on discovery authors only.

    Every requested discovery author must be present in every view; a missing
    author would otherwise be silently mean-imputed by the reindex, biasing the
    scaler toward the view mean. Pass ``allow_missing=True`` only to restore
    that legacy imputing behavior deliberately.
    """
    scalers: dict[str, BlockScaler] = {}
    discovery_ids = [str(user_id) for user_id in discovery_user_ids]
    for view in view_names:
        frame = feature_frames[view].set_index("user_id")
        if not allow_missing:
            present = set(frame.index.astype(str))
            missing = [user_id for user_id in discovery_ids if user_id not in present]
            if missing:
                raise ValueError(
                    f"fit_block_scalers: view '{view}' is missing {len(missing)} requested "
                    f"discovery author(s): {sorted(missing)}. Missing authors would be silently "
                    "mean-imputed; pass allow_missing=True only if that is intended."
                )
        values = frame.reindex(discovery_ids)[feature_names].to_numpy(float)
        center = np.nanmean(values, axis=0)
        center = np.where(np.isfinite(center), center, 0.0)
        filled = np.where(np.isfinite(values), values, center[None, :])
        scale = np.nanstd(filled, axis=0, ddof=0)
        scale = np.where(np.isfinite(scale) & (scale > 1e-9), scale, 1.0)
        scalers[view] = BlockScaler(feature_names=list(feature_names), center=center, scale=scale)
    return scalers


def transform_feature_block(frame: pd.DataFrame, *, scaler: BlockScaler, user_ids: list[str]) -> np.ndarray:
    """Apply a discovery-fitted block scaler to authors in declared order."""
    values = frame.set_index("user_id").reindex([str(value) for value in user_ids])[scaler.feature_names].to_numpy(float)
    values = np.where(np.isfinite(values), values, scaler.center[None, :])
    return (values - scaler.center[None, :]) / scaler.scale[None, :]


def effective_rank(values: np.ndarray) -> float:
    """Return entropy effective rank of a centered residual matrix."""
    matrix = np.asarray(values, dtype=float)
    if matrix.size == 0:
        return float("nan")
    singular = np.linalg.svd(matrix - np.mean(matrix, axis=0, keepdims=True), compute_uv=False)
    weights = singular**2
    total = float(weights.sum())
    if total <= 1e-14:
        return 0.0
    probabilities = weights / total
    probabilities = probabilities[probabilities > 1e-15]
    return float(np.exp(-np.sum(probabilities * np.log(probabilities))))


def _global_r2(target: np.ndarray, prediction: np.ndarray) -> float:
    target = np.asarray(target, dtype=float)
    prediction = np.asarray(prediction, dtype=float)
    denominator = float(np.sum((target - np.mean(target, axis=0, keepdims=True)) ** 2))
    if denominator <= 1e-14:
        return float("nan")
    return float(1.0 - np.sum((target - prediction) ** 2) / denominator)


def linear_cka(left: np.ndarray, right: np.ndarray) -> float:
    """Calculate linear CKA for same-author feature blocks."""
    x = np.asarray(left, dtype=float) - np.mean(left, axis=0, keepdims=True)
    y = np.asarray(right, dtype=float) - np.mean(right, axis=0, keepdims=True)
    numerator = float(np.linalg.norm(x.T @ y, ord="fro") ** 2)
    denominator = float(np.linalg.norm(x.T @ x, ord="fro") * np.linalg.norm(y.T @ y, ord="fro"))
    return numerator / denominator if denominator > 1e-14 else float("nan")


def fit_consensus_model(
    blocks: dict[str, np.ndarray],
    *,
    view_names: tuple[str, ...],
    rank: int,
    ridge_alpha: float,
) -> ConsensusModel:
    r"""Fit a cross-view-covariance shared subspace on aligned authors.

    Given standardized blocks \(X_j\), the shared author Gram operator is

    \[
      G = \sum_{j<k} \frac{X_j X_k^T + X_k X_j^T}{2p}.
    \]

    Only cross-view covariance enters \(G\), which *suppresses* view-private
    variation relative to concatenated PCA — but it does **not** eliminate
    finite-sample noise components. Independent view-private noise has nonzero
    sample cross-view covariance, so \(G\) acquires large positive eigenvalues
    from pure noise in finite samples (e.g. fully independent 30x6 blocks
    yield in-sample shared_variance_ratio around 0.6 at rank 10). The actual
    guards against interpreting such components are (1) calibrated rank
    selection on held-out authors and (2) broken-correspondence (permuted
    author) baselines — not this operator's algebraic form. View decoders and
    encoders are then fit conditionally on the resulting anonymous shared
    scores.
    """
    if not view_names:
        raise ValueError("Consensus model needs at least one view.")
    matrices = [np.asarray(blocks[view], dtype=float) for view in view_names]
    n_rows = matrices[0].shape[0]
    n_features = matrices[0].shape[1]
    if any(matrix.shape != (n_rows, n_features) for matrix in matrices):
        raise ValueError("All consensus blocks must have the same author and feature shape.")
    if rank < 0 or rank >= n_rows:
        raise ValueError(f"Invalid shared rank {rank} for {n_rows} discovery authors.")
    if rank == 0:
        zero = np.zeros((n_rows, 0), dtype=float)
        return ConsensusModel(
            rank=0,
            view_names=view_names,
            shared_scores=zero,
            eigenvalues=np.array([], dtype=float),
            decoders={view: np.zeros((0, n_features), dtype=float) for view in view_names},
            encoders={},
            shared_variance_ratio={view: 0.0 for view in view_names},
            private_effective_rank={view: effective_rank(blocks[view]) for view in view_names},
        )
    gram = np.zeros((n_rows, n_rows), dtype=float)
    for left_index, left in enumerate(matrices):
        for right in matrices[left_index + 1:]:
            cross = (left @ right.T) / float(n_features)
            gram += 0.5 * (cross + cross.T)
    eigenvalues, eigenvectors = np.linalg.eigh(gram)
    selected = np.argsort(eigenvalues)[::-1][:rank]
    shared = eigenvectors[:, selected]
    decoders: dict[str, np.ndarray] = {}
    encoders: dict[str, Ridge] = {}
    shared_variance_ratio: dict[str, float] = {}
    private_effective_rank: dict[str, float] = {}
    for view in view_names:
        matrix = np.asarray(blocks[view], dtype=float)
        decoder = np.linalg.lstsq(shared, matrix, rcond=None)[0]
        reconstruction = shared @ decoder
        residual = matrix - reconstruction
        total_variance = float(np.sum((matrix - np.mean(matrix, axis=0, keepdims=True)) ** 2))
        residual_variance = float(np.sum((residual - np.mean(residual, axis=0, keepdims=True)) ** 2))
        decoders[view] = decoder
        encoders[view] = Ridge(alpha=float(ridge_alpha), fit_intercept=True).fit(matrix, shared)
        shared_variance_ratio[view] = float(1.0 - residual_variance / total_variance) if total_variance > 1e-14 else float("nan")
        private_effective_rank[view] = effective_rank(residual)
    return ConsensusModel(
        rank=int(rank),
        view_names=view_names,
        shared_scores=shared,
        eigenvalues=eigenvalues[selected],
        decoders=decoders,
        encoders=encoders,
        shared_variance_ratio=shared_variance_ratio,
        private_effective_rank=private_effective_rank,
    )


def predict_target_from_source(
    model: ConsensusModel,
    source: str,
    target: str,
    source_block: np.ndarray,
) -> np.ndarray:
    """Predict one operator's feature block through the shared subspace."""
    if model.rank == 0:
        return np.zeros((len(source_block), model.decoders[target].shape[1]), dtype=float)
    predicted_shared = np.asarray(model.encoders[source].predict(np.asarray(source_block, dtype=float)), dtype=float)
    if predicted_shared.ndim == 1:
        predicted_shared = predicted_shared[:, None]
    return predicted_shared @ model.decoders[target]


def fit_direct_predictors(
    blocks: dict[str, np.ndarray],
    *,
    view_names: tuple[str, ...],
    ridge_alpha: float,
    permutation_seed: int | None = None,
) -> dict[tuple[str, str], Ridge]:
    """Fit direct cross-view Ridge maps, optionally breaking author alignment.

    When ``permutation_seed`` is set, each target block is permuted **once**:
    the resulting "permuted" baseline is a single draw from the
    broken-correspondence null, not a null distribution. Comparisons against
    it therefore carry one-draw sampling noise; use repeated draws (as in
    ``broken_correspondence_spectra``) when a calibrated null quantile is
    required.
    """
    rng = np.random.default_rng(permutation_seed) if permutation_seed is not None else None
    models: dict[tuple[str, str], Ridge] = {}
    for source in view_names:
        for target in view_names:
            if source == target:
                continue
            y = np.asarray(blocks[target], dtype=float)
            if rng is not None:
                y = y[rng.permutation(len(y))]
            models[(source, target)] = Ridge(alpha=float(ridge_alpha), fit_intercept=True).fit(blocks[source], y)
    return models


def evaluate_cross_view(
    blocks: dict[str, np.ndarray],
    *,
    model: ConsensusModel,
    direct_models: dict[tuple[str, str], Ridge],
    permuted_models: dict[tuple[str, str], Ridge],
) -> pd.DataFrame:
    """Evaluate shared and direct maps on held-out aligned authors.

    ``permuted_direct_global_r2`` comes from a single permutation draw (see
    ``fit_direct_predictors``); it is a one-draw broken-correspondence
    baseline, not a null-distribution quantile.
    """
    rows: list[dict[str, Any]] = []
    for source in model.view_names:
        for target in model.view_names:
            if source == target:
                continue
            truth = np.asarray(blocks[target], dtype=float)
            consensus = predict_target_from_source(model, source, target, blocks[source])
            direct = direct_models[(source, target)].predict(blocks[source])
            permuted = permuted_models[(source, target)].predict(blocks[source])
            rows.append({
                "source_view": source,
                "target_view": target,
                "n_authors": int(len(truth)),
                "consensus_global_r2": _global_r2(truth, consensus),
                "direct_global_r2": _global_r2(truth, direct),
                "permuted_direct_global_r2": _global_r2(truth, permuted),
                "linear_cka": linear_cka(blocks[source], truth),
            })
    return pd.DataFrame(rows)


def mean_row_cosine(left: np.ndarray, right: np.ndarray) -> float:
    """Return average matched-author cosine similarity across feature vectors."""
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    numerator = np.sum(x * y, axis=1)
    denominator = np.linalg.norm(x, axis=1) * np.linalg.norm(y, axis=1)
    values = np.divide(numerator, denominator, out=np.full(len(x), np.nan), where=denominator > 1e-14)
    return float(np.nanmean(values))
