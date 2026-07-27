"""Independent audits for SUICA M3 two-phase microkernel estimates."""
from __future__ import annotations

from dataclasses import fields, replace

import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import rankdata, spearmanr

from .m3_kernel_contracts import (
    M3KernelDesign,
    M3KernelEstimate,
    M3KernelObserved,
    M3KernelTruth,
)
from .m3_kernel_estimator import (
    estimate_choice_dynamics,
    fit_m3_kernel,
)


def _correlation(left: np.ndarray, right: np.ndarray) -> float:
    first = np.asarray(left, dtype=float).ravel()
    second = np.asarray(right, dtype=float).ravel()
    mask = np.isfinite(first) & np.isfinite(second)
    if mask.sum() < 3:
        return float("nan")
    first = first[mask]
    second = second[mask]
    if np.std(first) <= 1e-12 or np.std(second) <= 1e-12:
        return float("nan")
    return float(np.corrcoef(first, second)[0, 1])


def _distance_spearman(left: np.ndarray, right: np.ndarray) -> float:
    first = pdist(np.asarray(left, dtype=float).reshape(len(left), -1))
    second = pdist(np.asarray(right, dtype=float).reshape(len(right), -1))
    mask = np.isfinite(first) & np.isfinite(second)
    if mask.sum() < 3:
        return float("nan")
    if np.std(first[mask]) <= 1e-12 or np.std(second[mask]) <= 1e-12:
        return float("nan")
    return float(spearmanr(first[mask], second[mask]).statistic)


def _nrmse(estimate: np.ndarray, truth: np.ndarray) -> float:
    observed = np.asarray(estimate, dtype=float)
    target = np.asarray(truth, dtype=float)
    mask = np.isfinite(observed) & np.isfinite(target)
    if not mask.any():
        return float("nan")
    rmse = float(np.sqrt(np.mean((observed[mask] - target[mask]) ** 2)))
    scale = float(np.sqrt(np.mean(target[mask] ** 2)))
    return rmse / max(scale, 1e-12)


def _same_author_auc(
    train_representation: np.ndarray,
    test_representation: np.ndarray,
) -> float:
    train = np.asarray(train_representation, dtype=float).reshape(
        len(train_representation),
        -1,
    )
    test = np.asarray(test_representation, dtype=float).reshape(
        len(test_representation),
        -1,
    )
    finite_columns = (
        np.isfinite(train).all(axis=0)
        & np.isfinite(test).all(axis=0)
    )
    train = train[:, finite_columns]
    test = test[:, finite_columns]
    if train.shape[1] == 0 or len(train) < 2:
        return float("nan")
    center = train.mean(axis=0)
    scale = train.std(axis=0)
    scale[scale < 1e-8] = 1.0
    train = (train - center) / scale
    test = (test - center) / scale
    scores = -np.sum(
        (train[:, None] - test[None]) ** 2,
        axis=2,
    )
    labels = np.eye(len(train), dtype=bool).ravel()
    score = scores.ravel()
    ranks = rankdata(score, method="average")
    positives = int(labels.sum())
    negatives = int((~labels).sum())
    rank_sum = float(ranks[labels].sum())
    return (
        rank_sum - positives * (positives + 1) / 2.0
    ) / (positives * negatives)


def _empirical_test_field(observed: M3KernelObserved) -> np.ndarray:
    author = np.nanmean(observed.fixed_test, axis=(1, 3))
    reference = np.nanmean(
        observed.reference_test,
        axis=(0, 1, 3),
    )
    return author - reference[None]


