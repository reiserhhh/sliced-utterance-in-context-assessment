"""Tests for the narrow H4D-R2A iid confirmation."""
from __future__ import annotations

from pathlib import Path

from scripts.run_suica_v8_minority_information_frontier_v37h4d_r2a_confirmation import (
    _definitions,
    _read,
    _source_lock,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = (
    ROOT
    / "configs"
    / "v8_minority_information_frontier_v37h4d_r2a_confirmation.json"
)


def test_confirmation_is_narrow_and_fresh() -> None:
    config = _read(CONFIG)
    definitions = _definitions(config)
    assert len(definitions) == 4
    assert sum(item["repetitions"] for item in definitions) == 4000
    signal = [
        item for item in definitions if item["scaling_arm"] != "w0"
    ]
    assert all(item["active_test_authors"] == 8 for item in signal)
    assert all(item["support_scheme"] == "fixed" for item in signal)
    assert all(item["interaction_shape"] == "iid_block" for item in signal)


def test_confirmation_source_lock_matches_discovery() -> None:
    config = _read(CONFIG)
    assert _source_lock(config)["pass"]

