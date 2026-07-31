"""Response-safe cross-view errors-in-variables condition charts."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

import numpy as np
from scipy.linalg import subspace_angles
from scipy.spatial.distance import cdist, pdist, squareform

from .m4_condition_manifold_contracts import (
    M4ConditionObserved,
    M4ConditionPanel,
    forbidden_provenance_fields,
    validate_condition_observed,
)


ROLE_TO_BASIS = {
    "calibration": "mechanism_calibration",
    "selection": "mechanism_selection",
    "evaluation": "mechanism_evaluation",
}


@dataclass(frozen=True)
class M4EIVChartTransform:
    """Frozen quotient chart fitted from replicated pre-response views."""

    selected_rank: int
    effective_rank: int
    singular_values: np.ndarray
    permutation_threshold: float
    principal_angles_degrees: np.ndarray
    source_centers: np.ndarray
    source_maps: tuple[np.ndarray, np.ndarray]
    output_center: np.ndarray
    output_whitening: np.ndarray
    coverage: float
    provenance_hash: str
    refused: bool
    refusal_reasons: tuple[str, ...]

    def transform_prototypes(self, pre_context: np.ndarray) -> np.ndarray:
        """Transform one source-author-condition-feature panel."""
        values = np.asarray(pre_context, dtype=float)
        if values.ndim == 4:
            values = np.mean(values, axis=1)
        if values.ndim != 3 or values.shape[0] != 2:
            raise ValueError(
                "EIV chart expects two source/condition/feature prototypes"
            )
        left = (
            (values[0] - self.source_centers[0])
            @ self.source_maps[0]
        )
        right = (
            (values[1] - self.source_centers[1])
            @ self.source_maps[1]
        )
        fused = 0.5 * (left + right)
        whitened = (
            (fused - self.output_center)
            @ self.output_whitening
        )
        return np.column_stack([np.ones(len(whitened)), whitened])


@dataclass(frozen=True)
class M4SingleViewPCATransform:
    """Same-rank single-source linear control."""

    rank: int
    center: np.ndarray
    projection: np.ndarray
    output_center: np.ndarray
    output_whitening: np.ndarray
    provenance_hash: str

    def transform_prototypes(self, pre_context: np.ndarray) -> np.ndarray:
        """Transform source zero while ignoring the paired source."""
        values = np.asarray(pre_context, dtype=float)
        if values.ndim == 4:
            values = np.mean(values, axis=1)
        if values.ndim != 3 or values.shape[0] < 1:
            raise ValueError(
                "single-view PCA expects source/condition/feature prototypes"
            )
        raw = (values[0] - self.center) @ self.projection
        whitened = (
            (raw - self.output_center)
            @ self.output_whitening
        )
        return np.column_stack([np.ones(len(whitened)), whitened])


@dataclass(frozen=True)
class _EIVComponents:
    centers: np.ndarray
    source_maps: tuple[np.ndarray, np.ndarray]
    singular_values: np.ndarray


def _cross_covariance(
    first: np.ndarray,
    second: np.ndarray,
) -> np.ndarray:
    left = np.asarray(first, dtype=float)
    right = np.asarray(second, dtype=float)
    if left.shape != right.shape or left.ndim != 2:
        raise ValueError("cross-covariance inputs must be matched matrices")
    left = left - np.mean(left, axis=0)
    right = right - np.mean(right, axis=0)
    return left.T @ right / max(len(left) - 1, 1)


def _positive_inverse_sqrt(
    matrix: np.ndarray,
    *,
    tolerance: float,
) -> np.ndarray:
    symmetric = 0.5 * (matrix + matrix.T)
    values, vectors = np.linalg.eigh(symmetric)
    maximum = max(float(np.max(values)), 1e-12)
    keep = values > tolerance * maximum
    if not np.any(keep):
        return np.zeros_like(symmetric)
    return (
        vectors[:, keep]
        @ np.diag(1.0 / np.sqrt(values[keep]))
        @ vectors[:, keep].T
    )


def _author_half_prototypes(
    pre_context: np.ndarray,
) -> np.ndarray:
    values = np.asarray(pre_context, dtype=float)
    if values.ndim != 4 or values.shape[0] != 2:
        raise ValueError(
            "pre_context must be source/author/condition/feature with two sources"
        )
    even = np.arange(0, values.shape[1], 2, dtype=int)
    odd = np.arange(1, values.shape[1], 2, dtype=int)
    if min(len(even), len(odd)) < 4:
        raise ValueError("EIV chart requires four authors in each fixed half")
    return np.stack(
        [
            np.mean(values[:, even], axis=1),
            np.mean(values[:, odd], axis=1),
        ],
        axis=1,
    )


def _fit_components(
    pre_context: np.ndarray,
    *,
    covariance_tolerance: float,
    source_two_permutation: np.ndarray | None = None,
) -> _EIVComponents:
    halves = _author_half_prototypes(pre_context)
    if source_two_permutation is not None:
        permutation = np.asarray(source_two_permutation, dtype=int)
        points = halves.shape[2]
        if not np.array_equal(np.sort(permutation), np.arange(points)):
            raise ValueError("condition permutation must be one-to-one")
        halves = halves.copy()
        halves[1] = halves[1][:, permutation, :]
    centers = np.mean(halves, axis=(1, 2))
    signal = []
    for source in range(2):
        forward = _cross_covariance(
            halves[source, 0],
            halves[source, 1],
        )
        signal.append(0.5 * (forward + forward.T))
    inverse = [
        _positive_inverse_sqrt(
            current,
            tolerance=covariance_tolerance,
        )
        for current in signal
    ]
    cross = np.zeros(
        (halves.shape[-1], halves.shape[-1]),
        dtype=float,
    )
    for first_half in range(2):
        for second_half in range(2):
            cross += _cross_covariance(
                halves[0, first_half],
                halves[1, second_half],
            )
    cross /= 4.0
    operator = inverse[0] @ cross @ inverse[1]
    left, singular, right_t = np.linalg.svd(
        operator,
        full_matrices=False,
    )
    return _EIVComponents(
        centers=centers,
        source_maps=(
            inverse[0] @ left,
            inverse[1] @ right_t.T,
        ),
        singular_values=singular,
    )


def _largest_principal_angle_degrees(
    first: np.ndarray,
    second: np.ndarray,
) -> float:
    left, _ = np.linalg.qr(np.asarray(first, dtype=float))
    right, _ = np.linalg.qr(np.asarray(second, dtype=float))
    angles = subspace_angles(left, right)
    if len(angles) == 0:
        return 90.0
    return float(np.degrees(np.max(angles)))


def _whitening(
    values: np.ndarray,
    *,
    tolerance: float,
) -> tuple[np.ndarray, np.ndarray, int]:
    matrix = np.asarray(values, dtype=float)
    center = np.mean(matrix, axis=0)
    centered = matrix - center
    covariance = (
        centered.T @ centered / max(len(centered) - 1, 1)
    )
    eigenvalues, eigenvectors = np.linalg.eigh(
        0.5 * (covariance + covariance.T)
    )
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    maximum = max(float(eigenvalues[0]), 1e-12)
    keep = eigenvalues > tolerance * maximum
    if not np.any(keep):
        keep[0] = True
    transform = (
        eigenvectors[:, keep]
        / np.sqrt(np.maximum(eigenvalues[keep], 1e-12))[None]
    )
    return center, transform, int(np.sum(keep))


def _fused_coordinates(
    pre_context: np.ndarray,
    components: _EIVComponents,
    rank: int,
) -> np.ndarray:
    values = np.asarray(pre_context, dtype=float)
    if values.ndim == 4:
        values = np.mean(values, axis=1)
    maps = (
        components.source_maps[0][:, :rank],
        components.source_maps[1][:, :rank],
    )
    left = (values[0] - components.centers[0]) @ maps[0]
    right = (values[1] - components.centers[1]) @ maps[1]
    return 0.5 * (left + right)


def _coverage(
    calibration: np.ndarray,
    panels: tuple[np.ndarray, ...],
) -> float:
    reference = np.asarray(calibration, dtype=float)
    distances = squareform(pdist(reference))
    np.fill_diagonal(distances, np.inf)
    threshold = 2.0 * float(
        np.quantile(np.min(distances, axis=1), 0.95)
    )
    rates = [
        float(np.mean(
            np.min(cdist(np.asarray(panel), reference), axis=1)
            <= threshold
        ))
        for panel in panels
    ]
    return float(np.mean(rates))


def _digest(
    *,
    kind: str,
    parameters: dict[str, Any],
    arrays: tuple[np.ndarray, ...],
) -> str:
    digest = hashlib.sha256()
    digest.update(kind.encode("utf-8"))
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


def fit_response_safe_eiv_chart(
    observed: M4ConditionObserved,
    *,
    permutation_repetitions: int = 199,
    permutation_quantile: float = 0.99,
    permutation_seed: int = 1299709,
    maximum_rank: int = 8,
    covariance_tolerance: float = 1e-7,
    whitening_tolerance: float = 1e-7,
    maximum_principal_angle_degrees: float = 15.0,
    minimum_coverage: float = 0.80,
    shuffle_source_two: bool = False,
) -> M4EIVChartTransform:
    """Fit a truth-blind common condition subspace from replicated views."""
    validate_condition_observed(observed)
    if permutation_repetitions < 19:
        raise ValueError("at least 19 condition permutations are required")
    if not 0.5 < permutation_quantile < 1.0:
        raise ValueError("permutation_quantile must lie between .5 and 1")
    calibration_pre = observed.reference_calibration.pre_context
    selection_pre = observed.reference_selection.pre_context
    rng = np.random.default_rng(permutation_seed)
    fit_permutation = (
        rng.permutation(calibration_pre.shape[2])
        if shuffle_source_two
        else None
    )
    calibration = _fit_components(
        calibration_pre,
        covariance_tolerance=covariance_tolerance,
        source_two_permutation=fit_permutation,
    )
    selection = _fit_components(
        selection_pre,
        covariance_tolerance=covariance_tolerance,
        source_two_permutation=(
            rng.permutation(selection_pre.shape[2])
            if shuffle_source_two
            else None
        ),
    )
    null_maximum = []
    for _ in range(permutation_repetitions):
        permuted = _fit_components(
            calibration_pre,
            covariance_tolerance=covariance_tolerance,
            source_two_permutation=rng.permutation(
                calibration_pre.shape[2]
            ),
        )
        null_maximum.append(float(permuted.singular_values[0]))
    threshold = float(
        np.quantile(null_maximum, permutation_quantile)
    )
    available = min(
        maximum_rank,
        len(calibration.singular_values),
        len(selection.singular_values),
    )
    signal_rank = int(np.sum(
        calibration.singular_values[:available] > threshold
    ))
    selected_rank = 0
    selected_angles = np.asarray([90.0, 90.0])
    for rank in range(signal_rank, 0, -1):
        angles = np.asarray(
            [
                _largest_principal_angle_degrees(
                    calibration.source_maps[source][:, :rank],
                    selection.source_maps[source][:, :rank],
                )
                for source in range(2)
            ]
        )
        if float(np.max(angles)) <= maximum_principal_angle_degrees:
            selected_rank = rank
            selected_angles = angles
            break
    reasons: list[str] = []
    if selected_rank == 0:
        reasons.append("no_stable_cross_view_rank")
        selected_rank = 1
        selected_angles = np.asarray(
            [
                _largest_principal_angle_degrees(
                    calibration.source_maps[source][:, :1],
                    selection.source_maps[source][:, :1],
                )
                for source in range(2)
            ]
        )
    raw_calibration = _fused_coordinates(
        calibration_pre,
        calibration,
        selected_rank,
    )
    output_center, output_whitening, effective_rank = _whitening(
        raw_calibration,
        tolerance=whitening_tolerance,
    )
    source_maps = (
        calibration.source_maps[0][:, :selected_rank],
        calibration.source_maps[1][:, :selected_rank],
    )
    provisional = M4EIVChartTransform(
        selected_rank=selected_rank,
        effective_rank=effective_rank,
        singular_values=calibration.singular_values.copy(),
        permutation_threshold=threshold,
        principal_angles_degrees=selected_angles,
        source_centers=calibration.centers.copy(),
        source_maps=source_maps,
        output_center=output_center,
        output_whitening=output_whitening,
        coverage=0.0,
        provenance_hash="",
        refused=False,
        refusal_reasons=(),
    )
    calibration_basis = provisional.transform_prototypes(
        observed.reference_calibration.pre_context
    )[:, 1:]
    held_panels = tuple(
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
    coverage = _coverage(calibration_basis, held_panels)
    if coverage < minimum_coverage:
        reasons.append("evaluation_support_shift")
    forbidden = forbidden_provenance_fields(observed)
    if forbidden:
        reasons.append("forbidden_provenance:" + ",".join(forbidden))
    if effective_rank != selected_rank:
        reasons.append("fused_rank_collapse")
    parameters = {
        "selected_rank": selected_rank,
        "effective_rank": effective_rank,
        "permutation_repetitions": permutation_repetitions,
        "permutation_quantile": permutation_quantile,
        "permutation_seed": permutation_seed,
        "maximum_rank": maximum_rank,
        "covariance_tolerance": covariance_tolerance,
        "whitening_tolerance": whitening_tolerance,
        "maximum_principal_angle_degrees": (
            maximum_principal_angle_degrees
        ),
        "shuffle_source_two": shuffle_source_two,
    }
    provenance_hash = _digest(
        kind="response_safe_eiv",
        parameters=parameters,
        arrays=(
            calibration_pre,
            selection_pre,
            calibration.singular_values,
            calibration.centers,
            source_maps[0],
            source_maps[1],
            output_center,
            output_whitening,
        ),
    )
    return M4EIVChartTransform(
        selected_rank=selected_rank,
        effective_rank=effective_rank,
        singular_values=calibration.singular_values.copy(),
        permutation_threshold=threshold,
        principal_angles_degrees=selected_angles,
        source_centers=calibration.centers.copy(),
        source_maps=source_maps,
        output_center=output_center,
        output_whitening=output_whitening,
        coverage=coverage,
        provenance_hash=provenance_hash,
        refused=bool(reasons),
        refusal_reasons=tuple(reasons),
    )


def fit_single_view_pca_chart(
    observed: M4ConditionObserved,
    *,
    rank: int,
    whitening_tolerance: float = 1e-7,
) -> M4SingleViewPCATransform:
    """Fit the fixed same-rank source-zero PCA control."""
    validate_condition_observed(observed)
    values = np.mean(
        observed.reference_calibration.pre_context[0],
        axis=0,
    )
    center = np.mean(values, axis=0)
    _, _, right_t = np.linalg.svd(
        values - center,
        full_matrices=False,
    )
    retained = min(max(int(rank), 1), len(right_t))
    projection = right_t[:retained].T
    raw = (values - center) @ projection
    output_center, output_whitening, effective_rank = _whitening(
        raw,
        tolerance=whitening_tolerance,
    )
    provenance_hash = _digest(
        kind="single_view_pca",
        parameters={
            "rank": effective_rank,
            "whitening_tolerance": whitening_tolerance,
        },
        arrays=(
            observed.reference_calibration.pre_context,
            center,
            projection,
            output_center,
            output_whitening,
        ),
    )
    return M4SingleViewPCATransform(
        rank=effective_rank,
        center=center,
        projection=projection,
        output_center=output_center,
        output_whitening=output_whitening,
        provenance_hash=provenance_hash,
    )


def build_response_safe_basis(
    transform: M4EIVChartTransform | M4SingleViewPCATransform,
    observed: M4ConditionObserved,
) -> dict[str, np.ndarray]:
    """Apply one frozen chart to all mechanism condition roles."""
    return {
        role: transform.transform_prototypes(
            getattr(observed, panel_name).pre_context
        )
        for role, panel_name in ROLE_TO_BASIS.items()
    }
