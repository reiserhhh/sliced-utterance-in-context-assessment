"""Planted-world identification tools for the SUICA V8 C2 operator."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any

import numpy as np
from scipy.special import digamma, expit, polygamma
from scipy.spatial.distance import pdist
from scipy.stats import spearmanr

from .joint_process import same_author_auc
from .v8_realtext import auc_contributions


BINARY_MAX_CI_FULL_WIDTH = 4.0
FULL_WHITENING_EPSILON = 1e-6


@dataclass(frozen=True)
class C2SimulationSpec:
    """Frozen dimensions for one shared-condition simulation."""

    discovery_authors: int = 60
    calibration_authors: int = 20
    confirmation_authors: int = 80
    conditions: int = 8
    condition_dimensions: int = 3
    behavior_families: int = 5
    forced_repeats: int = 6
    extra_repeats: int = 96
    noise_sd: float = 1.0
    selection_strength: float = 2.0
    half_state_sd: float = 0.25
    intercept_sd: float = 0.45

    @property
    def authors(self) -> int:
        return (
            self.discovery_authors
            + self.calibration_authors
            + self.confirmation_authors
        )


def factorial_condition_basis(dimensions: int = 3) -> np.ndarray:
    """Return the complete centered {-1,+1} factorial condition basis."""
    values = np.asarray(list(product((-1.0, 1.0), repeat=dimensions)))
    return values / np.sqrt(float(dimensions))


def identification_status(
    basis: np.ndarray,
    opportunity: np.ndarray,
    shared_conditions: np.ndarray,
    *,
    condition_identity_shared: bool,
    minimum_conditions_per_family: int = 6,
    minimum_eigenvalue: float = 0.20,
) -> dict[str, Any]:
    """Check common support and rank before producing any C2 number."""
    basis = np.asarray(basis, dtype=float)
    opportunity = np.asarray(opportunity, dtype=bool)
    shared = np.asarray(shared_conditions, dtype=bool)
    if not condition_identity_shared:
        return {
            "status": "REFUSE_CONDITION_IDENTITY_NOT_SHARED",
            "ready": False,
        }
    family_rows = []
    for family in range(opportunity.shape[1]):
        mask = shared & opportunity[:, family]
        design = basis[mask]
        count = int(mask.sum())
        rank = int(np.linalg.matrix_rank(design)) if count else 0
        minimum = (
            float(np.linalg.eigvalsh(design.T @ design / count).min())
            if count and rank == basis.shape[1]
            else 0.0
        )
        family_rows.append({
            "family": family,
            "shared_conditions": count,
            "rank": rank,
            "minimum_eigenvalue": minimum,
        })
    ready = all(
        row["shared_conditions"] >= minimum_conditions_per_family
        and row["rank"] == basis.shape[1]
        and row["minimum_eigenvalue"] >= minimum_eigenvalue
        for row in family_rows
    )
    return {
        "status": (
            "C2_IDENTIFIABLE"
            if ready
            else "REFUSE_INSUFFICIENT_COMMON_SUPPORT_OR_RANK"
        ),
        "ready": ready,
        "families": family_rows,
    }


def _scale_operator(
    operator: np.ndarray,
    basis: np.ndarray,
    opportunity: np.ndarray,
    *,
    target_snr: float,
    noise_sd: float,
) -> np.ndarray:
    if target_snr <= 0:
        return np.zeros_like(operator)
    surface = np.einsum("ck,uhgk->uhcg", basis, operator)
    mask = opportunity[None, None, :, :]
    variance = float(np.mean(surface[mask.repeat(
        surface.shape[0],
        axis=0,
    ).repeat(surface.shape[1], axis=1)] ** 2))
    target = float(target_snr) * float(noise_sd) ** 2
    return operator * np.sqrt(target / max(variance, 1e-12))


def _scale_binary_operator(
    operator: np.ndarray,
    basis: np.ndarray,
    opportunity: np.ndarray,
    base_eta: np.ndarray,
    *,
    target_information: float,
    repeats: int,
) -> np.ndarray:
    """Scale link-space response by Fisher-information weighted energy."""
    if target_information <= 0:
        return np.zeros_like(operator)
    surface = np.einsum("ck,uhgk->uhcg", basis, operator)
    probability = expit(base_eta)
    information = (
        float(repeats)
        * probability
        * (1.0 - probability)
        * surface**2
    )
    mask = np.broadcast_to(
        opportunity[None, None, :, :],
        information.shape,
    )
    achieved = float(information[mask].mean())
    return operator * np.sqrt(
        float(target_information) / max(achieved, 1e-12)
    )


def _selection_counts(
    rng: np.random.Generator,
    q: np.ndarray,
    basis: np.ndarray,
    *,
    halves: int,
    extra_repeats: int,
    strength: float,
) -> np.ndarray:
    logits = strength * (q @ basis.T)
    logits -= logits.max(axis=1, keepdims=True)
    probabilities = np.exp(logits)
    probabilities /= probabilities.sum(axis=1, keepdims=True)
    counts = np.empty(
        (len(q), halves, len(basis)),
        dtype=int,
    )
    for author in range(len(q)):
        for half in range(halves):
            counts[author, half] = rng.multinomial(
                extra_repeats,
                probabilities[author],
            )
    return counts


def simulate_c2_world(
    *,
    seed: int,
    world: str,
    observation: str,
    snr: float,
    overlap: float,
    spec: C2SimulationSpec,
) -> dict[str, Any]:
    """Generate cell means for one identified or attacked C2 world."""
    if observation not in {"soft", "binary"}:
        raise ValueError(f"unsupported observation world: {observation}")
    rng = np.random.default_rng(seed)
    u, h, c, k, g = (
        spec.authors,
        2,
        spec.conditions,
        spec.condition_dimensions,
        spec.behavior_families,
    )
    basis = factorial_condition_basis(k)
    if len(basis) != c:
        raise ValueError("conditions must equal the full factorial size")
    opportunity = np.ones((c, g), dtype=bool)
    shared_count = int(round(c * float(overlap)))
    shared_conditions = np.arange(c) < shared_count
    condition_identity_shared = world not in {
        "unique_conditions",
        "private_stable_coordinates",
        "half_shuffled_coordinates",
    }
    q = (
        rng.normal(size=(u, k))
        if world in {"c1_only", "joint", "c1_information_imbalance"}
        else np.zeros((u, k))
    )
    intercept = (
        rng.normal(scale=spec.intercept_sd, size=(u, g))
        if world in {
            "intercept_only",
            "shared_c2",
            "joint",
            "unstable_operator",
            "private_stable_coordinates",
            "half_shuffled_coordinates",
            "c1_information_imbalance",
            "extreme_prevalence",
        }
        else np.zeros((u, g))
    )
    base_operator = rng.normal(size=(u, 1, g, k))
    if world == "unstable_operator":
        operator = rng.normal(size=(u, h, g, k))
    else:
        operator = np.repeat(base_operator, h, axis=1)
    if world in {
        "null",
        "c1_only",
        "intercept_only",
        "c1_information_imbalance",
    }:
        operator.fill(0.0)
    if world == "extreme_prevalence":
        prevalence = np.asarray([
            0.02,
            0.10,
            0.50,
            0.90,
            0.98,
            0.02,
            0.10,
            0.90,
        ])
        delta = np.repeat(
            np.log(prevalence / (1.0 - prevalence))[:, None],
            g,
            axis=1,
        )
    else:
        delta = rng.normal(scale=0.35, size=(c, g))
    half_state = rng.normal(
        scale=spec.half_state_sd,
        size=(u, h, g),
    )
    base_eta = (
        delta[None, None, :, :]
        + intercept[:, None, None, :]
        + half_state[:, :, None, :]
    )
    if observation == "binary":
        operator = _scale_binary_operator(
            operator,
            basis,
            opportunity,
            base_eta,
            target_information=snr,
            repeats=spec.forced_repeats,
        )
    else:
        operator = _scale_operator(
            operator,
            basis,
            opportunity,
            target_snr=snr,
            noise_sd=spec.noise_sd,
        )
    response = np.einsum("ck,uhgk->uhcg", basis, operator)
    permutations = np.tile(
        np.arange(c, dtype=int),
        (u, h, 1),
    )
    if world == "private_stable_coordinates":
        for author in range(u):
            permutation = rng.permutation(c)
            permutations[author, 0] = permutation
            permutations[author, 1] = permutation
    elif world in {"half_shuffled_coordinates", "unique_conditions"}:
        for author in range(u):
            for half in range(h):
                permutations[author, half] = rng.permutation(c)
    response_observed = np.take_along_axis(
        response,
        permutations[:, :, :, None],
        axis=2,
    )
    eta = base_eta + response_observed
    extra = _selection_counts(
        rng,
        q,
        basis,
        halves=h,
        extra_repeats=spec.extra_repeats,
        strength=spec.selection_strength,
    )
    fixed_n = np.full(
        (u, h, c, 1),
        spec.forced_repeats,
        dtype=int,
    )
    extra_n = extra[:, :, :, None]
    if observation == "soft":
        fixed_sum = (
            fixed_n * eta
            + rng.normal(
                scale=spec.noise_sd * np.sqrt(fixed_n),
                size=eta.shape,
            )
        )
        extra_sum = (
            extra_n * eta
            + rng.normal(
                scale=spec.noise_sd * np.sqrt(extra_n),
                size=eta.shape,
            )
        )
        expected_mean = eta
        fixed_variance = (
            spec.noise_sd**2 / fixed_n
        ) * np.ones_like(eta)
        all_variance = (
            spec.noise_sd**2
            / (fixed_n + extra_n)
        ) * np.ones_like(eta)
    else:
        probability = expit(np.clip(eta, -8.0, 8.0))
        fixed_sum = rng.binomial(fixed_n, probability)
        extra_sum = rng.binomial(extra_n, probability)
        expected_mean = probability
        fixed_variance = (
            probability * (1.0 - probability) / fixed_n
        )
        all_variance = (
            probability * (1.0 - probability)
            / (fixed_n + extra_n)
        )
    fixed_mean = fixed_sum / fixed_n
    all_n = fixed_n + extra_n
    all_sum = fixed_sum + extra_sum
    all_mean = all_sum / all_n
    observed_mask = (
        shared_conditions[:, None] & opportunity
    )[None, None, :, :]
    fixed_mean = np.where(observed_mask, fixed_mean, np.nan)
    all_mean = np.where(observed_mask, all_mean, np.nan)
    expected_mean = np.where(observed_mask, expected_mean, np.nan)
    fixed_variance = np.where(
        observed_mask,
        fixed_variance,
        np.nan,
    )
    all_variance = np.where(observed_mask, all_variance, np.nan)
    splits = np.asarray(
        ["discovery"] * spec.discovery_authors
        + ["calibration"] * spec.calibration_authors
        + ["confirmation"] * spec.confirmation_authors
    )
    c1_source = extra
    c1 = c1_source / np.maximum(
        c1_source.sum(axis=2, keepdims=True),
        1,
    )
    return {
        "world": world,
        "observation": observation,
        "snr": float(snr),
        "overlap": float(overlap),
        "truth": {
            "q": q,
            "intercept": intercept,
            "operator": operator,
            "response_surface": response,
            "response_surface_observed": response_observed,
        },
        "data": {
            "fixed_mean": fixed_mean,
            "all_mean": all_mean,
            "expected_mean": expected_mean,
            "fixed_variance": fixed_variance,
            "all_variance": all_variance,
            "c1": c1,
            "splits": splits,
            "basis": basis,
            "opportunity": opportunity,
            "shared_conditions": shared_conditions,
            "fixed_successes": (
                fixed_sum if observation == "binary" else None
            ),
            "all_successes": (
                all_sum if observation == "binary" else None
            ),
            "fixed_trials": (
                np.broadcast_to(fixed_n, eta.shape).copy()
                if observation == "binary"
                else None
            ),
            "all_trials": (
                np.broadcast_to(all_n, eta.shape).copy()
                if observation == "binary"
                else None
            ),
        },
        "design": {
            "condition_identity_shared": condition_identity_shared,
        },
    }


def _baseline(
    cell_means: np.ndarray,
    authors: np.ndarray,
) -> np.ndarray:
    values = cell_means[authors]
    count = np.isfinite(values).sum(axis=(0, 1))
    total = np.nansum(values, axis=(0, 1))
    return np.divide(
        total,
        count,
        out=np.full_like(total, np.nan, dtype=float),
        where=count > 0,
    )


def _baseline_variance(
    cell_variance: np.ndarray,
    authors: np.ndarray,
) -> np.ndarray:
    """Propagate independent discovery-cell variance into the baseline mean."""
    values = cell_variance[authors]
    count = np.isfinite(values).sum(axis=(0, 1))
    total = np.nansum(values, axis=(0, 1))
    return np.divide(
        total,
        count**2,
        out=np.full_like(total, np.nan, dtype=float),
        where=count > 0,
    )


def _estimate_given_baseline(
    cell_means: np.ndarray,
    baseline: np.ndarray,
    basis: np.ndarray,
    opportunity: np.ndarray,
    shared_conditions: np.ndarray,
    *,
    ridge: float,
) -> tuple[np.ndarray, np.ndarray]:
    u, h, c, g = cell_means.shape
    surface = np.zeros((u, h, c, g), dtype=float)
    intercept = np.zeros((u, h, g), dtype=float)
    penalty = np.diag([0.0] + [float(ridge)] * basis.shape[1])
    for family in range(g):
        mask = shared_conditions & opportunity[:, family]
        design = np.column_stack([
            np.ones(int(mask.sum())),
            basis[mask],
        ])
        projector = np.linalg.solve(
            design.T @ design + penalty,
            design.T,
        )
        values = cell_means[:, :, mask, family] - baseline[
            mask,
            family,
        ][None, None, :]
        coefficients = values @ projector.T
        intercept[:, :, family] = coefficients[:, :, 0]
        surface[:, :, mask, family] = np.einsum(
            "ck,uhk->uhc",
            basis[mask],
            coefficients[:, :, 1:],
        )
    feature_mask = (
        shared_conditions[:, None] & opportunity
    ).reshape(-1)
    return (
        surface.reshape(u, h, -1)[:, :, feature_mask],
        intercept,
    )


def _response_standard_errors(
    cell_variance: np.ndarray,
    baseline_variance: np.ndarray,
    basis: np.ndarray,
    opportunity: np.ndarray,
    shared_conditions: np.ndarray,
    *,
    ridge: float,
) -> np.ndarray:
    """Propagate cell-mean uncertainty to the fitted response surface."""
    u, h, c, g = cell_variance.shape
    response_variance = np.zeros((u, h, c, g), dtype=float)
    penalty = np.diag([0.0] + [float(ridge)] * basis.shape[1])
    for family in range(g):
        mask = shared_conditions & opportunity[:, family]
        design = np.column_stack([
            np.ones(int(mask.sum())),
            basis[mask],
        ])
        projector = np.linalg.solve(
            design.T @ design + penalty,
            design.T,
        )
        response_map = basis[mask] @ projector[1:, :]
        residual_variance = (
            cell_variance[:, :, mask, family]
            + baseline_variance[mask, family][None, None, :]
        )
        response_variance[:, :, mask, family] = np.einsum(
            "ij,uhj,ij->uhi",
            response_map,
            residual_variance,
            response_map,
        )
    feature_mask = (
        shared_conditions[:, None] & opportunity
    ).reshape(-1)
    return np.sqrt(
        np.maximum(
            response_variance.reshape(u, h, -1)[:, :, feature_mask],
            0.0,
        )
    )


def _fit_binary_condition_offsets(
    successes: np.ndarray,
    trials: np.ndarray,
    authors: np.ndarray,
    opportunity: np.ndarray,
    shared_conditions: np.ndarray,
    *,
    maximum_iterations: int = 80,
    tolerance: float = 1e-9,
) -> tuple[np.ndarray, np.ndarray]:
    """Fit discovery-only condition offsets with author-half intercepts."""
    successes = np.asarray(successes, dtype=float)[authors]
    trials = np.asarray(trials, dtype=float)[authors]
    conditions = successes.shape[2]
    families = successes.shape[3]
    offsets = np.full((conditions, families), np.nan, dtype=float)
    offset_covariance = np.zeros(
        (families, conditions, conditions),
        dtype=float,
    )
    for family in range(families):
        mask = shared_conditions & opportunity[:, family]
        k = successes[:, :, mask, family]
        n = trials[:, :, mask, family]
        pooled_success = k.sum(axis=2)
        pooled_trials = n.sum(axis=2)
        author_intercept = np.log(
            (pooled_success + 0.5)
            / np.maximum(pooled_trials - pooled_success + 0.5, 1e-12)
        )
        condition_offset = np.zeros(int(mask.sum()), dtype=float)
        for _ in range(maximum_iterations):
            eta = (
                author_intercept[:, :, None]
                + condition_offset[None, None, :]
            )
            probability = expit(np.clip(eta, -20.0, 20.0))
            author_score = np.sum(k - n * probability, axis=2)
            author_info = np.sum(
                n * probability * (1.0 - probability),
                axis=2,
            )
            author_step = np.divide(
                author_score,
                author_info,
                out=np.zeros_like(author_score),
                where=author_info > 1e-10,
            )
            author_step = np.clip(author_step, -2.0, 2.0)
            author_intercept += author_step
            eta = (
                author_intercept[:, :, None]
                + condition_offset[None, None, :]
            )
            probability = expit(np.clip(eta, -20.0, 20.0))
            condition_score = np.sum(
                k - n * probability,
                axis=(0, 1),
            )
            condition_info = np.sum(
                n * probability * (1.0 - probability),
                axis=(0, 1),
            )
            condition_step = np.divide(
                condition_score,
                condition_info,
                out=np.zeros_like(condition_score),
                where=condition_info > 1e-10,
            )
            condition_step = np.clip(condition_step, -2.0, 2.0)
            condition_offset += condition_step
            center = float(condition_offset.mean())
            condition_offset -= center
            author_intercept += center
            if max(
                float(np.max(np.abs(author_step))),
                float(np.max(np.abs(condition_step))),
            ) < tolerance:
                break
        eta = (
            author_intercept[:, :, None]
            + condition_offset[None, None, :]
        )
        probability = expit(np.clip(eta, -20.0, 20.0))
        weight = n * probability * (1.0 - probability)
        contrast = _helmert_contrasts(int(mask.sum()))
        author_info = weight.sum(axis=2).reshape(-1)
        author_condition = np.einsum(
            "ahc,cr->ahr",
            weight,
            contrast,
        ).reshape(-1, contrast.shape[1])
        condition_info = np.einsum(
            "cr,ahc,cs->rs",
            contrast,
            weight,
            contrast,
        )
        schur = condition_info - np.einsum(
            "ar,a,as->rs",
            author_condition,
            1.0 / np.maximum(author_info, 1e-10),
            author_condition,
        )
        schur += np.eye(schur.shape[0]) * 1e-8
        condition_covariance = (
            contrast @ np.linalg.inv(schur) @ contrast.T
        )
        offsets[mask, family] = condition_offset
        offset_covariance[family][np.ix_(mask, mask)] = (
            condition_covariance
        )
    return offsets, offset_covariance


def _helmert_contrasts(size: int) -> np.ndarray:
    """Return deterministic orthonormal contrasts orthogonal to the mean."""
    if size < 2:
        return np.empty((size, 0), dtype=float)
    output = np.zeros((size, size - 1), dtype=float)
    for column in range(size - 1):
        count = column + 1
        scale = np.sqrt(float(count * (count + 1)))
        output[:count, column] = 1.0 / scale
        output[count, column] = -float(count) / scale
    return output


def _estimate_binary_given_offsets(
    successes: np.ndarray,
    trials: np.ndarray,
    offsets: np.ndarray,
    offset_covariance: np.ndarray,
    basis: np.ndarray,
    opportunity: np.ndarray,
    shared_conditions: np.ndarray,
    *,
    ridge: float,
    bias_reduction: bool = False,
    maximum_iterations: int = 60,
    tolerance: float = 1e-9,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    """Fit author-half link operators with discovery-frozen offsets."""
    successes = np.asarray(successes, dtype=float)
    trials = np.asarray(trials, dtype=float)
    u, h, c, g = successes.shape
    surface = np.zeros((u, h, c, g), dtype=float)
    response_variance = np.zeros_like(surface)
    response_covariance = np.zeros(
        (u, h, c * g, c * g),
        dtype=float,
    )
    intercept = np.zeros((u, h, g), dtype=float)
    maximum_condition = np.zeros((u, h, g), dtype=float)
    maximum_coefficient = np.zeros((u, h, g), dtype=float)
    penalty = np.diag([0.0] + [float(ridge)] * basis.shape[1])
    for family in range(g):
        mask = shared_conditions & opportunity[:, family]
        design = np.column_stack([
            np.ones(int(mask.sum())),
            basis[mask],
        ])
        k = successes[:, :, mask, family]
        n = trials[:, :, mask, family]
        offset = offsets[mask, family]
        beta = np.zeros((u, h, design.shape[1]), dtype=float)
        pooled_success = k.sum(axis=2)
        pooled_trials = n.sum(axis=2)
        beta[:, :, 0] = np.log(
            (pooled_success + 0.5)
            / np.maximum(pooled_trials - pooled_success + 0.5, 1e-12)
        )
        information = None
        probability = None
        for _ in range(maximum_iterations):
            eta = (
                offset[None, None, :]
                + np.einsum("cp,uhp->uhc", design, beta)
            )
            probability = expit(np.clip(eta, -20.0, 20.0))
            weight = n * probability * (1.0 - probability)
            information = np.einsum(
                "ci,uhc,cj->uhij",
                design,
                weight,
                design,
            ) + penalty[None, None, :, :]
            information += (
                np.eye(design.shape[1])[None, None, :, :] * 1e-8
            )
            residual = k - n * probability
            if bias_reduction:
                inverse_information = np.linalg.inv(information)
                leverage = np.einsum(
                    "ci,uhij,cj,uhc->uhc",
                    design,
                    inverse_information,
                    design,
                    weight,
                )
                residual = residual + leverage * (0.5 - probability)
            score = np.einsum(
                "cp,uhc->uhp",
                design,
                residual,
            ) - np.einsum("pq,uhq->uhp", penalty, beta)
            step = np.linalg.solve(
                information,
                score[..., None],
            )[..., 0]
            step = np.clip(step, -2.0, 2.0)
            beta += step
            if float(np.max(np.abs(step))) < tolerance:
                break
        if information is None or probability is None:
            raise RuntimeError("binary operator fit did not initialize")
        maximum_condition[:, :, family] = np.linalg.cond(information)
        maximum_coefficient[:, :, family] = np.max(
            np.abs(beta),
            axis=2,
        )
        intercept[:, :, family] = beta[:, :, 0]
        surface[:, :, mask, family] = np.einsum(
            "ck,uhk->uhc",
            basis[mask],
            beta[:, :, 1:],
        )
        inverse = np.linalg.inv(information)
        weight = n * probability * (1.0 - probability)
        score_map = np.einsum(
            "uhij,cj,uhc->uhic",
            inverse,
            design,
            weight,
        )
        unpenalized_info = np.einsum(
            "ci,uhc,cj->uhij",
            design,
            weight,
            design,
        )
        sampling_covariance = np.einsum(
            "uhij,uhjk,uhlk->uhil",
            inverse,
            unpenalized_info,
            inverse,
        )
        contrasts = np.column_stack([
            np.zeros(int(mask.sum())),
            basis[mask],
        ])
        sampling_variance = np.einsum(
            "ci,uhij,cj->uhc",
            contrasts,
            sampling_covariance,
            contrasts,
        )
        offset_response_map = np.einsum(
            "ci,uhij->uhcj",
            contrasts,
            score_map,
        )
        condition_covariance = offset_covariance[family][
            np.ix_(mask, mask)
        ]
        propagated_offset = np.einsum(
            "uhci,ij,uhcj->uhc",
            offset_response_map,
            condition_covariance,
            offset_response_map,
        )
        response_variance[:, :, mask, family] = (
            sampling_variance + propagated_offset
        )
        sampling_surface_covariance = np.einsum(
            "ci,uhij,dj->uhcd",
            contrasts,
            sampling_covariance,
            contrasts,
        )
        offset_surface_covariance = np.einsum(
            "uhci,ij,uhdj->uhcd",
            offset_response_map,
            condition_covariance,
            offset_response_map,
        )
        family_covariance = (
            sampling_surface_covariance + offset_surface_covariance
        )
        feature_indices = np.flatnonzero(mask) * g + family
        for left_position, left_index in enumerate(feature_indices):
            for right_position, right_index in enumerate(feature_indices):
                response_covariance[
                    :,
                    :,
                    left_index,
                    right_index,
                ] = family_covariance[
                    :,
                    :,
                    left_position,
                    right_position,
                ]
    feature_mask = (
        shared_conditions[:, None] & opportunity
    ).reshape(-1)
    selected_se = np.sqrt(
        np.maximum(
            response_variance.reshape(u, h, -1)[:, :, feature_mask],
            0.0,
        )
    )
    selected_covariance = response_covariance[
        :,
        :,
        feature_mask,
        :,
    ][:, :, :, feature_mask]
    invalid = (
        ~np.isfinite(maximum_condition)
        | ~np.isfinite(maximum_coefficient)
        | (maximum_condition > 1e6)
        | (maximum_coefficient > 12.0)
    )
    maximum_ci_width = 3.92 * np.max(selected_se, axis=2)
    author_half_invalid = (
        invalid.any(axis=2)
        | (maximum_ci_width > BINARY_MAX_CI_FULL_WIDTH)
    )
    accepted_condition = maximum_condition[~invalid]
    return (
        surface.reshape(u, h, -1)[:, :, feature_mask],
        intercept,
        selected_se,
        {
            "maximum_information_condition_number": float(
                np.nanmax(maximum_condition)
            ),
            "maximum_accepted_information_condition_number": (
                float(np.nanmax(accepted_condition))
                if accepted_condition.size
                else float("inf")
            ),
            "maximum_absolute_coefficient": float(
                np.nanmax(maximum_coefficient)
            ),
            "author_half_refusal_rate": float(
                author_half_invalid.mean()
            ),
            "author_refusal_rate": float(
                author_half_invalid.any(axis=1).mean()
            ),
            "author_half_invalid": author_half_invalid,
            "information_condition_number": maximum_condition,
            "absolute_coefficient": maximum_coefficient,
            "maximum_ci_full_width": maximum_ci_width,
            "response_covariance": selected_covariance,
        },
    )


def _full_covariance_whiten(
    surface: np.ndarray,
    covariance: np.ndarray,
    *,
    epsilon: float = FULL_WHITENING_EPSILON,
) -> np.ndarray:
    """Whiten each response profile with its complete estimated covariance."""
    surface = np.asarray(surface, dtype=float)
    covariance = np.asarray(covariance, dtype=float)
    output = np.empty_like(surface)
    for author in range(surface.shape[0]):
        for half in range(surface.shape[1]):
            matrix = (
                covariance[author, half]
                + np.eye(surface.shape[2]) * float(epsilon)
            )
            values, vectors = np.linalg.eigh(matrix)
            inverse_root = vectors @ np.diag(
                1.0 / np.sqrt(np.maximum(values, float(epsilon)))
            ) @ vectors.T
            output[author, half] = inverse_root @ surface[author, half]
    return output


def _moment_observations(
    successes: np.ndarray,
    trials: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return finite-sample log-odds moments and trigamma variance."""
    successes = np.asarray(successes, dtype=float)
    trials = np.asarray(trials, dtype=float)
    failures = trials - successes
    moment = digamma(successes + 0.5) - digamma(failures + 0.5)
    variance = (
        polygamma(1, successes + 0.5)
        + polygamma(1, failures + 0.5)
    )
    return moment, variance


