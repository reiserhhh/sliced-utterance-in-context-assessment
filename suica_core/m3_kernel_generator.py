"""Two-phase microscopic state-choice-response worlds for SUICA M3.

The free phase has an event-level state-choice chain. The fixed phase samples
conditioned vector responses under occasion states. Hidden random-Fourier
emission functions and discrete micro-codes are never exposed to the estimator.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.special import softmax

from .m3_kernel_contracts import (
    M3KernelDesign,
    M3KernelObserved,
    M3KernelTruth,
)


@dataclass(frozen=True)
class M3KernelWorldSpec:
    """One two-phase microkernel world specification."""

    authors: int = 72
    reference_authors: int = 120
    conditions: int = 16
    coordinate_dimensions: int = 2
    response_dimensions: int = 6
    emission_codes: int = 12
    states: int = 3
    train_occasions: int = 12
    test_occasions: int = 12
    fixed_repeats: int = 2
    free_events: int = 80
    author_scale: float = 0.55
    nonlinear_scale: float = 0.35
    condition_frequency: float = 1.0
    state_scale: float = 0.70
    choice_scale: float = 0.65
    readout_noise: float = 0.15
    heavy_tail: bool = False
    heteroskedastic: bool = False
    null_authors: bool = False
    missing_common_support: bool = False
    single_occasion: bool = False
    rank_deficient: bool = False
    fixed_phase_randomized: bool = True
    missingness_mechanism: str = "MCAR"
    representation_drift: bool = False
    reference_mismatch: bool = False
    technical_streams_independent: bool = True
    coarse_blocks_condition_homogeneous: bool = True


def _condition_grid(
    conditions: int,
    dimensions: int,
    *,
    rank_deficient: bool,
) -> np.ndarray:
    side = int(round(np.sqrt(conditions)))
    if dimensions != 2 or side * side != conditions:
        index = np.linspace(-1.0, 1.0, conditions)
        coordinates = np.column_stack([
            index ** (power + 1)
            for power in range(dimensions)
        ])
    else:
        axis = np.linspace(-1.0, 1.0, side)
        coordinates = np.asarray([
            (left, right)
            for left in axis
            for right in axis
        ])
    coordinates -= coordinates.mean(axis=0, keepdims=True)
    scale = coordinates.std(axis=0, ddof=0)
    scale[scale < 1e-8] = 1.0
    coordinates /= scale
    if rank_deficient and dimensions > 1:
        coordinates[:, -1] = coordinates[:, 0]
    return coordinates


def _train_mask(coordinates: np.ndarray) -> np.ndarray:
    radius = np.max(np.abs(coordinates), axis=1)
    mask = radius > np.quantile(radius, 0.20)
    if mask.sum() >= len(mask) - 1:
        mask[np.arange(len(mask)) % 4 == 1] = False
    return mask


def _stationary(transition: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eig(np.asarray(transition).T)
    vector = np.real(vectors[:, int(np.argmin(np.abs(values - 1.0)))])
    if vector.sum() < 0.0:
        vector *= -1.0
    vector = np.maximum(vector, 0.0)
    return vector / vector.sum()


def _state_transition(states: int) -> np.ndarray:
    transition = np.full((states, states), 0.35 / max(states - 1, 1))
    np.fill_diagonal(transition, 0.65)
    return transition / transition.sum(axis=1, keepdims=True)


def _hidden_features(
    rng: np.random.Generator,
    coordinates: np.ndarray,
    rank: int,
    *,
    frequency_scale: float,
) -> np.ndarray:
    frequencies = rng.normal(
        scale=frequency_scale,
        size=(coordinates.shape[1], rank),
    )
    phases = rng.uniform(0.0, 2.0 * np.pi, size=rank)
    return np.sqrt(2.0 / rank) * np.cos(
        coordinates @ frequencies + phases
    )


def _author_choice_kernels(
    *,
    coordinates: np.ndarray,
    latent: np.ndarray,
    states: int,
    choice_scale: float,
) -> np.ndarray:
    authors, dimensions = latent.shape
    conditions = len(coordinates)
    state_direction = np.linspace(-0.6, 0.6, states)
    kernels = np.empty(
        (authors, states, conditions, conditions),
        dtype=float,
    )
    similarity = coordinates @ coordinates.T / max(dimensions, 1)
    for author in range(authors):
        preference = choice_scale * coordinates @ latent[author]
        for state in range(states):
            destination = preference + state_direction[state] * coordinates[:, 0]
            logits = destination[None] + 0.30 * similarity
            kernels[author, state] = softmax(logits, axis=1)
    return kernels


def _joint_choice_truth(
    kernels: np.ndarray,
    state_transition: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute exact choice marginals from the joint state-choice chain."""
    authors, states, conditions, _ = kernels.shape
    occupancy = np.empty((authors, conditions))
    transition = np.empty((authors, conditions, conditions))
    joint_stationary = np.empty((authors, states, conditions))
    for author in range(authors):
        stationary = np.full(
            (states, conditions),
            1.0 / (states * conditions),
        )
        for _ in range(10_000):
            updated = np.einsum(
                "sc,st,tcd->td",
                stationary,
                state_transition,
                kernels[author],
            )
            if np.max(np.abs(updated - stationary)) < 1e-13:
                stationary = updated
                break
            stationary = updated
        stationary /= stationary.sum()
        joint_stationary[author] = stationary
        occupancy[author] = stationary.sum(axis=0)
        choice_joint = np.einsum(
            "sc,st,tcd->cd",
            stationary,
            state_transition,
            kernels[author],
        )
        transition[author] = choice_joint / np.maximum(
            occupancy[author, :, None],
            1e-12,
        )
    return occupancy, transition, joint_stationary


