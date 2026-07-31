"""Tests for exact-inner K order nulls."""
from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v8_order_statistic_null import (
    PERMUTATIONS_4,
    build_exact_permutation_panel,
)
from suica_core.v8_realtext_relation_field import RealTextRelationSpec


def test_exact_permutation_residuals_have_zero_mean() -> None:
    assert np.array_equal(PERMUTATIONS_4[0], np.arange(4))
    events = pd.DataFrame(
        {
            "author_id": ["u"] * 8,
            "context": ["c"] * 8,
            "order": list(range(8)),
            "text": [f"event {index} with enough content" for index in range(8)],
        }
    )
    panel = build_exact_permutation_panel(
        events,
        corpus="test",
        feature_spec=RealTextRelationSpec(
            hash_dimensions=8,
            random_directions=2,
            transition_null_draws=0,
            minimum_split_authors=8,
            minimum_context_authors=4,
        ),
    )
    assert panel.residuals.shape[2] == 24
    assert np.allclose(panel.residuals.mean(axis=2), 0.0, atol=1e-6)
    assert np.array_equal(panel.native, panel.residuals[:, :, 0, :])
