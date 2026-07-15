"""Text-blind geometry diagnostics for paired SUICA author residuals.

The public functions in this module accept only paired numeric matrices.  Given
an early and late representation of the same authors, they quantify whether the
*relations among authors* reproduce across the two views.  They deliberately do
not inspect feature names, tokens, labels, or raw text.

The relevant object is a quotient geometry: a coordinate system may rotate or
rescale, while pairwise relations, neighbourhoods, and kernel geometry remain
testable.  This makes the module useful when no stable, nameable factor axis is
available.
"""
from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from scipy.stats import rankdata


def _validate_aligned_rows(left: np.ndarray, right: np.ndarray, *, min_rows: int = 12,
                           require_same_features: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """Validate finite matrices whose rows are aligned by the same authors."""
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    if left.ndim != 2 or right.ndim != 2:
        raise ValueError("aligned matrices must be two dimensional")
    if len(left) != len(right):
        raise ValueError("aligned matrices must have the same number of rows")
    if require_same_features and left.shape[1] != right.shape[1]:
        raise ValueError("paired matrices must have the same number of features")
    if len(left) < min_rows:
        raise ValueError(f"at least {min_rows} paired authors are required")
    if left.shape[1] < 1 or right.shape[1] < 1:
        raise ValueError("at least one feature is required")
    if not np.isfinite(left).all() or not np.isfinite(right).all():
        raise ValueError("geometry diagnostics require finite matrices")
    return left, right


def _validate_paired(early: np.ndarray, late: np.ndarray, *, min_rows: int = 12) -> tuple[np.ndarray, np.ndarray]:
    """Validate paired author-by-feature matrices with the same coordinates."""
    early = np.asarray(early, dtype=float)
    late = np.asarray(late, dtype=float)
    if early.ndim != 2 or late.ndim != 2:
        raise ValueError("early and late matrices must be two dimensional")
    if early.shape != late.shape:
        raise ValueError("early and late matrices must have identical shapes")
    return _validate_aligned_rows(early, late, min_rows=min_rows, require_same_features=True)


def pairwise_distances(values: np.ndarray) -> np.ndarray:
    """Return a Euclidean distance matrix without materializing a 3-D tensor."""
    values = np.asarray(values, dtype=float)
    squared_norm = np.sum(values * values, axis=1, keepdims=True)
    squared = squared_norm + squared_norm.T - 2.0 * (values @ values.T)
    return np.sqrt(np.maximum(squared, 0.0))


def centered_gram(values: np.ndarray) -> np.ndarray:
    """Return the doubly centered linear Gram matrix for a numeric point cloud."""
    gram = np.asarray(values, dtype=float) @ np.asarray(values, dtype=float).T
    return gram - gram.mean(axis=0, keepdims=True) - gram.mean(axis=1, keepdims=True) + gram.mean()


def rbf_centered_gram(values: np.ndarray) -> np.ndarray:
    """Return a median-bandwidth RBF Gram matrix, centered across authors."""
    distances = pairwise_distances(values)
    upper = distances[np.triu_indices(len(distances), k=1)]
    positive = upper[upper > 1e-12]
    bandwidth = float(np.median(positive)) if len(positive) else 1.0
    kernel = np.exp(-0.5 * (distances / max(bandwidth, 1e-12)) ** 2)
    return kernel - kernel.mean(axis=0, keepdims=True) - kernel.mean(axis=1, keepdims=True) + kernel.mean()


def linear_cka_from_grams(left: np.ndarray, right: np.ndarray) -> float:
    """Compute centered kernel alignment from already centered Gram matrices."""
    denominator = np.linalg.norm(left, ord="fro") * np.linalg.norm(right, ord="fro")
    if denominator <= 1e-12:
        return float("nan")
    return float(np.sum(left * right) / denominator)


def _symmetric_distance_ranks(distances: np.ndarray) -> np.ndarray:
    """Rank upper-triangle distances and mirror the ranks into a square matrix."""
    n = len(distances)
    upper = np.triu_indices(n, k=1)
    ranks = np.zeros_like(distances, dtype=float)
    ranks[upper] = rankdata(distances[upper], method="average")
    ranks[(upper[1], upper[0])] = ranks[upper]
    return ranks


def distance_spearman_from_ranks(left_ranks: np.ndarray, right_ranks: np.ndarray) -> float:
    """Correlate the rank order of all author-pair distances."""
    n = len(left_ranks)
    upper = np.triu_indices(n, k=1)
    left = left_ranks[upper]
    right = right_ranks[upper]
    left = left - left.mean()
    right = right - right.mean()
    denominator = np.linalg.norm(left) * np.linalg.norm(right)
    if denominator <= 1e-12:
        return float("nan")
    return float(np.dot(left, right) / denominator)


def top_k_neighbours(distances: np.ndarray, k: int) -> np.ndarray:
    """Return ordered nearest-neighbour indices, excluding each point itself."""
    n = len(distances)
    if not 1 <= k < n:
        raise ValueError("k must be between 1 and n - 1")
    work = np.asarray(distances, dtype=float).copy()
    np.fill_diagonal(work, np.inf)
    candidate = np.argpartition(work, kth=k - 1, axis=1)[:, :k]
    candidate_distances = np.take_along_axis(work, candidate, axis=1)
    order = np.argsort(candidate_distances, axis=1)
    return np.take_along_axis(candidate, order, axis=1)


def neighbour_lookup(neighbours: np.ndarray, n: int | None = None) -> np.ndarray:
    """Build a boolean row-wise membership table for fixed neighbourhoods."""
    n = int(n if n is not None else len(neighbours))
    lookup = np.zeros((n, n), dtype=bool)
    lookup[np.arange(n)[:, None], neighbours] = True
    return lookup


def neighbour_jaccard_from_lookup(lookup: np.ndarray, candidate: np.ndarray, *, k: int) -> float:
    """Return mean row-wise Jaccard overlap using a precomputed membership table."""
    overlap = lookup[np.arange(len(lookup))[:, None], candidate].sum(axis=1)
    return float(np.mean(overlap / (2 * k - overlap)))


def neighbour_jaccard(left: np.ndarray, right: np.ndarray) -> float:
    """Mean author-wise Jaccard overlap between two equal-width neighbour arrays."""
    if left.shape != right.shape:
        raise ValueError("neighbour arrays must have identical shapes")
    width = left.shape[1]
    overlaps = [len(set(a).intersection(b)) / width for a, b in zip(left, right, strict=True)]
    return float(np.mean(overlaps))


def aligned_geometry_statistics(left: np.ndarray, right: np.ndarray, *, neighbourhood_k: int = 10) -> dict[str, float]:
    """Compare numeric geometry across representations with aligned author rows.

    Feature dimensions may differ. The comparison is therefore made only through
    author-by-author kernels, pairwise distance order, and neighbour graphs.
    """
    left, right = _validate_aligned_rows(left, right)
    k = min(neighbourhood_k, len(left) - 1)
    left_distance, right_distance = pairwise_distances(left), pairwise_distances(right)
    left_neighbours, right_neighbours = top_k_neighbours(left_distance, k), top_k_neighbours(right_distance, k)
    return {
        "linear_cka": linear_cka_from_grams(centered_gram(left), centered_gram(right)),
        "rbf_cka": linear_cka_from_grams(rbf_centered_gram(left), rbf_centered_gram(right)),
        "distance_spearman": distance_spearman_from_ranks(
            _symmetric_distance_ranks(left_distance), _symmetric_distance_ranks(right_distance)
        ),
        "neighbour_jaccard": neighbour_jaccard_from_lookup(
            neighbour_lookup(left_neighbours), right_neighbours, k=k
        ),
        "n_neighbours": float(k),
    }


def aligned_geometry_permutation_test(
    left: np.ndarray,
    right: np.ndarray,
    *,
    neighbourhood_k: int = 10,
    iterations: int = 999,
    seed: int = 0,
) -> tuple[dict[str, float], list[dict[str, float]]]:
    """Test cross-representation geometry against a row-linkage permutation null."""
    left, right = _validate_aligned_rows(left, right)
    if iterations < 99:
        raise ValueError("at least 99 linkage permutations are required")
    n = len(left)
    k = min(neighbourhood_k, n - 1)
    left_distance, right_distance = pairwise_distances(left), pairwise_distances(right)
    left_ranks, right_ranks = _symmetric_distance_ranks(left_distance), _symmetric_distance_ranks(right_distance)
    left_linear, right_linear = centered_gram(left), centered_gram(right)
    left_rbf, right_rbf = rbf_centered_gram(left), rbf_centered_gram(right)
    left_neighbours, right_neighbours = top_k_neighbours(left_distance, k), top_k_neighbours(right_distance, k)
    left_lookup = neighbour_lookup(left_neighbours)
    observed = {
        "linear_cka": linear_cka_from_grams(left_linear, right_linear),
        "rbf_cka": linear_cka_from_grams(left_rbf, right_rbf),
        "distance_spearman": distance_spearman_from_ranks(left_ranks, right_ranks),
        "neighbour_jaccard": neighbour_jaccard_from_lookup(left_lookup, right_neighbours, k=k),
    }
    rng = np.random.default_rng(seed)
    base = np.arange(n)
    null_rows: list[dict[str, float]] = []
    for draw in range(iterations):
        permutation = rng.permutation(n)
        if np.array_equal(permutation, base):
            permutation = np.roll(permutation, 1)
        inverse = np.empty(n, dtype=int)
        inverse[permutation] = base
        permuted_neighbours = inverse[right_neighbours[permutation]]
        null_rows.append({
            "draw": float(draw),
            "linear_cka": linear_cka_from_grams(left_linear, right_linear[np.ix_(permutation, permutation)]),
            "rbf_cka": linear_cka_from_grams(left_rbf, right_rbf[np.ix_(permutation, permutation)]),
            "distance_spearman": distance_spearman_from_ranks(
                left_ranks, right_ranks[np.ix_(permutation, permutation)]
            ),
            "neighbour_jaccard": neighbour_jaccard_from_lookup(left_lookup, permuted_neighbours, k=k),
        })
    for metric, value in list(observed.items()):
        null = np.asarray([row[metric] for row in null_rows], dtype=float)
        observed[f"{metric}_null_mean"] = float(np.mean(null))
        observed[f"{metric}_null_q95"] = float(np.quantile(null, 0.95))
        observed[f"{metric}_permutation_p"] = float((1 + np.sum(null >= value)) / (iterations + 1))
    return observed, null_rows


def effective_rank(values: np.ndarray) -> float:
    """Entropy effective rank of a centered numeric cloud's covariance spectrum."""
    centered = np.asarray(values, dtype=float) - np.mean(values, axis=0, keepdims=True)
    eigenvalues = np.linalg.svd(centered, compute_uv=False) ** 2
    eigenvalues = eigenvalues[eigenvalues > 1e-12]
    if not len(eigenvalues):
        return 0.0
    weights = eigenvalues / eigenvalues.sum()
    return float(np.exp(-np.sum(weights * np.log(weights))))


def intrinsic_dimension(values: np.ndarray, *, k: int = 10) -> float:
    """Estimate local intrinsic dimension with the Levina--Bickel kNN estimator.

    This is a geometric descriptive statistic, not a claim that the source has
    a literal Euclidean latent manifold.  Duplicate or degenerate neighbourhoods
    are omitted rather than assigned an arbitrary dimension.
    """
    values = np.asarray(values, dtype=float)
    n = len(values)
    if n <= k:
        raise ValueError("intrinsic dimension needs more rows than k")
    distances = pairwise_distances(values)
    np.fill_diagonal(distances, np.inf)
    nearest = np.partition(distances, kth=k - 1, axis=1)[:, :k]
    nearest.sort(axis=1)
    radius = nearest[:, -1]
    inner = nearest[:, :-1]
    valid = (radius > 1e-12) & np.all(inner > 1e-12, axis=1)
    if not valid.any():
        return float("nan")
    log_ratio = np.log(radius[valid, None] / inner[valid])
    local_inverse = np.mean(log_ratio, axis=1)
    local = 1.0 / local_inverse[local_inverse > 1e-12]
    # Finite-sample kNN estimates can overshoot the observed ambient space.
    # The clipped value is the admissible geometric dimension of this embedding.
    return float(min(np.median(local), values.shape[1])) if len(local) else float("nan")


def _spectrum(values: np.ndarray) -> np.ndarray:
    centered = np.asarray(values, dtype=float) - np.mean(values, axis=0, keepdims=True)
    eigenvalues = np.linalg.svd(centered, compute_uv=False) ** 2
    if eigenvalues.sum() <= 1e-12:
        return np.zeros_like(eigenvalues)
    return eigenvalues / eigenvalues.sum()


def spectrum_cosine(left: np.ndarray, right: np.ndarray) -> float:
    """Compare normalized covariance spectra, ignoring axis orientation."""
    a, b = _spectrum(left), _spectrum(right)
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denominator) if denominator > 1e-12 else float("nan")


