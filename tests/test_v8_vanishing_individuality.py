"""Tests for the V8 vanishing-individuality hierarchy experiment."""
from __future__ import annotations

import numpy as np

from suica_core.v8_vanishing_individuality import (
    VanishingIndividualitySpec,
    pairing_auc_metrics,
    simulate_hierarchical_c2_world,
    stable_residual_covariance,
)


def test_group_only_contains_no_planted_individual_response() -> None:
    spec = VanishingIndividualitySpec(
        discovery_authors=12,
        calibration_authors=8,
        confirmation_authors=16,
        extra_repeats=16,
    )
    world = simulate_hierarchical_c2_world(
        seed=7,
        world="group_only",
        epsilon=0.0,
        group_amplitude=0.75,
        spec=spec,
    )
    assert np.allclose(world["truth"]["individual_response"], 0.0)
    labels = world["truth"]["group_labels"]
    for split in ("discovery", "calibration", "confirmation"):
        selected = labels[world["data"]["splits"] == split]
        assert np.ptp(
            np.unique(selected, return_counts=True)[1]
        ) == 0


def test_pairing_metrics_distinguish_group_from_author_identity() -> None:
    rng = np.random.default_rng(11)
    labels = np.repeat(np.arange(4), 20)
    group = rng.normal(size=(4, 12))
    left = group[labels] + rng.normal(scale=0.05, size=(80, 12))
    right = group[labels] + rng.normal(scale=0.05, size=(80, 12))
    metrics = pairing_auc_metrics(left, right, labels)
    assert metrics["author_all_auc"] > 0.75
    assert metrics["group_auc"] > 0.95
    assert 0.45 <= metrics["author_within_group_auc"] <= 0.55


def test_stable_residual_covariance_scales_quadratically() -> None:
    rng = np.random.default_rng(13)
    labels = np.repeat(np.arange(4), 40)
    stable = rng.normal(size=(160, 8))
    stable -= np.vstack([
        stable[labels == group].mean(axis=0)
        for group in labels
    ])
    noise_left = rng.normal(scale=0.1, size=stable.shape)
    noise_right = rng.normal(scale=0.1, size=stable.shape)
    energies = []
    for epsilon in (0.25, 0.5, 1.0):
        covariance = stable_residual_covariance(
            epsilon * stable + noise_left,
            epsilon * stable + noise_right,
            labels,
        )
        energies.append(float(np.trace(covariance)))
    slope = np.polyfit(
        np.log([0.25, 0.5, 1.0]),
        np.log(energies),
        deg=1,
    )[0]
    assert 1.8 <= slope <= 2.2
