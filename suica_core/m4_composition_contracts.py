"""Public contracts for SUICA M4 mechanism-composition discovery."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class M4CompositionObserved:
    """Independent event panels exposed to the composition estimator."""

    drivers_train: np.ndarray
    drivers_test: np.ndarray
    response_train: np.ndarray
    response_test: np.ndarray
    mechanism_names: tuple[str, ...]
    design: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class M4CompositionTruth:
    """Generator-only mechanism objects used by the discovery audit."""

    world: str
    expected_kind: str
    author_parameters: dict[str, np.ndarray]
    active_hyperedges: tuple[tuple[str, ...], ...] = ()
    signed_hyperedges: dict[tuple[str, ...], int] = field(default_factory=dict)
    target_pair: tuple[str, str] | None = None
    alias: bool = False


@dataclass(frozen=True)
class M4CompositionEstimate:
    """Anonymous composition signatures recovered from two event panels."""

    train_signature: np.ndarray
    test_signature: np.ndarray
    feature_names: tuple[str, ...]
    train_metrics: dict[str, np.ndarray]
    test_metrics: dict[str, np.ndarray]
    train_refusal: np.ndarray
    test_refusal: np.ndarray


def validate_composition_observed(observed: M4CompositionObserved) -> None:
    """Validate the public tensor contract without inspecting generator truth."""
    train = np.asarray(observed.drivers_train, dtype=float)
    test = np.asarray(observed.drivers_test, dtype=float)
    if train.ndim != 4 or test.ndim != 4:
        raise ValueError(
            "drivers must be author x occasion x event x mechanism"
        )
    if train.shape != test.shape:
        raise ValueError("train/test driver panels must have matching shapes")
    if train.shape[-1] != len(observed.mechanism_names):
        raise ValueError("mechanism_names must match the driver dimension")
    if len(set(observed.mechanism_names)) != len(observed.mechanism_names):
        raise ValueError("mechanism_names must be unique")

    response_train = np.asarray(observed.response_train, dtype=float)
    response_test = np.asarray(observed.response_test, dtype=float)
    if response_train.shape != train.shape[:3]:
        raise ValueError("response_train must match driver event axes")
    if response_test.shape != test.shape[:3]:
        raise ValueError("response_test must match driver event axes")
    for name, values in (
        ("drivers_train", train),
        ("drivers_test", test),
        ("response_train", response_train),
        ("response_test", response_test),
    ):
        if not np.isfinite(values).all():
            raise ValueError(f"{name} must contain only finite values")

    authors, occasions, events, mechanisms = train.shape
    if authors < 8:
        raise ValueError("composition discovery requires at least 8 authors")
    if occasions < 2:
        raise ValueError("composition discovery requires at least 2 occasions")
    if events < 16:
        raise ValueError("composition discovery requires at least 16 events")
    if mechanisms < 2:
        raise ValueError("composition discovery requires at least 2 mechanisms")


def validate_composition_estimate(
    estimate: M4CompositionEstimate,
    *,
    authors: int,
) -> None:
    """Validate signature dimensions and per-author metric arrays."""
    train = np.asarray(estimate.train_signature, dtype=float)
    test = np.asarray(estimate.test_signature, dtype=float)
    if train.shape != test.shape:
        raise ValueError("train/test signatures must have matching shapes")
    if train.shape[0] != authors:
        raise ValueError("signature author dimension does not match input")
    if train.shape[1] != len(estimate.feature_names):
        raise ValueError("feature_names must match signature width")
    if not np.isfinite(train).all() or not np.isfinite(test).all():
        raise ValueError("composition signatures must be finite")
    for collection in (estimate.train_metrics, estimate.test_metrics):
        for name, values in collection.items():
            array = np.asarray(values)
            if array.shape != (authors,):
                raise ValueError(f"metric {name} must be one value per author")
    for refusal in (estimate.train_refusal, estimate.test_refusal):
        if np.asarray(refusal, dtype=bool).shape != (authors,):
            raise ValueError("refusal arrays must be one value per author")
