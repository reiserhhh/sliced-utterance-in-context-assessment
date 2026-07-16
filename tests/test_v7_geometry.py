from __future__ import annotations

import json

import numpy as np
import pytest

from suica_core.v7_geometry import GeometryBundle, fit_geometry_bundle, geometry_profile_cosine, score_geometry_bundle


def _fit(values: np.ndarray):
    return fit_geometry_bundle(
        values,
        feature_names=[f"feature_{index}" for index in range(values.shape[1])],
        operator={"id": "unit_test_operator"},
        representation={"id": "unit_test_representation"},
        runtime_artifact={"hash": "runtime-test"},
        reference_population={"cohort_commitment": "test-only", "n_authors": len(values)},
        min_units_for_score=2,
        landmark_count=7,
    )


def test_geometry_profile_is_row_order_invariant() -> None:
    rng = np.random.default_rng(20)
    values = rng.normal(size=(30, 5))
    first = _fit(values)
    permutation = rng.permutation(len(values))
    second = _fit(values[permutation])
    first_profile = score_geometry_bundle(first, values, unit_counts=np.full(len(values), 2))["landmark_distance_profile"]
    second_profile = score_geometry_bundle(second, values, unit_counts=np.full(len(values), 2))["landmark_distance_profile"]
    assert np.allclose(first_profile, second_profile, atol=1e-8)


def test_geometry_profile_is_common_orthogonal_transform_invariant() -> None:
    rng = np.random.default_rng(21)
    values = rng.normal(size=(36, 6))
    rotation, _ = np.linalg.qr(rng.normal(size=(6, 6)))
    first = _fit(values)
    second = _fit(values @ rotation)
    first_profile = score_geometry_bundle(first, values, unit_counts=np.full(len(values), 2))["landmark_distance_profile"]
    second_profile = score_geometry_bundle(second, values @ rotation, unit_counts=np.full(len(values), 2))["landmark_distance_profile"]
    assert np.allclose(first_profile, second_profile, atol=1e-8)
    assert np.nanmean(geometry_profile_cosine(first_profile, second_profile)) > 0.999999


def test_geometry_profile_is_common_translation_invariant() -> None:
    rng = np.random.default_rng(210)
    values = rng.normal(size=(36, 6))
    translation = rng.normal(size=6)
    first = _fit(values)
    second = _fit(values + translation)
    first_profile = score_geometry_bundle(first, values, unit_counts=np.full(len(values), 2))["landmark_distance_profile"]
    second_profile = score_geometry_bundle(second, values + translation, unit_counts=np.full(len(values), 2))["landmark_distance_profile"]
    assert np.allclose(first_profile, second_profile, atol=1e-8)


def test_geometry_does_not_silently_align_an_independently_rotated_target() -> None:
    rng = np.random.default_rng(211)
    reference = rng.normal(size=(40, 5))
    target = rng.normal(size=(12, 5))
    rotation, _ = np.linalg.qr(rng.normal(size=(5, 5)))
    bundle = _fit(reference)
    original = score_geometry_bundle(bundle, target, unit_counts=np.full(len(target), 2))["landmark_distance_profile"]
    rotated = score_geometry_bundle(bundle, target @ rotation, unit_counts=np.full(len(target), 2))["landmark_distance_profile"]
    assert not np.allclose(original, rotated, atol=1e-4)


def test_geometry_refuses_out_of_domain_and_insufficient_support() -> None:
    rng = np.random.default_rng(22)
    bundle = _fit(rng.normal(size=(40, 4)))
    result = score_geometry_bundle(bundle, np.array([[100.0, 100.0, 100.0, 100.0], [0.0, 0.0, 0.0, 0.0]]), unit_counts=np.array([2, 1]))
    assert result["status"] == ["GEOMETRY_REFUSE_OUTSIDE_REFERENCE_RADIAL_ENVELOPE", "GEOMETRY_REFUSE_INSUFFICIENT_OBSERVATION_SUPPORT"]


