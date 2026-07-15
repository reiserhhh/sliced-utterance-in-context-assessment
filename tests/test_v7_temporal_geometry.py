from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.run_suica_v7_temporal_random_contrast import _nested_partition_author_bootstrap_ci
from suica_core.v7_observations import canonicalize_comments
from suica_core.v7_temporal_geometry import (
    align_author_panels,
    alignment_auc,
    alignment_contributions,
    fit_feature_scaler,
    fit_opportunity_residualizer,
    relative_distance_spearman,
    random_source_partition,
    structural_opportunity_profiles,
    temporal_source_partition,
)


def _comments() -> pd.DataFrame:
    rows = []
    for user in ("u1", "u2"):
        for index in range(8):
            rows.append({
                "user_id": user, "split": "discovery", "source_row": len(rows), "order": index,
                "text": f"comment {index} from {user}", "token_count": 4, "condition": "forum",
            })
    return pd.DataFrame(rows)


def test_temporal_partition_is_source_disjoint_and_ordered() -> None:
    early, late, diagnostics = temporal_source_partition(_comments(), min_comments_per_half=2, max_comments_per_half=2)
    assert not set(early["source_row"]).intersection(set(late["source_row"]))
    assert diagnostics["source_overlap_count"].eq(0).all()
    for user in ("u1", "u2"):
        assert early.loc[early["user_id"].eq(user), "order"].max() < late.loc[late["user_id"].eq(user), "order"].min()


def test_random_partition_is_source_disjoint_without_temporal_order_claim() -> None:
    left, right, diagnostics = random_source_partition(_comments(), seed=7, min_comments_per_half=2, max_comments_per_half=2)
    assert not set(left["source_row"]).intersection(set(right["source_row"]))
    assert diagnostics["source_overlap_count"].eq(0).all()


def test_opportunity_profile_excludes_semantic_columns() -> None:
    profile = structural_opportunity_profiles(_comments())
    assert {"total_tokens", "url_comment_rate", "quote_comment_rate"}.issubset(profile.columns)
    assert "condition" not in profile.columns
    assert "text" not in profile.columns


def test_train_only_scaling_and_residualization_preserve_shapes() -> None:
    early = pd.DataFrame({"user_id": ["a", "b", "c"], "split": ["discovery", "discovery", "confirmation"], "f0": [0.0, 1.0, 99.0], "f1": [1.0, 2.0, 100.0]})
    late = pd.DataFrame({"user_id": ["a", "b", "c"], "split": ["discovery", "discovery", "confirmation"], "f0": [0.1, 1.1, 101.0], "f1": [1.1, 2.1, 102.0]})
    left, right = align_author_panels(early, late, feature_columns=["f0", "f1"])
    scaler = fit_feature_scaler(left, right, feature_columns=["f0", "f1"], train_user_ids={"a", "b"})
    assert np.allclose(scaler.mean, [[0.55, 1.55]])
    opportunity = np.asarray([[0.0], [1.0], [2.0]])
    residualizer = fit_opportunity_residualizer(
        scaler.transform(left[["f0", "f1"]].to_numpy(float)), scaler.transform(right[["f0", "f1"]].to_numpy(float)),
        opportunity, opportunity, train_mask=np.asarray([True, True, False]), alpha=1.0,
    )
    residual = residualizer.residualize(scaler.transform(left[["f0", "f1"]].to_numpy(float)), opportunity)
    assert residual.shape == (3, 2)


def test_geometry_metrics_separate_matching_from_permutation() -> None:
    left = np.asarray([[0.0, 0.0], [2.0, 0.0], [4.0, 0.0], [6.0, 0.0]])
    right = left + 0.01
    assert alignment_auc(left, right) > 0.9
    assert relative_distance_spearman(left, right) > 0.9
    assert alignment_auc(left, right, pairing=np.asarray([3, 2, 1, 0])) < 0.6
    assert alignment_contributions(left, right).shape == (4,)


def test_canonicalization_marks_missing_time_provenance() -> None:
    raw = pd.DataFrame({"author": ["a", "a"], "body": ["one two three four", "five six seven eight"]})
    canonical = canonicalize_comments(raw, user_col="author", text_col="body", order_col=None, min_tokens=1)
    assert not canonical["order_observed"].any()


def test_nested_partition_author_interval_requires_partition_uncertainty() -> None:
    deltas = np.asarray([[0.1, 0.2, 0.3], [0.0, 0.2, 0.4], [0.2, 0.3, 0.1]])
    low, high = _nested_partition_author_bootstrap_ci(deltas, seed=9, iterations=99)
    assert np.isfinite(low)
    assert np.isfinite(high)
    assert low <= deltas.mean() <= high
