"""Context-fibered relation fields for SUICA V8-HJIC-1C.

This module joins replicated mesoscopic readouts to a population-level
relation field.  Every observable license is computed without opening the
synthetic truth lockbox.  Truth is used only by the separate audit function.

The implementation deliberately works in covariance space before applying a
single calibration-frozen whitening map.  This makes the total-covariance
decomposition exact and prevents an ecological relation from being silently
relabelled as an individual relation.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Iterable

import numpy as np


@dataclass(frozen=True)
class ContextRelationSpec:
    """Evidence budgets and observable decision thresholds."""

    calibration_authors: int = 1200
    confirmation_authors: int = 1200
    contexts: int = 4
    left_dimensions: int = 5
    right_dimensions: int = 4
    shared_dimensions: int = 2
    view_noise: float = 0.45
    private_noise: float = 0.60
    permutations: int = 999
    bootstrap_draws: int = 999
    relation_strength_floor: float = 0.075
    direction_floor: float = 0.80
    field_agreement_floor: float = 0.80
    context_agreement_floor: float = 0.70
    heterogeneity_floor: float = 0.12
    cancellation_floor: float = 0.55
    misspecification_floor: float = 0.25
    composition_weight_shift_floor: float = 0.40
    composition_attribution_floor: float = 0.70
    mode_margin: float = 0.04

    def __post_init__(self) -> None:
        if self.calibration_authors < 400:
            raise ValueError("Calibration requires at least 400 authors.")
        if self.confirmation_authors < 400:
            raise ValueError("Each confirmation split requires at least 400 authors.")
        if self.contexts < 2:
            raise ValueError("At least two contexts are required.")
        if min(self.left_dimensions, self.right_dimensions) < 2:
            raise ValueError("Both readout families must be multivariate.")
        if not 1 <= self.shared_dimensions <= min(
            self.left_dimensions,
            self.right_dimensions,
        ):
            raise ValueError("shared_dimensions must fit both margins.")
        if self.permutations < 19 or self.bootstrap_draws < 19:
            raise ValueError("Resampling budgets are too small.")
        if not 0 < self.context_agreement_floor <= 1:
            raise ValueError("context_agreement_floor must be in (0, 1].")


@dataclass(frozen=True)
class FrozenRelationCalibration:
    """Marginal whitening and null threshold frozen without cross-family truth."""

    left_whitener: np.ndarray
    right_whitener: np.ndarray
    local_max_null_q99: float
    context_cutpoints: np.ndarray
    residual_misspecification_q99: float = 0.0
    between_relation_q99: float = 0.0


def _orthonormal_loadings(
    rng: np.random.Generator,
    rows: int,
    columns: int,
) -> np.ndarray:
    basis, _ = np.linalg.qr(rng.normal(size=(rows, columns)))
    return np.asarray(basis[:, :columns], dtype=float)


def _center(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    return matrix - matrix.mean(axis=0, keepdims=True)


def _population_covariance(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Return population-denominator covariance for exact total decomposition."""
    x = _center(left)
    y = _center(right)
    return x.T @ y / max(1, len(x))


def _symmetric_cross_covariance(
    left_first: np.ndarray,
    left_second: np.ndarray,
    right_first: np.ndarray,
    right_second: np.ndarray,
) -> np.ndarray:
    return 0.5 * (
        _population_covariance(left_first, right_second)
        + _population_covariance(left_second, right_first)
    )


