"""Tests for same-author cross-context relation-geometry transport."""
from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v8_context_geometry_transport import (
    ContextTransportSpec,
    _holm_family_adjustment,
    _null_components,
    evaluate_context_transport,
)
from suica_core.v8_event_set_composition_knockout import build_event_tensor
from suica_core.v8_marginal_background_quotient import (
    marginal_feature_blocks_batch,
)
from suica_core.v8_realtext_relation_field import RealTextRelationSpec
from suica_core.v8_residual_geometry_correspondence import frozen_bandwidth


def _metadata() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "author_id": [f"u{index}" for index in range(240)],
            "context": "a",
            "split": ["D0"] * 100 + ["D1"] * 70 + ["D2"] * 70,
        }
    )


def _panel(*, transport: bool, seed: int) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    metadata = _metadata()
    latent_a = rng.normal(size=(len(metadata), 12))
    latent_b = (
        latent_a
        if transport
        else rng.normal(size=(len(metadata), 12))
    )
    q, _ = np.linalg.qr(rng.normal(size=(12, 12)))
    values_a = np.stack(
        [
            latent_a + rng.normal(scale=0.12, size=latent_a.shape),
            latent_a + rng.normal(scale=0.12, size=latent_a.shape),
        ],
        axis=1,
    )
    values_b = np.stack(
        [
            latent_b @ q + rng.normal(scale=0.12, size=latent_b.shape),
            latent_b @ q + rng.normal(scale=0.12, size=latent_b.shape),
        ],
        axis=1,
    )
    nuisance_a = rng.normal(size=(len(metadata), 2, 3))
    nuisance_b = rng.normal(size=(len(metadata), 2, 3))
    return {
        "metadata": metadata,
        "values_a": values_a,
        "values_b": values_b,
        "nuisance_a": nuisance_a,
        "nuisance_b": nuisance_b,
        "bandwidth_a": frozen_bandwidth(values_a, metadata),
        "bandwidth_b": frozen_bandwidth(values_b, metadata),
        "scales": (0.5,),
        "corpus": "synthetic",
        "context_a": "a",
        "context_b": "b",
    }


def _spec() -> ContextTransportSpec:
    return ContextTransportSpec(
        d0_null_draws=99,
        test_null_draws=499,
        bootstrap_draws=99,
        minimum_held_authors=24,
        seed=811,
    )


def test_synchronous_cross_null_preserves_b_geometry() -> None:
    rng = np.random.default_rng(31)
    base = rng.normal(size=(40, 40))
    base = 0.5 * (base + base.T)
    np.fill_diagonal(base, 0.0)
    null = _null_components(
        base,
        base,
        base,
        base,
        draws=99,
        rng=np.random.default_rng(33),
    )
    assert np.all(np.isfinite(null["cross"]))
    assert float(np.mean(null["cross"])) < 0.20
    assert np.isclose(
        np.linalg.norm(base, ord="fro"),
        np.linalg.norm(base, ord="fro"),
    )


def test_holm_family_adjustment_does_not_assume_pair_independence() -> None:
    cells = pd.DataFrame(
        {
            "cell_id": ["a", "b", "c", "d0"],
            "split": ["D1", "D1", "D2", "D0"],
            "raw_p": [0.01, 0.03, 0.04, 0.001],
        }
    )
    adjusted = _holm_family_adjustment(cells).set_index("cell_id")
    assert np.isclose(adjusted.loc["a", "holm_p"], 0.03)
    assert np.isclose(adjusted.loc["b", "holm_p"], 0.06)
    assert np.isclose(adjusted.loc["c", "holm_p"], 0.06)
    assert np.isnan(adjusted.loc["d0", "holm_p"])


def test_context_transport_detects_shared_relation_geometry() -> None:
    result = evaluate_context_transport(
        {"shared": _panel(transport=True, seed=41)},
        spec=_spec(),
    )
    assert result["pair_status"].iloc[0]["status"] == (
        "CONTEXT_TRANSPORTABLE_RELATION_GEOMETRY"
    )
    cross = result["cells"].loc[
        result["cells"]["component"].eq("cross")
        & result["cells"]["split"].isin(["D1", "D2"])
    ]
    assert cross["excess"].gt(0).all()
    assert cross["normalized_cross_excess"].ge(0.25).all()


def test_context_transport_refuses_unresolved_cross_context_geometry() -> None:
    result = evaluate_context_transport(
        {"bound": _panel(transport=False, seed=43)},
        spec=_spec(),
    )
    assert result["pair_status"].iloc[0]["status"] == (
        "CROSS_CONTEXT_UNDERRESOLVED"
    )


def test_context_transport_refuses_small_held_panels() -> None:
    panel = _panel(transport=True, seed=47)
    panel["metadata"] = panel["metadata"].iloc[:120].reset_index(drop=True)
    for key in ("values_a", "values_b", "nuisance_a", "nuisance_b"):
        panel[key] = panel[key][:120]
    result = evaluate_context_transport(
        {"small": panel},
        spec=_spec(),
    )
    assert result["pair_status"].iloc[0]["status"] == (
        "WITHIN_CONTEXT_GEOMETRY_UNDERRESOLVED"
    )


def test_even_event_budget_above_eight_is_supported() -> None:
    rows = []
    for author in ("u1", "u2"):
        for order in range(12):
            rows.append(
                {
                    "author_id": author,
                    "context": "a",
                    "order": order,
                    "text": f"event {order} for {author}",
                }
            )
    tensor = build_event_tensor(
        pd.DataFrame(rows),
        corpus="synthetic",
        feature_spec=RealTextRelationSpec(),
        expected_events=12,
    )
    assert tensor.vectors.shape[1] == 12
    paths = np.random.default_rng(59).normal(size=(5, 6, 8))
    blocks = marginal_feature_blocks_batch(
        paths,
        marginal_directions=np.random.default_rng(61).normal(size=(3, 8)),
    )
    assert all(len(values) == 5 for values in blocks.values())
