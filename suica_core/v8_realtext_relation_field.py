"""Prospective real-text support and relation-field estimators for SUICA V8.

The module deliberately avoids questionnaire labels and named psychological
features. Raw texts are mapped to a frozen signed-hash event space. Two
non-equivalent measurement families are then built:

``M``
    Order-free marginal geometry of the event path.
``K``
    Order-sensitive transition geometry after subtracting the conditional
    random-order expectation of the same event multiset.

Author-disjoint D0/D1/D2 panels identify replicated supports, test their
stability, and estimate a cross-family relation field. Cross-corpus transport
freezes the source map. No function in this module licenses a psychological
construct.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from itertools import combinations
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment, linprog, minimize_scalar


FAMILY_NAMES = ("M", "K")
SPLIT_NAMES = ("D0", "D1", "D2")


@dataclass(frozen=True)
class RealTextRelationSpec:
    """Frozen numerical choices for the prospective real-text experiment."""

    hash_dimensions: int = 32
    random_directions: int = 8
    transition_null_draws: int = 16
    maximum_rank: int = 6
    minimum_rank: int = 2
    support_permutations: int = 99
    relation_permutations: int = 199
    support_subsamples: int = 39
    minimum_split_authors: int = 24
    minimum_context_authors: int = 12
    alignment_floor: float = 0.35
    relation_agreement_floor: float = 0.60
    alias_residual_rank_floor: int = 1
    ridge: float = 1e-5
    seed: int = 20260805
    gw_authors: int = 48
    gw_iterations: int = 24

    def __post_init__(self) -> None:
        if self.hash_dimensions < 8:
            raise ValueError("hash_dimensions must be at least 8.")
        if self.random_directions < 2:
            raise ValueError("random_directions must be at least 2.")
        if self.transition_null_draws < 0:
            raise ValueError("transition_null_draws cannot be negative.")
        if self.minimum_rank < 1 or self.maximum_rank < self.minimum_rank:
            raise ValueError("Invalid support rank range.")
        if self.support_permutations < 19 or self.relation_permutations < 19:
            raise ValueError("Permutation budgets must be at least 19.")
        if self.minimum_split_authors < 8:
            raise ValueError("At least eight authors per split are required.")
        if self.minimum_context_authors < 4:
            raise ValueError("At least four authors per resolved context are required.")


@dataclass
class CorpusFeaturePanel:
    """One corpus after fixed event-to-family transformation."""

    metadata: pd.DataFrame
    raw: dict[str, np.ndarray]
    context_role: str
    replicate_type: str

    def __post_init__(self) -> None:
        required = {"author_id", "context", "split"}
        if not required.issubset(self.metadata.columns):
            raise ValueError(f"metadata must contain {sorted(required)}")
        rows = len(self.metadata)
        for family in FAMILY_NAMES:
            values = np.asarray(self.raw[family], dtype=float)
            if values.ndim != 3 or values.shape[:2] != (rows, 2):
                raise ValueError(
                    f"{family} must have shape (authors, 2, dimensions), "
                    f"got {values.shape}"
                )
            if not np.isfinite(values).all():
                raise ValueError(f"{family} contains non-finite values.")


@dataclass
class FrozenFamilySupport:
    """D0-frozen scaler, replicated support, and whitening map."""

    family: str
    center: np.ndarray
    scale: np.ndarray
    basis: np.ndarray
    eigenvalues: np.ndarray
    null_eigenvalues: np.ndarray
    rank: int
    whitener: np.ndarray
    density: np.ndarray
    soft_filter: np.ndarray
    effective_rank: float
    retained_energy_floor: float
    alignment_floor: float
    eigengap: float
    status: str


@dataclass
class FrozenCorpusCalibration:
    """All D0-frozen objects for one corpus."""

    corpus: str
    supports: dict[str, FrozenFamilySupport]
    relation_null_q99: float
    between_null_q99: float
    alias: dict[str, Any]
    spec: RealTextRelationSpec


def _digest(value: str, *, salt: str) -> bytes:
    return hashlib.blake2b(
        f"{salt}::{value}".encode("utf-8"),
        digest_size=16,
    ).digest()


def stable_bucket(value: str, *, salt: str, modulus: int) -> int:
    """Return a deterministic integer bucket."""
    return int.from_bytes(_digest(str(value), salt=salt)[:8], "big") % int(modulus)


def assign_d0_d1_d2(
    author_ids: Iterable[str],
    *,
    salt: str,
) -> dict[str, str]:
    """Assign authors to deterministic 40/30/30 calibration panels."""
    result: dict[str, str] = {}
    for author in map(str, author_ids):
        bucket = stable_bucket(author, salt=salt, modulus=10_000)
        result[author] = "D0" if bucket < 4_000 else ("D1" if bucket < 7_000 else "D2")
    return result


def _signed_hash(
    items: Iterable[str],
    *,
    dimensions: int,
    salt: str,
) -> np.ndarray:
    vector = np.zeros(int(dimensions), dtype=float)
    for item in items:
        digest = _digest(str(item), salt=salt)
        bucket = int.from_bytes(digest[:8], "big") % int(dimensions)
        vector[bucket] += 1.0 if digest[8] & 1 else -1.0
    norm = float(np.linalg.norm(vector))
    return vector / norm if norm > 1e-12 else vector


def frozen_event_vector(text: str, *, dimensions: int = 32) -> np.ndarray:
    """Map raw text to one fixed language-agnostic signed-hash event vector."""
    value = str(text or "")
    words = value.casefold().split()
    word_grams = list(words)
    word_grams.extend(
        f"{left}\x1f{right}"
        for left, right in zip(words[:-1], words[1:], strict=False)
    )
    compact = " ".join(words)
    char_grams = (
        compact[index : index + size]
        for size in (3, 4, 5)
        for index in range(max(0, len(compact) - size + 1))
    )
    word = _signed_hash(word_grams, dimensions=dimensions, salt="v8rt-word")
    char = _signed_hash(char_grams, dimensions=dimensions, salt="v8rt-char")
    return np.concatenate([word, char])


def frozen_random_directions(
    *,
    event_dimensions: int,
    count: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate fixed marginal, transition, and current directions."""
    rng = np.random.default_rng(seed)

    def normalized(rows: int, columns: int) -> np.ndarray:
        values = rng.normal(size=(rows, columns))
        return values / np.maximum(
            np.linalg.norm(values, axis=1, keepdims=True),
            1e-12,
        )

    marginal = normalized(count, event_dimensions)
    transition = normalized(count, 2 * event_dimensions)
    current = normalized(2 * count, event_dimensions).reshape(
        count,
        2,
        event_dimensions,
    )
    return marginal, transition, current


