"""Persistent incidence multiplicity for SUICA V8 planted populations.

This module estimates condition-indexed common-ball hyperedges. It keeps raw
intersection multiplicity separate from pair-specific persistence so a
population-wide condition anchor cannot masquerade as latent co-membership.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist, squareform
from scipy.stats import spearmanr


@dataclass(frozen=True)
class MultiplicitySpec:
    """Observation design for one planted population."""

    authors: int = 24
    groups: int = 4
    conditions: int = 65
    halves: int = 2
    observers: int = 2
    noise_sd: float = 0.03
    ridge_alpha: float = 0.001
    epsilon_grid: tuple[float, ...] = (1.0, 1.5, 2.0, 3.0)


WORLD_META: dict[str, dict[str, Any]] = {
    "group_regional_affine_2d": {
        "kind": "clear_group", "ambient": 2, "relation": "REGIONAL",
    },
    "group_tangent_quadratic_2d": {
        "kind": "clear_group", "ambient": 2, "relation": "TANGENT",
    },
    "group_regional_affine_3d": {
        "kind": "clear_group", "ambient": 3, "relation": "REGIONAL",
    },
    "common_anchor_plus_groups_2d": {
        "kind": "clear_group", "ambient": 2, "relation": "REGIONAL",
    },
    "group_isolated_transverse_2d": {
        "kind": "boundary", "ambient": 2, "relation": "TRANSVERSE_ISOLATED",
    },
    "global_common_anchor_2d": {
        "kind": "null", "ambient": 2, "relation": "GLOBAL_ANCHOR",
    },
    "random_crossings_2d": {
        "kind": "null", "ambient": 2, "relation": "RANDOM_CROSSING",
    },
    "pair_map_equivalence_2d": {
        "kind": "null", "ambient": 2, "relation": "PAIR_ONLY",
    },
    "continuous_ring_2d": {
        "kind": "null", "ambient": 2, "relation": "CONTINUOUS",
    },
    "projection_crossing_3d": {
        "kind": "null", "ambient": 3, "relation": "PROJECTION_ONLY",
    },
    "observer_artifact_2d": {
        "kind": "attack", "ambient": 2, "relation": "OBSERVER_ARTIFACT",
    },
    "half_artifact_2d": {
        "kind": "attack", "ambient": 2, "relation": "HALF_ARTIFACT",
    },
    "condition_permutation_2d": {
        "kind": "attack", "ambient": 2, "relation": "CONDITION_PERMUTATION",
    },
    "partial_support_2d": {
        "kind": "attack", "ambient": 2, "relation": "PARTIAL_SUPPORT",
    },
    "nonlinear_rbf_group_2d": {
        "kind": "challenge_group", "ambient": 2, "relation": "REGIONAL",
    },
    "heteroskedastic_group_3d": {
        "kind": "challenge_group", "ambient": 3, "relation": "REGIONAL",
    },
}


def _balanced_labels(
    authors: int,
    groups: int,
    rng: np.random.Generator,
) -> np.ndarray:
    labels = np.arange(authors, dtype=int) % groups
    return labels[rng.permutation(authors)]


def _unit(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm <= 1e-12:
        return np.zeros_like(vector)
    return vector / norm


def _group_geometry(groups: int, ambient: int) -> tuple[np.ndarray, np.ndarray]:
    angles = 2.0 * np.pi * np.arange(groups) / groups
    centers = np.zeros((groups, ambient), dtype=float)
    directions = np.zeros_like(centers)
    centers[:, 0] = 1.25 * np.cos(angles)
    centers[:, 1] = 1.25 * np.sin(angles)
    directions[:, 0] = np.cos(angles + 0.65)
    directions[:, 1] = np.sin(angles + 0.65)
    if ambient == 3:
        centers[:, 2] = np.linspace(-0.65, 0.65, groups)
        directions[:, 2] = np.where(np.arange(groups) % 2, 0.35, -0.35)
        directions = np.asarray([_unit(item) for item in directions])
    return centers, directions


def _common_curve(t: np.ndarray, ambient: int) -> np.ndarray:
    result = np.zeros((len(t), ambient), dtype=float)
    result[:, 0] = 0.18 * t
    result[:, 1] = 0.10 * np.sin(np.pi * t)
    if ambient == 3:
        result[:, 2] = 0.08 * np.cos(np.pi * t)
    return result


def _group_truth(
    *,
    world: str,
    t: np.ndarray,
    labels: np.ndarray,
    ambient: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate oracle trajectories and registered group anchor locations."""
    authors = len(labels)
    groups = int(labels.max()) + 1
    centers, directions = _group_geometry(groups, ambient)
    anchors = np.linspace(-0.55, 0.55, groups)
    truth = np.zeros((authors, len(t), ambient), dtype=float)
    common = _common_curve(t, ambient)

    for author, group in enumerate(labels):
        center = centers[group]
        direction = directions[group]
        anchor = anchors[group]
        delta = t - anchor
        if world in {
            "group_regional_affine_2d",
            "group_regional_affine_3d",
            "heteroskedastic_group_3d",
        }:
            author_direction = rng.normal(scale=0.035, size=ambient)
            curvature = rng.normal(scale=0.018, size=ambient)
            truth[author] = (
                common
                + center
                + np.outer(delta, 0.48 * direction + author_direction)
                + np.outer(delta**2, curvature)
            )
        elif world == "group_tangent_quadratic_2d":
            curvature = rng.normal(scale=0.18, size=ambient)
            truth[author] = (
                common
                + center
                + np.outer(delta, 0.62 * direction)
                + np.outer(delta**2, curvature)
            )
        elif world == "group_isolated_transverse_2d":
            angle = rng.uniform(0.0, 2.0 * np.pi)
            slope = 1.1 * np.asarray([np.cos(angle), np.sin(angle)])
            truth[author] = common + center + np.outer(delta, slope)
        elif world == "common_anchor_plus_groups_2d":
            author_direction = rng.normal(scale=0.025, size=ambient)
            truth[author] = np.outer(
                t,
                0.85 * direction + author_direction,
            ) + np.outer(t**2, 0.20 * center)
            anchors[group] = 0.0
        elif world == "nonlinear_rbf_group_2d":
            bump_center = anchors[group]
            bump = np.exp(-0.5 * ((t - bump_center) / 0.28) ** 2)
            normal = np.asarray([-direction[1], direction[0]])
            author_direction = rng.normal(scale=0.025, size=ambient)
            truth[author] = (
                common
                + center
                + np.outer(t, 0.35 * direction + author_direction)
                + np.outer(bump, 0.42 * normal)
            )
        else:
            raise ValueError(f"unsupported group world: {world}")
    return truth, anchors


