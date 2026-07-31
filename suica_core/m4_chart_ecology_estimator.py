"""Chart-covariant ecology estimation for M4-C.2."""
from __future__ import annotations

from dataclasses import replace
from typing import Any

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
from scipy.spatial.distance import pdist, squareform

from .m4_chart_ecology_contracts import (
    M4ChartEcologyEstimate,
    M4ChartEcologyObserved,
    M4ChartEcologyRouteEstimate,
    validate_chart_ecology_observed,
    validate_chart_ecology_route,
)
from .m4_condition_manifold_estimator import (
    fit_m4_condition_chart,
    freeze_m4_condition_transform,
)
from .m4_opportunity_contracts import M4OpportunityPanel


HAZARD_MODELS = ("base", "return", "feedback", "gate")


def _flatten_events(
    panel: M4OpportunityPanel,
    author: int,
) -> dict[str, np.ndarray]:
    """Flatten one author while preserving the declared event order."""
    events = panel.menu.shape[2]
    event_slice = slice(0, events - 1)
    next_slice = slice(1, events)
    return {
        "external": panel.external_menu[author, :, event_slice].reshape(
            -1,
            panel.menu.shape[-1],
        ),
        "external_next": panel.external_menu[
            author, :, next_slice
        ].reshape(-1, panel.menu.shape[-1]),
        "generated": panel.generated_menu[
            author, :, event_slice
        ].reshape(-1, panel.menu.shape[-1]),
        "generated_next": panel.generated_menu[
            author, :, next_slice
        ].reshape(-1, panel.menu.shape[-1]),
        "menu": panel.menu[author, :, event_slice].reshape(
            -1,
            panel.menu.shape[-1],
        ),
        "choice": panel.choice[author, :, event_slice].reshape(-1),
        "response": panel.response[author, :, event_slice].reshape(
            -1,
            panel.response.shape[-1],
        ),
        "response_next": panel.response[
            author, :, next_slice
        ].reshape(-1, panel.response.shape[-1]),
        "history": panel.history[author, :, event_slice].reshape(
            -1,
            panel.history.shape[-1],
        ),
        "duration": panel.duration[author, :, event_slice].reshape(
            -1,
            panel.menu.shape[-1],
        ),
    }


def _selected_basis(
    choice: np.ndarray,
    basis: np.ndarray,
) -> np.ndarray:
    output = np.zeros((len(choice), basis.shape[1]))
    active = choice > 0
    output[active] = basis[choice[active] - 1]
    return output


def _choice_probabilities(
    coefficient: np.ndarray,
    basis: np.ndarray,
    menu: np.ndarray,
) -> np.ndarray:
    utility = basis @ coefficient
    logits = np.column_stack(
        [
            np.zeros(len(menu)),
            np.where(menu, utility[None], -1e9),
        ]
    )
    logits -= logits.max(axis=1, keepdims=True)
    probability = np.exp(logits)
    return probability / probability.sum(axis=1, keepdims=True)


def _choice_objective(
    coefficient: np.ndarray,
    datasets: list[tuple[dict[str, np.ndarray], np.ndarray]],
    *,
    ridge: float,
) -> tuple[float, np.ndarray]:
    loss = 0.0
    gradient = np.zeros_like(coefficient)
    for rows, basis in datasets:
        probability = _choice_probabilities(
            coefficient,
            basis,
            rows["menu"],
        )
        loss -= float(np.sum(np.log(np.clip(
            probability[np.arange(len(rows["choice"])), rows["choice"]],
            1e-12,
            1.0,
        ))))
        expected = probability[:, 1:] @ basis
        observed = _selected_basis(rows["choice"], basis)
        gradient += np.sum(expected - observed, axis=0)
    scale = max(
        sum(len(rows["choice"]) for rows, _ in datasets),
        1,
    )
    return (
        loss / scale + 0.5 * ridge * float(coefficient @ coefficient),
        gradient / scale + ridge * coefficient,
    )


