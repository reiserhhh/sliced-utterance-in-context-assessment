"""Tests for M4-B endogenous opportunity-ecology discovery."""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from suica_core.m4_opportunity_audit import audit_m4_opportunity_ecology
from suica_core.m4_opportunity_estimator import fit_m4_opportunity_ecology
from suica_core.m4_opportunity_generator import (
    M4OpportunitySpec,
    generate_m4_opportunity_world,
)


SPEC = M4OpportunitySpec(
    authors=8,
    calibration_occasions=2,
    selection_occasions=1,
    evaluation_occasions=2,
    events=72,
    response_noise=0.13,
)


def _estimate(world: str, seed: int):
    observed, truth = generate_m4_opportunity_world(
        world=world,
        spec=SPEC,
        seed=seed,
    )
    estimate = fit_m4_opportunity_ecology(
        observed,
        logistic_iterations=10,
        complexity_penalty=0.00035,
    )
    return observed, truth, estimate


def test_opportunity_generator_is_reproducible() -> None:
    first, truth = generate_m4_opportunity_world(
        world="endogenous_creation_matched",
        spec=SPEC,
        seed=701,
    )
    second, repeated_truth = generate_m4_opportunity_world(
        world="endogenous_creation_matched",
        spec=SPEC,
        seed=701,
    )
    assert np.array_equal(
        first.train_calibration.menu,
        second.train_calibration.menu,
    )
    assert np.allclose(
        truth.author_parameters["loop"],
        repeated_truth.author_parameters["loop"],
    )


def test_hidden_source_alias_refuses_decomposition() -> None:
    _, truth, estimate = _estimate(
        "hidden_opportunity_alias",
        711,
    )
    result = audit_m4_opportunity_ecology(
        estimate,
        truth,
        selection_threshold=0.20,
        creation_threshold=0.045,
        gate_threshold=0.035,
        return_threshold=0.10,
    )
    assert result["alias_refused"] is True
    assert result["refusal_rate"] >= 0.95


def test_selection_and_creation_have_distinct_mechanism_scores() -> None:
    _, _, selection = _estimate("exogenous_selection", 721)
    _, _, creation = _estimate(
        "endogenous_creation_matched",
        722,
    )
    selection_strength = np.mean(np.linalg.norm(
        0.5 * (
            selection.train_metrics["selection"]
            + selection.test_metrics["selection"]
        ),
        axis=1,
    ))
    selection_creation = np.mean(np.linalg.norm(
        0.5 * (
            selection.train_metrics["creation"]
            + selection.test_metrics["creation"]
        ),
        axis=1,
    ))
    creation_selection = np.mean(np.linalg.norm(
        0.5 * (
            creation.train_metrics["selection"]
            + creation.test_metrics["selection"]
        ),
        axis=1,
    ))
    creation_strength = np.mean(np.linalg.norm(
        0.5 * (
            creation.train_metrics["creation"]
            + creation.test_metrics["creation"]
        ),
        axis=1,
    ))
    assert selection_strength > creation_selection
    assert creation_strength > selection_creation


def test_equal_marginal_return_worlds_have_different_persistence() -> None:
    _, _, fast = _estimate("fast_return_equal_marginal", 731)
    _, _, slow = _estimate("slow_hysteresis_equal_marginal", 732)
    fast_persistence = np.mean(
        0.5 * (
            fast.train_metrics["external_persistence"]
            + fast.test_metrics["external_persistence"]
        )
    )
    slow_persistence = np.mean(
        0.5 * (
            slow.train_metrics["external_persistence"]
            + slow.test_metrics["external_persistence"]
        )
    )
    assert slow_persistence - fast_persistence > 0.35


def test_evaluation_panel_cannot_change_model_selection() -> None:
    first, _ = generate_m4_opportunity_world(
        world="endogenous_creation_matched",
        spec=SPEC,
        seed=741,
    )
    replacement, _ = generate_m4_opportunity_world(
        world="endogenous_creation_matched",
        spec=SPEC,
        seed=742,
    )
    mixed = replace(
        first,
        train_evaluation=replacement.train_evaluation,
        test_evaluation=replacement.test_evaluation,
    )
    original_estimate = fit_m4_opportunity_ecology(
        first,
        logistic_iterations=10,
        complexity_penalty=0.00035,
    )
    mixed_estimate = fit_m4_opportunity_ecology(
        mixed,
        logistic_iterations=10,
        complexity_penalty=0.00035,
    )
    assert np.array_equal(
        original_estimate.train_selected_model,
        mixed_estimate.train_selected_model,
    )
    assert np.array_equal(
        original_estimate.test_selected_model,
        mixed_estimate.test_selected_model,
    )
