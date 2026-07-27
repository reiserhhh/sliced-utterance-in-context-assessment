"""Adaptive-rank and fixed-reference operators for SUICA V8.3.7E."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy.special import softmax
from sklearn.metrics import roc_auc_score

from .v8_author_routing_operator import (
    context_feature_map,
    ilr,
    ilr_basis,
    ilr_inverse,
    multivariate_reliability,
    predict_reference_router,
    registered_contexts,
)
from .v8_group_free_routing_transport import (
    apply_group_free_denoiser,
    fit_group_free_denoiser,
)


@dataclass(frozen=True)
class AdaptiveReferenceWorldSpec:
    """Synthetic fixed-reference routing world."""

    authors: int = 480
    latent_rank: int = 8
    maximum_latent_rank: int = 16
    events_per_context_session: int = 128
    author_rms: float = 0.30
    spectrum: str = "flat"
    spectrum_decay: float = 0.75
    branches: int = 4
    sessions: int = 2
    discovery_contexts: int = 12
    confirmation_contexts: int = 8
    extrapolation_contexts: int = 4
    shared_rms: float = 0.45
    context_rms: float = 0.35
    author_context_rms: float = 0.20
    session_rms: float = 0.10

    @property
    def cells(self) -> int:
        return self.branches**2

    @property
    def total_contexts(self) -> int:
        return (
            self.discovery_contexts
            + self.confirmation_contexts
            + self.extrapolation_contexts
        )

    @property
    def repeats_per_cell(self) -> int:
        if self.events_per_context_session % self.cells:
            raise ValueError("event budget must be divisible by cells")
        return self.events_per_context_session // self.cells


def _scale_rms(values: np.ndarray, target: float) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    rms = float(np.sqrt(np.mean(array**2)))
    if target == 0.0 or rms <= 1e-12:
        return np.zeros_like(array)
    return array * (target / rms)


def _haar(
    rng: np.random.Generator,
    dimension: int,
    rank: int,
) -> np.ndarray:
    return np.linalg.qr(
        rng.normal(size=(dimension, rank)),
        mode="reduced",
    )[0]


def _from_ilr(
    values: np.ndarray,
    *,
    cells: int,
    branches: int,
) -> np.ndarray:
    coordinates = np.asarray(values).reshape(
        *values.shape[:-1],
        cells,
        branches - 1,
    )
    return coordinates @ ilr_basis(branches).T


def simulate_adaptive_reference_world(
    *,
    seed: int,
    spec: AdaptiveReferenceWorldSpec,
) -> dict[str, Any]:
    """Generate a rank-controlled world with no fitted group labels."""
    if spec.latent_rank > spec.maximum_latent_rank:
        raise ValueError("latent rank exceeds maximum latent rank")
    if spec.spectrum not in {"flat", "decay"}:
        raise ValueError("spectrum must be flat or decay")
    sequences = np.random.SeedSequence(seed).spawn(6)
    rng_shared, rng_context, rng_author, rng_session, _, rng_ctx = (
        np.random.default_rng(sequence) for sequence in sequences
    )
    contexts = registered_contexts(
        seed=int(rng_ctx.integers(0, np.iinfo(np.int32).max)),
        spec=type("_ContextSpec", (), {
            "context_dimensions": 3,
            "discovery_contexts": spec.discovery_contexts,
            "confirmation_contexts": spec.confirmation_contexts,
            "extrapolation_contexts": spec.extrapolation_contexts,
        })(),
    )
    dimension = spec.cells * (spec.branches - 1)
    shared = _scale_rms(
        _from_ilr(
            rng_shared.normal(size=dimension),
            cells=spec.cells,
            branches=spec.branches,
        ),
        spec.shared_rms,
    )
    features = context_feature_map(contexts["all"])
    features -= features.mean(axis=0, keepdims=True)
    context_loading = _haar(
        rng_context,
        dimension,
        features.shape[1],
    )
    context = _scale_rms(
        _from_ilr(
            features @ context_loading.T,
            cells=spec.cells,
            branches=spec.branches,
        ),
        spec.context_rms,
    )
    author_loading = _haar(
        rng_author,
        dimension,
        spec.maximum_latent_rank,
    )
    author_score = rng_author.normal(
        size=(spec.authors, spec.maximum_latent_rank),
    )
    if spec.spectrum == "decay":
        weights = spec.spectrum_decay ** np.arange(spec.latent_rank)
    else:
        weights = np.ones(spec.latent_rank)
    author_ilr = (
        author_score[:, : spec.latent_rank]
        * weights[None]
    ) @ author_loading[:, : spec.latent_rank].T
    author = _scale_rms(
        _from_ilr(
            author_ilr,
            cells=spec.cells,
            branches=spec.branches,
        ),
        spec.author_rms,
    )
    interaction_features = context_feature_map(contexts["all"])
    interaction_features -= interaction_features[
        : spec.discovery_contexts
    ].mean(axis=0, keepdims=True)
    interaction_scale = np.maximum(
        interaction_features[: spec.discovery_contexts].std(
            axis=0,
            ddof=1,
        ),
        1e-8,
    )
    interaction_features /= interaction_scale
    interaction_rank = min(
        spec.latent_rank,
        interaction_features.shape[1],
    )
    author_context_ilr = np.einsum(
        "ar,cr,dr->acd",
        (
            author_score[:, :interaction_rank]
            * weights[:interaction_rank][None]
        ),
        interaction_features[:, :interaction_rank],
        author_loading[:, :interaction_rank],
    )
    author_context = _scale_rms(
        _from_ilr(
            author_context_ilr,
            cells=spec.cells,
            branches=spec.branches,
        ),
        spec.author_context_rms,
    )
    session_rank = min(3, dimension)
    session_loading = _haar(rng_session, dimension, session_rank)
    session_score = rng_session.normal(
        size=(spec.authors, session_rank),
    )
    session_ilr = np.stack([session_score, -session_score], axis=1)
    session = _scale_rms(
        _from_ilr(
            np.einsum("asr,dr->asd", session_ilr, session_loading),
            cells=spec.cells,
            branches=spec.branches,
        ),
        spec.session_rms,
    )
    eta = (
        shared[None, None, None]
        + context[None, None]
        + author[:, None, None]
        + author_context[:, None]
        + session[:, :, None]
    )
    probability = softmax(eta, axis=-1)
    trials = np.full(
        (
            spec.authors,
            spec.sessions,
            spec.total_contexts,
            spec.cells,
        ),
        spec.repeats_per_cell,
        dtype=np.int16,
    )
    return {
        "world": "adaptive_rank_fixed_reference",
        "contexts": contexts,
        "counts": np.zeros_like(probability, dtype=np.int16),
        "trials": trials,
        "probability": probability,
        "components": {
            "author_loading": author_loading,
            "author_score": author_score,
            "spectrum_weights": weights,
            "author_context": author_context,
        },
        "design": {
            "authors": spec.authors,
            "author_rank": spec.latent_rank,
            "maximum_latent_rank": spec.maximum_latent_rank,
            "spectrum": spec.spectrum,
            "author_rms": spec.author_rms,
            "author_context_rms": spec.author_context_rms,
            "events_per_context_session": (
                spec.events_per_context_session
            ),
        },
    }


def with_event_budget(
    sample: dict[str, Any],
    events_per_context_session: int,
) -> dict[str, Any]:
    """Return a view with a new balanced event budget."""
    cells = int(np.asarray(sample["probability"]).shape[-2])
    if events_per_context_session % cells:
        raise ValueError("event budget must be divisible by cells")
    result = dict(sample)
    result["trials"] = np.full(
        np.asarray(sample["trials"]).shape,
        events_per_context_session // cells,
        dtype=np.int16,
    )
    result["counts"] = np.zeros_like(sample["counts"], dtype=np.int16)
    result["design"] = dict(sample["design"])
    result["design"]["events_per_context_session"] = int(
        events_per_context_session
    )
    return result


def subset_authors(
    sample: dict[str, Any],
    indices: np.ndarray,
) -> dict[str, Any]:
    """Subset author-indexed arrays without changing shared design objects."""
    indices = np.asarray(indices, dtype=int)
    author_count = int(np.asarray(sample["probability"]).shape[0])
    result = dict(sample)
    for key, value in sample.items():
        if (
            isinstance(value, np.ndarray)
            and value.ndim > 0
            and value.shape[0] == author_count
        ):
            result[key] = value[indices].copy()
    result["design"] = dict(sample.get("design", {}))
    result["design"]["authors"] = int(len(indices))
    return result


def apply_opportunity_shift(
    sample: dict[str, Any],
    *,
    strength: float,
) -> dict[str, Any]:
    """Change context exposure while preserving overlap and total budget."""
    result = dict(sample)
    trials = np.asarray(sample["trials"]).copy()
    contexts = np.asarray(sample["contexts"]["all"])
    score = contexts[:, 0]
    multiplier = np.exp(strength * score)
    multiplier /= multiplier.mean()
    base = float(np.mean(trials))
    repeats = np.maximum(1, np.rint(base * multiplier)).astype(np.int16)
    trials[...] = repeats[None, None, :, None]
    result["trials"] = trials
    result["counts"] = np.zeros_like(sample["counts"], dtype=np.int16)
    result["opportunity_multiplier"] = multiplier
    return result


def population_shift_direction(
    sample: dict[str, Any],
    *,
    rms: float,
) -> np.ndarray:
    """Return a scorer-known shift aligned with the first author direction."""
    direction = np.asarray(
        sample["components"]["author_loading"][:, 0],
        dtype=float,
    )
    return _scale_rms(direction, rms)


def apply_population_shift(
    sample: dict[str, Any],
    *,
    indices: np.ndarray,
    shift_ilr: np.ndarray,
) -> dict[str, Any]:
    """Plant a common author-population movement in ILR coordinates."""
    result = dict(sample)
    probability = np.asarray(sample["probability"], dtype=float).copy()
    basis = ilr_basis(probability.shape[-1])
    coordinates = ilr(probability[indices], basis)
    coordinates += np.asarray(shift_ilr).reshape(
        1,
        1,
        1,
        probability.shape[-2],
        probability.shape[-1] - 1,
    )
    probability[indices] = ilr_inverse(coordinates, basis)
    result["probability"] = probability
    result["counts"] = np.zeros_like(sample["counts"], dtype=np.int16)
    result["planted_population_shift_ilr"] = np.asarray(shift_ilr).copy()
    return result


def _selected_sessions(sessions: int | Iterable[int]) -> np.ndarray:
    if isinstance(sessions, (int, np.integer)):
        return np.asarray([int(sessions)], dtype=int)
    return np.asarray(tuple(sessions), dtype=int)


def estimate_standardized_profile(
    sample: dict[str, Any],
    context_indices: Iterable[int],
    *,
    reference_fit: dict[str, np.ndarray],
    sessions: int | Iterable[int] = (0, 1),
    context_weights: np.ndarray | None = None,
    naive_exposure_weighted: bool = False,
) -> np.ndarray:
    """Estimate a profile under a fixed target context distribution."""
    contexts = np.asarray(tuple(context_indices), dtype=int)
    selected = _selected_sessions(sessions)
    counts = np.asarray(sample["counts"])[:, selected][:, :, contexts]
    trials = np.asarray(sample["trials"])[:, selected][:, :, contexts]
    if np.any(trials <= 0):
        raise ValueError("standardized profile requires positive overlap")
    proportions = np.divide(
        counts,
        trials[..., None],
        out=np.zeros_like(counts, dtype=float),
        where=trials[..., None] > 0,
    )
    if naive_exposure_weighted:
        author_probability = np.divide(
            counts.sum(axis=(1, 2)),
            trials.sum(axis=(1, 2))[..., None],
        )
        effective_trials = trials.sum(axis=(1, 2))
        reference_weight = trials.mean(axis=(0, 1, 3))
        reference_weight = reference_weight / reference_weight.sum()
    else:
        if context_weights is None:
            context_weights = np.ones(len(contexts), dtype=float)
        reference_weight = np.asarray(context_weights, dtype=float)
        reference_weight /= reference_weight.sum()
        by_context = proportions.mean(axis=1)
        author_probability = np.einsum(
            "c,acbo->abo",
            reference_weight,
            by_context,
        )
        observation_weight = (
            reference_weight[None, :, None]
            / len(selected)
        )
        effective_trials = 1.0 / np.sum(
            observation_weight[None] ** 2
            / trials,
            axis=(1, 2),
        )
    author_probability = (
        author_probability * effective_trials[..., None] + 0.5
    ) / (
        effective_trials[..., None]
        + 0.5 * author_probability.shape[-1]
    )
    author_probability = np.clip(author_probability, 1e-8, None)
    author_probability /= author_probability.sum(
        axis=-1,
        keepdims=True,
    )
    reference_by_context = predict_reference_router(
        reference_fit,
        sample["contexts"]["all"][contexts],
    )
    reference_probability = np.einsum(
        "c,cbo->bo",
        reference_weight,
        reference_by_context,
    )
    basis = ilr_basis(author_probability.shape[-1])
    return (
        ilr(author_probability, basis)
        - ilr(reference_probability, basis)[None]
    ).reshape(len(author_probability), -1)


def true_standardized_profile(
    sample: dict[str, Any],
    context_indices: Iterable[int],
    *,
    reference_fit: dict[str, np.ndarray],
    context_weights: np.ndarray | None = None,
) -> np.ndarray:
    """Return the scorer-only profile under the fixed target design."""
    contexts = np.asarray(tuple(context_indices), dtype=int)
    if context_weights is None:
        context_weights = np.ones(len(contexts), dtype=float)
    weights = np.asarray(context_weights, dtype=float)
    weights /= weights.sum()
    probability = np.asarray(sample["probability"])[:, :, contexts]
    probability = np.einsum(
        "c,ascbo->abo",
        weights,
        probability,
    ) / probability.shape[1]
    reference = predict_reference_router(
        reference_fit,
        sample["contexts"]["all"][contexts],
    )
    reference = np.einsum("c,cbo->bo", weights, reference)
    basis = ilr_basis(probability.shape[-1])
    return (
        ilr(probability, basis) - ilr(reference, basis)[None]
    ).reshape(len(probability), -1)


def cross_validated_rank_selection(
    left: np.ndarray,
    right: np.ndarray,
    *,
    candidates: Iterable[int],
    folds: int,
    seed: int,
) -> tuple[int, pd.DataFrame]:
    """Select stable rank by author-level one-standard-error prediction."""
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    if x.shape != y.shape:
        raise ValueError("left and right calibration profiles must match")
    if folds < 2 or folds > len(x):
        raise ValueError("invalid fold count")
    ranks = sorted(set(int(rank) for rank in candidates))
    if not ranks or ranks[0] < 0 or ranks[-1] > x.shape[1]:
        raise ValueError("invalid candidate ranks")
    order = np.random.default_rng(seed).permutation(len(x))
    fold_indices = np.array_split(order, folds)
    rows: list[dict[str, float | int]] = []
    for rank in ranks:
        losses = []
        for valid in fold_indices:
            train = np.setdiff1d(order, valid, assume_unique=True)
            denoiser = fit_group_free_denoiser(
                x[train],
                y[train],
                rank=rank,
            )
            center = np.asarray(denoiser["center"])
            predict_y = apply_group_free_denoiser(x[valid], denoiser)
            predict_x = apply_group_free_denoiser(y[valid], denoiser)
            numerator = (
                np.sum((y[valid] - predict_y) ** 2)
                + np.sum((x[valid] - predict_x) ** 2)
            )
            denominator = (
                np.sum((y[valid] - center) ** 2)
                + np.sum((x[valid] - center) ** 2)
            )
            losses.append(float(numerator / max(denominator, 1e-12)))
        rows.append({
            "rank": rank,
            "mean_loss": float(np.mean(losses)),
            "se_loss": float(
                np.std(losses, ddof=1) / np.sqrt(len(losses))
            ),
        })
    table = pd.DataFrame(rows)
    best = table.sort_values(["mean_loss", "rank"]).iloc[0]
    threshold = float(best["mean_loss"] + best["se_loss"])
    table["one_se_threshold"] = threshold
    table["within_one_se"] = table["mean_loss"] <= threshold
    selected = int(
        table[table["within_one_se"]]
        .sort_values(["rank", "mean_loss"])
        .iloc[0]["rank"]
    )
    table["selected"] = table["rank"] == selected
    return selected, table


def fixed_reference_pairing_metrics(
    left: np.ndarray,
    right: np.ndarray,
    *,
    center: np.ndarray,
    neighbor_count: int,
) -> dict[str, float]:
    """Score matching without recentering on the evaluation cohort."""
    x = np.asarray(left, dtype=float) - np.asarray(center)[None]
    y = np.asarray(right, dtype=float) - np.asarray(center)[None]
    x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-12)
    y /= np.maximum(np.linalg.norm(y, axis=1, keepdims=True), 1e-12)
    similarity = x @ y.T
    positive = np.diag(similarity)
    identity = np.eye(len(x), dtype=bool)
    all_negative = similarity[~identity]
    discovery_similarity = x @ x.T
    np.fill_diagonal(discovery_similarity, -np.inf)
    count = min(int(neighbor_count), len(x) - 1)
    neighbors = np.argpartition(
        discovery_similarity,
        kth=len(x) - count,
        axis=1,
    )[:, -count:]
    hard_negative = similarity[
        np.arange(len(x))[:, None],
        neighbors,
    ].ravel()

    def auc(negative: np.ndarray) -> float:
        labels = np.concatenate([
            np.ones(len(positive), dtype=int),
            np.zeros(len(negative), dtype=int),
        ])
        return float(roc_auc_score(
            labels,
            np.concatenate([positive, negative]),
        ))

    return {
        "same_author_auc": auc(all_negative),
        "hard_neighbor_auc": auc(hard_negative),
        "top1": float(
            np.mean(similarity.argmax(axis=1) == np.arange(len(x)))
        ),
    }


def score_rank(
    *,
    calibration_left: np.ndarray,
    calibration_right: np.ndarray,
    evaluation_left: np.ndarray,
    evaluation_right: np.ndarray,
    evaluation_combined: np.ndarray,
    truth: np.ndarray,
    rank: int,
    neighbor_count: int,
) -> tuple[dict[str, float | int], dict[str, Any]]:
    """Fit one rank on calibration authors and score new authors."""
    denoiser = fit_group_free_denoiser(
        calibration_left,
        calibration_right,
        rank=rank,
    )
    left = apply_group_free_denoiser(evaluation_left, denoiser)
    right = apply_group_free_denoiser(evaluation_right, denoiser)
    estimate = apply_group_free_denoiser(
        evaluation_combined,
        denoiser,
    )
    center = np.asarray(denoiser["center"], dtype=float)
    truth_vector = np.asarray(truth, dtype=float).ravel()
    estimate_vector = np.asarray(estimate, dtype=float).ravel()
    correlation = (
        float(np.corrcoef(estimate_vector, truth_vector)[0, 1])
        if np.std(estimate_vector) > 1e-12
        and np.std(truth_vector) > 1e-12
        else 0.0
    )
    truth_scale = float(np.sqrt(np.mean(
        (np.asarray(truth) - center[None]) ** 2
    )))
    metrics = {
        "requested_rank": int(rank),
        "effective_rank": int(denoiser["rank"]),
        "truth_correlation": correlation,
        "truth_nrmse": float(
            np.sqrt(np.mean((estimate - truth) ** 2))
            / max(truth_scale, 1e-12)
        ),
        "split_reliability": float(
            multivariate_reliability(left.copy(), right.copy())
        ),
        **fixed_reference_pairing_metrics(
            left,
            right,
            center=center,
            neighbor_count=neighbor_count,
        ),
    }
    return metrics, denoiser


def recovery_identity_state(
    metrics: dict[str, float | int],
    *,
    truth_threshold: float,
    reliability_threshold: float,
    auc_threshold: float,
    top1_threshold: float,
) -> dict[str, bool]:
    """Return the registered joint recovery/identity state."""
    recovery = bool(
        metrics["truth_correlation"] >= truth_threshold
        and metrics["split_reliability"] >= reliability_threshold
    )
    identity = bool(
        metrics["hard_neighbor_auc"] >= auc_threshold
        and metrics["top1"] >= top1_threshold
    )
    return {
        "recovery": recovery,
        "identity": identity,
        "recovery_only": recovery and not identity,
        "identity_only": identity and not recovery,
        "both": recovery and identity,
        "neither": not recovery and not identity,
    }


def clone_spec(
    spec: AdaptiveReferenceWorldSpec,
    **changes: Any,
) -> AdaptiveReferenceWorldSpec:
    """Return a dataclass copy for registered sensitivity arms."""
    return replace(spec, **changes)
