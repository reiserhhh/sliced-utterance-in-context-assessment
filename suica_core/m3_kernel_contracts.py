"""Contracts for the SUICA M3 two-phase microkernel battery."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class M3KernelDesign:
    """Observable protocol metadata, never planted model parameters."""

    condition_coordinates: np.ndarray
    reference_measure: np.ndarray
    train_condition_mask: np.ndarray
    fixed_phase_randomized: bool
    missingness_mechanism: str
    train_reference_version: str
    test_reference_version: str
    train_representation_version: str
    test_representation_version: str
    technical_streams_independent: bool
    coarse_blocks_condition_homogeneous: bool


@dataclass(frozen=True)
class M3KernelObserved:
    """Observed event arrays without hidden states, codes, or truth."""

    choice_train: np.ndarray
    choice_test: np.ndarray
    fixed_train: np.ndarray
    fixed_test: np.ndarray
    reference_train: np.ndarray
    reference_test: np.ndarray


@dataclass(frozen=True)
class M3KernelTruth:
    """Oracle mesoscopic targets derived from the microscopic kernel."""

    choice_stationary: np.ndarray
    choice_transition: np.ndarray
    response_field: np.ndarray
    author_position: np.ndarray
    response_projection: np.ndarray
    nonlinear_field: np.ndarray
    train_state_effect: np.ndarray
    test_state_effect: np.ndarray
    emission_signature: np.ndarray


@dataclass(frozen=True)
class M3KernelEstimate:
    """Out-of-family estimates and explicit refusal decisions."""

    choice_stationary: np.ndarray
    choice_transition: np.ndarray
    response_field: np.ndarray
    author_position: np.ndarray
    response_projection: np.ndarray
    nonlinear_field: np.ndarray
    train_state_effect: np.ndarray
    response_status: str
    state_status: str
    reliability_status: str
    coarse_status: str
    common_conditions: np.ndarray
    support_rank: int
    heldout_occupancy_skill: float
    heldout_transition_skill: float
    shuffled_transition_skill: float
    heldout_personal_transition_skill: float
    heldout_shared_transition_skill: float
    transition_prior_strength: float
    heldout_field_r2: float
    heldout_linear_r2: float
    heldout_nonlinear_increment: float


def validate_kernel_design(design: M3KernelDesign) -> None:
    """Validate public condition coordinates and protocol metadata."""
    coordinates = np.asarray(design.condition_coordinates, dtype=float)
    measure = np.asarray(design.reference_measure, dtype=float)
    mask = np.asarray(design.train_condition_mask, dtype=bool)
    if coordinates.ndim != 2 or len(coordinates) < 6:
        raise ValueError("condition_coordinates must be a non-trivial matrix")
    if measure.shape != (len(coordinates),):
        raise ValueError("reference_measure has the wrong shape")
    if mask.shape != (len(coordinates),) or mask.sum() < 3:
        raise ValueError("train_condition_mask has the wrong shape or support")
    if np.any(measure <= 0.0) or not np.isclose(measure.sum(), 1.0):
        raise ValueError("reference_measure must be positive and sum to one")
    if design.missingness_mechanism not in {"MCAR", "KNOWN", "UNKNOWN"}:
        raise ValueError("unsupported missingness mechanism")
