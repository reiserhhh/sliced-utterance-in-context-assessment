"""Tests for the V8 canonical-geometry fresh-panel statistics."""
from __future__ import annotations

import numpy as np

from scripts.run_suica_v8_canonical_geometry_fresh_panel import (
    _fast_pairing_permutation_p,
    _wilson_lower,
)
from suica_core.v8_bridge import cross_modal_author_auc


def test_wilson_lower_is_bounded_and_below_observed_rate() -> None:
    lower = _wilson_lower(89, 156)
    assert 0.0 < lower < 89 / 156
    assert np.isclose(lower, 0.4920613571347295)


def test_fast_pairing_permutation_detects_matching_halves() -> None:
    authors = np.repeat(np.asarray([f"A{index}" for index in range(10)]), 2)
    sides = np.tile(np.asarray(["left", "right"]), 10)
    centers = np.eye(10)
    values = np.vstack([
        np.vstack([center, center]) for center in centers
    ])
    observed = cross_modal_author_auc(
        values,
        values,
        authors,
        sides,
        metric="cosine",
    )
    p_value = _fast_pairing_permutation_p(
        values,
        authors,
        sides,
        metric="cosine",
        observed=observed,
        seed=17,
        permutations=2000,
    )
    assert observed == 1.0
    assert p_value < 0.01
