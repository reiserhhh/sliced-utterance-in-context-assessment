from __future__ import annotations

import numpy as np

from scripts.run_suica_v7_multiview_projection import (
    _admissible_rank_max,
    _bootstrap_alignment,
    _selection_table,
)
from suica_core.v7_multiview import (
    effective_rank,
    evaluate_cross_view,
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
