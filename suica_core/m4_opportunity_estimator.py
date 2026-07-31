"""Estimator for M4-B selection, creation, return, and feedback ecology."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

from .m4_opportunity_contracts import (
    M4OpportunityEstimate,
    M4OpportunityObserved,
    M4OpportunityPanel,
    validate_opportunity_estimate,
    validate_opportunity_observed,
)


MODEL_COLUMNS = {
    "base": ("intercept", "generated_current"),
    "return": ("intercept", "generated_current", "duration"),
    "feedback": (
        "intercept",
        "generated_current",
        "duration",
        "response_0",
        "response_1",
        "choice_0",
        "choice_1",
        "choice_2",
        "choice_3",
    ),
    "gate": (
        "intercept",
        "generated_current",
        "duration",
        "response_0",
        "response_1",
        "choice_0",
        "choice_1",
        "choice_2",
        "choice_3",
        "history_0",
        "history_1",
        "gate_0",
        "gate_1",
    ),
}


@dataclass(frozen=True)
class _HazardFit:
    names: tuple[str, ...]
    coefficient: np.ndarray
    constant: np.ndarray


def _flatten_events(
    panel: M4OpportunityPanel,
    author: int,
) -> dict[str, np.ndarray]:
    """Flatten one author's occasions while retaining temporal alignment."""
    categories = panel.menu.shape[-1]
    return {
        "menu": panel.menu[author].reshape(-1, categories),
        "external": panel.external_menu[author].reshape(-1, categories),
        "generated": panel.generated_menu[author].reshape(-1, categories),
        "choice": panel.choice[author].reshape(-1),
        "response": panel.response[author, :, :-1].reshape(
            -1,
            panel.response.shape[-1],
        ),
        "response_next": panel.response[author, :, 1:].reshape(
            -1,
            panel.response.shape[-1],
        ),
        "history": panel.history[author, :, :-1].reshape(
            -1,
            panel.history.shape[-1],
        ),
        "history_next": panel.history[author, :, 1:].reshape(
            -1,
            panel.history.shape[-1],
        ),
        "duration": panel.duration[author].reshape(-1, categories),
        "environment": panel.environment[author].reshape(
            -1,
            panel.environment.shape[-1],
        ),
    }


def _transition_rows(
    panel: M4OpportunityPanel,
    author: int,
) -> dict[str, np.ndarray]:
    """Return within-occasion rows with observed next menus."""
    categories = panel.menu.shape[-1]
    return {
        "menu": panel.menu[author, :, :-1].reshape(-1, categories),
        "menu_next": panel.menu[author, :, 1:].reshape(-1, categories),
        "external": panel.external_menu[author, :, :-1].reshape(
            -1,
            categories,
        ),
        "external_next": panel.external_menu[author, :, 1:].reshape(
            -1,
            categories,
        ),
        "generated": panel.generated_menu[author, :, :-1].reshape(
            -1,
            categories,
        ),
        "generated_next": panel.generated_menu[author, :, 1:].reshape(
            -1,
            categories,
        ),
        "choice": panel.choice[author, :, :-1].reshape(-1),
        "response": panel.response[author, :, :-2].reshape(
            -1,
            panel.response.shape[-1],
        ),
        "response_next": panel.response[author, :, 1:-1].reshape(
            -1,
            panel.response.shape[-1],
        ),
        "history": panel.history[author, :, :-2].reshape(
            -1,
            panel.history.shape[-1],
        ),
        "history_next": panel.history[author, :, 1:-1].reshape(
            -1,
            panel.history.shape[-1],
        ),
        "duration": panel.duration[author, :, :-1].reshape(
            -1,
            categories,
        ),
    }


