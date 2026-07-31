"""Tests for the V8 shared-gauge spectral-order replay."""
from __future__ import annotations

import numpy as np

from suica_core.v8_spectral_order_replay import (
    lorenz_excess,
    simultaneous_sup_band,
    spectral_signature,
)


def test_lorenz_excess_is_zero_for_isotropic_density() -> None:
    density = np.eye(6) / 6
    assert np.allclose(lorenz_excess(density), 0.0)


def test_concentrated_density_majorizes_diffuse_density() -> None:
    concentrated = np.diag([0.55, 0.20, 0.10, 0.07, 0.05, 0.03])
    diffuse = np.diag([0.25, 0.20, 0.18, 0.15, 0.12, 0.10])
    difference = lorenz_excess(concentrated) - lorenz_excess(diffuse)
    assert np.all(difference >= -1e-12)
    assert np.any(difference > 0)


def test_q_one_signature_matches_lorenz_excess() -> None:
    density = np.diag([0.40, 0.25, 0.15, 0.10, 0.06, 0.04])
    signature = spectral_signature(density, sharpness=(1.0,))
    assert np.allclose(signature["gain"], lorenz_excess(density))


def test_sup_band_handles_zero_variance_plateau() -> None:
    observed = np.asarray([0.2, 0.1, 0.0, 0.0])
    bootstrap = np.asarray(
        [
            [0.21, 0.11, 0.0, 0.0],
            [0.19, 0.09, 0.0, 0.0],
            [0.20, 0.10, 0.0, 0.0],
        ]
    )
    low, high, critical = simultaneous_sup_band(observed, bootstrap)
    assert np.isclose(critical, 0.01)
    assert np.allclose(high - low, 0.02)