def _replicate_covariance(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    return 0.5 * (
        _population_covariance(first, second)
        + _population_covariance(second, first)
    )


def _inverse_sqrt(matrix: np.ndarray, ridge: float = 1e-6) -> np.ndarray:
    symmetric = 0.5 * (matrix + matrix.T)
    values, vectors = np.linalg.eigh(symmetric)
    scale = max(float(values.max()), ridge)
    values = np.clip(values, ridge * scale, None)
    return vectors @ np.diag(1.0 / np.sqrt(values)) @ vectors.T


def _cosine(left: np.ndarray, right: np.ndarray) -> float:
    x = np.asarray(left, dtype=float).ravel()
    y = np.asarray(right, dtype=float).ravel()
    denominator = float(np.linalg.norm(x) * np.linalg.norm(y))
    if denominator <= 1e-12:
        return 0.0
    return float(np.dot(x, y) / denominator)


def _rms(matrix: np.ndarray) -> float:
    values = np.asarray(matrix, dtype=float)
    return float(np.linalg.norm(values) / np.sqrt(values.size))


def _folds(rng: np.random.Generator, authors: int) -> np.ndarray:
    order = rng.permutation(authors)
    result = np.empty(authors, dtype=int)
    result[order[: authors // 2]] = 0
    result[order[authors // 2 :]] = 1
    return result


def _monomial_powers(dimensions: int, degree: int) -> list[tuple[int, ...]]:
    powers: list[tuple[int, ...]] = []
    for candidate in product(range(degree + 1), repeat=dimensions):
        total = sum(candidate)
        if 1 <= total <= degree:
            powers.append(tuple(int(value) for value in candidate))
    return powers


def polynomial_design(
    nuisance: np.ndarray,
    *,
    degree: int,
    center: np.ndarray | None = None,
    scale: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build a deterministic total-degree polynomial sieve."""
    values = np.asarray(nuisance, dtype=float)
    if values.ndim != 2:
        raise ValueError("nuisance must be a two-dimensional matrix.")
    fitted_center = values.mean(axis=0) if center is None else np.asarray(center)
    fitted_scale = values.std(axis=0) if scale is None else np.asarray(scale)
    fitted_scale = np.where(fitted_scale <= 1e-8, 1.0, fitted_scale)
    standardized = (values - fitted_center) / fitted_scale
    columns = [np.ones(len(values), dtype=float)]
    for powers in _monomial_powers(values.shape[1], degree):
        column = np.ones(len(values), dtype=float)
        for index, exponent in enumerate(powers):
            if exponent:
                column *= standardized[:, index] ** exponent
        columns.append(column)
    return np.column_stack(columns), fitted_center, fitted_scale


def crossfit_polynomial_residualize(
    values: np.ndarray,
    nuisance: np.ndarray,
    folds: np.ndarray,
    *,
    degree: int = 3,
) -> np.ndarray:
    """Residualize with a fold-local polynomial sieve."""
    values = np.asarray(values, dtype=float)
    nuisance = np.asarray(nuisance, dtype=float)
    folds = np.asarray(folds, dtype=int)
    residual = np.full_like(values, np.nan, dtype=float)
    for fold in sorted(set(folds.tolist())):
        train = folds != fold
        test = folds == fold
        design_train, center, scale = polynomial_design(
            nuisance[train],
            degree=degree,
        )
        design_test, _, _ = polynomial_design(
            nuisance[test],
            degree=degree,
            center=center,
            scale=scale,
        )
        coefficients = np.linalg.lstsq(
            design_train,
            values[train],
            rcond=None,
        )[0]
        residual[test] = values[test] - design_test @ coefficients
    if not np.isfinite(residual).all():
        raise RuntimeError("Cross-fit residualization produced missing values.")
    return residual


def _residual_misspecification_score(
    residuals: Iterable[np.ndarray],
    nuisance: np.ndarray,
) -> float:
    """Measure dependence on registered fourth/fifth-degree omitted terms."""
    nuisance = np.asarray(nuisance, dtype=float)
    center = nuisance.mean(axis=0)
    scale = nuisance.std(axis=0)
    scale = np.where(scale <= 1e-8, 1.0, scale)
    standardized = (nuisance - center) / scale
    columns = []
    for powers in _monomial_powers(nuisance.shape[1], degree=5):
        if sum(powers) <= 3:
            continue
        column = np.ones(len(nuisance), dtype=float)
        for index, exponent in enumerate(powers):
            if exponent:
                column *= standardized[:, index] ** exponent
        columns.append(column)
    extra = np.column_stack(columns)
    extra = _center(extra)
    extra_scale = np.linalg.norm(extra, axis=0)
    scores: list[float] = []
    for residual in residuals:
        values = _center(np.asarray(residual, dtype=float))
        value_scale = np.linalg.norm(values, axis=0)
        denominator = np.outer(extra_scale, value_scale)
        correlation = np.divide(
            extra.T @ values,
            denominator,
            out=np.zeros((extra.shape[1], values.shape[1]), dtype=float),
            where=denominator > 1e-12,
        )
        scores.append(float(np.max(np.abs(correlation))))
    return max(scores, default=0.0)


def _context_labels(
    latent_context: np.ndarray,
    *,
    reliability: float,
    rng: np.random.Generator,
    cutpoints: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    if reliability >= 0.999:
        labels = np.asarray(latent_context, dtype=int)
        return labels.copy(), labels.copy()
    centers = np.linspace(-1.5, 1.5, len(cutpoints) + 1)
    noise_scale = 1.5 * (1.0 - reliability)
    first = centers[latent_context] + rng.normal(
        scale=noise_scale,
        size=len(latent_context),
    )
    second = centers[latent_context] + rng.normal(
        scale=noise_scale,
        size=len(latent_context),
    )
    return (
        np.digitize(first, cutpoints).astype(int),
        np.digitize(second, cutpoints).astype(int),
    )


def fit_relation_calibration(
    *,
    seed: int,
    spec: ContextRelationSpec,
) -> FrozenRelationCalibration:
    """Freeze marginal whitening and a max-context null threshold on D0."""
    rng = np.random.default_rng(seed)
    n = spec.calibration_authors
    b = spec.left_dimensions
    m = spec.right_dimensions
    left_latent = rng.normal(size=(n, b))
    right_latent = rng.normal(size=(n, m))
    left_first = left_latent + rng.normal(
        scale=spec.view_noise,
        size=(n, b),
    )
    left_second = left_latent + rng.normal(
        scale=spec.view_noise,
        size=(n, b),
    )
    right_first = right_latent + rng.normal(
        scale=spec.view_noise,
        size=(n, m),
    )
    right_second = right_latent + rng.normal(
        scale=spec.view_noise,
        size=(n, m),
    )
    left_whitener = _inverse_sqrt(
        _replicate_covariance(left_first, left_second)
    )
    right_whitener = _inverse_sqrt(
        _replicate_covariance(right_first, right_second)
    )
    contexts = np.arange(n, dtype=int) % spec.contexts
    maxima = np.empty(spec.permutations, dtype=float)
    for draw in range(spec.permutations):
        order = rng.permutation(n)
        strengths = []
        for context in range(spec.contexts):
            mask = contexts == context
            covariance = _symmetric_cross_covariance(
                left_first[mask],
                left_second[mask],
                right_first[order][mask],
                right_second[order][mask],
            )
            relation = left_whitener @ covariance @ right_whitener
            strengths.append(_rms(relation))
        maxima[draw] = max(strengths)
    return FrozenRelationCalibration(
        left_whitener=left_whitener,
        right_whitener=right_whitener,
        local_max_null_q99=float(np.quantile(maxima, 0.99)),
        context_cutpoints=np.linspace(
            -1.0,
            1.0,
            spec.contexts - 1,
        ),
    )


def _world_parameters(
    world: str,
    *,
    contexts: int,
    shared_dimensions: int,
) -> tuple[np.ndarray, np.ndarray]:
    left = np.linspace(0.85, 0.55, shared_dimensions)
    right = np.tile(
        np.linspace(0.85, 0.35, shared_dimensions),
        (contexts, 1),
    )
    if world == "BALANCED_SIGN_REVERSAL":
        signs = np.where(np.arange(contexts) % 2 == 0, 1.0, -1.0)
        right *= signs[:, None]
    elif world == "TRUE_CONTEXT_MODERATION":
        right *= np.linspace(0.45, 1.35, contexts)[:, None]
    elif world == "COMPOSITION_REWEIGHT":
        right[:, 0] *= np.linspace(1.80, -1.80, contexts)
        if shared_dimensions > 1:
            right[:, 1:] *= 0.90
    elif world == "LOCAL_LOW_SINGULAR_GAP":
        left[:] = 0.68
        right[:] = 0.68
    return left, right


def _panel(
    *,
    rng: np.random.Generator,
    spec: ContextRelationSpec,
    world: str,
    weights: np.ndarray,
    left_loadings: np.ndarray,
    right_loadings: np.ndarray,
    context_reliability: float,
) -> dict[str, Any]:
    n = spec.confirmation_authors
    b = spec.left_dimensions
    m = spec.right_dimensions
    k = spec.shared_dimensions
    context = rng.choice(spec.contexts, size=n, p=weights)
    nuisance = rng.normal(size=(n, 2))
    folds = _folds(rng, n)
    left_private = rng.normal(scale=spec.private_noise, size=(n, b))
    right_private = rng.normal(scale=spec.private_noise, size=(n, m))
    left_strength, right_strength = _world_parameters(
        world,
        contexts=spec.contexts,
        shared_dimensions=k,
    )
    shared = rng.normal(size=(n, k))
    left_true = (shared * left_strength) @ left_loadings.T + left_private
    right_true = (
        shared * right_strength[context]
    ) @ right_loadings.T + right_private
    oracle_local = np.asarray(
        [
            left_loadings
            @ np.diag(left_strength * right_strength[level])
            @ right_loadings.T
            for level in range(spec.contexts)
        ],
        dtype=float,
    )
    context_role = "PRE_RESPONSE_DESIGNED"

    if world in ("LOCAL_NULL_MULTIPLE_STRATA", "ECOLOGICAL_ONLY"):
        right_shared = rng.normal(size=(n, k))
        right_true = (
            right_shared * right_strength[context]
        ) @ right_loadings.T + right_private
        oracle_local = np.zeros_like(oracle_local)
    if world == "ECOLOGICAL_ONLY":
        offsets = np.linspace(-1.5, 1.5, spec.contexts)
        left_true += offsets[context, None] * left_loadings[:, 0][None, :]
        right_true += offsets[context, None] * right_loadings[:, 0][None, :]
    elif world == "NONLINEAR_SIMPSON_IN_SIEVE":
        right_shared = rng.normal(size=(n, k))
        left_true = left_private
        right_true = right_private
        common = (
            0.85 * (nuisance[:, 0] ** 2 - 1.0)
            + 0.45 * nuisance[:, 1]
            + 0.35 * nuisance[:, 0] * nuisance[:, 1]
        )
        left_true += common[:, None] * left_loadings[:, 0][None, :]
        right_true += common[:, None] * right_loadings[:, 0][None, :]
        oracle_local = np.zeros_like(oracle_local)
    elif world == "NONLINEAR_SIMPSON_OUT_OF_SIEVE":
        left_true = left_private
        right_true = right_private
        common = (
            1.05 * np.sin(2.8 * nuisance[:, 0])
            + 0.30 * (nuisance[:, 1] ** 4 - 3.0)
        )
        left_true += common[:, None] * left_loadings[:, 0][None, :]
        right_true += common[:, None] * right_loadings[:, 0][None, :]
        oracle_local = np.zeros_like(oracle_local)
    elif world == "COLLIDER_OR_DESCENDANT_Z":
        right_true = rng.normal(
            scale=np.sqrt(spec.private_noise**2 + 0.5),
            size=(n, m),
        )
        collider = (
            left_true[:, 0]
            + right_true[:, 0]
            + rng.normal(scale=0.20, size=n)
        )
        quantiles = np.quantile(
            collider,
            np.linspace(0, 1, spec.contexts + 1)[1:-1],
        )
        context = np.digitize(collider, quantiles).astype(int)
        context_role = "POST_RESPONSE_COLLIDER"
        oracle_local = np.zeros_like(oracle_local)

    context_first, context_second = _context_labels(
        context,
        reliability=context_reliability,
        rng=rng,
        cutpoints=np.linspace(-1.0, 1.0, spec.contexts - 1),
    )
    left_first = left_true + rng.normal(
        scale=spec.view_noise,
        size=(n, b),
    )
    left_second = left_true + rng.normal(
        scale=spec.view_noise,
        size=(n, b),
    )
    right_first = right_true + rng.normal(
        scale=spec.view_noise,
        size=(n, m),
    )
    right_second = right_true + rng.normal(
        scale=spec.view_noise,
        size=(n, m),
    )
    return {
        "left_first": left_first,
        "left_second": left_second,
        "right_first": right_first,
        "right_second": right_second,
        "nuisance": nuisance,
        "folds": folds,
        "context_first": context_first,
        "context_second": context_second,
        "declared_context_role": context_role,
        "truth_lockbox": {
            "oracle_local_covariance": oracle_local,
            "latent_context": context,
        },
    }


def simulate_context_relation_world(
    world: str,
    *,
    seed: int,
    spec: ContextRelationSpec,
    context_reliability: float = 1.0,
) -> dict[str, Any]:
    """Generate independent D1/D2 panels plus a locked analytic relation field."""
    rng = np.random.default_rng(seed)
    left_loadings = _orthonormal_loadings(
        rng,
        spec.left_dimensions,
        spec.shared_dimensions,
    )
    right_loadings = _orthonormal_loadings(
        rng,
        spec.right_dimensions,
        spec.shared_dimensions,
    )
    balanced = np.full(spec.contexts, 1.0 / spec.contexts)
    weights_first = balanced
    weights_second = balanced
    if world == "COMPOSITION_REWEIGHT":
        base = np.linspace(spec.contexts, 1, spec.contexts, dtype=float)
        weights_first = base / base.sum()
        weights_second = weights_first[::-1].copy()
    first = _panel(
        rng=rng,
        spec=spec,
        world=world,
        weights=weights_first,
        left_loadings=left_loadings,
        right_loadings=right_loadings,
        context_reliability=context_reliability,
    )
    second = _panel(
        rng=rng,
        spec=spec,
        world=world,
        weights=weights_second,
        left_loadings=left_loadings,
        right_loadings=right_loadings,
        context_reliability=context_reliability,
    )
    truth = {
        "first": first.pop("truth_lockbox"),
        "second": second.pop("truth_lockbox"),
    }
    return {
        "world": world,
        "context_reliability": float(context_reliability),
        "first": first,
        "second": second,
        "truth_lockbox": truth,
    }


def _residualize_panel(panel: dict[str, Any]) -> dict[str, Any]:
    nuisance = np.asarray(panel["nuisance"], dtype=float)
    folds = np.asarray(panel["folds"], dtype=int)
    result = {
        key: crossfit_polynomial_residualize(
            np.asarray(panel[key], dtype=float),
            nuisance,
            folds,
            degree=3,
        )
        for key in (
            "left_first",
            "left_second",
            "right_first",
            "right_second",
        )
    }
    result.update({
        "nuisance": nuisance,
        "context_first": np.asarray(panel["context_first"], dtype=int),
        "context_second": np.asarray(panel["context_second"], dtype=int),
        "declared_context_role": str(panel["declared_context_role"]),
    })
    result["misspecification_score"] = _residual_misspecification_score(
        (
            result["left_first"],
            result["left_second"],
            result["right_first"],
            result["right_second"],
        ),
        nuisance,
    )
    return result


def calibrate_residual_misspecification_null(
    panel: dict[str, Any],
    *,
    draws: int,
    seed: int,
) -> float:
    """Calibrate the max omitted-term score under independent nuisances.

    Each draw generates a new nuisance design and new cross-fitting split, then
    applies the complete registered residualizer. This preserves finite-sample
    fitting artifacts that a simple row permutation would incorrectly remove.
    """
    if draws < 19:
        raise ValueError("At least 19 null draws are required.")
    values = {
        key: np.asarray(panel[key], dtype=float)
        for key in (
            "left_first",
            "left_second",
            "right_first",
            "right_second",
        )
    }
    authors = len(values["left_first"])
    rng = np.random.default_rng(seed)
    maxima = np.empty(draws, dtype=float)
    for draw in range(draws):
        nuisance = rng.normal(size=(authors, 2))
        folds = _folds(rng, authors)
        residuals = [
            crossfit_polynomial_residualize(
                matrix,
                nuisance,
                folds,
                degree=3,
            )
            for matrix in values.values()
        ]
        maxima[draw] = _residual_misspecification_score(
            residuals,
            nuisance,
        )
    return float(np.quantile(maxima, 0.99))


def covariance_decomposition(
    panel: dict[str, Any],
    *,
    contexts: np.ndarray,
    calibration: FrozenRelationCalibration,
    context_count: int,
) -> dict[str, Any]:
    """Compute exact within/between/total cross-covariance decomposition."""
    labels = np.asarray(contexts, dtype=int)
    n = len(labels)
    local_covariances = []
    weights = []
    for context in range(context_count):
        mask = labels == context
        if int(mask.sum()) < 4:
            raise ValueError("Every context requires at least four authors.")
        weights.append(float(mask.mean()))
        local_covariances.append(
            _symmetric_cross_covariance(
                panel["left_first"][mask],
                panel["left_second"][mask],
                panel["right_first"][mask],
                panel["right_second"][mask],
            )
        )
    weight = np.asarray(weights, dtype=float)
    local_covariance = np.asarray(local_covariances, dtype=float)
    within = np.einsum("s,sij->ij", weight, local_covariance)

    def directional_between(
        left: np.ndarray,
        right: np.ndarray,
    ) -> np.ndarray:
        mean_left = left.mean(axis=0)
        mean_right = right.mean(axis=0)
        value = np.zeros((left.shape[1], right.shape[1]), dtype=float)
        for context in range(context_count):
            mask = labels == context
            delta_left = left[mask].mean(axis=0) - mean_left
            delta_right = right[mask].mean(axis=0) - mean_right
            value += weight[context] * np.outer(delta_left, delta_right)
        return value

    between = 0.5 * (
        directional_between(panel["left_first"], panel["right_second"])
        + directional_between(panel["left_second"], panel["right_first"])
    )
    total = _symmetric_cross_covariance(
        panel["left_first"],
        panel["left_second"],
        panel["right_first"],
        panel["right_second"],
    )
    decomposition_error = float(
        np.linalg.norm(total - within - between)
        / max(np.linalg.norm(total), np.linalg.norm(within + between), 1e-10)
    )
    left_whitener = calibration.left_whitener
    right_whitener = calibration.right_whitener

    def lift(covariance: np.ndarray) -> np.ndarray:
        return left_whitener @ covariance @ right_whitener

    local = np.asarray([lift(value) for value in local_covariance])
    relation_within = lift(within)
    relation_between = lift(between)
    relation_total = lift(total)
    energy = float(np.sum(weight * np.sum(local**2, axis=(1, 2))))
    heterogeneity = float(
        np.sum(
            weight
            * np.sum((local - relation_within[None, :, :]) ** 2, axis=(1, 2))
        )
        / max(energy, 1e-12)
    )
    local_norm_average = float(
        np.sum(weight * np.linalg.norm(local, axis=(1, 2)))
    )
    cancellation = float(
        1.0
        - np.linalg.norm(relation_within) / max(local_norm_average, 1e-12)
    )
    return {
        "n": n,
        "weights": weight,
        "local_covariance": local_covariance,
        "within_covariance": within,
        "between_covariance": between,
        "total_covariance": total,
        "local_relation": local,
        "within_relation": relation_within,
        "between_relation": relation_between,
        "total_relation": relation_total,
        "decomposition_error": decomposition_error,
        "heterogeneity": heterogeneity,
        "cancellation": cancellation,
    }


def _field_agreement(
    first: np.ndarray,
    second: np.ndarray,
) -> tuple[float, np.ndarray]:
    per_context = np.asarray(
        [_cosine(left, right) for left, right in zip(first, second)],
        dtype=float,
    )
    return float(np.mean(per_context)), per_context


def _field_drift(first: np.ndarray, second: np.ndarray) -> float:
    numerator = float(np.linalg.norm(first - second))
    denominator = max(
        float(np.linalg.norm(first)),
        float(np.linalg.norm(second)),
        1e-10,
    )
    return numerator / denominator


def _mode_diagnostics(
    first: np.ndarray,
    second: np.ndarray,
    licensed_contexts: np.ndarray,
    *,
    margin: float,
) -> tuple[float, float, int]:
    gaps = []
    errors = []
    for context in np.flatnonzero(licensed_contexts):
        operator = 0.5 * (first[context] + second[context])
        singular = np.linalg.svd(operator, compute_uv=False)
        gap = float(
            singular[0] - (singular[1] if len(singular) > 1 else 0.0)
        )
        error = 0.5 * float(
            np.linalg.norm(first[context] - second[context], ord=2)
        )
        gaps.append(gap)
        errors.append(error)
    if not gaps:
        return 0.0, float("inf"), 0
    minimum_gap = min(gaps)
    maximum_error = max(errors)
    licensed = int(minimum_gap > 2.0 * maximum_error + margin)
    return minimum_gap, maximum_error, licensed


def observable_context_relation_diagnostics(
    world: dict[str, Any],
    *,
    calibration: FrozenRelationCalibration,
    spec: ContextRelationSpec,
) -> dict[str, Any]:
    """Estimate and license a local relation field without opening truth."""
    first = _residualize_panel(world["first"])
    second = _residualize_panel(world["second"])
    first_primary = covariance_decomposition(
        first,
        contexts=first["context_first"],
        calibration=calibration,
        context_count=spec.contexts,
    )
    second_primary = covariance_decomposition(
        second,
        contexts=second["context_first"],
        calibration=calibration,
        context_count=spec.contexts,
    )
    first_replicate = covariance_decomposition(
        first,
        contexts=first["context_second"],
        calibration=calibration,
        context_count=spec.contexts,
    )
    second_replicate = covariance_decomposition(
        second,
        contexts=second["context_second"],
        calibration=calibration,
        context_count=spec.contexts,
    )

    assignment_agreement = 0.5 * (
        float(np.mean(first["context_first"] == first["context_second"]))
        + float(np.mean(second["context_first"] == second["context_second"]))
    )
    measurement_field_agreement = 0.5 * (
        _field_agreement(
            first_primary["local_relation"],
            first_replicate["local_relation"],
        )[0]
        + _field_agreement(
            second_primary["local_relation"],
            second_replicate["local_relation"],
        )[0]
    )
    confirmation_field_agreement, per_context_agreement = _field_agreement(
        first_primary["local_relation"],
        second_primary["local_relation"],
    )
    strengths_first = np.asarray(
        [_rms(value) for value in first_primary["local_relation"]]
    )
    strengths_second = np.asarray(
        [_rms(value) for value in second_primary["local_relation"]]
    )
    threshold = max(
        spec.relation_strength_floor,
        calibration.local_max_null_q99,
    )
    context_resolved = bool(
        assignment_agreement >= spec.context_agreement_floor
        and measurement_field_agreement >= spec.field_agreement_floor
    )
    misspecification_score = max(
        float(first["misspecification_score"]),
        float(second["misspecification_score"]),
    )
    misspecification_threshold = max(
        spec.misspecification_floor,
        calibration.residual_misspecification_q99,
    )
    residualizer_misspecified = bool(
        misspecification_score >= misspecification_threshold
    )
    causal_role_refusal = bool(
        first["declared_context_role"] != "PRE_RESPONSE_DESIGNED"
        or second["declared_context_role"] != "PRE_RESPONSE_DESIGNED"
    )
    local_licensed = (
        (strengths_first >= threshold)
        & (strengths_second >= threshold)
        & (per_context_agreement >= spec.direction_floor)
        & context_resolved
        & (not residualizer_misspecified)
        & (not causal_role_refusal)
    )
    relation_licensed = bool(local_licensed.sum() >= 2)
    mean_heterogeneity = 0.5 * (
        float(first_primary["heterogeneity"])
        + float(second_primary["heterogeneity"])
    )
    mean_cancellation = 0.5 * (
        float(first_primary["cancellation"])
        + float(second_primary["cancellation"])
    )
    heterogeneous = bool(
        relation_licensed
        and mean_heterogeneity >= spec.heterogeneity_floor
    )
    cancellation_detected = bool(
        heterogeneous
        and mean_cancellation >= spec.cancellation_floor
    )
    global_invariant = bool(
        relation_licensed
        and local_licensed.all()
        and not heterogeneous
        and confirmation_field_agreement >= spec.field_agreement_floor
    )
    local_atlas = bool(relation_licensed and heterogeneous)

    between_strengths = np.asarray([
        _rms(first_primary["between_relation"]),
        _rms(second_primary["between_relation"]),
    ])
    within_strengths = np.asarray([
        _rms(first_primary["within_relation"]),
        _rms(second_primary["within_relation"]),
    ])
    between_agreement = _cosine(
        first_primary["between_relation"],
        second_primary["between_relation"],
    )
    between_threshold = max(
        spec.relation_strength_floor,
        (
            calibration.between_relation_q99
            if calibration.between_relation_q99 > 0
            else calibration.local_max_null_q99
        ),
    )
    ecological_between_detected = bool(
        np.all(between_strengths >= between_threshold)
        and between_agreement >= spec.direction_floor
        and not relation_licensed
    )

    field_drift = _field_drift(
        first_primary["local_relation"],
        second_primary["local_relation"],
    )
    weight_shift = float(
        np.sum(
            np.abs(
                first_primary["weights"] - second_primary["weights"]
            )
        )
    )
    average_field = 0.5 * (
        first_primary["local_relation"]
        + second_primary["local_relation"]
    )
    predicted_shift = np.einsum(
        "s,sij->ij",
        first_primary["weights"] - second_primary["weights"],
        average_field,
    )
    observed_shift = (
        first_primary["within_relation"]
        - second_primary["within_relation"]
    )
    attribution = float(
        1.0
        - np.linalg.norm(observed_shift - predicted_shift)
        / max(np.linalg.norm(observed_shift), 1e-10)
    )
    composition_reweight = bool(
        relation_licensed
        and weight_shift >= spec.composition_weight_shift_floor
        and field_drift <= 0.85
        and attribution >= spec.composition_attribution_floor
    )
    minimum_gap, operator_error, mode_licensed = _mode_diagnostics(
        first_primary["local_relation"],
        second_primary["local_relation"],
        local_licensed,
        margin=spec.mode_margin,
    )

    if causal_role_refusal:
        taxonomy = "CONTEXT_ROLE_UNSUPPORTED"
    elif residualizer_misspecified:
        taxonomy = "RESIDUALIZER_MISSPECIFIED"
    elif not context_resolved:
        taxonomy = "CONTEXT_UNDERRESOLVED"
    elif ecological_between_detected:
        taxonomy = "ECOLOGICAL_ONLY"
    elif composition_reweight:
        taxonomy = "COMPOSITION_REWEIGHT"
    elif global_invariant:
        taxonomy = "GLOBAL_INVARIANT"
    elif cancellation_detected:
        taxonomy = "GLOBAL_CANCELLATION"
    elif local_atlas:
        taxonomy = "LOCAL_RELATION_ATLAS"
    elif relation_licensed and not mode_licensed:
        taxonomy = "MODE_UNDERRESOLVED"
    else:
        taxonomy = "NO_SUPPORTED_RELATION"

    final_relation_license = int(
        relation_licensed
        and context_resolved
        and not residualizer_misspecified
        and not causal_role_refusal
    )
    return {
        "taxonomy": taxonomy,
        "final_relation_license": final_relation_license,
        "global_invariant_license": int(global_invariant),
        "local_atlas_license": int(local_atlas or cancellation_detected),
        "mode_license": int(mode_licensed and final_relation_license),
        "cancellation_detected": int(cancellation_detected),
        "ecological_between_detected": int(ecological_between_detected),
        "composition_reweight_detected": int(composition_reweight),
        "residualizer_misspecified": int(residualizer_misspecified),
        "context_underresolved": int(not context_resolved),
        "causal_role_refusal": int(causal_role_refusal),
        "context_assignment_agreement": assignment_agreement,
        "context_measurement_field_agreement": measurement_field_agreement,
        "confirmation_field_agreement": confirmation_field_agreement,
        "local_license_count": int(local_licensed.sum()),
        "local_licensed": local_licensed.astype(int),
        "local_strength_first": strengths_first,
        "local_strength_second": strengths_second,
        "local_direction_agreement": per_context_agreement,
        "heterogeneity": mean_heterogeneity,
        "cancellation": mean_cancellation,
        "between_strength_first": float(between_strengths[0]),
        "between_strength_second": float(between_strengths[1]),
        "between_threshold": between_threshold,
        "within_strength_first": float(within_strengths[0]),
        "within_strength_second": float(within_strengths[1]),
        "between_agreement": between_agreement,
        "field_drift": field_drift,
        "weight_shift_l1": weight_shift,
        "composition_attribution": attribution,
        "minimum_singular_gap": minimum_gap,
        "maximum_operator_error": operator_error,
        "misspecification_score": misspecification_score,
        "misspecification_threshold": misspecification_threshold,
        "relation_threshold": threshold,
        "first": first_primary,
        "second": second_primary,
        "first_context_replicate": first_replicate,
        "second_context_replicate": second_replicate,
        "truth_used_by_license": False,
    }


def _bootstrap_context_coverage(
    panel: dict[str, Any],
    *,
    contexts: np.ndarray,
    oracle_local_relation: np.ndarray,
    calibration: FrozenRelationCalibration,
    spec: ContextRelationSpec,
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Audit pointwise percentile coverage of the analytic local field."""
    labels = np.asarray(contexts, dtype=int)
    draws = np.empty(
        (
            spec.bootstrap_draws,
            spec.contexts,
            spec.left_dimensions,
            spec.right_dimensions,
        ),
        dtype=float,
    )
    context_indices = [
        np.flatnonzero(labels == context)
        for context in range(spec.contexts)
    ]
    for draw in range(spec.bootstrap_draws):
        for context, indices in enumerate(context_indices):
            sampled = rng.choice(indices, size=len(indices), replace=True)
            covariance = _symmetric_cross_covariance(
                panel["left_first"][sampled],
                panel["left_second"][sampled],
                panel["right_first"][sampled],
                panel["right_second"][sampled],
            )
            draws[draw, context] = (
                calibration.left_whitener
                @ covariance
                @ calibration.right_whitener
            )
    lower = np.quantile(draws, 0.025, axis=0)
    upper = np.quantile(draws, 0.975, axis=0)
    covered = (
        (oracle_local_relation >= lower)
        & (oracle_local_relation <= upper)
    )
    return {
        "covered": int(covered.sum()),
        "total": int(covered.size),
        "coverage": float(covered.mean()),
        "mean_width": float(np.mean(upper - lower)),
    }


def audit_context_relation_truth(
    world: dict[str, Any],
    observable: dict[str, Any],
    *,
    calibration: FrozenRelationCalibration,
    spec: ContextRelationSpec,
    seed: int,
) -> dict[str, Any]:
    """Open truth only after licensing and report fidelity/coverage."""
    truth = world["truth_lockbox"]
    fidelity = []
    oracle_by_split: dict[str, np.ndarray] = {}
    for name in ("first", "second"):
        oracle_covariance = np.asarray(
            truth[name]["oracle_local_covariance"],
            dtype=float,
        )
        oracle_relation = np.asarray([
            calibration.left_whitener
            @ value
            @ calibration.right_whitener
            for value in oracle_covariance
        ])
        oracle_by_split[name] = oracle_relation
        estimate = observable[name]["local_relation"]
        fidelity.append(_cosine(estimate, oracle_relation))
    result: dict[str, Any] = {
        "truth_fidelity": float(np.mean(fidelity)),
        "truth_used_by_license": False,
        "coverage": None,
        "coverage_cells": 0,
        "coverage_total": 0,
    }
    if world["world"] in {
        "GLOBAL_INVARIANT",
        "BALANCED_SIGN_REVERSAL",
        "TRUE_CONTEXT_MODERATION",
        "LOCAL_LOW_SINGULAR_GAP",
    }:
        residualized_first = _residualize_panel(world["first"])
        coverage = _bootstrap_context_coverage(
            residualized_first,
            contexts=residualized_first["context_first"],
            oracle_local_relation=oracle_by_split["first"],
            calibration=calibration,
            spec=spec,
            rng=np.random.default_rng(seed),
        )
        result.update({
            "coverage": coverage["coverage"],
            "coverage_cells": coverage["covered"],
            "coverage_total": coverage["total"],
            "coverage_mean_width": coverage["mean_width"],
        })
    return result


def run_context_relation_repetition(
    repetition: int,
    *,
    seed: int,
    spec: ContextRelationSpec,
) -> dict[str, list[dict[str, Any]]]:
    """Run every registered world under one independently calibrated repetition."""
    calibration = fit_relation_calibration(
        seed=seed + repetition * 100_003,
        spec=spec,
    )
    worlds: list[tuple[str, float]] = [
        ("GLOBAL_INVARIANT", 1.0),
        ("BALANCED_SIGN_REVERSAL", 1.0),
        ("TRUE_CONTEXT_MODERATION", 1.0),
        ("ECOLOGICAL_ONLY", 1.0),
        ("COMPOSITION_REWEIGHT", 1.0),
        ("NONLINEAR_SIMPSON_IN_SIEVE", 1.0),
        ("NONLINEAR_SIMPSON_OUT_OF_SIEVE", 1.0),
        ("LOCAL_NULL_MULTIPLE_STRATA", 1.0),
        ("LOCAL_LOW_SINGULAR_GAP", 1.0),
        ("COLLIDER_OR_DESCENDANT_Z", 1.0),
    ]
    worlds.extend(
        ("NOISY_CONTEXT_FRONTIER", reliability)
        for reliability in (1.0, 0.8, 0.6, 0.4, 0.2)
    )
    tables: dict[str, list[dict[str, Any]]] = {
        "context_relation_field": [],
        "within_between_covariance": [],
        "aggregation_commutation": [],
        "heterogeneity_cancellation": [],
        "ecological_failure_modes": [],
        "context_reliability_frontier": [],
        "uncertainty_coverage": [],
        "licenses": [],
        "truth_audit": [],
    }
    for world_index, (world_name, reliability) in enumerate(worlds):
        generator_world = (
            "BALANCED_SIGN_REVERSAL"
            if world_name == "NOISY_CONTEXT_FRONTIER"
            else world_name
        )
        world = simulate_context_relation_world(
            generator_world,
            seed=seed + repetition * 100_003 + 1_009 * (world_index + 1),
            spec=spec,
            context_reliability=reliability,
        )
        world["world"] = world_name
        observable = observable_context_relation_diagnostics(
            world,
            calibration=calibration,
            spec=spec,
        )
        audit = audit_context_relation_truth(
            world,
            observable,
            calibration=calibration,
            spec=spec,
            seed=seed + repetition * 100_003 + 50_000 + world_index,
        )
        common = {
            "repetition": repetition,
            "world": world_name,
            "context_reliability": reliability,
        }
        tables["licenses"].append({
            **common,
            **{
                key: value
                for key, value in observable.items()
                if key
                in {
                    "taxonomy",
                    "final_relation_license",
                    "global_invariant_license",
                    "local_atlas_license",
                    "mode_license",
                    "cancellation_detected",
                    "ecological_between_detected",
                    "composition_reweight_detected",
                    "residualizer_misspecified",
                    "context_underresolved",
                    "causal_role_refusal",
                    "local_license_count",
                    "truth_used_by_license",
                }
            },
        })
        tables["truth_audit"].append({
            **common,
            **audit,
        })
        for split_name in ("first", "second"):
            split = observable[split_name]
            for context in range(spec.contexts):
                tables["context_relation_field"].append({
                    **common,
                    "split": split_name,
                    "context": context,
                    "weight": float(split["weights"][context]),
                    "strength": _rms(split["local_relation"][context]),
                    "licensed": int(observable["local_licensed"][context]),
                    "direction_agreement": float(
                        observable["local_direction_agreement"][context]
                    ),
                    "relation_json": np.asarray(
                        split["local_relation"][context]
                    ).round(10).tolist(),
                })
            for component in ("within", "between", "total"):
                covariance = split[f"{component}_covariance"]
                relation = split[f"{component}_relation"]
                tables["within_between_covariance"].append({
                    **common,
                    "split": split_name,
                    "component": component,
                    "covariance_norm": float(np.linalg.norm(covariance)),
                    "relation_norm": float(np.linalg.norm(relation)),
                })
            tables["aggregation_commutation"].append({
                **common,
                "split": split_name,
                "decomposition_error": float(split["decomposition_error"]),
                "correlation_average_defect": float(
                    np.linalg.norm(
                        split["total_relation"]
                        - np.mean(split["local_relation"], axis=0)
                    )
                ),
            })
        tables["heterogeneity_cancellation"].append({
            **common,
            "heterogeneity": observable["heterogeneity"],
            "cancellation": observable["cancellation"],
            "confirmation_field_agreement": observable[
                "confirmation_field_agreement"
            ],
            "field_drift": observable["field_drift"],
        })
        tables["ecological_failure_modes"].append({
            **common,
            "between_strength_first": observable["between_strength_first"],
            "between_strength_second": observable["between_strength_second"],
            "within_strength_first": observable["within_strength_first"],
            "within_strength_second": observable["within_strength_second"],
            "between_agreement": observable["between_agreement"],
            "weight_shift_l1": observable["weight_shift_l1"],
            "composition_attribution": observable["composition_attribution"],
            "ecological_between_detected": observable[
                "ecological_between_detected"
            ],
            "composition_reweight_detected": observable[
                "composition_reweight_detected"
            ],
        })
        if world_name == "NOISY_CONTEXT_FRONTIER":
            tables["context_reliability_frontier"].append({
                **common,
                "assignment_agreement": observable[
                    "context_assignment_agreement"
                ],
                "measurement_field_agreement": observable[
                    "context_measurement_field_agreement"
                ],
                "final_relation_license": observable[
                    "final_relation_license"
                ],
                "context_underresolved": observable[
                    "context_underresolved"
                ],
            })
        if audit["coverage"] is not None:
            tables["uncertainty_coverage"].append({
                **common,
                "coverage": audit["coverage"],
                "covered_cells": audit["coverage_cells"],
                "total_cells": audit["coverage_total"],
                "mean_width": audit["coverage_mean_width"],
            })
    return tables
