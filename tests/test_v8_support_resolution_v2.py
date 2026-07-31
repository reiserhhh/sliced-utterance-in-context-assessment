"""Tests for the scale-free V8 support-resolution region."""
from __future__ import annotations

import numpy as np

from suica_core.v8_support_resolution_v2 import (
    _simultaneous_band,
    build_spectral_bank,
    gains,
    sharp_capacity_weights,
)


def test_sharpness_constraints_hold() -> None:
    eigenvalues = np.asarray([0.35, 0.25, 0.15, 0.10, 0.06, 0.04, 0.03, 0.02])
    weights = sharp_capacity_weights(eigenvalues, 3, 0.5)
    c = 3 / len(eigenvalues)
    assert np.isclose(weights.sum(), 3.0, atol=1e-7)
    assert np.all((weights >= 0) & (weights <= 1))
    assert np.isclose(
        np.sum((weights - c) ** 2),
        0.5 * 3 * (1 - c),
        rtol=1e-5,
    )


def test_hard_sharpness_is_top_k_projector() -> None:
    eigenvalues = np.asarray([0.01, 0.02, 0.03, 0.04, 0.20, 0.30])
    weights = sharp_capacity_weights(eigenvalues, 2, 1.0)
    assert np.array_equal(weights, np.asarray([0, 0, 0, 0, 1, 1]))


def test_degenerate_spectrum_does_not_manufacture_a_hard_axis() -> None:
    eigenvalues = np.zeros(6)
    weights = sharp_capacity_weights(eigenvalues, 2, 1.0)
    assert np.allclose(weights, np.full(6, 1 / 3))


def test_complete_bank_covers_all_nontrivial_capacities() -> None:
    density = np.diag(np.asarray([0.35, 0.25, 0.15, 0.10, 0.08, 0.07]))
    bank = build_spectral_bank(density, sharpness=(0.25, 0.5, 1.0))
    assert set(bank.capacities) == set(range(1, 6))
    assert len(bank.capacities) == 5 * 3
    assert np.all(bank.achieved_sharpness <= bank.sharpness + 1e-8)
    assert gains(bank, density).shape == (15,)


def test_simultaneous_band_contains_point_with_zero_bootstrap_error() -> None:
    observed = np.asarray([0.1, 0.2, 0.3])
    bootstrap = np.tile(observed, (20, 1))
    low, high, critical = _simultaneous_band(observed, bootstrap)
    assert np.allclose(low, observed)
    assert np.allclose(high, observed)
    assert critical == 0.0
