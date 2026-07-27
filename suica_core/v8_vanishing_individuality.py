"""Vanishing-individuality planted worlds for the SUICA V8 C2 surface."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import pdist
from scipy.special import expit
from scipy.stats import spearmanr
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, roc_auc_score
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import KNeighborsRegressor

from .v8_behavior_c2 import (
    factorial_condition_basis,
    fit_c2_pipeline,
)


@dataclass(frozen=True)
class VanishingIndividualitySpec:
    """Dimensions for one hierarchical shared-condition planted world."""

    discovery_authors: int = 60
    calibration_authors: int = 20
    confirmation_authors: int = 80
    conditions: int = 8
    condition_dimensions: int = 3
    behavior_families: int = 5
    forced_repeats: int = 6
    extra_repeats: int = 96
    groups: int = 4
    intercept_sd: float = 0.45
    half_state_sd: float = 0.25
    selection_strength: float = 2.0

    @property
    def authors(self) -> int:
        return (
            self.discovery_authors
            + self.calibration_authors
            + self.confirmation_authors
        )


def _balanced_labels(
    rng: np.random.Generator,
    spec: VanishingIndividualitySpec,
) -> np.ndarray:
    labels: list[np.ndarray] = []
    for size in (
        spec.discovery_authors,
        spec.calibration_authors,
        spec.confirmation_authors,
    ):
        if size % spec.groups:
            raise ValueError("each split must be divisible by groups")
        block = np.repeat(np.arange(spec.groups), size // spec.groups)
        rng.shuffle(block)
        labels.append(block)
    return np.concatenate(labels)


def _group_center(
    values: np.ndarray,
    labels: np.ndarray,
    groups: int,
) -> np.ndarray:
    result = np.asarray(values, dtype=float).copy()
    for group in range(groups):
        mask = labels == group
        result[mask] -= result[mask].mean(axis=0, keepdims=True)
    return result


def _information_normalize(
    operator: np.ndarray,
    basis: np.ndarray,
    base_eta: np.ndarray,
    *,
    repeats: int,
) -> np.ndarray:
    response = np.einsum("ck,uhgk->uhcg", basis, operator)
    probability = expit(np.clip(base_eta, -8.0, 8.0))
    information = (
        float(repeats)
        * probability
        * (1.0 - probability)
        * response**2
    )
    scale = np.sqrt(1.0 / max(float(information.mean()), 1e-12))
    return operator * scale


def _selection_counts(
    rng: np.random.Generator,
    q: np.ndarray,
    basis: np.ndarray,
    *,
    halves: int,
    repeats: int,
    strength: float,
) -> np.ndarray:
    logits = strength * (q @ basis.T)
    logits -= logits.max(axis=1, keepdims=True)
    probabilities = np.exp(logits)
    probabilities /= probabilities.sum(axis=1, keepdims=True)
    counts = np.empty((len(q), halves, len(basis)), dtype=int)
    for author in range(len(q)):
        for half in range(halves):
            counts[author, half] = rng.multinomial(
                repeats,
                probabilities[author],
            )
    return counts


def simulate_hierarchical_c2_world(
    *,
    seed: int,
    world: str,
    epsilon: float,
    group_amplitude: float,
    spec: VanishingIndividualitySpec,
) -> dict[str, Any]:
    """Simulate a binary C2 surface with group and individual components."""
    rng = np.random.default_rng(seed)
    u, h, c, k, g = (
        spec.authors,
        2,
        spec.conditions,
        spec.condition_dimensions,
        spec.behavior_families,
    )
    basis = factorial_condition_basis(k)
    if len(basis) != c:
        raise ValueError("conditions must equal the factorial basis size")
    labels = _balanced_labels(rng, spec)
    splits = np.asarray(
        ["discovery"] * spec.discovery_authors
        + ["calibration"] * spec.calibration_authors
        + ["confirmation"] * spec.confirmation_authors
    )
    delta = rng.normal(scale=0.35, size=(c, g))
    intercept = rng.normal(scale=spec.intercept_sd, size=(u, g))
    half_state = rng.normal(scale=spec.half_state_sd, size=(u, h, g))
    base_eta = (
        delta[None, None, :, :]
        + intercept[:, None, None, :]
        + half_state[:, :, None, :]
    )

    group_seed = rng.normal(size=(spec.groups, g, k))
    group_seed -= group_seed.mean(axis=0, keepdims=True)
    group_operator = group_seed[labels, None]
    group_operator = np.repeat(group_operator, h, axis=1)
    group_operator = _information_normalize(
        group_operator,
        basis,
        base_eta,
        repeats=spec.forced_repeats,
    )

    stable_seed = rng.normal(size=(u, g, k))
    stable_seed = _group_center(stable_seed, labels, spec.groups)
    stable_operator = np.repeat(stable_seed[:, None], h, axis=1)
    stable_operator = _information_normalize(
        stable_operator,
        basis,
        base_eta,
        repeats=spec.forced_repeats,
    )

    unstable_operator = rng.normal(size=(u, h, g, k))
    for half in range(h):
        unstable_operator[:, half] = _group_center(
            unstable_operator[:, half],
            labels,
            spec.groups,
        )
    unstable_operator = _information_normalize(
        unstable_operator,
        basis,
        base_eta,
        repeats=spec.forced_repeats,
    )

    t = rng.uniform(size=u)
    manifold_latent = np.column_stack([
        np.cos(2.0 * np.pi * t),
        np.sin(2.0 * np.pi * t),
        t - 0.5,
    ])
    manifold_map = rng.normal(size=(3, g * k))
    manifold_seed = (manifold_latent @ manifold_map).reshape(u, g, k)
    manifold_seed -= manifold_seed.mean(axis=0, keepdims=True)
    manifold_operator = np.repeat(manifold_seed[:, None], h, axis=1)
    manifold_operator = _information_normalize(
        manifold_operator,
        basis,
        base_eta,
        repeats=spec.forced_repeats,
    )

    zero = np.zeros_like(stable_operator)
    individual_component = zero
    group_component = zero
    if world == "group_only":
        group_component = group_amplitude * group_operator
    elif world == "individual_only":
        individual_component = epsilon * stable_operator
    elif world in {"joint", "epsilon_ladder"}:
        group_component = group_amplitude * group_operator
        individual_component = epsilon * stable_operator
    elif world == "continuous_manifold":
        individual_component = manifold_operator
    elif world == "observer_artifact":
        individual_component = epsilon * stable_operator
    elif world == "half_unstable":
        individual_component = epsilon * unstable_operator
    elif world not in {"null", "c1_group_confound"}:
        raise ValueError(f"unsupported hierarchy world: {world}")
    operator = group_component + individual_component
    response = np.einsum("ck,uhgk->uhcg", basis, operator)
    eta = base_eta + response
    probability = expit(np.clip(eta, -8.0, 8.0))

    fixed_n = np.full((u, h, c, 1), spec.forced_repeats, dtype=int)
    fixed_n = np.broadcast_to(fixed_n, eta.shape).copy()
    fixed_sum = rng.binomial(fixed_n, probability)
    if world == "c1_group_confound":
        q_group = rng.normal(size=(spec.groups, k))
        q = q_group[labels]
    else:
        q = np.zeros((u, k))
    extra = _selection_counts(
        rng,
        q,
        basis,
        halves=h,
        repeats=spec.extra_repeats,
        strength=spec.selection_strength,
    )
    extra_n = np.broadcast_to(extra[:, :, :, None], eta.shape).copy()
    extra_sum = rng.binomial(extra_n, probability)
    all_n = fixed_n + extra_n
    all_sum = fixed_sum + extra_sum
    c1 = extra / np.maximum(extra.sum(axis=2, keepdims=True), 1)
    opportunity = np.ones((c, g), dtype=bool)
    shared = np.ones(c, dtype=bool)
    response_group = np.einsum(
        "ck,uhgk->uhcg",
        basis,
        group_component,
    )
    response_individual = np.einsum(
        "ck,uhgk->uhcg",
        basis,
        individual_component,
    )
    return {
        "world": world,
        "observation": "binary",
        "snr": float(group_amplitude**2 + epsilon**2),
        "overlap": 1.0,
        "truth": {
            "q": q,
            "intercept": intercept,
            "operator": operator,
            "response_surface": response,
            "response_surface_observed": response,
            "group_response": response_group,
            "individual_response": response_individual,
            "group_labels": labels,
            "manifold_t": t,
        },
        "data": {
            "fixed_mean": fixed_sum / fixed_n,
            "all_mean": all_sum / all_n,
            "expected_mean": probability,
            "fixed_variance": probability * (1.0 - probability) / fixed_n,
            "all_variance": probability * (1.0 - probability) / all_n,
            "c1": c1,
            "splits": splits,
            "basis": basis,
            "opportunity": opportunity,
            "shared_conditions": shared,
            "fixed_successes": fixed_sum,
            "all_successes": all_sum,
            "fixed_trials": fixed_n,
            "all_trials": all_n,
        },
        "design": {"condition_identity_shared": True},
        "hierarchy": {
            "epsilon": float(epsilon),
            "group_amplitude": float(group_amplitude),
        },
    }


def _row_normalize(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    return matrix / np.maximum(
        np.linalg.norm(matrix, axis=1, keepdims=True),
        1e-12,
    )


def pairing_auc_metrics(
    left: np.ndarray,
    right: np.ndarray,
    labels: np.ndarray,
) -> dict[str, float]:
    """Separate author identity from shared group membership."""
    similarity = _row_normalize(left) @ _row_normalize(right).T
    n = len(similarity)
    identity = np.eye(n, dtype=bool)
    same_group = labels[:, None] == labels[None, :]
    within_negative = same_group & ~identity
    between = ~same_group
    positive = similarity[identity]
    all_negative = similarity[~identity]

    def auc(pos: np.ndarray, neg: np.ndarray) -> float:
        target = np.concatenate([
            np.ones(len(pos), dtype=int),
            np.zeros(len(neg), dtype=int),
        ])
        score = np.concatenate([pos, neg])
        return float(roc_auc_score(target, score))

    return {
        "author_all_auc": auc(positive, all_negative),
        "author_within_group_auc": auc(
            positive,
            similarity[within_negative],
        ),
        "group_auc": auc(
            similarity[within_negative],
            similarity[between],
        ),
        "within_pairing_statistic": float(
            positive.mean() - similarity[within_negative].mean()
        ),
    }


def within_group_pairing_p(
    left: np.ndarray,
    right: np.ndarray,
    labels: np.ndarray,
    *,
    seed: int,
    permutations: int,
) -> float:
    """Test matched authors while preserving planted group membership."""
    similarity = _row_normalize(left) @ _row_normalize(right).T
    observed = float(np.diag(similarity).mean())
    rng = np.random.default_rng(seed)
    null = np.empty(permutations, dtype=float)
    indices = np.arange(len(labels))
    for draw in range(permutations):
        permuted = indices.copy()
        for group in np.unique(labels):
            mask = np.flatnonzero(labels == group)
            permuted[mask] = rng.permutation(mask)
        null[draw] = float(similarity[indices, permuted].mean())
    return float((1 + np.sum(null >= observed)) / (permutations + 1))


def stable_residual_covariance(
    left: np.ndarray,
    right: np.ndarray,
    labels: np.ndarray,
) -> np.ndarray:
    """Estimate stable within-group covariance by paired-minus-unpaired moments."""
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    paired = np.einsum("ni,nj->ij", left, right) / len(left)
    total = np.zeros_like(paired)
    pairs = 0
    for group in np.unique(labels):
        mask = np.flatnonzero(labels == group)
        if len(mask) < 2:
            continue
        l_group = left[mask]
        r_group = right[mask]
        cross = (
            l_group.sum(axis=0)[:, None]
            @ r_group.sum(axis=0)[None, :]
            - l_group.T @ r_group
        )
        total += cross
        pairs += len(mask) * (len(mask) - 1)
    unpaired = total / max(pairs, 1)
    covariance = paired - unpaired
    return 0.5 * (covariance + covariance.T)


def _remove_discovery_group_centers(
    values: np.ndarray,
    labels: np.ndarray,
    splits: np.ndarray,
) -> np.ndarray:
    result = np.asarray(values, dtype=float).copy()
    discovery = splits == "discovery"
    for half in range(result.shape[1]):
        for group in np.unique(labels):
            center = result[
                discovery & (labels == group),
                half,
            ].mean(axis=0)
            result[labels == group, half] -= center
    return result


def _predictive_geometry(
    discovery_left: np.ndarray,
    discovery_right: np.ndarray,
    calibration_left: np.ndarray,
    calibration_right: np.ndarray,
    confirmation_left: np.ndarray,
    confirmation_right: np.ndarray,
    *,
    seed: int,
) -> dict[str, float]:
    center = discovery_left.mean(axis=0)
    scale = discovery_left.std(axis=0)
    scale[scale < 1e-8] = 1.0

    def transform(values: np.ndarray) -> np.ndarray:
        return (values - center) / scale

    dl = transform(discovery_left)
    dr = transform(discovery_right)
    cl = transform(calibration_left)
    cr = transform(calibration_right)
    tl = transform(confirmation_left)
    tr = transform(confirmation_right)
    baseline = max(float(np.mean((tr - dr.mean(axis=0)) ** 2)), 1e-12)

    mixture_candidates: list[tuple[float, int, Any, np.ndarray]] = []
    for components in range(1, 7):
        model = GaussianMixture(
            n_components=components,
            covariance_type="diag",
            random_state=seed + components,
            reg_covar=1e-5,
        ).fit(dl)
        assignment = model.predict(dl)
        right_centers = np.vstack([
            dr[assignment == index].mean(axis=0)
            for index in range(components)
        ])
        prediction = right_centers[model.predict(cl)]
        mse = float(np.mean((cr - prediction) ** 2))
        mixture_candidates.append((mse, components, model, right_centers))
    _, mixture_k, mixture_model, right_centers = min(
        mixture_candidates,
        key=lambda row: (row[0], row[1]),
    )
    mixture_prediction = right_centers[mixture_model.predict(tl)]
    mixture_nmse = float(
        np.mean((tr - mixture_prediction) ** 2) / baseline
    )

    manifold_candidates: list[tuple[float, int, Any]] = []
    for neighbors in (3, 5, 10, 15):
        model = KNeighborsRegressor(
            n_neighbors=min(neighbors, len(dl)),
            weights="distance",
        ).fit(dl, dr)
        mse = float(np.mean((cr - model.predict(cl)) ** 2))
        manifold_candidates.append((mse, neighbors, model))
    _, manifold_k, manifold_model = min(
        manifold_candidates,
        key=lambda row: (row[0], row[1]),
    )
    manifold_nmse = float(
        np.mean((tr - manifold_model.predict(tl)) ** 2) / baseline
    )
    return {
        "mixture_components": float(mixture_k),
        "mixture_nmse": mixture_nmse,
        "manifold_neighbors": float(manifold_k),
        "manifold_nmse": manifold_nmse,
        "manifold_advantage": mixture_nmse - manifold_nmse,
    }


def analyze_hierarchical_world(
    world: dict[str, Any],
    *,
    seed: int,
    ridge_candidates: tuple[float, ...],
    permutations: int,
    audit_world: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fit the frozen C2 estimator and decompose author/group structure."""
    estimate = fit_c2_pipeline(
        world,
        cell_mean_key="fixed_mean",
        ridge_candidates=ridge_candidates,
    )
    if estimate["status"] != "C2_ESTIMATE_READY":
        return {
            "status": estimate["status"],
            "numeric_output": False,
        }
    splits = np.asarray(world["data"]["splits"])
    labels = np.asarray(world["truth"]["group_labels"])
    discovery = np.flatnonzero(splits == "discovery")
    calibration = np.flatnonzero(splits == "calibration")
    confirmation = np.flatnonzero(splits == "confirmation")
    score = np.asarray(estimate["standardized"], dtype=float)
    left = score[confirmation, 0]
    right = score[confirmation, 1]
    metrics = pairing_auc_metrics(left, right, labels[confirmation])
    metrics["within_group_pairing_p"] = within_group_pairing_p(
        left,
        right,
        labels[confirmation],
        seed=seed,
        permutations=permutations,
    )
    c1 = np.asarray(world["data"]["c1"], dtype=float).reshape(
        len(splits),
        2,
        -1,
    )
    metrics["c1_group_auc"] = pairing_auc_metrics(
        c1[confirmation, 0],
        c1[confirmation, 1],
        labels[confirmation],
    )["group_auc"]

    author_mean = score.mean(axis=1)
    cluster = KMeans(
        n_clusters=len(np.unique(labels)),
        random_state=seed,
        n_init=20,
    ).fit(author_mean[discovery])
    metrics["confirmation_cluster_ari"] = float(
        adjusted_rand_score(
            labels[confirmation],
            cluster.predict(author_mean[confirmation]),
        )
    )
    true_group = np.asarray(world["truth"]["group_response"]).reshape(
        len(splits),
        2,
        -1,
    ).mean(axis=1)
    estimated_centers = []
    true_centers = []
    for group in np.unique(labels):
        estimated_centers.append(
            author_mean[confirmation][labels[confirmation] == group].mean(
                axis=0
            )
        )
        true_centers.append(
            true_group[confirmation][labels[confirmation] == group].mean(
                axis=0
            )
        )
    estimated_distance = pdist(np.asarray(estimated_centers))
    true_distance = pdist(np.asarray(true_centers))
    metrics["group_distance_spearman"] = (
        float(spearmanr(true_distance, estimated_distance).statistic)
        if np.std(true_distance) > 1e-12
        else float("nan")
    )

    residual = _remove_discovery_group_centers(
        np.asarray(estimate["surface"], dtype=float),
        labels,
        splits,
    )
    residual_covariance = stable_residual_covariance(
        residual[confirmation, 0],
        residual[confirmation, 1],
        labels[confirmation],
    )
    eigenvalues = np.linalg.eigvalsh(residual_covariance)
    metrics["estimated_residual_energy"] = float(
        np.trace(residual_covariance)
    )
    metrics["estimated_positive_spectral_energy"] = float(
        eigenvalues[eigenvalues > 0].sum()
    )
    metrics["estimated_residual_effective_rank"] = float(
        np.exp(
            -np.sum(
                (positive := eigenvalues[eigenvalues > 0])
                / max(positive.sum(), 1e-12)
                * np.log(
                    positive / max(positive.sum(), 1e-12)
                )
            )
        )
        if np.any(eigenvalues > 0)
        else 0.0
    )

    oracle = np.asarray(world["truth"]["individual_response"]).reshape(
        len(splits),
        2,
        -1,
    )
    oracle = _remove_discovery_group_centers(oracle, labels, splits)
    oracle_covariance = stable_residual_covariance(
        oracle[confirmation, 0],
        oracle[confirmation, 1],
        labels[confirmation],
    )
    metrics["oracle_residual_energy"] = float(np.trace(oracle_covariance))
    oracle_norm = float(np.linalg.norm(oracle_covariance))
    if oracle_norm > 1e-12:
        alignment = float(
            np.sum(residual_covariance * oracle_covariance)
            / max(np.sum(residual_covariance**2), 1e-12)
        )
        metrics["residual_covariance_aligned_error"] = float(
            np.linalg.norm(
                alignment * residual_covariance - oracle_covariance
            )
            / oracle_norm
        )
    else:
        metrics["residual_covariance_aligned_error"] = float("nan")

    geometry = _predictive_geometry(
        score[discovery, 0],
        score[discovery, 1],
        score[calibration, 0],
        score[calibration, 1],
        score[confirmation, 0],
        score[confirmation, 1],
        seed=seed,
    )
    metrics.update(geometry)
    t = np.asarray(world["truth"]["manifold_t"])[confirmation]
    t_geometry = np.column_stack([
        np.cos(2.0 * np.pi * t),
        np.sin(2.0 * np.pi * t),
        t - 0.5,
    ])
    metrics["continuous_distance_spearman"] = float(
        spearmanr(
            pdist(t_geometry),
            pdist(author_mean[confirmation]),
        ).statistic
    )

    metrics["cross_observer_within_auc"] = float("nan")
    if audit_world is not None:
        audit = fit_c2_pipeline(
            audit_world,
            cell_mean_key="fixed_mean",
            ridge_candidates=ridge_candidates,
        )
        if audit["status"] == "C2_ESTIMATE_READY":
            audit_score = np.asarray(audit["standardized"], dtype=float)
            cross = pairing_auc_metrics(
                score[confirmation].mean(axis=1),
                audit_score[confirmation].mean(axis=1),
                labels[confirmation],
            )
            metrics["cross_observer_within_auc"] = cross[
                "author_within_group_auc"
            ]
    return {
        "status": "EPSILON_HIERARCHY_EVALUATED",
        "numeric_output": True,
        "selected_ridge": float(estimate["selected_ridge"]),
        **metrics,
    }
