"""Strong-chain counterfactuals for higher-order incidence structure."""
from __future__ import annotations

from itertools import combinations
from typing import Any
import warnings

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.linalg import orthogonal_procrustes
from scipy.spatial.distance import squareform
from scipy.stats import wasserstein_distance
from sklearn.cluster import SpectralClustering
from sklearn.metrics import (
    adjusted_rand_score,
    f1_score,
    roc_auc_score,
    silhouette_score,
)

from suica_core.v8_incidence_incremental import (
    IncrementalSpec,
    _balanced_labels,
    _baseline_positions,
    _center_rows,
    _distance_matrix,
    _embed_reservoir,
    _maximum_centered_eigenvalue,
    _pair_truth,
    _uncertainty_radius,
)
from suica_core.v8_incidence_incremental_v31 import (
    analyze_incidence_population_v31,
)
from suica_core.v8_incidence_multiplicity import minimum_enclosing_ball


STRONG_CHAIN_BLOCKS: tuple[tuple[int, int, int], ...] = (
    (0, 1, 2),
    (0, 1, 3),
    (0, 2, 4),
    (0, 3, 5),
    (0, 4, 5),
    (1, 2, 5),
    (1, 3, 4),
    (1, 4, 5),
    (2, 3, 4),
    (2, 3, 5),
)


def strong_chain_block_counts() -> tuple[np.ndarray, np.ndarray]:
    """Return author and author-pair counts for the balanced triplet design."""
    author_counts = np.zeros(6, dtype=int)
    pair_counts = np.zeros((6, 6), dtype=int)
    for block in STRONG_CHAIN_BLOCKS:
        author_counts[list(block)] += 1
        for left, right in combinations(block, 2):
            pair_counts[left, right] += 1
            pair_counts[right, left] += 1
    return author_counts, pair_counts


def _group_anchors(ambient: int, scale: float) -> np.ndarray:
    anchors = np.asarray([
        [-scale, -scale],
        [-scale, scale],
        [scale, -scale],
        [scale, scale],
    ])
    if ambient > 2:
        anchors = np.pad(
            anchors,
            ((0, 0), (0, ambient - 2)),
        )
    return anchors


def strong_chain_local_geometry(
    *,
    world: str,
    labels: np.ndarray,
    spec: IncrementalSpec,
    private_excursion_radius: float = 0.90,
    anchor_scale: float = 1.75,
) -> dict[str, np.ndarray]:
    """Construct core-six or pairwise-matched strong-chain local paths."""
    if world not in {"core6_matched", "strong_chain"}:
        raise ValueError(f"unsupported strong-chain world: {world}")
    if spec.authors != 24 or spec.groups != 4:
        raise ValueError("registered strong-chain design requires 24 authors")
    baseline = _baseline_positions(spec)
    local = np.zeros_like(baseline)
    event_mask = np.zeros(spec.conditions, dtype=bool)
    event_mask[:50] = True
    local[:, :50] = baseline[:, :50]
    opportunity = np.zeros((spec.authors, spec.conditions), dtype=int)
    cooccurrence = np.zeros((spec.authors, spec.authors), dtype=int)
    anchors = _group_anchors(spec.ambient, anchor_scale)

    for group in range(spec.groups):
        members = np.sort(np.flatnonzero(labels == group))
        if len(members) != 6:
            raise ValueError("strong-chain groups must contain six authors")
        anchor = anchors[group]
        if world == "core6_matched":
            local[np.ix_(members, np.arange(10))] = anchor
            opportunity[np.ix_(members, np.arange(25))] = 1
            for left, right in combinations(members, 2):
                cooccurrence[left, right] += 10
                cooccurrence[right, left] += 10
            angles = (
                2.0 * np.pi * np.arange(6) / 6.0
                + group * np.pi / 12.0
            )
            private = np.repeat(anchor[None, :], 6, axis=0)
            private[:, 0] += private_excursion_radius * np.cos(angles)
            private[:, 1] += private_excursion_radius * np.sin(angles)
            for condition in range(10, 25):
                local[members, condition] = private
        else:
            for block_index, block in enumerate(STRONG_CHAIN_BLOCKS):
                current = members[np.asarray(block, dtype=int)]
                conditions = np.arange(
                    5 * block_index,
                    5 * block_index + 5,
                )
                local[np.ix_(current, conditions)] = anchor
                opportunity[np.ix_(current, conditions)] = 1
                for left, right in combinations(current, 2):
                    cooccurrence[left, right] += 5
                    cooccurrence[right, left] += 5
    return {
        "local": local,
        "event_mask": event_mask,
        "opportunity": opportunity,
        "cooccurrence": cooccurrence,
    }