def _fit_moment_condition_offsets(
    moment: np.ndarray,
    variance: np.ndarray,
    authors: np.ndarray,
    opportunity: np.ndarray,
    shared_conditions: np.ndarray,
    *,
    maximum_iterations: int = 100,
    tolerance: float = 1e-10,
) -> np.ndarray:
    """Fit an independent finite-moment two-way discovery baseline."""
    moment = np.asarray(moment, dtype=float)[authors]
    variance = np.asarray(variance, dtype=float)[authors]
    c, g = moment.shape[2], moment.shape[3]
    offsets = np.full((c, g), np.nan, dtype=float)
    for family in range(g):
        mask = shared_conditions & opportunity[:, family]
        values = moment[:, :, mask, family]
        weights = 1.0 / np.maximum(variance[:, :, mask, family], 1e-12)
        author_intercept = np.average(values, axis=2, weights=weights)
        condition_offset = np.zeros(int(mask.sum()), dtype=float)
        for _ in range(maximum_iterations):
            previous = condition_offset.copy()
            author_intercept = np.sum(
                weights
                * (values - condition_offset[None, None, :]),
                axis=2,
            ) / np.sum(weights, axis=2)
            condition_offset = np.sum(
                weights
                * (values - author_intercept[:, :, None]),
                axis=(0, 1),
            ) / np.sum(weights, axis=(0, 1))
            center = float(condition_offset.mean())
            condition_offset -= center
            author_intercept += center
            if float(np.max(np.abs(condition_offset - previous))) < tolerance:
                break
        offsets[mask, family] = condition_offset
    return offsets