def test_default_scoring_path_reports_support_unverified_not_ready() -> None:
    rng = np.random.default_rng(31)
    values = rng.normal(size=(40, 4))
    bundle = _fit(values)
    target = np.vstack([values[:3], np.full((1, 4), 100.0)])

    # (a) With no unit_counts, ready rows are distinguished as support-unverified,
    # and radial-envelope refusal still takes precedence.
    default = score_geometry_bundle(bundle, target)
    assert default["status"][:3] == ["GEOMETRY_PROFILE_READY_SUPPORT_UNVERIFIED"] * 3
    assert default["status"][3] == "GEOMETRY_REFUSE_OUTSIDE_REFERENCE_RADIAL_ENVELOPE"
    assert "GEOMETRY_PROFILE_READY" not in default["status"]

    # (b) Explicit counts below the frozen threshold refuse.
    counted = score_geometry_bundle(bundle, target, unit_counts=np.array([2, 2, 1, 2]))
    assert counted["status"] == [
        "GEOMETRY_PROFILE_READY",
        "GEOMETRY_PROFILE_READY",
        "GEOMETRY_REFUSE_INSUFFICIENT_OBSERVATION_SUPPORT",
        "GEOMETRY_REFUSE_OUTSIDE_REFERENCE_RADIAL_ENVELOPE",
    ]

    # (c) An explicit attestation reproduces the old default statuses.
    attested = score_geometry_bundle(bundle, target, assume_support_verified=True)
    assert attested["status"][:3] == ["GEOMETRY_PROFILE_READY"] * 3
    assert attested["status"][3] == "GEOMETRY_REFUSE_OUTSIDE_REFERENCE_RADIAL_ENVELOPE"

    # Scoring math is unchanged across the three modes.
    assert np.allclose(default["landmark_distance_profile"], attested["landmark_distance_profile"])
    assert np.allclose(default["landmark_distance_profile"], counted["landmark_distance_profile"])


def test_fit_geometry_bundle_is_deterministic_and_takes_no_seed() -> None:
    rng = np.random.default_rng(32)
    values = rng.normal(size=(25, 3))
    first, second = _fit(values), _fit(values)
    assert first.bundle_id == second.bundle_id
    with pytest.raises(TypeError):
        _fit_with_seed(values)


def _fit_with_seed(values: np.ndarray):
    return fit_geometry_bundle(
        values,
        feature_names=[f"feature_{index}" for index in range(values.shape[1])],
        operator={"id": "unit_test_operator"},
        representation={"id": "unit_test_representation"},
        runtime_artifact={"hash": "runtime-test"},
        reference_population={"cohort_commitment": "test-only", "n_authors": len(values)},
        min_units_for_score=2,
        seed=11,
    )


def test_geometry_bundle_roundtrip_and_identifier_guard(tmp_path) -> None:
    rng = np.random.default_rng(23)
    bundle = _fit(rng.normal(size=(25, 3)))
    path = tmp_path / "geometry_bundle.json"
    bundle.write_json(path)
    loaded = GeometryBundle.from_dict(json.loads(path.read_text(encoding="utf-8")))
    assert loaded.bundle_id == bundle.bundle_id
    assert "author_id" not in path.read_text(encoding="utf-8")
    payload = bundle.to_dict()
    payload["reference_population"] = {"author_id": "not_allowed"}
    with pytest.raises(ValueError, match="identifier"):
        GeometryBundle.from_dict(payload)


def test_bundle_id_binds_reference_and_rejects_tampering() -> None:
    rng = np.random.default_rng(24)
    first = _fit(rng.normal(size=(25, 3)))
    second = _fit(rng.normal(loc=0.5, size=(25, 3)))
    assert first.bundle_id != second.bundle_id
    payload = first.to_dict()
    payload["feature_center"][0] += 0.1
    with pytest.raises(ValueError, match="does not match"):
        GeometryBundle.from_dict(payload)


def test_symmetric_landmark_orbit_is_row_order_invariant() -> None:
    square = np.array([
        [-1.0, -1.0],
        [-1.0, 1.0],
        [1.0, -1.0],
        [1.0, 1.0],
    ])
    target = np.array([[0.3, -0.2], [-0.7, 0.8]])
    kwargs = {
        "feature_names": ["x", "y"],
        "operator": {"id": "symmetric"},
        "representation": {"id": "symmetric"},
        "runtime_artifact": {"hash": "test"},
        "reference_population": {"cohort_commitment": "square", "n_authors": 4},
        "min_units_for_score": 1,
        "landmark_count": 1,
    }
    first = fit_geometry_bundle(square, **kwargs)
    second = fit_geometry_bundle(square[[2, 0, 3, 1]], **kwargs)
    first_profile = score_geometry_bundle(first, target)["landmark_distance_profile"]
    second_profile = score_geometry_bundle(second, target)["landmark_distance_profile"]
    assert len(first.reference_landmarks) == 4
    assert first.bundle_id == second.bundle_id
    assert np.allclose(first_profile, second_profile, atol=1e-8)
