"""Planted-world identification experiments for SUICA V8.

The simulator separates stable author configuration, session deviation,
menu-conditioned choice, fixed-condition response, and interaction-history
response.  It also generates wrong-design worlds in which the corresponding
component must be refused.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .joint_process import same_author_auc


COMPONENTS = ("theta", "state", "choice", "response", "history")


@dataclass(frozen=True)
class SimulationSpec:
    """Dimensions and support for one planted measurement world."""

    persons: int = 400
    sessions: int = 4
    units_per_session: int = 8
    dimensions: int = 6
    condition_dimensions: int = 3
    history_dimensions: int = 2
    choices: int = 4
    choice_opportunities: int = 24
    choice_smoothing: float = 1.5
    noise_sd: float = 0.30
    ridge: float = 0.25


def _corr(left: np.ndarray, right: np.ndarray) -> float:
    a = np.asarray(left, dtype=float).ravel()
    b = np.asarray(right, dtype=float).ravel()
    finite = np.isfinite(a) & np.isfinite(b)
    if finite.sum() < 4 or np.std(a[finite]) < 1e-12 or np.std(b[finite]) < 1e-12:
        return float("nan")
    return float(np.corrcoef(a[finite], b[finite])[0, 1])


def _distance_geometry_correlation(left: np.ndarray, right: np.ndarray) -> float:
    a = np.asarray(left, dtype=float)
    b = np.asarray(right, dtype=float)
    if a.shape != b.shape or a.ndim != 2 or len(a) < 4:
        return float("nan")
    da = np.sum((a[:, None, :] - a[None, :, :]) ** 2, axis=2)
    db = np.sum((b[:, None, :] - b[None, :, :]) ** 2, axis=2)
    upper = np.triu_indices(len(a), 1)
    return _corr(da[upper], db[upper])


def _condition_basis(dimensions: int) -> np.ndarray:
    """Return four balanced fixed conditions with zero column means."""
    if dimensions != 3:
        rng = np.random.default_rng(8103 + dimensions)
        values = rng.normal(size=(4, dimensions))
        return values - values.mean(axis=0, keepdims=True)
    return np.asarray([
        [-1.0, -1.0, -1.0],
        [-1.0, 1.0, 1.0],
        [1.0, -1.0, 1.0],
        [1.0, 1.0, -1.0],
    ]) / np.sqrt(3.0)


def simulate_world(
    *,
    seed: int,
    world: str,
    spec: SimulationSpec,
) -> dict[str, Any]:
    """Generate one independent or deliberately non-identifiable world."""
    rng = np.random.default_rng(seed)
    u, t, n, p = (
        int(spec.persons),
        int(spec.sessions),
        int(spec.units_per_session),
        int(spec.dimensions),
    )
    if world == "single_occasion":
        t = 1
    coupled = world == "identified_coupled"
    null = world == "null_components"

    theta = np.zeros((u, p)) if null else rng.normal(size=(u, p))
    state = np.zeros((u, t, p))
    if not null:
        innovations = rng.normal(scale=0.55, size=(u, t, p))
        state[:, 0] = innovations[:, 0]
        for session in range(1, t):
            state[:, session] = 0.55 * state[:, session - 1] + innovations[:, session]
        state -= state.mean(axis=1, keepdims=True)

    condition_basis = _condition_basis(spec.condition_dimensions)
    base_response = rng.normal(scale=0.25, size=(spec.condition_dimensions, p))
    response = np.zeros((u, spec.condition_dimensions, p)) if null else (
        base_response[None, :, :] + rng.normal(scale=0.40, size=(u, spec.condition_dimensions, p))
    )
    history = np.zeros((u, spec.history_dimensions, p)) if null else rng.normal(
        scale=0.45, size=(u, spec.history_dimensions, p)
    )
    choice_logits = np.zeros((u, spec.choices)) if null else rng.normal(scale=0.9, size=(u, spec.choices))
    if coupled and not null:
        choice_logits[:, : min(p, spec.choices)] += 0.55 * theta[:, : min(p, spec.choices)]
        response[:, 0, :] += 0.35 * theta
        history[:, 0, :] += 0.30 * theta
        state += 0.25 * theta[:, None, :] * np.linspace(-1.0, 1.0, t)[None, :, None]
        state -= state.mean(axis=1, keepdims=True)

    rows = u * t * n
    author_index = np.repeat(np.arange(u), t * n)
    session_index = np.tile(np.repeat(np.arange(t), n), u)
    within_index = np.tile(np.arange(n), u * t)
    condition_index = within_index % 4
    if world == "nonrandom_condition":
        condition_index = np.repeat(np.arange(u) % 4, t * n)
    condition_x = condition_basis[condition_index]
    history_x = rng.normal(size=(rows, spec.history_dimensions))
    if world == "hidden_history":
        history_observed = False
    else:
        history_observed = True

    systematic = (
        theta[author_index]
        + state[author_index, session_index]
        + np.einsum("ri,rip->rp", condition_x, response[author_index])
        + np.einsum("ri,rip->rp", history_x, history[author_index])
    )
    observed = systematic + rng.normal(scale=spec.noise_sd, size=systematic.shape)
    if world == "model_drift":
        transform, _ = np.linalg.qr(rng.normal(size=(p, p)))
        drift_mask = session_index >= max(1, t // 2)
        observed[drift_mask] = observed[drift_mask] @ transform

    probabilities = np.exp(choice_logits - choice_logits.max(axis=1, keepdims=True))
    probabilities /= probabilities.sum(axis=1, keepdims=True)
    choice_count = int(spec.choice_opportunities)
    choice_draws = np.vstack([
        rng.choice(spec.choices, size=choice_count, p=probabilities[author])
        for author in range(u)
    ])
    return {
        "world": world,
        "truth": {
            "theta": theta,
            "state": state,
            "choice_probabilities": probabilities,
            "response": response,
            "history": history,
        },
        "data": {
            "z": observed,
            "systematic": systematic,
            "author": author_index,
            "session": session_index,
            "within": within_index,
            "condition": condition_x,
            "history": history_x,
            "choice_draws": choice_draws,
        },
        "design": {
            "sessions": t,
            "menu_observed": world != "missing_menu",
            "condition_randomized": world != "nonrandom_condition",
            "history_observed": history_observed,
            "history_randomized": True,
            "representation_stable": world != "model_drift",
        },
    }


def component_status(world: dict[str, Any]) -> dict[str, str]:
    """Apply component-specific identification rules before estimation."""
    design = world["design"]
    if not design["representation_stable"]:
        return {component: "REFUSE_MODEL_DRIFT" for component in COMPONENTS}
    if int(design["sessions"]) < 2:
        return {component: "REFUSE_SINGLE_OCCASION" for component in COMPONENTS}
    status = {component: "READY" for component in COMPONENTS}
    if not design["menu_observed"]:
        status["choice"] = "REFUSE_MENU_UNOBSERVED"
    if not design["condition_randomized"]:
        status["response"] = "REFUSE_CONDITION_NOT_RANDOMIZED"
    if not design["history_observed"]:
        status["history"] = "REFUSE_HISTORY_UNOBSERVED"
    if not design["history_randomized"]:
        status["history"] = "REFUSE_HISTORY_NOT_RANDOMIZED"
    return status


def estimate_world(world: dict[str, Any], *, ridge: float) -> dict[str, Any]:
    """Estimate only components licensed by the observed design."""
    status = component_status(world)
    data = world["data"]
    z = np.asarray(data["z"], dtype=float)
    authors = np.asarray(data["author"], dtype=int)
    sessions = np.asarray(data["session"], dtype=int)
    condition = np.asarray(data["condition"], dtype=float)
    history_x = np.asarray(data["history"], dtype=float)
    person_count = int(authors.max()) + 1
    session_count = int(sessions.max()) + 1
    p = z.shape[1]
    response_hat = np.full((person_count, condition.shape[1], p), np.nan)
    history_hat = np.full((person_count, history_x.shape[1], p), np.nan)
    theta_hat = np.full((person_count, p), np.nan)
    state_hat = np.full((person_count, session_count, p), np.nan)

    if status["theta"] == "READY":
        for author in range(person_count):
            mask = authors == author
            za = z[mask]
            xa = condition[mask]
            ha = history_x[mask]
            sa = sessions[mask]
            # Remove each session mean before estimating within-session response.
            zc = za.copy()
            xc = xa.copy()
            hc = ha.copy()
            for session in range(session_count):
                local = sa == session
                zc[local] -= zc[local].mean(axis=0, keepdims=True)
                xc[local] -= xc[local].mean(axis=0, keepdims=True)
                hc[local] -= hc[local].mean(axis=0, keepdims=True)
            columns: list[np.ndarray] = []
            response_width = 0
            history_width = 0
            if status["response"] == "READY":
                columns.append(xc)
                response_width = xc.shape[1]
            if status["history"] == "READY":
                columns.append(hc)
                history_width = hc.shape[1]
            if columns:
                design = np.hstack(columns)
                gram = design.T @ design + float(ridge) * np.eye(design.shape[1])
                coef = np.linalg.solve(gram, design.T @ zc)
            else:
                coef = np.empty((0, p))
            offset = 0
            if response_width:
                response_hat[author] = coef[offset:offset + response_width]
                offset += response_width
            if history_width:
                history_hat[author] = coef[offset:offset + history_width]
            residual = za.copy()
            if response_width:
                residual -= xa @ response_hat[author]
            if history_width:
                residual -= ha @ history_hat[author]
            theta_hat[author] = residual.mean(axis=0)
            for session in range(session_count):
                local = sa == session
                state_hat[author, session] = residual[local].mean(axis=0) - theta_hat[author]

    choice_hat = np.full_like(world["truth"]["choice_probabilities"], np.nan)
    if status["choice"] == "READY":
        draws = np.asarray(data["choice_draws"], dtype=int)
        train_width = draws.shape[1] // 2
        alpha = float(world.get("choice_smoothing", 1.5))
        for author in range(person_count):
            counts = np.bincount(draws[author, :train_width], minlength=choice_hat.shape[1])
            choice_hat[author] = (counts + alpha) / (train_width + alpha * choice_hat.shape[1])

    return {
        "status": status,
        "theta": theta_hat,
        "state": state_hat,
        "choice_probabilities": choice_hat,
        "response": response_hat,
        "history": history_hat,
    }


def _log_loss(probabilities: np.ndarray, choices: np.ndarray) -> float:
    rows = np.arange(len(choices))
    return float(-np.mean(np.log(np.clip(probabilities[rows, choices], 1e-12, 1.0))))


def evaluate_world(world: dict[str, Any], estimate: dict[str, Any]) -> dict[str, Any]:
    """Calculate recovery, held-out skill, cross-talk, and null controls."""
    truth = world["truth"]
    data = world["data"]
    status = estimate["status"]
    result: dict[str, Any] = {
        "world": world["world"],
        **{f"{name}_status": status[name] for name in COMPONENTS},
    }
    if status["theta"] == "READY":
        result["theta_geometry_r"] = _distance_geometry_correlation(
            truth["theta"], estimate["theta"]
        )
        z = np.asarray(data["z"], dtype=float)
        authors = np.asarray(data["author"], dtype=int)
        sessions = np.asarray(data["session"], dtype=int)
        session_count = int(world["design"]["sessions"])
        split = max(1, session_count // 2)
        left = np.vstack([z[(authors == u) & (sessions < split)].mean(axis=0) for u in range(len(truth["theta"]))])
        right = np.vstack([z[(authors == u) & (sessions >= split)].mean(axis=0) for u in range(len(truth["theta"]))])
        result["theta_same_author_auc"] = same_author_auc(left, right)
        result["state_r"] = _corr(truth["state"], estimate["state"])
        true_share = float(np.var(truth["state"]) / max(np.var(data["systematic"]), 1e-12))
        estimated_share = float(np.nanvar(estimate["state"]) / max(np.var(data["z"]), 1e-12))
        result["state_variance_share_abs_error"] = abs(true_share - estimated_share)
    if status["choice"] == "READY":
        result["choice_probability_r"] = _corr(
            truth["choice_probabilities"], estimate["choice_probabilities"]
        )
        draws = np.asarray(data["choice_draws"], dtype=int)
        test = draws[:, draws.shape[1] // 2:]
        estimate_rows = np.repeat(estimate["choice_probabilities"], test.shape[1], axis=0)
        population = np.nanmean(estimate["choice_probabilities"], axis=0)
        population_rows = np.repeat(population[None, :], len(estimate_rows), axis=0)
        flat_choices = test.reshape(-1)
        model_loss = _log_loss(estimate_rows, flat_choices)
        population_loss = _log_loss(population_rows, flat_choices)
        result["choice_logloss_skill"] = float(1.0 - model_loss / population_loss)
    if status["response"] == "READY":
        result["response_operator_r"] = _corr(truth["response"], estimate["response"])
        true_effect = np.einsum(
            "ri,rip->rp",
            np.asarray(data["condition"], dtype=float),
            truth["response"][np.asarray(data["author"], dtype=int)],
        )
        estimated_effect = np.einsum(
            "ri,rip->rp",
            np.asarray(data["condition"], dtype=float),
            estimate["response"][np.asarray(data["author"], dtype=int)],
        )
        denominator = float(np.sum((true_effect - true_effect.mean(axis=0)) ** 2))
        result["response_heldout_r2"] = float(
            1.0 - np.sum((true_effect - estimated_effect) ** 2) / max(denominator, 1e-12)
        )
        own = np.mean((truth["response"] - estimate["response"]) ** 2)
        stranger = np.mean((truth["response"] - np.roll(estimate["response"], 1, axis=0)) ** 2)
        result["response_own_vs_stranger_delta_mse"] = float(stranger - own)
    if status["history"] == "READY":
        result["history_operator_r"] = _corr(truth["history"], estimate["history"])
        true_effect = np.einsum(
            "ri,rip->rp",
            np.asarray(data["history"], dtype=float),
            truth["history"][np.asarray(data["author"], dtype=int)],
        )
        estimated_effect = np.einsum(
            "ri,rip->rp",
            np.asarray(data["history"], dtype=float),
            estimate["history"][np.asarray(data["author"], dtype=int)],
        )
        denominator = float(np.sum((true_effect - true_effect.mean(axis=0)) ** 2))
        result["history_heldout_r2"] = float(
            1.0 - np.sum((true_effect - estimated_effect) ** 2) / max(denominator, 1e-12)
        )

    # Anonymous scalar projections quantify independent-world cross-talk only.
    if all(status[name] == "READY" for name in COMPONENTS) and world["world"] != "null_components":
        truth_scores = {
            "theta": truth["theta"][:, 0],
            "state": truth["state"][:, 0, 0] - truth["state"][:, -1, 0],
            "choice": truth["choice_probabilities"][:, 0] - truth["choice_probabilities"][:, 1],
            "response": truth["response"][:, 0, 0],
            "history": truth["history"][:, 0, 0],
        }
        estimate_scores = {
            "theta": estimate["theta"][:, 0],
            "state": estimate["state"][:, 0, 0] - estimate["state"][:, -1, 0],
            "choice": estimate["choice_probabilities"][:, 0] - estimate["choice_probabilities"][:, 1],
            "response": estimate["response"][:, 0, 0],
            "history": estimate["history"][:, 0, 0],
        }
        off_target = []
        margins = []
        for target in COMPONENTS:
            target_alignment = abs(_corr(estimate_scores[target], truth_scores[target]))
            target_off = [
                abs(_corr(estimate_scores[target], truth_scores[source]))
                for source in COMPONENTS
                if target != source
            ]
            off_target.extend(target_off)
            margins.append(target_alignment - max(target_off))
        result["max_off_target_abs_r"] = float(np.nanmax(off_target))
        result["min_target_alignment_minus_crosstalk"] = float(np.nanmin(margins))
    return result


def run_simulation_repetition(
    *,
    seed: int,
    world: str,
    spec: SimulationSpec,
) -> dict[str, Any]:
    """Generate, estimate, and evaluate one planted world."""
    generated = simulate_world(seed=seed, world=world, spec=spec)
    generated["choice_smoothing"] = float(spec.choice_smoothing)
    estimated = estimate_world(generated, ridge=spec.ridge)
    result = evaluate_world(generated, estimated)
    result["seed"] = int(seed)
    return result
