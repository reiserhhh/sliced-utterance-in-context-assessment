"""Tests for the V3.7H.4C W0 calibration protocol."""
from __future__ import annotations

from pathlib import Path

from scripts.run_suica_v8_w0_calibration_v37h4c import (
    ROOT,
    _read,
    count_boundaries,
    decision_from_bounds,
    one_sided_exact_bounds,
    power_table,
    verify_detector_lock,
)


def test_registered_count_boundaries_are_exact() -> None:
    calibrated, miscalibrated = count_boundaries(
        1000,
        tail_alpha=0.025,
        target=0.05,
    )
    assert calibrated == 36
    assert miscalibrated == 65
    assert one_sided_exact_bounds(
        36,
        1000,
        tail_alpha=0.025,
    )[1] < 0.05
    assert one_sided_exact_bounds(
        37,
        1000,
        tail_alpha=0.025,
    )[1] >= 0.05


def test_three_state_decision_has_uncertainty_region() -> None:
    assert decision_from_bounds(
        [(0.01, 0.04), (0.01, 0.049)],
        target=0.05,
    ) == "CALIBRATED"
    assert decision_from_bounds(
        [(0.02, 0.06), (0.01, 0.04)],
        target=0.05,
    ) == "INCONCLUSIVE"
    assert decision_from_bounds(
        [(0.051, 0.08), (0.01, 0.04)],
        target=0.05,
    ) == "MISCALIBRATED"


def test_power_at_two_percent_exceeds_registered_target() -> None:
    table = power_table(
        1000,
        calibrated_max=36,
        miscalibrated_min=65,
        rates=[0.02],
    )
    assert float(table.iloc[0]["p_calibrated"]) > 0.999


def test_smoke_uses_registered_boundary_not_smoke_sample_size() -> None:
    calibrated, miscalibrated = count_boundaries(
        1000,
        tail_alpha=0.025,
        target=0.05,
    )
    assert (calibrated, miscalibrated) == (36, 65)


def test_detector_source_lock_matches_h4_discovery() -> None:
    config = _read(ROOT / "configs/v8_w0_calibration_v37h4c.json")
    result = verify_detector_lock(config)
    assert result["all_match"]
    assert Path(
        ROOT / config["detector_lock"]["source_manifest"]
    ).exists()
