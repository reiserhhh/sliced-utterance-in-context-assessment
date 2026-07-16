from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.run_suica_v7_multiview_projection import (
    _admissible_rank_max,
    _bootstrap_alignment,
    _selection_table,
)
from suica_core.v7_multiview import (
    effective_rank,
    evaluate_cross_view,
    fit_block_scalers,
    fit_consensus_model,
    fit_direct_predictors,
    linear_cka,
    predict_target_from_source,
)


def _shared_blocks(seed: int = 8):
    rng = np.random.default_rng(seed)
    n_authors = 90
    shared = rng.normal(size=(n_authors, 2))
    blocks = {}
    for view, loading in {
        "native": rng.normal(size=(2, 8)),
        "fixed": rng.normal(size=(2, 8)),
        "sentence": rng.normal(size=(2, 8)),
    }.items():
        private = rng.normal(scale=0.18, size=(n_authors, 8))
        blocks[view] = shared @ loading + private
    return blocks


def test_consensus_projection_recovers_cross_view_structure_above_permuted_null() -> None:
    blocks = _shared_blocks()
    views = tuple(blocks)
    train = {view: values[:60] for view, values in blocks.items()}
    confirmation = {view: values[60:] for view, values in blocks.items()}
    model = fit_consensus_model(train, view_names=views, rank=2, ridge_alpha=1.0)
    direct = fit_direct_predictors(train, view_names=views, ridge_alpha=1.0)
    permuted = fit_direct_predictors(train, view_names=views, ridge_alpha=1.0, permutation_seed=7)
    result = evaluate_cross_view(confirmation, model=model, direct_models=direct, permuted_models=permuted)
    assert result["direct_global_r2"].mean() > result["permuted_direct_global_r2"].mean() + 0.25
    assert result["consensus_global_r2"].mean() > result["permuted_direct_global_r2"].mean() + 0.15


def test_linear_cka_and_effective_rank_behave_on_shared_vs_permuted_blocks() -> None:
    blocks = _shared_blocks(seed=11)
    rng = np.random.default_rng(12)
    matched = linear_cka(blocks["native"], blocks["fixed"])
    permuted = linear_cka(blocks["native"], blocks["fixed"][rng.permutation(len(blocks["fixed"]))])
    assert matched > permuted
    assert effective_rank(blocks["native"]) > 1.0


def test_rank_one_consensus_prediction_retains_matrix_shape() -> None:
    blocks = _shared_blocks(seed=19)
    train = {view: values[:60] for view, values in blocks.items()}
    model = fit_consensus_model(train, view_names=tuple(train), rank=1, ridge_alpha=1.0)
    predicted = predict_target_from_source(model, "native", "fixed", train["native"][:5])
    assert predicted.shape == (5, train["fixed"].shape[1])


def test_pure_view_private_noise_creates_positive_components_in_finite_samples() -> None:
    """The cross-view Gram suppresses but does not eliminate finite-sample noise.

    This pins the docstring correction: fully independent 30x6 blocks still
    produce large positive cross-view eigenvalues and substantial in-sample
    shared_variance_ratio at rank 10, so calibrated selection and
    broken-correspondence baselines are the actual guards.
    """
    rng = np.random.default_rng(41)
    views = ("a", "b", "c")
    blocks = {view: rng.normal(size=(30, 6)) for view in views}
    model = fit_consensus_model(blocks, view_names=views, rank=10, ridge_alpha=1.0)
    assert float(model.eigenvalues[0]) > 0.0
    assert float(np.mean(list(model.shared_variance_ratio.values()))) > 0.2
    doc = fit_consensus_model.__doc__ or ""
    assert "cannot create a component" not in doc
    assert "does" in doc and "not" in doc and "eliminate" in doc and "finite-sample" in doc


def test_permuted_baseline_is_documented_as_a_single_null_draw() -> None:
    predictors_doc = fit_direct_predictors.__doc__ or ""
    assert "single draw" in predictors_doc
    assert "not a null distribution" in predictors_doc
    evaluate_doc = evaluate_cross_view.__doc__ or ""
    assert "single permutation draw" in evaluate_doc


def _scaler_frames(missing_in_fixed: bool) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(43)
    users = [f"u{index}" for index in range(6)]
    frames = {}
    for view in ("native", "fixed"):
        ids = users[:-1] if (view == "fixed" and missing_in_fixed) else users
        frames[view] = pd.DataFrame({
            "user_id": ids,
            "mean::svd_000": rng.normal(size=len(ids)),
            "mean::svd_001": rng.normal(size=len(ids)),
        })
    return frames


def test_fit_block_scalers_raises_on_missing_author_and_names_it() -> None:
    frames = _scaler_frames(missing_in_fixed=True)
    with pytest.raises(ValueError, match=r"fixed.*u5"):
        fit_block_scalers(
            frames,
            view_names=("native", "fixed"),
            feature_names=["mean::svd_000", "mean::svd_001"],
            discovery_user_ids=[f"u{index}" for index in range(6)],
        )
    # Explicit opt-in restores the legacy mean-imputing behavior.
    scalers = fit_block_scalers(
        frames,
        view_names=("native", "fixed"),
        feature_names=["mean::svd_000", "mean::svd_001"],
        discovery_user_ids=[f"u{index}" for index in range(6)],
        allow_missing=True,
    )
    assert np.isfinite(scalers["fixed"].center).all()


def test_fit_block_scalers_passes_when_all_authors_present() -> None:
    frames = _scaler_frames(missing_in_fixed=False)
    scalers = fit_block_scalers(
        frames,
        view_names=("native", "fixed"),
        feature_names=["mean::svd_000", "mean::svd_001"],
        discovery_user_ids=[f"u{index}" for index in range(6)],
    )
    assert set(scalers) == {"native", "fixed"}


def test_full_admissible_search_uses_one_se_selection_and_bootstrap_alignment() -> None:
    blocks = _shared_blocks(seed=29)
    views = tuple(blocks)
    discovery = {view: values[:60] for view, values in blocks.items()}
    calibration = {view: values[60:78] for view, values in blocks.items()}
    rank_max = _admissible_rank_max(discovery)
    assert rank_max >= 2
    selection, selected = _selection_table(
        discovery,
        calibration,
        view_names=views,
        ranks=list(range(0, min(rank_max, 4) + 1)),
        alphas=[0.1, 1.0],
        bootstrap_iterations=9,
        seed=5,
    )
    assert selection["selected_by_one_se"].sum() == 1
    assert bool(selected["within_one_se"])
    detail, summary = _bootstrap_alignment(
        discovery,
        view_names=views,
        rank=int(selected["shared_rank"]),
        ridge_alpha=float(selected["ridge_alpha"]),
        iterations=9,
        seed=7,
    )
    if int(selected["shared_rank"]) == 0:
        assert detail.empty
    else:
        assert len(detail) == 9 * len(views)
        assert set(summary["axis_status"]).issubset({
            "ANONYMOUS_AXES_ALIGNMENT_CANDIDATE",
            "FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY",
        })
