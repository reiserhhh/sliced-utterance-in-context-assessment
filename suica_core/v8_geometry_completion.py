"""Scale, null, transversality, and nonlinear-manifold estimators for V3.5."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist
from sklearn.metrics import adjusted_rand_score, f1_score

from suica_core.v8_incidence_incremental import (
    _cores_overlap,
    _inclusion_maximal_cores,
    _predicted_labels,
    exact_maximal_hyperedges,
)
from suica_core.v8_incidence_multiplicity import minimum_enclosing_ball


@dataclass(frozen=True)
class GeometryCompletionSpec:
    """Frozen V3.5 simulator and estimator settings."""

    authors: int = 24
    groups: int = 4
    conditions: int = 33
    views: int = 4
    active_conditions: int = 8
    ambient: int = 2
    radius_min: float = 1.0
    radius_max: float = 1.06
    shape_birth_radius: float = 1.02
    noise_sd: float = 0.002
    continuous_persistence_threshold: float = 0.08
    minimum_group_coverage: float = 0.75
    permutations: int = 999
    grid_sizes: tuple[int, ...] = (9, 17, 33)
    curve_points: int = 13
    surface_grid: int = 13
    jet_noise_sd: float = 0.002
    rank_threshold: float = 0.45
    rank_margin: float = 0.10
    intersection_tolerance: float = 0.05
    hessian_threshold: float = 0.50
    bootstrap_repetitions: int = 199


def _balanced_labels(spec: GeometryCompletionSpec, seed: int) -> np.ndarray:
    labels = np.arange(spec.authors, dtype=int) % spec.groups
    return labels[np.random.default_rng(seed).permutation(spec.authors)]


def _base_positions(spec: GeometryCompletionSpec) -> np.ndarray:
    angles = 2.0 * np.pi * np.arange(spec.authors) / spec.authors
    points = np.column_stack([
        20.0 * np.cos(angles),
        20.0 * np.sin(angles),
    ])
    return np.repeat(points[:, None, :], spec.conditions, axis=1)


def _group_anchors() -> np.ndarray:
    return np.asarray([
        [-8.0, -8.0],
        [-8.0, 8.0],
        [8.0, -8.0],
        [8.0, 8.0],
    ])


def simulate_scale_pair(
    *,
    seed: int,
    spec: GeometryCompletionSpec,
    noiseless: bool = False,
) -> dict[str, Any]:
    """Generate stable and condition-permuted worlds with matched geometry."""
    labels = _balanced_labels(spec, seed)
    truth = _base_positions(spec)
    anchors = _group_anchors()
    active = np.arange(spec.active_conditions)
    rng = np.random.default_rng(seed + 10_003)
    for condition in active:
        phase = rng.uniform(0.0, 2.0 * np.pi)
        angles = 2.0 * np.pi * np.arange(6) / 6.0 + phase
        offsets = spec.shape_birth_radius * np.column_stack([
            np.cos(angles),
            np.sin(angles),
        ])
        for group in range(spec.groups):
            members = np.sort(np.flatnonzero(labels == group))
            truth[members, condition] = anchors[group] + offsets

    positive_views = []
    sigma = 0.0 if noiseless else spec.noise_sd
    for view in range(spec.views):
        noise = np.random.default_rng(
            seed + 20_011 + 101 * view
        ).normal(scale=sigma, size=truth.shape)
        positive_views.append(truth + noise)
    positive_views = np.asarray(positive_views)

    negative_views = positive_views.copy()
    condition_permutations = []
    for condition in active:
        permutation = np.random.default_rng(
            seed + 30_013 + int(condition)
        ).permutation(spec.authors)
        condition_permutations.append(permutation)
        negative_views[:, :, condition] = positive_views[
            :,
            permutation,
            condition,
        ]
    return {
        "labels": labels,
        "active_conditions": active,
        "positive_views": positive_views,
        "negative_views": negative_views,
        "condition_permutations": np.asarray(condition_permutations),
    }


def _candidate_edges(
    views: np.ndarray,
    *,
    spec: GeometryCompletionSpec,
) -> set[frozenset[int]]:
    candidates: set[frozenset[int]] = set()
    for condition in range(spec.conditions):
        per_view = []
        for view in range(spec.views):
            edges, _ = exact_maximal_hyperedges(
                views[view, :, condition],
                radius=spec.radius_max,
                node_cap=25_000,
            )
            per_view.append({
                frozenset(edge) for edge in edges if len(edge) >= 3
            })
        if per_view:
            candidates.update(set.intersection(*per_view))
    return candidates


def exact_birth_profiles(
    views: np.ndarray,
    candidates: set[frozenset[int]],
    *,
    spec: GeometryCompletionSpec,
) -> dict[frozenset[int], np.ndarray]:
    """Return cross-view worst-case exact MEB birth at each condition."""
    profiles: dict[frozenset[int], np.ndarray] = {}
    for candidate in candidates:
        members = sorted(candidate)
        birth = np.zeros(spec.conditions, dtype=float)
        for condition in range(spec.conditions):
            radii = [
                minimum_enclosing_ball(
                    views[view, members, condition]
                )[1]
                for view in range(spec.views)
            ]
            birth[condition] = max(radii)
        profiles[candidate] = birth
    return profiles


def continuous_persistence(
    birth: np.ndarray,
    *,
    multiplicity: int,
    spec: GeometryCompletionSpec,
) -> float:
    """Integrate simplex survival over the frozen radius interval."""
    width = spec.radius_max - spec.radius_min
    survival = np.clip(
        (
            spec.radius_max
            - np.maximum(spec.radius_min, birth)
        )
        / width,
        0.0,
        1.0,
    )
    specificity = (
        spec.authors - multiplicity
    ) / max(spec.authors - 2, 1)
    return float(specificity * np.mean(survival))


def grid_persistence(
    birth: np.ndarray,
    *,
    multiplicity: int,
    grid_size: int,
    spec: GeometryCompletionSpec,
) -> float:
    """Approximate radius survival on one registered finite grid."""
    grid = np.linspace(spec.radius_min, spec.radius_max, grid_size)
    survival = np.mean(
        grid[None, :] >= birth[:, None],
        axis=1,
    )
    specificity = (
        spec.authors - multiplicity
    ) / max(spec.authors - 2, 1)
    return float(specificity * np.mean(survival))


def _scores_from_profiles(
    profiles: dict[frozenset[int], np.ndarray],
    *,
    spec: GeometryCompletionSpec,
) -> dict[frozenset[int], float]:
    return {
        candidate: continuous_persistence(
            birth,
            multiplicity=len(candidate),
            spec=spec,
        )
        for candidate, birth in profiles.items()
    }


def _restricted_max_statistics(
    profiles: dict[frozenset[int], np.ndarray],
    *,
    seed: int,
    spec: GeometryCompletionSpec,
) -> np.ndarray:
    """Re-search after independent within-condition identity permutations."""
    cell_records: list[list[tuple[frozenset[int], float]]] = [
        [] for _ in range(spec.conditions)
    ]
    width = spec.radius_max - spec.radius_min
    for candidate, birth in profiles.items():
        specificity = (
            spec.authors - len(candidate)
        ) / max(spec.authors - 2, 1)
        survival = np.clip(
            (
                spec.radius_max
                - np.maximum(spec.radius_min, birth)
            )
            / width,
            0.0,
            1.0,
        )
        for condition, value in enumerate(survival):
            if value > 0.0:
                cell_records[condition].append(
                    (candidate, float(value * specificity))
                )

    output = np.zeros(spec.permutations, dtype=float)
    rng = np.random.default_rng(seed)
    for repetition in range(spec.permutations):
        totals: dict[frozenset[int], float] = {}
        for records in cell_records:
            if not records:
                continue
            permutation = rng.permutation(spec.authors)
            for candidate, value in records:
                mapped = frozenset(
                    int(permutation[item]) for item in candidate
                )
                totals[mapped] = totals.get(mapped, 0.0) + value
        output[repetition] = (
            max(totals.values(), default=0.0) / spec.conditions
        )
    return output


def analyze_scale_world(
    views: np.ndarray,
    labels: np.ndarray,
    *,
    seed: int,
    spec: GeometryCompletionSpec,
) -> dict[str, Any]:
    """Discover persistent author sets and test against restricted max-T."""
    candidates = _candidate_edges(views, spec=spec)
    profiles = exact_birth_profiles(views, candidates, spec=spec)
    scores = _scores_from_profiles(profiles, spec=spec)
    passing = _inclusion_maximal_cores(
        scores,
        threshold=spec.continuous_persistence_threshold,
    )
    ambiguity = _cores_overlap(passing)
    selected = [] if ambiguity else passing
    observed_max = max(scores.values(), default=0.0)
    null_max = _restricted_max_statistics(
        profiles,
        seed=seed + 70_001,
        spec=spec,
    )
    p_fwer = float(
        (
            1
            + np.count_nonzero(null_max >= observed_max - 1e-12)
        )
        / (len(null_max) + 1)
    )
    coverage = (
        len(set().union(*selected)) / spec.authors
        if selected else 0.0
    )
    group_claim = bool(
        not ambiguity
        and coverage >= spec.minimum_group_coverage
        and p_fwer <= 0.01
    )
    predicted = _predicted_labels(spec.authors, selected)
    upper = np.triu_indices(spec.authors, 1)
    truth_pairs = (labels[upper[0]] == labels[upper[1]]).astype(int)
    predicted_pairs = (
        predicted[upper[0]] == predicted[upper[1]]
    ).astype(int)

    grid_agreement: dict[str, bool] = {}
    for size in spec.grid_sizes:
        grid_scores = {
            candidate: grid_persistence(
                birth,
                multiplicity=len(candidate),
                grid_size=size,
                spec=spec,
            )
            for candidate, birth in profiles.items()
        }
        grid_passing = _inclusion_maximal_cores(
            grid_scores,
            threshold=spec.continuous_persistence_threshold,
        )
        grid_selected = [] if _cores_overlap(grid_passing) else grid_passing
        grid_agreement[str(size)] = {
            frozenset(item) for item in grid_selected
        } == {frozenset(item) for item in selected}

    edge_sizes = [len(item) for item in candidates]
    active_births = [
        float(value)
        for birth in profiles.values()
        for value in birth
        if value <= spec.radius_max
    ]
    return {
        "status": "ESTIMATE_READY",
        "group_claim": group_claim,
        "refused": ambiguity,
        "coverage": coverage,
        "p_fwer": p_fwer,
        "observed_max_persistence": observed_max,
        "null_max_mean": float(np.mean(null_max)),
        "null_max_99": float(np.quantile(null_max, 0.99)),
        "selected_groups": [
            sorted(int(item) for item in group) for group in selected
        ],
        "candidate_count": len(candidates),
        "mean_candidate_size": (
            float(np.mean(edge_sizes)) if edge_sizes else 0.0
        ),
        "mean_active_birth": (
            float(np.mean(active_births)) if active_births else np.nan
        ),
        "grid_agreement": grid_agreement,
        "group_f1": float(f1_score(
            truth_pairs,
            predicted_pairs,
            zero_division=0,
        )),
        "group_ari": float(adjusted_rand_score(labels, predicted)),
    }


def scale_matching_features(
    views: np.ndarray,
    *,
    spec: GeometryCompletionSpec,
) -> np.ndarray:
    """Return label-free condition geometry summaries for matching audits."""
    rows = []
    for condition in range(spec.conditions):
        points = views.mean(axis=0)[:, condition]
        edges, _ = exact_maximal_hyperedges(
            points,
            radius=spec.radius_max,
            node_cap=25_000,
        )
        sizes = [len(edge) for edge in edges]
        births = [
            minimum_enclosing_ball(points[list(edge)])[1]
            for edge in edges
        ]
        rows.append([
            len(edges),
            float(np.mean(sizes)) if sizes else 0.0,
            float(np.mean(births)) if births else 0.0,
        ])
    return np.asarray(rows, dtype=float)


def _quadratic_curve_jet(
    t: np.ndarray,
    response: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    design = np.column_stack([
        np.ones(len(t)),
        t,
        0.5 * t**2,
    ])
    coefficient, *_ = np.linalg.lstsq(design, response, rcond=None)
    return coefficient[0], coefficient[1], coefficient[2]


def simulate_curve_relation(
    *,
    seed: int,
    world: str,
    spec: GeometryCompletionSpec,
) -> dict[str, Any]:
    """Simulate two same-condition response curves near one contact."""
    t = np.linspace(-0.30, 0.30, spec.curve_points)
    first = np.column_stack([t, np.zeros_like(t)])
    if world == "transverse":
        second = np.column_stack([np.zeros_like(t), t])
    elif world == "tangent":
        second = np.column_stack([t, 0.8 * t**2])
    elif world == "coincident":
        second = first.copy()
    elif world == "near_miss":
        second = first + np.asarray([0.0, 0.15])
    elif world == "boundary":
        angle = 0.45
        second = np.column_stack([
            np.cos(angle) * t,
            np.sin(angle) * t,
        ])
    else:
        raise ValueError(f"unsupported curve world: {world}")
    observations = []
    rng = np.random.default_rng(seed)
    for _ in range(spec.views):
        observations.append(np.stack([
            first + rng.normal(scale=spec.jet_noise_sd, size=first.shape),
            second + rng.normal(scale=spec.jet_noise_sd, size=second.shape),
        ]))
    return {
        "world": world,
        "conditions": t,
        "observations": np.asarray(observations),
    }


def _bootstrap_interval(
    values: np.ndarray,
    *,
    seed: int,
    repetitions: int,
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    draws = np.asarray([
        np.mean(rng.choice(values, size=len(values), replace=True))
        for _ in range(repetitions)
    ])
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def classify_curve_relation(
    sample: dict[str, Any],
    *,
    seed: int,
    spec: GeometryCompletionSpec,
) -> dict[str, Any]:
    """Classify local curve contact from cross-view quadratic jets."""
    separations = []
    singular = []
    hessian = []
    for view in sample["observations"]:
        first = _quadratic_curve_jet(sample["conditions"], view[0])
        second = _quadratic_curve_jet(sample["conditions"], view[1])
        separations.append(float(np.linalg.norm(first[0] - second[0])))
        singular.append(float(np.linalg.norm(first[1] - second[1])))
        hessian.append(float(np.linalg.norm(first[2] - second[2])))
    separations = np.asarray(separations)
    singular = np.asarray(singular)
    hessian = np.asarray(hessian)
    low, high = _bootstrap_interval(
        singular,
        seed=seed,
        repetitions=spec.bootstrap_repetitions,
    )
    separation = float(np.mean(separations))
    rank_score = float(np.mean(singular))
    hessian_score = float(np.mean(hessian))
    if separation > spec.intersection_tolerance:
        relation = "NO_INTERSECTION"
        status = "ESTIMATE_READY"
        dimension = np.nan
    elif (
        low <= spec.rank_threshold + spec.rank_margin
        and high >= spec.rank_threshold - spec.rank_margin
    ):
        relation = "BOUNDARY"
        status = "REFUSE_GEOMETRY_BOUNDARY"
        dimension = np.nan
    elif rank_score > spec.rank_threshold:
        relation = "TRANSVERSE"
        status = "ESTIMATE_READY"
        dimension = 0.0
    elif hessian_score > spec.hessian_threshold:
        relation = "TANGENT"
        status = "ESTIMATE_READY"
        dimension = np.nan
    else:
        relation = "COINCIDENT"
        status = "ESTIMATE_READY"
        dimension = 1.0
    return {
        "status": status,
        "relation": relation,
        "separation": separation,
        "rank_score": rank_score,
        "rank_interval_low": low,
        "rank_interval_high": high,
        "hessian_score": hessian_score,
        "intersection_dimension": dimension,
    }


def _surface_design(coordinates: np.ndarray) -> np.ndarray:
    s = coordinates[:, 0]
    t = coordinates[:, 1]
    return np.column_stack([
        np.ones(len(s)),
        s,
        t,
        0.5 * s**2,
        s * t,
        0.5 * t**2,
    ])


def _surface_jet(
    coordinates: np.ndarray,
    response: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    local = np.max(np.abs(coordinates), axis=1) <= 0.31
    coefficient, *_ = np.linalg.lstsq(
        _surface_design(coordinates[local]),
        response[local],
        rcond=None,
    )
    jacobian = coefficient[[1, 2]].T
    hessian = np.stack([
        coefficient[3],
        coefficient[4],
        coefficient[5],
    ])
    return coefficient[0], jacobian, hessian


def simulate_surface_relation(
    *,
    seed: int,
    world: str,
    spec: GeometryCompletionSpec,
) -> dict[str, Any]:
    """Simulate two nonlinear two-condition response sheets."""
    axis = np.linspace(-0.60, 0.60, spec.surface_grid)
    s, t = np.meshgrid(axis, axis, indexing="ij")
    coordinates = np.column_stack([s.ravel(), t.ravel()])
    if world.startswith("reparameterized_"):
        coordinates_observed = np.column_stack([
            coordinates[:, 0] + 0.2 * coordinates[:, 0] ** 3,
            coordinates[:, 1] - 0.15 * coordinates[:, 1] ** 3,
        ])
        source_world = world.removeprefix("reparameterized_")
    else:
        coordinates_observed = coordinates
        source_world = world
    s0 = coordinates[:, 0]
    t0 = coordinates[:, 1]
    if source_world in {"sinusoidal_transverse", "rbf_transverse"}:
        base_z = 0.25 * np.sin(np.pi * s0) * np.sin(np.pi * t0)
    else:
        base_z = 0.25 * (s0**2 + t0**2)
    first = np.column_stack([s0, t0, base_z])
    if source_world == "transverse":
        delta = 1.20 * s0
    elif source_world == "tangent":
        delta = 1.20 * s0**2
    elif source_world == "coincident":
        delta = np.zeros_like(s0)
    elif source_world == "near_miss":
        delta = np.full_like(s0, 0.15)
    elif source_world == "boundary":
        delta = 0.45 * s0
    elif source_world == "sinusoidal_transverse":
        delta = 0.45 * np.sin(np.pi * s0)
    elif source_world == "rbf_transverse":
        delta = 1.20 * s0 * np.exp(-t0**2 / 0.12)
    else:
        raise ValueError(f"unsupported surface world: {world}")
    second = first.copy()
    second[:, 2] += delta
    covariance = spec.jet_noise_sd**2 * np.asarray([
        [1.0, 0.35, 0.20],
        [0.35, 1.0, 0.25],
        [0.20, 0.25, 1.0],
    ])
    observations = []
    rng = np.random.default_rng(seed)
    scale = 1.0 + 0.7 * np.linalg.norm(coordinates, axis=1)
    for _ in range(spec.views):
        first_noise = rng.multivariate_normal(
            np.zeros(3),
            covariance,
            size=len(coordinates),
        ) * scale[:, None]
        second_noise = rng.multivariate_normal(
            np.zeros(3),
            covariance,
            size=len(coordinates),
        ) * scale[:, None]
        observations.append(np.stack([
            first + first_noise,
            second + second_noise,
        ]))
    return {
        "world": world,
        "coordinates": coordinates_observed,
        "observations": np.asarray(observations),
    }


def classify_surface_relation(
    sample: dict[str, Any],
    *,
    seed: int,
    spec: GeometryCompletionSpec,
) -> dict[str, Any]:
    """Classify local sheet contact from cross-view quadratic jets."""
    separations = []
    singular_values = []
    hessian = []
    for view in sample["observations"]:
        first = _surface_jet(sample["coordinates"], view[0])
        second = _surface_jet(sample["coordinates"], view[1])
        separations.append(float(np.linalg.norm(first[0] - second[0])))
        singular_values.append(
            np.linalg.svd(first[1] - second[1], compute_uv=False)
        )
        hessian.append(float(np.linalg.norm(first[2] - second[2])))
    separations = np.asarray(separations)
    leading = np.asarray([
        values[0] if len(values) else 0.0
        for values in singular_values
    ])
    low, high = _bootstrap_interval(
        leading,
        seed=seed,
        repetitions=spec.bootstrap_repetitions,
    )
    separation = float(np.mean(separations))
    rank_score = float(np.mean(leading))
    hessian_score = float(np.mean(hessian))
    if separation > spec.intersection_tolerance:
        relation = "NO_INTERSECTION"
        status = "ESTIMATE_READY"
        dimension = np.nan
    elif (
        low <= spec.rank_threshold + spec.rank_margin
        and high >= spec.rank_threshold - spec.rank_margin
    ):
        relation = "BOUNDARY"
        status = "REFUSE_GEOMETRY_BOUNDARY"
        dimension = np.nan
    elif rank_score > spec.rank_threshold:
        relation = "TRANSVERSE"
        status = "ESTIMATE_READY"
        dimension = 1.0
    elif hessian_score > spec.hessian_threshold:
        relation = "TANGENT"
        status = "ESTIMATE_READY"
        dimension = np.nan
    else:
        relation = "COINCIDENT"
        status = "ESTIMATE_READY"
        dimension = 2.0
    return {
        "status": status,
        "relation": relation,
        "separation": separation,
        "rank_score": rank_score,
        "rank_interval_low": low,
        "rank_interval_high": high,
        "hessian_score": hessian_score,
        "intersection_dimension": dimension,
    }
