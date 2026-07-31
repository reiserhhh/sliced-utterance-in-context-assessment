"""Estimator for noncommuting M4 transition kernels and temporal gates."""
from __future__ import annotations

import numpy as np

from .m4_dynamic_kernel_contracts import (
    M4DynamicKernelEstimate,
    M4DynamicKernelObserved,
    validate_dynamic_kernel_estimate,
    validate_dynamic_kernel_observed,
)
from .m4_dynamic_kernel_generator import (
    REGIME_CONDITION,
    REGIME_HISTORY,
    REGIME_JOINT,
)


AffineMap = tuple[np.ndarray, np.ndarray]


def _fit_affine(
    pre: np.ndarray,
    post: np.ndarray,
    *,
    ridge: float,
) -> AffineMap:
    design = np.column_stack([pre, np.ones(len(pre))])
    penalty = ridge * np.eye(design.shape[1])
    penalty[-1, -1] = 0.0
    coefficient = np.linalg.solve(
        design.T @ design + penalty,
        design.T @ post,
    )
    return coefficient[:-1].T, coefficient[-1]


def _apply(mapping: AffineMap, values: np.ndarray) -> np.ndarray:
    matrix, offset = mapping
    return values @ matrix.T + offset


def _compose(second: AffineMap, first: AffineMap) -> AffineMap:
    """Compose affine maps as second(first(x))."""
    second_matrix, second_offset = second
    first_matrix, first_offset = first
    return (
        second_matrix @ first_matrix,
        second_matrix @ first_offset + second_offset,
    )


def _calibration_maps(
    pre: np.ndarray,
    post: np.ndarray,
    driver: np.ndarray,
    regime: np.ndarray,
    target_regime: int,
    *,
    ridge: float,
    minimum: int,
) -> dict[int, AffineMap] | None:
    output: dict[int, AffineMap] = {}
    for sign in (-1, 1):
        mask = (regime == target_regime) & (driver == sign)
        if int(np.sum(mask)) < minimum:
            return None
        output[sign] = _fit_affine(
            pre[mask],
            post[mask],
            ridge=ridge,
        )
    return output


def _ordered_prediction(
    pre: np.ndarray,
    condition: np.ndarray,
    history: np.ndarray,
    condition_maps: dict[int, AffineMap],
    history_maps: dict[int, AffineMap],
    *,
    forward: bool,
) -> np.ndarray:
    prediction = np.empty_like(pre)
    for condition_sign in (-1, 1):
        for history_sign in (-1, 1):
            mask = (
                (condition == condition_sign)
                & (history == history_sign)
            )
            first = condition_maps[condition_sign]
            second = history_maps[history_sign]
            mapping = (
                _compose(second, first)
                if forward
                else _compose(first, second)
            )
            prediction[mask] = _apply(mapping, pre[mask])
    return prediction


def _fit_gate(
    residual: np.ndarray,
    condition: np.ndarray,
    history: np.ndarray,
    *,
    ridge: float,
) -> np.ndarray:
    h_to_c = condition * (history > 0.0)
    c_to_h = history * (condition > 0.0)
    design = np.column_stack([
        np.ones(len(condition)),
        h_to_c,
        c_to_h,
    ])
    penalty = ridge * np.eye(design.shape[1])
    penalty[0, 0] = 0.0
    return np.linalg.solve(
        design.T @ design + penalty,
        design.T @ residual,
    )


def _apply_gate(
    coefficient: np.ndarray,
    condition: np.ndarray,
    history: np.ndarray,
) -> np.ndarray:
    design = np.column_stack([
        np.ones(len(condition)),
        condition * (history > 0.0),
        history * (condition > 0.0),
    ])
    return design @ coefficient


def _commutator(
    condition_maps: dict[int, AffineMap],
    history_maps: dict[int, AffineMap],
) -> float:
    values: list[float] = []
    scales: list[float] = []
    for condition_sign in (-1, 1):
        for history_sign in (-1, 1):
            condition_matrix = condition_maps[condition_sign][0]
            history_matrix = history_maps[history_sign][0]
            values.append(np.linalg.norm(
                history_matrix @ condition_matrix
                - condition_matrix @ history_matrix,
                ord="fro",
            ))
            scales.append(
                np.linalg.norm(condition_matrix, ord="fro")
                * np.linalg.norm(history_matrix, ord="fro")
            )
    return float(np.mean(values) / max(np.mean(scales), 1e-12))