def _conditional_softmax_fit(
    menu: np.ndarray,
    choice: np.ndarray,
    *,
    ridge: float,
) -> np.ndarray:
    """Fit category intercepts under an availability-restricted softmax."""
    categories = menu.shape[1]

    def objective(theta: np.ndarray) -> tuple[float, np.ndarray]:
        logits = np.column_stack([
            np.zeros(len(menu)),
            np.where(menu, theta[None], -1e9),
        ])
        logits -= logits.max(axis=1, keepdims=True)
        probability = np.exp(logits)
        probability /= probability.sum(axis=1, keepdims=True)
        loss = -float(np.sum(
            np.log(np.clip(probability[np.arange(len(choice)), choice], 1e-12, 1.0))
        ))
        loss += 0.5 * ridge * float(theta @ theta)
        observed = np.column_stack([
            choice == category + 1
            for category in range(categories)
        ]).astype(float)
        gradient = np.sum(probability[:, 1:] - observed, axis=0)
        gradient += ridge * theta
        return loss, gradient

    result = minimize(
        lambda value: objective(value)[0],
        np.zeros(categories),
        jac=lambda value: objective(value)[1],
        method="L-BFGS-B",
        options={"maxiter": 80, "ftol": 1e-10},
    )
    theta = np.asarray(result.x, dtype=float)
    return theta - theta.mean()


def _choice_operator(theta: np.ndarray) -> np.ndarray:
    categories = len(theta)

    def probabilities(menu: np.ndarray) -> np.ndarray:
        logits = np.concatenate([
            np.asarray([0.0]),
            np.where(menu, theta, -1e9),
        ])
        logits -= np.max(logits)
        value = np.exp(logits)
        return value[1:] / value.sum()

    full = np.ones(categories, dtype=bool)
    baseline = probabilities(full)
    operator = np.empty((categories, categories))
    for category in range(categories):
        reduced = full.copy()
        reduced[category] = False
        operator[:, category] = baseline - probabilities(reduced)
    return operator


