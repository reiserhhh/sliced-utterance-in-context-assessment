"""Synthetic worlds for SUICA M4 mechanism-composition discovery.

The response law is deliberately low-order and transparent to the generator,
while the estimator receives only event drivers and responses.  Independent
train/test panels share author parameters but not event realizations.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .m4_composition_contracts import (
    M4CompositionObserved,
    M4CompositionTruth,
    validate_composition_observed,
)


MECHANISM_NAMES = (
    "opportunity",
    "state",
    "condition",
    "interaction",
    "emission_drive",
    "history",
)

WORLD_KINDS = {
    "additive_dependent": "additive_dependent",
    "synergy": "synergy",
    "redundancy": "redundancy",
    "suppression": "suppression",
    "gate": "gate",
    "projection_order": "projection_order_sensitive",
    "composite": "composite",
    "alias": "alias",
    "null": "null",
}


@dataclass(frozen=True)
class M4CompositionSpec:
    """Dimensions and signal strengths for one M4 discovery world."""

    authors: int = 30
    occasions: int = 4
    events: int = 128
    noise: float = 0.35


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
    *,
    spec: M4CompositionSpec,
    seed: int,
) -> dict[str, np.ndarray]:
    return {
        "strength": _grid(
            authors=spec.authors,
            low=0.30,
            high=1.15,
            seed=seed + 101,
        ),
        "dependence": _grid(
            authors=spec.authors,
            low=0.20,
            high=0.92,
            seed=seed + 211,
        ),
        "secondary": _grid(
            authors=spec.authors,
            low=0.20,
            high=0.95,
            seed=seed + 307,
        ),
        "tertiary": _grid(
            authors=spec.authors,
            low=0.15,
            high=0.80,
            seed=seed + 401,
        ),
    }


def _correlate(
    drivers: np.ndarray,
    source: int,
    target: int,
    rho: np.ndarray,
) -> None:
    residual = np.sqrt(np.maximum(1.0 - rho ** 2, 1e-8))
    drivers[..., target] = (
        rho[:, None, None] * drivers[..., source]
        + residual[:, None, None] * drivers[..., target]
    )


def _active(
    disabled: frozenset[str],
    *mechanisms: str,
) -> bool:
    return not disabled.intersection(mechanisms)


def _make_panel(
    *,
    world: str,
    spec: M4CompositionSpec,
    parameters: dict[str, np.ndarray],
    seed: int,
    disabled: frozenset[str],
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    shape = (spec.authors, spec.occasions, spec.events)
    drivers = rng.normal(size=shape + (len(MECHANISM_NAMES),))
    index = {name: position for position, name in enumerate(MECHANISM_NAMES)}
    strength = parameters["strength"][:, None, None]
    dependence = parameters["dependence"]
    secondary = parameters["secondary"][:, None, None]
    tertiary = parameters["tertiary"][:, None, None]

    if world in {"additive_dependent", "redundancy", "alias"}:
        _correlate(
            drivers,
            index["opportunity"],
            index["condition"],
            dependence,
        )
    elif world == "suppression":
        _correlate(
            drivers,
            index["state"],
            index["interaction"],
            dependence,
        )
    elif world == "projection_order":
        _correlate(
            drivers,
            index["opportunity"],
            index["condition"],
            dependence,
        )
        _correlate(
            drivers,
            index["condition"],
            index["history"],
            dependence,
        )

    if world in {"gate", "composite"}:
        drivers[..., index["history"]] = np.where(
            drivers[..., index["history"]] >= 0.0,
            1.0,
            -1.0,
        )
    if world == "alias":
        drivers[..., index["condition"]] = drivers[..., index["opportunity"]]

    response = np.zeros(shape, dtype=float)
    opportunity = drivers[..., index["opportunity"]]
    state = drivers[..., index["state"]]
    condition = drivers[..., index["condition"]]
    interaction = drivers[..., index["interaction"]]
    emission_drive = drivers[..., index["emission_drive"]]
    history = drivers[..., index["history"]]

    if world == "additive_dependent":
        weights = {
            "opportunity": 0.00,
            "state": -0.35,
            "condition": 0.00,
            "interaction": 0.25,
            "emission_drive": 0.30,
            "history": -0.20,
        }
        for name, weight in weights.items():
            if _active(disabled, name):
                response += weight * drivers[..., index[name]]
    elif world == "synergy":
        if _active(disabled, "state"):
            response += 0.20 * state
        if _active(disabled, "condition"):
            response += 0.15 * condition
        if _active(disabled, "state", "condition"):
            response += strength * state * condition
    elif world == "redundancy":
        if _active(disabled, "opportunity"):
            response += 0.75 * opportunity
        if _active(disabled, "condition"):
            response += 0.75 * condition
    elif world == "suppression":
        if _active(disabled, "state"):
            response += 0.85 * state
        if _active(disabled, "interaction"):
            response -= 0.85 * interaction
    elif world == "gate":
        if _active(disabled, "condition"):
            response += 0.12 * condition
        if _active(disabled, "history", "condition"):
            response += strength * condition * (history > 0.0)
    elif world == "projection_order":
        if _active(disabled, "opportunity"):
            response += 0.60 * opportunity
        if _active(disabled, "condition"):
            response -= 0.25 * condition
        if _active(disabled, "history"):
            response += 0.60 * history
    elif world == "composite":
        if _active(disabled, "emission_drive"):
            response += 0.12 * emission_drive
        if _active(disabled, "state", "condition"):
            response += strength * state * condition
        if _active(disabled, "interaction", "history"):
            response += secondary * interaction * (history > 0.0)
        if _active(disabled, "opportunity", "emission_drive", "history"):
            response -= tertiary * opportunity * emission_drive * history
    elif world == "alias":
        if _active(disabled, "opportunity"):
            response += strength * opportunity
        elif _active(disabled, "condition"):
            response += strength * condition
    elif world == "null":
        pass
    else:
        raise ValueError(f"unsupported M4 composition world: {world}")

    response += rng.normal(scale=spec.noise, size=response.shape)
    return drivers, response


def _edge(*names: str) -> tuple[str, ...]:
    order = {name: index for index, name in enumerate(MECHANISM_NAMES)}
    return tuple(sorted(names, key=order.__getitem__))


def generate_m4_composition_world(
    *,
    world: str,
    spec: M4CompositionSpec,
    seed: int,
    disabled: frozenset[str] = frozenset(),
) -> tuple[M4CompositionObserved, M4CompositionTruth]:
    """Generate an independent-panel mechanism-composition world."""
    if world not in WORLD_KINDS:
        raise ValueError(f"unsupported M4 composition world: {world}")
    unknown = disabled.difference(MECHANISM_NAMES)
    if unknown:
        raise ValueError(f"unknown disabled mechanisms: {sorted(unknown)}")
    parameters = _parameters(spec=spec, seed=seed + 17_111)
    train = _make_panel(
        world=world,
        spec=spec,
        parameters=parameters,
        seed=seed,
        disabled=disabled,
    )
    test = _make_panel(
        world=world,
        spec=spec,
        parameters=parameters,
        seed=seed + 91_000_019,
        disabled=disabled,
    )

    active: tuple[tuple[str, ...], ...] = ()
    signed: dict[tuple[str, ...], int] = {}
    target_pair: tuple[str, str] | None = None
    if world == "synergy":
        target_pair = _edge("state", "condition")
        active = (target_pair,)
        signed[target_pair] = 1
    elif world == "gate":
        target_pair = _edge("condition", "history")
        active = (target_pair,)
        signed[target_pair] = 1
    elif world == "composite":
        first = _edge("state", "condition")
        second = _edge("interaction", "history")
        third = _edge("opportunity", "emission_drive", "history")
        active = (first, second, third)
        signed = {first: 1, second: 1, third: -1}
    elif world == "redundancy":
        target_pair = _edge("opportunity", "condition")
    elif world == "suppression":
        target_pair = _edge("state", "interaction")
    elif world == "projection_order":
        target_pair = _edge("opportunity", "condition")

    observed = M4CompositionObserved(
        drivers_train=train[0],
        drivers_test=test[0],
        response_train=train[1],
        response_test=test[1],
        mechanism_names=MECHANISM_NAMES,
        design={
            "world_hidden_from_estimator": True,
            "disabled": sorted(disabled),
            "response_kernel": "multilinear_order3_plus_gate",
        },
    )
    validate_composition_observed(observed)
    truth = M4CompositionTruth(
        world=world,
        expected_kind=WORLD_KINDS[world],
        author_parameters={
            name: values[:, None]
            for name, values in parameters.items()
        },
        active_hyperedges=active,
        signed_hyperedges=signed,
        target_pair=target_pair,
        alias=world == "alias",
    )
    return observed, truth
