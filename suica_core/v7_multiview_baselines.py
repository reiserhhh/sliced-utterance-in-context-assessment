"""Competing label-free multiview baselines for SUICA V7.

The implementations operate on author-aligned feature blocks already fitted and
scaled outside this module.  They compare mathematical decompositions; none of
their latent coordinates are psychological constructs or named factors.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import block_diag, eigh
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge


@dataclass(frozen=True)
class SharedLatentModel:
    """A shared-coordinate model with source encoders and target decoders."""

    method: str
    rank: int
    view_names: tuple[str, ...]
    shared_scores: np.ndarray
    encoders: dict[str, Ridge]
    decoders: dict[str, Ridge]


def _normalize_columns(values: np.ndarray) -> np.ndarray:
    """Center/scale latent columns to avoid one view dominating by magnitude."""
    matrix = np.asarray(values, dtype=float)
    center = matrix.mean(axis=0, keepdims=True)
    scale = np.maximum(matrix.std(axis=0, keepdims=True), 1e-12)
    return (matrix - center) / scale


def _fit_io_models(
    blocks: dict[str, np.ndarray],
    *,
    view_names: tuple[str, ...],
    shared: np.ndarray,
    ridge_alpha: float,
    method: str,
) -> SharedLatentModel:
    """Fit view-to-shared and shared-to-view maps after latent construction."""
    shared = _normalize_columns(shared)
    encoders = {
        view: Ridge(alpha=float(ridge_alpha), fit_intercept=True).fit(np.asarray(blocks[view], dtype=float), shared)
        for view in view_names
    }
    decoders = {
        view: Ridge(alpha=float(ridge_alpha), fit_intercept=True).fit(shared, np.asarray(blocks[view], dtype=float))
        for view in view_names
    }
    return SharedLatentModel(
        method=method, rank=int(shared.shape[1]), view_names=view_names, shared_scores=shared,
        encoders=encoders, decoders=decoders,
    )


def fit_concat_pca(
    blocks: dict[str, np.ndarray],
    *,
    view_names: tuple[str, ...],
    rank: int,
    ridge_alpha: float,
) -> SharedLatentModel:
    """Fit a concatenated-PCA shared representation baseline."""
    matrix = np.hstack([np.asarray(blocks[view], dtype=float) for view in view_names])
    admissible = min(matrix.shape[0] - 1, matrix.shape[1])
    if rank < 1 or rank > admissible:
        raise ValueError(f"Invalid concat-PCA rank {rank}; admissible <= {admissible}.")
    shared = PCA(n_components=int(rank), svd_solver="full").fit_transform(matrix)
    return _fit_io_models(blocks, view_names=view_names, shared=shared, ridge_alpha=ridge_alpha, method="CONCAT_PCA")


def fit_rgcca_sumcor(
    blocks: dict[str, np.ndarray],
    *,
    view_names: tuple[str, ...],
    rank: int,
    ridge_alpha: float,
) -> SharedLatentModel:
    r"""Fit a ridge-regularized SUMCOR generalized CCA baseline.

    With centered/scaled blocks \(X_v\), solve the regularized generalized
    eigenproblem

    \[
      C_{off} w = \lambda\, (C_{within}+\rho I) w,
    \]

    where the diagonal blocks of \(C_{off}\) are zero and off-diagonal blocks
    are \(X_v^T X_w/n\).  It maximizes cross-view covariance rather than any
    within-view variance alone.  Component signs are aligned before averaging
    view-specific scores into an anonymous common coordinate.

    ``ridge_alpha`` must be strictly positive: with \(\rho = 0\) the metric
    \(C_{within}\) can be singular (always when a block has more features than
    authors), making the generalized eigenproblem unreliable.
    """
    if not float(ridge_alpha) > 0.0:
        raise ValueError(f"fit_rgcca_sumcor requires ridge_alpha > 0 (got {ridge_alpha}); a singular metric makes the generalized eigenproblem unreliable.")
    matrices = [np.asarray(blocks[view], dtype=float) for view in view_names]
    n_rows = matrices[0].shape[0]
    if n_rows < 3 or any(matrix.shape[0] != n_rows for matrix in matrices):
        raise ValueError("RGCCA requires aligned blocks with at least three authors.")
    dimensions = [matrix.shape[1] for matrix in matrices]
    admissible = min(n_rows - 1, sum(dimensions))
    if rank < 1 or rank > admissible:
        raise ValueError(f"Invalid RGCCA rank {rank}; admissible <= {admissible}.")
    covariance = [[None for _ in matrices] for _ in matrices]
    within = []
    for left_index, left in enumerate(matrices):
        within.append((left.T @ left) / float(n_rows) + float(ridge_alpha) * np.eye(left.shape[1]))
        for right_index, right in enumerate(matrices):
            covariance[left_index][right_index] = np.zeros((left.shape[1], right.shape[1])) if left_index == right_index else (left.T @ right) / float(n_rows)
    off_diagonal = np.block(covariance)
    metric = block_diag(*within)
    eigenvalues, eigenvectors = eigh(off_diagonal, metric, check_finite=False)
    selected = np.argsort(eigenvalues)[::-1][: int(rank)]
    weights = eigenvectors[:, selected]
    offsets = np.cumsum([0, *dimensions])
    per_view_scores: list[np.ndarray] = []
    reference: np.ndarray | None = None
    for index, matrix in enumerate(matrices):
        score = matrix @ weights[offsets[index]:offsets[index + 1]]
        score = _normalize_columns(score)
        if reference is None:
            reference = score.copy()
        else:
            signs = np.sign(np.sum(reference * score, axis=0))
            signs[signs == 0] = 1.0
            score = score * signs[None, :]
        per_view_scores.append(score)
    shared = _normalize_columns(np.mean(np.stack(per_view_scores, axis=0), axis=0))
    return _fit_io_models(blocks, view_names=view_names, shared=shared, ridge_alpha=ridge_alpha, method="RGCCA_SUMCOR")


def predict_target(model: SharedLatentModel, *, source: str, target: str, source_block: np.ndarray) -> np.ndarray:
    """Predict one view through an anonymous shared coordinate."""
    shared = np.asarray(model.encoders[source].predict(np.asarray(source_block, dtype=float)), dtype=float)
    if shared.ndim == 1:
        shared = shared[:, None]
    return np.asarray(model.decoders[target].predict(shared), dtype=float)


def global_r2(target: np.ndarray, prediction: np.ndarray) -> float:
    """Calculate multivariate held-out R2 relative to the target mean."""
    truth = np.asarray(target, dtype=float)
    estimated = np.asarray(prediction, dtype=float)
    denominator = float(np.sum((truth - truth.mean(axis=0, keepdims=True)) ** 2))
    if denominator <= 1e-12:
        return float("nan")
    return float(1.0 - np.sum((truth - estimated) ** 2) / denominator)


def evaluate_shared_model(model: SharedLatentModel, blocks: dict[str, np.ndarray]) -> list[dict[str, float | str | int]]:
    """Evaluate all directed source-to-target maps on held-out aligned authors."""
    rows: list[dict[str, float | str | int]] = []
    for source in model.view_names:
        for target in model.view_names:
            if source == target:
                continue
            rows.append({
                "method": model.method, "source": source, "target": target,
                "n_authors": int(len(blocks[source])),
                "global_r2": global_r2(blocks[target], predict_target(model, source=source, target=target, source_block=blocks[source])),
            })
    return rows
