"""Dimension-density-event-budget geometry for SUICA V8.3.7D."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.special import softmax
from sklearn.metrics import roc_auc_score

from .v8_author_routing_operator import (
    context_feature_map,
    fit_reference_router,
    ilr_basis,
    multivariate_reliability,
    registered_contexts,
)
from .v8_group_free_routing_transport import (
    apply_group_free_denoiser,
    estimate_fixed_reference_profile,
    fit_group_free_denoiser,
    flat_correlation,
    group_free_pairing_metrics,
    resample_routing_counts,
    true_fixed_reference_profile,
)


@dataclass(frozen=True)
class DensityWorldSpec:
    """Synthetic group-free author-operator dimensions."""

    authors: int = 96
    latent_rank: int = 6
    events_per_context_session: int = 128
    author_rms: float = 0.30
    branches: int = 4
    sessions: int = 2
    discovery_contexts: int = 12
    confirmation_contexts: int = 8
    extrapolation_contexts: int = 4
    shared_rms: float = 0.45
    context_rms: float = 0.35
    session_rms: float = 0.10
    author_basis_rank: int | None = None

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


def _haar(rng: np.random.Generator, dimension: int, rank: int) -> np.ndarray:
    if rank <= 0 or rank > dimension:
        raise ValueError("rank outside routing dimension")
    return np.linalg.qr(rng.normal(size=(dimension, rank)), mode="reduced")[0]


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


def _draw_counts(
    probability: np.ndarray,
    trials: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    cumulative = np.cumsum(probability, axis=-1)
    eye = np.eye(probability.shape[-1], dtype=np.int16)
    counts = np.zeros_like(probability, dtype=np.int16)
    for draw in range(int(trials.max(initial=0))):
        uniform = rng.random(trials.shape)
        outcome = np.sum(uniform[..., None] > cumulative, axis=-1)
        active = trials > draw
        counts += eye[outcome] * active[..., None]
    return counts


def simulate_group_free_density_world(
    *,
    seed: int,
    spec: DensityWorldSpec,
) -> dict[str, Any]:
    """Generate a latent author-routing world without group centering."""
    sequences = np.random.SeedSequence(seed).spawn(6)
    rng_shared, rng_context, rng_author, rng_session, rng_counts, rng_ctx = (
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
    basis_rank = (
        spec.author_basis_rank
        if spec.author_basis_rank is not None
        else spec.latent_rank
    )
    if basis_rank < spec.latent_rank:
        raise ValueError("author_basis_rank cannot be below latent_rank")
    author_loading_full = _haar(rng_author, dimension, basis_rank)
    author_score = rng_author.normal(
        size=(spec.authors, basis_rank)
    )
    author_score -= author_score.mean(axis=0, keepdims=True)
    author_loading = author_loading_full[:, : spec.latent_rank]
    author = _scale_rms(
        _from_ilr(
            author_score[:, : spec.latent_rank] @ author_loading.T,
            cells=spec.cells,
            branches=spec.branches,
        ),
        spec.author_rms,
    )
    session_rank = min(3, dimension)
    session_loading = _haar(rng_session, dimension, session_rank)
    session_score = rng_session.normal(
        size=(spec.authors, session_rank)
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
        "world": "truly_group_free_density",
        "contexts": contexts,
        "counts": _draw_counts(probability, trials, rng_counts),
        "trials": trials,
        "probability": probability,
        "design": {
            "authors": spec.authors,
            "author_rank": spec.latent_rank,
            "author_basis_rank": basis_rank,
            "author_rms": spec.author_rms,
            "events_per_context_session": spec.events_per_context_session,
        },
    }


def with_event_budget(
    sample: dict[str, Any],
    events_per_context_session: int,
) -> dict[str, Any]:
    """Reuse latent probabilities under a new balanced event budget."""
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
    result["design"] = dict(sample.get("design", {}))
    result["design"]["events_per_context_session"] = int(
        events_per_context_session
    )
    return result


def author_geometry_diagnostics(
    truth: np.ndarray,
    left: np.ndarray,
    right: np.ndarray,
) -> dict[str, float]:
    """Measure raw and direction-normalized crowding diagnostics."""
    truth = np.asarray(truth, dtype=float)
    left = np.asarray(left, dtype=float).copy()
    right = np.asarray(right, dtype=float).copy()
    truth = truth - truth.mean(axis=0, keepdims=True)
    left = left - left.mean(axis=0, keepdims=True)
    right = right - right.mean(axis=0, keepdims=True)
    raw_combined = 0.5 * (left + right)
    raw_error = np.linalg.norm(raw_combined - truth, axis=1)

    def normalize(values: np.ndarray) -> np.ndarray:
        return values / np.maximum(
            np.linalg.norm(values, axis=1, keepdims=True),
            1e-12,
        )

    truth = normalize(truth)
    left = normalize(left)
    right = normalize(right)
    combined = 0.5 * (left + right)
    distance = np.linalg.norm(
        truth[:, None] - truth[None, :],
        axis=-1,
    )
    np.fill_diagonal(distance, np.inf)
    margin = distance.min(axis=1)
    finite_pair = distance[np.isfinite(distance)]
    left_error = np.linalg.norm(left - truth, axis=1)
    right_error = np.linalg.norm(right - truth, axis=1)
    combined_error = np.linalg.norm(combined - truth, axis=1)
    same_upper = left_error + right_error
    other_lower = (
        distance
        - left_error[:, None]
        - right_error[None, :]
    )
    certificate = same_upper < other_lower.min(axis=1)
    return {
        "median_truth_margin": float(np.median(margin)),
        "median_pair_distance": float(np.median(finite_pair)),
        "relative_margin": float(
            np.median(margin) / max(np.median(finite_pair), 1e-12)
        ),
        "median_raw_combined_error": float(np.median(raw_error)),
        "median_combined_error": float(np.median(combined_error)),
        "median_error_margin_ratio": float(
            np.median(combined_error / np.maximum(margin, 1e-12))
        ),
        "median_crowding_index": float(
            np.median(2.0 * combined_error / np.maximum(margin, 1e-12))
        ),
        "prototype_margin_fraction": float(
            np.mean(2.0 * combined_error < margin)
        ),
        "cross_session_certificate_fraction": float(
            certificate.mean()
        ),
    }


def random_neighbor_auc(
    left: np.ndarray,
    right: np.ndarray,
    *,
    neighbor_count: int,
    rng: np.random.Generator,
) -> float:
    """Score identity against random nonself neighbors as a density control."""
    left = np.asarray(left, dtype=float).copy()
    right = np.asarray(right, dtype=float).copy()
    left -= left.mean(axis=0, keepdims=True)
    right -= right.mean(axis=0, keepdims=True)
    left /= np.maximum(np.linalg.norm(left, axis=1, keepdims=True), 1e-12)
    right /= np.maximum(np.linalg.norm(right, axis=1, keepdims=True), 1e-12)
    similarity = left @ right.T
    positive = np.diag(similarity)
    count = min(neighbor_count, len(left) - 1)
    negatives = []
    candidates = np.arange(len(left))
    for author in range(len(left)):
        pool = candidates[candidates != author]
        selected = rng.choice(pool, size=count, replace=False)
        negatives.extend(similarity[author, selected])
    negatives = np.asarray(negatives)
    target = np.concatenate([
        np.ones(len(positive), dtype=int),
        np.zeros(len(negatives), dtype=int),
    ])
    return float(
        roc_auc_score(target, np.concatenate([positive, negatives]))
    )


def subset_authors(
    sample: dict[str, Any],
    indices: np.ndarray,
) -> dict[str, Any]:
    """Return an author-subset view while preserving shared design objects."""
    result = dict(sample)
    author_count = int(np.asarray(sample["counts"]).shape[0])
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


def evaluate_density_population(
    *,
    latent: dict[str, Any],
    reference_panel: dict[str, Any],
    observed_panel: dict[str, Any],
    primary_rank: int,
    oracle_rank: int,
    neighbor_count: int,
    training_indices: np.ndarray | None = None,
    evaluation_indices: np.ndarray | None = None,
    random_seed: int = 0,
) -> dict[str, float | int | bool]:
    """Fit on training authors and score disjoint evaluation authors."""
    author_count = int(np.asarray(latent["counts"]).shape[0])
    if training_indices is None:
        training_indices = np.arange(author_count)
    if evaluation_indices is None:
        evaluation_indices = np.arange(author_count)
    training_indices = np.asarray(training_indices, dtype=int)
    evaluation_indices = np.asarray(evaluation_indices, dtype=int)
    if np.intersect1d(training_indices, evaluation_indices).size:
        if not (
            len(training_indices) == author_count
            and len(evaluation_indices) == author_count
        ):
            raise ValueError("training and evaluation authors must be disjoint")
    latent_eval = subset_authors(latent, evaluation_indices)
    reference_train = subset_authors(reference_panel, training_indices)
    observed_train = subset_authors(observed_panel, training_indices)
    observed_eval = subset_authors(observed_panel, evaluation_indices)
    n_discovery = len(latent["contexts"]["discovery"])
    n_confirmation = len(latent["contexts"]["confirmation"])
    discovery = np.arange(n_discovery)
    confirmation = np.arange(
        n_discovery,
        n_discovery + n_confirmation,
    )
    reference_fit = fit_reference_router(reference_train, discovery)
    training_halves = [
        estimate_fixed_reference_profile(
            observed_train,
            discovery,
            reference_fit=reference_fit,
            sessions=session,
        )["profile"]
        for session in (0, 1)
    ]
    halves = [
        estimate_fixed_reference_profile(
            observed_eval,
            discovery,
            reference_fit=reference_fit,
            sessions=session,
        )["profile"]
        for session in (0, 1)
    ]
    combined = estimate_fixed_reference_profile(
        observed_eval,
        discovery,
        reference_fit=reference_fit,
    )["profile"]
    confirmation_profile = estimate_fixed_reference_profile(
        observed_eval,
        confirmation,
        reference_fit=reference_fit,
    )["profile"]
    truth = true_fixed_reference_profile(
        latent_eval,
        discovery,
        reference_fit=reference_fit,
    )

    def score(rank: int) -> dict[str, Any]:
        denoiser = fit_group_free_denoiser(
            training_halves[0],
            training_halves[1],
            rank=rank,
        )
        left, right = (
            apply_group_free_denoiser(profile, denoiser)
            for profile in halves
        )
        estimate = apply_group_free_denoiser(combined, denoiser)
        confirm = apply_group_free_denoiser(
            confirmation_profile,
            denoiser,
        )
        centered_truth = truth - truth.mean(axis=0, keepdims=True)
        centered_estimate = estimate - estimate.mean(
            axis=0,
            keepdims=True,
        )
        truth_scale = float(np.sqrt(np.mean(centered_truth**2)))
        return {
            "truth_correlation": flat_correlation(estimate, truth),
            "truth_nrmse": float(
                np.sqrt(np.mean((centered_estimate - centered_truth) ** 2))
                / max(truth_scale, 1e-12)
            ),
            "split_reliability": multivariate_reliability(left, right),
            "unseen_context_reliability": multivariate_reliability(
                estimate,
                confirm,
            ),
            **group_free_pairing_metrics(
                left,
                right,
                neighbor_count=neighbor_count,
            ),
            "random_neighbor_auc": random_neighbor_auc(
                left,
                right,
                neighbor_count=neighbor_count,
                rng=np.random.default_rng(random_seed + rank),
            ),
            **author_geometry_diagnostics(truth, left, right),
            "effective_rank": int(denoiser["rank"]),
        }

    primary = score(primary_rank)
    oracle = score(oracle_rank)
    return {
        **primary,
        "oracle_rank_truth_correlation": oracle["truth_correlation"],
        "oracle_rank_truth_nrmse": oracle["truth_nrmse"],
        "oracle_rank_local_neighbor_auc": oracle["local_neighbor_auc"],
        "oracle_rank_top1": oracle["top1"],
        "oracle_rank_certificate_fraction": oracle[
            "cross_session_certificate_fraction"
        ],
        "training_authors": int(len(training_indices)),
        "evaluation_authors": int(len(evaluation_indices)),
        "numeric_output": bool(
            np.isfinite([
                primary["truth_correlation"],
                primary["split_reliability"],
                primary["local_neighbor_auc"],
            ]).all()
        ),
    }
