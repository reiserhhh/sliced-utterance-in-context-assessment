"""Replicate-aware regularized CCA charts for SUICA M4-C.3.5-R1."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

import numpy as np
from scipy.spatial.distance import cdist, pdist, squareform
from sklearn.covariance import LedoitWolf

from .m4_condition_manifold_contracts import (
    M4ConditionObserved,
    forbidden_provenance_fields,
    validate_condition_observed,
)


ROLE_TO_PANEL = {
    "calibration": "mechanism_calibration",
    "selection": "mechanism_selection",
    "evaluation": "mechanism_evaluation",
}


@dataclass(frozen=True)
class M4RCCAChartTransform:
    """One response-safe quotient chart identified up to block rotations."""

    author_blocks: int
    support_ranks: tuple[int, int]
    shared_rank_lower: int
    shared_rank_upper: int
    shared_rank: int
    spectral_blocks: tuple[tuple[int, int], ...]
    reliability_values: tuple[np.ndarray, np.ndarray]
    support_selection_values: tuple[np.ndarray, np.ndarray]
    reliability_null_thresholds: tuple[float, float]
    support_rank_boundary_lcb: tuple[float, float]
    support_next_boundary_ucb: tuple[float, float]
    support_stability: tuple[float, float]
    support_stability_lcb: tuple[float, float]
    consensus_concentration: tuple[float, float]
    consensus_minimum_eigenvalue: tuple[float, float]
    consensus_eigengap_lcb: tuple[float, float]
    native_consensus_affinity: tuple[float, float]
    projector_affinities: tuple[float, float]
    canonical_singular_values: np.ndarray
    canonical_singular_lcb: np.ndarray
    canonical_singular_ucb: np.ndarray
    canonical_null_threshold: float
    gamma_fraction: float
    condition_numbers: tuple[float, float]
    negative_spectral_mass: tuple[float, float]
    asymmetric_mass: tuple[float, float]
    heldout_source_cka: float
    null_false_positive_rate: float
    null_trials: int
    source_centers: np.ndarray
    source_maps: tuple[np.ndarray, np.ndarray]
    output_center: np.ndarray
    output_scale: float
    coverage: float
    provenance_hash: str
    refused: bool
    refusal_reasons: tuple[str, ...]

    def transform_source_prototypes(
        self,
        pre_context: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Transform both sources without averaging their common coordinates."""
        values = np.asarray(pre_context, dtype=float)
        if values.ndim == 4:
            values = np.mean(values, axis=1)
        if values.ndim != 3 or values.shape[0] != 2:
            raise ValueError(
                "RCCA chart expects two source/condition/feature prototypes"
            )
        left = (
            (values[0] - self.source_centers[0])
            @ self.source_maps[0]
        )
        right = (
            (values[1] - self.source_centers[1])
            @ self.source_maps[1]
        )
        return left, right

    def transform_prototypes(self, pre_context: np.ndarray) -> np.ndarray:
        """Return the fused quotient coordinate with a constant mass column."""
        left, right = self.transform_source_prototypes(pre_context)
        fused = 0.5 * (left + right)
        scaled = (fused - self.output_center) * self.output_scale
        return np.column_stack([np.ones(len(scaled)), scaled])


@dataclass(frozen=True)
class _SupportEstimate:
    basis: np.ndarray
    native_rank: int
    reliability_values: np.ndarray
    selection_values: np.ndarray
    null_threshold: float
    rank_boundary_lcb: float
    next_boundary_ucb: float
    stability: float
    stability_lcb: float
    consensus_concentration: float
    consensus_minimum_eigenvalue: float
    consensus_eigengap_lcb: float
    native_consensus_affinity: float
    negative_mass: float
    asymmetric_mass: float
    shrinkage: float