def geometry_statistics(early: np.ndarray, late: np.ndarray, *, neighbourhood_k: int = 10) -> dict[str, float]:
    """Compute global, local, and spectral correspondence of numeric geometry."""
    early, late = _validate_paired(early, late)
    k = min(neighbourhood_k, len(early) - 1)
    early_distance = pairwise_distances(early)
    late_distance = pairwise_distances(late)
    early_ranks = _symmetric_distance_ranks(early_distance)
    late_ranks = _symmetric_distance_ranks(late_distance)
    early_neighbours = top_k_neighbours(early_distance, k)
    late_neighbours = top_k_neighbours(late_distance, k)
    return {
        "linear_cka": linear_cka_from_grams(centered_gram(early), centered_gram(late)),
        "distance_spearman": distance_spearman_from_ranks(early_ranks, late_ranks),
        "neighbour_jaccard": neighbour_jaccard(early_neighbours, late_neighbours),
        "effective_rank_early": effective_rank(early),
        "effective_rank_late": effective_rank(late),
        "intrinsic_dimension_early": intrinsic_dimension(early, k=min(10, len(early) - 1)),
        "intrinsic_dimension_late": intrinsic_dimension(late, k=min(10, len(late) - 1)),
        "spectrum_cosine": spectrum_cosine(early, late),
        "n_neighbours": float(k),
    }


