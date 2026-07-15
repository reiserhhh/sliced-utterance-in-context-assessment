"""Centred ordered-transition operators for SUICA's label-free path analysis.

The primary object removes first-order source and successor marginals before
asking whether an author's *ordering* is reproducible. It is deliberately a
mathematical path object, not a personality factor or a longitudinal clinical
state estimate.
"""
from __future__ import annotations

import hashlib
import itertools

import numpy as np

from suica_core.joint_process import row_l2_normalize


def centered_transition_operator(
    source: np.ndarray,
    target: np.ndarray,
    *,
    diagonal_standardize: bool = False,
) -> np.ndarray:
    """Return a centred cross-operator for aligned ordered event pairs.

    With ``diagonal_standardize=True``, the result is the elementwise
    cross-correlation operator. This removes source/target marginal amplitude
    differences that would otherwise make a shared transition law look
    author-specific merely because authors have different event variances.
    """
    x = np.asarray(source, dtype=float)
    y = np.asarray(target, dtype=float)
    if x.ndim != 2 or y.ndim != 2 or x.shape != y.shape or len(x) < 2:
        raise ValueError("source and target must be aligned matrices with at least two pairs")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("transition values must be finite")
    x_centered = x - x.mean(axis=0, keepdims=True)
    y_centered = y - y.mean(axis=0, keepdims=True)
    operator = (x_centered.T @ y_centered) / len(x)
    if diagonal_standardize:
        source_scale = np.sqrt(np.mean(x_centered ** 2, axis=0))
        target_scale = np.sqrt(np.mean(y_centered ** 2, axis=0))
        operator = operator / np.maximum(np.outer(source_scale, target_scale), 1e-8)
    return operator.ravel()


def ordered_pairs_from_blocks(blocks: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Extract within-block adjacent ordered pairs without joining separate blocks."""
    array = np.asarray(blocks, dtype=float)
    if array.ndim != 3 or array.shape[1] < 2:
        raise ValueError("blocks must have shape (n_blocks, block_size>=2, dimension)")
    return array[:, :-1, :].reshape(-1, array.shape[2]), array[:, 1:, :].reshape(-1, array.shape[2])


def block_order_null_operator(
    blocks: np.ndarray,
    *,
    draws: int,
    seed_key: str,
    diagonal_standardize: bool = False,
) -> np.ndarray:
    """Average nonidentity within-block order null operators.

    The null preserves every block's event multiset, author membership, and
    block topology. It destroys only observed within-block order. It therefore
    controls first-order event composition more tightly than a global successor
    shuffle, while still being a technical null rather than a causal control.
    """
    array = np.asarray(blocks, dtype=float)
    if draws < 1:
        raise ValueError("draws must be positive")
    digest = hashlib.sha256(seed_key.encode("utf-8")).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
    identity = tuple(range(array.shape[1]))
    nonidentity = [np.asarray(permutation, dtype=int)
                   for permutation in itertools.permutations(range(array.shape[1]))
                   if permutation != identity]
    if not nonidentity:
        raise ValueError("no nonidentity within-block permutation exists")
    # With three-event blocks and five draws, each block visits every possible
    # nonidentity local ordering once, eliminating Monte-Carlo noise from the
    # default null while avoiding a factorial enumeration of all block products.
    effective_draws = min(draws, len(nonidentity))
    offsets = rng.integers(0, len(nonidentity), size=len(array))
    estimates = []
    for draw in range(effective_draws):
        permuted = np.stack([
            block[nonidentity[(offsets[index] + draw) % len(nonidentity)]]
            for index, block in enumerate(array)
        ])
        source, target = ordered_pairs_from_blocks(permuted)
        estimates.append(centered_transition_operator(
            source, target, diagonal_standardize=diagonal_standardize,
        ))
    return np.mean(np.vstack(estimates), axis=0)


def alignment_margins(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Return each author's matched cosine advantage over all strangers."""
    a = row_l2_normalize(left)
    b = row_l2_normalize(right)
    if a.ndim != 2 or b.ndim != 2 or a.shape != b.shape or len(a) < 4:
        raise ValueError("left/right must be aligned matrices with at least four authors")
    similarity = a @ b.T
    diagonal = np.diag(similarity)
    stranger_mean = (similarity.sum(axis=1) - diagonal) / (len(a) - 1)
    return diagonal - stranger_mean


def paired_bootstrap_mean(
    values: np.ndarray,
    *,
    iterations: int,
    seed: int,
) -> dict[str, float]:
    """Bootstrap the mean paired contrast across authors.

    This is an uncertainty summary for the fixed author sample. It is not a
    confidence interval for a named psychological construct.
    """
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or len(array) < 4 or not np.isfinite(array).all():
        raise ValueError("values must be a finite one-dimensional array of length at least four")
    if iterations < 100:
        raise ValueError("iterations must be at least 100")
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(array), size=(iterations, len(array)))
    estimates = array[indices].mean(axis=1)
    return {
        "mean": float(array.mean()),
        "ci_lo": float(np.quantile(estimates, 0.025)),
        "ci_hi": float(np.quantile(estimates, 0.975)),
    }


def sign_flip_pvalue(values: np.ndarray, *, iterations: int, seed: int) -> float:
    """Return a two-sided paired sign-flip p-value for a mean contrast."""
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or len(array) < 4 or not np.isfinite(array).all():
        raise ValueError("values must be a finite one-dimensional array of length at least four")
    if iterations < 100:
        raise ValueError("iterations must be at least 100")
    observed = abs(float(array.mean()))
    rng = np.random.default_rng(seed)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(iterations, len(array)))
    null = abs((signs * array).mean(axis=1))
    return float((1 + np.sum(null >= observed)) / (iterations + 1))
