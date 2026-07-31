"""Tests for spectrum-matched orientation overlap."""
from __future__ import annotations

import numpy as np

from suica_core.v8_orientation_overlap import orientation_metrics


def test_identical_frames_have_unit_overlap() -> None:
    frame = np.eye(6)[:, :3]
    weights = np.asarray([0.5, 0.3, 0.2])
    metrics = orientation_metrics(frame, frame, weights, weights)
    assert np.isclose(metrics["hs"], 1.0)
    assert np.isclose(metrics["fidelity"], 1.0)
    assert np.isclose(metrics["principal_affinity"], 1.0)
    assert metrics["exact_intersection_rank"] == 3


def test_orthogonal_frames_have_zero_overlap() -> None:
    left = np.eye(6)[:, :3]
    right = np.eye(6)[:, 3:]
    weights = np.asarray([0.5, 0.3, 0.2])
    metrics = orientation_metrics(left, right, weights, weights)
    assert np.isclose(metrics["hs"], 0.0)
    assert np.isclose(metrics["fidelity"], 0.0)
    assert np.isclose(metrics["principal_affinity"], 0.0)
    assert metrics["exact_intersection_rank"] == 0


def test_hs_is_invariant_to_joint_rotation() -> None:
    rng = np.random.default_rng(11)
    left, _ = np.linalg.qr(rng.normal(size=(8, 3)))
    right, _ = np.linalg.qr(rng.normal(size=(8, 3)))
    rotation, _ = np.linalg.qr(rng.normal(size=(8, 8)))
    weights = np.asarray([0.6, 0.25, 0.15])
    before = orientation_metrics(left, right, weights, weights)
    after = orientation_metrics(
        rotation @ left,
        rotation @ right,
        weights,
        weights,
    )
    assert np.isclose(before["hs"], after["hs"])
    assert np.isclose(before["fidelity"], after["fidelity"])