def _estimate_moment_given_offsets(
    moment: np.ndarray,
    variance: np.ndarray,
    offsets: np.ndarray,
    basis: np.ndarray,
    opportunity: np.ndarray,
    shared_conditions: np.ndarray,
    *,
    ridge: float,
) -> np.ndarray:
    """Fit a finite-moment WLS response surface as a sensitivity estimator."""
    moment = np.asarray(moment, dtype=float)
    variance = np.asarray(variance, dtype=float)
    u, h, c, g = moment.shape
    surface = np.zeros((u, h, c, g), dtype=float)
    penalty = np.diag([0.0] + [float(ridge)] * basis.shape[1])
    for family in range(g):
        mask = shared_conditions & opportunity[:, family]
        design = np.column_stack([
            np.ones(int(mask.sum())),
            basis[mask],
        ])
        weights = 1.0 / np.maximum(
            variance[:, :, mask, family],
            1e-12,
        )
        values = (
            moment[:, :, mask, family]
            - offsets[mask, family][None, None, :]
        )
        information = np.einsum(
            "ci,uhc,cj->uhij",
            design,
            weights,
            design,
        ) + penalty[None, None, :, :]
        score = np.einsum(
            "ci,uhc,uhc->uhi",
            design,
            weights,
            values,
        )
        coefficients = np.linalg.solve(
            information,
            score[..., None],
        )[..., 0]
        surface[:, :, mask, family] = np.einsum(
            "ck,uhk->uhc",
            basis[mask],
            coefficients[:, :, 1:],
        )
    feature_mask = (
        shared_conditions[:, None] & opportunity
    ).reshape(-1)
    return surface.reshape(u, h, -1)[:, :, feature_mask]


