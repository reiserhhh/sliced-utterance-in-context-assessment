"""Synthetic calibration worlds for V7 identifiability and error claims.

These worlds are not simulations of personality.  They make the mathematical
limits of the V7 estimators observable because the shared component, omitted
condition component, and nonlinear relation are known by construction.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge


@dataclass(frozen=True)
class IdentificationWorld:
    """One source-disjoint synthetic panel with declared latent truth."""

    name: str
    left: np.ndarray
    right: np.ndarray
    observed_context: np.ndarray
    true_shared_loading: np.ndarray | None
    rotation_error: float | None


def _orthonormal(rng: np.random.Generator, rows: int, columns: int) -> np.ndarray:
    """Return an orthonormal-column matrix with deterministic random signs."""
    matrix, _ = np.linalg.qr(rng.normal(size=(rows, columns)))
    return matrix[:, :columns]


def _zscore(values: np.ndarray) -> np.ndarray:
    """Standardize columns while preserving finite degenerate columns."""
    center = values.mean(axis=0, keepdims=True)
    scale = values.std(axis=0, keepdims=True)
    return (values - center) / np.maximum(scale, 1e-12)


def _zscore_with_scale(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Standardize columns and retain the scaling needed to transform truth."""
    center = values.mean(axis=0, keepdims=True)
    scale = np.maximum(values.std(axis=0, keepdims=True), 1e-12)
    return (values - center) / scale, scale.reshape(-1)


def _alignment_auc(left: np.ndarray, right: np.ndarray) -> float:
    """Return own-vs-stranger rank alignment, not a psychological accuracy."""
    if left.shape != right.shape or len(left) < 2:
        return float("nan")
    distance = np.linalg.norm(left[:, None, :] - right[None, :, :], axis=2)
    ranks = []
    for index in range(len(left)):
        own = distance[index, index]
        stranger = np.delete(distance[index], index)
        ranks.append(np.mean(own < stranger) + 0.5 * np.mean(own == stranger))
    return float(np.mean(ranks))


def _relative_distance_spearman(left: np.ndarray, right: np.ndarray) -> float:
    """Compare within-view pairwise geometry without assuming shared coordinates.

    A coordinate-wise comparison is invalid after an arbitrary rotation or a
    nonlinear observation map.  This statistic instead compares the rank order
    of all within-view person-pair distances.  It is still only a technical
    geometry statistic: it cannot identify a named axis or a psychological
    construct.
    """
    if left.shape[0] != right.shape[0] or len(left) < 3:
        return float("nan")
    upper = np.triu_indices(len(left), k=1)
    left_distance = np.linalg.norm(left[:, None, :] - left[None, :, :], axis=2)[upper]
    right_distance = np.linalg.norm(right[:, None, :] - right[None, :, :], axis=2)[upper]
    result = spearmanr(left_distance, right_distance)
    return float(result.statistic) if np.isfinite(result.statistic) else float("nan")


def _global_r2(target: np.ndarray, prediction: np.ndarray) -> float:
    """Return a multivariate held-out R2 with a global mean baseline."""
    denominator = float(np.sum((target - target.mean(axis=0, keepdims=True)) ** 2))
    if denominator <= 1e-12:
        return float("nan")
    return float(1.0 - np.sum((target - prediction) ** 2) / denominator)


