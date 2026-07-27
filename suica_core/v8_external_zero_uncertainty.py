"""External-zero scoring and uncertainty operators for SUICA V8.3.7F.

The module deliberately treats omitted coordinates as an unresolved channel.
They are called noise only after cross-session and permutation controls fail
to find stable author information.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.special import softmax
from sklearn.metrics import roc_auc_score

from .v8_adaptive_rank_reference import (
    estimate_standardized_profile,
)
from .v8_author_routing_operator import (
    context_feature_map,
    ilr,
    ilr_basis,
    ilr_inverse,
    multivariate_reliability,
    predict_reference_router,
    registered_contexts,
)


@dataclass(frozen=True)
class ExternalZeroWorldSpec:
    """Synthetic world for external norms and residual sufficiency."""

    authors: int = 736
    world: str = "hard_rank12"
    events_per_context_session: int = 256
    branches: int = 4
    sessions: int = 2
    discovery_contexts: int = 12
    confirmation_contexts: int = 8
    extrapolation_contexts: int = 4
    shared_rms: float = 0.45
    context_rms: float = 0.35
    author_rms: float = 0.30
    author_context_rms: float = 0.20
    state_rms: float = 0.16
    dense_exponent: float = 0.75

    @property
    def cells(self) -> int:
        return self.branches**2

    @property
    def dimension(self) -> int:
        return self.cells * (self.branches - 1)

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


def stable_spectrum(
    *,
    world: str,
    dimension: int,
    exponent: float,
) -> np.ndarray:
    """Return the planted stable-author spectrum."""
    if world == "hard_rank12":
        weights = np.zeros(dimension, dtype=float)
        weights[:12] = 1.0
        return weights
    if world in {"dense_tail48", "dense_state_alias"}:
        index = np.arange(1, dimension + 1, dtype=float)
        return (1.0 + index / 4.0) ** (-float(exponent))
    if world == "author_permutation":
        weights = np.zeros(dimension, dtype=float)
        weights[:12] = 1.0
        return weights
    raise ValueError(f"unsupported V3.7F world: {world}")


def simulate_external_zero_world(
    *,
    seed: int,
    spec: ExternalZeroWorldSpec,
) -> dict[str, Any]:
    """Generate a full-rank-capable routing world.

    ``stable_probability`` excludes temporary state and is scorer-only.
    ``probability`` is the observable process. In the permutation control the
    second session receives a permuted author component while preserving
    session marginals.
    """
    streams = np.random.SeedSequence(seed).spawn(8)
    (
        rng_shared,
        rng_context,
        rng_author,
        rng_interaction,
        rng_state,
        rng_permutation,
        rng_context_seed,
        _,
    ) = (np.random.default_rng(stream) for stream in streams)
    contexts = registered_contexts(
        seed=int(
            rng_context_seed.integers(0, np.iinfo(np.int32).max)
        ),
        spec=type("_ContextSpec", (), {
            "context_dimensions": 3,
            "discovery_contexts": spec.discovery_contexts,
            "confirmation_contexts": spec.confirmation_contexts,
            "extrapolation_contexts": spec.extrapolation_contexts,
        })(),
    )
    dimension = spec.dimension
    shared = _scale_rms(
        _from_ilr(
            rng_shared.normal(size=dimension),
            cells=spec.cells,
            branches=spec.branches,
        ),
        spec.shared_rms,
    )
    features = context_feature_map(contexts["all"])
    features -= features[: spec.discovery_contexts].mean(
        axis=0,
        keepdims=True,
    )
    context_loading = _haar(
        rng_context,
        dimension,
        features.shape[1],
    )
    context_target = (
        0.0
        if spec.world in {"hard_rank12", "author_permutation"}
        else spec.context_rms
    )
    context = _scale_rms(
        _from_ilr(
            features @ context_loading.T,
            cells=spec.cells,
            branches=spec.branches,
        ),
        context_target,
    )
    loading = _haar(rng_author, dimension, dimension)
    score = rng_author.normal(size=(spec.authors, dimension))
    weights = stable_spectrum(
        world=spec.world,
        dimension=dimension,
        exponent=spec.dense_exponent,
    )
    author_ilr = (score * weights[None]) @ loading.T
    author = _scale_rms(
        _from_ilr(
            author_ilr,
            cells=spec.cells,
            branches=spec.branches,
        ),
        spec.author_rms,
    )
    interaction_rank = features.shape[1]
    interaction_score = rng_interaction.normal(
        size=(spec.authors, interaction_rank),
    )
    interaction_loading = (
        loading[:, :interaction_rank]
        if spec.world in {"hard_rank12", "author_permutation"}
        else _haar(rng_interaction, dimension, interaction_rank)
    )
    interaction_ilr = np.einsum(
        "ar,cr,dr->acd",
        interaction_score,
        features[:, :interaction_rank],
        interaction_loading,
    )
    interaction_target = (
        0.0
        if spec.world in {"hard_rank12", "author_permutation"}
        else spec.author_context_rms
    )
    interaction = _scale_rms(
        _from_ilr(
            interaction_ilr,
            cells=spec.cells,
            branches=spec.branches,
        ),
        interaction_target,
    )
    stable_eta = (
        shared[None, None]
        + context[None]
        + author[:, None]
        + interaction
    )
    stable_probability = softmax(
        np.repeat(
            stable_eta[:, None],
            spec.sessions,
            axis=1,
        ),
        axis=-1,
    )
    observed_eta = np.repeat(
        stable_eta[:, None],
        spec.sessions,
        axis=1,
    )
    if spec.world == "author_permutation":
        for session in range(1, spec.sessions):
            permutation = rng_permutation.permutation(spec.authors)
            observed_eta[:, session] = (
                shared[None, None]
                + context[None]
                + author[permutation, None]
                + interaction[permutation]
            )
    elif spec.world == "dense_state_alias":
        state_rank = min(8, dimension)
        state_loading = _haar(rng_state, dimension, state_rank)
        shared_state = rng_state.normal(
            size=(spec.authors, state_rank),
        )
        innovation = rng_state.normal(
            size=(spec.authors, spec.sessions, state_rank),
        )
        state_score = (
            0.80 * shared_state[:, None]
            + np.sqrt(1.0 - 0.80**2) * innovation
        )
        state_ilr = np.einsum(
            "asr,dr->asd",
            state_score,
            state_loading,
        )
        state = _scale_rms(
            _from_ilr(
                state_ilr,
                cells=spec.cells,
                branches=spec.branches,
            ),
            spec.state_rms,
        )
        observed_eta += state[:, :, None]
    probability = softmax(observed_eta, axis=-1)
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
        "world": spec.world,
        "contexts": contexts,
        "counts": np.zeros_like(probability, dtype=np.int16),
        "trials": trials,
        "probability": probability,
        "stable_probability": stable_probability,
        "components": {
            "stable_loading": loading,
            "stable_score": score,
            "stable_weights": weights,
            "stable_author_ilr": author_ilr,
        },
        "design": {
            "authors": spec.authors,
            "dimension": dimension,
            "world": spec.world,
            "events_per_context_session": (
                spec.events_per_context_session
            ),
        },
    }


def with_event_budget(
    sample: dict[str, Any],
    events_per_context_session: int,
) -> dict[str, Any]:
    """Return the same latent world under another event budget."""
    cells = np.asarray(sample["probability"]).shape[-2]
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
    """Subset all author-indexed arrays without sharing mutable memory."""
    selected = np.asarray(indices, dtype=int)
    author_count = np.asarray(sample["probability"]).shape[0]
    result = dict(sample)
    for key, value in sample.items():
        if (
            isinstance(value, np.ndarray)
            and value.ndim > 0
            and value.shape[0] == author_count
        ):
            result[key] = value[selected].copy()
    result["design"] = dict(sample.get("design", {}))
    result["design"]["authors"] = int(len(selected))
    return result


def true_stable_profile(
    sample: dict[str, Any],
    context_indices: Iterable[int],
    *,
    reference_fit: dict[str, np.ndarray],
    sessions: int | Iterable[int] = (0, 1),
) -> np.ndarray:
    """Return scorer-only stable profiles against the fitted external router."""
    contexts = np.asarray(tuple(context_indices), dtype=int)
    if isinstance(sessions, (int, np.integer)):
        selected = np.asarray([int(sessions)], dtype=int)
    else:
        selected = np.asarray(tuple(sessions), dtype=int)
    probability = np.asarray(sample["stable_probability"])[
        :, selected
    ][:, :, contexts].mean(axis=(1, 2))
    reference = predict_reference_router(
        reference_fit,
        np.asarray(sample["contexts"]["all"])[contexts],
    ).mean(axis=0)
    basis = ilr_basis(probability.shape[-1])
    return (
        ilr(probability, basis)
        - ilr(reference, basis)[None]
    ).reshape(len(probability), -1)


def true_observed_profile(
    sample: dict[str, Any],
    context_indices: Iterable[int],
    *,
    reference_fit: dict[str, np.ndarray],
    sessions: int | Iterable[int] = (0, 1),
) -> np.ndarray:
    """Return the infinite-event profile of the observable process."""
    proxy = dict(sample)
    proxy["stable_probability"] = np.asarray(sample["probability"])
    return true_stable_profile(
        proxy,
        context_indices,
        reference_fit=reference_fit,
        sessions=sessions,
    )


def empirical_parametric_sample(
    sample: dict[str, Any],
) -> dict[str, Any]:
    """Replace latent probabilities with smoothed observed proportions."""
    counts = np.asarray(sample["counts"], dtype=float)
    trials = np.asarray(sample["trials"], dtype=float)
    probability = (counts + 0.5) / (
        trials[..., None] + 0.5 * counts.shape[-1]
    )
    result = dict(sample)
    result["probability"] = probability
    result["counts"] = np.zeros_like(sample["counts"], dtype=np.int16)
    return result


def resample_counts_fast(
    sample: dict[str, Any],
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Draw independent multinomial counts for balanced V3.7F panels."""
    probability = np.asarray(sample["probability"], dtype=float)
    trials = np.asarray(sample["trials"], dtype=np.int16)
    if not np.all(trials == trials.flat[0]):
        raise ValueError("fast sampler requires a balanced trial tensor")
    flat = probability.reshape(-1, probability.shape[-1])
    counts = rng.multinomial(int(trials.flat[0]), flat).reshape(
        probability.shape
    )
    result = dict(sample)
    result["counts"] = counts.astype(np.int16, copy=False)
    result["trials"] = trials.copy()
    return result