def _one_fold(
    *,
    pre_fit: np.ndarray,
    post_fit: np.ndarray,
    condition_fit: np.ndarray,
    history_fit: np.ndarray,
    regime_fit: np.ndarray,
    pre_eval: np.ndarray,
    post_eval: np.ndarray,
    condition_eval: np.ndarray,
    history_eval: np.ndarray,
    regime_eval: np.ndarray,
    ridge: float,
    minimum_calibration_events: int,
) -> dict[str, float]:
    condition_maps = _calibration_maps(
        pre_fit,
        post_fit,
        condition_fit,
        regime_fit,
        REGIME_CONDITION,
        ridge=ridge,
        minimum=minimum_calibration_events,
    )
    history_maps = _calibration_maps(
        pre_fit,
        post_fit,
        history_fit,
        regime_fit,
        REGIME_HISTORY,
        ridge=ridge,
        minimum=minimum_calibration_events,
    )
    if condition_maps is None or history_maps is None:
        return {
            "refusal": 1.0,
            "commutator": 0.0,
            "order_margin": 0.0,
            "gate_h_to_c": 0.0,
            "gate_c_to_h": 0.0,
            "gate_direction_margin": 0.0,
            "path_logscore_gain": 0.0,
            "selected_forward": 0.5,
        }

    fit_joint = regime_fit == REGIME_JOINT
    eval_joint = regime_eval == REGIME_JOINT
    if (
        int(np.sum(fit_joint)) < minimum_calibration_events
        or int(np.sum(eval_joint)) < minimum_calibration_events
    ):
        return {
            "refusal": 1.0,
            "commutator": 0.0,
            "order_margin": 0.0,
            "gate_h_to_c": 0.0,
            "gate_c_to_h": 0.0,
            "gate_direction_margin": 0.0,
            "path_logscore_gain": 0.0,
            "selected_forward": 0.5,
        }

    candidate_errors: dict[bool, float] = {}
    candidate_gates: dict[bool, np.ndarray] = {}
    for forward in (True, False):
        fit_base = _ordered_prediction(
            pre_fit[fit_joint],
            condition_fit[fit_joint],
            history_fit[fit_joint],
            condition_maps,
            history_maps,
            forward=forward,
        )
        gate = _fit_gate(
            post_fit[fit_joint] - fit_base,
            condition_fit[fit_joint],
            history_fit[fit_joint],
            ridge=ridge,
        )
        eval_base = _ordered_prediction(
            pre_eval[eval_joint],
            condition_eval[eval_joint],
            history_eval[eval_joint],
            condition_maps,
            history_maps,
            forward=forward,
        )
        prediction = eval_base + _apply_gate(
            gate,
            condition_eval[eval_joint],
            history_eval[eval_joint],
        )
        candidate_errors[forward] = float(np.mean(
            (post_eval[eval_joint] - prediction) ** 2
        ))
        candidate_gates[forward] = gate

    forward_error = candidate_errors[True]
    reverse_error = candidate_errors[False]
    chosen_forward = forward_error <= reverse_error
    chosen_error = min(forward_error, reverse_error)
    chosen_gate = candidate_gates[chosen_forward]
    order_margin = (
        (reverse_error - forward_error)
        / (reverse_error + forward_error + 1e-12)
    )

    pooled = _fit_affine(pre_fit, post_fit, ridge=ridge)
    baseline_prediction = _apply(pooled, pre_eval[eval_joint])
    baseline_error = float(np.mean(
        (post_eval[eval_joint] - baseline_prediction) ** 2
    ))
    logscore_gain = 0.5 * np.log(
        max(baseline_error, 1e-12) / max(chosen_error, 1e-12)
    )
    h_to_c = float(np.linalg.norm(chosen_gate[1]))
    c_to_h = float(np.linalg.norm(chosen_gate[2]))
    return {
        "refusal": 0.0,
        "commutator": _commutator(condition_maps, history_maps),
        "order_margin": float(order_margin),
        "gate_h_to_c": h_to_c,
        "gate_c_to_h": c_to_h,
        "gate_direction_margin": float(
            (h_to_c - c_to_h) / (h_to_c + c_to_h + 1e-12)
        ),
        "path_logscore_gain": float(logscore_gain),
        "selected_forward": float(chosen_forward),
    }


