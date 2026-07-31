"""Tests for permutation-orbit standardization."""
from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v8_order_statistic_null import ExactPermutationPanel
from suica_core.v8_permutation_orbit_phase import (
    _block_haar_null,
    _regularized_orbit_coordinates,
    build_orbit_phase_panel,
    mean_orbit_covariance,
)


def test_regularized_orbit_coordinates_are_centered_and_scale_invariant() -> None:
    rng = np.random.default_rng(4)
    orbit = rng.normal(size=(24, 12))
    first, diagnostic = _regularized_orbit_coordinates(
        orbit,
        ridge_ratio=0.1,
    )
    second, _ = _regularized_orbit_coordinates(
        7.5 * orbit,
        ridge_ratio=0.1,
    )
    assert diagnostic["orbit_rank"] > 0
    assert np.allclose(first.mean(axis=0), 0.0, atol=1e-10)
    assert np.allclose(first, second, atol=1e-9)


def test_phase_panel_preserves_all_permutations_and_zero_mean() -> None:
    rng = np.random.default_rng(8)
    values = rng.normal(size=(2, 2, 24, 10)).astype(np.float32)
    values -= values.mean(axis=2, keepdims=True)
    metadata = pd.DataFrame(
        {
            "corpus": ["x", "x"],
            "author_id": ["a", "b"],
            "context": ["c", "c"],
            "split": ["D0", "D1"],
        }
    )
    panel = ExactPermutationPanel(metadata=metadata, residuals=values)
    result = build_orbit_phase_panel(
        panel,
        scale=np.ones(10),
        ridge_ratio=0.1,
    )
    assert result.phase.residuals.shape == values.shape
    assert np.allclose(result.phase.residuals.mean(axis=2), 0.0, atol=1e-6)
    covariance = mean_orbit_covariance(result.standardized.residuals)
    assert covariance.shape == (10, 10)
    assert np.linalg.eigvalsh(covariance).min() >= -1e-8


def test_block_haar_preserves_metric_shapes() -> None:
    rng = np.random.default_rng(12)
    left, _ = np.linalg.qr(rng.normal(size=(10, 3)), mode="reduced")
    right, _ = np.linalg.qr(rng.normal(size=(10, 3)), mode="reduced")
    result = _block_haar_null(
        left,
        right,
        np.full(3, 1 / 3),
        block_sizes=(4, 6),
        draws=19,
        rng=rng,
    )
    assert result["hs"].shape == (19,)
    assert result["fidelity"].shape == (19,)
