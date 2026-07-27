"""Agreement and accuracy utilities for SUICA V8 blind human coding."""
from __future__ import annotations

from collections.abc import Iterable

import numpy as np


def gwet_ac1_binary(first: Iterable[int], second: Iterable[int]) -> float:
    """Return Gwet AC1 for two complete binary coding vectors."""
    left = np.asarray(list(first), dtype=int)
    right = np.asarray(list(second), dtype=int)
    if left.shape != right.shape or left.ndim != 1 or not len(left):
        raise ValueError("Gwet AC1 requires equal non-empty vectors")
    if not (
        np.isin(left, (0, 1)).all()
        and np.isin(right, (0, 1)).all()
    ):
        raise ValueError("Gwet AC1 inputs must be binary")
    observed = float(np.mean(left == right))
    positive_prevalence = float((left.mean() + right.mean()) / 2.0)
    chance = 2.0 * positive_prevalence * (1.0 - positive_prevalence)
    denominator = 1.0 - chance
    return (
        float((observed - chance) / denominator)
        if denominator > 1e-12
        else 1.0
    )


def binary_metrics(
    truth: Iterable[int],
    predicted: Iterable[int],
) -> dict[str, float]:
    """Return precision, recall, and F1 for a binary event code."""
    gold = np.asarray(list(truth), dtype=int)
    estimate = np.asarray(list(predicted), dtype=int)
    if gold.shape != estimate.shape or gold.ndim != 1 or not len(gold):
        raise ValueError("binary metrics require equal non-empty vectors")
    true_positive = int(np.sum((gold == 1) & (estimate == 1)))
    false_positive = int(np.sum((gold == 0) & (estimate == 1)))
    false_negative = int(np.sum((gold == 1) & (estimate == 0)))
    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive
        else 0.0
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative
        else 0.0
    )
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "support": int(gold.sum()),
    }


def span_set_f1(
    truth: Iterable[str],
    predicted: Iterable[str],
) -> float:
    """Return set F1 for evidence span identifiers."""
    gold = {str(value) for value in truth if str(value)}
    estimate = {str(value) for value in predicted if str(value)}
    if not gold and not estimate:
        return 1.0
    if not gold or not estimate:
        return 0.0
    return float(2.0 * len(gold & estimate) / (len(gold) + len(estimate)))
