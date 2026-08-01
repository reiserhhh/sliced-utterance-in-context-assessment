"""Relation-to-individual bridge (M4-D leg 2).

The V8 type system forbids silent ``R -> V`` conversion.  This module builds
the licensed version: given an observed relation field ``R_uv`` (noisy pairwise
squared distances or similarities between authors), it computes a RIGIDITY
INDEX from the observed field alone and licenses reconstruction of individual
coordinates ``V_u`` (up to gauge: rotation, reflection, translation, and
isotropic scale) only when the index clears a pre-fixed threshold.

Formal frame: Euclidean distance geometry / Gram completion.  The observed
field is doubly centered into a Gram candidate ``B``; identifiability of a
rank-``r`` configuration requires (i) a stable signal rank (eigenvalues above
the noise floor estimated from the negative spectrum), (ii) an open spectral
gap at the candidate rank (Davis-Kahan: subspace error scales with
``||noise|| / (lambda_r - lambda_{r+1})``), and (iii) coordinate-level
stability under noise-matched re-measurement (the stress-stability probe).
Group-only worlds -- the v8_vanishing_individuality designed null, where
author separability is high with zero individual structure -- must be REFUSED:
their fields determine group centroids, never per-author coordinates.

Pre-fixed decision constants (set at design time, before the world battery was
run; recorded in the leg report):

- ``license_threshold = 0.5`` (provisional licensing tau on the index),
- ``label_margin_ratio = 0.5`` (ground-truth label: a world counts as
  reconstructable only when the gauge-aligned reconstruction error beats the
  median within-block permuted-truth baseline by a factor of two).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.linalg import orthogonal_procrustes
from sklearn.metrics import roc_auc_score

from .v8_vanishing_individuality import (
    VanishingIndividualitySpec,
    pairing_auc_metrics,
    simulate_hierarchical_c2_world,
)

_EPS = 1e-12


@dataclass(frozen=True)
class RelationBridgeConfig:
    """Pre-fixed constants for the rigidity index and the truth labels."""

    rank_cap: int = 8
    floor_multiplier: float = 2.0
    probe_replicates: int = 12
    probe_floor_fraction: float = 0.02
    permutation_draws: int = 24
    license_threshold: float = 0.5
    label_margin_ratio: float = 0.5


def squared_distance_field(points: np.ndarray) -> np.ndarray:
    """Exact squared Euclidean distance matrix of a configuration."""
    points = np.asarray(points, dtype=float)
    norms = np.sum(points**2, axis=1)
    field = norms[:, None] + norms[None, :] - 2.0 * points @ points.T
    field = np.maximum(field, 0.0)
    np.fill_diagonal(field, 0.0)
    return 0.5 * (field + field.T)


def gram_from_relation(
    relation: np.ndarray,
    *,
    kind: str = "squared_distance",
) -> np.ndarray:
    """Doubly centered Gram candidate from an observed relation field."""
    relation = np.asarray(relation, dtype=float)
    if relation.ndim != 2 or relation.shape[0] != relation.shape[1]:
        raise ValueError("relation field must be a square matrix")
    if kind == "similarity":
        diagonal = np.diag(relation)
        relation = diagonal[:, None] + diagonal[None, :] - 2.0 * relation
    elif kind != "squared_distance":
        raise ValueError(f"unsupported relation kind: {kind}")
    relation = 0.5 * (relation + relation.T)
    n = len(relation)
    centering = np.eye(n) - np.full((n, n), 1.0 / n)
    return -0.5 * centering @ relation @ centering


def spectral_profile(
    gram: np.ndarray,
    *,
    rank_cap: int = 8,
    floor_multiplier: float = 2.0,
) -> dict[str, Any]:
    """Eigenvalue profile, negative-spectrum noise floor, and rank choice."""
    eigenvalues = np.linalg.eigvalsh(0.5 * (gram + gram.T))[::-1]
    top = float(max(eigenvalues[0], 0.0))
    negative = eigenvalues[eigenvalues < 0.0]
    noise_floor = float(
        max(-negative.min() if len(negative) else 0.0, 1e-12 * max(top, 1.0))
    )
    selected = int(
        np.sum(eigenvalues > floor_multiplier * noise_floor)
    )
    selected = min(selected, rank_cap, len(eigenvalues) - 1)
    if selected >= 1:
        lam_r = float(eigenvalues[selected - 1])
        lam_next = float(max(eigenvalues[selected], 0.0))
        margin = (lam_r - lam_next) / max(lam_r + lam_next, _EPS)
        margin = float(np.clip(margin, 0.0, 1.0))
    else:
        lam_r = 0.0
        lam_next = float(max(eigenvalues[0], 0.0)) if len(eigenvalues) else 0.0
        margin = 0.0
    return {
        "eigenvalues": eigenvalues,
        "noise_floor": noise_floor,
        "selected_rank": selected,
        "lambda_rank": lam_r,
        "lambda_next": lam_next,
        "spectral_margin": margin,
    }


def classical_mds(gram: np.ndarray, rank: int) -> np.ndarray:
    """Classical MDS coordinates from the top ``rank`` Gram eigenpairs."""
    if rank < 1:
        return np.zeros((len(gram), 1))
    values, vectors = np.linalg.eigh(0.5 * (gram + gram.T))
    order = np.argsort(values)[::-1][:rank]
    scales = np.sqrt(np.maximum(values[order], 0.0))
    return vectors[:, order] * scales[None, :]


def _pad_columns(matrix: np.ndarray, width: int) -> np.ndarray:
    if matrix.shape[1] >= width:
        return matrix
    padding = np.zeros((matrix.shape[0], width - matrix.shape[1]))
    return np.hstack([matrix, padding])


def gauge_aligned_error(
    source: np.ndarray,
    target: np.ndarray,
    *,
    allow_scale: bool = True,
) -> float:
    """Normalized error after the best gauge (similarity) transform.

    Gauge group: rotation + reflection + translation, plus isotropic scale
    when ``allow_scale`` (the relation field only fixes scale up to the
    units of the observed similarities).  Returns
    ``||s * source @ Q - target||_F / ||target - mean||_F``.
    """
    source = np.asarray(source, dtype=float)
    target = np.asarray(target, dtype=float)
    width = max(source.shape[1], target.shape[1])
    source_c = _pad_columns(source - source.mean(axis=0), width)
    target_c = _pad_columns(target - target.mean(axis=0), width)
    target_norm = float(np.linalg.norm(target_c))
    rotation, gain = orthogonal_procrustes(source_c, target_c)
    scale = 1.0
    if allow_scale:
        source_norm_sq = float(np.sum(source_c**2))
        scale = gain / max(source_norm_sq, _EPS)
    aligned = scale * source_c @ rotation
    return float(
        np.linalg.norm(aligned - target_c) / max(target_norm, _EPS)
    )


def _procrustes_transport(
    source: np.ndarray,
    target: np.ndarray,
) -> np.ndarray:
    """Similarity-aligned copy of ``source`` in ``target`` coordinates."""
    width = max(source.shape[1], target.shape[1])
    source_c = _pad_columns(source - source.mean(axis=0), width)
    target_c = _pad_columns(target - target.mean(axis=0), width)
    rotation, gain = orthogonal_procrustes(source_c, target_c)
    scale = gain / max(float(np.sum(source_c**2)), _EPS)
    target_mean = _pad_columns(target.mean(axis=0)[None, :], width)
    return scale * source_c @ rotation + target_mean


def _offdiag_rms(matrix: np.ndarray) -> float:
    n = len(matrix)
    mask = ~np.eye(n, dtype=bool)
    return float(np.sqrt(np.mean(matrix[mask] ** 2)))


def _symmetric_noise(
    rng: np.random.Generator,
    n: int,
    sigma: float,
) -> np.ndarray:
    noise = rng.normal(scale=sigma, size=(n, n))
    noise = (noise + noise.T) / np.sqrt(2.0)
    np.fill_diagonal(noise, 0.0)
    return noise


def rigidity_report(
    relation: np.ndarray,
    *,
    config: RelationBridgeConfig = RelationBridgeConfig(),
    seed: int = 0,
    kind: str = "squared_distance",
    candidate_rank: int | None = None,
) -> dict[str, Any]:
    """Rigidity index and licensing decision from the observed field alone.

    Index = spectral_margin * stability (product composition, frozen after a
    three-seed placement pilot showed the sqrt composition leaves the
    group-only refusal margin thin at the easiest null cell; the product is
    a monotone transform of the same pair, so battery AUC is unaffected by
    this choice).  Stability is the mean identity-preservation rate under
    noise-matched re-measurement: perturb the field at its own estimated
    residual scale, re-embed, gauge-align to the unperturbed embedding, and
    ask whether each author's coordinate is still nearest to its own
    original coordinate.  Group-only fields fail this even at high author
    separability because same-group coordinates are interchangeable.
    """
    relation = np.asarray(relation, dtype=float)
    gram = gram_from_relation(relation, kind=kind)
    profile = spectral_profile(
        gram,
        rank_cap=config.rank_cap,
        floor_multiplier=config.floor_multiplier,
    )
    rank = (
        int(candidate_rank)
        if candidate_rank is not None
        else profile["selected_rank"]
    )
    base = {
        "selected_rank": rank,
        "auto_rank": profile["selected_rank"],
        "noise_floor": profile["noise_floor"],
        "lambda_rank": profile["lambda_rank"],
        "lambda_next": profile["lambda_next"],
        "spectral_margin": profile["spectral_margin"],
    }
    if rank < 1:
        return {
            **base,
            "status": "R_TO_V_REFUSED",
            "refusal_reason": "NO_STABLE_RANK",
            "stability": 0.0,
            "dispersion_ratio": float("inf"),
            "probe_sigma": float("nan"),
            "rigidity_index": 0.0,
        }
    if candidate_rank is not None:
        margin_profile = spectral_profile(
            gram,
            rank_cap=max(config.rank_cap, rank),
            floor_multiplier=config.floor_multiplier,
        )
        eigenvalues = margin_profile["eigenvalues"]
        lam_r = float(eigenvalues[rank - 1])
        lam_next = (
            float(max(eigenvalues[rank], 0.0))
            if rank < len(eigenvalues)
            else 0.0
        )
        base["lambda_rank"] = lam_r
        base["lambda_next"] = lam_next
        base["spectral_margin"] = (
            float(
                np.clip(
                    (lam_r - lam_next) / max(lam_r + lam_next, _EPS),
                    0.0,
                    1.0,
                )
            )
            if lam_r > 0
            else 0.0
        )
    embedding = classical_mds(gram, rank)
    model_field = squared_distance_field(embedding)
    residual = _offdiag_rms(relation - model_field)
    probe_sigma = max(
        residual,
        config.probe_floor_fraction * _offdiag_rms(relation),
        _EPS,
    )
    pairwise = np.sqrt(
        np.maximum(squared_distance_field(embedding), 0.0)
    )
    np.fill_diagonal(pairwise, np.inf)
    nearest = pairwise.min(axis=1)
    rng = np.random.default_rng(seed)
    n = len(relation)
    preservation = np.empty(config.probe_replicates)
    dispersion = np.empty(config.probe_replicates)
    for draw in range(config.probe_replicates):
        perturbed = relation + _symmetric_noise(rng, n, probe_sigma)
        probe_embedding = classical_mds(
            gram_from_relation(perturbed, kind="squared_distance"),
            rank,
        )
        aligned = _procrustes_transport(probe_embedding, embedding)
        aligned = aligned[:, : embedding.shape[1]]
        displacement = np.linalg.norm(aligned - embedding, axis=1)
        cross = (
            np.sum(aligned**2, axis=1)[:, None]
            + np.sum(embedding**2, axis=1)[None, :]
            - 2.0 * aligned @ embedding.T
        )
        preservation[draw] = float(np.mean(np.argmin(cross, axis=1) == np.arange(n)))
        dispersion[draw] = float(
            np.median(displacement) / max(np.median(nearest), _EPS)
        )
    stability = float(preservation.mean())
    margin = float(base["spectral_margin"])
    index = float(max(margin, 0.0) * max(stability, 0.0))
    licensed = index >= config.license_threshold
    return {
        **base,
        "status": "R_TO_V_LICENSED" if licensed else "R_TO_V_REFUSED",
        "refusal_reason": None if licensed else "LOW_RIGIDITY",
        "stability": stability,
        "dispersion_ratio": float(np.median(dispersion)),
        "probe_sigma": float(probe_sigma),
        "rigidity_index": index,
    }


def _block_permutation(
    rng: np.random.Generator,
    labels: np.ndarray | None,
    n: int,
) -> np.ndarray:
    permutation = np.arange(n)
    if labels is None:
        return rng.permutation(n)
    for group in np.unique(labels):
        members = np.flatnonzero(labels == group)
        permutation[members] = rng.permutation(members)
    return permutation


def reconstruction_vs_truth(
    relation: np.ndarray,
    truth: np.ndarray,
    *,
    rank: int,
    group_labels: np.ndarray | None = None,
    config: RelationBridgeConfig = RelationBridgeConfig(),
    seed: int = 0,
    kind: str = "squared_distance",
) -> dict[str, Any]:
    """Gauge-aligned reconstruction error against the planted truth.

    Ground-truth label (pre-fixed margin): a world is RECONSTRUCTABLE only
    when the gauge-aligned error beats the median error against
    within-block permuted truth by ``label_margin_ratio`` (0.5 = factor two).
    Blocks are the planted group labels (single block when ``None``), so in
    group-only worlds the permuted baseline equals the observed error by
    construction and the label is non-reconstructable at any noise level:
    coincident coordinates carry no individual identifiability.
    """
    truth = np.asarray(truth, dtype=float)
    n = len(truth)
    if rank >= 1:
        gram = gram_from_relation(np.asarray(relation, float), kind=kind)
        embedding = classical_mds(gram, rank)
    else:
        embedding = np.zeros((n, 1))
    error = gauge_aligned_error(embedding, truth)
    rng = np.random.default_rng(seed)
    permuted = np.empty(config.permutation_draws)
    for draw in range(config.permutation_draws):
        order = _block_permutation(rng, group_labels, n)
        permuted[draw] = gauge_aligned_error(embedding, truth[order])
    baseline = float(np.median(permuted))
    ratio = error / max(baseline, _EPS)
    return {
        "reconstruction_error": float(error),
        "permuted_baseline_median": baseline,
        "error_ratio": float(ratio),
        "reconstructable": bool(ratio < config.label_margin_ratio),
    }


def relation_field_author_auc(
    field_one: np.ndarray,
    field_two: np.ndarray,
    group_labels: np.ndarray | None = None,
) -> dict[str, float]:
    """Author separability across two independent measurements of the field.

    Rows of the relation field are the author profiles.  With group labels
    this reuses ``pairing_auc_metrics`` from the vanishing-individuality
    module, whose ``author_all_auc`` is exactly the trap statistic: it is
    high in group-only worlds although no individual structure exists
    (within-group AUC stays at chance there).
    """
    left = np.asarray(field_one, dtype=float)
    right = np.asarray(field_two, dtype=float)
    if group_labels is not None:
        labels = np.asarray(group_labels)
        counts = np.unique(labels, return_counts=True)[1]
        if len(counts) >= 2 and counts.min() >= 2:
            metrics = pairing_auc_metrics(left, right, labels)
            return {
                "author_all_auc": metrics["author_all_auc"],
                "author_within_group_auc": metrics[
                    "author_within_group_auc"
                ],
                "group_auc": metrics["group_auc"],
            }
    norm_left = left / np.maximum(
        np.linalg.norm(left, axis=1, keepdims=True), _EPS
    )
    norm_right = right / np.maximum(
        np.linalg.norm(right, axis=1, keepdims=True), _EPS
    )
    similarity = norm_left @ norm_right.T
    identity = np.eye(len(similarity), dtype=bool)
    target = np.concatenate([
        np.ones(int(identity.sum()), dtype=int),
        np.zeros(int((~identity).sum()), dtype=int),
    ])
    score = np.concatenate([similarity[identity], similarity[~identity]])
    return {
        "author_all_auc": float(roc_auc_score(target, score)),
        "author_within_group_auc": float("nan"),
        "group_auc": float("nan"),
    }


def planted_relation_world(
    family: str,
    *,
    authors: int = 80,
    latent_rank: int = 3,
    groups: int = 4,
    epsilon: float = 0.0,
    noise: float = 0.1,
    seed: int = 0,
    field_count: int = 2,
) -> dict[str, Any]:
    """Planted latent configurations observed as noisy squared-distance fields.

    Families: ``individual`` (true low-rank per-author coordinates),
    ``group_only`` (every author sits exactly on its group centroid --
    the pairwise analogue of the vanishing-individuality designed null),
    ``mixed`` (group centroids plus within-group-centered individual offsets
    whose RMS size is ``epsilon`` times the centroid spread).  Observation:
    ``R = D2(truth) + noise * rms_offdiag(D2) * symmetric Gaussian`` --
    entries may go negative; the field is a relation object, not a metric.
    """
    rng = np.random.default_rng(seed)
    labels: np.ndarray | None = None
    if family == "individual":
        scales = 0.85 ** np.arange(latent_rank)
        truth = rng.normal(size=(authors, latent_rank)) * scales[None, :]
    elif family in {"group_only", "mixed"}:
        if authors % groups:
            raise ValueError("authors must be divisible by groups")
        labels = np.repeat(np.arange(groups), authors // groups)
        rng.shuffle(labels)
        centroids = rng.normal(size=(groups, latent_rank))
        truth = centroids[labels].astype(float)
        if family == "mixed":
            offsets = rng.normal(size=(authors, latent_rank))
            for group in range(groups):
                mask = labels == group
                offsets[mask] -= offsets[mask].mean(axis=0, keepdims=True)
            spread = float(
                np.sqrt(
                    np.mean(
                        np.sum(
                            (truth - truth.mean(axis=0)) ** 2, axis=1
                        )
                    )
                )
            )
            offset_rms = float(
                np.sqrt(np.mean(np.sum(offsets**2, axis=1)))
            )
            offsets *= epsilon * spread / max(offset_rms, _EPS)
            truth = truth + offsets
    else:
        raise ValueError(f"unsupported planted family: {family}")
    exact = squared_distance_field(truth)
    sigma_abs = noise * _offdiag_rms(exact)
    fields = [
        exact + _symmetric_noise(rng, authors, sigma_abs)
        for _ in range(field_count)
    ]
    return {
        "family": family,
        "truth": truth,
        "group_labels": labels,
        "fields": fields,
        "latent_rank": latent_rank,
        "noise": float(noise),
        "sigma_abs": float(sigma_abs),
        "epsilon": float(epsilon),
    }


def c2_machinery_relation_world(
    world: str = "group_only",
    *,
    epsilon: float = 0.0,
    group_amplitude: float = 1.0,
    seed: int = 0,
    spec: VanishingIndividualitySpec | None = None,
) -> dict[str, Any]:
    """Pairwise fields built from the vanishing-individuality C2 machinery.

    Faithful-analogue construction (stated per plan): the hierarchical C2
    simulator emits per-author binomial response surfaces, not pairwise
    fields.  We convert each half's counts to empirical logits
    ``log((s+.5)/(n-s+.5))`` -- additive in eta -- then condition-center per
    (author, half, family), which removes the author intercept and half
    state exactly in expectation, leaving only the planted operator response
    (group and/or individual).  Each half yields one squared-distance field;
    the truth configuration is the condition-centered planted response
    surface averaged over halves.
    """
    spec = spec or VanishingIndividualitySpec()
    simulated = simulate_hierarchical_c2_world(
        seed=seed,
        world=world,
        epsilon=epsilon,
        group_amplitude=group_amplitude,
        spec=spec,
    )
    successes = np.asarray(
        simulated["data"]["fixed_successes"], dtype=float
    )
    trials = np.asarray(simulated["data"]["fixed_trials"], dtype=float)
    logits = np.log(
        (successes + 0.5) / (trials - successes + 0.5)
    )
    logits -= logits.mean(axis=2, keepdims=True)
    authors = logits.shape[0]
    fields = [
        squared_distance_field(logits[:, half].reshape(authors, -1))
        for half in range(logits.shape[1])
    ]
    response = np.asarray(
        simulated["truth"]["response_surface"], dtype=float
    ).mean(axis=1)
    response -= response.mean(axis=1, keepdims=True)
    truth = response.reshape(authors, -1)
    individual = float(
        np.linalg.norm(simulated["truth"]["individual_response"])
    )
    total = float(
        np.linalg.norm(simulated["truth"]["response_surface"])
    )
    centered = truth - truth.mean(axis=0)
    truth_rank = int(
        np.sum(
            np.linalg.svd(centered, compute_uv=False)
            > 1e-8 * max(np.linalg.norm(centered), 1.0)
        )
    )
    return {
        "family": f"c2_{world}",
        "truth": truth,
        "group_labels": np.asarray(simulated["truth"]["group_labels"]),
        "fields": fields,
        "latent_rank": truth_rank,
        "noise": float("nan"),
        "sigma_abs": float("nan"),
        "epsilon": float(epsilon),
        "individual_share": individual / max(total, _EPS),
    }


def evaluate_relation_world(
    world: dict[str, Any],
    *,
    config: RelationBridgeConfig = RelationBridgeConfig(),
    seed: int = 0,
) -> dict[str, Any]:
    """Full per-world record: index from field one, truth label, author AUC."""
    field = world["fields"][0]
    rigidity = rigidity_report(field, config=config, seed=seed)
    oracle_rank = min(int(world["latent_rank"]), config.rank_cap)
    label = reconstruction_vs_truth(
        field,
        world["truth"],
        rank=oracle_rank,
        group_labels=world["group_labels"],
        config=config,
        seed=seed + 1,
    )
    selected = reconstruction_vs_truth(
        field,
        world["truth"],
        rank=rigidity["selected_rank"],
        group_labels=world["group_labels"],
        config=config,
        seed=seed + 2,
    )
    auc = relation_field_author_auc(
        world["fields"][0],
        world["fields"][1],
        world["group_labels"],
    ) if len(world["fields"]) >= 2 else {
        "author_all_auc": float("nan"),
        "author_within_group_auc": float("nan"),
        "group_auc": float("nan"),
    }
    return {
        "family": world["family"],
        "noise": world["noise"],
        "epsilon": world["epsilon"],
        "authors": len(world["truth"]),
        "oracle_rank": oracle_rank,
        "individual_share": world.get("individual_share", float("nan")),
        **{f"rigidity_{key}": value for key, value in rigidity.items()},
        "e_rec_oracle": label["reconstruction_error"],
        "e_perm_median": label["permuted_baseline_median"],
        "e_ratio_oracle": label["error_ratio"],
        "gt_reconstructable": label["reconstructable"],
        "e_rec_selected": selected["reconstruction_error"],
        "e_ratio_selected": selected["error_ratio"],
        **auc,
    }