def _emission_probabilities(
    *,
    base_logits: np.ndarray,
    hidden: np.ndarray,
    author_bias: np.ndarray,
    author_hidden: np.ndarray,
    state_logits: np.ndarray,
) -> np.ndarray:
    # author x state x condition x code
    logits = (
        base_logits[None, None]
        + author_bias[:, None, None]
        + np.einsum("cr,urj->ucj", hidden, author_hidden)[:, None]
        + state_logits[None, :, None]
    )
    return softmax(logits, axis=-1)


def _expected_vectors(
    probabilities: np.ndarray,
    prototypes: np.ndarray,
) -> np.ndarray:
    return np.einsum("uscj,jp->uscp", probabilities, prototypes)


def _draw_state_sequences(
    rng: np.random.Generator,
    transition: np.ndarray,
    *,
    authors: int,
    occasions: int,
) -> np.ndarray:
    stationary = _stationary(transition)
    sequence = np.empty((authors, occasions), dtype=np.int16)
    for author in range(authors):
        sequence[author, 0] = rng.choice(len(stationary), p=stationary)
        for occasion in range(1, occasions):
            sequence[author, occasion] = rng.choice(
                len(stationary),
                p=transition[sequence[author, occasion - 1]],
            )
    return sequence


def _draw_choice(
    rng: np.random.Generator,
    kernels: np.ndarray,
    state_transition: np.ndarray,
    joint_stationary: np.ndarray,
    *,
    occasions: int,
    events: int,
) -> np.ndarray:
    authors, states, conditions, _ = kernels.shape
    output = np.empty((authors, occasions, events), dtype=np.int16)
    for author in range(authors):
        for occasion in range(occasions):
            initial = int(rng.choice(
                states * conditions,
                p=joint_stationary[author].ravel(),
            ))
            state = initial // conditions
            condition = initial % conditions
            output[author, occasion, 0] = condition
            for event in range(1, events):
                state = int(rng.choice(
                    states,
                    p=state_transition[state],
                ))
                condition = int(rng.choice(
                    conditions,
                    p=kernels[author, state, condition],
                ))
                output[author, occasion, event] = condition
    return output


