"""Tests for the fresh R2E.2 confirmation analysis."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from scripts.analyze_suica_v8_conditional_heterogeneity_injection_v37h4d_r2e2 import (
    _confirmation_intervals,
    _decision,
    _read,
)
from scripts.run_suica_v8_conditional_heterogeneity_injection_v37h4d_r2e import (
    _source_lock,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = (
    ROOT
    / "configs"
    / "v8_conditional_heterogeneity_injection_v37h4d_r2e2.json"
)


def _endpoint_frame() -> pd.DataFrame:
    records = []
    for noise in ["gaussian", "heteroskedastic_t5"]:
        records.extend([
            {
                "endpoint": f"j|normal|{noise}",
                "noise_mode": noise,
                "arm": "normal",
                "metric": "direction_sensitivity_j",
                "point": 0.19,
                "baseline_variance": 0.01,
                "plus_minus_rate_gap": 0.8,
            },
            {
                "endpoint": f"j|tangent|{noise}",
                "noise_mode": noise,
                "arm": "tangent",
                "metric": "direction_sensitivity_j",
                "point": 0.0,
                "baseline_variance": 0.01,
                "plus_minus_rate_gap": 0.0,
            },
            {
                "endpoint": f"delta_v|tangent|{noise}",
                "noise_mode": noise,
                "arm": "tangent",
                "metric": "delta_variance",
                "point": 0.0,
                "baseline_variance": 0.01,
                "plus_minus_rate_gap": 0.0,
            },
        ])
    records.append({
        "endpoint": "delta_v|tangent|pooled",
        "noise_mode": "pooled",
        "arm": "tangent",
        "metric": "delta_variance",
        "point": 0.0,
        "baseline_variance": np.nan,
        "plus_minus_rate_gap": np.nan,
    })
    return pd.DataFrame(records)


def test_source_lock_and_fresh_confirmation_scope() -> None:
    config = _read(CONFIG)
    assert _source_lock(config)["pass"]
    assert config["parents_per_noise"] == 80
    assert config["normal_tau_grid"] == [0.09]
    assert config["tangent_phi_grid"] == [0.4]


def test_separate_bonferroni_families_can_confirm_normal_only() -> None:
    config = _read(CONFIG)
    endpoints = _endpoint_frame()
    rng = np.random.default_rng(11)
    bootstrap = {
        name: (
            rng.normal(0.19, 0.002, 5000)
            if "|normal|" in name
            else rng.normal(0.0, 0.0005, 5000)
        )
        for name in endpoints["endpoint"]
    }
    intervals = _confirmation_intervals(
        endpoints,
        bootstrap,
        config=config,
    )
    status, checks = _decision(
        intervals,
        config=config,
        integrity={"synthetic": True},
    )
    assert status == "V8_R2E2_CONFIRMED_NORMAL_ONLY"
    assert checks["normal_positive_control_confirmed"]
    assert checks["tangent_practical_effect_excluded"]
