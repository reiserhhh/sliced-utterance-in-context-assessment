"""Conditional uncertainty accounting for frozen SUICA V7 geometry profiles."""
from __future__ import annotations

from typing import Any

import numpy as np


_COMPONENTS = ("source_cluster", "model_refit", "reference_norm")


def _draws(values: Any, *, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or len(array) < 2 or not np.isfinite(array).all():
        raise ValueError(f"{name} must be a finite one-dimensional draw vector with at least two values.")
    return array


def summarize_geometry_uncertainty(
    *,
    source_cluster_draws: Any,
    model_refit_draws: Any,
    reference_norm_draws: Any,
    support_status: str,
    joint_nested_draws: Any | None = None,
    independence_declared: bool = False,
) -> dict[str, Any]:
    """Separate uncertainty sources before exposing one conditional score error.

    Source cluster draws resample an author's non-overlapping source units;
    model-refit draws rerun discovery representation/aggregation fitting; and
    reference-norm draws resample the frozen reference population. A total SEM
    is only emitted from joint nested draws, or from an explicitly declared
    independence approximation. The latter remains an assumption, not a
    measured total-variance decomposition.
    """
    if str(support_status) != "GEOMETRY_PROFILE_READY":
        return {
            "status": "REFUSE_GEOMETRY_UNCERTAINTY_OUT_OF_SUPPORT",
            "support_status": str(support_status),
            "claim_boundary": "Unsupported geometry rows cannot receive a precision estimate.",
        }
    components = {
        "source_cluster": _draws(source_cluster_draws, name="source_cluster_draws"),
        "model_refit": _draws(model_refit_draws, name="model_refit_draws"),
        "reference_norm": _draws(reference_norm_draws, name="reference_norm_draws"),
    }
    component_summary = {
        name: {
            "n_draws": int(len(values)),
            "mean": float(values.mean()),
            "variance": float(np.var(values, ddof=1)),
            "conditional_sem": float(np.std(values, ddof=1)),
        }
        for name, values in components.items()
    }
    if joint_nested_draws is not None:
        total = _draws(joint_nested_draws, name="joint_nested_draws")
        return {
            "status": "CONDITIONAL_GEOMETRY_UNCERTAINTY_READY",
            "combination_method": "JOINT_NESTED_DRAWS",
            "component_summary": component_summary,
            "total_n_draws": int(len(total)),
            "total_conditional_sem": float(np.std(total, ddof=1)),
            "total_interval_95": [float(np.quantile(total, 0.025)), float(np.quantile(total, 0.975))],
            "claim_boundary": "Conditional score uncertainty only; not trait reliability, G coefficient, or clinical precision.",
        }
    component_variance_sum = float(sum(entry["variance"] for entry in component_summary.values()))
    if independence_declared:
        return {
            "status": "CONDITIONAL_GEOMETRY_UNCERTAINTY_INDEPENDENCE_APPROXIMATION",
            "combination_method": "SUM_OF_COMPONENT_VARIANCES_UNDER_DECLARED_INDEPENDENCE",
            "component_summary": component_summary,
            "total_conditional_sem": float(np.sqrt(component_variance_sum)),
            "claim_boundary": "Approximate conditional uncertainty under an untested independence assumption; not a final total error estimate.",
        }
    return {
        "status": "REFUSE_TOTAL_GEOMETRY_UNCERTAINTY_DEPENDENCE_UNMODELED",
        "component_summary": component_summary,
        "claim_boundary": "Component variability is reported, but no total SEM is emitted without joint nested draws or an explicit approximation.",
    }