def _readout_noise(
    rng: np.random.Generator,
    shape: tuple[int, ...],
    *,
    scale: float,
    heavy_tail: bool,
    multiplier: np.ndarray | None,
) -> np.ndarray:
    if heavy_tail:
        values = rng.standard_t(df=5.0, size=shape) / np.sqrt(5.0 / 3.0)
    else:
        values = rng.normal(size=shape)
    if multiplier is not None:
        values *= multiplier.reshape(
            (len(multiplier),) + (1,) * (len(shape) - 1)
        )
    return scale * values


def _draw_fixed(
    rng: np.random.Generator,
    expected: np.ndarray,
    probabilities: np.ndarray,
    prototypes: np.ndarray,
    states: np.ndarray,
    *,
    repeats: int,
    noise_scale: float,
    heavy_tail: bool,
    multiplier: np.ndarray | None,
) -> np.ndarray:
    authors, occasions = states.shape
    conditions = probabilities.shape[2]
    dimensions = prototypes.shape[1]
    output = np.empty(
        (authors, occasions, conditions, repeats, dimensions),
        dtype=float,
    )
    for author in range(authors):
        for occasion in range(occasions):
            state = int(states[author, occasion])
            for condition in range(conditions):
                codes = rng.choice(
                    len(prototypes),
                    size=repeats,
                    p=probabilities[author, state, condition],
                )
                output[author, occasion, condition] = prototypes[codes]
    output += _readout_noise(
        rng,
        output.shape,
        scale=noise_scale,
        heavy_tail=heavy_tail,
        multiplier=multiplier,
    )
    return output


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


def _missing_support(
    values: np.ndarray,
    *,
    train_mask: np.ndarray,
    coordinate_dimensions: int,
) -> np.ndarray:
    output = values.copy()
    available = np.flatnonzero(train_mask)
    for author in range(len(output)):
        keep = available[
            (np.arange(len(available)) + author) % 3 == 0
        ][: max(coordinate_dimensions, 1)]
        remove = np.ones(output.shape[2], dtype=bool)
        remove[keep] = False
        output[author, :, remove] = np.nan
    return output


