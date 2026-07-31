"""Synthetic L4-to-L5 reference-frame operators for the SUICA foundation.

The module starts from anonymous, facet-indexed technical vectors. It does not
read text or psychological labels. Its purpose is to test when a frozen
reference population, target facet measure, operator, support rule, and error
model license a comparable technical measurement object.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np

from .v8_external_zero_uncertainty import (
    apply_external_zero_denoiser,
    cross_validated_external_rank_selection,
    fit_external_zero_denoiser,
)


@dataclass(frozen=True)
class L45ReferenceSpec:
    """Balanced synthetic design for one L4-to-L5 experiment."""

    reference_authors: int = 192
    fit_authors: int = 96
    test_authors: int = 64
    facets: int = 16
    occasions: int = 4
    dimensions: int = 6
    response_rank: int = 3
    events_per_facet: int = 8
    author_scale: float = 0.45
    response_scale: float = 0.24
    occasion_scale: float = 0.14
    event_scale: float = 0.60
    covariance_ridge: float = 1e-4


def _rms_scale(values: np.ndarray, target: float) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    rms = float(np.sqrt(np.mean(array**2)))
    if target <= 0.0 or rms <= 1e-12:
        return np.zeros_like(array)
    return array * (float(target) / rms)


def _groups(
    rng: np.random.Generator,
    n_authors: int,
    positive_rate: float,
) -> np.ndarray:
    n_positive = int(round(float(positive_rate) * int(n_authors)))
    labels = np.concatenate([
        np.zeros(int(n_authors) - n_positive, dtype=int),
        np.ones(n_positive, dtype=int),
    ])
    return labels[rng.permutation(len(labels))]


def _event_noise(
    rng: np.random.Generator,
    shape: tuple[int, ...],
    *,
    noise_mode: str,
) -> np.ndarray:
    if noise_mode == "gaussian":
        return rng.normal(size=shape)
    if noise_mode == "heteroskedastic_t5":
        return rng.standard_t(5, size=shape) / np.sqrt(5.0 / 3.0)
    raise ValueError(f"unsupported noise mode: {noise_mode}")


def _panel(
    rng: np.random.Generator,
    *,
    n_authors: int,
    group_rate: float,
    role: str,
    world: str,
    shared: np.ndarray,
    group_effect: np.ndarray,
    response_basis: np.ndarray,
    spec: L45ReferenceSpec,
    noise_mode: str,
) -> dict[str, Any]:
    groups = _groups(rng, n_authors, group_rate)
    author = _rms_scale(
        rng.normal(size=(n_authors, spec.dimensions)),
        spec.author_scale,
    )
    response_score = rng.normal(size=(n_authors, spec.response_rank))
    response = _rms_scale(
        np.einsum("nr,frd->nfd", response_score, response_basis),
        spec.response_scale,
    )
    stable_field = (
        shared[None]
        + group_effect[groups]
        + author[:, None]
        + response
    )

    occasions = 1 if world == "person_occasion_alias" else spec.occasions
    occasion = _rms_scale(
        rng.normal(size=(n_authors, occasions, spec.dimensions)),
        spec.occasion_scale,
    )
    independent_occasions = world != "correlated_replicate_shock"
    if not independent_occasions:
        occasion = np.repeat(occasion[:, :1], occasions, axis=1)

    counts = np.full(
        (n_authors, occasions, spec.facets),
        spec.events_per_facet,
        dtype=int,
    )
    if world == "composition_shift" and role == "test":
        multiplier = np.exp(np.linspace(-1.25, 1.25, spec.facets))
        multiplier /= multiplier.mean()
        tilted = np.maximum(
            1,
            np.rint(spec.events_per_facet * multiplier),
        ).astype(int)
        counts[...] = tilted[None, None]
    if world == "support_hole" and role == "test":
        counts[..., -max(2, spec.facets // 4) :] = 0

    author_norm = np.linalg.norm(author, axis=1)
    author_norm /= max(float(np.median(author_norm)), 1e-8)
    scale = np.full(
        (n_authors, occasions, spec.facets, 1),
        spec.event_scale,
        dtype=float,
    )
    if world == "informative_precision":
        scale *= (0.45 + 0.75 * author_norm)[:, None, None, None]
    standard_error = np.divide(
        scale,
        np.sqrt(counts[..., None]),
        out=np.full_like(scale, np.nan),
        where=counts[..., None] > 0,
    )
    noise = _event_noise(
        rng,
        (n_authors, occasions, spec.facets, spec.dimensions),
        noise_mode=noise_mode,
    )
    means = (
        stable_field[:, None]
        + occasion[:, :, None]
        + standard_error * noise
    )
    means[counts == 0] = np.nan

    degrees = np.maximum(counts - 1, 1)
    sample_variance = (
        scale**2
        * rng.chisquare(degrees[..., None])
        / degrees[..., None]
    )
    sample_variance[counts == 0] = np.nan
    return {
        "role": role,
        "means": means,
        "sample_variance": sample_variance,
        "counts": counts,
        "groups": groups,
        "stable_field": stable_field,
        "facet_provenance": world != "choice_response_alias",
        "independent_occasions": independent_occasions,
    }


def simulate_l45_world(
    *,
    seed: int,
    world: str,
    noise_mode: str,
    spec: L45ReferenceSpec,
) -> dict[str, Any]:
    """Generate one registered L4 technical-vector world."""
    supported = {
        "clean",
        "composition_shift",
        "reference_mixture",
        "support_hole",
        "aq_gauge_alias",
        "choice_response_alias",
        "person_occasion_alias",
        "operator_kernel",
        "correlated_replicate_shock",
        "informative_precision",
    }
    if world not in supported:
        raise ValueError(f"unsupported L45 world: {world}")
    streams = np.random.SeedSequence(seed).spawn(7)
    (
        rng_global,
        rng_reference,
        rng_fit,
        rng_test,
        rng_operator,
        rng_alias,
        _,
    ) = (np.random.default_rng(stream) for stream in streams)

    shared = _rms_scale(
        rng_global.normal(size=(spec.facets, spec.dimensions)),
        0.30,
    )
    group_global = _rms_scale(
        rng_global.normal(size=spec.dimensions),
        0.22,
    )
    group_variation = rng_global.normal(
        size=(spec.facets, spec.dimensions),
    )
    group_variation -= group_variation.mean(axis=0, keepdims=True)
    group_direction = (
        group_global[None]
        + _rms_scale(group_variation, 0.08)
    )
    group_effect = np.stack([-group_direction, group_direction])
    response_basis = rng_global.normal(
        size=(spec.facets, spec.response_rank, spec.dimensions)
    )
    response_basis -= response_basis.mean(axis=0, keepdims=True)
    target_group_weights = np.asarray([0.5, 0.5], dtype=float)
    reference_rate = 0.82 if world == "reference_mixture" else 0.5

    reference = _panel(
        rng_reference,
        n_authors=spec.reference_authors,
        group_rate=reference_rate,
        role="reference",
        world=world,
        shared=shared,
        group_effect=group_effect,
        response_basis=response_basis,
        spec=spec,
        noise_mode=noise_mode,
    )
    fit = _panel(
        rng_fit,
        n_authors=spec.fit_authors,
        group_rate=0.5,
        role="fit",
        world=world,
        shared=shared,
        group_effect=group_effect,
        response_basis=response_basis,
        spec=spec,
        noise_mode=noise_mode,
    )
    test = _panel(
        rng_test,
        n_authors=spec.test_authors,
        group_rate=0.5,
        role="test",
        world=world,
        shared=shared,
        group_effect=group_effect,
        response_basis=response_basis,
        spec=spec,
        noise_mode=noise_mode,
    )

    operator, _ = np.linalg.qr(
        rng_operator.normal(size=(spec.dimensions, spec.dimensions))
    )
    if world == "operator_kernel":
        operator = operator @ np.diag(
            [1.0] * (spec.dimensions - 2) + [0.0, 0.0]
        )
    lambda_facet = np.full(spec.facets, 1.0 / spec.facets)
    true_reference_center = np.einsum(
        "f,g,gfd->d",
        lambda_facet,
        target_group_weights,
        group_effect,
    ) + np.einsum("f,fd->d", lambda_facet, shared)

    alias_shift = rng_alias.normal(size=(spec.test_authors, spec.dimensions))
    alias_a = alias_shift
    alias_q = -np.repeat(alias_shift[:, None], spec.facets, axis=1)
    alias_identity_error = float(
        np.max(np.abs(alias_a[:, None] + alias_q))
    )
    return {
        "world": world,
        "noise_mode": noise_mode,
        "reference": reference,
        "fit": fit,
        "test": test,
        "lambda_facet": lambda_facet,
        "target_group_weights": target_group_weights,
        "true_reference_center": true_reference_center,
        "operator_matrix": operator,
        "operator_rank": int(np.linalg.matrix_rank(operator)),
        "alias_identity_error": alias_identity_error,
        "cause_attribution_allowed": False,
        "spec": spec,
    }


def _panel_subset(panel: dict[str, Any], indices: np.ndarray) -> dict[str, Any]:
    selected = np.asarray(indices, dtype=int)
    result = dict(panel)
    n_authors = len(panel["groups"])
    for key, value in panel.items():
        if (
            isinstance(value, np.ndarray)
            and value.ndim > 0
            and value.shape[0] == n_authors
        ):
            result[key] = value[selected].copy()
    return result


def aggregate_to_common_facet(
    panel: dict[str, Any],
    lambda_facet: np.ndarray,
) -> dict[str, Any]:
    """Standardize observed facet composition to a frozen target measure."""
    if not bool(panel.get("facet_provenance", False)):
        return {
            "status": "REFUSE_CHOICE_RESPONSE_ALIAS_NO_FACET_PROVENANCE",
        }
    means = np.asarray(panel["means"], dtype=float)
    counts = np.asarray(panel["counts"], dtype=float)
    target = np.asarray(lambda_facet, dtype=float)
    target /= target.sum()
    required = target > 0
    supported = np.all(counts[..., required] > 0, axis=-1)
    if not supported.all():
        coverage = np.sum(
            target[None, None] * (counts > 0),
            axis=-1,
        )
        return {
            "status": "REFUSE_NONOVERLAP",
            "minimum_support_mass": float(np.min(coverage)),
        }
    standardized = np.einsum("f,aofd->aod", target, means)
    observed_probability = counts / counts.sum(axis=-1, keepdims=True)
    naive = np.einsum("aof,aofd->aod", observed_probability, means)
    ess_ratio = 1.0 / np.sum(
        target[None, None] ** 2 / observed_probability,
        axis=-1,
    )
    return {
        "status": "COMMON_FACET_READY",
        "standardized": standardized,
        "naive": naive,
        "minimum_ess_ratio": float(np.min(ess_ratio)),
        "median_ess_ratio": float(np.median(ess_ratio)),
    }


def _weighted_mean_covariance(
    values: np.ndarray,
    weights: np.ndarray,
    ridge: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    normalized = np.asarray(weights, dtype=float)
    normalized /= normalized.sum()
    center = np.einsum("n,nd->d", normalized, values)
    centered = values - center
    denominator = max(1.0 - float(np.sum(normalized**2)), 1e-8)
    covariance = np.einsum(
        "n,ni,nj->ij",
        normalized,
        centered,
        centered,
    ) / denominator
    floor = max(
        float(np.trace(covariance)) / max(covariance.shape[0], 1)
        * float(ridge),
        1e-8,
    )
    covariance = 0.5 * (covariance + covariance.T)
    covariance += floor * np.eye(covariance.shape[0])
    eigenvalue, eigenvector = np.linalg.eigh(covariance)
    eigenvalue = np.maximum(eigenvalue, floor)
    inverse_sqrt = (
        eigenvector
        @ np.diag(eigenvalue ** -0.5)
        @ eigenvector.T
    )
    return center, covariance, inverse_sqrt


def fit_reference_frame(
    panel: dict[str, Any],
    *,
    lambda_facet: np.ndarray,
    target_group_weights: np.ndarray,
    ridge: float,
    weighted: bool = True,
) -> dict[str, Any]:
    """Fit a population- and facet-declared reference chart."""
    aggregated = aggregate_to_common_facet(panel, lambda_facet)
    if aggregated["status"] != "COMMON_FACET_READY":
        return {"status": aggregated["status"], "aggregate": aggregated}
    groups = np.asarray(panel["groups"], dtype=int)
    group_counts = np.bincount(
        groups,
        minlength=len(target_group_weights),
    )
    if np.any(
        (np.asarray(target_group_weights) > 0)
        & (group_counts == 0)
    ):
        return {
            "status": "REFUSE_REFERENCE_GROUP_NONPOSITIVITY",
            "group_counts": group_counts.tolist(),
        }
    author_values = np.asarray(aggregated["standardized"]).mean(axis=1)
    if weighted:
        weights = np.asarray(target_group_weights)[groups] / group_counts[groups]
    else:
        weights = np.ones(len(groups), dtype=float)
    center, covariance, inverse_sqrt = _weighted_mean_covariance(
        author_values,
        weights,
        ridge,
    )
    return {
        "status": "REFERENCE_FRAME_READY",
        "center": center,
        "covariance": covariance,
        "inverse_sqrt": inverse_sqrt,
        "group_counts": group_counts,
        "weighted": bool(weighted),
        "aggregate": aggregated,
    }


def _candidate_loss(
    left: np.ndarray,
    right: np.ndarray,
    *,
    rank: int | None,
    soft: bool,
    folds: int,
    seed: int,
) -> np.ndarray:
    order = np.random.default_rng(seed).permutation(len(left))
    partitions = np.array_split(order, folds)
    losses = []
    zero = np.zeros(left.shape[1], dtype=float)
    for valid in partitions:
        train = np.setdiff1d(order, valid, assume_unique=True)
        fitted = fit_external_zero_denoiser(
            left[train],
            right[train],
            external_zero=zero,
            rank=rank,
            soft=soft,
        )
        predict_right = apply_external_zero_denoiser(left[valid], fitted)
        predict_left = apply_external_zero_denoiser(right[valid], fitted)
        numerator = (
            np.sum((right[valid] - predict_right) ** 2)
            + np.sum((left[valid] - predict_left) ** 2)
        )
        denominator = (
            np.sum(right[valid] ** 2)
            + np.sum(left[valid] ** 2)
        )
        losses.append(float(numerator / max(denominator, 1e-12)))
    return np.asarray(losses, dtype=float)


def fit_l45_pipeline(
    world: dict[str, Any],
    *,
    candidates: Iterable[int],
    folds: int,
    seed: int,
    soft_noninferiority_margin: float,
) -> dict[str, Any]:
    """Fit a frozen reference chart and observable-only stable scorer."""
    fit_panel = world["fit"]
    if not bool(fit_panel.get("independent_occasions", False)):
        return {"status": "REFUSE_CORRELATED_OR_UNDECLARED_OCCASIONS"}
    if np.asarray(fit_panel["means"]).shape[1] < 2:
        return {"status": "REFUSE_PERSON_OCCASION_ALIAS"}
    frame = fit_reference_frame(
        world["reference"],
        lambda_facet=world["lambda_facet"],
        target_group_weights=world["target_group_weights"],
        ridge=world["spec"].covariance_ridge,
    )
    if frame["status"] != "REFERENCE_FRAME_READY":
        return {"status": frame["status"], "reference_frame": frame}
    aggregate = aggregate_to_common_facet(
        fit_panel,
        world["lambda_facet"],
    )
    if aggregate["status"] != "COMMON_FACET_READY":
        return {"status": aggregate["status"], "reference_frame": frame}
    values = (
        np.asarray(aggregate["standardized"]) - frame["center"]
    ) @ frame["inverse_sqrt"]
    left = values[:, ::2].mean(axis=1)
    right = values[:, 1::2].mean(axis=1)
    ranks = sorted(
        set(
            int(value)
            for value in candidates
            if 0 <= int(value) <= values.shape[-1]
        )
    )
    selected_rank, rank_table = cross_validated_external_rank_selection(
        left,
        right,
        external_zero=np.zeros(values.shape[-1]),
        candidates=ranks,
        folds=folds,
        seed=seed,
    )
    hard_loss = _candidate_loss(
        left,
        right,
        rank=selected_rank,
        soft=False,
        folds=folds,
        seed=seed,
    )
    soft_loss = _candidate_loss(
        left,
        right,
        rank=None,
        soft=True,
        folds=folds,
        seed=seed,
    )
    difference = soft_loss - hard_loss
    se_difference = (
        float(np.std(difference, ddof=1) / np.sqrt(len(difference)))
        if len(difference) > 1
        else 0.0
    )
    soft_allowed = float(soft_loss.mean()) <= (
        float(hard_loss.mean())
        + max(float(soft_noninferiority_margin), se_difference)
    )
    estimator = "soft_conserving" if soft_allowed else "hard_selected"
    denoiser = fit_external_zero_denoiser(
        left,
        right,
        external_zero=np.zeros(values.shape[-1]),
        rank=None if soft_allowed else selected_rank,
        soft=soft_allowed,
    )
    return {
        "status": "L45_PIPELINE_READY",
        "reference_frame": frame,
        "denoiser": denoiser,
        "estimator": estimator,
        "selected_rank": int(selected_rank),
        "hard_cv_loss": float(hard_loss.mean()),
        "soft_cv_loss": float(soft_loss.mean()),
        "soft_minus_hard_se": se_difference,
        "rank_table": rank_table,
    }


def score_panel(
    panel: dict[str, Any],
    world: dict[str, Any],
    pipeline: dict[str, Any],
) -> dict[str, Any]:
    """Apply one frozen L5 candidate using observable panel fields only."""
    if pipeline["status"] != "L45_PIPELINE_READY":
        return {"status": pipeline["status"]}
    aggregate = aggregate_to_common_facet(
        panel,
        world["lambda_facet"],
    )
    if aggregate["status"] != "COMMON_FACET_READY":
        return {"status": aggregate["status"], "aggregate": aggregate}
    frame = pipeline["reference_frame"]
    standardized = (
        np.asarray(aggregate["standardized"]) - frame["center"]
    ) @ frame["inverse_sqrt"]
    per_occasion = apply_external_zero_denoiser(
        standardized.reshape(-1, standardized.shape[-1]),
        pipeline["denoiser"],
    ).reshape(standardized.shape)
    point = per_occasion.mean(axis=1)
    left = per_occasion[:, ::2].mean(axis=1)
    right = per_occasion[:, 1::2].mean(axis=1)
    return {
        "status": "L5_CANDIDATE_SCORE_READY",
        "point": point,
        "left": left,
        "right": right,
        "aggregate": aggregate,
        "cause_attribution_allowed": False,
    }


def oracle_score_target(
    panel: dict[str, Any],
    world: dict[str, Any],
    pipeline: dict[str, Any],
) -> np.ndarray:
    """Return generator truth for post-fit synthetic audit only."""
    if pipeline["status"] != "L45_PIPELINE_READY":
        raise ValueError("oracle target requires a fitted L45 pipeline")
    if "stable_field" not in panel:
        raise ValueError("oracle target is unavailable outside synthetic worlds")
    frame = pipeline["reference_frame"]
    stable = np.einsum(
        "f,afd->ad",
        world["lambda_facet"],
        np.asarray(panel["stable_field"]),
    )
    stable_z = (stable - frame["center"]) @ frame["inverse_sqrt"]
    return apply_external_zero_denoiser(
        stable_z,
        pipeline["denoiser"],
    )


def resample_observed_panel(
    panel: dict[str, Any],
    rng: np.random.Generator,
    *,
    indices: np.ndarray | None = None,
    lambda_facet: np.ndarray | None = None,
    resample_occasions: bool = True,
) -> dict[str, Any]:
    """Bootstrap authors, occasions, and event means from observables.

    Occasion resampling is centered within author and uses a finite-occasion
    variance correction. Event noise is then drawn from the observed
    within-event variance. This keeps the two channels separate instead of
    treating the realized occasion effects as fixed.
    """
    source = panel if indices is None else _panel_subset(panel, indices)
    result = dict(source)
    means = np.asarray(source["means"], dtype=float)
    counts = np.asarray(source["counts"], dtype=float)
    variance = np.asarray(source["sample_variance"], dtype=float)
    n_authors, occasions, facets, dimensions = means.shape
    if lambda_facet is None:
        target = np.full(facets, 1.0 / facets)
    else:
        target = np.asarray(lambda_facet, dtype=float)
        target /= target.sum()

    if resample_occasions and occasions >= 2:
        index = rng.integers(
            0,
            occasions,
            size=(n_authors, occasions),
        )
        count_index = np.broadcast_to(
            index[:, :, None],
            counts.shape,
        )
        variance_index = np.broadcast_to(
            index[:, :, None, None],
            variance.shape,
        )
        draw_counts = np.take_along_axis(
            counts,
            count_index,
            axis=1,
        )
        draw_variance = np.take_along_axis(
            variance,
            variance_index,
            axis=1,
        )
        facet_center = np.nanmean(means, axis=1)
        observed_mass = np.einsum(
            "f,aof->ao",
            target,
            np.isfinite(means).all(axis=-1),
        )
        occasion_profile = np.divide(
            np.einsum(
                "f,aofd->aod",
                target,
                np.nan_to_num(means),
            ),
            observed_mass[..., None],
            out=np.zeros((n_authors, occasions, dimensions)),
            where=observed_mass[..., None] > 0,
        )
        occasion_deviation = (
            occasion_profile
            - occasion_profile.mean(axis=1, keepdims=True)
        )
        deviation_index = np.broadcast_to(
            index[:, :, None],
            occasion_deviation.shape,
        )
        sampled_deviation = np.take_along_axis(
            occasion_deviation,
            deviation_index,
            axis=1,
        )
        sampled_deviation *= np.sqrt(occasions / (occasions - 1.0))
        center = facet_center[:, None] + sampled_deviation[:, :, None]
    else:
        draw_counts = counts
        draw_variance = variance
        center = means

    se = np.sqrt(
        np.divide(
            draw_variance,
            draw_counts[..., None],
            out=np.zeros_like(draw_variance),
            where=draw_counts[..., None] > 0,
        )
    )
    draw = center + rng.normal(size=means.shape) * se
    draw[draw_counts == 0] = np.nan
    result["means"] = draw
    result["counts"] = draw_counts
    result["sample_variance"] = draw_variance
    return result


def observable_nested_region(
    world: dict[str, Any],
    pipeline: dict[str, Any],
    *,
    draws: int,
    tracked_authors: int,
    candidates: Iterable[int],
    folds: int,
    seed: int,
    soft_noninferiority_margin: float,
) -> dict[str, float]:
    """Estimate an observable-only nested score region and score oracle coverage.

    Generator truth is used only after the region is fitted. Reference,
    calibration, and event bootstrap draws use observed means and variances.
    """
    baseline = score_panel(world["test"], world, pipeline)
    if baseline["status"] != "L5_CANDIDATE_SCORE_READY":
        return {
            "coverage": 0.0,
            "median_radius": float("inf"),
            "successful_draw_rate": 0.0,
        }
    tracked = min(int(tracked_authors), len(baseline["point"]))
    clouds: list[np.ndarray] = []
    root = np.random.SeedSequence(seed).spawn(draws)
    for sequence in root:
        rng = np.random.default_rng(sequence)
        reference_indices = []
        groups = np.asarray(world["reference"]["groups"])
        for group in range(len(world["target_group_weights"])):
            available = np.flatnonzero(groups == group)
            if len(available) == 0:
                continue
            reference_indices.extend(
                rng.choice(available, size=len(available), replace=True)
            )
        fit_indices = rng.integers(
            0,
            len(world["fit"]["groups"]),
            size=len(world["fit"]["groups"]),
        )
        bootstrap_world = dict(world)
        bootstrap_world["reference"] = resample_observed_panel(
            world["reference"],
            rng,
            indices=np.asarray(reference_indices, dtype=int),
            lambda_facet=world["lambda_facet"],
        )
        bootstrap_world["fit"] = resample_observed_panel(
            world["fit"],
            rng,
            indices=np.asarray(fit_indices, dtype=int),
            lambda_facet=world["lambda_facet"],
        )
        bootstrap_world["test"] = resample_observed_panel(
            world["test"],
            rng,
            lambda_facet=world["lambda_facet"],
        )
        fitted = fit_l45_pipeline(
            bootstrap_world,
            candidates=candidates,
            folds=folds,
            seed=int(rng.integers(0, np.iinfo(np.int32).max)),
            soft_noninferiority_margin=soft_noninferiority_margin,
        )
        scored = score_panel(
            bootstrap_world["test"],
            bootstrap_world,
            fitted,
        )
        if scored["status"] == "L5_CANDIDATE_SCORE_READY":
            clouds.append(np.asarray(scored["point"])[:tracked])
    if len(clouds) < max(12, draws // 2):
        return {
            "coverage": 0.0,
            "median_radius": float("inf"),
            "successful_draw_rate": len(clouds) / max(draws, 1),
        }
    cloud = np.stack(clouds)
    point = np.asarray(baseline["point"])[:tracked]
    # Generator truth enters only after the observable region is frozen.
    truth = oracle_score_target(
        world["test"],
        world,
        pipeline,
    )[:tracked]
    covered: list[bool] = []
    radii: list[float] = []
    for author in range(tracked):
        deviations = cloud[:, author] - point[author]
        split = max(6, len(deviations) // 2)
        fit_deviation = deviations[:split]
        radius_deviation = deviations[split:]
        covariance = np.cov(fit_deviation, rowvar=False)
        average = max(
            float(np.trace(covariance)) / covariance.shape[0],
            1e-10,
        )
        covariance = 0.5 * covariance + 0.5 * average * np.eye(
            covariance.shape[0]
        )
        inverse = np.linalg.pinv(covariance, hermitian=True)
        bootstrap_distance = np.einsum(
            "ni,ij,nj->n",
            radius_deviation,
            inverse,
            radius_deviation,
        )
        threshold = float(np.quantile(bootstrap_distance, 0.95))
        truth_error = truth[author] - point[author]
        truth_distance = float(truth_error @ inverse @ truth_error)
        covered.append(truth_distance <= threshold)
        radii.append(
            float(
                np.sqrt(
                    max(
                        threshold * np.linalg.eigvalsh(covariance).max(),
                        0.0,
                    )
                )
            )
        )
    return {
        "coverage": float(np.mean(covered)),
        "median_radius": float(np.median(radii)),
        "successful_draw_rate": len(clouds) / max(draws, 1),
    }


def score_correlation(left: np.ndarray, right: np.ndarray) -> float:
    """Flattened score correlation with a finite-variance guard."""
    x = np.asarray(left, dtype=float).ravel()
    y = np.asarray(right, dtype=float).ravel()
    if np.std(x) <= 1e-12 or np.std(y) <= 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def normalized_score_error(point: np.ndarray, target: np.ndarray) -> float:
    """Normalized technical-score error."""
    truth = np.asarray(target, dtype=float)
    scale = float(np.sqrt(np.mean(truth**2)))
    return float(
        np.sqrt(np.mean((np.asarray(point) - truth) ** 2))
        / max(scale, 1e-12)
    )


def mdd_metrics(left: np.ndarray, right: np.ndarray) -> dict[str, float]:
    """Calibrate MDD on one author half and evaluate it on the other half."""
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    split = max(2, len(x) // 2)
    calibration = np.linalg.norm(x[:split] - y[:split], axis=1)
    evaluation = np.linalg.norm(x[split:] - y[split:], axis=1)
    mdd95 = float(np.quantile(calibration, 0.95))
    direction = np.ones(x.shape[1], dtype=float)
    direction /= np.linalg.norm(direction)
    changed = np.linalg.norm(
        x[split:] - (y[split:] + 2.0 * mdd95 * direction),
        axis=1,
    )
    return {
        "mdd95": mdd95,
        "null_false_positive": float(np.mean(evaluation > mdd95)),
        "two_mdd_power": float(np.mean(changed > mdd95)),
    }


def operator_transport_audit(world: dict[str, Any]) -> dict[str, Any]:
    """Check whether the registered alternative operator is invertible."""
    operator = np.asarray(world["operator_matrix"], dtype=float)
    dimension = operator.shape[0]
    if np.linalg.matrix_rank(operator) < dimension:
        return {
            "status": "REFUSE_OPERATOR_KERNEL_NONINVERTIBLE",
            "operator_rank": int(np.linalg.matrix_rank(operator)),
            "commutation_defect": float("inf"),
        }
    base = np.einsum(
        "f,afd->ad",
        world["lambda_facet"],
        world["test"]["stable_field"],
    )
    transformed = base @ operator.T
    recovered = transformed @ operator
    defect = float(
        np.linalg.norm(recovered - base)
        / max(float(np.linalg.norm(base)), 1e-12)
    )
    return {
        "status": (
            "OPERATOR_TRANSPORT_READY"
            if defect <= 1e-10
            else "REFUSE_OPERATOR_TRANSPORT_DEFECT"
        ),
        "operator_rank": dimension,
        "commutation_defect": defect,
    }
