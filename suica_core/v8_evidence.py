"""Restricted vector queries and planted explanation-fidelity tests for V8."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from .v8_contracts import canonical_sha256


def row_cosine(values: np.ndarray) -> np.ndarray:
    """Return row-normalized vectors with zero rows left at zero."""
    matrix = np.asarray(values, dtype=float)
    if matrix.ndim != 2 or not np.isfinite(matrix).all():
        raise ValueError("values must be a finite matrix")
    return matrix / np.maximum(np.linalg.norm(matrix, axis=1, keepdims=True), 1e-12)


def nearest_neighbors(
    query: np.ndarray,
    reference: np.ndarray,
    *,
    count: int,
    exclude_index: int | None = None,
) -> list[dict[str, float | int]]:
    """Query a frozen reference by cosine distance only."""
    q = np.asarray(query, dtype=float).reshape(1, -1)
    r = np.asarray(reference, dtype=float)
    if r.ndim != 2 or q.shape[1] != r.shape[1] or count < 1:
        raise ValueError("query/reference dimensions and count must be valid")
    similarity = (row_cosine(q) @ row_cosine(r).T).ravel()
    if exclude_index is not None and 0 <= int(exclude_index) < len(similarity):
        similarity[int(exclude_index)] = -np.inf
    order = np.argsort(-similarity, kind="stable")[: min(int(count), len(r))]
    return [
        {"reference_index": int(index), "cosine_similarity": float(similarity[index])}
        for index in order
    ]


def matched_neighbor(
    query_nuisance: np.ndarray,
    reference_nuisance: np.ndarray,
    *,
    exclude_index: int | None = None,
) -> dict[str, float | int]:
    """Find the closest nuisance-matched reference without reading outcomes."""
    q = np.asarray(query_nuisance, dtype=float).reshape(1, -1)
    r = np.asarray(reference_nuisance, dtype=float)
    if r.ndim != 2 or q.shape[1] != r.shape[1]:
        raise ValueError("nuisance query/reference dimensions must match")
    distances = np.linalg.norm(r - q, axis=1)
    if exclude_index is not None and 0 <= int(exclude_index) < len(distances):
        distances[int(exclude_index)] = np.inf
    index = int(np.argmin(distances))
    return {"reference_index": index, "nuisance_distance": float(distances[index])}


def local_direction_traversal(
    vectors: np.ndarray,
    direction: np.ndarray,
    *,
    center: np.ndarray | None = None,
) -> np.ndarray:
    """Project vectors onto one frozen local technical direction."""
    values = np.asarray(vectors, dtype=float)
    axis = np.asarray(direction, dtype=float).ravel()
    if values.ndim != 2 or values.shape[1] != len(axis) or not np.isfinite(values).all():
        raise ValueError("vectors and direction must be finite and aligned")
    norm = float(np.linalg.norm(axis))
    if norm <= 1e-12:
        raise ValueError("direction must be non-zero")
    origin = np.zeros(values.shape[1]) if center is None else np.asarray(center, dtype=float)
    if origin.shape != (values.shape[1],):
        raise ValueError("center dimension mismatch")
    return (values - origin[None, :]) @ (axis / norm)


def group_difference(
    first: np.ndarray,
    second: np.ndarray,
    *,
    direction: np.ndarray,
) -> dict[str, float]:
    """Compare two groups along a frozen direction with a standard error."""
    left = local_direction_traversal(first, direction)
    right = local_direction_traversal(second, direction)
    difference = float(np.mean(left) - np.mean(right))
    sem = float(np.sqrt(np.var(left, ddof=1) / len(left) + np.var(right, ddof=1) / len(right)))
    return {"mean_difference": difference, "sem": sem}


def score_segments(
    segments: np.ndarray,
    *,
    direction: np.ndarray,
    denominator: int | None = None,
) -> float:
    """Evaluate an additive registered functional over segment vectors."""
    values = np.asarray(segments, dtype=float)
    if values.ndim != 2 or not len(values):
        return 0.0
    count = int(denominator or len(values))
    if count < len(values):
        raise ValueError("denominator cannot be smaller than retained segments")
    return float(np.sum(local_direction_traversal(values, direction)) / count)


def occlusion_effect(
    segments: np.ndarray,
    indices: np.ndarray | list[int],
    *,
    direction: np.ndarray,
) -> float:
    """Return full minus retained score under an original-count denominator."""
    values = np.asarray(segments, dtype=float)
    removed = np.asarray(indices, dtype=int)
    keep = np.ones(len(values), dtype=bool)
    keep[removed] = False
    return score_segments(values, direction=direction) - score_segments(
        values[keep], direction=direction, denominator=len(values)
    )


def bootstrap_mean_ci(
    values: np.ndarray,
    *,
    seed: int,
    draws: int = 2000,
) -> tuple[float, float, float]:
    """Return mean and percentile interval from row-level bootstrap draws."""
    array = np.asarray(values, dtype=float)
    array = array[np.isfinite(array)]
    if len(array) < 2:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    sampled = array[rng.integers(0, len(array), size=(int(draws), len(array)))].mean(axis=1)
    return float(array.mean()), float(np.quantile(sampled, 0.025)), float(np.quantile(sampled, 0.975))


def simulate_evidence_world(
    *,
    seed: int,
    authors: int = 400,
    segments_per_author: int = 12,
    dimensions: int = 16,
    causal_segments: int = 4,
    null: bool = False,
) -> dict[str, Any]:
    """Plant causal spans in a high-dimensional nuisance-rich vector world."""
    if not 0 <= causal_segments < segments_per_author:
        raise ValueError("causal_segments must be smaller than total segments")
    rng = np.random.default_rng(seed)
    direction = rng.normal(size=dimensions)
    direction /= np.linalg.norm(direction)
    nuisance_seed = rng.normal(size=(dimensions, dimensions - 1))
    nuisance_seed -= direction[:, None] * (direction @ nuisance_seed)[None, :]
    nuisance_basis, _ = np.linalg.qr(nuisance_seed)
    vectors = np.empty((authors, segments_per_author, dimensions))
    nuisance = np.empty((authors, segments_per_author, 3))
    causal = np.zeros((authors, segments_per_author), dtype=bool)
    strengths = np.zeros((authors, segments_per_author))
    for author in range(authors):
        selected = rng.choice(segments_per_author, size=causal_segments, replace=False)
        if not null:
            causal[author, selected] = True
            strengths[author, selected] = rng.uniform(0.8, 1.4, size=causal_segments)
        local_nuisance = rng.normal(size=(segments_per_author, 3))
        nuisance[author] = local_nuisance
        nuisance_weights = rng.normal(scale=0.55, size=(segments_per_author, dimensions - 1))
        orthogonal = nuisance_weights @ nuisance_basis.T
        vectors[author] = (
            strengths[author, :, None] * direction[None, :]
            + orthogonal
            + rng.normal(scale=0.08, size=(segments_per_author, dimensions))
        )
    return {
        "direction": direction,
        "vectors": vectors,
        "nuisance": nuisance,
        "causal": causal,
        "strengths": strengths,
    }


def _matched_random_indices(
    nuisance: np.ndarray,
    selected: np.ndarray,
    *,
    eligible: np.ndarray,
) -> np.ndarray:
    """Match each evidence span to a distinct nuisance-near control span."""
    remaining = set(map(int, np.flatnonzero(eligible)))
    matched: list[int] = []
    for index in map(int, selected):
        if not remaining:
            break
        candidates = np.asarray(sorted(remaining), dtype=int)
        chosen = int(candidates[np.argmin(np.linalg.norm(nuisance[candidates] - nuisance[index], axis=1))])
        matched.append(chosen)
        remaining.remove(chosen)
    return np.asarray(matched, dtype=int)


def evaluate_evidence_fidelity(
    world: dict[str, Any],
    *,
    seed: int,
    select_count: int = 4,
    bootstrap_draws: int = 2000,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Evaluate planted recovery, necessity, sufficiency, and perturbations."""
    vectors = np.asarray(world["vectors"], dtype=float)
    nuisance = np.asarray(world["nuisance"], dtype=float)
    causal = np.asarray(world["causal"], dtype=bool)
    direction = np.asarray(world["direction"], dtype=float)
    rng = np.random.default_rng(seed)
    rows: list[dict[str, Any]] = []
    for author in range(len(vectors)):
        contributions = local_direction_traversal(vectors[author], direction)
        selected = np.argsort(-contributions, kind="stable")[: int(select_count)]
        eligible = np.ones(len(selected) + (len(vectors[author]) - len(selected)), dtype=bool)
        eligible[selected] = False
        matched = _matched_random_indices(nuisance[author], selected, eligible=eligible)
        evidence_true = causal[author, selected]
        total_causal = int(causal[author].sum())
        precision = float(evidence_true.mean()) if len(selected) else 0.0
        recall = float(evidence_true.sum() / total_causal) if total_causal else 0.0
        selected_effect = occlusion_effect(vectors[author], selected, direction=direction)
        random_effect = occlusion_effect(vectors[author], matched, direction=direction)
        full = score_segments(vectors[author], direction=direction)
        evidence_only = score_segments(
            vectors[author, selected], direction=direction, denominator=len(vectors[author])
        )
        sem = float(np.std(contributions, ddof=1) / np.sqrt(len(contributions)))
        stable_denominator = abs(full) >= 1.96 * max(sem, 1e-12)
        sufficiency = float(evidence_only / full) if stable_denominator else np.nan
        # Harmless paraphrase moves only in the orthogonal complement.
        perturbation = rng.normal(scale=0.12, size=vectors[author].shape)
        perturbation -= np.outer(perturbation @ direction, direction)
        paraphrased = vectors[author] + perturbation
        paraphrase_change_sem = abs(
            score_segments(paraphrased, direction=direction) - full
        ) / max(sem, 1e-12)
        flipped = vectors[author] - 2.0 * world["strengths"][author, :, None] * direction[None, :]
        flip_delta_sem = abs(score_segments(flipped, direction=direction) - full) / max(sem, 1e-12)
        rows.append({
            "author_index": author,
            "evidence_precision": precision,
            "evidence_recall": recall,
            "necessity_advantage": float(selected_effect - random_effect),
            "selected_effect": float(selected_effect),
            "matched_random_effect": float(random_effect),
            "sufficiency_ratio": sufficiency,
            "stable_denominator": bool(stable_denominator),
            "paraphrase_change_sem": float(paraphrase_change_sem),
            "mechanism_flip_delta_sem": float(flip_delta_sem),
            "mechanism_flip_detected": bool(flip_delta_sem >= 1.96),
        })
    precision = bootstrap_mean_ci(
        np.asarray([row["evidence_precision"] for row in rows]), seed=seed + 1, draws=bootstrap_draws
    )
    recall = bootstrap_mean_ci(
        np.asarray([row["evidence_recall"] for row in rows]), seed=seed + 2, draws=bootstrap_draws
    )
    necessity = bootstrap_mean_ci(
        np.asarray([row["necessity_advantage"] for row in rows]), seed=seed + 3, draws=bootstrap_draws
    )
    sufficiency = bootstrap_mean_ci(
        np.asarray([row["sufficiency_ratio"] for row in rows]), seed=seed + 4, draws=bootstrap_draws
    )
    summary = {
        "evidence_precision_mean": precision[0],
        "evidence_precision_ci_lower": precision[1],
        "evidence_precision_ci_upper": precision[2],
        "evidence_recall_mean": recall[0],
        "evidence_recall_ci_lower": recall[1],
        "evidence_recall_ci_upper": recall[2],
        "necessity_advantage_mean": necessity[0],
        "necessity_advantage_ci_lower": necessity[1],
        "necessity_advantage_ci_upper": necessity[2],
        "sufficiency_ratio_mean": sufficiency[0],
        "sufficiency_ratio_ci_lower": sufficiency[1],
        "sufficiency_ratio_ci_upper": sufficiency[2],
        "sufficiency_ratio_median": float(np.nanmedian([row["sufficiency_ratio"] for row in rows])),
        "paraphrase_change_sem_q95": float(np.quantile([row["paraphrase_change_sem"] for row in rows], 0.95)),
        "mechanism_flip_detection_rate": float(np.mean([row["mechanism_flip_detected"] for row in rows])),
        "uncertainty_refusal_rate": float(np.mean([not row["stable_denominator"] for row in rows])),
    }
    return summary, rows


