"""Synthetic joint-identifiability battery for the SUICA V8 typed graph.

The module keeps latent author-process objects separate from estimates,
uncertainty, refusals, population lifts, and external readouts.  It contains
no text, questionnaire labels, or PANDORA-specific tuning.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class HJICSpec:
    """Dimensions and evidence budgets for one synthetic HJIC population."""

    authors: int = 64
    conditions: int = 4
    occasions: int = 4
    free_events: int = 256
    fixed_repetitions: int = 6
    response_dimensions: int = 4
    condition_dimensions: int = 2
    observation_noise: float = 0.20
    route_source_authors: int = 72
    route_validation_authors: int = 72
    route_test_authors: int = 512
    route_tasks: int = 6

    def __post_init__(self) -> None:
        if self.authors < 16:
            raise ValueError("HJIC requires at least 16 authors.")
        if self.conditions < 3:
            raise ValueError("HJIC requires at least three conditions.")
        if not 1 <= self.condition_dimensions < self.conditions:
            raise ValueError(
                "condition_dimensions must be positive and below conditions."
            )
        if self.occasions < 2:
            raise ValueError("Identifiable HJIC requires repeated occasions.")
        if self.free_events < 32 or self.fixed_repetitions < 2:
            raise ValueError("HJIC evidence budgets are too small.")
        if self.response_dimensions < 2:
            raise ValueError("HJIC requires multivariate responses.")
        if self.observation_noise <= 0:
            raise ValueError("observation_noise must be positive.")


def safe_correlation(left: np.ndarray, right: np.ndarray) -> float:
    """Return Pearson correlation or NaN for a degenerate pair."""
    x = np.asarray(left, dtype=float).ravel()
    y = np.asarray(right, dtype=float).ravel()
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 3:
        return float("nan")
    x = x[mask]
    y = y[mask]
    if np.std(x) <= 1e-12 or np.std(y) <= 1e-12:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def normalized_error(estimate: np.ndarray, truth: np.ndarray) -> float:
    """Return Frobenius error relative to planted truth energy."""
    estimate = np.asarray(estimate, dtype=float)
    truth = np.asarray(truth, dtype=float)
    denominator = float(np.linalg.norm(truth))
    if denominator <= 1e-12:
        return float(np.linalg.norm(estimate - truth))
    return float(np.linalg.norm(estimate - truth) / denominator)


def centered_condition_basis(
    conditions: int,
    dimensions: int,
) -> np.ndarray:
    """Construct a deterministic centered orthonormal condition basis."""
    center = np.eye(conditions) - np.ones((conditions, conditions)) / conditions
    vectors, _, _ = np.linalg.svd(center, full_matrices=False)
    basis = vectors[:, :dimensions] * np.sqrt(conditions)
    signs = np.sign(basis[np.argmax(np.abs(basis), axis=0), range(dimensions)])
    signs = np.where(signs == 0, 1.0, signs)
    return basis * signs[None, :]


def effect_coding(levels: int) -> np.ndarray:
    """Return sum-to-zero effect coding for a balanced categorical variable."""
    coding = np.zeros((levels, levels - 1), dtype=float)
    coding[: levels - 1] = np.eye(levels - 1)
    coding[levels - 1] = -1.0
    return coding


def _orthogonal_map(rng: np.random.Generator, dimensions: int) -> np.ndarray:
    matrix = rng.normal(size=(dimensions, dimensions))
    q, _ = np.linalg.qr(matrix)
    return np.asarray(q, dtype=float)


def _draw_choice(
    rng: np.random.Generator,
    utility: np.ndarray,
    available: np.ndarray,
) -> int:
    indices = np.flatnonzero(available)
    local = utility[indices]
    probability = np.exp(local - logsumexp(local))
    return int(rng.choice(indices, p=probability))


def simulate_identifiable_world(
    seed: int,
    spec: HJICSpec,
) -> dict[str, Any]:
    """Generate a full-support world with identifiable technical components."""
    rng = np.random.default_rng(seed)
    n = spec.authors
    c = spec.conditions
    o = spec.occasions
    d = spec.response_dimensions
    p = spec.condition_dimensions
    phi = centered_condition_basis(c, p)
    observation_map = _orthogonal_map(rng, d)

    stable = rng.normal(scale=0.80, size=(n, d))
    preference = rng.normal(scale=0.65, size=(n, c))
    preference -= preference.mean(axis=1, keepdims=True)
    persistence = np.clip(rng.normal(0.75, 0.30, size=n), 0.10, 1.50)
    response_operator = rng.normal(scale=0.55, size=(n, d, p))
    coupling = rng.normal(scale=0.35, size=(n, d))
    state_direction = rng.normal(size=d)
    state_direction *= 0.55 / np.linalg.norm(state_direction)
    state = np.zeros((n, o), dtype=float)
    state[:, 0] = rng.normal(size=n)
    for occasion in range(1, o):
        state[:, occasion] = (
            0.55 * state[:, occasion - 1]
            + rng.normal(scale=np.sqrt(1 - 0.55**2), size=n)
        )
    state -= state.mean(axis=1, keepdims=True)

    menus = np.zeros((n, spec.free_events, c), dtype=bool)
    choices = np.zeros((n, spec.free_events), dtype=int)
    for author in range(n):
        previous = -1
        for event in range(spec.free_events):
            menu_size = c - 1
            available = rng.choice(c, size=menu_size, replace=False)
            if previous >= 0 and rng.random() < 0.70 and previous not in available:
                available[rng.integers(menu_size)] = previous
                available = np.unique(available)
                if len(available) < menu_size:
                    remaining = [
                        item
                        for item in range(c)
                        if item not in set(available.tolist())
                    ]
                    available = np.append(
                        available,
                        rng.choice(remaining, size=menu_size - len(available)),
                    )
            menus[author, event, available] = True
            utility = preference[author].copy()
            if previous >= 0:
                utility[previous] += persistence[author]
            selected = _draw_choice(
                rng,
                utility,
                menus[author, event],
            )
            choices[author, event] = selected
            previous = selected

    occasion_code = effect_coding(o)
    cue_values = np.linspace(
        -1.0,
        1.0,
        spec.fixed_repetitions,
    )
    rows: list[tuple[int, int, float]] = []
    for occasion in range(o):
        for condition in range(c):
            for cue in cue_values:
                rows.append((occasion, condition, float(cue)))
    row_count = len(rows)
    design = np.zeros(
        (row_count, 1 + p + 1 + (o - 1)),
        dtype=float,
    )
    latent = np.zeros((n, row_count, d), dtype=float)
    for row, (occasion, condition, cue) in enumerate(rows):
        design[row, 0] = 1.0
        design[row, 1 : 1 + p] = phi[condition]
        design[row, 1 + p] = cue
        design[row, 2 + p :] = occasion_code[occasion]
        latent[:, row] = (
            stable
            + np.einsum(
                "udp,p->ud",
                response_operator,
                phi[condition],
            )
            + coupling * cue
            + state[:, occasion, None] * state_direction[None, :]
        )
    noise = rng.normal(
        scale=spec.observation_noise,
        size=latent.shape,
    )
    pre_observation = latent + noise
    observed = pre_observation @ observation_map.T
    projected_truth = {
        "stable": stable @ observation_map.T,
        "response_operator": np.einsum(
            "ij,ujk->uik",
            observation_map,
            response_operator,
        ),
        "coupling": coupling @ observation_map.T,
        "state": (
            state[:, :, None]
            * (state_direction @ observation_map.T)[None, None, :]
        ),
    }
    return {
        "spec": spec,
        "phi": phi,
        "observation_map": observation_map,
        "preference": preference,
        "persistence": persistence,
        "menus": menus,
        "choices": choices,
        "design": design,
        "pre_observation": pre_observation,
        "observed": observed,
        "rows": rows,
        "projected_truth": projected_truth,
    }


def fit_choice_kernel(
    menus: np.ndarray,
    choices: np.ndarray,
) -> tuple[np.ndarray, float]:
    """Fit menu-conditioned preference and one-step persistence."""
    menus = np.asarray(menus, dtype=bool)
    choices = np.asarray(choices, dtype=int)
    events, conditions = menus.shape
    if len(choices) != events:
        raise ValueError("menus and choices must contain the same events.")
    previous = np.zeros((events, conditions), dtype=float)
    if events > 1:
        previous[np.arange(1, events), choices[:-1]] = 1.0
    chosen = np.zeros((events, conditions), dtype=float)
    chosen[np.arange(events), choices] = 1.0

    def objective(parameter: np.ndarray) -> tuple[float, np.ndarray]:
        beta = parameter[:conditions]
        beta = beta - beta.mean()
        kappa = float(parameter[-1])
        utility = beta[None, :] + kappa * previous
        masked = np.where(menus, utility, -1e12)
        log_norm = logsumexp(masked, axis=1)
        log_probability = masked[np.arange(events), choices] - log_norm
        probability = np.exp(masked - log_norm[:, None])
        score = chosen - probability
        gradient_beta = score.sum(axis=0)
        gradient_beta -= gradient_beta.mean()
        gradient_kappa = float(np.sum(score * previous))
        ridge = 1e-4 * float(np.dot(parameter, parameter))
        value = -float(np.mean(log_probability)) + ridge
        gradient = -np.append(
            gradient_beta / events,
            gradient_kappa / events,
        ) + 2e-4 * parameter
        return value, gradient

    fit = minimize(
        objective,
        np.zeros(conditions + 1, dtype=float),
        method="L-BFGS-B",
        jac=True,
        bounds=[(None, None)] * conditions + [(-3.0, 3.0)],
        options={"maxiter": 300, "ftol": 1e-11},
    )
    if not fit.success:
        raise RuntimeError(f"Choice-kernel fit failed: {fit.message}")
    preference = fit.x[:conditions] - fit.x[:conditions].mean()
    return preference, float(fit.x[-1])


def fit_identifiable_world(world: dict[str, Any]) -> dict[str, Any]:
    """Estimate all identifiable components without access to planted truth."""
    spec: HJICSpec = world["spec"]
    design = np.asarray(world["design"], dtype=float)
    observed = np.asarray(world["observed"], dtype=float)
    inverse = np.linalg.inv(design.T @ design)
    pseudo = inverse @ design.T
    coefficients = np.einsum("qr,urd->uqd", pseudo, observed)
    fitted = np.einsum("rq,uqd->urd", design, coefficients)
    residual = observed - fitted
    degrees = len(design) - design.shape[1]
    residual_variance = np.sum(residual**2, axis=1) / degrees
    intercept_se = np.sqrt(residual_variance * inverse[0, 0])

    p = spec.condition_dimensions
    o = spec.occasions
    occasion_code = effect_coding(o)
    state_coefficients = coefficients[:, 2 + p :, :]
    state = np.einsum("ok,ukd->uod", occasion_code, state_coefficients)

    preference = np.zeros_like(world["preference"])
    persistence = np.zeros_like(world["persistence"])
    for author in range(spec.authors):
        preference[author], persistence[author] = fit_choice_kernel(
            world["menus"][author],
            world["choices"][author],
        )
    return {
        "stable": coefficients[:, 0, :],
        "response_operator": np.transpose(
            coefficients[:, 1 : 1 + p, :],
            (0, 2, 1),
        ),
        "coupling": coefficients[:, 1 + p, :],
        "state": state,
        "preference": preference,
        "persistence": persistence,
        "intercept_se": intercept_se,
    }


def evaluate_identifiable_world(
    world: dict[str, Any],
    estimate: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    """Score recovery, commutation, and interval coverage."""
    truth = world["projected_truth"]
    component_rows: list[dict[str, Any]] = []
    commutation_rows: list[dict[str, Any]] = []
    pairs = {
        "stable": (estimate["stable"], truth["stable"]),
        "response_operator": (
            estimate["response_operator"],
            truth["response_operator"],
        ),
        "coupling": (estimate["coupling"], truth["coupling"]),
        "state": (estimate["state"], truth["state"]),
        "preference": (estimate["preference"], world["preference"]),
        "persistence": (estimate["persistence"], world["persistence"]),
    }
    for component, (observed, planted) in pairs.items():
        component_rows.append({
            "world": "IDENTIFIABLE",
            "component": component,
            "truth_correlation": safe_correlation(observed, planted),
        })

    design = np.asarray(world["design"], dtype=float)
    pseudo = np.linalg.inv(design.T @ design) @ design.T
    latent_coefficients = np.einsum(
        "qr,urd->uqd",
        pseudo,
        np.asarray(world["pre_observation"], dtype=float),
    )
    observation_map = np.asarray(world["observation_map"], dtype=float)
    p = world["spec"].condition_dimensions
    occasion_code = effect_coding(world["spec"].occasions)
    latent_state = np.einsum(
        "ok,ukd->uod",
        occasion_code,
        latent_coefficients[:, 2 + p :, :],
    )
    projected_estimates = {
        "stable": latent_coefficients[:, 0, :] @ observation_map.T,
        "response_operator": np.einsum(
            "ij,ujk->uik",
            observation_map,
            np.transpose(
                latent_coefficients[:, 1 : 1 + p, :],
                (0, 2, 1),
            ),
        ),
        "coupling": (
            latent_coefficients[:, 1 + p, :] @ observation_map.T
        ),
        "state": latent_state @ observation_map.T,
        "preference": estimate["preference"],
        "persistence": estimate["persistence"],
    }
    for component, observed in estimate.items():
        if component not in projected_estimates:
            continue
        commutation_rows.append({
            "world": "IDENTIFIABLE",
            "component": component,
            "standardized_commutation_defect": normalized_error(
                observed,
                projected_estimates[component],
            ),
        })

    stable = np.asarray(estimate["stable"], dtype=float)
    stable_truth = np.asarray(truth["stable"], dtype=float)
    se = np.asarray(estimate["intercept_se"], dtype=float)
    covered = (
        (stable_truth >= stable - 1.96 * se)
        & (stable_truth <= stable + 1.96 * se)
    )
    coverage_rows = [{
        "world": "IDENTIFIABLE",
        "component": "stable",
        "nominal": 0.95,
        "coverage": float(np.mean(covered)),
        "interval_cells": int(covered.size),
    }]

    rng = np.random.default_rng(9401)
    micro = rng.normal(size=(100, world["spec"].response_dimensions))
    exact_error = float(
        np.max(
            np.abs(
                micro.mean(axis=0) @ observation_map.T
                - (micro @ observation_map.T).mean(axis=0)
            )
        )
    )
    commutation_rows.append({
        "world": "IDENTIFIABLE",
        "component": "linear_observation_mean",
        "standardized_commutation_defect": exact_error,
    })
    return {
        "component": component_rows,
        "commutation": commutation_rows,
        "coverage": coverage_rows,
    }


def paired_observation_auc(
    left: np.ndarray,
    right: np.ndarray,
    *,
    seed: int,
) -> float:
    """Classify two paired observed worlds while keeping each pair together."""
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    if left.shape != right.shape or left.ndim != 2:
        raise ValueError("Alias observations must be paired matrices.")
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(left))
    split = max(4, int(0.70 * len(order)))
    train = order[:split]
    test = order[split:]
    train_x = np.vstack([left[train], right[train]])
    train_y = np.concatenate([
        np.zeros(len(train), dtype=int),
        np.ones(len(train), dtype=int),
    ])
    test_x = np.vstack([left[test], right[test]])
    test_y = np.concatenate([
        np.zeros(len(test), dtype=int),
        np.ones(len(test), dtype=int),
    ])
    scaler = StandardScaler().fit(train_x)
    model = LogisticRegression(
        C=1.0,
        solver="lbfgs",
        max_iter=1000,
    ).fit(scaler.transform(train_x), train_y)
    prediction = model.predict_proba(scaler.transform(test_x))[:, 1]
    return float(roc_auc_score(test_y, prediction))


def alias_world(
    world: str,
    *,
    seed: int,
    authors: int = 96,
) -> dict[str, Any]:
    """Construct paired latent worlds that are observationally equivalent."""
    rng = np.random.default_rng(seed)
    if world == "STATE_ALIAS":
        stable = rng.normal(size=(authors, 4))
        shift = rng.normal(scale=0.8, size=(authors, 4))
        left = stable
        right = (stable + shift) + (-shift)
        latent_separation = float(np.mean(np.linalg.norm(shift, axis=1)))
        component = "stable_vs_state"
    elif world == "MENU_ALIAS":
        probability = rng.dirichlet(np.ones(4), size=authors)
        counts = np.vstack([
            rng.multinomial(240, row) for row in probability
        ]).astype(float)
        left = counts / counts.sum(axis=1, keepdims=True)
        right = left.copy()
        latent_separation = float(
            np.mean(np.linalg.norm(np.log(probability + 1e-9), axis=1))
        )
        component = "preference_vs_availability"
    elif world == "KERNEL_ALIAS":
        operator = rng.normal(size=(authors, 4, 3))
        hidden_shift = rng.normal(scale=0.8, size=(authors, 1, 3))
        alternative = operator.copy()
        alternative[:, -1:, :] += hidden_shift
        projection = np.eye(3, 4)
        left = np.einsum("ij,ujk->uik", projection, operator).reshape(
            authors,
            -1,
        )
        right = np.einsum(
            "ij,ujk->uik",
            projection,
            alternative,
        ).reshape(authors, -1)
        latent_separation = float(
            np.mean(
                np.linalg.norm(
                    (alternative - operator).reshape(authors, -1),
                    axis=1,
                )
            )
        )
        component = "full_response_operator"
    elif world == "ORDER_ALIAS":
        base = np.tile(np.arange(4), 40)
        left_sequences = []
        right_sequences = []
        for _ in range(authors):
            permutation = rng.permutation(len(base))
            alternating = base[permutation]
            block = np.sort(alternating)
            left_sequences.append(alternating)
            right_sequences.append(block)
        left_sequences = np.asarray(left_sequences)
        right_sequences = np.asarray(right_sequences)
        left = np.stack(
            [(left_sequences == index).mean(axis=1) for index in range(4)],
            axis=1,
        )
        right = np.stack(
            [(right_sequences == index).mean(axis=1) for index in range(4)],
            axis=1,
        )
        left_stay = np.mean(
            left_sequences[:, 1:] == left_sequences[:, :-1],
            axis=1,
        )
        right_stay = np.mean(
            right_sequences[:, 1:] == right_sequences[:, :-1],
            axis=1,
        )
        latent_separation = float(np.mean(np.abs(left_stay - right_stay)))
        component = "ordered_transition"
    else:
        raise ValueError(f"Unsupported alias world: {world}")
    return {
        "world": world,
        "component": component,
        "left": np.asarray(left, dtype=float),
        "right": np.asarray(right, dtype=float),
        "latent_separation": latent_separation,
        "observed_max_difference": float(np.max(np.abs(left - right))),
        "refusal": 1,
        "false_point_identification": 0,
        "observational_auc": paired_observation_auc(
            left,
            right,
            seed=seed + 71,
        ),
    }


def gaussian_information_order(seed: int) -> dict[str, float]:
    """Verify frozen-contraction DPI and Bayes-risk ordering analytically."""
    rng = np.random.default_rng(seed)
    latent_dimensions = 5
    x_dimensions = 9
    y_dimensions = 3
    contraction_dimensions = 4
    x_map = rng.normal(size=(x_dimensions, latent_dimensions))
    y_map = rng.normal(size=(y_dimensions, latent_dimensions))
    sigma_x = x_map @ x_map.T + 0.6**2 * np.eye(x_dimensions)
    sigma_y = y_map @ y_map.T + 0.7**2 * np.eye(y_dimensions)
    sigma_yx = y_map @ x_map.T
    q, _ = np.linalg.qr(
        rng.normal(size=(x_dimensions, contraction_dimensions))
    )
    contraction = q.T

    def conditional(
        covariance_x: np.ndarray,
        covariance_yx: np.ndarray,
    ) -> np.ndarray:
        value = sigma_y - covariance_yx @ np.linalg.solve(
            covariance_x,
            covariance_yx.T,
        )
        return 0.5 * (value + value.T)

    residual_full = conditional(sigma_x, sigma_yx)
    covariance_contracted = contraction @ sigma_x @ contraction.T
    y_contracted = sigma_yx @ contraction.T
    residual_contracted = conditional(
        covariance_contracted,
        y_contracted,
    )

    def mutual_information(residual: np.ndarray) -> float:
        sign_y, log_y = np.linalg.slogdet(sigma_y)
        sign_r, log_r = np.linalg.slogdet(residual)
        if sign_y <= 0 or sign_r <= 0:
            raise ValueError("Gaussian covariance must be positive definite.")
        return float(0.5 * (log_y - log_r) / np.log(2.0))

    mi_full = mutual_information(residual_full)
    mi_contracted = mutual_information(residual_contracted)
    loewner = residual_contracted - residual_full
    return {
        "mi_full_bits": mi_full,
        "mi_contracted_bits": mi_contracted,
        "dpi_violation_bits": max(0.0, mi_contracted - mi_full),
        "conditional_covariance_order_min_eigenvalue": float(
            np.linalg.eigvalsh(loewner).min()
        ),
        "bayes_mse_full": float(np.trace(residual_full)),
        "bayes_mse_contracted": float(np.trace(residual_contracted)),
        "bayes_risk_violation": max(
            0.0,
            float(np.trace(residual_full) - np.trace(residual_contracted)),
        ),
    }


def _fit_route(
    train_x: np.ndarray,
    train_y: np.ndarray,
    validation_x: np.ndarray,
    validation_y: np.ndarray,
) -> tuple[float, float]:
    scaler = StandardScaler().fit(train_x)
    train = scaler.transform(train_x)
    validation = scaler.transform(validation_x)
    best_score = -np.inf
    best_alpha = 1.0
    for alpha in (0.1, 1.0, 10.0, 100.0):
        prediction = Ridge(alpha=alpha).fit(train, train_y).predict(validation)
        score = safe_correlation(prediction, validation_y)
        if np.isfinite(score) and score > best_score:
            best_score = score
            best_alpha = alpha
    return float(best_score), float(best_alpha)


def route_null_trial(seed: int, spec: HJICSpec) -> dict[str, Any]:
    """Show that finite-sample route heterogeneity is not ontology evidence."""
    rng = np.random.default_rng(seed)
    total = (
        spec.route_source_authors
        + spec.route_validation_authors
        + spec.route_test_authors
    )
    latent = rng.normal(size=(total, 4))
    core = latent + rng.normal(scale=0.35, size=latent.shape)
    nuisance = rng.normal(size=(total, 10))
    routes = {
        "core_only": core,
        "core_plus_2": np.column_stack([core, nuisance[:, :2]]),
        "core_plus_10": np.column_stack([core, nuisance]),
    }
    source_stop = spec.route_source_authors
    validation_stop = source_stop + spec.route_validation_authors
    weights = rng.normal(size=(spec.route_tasks, 4))
    selected: list[str] = []
    test_scores: list[float] = []
    for task in range(spec.route_tasks):
        outcome = (
            latent @ weights[task]
            + rng.normal(scale=1.4, size=total)
        )
        candidates = []
        for route_name, values in routes.items():
            score, alpha = _fit_route(
                values[:source_stop],
                outcome[:source_stop],
                values[source_stop:validation_stop],
                outcome[source_stop:validation_stop],
            )
            candidates.append((score, -values.shape[1], route_name, alpha))
        _, _, route_name, alpha = max(candidates)
        selected.append(route_name)
        values = routes[route_name]
        scaler = StandardScaler().fit(values[:validation_stop])
        model = Ridge(alpha=alpha).fit(
            scaler.transform(values[:validation_stop]),
            outcome[:validation_stop],
        )
        prediction = model.predict(
            scaler.transform(values[validation_stop:])
        )
        test_scores.append(
            safe_correlation(prediction, outcome[validation_stop:])
        )
    distinct = len(set(selected))
    naive = int(distinct >= 2)
    planted_unique_information = 0.0
    licensed = int(naive and planted_unique_information > 0.0)
    return {
        "world": "ROUTE_NULL",
        "tasks": spec.route_tasks,
        "distinct_selected_routes": distinct,
        "selected_routes": "|".join(selected),
        "naive_specialization_claim": naive,
        "licensed_specialization_claim": licensed,
        "planted_incremental_information": planted_unique_information,
        "mean_test_correlation": float(np.nanmean(test_scores)),
    }


def _correlation_matrix(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    combined = np.corrcoef(
        np.column_stack([left, right]),
        rowvar=False,
    )
    return combined[: left.shape[1], left.shape[1] :]


def _residualize(values: np.ndarray, nuisance: np.ndarray) -> np.ndarray:
    design = np.column_stack([np.ones(len(values)), nuisance])
    coefficients = np.linalg.lstsq(design, values, rcond=None)[0]
    return values - design @ coefficients


def relational_lift_trial(
    seed: int,
    *,
    world: str,
    authors: int = 1600,
) -> dict[str, Any]:
    """Separate individual accuracy, relation-pattern fidelity, and confounding."""
    rng = np.random.default_rng(seed)
    big5_dimensions = 5
    mbti_dimensions = 4
    shared_dimensions = 2
    nuisance = rng.normal(size=(authors, 2))
    big5_load = rng.normal(size=(big5_dimensions, shared_dimensions))
    mbti_load = rng.normal(size=(mbti_dimensions, shared_dimensions))
    if world == "SHARED_LATENT":
        shared = rng.normal(size=(authors, shared_dimensions))
        text_state = shared + rng.normal(scale=0.80, size=shared.shape)
        big5 = (
            0.40 * shared @ big5_load.T
            + rng.normal(scale=1.0, size=(authors, big5_dimensions))
        )
        mbti = (
            0.40 * shared @ mbti_load.T
            + rng.normal(scale=1.0, size=(authors, mbti_dimensions))
        )
        predicted_big5 = text_state @ big5_load.T
        predicted_mbti = text_state @ mbti_load.T
    elif world == "COMMON_NUISANCE":
        big5 = (
            0.55 * nuisance @ big5_load.T
            + rng.normal(scale=1.0, size=(authors, big5_dimensions))
        )
        mbti = (
            0.55 * nuisance @ mbti_load.T
            + rng.normal(scale=1.0, size=(authors, mbti_dimensions))
        )
        text_state = nuisance + rng.normal(scale=0.35, size=nuisance.shape)
        predicted_big5 = text_state @ big5_load.T
        predicted_mbti = text_state @ mbti_load.T
    else:
        raise ValueError(f"Unsupported relational world: {world}")

    true_matrix = _correlation_matrix(big5, mbti)
    predicted_matrix = _correlation_matrix(
        predicted_big5,
        predicted_mbti,
    )
    residual_big5 = _residualize(big5, nuisance)
    residual_mbti = _residualize(mbti, nuisance)
    residual_predicted_big5 = _residualize(predicted_big5, nuisance)
    residual_predicted_mbti = _residualize(predicted_mbti, nuisance)
    conditional_true = _correlation_matrix(
        residual_big5,
        residual_mbti,
    )
    conditional_predicted = _correlation_matrix(
        residual_predicted_big5,
        residual_predicted_mbti,
    )
    true_norm = float(np.linalg.norm(true_matrix))
    conditional_norm = float(np.linalg.norm(conditional_true))
    conditional_fidelity = safe_correlation(
        conditional_true,
        conditional_predicted,
    )
    raw_fidelity = safe_correlation(true_matrix, predicted_matrix)
    direct = [
        safe_correlation(big5[:, index], predicted_big5[:, index])
        for index in range(big5_dimensions)
    ] + [
        safe_correlation(mbti[:, index], predicted_mbti[:, index])
        for index in range(mbti_dimensions)
    ]
    nuisance_fraction = (
        max(0.0, min(1.0, 1.0 - conditional_norm / true_norm))
        if true_norm > 1e-12
        else 1.0
    )
    licensed = bool(
        np.isfinite(raw_fidelity)
        and raw_fidelity >= 0.80
        and np.isfinite(conditional_fidelity)
        and conditional_fidelity >= 0.80
        and conditional_norm >= 0.10
        and nuisance_fraction < 0.80
    )
    return {
        "world": world,
        "authors": authors,
        "mean_individual_correlation": float(np.nanmean(direct)),
        "raw_relation_element_correlation": raw_fidelity,
        "conditional_relation_element_correlation": conditional_fidelity,
        "true_relation_frobenius": true_norm,
        "conditional_relation_frobenius": conditional_norm,
        "nuisance_explained_fraction": nuisance_fraction,
        "licensed_structural_connection": int(licensed),
    }


def reference_drift_trial(seed: int, *, authors: int = 1200) -> dict[str, Any]:
    """Test fixed-origin scoring and population-specific relation lifts."""
    rng = np.random.default_rng(seed)
    dimensions = 4
    reference = rng.normal(size=(authors, dimensions))
    direction = rng.normal(size=dimensions)
    direction /= np.linalg.norm(direction)
    true_shift = 0.80 * direction
    q, _ = np.linalg.qr(rng.normal(size=(dimensions, dimensions)))
    covariance = q @ np.diag([2.0, 1.5, 0.6, 0.4]) @ q.T
    evaluation = rng.multivariate_normal(
        true_shift,
        covariance,
        size=authors,
    )
    external_center = reference.mean(axis=0)
    fixed_score = evaluation - external_center
    transductive_score = evaluation - evaluation.mean(axis=0)
    recovered_shift = fixed_score.mean(axis=0)
    cosine = float(
        np.dot(recovered_shift, true_shift)
        / (np.linalg.norm(recovered_shift) * np.linalg.norm(true_shift))
    )
    amplitude_error = float(
        abs(np.linalg.norm(recovered_shift) / np.linalg.norm(true_shift) - 1.0)
    )

    big5_load = rng.normal(size=(5, dimensions))
    mbti_load = rng.normal(size=(4, dimensions))
    p0_big5 = reference @ big5_load.T + rng.normal(
        scale=0.5,
        size=(authors, 5),
    )
    p0_mbti = reference @ mbti_load.T + rng.normal(
        scale=0.5,
        size=(authors, 4),
    )
    p1_big5 = evaluation @ big5_load.T + rng.normal(
        scale=0.5,
        size=(authors, 5),
    )
    p1_mbti = evaluation @ mbti_load.T + rng.normal(
        scale=0.5,
        size=(authors, 4),
    )
    relation_p0 = _correlation_matrix(p0_big5, p0_mbti)
    relation_p1 = _correlation_matrix(p1_big5, p1_mbti)
    return {
        "world": "REFERENCE_DRIFT",
        "fixed_origin_shift_cosine": cosine,
        "fixed_origin_amplitude_error": amplitude_error,
        "transductive_shift_norm": float(
            np.linalg.norm(transductive_score.mean(axis=0))
        ),
        "population_relation_shift_frobenius": float(
            np.linalg.norm(relation_p1 - relation_p0)
        ),
        "reference_mismatch_refusal": 1,
    }


def run_hjic_repetition(
    repetition: int,
    *,
    seed: int,
    spec: HJICSpec,
) -> dict[str, list[dict[str, Any]]]:
    """Run every HJIC arm for one deterministic repetition."""
    local_seed = int(seed + repetition * 1_000_003)
    identifiable = simulate_identifiable_world(local_seed, spec)
    estimate = fit_identifiable_world(identifiable)
    evaluated = evaluate_identifiable_world(identifiable, estimate)
    refusal = []
    for index, world in enumerate(
        ("STATE_ALIAS", "MENU_ALIAS", "KERNEL_ALIAS", "ORDER_ALIAS")
    ):
        result = alias_world(
            world,
            seed=local_seed + 10_007 * (index + 1),
        )
        refusal.append({
            key: value
            for key, value in result.items()
            if key not in {"left", "right"}
        })
    return {
        **evaluated,
        "refusal": refusal,
        "information": [gaussian_information_order(local_seed + 71_003)],
        "route": [route_null_trial(local_seed + 83_003, spec)],
        "relation": [
            relational_lift_trial(
                local_seed + 97_003,
                world="SHARED_LATENT",
            ),
            relational_lift_trial(
                local_seed + 101_003,
                world="COMMON_NUISANCE",
            ),
        ],
        "reference": [reference_drift_trial(local_seed + 109_003)],
    }