def simulate_strong_chain_pair(
    *,
    seed: int,
    spec: IncrementalSpec,
    private_excursion_radius: float = 0.90,
    anchor_scale: float = 1.75,
) -> dict[str, Any]:
    """Generate core-six and strong-chain paths with matched whole geometry."""
    labels = _balanced_labels(spec, np.random.default_rng(seed))
    positive_local = strong_chain_local_geometry(
        world="core6_matched",
        labels=labels,
        spec=spec,
        private_excursion_radius=private_excursion_radius,
        anchor_scale=anchor_scale,
    )
    chain_local = strong_chain_local_geometry(
        world="strong_chain",
        labels=labels,
        spec=spec,
        private_excursion_radius=private_excursion_radius,
        anchor_scale=anchor_scale,
    )
    gamma = (
        max(
            _maximum_centered_eigenvalue(positive_local["local"]),
            _maximum_centered_eigenvalue(chain_local["local"]),
        )
        + 1.0
    )
    positive = _embed_reservoir(
        positive_local["local"],
        event_mask=positive_local["event_mask"],
        gamma=gamma,
        rng=np.random.default_rng(seed + 30_007),
    )
    chain = _embed_reservoir(
        chain_local["local"],
        event_mask=chain_local["event_mask"],
        gamma=gamma,
        rng=np.random.default_rng(seed + 40_009),
    )
    positive_flat = positive.reshape(spec.authors, -1)
    chain_flat = chain.reshape(spec.authors, -1)
    transform, _ = orthogonal_procrustes(positive_flat, chain_flat)
    mapping_error = float(
        np.linalg.norm(positive_flat @ transform - chain_flat)
        / max(np.linalg.norm(chain_flat), 1e-12)
    )
    if mapping_error > 1e-8:
        raise RuntimeError(
            f"orthogonal pair mapping failed: {mapping_error:.6g}"
        )
    positive_views = []
    chain_views = []
    for view in range(spec.views):
        noise = np.random.default_rng(
            seed + 50_021 + 101 * view
        ).normal(
            scale=spec.noise_sd,
            size=positive_flat.shape,
        )
        positive_views.append(
            (positive_flat + noise).reshape(positive.shape)
        )
        chain_views.append(
            (chain_flat + noise @ transform).reshape(chain.shape)
        )
    positive_views_array = np.asarray(positive_views)
    chain_views_array = np.asarray(chain_views)
    oracle_positive = _distance_matrix(positive)
    oracle_chain = _distance_matrix(chain)
    fitted_positive = _distance_matrix(
        positive_views_array.mean(axis=0)
    )
    fitted_chain = _distance_matrix(chain_views_array.mean(axis=0))
    oracle_pair_positive = (
        positive_local["cooccurrence"] / spec.conditions
    )
    oracle_pair_chain = chain_local["cooccurrence"] / spec.conditions
    return {
        "pair_id": "SC1",
        "positive_world": "core6_matched",
        "negative_world": "strong_chain",
        "labels": labels,
        "positive_truth": positive,
        "negative_truth": chain,
        "positive_views": positive_views_array,
        "negative_views": chain_views_array,
        "positive_local": positive_local["local"],
        "negative_local": chain_local["local"],
        "positive_opportunity": positive_local["opportunity"],
        "negative_opportunity": chain_local["opportunity"],
        "oracle_pair_positive": oracle_pair_positive,
        "oracle_pair_negative": oracle_pair_chain,
        "oracle_pair_matrix_max_error": float(
            np.max(np.abs(
                oracle_pair_positive - oracle_pair_chain
            ))
        ),
        "oracle_distance_relative_error": float(
            np.linalg.norm(oracle_positive - oracle_chain)
            / max(np.linalg.norm(oracle_positive), 1e-12)
        ),
        "fitted_distance_relative_error": float(
            np.linalg.norm(fitted_positive - fitted_chain)
            / max(np.linalg.norm(fitted_positive), 1e-12)
        ),
        "orthogonal_mapping_error": mapping_error,
        "gamma": gamma,
        "private_excursion_radius": private_excursion_radius,
        "anchor_scale": anchor_scale,
    }


