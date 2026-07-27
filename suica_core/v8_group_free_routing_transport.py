"""Group-free routing transport and missingness corrections for V3.7C."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
from sklearn.metrics import roc_auc_score

from .v8_author_routing_operator import (
    fit_reference_router,
    heldout_prediction_metrics,
    ilr,
    ilr_basis,
    multivariate_reliability,
    predict_reference_router,
)
from .v8_blind_junction_localization import (
    BlindJunctionSpec,
    branch_directions,
    infer_route_branches,
    localize_trajectories,
    simulate_no_junction_trajectories,
)


@dataclass(frozen=True)
class TransportPathSpec:
    """Path family shared by transport and localization experiments."""

    path_points: int = 25
    junction_min: int = 9
    junction_max: int = 15
    locator_window: int = 4
    threshold: float = 0.30
    branches: int = 4


def seed_sequence_int(sequence: np.random.SeedSequence) -> int:
    """Return one reproducible uint64 seed from a spawned sequence."""
    return int(sequence.generate_state(1, dtype=np.uint64)[0])


def resample_routing_counts(
    sample: dict[str, Any],
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Draw an independent count panel from frozen routing probabilities."""
    probability = np.asarray(sample["probability"], dtype=float)
    trials = np.asarray(sample["trials"], dtype=np.int16)
    cumulative = np.cumsum(probability, axis=-1)
    eye = np.eye(probability.shape[-1], dtype=np.int16)
    counts = np.zeros_like(probability, dtype=np.int16)
    for draw in range(int(trials.max(initial=0))):
        uniform = rng.random(trials.shape)
        outcome = np.sum(uniform[..., None] > cumulative, axis=-1)
        active = trials > draw
        counts += eye[outcome] * active[..., None]
    result = dict(sample)
    result["counts"] = counts
    result["trials"] = trials.copy()
    return result


def fit_group_free_denoiser(
    left: np.ndarray,
    right: np.ndarray,
    *,
    rank: int,
) -> dict[str, np.ndarray | int | float]:
    """Estimate a PSD cross-session subspace without groups or labels."""
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    if x.shape != y.shape:
        raise ValueError("profile halves must have identical shape")
    if rank < 0 or rank > x.shape[1]:
        raise ValueError("invalid denoiser rank")
    center = 0.5 * (x.mean(axis=0) + y.mean(axis=0))
    x_centered = x - center
    y_centered = y - center
    covariance = (
        x_centered.T @ y_centered
        + y_centered.T @ x_centered
    ) / (2.0 * max(len(x) - 1, 1))
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    positive_rank = int(np.sum(eigenvalues > 1e-10))
    used_rank = min(rank, positive_rank)
    basis = eigenvectors[:, :used_rank]
    half_difference = 0.5 * (x_centered - y_centered)
    noise_covariance = (
        half_difference.T @ half_difference
    ) / max(len(x) - 1, 1)
    noise_energy = (
        np.diag(basis.T @ noise_covariance @ basis)
        if used_rank > 0 else np.asarray([], dtype=float)
    )
    signal_energy = np.clip(eigenvalues[:used_rank], 0.0, None)
    spectral_weight = signal_energy / np.maximum(
        signal_energy + noise_energy,
        1e-12,
    )
    projector = (
        basis @ np.diag(spectral_weight) @ basis.T
        if used_rank > 0 else np.zeros_like(covariance)
    )
    condition = (
        float(eigenvalues[0] / eigenvalues[used_rank - 1])
        if used_rank > 0 else float("inf")
    )
    return {
        "center": center,
        "basis": basis,
        "projector": projector,
        "eigenvalues": eigenvalues,
        "noise_energy": noise_energy,
        "spectral_weight": spectral_weight,
        "requested_rank": int(rank),
        "rank": used_rank,
        "condition_number": condition,
    }


def apply_group_free_denoiser(
    profile: np.ndarray,
    denoiser: dict[str, Any],
) -> np.ndarray:
    """Project profiles into a discovery-only group-free stable subspace."""
    values = np.asarray(profile, dtype=float)
    center = np.asarray(denoiser["center"], dtype=float)
    projector = np.asarray(denoiser["projector"], dtype=float)
    return center + (values - center) @ projector


def _selected_sessions(sessions: int | Iterable[int]) -> np.ndarray:
    if isinstance(sessions, (int, np.integer)):
        return np.asarray([int(sessions)], dtype=int)
    return np.asarray(tuple(sessions), dtype=int)


