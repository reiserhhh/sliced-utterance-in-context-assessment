"""Truth-open audit for M4-C chart, topology, and response recovery."""
from __future__ import annotations

from typing import Any

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, minimum_spanning_tree
from scipy.spatial.distance import pdist, squareform
from scipy.stats import spearmanr

from .m4_condition_manifold_contracts import (
    M4ConditionEstimate,
    M4ConditionObserved,
    M4ConditionTruth,
)


def _safe_spearman(first: np.ndarray, second: np.ndarray) -> float:
    x = np.asarray(first, dtype=float).ravel()
    y = np.asarray(second, dtype=float).ravel()
    if np.std(x) <= 1e-12 or np.std(y) <= 1e-12:
        return 0.0
    value = float(spearmanr(x, y).statistic)
    return value if np.isfinite(value) else 0.0


def _neighbor_jaccard(
    first: np.ndarray,
    second: np.ndarray,
    *,
    neighbors: int,
) -> float:
    left = np.asarray(first, dtype=float).copy()
    right = np.asarray(second, dtype=float).copy()
    np.fill_diagonal(left, np.inf)
    np.fill_diagonal(right, np.inf)
    k = min(neighbors, len(left) - 1)
    left_ids = np.argpartition(left, k, axis=1)[:, :k]
    right_ids = np.argpartition(right, k, axis=1)[:, :k]
    scores = []
    for row in range(len(left)):
        a = set(left_ids[row].tolist())
        b = set(right_ids[row].tolist())
        scores.append(len(a & b) / max(1, len(a | b)))
    return float(np.mean(scores))


def _intrinsic_dimension(distances: np.ndarray, neighbors: int = 8) -> float:
    values = np.asarray(distances, dtype=float).copy()
    np.fill_diagonal(values, np.inf)
    k = min(neighbors, len(values) - 1)
    ordered = np.sort(values, axis=1)[:, :k]
    radius = np.maximum(ordered[:, -1], 1e-10)
    log_ratio = np.log(radius[:, None] / np.maximum(ordered[:, :-1], 1e-10))
    denominator = np.mean(log_ratio, axis=1)
    local = np.divide(
        k - 1,
        np.maximum((k - 1) * denominator, 1e-10),
    )
    finite = local[np.isfinite(local) & (local < 20.0)]
    return float(np.median(finite)) if len(finite) else float("nan")