def generate_m3_kernel_world(
    *,
    spec: M3KernelWorldSpec,
    seed: int,
) -> tuple[M3KernelObserved, M3KernelTruth, M3KernelDesign]:
    """Generate one separated two-phase microkernel world."""
    streams = [
        np.random.default_rng(item)
        for item in np.random.SeedSequence(seed).spawn(18)
    ]
    (
        rng_hidden,
        rng_prototypes,
        rng_base,
        rng_latent,
        rng_author,
        rng_state_logits,
        rng_train_state,
        rng_test_state,
        rng_ref_train_state,
        rng_ref_test_state,
        rng_choice_train,
        rng_choice_test,
        rng_fixed_train,
        rng_fixed_test,
        rng_ref_train,
        rng_ref_test,
        rng_rotation,
        _rng_unused,
    ) = streams
    coordinates = _condition_grid(
        spec.conditions,
        spec.coordinate_dimensions,
        rank_deficient=spec.rank_deficient,
    )
    measure = np.full(spec.conditions, 1.0 / spec.conditions)
    train_mask = _train_mask(coordinates)
    hidden = _hidden_features(
        rng_hidden,
        coordinates,
        rank=5,
        frequency_scale=spec.condition_frequency,
    )
    prototypes = rng_prototypes.normal(
        size=(spec.emission_codes, spec.response_dimensions)
    )
    prototypes -= prototypes.mean(axis=0, keepdims=True)
    prototypes /= np.maximum(
        prototypes.std(axis=0, keepdims=True),
        1e-8,
    )
    base_logits = (
        hidden @ rng_base.normal(
            scale=0.45,
            size=(hidden.shape[1], spec.emission_codes),
        )
    )
    state_logits = float(spec.state_scale) * rng_state_logits.normal(
        size=(spec.states, spec.emission_codes)
    )
    state_logits -= state_logits.mean(axis=0, keepdims=True)
    latent = rng_latent.normal(
        size=(spec.authors, spec.coordinate_dimensions)
    )
    if spec.null_authors:
        latent.fill(0.0)
    author_bias = float(spec.author_scale) * (
        latent @ rng_author.normal(
            scale=0.35,
            size=(spec.coordinate_dimensions, spec.emission_codes),
        )
        + rng_author.normal(
            scale=0.30,
            size=(spec.authors, spec.emission_codes),
        )
    )
    author_hidden = float(spec.author_scale) * rng_author.normal(
        scale=spec.nonlinear_scale,
        size=(spec.authors, hidden.shape[1], spec.emission_codes),
    )
    if spec.null_authors:
        author_bias.fill(0.0)
        author_hidden.fill(0.0)

    probabilities = _emission_probabilities(
        base_logits=base_logits,
        hidden=hidden,
        author_bias=author_bias,
        author_hidden=author_hidden,
        state_logits=state_logits,
    )
    reference_probabilities = _emission_probabilities(
        base_logits=base_logits,
        hidden=hidden,
        author_bias=np.zeros((1, spec.emission_codes)),
        author_hidden=np.zeros(
            (1, hidden.shape[1], spec.emission_codes)
        ),
        state_logits=state_logits,
    )
    expected = _expected_vectors(probabilities, prototypes)
    reference_expected = _expected_vectors(
        reference_probabilities,
        prototypes,
    )[0]
    state_transition = _state_transition(spec.states)
    state_stationary = _stationary(state_transition)
    response_field = (
        np.einsum("s,uscp->ucp", state_stationary, expected)
        - np.einsum("s,scp->cp", state_stationary, reference_expected)[None]
    )
    position, projection, nonlinear = _project_field(
        response_field,
        coordinates,
        measure,
    )

    choice_kernels = _author_choice_kernels(
        coordinates=coordinates,
        latent=latent,
        states=spec.states,
        choice_scale=0.0 if spec.null_authors else spec.choice_scale,
    )
    (
        choice_stationary,
        choice_transition,
        choice_joint_stationary,
    ) = _joint_choice_truth(
        choice_kernels,
        state_transition,
    )
    train_occasions = 1 if spec.single_occasion else spec.train_occasions
    train_state = _draw_state_sequences(
        rng_train_state,
        state_transition,
        authors=spec.authors,
        occasions=train_occasions,
    )
    test_state = _draw_state_sequences(
        rng_test_state,
        state_transition,
        authors=spec.authors,
        occasions=spec.test_occasions,
    )
    free_train = _draw_choice(
        rng_choice_train,
        choice_kernels,
        state_transition,
        choice_joint_stationary,
        occasions=train_occasions,
        events=spec.free_events,
    )
    free_test = _draw_choice(
        rng_choice_test,
        choice_kernels,
        state_transition,
        choice_joint_stationary,
        occasions=spec.test_occasions,
        events=spec.free_events,
    )
    multiplier = None
    if spec.heteroskedastic:
        multiplier = np.clip(np.exp(0.20 * latent[:, 0]), 0.60, 1.70)
    fixed_train = _draw_fixed(
        rng_fixed_train,
        expected,
        probabilities,
        prototypes,
        train_state,
        repeats=spec.fixed_repeats,
        noise_scale=spec.readout_noise,
        heavy_tail=spec.heavy_tail,
        multiplier=multiplier,
    )
    fixed_test = _draw_fixed(
        rng_fixed_test,
        expected,
        probabilities,
        prototypes,
        test_state,
        repeats=spec.fixed_repeats,
        noise_scale=spec.readout_noise,
        heavy_tail=spec.heavy_tail,
        multiplier=multiplier,
    )
    fixed_train[:, :, ~train_mask] = np.nan
    if spec.missing_common_support:
        fixed_train = _missing_support(
            fixed_train,
            train_mask=train_mask,
            coordinate_dimensions=spec.coordinate_dimensions,
        )

    reference_train_state = _draw_state_sequences(
        rng_ref_train_state,
        state_transition,
        authors=spec.reference_authors,
        occasions=train_occasions,
    )
    reference_test_state = _draw_state_sequences(
        rng_ref_test_state,
        state_transition,
        authors=spec.reference_authors,
        occasions=spec.test_occasions,
    )
    ref_probability = np.broadcast_to(
        reference_probabilities,
        (
            spec.reference_authors,
            spec.states,
            spec.conditions,
            spec.emission_codes,
        ),
    )
    reference_train = _draw_fixed(
        rng_ref_train,
        np.broadcast_to(
            reference_expected,
            (
                spec.reference_authors,
                spec.states,
                spec.conditions,
                spec.response_dimensions,
            ),
        ),
        ref_probability,
        prototypes,
        reference_train_state,
        repeats=spec.fixed_repeats,
        noise_scale=spec.readout_noise,
        heavy_tail=spec.heavy_tail,
        multiplier=None,
    )
    reference_test = _draw_fixed(
        rng_ref_test,
        np.broadcast_to(
            reference_expected,
            (
                spec.reference_authors,
                spec.states,
                spec.conditions,
                spec.response_dimensions,
            ),
        ),
        ref_probability,
        prototypes,
        reference_test_state,
        repeats=spec.fixed_repeats,
        noise_scale=spec.readout_noise,
        heavy_tail=spec.heavy_tail,
        multiplier=None,
    )
    reference_train[:, :, ~train_mask] = np.nan

    if spec.representation_drift:
        rotation = np.linalg.qr(
            rng_rotation.normal(
                size=(spec.response_dimensions, spec.response_dimensions)
            )
        )[0]
        fixed_test = fixed_test @ rotation.T
        reference_test = reference_test @ rotation.T

    train_state_effect = np.empty(
        (spec.authors, train_occasions, spec.response_dimensions)
    )
    test_state_effect = np.empty(
        (spec.authors, spec.test_occasions, spec.response_dimensions)
    )
    average_author = np.einsum(
        "s,uscp->ucp",
        state_stationary,
        expected,
    )
    q_train = measure * train_mask
    q_train /= q_train.sum()
    for author in range(spec.authors):
        for occasion, state in enumerate(train_state[author]):
            deviation = (
                expected[author, state] - average_author[author]
            )
            train_state_effect[author, occasion] = np.einsum(
                "c,cp->p",
                q_train,
                deviation,
            )
        for occasion, state in enumerate(test_state[author]):
            deviation = (
                expected[author, state] - average_author[author]
            )
            test_state_effect[author, occasion] = np.einsum(
                "c,cp->p",
                measure,
                deviation,
            )

    design = M3KernelDesign(
        condition_coordinates=coordinates,
        reference_measure=measure,
        train_condition_mask=train_mask,
        fixed_phase_randomized=spec.fixed_phase_randomized,
        missingness_mechanism=spec.missingness_mechanism,
        train_reference_version="P0-reference-v1",
        test_reference_version=(
            "P0-reference-v2"
            if spec.reference_mismatch
            else "P0-reference-v1"
        ),
        train_representation_version="P0-representation-v1",
        test_representation_version=(
            "P0-representation-v2"
            if spec.representation_drift
            else "P0-representation-v1"
        ),
        technical_streams_independent=spec.technical_streams_independent,
        coarse_blocks_condition_homogeneous=(
            spec.coarse_blocks_condition_homogeneous
        ),
    )
    observed = M3KernelObserved(
        choice_train=free_train,
        choice_test=free_test,
        fixed_train=fixed_train,
        fixed_test=fixed_test,
        reference_train=reference_train,
        reference_test=reference_test,
    )
    emission_signature = np.column_stack([
        np.linalg.norm(author_bias, axis=1),
        np.linalg.norm(author_hidden.reshape(spec.authors, -1), axis=1),
        np.mean(
            -np.sum(
                probabilities * np.log(probabilities + 1e-12),
                axis=-1,
            ),
            axis=(1, 2),
        ),
    ])
    truth = M3KernelTruth(
        choice_stationary=choice_stationary,
        choice_transition=choice_transition,
        response_field=response_field,
        author_position=position,
        response_projection=projection,
        nonlinear_field=nonlinear,
        train_state_effect=train_state_effect,
        test_state_effect=test_state_effect,
        emission_signature=emission_signature,
    )
    return observed, truth, design
