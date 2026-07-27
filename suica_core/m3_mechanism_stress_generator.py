"""Low-order-matched attacks for the SUICA M3 mechanism atlas."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .m3_mechanism_contracts import M3MechanismObserved, M3MechanismTruth


@dataclass(frozen=True)
class M3MechanismStressSpec:
    """Dimensions for low-order-matched synthetic attacks."""

    authors: int = 36
    occasions: int = 6
    events: int = 96
    dimensions: int = 3
    noise: float = 0.10


_EXPECTED = {
    "equal_covariance_density_shape": "distribution_kme",
    "matched_linear_nonlinear_response": "nonlinear_condition",
    "matched_lag1_ar2_slow_mode": "ar2_slow_spectrum",
    "matched_lag12_lag3_path": "lag3_memory",
    "matched_linear_nonlinear_interaction": "nonlinear_partner",
    "null_author": None,
}


def _hermite_three(values: np.ndarray) -> np.ndarray:
    return (values ** 3 - 3.0 * values) / np.sqrt(6.0)


def _draw_ar(
    rng: np.random.Generator,
    *,
    a_one: np.ndarray,
    a_two: np.ndarray,
    spec: M3MechanismStressSpec,
) -> np.ndarray:
    burn = 240
    total = burn + spec.events
    values = np.empty(
        (spec.authors, spec.occasions, total),
        dtype=float,
    )
    values[:, :, :2] = rng.normal(
        size=(spec.authors, spec.occasions, 2),
    )
    rho_one = a_one / np.maximum(1.0 - a_two, 1e-8)
    innovation_variance = (
        1.0
        - a_one * rho_one
        - a_two * (a_one * rho_one + a_two)
    )
    innovation_scale = np.sqrt(np.maximum(innovation_variance, 0.05))
    for event in range(2, total):
        values[:, :, event] = (
            a_one[:, None] * values[:, :, event - 1]
            + a_two[:, None] * values[:, :, event - 2]
            + rng.normal(
                scale=innovation_scale[:, None],
                size=(spec.authors, spec.occasions),
            )
        )
    return values[:, :, burn:]


def _lag_three_binary(
    rng: np.random.Generator,
    *,
    persistence: np.ndarray,
    spec: M3MechanismStressSpec,
) -> np.ndarray:
    shape = (spec.authors, spec.occasions, spec.events)
    values = np.empty(shape, dtype=float)
    values[:, :, :3] = rng.choice(
        (-1.0, 1.0),
        size=(spec.authors, spec.occasions, 3),
    )
    for event in range(3, spec.events):
        keep = rng.random((spec.authors, spec.occasions)) < persistence[:, None]
        values[:, :, event] = np.where(
            keep,
            values[:, :, event - 3],
            -values[:, :, event - 3],
        )
    return values


def _panel(
    world: str,
    *,
    rng: np.random.Generator,
    spec: M3MechanismStressSpec,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    shape = (spec.authors, spec.occasions, spec.events, spec.dimensions)
    condition = rng.normal(size=shape)
    partner = rng.normal(size=shape)
    response = rng.normal(scale=spec.noise, size=shape)

    if world == "equal_covariance_density_shape":
        active_probability = np.linspace(0.18, 0.88, spec.authors)
        active = (
            rng.random(shape[:-1])
            < active_probability[:, None, None]
        )
        sign = rng.choice((-1.0, 1.0), size=shape[:-1])
        response[..., 0] += (
            active
            * sign
            / np.sqrt(active_probability[:, None, None])
        )
        response[..., 1:] += rng.normal(size=shape[:-1] + (spec.dimensions - 1,))
        parameter = active_probability[:, None]
    elif world == "matched_linear_nonlinear_response":
        nonlinear = np.linspace(-0.75, 0.75, spec.authors)
        response += condition
        response[..., 0] += (
            nonlinear[:, None, None]
            * _hermite_three(condition[..., 0])
        )
        parameter = nonlinear[:, None]
    elif world == "matched_lag1_ar2_slow_mode":
        lag_two = np.linspace(-0.20, 0.58, spec.authors)
        fixed_rho_one = 0.32
        lag_one = fixed_rho_one * (1.0 - lag_two)
        series = _draw_ar(
            rng,
            a_one=lag_one,
            a_two=lag_two,
            spec=spec,
        )
        response[..., 0] += series
        response[..., 1:] += rng.normal(size=shape[:-1] + (spec.dimensions - 1,))
        parameter = np.column_stack([lag_one, lag_two])
    elif world == "matched_lag12_lag3_path":
        persistence = np.linspace(0.56, 0.96, spec.authors)
        series = _lag_three_binary(
            rng,
            persistence=persistence,
            spec=spec,
        )
        response[..., 0] += series
        response[..., 1:] += rng.normal(size=shape[:-1] + (spec.dimensions - 1,))
        parameter = persistence[:, None]
    elif world == "matched_linear_nonlinear_interaction":
        nonlinear = np.linspace(-0.75, 0.75, spec.authors)
        response += partner
        response[..., 0] += (
            nonlinear[:, None, None]
            * _hermite_three(partner[..., 0])
        )
        parameter = nonlinear[:, None]
    elif world == "null_author":
        response = rng.normal(size=shape)
        parameter = np.zeros((spec.authors, 1), dtype=float)
    else:
        raise ValueError(f"unsupported mechanism stress world: {world}")
    return response, condition, partner, parameter


def generate_m3_mechanism_stress_world(
    *,
    world: str,
    spec: M3MechanismStressSpec,
    seed: int,
) -> tuple[M3MechanismObserved, M3MechanismTruth]:
    """Generate independent panels with deliberately matched low-order moments."""
    if world not in _EXPECTED:
        raise ValueError(f"unsupported mechanism stress world: {world}")
    train = _panel(world, rng=np.random.default_rng(seed), spec=spec)
    test = _panel(
        world,
        rng=np.random.default_rng(seed + 70_000_003),
        spec=spec,
    )
    if not np.allclose(train[3], test[3]):
        raise RuntimeError("stress panels must share author truth")
    return (
        M3MechanismObserved(
            response_train=train[0],
            response_test=test[0],
            condition_train=train[1],
            condition_test=test[1],
            partner_train=train[2],
            partner_test=test[2],
        ),
        M3MechanismTruth(
            world=world,
            expected_family=_EXPECTED[world],
            author_parameter=train[3],
        ),
    )