def _ridge_holdout_r2(left: np.ndarray, right: np.ndarray, *, seed: int, alpha: float) -> float:
    """Fit a fixed linear transport map on one author subset and score another."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(left))
    split = max(8, int(round(0.65 * len(left))))
    train, test = order[:split], order[split:]
    if len(test) < 4:
        return float("nan")
    model = Ridge(alpha=float(alpha), fit_intercept=True).fit(left[train], right[train])
    return _global_r2(right[test], model.predict(left[test]))


def _projector_congruence(left: np.ndarray, right: np.ndarray, truth: np.ndarray, *, rank: int) -> float:
    """Compare a cross-view recovered loading subspace to known shared truth."""
    cross = left.T @ right / max(1, len(left))
    recovered, _, _ = np.linalg.svd(cross, full_matrices=False)
    reference, _ = np.linalg.qr(np.asarray(truth, dtype=float))
    dimension = min(int(rank), recovered.shape[1], reference.shape[1])
    if dimension < 1:
        return float("nan")
    overlap = recovered[:, :dimension].T @ reference[:, :dimension]
    return float(np.linalg.norm(overlap, ord="fro") ** 2 / dimension)


def _residualize(values: np.ndarray, context: np.ndarray, *, train_index: np.ndarray) -> np.ndarray:
    """Residualize with a train-fitted observed context surface only."""
    design = np.column_stack([np.ones(len(context)), context])
    beta, *_ = np.linalg.lstsq(design[train_index], values[train_index], rcond=None)
    return values - design @ beta


def _shared_world(
    rng: np.random.Generator,
    *,
    persons: int,
    features: int,
    shared_rank: int,
    context_rank: int,
    noise_scale: float,
    shared_strength: float,
) -> IdentificationWorld:
    shared = rng.normal(size=(persons, shared_rank))
    loading = _orthonormal(rng, features, shared_rank)
    observed_context = rng.normal(size=(persons, context_rank))
    context_loading = rng.normal(scale=0.35, size=(context_rank, features))
    left = shared_strength * shared @ loading.T + observed_context @ context_loading
    right = shared_strength * shared @ loading.T + observed_context @ context_loading
    left += rng.normal(scale=noise_scale, size=left.shape)
    right += rng.normal(scale=noise_scale, size=right.shape)
    standardized_left, left_scale = _zscore_with_scale(left)
    standardized_right, _ = _zscore_with_scale(right)
    # The estimator operates on standardized feature coordinates. The recovery
    # truth must therefore be D_left^{-1} Lambda, not the raw loading Lambda.
    standardized_loading = shared_strength * loading / left_scale[:, None]
    return IdentificationWorld("shared_linear", standardized_left, standardized_right, observed_context, standardized_loading, None)


def _null_world(
    rng: np.random.Generator,
    *,
    persons: int,
    features: int,
    context_rank: int,
    noise_scale: float,
) -> IdentificationWorld:
    observed_context = rng.normal(size=(persons, context_rank))
    left = rng.normal(scale=noise_scale, size=(persons, features))
    right = rng.normal(scale=noise_scale, size=(persons, features))
    return IdentificationWorld("null", _zscore(left), _zscore(right), observed_context, None, None)


def _axis_rotation_world(rng: np.random.Generator, *, persons: int, features: int, shared_rank: int) -> IdentificationWorld:
    """Construct two exactly equivalent parameterizations of one observation."""
    shared = rng.normal(size=(persons, shared_rank))
    loading = rng.normal(size=(features, shared_rank))
    rotation = _orthonormal(rng, shared_rank, shared_rank)
    original = shared @ loading.T
    rotated = (shared @ rotation) @ (loading @ rotation).T
    return IdentificationWorld(
        "axis_rotation_equivalence",
        _zscore(original),
        _zscore(rotated),
        np.zeros((persons, 1)),
        loading,
        float(np.max(np.abs(original - rotated))),
    )


def _nonlinear_metric_world(
    rng: np.random.Generator,
    *,
    persons: int,
    features: int,
    shared_rank: int,
    noise_scale: float,
) -> IdentificationWorld:
    """Retain partial relative geometry while making fixed linear transport fail.

    The fifth-power map is deliberately odd and monotone.  It retains a common
    latent source and weak distance ordering, but its linear projection from the
    left observation is poor.  This demonstrates a boundary: poor linear
    transport does not prove absence of a shared latent relation.
    """
    shared = rng.normal(size=(persons, shared_rank))
    loading = _orthonormal(rng, features, shared_rank)
    base = shared @ loading.T
    left = base + rng.normal(scale=noise_scale, size=base.shape)
    right = np.sign(base) * np.abs(base) ** 5 + rng.normal(scale=noise_scale, size=base.shape)
    return IdentificationWorld(
        "nonlinear_metric_without_linear_coordinate",
        _zscore(left),
        _zscore(right),
        rng.normal(size=(persons, 1)),
        None,
        None,
    )


def _omitted_context_world(
    rng: np.random.Generator,
    *,
    persons: int,
    features: int,
    observed_context_rank: int,
    omitted_context_rank: int,
    noise_scale: float,
) -> IdentificationWorld:
    """Show that an omitted persistent condition can mimic residual author structure."""
    observed = rng.normal(size=(persons, observed_context_rank))
    omitted = rng.normal(size=(persons, omitted_context_rank))
    observed_loading = rng.normal(scale=0.35, size=(observed_context_rank, features))
    omitted_loading = rng.normal(scale=1.0, size=(omitted_context_rank, features))
    common = observed @ observed_loading + omitted @ omitted_loading
    left = common + rng.normal(scale=noise_scale, size=common.shape)
    right = common + rng.normal(scale=noise_scale, size=common.shape)
    return IdentificationWorld("omitted_context_counterexample", _zscore(left), _zscore(right), observed, None, None)


def _endogenous_context_overadjustment_world(
    rng: np.random.Generator,
    *,
    persons: int,
    features: int,
    shared_rank: int,
    context_rank: int,
    noise_scale: float,
) -> IdentificationWorld:
    """Show that residualizing a selected context can remove shared structure.

    Here observed context is partly generated by the same latent source as the
    shared component. It is a counterexample to an unconditional "always
    residualize context" policy, not a causal model of natural language.
    """
    shared = rng.normal(size=(persons, shared_rank))
    relation = rng.normal(size=(shared_rank, context_rank))
    observed = shared @ relation + rng.normal(scale=0.25, size=(persons, context_rank))
    loading = _orthonormal(rng, features, shared_rank)
    # The recorded context is a descendant/proxy of shared structure here. It
    # has no separate generative contribution to the observations, so treating
    # it as a nuisance surface removes rather than clarifies shared signal.
    left = shared @ loading.T + rng.normal(scale=noise_scale, size=(persons, features))
    right = shared @ loading.T + rng.normal(scale=noise_scale, size=(persons, features))
    standardized_left, left_scale = _zscore_with_scale(left)
    standardized_right, _ = _zscore_with_scale(right)
    return IdentificationWorld(
        "endogenous_context_overadjustment_counterexample",
        standardized_left,
        standardized_right,
        observed,
        loading / left_scale[:, None],
        None,
    )


def _measurement_error_context_world(
    rng: np.random.Generator,
    *,
    persons: int,
    features: int,
    context_rank: int,
    noise_scale: float,
) -> IdentificationWorld:
    """Show residual shared alignment can remain after noisy context measurement."""
    true_context = rng.normal(size=(persons, context_rank))
    observed = true_context + rng.normal(scale=2.0, size=(persons, context_rank))
    loading = rng.normal(size=(context_rank, features))
    common = true_context @ loading
    left = common + rng.normal(scale=noise_scale, size=(persons, features))
    right = common + rng.normal(scale=noise_scale, size=(persons, features))
    return IdentificationWorld("measurement_error_context_counterexample", _zscore(left), _zscore(right), observed, None, None)


def _view_private_structure_world(
    rng: np.random.Generator,
    *,
    persons: int,
    features: int,
    shared_rank: int,
    noise_scale: float,
) -> IdentificationWorld:
    """Mix true shared geometry with view-private geometry of equal magnitude."""
    shared = rng.normal(size=(persons, shared_rank))
    private_left = rng.normal(size=(persons, shared_rank))
    private_right = rng.normal(size=(persons, shared_rank))
    shared_loading = _orthonormal(rng, features, shared_rank)
    left_loading = _orthonormal(rng, features, shared_rank)
    right_loading = _orthonormal(rng, features, shared_rank)
    left = shared @ shared_loading.T + private_left @ left_loading.T + rng.normal(scale=noise_scale, size=(persons, features))
    right = shared @ shared_loading.T + private_right @ right_loading.T + rng.normal(scale=noise_scale, size=(persons, features))
    standardized_left, left_scale = _zscore_with_scale(left)
    standardized_right, _ = _zscore_with_scale(right)
    return IdentificationWorld(
        "view_private_structure_sensitivity",
        standardized_left,
        standardized_right,
        rng.normal(size=(persons, 1)),
        shared_loading / left_scale[:, None],
        None,
    )


def generate_world(kind: str, *, seed: int, persons: int, features: int, shared_rank: int, context_rank: int, noise_scale: float) -> IdentificationWorld:
    """Generate one declared synthetic world for the V7 identification matrix."""
    rng = np.random.default_rng(seed)
    if kind == "shared_linear":
        return _shared_world(
            rng, persons=persons, features=features, shared_rank=shared_rank,
            context_rank=context_rank, noise_scale=noise_scale, shared_strength=1.0,
        )
    if kind == "null":
        return _null_world(rng, persons=persons, features=features, context_rank=context_rank, noise_scale=noise_scale)
    if kind == "axis_rotation_equivalence":
        return _axis_rotation_world(rng, persons=persons, features=features, shared_rank=shared_rank)
    if kind == "nonlinear_metric_without_linear_coordinate":
        return _nonlinear_metric_world(
            rng, persons=persons, features=features, shared_rank=shared_rank, noise_scale=noise_scale,
        )
    if kind == "omitted_context_counterexample":
        return _omitted_context_world(
            rng, persons=persons, features=features, observed_context_rank=context_rank,
            omitted_context_rank=max(1, shared_rank), noise_scale=noise_scale,
        )
    if kind == "endogenous_context_overadjustment_counterexample":
        return _endogenous_context_overadjustment_world(
            rng, persons=persons, features=features, shared_rank=shared_rank,
            context_rank=context_rank, noise_scale=noise_scale,
        )
    if kind == "measurement_error_context_counterexample":
        return _measurement_error_context_world(
            rng, persons=persons, features=features, context_rank=context_rank,
            noise_scale=noise_scale,
        )
    if kind == "view_private_structure_sensitivity":
        return _view_private_structure_world(
            rng, persons=persons, features=features, shared_rank=shared_rank,
            noise_scale=noise_scale,
        )
    raise ValueError(f"Unknown V7 identification world: {kind}")


def evaluate_world(world: IdentificationWorld, *, seed: int, shared_rank: int, ridge_alpha: float = 10.0) -> dict[str, float | str]:
    """Evaluate technical estimators against known synthetic world properties."""
    left, right = world.left, world.right
    rng = np.random.default_rng(seed)
    train = rng.permutation(len(left))[: max(8, int(round(0.65 * len(left))))]
    residual_left = _residualize(left, world.observed_context, train_index=train)
    residual_right = _residualize(right, world.observed_context, train_index=train)
    result: dict[str, float | str] = {
        "world": world.name,
        "alignment_auc": _alignment_auc(left, right),
        "relative_distance_spearman": _relative_distance_spearman(left, right),
        "linear_transport_r2": _ridge_holdout_r2(left, right, seed=seed + 7, alpha=ridge_alpha),
        "residual_alignment_auc": _alignment_auc(residual_left, residual_right),
        "rotation_max_abs_error": float(world.rotation_error) if world.rotation_error is not None else float("nan"),
    }
    result["raw_subspace_congruence"] = (
        _projector_congruence(left, right, world.true_shared_loading, rank=shared_rank)
        if world.true_shared_loading is not None else float("nan")
    )
    result["context_adjusted_subspace_congruence"] = (
        _projector_congruence(residual_left, residual_right, world.true_shared_loading, rank=shared_rank)
        if world.true_shared_loading is not None else float("nan")
    )
    return result


def run_identification_matrix(config: dict[str, Any]) -> list[dict[str, float | str]]:
    """Run all configured worlds and repetitions without any human-text input."""
    rows: list[dict[str, float | str]] = []
    seed = int(config["seed"])
    for world_index, kind in enumerate(config["worlds"]):
        for repetition in range(int(config["repetitions"])):
            trial_seed = seed + 10_000 * world_index + repetition
            world = generate_world(
                str(kind), seed=trial_seed, persons=int(config["persons"]), features=int(config["features"]),
                shared_rank=int(config["shared_rank"]), context_rank=int(config["context_rank"]),
                noise_scale=float(config["noise_scale"]),
            )
            row = evaluate_world(world, seed=trial_seed, shared_rank=int(config["shared_rank"]), ridge_alpha=float(config["ridge_alpha"]))
            row["repetition"] = repetition
            rows.append(row)
    return rows