def family_features(
    events: np.ndarray,
    *,
    marginal_directions: np.ndarray,
    transition_directions: np.ndarray,
    current_directions: np.ndarray,
) -> dict[str, np.ndarray]:
    """Extract order-free ``M`` and order-sensitive ``K`` path summaries."""
    values = np.asarray(events, dtype=float)
    if values.ndim != 2 or len(values) < 2:
        raise ValueError("Each replicate path requires at least two events.")

    mean = values.mean(axis=0)
    centered = values - mean
    variance = np.mean(centered**2, axis=0)
    marginal_phase = centered @ marginal_directions.T
    marginal_rff = np.concatenate(
        [
            np.mean(np.cos(marginal_phase), axis=0),
            np.mean(np.sin(marginal_phase), axis=0),
        ]
    )
    projections = values @ marginal_directions.T
    quantiles = np.quantile(projections, (0.25, 0.50, 0.75), axis=0).ravel()
    marginal = np.concatenate([mean, variance, marginal_rff, quantiles])

    previous = values[:-1]
    following = values[1:]
    delta = following - previous
    lag_product = np.mean(previous * following, axis=0)
    delta_variance = np.mean((delta - delta.mean(axis=0)) ** 2, axis=0)
    pairs = np.concatenate([previous, following], axis=1)
    transition_phase = pairs @ transition_directions.T
    transition_rff = np.concatenate(
        [
            np.mean(np.cos(transition_phase), axis=0),
            np.mean(np.sin(transition_phase), axis=0),
        ]
    )
    currents = []
    for first, second in current_directions:
        forward = np.tanh(previous @ first) * np.tanh(following @ second)
        reverse = np.tanh(previous @ second) * np.tanh(following @ first)
        currents.append(float(np.mean(forward - reverse)))
    transition = np.concatenate(
        [lag_product, delta_variance, transition_rff, np.asarray(currents)]
    )
    return {"M": marginal, "K": transition}


def build_feature_panel(
    event_rows: pd.DataFrame,
    *,
    corpus: str,
    context_role: str,
    replicate_type: str,
    spec: RealTextRelationSpec,
) -> CorpusFeaturePanel:
    """Convert ordered author-context text events into replicated family arrays.

    ``event_rows`` must contain one selected context per author. Replicates are
    source-disjoint alternating events, preserving broad path coverage without
    pretending that they are independent longitudinal occasions.
    """
    required = {"author_id", "context", "order", "text"}
    if not required.issubset(event_rows.columns):
        raise ValueError(f"event_rows must contain {sorted(required)}")
    directions = frozen_random_directions(
        event_dimensions=2 * spec.hash_dimensions,
        count=spec.random_directions,
        seed=spec.seed + 17,
    )
    split_map = assign_d0_d1_d2(
        event_rows["author_id"].astype(str).unique(),
        salt=f"v8rt-{corpus}-{spec.seed}",
    )
    metadata_rows: list[dict[str, Any]] = []
    family_rows: dict[str, list[np.ndarray]] = {name: [] for name in FAMILY_NAMES}
    grouped = event_rows.sort_values(
        ["author_id", "order"],
        kind="stable",
    ).groupby("author_id", observed=True, sort=False)
    for author, group in grouped:
        contexts = group["context"].astype(str).unique()
        if len(contexts) != 1:
            raise ValueError("Each author must have exactly one selected context.")
        vectors = np.vstack(
            [
                frozen_event_vector(text, dimensions=spec.hash_dimensions)
                for text in group["text"].astype(str)
            ]
        )
        replicate_features = []
        for offset in (0, 1):
            path = vectors[offset::2]
            if len(path) < 2:
                break
            observed = family_features(
                path,
                marginal_directions=directions[0],
                transition_directions=directions[1],
                current_directions=directions[2],
            )
            if spec.transition_null_draws:
                rng = np.random.default_rng(
                    spec.seed
                    + stable_bucket(
                        f"{corpus}-{author}-{offset}",
                        salt="v8rt-transition-null",
                        modulus=2**31 - 1,
                    )
                )
                null_k = np.mean(
                    [
                        family_features(
                            path[rng.permutation(len(path))],
                            marginal_directions=directions[0],
                            transition_directions=directions[1],
                            current_directions=directions[2],
                        )["K"]
                        for _ in range(spec.transition_null_draws)
                    ],
                    axis=0,
                )
                observed["K"] = observed["K"] - null_k
            replicate_features.append(observed)
        if len(replicate_features) != 2:
            continue
        metadata_rows.append(
            {
                "corpus": str(corpus),
                "author_id": str(author),
                "context": str(contexts[0]),
                "split": split_map[str(author)],
                "event_count": int(len(group)),
            }
        )
        for family in FAMILY_NAMES:
            family_rows[family].append(
                np.stack(
                    [
                        replicate_features[0][family],
                        replicate_features[1][family],
                    ]
                )
            )
    if not metadata_rows:
        raise ValueError(f"No eligible replicated paths for {corpus}.")
    return CorpusFeaturePanel(
        metadata=pd.DataFrame(metadata_rows),
        raw={
            family: np.stack(rows)
            for family, rows in family_rows.items()
        },
        context_role=context_role,
        replicate_type=replicate_type,
    )


