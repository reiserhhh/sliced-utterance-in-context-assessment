"""Basis-blinded estimators for the SUICA M3 two-phase microkernel battery.

This module imports only the public microkernel contracts. It never imports
the synthetic generator or receives hidden states, emission codes, prototypes,
or random-Fourier features.
"""
from __future__ import annotations

import warnings

import numpy as np

from .m3_kernel_contracts import (
    M3KernelDesign,
    M3KernelEstimate,
    M3KernelObserved,
    validate_kernel_design,
)


def _safe_nanmean(values: np.ndarray, axis: tuple[int, ...]) -> np.ndarray:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return np.nanmean(values, axis=axis)


def _r2(observed: np.ndarray, predicted: np.ndarray) -> float:
    truth = np.asarray(observed, dtype=float).ravel()
    estimate = np.asarray(predicted, dtype=float).ravel()
    mask = np.isfinite(truth) & np.isfinite(estimate)
    if mask.sum() < 3:
        return float("nan")
    truth = truth[mask]
    estimate = estimate[mask]
    denominator = float(np.sum((truth - truth.mean()) ** 2))
    if denominator <= 1e-12:
        return float("nan")
    return float(
        1.0 - np.sum((truth - estimate) ** 2) / denominator
    )


def estimate_choice_dynamics(
    sequence: np.ndarray,
    *,
    conditions: int,
    smoothing: float = 0.5,
) -> tuple[np.ndarray, np.ndarray]:
    """Estimate occupancy and ordered transition kernels by author.

    Occasion boundaries are respected: no transition is counted between the
    last event of one occasion and the first event of the next.
    """
    values = np.asarray(sequence, dtype=int)
    if values.ndim != 3:
        raise ValueError("choice sequence must be author x occasion x event")
    authors = values.shape[0]
    occupancy = np.empty((authors, conditions), dtype=float)
    transition = np.empty(
        (authors, conditions, conditions),
        dtype=float,
    )
    for author in range(authors):
        counts = np.bincount(
            values[author].ravel(),
            minlength=conditions,
        ).astype(float)
        occupancy[author] = (
            counts + smoothing
        ) / (counts.sum() + smoothing * conditions)
        pairs = np.full(
            (conditions, conditions),
            float(smoothing),
        )
        for occasion in values[author]:
            np.add.at(pairs, (occasion[:-1], occasion[1:]), 1.0)
        transition[author] = pairs / pairs.sum(axis=1, keepdims=True)
    return occupancy, transition


def _pooled_choice_dynamics(
    sequence: np.ndarray,
    *,
    conditions: int,
    smoothing: float,
) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(sequence, dtype=int)
    counts = np.bincount(
        values.ravel(),
        minlength=conditions,
    ).astype(float)
    occupancy = (
        counts + smoothing
    ) / (counts.sum() + smoothing * conditions)
    pairs = np.full((conditions, conditions), float(smoothing))
    for author in values:
        for occasion in author:
            np.add.at(pairs, (occasion[:-1], occasion[1:]), 1.0)
    return occupancy, pairs / pairs.sum(axis=1, keepdims=True)


def _transition_counts(
    sequence: np.ndarray,
    *,
    conditions: int,
) -> np.ndarray:
    values = np.asarray(sequence, dtype=int)
    counts = np.zeros(
        (values.shape[0], conditions, conditions),
        dtype=float,
    )
    for author in range(values.shape[0]):
        for occasion in values[author]:
            np.add.at(
                counts[author],
                (occasion[:-1], occasion[1:]),
                1.0,
            )
    return counts


def _hierarchical_transition(
    counts: np.ndarray,
    *,
    prior_strength: float,
    smoothing: float = 0.01,
) -> tuple[np.ndarray, np.ndarray]:
    """Shrink sparse author transitions toward a pooled transition kernel."""
    conditions = counts.shape[-1]
    pooled = counts.sum(axis=0) + 0.5
    pooled /= pooled.sum(axis=1, keepdims=True)
    transition = (
        counts
        + float(prior_strength) * pooled[None]
        + float(smoothing)
    ) / (
        counts.sum(axis=2, keepdims=True)
        + float(prior_strength)
        + float(smoothing) * conditions
    )
    return transition, pooled


