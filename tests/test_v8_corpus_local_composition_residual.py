"""Tests for corpus-local signed composition residuals."""
from __future__ import annotations

import numpy as np

from suica_core.v8_corpus_local_composition_residual import (
    _symmetric_coordinates,
    residual_coordinates,
    signed_replicate_strength,
)


def test_symmetric_coordinates_preserve_frobenius_inner_product() -> None:
    rng = np.random.default_rng(3)
    first = rng.normal(size=(1, 24, 5))
    second = rng.normal(size=(1, 24, 5))
    first_covariance = first[0].T @ first[0] / 24
    second_covariance = second[0].T @ second[0] / 24
    first_coordinate = _symmetric_coordinates(first)[0]
    second_coordinate = _symmetric_coordinates(second)[0]
    assert np.isclose(
        first_coordinate @ second_coordinate,
        np.sum(first_covariance * second_covariance),
    )


def test_signed_strength_and_context_baseline() -> None:
    values = np.asarray(
        [
            [[2.0, 1.0], [2.1, 1.1]],
            [[-2.0, -1.0], [-2.1, -1.1]],
            [[1.5, 0.5], [1.6, 0.6]],
            [[-1.5, -0.5], [-1.6, -0.6]],
        ]
    )
    baseline = {
        ("c", 0): np.asarray([0.5, 0.5]),
        ("c", 1): np.asarray([0.5, 0.5]),
    }
    residual = residual_coordinates(
        values,
        np.asarray(["c"] * len(values)),
        baseline,
    )
    assert np.allclose(residual[0, 0], [1.5, 0.5])
    assert signed_replicate_strength(residual) > 0
