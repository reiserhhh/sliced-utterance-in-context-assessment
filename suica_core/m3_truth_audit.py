"""Independent truth and invariance audits for SUICA M3."""
from __future__ import annotations

from dataclasses import fields
from typing import Any

import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import spearmanr

from .m3_contracts import (
    M3DesignManifest,
    M3EstimatePacket,
    M3ObservedPacket,
    M3TruthPacket,
    coarse_grain_homogeneous_replicates,
    transform_responses,
)
from .m3_meso_estimator import fit_m3_meso


def _correlation(left: np.ndarray, right: np.ndarray) -> float:
    x = np.asarray(left, dtype=float).ravel()
    y = np.asarray(right, dtype=float).ravel()
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 3:
        return float("nan")
    x = x[mask]
    y = y[mask]
    if np.std(x) <= 1e-12 or np.std(y) <= 1e-12:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def _distance_spearman(left: np.ndarray, right: np.ndarray) -> float:
    first = pdist(np.asarray(left, dtype=float).reshape(len(left), -1))
    second = pdist(np.asarray(right, dtype=float).reshape(len(right), -1))
    if not np.isfinite(first).all() or not np.isfinite(second).all():
        return float("nan")
    if np.std(first) <= 1e-12 or np.std(second) <= 1e-12:
        return float("nan")
    return float(spearmanr(first, second).statistic)


def _nrmse(estimate: np.ndarray, truth: np.ndarray) -> float:
    observed = np.asarray(estimate, dtype=float)
    target = np.asarray(truth, dtype=float)
    mask = np.isfinite(observed) & np.isfinite(target)
    if not mask.any():
        return float("nan")
    error = float(np.sqrt(np.mean((observed[mask] - target[mask]) ** 2)))
    scale = float(np.sqrt(np.mean(target[mask] ** 2)))
    return error / max(scale, 1e-12)


