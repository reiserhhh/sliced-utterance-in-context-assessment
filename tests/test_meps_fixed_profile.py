from __future__ import annotations

import numpy as np

from suica_core.meps_fixed_profile import auc_probability, paired_embedding_summary


def test_auc_probability_handles_ties() -> None:
    assert auc_probability(np.array([1.0]), np.array([1.0])) == 0.5
    assert auc_probability(np.array([2.0]), np.array([1.0, 1.5])) == 1.0


def test_paired_embedding_summary_recovers_aligned_signal() -> None:
    # Diagonal links are systematically larger than every stranger link.
    similarity = np.full((6, 6), 0.15)
    np.fill_diagonal(similarity, 0.85)
    result = paired_embedding_summary(
        similarity,
        np.array([100, 110, 120, 130, 140, 150]),
        bootstrap_draws=99,
        permutation_draws=99,
        seed=8,
    )
    assert result["same_person_auc"] == 1.0
    assert result["same_person_auc_ci_low"] > 0.99
    assert result["linkage_permutation_p"] <= 0.02
    assert result["length_matched_coverage"] > 0.0


def test_paired_embedding_summary_rejects_too_few_participants() -> None:
    with np.testing.assert_raises(ValueError):
        paired_embedding_summary(np.eye(3), np.array([10, 10, 10]), bootstrap_draws=99, permutation_draws=99)
