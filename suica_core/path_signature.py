"""Truncated, time-augmented path signatures for SUICA trajectory probes.

The signature is a geometric path object rather than a factor axis. For a
piecewise-linear path X, level k stores the iterated integral

    S_k(X) = integral_{t1 < ... < tk} dX_t1 tensor ... tensor dX_tk.

Chen's identity lets us calculate it exactly from discrete increments. With a
strictly increasing time coordinate, the full signature distinguishes bounded
variation paths up to the usual tree-like equivalence. A finite truncation is a
registered, non-injective measurement map and must not be treated as a complete
path recovery.
"""
from __future__ import annotations

import math

import numpy as np


def signature_dimension(dimension: int, depth: int, *, include_level_zero: bool = False) -> int:
    """Return flattened tensor-algebra dimension through ``depth``."""
    if dimension < 1 or depth < 1:
        raise ValueError("dimension and depth must be positive")
    start = 0 if include_level_zero else 1
    return int(sum(dimension ** level for level in range(start, depth + 1)))


def _tensor_power(vector: np.ndarray, level: int) -> np.ndarray:
    result = np.array([1.0])
    for _ in range(level):
        result = np.kron(result, vector)
    return result


def piecewise_linear_signature(path: np.ndarray, depth: int = 3,
                               *, include_level_zero: bool = False) -> np.ndarray:
    """Compute a truncated signature via Chen products of straight segments.

    Parameters
    ----------
    path:
        ``(n_points, dimension)`` path. Consecutive duplicates are allowed.
    depth:
        Maximum iterated-integral degree. Depth 3 is 39 coordinates for a
        time-augmented two-dimensional path, so it is tractable for sparse text
        trajectories while including ordered pair and triple interactions.
    """
    x = np.asarray(path, float)
    if x.ndim != 2 or len(x) < 2:
        raise ValueError("path must be a two-dimensional array with at least two points")
    if not np.isfinite(x).all():
        raise ValueError("path contains non-finite values")
    d = x.shape[1]
    levels = [np.array([1.0])] + [np.zeros(d ** order) for order in range(1, depth + 1)]
    for increment in np.diff(x, axis=0):
        segment = [np.array([1.0])]
        for order in range(1, depth + 1):
            segment.append(_tensor_power(increment, order) / math.factorial(order))
        updated = []
        for order in range(depth + 1):
            updated.append(sum(np.kron(levels[left], segment[order - left])
                               for left in range(order + 1)))
        levels = updated
    start = 0 if include_level_zero else 1
    return np.concatenate(levels[start:])


def time_augmented_shape_path(points: np.ndarray, *, normalize_shape: bool = True) -> tuple[np.ndarray, float]:
    """Center a path, optionally normalize its spatial variation, then add time.

    Returning the removed scale keeps amplitude available as a separate,
    opportunity-auditable quantity. The signature itself then represents ordered
    shape rather than raw comment count or vector magnitude.
    """
    x = np.asarray(points, float)
    if x.ndim != 2 or len(x) < 2:
        raise ValueError("points must be a two-dimensional array with at least two points")
    centered = x - x[0]
    increments = np.diff(centered, axis=0)
    scale = float(np.sqrt(np.mean(np.sum(increments ** 2, axis=1))))
    if normalize_shape and scale > 1e-12:
        centered = centered / scale
    time = np.linspace(0.0, 1.0, len(x))[:, None]
    return np.column_stack([time, centered]), scale


def path_signature_features(points: np.ndarray, depth: int = 3,
                            *, normalize_shape: bool = True) -> tuple[np.ndarray, float]:
    """Return a time-augmented signature and the separately retained path scale."""
    path, scale = time_augmented_shape_path(points, normalize_shape=normalize_shape)
    return piecewise_linear_signature(path, depth=depth), scale
