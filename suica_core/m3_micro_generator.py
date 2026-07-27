"""Synthetic microscopic kernels for the SUICA M3 foundation.

This module creates observed, truth, and design packets separately. Estimation
code must not import this module.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import softmax

from .m3_contracts import (
    M3DesignManifest,
    M3ObservedPacket,
    M3TruthPacket,
)


@dataclass(frozen=True)
class M3WorldSpec:
    """Configuration for one discrete micro-kernel world."""

    authors: int = 96
    reference_authors: int = 192
    conditions: int = 8
    condition_dimensions: int = 3
    response_dimensions: int = 6
    occasions: int = 4
    fixed_repeats_train: int = 4
    fixed_repeats_test: int = 4
    free_events_train: int = 160
    free_events_test: int = 160
    author_scale: float = 0.45
    response_scale: float = 0.35
    nonlinear_scale: float = 0.24
    state_scale: float = 0.30
    noise_scale: float = 0.45
    choice_scale: float = 0.70
    choice_inertia: float = 0.35
    heavy_tail: bool = False
    heteroskedastic: bool = False
    nonlinear: bool = True
    shared_latent: bool = True
    missing_common_support: bool = False
    rank_deficient: bool = False
    null_authors: bool = False


def _weighted_basis(
    rng: np.random.Generator,
    *,
    conditions: int,
    dimensions: int,
    measure: np.ndarray,
    rank_deficient: bool,
) -> np.ndarray:
    raw = rng.normal(size=(conditions, dimensions))
    raw -= measure @ raw
    covariance = raw.T @ (measure[:, None] * raw)
    values, vectors = np.linalg.eigh(0.5 * (covariance + covariance.T))
    inverse = np.where(values > 1e-10, 1.0 / np.sqrt(values), 0.0)
    features = raw @ (vectors * inverse[None]) @ vectors.T
    if rank_deficient and dimensions > 1:
        features[:, -1] = features[:, 0]
    return features


def _nonlinear_basis(
    rng: np.random.Generator,
    *,
    features: np.ndarray,
    measure: np.ndarray,
    rank: int,
) -> np.ndarray:
    if rank <= 0:
        return np.zeros((len(features), 0), dtype=float)
    frequencies = rng.normal(size=(features.shape[1], max(3 * rank, rank)))
    phases = rng.uniform(0.0, 2.0 * np.pi, size=frequencies.shape[1])
    raw = np.sin(features @ frequencies + phases)
    design = np.column_stack([np.ones(len(features)), features])
    gram = design.T @ (measure[:, None] * design)
    projection = design @ np.linalg.pinv(gram) @ (
        design.T @ (measure[:, None] * raw)
    )
    residual = raw - projection
    weighted = np.sqrt(measure)[:, None] * residual
    left, singular, _ = np.linalg.svd(weighted, full_matrices=False)
    usable = min(rank, int(np.sum(singular > 1e-8)))
    basis = np.zeros((len(features), rank), dtype=float)
    if usable:
        basis[:, :usable] = left[:, :usable] / np.sqrt(measure)[:, None]
    return basis


def _stationary(transition: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eig(np.asarray(transition, dtype=float).T)
    index = int(np.argmin(np.abs(values - 1.0)))
    stationary = np.real(vectors[:, index])
    if stationary.sum() < 0.0:
        stationary *= -1.0
    stationary = np.maximum(stationary, 0.0)
    return stationary / stationary.sum()


def _choice_transition(
    features: np.ndarray,
    measure: np.ndarray,
    preference: np.ndarray,
    inertia: float,
) -> np.ndarray:
    logits = np.log(measure + 1e-12) + features @ preference
    rows = []
    for previous in range(len(measure)):
        row = logits.copy()
        row[previous] += float(inertia)
        rows.append(softmax(row))
    return np.asarray(rows)


def _draw_choice_sequences(
    rng: np.random.Generator,
    transitions: np.ndarray,
    stationary: np.ndarray,
    events: int,
) -> np.ndarray:
    authors, conditions, _ = transitions.shape
    sequences = np.empty((authors, events), dtype=np.int16)
    for author in range(authors):
        sequences[author, 0] = rng.choice(
            conditions,
            p=stationary[author],
        )
        for event in range(1, events):
            sequences[author, event] = rng.choice(
                conditions,
                p=transitions[author, sequences[author, event - 1]],
            )
    return sequences


def _states(
    rng: np.random.Generator,
    *,
    authors: int,
    occasions: int,
    dimensions: int,
    scale: float,
) -> np.ndarray:
    if occasions < 1:
        raise ValueError("occasions must be positive")
    state = np.empty((authors, occasions, dimensions), dtype=float)
    innovation = rng.normal(size=state.shape)
    state[:, 0] = innovation[:, 0]
    for occasion in range(1, occasions):
        state[:, occasion] = (
            0.55 * state[:, occasion - 1]
            + np.sqrt(1.0 - 0.55**2) * innovation[:, occasion]
        )
    if occasions > 1:
        state -= state.mean(axis=1, keepdims=True)
    rms = np.sqrt(np.mean(state**2))
    return state * (float(scale) / max(float(rms), 1e-12))


def _noise(
    rng: np.random.Generator,
    shape: tuple[int, ...],
    *,
    scale: float,
    heavy_tail: bool,
    author_multiplier: np.ndarray | None,
) -> np.ndarray:
    if heavy_tail:
        values = rng.standard_t(df=5.0, size=shape) / np.sqrt(5.0 / 3.0)
    else:
        values = rng.normal(size=shape)
    if author_multiplier is not None:
        reshape = (len(author_multiplier),) + (1,) * (len(shape) - 1)
        values *= author_multiplier.reshape(reshape)
    return float(scale) * values


def _fixed_responses(
    rng: np.random.Generator,
    *,
    origin: np.ndarray,
    field: np.ndarray,
    state: np.ndarray,
    repeats: int,
    scale: float,
    heavy_tail: bool,
    author_multiplier: np.ndarray | None,
) -> np.ndarray:
    systematic = (
        origin[None, None, :, None, :]
        + field[:, None, :, None, :]
        + state[:, :, None, None, :]
    )
    shape = systematic.shape[:-2] + (repeats, systematic.shape[-1])
    return systematic + _noise(
        rng,
        shape,
        scale=scale,
        heavy_tail=heavy_tail,
        author_multiplier=author_multiplier,
    )


def _reference_responses(
    rng: np.random.Generator,
    *,
    origin: np.ndarray,
    authors: int,
    occasions: int,
    repeats: int,
    state_scale: float,
    noise_scale: float,
    heavy_tail: bool,
) -> np.ndarray:
    state = _states(
        rng,
        authors=authors,
        occasions=occasions,
        dimensions=origin.shape[1],
        scale=state_scale,
    )
    field = np.zeros((authors, origin.shape[0], origin.shape[1]))
    return _fixed_responses(
        rng,
        origin=origin,
        field=field,
        state=state,
        repeats=repeats,
        scale=noise_scale,
        heavy_tail=heavy_tail,
        author_multiplier=None,
    )


def _apply_missing_support(
    values: np.ndarray,
    *,
    condition_dimensions: int,
) -> np.ndarray:
    array = values.copy()
    authors, _, conditions, _, _ = array.shape
    kept = max(condition_dimensions, 1)
    for author in range(authors):
        start = author % conditions
        mask = np.ones(conditions, dtype=bool)
        mask[(start + np.arange(kept)) % conditions] = False
        array[author, :, mask, :, :] = np.nan
    return array


def generate_m3_world(
    *,
    spec: M3WorldSpec,
    seed: int,
) -> tuple[M3ObservedPacket, M3TruthPacket, M3DesignManifest]:
    """Generate separated observed, truth, and public design packets."""
    streams = np.random.SeedSequence(seed).spawn(14)
    rngs = [np.random.default_rng(item) for item in streams]
    (
        rng_design,
        rng_nonlinear,
        rng_latent,
        rng_parameters,
        rng_origin,
        rng_state,
        rng_reference,
        rng_choice_train,
        rng_choice_test,
        rng_fixed_train,
        rng_fixed_test,
        _rng_free_response,
        _rng_audit,
        _rng_unused,
    ) = rngs

    measure = np.full(spec.conditions, 1.0 / spec.conditions)
    features = _weighted_basis(
        rng_design,
        conditions=spec.conditions,
        dimensions=spec.condition_dimensions,
        measure=measure,
        rank_deficient=spec.rank_deficient,
    )
    nonlinear_rank = min(
        3,
        max(spec.conditions - spec.condition_dimensions - 1, 0),
    )
    nonlinear_basis = _nonlinear_basis(
        rng_nonlinear,
        features=features,
        measure=measure,
        rank=nonlinear_rank if spec.nonlinear else 0,
    )
    latent = rng_latent.normal(
        size=(spec.authors, spec.condition_dimensions),
    )
    if spec.null_authors:
        latent.fill(0.0)

    preference = float(spec.choice_scale) * (
        latent
        if spec.shared_latent
        else rng_parameters.normal(size=latent.shape)
    )
    if spec.null_authors:
        preference.fill(0.0)
    transitions = np.asarray([
        _choice_transition(
            features,
            measure,
            preference[author],
            spec.choice_inertia,
        )
        for author in range(spec.authors)
    ])
    stationary = np.asarray([
        _stationary(transitions[author])
        for author in range(spec.authors)
    ])

    position = float(spec.author_scale) * rng_parameters.normal(
        size=(spec.authors, spec.response_dimensions),
    )
    response = float(spec.response_scale) * rng_parameters.normal(
        size=(
            spec.authors,
            spec.response_dimensions,
            spec.condition_dimensions,
        ),
    )
    if spec.shared_latent:
        position += (
            float(spec.author_scale)
            * latent
            @ rng_parameters.normal(
                scale=0.35,
                size=(spec.condition_dimensions, spec.response_dimensions),
            )
        )
        response += (
            0.20
            * latent[:, None, :]
            * rng_parameters.normal(
                size=(1, spec.response_dimensions, spec.condition_dimensions),
            )
        )
    nonlinear_coefficients = float(spec.nonlinear_scale) * rng_parameters.normal(
        size=(
            spec.authors,
            spec.response_dimensions,
            nonlinear_basis.shape[1],
        ),
    )
    if spec.null_authors:
        position.fill(0.0)
        response.fill(0.0)
        nonlinear_coefficients.fill(0.0)

    nonlinear_field = np.einsum(
        "ck,upk->ucp",
        nonlinear_basis,
        nonlinear_coefficients,
    )
    response_field = (
        position[:, None, :]
        + np.einsum("cq,upq->ucp", features, response)
        + nonlinear_field
    )
    origin = rng_origin.normal(
        scale=0.30,
        size=(spec.conditions, spec.response_dimensions),
    )
    state = _states(
        rng_state,
        authors=spec.authors,
        occasions=spec.occasions,
        dimensions=spec.response_dimensions,
        scale=spec.state_scale,
    )
    author_multiplier = None
    if spec.heteroskedastic:
        anchor = latent[:, 0]
        author_multiplier = np.clip(np.exp(0.22 * anchor), 0.55, 1.80)

    fixed_train = _fixed_responses(
        rng_fixed_train,
        origin=origin,
        field=response_field,
        state=state,
        repeats=spec.fixed_repeats_train,
        scale=spec.noise_scale,
        heavy_tail=spec.heavy_tail,
        author_multiplier=author_multiplier,
    )
    fixed_test = _fixed_responses(
        rng_fixed_test,
        origin=origin,
        field=response_field,
        state=state,
        repeats=spec.fixed_repeats_test,
        scale=spec.noise_scale,
        heavy_tail=spec.heavy_tail,
        author_multiplier=author_multiplier,
    )
    if spec.missing_common_support:
        fixed_train = _apply_missing_support(
            fixed_train,
            condition_dimensions=spec.condition_dimensions,
        )
        fixed_test = _apply_missing_support(
            fixed_test,
            condition_dimensions=spec.condition_dimensions,
        )

    reference = _reference_responses(
        rng_reference,
        origin=origin,
        authors=spec.reference_authors,
        occasions=max(spec.occasions, 2),
        repeats=spec.fixed_repeats_train,
        state_scale=spec.state_scale,
        noise_scale=spec.noise_scale,
        heavy_tail=spec.heavy_tail,
    )
    free_train = _draw_choice_sequences(
        rng_choice_train,
        transitions,
        stationary,
        spec.free_events_train,
    )
    free_test = _draw_choice_sequences(
        rng_choice_test,
        transitions,
        stationary,
        spec.free_events_test,
    )

    base_transition = _choice_transition(
        features,
        measure,
        np.zeros(spec.condition_dimensions),
        spec.choice_inertia,
    )
    information_choice = np.sum(
        stationary[:, :, None]
        * transitions
        * np.log((transitions + 1e-12) / (base_transition[None] + 1e-12)),
        axis=(1, 2),
    )
    information_response = (
        0.5
        * np.sum(
            stationary[:, :, None] * response_field**2,
            axis=(1, 2),
        )
        / max(spec.noise_scale**2, 1e-12)
    )
    signature = np.column_stack([
        information_choice,
        information_response,
        np.linalg.norm(response.reshape(spec.authors, -1), axis=1),
        np.linalg.norm(nonlinear_field.reshape(spec.authors, -1), axis=1),
    ])

    observed = M3ObservedPacket(
        free_conditions_train=free_train,
        free_conditions_test=free_test,
        fixed_responses_train=fixed_train,
        fixed_responses_test=fixed_test,
        reference_responses=reference,
    )
    truth = M3TruthPacket(
        choice_stationary=stationary,
        choice_transition=transitions,
        author_position=position,
        response_operator=response,
        nonlinear_field=nonlinear_field,
        occasion_state=state,
        response_field=response_field,
        information_choice=information_choice,
        information_response=information_response,
        microscopic_signature=signature,
    )
    manifest = M3DesignManifest(
        condition_features=features,
        reference_measure=measure,
        fixed_phase_randomized=True,
        reference_version=f"m3-reference-seed-{seed}",
    )
    return observed, truth, manifest


def same_occupancy_different_transition(
    stationary: np.ndarray,
    *,
    first_inertia: float,
    second_inertia: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return two transition kernels with one stationary distribution."""
    pi = np.asarray(stationary, dtype=float)
    pi = pi / pi.sum()
    base = np.broadcast_to(pi, (len(pi), len(pi)))
    first = (1.0 - first_inertia) * base + first_inertia * np.eye(len(pi))
    second = (1.0 - second_inertia) * base + second_inertia * np.eye(len(pi))
    return first, second


def stable_state_alias_counterexample(
    *,
    seed: int,
    authors: int = 32,
    dimensions: int = 4,
) -> dict[str, np.ndarray]:
    """Build observationally identical stable-position/state decompositions."""
    rng = np.random.default_rng(seed)
    total = rng.normal(size=(authors, dimensions))
    noise = rng.normal(scale=0.2, size=(authors, 1, dimensions))
    observed = total[:, None] + noise
    return {
        "observed_world_a": observed.copy(),
        "observed_world_b": observed.copy(),
        "position_world_a": total.copy(),
        "state_world_a": np.zeros_like(total),
        "position_world_b": np.zeros_like(total),
        "state_world_b": total.copy(),
    }