def condition_aligned_pair_matrix(
    views: np.ndarray,
    *,
    spec: IncrementalSpec,
) -> np.ndarray:
    """Aggregate same-condition pair recurrence across radii and views."""
    radius = _uncertainty_radius(views)
    output = np.zeros((spec.authors, spec.authors), dtype=float)
    for condition in range(spec.conditions):
        points = views[:, :, condition, :]
        distances = np.linalg.norm(
            points[:, :, None, :] - points[:, None, :, :],
            axis=-1,
        )
        for epsilon in spec.epsilon_grid:
            supported = np.all(
                distances <= 2.0 * epsilon * radius[condition],
                axis=0,
            )
            output += supported.astype(float)
    output /= spec.conditions * len(spec.epsilon_grid)
    np.fill_diagonal(output, 0.0)
    return output


def soft_condition_aligned_pair_matrix(
    views: np.ndarray,
    *,
    spec: IncrementalSpec,
) -> np.ndarray:
    """Return cross-view minimum Gaussian affinity by condition."""
    radius = _uncertainty_radius(views)
    output = np.zeros((spec.authors, spec.authors), dtype=float)
    for condition in range(spec.conditions):
        points = views[:, :, condition, :]
        distances = np.linalg.norm(
            points[:, :, None, :] - points[:, None, :, :],
            axis=-1,
        )
        kernels = np.exp(
            -0.5
            * (
                distances
                / max(float(radius[condition]), 1e-8)
            ) ** 2
        )
        output += np.min(kernels, axis=0)
    output /= spec.conditions
    np.fill_diagonal(output, 0.0)
    return output


def _laplacian_spectrum(matrix: np.ndarray) -> np.ndarray:
    strength = matrix.sum(axis=1)
    inverse = np.zeros_like(strength)
    positive = strength > 1e-12
    inverse[positive] = 1.0 / np.sqrt(strength[positive])
    normalized = inverse[:, None] * matrix * inverse[None, :]
    laplacian = np.eye(len(matrix)) - normalized
    laplacian[~positive, ~positive] = 0.0
    return np.linalg.eigvalsh(
        (laplacian + laplacian.T) / 2.0
    )


def _pair_condition_distances(views: np.ndarray) -> np.ndarray:
    aggregate = views.mean(axis=0)
    upper = np.triu_indices(aggregate.shape[0], 1)
    delta = (
        aggregate[upper[0], :, :]
        - aggregate[upper[1], :, :]
    )
    return np.linalg.norm(delta, axis=-1).reshape(-1)


