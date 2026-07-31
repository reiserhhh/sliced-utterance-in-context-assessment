"""Truth-open audit for SUICA M4 mechanism-composition discovery."""
from __future__ import annotations

from itertools import combinations
from typing import Any

import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import spearmanr

from .m3_mechanism_audit import same_author_auc
from .m4_composition_contracts import (
    M4CompositionEstimate,
    M4CompositionTruth,
)


def _edge_key(
    edge: tuple[str, ...],
    mechanism_names: tuple[str, ...],
) -> str:
    index = {name: position for position, name in enumerate(mechanism_names)}
    values = tuple(sorted((index[name] for name in edge)))
    return "&".join(str(value) for value in values)


def _mean_metric(
    estimate: M4CompositionEstimate,
    name: str,
) -> np.ndarray:
    return 0.5 * (
        np.asarray(estimate.train_metrics[name], dtype=float)
        + np.asarray(estimate.test_metrics[name], dtype=float)
    )


def _safe_spearman(first: np.ndarray, second: np.ndarray) -> float:
    first = np.asarray(first, dtype=float)
    second = np.asarray(second, dtype=float)
    if np.std(first) <= 1e-12 or np.std(second) <= 1e-12:
        return float("nan")
    return float(spearmanr(first, second).statistic)


def _geometry(
    features: np.ndarray,
    parameters: np.ndarray,
) -> float:
    if features.ndim == 1:
        features = features[:, None]
    if parameters.ndim == 1:
        parameters = parameters[:, None]
    if len(features) < 3:
        return float("nan")
    return _safe_spearman(pdist(features), pdist(parameters))


def _target_profile(
    estimate: M4CompositionEstimate,
    truth: M4CompositionTruth,
    mechanism_names: tuple[str, ...],
) -> tuple[np.ndarray | None, np.ndarray | None]:
    if truth.world in {"synergy", "gate"} and truth.target_pair is not None:
        key = _edge_key(truth.target_pair, mechanism_names)
        return (
            _mean_metric(estimate, f"product_div|{key}")[:, None],
            truth.author_parameters["strength"],
        )
    if truth.world in {"redundancy", "suppression"}:
        if truth.target_pair is None:
            return None, None
        key = _edge_key(truth.target_pair, mechanism_names)
        return (
            _mean_metric(estimate, f"obs_div|{key}")[:, None],
            truth.author_parameters["dependence"],
        )
    if truth.world == "projection_order" and truth.target_pair is not None:
        key = _edge_key(truth.target_pair, mechanism_names)
        return (
            _mean_metric(estimate, f"commutator|{key}")[:, None],
            truth.author_parameters["dependence"],
        )
    if truth.world == "composite":
        observed: list[np.ndarray] = []
        planted: list[np.ndarray] = []
        parameter_names = ("strength", "secondary", "tertiary")
        for edge, parameter_name in zip(
            truth.active_hyperedges,
            parameter_names,
            strict=True,
        ):
            key = _edge_key(edge, mechanism_names)
            observed.append(_mean_metric(estimate, f"product_div|{key}"))
            planted.append(truth.author_parameters[parameter_name].ravel())
        return np.column_stack(observed), np.column_stack(planted)
    return None, None


def _candidate_edges(
    mechanism_names: tuple[str, ...],
    *,
    maximum_order: int = 3,
) -> tuple[tuple[str, ...], ...]:
    return tuple(
        edge
        for order in range(2, maximum_order + 1)
        for edge in combinations(mechanism_names, order)
    )


def diagnose_composition_kind(
    estimate: M4CompositionEstimate,
    mechanism_names: tuple[str, ...],
    *,
    support_threshold: float,
    observational_threshold: float,
    gate_threshold: float,
    commutator_threshold: float,
    null_value_threshold: float,
) -> str:
    """Assign a descriptive composition class without using generator truth."""
    refusal_rate = float(np.mean(
        np.logical_and(estimate.train_refusal, estimate.test_refusal)
    ))
    if refusal_rate >= 0.80:
        return "alias"

    heldout = float(np.mean(
        _mean_metric(estimate, "heldout_full_value")
    ))
    if heldout <= null_value_threshold:
        return "null"

    pairs = _candidate_edges(mechanism_names, maximum_order=2)
    triples = tuple(combinations(mechanism_names, 3))
    product_pair = {
        edge: float(np.mean(_mean_metric(
            estimate,
            f"product_div|{_edge_key(edge, mechanism_names)}",
        )))
        for edge in pairs
    }
    product_triple = {
        edge: float(np.mean(_mean_metric(
            estimate,
            f"product_div|{_edge_key(edge, mechanism_names)}",
        )))
        for edge in triples
    }
    observational_pair = {
        edge: float(np.mean(_mean_metric(
            estimate,
            f"obs_div|{_edge_key(edge, mechanism_names)}",
        )))
        for edge in pairs
    }
    commutator = {
        edge: float(np.mean(_mean_metric(
            estimate,
            f"commutator|{_edge_key(edge, mechanism_names)}",
        )))
        for edge in pairs
    }
    gate_values: dict[tuple[str, str], float] = {}
    positions = {name: index for index, name in enumerate(mechanism_names)}
    for gate, target in (
        (gate, target)
        for gate in mechanism_names
        for target in mechanism_names
        if gate != target
    ):
        gate_values[(gate, target)] = float(np.mean(_mean_metric(
            estimate,
            f"gate|{positions[gate]}->{positions[target]}",
        )))

    active_triples = [
        edge for edge, value in product_triple.items()
        if value >= support_threshold
    ]
    active_pairs = [
        edge for edge, value in product_pair.items()
        if value >= support_threshold
    ]
    if active_triples and len(active_pairs) >= 2:
        return "composite"
    if active_pairs:
        best_pair = max(active_pairs, key=product_pair.__getitem__)
        first, second = best_pair
        directional = max(
            gate_values[(first, second)],
            gate_values[(second, first)],
        )
        if directional >= gate_threshold:
            return "gate"
        return "synergy"

    ordered_pairs = [
        edge for edge, value in commutator.items()
        if value >= commutator_threshold
    ]
    if len(ordered_pairs) >= 2:
        return "projection_order_sensitive"
    minimum = min(observational_pair.values())
    maximum = max(observational_pair.values())
    if minimum <= -observational_threshold:
        return "redundancy"
    if maximum >= observational_threshold:
        return "suppression"
    return "additive_dependent"


