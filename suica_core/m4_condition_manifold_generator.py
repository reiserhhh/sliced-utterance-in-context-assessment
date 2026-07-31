"""Synthetic worlds for M4-C response-safe condition-manifold discovery."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.spatial.distance import pdist, squareform

from .m4_condition_manifold_contracts import (
    M4ConditionObserved,
    M4ConditionPanel,
    M4ConditionTruth,
    validate_condition_observed,
)


WORLDS = (
    "true_linear_manifold",
    "true_nonlinear_multichart",
    "source_specific_rotations",
    "author_leakage",
    "response_leakage_circular",
    "topology_mismatch",
    "null_no_manifold",
    "condition_alias",
)


@dataclass(frozen=True)
class M4ConditionSpec:
    """Evidence budgets for one M4-C synthetic population."""

    reference_authors: int = 48
    mechanism_authors: int = 32
    calibration_points: int = 96
    selection_points: int = 64
    evaluation_points: int = 96
    sources: int = 2
    pre_dimensions: int = 8
    response_dimensions: int = 3
    response_basis_dimensions: int = 6
    pre_noise: float = 0.07
    response_noise: float = 0.12

    def __post_init__(self) -> None:
        if min(self.reference_authors, self.mechanism_authors) < 8:
            raise ValueError("M4-C requires at least eight authors per role")
        if min(
            self.calibration_points,
            self.selection_points,
            self.evaluation_points,
        ) < 16:
            raise ValueError("M4-C condition panels are too small")
        if self.sources < 2:
            raise ValueError("M4-C requires at least two condition sources")
        if self.pre_dimensions < 6:
            raise ValueError("pre_dimensions must be at least six")
        if self.response_basis_dimensions != 6:
            raise ValueError("M4-C V1 uses a six-dimensional response basis")


@dataclass(frozen=True)
class _ConditionDraw:
    coordinate: np.ndarray
    basis: np.ndarray
    geodesic: np.ndarray


def _orthogonal_map(
    rng: np.random.Generator,
    dimensions: int,
) -> np.ndarray:
    matrix = rng.normal(size=(dimensions, dimensions))
    q, _ = np.linalg.qr(matrix)
    return np.asarray(q, dtype=float)


def _disk_draw(rng: np.random.Generator, points: int) -> _ConditionDraw:
    radius = np.sqrt(rng.uniform(0.0, 1.0, size=points))
    angle = rng.uniform(-np.pi, np.pi, size=points)
    coordinate = np.column_stack(
        [radius * np.cos(angle), radius * np.sin(angle)]
    )
    x, y = coordinate.T
    basis = np.column_stack([x, y, x * y, x**2, y**2, x**2 - y**2])
    return _ConditionDraw(
        coordinate=coordinate,
        basis=basis,
        geodesic=squareform(pdist(coordinate)),
    )


def _circle_draw(rng: np.random.Generator, points: int) -> _ConditionDraw:
    angle = rng.uniform(-np.pi, np.pi, size=points)
    coordinate = np.column_stack([np.cos(angle), np.sin(angle)])
    delta = np.abs(angle[:, None] - angle[None, :])
    geodesic = np.minimum(delta, 2.0 * np.pi - delta)
    basis = np.column_stack(
        [
            np.cos(angle),
            np.sin(angle),
            np.cos(2.0 * angle),
            np.sin(2.0 * angle),
            np.cos(3.0 * angle),
            np.sin(3.0 * angle),
        ]
    )
    return _ConditionDraw(
        coordinate=coordinate,
        basis=basis,
        geodesic=geodesic,
    )


def _sphere_draw(rng: np.random.Generator, points: int) -> _ConditionDraw:
    coordinate = rng.normal(size=(points, 3))
    coordinate /= np.linalg.norm(coordinate, axis=1, keepdims=True)
    dot = np.clip(coordinate @ coordinate.T, -1.0, 1.0)
    x, y, z = coordinate.T
    basis = np.column_stack([x, y, z, x * y, y * z, z * x])
    return _ConditionDraw(
        coordinate=coordinate,
        basis=basis,
        geodesic=np.arccos(dot),
    )


def _branch_draw(rng: np.random.Generator, points: int) -> _ConditionDraw:
    branch = rng.integers(0, 3, size=points)
    radius = rng.uniform(0.03, 1.0, size=points)
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
    basis = np.column_stack(
        [x, y, radius, x * y, radius**2, branch.astype(float) - 1.0]
    )
    return _ConditionDraw(
        coordinate=coordinate,
        basis=basis,
        geodesic=geodesic,
    )


def _hidden_draw(rng: np.random.Generator, points: int) -> _ConditionDraw:
    latent = rng.normal(size=(points, 3))
    basis = np.column_stack(
        [
            latent[:, 0],
            latent[:, 1],
            latent[:, 2],
            latent[:, 0] * latent[:, 1],
            latent[:, 1] * latent[:, 2],
            latent[:, 2] * latent[:, 0],
        ]
    )
    return _ConditionDraw(
        coordinate=latent,
        basis=basis,
        geodesic=squareform(pdist(latent)),
    )


def _draw_for_world(
    world: str,
    rng: np.random.Generator,
    points: int,
) -> _ConditionDraw:
    if world in {
        "true_linear_manifold",
        "author_leakage",
        "response_leakage_circular",
    }:
        return _disk_draw(rng, points)
    if world in {"source_specific_rotations", "condition_alias"}:
        return _circle_draw(rng, points)
    if world == "true_nonlinear_multichart":
        return _sphere_draw(rng, points)
    if world == "topology_mismatch":
        return _branch_draw(rng, points)
    if world == "null_no_manifold":
        return _hidden_draw(rng, points)
    raise ValueError(f"unsupported M4-C world: {world}")


def _base_pre_features(world: str, draw: _ConditionDraw) -> np.ndarray:
    coordinate = draw.coordinate
    if world == "condition_alias":
        angle = np.arctan2(coordinate[:, 1], coordinate[:, 0])
        folded = np.cos(angle)
        return np.column_stack(
            [
                folded,
                folded**2,
                folded**3,
                np.cos(2.0 * angle),
                np.cos(3.0 * angle),
                np.ones(len(angle)),
            ]
        )
    if coordinate.shape[1] == 2:
        x, y = coordinate.T
        return np.column_stack([x, y, x * y, x**2, y**2, x**2 - y**2])
    x, y, z = coordinate.T
    return np.column_stack([x, y, z, x * y, y * z, z * x])


def _pad_features(values: np.ndarray, dimensions: int) -> np.ndarray:
    if values.shape[1] > dimensions:
        return values[:, :dimensions]
    if values.shape[1] == dimensions:
        return values
    extra = []
    for index in range(dimensions - values.shape[1]):
        column = values[:, index % values.shape[1]]
        extra.append(np.tanh((index + 1.5) * column))
    return np.column_stack([values, *extra])


def _author_response_parameters(
    rng: np.random.Generator,
    authors: int,
    spec: M4ConditionSpec,
) -> tuple[np.ndarray, np.ndarray]:
    intercept = rng.normal(
        scale=0.65,
        size=(authors, spec.response_dimensions),
    )
    operator = rng.normal(
        scale=0.52,
        size=(
            authors,
            spec.response_dimensions,
            spec.response_basis_dimensions,
        ),
    )
    return intercept, operator


def _response(
    draw: _ConditionDraw,
    intercept: np.ndarray,
    operator: np.ndarray,
    *,
    noise: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    noiseless = (
        intercept[:, None, :]
        + np.einsum("udq,nq->und", operator, draw.basis)
    )
    observed = noiseless + rng.normal(scale=noise, size=noiseless.shape)
    return observed, noiseless


def _pre_context(
    *,
    world: str,
    draw: _ConditionDraw,
    response: np.ndarray,
    authors: int,
    source_maps: np.ndarray,
    author_fingerprint: np.ndarray,
    spec: M4ConditionSpec,
    rng: np.random.Generator,
    role_seed: int,
) -> tuple[np.ndarray, tuple[str, ...]]:
    base = _pad_features(
        _base_pre_features(world, draw),
        spec.pre_dimensions,
    )
    output = np.empty(
        (spec.sources, authors, len(base), spec.pre_dimensions),
        dtype=float,
    )
    for source in range(spec.sources):
        if world == "null_no_manifold":
            source_base = np.random.default_rng(
                role_seed + 1009 * (source + 1)
            ).normal(size=base.shape)
        elif world == "topology_mismatch" and source == 1:
            source_base = base.copy()
            source_base[:, 1] = np.abs(source_base[:, 1])
        else:
            source_base = base
        transformed = source_base @ source_maps[source]
        values = np.broadcast_to(
            transformed[None],
            (authors, *transformed.shape),
        ).copy()
        if world == "author_leakage":
            values += 1.35 * author_fingerprint[:, None, :]
        if world == "response_leakage_circular":
            leaked = np.zeros_like(values)
            width = min(response.shape[-1], values.shape[-1])
            leaked[..., :width] = response[..., :width]
            values += 1.10 * leaked
        values += rng.normal(scale=spec.pre_noise, size=values.shape)
        output[source] = values
    provenance = [f"pre_context_{index}" for index in range(spec.pre_dimensions)]
    if world == "response_leakage_circular":
        provenance[0] = "current_response"
    return output, tuple(provenance)


def _panel(
    *,
    world: str,
    points: int,
    authors: int,
    intercept: np.ndarray,
    operator: np.ndarray,
    source_maps: np.ndarray,
    author_fingerprint: np.ndarray,
    spec: M4ConditionSpec,
    seed: int,
) -> tuple[M4ConditionPanel, _ConditionDraw, np.ndarray]:
    rng = np.random.default_rng(seed)
    draw = _draw_for_world(world, rng, points)
    response, noiseless = _response(
        draw,
        intercept,
        operator,
        noise=spec.response_noise,
        rng=rng,
    )
    pre, provenance = _pre_context(
        world=world,
        draw=draw,
        response=response,
        authors=authors,
        source_maps=source_maps,
        author_fingerprint=author_fingerprint,
        spec=spec,
        rng=rng,
        role_seed=seed,
    )
    return (
        M4ConditionPanel(
            pre_context=pre,
            response=response,
            provenance_fields=provenance,
        ),
        draw,
        noiseless,
    )


def generate_m4_condition_world(
    *,
    world: str,
    spec: M4ConditionSpec,
    seed: int,
) -> tuple[M4ConditionObserved, M4ConditionTruth]:
    """Generate one condition-geometry world without exposing truth to fitters."""
    if world not in WORLDS:
        raise ValueError(f"unknown M4-C world: {world}")
    rng = np.random.default_rng(seed)
    source_maps = np.stack(
        [
            _orthogonal_map(rng, spec.pre_dimensions)
            for _ in range(spec.sources)
        ]
    )
    if world not in {"source_specific_rotations", "true_nonlinear_multichart"}:
        source_maps[1:] = source_maps[0]

    reference_intercept, reference_operator = _author_response_parameters(
        rng,
        spec.reference_authors,
        spec,
    )
    mechanism_intercept, mechanism_operator = _author_response_parameters(
        rng,
        spec.mechanism_authors,
        spec,
    )
    reference_fingerprint = rng.normal(
        size=(spec.reference_authors, spec.pre_dimensions)
    )
    mechanism_fingerprint = rng.normal(
        size=(spec.mechanism_authors, spec.pre_dimensions)
    )
    role_specs: tuple[
        tuple[str, int, int, np.ndarray, np.ndarray, np.ndarray],
        ...,
    ] = (
        (
            "reference_calibration",
            spec.calibration_points,
            spec.reference_authors,
            reference_intercept,
            reference_operator,
            reference_fingerprint,
        ),
        (
            "reference_selection",
            spec.selection_points,
            spec.reference_authors,
            reference_intercept,
            reference_operator,
            reference_fingerprint,
        ),
        (
            "mechanism_calibration",
            spec.calibration_points,
            spec.mechanism_authors,
            mechanism_intercept,
            mechanism_operator,
            mechanism_fingerprint,
        ),
        (
            "mechanism_selection",
            spec.selection_points,
            spec.mechanism_authors,
            mechanism_intercept,
            mechanism_operator,
            mechanism_fingerprint,
        ),
        (
            "mechanism_evaluation",
            spec.evaluation_points,
            spec.mechanism_authors,
            mechanism_intercept,
            mechanism_operator,
            mechanism_fingerprint,
        ),
    )
    panels: dict[str, M4ConditionPanel] = {}
    draws: dict[str, _ConditionDraw] = {}
    noiseless: dict[str, np.ndarray] = {}
    for role_index, (
        role,
        points,
        authors,
        intercept,
        operator,
        fingerprint,
    ) in enumerate(role_specs):
        panel, draw, surface = _panel(
            world=world,
            points=points,
            authors=authors,
            intercept=intercept,
            operator=operator,
            source_maps=source_maps,
            author_fingerprint=fingerprint,
            spec=spec,
            seed=seed + 10_003 * (role_index + 1),
        )
        panels[role] = panel
        draws[role] = draw
        noiseless[role] = surface

    observed = M4ConditionObserved(
        reference_calibration=panels["reference_calibration"],
        reference_selection=panels["reference_selection"],
        mechanism_calibration=panels["mechanism_calibration"],
        mechanism_selection=panels["mechanism_selection"],
        mechanism_evaluation=panels["mechanism_evaluation"],
        design={
            "chart_sigma_field": "pre_response_only",
            "reference_authors": spec.reference_authors,
            "mechanism_authors": spec.mechanism_authors,
        },
    )
    validate_condition_observed(observed)
    expected = {
        "true_linear_manifold": "IDENTIFIABLE",
        "true_nonlinear_multichart": "IDENTIFIABLE",
        "source_specific_rotations": "IDENTIFIABLE",
        "topology_mismatch": "ATLAS_OR_REFUSE",
        "author_leakage": "REFUSE",
        "response_leakage_circular": "REFUSE",
        "null_no_manifold": "REFUSE",
        "condition_alias": "QUOTIENT_ONLY",
    }[world]
    topology = {
        "true_linear_manifold": "surface",
        "true_nonlinear_multichart": "closed_surface",
        "source_specific_rotations": "cycle",
        "author_leakage": "surface",
        "response_leakage_circular": "surface",
        "topology_mismatch": "branch",
        "null_no_manifold": "none",
        "condition_alias": "cycle_aliased",
    }[world]
    truth = M4ConditionTruth(
        world=world,
        expected_chart_status=expected,
        expected_topology=topology,
        geodesic_distances={
            role: draw.geodesic
            for role, draw in draws.items()
        },
        response_basis={
            role: draw.basis
            for role, draw in draws.items()
        },
        noiseless_response=noiseless,
        latent_coordinates={
            role: draw.coordinate
            for role, draw in draws.items()
        },
        alias=world == "condition_alias",
        leakage=world in {
            "author_leakage",
            "response_leakage_circular",
        },
    )
    return observed, truth