def _fit_choice(
    datasets: list[tuple[dict[str, np.ndarray], np.ndarray]],
    *,
    ridge: float,
) -> np.ndarray:
    width = datasets[0][1].shape[1]
    result = minimize(
        lambda value: _choice_objective(
            value,
            datasets,
            ridge=ridge,
        )[0],
        np.zeros(width),
        jac=lambda value: _choice_objective(
            value,
            datasets,
            ridge=ridge,
        )[1],
        method="L-BFGS-B",
        options={"maxiter": 200, "ftol": 1e-14, "gtol": 1e-10},
    )
    return np.asarray(result.x, dtype=float)


def _choice_logloss(
    coefficient: np.ndarray,
    rows: dict[str, np.ndarray],
    basis: np.ndarray,
) -> float:
    probability = _choice_probabilities(
        coefficient,
        basis,
        rows["menu"],
    )
    return -float(np.mean(np.log(np.clip(
        probability[np.arange(len(rows["choice"])), rows["choice"]],
        1e-12,
        1.0,
    ))))


def _choice_null_loss(rows: dict[str, np.ndarray]) -> float:
    options = 1.0 + np.sum(rows["menu"], axis=1)
    return float(np.mean(np.log(options)))


def _fit_response(
    datasets: list[tuple[dict[str, np.ndarray], np.ndarray]],
    *,
    ridge: float,
    include_choice: bool = True,
) -> np.ndarray:
    designs = []
    targets = []
    for rows, basis in datasets:
        values = [rows["response"]]
        if include_choice:
            values.append(_selected_basis(rows["choice"], basis))
        values.extend(
            [rows["history"], np.ones((len(rows["choice"]), 1))]
        )
        designs.append(np.column_stack(values))
        targets.append(rows["response_next"])
    design = np.vstack(designs)
    target = np.vstack(targets)
    penalty = ridge * len(design) * np.eye(design.shape[1])
    penalty[-1, -1] = 0.0
    return np.linalg.solve(
        design.T @ design + penalty,
        design.T @ target,
    )


def _response_prediction(
    coefficient: np.ndarray,
    rows: dict[str, np.ndarray],
    basis: np.ndarray,
    *,
    include_choice: bool = True,
) -> np.ndarray:
    values = [rows["response"]]
    if include_choice:
        values.append(_selected_basis(rows["choice"], basis))
    values.extend([rows["history"], np.ones((len(rows["choice"]), 1))])
    return np.column_stack(values) @ coefficient


def _response_loss(
    coefficient: np.ndarray,
    rows: dict[str, np.ndarray],
    basis: np.ndarray,
    *,
    include_choice: bool = True,
) -> float:
    prediction = _response_prediction(
        coefficient,
        rows,
        basis,
        include_choice=include_choice,
    )
    return float(np.mean((prediction - rows["response_next"]) ** 2))


def _response_metrics(
    coefficient: np.ndarray,
    baseline: np.ndarray,
    rows: dict[str, np.ndarray],
    basis: np.ndarray,
) -> tuple[float, float]:
    prediction = _response_prediction(coefficient, rows, basis)
    baseline_prediction = _response_prediction(
        baseline,
        rows,
        basis,
        include_choice=False,
    )
    target = rows["response_next"]
    mean = np.mean(target, axis=0, keepdims=True)
    denominator = float(np.sum((target - mean) ** 2))
    r2 = (
        1.0 - float(np.sum((target - prediction) ** 2)) / denominator
        if denominator > 1e-12
        else 0.0
    )
    baseline_error = float(np.sum((target - baseline_prediction) ** 2))
    increment = (
        (baseline_error - float(np.sum((target - prediction) ** 2)))
        / baseline_error
        if baseline_error > 1e-12
        else 0.0
    )
    return float(r2), float(increment)


def _hazard_names(model: str, width: int, dimensions: int) -> tuple[str, ...]:
    names = ["intercept"]
    names.extend(f"condition_{index}" for index in range(width))
    if model in {"return", "feedback", "gate"}:
        names.extend(("generated_current", "duration"))
    if model in {"feedback", "gate"}:
        names.extend(
            f"feedback_{condition}_{dimension}"
            for condition in range(width)
            for dimension in range(dimensions)
        )
    if model == "gate":
        names.extend(
            f"gate_{condition}_{dimension}"
            for condition in range(width)
            for dimension in range(dimensions)
        )
    return tuple(names)


