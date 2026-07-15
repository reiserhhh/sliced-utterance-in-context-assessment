from __future__ import annotations

import numpy as np

from suica_core.conditional_transition import fit_conditional_transition_model, median_bandwidth


def test_median_bandwidth_is_positive_for_nonconstant_data() -> None:
    values = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 2.0]])
    assert median_bandwidth(values, seed=3) > 0.0


def test_conditional_embedding_reduces_nonlinear_reference_error() -> None:
    rng = np.random.default_rng(7)
    history = rng.uniform(-2.0, 2.0, size=(400, 1))
    outcome = np.column_stack([np.sin(2.0 * history[:, 0]), np.cos(history[:, 0])])
    model = fit_conditional_transition_model(
        history,
        outcome,
        input_features=96,
        output_features=48,
        ridge_alpha=0.1,
        seed=8,
    )
    residual = model.residual_embedding(history, outcome)
    null_residual = model.output_map.transform(outcome) - model.output_map.transform(outcome).mean(axis=0)
    assert np.mean(residual ** 2) < np.mean(null_residual ** 2)
