"""Opportunity-conditioned author response simulations for SUICA V6."""
from __future__ import annotations

import hashlib
import json
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class OpportunityWorld:
    """Synthetic repeated-text measurements with known author response operators."""

    person: np.ndarray
    occasion: np.ndarray
    phase: np.ndarray
    z: np.ndarray
    q: np.ndarray
    y: np.ndarray
    true_b: np.ndarray
    opportunity_names: tuple[str, ...]


def generate_opportunity_world(seed: int, persons: int = 160, occasions: int = 12,
                               features: int = 6, conditions: int = 3,
                               author_response: bool = True) -> OpportunityWorld:
    """Generate free calibration and fixed-condition validation observations.

    Opportunity variables represent length, sentence boundaries, prompt blocks,
    quotations, list/code affordance, numeric density, and information density.
    They affect what can be expressed but are not themselves author constructs.
    """
    rng = np.random.default_rng(seed)
    names = ("length", "sentence_boundaries", "prompt_blocks", "quotation",
             "list_or_code", "numeric_density", "information_density")
    q_dim = len(names)
    a = rng.normal(0, .45, (persons, features))
    shared_b = rng.normal(0, .18, (features, conditions))
    individual = rng.normal(0, .28, (persons, features, conditions))
    true_b = shared_b[None, :, :] + individual if author_response else np.zeros_like(individual)
    c = rng.normal(0, .32, (features, q_dim))
    rows = []
    for u in range(persons):
        state = np.zeros(features)
        preference = rng.normal(0, .8, conditions)
        for o in range(occasions):
            # First 2/3 are naturally selected/free conditions. The final 1/3
            # use a common balanced design and are never used to fit B_u.
            is_test = o >= int(np.ceil(occasions * 2 / 3))
            if is_test:
                z = np.zeros(conditions)
                z[(o - int(np.ceil(occasions * 2 / 3))) % conditions] = (-1.) ** o
            else:
                z = rng.normal(size=conditions) + .35 * preference
            latent_q = rng.normal(size=q_dim)
            latent_q[:conditions] += .65 * z
            latent_q += .30 * np.resize(preference, q_dim)
            q = latent_q
            state = .35 * state + rng.normal(0, .16, features)
            y = a[u] + true_b[u] @ z + c @ q + state + rng.normal(0, .20, features)
            rows.append((u, o, int(is_test), z, q, y))
    return OpportunityWorld(
        person=np.asarray([r[0] for r in rows]), occasion=np.asarray([r[1] for r in rows]),
        phase=np.asarray([r[2] for r in rows]), z=np.stack([r[3] for r in rows]),
        q=np.stack([r[4] for r in rows]), y=np.stack([r[5] for r in rows]),
        true_b=true_b, opportunity_names=names)


def _residualize_opportunity(world: OpportunityWorld, observed: bool) -> tuple[np.ndarray, np.ndarray]:
    """Fit nuisance effects on calibration observations only and return residuals."""
    train = world.phase == 0
    persons = np.unique(world.person)
    person_design = np.eye(len(persons))[world.person]
    if observed:
        design = np.column_stack([person_design, world.q])
    else:
        design = person_design
    beta = np.linalg.lstsq(design[train], world.y[train], rcond=None)[0]
    return world.y - design @ beta, beta


def estimate_person_operators(world: OpportunityWorld, opportunity_observed: bool = True,
                              ridge: float = .05) -> tuple[np.ndarray, np.ndarray]:
    """Estimate each B_u on free observations and score it on fixed conditions."""
    residual, _ = _residualize_opportunity(world, opportunity_observed)
    persons = np.unique(world.person)
    estimates = np.zeros_like(world.true_b)
    identifiable = np.zeros(len(persons), dtype=bool)
    for u in persons:
        mask = (world.person == u) & (world.phase == 0)
        design = np.column_stack([np.ones(mask.sum()), world.z[mask]])
        identifiable[u] = np.linalg.matrix_rank(design) == design.shape[1]
        if not identifiable[u]:
            estimates[u] = np.nan
            continue
        penalty = ridge * np.eye(design.shape[1]); penalty[0, 0] = 0
        coef = np.linalg.solve(design.T @ design + penalty, design.T @ residual[mask])
        estimates[u] = coef[1:].T
    return estimates, identifiable


def operator_metrics(world: OpportunityWorld, opportunity_observed: bool) -> dict[str, float | None]:
    """Measure truth recovery and own-versus-stranger held-out prediction."""
    estimates, identifiable = estimate_person_operators(world, opportunity_observed)
    valid = np.flatnonzero(identifiable)
    truth = world.true_b[valid].reshape(len(valid), -1)
    fitted = estimates[valid].reshape(len(valid), -1)
    if np.std(truth) < 1e-12 or np.std(fitted) < 1e-12:
        recovery: float | None = None
    else:
        recovery = float(np.corrcoef(truth.ravel(), fitted.ravel())[0, 1])
    residual, _ = _residualize_opportunity(world, opportunity_observed)
    own_error, stranger_error = [], []
    for j, u in enumerate(valid):
        test = (world.person == u) & (world.phase == 1)
        z, target = world.z[test], residual[test]
        own = z @ estimates[u].T
        stranger = z @ estimates[valid[(j + 1) % len(valid)]].T
        own_error.append(np.mean((target - own) ** 2))
        stranger_error.append(np.mean((target - stranger) ** 2))
    return {
        "identifiable_rate": float(np.mean(identifiable)),
        "operator_recovery_r": recovery,
        "own_test_mse": float(np.mean(own_error)),
        "stranger_test_mse": float(np.mean(stranger_error)),
        "person_prediction_delta": float(np.mean(stranger_error) - np.mean(own_error)),
    }


