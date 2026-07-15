"""Finite-dimensional estimators for conditional kernel transition embeddings.

The object estimated here is not a factor score.  Given a history ``H`` and a
next residual state ``Y``, a characteristic output kernel embeds the conditional
law ``P(Y | H)`` as ``E[ell(Y, .) | H]``.  Random Fourier features provide a
fixed, reproducible approximation of that embedding; a ridge regressor estimates
the pooled conditional mean embedding.  Per-author residual embeddings can then
be compared across independent text views.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _as_matrix(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 2 or not len(array):
        raise ValueError("expected a non-empty two-dimensional array")
    if not np.isfinite(array).all():
        raise ValueError("values contain non-finite entries")
    return array


def median_bandwidth(values: np.ndarray, *, seed: int, max_points: int = 512) -> float:
    """Return a deterministic median-distance Gaussian-kernel bandwidth."""
    array = _as_matrix(values)
    if len(array) > max_points:
        rng = np.random.default_rng(seed)
        array = array[rng.choice(len(array), size=max_points, replace=False)]
    distances = np.linalg.norm(array[:, None, :] - array[None, :, :], axis=2)
    upper = distances[np.triu_indices(len(array), k=1)]
    positive = upper[np.isfinite(upper) & (upper > 1e-12)]
    return float(np.median(positive)) if len(positive) else 1.0


@dataclass(frozen=True)
class GaussianRFF:
    """A frozen Gaussian-kernel random Fourier feature map."""

    mean: np.ndarray
    scale: np.ndarray
    frequencies: np.ndarray
    phase: np.ndarray
    bandwidth: float

    def transform(self, values: np.ndarray) -> np.ndarray:
        """Map observations to an approximate Gaussian-kernel feature space."""
        array = _as_matrix(values)
        standardized = (array - self.mean) / self.scale
        angle = standardized @ self.frequencies + self.phase
        return np.sqrt(2.0 / self.frequencies.shape[1]) * np.cos(angle)


def fit_gaussian_rff(
    values: np.ndarray,
    *,
    n_features: int,
    seed: int,
) -> GaussianRFF:
    """Fit a reproducible standardization and Gaussian RFF map on a reference set."""
    array = _as_matrix(values)
    if n_features < 2:
        raise ValueError("n_features must be at least two")
    mean = array.mean(axis=0)
    scale = array.std(axis=0, ddof=1)
    scale[~np.isfinite(scale) | (scale < 1e-8)] = 1.0
    standardized = (array - mean) / scale
    bandwidth = median_bandwidth(standardized, seed=seed + 17)
    rng = np.random.default_rng(seed)
    frequencies = rng.normal(
        loc=0.0,
        scale=1.0 / max(bandwidth, 1e-8),
        size=(array.shape[1], n_features),
    )
    phase = rng.uniform(0.0, 2.0 * np.pi, size=n_features)
    return GaussianRFF(mean, scale, frequencies, phase, bandwidth)


@dataclass(frozen=True)
class ConditionalTransitionModel:
    """Frozen approximation to the pooled conditional output distribution."""

    input_map: GaussianRFF
    output_map: GaussianRFF
    coefficients: np.ndarray
    intercept: np.ndarray
    ridge_alpha: float

    def predict_embedding(self, history: np.ndarray) -> np.ndarray:
        """Estimate the output-kernel mean embedding conditional on ``history``."""
        return self.input_map.transform(history) @ self.coefficients + self.intercept

    def residual_embedding(self, history: np.ndarray, outcome: np.ndarray) -> np.ndarray:
        """Return observed output features minus the pooled conditional embedding."""
        return self.output_map.transform(outcome) - self.predict_embedding(history)


def fit_conditional_transition_model(
    history: np.ndarray,
    outcome: np.ndarray,
    *,
    input_features: int = 128,
    output_features: int = 64,
    ridge_alpha: float = 10.0,
    seed: int = 0,
) -> ConditionalTransitionModel:
    """Fit an RFF conditional-mean embedding using only reference authors.

    A Gaussian kernel is characteristic on Euclidean output space, so the full
    infinite-dimensional mean embedding identifies the output distribution.  This
    finite RFF version is an explicitly approximate, regularized screen.
    """
    from sklearn.linear_model import Ridge

    h = _as_matrix(history)
    y = _as_matrix(outcome)
    if len(h) != len(y):
        raise ValueError("history and outcome must have the same number of rows")
    input_map = fit_gaussian_rff(h, n_features=input_features, seed=seed + 101)
    output_map = fit_gaussian_rff(y, n_features=output_features, seed=seed + 211)
    design = input_map.transform(h)
    target = output_map.transform(y)
    ridge = Ridge(alpha=ridge_alpha, fit_intercept=True).fit(design, target)
    return ConditionalTransitionModel(
        input_map=input_map,
        output_map=output_map,
        coefficients=np.asarray(ridge.coef_, dtype=float).T,
        intercept=np.asarray(ridge.intercept_, dtype=float),
        ridge_alpha=float(ridge_alpha),
    )
