"""Geometry-only blind junction localization for SUICA V8.3.7B."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .v8_author_routing_operator import (
    analyze_author_routing_world,
    apply_profile_denoiser,
    fit_profile_denoiser,
    fit_reference_router,
    heldout_prediction_metrics,
    ilr,
    ilr_basis,
    multivariate_reliability,
    pairing_metrics,
    true_q_profile,
)


@dataclass(frozen=True)
class BlindJunctionSpec:
    """Frozen continuous-path and locator settings."""

    path_points: int = 25
    junction_min: int = 10
    junction_max: int = 14
    locator_window: int = 4
    threshold: float = 0.45
    trajectory_noise_sd: float = 0.015
    cue_distractor_rate: float = 0.35
    cusp_amplitude_min: float = 0.14
    cusp_amplitude_max: float = 0.30
    pause_inner_min: float = 0.25
    pause_inner_max: float = 0.45
    branch_angle_jitter_sd: float = 0.08
    branches: int = 4


def branch_directions(branches: int = 4) -> np.ndarray:
    """Return the fixed geometry-only branch direction dictionary."""
    angles = 2.0 * np.pi * np.arange(branches) / branches
    return np.column_stack([np.cos(angles), np.sin(angles)])


def _perpendicular(values: np.ndarray) -> np.ndarray:
    return np.column_stack([-values[:, 1], values[:, 0]])


def _rotate(values: np.ndarray, angle: np.ndarray) -> np.ndarray:
    cosine = np.cos(angle)
    sine = np.sin(angle)
    return np.column_stack([
        cosine * values[:, 0] - sine * values[:, 1],
        sine * values[:, 0] + cosine * values[:, 1],
    ])


def simulate_junction_trajectories(
    incoming: np.ndarray,
    outgoing: np.ndarray,
    cue: np.ndarray,
    *,
    seed: int,
    spec: BlindJunctionSpec,
) -> dict[str, np.ndarray]:
    """Generate true-junction trajectories with bends and cue distractors."""
    incoming = np.asarray(incoming, dtype=int)
    outgoing = np.asarray(outgoing, dtype=int)
    cue = np.asarray(cue, dtype=int)
    if not (len(incoming) == len(outgoing) == len(cue)):
        raise ValueError("routing arrays must have equal length")
    rng = np.random.default_rng(seed)
    n = len(incoming)
    directions = branch_directions(spec.branches)
    before = _rotate(
        directions[incoming],
        rng.normal(scale=spec.branch_angle_jitter_sd, size=n),
    )
    after = _rotate(
        directions[outgoing],
        rng.normal(scale=spec.branch_angle_jitter_sd, size=n),
    )
    junction = rng.integers(
        spec.junction_min,
        spec.junction_max + 1,
        size=n,
    )
    speed = rng.uniform(0.85, 1.15, size=n)
    time = np.arange(spec.path_points)[None, :]
    offset = time - junction[:, None]
    path = np.where(
        (offset <= 0)[..., None],
        offset[..., None] * before[:, None, :],
        offset[..., None] * after[:, None, :],
    )
    path *= speed[:, None, None]

    phase = rng.uniform(0.0, 2.0 * np.pi, size=n)
    drift_direction = np.column_stack([np.cos(phase), np.sin(phase)])
    smooth = 0.08 * np.sin(
        np.pi * (time + 1.0) / (spec.path_points + 1.0)
    )
    path += smooth[..., None] * drift_direction[:, None, :]

    rows = np.arange(n)
    lateral = _perpendicular(before)
    inner = rng.uniform(
        spec.pause_inner_min,
        spec.pause_inner_max,
        size=n,
    )
    cusp_amplitude = rng.uniform(
        spec.cusp_amplitude_min,
        spec.cusp_amplitude_max,
        size=n,
    )
    path[rows, junction - 2] = -1.20 * speed[:, None] * before
    path[rows, junction - 1] = (
        -inner[:, None] * speed[:, None] * before
    )
    path[rows, junction] = (
        cusp_amplitude[:, None] * speed[:, None] * lateral
    )
    path[rows, junction + 1] = (
        inner[:, None] * speed[:, None] * after
    )
    path[rows, junction + 2] = 1.20 * speed[:, None] * after

    distractor = rng.random(n) < spec.cue_distractor_rate
    distractor_at = junction - 5
    cue_lateral = _perpendicular(directions[cue])
    path[rows[distractor], distractor_at[distractor]] += (
        0.42 * speed[distractor, None] * cue_lateral[distractor]
    )
    path += rng.normal(
        scale=spec.trajectory_noise_sd,
        size=path.shape,
    )
    return {
        "trajectory": path.astype(np.float32),
        "junction": junction,
        "incoming": incoming,
        "outgoing": outgoing,
        "cue": cue,
    }


def simulate_no_junction_trajectories(
    *,
    seed: int,
    count: int,
    spec: BlindJunctionSpec,
) -> dict[str, np.ndarray]:
    """Generate smooth and single-signature negative-control paths."""
    rng = np.random.default_rng(seed)
    directions = branch_directions(spec.branches)
    branch = rng.integers(0, spec.branches, size=count)
    base = directions[branch]
    speed = rng.uniform(0.85, 1.15, size=count)
    time = np.arange(spec.path_points)[None, :]
    centered = time - (spec.path_points - 1) / 2.0
    path = centered[..., None] * speed[:, None, None] * base[:, None, :]
    lateral = _perpendicular(base)
    curve = rng.uniform(-0.15, 0.15, size=count)
    path += (
        curve[:, None, None]
        * ((centered / spec.path_points) ** 2)[..., None]
        * lateral[:, None, :]
    )
    kind = np.arange(count) % 5
    center = rng.integers(
        spec.junction_min,
        spec.junction_max + 1,
        size=count,
    )
    rows = np.arange(count)

    bend = kind == 0
    path[rows[bend], center[bend]] += (
        0.55 * lateral[bend]
    )

    pause = kind == 1
    anchor = path[rows[pause], center[pause]].copy()
    path[rows[pause], center[pause] - 2] = (
        anchor - 1.20 * speed[pause, None] * base[pause]
    )
    path[rows[pause], center[pause] - 1] = (
        anchor - 0.35 * speed[pause, None] * base[pause]
    )
    path[rows[pause], center[pause]] = anchor
    path[rows[pause], center[pause] + 1] = (
        anchor + 0.35 * speed[pause, None] * base[pause]
    )
    path[rows[pause], center[pause] + 2] = (
        anchor + 1.20 * speed[pause, None] * base[pause]
    )

    cue_bend = kind == 2
    cue = rng.integers(0, spec.branches, size=count)
    cue_lateral = _perpendicular(directions[cue])
    path[rows[cue_bend], center[cue_bend]] += (
        0.45 * cue_lateral[cue_bend]
    )

    near_crossing = kind == 3
    path[near_crossing] += 0.08 * lateral[near_crossing, None, :]

    speed_wave = kind == 4
    modulation = 1.0 + 0.20 * np.sin(
        2.0 * np.pi * time / spec.path_points
    )
    path[speed_wave] *= modulation[0, :, None]
    path += rng.normal(
        scale=spec.trajectory_noise_sd,
        size=path.shape,
    )
    return {
        "trajectory": path.astype(np.float32),
        "kind": kind,
    }


def localize_trajectories(
    trajectory: np.ndarray,
    *,
    window: int,
    threshold: float,
) -> dict[str, np.ndarray]:
    """Locate a pause-cusp transition using geometry and order only."""
    path = np.asarray(trajectory, dtype=float)
    if path.ndim != 3 or path.shape[-1] != 2:
        raise ValueError("trajectory must have shape events by time by 2")
    n, points, _ = path.shape
    velocity = np.diff(path, axis=1)
    speed = np.linalg.norm(velocity, axis=-1)
    candidates = np.arange(window, points - window)
    scores = np.zeros((n, len(candidates)), dtype=float)
    for column, location in enumerate(candidates):
        local_speed = 0.5 * (
            speed[:, location - 1] + speed[:, location]
        )
        flank = np.concatenate([
            speed[:, location - window : location - 2],
            speed[:, location + 2 : location + window],
        ], axis=1)
        flank_speed = np.median(flank, axis=1)
        dip = np.clip(
            1.0 - local_speed / np.maximum(flank_speed, 1e-8),
            0.0,
            1.0,
        )
        pre_direction = (
            path[:, location - 1]
            - path[:, location - window]
        )
        pre_direction /= np.maximum(
            np.linalg.norm(pre_direction, axis=1, keepdims=True),
            1e-8,
        )
        cusp_vector = (
            path[:, location - 1]
            + path[:, location + 1]
            - 2.0 * path[:, location]
        )
        parallel = (
            np.sum(cusp_vector * pre_direction, axis=1)[:, None]
            * pre_direction
        )
        cusp = np.linalg.norm(
            cusp_vector - parallel,
            axis=1,
        ) / np.maximum(flank_speed, 1e-8)
        scores[:, column] = np.sqrt(
            dip * np.clip(cusp, 0.0, 2.0)
        )
    selected_column = scores.argmax(axis=1)
    selected_score = scores[np.arange(n), selected_column]
    location = candidates[selected_column]
    detected = selected_score >= threshold
    location = np.where(detected, location, -1)
    return {
        "detected": detected,
        "location": location,
        "score": selected_score,
        "score_surface": scores,
    }


def infer_route_branches(
    trajectory: np.ndarray,
    location: np.ndarray,
    *,
    window: int,
    branches: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Infer pre/post branch directions after blind localization."""
    path = np.asarray(trajectory, dtype=float)
    location = np.asarray(location, dtype=int)
    directions = branch_directions(branches)
    incoming = np.full(len(path), -1, dtype=int)
    outgoing = np.full(len(path), -1, dtype=int)
    valid = np.flatnonzero(location >= 0)
    if len(valid) == 0:
        return incoming, outgoing
    loc = location[valid]
    pre = (
        path[valid, loc - 1]
        - path[valid, loc - window]
    )
    post = (
        path[valid, loc + window]
        - path[valid, loc + 1]
    )
    pre /= np.maximum(np.linalg.norm(pre, axis=1, keepdims=True), 1e-9)
    post /= np.maximum(np.linalg.norm(post, axis=1, keepdims=True), 1e-9)
    incoming[valid] = np.argmax(pre @ directions.T, axis=1)
    outgoing[valid] = np.argmax(post @ directions.T, axis=1)
    return incoming, outgoing


