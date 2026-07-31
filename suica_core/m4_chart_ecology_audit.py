"""Truth-open audit for M4-C.2 chart-covariant opportunity ecology."""
from __future__ import annotations

from typing import Any

import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import spearmanr
from sklearn.metrics import f1_score

from .m3_mechanism_audit import same_author_auc
from .m4_chart_ecology_contracts import (
    M4ChartEcologyEstimate,
    M4ChartEcologyRouteEstimate,
    M4ChartEcologyTruth,
)


MECHANISMS = ("selection", "creation", "gate", "return")


def _mean_metric(
    estimate: M4ChartEcologyRouteEstimate,
    name: str,
) -> np.ndarray:
    return 0.5 * (
        np.asarray(estimate.train_metrics[name], dtype=float)
        + np.asarray(estimate.test_metrics[name], dtype=float)
    )


def _safe_spearman(first: np.ndarray, second: np.ndarray) -> float:
    x = np.asarray(first, dtype=float).ravel()
    y = np.asarray(second, dtype=float).ravel()
    if np.std(x) <= 1e-12 or np.std(y) <= 1e-12:
        return 0.0
    value = float(spearmanr(x, y).statistic)
    return value if np.isfinite(value) else 0.0


def _geometry(first: np.ndarray, second: np.ndarray) -> float:
    x = np.asarray(first, dtype=float)
    y = np.asarray(second, dtype=float)
    if x.ndim == 1:
        x = x[:, None]
    if y.ndim == 1:
        y = y[:, None]
    return _safe_spearman(pdist(x), pdist(y))


def _supports(
    route: M4ChartEcologyRouteEstimate,
    *,
    selection_threshold: float,
    creation_threshold: float,
    gate_threshold: float,
    return_threshold: float,
) -> dict[str, np.ndarray]:
    selection = _mean_metric(route, "selection_strength")
    creation = _mean_metric(route, "creation_strength")
    gate = _mean_metric(route, "gate_strength")
    persistence = _mean_metric(route, "external_persistence")
    result = {
        "selection": selection >= selection_threshold,
        "creation": creation >= creation_threshold,
        "gate": gate >= gate_threshold,
        "return": np.abs(persistence - 0.24) >= return_threshold,
    }
    return result


def _labels(
    route: M4ChartEcologyRouteEstimate,
    support: dict[str, np.ndarray],
) -> np.ndarray:
    authors = len(route.train_signature)
    labels = np.full(authors, "linear_null_ecology", dtype=object)
    persistence = _mean_metric(route, "external_persistence")
    refused = route.train_refusal & route.test_refusal
    for author in range(authors):
        if refused[author]:
            labels[author] = "hidden_opportunity_source_alias"
        elif support["gate"][author]:
            labels[author] = "history_gated_ecology"
        elif support["selection"][author] and support["creation"][author]:
            labels[author] = "selection_creation_compensation"
        elif support["selection"][author]:
            labels[author] = "linear_exogenous_selection"
        elif support["creation"][author]:
            labels[author] = "endogenous_creation"
        elif support["return"][author]:
            labels[author] = (
                "slow_hysteresis_equal_marginal"
                if persistence[author] > 0.40
                else "fast_return_equal_marginal"
            )
    return labels


def _sign_agreement(
    discovered: np.ndarray,
    oracle: np.ndarray,
) -> float:
    reference = np.asarray(oracle, dtype=float).ravel()
    estimate = np.asarray(discovered, dtype=float).ravel()
    threshold = max(
        float(np.quantile(np.abs(reference), 0.60)),
        1e-5,
    )
    active = np.abs(reference) >= threshold
    if not np.any(active):
        return 1.0
    return float(np.mean(
        np.sign(reference[active]) == np.sign(estimate[active])
    ))


