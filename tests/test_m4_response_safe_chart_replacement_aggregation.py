"""Tests for strict M4-C.3.5-R2 shard aggregation."""
from __future__ import annotations

import pandas as pd
import pytest

from scripts.aggregate_suica_m4_response_safe_chart_replacement import (
    _validate,
)
from scripts.run_suica_m4_response_safe_chart_replacement import ARM_NAMES


def _config() -> dict:
    return {
        "repetitions": 2,
        "main_worlds": ["main_a", "main_b"],
        "null_worlds": ["null_a"],
        "null_repeats": {"null_a": 1},
    }


def _frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    config = _config()
    metrics = pd.DataFrame([
        {
            "repetition": repetition,
            "world": world,
            "world_type": world_type,
            "view": view,
            "arm": arm,
        }
        for repetition in range(config["repetitions"])
        for world_type, names in (
            ("main", config["main_worlds"]),
            ("null", ["null_a__draw_00"]),
        )
        for world in names
        for view in ("train", "test")
        for arm in ARM_NAMES
    ])
    controls = pd.DataFrame([
        {
            "repetition": repetition,
            "world": world,
            "control": control,
        }
        for repetition in range(config["repetitions"])
        for world, control in (
            ("main_a", "author_permutation"),
            ("main_a", "source_shuffle"),
            ("main_a", "cka_permutation"),
            ("main_b", "author_permutation"),
            ("main_b", "source_shuffle"),
            ("main_b", "cka_permutation"),
            ("main_a", "basis_contract"),
            ("main_b", "basis_contract"),
            ("null_a__draw_00", "basis_contract"),
            ("main_a", "block_gauge"),
            ("main_a", "common_shift"),
            ("evaluation_support_shift", "support_shift"),
            ("condition_alias_ecology", "latent_alias"),
        )
    ])
    return metrics, controls


def test_validate_accepts_complete_nonoverlapping_shards() -> None:
    metrics, controls = _frames()
    _validate(metrics, controls, config=_config())


def test_validate_rejects_duplicate_metric_cell() -> None:
    metrics, controls = _frames()
    duplicated = pd.concat([metrics, metrics.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        _validate(duplicated, controls, config=_config())
