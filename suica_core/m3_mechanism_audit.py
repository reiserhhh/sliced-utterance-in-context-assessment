"""Evaluation utilities for mechanism-selective micro-to-meso discovery."""
from __future__ import annotations

import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

from .m3_mechanism_contracts import (
    M3MechanismEstimate,
    M3MechanismTruth,
)


def same_author_auc(train: np.ndarray, test: np.ndarray) -> float:
    """Score whether independent views of the same author are nearest."""
    distance = np.linalg.norm(
        train[:, None] - test[None],
        axis=2,
    ) / np.sqrt(max(train.shape[1], 1))
    labels = np.eye(len(train), dtype=int).ravel()
    return float(roc_auc_score(labels, -distance.ravel()))


def truth_geometry_correlation(
    feature: np.ndarray,
    truth: np.ndarray,
) -> float:
    """Compare pairwise author geometry without aligning coordinate axes."""
    truth_distance = pdist(np.asarray(truth, dtype=float))
    if np.max(truth_distance) <= 1e-12:
        return float("nan")
    feature_distance = pdist(np.asarray(feature, dtype=float))
    value = spearmanr(feature_distance, truth_distance).statistic
    return float(value)


def audit_m3_mechanism_atlas(
    estimate: M3MechanismEstimate,
    truth: M3MechanismTruth,
) -> list[dict[str, float | str | bool]]:
    """Return one metric row per competing summary family."""
    rows: list[dict[str, float | str | bool]] = []
    for family in estimate.train_features:
        rows.append({
            "world": truth.world,
            "family": family,
            "expected": family == truth.expected_family,
            "same_author_auc": same_author_auc(
                estimate.train_features[family],
                estimate.test_features[family],
            ),
            "truth_geometry_spearman": truth_geometry_correlation(
                estimate.train_features[family],
                truth.author_parameter,
            ),
        })
    return rows
