"""Synthetic author-specific stochastic routing operators for SUICA V8.3.7A.

The estimator works on anonymous packet-level categorical counts. Author and
hidden-group identities are used only by the scorer after packet profiles have
been frozen.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
from scipy.linalg import helmert
from scipy.special import softmax
from scipy.stats import qmc
from sklearn.mixture import GaussianMixture
from sklearn.metrics import roc_auc_score


@dataclass(frozen=True)
class AuthorRoutingSpec:
    """Registered dimensions and signal amplitudes for V3.7A."""

    branches: int = 4
    groups: int = 4
    authors: int = 96
    discovery_contexts: int = 12
    confirmation_contexts: int = 8
    extrapolation_contexts: int = 4
    sessions: int = 2
    events_per_context_session: int = 32
    context_dimensions: int = 3
    shared_rms: float = 0.45
    context_rms: float = 0.35
    group_rms: float = 0.25
    author_rms: float = 0.30
    session_rms: float = 0.10
    author_rank: int = 6
    group_rank: int = 3
    context_rank: int = 6
    session_rank: int = 3
    minimum_marginal_probability: float = 0.05
    maximum_marginal_probability: float = 0.75
    minimum_normalized_entropy: float = 0.55

    @property
    def cells(self) -> int:
        """Number of incoming-branch by cue cells."""
        return self.branches**2

    @property
    def repeats_per_cell(self) -> int:
        """Registered number of events in each balanced cell."""
        if self.events_per_context_session % self.cells:
            raise ValueError(
                "events_per_context_session must be divisible by branches ** 2"
            )
        return self.events_per_context_session // self.cells

    @property
    def regular_contexts(self) -> int:
        """Number of interpolation contexts used by the primary analysis."""
        return self.discovery_contexts + self.confirmation_contexts

    @property
    def total_contexts(self) -> int:
        """All interpolation and extrapolation contexts."""
        return self.regular_contexts + self.extrapolation_contexts


def ilr_basis(branches: int) -> np.ndarray:
    """Return a fixed orthonormal simplex basis with shape K by K-1."""
    return helmert(branches, full=False).T


def ilr(probability: np.ndarray, basis: np.ndarray) -> np.ndarray:
    """Map strictly positive simplex coordinates to ILR coordinates."""
    values = np.asarray(probability, dtype=float)
    values = np.clip(values, 1e-9, None)
    values /= values.sum(axis=-1, keepdims=True)
    return np.log(values) @ basis


def ilr_inverse(coordinates: np.ndarray, basis: np.ndarray) -> np.ndarray:
    """Map ILR coordinates back to the probability simplex."""
    return softmax(np.asarray(coordinates, dtype=float) @ basis.T, axis=-1)


def _center_outcomes(values: np.ndarray) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    return result - result.mean(axis=-1, keepdims=True)


def _scale_rms(values: np.ndarray, target: float) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    rms = float(np.sqrt(np.mean(result**2)))
    if target == 0.0 or rms <= 1e-12:
        return np.zeros_like(result)
    return result * (target / rms)


def _balanced_groups(
    rng: np.random.Generator,
    spec: AuthorRoutingSpec,
) -> np.ndarray:
    if spec.authors % spec.groups:
        raise ValueError("authors must be divisible by groups")
    labels = np.repeat(
        np.arange(spec.groups),
        spec.authors // spec.groups,
    )
    return labels[rng.permutation(spec.authors)]


def registered_contexts(
    *,
    seed: int,
    spec: AuthorRoutingSpec,
) -> dict[str, np.ndarray]:
    """Create discovery, interpolation, and extrapolation context coordinates."""
    exponent = int(np.ceil(np.log2(max(spec.discovery_contexts, 2))))
    sobol = qmc.Sobol(
        d=spec.context_dimensions,
        scramble=True,
        seed=seed,
    )
    discovery = 2.0 * sobol.random_base2(exponent) - 1.0
    discovery = discovery[: spec.discovery_contexts]
    discovery -= discovery.mean(axis=0, keepdims=True)
    scale = np.maximum(np.max(np.abs(discovery), axis=0), 1e-9)
    discovery /= scale

    rng = np.random.default_rng(seed + 911)
    confirmation = np.empty(
        (spec.confirmation_contexts, spec.context_dimensions),
        dtype=float,
    )
    for index in range(spec.confirmation_contexts):
        selected = rng.choice(len(discovery), size=3, replace=False)
        weights = rng.dirichlet(np.ones(3))
        confirmation[index] = weights @ discovery[selected]

    directions = rng.normal(
        size=(spec.extrapolation_contexts, spec.context_dimensions)
    )
    directions /= np.maximum(
        np.linalg.norm(directions, axis=1, keepdims=True),
        1e-9,
    )
    extrapolation = 1.75 * directions
    return {
        "discovery": discovery,
        "confirmation": confirmation,
        "extrapolation": extrapolation,
        "all": np.vstack([discovery, confirmation, extrapolation]),
    }


def context_feature_map(contexts: np.ndarray) -> np.ndarray:
    """Registered six-term context basis, centered by the Sobol design."""
    z = np.asarray(contexts, dtype=float)
    if z.shape[1] != 3:
        raise ValueError("the registered context feature map requires 3 axes")
    return np.column_stack([
        z,
        z[:, 0] * z[:, 1],
        z[:, 0] * z[:, 2],
        z[:, 1] * z[:, 2],
    ])


def _group_center(
    values: np.ndarray,
    labels: np.ndarray,
    groups: int,
) -> np.ndarray:
    result = np.asarray(values, dtype=float).copy()
    for group in range(groups):
        mask = labels == group
        result[mask] -= result[mask].mean(axis=0, keepdims=True)
    return result


def _component_bank(
    *,
    seed: int,
    spec: AuthorRoutingSpec,
    contexts: np.ndarray,
    labels: np.ndarray,
) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    outcome_basis = ilr_basis(spec.branches)
    dimension = spec.cells * (spec.branches - 1)

    def haar_subspace(rank: int) -> np.ndarray:
        if rank <= 0 or rank > dimension:
            raise ValueError(f"rank must be in [1, {dimension}], got {rank}")
        matrix = rng.normal(size=(dimension, rank))
        return np.linalg.qr(matrix, mode="reduced")[0]

    def from_ilr(vector: np.ndarray) -> np.ndarray:
        coordinates = vector.reshape(
            *vector.shape[:-1],
            spec.cells,
            spec.branches - 1,
        )
        return coordinates @ outcome_basis.T

    shared_ilr = rng.normal(size=dimension)
    shared = _scale_rms(from_ilr(shared_ilr), spec.shared_rms)

    z = np.asarray(contexts, dtype=float)
    context_features = context_feature_map(z)
    if context_features.shape[1] != spec.context_rank:
        raise ValueError(
            "registered context_rank must match the six-term feature map"
        )
    context_features -= context_features.mean(axis=0, keepdims=True)
    context_loading = haar_subspace(spec.context_rank)
    context_ilr = context_features @ context_loading.T
    context = _scale_rms(from_ilr(context_ilr), spec.context_rms)

    group_rank = min(spec.group_rank, spec.groups - 1)
    group_loading = haar_subspace(group_rank)
    group_score = rng.normal(size=(spec.groups, group_rank))
    group_score -= group_score.mean(axis=0, keepdims=True)
    group_ilr = group_score @ group_loading.T
    group = _scale_rms(from_ilr(group_ilr), spec.group_rms)

    author_loading = haar_subspace(spec.author_rank)
    author_score = rng.normal(size=(spec.authors, spec.author_rank))
    author_score = _group_center(author_score, labels, spec.groups)
    author_ilr = author_score @ author_loading.T
    author = _scale_rms(from_ilr(author_ilr), spec.author_rms)

    session_loading = haar_subspace(spec.session_rank)
    session_score = rng.normal(size=(spec.authors, spec.session_rank))
    session_ilr = np.stack([session_score, -session_score], axis=1)
    session_ilr = np.einsum(
        "asr,dr->asd",
        session_ilr,
        session_loading,
    )
    session = _scale_rms(from_ilr(session_ilr), spec.session_rms)
    return {
        "shared": shared,
        "context_weight": context_loading,
        "context_features": context_features,
        "context": context,
        "group": group,
        "author": author,
        "session": session,
        "author_subspace": author_loading,
        "group_subspace": group_loading,
        "session_subspace": session_loading,
    }


def _opportunity_trials(
    *,
    seed: int,
    world: str,
    spec: AuthorRoutingSpec,
) -> np.ndarray:
    shape = (
        spec.authors,
        spec.sessions,
        spec.total_contexts,
        spec.cells,
    )
    trials = np.full(shape, spec.repeats_per_cell, dtype=np.int16)
    if world == "opportunity_only":
        rng = np.random.default_rng(seed + 1_901)
        for author in range(spec.authors):
            order = rng.permutation(spec.cells)
            pattern = np.ones(spec.cells, dtype=np.int16)
            pattern[order[: spec.cells // 2]] = 3
            trials[author] = pattern[None, None, :]
    elif world == "opportunity_nonoverlap":
        for author in range(spec.authors):
            missing = (
                np.arange(spec.branches) * spec.branches
                + author % spec.branches
            )
            trials[author, :, :, missing] = 0
    return trials


def _sample_multinomial_counts(
    rng: np.random.Generator,
    probability: np.ndarray,
    trials: np.ndarray,
) -> np.ndarray:
    counts = np.zeros(probability.shape, dtype=np.int16)
    cumulative = np.cumsum(probability, axis=-1)
    eye = np.eye(probability.shape[-1], dtype=np.int16)
    for draw in range(int(trials.max(initial=0))):
        uniform = rng.random(trials.shape)
        outcome = np.sum(
            uniform[..., None] > cumulative,
            axis=-1,
        )
        active = trials > draw
        counts += eye[outcome] * active[..., None]
    return counts


def simulate_author_routing_world(
    *,
    seed: int,
    world: str,
    spec: AuthorRoutingSpec,
) -> dict[str, Any]:
    """Generate one registered categorical routing population."""
    supported = {
        "stable_author",
        "context_only",
        "group_only",
        "session_unstable",
        "opportunity_only",
        "cue_leakage",
        "random",
        "opportunity_nonoverlap",
    }
    if world not in supported:
        raise ValueError(f"unsupported author-routing world: {world}")
    rng = np.random.default_rng(seed)
    context_sets = registered_contexts(seed=seed + 101, spec=spec)
    labels = _balanced_groups(rng, spec)
    bank = _component_bank(
        seed=seed + 307,
        spec=spec,
        contexts=context_sets["all"],
        labels=labels,
    )

    shared = bank["shared"].copy()
    context = bank["context"].copy()
    group = np.zeros_like(bank["group"])
    author = np.zeros_like(bank["author"])
    session = np.zeros_like(bank["session"])
    if world == "stable_author":
        group = bank["group"]
        author = bank["author"]
        session = bank["session"]
    elif world == "context_only":
        session = 0.5 * bank["session"]
    elif world == "group_only":
        group = bank["group"]
        session = 0.5 * bank["session"]
    elif world == "session_unstable":
        group = bank["group"]
        session = _scale_rms(bank["session"], spec.author_rms)
    elif world == "cue_leakage":
        cue = np.arange(spec.cells) % spec.branches
        cue_template = _center_outcomes(np.eye(spec.branches)[cue])
        shared = _scale_rms(
            shared + cue_template,
            spec.shared_rms + 0.35,
        )
    elif world == "random":
        shared = np.zeros_like(shared)
        context = np.zeros_like(context)
    elif world in {"opportunity_only", "opportunity_nonoverlap"}:
        pass

    eta = (
        shared[None, None, None, :, :]
        + context[None, None, :, :, :]
        + group[labels, None, None, :, :]
        + author[:, None, None, :, :]
        + session[:, :, None, :, :]
    )
    probability = softmax(eta, axis=-1)
    trials = _opportunity_trials(seed=seed, world=world, spec=spec)
    counts = _sample_multinomial_counts(
        np.random.default_rng(seed + 509),
        probability,
        trials,
    )
    pooled = probability[trials > 0].reshape(-1, spec.branches).mean(axis=0)
    entropy = -float(np.sum(pooled * np.log2(np.clip(pooled, 1e-12, None))))
    entropy /= np.log2(spec.branches)
    return {
        "world": world,
        "contexts": context_sets,
        "labels": labels,
        "counts": counts,
        "trials": trials,
        "probability": probability,
        "components": {
            "shared": shared,
            "context_weight": bank["context_weight"],
            "context_features": bank["context_features"],
            "context": context,
            "group": group,
            "author": author,
            "session": session,
            "author_subspace": bank["author_subspace"],
            "group_subspace": bank["group_subspace"],
            "session_subspace": bank["session_subspace"],
        },
        "design": {
            "mixture_components": spec.groups,
            "author_rank": spec.author_rank,
            "events_per_context_session": spec.events_per_context_session,
        },
        "audit": {
            "minimum_pooled_marginal_probability": float(pooled.min()),
            "maximum_pooled_marginal_probability": float(pooled.max()),
            "normalized_pooled_entropy": entropy,
        },
    }


def fit_reference_router(
    sample: dict[str, Any],
    context_indices: Iterable[int],
    *,
    ridge: float = 1e-6,
) -> dict[str, np.ndarray]:
    """Fit the anonymous pooled context router in ILR coordinates."""
    indices = np.asarray(tuple(context_indices), dtype=int)
    counts = sample["counts"][:, :, indices].sum(axis=(0, 1))
    trials = sample["trials"][:, :, indices].sum(axis=(0, 1))
    probability = (counts + 0.5) / (
        trials[..., None] + 0.5 * counts.shape[-1]
    )
    basis = ilr_basis(counts.shape[-1])
    response = ilr(probability, basis)
    all_features = context_feature_map(sample["contexts"]["all"])
    feature_center = all_features[
        : sample["contexts"]["discovery"].shape[0]
    ].mean(axis=0)
    features = all_features[indices] - feature_center
    design = np.column_stack([np.ones(len(indices)), features])
    penalty = ridge * np.eye(design.shape[1])
    penalty[0, 0] = 0.0
    right = np.einsum("np,nij->pij", design, response)
    beta = np.linalg.solve(
        design.T @ design + penalty,
        right.reshape(design.shape[1], -1),
    ).reshape(right.shape)
    return {
        "beta": beta,
        "basis": basis,
        "feature_center": feature_center,
    }


def predict_reference_router(
    fit: dict[str, np.ndarray],
    contexts: np.ndarray,
) -> np.ndarray:
    """Predict anonymous reference probabilities for context coordinates."""
    values = context_feature_map(np.asarray(contexts, dtype=float))
    values -= fit["feature_center"]
    design = np.column_stack([np.ones(len(values)), values])
    coordinates = np.einsum("nc,cij->nij", design, fit["beta"])
    return ilr_inverse(coordinates, fit["basis"])


def _selected_sessions(
    sessions: int | Iterable[int],
) -> np.ndarray:
    if isinstance(sessions, (int, np.integer)):
        return np.asarray([int(sessions)], dtype=int)
    return np.asarray(tuple(sessions), dtype=int)


def estimate_packet_profile(
    sample: dict[str, Any],
    context_indices: Iterable[int],
    *,
    sessions: int | Iterable[int] = (0, 1),
) -> dict[str, Any]:
    """Estimate equal-context, equal-cell anonymous packet profiles."""
    contexts = np.asarray(tuple(context_indices), dtype=int)
    halves = _selected_sessions(sessions)
    counts = sample["counts"][:, halves][:, :, contexts]
    trials = sample["trials"][:, halves][:, :, contexts]
    coverage = trials.sum(axis=(1, 2))
    if np.any(coverage == 0):
        return {
            "status": "REFUSE_NONOVERLAP",
            "refused": True,
            "minimum_cell_trials": int(coverage.min()),
        }
    proportions = counts / trials[..., None]
    probability = proportions.mean(axis=(1, 2))
    observations = trials.shape[1] * trials.shape[2]
    effective_trials = observations / np.mean(
        1.0 / trials.astype(float),
        axis=(1, 2),
    )
    probability = (
        probability * effective_trials[..., None] + 0.5
    ) / (effective_trials[..., None] + 0.5 * probability.shape[-1])
    probability /= probability.sum(axis=-1, keepdims=True)
    reference = probability.mean(axis=0)
    basis = ilr_basis(probability.shape[-1])
    profile = ilr(probability, basis) - ilr(reference, basis)[None, :, :]
    return {
        "status": "PROFILE_READY",
        "refused": False,
        "profile": profile.reshape(len(profile), -1),
        "cell_profile": profile,
        "probability": probability,
        "reference_probability": reference,
        "effective_cell_trials": effective_trials,
        "minimum_cell_trials": int(coverage.min()),
    }


def true_q_profile(
    sample: dict[str, Any],
    context_indices: Iterable[int],
    *,
    sessions: int | Iterable[int] = (0, 1),
) -> dict[str, np.ndarray]:
    """Calculate the scorer-only planted Q-standardized operator."""
    contexts = np.asarray(tuple(context_indices), dtype=int)
    halves = _selected_sessions(sessions)
    probability = sample["probability"][:, halves][:, :, contexts].mean(
        axis=(1, 2)
    )
    reference = probability.mean(axis=0)
    basis = ilr_basis(probability.shape[-1])
    profile = ilr(probability, basis) - ilr(reference, basis)[None, :, :]
    return {
        "profile": profile.reshape(len(profile), -1),
        "cell_profile": profile,
        "probability": probability,
        "reference_probability": reference,
    }


def profile_standard_error(
    sample: dict[str, Any],
    context_indices: Iterable[int],
    *,
    sessions: int | Iterable[int] = (0, 1),
) -> np.ndarray:
    """Delta-method standard errors for one equal-context ILR profile."""
    estimate = estimate_packet_profile(
        sample,
        context_indices,
        sessions=sessions,
    )
    if estimate["refused"]:
        return np.full(
            (sample["counts"].shape[0], sample["counts"].shape[3] * 3),
            np.nan,
        )
    contexts = np.asarray(tuple(context_indices), dtype=int)
    halves = _selected_sessions(sessions)
    trials = sample["trials"][:, halves][:, :, contexts].astype(float)
    probability = estimate["probability"]
    basis = ilr_basis(probability.shape[-1])
    observations = trials.shape[1] * trials.shape[2]
    inverse_n = np.mean(1.0 / trials, axis=(1, 2)) / observations
    variance = np.empty(
        (
            len(probability),
            probability.shape[1],
            probability.shape[2] - 1,
        ),
        dtype=float,
    )
    for author in range(len(probability)):
        for cell in range(probability.shape[1]):
            p = probability[author, cell]
            covariance = (
                np.diag(p) - np.outer(p, p)
            ) * inverse_n[author, cell]
            jacobian = basis / np.clip(p[:, None], 1e-5, None)
            variance[author, cell] = np.diag(
                jacobian.T @ covariance @ jacobian
            )
    reference_variance = variance.mean(axis=0) / len(probability)
    variance += reference_variance[None, :, :]
    return np.sqrt(np.clip(variance, 0.0, None)).reshape(len(probability), -1)


def fit_profile_denoiser(
    left: np.ndarray,
    right: np.ndarray,
    *,
    rank: int,
    groups: int,
    seed: int,
) -> dict[str, Any]:
    """Learn a hidden-group center and PSD cross-session author subspace."""
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    if x.shape != y.shape:
        raise ValueError("profile halves must have identical shape")
    if rank < 0 or rank > x.shape[1]:
        raise ValueError("invalid denoiser rank")
    mean_profile = 0.5 * (x + y)
    mixture = GaussianMixture(
        n_components=groups,
        covariance_type="diag",
        reg_covar=1e-3,
        n_init=5,
        max_iter=500,
        random_state=seed,
    ).fit(mean_profile)
    assignment = mixture.predict(mean_profile)
    centers = np.vstack([
        mean_profile[assignment == group].mean(axis=0)
        if np.any(assignment == group)
        else mixture.means_[group]
        for group in range(groups)
    ])
    residual_left = x - centers[assignment]
    residual_right = y - centers[assignment]
    covariance = (
        residual_left.T @ residual_right
        + residual_right.T @ residual_left
    ) / (2.0 * max(len(x) - 1, 1))
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    basis = eigenvectors[:, :rank]
    projector = basis @ basis.T
    positive = eigenvalues[eigenvalues > 1e-10]
    condition = (
        float(positive[0] / positive[min(rank, len(positive)) - 1])
        if rank > 0 and len(positive) >= rank
        else float("inf")
    )
    return {
        "mixture": mixture,
        "centers": centers,
        "assignment": assignment,
        "basis": basis,
        "projector": projector,
        "eigenvalues": eigenvalues,
        "condition_number": condition,
        "rank": int(rank),
    }


def apply_profile_denoiser(
    profile: np.ndarray,
    denoiser: dict[str, Any],
) -> np.ndarray:
    """Project a packet profile using a discovery-only hidden basis."""
    values = np.asarray(profile, dtype=float)
    assignment = denoiser["mixture"].predict(values)
    centers = denoiser["centers"][assignment]
    return centers + (values - centers) @ denoiser["projector"]


def rank_lambda_cv_losses(
    sample: dict[str, Any],
    ranks: Iterable[int],
    candidates: Iterable[float],
    *,
    seed: int,
    folds: int = 3,
) -> dict[tuple[int, float], float]:
    """Choose hidden rank and shrinkage by discovery-context log loss."""
    discovery = np.arange(
        sample["contexts"]["discovery"].shape[0],
        dtype=int,
    )
    fold_ids = np.arange(len(discovery)) % folds
    losses: dict[tuple[int, float], list[float]] = {
        (int(rank), float(candidate)): []
        for rank in ranks
        for candidate in candidates
    }
    for fold in range(folds):
        train = discovery[fold_ids != fold]
        valid = discovery[fold_ids == fold]
        fit = fit_reference_router(sample, train)
        combined = estimate_packet_profile(sample, train)
        halves = (
            estimate_packet_profile(sample, train, sessions=0),
            estimate_packet_profile(sample, train, sessions=1),
        )
        if combined["refused"] or any(row["refused"] for row in halves):
            continue
        effective_trials = float(combined["minimum_cell_trials"])
        for rank in {key[0] for key in losses}:
            denoiser = fit_profile_denoiser(
                halves[0]["profile"],
                halves[1]["profile"],
                rank=rank,
                groups=int(sample["design"]["mixture_components"]),
                seed=seed + 101 * fold + rank,
            )
            profile = apply_profile_denoiser(
                combined["profile"],
                denoiser,
            )
            for candidate in {key[1] for key in losses}:
                shrinkage = effective_trials / (
                    effective_trials + candidate
                )
                metric = heldout_prediction_metrics(
                    sample,
                    reference_fit=fit,
                    profile=profile,
                    context_indices=valid,
                    shrinkage=shrinkage,
                )
                losses[(rank, candidate)].append(
                    metric["personalized_log_loss"]
                )
    return {
        key: float(np.mean(values)) if values else float("inf")
        for key, values in losses.items()
    }


def _multiclass_log_loss(
    counts: np.ndarray,
    probability: np.ndarray,
) -> float:
    total = float(counts.sum())
    if total <= 0:
        return float("nan")
    return -float(
        np.sum(counts * np.log(np.clip(probability, 1e-12, 1.0))) / total
    )


def predict_with_profile(
    reference_fit: dict[str, np.ndarray],
    profile: np.ndarray,
    contexts: np.ndarray,
    *,
    shrinkage: float,
) -> np.ndarray:
    """Apply an anonymous packet profile to an unseen context router."""
    reference = predict_reference_router(reference_fit, contexts)
    base = ilr(reference, reference_fit["basis"])
    cell_profile = np.asarray(profile).reshape(
        len(profile),
        base.shape[1],
        base.shape[2],
    )
    return ilr_inverse(
        base[None, None, :, :, :]
        + shrinkage * cell_profile[:, None, None, :, :],
        reference_fit["basis"],
    )


def heldout_prediction_metrics(
    sample: dict[str, Any],
    *,
    reference_fit: dict[str, np.ndarray],
    profile: np.ndarray,
    context_indices: Iterable[int],
    shrinkage: float,
) -> dict[str, float]:
    """Score personalized and anonymous routers on held-out counts."""
    indices = np.asarray(tuple(context_indices), dtype=int)
    contexts = sample["contexts"]["all"][indices]
    personalized = predict_with_profile(
        reference_fit,
        profile,
        contexts,
        shrinkage=shrinkage,
    )
    personalized = np.broadcast_to(
        personalized,
        (
            personalized.shape[0],
            sample["trials"].shape[1],
            personalized.shape[2],
            personalized.shape[3],
            personalized.shape[4],
        ),
    )
    baseline = predict_reference_router(reference_fit, contexts)
    baseline = np.broadcast_to(
        baseline[None, None],
        personalized.shape,
    )
    counts = sample["counts"][:, :, indices]
    trials = sample["trials"][:, :, indices]
    personalized_loss = _multiclass_log_loss(counts, personalized)
    baseline_loss = _multiclass_log_loss(counts, baseline)
    confidence = personalized.max(axis=-1)
    predicted = personalized.argmax(axis=-1)
    correctness = np.take_along_axis(
        counts,
        predicted[..., None],
        axis=-1,
    )[..., 0]
    bins = np.linspace(0.0, 1.0, 11)
    ece = 0.0
    total = float(trials.sum())
    for lower, upper in zip(bins[:-1], bins[1:], strict=True):
        mask = (confidence >= lower) & (
            (confidence < upper) if upper < 1.0 else (confidence <= upper)
        )
        weight = float(trials[mask].sum())
        if weight <= 0:
            continue
        observed = float(correctness[mask].sum() / weight)
        expected = float(
            np.sum(confidence[mask] * trials[mask]) / weight
        )
        ece += weight / total * abs(observed - expected)
    return {
        "personalized_log_loss": personalized_loss,
        "baseline_log_loss": baseline_loss,
        "log_loss_gain": baseline_loss - personalized_loss,
        "ece": float(ece),
    }


def lambda_cv_losses(
    sample: dict[str, Any],
    candidates: Iterable[float],
    *,
    folds: int = 3,
) -> dict[float, float]:
    """Select profile shrinkage using discovery-context held-out log loss."""
    discovery = np.arange(
        sample["contexts"]["discovery"].shape[0],
        dtype=int,
    )
    fold_ids = np.arange(len(discovery)) % folds
    losses: dict[float, list[float]] = {
        float(candidate): [] for candidate in candidates
    }
    for fold in range(folds):
        train = discovery[fold_ids != fold]
        valid = discovery[fold_ids == fold]
        fit = fit_reference_router(sample, train)
        estimate = estimate_packet_profile(sample, train)
        if estimate["refused"]:
            continue
        effective_trials = float(estimate["minimum_cell_trials"])
        for candidate in losses:
            shrinkage = effective_trials / (effective_trials + candidate)
            metric = heldout_prediction_metrics(
                sample,
                reference_fit=fit,
                profile=estimate["profile"],
                context_indices=valid,
                shrinkage=shrinkage,
            )
            losses[candidate].append(metric["personalized_log_loss"])
    return {
        candidate: float(np.mean(values)) if values else float("inf")
        for candidate, values in losses.items()
    }


def _row_normalize(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    matrix -= matrix.mean(axis=1, keepdims=True)
    return matrix / np.maximum(
        np.linalg.norm(matrix, axis=1, keepdims=True),
        1e-12,
    )


def _pair_auc(
    similarity: np.ndarray,
    labels: np.ndarray,
) -> dict[str, float]:
    authors = len(similarity)
    identity = np.eye(authors, dtype=bool)
    same_group = labels[:, None] == labels[None, :]
    positive = similarity[identity]

    def auc(negative: np.ndarray) -> float:
        target = np.concatenate([
            np.ones(len(positive), dtype=int),
            np.zeros(len(negative), dtype=int),
        ])
        score = np.concatenate([positive, negative])
        return float(roc_auc_score(target, score))

    return {
        "same_author_auc": auc(similarity[~identity]),
        "within_group_auc": auc(similarity[same_group & ~identity]),
    }


def pairing_metrics(
    left: np.ndarray,
    right: np.ndarray,
    labels: np.ndarray,
) -> dict[str, float]:
    """Evaluate anonymous profiles after opening match and group truth."""
    similarity = _row_normalize(left) @ _row_normalize(right).T
    result = _pair_auc(similarity, labels)
    result["top1"] = float(np.mean(similarity.argmax(axis=1) == np.arange(len(left))))
    within_correct = 0
    for author in range(len(left)):
        candidates = np.flatnonzero(labels == labels[author])
        selected = candidates[np.argmax(similarity[author, candidates])]
        within_correct += int(selected == author)
    result["within_group_top1"] = within_correct / len(left)
    return result


def multivariate_reliability(left: np.ndarray, right: np.ndarray) -> float:
    """Return the signed trace cross-covariance reliability coefficient."""
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    x -= x.mean(axis=0, keepdims=True)
    y -= y.mean(axis=0, keepdims=True)
    numerator = 2.0 * float(np.sum(x * y) / max(len(x) - 1, 1))
    denominator = float(
        (np.sum(x * x) + np.sum(y * y)) / max(len(x) - 1, 1)
    )
    return numerator / max(denominator, 1e-12)


def _within_group_center(
    values: np.ndarray,
    labels: np.ndarray,
) -> np.ndarray:
    result = np.asarray(values, dtype=float).copy()
    for group in np.unique(labels):
        mask = labels == group
        result[mask] -= result[mask].mean(axis=0, keepdims=True)
    return result


def _flat_correlation(left: np.ndarray, right: np.ndarray) -> float:
    x = np.asarray(left, dtype=float).ravel()
    y = np.asarray(right, dtype=float).ravel()
    if np.std(x) <= 1e-12 or np.std(y) <= 1e-12:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _variance_shares(
    sample: dict[str, Any],
    reference_fit: dict[str, np.ndarray],
    session_profiles: tuple[np.ndarray, np.ndarray],
    session_standard_errors: tuple[np.ndarray, np.ndarray],
) -> dict[str, Any]:
    basis = reference_fit["basis"]
    components = sample["components"]
    labels = sample["labels"]
    true_parts = {
        "shared": np.asarray(components["shared"]) @ basis,
        "context": np.asarray(components["context"]) @ basis,
        "group": np.asarray(components["group"]) @ basis,
        "author": np.asarray(components["author"]) @ basis,
        "session": np.asarray(components["session"]) @ basis,
    }
    true_energy = {
        key: float(np.mean(value**2))
        for key, value in true_parts.items()
    }
    true_total = max(sum(true_energy.values()), 1e-12)
    true_share = {
        key: value / true_total for key, value in true_energy.items()
    }

    beta = np.asarray(reference_fit["beta"])
    context = context_feature_map(
        sample["contexts"]["all"][: sample["probability"].shape[2]]
    )
    context -= reference_fit["feature_center"]
    reference_ilr = np.einsum(
        "nc,cij->nij",
        np.column_stack([np.ones(len(context)), context]),
        beta,
    )
    intercept = beta[0]
    estimated_energy: dict[str, float] = {
        "shared": float(np.mean(intercept**2)),
        "context": float(
            np.mean((reference_ilr - intercept[None]) ** 2)
        ),
    }
    left, right = session_profiles
    mean_profile = 0.5 * (left + right)
    difference = 0.5 * (left - right)
    grand = mean_profile.mean(axis=0, keepdims=True)
    group_center = np.zeros_like(mean_profile)
    for group in np.unique(labels):
        mask = labels == group
        group_center[mask] = mean_profile[mask].mean(axis=0, keepdims=True)
    group_residual = mean_profile - group_center
    se_left, se_right = session_standard_errors
    noise_mean = float(np.mean((se_left**2 + se_right**2) / 4.0))
    estimated_energy["group"] = float(np.mean((group_center - grand) ** 2))
    estimated_energy["author"] = float(
        np.mean(group_residual**2) - noise_mean
    )
    estimated_energy["session"] = float(
        np.mean(difference**2) - noise_mean
    )
    estimated_total = sum(estimated_energy.values())
    estimated_share = {
        key: value / max(estimated_total, 1e-12)
        for key, value in estimated_energy.items()
    }
    errors = {
        key: abs(estimated_share[key] - true_share[key])
        for key in true_share
    }
    return {
        "true": true_share,
        "estimated": estimated_share,
        "absolute_error": errors,
        "maximum_absolute_error": max(errors.values()),
    }


def analyze_author_routing_world(
    sample: dict[str, Any],
    *,
    selected_lambda: float,
    selected_rank: int | None = None,
    denoiser_seed: int = 0,
    claim_thresholds: dict[str, float],
) -> dict[str, Any]:
    """Fit and score one anonymous V3.7A routing population."""
    spec_contexts = sample["contexts"]
    discovery = np.arange(len(spec_contexts["discovery"]), dtype=int)
    confirmation = np.arange(
        len(spec_contexts["discovery"]),
        len(spec_contexts["discovery"]) + len(spec_contexts["confirmation"]),
        dtype=int,
    )
    regular = np.concatenate([discovery, confirmation])
    disc = estimate_packet_profile(sample, discovery)
    conf = estimate_packet_profile(sample, confirmation)
    if disc["refused"] or conf["refused"]:
        return {
            "status": "REFUSE_NONOVERLAP",
            "numeric_output": False,
            "author_claim": False,
            "minimum_cell_trials": min(
                disc["minimum_cell_trials"],
                conf["minimum_cell_trials"],
            ),
        }
    fit = fit_reference_router(sample, discovery)
    discovery_sessions = (
        estimate_packet_profile(sample, discovery, sessions=0),
        estimate_packet_profile(sample, discovery, sessions=1),
    )
    dimension = disc["profile"].shape[1]
    rank = dimension if selected_rank is None else int(selected_rank)
    denoiser = fit_profile_denoiser(
        discovery_sessions[0]["profile"],
        discovery_sessions[1]["profile"],
        rank=rank,
        groups=int(sample["design"]["mixture_components"]),
        seed=denoiser_seed,
    )
    disc_profile = apply_profile_denoiser(disc["profile"], denoiser)
    conf_profile = apply_profile_denoiser(conf["profile"], denoiser)
    effective_trials = float(disc["minimum_cell_trials"])
    shrinkage = effective_trials / (effective_trials + selected_lambda)
    prediction = heldout_prediction_metrics(
        sample,
        reference_fit=fit,
        profile=disc_profile,
        context_indices=confirmation,
        shrinkage=shrinkage,
    )
    labels = np.asarray(sample["labels"])
    pairing = pairing_metrics(disc_profile, conf_profile, labels)
    disc_within = _within_group_center(disc_profile, labels)
    conf_within = _within_group_center(conf_profile, labels)
    unseen_reliability = multivariate_reliability(
        disc_within,
        conf_within,
    )
    # A learned subspace must be evaluated on contexts not used to learn it.
    # The full-rank identity branch has no learned projection and can use the
    # complete registered context panel for its information-limit diagnostic.
    session_contexts = regular if rank == dimension else confirmation
    session_estimates = (
        estimate_packet_profile(sample, session_contexts, sessions=0),
        estimate_packet_profile(sample, session_contexts, sessions=1),
    )
    session_profiles = (
        apply_profile_denoiser(session_estimates[0]["profile"], denoiser),
        apply_profile_denoiser(session_estimates[1]["profile"], denoiser),
    )
    split_reliability = multivariate_reliability(
        _within_group_center(session_profiles[0], labels),
        _within_group_center(session_profiles[1], labels),
    )
    truth = true_q_profile(sample, regular)
    estimated_centered = _within_group_center(disc_profile, labels)
    truth_centered = _within_group_center(truth["profile"], labels)
    truth_correlation = _flat_correlation(
        estimated_centered,
        truth_centered,
    )
    q_contexts = spec_contexts["all"][regular]
    estimated_probability = predict_with_profile(
        fit,
        disc_profile,
        q_contexts,
        shrinkage=1.0,
    ).mean(axis=(1, 2))
    probability_rmse = float(
        np.sqrt(np.mean((estimated_probability - truth["probability"]) ** 2))
    )
    se = profile_standard_error(sample, discovery)
    truth_discovery = true_q_profile(sample, discovery)["profile"]
    projected_se = np.sqrt(
        np.maximum(
            (se**2) @ (denoiser["projector"] ** 2),
            0.0,
        )
    )
    # The projection residual is approximation uncertainty, not disposable
    # noise. Keeping its full magnitude prevents low-rank confidence intervals
    # from pretending that omitted coordinates were observed precisely.
    operator_se = np.sqrt(
        projected_se**2 + (disc["profile"] - disc_profile) ** 2
    )
    coverage = float(
        np.mean(
            (truth_discovery >= disc_profile - 1.96 * operator_se)
            & (truth_discovery <= disc_profile + 1.96 * operator_se)
        )
    )
    session_se = tuple(
        np.sqrt(
            np.maximum(
                profile_standard_error(
                    sample,
                    session_contexts,
                    sessions=session,
                )
                ** 2
                @ (denoiser["projector"] ** 2),
                0.0,
            )
        )
        for session in (0, 1)
    )
    variance = _variance_shares(
        sample,
        fit,
        (
            session_profiles[0],
            session_profiles[1],
        ),
        session_se,
    )
    true_basis = np.asarray(sample["components"]["author_subspace"])
    true_projector = true_basis @ true_basis.T
    true_rank = true_basis.shape[1]
    subspace_score = 1.0 - float(
        np.linalg.norm(
            denoiser["projector"] - true_projector,
            ord="fro",
        )
        ** 2
        / (2.0 * true_rank)
    )
    audit = sample["audit"]
    probability_audit_pass = bool(
        audit["minimum_pooled_marginal_probability"]
        >= 0.05 - 1e-9
        and audit["maximum_pooled_marginal_probability"]
        <= 0.75 + 1e-9
        and audit["normalized_pooled_entropy"] >= 0.55
    )
    author_claim = bool(
        pairing["within_group_auc"]
        >= float(claim_thresholds["minimum_within_group_auc"])
        and min(unseen_reliability, split_reliability)
        >= float(claim_thresholds["minimum_multivariate_reliability"])
        and prediction["log_loss_gain"]
        >= float(claim_thresholds["minimum_log_loss_gain"])
    )
    return {
        "status": "AUTHOR_ROUTING_OPERATOR_EVALUATED",
        "numeric_output": True,
        "selected_lambda": float(selected_lambda),
        "selected_rank": rank,
        "shrinkage": float(shrinkage),
        "subspace_score": subspace_score,
        "operator_hessian_condition_number": float(
            denoiser["condition_number"]
        ),
        "median_operator_ci_width": float(
            np.median(2.0 * 1.96 * operator_se)
        ),
        "author_claim": author_claim,
        "truth_correlation": truth_correlation,
        "probability_rmse": probability_rmse,
        "split_session_reliability": split_reliability,
        "unseen_context_reliability": unseen_reliability,
        "operator_interval_coverage": coverage,
        "maximum_variance_share_error": variance["maximum_absolute_error"],
        "variance_shares": variance,
        "probability_audit_pass": probability_audit_pass,
        **pairing,
        **prediction,
        **audit,
    }