def pairwise_matching_metrics(
    pair: dict[str, Any],
    *,
    spec: IncrementalSpec,
) -> dict[str, Any]:
    """Compare all registered aggregate pairwise summaries."""
    positive = condition_aligned_pair_matrix(
        pair["positive_views"],
        spec=spec,
    )
    chain = condition_aligned_pair_matrix(
        pair["negative_views"],
        spec=spec,
    )
    upper = np.triu_indices(spec.authors, 1)
    positive_vector = positive[upper]
    chain_vector = chain[upper]
    correlation = float(np.corrcoef(
        positive_vector,
        chain_vector,
    )[0, 1])
    truth = _pair_truth(pair["labels"])
    positive_auc = float(roc_auc_score(truth, positive_vector))
    chain_auc = float(roc_auc_score(truth, chain_vector))
    positive_distances = _pair_condition_distances(
        pair["positive_views"]
    )
    chain_distances = _pair_condition_distances(
        pair["negative_views"]
    )
    scale = float(np.median(np.concatenate([
        positive_distances,
        chain_distances,
    ])))
    scale = max(scale, 1e-8)
    positive_spectrum = _laplacian_spectrum(positive)
    chain_spectrum = _laplacian_spectrum(chain)
    return {
        "positive_pair_matrix": positive,
        "chain_pair_matrix": chain,
        "observed_pair_matrix_mae": float(
            np.mean(np.abs(positive - chain))
        ),
        "observed_pair_matrix_correlation": correlation,
        "positive_pair_auc": positive_auc,
        "chain_pair_auc": chain_auc,
        "pair_auc_difference": positive_auc - chain_auc,
        "normalized_wasserstein": float(wasserstein_distance(
            positive_distances / scale,
            chain_distances / scale,
        )),
        "degree_strength_relative_error": float(
            np.linalg.norm(
                positive.sum(axis=1) - chain.sum(axis=1)
            )
            / max(np.linalg.norm(positive.sum(axis=1)), 1e-12)
        ),
        "laplacian_spectrum_relative_error": float(
            np.linalg.norm(positive_spectrum - chain_spectrum)
            / max(np.linalg.norm(positive_spectrum), 1e-12)
        ),
    }


def _component_labels(adjacency: np.ndarray) -> np.ndarray:
    labels = np.full(len(adjacency), -1, dtype=int)
    current = 0
    for start in range(len(adjacency)):
        if labels[start] >= 0:
            continue
        stack = [start]
        labels[start] = current
        while stack:
            node = stack.pop()
            neighbors = np.flatnonzero(adjacency[node])
            for neighbor in neighbors:
                if labels[neighbor] < 0:
                    labels[neighbor] = current
                    stack.append(int(neighbor))
        current += 1
    return labels