def correspondence_permutation_test(
    early: np.ndarray,
    late: np.ndarray,
    *,
    neighbourhood_k: int = 10,
    iterations: int = 199,
    seed: int = 0,
) -> tuple[dict[str, float], list[dict[str, float]]]:
    """Test paired geometry against a late-author linkage permutation null.

    The null preserves both individual point clouds exactly.  It destroys only
    which late author belongs to which early author, so a small p-value supports
    reproducible *relational geometry*, not a psychological interpretation.
    """
    early, late = _validate_paired(early, late)
    if iterations < 19:
        raise ValueError("at least 19 linkage permutations are required")
    n = len(early)
    k = min(neighbourhood_k, n - 1)
    early_distance = pairwise_distances(early)
    late_distance = pairwise_distances(late)
    early_ranks = _symmetric_distance_ranks(early_distance)
    late_ranks = _symmetric_distance_ranks(late_distance)
    early_gram = centered_gram(early)
    late_gram = centered_gram(late)
    early_neighbours = top_k_neighbours(early_distance, k)
    late_neighbours = top_k_neighbours(late_distance, k)

    observed = {
        "linear_cka": linear_cka_from_grams(early_gram, late_gram),
        "distance_spearman": distance_spearman_from_ranks(early_ranks, late_ranks),
        "neighbour_jaccard": neighbour_jaccard(early_neighbours, late_neighbours),
    }
    rng = np.random.default_rng(seed)
    null_rows: list[dict[str, float]] = []
    base = np.arange(n)
    for draw in range(iterations):
        permutation = rng.permutation(n)
        if np.array_equal(permutation, base):
            permutation = np.roll(permutation, 1)
        inverse = np.empty(n, dtype=int)
        inverse[permutation] = base
        late_neighbours_permuted = inverse[late_neighbours[permutation]]
        late_gram_permuted = late_gram[np.ix_(permutation, permutation)]
        late_ranks_permuted = late_ranks[np.ix_(permutation, permutation)]
        null_rows.append({
            "draw": float(draw),
            "linear_cka": linear_cka_from_grams(early_gram, late_gram_permuted),
            "distance_spearman": distance_spearman_from_ranks(early_ranks, late_ranks_permuted),
            "neighbour_jaccard": neighbour_jaccard(early_neighbours, late_neighbours_permuted),
        })

    for metric, value in list(observed.items()):
        null = np.array([row[metric] for row in null_rows], dtype=float)
        observed[f"{metric}_null_mean"] = float(np.mean(null))
        observed[f"{metric}_null_q95"] = float(np.quantile(null, 0.95))
        observed[f"{metric}_permutation_p"] = float((1 + np.sum(null >= value)) / (iterations + 1))
    return observed, null_rows