def _personal_transition_skill(
    test: np.ndarray,
    author_transition: np.ndarray,
    pooled_transition: np.ndarray,
) -> float:
    scores: list[np.ndarray] = []
    for author in range(test.shape[0]):
        previous = test[author, :, :-1]
        current = test[author, :, 1:]
        scores.append(
            np.log(
                author_transition[author, previous, current] + 1e-12
            )
            - np.log(pooled_transition[previous, current] + 1e-12)
        )
    return float(np.mean(np.concatenate([
        item.ravel()
        for item in scores
    ])))


def _shared_transition_skill(
    test: np.ndarray,
    pooled_transition: np.ndarray,
    pooled_occupancy: np.ndarray,
) -> float:
    scores: list[np.ndarray] = []
    for author in range(test.shape[0]):
        previous = test[author, :, :-1]
        current = test[author, :, 1:]
        scores.append(
            np.log(pooled_transition[previous, current] + 1e-12)
            - np.log(pooled_occupancy[current] + 1e-12)
        )
    return float(np.mean(np.concatenate([
        item.ravel()
        for item in scores
    ])))


def _select_transition_prior(
    sequence: np.ndarray,
    *,
    conditions: int,
) -> float:
    """Choose population shrinkage by held-out training occasions only."""
    values = np.asarray(sequence, dtype=int)
    if values.shape[1] < 2:
        return 10_000.0
    candidates = (0.0, 5.0, 20.0, 100.0, 500.0, 2_000.0, 10_000.0)
    scores = np.empty(len(candidates), dtype=float)
    for index, strength in enumerate(candidates):
        fold_scores: list[float] = []
        for heldout in range(values.shape[1]):
            train = np.delete(values, heldout, axis=1)
            transition, pooled = _hierarchical_transition(
                _transition_counts(train, conditions=conditions),
                prior_strength=strength,
            )
            fold_scores.append(_personal_transition_skill(
                values[:, heldout:heldout + 1],
                transition,
                pooled,
            ))
        scores[index] = float(np.mean(fold_scores))
    return float(candidates[int(np.argmax(scores))])


def _occupancy_skill(
    test: np.ndarray,
    author_probability: np.ndarray,
    pooled_probability: np.ndarray,
) -> float:
    authors = test.shape[0]
    selected = author_probability[
        np.arange(authors)[:, None, None],
        test,
    ]
    baseline = pooled_probability[test]
    return float(np.mean(
        np.log(selected + 1e-12) - np.log(baseline + 1e-12)
    ))


def _transition_skill(
    test: np.ndarray,
    author_transition: np.ndarray,
    occupancy_baseline: np.ndarray,
) -> float:
    """Conditional order skill beyond each author's marginal occupancy."""
    scores: list[np.ndarray] = []
    for author in range(test.shape[0]):
        previous = test[author, :, :-1]
        current = test[author, :, 1:]
        selected = author_transition[author, previous, current]
        baseline = occupancy_baseline[author, current]
        scores.append(
            np.log(selected + 1e-12) - np.log(baseline + 1e-12)
        )
    return float(np.mean(np.concatenate([
        item.ravel()
        for item in scores
    ])))


def _shuffled_sequences(sequence: np.ndarray) -> np.ndarray:
    """Break ordering while preserving each occasion's occupancy exactly."""
    values = np.asarray(sequence, dtype=int)
    shuffled = np.empty_like(values)
    rng = np.random.default_rng(73_921)
    for author in range(values.shape[0]):
        for occasion in range(values.shape[1]):
            shuffled[author, occasion] = values[
                author,
                occasion,
                rng.permutation(values.shape[2]),
            ]
    return shuffled


