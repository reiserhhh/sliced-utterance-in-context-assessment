"""Topology-margin tools for planted SUICA V8 C2 response surfaces.

The module deliberately separates two questions:

1. whether stable author coordinates can be recovered across halves/observers;
2. whether their population geometry is discrete, ring-like, curve-like, or
   not identifiable.

Topology is computed on an ordinal dissimilarity
``d_star(i, j) = empirical_cdf(d(i, j))``.  This removes scalar distance-CDF
differences while preserving the filtration order used by Vietoris--Rips
persistence.  Raw projected coordinates remain available for moment and
author-matching audits.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
from persim import bottleneck
from ripser import ripser
from scipy.spatial.distance import cdist
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, minimum_spanning_tree
from scipy.sparse.linalg import ArpackNoConvergence, eigsh
from scipy.spatial.distance import pdist, squareform
from scipy.stats import rankdata
from sklearn.cluster import HDBSCAN, KMeans
from sklearn.metrics import roc_auc_score, silhouette_score


TOPOLOGY_CLASSES = (
    "DISCRETE_K",
    "CONTINUOUS_RING",
    "CONTINUOUS_CURVE",
    "TOPOLOGY_NOT_IDENTIFIABLE",
)


@dataclass(frozen=True)
class TopologySpec:
    """Dimensions and observation parameters for one planted world."""

    confirmation_authors: int = 320
    latent_dimensions: int = 3
    operator_dimensions: int = 15
    observers: int = 2
    halves: int = 2
    groups: int = 4
    landmarks: int = 64
    noise_ratio: float = 0.5
    gap_ratio: float = 4.0
    bridge_mass: float = 0.0

    @property
    def discovery_authors(self) -> int:
        return max(12, int(round(0.75 * self.confirmation_authors)))

    @property
    def calibration_authors(self) -> int:
        return max(8, int(round(0.25 * self.confirmation_authors)))

    @property
    def authors(self) -> int:
        return (
            self.discovery_authors
            + self.calibration_authors
            + self.confirmation_authors
        )


def _balanced_counts(total: int, groups: int) -> np.ndarray:
    counts = np.full(groups, total // groups, dtype=int)
    counts[: total % groups] += 1
    return counts


def _tetrahedron() -> np.ndarray:
    centers = np.asarray(
        [
            [1.0, 1.0, 1.0],
            [1.0, -1.0, -1.0],
            [-1.0, 1.0, -1.0],
            [-1.0, -1.0, 1.0],
        ]
    )
    return centers / np.linalg.norm(centers[0])


def _empirical_whiten(
    values: np.ndarray,
    *,
    regularization: float = 1e-8,
) -> np.ndarray:
    """Center and whiten one planted cloud without changing its topology."""
    centered = np.asarray(values, dtype=float) - np.mean(values, axis=0)
    covariance = centered.T @ centered / max(len(centered) - 1, 1)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    inverse_root = eigenvectors @ np.diag(
        1.0 / np.sqrt(np.maximum(eigenvalues, regularization))
    ) @ eigenvectors.T
    result = centered @ inverse_root
    result -= result.mean(axis=0, keepdims=True)
    return result


def _mixture(
    rng: np.random.Generator,
    n: int,
    *,
    gap_ratio: float,
    groups: int,
) -> tuple[np.ndarray, np.ndarray]:
    if groups != 4:
        raise ValueError("the registered mixture uses four tetrahedral groups")
    counts = _balanced_counts(n, groups)
    labels = np.concatenate([
        np.full(count, index, dtype=int)
        for index, count in enumerate(counts)
    ])
    rng.shuffle(labels)
    centers = _tetrahedron() * float(gap_ratio)
    values = centers[labels] + rng.normal(size=(n, 3))
    return values, labels


def _ring(rng: np.random.Generator, n: int) -> tuple[np.ndarray, np.ndarray]:
    angle = rng.uniform(0.0, 2.0 * np.pi, size=n)
    radius = 1.0 + rng.normal(scale=0.035, size=n)
    values = np.column_stack([
        radius * np.cos(angle),
        radius * np.sin(angle),
        rng.normal(scale=0.025, size=n),
    ])
    return values, angle


def _curve(rng: np.random.Generator, n: int) -> tuple[np.ndarray, np.ndarray]:
    t = rng.uniform(-1.0, 1.0, size=n)
    values = np.column_stack([
        t,
        0.75 * (t**2 - 1.0 / 3.0),
        0.45 * t**3,
    ])
    values += rng.normal(scale=0.018, size=values.shape)
    return values, t


def _pearls(
    rng: np.random.Generator,
    n: int,
    *,
    bridge_mass: float,
    groups: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Four ring pearls plus a finite bridge population between them."""
    bridge_n = min(n, int(round(float(bridge_mass) * n)))
    pearl_n = n - bridge_n
    labels = np.concatenate([
        np.repeat(np.arange(groups), _balanced_counts(pearl_n, groups)),
        np.full(bridge_n, groups, dtype=int),
    ])
    rng.shuffle(labels)
    values = np.empty((n, 3), dtype=float)
    centers_angle = 2.0 * np.pi * np.arange(groups) / groups
    for index, label in enumerate(labels):
        if label < groups:
            angle = centers_angle[label] + rng.normal(scale=0.10)
            radius = 1.0 + rng.normal(scale=0.045)
        else:
            angle = rng.uniform(0.0, 2.0 * np.pi)
            radius = 1.0 + rng.normal(scale=0.025)
        values[index] = (
            radius * np.cos(angle),
            radius * np.sin(angle),
            rng.normal(scale=0.025),
        )
    return values, labels


