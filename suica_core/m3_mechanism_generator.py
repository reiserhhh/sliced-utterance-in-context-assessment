"""Synthetic mechanism worlds between microscopic events and mesoscopic authors.

Each world isolates a different author-level object while holding simpler
summaries uninformative where possible. The estimator sees only event vectors,
condition vectors, and partner vectors; hidden states and planted parameters
remain in the truth packet.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .m3_mechanism_contracts import (
    M3MechanismObserved,
    M3MechanismTruth,
)


@dataclass(frozen=True)
class M3MechanismWorldSpec:
    """Dimensions and signal strengths for one mechanism-atlas world."""

    authors: int = 36
    occasions: int = 6
    events: int = 64
    response_dimensions: int = 3
    condition_dimensions: int = 3
    noise: float = 0.16


_EXPECTED_FAMILY = {
    "density_state_distribution": "distribution_kme",
    "conditional_response_operator": "conditional_operator",
    "metastable_slow_mode": "koopman_spectrum",
    "interactional_alignment": "interaction_coupling",
    "higher_order_path": "higher_order_path",
    "opportunity_only": "opportunity_profile",
    "mixed_superposition": "union",
    "null_author": None,
}


def _rotation_z(theta: float, dimensions: int) -> np.ndarray:
    matrix = np.eye(dimensions)
    cosine = float(np.cos(theta))
    sine = float(np.sin(theta))
    matrix[:2, :2] = np.asarray([
        [cosine, -sine],
        [sine, cosine],
    ])
    if dimensions >= 3:
        tilt = 0.35 * theta
        cosine = float(np.cos(tilt))
        sine = float(np.sin(tilt))
        x_rotation = np.eye(dimensions)
        x_rotation[1:3, 1:3] = np.asarray([
            [cosine, -sine],
            [sine, cosine],
        ])
        matrix = x_rotation @ matrix
    return matrix


def _binary_markov(
    rng: np.random.Generator,
    shape: tuple[int, int, int],
    persistence: np.ndarray,
) -> np.ndarray:
    authors, occasions, events = shape
    values = np.empty(shape, dtype=float)
    values[:, :, 0] = rng.choice((-1.0, 1.0), size=(authors, occasions))
    for event in range(1, events):
        keep = rng.random((authors, occasions)) < persistence[:, None]
        values[:, :, event] = np.where(
            keep,
            values[:, :, event - 1],
            -values[:, :, event - 1],
        )
    return values


def _lag_two_process(
    rng: np.random.Generator,
    shape: tuple[int, int, int],
    persistence: np.ndarray,
) -> np.ndarray:
    authors, occasions, events = shape
    values = np.empty(shape, dtype=float)
    values[:, :, :2] = rng.choice(
        (-1.0, 1.0),
        size=(authors, occasions, 2),
    )
    for event in range(2, events):
        keep = rng.random((authors, occasions)) < persistence[:, None]
        values[:, :, event] = np.where(
            keep,
            values[:, :, event - 2],
            -values[:, :, event - 2],
        )
    return values


def _density_response(
    rng: np.random.Generator,
    spec: M3MechanismWorldSpec,
    mixing: np.ndarray,
) -> np.ndarray:
    shape = (spec.authors, spec.occasions, spec.events)
    choose_first = rng.random(shape) < mixing[:, None, None]
    signs = rng.choice((-1.0, 1.0), size=shape)
    response = np.zeros(shape + (spec.response_dimensions,), dtype=float)
    response[..., 0] = signs * choose_first
    response[..., 1] = signs * (~choose_first)
    return response + rng.normal(scale=spec.noise, size=response.shape)


def _state_response(
    state: np.ndarray,
    spec: M3MechanismWorldSpec,
    rng: np.random.Generator,
    *,
    scale: float = 1.0,
) -> np.ndarray:
    response = np.zeros(state.shape + (spec.response_dimensions,), dtype=float)
    response[..., 0] = scale * state
    if spec.response_dimensions > 1:
        response[..., 1] = 0.25 * scale * state
    return response + rng.normal(scale=spec.noise, size=response.shape)


def _panel(
    *,
    world: str,
    rng: np.random.Generator,
    spec: M3MechanismWorldSpec,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    shape = (spec.authors, spec.occasions, spec.events)
    condition = rng.normal(size=shape + (spec.condition_dimensions,))
    partner = rng.normal(size=shape + (spec.response_dimensions,))
    theta = np.linspace(
        -0.85 * np.pi,
        0.85 * np.pi,
        spec.authors,
        endpoint=True,
    )

    if world == "density_state_distribution":
        parameter = np.linspace(0.12, 0.88, spec.authors)[:, None]
        response = _density_response(rng, spec, parameter[:, 0])
    elif world == "conditional_response_operator":
        operators = np.asarray([
            _rotation_z(value, spec.response_dimensions)
            for value in theta
        ])
        usable = min(spec.condition_dimensions, spec.response_dimensions)
        response = np.einsum(
            "u...d,upd->u...p",
            condition[..., :usable],
            operators[:, :, :usable],
        )
        response += rng.normal(scale=spec.noise, size=response.shape)
        parameter = operators.reshape(spec.authors, -1)
    elif world == "metastable_slow_mode":
        persistence = np.linspace(0.56, 0.96, spec.authors)
        state = _binary_markov(rng, shape, persistence)
        response = _state_response(state, spec, rng)
        parameter = persistence[:, None]
    elif world == "interactional_alignment":
        operators = np.asarray([
            _rotation_z(value, spec.response_dimensions)
            for value in theta
        ])
        response = np.einsum("u...d,upd->u...p", partner, operators)
        response += rng.normal(scale=spec.noise, size=response.shape)
        parameter = operators.reshape(spec.authors, -1)
    elif world == "higher_order_path":
        persistence = np.linspace(0.56, 0.96, spec.authors)
        state = _lag_two_process(rng, shape, persistence)
        response = _state_response(state, spec, rng)
        parameter = persistence[:, None]
    elif world == "opportunity_only":
        angle = np.linspace(0.0, 2.0 * np.pi, spec.authors, endpoint=False)
        opportunity = np.zeros((spec.authors, spec.condition_dimensions))
        opportunity[:, 0] = 1.10 * np.cos(angle)
        opportunity[:, 1] = 1.10 * np.sin(angle)
        condition += opportunity[:, None, None]
        common = np.zeros(
            (spec.response_dimensions, spec.condition_dimensions),
            dtype=float,
        )
        diagonal = min(spec.response_dimensions, spec.condition_dimensions)
        common[np.arange(diagonal), np.arange(diagonal)] = 0.90
        response = np.einsum("u...d,pd->u...p", condition, common)
        response += rng.normal(scale=spec.noise, size=response.shape)
        parameter = opportunity
    elif world == "mixed_superposition":
        mixing = np.linspace(0.18, 0.82, spec.authors)
        density = 0.35 * _density_response(rng, spec, mixing)
        operators = np.asarray([
            _rotation_z(value, spec.response_dimensions)
            for value in theta
        ])
        usable = min(spec.condition_dimensions, spec.response_dimensions)
        conditional = 0.40 * np.einsum(
            "u...d,upd->u...p",
            condition[..., :usable],
            operators[:, :, :usable],
        )
        interaction = 0.40 * np.einsum(
            "u...d,upd->u...p",
            partner,
            operators,
        )
        persistence = np.linspace(0.58, 0.94, spec.authors)
        state_one = _binary_markov(rng, shape, persistence)
        state_two = _lag_two_process(rng, shape, persistence[::-1])
        dynamics = _state_response(
            0.30 * state_one + 0.25 * state_two,
            spec,
            rng,
            scale=1.0,
        )
        response = density + conditional + interaction + dynamics
        parameter = np.column_stack([
            mixing,
            persistence,
            persistence[::-1],
            operators.reshape(spec.authors, -1),
        ])
    elif world == "null_author":
        response = rng.normal(
            scale=1.0,
            size=shape + (spec.response_dimensions,),
        )
        parameter = np.zeros((spec.authors, 1), dtype=float)
    else:
        raise ValueError(f"unsupported M3 mechanism world: {world}")
    return response, condition, partner, parameter


def generate_m3_mechanism_world(
    *,
    world: str,
    spec: M3MechanismWorldSpec,
    seed: int,
) -> tuple[M3MechanismObserved, M3MechanismTruth]:
    """Generate independent views with a shared author mechanism."""
    if world not in _EXPECTED_FAMILY:
        raise ValueError(f"unsupported M3 mechanism world: {world}")
    if spec.authors < 12 or spec.events < 8 or spec.occasions < 2:
        raise ValueError("mechanism worlds require authors>=12, events>=8, occasions>=2")
    train_rng = np.random.default_rng(seed)
    test_rng = np.random.default_rng(seed + 10_000_019)
    train = _panel(world=world, rng=train_rng, spec=spec)
    test = _panel(world=world, rng=test_rng, spec=spec)
    observed = M3MechanismObserved(
        response_train=train[0],
        response_test=test[0],
        condition_train=train[1],
        condition_test=test[1],
        partner_train=train[2],
        partner_test=test[2],
    )
    truth = M3MechanismTruth(
        world=world,
        expected_family=_EXPECTED_FAMILY[world],
        author_parameter=train[3],
    )
    if not np.allclose(train[3], test[3]):
        raise RuntimeError("train/test panels do not share the planted author mechanism")
    return observed, truth
