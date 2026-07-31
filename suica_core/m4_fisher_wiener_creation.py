"""Cross-fitted Fisher-Wiener creation estimation for M4-C.3.2."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .m4_chart_ecology_estimator import (
    HAZARD_MODELS,
    _feedback_derivative,
    _fit_hazard_candidate,
    _flatten_events,
    _hazard_design,
    _hazard_logloss,
)
from .m4_opportunity_contracts import (
    M4OpportunityObserved,
    M4OpportunityPanel,
)


@dataclass(frozen=True)
class M4FixedHazardView:
    """One independent-view fixed-model hazard estimate."""

    coefficient: np.ndarray
    names: tuple[str, ...]
    creation: np.ndarray
    evaluation_loss: np.ndarray


@dataclass(frozen=True)
class M4FixedHazardRoute:
    """Train/test fixed-model hazard estimates."""

    model: str
    train: M4FixedHazardView
    test: M4FixedHazardView


@dataclass(frozen=True)
class M4SelectedHazardView:
    """Evaluation losses from the legacy per-author model selector."""

    creation: np.ndarray
    evaluation_loss: np.ndarray
    selected_model: np.ndarray


@dataclass(frozen=True)
class M4SelectedHazardRoute:
    """Train/test legacy selected-hazard controls."""

    train: M4SelectedHazardView
    test: M4SelectedHazardView


def _subset_panel(
    panel: M4OpportunityPanel,
    occasion_indices: np.ndarray,
) -> M4OpportunityPanel:
    indices = np.asarray(occasion_indices, dtype=int)
    return M4OpportunityPanel(
        external_menu=panel.external_menu[:, indices],
        generated_menu=panel.generated_menu[:, indices],
        menu=panel.menu[:, indices],
        choice=panel.choice[:, indices],
        response=panel.response[:, indices],
        history=panel.history[:, indices],
        duration=panel.duration[:, indices],
        environment=panel.environment[:, indices],
    )


def split_opportunity_occasions(
    observed: M4OpportunityObserved,
) -> tuple[M4OpportunityObserved, M4OpportunityObserved]:
    """Split every role/view deterministically into even and odd occasions."""
    first: dict[str, M4OpportunityPanel] = {}
    second: dict[str, M4OpportunityPanel] = {}
    for view in ("train", "test"):
        for role in ("calibration", "selection", "evaluation"):
            name = f"{view}_{role}"
            panel = getattr(observed, name)
            count = panel.menu.shape[1]
            even = np.arange(0, count, 2, dtype=int)
            odd = np.arange(1, count, 2, dtype=int)
            if len(even) == 0 or len(odd) == 0:
                raise ValueError(
                    f"{name} requires at least two occasions for cross-fit"
                )
            first[name] = _subset_panel(panel, even)
            second[name] = _subset_panel(panel, odd)
    return (
        M4OpportunityObserved(**first, design=dict(observed.design)),
        M4OpportunityObserved(**second, design=dict(observed.design)),
    )


def _fixed_view(
    calibration: M4OpportunityPanel,
    selection: M4OpportunityPanel,
    evaluation: M4OpportunityPanel,
    basis: dict[str, np.ndarray],
    *,
    model: str,
    ridge: float,
    iterations: int,
) -> M4FixedHazardView:
    coefficients = []
    creations = []
    losses = []
    names: tuple[str, ...] | None = None
    for author in range(calibration.menu.shape[0]):
        calibration_rows = _flatten_events(calibration, author)
        selection_rows = _flatten_events(selection, author)
        evaluation_rows = _flatten_events(evaluation, author)
        coefficient, current_names = _fit_hazard_candidate(
            [
                (calibration_rows, basis["calibration"]),
                (selection_rows, basis["selection"]),
            ],
            model=model,
            ridge=ridge,
            iterations=iterations,
        )
        design, _ = _hazard_design(
            evaluation_rows,
            basis["evaluation"],
            model=model,
        )
        coefficients.append(coefficient)
        creations.append(
            _feedback_derivative(
                coefficient,
                current_names,
                basis["evaluation"],
                evaluation.response.shape[-1],
            )
        )
        losses.append(
            _hazard_logloss(
                coefficient,
                design,
                evaluation_rows["generated_next"],
            )
        )
        names = current_names
    return M4FixedHazardView(
        coefficient=np.stack(coefficients),
        names=names or (),
        creation=np.stack(creations),
        evaluation_loss=np.asarray(losses, dtype=float),
    )


def fit_fixed_hazard_route(
    observed: M4OpportunityObserved,
    basis: dict[str, np.ndarray],
    *,
    model: str = "gate",
    ridge: float = 0.005,
    iterations: int = 30,
) -> M4FixedHazardRoute:
    """Fit one common nested hazard family in both independent path views."""
    return M4FixedHazardRoute(
        model=model,
        train=_fixed_view(
            observed.train_calibration,
            observed.train_selection,
            observed.train_evaluation,
            basis,
            model=model,
            ridge=ridge,
            iterations=iterations,
        ),
        test=_fixed_view(
            observed.test_calibration,
            observed.test_selection,
            observed.test_evaluation,
            basis,
            model=model,
            ridge=ridge,
            iterations=iterations,
        ),
    )


def _selected_view(
    calibration: M4OpportunityPanel,
    selection: M4OpportunityPanel,
    evaluation: M4OpportunityPanel,
    basis: dict[str, np.ndarray],
    *,
    ridge: float,
    iterations: int,
    complexity_penalty: float,
) -> M4SelectedHazardView:
    creations = []
    losses = []
    selected_models = []
    for author in range(calibration.menu.shape[0]):
        calibration_rows = _flatten_events(calibration, author)
        selection_rows = _flatten_events(selection, author)
        evaluation_rows = _flatten_events(evaluation, author)
        scores: dict[str, float] = {}
        for model in HAZARD_MODELS:
            coefficient, _ = _fit_hazard_candidate(
                [(calibration_rows, basis["calibration"])],
                model=model,
                ridge=ridge,
                iterations=iterations,
            )
            design, _ = _hazard_design(
                selection_rows,
                basis["selection"],
                model=model,
            )
            scores[model] = (
                _hazard_logloss(
                    coefficient,
                    design,
                    selection_rows["generated_next"],
                )
                + complexity_penalty * design.shape[1]
            )
        minimum = min(scores.values())
        selected = next(
            model
            for model in HAZARD_MODELS
            if scores[model] <= minimum + 1e-10
        )
        coefficient, names = _fit_hazard_candidate(
            [
                (calibration_rows, basis["calibration"]),
                (selection_rows, basis["selection"]),
            ],
            model=selected,
            ridge=ridge,
            iterations=iterations,
        )
        design, _ = _hazard_design(
            evaluation_rows,
            basis["evaluation"],
            model=selected,
        )
        creations.append(
            _feedback_derivative(
                coefficient,
                names,
                basis["evaluation"],
                evaluation.response.shape[-1],
            )
        )
        losses.append(
            _hazard_logloss(
                coefficient,
                design,
                evaluation_rows["generated_next"],
            )
        )
        selected_models.append(selected)
    return M4SelectedHazardView(
        creation=np.stack(creations),
        evaluation_loss=np.asarray(losses, dtype=float),
        selected_model=np.asarray(selected_models, dtype=object),
    )


def fit_selected_hazard_route(
    observed: M4OpportunityObserved,
    basis: dict[str, np.ndarray],
    *,
    ridge: float = 0.005,
    iterations: int = 30,
    complexity_penalty: float = 0.00001,
) -> M4SelectedHazardRoute:
    """Replay the legacy hazard-family selector for loss comparison."""
    parameters = {
        "ridge": ridge,
        "iterations": iterations,
        "complexity_penalty": complexity_penalty,
    }
    return M4SelectedHazardRoute(
        train=_selected_view(
            observed.train_calibration,
            observed.train_selection,
            observed.train_evaluation,
            basis,
            **parameters,
        ),
        test=_selected_view(
            observed.test_calibration,
            observed.test_selection,
            observed.test_evaluation,
            basis,
            **parameters,
        ),
    )


def feedback_indices(names: tuple[str, ...]) -> np.ndarray:
    """Return the fixed feedback block, excluding history-gate interactions."""
    indices = np.asarray(
        [
            index
            for index, name in enumerate(names)
            if name.startswith("feedback_")
        ],
        dtype=int,
    )
    if len(indices) == 0:
        raise ValueError("fixed hazard model has no feedback block")
    return indices


def _positive_part(values: np.ndarray) -> np.ndarray:
    symmetric = 0.5 * (values + values.T)
    eigenvalues, eigenvectors = np.linalg.eigh(symmetric)
    return (
        eigenvectors
        @ np.diag(np.maximum(eigenvalues, 0.0))
        @ eigenvectors.T
    )


def fisher_wiener_feedback(
    first_half: np.ndarray,
    second_half: np.ndarray,
    raw: np.ndarray,
    *,
    epsilon_scale: float = 1e-6,
    second_permutation: np.ndarray | None = None,
) -> np.ndarray:
    """Apply leave-one-author-out stable-subspace Wiener shrinkage."""
    first = np.asarray(first_half, dtype=float)
    second = np.asarray(second_half, dtype=float)
    observed = np.asarray(raw, dtype=float)
    if first.shape != second.shape or first.shape != observed.shape:
        raise ValueError("half and raw feedback matrices must match")
    if second_permutation is not None:
        permutation = np.asarray(second_permutation, dtype=int)
        if not np.array_equal(np.sort(permutation), np.arange(len(second))):
            raise ValueError("second-half permutation must be one-to-one")
        second = second[permutation]
    authors, width = first.shape
    if authors < 6:
        raise ValueError("Fisher-Wiener shrinkage requires six authors")
    output = np.empty_like(observed)
    all_indices = np.arange(authors)
    for author in range(authors):
        keep = all_indices != author
        first_other = first[keep]
        second_other = second[keep]
        average_other = 0.5 * (first_other + second_other)
        center = np.mean(average_other, axis=0)
        first_centered = first_other - np.mean(first_other, axis=0)
        second_centered = second_other - np.mean(second_other, axis=0)
        denominator = max(len(first_other) - 1, 1)
        signal = _positive_part(
            (
                first_centered.T @ second_centered
                + second_centered.T @ first_centered
            )
            / (2.0 * denominator)
        )
        difference = (
            (first_other - second_other)
            - np.mean(first_other - second_other, axis=0)
        )
        noise = (
            difference.T @ difference
        ) / (4.0 * denominator)
        scale = max(
            float(np.trace(signal + noise)) / max(width, 1),
            1e-12,
        )
        regularized = (
            signal + noise + epsilon_scale * scale * np.eye(width)
        )
        wiener = signal @ np.linalg.pinv(regularized, rcond=1e-10)
        output[author] = (
            center + wiener @ (observed[author] - center)
        )
    return output


def apply_feedback_coefficients(
    full: M4FixedHazardView,
    feedback: np.ndarray,
    evaluation: M4OpportunityPanel,
    evaluation_basis: np.ndarray,
) -> M4FixedHazardView:
    """Replace only the fixed-model feedback block and reevaluate it."""
    indices = feedback_indices(full.names)
    values = np.asarray(feedback, dtype=float)
    if values.shape != (len(full.coefficient), len(indices)):
        raise ValueError("replacement feedback block has the wrong shape")
    coefficients = full.coefficient.copy()
    coefficients[:, indices] = values
    creations = []
    losses = []
    model = (
        "gate"
        if any(name.startswith("gate_") for name in full.names)
        else "feedback"
    )
    for author, coefficient in enumerate(coefficients):
        rows = _flatten_events(evaluation, author)
        design, _ = _hazard_design(
            rows,
            evaluation_basis,
            model=model,
        )
        creations.append(
            _feedback_derivative(
                coefficient,
                full.names,
                evaluation_basis,
                evaluation.response.shape[-1],
            )
        )
        losses.append(
            _hazard_logloss(
                coefficient,
                design,
                rows["generated_next"],
            )
        )
    return M4FixedHazardView(
        coefficient=coefficients,
        names=full.names,
        creation=np.stack(creations),
        evaluation_loss=np.asarray(losses, dtype=float),
    )


def build_fisher_wiener_route(
    observed: M4OpportunityObserved,
    basis: dict[str, np.ndarray],
    full: M4FixedHazardRoute,
    first_half: M4FixedHazardRoute,
    second_half: M4FixedHazardRoute,
    *,
    epsilon_scale: float = 1e-6,
    second_permutation: np.ndarray | None = None,
) -> M4FixedHazardRoute:
    """Learn the stable subspace from train halves and apply it to both views."""
    indices = feedback_indices(full.train.names)
    first_feedback = first_half.train.coefficient[:, indices]
    second_feedback = second_half.train.coefficient[:, indices]
    views: dict[str, M4FixedHazardView] = {}
    for view_name in ("train", "test"):
        full_view = getattr(full, view_name)
        raw_feedback = full_view.coefficient[:, indices]
        shrunk = fisher_wiener_feedback(
            first_feedback,
            second_feedback,
            raw_feedback,
            epsilon_scale=epsilon_scale,
            second_permutation=second_permutation,
        )
        views[view_name] = apply_feedback_coefficients(
            full_view,
            shrunk,
            getattr(observed, f"{view_name}_evaluation"),
            basis["evaluation"],
        )
    return M4FixedHazardRoute(
        model=full.model,
        train=views["train"],
        test=views["test"],
    )


def fixed_hazard_parameters(
    route_parameters: dict[str, Any],
) -> dict[str, Any]:
    """Translate the shared route config into fixed-hazard parameters."""
    return {
        "ridge": float(route_parameters["hazard_ridge"]),
        "iterations": int(route_parameters["logistic_iterations"]),
    }