def estimate_fixed_reference_profile(
    sample: dict[str, Any],
    context_indices: Iterable[int],
    *,
    reference_fit: dict[str, np.ndarray],
    sessions: int | Iterable[int] = (0, 1),
    method: str = "complete",
    propensity: np.ndarray | None = None,
) -> dict[str, Any]:
    """Estimate an author profile against one externally fixed Q reference."""
    contexts = np.asarray(tuple(context_indices), dtype=int)
    halves = _selected_sessions(sessions)
    counts = np.asarray(sample["counts"])[:, halves][:, :, contexts]
    trials = np.asarray(sample["trials"])[:, halves][:, :, contexts]
    valid = trials > 0
    available = valid.sum(axis=(1, 2))
    if np.any(available == 0):
        return {
            "status": "REFUSE_NONOVERLAP",
            "refused": True,
            "minimum_available_contexts": int(available.min()),
        }
    if method not in {"complete", "available", "ipw", "aipw"}:
        raise ValueError(f"unsupported profile method: {method}")

    if method in {"complete", "available"}:
        cell_probability = np.divide(
            counts,
            trials[..., None],
            out=np.zeros_like(counts, dtype=float),
            where=valid[..., None],
        )
    else:
        if propensity is None:
            propensity = np.asarray(
                sample["observation_probability"],
                dtype=float,
            )
        propensity = np.asarray(propensity)[:, halves][:, :, contexts]
        if np.min(propensity) < 0.05:
            return {
                "status": "REFUSE_POSITIVITY",
                "refused": True,
                "minimum_propensity": float(np.min(propensity)),
            }
        weighted = counts / np.maximum(propensity, 1e-8)
        if method == "ipw":
            denominator = weighted.sum(axis=-1)
            cell_probability = np.divide(
                weighted,
                denominator[..., None],
                out=np.zeros_like(weighted),
                where=denominator[..., None] > 0,
            )
        else:
            intended = np.asarray(
                sample["intended_trials"],
                dtype=float,
            )[:, halves][:, :, contexts]
            baseline = predict_reference_router(
                reference_fit,
                sample["contexts"]["all"][contexts],
            )
            baseline = baseline[None, None]
            weighted_observed = weighted.sum(axis=-1)
            augmented = (
                intended[..., None] * baseline
                + weighted
                - baseline * weighted_observed[..., None]
            )
            augmented = np.clip(augmented, 1e-6, None)
            cell_probability = augmented / augmented.sum(
                axis=-1,
                keepdims=True,
            )
        valid = (
            np.asarray(sample["intended_trials"])[:, halves][:, :, contexts]
            > 0
        )
        available = valid.sum(axis=(1, 2))

    author_probability = (
        (cell_probability * valid[..., None]).sum(axis=(1, 2))
        / available[..., None]
    )
    author_probability = np.clip(author_probability, 1e-6, None)
    author_probability /= author_probability.sum(axis=-1, keepdims=True)
    reference_probability = predict_reference_router(
        reference_fit,
        sample["contexts"]["all"][contexts],
    ).mean(axis=0)
    basis = ilr_basis(author_probability.shape[-1])
    profile = (
        ilr(author_probability, basis)
        - ilr(reference_probability, basis)[None]
    )
    intended_total = (
        np.asarray(sample.get("intended_trials", sample["trials"]))[
            :, halves
        ][:, :, contexts]
        .sum(axis=(1, 2))
    )
    observed_total = trials.sum(axis=(1, 2))
    return {
        "status": "FIXED_REFERENCE_PROFILE_READY",
        "refused": False,
        "profile": profile.reshape(len(profile), -1),
        "cell_profile": profile,
        "probability": author_probability,
        "reference_probability": reference_probability,
        "minimum_total_trials": float(np.min(intended_total)),
        "mean_available_fraction": float(
            observed_total.sum() / max(intended_total.sum(), 1.0)
        ),
    }


def true_fixed_reference_profile(
    sample: dict[str, Any],
    context_indices: Iterable[int],
    *,
    reference_fit: dict[str, np.ndarray],
) -> np.ndarray:
    """Return the scorer-only true profile against the fixed reference."""
    contexts = np.asarray(tuple(context_indices), dtype=int)
    probability = np.asarray(sample["probability"])[:, :, contexts].mean(
        axis=(1, 2)
    )
    reference = predict_reference_router(
        reference_fit,
        sample["contexts"]["all"][contexts],
    ).mean(axis=0)
    basis = ilr_basis(probability.shape[-1])
    return (
        ilr(probability, basis) - ilr(reference, basis)[None]
    ).reshape(len(probability), -1)


