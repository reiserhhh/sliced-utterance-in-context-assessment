"""Condition-aware pairwise comparators for the V3.2 strong-chain world."""
from __future__ import annotations

from itertools import combinations
from typing import Any

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.metrics import adjusted_rand_score, f1_score

from suica_core.v8_incidence_incremental import (
    IncrementalSpec,
    _bron_kerbosch_maximal_cliques,
    _cores_overlap,
    _inclusion_maximal_cores,
    _predicted_labels,
    _specificity,
    _uncertainty_radius,
)
from suica_core.v8_incidence_incremental_v31 import (
    condition_aligned_core_scores,
)


def condition_pair_adjacency_tensor(
    views: np.ndarray,
    *,
    spec: IncrementalSpec,
) -> np.ndarray:
    """Return condition-radius pair adjacency intersected across views."""
    radius = _uncertainty_radius(views)
    tensor = np.zeros(
        (
            spec.conditions,
            len(spec.epsilon_grid),
            spec.authors,
            spec.authors,
        ),
        dtype=bool,
    )
    for condition in range(spec.conditions):
        points = views[:, :, condition, :]
        distances = np.linalg.norm(
            points[:, :, None, :] - points[:, None, :, :],
            axis=-1,
        )
        for radius_index, epsilon in enumerate(spec.epsilon_grid):
            tensor[condition, radius_index] = np.all(
                distances <= 2.0 * epsilon * radius[condition],
                axis=0,
            )
            np.fill_diagonal(
                tensor[condition, radius_index],
                False,
            )
    return tensor


def _maximal_cliques(
    adjacency: np.ndarray,
    *,
    node_cap: int,
) -> list[tuple[int, ...]]:
    masks = []
    for left in range(len(adjacency)):
        mask = 0
        for right in np.flatnonzero(adjacency[left]):
            mask |= 1 << int(right)
        masks.append(mask)
    cliques, _ = _bron_kerbosch_maximal_cliques(
        masks,
        node_cap=node_cap,
    )
    return [
        clique for clique in cliques
        if len(clique) >= 3
    ]


def maximal_clique_grid(
    tensor: np.ndarray,
    *,
    node_cap: int,
) -> list[list[list[tuple[int, ...]]]]:
    """Enumerate maximal pairwise cliques at every condition-radius cell."""
    return [
        [
            _maximal_cliques(
                tensor[condition, radius_index],
                node_cap=node_cap,
            )
            for radius_index in range(tensor.shape[1])
        ]
        for condition in range(tensor.shape[0])
    ]


def complete_link_grid(
    tensor: np.ndarray,
) -> list[list[list[tuple[int, ...]]]]:
    """Partition every cell into complete-link binary-distance clusters."""
    output = []
    for condition in range(tensor.shape[0]):
        condition_output = []
        for radius_index in range(tensor.shape[1]):
            distance = 1.0 - tensor[
                condition,
                radius_index,
            ].astype(float)
            np.fill_diagonal(distance, 0.0)
            hierarchy = linkage(
                squareform(distance, checks=True),
                method="complete",
            )
            labels = fcluster(
                hierarchy,
                t=0.5,
                criterion="distance",
            )
            groups = [
                tuple(int(item) for item in np.flatnonzero(
                    labels == label
                ))
                for label in np.unique(labels)
            ]
            condition_output.append([
                group for group in groups if len(group) >= 3
            ])
        output.append(condition_output)
    return output