def _cross_fitted_discovery(
    cell_means: np.ndarray,
    discovery: np.ndarray,
    basis: np.ndarray,
    opportunity: np.ndarray,
    shared_conditions: np.ndarray,
    *,
    ridge: float,
) -> np.ndarray:
    output = None
    for fold in range(5):
        target = discovery[np.arange(len(discovery)) % 5 == fold]
        train = np.setdiff1d(discovery, target, assume_unique=True)
        baseline = _baseline(cell_means, train)
        surface, _ = _estimate_given_baseline(
            cell_means[target],
            baseline,
            basis,
            opportunity,
            shared_conditions,
            ridge=ridge,
        )
        if output is None:
            output = np.empty(
                (len(discovery), 2, surface.shape[2]),
                dtype=float,
            )
        positions = np.flatnonzero(np.isin(discovery, target))
        output[positions] = surface
    if output is None:
        raise RuntimeError("no discovery folds were estimated")
    return output


def _cross_fitted_discovery_binary(
    successes: np.ndarray,
    trials: np.ndarray,
    discovery: np.ndarray,
    basis: np.ndarray,
    opportunity: np.ndarray,
    shared_conditions: np.ndarray,
    *,
    ridge: float,
) -> tuple[np.ndarray, np.ndarray]:
    output = None
    output_se = None
    for fold in range(5):
        target = discovery[np.arange(len(discovery)) % 5 == fold]
        train = np.setdiff1d(discovery, target, assume_unique=True)
        offsets, offset_variance = _fit_binary_condition_offsets(
            successes,
            trials,
            train,
            opportunity,
            shared_conditions,
        )
        surface, _, response_se, _ = _estimate_binary_given_offsets(
            successes[target],
            trials[target],
            offsets,
            offset_variance,
            basis,
            opportunity,
            shared_conditions,
            ridge=ridge,
        )
        if output is None:
            output = np.empty(
                (len(discovery), 2, surface.shape[2]),
                dtype=float,
            )
            output_se = np.empty_like(output)
        positions = np.flatnonzero(np.isin(discovery, target))
        output[positions] = surface
        output_se[positions] = response_se
    if output is None or output_se is None:
        raise RuntimeError("no binary discovery folds were estimated")
    return output, output_se


