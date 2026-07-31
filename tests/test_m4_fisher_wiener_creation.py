"""Tests for cross-fitted M4 Fisher-Wiener creation estimation."""
from __future__ import annotations

import numpy as np

from suica_core.m4_fisher_wiener_creation import (
    build_fisher_wiener_route,
    fit_fixed_hazard_route,
    fit_selected_hazard_route,
    fisher_wiener_feedback,
    split_opportunity_occasions,
)
from suica_core.m4_chart_ecology_estimator import (
    build_m4_discovered_basis,
)
from suica_core.m4_chart_ecology_generator import (
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_condition_manifold_estimator import (
    fit_m4_condition_chart,
)
from suica_core.m4_physical_edge_composition import (
    fit_m4_physical_edge_route,
)


def test_occasion_split_is_disjoint_and_exhaustive() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="endogenous_creation_expansion",
        spec=M4ChartEcologySpec(
            reference_authors=8,
            mechanism_authors=8,
            reference_calibration_points=24,
            reference_selection_points=16,
            calibration_occasions=5,
            selection_occasions=2,
            evaluation_occasions=5,
            events=32,
        ),
        seed=1401,
    )
    first, second = split_opportunity_occasions(observed.ecology)
    for view in ("train", "test"):
        for role in ("calibration", "selection", "evaluation"):
            original = getattr(observed.ecology, f"{view}_{role}")
            left = getattr(first, f"{view}_{role}")
            right = getattr(second, f"{view}_{role}")
            assert (
                left.menu.shape[1] + right.menu.shape[1]
                == original.menu.shape[1]
            )


def test_fisher_wiener_recovers_stable_author_subspace() -> None:
    rng = np.random.default_rng(1402)
    authors = 64
    width = 10
    latent = rng.normal(size=(authors, 3))
    loading = rng.normal(size=(3, width))
    truth = latent @ loading
    first = truth + rng.normal(scale=1.2, size=truth.shape)
    second = truth + rng.normal(scale=1.2, size=truth.shape)
    raw = truth + rng.normal(scale=0.8, size=truth.shape)
    recovered = fisher_wiener_feedback(first, second, raw)
    assert np.mean((recovered - truth) ** 2) < np.mean(
        (raw - truth) ** 2
    )
    assert np.isfinite(recovered).all()


def test_permuted_half_removes_stable_cross_author_alignment() -> None:
    rng = np.random.default_rng(1403)
    truth = rng.normal(size=(32, 6))
    first = truth + rng.normal(scale=0.2, size=truth.shape)
    second = truth + rng.normal(scale=0.2, size=truth.shape)
    raw = truth + rng.normal(scale=0.2, size=truth.shape)
    ordinary = fisher_wiener_feedback(first, second, raw)
    permuted = fisher_wiener_feedback(
        first,
        second,
        raw,
        second_permutation=rng.permutation(len(second)),
    )
    assert np.var(ordinary, axis=0).mean() > np.var(
        permuted,
        axis=0,
    ).mean()


def test_selected_hazard_replays_physical_creation_and_fw_is_finite() -> None:
    observed, _ = generate_m4_chart_ecology_world(
        world="endogenous_creation_expansion",
        spec=M4ChartEcologySpec(
            reference_authors=8,
            mechanism_authors=8,
            reference_calibration_points=24,
            reference_selection_points=16,
            calibration_occasions=2,
            selection_occasions=2,
            evaluation_occasions=2,
            events=32,
        ),
        seed=1404,
    )
    chart = fit_m4_condition_chart(
        observed.condition,
        candidates=(
            {
                "family": "linear_pca",
                "dimensions": 2,
                "neighbors": 8,
                "landmarks": 16,
            },
        ),
        minimum_cross_source_geometry=-1.0,
        minimum_split_geometry=-1.0,
        minimum_trustworthiness=0.0,
        minimum_continuity=0.0,
        minimum_coverage=0.0,
        maximum_author_leakage_auc=1.0,
    )
    _, basis = build_m4_discovered_basis(
        observed,
        chart,
        maximum_rank=8,
    )
    selected = fit_selected_hazard_route(
        observed.ecology,
        basis,
        ridge=0.005,
        iterations=8,
        complexity_penalty=0.00001,
    )
    physical = fit_m4_physical_edge_route(
        observed.ecology,
        basis,
        basis_name="test",
        ridge_grid=(0.005,),
        hazard_ridge=0.005,
        logistic_iterations=8,
        complexity_penalty=0.00001,
    )
    assert np.allclose(selected.train.creation, physical.train.creation)
    assert np.array_equal(
        selected.test.selected_model,
        physical.test.selected_model,
    )
    first_ecology, second_ecology = split_opportunity_occasions(
        observed.ecology
    )
    full = fit_fixed_hazard_route(
        observed.ecology,
        basis,
        iterations=8,
    )
    first = fit_fixed_hazard_route(
        first_ecology,
        basis,
        iterations=8,
    )
    second = fit_fixed_hazard_route(
        second_ecology,
        basis,
        iterations=8,
    )
    fisher = build_fisher_wiener_route(
        observed.ecology,
        basis,
        full,
        first,
        second,
    )
    assert np.isfinite(fisher.train.creation).all()
    assert np.isfinite(fisher.test.evaluation_loss).all()