def _hazard_design(
    rows: dict[str, np.ndarray],
    basis: np.ndarray,
    *,
    model: str,
    misalign_gate: bool = False,
) -> tuple[np.ndarray, tuple[str, ...]]:
    events = len(rows["choice"])
    categories, width = basis.shape
    values = [
        np.ones((events, categories, 1)),
        np.broadcast_to(
            basis[None],
            (events, categories, width),
        ),
    ]
    if model in {"return", "feedback", "gate"}:
        values.extend(
            [
                rows["generated"][..., None].astype(float),
                np.tanh(rows["duration"] / 4.0)[..., None],
            ]
        )
    if model in {"feedback", "gate"}:
        feedback = np.einsum(
            "kp,nd->nkpd",
            basis,
            rows["response_next"],
        ).reshape(events, categories, -1)
        values.append(feedback)
    if model == "gate":
        gate = (rows["history"][:, 0] > 0.0).astype(float)
        if misalign_gate:
            gate = gate[::-1].copy()
        values.append(feedback * gate[:, None, None])
    design = np.concatenate(values, axis=-1).reshape(
        events * categories,
        -1,
    )
    return design, _hazard_names(
        model,
        width,
        rows["response_next"].shape[1],
    )


def _fit_logistic(
    design: np.ndarray,
    target: np.ndarray,
    *,
    ridge: float,
    iterations: int,
) -> np.ndarray:
    y = np.asarray(target, dtype=float).reshape(-1)
    penalty = ridge * len(y) * np.eye(design.shape[1])
    penalty[0, 0] = 0.0
    coefficient = np.zeros(design.shape[1])
    probability = (np.sum(y) + 0.5) / (len(y) + 1.0)
    coefficient[0] = np.log(probability / (1.0 - probability))
    for _ in range(iterations):
        fitted = expit(np.clip(design @ coefficient, -20.0, 20.0))
        weight = np.clip(fitted * (1.0 - fitted), 1e-4, None)
        adjusted = (
            design @ coefficient + (y - fitted) / weight
        )
        system = design.T @ (weight[:, None] * design) + penalty
        updated = np.linalg.solve(
            system,
            design.T @ (weight * adjusted),
        )
        if np.max(np.abs(updated - coefficient)) < 1e-10:
            coefficient = updated
            break
        coefficient = updated
    return coefficient


def _hazard_logloss(
    coefficient: np.ndarray,
    design: np.ndarray,
    target: np.ndarray,
) -> float:
    probability = expit(np.clip(design @ coefficient, -20.0, 20.0))
    y = np.asarray(target, dtype=float).reshape(-1)
    return -float(np.mean(
        y * np.log(np.clip(probability, 1e-10, 1.0))
        + (1.0 - y)
        * np.log(np.clip(1.0 - probability, 1e-10, 1.0))
    ))


def _fit_hazard_candidate(
    datasets: list[tuple[dict[str, np.ndarray], np.ndarray]],
    *,
    model: str,
    ridge: float,
    iterations: int,
    misalign_gate: bool = False,
) -> tuple[np.ndarray, tuple[str, ...]]:
    designs = []
    targets = []
    names: tuple[str, ...] | None = None
    for rows, basis in datasets:
        design, current_names = _hazard_design(
            rows,
            basis,
            model=model,
            misalign_gate=misalign_gate,
        )
        designs.append(design)
        targets.append(rows["generated_next"].reshape(-1))
        names = current_names
    return (
        _fit_logistic(
            np.vstack(designs),
            np.concatenate(targets),
            ridge=ridge,
            iterations=iterations,
        ),
        names or (),
    )


