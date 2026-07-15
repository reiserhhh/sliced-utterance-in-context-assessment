"""Analytic identities used by the V6 simulation worlds."""
from __future__ import annotations

import numpy as np


def stationary_mean_variance(gamma: np.ndarray, m: int) -> np.ndarray:
    """T1': covariance of an m-point mean for a stationary process.

    ``gamma[h]`` is the (possibly matrix-valued) autocovariance at lag h.
    For multivariate input the symmetric contribution is Gamma_h + Gamma_h.T.
    """
    gamma = np.asarray(gamma, dtype=float)
    if m < 1 or gamma.shape[0] < m:
        raise ValueError("gamma must contain lags 0 through m-1")
    total = m * gamma[0]
    for h in range(1, m):
        term = gamma[h] if gamma.ndim == 1 else gamma[h] + gamma[h].T
        total = total + (m - h) * (2.0 * term if gamma.ndim == 1 else term)
    return total / (m * m)


def endpoint_flow_variance(flow_cov: np.ndarray, gamma0: np.ndarray,
                           gamma_endpoint: np.ndarray, m: int) -> np.ndarray:
    """T2': covariance of (X[m-1]-X[0])/(m-1), including endpoint memory."""
    if m < 2:
        raise ValueError("m must be at least 2")
    flow_cov = np.asarray(flow_cov, dtype=float)
    gamma0 = np.asarray(gamma0, dtype=float)
    gamma_endpoint = np.asarray(gamma_endpoint, dtype=float)
    correction = (2 * gamma0 - gamma_endpoint - np.swapaxes(gamma_endpoint, -1, -2))
    return flow_cov + correction / ((m - 1) ** 2)


def three_point_mixed_moments(flow_cov: np.ndarray, gamma: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """T2' moments for ell=(X2-X0)/2 and q=(X0-2X1+X2)/sqrt(6)."""
    flow_cov = np.asarray(flow_cov, float)
    gamma = np.asarray(gamma, float)
    if gamma.shape[0] < 3:
        raise ValueError("gamma requires lags 0, 1, and 2")
    g0, g1, g2 = gamma[:3]
    cov_ell = flow_cov + (2 * g0 - g2 - g2.T) / 4
    cov_q = (6 * g0 - 4 * (g1 + g1.T) + g2 + g2.T) / 6
    cross = (-g2 + 2 * g1 - 2 * g1.T + g2.T) / (2 * np.sqrt(6))
    return cov_ell, cov_q, cross


def conditional_innovation(covariance: np.ndarray, observed: list[int], target: list[int],
                           tol: float = 1e-9) -> tuple[np.ndarray, int]:
    """T8': Schur-complement innovation covariance and numerical rank."""
    covariance = np.asarray(covariance, float)
    xx = covariance[np.ix_(observed, observed)]
    yy = covariance[np.ix_(target, target)]
    yx = covariance[np.ix_(target, observed)]
    schur = (yy - yx @ np.linalg.pinv(xx, rcond=tol) @ yx.T)
    schur = (schur + schur.T) / 2
    scale = max(1.0, float(np.linalg.norm(schur, ord=2)))
    return schur, int(np.linalg.matrix_rank(schur, tol=tol * scale))
