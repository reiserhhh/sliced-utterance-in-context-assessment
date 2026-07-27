"""Data contracts for the SUICA micro-meso-macro (M3) foundation.

The observed packet intentionally contains no planted truth or world label.
The estimator receives only this packet and a design manifest. Synthetic truth
is held by a separate audit path.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class M3DesignManifest:
    """Public design information available to a mesoscopic estimator."""

    condition_features: np.ndarray
    reference_measure: np.ndarray
    fixed_phase_randomized: bool
    reference_version: str


@dataclass(frozen=True)
class M3ObservedPacket:
    """Observable arrays with truth and generator metadata removed."""

    free_conditions_train: np.ndarray
    free_conditions_test: np.ndarray
    fixed_responses_train: np.ndarray
    fixed_responses_test: np.ndarray
    reference_responses: np.ndarray


@dataclass(frozen=True)
class M3TruthPacket:
    """Synthetic truth visible only to the independent audit function."""

    choice_stationary: np.ndarray
    choice_transition: np.ndarray
    author_position: np.ndarray
    response_operator: np.ndarray
    nonlinear_field: np.ndarray
    occasion_state: np.ndarray
    response_field: np.ndarray
    information_choice: np.ndarray
    information_response: np.ndarray
    microscopic_signature: np.ndarray


@dataclass(frozen=True)
class M3EstimatePacket:
    """Mesoscopic estimates and design-derived refusal states."""

    choice_stationary: np.ndarray
    choice_transition: np.ndarray
    author_position: np.ndarray
    response_operator: np.ndarray
    nonlinear_field: np.ndarray
    occasion_state: np.ndarray
    response_field: np.ndarray
    reference_origin: np.ndarray
    support_rank: int
    common_conditions: np.ndarray
    response_status: str
    state_status: str
    heldout_choice_log_skill: float
    heldout_response_r2_linear: float
    heldout_response_r2_full: float


def validate_manifest(manifest: M3DesignManifest) -> None:
    """Validate dimensions and the frozen reference measure."""
    features = np.asarray(manifest.condition_features, dtype=float)
    measure = np.asarray(manifest.reference_measure, dtype=float)
    if features.ndim != 2 or features.shape[0] < 2:
        raise ValueError("condition_features must be a non-trivial matrix")
    if measure.shape != (features.shape[0],):
        raise ValueError("reference_measure has the wrong shape")
    if not np.isfinite(features).all() or not np.isfinite(measure).all():
        raise ValueError("manifest contains non-finite values")
    if np.any(measure <= 0.0) or not np.isclose(measure.sum(), 1.0):
        raise ValueError("reference_measure must be strictly positive and sum to one")
    if not manifest.reference_version:
        raise ValueError("reference_version is required")


def transform_responses(
    packet: M3ObservedPacket,
    *,
    matrix: np.ndarray | None = None,
    shift: np.ndarray | None = None,
) -> M3ObservedPacket:
    """Apply one common affine response-coordinate transform."""
    dimension = int(packet.fixed_responses_train.shape[-1])
    transform = (
        np.eye(dimension)
        if matrix is None
        else np.asarray(matrix, dtype=float)
    )
    offset = (
        np.zeros(dimension)
        if shift is None
        else np.asarray(shift, dtype=float)
    )
    if transform.shape != (dimension, dimension):
        raise ValueError("matrix has the wrong shape")
    if offset.shape != (dimension,):
        raise ValueError("shift has the wrong shape")

    def apply(values: np.ndarray) -> np.ndarray:
        return np.asarray(values, dtype=float) @ transform.T + offset

    return M3ObservedPacket(
        free_conditions_train=packet.free_conditions_train.copy(),
        free_conditions_test=packet.free_conditions_test.copy(),
        fixed_responses_train=apply(packet.fixed_responses_train),
        fixed_responses_test=apply(packet.fixed_responses_test),
        reference_responses=apply(packet.reference_responses),
    )


def coarse_grain_homogeneous_replicates(
    packet: M3ObservedPacket,
    *,
    block_size: int,
) -> M3ObservedPacket:
    """Average replicate blocks without mixing authors, occasions, or conditions."""
    if block_size < 1:
        raise ValueError("block_size must be positive")

    def aggregate(values: np.ndarray) -> np.ndarray:
        array = np.asarray(values, dtype=float)
        repeats = int(array.shape[-2])
        if repeats % block_size:
            raise ValueError("replicate count must be divisible by block_size")
        shape = array.shape[:-2] + (
            repeats // block_size,
            block_size,
            array.shape[-1],
        )
        with np.errstate(invalid="ignore"):
            return np.nanmean(array.reshape(shape), axis=-2)

    return M3ObservedPacket(
        free_conditions_train=packet.free_conditions_train.copy(),
        free_conditions_test=packet.free_conditions_test.copy(),
        fixed_responses_train=aggregate(packet.fixed_responses_train),
        fixed_responses_test=aggregate(packet.fixed_responses_test),
        reference_responses=aggregate(packet.reference_responses),
    )
