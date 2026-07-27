"""Tests for the exploratory V3.7D phase diagram."""
from __future__ import annotations

import numpy as np

from suica_core.v8_dimension_density_budget import (
    DensityWorldSpec,
    author_geometry_diagnostics,
    evaluate_density_population,
    simulate_group_free_density_world,
    subset_authors,
)
from suica_core.v8_group_free_routing_transport import (
    resample_routing_counts,
)


def test_density_world_has_no_group_labels_or_centering_contract() -> None:
    sample = simulate_group_free_density_world(
        seed=37_001,
        spec=DensityWorldSpec(
            authors=16,
            latent_rank=2,
            events_per_context_session=16,
        ),
    )
    assert "labels" not in sample
    assert sample["world"] == "truly_group_free_density"
    assert sample["probability"].shape == (16, 2, 24, 16, 4)


def test_geometry_certificate_accepts_exact_repeated_profiles() -> None:
    rng = np.random.default_rng(37_101)
    truth = rng.normal(size=(24, 6))
    result = author_geometry_diagnostics(truth, truth, truth)
    assert result["prototype_margin_fraction"] == 1.0
    assert result["cross_session_certificate_fraction"] == 1.0
    assert result["median_combined_error"] == 0.0
    assert result["median_raw_combined_error"] == 0.0


def test_geometry_certificate_rejects_collapsed_profiles() -> None:
    truth = np.column_stack([np.arange(12), np.zeros(12)])
    collapsed = np.zeros_like(truth)
    result = author_geometry_diagnostics(truth, collapsed, collapsed)
    assert result["cross_session_certificate_fraction"] == 0.0
    assert result["median_error_margin_ratio"] > 1.0


def test_density_evaluation_is_finite() -> None:
    latent = simulate_group_free_density_world(
        seed=37_201,
        spec=DensityWorldSpec(
            authors=32,
            latent_rank=4,
            events_per_context_session=32,
        ),
    )
    reference = resample_routing_counts(
        latent,
        np.random.default_rng(37_202),
    )
    observed = resample_routing_counts(
        latent,
        np.random.default_rng(37_203),
    )
    result = evaluate_density_population(
        latent=latent,
        reference_panel=reference,
        observed_panel=observed,
        primary_rank=8,
        oracle_rank=4,
        neighbor_count=8,
        training_indices=np.arange(16),
        evaluation_indices=np.arange(16, 32),
    )
    assert result["numeric_output"]
    assert -1.0 <= result["truth_correlation"] <= 1.0
    assert 0.0 <= result["local_neighbor_auc"] <= 1.0
    assert result["training_authors"] == 16
    assert result["evaluation_authors"] == 16


def test_author_subset_preserves_shared_contexts() -> None:
    sample = simulate_group_free_density_world(
        seed=37_301,
        spec=DensityWorldSpec(
            authors=20,
            latent_rank=2,
            events_per_context_session=16,
        ),
    )
    subset = subset_authors(sample, np.arange(5, 12))
    assert subset["counts"].shape[0] == 7
    assert subset["probability"].shape[0] == 7
    assert subset["contexts"] is sample["contexts"]
