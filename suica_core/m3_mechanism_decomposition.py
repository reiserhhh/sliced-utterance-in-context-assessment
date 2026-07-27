"""Independent-parameter pairwise mixtures for M3 mechanism decomposition."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .m3_mechanism_contracts import M3MechanismObserved


MECHANISM_TO_FAMILY = {
    "density": "standardized_distribution_shape",
    "condition": "nonlinear_condition",
    "ar2": "ar2_slow_spectrum",
    "interaction": "nonlinear_partner",
    "lag3": "lag3_partial_operator",
}


@dataclass(frozen=True)
class M3MechanismMixtureTruth:
    """Independent author parameters for a pairwise mechanism world."""

    pair: tuple[str, str]
    author_parameters: dict[str, np.ndarray]


@dataclass(frozen=True)
class M3MechanismMixtureSpec:
    """Dimensions and component strengths for decomposition discovery."""

    authors: int = 40
    occasions: int = 6
    events: int = 160
    dimensions: int = 3
    noise: float = 0.16
    component_scale: float = 0.65


_DIRECTIONS = {
    "density": np.asarray([1.0, 0.0, 0.0]),
    "condition": np.asarray([0.60, 0.80, 0.0]),
    "ar2": np.asarray([0.0, 0.60, 0.80]),
    "interaction": np.asarray([0.70, -0.40, 0.591607978]),
    "lag3": np.asarray([-0.30, 0.80, -0.519615242]),
}


def _hermite_three(values: np.ndarray) -> np.ndarray:
    return (values ** 3 - 3.0 * values) / np.sqrt(6.0)


def _parameters(
    *,
    authors: int,
    seed: int,
) -> dict[str, np.ndarray]:
    values = {
        "density": np.linspace(0.20, 0.88, authors),
        "condition": np.linspace(-0.85, 0.85, authors),
        "ar2": np.linspace(-0.18, 0.58, authors),
        "interaction": np.linspace(-0.85, 0.85, authors),
        "lag3": np.linspace(0.56, 0.96, authors),
    }
    output: dict[str, np.ndarray] = {}
    for index, (name, parameter) in enumerate(values.items()):
        rng = np.random.default_rng(seed + 10_003 * (index + 1))
        output[name] = parameter[rng.permutation(authors)]
    return output


def _ar2(
    rng: np.random.Generator,
    *,
    lag_two: np.ndarray,
    spec: M3MechanismMixtureSpec,
) -> np.ndarray:
    burn = 220
    total = burn + spec.events
    fixed_rho_one = 0.30
    lag_one = fixed_rho_one * (1.0 - lag_two)
    innovation_variance = (
        1.0
        - lag_one * fixed_rho_one
        - lag_two * (lag_one * fixed_rho_one + lag_two)
    )
    values = np.empty(
        (spec.authors, spec.occasions, total),
        dtype=float,
    )
    values[:, :, :2] = rng.normal(
        size=(spec.authors, spec.occasions, 2),
    )
    for event in range(2, total):
        values[:, :, event] = (
            lag_one[:, None] * values[:, :, event - 1]
            + lag_two[:, None] * values[:, :, event - 2]
            + rng.normal(
                scale=np.sqrt(np.maximum(innovation_variance, 0.05))[:, None],
                size=(spec.authors, spec.occasions),
            )
        )
    return values[:, :, burn:]


def _lag3(
    rng: np.random.Generator,
    *,
    persistence: np.ndarray,
    spec: M3MechanismMixtureSpec,
) -> np.ndarray:
    shape = (spec.authors, spec.occasions, spec.events)
    values = np.empty(shape, dtype=float)
    values[:, :, :3] = rng.choice((-1.0, 1.0), size=shape[:2] + (3,))
    for event in range(3, spec.events):
        keep = rng.random(shape[:2]) < persistence[:, None]
        values[:, :, event] = np.where(
            keep,
            values[:, :, event - 3],
            -values[:, :, event - 3],
        )
    return values


def _component_panel(
    *,
    mechanism: str,
    parameter: np.ndarray,
    condition: np.ndarray,
    partner: np.ndarray,
    spec: M3MechanismMixtureSpec,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    event_shape = condition.shape[:-1]
    if mechanism == "density":
        active = rng.random(event_shape) < parameter[:, None, None]
        sign = rng.choice((-1.0, 1.0), size=event_shape)
        scalar = active * sign / np.sqrt(parameter[:, None, None])
    elif mechanism == "condition":
        scalar = parameter[:, None, None] * _hermite_three(condition[..., 0])
    elif mechanism == "ar2":
        scalar = _ar2(rng, lag_two=parameter, spec=spec)
    elif mechanism == "interaction":
        scalar = parameter[:, None, None] * _hermite_three(partner[..., 0])
    elif mechanism == "lag3":
        scalar = _lag3(rng, persistence=parameter, spec=spec)
    else:
        raise ValueError(f"unsupported mixture mechanism: {mechanism}")
    direction = _DIRECTIONS[mechanism][:spec.dimensions]
    direction = direction / np.linalg.norm(direction)
    return spec.component_scale * scalar[..., None] * direction


def _view(
    *,
    pair: tuple[str, str],
    disabled: frozenset[str],
    parameters: dict[str, np.ndarray],
    spec: M3MechanismMixtureSpec,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    base_rng = np.random.default_rng(seed)
    shape = (
        spec.authors,
        spec.occasions,
        spec.events,
        spec.dimensions,
    )
    condition = base_rng.normal(size=shape)
    partner = base_rng.normal(size=shape)
    response = base_rng.normal(scale=spec.noise, size=shape)
    for index, mechanism in enumerate(pair):
        if mechanism in disabled:
            continue
        response += _component_panel(
            mechanism=mechanism,
            parameter=parameters[mechanism],
            condition=condition,
            partner=partner,
            spec=spec,
            seed=seed + 1_000_003 * (index + 1),
        )
    return response, condition, partner


def generate_m3_mechanism_pair_world(
    *,
    pair: tuple[str, str],
    spec: M3MechanismMixtureSpec,
    seed: int,
    disabled: frozenset[str] = frozenset(),
) -> tuple[M3MechanismObserved, M3MechanismMixtureTruth]:
    """Generate a pairwise superposition with independent author parameters."""
    if len(pair) != 2 or pair[0] == pair[1]:
        raise ValueError("pair must contain two distinct mechanisms")
    if any(name not in MECHANISM_TO_FAMILY for name in pair):
        raise ValueError("pair contains an unsupported mechanism")
    parameters = _parameters(authors=spec.authors, seed=seed + 409)
    train = _view(
        pair=pair,
        disabled=disabled,
        parameters=parameters,
        spec=spec,
        seed=seed,
    )
    test = _view(
        pair=pair,
        disabled=disabled,
        parameters=parameters,
        spec=spec,
        seed=seed + 90_000_011,
    )
    return (
        M3MechanismObserved(
            response_train=train[0],
            response_test=test[0],
            condition_train=train[1],
            condition_test=test[1],
            partner_train=train[2],
            partner_test=test[2],
        ),
        M3MechanismMixtureTruth(
            pair=pair,
            author_parameters={
                name: parameters[name][:, None]
                for name in pair
            },
        ),
    )
