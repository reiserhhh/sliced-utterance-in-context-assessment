"""Cross-family synthetic worlds for the SUICA M3 confirmation program.

The generators intentionally do not share a dictionary with the estimator:

* CF-D uses bounded high-order Legendre density perturbations.
* CF-O uses spline, Voronoi, or neural response surfaces orthogonal to all
  observed polynomial terms through total degree three.
* CF-KP uses constrained renewal, non-reversible hidden-state, or ARCH paths
  whose population lag-0:2 covariance is fixed across authors. No path is
  modified after generation to force an empirical spectrum match.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np
from numpy.polynomial.legendre import legval

from .m3_cross_family_contracts import (
    M3CrossFamilyObserved,
    M3CrossFamilyTruth,
)


@dataclass(frozen=True)
class M3CrossFamilySpec:
    """Shared dimensions for a cross-family synthetic panel."""

    authors: int = 48
    occasions: int = 4
    events: int = 192
    dimensions: int = 3
    partners: int = 16
    noise: float = 0.14


WORLD_TARGETS: dict[str, tuple[str, ...]] = {
    "cf_d_tail": ("distribution",),
    "cf_d_skew": ("distribution",),
    "cf_d_multimodal": ("distribution",),
    "cf_d_copula": ("distribution",),
    "cf_o_spline": ("condition", "partner"),
    "cf_o_voronoi": ("condition", "partner"),
    "cf_o_neural": ("condition", "partner"),
    "cf_kp_hsmm": ("hazard",),
    "cf_kp_cycle": ("direction",),
    "cf_kp_arch": ("nonlinear_dynamics",),
    "null_author": (),
    "alias_hidden": ("direction",),
    "alias_operator_support": ("condition", "partner"),
}


def _author_parameters(
    rng: np.random.Generator,
    authors: int,
    dimensions: int = 2,
) -> np.ndarray:
    values = rng.normal(size=(authors, dimensions))
    values -= values.mean(axis=0, keepdims=True)
    values /= np.maximum(values.std(axis=0, keepdims=True), 1e-8)
    return values


def _orthogonal(rng: np.random.Generator, dimensions: int) -> np.ndarray:
    matrix, _ = np.linalg.qr(rng.normal(size=(dimensions, dimensions)))
    if np.linalg.det(matrix) < 0:
        matrix[:, 0] *= -1.0
    return matrix


def _legendre(order: int, values: np.ndarray) -> np.ndarray:
    coefficients = np.zeros(order + 1, dtype=float)
    coefficients[order] = 1.0
    return legval(values, coefficients)


def _density_score(
    family: str,
    points: np.ndarray,
    coefficients: np.ndarray,
) -> np.ndarray:
    x0 = points[:, 0]
    x1 = points[:, 1] if points.shape[1] > 1 else points[:, 0]
    if family == "tail":
        basis = np.column_stack([
            _legendre(6, x0),
            _legendre(8, x0),
        ])
    elif family == "skew":
        basis = np.column_stack([
            _legendre(5, x0),
            _legendre(7, x0),
        ])
    elif family == "multimodal":
        basis = np.column_stack([
            _legendre(6, x0),
            _legendre(10, x0),
        ])
    elif family == "copula":
        basis = np.column_stack([
            _legendre(3, x0) * _legendre(3, x1),
            _legendre(4, x0) * _legendre(3, x1),
        ])
    else:
        raise ValueError(f"unsupported density family: {family}")
    weights = coefficients / max(np.sum(np.abs(coefficients)), 1e-8)
    return np.clip(basis @ weights, -1.0, 1.0)


def _draw_legendre_density(
    rng: np.random.Generator,
    *,
    family: str,
    coefficients: np.ndarray,
    count: int,
    dimensions: int,
    eta: float = 0.92,
) -> np.ndarray:
    accepted: list[np.ndarray] = []
    remaining = count
    while remaining > 0:
        candidates = rng.uniform(
            -1.0,
            1.0,
            size=(max(remaining * 3, 256), dimensions),
        )
        score = _density_score(family, candidates, coefficients)
        probability = (1.0 + eta * score) / (1.0 + eta)
        keep = rng.random(len(candidates)) < probability
        block = candidates[keep][:remaining]
        if len(block):
            accepted.append(block)
            remaining -= len(block)
    return np.concatenate(accepted, axis=0)


def _distribution_panel(
    rng: np.random.Generator,
    *,
    family: str,
    spec: M3CrossFamilySpec,
    parameters: np.ndarray,
    rotation: np.ndarray,
) -> np.ndarray:
    count = spec.occasions * spec.events
    panel = np.empty(
        (spec.authors, spec.occasions, spec.events, spec.dimensions),
        dtype=float,
    )
    for author in range(spec.authors):
        values = _draw_legendre_density(
            rng,
            family=family,
            coefficients=parameters[author],
            count=count,
            dimensions=spec.dimensions,
        )
        panel[author] = (values @ rotation).reshape(
            spec.occasions,
            spec.events,
            spec.dimensions,
        )
    return panel


def _polynomial_design(values: np.ndarray, degree: int = 3) -> np.ndarray:
    flat = np.asarray(values, dtype=float).reshape(-1, values.shape[-1])
    powers = [
        power
        for power in product(range(degree + 1), repeat=values.shape[-1])
        if sum(power) <= degree
    ]
    return np.column_stack([
        np.prod(flat ** np.asarray(power)[None, :], axis=1)
        for power in powers
    ])


def _orthogonalize_surface(
    raw: np.ndarray,
    predictor: np.ndarray,
    partner_ids: np.ndarray | None = None,
) -> np.ndarray:
    design = _polynomial_design(predictor, degree=3)
    if partner_ids is not None:
        raw = _center_shared_groups(raw, partner_ids)
        design = _center_shared_groups(design, partner_ids)
    residual = raw - design @ np.linalg.lstsq(design, raw, rcond=None)[0]
    columns: list[np.ndarray] = []
    for index in range(residual.shape[1]):
        column = residual[:, index].copy()
        for previous in columns:
            column -= previous * np.dot(previous, column)
        norm = np.linalg.norm(column)
        if norm <= 1e-10:
            raise RuntimeError("operator surface collapsed after polynomial projection")
        # Gram-Schmidt starts from the raw residual itself, so unlike an
        # unconstrained QR factorization the orientation cannot flip between
        # independent train and test opportunity panels.
        columns.append(column / norm)
    return np.column_stack(columns) * np.sqrt(len(residual))


def _center_shared_groups(
    values: np.ndarray,
    partner_ids: np.ndarray,
) -> np.ndarray:
    ids = np.asarray(partner_ids, dtype=int)
    occasions, events = ids.shape
    reshaped = np.asarray(values, dtype=float).reshape(
        occasions,
        events,
        -1,
    ).copy()
    for occasion in range(occasions):
        for partner_id in np.unique(ids[occasion]):
            mask = ids[occasion] == partner_id
            reshaped[occasion, mask] -= reshaped[occasion, mask].mean(
                axis=0,
                keepdims=True,
            )
    return reshaped.reshape(-1, reshaped.shape[-1])


def _raw_surface(
    family: str,
    values: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    flat = np.asarray(values, dtype=float).reshape(-1, values.shape[-1])
    x0 = flat[:, 0]
    x1 = flat[:, 1] if flat.shape[1] > 1 else flat[:, 0]
    if family == "spline":
        knots = np.asarray([-1.1, -0.25, 0.55, 1.15])
        first = sum(
            weight * np.maximum(x0 - knot, 0.0) ** 3
            for weight, knot in zip((1.0, -1.4, 0.8, -0.35), knots)
        )
        second = (
            np.maximum(x1 + 0.65, 0.0) ** 3
            - 1.2 * np.maximum(x1 - 0.20, 0.0) ** 3
            + 0.35 * np.maximum(x1 - 1.0, 0.0) ** 3
        )
    elif family == "voronoi":
        centers = np.asarray([
            [-1.2, -0.5],
            [-0.3, 1.0],
            [0.7, -1.1],
            [1.1, 0.6],
        ])
        points = np.column_stack([x0, x1])
        labels = np.argmin(
            np.sum((points[:, None, :] - centers[None, :, :]) ** 2, axis=2),
            axis=1,
        )
        first = np.asarray([-1.0, 0.7, 1.2, -0.45])[labels]
        second = np.asarray([0.8, -1.1, 0.35, 1.0])[labels]
    elif family == "neural":
        weights = rng.normal(size=(2, flat.shape[1], 10))
        biases = rng.uniform(-1.0, 1.0, size=(2, 10))
        out = rng.normal(size=(2, 10))
        first = np.tanh(flat @ weights[0] + biases[0]) @ out[0]
        hidden = flat @ weights[1] + biases[1]
        second = (
            np.logaddexp(0.0, hidden) - np.log(2.0)
        ) @ out[1]
    else:
        raise ValueError(f"unsupported operator family: {family}")
    return np.column_stack([first, second])


def _support_alias_surface(
    values: np.ndarray,
    *,
    bound: float = 1.0,
) -> np.ndarray:
    """Return an author-modulated surface that vanishes on observed support."""
    flat = np.asarray(values, dtype=float).reshape(-1, values.shape[-1])
    if flat.shape[1] < 2:
        raise ValueError("support-alias worlds require at least 2 dimensions")
    coordinates = flat[:, :2]
    excess = np.maximum(np.abs(coordinates) - bound, 0.0)
    return np.sign(coordinates) * excess**4


def _partner_schedule(
    spec: M3CrossFamilySpec,
    *,
    test: bool,
) -> np.ndarray:
    if spec.partners < 4:
        raise ValueError("cross-family operator worlds require at least 4 partners")
    degree = max(2, min(8, spec.partners // 4))
    ids = np.empty((spec.authors, spec.occasions, spec.events), dtype=int)
    base_event = np.arange(spec.events)
    for author in range(spec.authors):
        offset = spec.partners // 2 if test else 0
        pool = (
            author * 3
            + offset
            + np.arange(degree)
        ) % spec.partners
        shifted = pool[base_event % degree]
        ids[author] = np.broadcast_to(
            shifted[None, :],
            (spec.occasions, spec.events),
        )
    return ids


def _operator_panel(
    rng: np.random.Generator,
    *,
    spec: M3CrossFamilySpec,
    condition_parameters: np.ndarray,
    partner_parameters: np.ndarray,
    test: bool,
    active_condition: bool,
    active_partner: bool,
    actor_intercept: np.ndarray,
    partner_intercept: np.ndarray,
    dyad_intercept: np.ndarray,
    occasion_intercept: np.ndarray,
    shared_condition: np.ndarray,
    shared_partner: np.ndarray,
    condition_basis: np.ndarray,
    partner_basis: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    shared_shape = (spec.occasions, spec.events, spec.dimensions)
    if shared_condition.shape != shared_shape or shared_partner.shape != shared_shape:
        raise ValueError("operator opportunity panels must match the shared shape")
    condition = np.broadcast_to(
        shared_condition[None, ...],
        (spec.authors,) + shared_shape,
    ).copy()
    partner = np.broadcast_to(
        shared_partner[None, ...],
        (spec.authors,) + shared_shape,
    ).copy()
    partner_id = _partner_schedule(spec, test=test)

    response = rng.normal(
        scale=spec.noise,
        size=(
            spec.authors,
            spec.occasions,
            spec.events,
            spec.dimensions,
        ),
    )
    response += 0.25 * condition + 0.20 * partner
    for author in range(spec.authors):
        nuisance = (
            actor_intercept[author]
            + partner_intercept[partner_id[author]]
            + dyad_intercept[author, partner_id[author]]
            + occasion_intercept[:, None]
        )
        response[author, ..., 0] += nuisance
        if active_condition:
            response[author, ..., 0] += (
                condition_basis @ condition_parameters[author]
            )
        if active_partner:
            response[author, ..., 0] += (
                partner_basis @ partner_parameters[author]
            )
    return response, condition, partner, partner_id


def _renewal_series(
    rng: np.random.Generator,
    *,
    hazard_parameter: float,
    length: int,
) -> np.ndarray:
    theta = 0.01 + 0.09 * np.tanh(hazard_parameter)
    dwell = np.asarray([
        0.20,
        0.25 + theta,
        0.30 - 2.0 * theta,
        0.25 + theta,
    ])
    support = np.arange(1, 5)
    mean_dwell = float(dwell @ support)
    residual_probability = np.asarray([
        np.sum(dwell[support >= residual]) / mean_dwell
        for residual in support
    ])
    residual_probability /= residual_probability.sum()
    remaining = int(rng.choice(support, p=residual_probability))
    state = float(rng.choice((-1.0, 1.0)))
    values: list[float] = []
    while len(values) < length:
        take = min(remaining, length - len(values))
        values.extend([state] * take)
        if take < remaining:
            break
        state *= -1.0
        remaining = int(rng.choice(support, p=dwell))
    return np.asarray(values, dtype=float)


def _cycle_states(
    rng: np.random.Generator,
    *,
    current: float,
    length: int,
) -> np.ndarray:
    state = int(rng.integers(0, 3))
    states = np.empty(length, dtype=int)
    probability_clockwise = 0.5 + 0.42 * np.tanh(current)
    for index in range(length):
        states[index] = state
        step = 1 if rng.random() < probability_clockwise else -1
        if rng.random() < 0.06:
            step = 0
        state = (state + step) % 3
    return states


def _arch_series(
    rng: np.random.Generator,
    *,
    persistence: float,
    length: int,
) -> np.ndarray:
    alpha = float(0.25 + 0.20 * np.tanh(persistence))
    values = np.empty(length + 300, dtype=float)
    values[0] = rng.normal()
    for index in range(1, len(values)):
        scale = np.sqrt(max(1.0 - alpha + alpha * values[index - 1] ** 2, 0.03))
        values[index] = scale * rng.normal()
    return values[300:]


def _path_panel(
    rng: np.random.Generator,
    *,
    family: str,
    spec: M3CrossFamilySpec,
    parameters: np.ndarray,
    active: bool,
    rotation: np.ndarray,
    emission_alias: bool = False,
) -> np.ndarray:
    panel = np.empty(
        (spec.authors, spec.occasions, spec.events, spec.dimensions),
        dtype=float,
    )
    for author in range(spec.authors):
        for occasion in range(spec.occasions):
            if emission_alias:
                if family == "cycle":
                    for _ in range(spec.dimensions):
                        _cycle_states(
                            rng,
                            current=parameters[author, 0],
                            length=spec.events,
                        )
                latent = rng.normal(
                    size=(spec.events, spec.dimensions)
                )
            elif not active:
                latent = rng.normal(
                    size=(spec.events, spec.dimensions)
                )
            elif family == "hsmm":
                latent = spec.noise * rng.normal(
                    size=(spec.events, spec.dimensions)
                )
                latent[:, 0] += _renewal_series(
                    rng,
                    hazard_parameter=parameters[author, 0],
                    length=spec.events,
                )
            elif family == "cycle":
                states = _cycle_states(
                    rng,
                    current=parameters[author, 0],
                    length=spec.events,
                )
                emissions = np.asarray([-1.0, 0.10, 0.90])
                centered = emissions - emissions.mean()
                latent = spec.noise * rng.normal(
                    size=(spec.events, spec.dimensions)
                )
                latent[:, 0] += (
                    centered[states] / np.sqrt(np.mean(centered**2))
                )
            elif family == "arch":
                latent = np.column_stack([
                    _arch_series(
                        rng,
                        persistence=parameters[author, 0],
                        length=spec.events,
                    )
                    for _ in range(spec.dimensions)
                ])
            else:
                raise ValueError(f"unsupported path family: {family}")
            panel[author, occasion] = latent @ rotation
    return panel


def _path_second_order_error(panel: np.ndarray, max_lag: int = 2) -> float:
    values = np.asarray(panel, dtype=float)
    summaries = np.empty(
        (
            values.shape[0],
            max_lag + 1,
            values.shape[-1],
            values.shape[-1],
        ),
        dtype=float,
    )
    for author in range(values.shape[0]):
        for lag in range(max_lag + 1):
            occasion_matrices = []
            for occasion in range(values.shape[1]):
                current = values[author, occasion]
                centered = current - current.mean(axis=0, keepdims=True)
                occasion_matrices.append(
                    centered.T @ np.roll(centered, -lag, axis=0)
                    / len(centered)
                )
            summaries[author, lag] = np.mean(occasion_matrices, axis=0)
    return float(np.max(np.ptp(summaries, axis=0)))


def _distribution_oracle_profile(
    family: str,
    parameters: np.ndarray,
    dimensions: int,
) -> np.ndarray:
    rng = np.random.default_rng(7_170_031)
    grid = rng.uniform(-1.0, 1.0, size=(4096, dimensions))
    profiles = []
    for parameter in parameters:
        score = _density_score(family, grid, parameter)
        profiles.append(np.sqrt(np.maximum(1.0 + 0.92 * score, 1e-8)))
    return np.asarray(profiles)


def _path_oracle_parameter(
    family: str,
    parameter: np.ndarray,
) -> np.ndarray:
    if family == "hsmm":
        theta = 0.01 + 0.09 * np.tanh(parameter)
        probability = np.column_stack([
            np.full(len(theta), 0.20),
            0.25 + theta[:, 0],
            0.30 - 2.0 * theta[:, 0],
            0.25 + theta[:, 0],
        ])
        survival = np.flip(
            np.cumsum(np.flip(probability, axis=1), axis=1),
            axis=1,
        )
        return probability / survival
    if family == "cycle":
        return np.sign(parameter)
    if family == "arch":
        return 0.25 + 0.20 * np.tanh(parameter)
    raise ValueError(f"unsupported path family: {family}")


def generate_m3_cross_family_world(
    *,
    world: str,
    spec: M3CrossFamilySpec,
    seed: int,
    disabled: frozenset[str] = frozenset(),
) -> tuple[M3CrossFamilyObserved, M3CrossFamilyTruth]:
    """Generate one blinded cross-family world and its separately held truth."""
    if world not in WORLD_TARGETS:
        raise ValueError(f"unsupported cross-family world: {world}")
    root = np.random.default_rng(seed)
    train_rng = np.random.default_rng(root.integers(0, 2**63 - 1))
    test_rng = np.random.default_rng(root.integers(0, 2**63 - 1))
    parameter_rng = np.random.default_rng(root.integers(0, 2**63 - 1))
    opportunity_rng = np.random.default_rng(root.integers(0, 2**63 - 1))
    targets = WORLD_TARGETS[world]
    parameters: dict[str, np.ndarray] = {}
    profiles: dict[str, np.ndarray] = {}
    design = {
        "authors": spec.authors,
        "occasions": spec.occasions,
        "events": spec.events,
        "dimensions": spec.dimensions,
        "partners": spec.partners,
        "noise": spec.noise,
        "independent_replicates": True,
        "common_support": True,
    }

    empty_shape = (
        spec.authors,
        spec.occasions,
        spec.events,
        spec.dimensions,
    )
    shared_shape = (spec.occasions, spec.events, spec.dimensions)
    condition_train = np.broadcast_to(
        train_rng.normal(size=shared_shape)[None, ...],
        empty_shape,
    ).copy()
    condition_test = np.broadcast_to(
        test_rng.normal(size=shared_shape)[None, ...],
        empty_shape,
    ).copy()
    partner_train = np.broadcast_to(
        train_rng.normal(size=shared_shape)[None, ...],
        empty_shape,
    ).copy()
    partner_test = np.broadcast_to(
        test_rng.normal(size=shared_shape)[None, ...],
        empty_shape,
    ).copy()
    partner_id_train = _partner_schedule(spec, test=False)
    partner_id_test = _partner_schedule(spec, test=True)
    exact_alias = world.startswith("alias_")

    if world.startswith("cf_d_"):
        family = world.removeprefix("cf_d_")
        parameter = _author_parameters(parameter_rng, spec.authors)
        rotation = _orthogonal(parameter_rng, spec.dimensions)
        active = "distribution" not in disabled
        if not active:
            parameter_for_data = np.zeros_like(parameter)
        else:
            parameter_for_data = parameter
        response_train = _distribution_panel(
            train_rng,
            family=family,
            spec=spec,
            parameters=parameter_for_data,
            rotation=rotation,
        )
        response_test = _distribution_panel(
            test_rng,
            family=family,
            spec=spec,
            parameters=parameter_for_data,
            rotation=rotation,
        )
        parameters["distribution"] = parameter
        profiles["distribution"] = _distribution_oracle_profile(
            family,
            parameter,
            spec.dimensions,
        )
        profiles["audit_rotation"] = rotation
    elif world.startswith("cf_o_") or world == "alias_operator_support":
        family = (
            "neural"
            if world == "alias_operator_support"
            else world.removeprefix("cf_o_")
        )
        condition_parameter = _author_parameters(
            parameter_rng,
            spec.authors,
        )
        partner_parameter = _author_parameters(
            parameter_rng,
            spec.authors,
        )
        active = True
        actor_intercept = parameter_rng.normal(
            scale=0.65,
            size=(spec.authors, 1, 1),
        )
        actor_intercept -= actor_intercept.mean(axis=0, keepdims=True)
        partner_intercept = parameter_rng.normal(
            scale=0.45,
            size=spec.partners,
        )
        partner_intercept -= partner_intercept.mean()
        dyad_intercept = parameter_rng.normal(
            scale=0.35,
            size=(spec.authors, spec.partners),
        )
        dyad_intercept = (
            dyad_intercept
            - dyad_intercept.mean(axis=0, keepdims=True)
            - dyad_intercept.mean(axis=1, keepdims=True)
            + dyad_intercept.mean()
        )
        occasion_intercept = parameter_rng.normal(
            scale=0.30,
            size=spec.occasions,
        )
        occasion_intercept -= occasion_intercept.mean()
        if exact_alias:
            shared_condition = opportunity_rng.uniform(
                -1.0,
                1.0,
                size=shared_shape,
            )
            shared_partner = opportunity_rng.uniform(
                -1.0,
                1.0,
                size=shared_shape,
            )
            condition_basis = _support_alias_surface(
                shared_condition,
            ).reshape(spec.occasions, spec.events, 2)
            partner_basis = _support_alias_surface(
                shared_partner,
            ).reshape(spec.occasions, spec.events, 2)
        else:
            shared_condition = opportunity_rng.normal(size=shared_shape)
            shared_partner = opportunity_rng.normal(size=shared_shape)
            joint_predictor = np.concatenate(
                [shared_condition, shared_partner],
                axis=2,
            )
            shared_partner_id = _partner_schedule(spec, test=False)[0]
            surface_rng = np.random.default_rng(seed + 31_337)
            condition_basis = _orthogonalize_surface(
                _raw_surface(family, shared_condition, surface_rng),
                joint_predictor,
                shared_partner_id,
            ).reshape(spec.occasions, spec.events, 2)
            partner_basis = _orthogonalize_surface(
                _raw_surface(family, shared_partner, surface_rng),
                joint_predictor,
                shared_partner_id,
            ).reshape(spec.occasions, spec.events, 2)
        train = _operator_panel(
            train_rng,
            spec=spec,
            condition_parameters=condition_parameter,
            partner_parameters=partner_parameter,
            test=False,
            active_condition=active and "condition" not in disabled,
            active_partner=active and "partner" not in disabled,
            actor_intercept=actor_intercept,
            partner_intercept=partner_intercept,
            dyad_intercept=dyad_intercept,
            occasion_intercept=occasion_intercept,
            shared_condition=shared_condition,
            shared_partner=shared_partner,
            condition_basis=condition_basis,
            partner_basis=partner_basis,
        )
        test = _operator_panel(
            test_rng,
            spec=spec,
            condition_parameters=condition_parameter,
            partner_parameters=partner_parameter,
            test=True,
            active_condition=active and "condition" not in disabled,
            active_partner=active and "partner" not in disabled,
            actor_intercept=actor_intercept,
            partner_intercept=partner_intercept,
            dyad_intercept=dyad_intercept,
            occasion_intercept=occasion_intercept,
            shared_condition=shared_condition,
            shared_partner=shared_partner,
            condition_basis=condition_basis,
            partner_basis=partner_basis,
        )
        response_train, condition_train, partner_train, partner_id_train = train
        response_test, condition_test, partner_test, partner_id_test = test
        parameters["condition"] = condition_parameter
        parameters["partner"] = partner_parameter
        profiles["condition"] = condition_parameter
        profiles["partner"] = partner_parameter
        profiles["audit_condition_basis"] = condition_basis
        profiles["audit_partner_basis"] = partner_basis
        profiles["audit_actor_intercept"] = actor_intercept
        profiles["audit_partner_intercept"] = partner_intercept
        profiles["audit_dyad_intercept"] = dyad_intercept
        profiles["audit_occasion_intercept"] = occasion_intercept
        design["leave_dyad_out"] = True
        design["same_partner_population"] = True
        design["stable_nuisance_across_replicates"] = True
    elif world.startswith("cf_kp_") or world == "alias_hidden":
        family = "cycle" if world == "alias_hidden" else world.removeprefix("cf_kp_")
        if family == "cycle":
            parameter = np.ones((spec.authors, 1), dtype=float)
            parameter[: spec.authors // 2] = -1.0
            parameter_rng.shuffle(parameter, axis=0)
        else:
            parameter = _author_parameters(
                parameter_rng,
                spec.authors,
                dimensions=1,
            )
        target = (
            "hazard"
            if family == "hsmm"
            else "direction"
            if family == "cycle"
            else "nonlinear_dynamics"
        )
        active = target not in disabled
        rotation = _orthogonal(parameter_rng, spec.dimensions)
        response_train = _path_panel(
            train_rng,
            family=family,
            spec=spec,
            parameters=parameter,
            active=active,
            rotation=rotation,
            emission_alias=exact_alias,
        )
        response_test = _path_panel(
            test_rng,
            family=family,
            spec=spec,
            parameters=parameter,
            active=active,
            rotation=rotation,
            emission_alias=exact_alias,
        )
        oracle_parameter = _path_oracle_parameter(family, parameter)
        parameters[target] = oracle_parameter
        profiles[target] = oracle_parameter
        profiles["audit_rotation"] = rotation
    elif world == "null_author":
        response_train = _path_panel(
            train_rng,
            family="arch",
            spec=spec,
            parameters=np.zeros((spec.authors, 1)),
            active=False,
            rotation=np.eye(spec.dimensions),
        )
        response_test = _path_panel(
            test_rng,
            family="arch",
            spec=spec,
            parameters=np.zeros((spec.authors, 1)),
            active=False,
            rotation=np.eye(spec.dimensions),
        )
    else:
        raise ValueError(f"unsupported cross-family world: {world}")

    validity: dict[str, float | bool | str] = {
        "finite": bool(
            np.isfinite(response_train).all()
            and np.isfinite(response_test).all()
        ),
    }
    if world.startswith("cf_kp_") or world == "alias_hidden":
        validity["second_order_max_range_train"] = _path_second_order_error(
            response_train
        )
        validity["second_order_max_range_test"] = _path_second_order_error(
            response_test
        )
    if world.startswith("cf_d_"):
        validity["density_eta"] = 0.92
    if world.startswith("cf_o_") or world == "alias_operator_support":
        validity["actor_degree"] = max(2, min(8, spec.partners // 4))
        if world == "alias_operator_support":
            validity["observed_support_bound"] = 1.0
            validity["alias_definition"] = (
                "signed fourth-power hinge: "
                "sign(x_j)*max(abs(x_j)-1,0)^4"
            )
    if world.startswith("cf_kp_") or world == "alias_hidden":
        validity["path_process_definition"] = {
            "cf_kp_hsmm": "constrained_hidden_renewal",
            "cf_kp_cycle": "nonreversible_three_state_cycle",
            "cf_kp_arch": "stationary_arch1",
            "alias_hidden": "hidden_cycle_with_author_invariant_emission",
        }[world]
        validity["posthoc_spectral_matching"] = False

    observed = M3CrossFamilyObserved(
        response_train=response_train,
        response_test=response_test,
        condition_train=condition_train,
        condition_test=condition_test,
        partner_train=partner_train,
        partner_test=partner_test,
        partner_id_train=partner_id_train,
        partner_id_test=partner_id_test,
        design=design,
    )
    truth = M3CrossFamilyTruth(
        world=world,
        active_targets=targets,
        author_parameters=parameters,
        oracle_profiles=profiles,
        exact_alias=exact_alias,
        validity=validity,
    )
    return observed, truth