def _fit_c2_binary(
    world: dict[str, Any],
    *,
    cell_mean_key: str,
    ridge_candidates: tuple[float, ...],
    identification: dict[str, Any],
) -> dict[str, Any]:
    """Fit the primary C2 operator on the binomial link scale."""
    data = world["data"]
    count_keys = {
        "fixed_mean": ("fixed_successes", "fixed_trials"),
        "all_mean": ("all_successes", "all_trials"),
    }
    if cell_mean_key not in count_keys:
        raise ValueError(
            f"no binomial count mapping for {cell_mean_key!r}"
        )
    success_key, trial_key = count_keys[cell_mean_key]
    successes = np.asarray(data[success_key], dtype=float)
    trials = np.asarray(data[trial_key], dtype=float)
    splits = np.asarray(data["splits"])
    discovery = np.flatnonzero(splits == "discovery")
    calibration = np.flatnonzero(splits == "calibration")
    offsets, offset_variance = _fit_binary_condition_offsets(
        successes,
        trials,
        discovery,
        data["opportunity"],
        data["shared_conditions"],
    )
    candidates = []
    cached = {}
    for ridge in ridge_candidates:
        cross_fitted, cross_fitted_se = _cross_fitted_discovery_binary(
            successes,
            trials,
            discovery,
            data["basis"],
            data["opportunity"],
            data["shared_conditions"],
            ridge=float(ridge),
        )
        center = cross_fitted.reshape(-1, cross_fitted.shape[2]).mean(
            axis=0
        )
        scale = cross_fitted.reshape(-1, cross_fitted.shape[2]).std(
            axis=0
        )
        scale[scale < 1e-8] = 1.0
        surface, intercept, response_se, diagnostics = (
            _estimate_binary_given_offsets(
                successes,
                trials,
                offsets,
                offset_variance,
                data["basis"],
                data["opportunity"],
                data["shared_conditions"],
                ridge=float(ridge),
            )
        )
        raw_standardized = (surface - center[None, None, :]) / scale[
            None,
            None,
            :,
        ]
        cross_studentized = np.divide(
            cross_fitted,
            cross_fitted_se,
            out=np.zeros_like(cross_fitted),
            where=cross_fitted_se > 1e-10,
        )
        studentized_center = cross_studentized.reshape(
            -1,
            cross_studentized.shape[2],
        ).mean(axis=0)
        studentized_scale = cross_studentized.reshape(
            -1,
            cross_studentized.shape[2],
        ).std(axis=0)
        studentized_scale[studentized_scale < 1e-8] = 1.0
        studentized = np.divide(
            surface,
            response_se,
            out=np.zeros_like(surface),
            where=response_se > 1e-10,
        )
        standardized = (
            studentized - studentized_center[None, None, :]
        ) / studentized_scale[None, None, :]
        auc = same_author_auc(
            raw_standardized[calibration, 0],
            raw_standardized[calibration, 1],
        )
        candidates.append({
            "ridge": float(ridge),
            "calibration_auc": float(auc),
        })
        cached[float(ridge)] = {
            "surface": surface,
            "intercept": intercept,
            "response_se": response_se,
            "diagnostics": diagnostics,
            "standardized": raw_standardized,
            "studentized_standardized": standardized,
            "raw_standardized": raw_standardized,
            "center": center,
            "scale": scale,
            "studentized_center": studentized_center,
            "studentized_scale": studentized_scale,
        }
    selected = sorted(
        candidates,
        key=lambda row: (-row["calibration_auc"], row["ridge"]),
    )[0]
    chosen = cached[selected["ridge"]]
    log_se = np.log(np.maximum(chosen["response_se"], 1e-10))
    log_se_center = log_se[discovery].reshape(
        -1,
        log_se.shape[2],
    ).mean(axis=0)
    log_se_scale = log_se[discovery].reshape(
        -1,
        log_se.shape[2],
    ).std(axis=0)
    log_se_scale[log_se_scale < 1e-8] = 1.0
    se_only_standardized = (
        log_se - log_se_center[None, None, :]
    ) / log_se_scale[None, None, :]
    full_whitened = _full_covariance_whiten(
        chosen["surface"],
        chosen["diagnostics"]["response_covariance"],
    )
    full_whitened_center = full_whitened[discovery].reshape(
        -1,
        full_whitened.shape[2],
    ).mean(axis=0)
    full_whitened_scale = full_whitened[discovery].reshape(
        -1,
        full_whitened.shape[2],
    ).std(axis=0)
    full_whitened_scale[full_whitened_scale < 1e-8] = 1.0
    full_whitened_standardized = (
        full_whitened - full_whitened_center[None, None, :]
    ) / full_whitened_scale[None, None, :]
    (
        inference_surface,
        inference_intercept,
        inference_response_se,
        inference_diagnostics,
    ) = (
        _estimate_binary_given_offsets(
            successes,
            trials,
            offsets,
            offset_variance,
            data["basis"],
            data["opportunity"],
            data["shared_conditions"],
            ridge=0.0,
            bias_reduction=True,
        )
    )
    inference_center = inference_surface[discovery].reshape(
        -1,
        inference_surface.shape[2],
    ).mean(axis=0)
    inference_scale = inference_surface[discovery].reshape(
        -1,
        inference_surface.shape[2],
    ).std(axis=0)
    inference_scale[inference_scale < 1e-8] = 1.0
    inference_standardized = (
        inference_surface - inference_center[None, None, :]
    ) / inference_scale[None, None, :]
    mask = (
        data["shared_conditions"][:, None]
        & data["opportunity"]
    ).reshape(-1)
    oracle_surface = world["truth"]["response_surface_observed"].reshape(
        len(splits),
        2,
        -1,
    )[:, :, mask]
    moment, moment_variance = _moment_observations(
        successes,
        trials,
    )
    moment_offsets = _fit_moment_condition_offsets(
        moment,
        moment_variance,
        discovery,
        data["opportunity"],
        data["shared_conditions"],
    )
    moment_surface = _estimate_moment_given_offsets(
        moment,
        moment_variance,
        moment_offsets,
        data["basis"],
        data["opportunity"],
        data["shared_conditions"],
        ridge=0.0,
    )
    moment_center = moment_surface[discovery].reshape(
        -1,
        moment_surface.shape[2],
    ).mean(axis=0)
    moment_scale = moment_surface[discovery].reshape(
        -1,
        moment_surface.shape[2],
    ).std(axis=0)
    moment_scale[moment_scale < 1e-8] = 1.0
    moment_standardized = (
        moment_surface - moment_center[None, None, :]
    ) / moment_scale[None, None, :]
    probability_baseline = _baseline(
        np.asarray(data[cell_mean_key], dtype=float),
        discovery,
    )
    incidence_surface, _ = _estimate_given_baseline(
        np.asarray(data[cell_mean_key], dtype=float),
        probability_baseline,
        data["basis"],
        data["opportunity"],
        data["shared_conditions"],
        ridge=float(selected["ridge"]),
    )
    incidence_center = incidence_surface[discovery].reshape(
        -1,
        incidence_surface.shape[2],
    ).mean(axis=0)
    incidence_scale = incidence_surface[discovery].reshape(
        -1,
        incidence_surface.shape[2],
    ).std(axis=0)
    incidence_scale[incidence_scale < 1e-8] = 1.0
    incidence_standardized = (
        incidence_surface - incidence_center[None, None, :]
    ) / incidence_scale[None, None, :]
    return {
        "status": "C2_ESTIMATE_READY",
        "estimand": "C2_LOGIT_OPERATOR",
        "identification": identification,
        "selected_ridge": selected["ridge"],
        "calibration_candidates": candidates,
        "oracle_surface": oracle_surface,
        "inference_surface": inference_surface,
        "inference_intercept": inference_intercept,
        "inference_response_se": inference_response_se,
        "inference_standardized": inference_standardized,
        "score_studentized_standardized": chosen[
            "studentized_standardized"
        ],
        "se_only_standardized": se_only_standardized,
        "full_whitened_standardized": full_whitened_standardized,
        "inference_diagnostics": inference_diagnostics,
        "inference_method": "FIRTH_BINOMIAL_LINK",
        "binary_offsets": offsets,
        "binary_offset_covariance": offset_variance,
        "binary_cell_mean_key": cell_mean_key,
        "moment_surface": moment_surface,
        "moment_standardized": moment_standardized,
        "incidence_surface": incidence_surface,
        "incidence_standardized": incidence_standardized,
        **chosen,
    }


