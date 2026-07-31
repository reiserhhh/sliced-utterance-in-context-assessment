"""Truth-open audit for M4-B opportunity-ecology discovery."""
from __future__ import annotations

from typing import Any

import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import spearmanr
from sklearn.metrics import f1_score

from .m3_mechanism_audit import same_author_auc
from .m4_opportunity_contracts import (
    M4OpportunityEstimate,
    M4OpportunityTruth,
)


MECHANISMS = ("selection", "creation", "gate", "return")


def _mean_metric(
    estimate: M4OpportunityEstimate,
    name: str,
) -> np.ndarray:
    return 0.5 * (
        np.asarray(estimate.train_metrics[name], dtype=float)
        + np.asarray(estimate.test_metrics[name], dtype=float)
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


def _sign_accuracy(estimate: np.ndarray, truth: np.ndarray) -> float:
    estimate = np.asarray(estimate, dtype=float)
    truth = np.asarray(truth, dtype=float)
    active = np.abs(truth) > 1e-8
    if not np.any(active):
        return float("nan")
    return float(np.mean(
        np.sign(estimate[active]) == np.sign(truth[active])
    ))


def _support_predictions(
    estimate: M4OpportunityEstimate,
    *,
    selection_threshold: float,
    creation_threshold: float,
    gate_threshold: float,
    return_threshold: float,
) -> dict[str, np.ndarray]:
    selection = np.linalg.norm(
        _mean_metric(estimate, "selection"),
        axis=1,
    ) / np.sqrt(estimate.train_metrics["selection"].shape[1])
    creation = np.linalg.norm(
        _mean_metric(estimate, "creation"),
        axis=1,
    )
    gate = _mean_metric(estimate, "gate_strength")
    persistence = np.mean(
        _mean_metric(estimate, "external_persistence"),
        axis=1,
    )
    return {
        "selection": selection >= selection_threshold,
        "creation": creation >= creation_threshold,
        "gate": gate >= gate_threshold,
        "return": np.abs(persistence - 0.24) >= return_threshold,
    }


def _classify(
    support: dict[str, np.ndarray],
    estimate: M4OpportunityEstimate,
) -> np.ndarray:
    authors = len(estimate.train_signature)
    labels = np.full(authors, "null_exogenous", dtype=object)
    refused = np.logical_and(
        estimate.train_refusal,
        estimate.test_refusal,
    )
    persistence = np.mean(
        _mean_metric(estimate, "external_persistence"),
        axis=1,
    )
    for author in range(authors):
        if refused[author]:
            labels[author] = "hidden_opportunity_alias"
        elif support["gate"][author]:
            labels[author] = "history_gated_ecology"
        elif support["selection"][author] and support["creation"][author]:
            labels[author] = "selection_creation_compensation"
        elif support["selection"][author]:
            labels[author] = "exogenous_selection"
        elif support["creation"][author]:
            labels[author] = "endogenous_creation_matched"
        elif support["return"][author]:
            labels[author] = (
                "slow_hysteresis_equal_marginal"
                if persistence[author] > 0.40
                else "fast_return_equal_marginal"
            )
    return labels


def audit_m4_opportunity_ecology(
    estimate: M4OpportunityEstimate,
    truth: M4OpportunityTruth,
    *,
    selection_threshold: float,
    creation_threshold: float,
    gate_threshold: float,
    return_threshold: float,
) -> dict[str, Any]:
    """Audit mechanism support, geometry, margins, and refusal."""
    support = _support_predictions(
        estimate,
        selection_threshold=selection_threshold,
        creation_threshold=creation_threshold,
        gate_threshold=gate_threshold,
        return_threshold=return_threshold,
    )
    authors = len(estimate.train_signature)
    expected_support = np.asarray([
        mechanism in truth.active_mechanisms
        for mechanism in MECHANISMS
    ])
    predicted_support = np.column_stack([
        support[mechanism]
        for mechanism in MECHANISMS
    ])
    support_truth = np.broadcast_to(
        expected_support[None],
        predicted_support.shape,
    )
    selected_label = _classify(support, estimate)
    selection = _mean_metric(estimate, "selection")
    creation = _mean_metric(estimate, "creation")
    loop = _mean_metric(estimate, "loop")
    rho = _mean_metric(estimate, "rho")
    return_time = _mean_metric(estimate, "return_time")
    recovery_time = _mean_metric(estimate, "recovery_time")
    gate = _mean_metric(estimate, "gate_strength")
    reverse_gate = _mean_metric(estimate, "reverse_gate_strength")
    gate_margin = (gate - reverse_gate) / (
        gate + reverse_gate + 1e-12
    )
    refusal = np.logical_and(
        estimate.train_refusal,
        estimate.test_refusal,
    )
    null_false_positive = float(np.mean(predicted_support)) if (
        truth.world == "null_exogenous"
    ) else float("nan")
    active_signs = []
    if "selection" in truth.active_mechanisms:
        active_signs.append(_sign_accuracy(
            selection,
            truth.author_parameters["selection"],
        ))
    if "creation" in truth.active_mechanisms:
        active_signs.append(_sign_accuracy(
            creation,
            truth.author_parameters["creation"],
        ))
    if "gate" in truth.active_mechanisms:
        active_signs.append(_sign_accuracy(
            _mean_metric(estimate, "gate"),
            truth.author_parameters["gate"],
        ))
    return {
        "world": truth.world,
        "active_mechanisms": "|".join(truth.active_mechanisms),
        "matched_group": truth.matched_group or "",
        "same_author_auc": same_author_auc(
            estimate.train_signature,
            estimate.test_signature,
        ),
        "classification_accuracy": float(np.mean(
            selected_label == truth.world
        )),
        "predicted_labels": selected_label.tolist(),
        "support_f1": float(f1_score(
            support_truth.ravel(),
            predicted_support.ravel(),
            zero_division=1.0,
        )),
        "sign_accuracy": (
            float(np.nanmean(active_signs))
            if active_signs
            else float("nan")
        ),
        "loop_geometry": _geometry(
            loop,
            truth.author_parameters["loop"],
        ),
        "rho_spearman": _spearman(
            rho,
            truth.author_parameters["rho"],
        ),
        "return_time_spearman": _spearman(
            return_time,
            truth.author_parameters["return_time"],
        ),
        "recovery_time_spearman": _spearman(
            recovery_time,
            truth.author_parameters["recovery_time"],
        ),
        "mean_gate_direction_margin": float(np.mean(gate_margin)),
        "mean_gate_strength": float(np.mean(gate)),
        "mean_reverse_gate_strength": float(np.mean(reverse_gate)),
        "mean_path_gain": float(np.mean(
            _mean_metric(estimate, "path_gain")
        )),
        "mean_selection_strength": float(np.mean(
            np.linalg.norm(selection, axis=1)
        )),
        "mean_creation_strength": float(np.mean(
            np.linalg.norm(creation, axis=1)
        )),
        "mean_external_persistence": float(np.mean(
            _mean_metric(estimate, "external_persistence")
        )),
        "menu_marginal": np.mean(
            _mean_metric(estimate, "menu_marginal"),
            axis=0,
        ).tolist(),
        "choice_marginal": np.mean(
            _mean_metric(estimate, "choice_marginal"),
            axis=0,
        ).tolist(),
        "refusal_rate": float(np.mean(refusal)),
        "alias_refused": bool(not truth.alias or np.mean(refusal) >= 0.95),
        "null_false_positive_rate": null_false_positive,
        "selected_models": {
            model: float(np.mean(
                estimate.train_selected_model == model
            ))
            for model in ("base", "return", "feedback", "gate", "refuse")
        },
        "authors": authors,
    }