def audit_m3_kernel_truth(
    estimate: M3KernelEstimate,
    truth: M3KernelTruth,
    observed: M3KernelObserved,
    design: M3KernelDesign,
) -> dict[str, float | int | str]:
    """Compare estimates to oracle projections without exposing truth to fit."""
    metrics: dict[str, float | int | str] = {
        "response_status": estimate.response_status,
        "state_status": estimate.state_status,
        "reliability_status": estimate.reliability_status,
        "coarse_status": estimate.coarse_status,
        "support_rank": int(estimate.support_rank),
        "common_condition_count": int(len(estimate.common_conditions)),
        "occupancy_correlation": _correlation(
            estimate.choice_stationary,
            truth.choice_stationary,
        ),
        "transition_correlation": _correlation(
            estimate.choice_transition,
            truth.choice_transition,
        ),
        "heldout_occupancy_skill": float(
            estimate.heldout_occupancy_skill
        ),
        "heldout_transition_skill": float(
            estimate.heldout_transition_skill
        ),
        "shuffled_transition_skill": float(
            estimate.shuffled_transition_skill
        ),
        "transition_order_gain": float(
            estimate.heldout_transition_skill
            - estimate.shuffled_transition_skill
        ),
        "heldout_personal_transition_skill": float(
            estimate.heldout_personal_transition_skill
        ),
        "heldout_shared_transition_skill": float(
            estimate.heldout_shared_transition_skill
        ),
        "transition_prior_strength": float(
            estimate.transition_prior_strength
        ),
        "heldout_field_r2": float(estimate.heldout_field_r2),
        "heldout_linear_r2": float(estimate.heldout_linear_r2),
        "heldout_nonlinear_increment": float(
            estimate.heldout_nonlinear_increment
        ),
    }
    if estimate.response_status in {
        "RESPONSE_OK",
        "RESPONSE_OBSERVATIONAL_ONLY",
    }:
        heldout = ~np.asarray(design.train_condition_mask, dtype=bool)
        metrics.update({
            "field_correlation": _correlation(
                estimate.response_field,
                truth.response_field,
            ),
            "field_distance_spearman": _distance_spearman(
                estimate.response_field,
                truth.response_field,
            ),
            "position_correlation": _correlation(
                estimate.author_position,
                truth.author_position,
            ),
            "position_distance_spearman": _distance_spearman(
                estimate.author_position,
                truth.author_position,
            ),
            "projection_correlation": _correlation(
                estimate.response_projection,
                truth.response_projection,
            ),
            "projection_distance_spearman": _distance_spearman(
                estimate.response_projection,
                truth.response_projection,
            ),
            "nonlinear_heldout_correlation": _correlation(
                estimate.nonlinear_field[:, heldout],
                truth.nonlinear_field[:, heldout],
            ),
            "nonlinear_heldout_nrmse": _nrmse(
                estimate.nonlinear_field[:, heldout],
                truth.nonlinear_field[:, heldout],
            ),
            "same_author_response_auc": _same_author_auc(
                estimate.response_field,
                _empirical_test_field(observed),
            ),
        })
    if estimate.state_status == "STATE_WITHIN_AUTHOR_RELATIVE_OK":
        centered_truth = (
            truth.train_state_effect
            - truth.train_state_effect.mean(axis=1, keepdims=True)
        )
        metrics.update({
            "state_relative_correlation": _correlation(
                estimate.train_state_effect,
                centered_truth,
            ),
            "state_relative_nrmse": _nrmse(
                estimate.train_state_effect,
                centered_truth,
            ),
        })
    return metrics


def _transform_observed(
    observed: M3KernelObserved,
    *,
    matrix: np.ndarray | None = None,
    shift: np.ndarray | None = None,
) -> M3KernelObserved:
    def transform(values: np.ndarray) -> np.ndarray:
        output = np.asarray(values, dtype=float)
        if matrix is not None:
            output = output @ matrix.T
        if shift is not None:
            output = output + shift
        return output

    return replace(
        observed,
        fixed_train=transform(observed.fixed_train),
        fixed_test=transform(observed.fixed_test),
        reference_train=transform(observed.reference_train),
        reference_test=transform(observed.reference_test),
    )


def audit_m3_kernel_invariance(
    observed: M3KernelObserved,
    design: M3KernelDesign,
    *,
    seed: int,
) -> dict[str, float]:
    """Refit after common response rotations and translations."""
    baseline = fit_m3_kernel(observed, design)
    dimension = observed.fixed_train.shape[-1]
    rng = np.random.default_rng(seed)
    rotation = np.linalg.qr(
        rng.normal(size=(dimension, dimension))
    )[0]
    shift = rng.normal(size=dimension)
    rotated = fit_m3_kernel(
        _transform_observed(observed, matrix=rotation),
        design,
    )
    translated = fit_m3_kernel(
        _transform_observed(observed, shift=shift),
        design,
    )
    rotated_position = rotated.author_position @ rotation
    rotated_projection = np.einsum(
        "pq,uqd->upd",
        rotation.T,
        rotated.response_projection,
    )
    rotated_field = rotated.response_field @ rotation
    return {
        "rotation_position_max_abs": float(np.nanmax(np.abs(
            rotated_position - baseline.author_position
        ))),
        "rotation_projection_max_abs": float(np.nanmax(np.abs(
            rotated_projection - baseline.response_projection
        ))),
        "rotation_field_max_abs": float(np.nanmax(np.abs(
            rotated_field - baseline.response_field
        ))),
        "rotation_position_geometry": _distance_spearman(
            baseline.author_position,
            rotated.author_position,
        ),
        "rotation_projection_geometry": _distance_spearman(
            baseline.response_projection,
            rotated.response_projection,
        ),
        "translation_position_max_abs": float(np.nanmax(np.abs(
            translated.author_position - baseline.author_position
        ))),
        "translation_projection_max_abs": float(np.nanmax(np.abs(
            translated.response_projection
            - baseline.response_projection
        ))),
        "translation_field_max_abs": float(np.nanmax(np.abs(
            translated.response_field - baseline.response_field
        ))),
    }