def _estimate_author(
    *,
    pre: np.ndarray,
    post: np.ndarray,
    condition: np.ndarray,
    history: np.ndarray,
    regime: np.ndarray,
    ridge: float,
    minimum_calibration_events: int,
) -> dict[str, float]:
    occasions = pre.shape[0]
    rows: list[dict[str, float]] = []
    for parity in (0, 1):
        fit = np.arange(occasions) % 2 == parity
        evaluate = ~fit
        rows.append(_one_fold(
            pre_fit=pre[fit].reshape(-1, pre.shape[-1]),
            post_fit=post[fit].reshape(-1, post.shape[-1]),
            condition_fit=condition[fit].reshape(-1),
            history_fit=history[fit].reshape(-1),
            regime_fit=regime[fit].reshape(-1),
            pre_eval=pre[evaluate].reshape(-1, pre.shape[-1]),
            post_eval=post[evaluate].reshape(-1, post.shape[-1]),
            condition_eval=condition[evaluate].reshape(-1),
            history_eval=history[evaluate].reshape(-1),
            regime_eval=regime[evaluate].reshape(-1),
            ridge=ridge,
            minimum_calibration_events=minimum_calibration_events,
        ))
    names = rows[0].keys()
    return {
        name: float(np.mean([row[name] for row in rows]))
        for name in names
    }


def _panel_metrics(
    *,
    pre: np.ndarray,
    post: np.ndarray,
    condition: np.ndarray,
    history: np.ndarray,
    regime: np.ndarray,
    ridge: float,
    minimum_calibration_events: int,
) -> dict[str, np.ndarray]:
    rows = [
        _estimate_author(
            pre=pre[author],
            post=post[author],
            condition=condition[author],
            history=history[author],
            regime=regime[author],
            ridge=ridge,
            minimum_calibration_events=minimum_calibration_events,
        )
        for author in range(len(pre))
    ]
    names = tuple(sorted(rows[0]))
    return {
        name: np.asarray([row[name] for row in rows], dtype=float)
        for name in names
    }


def fit_m4_dynamic_kernel(
    observed: M4DynamicKernelObserved,
    *,
    ridge: float = 0.03,
    minimum_calibration_events: int = 12,
) -> M4DynamicKernelEstimate:
    """Estimate independent-panel order, gate, and commutator signatures."""
    validate_dynamic_kernel_observed(observed)
    train = _panel_metrics(
        pre=observed.pre_train,
        post=observed.post_train,
        condition=observed.condition_train,
        history=observed.history_train,
        regime=observed.regime_train,
        ridge=ridge,
        minimum_calibration_events=minimum_calibration_events,
    )
    test = _panel_metrics(
        pre=observed.pre_test,
        post=observed.post_test,
        condition=observed.condition_test,
        history=observed.history_test,
        regime=observed.regime_test,
        ridge=ridge,
        minimum_calibration_events=minimum_calibration_events,
    )
    names = tuple(
        name for name in sorted(train)
        if name not in {"refusal", "selected_forward"}
    )
    train_raw = np.column_stack([train[name] for name in names])
    test_raw = np.column_stack([test[name] for name in names])
    center = train_raw.mean(axis=0, keepdims=True)
    scale = train_raw.std(axis=0, ddof=0, keepdims=True)
    scale = np.where(scale > 1e-8, scale, 1.0)
    estimate = M4DynamicKernelEstimate(
        train_signature=(train_raw - center) / scale,
        test_signature=(test_raw - center) / scale,
        feature_names=names,
        train_metrics=train,
        test_metrics=test,
        train_refusal=train["refusal"].astype(bool),
        test_refusal=test["refusal"].astype(bool),
    )
    validate_dynamic_kernel_estimate(
        estimate,
        authors=observed.pre_train.shape[0],
    )
    return estimate
