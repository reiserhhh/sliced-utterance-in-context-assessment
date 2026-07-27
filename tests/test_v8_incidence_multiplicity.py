"""Tests for SUICA V8 incidence multiplicity."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import roc_auc_score

from scripts.run_suica_v8_incidence_multiplicity import (
    _calibrate_population_threshold,
    _validate_calibration_power,
)
from suica_core.v8_incidence_multiplicity import (
    MultiplicitySpec,
    analyze_population,
    condition_reparameterization_consistency,
    minimum_enclosing_ball,
    rank_condition_coordinate,
    simulate_population,
    verified_hyperedges,
)


def test_rank_condition_coordinate_is_monotone_reparameterization_invariant() -> None:
    original = np.linspace(-1.0, 1.0, 21)
    transformed = 0.4 + 2.7 * np.sign(original) * np.abs(original) ** 1.7
    assert np.allclose(
        rank_condition_coordinate(original),
        rank_condition_coordinate(transformed),
    )


def test_minimum_enclosing_ball_recovers_triangle_circumradius() -> None:
    points = np.asarray([
        [1.0, 0.0],
        [-0.5, np.sqrt(3.0) / 2.0],
        [-0.5, -np.sqrt(3.0) / 2.0],
    ])
    center, radius = minimum_enclosing_ball(points)
    assert np.allclose(center, np.zeros(2), atol=1e-8)
    assert np.isclose(radius, 1.0, atol=1e-8)


def test_common_ball_verification_rejects_pairwise_chain() -> None:
    chain = np.asarray([
        [0.0, 0.0],
        [1.5, 0.0],
        [3.0, 0.0],
    ])
    hyperedges = verified_hyperedges(chain, epsilon=1.0)
    assert not any(len(edge) == 3 for edge in hyperedges)


def test_clear_group_world_has_recoverable_pair_structure() -> None:
    spec = MultiplicitySpec()
    population = simulate_population(
        seed=41,
        world="group_regional_affine_2d",
        spec=spec,
    )
    result = analyze_population(
        population,
        ridge_alpha=spec.ridge_alpha,
        epsilon_grid=spec.epsilon_grid,
    )
    assert roc_auc_score(
        result["pair_labels"],
        result["pair_scores"],
    ) >= 0.95
    assert result["estimated_multiplicity"] == 6.0


def test_global_anchor_has_high_raw_multiplicity_but_no_group_auc() -> None:
    spec = MultiplicitySpec()
    population = simulate_population(
        seed=43,
        world="global_common_anchor_2d",
        spec=spec,
    )
    result = analyze_population(
        population,
        ridge_alpha=spec.ridge_alpha,
        epsilon_grid=spec.epsilon_grid,
    )
    auc = roc_auc_score(result["pair_labels"], result["pair_scores"])
    assert result["max_raw_multiplicity"] == spec.authors
    assert 0.35 <= auc <= 0.65


def test_condition_reparameterization_is_pipeline_invariant() -> None:
    spec = MultiplicitySpec()
    population = simulate_population(
        seed=47,
        world="group_tangent_quadratic_2d",
        spec=spec,
    )
    assert np.isclose(
        condition_reparameterization_consistency(
            population,
            ridge_alpha=spec.ridge_alpha,
        ),
        1.0,
        atol=1e-10,
    )


def test_population_calibration_does_not_confuse_one_local_null_edge_for_group() -> None:
    authors = 6
    upper = np.triu_indices(authors, 1)
    labels = np.asarray([0, 0, 0, 1, 1, 1])
    pair_labels = (labels[upper[0]] == labels[upper[1]]).astype(int)
    clear = {
        "status": "ESTIMATE_READY",
        "kind": "clear_group",
        "world": "clear",
        "pair_labels": pair_labels,
        "hyperedges": [
            {"members": [0, 1, 2], "persistence": 0.30},
            {"members": [3, 4, 5], "persistence": 0.30},
        ],
    }
    null = {
        "status": "ESTIMATE_READY",
        "kind": "null",
        "world": "null",
        "pair_labels": np.zeros_like(pair_labels),
        "hyperedges": [
            {"members": [0, 1, 2], "persistence": 0.40},
        ],
    }
    diagnostics = _calibrate_population_threshold(
        [*[dict(clear) for _ in range(20)],
         *[dict(null) for _ in range(100)]],
        authors=authors,
        minimum_coverage=0.75,
        gates={
            "maximum_false_group_upper_95": 0.03,
            "minimum_group_f1": 0.80,
            "minimum_group_ari": 0.70,
        },
    )
    selected = diagnostics[diagnostics["selected"]].iloc[0]
    assert selected["null_control_pass"]
    assert selected["clear_recovery_pass"]
    assert float(selected["threshold"]) <= 0.30


def test_population_calibration_controls_each_null_world_not_only_pool() -> None:
    authors = 6
    upper = np.triu_indices(authors, 1)
    labels = np.asarray([0, 0, 0, 1, 1, 1])
    pair_labels = (labels[upper[0]] == labels[upper[1]]).astype(int)
    clear = {
        "status": "ESTIMATE_READY",
        "kind": "clear_group",
        "world": "clear",
        "pair_labels": pair_labels,
        "hyperedges": [
            {"members": [0, 1, 2], "persistence": 0.30},
            {"members": [3, 4, 5], "persistence": 0.30},
        ],
    }
    bad_null = {
        "status": "ESTIMATE_READY",
        "kind": "null",
        "world": "anchor_null",
        "pair_labels": np.zeros_like(pair_labels),
        "hyperedges": [
            {"members": [0, 1, 2], "persistence": 0.20},
            {"members": [3, 4, 5], "persistence": 0.20},
        ],
    }
    easy_nulls = [
        {
            "status": "ESTIMATE_READY",
            "kind": "null",
            "world": f"easy_null_{index}",
            "pair_labels": np.zeros_like(pair_labels),
            "hyperedges": [],
        }
        for index in range(4)
    ]
    calibration = [dict(clear) for _ in range(20)]
    calibration.extend(dict(bad_null) for _ in range(100))
    for easy in easy_nulls:
        calibration.extend(dict(easy) for _ in range(100))
    diagnostics = _calibrate_population_threshold(
        calibration,
        authors=authors,
        minimum_coverage=0.75,
        gates={
            "maximum_false_group_upper_95": 0.03,
            "minimum_group_f1": 0.80,
            "minimum_group_ari": 0.70,
        },
    )
    selected = diagnostics[diagnostics["selected"]].iloc[0]
    assert selected["null_control_pass"]
    assert selected["clear_recovery_pass"]
    assert 0.20 < float(selected["threshold"]) <= 0.30


def test_calibration_power_check_rejects_unreachable_binomial_gate() -> None:
    config = {
        "calibration_repetitions": 80,
        "gates": {"maximum_false_group_upper_95": 0.03},
    }
    with np.testing.assert_raises_regex(
        ValueError,
        "cannot establish",
    ):
        _validate_calibration_power(config)
    config["calibration_repetitions"] = 120
    _validate_calibration_power(config)