def _heavy_tail(
    rng: np.random.Generator,
    n: int,
) -> tuple[np.ndarray, np.ndarray]:
    values = rng.standard_t(df=3.0, size=(n, 3))
    return values, np.zeros(n, dtype=int)


def _latent_cloud(
    rng: np.random.Generator,
    n: int,
    *,
    world: str,
    gap_ratio: float,
    bridge_mass: float,
    groups: int,
) -> tuple[np.ndarray, np.ndarray]:
    if world in {"separated_mixture", "half_shuffled"}:
        return _mixture(
            rng,
            n,
            gap_ratio=gap_ratio,
            groups=groups,
        )
    if world == "high_overlap_mixture":
        return _mixture(
            rng,
            n,
            gap_ratio=0.65,
            groups=groups,
        )
    if world in {"continuous_ring", "observer_specific"}:
        return _ring(rng, n)
    if world == "continuous_curve":
        return _curve(rng, n)
    if world == "pearls_on_string":
        return _pearls(
            rng,
            n,
            bridge_mass=bridge_mass,
            groups=groups,
        )
    if world in {"null_gaussian", "matching_fail"}:
        return rng.normal(size=(n, 3)), np.zeros(n, dtype=int)
    if world == "heavy_tailed_elliptical":
        return _heavy_tail(rng, n)
    raise ValueError(f"unsupported topology world: {world}")


def _orthogonal_embedding(
    rng: np.random.Generator,
    latent_dimensions: int,
    operator_dimensions: int,
) -> np.ndarray:
    matrix = rng.normal(size=(operator_dimensions, latent_dimensions))
    q, _ = np.linalg.qr(matrix)
    return q[:, :latent_dimensions].T


def simulate_topology_world(
    *,
    seed: int,
    world: str,
    spec: TopologySpec,
) -> dict[str, Any]:
    """Simulate four observed views of a stable planted response surface."""
    rng = np.random.default_rng(seed)
    latent, labels = _latent_cloud(
        rng,
        spec.authors,
        world=world,
        gap_ratio=spec.gap_ratio,
        bridge_mass=spec.bridge_mass,
        groups=spec.groups,
    )
    latent = _empirical_whiten(latent)
    splits = np.asarray(
        ["discovery"] * spec.discovery_authors
        + ["calibration"] * spec.calibration_authors
        + ["confirmation"] * spec.confirmation_authors
    )
    embedding = _orthogonal_embedding(
        rng,
        spec.latent_dimensions,
        spec.operator_dimensions,
    )
    stable = latent @ embedding
    rho = 1.0 / (1.0 + max(float(spec.noise_ratio), 1e-8))
    omega = 0.5
    half_noise = rng.normal(
        size=(spec.authors, spec.halves, spec.operator_dimensions)
    )
    observer_noise = rng.normal(
        size=(
            spec.authors,
            spec.halves,
            spec.observers,
            spec.operator_dimensions,
        )
    )
    views = (
        np.sqrt(rho) * stable[:, None, None, :]
        + np.sqrt(1.0 - rho)
        * (
            np.sqrt(omega) * half_noise[:, :, None, :]
            + np.sqrt(1.0 - omega) * observer_noise
        )
    )

    if world == "half_shuffled":
        for observer in range(spec.observers):
            permutation = rng.permutation(spec.authors)
            views[:, 1, observer] = views[permutation, 1, observer]
    elif world == "observer_specific":
        alternate, _ = _curve(rng, spec.authors)
        alternate = _empirical_whiten(alternate) @ embedding
        for half in range(spec.halves):
            views[:, half, 1] = (
                np.sqrt(rho) * alternate
                + np.sqrt(1.0 - rho)
                * (
                    np.sqrt(omega) * half_noise[:, half]
                    + np.sqrt(1.0 - omega)
                    * observer_noise[:, half, 1]
                )
            )
    elif world == "matching_fail":
        confirmation = splits == "confirmation"
        views[confirmation] *= np.linspace(
            0.35,
            2.5,
            spec.operator_dimensions,
        )
        views[confirmation] += 0.8

    bridge_count = (
        int(round(spec.bridge_mass * spec.confirmation_authors))
        if world == "pearls_on_string"
        else -1
    )
    return {
        "world": world,
        "views": views,
        "splits": splits,
        "latent": latent,
        "labels": labels,
        "rho": rho,
        "noise_ratio": float(spec.noise_ratio),
        "bridge_count": bridge_count,
        "expected_class": expected_topology_class(
            world,
            bridge_count=bridge_count,
        ),
    }


