"""Frozen coordinate-free relative geometry for the primary SUICA V7 object.

Current V7 evidence supports distributed, representation-indexed relative
geometry, not a small named factor coordinate system.  This module scores
distances to a frozen identifier-free landmark configuration under a
regularized Mahalanobis metric.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np


_FIELDS = {
    "bundle_id", "version", "feature_names", "feature_impute",
    "feature_center", "metric_whitener", "metric_regularization",
    "reference_landmarks", "reference_distance_summary", "support_rule",
    "runtime_artifact", "reference_population", "operator",
    "representation", "claim_boundary", "created_utc",
}
_FORBIDDEN_KEYS = {"author_id", "user_id", "participant_id", "document_id", "raw_text", "text"}
_CONTENT_HASH_EXCLUSIONS = {"bundle_id", "created_utc"}


@dataclass
class GeometryBundle:
    """Serializable V7 relative-geometry bundle without factor axes or IDs."""

    bundle_id: str
    version: str
    feature_names: list[str]
    feature_impute: list[float]
    feature_center: list[float]
    metric_whitener: list[list[float]]
    metric_regularization: float
    reference_landmarks: list[list[float]]
    reference_distance_summary: dict[str, Any]
    support_rule: dict[str, Any]
    runtime_artifact: dict[str, Any]
    reference_population: dict[str, Any]
    operator: dict[str, Any]
    representation: dict[str, Any]
    claim_boundary: str
    created_utc: str

    def to_dict(self) -> dict[str, Any]:
        """Return the complete frozen manifest needed for profile scoring."""
        return asdict(self)

    def write_json(self, path: str | Path) -> None:
        """Write an auditable bundle without source text or identifiers."""
        payload = self.to_dict()
        validate_geometry_bundle_payload(payload)
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GeometryBundle":
        """Load a previously frozen bundle after strict validation."""
        validate_geometry_bundle_payload(payload)
        return cls(**payload)


def geometry_content_sha256(payload: dict[str, Any]) -> str:
    """Hash every score-defining field in canonical JSON form."""
    content = {
        key: payload[key]
        for key in sorted(payload)
        if key not in _CONTENT_HASH_EXCLUSIONS
    }
    encoded = json.dumps(
        content,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _vector(value: Any, *, name: str, length: int | None = None) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 1 or (length is not None and len(array) != length) or not np.isfinite(array).all():
        raise ValueError(f"Geometry bundle {name} must be a finite vector with the required length.")
    return array


def _matrix(value: Any, *, name: str, columns: int) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim != 2 or array.shape[0] < 1 or array.shape[1] != columns or not np.isfinite(array).all():
        raise ValueError(f"Geometry bundle {name} must be a finite matrix with the required column count.")
    return array


def _reject_identifier_keys(value: Any, *, path: str = "payload") -> None:
    """Prevent persisted raw identifiers/text from entering a frozen bundle."""
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).strip().lower() in _FORBIDDEN_KEYS:
                raise ValueError(f"Geometry bundle may not persist identifier/text key: {path}.{key}")
            _reject_identifier_keys(nested, path=f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _reject_identifier_keys(nested, path=f"{path}[{index}]")


def validate_geometry_bundle_payload(payload: dict[str, Any]) -> None:
    """Validate the frozen V7 geometry contract without refitting anything."""
    if not isinstance(payload, dict):
        raise ValueError("Geometry bundle payload must be an object.")
    missing, unknown = sorted(_FIELDS.difference(payload)), sorted(set(payload).difference(_FIELDS))
    if missing:
        raise ValueError(f"Geometry bundle missing required fields: {', '.join(missing)}")
    if unknown:
        raise ValueError(f"Geometry bundle has unsupported fields: {', '.join(unknown)}")
    for field in ("bundle_id", "version", "claim_boundary", "created_utc"):
        if not isinstance(payload[field], str) or not payload[field].strip():
            raise ValueError(f"Geometry bundle {field} must be a non-empty string.")
    names = payload["feature_names"]
    if not isinstance(names, list) or not names or len(set(names)) != len(names) or not all(isinstance(name, str) and name for name in names):
        raise ValueError("Geometry bundle feature_names must be unique non-empty strings.")
    width = len(names)
    _vector(payload["feature_impute"], name="feature_impute", length=width)
    _vector(payload["feature_center"], name="feature_center", length=width)
    whitener = _matrix(payload["metric_whitener"], name="metric_whitener", columns=width)
    if whitener.shape[0] != width or not np.allclose(whitener, whitener.T, atol=1e-8):
        raise ValueError("Geometry bundle metric_whitener must be a symmetric feature-square matrix.")
    if not np.isfinite(float(payload["metric_regularization"])) or float(payload["metric_regularization"]) <= 0.0:
        raise ValueError("Geometry bundle metric_regularization must be positive and finite.")
    _matrix(payload["reference_landmarks"], name="reference_landmarks", columns=width)
    summary = payload["reference_distance_summary"]
    if not isinstance(summary, dict) or not {"support_radius_quantile", "support_radius_threshold", "n_reference_authors"}.issubset(summary):
        raise ValueError("Geometry bundle reference_distance_summary is incomplete.")
    if not 0.0 < float(summary["support_radius_quantile"]) <= 1.0 or float(summary["support_radius_threshold"]) <= 0.0 or int(summary["n_reference_authors"]) < 2:
        raise ValueError("Geometry bundle reference support summary is invalid.")
    for field in ("support_rule", "runtime_artifact", "reference_population", "operator", "representation"):
        if not isinstance(payload[field], dict) or not payload[field]:
            raise ValueError(f"Geometry bundle {field} must be a non-empty object.")
    support = payload["support_rule"]
    required_support = {
        "min_units_for_score",
        "radial_envelope_rule",
        "density_or_domain_support_estimated",
    }
    if not required_support.issubset(support):
        raise ValueError("Geometry bundle support_rule is incomplete.")
    if int(support["min_units_for_score"]) < 1 or bool(support["density_or_domain_support_estimated"]):
        raise ValueError("Geometry bundle support_rule must declare radial-only support.")
    _reject_identifier_keys(payload)
    expected_id = f"SU7-GEO-{geometry_content_sha256(payload)[:24]}"
    if payload["bundle_id"] != expected_id:
        raise ValueError("Geometry bundle_id does not match its score-defining content.")


def _as_matrix(features: np.ndarray | list[list[float]], *, width: int | None = None) -> np.ndarray:
    values = np.asarray(features, dtype=float)
    if values.ndim != 2 or values.shape[0] < 1 or values.shape[1] < 1 or (width is not None and values.shape[1] != width):
        raise ValueError("Geometry features must be a non-empty matrix with the frozen feature count.")
    return values


def _impute(values: np.ndarray, impute: np.ndarray) -> np.ndarray:
    return np.where(np.isfinite(values), values, impute[None, :])


def _distances(values: np.ndarray) -> np.ndarray:
    squared = np.sum(values**2, axis=1, keepdims=True)
    return np.sqrt(np.maximum(squared + squared.T - 2.0 * values @ values.T, 0.0))


def _landmarks(values: np.ndarray, count: int) -> np.ndarray:
    """Select complete tied farthest-point orbits, then canonically order them.

    A geometry-symmetric reference set has no identified member that can break
    a distance tie. Selecting one by row number would make the score depend on
    input order. We therefore include the complete tied orbit, even when that
    exceeds the requested landmark count. Profile scoring later sorts landmark
    distances, so an arbitrary order within an unresolved orbit is irrelevant.
    """
    if count < 1:
        raise ValueError("landmark_count must be >= 1.")
    distances = _distances(values)
    target = min(int(count), len(values))

    def tied_max(scores: np.ndarray) -> list[int]:
        finite = scores[np.isfinite(scores)]
        if not len(finite):
            return []
        maximum = float(finite.max())
        return np.flatnonzero(np.isclose(scores, maximum, rtol=1e-10, atol=1e-12)).astype(int).tolist()

    selected = set(tied_max(distances.mean(axis=1)))
    while len(selected) < target:
        indices = np.asarray(sorted(selected), dtype=int)
        minimum = distances[:, indices].min(axis=1)
        minimum[indices] = -np.inf
        tied = tied_max(minimum)
        if not tied:
            break
        selected.update(tied)
    chosen = values[np.asarray(sorted(selected), dtype=int)]
    order = np.lexsort(tuple(chosen[:, column] for column in reversed(range(chosen.shape[1]))))
    return chosen[order]


def _whitener(centered: np.ndarray, regularization: float) -> tuple[np.ndarray, float]:
    covariance = np.atleast_2d(np.cov(centered, rowvar=False, ddof=1)).astype(float)
    scale = float(np.trace(covariance) / centered.shape[1])
    effective = max(float(regularization) * max(scale, 1e-12), 1e-12)
    values, vectors = np.linalg.eigh(0.5 * (covariance + covariance.T))
    inverse_sqrt = 1.0 / np.sqrt(np.maximum(values + effective, 1e-12))
    return (vectors * inverse_sqrt[None, :]) @ vectors.T, effective


def fit_geometry_bundle(
    features: np.ndarray | list[list[float]],
    *,
    feature_names: list[str],
    operator: dict[str, Any],
    representation: dict[str, Any],
    runtime_artifact: dict[str, Any],
    reference_population: dict[str, Any],
    min_units_for_score: int,
    landmark_count: int = 16,
    regularization: float = 1e-3,
    support_radius_quantile: float = 0.99,
    seed: int = 20260715,
    version: str = "v7-geometry-1",
) -> GeometryBundle:
    """Freeze a reference-relative landmark geometry from author features only."""
    if not feature_names or len(feature_names) != len(set(feature_names)):
        raise ValueError("feature_names must be a unique non-empty list.")
    if int(min_units_for_score) < 1 or not 0.0 < float(support_radius_quantile) <= 1.0:
        raise ValueError("Invalid geometry support parameters.")
    values = _as_matrix(features, width=len(feature_names))
    if len(values) < 2:
        raise ValueError("Geometry fitting requires at least two reference authors.")
    impute = np.nanmean(np.where(np.isfinite(values), values, np.nan), axis=0)
    impute = np.where(np.isfinite(impute), impute, 0.0)
    complete = _impute(values, impute)
    center = complete.mean(axis=0)
    transform, effective_regularization = _whitener(complete - center, float(regularization))
    whitened = (complete - center) @ transform
    radii = np.linalg.norm(whitened, axis=1)
    content = {
        "version": str(version),
        "feature_names": list(feature_names),
        "feature_impute": impute.tolist(),
        "feature_center": center.tolist(),
        "metric_whitener": transform.tolist(),
        "metric_regularization": effective_regularization,
        "reference_landmarks": _landmarks(whitened, int(landmark_count)).tolist(),
        "reference_distance_summary": {
            "support_radius_quantile": float(support_radius_quantile),
            "support_radius_threshold": float(np.quantile(radii, support_radius_quantile)),
            "n_reference_authors": int(len(complete)),
            "radius_definition": "regularized_mahalanobis_radius_from_reference_center",
        },
        "support_rule": {
            "min_units_for_score": int(min_units_for_score),
            "radial_envelope_rule": "refuse_if_regularized_mahalanobis_radius_exceeds_frozen_threshold",
            "density_or_domain_support_estimated": False,
        },
        "runtime_artifact": dict(runtime_artifact),
        "reference_population": dict(reference_population),
        "operator": dict(operator),
        "representation": dict(representation),
        "claim_boundary": (
            "Frozen relative geometry only. Landmark-distance profiles are reference-relative, "
            "not factor scores, traits, clinical states, or cross-domain comparable values without transport evidence."
        ),
    }
    bundle = GeometryBundle(
        bundle_id=f"SU7-GEO-{geometry_content_sha256(content)[:24]}",
        created_utc=datetime.now(UTC).isoformat(),
        **content,
    )
    validate_geometry_bundle_payload(bundle.to_dict())
    return bundle


def score_geometry_bundle(
    bundle: GeometryBundle | dict[str, Any],
    features: np.ndarray | list[list[float]],
    *,
    unit_counts: np.ndarray | list[int] | None = None,
) -> dict[str, Any]:
    """Return frozen landmark-distance profiles plus explicit support refusals."""
    frozen = bundle if isinstance(bundle, GeometryBundle) else GeometryBundle.from_dict(bundle)
    values = _as_matrix(features, width=len(frozen.feature_names))
    counts = np.full(len(values), int(frozen.support_rule["min_units_for_score"]), dtype=int) if unit_counts is None else np.asarray(unit_counts, dtype=int)
    if counts.shape != (len(values),):
        raise ValueError("unit_counts must contain one count per feature row.")
    whitened = (_impute(values, np.asarray(frozen.feature_impute)) - np.asarray(frozen.feature_center)) @ np.asarray(frozen.metric_whitener)
    landmarks = np.asarray(frozen.reference_landmarks)
    profile = np.sqrt(np.maximum(np.sum((whitened[:, None, :] - landmarks[None, :, :]) ** 2, axis=2), 0.0))
    profile = np.sort(profile, axis=1)
    radius = np.linalg.norm(whitened, axis=1)
    threshold = float(frozen.reference_distance_summary["support_radius_threshold"])
    minimum = int(frozen.support_rule["min_units_for_score"])
    status = [
        "GEOMETRY_REFUSE_INSUFFICIENT_OBSERVATION_SUPPORT" if int(count) < minimum else
        "GEOMETRY_REFUSE_OUTSIDE_REFERENCE_RADIAL_ENVELOPE" if float(value) > threshold else
        "GEOMETRY_PROFILE_READY"
        for count, value in zip(counts, radius, strict=True)
    ]
    return {
        "status": status,
        "landmark_distance_profile": profile,
        "nearest_landmark_distance": profile.min(axis=1),
        "mean_landmark_distance": profile.mean(axis=1),
        "reference_radius": radius,
        "support_radius_threshold": threshold,
        "bundle_id": frozen.bundle_id,
        "claim_boundary": frozen.claim_boundary,
    }


def geometry_profile_cosine(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Return rowwise cosine agreement between equally shaped geometry profiles."""
    first = _as_matrix(left)
    second = _as_matrix(right, width=first.shape[1])
    if len(first) != len(second):
        raise ValueError("Geometry profiles must have matching row counts.")
    denominator = np.linalg.norm(first, axis=1) * np.linalg.norm(second, axis=1)
    return np.divide(np.sum(first * second, axis=1), denominator, out=np.full(len(first), np.nan), where=denominator > 1e-12)
