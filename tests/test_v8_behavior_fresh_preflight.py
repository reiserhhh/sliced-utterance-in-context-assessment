"""Tests for behavior-v2.1 fresh-panel support checks."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "v8_behavior_fresh_preflight",
    ROOT / "scripts" / "run_suica_v8_behavior_v21_fresh_preflight.py",
)
assert SPEC is not None and SPEC.loader is not None
PREFLIGHT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREFLIGHT)


def test_thread_disjoint_halves_never_split_a_thread() -> None:
    rows = []
    for thread in range(6):
        for index in range(12):
            rows.append({
                "body": "text",
                "created_utc": float(thread * 100 + index),
                "link_id": f"thread-{thread}",
                "id": f"comment-{thread}-{index}",
                "subreddit": f"condition-{thread % 2}",
                "lang": "en",
            })
    halves = PREFLIGHT._thread_disjoint_halves(
        pd.DataFrame(rows),
        comments_per_half=24,
    )
    assert halves is not None
    left = set(halves.loc[halves["side"].eq("left"), "link_id"])
    right = set(halves.loc[halves["side"].eq("right"), "link_id"])
    assert len(halves) == 48
    assert not (left & right)


def test_time_even_selection_preserves_endpoints() -> None:
    frame = pd.DataFrame({
        "created_utc": np.arange(20, dtype=float),
        "id": [f"c-{index:02d}" for index in range(20)],
    })
    selected = PREFLIGHT._time_even_rows(frame, 5)
    assert selected["created_utc"].tolist()[0] == 0.0
    assert selected["created_utc"].tolist()[-1] == 19.0
    assert len(selected) == 5
