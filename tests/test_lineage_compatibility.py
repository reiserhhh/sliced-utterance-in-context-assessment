from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.lineage_compatibility import (
    evenly_spread_token_views,
    paired_correlation_delta,
    paired_reliability_change,
    reference_condition_residuals,
    span_spread_disjoint_views,
)


def test_span_spread_views_are_disjoint_and_cover_both_timeline_ends() -> None:
    events = pd.DataFrame({
        "created_utc": np.arange(30, dtype=float),
        "_source_index": np.arange(30),
        "body": [f"text-{index}" for index in range(30)],
    })
    views = span_spread_disjoint_views(events, block_size=3, blocks_per_view=4)
    assert views.groupby("technical_view").size().to_dict() == {"left": 12, "right": 12}
    assert views["body"].nunique() == len(views)
    assert views.groupby(["technical_view", "technical_block"]).size().eq(3).all()
    assert views.groupby("technical_view")["created_utc"].min().max() <= 4
    assert views.groupby("technical_view")["created_utc"].max().min() >= 25


def test_paired_correlation_delta_recovers_a_positive_fixed_arm() -> None:
    rng = np.random.default_rng(1)
    signal = rng.normal(size=80)
    outcome = paired_correlation_delta(
        signal,
        signal + rng.normal(scale=0.05, size=80),
        signal,
        rng.normal(size=80),
        bootstrap_iterations=200,
        seed=2,
    )
    assert outcome["delta"] > 0.5
    assert outcome["ci_lo"] > 0.0


def test_evenly_spread_token_views_are_token_disjoint_and_cover_endpoints() -> None:
    text = " ".join(f"t{index}" for index in range(80))
    views = evenly_spread_token_views(text, slice_tokens=4, slices_per_view=4)
    assert len(views) == 8
    spans = {(int(row["token_start"]), int(row["token_end"])) for row in views}
    assert len(spans) == 8
    assert {str(row["technical_view"]) for row in views} == {"left", "right"}
    assert min(int(row["token_start"]) for row in views) == 0
    assert max(int(row["token_end"]) for row in views) == 80


def test_paired_reliability_change_keeps_direction_explicit() -> None:
    rng = np.random.default_rng(3)
    signal = rng.normal(size=100)
    outcome = paired_reliability_change(
        signal,
        signal + rng.normal(scale=2.0, size=100),
        signal,
        signal + rng.normal(scale=0.05, size=100),
        bootstrap_iterations=200,
        seed=4,
    )
    assert outcome["second_minus_first"] > 0.3
    assert outcome["ci_lo"] > 0.0


def test_reference_condition_residuals_fit_only_reference_rows() -> None:
    values = np.array([[2.0], [4.0], [10.0], [12.0], [100.0]])
    residual, metadata = reference_condition_residuals(
        values,
        ["a", "a", "b", "b", "new"],
        [True, True, True, True, False],
        min_reference_events=2,
    )
    assert np.allclose(residual[:4, 0], [-1.0, 1.0, -1.0, 1.0])
    assert np.isclose(residual[4, 0], 93.0)  # unseen condition uses reference grand mean=7
    assert metadata["reference_conditions_supported"] == 2
    assert metadata["rows_using_global_fallback"] == 1
