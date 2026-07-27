"""Counterfactual incidence geometry for SUICA V8.

The module constructs paired response-path populations with identical
whole-map distance geometry but different same-condition incidence topology.
It also provides an exact small-dimensional maximal common-ball enumerator
and a no-chaining persistent-core estimator.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any

import numpy as np
from scipy.linalg import orthogonal_procrustes
from sklearn.metrics import adjusted_rand_score, f1_score, roc_auc_score

from suica_core.v8_incidence_multiplicity import (
    minimum_enclosing_ball,
    verified_hyperedges,
)


@dataclass(frozen=True)
class IncrementalSpec:
    """Frozen observation and estimator settings for V3."""

    authors: int = 24
    groups: int = 4
    conditions: int = 65
    halves: int = 2
    observers: int = 2
    ambient: int = 2
    event_width: int = 6
    noise_sd: float = 0.01
    epsilon_grid: tuple[float, ...] = (2.0, 3.0, 4.0)
    core_persistence_threshold: float = 0.04
    minimum_group_coverage: float = 0.75
    enumeration_node_cap: int = 25_000

    @property
    def views(self) -> int:
        """Return the number of independent half-observer views."""
        return self.halves * self.observers


PAIR_WORLDS: dict[str, tuple[str, str]] = {
    "CF1": ("sync6", "async6"),
    "CF2": ("core6", "chain3"),
    "CF3": ("persist6", "rotating6"),
}


class EnumerationCapError(RuntimeError):
    """Raised when exact hyperedge enumeration exceeds its frozen cap."""


def _balanced_labels(
    spec: IncrementalSpec,
    rng: np.random.Generator,
) -> np.ndarray:
    labels = np.arange(spec.authors, dtype=int) % spec.groups
    return labels[rng.permutation(spec.authors)]


def _event_blocks(spec: IncrementalSpec) -> list[np.ndarray]:
    starts = np.linspace(
        4,
        spec.conditions - spec.event_width - 4,
        spec.groups,
    ).round().astype(int)
    return [
        np.arange(start, start + spec.event_width, dtype=int)
        for start in starts
    ]


def _baseline_positions(
    spec: IncrementalSpec,
) -> np.ndarray:
    """Return separated author positions at every condition."""
    authors = np.arange(spec.authors, dtype=float)[:, None]
    conditions = np.arange(spec.conditions, dtype=float)[None, :]
    angle = (
        2.0 * np.pi * authors / spec.authors
        + 0.07 * np.sin(conditions / 4.0)
    )
    result = np.zeros(
        (spec.authors, spec.conditions, spec.ambient),
        dtype=float,
    )
    result[:, :, 0] = 3.0 * np.cos(angle)
    result[:, :, 1] = 3.0 * np.sin(angle)
    if spec.ambient >= 3:
        result[:, :, 2] = (
            (authors % 4) / 2.0
            + 0.15 * np.cos(conditions / 5.0)
        )
    return result


def _rotating_partition(
    spec: IncrementalSpec,
    rng: np.random.Generator,
    forbidden: set[frozenset[int]],
    seen: set[frozenset[int]],
) -> list[np.ndarray]:
    for _ in range(1_000):
        permutation = rng.permutation(spec.authors)
        groups = [
            np.sort(chunk)
            for chunk in np.array_split(permutation, spec.groups)
        ]
        sets = [frozenset(int(item) for item in group) for group in groups]
        if any(item in forbidden or item in seen for item in sets):
            continue
        seen.update(sets)
        return groups
    raise RuntimeError("failed to construct rotating memberships")


def local_event_geometry(
    *,
    world: str,
    labels: np.ndarray,
    spec: IncrementalSpec,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Build local event coordinates before Gram reservoir compensation."""
    valid_worlds = {
        "sync6",
        "async6",
        "core6",
        "chain3",
        "persist6",
        "rotating6",
    }
    if world not in valid_worlds:
        raise ValueError(f"unsupported incremental world: {world}")
    baseline = _baseline_positions(spec)
    local = np.zeros_like(baseline)
    event_mask = np.zeros(spec.conditions, dtype=bool)
    blocks = _event_blocks(spec)
    for block in blocks:
        event_mask[block] = True
        local[:, block] = baseline[:, block]

    if world in {"sync6", "core6", "persist6"}:
        for group, block in enumerate(blocks):
            members = np.flatnonzero(labels == group)
            local[np.ix_(members, block)] = 0.0
        return local, event_mask

    if world == "async6":
        for group, block in enumerate(blocks):
            members = np.sort(np.flatnonzero(labels == group))
            for condition, member in zip(block, members, strict=True):
                local[member, condition] = 0.0
        return local, event_mask

    if world == "chain3":
        for group, block in enumerate(blocks):
            members = np.sort(np.flatnonzero(labels == group))
            triplets = [
                members[[0, 1, 2]],
                members[[2, 3, 4]],
                members[[4, 5, 0]],
            ]
            for index, condition in enumerate(block):
                current = triplets[index // 2]
                local[current, condition] = 0.0
        return local, event_mask

    anchors = np.asarray([
        [-1.25, -1.25],
        [-1.25, 1.25],
        [1.25, -1.25],
        [1.25, 1.25],
    ])
    if spec.ambient > 2:
        anchors = np.pad(
            anchors,
            ((0, 0), (0, spec.ambient - 2)),
        )
    forbidden = {
        frozenset(int(item) for item in np.flatnonzero(labels == group))
        for group in range(spec.groups)
    }
    seen: set[frozenset[int]] = set()
    for condition in np.flatnonzero(event_mask):
        partition = _rotating_partition(
            spec,
            rng,
            forbidden,
            seen,
        )
        for group, members in enumerate(partition):
            local[members, condition] = anchors[group]
    return local, event_mask


def _center_rows(values: np.ndarray) -> np.ndarray:
    return values - values.mean(axis=0, keepdims=True)


def _residual_factor(
    residual_gram: np.ndarray,
    *,
    tolerance: float = 1e-9,
) -> np.ndarray:
    values, vectors = np.linalg.eigh(
        (residual_gram + residual_gram.T) / 2.0
    )
    if float(values.min()) < -tolerance:
        raise ValueError(
            f"reservoir Gram is not PSD: {values.min():.6g}"
        )
    keep = values > tolerance
    return vectors[:, keep] * np.sqrt(values[keep])[None, :]


def _embed_reservoir(
    local: np.ndarray,
    *,
    event_mask: np.ndarray,
    gamma: float,
    rng: np.random.Generator,
) -> np.ndarray:
    authors, conditions, ambient = local.shape
    flat = _center_rows(local.reshape(authors, -1))
    gram = flat @ flat.T
    centering = np.eye(authors) - np.ones((authors, authors)) / authors
    residual = gamma * centering - gram
    factor = _residual_factor(residual)
    coordinate_mask = np.repeat(~event_mask, ambient)
    reservoir_indices = np.flatnonzero(coordinate_mask)
    if len(reservoir_indices) < factor.shape[1]:
        raise ValueError("insufficient reservoir coordinates")
    random_basis = rng.normal(
        size=(len(reservoir_indices), factor.shape[1])
    )
    orthonormal, _ = np.linalg.qr(random_basis, mode="reduced")
    reservoir = factor @ orthonormal.T
    flat[:, reservoir_indices] += reservoir
    return flat.reshape(authors, conditions, ambient)


def _maximum_centered_eigenvalue(local: np.ndarray) -> float:
    flat = _center_rows(local.reshape(local.shape[0], -1))
    return float(np.linalg.eigvalsh(flat @ flat.T).max())


def pairwise_whole_map_distances(paths: np.ndarray) -> np.ndarray:
    """Return upper-triangle mean squared whole-path distances."""
    flat = paths.reshape(paths.shape[0], -1)
    left, right = np.triu_indices(paths.shape[0], 1)
    return np.mean((flat[left] - flat[right]) ** 2, axis=1)


def _distance_matrix(paths: np.ndarray) -> np.ndarray:
    vector = pairwise_whole_map_distances(paths)
    result = np.zeros((paths.shape[0], paths.shape[0]), dtype=float)
    upper = np.triu_indices(paths.shape[0], 1)
    result[upper] = vector
    result[(upper[1], upper[0])] = vector
    return result


def simulate_counterfactual_pair(
    *,
    seed: int,
    pair_id: str,
    spec: IncrementalSpec,
) -> dict[str, Any]:
    """Generate distance-matched positive and counterfactual path views."""
    if pair_id not in PAIR_WORLDS:
        raise ValueError(f"unsupported pair: {pair_id}")
    rng = np.random.default_rng(seed)
    labels = _balanced_labels(spec, rng)
    positive_world, negative_world = PAIR_WORLDS[pair_id]
    positive_local, positive_mask = local_event_geometry(
        world=positive_world,
        labels=labels,
        spec=spec,
        rng=np.random.default_rng(seed + 10_001),
    )
    negative_local, negative_mask = local_event_geometry(
        world=negative_world,
        labels=labels,
        spec=spec,
        rng=np.random.default_rng(seed + 20_003),
    )
    gamma = (
        max(
            _maximum_centered_eigenvalue(positive_local),
            _maximum_centered_eigenvalue(negative_local),
        )
        + 1.0
    )
    positive = _embed_reservoir(
        positive_local,
        event_mask=positive_mask,
        gamma=gamma,
        rng=np.random.default_rng(seed + 30_007),
    )
    negative = _embed_reservoir(
        negative_local,
        event_mask=negative_mask,
        gamma=gamma,
        rng=np.random.default_rng(seed + 40_009),
    )
    positive_flat = positive.reshape(spec.authors, -1)
    negative_flat = negative.reshape(spec.authors, -1)
    transform, _ = orthogonal_procrustes(
        positive_flat,
        negative_flat,
    )
    mapping_error = float(
        np.linalg.norm(positive_flat @ transform - negative_flat)
        / max(np.linalg.norm(negative_flat), 1e-12)
    )
    if mapping_error > 1e-8:
        raise RuntimeError(
            f"orthogonal pair mapping failed: {mapping_error:.6g}"
        )

    positive_views = []
    negative_views = []
    for view in range(spec.views):
        noise_rng = np.random.default_rng(seed + 50_021 + 101 * view)
        noise = noise_rng.normal(
            scale=spec.noise_sd,
            size=positive_flat.shape,
        )
        positive_views.append(
            (positive_flat + noise).reshape(positive.shape)
        )
        negative_views.append(
            (negative_flat + noise @ transform).reshape(negative.shape)
        )
    positive_views_array = np.asarray(positive_views)
    negative_views_array = np.asarray(negative_views)
    oracle_positive = _distance_matrix(positive)
    oracle_negative = _distance_matrix(negative)
    fitted_positive = _distance_matrix(positive_views_array.mean(axis=0))
    fitted_negative = _distance_matrix(negative_views_array.mean(axis=0))
    return {
        "pair_id": pair_id,
        "positive_world": positive_world,
        "negative_world": negative_world,
        "labels": labels,
        "positive_truth": positive,
        "negative_truth": negative,
        "positive_views": positive_views_array,
        "negative_views": negative_views_array,
        "oracle_distance_relative_error": float(
            np.linalg.norm(oracle_positive - oracle_negative)
            / max(np.linalg.norm(oracle_positive), 1e-12)
        ),
        "fitted_distance_relative_error": float(
            np.linalg.norm(fitted_positive - fitted_negative)
            / max(np.linalg.norm(fitted_positive), 1e-12)
        ),
        "orthogonal_mapping_error": mapping_error,
        "gamma": gamma,
    }


def simulate_null_population(
    *,
    seed: int,
    world: str,
    spec: IncrementalSpec,
) -> dict[str, Any]:
    """Generate a reservoir-only or population-anchor null population."""
    if world not in {"global_anchor", "reservoir_only"}:
        raise ValueError(f"unsupported incremental null: {world}")
    rng = np.random.default_rng(seed)
    labels = _balanced_labels(spec, rng)
    local = np.zeros(
        (spec.authors, spec.conditions, spec.ambient),
        dtype=float,
    )
    event_mask = np.zeros(spec.conditions, dtype=bool)
    if world == "global_anchor":
        block = np.arange(
            spec.conditions // 2 - spec.event_width // 2,
            spec.conditions // 2 - spec.event_width // 2
            + spec.event_width,
        )
        event_mask[block] = True
        local[:, block] = 0.0
    gamma = _maximum_centered_eigenvalue(local) + 1.0
    paths = _embed_reservoir(
        local,
        event_mask=event_mask,
        gamma=gamma,
        rng=np.random.default_rng(seed + 10_019),
    )
    views = []
    for view in range(spec.views):
        noise = np.random.default_rng(
            seed + 20_021 + 101 * view
        ).normal(
            scale=spec.noise_sd,
            size=paths.shape,
        )
        views.append(paths + noise)
    return {
        "world": world,
        "labels": labels,
        "views": np.asarray(views),
    }


def _bron_kerbosch_maximal_cliques(
    adjacency: list[int],
    *,
    node_cap: int,
) -> tuple[list[tuple[int, ...]], int]:
    n = len(adjacency)
    cliques: list[tuple[int, ...]] = []
    visited = 0

    def bits(mask: int) -> list[int]:
        output = []
        while mask:
            bit = mask & -mask
            output.append(bit.bit_length() - 1)
            mask ^= bit
        return output

    def recurse(current: int, possible: int, excluded: int) -> None:
        nonlocal visited
        visited += 1
        if visited > node_cap:
            raise EnumerationCapError(
                f"Bron-Kerbosch exceeded node cap {node_cap}"
            )
        if possible == 0 and excluded == 0:
            members = tuple(bits(current))
            if len(members) >= 3:
                cliques.append(members)
            return
        union = possible | excluded
        pivot = -1
        if union:
            pivot = max(
                bits(union),
                key=lambda item: (
                    possible & adjacency[item]
                ).bit_count(),
            )
        candidates = (
            possible
            if pivot < 0
            else possible & ~adjacency[pivot]
        )
        while candidates:
            bit = candidates & -candidates
            vertex = bit.bit_length() - 1
            recurse(
                current | bit,
                possible & adjacency[vertex],
                excluded & adjacency[vertex],
            )
            possible &= ~bit
            excluded |= bit
            candidates &= ~bit

    recurse(0, (1 << n) - 1, 0)
    return cliques, visited


def _is_common_ball(
    points: np.ndarray,
    members: tuple[int, ...],
    radius: float,
) -> bool:
    _, enclosing_radius = minimum_enclosing_ball(
        points[list(members)]
    )
    return bool(enclosing_radius <= radius + 1e-9)


def exact_maximal_hyperedges(
    points: np.ndarray,
    *,
    radius: float,
    node_cap: int,
) -> tuple[list[tuple[int, ...]], dict[str, int]]:
    """Enumerate all inclusion-maximal common-ball sets of size at least 3."""
    points = np.asarray(points, dtype=float)
    n, ambient = points.shape
    distances = np.linalg.norm(
        points[:, None, :] - points[None, :, :],
        axis=-1,
    )
    adjacency = []
    for left in range(n):
        mask = 0
        for right in range(n):
            if (
                left != right
                and distances[left, right] <= 2.0 * radius + 1e-9
            ):
                mask |= 1 << right
        adjacency.append(mask)
    cliques, bron_nodes = _bron_kerbosch_maximal_cliques(
        adjacency,
        node_cap=node_cap,
    )
    feasible: set[frozenset[int]] = set()
    memo: set[frozenset[int]] = set()
    split_nodes = 0

    def recurse(members_set: frozenset[int]) -> None:
        nonlocal split_nodes
        if members_set in memo or len(members_set) < 3:
            return
        memo.add(members_set)
        split_nodes += 1
        if bron_nodes + split_nodes > node_cap:
            raise EnumerationCapError(
                f"common-ball splitting exceeded node cap {node_cap}"
            )
        members = tuple(sorted(members_set))
        if _is_common_ball(points, members, radius):
            feasible.add(members_set)
            return
        witness: tuple[int, ...] | None = None
        maximum_witness = min(ambient + 1, len(members))
        for size in range(3, maximum_witness + 1):
            for candidate in combinations(members, size):
                if not _is_common_ball(points, candidate, radius):
                    witness = candidate
                    break
            if witness is not None:
                break
        if witness is None:
            witness = members
        for vertex in witness:
            recurse(members_set - {vertex})

    for clique in cliques:
        recurse(frozenset(clique))
    maximal = [
        item for item in feasible
        if not any(item < other for other in feasible)
    ]
    output = sorted(
        (tuple(sorted(item)) for item in maximal),
        key=lambda item: (-len(item), item),
    )
    return output, {
        "bron_kerbosch_nodes": bron_nodes,
        "split_nodes": split_nodes,
        "candidate_cliques": len(cliques),
    }


def exhaustive_maximal_hyperedges(
    points: np.ndarray,
    *,
    radius: float,
) -> list[tuple[int, ...]]:
    """Brute-force truth used only by small-n correctness tests."""
    points = np.asarray(points, dtype=float)
    feasible: list[frozenset[int]] = []
    for size in range(3, len(points) + 1):
        for members in combinations(range(len(points)), size):
            if _is_common_ball(points, members, radius):
                feasible.append(frozenset(members))
    maximal = [
        item for item in feasible
        if not any(item < other for other in feasible)
    ]
    return sorted(
        (tuple(sorted(item)) for item in maximal),
        key=lambda item: (-len(item), item),
    )


def _uncertainty_radius(views: np.ndarray) -> np.ndarray:
    aggregate = views.mean(axis=0)
    dispersion = np.sqrt(np.mean(
        np.sum((views - aggregate[None, ...]) ** 2, axis=-1),
        axis=0,
    ))
    radius = np.median(dispersion, axis=0)
    positive = radius[radius > 1e-10]
    fallback = float(np.median(positive)) if len(positive) else 1e-4
    return np.maximum(radius, max(fallback * 0.25, 1e-6))


def _specificity(authors: int, multiplicity: int) -> float:
    return (authors - multiplicity) / max(authors - 2, 1)


def _core_scores(
    grids: list[list[list[list[tuple[int, ...]]]]],
    *,
    authors: int,
) -> tuple[
    dict[frozenset[int], float],
    list[dict[frozenset[int], float]],
]:
    candidates = {
        frozenset(edge)
        for view in grids
        for condition in view
        for radius_edges in condition
        for edge in radius_edges
        if len(edge) >= 3
    }
    per_view: list[dict[frozenset[int], float]] = []
    for view in grids:
        denominator = len(view) * len(view[0])
        scores: dict[frozenset[int], float] = {}
        for candidate in candidates:
            total = 0.0
            for condition in view:
                for radius_edges in condition:
                    best = 0.0
                    for edge in radius_edges:
                        edge_set = frozenset(edge)
                        if candidate <= edge_set:
                            best = max(
                                best,
                                _specificity(authors, len(edge)),
                            )
                    total += best
            scores[candidate] = total / denominator
        per_view.append(scores)
    minimum_scores = {
        candidate: min(
            scores.get(candidate, 0.0)
            for scores in per_view
        )
        for candidate in candidates
    }
    return minimum_scores, per_view


def _inclusion_maximal_cores(
    scores: dict[frozenset[int], float],
    *,
    threshold: float,
) -> list[frozenset[int]]:
    passing = {
        members for members, score in scores.items()
        if len(members) >= 3 and score >= threshold
    }
    return sorted(
        (
            members for members in passing
            if not any(members < other for other in passing)
        ),
        key=lambda members: (-len(members), tuple(sorted(members))),
    )


def _cores_overlap(cores: list[frozenset[int]]) -> bool:
    return any(
        bool(left & right)
        for left, right in combinations(cores, 2)
    )


def _predicted_labels(
    authors: int,
    cores: list[frozenset[int]],
) -> np.ndarray:
    labels = np.arange(authors, dtype=int)
    next_label = 0
    assigned = np.zeros(authors, dtype=bool)
    for core in cores:
        indices = np.asarray(sorted(core), dtype=int)
        labels[indices] = next_label
        assigned[indices] = True
        next_label += 1
    for author in np.flatnonzero(~assigned):
        labels[author] = next_label
        next_label += 1
    return labels


def _pair_truth(labels: np.ndarray) -> np.ndarray:
    upper = np.triu_indices(len(labels), 1)
    return (labels[upper[0]] == labels[upper[1]]).astype(int)


def _pair_core_scores(
    scores: dict[frozenset[int], float],
    authors: int,
) -> np.ndarray:
    upper = np.triu_indices(authors, 1)
    output = np.zeros(len(upper[0]), dtype=float)
    for index, (left, right) in enumerate(
        zip(upper[0], upper[1], strict=True)
    ):
        output[index] = max(
            (
                score for members, score in scores.items()
                if left in members and right in members
            ),
            default=0.0,
        )
    return output


def _core_jaccard(
    aggregate: list[frozenset[int]],
    per_view: list[list[frozenset[int]]],
) -> float:
    if not aggregate:
        return 0.0
    values = []
    for core in aggregate:
        for view_cores in per_view:
            values.append(max(
                (
                    len(core & candidate) / len(core | candidate)
                    for candidate in view_cores
                ),
                default=0.0,
            ))
    return float(np.median(values))


def analyze_incidence_population(
    views: np.ndarray,
    labels: np.ndarray,
    *,
    spec: IncrementalSpec,
) -> dict[str, Any]:
    """Estimate exact persistent cores and whole-map baseline metrics."""
    radius = _uncertainty_radius(views)
    grids: list[list[list[list[tuple[int, ...]]]]] = []
    exact_sets = 0
    approximate_sets = 0
    exact_matched_by_approx = 0
    approximate_matched_by_exact = 0
    enumeration_nodes = 0
    try:
        for view in views:
            view_grid = []
            for condition in range(spec.conditions):
                condition_grid = []
                for epsilon in spec.epsilon_grid:
                    current_radius = float(epsilon * radius[condition])
                    exact, diagnostics = exact_maximal_hyperedges(
                        view[:, condition],
                        radius=current_radius,
                        node_cap=spec.enumeration_node_cap,
                    )
                    approximate = [
                        edge for edge in verified_hyperedges(
                            view[:, condition],
                            epsilon=current_radius,
                        )
                        if len(edge) >= 3
                    ]
                    exact_lookup = {frozenset(item) for item in exact}
                    approximate_lookup = {
                        frozenset(item) for item in approximate
                    }
                    exact_sets += len(exact_lookup)
                    approximate_sets += len(approximate_lookup)
                    exact_matched_by_approx += len(
                        exact_lookup & approximate_lookup
                    )
                    approximate_matched_by_exact += len(
                        exact_lookup & approximate_lookup
                    )
                    enumeration_nodes += (
                        diagnostics["bron_kerbosch_nodes"]
                        + diagnostics["split_nodes"]
                    )
                    condition_grid.append(exact)
                view_grid.append(condition_grid)
            grids.append(view_grid)
    except EnumerationCapError as error:
        return {
            "status": "REFUSE_ENUMERATION_CAP",
            "refusal_reason": str(error),
        }

    scores, per_view_scores = _core_scores(
        grids,
        authors=spec.authors,
    )
    cores = _inclusion_maximal_cores(
        scores,
        threshold=spec.core_persistence_threshold,
    )
    ambiguity = _cores_overlap(cores)
    per_view_cores = [
        _inclusion_maximal_cores(
            view_scores,
            threshold=spec.core_persistence_threshold,
        )
        for view_scores in per_view_scores
    ]
    selected = [] if ambiguity else cores
    coverage = (
        len(set().union(*selected)) / spec.authors
        if selected else 0.0
    )
    group_claim = bool(
        len(selected) >= 2
        and coverage >= spec.minimum_group_coverage
    )
    predicted = _predicted_labels(spec.authors, selected)
    upper = np.triu_indices(spec.authors, 1)
    predicted_pairs = (
        predicted[upper[0]] == predicted[upper[1]]
    ).astype(int)
    pair_truth = _pair_truth(labels)
    pair_scores = _pair_core_scores(scores, spec.authors)
    whole_scores = -pairwise_whole_map_distances(views.mean(axis=0))
    return {
        "status": (
            "REFUSE_CORE_AMBIGUITY"
            if ambiguity
            else "ESTIMATE_READY"
        ),
        "refused": ambiguity,
        "group_claim": group_claim,
        "coverage": coverage,
        "selected_cores": [
            sorted(int(item) for item in core)
            for core in selected
        ],
        "candidate_core_count": len(scores),
        "incidence_auc": float(roc_auc_score(
            pair_truth,
            pair_scores,
        )),
        "whole_map_auc": float(roc_auc_score(
            pair_truth,
            whole_scores,
        )),
        "group_f1": float(f1_score(
            pair_truth,
            predicted_pairs,
            zero_division=0,
        )),
        "group_ari": float(adjusted_rand_score(
            labels,
            predicted,
        )),
        "cross_view_core_jaccard": _core_jaccard(
            selected,
            per_view_cores,
        ),
        "pair_scores": pair_scores.tolist(),
        "whole_map_scores": whole_scores.tolist(),
        "pair_truth": pair_truth.tolist(),
        "enumeration_nodes": enumeration_nodes,
        "exact_hyperedge_sets": exact_sets,
        "approximate_hyperedge_sets": approximate_sets,
        "approximate_precision": (
            approximate_matched_by_exact / approximate_sets
            if approximate_sets else 1.0
        ),
        "approximate_recall": (
            exact_matched_by_approx / exact_sets
            if exact_sets else 1.0
        ),
    }


def analyze_counterfactual_pair(
    pair: dict[str, Any],
    *,
    spec: IncrementalSpec,
    permutation_seed: int,
) -> dict[str, Any]:
    """Analyze one matched positive/counterfactual population pair."""
    positive = analyze_incidence_population(
        pair["positive_views"],
        pair["labels"],
        spec=spec,
    )
    negative = analyze_incidence_population(
        pair["negative_views"],
        pair["labels"],
        spec=spec,
    )
    if (
        positive["status"] == "REFUSE_ENUMERATION_CAP"
        or negative["status"] == "REFUSE_ENUMERATION_CAP"
    ):
        return {
            "status": "REFUSE_ENUMERATION_CAP",
            "positive": positive,
            "negative": negative,
        }
    permutation = np.random.default_rng(permutation_seed).permutation(
        pair["labels"]
    )
    permuted_truth = _pair_truth(permutation)
    permutation_auc = float(roc_auc_score(
        permuted_truth,
        np.asarray(positive["pair_scores"], dtype=float),
    ))
    return {
        "status": "ESTIMATE_READY",
        "pair_id": pair["pair_id"],
        "positive_world": pair["positive_world"],
        "negative_world": pair["negative_world"],
        "oracle_distance_relative_error": (
            pair["oracle_distance_relative_error"]
        ),
        "fitted_distance_relative_error": (
            pair["fitted_distance_relative_error"]
        ),
        "orthogonal_mapping_error": pair["orthogonal_mapping_error"],
        "positive": positive,
        "negative": negative,
        "incremental_auc": (
            float(positive["incidence_auc"])
            - float(positive["whole_map_auc"])
        ),
        "permutation_auc": permutation_auc,
        "chaining_error": bool(
            pair["pair_id"] == "CF2"
            and negative["group_claim"]
        ),
    }