def audit_m4_composition(
    estimate: M4CompositionEstimate,
    truth: M4CompositionTruth,
    mechanism_names: tuple[str, ...],
    *,
    support_threshold: float,
    observational_threshold: float,
    gate_threshold: float,
    commutator_threshold: float,
    null_value_threshold: float,
) -> dict[str, Any]:
    """Compare an anonymous estimate with the hidden synthetic mechanism."""
    candidate_edges = _candidate_edges(mechanism_names)
    estimated = {
        edge
        for edge in candidate_edges
        if float(np.mean(_mean_metric(
            estimate,
            f"product_div|{_edge_key(edge, mechanism_names)}",
        ))) >= support_threshold
    }
    expected = set(truth.active_hyperedges)
    true_positive = len(estimated.intersection(expected))
    precision = true_positive / len(estimated) if estimated else (
        1.0 if not expected else 0.0
    )
    recall = true_positive / len(expected) if expected else 1.0
    support_f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall > 0.0
        else 0.0
    )

    sign_checks: list[bool] = []
    for edge, expected_sign in truth.signed_hyperedges.items():
        key = _edge_key(edge, mechanism_names)
        observed_sign = float(np.sign(np.mean(_mean_metric(
            estimate,
            f"coefficient_sign|{key}",
        ))))
        sign_checks.append(observed_sign == expected_sign)
    sign_accuracy = float(np.mean(sign_checks)) if sign_checks else 1.0

    target, parameter = _target_profile(
        estimate,
        truth,
        mechanism_names,
    )
    target_geometry = (
        _geometry(target, parameter)
        if target is not None and parameter is not None
        else float("nan")
    )
    target_correlation = (
        _safe_spearman(target.ravel(), parameter.ravel())
        if target is not None
        and parameter is not None
        and target.shape[1] == 1
        else float("nan")
    )
    diagnosis = diagnose_composition_kind(
        estimate,
        mechanism_names,
        support_threshold=support_threshold,
        observational_threshold=observational_threshold,
        gate_threshold=gate_threshold,
        commutator_threshold=commutator_threshold,
        null_value_threshold=null_value_threshold,
    )
    refusal_rate = float(np.mean(
        np.logical_and(estimate.train_refusal, estimate.test_refusal)
    ))
    target_product = float("nan")
    target_observational = float("nan")
    target_commutator = float("nan")
    target_gate = float("nan")
    reverse_gate = float("nan")
    if truth.target_pair is not None:
        key = _edge_key(truth.target_pair, mechanism_names)
        target_product = float(np.mean(_mean_metric(
            estimate,
            f"product_div|{key}",
        )))
        target_observational = float(np.mean(_mean_metric(
            estimate,
            f"obs_div|{key}",
        )))
        target_commutator = float(np.mean(_mean_metric(
            estimate,
            f"commutator|{key}",
        )))
        if truth.world == "gate":
            positions = {
                name: index for index, name in enumerate(mechanism_names)
            }
            target_name = "condition"
            gate_name = "history"
            target_gate = float(np.mean(_mean_metric(
                estimate,
                f"gate|{positions[gate_name]}->{positions[target_name]}",
            )))
            reverse_gate = float(np.mean(_mean_metric(
                estimate,
                f"gate|{positions[target_name]}->{positions[gate_name]}",
            )))
    return {
        "world": truth.world,
        "expected_kind": truth.expected_kind,
        "diagnosed_kind": diagnosis,
        "kind_correct": diagnosis == truth.expected_kind,
        "same_author_auc": same_author_auc(
            estimate.train_signature,
            estimate.test_signature,
        ),
        "target_geometry_spearman": target_geometry,
        "target_parameter_spearman": target_correlation,
        "support_precision": float(precision),
        "support_recall": float(recall),
        "support_f1": float(support_f1),
        "sign_accuracy": sign_accuracy,
        "estimated_hyperedges": [
            "&".join(edge) for edge in sorted(estimated)
        ],
        "expected_hyperedges": [
            "&".join(edge) for edge in truth.active_hyperedges
        ],
        "refusal_rate": refusal_rate,
        "alias_refused": bool(not truth.alias or refusal_rate >= 0.80),
        "null_false_positive_rate": (
            float(len(estimated) / len(candidate_edges))
            if truth.world == "null"
            else float("nan")
        ),
        "mean_heldout_full_value": float(np.mean(
            _mean_metric(estimate, "heldout_full_value")
        )),
        "target_product_dividend": target_product,
        "target_observational_dividend": target_observational,
        "target_commutator": target_commutator,
        "target_gate_direction": target_gate,
        "reverse_gate_direction": reverse_gate,
    }
