from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.run_suica_v7_multiview_method_benchmark import (
    _cohort_commitment,
    _paired_method_differences,
    _rank_boundary_status,
)
from suica_core.v7_multiview_baselines import evaluate_shared_model, fit_concat_pca, fit_rgcca_sumcor


def _blocks(seed: int = 7) -> tuple[dict[str, np.ndarray], tuple[str, ...]]:
    rng = np.random.default_rng(seed)
    shared = rng.normal(size=(80, 3))
    names = ("a", "b", "c")
    blocks = {
        name: shared @ rng.normal(size=(3, 8)) + rng.normal(scale=0.15, size=(80, 8))
        for name in names
    }
    return blocks, names


def test_concat_pca_predicts_cross_view_signal() -> None:
    blocks, names = _blocks()
    model = fit_concat_pca(blocks, view_names=names, rank=3, ridge_alpha=1.0)
    result = evaluate_shared_model(model, blocks)
    assert len(result) == 6
    assert np.mean([float(row["global_r2"]) for row in result]) > 0.1


def test_rgcca_sumcor_predicts_cross_view_signal() -> None:
    blocks, names = _blocks()
    model = fit_rgcca_sumcor(blocks, view_names=names, rank=3, ridge_alpha=0.1)
    result = evaluate_shared_model(model, blocks)
    assert model.shared_scores.shape == (80, 3)
    assert np.mean([float(row["global_r2"]) for row in result]) > 0.1


def test_rank_one_shared_coordinate_stays_two_dimensional_for_decoding() -> None:
    blocks, names = _blocks()
    model = fit_concat_pca(blocks, view_names=names, rank=1, ridge_alpha=1.0)
    result = evaluate_shared_model(model, blocks)
    assert len(result) == 6
    assert np.isfinite([float(row["global_r2"]) for row in result]).all()


def test_rank_boundary_is_reported_without_turning_rank_into_a_dimension() -> None:
    summary = pd.DataFrame({"selected_rank": [4, 8]})
    assert _rank_boundary_status(summary, rank_grid=[1, 2, 4, 8]) == "RANK_UNRESOLVED_AT_REGISTERED_GRID_BOUNDARY"
    assert _rank_boundary_status(pd.DataFrame({"selected_rank": [4]}), rank_grid=[1, 2, 4, 8]) == "RANK_RESOLVED_WITHIN_REGISTERED_GRID"


def test_cohort_commitment_is_identifier_free_and_order_invariant() -> None:
    recipe = {"cohort_id": "test", "seed": 1, "min_comments_per_user": 2, "max_users": 3}
    left = _cohort_commitment(pd.Series(["u2", "u1", "u3"]), recipe=recipe)
    right = _cohort_commitment(pd.Series(["u3", "u2", "u1"]), recipe=recipe)
    assert left["membership_sha256"] == right["membership_sha256"]
    assert left["raw_identifiers_persisted"] is False


def test_paired_method_differences_produces_frozen_model_interval() -> None:
    blocks, names = _blocks(9)
    concat = fit_concat_pca(blocks, view_names=names, rank=3, ridge_alpha=1.0)
    rgcca = fit_rgcca_sumcor(blocks, view_names=names, rank=3, ridge_alpha=0.1)
    result = _paired_method_differences(
        {"CONCAT_PCA": concat, "RGCCA_SUMCOR": rgcca},
        blocks,
        views=names,
        iterations=49,
        seed=12,
        material_threshold=0.02,
    )
    assert len(result) == 1
    assert np.isfinite(result["mean_r2_difference_first_minus_second"]).all()
    assert result["ci_low"].iloc[0] <= result["ci_high"].iloc[0]
