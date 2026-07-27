"""Tests for SUICA V8 response-set incidence geometry."""
from __future__ import annotations

import numpy as np

from suica_core.v8_response_set_incidence import (
    ResponseSetSpec,
    analyze_pair,
    bounded_affine_distance,
    box_count_dimension,
    finite_direction_family,
    pairwise_incidence_graph,
    planted_pair,
    principal_angle_degrees,
    rigid_transform,
    simulate_pair_observations,
)


def test_same_condition_and_free_incidence_are_distinct() -> None:
    left, right = planted_pair("l2_cross_condition")
    same = bounded_affine_distance(
        left,
        right,
        same_condition=True,
    )
    free = bounded_affine_distance(
        left,
        right,
        same_condition=False,
    )
    assert same["distance"] > 0.25
    assert free["distance"] < 1e-8
    assert free["condition_gap"] > 0.25


def test_three_dimensional_skew_lines_do_not_intersect() -> None:
    left, right = planted_pair("l3_skew")
    free = bounded_affine_distance(
        left,
        right,
        same_condition=False,
    )
    assert np.isclose(free["distance"], 0.25)
    assert np.isclose(principal_angle_degrees(left, right), 90.0)


def test_rigid_transform_preserves_incidence_distances() -> None:
    left, right = planted_pair("p3_cross_condition")
    rng = np.random.default_rng(7)
    rotation, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    translation = rng.normal(size=3)
    for same_condition in (True, False):
        original = bounded_affine_distance(
            left,
            right,
            same_condition=same_condition,
        )["distance"]
        transformed = bounded_affine_distance(
            rigid_transform(left, rotation, translation),
            rigid_transform(right, rotation, translation),
            same_condition=same_condition,
        )["distance"]
        assert np.isclose(original, transformed, atol=1e-8)


def test_box_count_recovers_line_surface_and_volume_dimensions() -> None:
    cases = [
        ("l2_same_cross", 1.0),
        ("p3_same_line", 2.0),
        ("v3_coincident", 3.0),
    ]
    for world, expected in cases:
        estimate = box_count_dimension(
            planted_pair(world)[0],
            samples=100_000,
            seed=11,
        )
        assert abs(estimate["dimension"] - expected) <= 0.25
        assert estimate["r2"] >= 0.98


def test_private_conditions_fail_closed() -> None:
    observed = simulate_pair_observations(
        seed=13,
        world="private_conditions",
        spec=ResponseSetSpec(),
    )
    result = analyze_pair(observed)
    assert result["status"] == "REFUSE_CONDITION_IDENTITY_NOT_SHARED"
    assert result["expected_same"] is False
    assert result["expected_free"] is False
    assert result["expected_attack"] is True


def test_low_noise_crossing_is_recovered_near_zero() -> None:
    observed = simulate_pair_observations(
        seed=17,
        world="l2_same_cross",
        spec=ResponseSetSpec(noise_sd=0.01),
    )
    result = analyze_pair(observed)
    assert result["status"] == "ESTIMATE_READY"
    assert result["same_z"] < 2.0
    assert result["principal_angle_error"] < 2.0


def test_direction_coverage_does_not_determine_connectivity() -> None:
    anchor = finite_direction_family(
        authors=16,
        world="common_anchor",
    )
    tangent = finite_direction_family(
        authors=16,
        world="tangent_segments",
    )
    anchor_graph = pairwise_incidence_graph(
        anchor,
        distance_threshold=1e-9,
    )
    tangent_graph = pairwise_incidence_graph(
        tangent,
        distance_threshold=1e-9,
    )
    assert int(anchor_graph.sum() // 2) == 120
    assert int(tangent_graph.sum() // 2) == 0
