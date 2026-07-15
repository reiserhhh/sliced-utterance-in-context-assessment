from __future__ import annotations

import numpy as np

from suica_core.residual_geometry import (
    aligned_geometry_permutation_test,
    aligned_geometry_statistics,
    correspondence_permutation_test,
    geometry_audit,
    geometry_statistics,
    intrinsic_dimension,
    linear_cka_from_grams,
    centered_gram,
    geometry_status,
)


def test_linear_cka_is_invariant_to_rotation_and_isotropic_scale() -> None:
    rng = np.random.default_rng(5)
    values = rng.normal(size=(80, 5))
    rotation, _ = np.linalg.qr(rng.normal(size=(5, 5)))
    transformed = 7.0 * values @ rotation
    score = linear_cka_from_grams(centered_gram(values), centered_gram(transformed))
    assert score > 0.999999


def test_geometry_audit_detects_replicated_relational_structure() -> None:
    rng = np.random.default_rng(6)
    latent = rng.normal(size=(120, 4))
    early = latent + rng.normal(scale=0.08, size=latent.shape)
    late = latent + rng.normal(scale=0.08, size=latent.shape)
    metrics, null = geometry_audit(
        early, late, permutation_iterations=49, subsample_iterations=12, seed=7
    )
    assert metrics["linear_cka"] > 0.9
    assert metrics["distance_spearman"] > 0.8
    assert metrics["neighbour_jaccard"] > 0.5
    assert metrics["linear_cka_permutation_p"] <= 0.04
    assert len(null) == 49


def test_permutation_breaks_independent_linkage() -> None:
    rng = np.random.default_rng(8)
    early = rng.normal(size=(100, 4))
    late = rng.normal(size=(100, 4))
    observed, _ = correspondence_permutation_test(early, late, iterations=49, seed=9)
    assert observed["linear_cka_permutation_p"] > 0.05


def test_intrinsic_dimension_is_finite_for_a_low_rank_cloud() -> None:
    rng = np.random.default_rng(10)
    latent = rng.normal(size=(150, 2))
    projection = rng.normal(size=(2, 8))
    values = latent @ projection + rng.normal(scale=1e-4, size=(150, 8))
    estimate = intrinsic_dimension(values, k=10)
    assert np.isfinite(estimate)
    assert 1.0 < estimate < 4.0


def test_geometry_statistics_exposes_global_local_and_spectral_values() -> None:
    rng = np.random.default_rng(11)
    values = rng.normal(size=(60, 3))
    metrics = geometry_statistics(values, values + rng.normal(scale=0.05, size=values.shape))
    assert set(("linear_cka", "distance_spearman", "neighbour_jaccard", "spectrum_cosine")).issubset(metrics)
    assert metrics["effective_rank_early"] > 1.0


def test_status_prefers_familywise_adjusted_p_values() -> None:
    metrics = {
        "linear_cka_permutation_p": 0.001,
        "distance_spearman_permutation_p": 0.001,
        "neighbour_jaccard_permutation_p": 0.001,
        "linear_cka_bonferroni_p": 0.08,
        "distance_spearman_bonferroni_p": 0.08,
        "neighbour_jaccard_bonferroni_p": 0.08,
    }
    assert geometry_status(metrics) == "NO_LINKAGE_GEOMETRY_DETECTED"


def test_aligned_geometry_accepts_different_coordinate_dimensions() -> None:
    """Cross-representation geometry must not require matching feature axes."""
    rng = np.random.default_rng(12)
    latent = rng.normal(size=(96, 4))
    left_rotation, _ = np.linalg.qr(rng.normal(size=(4, 4)))
    right_rotation, _ = np.linalg.qr(rng.normal(size=(4, 4)))
    left = np.column_stack([latent @ left_rotation, np.zeros((len(latent), 3))])
    right = np.column_stack([latent @ right_rotation, np.zeros((len(latent), 7))])
    summary = aligned_geometry_statistics(left, right, neighbourhood_k=8)
    observed, _ = aligned_geometry_permutation_test(
        left, right, neighbourhood_k=8, iterations=99, seed=13,
    )
    assert summary["linear_cka"] > 0.99
    assert summary["rbf_cka"] > 0.99
    assert summary["distance_spearman"] > 0.99
    assert observed["linear_cka_permutation_p"] <= 0.02
    assert observed["distance_spearman_permutation_p"] <= 0.02