def _center(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    return matrix - matrix.mean(axis=0, keepdims=True)


def flat_correlation(left: np.ndarray, right: np.ndarray) -> float:
    """Return a global-center flattened correlation."""
    x = _center(left).ravel()
    y = _center(right).ravel()
    if np.std(x) <= 1e-12 or np.std(y) <= 1e-12:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _row_normalize(values: np.ndarray) -> np.ndarray:
    matrix = _center(values)
    return matrix / np.maximum(
        np.linalg.norm(matrix, axis=1, keepdims=True),
        1e-12,
    )


def group_free_pairing_metrics(
    left: np.ndarray,
    right: np.ndarray,
    *,
    neighbor_count: int,
) -> dict[str, float]:
    """Score identity against all and discovery-nearest hard negatives."""
    x = _row_normalize(left)
    y = _row_normalize(right)
    similarity = x @ y.T
    identity = np.eye(len(x), dtype=bool)
    positive = np.diag(similarity)
    all_negative = similarity[~identity]
    discovery_similarity = x @ x.T
    np.fill_diagonal(discovery_similarity, -np.inf)
    count = min(neighbor_count, len(x) - 1)
    neighbors = np.argpartition(
        discovery_similarity,
        kth=len(x) - count,
        axis=1,
    )[:, -count:]
    local_negative = similarity[
        np.arange(len(x))[:, None],
        neighbors,
    ].ravel()

    def auc(negative: np.ndarray) -> float:
        target = np.concatenate([
            np.ones(len(positive), dtype=int),
            np.zeros(len(negative), dtype=int),
        ])
        return float(
            roc_auc_score(
                target,
                np.concatenate([positive, negative]),
            )
        )

    return {
        "same_author_auc": auc(all_negative),
        "local_neighbor_auc": auc(local_negative),
        "top1": float(
            np.mean(similarity.argmax(axis=1) == np.arange(len(x)))
        ),
    }


def true_group_sensitivity_auc(
    left: np.ndarray,
    right: np.ndarray,
    labels: np.ndarray,
) -> float:
    """Open true groups only for a post-primary scorer sensitivity."""
    x = _row_normalize(left)
    y = _row_normalize(right)
    similarity = x @ y.T
    labels = np.asarray(labels)
    identity = np.eye(len(x), dtype=bool)
    same_group = labels[:, None] == labels[None]
    positive = np.diag(similarity)
    negative = similarity[same_group & ~identity]
    target = np.concatenate([
        np.ones(len(positive), dtype=int),
        np.zeros(len(negative), dtype=int),
    ])
    return float(
        roc_auc_score(target, np.concatenate([positive, negative]))
    )


def _perpendicular(values: np.ndarray) -> np.ndarray:
    return np.column_stack([-values[:, 1], values[:, 0]])


def _rotate(values: np.ndarray, angle: np.ndarray) -> np.ndarray:
    cosine = np.cos(angle)
    sine = np.sin(angle)
    return np.column_stack([
        cosine * values[:, 0] - sine * values[:, 1],
        sine * values[:, 0] + cosine * values[:, 1],
    ])


def simulate_transport_paths(
    incoming: np.ndarray,
    outgoing: np.ndarray,
    cue: np.ndarray,
    *,
    rng: np.random.Generator,
    spec: TransportPathSpec,
    mechanism: str,
) -> dict[str, np.ndarray]:
    """Generate core, transported, or high-noise transition paths."""
    incoming = np.asarray(incoming, dtype=int)
    outgoing = np.asarray(outgoing, dtype=int)
    cue = np.asarray(cue, dtype=int)
    n = len(incoming)
    directions = branch_directions(spec.branches)
    angle_sd = 0.08 if mechanism == "core" else 0.14
    before = _rotate(
        directions[incoming],
        rng.normal(scale=angle_sd, size=n),
    )
    after = _rotate(
        directions[outgoing],
        rng.normal(scale=angle_sd, size=n),
    )
    junction = rng.integers(
        spec.junction_min,
        spec.junction_max + 1,
        size=n,
    )
    speed = rng.uniform(0.75, 1.25, size=n)
    time = np.arange(spec.path_points)[None]
    offset = time - junction[:, None]
    path = np.where(
        (offset <= 0)[..., None],
        offset[..., None] * before[:, None],
        offset[..., None] * after[:, None],
    )
    path *= speed[:, None, None]
    phase = rng.uniform(0.0, 2.0 * np.pi, size=n)
    drift = np.column_stack([np.cos(phase), np.sin(phase)])
    smooth = 0.10 * np.sin(
        np.pi * (time + 1.0) / (spec.path_points + 1.0)
    )
    path += smooth[..., None] * drift[:, None]

    rows = np.arange(n)
    lateral = _perpendicular(before)
    if mechanism == "high_noise":
        inner = rng.uniform(0.28, 0.55, size=n)
        cusp = rng.uniform(0.12, 0.28, size=n)
        noise = 0.040
    elif mechanism == "out_of_family":
        inner = rng.uniform(0.25, 0.55, size=n)
        cusp = rng.uniform(0.14, 0.30, size=n)
        noise = 0.020
    else:
        inner = rng.uniform(0.25, 0.45, size=n)
        cusp = rng.uniform(0.14, 0.30, size=n)
        noise = 0.015
    path[rows, junction - 2] = -1.20 * speed[:, None] * before
    path[rows, junction - 1] = -inner[:, None] * speed[:, None] * before
    path[rows, junction] = cusp[:, None] * speed[:, None] * lateral
    path[rows, junction + 1] = inner[:, None] * speed[:, None] * after
    path[rows, junction + 2] = 1.20 * speed[:, None] * after
    if mechanism == "out_of_family":
        alternate = _perpendicular(after)
        multi = rng.random(n) < 0.5
        path[rows[multi], junction[multi] + 1] += (
            0.11 * speed[multi, None] * alternate[multi]
        )
        asymmetric = ~multi
        path[rows[asymmetric], junction[asymmetric] - 1] += (
            0.09 * speed[asymmetric, None] * lateral[asymmetric]
        )
    distractor = rng.random(n) < 0.40
    distractor_at = np.maximum(junction - 5, 2)
    cue_lateral = _perpendicular(directions[cue])
    path[rows[distractor], distractor_at[distractor]] += (
        0.42 * speed[distractor, None] * cue_lateral[distractor]
    )
    path += rng.normal(scale=noise, size=path.shape)
    return {
        "trajectory": path.astype(np.float32),
        "junction": junction,
        "incoming": incoming,
        "outgoing": outgoing,
        "cue": cue,
    }


def _negative_paths(
    *,
    rng: np.random.Generator,
    count: int,
    spec: TransportPathSpec,
    noise: float,
) -> dict[str, np.ndarray]:
    blind_spec = BlindJunctionSpec(
        path_points=spec.path_points,
        junction_min=spec.junction_min,
        junction_max=spec.junction_max,
        locator_window=spec.locator_window,
        threshold=spec.threshold,
        trajectory_noise_sd=noise,
    )
    return simulate_no_junction_trajectories(
        seed=int(rng.integers(0, np.iinfo(np.int64).max)),
        count=count,
        spec=blind_spec,
    )


def transport_localization_metrics(
    *,
    rng: np.random.Generator,
    spec: TransportPathSpec,
    mechanism: str,
    positive_count: int,
    negative_count: int,
) -> dict[str, float | bool]:
    """Score unconditional localization and an isomorphic-label control."""
    incoming = rng.integers(0, spec.branches, size=positive_count)
    outgoing = rng.integers(0, spec.branches, size=positive_count)
    cue = rng.integers(0, spec.branches, size=positive_count)
    positive = simulate_transport_paths(
        incoming,
        outgoing,
        cue,
        rng=rng,
        spec=spec,
        mechanism=mechanism,
    )
    noise = 0.040 if mechanism == "high_noise" else 0.020
    negative = _negative_paths(
        rng=rng,
        count=negative_count,
        spec=spec,
        noise=noise,
    )
    detected_positive = localize_trajectories(
        positive["trajectory"],
        window=spec.locator_window,
        threshold=spec.threshold,
    )
    detected_negative = localize_trajectories(
        negative["trajectory"],
        window=spec.locator_window,
        threshold=spec.threshold,
    )
    raw_error = np.abs(
        detected_positive["location"] - positive["junction"]
    )
    correct = detected_positive["detected"] & (raw_error <= 2)
    unconditional_error = np.where(
        detected_positive["detected"],
        raw_error,
        spec.path_points,
    )
    detections = int(
        detected_positive["detected"].sum()
        + detected_negative["detected"].sum()
    )
    precision = float(correct.sum() / max(detections, 1))
    recall = float(correct.mean())
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall > 0 else 0.0
    )
    inferred_in, inferred_out = infer_route_branches(
        positive["trajectory"],
        detected_positive["location"],
        window=spec.locator_window,
        branches=spec.branches,
    )
    detected = detected_positive["detected"]

    iso_count = max(1000, positive_count)
    iso = simulate_transport_paths(
        rng.integers(0, spec.branches, size=iso_count),
        rng.integers(0, spec.branches, size=iso_count),
        rng.integers(0, spec.branches, size=iso_count),
        rng=rng,
        spec=spec,
        mechanism=mechanism,
    )
    iso_score = localize_trajectories(
        iso["trajectory"],
        window=spec.locator_window,
        threshold=spec.threshold,
    )["score"]
    iso_label = rng.integers(0, 2, size=iso_count)
    iso_auc = float(roc_auc_score(iso_label, iso_score))
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "unconditional_median_error": float(
            np.median(unconditional_error)
        ),
        "unconditional_p95_error": float(
            np.quantile(unconditional_error, 0.95)
        ),
        "false_junction_rate": float(
            detected_negative["detected"].mean()
        ),
        "incoming_accuracy_detected": float(
            np.mean(inferred_in[detected] == incoming[detected])
            if np.any(detected) else 0.0
        ),
        "outgoing_accuracy_detected": float(
            np.mean(inferred_out[detected] == outgoing[detected])
            if np.any(detected) else 0.0
        ),
        "isomorphic_auc": iso_auc,
        "isomorphic_refusal": bool(0.45 <= iso_auc <= 0.55),
    }


