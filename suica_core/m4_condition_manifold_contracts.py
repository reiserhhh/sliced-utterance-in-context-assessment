"""Public contracts for M4-C response-safe condition-manifold discovery."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


FORBIDDEN_PRE_RESPONSE_FIELDS = frozenset(
    {
        "author_id",
        "current_choice",
        "current_response",
        "future_response",
        "future_history",
        "generated_next",
        "mechanism_label",
        "synthetic_truth",
        "big5",
        "mbti",
    }
)


@dataclass(frozen=True)
class M4ConditionPanel:
    """One role-specific panel.

    ``pre_context`` is source x author x condition-point x feature. Conditions
    are shared across authors, while each author observes an independent noisy
    pre-response view. ``response`` is intentionally stored separately and is
    unavailable to the chart-fitting functions.
    """

    pre_context: np.ndarray
    response: np.ndarray
    provenance_fields: tuple[str, ...]


@dataclass(frozen=True)
class M4ConditionObserved:
    """Reference and mechanism panels with strict three-way response roles."""

    reference_calibration: M4ConditionPanel
    reference_selection: M4ConditionPanel
    mechanism_calibration: M4ConditionPanel
    mechanism_selection: M4ConditionPanel
    mechanism_evaluation: M4ConditionPanel
    design: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class M4ConditionTruth:
    """Generator-only latent geometry and noiseless response surfaces."""

    world: str
    expected_chart_status: str
    expected_topology: str
    geodesic_distances: dict[str, np.ndarray]
    response_basis: dict[str, np.ndarray]
    noiseless_response: dict[str, np.ndarray]
    latent_coordinates: dict[str, np.ndarray]
    alias: bool = False
    leakage: bool = False


@dataclass(frozen=True)
class M4ConditionChart:
    """Frozen response-safe chart and its panel representations."""

    selected_family: str
    selected_parameters: dict[str, Any]
    panel_features: dict[str, np.ndarray]
    selection_diagnostics: dict[str, float]
    evaluation_diagnostics: dict[str, float]
    author_leakage_auc: float
    refused: bool
    refusal_reasons: tuple[str, ...]


@dataclass(frozen=True)
class M4ConditionEstimate:
    """Frozen chart plus untouched response-mechanism evaluation."""

    chart: M4ConditionChart
    selected_ridge: float
    response_predictions: np.ndarray
    response_baseline: np.ndarray
    response_r2: float
    response_mae: float


def validate_condition_panel(panel: M4ConditionPanel) -> None:
    """Validate one condition panel without interpreting feature semantics."""
    pre = np.asarray(panel.pre_context)
    response = np.asarray(panel.response)
    if pre.ndim != 4:
        raise ValueError(
            "pre_context must have source/author/condition/feature axes"
        )
    if response.ndim != 3:
        raise ValueError("response must have author/condition/feature axes")
    if pre.shape[1:3] != response.shape[:2]:
        raise ValueError(
            "pre-response author/condition axes must match response axes"
        )
    if pre.shape[0] < 2:
        raise ValueError("M4-C requires at least two pre-response sources")
    if pre.shape[1] < 8 or pre.shape[2] < 16 or pre.shape[3] < 2:
        raise ValueError("condition panel is too small for chart discovery")
    if response.shape[-1] < 1:
        raise ValueError("response must contain at least one dimension")
    if not np.isfinite(pre.astype(float)).all():
        raise ValueError("pre_context must be finite")
    if not np.isfinite(response.astype(float)).all():
        raise ValueError("response must be finite")
    if len(panel.provenance_fields) != pre.shape[-1]:
        raise ValueError(
            "one provenance field is required for every pre-response feature"
        )


def validate_condition_observed(observed: M4ConditionObserved) -> None:
    """Validate role separation and common tensor dimensions."""
    panels = (
        observed.reference_calibration,
        observed.reference_selection,
        observed.mechanism_calibration,
        observed.mechanism_selection,
        observed.mechanism_evaluation,
    )
    for panel in panels:
        validate_condition_panel(panel)
    reference = panels[0].pre_context.shape
    response_dimensions = panels[0].response.shape[-1]
    for panel in panels[1:]:
        shape = panel.pre_context.shape
        if shape[0] != reference[0] or shape[-1] != reference[-1]:
            raise ValueError(
                "all panels must share source and pre-feature dimensions"
            )
        if panel.response.shape[-1] != response_dimensions:
            raise ValueError(
                "all panels must share response dimensionality"
            )
    if (
        observed.reference_calibration.pre_context.shape[1]
        != observed.reference_selection.pre_context.shape[1]
    ):
        raise ValueError("reference panels must contain the same authors")
    mechanism_authors = observed.mechanism_calibration.pre_context.shape[1]
    if any(
        panel.pre_context.shape[1] != mechanism_authors
        for panel in (
            observed.mechanism_selection,
            observed.mechanism_evaluation,
        )
    ):
        raise ValueError("mechanism panels must contain the same authors")


def forbidden_provenance_fields(
    observed: M4ConditionObserved,
) -> tuple[str, ...]:
    """Return forbidden fields declared anywhere in the chart inputs."""
    panels = (
        observed.reference_calibration,
        observed.reference_selection,
        observed.mechanism_calibration,
        observed.mechanism_selection,
        observed.mechanism_evaluation,
    )
    found = {
        field
        for panel in panels
        for field in panel.provenance_fields
        if field in FORBIDDEN_PRE_RESPONSE_FIELDS
    }
    return tuple(sorted(found))
