"""Designed response excitation and nested opportunity budgets for M4-C.3.3."""
from __future__ import annotations

from dataclasses import replace

import numpy as np
from scipy.special import expit, logit

from .m4_chart_ecology_contracts import (
    M4ChartEcologyObserved,
    M4ChartEcologyTruth,
)
from .m4_chart_ecology_generator import (
    M4ChartEcologySpec,
    _choice_probabilities,
    _condition_similarity,
    _ensure_nonempty,
)
from .m4_fisher_wiener_creation import _subset_panel
from .m4_opportunity_contracts import (
    M4OpportunityObserved,
    M4OpportunityPanel,
)


def balanced_response_probe(
    index: int,
    scale: np.ndarray,
    *,
    amplitude: float = 1.0,
) -> np.ndarray:
    """Cycle through zero-mean orthogonal signed response probes."""
    values = np.asarray(scale, dtype=float)
    if values.shape != (2,):
        raise ValueError("M4-C.3.3 requires two response dimensions")
    directions = np.asarray(
        [[1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0]]
    )
    return amplitude * values * directions[index % len(directions)]


def estimate_response_scale(
    observed: M4OpportunityObserved,
) -> np.ndarray:
    """Estimate a response-safe reference scale from natural pre-evaluation paths."""
    values = []
    for view in ("train", "test"):
        for role in ("calibration", "selection"):
            panel = getattr(observed, f"{view}_{role}")
            values.append(panel.response[:, :, 1:].reshape(-1, 2))
    scale = np.std(np.vstack(values), axis=0, ddof=1)
    return np.maximum(scale, 1e-6)


def _excited_path_panel(
    *,
    world: str,
    basis: np.ndarray,
    parameters: dict[str, np.ndarray],
    occasions: int,
    spec: M4ChartEcologySpec,
    seed: int,
    response_scale: np.ndarray,
    amplitude: float,
) -> M4OpportunityPanel:
    """Replay the registered path generator with a balanced response intervention."""
    rng = np.random.default_rng(seed)
    envelope_rng = np.random.default_rng(seed + 80_000_009)
    environment_rng = np.random.default_rng(seed + 90_000_011)
    authors = spec.mechanism_authors
    events = spec.events
    categories = spec.categories
    dimensions = spec.response_dimensions
    shape = (authors, occasions, events, categories)
    external = np.zeros(shape, dtype=bool)
    generated = np.zeros(shape, dtype=bool)
    menu = np.zeros(shape, dtype=bool)
    choice = np.zeros(shape[:-1], dtype=int)
    response = np.zeros(
        (authors, occasions, events + 1, dimensions),
        dtype=float,
    )
    history = np.zeros(
        (authors, occasions, events + 1, spec.history_dimensions),
        dtype=float,
    )
    duration = np.zeros(shape, dtype=float)
    environment = np.zeros(
        (authors, occasions, events, dimensions),
        dtype=float,
    )
    similarity = _condition_similarity(basis)
    source_alias = world == "hidden_opportunity_source_alias"
    matched_pair = world in {
        "linear_exogenous_selection",
        "endogenous_source_partition_matched",
    }
    external_rate = 0.45 if np.any(parameters["generated_base"]) else 0.62

    for occasion in range(occasions):
        shared_environment = np.zeros((events, dimensions))
        shared_environment[0] = environment_rng.normal(
            scale=0.4,
            size=dimensions,
        )
        for event in range(1, events):
            shared_environment[event] = (
                0.72 * shared_environment[event - 1]
                + environment_rng.normal(scale=0.28, size=dimensions)
            )
        environment[:, occasion] = shared_environment[None]
        for author in range(authors):
            if matched_pair:
                envelope_current = envelope_rng.random(categories) < 0.62
                if not np.any(envelope_current):
                    envelope_current[
                        int(envelope_rng.integers(categories))
                    ] = True
                if world == "endogenous_source_partition_matched":
                    generated_current = envelope_current & (
                        rng.random(categories)
                        < parameters["generated_base"][author]
                    )
                    external_current = envelope_current & ~generated_current
                else:
                    external_current = envelope_current.copy()
                    generated_current = np.zeros(categories, dtype=bool)
            else:
                external_current = rng.random(categories) < external_rate
                generated_current = (
                    external_current.copy()
                    if source_alias
                    else rng.random(categories)
                    < parameters["generated_base"][author]
                )
                _ensure_nonempty(external_current, generated_current, rng)
                if source_alias:
                    generated_current = external_current.copy()
            response[author, occasion, 0] = rng.normal(
                scale=0.28,
                size=dimensions,
            )
            recency = np.zeros(categories)
            for event in range(events):
                total = np.logical_or(external_current, generated_current)
                external[author, occasion, event] = external_current
                generated[author, occasion, event] = generated_current
                menu[author, occasion, event] = total
                duration_current = -spec.recency_decay * np.log(
                    np.maximum(recency, 1e-8)
                )
                duration[author, occasion, event] = np.minimum(
                    duration_current,
                    40.0,
                )
                probability = _choice_probabilities(
                    basis,
                    total,
                    parameters["selection"][author],
                )
                selected = int(rng.choice(categories + 1, p=probability))
                choice[author, occasion, event] = selected
                selected_basis = (
                    np.zeros(basis.shape[1])
                    if selected == 0
                    else basis[selected - 1]
                )
                response_next = (
                    parameters["response_transition"][author]
                    @ response[author, occasion, event]
                    + parameters["response_choice"][author] @ selected_basis
                    + 0.10 * history[author, occasion, event]
                    + rng.normal(scale=spec.response_noise, size=dimensions)
                )
                response_next = (
                    response_next
                    + balanced_response_probe(
                        occasion * events + event,
                        response_scale,
                        amplitude=amplitude,
                    )
                )
                response[author, occasion, event + 1] = response_next
                selected_history = (
                    np.zeros(spec.history_dimensions)
                    if selected == 0
                    else selected_basis[
                        1 : 1 + spec.history_dimensions
                    ]
                )
                history[author, occasion, event + 1] = (
                    0.64 * history[author, occasion, event]
                    + 0.22 * selected_history
                    + 0.12 * response_next
                )

                recency *= np.exp(-1.0 / spec.recency_decay)
                if selected > 0:
                    recency = np.maximum(recency, similarity[:, selected - 1])
                if matched_pair:
                    envelope_probability = np.clip(
                        0.24 * envelope_current.astype(float)
                        + 0.76 * 0.62,
                        0.02,
                        0.98,
                    )
                    envelope_next = (
                        envelope_rng.random(categories)
                        < envelope_probability
                    )
                    if not np.any(envelope_next):
                        envelope_next[
                            int(envelope_rng.integers(categories))
                        ] = True
                else:
                    condition_shift = (
                        0.025
                        * np.tanh(
                            basis[:, 1] * shared_environment[event, 0]
                        )
                        if basis.shape[1] > 1
                        else 0.0
                    )
                    persistence = parameters["external_persistence"][author]
                    external_probability = np.clip(
                        persistence * external_current.astype(float)
                        + (1.0 - persistence) * external_rate
                        + condition_shift,
                        0.02,
                        0.98,
                    )
                    external_next = (
                        rng.random(categories) < external_probability
                    )
                if source_alias:
                    generated_next = external_next.copy()
                else:
                    feedback = np.einsum(
                        "kp,pd,d->k",
                        basis,
                        parameters["creation"][author],
                        response_next,
                    )
                    gate = float(
                        history[author, occasion, event, 0] > 0.0
                    )
                    gated = gate * np.einsum(
                        "kp,pd,d->k",
                        basis,
                        parameters["gate"][author],
                        response_next,
                    )
                    generated_probability = expit(
                        logit(
                            np.clip(
                                parameters["generated_base"][author],
                                0.02,
                                0.98,
                            )
                        )
                        + 0.40
                        * (2.0 * generated_current.astype(float) - 1.0)
                        + 0.035 * np.tanh(duration_current / 4.0)
                        + feedback
                        + gated
                    )
                    generated_next = (
                        rng.random(categories) < generated_probability
                    )
                if world == "endogenous_source_partition_matched":
                    generated_next &= envelope_next
                    external_next = envelope_next & ~generated_next
                elif world == "linear_exogenous_selection":
                    external_next = envelope_next
                    generated_next = np.zeros(categories, dtype=bool)
                else:
                    _ensure_nonempty(external_next, generated_next, rng)
                if source_alias:
                    generated_next = external_next.copy()
                external_current = external_next
                generated_current = generated_next
                if matched_pair:
                    envelope_current = envelope_next
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


