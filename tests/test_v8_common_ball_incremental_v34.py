"""Tests for V3.4 common-ball information beyond pair adjacency."""
from __future__ import annotations

import copy

import numpy as np

from suica_core.v8_common_ball_incremental import (
    CommonBallSpec,
    analyze_common_ball_pair,
    common_ball_truth_paths,
    fixed_pair_adjacency_view_tensor,
    simulate_common_ball_pair,
)
from suica_core.v8_incidence_multiplicity import minimum_enclosing_ball


def _pair(
    *,
    seed: int = 41,
    positive_geometry: str = "hexagon",
    positive_radius: float = 0.90,
    negative_geometry: str = "triangle",
    negative_radius: float = 1.10,
) -> tuple[CommonBallSpec, dict[str, object]]:
    spec = CommonBallSpec()
    return spec, simulate_common_ball_pair(
        seed=seed,
        spec=spec,
        positive_geometry=positive_geometry,
        positive_shape_radius=positive_radius,
        negative_geometry=negative_geometry,
        negative_shape_radius=negative_radius,
    )


def test_registered_geometries_have_expected_meb_radii() -> None:
    spec = CommonBallSpec(noise_sd=0.0)
    labels = np.repeat(np.arange(4), 6)
    positive = common_ball_truth_paths(
        labels=labels,
        spec=spec,
        geometry="hexagon",
        shape_radius=0.90,
        seed=17,
    )
    negative = common_ball_truth_paths(
        labels=labels,
        spec=spec,
        geometry="triangle",
        shape_radius=1.10,
        seed=17,
    )
    members = np.flatnonzero(labels == 0)
    _, positive_radius = minimum_enclosing_ball(
        positive[members, 0]
    )
    _, negative_radius = minimum_enclosing_ball(
        negative[members, 0]
    )
    assert np.isclose(positive_radius, 0.90)
    assert np.isclose(negative_radius, 1.10)
    positive_distance = np.linalg.norm(
        positive[members, 0][:, None]
        - positive[members, 0][None, :],
        axis=-1,
    )
    negative_distance = np.linalg.norm(
        negative[members, 0][:, None]
        - negative[members, 0][None, :],
        axis=-1,
    )
    assert positive_distance.max() < 2.0
    assert negative_distance.max() < 2.0


def test_main_world_matches_pair_tensor_but_changes_joint_feasibility() -> None:
    spec, pair = _pair()
    positive_tensor = fixed_pair_adjacency_view_tensor(
        pair["positive_views"],
        spec=spec,
    )
    negative_tensor = fixed_pair_adjacency_view_tensor(
        pair["negative_views"],
        spec=spec,
    )
    assert np.array_equal(positive_tensor, negative_tensor)
    result = analyze_common_ball_pair(pair, spec=spec)
    assert result["status"] == "ESTIMATE_READY"
    assert result["pairwise_output_match"]
    assert result["positive_meb"]["group_claim"]
    assert result["positive_meb"]["group_f1"] == 1.0
    assert not result["negative_meb"]["group_claim"]
    assert result["negative_meb"]["refused"]
    assert result["negative_meb"]["maximum_passing_size"] == 4


def test_mismatch_and_boundary_controls_stop_or_refuse() -> None:
    spec, mismatch = _pair(negative_radius=1.20)
    mismatch_result = analyze_common_ball_pair(mismatch, spec=spec)
    assert mismatch_result["status"] == "STOP_ADJACENCY_MISMATCH"
    assert mismatch_result["view_tensor_mismatch_count"] > 0

    spec, boundary = _pair(negative_radius=1.055)
    boundary_result = analyze_common_ball_pair(boundary, spec=spec)
    assert boundary_result["status"] == "ESTIMATE_READY"
    assert boundary_result["negative_meb"]["status"] == "REFUSE_MARGIN"
    assert not boundary_result["negative_meb"]["group_claim"]


def test_feasible_and_infeasible_controls_agree() -> None:
    spec, feasible = _pair(
        negative_geometry="hexagon",
        negative_radius=0.90,
    )
    feasible_result = analyze_common_ball_pair(feasible, spec=spec)
    assert feasible_result["positive_meb"]["group_claim"]
    assert feasible_result["negative_meb"]["group_claim"]

    spec, infeasible = _pair(
        positive_geometry="triangle",
        positive_radius=1.10,
    )
    infeasible_result = analyze_common_ball_pair(infeasible, spec=spec)
    assert not infeasible_result["positive_meb"]["group_claim"]
    assert not infeasible_result["negative_meb"]["group_claim"]


def test_decision_is_rigid_permutation_and_label_blind() -> None:
    spec, pair = _pair(seed=53)
    original = analyze_common_ball_pair(pair, spec=spec)

    angle = 0.71
    rotation = np.asarray([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle), np.cos(angle)],
    ])
    rigid = copy.deepcopy(pair)
    for key in ("positive_views", "negative_views"):
        rigid[key] = pair[key] @ rotation.T + np.asarray([3.0, -4.0])
    rigid_result = analyze_common_ball_pair(rigid, spec=spec)

    permutation = np.random.default_rng(59).permutation(spec.authors)
    permuted = copy.deepcopy(pair)
    permuted["labels"] = pair["labels"][permutation]
    for key in ("positive_views", "negative_views"):
        permuted[key] = pair[key][:, permutation]
    permuted_result = analyze_common_ball_pair(permuted, spec=spec)

    relabeled = copy.deepcopy(pair)
    relabeled["labels"] = np.random.default_rng(61).permutation(
        pair["labels"]
    )
    relabeled_result = analyze_common_ball_pair(relabeled, spec=spec)

    for result in (rigid_result, permuted_result, relabeled_result):
        assert result["status"] == original["status"]
        assert (
            result["positive_meb"]["group_claim"]
            == original["positive_meb"]["group_claim"]
        )
        assert (
            result["negative_meb"]["group_claim"]
            == original["negative_meb"]["group_claim"]
        )
        assert (
            result["positive_meb"]["maximum_passing_size"]
            == original["positive_meb"]["maximum_passing_size"]
        )
        assert (
            result["negative_meb"]["maximum_passing_size"]
            == original["negative_meb"]["maximum_passing_size"]
        )
