"""Common-ball information beyond thresholded pair adjacency."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.metrics import adjusted_rand_score, f1_score

from suica_core.v8_incidence_graph_fairness import (
    aggregate_component_concurrency_gate,
    complete_link_grid,
    maximal_clique_grid,
    persistent_grid_estimator,
)
from suica_core.v8_incidence_incremental import (
    IncrementalSpec,
    _balanced_labels,
    _bron_kerbosch_maximal_cliques,
    _cores_overlap,
    _inclusion_maximal_cores,
    _predicted_labels,
    exact_maximal_hyperedges,
)
from suica_core.v8_incidence_incremental_v31 import (
    condition_aligned_core_scores,
)
from suica_core.v8_incidence_multiplicity import minimum_enclosing_ball


@dataclass(frozen=True)
class CommonBallSpec:
    """Frozen V3.4 geometry and estimator settings."""

    authors: int = 24
    groups: int = 4
    conditions: int = 65
    views: int = 4
    ambient: int = 2
    active_conditions: int = 4
    fixed_radius: float = 1.0
    epsilon_grid: tuple[float, ...] = (1.0, 1.03, 1.06)
    noise_sd: float = 0.002
    core_persistence_threshold: float = 0.04
    minimum_group_coverage: float = 0.75
    margin_refusal: float = 0.02
    enumeration_node_cap: int = 25_000
    candidate_cap: int = 5_000


def _pair_spec(spec: CommonBallSpec) -> IncrementalSpec:
    return IncrementalSpec(
        authors=spec.authors,
        groups=spec.groups,
        conditions=spec.conditions,
        halves=2,
        observers=2,
        ambient=spec.ambient,
        event_width=spec.active_conditions,
        noise_sd=spec.noise_sd,
        epsilon_grid=spec.epsilon_grid,
        core_persistence_threshold=spec.core_persistence_threshold,
        minimum_group_coverage=spec.minimum_group_coverage,
        enumeration_node_cap=spec.enumeration_node_cap,
    )


def _anchors() -> np.ndarray:
    return np.asarray([
        [-8.0, -8.0],
        [-8.0, 8.0],
        [8.0, -8.0],
        [8.0, 8.0],
    ])


def _base_positions(spec: CommonBallSpec) -> np.ndarray:
    angles = 2.0 * np.pi * np.arange(spec.authors) / spec.authors
    points = np.column_stack([
        20.0 * np.cos(angles),
        20.0 * np.sin(angles),
    ])
    return np.repeat(points[:, None, :], spec.conditions, axis=1)


def common_ball_truth_paths(
    *,
    labels: np.ndarray,
    spec: CommonBallSpec,
    geometry: str,
    shape_radius: float,
    seed: int,
) -> np.ndarray:
    """Construct group response sets with a registered geometry and radius."""
    if geometry not in {"hexagon", "triangle"}:
        raise ValueError(f"unsupported common-ball geometry: {geometry}")
    paths = _base_positions(spec)
    anchors = _anchors()
    rng = np.random.default_rng(seed)
    for condition in range(spec.active_conditions):
        for group in range(spec.groups):
            members = np.sort(np.flatnonzero(labels == group))
            offset = rng.uniform(0.0, 2.0 * np.pi)
            if geometry == "hexagon":
                angles = (
                    2.0 * np.pi * np.arange(6) / 6.0
                    + offset
                )
            else:
                triangle = (
                    2.0 * np.pi * np.arange(3) / 3.0
                    + offset
                )
                angles = np.repeat(triangle, 2)
            points = np.repeat(
                anchors[group][None, :],
                6,
                axis=0,
            )
            points[:, 0] += shape_radius * np.cos(angles)
            points[:, 1] += shape_radius * np.sin(angles)
            paths[members, condition] = points
    return paths


def simulate_common_ball_pair(
    *,
    seed: int,
    spec: CommonBallSpec,
    positive_geometry: str = "hexagon",
    negative_geometry: str = "triangle",
    positive_shape_radius: float,
    negative_shape_radius: float,
) -> dict[str, Any]:
    """Generate paired worlds and paired observer perturbations."""
    labels = _balanced_labels(
        _pair_spec(spec),
        np.random.default_rng(seed),
    )
    positive_truth = common_ball_truth_paths(
        labels=labels,
        spec=spec,
        geometry=positive_geometry,
        shape_radius=positive_shape_radius,
        seed=seed + 10_003,
    )
    negative_truth = common_ball_truth_paths(
        labels=labels,
        spec=spec,
        geometry=negative_geometry,
        shape_radius=negative_shape_radius,
        seed=seed + 10_003,
    )
    positive_views = []
    negative_views = []
    for view in range(spec.views):
        noise = np.random.default_rng(
            seed + 20_011 + 101 * view
        ).normal(
            scale=spec.noise_sd,
            size=positive_truth.shape,
        )
        positive_views.append(positive_truth + noise)
        negative_views.append(negative_truth + noise)
    return {
        "labels": labels,
        "positive_truth": positive_truth,
        "negative_truth": negative_truth,
        "positive_views": np.asarray(positive_views),
        "negative_views": np.asarray(negative_views),
        "positive_shape_radius": positive_shape_radius,
        "negative_shape_radius": negative_shape_radius,
        "positive_geometry": positive_geometry,
        "negative_geometry": negative_geometry,
    }


def fixed_pair_adjacency_view_tensor(
    views: np.ndarray,
    *,
    spec: CommonBallSpec,
) -> np.ndarray:
    """Return per-view pair adjacency at the registered fixed radii."""
    tensor = np.zeros(
        (
            spec.views,
            spec.conditions,
            len(spec.epsilon_grid),
            spec.authors,
            spec.authors,
        ),
        dtype=bool,
    )
    for view in range(spec.views):
        for condition in range(spec.conditions):
            points = views[view, :, condition, :]
            distances = np.linalg.norm(
                points[:, None, :] - points[None, :, :],
                axis=-1,
            )
            for radius_index, epsilon in enumerate(spec.epsilon_grid):
                tensor[view, condition, radius_index] = (
                    distances
                    <= 2.0 * epsilon * spec.fixed_radius
                )
                np.fill_diagonal(
                    tensor[view, condition, radius_index],
                    False,
                )
    return tensor


def fixed_pair_adjacency_tensor(
    views: np.ndarray,
    *,
    spec: CommonBallSpec,
) -> np.ndarray:
    """Return pair adjacency intersected across registered observer views."""
    return np.all(
        fixed_pair_adjacency_view_tensor(views, spec=spec),
        axis=0,
    )


def _margin_violation(
    points: np.ndarray,
    *,
    radius: float,
    margin: float,
    node_cap: int,
) -> bool:
    distances = np.linalg.norm(
        points[:, None, :] - points[None, :, :],
        axis=-1,
    )
    masks = []
    for left in range(len(points)):
        mask = 0
        for right in range(len(points)):
            if (
                left != right
                and distances[left, right] <= 2.0 * radius
            ):
                mask |= 1 << right
        masks.append(mask)
    cliques, _ = _bron_kerbosch_maximal_cliques(
        masks,
        node_cap=node_cap,
    )
    for clique in cliques:
        if len(clique) < 3:
            continue
        _, enclosing_radius = minimum_enclosing_ball(
            points[list(clique)]
        )
        if abs(enclosing_radius - radius) <= margin:
            return True
    return False


def _partition_result(
    selected: list[frozenset[int]],
    passing: list[frozenset[int]],
    labels: np.ndarray,
    *,
    status: str,
    minimum_group_coverage: float,
) -> dict[str, Any]:
    predicted = _predicted_labels(len(labels), selected)
    upper = np.triu_indices(len(labels), 1)
    truth_pairs = (
        labels[upper[0]] == labels[upper[1]]
    ).astype(int)
    predicted_pairs = (
        predicted[upper[0]] == predicted[upper[1]]
    ).astype(int)
    coverage = (
        len(set().union(*selected)) / len(labels)
        if selected else 0.0
    )
    return {
        "status": status,
        "refused": status.startswith("REFUSE"),
        "group_claim": bool(
            status == "ESTIMATE_READY"
            and len(selected) >= 2
            and coverage >= minimum_group_coverage
        ),
        "coverage": coverage,
        "selected_groups": [
            sorted(int(item) for item in group)
            for group in selected
        ],
        "passing_groups": [
            sorted(int(item) for item in group)
            for group in passing
        ],
        "maximum_passing_size": max(
            (len(group) for group in passing),
            default=0,
        ),
        "group_f1": float(f1_score(
            truth_pairs,
            predicted_pairs,
            zero_division=0,
        )),
        "group_ari": float(adjusted_rand_score(labels, predicted)),
    }


def fixed_radius_meb_estimator(
    views: np.ndarray,
    labels: np.ndarray,
    *,
    spec: CommonBallSpec,
) -> dict[str, Any]:
    """Estimate persistent common-ball groups at fixed registered radii."""
    grids: list[list[list[list[tuple[int, ...]]]]] = []
    boundary = False
    try:
        for view in views:
            view_grid = []
            for condition in range(spec.conditions):
                condition_grid = []
                for epsilon in spec.epsilon_grid:
                    radius = epsilon * spec.fixed_radius
                    boundary = boundary or _margin_violation(
                        view[:, condition],
                        radius=radius,
                        margin=spec.margin_refusal * spec.fixed_radius,
                        node_cap=spec.enumeration_node_cap,
                    )
                    edges, _ = exact_maximal_hyperedges(
                        view[:, condition],
                        radius=radius,
                        node_cap=spec.enumeration_node_cap,
                    )
                    condition_grid.append(edges)
                view_grid.append(condition_grid)
            grids.append(view_grid)
        scores, _ = condition_aligned_core_scores(
            grids,
            authors=spec.authors,
            closure_cap=spec.candidate_cap,
            threshold=spec.core_persistence_threshold,
        )
    except RuntimeError as error:
        return {
            "status": "REFUSE_CAP",
            "refusal_reason": str(error),
            "refused": True,
            "group_claim": False,
        }
    passing = _inclusion_maximal_cores(
        scores,
        threshold=spec.core_persistence_threshold,
    )
    ambiguity = _cores_overlap(passing)
    if boundary:
        status = "REFUSE_MARGIN"
        selected: list[frozenset[int]] = []
    elif ambiguity:
        status = "REFUSE_OVERLAP_AMBIGUITY"
        selected = []
    else:
        status = "ESTIMATE_READY"
        selected = passing
    return _partition_result(
        selected,
        passing,
        labels,
        status=status,
        minimum_group_coverage=spec.minimum_group_coverage,
    )


def pair_tensor_baselines(
    tensor: np.ndarray,
    labels: np.ndarray,
    *,
    spec: CommonBallSpec,
) -> dict[str, dict[str, Any]]:
    """Run all V3.3 comparators directly on a fixed-radius tensor."""
    pair_spec = _pair_spec(spec)
    return {
        "persistent_maximal_clique": persistent_grid_estimator(
            maximal_clique_grid(
                tensor,
                node_cap=spec.enumeration_node_cap,
            ),
            labels,
            spec=pair_spec,
            candidate_cap=spec.candidate_cap,
        ),
        "condition_complete_link": persistent_grid_estimator(
            complete_link_grid(tensor),
            labels,
            spec=pair_spec,
            candidate_cap=spec.candidate_cap,
        ),
        "aggregate_component_concurrency_gate": (
            aggregate_component_concurrency_gate(
                tensor,
                labels,
                spec=pair_spec,
            )
        ),
    }


def analyze_common_ball_pair(
    pair: dict[str, Any],
    *,
    spec: CommonBallSpec,
) -> dict[str, Any]:
    """Compare MEB decisions after exact adjacency-tensor matching."""
    positive_view_tensor = fixed_pair_adjacency_view_tensor(
        pair["positive_views"],
        spec=spec,
    )
    negative_view_tensor = fixed_pair_adjacency_view_tensor(
        pair["negative_views"],
        spec=spec,
    )
    view_mismatch = int(np.count_nonzero(
        positive_view_tensor != negative_view_tensor
    ))
    positive_tensor = np.all(positive_view_tensor, axis=0)
    negative_tensor = np.all(negative_view_tensor, axis=0)
    collapsed_mismatch = int(np.count_nonzero(
        positive_tensor != negative_tensor
    ))
    if view_mismatch or collapsed_mismatch:
        return {
            "status": "STOP_ADJACENCY_MISMATCH",
            "view_tensor_mismatch_count": view_mismatch,
            "tensor_mismatch_count": collapsed_mismatch,
        }
    positive_pair = pair_tensor_baselines(
        positive_tensor,
        pair["labels"],
        spec=spec,
    )
    negative_pair = pair_tensor_baselines(
        negative_tensor,
        pair["labels"],
        spec=spec,
    )
    pairwise_output_match = all(
        positive_pair[method]["status"]
        == negative_pair[method]["status"]
        and positive_pair[method]["group_claim"]
        == negative_pair[method]["group_claim"]
        and positive_pair[method]["selected_groups"]
        == negative_pair[method]["selected_groups"]
        for method in positive_pair
    )
    positive_meb = fixed_radius_meb_estimator(
        pair["positive_views"],
        pair["labels"],
        spec=spec,
    )
    negative_meb = fixed_radius_meb_estimator(
        pair["negative_views"],
        pair["labels"],
        spec=spec,
    )
    return {
        "status": "ESTIMATE_READY",
        "view_tensor_mismatch_count": 0,
        "tensor_mismatch_count": 0,
        "pairwise_output_match": pairwise_output_match,
        "positive_pairwise": positive_pair,
        "negative_pairwise": negative_pair,
        "positive_meb": positive_meb,
        "negative_meb": negative_meb,
        "decision_delta": (
            int(positive_meb["group_claim"])
            - int(negative_meb["group_claim"])
        ),
    }
