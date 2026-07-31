"""Synthetic worlds for M4-B endogenous opportunity ecology."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import expit, logit

from .m4_opportunity_contracts import (
    M4OpportunityObserved,
    M4OpportunityPanel,
    M4OpportunityTruth,
    validate_opportunity_observed,
)


WORLDS = (
    "null_exogenous",
    "exogenous_selection",
    "endogenous_creation_matched",
    "fast_return_equal_marginal",
    "slow_hysteresis_equal_marginal",
    "history_gated_ecology",
    "selection_creation_compensation",
    "hidden_opportunity_alias",
)

ACTIVE_MECHANISMS = {
    "null_exogenous": (),
    "exogenous_selection": ("selection",),
    "endogenous_creation_matched": ("creation",),
    "fast_return_equal_marginal": ("return",),
    "slow_hysteresis_equal_marginal": ("return", "hysteresis"),
    "history_gated_ecology": ("creation", "gate"),
    "selection_creation_compensation": ("selection", "creation"),
    "hidden_opportunity_alias": (),
}


@dataclass(frozen=True)
class M4OpportunitySpec:
    """Dimensions for the opportunity-ecology discovery battery."""

    authors: int = 32
    categories: int = 4
    response_dimensions: int = 2
    history_dimensions: int = 2
    calibration_occasions: int = 6
    selection_occasions: int = 3
    evaluation_occasions: int = 6
    events: int = 160
    response_noise: float = 0.16


def _grid(
    authors: int,
    low: float,
    high: float,
    *,
    seed: int,
) -> np.ndarray:
    values = np.linspace(low, high, authors)
    return values[np.random.default_rng(seed).permutation(authors)]


def _category_vectors(categories: int, dimensions: int) -> np.ndarray:
    if categories != 4 or dimensions != 2:
        raise ValueError("M4-B V1 requires K=4 and response dimension=2")
    return np.asarray([
        [1.0, 0.0],
        [0.0, 1.0],
        [-1.0, 0.0],
        [0.0, -1.0],
    ])


def _author_patterns(authors: int, categories: int) -> np.ndarray:
    base = np.asarray([1.0, 0.35, -0.35, -1.0])
    return np.stack([
        np.roll(base, author % categories)
        for author in range(authors)
    ])


def _world_parameters(
    world: str,
    spec: M4OpportunitySpec,
    *,
    seed: int,
) -> dict[str, np.ndarray]:
    authors = spec.authors
    categories = spec.categories
    dimensions = spec.response_dimensions
    vectors = _category_vectors(categories, dimensions)
    patterns = _author_patterns(authors, categories)
    strength = _grid(authors, 0.55, 1.05, seed=seed + 101)
    recovery = _grid(authors, 0.44, 0.76, seed=seed + 211)

    choice_preference = np.zeros((authors, categories))
    creation = np.zeros((authors, categories, dimensions))
    gate = np.zeros_like(creation)
    external_rate = np.full((authors, categories), 0.65)
    external_persistence = np.full((authors, categories), 0.24)
    generated_rate = np.zeros((authors, categories))
    generated_persistence = np.zeros((authors, categories))

    if world == "exogenous_selection":
        choice_preference = strength[:, None] * patterns
    elif world == "endogenous_creation_matched":
        external_rate.fill(0.45)
        generated_rate.fill((0.65 - 0.45) / (1.0 - 0.45))
        generated_persistence.fill(0.12)
        for author in range(authors):
            creation[author] = (
                1.35
                * strength[author]
                * np.roll(vectors, author % categories, axis=0)
            )
    elif world == "fast_return_equal_marginal":
        external_persistence[:] = (
            _grid(authors, 0.02, 0.12, seed=seed + 307)[:, None]
        )
    elif world == "slow_hysteresis_equal_marginal":
        external_persistence[:] = (
            _grid(authors, 0.68, 0.84, seed=seed + 307)[:, None]
        )
    elif world == "history_gated_ecology":
        external_rate.fill(0.45)
        generated_rate.fill((0.65 - 0.45) / (1.0 - 0.45))
        generated_persistence.fill(0.10)
        for author in range(authors):
            gate[author] = (
                1.90
                * strength[author]
                * np.roll(vectors, author % categories, axis=0)
            )
    elif world == "selection_creation_compensation":
        external_rate.fill(0.45)
        generated_rate.fill((0.65 - 0.45) / (1.0 - 0.45))
        generated_persistence.fill(0.10)
        choice_preference = 0.75 * strength[:, None] * patterns
        for author in range(authors):
            creation[author] = (
                -1.20
                * strength[author]
                * np.roll(vectors, author % categories, axis=0)
            )
    elif world in {
        "null_exogenous",
        "hidden_opportunity_alias",
    }:
        recovery.fill(0.62)
    else:
        raise ValueError(f"unsupported M4-B world: {world}")

    response_choice = np.broadcast_to(
        (0.46 * vectors.T)[None],
        (authors, dimensions, categories),
    ).copy()
    response_transition = np.stack([
        value * np.eye(dimensions)
        for value in recovery
    ])
    return {
        "choice_preference": choice_preference,
        "creation": creation,
        "gate": gate,
        "external_rate": external_rate,
        "external_persistence": external_persistence,
        "generated_rate": generated_rate,
        "generated_persistence": generated_persistence,
        "response_choice": response_choice,
        "response_transition": response_transition,
        "recovery": recovery,
    }


def _choice_probabilities(
    preference: np.ndarray,
    menu: np.ndarray,
    response: np.ndarray,
    history: np.ndarray,
    vectors: np.ndarray,
) -> np.ndarray:
    category_utility = (
        preference
        + 0.10 * (vectors @ response)
        + 0.06 * (vectors @ history[: vectors.shape[1]])
    )
    logits = np.concatenate([np.asarray([-0.85]), category_utility])
    allowed = np.concatenate([np.asarray([True]), menu])
    logits = np.where(allowed, logits, -1e9)
    logits -= np.max(logits)
    values = np.exp(logits)
    return values / values.sum()


def _external_next_probability(
    current: np.ndarray,
    rate: np.ndarray,
    persistence: np.ndarray,
    environment: np.ndarray,
    vectors: np.ndarray,
) -> np.ndarray:
    base = rate + persistence * (current.astype(float) - rate)
    perturbation = 0.025 * np.tanh(vectors @ environment)
    return np.clip(base + perturbation, 0.02, 0.98)


def _generated_next_probability(
    *,
    current: np.ndarray,
    base_rate: np.ndarray,
    persistence: np.ndarray,
    creation: np.ndarray,
    gate: np.ndarray,
    response: np.ndarray,
    history: np.ndarray,
    duration: np.ndarray,
) -> np.ndarray:
    if np.max(base_rate) <= 0.0:
        return np.zeros_like(base_rate)
    linear = (
        logit(np.clip(base_rate, 1e-4, 1.0 - 1e-4))
        + persistence * (2.0 * current.astype(float) - 1.0)
        + np.einsum("kd,d->k", creation, response)
        + (
            (history[0] > 0.0)
            * np.einsum("kd,d->k", gate, response)
        )
        + 0.035 * np.tanh(duration / 4.0)
    )
    return np.clip(expit(linear), 0.02, 0.98)


def _ensure_nonempty(
    external: np.ndarray,
    generated: np.ndarray,
    rng: np.random.Generator,
) -> None:
    if not np.any(np.logical_or(external, generated)):
        external[int(rng.integers(len(external)))] = True


def _panel(
    *,
    world: str,
    spec: M4OpportunitySpec,
    parameters: dict[str, np.ndarray],
    occasions: int,
    seed: int,
) -> M4OpportunityPanel:
    rng = np.random.default_rng(seed)
    authors = spec.authors
    events = spec.events
    categories = spec.categories
    response_dimensions = spec.response_dimensions
    history_dimensions = spec.history_dimensions
    vectors = _category_vectors(categories, response_dimensions)

    shape = (authors, occasions, events, categories)
    external = np.zeros(shape, dtype=bool)
    generated = np.zeros(shape, dtype=bool)
    menu = np.zeros(shape, dtype=bool)
    choice = np.zeros(shape[:-1], dtype=int)
    response = np.zeros(
        (authors, occasions, events + 1, response_dimensions),
        dtype=float,
    )
    history = np.zeros(
        (authors, occasions, events + 1, history_dimensions),
        dtype=float,
    )
    duration = np.zeros(shape, dtype=float)
    environment = np.zeros(
        (authors, occasions, events, response_dimensions),
        dtype=float,
    )
    alias = world == "hidden_opportunity_alias"

    for occasion in range(occasions):
        shared_environment = np.zeros(
            (events, response_dimensions),
            dtype=float,
        )
        shared_environment[0] = rng.normal(scale=0.45, size=response_dimensions)
        for event in range(1, events):
            shared_environment[event] = (
                0.72 * shared_environment[event - 1]
                + rng.normal(scale=0.32, size=response_dimensions)
            )
        environment[:, occasion] = shared_environment[None]

        for author in range(authors):
            external_current = (
                rng.random(categories)
                < parameters["external_rate"][author]
            )
            if alias:
                generated_current = external_current.copy()
            else:
                generated_current = (
                    rng.random(categories)
                    < parameters["generated_rate"][author]
                )
            _ensure_nonempty(external_current, generated_current, rng)
            if alias:
                generated_current = external_current.copy()
            response[author, occasion, 0] = rng.normal(
                scale=0.30,
                size=response_dimensions,
            )
            history[author, occasion, 0] = rng.normal(
                scale=0.08,
                size=history_dimensions,
            )
            duration_current = rng.integers(0, 4, size=categories).astype(float)

            for event in range(events):
                total_menu = np.logical_or(
                    external_current,
                    generated_current,
                )
                external[author, occasion, event] = external_current
                generated[author, occasion, event] = generated_current
                menu[author, occasion, event] = total_menu
                duration[author, occasion, event] = duration_current

                probabilities = _choice_probabilities(
                    parameters["choice_preference"][author],
                    total_menu,
                    response[author, occasion, event],
                    history[author, occasion, event],
                    vectors,
                )
                current_choice = int(
                    rng.choice(categories + 1, p=probabilities)
                )
                choice[author, occasion, event] = current_choice
                choice_vector = (
                    np.zeros(response_dimensions)
                    if current_choice == 0
                    else parameters["response_choice"][
                        author, :, current_choice - 1
                    ]
                )
                response_next = (
                    parameters["response_transition"][author]
                    @ response[author, occasion, event]
                    + choice_vector
                    + 0.10 * history[author, occasion, event]
                    + rng.normal(
                        scale=spec.response_noise,
                        size=response_dimensions,
                    )
                )
                response[author, occasion, event + 1] = response_next
                choice_history = (
                    np.zeros(history_dimensions)
                    if current_choice == 0
                    else vectors[current_choice - 1, :history_dimensions]
                )
                history[author, occasion, event + 1] = (
                    0.64 * history[author, occasion, event]
                    + 0.22 * choice_history
                    + 0.12 * response_next[:history_dimensions]
                )

                duration_current = duration_current + 1.0
                if current_choice > 0:
                    duration_current[current_choice - 1] = 0.0
                external_probability = _external_next_probability(
                    external_current,
                    parameters["external_rate"][author],
                    parameters["external_persistence"][author],
                    shared_environment[event],
                    vectors,
                )
                external_next = rng.random(categories) < external_probability
                if alias:
                    generated_next = external_next.copy()
                else:
                    generated_probability = _generated_next_probability(
                        current=generated_current,
                        base_rate=parameters["generated_rate"][author],
                        persistence=parameters["generated_persistence"][author],
                        creation=parameters["creation"][author],
                        gate=parameters["gate"][author],
                        response=response_next,
                        history=history[author, occasion, event],
                        duration=duration_current,
                    )
                    generated_next = (
                        rng.random(categories) < generated_probability
                    )
                _ensure_nonempty(external_next, generated_next, rng)
                if alias:
                    generated_next = external_next.copy()
                external_current = external_next
                generated_current = generated_next

    return M4OpportunityPanel(
        external_menu=external,
        generated_menu=generated,
        menu=menu,
        choice=choice,
        response=response,
        history=history,
        duration=duration,
        environment=environment,
    )


def _choice_menu_operator(preference: np.ndarray) -> np.ndarray:
    categories = len(preference)
    all_menu = np.ones(categories, dtype=bool)
    zero = np.zeros(2)
    vectors = _category_vectors(categories, 2)
    baseline = _choice_probabilities(
        preference,
        all_menu,
        zero,
        zero,
        vectors,
    )[1:]
    operator = np.empty((categories, categories))
    for category in range(categories):
        reduced = all_menu.copy()
        reduced[category] = False
        counterfactual = _choice_probabilities(
            preference,
            reduced,
            zero,
            zero,
            vectors,
        )[1:]
        operator[:, category] = baseline - counterfactual
    return operator


def _truth_parameters(
    parameters: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    authors, categories = parameters["choice_preference"].shape
    loop = np.empty((authors, categories, categories))
    jacobian = np.empty_like(loop)
    rho = np.empty((authors, 1))
    return_time = np.empty((authors, 1))
    recovery_time = np.empty((authors, 1))
    for author in range(authors):
        choice_operator = _choice_menu_operator(
            parameters["choice_preference"][author]
        )
        generated_rate = parameters["generated_rate"][author]
        external_rate = parameters["external_rate"][author]
        creation = parameters["creation"][author]
        gate = 0.5 * parameters["gate"][author]
        opportunity_response = (
            (1.0 - external_rate)[:, None]
            * (generated_rate * (1.0 - generated_rate))[:, None]
            * (creation + gate)
        )
        current_loop = (
            opportunity_response
            @ parameters["response_choice"][author]
            @ choice_operator
        )
        generated_persistence = (
            2.0
            * generated_rate
            * (1.0 - generated_rate)
            * parameters["generated_persistence"][author]
        )
        persistence = 0.5 * (
            parameters["external_persistence"][author]
            + generated_persistence
        )
        current_jacobian = np.diag(persistence) + current_loop
        loop[author] = current_loop
        jacobian[author] = current_jacobian
        rho[author, 0] = float(
            np.max(np.abs(np.linalg.eigvals(current_jacobian)))
        )
        stationary_rate = np.mean(external_rate)
        persistence_rate = np.mean(
            parameters["external_persistence"][author]
        )
        return_time[author, 0] = 1.0 / max(
            stationary_rate * (1.0 - persistence_rate),
            1e-6,
        )
        recovery_time[author, 0] = (
            np.log(0.5)
            / np.log(max(parameters["recovery"][author], 1e-6))
        )
    return {
        "selection": parameters["choice_preference"],
        "creation": parameters["creation"].reshape(authors, -1),
        "gate": parameters["gate"].reshape(authors, -1),
        "loop": loop.reshape(authors, -1),
        "jacobian": jacobian.reshape(authors, -1),
        "rho": rho,
        "return_time": return_time,
        "recovery_time": recovery_time,
    }


def generate_m4_opportunity_world(
    *,
    world: str,
    spec: M4OpportunitySpec,
    seed: int,
) -> tuple[M4OpportunityObserved, M4OpportunityTruth]:
    """Generate independent three-role opportunity-ecology panels."""
    if world not in WORLDS:
        raise ValueError(f"unsupported M4-B world: {world}")
    parameters = _world_parameters(world, spec, seed=seed + 17_021)
    panels: dict[str, M4OpportunityPanel] = {}
    role_occasions = {
        "calibration": spec.calibration_occasions,
        "selection": spec.selection_occasions,
        "evaluation": spec.evaluation_occasions,
    }
    for view_index, view in enumerate(("train", "test")):
        for role_index, (role, occasions) in enumerate(
            role_occasions.items()
        ):
            panels[f"{view}_{role}"] = _panel(
                world=world,
                spec=spec,
                parameters=parameters,
                occasions=occasions,
                seed=(
                    seed
                    + view_index * 10_000_019
                    + role_index * 1_000_003
                ),
            )
    observed = M4OpportunityObserved(
        train_calibration=panels["train_calibration"],
        train_selection=panels["train_selection"],
        train_evaluation=panels["train_evaluation"],
        test_calibration=panels["test_calibration"],
        test_selection=panels["test_selection"],
        test_evaluation=panels["test_evaluation"],
        design={
            "categories": spec.categories,
            "response_dimensions": spec.response_dimensions,
            "history_dimensions": spec.history_dimensions,
            "role_separation": (
                "calibration -> selection -> untouched evaluation"
            ),
            "world_hidden_from_estimator": True,
        },
    )
    validate_opportunity_observed(observed)
    truth = M4OpportunityTruth(
        world=world,
        active_mechanisms=ACTIVE_MECHANISMS[world],
        author_parameters=_truth_parameters(parameters),
        alias=world == "hidden_opportunity_alias",
        matched_group=(
            "selection_vs_creation"
            if world in {
                "exogenous_selection",
                "endogenous_creation_matched",
            }
            else (
                "fast_vs_slow_return"
                if world in {
                    "fast_return_equal_marginal",
                    "slow_hysteresis_equal_marginal",
                }
                else None
            )
        ),
    )
    return observed, truth