def estimate_external_zero(
    zero_sample: dict[str, Any],
    context_indices: Iterable[int],
    *,
    reference_fit: dict[str, np.ndarray],
) -> np.ndarray:
    """Estimate an absolute score origin from independent norm authors."""
    profile = estimate_standardized_profile(
        zero_sample,
        context_indices,
        reference_fit=reference_fit,
    )
    return profile.mean(axis=0)


def fit_external_zero_denoiser(
    left: np.ndarray,
    right: np.ndarray,
    *,
    external_zero: np.ndarray,
    rank: int | None,
    soft: bool = False,
) -> dict[str, Any]:
    """Fit a stable cross-session operator around a frozen external zero."""
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    zero = np.asarray(external_zero, dtype=float)
    if x.shape != y.shape or x.shape[1:] != zero.shape:
        raise ValueError("profiles and external zero are incompatible")
    xc = x - zero
    yc = y - zero
    covariance = (
        xc.T @ yc + yc.T @ xc
    ) / (2.0 * max(len(x) - 1, 1))
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    positive = int(np.sum(eigenvalues > 1e-10))
    if rank is None:
        requested = x.shape[1]
        used = positive
    else:
        requested = int(rank)
        if requested < 0 or requested > x.shape[1]:
            raise ValueError("invalid denoiser rank")
        used = min(requested, positive)
    basis = eigenvectors[:, :used]
    difference = 0.5 * (xc - yc)
    noise_covariance = (
        difference.T @ difference
    ) / max(len(x) - 1, 1)
    noise_energy = (
        np.diag(basis.T @ noise_covariance @ basis)
        if used else np.asarray([], dtype=float)
    )
    signal_energy = np.clip(eigenvalues[:used], 0.0, None)
    if soft:
        weights = signal_energy / np.maximum(
            signal_energy + noise_energy / 8.0,
            1e-12,
        )
    else:
        weights = np.ones(used, dtype=float)
    projector = (
        basis @ np.diag(weights) @ basis.T
        if used else np.zeros_like(covariance)
    )
    orthogonal = (
        basis @ basis.T
        if used else np.zeros_like(covariance)
    )
    return {
        "external_zero": zero,
        "basis": basis,
        "eigenvalues": eigenvalues,
        "noise_energy": noise_energy,
        "weights": weights,
        "projector": projector,
        "orthogonal_projector": orthogonal,
        "requested_rank": requested,
        "rank": used,
        "soft": bool(soft),
    }