def _evaluate_partition(
    predicted: np.ndarray,
    truth: np.ndarray,
    *,
    refused: bool,
    diagnostics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    groups = [
        frozenset(int(item) for item in np.flatnonzero(predicted == label))
        for label in np.unique(predicted)
    ]
    eligible = [group for group in groups if len(group) >= 3]
    coverage = (
        len(set().union(*eligible)) / len(predicted)
        if eligible else 0.0
    )
    group_claim = bool(
        not refused
        and len(eligible) >= 2
        and coverage >= 0.75
    )
    true_groups = [
        frozenset(int(item) for item in np.flatnonzero(truth == label))
        for label in np.unique(truth)
    ]
    recovered = sum(group in eligible for group in true_groups)
    upper = np.triu_indices(len(truth), 1)
    truth_pairs = (truth[upper[0]] == truth[upper[1]]).astype(int)
    predicted_pairs = (
        predicted[upper[0]] == predicted[upper[1]]
    ).astype(int)
    return {
        "refused": refused,
        "group_claim": group_claim,
        "coverage": coverage,
        "groups": [sorted(group) for group in eligible],
        "recovered_six_groups": recovered,
        "six_group_claim": bool(group_claim and recovered == len(true_groups)),
        "group_f1": float(f1_score(
            truth_pairs,
            predicted_pairs,
            zero_division=0,
        )),
        "group_ari": float(adjusted_rand_score(truth, predicted)),
        **(diagnostics or {}),
    }


def graph_partitions(
    matrix: np.ndarray,
    truth: np.ndarray,
    *,
    edge_threshold: float,
    spectral_k_min: int,
    spectral_k_max: int,
    spectral_min_eigengap: float,
    spectral_min_silhouette: float,
    seed: int,
) -> dict[str, dict[str, Any]]:
    """Fit frozen aggregate pairwise graph methods."""
    adjacency = matrix >= edge_threshold
    np.fill_diagonal(adjacency, False)
    single_labels = _component_labels(adjacency)
    single = _evaluate_partition(
        single_labels,
        truth,
        refused=False,
    )

    distance = 1.0 - matrix
    np.fill_diagonal(distance, 0.0)
    hierarchy = linkage(
        squareform(distance, checks=True),
        method="complete",
    )
    complete_labels = fcluster(
        hierarchy,
        t=1.0 - edge_threshold,
        criterion="distance",
    ) - 1
    complete = _evaluate_partition(
        complete_labels,
        truth,
        refused=False,
    )

    spectrum = _laplacian_spectrum(matrix)
    k_values = np.arange(
        spectral_k_min,
        min(spectral_k_max, len(matrix) - 1) + 1,
    )
    gaps = np.asarray([
        spectrum[k] - spectrum[k - 1]
        for k in k_values
    ])
    selected_index = int(np.argmax(gaps))
    selected_k = int(k_values[selected_index])
    eigengap = float(gaps[selected_index])
    spectral_refused = bool(
        matrix.sum() <= 1e-12
        or eigengap < spectral_min_eigengap
    )
    if spectral_refused:
        spectral_labels = np.arange(len(matrix), dtype=int)
        silhouette = 0.0
    else:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="Graph is not fully connected",
                category=UserWarning,
            )
            spectral_labels = SpectralClustering(
                n_clusters=selected_k,
                affinity="precomputed",
                assign_labels="cluster_qr",
                random_state=seed,
            ).fit_predict(matrix)
        maximum = max(float(matrix.max()), 1e-8)
        silhouette_distance = 1.0 - matrix / maximum
        np.fill_diagonal(silhouette_distance, 0.0)
        silhouette = float(silhouette_score(
            silhouette_distance,
            spectral_labels,
            metric="precomputed",
        ))
        spectral_refused = silhouette < spectral_min_silhouette
    spectral = _evaluate_partition(
        spectral_labels,
        truth,
        refused=spectral_refused,
        diagnostics={
            "selected_k": selected_k,
            "eigengap": eigengap,
            "silhouette": silhouette,
        },
    )
    return {
        "single_link": single,
        "complete_link": complete,
        "spectral": spectral,
    }


def registered_chain_triplets(
    labels: np.ndarray,
) -> list[frozenset[int]]:
    """Return all 40 global-author triplets in the strong-chain design."""
    output = []
    for group in np.unique(labels):
        members = np.sort(np.flatnonzero(labels == group))
        for block in STRONG_CHAIN_BLOCKS:
            output.append(frozenset(
                int(members[index]) for index in block
            ))
    return output


def direct_common_ball_persistence(
    views: np.ndarray,
    candidates: list[frozenset[int]],
    *,
    spec: IncrementalSpec,
) -> dict[frozenset[int], float]:
    """Score registered sets directly as a diagnostic, not an estimator."""
    radius = _uncertainty_radius(views)
    output: dict[frozenset[int], float] = {}
    denominator = spec.conditions * len(spec.epsilon_grid)
    for candidate in candidates:
        total = 0.0
        indices = sorted(candidate)
        specificity = (
            (spec.authors - len(candidate))
            / max(spec.authors - 2, 1)
        )
        for condition in range(spec.conditions):
            for epsilon in spec.epsilon_grid:
                supported = []
                for view in views:
                    _, enclosing_radius = minimum_enclosing_ball(
                        view[indices, condition]
                    )
                    supported.append(
                        enclosing_radius
                        <= epsilon * radius[condition] + 1e-9
                    )
                if all(supported):
                    total += specificity
        output[candidate] = total / denominator
    return output


