"""Creation-hazard information diagnostics for M4-C.3.3."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import expit

from .m4_chart_ecology_estimator import (
    _flatten_events,
    _hazard_design,
)
from .m4_fisher_wiener_creation import (
    M4FixedHazardRoute,
    feedback_indices,
)
from .m4_opportunity_contracts import (
    M4OpportunityObserved,
    M4OpportunityPanel,
)


@dataclass(frozen=True)
class M4CreationInformationView:
    """Author-indexed empirical Fisher information summaries."""

    minimum_positive_eigenvalue: np.ndarray
    trace: np.ndarray
    effective_rank: np.ndarray
    condition_number: np.ndarray


@dataclass(frozen=True)
class M4CreationInformationRoute:
    """Train/test creation information summaries."""

    train: M4CreationInformationView
    test: M4CreationInformationView


def fisher_spectrum_from_design(
    design: np.ndarray,
    coefficient: np.ndarray,
    feedback_columns: np.ndarray,
    *,
    tolerance: float = 1e-10,
) -> tuple[float, float, float, float]:
    """Summarize the empirical logistic Fisher matrix on feedback columns."""
    matrix = np.asarray(design, dtype=float)
    beta = np.asarray(coefficient, dtype=float)
    columns = np.asarray(feedback_columns, dtype=int)
    probability = expit(np.clip(matrix @ beta, -20.0, 20.0))
    weight = np.clip(probability * (1.0 - probability), 1e-12, None)
    feedback = matrix[:, columns]
    information = feedback.T @ (weight[:, None] * feedback)
    eigenvalues = np.linalg.eigvalsh(
        0.5 * (information + information.T)
    )
    maximum = max(float(np.max(eigenvalues)), 1e-12)
    positive = eigenvalues[eigenvalues > tolerance * maximum]
    if len(positive) == 0:
        return 0.0, float(np.sum(eigenvalues)), 0.0, float("inf")
    total = float(np.sum(np.maximum(eigenvalues, 0.0)))
    squared = float(np.sum(np.maximum(eigenvalues, 0.0) ** 2))
    effective_rank = total * total / max(squared, 1e-12)
    return (
        float(np.min(positive)),
        total,
        effective_rank,
        float(np.max(positive) / np.min(positive)),
    )


def _information_view(
    calibration: M4OpportunityPanel,
    selection: M4OpportunityPanel,
    basis: dict[str, np.ndarray],
    coefficients: np.ndarray,
    names: tuple[str, ...],
    *,
    model: str,
) -> M4CreationInformationView:
    columns = feedback_indices(names)
    rows = []
    for author, coefficient in enumerate(coefficients):
        designs = []
        for panel, role in (
            (calibration, "calibration"),
            (selection, "selection"),
        ):
            values = _flatten_events(panel, author)
            design, _ = _hazard_design(
                values,
                basis[role],
                model=model,
            )
            designs.append(design)
        rows.append(
            fisher_spectrum_from_design(
                np.vstack(designs),
                coefficient,
                columns,
            )
        )
    values = np.asarray(rows, dtype=float)
    return M4CreationInformationView(
        minimum_positive_eigenvalue=values[:, 0],
        trace=values[:, 1],
        effective_rank=values[:, 2],
        condition_number=values[:, 3],
    )


def creation_information_route(
    observed: M4OpportunityObserved,
    basis: dict[str, np.ndarray],
    route: M4FixedHazardRoute,
) -> M4CreationInformationRoute:
    """Compute information from calibration/selection only."""
    return M4CreationInformationRoute(
        train=_information_view(
            observed.train_calibration,
            observed.train_selection,
            basis,
            route.train.coefficient,
            route.train.names,
            model=route.model,
        ),
        test=_information_view(
            observed.test_calibration,
            observed.test_selection,
            basis,
            route.test.coefficient,
            route.test.names,
            model=route.model,
        ),
    )
