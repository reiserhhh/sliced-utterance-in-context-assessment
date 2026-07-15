from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.joint_process import (
    alignment_permutation_test,
    author_support_summary,
    candidate_support_table,
    cohort_from_bucket,
    disjoint_block_views,
    gap_bin,
    gap_one_hot,
    metadata_events,
    pairwise_cosine_geometry_correlation,
    rank_auc,
    selection_hash_matrix,
    same_author_auc,
    selected_candidate,
    stable_bucket,
)


def _comments() -> pd.DataFrame:
    return pd.DataFrame({
        "author": ["a", "a", "a", "b", "b", "b"],
        "body": ["alpha text", "beta longer text", "gamma text", "one longer text", "two longer text", "three longer text"],
        "created_utc": [0.0, 3600.0, 9 * 86_400.0, 0.0, 2 * 86_400.0, 40 * 86_400.0],
        "subreddit": ["x", "y", "x", "z", "z", "q"],
    })


def test_metadata_events_remove_body_and_preserve_selection_order() -> None:
    events = metadata_events(_comments())
    assert "body" not in events.columns
    assert events.loc[events["user_id"].eq("a"), "selection"].tolist() == ["x", "y", "x"]
    assert events.loc[events["user_id"].eq("a"), "event_index"].tolist() == [0, 1, 2]


def test_gap_bin_and_support_gate_are_deterministic() -> None:
    assert gap_bin(np.array([0.0, 2 * 86_400.0, 45 * 86_400.0])).tolist() == [
        "within_day", "one_to_seven_days", "one_to_six_months"
    ]
    summary = author_support_summary(metadata_events(_comments()))
    private, cohorts, decision = candidate_support_table(
        summary, min_events=3, min_transitions=2, min_endpoint_authors=1, namespace="test"
    )
    assert "user_id" in private.columns
    assert set(cohorts["cohort"]).issubset({"discovery", "calibration", "confirmation"})
    assert decision["licensed_object"] == "joint_selection_expression_transition_only"
    assert cohort_from_bucket(stable_bucket("a", namespace="test")) in {"discovery", "calibration", "confirmation"}


def test_rank_auc_and_same_author_auc_detect_aligned_geometry() -> None:
    assert rank_auc(np.array([2.0]), np.array([1.0])) == 1.0
    left = np.eye(5)
    right = np.eye(5)
    assert same_author_auc(left, right) == 1.0


def test_selected_candidate_is_smallest_qualified_pair() -> None:
    frame = pd.DataFrame([
        {"min_events": 48, "min_transitions": 16, "alternative_auc_q05": .56, "null_promotion_rate": .01, "qualified": True},
        {"min_events": 24, "min_transitions": 8, "alternative_auc_q05": .50, "null_promotion_rate": .01, "qualified": False},
    ])
    assert selected_candidate(frame) == {"min_events": 48, "min_transitions": 16}


def test_disjoint_three_event_views_inflate_support_requirement() -> None:
    summary = pd.DataFrame({
        "user_id": ["a", "b", "c", "d"],
        "event_count": [48, 47, 60, 48],
        "transition_count": [47, 46, 59, 47],
        "selection_count": [2, 2, 2, 2],
        "selection_entropy": [0.5, 0.5, 0.5, 0.5],
        "largest_selection_share": [0.7, 0.7, 0.7, 0.7],
        "median_text_characters": [30.0] * 4,
        "mean_text_characters": [30.0] * 4,
        **{f"transitions::{label}": [1, 1, 1, 1] for label in (
            "within_day", "one_to_seven_days", "one_to_thirty_days",
            "one_to_six_months", "over_six_months",
        )},
    })
    table, _, decision = candidate_support_table(
        summary, min_events=24, min_transitions=8, min_endpoint_authors=1,
        namespace="test", replicate_views=2, replication_block_size=3,
    )
    assert decision["minimum_total_events_for_disjoint_views"] == 48
    assert decision["minimum_total_transitions_for_disjoint_views"] == 32
    assert int(table["eligible"].sum()) == 3


def test_disjoint_block_views_do_not_reuse_events_or_transitions() -> None:
    comments = pd.DataFrame({
        "author": ["a"] * 12,
        "body": [f"text-{index}" for index in range(12)],
        "created_utc": np.arange(12, dtype=float),
        "subreddit": ["x", "y", "z"] * 4,
    })
    views = disjoint_block_views(
        comments, min_events_per_view=6, min_transitions_per_view=2, block_size=3,
    )
    assert views.groupby("technical_view").size().to_dict() == {"left": 6, "right": 6}
    assert views["body"].nunique() == len(views)
    assert views.groupby(["technical_view", "technical_block"]).size().eq(3).all()


def test_joint_geometry_helpers_keep_signal_and_null_separate() -> None:
    encoded = selection_hash_matrix(["x", "y", "x"], dimensions=8, namespace="test")
    assert encoded.shape == (3, 8)
    assert np.allclose(encoded.sum(axis=1), 1.0)
    assert gap_one_hot([0.0, 2 * 86_400.0]).shape == (2, 5)
    left = np.array([
        [1.0, 0.0], [0.9, 0.1], [0.6, 0.4], [0.2, 0.8], [0.0, 1.0], [0.3, 0.7],
    ])
    right = left.copy()
    permutation = alignment_permutation_test(left, right, permutations=20, seed=1)
    assert permutation["observed_auc"] == 1.0
    assert permutation["permutation_p"] <= 1 / 21
    assert pairwise_cosine_geometry_correlation(left, right) == 1.0
