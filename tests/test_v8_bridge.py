"""Synthetic tests for the offline V8 geometry-behavior bridge."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from suica_core.v8_bridge import (
    EVENT_CODES,
    QuantileGeometryProjector,
    SpectralGeometryProjector,
    canonical_orbit_distance_signatures,
    cross_modal_author_auc,
    distance_alignment,
    effective_rank,
    fit_opportunity_baseline,
    landmark_spectral_signatures,
    profile_behavior_features,
    profile_repeated_behavior_features,
    segment_event_frame,
    segment_event_repetition_frame,
    supported_profile_rate,
)


def test_quantile_shape_projector_removes_location_and_scale() -> None:
    base = np.linspace(1.0, 3.0, 16)
    bump = np.exp(-((np.arange(16) - 7.5) ** 2) / 8.0)
    profiles = np.vstack([
        base,
        base * 2.0 + 5.0,
        np.sort(base + 0.10 * bump),
        np.sort(base + 0.20 * bump),
    ])
    projector = QuantileGeometryProjector(
        family="shape_fpca",
        max_components=3,
    ).fit(profiles)
    scores = projector.transform(profiles)
    assert np.allclose(scores[0], scores[1], atol=1e-8)
    assert not np.allclose(scores[0], scores[-1])


def test_effective_rank_detects_one_dominant_direction() -> None:
    line = np.linspace(-2.0, 2.0, 40)
    values = np.column_stack([line, 2 * line, -3 * line])
    assert np.isclose(effective_rank(values), 1.0)


def test_opportunity_residual_changes_with_condition_expectation() -> None:
    rows = []
    for index in range(20):
        row = {"condition": "A" if index < 10 else "B"}
        row.update({code: 0 for code in EVENT_CODES})
        row["self_reference"] = int(index < 8 or index >= 18)
        rows.append(row)
    baseline = fit_opportunity_baseline(pd.DataFrame(rows), shrinkage=2.0)
    assert (
        baseline.probability("A", "self_reference")
        > baseline.probability("B", "self_reference")
    )
    assert np.isclose(
        baseline.probability("<unseen>", "self_reference"),
        baseline.global_probability["self_reference"],
    )


def test_behavior_features_include_pairs_and_transitions() -> None:
    profiles = [{
        "profile_id": "P1",
        "author_id": "A1",
        "side": "left",
        "cohort_split": "discovery",
        "segments": [
            {"segment_id": "S1", "spans": [{"text": "I feel ready."}]},
            {"segment_id": "S2", "spans": [{"text": "Please continue."}]},
            {"segment_id": "S3", "spans": [{"text": "I agree."}]},
        ],
    }]
    events = {
        "P1": [
            {
                "event_id": "S1::self_reference",
                "segment_id": "S1",
                "event_code": "self_reference",
                "evidence_span_ids": ["X1"],
            },
            {
                "event_id": "S1::affect_expression",
                "segment_id": "S1",
                "event_code": "affect_expression",
                "evidence_span_ids": ["X1"],
            },
            {
                "event_id": "S2::directive_expression",
                "segment_id": "S2",
                "event_code": "directive_expression",
                "evidence_span_ids": ["X2"],
            },
        ],
    }
    segments = segment_event_frame(
        profiles,
        events,
        condition_by_segment={"S1": "C", "S2": "C", "S3": "C"},
    )
    baseline = fit_opportunity_baseline(segments, shrinkage=2.0)
    features = profile_behavior_features(segments, opportunity=baseline)
    assert features.loc[0, "pair::affect_expression+self_reference"] == 1 / 3
    assert (
        features.loc[
            0,
            "transition::self_reference->directive_expression",
        ]
        == 0.5
    )
    assert features.loc[0, "summary::active_segment_rate"] == 2 / 3


def test_cross_modal_author_auc_is_perfect_for_matching_halves() -> None:
    authors = np.array(["A", "A", "B", "B", "C", "C"])
    sides = np.array(["left", "right"] * 3)
    observed = np.array([
        [1.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [0.0, 1.0],
        [-1.0, -1.0],
        [-1.0, -1.0],
    ])
    assert cross_modal_author_auc(observed, observed, authors, sides) == 1.0
    assert supported_profile_rate(
        observed,
        observed,
        authors,
        sides,
        prediction_threshold=0.1,
        evidence_threshold=0.1,
    ) == 1.0


def test_distance_alignment_recovers_shared_author_geometry() -> None:
    authors = np.array(["A", "A", "B", "B", "C", "C"])
    geometry = np.array([
        [0.0, 0.0],
        [0.1, 0.0],
        [1.0, 1.0],
        [1.1, 1.0],
        [3.0, 3.0],
        [3.1, 3.0],
    ])
    behavior = geometry * 2.0
    result = distance_alignment(geometry, behavior, authors)
    assert result["authors"] == 3
    assert np.isclose(result["distance_spearman"], 1.0)


def test_repeated_behavior_uses_exact_order_null() -> None:
    profiles = [{
        "profile_id": "P1",
        "author_id": "A1",
        "side": "left",
        "cohort_split": "discovery",
        "segments": [
            {"segment_id": "S1", "spans": [{"text": "one"}]},
            {"segment_id": "S2", "spans": [{"text": "two"}]},
            {"segment_id": "S3", "spans": [{"text": "three"}]},
        ],
    }]
    event_rows = [
        ("S1", "self_reference"),
        ("S2", "directive_expression"),
        ("S3", "affect_expression"),
    ]
    observer_runs = []
    for _ in range(3):
        observer_runs.append({
            "observer": {
                "P1": [
                    {
                        "event_id": f"{segment}::{code}",
                        "segment_id": segment,
                        "event_code": code,
                        "evidence_span_ids": [f"X-{segment}"],
                    }
                    for segment, code in event_rows
                ],
            },
        })
    segments = segment_event_repetition_frame(
        profiles,
        observer_runs,
        condition_by_segment={"S1": "C", "S2": "C", "S3": "C"},
    )
    baseline = fit_opportunity_baseline(segments, shrinkage=2.0)
    features = profile_repeated_behavior_features(
        segments,
        opportunity=baseline,
    )
    assert len(segments) == 9
    assert np.isfinite(
        features.loc[
            0,
            "order_null::self_reference->directive_expression",
        ]
    )
    assert (
        features.loc[
            0,
            "order_null::self_reference->directive_expression",
        ]
        > 0
    )


def test_stable_fpca_uses_paired_half_covariance() -> None:
    authors = np.repeat(np.array(["A", "B", "C", "D"]), 2)
    sides = np.tile(np.array(["left", "right"]), 4)
    base = np.linspace(1.0, 2.0, 16)
    profiles = []
    for author_index in range(4):
        author_shape = base + author_index * np.linspace(0.0, 0.2, 16)
        profiles.append(author_shape)
        profiles.append(author_shape + 0.01 * np.sin(np.arange(16)))
    projector = QuantileGeometryProjector(
        family="stable_fpca",
        max_components=4,
    ).fit(
        np.asarray(profiles),
        authors=authors,
        sides=sides,
    )
    transformed = projector.transform(np.asarray(profiles))
    assert transformed.shape[0] == 8
    assert 1 <= transformed.shape[1] <= 4


def test_landmark_spectral_signature_is_permutation_and_isometry_invariant() -> None:
    rng = np.random.default_rng(42)
    landmarks = rng.normal(size=(8, 5))
    queries = rng.normal(size=(4, 5))
    baseline, names = landmark_spectral_signatures(
        queries,
        landmarks,
        mode="combined",
    )
    permutation = rng.permutation(len(landmarks))
    permuted, permuted_names = landmark_spectral_signatures(
        queries,
        landmarks[permutation],
        mode="combined",
    )
    orthogonal, _ = np.linalg.qr(rng.normal(size=(5, 5)))
    translation = rng.normal(size=5)
    transformed, transformed_names = landmark_spectral_signatures(
        queries @ orthogonal + translation,
        landmarks @ orthogonal + translation,
        mode="combined",
    )
    assert names == permuted_names == transformed_names
    assert np.allclose(baseline, permuted, atol=1e-8)
    assert np.allclose(baseline, transformed, atol=1e-8)


def test_spectral_projector_has_fixed_out_of_sample_schema() -> None:
    rng = np.random.default_rng(7)
    landmarks = rng.normal(size=(8, 4))
    discovery = rng.normal(size=(20, 4))
    heldout = rng.normal(size=(5, 4))
    projector = SpectralGeometryProjector(
        landmarks=landmarks,
        mode="energy",
        max_components=6,
    ).fit(discovery)
    transformed = projector.transform(heldout)
    assert transformed.shape == (5, len(projector.output_names))
    assert transformed.shape[1] <= 6
    assert np.isfinite(transformed).all()


def test_canonical_orbit_signature_preserves_topology_without_input_identity() -> None:
    rng = np.random.default_rng(19)
    landmarks = rng.normal(size=(10, 6))
    queries = rng.normal(size=(5, 6))
    baseline, names, diagnostics = canonical_orbit_distance_signatures(
        queries,
        landmarks,
    )
    permutation = rng.permutation(len(landmarks))
    permuted, permuted_names, permuted_diagnostics = (
        canonical_orbit_distance_signatures(
            queries,
            landmarks[permutation],
        )
    )
    orthogonal, _ = np.linalg.qr(rng.normal(size=(6, 6)))
    translation = rng.normal(size=6)
    transformed, transformed_names, _ = canonical_orbit_distance_signatures(
        queries @ orthogonal + translation,
        landmarks @ orthogonal + translation,
    )
    assert names == permuted_names == transformed_names
    assert diagnostics["orbit_sizes"] == permuted_diagnostics["orbit_sizes"]
    assert np.allclose(baseline, permuted, atol=1e-8)
    assert np.allclose(baseline, transformed, atol=1e-8)


def test_canonical_orbit_refuses_unresolved_symmetric_fingerprints() -> None:
    landmarks = np.array([
        [-1.0, -1.0],
        [-1.0, 1.0],
        [1.0, -1.0],
        [1.0, 1.0],
    ])
    with pytest.raises(
        ValueError,
        match="CANONICAL_ORBIT_REFUSE_FINGERPRINT_COLLISION",
    ):
        canonical_orbit_distance_signatures(
            np.array([[0.2, 0.1]]),
            landmarks,
        )
