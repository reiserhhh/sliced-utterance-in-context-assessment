"""Vector-valued pre-response applicability signatures for M4 charts."""
from __future__ import annotations

import numpy as np
from scipy.spatial.distance import pdist

from .m4_boundary_ecology import support_geometry
from .m4_condition_manifold_contracts import M4ConditionObserved
from .m4_response_safe_rcca_chart import M4RCCAChartTransform


def _nonmass(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    return matrix[:, 1:] if matrix.shape[1] > 1 else matrix


def _linear_cka(first: np.ndarray, second: np.ndarray) -> float:
    left = np.asarray(first, dtype=float)
    right = np.asarray(second, dtype=float)
    left = left - np.mean(left, axis=0, keepdims=True)
    right = right - np.mean(right, axis=0, keepdims=True)
    cross = np.linalg.norm(left.T @ right, ord="fro") ** 2
    scale = (
        np.linalg.norm(left.T @ left, ord="fro")
        * np.linalg.norm(right.T @ right, ord="fro")
    )
    return float(cross / max(scale, 1e-12))


def _normalized_gram(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    matrix = matrix - np.mean(matrix, axis=0, keepdims=True)
    gram = matrix @ matrix.T
    return gram / max(float(np.linalg.norm(gram, ord="fro")), 1e-12)


def _gram_distance(first: np.ndarray, second: np.ndarray) -> float:
    return float(np.linalg.norm(
        _normalized_gram(first) - _normalized_gram(second),
        ord="fro",
    ))


def _covariance(values: np.ndarray) -> np.ndarray:
    matrix = np.asarray(values, dtype=float)
    matrix = matrix - np.mean(matrix, axis=0, keepdims=True)
    return matrix.T @ matrix / max(len(matrix) - 1, 1)


def _covariance_drift(first: np.ndarray, second: np.ndarray) -> float:
    left = _covariance(first)
    right = _covariance(second)
    return float(
        np.linalg.norm(left - right, ord="fro")
        / max(
            np.linalg.norm(left, ord="fro")
            + np.linalg.norm(right, ord="fro"),
            1e-12,
        )
    )


def _procrustes_residual(first: np.ndarray, second: np.ndarray) -> float:
    left = np.asarray(first, dtype=float)
    right = np.asarray(second, dtype=float)
    left = left - np.mean(left, axis=0, keepdims=True)
    right = right - np.mean(right, axis=0, keepdims=True)
    u, _, vt = np.linalg.svd(left.T @ right, full_matrices=False)
    aligned = left @ (u @ vt)
    return float(
        np.linalg.norm(aligned - right, ord="fro")
        / max(
            np.linalg.norm(left, ord="fro")
            + np.linalg.norm(right, ord="fro"),
            1e-12,
        )
    )


def _spectral_entropy(values: np.ndarray) -> float:
    spectrum = np.maximum(np.asarray(values, dtype=float), 0.0)
    if float(np.sum(spectrum)) <= 1e-12:
        return 0.0
    probabilities = spectrum / np.sum(spectrum)
    entropy = -np.sum(
        probabilities * np.log(np.maximum(probabilities, 1e-12))
    )
    return float(entropy / max(np.log(len(probabilities)), 1e-12))


def m4_applicability_signature(
    observed: M4ConditionObserved,
    chart: M4RCCAChartTransform,
    bases: dict[str, dict[str, np.ndarray]],
) -> dict[str, float]:
    """Extract a fixed response-safe signature from one chart cell."""
    geometry = support_geometry(chart, observed)
    distances = (
        geometry.role_distances["mechanism_evaluation"]
        / max(geometry.threshold, 1e-12)
    )
    outside = ~geometry.role_masks["mechanism_evaluation"]
    r_calibration = _nonmass(bases["R"]["calibration"])
    r_selection = _nonmass(bases["R"]["selection"])
    r_evaluation = _nonmass(bases["R"]["evaluation"])
    b_calibration = _nonmass(bases["B0"]["calibration"])
    b_selection = _nonmass(bases["B0"]["selection"])
    b_evaluation = _nonmass(bases["B0"]["evaluation"])
    leverage_scale = max(
        float(np.mean(np.linalg.norm(r_calibration, axis=1))),
        1e-12,
    )
    leverage = np.linalg.norm(r_evaluation, axis=1) / leverage_scale
    tail = leverage[outside]
    left, right = chart.transform_source_prototypes(
        observed.mechanism_evaluation.pre_context
    )
    source_scale = max(
        float(np.sqrt(
            np.mean(np.sum(left**2, axis=1))
            + np.mean(np.sum(right**2, axis=1))
        )),
        1e-12,
    )
    centroid_shift = float(
        np.linalg.norm(
            np.mean(r_evaluation, axis=0)
            - np.mean(r_selection, axis=0)
        )
        / max(
            np.sqrt(np.mean(np.sum(r_selection**2, axis=1))),
            1e-12,
        )
    )
    distance_correlation = np.corrcoef(
        pdist(r_evaluation),
        pdist(b_evaluation),
    )[0, 1]
    return {
        "support_minimum_coverage": geometry.minimum_coverage,
        "support_eval_distance_median": float(np.median(distances)),
        "support_eval_distance_p90": float(np.quantile(distances, 0.9)),
        "support_eval_distance_maximum": float(np.max(distances)),
        "support_eval_mean_excess": float(
            np.mean(np.maximum(distances - 1.0, 0.0))
        ),
        "tail_fraction": float(np.mean(outside)),
        "tail_leverage_mean": (
            float(np.mean(tail)) if len(tail) else 0.0
        ),
        "tail_leverage_concentration": (
            float(np.max(tail) / max(np.sum(tail), 1e-12))
            if len(tail)
            else 0.0
        ),
        "source_linear_cka": _linear_cka(left, right),
        "source_procrustes_residual": _procrustes_residual(left, right),
        "source_centroid_distance": float(
            np.linalg.norm(np.mean(left, axis=0) - np.mean(right, axis=0))
            / source_scale
        ),
        "panel_covariance_drift": _covariance_drift(
            r_selection,
            r_evaluation,
        ),
        "panel_centroid_shift": centroid_shift,
        "rb_gram_calibration": _gram_distance(
            r_calibration,
            b_calibration,
        ),
        "rb_gram_selection": _gram_distance(
            r_selection,
            b_selection,
        ),
        "rb_gram_evaluation": _gram_distance(
            r_evaluation,
            b_evaluation,
        ),
        "rb_distance_correlation_evaluation": float(
            np.nan_to_num(distance_correlation)
        ),
        "shared_rank": float(chart.shared_rank),
        "canonical_spectral_entropy": _spectral_entropy(
            chart.canonical_singular_values[: chart.shared_rank]
        ),
        "minimum_support_stability_lcb": float(
            min(chart.support_stability_lcb)
        ),
        "heldout_source_cka": float(chart.heldout_source_cka),
        "maximum_condition_number": float(max(chart.condition_numbers)),
        "maximum_negative_spectral_mass": float(
            max(chart.negative_spectral_mass)
        ),
        "maximum_asymmetric_mass": float(max(chart.asymmetric_mass)),
    }
