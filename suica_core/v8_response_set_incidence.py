"""Affine response-set incidence geometry for SUICA V8 planted worlds.

The module treats an author as a condition-indexed response image rather than
as one point. It keeps same-condition incidence separate from free image-set
incidence, because two authors can pass through the same response under
different conditions without sharing a conditional response.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.linalg import subspace_angles
from scipy.optimize import lsq_linear


@dataclass(frozen=True)
class ResponseSetSpec:
    """Observation design for one affine response-set pair."""

    halves: int = 2
    observers: int = 2
    line_conditions: int = 33
    surface_conditions: int = 81
    volume_conditions: int = 125
    noise_sd: float = 0.03


@dataclass(frozen=True)
class AffineMap:
    """One bounded affine condition-response map."""

    intercept: np.ndarray
    operator: np.ndarray

    @property
    def ambient_dimensions(self) -> int:
        return int(self.operator.shape[0])

    @property
    def condition_dimensions(self) -> int:
        return int(self.operator.shape[1])


WORLD_LABELS: dict[str, dict[str, Any]] = {
    "l2_same_cross": {
        "same": True, "free": True, "overlap": False, "attack": False,
    },
    "l2_coincident": {
        "same": True, "free": True, "overlap": True, "attack": False,
    },
    "l2_cross_condition": {
        "same": False, "free": True, "overlap": False, "attack": False,
    },
    "l2_parallel": {
        "same": False, "free": False, "overlap": False, "attack": False,
    },
    "l2_near_miss": {
        "same": False, "free": False, "overlap": False, "attack": False,
    },
    "l3_same_cross": {
        "same": True, "free": True, "overlap": False, "attack": False,
    },
    "l3_coincident": {
        "same": True, "free": True, "overlap": True, "attack": False,
    },
    "l3_cross_condition": {
        "same": False, "free": True, "overlap": False, "attack": False,
    },
    "l3_parallel": {
        "same": False, "free": False, "overlap": False, "attack": False,
    },
    "l3_skew": {
        "same": False, "free": False, "overlap": False, "attack": False,
    },
    "p3_same_line": {
        "same": True, "free": True, "overlap": False, "attack": False,
    },
    "p3_coincident": {
        "same": True, "free": True, "overlap": True, "attack": False,
    },
    "p3_cross_condition": {
        "same": False, "free": True, "overlap": False, "attack": False,
    },
    "p3_parallel": {
        "same": False, "free": False, "overlap": False, "attack": False,
    },
    "v3_coincident": {
        "same": True, "free": True, "overlap": True, "attack": False,
    },
    "v3_free_overlap": {
        "same": False, "free": True, "overlap": True, "attack": False,
    },
    "v3_disjoint": {
        "same": False, "free": False, "overlap": False, "attack": False,
    },
    "private_conditions": {
        "same": False, "free": False, "overlap": False, "attack": True,
    },
    "condition_permutation": {
        "same": False, "free": False, "overlap": False, "attack": True,
    },
    "half_shuffled": {
        "same": False, "free": False, "overlap": False, "attack": True,
    },
    "observer_specific": {
        "same": False, "free": False, "overlap": False, "attack": True,
    },
}


def _map(
    intercept: list[float],
    columns: list[list[float]],
) -> AffineMap:
    return AffineMap(
        intercept=np.asarray(intercept, dtype=float),
        operator=np.asarray(columns, dtype=float).T,
    )


def planted_pair(world: str) -> tuple[AffineMap, AffineMap]:
    """Return the registered oracle pair for one planted affine world."""
    x2 = _map([0.0, 0.0], [[1.0, 0.0]])
    x3 = _map([0.0, 0.0, 0.0], [[1.0, 0.0, 0.0]])
    if world == "l2_same_cross":
        return x2, _map([0.0, 0.0], [[0.0, 1.0]])
    if world == "l2_coincident":
        return x2, x2
    if world == "l2_cross_condition":
        return x2, _map([0.50, 0.0], [[0.0, 1.0]])
    if world == "l2_parallel":
        return x2, _map([0.0, 0.60], [[1.0, 0.0]])
    if world == "l2_near_miss":
        return x2, _map([1.08, 0.18], [[0.0, 0.08]])
    if world in {
        "private_conditions",
        "condition_permutation",
        "half_shuffled",
        "observer_specific",
    }:
        return x2, _map([0.0, 0.0], [[0.0, 1.0]])
    if world == "l3_same_cross":
        return x3, _map([0.0, 0.0, 0.0], [[0.0, 1.0, 0.0]])
    if world == "l3_coincident":
        return x3, x3
    if world == "l3_cross_condition":
        return x3, _map([0.50, 0.0, 0.0], [[0.0, 1.0, 0.0]])
    if world == "l3_parallel":
        return x3, _map([0.0, 0.60, 0.0], [[1.0, 0.0, 0.0]])
    if world == "l3_skew":
        return x3, _map([0.0, 0.0, 0.25], [[0.0, 1.0, 0.0]])
    xy = _map(
        [0.0, 0.0, 0.0],
        [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
    )
    if world == "p3_same_line":
        return xy, _map(
            [0.0, 0.0, 0.0],
            [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]],
        )
    if world == "p3_coincident":
        return xy, xy
    if world == "p3_cross_condition":
        return xy, _map(
            [0.40, 0.0, 0.20],
            [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]],
        )
    if world == "p3_parallel":
        return xy, _map(
            [0.0, 0.0, 0.60],
            [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        )
    cube = _map(
        [0.0, 0.0, 0.0],
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
    )
    if world == "v3_coincident":
        return cube, cube
    if world == "v3_free_overlap":
        return cube, _map(
            [0.50, 0.35, 0.25],
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
        )
    if world == "v3_disjoint":
        return cube, _map(
            [2.60, 0.0, 0.0],
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
        )
    raise ValueError(f"unsupported response-set world: {world}")


def condition_design(
    dimensions: int,
    count: int,
    *,
    rng: np.random.Generator,
) -> np.ndarray:
    """Build a bounded, full-rank condition design with center and corners."""
    if dimensions == 1:
        return np.linspace(-1.0, 1.0, count, dtype=float)[:, None]
    corners = np.asarray(
        np.meshgrid(*([[-1.0, 1.0]] * dimensions), indexing="ij")
    ).reshape(dimensions, -1).T
    center = np.zeros((1, dimensions), dtype=float)
    remaining = max(count - len(corners) - 1, 0)
    random = rng.uniform(-1.0, 1.0, size=(remaining, dimensions))
    return np.vstack([center, corners, random])[:count]


def evaluate_affine(model: AffineMap, conditions: np.ndarray) -> np.ndarray:
    """Evaluate a bounded affine response map."""
    return np.asarray(conditions, dtype=float) @ model.operator.T + model.intercept


def simulate_pair_observations(
    *,
    seed: int,
    world: str,
    spec: ResponseSetSpec,
    noise_sd: float | None = None,
) -> dict[str, Any]:
    """Generate two-half, two-observer observations for one oracle pair."""
    if world not in WORLD_LABELS:
        raise ValueError(f"unregistered response-set world: {world}")
    rng = np.random.default_rng(seed)
    left, right = planted_pair(world)
    q = left.condition_dimensions
    count = (
        spec.line_conditions
        if q == 1
        else spec.surface_conditions
        if q == 2
        else spec.volume_conditions
    )
    conditions = condition_design(q, count, rng=rng)
    sigma = float(spec.noise_sd if noise_sd is None else noise_sd)
    maps = (left, right)
    observations = np.empty(
        (
            2,
            spec.halves,
            spec.observers,
            len(conditions),
            left.ambient_dimensions,
        ),
        dtype=float,
    )
    for author, model in enumerate(maps):
        base = evaluate_affine(model, conditions)
        for half in range(spec.halves):
            for observer in range(spec.observers):
                current = base.copy()
                if world == "condition_permutation" and author == 1:
                    current = current[
                        rng.permutation(len(current))
                    ]
                elif world == "half_shuffled" and author == 1 and half == 1:
                    current = current + np.asarray([0.0, 0.55])
                elif (
                    world == "observer_specific"
                    and author == 1
                    and observer == 1
                ):
                    current = current + np.asarray([0.0, 0.55])
                observations[author, half, observer] = (
                    current
                    + rng.normal(scale=sigma, size=current.shape)
                )
    return {
        "world": world,
        "conditions": conditions,
        "observations": observations,
        "oracle_maps": maps,
        "condition_identity_shared": world != "private_conditions",
        **WORLD_LABELS[world],
    }


def fit_affine_views(
    conditions: np.ndarray,
    observations: np.ndarray,
) -> dict[str, Any]:
    """Fit one affine map per half/observer view and aggregate them."""
    conditions = np.asarray(conditions, dtype=float)
    observations = np.asarray(observations, dtype=float)
    design = np.column_stack([np.ones(len(conditions)), conditions])
    view_shape = observations.shape[:2]
    p = observations.shape[-1]
    q = conditions.shape[1]
    intercepts = np.empty((*view_shape, p), dtype=float)
    operators = np.empty((*view_shape, p, q), dtype=float)
    residual_rmse = np.empty(view_shape, dtype=float)
    for half in range(view_shape[0]):
        for observer in range(view_shape[1]):
            response = observations[half, observer]
            coefficient, *_ = np.linalg.lstsq(
                design,
                response,
                rcond=None,
            )
            fitted = design @ coefficient
            intercepts[half, observer] = coefficient[0]
            operators[half, observer] = coefficient[1:].T
            residual_rmse[half, observer] = float(
                np.sqrt(np.mean((response - fitted) ** 2))
            )
    aggregate = AffineMap(
        intercept=intercepts.mean(axis=(0, 1)),
        operator=operators.mean(axis=(0, 1)),
    )
    grid = dense_condition_grid(q)
    predictions = np.asarray([
        evaluate_affine(
            AffineMap(intercepts[h, r], operators[h, r]),
            grid,
        )
        for h in range(view_shape[0])
        for r in range(view_shape[1])
    ])
    dispersion = float(
        np.sqrt(np.mean((predictions - predictions.mean(axis=0)) ** 2))
    )
    return {
        "aggregate": aggregate,
        "intercepts": intercepts,
        "operators": operators,
        "residual_rmse": residual_rmse,
        "prediction_dispersion": dispersion,
    }


def bounded_affine_distance(
    left: AffineMap,
    right: AffineMap,
    *,
    same_condition: bool,
) -> dict[str, Any]:
    """Return the minimum distance between two bounded affine images."""
    offset = left.intercept - right.intercept
    if same_condition:
        matrix = left.operator - right.operator
    else:
        matrix = np.column_stack([left.operator, -right.operator])
    solution = lsq_linear(
        matrix,
        -offset,
        bounds=(-1.0, 1.0),
        lsmr_tol="auto",
    )
    residual = offset + matrix @ solution.x
    q = left.condition_dimensions
    return {
        "distance": float(np.linalg.norm(residual)),
        "left_condition": solution.x[:q].copy(),
        "right_condition": (
            solution.x[:q].copy()
            if same_condition
            else solution.x[q:].copy()
        ),
        "condition_gap": (
            0.0
            if same_condition
            else float(np.linalg.norm(solution.x[:q] - solution.x[q:]))
        ),
        "boundary": bool(np.any(np.abs(solution.x) > 0.999)),
    }


def dense_condition_grid(dimensions: int) -> np.ndarray:
    """Return a deterministic integration grid for dimensions one to three."""
    points = 129 if dimensions == 1 else 25 if dimensions == 2 else 11
    axis = np.linspace(-1.0, 1.0, points)
    mesh = np.meshgrid(*([axis] * dimensions), indexing="ij")
    return np.column_stack([item.ravel() for item in mesh])


def same_condition_coverage(
    left: AffineMap,
    right: AffineMap,
    *,
    radius: float,
) -> float:
    """Fraction of the common condition domain inside a response tube."""
    grid = dense_condition_grid(left.condition_dimensions)
    delta = evaluate_affine(left, grid) - evaluate_affine(right, grid)
    distance = np.linalg.norm(delta, axis=1)
    return float(np.mean(distance <= float(radius)))


def principal_angle_degrees(left: AffineMap, right: AffineMap) -> float:
    """Return the largest principal angle between response tangent spaces."""
    angles = subspace_angles(left.operator, right.operator)
    return float(np.degrees(np.max(angles))) if len(angles) else 0.0


def affine_rank(
    model: AffineMap,
    *,
    relative_threshold: float = 0.05,
) -> int:
    """Estimate intrinsic affine dimension from the operator spectrum."""
    singular = np.linalg.svd(model.operator, compute_uv=False)
    if not len(singular) or singular[0] <= 1e-12:
        return 0
    return int(np.sum(singular >= relative_threshold * singular[0]))


def box_count_dimension(
    model: AffineMap,
    *,
    samples: int = 100_000,
    seed: int = 0,
) -> dict[str, Any]:
    """Estimate finite-scale Minkowski dimension of one bounded affine image."""
    rng = np.random.default_rng(seed)
    points = evaluate_affine(
        model,
        rng.uniform(
            -1.0,
            1.0,
            size=(int(samples), model.condition_dimensions),
        ),
    )
    centered = points - points.mean(axis=0, keepdims=True)
    scale = float(np.max(np.linalg.norm(centered, axis=1)))
    normalized = centered / max(scale, 1e-12)
    epsilons = np.asarray([0.16, 0.13, 0.105, 0.085, 0.070, 0.058])
    counts = []
    for epsilon in epsilons:
        shifted_counts = []
        for shift_seed in range(3):
            shift = np.random.default_rng(shift_seed).uniform(
                0.0,
                epsilon,
                size=model.ambient_dimensions,
            )
            boxes = np.floor(
                (normalized + shift) / epsilon
            ).astype(np.int64)
            shifted_counts.append(len(np.unique(boxes, axis=0)))
        counts.append(float(np.mean(shifted_counts)))
    x = np.log(1.0 / epsilons)
    y = np.log(np.maximum(np.asarray(counts, dtype=float), 1.0))
    slope, intercept = np.polyfit(x, y, 1)
    fitted = slope * x + intercept
    total = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - float(np.sum((y - fitted) ** 2)) / max(total, 1e-12)
    return {
        "dimension": float(slope),
        "r2": r2,
        "epsilons": epsilons,
        "counts": np.asarray(counts, dtype=float),
    }


def analyze_pair(world: dict[str, Any]) -> dict[str, Any]:
    """Estimate same/free incidence and stability for one observed pair."""
    if not world["condition_identity_shared"]:
        return {
            "status": "REFUSE_CONDITION_IDENTITY_NOT_SHARED",
            "world": world["world"],
            "expected_same": bool(world["same"]),
            "expected_free": bool(world["free"]),
            "expected_overlap": bool(world["overlap"]),
            "expected_attack": bool(world["attack"]),
        }
    fits = [
        fit_affine_views(
            world["conditions"],
            world["observations"][author],
        )
        for author in range(2)
    ]
    left = fits[0]["aggregate"]
    right = fits[1]["aggregate"]
    oracle_left, oracle_right = world["oracle_maps"]
    same = bounded_affine_distance(
        left,
        right,
        same_condition=True,
    )
    free = bounded_affine_distance(
        left,
        right,
        same_condition=False,
    )
    uncertainty = float(
        np.sqrt(
            fits[0]["prediction_dispersion"] ** 2
            + fits[1]["prediction_dispersion"] ** 2
            + np.mean(fits[0]["residual_rmse"]) ** 2
            / len(world["conditions"])
            + np.mean(fits[1]["residual_rmse"]) ** 2
            / len(world["conditions"])
        )
    )
    uncertainty = max(uncertainty, 1e-8)
    view_same: list[float] = []
    view_free: list[float] = []
    for half in range(fits[0]["intercepts"].shape[0]):
        for observer in range(fits[0]["intercepts"].shape[1]):
            left_view = AffineMap(
                fits[0]["intercepts"][half, observer],
                fits[0]["operators"][half, observer],
            )
            right_view = AffineMap(
                fits[1]["intercepts"][half, observer],
                fits[1]["operators"][half, observer],
            )
            view_same.append(bounded_affine_distance(
                left_view,
                right_view,
                same_condition=True,
            )["distance"])
            view_free.append(bounded_affine_distance(
                left_view,
                right_view,
                same_condition=False,
            )["distance"])
    coefficient_stability = float(max(
        np.sqrt(np.mean(
            (
                fits[author]["intercepts"]
                - fits[author]["intercepts"].mean(axis=(0, 1))
            ) ** 2
        ))
        + np.sqrt(np.mean(
            (
                fits[author]["operators"]
                - fits[author]["operators"].mean(axis=(0, 1))
            ) ** 2
        ))
        for author in range(2)
    ))
    radius = 2.0 * uncertainty
    map_difference = float(np.sqrt(
        np.sum((left.intercept - right.intercept) ** 2)
        + np.sum((left.operator - right.operator) ** 2)
    ))
    return {
        "status": "ESTIMATE_READY",
        "world": world["world"],
        "same_distance": same["distance"],
        "free_distance": free["distance"],
        "same_z": same["distance"] / uncertainty,
        "free_z": free["distance"] / uncertainty,
        "free_condition_gap": free["condition_gap"],
        "same_boundary": same["boundary"],
        "free_boundary": free["boundary"],
        "uncertainty": uncertainty,
        "same_view_cv": float(
            np.std(view_same) / max(np.mean(view_same), uncertainty)
        ),
        "free_view_cv": float(
            np.std(view_free) / max(np.mean(view_free), uncertainty)
        ),
        "coefficient_stability": coefficient_stability,
        "residual_rmse": float(
            np.mean([
                fits[0]["residual_rmse"].mean(),
                fits[1]["residual_rmse"].mean(),
            ])
        ),
        "same_coverage": same_condition_coverage(
            left,
            right,
            radius=radius,
        ),
        "map_difference_z": map_difference / uncertainty,
        "principal_angle_degrees": principal_angle_degrees(left, right),
        "oracle_principal_angle_degrees": principal_angle_degrees(
            oracle_left,
            oracle_right,
        ),
        "principal_angle_error": abs(
            principal_angle_degrees(left, right)
            - principal_angle_degrees(oracle_left, oracle_right)
        ),
        "left_dimension": affine_rank(left),
        "right_dimension": affine_rank(right),
        "expected_dimension": left.condition_dimensions,
        "expected_same": bool(world["same"]),
        "expected_free": bool(world["free"]),
        "expected_overlap": bool(world["overlap"]),
        "expected_attack": bool(world["attack"]),
    }


def rigid_transform(
    model: AffineMap,
    rotation: np.ndarray,
    translation: np.ndarray,
) -> AffineMap:
    """Apply one common rigid transformation to a response set."""
    return AffineMap(
        intercept=rotation @ model.intercept + translation,
        operator=rotation @ model.operator,
    )


def finite_direction_family(
    *,
    authors: int,
    world: str,
) -> list[AffineMap]:
    """Construct finite 2D direction-rich line families."""
    angles = np.linspace(0.0, np.pi, authors, endpoint=False)
    result: list[AffineMap] = []
    for index, angle in enumerate(angles):
        direction = np.asarray([np.cos(angle), np.sin(angle)])
        if world == "common_anchor":
            center = np.zeros(2)
        elif world == "tangent_segments":
            radial_angle = 2.0 * np.pi * index / authors
            center = 3.0 * np.asarray([
                np.cos(radial_angle),
                np.sin(radial_angle),
            ])
            direction = np.asarray([
                -np.sin(radial_angle),
                np.cos(radial_angle),
            ])
        elif world == "paired_overlaps":
            pair = index // 2
            center = np.asarray([4.0 * pair, 0.0])
            if index % 2:
                direction = np.asarray([
                    np.cos(0.35 + 0.1 * pair),
                    np.sin(0.35 + 0.1 * pair),
                ])
            else:
                direction = np.asarray([
                    np.cos(0.35 + 0.1 * pair),
                    np.sin(0.35 + 0.1 * pair),
                ])
        else:
            raise ValueError(f"unsupported direction family: {world}")
        result.append(AffineMap(center, direction[:, None]))
    return result


def pairwise_incidence_graph(
    models: list[AffineMap],
    *,
    distance_threshold: float,
) -> np.ndarray:
    """Return an undirected same-condition incidence adjacency matrix."""
    n = len(models)
    result = np.zeros((n, n), dtype=bool)
    for left in range(n):
        for right in range(left + 1, n):
            distance = bounded_affine_distance(
                models[left],
                models[right],
                same_condition=True,
            )["distance"]
            result[left, right] = result[right, left] = (
                distance <= distance_threshold
            )
    return result


def graph_edge_f1(oracle: np.ndarray, predicted: np.ndarray) -> float:
    """Calculate edge F1 on the upper triangle of two simple graphs."""
    upper = np.triu_indices(len(oracle), 1)
    truth = np.asarray(oracle[upper], dtype=bool)
    estimate = np.asarray(predicted[upper], dtype=bool)
    tp = int(np.sum(truth & estimate))
    fp = int(np.sum(~truth & estimate))
    fn = int(np.sum(truth & ~estimate))
    if tp == 0 and fp == 0 and fn == 0:
        return 1.0
    return float(2 * tp / max(2 * tp + fp + fn, 1))