def _null_truth(
    *,
    world: str,
    t: np.ndarray,
    labels: np.ndarray,
    ambient: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    authors = len(labels)
    truth = np.zeros((authors, len(t), ambient), dtype=float)
    anchors = np.full(int(labels.max()) + 1, np.nan)

    if world == "global_common_anchor_2d":
        for author in range(authors):
            slope = rng.normal(size=ambient)
            slope = _unit(slope) * rng.uniform(0.65, 1.25)
            curve = rng.normal(scale=0.18, size=ambient)
            truth[author] = np.outer(t, slope) + np.outer(t**2, curve)
        return truth, np.zeros_like(anchors)

    if world == "random_crossings_2d":
        for author in range(authors):
            intercept = rng.normal(scale=1.1, size=ambient)
            slope = rng.normal(scale=0.75, size=ambient)
            curve = rng.normal(scale=0.12, size=ambient)
            truth[author] = (
                intercept
                + np.outer(t, slope)
                + np.outer(t**2, curve)
            )
        return truth, anchors

    if world == "pair_map_equivalence_2d":
        for pair_start in range(0, authors, 2):
            intercept = rng.normal(scale=1.1, size=ambient)
            slope = rng.normal(scale=0.65, size=ambient)
            curve = rng.normal(scale=0.10, size=ambient)
            base = (
                intercept
                + np.outer(t, slope)
                + np.outer(t**2, curve)
            )
            for author in range(pair_start, min(pair_start + 2, authors)):
                truth[author] = base + np.outer(
                    t,
                    rng.normal(scale=0.008, size=ambient),
                )
        return truth, anchors

    if world == "continuous_ring_2d":
        phase = rng.uniform(0.0, 2.0 * np.pi)
        angles = phase + 2.0 * np.pi * np.arange(authors) / authors
        for author, angle in enumerate(angles):
            radial = np.asarray([np.cos(angle), np.sin(angle)])
            tangent = np.asarray([-np.sin(angle), np.cos(angle)])
            truth[author] = (
                3.0 * radial
                + np.outer(t, 0.45 * tangent)
                + np.outer(t**2, 0.10 * radial)
            )
        return truth, anchors

    if world == "projection_crossing_3d":
        offsets = np.linspace(-1.2, 1.2, authors)
        for author in range(authors):
            angle = 2.0 * np.pi * author / authors
            truth[author, :, 0] = np.cos(angle) * t
            truth[author, :, 1] = np.sin(angle) * t
            truth[author, :, 2] = offsets[author]
        return truth, anchors

    raise ValueError(f"unsupported null world: {world}")


def simulate_population(
    *,
    seed: int,
    world: str,
    spec: MultiplicitySpec,
    noise_sd: float | None = None,
) -> dict[str, Any]:
    """Simulate a fresh multi-author condition-response population."""
    if world not in WORLD_META:
        raise ValueError(f"unsupported multiplicity world: {world}")
    rng = np.random.default_rng(seed)
    meta = WORLD_META[world]
    ambient = int(meta["ambient"])
    t = np.linspace(-1.0, 1.0, spec.conditions)
    labels = _balanced_labels(spec.authors, spec.groups, rng)

    group_source = world
    if world in {
        "observer_artifact_2d",
        "half_artifact_2d",
        "condition_permutation_2d",
        "partial_support_2d",
    }:
        group_source = "group_regional_affine_2d"

    if meta["kind"] in {"clear_group", "challenge_group"} or world in {
        "group_isolated_transverse_2d",
        "condition_permutation_2d",
        "partial_support_2d",
    }:
        truth, anchors = _group_truth(
            world=group_source,
            t=t,
            labels=labels,
            ambient=ambient,
            rng=rng,
        )
    elif world in {"observer_artifact_2d", "half_artifact_2d"}:
        truth, anchors = _null_truth(
            world="random_crossings_2d",
            t=t,
            labels=labels,
            ambient=ambient,
            rng=rng,
        )
    else:
        truth, anchors = _null_truth(
            world=world,
            t=t,
            labels=labels,
            ambient=ambient,
            rng=rng,
        )

    sigma = float(spec.noise_sd if noise_sd is None else noise_sd)
    observations = np.empty(
        (
            spec.authors,
            spec.halves,
            spec.observers,
            spec.conditions,
            ambient,
        ),
        dtype=float,
    )
    centers, _ = _group_geometry(spec.groups, ambient)
    for author in range(spec.authors):
        for half in range(spec.halves):
            for observer in range(spec.observers):
                current = truth[author].copy()
                if world == "observer_artifact_2d" and observer == 1:
                    current = current + 0.85 * centers[labels[author]]
                if world == "half_artifact_2d" and half == 1:
                    current = current + 0.85 * centers[labels[author]]
                if world == "condition_permutation_2d":
                    permutation_rng = np.random.default_rng(
                        seed + 100_000 + author
                    )
                    current = current[
                        permutation_rng.permutation(spec.conditions)
                    ]
                local_sigma = sigma
                if world == "heteroskedastic_group_3d":
                    local_sigma = sigma * (
                        0.45 + 1.55 * np.abs(t)
                    )[:, None]
                observations[author, half, observer] = (
                    current
                    + rng.normal(size=current.shape) * local_sigma
                )

    if world == "partial_support_2d":
        mask_rng = np.random.default_rng(seed + 900_000)
        keep = mask_rng.random(observations.shape[:-1]) < 0.48
        observations[~keep] = np.nan

    return {
        "world": world,
        "meta": meta,
        "conditions": t,
        "truth": truth,
        "observations": observations,
        "group_labels": labels,
        "group_anchors": anchors,
    }


def rank_condition_coordinate(conditions: np.ndarray) -> np.ndarray:
    """Map any strictly ordered scalar condition coordinate to [-1, 1]."""
    values = np.asarray(conditions, dtype=float)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    ranks[order] = np.arange(len(values), dtype=float)
    if len(values) <= 1:
        return np.zeros_like(values)
    return 2.0 * ranks / (len(values) - 1.0) - 1.0


def basis_design(conditions: np.ndarray) -> np.ndarray:
    """Return the frozen polynomial/RBF basis on rank-normalized conditions."""
    z = rank_condition_coordinate(conditions)
    centers = np.linspace(-1.0, 1.0, 7)
    width = 0.34
    rbf = np.exp(
        -0.5 * ((z[:, None] - centers[None, :]) / width) ** 2
    )
    return np.column_stack([
        np.ones(len(z)),
        z,
        z**2,
        z**3,
        rbf,
    ])


def fit_population(
    conditions: np.ndarray,
    observations: np.ndarray,
    *,
    ridge_alpha: float,
) -> dict[str, Any]:
    """Fit one frozen-basis response map per author/half/observer."""
    design = basis_design(conditions)
    authors, halves, observers, _, ambient = observations.shape
    predictions = np.full(
        (halves * observers, authors, len(conditions), ambient),
        np.nan,
    )
    residuals = np.full((halves * observers, authors), np.nan)
    supports = np.zeros((halves * observers, authors), dtype=float)
    penalty = np.eye(design.shape[1]) * float(ridge_alpha)
    penalty[0, 0] = 0.0
    for author in range(authors):
        view = 0
        for half in range(halves):
            for observer in range(observers):
                response = observations[author, half, observer]
                valid = np.all(np.isfinite(response), axis=1)
                supports[view, author] = float(np.mean(valid))
                if int(valid.sum()) >= design.shape[1] + 2:
                    x = design[valid]
                    y = response[valid]
                    coefficient = np.linalg.solve(
                        x.T @ x + penalty,
                        x.T @ y,
                    )
                    fitted = design @ coefficient
                    predictions[view, author] = fitted
                    residuals[view, author] = float(
                        np.sqrt(np.mean((y - fitted[valid]) ** 2))
                    )
                view += 1
    aggregate = np.nanmean(predictions, axis=0)
    view_variance = np.nanmean(
        np.sum(
            (predictions - aggregate[None, ...]) ** 2,
            axis=-1,
        ),
        axis=0,
    )
    author_residual = np.nanmedian(residuals, axis=0)
    prediction_scale = np.sqrt(
        np.maximum(
            view_variance
            + author_residual[:, None] ** 2,
            1e-10,
        )
    )
    return {
        "aggregate": aggregate,
        "views": predictions,
        "residuals": residuals,
        "supports": supports,
        "prediction_scale": prediction_scale,
    }


def _circumball(points: np.ndarray) -> tuple[np.ndarray, float] | None:
    """Return the ball through up to p+1 affinely independent points."""
    points = np.asarray(points, dtype=float)
    if len(points) == 0:
        return np.zeros(points.shape[1]), 0.0
    if len(points) == 1:
        return points[0].copy(), 0.0
    base = points[0]
    differences = points[1:] - base
    gram = differences @ differences.T
    if np.linalg.matrix_rank(gram) < len(points) - 1:
        return None
    rhs = np.sum(differences**2, axis=1) / 2.0
    coefficients = np.linalg.solve(gram, rhs)
    center = base + differences.T @ coefficients
    radius = float(np.max(np.linalg.norm(points - center, axis=1)))
    return center, radius


def minimum_enclosing_ball(points: np.ndarray) -> tuple[np.ndarray, float]:
    """Exact small-dimensional minimum enclosing ball by support enumeration."""
    points = np.asarray(points, dtype=float)
    if len(points) == 0:
        raise ValueError("minimum enclosing ball requires at least one point")
    ambient = points.shape[1]
    best_center = points[0].copy()
    best_radius = float("inf")
    for size in range(1, min(ambient + 1, len(points)) + 1):
        for indices in combinations(range(len(points)), size):
            candidate = _circumball(points[list(indices)])
            if candidate is None:
                continue
            center, radius = candidate
            distances = np.linalg.norm(points - center, axis=1)
            required = float(np.max(distances))
            if required <= radius + 1e-8 and required < best_radius:
                best_center = center
                best_radius = required
    if not np.isfinite(best_radius):
        center = points.mean(axis=0)
        return center, float(np.max(np.linalg.norm(points - center, axis=1)))
    return best_center, best_radius


def verified_hyperedges(
    centers: np.ndarray,
    *,
    epsilon: float,
) -> list[tuple[int, ...]]:
    """Find disjoint complete-link candidates with a verified common ball."""
    centers = np.asarray(centers, dtype=float)
    if len(centers) < 2:
        return []
    condensed = pdist(centers)
    if np.all(condensed <= 1e-12):
        candidates = np.ones(len(centers), dtype=int)
    else:
        tree = linkage(condensed, method="complete")
        candidates = fcluster(
            tree,
            t=2.0 * float(epsilon),
            criterion="distance",
        )
    result: list[tuple[int, ...]] = []
    for cluster_id in np.unique(candidates):
        members = np.flatnonzero(candidates == cluster_id)
        if len(members) < 2:
            continue
        _, radius = minimum_enclosing_ball(centers[members])
        if radius <= float(epsilon) + 1e-7:
            result.append(tuple(int(item) for item in members))
    return result


def _pair_indices(authors: int) -> tuple[np.ndarray, np.ndarray]:
    return np.triu_indices(authors, 1)


def _pair_kernel(
    predictions: np.ndarray,
    scale: np.ndarray,
) -> np.ndarray:
    authors = predictions.shape[0]
    left, right = _pair_indices(authors)
    delta = predictions[left] - predictions[right]
    denominator = np.sqrt(
        scale[left] ** 2 + scale[right] ** 2
    )
    q = np.linalg.norm(delta, axis=-1) / np.maximum(denominator, 1e-8)
    return np.mean(np.exp(-0.5 * q**2), axis=1)


def persistent_hyperedge_scores(
    predictions: np.ndarray,
    prediction_scale: np.ndarray,
    *,
    epsilon_grid: tuple[float, ...],
) -> dict[str, Any]:
    """Estimate raw and pair-specific persistent common-ball incidence."""
    authors, conditions, _ = predictions.shape
    left, right = _pair_indices(authors)
    pair_lookup = {
        (int(a), int(b)): index
        for index, (a, b) in enumerate(zip(left, right, strict=True))
    }
    raw_score = np.zeros(len(left), dtype=float)
    specific_score = np.zeros(len(left), dtype=float)
    tangent_score = np.zeros(len(left), dtype=float)
    occurrences: dict[tuple[int, ...], float] = {}
    condition_max = np.ones(conditions, dtype=int)
    derivatives = np.gradient(predictions, axis=1)
    derivative_norm = np.linalg.norm(derivatives, axis=-1, keepdims=True)
    derivative_unit = derivatives / np.maximum(derivative_norm, 1e-8)

    for condition in range(conditions):
        pooled_scale = float(
            np.nanmedian(prediction_scale[:, condition])
        )
        normalized = predictions[:, condition] / max(pooled_scale, 1e-8)
        for epsilon in epsilon_grid:
            hyperedges = verified_hyperedges(
                normalized,
                epsilon=float(epsilon),
            )
            for members in hyperedges:
                multiplicity = len(members)
                condition_max[condition] = max(
                    condition_max[condition],
                    multiplicity,
                )
                specificity = (
                    (authors - multiplicity) / max(authors - 2, 1)
                )
                if specificity > 0.0 and multiplicity >= 3:
                    occurrences[members] = (
                        occurrences.get(members, 0.0) + specificity
                    )
                for a, b in combinations(members, 2):
                    index = pair_lookup[(min(a, b), max(a, b))]
                    raw_score[index] += 1.0
                    specific_score[index] += specificity
                    alignment = float(
                        np.clip(
                            np.dot(
                                derivative_unit[a, condition],
                                derivative_unit[b, condition],
                            ),
                            -1.0,
                            1.0,
                        )
                    )
                    tangent_score[index] += (
                        specificity * (alignment + 1.0) / 2.0
                    )
    denominator = float(conditions * len(epsilon_grid))
    raw_score /= denominator
    specific_score /= denominator
    tangent_score /= denominator
    centered = specific_score - float(np.mean(specific_score))
    standardized = centered / max(float(np.std(centered)), 1e-8)
    ranked_hyperedges = sorted(
        (
            (members, score / denominator)
            for members, score in occurrences.items()
        ),
        key=lambda item: item[1],
        reverse=True,
    )
    return {
        "raw_pair_score": raw_score,
        "specific_pair_score": specific_score,
        "tangent_pair_score": tangent_score,
        "standardized_pair_score": standardized,
        "condition_max_multiplicity": condition_max,
        "max_raw_multiplicity": int(condition_max.max()),
        "ranked_hyperedges": ranked_hyperedges,
    }


def _group_localization(
    predictions: np.ndarray,
    labels: np.ndarray,
    anchors: np.ndarray,
    conditions: np.ndarray,
) -> float:
    errors = []
    for group in range(int(labels.max()) + 1):
        if group >= len(anchors) or not np.isfinite(anchors[group]):
            continue
        members = np.flatnonzero(labels == group)
        pair_distances = []
        for left, right in combinations(members, 2):
            pair_distances.append(np.linalg.norm(
                predictions[left] - predictions[right],
                axis=1,
            ))
        if not pair_distances:
            continue
        mean_distance = np.mean(pair_distances, axis=0)
        estimated = float(conditions[int(np.argmin(mean_distance))])
        errors.append(abs(estimated - float(anchors[group])) / 2.0)
    return float(np.median(errors)) if errors else float("nan")


def analyze_population(
    population: dict[str, Any],
    *,
    ridge_alpha: float,
    epsilon_grid: tuple[float, ...],
) -> dict[str, Any]:
    """Fit one population and return label-free scores plus audit labels."""
    fit = fit_population(
        population["conditions"],
        population["observations"],
        ridge_alpha=ridge_alpha,
    )
    if np.any(~np.isfinite(fit["aggregate"])):
        return {
            "status": "REFUSE_FIT_FAILURE",
            "world": population["world"],
            "kind": population["meta"]["kind"],
        }
    hyper = persistent_hyperedge_scores(
        fit["aggregate"],
        fit["prediction_scale"],
        epsilon_grid=epsilon_grid,
    )
    labels = population["group_labels"]
    left, right = _pair_indices(len(labels))
    pair_labels = (labels[left] == labels[right]).astype(int)
    view_scores = []
    residual_scale = np.nanmedian(
        fit["prediction_scale"],
        axis=0,
    )[None, :]
    residual_scale = np.repeat(
        residual_scale,
        len(labels),
        axis=0,
    )
    for view in fit["views"]:
        view_scores.append(_pair_kernel(view, residual_scale))
    correlations = []
    for first, second in combinations(view_scores, 2):
        correlation = spearmanr(first, second).statistic
        correlations.append(
            0.0 if not np.isfinite(correlation) else float(correlation)
        )
    top = hyper["ranked_hyperedges"][: max(int(labels.max()) + 1, 1)]
    estimated_multiplicity = (
        float(np.median([len(members) for members, _ in top]))
        if top
        else 1.0
    )
    return {
        "status": "ESTIMATE_READY",
        "world": population["world"],
        "kind": population["meta"]["kind"],
        "relation": population["meta"]["relation"],
        "pair_scores": hyper["standardized_pair_score"].tolist(),
        "raw_pair_scores": hyper["raw_pair_score"].tolist(),
        "tangent_pair_scores": hyper["tangent_pair_score"].tolist(),
        "pair_labels": pair_labels.tolist(),
        "hyperedges": [
            {
                "members": list(members),
                "persistence": float(persistence),
            }
            for members, persistence in hyper["ranked_hyperedges"]
        ],
        "maximum_hyperedge_persistence": (
            float(hyper["ranked_hyperedges"][0][1])
            if hyper["ranked_hyperedges"]
            else 0.0
        ),
        "max_raw_multiplicity": hyper["max_raw_multiplicity"],
        "estimated_multiplicity": estimated_multiplicity,
        "expected_multiplicity": int(np.sum(labels == labels[0])),
        "condition_localization_error": _group_localization(
            fit["aggregate"],
            labels,
            population["group_anchors"],
            population["conditions"],
        ),
        "cross_view_spearman": float(np.median(correlations)),
        "residual_rmse": float(np.nanmedian(fit["residuals"])),
        "residual_fraction": float(
            np.nanmedian(fit["residuals"])
            / max(
                float(np.nanstd(population["observations"])),
                1e-8,
            )
        ),
        "maximum_residual_rmse": float(np.nanmax(fit["residuals"])),
        "minimum_support": float(np.nanmin(fit["supports"])),
    }


def condition_reparameterization_consistency(
    population: dict[str, Any],
    *,
    ridge_alpha: float,
) -> float:
    """Check invariance to a strictly monotone condition reparameterization."""
    original = fit_population(
        population["conditions"],
        population["observations"],
        ridge_alpha=ridge_alpha,
    )
    transformed_conditions = (
        0.37
        + 2.4 * np.sign(population["conditions"])
        * np.abs(population["conditions"]) ** 1.7
    )
    transformed = fit_population(
        transformed_conditions,
        population["observations"],
        ridge_alpha=ridge_alpha,
    )
    left = _pair_kernel(
        original["aggregate"],
        original["prediction_scale"],
    )
    right = _pair_kernel(
        transformed["aggregate"],
        transformed["prediction_scale"],
    )
    correlation = spearmanr(left, right).statistic
    return 0.0 if not np.isfinite(correlation) else float(correlation)


def pair_score_matrix(scores: np.ndarray, authors: int) -> np.ndarray:
    """Convert upper-triangle pair scores into a symmetric matrix."""
    result = np.zeros((authors, authors), dtype=float)
    upper = _pair_indices(authors)
    result[upper] = np.asarray(scores, dtype=float)
    result[(upper[1], upper[0])] = result[upper]
    return result


def complete_link_labels(
    scores: np.ndarray,
    *,
    authors: int,
    threshold: float,
) -> np.ndarray:
    """Partition authors so every within-cluster score clears a threshold."""
    values = np.asarray(scores, dtype=float)
    if len(values) == 0 or float(np.max(values)) < threshold:
        return np.arange(authors, dtype=int)
    maximum = max(float(np.max(values)), float(threshold))
    distances = np.maximum(maximum - values, 0.0)
    tree = linkage(distances, method="complete")
    return fcluster(
        tree,
        t=max(maximum - float(threshold), 0.0),
        criterion="distance",
    ) - 1
