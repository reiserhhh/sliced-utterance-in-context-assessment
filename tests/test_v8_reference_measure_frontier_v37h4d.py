"""Tests for the V3.7H.4D reference-measure frontier."""
from __future__ import annotations

import numpy as np

from scripts.run_suica_v8_reference_measure_frontier_v37h4d import (
    _read,
    _score_at_k,
    _select_pseudocount,
    _spec,
)
from suica_core.v8_reference_measure_frontier import (
    ReferenceFrontierSpec,
    empirical_structural_zero,
    higher_criticism_stat,
    jensen_shannon,
    reference_pair,
    reference_score,
    simulate_reference_world,
)


def _config() -> dict:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    return _read(root / "configs/v8_reference_measure_frontier_v37h4d.json")


def _world(
    world: str,
    *,
    seed: int,
    effect_share: float = 0.20,
    reference_jsd: float = 0.0,
    support_coverage: float = 1.0,
    near_kernel_fraction: float = 0.02,
) -> dict:
    config = _config()
    spec = _spec(config)
    return simulate_reference_world(
        seed=seed,
        world=world,
        effect_share=effect_share,
        reference_jsd=reference_jsd,
        support_coverage=support_coverage,
        near_kernel_fraction=near_kernel_fraction,
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
    )


def test_reference_pair_hits_registered_jsd() -> None:
    left, right, achieved = reference_pair(16, 0.15)
    assert np.isclose(left.sum(), 1.0)
    assert np.isclose(right.sum(), 1.0)
    assert np.isclose(achieved, 0.15, atol=1e-8)
    assert np.isclose(jensen_shannon(left, right), 0.15, atol=1e-8)


def test_reference_score_changes_under_nonorthogonal_interaction() -> None:
    world = _world("noncentered", seed=402_101)
    uniform = world["reference"]
    tilted, _, _ = reference_pair(16, 0.10)
    score_uniform = reference_score(world["cell_truth"], uniform)
    score_tilted = reference_score(world["cell_truth"], tilted)
    assert np.sqrt(np.mean((score_uniform - score_tilted) ** 2)) > 0.01


def test_support_violation_is_detected_without_oracle_imputation() -> None:
    config = _config()
    spec = _spec(config)
    world = _world(
        "support_violation",
        seed=402_102,
        support_coverage=0.75,
    )
    train, calibration, _ = spec.author_split
    assert empirical_structural_zero(
        world["counts_by_k"][128],
        np.concatenate([train, calibration]),
        world["group_labels"],
    )
    assert np.isclose(world["achieved_support_coverage"], 0.75)


def test_aq_alias_has_identical_observations() -> None:
    world = _world("aq_alias", seed=402_103)
    assert world["alias_identity_error"] <= 1e-12


def test_full_rank_world_is_not_a_rank_three_construction() -> None:
    world = _world("full_rank", seed=402_104)
    assert float(world["effective_rank"]) > 20.0


def test_reference_weighting_reduces_registered_environment_shift() -> None:
    config = _config()
    spec = _spec(config)
    world = _world(
        "reference_shift",
        seed=402_105,
        reference_jsd=0.15,
    )
    pseudocount, _ = _select_pseudocount(
        world,
        opportunities=128,
        candidates=[
            float(value)
            for value in config["propensity_pseudocounts"]
        ],
        spec=spec,
    )
    score = _score_at_k(
        world,
        opportunities=128,
        pseudocount=pseudocount,
        spec=spec,
    )
    assert score["reference_correction_gain"] > 0.0
    assert score["common_score_correlation"] > 0.8


def test_higher_criticism_distinguishes_sparse_replication() -> None:
    rng = np.random.default_rng(402_106)
    left = rng.normal(size=(64, 16, 6))
    right_null = rng.normal(size=(64, 16, 6))
    right_signal = right_null.copy()
    right_signal[:8, :4] = left[:8, :4] + 0.05 * rng.normal(
        size=(8, 4, 6)
    )
    mask = np.ones((64, 16), dtype=bool)
    assert higher_criticism_stat(
        left,
        right_signal,
        mask,
    ) > higher_criticism_stat(left, right_null, mask)


def test_registered_author_split_is_stratified() -> None:
    spec = ReferenceFrontierSpec()
    train, calibration, test = spec.author_split
    assert (len(train), len(calibration), len(test)) == (128, 64, 64)
    _, groups = spec.author_labels
    for group in range(spec.groups):
        assert np.sum(groups[train] == group) == 4
        assert np.sum(groups[calibration] == group) == 2
        assert np.sum(groups[test] == group) == 2
