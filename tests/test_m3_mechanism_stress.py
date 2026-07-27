"""Smoke tests for low-order-matched M3 mechanism attacks."""
from __future__ import annotations

from suica_core.m3_mechanism_audit import audit_m3_mechanism_atlas
from suica_core.m3_mechanism_stress_estimator import fit_m3_mechanism_stress
from suica_core.m3_mechanism_stress_generator import (
    M3MechanismStressSpec,
    generate_m3_mechanism_stress_world,
)


def _rows(world: str, seed: int) -> dict[str, dict[str, object]]:
    observed, truth = generate_m3_mechanism_stress_world(
        world=world,
        spec=M3MechanismStressSpec(
            authors=24,
            occasions=5,
            events=120,
            noise=0.08,
        ),
        seed=seed,
    )
    estimate = fit_m3_mechanism_stress(observed, seed=seed + 1)
    return {
        str(row["family"]): row
        for row in audit_m3_mechanism_atlas(estimate, truth)
    }


def test_equal_covariance_shape_beats_covariance_summary() -> None:
    rows = _rows("equal_covariance_density_shape", 301)
    assert (
        float(rows["standardized_distribution_shape"]["same_author_auc"])
        > float(rows["covariance_profile"]["same_author_auc"]) + 0.03
    )


def test_nonlinear_condition_beats_linear_slope() -> None:
    rows = _rows("matched_linear_nonlinear_response", 302)
    assert (
        float(rows["nonlinear_condition"]["truth_geometry_spearman"])
        > float(rows["linear_condition"]["truth_geometry_spearman"]) + 0.20
    )


def test_ar2_spectrum_recovers_dynamics_with_matched_lag_one() -> None:
    rows = _rows("matched_lag1_ar2_slow_mode", 303)
    assert (
        float(rows["ar2_slow_spectrum"]["truth_geometry_spearman"])
        > float(rows["lag1_spectrum"]["truth_geometry_spearman"]) + 0.10
    )


def test_lag_three_memory_survives_lag_one_two_match() -> None:
    rows = _rows("matched_lag12_lag3_path", 304)
    assert (
        float(rows["lag3_partial_operator"]["same_author_auc"])
        > float(rows["lag2_memory"]["same_author_auc"]) + 0.03
    )


def test_nonlinear_partner_beats_linear_coupling() -> None:
    rows = _rows("matched_linear_nonlinear_interaction", 305)
    assert (
        float(rows["nonlinear_partner"]["truth_geometry_spearman"])
        > float(rows["linear_partner"]["truth_geometry_spearman"]) + 0.20
    )
