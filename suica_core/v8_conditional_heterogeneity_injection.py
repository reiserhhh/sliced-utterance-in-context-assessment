"""Geometry and estimands for the H4D-R2E injection frontier."""
from __future__ import annotations

from typing import Any

import numpy as np

from suica_core.v8_minority_information_frontier import (
    complete_double_center,
)


def _unit(values: np.ndarray) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    norm = float(np.linalg.norm(result))
    if norm <= 1e-12:
        raise ValueError("cannot normalize a zero geometry")
    return result / norm


def orthonormal_geometry_frame(
    core: np.ndarray,
    halo: np.ndarray,
    *,
    seed: int,
    maximum_attempts: int = 100,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return double-centered orthonormal core, halo, and tangent axes."""
    c = _unit(complete_double_center(np.asarray(core, dtype=float)))
    h = complete_double_center(np.asarray(halo, dtype=float))
    h = _unit(h - float(np.sum(h * c)) * c)
    rng = np.random.default_rng(int(seed))
    for _ in range(int(maximum_attempts)):
        tangent = complete_double_center(rng.normal(size=c.shape))
        tangent -= float(np.sum(tangent * c)) * c
        tangent -= float(np.sum(tangent * h)) * h
        norm = float(np.linalg.norm(tangent))
        if norm <= 1e-12:
            continue
        tangent /= norm
        author_energy = np.linalg.norm(tangent, axis=(1, 2))
        if np.all(author_energy > 1e-12):
            return c, h, tangent
    raise RuntimeError("failed to generate an all-author tangent axis")


def injection_geometry(
    core: np.ndarray,
    halo: np.ndarray,
    tangent: np.ndarray,
    *,
    theta: float,
    arm: str,
    magnitude: float,
    sign: int,
) -> np.ndarray:
    """Construct one unit-norm baseline, normal, or tangent geometry."""
    c = np.asarray(core, dtype=float)
    h = np.asarray(halo, dtype=float)
    t = np.asarray(tangent, dtype=float)
    if arm == "baseline":
        if sign != 0 or float(magnitude) != 0.0:
            raise ValueError("baseline requires zero sign and magnitude")
        result = np.cos(float(theta)) * c + np.sin(float(theta)) * h
    elif arm == "normal":
        if sign not in {-1, 1}:
            raise ValueError("normal arm requires sign +/-1")
        angle = float(theta) + int(sign) * float(magnitude)
        result = np.cos(angle) * c + np.sin(angle) * h
    elif arm == "tangent":
        if sign not in {-1, 1}:
            raise ValueError("tangent arm requires sign +/-1")
        rotated_halo = (
            np.cos(float(magnitude)) * h
            + int(sign) * np.sin(float(magnitude)) * t
        )
        result = (
            np.cos(float(theta)) * c
            + np.sin(float(theta)) * rotated_halo
        )
    else:
        raise ValueError(f"unknown injection arm: {arm}")
    return result


def frame_audit(
    core: np.ndarray,
    halo: np.ndarray,
    tangent: np.ndarray,
) -> dict[str, float]:
    """Return orthogonality and double-centering diagnostics."""
    axes = [
        np.asarray(core, dtype=float),
        np.asarray(halo, dtype=float),
        np.asarray(tangent, dtype=float),
    ]
    marginal_error = max(
        max(
            float(np.max(np.abs(axis.mean(axis=0)))),
            float(np.max(np.abs(axis.mean(axis=1)))),
        )
        for axis in axes
    )
    return {
        "maximum_axis_norm_error": float(
            max(abs(float(np.linalg.norm(axis)) - 1.0) for axis in axes)
        ),
        "maximum_axis_inner_product": float(
            max(
                abs(float(np.sum(axes[left] * axes[right])))
                for left, right in [(0, 1), (0, 2), (1, 2)]
            )
        ),
        "maximum_double_centering_marginal_error": marginal_error,
    }


def geometry_audit(
    geometry: np.ndarray,
    core: np.ndarray,
    *,
    expected_halo_share: float,
) -> dict[str, Any]:
    """Audit norm, halo share, marginals, and realized author support."""
    q = np.asarray(geometry, dtype=float)
    c = np.asarray(core, dtype=float)
    norm_squared = float(np.sum(q**2))
    core_share = (
        float(np.sum(q * c)) ** 2 / max(norm_squared, 1e-12)
    )
    halo_share = 1.0 - core_share
    author_energy = np.linalg.norm(q, axis=(1, 2))
    return {
        "geometry_norm_error": abs(np.sqrt(norm_squared) - 1.0),
        "realized_halo_share": halo_share,
        "halo_share_error": abs(
            halo_share - float(expected_halo_share)
        ),
        "realized_author_support": int(
            np.sum(author_energy > 1e-12)
        ),
        "minimum_author_energy": float(author_energy.min()),
        "maximum_geometry_marginal_error": float(
            max(
                np.max(np.abs(q.mean(axis=0))),
                np.max(np.abs(q.mean(axis=1))),
            )
        ),
    }


def paired_direction_sensitivity(
    plus: np.ndarray,
    minus: np.ndarray,
) -> float:
    """Estimate J=E[(p_plus-p_minus)^2]/4 without truncation."""
    positive = np.asarray(plus, dtype=float)
    negative = np.asarray(minus, dtype=float)
    if positive.shape != negative.shape or positive.ndim != 2:
        raise ValueError("plus and minus must be paired base x replicate")
    if positive.shape[1] < 2:
        raise ValueError("direction sensitivity needs repeated outcomes")
    difference = positive - negative
    mean_difference = difference.mean(axis=1)
    sampling_variance = difference.var(axis=1, ddof=1)
    unbiased_square = (
        mean_difference**2
        - sampling_variance / difference.shape[1]
    )
    return float(unbiased_square.mean() / 4.0)
