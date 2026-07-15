"""Synthetic identification limits for V7 representation/domain transport.

These worlds are not language models and not personality simulations. They
make one narrow fact executable: a frozen procedure can be reused in a new
domain, while cross-domain numerical coordinates require an identified map.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.stats import spearmanr


@dataclass(frozen=True)
class TransportWorld:
    """Paired or deliberately unpaired source/target representation world."""

    name: str
    source: np.ndarray
    target: np.ndarray
    anchor_index: np.ndarray | None
    holdout_index: np.ndarray | None
    paired_available: bool


def _orthogonal(rng: np.random.Generator, dimension: int) -> np.ndarray:
    matrix, _ = np.linalg.qr(rng.normal(size=(dimension, dimension)))
    return matrix


def _r2(target: np.ndarray, prediction: np.ndarray) -> float:
    denominator = float(np.sum((target - target.mean(axis=0, keepdims=True)) ** 2))
    return float(1.0 - np.sum((target - prediction) ** 2) / denominator) if denominator > 1e-12 else float("nan")


def _distance_spearman(left: np.ndarray, right: np.ndarray) -> float:
    upper = np.triu_indices(len(left), k=1)
    left_distance = np.linalg.norm(left[:, None, :] - left[None, :, :], axis=2)[upper]
    right_distance = np.linalg.norm(right[:, None, :] - right[None, :, :], axis=2)[upper]
    value = spearmanr(left_distance, right_distance).statistic
    return float(value) if np.isfinite(value) else float("nan")


def _retrieval_accuracy(source: np.ndarray, target: np.ndarray) -> float:
    distances = np.linalg.norm(target[:, None, :] - source[None, :, :], axis=2)
    return float(np.mean(np.argmin(distances, axis=1) == np.arange(len(source))))


def _procrustes_target_to_source(source_anchor: np.ndarray, target_anchor: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Fit the orthogonal map only because paired anchors are supplied."""
    source_center = source_anchor.mean(axis=0, keepdims=True)
    target_center = target_anchor.mean(axis=0, keepdims=True)
    left, _, right_t = np.linalg.svd((target_anchor - target_center).T @ (source_anchor - source_center), full_matrices=False)
    rotation = left @ right_t
    return (target - target_center) @ rotation + source_center