def _inflate_surface(
    surface: np.ndarray,
    opportunity: np.ndarray,
    shared_conditions: np.ndarray,
) -> np.ndarray:
    """Restore a flattened supported surface to condition-by-family form."""
    u, h, _ = surface.shape
    c, g = opportunity.shape
    output = np.zeros((u, h, c, g), dtype=float)
    mask = (
        shared_conditions[:, None] & opportunity
    ).reshape(-1)
    flattened = output.reshape(u, h, -1)
    flattened[:, :, mask] = surface
    return output


def _binary_parametric_bootstrap_coverage(
    world: dict[str, Any],
    estimate: dict[str, Any],
    confirmation: np.ndarray,
    *,
    seed: int,
    draws: int,
    authors: int,
) -> float:
    """Audit link-operator intervals with discovery and target resampling."""
    if draws <= 0 or authors <= 0:
        return float("nan")
    data = world["data"]
    count_keys = {
        "fixed_mean": ("fixed_successes", "fixed_trials"),
        "all_mean": ("all_successes", "all_trials"),
    }
    success_key, trial_key = count_keys[
        str(estimate["binary_cell_mean_key"])
    ]
    successes = np.asarray(data[success_key], dtype=float)
    trials = np.asarray(data[trial_key], dtype=float)
    discovery = np.flatnonzero(np.asarray(data["splits"]) == "discovery")
    rng = np.random.default_rng(seed)
    selected = np.sort(
        rng.choice(
            confirmation,
            size=min(int(authors), len(confirmation)),
            replace=False,
        )
    )
    fitted_surface = _inflate_surface(
        estimate["inference_surface"][selected],
        data["opportunity"],
        data["shared_conditions"],
    )
    fitted_eta = (
        estimate["binary_offsets"][None, None, :, :]
        + estimate["inference_intercept"][selected, :, None, :]
        + fitted_surface
    )
    fitted_probability = expit(np.clip(fitted_eta, -20.0, 20.0))
    bootstrap_surfaces = []
    bootstrap_standard_errors = []
    for _ in range(int(draws)):
        resampled_discovery = rng.choice(
            discovery,
            size=len(discovery),
            replace=True,
        )
        offsets, offset_covariance = _fit_binary_condition_offsets(
            successes,
            trials,
            resampled_discovery,
            data["opportunity"],
            data["shared_conditions"],
        )
        generated = rng.binomial(
            trials[selected].astype(int),
            fitted_probability,
        )
        surface, _, standard_error, _ = _estimate_binary_given_offsets(
            generated,
            trials[selected],
            offsets,
            offset_covariance,
            data["basis"],
            data["opportunity"],
            data["shared_conditions"],
            ridge=0.0,
            bias_reduction=True,
        )
        bootstrap_surfaces.append(surface)
        bootstrap_standard_errors.append(standard_error)
    samples = np.asarray(bootstrap_surfaces)
    bootstrap_se = np.asarray(bootstrap_standard_errors)
    original = estimate["inference_surface"][selected]
    original_se = estimate["inference_response_se"][selected]
    studentized = np.divide(
        samples - original[None, :, :, :],
        bootstrap_se,
        out=np.zeros_like(samples),
        where=bootstrap_se > 1e-10,
    )
    lower = original - np.quantile(
        studentized,
        0.975,
        axis=0,
    ) * original_se
    upper = original - np.quantile(
        studentized,
        0.025,
        axis=0,
    ) * original_se
    oracle = estimate["oracle_surface"][selected]
    return float(((oracle >= lower) & (oracle <= upper)).mean())