def localize_routing_counts(
    sample: dict[str, Any],
    *,
    rng: np.random.Generator,
    spec: TransportPathSpec,
    mechanism: str,
    batch_size: int = 20_000,
) -> tuple[dict[str, Any], dict[str, float]]:
    """Convert independent oracle counts into blind geometry-derived counts."""
    nonzero = np.argwhere(np.asarray(sample["counts"]) > 0)
    repeats = sample["counts"][tuple(nonzero.T)].astype(int)
    events = np.repeat(nonzero, repeats, axis=0)
    localized_counts = np.zeros_like(sample["counts"])
    localized_trials = np.zeros_like(sample["trials"])
    detected_total = 0
    error_total: list[np.ndarray] = []
    correct_in = 0
    correct_out = 0
    for start in range(0, len(events), batch_size):
        batch = events[start : start + batch_size]
        author, session, context, cell, outcome = batch.T
        incoming = cell // spec.branches
        cue = cell % spec.branches
        generated = simulate_transport_paths(
            incoming,
            outcome,
            cue,
            rng=rng,
            spec=spec,
            mechanism=mechanism,
        )
        located = localize_trajectories(
            generated["trajectory"],
            window=spec.locator_window,
            threshold=spec.threshold,
        )
        inferred_in, inferred_out = infer_route_branches(
            generated["trajectory"],
            located["location"],
            window=spec.locator_window,
            branches=spec.branches,
        )
        raw_error = np.abs(located["location"] - generated["junction"])
        error_total.append(np.where(
            located["detected"],
            raw_error,
            spec.path_points,
        ))
        valid = np.flatnonzero(located["detected"])
        detected_total += len(valid)
        if len(valid) == 0:
            continue
        correct_in += int(np.sum(inferred_in[valid] == incoming[valid]))
        correct_out += int(np.sum(inferred_out[valid] == outcome[valid]))
        observed_cell = (
            inferred_in[valid] * spec.branches + cue[valid]
        )
        np.add.at(
            localized_counts,
            (
                author[valid],
                session[valid],
                context[valid],
                observed_cell,
                inferred_out[valid],
            ),
            1,
        )
        np.add.at(
            localized_trials,
            (
                author[valid],
                session[valid],
                context[valid],
                observed_cell,
            ),
            1,
        )
    result = dict(sample)
    result["counts"] = localized_counts
    result["trials"] = localized_trials
    errors = np.concatenate(error_total)
    return result, {
        "event_detection_rate": detected_total / max(len(events), 1),
        "event_unconditional_median_error": float(np.median(errors)),
        "event_unconditional_p95_error": float(np.quantile(errors, 0.95)),
        "event_incoming_accuracy_detected": (
            correct_in / max(detected_total, 1)
        ),
        "event_outgoing_accuracy_detected": (
            correct_out / max(detected_total, 1)
        ),
    }


