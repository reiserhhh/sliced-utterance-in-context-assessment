"""Tests for M4-C response-safe condition-manifold discovery."""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from suica_core.m4_condition_manifold_audit import (
    audit_m4_condition_manifold,
)
from suica_core.m4_condition_manifold_contracts import M4ConditionObserved
from suica_core.m4_condition_manifold_estimator import (
    PANEL_NAMES,
    fit_m4_condition_chart,
    fit_m4_condition_manifold,
)
from suica_core.m4_condition_manifold_generator import (
    M4ConditionSpec,
    generate_m4_condition_world,
)


SPEC = M4ConditionSpec(
    reference_authors=12,
    mechanism_authors=10,
    calibration_points=40,
    selection_points=28,
    evaluation_points=40,
    pre_noise=0.05,
    response_noise=0.10,
)

CANDIDATES = (
    {
        "family": "linear_pca",
        "dimensions": 2,
        "neighbors": 7,
        "landmarks": 10,
    },
    {
        "family": "global_isomap",
        "dimensions": 2,
        "neighbors": 7,
        "landmarks": 10,
    },
    {
        "family": "landmark_atlas",
        "dimensions": 2,
        "neighbors": 7,
        "landmarks": 10,
    },
)


def _permuted_response(observed: M4ConditionObserved) -> M4ConditionObserved:
    rng = np.random.default_rng(991)
    panels = {}
    for name in PANEL_NAMES:
        panel = getattr(observed, name)
        response = panel.response.reshape(-1, panel.response.shape[-1]).copy()
        rng.shuffle(response, axis=0)
        panels[name] = replace(
            panel,
            response=response.reshape(panel.response.shape),
        )
    return M4ConditionObserved(**panels, design=dict(observed.design))


def test_condition_generator_is_reproducible() -> None:
    first, truth = generate_m4_condition_world(
        world="source_specific_rotations",
        spec=SPEC,
        seed=701,
    )
    second, repeated_truth = generate_m4_condition_world(
        world="source_specific_rotations",
        spec=SPEC,
        seed=701,
    )
    assert np.allclose(
        first.reference_calibration.pre_context,
        second.reference_calibration.pre_context,
    )
    assert np.allclose(
        truth.geodesic_distances["mechanism_evaluation"],
        repeated_truth.geodesic_distances["mechanism_evaluation"],
    )


def test_chart_is_invariant_to_response_permutation() -> None:
    observed, _ = generate_m4_condition_world(
        world="true_linear_manifold",
        spec=SPEC,
        seed=711,
    )
    original = fit_m4_condition_chart(
        observed,
        candidates=CANDIDATES,
        minimum_coverage=0.60,
    )
    permuted = fit_m4_condition_chart(
        _permuted_response(observed),
        candidates=CANDIDATES,
        minimum_coverage=0.60,
    )
    assert original.selected_family == permuted.selected_family
    assert original.selected_parameters == permuted.selected_parameters
    for name in PANEL_NAMES:
        assert np.allclose(
            original.panel_features[name],
            permuted.panel_features[name],
            atol=1e-12,
            rtol=0.0,
        )


def test_source_rotation_recovers_condition_geometry() -> None:
    observed, truth = generate_m4_condition_world(
        world="source_specific_rotations",
        spec=SPEC,
        seed=721,
    )
    estimate = fit_m4_condition_manifold(
        observed,
        candidates=CANDIDATES,
        minimum_coverage=0.60,
    )
    result = audit_m4_condition_manifold(
        estimate,
        observed,
        truth,
        minimum_geometry=0.65,
        minimum_neighbor_jaccard=0.35,
        minimum_response_retention=0.40,
        minimum_conditional_response_r2=0.55,
        response_perturbation_invariant=True,
    )
    assert result["geometry_spearman"] >= 0.64
    assert result["cross_source_geometry_evaluation"] >= 0.70


def test_declared_response_leakage_is_refused() -> None:
    observed, _ = generate_m4_condition_world(
        world="response_leakage_circular",
        spec=SPEC,
        seed=731,
    )
    chart = fit_m4_condition_chart(
        observed,
        candidates=CANDIDATES,
        minimum_coverage=0.60,
    )
    assert chart.refused is True
    assert any(
        reason.startswith("forbidden_provenance")
        for reason in chart.refusal_reasons
    )


def test_condition_alias_refuses_mechanism_not_quotient_chart() -> None:
    observed, truth = generate_m4_condition_world(
        world="condition_alias",
        spec=SPEC,
        seed=741,
    )
    estimate = fit_m4_condition_manifold(
        observed,
        candidates=CANDIDATES,
        minimum_coverage=0.60,
    )
    result = audit_m4_condition_manifold(
        estimate,
        observed,
        truth,
        minimum_geometry=0.65,
        minimum_neighbor_jaccard=0.35,
        minimum_response_retention=0.55,
        minimum_conditional_response_r2=0.60,
        response_perturbation_invariant=True,
    )
    assert result["oracle_response_r2"] >= 0.50
    assert result["mechanism_underresolved"] == 1.0
    assert result["mechanism_alias_refused"] == 1.0


def test_evaluation_response_does_not_change_chart_selection() -> None:
    observed, _ = generate_m4_condition_world(
        world="true_nonlinear_multichart",
        spec=SPEC,
        seed=751,
    )
    changed = replace(
        observed,
        mechanism_evaluation=replace(
            observed.mechanism_evaluation,
            response=np.zeros_like(
                observed.mechanism_evaluation.response
            ),
        ),
    )
    original = fit_m4_condition_chart(
        observed,
        candidates=CANDIDATES,
        minimum_coverage=0.60,
    )
    modified = fit_m4_condition_chart(
        changed,
        candidates=CANDIDATES,
        minimum_coverage=0.60,
    )
    assert original.selected_family == modified.selected_family
    assert original.selected_parameters == modified.selected_parameters