def apply_external_zero_denoiser(
    profile: np.ndarray,
    denoiser: dict[str, Any],
) -> np.ndarray:
    """Score profiles without introducing a calibration-cohort origin."""
    values = np.asarray(profile, dtype=float)
    zero = np.asarray(denoiser["external_zero"], dtype=float)
    projector = np.asarray(denoiser["projector"], dtype=float)
    return zero + (values - zero) @ projector


def unresolved_residual(
    profile: np.ndarray,
    denoiser: dict[str, Any],
) -> np.ndarray:
    """Return coordinates omitted by the selected stable subspace."""
    values = np.asarray(profile, dtype=float)
    zero = np.asarray(denoiser["external_zero"], dtype=float)
    orthogonal = np.asarray(
        denoiser["orthogonal_projector"],
        dtype=float,
    )
    return (values - zero) @ (
        np.eye(values.shape[-1]) - orthogonal
    )


def cross_validated_external_rank_selection(
    left: np.ndarray,
    right: np.ndarray,
    *,
    external_zero: np.ndarray,
    candidates: Iterable[int],
    folds: int,
    seed: int,
) -> tuple[int, pd.DataFrame]:
    """Select rank by author CV while keeping the external origin frozen."""
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    ranks = sorted(set(int(value) for value in candidates))
    if x.shape != y.shape:
        raise ValueError("profile halves must match")
    if not ranks or ranks[0] < 0 or ranks[-1] > x.shape[1]:
        raise ValueError("invalid candidate ranks")
    order = np.random.default_rng(seed).permutation(len(x))
    partitions = np.array_split(order, folds)
    rows: list[dict[str, float | int]] = []
    zero = np.asarray(external_zero, dtype=float)
    for rank in ranks:
        losses = []
        for valid in partitions:
            train = np.setdiff1d(order, valid, assume_unique=True)
            fit = fit_external_zero_denoiser(
                x[train],
                y[train],
                external_zero=zero,
                rank=rank,
            )
            predict_y = apply_external_zero_denoiser(x[valid], fit)
            predict_x = apply_external_zero_denoiser(y[valid], fit)
            numerator = (
                np.sum((y[valid] - predict_y) ** 2)
                + np.sum((x[valid] - predict_x) ** 2)
            )
            denominator = (
                np.sum((y[valid] - zero) ** 2)
                + np.sum((x[valid] - zero) ** 2)
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


def _auc(positive: np.ndarray, negative: np.ndarray) -> float:
    labels = np.concatenate([
        np.ones(len(positive), dtype=int),
        np.zeros(len(negative), dtype=int),
    ])
    values = np.concatenate([positive, negative])
    return float(roc_auc_score(labels, values))


def paired_similarity_metrics(
    left: np.ndarray,
    right: np.ndarray,
    *,
    neighbor_count: int,
    discovery: np.ndarray | None = None,
) -> dict[str, float]:
    """Return same-author and hard-neighbor pairing metrics."""
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    if x.shape != y.shape:
        raise ValueError("pairing views must match")
    if x.shape[1] == 0 or np.max(np.linalg.norm(x, axis=1)) <= 1e-12:
        return {
            "same_author_auc": 0.5,
            "hard_neighbor_auc": 0.5,
            "top1": 1.0 / max(len(x), 1),
        }
    x = x / np.maximum(
        np.linalg.norm(x, axis=1, keepdims=True),
        1e-12,
    )
    y = y / np.maximum(
        np.linalg.norm(y, axis=1, keepdims=True),
        1e-12,
    )
    similarity = x @ y.T
    positive = np.diag(similarity)
    identity = np.eye(len(x), dtype=bool)
    all_negative = similarity[~identity]
    anchor = x if discovery is None else np.asarray(discovery, dtype=float)
    anchor = anchor / np.maximum(
        np.linalg.norm(anchor, axis=1, keepdims=True),
        1e-12,
    )
    neighborhood = anchor @ anchor.T
    np.fill_diagonal(neighborhood, -np.inf)
    count = min(int(neighbor_count), len(x) - 1)
    neighbors = np.argpartition(
        neighborhood,
        kth=len(x) - count,
        axis=1,
    )[:, -count:]
    hard_negative = similarity[
        np.arange(len(x))[:, None],
        neighbors,
    ].ravel()
    return {
        "same_author_auc": _auc(positive, all_negative),
        "hard_neighbor_auc": _auc(positive, hard_negative),
        "top1": float(
            np.mean(similarity.argmax(axis=1) == np.arange(len(x)))
        ),
    }


def residual_sufficiency_metrics(
    left: np.ndarray,
    right: np.ndarray,
    *,
    denoiser: dict[str, Any],
    neighbor_count: int,
    permutation: np.ndarray | None = None,
) -> dict[str, float]:
    """Audit stable information omitted by a hard projection."""
    score_left = (
        apply_external_zero_denoiser(left, denoiser)
        - np.asarray(denoiser["external_zero"])
    )
    score_right = (
        apply_external_zero_denoiser(right, denoiser)
        - np.asarray(denoiser["external_zero"])
    )
    residual_left = unresolved_residual(left, denoiser)
    residual_right = unresolved_residual(right, denoiser)
    if permutation is not None:
        residual_right = residual_right[np.asarray(permutation, dtype=int)]
    score_metrics = paired_similarity_metrics(
        score_left,
        score_right,
        neighbor_count=neighbor_count,
    )
    residual_metrics = paired_similarity_metrics(
        residual_left,
        residual_right,
        neighbor_count=neighbor_count,
        discovery=score_left,
    )
    score_scale = np.maximum(
        np.sqrt(np.mean(score_left**2, axis=0, keepdims=True)),
        1e-8,
    )
    residual_scale = np.maximum(
        np.sqrt(np.mean(residual_left**2, axis=0, keepdims=True)),
        1e-8,
    )
    joint_left = np.column_stack([
        score_left / score_scale,
        residual_left / residual_scale,
    ])
    joint_right = np.column_stack([
        score_right / score_scale,
        residual_right / residual_scale,
    ])
    joint_metrics = paired_similarity_metrics(
        joint_left,
        joint_right,
        neighbor_count=neighbor_count,
        discovery=score_left,
    )
    reliability = (
        float(multivariate_reliability(
            residual_left.copy(),
            residual_right.copy(),
        ))
        if np.std(residual_left) > 1e-12
        and np.std(residual_right) > 1e-12
        else 0.0
    )
    return {
        "score_hard_neighbor_auc": score_metrics["hard_neighbor_auc"],
        "residual_hard_neighbor_auc": (
            residual_metrics["hard_neighbor_auc"]
        ),
        "joint_hard_neighbor_auc": joint_metrics["hard_neighbor_auc"],
        # Residual AUC is computed only against hard negatives selected in the
        # retained score space. Its excess over chance is therefore the
        # conditional information gain; joint AUC is reported separately
        # because it can be ceiling-limited when the retained score is strong.
        "residual_incremental_auc": (
            residual_metrics["hard_neighbor_auc"] - 0.5
        ),
        "residual_reliability": reliability,
        "residual_energy": float(np.mean(
            0.5 * (residual_left**2 + residual_right**2)
        )),
    }


def normalized_mse(
    estimate: np.ndarray,
    truth: np.ndarray,
) -> float:
    """Return MSE normalized by the scorer-only truth energy."""
    values = np.asarray(estimate, dtype=float)
    target = np.asarray(truth, dtype=float)
    scale = float(np.mean(target**2))
    return float(np.mean((values - target) ** 2) / max(scale, 1e-12))


def fit_error_asymptote(
    budgets: np.ndarray,
    errors: np.ndarray,
) -> dict[str, float]:
    """Fit ``floor + amplitude * budget ** -alpha``."""
    x = np.asarray(budgets, dtype=float)
    y = np.asarray(errors, dtype=float)

    def curve(
        budget: np.ndarray,
        floor: float,
        amplitude: float,
        alpha: float,
    ) -> np.ndarray:
        return floor + amplitude * budget ** (-alpha)

    try:
        parameter, _ = curve_fit(
            curve,
            x,
            y,
            p0=(max(0.0, float(y.min()) * 0.5), float(y.max()), 1.0),
            bounds=([0.0, 0.0, 0.1], [np.inf, np.inf, 3.0]),
            maxfev=20_000,
        )
        fitted = curve(x, *parameter)
        return {
            "floor": float(parameter[0]),
            "amplitude": float(parameter[1]),
            "alpha": float(parameter[2]),
            "rmse": float(np.sqrt(np.mean((fitted - y) ** 2))),
        }
    except (RuntimeError, ValueError):
        return {
            "floor": float("nan"),
            "amplitude": float("nan"),
            "alpha": float("nan"),
            "rmse": float("nan"),
        }


def functional_anova_energy(
    samples: np.ndarray,
) -> dict[str, float]:
    """Decompose a balanced R by K by E score tensor by Hoeffding ANOVA."""
    values = np.asarray(samples, dtype=float)
    if values.ndim < 4:
        raise ValueError("samples must be R by K by E by ...")
    grand = values.mean(axis=(0, 1, 2), keepdims=True)
    r = values.mean(axis=(1, 2), keepdims=True) - grand
    k = values.mean(axis=(0, 2), keepdims=True) - grand
    e = values.mean(axis=(0, 1), keepdims=True) - grand
    rk = (
        values.mean(axis=2, keepdims=True)
        - grand - r - k
    )
    re = (
        values.mean(axis=1, keepdims=True)
        - grand - r - e
    )
    ke = (
        values.mean(axis=0, keepdims=True)
        - grand - k - e
    )
    rke = values - grand - r - k - e - rk - re - ke
    components = {
        "reference": r,
        "selection": k,
        "event": e,
        "reference_selection": rk,
        "reference_event": re,
        "selection_event": ke,
        "three_way": rke,
    }
    energies = {
        name: float(np.mean(component**2))
        for name, component in components.items()
    }
    total = float(np.mean((values - grand) ** 2))
    reconstructed = float(sum(energies.values()))
    energies["total"] = total
    energies["reconstruction_error"] = float(
        abs(reconstructed - total) / max(total, 1e-12)
    )
    return energies


def confidence_region_metrics(
    bootstrap: np.ndarray,
    truth: np.ndarray,
    *,
    regularization: float = 0.50,
) -> dict[str, float]:
    """Score held-out Monte Carlo Mahalanobis confidence regions.

    The first 75% of draws calibrate bias, covariance, and radius. Coverage is
    evaluated on the remaining draws. In V3.7F these are scorer-known
    synthetic repeated samples, not a deployable claim that truth is known.
    """
    values = np.asarray(bootstrap, dtype=float)
    target = np.asarray(truth, dtype=float)
    if values.ndim != 3 or target.shape != values.shape[1:]:
        raise ValueError("bootstrap must be draws by authors by dimensions")
    cover = []
    radii = []
    for author in range(values.shape[1]):
        cloud = values[:, author]
        order = np.random.default_rng(0x37F + author).permutation(
            len(cloud)
        )
        first = max(4, len(cloud) // 2)
        second = max(first + 2, first + len(cloud) // 4)
        second = min(second, len(cloud) - 1)
        fit_cloud = cloud[order[:first]]
        radius_cloud = cloud[order[first:second]]
        validation = cloud[order[second:]]
        error = fit_cloud - target[author]
        bias = error.mean(axis=0)
        centered = error - bias
        covariance = np.cov(centered, rowvar=False)
        average_variance = max(
            float(np.trace(covariance)) / max(cloud.shape[1], 1),
            1e-10,
        )
        covariance = (
            (1.0 - regularization) * covariance
            + regularization
            * average_variance
            * np.eye(cloud.shape[1])
        )
        inverse = np.linalg.pinv(covariance, hermitian=True)
        radius_error = radius_cloud - target[author] - bias
        distance = np.einsum(
            "ni,ij,nj->n",
            radius_error,
            inverse,
            radius_error,
        )
        conformal_index = min(
            len(distance) - 1,
            int(np.ceil(0.95 * (len(distance) + 1))) - 1,
        )
        threshold = float(np.sort(distance)[conformal_index])
        validation_error = validation - target[author] - bias
        validation_distance = np.einsum(
            "ni,ij,nj->n",
            validation_error,
            inverse,
            validation_error,
        )
        eigen_max = float(np.linalg.eigvalsh(covariance).max())
        cover.extend((validation_distance <= threshold).tolist())
        radii.append(np.sqrt(max(threshold * eigen_max, 0.0)))
    return {
        "coverage": float(np.mean(cover)),
        "median_radius": float(np.median(radii)),
        "maximum_radius": float(np.max(radii)),
    }


def mdc_metrics(
    event_bootstrap: np.ndarray,
    *,
    rng: np.random.Generator,
) -> dict[str, float]:
    """Estimate null MDC and power for a planted two-MDC movement."""
    values = np.asarray(event_bootstrap, dtype=float)
    if values.ndim != 3:
        raise ValueError("event bootstrap must be draws by authors by dims")
    order = rng.permutation(values.shape[0])
    midpoint = len(order) // 2
    pairs = min(midpoint, len(order) - midpoint)
    left = values[order[:pairs]]
    right = values[order[midpoint : midpoint + pairs]]
    null_change = np.linalg.norm(left - right, axis=-1).ravel()
    mdc = float(np.quantile(null_change, 0.95))
    direction = values.mean(axis=(0, 1))
    if np.linalg.norm(direction) <= 1e-12:
        direction = np.ones(values.shape[-1])
    direction = direction / np.linalg.norm(direction)
    planted = np.linalg.norm(
        left - (right + 2.0 * mdc * direction),
        axis=-1,
    ).ravel()
    return {
        "mdc95": mdc,
        "null_false_positive": float(np.mean(null_change > mdc)),
        "two_mdc_power": float(np.mean(planted > mdc)),
    }
