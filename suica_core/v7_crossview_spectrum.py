"""Coordinate-free spectral diagnostics for V7 shared multiview geometry.

This module does not choose a number of psychological factors. It measures how
distributed cross-view covariance is after a registered representation and
source panel are frozen. The resulting effective-rank quantities are capacity
descriptors, not latent dimensions.
"""
from __future__ import annotations

from typing import Any

import numpy as np


def off_diagonal_cross_view_operator(blocks: dict[str, np.ndarray], *, view_names: tuple[str, ...]) -> np.ndarray:
    r"""Return the centered, symmetric mean cross-view covariance operator.

    With aligned, same-coordinate blocks \(X_v\), the operator is

    \[
    C_{off}=\frac{1}{|V|(|V|-1)}\sum_{v\ne w}
       \frac{X_v^\top X_w}{n}.
    \]

    Each block is centered within the split, so the diagnostic describes
    cross-view variation rather than split mean position. All views must share
    author rows and feature coordinates.
    """
    if len(view_names) < 2:
        raise ValueError("At least two views are required.")
    matrices = [np.asarray(blocks[name], dtype=float) for name in view_names]
    n_rows, n_features = matrices[0].shape
    if n_rows < 3 or n_features < 1 or any(matrix.shape != (n_rows, n_features) for matrix in matrices):
        raise ValueError("Cross-view spectrum requires aligned blocks with common shape and >=3 rows.")
    centered = [matrix - matrix.mean(axis=0, keepdims=True) for matrix in matrices]
    operator = np.zeros((n_features, n_features), dtype=float)
    n_pairs = 0
    for left_index, left in enumerate(centered):
        for right in centered[left_index + 1:]:
            cross = (left.T @ right) / float(n_rows)
            operator += 0.5 * (cross + cross.T)
            n_pairs += 1
    return operator / float(n_pairs)


def ordered_spectrum(operator: np.ndarray) -> np.ndarray:
    """Return a descending real eigenspectrum for a symmetric operator."""
    matrix = np.asarray(operator, dtype=float)
    return np.linalg.eigvalsh(0.5 * (matrix + matrix.T))[::-1]


def broken_correspondence_spectra(
    blocks: dict[str, np.ndarray],
    *,
    view_names: tuple[str, ...],
    iterations: int,
    seed: int,
) -> np.ndarray:
    """Generate a cross-view spectral null by independently breaking author IDs."""
    if int(iterations) < 2:
        raise ValueError("At least two null iterations are required.")
    rng = np.random.default_rng(int(seed))
    n_rows = len(blocks[view_names[0]])
    rows: list[np.ndarray] = []
    for _ in range(int(iterations)):
        broken = {view_names[0]: np.asarray(blocks[view_names[0]], dtype=float)}
        for name in view_names[1:]:
            broken[name] = np.asarray(blocks[name], dtype=float)[rng.permutation(n_rows)]
        rows.append(ordered_spectrum(off_diagonal_cross_view_operator(broken, view_names=view_names)))
    return np.vstack(rows)


def excess_spectral_profile(
    blocks: dict[str, np.ndarray],
    *,
    view_names: tuple[str, ...],
    null_upper: np.ndarray,
) -> dict[str, Any]:
    """Summarize observed cross-view spectrum beyond a frozen null envelope."""
    observed = ordered_spectrum(off_diagonal_cross_view_operator(blocks, view_names=view_names))
    upper = np.asarray(null_upper, dtype=float)
    if observed.shape != upper.shape:
        raise ValueError("Observed and null spectra must share dimension.")
    # A less-negative eigenvalue than the broken-correspondence null is not a
    # positive shared mode. Retain only covariance modes that are both positive
    # in the observed operator and above the frozen null envelope.
    excess = np.where(observed > 0.0, np.maximum(observed - upper, 0.0), 0.0)
    total = float(excess.sum())
    if total <= 1e-12:
        entropy_rank = 0.0
        participation_rank = 0.0
        energy_90_rank = 0
    else:
        probabilities = excess / total
        positive = probabilities[probabilities > 1e-15]
        entropy_rank = float(np.exp(-np.sum(positive * np.log(positive))))
        participation_rank = float(total**2 / np.sum(excess**2))
        energy_90_rank = int(np.searchsorted(np.cumsum(excess) / total, 0.90, side="left") + 1)
    return {
        "observed_eigenvalues": observed,
        "null_upper_eigenvalues": upper,
        "excess_eigenvalues": excess,
        "n_positive_excess": int(np.sum(excess > 1e-12)),
        "entropy_effective_rank": entropy_rank,
        "participation_effective_rank": participation_rank,
        "excess_energy_90_rank": energy_90_rank,
    }


def profile_cosine(left: np.ndarray, right: np.ndarray) -> float:
    """Return cosine similarity for nonnegative spectral-excess profiles."""
    a, b = np.asarray(left, dtype=float), np.asarray(right, dtype=float)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(a @ b / denom) if denom > 1e-12 else float("nan")
