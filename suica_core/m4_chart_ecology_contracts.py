"""Contracts for M4-C.2 chart-covariant opportunity ecology."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .m4_condition_manifold_contracts import (
    M4ConditionChart,
    M4ConditionObserved,
    validate_condition_observed,
)
from .m4_opportunity_contracts import (
    M4OpportunityObserved,
    validate_opportunity_observed,
)


ECOLOGY_ROLES = ("calibration", "selection", "evaluation")


@dataclass(frozen=True)
class M4ChartEcologyObserved:
    """Response-safe condition panels and independent dynamic path views."""

    condition: M4ConditionObserved
    ecology: M4OpportunityObserved
    reference_calibration_author_ids: tuple[int, ...]
    reference_selection_author_ids: tuple[int, ...]
    design: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class M4ChartEcologyTruth:
    """Truth-open synthetic mechanisms and oracle condition basis."""

    world: str
    expected_status: str
    active_mechanisms: tuple[str, ...]
    oracle_basis: dict[str, np.ndarray]
    author_parameters: dict[str, np.ndarray]
    chart_alias: bool = False
    source_alias: bool = False


@dataclass(frozen=True)
class M4ChartEcologyRouteEstimate:
    """One ecology estimate under either oracle or discovered coordinates."""

    basis_name: str
    train_signature: np.ndarray
    test_signature: np.ndarray
    feature_names: tuple[str, ...]
    train_metrics: dict[str, np.ndarray]
    test_metrics: dict[str, np.ndarray]
    train_selected_model: np.ndarray
    test_selected_model: np.ndarray
    train_refusal: np.ndarray
    test_refusal: np.ndarray
    query_masks: np.ndarray


@dataclass(frozen=True)
class M4ChartEcologyEstimate:
    """Frozen response-safe chart and discovered-coordinate ecology route."""

    chart: M4ConditionChart
    transform_hash: str
    transform_rank: int
    discovered: M4ChartEcologyRouteEstimate
    refused: bool
    refusal_reasons: tuple[str, ...]


def validate_chart_ecology_observed(
    observed: M4ChartEcologyObserved,
) -> None:
    """Validate role isolation and chart-to-path condition alignment."""
    validate_condition_observed(observed.condition)
    validate_opportunity_observed(observed.ecology)
    calibration_ids = set(observed.reference_calibration_author_ids)
    selection_ids = set(observed.reference_selection_author_ids)
    if not calibration_ids or not selection_ids:
        raise ValueError("both reference-author roles must be declared")
    if calibration_ids & selection_ids:
        raise ValueError(
            "reference calibration and selection authors must be disjoint"
        )
    if (
        len(calibration_ids)
        != observed.condition.reference_calibration.pre_context.shape[1]
    ):
        raise ValueError("reference-calibration author IDs do not match panel")
    if (
        len(selection_ids)
        != observed.condition.reference_selection.pre_context.shape[1]
    ):
        raise ValueError("reference-selection author IDs do not match panel")
    condition_panels = {
        "calibration": observed.condition.mechanism_calibration,
        "selection": observed.condition.mechanism_selection,
        "evaluation": observed.condition.mechanism_evaluation,
    }
    for role, condition_panel in condition_panels.items():
        categories = condition_panel.pre_context.shape[2]
        for view in ("train", "test"):
            path_panel = getattr(observed.ecology, f"{view}_{role}")
            if path_panel.menu.shape[-1] != categories:
                raise ValueError(
                    f"{view}_{role} menu atoms do not match condition panel"
                )
            if path_panel.menu.shape[0] != condition_panel.response.shape[0]:
                raise ValueError(
                    f"{view}_{role} mechanism authors do not match chart panel"
                )


def validate_chart_ecology_route(
    estimate: M4ChartEcologyRouteEstimate,
    *,
    authors: int,
) -> None:
    """Validate one coordinate route without interpreting its axes."""
    if estimate.train_signature.shape != estimate.test_signature.shape:
        raise ValueError("independent route signatures must match")
    if estimate.train_signature.shape[0] != authors:
        raise ValueError("route author count does not match")
    if estimate.train_signature.shape[1] != len(estimate.feature_names):
        raise ValueError("route feature names do not match signature width")
    if not np.isfinite(estimate.train_signature).all():
        raise ValueError("train route signature must be finite")
    if not np.isfinite(estimate.test_signature).all():
        raise ValueError("test route signature must be finite")
    for metrics in (estimate.train_metrics, estimate.test_metrics):
        for name, values in metrics.items():
            array = np.asarray(values)
            if array.shape[0] != authors:
                raise ValueError(f"metric {name} must be author-indexed")
            if array.dtype.kind in "fc" and not np.isfinite(array).all():
                raise ValueError(f"metric {name} must be finite")
    if estimate.train_refusal.shape != (authors,):
        raise ValueError("train refusal must be author-indexed")
    if estimate.test_refusal.shape != (authors,):
        raise ValueError("test refusal must be author-indexed")
