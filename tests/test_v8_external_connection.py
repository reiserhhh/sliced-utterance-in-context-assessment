from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v8_external_connection import (
    benjamini_hochberg,
    canonical_scale_residual,
    matrix_alignment,
    relation_matrix,
    run_official_cv,
    split_comment_units,
)


def test_split_comment_units_preserves_prepared_boundaries() -> None:
    text = "short\n\n" + "one " * 30 + "\n\n" + "two " * 40
    units = split_comment_units(text, min_tokens=24, max_chars=1000)
    assert len(units) == 2
    assert units[0]["token_count"] == 30
    assert units[1]["token_count"] == 40


def test_canonical_scale_residual_removes_row_location_and_scale() -> None:
    values = np.array([[1.0, 2.0, 4.0], [11.0, 13.0, 17.0]])
    first = canonical_scale_residual(values)
    transformed = canonical_scale_residual(values * 7.0 + 40.0)
    np.testing.assert_allclose(first, transformed)
    np.testing.assert_allclose(first.mean(axis=1), 0.0, atol=1e-12)
    np.testing.assert_allclose(first.std(axis=1), 1.0, atol=1e-12)


def test_benjamini_hochberg_is_monotone_in_sorted_p() -> None:
    p_values = pd.Series([0.04, 0.001, 0.02, np.nan])
    adjusted = benjamini_hochberg(p_values)
    assert np.isnan(adjusted.iloc[3])
    order = p_values.dropna().sort_values().index
    ordered_q = adjusted.loc[order].to_numpy(float)
    assert np.all(np.diff(ordered_q) >= -1e-12)
    assert adjusted.iloc[1] <= adjusted.iloc[2] <= adjusted.iloc[0]


def test_relation_alignment_recovers_equal_matrix() -> None:
    frame = pd.DataFrame({
        "b1": [0.0, 1.0, 2.0, 3.0],
        "b2": [3.0, 2.0, 1.0, 0.0],
        "m1": [0.0, 0.0, 1.0, 1.0],
        "m2": [1.0, 0.0, 1.0, 0.0],
    })
    matrix = relation_matrix(
        frame,
        big5_columns=["b1", "b2"],
        mbti_columns=["m1", "m2"],
    )
    result = matrix_alignment(matrix, matrix)
    assert np.isclose(result["element_r"], 1.0)
    assert np.isclose(result["frobenius_distance"], 0.0)


def test_official_cv_produces_one_prediction_per_row() -> None:
    rng = np.random.default_rng(42)
    rows = []
    for fold in range(5):
        for index in range(20):
            x1 = rng.normal()
            x2 = rng.normal()
            rows.append({
                "pseudonymous_id": f"{fold}-{index}",
                "official_fold": fold,
                "x1": x1,
                "x2": x2,
                "target": 0.8 * x1 - 0.3 * x2 + rng.normal(scale=0.1),
            })
    frame = pd.DataFrame(rows)
    result = run_official_cv(
        frame,
        columns=["x1", "x2"],
        target="target",
        fold_column="official_fold",
        task="continuous",
        view="test",
        cohort="synthetic",
        ridge_alphas=[0.01, 0.1, 1.0],
        logistic_c=[1.0],
    )
    assert len(result.predictions) == len(frame)
    assert result.predictions["prediction"].notna().all()
    assert set(result.folds["test_fold"]) == set(range(5))
    assert result.summary["pearson_r"] > 0.9


def test_binary_official_cv_handles_single_class_validation_fold() -> None:
    rng = np.random.default_rng(7)
    rows = []
    for fold in range(5):
        for index in range(20):
            feature = rng.normal()
            target = 0 if fold == 1 else int(feature > 0)
            rows.append({
                "pseudonymous_id": f"{fold}-{index}",
                "official_fold": fold,
                "x": feature,
                "target": target,
            })
    result = run_official_cv(
        pd.DataFrame(rows),
        columns=["x"],
        target="target",
        fold_column="official_fold",
        task="binary",
        view="test",
        cohort="synthetic",
        ridge_alphas=[1.0],
        logistic_c=[0.1, 1.0],
    )
    assert result.predictions["prediction"].notna().all()
    assert np.isfinite(result.summary["roc_auc"])
