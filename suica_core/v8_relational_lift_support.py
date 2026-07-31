"""Support-gated population relation lift for SUICA V8-HJIC-1A.

Licensing uses only replicated observations, declared nuisance variables,
independent author splits, bootstrap perturbations, and conditional
permutations. Synthetic truth is returned separately for post-license audit
and is never accepted by :func:`license_relation`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .v8_hierarchical_identifiability import safe_correlation


@dataclass(frozen=True)
class RelationSupportSpec:
    """Dimensions and resampling budgets for one relation-lift world."""

    authors: int = 2400
    big5_dimensions: int = 5
    mbti_dimensions: int = 4
    shared_dimensions: int = 2
    repeated_splits: int = 32
    bootstrap_draws: int = 120
    permutations: int = 199
    view_noise: float = 0.55
    anchor_private_noise: float = 1.0
    relation_norm_floor: float = 0.10
    material_relation_shift: float = 0.10
    material_cell_shift: float = 0.10

    def __post_init__(self) -> None:
        if self.authors < 400 or self.authors % 2:
            raise ValueError("Relation support requires an even n >= 400.")
        if self.big5_dimensions < 2 or self.mbti_dimensions < 2:
            raise ValueError("Both relation margins must be multivariate.")
        if not 1 <= self.shared_dimensions <= min(
            self.big5_dimensions,
            self.mbti_dimensions,
        ):
            raise ValueError("shared_dimensions must fit both margins.")
        if self.repeated_splits < 8:
            raise ValueError("At least eight independent splits are required.")
        if self.bootstrap_draws < 20 or self.permutations < 19:
            raise ValueError("Resampling budgets are too small.")
        if min(
            self.relation_norm_floor,
            self.material_relation_shift,
            self.material_cell_shift,
        ) <= 0:
            raise ValueError("Relation invariance tolerances must be positive.")


@dataclass(frozen=True)
class ReplicatedSupport:
    """Observable marginal subspaces shared by independent replicates."""

    big5_basis: np.ndarray
    mbti_basis: np.ndarray
    big5_eigenvalues: np.ndarray
    mbti_eigenvalues: np.ndarray
    big5_null_q99: float
    mbti_null_q99: float

    @property
    def big5_rank(self) -> int:
        return int(self.big5_basis.shape[1])

    @property
    def mbti_rank(self) -> int:
        return int(self.mbti_basis.shape[1])


def _center(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    return matrix - matrix.mean(axis=0, keepdims=True)


def _covariance(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    x = _center(left)
    y = _center(right)
    return x.T @ y / max(1, len(x) - 1)


def _sym_cross_covariance(
    first: np.ndarray,
    second: np.ndarray,
) -> np.ndarray:
    return 0.5 * (
        _covariance(first, second)
        + _covariance(second, first).T
    )


def _matrix_correlation(left: np.ndarray, right: np.ndarray) -> float:
    return safe_correlation(np.asarray(left).ravel(), np.asarray(right).ravel())


def _relation_matrix(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    covariance = _covariance(left, right)
    left_scale = np.sqrt(
        np.clip(np.diag(_covariance(left, left)), 1e-12, None)
    )
    right_scale = np.sqrt(
        np.clip(np.diag(_covariance(right, right)), 1e-12, None)
    )
    return covariance / np.outer(left_scale, right_scale)


def _replicated_relation_matrix(
    data: dict[str, np.ndarray],
) -> np.ndarray:
    sigma_big5 = _sym_cross_covariance(
        data["big5_first"],
        data["big5_second"],
    )
    sigma_mbti = _sym_cross_covariance(
        data["mbti_first"],
        data["mbti_second"],
    )
    diagonal_big5 = np.diag(sigma_big5)
    diagonal_mbti = np.diag(sigma_mbti)
    if np.any(diagonal_big5 <= 1e-10) or np.any(
        diagonal_mbti <= 1e-10
    ):
        raise ValueError("Replicated marginal variance is unsupported.")
    cross = 0.5 * (
        _covariance(data["big5_first"], data["mbti_second"])
        + _covariance(data["big5_second"], data["mbti_first"])
    )
    return cross / np.sqrt(np.outer(diagonal_big5, diagonal_mbti))


def relation_shift_statistics(
    raw_relation: np.ndarray,
    conditioned_relation: np.ndarray,
    *,
    spec: RelationSupportSpec,
) -> dict[str, float]:
    """Measure global and localized sensitivity to declared conditioning."""
    difference = np.asarray(raw_relation) - np.asarray(conditioned_relation)
    denominator = max(
        float(np.linalg.norm(raw_relation)),
        float(np.linalg.norm(conditioned_relation)),
        spec.relation_norm_floor,
    )
    global_shift = float(np.linalg.norm(difference) / denominator)
    maximum_cell_shift = float(np.max(np.abs(difference)))
    max_statistic = max(
        global_shift / spec.material_relation_shift,
        maximum_cell_shift / spec.material_cell_shift,
    )
    return {
        "global_shift": global_shift,
        "maximum_cell_shift": maximum_cell_shift,
        "max_statistic": max_statistic,
    }


def crossfit_residualize(
    values: np.ndarray,
    nuisance: np.ndarray,
    *,
    folds: np.ndarray,
) -> np.ndarray:
    """Residualize each row using nuisance models fitted on other folds."""
    values = np.asarray(values, dtype=float)
    nuisance = np.asarray(nuisance, dtype=float)
    folds = np.asarray(folds, dtype=int)
    design = np.column_stack([np.ones(len(nuisance)), nuisance])
    residual = np.full_like(values, np.nan, dtype=float)
    for fold in sorted(set(folds.tolist())):
        train = folds != fold
        test = folds == fold
        coefficients = np.linalg.lstsq(
            design[train],
            values[train],
            rcond=None,
        )[0]
        residual[test] = values[test] - design[test] @ coefficients
    if not np.isfinite(residual).all():
        raise RuntimeError("Cross-fit residualization produced missing values.")
    return residual


def _strict_inverse_sqrt(
    covariance: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float]:
    symmetric = 0.5 * (covariance + covariance.T)
    values, vectors = np.linalg.eigh(symmetric)
    if np.any(values <= 1e-10):
        raise ValueError("Frozen replicated support lost positive variance.")
    inverse = (
        vectors
        @ np.diag(1.0 / np.sqrt(values))
        @ vectors.T
    )
    condition = float(values.max() / values.min())
    return inverse, values, condition


def _margin_support(
    first: np.ndarray,
    second: np.ndarray,
    *,
    rng: np.random.Generator,
    permutations: int,
) -> tuple[np.ndarray, np.ndarray, float]:
    covariance = _sym_cross_covariance(first, second)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    null_maxima = []
    for _ in range(permutations):
        order = rng.permutation(len(first))
        null_covariance = _sym_cross_covariance(first, second[order])
        null_maxima.append(float(np.linalg.eigvalsh(null_covariance).max()))
    null_q99 = float(np.quantile(null_maxima, 0.99))
    supported = eigenvalues > null_q99
    if not supported.any():
        raise ValueError("No replicated direction exceeds the null support.")
    return eigenvectors[:, supported], eigenvalues, null_q99


def estimate_replicated_support(
    big5_first: np.ndarray,
    big5_second: np.ndarray,
    mbti_first: np.ndarray,
    mbti_second: np.ndarray,
    *,
    rng: np.random.Generator,
    permutations: int,
) -> ReplicatedSupport:
    """Estimate marginal support without using cross-scale pairing or truth."""
    big5_basis, big5_eigenvalues, big5_null_q99 = _margin_support(
        big5_first,
        big5_second,
        rng=rng,
        permutations=permutations,
    )
    mbti_basis, mbti_eigenvalues, mbti_null_q99 = _margin_support(
        mbti_first,
        mbti_second,
        rng=rng,
        permutations=permutations,
    )
    return ReplicatedSupport(
        big5_basis=big5_basis,
        mbti_basis=mbti_basis,
        big5_eigenvalues=big5_eigenvalues,
        mbti_eigenvalues=mbti_eigenvalues,
        big5_null_q99=big5_null_q99,
        mbti_null_q99=mbti_null_q99,
    )


def replicated_relation_object(
    big5_first: np.ndarray,
    big5_second: np.ndarray,
    mbti_first: np.ndarray,
    mbti_second: np.ndarray,
    *,
    support: ReplicatedSupport,
) -> dict[str, Any]:
    """Estimate cross-replicate relation and whitened structure operator."""
    sigma_big5 = _sym_cross_covariance(big5_first, big5_second)
    sigma_mbti = _sym_cross_covariance(mbti_first, mbti_second)
    cross_12 = _covariance(big5_first, mbti_second)
    cross_21 = _covariance(big5_second, mbti_first)
    cross = 0.5 * (cross_12 + cross_21)
    diagonal_big5 = np.diag(sigma_big5)
    diagonal_mbti = np.diag(sigma_mbti)
    if np.any(diagonal_big5 <= 1e-10) or np.any(diagonal_mbti <= 1e-10):
        raise ValueError("Replicated marginal variance is unsupported.")
    relation = cross / np.sqrt(
        np.outer(diagonal_big5, diagonal_mbti)
    )
    direction_12 = cross_12 / np.sqrt(
        np.outer(diagonal_big5, diagonal_mbti)
    )
    direction_21 = cross_21 / np.sqrt(
        np.outer(diagonal_big5, diagonal_mbti)
    )
    supported_big5 = (
        support.big5_basis.T @ sigma_big5 @ support.big5_basis
    )
    supported_mbti = (
        support.mbti_basis.T @ sigma_mbti @ support.mbti_basis
    )
    supported_cross = (
        support.big5_basis.T @ cross @ support.mbti_basis
    )
    inverse_big5, eigen_big5, condition_big5 = _strict_inverse_sqrt(
        supported_big5
    )
    inverse_mbti, eigen_mbti, condition_mbti = _strict_inverse_sqrt(
        supported_mbti
    )
    operator = inverse_big5 @ supported_cross @ inverse_mbti
    singular_values = np.linalg.svd(operator, compute_uv=False)
    return {
        "relation": relation,
        "direction_12": direction_12,
        "direction_21": direction_21,
        "operator": operator,
        "singular_values": singular_values,
        "big5_eigenvalues": eigen_big5,
        "mbti_eigenvalues": eigen_mbti,
        "big5_condition": condition_big5,
        "mbti_condition": condition_mbti,
        "big5_support_rank": support.big5_rank,
        "mbti_support_rank": support.mbti_rank,
        "maximum_canonical_correlation": float(singular_values[0]),
    }


def _fold_assignments(
    rng: np.random.Generator,
    authors: int,
) -> np.ndarray:
    order = rng.permutation(authors)
    folds = np.empty(authors, dtype=int)
    folds[order[: authors // 2]] = 0
    folds[order[authors // 2 :]] = 1
    return folds


def _random_loadings(
    rng: np.random.Generator,
    rows: int,
    columns: int,
) -> np.ndarray:
    matrix = rng.normal(size=(rows, columns))
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix


def _orthonormal_loadings(
    rng: np.random.Generator,
    rows: int,
    columns: int,
) -> np.ndarray:
    basis, _ = np.linalg.qr(rng.normal(size=(rows, columns)))
    return basis[:, :columns]


def simulate_relation_world(
    world: str,
    *,
    seed: int,
    spec: RelationSupportSpec,
) -> dict[str, Any]:
    """Generate replicated text readouts, anchors, nuisance, and locked truth."""
    rng = np.random.default_rng(seed)
    n = spec.authors
    b = spec.big5_dimensions
    m = spec.mbti_dimensions
    k = spec.shared_dimensions
    nuisance = rng.normal(size=(n, 2))
    folds = _fold_assignments(rng, n)
    big5_load = _random_loadings(rng, b, k)
    mbti_load = _random_loadings(rng, m, k)
    anchor_noise_b = rng.normal(
        scale=spec.anchor_private_noise,
        size=(n, b),
    )
    anchor_noise_m = rng.normal(
        scale=spec.anchor_private_noise,
        size=(n, m),
    )
    oracle_relation: np.ndarray | None
    true_shared_big5: np.ndarray
    true_shared_mbti: np.ndarray

    if world in ("SHARED_LATENT", "NULL_HIGH_DIM_NUISANCE"):
        if world == "NULL_HIGH_DIM_NUISANCE":
            nuisance = rng.normal(size=(n, 20))
        big5_load = _orthonormal_loadings(rng, b, k)
        mbti_load = _orthonormal_loadings(rng, m, k)
        strengths = np.linspace(0.65, 0.22, k)
        weighted_big5 = big5_load * strengths[None, :]
        weighted_mbti = mbti_load * strengths[None, :]
        shared = rng.normal(size=(n, k))
        private_scale = 0.35
        true_shared_big5 = (
            shared @ weighted_big5.T
            + rng.normal(scale=private_scale, size=(n, b))
        )
        true_shared_mbti = (
            shared @ weighted_mbti.T
            + rng.normal(scale=private_scale, size=(n, m))
        )
        anchor_big5 = true_shared_big5 + anchor_noise_b
        anchor_mbti = true_shared_mbti + anchor_noise_m
        covariance_cross = weighted_big5 @ weighted_mbti.T
        covariance_big5 = (
            weighted_big5 @ weighted_big5.T
            + (private_scale**2 + 1.0) * np.eye(b)
        )
        covariance_mbti = (
            weighted_mbti @ weighted_mbti.T
            + (private_scale**2 + 1.0) * np.eye(m)
        )
        oracle_relation = covariance_cross / np.sqrt(
            np.outer(
                np.diag(covariance_big5),
                np.diag(covariance_mbti),
            )
        )
    elif world == "WEAK_RELATION":
        big5_load = _orthonormal_loadings(rng, b, k)
        mbti_load = _orthonormal_loadings(rng, m, k)
        shared = rng.normal(size=(n, k))
        shared_scale = 0.06
        private_scale = 0.55
        true_shared_big5 = (
            shared_scale * shared @ big5_load.T
            + rng.normal(scale=private_scale, size=(n, b))
        )
        true_shared_mbti = (
            shared_scale * shared @ mbti_load.T
            + rng.normal(scale=private_scale, size=(n, m))
        )
        anchor_big5 = true_shared_big5 + anchor_noise_b
        anchor_mbti = true_shared_mbti + anchor_noise_m
        covariance_cross = (
            shared_scale**2 * big5_load @ mbti_load.T
        )
        covariance_big5 = (
            shared_scale**2 * big5_load @ big5_load.T
            + (private_scale**2 + 1.0) * np.eye(b)
        )
        covariance_mbti = (
            shared_scale**2 * mbti_load @ mbti_load.T
            + (private_scale**2 + 1.0) * np.eye(m)
        )
        oracle_relation = covariance_cross / np.sqrt(
            np.outer(
                np.diag(covariance_big5),
                np.diag(covariance_mbti),
            )
        )
    elif world == "COMMON_NUISANCE":
        true_shared_big5 = 0.55 * nuisance @ big5_load.T
        true_shared_mbti = 0.55 * nuisance @ mbti_load.T
        anchor_big5 = true_shared_big5 + anchor_noise_b
        anchor_mbti = true_shared_mbti + anchor_noise_m
        oracle_relation = np.zeros((b, m), dtype=float)
    elif world == "CORRELATED_REPLICATE_ERROR":
        true_shared_big5 = rng.normal(scale=0.35, size=(n, b))
        true_shared_mbti = rng.normal(scale=0.35, size=(n, m))
        anchor_big5 = true_shared_big5 + anchor_noise_b
        anchor_mbti = true_shared_mbti + anchor_noise_m
        oracle_relation = np.zeros((b, m), dtype=float)
    elif world == "LOW_SINGULAR_GAP":
        shared = rng.normal(size=(n, 2))
        big5_load = _orthonormal_loadings(rng, b, 2)
        mbti_load = _orthonormal_loadings(rng, m, 2)
        private_scale = 0.35
        true_shared_big5 = (
            0.55 * shared @ big5_load.T
            + rng.normal(scale=private_scale, size=(n, b))
        )
        true_shared_mbti = (
            0.55 * shared @ mbti_load.T
            + rng.normal(scale=private_scale, size=(n, m))
        )
        anchor_big5 = true_shared_big5 + anchor_noise_b
        anchor_mbti = true_shared_mbti + anchor_noise_m
        covariance_cross = 0.55**2 * big5_load @ mbti_load.T
        covariance_big5 = (
            0.55**2 * big5_load @ big5_load.T
            + (private_scale**2 + 1.0) * np.eye(b)
        )
        covariance_mbti = (
            0.55**2 * mbti_load @ mbti_load.T
            + (private_scale**2 + 1.0) * np.eye(m)
        )
        oracle_relation = covariance_cross / np.sqrt(
            np.outer(
                np.diag(covariance_big5),
                np.diag(covariance_mbti),
            )
        )
    elif world == "SIMPSON_MIXTURE":
        group = (nuisance[:, 0] > 0).astype(float)
        nuisance[:, 0] = group
        within = rng.normal(size=(n, k))
        true_shared_big5 = 0.45 * within @ big5_load.T
        true_shared_mbti = -0.45 * within @ mbti_load.T
        centered_group = group[:, None] - 0.5
        group_big5 = 1.5 * centered_group @ big5_load[:, :1].T
        group_mbti = 1.5 * centered_group @ mbti_load[:, :1].T
        true_shared_big5 += group_big5
        true_shared_mbti += group_mbti
        anchor_big5 = true_shared_big5 + anchor_noise_b
        anchor_mbti = true_shared_mbti + anchor_noise_m
        covariance_cross = -0.45**2 * big5_load @ mbti_load.T
        covariance_big5 = (
            0.45**2 * big5_load @ big5_load.T + np.eye(b)
        )
        covariance_mbti = (
            0.45**2 * mbti_load @ mbti_load.T + np.eye(m)
        )
        oracle_relation = covariance_cross / np.sqrt(
            np.outer(
                np.diag(covariance_big5),
                np.diag(covariance_mbti),
            )
        )
    elif world == "LOCALIZED_SIMPSON":
        group = (nuisance[:, 0] > 0).astype(float)
        nuisance[:, 0] = group
        shared = rng.normal(size=(n, k))
        big5_load = _orthonormal_loadings(rng, b, k)
        mbti_load = _orthonormal_loadings(rng, m, k)
        private_scale = 0.30
        true_shared_big5 = (
            0.40 * shared @ big5_load.T
            + rng.normal(scale=private_scale, size=(n, b))
        )
        true_shared_mbti = (
            0.40 * shared @ mbti_load.T
            + rng.normal(scale=private_scale, size=(n, m))
        )
        centered_group = group - 0.5
        true_shared_big5[:, 0] += 1.5 * centered_group
        true_shared_mbti[:, 0] += 1.5 * centered_group
        anchor_big5 = true_shared_big5 + anchor_noise_b
        anchor_mbti = true_shared_mbti + anchor_noise_m
        covariance_cross = 0.40**2 * big5_load @ mbti_load.T
        covariance_big5 = (
            0.40**2 * big5_load @ big5_load.T
            + (private_scale**2 + 1.0) * np.eye(b)
        )
        covariance_mbti = (
            0.40**2 * mbti_load @ mbti_load.T
            + (private_scale**2 + 1.0) * np.eye(m)
        )
        oracle_relation = covariance_cross / np.sqrt(
            np.outer(
                np.diag(covariance_big5),
                np.diag(covariance_mbti),
            )
        )
    elif world == "COLLIDER_OR_DESCENDANT_Z":
        latent_big5 = rng.normal(size=(n, b))
        latent_mbti = rng.normal(size=(n, m))
        stable_scale = 0.65
        true_shared_big5 = stable_scale * latent_big5
        true_shared_mbti = stable_scale * latent_mbti
        collider = (
            true_shared_big5[:, 0]
            + true_shared_mbti[:, 0]
            + rng.normal(scale=0.15, size=n)
        )
        nuisance = np.column_stack([
            collider,
            rng.normal(size=n),
        ])
        anchor_big5 = true_shared_big5 + anchor_noise_b
        anchor_mbti = true_shared_mbti + anchor_noise_m
        oracle_relation = np.zeros((b, m), dtype=float)
    elif world == "PRIVATE_AXES":
        latent_big5 = rng.normal(size=(n, b))
        latent_mbti = rng.normal(size=(n, m))
        true_shared_big5 = 0.65 * latent_big5
        true_shared_mbti = 0.65 * latent_mbti
        anchor_big5 = true_shared_big5 + anchor_noise_b
        anchor_mbti = true_shared_mbti + anchor_noise_m
        oracle_relation = np.zeros((b, m), dtype=float)
    else:
        raise ValueError(f"Unsupported relation world: {world}")

    if world == "CORRELATED_REPLICATE_ERROR":
        error_first = rng.normal(size=(n, k))
        error_second = rng.normal(size=(n, k))
        big5_first = (
            true_shared_big5
            + 0.8 * error_first @ big5_load.T
            + rng.normal(scale=0.25, size=(n, b))
        )
        mbti_first = (
            true_shared_mbti
            + 0.8 * error_first @ mbti_load.T
            + rng.normal(scale=0.25, size=(n, m))
        )
        big5_second = (
            true_shared_big5
            + 0.8 * error_second @ big5_load.T
            + rng.normal(scale=0.25, size=(n, b))
        )
        mbti_second = (
            true_shared_mbti
            + 0.8 * error_second @ mbti_load.T
            + rng.normal(scale=0.25, size=(n, m))
        )
    else:
        big5_first = true_shared_big5 + rng.normal(
            scale=spec.view_noise,
            size=(n, b),
        )
        big5_second = true_shared_big5 + rng.normal(
            scale=spec.view_noise,
            size=(n, b),
        )
        mbti_first = true_shared_mbti + rng.normal(
            scale=spec.view_noise,
            size=(n, m),
        )
        mbti_second = true_shared_mbti + rng.normal(
            scale=spec.view_noise,
            size=(n, m),
        )
    return {
        "world": world,
        "nuisance": nuisance,
        "folds": folds,
        "big5_first": big5_first,
        "big5_second": big5_second,
        "mbti_first": mbti_first,
        "mbti_second": mbti_second,
        "anchor_big5": anchor_big5,
        "anchor_mbti": anchor_mbti,
        "truth_lockbox": {
            "oracle_relation": oracle_relation,
            "true_shared_big5": true_shared_big5,
            "true_shared_mbti": true_shared_mbti,
        },
    }


def _raw_public_data(world: dict[str, Any]) -> dict[str, np.ndarray]:
    return {
        name: np.asarray(world[name], dtype=float)
        for name in (
            "big5_first",
            "big5_second",
            "mbti_first",
            "mbti_second",
            "anchor_big5",
            "anchor_mbti",
        )
    }


def _residualize_public_data(
    data: dict[str, np.ndarray],
    nuisance: np.ndarray,
    folds: np.ndarray,
) -> dict[str, np.ndarray]:
    return {
        name: crossfit_residualize(
            values,
            nuisance,
            folds=folds,
        )
        for name, values in data.items()
    }


def _residualized_public_data(world: dict[str, Any]) -> dict[str, np.ndarray]:
    return _residualize_public_data(
        _raw_public_data(world),
        np.asarray(world["nuisance"], dtype=float),
        np.asarray(world["folds"], dtype=int),
    )


def _safe_replicated_object(
    data: dict[str, np.ndarray],
    *,
    support: ReplicatedSupport,
) -> dict[str, Any] | None:
    try:
        return replicated_relation_object(
            data["big5_first"],
            data["big5_second"],
            data["mbti_first"],
            data["mbti_second"],
            support=support,
        )
    except (ValueError, np.linalg.LinAlgError):
        return None


def _subset(
    data: dict[str, np.ndarray],
    indices: np.ndarray,
) -> dict[str, np.ndarray]:
    return {
        key: values[indices]
        for key, values in data.items()
    }


def observable_relation_diagnostics(
    world: dict[str, Any],
    *,
    seed: int,
    spec: RelationSupportSpec,
    apply_nuisance_veto: bool = True,
    refit_bootstrap_residualizer: bool = True,
) -> dict[str, Any]:
    """Compute support diagnostics without reading ``truth_lockbox``."""
    rng = np.random.default_rng(seed)
    raw = _raw_public_data(world)
    nuisance = np.asarray(world["nuisance"], dtype=float)
    folds = np.asarray(world["folds"], dtype=int)
    conditioned = _residualized_public_data(world)
    try:
        replicated_support = estimate_replicated_support(
            conditioned["big5_first"],
            conditioned["big5_second"],
            conditioned["mbti_first"],
            conditioned["mbti_second"],
            rng=rng,
            permutations=spec.permutations,
        )
    except (ValueError, np.linalg.LinAlgError):
        return {
            "status": "MARGINAL_SUPPORT_FAILURE",
            "licensed": 0,
            "mode_licensed": 0,
            "support_failure": 1,
        }
    raw_object = _safe_replicated_object(
        raw,
        support=replicated_support,
    )
    point = _safe_replicated_object(
        conditioned,
        support=replicated_support,
    )
    if point is None:
        return {
            "status": "MARGINAL_SUPPORT_FAILURE",
            "licensed": 0,
            "mode_licensed": 0,
            "support_failure": 1,
        }

    raw_relation = (
        raw_object["relation"] if raw_object is not None else None
    )
    conditional_relation = point["relation"]
    raw_conditional_correlation = (
        _matrix_correlation(raw_relation, conditional_relation)
        if raw_relation is not None
        else float("nan")
    )
    raw_norm = (
        float(np.linalg.norm(raw_relation))
        if raw_relation is not None
        else float("nan")
    )
    conditional_norm = float(np.linalg.norm(conditional_relation))
    retention = (
        conditional_norm / raw_norm
        if np.isfinite(raw_norm) and raw_norm > 1e-12
        else 0.0
    )
    point_shift = (
        relation_shift_statistics(
            raw_relation,
            conditional_relation,
            spec=spec,
        )
        if raw_relation is not None
        else {
            "global_shift": float("inf"),
            "maximum_cell_shift": float("inf"),
            "max_statistic": float("inf"),
        }
    )

    split_predicted = []
    split_anchor = []
    split_cross = []
    for _ in range(spec.repeated_splits):
        assignment = _fold_assignments(rng, spec.authors)
        first = np.flatnonzero(assignment == 0)
        second = np.flatnonzero(assignment == 1)
        object_first = _safe_replicated_object(
            _subset(conditioned, first),
            support=replicated_support,
        )
        object_second = _safe_replicated_object(
            _subset(conditioned, second),
            support=replicated_support,
        )
        if object_first is None or object_second is None:
            continue
        anchor_first = _relation_matrix(
            conditioned["anchor_big5"][first],
            conditioned["anchor_mbti"][first],
        )
        anchor_second = _relation_matrix(
            conditioned["anchor_big5"][second],
            conditioned["anchor_mbti"][second],
        )
        split_predicted.append(
            _matrix_correlation(
                object_first["relation"],
                object_second["relation"],
            )
        )
        split_anchor.append(
            _matrix_correlation(anchor_first, anchor_second)
        )
        split_cross.extend([
            _matrix_correlation(
                object_first["relation"],
                anchor_second,
            ),
            _matrix_correlation(
                object_second["relation"],
                anchor_first,
            ),
        ])
    if (
        len(split_predicted) < max(4, spec.repeated_splits // 2)
        or len(split_anchor) != len(split_predicted)
        or len(split_cross) != 2 * len(split_predicted)
    ):
        return {
            "status": "SPLIT_SUPPORT_FAILURE",
            "licensed": 0,
            "mode_licensed": 0,
            "support_failure": 1,
            "raw_conditional_element_r": raw_conditional_correlation,
            "nuisance_retention": retention,
        }

    bootstrap_relations = []
    operator_errors = []
    directional_correlations = []
    nuisance_global_shifts = []
    nuisance_cell_shifts = []
    for _ in range(spec.bootstrap_draws):
        indices = rng.integers(0, spec.authors, size=spec.authors)
        if refit_bootstrap_residualizer:
            raw_candidate_data = _subset(raw, indices)
            conditioned_candidate_data = _residualize_public_data(
                raw_candidate_data,
                nuisance[indices],
                folds[indices],
            )
        else:
            raw_candidate_data = _subset(raw, indices)
            conditioned_candidate_data = _subset(conditioned, indices)
        candidate = _safe_replicated_object(
            conditioned_candidate_data,
            support=replicated_support,
        )
        if candidate is None:
            continue
        bootstrap_relations.append(candidate["relation"])
        operator_errors.append(
            float(
                np.linalg.norm(
                    candidate["operator"] - point["operator"],
                    ord=2,
                )
            )
        )
        directional_correlations.append(
            _matrix_correlation(
                candidate["direction_12"],
                candidate["direction_21"],
            )
        )
        if apply_nuisance_veto:
            raw_candidate = _safe_replicated_object(
                raw_candidate_data,
                support=replicated_support,
            )
            if raw_candidate is not None:
                shift = relation_shift_statistics(
                    raw_candidate["relation"],
                    candidate["relation"],
                    spec=spec,
                )
                nuisance_global_shifts.append(shift["global_shift"])
                nuisance_cell_shifts.append(
                    shift["maximum_cell_shift"]
                )
    if not bootstrap_relations:
        return {
            "status": "BOOTSTRAP_SUPPORT_FAILURE",
            "licensed": 0,
            "mode_licensed": 0,
            "support_failure": 1,
        }
    confidence_cone_worst = float(
        np.quantile(
            [
                _matrix_correlation(matrix, conditional_relation)
                for matrix in bootstrap_relations
            ],
            0.05,
        )
    )
    operator_error = float(np.quantile(operator_errors, 0.95))
    direction_lcb = float(np.quantile(directional_correlations, 0.05))
    nuisance_global_shift_lcb99 = (
        float(np.quantile(nuisance_global_shifts, 0.01))
        if nuisance_global_shifts
        else float("nan")
    )
    nuisance_cell_shift_lcb99 = (
        float(np.quantile(nuisance_cell_shifts, 0.01))
        if nuisance_cell_shifts
        else float("nan")
    )

    permutation_norms = []
    for _ in range(spec.permutations):
        permutation = rng.permutation(spec.authors)
        permuted = {
            **conditioned,
            "mbti_first": conditioned["mbti_first"][permutation],
            "mbti_second": conditioned["mbti_second"][permutation],
        }
        candidate = _safe_replicated_object(
            permuted,
            support=replicated_support,
        )
        if candidate is not None:
            permutation_norms.append(
                float(np.linalg.norm(candidate["operator"], ord=2))
            )
    observed_norm = float(np.linalg.norm(point["operator"], ord=2))
    permutation_array = np.asarray(permutation_norms, dtype=float)
    if len(permutation_array) < max(9, spec.permutations // 2):
        return {
            "status": "PERMUTATION_SUPPORT_FAILURE",
            "licensed": 0,
            "mode_licensed": 0,
            "support_failure": 1,
            "raw_conditional_element_r": raw_conditional_correlation,
            "nuisance_retention": retention,
        }
    permutation_p = float(
        (1 + np.sum(permutation_array >= observed_norm))
        / (1 + len(permutation_array))
    )
    permutation_q99 = float(np.quantile(permutation_array, 0.99))

    if apply_nuisance_veto:
        nuisance_null_statistics = []
        for _ in range(spec.permutations):
            permutation = rng.permutation(spec.authors)
            null_conditioned = _residualize_public_data(
                raw,
                nuisance[permutation],
                folds,
            )
            try:
                null_relation = _replicated_relation_matrix(
                    null_conditioned
                )
            except (ValueError, np.linalg.LinAlgError):
                continue
            nuisance_null_statistics.append(
                relation_shift_statistics(
                    raw_relation,
                    null_relation,
                    spec=spec,
                )["max_statistic"]
            )
        nuisance_null_array = np.asarray(
            nuisance_null_statistics,
            dtype=float,
        )
        if len(nuisance_null_array) < max(9, spec.permutations // 2):
            return {
                "status": "NUISANCE_PERMUTATION_FAILURE",
                "licensed": 0,
                "mode_licensed": 0,
                "support_failure": 1,
                "raw_conditional_element_r": raw_conditional_correlation,
                "nuisance_retention": retention,
            }
        nuisance_permutation_p = float(
            (
                1
                + np.sum(
                    nuisance_null_array >= point_shift["max_statistic"]
                )
            )
            / (1 + len(nuisance_null_array))
        )
        nuisance_permutation_q99 = float(
            np.quantile(nuisance_null_array, 0.99)
        )
    else:
        nuisance_permutation_p = float("nan")
        nuisance_permutation_q99 = float("nan")

    singular = np.asarray(point["singular_values"], dtype=float)
    second = float(singular[1]) if len(singular) > 1 else 0.0
    signal_supported = bool(
        float(singular[0]) - operator_error > permutation_q99
    )
    gap_supported = bool(
        float(singular[0]) - second > 2.0 * operator_error
    )
    canonical_valid = bool(
        point["maximum_canonical_correlation"] <= 1.05
        and point["big5_condition"] <= 100.0
        and point["mbti_condition"] <= 100.0
    )
    split_predicted_lcb = float(np.quantile(split_predicted, 0.05))
    split_anchor_lcb = float(np.quantile(split_anchor, 0.05))
    split_cross_lcb = float(np.quantile(split_cross, 0.05))

    nuisance_collapse = bool(retention < 0.25)
    nuisance_reversal = bool(
        np.isfinite(raw_conditional_correlation)
        and raw_conditional_correlation < 0.50
    )
    nuisance_material = bool(
        apply_nuisance_veto
        and (
            nuisance_global_shift_lcb99 > spec.material_relation_shift
            or nuisance_cell_shift_lcb99 > spec.material_cell_shift
        )
    )
    nuisance_instability = bool(
        nuisance_material and nuisance_permutation_p <= 0.01
    )
    support = bool(
        permutation_p <= 0.01
        and signal_supported
        and split_predicted_lcb >= 0.80
        and split_anchor_lcb >= 0.80
        and split_cross_lcb >= 0.80
        and confidence_cone_worst >= 0.80
        and direction_lcb >= 0.80
        and canonical_valid
        and not nuisance_collapse
        and not nuisance_reversal
        and not nuisance_instability
    )
    mode_license = bool(support and gap_supported)
    if nuisance_collapse:
        status = "COMMON_NUISANCE_COMPATIBLE"
    elif nuisance_reversal:
        status = "SIMPSON_OR_NUISANCE_REVERSAL"
    elif nuisance_instability:
        status = "NUISANCE_INVARIANCE_VETO"
    elif not canonical_valid:
        status = "WHITENING_SUPPORT_FAILURE"
    elif support and not gap_supported:
        status = "RELATION_MATRIX_STABLE_MODE_UNRESOLVED"
    elif support:
        status = "RELATION_LICENSED"
    else:
        status = "RELATION_UNDERRESOLVED"
    return {
        "status": status,
        "licensed": int(support),
        "mode_licensed": int(mode_license),
        "support_failure": 0,
        "raw_conditional_element_r": raw_conditional_correlation,
        "nuisance_retention": retention,
        "nuisance_global_shift": point_shift["global_shift"],
        "nuisance_cell_shift": point_shift["maximum_cell_shift"],
        "nuisance_global_shift_lcb99": nuisance_global_shift_lcb99,
        "nuisance_cell_shift_lcb99": nuisance_cell_shift_lcb99,
        "nuisance_permutation_p": nuisance_permutation_p,
        "nuisance_permutation_q99": nuisance_permutation_q99,
        "nuisance_instability": int(nuisance_instability),
        "split_predicted_lcb": split_predicted_lcb,
        "split_anchor_lcb": split_anchor_lcb,
        "split_cross_lcb": split_cross_lcb,
        "confidence_cone_worst": confidence_cone_worst,
        "direction_lcb": direction_lcb,
        "operator_error_q95": operator_error,
        "permutation_operator_q99": permutation_q99,
        "permutation_p": permutation_p,
        "top_singular_value": float(singular[0]),
        "second_singular_value": second,
        "eigengap": float(singular[0] - second),
        "signal_supported": int(signal_supported),
        "gap_supported": int(gap_supported),
        "maximum_canonical_correlation": point[
            "maximum_canonical_correlation"
        ],
        "big5_condition": point["big5_condition"],
        "mbti_condition": point["mbti_condition"],
        "big5_support_rank": replicated_support.big5_rank,
        "mbti_support_rank": replicated_support.mbti_rank,
        "big5_support_null_q99": replicated_support.big5_null_q99,
        "mbti_support_null_q99": replicated_support.mbti_null_q99,
        "conditional_relation": conditional_relation,
    }


def audit_relation_truth(
    world: dict[str, Any],
    observable: dict[str, Any],
) -> dict[str, Any]:
    """Open synthetic truth only after the observable license is frozen."""
    truth = world["truth_lockbox"]
    relation = observable.get("conditional_relation")
    oracle = truth["oracle_relation"]
    fidelity = (
        _matrix_correlation(relation, oracle)
        if relation is not None and oracle is not None
        else float("nan")
    )
    predicted_big5 = 0.5 * (
        world["big5_first"] + world["big5_second"]
    )
    predicted_mbti = 0.5 * (
        world["mbti_first"] + world["mbti_second"]
    )
    direct = [
        safe_correlation(
            predicted_big5[:, index],
            world["anchor_big5"][:, index],
        )
        for index in range(predicted_big5.shape[1])
    ] + [
        safe_correlation(
            predicted_mbti[:, index],
            world["anchor_mbti"][:, index],
        )
        for index in range(predicted_mbti.shape[1])
    ]
    return {
        "truth_fidelity": fidelity,
        "truth_fidelity_pass": int(
            np.isfinite(fidelity) and fidelity >= 0.80
        ),
        "mean_individual_correlation": float(np.nanmean(direct)),
        "oracle_relation_norm": (
            float(np.linalg.norm(oracle))
            if oracle is not None
            else 0.0
        ),
    }


def run_relation_support_repetition(
    repetition: int,
    *,
    seed: int,
    spec: RelationSupportSpec,
    worlds: tuple[str, ...] | None = None,
    apply_nuisance_veto: bool = True,
    refit_bootstrap_residualizer: bool = True,
) -> list[dict[str, Any]]:
    """Run all registered relation worlds and audit post-license truth."""
    rows = []
    if worlds is None:
        worlds = (
            "SHARED_LATENT",
            "NULL_HIGH_DIM_NUISANCE",
            "COMMON_NUISANCE",
            "CORRELATED_REPLICATE_ERROR",
            "LOW_SINGULAR_GAP",
            "SIMPSON_MIXTURE",
            "LOCALIZED_SIMPSON",
            "PRIVATE_AXES",
            "WEAK_RELATION",
            "COLLIDER_OR_DESCENDANT_Z",
        )
    local_seed = int(seed + repetition * 1_000_003)
    for index, name in enumerate(worlds):
        world = simulate_relation_world(
            name,
            seed=local_seed + index * 10_007,
            spec=spec,
        )
        observable = observable_relation_diagnostics(
            world,
            seed=local_seed + index * 10_007 + 503,
            spec=spec,
            apply_nuisance_veto=apply_nuisance_veto,
            refit_bootstrap_residualizer=(
                refit_bootstrap_residualizer
            ),
        )
        frozen = {
            key: value
            for key, value in observable.items()
            if key != "conditional_relation"
        }
        truth = audit_relation_truth(world, observable)
        rows.append({
            "repetition": repetition,
            "seed": local_seed,
            "world": name,
            **frozen,
            **truth,
            "truth_used_by_license": False,
        })
    return rows