def _covariance(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    centered = matrix - np.mean(matrix, axis=0)
    return centered.T @ centered / max(len(centered) - 1, 1)


def _cross_covariance(
    first: np.ndarray,
    second: np.ndarray,
) -> np.ndarray:
    left = np.asarray(first, dtype=float)
    right = np.asarray(second, dtype=float)
    if (
        left.ndim != 2
        or right.ndim != 2
        or left.shape[0] != right.shape[0]
    ):
        raise ValueError(
            "cross-covariance inputs must share the condition axis"
        )
    left = left - np.mean(left, axis=0)
    right = right - np.mean(right, axis=0)
    return left.T @ right / max(len(left) - 1, 1)


def _inverse_sqrt(
    matrix: np.ndarray,
    *,
    tolerance: float = 1e-10,
) -> np.ndarray:
    symmetric = 0.5 * (
        np.asarray(matrix, dtype=float)
        + np.asarray(matrix, dtype=float).T
    )
    values, vectors = np.linalg.eigh(symmetric)
    maximum = max(float(np.max(values)), 1e-12)
    keep = values > tolerance * maximum
    if not np.any(keep):
        raise ValueError("matrix has no positive numerical support")
    return (
        vectors[:, keep]
        @ np.diag(1.0 / np.sqrt(values[keep]))
        @ vectors[:, keep].T
    )


def _author_block_indices(
    authors: int,
    blocks: int,
) -> tuple[np.ndarray, ...]:
    if blocks < 2 or authors < 2 * blocks:
        raise ValueError("each author block requires at least two authors")
    result = tuple(
        np.arange(block, authors, blocks, dtype=int)
        for block in range(blocks)
    )
    if min(len(indices) for indices in result) < 2:
        raise ValueError("fixed author blocks are underpopulated")
    return result


def _block_prototypes(
    pre_context: np.ndarray,
    *,
    blocks: int,
    resamples: tuple[np.ndarray, ...] | None = None,
) -> np.ndarray:
    values = np.asarray(pre_context, dtype=float)
    if values.ndim != 3:
        raise ValueError(
            "one source must be author/condition/feature"
        )
    indices = _author_block_indices(values.shape[0], blocks)
    rows = []
    for block, author_indices in enumerate(indices):
        selected = (
            author_indices
            if resamples is None
            else author_indices[np.asarray(resamples[block], dtype=int)]
        )
        rows.append(np.mean(values[selected], axis=0))
    return np.stack(rows)


def _repeatable_covariance(
    block_values: np.ndarray,
) -> tuple[np.ndarray, float, float]:
    blocks = np.asarray(block_values, dtype=float)
    cross = []
    for first in range(len(blocks)):
        for second in range(first + 1, len(blocks)):
            cross.append(
                _cross_covariance(blocks[first], blocks[second])
            )
    unsymmetrized = np.mean(cross, axis=0)
    asymmetric = unsymmetrized - unsymmetrized.T
    asymmetric_mass = float(
        np.linalg.norm(asymmetric, ord="fro")
        / max(np.linalg.norm(unsymmetrized, ord="fro"), 1e-12)
    )
    symmetric = 0.5 * (unsymmetrized + unsymmetrized.T)
    values, vectors = np.linalg.eigh(symmetric)
    negative = np.minimum(values, 0.0)
    negative_mass = float(
        np.linalg.norm(negative)
        / max(np.linalg.norm(values), 1e-12)
    )
    positive = np.maximum(values, 0.0)
    psd = vectors @ np.diag(positive) @ vectors.T
    return psd, negative_mass, asymmetric_mass


def _shrunk_total_covariance(
    block_values: np.ndarray,
) -> tuple[np.ndarray, float]:
    blocks = np.asarray(block_values, dtype=float)
    centered = blocks - np.mean(blocks, axis=1, keepdims=True)
    rows = centered.reshape(-1, centered.shape[-1])
    estimator = LedoitWolf(assume_centered=True).fit(rows)
    return np.asarray(estimator.covariance_, dtype=float), float(
        estimator.shrinkage_
    )


def _reliability_operator(
    block_values: np.ndarray,
    *,
    fixed_total_inverse_sqrt: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, float, float, float]:
    repeatable, negative_mass, asymmetric_mass = _repeatable_covariance(
        block_values
    )
    if fixed_total_inverse_sqrt is None:
        total, shrinkage = _shrunk_total_covariance(block_values)
        inverse = _inverse_sqrt(total)
    else:
        inverse = np.asarray(fixed_total_inverse_sqrt, dtype=float)
        shrinkage = float("nan")
    operator = inverse @ repeatable @ inverse
    operator = 0.5 * (operator + operator.T)
    return operator, inverse, negative_mass, asymmetric_mass, shrinkage


def _support_null_threshold(
    block_values: np.ndarray,
    inverse: np.ndarray,
    *,
    repetitions: int,
    quantile: float,
    rng: np.random.Generator,
) -> float:
    maxima = []
    for _ in range(repetitions):
        permuted = np.asarray(block_values, dtype=float).copy()
        for block in range(1, len(permuted)):
            permuted[block] = permuted[
                block,
                rng.permutation(permuted.shape[1]),
            ]
        operator, _, _, _, _ = _reliability_operator(
            permuted,
            fixed_total_inverse_sqrt=inverse,
        )
        maxima.append(float(np.max(np.linalg.eigvalsh(operator))))
    return float(np.quantile(maxima, quantile))


def _support_projector(
    operator: np.ndarray,
    inverse: np.ndarray,
    threshold: float,
) -> tuple[np.ndarray, np.ndarray]:
    values, vectors = np.linalg.eigh(0.5 * (operator + operator.T))
    order = np.argsort(values)[::-1]
    values = values[order]
    vectors = vectors[:, order]
    keep = values > threshold
    if not np.any(keep):
        return np.zeros_like(operator), values
    mapped = inverse @ vectors[:, keep]
    orthogonal, _ = np.linalg.qr(mapped)
    return orthogonal @ orthogonal.T, values


def _fit_support(
    source_values: np.ndarray,
    *,
    author_blocks: int,
    permutation_repetitions: int,
    permutation_quantile: float,
    bootstrap_repetitions: int,
    selection_probability: float,
    rng: np.random.Generator,
) -> _SupportEstimate:
    blocks = _block_prototypes(
        source_values,
        blocks=author_blocks,
    )
    operator, inverse, negative, asymmetric, shrinkage = (
        _reliability_operator(blocks)
    )
    threshold = _support_null_threshold(
        blocks,
        inverse,
        repetitions=permutation_repetitions,
        quantile=permutation_quantile,
        rng=rng,
    )
    native_projector, reliability_values = _support_projector(
        operator,
        inverse,
        threshold,
    )
    native_rank = int(np.sum(reliability_values > threshold))
    projectors = []
    bootstrap_values = []
    bootstrap_affinities = []
    block_indices = _author_block_indices(
        source_values.shape[0],
        author_blocks,
    )
    for _ in range(bootstrap_repetitions):
        resamples = tuple(
            rng.integers(0, len(indices), size=len(indices))
            for indices in block_indices
        )
        boot_blocks = _block_prototypes(
            source_values,
            blocks=author_blocks,
            resamples=resamples,
        )
        boot_operator, _, _, _, _ = _reliability_operator(
            boot_blocks,
            fixed_total_inverse_sqrt=inverse,
        )
        values, vectors = np.linalg.eigh(
            0.5 * (boot_operator + boot_operator.T)
        )
        order = np.argsort(values)[::-1]
        values = values[order]
        vectors = vectors[:, order]
        bootstrap_values.append(values)
        if native_rank:
            mapped = inverse @ vectors[:, :native_rank]
            orthogonal, _ = np.linalg.qr(mapped)
            projector = orthogonal @ orthogonal.T
            bootstrap_affinities.append(
                float(
                    np.trace(native_projector @ projector)
                    / native_rank
                )
            )
        else:
            projector = np.zeros_like(operator)
            bootstrap_affinities.append(0.0)
        projectors.append(projector)
    selection_operator = np.mean(projectors, axis=0)
    selection_values, selection_vectors = np.linalg.eigh(
        0.5 * (selection_operator + selection_operator.T)
    )
    order = np.argsort(selection_values)[::-1]
    selection_values = selection_values[order]
    selection_vectors = selection_vectors[:, order]
    basis = selection_vectors[:, :native_rank]
    bootstrap_values_array = np.stack(bootstrap_values)
    affinity_array = np.asarray(bootstrap_affinities, dtype=float)
    rank_boundary_lcb = (
        float(np.quantile(
            bootstrap_values_array[:, native_rank - 1] - threshold,
            0.025,
        ))
        if native_rank
        else float("-inf")
    )
    next_boundary_ucb = (
        float(np.quantile(
            bootstrap_values_array[:, native_rank] - threshold,
            0.975,
        ))
        if native_rank < len(reliability_values)
        else float("-inf")
    )
    stability = float(np.mean(affinity_array))
    stability_lcb = float(np.quantile(affinity_array, 0.025))
    consensus_concentration = (
        float(np.mean(selection_values[:native_rank]))
        if native_rank
        else 0.0
    )
    consensus_minimum = (
        float(selection_values[native_rank - 1])
        if native_rank
        else 0.0
    )
    consensus_gap_samples = []
    if native_rank and native_rank < len(selection_values):
        for _ in range(bootstrap_repetitions):
            indices = rng.integers(
                0,
                len(projectors),
                size=len(projectors),
            )
            current = np.mean(
                [projectors[index] for index in indices],
                axis=0,
            )
            eigenvalues = np.linalg.eigvalsh(
                0.5 * (current + current.T)
            )[::-1]
            consensus_gap_samples.append(
                eigenvalues[native_rank - 1]
                - eigenvalues[native_rank]
            )
    consensus_gap_lcb = (
        float(np.quantile(consensus_gap_samples, 0.025))
        if consensus_gap_samples
        else float("inf")
    )
    native_consensus = (
        float(
            np.trace(
                native_projector
                @ (basis @ basis.T)
            )
            / native_rank
        )
        if native_rank
        else 0.0
    )
    return _SupportEstimate(
        basis=basis,
        native_rank=native_rank,
        reliability_values=reliability_values,
        selection_values=selection_values,
        null_threshold=threshold,
        rank_boundary_lcb=rank_boundary_lcb,
        next_boundary_ucb=next_boundary_ucb,
        stability=stability,
        stability_lcb=stability_lcb,
        consensus_concentration=consensus_concentration,
        consensus_minimum_eigenvalue=consensus_minimum,
        consensus_eigengap_lcb=consensus_gap_lcb,
        native_consensus_affinity=native_consensus,
        negative_mass=negative,
        asymmetric_mass=asymmetric,
        shrinkage=shrinkage,
    )


def _projector_affinity(
    first: np.ndarray,
    second: np.ndarray,
) -> float:
    left = np.asarray(first, dtype=float)
    right = np.asarray(second, dtype=float)
    if left.shape[1] == 0 or right.shape[1] == 0:
        return 0.0
    numerator = float(np.linalg.norm(left.T @ right, ord="fro") ** 2)
    return numerator / max(left.shape[1], right.shape[1])


def _linear_cka(first: np.ndarray, second: np.ndarray) -> float:
    left = np.asarray(first, dtype=float)
    right = np.asarray(second, dtype=float)
    left -= np.mean(left, axis=0)
    right -= np.mean(right, axis=0)
    numerator = float(np.linalg.norm(left.T @ right, ord="fro") ** 2)
    denominator = float(
        np.linalg.norm(left.T @ left, ord="fro")
        * np.linalg.norm(right.T @ right, ord="fro")
    )
    return numerator / max(denominator, 1e-12)


def _regularized_cca(
    first: np.ndarray,
    second: np.ndarray,
    *,
    gamma_fraction: float,
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    tuple[float, float],
]:
    left = np.asarray(first, dtype=float)
    right = np.asarray(second, dtype=float)
    covariance_left = _covariance(left)
    covariance_right = _covariance(right)
    gamma_left = (
        gamma_fraction
        * float(np.trace(covariance_left))
        / max(len(covariance_left), 1)
    )
    gamma_right = (
        gamma_fraction
        * float(np.trace(covariance_right))
        / max(len(covariance_right), 1)
    )
    regularized_left = covariance_left + gamma_left * np.eye(
        len(covariance_left)
    )
    regularized_right = covariance_right + gamma_right * np.eye(
        len(covariance_right)
    )
    inverse_left = _inverse_sqrt(regularized_left)
    inverse_right = _inverse_sqrt(regularized_right)
    cross = _cross_covariance(left, right)
    operator = inverse_left @ cross @ inverse_right
    u, singular, vt = np.linalg.svd(operator, full_matrices=False)
    return (
        operator,
        u,
        singular,
        vt.T,
        np.asarray([gamma_left, gamma_right]),
        (
            float(np.linalg.cond(regularized_left)),
            float(np.linalg.cond(regularized_right)),
        ),
    )


def _heldout_prediction_errors(
    calibration: tuple[np.ndarray, np.ndarray],
    heldout: tuple[np.ndarray, np.ndarray],
    *,
    gamma_fraction: float,
) -> np.ndarray:
    left, right = calibration
    held_left, held_right = heldout
    covariance_left = _covariance(left)
    covariance_right = _covariance(right)
    gamma_left = (
        gamma_fraction
        * float(np.trace(covariance_left))
        / max(len(covariance_left), 1)
    )
    gamma_right = (
        gamma_fraction
        * float(np.trace(covariance_right))
        / max(len(covariance_right), 1)
    )
    cross = _cross_covariance(left, right)
    map_left_right = np.linalg.solve(
        covariance_left + gamma_left * np.eye(len(covariance_left)),
        cross,
    )
    map_right_left = np.linalg.solve(
        covariance_right + gamma_right * np.eye(len(covariance_right)),
        cross.T,
    )
    prediction_right = held_left @ map_left_right
    prediction_left = held_right @ map_right_left
    scale_left = max(float(np.mean(held_left**2)), 1e-12)
    scale_right = max(float(np.mean(held_right**2)), 1e-12)
    return 0.5 * (
        np.mean((prediction_left - held_left) ** 2, axis=1) / scale_left
        + np.mean((prediction_right - held_right) ** 2, axis=1) / scale_right
    )


def _select_gamma(
    calibration: tuple[np.ndarray, np.ndarray],
    heldout: tuple[np.ndarray, np.ndarray],
    *,
    grid: tuple[float, ...],
    maximum_condition_number: float,
) -> float:
    candidates = []
    for fraction in grid:
        _, _, _, _, _, conditions = _regularized_cca(
            calibration[0],
            calibration[1],
            gamma_fraction=fraction,
        )
        if max(conditions) > maximum_condition_number:
            continue
        errors = _heldout_prediction_errors(
            calibration,
            heldout,
            gamma_fraction=fraction,
        )
        candidates.append(
            (
                float(fraction),
                float(np.mean(errors)),
                float(np.std(errors, ddof=1) / np.sqrt(len(errors))),
            )
        )
    if not candidates:
        return float(max(grid))
    minimum = min(value[1] for value in candidates)
    best = next(value for value in candidates if value[1] <= minimum + 1e-12)
    threshold = best[1] + best[2]
    eligible = [value[0] for value in candidates if value[1] <= threshold]
    return float(max(eligible))


def _canonical_null(
    first: np.ndarray,
    second: np.ndarray,
    inverse_left: np.ndarray,
    inverse_right: np.ndarray,
    *,
    repetitions: int,
    quantile: float,
    rng: np.random.Generator,
) -> tuple[float, float]:
    maxima = []
    for _ in range(repetitions):
        cross = _cross_covariance(
            first,
            second[rng.permutation(len(second))],
        )
        singular = np.linalg.svd(
            inverse_left @ cross @ inverse_right,
            compute_uv=False,
        )
        maxima.append(float(singular[0]))
    threshold = float(np.quantile(maxima, quantile))
    return threshold, float(np.mean(np.asarray(maxima) > threshold))


def _canonical_bootstrap(
    first: np.ndarray,
    second: np.ndarray,
    *,
    gamma_fraction: float,
    repetitions: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    singular_rows = []
    operators = []
    for _ in range(repetitions):
        indices = rng.integers(0, len(first), size=len(first))
        operator, _, singular, _, _, _ = _regularized_cca(
            first[indices],
            second[indices],
            gamma_fraction=gamma_fraction,
        )
        singular_rows.append(singular)
        operators.append(operator)
    return np.stack(singular_rows), np.stack(operators)


def _spectral_blocks(
    singular: np.ndarray,
    boot_singular: np.ndarray,
    boot_operators: np.ndarray,
    operator: np.ndarray,
    rank: int,
) -> tuple[tuple[int, int], ...]:
    if rank <= 1:
        return ((0, rank),)
    perturbation = np.quantile(
        [
            np.linalg.norm(current - operator, ord=2)
            for current in boot_operators
        ],
        0.95,
    )
    boundaries = []
    for index in range(rank - 1):
        gap_lcb = float(np.quantile(
            boot_singular[:, index] - boot_singular[:, index + 1],
            0.025,
        ))
        if gap_lcb > 2.0 * perturbation:
            boundaries.append(index + 1)
    starts = [0, *boundaries]
    stops = [*boundaries, rank]
    return tuple(zip(starts, stops, strict=True))


def _coverage(
    calibration: np.ndarray,
    heldout: tuple[np.ndarray, ...],
) -> float:
    reference = np.asarray(calibration, dtype=float)
    distances = squareform(pdist(reference))
    np.fill_diagonal(distances, np.inf)
    neighbors = min(3, len(reference) - 1)
    calibration_knn = np.partition(
        distances,
        neighbors - 1,
        axis=1,
    )[:, neighbors - 1]
    threshold = float(np.quantile(calibration_knn, 0.99))
    rates = []
    for panel in heldout:
        current = cdist(np.asarray(panel, dtype=float), reference)
        held_knn = np.partition(
            current,
            min(neighbors - 1, current.shape[1] - 1),
            axis=1,
        )[:, min(neighbors - 1, current.shape[1] - 1)]
        rates.append(float(np.mean(held_knn <= threshold)))
    return float(np.min(rates))


def _digest(
    *,
    parameters: dict[str, Any],
    arrays: tuple[np.ndarray, ...],
) -> str:
    digest = hashlib.sha256()
    digest.update(b"response_safe_replicate_rcca")
    digest.update(
        json.dumps(
            parameters,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    for array in arrays:
        digest.update(np.ascontiguousarray(array).view(np.uint8))
    return digest.hexdigest()


def fit_response_safe_rcca_chart(
    observed: M4ConditionObserved,
    *,
    author_blocks: int = 4,
    support_permutation_repetitions: int = 199,
    support_permutation_quantile: float = 0.99,
    support_bootstrap_repetitions: int = 199,
    support_selection_probability: float = 0.80,
    minimum_support_stability_lcb: float = 0.75,
    minimum_consensus_eigenvalue: float = 0.60,
    minimum_consensus_eigengap_lcb: float = 0.0,
    minimum_native_consensus_affinity: float = 0.80,
    canonical_permutation_repetitions: int = 499,
    canonical_permutation_quantile: float = 0.99,
    canonical_bootstrap_repetitions: int = 199,
    null_trials: int = 25,
    gamma_grid: tuple[float, ...] = (0.0001, 0.001, 0.01, 0.1),
    maximum_condition_number: float = 100.0,
    maximum_negative_mass: float = 0.10,
    maximum_asymmetric_mass: float = 0.30,
    minimum_projector_affinity: float = 0.80,
    minimum_heldout_cka: float = 0.80,
    minimum_coverage: float = 0.80,
    numerical_singular_tolerance: float = 1e-8,
    seed: int = 1618033988,
    shuffle_source_two: bool = False,
) -> M4RCCAChartTransform:
    """Fit a repeatability-filtered RCCA chart without response access."""
    validate_condition_observed(observed)
    if support_permutation_repetitions < 19:
        raise ValueError("at least 19 support permutations are required")
    if canonical_permutation_repetitions < 19:
        raise ValueError("at least 19 canonical permutations are required")
    if min(
        support_bootstrap_repetitions,
        canonical_bootstrap_repetitions,
    ) < 19:
        raise ValueError("at least 19 bootstrap repetitions are required")
    rng = np.random.default_rng(seed)
    calibration_pre = observed.reference_calibration.pre_context
    selection_pre = observed.reference_selection.pre_context
    calibration_support = []
    selection_support = []
    for source in range(2):
        calibration_support.append(
            _fit_support(
                calibration_pre[source],
                author_blocks=author_blocks,
                permutation_repetitions=(
                    support_permutation_repetitions
                ),
                permutation_quantile=support_permutation_quantile,
                bootstrap_repetitions=support_bootstrap_repetitions,
                selection_probability=support_selection_probability,
                rng=np.random.default_rng(
                    int(rng.integers(0, 2**32 - 1))
                ),
            )
        )
        selection_support.append(
            _fit_support(
                selection_pre[source],
                author_blocks=author_blocks,
                permutation_repetitions=(
                    support_permutation_repetitions
                ),
                permutation_quantile=support_permutation_quantile,
                bootstrap_repetitions=support_bootstrap_repetitions,
                selection_probability=support_selection_probability,
                rng=np.random.default_rng(
                    int(rng.integers(0, 2**32 - 1))
                ),
            )
        )
    reasons: list[str] = []
    support_ranks = tuple(
        int(value.basis.shape[1]) for value in calibration_support
    )
    if min(support_ranks) == 0:
        reasons.append("NO_REPRODUCIBLE_SUPPORT")
        fallback = []
        for value in calibration_support:
            if value.basis.shape[1]:
                fallback.append(value)
                continue
            basis = np.eye(calibration_pre.shape[-1])[:, :1]
            fallback.append(
                _SupportEstimate(
                    basis=basis,
                    native_rank=1,
                    reliability_values=value.reliability_values,
                    selection_values=value.selection_values,
                    null_threshold=value.null_threshold,
                    rank_boundary_lcb=float("-inf"),
                    next_boundary_ucb=float("inf"),
                    stability=0.0,
                    stability_lcb=0.0,
                    consensus_concentration=0.0,
                    consensus_minimum_eigenvalue=0.0,
                    consensus_eigengap_lcb=float("-inf"),
                    native_consensus_affinity=0.0,
                    negative_mass=value.negative_mass,
                    asymmetric_mass=value.asymmetric_mass,
                    shrinkage=value.shrinkage,
                )
            )
        calibration_support = fallback
        support_ranks = tuple(
            int(value.basis.shape[1]) for value in calibration_support
        )
    negative_mass = tuple(
        value.negative_mass for value in calibration_support
    )
    asymmetric_mass = tuple(
        value.asymmetric_mass for value in calibration_support
    )
    if (
        max(negative_mass) > maximum_negative_mass
        or max(asymmetric_mass) > maximum_asymmetric_mass
    ):
        reasons.append("REPLICATE_MODEL_MISSPECIFIED")
    support_checks = [
        value.rank_boundary_lcb > 0.0
        and value.next_boundary_ucb < 0.0
        and value.stability >= support_selection_probability
        and value.stability_lcb >= minimum_support_stability_lcb
        and value.consensus_concentration
        >= support_selection_probability
        and value.consensus_minimum_eigenvalue
        >= minimum_consensus_eigenvalue
        and value.consensus_eigengap_lcb
        > minimum_consensus_eigengap_lcb
        and value.native_consensus_affinity
        >= minimum_native_consensus_affinity
        for value in (*calibration_support, *selection_support)
    ]
    if not all(support_checks):
        reasons.append("SUPPORT_CONSENSUS_UNSTABLE")
    affinities = tuple(
        _projector_affinity(
            calibration_support[source].basis,
            selection_support[source].basis,
        )
        for source in range(2)
    )
    if min(affinities) < minimum_projector_affinity:
        reasons.append("HELDOUT_SUPPORT_UNSTABLE")

    centers = np.mean(calibration_pre, axis=(1, 2))
    calibration_mean = np.mean(calibration_pre, axis=1)
    selection_mean = np.mean(selection_pre, axis=1)
    calibration_coordinates = tuple(
        (calibration_mean[source] - centers[source])
        @ calibration_support[source].basis
        for source in range(2)
    )
    selection_coordinates = tuple(
        (selection_mean[source] - centers[source])
        @ calibration_support[source].basis
        for source in range(2)
    )
    gamma_fraction = _select_gamma(
        calibration_coordinates,
        selection_coordinates,
        grid=tuple(float(value) for value in gamma_grid),
        maximum_condition_number=maximum_condition_number,
    )
    canonical_second = calibration_coordinates[1]
    if shuffle_source_two:
        canonical_second = canonical_second[
            rng.permutation(len(canonical_second))
        ]
    (
        operator,
        left_vectors,
        singular,
        right_vectors,
        gamma_values,
        condition_numbers,
    ) = _regularized_cca(
        calibration_coordinates[0],
        canonical_second,
        gamma_fraction=gamma_fraction,
    )
    covariance_left = _covariance(calibration_coordinates[0])
    covariance_right = _covariance(calibration_coordinates[1])
    inverse_left = _inverse_sqrt(
        covariance_left + gamma_values[0] * np.eye(len(covariance_left))
    )
    inverse_right = _inverse_sqrt(
        covariance_right + gamma_values[1] * np.eye(len(covariance_right))
    )
    canonical_threshold, _ = _canonical_null(
        calibration_coordinates[0],
        canonical_second,
        inverse_left,
        inverse_right,
        repetitions=canonical_permutation_repetitions,
        quantile=canonical_permutation_quantile,
        rng=rng,
    )
    boot_singular, boot_operators = _canonical_bootstrap(
        calibration_coordinates[0],
        canonical_second,
        gamma_fraction=gamma_fraction,
        repetitions=canonical_bootstrap_repetitions,
        rng=rng,
    )
    singular_lcb = np.quantile(boot_singular, 0.025, axis=0)
    singular_ucb = np.quantile(boot_singular, 0.975, axis=0)
    rank_lower = int(np.sum(singular_lcb > canonical_threshold))
    rank_upper = int(np.sum(singular_ucb > canonical_threshold))
    if rank_lower == 0:
        reasons.append("NO_SHARED_CROSS_SOURCE_BLOCK")
    if rank_lower != rank_upper:
        reasons.append("RANK_UNDERRESOLVED")
    shared_rank = max(rank_lower, 1)
    shared_rank = min(shared_rank, len(singular))
    blocks = _spectral_blocks(
        singular,
        boot_singular,
        boot_operators,
        operator,
        shared_rank,
    )
    weights = np.zeros(shared_rank)
    for start, stop in blocks:
        weight = max(
            float(np.mean(singular[start:stop])) - canonical_threshold,
            0.0,
        )
        weights[start:stop] = np.sqrt(weight)
    if not np.any(weights > 0.0):
        weights.fill(1.0)
    source_maps = (
        calibration_support[0].basis
        @ inverse_left
        @ left_vectors[:, :shared_rank]
        * weights[None],
        calibration_support[1].basis
        @ inverse_right
        @ right_vectors[:, :shared_rank]
        * weights[None],
    )
    left_held = (
        (selection_mean[0] - centers[0])
        @ source_maps[0]
    )
    right_held = (
        (selection_mean[1] - centers[1])
        @ source_maps[1]
    )
    heldout_cka = _linear_cka(left_held, right_held)
    if heldout_cka < minimum_heldout_cka:
        reasons.append("HELDOUT_CROSS_SOURCE_UNSTABLE")
    fused_calibration = 0.5 * (
        (calibration_mean[0] - centers[0]) @ source_maps[0]
        + (calibration_mean[1] - centers[1]) @ source_maps[1]
    )
    output_center = np.mean(fused_calibration, axis=0)
    centered_fused = fused_calibration - output_center
    trace = float(np.trace(_covariance(centered_fused)))
    output_scale = np.sqrt(shared_rank / max(trace, 1e-12))

    provisional = M4RCCAChartTransform(
        author_blocks=author_blocks,
        support_ranks=support_ranks,
        shared_rank_lower=rank_lower,
        shared_rank_upper=rank_upper,
        shared_rank=shared_rank,
        spectral_blocks=blocks,
        reliability_values=tuple(
            value.reliability_values.copy()
            for value in calibration_support
        ),
        support_selection_values=tuple(
            value.selection_values.copy()
            for value in calibration_support
        ),
        reliability_null_thresholds=tuple(
            value.null_threshold for value in calibration_support
        ),
        support_rank_boundary_lcb=tuple(
            value.rank_boundary_lcb for value in calibration_support
        ),
        support_next_boundary_ucb=tuple(
            value.next_boundary_ucb for value in calibration_support
        ),
        support_stability=tuple(
            value.stability for value in calibration_support
        ),
        support_stability_lcb=tuple(
            value.stability_lcb for value in calibration_support
        ),
        consensus_concentration=tuple(
            value.consensus_concentration
            for value in calibration_support
        ),
        consensus_minimum_eigenvalue=tuple(
            value.consensus_minimum_eigenvalue
            for value in calibration_support
        ),
        consensus_eigengap_lcb=tuple(
            value.consensus_eigengap_lcb
            for value in calibration_support
        ),
        native_consensus_affinity=tuple(
            value.native_consensus_affinity
            for value in calibration_support
        ),
        projector_affinities=affinities,
        canonical_singular_values=singular.copy(),
        canonical_singular_lcb=singular_lcb.copy(),
        canonical_singular_ucb=singular_ucb.copy(),
        canonical_null_threshold=canonical_threshold,
        gamma_fraction=gamma_fraction,
        condition_numbers=condition_numbers,
        negative_spectral_mass=negative_mass,
        asymmetric_mass=asymmetric_mass,
        heldout_source_cka=heldout_cka,
        null_false_positive_rate=0.0,
        null_trials=null_trials,
        source_centers=centers.copy(),
        source_maps=source_maps,
        output_center=output_center,
        output_scale=float(output_scale),
        coverage=0.0,
        provenance_hash="",
        refused=False,
        refusal_reasons=(),
    )
    calibration_basis = provisional.transform_prototypes(
        observed.reference_calibration.pre_context
    )[:, 1:]
    heldout_basis = tuple(
        provisional.transform_prototypes(
            getattr(observed, role).pre_context
        )[:, 1:]
        for role in (
            "reference_selection",
            "mechanism_calibration",
            "mechanism_selection",
            "mechanism_evaluation",
        )
    )
    coverage = _coverage(calibration_basis, heldout_basis)
    if coverage < minimum_coverage:
        reasons.append("SUPPORT_SHIFT")
    forbidden = forbidden_provenance_fields(observed)
    if forbidden:
        reasons.append("FORBIDDEN_PROVENANCE:" + ",".join(forbidden))
    if (
        max(condition_numbers) > maximum_condition_number
        or float(np.max(singular)) > 1.0 + numerical_singular_tolerance
    ):
        reasons.append("NUMERICAL_CONTRACT_VIOLATION")

    null_false = 0
    for _ in range(null_trials):
        cross = _cross_covariance(
            calibration_coordinates[0],
            calibration_coordinates[1][
                rng.permutation(len(calibration_coordinates[1]))
            ],
        )
        null_singular = np.linalg.svd(
            inverse_left @ cross @ inverse_right,
            compute_uv=False,
        )
        null_false += int(
            np.any(null_singular > canonical_threshold)
        )
    null_false_rate = null_false / max(null_trials, 1)
    parameters = {
        "author_blocks": author_blocks,
        "support_permutation_repetitions": (
            support_permutation_repetitions
        ),
        "support_permutation_quantile": support_permutation_quantile,
        "support_bootstrap_repetitions": support_bootstrap_repetitions,
        "support_selection_probability": support_selection_probability,
        "minimum_support_stability_lcb": (
            minimum_support_stability_lcb
        ),
        "minimum_consensus_eigenvalue": minimum_consensus_eigenvalue,
        "minimum_consensus_eigengap_lcb": (
            minimum_consensus_eigengap_lcb
        ),
        "minimum_native_consensus_affinity": (
            minimum_native_consensus_affinity
        ),
        "canonical_permutation_repetitions": (
            canonical_permutation_repetitions
        ),
        "canonical_permutation_quantile": canonical_permutation_quantile,
        "canonical_bootstrap_repetitions": (
            canonical_bootstrap_repetitions
        ),
        "null_trials": null_trials,
        "gamma_grid": tuple(float(value) for value in gamma_grid),
        "gamma_fraction": gamma_fraction,
        "shuffle_source_two": shuffle_source_two,
        "shared_rank": shared_rank,
        "spectral_blocks": blocks,
    }
    provenance_hash = _digest(
        parameters=parameters,
        arrays=(
            calibration_pre,
            selection_pre,
            calibration_support[0].basis,
            calibration_support[1].basis,
            source_maps[0],
            source_maps[1],
            singular,
            output_center,
        ),
    )
    return M4RCCAChartTransform(
        author_blocks=author_blocks,
        support_ranks=support_ranks,
        shared_rank_lower=rank_lower,
        shared_rank_upper=rank_upper,
        shared_rank=shared_rank,
        spectral_blocks=blocks,
        reliability_values=tuple(
            value.reliability_values.copy()
            for value in calibration_support
        ),
        support_selection_values=tuple(
            value.selection_values.copy()
            for value in calibration_support
        ),
        reliability_null_thresholds=tuple(
            value.null_threshold for value in calibration_support
        ),
        support_rank_boundary_lcb=tuple(
            value.rank_boundary_lcb for value in calibration_support
        ),
        support_next_boundary_ucb=tuple(
            value.next_boundary_ucb for value in calibration_support
        ),
        support_stability=tuple(
            value.stability for value in calibration_support
        ),
        support_stability_lcb=tuple(
            value.stability_lcb for value in calibration_support
        ),
        consensus_concentration=tuple(
            value.consensus_concentration
            for value in calibration_support
        ),
        consensus_minimum_eigenvalue=tuple(
            value.consensus_minimum_eigenvalue
            for value in calibration_support
        ),
        consensus_eigengap_lcb=tuple(
            value.consensus_eigengap_lcb
            for value in calibration_support
        ),
        native_consensus_affinity=tuple(
            value.native_consensus_affinity
            for value in calibration_support
        ),
        projector_affinities=affinities,
        canonical_singular_values=singular.copy(),
        canonical_singular_lcb=singular_lcb.copy(),
        canonical_singular_ucb=singular_ucb.copy(),
        canonical_null_threshold=canonical_threshold,
        gamma_fraction=gamma_fraction,
        condition_numbers=condition_numbers,
        negative_spectral_mass=negative_mass,
        asymmetric_mass=asymmetric_mass,
        heldout_source_cka=heldout_cka,
        null_false_positive_rate=float(null_false_rate),
        null_trials=null_trials,
        source_centers=centers.copy(),
        source_maps=source_maps,
        output_center=output_center,
        output_scale=float(output_scale),
        coverage=coverage,
        provenance_hash=provenance_hash,
        refused=bool(reasons),
        refusal_reasons=tuple(dict.fromkeys(reasons)),
    )


def build_response_safe_rcca_basis(
    transform: M4RCCAChartTransform,
    observed: M4ConditionObserved,
) -> dict[str, np.ndarray]:
    """Apply a frozen RCCA quotient chart to all mechanism roles."""
    return {
        role: transform.transform_prototypes(
            getattr(observed, panel_name).pre_context
        )
        for role, panel_name in ROLE_TO_PANEL.items()
    }