def _common_support(
    observed: M3KernelObserved,
    design: M3KernelDesign,
) -> np.ndarray:
    author_mean = _safe_nanmean(observed.fixed_train, axis=(1, 3))
    reference_mean = _safe_nanmean(
        observed.reference_train,
        axis=(0, 1, 3),
    )
    available = (
        np.isfinite(author_mean).all(axis=2).all(axis=0)
        & np.isfinite(reference_mean).all(axis=1)
        & np.asarray(design.train_condition_mask, dtype=bool)
    )
    return np.flatnonzero(available)


def _response_status(
    design: M3KernelDesign,
    *,
    common_conditions: np.ndarray,
    support_rank: int,
) -> str:
    required_rank = design.condition_coordinates.shape[1] + 1
    if (
        design.train_representation_version
        != design.test_representation_version
    ):
        return "RESPONSE_REFUSED_REPRESENTATION_VERSION"
    if design.train_reference_version != design.test_reference_version:
        return "RESPONSE_REFUSED_REFERENCE_VERSION"
    if design.missingness_mechanism == "UNKNOWN":
        return "RESPONSE_REFUSED_UNKNOWN_MISSINGNESS"
    if len(common_conditions) < required_rank + 1:
        return "RESPONSE_REFUSED_NO_COMMON_SUPPORT"
    if support_rank < required_rank:
        return "RESPONSE_REFUSED_RANK_DEFICIENT"
    if not design.fixed_phase_randomized:
        return "RESPONSE_OBSERVATIONAL_ONLY"
    return "RESPONSE_OK"


def _rbf_kernel(
    left: np.ndarray,
    right: np.ndarray,
    *,
    bandwidth: float,
) -> np.ndarray:
    distance = np.sum(
        (left[:, None] - right[None]) ** 2,
        axis=2,
    )
    return np.exp(-distance / (2.0 * bandwidth ** 2))


def _fixed_bandwidth(coordinates: np.ndarray) -> float:
    distance = np.sqrt(np.sum(
        (coordinates[:, None] - coordinates[None]) ** 2,
        axis=2,
    ))
    positive = distance[distance > 1e-12]
    if not len(positive):
        return 1.0
    return max(float(np.median(positive)), 1e-6)


def _rbf_predict(
    train_coordinates: np.ndarray,
    target_coordinates: np.ndarray,
    response: np.ndarray,
    *,
    bandwidth: float,
    ridge: float,
) -> np.ndarray:
    """Fit a fixed-bandwidth kernel ridge surface for each author/output."""
    kernel = _rbf_kernel(
        train_coordinates,
        train_coordinates,
        bandwidth=bandwidth,
    )
    regularized = kernel + float(ridge) * np.eye(len(kernel))
    coefficients = np.linalg.solve(
        regularized,
        response.transpose(1, 0, 2).reshape(len(kernel), -1),
    )
    predicted = _rbf_kernel(
        target_coordinates,
        train_coordinates,
        bandwidth=bandwidth,
    ) @ coefficients
    return predicted.reshape(
        len(target_coordinates),
        response.shape[0],
        response.shape[2],
    ).transpose(1, 0, 2)


def _select_rbf_hyperparameters(
    coordinates: np.ndarray,
    response: np.ndarray,
) -> tuple[float, float]:
    """Select smoothing using leave-one-condition-out training error only."""
    base_bandwidth = _fixed_bandwidth(coordinates)
    candidates = [
        (base_bandwidth * multiplier, ridge)
        for multiplier in (0.35, 0.60, 1.0, 1.8, 3.0)
        for ridge in (0.01, 0.10, 0.50, 1.50)
    ]
    best = candidates[0]
    best_error = float("inf")
    for bandwidth, ridge in candidates:
        squared_error = 0.0
        count = 0
        for heldout in range(len(coordinates)):
            keep = np.arange(len(coordinates)) != heldout
            predicted = _rbf_predict(
                coordinates[keep],
                coordinates[[heldout]],
                response[:, keep],
                bandwidth=bandwidth,
                ridge=ridge,
            )
            difference = predicted[:, 0] - response[:, heldout]
            squared_error += float(np.sum(difference ** 2))
            count += int(difference.size)
        error = squared_error / max(count, 1)
        if error < best_error:
            best_error = error
            best = (bandwidth, ridge)
    return best