def _affine_target_to_source(source_anchor: np.ndarray, target_anchor: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Fit an affine paired-anchor map; never use it with unpaired data."""
    design = np.column_stack([target_anchor, np.ones(len(target_anchor))])
    coefficients, *_ = np.linalg.lstsq(design, source_anchor, rcond=None)
    return np.column_stack([target, np.ones(len(target))]) @ coefficients


def _whiten(values: np.ndarray) -> np.ndarray:
    centered = values - values.mean(axis=0, keepdims=True)
    covariance = np.cov(centered, rowvar=False, ddof=1)
    eigenvalues, eigenvectors = np.linalg.eigh(0.5 * (covariance + covariance.T))
    transform = (eigenvectors * (1.0 / np.sqrt(np.maximum(eigenvalues, 1e-9)))[None, :]) @ eigenvectors.T
    return centered @ transform


def generate_transport_world(kind: str, *, seed: int, persons: int, features: int, noise_scale: float, anchor_fraction: float) -> TransportWorld:
    """Create one declared source/target world with known transport status."""
    if persons < 20 or features < 2 or not 0.1 <= anchor_fraction < 0.9:
        raise ValueError("Transport world needs >=20 persons, >=2 features, and anchor_fraction in [0.1, 0.9).")
    rng = np.random.default_rng(int(seed))
    latent = rng.normal(size=(persons, features))
    source = latent + rng.normal(scale=noise_scale, size=latent.shape)
    order = rng.permutation(persons)
    anchor_count = max(features + 2, int(round(persons * anchor_fraction)))
    anchors, holdout = order[:anchor_count], order[anchor_count:]
    if kind == "common_coordinate":
        target = latent + rng.normal(scale=noise_scale, size=latent.shape)
        return TransportWorld(kind, source, target, anchors, holdout, True)
    if kind == "unknown_rotation":
        target = latent @ _orthogonal(rng, features) + rng.normal(scale=noise_scale, size=latent.shape)
        return TransportWorld(kind, source, target, anchors, holdout, True)
    if kind == "unknown_affine":
        rotation = _orthogonal(rng, features)
        scale = np.linspace(0.45, 2.0, features)
        affine = rotation @ np.diag(scale) @ _orthogonal(rng, features)
        target = latent @ affine + rng.normal(scale=noise_scale, size=latent.shape) + rng.normal(scale=0.5, size=(1, features))
        return TransportWorld(kind, source, target, anchors, holdout, True)
    if kind == "unpaired_isotropic_orientation_ambiguity":
        permutation = rng.permutation(persons)
        target = latent[permutation] @ _orthogonal(rng, features) + rng.normal(scale=noise_scale, size=latent.shape)
        return TransportWorld(kind, source, target, None, None, False)
    raise ValueError(f"Unknown representation transport world: {kind}")


def evaluate_transport_world(world: TransportWorld) -> dict[str, float | str | bool]:
    """Evaluate only the transport operations licensed by each synthetic world."""
    source, target = world.source, world.target
    result: dict[str, float | str | bool] = {
        "world": world.name,
        "paired_available": world.paired_available,
        "source_target_covariance_frobenius_gap": float(np.linalg.norm(np.cov(source, rowvar=False) - np.cov(target, rowvar=False), ord="fro")),
    }
    if not world.paired_available:
        result.update({
            "within_domain_distribution_orientation_ambiguous": True,
            "cross_domain_coordinate_status": "REFUSE_UNPAIRED_ORIENTATION_NOT_IDENTIFIED",
            "paired_relative_distance_spearman": float("nan"),
            "naive_coordinate_r2": float("nan"),
            "naive_retrieval_accuracy": float("nan"),
            "procrustes_coordinate_r2": float("nan"),
            "procrustes_retrieval_accuracy": float("nan"),
            "affine_coordinate_r2": float("nan"),
            "affine_retrieval_accuracy": float("nan"),
            "separate_whitened_distance_spearman": float("nan"),
        })
        return result
    assert world.anchor_index is not None and world.holdout_index is not None
    anchors, holdout = world.anchor_index, world.holdout_index
    source_hold, target_hold = source[holdout], target[holdout]
    procrustes = _procrustes_target_to_source(source[anchors], target[anchors], target_hold)
    affine = _affine_target_to_source(source[anchors], target[anchors], target_hold)
    result.update({
        "within_domain_distribution_orientation_ambiguous": False,
        "cross_domain_coordinate_status": "PAIRED_ANCHOR_EVALUATED",
        "paired_relative_distance_spearman": _distance_spearman(source_hold, target_hold),
        "naive_coordinate_r2": _r2(source_hold, target_hold),
        "naive_retrieval_accuracy": _retrieval_accuracy(source_hold, target_hold),
        "procrustes_coordinate_r2": _r2(source_hold, procrustes),
        "procrustes_retrieval_accuracy": _retrieval_accuracy(source_hold, procrustes),
        "affine_coordinate_r2": _r2(source_hold, affine),
        "affine_retrieval_accuracy": _retrieval_accuracy(source_hold, affine),
        "separate_whitened_distance_spearman": _distance_spearman(_whiten(source_hold), _whiten(target_hold)),
    })
    return result


def run_transport_matrix(config: dict[str, Any]) -> list[dict[str, float | str | bool]]:
    """Run all registered mathematical transport worlds without human text."""
    rows: list[dict[str, float | str | bool]] = []
    for world_index, kind in enumerate(config["worlds"]):
        for repetition in range(int(config["repetitions"])):
            world = generate_transport_world(
                str(kind),
                seed=int(config["seed"]) + 10000 * world_index + repetition,
                persons=int(config["persons"]),
                features=int(config["features"]),
                noise_scale=float(config["noise_scale"]),
                anchor_fraction=float(config["anchor_fraction"]),
            )
            row = evaluate_transport_world(world)
            row["repetition"] = repetition
            rows.append(row)
    return rows
