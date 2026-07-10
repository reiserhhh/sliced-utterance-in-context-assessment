from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.run_suica_market_measurement_first_audit_v1 import (
    AuditConfig,
    SCORE_COLUMNS,
    build_slices,
    build_weekly_features,
    week_start,
)


def test_week_start_accepts_mixed_iso_timestamp_precision():
    values = pd.Series(["2026-03-17T16:52:52Z", "2026-06-23T10:00:00.123Z"])
    assert week_start(values).tolist() == ["2026-03-16", "2026-06-22"]


def test_slices_never_cross_collector_context_or_week():
    posts = pd.DataFrame(
        [
            {
                "user_id": "u1",
                "measurement_rind_id": "AAA",
                "collector_context_id": "AAA|topic_a",
                "symbol": "AAA",
                "query_group": "topic_a",
                "week_start": "2026-03-16",
                "collector_regime": "phase_18symbol",
                "timestamp": "2026-03-17T00:00:00Z",
                "post_id": "p1",
                "text": "alpha " * 30,
            },
            {
                "user_id": "u1",
                "measurement_rind_id": "AAA",
                "collector_context_id": "AAA|topic_b",
                "symbol": "AAA",
                "query_group": "topic_b",
                "week_start": "2026-03-16",
                "collector_regime": "phase_18symbol",
                "timestamp": "2026-03-18T00:00:00Z",
                "post_id": "p2",
                "text": "beta " * 30,
            },
        ]
    )
    slices, _ = build_slices(posts, AuditConfig(slice_tokens=128, min_slice_tokens=24))
    assert len(slices) == 2
    assert slices["collector_context_id"].nunique() == 2
    assert slices["source_post_count"].eq(1).all()


def test_state_features_require_two_strictly_prior_occasions():
    rows = []
    for index, week in enumerate(
        ["2026-03-16", "2026-03-23", "2026-03-30", "2026-04-06"], start=1
    ):
        row = {
            "collector_regime": "phase_18symbol",
            "symbol": "AAA",
            "week_start": week,
            "user_id": "u1",
            "measurement_rind_id": "AAA",
            "slice_index": 0,
        }
        row.update({column: float(index) for column in SCORE_COLUMNS})
        rows.append(row)

    weekly = build_weekly_features(pd.DataFrame(rows), AuditConfig(min_prior_occasions=2))
    state = weekly.set_index("week_start")["state__certainty_rate"]
    assert np.isnan(state.loc["2026-03-16"])
    assert np.isnan(state.loc["2026-03-23"])
    assert state.loc["2026-03-30"] == 1.5
    assert state.loc["2026-04-06"] == 2.0
    assert weekly.set_index("week_start").loc["2026-03-30", "n_prior_authors"] == 1