def _linear_predict(
    train_coordinates: np.ndarray,
    target_coordinates: np.ndarray,
    response: np.ndarray,
) -> np.ndarray:
    train_design = np.column_stack([
        np.ones(len(train_coordinates)),
        train_coordinates,
    ])
    target_design = np.column_stack([
        np.ones(len(target_coordinates)),
        target_coordinates,
    ])
    coefficients = np.einsum(
        "kc,ucp->ukp",
        np.linalg.pinv(train_design),
        response,
    )
    return np.einsum("ck,ukp->ucp", target_design, coefficients)


def _project_field(
    field: np.ndarray,
    coordinates: np.ndarray,
    measure: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    design = np.column_stack([np.ones(len(coordinates)), coordinates])
    projection = np.linalg.pinv(
        design.T @ (measure[:, None] * design)
    ) @ (design.T * measure[None])
    coefficients = np.einsum("kc,ucp->ukp", projection, field)
    fitted = np.einsum("ck,ukp->ucp", design, coefficients)
    return (
        coefficients[:, 0],
        coefficients[:, 1:].transpose(0, 2, 1),
        field - fitted,
    )


def fit_m3_kernel(
    observed: M3KernelObserved,
    design: M3KernelDesign,
    *,
    choice_smoothing: float = 0.5,
    response_ridge: float = 0.15,
) -> M3KernelEstimate:
    """Estimate mesoscopic objects from event observations only."""
    validate_kernel_design(design)
    coordinates = np.asarray(design.condition_coordinates, dtype=float)
    measure = np.asarray(design.reference_measure, dtype=float)
    conditions = len(coordinates)
    authors = observed.choice_train.shape[0]
    dimensions = observed.fixed_train.shape[-1]

    occupancy, _ = estimate_choice_dynamics(
        observed.choice_train,
        conditions=conditions,
        smoothing=choice_smoothing,
    )
    pooled_occupancy, _ = _pooled_choice_dynamics(
        observed.choice_train,
        conditions=conditions,
        smoothing=choice_smoothing,
    )
    transition_prior = _select_transition_prior(
        observed.choice_train,
        conditions=conditions,
    )
    transition, pooled_transition = _hierarchical_transition(
        _transition_counts(
            observed.choice_train,
            conditions=conditions,
        ),
        prior_strength=transition_prior,
    )
    occupancy_skill = _occupancy_skill(
        observed.choice_test,
        occupancy,
        pooled_occupancy,
    )
    transition_skill = _transition_skill(
        observed.choice_test,
        transition,
        occupancy,
    )
    shuffled_skill = _transition_skill(
        _shuffled_sequences(observed.choice_test),
        transition,
        occupancy,
    )
    personal_transition_skill = _personal_transition_skill(
        observed.choice_test,
        transition,
        pooled_transition,
    )
    shared_transition_skill = _shared_transition_skill(
        observed.choice_test,
        pooled_transition,
        pooled_occupancy,
    )

    common = _common_support(observed, design)
    public_design = np.column_stack([
        np.ones(len(common)),
        coordinates[common],
    ])
    support_rank = (
        int(np.linalg.matrix_rank(public_design))
        if len(common)
        else 0
    )
    response_status = _response_status(
        design,
        common_conditions=common,
        support_rank=support_rank,
    )

    response_field = np.full(
        (authors, conditions, dimensions),
        np.nan,
    )
    position = np.full((authors, dimensions), np.nan)
    response_projection = np.full(
        (authors, dimensions, coordinates.shape[1]),
        np.nan,
    )
    nonlinear = np.full_like(response_field, np.nan)
    state = np.full(
        (
            authors,
            observed.fixed_train.shape[1],
            dimensions,
        ),
        np.nan,
    )
    heldout_field_r2 = float("nan")
    heldout_linear_r2 = float("nan")
    heldout_increment = float("nan")

    estimable = response_status in {
        "RESPONSE_OK",
        "RESPONSE_OBSERVATIONAL_ONLY",
    }
    if estimable:
        author_train = _safe_nanmean(
            observed.fixed_train,
            axis=(1, 3),
        )
        reference_train = _safe_nanmean(
            observed.reference_train,
            axis=(0, 1, 3),
        )
        train_field = (
            author_train[:, common]
            - reference_train[None, common]
        )
        bandwidth, selected_ridge = _select_rbf_hyperparameters(
            coordinates[common],
            train_field,
        )
        response_field = _rbf_predict(
            coordinates[common],
            coordinates,
            train_field,
            bandwidth=bandwidth,
            ridge=selected_ridge * response_ridge / 0.15,
        )
        linear_field = _linear_predict(
            coordinates[common],
            coordinates,
            train_field,
        )
        position, response_projection, nonlinear = _project_field(
            response_field,
            coordinates,
            measure,
        )

        author_test = _safe_nanmean(
            observed.fixed_test,
            axis=(1, 3),
        )
        reference_test = _safe_nanmean(
            observed.reference_test,
            axis=(0, 1, 3),
        )
        test_field = author_test - reference_test[None]
        heldout = ~np.asarray(design.train_condition_mask, dtype=bool)
        if not heldout.any():
            heldout = np.ones(conditions, dtype=bool)
        heldout_field_r2 = _r2(
            test_field[:, heldout],
            response_field[:, heldout],
        )
        heldout_linear_r2 = _r2(
            test_field[:, heldout],
            linear_field[:, heldout],
        )
        heldout_increment = heldout_field_r2 - heldout_linear_r2

        occasion = _safe_nanmean(observed.fixed_train, axis=(3,))
        residual = (
            occasion[:, :, common]
            - author_train[:, None, common]
        )
        q_common = measure[common] / measure[common].sum()
        state = np.einsum("c,uocp->uop", q_common, residual)
        if state.shape[1] > 1:
            state -= state.mean(axis=1, keepdims=True)

    if observed.fixed_train.shape[1] < 2:
        state_status = "STATE_REFUSED_SINGLE_OCCASION"
    elif not estimable:
        state_status = "STATE_REFUSED_RESPONSE_UNIDENTIFIED"
    else:
        state_status = "STATE_WITHIN_AUTHOR_RELATIVE_OK"
    reliability_status = (
        "RELIABILITY_OK"
        if design.technical_streams_independent
        else "RELIABILITY_REFUSED_TECHNICAL_DEPENDENCE"
    )
    coarse_status = (
        "COARSE_INVARIANCE_ELIGIBLE"
        if design.coarse_blocks_condition_homogeneous
        else "COARSE_INVARIANCE_REFUSED_MIXED_CONDITIONS"
    )

    return M3KernelEstimate(
        choice_stationary=occupancy,
        choice_transition=transition,
        response_field=response_field,
        author_position=position,
        response_projection=response_projection,
        nonlinear_field=nonlinear,
        train_state_effect=state,
        response_status=response_status,
        state_status=state_status,
        reliability_status=reliability_status,
        coarse_status=coarse_status,
        common_conditions=common,
        support_rank=support_rank,
        heldout_occupancy_skill=occupancy_skill,
        heldout_transition_skill=transition_skill,
        shuffled_transition_skill=shuffled_skill,
        heldout_personal_transition_skill=personal_transition_skill,
        heldout_shared_transition_skill=shared_transition_skill,
        transition_prior_strength=transition_prior,
        heldout_field_r2=heldout_field_r2,
        heldout_linear_r2=heldout_linear_r2,
        heldout_nonlinear_increment=heldout_increment,
    )
