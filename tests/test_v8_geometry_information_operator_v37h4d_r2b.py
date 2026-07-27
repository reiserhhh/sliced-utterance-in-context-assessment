"""Tests for the H4D-R2B geometry information operator."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from scripts.run_suica_v8_geometry_information_operator_v37h4d_r2b import (
    _geometry_plan,
    _read,
    _source_lock,
    _spec,
)
from suica_core.v8_geometry_information_operator import (
    GEOMETRY_FAMILIES,
    build_geometry_interaction,
    geometry_information_coordinates,
    match_residual_information,
    weighted_whitened_residual,
)
from suica_core.v8_minority_information_frontier import (
    complete_double_center,
    expected_panel_variance,
    plant_minority_interaction,
    residual_precision_energy,
)
from suica_core.v8_reference_measure_frontier import simulate_reference_world


ROOT = Path(__file__).resolve().parents[1]
CONFIG = (
    ROOT / "configs/v8_geometry_information_operator_v37h4d_r2b.json"
)


def _config() -> dict:
    config = _read(CONFIG)
    config["_active_permutations"] = 19
    return config


def _world(seed: int) -> dict:
    config = _config()
    spec = _spec(config)
    return simulate_reference_world(
        seed=seed,
        world="additive",
        effect_share=0.0,
        reference_jsd=0.15,
        support_coverage=1.0,
        near_kernel_fraction=0.02,
        noise_mode="gaussian",
        opportunity_prefixes=(64, 128, 256),
        author_tilt=float(config["author_tilt"]),
        author_amplitude=float(config["author_amplitude"]),
        condition_amplitude=float(config["condition_amplitude"]),
        society_amplitude=float(config["society_amplitude"]),
        group_amplitude=float(config["group_amplitude"]),
        panel_noise_amplitude=float(config["panel_noise_amplitude"]),
        technical_noise_amplitude=float(
            config["technical_noise_amplitude"]
        ),
        student_df=float(config["student_df"]),
        heteroskedastic_strength=float(
            config["heteroskedastic_strength"]
        ),
        minority_author_fraction=0.1,
        minority_condition_fraction=0.25,
        spec=spec,
        acquisition_reference_shift=True,
    )


def _anchor(seed: int) -> tuple[dict, dict, dict]:
    config = _config()
    spec = _spec(config)
    world = _world(seed)
    planted, audit = plant_minority_interaction(
        world,
        spec=spec,
        seed=seed + 1,
        active_test_authors=8,
        active_conditions=4,
        support_scheme="fixed",
        interaction_shape="iid_block",
        scaling_arm="active_snr",
        global_effect_share=0.20,
        active_cell_snr=15.0,
        primary_opportunities=128,
        panel_noise_amplitude=float(config["panel_noise_amplitude"]),
        technical_noise_amplitude=float(
            config["technical_noise_amplitude"]
        ),
        heteroskedastic_strength=float(
            config["heteroskedastic_strength"]
        ),
    )
    return world, planted, audit


def test_weighted_operator_energy_matches_precision_quadratic() -> None:
    rng = np.random.default_rng(604_001)
    residual = complete_double_center(rng.normal(size=(8, 4, 3)))
    variance = rng.uniform(0.1, 1.0, size=(8, 4))
    whitened = weighted_whitened_residual(residual, variance)
    assert np.isclose(
        np.sum(whitened**2),
        residual_precision_energy(residual, variance),
        rtol=1e-10,
        atol=1e-10,
    )


def test_all_registered_geometries_match_anchor_information() -> None:
    config = _config()
    spec = _spec(config)
    world, anchor, audit = _anchor(604_010)
    _, _, test = spec.author_split
    active = np.asarray(audit["selected_test_authors"], dtype=int)
    conditions = np.asarray(audit["selected_conditions"], dtype=int)
    for index, family in enumerate(GEOMETRY_FAMILIES):
        interaction = build_geometry_interaction(
            anchor["interaction"],
            spec=spec,
            test_authors=test,
            active_test_authors=active,
            active_conditions=conditions,
            geometry_family=family,
            halo_lambda=0.06,
            seed=604_020 + index,
        )
        matched, match = match_residual_information(
            world,
            interaction,
            target_information=float(
                audit["information_budget_residual"]
            ),
            spec=spec,
            active_test_authors=active,
            active_conditions=conditions,
            primary_opportunities=128,
            panel_noise_amplitude=float(
                config["panel_noise_amplitude"]
            ),
            technical_noise_amplitude=float(
                config["technical_noise_amplitude"]
            ),
            heteroskedastic_strength=float(
                config["heteroskedastic_strength"]
            ),
        )
        assert match["information_match_relative_error"] < 1e-10
        coordinates = geometry_information_coordinates(
            world,
            matched,
            spec=spec,
            active_test_authors=active,
            active_conditions=conditions,
            primary_opportunities=128,
            panel_noise_amplitude=float(
                config["panel_noise_amplitude"]
            ),
            technical_noise_amplitude=float(
                config["technical_noise_amplitude"]
            ),
            heteroskedastic_strength=float(
                config["heteroskedastic_strength"]
            ),
        )
        assert np.isclose(
            coordinates["operator_total_information"],
            match["matched_residual_information"],
            rtol=1e-8,
        )
        assert coordinates["operator_neff_author"] >= 1.0
        assert 0.0 <= coordinates["operator_rho3"] <= 1.0
        assert 0.0 <= coordinates["operator_whitened_leakage"] <= 1.0


def test_geometry_plan_cycles_halo_lambda_only() -> None:
    config = _config()
    observed = [
        next(
            item["halo_lambda"]
            for item in _geometry_plan(config, repetition=repetition)
            if item["geometry_family"] == "halo_sweep"
        )
        for repetition in range(4)
    ]
    assert observed == list(config["halo_lambda_grid"])


def test_r2b_source_lock_matches_frozen_detector() -> None:
    assert _source_lock(_config())["pass"]
