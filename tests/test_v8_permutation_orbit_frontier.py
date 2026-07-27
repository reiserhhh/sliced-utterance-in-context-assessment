"""Unit tests for the H4D-R2C permutation-orbit primitives."""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v8_permutation_orbit_frontier import (
    author_contribution_spectrum,
    build_controlled_halo_interaction,
    frozen_logistic_probability,
    holm_adjust_rows,
    orbit_rejection_probability,
)
from suica_core.v8_reference_measure_frontier import ReferenceFrontierSpec


def test_holm_adjust_rows_matches_known_three_test_cases() -> None:
    raw = np.asarray([
        [0.01, 0.03, 0.20],
        [0.20, 0.01, 0.03],
    ])
    adjusted = holm_adjust_rows(raw)
    assert np.allclose(adjusted[0], [0.03, 0.06, 0.20])
    assert np.allclose(adjusted[1], [0.20, 0.03, 0.06])


def test_author_contribution_spectrum_recovers_equal_support() -> None:
    left = np.zeros((4, 3, 1))
    right = np.zeros_like(left)
    left[:, 0, 0] = [1.0, -1.0, 1.0, -1.0]
    right[:, 0, 0] = left[:, 0, 0]
    mask = np.ones((4, 3), dtype=bool)
    spectrum = author_contribution_spectrum(left, right, mask, mask)
    assert 3.9 < spectrum["n1"] <= 4.0
    assert 3.9 < spectrum["n2"] <= 4.0
    assert 3.9 < spectrum["n_inf"] <= 4.0


def test_controlled_halo_has_requested_author_support() -> None:
    spec = ReferenceFrontierSpec(
        societies=1,
        groups_per_society=2,
        authors_per_group=4,
        conditions=6,
        dimensions=2,
        panels=4,
    )
    anchor = np.zeros((spec.authors, spec.conditions, spec.dimensions))
    test = np.arange(spec.authors)
    interaction, audit = build_controlled_halo_interaction(
        anchor,
        spec=spec,
        test_authors=test,
        active_test_authors=np.asarray([0, 1]),
        active_conditions=np.asarray([0, 1, 2]),
        halo_lambda=0.1,
        halo_author_support=4,
        seed=19,
    )
    assert interaction.shape == anchor.shape
    assert audit["halo_author_support"] == 4
    assert len(audit["realized_halo_author_indices"]) == 4
    assert np.isfinite(interaction).all()


def test_orbit_probability_is_bounded_and_deterministic() -> None:
    rng = np.random.default_rng(11)
    left = rng.normal(size=(8, 4, 2))
    right = left + 0.1 * rng.normal(size=left.shape)
    mask = np.ones((8, 4), dtype=bool)
    first = orbit_rejection_probability(
        left,
        right,
        mask,
        mask,
        seed=23,
        orbit_draws=29,
        detector_permutations=19,
        resamples=50,
        alpha=0.05,
    )
    second = orbit_rejection_probability(
        left,
        right,
        mask,
        mask,
        seed=23,
        orbit_draws=29,
        detector_permutations=19,
        resamples=50,
        alpha=0.05,
    )
    assert first == second
    assert 0.0 <= first["orbit_rejection_probability"] <= 1.0


def test_frozen_logistic_probability_matches_zero_logit() -> None:
    artifact = {
        "scaler_mean": [1.0, 2.0],
        "scaler_scale": [2.0, 4.0],
        "logistic_coefficient": [1.0, -1.0],
        "logistic_intercept": 0.0,
    }
    probability = frozen_logistic_probability(
        np.asarray([[1.0, 2.0]]),
        artifact,
    )
    assert np.allclose(probability, [0.5])