def write_evidence_artifact(
    path: str | Path,
    *,
    source_span_ids: list[str],
    measurements: dict[str, float | str | bool],
) -> str:
    """Write an identifier-free evidence artifact and return its SHA-256."""
    payload = {
        "source_spans": {
            str(span_id): {"present": True}
            for span_id in source_span_ids
        },
        "measurements": {
            str(field): {"value": value}
            for field, value in measurements.items()
        },
    }
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return hashlib.sha256(destination.read_bytes()).hexdigest()


def evidence_node(
    *,
    node_id: str,
    kind: str,
    artifact_path: str,
    artifact_hash: str,
    source_span_ids: list[str],
    measurement_field: str,
    observed_value: float | str | bool,
) -> dict[str, Any]:
    """Create one canonical typed EvidenceGraph node."""
    node = {
        "node_id": node_id,
        "kind": kind,
        "artifact_path": artifact_path,
        "artifact_hash": artifact_hash,
        "source_span_ids": source_span_ids,
        "measurement_field": measurement_field,
        "observed_value": observed_value,
    }
    node["node_sha256"] = canonical_sha256(node)
    return node


def validate_evidence_graph(
    graph: dict[str, dict[str, Any]],
    *,
    repository_root: str | Path,
) -> list[str]:
    """Return closed-chain errors for a technical EvidenceGraph candidate."""
    errors: list[str] = []
    root = Path(repository_root).resolve()
    required = {
        "node_id", "kind", "artifact_path", "artifact_hash", "source_span_ids",
        "measurement_field", "observed_value", "node_sha256",
    }
    for key, node in graph.items():
        if set(node) != required or node.get("node_id") != key:
            errors.append(f"{key}:typed_node_invalid")
            continue
        if node.get("kind") not in {"supporting", "counterevidence"}:
            errors.append(f"{key}:kind_invalid")
        expected_node_hash = canonical_sha256(node, omit_keys={"node_sha256"})
        if node.get("node_sha256") != expected_node_hash:
            errors.append(f"{key}:node_hash_mismatch")
        try:
            artifact = (root / str(node["artifact_path"])).resolve()
            artifact.relative_to(root)
            observed_hash = hashlib.sha256(artifact.read_bytes()).hexdigest()
            payload = json.loads(artifact.read_text(encoding="utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            errors.append(f"{key}:artifact_unresolved")
            continue
        if observed_hash != node.get("artifact_hash"):
            errors.append(f"{key}:artifact_hash_mismatch")
        spans = payload.get("source_spans", {})
        if any(str(span) not in spans for span in node.get("source_span_ids", [])):
            errors.append(f"{key}:source_span_unresolved")
        record = payload.get("measurements", {}).get(str(node.get("measurement_field")))
        if not isinstance(record, dict) or record.get("value") != node.get("observed_value"):
            errors.append(f"{key}:measurement_mismatch")
    return errors