def subsample_stability(
    early: np.ndarray,
    late: np.ndarray,
    *,
    neighbourhood_k: int = 10,
    iterations: int = 64,
    max_rows: int = 384,
    seed: int = 0,
) -> dict[str, float]:
    """Return subsample stability intervals for geometry statistics.

    These are deliberately labelled as *subsample intervals*, not confidence
    intervals: pairwise distances are dependent and ordinary iid bootstrap CIs
    would overstate certainty.
    """
    early, late = _validate_paired(early, late)
    if iterations < 8:
        raise ValueError("at least eight subsamples are required")
    size = min(len(early), max(max_rows, neighbourhood_k + 2))
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(iterations):
        index = rng.choice(len(early), size=size, replace=False)
        rows.append(geometry_statistics(early[index], late[index], neighbourhood_k=neighbourhood_k))
    result: dict[str, float] = {"subsample_rows": float(size), "subsample_iterations": float(iterations)}
    for metric in ("linear_cka", "distance_spearman", "neighbour_jaccard", "spectrum_cosine"):
        values = np.array([row[metric] for row in rows], dtype=float)
        result[f"{metric}_subsample_lo"] = float(np.nanquantile(values, 0.025))
        result[f"{metric}_subsample_hi"] = float(np.nanquantile(values, 0.975))
    return result


