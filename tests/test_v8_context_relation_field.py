"""Tests for the V8-HJIC-1C context relation field."""
from __future__ import annotations

from functools import lru_cache

from suica_core.v8_context_relation_field import (
    ContextRelationSpec,
    audit_context_relation_truth,
    fit_relation_calibration,
    observable_context_relation_diagnostics,
    simulate_context_relation_world,
)


@lru_cache(maxsize=1)
def _setup():
    spec = ContextRelationSpec(
        calibration_authors=1200,
        confirmation_authors=1200,
        permutations=99,
        bootstrap_draws=39,
    )
    calibration = fit_relation_calibration(seed=20260801, spec=spec)
    return spec, calibration


def _evaluate(world: str, seed: int, reliability: float = 1.0):
    spec, calibration = _setup()
    generated = simulate_context_relation_world(
        world,
        seed=seed,
        spec=spec,
        context_reliability=reliability,
    )
    result = observable_context_relation_diagnostics(
        generated,
        calibration=calibration,
        spec=spec,
    )
    return generated, result


def test_covariance_decomposition_is_exact_before_whitening() -> None:
    _, result = _evaluate("GLOBAL_INVARIANT", 11)
    assert result["first"]["decomposition_error"] < 1e-10
    assert result["second"]["decomposition_error"] < 1e-10
    assert result["global_invariant_license"] == 1


def test_sign_reversal_is_local_and_cancels_globally() -> None:
    _, result = _evaluate("BALANCED_SIGN_REVERSAL", 21)
    assert result["local_atlas_license"] == 1
    assert result["cancellation_detected"] == 1
    assert result["global_invariant_license"] == 0


def test_ecological_relation_is_not_an_individual_license() -> None:
    _, result = _evaluate("ECOLOGICAL_ONLY", 31)
    assert result["ecological_between_detected"] == 1
    assert result["final_relation_license"] == 0
    assert result["taxonomy"] == "ECOLOGICAL_ONLY"


def test_out_of_sieve_and_collider_worlds_refuse_for_different_reasons() -> None:
    _, misspecified = _evaluate("NONLINEAR_SIMPSON_OUT_OF_SIEVE", 41)
    _, collider = _evaluate("COLLIDER_OR_DESCENDANT_Z", 42)
    assert misspecified["residualizer_misspecified"] == 1
    assert misspecified["final_relation_license"] == 0
    assert collider["causal_role_refusal"] == 1
    assert collider["final_relation_license"] == 0


def test_relation_and_unique_mode_are_separate() -> None:
    _, result = _evaluate("LOCAL_LOW_SINGULAR_GAP", 51)
    assert result["final_relation_license"] == 1
    assert result["mode_license"] == 0


def test_context_measurement_frontier_refuses_low_reliability() -> None:
    _, high = _evaluate("BALANCED_SIGN_REVERSAL", 61, reliability=0.8)
    _, low = _evaluate("BALANCED_SIGN_REVERSAL", 62, reliability=0.2)
    assert high["final_relation_license"] == 1
    assert high["context_underresolved"] == 0
    assert low["final_relation_license"] == 0
    assert low["context_underresolved"] == 1


def test_truth_is_opened_only_after_observable_license() -> None:
    spec, calibration = _setup()
    world, observable = _evaluate("GLOBAL_INVARIANT", 71)
    assert observable["truth_used_by_license"] is False
    assert "truth_fidelity" not in observable
    audit = audit_context_relation_truth(
        world,
        observable,
        calibration=calibration,
        spec=spec,
        seed=72,
    )
    assert audit["truth_used_by_license"] is False
    assert audit["truth_fidelity"] > 0.8