def _partition_result(
    selected: list[frozenset[int]],
    truth: np.ndarray,
    *,
    ambiguity: bool,
    passing: list[frozenset[int]],
) -> dict[str, Any]:
    predicted = _predicted_labels(len(truth), selected)
    upper = np.triu_indices(len(truth), 1)
    true_pairs = (truth[upper[0]] == truth[upper[1]]).astype(int)
    predicted_pairs = (
        predicted[upper[0]] == predicted[upper[1]]
    ).astype(int)
    coverage = (
        len(set().union(*selected)) / len(truth)
        if selected else 0.0
    )
    return {
        "status": (
            "REFUSE_OVERLAP_AMBIGUITY"
            if ambiguity
            else "ESTIMATE_READY"
        ),
        "refused": ambiguity,
        "group_claim": bool(
            not ambiguity
            and len(selected) >= 2
            and coverage >= 0.75
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
            true_pairs,
            predicted_pairs,
            zero_division=0,
        )),
        "group_ari": float(adjusted_rand_score(truth, predicted)),
    }


def persistent_grid_estimator(
    grid: list[list[list[tuple[int, ...]]]],
    truth: np.ndarray,
    *,
    spec: IncrementalSpec,
    candidate_cap: int,
) -> dict[str, Any]:
    """Estimate persistent groups from one condition-aware pairwise grid."""
    scores, _ = condition_aligned_core_scores(
        [grid],
        authors=spec.authors,
        closure_cap=candidate_cap,
        threshold=spec.core_persistence_threshold,
    )
    passing = _inclusion_maximal_cores(
        scores,
        threshold=spec.core_persistence_threshold,
    )
    ambiguity = _cores_overlap(passing)
    selected = [] if ambiguity else passing
    return _partition_result(
        selected,
        truth,
        ambiguity=ambiguity,
        passing=passing,
    )


def aggregate_component_concurrency_gate(
    tensor: np.ndarray,
    truth: np.ndarray,
    *,
    spec: IncrementalSpec,
) -> dict[str, Any]:
    """Gate aggregate connected components by same-cell full concurrency."""
    aggregate = tensor.mean(axis=(0, 1))
    adjacency = aggregate >= spec.core_persistence_threshold
    np.fill_diagonal(adjacency, False)
    visited = np.zeros(spec.authors, dtype=bool)
    candidates: list[frozenset[int]] = []
    for start in range(spec.authors):
        if visited[start]:
            continue
        stack = [start]
        visited[start] = True
        members = []
        while stack:
            node = stack.pop()
            members.append(node)
            for neighbor in np.flatnonzero(adjacency[node]):
                if not visited[neighbor]:
                    visited[neighbor] = True
                    stack.append(int(neighbor))
        if len(members) >= 3:
            candidates.append(frozenset(members))

    passing = []
    denominator = tensor.shape[0] * tensor.shape[1]
    for candidate in candidates:
        pairs = list(combinations(sorted(candidate), 2))
        cells = 0
        for condition in range(tensor.shape[0]):
            for radius_index in range(tensor.shape[1]):
                if all(
                    tensor[condition, radius_index, left, right]
                    for left, right in pairs
                ):
                    cells += 1
        score = (
            cells
            / denominator
            * _specificity(spec.authors, len(candidate))
        )
        if score >= spec.core_persistence_threshold:
            passing.append(candidate)
    return _partition_result(
        passing,
        truth,
        ambiguity=False,
        passing=passing,
    )


def analyze_condition_pair_baselines(
    views: np.ndarray,
    truth: np.ndarray,
    *,
    spec: IncrementalSpec,
    node_cap: int,
    candidate_cap: int,
) -> dict[str, dict[str, Any]]:
    """Run all registered condition-aware pairwise comparators."""
    tensor = condition_pair_adjacency_tensor(views, spec=spec)
    return {
        "persistent_maximal_clique": persistent_grid_estimator(
            maximal_clique_grid(tensor, node_cap=node_cap),
            truth,
            spec=spec,
            candidate_cap=candidate_cap,
        ),
        "condition_complete_link": persistent_grid_estimator(
            complete_link_grid(tensor),
            truth,
            spec=spec,
            candidate_cap=candidate_cap,
        ),
        "aggregate_component_concurrency_gate": (
            aggregate_component_concurrency_gate(
                tensor,
                truth,
                spec=spec,
            )
        ),
    }