def geometry_audit(
    early: np.ndarray,
    late: np.ndarray,
    *,
    neighbourhood_k: int = 10,
    permutation_iterations: int = 199,
    subsample_iterations: int = 64,
    subsample_max_rows: int = 384,
    seed: int = 0,
) -> tuple[dict[str, float], list[dict[str, float]]]:
    """Run the complete numeric-only geometry audit for one paired object."""
    summary = geometry_statistics(early, late, neighbourhood_k=neighbourhood_k)
    permutation, null_rows = correspondence_permutation_test(
        early, late, neighbourhood_k=neighbourhood_k,
        iterations=permutation_iterations, seed=seed,
    )
    stability = subsample_stability(
        early, late, neighbourhood_k=neighbourhood_k,
        iterations=subsample_iterations, max_rows=subsample_max_rows, seed=seed + 1,
    )
    return {**summary, **permutation, **stability}, null_rows


def geometry_status(metrics: dict[str, float], *, alpha: float = 0.05) -> str:
    """Give a conservative linkage status without naming a construct.

    This intentionally does not call a statistically positive result a strong
    replication: no substantive geometry margin has been preregistered yet.
    """
    keys: Iterable[str] = ("linear_cka", "distance_spearman", "neighbour_jaccard")
    supported = [metrics.get(f"{key}_bonferroni_p", metrics.get(f"{key}_permutation_p", 1.0)) < alpha
                 for key in keys]
    if all(supported):
        return "LINKAGE_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN"
    if any(supported):
        return "PARTIAL_LINKAGE_GEOMETRY_ONLY"
    return "NO_LINKAGE_GEOMETRY_DETECTED"
