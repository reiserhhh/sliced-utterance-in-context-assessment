from __future__ import annotations

import numpy as np

from suica_core.path_signature import (
    path_signature_features,
    piecewise_linear_signature,
    signature_dimension,
)


def test_signature_dimension_and_straight_line_level_one() -> None:
    assert signature_dimension(3, 3) == 39
    path = np.array([[0.0, 0.0], [1.0, 2.0]])
    signature = piecewise_linear_signature(path, depth=2)
    assert np.allclose(signature[:2], [1.0, 2.0])


def test_ordered_paths_with_same_endpoint_differ_at_higher_signature_level() -> None:
    left_then_up = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]])
    up_then_left = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    a = piecewise_linear_signature(left_then_up, depth=2)
    b = piecewise_linear_signature(up_then_left, depth=2)
    assert np.allclose(a[:2], b[:2])
    assert not np.allclose(a[2:], b[2:])


def test_time_augmented_shape_removes_scale_but_keeps_ordered_geometry() -> None:
    base = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]])
    scaled = base * 10.0
    a, scale_a = path_signature_features(base, depth=3)
    b, scale_b = path_signature_features(scaled, depth=3)
    assert scale_b > scale_a
    assert np.allclose(a, b)