def build_excited_observed(
    observed: M4ChartEcologyObserved,
    truth: M4ChartEcologyTruth,
    spec: M4ChartEcologySpec,
    *,
    seed: int,
    amplitude: float = 1.0,
) -> M4ChartEcologyObserved:
    """Replace calibration/selection paths while preserving natural evaluation."""
    scale = estimate_response_scale(observed.ecology)
    panels: dict[str, M4OpportunityPanel] = {}
    role_occasions = {
        "calibration": spec.calibration_occasions,
        "selection": spec.selection_occasions,
    }
    for view_index, view in enumerate(("train", "test")):
        for role_index, (role, occasions) in enumerate(
            role_occasions.items()
        ):
            panels[f"{view}_{role}"] = _excited_path_panel(
                world=truth.world,
                basis=truth.oracle_basis[role],
                parameters=truth.author_parameters,
                occasions=occasions,
                spec=spec,
                seed=(
                    seed
                    + view_index * 10_000_019
                    + role_index * 1_000_003
                ),
                response_scale=scale,
                amplitude=amplitude,
            )
        panels[f"{view}_evaluation"] = getattr(
            observed.ecology,
            f"{view}_evaluation",
        )
    ecology = M4OpportunityObserved(
        **panels,
        design={
            **observed.ecology.design,
            "calibration_selection_response_excitation": True,
            "response_excitation_amplitude": amplitude,
            "response_excitation_scale": scale.tolist(),
            "evaluation_natural": True,
        },
    )
    return replace(observed, ecology=ecology)


def subset_opportunity_budget(
    observed: M4ChartEcologyObserved,
    *,
    calibration_occasions: int,
    selection_occasions: int,
) -> M4ChartEcologyObserved:
    """Take a strictly nested occasion prefix while preserving evaluation."""
    panels: dict[str, M4OpportunityPanel] = {}
    for view in ("train", "test"):
        calibration = getattr(
            observed.ecology,
            f"{view}_calibration",
        )
        selection = getattr(
            observed.ecology,
            f"{view}_selection",
        )
        if calibration_occasions > calibration.menu.shape[1]:
            raise ValueError("calibration budget exceeds generated maximum")
        if selection_occasions > selection.menu.shape[1]:
            raise ValueError("selection budget exceeds generated maximum")
        panels[f"{view}_calibration"] = _subset_panel(
            calibration,
            np.arange(calibration_occasions),
        )
        panels[f"{view}_selection"] = _subset_panel(
            selection,
            np.arange(selection_occasions),
        )
        panels[f"{view}_evaluation"] = getattr(
            observed.ecology,
            f"{view}_evaluation",
        )
    ecology = M4OpportunityObserved(
        **panels,
        design={
            **observed.ecology.design,
            "nested_calibration_occasions": calibration_occasions,
            "nested_selection_occasions": selection_occasions,
        },
    )
    return replace(observed, ecology=ecology)
