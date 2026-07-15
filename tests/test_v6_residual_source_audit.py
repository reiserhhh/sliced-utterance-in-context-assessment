from __future__ import annotations

import numpy as np

from scripts.run_suica_v6_residual_source_audit import (
    auc_from_stranger_distances,
    matched_stranger_distances,
)


def test_matched_strangers_prefer_same_condition_profiles() -> None:
    rng = np.random.default_rng(1)
    early = rng.normal(size=(30, 3))
    late = early + rng.normal(scale=0.1, size=(30, 3))
    meta = np.column_stack([np.arange(30) % 3, np.arange(30) % 5])
    sets = [{f"c{i % 3}", f"d{i % 2}"} for i in range(30)]
    _, summary = matched_stranger_distances(
        early, late, meta, meta, sets, sets, condition_weight=2.0, seed=2,
    )
    assert summary["matched_condition_jaccard"] > 0.5
    assert summary["candidate_pool_max"] == 25


def test_condition_caliper_reports_partial_coverage_without_fallback() -> None:
    rng = np.random.default_rng(7)
    early = rng.normal(size=(4, 2))
    late = early + rng.normal(scale=0.1, size=(4, 2))
    meta = np.zeros((4, 1))
    early_sets = [{"a"}, {"b"}, {"c"}, {"d"}]
    late_sets = [{"a"}, {"a"}, {"y"}, {"z"}]
    strangers, summary = matched_stranger_distances(
        early, late, meta, meta, early_sets, late_sets, condition_weight=1.0,
        seed=8, minimum_condition_jaccard=0.5,
    )
    assert summary["minimum_condition_jaccard"] == 0.5
    assert 0 < summary["condition_caliper_coverage"] < 1
    assert np.isnan(strangers).any()


def test_matched_auc_retains_planted_author_signal() -> None:
    rng = np.random.default_rng(3)
    author = rng.normal(size=(100, 5))
    early = author + rng.normal(scale=0.15, size=author.shape)
    late = author + rng.normal(scale=0.15, size=author.shape)
    meta = rng.normal(size=(100, 2))
    sets = [{f"c{i % 5}"} for i in range(100)]
    stranger, _ = matched_stranger_distances(
        early, late, meta, meta, sets, sets, condition_weight=1.0, seed=4,
    )
    result = auc_from_stranger_distances(np.linalg.norm(early - late, axis=1), stranger, seed=5)
    assert result["matched_auc"] > 0.9
    assert result["matched_auc_ci_lo"] > 0.85