def _hazard_probability(
    coefficient: np.ndarray,
    names: tuple[str, ...],
    basis: np.ndarray,
    response: np.ndarray,
    history_gate: np.ndarray,
) -> np.ndarray:
    events = len(response)
    categories = len(basis)
    rows = {
        "choice": np.zeros(events, dtype=int),
        "response_next": np.asarray(response, dtype=float),
        "history": np.column_stack(
            [np.asarray(history_gate, dtype=float), np.zeros(events)]
        ),
        "generated": np.zeros((events, categories), dtype=bool),
        "duration": np.zeros((events, categories)),
    }
    model = (
        "gate"
        if any(name.startswith("gate_") for name in names)
        else "feedback"
        if any(name.startswith("feedback_") for name in names)
        else "return"
        if "generated_current" in names
        else "base"
    )
    design, _ = _hazard_design(rows, basis, model=model)
    return expit(np.clip(design @ coefficient, -20.0, 20.0)).reshape(
        events,
        categories,
    )


def _query_masks(categories: int) -> np.ndarray:
    candidates = [
        np.ones(categories, dtype=bool),
        np.arange(categories) % 2 == 0,
        np.arange(categories) % 2 == 1,
        np.arange(categories) < categories // 2,
        np.arange(categories) >= categories // 2,
        np.arange(categories) % 3 == 0,
        np.arange(categories) % 3 == 1,
        np.arange(categories) % 3 == 2,
    ]
    unique = []
    for values in candidates:
        if np.any(values) and not any(
            np.array_equal(values, existing)
            for existing in unique
        ):
            unique.append(values)
    return np.stack(unique)


def _choice_action(
    coefficient: np.ndarray,
    basis: np.ndarray,
    query_masks: np.ndarray,
) -> np.ndarray:
    return _choice_probabilities(coefficient, basis, query_masks)


def _creation_action(
    coefficient: np.ndarray,
    names: tuple[str, ...],
    basis: np.ndarray,
    dimensions: int,
) -> np.ndarray:
    gate_probe = np.ones((1, dimensions))
    probes = np.vstack(
        [
            np.zeros((1, dimensions)),
            np.eye(dimensions),
            -np.eye(dimensions),
            gate_probe,
            gate_probe,
        ]
    )
    gate = np.zeros(len(probes))
    gate[-1] = 1.0
    return _hazard_probability(
        coefficient,
        names,
        basis,
        probes,
        gate,
    )


def _choice_delta(
    coefficient: np.ndarray,
    basis: np.ndarray,
) -> np.ndarray:
    categories = len(basis)
    full = np.ones((1, categories), dtype=bool)
    full_probability = _choice_probabilities(
        coefficient,
        basis,
        full,
    )[0, 1:]
    full_expectation = full_probability @ basis
    output = np.empty((basis.shape[1], categories))
    for category in range(categories):
        reduced = full.copy()
        reduced[0, category] = False
        probability = _choice_probabilities(
            coefficient,
            basis,
            reduced,
        )[0, 1:]
        output[:, category] = full_expectation - probability @ basis
    return output


def _feedback_derivative(
    coefficient: np.ndarray,
    names: tuple[str, ...],
    basis: np.ndarray,
    dimensions: int,
    *,
    epsilon: float = 0.05,
) -> np.ndarray:
    output = np.empty((len(basis), dimensions))
    for dimension in range(dimensions):
        positive = np.zeros((1, dimensions))
        negative = np.zeros((1, dimensions))
        positive[0, dimension] = epsilon
        negative[0, dimension] = -epsilon
        output[:, dimension] = (
            _hazard_probability(
                coefficient,
                names,
                basis,
                positive,
                np.zeros(1),
            )[0]
            - _hazard_probability(
                coefficient,
                names,
                basis,
                negative,
                np.zeros(1),
            )[0]
        ) / (2.0 * epsilon)
    return output


