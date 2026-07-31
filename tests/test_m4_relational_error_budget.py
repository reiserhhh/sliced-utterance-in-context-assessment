"""Tests for M4-C.3.1 relational error coordinates."""
from __future__ import annotations

import numpy as np

from suica_core.m4_relational_error_budget import (
    relational_invariance_error,
    relational_mobius_budget,
    spearman_loss,
    spearman_loss_identity_error,
)


def _loops(seed: int = 1001) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    baseline = rng.normal(size=(12, 6, 6))
    creation = rng.normal(scale=0.08, size=baseline.shape)
    response = rng.normal(scale=0.05, size=baseline.shape)
    choice = rng.normal(scale=0.03, size=baseline.shape)
    interaction = rng.normal(scale=0.01, size=baseline.shape)
    return {
        "OOO": baseline,
        "DOO": baseline + creation,
        "ODO": baseline + response,
        "OOD": baseline + choice,
        "DDO": baseline + creation + response + interaction,
        "DOD": baseline + creation + choice,
        "ODD": baseline + response + choice,
        "DDD": (
            baseline
            + creation
            + response
            + choice
            + interaction
        ),
    }


def test_spearman_loss_has_exact_midranks_representation() -> None:
    rng = np.random.default_rng(1002)
    first = rng.normal(size=120)
    second = first + rng.normal(scale=0.2, size=120)
    assert spearman_loss(first, second) > 0.0
    assert spearman_loss_identity_error(first, second) < 1e-12


def test_mobius_budget_reconstructs_complete_distance_change() -> None:
    result = relational_mobius_budget(_loops())
    assert result["mobius_reconstruction_error"] < 1e-12
    assert result["spearman_identity_error"] < 1e-12
    assert result["shapley_efficiency_error"] < 1e-12


def test_relation_coordinates_ignore_shared_similarity_transform() -> None:
    values = _loops(seed=1003)["DDD"]
    assert relational_invariance_error(values, seed=11003) < 1e-12