def analyze_strong_chain_pair(
    pair: dict[str, Any],
    *,
    spec: IncrementalSpec,
    candidate_closure_cap: int,
    graph_config: dict[str, Any],
    seed: int,
) -> dict[str, Any]:
    """Analyze one matched core-six/strong-chain population pair."""
    positive = analyze_incidence_population_v31(
        pair["positive_views"],
        pair["labels"],
        spec=spec,
        candidate_closure_cap=candidate_closure_cap,
    )
    chain = analyze_incidence_population_v31(
        pair["negative_views"],
        pair["labels"],
        spec=spec,
        candidate_closure_cap=candidate_closure_cap,
    )
    matching = pairwise_matching_metrics(pair, spec=spec)
    positive_graphs = graph_partitions(
        matching["positive_pair_matrix"],
        pair["labels"],
        edge_threshold=float(graph_config["graph_edge_threshold"]),
        spectral_k_min=int(graph_config["spectral_k_min"]),
        spectral_k_max=int(graph_config["spectral_k_max"]),
        spectral_min_eigengap=float(
            graph_config["spectral_min_eigengap"]
        ),
        spectral_min_silhouette=float(
            graph_config["spectral_min_silhouette"]
        ),
        seed=seed,
    )
    chain_graphs = graph_partitions(
        matching["chain_pair_matrix"],
        pair["labels"],
        edge_threshold=float(graph_config["graph_edge_threshold"]),
        spectral_k_min=int(graph_config["spectral_k_min"]),
        spectral_k_max=int(graph_config["spectral_k_max"]),
        spectral_min_eigengap=float(
            graph_config["spectral_min_eigengap"]
        ),
        spectral_min_silhouette=float(
            graph_config["spectral_min_silhouette"]
        ),
        seed=seed,
    )
    triplets = registered_chain_triplets(pair["labels"])
    triplet_scores = direct_common_ball_persistence(
        pair["negative_views"],
        triplets,
        spec=spec,
    )
    cap_statuses = {
        "REFUSE_ENUMERATION_CAP",
        "REFUSE_CANDIDATE_CLOSURE_CAP",
    }
    ready = bool(
        positive["status"] not in cap_statuses
        and chain["status"] not in cap_statuses
    )
    if ready:
        permutation = np.random.default_rng(
            seed + 9_000_001
        ).permutation(pair["labels"])
        permutation_auc = float(roc_auc_score(
            _pair_truth(permutation),
            np.asarray(positive["pair_scores"], dtype=float),
        ))
    else:
        permutation_auc = float("nan")
    matching_scalars = {
        key: value
        for key, value in matching.items()
        if not isinstance(value, np.ndarray)
    }
    return {
        "status": (
            "ESTIMATE_READY"
            if ready
            else "REFUSE_CAP"
        ),
        "positive": positive,
        "chain": chain,
        "matching": {
            **matching_scalars,
            "oracle_pair_matrix_max_error": pair[
                "oracle_pair_matrix_max_error"
            ],
            "oracle_distance_relative_error": pair[
                "oracle_distance_relative_error"
            ],
            "fitted_distance_relative_error": pair[
                "fitted_distance_relative_error"
            ],
            "orthogonal_mapping_error": pair[
                "orthogonal_mapping_error"
            ],
            "opportunity_max_error": int(np.max(np.abs(
                pair["positive_opportunity"].sum(axis=1)
                - pair["negative_opportunity"].sum(axis=1)
            ))),
        },
        "positive_graphs": positive_graphs,
        "chain_graphs": chain_graphs,
        "chain_triplet_min_persistence": float(
            min(triplet_scores.values())
        ),
        "chain_triplet_max_persistence": float(
            max(triplet_scores.values())
        ),
        "chain_all_triplets_pass": bool(
            min(triplet_scores.values())
            >= spec.core_persistence_threshold
        ),
        "permutation_auc": permutation_auc,
    }
