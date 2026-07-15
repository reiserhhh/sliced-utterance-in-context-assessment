from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.run_suica_v6_opportunity_profile_audit import _random_match_baseline
from suica_core.opportunity_profiles import (
    SURFACE_COLUMNS,
    build_opportunity_profiles,
    paired_profile_matrices,
    profile_columns,
)


def _units() -> pd.DataFrame:
    rows = []
    for user, offset in (("u1", 0.0), ("u2", 10.0)):
        for half, half_offset in (("early", 0.0), ("late", 100.0)):
            for index in range(3):
                row = {
                    "user_id": user,
                    "half": half,
                    "condition": f"c{index % 2}",
                    "created_utc": offset + half_offset + index * 3600.0,
                    "run_len": 4 if index < 2 else 1,
                }
                row.update({column: float(index + (column == "log_tokens")) for column in SURFACE_COLUMNS})
                rows.append(row)
    return pd.DataFrame(rows)


def test_profile_layers_are_nested_and_fixed() -> None:
    assert len(profile_columns("coarse")) < len(profile_columns("surface_mean"))
    assert len(profile_columns("surface_mean")) < len(profile_columns("surface_distribution"))
    assert len(profile_columns("surface_distribution")) < len(profile_columns("surface_time"))


def test_profiles_keep_only_aggregate_opportunity_coordinates() -> None:
    profiles, condition_sets = build_opportunity_profiles(_units())
    assert len(profiles) == 4
    assert set(condition_sets[("u1", "early")]) == {"c0", "c1"}
    assert not any(column in profiles for column in ("body", "text", "author", "subreddit"))
    assert np.isfinite(profiles[profile_columns("surface_time")].to_numpy(float)).all()


def test_paired_profiles_follow_requested_author_order() -> None:
    profiles, _ = build_opportunity_profiles(_units())
    early, late, columns = paired_profile_matrices(profiles, ["u2", "u1"], "surface_time")
    assert early.shape == late.shape == (2, len(columns))
    assert early[0, 0] == profiles.loc[
        (profiles["user_id"] == "u2") & (profiles["half"] == "early"), columns[0]
    ].iloc[0]


def test_random_matching_qa_excludes_self_pairs() -> None:
    early = np.array([[0.0], [1.0], [20.0]])
    late = np.array([[0.0], [1.0], [20.0]])
    baseline = _random_match_baseline(
        early,
        late,
        [{"a"}, {"b"}, {"c"}],
        np.array([True, True, True]),
        seed=3,
        n_draws=20,
    )
    assert baseline["random_numeric_opportunity_distance"] > 0.0
    assert baseline["random_condition_jaccard"] == 0.0
