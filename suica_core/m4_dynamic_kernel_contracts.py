"""Contracts for the M4 dynamic gate/order kernel experiment."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class M4DynamicKernelObserved:
    """Observed transition panels available to the kernel estimator."""

    pre_train: np.ndarray
    post_train: np.ndarray
    condition_train: np.ndarray
    history_train: np.ndarray
    regime_train: np.ndarray
    pre_test: np.ndarray
    post_test: np.ndarray
    condition_test: np.ndarray
    history_test: np.ndarray
    regime_test: np.ndarray
    design: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class M4DynamicKernelTruth:
    """Generator-only transition objects."""

    world: str
    expected_order: str
    author_parameters: dict[str, np.ndarray]
    alias: bool = False


@dataclass(frozen=True)
class M4DynamicKernelEstimate:
    """Independent-panel dynamic composition signatures."""

    train_signature: np.ndarray
    test_signature: np.ndarray
    feature_names: tuple[str, ...]
    train_metrics: dict[str, np.ndarray]
    test_metrics: dict[str, np.ndarray]
    train_refusal: np.ndarray
    test_refusal: np.ndarray


def validate_dynamic_kernel_observed(
    observed: M4DynamicKernelObserved,
) -> None:
    """Validate matching author/occasion/event transition panels."""
    for suffix in ("train", "test"):
        pre = np.asarray(getattr(observed, f"pre_{suffix}"), dtype=float)
        post = np.asarray(getattr(observed, f"post_{suffix}"), dtype=float)
        if pre.ndim != 4 or post.shape != pre.shape:
            raise ValueError("pre/post must be matching 4D transition tensors")
        for name in ("condition", "history", "regime"):
            values = np.asarray(getattr(observed, f"{name}_{suffix}"))
            if values.shape != pre.shape[:3]:
                raise ValueError(f"{name}_{suffix} must match event axes")
        if not np.isfinite(pre).all() or not np.isfinite(post).all():
            raise ValueError("transition states must be finite")
    if observed.pre_train.shape != observed.pre_test.shape:
        raise ValueError("train/test transition panels must match")
    if observed.pre_train.shape[0] < 8:
        raise ValueError("dynamic kernel discovery requires at least 8 authors")
    if observed.pre_train.shape[1] < 2:
        raise ValueError("dynamic kernel discovery requires at least 2 occasions")
    if observed.pre_train.shape[2] < 24:
        raise ValueError("dynamic kernel discovery requires at least 24 events")
    for values in (observed.regime_train, observed.regime_test):
        if not np.issubdtype(np.asarray(values).dtype, np.integer):
            raise ValueError("regime arrays must be integer-valued")


def validate_dynamic_kernel_estimate(
    estimate: M4DynamicKernelEstimate,
    *,
    authors: int,
) -> None:
    """Validate independent-panel signature and metric dimensions."""
    if estimate.train_signature.shape != estimate.test_signature.shape:
        raise ValueError("train/test dynamic signatures must match")
    if estimate.train_signature.shape[0] != authors:
        raise ValueError("dynamic signature author count does not match")
    if estimate.train_signature.shape[1] != len(estimate.feature_names):
        raise ValueError("feature names do not match dynamic signature width")
    if not np.isfinite(estimate.train_signature).all():
        raise ValueError("train dynamic signatures must be finite")
    if not np.isfinite(estimate.test_signature).all():
        raise ValueError("test dynamic signatures must be finite")
    for metrics in (estimate.train_metrics, estimate.test_metrics):
        for name, values in metrics.items():
            if np.asarray(values).shape != (authors,):
                raise ValueError(f"dynamic metric {name} must be per-author")
