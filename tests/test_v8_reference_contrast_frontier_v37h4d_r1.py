"""Tests for the V3.7H.4D R1 gauge-invariant contrast repair."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from scripts.run_suica_v8_reference_contrast_frontier_v37h4d_r1 import (
    _evaluate,
)
from scripts.run_suica_v8_reference_measure_frontier_v37h4d import (
    _read,
    _spec,
)
from suica_core.v8_reference_measure_frontier import (
    contrast_bootstrap_interval,
    reference_pair,
    reference_score,
    simulate_reference_world,
    wild_residual_diagnostics,
)


ROOT = Path(__file__).resolve().parents[1]


def _config() -> dict:
    config = _read(
        ROOT / "configs/v8_reference_contrast_frontier_v37h4d_r1.json"
    )
    config["_active_permutations"] = 99
    config["_active_contrast_bootstrap"] = 99
    return config


def _world(world: str, seed: int) -> dict:
    config = _config()
    spec = _spec(config)
    return simulate_reference_world(
        seed=seed,
        world=world,
        effect_share=0.20,
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
        minority_author_fraction=float(
            config["minority_author_fraction"]
        ),
        minority_condition_fraction=float(
            config["minority_condition_fraction"]
        ),
        spec=spec,
        acquisition_reference_shift=True,
    )


def test_reference_contrast_is_gauge_invariant() -> None:
    rng = np.random.default_rng(501_101)
    values = rng.normal(size=(32, 16, 4))
    shift = rng.normal(size=(32, 1, 4))
    left, right, _ = reference_pair(16, 0.15)
    contrast = (
        reference_score(values, right)
        - reference_score(values, left)
    )
    shifted = (
        reference_score(values + shift, right)
        - reference_score(values + shift, left)
    )
    assert np.max(np.abs(contrast - shifted)) < 1e-12


def test_planted_contrast_kernel_and_sensitive_worlds_separate() -> None:
    sensitive = _world("contrast_sensitive", 501_102)
    kernel = _world("contrast_kernel", 501_103)

    def _oracle_delta(world: dict) -> float:
        left = reference_score(
            world["cell_truth"],
            world["contrast_reference_0"],
        )
        right = reference_score(
            world["cell_truth"],
            world["contrast_reference_1"],
        )
        scale = max(float(np.std(world["theta_star"])), 1e-12)
        return float(np.sqrt(np.mean((right - left) ** 2)) / scale)

    assert _oracle_delta(sensitive) > 0.20
    assert _oracle_delta(kernel) < 1e-10


def test_bootstrap_contrast_uses_cross_panel_energy() -> None:
    rng = np.random.default_rng(501_104)
    signal = rng.normal(scale=0.4, size=(64, 6))
    left = signal + rng.normal(scale=0.03, size=(64, 6))
    right = signal + rng.normal(scale=0.03, size=(64, 6))
    theta = rng.normal(size=(64, 6))
    result = contrast_bootstrap_interval(
        left,
        right,
        theta,
        theta,
        seed=501_105,
        draws=199,
    )
    assert result["d_contrast_lower_95"] > 0.20
    assert result["contrast_split_correlation"] > 0.9


def test_wild_null_preserves_author_vector_geometry() -> None:
    rng = np.random.default_rng(501_106)
    left = rng.normal(size=(64, 16, 6))
    right = rng.normal(size=(64, 16, 6))
    mask = np.ones((64, 16), dtype=bool)
    result = wild_residual_diagnostics(
        left,
        right,
        mask,
        mask,
        rank=3,
        seed=501_107,
        permutations=99,
        alpha=0.05,
    )
    assert {
        result["crc_p"],
        result["cross_low_rank_p"],
        result["hc_p"],
    } <= {value / 100 for value in range(1, 101)}


def test_author_centered_residual_has_zero_absolute_projection() -> None:
    world = _world("contrast_sensitive", 501_108)
    config = _config()
    spec = _spec(config)
    _, _, test = spec.author_split
    values = world["cell_truth"][test]
    residual = (
        values
        - values.mean(axis=1, keepdims=True)
        - values.mean(axis=0, keepdims=True)
        + values.mean(axis=(0, 1), keepdims=True)
    )
    projected = residual.mean(axis=1)
    assert np.max(np.abs(projected)) < 1e-12


def test_r1_sensitive_cell_uses_reference_contrast_not_oracle_label() -> None:
    config = _config()
    definition = {
        "world": "contrast_sensitive",
        "cell_kind": "main",
        "noise_mode": "gaussian",
        "effect_share": 0.20,
        "reference_jsd": 0.15,
        "support_coverage": 1.0,
    }
    row, _ = _evaluate(
        definition=definition,
        repetition=0,
        world_seed=501_109,
        diagnostic_seed=501_110,
        contrast_seed=501_111,
        config=config,
    )
    assert row["d_contrast_lower_95"] > 0.20
    assert row["contrast_oracle_correlation"] > 0.8