def fit_c2_pipeline(
    world: dict[str, Any],
    *,
    cell_mean_key: str,
    ridge_candidates: tuple[float, ...],
) -> dict[str, Any]:
    """Select ridge on calibration and freeze discovery-only scaling."""
    data = world["data"]
    status = identification_status(
        data["basis"],
        data["opportunity"],
        data["shared_conditions"],
        condition_identity_shared=bool(
            world["design"]["condition_identity_shared"]
        ),
    )
    if not status["ready"]:
        return {
            "status": status["status"],
            "identification": status,
        }
    if world["observation"] == "binary":
        return _fit_c2_binary(
            world,
            cell_mean_key=cell_mean_key,
            ridge_candidates=ridge_candidates,
            identification=status,
        )
    cell_means = np.asarray(data[cell_mean_key], dtype=float)
    variance_key = {
        "fixed_mean": "fixed_variance",
        "all_mean": "all_variance",
    }.get(cell_mean_key)
    if variance_key is None:
        raise ValueError(
            f"no cell-variance mapping for estimator input {cell_mean_key!r}"
        )
    cell_variance = np.asarray(data[variance_key], dtype=float)
    expected_mean = np.asarray(data["expected_mean"], dtype=float)
    splits = np.asarray(data["splits"])
    discovery = np.flatnonzero(splits == "discovery")
    calibration = np.flatnonzero(splits == "calibration")
    baseline = _baseline(cell_means, discovery)
    baseline_variance = _baseline_variance(
        cell_variance,
        discovery,
    )
    candidates = []
    cached = {}
    for ridge in ridge_candidates:
        cross_fitted = _cross_fitted_discovery(
            cell_means,
            discovery,
            data["basis"],
            data["opportunity"],
            data["shared_conditions"],
            ridge=float(ridge),
        )
        center = cross_fitted.reshape(-1, cross_fitted.shape[2]).mean(
            axis=0
        )
        scale = cross_fitted.reshape(-1, cross_fitted.shape[2]).std(
            axis=0
        )
        scale[scale < 1e-8] = 1.0
        surface, intercept = _estimate_given_baseline(
            cell_means,
            baseline,
            data["basis"],
            data["opportunity"],
            data["shared_conditions"],
            ridge=float(ridge),
        )
        standardized = (surface - center[None, None, :]) / scale[
            None,
            None,
            :,
        ]
        auc = same_author_auc(
            standardized[calibration, 0],
            standardized[calibration, 1],
        )
        candidates.append({
            "ridge": float(ridge),
            "calibration_auc": float(auc),
        })
        cached[float(ridge)] = {
            "surface": surface,
            "intercept": intercept,
            "standardized": standardized,
        }
    selected = sorted(
        candidates,
        key=lambda row: (-row["calibration_auc"], row["ridge"]),
    )[0]
    chosen = cached[selected["ridge"]]
    oracle_baseline = _baseline(expected_mean, discovery)
    oracle_surface, _ = _estimate_given_baseline(
        expected_mean,
        oracle_baseline,
        data["basis"],
        data["opportunity"],
        data["shared_conditions"],
        ridge=float(selected["ridge"]),
    )
    response_se = _response_standard_errors(
        cell_variance,
        baseline_variance,
        data["basis"],
        data["opportunity"],
        data["shared_conditions"],
        ridge=float(selected["ridge"]),
    )
    return {
        "status": "C2_ESTIMATE_READY",
        "estimand": "C2_LINEAR_OPERATOR",
        "identification": status,
        "selected_ridge": selected["ridge"],
        "calibration_candidates": candidates,
        "oracle_surface": oracle_surface,
        "response_se": response_se,
        **chosen,
    }


def _pairing_test(
    left: np.ndarray,
    right: np.ndarray,
    *,
    seed: int,
    permutations: int,
) -> tuple[float, float]:
    a = left - left.mean(axis=0, keepdims=True)
    b = right - right.mean(axis=0, keepdims=True)
    similarity = a @ b.T / max(a.shape[1], 1)
    observed = float(np.diag(similarity).mean())
    rng = np.random.default_rng(seed)
    permuted = np.vstack([
        rng.permutation(len(right))
        for _ in range(permutations)
    ])
    null = similarity[
        np.arange(len(right))[None, :],
        permuted,
    ].mean(axis=1)
    p_value = float(
        (1 + np.sum(null >= observed)) / (permutations + 1)
    )
    return observed, p_value


def _auc_interval(
    left: np.ndarray,
    right: np.ndarray,
    *,
    seed: int,
    draws: int,
) -> tuple[float, float, float]:
    contributions = auc_contributions(left, right)
    rng = np.random.default_rng(seed)
    samples = contributions[
        rng.integers(
            0,
            len(contributions),
            size=(draws, len(contributions)),
        )
    ].mean(axis=1)
    return (
        float(contributions.mean()),
        float(np.quantile(samples, 0.025)),
        float(np.quantile(samples, 0.975)),
    )


def _cross_validated_q_r2(
    q: np.ndarray,
    response: np.ndarray,
) -> float:
    if np.std(q) < 1e-12:
        return 0.0
    prediction = np.zeros_like(response)
    for fold in range(5):
        test = np.arange(len(q)) % 5 == fold
        train = ~test
        design = np.column_stack([np.ones(train.sum()), q[train]])
        coefficients = np.linalg.lstsq(
            design,
            response[train],
            rcond=None,
        )[0]
        prediction[test] = np.column_stack([
            np.ones(test.sum()),
            q[test],
        ]) @ coefficients
    denominator = float(np.sum(
        (response - response.mean(axis=0, keepdims=True)) ** 2
    ))
    return float(
        1.0
        - np.sum((response - prediction) ** 2)
        / max(denominator, 1e-12)
    )