def apply_registered_missingness(
    sample: dict[str, Any],
    *,
    rng: np.random.Generator,
    kind: str,
    base_probability: float,
    floor: float,
    ceiling: float,
    gamma: float,
) -> dict[str, Any]:
    """Apply registered MAR or MNAR event observation probabilities."""
    if kind not in {"mar", "mnar"}:
        raise ValueError("kind must be mar or mnar")
    counts = np.asarray(sample["counts"])
    contexts = np.asarray(sample["contexts"]["all"])
    authors, sessions, n_contexts, cells, outcomes = counts.shape
    base_logit_scalar = np.log(base_probability / (1.0 - base_probability))
    context_term = 0.45 * contexts[:, 0]
    cell_term = 0.25 * np.sin(
        2.0 * np.pi * np.arange(cells) / cells
    )
    session_term = np.linspace(-0.10, 0.10, sessions)
    author_term = 0.12 * np.sin(
        2.0 * np.pi * np.arange(authors) / max(authors, 1)
    )
    base_logit = (
        base_logit_scalar
        + author_term[:, None, None, None]
        + session_term[None, :, None, None]
        + context_term[None, None, :, None]
        + cell_term[None, None, None, :]
    )
    outcome_score = np.linspace(-1.5, 1.5, outcomes)
    full_logit = base_logit[..., None]
    if kind == "mnar":
        full_logit = full_logit + gamma * outcome_score
    probability = 1.0 / (1.0 + np.exp(-full_logit))
    probability = np.broadcast_to(probability, counts.shape).copy()
    probability = np.clip(probability, floor, ceiling)
    observed = rng.binomial(counts.astype(int), probability).astype(np.int16)
    result = dict(sample)
    result["counts"] = observed
    result["trials"] = observed.sum(axis=-1).astype(np.int16)
    result["intended_trials"] = np.asarray(sample["trials"]).copy()
    result["observation_probability"] = probability
    result["missingness_base_logit"] = base_logit
    result["missingness_outcome_score"] = outcome_score
    result["missingness_kind"] = kind
    result["missingness_gamma"] = gamma
    return result