def _recovery_curve(
    transition: np.ndarray,
    response_choice: np.ndarray,
    basis: np.ndarray,
    *,
    horizons: int = 10,
) -> np.ndarray:
    distances = squareform(pdist(basis[:, 1:]))
    pairs = np.dstack(np.unravel_index(
        np.argsort(distances.ravel())[::-1],
        distances.shape,
    ))[0]
    unique = []
    for first, second in pairs:
        if first >= second:
            continue
        unique.append((int(first), int(second)))
        if len(unique) == 4:
            break
    curves = []
    for first, second in unique:
        impulse = response_choice @ (basis[second] - basis[first])
        norm0 = max(float(np.linalg.norm(impulse)), 1e-12)
        current = impulse
        curve = []
        for _ in range(horizons + 1):
            curve.append(float(np.linalg.norm(current)) / norm0)
            current = transition @ current
        curves.append(curve)
    return np.mean(curves, axis=0)


def _return_curve(
    panel: M4OpportunityPanel,
    author: int,
    basis: np.ndarray,
) -> np.ndarray:
    distance = squareform(pdist(basis[:, 1:]))
    positive = distance[distance > 1e-12]
    radii = np.quantile(positive, [0.10, 0.20, 0.30])
    values = []
    for radius in radii:
        lags: list[int] = []
        for occasion in range(panel.menu.shape[1]):
            path = panel.menu[author, occasion]
            for event in range(len(path) - 1):
                active = np.flatnonzero(path[event])
                for category in active:
                    neighborhood = distance[category] <= radius
                    for following in range(event + 1, len(path)):
                        if np.any(path[following] & neighborhood):
                            lags.append(following - event)
                            break
        values.append(
            float(np.mean(lags)) if lags else float(panel.menu.shape[2])
        )
    return np.asarray(values)


def _external_persistence(rows: dict[str, np.ndarray]) -> float:
    values = []
    for category in range(rows["external"].shape[1]):
        current = rows["external"][:, category]
        following = rows["external_next"][:, category]
        if np.sum(current) < 4 or np.sum(~current) < 4:
            continue
        values.append(
            float(np.mean(following[current]) - np.mean(following[~current]))
        )
    return float(np.mean(values)) if values else 0.0


def _source_alias(rows: dict[str, np.ndarray], threshold: float) -> bool:
    match = float(np.mean(rows["external"] == rows["generated"]))
    rate_gap = abs(
        float(np.mean(rows["external"]))
        - float(np.mean(rows["generated"]))
    )
    return bool(match >= threshold and rate_gap <= 1.0 - threshold)


