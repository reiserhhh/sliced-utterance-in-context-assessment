"""Tests for the preregistered H4D-R2B geometry-operator analysis."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts"
    / "analyze_suica_v8_geometry_information_operator_v37h4d_r2b.py"
)
SPEC = importlib.util.spec_from_file_location("v8_r2b_analysis", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
ANALYSIS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANALYSIS)


def _rows() -> pd.DataFrame:
    records = []
    families = [
        "iid_halo",
        "intrinsic_zero_sum",
        "author_concentrated",
        "condition_concentrated",
        "rank1_coherent",
        "balanced_antiphase",
        "halo_sweep",
    ]
    for base_id in range(18):
        for family_index, family in enumerate(families):
            signal = 0.2 + 0.08 * family_index + 0.01 * base_id
            records.append({
                "base_id": base_id,
                "geometry_family": family,
                "noise_mode": (
                    "heteroskedastic_t5"
                    if base_id % 2
                    else "gaussian"
                ),
                "active_test_authors": [4, 8, 16][base_id % 3],
                "halo_lambda": 0.03,
                "crc_or_hc_detected": int(
                    (base_id + family_index) % 3 != 0
                ),
                "operator_total_information": 3.0 + signal,
                "operator_neff_author": 2.0 + signal,
                "operator_neff_cell": 5.0 + signal,
                "operator_rho3": 0.3 + 0.02 * family_index,
                "operator_whitened_leakage": 0.1 + 0.01 * family_index,
                "operator_condition_coherence": -0.2 + signal,
                "operator_neff_sign": 1.5 + signal,
            })
    return pd.DataFrame(records)


def test_feature_frame_is_finite_and_excludes_geometry_labels() -> None:
    frame = ANALYSIS.build_feature_frame(_rows())
    assert "geometry_family" not in frame.columns
    assert "base_id" not in frame.columns
    assert np.isfinite(frame.to_numpy(dtype=float)).all()


def test_logo_predictions_cover_rows_without_duplicate_keys() -> None:
    rows = _rows()
    features = ANALYSIS.build_feature_frame(rows)
    predictions = ANALYSIS.logo_group_predictions(
        rows,
        features,
        scalar_columns=[
            "log_information",
            "log_information_squared",
            "log_active_authors",
            "noise_t5",
        ],
        operator_columns=[
            "log_neff_author",
            "log_neff_cell",
            "logit_rho3",
            "logit_whitened_leakage",
            "condition_coherence",
            "log_neff_sign",
        ],
        candidates=[0.1],
        outer_folds=3,
        inner_folds=2,
    )
    assert len(predictions) == len(rows)
    assert not predictions.duplicated(
        ["base_id", "geometry_family"]
    ).any()
    assert predictions["scalar_probability"].between(0.0, 1.0).all()
    assert predictions["operator_probability"].between(0.0, 1.0).all()


def test_paired_counterexample_preserves_base_pairing() -> None:
    records = []
    for noise in ["gaussian", "heteroskedastic_t5"]:
        for m in [4, 8]:
            for base_id in range(10):
                records.extend([
                    {
                        "base_id": f"{noise}-{m}-{base_id}",
                        "geometry_family": "iid_halo",
                        "noise_mode": noise,
                        "active_test_authors": m,
                        "crc_or_hc_detected": 1,
                    },
                    {
                        "base_id": f"{noise}-{m}-{base_id}",
                        "geometry_family": "intrinsic_zero_sum",
                        "noise_mode": noise,
                        "active_test_authors": m,
                        "crc_or_hc_detected": 0,
                    },
                ])
    result = ANALYSIS.paired_counterexample(
        pd.DataFrame(records),
        seed=31,
        draws=100,
    )
    assert len(result) == 4
    assert (result["pairs"] == 10).all()
    assert (result["iid_minus_intrinsic_power"] == 1.0).all()
    assert (result["difference_lower_95"] == 1.0).all()


def test_cluster_bootstrap_constant_is_exact() -> None:
    result = ANALYSIS.cluster_bootstrap_mean(
        pd.Series([0.25, 0.25, 0.25, 0.25]),
        pd.Series([0, 0, 1, 1]),
        seed=11,
        draws=100,
    )
    assert result == {
        "mean": 0.25,
        "lower_95": 0.25,
        "upper_95": 0.25,
    }