def expected_topology_class(
    world: str,
    *,
    bridge_count: int = 0,
) -> str:
    """Return the registered class or refusal target for a planted world."""
    if world == "separated_mixture":
        return "DISCRETE_K"
    if world == "continuous_ring":
        return "CONTINUOUS_RING"
    if world == "continuous_curve":
        return "CONTINUOUS_CURVE"
    if world == "pearls_on_string" and bridge_count >= 20:
        return "CONTINUOUS_RING"
    return "TOPOLOGY_NOT_IDENTIFIABLE"


def fit_stable_projection(
    views: np.ndarray,
    discovery_mask: np.ndarray,
    *,
    dimensions: int = 3,
) -> dict[str, np.ndarray]:
    """Fit a discovery-only stable subspace from the four-view author mean."""
    values = np.asarray(views, dtype=float)
    author_mean = values.mean(axis=(1, 2))
    discovery = author_mean[np.asarray(discovery_mask, dtype=bool)]
    center = discovery.mean(axis=0)
    _, _, right = np.linalg.svd(discovery - center, full_matrices=False)
    projection = right[:dimensions].T
    projected_discovery = (discovery - center) @ projection
    covariance = (
        projected_discovery.T
        @ projected_discovery
        / max(len(projected_discovery) - 1, 1)
    )
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    whitening = eigenvectors @ np.diag(
        1.0 / np.sqrt(np.maximum(eigenvalues, 1e-8))
    ) @ eigenvectors.T
    return {
        "center": center,
        "projection": projection,
        "whitening": whitening,
    }


def apply_stable_projection(
    views: np.ndarray,
    fitted: dict[str, np.ndarray],
) -> np.ndarray:
    """Apply one frozen discovery projection to all author views."""
    centered = np.asarray(views, dtype=float) - fitted["center"]
    return (
        np.einsum("...p,pk->...k", centered, fitted["projection"])
        @ fitted["whitening"]
    )


def ordinal_distance_matrix(values: np.ndarray) -> np.ndarray:
    """Map pairwise distances to a common empirical-CDF dissimilarity."""
    distances = pdist(np.asarray(values, dtype=float))
    if not np.all(np.isfinite(distances)):
        raise ValueError("non-finite distance encountered")
    ranks = rankdata(distances, method="average")
    quantiles = ranks / (len(ranks) + 1.0)
    matrix = squareform(quantiles)
    np.fill_diagonal(matrix, 0.0)
    return matrix


def farthest_point_landmarks(
    distance: np.ndarray,
    count: int,
) -> np.ndarray:
    """Select deterministic max-min landmarks from a dissimilarity matrix."""
    n = len(distance)
    count = min(max(int(count), 2), n)
    first = int(np.argmin(np.mean(distance, axis=1)))
    selected = [first]
    nearest = distance[first].copy()
    nearest[first] = -np.inf
    while len(selected) < count:
        candidate = int(np.argmax(nearest))
        selected.append(candidate)
        nearest = np.minimum(nearest, distance[candidate])
        nearest[np.asarray(selected, dtype=int)] = -np.inf
    return np.asarray(selected, dtype=int)