def evaluate_c2_pipeline(
    world: dict[str, Any],
    estimate: dict[str, Any],
    *,
    seed: int,
    bootstrap_draws: int,
    permutations: int,
    binary_ci_bootstrap_draws: int = 0,
    binary_ci_bootstrap_authors: int = 0,
) -> dict[str, Any]:
    """Evaluate stable response recovery on confirmation authors only."""
    if estimate["status"] != "C2_ESTIMATE_READY":
        return {
            "status": estimate["status"],
            "c2_numeric_output": False,
        }
    splits = np.asarray(world["data"]["splits"])
    confirmation = np.flatnonzero(splits == "confirmation")
    left = estimate["standardized"][confirmation, 0]
    right = estimate["standardized"][confirmation, 1]
    auc, lower, upper = _auc_interval(
        left,
        right,
        seed=seed,
        draws=bootstrap_draws,
    )
    statistic, p_value = _pairing_test(
        left,
        right,
        seed=seed + 100_000,
        permutations=permutations,
    )
    c1 = world["data"]["c1"][confirmation]
    c1_auc = same_author_auc(c1[:, 0], c1[:, 1])
    intercept = estimate["intercept"][confirmation]
    intercept_auc = same_author_auc(
        intercept[:, 0],
        intercept[:, 1],
    )
    estimated_halves = estimate.get(
        "inference_surface",
        estimate["surface"],
    )[confirmation]
    oracle_halves = estimate["oracle_surface"][confirmation]
    standard_error = estimate.get(
        "inference_response_se",
        estimate["response_se"],
    )[confirmation]
    inference_author_half_valid = np.ones(
        estimated_halves.shape[:2],
        dtype=bool,
    )
    if "inference_diagnostics" in estimate:
        inference_author_half_valid = ~estimate[
            "inference_diagnostics"
        ]["author_half_invalid"][confirmation]
    valid_ci = (
        np.isfinite(estimated_halves)
        & np.isfinite(oracle_halves)
        & np.isfinite(standard_error)
        & inference_author_half_valid[:, :, None]
    )
    ci_covered = (
        np.abs(estimated_halves - oracle_halves)
        <= 1.96 * standard_error
    )
    pointwise_coverage = (
        float(ci_covered[valid_ci].mean())
        if valid_ci.any()
        else float("nan")
    )
    standardized_bias = np.divide(
        estimated_halves - oracle_halves,
        standard_error,
        out=np.zeros_like(estimated_halves),
        where=standard_error > 1e-10,
    )
    standardized_bias_masked = np.where(
        valid_ci,
        standardized_bias,
        np.nan,
    )
    if valid_ci.any():
        feature_bias = np.nanmean(
            standardized_bias_masked,
            axis=(0, 1),
        )
        mean_standardized_bias = float(
            np.nanmean(np.abs(feature_bias))
        )
    else:
        mean_standardized_bias = float("nan")
    accepted_author = inference_author_half_valid.all(axis=1)
    estimated = estimated_halves[accepted_author].mean(axis=1)
    oracle = oracle_halves[accepted_author].mean(axis=1)
    numerator = np.sum(estimated * oracle, axis=1)
    denominator = (
        np.linalg.norm(estimated, axis=1)
        * np.linalg.norm(oracle, axis=1)
    )
    valid = denominator > 1e-12
    recovery_slope = (
        float(
            np.sum(estimated * oracle)
            / max(np.sum(oracle**2), 1e-12)
        )
        if np.sum(oracle**2) > 1e-12
        else float("nan")
    )
    recovery_slope_bias = (
        float(abs(recovery_slope - 1.0))
        if np.isfinite(recovery_slope)
        else float("nan")
    )
    cosine = (
        float(np.median(numerator[valid] / denominator[valid]))
        if valid.any()
        else 0.0
    )
    if valid.any():
        scale = float(
            np.sum(estimated[valid] * oracle[valid])
            / max(np.sum(estimated[valid] ** 2), 1e-12)
        )
        nrmse = float(
            np.sqrt(np.mean((scale * estimated[valid] - oracle[valid]) ** 2))
            / max(np.std(oracle[valid]), 1e-12)
        )
        distance_r = float(
            spearmanr(
                pdist(oracle[valid], metric="euclidean"),
                pdist(estimated[valid], metric="euclidean"),
            ).statistic
        )
    else:
        nrmse = float("nan")
        distance_r = float("nan")
    q_r2 = (
        _cross_validated_q_r2(
            world["truth"]["q"][confirmation][accepted_author],
            estimated,
        )
        if accepted_author.sum() >= 5
        else float("nan")
    )
    moment_auc = float("nan")
    moment_cosine = float("nan")
    incidence_auc = float("nan")
    inference_auc = float("nan")
    auc_gap = float("nan")
    cosine_gap = float("nan")
    binary_bootstrap_coverage = float("nan")
    studentized_score_auc = float("nan")
    studentized_pairing_p = float("nan")
    raw_score_auc = float("nan")
    raw_pairing_p = float("nan")
    se_only_auc = float("nan")
    se_only_pairing_p = float("nan")
    permuted_numerator_auc = float("nan")
    full_whitened_auc = float("nan")
    full_whitened_pairing_p = float("nan")
    inference_refusal_rate = float("nan")
    inference_maximum_condition = float("nan")
    if "moment_surface" in estimate:
        studentized_left = estimate[
            "score_studentized_standardized"
        ][confirmation, 0]
        studentized_right = estimate[
            "score_studentized_standardized"
        ][confirmation, 1]
        studentized_score_auc = float(same_author_auc(
            studentized_left,
            studentized_right,
        ))
        _, studentized_pairing_p = _pairing_test(
            studentized_left,
            studentized_right,
            seed=seed + 200_000,
            permutations=permutations,
        )
        raw_left = estimate["raw_standardized"][confirmation, 0]
        raw_right = estimate["raw_standardized"][confirmation, 1]
        raw_score_auc = float(same_author_auc(raw_left, raw_right))
        _, raw_pairing_p = _pairing_test(
            raw_left,
            raw_right,
            seed=seed + 250_000,
            permutations=permutations,
        )
        se_left = estimate["se_only_standardized"][confirmation, 0]
        se_right = estimate["se_only_standardized"][confirmation, 1]
        se_only_auc = float(same_author_auc(se_left, se_right))
        _, se_only_pairing_p = _pairing_test(
            se_left,
            se_right,
            seed=seed + 260_000,
            permutations=permutations,
        )
        rng = np.random.default_rng(seed + 270_000)
        permuted_surface = estimate["surface"][confirmation].copy()
        for half in range(permuted_surface.shape[1]):
            permuted_surface[:, half] = permuted_surface[
                rng.permutation(len(permuted_surface)),
                half,
            ]
        permuted_studentized = np.divide(
            permuted_surface,
            estimate["response_se"][confirmation],
            out=np.zeros_like(permuted_surface),
            where=estimate["response_se"][confirmation] > 1e-10,
        )
        permuted_standardized = (
            permuted_studentized
            - estimate["studentized_center"][None, None, :]
        ) / estimate["studentized_scale"][None, None, :]
        permuted_numerator_auc = float(same_author_auc(
            permuted_standardized[:, 0],
            permuted_standardized[:, 1],
        ))
        full_left = estimate["full_whitened_standardized"][
            confirmation,
            0,
        ]
        full_right = estimate["full_whitened_standardized"][
            confirmation,
            1,
        ]
        full_whitened_auc = float(same_author_auc(
            full_left,
            full_right,
        ))
        _, full_whitened_pairing_p = _pairing_test(
            full_left,
            full_right,
            seed=seed + 280_000,
            permutations=permutations,
        )
        if accepted_author.sum() >= 4:
            inference_auc = float(same_author_auc(
                estimate["inference_standardized"][
                    confirmation[accepted_author],
                    0,
                ],
                estimate["inference_standardized"][
                    confirmation[accepted_author],
                    1,
                ],
            ))
            moment_left = estimate["moment_standardized"][
                confirmation[accepted_author],
                0,
            ]
            moment_right = estimate["moment_standardized"][
                confirmation[accepted_author],
                1,
            ]
            moment_auc = float(same_author_auc(moment_left, moment_right))
            moment_estimated = estimate["moment_surface"][
                confirmation[accepted_author]
            ].mean(axis=1)
            moment_numerator = np.sum(moment_estimated * oracle, axis=1)
            moment_denominator = (
                np.linalg.norm(moment_estimated, axis=1)
                * np.linalg.norm(oracle, axis=1)
            )
            moment_valid = moment_denominator > 1e-12
            moment_cosine = (
                float(np.median(
                    moment_numerator[moment_valid]
                    / moment_denominator[moment_valid]
                ))
                if moment_valid.any()
                else 0.0
            )
        incidence_auc = float(same_author_auc(
            estimate["incidence_standardized"][confirmation, 0],
            estimate["incidence_standardized"][confirmation, 1],
        ))
        if accepted_author.sum() >= 4:
            auc_gap = float(abs(inference_auc - moment_auc))
            cosine_gap = float(abs(cosine - moment_cosine))
            binary_bootstrap_coverage = (
                _binary_parametric_bootstrap_coverage(
                    world,
                    estimate,
                    confirmation[accepted_author],
                    seed=seed + 300_000,
                    draws=binary_ci_bootstrap_draws,
                    authors=binary_ci_bootstrap_authors,
                )
            )
        diagnostics = estimate["inference_diagnostics"]
        inference_refusal_rate = float(
            diagnostics["author_half_invalid"][confirmation].mean()
        )
        accepted_conditions = np.where(
            diagnostics["author_half_invalid"][confirmation, :, None],
            np.nan,
            diagnostics["information_condition_number"][confirmation],
        )
        inference_maximum_condition = (
            float(np.nanmax(accepted_conditions))
            if np.isfinite(accepted_conditions).any()
            else float("nan")
        )
    return {
        "status": "C2_EVALUATED",
        "c2_numeric_output": True,
        "same_author_auc": auc,
        "auc_ci_lower": lower,
        "auc_ci_upper": upper,
        "pairing_statistic": statistic,
        "pairing_permutation_p": p_value,
        "c1_same_author_auc": float(c1_auc),
        "intercept_same_author_auc": float(intercept_auc),
        "response_surface_cosine": cosine,
        "response_distance_spearman": distance_r,
        "response_nrmse": nrmse,
        "response_pointwise_ci_coverage": pointwise_coverage,
        "response_mean_standardized_bias": mean_standardized_bias,
        "response_recovery_slope": recovery_slope,
        "response_recovery_slope_bias": recovery_slope_bias,
        "q_to_response_cv_r2": q_r2,
        "moment_same_author_auc": moment_auc,
        "inference_same_author_auc": inference_auc,
        "moment_response_surface_cosine": moment_cosine,
        "probability_incidence_same_author_auc": incidence_auc,
        "binary_estimator_auc_gap": auc_gap,
        "binary_estimator_cosine_gap": cosine_gap,
        "binary_parametric_ci_coverage": binary_bootstrap_coverage,
        "studentized_score_same_author_auc": studentized_score_auc,
        "studentized_score_pairing_p": studentized_pairing_p,
        "raw_score_same_author_auc": raw_score_auc,
        "raw_score_pairing_p": raw_pairing_p,
        "se_only_same_author_auc": se_only_auc,
        "se_only_pairing_p": se_only_pairing_p,
        "permuted_numerator_same_author_auc": permuted_numerator_auc,
        "full_whitened_same_author_auc": full_whitened_auc,
        "full_whitened_pairing_p": full_whitened_pairing_p,
        "inference_author_half_refusal_rate": inference_refusal_rate,
        "inference_maximum_information_condition_number": (
            inference_maximum_condition
        ),
        "selected_ridge": float(estimate["selected_ridge"]),
    }