def _jensen_shannon(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    first = np.asarray(left, dtype=float)
    second = np.asarray(right, dtype=float)
    midpoint = 0.5 * (first + second)
    return 0.5 * np.sum(
        first * np.log((first + 1e-12) / (midpoint + 1e-12))
        + second * np.log((second + 1e-12) / (midpoint + 1e-12)),
        axis=1,
    )


def audit_m3_truth(
    estimate: M3EstimatePacket,
    truth: M3TruthPacket,
) -> dict[str, Any]:
    """Compare one estimate packet against held-out synthetic truth."""
    metrics: dict[str, Any] = {
        "response_status": estimate.response_status,
        "state_status": estimate.state_status,
        "choice_js_median": float(np.median(_jensen_shannon(
            estimate.choice_stationary,
            truth.choice_stationary,
        ))),
        "choice_correlation": _correlation(
            estimate.choice_stationary,
            truth.choice_stationary,
        ),
        "choice_transition_correlation": _correlation(
            estimate.choice_transition,
            truth.choice_transition,
        ),
        "heldout_choice_log_skill": float(
            estimate.heldout_choice_log_skill
        ),
        "heldout_response_r2_linear": float(
            estimate.heldout_response_r2_linear
        ),
        "heldout_response_r2_full": float(
            estimate.heldout_response_r2_full
        ),
        "heldout_nonlinear_incremental_r2": float(
            estimate.heldout_response_r2_full
            - estimate.heldout_response_r2_linear
        ),
        "information_choice_mean": float(
            np.mean(truth.information_choice)
        ),
        "information_response_mean": float(
            np.mean(truth.information_response)
        ),
    }
    if estimate.response_status in {
        "RESPONSE_OK",
        "RESPONSE_OBSERVATIONAL_ONLY",
    }:
        metrics.update({
            "position_correlation": _correlation(
                estimate.author_position,
                truth.author_position,
            ),
            "position_distance_spearman": _distance_spearman(
                estimate.author_position,
                truth.author_position,
            ),
            "position_nrmse": _nrmse(
                estimate.author_position,
                truth.author_position,
            ),
            "operator_correlation": _correlation(
                estimate.response_operator,
                truth.response_operator,
            ),
            "operator_distance_spearman": _distance_spearman(
                estimate.response_operator,
                truth.response_operator,
            ),
            "operator_nrmse": _nrmse(
                estimate.response_operator,
                truth.response_operator,
            ),
            "nonlinear_correlation": _correlation(
                estimate.nonlinear_field,
                truth.nonlinear_field,
            ),
            "nonlinear_distance_spearman": _distance_spearman(
                estimate.nonlinear_field,
                truth.nonlinear_field,
            ),
            "nonlinear_nrmse": _nrmse(
                estimate.nonlinear_field,
                truth.nonlinear_field,
            ),
            "field_correlation": _correlation(
                estimate.response_field,
                truth.response_field,
            ),
        })
    if estimate.state_status == "STATE_OK":
        metrics.update({
            "state_correlation": _correlation(
                estimate.occasion_state,
                truth.occasion_state,
            ),
            "state_nrmse": _nrmse(
                estimate.occasion_state,
                truth.occasion_state,
            ),
        })
    return metrics


def audit_m3_invariance(
    observed: M3ObservedPacket,
    manifest: M3DesignManifest,
    *,
    seed: int,
) -> dict[str, float]:
    """Refit after rotation, translation, and homogeneous coarsening attacks."""
    baseline = fit_m3_meso(observed, manifest)
    dimension = int(observed.fixed_responses_train.shape[-1])
    rng = np.random.default_rng(seed)
    rotation = np.linalg.qr(rng.normal(size=(dimension, dimension)))[0]
    shift = rng.normal(size=dimension)

    rotated = fit_m3_meso(
        transform_responses(observed, matrix=rotation),
        manifest,
    )
    translated = fit_m3_meso(
        transform_responses(observed, shift=shift),
        manifest,
    )
    coarse = fit_m3_meso(
        coarse_grain_homogeneous_replicates(
            observed,
            block_size=2,
        ),
        manifest,
    )

    rotated_position_back = rotated.author_position @ rotation
    rotated_operator_back = np.einsum(
        "ij,ujk->uik",
        rotation.T,
        rotated.response_operator,
    )
    rotated_nonlinear_back = rotated.nonlinear_field @ rotation
    metrics = {
        "rotation_position_max_abs": float(np.nanmax(np.abs(
            rotated_position_back - baseline.author_position
        ))),
        "rotation_operator_max_abs": float(np.nanmax(np.abs(
            rotated_operator_back - baseline.response_operator
        ))),
        "rotation_nonlinear_max_abs": float(np.nanmax(np.abs(
            rotated_nonlinear_back - baseline.nonlinear_field
        ))),
        "rotation_position_geometry": _distance_spearman(
            baseline.author_position,
            rotated.author_position,
        ),
        "rotation_operator_geometry": _distance_spearman(
            baseline.response_operator,
            rotated.response_operator,
        ),
        "translation_position_max_abs": float(np.nanmax(np.abs(
            translated.author_position - baseline.author_position
        ))),
        "translation_operator_max_abs": float(np.nanmax(np.abs(
            translated.response_operator - baseline.response_operator
        ))),
        "translation_nonlinear_max_abs": float(np.nanmax(np.abs(
            translated.nonlinear_field - baseline.nonlinear_field
        ))),
        "coarse_position_max_abs": float(np.nanmax(np.abs(
            coarse.author_position - baseline.author_position
        ))),
        "coarse_operator_max_abs": float(np.nanmax(np.abs(
            coarse.response_operator - baseline.response_operator
        ))),
        "coarse_nonlinear_max_abs": float(np.nanmax(np.abs(
            coarse.nonlinear_field - baseline.nonlinear_field
        ))),
    }
    return metrics


def packet_has_truth_leakage(packet: M3ObservedPacket) -> bool:
    """Return true if an observed contract exposes a truth-like field name."""
    forbidden = {
        "truth",
        "systematic",
        "world",
        "rank",
        "basis",
        "parameter",
        "latent",
    }
    return any(
        any(token in item.name.lower() for token in forbidden)
        for item in fields(packet)
    )
