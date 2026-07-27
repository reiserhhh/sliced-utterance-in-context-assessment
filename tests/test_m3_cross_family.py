"""Tests for generator-blind SUICA M3 cross-family experiments."""
from __future__ import annotations

import numpy as np

from suica_core.m3_cross_family_audit import audit_m3_cross_family
from suica_core.m3_cross_family_contracts import (
    observed_from_payload,
    observed_to_payload,
    validate_cross_family_observed,
)
from suica_core.m3_cross_family_estimator import fit_m3_cross_family
from suica_core.m3_cross_family_generator import (
    M3CrossFamilySpec,
    _support_alias_surface,
    generate_m3_cross_family_world,
)
from suica_core.m3_cross_family_validity import (
    audit_m3_cross_family_validity,
)


def _spec() -> M3CrossFamilySpec:
    return M3CrossFamilySpec(
        authors=16,
        occasions=4,
        events=96,
        dimensions=3,
        partners=8,
        noise=0.10,
    )


def test_observation_payload_excludes_hidden_truth() -> None:
    observed, _ = generate_m3_cross_family_world(
        world="cf_d_tail",
        spec=_spec(),
        seed=101,
    )
    payload = observed_to_payload(observed)
    assert not any("truth" in key or "parameter" in key for key in payload)
    restored = observed_from_payload(payload)
    validate_cross_family_observed(restored)
    assert np.allclose(restored.response_train, observed.response_train)


def test_distribution_world_independently_passes_moment_orthogonality() -> None:
    observed, truth = generate_m3_cross_family_world(
        world="cf_d_copula",
        spec=_spec(),
        seed=102,
    )
    validity = audit_m3_cross_family_validity(observed, truth)
    assert float(validity["density_relative_minimum"]) > 0.0
    assert float(validity["moment_tensor_degree4_max_author_range"]) < 1e-12
    assert truth.oracle_profiles["distribution"].shape[0] == _spec().authors


def test_operator_world_has_independent_condition_and_partner_truth() -> None:
    observed, truth = generate_m3_cross_family_world(
        world="cf_o_voronoi",
        spec=_spec(),
        seed=103,
    )
    assert truth.active_targets == ("condition", "partner")
    assert abs(np.corrcoef(
        truth.author_parameters["condition"].ravel(),
        truth.author_parameters["partner"].ravel(),
    )[0, 1]) < 0.45
    assert observed.design["leave_dyad_out"] is True
    for author in range(_spec().authors):
        assert not np.intersect1d(
            np.unique(observed.partner_id_train[author]),
            np.unique(observed.partner_id_test[author]),
        ).size
    assert set(np.unique(observed.partner_id_train)) == set(
        np.unique(observed.partner_id_test)
    )
    validity = audit_m3_cross_family_validity(observed, truth)
    assert validity["actor_partner_graph_connected"] is True
    assert float(validity["poly3_projection_ratio_max"]) < 1e-10


def test_path_worlds_match_population_lag02_without_fft_replacement() -> None:
    for offset, world in enumerate(
        ("cf_kp_hsmm", "cf_kp_cycle", "cf_kp_arch")
    ):
        observed, truth = generate_m3_cross_family_world(
            world=world,
            spec=_spec(),
            seed=104 + offset,
        )
        validity = audit_m3_cross_family_validity(observed, truth)
        assert (
            float(validity["theoretical_lag02_max_author_range"]) < 1e-12
        )
        assert truth.validity["posthoc_spectral_matching"] is False


def test_blind_estimator_recovers_cross_family_operator_geometry() -> None:
    observed, truth = generate_m3_cross_family_world(
        world="cf_o_spline",
        spec=M3CrossFamilySpec(
            authors=20,
            occasions=4,
            events=128,
            dimensions=3,
            partners=8,
            noise=0.08,
        ),
        seed=105,
    )
    estimate = fit_m3_cross_family(
        observed,
        seed=106,
        frequency_directions=16,
        nystroem_components=32,
    )
    rows = {
        str(row["target"]): row
        for row in audit_m3_cross_family(estimate, truth)
    }
    assert float(rows["condition"]["expected_geometry"]) > 0.75
    assert float(rows["partner"]["expected_geometry"]) > 0.75


def test_blind_estimator_keeps_path_objects_separate() -> None:
    observed, _ = generate_m3_cross_family_world(
        world="cf_kp_hsmm",
        spec=_spec(),
        seed=106,
    )
    estimate = fit_m3_cross_family(
        observed,
        seed=2_001,
        frequency_directions=16,
        nystroem_components=24,
    )
    assert {
        "path_hazard",
        "path_time_reversal",
        "path_delay_vamp",
        "path_second_order",
    } <= set(estimate.train_features)
    assert "path_higher_order" not in estimate.train_features
    assert "distribution_rpecf" not in estimate.train_features


def test_exact_hidden_alias_is_not_recovered() -> None:
    observed, truth = generate_m3_cross_family_world(
        world="alias_hidden",
        spec=M3CrossFamilySpec(
            authors=28,
            occasions=4,
            events=192,
            dimensions=3,
            partners=8,
        ),
        seed=107,
    )
    estimate = fit_m3_cross_family(
        observed,
        seed=108,
        frequency_directions=16,
        nystroem_components=24,
    )
    row = audit_m3_cross_family(estimate, truth)[0]
    assert abs(float(row["expected_auc"]) - 0.5) < 0.12
    assert abs(float(row["expected_geometry"])) < 0.25


def test_support_alias_is_identical_on_support_but_nontrivial_outside() -> None:
    observed, truth = generate_m3_cross_family_world(
        world="alias_operator_support",
        spec=_spec(),
        seed=109,
    )
    validity = audit_m3_cross_family_validity(observed, truth)
    assert truth.active_targets == ("condition", "partner")
    assert float(validity["observed_support_max_abs"]) <= 1.0
    assert float(validity["alias_on_support_basis_max_abs"]) == 0.0
    assert float(validity["outside_support_author_variation"]) > 0.10


def test_support_alias_surface_is_zero_only_on_registered_support() -> None:
    points = np.asarray([
        [-1.0, 1.0, 7.0],
        [0.25, -0.75, -3.0],
        [1.5, -1.8, 0.0],
    ])
    basis = _support_alias_surface(points)
    assert np.array_equal(basis[:2], np.zeros((2, 2)))
    assert np.allclose(basis[2], [0.5**4, -(0.8**4)])
