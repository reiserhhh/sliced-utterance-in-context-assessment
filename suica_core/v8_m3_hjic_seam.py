"""End-to-end synthetic seam from event paths through M3 to HJIC-1C.

The event estimator is frozen and generator-blind.  It summarizes fixed
event blocks with marginal, second-order, characteristic-function, and
transition-characteristic features.  D0 may use only same-family replicate
support to freeze quotient coordinates; cross-family truth remains locked
until the audit stage.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .v8_context_relation_field import (
    ContextRelationSpec,
    FrozenRelationCalibration,
    calibrate_residual_misspecification_null,
    covariance_decomposition,
    observable_context_relation_diagnostics,
)


@dataclass(frozen=True)
class M3HJICSeamSpec:
    """Evidence budgets for the event-to-relation seam."""

    calibration_authors: int = 400
    confirmation_authors: int = 400
    contexts: int = 4
    events: int = 128
    block_size: int = 16
    event_dimensions: int = 3
    quotient_dimensions: int = 2
    shared_dimensions: int = 2
    random_frequencies: int = 4
    permutations: int = 999
    bootstrap_draws: int = 999
    innovation_noise: float = 0.85
    ar_coefficient: float = 0.35
    relation_strength_floor: float = 0.065
    mesoscopic_reliability_floor: float = 0.45
    mismatch_periodic_reliability_floor: float = 0.75
    mismatch_mesoscopic_ceiling: float = 0.25
    shared_generator_mechanism: bool = False
    calibrate_between_null: bool = False
    support_invariance_audit: bool = False

    def __post_init__(self) -> None:
        if self.calibration_authors < 200:
            raise ValueError("Calibration requires at least 200 authors.")
        if self.confirmation_authors < 200:
            raise ValueError("Confirmation requires at least 200 authors.")
        if self.events % self.block_size:
            raise ValueError("events must be divisible by block_size.")
        if self.block_size < 8:
            raise ValueError("Blocks must contain at least eight events.")
        if self.quotient_dimensions < 2:
            raise ValueError("The relation seam must remain multivariate.")
        if self.shared_dimensions > self.quotient_dimensions:
            raise ValueError("shared_dimensions must fit quotient_dimensions.")
        if self.permutations < 19 or self.bootstrap_draws < 19:
            raise ValueError("Resampling budgets are too small.")

    @property
    def blocks(self) -> int:
        return self.events // self.block_size


@dataclass(frozen=True)
class FrozenM3SeamCalibration:
    """D0-frozen M3 quotient maps and HJIC relation calibration."""

    left_center: np.ndarray
    right_center: np.ndarray
    left_basis: np.ndarray
    right_basis: np.ndarray
    relation: FrozenRelationCalibration
    event_frequencies: np.ndarray
    transition_frequencies: np.ndarray
    raw_feature_names: tuple[str, ...]
    support_alignment_floor: float
    support_eigengap_floor: float
    support_eigenvalue_floor: float


def _center(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    return matrix - matrix.mean(axis=0, keepdims=True)


def _covariance(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    x = _center(left)
    y = _center(right)
    return x.T @ y / max(1, len(x))


def _replicate_covariance(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    return 0.5 * (
        _covariance(first, second)
        + _covariance(second, first).T
    )


def _inverse_sqrt(matrix: np.ndarray, ridge: float = 1e-5) -> np.ndarray:
    symmetric = 0.5 * (matrix + matrix.T)
    values, vectors = np.linalg.eigh(symmetric)
    scale = max(float(values.max()), ridge)
    values = np.clip(values, ridge * scale, None)
    return vectors @ np.diag(1.0 / np.sqrt(values)) @ vectors.T


def _orthonormal_loadings(
    rng: np.random.Generator,
    rows: int,
    columns: int,
) -> np.ndarray:
    basis, _ = np.linalg.qr(rng.normal(size=(rows, columns)))
    return np.asarray(basis[:, :columns], dtype=float)


def _cosine(left: np.ndarray, right: np.ndarray) -> float:
    x = np.asarray(left, dtype=float).ravel()
    y = np.asarray(right, dtype=float).ravel()
    denominator = float(np.linalg.norm(x) * np.linalg.norm(y))
    if denominator <= 1e-12:
        return 0.0
    return float(np.dot(x, y) / denominator)


def _relative_error(estimate: np.ndarray, truth: np.ndarray) -> float:
    denominator = max(float(np.linalg.norm(truth)), 1e-10)
    return float(np.linalg.norm(estimate - truth) / denominator)


def _rms(matrix: np.ndarray) -> float:
    values = np.asarray(matrix, dtype=float)
    return float(np.linalg.norm(values) / np.sqrt(values.size))


def frozen_random_features(
    *,
    seed: int,
    spec: M3HJICSeamSpec,
) -> tuple[np.ndarray, np.ndarray]:
    """Create generator-independent event and transition frequencies."""
    rng = np.random.default_rng(seed)
    event = rng.normal(
        size=(spec.random_frequencies, spec.event_dimensions)
    )
    event /= np.maximum(np.linalg.norm(event, axis=1, keepdims=True), 1e-12)
    transition = rng.normal(
        size=(spec.random_frequencies, 2 * spec.event_dimensions)
    )
    transition /= np.maximum(
        np.linalg.norm(transition, axis=1, keepdims=True),
        1e-12,
    )
    scales = np.geomspace(0.7, 2.2, spec.random_frequencies)
    return event * scales[:, None], transition * scales[:, None]


def m3_block_features(
    events: np.ndarray,
    *,
    event_frequencies: np.ndarray,
    transition_frequencies: np.ndarray,
    block_size: int,
) -> tuple[np.ndarray, tuple[str, ...]]:
    """Extract a fixed family-blind M3 feature vector from each event block."""
    values = np.asarray(events, dtype=float)
    authors, event_count, dimensions = values.shape
    if event_count % block_size:
        raise ValueError("Event count must be divisible by block_size.")
    blocks = event_count // block_size
    panel = values.reshape(authors, blocks, block_size, dimensions)
    mean = panel.mean(axis=2)
    centered = panel - mean[:, :, None, :]
    variance = np.mean(centered**2, axis=2)
    following = np.roll(centered, -1, axis=2)
    lag = np.mean(centered * following, axis=2)

    event_phase = np.einsum(
        "nbtd,fd->nbtf",
        centered,
        event_frequencies,
    )
    event_rff = np.concatenate(
        [
            np.mean(np.cos(event_phase), axis=2),
            np.mean(np.sin(event_phase), axis=2),
        ],
        axis=2,
    )
    pair = np.concatenate([centered, following], axis=3)
    transition_phase = np.einsum(
        "nbtd,fd->nbtf",
        pair,
        transition_frequencies,
    )
    transition_rff = np.concatenate(
        [
            np.mean(np.cos(transition_phase), axis=2),
            np.mean(np.sin(transition_phase), axis=2),
        ],
        axis=2,
    )
    features = np.concatenate(
        [mean, variance, lag, event_rff, transition_rff],
        axis=2,
    )
    names = (
        tuple(f"mean_{index}" for index in range(dimensions))
        + tuple(f"variance_{index}" for index in range(dimensions))
        + tuple(f"lag1_{index}" for index in range(dimensions))
        + tuple(
            f"event_rff_{part}_{index}"
            for part in ("cos", "sin")
            for index in range(len(event_frequencies))
        )
        + tuple(
            f"transition_rff_{part}_{index}"
            for part in ("cos", "sin")
            for index in range(len(transition_frequencies))
        )
    )
    return features, names


def _periodic_diagnostic(events: np.ndarray, period: int = 8) -> np.ndarray:
    values = np.asarray(events, dtype=float)
    time = np.arange(values.shape[1], dtype=float)
    phase = 2.0 * np.pi * time / period
    return np.column_stack([
        np.mean(values[:, :, 0] * np.cos(phase)[None, :], axis=1),
        np.mean(values[:, :, 0] * np.sin(phase)[None, :], axis=1),
    ])


def _simulate_ar_events(
    mean: np.ndarray,
    *,
    rng: np.random.Generator,
    spec: M3HJICSeamSpec,
    noise: float,
    coefficient: float,
) -> np.ndarray:
    authors, dimensions = mean.shape
    events = np.empty((authors, spec.events, dimensions), dtype=float)
    stationary = noise / np.sqrt(max(1.0 - coefficient**2, 1e-6))
    events[:, 0] = mean + rng.normal(
        scale=stationary,
        size=(authors, dimensions),
    )
    for event in range(1, spec.events):
        events[:, event] = (
            mean
            + coefficient * (events[:, event - 1] - mean)
            + rng.normal(scale=noise, size=(authors, dimensions))
        )
    return events


def _simulate_periodic_events(
    phase_index: np.ndarray,
    *,
    rng: np.random.Generator,
    spec: M3HJICSeamSpec,
) -> np.ndarray:
    time = np.arange(spec.events, dtype=float)[None, :]
    phase = 2.0 * np.pi * phase_index[:, None] / 8.0
    wave = np.cos(2.0 * np.pi * time / 8.0 + phase)
    events = rng.normal(
        scale=0.08,
        size=(len(phase_index), spec.events, spec.event_dimensions),
    )
    events[:, :, 0] += wave
    events[:, :, 1] += np.roll(wave, 2, axis=1)
    return events


def _world_author_coordinates(
    world: str,
    *,
    rng: np.random.Generator,
    contexts: np.ndarray,
    dimensions: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
    left = rng.normal(size=(len(contexts), dimensions))
    right = left + rng.normal(scale=0.08, size=left.shape)
    phase: np.ndarray | None = None
    if world == "BALANCED_CONTEXT_CANCELLATION":
        signs = np.where(contexts % 2 == 0, 1.0, -1.0)
        right = left * signs[:, None]
    elif world in (
        "ECOLOGICAL_ONLY",
        "CALIBRATION_NULL",
        "HELDOUT_D0_NULL",
    ):
        right = rng.normal(size=left.shape)
    elif world == "SUPPORT_UNDERRESOLVED":
        left = np.zeros_like(left)
        right = np.zeros_like(right)
    elif world == "MECHANISM_FAMILY_MISMATCH":
        phase = rng.integers(0, 8, size=len(contexts))
        left = rng.normal(size=left.shape)
        right = rng.normal(size=right.shape)
    return left, right, phase


def _generate_event_panel(
    world: str,
    *,
    seed: int,
    spec: M3HJICSeamSpec,
    weights: np.ndarray,
    left_loadings: np.ndarray,
    right_loadings: np.ndarray,
    event_frequencies: np.ndarray,
    transition_frequencies: np.ndarray,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    contexts = rng.choice(spec.contexts, size=spec.confirmation_authors, p=weights)
    left_coordinate, right_coordinate, phase = _world_author_coordinates(
        world,
        rng=rng,
        contexts=contexts,
        dimensions=spec.shared_dimensions,
    )
    left_mean = 1.20 * left_coordinate @ left_loadings.T
    right_mean = 1.20 * right_coordinate @ right_loadings.T
    if world == "ECOLOGICAL_ONLY":
        offset = np.linspace(-1.8, 1.8, spec.contexts)
        left_mean += offset[contexts, None] * left_loadings[:, 0][None, :]
        right_mean += offset[contexts, None] * right_loadings[:, 0][None, :]

    if world == "MECHANISM_FAMILY_MISMATCH":
        assert phase is not None
        left_first_events = _simulate_periodic_events(
            phase,
            rng=rng,
            spec=spec,
        )
        left_second_events = _simulate_periodic_events(
            phase,
            rng=rng,
            spec=spec,
        )
        right_first_events = _simulate_periodic_events(
            phase,
            rng=rng,
            spec=spec,
        )
        right_second_events = _simulate_periodic_events(
            phase,
            rng=rng,
            spec=spec,
        )
        left_truth_mean = np.zeros_like(left_mean)
        right_truth_mean = np.zeros_like(right_mean)
    else:
        noise = spec.innovation_noise
        coefficient = spec.ar_coefficient
        if world == "ESTIMATION_ATTENUATION":
            noise = 1.10
            coefficient = 0.55
        left_first_events = _simulate_ar_events(
            left_mean,
            rng=rng,
            spec=spec,
            noise=noise,
            coefficient=coefficient,
        )
        left_second_events = _simulate_ar_events(
            left_mean,
            rng=rng,
            spec=spec,
            noise=noise,
            coefficient=coefficient,
        )
        right_first_events = _simulate_ar_events(
            right_mean,
            rng=rng,
            spec=spec,
            noise=noise,
            coefficient=coefficient,
        )
        right_second_events = _simulate_ar_events(
            right_mean,
            rng=rng,
            spec=spec,
            noise=noise,
            coefficient=coefficient,
        )
        if world == "ESTIMATION_ATTENUATION":
            # Same-occasion cross-family measurement shock. The shock is
            # independent across repetitions, so a cross-replicate estimator
            # removes it while a same-view estimator does not.
            shock_first = rng.normal(
                scale=1.30,
                size=(len(left_first_events), 1, spec.event_dimensions),
            )
            shock_second = rng.normal(
                scale=1.30,
                size=(len(left_second_events), 1, spec.event_dimensions),
            )
            left_first_events += shock_first
            right_first_events += shock_first
            left_second_events += shock_second
            right_second_events += shock_second
        left_truth_mean = left_mean
        right_truth_mean = right_mean

    event_arrays = {
        "left_first": left_first_events,
        "left_second": left_second_events,
        "right_first": right_first_events,
        "right_second": right_second_events,
    }
    block_features: dict[str, np.ndarray] = {}
    raw_names: tuple[str, ...] | None = None
    for name, events in event_arrays.items():
        block_features[name], names = m3_block_features(
            events,
            event_frequencies=event_frequencies,
            transition_frequencies=transition_frequencies,
            block_size=spec.block_size,
        )
        raw_names = names
    periodic = {
        name: _periodic_diagnostic(events)
        for name, events in event_arrays.items()
    }
    raw_dimension = block_features["left_first"].shape[2]
    truth_left = np.zeros((len(contexts), raw_dimension), dtype=float)
    truth_right = np.zeros((len(contexts), raw_dimension), dtype=float)
    truth_left[:, : spec.event_dimensions] = left_truth_mean
    truth_right[:, : spec.event_dimensions] = right_truth_mean
    population_cross_raw = np.zeros(
        (spec.contexts, raw_dimension, raw_dimension),
        dtype=float,
    )
    if world not in {
        "ECOLOGICAL_ONLY",
        "CALIBRATION_NULL",
        "HELDOUT_D0_NULL",
        "MECHANISM_FAMILY_MISMATCH",
        "SUPPORT_UNDERRESOLVED",
    }:
        base_cross = (
            1.20**2 * left_loadings @ right_loadings.T
        )
        signs = np.ones(spec.contexts, dtype=float)
        if world == "BALANCED_CONTEXT_CANCELLATION":
            signs = np.where(np.arange(spec.contexts) % 2 == 0, 1.0, -1.0)
        population_cross_raw[
            :,
            : spec.event_dimensions,
            : spec.event_dimensions,
        ] = signs[:, None, None] * base_cross[None, :, :]
    return {
        "contexts": contexts,
        "block_features": block_features,
        "periodic": periodic,
        "truth_raw_left": truth_left,
        "truth_raw_right": truth_right,
        "population_cross_raw": population_cross_raw,
        "raw_feature_names": raw_names,
        "event_arrays": event_arrays,
    }


def _support_basis(
    first: np.ndarray,
    second: np.ndarray,
    dimensions: int,
) -> tuple[np.ndarray, np.ndarray]:
    center = 0.5 * (first.mean(axis=0) + second.mean(axis=0))
    covariance = _replicate_covariance(first - center, second - center)
    values, vectors = np.linalg.eigh(0.5 * (covariance + covariance.T))
    order = np.argsort(values)[::-1]
    if np.any(values[order[:dimensions]] <= 1e-8):
        raise ValueError("D0 did not identify the requested replicated support.")
    return center, vectors[:, order[:dimensions]]


def _replicated_support_summary(
    first: np.ndarray,
    second: np.ndarray,
    *,
    dimensions: int,
) -> dict[str, Any]:
    """Estimate the positive replicated support and its resolution."""
    covariance = _replicate_covariance(first, second)
    values, vectors = np.linalg.eigh(0.5 * (covariance + covariance.T))
    order = np.argsort(values)[::-1]
    ordered = values[order]
    support = vectors[:, order[:dimensions]]
    kth = float(ordered[dimensions - 1])
    following = float(
        ordered[dimensions]
        if dimensions < len(ordered)
        else 0.0
    )
    gap = float(
        (kth - following) / max(abs(kth), 1e-12)
    )
    return {
        "support": support,
        "normalized_eigengap": gap,
        "kth_eigenvalue": kth,
    }


def _support_alignment(
    reference: np.ndarray,
    candidate: np.ndarray,
) -> float:
    singular = np.linalg.svd(
        reference.T @ candidate,
        compute_uv=False,
    )
    return float(np.min(singular) ** 2)


def _support_geometry(
    first: np.ndarray,
    second: np.ndarray,
    *,
    reference: np.ndarray,
    dimensions: int,
) -> dict[str, float]:
    """Measure replicated support strength, separation, and alignment."""
    summary = _replicated_support_summary(
        first,
        second,
        dimensions=dimensions,
    )
    return {
        "alignment": _support_alignment(
            reference,
            summary["support"],
        ),
        "normalized_eigengap": summary["normalized_eigengap"],
        "kth_eigenvalue": summary["kth_eigenvalue"],
    }


def _project_blocks(
    blocks: np.ndarray,
    *,
    center: np.ndarray,
    basis: np.ndarray,
) -> np.ndarray:
    return np.einsum("nbr,rd->nbd", blocks - center, basis)


def _panel_from_projected(
    projected: dict[str, np.ndarray],
    contexts: np.ndarray,
    *,
    seed: int,
) -> dict[str, Any]:
    authors = len(contexts)
    rng = np.random.default_rng(seed)
    order = rng.permutation(authors)
    folds = np.empty(authors, dtype=int)
    folds[order[: authors // 2]] = 0
    folds[order[authors // 2 :]] = 1
    return {
        name: values.mean(axis=1)
        for name, values in projected.items()
    } | {
        "nuisance": rng.normal(size=(authors, 2)),
        "folds": folds,
        "context_first": np.asarray(contexts, dtype=int),
        "context_second": np.asarray(contexts, dtype=int),
        "declared_context_role": "PRE_RESPONSE_DESIGNED",
    }


def _same_view_covariance(values: np.ndarray) -> np.ndarray:
    return _covariance(values, values)


def _between_covariance(
    left: np.ndarray,
    right: np.ndarray,
    contexts: np.ndarray,
    context_count: int,
) -> np.ndarray:
    """Return the covariance carried only by context mean differences."""
    mean_left = left.mean(axis=0)
    mean_right = right.mean(axis=0)
    value = np.zeros((left.shape[1], right.shape[1]), dtype=float)
    for context in range(context_count):
        mask = contexts == context
        weight = float(mask.mean())
        delta_left = left[mask].mean(axis=0) - mean_left
        delta_right = right[mask].mean(axis=0) - mean_right
        value += weight * np.outer(delta_left, delta_right)
    return value


def fit_m3_seam_calibration(
    *,
    seed: int,
    spec: M3HJICSeamSpec,
) -> FrozenM3SeamCalibration:
    """Freeze the M3 quotient and HJIC calibration using D0 only."""
    event_frequencies, transition_frequencies = frozen_random_features(
        seed=seed + 17,
        spec=spec,
    )
    rng = np.random.default_rng(seed)
    left_loadings = _orthonormal_loadings(
        rng,
        spec.event_dimensions,
        spec.shared_dimensions,
    )
    right_loadings = _orthonormal_loadings(
        rng,
        spec.event_dimensions,
        spec.shared_dimensions,
    )
    balanced = np.full(spec.contexts, 1.0 / spec.contexts)
    calibration_spec = M3HJICSeamSpec(
        **{
            **spec.__dict__,
            "confirmation_authors": spec.calibration_authors,
        }
    )
    panel = _generate_event_panel(
        "CALIBRATION_NULL",
        seed=seed + 31,
        spec=calibration_spec,
        weights=balanced,
        left_loadings=left_loadings,
        right_loadings=right_loadings,
        event_frequencies=event_frequencies,
        transition_frequencies=transition_frequencies,
    )
    blocks = panel["block_features"]
    left_first_raw = blocks["left_first"].mean(axis=1)
    left_second_raw = blocks["left_second"].mean(axis=1)
    right_first_raw = blocks["right_first"].mean(axis=1)
    right_second_raw = blocks["right_second"].mean(axis=1)
    left_center, left_basis = _support_basis(
        left_first_raw,
        left_second_raw,
        spec.quotient_dimensions,
    )
    right_center, right_basis = _support_basis(
        right_first_raw,
        right_second_raw,
        spec.quotient_dimensions,
    )
    left_first = (left_first_raw - left_center) @ left_basis
    left_second = (left_second_raw - left_center) @ left_basis
    right_first = (right_first_raw - right_center) @ right_basis
    right_second = (right_second_raw - right_center) @ right_basis
    left_whitener = _inverse_sqrt(
        _replicate_covariance(left_first, left_second)
    )
    right_whitener = _inverse_sqrt(
        _replicate_covariance(right_first, right_second)
    )
    contexts = np.arange(spec.calibration_authors) % spec.contexts
    maxima = np.empty(spec.permutations, dtype=float)
    between_null = np.empty(spec.permutations, dtype=float)
    for draw in range(spec.permutations):
        order = rng.permutation(spec.calibration_authors)
        strengths = []
        for context in range(spec.contexts):
            mask = contexts == context
            cross = 0.5 * (
                _covariance(left_first[mask], right_second[order][mask])
                + _covariance(left_second[mask], right_first[order][mask])
            )
            strengths.append(_rms(left_whitener @ cross @ right_whitener))
        maxima[draw] = max(strengths)
        between = 0.5 * (
            _between_covariance(
                left_first,
                right_second[order],
                contexts,
                spec.contexts,
            )
            + _between_covariance(
                left_second,
                right_first[order],
                contexts,
                spec.contexts,
            )
        )
        between_null[draw] = _rms(
            left_whitener @ between @ right_whitener
        )
    calibration_panel = {
        "left_first": left_first,
        "left_second": left_second,
        "right_first": right_first,
        "right_second": right_second,
    }
    misspecification_q99 = calibrate_residual_misspecification_null(
        calibration_panel,
        draws=spec.permutations,
        seed=seed + 53,
    )
    support_alignment_floor = 0.0
    support_eigengap_floor = 0.0
    support_eigenvalue_floor = 0.0
    if spec.support_invariance_audit:
        alignment_null = np.empty(spec.permutations, dtype=float)
        eigengap_null = np.empty(spec.permutations, dtype=float)
        eigenvalue_null = np.empty(spec.permutations, dtype=float)
        for draw in range(spec.permutations):
            order = rng.permutation(spec.calibration_authors)
            midpoint = spec.calibration_authors // 2
            halves = (order[:midpoint], order[midpoint:])
            family_summaries = []
            for first, second in (
                (left_first_raw, left_second_raw),
                (right_first_raw, right_second_raw),
            ):
                family_summaries.append([
                    _replicated_support_summary(
                        first[indices],
                        second[indices],
                        dimensions=spec.quotient_dimensions,
                    )
                    for indices in halves
                ])
            alignment_null[draw] = min(
                _support_alignment(
                    summaries[0]["support"],
                    summaries[1]["support"],
                )
                for summaries in family_summaries
            )
            eigengap_null[draw] = min(
                summary["normalized_eigengap"]
                for summaries in family_summaries
                for summary in summaries
            )
            eigenvalue_null[draw] = min(
                summary["kth_eigenvalue"]
                for summaries in family_summaries
                for summary in summaries
            )
        support_alignment_floor = float(
            np.quantile(alignment_null, 0.01)
        )
        support_eigengap_floor = float(
            np.quantile(eigengap_null, 0.01)
        )
        support_eigenvalue_floor = float(
            np.quantile(eigenvalue_null, 0.01)
        )
    relation = FrozenRelationCalibration(
        left_whitener=left_whitener,
        right_whitener=right_whitener,
        local_max_null_q99=float(np.quantile(maxima, 0.99)),
        context_cutpoints=np.linspace(-1.0, 1.0, spec.contexts - 1),
        residual_misspecification_q99=misspecification_q99,
        between_relation_q99=(
            float(np.quantile(between_null, 0.99))
            if spec.calibrate_between_null
            else 0.0
        ),
    )
    assert panel["raw_feature_names"] is not None
    return FrozenM3SeamCalibration(
        left_center=left_center,
        right_center=right_center,
        left_basis=left_basis,
        right_basis=right_basis,
        relation=relation,
        event_frequencies=event_frequencies,
        transition_frequencies=transition_frequencies,
        raw_feature_names=panel["raw_feature_names"],
        support_alignment_floor=support_alignment_floor,
        support_eigengap_floor=support_eigengap_floor,
        support_eigenvalue_floor=support_eigenvalue_floor,
    )


def _project_generated_panel(
    generated: dict[str, Any],
    *,
    calibration: FrozenM3SeamCalibration,
    seed: int,
) -> dict[str, Any]:
    blocks = generated["block_features"]
    projected = {
        "left_first": _project_blocks(
            blocks["left_first"],
            center=calibration.left_center,
            basis=calibration.left_basis,
        ),
        "left_second": _project_blocks(
            blocks["left_second"],
            center=calibration.left_center,
            basis=calibration.left_basis,
        ),
        "right_first": _project_blocks(
            blocks["right_first"],
            center=calibration.right_center,
            basis=calibration.right_basis,
        ),
        "right_second": _project_blocks(
            blocks["right_second"],
            center=calibration.right_center,
            basis=calibration.right_basis,
        ),
    }
    panel = _panel_from_projected(
        projected,
        generated["contexts"],
        seed=seed,
    )
    truth_left = (
        generated["truth_raw_left"] - calibration.left_center
    ) @ calibration.left_basis
    truth_right = (
        generated["truth_raw_right"] - calibration.right_center
    ) @ calibration.right_basis
    population_cross_projected = np.asarray([
        calibration.left_basis.T @ value @ calibration.right_basis
        for value in generated["population_cross_raw"]
    ])
    population_relation = np.asarray([
        calibration.relation.left_whitener
        @ value
        @ calibration.relation.right_whitener
        for value in population_cross_projected
    ])
    return {
        "panel": panel,
        "projected_blocks": projected,
        "truth_left": truth_left,
        "truth_right": truth_right,
        "population_relation": population_relation,
        "periodic": generated["periodic"],
        "events": generated["event_arrays"],
        "raw_author_features": {
            name: values.mean(axis=1)
            for name, values in blocks.items()
        },
    }


def _support_invariance_diagnostics(
    projected: dict[str, Any],
    *,
    calibration: FrozenM3SeamCalibration,
    spec: M3HJICSeamSpec,
) -> dict[str, Any]:
    geometries = {}
    for family, reference in (
        ("left", calibration.left_basis),
        ("right", calibration.right_basis),
    ):
        geometries[family] = _support_geometry(
            projected["raw_author_features"][f"{family}_first"],
            projected["raw_author_features"][f"{family}_second"],
            reference=reference,
            dimensions=spec.quotient_dimensions,
        )
    minimum_alignment = min(
        value["alignment"] for value in geometries.values()
    )
    minimum_eigengap = min(
        value["normalized_eigengap"] for value in geometries.values()
    )
    minimum_eigenvalue = min(
        value["kth_eigenvalue"] for value in geometries.values()
    )
    underresolved = bool(
        minimum_eigengap < calibration.support_eigengap_floor
        or minimum_eigenvalue < calibration.support_eigenvalue_floor
    )
    noninvariant = bool(
        not underresolved
        and minimum_alignment < calibration.support_alignment_floor
    )
    return {
        "minimum_alignment": minimum_alignment,
        "minimum_eigengap": minimum_eigengap,
        "minimum_eigenvalue": minimum_eigenvalue,
        "alignment_floor": calibration.support_alignment_floor,
        "eigengap_floor": calibration.support_eigengap_floor,
        "eigenvalue_floor": calibration.support_eigenvalue_floor,
        "support_underresolved": int(underresolved),
        "support_noninvariant": int(noninvariant),
        "support_adequate": int(not underresolved and not noninvariant),
    }


def _replicate_reliability(first: np.ndarray, second: np.ndarray) -> float:
    values = []
    for dimension in range(first.shape[1]):
        x = first[:, dimension]
        y = second[:, dimension]
        if np.std(x) <= 1e-10 or np.std(y) <= 1e-10:
            continue
        values.append(float(np.corrcoef(x, y)[0, 1]))
    return float(np.mean(values)) if values else 0.0


def _oracle_decomposition(
    projected: dict[str, Any],
    *,
    calibration: FrozenRelationCalibration,
    contexts: int,
) -> dict[str, Any]:
    truth_panel = {
        "left_first": projected["truth_left"],
        "left_second": projected["truth_left"],
        "right_first": projected["truth_right"],
        "right_second": projected["truth_right"],
    }
    return covariance_decomposition(
        truth_panel,
        contexts=projected["panel"]["context_first"],
        calibration=calibration,
        context_count=contexts,
    )


def _naive_decomposition(
    panel: dict[str, Any],
    *,
    calibration: FrozenM3SeamCalibration,
    contexts: int,
) -> dict[str, Any]:
    left_covariance = 0.5 * (
        _same_view_covariance(panel["left_first"])
        + _same_view_covariance(panel["left_second"])
    )
    right_covariance = 0.5 * (
        _same_view_covariance(panel["right_first"])
        + _same_view_covariance(panel["right_second"])
    )
    naive_calibration = FrozenRelationCalibration(
        left_whitener=_inverse_sqrt(left_covariance),
        right_whitener=_inverse_sqrt(right_covariance),
        local_max_null_q99=calibration.relation.local_max_null_q99,
        context_cutpoints=calibration.relation.context_cutpoints,
    )
    same_view_panel = {
        "left_first": panel["left_first"],
        "left_second": panel["left_first"],
        "right_first": panel["right_first"],
        "right_second": panel["right_first"],
    }
    return covariance_decomposition(
        same_view_panel,
        contexts=panel["context_first"],
        calibration=naive_calibration,
        context_count=contexts,
    )


def _periodic_reliability(periodic: dict[str, np.ndarray]) -> float:
    return 0.5 * (
        _replicate_reliability(
            periodic["left_first"],
            periodic["left_second"],
        )
        + _replicate_reliability(
            periodic["right_first"],
            periodic["right_second"],
        )
    )


def _bootstrap_coverage(
    projected: dict[str, Any],
    *,
    calibration: FrozenRelationCalibration,
    spec: M3HJICSeamSpec,
    seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    blocks = projected["projected_blocks"]
    labels = projected["panel"]["context_first"]
    indices_by_context = [
        np.flatnonzero(labels == context)
        for context in range(spec.contexts)
    ]
    cluster_draws = np.empty(
        (
            spec.bootstrap_draws,
            spec.contexts,
            spec.quotient_dimensions,
            spec.quotient_dimensions,
        ),
        dtype=float,
    )
    nested_draws = np.empty_like(cluster_draws)
    author_grid = np.arange(len(labels))[:, None]
    for draw in range(spec.bootstrap_draws):
        author_indices = np.concatenate([
            rng.choice(indices, size=len(indices), replace=True)
            for indices in indices_by_context
        ])
        cluster_panel = {
            name: values.mean(axis=1)[author_indices]
            for name, values in blocks.items()
        }
        draw_labels = labels[author_indices]
        cluster_decomposition = covariance_decomposition(
            cluster_panel,
            contexts=draw_labels,
            calibration=calibration,
            context_count=spec.contexts,
        )
        cluster_draws[draw] = cluster_decomposition["local_relation"]

        # The nested version is retained as a conservative sensitivity audit,
        # not as the primary superpopulation interval.
        block_draws = {
            name: values[
                author_grid,
                rng.integers(0, spec.blocks, size=(len(labels), spec.blocks)),
            ].mean(axis=1)
            for name, values in blocks.items()
        }
        nested_panel = {
            name: values[author_indices]
            for name, values in block_draws.items()
        }
        nested_decomposition = covariance_decomposition(
            nested_panel,
            contexts=draw_labels,
            calibration=calibration,
            context_count=spec.contexts,
        )
        nested_draws[draw] = nested_decomposition["local_relation"]

    lower = np.quantile(cluster_draws, 0.025, axis=0)
    upper = np.quantile(cluster_draws, 0.975, axis=0)
    nested_lower = np.quantile(nested_draws, 0.025, axis=0)
    nested_upper = np.quantile(nested_draws, 0.975, axis=0)
    target = projected["population_relation"]
    covered = (target >= lower) & (target <= upper)
    nested_covered = (
        (target >= nested_lower)
        & (target <= nested_upper)
    )
    return {
        "covered": int(covered.sum()),
        "total": int(covered.size),
        "coverage": float(covered.mean()),
        "mean_width": float(np.mean(upper - lower)),
        "nested_covered": int(nested_covered.sum()),
        "nested_total": int(nested_covered.size),
        "nested_coverage": float(nested_covered.mean()),
        "nested_mean_width": float(
            np.mean(nested_upper - nested_lower)
        ),
    }


def run_m3_hjic_seam_repetition(
    repetition: int,
    *,
    seed: int,
    spec: M3HJICSeamSpec,
) -> dict[str, list[dict[str, Any]]]:
    """Run all end-to-end worlds under one independent D0 calibration."""
    calibration = fit_m3_seam_calibration(
        seed=seed + repetition * 100_003,
        spec=spec,
    )
    hjic_spec = ContextRelationSpec(
        calibration_authors=spec.calibration_authors,
        confirmation_authors=spec.confirmation_authors,
        contexts=spec.contexts,
        left_dimensions=spec.quotient_dimensions,
        right_dimensions=spec.quotient_dimensions,
        shared_dimensions=spec.shared_dimensions,
        permutations=spec.permutations,
        bootstrap_draws=spec.bootstrap_draws,
        relation_strength_floor=spec.relation_strength_floor,
        misspecification_floor=0.30,
    )
    generator_seed = seed + repetition * 100_003
    rng = np.random.default_rng(
        generator_seed
        if spec.shared_generator_mechanism
        else generator_seed + 1
    )
    left_loadings = _orthonormal_loadings(
        rng,
        spec.event_dimensions,
        spec.shared_dimensions,
    )
    right_loadings = _orthonormal_loadings(
        rng,
        spec.event_dimensions,
        spec.shared_dimensions,
    )
    weights = np.full(spec.contexts, 1.0 / spec.contexts)
    worlds = [
        "GLOBAL_INVARIANT",
        "MICRO_GAUGE_ALIAS",
        "ESTIMATION_ATTENUATION",
        "BALANCED_CONTEXT_CANCELLATION",
        "ECOLOGICAL_ONLY",
        "MECHANISM_FAMILY_MISMATCH",
    ]
    if spec.calibrate_between_null:
        worlds.append("HELDOUT_D0_NULL")
    if spec.support_invariance_audit:
        worlds.extend([
            "WITHIN_SUPPORT_GAUGE",
            "MEASUREMENT_SUPPORT_DRIFT_GLOBAL",
            "MEASUREMENT_SUPPORT_DRIFT_ECOLOGICAL",
            "SUPPORT_UNDERRESOLVED",
        ])
    tables: dict[str, list[dict[str, Any]]] = {
        "mesoscopic_replicates": [],
        "m3_adequacy_diagnostics": [],
        "relation_field": [],
        "within_between_covariance": [],
        "attenuation_diagnostics": [],
        "aggregation_commutation": [],
        "alias_invariance": [],
        "mechanism_mismatch": [],
        "support_invariance": [],
        "uncertainty_coverage": [],
        "licenses": [],
        "truth_audit": [],
    }
    for world_index, world_name in enumerate(worlds):
        source_world = {
            "MICRO_GAUGE_ALIAS": "GLOBAL_INVARIANT",
            "WITHIN_SUPPORT_GAUGE": "GLOBAL_INVARIANT",
            "MEASUREMENT_SUPPORT_DRIFT_GLOBAL": "GLOBAL_INVARIANT",
            "MEASUREMENT_SUPPORT_DRIFT_ECOLOGICAL": "ECOLOGICAL_ONLY",
        }.get(world_name, world_name)
        world_left_loadings = left_loadings
        world_right_loadings = right_loadings
        if world_name == "WITHIN_SUPPORT_GAUGE":
            gauge_rng = np.random.default_rng(
                seed
                + repetition * 100_003
                + (world_index + 1) * 10_007
                + 701
            )
            gauge, _ = np.linalg.qr(
                gauge_rng.normal(
                    size=(
                        spec.shared_dimensions,
                        spec.shared_dimensions,
                    )
                )
            )
            world_left_loadings = left_loadings @ gauge
            world_right_loadings = right_loadings @ gauge
        elif world_name.startswith("MEASUREMENT_SUPPORT_DRIFT"):
            drift_rng = np.random.default_rng(
                seed
                + repetition * 100_003
                + (world_index + 1) * 10_007
                + 907
            )
            world_left_loadings = _orthonormal_loadings(
                drift_rng,
                spec.event_dimensions,
                spec.shared_dimensions,
            )
            world_right_loadings = _orthonormal_loadings(
                drift_rng,
                spec.event_dimensions,
                spec.shared_dimensions,
            )
        generated_splits = []
        for split_index in range(2):
            generated = _generate_event_panel(
                source_world,
                seed=(
                    seed
                    + repetition * 100_003
                    + (world_index + 1) * 10_007
                    + split_index * 503
                ),
                spec=spec,
                weights=weights,
                left_loadings=world_left_loadings,
                right_loadings=world_right_loadings,
                event_frequencies=calibration.event_frequencies,
                transition_frequencies=calibration.transition_frequencies,
            )
            generated_splits.append(
                _project_generated_panel(
                    generated,
                    calibration=calibration,
                    seed=seed + repetition + world_index + split_index,
                )
            )
        world = {
            "world": world_name,
            "context_reliability": 1.0,
            "first": generated_splits[0]["panel"],
            "second": generated_splits[1]["panel"],
        }
        observable = observable_context_relation_diagnostics(
            world,
            calibration=calibration.relation,
            spec=hjic_spec,
        )
        oracle_first = _oracle_decomposition(
            generated_splits[0],
            calibration=calibration.relation,
            contexts=spec.contexts,
        )
        oracle_second = _oracle_decomposition(
            generated_splits[1],
            calibration=calibration.relation,
            contexts=spec.contexts,
        )
        fidelity = 0.5 * (
            _cosine(
                observable["first"]["local_relation"],
                oracle_first["local_relation"],
            )
            + _cosine(
                observable["second"]["local_relation"],
                oracle_second["local_relation"],
            )
        )
        frobenius_error = 0.5 * (
            _relative_error(
                observable["first"]["local_relation"],
                oracle_first["local_relation"],
            )
            + _relative_error(
                observable["second"]["local_relation"],
                oracle_second["local_relation"],
            )
        )
        left_reliability = 0.5 * (
            _replicate_reliability(
                world["first"]["left_first"],
                world["first"]["left_second"],
            )
            + _replicate_reliability(
                world["second"]["left_first"],
                world["second"]["left_second"],
            )
        )
        right_reliability = 0.5 * (
            _replicate_reliability(
                world["first"]["right_first"],
                world["first"]["right_second"],
            )
            + _replicate_reliability(
                world["second"]["right_first"],
                world["second"]["right_second"],
            )
        )
        mesoscopic_reliability = 0.5 * (
            left_reliability + right_reliability
        )
        periodic_reliability = 0.5 * (
            _periodic_reliability(generated_splits[0]["periodic"])
            + _periodic_reliability(generated_splits[1]["periodic"])
        )
        mismatch_detected = bool(
            periodic_reliability
            >= spec.mismatch_periodic_reliability_floor
            and mesoscopic_reliability
            <= spec.mismatch_mesoscopic_ceiling
        )
        adequate = bool(
            mesoscopic_reliability >= spec.mesoscopic_reliability_floor
        )
        support_diagnostics = [
            _support_invariance_diagnostics(
                projected,
                calibration=calibration,
                spec=spec,
            )
            for projected in generated_splits
        ]
        support_adequate = bool(
            not spec.support_invariance_audit
            or all(
                diagnostic["support_adequate"]
                for diagnostic in support_diagnostics
            )
        )
        support_noninvariant = bool(
            spec.support_invariance_audit
            and all(
                diagnostic["support_noninvariant"]
                for diagnostic in support_diagnostics
            )
        )
        support_underresolved = bool(
            spec.support_invariance_audit
            and any(
                diagnostic["support_underresolved"]
                for diagnostic in support_diagnostics
            )
        )
        final_seam_license = int(
            observable["final_relation_license"]
            and adequate
            and support_adequate
            and not mismatch_detected
        )
        alias_output_difference = 0.0
        if world_name == "MICRO_GAUGE_ALIAS":
            alias_differences = []
            alias_rng = np.random.default_rng(
                seed + repetition * 100_003 + 880_001
            )
            gauge, _ = np.linalg.qr(
                alias_rng.normal(
                    size=(spec.event_dimensions, spec.event_dimensions)
                )
            )
            for projected in generated_splits:
                for family in ("left", "right"):
                    center = (
                        calibration.left_center
                        if family == "left"
                        else calibration.right_center
                    )
                    basis = (
                        calibration.left_basis
                        if family == "left"
                        else calibration.right_basis
                    )
                    for replicate in ("first", "second"):
                        events = projected["events"][
                            f"{family}_{replicate}"
                        ]
                        reconstructed = (events @ gauge) @ gauge.T
                        alias_blocks, _ = m3_block_features(
                            reconstructed,
                            event_frequencies=calibration.event_frequencies,
                            transition_frequencies=(
                                calibration.transition_frequencies
                            ),
                            block_size=spec.block_size,
                        )
                        alias_projected = _project_blocks(
                            alias_blocks,
                            center=center,
                            basis=basis,
                        )
                        original = projected["projected_blocks"][
                            f"{family}_{replicate}"
                        ]
                        alias_differences.append(
                            float(
                                np.linalg.norm(alias_projected - original)
                                / max(np.linalg.norm(original), 1e-10)
                            )
                        )
            alias_output_difference = max(alias_differences)
        mechanism_identity_license = 0

        naive = _naive_decomposition(
            world["first"],
            calibration=calibration,
            contexts=spec.contexts,
        )
        corrected_error = _relative_error(
            observable["first"]["local_relation"],
            oracle_first["local_relation"],
        )
        naive_error = _relative_error(
            naive["local_relation"],
            oracle_first["local_relation"],
        )
        attenuation_gain = float(
            (naive_error - corrected_error) / max(naive_error, 1e-10)
        )
        common = {"repetition": repetition, "world": world_name}
        tables["m3_adequacy_diagnostics"].append({
            **common,
            "left_replicate_reliability": left_reliability,
            "right_replicate_reliability": right_reliability,
            "mesoscopic_reliability": mesoscopic_reliability,
            "periodic_out_of_model_reliability": periodic_reliability,
            "mismatch_detected": int(mismatch_detected),
        })
        for split_name, split in (
            ("first", observable["first"]),
            ("second", observable["second"]),
        ):
            for context in range(spec.contexts):
                tables["relation_field"].append({
                    **common,
                    "split": split_name,
                    "context": context,
                    "strength": _rms(split["local_relation"][context]),
                    "relation_json": np.asarray(
                        split["local_relation"][context]
                    ).round(10).tolist(),
                })
            for component in ("within", "between", "total"):
                tables["within_between_covariance"].append({
                    **common,
                    "split": split_name,
                    "component": component,
                    "relation_norm": float(
                        np.linalg.norm(split[f"{component}_relation"])
                    ),
                })
            tables["aggregation_commutation"].append({
                **common,
                "split": split_name,
                "decomposition_error": float(split["decomposition_error"]),
                "aggregate_before_context_defect": float(
                    np.linalg.norm(
                        split["total_relation"]
                        - np.mean(split["local_relation"], axis=0)
                    )
                ),
            })
        tables["attenuation_diagnostics"].append({
            **common,
            "corrected_relative_error": corrected_error,
            "naive_relative_error": naive_error,
            "relative_error_reduction": attenuation_gain,
            "corrected_better": int(corrected_error < naive_error),
        })
        tables["alias_invariance"].append({
            **common,
            "relative_output_difference": alias_output_difference,
            "mechanism_identity_license": mechanism_identity_license,
        })
        tables["mechanism_mismatch"].append({
            **common,
            "periodic_reliability": periodic_reliability,
            "mesoscopic_reliability": mesoscopic_reliability,
            "mismatch_detected": int(mismatch_detected),
            "final_seam_license": final_seam_license,
        })
        for split_name, diagnostic in zip(
            ("first", "second"),
            support_diagnostics,
        ):
            tables["support_invariance"].append({
                **common,
                "split": split_name,
                **diagnostic,
            })
        split_relation_decisions = []
        threshold = max(
            spec.relation_strength_floor,
            calibration.relation.local_max_null_q99,
        )
        for split in (observable["first"], observable["second"]):
            split_relation_decisions.append(
                sum(
                    _rms(value) >= threshold
                    for value in split["local_relation"]
                )
                >= 2
            )
        tables["licenses"].append({
            **common,
            "final_seam_license": final_seam_license,
            "relation_license": observable["final_relation_license"],
            "global_invariant_license": observable[
                "global_invariant_license"
            ],
            "local_atlas_license": observable["local_atlas_license"],
            "cancellation_detected": observable["cancellation_detected"],
            "ecological_between_detected": observable[
                "ecological_between_detected"
            ],
            "between_strength_first": observable[
                "between_strength_first"
            ],
            "between_strength_second": observable[
                "between_strength_second"
            ],
            "between_agreement": observable["between_agreement"],
            "between_threshold": observable["between_threshold"],
            "mismatch_detected": int(mismatch_detected),
            "support_adequate": int(support_adequate),
            "support_noninvariant": int(support_noninvariant),
            "support_underresolved": int(support_underresolved),
            "support_d1_d2_decision_agreement": int(
                support_diagnostics[0]["support_adequate"]
                == support_diagnostics[1]["support_adequate"]
                and support_diagnostics[0]["support_noninvariant"]
                == support_diagnostics[1]["support_noninvariant"]
                and support_diagnostics[0]["support_underresolved"]
                == support_diagnostics[1]["support_underresolved"]
            ),
            "d1_d2_decision_agreement": int(
                split_relation_decisions[0] == split_relation_decisions[1]
            ),
            "local_license_count": observable["local_license_count"],
            "relation_threshold": observable["relation_threshold"],
            "minimum_local_strength": float(
                min(
                    np.min(observable["local_strength_first"]),
                    np.min(observable["local_strength_second"]),
                )
            ),
            "minimum_direction_agreement": float(
                np.min(observable["local_direction_agreement"])
            ),
            "confirmation_field_agreement": observable[
                "confirmation_field_agreement"
            ],
            "context_measurement_field_agreement": observable[
                "context_measurement_field_agreement"
            ],
            "misspecification_score": observable["misspecification_score"],
            "misspecification_threshold": observable[
                "misspecification_threshold"
            ],
            "residualizer_misspecified": observable[
                "residualizer_misspecified"
            ],
            "context_underresolved": observable["context_underresolved"],
            "heterogeneity": observable["heterogeneity"],
            "cancellation": observable["cancellation"],
            "mechanism_identity_license": mechanism_identity_license,
            "truth_used_by_license": False,
        })
        tables["truth_audit"].append({
            **common,
            "relation_fidelity": fidelity,
            "relative_frobenius_error": frobenius_error,
            "truth_used_by_license": False,
        })
        if world_name == "GLOBAL_INVARIANT":
            coverage = _bootstrap_coverage(
                generated_splits[0],
                calibration=calibration.relation,
                spec=spec,
                seed=seed + repetition * 100_003 + 90_001,
            )
            tables["uncertainty_coverage"].append({
                **common,
                **coverage,
            })
        for split_name, projected in zip(
            ("first", "second"),
            generated_splits,
        ):
            for family in ("left", "right"):
                first_values = projected["panel"][f"{family}_first"]
                second_values = projected["panel"][f"{family}_second"]
                for dimension in range(spec.quotient_dimensions):
                    tables["mesoscopic_replicates"].append({
                        **common,
                        "split": split_name,
                        "family": family,
                        "dimension": dimension,
                        "replicate_correlation": float(
                            np.corrcoef(
                                first_values[:, dimension],
                                second_values[:, dimension],
                            )[0, 1]
                        ),
                    })
    return tables
