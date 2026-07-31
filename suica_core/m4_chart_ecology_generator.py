"""Synthetic worlds for M4-C.2 chart-covariant opportunity ecology."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import expit, logit
from scipy.spatial.distance import pdist, squareform

from .m4_chart_ecology_contracts import (
    M4ChartEcologyObserved,
    M4ChartEcologyTruth,
    validate_chart_ecology_observed,
)
from .m4_condition_manifold_contracts import (
    M4ConditionObserved,
    M4ConditionPanel,
)
from .m4_opportunity_contracts import (
    M4OpportunityObserved,
    M4OpportunityPanel,
)


WORLDS = (
    "linear_null_ecology",
    "linear_exogenous_selection",
    "endogenous_source_partition_matched",
    "endogenous_creation_expansion",
    "source_rotated_feedback",
    "fast_return_equal_marginal",
    "slow_hysteresis_equal_marginal",
    "history_gated_ecology",
    "selection_creation_compensation",
    "condition_alias_ecology",
    "hidden_opportunity_source_alias",
    "author_leakage",
    "response_leakage_circular",
    "evaluation_support_shift",
    "topology_mismatch",
)

ACTIVE_MECHANISMS = {
    "linear_null_ecology": (),
    "linear_exogenous_selection": ("selection",),
    "endogenous_source_partition_matched": ("creation",),
    "endogenous_creation_expansion": ("creation",),
    "source_rotated_feedback": ("creation",),
    "fast_return_equal_marginal": ("return",),
    "slow_hysteresis_equal_marginal": ("return", "hysteresis"),
    "history_gated_ecology": ("creation", "gate"),
    "selection_creation_compensation": ("selection", "creation"),
    "condition_alias_ecology": ("selection", "creation"),
    "hidden_opportunity_source_alias": (),
    "author_leakage": ("selection",),
    "response_leakage_circular": ("creation",),
    "evaluation_support_shift": ("creation",),
    "topology_mismatch": ("creation",),
}

EXPECTED_STATUS = {
    "linear_null_ecology": "IDENTIFIABLE",
    "linear_exogenous_selection": "IDENTIFIABLE",
    "endogenous_source_partition_matched": "IDENTIFIABLE",
    "endogenous_creation_expansion": "IDENTIFIABLE",
    "source_rotated_feedback": "IDENTIFIABLE",
    "fast_return_equal_marginal": "IDENTIFIABLE",
    "slow_hysteresis_equal_marginal": "IDENTIFIABLE",
    "history_gated_ecology": "IDENTIFIABLE",
    "selection_creation_compensation": "IDENTIFIABLE",
    "condition_alias_ecology": "REFUSE_MECHANISM",
    "hidden_opportunity_source_alias": "REFUSE_SOURCE",
    "author_leakage": "REFUSE_CHART",
    "response_leakage_circular": "REFUSE_CHART",
    "evaluation_support_shift": "REFUSE_SUPPORT",
    "topology_mismatch": "ATLAS_OR_REFUSE",
}


@dataclass(frozen=True)
class M4ChartEcologySpec:
    """Dimensions for one chart-covariant ecology population."""

    reference_authors: int = 32
    mechanism_authors: int = 16
    reference_calibration_points: int = 72
    reference_selection_points: int = 48
    categories: int = 16
    sources: int = 2
    pre_dimensions: int = 8
    response_dimensions: int = 2
    history_dimensions: int = 2
    calibration_occasions: int = 4
    selection_occasions: int = 2
    evaluation_occasions: int = 4
    events: int = 96
    pre_noise: float = 0.05
    response_noise: float = 0.13
    recency_decay: float = 5.0

    def __post_init__(self) -> None:
        if self.reference_authors < 8 or self.mechanism_authors < 8:
            raise ValueError("M4-C.2 requires at least eight authors per role")
        if min(
            self.reference_calibration_points,
            self.reference_selection_points,
            self.categories,
        ) < 16:
            raise ValueError("condition panels require at least 16 points")
        if self.sources < 2 or self.pre_dimensions < 6:
            raise ValueError("condition chart is underdimensioned")
        if self.response_dimensions != 2 or self.history_dimensions != 2:
            raise ValueError("M4-C.2 V1 uses two response/history dimensions")
        if self.events < 24:
            raise ValueError("dynamic panels require at least 24 events")


@dataclass(frozen=True)
class _ConditionSet:
    coordinate: np.ndarray
    raw_basis: np.ndarray
    geodesic: np.ndarray


def _orthogonal(rng: np.random.Generator, dimensions: int) -> np.ndarray:
    values = rng.normal(size=(dimensions, dimensions))
    q, _ = np.linalg.qr(values)
    return np.asarray(q, dtype=float)


def _condition_kind(world: str) -> str:
    if world in {
        "history_gated_ecology",
        "condition_alias_ecology",
    }:
        return "circle"
    if world == "topology_mismatch":
        return "branch"
    return "disk"


def _draw_conditions(
    rng: np.random.Generator,
    points: int,
    *,
    kind: str,
    support_scale: float = 1.0,
) -> _ConditionSet:
    if kind == "circle":
        angle = rng.uniform(-np.pi, np.pi, size=points)
        coordinate = support_scale * np.column_stack(
            [np.cos(angle), np.sin(angle)]
        )
        delta = np.abs(angle[:, None] - angle[None, :])
        geodesic = support_scale * np.minimum(
            delta,
            2.0 * np.pi - delta,
        )
        raw = np.column_stack(
            [
                np.cos(angle),
                np.sin(angle),
                np.cos(2.0 * angle),
                np.sin(2.0 * angle),
                np.cos(3.0 * angle),
                np.sin(3.0 * angle),
            ]
        )
    elif kind == "branch":
        branch = rng.integers(0, 3, size=points)
        radius = support_scale * rng.uniform(0.04, 1.0, size=points)
        angle = 2.0 * np.pi * branch / 3.0
        coordinate = np.column_stack(
            [radius * np.cos(angle), radius * np.sin(angle)]
        )
        same = branch[:, None] == branch[None, :]
        geodesic = np.where(
            same,
            np.abs(radius[:, None] - radius[None, :]),
            radius[:, None] + radius[None, :],
        )
        x, y = coordinate.T
        raw = np.column_stack(
            [x, y, radius, x * y, radius**2, branch.astype(float) - 1.0]
        )
    else:
        radius = support_scale * np.sqrt(rng.uniform(size=points))
        angle = rng.uniform(-np.pi, np.pi, size=points)
        coordinate = np.column_stack(
            [radius * np.cos(angle), radius * np.sin(angle)]
        )
        geodesic = squareform(pdist(coordinate))
        x, y = coordinate.T
        raw = np.column_stack(
            [x, y, x * y, x**2 - y**2, np.sin(np.pi * x), np.sin(np.pi * y)]
        )
    return _ConditionSet(
        coordinate=coordinate,
        raw_basis=raw,
        geodesic=np.asarray(geodesic, dtype=float),
    )


def _pad(values: np.ndarray, width: int) -> np.ndarray:
    if values.shape[1] >= width:
        return values[:, :width]
    columns = [values]
    for index in range(width - values.shape[1]):
        columns.append(
            np.tanh((index + 1.25) * values[:, [index % values.shape[1]]])
        )
    return np.column_stack(columns)


def _observable_features(
    world: str,
    conditions: _ConditionSet,
    *,
    width: int,
) -> np.ndarray:
    if world == "condition_alias_ecology":
        x, y = conditions.coordinate.T
        values = np.column_stack(
            [x**2, y**2, x * y, x**4, y**4, (x * y) ** 2]
        )
    else:
        values = conditions.raw_basis
    return _pad(values, width)


def _whiten_oracle(
    reference: np.ndarray,
    roles: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    center = np.mean(reference, axis=0)
    centered = reference - center
    covariance = centered.T @ centered / max(len(centered) - 1, 1)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    keep = eigenvalues > max(float(eigenvalues[0]), 1e-12) * 1e-7
    whitening = (
        eigenvectors[:, keep]
        / np.sqrt(np.maximum(eigenvalues[keep], 1e-12))[None]
    )
    return {
        role: np.column_stack(
            [np.ones(len(values)), (values - center) @ whitening]
        )
        for role, values in roles.items()
    }


def _pre_context(
    *,
    world: str,
    conditions: _ConditionSet,
    authors: int,
    source_maps: np.ndarray,
    response: np.ndarray,
    spec: M4ChartEcologySpec,
    rng: np.random.Generator,
) -> tuple[np.ndarray, tuple[str, ...]]:
    base = _observable_features(
        world,
        conditions,
        width=spec.pre_dimensions,
    )
    values = np.empty(
        (
            spec.sources,
            authors,
            len(base),
            spec.pre_dimensions,
        ),
        dtype=float,
    )
    fingerprints = rng.normal(size=(authors, spec.pre_dimensions))
    for source in range(spec.sources):
        source_base = base
        if world == "topology_mismatch" and source == 1:
            source_base = base.copy()
            source_base[:, 1] = np.abs(source_base[:, 1])
        transformed = source_base @ source_maps[source]
        current = np.broadcast_to(
            transformed[None],
            (authors, *transformed.shape),
        ).copy()
        if world == "author_leakage":
            current += 1.45 * fingerprints[:, None]
        if world == "response_leakage_circular":
            leaked = np.zeros_like(current)
            leaked[..., : response.shape[-1]] = response
            current += 1.10 * leaked
        current += rng.normal(scale=spec.pre_noise, size=current.shape)
        values[source] = current
    provenance = [
        f"pre_context_{index}"
        for index in range(spec.pre_dimensions)
    ]
    if world == "author_leakage":
        provenance[0] = "author_id"
    if world == "response_leakage_circular":
        provenance[0] = "current_response"
    return values, tuple(provenance)


def _condition_response(
    raw_basis: np.ndarray,
    *,
    intercept: np.ndarray,
    operator: np.ndarray,
    noise: float,
    rng: np.random.Generator,
) -> np.ndarray:
    response = (
        intercept[:, None]
        + np.einsum("udq,nq->und", operator, raw_basis)
    )
    return response + rng.normal(scale=noise, size=response.shape)


def _condition_panels(
    *,
    world: str,
    spec: M4ChartEcologySpec,
    seed: int,
) -> tuple[
    M4ConditionObserved,
    dict[str, np.ndarray],
    dict[str, np.ndarray],
]:
    rng = np.random.default_rng(seed)
    kind = _condition_kind(world)
    role_points = {
        "reference_calibration": spec.reference_calibration_points,
        "reference_selection": spec.reference_selection_points,
        "mechanism_calibration": spec.categories,
        "mechanism_selection": spec.categories,
        "mechanism_evaluation": spec.categories,
    }
    conditions = {
        role: _draw_conditions(
            np.random.default_rng(seed + 10_003 * (index + 1)),
            points,
            kind=kind,
            support_scale=(
                2.4
                if world == "evaluation_support_shift"
                and role == "mechanism_evaluation"
                else 1.0
            ),
        )
        for index, (role, points) in enumerate(role_points.items())
    }
    source_maps = np.stack(
        [_orthogonal(rng, spec.pre_dimensions) for _ in range(spec.sources)]
    )
    if world not in {
        "source_rotated_feedback",
        "topology_mismatch",
    }:
        source_maps[1:] = source_maps[0]

    reference_cal_intercept = rng.normal(
        scale=0.5,
        size=(spec.reference_authors, spec.response_dimensions),
    )
    reference_cal_operator = rng.normal(
        scale=0.4,
        size=(spec.reference_authors, spec.response_dimensions, 6),
    )
    reference_sel_intercept = rng.normal(
        scale=0.5,
        size=(spec.reference_authors, spec.response_dimensions),
    )
    reference_sel_operator = rng.normal(
        scale=0.4,
        size=(spec.reference_authors, spec.response_dimensions, 6),
    )
    mechanism_intercept = rng.normal(
        scale=0.5,
        size=(spec.mechanism_authors, spec.response_dimensions),
    )
    mechanism_operator = rng.normal(
        scale=0.4,
        size=(spec.mechanism_authors, spec.response_dimensions, 6),
    )
    response_roles = {
        "reference_calibration": (
            reference_cal_intercept,
            reference_cal_operator,
        ),
        "reference_selection": (
            reference_sel_intercept,
            reference_sel_operator,
        ),
        "mechanism_calibration": (
            mechanism_intercept,
            mechanism_operator,
        ),
        "mechanism_selection": (
            mechanism_intercept,
            mechanism_operator,
        ),
        "mechanism_evaluation": (
            mechanism_intercept,
            mechanism_operator,
        ),
    }
    panels: dict[str, M4ConditionPanel] = {}
    for index, (role, draw) in enumerate(conditions.items()):
        authors = (
            spec.reference_authors
            if role.startswith("reference")
            else spec.mechanism_authors
        )
        intercept, operator = response_roles[role]
        role_rng = np.random.default_rng(seed + 101_003 * (index + 1))
        response = _condition_response(
            draw.raw_basis,
            intercept=intercept,
            operator=operator,
            noise=spec.response_noise,
            rng=role_rng,
        )
        pre_context, provenance = _pre_context(
            world=world,
            conditions=draw,
            authors=authors,
            source_maps=source_maps,
            response=response,
            spec=spec,
            rng=role_rng,
        )
        panels[role] = M4ConditionPanel(
            pre_context=pre_context,
            response=response,
            provenance_fields=provenance,
        )
    observed = M4ConditionObserved(
        reference_calibration=panels["reference_calibration"],
        reference_selection=panels["reference_selection"],
        mechanism_calibration=panels["mechanism_calibration"],
        mechanism_selection=panels["mechanism_selection"],
        mechanism_evaluation=panels["mechanism_evaluation"],
        design={
            "reference_author_roles": "strictly_disjoint",
            "chart_sigma_field": "pre_response_only",
        },
    )
    oracle = _whiten_oracle(
        conditions["reference_calibration"].raw_basis,
        {
            "calibration": conditions["mechanism_calibration"].raw_basis,
            "selection": conditions["mechanism_selection"].raw_basis,
            "evaluation": conditions["mechanism_evaluation"].raw_basis,
        },
    )
    geodesic = {
        role: draw.geodesic
        for role, draw in conditions.items()
    }
    return observed, oracle, geodesic


def generate_m4_pre_response_condition(
    *,
    world: str,
    spec: M4ChartEcologySpec,
    seed: int,
) -> M4ConditionObserved:
    """Replay chart inputs without constructing response or mechanism truth.

    The full ecology generator consumes one response-noise draw before each
    pre-context draw. This entry point advances those role-local generators by
    the same amount, but never constructs the response surface itself. Its
    pre-context bytes therefore match the response-sanitized full generator
    while preserving a physical Phase-A/Phase-B boundary.
    """
    if world not in WORLDS:
        raise ValueError(f"unknown M4-C.2 world: {world}")
    if world == "response_leakage_circular":
        raise ValueError(
            "response_leakage_circular has no response-safe Phase-A view"
        )

    condition_seed = int(seed) + 1_009
    rng = np.random.default_rng(condition_seed)
    kind = _condition_kind(world)
    role_points = {
        "reference_calibration": spec.reference_calibration_points,
        "reference_selection": spec.reference_selection_points,
        "mechanism_calibration": spec.categories,
        "mechanism_selection": spec.categories,
        "mechanism_evaluation": spec.categories,
    }
    conditions = {
        role: _draw_conditions(
            np.random.default_rng(
                condition_seed + 10_003 * (index + 1)
            ),
            points,
            kind=kind,
            support_scale=(
                2.4
                if world == "evaluation_support_shift"
                and role == "mechanism_evaluation"
                else 1.0
            ),
        )
        for index, (role, points) in enumerate(role_points.items())
    }
    source_maps = np.stack(
        [_orthogonal(rng, spec.pre_dimensions) for _ in range(spec.sources)]
    )
    if world not in {
        "source_rotated_feedback",
        "topology_mismatch",
    }:
        source_maps[1:] = source_maps[0]

    panels: dict[str, M4ConditionPanel] = {}
    for index, (role, draw) in enumerate(conditions.items()):
        authors = (
            spec.reference_authors
            if role.startswith("reference")
            else spec.mechanism_authors
        )
        role_rng = np.random.default_rng(
            condition_seed + 101_003 * (index + 1)
        )
        response_shape = (
            authors,
            len(draw.raw_basis),
            spec.response_dimensions,
        )
        # Match the full generator's RNG position without constructing the
        # condition-dependent response surface.
        role_rng.normal(scale=spec.response_noise, size=response_shape)
        response = np.zeros(response_shape, dtype=float)
        pre_context, provenance = _pre_context(
            world=world,
            conditions=draw,
            authors=authors,
            source_maps=source_maps,
            response=response,
            spec=spec,
            rng=role_rng,
        )
        panels[role] = M4ConditionPanel(
            pre_context=pre_context,
            response=response,
            provenance_fields=provenance,
        )
    return M4ConditionObserved(
        reference_calibration=panels["reference_calibration"],
        reference_selection=panels["reference_selection"],
        mechanism_calibration=panels["mechanism_calibration"],
        mechanism_selection=panels["mechanism_selection"],
        mechanism_evaluation=panels["mechanism_evaluation"],
        design={
            "reference_author_roles": "strictly_disjoint",
            "chart_sigma_field": "pre_response_only",
        },
    )


def _paired_directions(
    rng: np.random.Generator,
    authors: int,
    width: int,
) -> np.ndarray:
    half = (authors + 1) // 2
    values = rng.normal(size=(half, width))
    values[:, 0] = 0.0
    values /= np.maximum(
        np.linalg.norm(values, axis=1, keepdims=True),
        1e-12,
    )
    paired = np.vstack([values, -values])[:authors]
    return paired[rng.permutation(authors)]


def _mechanism_parameters(
    *,
    world: str,
    oracle_width: int,
    spec: M4ChartEcologySpec,
    seed: int,
) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    authors = spec.mechanism_authors
    dimensions = spec.response_dimensions
    strength = np.linspace(0.75, 1.25, authors)
    strength = strength[rng.permutation(authors)]
    directions = _paired_directions(rng, authors, oracle_width)
    selection = np.zeros((authors, oracle_width))
    selection[:, 0] = 0.35
    creation = np.zeros((authors, oracle_width, dimensions))
    gate = np.zeros_like(creation)
    if "selection" in ACTIVE_MECHANISMS[world]:
        selection_scale = 3.00 if world == "condition_alias_ecology" else 1.20
        selection += selection_scale * strength[:, None] * directions
        # Active utility variation increases log-sum-exp and would otherwise
        # lower the outside-option rate despite matched population choices.
        selection[:, 0] = -0.30
    if "creation" in ACTIVE_MECHANISMS[world]:
        creation_scale = 10.00 if world == "condition_alias_ecology" else 1.35
        for author in range(authors):
            creation[author] = (
                creation_scale
                * strength[author]
                * np.outer(
                    directions[author],
                    np.asarray([1.0, -0.72]),
                )
            )
    if world == "selection_creation_compensation":
        creation *= -1.0
    if "gate" in ACTIVE_MECHANISMS[world]:
        for author in range(authors):
            gate[author] = (
                4.00
                * strength[author]
                * np.outer(
                    np.roll(directions[author], 1),
                    np.asarray([0.8, 1.0]),
                )
            )
    recovery = np.linspace(0.46, 0.72, authors)
    recovery = recovery[rng.permutation(authors)]
    response_transition = np.stack(
        [value * np.eye(dimensions) for value in recovery]
    )
    common_response = rng.normal(
        scale=0.20,
        size=(dimensions, oracle_width),
    )
    response_choice = np.stack(
        [
            common_response
            + 0.08 * strength[author] * rng.normal(
                size=(dimensions, oracle_width)
            )
            for author in range(authors)
        ]
    )
    external_persistence = np.full(authors, 0.24)
    if world == "fast_return_equal_marginal":
        external_persistence = np.linspace(0.03, 0.12, authors)
    elif world == "slow_hysteresis_equal_marginal":
        external_persistence = np.linspace(0.68, 0.82, authors)
    generated_base = np.zeros(authors)
    if "creation" in ACTIVE_MECHANISMS[world]:
        # Feedback variance raises the logistic mean. This calibrated base
        # keeps the union-menu marginal near the exogenous 0.62 arm.
        generated_base.fill(0.23)
    return {
        "selection": selection,
        "creation": creation,
        "gate": gate,
        "response_transition": response_transition,
        "response_choice": response_choice,
        "recovery": recovery,
        "external_persistence": external_persistence,
        "generated_base": generated_base,
    }


def _ensure_nonempty(
    external: np.ndarray,
    generated: np.ndarray,
    rng: np.random.Generator,
) -> None:
    if not np.any(np.logical_or(external, generated)):
        external[int(rng.integers(len(external)))] = True


def _choice_probabilities(
    basis: np.ndarray,
    menu: np.ndarray,
    coefficient: np.ndarray,
) -> np.ndarray:
    utilities = basis @ coefficient
    logits = np.concatenate(
        [np.asarray([0.0]), np.where(menu, utilities, -1e9)]
    )
    logits -= np.max(logits)
    probability = np.exp(logits)
    return probability / probability.sum()


def _condition_similarity(basis: np.ndarray) -> np.ndarray:
    values = basis[:, 1:]
    distances = squareform(pdist(values))
    positive = distances[distances > 1e-12]
    bandwidth = float(np.median(positive)) if len(positive) else 1.0
    return np.exp(-0.5 * (distances / max(bandwidth, 1e-8)) ** 2)


def _path_panel(
    *,
    world: str,
    basis: np.ndarray,
    parameters: dict[str, np.ndarray],
    occasions: int,
    spec: M4ChartEcologySpec,
    seed: int,
) -> M4OpportunityPanel:
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
                    gate = float(history[author, occasion, event, 0] > 0.0)
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


def generate_m4_chart_ecology_world(
    *,
    world: str,
    spec: M4ChartEcologySpec,
    seed: int,
) -> tuple[M4ChartEcologyObserved, M4ChartEcologyTruth]:
    """Generate a response-safe chart plus independent ecology path views."""
    if world not in WORLDS:
        raise ValueError(f"unknown M4-C.2 world: {world}")
    condition, oracle_basis, geodesic = _condition_panels(
        world=world,
        spec=spec,
        seed=seed + 1_009,
    )
    width = oracle_basis["calibration"].shape[1]
    parameters = _mechanism_parameters(
        world=world,
        oracle_width=width,
        spec=spec,
        seed=seed + 17_021,
    )
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
            panels[f"{view}_{role}"] = _path_panel(
                world=world,
                basis=oracle_basis[role],
                parameters=parameters,
                occasions=occasions,
                spec=spec,
                seed=(
                    seed
                    + view_index * 10_000_019
                    + role_index * 1_000_003
                ),
            )
    ecology = M4OpportunityObserved(
        train_calibration=panels["train_calibration"],
        train_selection=panels["train_selection"],
        train_evaluation=panels["train_evaluation"],
        test_calibration=panels["test_calibration"],
        test_selection=panels["test_selection"],
        test_evaluation=panels["test_evaluation"],
        design={
            "condition_coordinates_hidden": True,
            "role_order": "calibration -> selection -> evaluation",
            "chart_response_safe": True,
            "choice_kernel_inputs": "condition_basis|union_menu",
        },
    )
    observed = M4ChartEcologyObserved(
        condition=condition,
        ecology=ecology,
        reference_calibration_author_ids=tuple(
            range(spec.reference_authors)
        ),
        reference_selection_author_ids=tuple(
            range(spec.reference_authors, 2 * spec.reference_authors)
        ),
        design={
            "chart_and_mechanism_roles_separate": True,
            "reference_authors_disjoint": True,
            "geodesic_truth_hidden": True,
        },
    )
    validate_chart_ecology_observed(observed)
    truth = M4ChartEcologyTruth(
        world=world,
        expected_status=EXPECTED_STATUS[world],
        active_mechanisms=ACTIVE_MECHANISMS[world],
        oracle_basis=oracle_basis,
        author_parameters={
            **parameters,
            "evaluation_geodesic": geodesic["mechanism_evaluation"],
        },
        chart_alias=world == "condition_alias_ecology",
        source_alias=world == "hidden_opportunity_source_alias",
    )
    return observed, truth
