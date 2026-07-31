"""Tests for the M4-C.3.2 creation-only intervention."""
from __future__ import annotations

import numpy as np

from suica_core.m4_creation_intervention import (
    author_relation_geometry,
    compose_creation_only_loop,
    relative_headroom_recovery,
)
from suica_core.m4_physical_edge_composition import M4PhysicalEdgeView


def _view(seed: int = 1301) -> M4PhysicalEdgeView:
    rng = np.random.default_rng(seed)
    creation = rng.normal(size=(12, 7, 2))
    response = rng.normal(size=(12, 2, 7))
    choice = rng.normal(size=(12, 7, 7))
    loop = np.einsum(
        "acd,adk,akj->acj",
        creation,
        response,
        choice,
        optimize=True,
    )
    return M4PhysicalEdgeView(
        creation=creation,
        response=response,
        choice=choice,
        jacobian_loop=loop,
        finite_loop=loop.copy(),
        selected_model=np.full(12, "linear", dtype=object),
        projection_error=np.zeros(12),
        legacy_loop_difference=np.zeros(12),
    )


def test_creation_intervention_freezes_other_edges() -> None:
    frozen = _view()
    candidate = _view(seed=1302)
    observed = compose_creation_only_loop(candidate.creation, frozen)
    expected = np.einsum(
        "acd,adk,akj->acj",
        candidate.creation,
        frozen.response,
        frozen.choice,
        optimize=True,
    )
    assert np.array_equal(observed, expected)
    assert not np.allclose(observed, candidate.jacobian_loop)


def test_author_relation_geometry_and_headroom_recovery() -> None:
    frozen = _view(seed=1303)
    assert author_relation_geometry(
        frozen.jacobian_loop,
        frozen.jacobian_loop,
    ) == 1.0
    assert np.isclose(
        relative_headroom_recovery(0.55, 0.70, 0.80),
        0.6,
    )
    assert np.isnan(relative_headroom_recovery(0.80, 0.81, 0.80))
