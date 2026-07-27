"""Tests for the V3.7H.3 multiscale zero-identification battery."""
from __future__ import annotations

import numpy as np

from suica_core.v8_multiscale_zero_identification import (
    ALL_COMPONENTS,
    MultiscaleZeroSpec,
    coarse_graining_assay,
    decompose_balanced_panel,
    generate_multiscale_basis,
    measurement_energies,
    minority_near_kernel_assay,
    persistent_alias_assay,
    simulate_multiscale_panel,
    simulate_selection_assay,
)


def _spec() -> MultiscaleZeroSpec:
    return MultiscaleZeroSpec(
        societies=4,
        groups_per_society=3,
        authors_per_group=5,
        conditions=5,
        response_rank=2,
        opportunities=4,
        technical_streams=2,
        dimensions=4,
    )


def _zero_scales() -> dict[str, float]:
    return {component: 0.0 for component in ALL_COMPONENTS}


def test_noise_free_balanced_decomposition_is_exact() -> None:
    spec = _spec()
    basis = generate_multiscale_basis(
        seed=83_101,
        spec=spec,
        noise_mode="gaussian",
    )
    scales = _zero_scales()
    for component in (
        "social",
        "group",
        "author",
        "condition",
        "response",
    ):
        scales[component] = 0.6
    panel = simulate_multiscale_panel(basis, scales=scales)
    fitted = decompose_balanced_panel(panel)
    assert float(fitted["reconstruction_error"]) <= 1e-12
    for component in (
        "social",
        "group",
        "author",
        "condition",
        "response",
    ):
        assert np.allclose(
            fitted[component][0],
            0.6 * basis[component],
            atol=1e-10,
        )
        assert np.array_equal(
            fitted[component][0],
            fitted[component][1],
        )


def test_opportunity_and_technical_energy_estimators_recover_units() -> None:
    spec = _spec()
    basis = generate_multiscale_basis(
        seed=83_102,
        spec=spec,
        noise_mode="gaussian",
    )
    scales = _zero_scales()
    scales["opportunity"] = 0.7
    scales["technical"] = 0.4
    panel = simulate_multiscale_panel(basis, scales=scales)
    energy = measurement_energies(panel)
    assert abs(energy["technical"] - 0.4**2) < 1e-10
    assert abs(energy["opportunity"] - 0.7**2) < 0.03


def test_symmetric_zero_path_is_quadratic_and_separated() -> None:
    spec = _spec()
    basis = generate_multiscale_basis(
        seed=83_103,
        spec=spec,
        noise_mode="gaussian",
    )
    background = {component: 0.15 for component in ALL_COMPONENTS}
    zero = background.copy()
    zero["author"] = 0.0
    plus = background.copy()
    plus["author"] = 0.5
    minus = background.copy()
    minus["author"] = -0.5
    e0 = measurement_energies(
        simulate_multiscale_panel(basis, scales=zero)
    )
    ep = measurement_energies(
        simulate_multiscale_panel(basis, scales=plus)
    )
    em = measurement_energies(
        simulate_multiscale_panel(basis, scales=minus)
    )
    even = {
        component: 0.5 * (ep[component] + em[component]) - e0[component]
        for component in ALL_COMPONENTS
    }
    assert abs(even["author"] - 0.25) < 1e-10
    for component in ALL_COMPONENTS:
        if component != "author":
            assert abs(even[component]) < 1e-10


def test_coarse_graining_separates_independent_and_common_structure() -> None:
    rows = coarse_graining_assay(
        seed=83_104,
        sizes=(2, 4, 8, 16, 32, 64),
        units=2048,
        dimensions=4,
    )
    by_family: dict[str, list[tuple[int, float]]] = {}
    for row in rows:
        by_family.setdefault(str(row["family"]), []).append(
            (int(row["size"]), float(row["energy"]))
        )

    def slope(family: str) -> float:
        pairs = sorted(by_family[family])
        return float(np.polyfit(
            np.log([size for size, _ in pairs]),
            np.log([energy for _, energy in pairs]),
            1,
        )[0])

    assert -1.08 < slope("author_independent_to_group_mean") < -0.92
    assert -0.03 < slope("group_common_across_authors") < 0.03
    assert -1.08 < slope("group_independent_to_society_mean") < -0.92
    assert -0.03 < slope("society_common_across_groups") < 0.03


def test_selection_standardization_repairs_reversal_and_commutator() -> None:
    result = simulate_selection_assay(
        seed=83_105,
        authors=256,
        conditions=6,
        forced_per_condition=2,
        extra_draws=64,
        selection_strength=2.5,
        author_effect=0.5,
        condition_effect=2.0,
        noise_sd=0.2,
    )
    assert result["naive_author_correlation"] < 0.0
    assert result["standardized_author_correlation"] > 0.9
    assert result["raw_commutator"] > 0.01
    assert result["balanced_to_raw_ratio"] < 0.1


def test_alias_and_near_kernel_boundaries_are_exact() -> None:
    alias = persistent_alias_assay(seed=83_106, shape=(20, 8))
    assert alias["identity_error"] == 0.0
    assert alias["classification"] == "CAUSE_UNIDENTIFIED"
    rows = minority_near_kernel_assay(
        seed=83_107,
        authors=4096,
        dimensions=6,
        prevalence=(0.05, 0.25, 1.0),
        observable_fraction=(0.0, 0.1, 1.0),
        individual_energy=0.1,
    )
    assert max(float(row["relative_error"]) for row in rows) < 1e-10
