from __future__ import annotations

import numpy as np

from suica_core.v7_operator_atlas import (
    atlas_asymmetry,
    cycle_errors,
    evaluate_directed_atlas,
    fit_directed_maps,
)


def _blocks(seed: int = 4):
    rng = np.random.default_rng(seed)
    shared = rng.normal(size=(96, 3))
    return {
        "alpha": shared @ rng.normal(size=(3, 7)) + rng.normal(scale=0.12, size=(96, 7)),
        "beta": shared @ rng.normal(size=(3, 7)) + rng.normal(scale=0.12, size=(96, 7)),
        "gamma": shared @ rng.normal(size=(3, 7)) + rng.normal(scale=0.12, size=(96, 7)),
    }


def test_operator_atlas_edges_exceed_broken_correspondence_and_cycles_are_finite() -> None:
    blocks = _blocks()
    views = tuple(blocks)
    train = {view: values[:70] for view, values in blocks.items()}
    confirmation = {view: values[70:] for view, values in blocks.items()}
    maps = fit_directed_maps(train, view_names=views, ridge_alpha=1.0)
    permuted = fit_directed_maps(train, view_names=views, ridge_alpha=1.0, permutation_seed=13)
    edges = evaluate_directed_atlas(train, confirmation, view_names=views, maps=maps, permuted_maps=permuted)
    assert edges["direct_global_r2"].mean() > edges["permuted_direct_global_r2"].mean() + 0.25
    assert atlas_asymmetry(edges).shape[0] == 3
    cycles = cycle_errors(confirmation, view_names=views, maps=maps)
    assert len(cycles) == 6
    assert np.isfinite(cycles["cycle_rmse_standardized"]).all()