def localization_panel_metrics(
    positive: dict[str, np.ndarray],
    negative: dict[str, np.ndarray],
    *,
    window: int,
    threshold: float,
) -> dict[str, float]:
    """Score localization without exposing routing metadata to the locator."""
    located_positive = localize_trajectories(
        positive["trajectory"],
        window=window,
        threshold=threshold,
    )
    located_negative = localize_trajectories(
        negative["trajectory"],
        window=window,
        threshold=threshold,
    )
    error = np.abs(
        located_positive["location"] - positive["junction"]
    )
    correct = located_positive["detected"] & (error <= 2)
    detections = int(
        located_positive["detected"].sum()
        + located_negative["detected"].sum()
    )
    precision = float(correct.sum() / max(detections, 1))
    recall = float(correct.mean())
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall > 0
        else 0.0
    )
    correct_error = error[correct]
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "median_location_error": (
            float(np.median(correct_error))
            if len(correct_error) else float("inf")
        ),
        "p95_location_error": (
            float(np.quantile(correct_error, 0.95))
            if len(correct_error) else float("inf")
        ),
        "false_junctions_per_1000": float(
            1000.0
            * located_negative["detected"].mean()
        ),
    }


def _expand_count_events(
    counts: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    nonzero = np.argwhere(counts > 0)
    repeats = counts[tuple(nonzero.T)].astype(int)
    return np.repeat(nonzero, repeats, axis=0), repeats


def localize_routing_sample(
    sample: dict[str, Any],
    *,
    seed: int,
    spec: BlindJunctionSpec,
    batch_size: int = 20_000,
) -> tuple[dict[str, Any], dict[str, float]]:
    """Replace oracle routing counts with geometry-only localized counts."""
    events, _ = _expand_count_events(np.asarray(sample["counts"]))
    localized_counts = np.zeros_like(sample["counts"])
    localized_trials = np.zeros_like(sample["trials"])
    detected_total = 0
    correct_location = 0
    correct_incoming = 0
    correct_outgoing = 0
    error_values: list[np.ndarray] = []
    for start in range(0, len(events), batch_size):
        batch = events[start : start + batch_size]
        author, session, context, cell, outcome = batch.T
        incoming = cell // spec.branches
        cue = cell % spec.branches
        generated = simulate_junction_trajectories(
            incoming,
            outcome,
            cue,
            seed=seed + start,
            spec=spec,
        )
        located = localize_trajectories(
            generated["trajectory"],
            window=spec.locator_window,
            threshold=spec.threshold,
        )
        inferred_incoming, inferred_outgoing = infer_route_branches(
            generated["trajectory"],
            located["location"],
            window=spec.locator_window,
            branches=spec.branches,
        )
        valid = np.flatnonzero(located["detected"])
        detected_total += len(valid)
        if len(valid) == 0:
            continue
        location_error = np.abs(
            located["location"][valid] - generated["junction"][valid]
        )
        error_values.append(location_error)
        correct_location += int(np.sum(location_error <= 2))
        correct_incoming += int(
            np.sum(inferred_incoming[valid] == incoming[valid])
        )
        correct_outgoing += int(
            np.sum(inferred_outgoing[valid] == outcome[valid])
        )
        observed_cell = (
            inferred_incoming[valid] * spec.branches + cue[valid]
        )
        np.add.at(
            localized_counts,
            (
                author[valid],
                session[valid],
                context[valid],
                observed_cell,
                inferred_outgoing[valid],
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
    errors = (
        np.concatenate(error_values)
        if error_values else np.asarray([], dtype=float)
    )
    metrics = {
        "events": len(events),
        "detection_rate": detected_total / max(len(events), 1),
        "correct_location_rate": correct_location / max(len(events), 1),
        "incoming_accuracy_detected": (
            correct_incoming / max(detected_total, 1)
        ),
        "outgoing_accuracy_detected": (
            correct_outgoing / max(detected_total, 1)
        ),
        "median_location_error": (
            float(np.median(errors)) if len(errors) else float("inf")
        ),
        "p95_location_error": (
            float(np.quantile(errors, 0.95)) if len(errors) else float("inf")
        ),
    }
    return result, metrics


def _within_group_center(
    values: np.ndarray,
    labels: np.ndarray,
) -> np.ndarray:
    result = np.asarray(values, dtype=float).copy()
    for group in np.unique(labels):
        mask = labels == group
        result[mask] -= result[mask].mean(axis=0, keepdims=True)
    return result


def _safe_correlation(left: np.ndarray, right: np.ndarray) -> float:
    x = np.asarray(left, dtype=float).ravel()
    y = np.asarray(right, dtype=float).ravel()
    if np.std(x) <= 1e-12 or np.std(y) <= 1e-12:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def estimate_masked_packet_profile(
    sample: dict[str, Any],
    context_indices: np.ndarray,
    *,
    sessions: int | tuple[int, ...] = (0, 1),
) -> dict[str, Any]:
    """Estimate equal-context profiles while retaining partial masks."""
    contexts = np.asarray(context_indices, dtype=int)
    halves = (
        np.asarray([sessions], dtype=int)
        if isinstance(sessions, (int, np.integer))
        else np.asarray(sessions, dtype=int)
    )
    counts = sample["counts"][:, halves][:, :, contexts]
    trials = sample["trials"][:, halves][:, :, contexts].astype(float)
    valid = trials > 0
    available = valid.sum(axis=(1, 2))
    if np.any(available == 0):
        return {
            "status": "REFUSE_NONOVERLAP",
            "refused": True,
            "minimum_available_contexts": int(available.min()),
        }
    proportions = np.divide(
        counts,
        trials[..., None],
        out=np.zeros_like(counts, dtype=float),
        where=valid[..., None],
    )
    probability = proportions.sum(axis=(1, 2)) / available[..., None]
    inverse_trials = np.divide(
        1.0,
        trials,
        out=np.zeros_like(trials),
        where=valid,
    ).sum(axis=(1, 2))
    effective_trials = available**2 / np.maximum(inverse_trials, 1e-12)
    probability = (
        probability * effective_trials[..., None] + 0.5
    ) / (effective_trials[..., None] + 0.5 * probability.shape[-1])
    probability /= probability.sum(axis=-1, keepdims=True)
    reference = probability.mean(axis=0)
    basis = ilr_basis(probability.shape[-1])
    profile = ilr(probability, basis) - ilr(reference, basis)[None]
    return {
        "status": "MASKED_PROFILE_READY",
        "refused": False,
        "profile": profile.reshape(len(profile), -1),
        "cell_profile": profile,
        "probability": probability,
        "reference_probability": reference,
        "minimum_available_contexts": int(available.min()),
        "mean_available_fraction": float(valid.mean()),
    }


def _operator_profile(
    sample: dict[str, Any],
    *,
    rank: int,
    seed: int,
) -> np.ndarray:
    discovery = np.arange(len(sample["contexts"]["discovery"]))
    combined = estimate_masked_packet_profile(sample, discovery)
    halves = (
        estimate_masked_packet_profile(sample, discovery, sessions=0),
        estimate_masked_packet_profile(sample, discovery, sessions=1),
    )
    if combined["refused"] or any(row["refused"] for row in halves):
        raise ValueError("localized routing sample has non-overlapping cells")
    denoiser = fit_profile_denoiser(
        halves[0]["profile"],
        halves[1]["profile"],
        rank=rank,
        groups=int(sample["design"]["mixture_components"]),
        seed=seed,
    )
    return apply_profile_denoiser(combined["profile"], denoiser)


def compare_blind_and_oracle_operator(
    oracle: dict[str, Any],
    blind: dict[str, Any],
    *,
    rank: int,
    selected_lambda: float,
    seed: int,
    claim_thresholds: dict[str, float],
) -> dict[str, float | bool]:
    """Compare blind-localized and oracle-window routing operators."""
    oracle_profile = _operator_profile(oracle, rank=rank, seed=seed)
    blind_profile = _operator_profile(blind, rank=rank, seed=seed + 1)
    labels = np.asarray(oracle["labels"])
    left = _within_group_center(oracle_profile, labels).ravel()
    right = _within_group_center(blind_profile, labels).ravel()
    correlation = _safe_correlation(left, right)
    oracle_result = analyze_author_routing_world(
        oracle,
        selected_lambda=selected_lambda,
        selected_rank=rank,
        denoiser_seed=seed,
        claim_thresholds=claim_thresholds,
    )
    discovery = np.arange(len(blind["contexts"]["discovery"]))
    confirmation = np.arange(
        len(blind["contexts"]["discovery"]),
        len(blind["contexts"]["discovery"])
        + len(blind["contexts"]["confirmation"]),
    )
    oracle_gain = float(oracle_result["log_loss_gain"])
    combined = estimate_masked_packet_profile(blind, discovery)
    halves = (
        estimate_masked_packet_profile(blind, discovery, sessions=0),
        estimate_masked_packet_profile(blind, discovery, sessions=1),
    )
    confirmation_profile = estimate_masked_packet_profile(
        blind,
        confirmation,
    )
    confirmation_halves = (
        estimate_masked_packet_profile(blind, confirmation, sessions=0),
        estimate_masked_packet_profile(blind, confirmation, sessions=1),
    )
    denoiser = fit_profile_denoiser(
        halves[0]["profile"],
        halves[1]["profile"],
        rank=rank,
        groups=int(blind["design"]["mixture_components"]),
        seed=seed + 1,
    )
    blind_discovery = apply_profile_denoiser(
        combined["profile"],
        denoiser,
    )
    blind_confirmation = apply_profile_denoiser(
        confirmation_profile["profile"],
        denoiser,
    )
    blind_sessions = tuple(
        apply_profile_denoiser(row["profile"], denoiser)
        for row in confirmation_halves
    )
    reference_fit = fit_reference_router(blind, discovery)
    effective_trials = max(
        2.0 * combined["minimum_available_contexts"],
        1.0,
    )
    shrinkage = effective_trials / (
        effective_trials + selected_lambda
    )
    prediction = heldout_prediction_metrics(
        blind,
        reference_fit=reference_fit,
        profile=blind_discovery,
        context_indices=confirmation,
        shrinkage=shrinkage,
    )
    blind_gain = float(prediction["log_loss_gain"])
    pairing = pairing_metrics(
        blind_discovery,
        blind_confirmation,
        labels,
    )
    unseen_reliability = multivariate_reliability(
        _within_group_center(blind_discovery, labels),
        _within_group_center(blind_confirmation, labels),
    )
    split_reliability = multivariate_reliability(
        _within_group_center(blind_sessions[0], labels),
        _within_group_center(blind_sessions[1], labels),
    )
    truth = true_q_profile(
        oracle,
        np.concatenate([discovery, confirmation]),
    )["profile"]
    truth_correlation = _safe_correlation(
        _within_group_center(blind_discovery, labels).ravel(),
        _within_group_center(truth, labels).ravel(),
    )
    blind_claim = bool(
        pairing["within_group_auc"]
        >= claim_thresholds["minimum_within_group_auc"]
        and min(split_reliability, unseen_reliability)
        >= claim_thresholds["minimum_multivariate_reliability"]
        and blind_gain >= claim_thresholds["minimum_log_loss_gain"]
    )
    return {
        "operator_correlation": correlation,
        "oracle_log_loss_gain": oracle_gain,
        "blind_log_loss_gain": blind_gain,
        "predictive_gain_retention": blind_gain / max(oracle_gain, 1e-12),
        "blind_author_claim": blind_claim,
        "blind_truth_correlation": truth_correlation,
        "blind_split_session_reliability": split_reliability,
        "blind_unseen_context_reliability": unseen_reliability,
        "blind_within_group_auc": float(pairing["within_group_auc"]),
        "blind_available_fraction": combined["mean_available_fraction"],
    }
