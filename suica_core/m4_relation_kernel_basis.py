"""Response-safe relation-kernel bases for M4-C.3.2."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial.distance import cdist, pdist, squareform


@dataclass(frozen=True)
class FrozenRelationKernelBasis:
    """Calibration-only centered RBF kernel PCA with Nyström transport."""

    calibration_relation: np.ndarray
    bandwidth: float
    eigenvectors: np.ndarray
    eigenvalues: np.ndarray
    calibration_column_mean: np.ndarray
    calibration_grand_mean: float

    def transform(self, relation: np.ndarray) -> np.ndarray:
        """Transport relation coordinates without reading path outcomes."""
        values = np.asarray(relation, dtype=float)
        distance = cdist(values, self.calibration_relation)
        kernel = np.exp(
            -0.5 * (distance / max(self.bandwidth, 1e-12)) ** 2
        )
        centered = (
            kernel
            - np.mean(kernel, axis=1, keepdims=True)
            - self.calibration_column_mean[None]
            + self.calibration_grand_mean
        )
        coordinates = (
            centered @ self.eigenvectors
            / np.sqrt(self.eigenvalues)[None]
        )
        return np.column_stack([np.ones(len(values)), coordinates])


def freeze_relation_kernel_basis(
    calibration_basis: np.ndarray,
    *,
    rank: int,
    bandwidth_scale: float = 1.0,
    eigen_tolerance: float = 1e-8,
) -> FrozenRelationKernelBasis:
    """Fit one relation kernel using calibration conditions only."""
    relation = np.asarray(calibration_basis, dtype=float)[:, 1:]
    distance = squareform(pdist(relation))
    positive = distance[distance > 1e-12]
    bandwidth = (
        float(np.median(positive)) * bandwidth_scale
        if len(positive)
        else bandwidth_scale
    )
    kernel = np.exp(
        -0.5 * (distance / max(bandwidth, 1e-12)) ** 2
    )
    count = len(kernel)
    centering = np.eye(count) - np.ones((count, count)) / count
    centered = centering @ kernel @ centering
    eigenvalues, eigenvectors = np.linalg.eigh(centered)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    threshold = max(float(eigenvalues[0]), 1e-12) * eigen_tolerance
    keep = np.flatnonzero(eigenvalues > threshold)[:rank]
    if len(keep) == 0:
        raise ValueError("relation kernel has no resolved dimensions")
    return FrozenRelationKernelBasis(
        calibration_relation=relation.copy(),
        bandwidth=bandwidth,
        eigenvectors=eigenvectors[:, keep].copy(),
        eigenvalues=eigenvalues[keep].copy(),
        calibration_column_mean=np.mean(kernel, axis=0),
        calibration_grand_mean=float(np.mean(kernel)),
    )


def build_relation_kernel_bases(
    discovered_basis: dict[str, np.ndarray],
    *,
    rank: int,
    bandwidth_scale: float = 1.0,
) -> tuple[FrozenRelationKernelBasis, dict[str, np.ndarray]]:
    """Fit on calibration and transform every declared mechanism role."""
    frozen = freeze_relation_kernel_basis(
        discovered_basis["calibration"],
        rank=rank,
        bandwidth_scale=bandwidth_scale,
    )
    return frozen, {
        role: frozen.transform(values[:, 1:])
        for role, values in discovered_basis.items()
    }