def persistence_diagrams(
    values: np.ndarray,
    distance: np.ndarray,
    *,
    landmarks: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute H0 exactly and H1 on density-representative landmarks."""
    h0 = ripser(
        distance,
        distance_matrix=True,
        maxdim=0,
    )["dgms"][0]
    count = min(max(int(landmarks), 2), len(values))
    model = KMeans(
        n_clusters=count,
        random_state=0,
        n_init=5,
        max_iter=200,
    ).fit(np.asarray(values, dtype=float))
    center_distance = cdist(model.cluster_centers_, values)
    selected_list: list[int] = []
    used: set[int] = set()
    for row in center_distance:
        for candidate in np.argsort(row):
            index = int(candidate)
            if index not in used:
                used.add(index)
                selected_list.append(index)
                break
    selected = np.asarray(selected_list, dtype=int)
    h1 = ripser(
        distance[np.ix_(selected, selected)],
        distance_matrix=True,
        maxdim=1,
    )["dgms"][1]
    h0 = h0[np.isfinite(h0[:, 1])]
    h1 = h1[np.isfinite(h1[:, 1])] if len(h1) else h1
    return h0, h1


def _safe_bottleneck(left: np.ndarray, right: np.ndarray) -> float:
    if not len(left) and not len(right):
        return 0.0
    return float(bottleneck(left, right))


def _knn_adjacency(distance: np.ndarray, neighbors: int) -> np.ndarray:
    n = len(distance)
    k = min(max(int(neighbors), 2), n - 1)
    order = np.argsort(distance, axis=1)[:, 1 : k + 1]
    adjacency = np.zeros((n, n), dtype=float)
    rows = np.repeat(np.arange(n), k)
    cols = order.reshape(-1)
    local = distance[rows, cols]
    scale = max(float(np.median(local)), 1e-8)
    adjacency[rows, cols] = np.exp(
        -np.minimum((local / scale) ** 2, 30.0)
    )
    return np.maximum(adjacency, adjacency.T)


def _spectral_graph_features(
    distance: np.ndarray,
    *,
    neighbors: int,
    groups: int,
) -> dict[str, float]:
    adjacency = _knn_adjacency(distance, neighbors)
    degree = adjacency.sum(axis=1)
    safe = np.maximum(degree, 1e-12)
    normalized = (
        np.eye(len(adjacency))
        - adjacency
        / np.sqrt(safe[:, None] * safe[None, :])
    )
    count = min(max(groups + 3, 7), len(adjacency) - 1)
    if len(adjacency) <= 10:
        eigenvalues, eigenvectors = np.linalg.eigh(normalized)
        eigenvalues = eigenvalues[:count]
        eigenvectors = eigenvectors[:, :count]
    else:
        try:
            eigenvalues, eigenvectors = eigsh(
                csr_matrix(normalized),
                k=count,
                which="SM",
                tol=1e-5,
                maxiter=max(5000, 20 * len(adjacency)),
            )
            order = np.argsort(eigenvalues)
            eigenvalues = eigenvalues[order]
            eigenvectors = eigenvectors[:, order]
        except ArpackNoConvergence:
            # Rare disconnected/near-singular graphs can exhaust ARPACK.
            # The graph is at most 640x640 in the registered battery, so a
            # deterministic symmetric fallback is preferable to losing the
            # complete repetition or leaking a non-picklable worker error.
            eigenvalues, eigenvectors = np.linalg.eigh(normalized)
            eigenvalues = eigenvalues[:count]
            eigenvectors = eigenvectors[:, :count]
    eigengap = float(
        eigenvalues[groups] - eigenvalues[groups - 1]
        if len(eigenvalues) > groups
        else 0.0
    )
    cycle_pair_similarity = float(
        1.0
        - abs(eigenvalues[1] - eigenvalues[2])
        / max(abs(eigenvalues[2]), 1e-12)
        if len(eigenvalues) > 2
        else 0.0
    )
    cycle_exit_gap = float(
        (eigenvalues[3] - eigenvalues[2])
        / max(abs(eigenvalues[3]), 1e-12)
        if len(eigenvalues) > 3
        else 0.0
    )

    fiedler = eigenvectors[:, 1] if len(eigenvalues) > 1 else eigenvectors[:, 0]
    order = np.argsort(fiedler)
    total_volume = float(degree.sum())
    cut = 0.0
    volume = 0.0
    best = 1.0
    in_set = np.zeros(len(adjacency), dtype=bool)
    for position, node in enumerate(order[:-1]):
        connections_in = float(adjacency[node, in_set].sum())
        cut += float(degree[node]) - 2.0 * connections_in
        volume += float(degree[node])
        in_set[node] = True
        if position + 1 < max(3, int(0.05 * len(adjacency))):
            continue
        denominator = min(volume, total_volume - volume)
        if denominator > 1e-12:
            best = min(best, max(cut, 0.0) / denominator)
    return {
        "laplacian_k4_eigengap": eigengap,
        "minimum_conductance": float(best),
        "cycle_eigenpair_similarity": cycle_pair_similarity,
        "cycle_exit_gap": cycle_exit_gap,
    }


def _density_tree_features(
    distance: np.ndarray,
    *,
    groups: int,
) -> dict[str, float]:
    n = len(distance)
    minimum_component = max(3, int(np.ceil(0.025 * n)))
    best_groups = 1
    group_levels = 0
    longest = 0
    current = 0
    for quantile in np.linspace(0.01, 0.25, 40):
        threshold = float(np.quantile(distance[np.triu_indices(n, 1)], quantile))
        graph = csr_matrix((distance <= threshold).astype(np.int8))
        _, labels = connected_components(graph, directed=False)
        sizes = np.bincount(labels)
        retained = int(np.sum(sizes >= minimum_component))
        best_groups = max(best_groups, retained)
        if retained == groups:
            group_levels += 1
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return {
        "density_tree_max_branches": float(best_groups),
        "density_tree_k4_levels": float(group_levels),
        "density_tree_k4_longest": float(longest),
    }


def _cluster_features(
    values: np.ndarray,
    distance: np.ndarray,
    *,
    groups: int,
    neighbors: int,
) -> dict[str, float]:
    kmeans = KMeans(
        n_clusters=groups,
        random_state=0,
        n_init=10,
    ).fit(np.asarray(values, dtype=float))
    k4_silhouette = float(
        silhouette_score(
            distance,
            kmeans.labels_,
            metric="precomputed",
        )
    )
    minimum_cluster = max(8, int(np.ceil(0.05 * len(values))))
    density = HDBSCAN(
        min_cluster_size=minimum_cluster,
        min_samples=min(max(int(neighbors // 2), 4), minimum_cluster),
        metric="precomputed",
        copy=True,
    ).fit_predict(distance)
    labels = sorted(set(map(int, density)) - {-1})
    density_clusters = len(labels)
    density_noise = float(np.mean(density < 0))
    density_silhouette = -1.0
    retained = density >= 0
    if density_clusters >= 2 and int(retained.sum()) > density_clusters:
        retained_distance = distance[retained][:, retained].copy()
        np.fill_diagonal(retained_distance, 0.0)
        density_silhouette = float(
            silhouette_score(
                retained_distance,
                density[retained],
                metric="precomputed",
            )
        )
    return {
        "k4_silhouette": k4_silhouette,
        "hdbscan_clusters": float(density_clusters),
        "hdbscan_noise_rate": density_noise,
        "hdbscan_silhouette": density_silhouette,
        "hdbscan_k4_supported": float(
            density_clusters == groups
            and density_noise <= 0.65
            and density_silhouette >= 0.60
        ),
    }


def _local_linearity(
    values: np.ndarray,
    distance: np.ndarray,
    *,
    neighbors: int,
) -> float:
    n = len(values)
    k = min(max(int(neighbors), 5), n - 1)
    neighborhood = np.argsort(distance, axis=1)[:, 1 : k + 1]
    ratios = []
    for index in range(n):
        local = values[neighborhood[index]]
        local -= local.mean(axis=0, keepdims=True)
        singular = np.linalg.svd(local, compute_uv=False)
        energy = singular**2
        ratios.append(float(energy[0] / max(energy.sum(), 1e-12)))
    return float(np.median(ratios))


def topology_features(
    values: np.ndarray,
    *,
    neighbors: int,
    groups: int = 4,
    landmarks: int = 64,
) -> dict[str, Any]:
    """Extract PH, graph, density-tree, and local-geometry features."""
    distance = ordinal_distance_matrix(values)
    h0, h1 = persistence_diagrams(
        np.asarray(values, dtype=float),
        distance,
        landmarks=landmarks,
    )
    deaths = np.sort(h0[:, 1])
    if len(deaths) >= groups + 1:
        h0_gap = float(
            np.log(
                max(deaths[-(groups - 1)], 1e-12)
                / max(deaths[-groups], 1e-12)
            )
        )
    else:
        h0_gap = 0.0
    h1_lifetimes = h1[:, 1] - h1[:, 0] if len(h1) else np.empty(0)
    graph = _spectral_graph_features(
        distance,
        neighbors=neighbors,
        groups=groups,
    )
    density = _density_tree_features(distance, groups=groups)
    cluster = _cluster_features(
        np.asarray(values, dtype=float),
        distance,
        groups=groups,
        neighbors=neighbors,
    )
    return {
        "ordinal_distance": distance,
        "h0_diagram": h0,
        "h1_diagram": h1,
        "h0_k_gap": h0_gap,
        "h0_top3_mean": float(np.mean(deaths[-3:])) if len(deaths) >= 3 else 0.0,
        "h1_max_lifetime": (
            float(h1_lifetimes.max()) if len(h1_lifetimes) else 0.0
        ),
        "h1_total_lifetime": float(h1_lifetimes.sum()),
        "h1_count": float(len(h1_lifetimes)),
        "local_linearity": _local_linearity(
            np.asarray(values, dtype=float),
            distance,
            # k is scaled by the runner to preserve the discovery-calibrated
            # neighborhood fraction as N changes.
            neighbors=neighbors,
        ),
        **graph,
        **density,
        **cluster,
    }


def _cosine_similarity(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    left_norm = left / np.maximum(
        np.linalg.norm(left, axis=1, keepdims=True),
        1e-12,
    )
    right_norm = right / np.maximum(
        np.linalg.norm(right, axis=1, keepdims=True),
        1e-12,
    )
    return left_norm @ right_norm.T


def author_matching_auc(left: np.ndarray, right: np.ndarray) -> float:
    """AUC for true same-author pairs against all different authors."""
    similarity = _cosine_similarity(left, right)
    n = len(left)
    labels = np.eye(n, dtype=int).reshape(-1)
    return float(roc_auc_score(labels, similarity.reshape(-1)))


def neighborhood_jaccard(
    left_distance: np.ndarray,
    right_distance: np.ndarray,
    *,
    neighbors: int,
) -> float:
    """Mean same-author overlap of local neighborhoods across two views."""
    n = len(left_distance)
    k = min(max(int(neighbors), 2), n - 1)
    left = np.argsort(left_distance, axis=1)[:, 1 : k + 1]
    right = np.argsort(right_distance, axis=1)[:, 1 : k + 1]
    scores = []
    for index in range(n):
        a = set(map(int, left[index]))
        b = set(map(int, right[index]))
        scores.append(len(a & b) / max(len(a | b), 1))
    return float(np.mean(scores))


def _view_pairs() -> tuple[tuple[tuple[int, int], tuple[int, int]], ...]:
    return (
        ((0, 0), (1, 0)),
        ((0, 1), (1, 1)),
        ((0, 0), (0, 1)),
        ((1, 0), (1, 1)),
    )


def aggregate_topology_features(
    projected_confirmation: np.ndarray,
    *,
    neighbors: int,
    groups: int,
    landmarks: int,
) -> dict[str, float]:
    """Aggregate four-view topology and cross-view stability metrics."""
    values = np.asarray(projected_confirmation, dtype=float)
    population = topology_features(
        values.mean(axis=(1, 2)),
        neighbors=neighbors,
        groups=groups,
        landmarks=landmarks,
    )
    stability_views = {
        "half_0": values[:, 0].mean(axis=1),
        "half_1": values[:, 1].mean(axis=1),
        "observer_0": values[:, :, 0].mean(axis=1),
        "observer_1": values[:, :, 1].mean(axis=1),
    }
    per_view = {
        key: topology_features(
            view,
            neighbors=neighbors,
            groups=groups,
            landmarks=landmarks,
        )
        for key, view in stability_views.items()
    }
    scalar_keys = (
        "h0_k_gap",
        "h0_top3_mean",
        "h1_max_lifetime",
        "h1_total_lifetime",
        "h1_count",
        "laplacian_k4_eigengap",
        "minimum_conductance",
        "density_tree_max_branches",
        "density_tree_k4_levels",
        "density_tree_k4_longest",
        "local_linearity",
        "cycle_eigenpair_similarity",
        "cycle_exit_gap",
        "k4_silhouette",
        "hdbscan_clusters",
        "hdbscan_noise_rate",
        "hdbscan_silhouette",
        "hdbscan_k4_supported",
    )
    result = {
        key: float(population[key])
        for key in scalar_keys
    }
    h0_bn = []
    h1_bn = []
    jaccard = []
    auc = []
    for left_key, right_key in (
        ("half_0", "half_1"),
        ("observer_0", "observer_1"),
    ):
        left = per_view[left_key]
        right = per_view[right_key]
        # H0 contains one short bar per sampled author.  Exact matching of all
        # short bars is cubic and measures local sample density rather than the
        # registered population split.  Keep the 16 longest bars; the complete
        # diagram is still used above for the exact MST separation statistic.
        left_h0 = left["h0_diagram"][
            np.argsort(left["h0_diagram"][:, 1])[-16:]
        ]
        right_h0 = right["h0_diagram"][
            np.argsort(right["h0_diagram"][:, 1])[-16:]
        ]
        h0_bn.append(_safe_bottleneck(left_h0, right_h0))
        h1_bn.append(_safe_bottleneck(left["h1_diagram"], right["h1_diagram"]))
        jaccard.append(neighborhood_jaccard(
            left["ordinal_distance"],
            right["ordinal_distance"],
            neighbors=neighbors,
        ))
        auc.append(author_matching_auc(
            stability_views[left_key],
            stability_views[right_key],
        ))
    result.update({
        "h0_bottleneck_raw": float(np.median(h0_bn)),
        "h1_bottleneck_raw": float(np.median(h1_bn)),
        "h0_bottleneck": float(
            np.median(h0_bn)
            / max(float(population["h0_top3_mean"]), 0.05)
        ),
        "h1_bottleneck": float(
            np.median(h1_bn)
            / max(float(population["h1_max_lifetime"]), 0.05)
        ),
        "neighborhood_jaccard": float(np.median(jaccard)),
        "author_matching_auc": float(np.median(auc)),
    })
    return result


def matching_diagnostics(
    projected: np.ndarray,
    discovery_mask: np.ndarray,
    confirmation_mask: np.ndarray,
    *,
    maximum_mean_abs: float,
    maximum_covariance_error: float,
    maximum_auc_gap: float,
) -> dict[str, Any]:
    """Check that confirmation geometry remains on the discovery scale."""
    author_mean = projected.mean(axis=(1, 2))
    discovery = author_mean[discovery_mask]
    confirmation = author_mean[confirmation_mask]
    mean_abs = float(np.max(np.abs(confirmation.mean(axis=0))))
    covariance_discovery = np.cov(discovery, rowvar=False)
    covariance_confirmation = np.cov(confirmation, rowvar=False)
    covariance_error = float(
        np.linalg.norm(covariance_confirmation - covariance_discovery)
        / max(np.linalg.norm(covariance_discovery), 1e-12)
    )
    discovery_auc = author_matching_auc(
        projected[discovery_mask, 0, 0],
        projected[discovery_mask, 1, 0],
    )
    confirmation_auc = author_matching_auc(
        projected[confirmation_mask, 0, 0],
        projected[confirmation_mask, 1, 0],
    )
    auc_gap = abs(discovery_auc - confirmation_auc)
    passed = bool(
        mean_abs <= maximum_mean_abs
        and covariance_error <= maximum_covariance_error
        and auc_gap <= maximum_auc_gap
    )
    return {
        "matching_pass": passed,
        "matching_mean_abs": mean_abs,
        "matching_covariance_error": covariance_error,
        "discovery_author_auc": discovery_auc,
        "confirmation_author_auc": confirmation_auc,
        "matching_auc_gap": float(auc_gap),
        "ordinal_distance_cdf": "EXACT_EMPIRICAL_UNIFORM_BY_CONSTRUCTION",
    }


def calibrate_thresholds(
    feature_rows: Iterable[dict[str, Any]],
) -> dict[str, float]:
    """Calibrate conservative one-sided thresholds on discovery worlds only."""
    rows = list(feature_rows)
    controls = [
        row for row in rows
        if row["world"] in {
            "null_gaussian",
            "heavy_tailed_elliptical",
            "high_overlap_mixture",
        }
    ]
    ring_rows = [
        row for row in rows if row["world"] == "continuous_ring"
    ]
    curve_rows = [
        row for row in rows if row["world"] == "continuous_curve"
    ]
    h1_controls = [
        row for row in rows
        if row["world"] in {
            "separated_mixture",
            "high_overlap_mixture",
            "null_gaussian",
            "heavy_tailed_elliptical",
        }
    ]
    stable = [
        row for row in rows
        if row["world"] in {
            "separated_mixture",
            "continuous_ring",
            "continuous_curve",
        }
    ]
    non_discrete = [
        row for row in rows if row["world"] != "separated_mixture"
    ]
    non_ring = [
        row for row in rows if row["world"] != "continuous_ring"
    ]
    non_curve = [
        row for row in rows if row["world"] != "continuous_curve"
    ]

    def percentile(
        selected: list[dict[str, Any]],
        key: str,
        q: float,
    ) -> float:
        values = np.asarray(
            [float(row[key]) for row in selected],
            dtype=float,
        )
        return float(np.quantile(values[np.isfinite(values)], q))

    curve_h1_ceiling = percentile(
        curve_rows,
        "h1_max_lifetime",
        0.99,
    )
    ring_h1_floor = max(
        percentile(h1_controls, "h1_max_lifetime", 0.99),
        percentile(ring_rows, "h1_max_lifetime", 0.01),
    )
    return {
        "h0_k_gap": percentile(non_discrete, "h0_k_gap", 0.99),
        "laplacian_k4_eigengap": percentile(
            non_discrete,
            "laplacian_k4_eigengap",
            0.99,
        ),
        "k4_silhouette": percentile(
            non_discrete,
            "k4_silhouette",
            0.99,
        ),
        "maximum_conductance": percentile(
            non_discrete,
            "minimum_conductance",
            0.01,
        ),
        "density_tree_k4_longest": percentile(
            non_discrete,
            "density_tree_k4_longest",
            0.99,
        ),
        "h1_max_lifetime": percentile(
            non_ring,
            "h1_max_lifetime",
            0.975,
        ),
        "curve_h1_ceiling": curve_h1_ceiling,
        "ring_h1_floor": ring_h1_floor,
        "h1_open_set_gap": ring_h1_floor - curve_h1_ceiling,
        "cycle_eigenpair_similarity": percentile(
            [
                row for row in non_ring
                if row["world"] != "separated_mixture"
            ],
            "cycle_eigenpair_similarity",
            0.975,
        ),
        "local_linearity": percentile(
            [
                row for row in non_curve
                if row["world"] not in {
                    "separated_mixture",
                    "continuous_ring",
                }
            ],
            "local_linearity",
            0.99,
        ),
        "manifold_k4_silhouette": percentile(
            [
                row for row in rows
                if row["world"] in {
                    "null_gaussian",
                    "heavy_tailed_elliptical",
                    "high_overlap_mixture",
                }
            ],
            "k4_silhouette",
            0.99,
        ),
        "maximum_h0_bottleneck": percentile(
            stable,
            "h0_bottleneck",
            0.99,
        ),
        "maximum_h1_bottleneck": percentile(
            stable,
            "h1_bottleneck",
            0.99,
        ),
        "minimum_neighborhood_jaccard": percentile(
            stable,
            "neighborhood_jaccard",
            0.01,
        ),
        "minimum_author_matching_auc": max(
            0.5,
            percentile(stable, "author_matching_auc", 0.01),
        ),
        "control_h0_99": percentile(controls, "h0_k_gap", 0.99),
        "control_h1_99": percentile(
            controls,
            "h1_max_lifetime",
            0.99,
        ),
    }


def classify_topology(
    features: dict[str, float],
    thresholds: dict[str, float],
    *,
    matching_pass: bool,
    bridge_count: int = 0,
) -> dict[str, Any]:
    """Apply the frozen multi-evidence topology rule with explicit refusal."""
    base_stable = bool(
        features["h0_bottleneck"] <= thresholds["maximum_h0_bottleneck"]
        and features["neighborhood_jaccard"]
        >= thresholds["minimum_neighborhood_jaccard"]
    )
    votes = {
        "h0_gap": features["h0_k_gap"] > thresholds["h0_k_gap"],
        "eigengap": (
            features["laplacian_k4_eigengap"]
            > thresholds["laplacian_k4_eigengap"]
        ),
        "conductance": (
            features["minimum_conductance"]
            < thresholds["maximum_conductance"]
        ),
        "density_tree": (
            features["density_tree_k4_longest"]
            > thresholds["density_tree_k4_longest"]
        ),
        "k4_silhouette": (
            features["k4_silhouette"]
            > thresholds["k4_silhouette"]
        ),
        "hdbscan": bool(features["hdbscan_k4_supported"] >= 0.5),
    }
    discrete_votes = int(sum(votes.values()))
    ring_votes = int(
        features["h1_max_lifetime"] > thresholds["h1_max_lifetime"]
    ) + int(
        features["cycle_eigenpair_similarity"]
        > thresholds["cycle_eigenpair_similarity"]
    )
    # H1 is the registered ring evidence.  The spectral eigenpair is retained
    # as a mechanism diagnostic but is not mandatory because near-equal tiny
    # eigenvalues make its ratio unstable under null clouds.
    ring = bool(
        features["h1_max_lifetime"] >= thresholds["ring_h1_floor"]
    )
    curve = bool(
        features["local_linearity"] > thresholds["local_linearity"]
        and features["h1_max_lifetime"]
        <= thresholds["curve_h1_ceiling"]
    )
    h1_stable = bool(
        features["h1_bottleneck"] <= thresholds["maximum_h1_bottleneck"]
    )
    stable = bool(base_stable and (not ring or h1_stable))
    reasons: list[str] = []
    if not matching_pass:
        reasons.append("MOMENT_OR_AUC_MATCHING_FAILED")
    if not stable:
        reasons.append("CROSS_VIEW_STABILITY_FAILED")
    if 0 <= bridge_count < 20:
        reasons.append("BRIDGE_SUPPORT_BELOW_IDENTIFICATION_MINIMUM")
    if reasons:
        label = "TOPOLOGY_NOT_IDENTIFIABLE"
    elif (
        votes["k4_silhouette"]
        and discrete_votes >= 3
        and not ring
    ):
        label = "DISCRETE_K"
    elif ring and discrete_votes < 3:
        label = "CONTINUOUS_RING"
    elif curve and not ring and discrete_votes < 3:
        label = "CONTINUOUS_CURVE"
    else:
        label = "TOPOLOGY_NOT_IDENTIFIABLE"
        reasons.append("EVIDENCE_CONFLICT_OR_BELOW_MARGIN")
    return {
        "predicted_class": label,
        "stable": stable,
        "base_stable": base_stable,
        "h1_stable": h1_stable,
        "discrete_votes": discrete_votes,
        "ring_vote": ring,
        "ring_votes": ring_votes,
        "curve_vote": curve,
        "h1_open_set_region": (
            "RING"
            if features["h1_max_lifetime"] >= thresholds["ring_h1_floor"]
            else "CURVE_COMPATIBLE"
            if features["h1_max_lifetime"] <= thresholds["curve_h1_ceiling"]
            else "GRAY_REFUSAL"
        ),
        "votes": votes,
        "refusal_reasons": reasons,
    }


def analyze_topology_world(
    world: dict[str, Any],
    *,
    neighbors: int,
    thresholds: dict[str, float] | None,
    groups: int,
    landmarks: int,
    matching_gates: dict[str, float],
) -> dict[str, Any]:
    """Project, audit, feature-extract, and optionally classify one world."""
    splits = np.asarray(world["splits"])
    discovery = splits == "discovery"
    confirmation = splits == "confirmation"
    fitted = fit_stable_projection(world["views"], discovery)
    projected = apply_stable_projection(world["views"], fitted)
    matching = matching_diagnostics(
        projected,
        discovery,
        confirmation,
        maximum_mean_abs=float(matching_gates["maximum_matching_mean_abs"]),
        maximum_covariance_error=float(
            matching_gates["maximum_matching_covariance_error"]
        ),
        maximum_auc_gap=float(matching_gates["maximum_matching_auc_gap"]),
    )
    features = aggregate_topology_features(
        projected[confirmation],
        neighbors=neighbors,
        groups=groups,
        landmarks=landmarks,
    )
    result: dict[str, Any] = {
        "world": world["world"],
        "expected_class": world["expected_class"],
        "bridge_count": int(world["bridge_count"]),
        **matching,
        **features,
    }
    if thresholds is not None:
        result.update(classify_topology(
            features,
            thresholds,
            matching_pass=bool(matching["matching_pass"]),
            bridge_count=int(world["bridge_count"]),
        ))
    return result