def audit_m4_chart_ecology(
    estimate: M4ChartEcologyEstimate,
    oracle: M4ChartEcologyRouteEstimate,
    truth: M4ChartEcologyTruth,
    *,
    selection_threshold: float,
    creation_threshold: float,
    gate_threshold: float,
    return_threshold: float,
    minimum_conditional_skill: float,
    minimum_alias_oracle_skill: float = 0.50,
    minimum_alias_skill_gap: float = 0.20,
    maximum_alias_retained_ratio: float = 0.70,
    alias_bootstrap_repetitions: int = 2000,
    alias_bootstrap_seed: int = 97531,
    basis_action_invariant: bool,
    response_perturbation_invariant: bool,
) -> dict[str, Any]:
    """Compare physical operator actions, not coordinate coefficients."""
    discovered = estimate.discovered
    support = _supports(
        discovered,
        selection_threshold=selection_threshold,
        creation_threshold=creation_threshold,
        gate_threshold=gate_threshold,
        return_threshold=return_threshold,
    )
    oracle_support = _supports(
        oracle,
        selection_threshold=selection_threshold,
        creation_threshold=creation_threshold,
        gate_threshold=gate_threshold,
        return_threshold=return_threshold,
    )
    expected = np.asarray(
        [mechanism in truth.active_mechanisms for mechanism in MECHANISMS]
    )
    predicted = np.column_stack(
        [support[mechanism] for mechanism in MECHANISMS]
    )
    oracle_predicted = np.column_stack(
        [oracle_support[mechanism] for mechanism in MECHANISMS]
    )
    expected_matrix = np.broadcast_to(expected[None], predicted.shape)
    labels = _labels(discovered, support)
    oracle_labels = _labels(oracle, oracle_support)
    discovered_conditional = _mean_metric(discovered, "conditional_skill")
    oracle_conditional = _mean_metric(oracle, "conditional_skill")
    discovered_alias_skill_by_author = 0.5 * (
        _mean_metric(discovered, "choice_skill")
        + _mean_metric(discovered, "hazard_skill")
    )
    oracle_alias_skill_by_author = 0.5 * (
        _mean_metric(oracle, "choice_skill")
        + _mean_metric(oracle, "hazard_skill")
    )
    alias_skill_difference = (
        oracle_alias_skill_by_author - discovered_alias_skill_by_author
    )
    alias_oracle_skill = float(np.mean(oracle_alias_skill_by_author))
    alias_discovered_skill = float(np.mean(discovered_alias_skill_by_author))
    alias_skill_gap = alias_oracle_skill - alias_discovered_skill
    alias_retained_ratio = (
        alias_discovered_skill / alias_oracle_skill
        if alias_oracle_skill > 1e-12
        else float("nan")
    )
    bootstrap_rng = np.random.default_rng(alias_bootstrap_seed)
    bootstrap_means = np.mean(
        bootstrap_rng.choice(
            alias_skill_difference,
            size=(
                int(alias_bootstrap_repetitions),
                len(alias_skill_difference),
            ),
            replace=True,
        ),
        axis=1,
    )
    alias_gap_lcb = float(np.quantile(bootstrap_means, 0.025))
    observed_mechanism_underresolved = bool(
        np.mean(discovered_conditional) < minimum_conditional_skill
    )
    truth_open_alias_information_loss = bool(
        truth.chart_alias
        and alias_oracle_skill >= minimum_alias_oracle_skill
        and alias_skill_gap >= minimum_alias_skill_gap
        and alias_retained_ratio <= maximum_alias_retained_ratio
        and alias_gap_lcb > 0.0
    )
    action_pairs = {
        "selection": (
            _mean_metric(discovered, "choice_action"),
            _mean_metric(oracle, "choice_action"),
        ),
        "creation": (
            _mean_metric(discovered, "creation_action")[..., 1:, :]
            - _mean_metric(discovered, "creation_action")[..., :1, :],
            _mean_metric(oracle, "creation_action")[..., 1:, :]
            - _mean_metric(oracle, "creation_action")[..., :1, :],
        ),
        "gate": (
            _mean_metric(discovered, "creation_action")[..., -1, :]
            - _mean_metric(discovered, "creation_action")[..., 0, :],
            _mean_metric(oracle, "creation_action")[..., -1, :]
            - _mean_metric(oracle, "creation_action")[..., 0, :],
        ),
        "return": (
            _mean_metric(discovered, "external_persistence") - 0.24,
            _mean_metric(oracle, "external_persistence") - 0.24,
        ),
    }
    active_signs = [
        _sign_agreement(*action_pairs[mechanism])
        for mechanism in truth.active_mechanisms
        if mechanism in action_pairs
    ]
    loop_discovered = _mean_metric(discovered, "loop_kernel")
    loop_oracle = _mean_metric(oracle, "loop_kernel")
    choice_discovered = _mean_metric(discovered, "choice_action")
    choice_oracle = _mean_metric(oracle, "choice_action")
    creation_discovered = _mean_metric(discovered, "creation_action")
    creation_oracle = _mean_metric(oracle, "creation_action")
    return_discovered = _mean_metric(discovered, "return_curve")
    return_oracle = _mean_metric(oracle, "return_curve")
    recovery_discovered = _mean_metric(discovered, "recovery_curve")
    recovery_oracle = _mean_metric(oracle, "recovery_curve")
    null_false_positive = (
        float(np.mean(predicted))
        if truth.world == "linear_null_ecology"
        else float("nan")
    )
    chart_refused = estimate.refused
    identifiable_resolution = (
        not chart_refused
        and (
            truth.world == "linear_null_ecology"
            or not observed_mechanism_underresolved
        )
    )
    expected_resolution = {
        "IDENTIFIABLE": identifiable_resolution,
        "REFUSE_CHART": chart_refused,
        "REFUSE_SUPPORT": chart_refused,
        "REFUSE_SOURCE": chart_refused,
        "REFUSE_MECHANISM": truth_open_alias_information_loss,
        "ATLAS_OR_REFUSE": True,
    }[truth.expected_status]
    result = {
        "world": truth.world,
        "expected_status": truth.expected_status,
        "active_mechanisms": "|".join(truth.active_mechanisms),
        "expected_resolution": float(expected_resolution),
        "chart_refused": float(chart_refused),
        "refusal_reasons": "|".join(estimate.refusal_reasons),
        "mechanism_underresolved": float(
            observed_mechanism_underresolved
        ),
        "truth_open_alias_information_loss": float(
            truth_open_alias_information_loss
        ),
        "conditional_skill": float(np.mean(discovered_conditional)),
        "oracle_conditional_skill": float(np.mean(oracle_conditional)),
        "alias_discovered_skill": alias_discovered_skill,
        "alias_oracle_skill": alias_oracle_skill,
        "alias_skill_gap": alias_skill_gap,
        "alias_retained_ratio": alias_retained_ratio,
        "alias_skill_gap_lcb": alias_gap_lcb,
        "mean_selection_strength": float(np.mean(
            _mean_metric(discovered, "selection_strength")
        )),
        "oracle_mean_selection_strength": float(np.mean(
            _mean_metric(oracle, "selection_strength")
        )),
        "mean_creation_strength": float(np.mean(
            _mean_metric(discovered, "creation_strength")
        )),
        "oracle_mean_creation_strength": float(np.mean(
            _mean_metric(oracle, "creation_strength")
        )),
        "mean_gate_strength": float(np.mean(
            _mean_metric(discovered, "gate_strength")
        )),
        "oracle_mean_gate_strength": float(np.mean(
            _mean_metric(oracle, "gate_strength")
        )),
        "mean_external_persistence": float(np.mean(
            _mean_metric(discovered, "external_persistence")
        )),
        "mean_choice_skill": float(np.mean(
            _mean_metric(discovered, "choice_skill")
        )),
        "oracle_mean_choice_skill": float(np.mean(
            _mean_metric(oracle, "choice_skill")
        )),
        "mean_hazard_skill": float(np.mean(
            _mean_metric(discovered, "hazard_skill")
        )),
        "oracle_mean_hazard_skill": float(np.mean(
            _mean_metric(oracle, "hazard_skill")
        )),
        "mean_response_choice_increment": float(np.mean(
            _mean_metric(discovered, "response_choice_increment")
        )),
        "oracle_mean_response_choice_increment": float(np.mean(
            _mean_metric(oracle, "response_choice_increment")
        )),
        "classification_accuracy": float(np.mean(labels == truth.world)),
        "oracle_classification_accuracy": float(
            np.mean(oracle_labels == truth.world)
        ),
        "predicted_labels": labels.tolist(),
        "oracle_predicted_labels": oracle_labels.tolist(),
        "support_f1": float(f1_score(
            expected_matrix.ravel(),
            predicted.ravel(),
            zero_division=1.0,
        )),
        "oracle_support_f1": float(f1_score(
            expected_matrix.ravel(),
            oracle_predicted.ravel(),
            zero_division=1.0,
        )),
        "sign_accuracy": (
            float(np.mean(active_signs)) if active_signs else 1.0
        ),
        "choice_action_geometry": _geometry(
            choice_discovered.reshape(len(choice_discovered), -1),
            choice_oracle.reshape(len(choice_oracle), -1),
        ),
        "creation_action_geometry": _geometry(
            creation_discovered.reshape(len(creation_discovered), -1),
            creation_oracle.reshape(len(creation_oracle), -1),
        ),
        "loop_action_geometry": _geometry(
            loop_discovered.reshape(len(loop_discovered), -1),
            loop_oracle.reshape(len(loop_oracle), -1),
        ),
        "loop_action_element_r": _safe_spearman(
            loop_discovered,
            loop_oracle,
        ),
        "return_spearman": _safe_spearman(
            np.mean(return_discovered, axis=1),
            np.mean(return_oracle, axis=1),
        ),
        "recovery_spearman": _safe_spearman(
            np.mean(recovery_discovered, axis=1),
            np.mean(recovery_oracle, axis=1),
        ),
        "gate_direction_margin": float(np.mean(
            _mean_metric(discovered, "gate_direction_margin")
        )),
        "same_author_auc": same_author_auc(
            discovered.train_signature,
            discovered.test_signature,
        ),
        "oracle_same_author_auc": same_author_auc(
            oracle.train_signature,
            oracle.test_signature,
        ),
        "basis_action_invariant": float(basis_action_invariant),
        "response_perturbation_invariant": float(
            response_perturbation_invariant
        ),
        "source_alias_refusal_rate": float(np.mean(
            discovered.train_refusal & discovered.test_refusal
        )),
        "null_false_positive_rate": null_false_positive,
        "transform_rank": estimate.transform_rank,
        "selected_models": {
            model: float(np.mean(
                discovered.train_selected_model == model
            ))
            for model in ("base", "return", "feedback", "gate")
        },
    }
    for index, mechanism in enumerate(MECHANISMS):
        result[f"truth_{mechanism}"] = float(expected[index])
        result[f"predicted_{mechanism}_rate"] = float(
            np.mean(predicted[:, index])
        )
        result[f"oracle_predicted_{mechanism}_rate"] = float(
            np.mean(oracle_predicted[:, index])
        )
    return result
