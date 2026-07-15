from __future__ import annotations

import numpy as np

from suica_core.ordered_transition import (
    alignment_margins,
    block_order_null_operator,
    centered_transition_operator,
    ordered_pairs_from_blocks,
    paired_bootstrap_mean,
    sign_flip_pvalue,
)


def test_centered_operator_removes_constant_margins() -> None:
    values = np.ones((5, 3))
    operator = centered_transition_operator(values, values)
    assert np.allclose(operator, 0.0)


def test_standardized_operator_removes_pure_amplitude_difference() -> None:
    source = np.array([[0.0], [1.0], [2.0], [3.0]])
    target = np.array([[0.0], [2.0], [4.0], [6.0]])
    raw = centered_transition_operator(source, target)
    standardized = centered_transition_operator(source, target, diagonal_standardize=True)
    assert raw[0] != standardized[0]
    assert np.isclose(standardized[0], 1.0)


def test_block_null_is_deterministic_and_differs_from_ordered_path() -> None:
    blocks = np.array([
        [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]],
        [[0.0, 1.0], [1.0, 1.0], [2.0, 1.0]],
    ])
    source, target = ordered_pairs_from_blocks(blocks)
    ordered = centered_transition_operator(source, target)
    first = block_order_null_operator(blocks, draws=10, seed_key="fixed")
    second = block_order_null_operator(blocks, draws=10, seed_key="fixed")
    assert np.allclose(first, second)
    assert not np.allclose(ordered, first)


def test_alignment_and_paired_inference_detect_positive_contrast() -> None:
    left = np.eye(6)
    right = np.eye(6)
    assert np.all(alignment_margins(left, right) > 0.9)
    contrast = np.array([0.1, 0.2, 0.1, 0.3, 0.15, 0.25])
    bootstrap = paired_bootstrap_mean(contrast, iterations=200, seed=1)
    assert bootstrap["ci_lo"] > 0.0
    assert sign_flip_pvalue(contrast, iterations=999, seed=1) < 0.05
