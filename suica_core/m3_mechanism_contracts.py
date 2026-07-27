"""Public contracts for the SUICA M3 micro-to-meso mechanism atlas."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class M3MechanismObserved:
    """Independent train/test event panels exposed to all estimators."""

    response_train: np.ndarray
    response_test: np.ndarray
    condition_train: np.ndarray
    condition_test: np.ndarray
    partner_train: np.ndarray
    partner_test: np.ndarray


@dataclass(frozen=True)
class M3MechanismTruth:
    """Mechanism-specific oracle geometry hidden from feature extraction."""

    world: str
    expected_family: str | None
    author_parameter: np.ndarray


@dataclass(frozen=True)
class M3MechanismEstimate:
    """Cross-view author summaries for each competing mechanism family."""

    train_features: dict[str, np.ndarray]
    test_features: dict[str, np.ndarray]


def validate_mechanism_observed(observed: M3MechanismObserved) -> None:
    """Reject malformed or non-independent event-panel interfaces."""
    pairs = (
        (observed.response_train, observed.response_test, "response"),
        (observed.condition_train, observed.condition_test, "condition"),
        (observed.partner_train, observed.partner_test, "partner"),
    )
    author_shape: tuple[int, int, int] | None = None
    for train, test, name in pairs:
        train_values = np.asarray(train, dtype=float)
        test_values = np.asarray(test, dtype=float)
        if train_values.ndim != 4 or test_values.ndim != 4:
            raise ValueError(f"{name} panels must be author x occasion x event x dimension")
        if train_values.shape != test_values.shape:
            raise ValueError(f"{name} train/test panel shapes must match")
        if not np.isfinite(train_values).all() or not np.isfinite(test_values).all():
            raise ValueError(f"{name} panels must be finite")
        current = train_values.shape[:3]
        if author_shape is None:
            author_shape = current
        elif current != author_shape:
            raise ValueError("all event panels must share author/occasion/event axes")
