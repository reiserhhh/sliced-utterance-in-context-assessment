"""Truth-open audit for M4 dynamic transition-kernel discovery."""
from __future__ import annotations

from typing import Any

import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import spearmanr

from .m3_mechanism_audit import same_author_auc
from .m4_dynamic_kernel_contracts import (
    M4DynamicKernelEstimate,
    M4DynamicKernelTruth,
)


def _mean_metric(
    estimate: M4DynamicKernelEstimate,
    name: str,
) -> np.ndarray:
    return 0.5 * (
        estimate.train_metrics[name] + estimate.test_metrics[name]
    )


def _spearman(first: np.ndarray, second: np.ndarray) -> float:
    first = np.asarray(first, dtype=float).ravel()
    second = np.asarray(second, dtype=float).ravel()
    if np.std(first) <= 1e-12 or np.std(second) <= 1e-12:
        return float("nan")
    return float(spearmanr(first, second).statistic)


def _geometry(first: np.ndarray, second: np.ndarray) -> float:
    first = np.asarray(first, dtype=float)
    second = np.asarray(second, dtype=float)
    if first.ndim == 1:
        first = first[:, None]
    if second.ndim == 1:
        second = second[:, None]
    return _spearman(pdist(first), pdist(second))


def audit_m4_dynamic_kernel(
    estimate: M4DynamicKernelEstimate,
    truth: M4DynamicKernelTruth,
    *,
    minimum_order_margin: float,
    minimum_resolvable_commutator: float,
    maximum_commuting_commutator: float,
) -> dict[str, Any]:
    """Evaluate order recovery, temporal gate direction, and alias refusal."""
    refusal_rate = float(np.mean(
        np.logical_and(estimate.train_refusal, estimate.test_refusal)
    ))
    order_margin = _mean_metric(estimate, "order_margin")
    commutator = _mean_metric(estimate, "commutator")
    gate_h_to_c = _mean_metric(estimate, "gate_h_to_c")
    gate_c_to_h = _mean_metric(estimate, "gate_c_to_h")
    gate_margin = _mean_metric(estimate, "gate_direction_margin")
    path_gain = _mean_metric(estimate, "path_logscore_gain")

    truth_commutator = truth.author_parameters["commutator"].ravel()
    resolvable = truth_commutator >= minimum_resolvable_commutator
    if truth.expected_order == "history_after_condition":
        order_accuracy = float(np.mean(
            order_margin[resolvable] >= minimum_order_margin
        ))
    elif truth.expected_order == "condition_after_history":
        order_accuracy = float(np.mean(
            order_margin[resolvable] <= -minimum_order_margin
        ))
    elif truth.expected_order == "commuting":
        order_accuracy = float(np.mean(
            np.abs(order_margin) < minimum_order_margin
        ))
    else:
        order_accuracy = float(refusal_rate >= 0.80)

    commutator_parameter = truth.author_parameters["commutator"]
    gate_parameter = truth.author_parameters["gate_strength"]
    return {
        "world": truth.world,
        "expected_order": truth.expected_order,
        "same_author_auc": same_author_auc(
            estimate.train_signature,
            estimate.test_signature,
        ),
        "order_accuracy": order_accuracy,
        "mean_order_margin": float(np.mean(order_margin)),
        "mean_commutator": float(np.mean(commutator)),
        "commutator_geometry": (
            _geometry(commutator, commutator_parameter)
            if np.std(commutator_parameter) > 1e-12
            else float("nan")
        ),
        "commutator_parameter_spearman": (
            _spearman(commutator, commutator_parameter)
            if np.std(commutator_parameter) > 1e-12
            else float("nan")
        ),
        "commuting_control_pass": bool(
            truth.expected_order != "commuting"
            or float(np.mean(commutator)) <= maximum_commuting_commutator
        ),
        "mean_gate_h_to_c": float(np.mean(gate_h_to_c)),
        "mean_gate_c_to_h": float(np.mean(gate_c_to_h)),
        "mean_gate_direction_margin": float(np.mean(gate_margin)),
        "gate_parameter_spearman": (
            _spearman(gate_h_to_c, gate_parameter)
            if np.std(gate_parameter) > 1e-12
            else float("nan")
        ),
        "mean_path_logscore_gain": float(np.mean(path_gain)),
        "refusal_rate": refusal_rate,
        "alias_refused": bool(not truth.alias or refusal_rate >= 0.80),
    }
