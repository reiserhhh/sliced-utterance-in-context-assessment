"""Tests for the R2G.2 hierarchical society-limit frontier."""
from __future__ import annotations

import numpy as np

from suica_core.v8_hierarchical_society_limit import (
    HierarchicalSocietySpec,
    ar1_group_weight,
    correlated_hierarchy_truth,
    cross_view_surface,
    fit_ar1_surface,
    fit_independent_surface,
    fit_local_to_unity_surface,
    hierarchy_cross_level_covariances,
    local_to_unity_group_weight,
    local_to_unity_limit,
    residual_arms,
    simulate_hierarchical_panel,
    test_centered_full_mean_energy as leaky_centering_assay,
)


def _spec() -> HierarchicalSocietySpec:
    return HierarchicalSocietySpec(
        societies=256,
        max_groups=16,
        max_authors=32,
        dimensions=4,
        local_to_unity_c=1.5,
    )


def _exact_rows(
    *,
    society: float,
    group: float,
    author: float,
) -> list[dict[str, float | int]]:
    return [
        {
            "groups": groups,
            "authors": authors,
            "cross_energy": (
                society
                + group / groups
                + author / (groups * authors)
            ),
        }
        for groups in (1, 2, 4, 8, 16)
        for authors in (2, 4, 8, 16, 32)
    ]


def test_independent_surface_recovers_exact_hierarchy() -> None:
    fitted = fit_independent_surface(
        _exact_rows(society=0.03, group=0.06, author=0.09)
    )
    assert abs(fitted["society"] - 0.03) < 1e-12
    assert abs(fitted["group"] - 0.06) < 1e-12
    assert abs(fitted["author"] - 0.09) < 1e-12
    assert fitted["test"]["max_abs_error"] < 1e-12


def test_ar1_weight_and_fit_recover_registered_dependence() -> None:
    rho = 0.72
    assert abs(ar1_group_weight(8, 0.0) - 1.0 / 8.0) < 1e-12
    assert ar1_group_weight(8, rho) > 1.0 / 8.0
    rows = [
        {
            "groups": groups,
            "authors": authors,
            "cross_energy": (
                0.02
                + 0.07 * ar1_group_weight(groups, rho)
                + 0.09 / (groups * authors)
            ),
        }
        for groups in (1, 2, 4, 8, 16, 32)
        for authors in (2, 4, 8, 16, 32)
    ]
    fitted = fit_ar1_surface(rows)
    assert abs(fitted["rho"] - rho) < 1e-5
    assert fitted["test"]["max_abs_error"] < 1e-8


def test_conditional_hierarchy_removes_cross_level_covariance() -> None:
    spec = _spec()
    panel = simulate_hierarchical_panel(
        seed=91_101,
        world="correlated_hierarchy",
        spec=spec,
        noise_mode="gaussian",
    )
    raw = hierarchy_cross_level_covariances(panel["raw_components"])
    centered = hierarchy_cross_level_covariances(
        panel["martingale_components"]
    )
    truth = correlated_hierarchy_truth(spec)
    assert raw["maximum_absolute"] > 0.02
    assert centered["maximum_absolute"] < 0.01
    assert truth["martingale_society"] > spec.society_energy


def test_score_visible_and_unavailable_society_terms_separate() -> None:
    spec = _spec()
    sizes_g = (2, 4, 8, 16)
    sizes_n = (4, 8, 16, 32)
    visible = simulate_hierarchical_panel(
        seed=91_102,
        world="society_completable",
        spec=spec,
        noise_mode="gaussian",
    )
    unavailable = simulate_hierarchical_panel(
        seed=91_103,
        world="unavailable_society_shock",
        spec=spec,
        noise_mode="gaussian",
    )
    visible_arms = residual_arms(visible)
    unavailable_arms = residual_arms(unavailable)
    visible_raw = fit_independent_surface(cross_view_surface(
        *visible_arms["raw"],
        group_sizes=sizes_g,
        author_sizes=sizes_n,
    ))
    visible_admissible = fit_independent_surface(cross_view_surface(
        *visible_arms["admissible"],
        group_sizes=sizes_g,
        author_sizes=sizes_n,
    ))
    unavailable_admissible = fit_independent_surface(cross_view_surface(
        *unavailable_arms["admissible"],
        group_sizes=sizes_g,
        author_sizes=sizes_n,
    ))
    assert visible_raw["society"] > 0.04
    assert abs(visible_admissible["society"]) < 0.015
    assert unavailable_admissible["society"] > 0.04


def test_local_to_unity_has_positive_non_society_limit() -> None:
    c = 1.5
    assert local_to_unity_limit(c) > 0.5
    values = [
        local_to_unity_group_weight(groups, c)
        for groups in (8, 32, 128, 512)
    ]
    assert abs(values[-1] - local_to_unity_limit(c)) < 0.01
    rows = [
        {
            "groups": groups,
            "authors": authors,
            "cross_energy": (
                0.06 * local_to_unity_group_weight(groups, c)
                + 0.08 / (groups * authors)
            ),
        }
        for groups in (2, 4, 8, 16, 32, 64)
        for authors in (2, 4, 8, 16, 32)
    ]
    naive = fit_independent_surface(rows)
    correct = fit_local_to_unity_surface(rows, c=c)
    assert naive["society"] > 0.02
    assert abs(correct["society"]) < 1e-10


def test_test_centering_manufactures_false_zero() -> None:
    panel = simulate_hierarchical_panel(
        seed=91_104,
        world="unavailable_society_shock",
        spec=_spec(),
        noise_mode="gaussian",
    )
    diagnostic = leaky_centering_assay(
        panel["target_a"],
        panel["target_b"],
    )
    assert diagnostic["raw_cross_energy"] > 0.04
    assert (
        abs(diagnostic["leaky_test_centered_cross_energy"])
        < 1e-28
    )


def test_shared_technical_noise_is_second_order_equivalent() -> None:
    spec = _spec()
    panel = simulate_hierarchical_panel(
        seed=91_105,
        world="correlated_view_noise",
        spec=spec,
        noise_mode="gaussian",
    )
    arms = residual_arms(panel)
    structural = fit_independent_surface(cross_view_surface(
        *arms["structural_oracle"],
        group_sizes=(2, 4, 8, 16),
        author_sizes=(4, 8, 16, 32),
    ))
    omniscient = fit_independent_surface(cross_view_surface(
        *arms["omniscient_oracle"],
        group_sizes=(2, 4, 8, 16),
        author_sizes=(4, 8, 16, 32),
    ))
    assert structural["society"] > 0.04
    assert abs(omniscient["society"]) < 0.015
