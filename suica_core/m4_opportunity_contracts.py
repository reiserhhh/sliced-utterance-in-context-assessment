"""Contracts for M4-B endogenous opportunity-ecology discovery."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class M4OpportunityPanel:
    """One role-specific panel of observed opportunity paths."""

    external_menu: np.ndarray
    generated_menu: np.ndarray
    menu: np.ndarray
    choice: np.ndarray
    response: np.ndarray
    history: np.ndarray
    duration: np.ndarray
    environment: np.ndarray


@dataclass(frozen=True)
class M4OpportunityObserved:
    """Independent views with calibration, selection, and evaluation roles."""

    train_calibration: M4OpportunityPanel
    train_selection: M4OpportunityPanel
    train_evaluation: M4OpportunityPanel
    test_calibration: M4OpportunityPanel
    test_selection: M4OpportunityPanel
    test_evaluation: M4OpportunityPanel
    design: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class M4OpportunityTruth:
    """Generator-only ecology mechanisms."""

    world: str
    active_mechanisms: tuple[str, ...]
    author_parameters: dict[str, np.ndarray]
    alias: bool = False
    matched_group: str | None = None


@dataclass(frozen=True)
class M4OpportunityEstimate:
    """Independent-view author ecology signatures and diagnostics."""

    train_signature: np.ndarray
    test_signature: np.ndarray
    feature_names: tuple[str, ...]
    train_metrics: dict[str, np.ndarray]
    test_metrics: dict[str, np.ndarray]
    train_selected_model: np.ndarray
    test_selected_model: np.ndarray
    train_refusal: np.ndarray
    test_refusal: np.ndarray


def validate_opportunity_panel(panel: M4OpportunityPanel) -> None:
    """Validate one opportunity path panel."""
    external = np.asarray(panel.external_menu)
    generated = np.asarray(panel.generated_menu)
    menu = np.asarray(panel.menu)
    if external.ndim != 4:
        raise ValueError("menu tensors must have author/occasion/event/category axes")
    if generated.shape != external.shape or menu.shape != external.shape:
        raise ValueError("external, generated, and total menus must match")
    authors, occasions, events, categories = external.shape
    if panel.choice.shape != (authors, occasions, events):
        raise ValueError("choice must match menu event axes")
    if panel.duration.shape != external.shape:
        raise ValueError("duration must match menu axes")
    if panel.environment.ndim != 4:
        raise ValueError("environment must be a 4D event tensor")
    if panel.environment.shape[:3] != (authors, occasions, events):
        raise ValueError("environment event axes must match menus")
    if panel.response.ndim != 4:
        raise ValueError("response must be a 4D path tensor")
    if panel.history.ndim != 4:
        raise ValueError("history must be a 4D path tensor")
    if panel.response.shape[:2] != (authors, occasions):
        raise ValueError("response author/occasion axes must match menus")
    if panel.history.shape[:2] != (authors, occasions):
        raise ValueError("history author/occasion axes must match menus")
    if panel.response.shape[2] != events + 1:
        raise ValueError("response paths must include the terminal state")
    if panel.history.shape[2] != events + 1:
        raise ValueError("history paths must include the terminal state")
    if categories < 2:
        raise ValueError("opportunity ecology requires at least two categories")
    if authors < 6 or occasions < 1 or events < 24:
        raise ValueError("opportunity panel is too small for discovery")
    if not np.array_equal(menu, np.logical_or(external, generated)):
        raise ValueError("total menu must be the union of its two sources")
    if np.any((panel.choice < 0) | (panel.choice > categories)):
        raise ValueError("choice codes must be in 0..K")
    chosen = panel.choice > 0
    if np.any(
        chosen
        & ~np.take_along_axis(
            menu,
            np.maximum(panel.choice - 1, 0)[..., None],
            axis=-1,
        )[..., 0]
    ):
        raise ValueError("a chosen category must be available")
    for values in (
        panel.response,
        panel.history,
        panel.duration,
        panel.environment,
    ):
        if not np.isfinite(np.asarray(values, dtype=float)).all():
            raise ValueError("path values must be finite")


def validate_opportunity_observed(
    observed: M4OpportunityObserved,
) -> None:
    """Validate all role-specific panels and their shared dimensions."""
    names = (
        "train_calibration",
        "train_selection",
        "train_evaluation",
        "test_calibration",
        "test_selection",
        "test_evaluation",
    )
    panels = [getattr(observed, name) for name in names]
    for panel in panels:
        validate_opportunity_panel(panel)
    reference = panels[0].external_menu.shape
    for panel in panels[1:]:
        shape = panel.external_menu.shape
        if shape[0] != reference[0] or shape[2:] != reference[2:]:
            raise ValueError("all panels must share authors, events, and categories")
    if panels[0].response.shape[-1] != panels[-1].response.shape[-1]:
        raise ValueError("response dimensions must match across panels")
    if panels[0].history.shape[-1] != panels[-1].history.shape[-1]:
        raise ValueError("history dimensions must match across panels")


def validate_opportunity_estimate(
    estimate: M4OpportunityEstimate,
    *,
    authors: int,
) -> None:
    """Validate ecology signatures and per-author diagnostics."""
    if estimate.train_signature.shape != estimate.test_signature.shape:
        raise ValueError("independent ecology signatures must match")
    if estimate.train_signature.shape[0] != authors:
        raise ValueError("ecology signature author count does not match")
    if estimate.train_signature.shape[1] != len(estimate.feature_names):
        raise ValueError("feature names do not match ecology signature width")
    if not np.isfinite(estimate.train_signature).all():
        raise ValueError("train ecology signature must be finite")
    if not np.isfinite(estimate.test_signature).all():
        raise ValueError("test ecology signature must be finite")
    for metrics in (estimate.train_metrics, estimate.test_metrics):
        for name, values in metrics.items():
            if np.asarray(values).shape[0] != authors:
                raise ValueError(f"metric {name} must be author-indexed")
