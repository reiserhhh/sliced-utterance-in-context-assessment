"""Tests for V3.7F external-zero and information-preserving mechanics."""
from __future__ import annotations

import numpy as np

from suica_core.v8_external_zero_uncertainty import (
    ExternalZeroWorldSpec,
    apply_external_zero_denoiser,
    confidence_region_metrics,
    cross_validated_external_rank_selection,
    fit_error_asymptote,
    fit_external_zero_denoiser,
    functional_anova_energy,
    simulate_external_zero_world,
    stable_spectrum,
    subset_authors,
    unresolved_residual,
    with_event_budget,
)


def test_dense_spectrum_has_no_zero_stable_direction() -> None:
    weights = stable_spectrum(
        world="dense_tail48",
        dimension=48,
        exponent=0.75,
    )
    assert np.all(weights > 0.0)
    hard = stable_spectrum(
        world="hard_rank12",
        dimension=48,
        exponent=0.75,
    )
    assert np.count_nonzero(hard) == 12


def test_external_zero_is_a_fixed_point() -> None:
    rng = np.random.default_rng(37_701)
    left = rng.normal(size=(64, 12))
    right = left + rng.normal(scale=0.2, size=left.shape)
    zero = rng.normal(size=12)
    fit = fit_external_zero_denoiser(
        left,
        right,
        external_zero=zero,
        rank=4,
    )
    score = apply_external_zero_denoiser(zero[None], fit)
    assert np.allclose(score[0], zero)


def test_hard_projection_and_residual_reconstruct_profile() -> None:
    rng = np.random.default_rng(37_702)
    left = rng.normal(size=(64, 10))
    right = left + rng.normal(scale=0.1, size=left.shape)
    zero = np.zeros(10)
    fit = fit_external_zero_denoiser(
        left,
        right,
        external_zero=zero,
        rank=4,
    )
    score = apply_external_zero_denoiser(left, fit)
    residual = unresolved_residual(left, fit)
    assert np.allclose(score + residual, left)


def test_external_rank_selector_rejects_permuted_pairs() -> None:
    rng = np.random.default_rng(37_703)
    left = rng.normal(size=(96, 24))
    right = left + rng.normal(scale=0.2, size=left.shape)
    candidates = [0, 2, 4, 8, 12, 24]
    selected, _ = cross_validated_external_rank_selection(
        left,
        right,
        external_zero=np.zeros(24),
        candidates=candidates,
        folds=4,
        seed=37_704,
    )
    permuted, _ = cross_validated_external_rank_selection(
        left,
        right[rng.permutation(len(right))],
        external_zero=np.zeros(24),
        candidates=candidates,
        folds=4,
        seed=37_704,
    )
    assert selected > 0
    assert permuted <= 2


def test_world_budget_and_subset_preserve_latent_probability() -> None:
    world = simulate_external_zero_world(
        seed=37_705,
        spec=ExternalZeroWorldSpec(
            authors=40,
            events_per_context_session=64,
        ),
    )
    low = with_event_budget(world, 32)
    subset = subset_authors(low, np.arange(12))
    assert low["probability"] is world["probability"]
    assert subset["probability"].shape[0] == 12
    assert np.all(low["trials"] == 2)


def test_functional_anova_reconstructs_balanced_cloud() -> None:
    rng = np.random.default_rng(37_706)
    values = rng.normal(size=(4, 5, 6, 3, 7))
    result = functional_anova_energy(values)
    assert result["reconstruction_error"] < 1e-12
    assert result["total"] > 0.0


def test_error_asymptote_recovers_positive_floor() -> None:
    budget = np.asarray([32, 64, 128, 256, 512])
    truth = 0.08 + 2.0 * budget.astype(float) ** -0.8
    result = fit_error_asymptote(budget, truth)
    assert abs(result["floor"] - 0.08) < 1e-4
    assert abs(result["alpha"] - 0.8) < 1e-3


def test_empirical_confidence_region_accepts_center_truth() -> None:
    rng = np.random.default_rng(37_707)
    values = rng.normal(scale=0.2, size=(120, 4, 6))
    truth = np.zeros((4, 6))
    result = confidence_region_metrics(values, truth)
    assert 0.80 <= result["coverage"] <= 1.0
    assert result["median_radius"] > 0.0
