"""Protocol tests for the fresh R2D conditional-heterogeneity Gate-0."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.run_suica_v8_conditional_heterogeneity_gate0_v37h4d_r2d import (
    _base_summary,
    _cell_definitions,
    _formal_status,
    _read,
    _source_lock,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = (
    ROOT / "configs/v8_conditional_heterogeneity_gate0_v37h4d_r2d.json"
)


def test_registered_design_has_eight_cells_and_locked_sources() -> None:
    config = _read(CONFIG)
    cells = _cell_definitions(config)
    assert len(cells) == 8
    assert {row["noise_mode"] for row in cells} == {
        "gaussian",
        "heteroskedastic_t5",
    }
    assert _source_lock(config)["pass"]


def test_base_summary_uses_other_bases_for_cell_comparator() -> None:
    rows = []
    for base, outcome in {
        "a": [1, 1, 0, 0],
        "b": [0, 0, 1, 1],
    }.items():
        for replicate, detected in enumerate(outcome):
            rows.append({
                "base_id": base,
                "noise_mode": "gaussian",
                "halo_lambda": 0.0,
                "halo_author_support": 4,
                "support_label": "core_only",
                "outcome_replicate": replicate,
                "crc_or_hc_detected": detected,
            })
    summary = _base_summary(
        pd.DataFrame(rows),
        outcome_replicates=4,
    ).set_index("base_id")
    assert summary.loc["a", "candidate_probability"] == 2.5 / 3.0
    assert summary.loc["b", "candidate_probability"] == 0.5 / 3.0
    assert summary.loc["a", "cell_probability"] == 0.5 / 3.0
    assert summary.loc["b", "cell_probability"] == 2.5 / 3.0


def test_formal_status_does_not_stop_only_for_weak_jeffreys_gain() -> None:
    config = _read(CONFIG)
    variance = pd.DataFrame({
        "simultaneous_lower_95": [0.01, 0.01],
    })
    status, checks = _formal_status(
        integrity={"protocol": True},
        variance=variance,
        pooled_variance={
            "mean": 0.01,
            "lower_95": 0.006,
            "upper_95": 0.02,
        },
        gains={
            "log_loss_gain": {
                "mean": 0.0,
                "lower_95": -0.01,
                "upper_95": 0.01,
            },
            "brier_gain": {
                "mean": 0.0,
                "lower_95": -0.01,
                "upper_95": 0.01,
            },
        },
        noise_direction={
            "gaussian": {"log_loss_gain": 0.0, "brier_gain": 0.0},
            "heteroskedastic_t5": {
                "log_loss_gain": 0.0,
                "brier_gain": 0.0,
            },
        },
        gates=config["gates"],
    )
    assert status == (
        "V8_R2D_GATE0_INCONCLUSIVE_INCREASE_REPLICATES_ONLY"
    )
    assert not checks["stop_pooled_variance_absent"]


def test_formal_status_stops_only_for_small_variance_upper() -> None:
    config = _read(CONFIG)
    status, checks = _formal_status(
        integrity={"protocol": True},
        variance=pd.DataFrame({
            "simultaneous_lower_95": [-0.01, -0.01],
        }),
        pooled_variance={
            "mean": 0.0,
            "lower_95": -0.005,
            "upper_95": 0.004,
        },
        gains={
            "log_loss_gain": {
                "mean": -0.1,
                "lower_95": -0.2,
                "upper_95": 0.0,
            },
            "brier_gain": {
                "mean": -0.01,
                "lower_95": -0.02,
                "upper_95": 0.0,
            },
        },
        noise_direction={
            "gaussian": {"log_loss_gain": -0.1, "brier_gain": -0.01},
            "heteroskedastic_t5": {
                "log_loss_gain": -0.1,
                "brier_gain": -0.01,
            },
        },
        gates=config["gates"],
    )
    assert status == "V8_R2D_GATE0_STOP_NO_EXPLOITABLE_CONDITIONAL_TARGET"
    assert checks["stop_pooled_variance_absent"]
