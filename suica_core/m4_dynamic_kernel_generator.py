"""True transition-kernel worlds for M4 gate and order discovery."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .m4_dynamic_kernel_contracts import (
    M4DynamicKernelObserved,
    M4DynamicKernelTruth,
    validate_dynamic_kernel_observed,
)


REGIME_CONDITION = 0
REGIME_HISTORY = 1
REGIME_JOINT = 2

WORLD_ORDERS = {
    "noncommuting_forward_gate": "history_after_condition",
    "noncommuting_reverse_gate": "condition_after_history",
    "commuting_null": "commuting",
    "gate_role_alias": "alias",
}


@dataclass(frozen=True)
class M4DynamicKernelSpec:
    """Dimensions for a dynamic transition-kernel panel."""

    authors: int = 24
    occasions: int = 6
    events: int = 180
    dimensions: int = 2
    noise: float = 0.055


def _grid(
    *,
    authors: int,
    low: float,
    high: float,
    seed: int,
) -> np.ndarray:
    values = np.linspace(low, high, authors)
    return values[np.random.default_rng(seed).permutation(authors)]


def _parameters(
    spec: M4DynamicKernelSpec,
    *,
    seed: int,
) -> dict[str, np.ndarray]:
    return {
        "angle": _grid(
            authors=spec.authors,
            low=0.12,
            high=0.58,
            seed=seed + 101,
        ),
        "shear": _grid(
            authors=spec.authors,
            low=0.06,
            high=0.34,
            seed=seed + 211,
        ),
        "gate_strength": _grid(
            authors=spec.authors,
            low=0.12,
            high=0.72,
            seed=seed + 307,
        ),
    }


def _condition_matrix(
    sign: float,
    angle: float,
    dimensions: int,
) -> np.ndarray:
    if dimensions != 2:
        raise ValueError("M4 dynamic V1 currently requires dimensions=2")
    value = sign * angle
    cosine = float(np.cos(value))
    sine = float(np.sin(value))
    return 0.94 * np.asarray([
        [cosine, -sine],
        [sine, cosine],
    ])


def _history_matrix(
    sign: float,
    shear: float,
    dimensions: int,
    *,
    commuting: bool,
) -> np.ndarray:
    if dimensions != 2:
        raise ValueError("M4 dynamic V1 currently requires dimensions=2")
    if commuting:
        return (0.82 + 0.04 * sign) * np.eye(dimensions)
    return np.asarray([
        [0.86, sign * shear],
        [0.0, 0.78],
    ])


def _regime_schedule(
    rng: np.random.Generator,
    events: int,
    *,
    alias: bool,
) -> np.ndarray:
    if alias:
        return np.full(events, REGIME_JOINT, dtype=int)
    condition_count = events // 4
    history_count = events // 4
    schedule = np.concatenate([
        np.full(condition_count, REGIME_CONDITION, dtype=int),
        np.full(history_count, REGIME_HISTORY, dtype=int),
        np.full(
            events - condition_count - history_count,
            REGIME_JOINT,
            dtype=int,
        ),
    ])
    return schedule[rng.permutation(events)]


def _truth_commutator(
    *,
    angle: float,
    shear: float,
    dimensions: int,
    commuting: bool,
) -> float:
    values = []
    for condition in (-1.0, 1.0):
        for history in (-1.0, 1.0):
            condition_matrix = _condition_matrix(
                condition,
                angle,
                dimensions,
            )
            history_matrix = _history_matrix(
                history,
                shear,
                dimensions,
                commuting=commuting,
            )
            values.append(np.linalg.norm(
                history_matrix @ condition_matrix
                - condition_matrix @ history_matrix,
                ord="fro",
            ))
    return float(np.mean(values))


def _panel(
    *,
    world: str,
    spec: M4DynamicKernelSpec,
    parameters: dict[str, np.ndarray],
    seed: int,
) -> tuple[np.ndarray, ...]:
    rng = np.random.default_rng(seed)
    shape = (spec.authors, spec.occasions, spec.events)
    pre = np.empty(shape + (spec.dimensions,), dtype=float)
    post = np.empty_like(pre)
    condition = np.zeros(shape, dtype=float)
    history = np.zeros(shape, dtype=float)
    regime = np.empty(shape, dtype=int)
    alias = world == "gate_role_alias"
    commuting = world == "commuting_null"
    forward = world != "noncommuting_reverse_gate"
    gate_direction = np.asarray([1.0, 0.35], dtype=float)
    gate_direction /= np.linalg.norm(gate_direction)

    for author in range(spec.authors):
        angle = float(parameters["angle"][author])
        shear = float(parameters["shear"][author])
        gate_strength = (
            0.0
            if commuting
            else float(parameters["gate_strength"][author])
        )
        for occasion in range(spec.occasions):
            state = rng.normal(scale=0.65, size=spec.dimensions)
            schedule = _regime_schedule(
                rng,
                spec.events,
                alias=alias,
            )
            for event, current_regime in enumerate(schedule):
                condition_value = 0.0
                history_value = 0.0
                if current_regime in (REGIME_CONDITION, REGIME_JOINT):
                    condition_value = float(rng.choice((-1.0, 1.0)))
                if current_regime in (REGIME_HISTORY, REGIME_JOINT):
                    history_value = float(rng.choice((-1.0, 1.0)))
                if alias:
                    history_value = condition_value

                condition_matrix = _condition_matrix(
                    condition_value or 1.0,
                    angle,
                    spec.dimensions,
                )
                history_matrix = _history_matrix(
                    history_value or 1.0,
                    shear,
                    spec.dimensions,
                    commuting=commuting,
                )
                if current_regime == REGIME_CONDITION:
                    transition = condition_matrix
                elif current_regime == REGIME_HISTORY:
                    transition = history_matrix
                elif forward:
                    transition = history_matrix @ condition_matrix
                else:
                    transition = condition_matrix @ history_matrix

                gate = (
                    gate_strength
                    * condition_value
                    * float(history_value > 0.0)
                    * gate_direction
                )
                next_state = (
                    transition @ state
                    + gate
                    + rng.normal(scale=spec.noise, size=spec.dimensions)
                )
                pre[author, occasion, event] = state
                post[author, occasion, event] = next_state
                condition[author, occasion, event] = condition_value
                history[author, occasion, event] = history_value
                regime[author, occasion, event] = current_regime
                state = next_state
    return pre, post, condition, history, regime


def generate_m4_dynamic_kernel_world(
    *,
    world: str,
    spec: M4DynamicKernelSpec,
    seed: int,
) -> tuple[M4DynamicKernelObserved, M4DynamicKernelTruth]:
    """Generate independent transition paths with shared author kernels."""
    if world not in WORLD_ORDERS:
        raise ValueError(f"unsupported M4 dynamic kernel world: {world}")
    parameters = _parameters(spec, seed=seed + 71_117)
    train = _panel(
        world=world,
        spec=spec,
        parameters=parameters,
        seed=seed,
    )
    test = _panel(
        world=world,
        spec=spec,
        parameters=parameters,
        seed=seed + 93_000_031,
    )
    observed = M4DynamicKernelObserved(
        pre_train=train[0],
        post_train=train[1],
        condition_train=train[2],
        history_train=train[3],
        regime_train=train[4],
        pre_test=test[0],
        post_test=test[1],
        condition_test=test[2],
        history_test=test[3],
        regime_test=test[4],
        design={
            "regime_condition": REGIME_CONDITION,
            "regime_history": REGIME_HISTORY,
            "regime_joint": REGIME_JOINT,
            "world_hidden_from_estimator": True,
        },
    )
    validate_dynamic_kernel_observed(observed)
    commuting = world == "commuting_null"
    commutator = np.asarray([
        _truth_commutator(
            angle=float(parameters["angle"][author]),
            shear=float(parameters["shear"][author]),
            dimensions=spec.dimensions,
            commuting=commuting,
        )
        for author in range(spec.authors)
    ])
    truth = M4DynamicKernelTruth(
        world=world,
        expected_order=WORLD_ORDERS[world],
        author_parameters={
            "angle": parameters["angle"][:, None],
            "shear": parameters["shear"][:, None],
            "gate_strength": (
                np.zeros((spec.authors, 1), dtype=float)
                if commuting
                else parameters["gate_strength"][:, None]
            ),
            "commutator": commutator[:, None],
        },
        alias=world == "gate_role_alias",
    )
    return observed, truth