def propensity_for_gamma(
    sample: dict[str, Any],
    gamma: float,
    *,
    floor: float,
    ceiling: float,
) -> np.ndarray:
    """Reconstruct one registered MNAR sensitivity propensity surface."""
    logit = (
        np.asarray(sample["missingness_base_logit"])[..., None]
        + gamma * np.asarray(sample["missingness_outcome_score"])
    )
    probability = 1.0 / (1.0 + np.exp(-logit))
    probability = np.broadcast_to(
        probability,
        sample["counts"].shape,
    ).copy()
    return np.clip(probability, floor, ceiling)


def evaluate_group_free_operator(
    *,
    latent: dict[str, Any],
    reference_train: dict[str, Any],
    blind_train: dict[str, Any],
    oracle_train: dict[str, Any],
    oracle_test: dict[str, Any],
    rank: int,
    lambda_author: float,
    neighbor_count: int,
    method: str = "complete",
    propensity: np.ndarray | None = None,
) -> dict[str, Any]:
    """Fit blind and oracle operators and score one independent test panel."""
    discovery = np.arange(len(latent["contexts"]["discovery"]))
    confirmation = np.arange(
        len(discovery),
        len(discovery) + len(latent["contexts"]["confirmation"]),
    )
    reference_fit = fit_reference_router(reference_train, discovery)

    blind_disc = estimate_fixed_reference_profile(
        blind_train,
        discovery,
        reference_fit=reference_fit,
        method=method,
        propensity=propensity,
    )
    blind_conf = estimate_fixed_reference_profile(
        blind_train,
        confirmation,
        reference_fit=reference_fit,
        method=method,
        propensity=propensity,
    )
    blind_halves = tuple(
        estimate_fixed_reference_profile(
            blind_train,
            discovery,
            reference_fit=reference_fit,
            sessions=session,
            method=method,
            propensity=propensity,
        )
        for session in (0, 1)
    )
    blind_confirm_halves = tuple(
        estimate_fixed_reference_profile(
            blind_train,
            confirmation,
            reference_fit=reference_fit,
            sessions=session,
            method=method,
            propensity=propensity,
        )
        for session in (0, 1)
    )
    if any(
        row["refused"]
        for row in (
            blind_disc,
            blind_conf,
            *blind_halves,
            *blind_confirm_halves,
        )
    ):
        return {"status": "REFUSE_PROFILE", "numeric_output": False}
    blind_denoiser = fit_group_free_denoiser(
        blind_halves[0]["profile"],
        blind_halves[1]["profile"],
        rank=rank,
    )
    blind_discovery = apply_group_free_denoiser(
        blind_disc["profile"],
        blind_denoiser,
    )
    blind_confirmation = apply_group_free_denoiser(
        blind_conf["profile"],
        blind_denoiser,
    )
    blind_sessions = tuple(
        apply_group_free_denoiser(row["profile"], blind_denoiser)
        for row in blind_confirm_halves
    )

    oracle_disc = estimate_fixed_reference_profile(
        oracle_train,
        discovery,
        reference_fit=reference_fit,
    )
    oracle_halves = tuple(
        estimate_fixed_reference_profile(
            oracle_train,
            discovery,
            reference_fit=reference_fit,
            sessions=session,
        )
        for session in (0, 1)
    )
    oracle_denoiser = fit_group_free_denoiser(
        oracle_halves[0]["profile"],
        oracle_halves[1]["profile"],
        rank=rank,
    )
    oracle_discovery = apply_group_free_denoiser(
        oracle_disc["profile"],
        oracle_denoiser,
    )
    effective_trials = float(blind_disc["minimum_total_trials"])
    shrinkage = effective_trials / (effective_trials + lambda_author)
    blind_prediction = heldout_prediction_metrics(
        oracle_test,
        reference_fit=reference_fit,
        profile=blind_discovery,
        context_indices=confirmation,
        shrinkage=shrinkage,
    )
    oracle_effective = float(oracle_disc["minimum_total_trials"])
    oracle_shrinkage = oracle_effective / (
        oracle_effective + lambda_author
    )
    oracle_prediction = heldout_prediction_metrics(
        oracle_test,
        reference_fit=reference_fit,
        profile=oracle_discovery,
        context_indices=confirmation,
        shrinkage=oracle_shrinkage,
    )
    truth = true_fixed_reference_profile(
        latent,
        discovery,
        reference_fit=reference_fit,
    )
    pairing = group_free_pairing_metrics(
        blind_discovery,
        blind_confirmation,
        neighbor_count=neighbor_count,
    )
    split_reliability = multivariate_reliability(
        _center(blind_sessions[0]),
        _center(blind_sessions[1]),
    )
    unseen_reliability = multivariate_reliability(
        _center(blind_discovery),
        _center(blind_confirmation),
    )
    oracle_gain = float(oracle_prediction["log_loss_gain"])
    blind_gain = float(blind_prediction["log_loss_gain"])
    truth_scale = float(np.sqrt(np.mean(_center(truth) ** 2)))
    truth_nrmse = float(
        np.sqrt(np.mean((_center(blind_discovery) - _center(truth)) ** 2))
        / max(truth_scale, 1e-12)
    )
    return {
        "status": "GROUP_FREE_OPERATOR_READY",
        "numeric_output": True,
        "selected_rank": int(rank),
        "effective_rank": int(blind_denoiser["rank"]),
        "truth_correlation": flat_correlation(blind_discovery, truth),
        "truth_nrmse": truth_nrmse,
        "independent_oracle_correlation": flat_correlation(
            blind_discovery,
            oracle_discovery,
        ),
        "split_session_reliability": split_reliability,
        "unseen_context_reliability": unseen_reliability,
        **pairing,
        "true_group_sensitivity_auc": true_group_sensitivity_auc(
            blind_discovery,
            blind_confirmation,
            latent["labels"],
        ),
        "blind_log_loss_gain": blind_gain,
        "oracle_log_loss_gain": oracle_gain,
        "predictive_gain_retention": (
            blind_gain / oracle_gain if oracle_gain > 1e-12 else float("nan")
        ),
        "blind_ece": float(blind_prediction["ece"]),
        "mean_available_fraction": float(
            blind_disc["mean_available_fraction"]
        ),
        "_blind_profile": blind_discovery,
        "_truth_profile": truth,
        "_reference_fit": reference_fit,
    }


