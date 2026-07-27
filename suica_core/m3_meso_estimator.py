"""Mesoscopic estimators for the SUICA M3 foundation.

This module deliberately imports only public M3 contracts. It has no access to
the synthetic generator, planted parameters, or world labels.
"""
from __future__ import annotations

import warnings

import numpy as np

from .m3_contracts import (
    M3DesignManifest,
    M3EstimatePacket,
    M3ObservedPacket,
    validate_manifest,
)


def _choice_estimates(
    sequence: np.ndarray,
    *,
    conditions: int,
    smoothing: float,
) -> tuple[np.ndarray, np.ndarray]:
    authors = int(sequence.shape[0])
    occupancy = np.empty((authors, conditions), dtype=float)
    transition = np.empty((authors, conditions, conditions), dtype=float)
    for author in range(authors):
        counts = np.bincount(
            sequence[author],
            minlength=conditions,
        ).astype(float)
        occupancy[author] = (
            counts + float(smoothing)
        ) / (counts.sum() + conditions * float(smoothing))
        pair_counts = np.full(
            (conditions, conditions),
            float(smoothing),
        )
        for previous, current in zip(
            sequence[author, :-1],
            sequence[author, 1:],
            strict=True,
        ):
            pair_counts[int(previous), int(current)] += 1.0
        transition[author] = pair_counts / pair_counts.sum(
            axis=1,
            keepdims=True,
        )
    return occupancy, transition


def _r2(observed: np.ndarray, predicted: np.ndarray) -> float:
    truth = np.asarray(observed, dtype=float).ravel()
    estimate = np.asarray(predicted, dtype=float).ravel()
    mask = np.isfinite(truth) & np.isfinite(estimate)
    if mask.sum() < 2:
        return float("nan")
    truth = truth[mask]
    estimate = estimate[mask]
    denominator = float(np.sum((truth - truth.mean()) ** 2))
    if denominator <= 1e-12:
        return float("nan")
    return float(1.0 - np.sum((truth - estimate) ** 2) / denominator)


def _condition_means(values: np.ndarray) -> np.ndarray:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return np.nanmean(values, axis=(1, 3))


def fit_m3_meso(
    observed: M3ObservedPacket,
    manifest: M3DesignManifest,
    *,
    choice_smoothing: float = 0.5,
) -> M3EstimatePacket:
    """Estimate choice, response, nonlinear, and state mesoscopic objects."""
    validate_manifest(manifest)
    features = np.asarray(manifest.condition_features, dtype=float)
    measure = np.asarray(manifest.reference_measure, dtype=float)
    conditions, condition_dimensions = features.shape
    authors = int(observed.fixed_responses_train.shape[0])
    response_dimensions = int(observed.fixed_responses_train.shape[-1])

    choice, transition = _choice_estimates(
        np.asarray(observed.free_conditions_train, dtype=int),
        conditions=conditions,
        smoothing=choice_smoothing,
    )
    test_choice = np.asarray(observed.free_conditions_test, dtype=int)
    author_index = np.arange(authors)[:, None]
    selected_probability = choice[author_index, test_choice]
    baseline_probability = measure[test_choice]
    heldout_choice_skill = float(np.mean(
        np.log(selected_probability + 1e-12)
        - np.log(baseline_probability + 1e-12)
    ))

    with np.errstate(invalid="ignore"):
        reference_origin = np.nanmean(
            observed.reference_responses,
            axis=(0, 1, 3),
        )
    train_condition_mean = _condition_means(
        observed.fixed_responses_train
    )
    test_condition_mean = _condition_means(
        observed.fixed_responses_test
    )
    response_field = train_condition_mean - reference_origin[None]
    available = np.isfinite(response_field).all(axis=2)
    common_conditions = np.flatnonzero(available.all(axis=0))
    common_design = np.column_stack([
        np.ones(len(common_conditions)),
        features[common_conditions],
    ])
    support_rank = (
        int(np.linalg.matrix_rank(common_design))
        if len(common_conditions)
        else 0
    )
    required_rank = int(condition_dimensions + 1)

    response_status = "RESPONSE_OK"
    if not manifest.fixed_phase_randomized:
        response_status = "RESPONSE_OBSERVATIONAL_ONLY"
    if len(common_conditions) < required_rank:
        response_status = "RESPONSE_REFUSED_NO_COMMON_SUPPORT"
    elif support_rank < required_rank:
        response_status = "RESPONSE_REFUSED_RANK_DEFICIENT"

    position = np.full((authors, response_dimensions), np.nan)
    operator = np.full(
        (authors, response_dimensions, condition_dimensions),
        np.nan,
    )
    nonlinear = np.full(
        (authors, conditions, response_dimensions),
        np.nan,
    )
    state = np.full(
        (
            authors,
            observed.fixed_responses_train.shape[1],
            response_dimensions,
        ),
        np.nan,
    )
    heldout_linear = float("nan")
    heldout_full = float("nan")

    if response_status in {"RESPONSE_OK", "RESPONSE_OBSERVATIONAL_ONLY"}:
        design = np.column_stack([np.ones(conditions), features])
        gram = design.T @ (measure[:, None] * design)
        projection = np.linalg.pinv(gram) @ (
            design.T * measure[None]
        )
        coefficients = np.einsum(
            "kc,ucp->ukp",
            projection,
            response_field,
        )
        position = coefficients[:, 0]
        operator = coefficients[:, 1:].transpose(0, 2, 1)
        linear_field = np.einsum(
            "ck,ukp->ucp",
            design,
            coefficients,
        )
        nonlinear = response_field - linear_field
        full_prediction = reference_origin[None] + response_field
        linear_prediction = reference_origin[None] + linear_field
        heldout_linear = _r2(test_condition_mean, linear_prediction)
        heldout_full = _r2(test_condition_mean, full_prediction)

        occasion_mean = np.nanmean(
            observed.fixed_responses_train,
            axis=(2, 3),
        )
        fitted_occasion_origin = np.sum(
            measure[None, :, None]
            * (reference_origin[None] + response_field),
            axis=1,
        )
        state = occasion_mean - fitted_occasion_origin[:, None]
        if state.shape[1] > 1:
            state -= state.mean(axis=1, keepdims=True)

    state_status = (
        "STATE_OK"
        if observed.fixed_responses_train.shape[1] >= 2
        and response_status in {"RESPONSE_OK", "RESPONSE_OBSERVATIONAL_ONLY"}
        else "STATE_REFUSED_SINGLE_OCCASION"
        if observed.fixed_responses_train.shape[1] < 2
        else "STATE_REFUSED_RESPONSE_UNIDENTIFIED"
    )

    return M3EstimatePacket(
        choice_stationary=choice,
        choice_transition=transition,
        author_position=position,
        response_operator=operator,
        nonlinear_field=nonlinear,
        occasion_state=state,
        response_field=response_field,
        reference_origin=reference_origin,
        support_rank=support_rank,
        common_conditions=common_conditions,
        response_status=response_status,
        state_status=state_status,
        heldout_choice_log_skill=heldout_choice_skill,
        heldout_response_r2_linear=heldout_linear,
        heldout_response_r2_full=heldout_full,
    )
