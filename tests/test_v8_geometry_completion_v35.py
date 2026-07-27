"""Tests for V3.5 scale, null, transversality, and manifold completion."""
from __future__ import annotations

import numpy as np

from suica_core.v8_geometry_completion import (
    GeometryCompletionSpec,
    _candidate_edges,
    analyze_scale_world,
    classify_curve_relation,
    classify_surface_relation,
    exact_birth_profiles,
    scale_matching_features,
    simulate_curve_relation,
    simulate_scale_pair,
    simulate_surface_relation,
)


def _spec() -> GeometryCompletionSpec:
    return GeometryCompletionSpec(
        permutations=199,
        bootstrap_repetitions=49,
    )


def test_exact_birth_and_grid_stable_group_recovery() -> None:
    spec = _spec()
    pair = simulate_scale_pair(seed=71, spec=spec, noiseless=True)
    candidates = _candidate_edges(pair["positive_views"], spec=spec)
    profiles = exact_birth_profiles(
        pair["positive_views"],
        candidates,
        spec=spec,
    )
    births = [
        value
        for profile in profiles.values()
        for value in profile[: spec.active_conditions]
    ]
    assert max(
        abs(value - spec.shape_birth_radius)
        for value in births
    ) <= 1e-8
    result = analyze_scale_world(
        pair["positive_views"],
        pair["labels"],
        seed=71,
        spec=spec,
    )
    assert result["group_claim"]
    assert result["group_f1"] == 1.0
    assert all(result["grid_agreement"].values())


def test_condition_permutation_preserves_geometry_but_breaks_membership() -> None:
    spec = _spec()
    pair = simulate_scale_pair(seed=73, spec=spec)
    positive = scale_matching_features(
        pair["positive_views"],
        spec=spec,
    )
    negative = scale_matching_features(
        pair["negative_views"],
        spec=spec,
    )
    assert np.allclose(positive, negative)
    result = analyze_scale_world(
        pair["negative_views"],
        pair["labels"],
        seed=73,
        spec=spec,
    )
    assert not result["group_claim"]
    assert result["p_fwer"] > 0.01


def test_curve_relations_and_boundary() -> None:
    spec = _spec()
    expected = {
        "transverse": "TRANSVERSE",
        "tangent": "TANGENT",
        "coincident": "COINCIDENT",
        "near_miss": "NO_INTERSECTION",
    }
    for index, (world, relation) in enumerate(expected.items()):
        sample = simulate_curve_relation(
            seed=79 + index,
            world=world,
            spec=spec,
        )
        result = classify_curve_relation(
            sample,
            seed=79 + index,
            spec=spec,
        )
        assert result["relation"] == relation
    boundary = classify_curve_relation(
        simulate_curve_relation(seed=89, world="boundary", spec=spec),
        seed=89,
        spec=spec,
    )
    assert boundary["status"] == "REFUSE_GEOMETRY_BOUNDARY"


def test_nonlinear_surface_relations_and_dimensions() -> None:
    spec = _spec()
    expected = {
        "transverse": ("TRANSVERSE", 1.0),
        "coincident": ("COINCIDENT", 2.0),
        "sinusoidal_transverse": ("TRANSVERSE", 1.0),
        "rbf_transverse": ("TRANSVERSE", 1.0),
        "reparameterized_transverse": ("TRANSVERSE", 1.0),
    }
    for index, (world, (relation, dimension)) in enumerate(
        expected.items()
    ):
        sample = simulate_surface_relation(
            seed=97 + index,
            world=world,
            spec=spec,
        )
        result = classify_surface_relation(
            sample,
            seed=97 + index,
            spec=spec,
        )
        assert result["relation"] == relation
        assert result["intersection_dimension"] == dimension


def test_surface_tangent_near_miss_and_boundary() -> None:
    spec = _spec()
    tangent = classify_surface_relation(
        simulate_surface_relation(seed=107, world="tangent", spec=spec),
        seed=107,
        spec=spec,
    )
    near_miss = classify_surface_relation(
        simulate_surface_relation(seed=109, world="near_miss", spec=spec),
        seed=109,
        spec=spec,
    )
    boundary = classify_surface_relation(
        simulate_surface_relation(seed=113, world="boundary", spec=spec),
        seed=113,
        spec=spec,
    )
    assert tangent["relation"] == "TANGENT"
    assert near_miss["relation"] == "NO_INTERSECTION"
    assert boundary["status"] == "REFUSE_GEOMETRY_BOUNDARY"
