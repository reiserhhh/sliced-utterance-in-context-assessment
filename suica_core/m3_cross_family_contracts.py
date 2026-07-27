"""Public contracts for blinded SUICA M3 cross-family experiments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class M3CrossFamilyObserved:
    """Observed panels available to the estimator.

    The contract deliberately omits generator family, planted parameters,
    hidden states, rotations, knots, neural weights, and process order.
    """

    response_train: np.ndarray
    response_test: np.ndarray
    condition_train: np.ndarray
    condition_test: np.ndarray
    partner_train: np.ndarray
    partner_test: np.ndarray
    partner_id_train: np.ndarray
    partner_id_test: np.ndarray
    design: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class M3CrossFamilyTruth:
    """Oracle objects kept outside the blinded estimator process."""

    world: str
    active_targets: tuple[str, ...]
    author_parameters: dict[str, np.ndarray]
    oracle_profiles: dict[str, np.ndarray]
    exact_alias: bool = False
    validity: dict[str, float | bool | str] = field(default_factory=dict)


@dataclass(frozen=True)
class M3CrossFamilyEstimate:
    """Frozen cross-family summaries and held-out diagnostics."""

    train_features: dict[str, np.ndarray]
    test_features: dict[str, np.ndarray]
    heldout_metrics: dict[str, float]
    heldout_by_author: dict[str, np.ndarray] = field(default_factory=dict)
    refusals: tuple[str, ...] = ()


def validate_cross_family_observed(observed: M3CrossFamilyObserved) -> None:
    """Validate shapes and finite values without inspecting hidden truth."""
    arrays = {
        "response_train": observed.response_train,
        "response_test": observed.response_test,
        "condition_train": observed.condition_train,
        "condition_test": observed.condition_test,
        "partner_train": observed.partner_train,
        "partner_test": observed.partner_test,
    }
    base_shape: tuple[int, int, int] | None = None
    for name, value in arrays.items():
        panel = np.asarray(value, dtype=float)
        if panel.ndim != 4:
            raise ValueError(
                f"{name} must be author x occasion x event x dimension"
            )
        if not np.isfinite(panel).all():
            raise ValueError(f"{name} must contain only finite values")
        if base_shape is None:
            base_shape = panel.shape[:3]
        elif panel.shape[:3] != base_shape:
            raise ValueError("all observed panels must share their first three axes")

    if observed.response_train.shape != observed.response_test.shape:
        raise ValueError("response train/test shapes must match")
    if observed.condition_train.shape != observed.condition_test.shape:
        raise ValueError("condition train/test shapes must match")
    if observed.partner_train.shape != observed.partner_test.shape:
        raise ValueError("partner train/test shapes must match")

    for name, value in (
        ("partner_id_train", observed.partner_id_train),
        ("partner_id_test", observed.partner_id_test),
    ):
        identifiers = np.asarray(value)
        if identifiers.shape != base_shape:
            raise ValueError(f"{name} must match author/occasion/event axes")
        if not np.issubdtype(identifiers.dtype, np.integer):
            raise ValueError(f"{name} must be integer-valued")
        if np.min(identifiers) < 0:
            raise ValueError(f"{name} must be non-negative")


def observed_to_payload(observed: M3CrossFamilyObserved) -> dict[str, np.ndarray]:
    """Convert the public contract to an NPZ-safe payload."""
    validate_cross_family_observed(observed)
    import json

    return {
        "response_train": observed.response_train,
        "response_test": observed.response_test,
        "condition_train": observed.condition_train,
        "condition_test": observed.condition_test,
        "partner_train": observed.partner_train,
        "partner_test": observed.partner_test,
        "partner_id_train": observed.partner_id_train,
        "partner_id_test": observed.partner_id_test,
        "design_json": np.asarray(
            json.dumps(observed.design, sort_keys=True),
            dtype=np.str_,
        ),
    }


def observed_from_payload(payload: Any) -> M3CrossFamilyObserved:
    """Restore the public observation contract from an NPZ payload."""
    import json

    observed = M3CrossFamilyObserved(
        response_train=np.asarray(payload["response_train"], dtype=float),
        response_test=np.asarray(payload["response_test"], dtype=float),
        condition_train=np.asarray(payload["condition_train"], dtype=float),
        condition_test=np.asarray(payload["condition_test"], dtype=float),
        partner_train=np.asarray(payload["partner_train"], dtype=float),
        partner_test=np.asarray(payload["partner_test"], dtype=float),
        partner_id_train=np.asarray(payload["partner_id_train"], dtype=int),
        partner_id_test=np.asarray(payload["partner_id_test"], dtype=int),
        design=json.loads(str(payload["design_json"])),
    )
    validate_cross_family_observed(observed)
    return observed