def rank_lambda_cv_losses_group_free(
    *,
    reference_train: dict[str, Any],
    blind_train: dict[str, Any],
    oracle_valid: dict[str, Any],
    ranks: Iterable[int],
    lambdas: Iterable[float],
    folds: int = 3,
) -> dict[tuple[int, float], float]:
    """Select rank and shrinkage without labels on independent events."""
    discovery = np.arange(
        len(reference_train["contexts"]["discovery"]),
        dtype=int,
    )
    fold_id = np.arange(len(discovery)) % folds
    result: dict[tuple[int, float], list[float]] = {
        (int(rank), float(value)): []
        for rank in ranks for value in lambdas
    }
    for fold in range(folds):
        train = discovery[fold_id != fold]
        valid = discovery[fold_id == fold]
        reference_fit = fit_reference_router(reference_train, train)
        combined = estimate_fixed_reference_profile(
            blind_train,
            train,
            reference_fit=reference_fit,
        )
        halves = tuple(
            estimate_fixed_reference_profile(
                blind_train,
                train,
                reference_fit=reference_fit,
                sessions=session,
            )
            for session in (0, 1)
        )
        for rank in {key[0] for key in result}:
            denoiser = fit_group_free_denoiser(
                halves[0]["profile"],
                halves[1]["profile"],
                rank=rank,
            )
            profile = apply_group_free_denoiser(
                combined["profile"],
                denoiser,
            )
            effective = float(combined["minimum_total_trials"])
            for value in {key[1] for key in result}:
                shrinkage = effective / (effective + value)
                metrics = heldout_prediction_metrics(
                    oracle_valid,
                    reference_fit=reference_fit,
                    profile=profile,
                    context_indices=valid,
                    shrinkage=shrinkage,
                )
                result[(rank, value)].append(
                    float(metrics["personalized_log_loss"])
                )
    return {
        key: float(np.mean(values)) if values else float("inf")
        for key, values in result.items()
    }


