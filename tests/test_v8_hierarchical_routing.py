from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from suica_core.v8_hierarchical_routing import (
    EvidenceLayer,
    TaskRoute,
    fit_selected_route_predict,
    fit_source_router_predict,
    route_columns,
    run_nested_route_cv,
    validate_hierarchy,
)


def _continuous_frame(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for fold in range(5):
        for index in range(24):
            upstream = rng.normal()
            canonical = rng.normal()
            opportunity = rng.normal()
            rows.append({
                "pseudonymous_id": f"{fold}-{index}",
                "official_fold": fold,
                "upstream": upstream,
                "canonical": canonical,
                "opportunity": opportunity,
                "target": 0.9 * upstream + rng.normal(scale=0.12),
            })
    return pd.DataFrame(rows)


def _layers() -> dict[str, EvidenceLayer]:
    return {
        "upstream": EvidenceLayer(
            name="upstream",
            level="L1",
            columns=("upstream",),
            estimand="source representation",
        ),
        "canonical": EvidenceLayer(
            name="canonical",
            level="L2",
            columns=("canonical",),
            estimand="canonical geometry",
        ),
        "opportunity": EvidenceLayer(
            name="opportunity",
            level="L2C",
            columns=("opportunity",),
            estimand="observation opportunity",
        ),
    }


def test_hierarchy_refuses_overlapping_columns() -> None:
    layers = _layers()
    layers["canonical"] = EvidenceLayer(
        name="canonical",
        level="L2",
        columns=("upstream",),
        estimand="invalid overlap",
    )
    with pytest.raises(ValueError, match="disjoint"):
        validate_hierarchy(
            layers,
            [TaskRoute(name="one", layers=("upstream",))],
        )


def test_route_resolution_preserves_declared_layer_order() -> None:
    route = TaskRoute(
        name="mixed",
        layers=("canonical", "opportunity"),
    )
    assert route_columns(_layers(), route) == ["canonical", "opportunity"]


def test_nested_router_uses_only_non_test_rows_for_selection() -> None:
    frame = _continuous_frame()
    routes = [
        TaskRoute(name="upstream", layers=("upstream",)),
        TaskRoute(name="canonical", layers=("canonical",)),
    ]
    result = run_nested_route_cv(
        frame,
        layers=_layers(),
        routes=routes,
        target="target",
        fold_column="official_fold",
        task="continuous",
        parameters=[0.01, 1.0],
        view="nested_router",
        cohort="synthetic",
    )
    assert len(result.predictions) == len(frame)
    assert set(result.selections["test_fold"]) == set(range(5))
    assert (result.selections["n_train"] == 96).all()
    assert set(result.selections["selected_route"]) == {"upstream"}
    assert result.summary["pearson_r"] > 0.95


def test_source_router_predicts_destination_without_destination_labels() -> None:
    source = _continuous_frame()
    destination = source.drop(columns="target").iloc[:10].copy()
    predictions, selection = fit_source_router_predict(
        source,
        destination,
        layers=_layers(),
        routes=[
            TaskRoute(name="upstream", layers=("upstream",)),
            TaskRoute(name="canonical", layers=("canonical",)),
        ],
        target="target",
        fold_column="official_fold",
        task="continuous",
        parameters=[0.01, 1.0],
    )
    assert len(predictions) == len(destination)
    assert np.isfinite(predictions).all()
    assert selection["selected_route"] == "upstream"


def test_frozen_route_prediction_does_not_reselect() -> None:
    source = _continuous_frame()
    destination = source.drop(columns="target").iloc[:10].copy()
    predictions = fit_selected_route_predict(
        source,
        destination,
        layers=_layers(),
        route=TaskRoute(name="frozen", layers=("upstream",)),
        target="target",
        fold_column="official_fold",
        task="continuous",
        parameter=0.01,
    )
    assert len(predictions) == len(destination)
    assert np.isfinite(predictions).all()