def _topology_signature(distances: np.ndarray) -> tuple[str, dict[str, float]]:
    values = np.asarray(distances, dtype=float).copy()
    np.fill_diagonal(values, np.inf)
    n = len(values)
    k = min(3, n - 1)
    nearest = np.argpartition(values, k, axis=1)[:, :k]
    graph = np.zeros((n, n), dtype=bool)
    rows = np.arange(n)[:, None]
    graph[rows, nearest] = True
    graph |= graph.T
    np.fill_diagonal(graph, False)
    components, _ = connected_components(
        csr_matrix(graph),
        directed=False,
        return_labels=True,
    )
    degree = graph.sum(axis=1)
    edges = int(np.sum(graph) // 2)
    cycle_rank = max(0, edges - n + int(components))
    dimension = _intrinsic_dimension(values)
    tree = minimum_spanning_tree(csr_matrix(np.where(
        np.isfinite(values),
        values,
        0.0,
    )))
    tree_graph = (tree.toarray() + tree.toarray().T) > 0.0
    tree_degree = tree_graph.sum(axis=1)
    tree_endpoints = np.flatnonzero(tree_degree == 1)
    tree_edges = tree.toarray()
    positive_tree_edges = tree_edges[tree_edges > 0.0]
    typical_edge = (
        float(np.median(positive_tree_edges))
        if len(positive_tree_edges)
        else float("nan")
    )
    closure_ratio = (
        float(values[tree_endpoints[0], tree_endpoints[1]] / typical_edge)
        if len(tree_endpoints) == 2 and typical_edge > 1e-12
        else float("nan")
    )
    endpoint_fraction = float(np.mean(tree_degree == 1))
    branch_fraction = float(np.mean(tree_degree >= 3))
    if dimension >= 1.45:
        label = "surface"
    elif np.max(tree_degree) >= 3 and len(tree_endpoints) >= 3:
        label = "branch"
    elif len(tree_endpoints) == 2 and closure_ratio <= 10.0:
        label = "cycle"
    else:
        label = "curve"
    return label, {
        "intrinsic_dimension": dimension,
        "graph_components": float(components),
        "graph_cycle_rank": float(cycle_rank),
        "endpoint_fraction": endpoint_fraction,
        "branch_fraction": branch_fraction,
        "mst_closure_ratio": closure_ratio,
    }


def _response_r2(
    target: np.ndarray,
    prediction: np.ndarray,
    baseline: np.ndarray,
) -> float:
    denominator = float(np.sum((target - baseline) ** 2))
    if denominator <= 1e-12:
        return float("nan")
    return 1.0 - float(np.sum((target - prediction) ** 2)) / denominator


def _response_geometry(
    estimate: np.ndarray,
    truth: np.ndarray,
) -> float:
    estimate = estimate - estimate.mean(axis=1, keepdims=True)
    truth = truth - truth.mean(axis=1, keepdims=True)
    return _safe_spearman(
        pdist(estimate.reshape(len(estimate), -1)),
        pdist(truth.reshape(len(truth), -1)),
    )


def audit_m4_condition_manifold(
    estimate: M4ConditionEstimate,
    observed: M4ConditionObserved,
    truth: M4ConditionTruth,
    *,
    minimum_geometry: float,
    minimum_neighbor_jaccard: float,
    minimum_response_retention: float,
    minimum_conditional_response_r2: float,
    response_perturbation_invariant: bool,
) -> dict[str, Any]:
    """Audit latent geometry only after the response-safe chart is frozen."""
    fused = np.mean(
        estimate.chart.panel_features["mechanism_evaluation"],
        axis=0,
    )
    discovered_distance = squareform(pdist(fused))
    truth_distance = truth.geodesic_distances["mechanism_evaluation"]
    geometry = _safe_spearman(
        squareform(discovered_distance, checks=False),
        squareform(truth_distance, checks=False),
    )
    neighbor_jaccard = _neighbor_jaccard(
        discovered_distance,
        truth_distance,
        neighbors=10,
    )
    topology, topology_diagnostics = _topology_signature(
        discovered_distance
    )
    expected_topology = {
        "closed_surface": "surface",
        "cycle_aliased": "cycle",
        "none": "none",
    }.get(truth.expected_topology, truth.expected_topology)
    topology_match = bool(
        expected_topology == "none"
        or topology == expected_topology
        or (
            truth.expected_topology == "branch"
            and estimate.chart.selected_family == "landmark_atlas"
        )
    )

    target = observed.mechanism_evaluation.response
    noiseless = truth.noiseless_response["mechanism_evaluation"]
    oracle_r2 = _response_r2(
        target,
        noiseless,
        estimate.response_baseline,
    )
    response_retention = (
        float(estimate.response_r2 / oracle_r2)
        if oracle_r2 > 1e-8
        else float("nan")
    )
    mechanism_underresolved = bool(
        estimate.response_r2 < minimum_conditional_response_r2
    )
    mechanism_alias_refused = bool(
        truth.alias
        and mechanism_underresolved
        and oracle_r2 >= 0.50
    )
    chart_identified = bool(
        not estimate.chart.refused
        and geometry >= minimum_geometry
        and neighbor_jaccard >= minimum_neighbor_jaccard
    )
    post_topology_refusal = bool(
        topology == "branch"
        and estimate.chart.selected_family != "landmark_atlas"
    )
    topology_resolved = bool(
        topology_match
        and (
            truth.world != "topology_mismatch"
            or estimate.chart.refused
            or estimate.chart.selected_family == "landmark_atlas"
            or post_topology_refusal
        )
    )
    if truth.expected_chart_status == "IDENTIFIABLE":
        expected_resolution = chart_identified
    elif truth.expected_chart_status == "ATLAS_OR_REFUSE":
        expected_resolution = topology_resolved
    elif truth.expected_chart_status == "QUOTIENT_ONLY":
        expected_resolution = mechanism_alias_refused
    else:
        expected_resolution = estimate.chart.refused
    return {
        "world": truth.world,
        "expected_chart_status": truth.expected_chart_status,
        "expected_topology": truth.expected_topology,
        "selected_family": estimate.chart.selected_family,
        "selected_dimensions": estimate.chart.selected_parameters[
            "dimensions"
        ],
        "selected_neighbors": estimate.chart.selected_parameters[
            "neighbors"
        ],
        "chart_refused": float(estimate.chart.refused),
        "refusal_reasons": "|".join(estimate.chart.refusal_reasons),
        "expected_resolution": float(expected_resolution),
        "chart_identified": float(chart_identified),
        "geometry_spearman": geometry,
        "neighbor_jaccard": neighbor_jaccard,
        "topology_detected": topology,
        "topology_match": float(topology_match),
        "topology_resolved": float(topology_resolved),
        "post_topology_refusal": float(post_topology_refusal),
        "cross_source_geometry_selection": estimate.chart.selection_diagnostics[
            "cross_source_geometry"
        ],
        "split_geometry_selection": estimate.chart.selection_diagnostics[
            "author_split_geometry"
        ],
        "trustworthiness_selection": estimate.chart.selection_diagnostics[
            "trustworthiness"
        ],
        "continuity_selection": estimate.chart.selection_diagnostics[
            "continuity"
        ],
        "coverage_selection": estimate.chart.selection_diagnostics["coverage"],
        "cross_source_geometry_evaluation": (
            estimate.chart.evaluation_diagnostics["cross_source_geometry"]
        ),
        "author_leakage_auc": estimate.chart.author_leakage_auc,
        "response_r2": estimate.response_r2,
        "oracle_response_r2": oracle_r2,
        "response_retention": response_retention,
        "response_geometry": _response_geometry(
            estimate.response_predictions,
            noiseless,
        ),
        "response_mae": estimate.response_mae,
        "mechanism_underresolved": float(mechanism_underresolved),
        "mechanism_alias_refused": float(mechanism_alias_refused),
        "response_perturbation_invariant": float(
            response_perturbation_invariant
        ),
        **topology_diagnostics,
    }