def mnar_sensitivity_envelope(
    *,
    masked: dict[str, Any],
    reference_fit: dict[str, np.ndarray],
    truth_profile: np.ndarray,
    rank: int,
    gamma_grid: Iterable[float],
    floor: float,
    ceiling: float,
) -> dict[str, float]:
    """Return a coordinate-wise MNAR sensitivity envelope."""
    discovery = np.arange(len(masked["contexts"]["discovery"]))
    profiles = []
    lower_profiles = []
    upper_profiles = []
    for gamma in gamma_grid:
        propensity = propensity_for_gamma(
            masked,
            float(gamma),
            floor=floor,
            ceiling=ceiling,
        )
        combined = estimate_fixed_reference_profile(
            masked,
            discovery,
            reference_fit=reference_fit,
            method="aipw",
            propensity=propensity,
        )
        halves = tuple(
            estimate_fixed_reference_profile(
                masked,
                discovery,
                reference_fit=reference_fit,
                sessions=session,
                method="aipw",
                propensity=propensity,
            )
            for session in (0, 1)
        )
        denoiser = fit_group_free_denoiser(
            halves[0]["profile"],
            halves[1]["profile"],
            rank=rank,
        )
        profile = apply_group_free_denoiser(
            combined["profile"],
            denoiser,
        )
        half_profiles = [
            apply_group_free_denoiser(row["profile"], denoiser)
            for row in halves
        ]
        empirical_se = np.abs(
            half_profiles[0] - half_profiles[1]
        ) / np.sqrt(2.0)
        profiles.append(profile)
        lower_profiles.append(profile - 1.96 * empirical_se)
        upper_profiles.append(profile + 1.96 * empirical_se)
    stack = np.stack(profiles)
    lower = np.stack(lower_profiles).min(axis=0)
    upper = np.stack(upper_profiles).max(axis=0)
    covered = (
        (truth_profile >= lower)
        & (truth_profile <= upper)
    )
    return {
        "mnar_sensitivity_coverage": float(covered.mean()),
        "mnar_sensitivity_mean_width": float(
            np.mean(upper - lower)
        ),
        "mnar_sensitivity_min_truth_correlation": float(
            min(flat_correlation(row, truth_profile) for row in profiles)
        ),
        "mnar_sensitivity_max_truth_correlation": float(
            max(flat_correlation(row, truth_profile) for row in profiles)
        ),
    }