def _center(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    return matrix - matrix.mean(axis=0, keepdims=True)


def _cross_covariance(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return _center(left).T @ _center(right) / max(1, len(left))


def replicated_covariance(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    """Return a symmetrized cross-replicate covariance."""
    return 0.5 * (
        _cross_covariance(first, second)
        + _cross_covariance(second, first).T
    )


def _eigendecomposition(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    values, vectors = np.linalg.eigh(0.5 * (matrix + matrix.T))
    order = np.argsort(values)[::-1]
    return values[order], vectors[:, order]


def _inverse_sqrt(matrix: np.ndarray, *, ridge: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(0.5 * (matrix + matrix.T))
    scale = max(float(np.max(values)), ridge)
    clipped = np.clip(values, ridge * scale, None)
    return vectors @ np.diag(1.0 / np.sqrt(clipped)) @ vectors.T


def _positive_density(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Return the trace-one positive part and participation effective rank."""
    values, vectors = _eigendecomposition(matrix)
    positive = np.clip(values, 0.0, None)
    total = float(np.sum(positive))
    if total <= 1e-12:
        return np.zeros_like(matrix), positive, 0.0
    probabilities = positive / total
    density = (vectors * probabilities) @ vectors.T
    effective_rank = float(1.0 / max(np.sum(probabilities**2), 1e-12))
    return density, positive, effective_rank


def _density_sqrt(density: np.ndarray) -> np.ndarray:
    values, vectors = np.linalg.eigh(0.5 * (density + density.T))
    return (vectors * np.sqrt(np.clip(values, 0.0, None))) @ vectors.T


def _density_fidelity(reference: np.ndarray, candidate: np.ndarray) -> float:
    root = _density_sqrt(reference)
    middle = root @ candidate @ root
    values = np.linalg.eigvalsh(0.5 * (middle + middle.T))
    return float(np.sum(np.sqrt(np.clip(values, 0.0, None))) ** 2)


def _hilbert_schmidt_alignment(
    reference: np.ndarray,
    candidate: np.ndarray,
) -> float:
    denominator = float(np.linalg.norm(reference) * np.linalg.norm(candidate))
    return (
        float(np.trace(reference @ candidate) / denominator)
        if denominator > 1e-12
        else 0.0
    )


def _haar_alignment_null(
    reference: np.ndarray,
    candidate: np.ndarray,
    *,
    draws: int,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    values = np.empty(int(draws), dtype=float)
    for draw in range(int(draws)):
        rotation, _ = np.linalg.qr(
            rng.normal(size=(candidate.shape[0], candidate.shape[0]))
        )
        rotated = rotation @ candidate @ rotation.T
        values[draw] = _hilbert_schmidt_alignment(reference, rotated)
    return values


def support_overlap(
    reference: np.ndarray,
    candidate: np.ndarray,
) -> dict[str, Any]:
    """Return gauge-invariant principal-angle support overlap."""
    singular = np.linalg.svd(reference.T @ candidate, compute_uv=False)
    squared = singular**2
    return {
        "overlap_rank": int(len(squared)),
        "omega": float(np.mean(squared)) if len(squared) else 0.0,
        "worst_alignment": float(np.min(squared)) if len(squared) else 0.0,
        "principal_cosine_squared": squared.tolist(),
    }


def _stratified_permutation(
    metadata: pd.DataFrame,
    *,
    rng: np.random.Generator,
) -> np.ndarray:
    order = np.arange(len(metadata))
    for _context, group in metadata.reset_index().groupby("context", observed=True):
        indices = group["index"].to_numpy(dtype=int)
        order[indices] = rng.permutation(indices)
    return order


def _fit_standardizer(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    pooled = values.reshape(-1, values.shape[-1])
    center = pooled.mean(axis=0)
    scale = pooled.std(axis=0)
    scale = np.where(scale < 1e-8, 1.0, scale)
    return center, scale


def _standardize(
    values: np.ndarray,
    center: np.ndarray,
    scale: np.ndarray,
) -> np.ndarray:
    return (np.asarray(values, dtype=float) - center[None, None, :]) / scale[
        None, None, :
    ]


def _select_support_rank(
    standardized: np.ndarray,
    metadata: pd.DataFrame,
    *,
    spec: RealTextRelationSpec,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, int]:
    observed, _ = _eigendecomposition(
        replicated_covariance(standardized[:, 0], standardized[:, 1])
    )
    rng = np.random.default_rng(seed)
    null = np.empty((spec.support_permutations, len(observed)), dtype=float)
    for draw in range(spec.support_permutations):
        order = _stratified_permutation(metadata, rng=rng)
        values, _ = _eigendecomposition(
            replicated_covariance(
                standardized[:, 0],
                standardized[order, 1],
            )
        )
        null[draw] = values
    threshold = np.quantile(null, 0.99, axis=0)
    rank = int(
        min(
            spec.maximum_rank,
            np.sum(
                (observed[: spec.maximum_rank] > threshold[: spec.maximum_rank])
                & (observed[: spec.maximum_rank] > 0)
            ),
        )
    )
    return observed, threshold, rank


def _calibrate_alignment_floor(
    standardized: np.ndarray,
    basis: np.ndarray,
    *,
    spec: RealTextRelationSpec,
    seed: int,
) -> float:
    if len(standardized) < 2 * max(8, basis.shape[1] + 2):
        return float(spec.alignment_floor)
    rng = np.random.default_rng(seed)
    alignments = []
    for _ in range(spec.support_subsamples):
        order = rng.permutation(len(standardized))
        half = order[: len(order) // 2]
        covariance = replicated_covariance(
            standardized[half, 0],
            standardized[half, 1],
        )
        values, vectors = _eigendecomposition(covariance)
        if values[basis.shape[1] - 1] <= 0:
            continue
        alignments.append(
            support_overlap(basis, vectors[:, : basis.shape[1]])[
                "worst_alignment"
            ]
        )
    if not alignments:
        return float(spec.alignment_floor)
    return float(max(spec.alignment_floor, np.quantile(alignments, 0.01)))


def _calibrate_soft_retained_floor(
    standardized: np.ndarray,
    *,
    spec: RealTextRelationSpec,
    seed: int,
) -> float:
    """Calibrate retained energy with disjoint D0 train/holdout supports."""
    rng = np.random.default_rng(seed)
    retained = []
    for _ in range(spec.support_subsamples):
        order = rng.permutation(len(standardized))
        midpoint = len(order) // 2
        train = order[:midpoint]
        heldout = order[midpoint:]
        train_covariance = replicated_covariance(
            standardized[train, 0],
            standardized[train, 1],
        )
        train_density, _train_positive, _train_rank = _positive_density(
            train_covariance
        )
        maximum_density = max(
            float(np.linalg.eigvalsh(train_density).max()),
            1e-12,
        )
        soft_projector = train_density / maximum_density
        heldout_covariance = replicated_covariance(
            standardized[heldout, 0],
            standardized[heldout, 1],
        )
        values, vectors = _eigendecomposition(heldout_covariance)
        positive = np.clip(values, 0.0, None)
        if float(np.sum(positive)) <= 1e-12:
            continue
        positive_covariance = (vectors * positive) @ vectors.T
        retained.append(
            float(
                np.trace(soft_projector @ positive_covariance)
                / np.sum(positive)
            )
        )
    if not retained:
        return 1.0
    return float(np.quantile(retained, 0.01))


def fit_family_support(
    family: str,
    raw_d0: np.ndarray,
    metadata_d0: pd.DataFrame,
    *,
    spec: RealTextRelationSpec,
    seed: int,
) -> FrozenFamilySupport:
    """Fit a D0-only replicated support and whitening map."""
    center, scale = _fit_standardizer(raw_d0)
    standardized = _standardize(raw_d0, center, scale)
    covariance = replicated_covariance(standardized[:, 0], standardized[:, 1])
    density, _positive, effective_rank = _positive_density(covariance)
    soft_filter = _density_sqrt(density)
    eigenvalues, null_eigenvalues, rank = _select_support_rank(
        standardized,
        metadata_d0,
        spec=spec,
        seed=seed,
    )
    if rank < spec.minimum_rank:
        empty = np.empty((raw_d0.shape[-1], 0), dtype=float)
        return FrozenFamilySupport(
            family=family,
            center=center,
            scale=scale,
            basis=empty,
            eigenvalues=eigenvalues,
            null_eigenvalues=null_eigenvalues,
            rank=rank,
            whitener=np.empty((0, 0), dtype=float),
            density=density,
            soft_filter=soft_filter,
            effective_rank=effective_rank,
            retained_energy_floor=_calibrate_soft_retained_floor(
                standardized,
                spec=spec,
                seed=seed + 2,
            ),
            alignment_floor=float(spec.alignment_floor),
            eigengap=float("nan"),
            status=(
                "SOFT_SUPPORT_CALIBRATED"
                if effective_rank >= spec.minimum_rank
                else "SUPPORT_UNDERRESOLVED"
            ),
        )
    _values, vectors = _eigendecomposition(covariance)
    basis = vectors[:, :rank]
    projected = np.einsum("nrd,dk->nrk", standardized, basis)
    whitener = _inverse_sqrt(
        replicated_covariance(projected[:, 0], projected[:, 1]),
        ridge=spec.ridge,
    )
    following = float(eigenvalues[rank]) if rank < len(eigenvalues) else 0.0
    eigengap = float(
        (eigenvalues[rank - 1] - following)
        / max(abs(float(eigenvalues[rank - 1])), 1e-12)
    )
    floor = _calibrate_alignment_floor(
        standardized,
        basis,
        spec=spec,
        seed=seed + 1,
    )
    return FrozenFamilySupport(
        family=family,
        center=center,
        scale=scale,
        basis=basis,
        eigenvalues=eigenvalues,
        null_eigenvalues=null_eigenvalues,
        rank=rank,
        whitener=whitener,
        density=density,
        soft_filter=soft_filter,
        effective_rank=effective_rank,
        retained_energy_floor=_calibrate_soft_retained_floor(
            standardized,
            spec=spec,
            seed=seed + 2,
        ),
        alignment_floor=floor,
        eigengap=eigengap,
        status="SOFT_SUPPORT_CALIBRATED",
    )


def project_family(
    raw: np.ndarray,
    support: FrozenFamilySupport,
    *,
    target_center: bool = False,
) -> np.ndarray:
    """Project through a frozen source support."""
    standardized = _standardize(raw, support.center, support.scale)
    if target_center:
        standardized = standardized - standardized.reshape(
            -1,
            standardized.shape[-1],
        ).mean(axis=0)[None, None, :]
    return np.einsum("nrd,dk->nrk", standardized, support.basis)


def project_family_soft(
    raw: np.ndarray,
    support: FrozenFamilySupport,
    *,
    target_center: bool = False,
) -> np.ndarray:
    """Apply the source-frozen soft spectral filter without choosing axes."""
    standardized = _standardize(raw, support.center, support.scale)
    if target_center:
        standardized = standardized - standardized.reshape(
            -1,
            standardized.shape[-1],
        ).mean(axis=0)[None, None, :]
    return np.einsum("nrd,dk->nrk", standardized, support.soft_filter)


def candidate_support_geometry(
    raw: np.ndarray,
    support: FrozenFamilySupport,
) -> dict[str, Any]:
    """Assess target replicated support in the source-standardized space."""
    if support.effective_rank < 1:
        return {
            "status": "SUPPORT_UNDERRESOLVED",
            "rank": 0,
            "omega": 0.0,
            "worst_alignment": 0.0,
            "retained_energy": 0.0,
        }
    standardized = _standardize(raw, support.center, support.scale)
    covariance = replicated_covariance(standardized[:, 0], standardized[:, 1])
    values, vectors = _eigendecomposition(covariance)
    positive = np.clip(values, 0.0, None)
    candidate_density, _candidate_positive, candidate_effective_rank = (
        _positive_density(covariance)
    )
    if candidate_effective_rank < 1:
        return {
            "status": "SUPPORT_UNDERRESOLVED",
            "rank": 0,
            "omega": 0.0,
            "worst_alignment": 0.0,
            "retained_energy": 0.0,
        }
    candidate_rank = min(support.rank, int(np.sum(positive > 1e-10)))
    overlap = (
        support_overlap(
            support.basis,
            vectors[:, : support.rank],
        )
        if support.rank >= 1 and candidate_rank >= support.rank
        else {
            "omega": 0.0,
            "worst_alignment": 0.0,
        }
    )
    hs_alignment = _hilbert_schmidt_alignment(
        support.density,
        candidate_density,
    )
    fidelity = _density_fidelity(support.density, candidate_density)
    null = _haar_alignment_null(
        support.density,
        candidate_density,
        draws=99,
        seed=stable_bucket(
            f"{support.family}-{raw.shape}-{float(np.sum(raw)):.8g}",
            salt="v8rt-soft-support",
            modulus=2**31 - 1,
        ),
    )
    null_q99 = float(np.quantile(null, 0.99))
    p_value = float((1 + np.sum(null >= hs_alignment)) / (len(null) + 1))
    soft_aligned = bool(hs_alignment > null_q99 and p_value <= 0.05)
    maximum_density = max(float(np.linalg.eigvalsh(support.density).max()), 1e-12)
    soft_projector = support.density / maximum_density
    retained = float(
        np.trace(soft_projector @ (vectors * positive) @ vectors.T)
        / max(float(np.sum(positive)), 1e-12)
    )
    hard_aligned = bool(
        support.rank >= 1
        and candidate_rank >= support.rank
        and overlap["worst_alignment"] >= support.alignment_floor
    )
    if hard_aligned:
        status = "SUPPORT_ALIGNED"
    elif soft_aligned:
        status = "SOFT_SUPPORT_ALIGNED_HARD_AXES_NONIDENTIFIABLE"
    else:
        status = "SUPPORT_NONINVARIANT"
    return {
        "status": status,
        "rank": int(candidate_rank),
        "effective_rank": candidate_effective_rank,
        "omega": overlap["omega"],
        "worst_alignment": overlap["worst_alignment"],
        "hs_alignment": hs_alignment,
        "hs_null_q99": null_q99,
        "hs_p_value": p_value,
        "density_fidelity": fidelity,
        "bures_distance": float(
            np.sqrt(max(0.0, 2.0 - 2.0 * np.sqrt(max(fidelity, 0.0))))
        ),
        "retained_energy": retained,
        "kth_eigenvalue": (
            float(values[support.rank - 1])
            if support.rank >= 1 and len(values) >= support.rank
            else float("nan")
        ),
    }


def _matrix_strength(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix) / np.sqrt(matrix.size))


def _matrix_cosine(left: np.ndarray, right: np.ndarray) -> float:
    a = np.asarray(left, dtype=float).ravel()
    b = np.asarray(right, dtype=float).ravel()
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denominator) if denominator > 1e-12 else 0.0


def _relation_permutation_samples(
    left: np.ndarray,
    right: np.ndarray,
    *,
    draws: int,
    spectrum_length: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Return row-permutation relation matrices and singular spectra."""
    rng = np.random.default_rng(seed)
    matrices = np.empty(
        (int(draws), left.shape[-1], right.shape[-1]),
        dtype=float,
    )
    spectra = np.empty((int(draws), int(spectrum_length)), dtype=float)
    for draw in range(int(draws)):
        order = rng.permutation(len(left))
        matrix = soft_relation_matrix(left, right[order])
        matrices[draw] = matrix
        spectra[draw] = _spectrum(matrix, spectrum_length)
    return matrices, spectra


def _spectrum(matrix: np.ndarray, length: int | None = None) -> np.ndarray:
    values = np.linalg.svd(matrix, compute_uv=False)
    if length is None:
        return values
    result = np.zeros(int(length), dtype=float)
    result[: min(len(values), len(result))] = values[: len(result)]
    return result


def relation_matrix(
    left: np.ndarray,
    right: np.ndarray,
    *,
    left_whitener: np.ndarray,
    right_whitener: np.ndarray,
) -> np.ndarray:
    """Estimate a symmetric cross-replicate relation matrix."""
    covariance = 0.5 * (
        _cross_covariance(left[:, 0], right[:, 1])
        + _cross_covariance(left[:, 1], right[:, 0])
    )
    return left_whitener @ covariance @ right_whitener


def soft_relation_matrix(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Return a trace-normalized cross-replicate relation operator."""
    covariance = _soft_cross_covariance(left, right)
    return covariance / _soft_relation_denominator(left, right)


def _soft_cross_covariance(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return 0.5 * (
        _cross_covariance(left[:, 0], right[:, 1])
        + _cross_covariance(left[:, 1], right[:, 0])
    )


def _soft_relation_denominator(left: np.ndarray, right: np.ndarray) -> float:
    left_covariance = replicated_covariance(left[:, 0], left[:, 1])
    right_covariance = replicated_covariance(right[:, 0], right[:, 1])
    left_energy = float(np.sum(np.clip(
        np.linalg.eigvalsh(0.5 * (left_covariance + left_covariance.T)),
        0.0,
        None,
    )))
    right_energy = float(np.sum(np.clip(
        np.linalg.eigvalsh(0.5 * (right_covariance + right_covariance.T)),
        0.0,
        None,
    )))
    return max(np.sqrt(left_energy * right_energy), 1e-12)


def _relation_nulls(
    left: np.ndarray,
    right: np.ndarray,
    metadata: pd.DataFrame,
    *,
    draws: int,
    seed: int,
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    local_max = np.zeros(draws, dtype=float)
    between = np.zeros(draws, dtype=float)
    contexts = metadata["context"].astype(str).to_numpy()
    resolved = [
        context
        for context, count in metadata["context"].value_counts().items()
        if int(count) >= 4
    ]
    for draw in range(draws):
        order = rng.permutation(len(metadata))
        strengths = []
        for context in resolved:
            mask = contexts == context
            matrix = soft_relation_matrix(left[mask], right[order][mask])
            strengths.append(_matrix_strength(matrix))
        local_max[draw] = max(strengths, default=0.0)
        between[draw] = _matrix_strength(
            _soft_between_relation(
                left,
                right[order],
                contexts,
            )
        )
    return float(np.quantile(local_max, 0.99)), float(np.quantile(between, 0.99))


def _soft_between_relation(
    left: np.ndarray,
    right: np.ndarray,
    contexts: np.ndarray,
) -> np.ndarray:
    covariance = _soft_between_covariance(left, right, contexts)
    left_covariance = replicated_covariance(left[:, 0], left[:, 1])
    right_covariance = replicated_covariance(right[:, 0], right[:, 1])
    left_energy = float(np.sum(np.clip(
        np.linalg.eigvalsh(0.5 * (left_covariance + left_covariance.T)),
        0.0,
        None,
    )))
    right_energy = float(np.sum(np.clip(
        np.linalg.eigvalsh(0.5 * (right_covariance + right_covariance.T)),
        0.0,
        None,
    )))
    return covariance / max(np.sqrt(left_energy * right_energy), 1e-12)


def _soft_between_covariance(
    left: np.ndarray,
    right: np.ndarray,
    contexts: np.ndarray,
) -> np.ndarray:
    def directional(first: np.ndarray, second: np.ndarray) -> np.ndarray:
        overall_first = first.mean(axis=0)
        overall_second = second.mean(axis=0)
        value = np.zeros((first.shape[-1], second.shape[-1]), dtype=float)
        for context in np.unique(contexts):
            mask = contexts == context
            weight = float(mask.mean())
            value += weight * np.outer(
                first[mask].mean(axis=0) - overall_first,
                second[mask].mean(axis=0) - overall_second,
            )
        return value

    return 0.5 * (
        directional(left[:, 0], right[:, 1])
        + directional(left[:, 1], right[:, 0])
    )


def _fit_alias_audit(
    raw: dict[str, np.ndarray],
    metadata: pd.DataFrame,
    supports: dict[str, FrozenFamilySupport],
    *,
    spec: RealTextRelationSpec,
) -> dict[str, Any]:
    """Test whether K retains replicated support after predicting it from M."""
    if any(value.status == "SUPPORT_UNDERRESOLVED" for value in supports.values()):
        return {
            "status": "FAMILY_ALIAS_UNRESOLVED_SUPPORT",
            "cross_validated_r2": float("nan"),
            "residual_rank": 0,
        }
    m = project_family_soft(raw["M"], supports["M"])
    k = project_family_soft(raw["K"], supports["K"])
    indices = np.arange(len(metadata))
    fold = np.asarray(
        [
            stable_bucket(str(author), salt="v8rt-alias", modulus=2)
            for author in metadata["author_id"]
        ],
        dtype=int,
    )
    predictions = np.zeros_like(k)
    for heldout in (0, 1):
        train = fold != heldout
        test = fold == heldout
        design = np.column_stack(
            [
                np.ones(2 * int(train.sum())),
                m[train].reshape(-1, m.shape[-1]),
            ]
        )
        target = k[train].reshape(-1, k.shape[-1])
        penalty = spec.ridge * np.eye(design.shape[1])
        penalty[0, 0] = 0.0
        coefficients = np.linalg.solve(
            design.T @ design + penalty,
            design.T @ target,
        )
        test_design = np.column_stack(
            [
                np.ones(2 * int(test.sum())),
                m[test].reshape(-1, m.shape[-1]),
            ]
        )
        predictions[test] = (test_design @ coefficients).reshape(
            int(test.sum()),
            2,
            -1,
        )
    residual = k - predictions
    total = float(np.sum((k - k.mean(axis=(0, 1), keepdims=True)) ** 2))
    error = float(np.sum(residual**2))
    covariance = replicated_covariance(residual[:, 0], residual[:, 1])
    values, _vectors = _eigendecomposition(covariance)
    observed_energy = float(np.sum(np.clip(values, 0.0, None)))
    rng = np.random.default_rng(spec.seed + 79)
    null_energy = np.empty(spec.support_permutations, dtype=float)
    for draw in range(spec.support_permutations):
        order = rng.permutation(indices)
        null_values, _ = _eigendecomposition(
            replicated_covariance(residual[:, 0], residual[order, 1])
        )
        null_energy[draw] = float(np.sum(np.clip(null_values, 0.0, None)))
    threshold = float(np.quantile(null_energy, 0.99))
    residual_rank = int(np.sum(values > 0))
    status = (
        "FAMILIES_DISTINCT"
        if residual_rank >= spec.alias_residual_rank_floor
        and observed_energy > threshold
        else "FAMILY_ALGEBRAIC_ALIAS"
    )
    return {
        "status": status,
        "cross_validated_r2": float(1.0 - error / max(total, 1e-12)),
        "residual_rank": residual_rank,
        "residual_positive_energy": observed_energy,
        "leading_residual_eigenvalue": float(values[0]),
        "residual_null_q99": threshold,
    }


def fit_corpus_calibration(
    corpus: str,
    panel: CorpusFeaturePanel,
    *,
    spec: RealTextRelationSpec,
) -> FrozenCorpusCalibration:
    """Freeze all support and relation objects on D0 authors only."""
    d0 = panel.metadata["split"].eq("D0").to_numpy()
    if int(d0.sum()) < spec.minimum_split_authors:
        raise ValueError(
            f"{corpus} has only {int(d0.sum())} D0 authors; "
            f"minimum is {spec.minimum_split_authors}."
        )
    metadata = panel.metadata.loc[d0].reset_index(drop=True)
    supports = {
        family: fit_family_support(
            family,
            panel.raw[family][d0],
            metadata,
            spec=spec,
            seed=spec.seed + 100 * index,
        )
        for index, family in enumerate(FAMILY_NAMES)
    }
    if all(value.status != "SUPPORT_UNDERRESOLVED" for value in supports.values()):
        left = project_family_soft(panel.raw["M"][d0], supports["M"])
        right = project_family_soft(panel.raw["K"][d0], supports["K"])
        relation_null, between_null = _relation_nulls(
            left,
            right,
            metadata,
            draws=spec.relation_permutations,
            seed=spec.seed + 317,
        )
    else:
        relation_null = float("nan")
        between_null = float("nan")
    alias = _fit_alias_audit(
        {family: panel.raw[family][d0] for family in FAMILY_NAMES},
        metadata,
        supports,
        spec=spec,
    )
    return FrozenCorpusCalibration(
        corpus=corpus,
        supports=supports,
        relation_null_q99=relation_null,
        between_null_q99=between_null,
        alias=alias,
        spec=spec,
    )


def _macro_decomposition(
    left: np.ndarray,
    right: np.ndarray,
    contexts: np.ndarray,
) -> dict[str, Any]:
    unique = np.unique(contexts)
    local = []
    weights = []
    denominator = _soft_relation_denominator(left, right)
    for context in unique:
        mask = contexts == context
        weights.append(float(mask.mean()))
        local.append(_soft_cross_covariance(left[mask], right[mask]) / denominator)
    matrices = np.asarray(local)
    weights_array = np.asarray(weights)
    within = np.einsum("s,sij->ij", weights_array, matrices)
    between_covariance = _soft_between_covariance(left, right, contexts)
    between = between_covariance / denominator
    total = _soft_cross_covariance(left, right) / denominator
    decomposition_error = float(
        np.linalg.norm(total - within - between)
        / max(np.linalg.norm(total), np.linalg.norm(within + between), 1e-12)
    )
    energy = float(
        np.sum(weights_array * np.sum(matrices**2, axis=(1, 2)))
    )
    heterogeneity = float(
        np.sum(
            weights_array
            * np.sum((matrices - within[None, :, :]) ** 2, axis=(1, 2))
        )
        / max(energy, 1e-12)
    )
    local_norm = float(
        np.sum(weights_array * np.linalg.norm(matrices, axis=(1, 2)))
    )
    cancellation = float(
        1.0 - np.linalg.norm(within) / max(local_norm, 1e-12)
    )
    return {
        "contexts": unique.tolist(),
        "weights": weights_array.tolist(),
        "local": matrices,
        "within": within,
        "between": between,
        "total": total,
        "decomposition_error": decomposition_error,
        "heterogeneity": heterogeneity,
        "cancellation": cancellation,
    }


def evaluate_corpus_local(
    panel: CorpusFeaturePanel,
    calibration: FrozenCorpusCalibration,
) -> dict[str, list[dict[str, Any]]]:
    """Evaluate D1 and D2 without refitting any D0-selected object."""
    support_rows: list[dict[str, Any]] = []
    relation_rows: list[dict[str, Any]] = []
    macro_rows: list[dict[str, Any]] = []
    split_details: dict[str, dict[str, dict[str, Any]]] = {}
    for split in ("D1", "D2"):
        mask = panel.metadata["split"].eq(split).to_numpy()
        metadata = panel.metadata.loc[mask].reset_index(drop=True)
        if int(mask.sum()) < calibration.spec.minimum_split_authors:
            for family in FAMILY_NAMES:
                support_rows.append(
                    {
                        "corpus": calibration.corpus,
                        "split": split,
                        "family": family,
                        "n_authors": int(mask.sum()),
                        "status": "SUPPORT_UNDERRESOLVED",
                    }
                )
            continue
        geometries = {}
        for family in FAMILY_NAMES:
            geometry = candidate_support_geometry(
                panel.raw[family][mask],
                calibration.supports[family],
            )
            geometries[family] = geometry
            support_rows.append(
                {
                    "corpus": calibration.corpus,
                    "split": split,
                    "family": family,
                    "n_authors": int(mask.sum()),
                    "reference_rank": calibration.supports[family].rank,
                    "reference_effective_rank": calibration.supports[
                        family
                    ].effective_rank,
                    "alignment_floor": calibration.supports[family].alignment_floor,
                    **geometry,
                }
            )
        if any(
            geometry["status"]
            not in {
                "SUPPORT_ALIGNED",
                "SOFT_SUPPORT_ALIGNED_HARD_AXES_NONIDENTIFIABLE",
            }
            for geometry in geometries.values()
        ):
            continue
        left = project_family_soft(
            panel.raw["M"][mask],
            calibration.supports["M"],
        )
        right = project_family_soft(
            panel.raw["K"][mask],
            calibration.supports["K"],
        )
        contexts = metadata["context"].astype(str).to_numpy()
        resolved = [
            context
            for context, count in metadata["context"].value_counts().items()
            if int(count) >= calibration.spec.minimum_context_authors
        ]
        resolved_total = int(metadata["context"].isin(resolved).sum())
        details = {}
        for context in resolved:
            context_mask = contexts == context
            context_left = left[context_mask]
            context_right = right[context_mask]
            matrix = soft_relation_matrix(context_left, context_right)
            spectrum = _spectrum(matrix, calibration.spec.maximum_rank)
            null_matrices, null_spectra = _relation_permutation_samples(
                context_left,
                context_right,
                draws=calibration.spec.relation_permutations,
                spectrum_length=calibration.spec.maximum_rank,
                seed=calibration.spec.seed
                + stable_bucket(
                    f"{calibration.corpus}-{split}-{context}",
                    salt="v8rt-relation-local-null",
                    modulus=2**31 - 1,
                ),
            )
            local_strengths = np.asarray(
                [_matrix_strength(value) for value in null_matrices],
                dtype=float,
            )
            local_p = float(
                (
                    1
                    + np.sum(local_strengths >= _matrix_strength(matrix))
                )
                / (len(local_strengths) + 1)
            )
            null_spectrum_mean = null_spectra.mean(axis=0)
            excess_spectrum = spectrum - null_spectrum_mean
            details[str(context)] = {
                "matrix": matrix,
                "spectrum": spectrum,
                "excess_spectrum": excess_spectrum,
                "null_matrices": (
                    null_matrices if split == "D2" else np.empty((0, 0, 0))
                ),
                "null_spectra": null_spectra,
                "left": context_left,
                "right": context_right,
            }
            relation_rows.append(
                {
                    "corpus": calibration.corpus,
                    "split": split,
                    "context": str(context),
                    "context_role": panel.context_role,
                    "replicate_type": panel.replicate_type,
                    "n_authors": int(context_mask.sum()),
                    "weight": float(context_mask.sum() / max(resolved_total, 1)),
                    "sigma1": float(spectrum[0]),
                    "sigma2": float(spectrum[1]),
                    "fro_norm": float(np.linalg.norm(matrix)),
                    "rms_strength": _matrix_strength(matrix),
                    "spectrum": spectrum.tolist(),
                    "null_spectrum_mean": null_spectrum_mean.tolist(),
                    "excess_spectrum": excess_spectrum.tolist(),
                    "local_permutation_p": local_p,
                    "null_q99": calibration.relation_null_q99,
                    "relation_license": int(
                        _matrix_strength(matrix) > calibration.relation_null_q99
                        and local_p <= 0.05
                        and calibration.alias["status"] == "FAMILIES_DISTINCT"
                    ),
                }
            )
        split_details[split] = details
        if len(resolved) >= 2:
            resolved_mask = metadata["context"].isin(resolved).to_numpy()
            macro = _macro_decomposition(
                left[resolved_mask],
                right[resolved_mask],
                contexts[resolved_mask],
            )
            macro_rows.append(
                {
                    "corpus": calibration.corpus,
                    "split": split,
                    "context_count": int(len(resolved)),
                    "n_authors": int(resolved_mask.sum()),
                    "J_W_norm": float(np.linalg.norm(macro["within"])),
                    "J_B_norm": float(np.linalg.norm(macro["between"])),
                    "J_T_norm": float(np.linalg.norm(macro["total"])),
                    "H": macro["heterogeneity"],
                    "kappa": macro["cancellation"],
                    "decomposition_error": macro["decomposition_error"],
                    "between_null_q99": calibration.between_null_q99,
                    "ecological_between_detected": int(
                        _matrix_strength(macro["between"])
                        > calibration.between_null_q99
                    ),
                    "classification": "MULTI_CONTEXT_OBSERVATIONAL",
                }
            )
        else:
            macro_rows.append(
                {
                    "corpus": calibration.corpus,
                    "split": split,
                    "context_count": int(len(resolved)),
                    "n_authors": int(len(metadata)),
                    "J_W_norm": float("nan"),
                    "J_B_norm": float("nan"),
                    "J_T_norm": float("nan"),
                    "H": float("nan"),
                    "kappa": float("nan"),
                    "decomposition_error": float("nan"),
                    "between_null_q99": calibration.between_null_q99,
                    "ecological_between_detected": 0,
                    "classification": "SINGLE_OR_UNDERRESOLVED_CONTEXT_ONLY",
                }
            )
    common_contexts = sorted(
        set(split_details.get("D1", {}))
        & set(split_details.get("D2", {}))
    )
    agreement_rows = []
    for context in common_contexts:
        first = split_details["D1"][context]
        second = split_details["D2"][context]
        matrix_first = first["matrix"]
        matrix_second = second["matrix"]
        spectrum_first = first["spectrum"]
        spectrum_second = second["spectrum"]
        excess_first = first["excess_spectrum"]
        excess_second = second["excess_spectrum"]
        matrix_cosine = _matrix_cosine(matrix_first, matrix_second)
        matrix_null = np.asarray(
            [
                _matrix_cosine(matrix_first, candidate)
                for candidate in second["null_matrices"]
            ],
            dtype=float,
        )
        matrix_p = float(
            (1 + np.sum(matrix_null >= matrix_cosine))
            / (len(matrix_null) + 1)
        )
        excess_cosine = _matrix_cosine(excess_first, excess_second)
        excess_null = np.asarray(
            [
                _matrix_cosine(
                    excess_first,
                    candidate - second["null_spectra"].mean(axis=0),
                )
                for candidate in second["null_spectra"]
            ],
            dtype=float,
        )
        excess_p = float(
            (1 + np.sum(excess_null >= excess_cosine))
            / (len(excess_null) + 1)
        )
        rows_for_context = [
            row
            for row in relation_rows
            if row["context"] == context
            and row["corpus"] == calibration.corpus
        ]
        both_energy_licensed = (
            len(rows_for_context) == 2
            and all(row["relation_license"] == 1 for row in rows_for_context)
        )
        if both_energy_licensed and matrix_p <= 0.05 and matrix_cosine > 0:
            classification = "RELATION_OPERATOR_REPLICATED"
        elif both_energy_licensed and excess_p <= 0.05 and excess_cosine > 0:
            classification = "GAUGE_INVARIANT_EXCESS_SPECTRUM_REPLICATED"
        elif both_energy_licensed:
            classification = "DEPENDENCE_ENERGY_ONLY"
        else:
            classification = "RELATION_NOT_REPLICATED"
        agreement_rows.append(
            {
                "corpus": calibration.corpus,
                "context": context,
                "matrix_cosine": matrix_cosine,
                "matrix_null_q95": float(np.quantile(matrix_null, 0.95)),
                "matrix_agreement_p": matrix_p,
                "spectrum_cosine": _matrix_cosine(
                    spectrum_first,
                    spectrum_second,
                ),
                "excess_spectrum_cosine": excess_cosine,
                "excess_spectrum_null_q95": float(
                    np.quantile(excess_null, 0.95)
                ),
                "excess_spectrum_agreement_p": excess_p,
                "d1_d2_agreement": int(
                    classification
                    in {
                        "RELATION_OPERATOR_REPLICATED",
                        "GAUGE_INVARIANT_EXCESS_SPECTRUM_REPLICATED",
                    }
                ),
                "classification": classification,
            }
        )
    return {
        "support": support_rows,
        "relation": relation_rows,
        "macro": macro_rows,
        "agreement": agreement_rows,
    }


def transport_calibration(
    source: FrozenCorpusCalibration,
    target_panel: CorpusFeaturePanel,
) -> dict[str, list[dict[str, Any]]]:
    """Apply a source-frozen map to a target corpus and audit comparability."""
    rows: list[dict[str, Any]] = []
    relation_rows: list[dict[str, Any]] = []
    for family in FAMILY_NAMES:
        d0 = target_panel.metadata["split"].eq("D0").to_numpy()
        geometry = candidate_support_geometry(
            target_panel.raw[family][d0],
            source.supports[family],
        )
        rows.append(
            {
                "source": source.corpus,
                "target": str(target_panel.metadata["corpus"].iloc[0]),
                "family": family,
                "target_d0_authors": int(d0.sum()),
                "source_rank": source.supports[family].rank,
                "alignment_floor": source.supports[family].alignment_floor,
                "retained_energy_floor": source.supports[
                    family
                ].retained_energy_floor,
                **geometry,
                "decision": (
                    "TRANSPORT_SUPPORT_ACCEPT"
                    if geometry["status"]
                    in {
                        "SUPPORT_ALIGNED",
                        "SOFT_SUPPORT_ALIGNED_HARD_AXES_NONIDENTIFIABLE",
                    }
                    and geometry["retained_energy"]
                    >= source.supports[family].retained_energy_floor
                    else "TRANSPORT_SUPPORT_REFUSE"
                ),
            }
        )
    accepted = all(row["decision"] == "TRANSPORT_SUPPORT_ACCEPT" for row in rows)
    for arm, target_center in (
        ("strict_source", False),
        ("source_support_target_center", True),
    ):
        for split in ("D1", "D2"):
            mask = target_panel.metadata["split"].eq(split).to_numpy()
            if int(mask.sum()) < source.spec.minimum_split_authors or not accepted:
                relation_rows.append(
                    {
                        "source": source.corpus,
                        "target": str(target_panel.metadata["corpus"].iloc[0]),
                        "arm": arm,
                        "split": split,
                        "n_authors": int(mask.sum()),
                        "status": "TRANSPORT_REFUSED",
                    }
                )
                continue
            left = project_family_soft(
                target_panel.raw["M"][mask],
                source.supports["M"],
                target_center=target_center,
            )
            right = project_family_soft(
                target_panel.raw["K"][mask],
                source.supports["K"],
                target_center=target_center,
            )
            matrix = soft_relation_matrix(left, right)
            spectrum = _spectrum(matrix, source.spec.maximum_rank)
            relation_rows.append(
                {
                    "source": source.corpus,
                    "target": str(target_panel.metadata["corpus"].iloc[0]),
                    "arm": arm,
                    "split": split,
                    "n_authors": int(mask.sum()),
                    "status": "TRANSPORT_ESTIMATED",
                    "sigma1": float(spectrum[0]),
                    "sigma2": float(spectrum[1]),
                    "fro_norm": float(np.linalg.norm(matrix)),
                    "rms_strength": _matrix_strength(matrix),
                    "spectrum": spectrum.tolist(),
                }
            )
    return {"support": rows, "relation": relation_rows}


def approximate_gromov_wasserstein(
    left: np.ndarray,
    right: np.ndarray,
    *,
    maximum_authors: int,
    iterations: int,
    seed: int,
) -> dict[str, Any]:
    """Approximate squared-loss GW by Frank-Wolfe assignment updates.

    Equal deterministic subsamples and uniform masses are used. The returned
    value is a technical population-geometry diagnostic, not an exact optimal
    transport certificate.
    """
    rng = np.random.default_rng(seed)
    n = min(len(left), len(right), int(maximum_authors))
    if n < 8:
        return {"status": "GW_UNDERRESOLVED", "n": int(n), "distance": float("nan")}
    left_indices = rng.choice(len(left), size=n, replace=False)
    right_indices = rng.choice(len(right), size=n, replace=False)
    x = np.asarray(left[left_indices], dtype=float)
    y = np.asarray(right[right_indices], dtype=float)

    def distances(values: np.ndarray) -> np.ndarray:
        squared = np.sum(values**2, axis=1)
        matrix = np.sqrt(
            np.maximum(
                squared[:, None] + squared[None, :] - 2.0 * values @ values.T,
                0.0,
            )
        )
        positive = matrix[matrix > 0]
        scale = float(np.median(positive)) if len(positive) else 1.0
        return matrix / max(scale, 1e-12)

    c1 = distances(x)
    c2 = distances(y)
    p = np.full(n, 1.0 / n)
    q = np.full(n, 1.0 / n)
    constant = (c1**2 @ p)[:, None] + (c2**2 @ q)[None, :]

    def objective(coupling: np.ndarray) -> float:
        return float(
            np.sum(constant * coupling)
            - 2.0 * np.sum((c1 @ coupling @ c2.T) * coupling)
        )

    coupling = np.outer(p, q)
    previous = objective(coupling)
    for _ in range(int(iterations)):
        gradient = constant - 4.0 * (c1 @ coupling @ c2.T)
        row, column = linear_sum_assignment(gradient)
        vertex = np.zeros_like(coupling)
        vertex[row, column] = 1.0 / n
        direction = vertex - coupling
        result = minimize_scalar(
            lambda alpha: objective(coupling + float(alpha) * direction),
            bounds=(0.0, 1.0),
            method="bounded",
        )
        coupling = coupling + float(result.x) * direction
        current = objective(coupling)
        if abs(previous - current) <= 1e-8 * max(1.0, abs(previous)):
            previous = current
            break
        previous = current
    return {
        "status": "GW_APPROXIMATED",
        "n": int(n),
        "distance": float(np.sqrt(max(previous, 0.0))),
        "iterations": int(iterations),
        "solver": "uniform_frank_wolfe_linear_assignment",
    }


def author_coordinates(
    panel: CorpusFeaturePanel,
    calibration: FrozenCorpusCalibration,
    *,
    split: str = "D0",
) -> tuple[pd.DataFrame, np.ndarray]:
    """Return concatenated local M/K author coordinates."""
    mask = panel.metadata["split"].eq(split).to_numpy()
    pieces = []
    for family in FAMILY_NAMES:
        support = calibration.supports[family]
        if support.status == "SUPPORT_UNDERRESOLVED":
            return panel.metadata.loc[mask].copy(), np.empty((int(mask.sum()), 0))
        projected = project_family_soft(panel.raw[family][mask], support)
        pieces.append(projected.mean(axis=1))
    return panel.metadata.loc[mask].reset_index(drop=True), np.concatenate(pieces, axis=1)


def _transport_cost(
    cost: np.ndarray,
    left_weights: np.ndarray,
    right_weights: np.ndarray,
) -> tuple[float, np.ndarray]:
    rows, columns = cost.shape
    objective = cost.ravel()
    equality = []
    target = []
    for row in range(rows):
        constraint = np.zeros((rows, columns), dtype=float)
        constraint[row, :] = 1.0
        equality.append(constraint.ravel())
        target.append(left_weights[row])
    for column in range(columns):
        constraint = np.zeros((rows, columns), dtype=float)
        constraint[:, column] = 1.0
        equality.append(constraint.ravel())
        target.append(right_weights[column])
    result = linprog(
        objective,
        A_eq=np.vstack(equality),
        b_eq=np.asarray(target),
        bounds=(0.0, None),
        method="highs",
    )
    if not result.success:
        raise RuntimeError(f"Context transport failed: {result.message}")
    coupling = result.x.reshape(rows, columns)
    return float(np.sum(coupling * cost)), coupling


def frgw_summary(
    corpus_a: str,
    corpus_b: str,
    support_transport: list[dict[str, Any]],
    context_a: list[dict[str, Any]],
    context_b: list[dict[str, Any]],
    geometry_cost: np.ndarray | None,
) -> dict[str, Any]:
    """Combine support, population, relation, and composition defects."""
    rows = [
        row
        for row in support_transport
        if row["source"] == corpus_a and row["target"] == corpus_b
    ]
    if len(rows) != len(FAMILY_NAMES):
        return {
            "corpus_a": corpus_a,
            "corpus_b": corpus_b,
            "status": "FRGW_SUPPORT_MISSING",
        }
    support_defect = float(
        np.mean(
            [
                float(row.get("bures_distance", np.sqrt(2.0)))
                / np.sqrt(2.0)
                for row in rows
            ]
        )
    )
    if not context_a or not context_b or geometry_cost is None:
        return {
            "corpus_a": corpus_a,
            "corpus_b": corpus_b,
            "status": "FRGW_CONTEXT_UNDERRESOLVED",
            "support_defect": support_defect,
        }
    relation_cost = np.zeros((len(context_a), len(context_b)), dtype=float)
    for row, left in enumerate(context_a):
        for column, right in enumerate(context_b):
            left_spectrum = np.asarray(left["spectrum"], dtype=float)
            right_spectrum = np.asarray(right["spectrum"], dtype=float)
            norm = max(
                float(np.linalg.norm(left_spectrum)),
                float(np.linalg.norm(right_spectrum)),
                1e-12,
            )
            relation_cost[row, column] = float(
                np.linalg.norm(left_spectrum - right_spectrum) / norm
            )
    left_weights = np.asarray([row["weight"] for row in context_a], dtype=float)
    right_weights = np.asarray([row["weight"] for row in context_b], dtype=float)
    left_weights /= left_weights.sum()
    right_weights /= right_weights.sum()
    combined = geometry_cost + relation_cost
    total, coupling = _transport_cost(combined, left_weights, right_weights)
    population_defect = float(np.sum(coupling * geometry_cost))
    relation_defect = float(np.sum(coupling * relation_cost))
    return {
        "corpus_a": corpus_a,
        "corpus_b": corpus_b,
        "status": "FRGW_ESTIMATED",
        "support_defect": support_defect,
        "population_defect": population_defect,
        "relation_defect": relation_defect,
        "composition_cost": total,
        "total_FRGW": float(support_defect + total),
    }


def corpus_pair_names(corpora: Iterable[str]) -> list[tuple[str, str]]:
    """Return stable unordered corpus pairs."""
    return list(combinations(sorted(set(map(str, corpora))), 2))