def _response_kernel(
    rows: dict[str, np.ndarray],
    *,
    ridge: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    categories = rows["menu"].shape[1]
    choice_design = np.column_stack([
        rows["choice"] == category + 1
        for category in range(categories)
    ]).astype(float)
    design = np.column_stack([
        rows["response"],
        choice_design,
        rows["history"],
        np.ones(len(rows["choice"])),
    ])
    penalty = ridge * np.eye(design.shape[1])
    penalty[-1, -1] = 0.0
    coefficient = np.linalg.solve(
        design.T @ design + penalty,
        design.T @ rows["response_next"],
    )
    dimensions = rows["response"].shape[1]
    transition = coefficient[:dimensions].T
    choice_effect = coefficient[
        dimensions:dimensions + categories
    ].T
    history_effect = coefficient[
        dimensions + categories:-1
    ].T
    return transition, choice_effect, history_effect


def _hazard_design(
    rows: dict[str, np.ndarray],
    names: tuple[str, ...],
) -> np.ndarray:
    categories = rows["generated"].shape[1]
    values: list[np.ndarray] = []
    for name in names:
        if name == "intercept":
            values.append(np.ones((categories, len(rows["choice"]))))
        elif name == "generated_current":
            values.append(rows["generated"].T.astype(float))
        elif name == "duration":
            values.append(np.tanh(rows["duration"].T / 4.0))
        elif name.startswith("response_"):
            index = int(name.rsplit("_", 1)[1])
            values.append(np.broadcast_to(
                rows["response_next"][:, index][None],
                (categories, len(rows["choice"])),
            ))
        elif name.startswith("choice_"):
            index = int(name.rsplit("_", 1)[1])
            values.append(np.broadcast_to(
                (rows["choice"] == index + 1)[None],
                (categories, len(rows["choice"])),
            ).astype(float))
        elif name.startswith("history_"):
            index = int(name.rsplit("_", 1)[1])
            values.append(np.broadcast_to(
                rows["history"][:, index][None],
                (categories, len(rows["choice"])),
            ))
        elif name.startswith("gate_"):
            index = int(name.rsplit("_", 1)[1])
            gate = (
                (rows["history"][:, 0] > 0.0)
                * rows["response_next"][:, index]
            )
            values.append(np.broadcast_to(
                gate[None],
                (categories, len(rows["choice"])),
            ))
        else:
            raise ValueError(f"unknown hazard feature: {name}")
    return np.stack(values, axis=-1)


def _fit_logistic_hazards(
    design: np.ndarray,
    target: np.ndarray,
    *,
    ridge: float,
    iterations: int,
) -> _HazardFit:
    """Fit K independent ridge-logistic hazards with batched IRLS."""
    categories, _, width = design.shape
    coefficient = np.zeros((categories, width))
    constant = np.zeros(categories, dtype=bool)
    penalty = ridge * np.eye(width)
    penalty[0, 0] = 0.0
    for category in range(categories):
        y = target[:, category].astype(float)
        if np.min(y) == np.max(y):
            probability = (np.sum(y) + 0.5) / (len(y) + 1.0)
            coefficient[category, 0] = np.log(
                probability / (1.0 - probability)
            )
            constant[category] = True
            continue
        x = design[category]
        beta = np.zeros(width)
        beta[0] = np.log((np.mean(y) + 1e-4) / (1.0 - np.mean(y) + 1e-4))
        for _ in range(iterations):
            probability = expit(np.clip(x @ beta, -20.0, 20.0))
            weight = np.clip(probability * (1.0 - probability), 1e-4, None)
            adjusted = x @ beta + (y - probability) / weight
            system = x.T @ (weight[:, None] * x) + penalty
            updated = np.linalg.solve(
                system,
                x.T @ (weight * adjusted),
            )
            if np.max(np.abs(updated - beta)) < 1e-7:
                beta = updated
                break
            beta = updated
        coefficient[category] = beta
    return _HazardFit(
        names=tuple(),
        coefficient=coefficient,
        constant=constant,
    )


def _hazard_logloss(
    fit: _HazardFit,
    design: np.ndarray,
    target: np.ndarray,
) -> float:
    probability = expit(np.einsum(
        "knp,kp->kn",
        design,
        fit.coefficient,
    )).T
    y = target.astype(float)
    return -float(np.mean(
        y * np.log(np.clip(probability, 1e-10, 1.0))
        + (1.0 - y) * np.log(np.clip(1.0 - probability, 1e-10, 1.0))
    ))


def _fit_candidate_models(
    calibration: dict[str, np.ndarray],
    *,
    ridge: float,
    iterations: int,
) -> dict[str, _HazardFit]:
    output: dict[str, _HazardFit] = {}
    for model, names in MODEL_COLUMNS.items():
        design = _hazard_design(calibration, names)
        fitted = _fit_logistic_hazards(
            design,
            calibration["generated_next"],
            ridge=ridge,
            iterations=iterations,
        )
        output[model] = _HazardFit(
            names=names,
            coefficient=fitted.coefficient,
            constant=fitted.constant,
        )
    return output


def _misalign_history(
    rows: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Create a deterministic temporal-placebo history alignment."""
    output = dict(rows)
    shift = max(len(rows["history"]) // 2, 1)
    output["history"] = np.roll(rows["history"], shift, axis=0)
    output["history_next"] = np.roll(
        rows["history_next"],
        shift,
        axis=0,
    )
    return output


def _select_model(
    fits: dict[str, _HazardFit],
    selection: dict[str, np.ndarray],
    *,
    complexity_penalty: float,
) -> str:
    scores = {}
    for model, fit in fits.items():
        loss = _hazard_logloss(
            fit,
            _hazard_design(selection, fit.names),
            selection["generated_next"],
        )
        scores[model] = loss + complexity_penalty * len(fit.names)
    return min(scores, key=scores.get)


def _coefficient(
    fit: _HazardFit,
    prefix: str,
) -> np.ndarray:
    indices = [
        index for index, name in enumerate(fit.names)
        if name.startswith(prefix)
    ]
    if not indices:
        return np.zeros((fit.coefficient.shape[0], 0))
    return fit.coefficient[:, indices]


def _external_persistence(rows: dict[str, np.ndarray]) -> np.ndarray:
    categories = rows["external"].shape[1]
    values = np.zeros(categories)
    for category in range(categories):
        current = rows["external"][:, category]
        following = rows["external_next"][:, category]
        if np.sum(current) < 4 or np.sum(~current) < 4:
            continue
        values[category] = (
            np.mean(following[current])
            - np.mean(following[~current])
        )
    return values


def _return_time(panel: M4OpportunityPanel, author: int) -> float:
    lengths: list[int] = []
    paths = panel.menu[author]
    for occasion in range(paths.shape[0]):
        for category in range(paths.shape[-1]):
            run = 0
            for available in paths[occasion, :, category]:
                if available:
                    if run:
                        lengths.append(run)
                        run = 0
                else:
                    run += 1
    return float(np.mean(lengths)) if lengths else 0.0


def _marginal(values: np.ndarray, width: int) -> np.ndarray:
    counts = np.asarray([
        np.mean(values == index)
        for index in range(width)
    ])
    return counts / max(np.sum(counts), 1e-12)


def _source_alias(
    calibration: M4OpportunityPanel,
    author: int,
    *,
    threshold: float,
) -> bool:
    external = calibration.external_menu[author].reshape(-1)
    generated = calibration.generated_menu[author].reshape(-1)
    if np.std(external.astype(float)) < 0.05:
        return False
    return float(np.mean(external == generated)) >= threshold


def _one_author(
    calibration_panel: M4OpportunityPanel,
    selection_panel: M4OpportunityPanel,
    evaluation_panel: M4OpportunityPanel,
    author: int,
    *,
    ridge: float,
    logistic_iterations: int,
    complexity_penalty: float,
    alias_match_threshold: float,
) -> tuple[np.ndarray, tuple[str, ...], dict[str, np.ndarray | float], str, bool]:
    categories = calibration_panel.menu.shape[-1]
    response_dimensions = calibration_panel.response.shape[-1]
    calibration_events = _flatten_events(calibration_panel, author)
    calibration = _transition_rows(calibration_panel, author)
    selection = _transition_rows(selection_panel, author)
    evaluation = _transition_rows(evaluation_panel, author)
    alias = _source_alias(
        calibration_panel,
        author,
        threshold=alias_match_threshold,
    )
    if alias:
        names = tuple(
            [f"selection_{index}" for index in range(categories)]
            + [
                f"creation_{index}"
                for index in range(categories * response_dimensions)
            ]
            + [f"loop_{index}" for index in range(categories * categories)]
            + [
                "rho",
                "return_time",
                "recovery_time",
                "gate_strength",
                "path_gain",
            ]
        )
        return (
            np.zeros(len(names)),
            names,
            {
                "selection": np.zeros(categories),
                "creation": np.zeros(categories * response_dimensions),
                "gate": np.zeros(categories * response_dimensions),
                "loop": np.zeros(categories * categories),
                "rho": 0.0,
                "return_time": 0.0,
                "recovery_time": 0.0,
                "gate_strength": 0.0,
                "reverse_gate_strength": 0.0,
                "path_gain": 0.0,
                "menu_marginal": np.zeros(categories),
                "choice_marginal": np.zeros(categories + 1),
                "external_persistence": np.zeros(categories),
            },
            "refuse",
            True,
        )

    theta = _conditional_softmax_fit(
        calibration_events["menu"],
        calibration_events["choice"],
        ridge=ridge,
    )
    choice_operator = _choice_operator(theta)
    transition, choice_effect, _ = _response_kernel(
        calibration_events,
        ridge=ridge,
    )
    fits = _fit_candidate_models(
        calibration,
        ridge=ridge,
        iterations=logistic_iterations,
    )
    selected_model = _select_model(
        fits,
        selection,
        complexity_penalty=complexity_penalty,
    )
    selected = fits[selected_model]
    base = fits["base"]
    selected_loss = _hazard_logloss(
        selected,
        _hazard_design(evaluation, selected.names),
        evaluation["generated_next"],
    )
    base_loss = _hazard_logloss(
        base,
        _hazard_design(evaluation, base.names),
        evaluation["generated_next"],
    )
    path_gain = base_loss - selected_loss
    placebo_calibration = _misalign_history(calibration)
    placebo_selection = _misalign_history(selection)
    placebo_fit_raw = _fit_logistic_hazards(
        _hazard_design(
            placebo_calibration,
            MODEL_COLUMNS["gate"],
        ),
        placebo_calibration["generated_next"],
        ridge=ridge,
        iterations=logistic_iterations,
    )
    placebo_fit = _HazardFit(
        names=MODEL_COLUMNS["gate"],
        coefficient=placebo_fit_raw.coefficient,
        constant=placebo_fit_raw.constant,
    )
    placebo_selected_loss = _hazard_logloss(
        placebo_fit,
        _hazard_design(placebo_selection, placebo_fit.names),
        placebo_selection["generated_next"],
    )

    response_coefficient = _coefficient(selected, "response_")
    gate_coefficient = _coefficient(selected, "gate_")
    if response_coefficient.shape[1] == 0:
        response_coefficient = np.zeros(
            (categories, response_dimensions),
        )
    if gate_coefficient.shape[1] == 0:
        gate_coefficient = np.zeros(
            (categories, response_dimensions),
        )
    persistence_coefficient = _coefficient(
        selected,
        "generated_current",
    ).ravel()
    predicted_probability = expit(np.einsum(
        "knp,kp->kn",
        _hazard_design(calibration, selected.names),
        selected.coefficient,
    ))
    derivative = np.mean(
        predicted_probability * (1.0 - predicted_probability),
        axis=1,
    )
    external_absence = 1.0 - np.mean(
        calibration["external_next"],
        axis=0,
    )
    history_open_rate = float(np.mean(
        calibration["history"][:, 0] > 0.0
    ))
    effective_response_coefficient = (
        response_coefficient
        + history_open_rate * gate_coefficient
    )
    opportunity_response = (
        external_absence[:, None]
        * derivative[:, None]
        * effective_response_coefficient
    )
    gate_operator = (
        external_absence[:, None]
        * derivative[:, None]
        * gate_coefficient
    )
    loop = opportunity_response @ choice_effect @ choice_operator
    external_persistence = _external_persistence(calibration)
    generated_persistence = derivative * persistence_coefficient
    jacobian = (
        np.diag(0.5 * (external_persistence + generated_persistence))
        + loop
    )
    rho = float(np.max(np.abs(np.linalg.eigvals(jacobian))))
    transition_rho = float(np.max(np.abs(np.linalg.eigvals(transition))))
    recovery_time = (
        float(np.log(0.5) / np.log(np.clip(transition_rho, 1e-4, 0.999)))
        if transition_rho < 0.999
        else 100.0
    )
    gate_strength = float(np.linalg.norm(
        gate_operator
    ))
    placebo_gate = _coefficient(placebo_fit, "gate_")
    placebo_probability = expit(np.einsum(
        "knp,kp->kn",
        _hazard_design(placebo_calibration, placebo_fit.names),
        placebo_fit.coefficient,
    ))
    placebo_derivative = np.mean(
        placebo_probability * (1.0 - placebo_probability),
        axis=1,
    )
    reverse_gate_strength = float(np.linalg.norm(
        external_absence[:, None]
        * placebo_derivative[:, None]
        * placebo_gate
    ))
    if selected_model != "gate":
        gate_operator = np.zeros_like(gate_operator)
        gate_strength = 0.0
    if placebo_selected_loss >= min(
        _hazard_logloss(
            fits["feedback"],
            _hazard_design(selection, fits["feedback"].names),
            selection["generated_next"],
        ),
        _hazard_logloss(
            fits["base"],
            _hazard_design(selection, fits["base"].names),
            selection["generated_next"],
        ),
    ):
        reverse_gate_strength = 0.0
    evaluation_events = _flatten_events(evaluation_panel, author)
    menu_marginal = np.mean(
        evaluation_events["menu"].astype(float),
        axis=0,
    )
    choice_marginal = _marginal(
        evaluation_events["choice"],
        categories + 1,
    )
    metrics: dict[str, np.ndarray | float] = {
        "selection": theta,
        "creation": opportunity_response.ravel(),
        "gate": gate_operator.ravel(),
        "loop": loop.ravel(),
        "rho": rho,
        "return_time": _return_time(evaluation_panel, author),
        "recovery_time": recovery_time,
        "gate_strength": gate_strength,
        "reverse_gate_strength": reverse_gate_strength,
        "path_gain": path_gain,
        "menu_marginal": menu_marginal,
        "choice_marginal": choice_marginal,
        "external_persistence": external_persistence,
    }
    names = tuple(
        [f"selection_{index}" for index in range(categories)]
        + [
            f"creation_{index}"
            for index in range(categories * response_dimensions)
        ]
        + [f"loop_{index}" for index in range(categories * categories)]
        + [
            "rho",
            "return_time",
            "recovery_time",
            "gate_strength",
            "path_gain",
        ]
    )
    signature = np.concatenate([
        theta,
        opportunity_response.ravel(),
        loop.ravel(),
        np.asarray([
            rho,
            metrics["return_time"],
            recovery_time,
            gate_strength,
            path_gain,
        ]),
    ])
    return signature, names, metrics, selected_model, False


def _one_view(
    calibration: M4OpportunityPanel,
    selection: M4OpportunityPanel,
    evaluation: M4OpportunityPanel,
    *,
    ridge: float,
    logistic_iterations: int,
    complexity_penalty: float,
    alias_match_threshold: float,
) -> tuple[np.ndarray, tuple[str, ...], dict[str, np.ndarray], np.ndarray, np.ndarray]:
    rows = [
        _one_author(
            calibration,
            selection,
            evaluation,
            author,
            ridge=ridge,
            logistic_iterations=logistic_iterations,
            complexity_penalty=complexity_penalty,
            alias_match_threshold=alias_match_threshold,
        )
        for author in range(calibration.menu.shape[0])
    ]
    signature = np.stack([row[0] for row in rows])
    names = rows[0][1]
    metric_names = tuple(rows[0][2])
    metrics = {
        name: np.stack([
            np.atleast_1d(row[2][name]).astype(float)
            for row in rows
        ]).squeeze(axis=1)
        if np.atleast_1d(rows[0][2][name]).size == 1
        else np.stack([
            np.atleast_1d(row[2][name]).astype(float)
            for row in rows
        ])
        for name in metric_names
    }
    return (
        signature,
        names,
        metrics,
        np.asarray([row[3] for row in rows], dtype=object),
        np.asarray([row[4] for row in rows], dtype=bool),
    )


def fit_m4_opportunity_ecology(
    observed: M4OpportunityObserved,
    *,
    ridge: float = 0.08,
    logistic_iterations: int = 18,
    complexity_penalty: float = 0.00035,
    alias_match_threshold: float = 0.995,
) -> M4OpportunityEstimate:
    """Estimate independent-view opportunity ecology signatures."""
    validate_opportunity_observed(observed)
    train = _one_view(
        observed.train_calibration,
        observed.train_selection,
        observed.train_evaluation,
        ridge=ridge,
        logistic_iterations=logistic_iterations,
        complexity_penalty=complexity_penalty,
        alias_match_threshold=alias_match_threshold,
    )
    test = _one_view(
        observed.test_calibration,
        observed.test_selection,
        observed.test_evaluation,
        ridge=ridge,
        logistic_iterations=logistic_iterations,
        complexity_penalty=complexity_penalty,
        alias_match_threshold=alias_match_threshold,
    )
    center = train[0].mean(axis=0, keepdims=True)
    scale = train[0].std(axis=0, ddof=0, keepdims=True)
    scale = np.where(scale > 1e-8, scale, 1.0)
    estimate = M4OpportunityEstimate(
        train_signature=(train[0] - center) / scale,
        test_signature=(test[0] - center) / scale,
        feature_names=train[1],
        train_metrics=train[2],
        test_metrics=test[2],
        train_selected_model=train[3],
        test_selected_model=test[3],
        train_refusal=train[4],
        test_refusal=test[4],
    )
    validate_opportunity_estimate(
        estimate,
        authors=observed.train_calibration.menu.shape[0],
    )
    return estimate
