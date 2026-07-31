"""Physical-edge composition diagnostics for M4-C.3."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any

import numpy as np

from .m4_chart_ecology_estimator import (
    HAZARD_MODELS,
    _choice_delta,
    _choice_logloss,
    _feedback_derivative,
    _fit_choice,
    _fit_hazard_candidate,
    _fit_response,
    _flatten_events,
    _hazard_logloss,
    _hazard_probability,
    _hazard_design,
    _response_loss,
)
from .m4_opportunity_contracts import M4OpportunityObserved, M4OpportunityPanel


EDGE_NAMES = ("creation", "response", "choice")


@dataclass(frozen=True)
class M4PhysicalEdgeView:
    """Author-indexed physical edges from one independent path view."""

    creation: np.ndarray
    response: np.ndarray
    choice: np.ndarray
    jacobian_loop: np.ndarray
    finite_loop: np.ndarray
    selected_model: np.ndarray
    projection_error: np.ndarray
    legacy_loop_difference: np.ndarray


@dataclass(frozen=True)
class M4PhysicalEdgeRoute:
    """Train/test physical-edge estimates under one condition basis."""

    basis_name: str
    train: M4PhysicalEdgeView
    test: M4PhysicalEdgeView


def _fit_author_edges(
    calibration_panel: M4OpportunityPanel,
    selection_panel: M4OpportunityPanel,
    evaluation_panel: M4OpportunityPanel,
    basis: dict[str, np.ndarray],
    author: int,
    *,
    ridge_grid: tuple[float, ...],
    hazard_ridge: float,
    logistic_iterations: int,
    complexity_penalty: float,
) -> tuple[np.ndarray, ...]:
    calibration = _flatten_events(calibration_panel, author)
    selection = _flatten_events(selection_panel, author)
    evaluation = _flatten_events(evaluation_panel, author)
    calibration_pair = (calibration, basis["calibration"])
    selection_pair = (selection, basis["selection"])
    combined = [calibration_pair, selection_pair]

    choice_candidates = [
        _fit_choice([calibration_pair], ridge=ridge)
        for ridge in ridge_grid
    ]
    choice_losses = [
        _choice_logloss(
            coefficient,
            selection,
            basis["selection"],
        )
        for coefficient in choice_candidates
    ]
    minimum_choice_loss = float(np.min(choice_losses))
    choice_ridge = next(
        ridge
        for ridge, loss in zip(ridge_grid, choice_losses, strict=True)
        if loss <= minimum_choice_loss + 1e-10
    )
    choice_coefficient = _fit_choice(combined, ridge=choice_ridge)

    response_candidates = [
        _fit_response([calibration_pair], ridge=ridge)
        for ridge in ridge_grid
    ]
    response_losses = [
        _response_loss(
            coefficient,
            selection,
            basis["selection"],
        )
        for coefficient in response_candidates
    ]
    minimum_response_loss = float(np.min(response_losses))
    response_ridge = next(
        ridge
        for ridge, loss in zip(ridge_grid, response_losses, strict=True)
        if loss <= minimum_response_loss + 1e-10
    )
    response_coefficient = _fit_response(
        combined,
        ridge=response_ridge,
    )

    hazard_scores: dict[str, float] = {}
    for model in HAZARD_MODELS:
        coefficient, _ = _fit_hazard_candidate(
            [calibration_pair],
            model=model,
            ridge=hazard_ridge,
            iterations=logistic_iterations,
        )
        design, _ = _hazard_design(
            selection,
            basis["selection"],
            model=model,
        )
        hazard_scores[model] = (
            _hazard_logloss(
                coefficient,
                design,
                selection["generated_next"],
            )
            + complexity_penalty * design.shape[1]
        )
    minimum_hazard_score = min(hazard_scores.values())
    selected_model = next(
        model
        for model in HAZARD_MODELS
        if hazard_scores[model] <= minimum_hazard_score + 1e-10
    )
    hazard_coefficient, hazard_names = _fit_hazard_candidate(
        combined,
        model=selected_model,
        ridge=hazard_ridge,
        iterations=logistic_iterations,
    )

    evaluation_basis = basis["evaluation"]
    response_dimensions = evaluation["response"].shape[1]
    basis_width = evaluation_basis.shape[1]
    response_choice = response_coefficient[
        response_dimensions : response_dimensions + basis_width
    ].T
    choice_basis = _choice_delta(
        choice_coefficient,
        evaluation_basis,
    )
    basis_reconstruction = np.linalg.pinv(
        evaluation_basis.T,
        rcond=1e-10,
    )
    choice_physical = basis_reconstruction @ choice_basis
    response_physical = response_choice @ evaluation_basis.T
    creation_physical = _feedback_derivative(
        hazard_coefficient,
        hazard_names,
        evaluation_basis,
        response_dimensions,
    )
    jacobian_loop = (
        creation_physical @ response_physical @ choice_physical
    )
    legacy_loop = creation_physical @ response_choice @ choice_basis
    projection_error = (
        np.linalg.norm(
            evaluation_basis.T @ choice_physical - choice_basis
        )
        / max(np.linalg.norm(choice_basis), 1e-12)
    )
    legacy_difference = (
        np.linalg.norm(jacobian_loop - legacy_loop)
        / max(np.linalg.norm(legacy_loop), 1e-12)
    )

    baseline = _hazard_probability(
        hazard_coefficient,
        hazard_names,
        evaluation_basis,
        np.zeros((1, response_dimensions)),
        np.zeros(1),
    )[0]
    finite_loop = np.empty_like(jacobian_loop)
    for category in range(len(evaluation_basis)):
        response_delta = (
            response_physical @ choice_physical[:, category]
        )
        changed = _hazard_probability(
            hazard_coefficient,
            hazard_names,
            evaluation_basis,
            response_delta[None],
            np.zeros(1),
        )[0]
        finite_loop[:, category] = changed - baseline
    return (
        creation_physical,
        response_physical,
        choice_physical,
        jacobian_loop,
        finite_loop,
        np.asarray(selected_model, dtype=object),
        np.asarray(projection_error),
        np.asarray(legacy_difference),
    )


def _fit_view(
    calibration: M4OpportunityPanel,
    selection: M4OpportunityPanel,
    evaluation: M4OpportunityPanel,
    basis: dict[str, np.ndarray],
    **parameters: Any,
) -> M4PhysicalEdgeView:
    rows = [
        _fit_author_edges(
            calibration,
            selection,
            evaluation,
            basis,
            author,
            **parameters,
        )
        for author in range(calibration.menu.shape[0])
    ]
    return M4PhysicalEdgeView(
        creation=np.stack([row[0] for row in rows]),
        response=np.stack([row[1] for row in rows]),
        choice=np.stack([row[2] for row in rows]),
        jacobian_loop=np.stack([row[3] for row in rows]),
        finite_loop=np.stack([row[4] for row in rows]),
        selected_model=np.asarray([row[5].item() for row in rows]),
        projection_error=np.asarray([row[6].item() for row in rows]),
        legacy_loop_difference=np.asarray(
            [row[7].item() for row in rows]
        ),
    )


def fit_m4_physical_edge_route(
    ecology: M4OpportunityObserved,
    basis: dict[str, np.ndarray],
    *,
    basis_name: str,
    ridge_grid: tuple[float, ...] = (0.03, 0.10, 0.30),
    hazard_ridge: float = 0.10,
    logistic_iterations: int = 14,
    complexity_penalty: float = 0.0004,
    **_: Any,
) -> M4PhysicalEdgeRoute:
    """Fit chart-free physical edges under one supplied condition basis."""
    parameters = {
        "ridge_grid": ridge_grid,
        "hazard_ridge": hazard_ridge,
        "logistic_iterations": logistic_iterations,
        "complexity_penalty": complexity_penalty,
    }
    return M4PhysicalEdgeRoute(
        basis_name=basis_name,
        train=_fit_view(
            ecology.train_calibration,
            ecology.train_selection,
            ecology.train_evaluation,
            basis,
            **parameters,
        ),
        test=_fit_view(
            ecology.test_calibration,
            ecology.test_selection,
            ecology.test_evaluation,
            basis,
            **parameters,
        ),
    )


def mixed_physical_loops(
    oracle: M4PhysicalEdgeView,
    discovered: M4PhysicalEdgeView,
) -> dict[str, np.ndarray]:
    """Construct all eight oracle/discovered physical edge products."""
    loops = {}
    for creation_source, response_source, choice_source in product("OD", repeat=3):
        creation = (
            oracle.creation
            if creation_source == "O"
            else discovered.creation
        )
        response = (
            oracle.response
            if response_source == "O"
            else discovered.response
        )
        choice = (
            oracle.choice
            if choice_source == "O"
            else discovered.choice
        )
        loops[
            f"{creation_source}{response_source}{choice_source}"
        ] = np.einsum(
            "acd,adk,akj->acj",
            creation,
            response,
            choice,
            optimize=True,
        )
    return loops


def edge_error_budget(
    oracle: M4PhysicalEdgeView,
    discovered: M4PhysicalEdgeView,
    query_bank: np.ndarray,
) -> dict[str, np.ndarray]:
    """Measure each edge error only along the registered loop path."""
    q = np.asarray(query_bank, dtype=float)
    target = np.einsum(
        "acd,adk,akj,jq->acq",
        oracle.creation,
        oracle.response,
        oracle.choice,
        q,
        optimize=True,
    )
    denominator = np.maximum(
        np.linalg.norm(target, axis=(1, 2)),
        1e-12,
    )

    creation_error = np.einsum(
        "acd,adk,akj,jq->acq",
        discovered.creation - oracle.creation,
        oracle.response,
        oracle.choice,
        q,
        optimize=True,
    )
    response_error = np.einsum(
        "acd,adk,akj,jq->acq",
        oracle.creation,
        discovered.response - oracle.response,
        oracle.choice,
        q,
        optimize=True,
    )
    choice_error = np.einsum(
        "acd,adk,akj,jq->acq",
        oracle.creation,
        oracle.response,
        discovered.choice - oracle.choice,
        q,
        optimize=True,
    )
    total_error = np.einsum(
        "acj,jq->acq",
        discovered.jacobian_loop - oracle.jacobian_loop,
        q,
        optimize=True,
    )
    return {
        "creation": np.linalg.norm(
            creation_error,
            axis=(1, 2),
        )
        / denominator,
        "response": np.linalg.norm(
            response_error,
            axis=(1, 2),
        )
        / denominator,
        "choice": np.linalg.norm(
            choice_error,
            axis=(1, 2),
        )
        / denominator,
        "total": np.linalg.norm(total_error, axis=(1, 2)) / denominator,
    }


def inject_physical_edge_fault(
    oracle: M4PhysicalEdgeView,
    *,
    edge: str,
    strength: float,
    seed: int,
) -> M4PhysicalEdgeView:
    """Inject one controlled physical-space fault for attribution tests."""
    if edge not in EDGE_NAMES:
        raise ValueError(f"unknown edge: {edge}")
    rng = np.random.default_rng(seed)
    values = {
        "creation": oracle.creation.copy(),
        "response": oracle.response.copy(),
        "choice": oracle.choice.copy(),
    }
    target = values[edge]
    noise = rng.normal(size=target.shape)
    target_norm = np.linalg.norm(target, axis=tuple(range(1, target.ndim)))
    noise_norm = np.maximum(
        np.linalg.norm(noise, axis=tuple(range(1, noise.ndim))),
        1e-12,
    )
    scale = strength * target_norm / noise_norm
    target += noise * scale.reshape((-1,) + (1,) * (target.ndim - 1))
    creation = values["creation"]
    response = values["response"]
    choice = values["choice"]
    loop = np.einsum(
        "acd,adk,akj->acj",
        creation,
        response,
        choice,
        optimize=True,
    )
    return M4PhysicalEdgeView(
        creation=creation,
        response=response,
        choice=choice,
        jacobian_loop=loop,
        finite_loop=oracle.finite_loop.copy(),
        selected_model=oracle.selected_model.copy(),
        projection_error=oracle.projection_error.copy(),
        legacy_loop_difference=oracle.legacy_loop_difference.copy(),
    )
