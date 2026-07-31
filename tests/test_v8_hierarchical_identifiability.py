"""Tests for the V8-HJIC-1 typed-graph synthetic battery."""
from __future__ import annotations

import numpy as np

from suica_core.v8_hierarchical_identifiability import (
    HJICSpec,
    alias_world,
    centered_condition_basis,
    evaluate_identifiable_world,
    fit_identifiable_world,
    gaussian_information_order,
    reference_drift_trial,
    relational_lift_trial,
    route_null_trial,
    simulate_identifiable_world,
)


def test_condition_basis_is_centered_and_orthonormal() -> None:
    basis = centered_condition_basis(5, 3)
    assert np.allclose(basis.mean(axis=0), 0.0, atol=1e-12)
    assert np.allclose(basis.T @ basis / 5, np.eye(3), atol=1e-12)


def test_identifiable_world_recovers_components_and_commutes() -> None:
    spec = HJICSpec()
    world = simulate_identifiable_world(42, spec)
    result = evaluate_identifiable_world(
        world,
        fit_identifiable_world(world),
    )
    correlations = {
        row["component"]: row["truth_correlation"]
        for row in result["component"]
    }
    assert min(correlations.values()) > 0.75
    assert max(
        row["standardized_commutation_defect"]
        for row in result["commutation"]
    ) < 1e-10
    assert 0.85 <= result["coverage"][0]["coverage"] <= 1.0


def test_alias_worlds_are_observationally_equivalent_and_refused() -> None:
    for index, name in enumerate(
        ("STATE_ALIAS", "MENU_ALIAS", "KERNEL_ALIAS", "ORDER_ALIAS")
    ):
        result = alias_world(name, seed=100 + index)
        assert result["latent_separation"] > 0
        assert result["observed_max_difference"] < 1e-12
        assert result["observational_auc"] == 0.5
        assert result["refusal"] == 1
        assert result["false_point_identification"] == 0


def test_frozen_contraction_respects_information_order() -> None:
    result = gaussian_information_order(123)
    assert result["mi_full_bits"] >= result["mi_contracted_bits"]
    assert result["dpi_violation_bits"] <= 1e-10
    assert result["conditional_covariance_order_min_eigenvalue"] >= -1e-10
    assert result["bayes_mse_full"] <= result["bayes_mse_contracted"]


def test_route_null_never_licenses_an_ontology_claim() -> None:
    result = route_null_trial(321, HJICSpec())
    assert result["planted_incremental_information"] == 0.0
    assert result["licensed_specialization_claim"] == 0


def test_relation_lift_separates_shared_structure_from_nuisance() -> None:
    shared = relational_lift_trial(456, world="SHARED_LATENT")
    nuisance = relational_lift_trial(789, world="COMMON_NUISANCE")
    assert shared["mean_individual_correlation"] < 0.5
    assert shared["raw_relation_element_correlation"] > 0.75
    assert shared["licensed_structural_connection"] == 1
    assert nuisance["raw_relation_element_correlation"] > 0.75
    assert nuisance["nuisance_explained_fraction"] > 0.8
    assert nuisance["licensed_structural_connection"] == 0


def test_reference_drift_requires_a_declared_population() -> None:
    result = reference_drift_trial(987)
    assert result["fixed_origin_shift_cosine"] > 0.95
    assert result["fixed_origin_amplitude_error"] < 0.1
    assert result["transductive_shift_norm"] < 1e-10
    assert result["population_relation_shift_frobenius"] > 0.25
    assert result["reference_mismatch_refusal"] == 1