def audit_same_occupancy_different_transition(
    *,
    seed: int,
    authors_per_group: int = 20,
    occasions: int = 8,
    events: int = 100,
    conditions: int = 6,
) -> dict[str, float]:
    """Route an exact occupancy alias through the ordered estimator."""
    rng = np.random.default_rng(seed)
    stationary = np.full(conditions, 1.0 / conditions)
    transitions = [
        (1.0 - inertia) * np.tile(stationary, (conditions, 1))
        + inertia * np.eye(conditions)
        for inertia in (0.10, 0.80)
    ]

    def draw(transition: np.ndarray, count: int) -> np.ndarray:
        output = np.empty(
            (count, occasions, events),
            dtype=np.int16,
        )
        for author in range(count):
            for occasion in range(occasions):
                output[author, occasion, 0] = rng.choice(
                    conditions,
                    p=stationary,
                )
                for event in range(1, events):
                    previous = output[author, occasion, event - 1]
                    output[author, occasion, event] = rng.choice(
                        conditions,
                        p=transition[previous],
                    )
        return output

    train = np.concatenate([
        draw(transitions[0], authors_per_group),
        draw(transitions[1], authors_per_group),
    ])
    test = np.concatenate([
        draw(transitions[0], authors_per_group),
        draw(transitions[1], authors_per_group),
    ])
    train_occupancy, train_transition = estimate_choice_dynamics(
        train,
        conditions=conditions,
    )
    test_occupancy, test_transition = estimate_choice_dynamics(
        test,
        conditions=conditions,
    )
    labels = np.repeat([0, 1], authors_per_group)
    occupancy_centroid = np.asarray([
        train_occupancy[labels == group].mean(axis=0)
        for group in (0, 1)
    ])
    transition_centroid = np.asarray([
        train_transition[labels == group].mean(axis=0)
        for group in (0, 1)
    ])
    occupancy_distance = np.asarray([
        np.linalg.norm(
            test_occupancy - occupancy_centroid[group],
            axis=1,
        )
        for group in (0, 1)
    ]).T
    transition_distance = np.asarray([
        np.linalg.norm(
            test_transition - transition_centroid[group],
            axis=(1, 2),
        )
        for group in (0, 1)
    ]).T
    return {
        "occupancy_centroid_distance": float(np.linalg.norm(
            occupancy_centroid[0] - occupancy_centroid[1]
        )),
        "transition_centroid_distance": float(np.linalg.norm(
            transition_centroid[0] - transition_centroid[1]
        )),
        "occupancy_group_accuracy": float(np.mean(
            np.argmin(occupancy_distance, axis=1) == labels
        )),
        "transition_group_accuracy": float(np.mean(
            np.argmin(transition_distance, axis=1) == labels
        )),
    }


def audit_single_occasion_state_alias(
    observed: M3KernelObserved,
    design: M3KernelDesign,
    *,
    seed: int,
) -> dict[str, float | str]:
    """Pass an exact stable/state observational alias through the estimator."""
    if observed.fixed_train.shape[1] != 1:
        raise ValueError("state alias requires exactly one train occasion")
    estimate_a = fit_m3_kernel(observed, design)
    estimate_b = fit_m3_kernel(observed, design)
    author_level = np.nanmean(
        observed.fixed_train,
        axis=(1, 2, 3),
    )
    rng = np.random.default_rng(seed)
    shift = rng.normal(size=author_level.shape)
    stable_a = author_level
    state_a = np.zeros_like(author_level)
    stable_b = author_level + shift
    state_b = -shift
    return {
        "alias_observable_error": float(np.max(np.abs(
            (stable_a + state_a) - (stable_b + state_b)
        ))),
        "alias_stable_truth_difference": float(np.sqrt(np.mean(
            (stable_a - stable_b) ** 2
        ))),
        "alias_state_truth_difference": float(np.sqrt(np.mean(
            (state_a - state_b) ** 2
        ))),
        "estimator_response_difference": float(np.nanmax(np.abs(
            estimate_a.response_field - estimate_b.response_field
        ))),
        "state_status_a": estimate_a.state_status,
        "state_status_b": estimate_b.state_status,
    }


def packet_has_hidden_kernel_fields(
    packet: M3KernelObserved | M3KernelDesign,
) -> bool:
    """Detect forbidden hidden generator concepts in estimator inputs."""
    forbidden = {
        "truth",
        "latent",
        "hidden",
        "prototype",
        "emission",
        "state_sequence",
        "world",
        "parameter",
    }
    return any(
        any(token in item.name.lower() for token in forbidden)
        for item in fields(packet)
    )