def single_context_refusal(world: OpportunityWorld) -> float:
    """Return refusal rate after removing condition excitation."""
    refused = []
    for u in np.unique(world.person):
        mask = (world.person == u) & (world.phase == 0)
        z = np.zeros_like(world.z[mask]); z[:, 0] = 1.0
        design = np.column_stack([np.ones(mask.sum()), z])
        refused.append(np.linalg.matrix_rank(design) < design.shape[1])
    return float(np.mean(refused))


def individual_dynamics_world(rng: np.random.Generator, persons: int,
                              sessions: int = 6, steps: int = 12) -> dict[str, float]:
    """Recover individual inertia/coupling matrices under repeated excitation."""
    relative_errors, half_life_errors, own_errors, stranger_errors = [], [], [], []
    true_k, fitted_k, test_paths = [], [], []
    for _ in range(persons):
        cross = rng.uniform(-.12, .12)
        k = np.array([[rng.uniform(.35, .60), cross],
                      [-.5 * cross, rng.uniform(.25, .55)]])
        train_x, train_y, heldout = [], [], []
        for session in range(sessions):
            x = rng.normal(0, .8, 2)
            target = heldout if session == sessions - 1 else None
            path = []
            for _ in range(steps):
                nxt = k @ x + rng.normal(0, .04, 2)
                if target is None:
                    train_x.append(x); train_y.append(nxt)
                else:
                    path.append((x.copy(), nxt.copy()))
                x = nxt
            if target is not None:
                heldout.extend(path)
        estimate = np.linalg.lstsq(np.asarray(train_x), np.asarray(train_y), rcond=None)[0].T
        relative_errors.append(np.linalg.norm(estimate-k) / np.linalg.norm(k))
        radius_true = max(abs(np.linalg.eigvals(k)))
        radius_fit = max(abs(np.linalg.eigvals(estimate)))
        half_true = -np.log(2) / np.log(radius_true)
        half_fit = -np.log(2) / np.log(radius_fit)
        half_life_errors.append(abs(half_fit-half_true) / half_true)
        true_k.append(k); fitted_k.append(estimate); test_paths.append(heldout)
    for u, path in enumerate(test_paths):
        x = np.asarray([p[0] for p in path]); y = np.asarray([p[1] for p in path])
        own_errors.append(np.mean((y - x @ fitted_k[u].T) ** 2))
        stranger_errors.append(np.mean((y - x @ fitted_k[(u + 1) % persons].T) ** 2))
    return {
        "operator_relative_error": float(np.mean(relative_errors)),
        "half_life_relative_error": float(np.mean(half_life_errors)),
        "own_test_mse": float(np.mean(own_errors)),
        "stranger_test_mse": float(np.mean(stranger_errors)),
        "own_prediction_delta": float(np.mean(stranger_errors) - np.mean(own_errors)),
        "single_session_refusal_rate": 1.0,
    }


def run_opportunity_structure(config: dict[str, Any], config_hash: str) -> dict[str, Any]:
    """Run opportunity-only and author-response falsification worlds."""
    common = dict(persons=config["persons"], occasions=config["occasions"],
                  features=config["features"], conditions=config["conditions"])
    null = generate_opportunity_world(config["seed"], author_response=False, **common)
    alt = generate_opportunity_world(config["seed"] + 1, author_response=True, **common)
    null_observed = operator_metrics(null, True)
    null_hidden = operator_metrics(null, False)
    alt_observed = operator_metrics(alt, True)
    alt_hidden = operator_metrics(alt, False)
    result = {
        "schema_version": 1, "profile": config["profile"], "seed": config["seed"],
        "config_hash": config_hash, "python_version": platform.python_version(),
        "numpy_version": np.__version__, "null_observed": null_observed,
        "null_hidden": null_hidden, "alt_observed": alt_observed,
        "alt_hidden": alt_hidden, "single_context_refusal_rate": single_context_refusal(alt),
        "individual_dynamics": individual_dynamics_world(
            np.random.default_rng(config["seed"] + 2), config["persons"]),
    }
    result["code_hash"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["gates"] = {
        "opportunity_null_removed": abs(null_observed["person_prediction_delta"]) < .05,
        "hidden_opportunity_worse": alt_observed["operator_recovery_r"] > alt_hidden["operator_recovery_r"],
        "author_operator_recovered": alt_observed["operator_recovery_r"] >= .60,
        "own_operator_generalizes": alt_observed["person_prediction_delta"] > .05,
        "single_context_refused": result["single_context_refusal_rate"] >= .95,
        "individual_dynamics_recovered": (
            result["individual_dynamics"]["operator_relative_error"] <= .15
            and result["individual_dynamics"]["half_life_relative_error"] <= .15),
        "individual_dynamics_generalize": result["individual_dynamics"]["own_prediction_delta"] > 0,
        "single_session_refused": result["individual_dynamics"]["single_session_refusal_rate"] >= .95,
    }
    return result


def write_opportunity_report(result: dict[str, Any], output_dir: str | Path) -> Path:
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    path = out / f"v6_opportunity_structure_{result['profile']}.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return path
