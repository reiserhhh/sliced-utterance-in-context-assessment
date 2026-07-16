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


def simultaneous_null_upper(null_spectra: np.ndarray, *, quantile: float = 0.95) -> float:
    """Return a max-T style simultaneous null bound for an ordered spectrum.

    The pointwise per-position quantile controls the exceedance rate at each
    position separately; with many positions the expected number of chance
    exceedances grows, so counting positions above a pointwise envelope is
    positively biased under a global null. This bound instead takes the max
    over positions within each null draw and returns the requested quantile of
    that max, controlling the family-wise chance of any exceedance.
    """
    spectra = np.asarray(null_spectra, dtype=float)
    if spectra.ndim != 2 or spectra.shape[0] < 2 or spectra.shape[1] < 1:
        raise ValueError("Simultaneous envelope requires a [draw, position] null spectrum matrix.")
    if not 0.0 < float(quantile) < 1.0:
        raise ValueError("Simultaneous envelope quantile must be inside (0, 1).")
    return float(np.quantile(spectra.max(axis=1), float(quantile)))


def excess_spectral_profile(
    blocks: dict[str, np.ndarray],
    *,
    view_names: tuple[str, ...],
    null_upper: np.ndarray,
    null_spectra: np.ndarray | None = None,
    simultaneous_quantile: float = 0.95,
) -> dict[str, Any]:
    """Summarize observed cross-view spectrum beyond a frozen null envelope.

    The primary quantities use the frozen *pointwise* ``null_upper`` envelope
    and are unchanged. When the raw ``null_spectra`` draws are also supplied,
    the result additionally carries max-T style *simultaneous* envelope
    quantities (``*_simultaneous`` keys, see ``simultaneous_null_upper``);
    these are computed alongside and never alter the pointwise outputs.
    """
    observed = ordered_spectrum(off_diagonal_cross_view_operator(blocks, view_names=view_names))
    upper = np.asarray(null_upper, dtype=float)
    if observed.shape != upper.shape:
        raise ValueError("Observed and null spectra must share dimension.")

    def _summary(excess: np.ndarray) -> tuple[float, float, int]:
        total = float(excess.sum())
        if total <= 1e-12:
            return 0.0, 0.0, 0
        probabilities = excess / total
        positive = probabilities[probabilities > 1e-15]
        entropy_rank = float(np.exp(-np.sum(positive * np.log(positive))))
        participation_rank = float(total**2 / np.sum(excess**2))
        energy_90_rank = int(np.searchsorted(np.cumsum(excess) / total, 0.90, side="left") + 1)
        return entropy_rank, participation_rank, energy_90_rank

    # A less-negative eigenvalue than the broken-correspondence null is not a
    # positive shared mode. Retain only covariance modes that are both positive
    # in the observed operator and above the frozen null envelope.
    excess = np.where(observed > 0.0, np.maximum(observed - upper, 0.0), 0.0)
    entropy_rank, participation_rank, energy_90_rank = _summary(excess)
    result: dict[str, Any] = {
        "observed_eigenvalues": observed,
        "null_upper_eigenvalues": upper,
        "excess_eigenvalues": excess,
        "n_positive_excess": int(np.sum(excess > 1e-12)),
        "entropy_effective_rank": entropy_rank,
        "participation_effective_rank": participation_rank,
        "excess_energy_90_rank": energy_90_rank,
    }
    if null_spectra is not None:
        bound = simultaneous_null_upper(null_spectra, quantile=simultaneous_quantile)
        if np.asarray(null_spectra, dtype=float).shape[1] != observed.shape[0]:
            raise ValueError("Simultaneous null spectra must share the observed spectrum dimension.")
        excess_simultaneous = np.where(observed > 0.0, np.maximum(observed - bound, 0.0), 0.0)
        result["null_upper_simultaneous"] = bound
        result["excess_eigenvalues_simultaneous"] = excess_simultaneous
        result["n_positive_excess_simultaneous"] = int(np.sum(excess_simultaneous > 1e-12))
    return result


def profile_cosine(left: np.ndarray, right: np.ndarray) -> float:
    """Return cosine similarity for nonnegative spectral-excess profiles."""
    a, b = np.asarray(left, dtype=float), np.asarray(right, dtype=float)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(a @ b / denom) if denom > 1e-12 else float("nan")