def _one_author(
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
    alias_match_threshold: float,
    query_masks: np.ndarray,
) -> tuple[
    np.ndarray,
    tuple[str, ...],
    dict[str, np.ndarray | float],
    str,
    bool,
]:
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
    response_baseline = _fit_response(
        combined,
        ridge=response_ridge,
        include_choice=False,
    )

    hazard_fits: dict[str, tuple[np.ndarray, tuple[str, ...]]] = {}
    hazard_scores = {}
    for model in HAZARD_MODELS:
        fit = _fit_hazard_candidate(
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
        loss = _hazard_logloss(
            fit[0],
            design,
            selection["generated_next"],
        )
        hazard_fits[model] = fit
        hazard_scores[model] = (
            loss + complexity_penalty * len(fit[1])
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
    evaluation_design, _ = _hazard_design(
        evaluation,
        basis["evaluation"],
        model=selected_model,
    )
    hazard_loss = _hazard_logloss(
        hazard_coefficient,
        evaluation_design,
        evaluation["generated_next"],
    )
    target_rate = float(np.mean(evaluation["generated_next"]))
    null_probability = np.clip(target_rate, 1e-6, 1.0 - 1e-6)
    hazard_null = -float(np.mean(
        evaluation["generated_next"] * np.log(null_probability)
        + (1.0 - evaluation["generated_next"])
        * np.log(1.0 - null_probability)
    ))

    reverse_gate_strength = 0.0
    gate_direction_margin = 0.0
    if selected_model == "gate":
        reverse_coefficient, reverse_names = _fit_hazard_candidate(
            combined,
            model="gate",
            ridge=hazard_ridge,
            iterations=logistic_iterations,
            misalign_gate=True,
        )
        gate_index = [
            index
            for index, name in enumerate(hazard_names)
            if name.startswith("gate_")
        ]
        reverse_index = [
            index
            for index, name in enumerate(reverse_names)
            if name.startswith("gate_")
        ]
        gate_norm = float(np.linalg.norm(hazard_coefficient[gate_index]))
        reverse_gate_strength = float(
            np.linalg.norm(reverse_coefficient[reverse_index])
        )
        gate_direction_margin = (
            (gate_norm - reverse_gate_strength)
            / (gate_norm + reverse_gate_strength + 1e-12)
        )

    eval_basis = basis["evaluation"]
    choice_action = _choice_action(
        choice_coefficient,
        eval_basis,
        query_masks,
    )
    creation_action = _creation_action(
        hazard_coefficient,
        hazard_names,
        eval_basis,
        evaluation["response_next"].shape[1],
    )
    derivative = _feedback_derivative(
        hazard_coefficient,
        hazard_names,
        eval_basis,
        evaluation["response_next"].shape[1],
    )
    response_dimensions = evaluation["response"].shape[1]
    basis_width = eval_basis.shape[1]
    transition = response_coefficient[:response_dimensions].T
    response_choice = response_coefficient[
        response_dimensions : response_dimensions + basis_width
    ].T
    loop_kernel = (
        derivative
        @ response_choice
        @ _choice_delta(choice_coefficient, eval_basis)
    )
    recovery = _recovery_curve(
        transition,
        response_choice,
        eval_basis,
    )
    returns = _return_curve(evaluation_panel, author, eval_basis)
    response_r2, response_increment = _response_metrics(
        response_coefficient,
        response_baseline,
        evaluation,
        eval_basis,
    )
    choice_loss = _choice_logloss(
        choice_coefficient,
        evaluation,
        eval_basis,
    )
    choice_null = _choice_null_loss(evaluation)
    choice_skill = 1.0 - choice_loss / max(choice_null, 1e-12)
    hazard_skill = 1.0 - hazard_loss / max(hazard_null, 1e-12)
    selection_strength = float(
        np.linalg.norm(choice_coefficient[1:])
        / np.sqrt(max(len(choice_coefficient) - 1, 1))
    )
    creation_strength = float(
        np.linalg.norm(derivative) / np.sqrt(derivative.size)
    )
    gate_effect = (
        creation_action[-1] - creation_action[0]
        if selected_model == "gate"
        else np.zeros(len(eval_basis))
    )
    gate_strength = float(
        np.linalg.norm(gate_effect) / np.sqrt(len(gate_effect))
    )
    persistence = _external_persistence(evaluation)
    source_alias = _source_alias(calibration, alias_match_threshold)
    conditional_skill = max(
        choice_skill,
        hazard_skill,
        response_increment,
    )
    metrics: dict[str, np.ndarray | float] = {
        "choice_action": choice_action,
        "creation_action": creation_action,
        "loop_kernel": loop_kernel,
        "return_curve": returns,
        "recovery_curve": recovery,
        "selection_strength": selection_strength,
        "creation_strength": creation_strength,
        "gate_strength": gate_strength,
        "external_persistence": persistence,
        "choice_skill": choice_skill,
        "hazard_skill": hazard_skill,
        "response_r2": response_r2,
        "response_choice_increment": response_increment,
        "conditional_skill": conditional_skill,
        "gate_direction_margin": gate_direction_margin,
        "reverse_gate_strength": reverse_gate_strength,
    }
    signature = np.concatenate(
        [
            choice_action.ravel(),
            creation_action.ravel(),
            loop_kernel.ravel(),
            returns,
            recovery,
            np.asarray(
                [
                    selection_strength,
                    creation_strength,
                    gate_strength,
                    persistence,
                    choice_skill,
                    hazard_skill,
                    response_increment,
                    gate_direction_margin,
                ]
            ),
        ]
    )
    names = tuple(f"action_{index}" for index in range(len(signature)))
    return signature, names, metrics, selected_model, source_alias


def _one_view(
    calibration: M4OpportunityPanel,
    selection: M4OpportunityPanel,
    evaluation: M4OpportunityPanel,
    basis: dict[str, np.ndarray],
    *,
    ridge_grid: tuple[float, ...],
    hazard_ridge: float,
    logistic_iterations: int,
    complexity_penalty: float,
    alias_match_threshold: float,
    query_masks: np.ndarray,
) -> tuple[
    np.ndarray,
    tuple[str, ...],
    dict[str, np.ndarray],
    np.ndarray,
    np.ndarray,
]:
    rows = [
        _one_author(
            calibration,
            selection,
            evaluation,
            basis,
            author,
            ridge_grid=ridge_grid,
            hazard_ridge=hazard_ridge,
            logistic_iterations=logistic_iterations,
            complexity_penalty=complexity_penalty,
            alias_match_threshold=alias_match_threshold,
            query_masks=query_masks,
        )
        for author in range(calibration.menu.shape[0])
    ]
    metric_names = tuple(rows[0][2])
    metrics = {
        name: np.stack(
            [np.atleast_1d(row[2][name]).astype(float) for row in rows]
        ).squeeze(axis=1)
        if np.atleast_1d(rows[0][2][name]).size == 1
        else np.stack(
            [np.asarray(row[2][name], dtype=float) for row in rows]
        )
        for name in metric_names
    }
    return (
        np.stack([row[0] for row in rows]),
        rows[0][1],
        metrics,
        np.asarray([row[3] for row in rows], dtype=object),
        np.asarray([row[4] for row in rows], dtype=bool),
    )


def fit_m4_chart_ecology_route(
    ecology: Any,
    basis: dict[str, np.ndarray],
    *,
    basis_name: str,
    ridge_grid: tuple[float, ...] = (0.03, 0.10, 0.30),
    hazard_ridge: float = 0.10,
    logistic_iterations: int = 14,
    complexity_penalty: float = 0.0004,
    alias_match_threshold: float = 0.999,
) -> M4ChartEcologyRouteEstimate:
    """Fit identical ecology estimators in a supplied condition basis."""
    categories = ecology.train_calibration.menu.shape[-1]
    if any(
        values.shape[0] != categories
        for values in basis.values()
    ):
        raise ValueError("every role basis must match the menu atoms")
    query_masks = _query_masks(categories)
    train = _one_view(
        ecology.train_calibration,
        ecology.train_selection,
        ecology.train_evaluation,
        basis,
        ridge_grid=ridge_grid,
        hazard_ridge=hazard_ridge,
        logistic_iterations=logistic_iterations,
        complexity_penalty=complexity_penalty,
        alias_match_threshold=alias_match_threshold,
        query_masks=query_masks,
    )
    test = _one_view(
        ecology.test_calibration,
        ecology.test_selection,
        ecology.test_evaluation,
        basis,
        ridge_grid=ridge_grid,
        hazard_ridge=hazard_ridge,
        logistic_iterations=logistic_iterations,
        complexity_penalty=complexity_penalty,
        alias_match_threshold=alias_match_threshold,
        query_masks=query_masks,
    )
    center = np.mean(train[0], axis=0, keepdims=True)
    scale = np.std(train[0], axis=0, keepdims=True)
    scale = np.where(scale > 1e-8, scale, 1.0)
    estimate = M4ChartEcologyRouteEstimate(
        basis_name=basis_name,
        train_signature=(train[0] - center) / scale,
        test_signature=(test[0] - center) / scale,
        feature_names=train[1],
        train_metrics=train[2],
        test_metrics=test[2],
        train_selected_model=train[3],
        test_selected_model=test[3],
        train_refusal=train[4],
        test_refusal=test[4],
        query_masks=query_masks,
    )
    validate_chart_ecology_route(
        estimate,
        authors=ecology.train_calibration.menu.shape[0],
    )
    return estimate


def fit_m4_chart_ecology(
    observed: M4ChartEcologyObserved,
    *,
    candidates: tuple[dict[str, int | str], ...],
    rank_tolerance: float = 1e-6,
    maximum_rank: int | None = None,
    minimum_evaluation_coverage: float = 0.80,
    route_parameters: dict[str, Any] | None = None,
    **chart_thresholds: float,
) -> M4ChartEcologyEstimate:
    """Freeze the response-safe chart, then fit the complete ecology route."""
    validate_chart_ecology_observed(observed)
    chart = fit_m4_condition_chart(
        observed.condition,
        candidates=candidates,
        **chart_thresholds,
    )
    transform, discovered_basis = build_m4_discovered_basis(
        observed,
        chart,
        rank_tolerance=rank_tolerance,
        maximum_rank=maximum_rank,
    )
    discovered = fit_m4_chart_ecology_route(
        observed.ecology,
        discovered_basis,
        basis_name="discovered",
        **(route_parameters or {}),
    )
    reasons = list(chart.refusal_reasons)
    if (
        chart.evaluation_diagnostics["coverage"]
        < minimum_evaluation_coverage
    ):
        reasons.append("evaluation_support_shift")
    if np.mean(discovered.train_refusal & discovered.test_refusal) >= 0.95:
        reasons.append("hidden_opportunity_source_alias")
    return M4ChartEcologyEstimate(
        chart=chart,
        transform_hash=transform.provenance_hash,
        transform_rank=transform.effective_rank,
        discovered=discovered,
        refused=bool(reasons),
        refusal_reasons=tuple(reasons),
    )


def build_m4_discovered_basis(
    observed: M4ChartEcologyObserved,
    chart: Any,
    *,
    rank_tolerance: float = 1e-6,
    maximum_rank: int | None = None,
) -> tuple[Any, dict[str, np.ndarray]]:
    """Build the frozen whitened bases used by the ecology estimator."""
    transform = freeze_m4_condition_transform(
        observed.condition,
        chart,
        rank_tolerance=rank_tolerance,
        maximum_rank=maximum_rank,
    )
    basis = {
        "calibration": transform.transform_prototypes(
            observed.condition.mechanism_calibration.pre_context
        ),
        "selection": transform.transform_prototypes(
            observed.condition.mechanism_selection.pre_context
        ),
        "evaluation": transform.transform_prototypes(
            observed.condition.mechanism_evaluation.pre_context
        ),
    }
    return transform, basis


def rotate_whitened_basis(
    basis: dict[str, np.ndarray],
    *,
    seed: int,
) -> dict[str, np.ndarray]:
    """Apply one shared orthogonal gauge while preserving the mass axis."""
    width = next(iter(basis.values())).shape[1]
    if width <= 1:
        return {name: values.copy() for name, values in basis.items()}
    rng = np.random.default_rng(seed)
    q, _ = np.linalg.qr(rng.normal(size=(width - 1, width - 1)))
    transform = np.eye(width)
    transform[1:, 1:] = q
    return {
        name: values @ transform
        for name, values in basis.items()
    }


def route_action_max_difference(
    first: M4ChartEcologyRouteEstimate,
    second: M4ChartEcologyRouteEstimate,
) -> float:
    """Maximum physical-action difference between two coordinate routes."""
    names = (
        "choice_action",
        "creation_action",
        "loop_kernel",
        "return_curve",
        "recovery_curve",
    )
    differences = []
    for metrics_first, metrics_second in (
        (first.train_metrics, second.train_metrics),
        (first.test_metrics, second.test_metrics),
    ):
        for name in names:
            differences.append(float(np.max(np.abs(
                np.asarray(metrics_first[name], dtype=float)
                - np.asarray(metrics_second[name], dtype=float)
            ))))
    return max(differences, default=0.0)


def replace_evaluation_paths(
    observed: M4ChartEcologyObserved,
    *,
    value: float = 0.0,
) -> M4ChartEcologyObserved:
    """Test helper replacing evaluation responses without touching chart data."""
    ecology = replace(
        observed.ecology,
        train_evaluation=replace(
            observed.ecology.train_evaluation,
            response=np.full_like(
                observed.ecology.train_evaluation.response,
                value,
            ),
        ),
        test_evaluation=replace(
            observed.ecology.test_evaluation,
            response=np.full_like(
                observed.ecology.test_evaluation.response,
                value,
            ),
        ),
    )
    return replace(observed, ecology=ecology)
