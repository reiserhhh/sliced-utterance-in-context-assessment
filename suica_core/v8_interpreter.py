"""Evidence-bound, non-scoring LLM interpreter utilities for SUICA V8."""
from __future__ import annotations

from itertools import combinations
from copy import deepcopy
import hashlib
import json
import re
import time
from typing import Any, Callable

import jsonschema
import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score, roc_auc_score

from .v8_contracts import strict_json_loads
from .v8_semantic import SemanticProvider, SemanticTransducerSpec


BEHAVIOR_CODES = frozenset({
    "discourse_stance",
    "affect_expression",
    "self_reference",
    "directive_expression",
    "novelty_expression",
    "interaction_response",
})

FORBIDDEN_INTERPRETATION_RE = re.compile(
    r"\b(?:big\s*five|mbti|personality\s+(?:trait|type)|diagnos(?:is|e|tic)|"
    r"disorder|patholog(?:y|ical)|clinical\s+severity)\b",
    re.IGNORECASE,
)


def _structured_error_detail(exc: Exception) -> str:
    """Keep validator location and rule without serializing a large instance."""
    if isinstance(exc, jsonschema.ValidationError):
        return json.dumps(
            {
                "validator": exc.validator,
                "validator_value": exc.validator_value,
                "path": list(exc.absolute_path),
                "schema_path": list(exc.absolute_schema_path),
                "message_tail": exc.message[-300:],
            },
            ensure_ascii=False,
            default=str,
            separators=(",", ":"),
        )[:1000]
    return str(exc)[:500]


def normalize_behavior_bookkeeping(
    payload: Any,
) -> tuple[Any, dict[str, int]]:
    """Normalize IDs and redundant abstention markers without adding semantics."""
    audit = {
        "canonicalized_event_ids": 0,
        "merged_duplicate_events": 0,
        "dropped_abstain_markers": 0,
        "corrected_abstain_flags": 0,
    }
    if not isinstance(payload, dict) or not isinstance(payload.get("profiles"), list):
        return payload, audit
    normalized = deepcopy(payload)
    for profile in normalized["profiles"]:
        if not isinstance(profile, dict) or not isinstance(profile.get("events"), list):
            continue
        merged: dict[tuple[str, str], dict[str, Any]] = {}
        passthrough: list[Any] = []
        for event in profile["events"]:
            if not isinstance(event, dict):
                passthrough.append(event)
                continue
            segment_id = str(event.get("segment_id", ""))
            event_code = str(event.get("event_code", ""))
            if event_code == "abstain":
                audit["dropped_abstain_markers"] += 1
                continue
            if not segment_id or event_code not in BEHAVIOR_CODES:
                passthrough.append(event)
                continue
            canonical_id = f"{segment_id}::{event_code}"
            if str(event.get("event_id", "")) != canonical_id:
                audit["canonicalized_event_ids"] += 1
            clean = dict(event)
            clean["event_id"] = canonical_id
            key = (segment_id, event_code)
            if key in merged:
                audit["merged_duplicate_events"] += 1
                existing = list(map(str, merged[key].get("evidence_span_ids", [])))
                incoming = list(map(str, clean.get("evidence_span_ids", [])))
                merged[key]["evidence_span_ids"] = sorted(set(existing + incoming))
            else:
                merged[key] = clean
        profile["events"] = passthrough + list(merged.values())
        expected_abstain = len(profile["events"]) == 0
        if profile.get("abstain") is not expected_abstain:
            audit["corrected_abstain_flags"] += 1
        profile["abstain"] = expected_abstain
    return normalized, audit


def validate_behavior_payload(
    payload: Any,
    *,
    schema: dict[str, Any],
    expected_profiles: set[str],
    spans_by_segment: dict[str, set[str]],
    segments_by_profile: dict[str, set[str]],
    return_audit: bool = False,
) -> dict[str, Any] | tuple[dict[str, Any], dict[str, int]]:
    """Validate discrete behavior events and their exact source bindings."""
    payload, audit = normalize_behavior_bookkeeping(payload)
    jsonschema.Draft202012Validator(schema).validate(payload)
    profiles = payload["profiles"]
    observed_profiles = [str(row["profile_id"]) for row in profiles]
    if set(observed_profiles) != expected_profiles or len(observed_profiles) != len(
        expected_profiles
    ):
        raise ValueError("behavior output must contain every expected profile exactly once")
    event_ids: set[str] = set()
    for profile in profiles:
        profile_id = str(profile["profile_id"])
        known_segments = segments_by_profile.get(profile_id, set())
        events = profile["events"]
        if bool(profile["abstain"]) != (len(events) == 0):
            raise ValueError("behavior abstain flag must match an empty event list")
        per_segment_code: set[tuple[str, str]] = set()
        for event in events:
            event_id = str(event["event_id"])
            segment_id = str(event["segment_id"])
            event_code = str(event["event_code"])
            if event_id in event_ids:
                raise ValueError("behavior event_id values must be globally unique")
            if event_code not in BEHAVIOR_CODES:
                raise ValueError("unknown behavior event code")
            if segment_id not in spans_by_segment:
                raise ValueError("behavior event references an unknown segment")
            if segment_id not in known_segments:
                raise ValueError("behavior event crosses a profile boundary")
            if event_id != f"{segment_id}::{event_code}":
                raise ValueError("behavior event_id must be segment_id::event_code")
            cited = set(map(str, event["evidence_span_ids"]))
            if not cited.issubset(spans_by_segment[segment_id]):
                raise ValueError("behavior evidence crosses a segment boundary")
            key = (segment_id, event_code)
            if key in per_segment_code:
                raise ValueError("duplicate behavior code within one segment")
            per_segment_code.add(key)
            event_ids.add(event_id)
    return (payload, audit) if return_audit else payload


def validate_interpretation_payload(
    payload: Any,
    *,
    schema: dict[str, Any],
    expected_profiles: set[str],
    event_ids_by_profile: dict[str, set[str]],
    event_codes_by_profile: dict[str, dict[str, str]],
    registered_links_by_profile: dict[str, set[tuple[str, str]]],
    candidate_atoms_by_profile: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    """Validate bounded hypotheses without accepting person-level scores."""
    jsonschema.Draft202012Validator(schema).validate(payload)
    profiles = payload["profiles"]
    observed_profiles = [str(row["profile_id"]) for row in profiles]
    if set(observed_profiles) != expected_profiles or len(observed_profiles) != len(
        expected_profiles
    ):
        raise ValueError("interpretation output must contain every profile exactly once")
    for profile in profiles:
        profile_id = str(profile["profile_id"])
        known = event_ids_by_profile.get(profile_id, set())
        event_codes = event_codes_by_profile.get(profile_id, {})
        registered = registered_links_by_profile.get(profile_id, set())
        candidates = candidate_atoms_by_profile.get(profile_id, {})
        atom_ids: set[str] = set()
        for atom in profile["interpretation_atoms"]:
            atom_id = str(atom["atom_id"])
            if atom_id in atom_ids:
                raise ValueError("interpretation atom_id values must be unique")
            candidate = candidates.get(atom_id)
            if candidate is None:
                raise ValueError("interpretation atom is not a supplied candidate")
            dimensions = list(map(str, atom["target_dimension_ids"]))
            if not dimensions or len(dimensions) != len(set(dimensions)):
                raise ValueError("interpretation atoms require unique target dimensions")
            if set(dimensions) != set(map(str, candidate["target_dimension_ids"])):
                raise ValueError("interpretation atom changes candidate dimensions")
            cited = set(map(str, atom["evidence_event_ids"]))
            counter = set(map(str, atom["counterevidence_event_ids"]))
            if not cited.issubset(known) or not counter.issubset(known):
                raise ValueError("interpretation references an unknown behavior event")
            if cited.intersection(counter):
                raise ValueError("support and counterevidence must be disjoint")
            if not cited.issubset(set(map(str, candidate["evidence_event_ids"]))):
                raise ValueError("interpretation atom cites evidence outside its candidate")
            for field in ("scope", "relation", "direction"):
                if str(atom[field]) != str(candidate[field]):
                    raise ValueError(f"interpretation atom changes candidate {field}")
            for dimension in dimensions:
                if not any(
                    (dimension, event_codes.get(event_id, "")) in registered
                    for event_id in cited
                ):
                    raise ValueError(
                        "interpretation atom lacks a registered dimension-event link"
                    )
            atom_ids.add(atom_id)
        has_atoms = bool(profile["interpretation_atoms"])
        if profile["assessment_status"] == "insufficient_support":
            if has_atoms:
                raise ValueError("insufficient-support interpretation cannot contain atoms")
            if not profile["refusal_codes"]:
                raise ValueError("insufficient-support interpretation requires a refusal code")
        elif not has_atoms:
            raise ValueError("interpreted status requires at least one atom")
        elif profile["refusal_codes"]:
            raise ValueError("interpreted status cannot contain refusal codes")
    return payload


def validate_critique_payload(
    payload: Any,
    *,
    schema: dict[str, Any],
    expected_profiles: set[str],
    atom_ids_by_profile: dict[str, set[str]],
) -> dict[str, Any]:
    """Validate critic decisions against the submitted hypothesis set."""
    jsonschema.Draft202012Validator(schema).validate(payload)
    profiles = payload["profiles"]
    observed_profiles = [str(row["profile_id"]) for row in profiles]
    if set(observed_profiles) != expected_profiles or len(observed_profiles) != len(
        expected_profiles
    ):
        raise ValueError("critique output must contain every profile exactly once")
    for profile in profiles:
        profile_id = str(profile["profile_id"])
        known = atom_ids_by_profile.get(profile_id, set())
        observed: set[str] = set()
        for atom in profile["atom_verdicts"]:
            atom_id = str(atom["atom_id"])
            if atom_id not in known or atom_id in observed:
                raise ValueError("critic must judge every submitted atom at most once")
            observed.add(atom_id)
        if observed != known:
            raise ValueError("critic must judge every submitted atom exactly once")
    return payload


def run_structured_stage(
    provider: SemanticProvider,
    spec: SemanticTransducerSpec,
    payload: dict[str, Any],
    *,
    run_id: str,
    validator: Callable[[Any], dict[str, Any]],
) -> dict[str, Any]:
    """Run one schema-constrained stage and return output or explicit refusal."""
    user_payload = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    started = time.perf_counter()
    ledger: dict[str, Any] = {
        "run_id": str(run_id),
        "runtime": spec.public_runtime(),
        "input_sha256": hashlib.sha256(user_payload.encode("utf-8")).hexdigest(),
    }
    attempt_history: list[dict[str, Any]] = []
    last_error: Exception | None = None
    try:
        for validation_attempt in range(max(1, int(spec.max_validation_retries))):
            raw: str | None = None
            metadata: dict[str, Any] | None = None
            try:
                raw, metadata = provider.complete(spec=spec, user_payload=user_payload)
                raw_sha256 = hashlib.sha256(raw.encode("utf-8")).hexdigest()
                validated = validator(strict_json_loads(raw))
                validator_metadata: dict[str, Any] = {}
                if (
                    isinstance(validated, tuple)
                    and len(validated) == 2
                    and isinstance(validated[0], dict)
                    and isinstance(validated[1], dict)
                ):
                    output, validator_metadata = validated
                else:
                    output = validated
                attempt_history.append({
                    "validation_attempt": validation_attempt + 1,
                    "raw_response_sha256": raw_sha256,
                    "provider_metadata": metadata,
                    "validator_metadata": validator_metadata,
                    "status": "VALID",
                })
                ledger["provider_metadata"] = metadata
                ledger["raw_response_sha256"] = raw_sha256
                ledger["validation_attempts"] = validation_attempt + 1
                ledger["validator_metadata"] = validator_metadata
                ledger["attempt_history"] = attempt_history
                ledger["status"] = "STRUCTURED_STAGE_READY"
                ledger["refusal_codes"] = []
                return {"status": ledger["status"], "output": output, "ledger": ledger}
            except Exception as exc:
                last_error = exc
                attempt = {
                    "validation_attempt": validation_attempt + 1,
                    "status": "INVALID",
                    "error_type": type(exc).__name__,
                    "error_detail": _structured_error_detail(exc),
                }
                if metadata is not None:
                    attempt["provider_metadata"] = metadata
                if raw is not None:
                    attempt["raw_response_sha256"] = hashlib.sha256(
                        raw.encode("utf-8")
                    ).hexdigest()
                attempt_history.append(attempt)
        exc = last_error or RuntimeError("structured stage failed without an error")
        ledger["status"] = "REFUSE_STRUCTURED_STAGE"
        ledger["refusal_codes"] = [type(exc).__name__]
        ledger["error_detail"] = _structured_error_detail(exc)
        ledger["validation_attempts"] = len(attempt_history)
        ledger["attempt_history"] = attempt_history
        return {"status": ledger["status"], "output": None, "ledger": ledger}
    finally:
        ledger["latency_seconds"] = float(time.perf_counter() - started)


def set_jaccard(first: set[str], second: set[str]) -> float:
    """Return Jaccard agreement, treating two empty sets as exact agreement."""
    union = first.union(second)
    return float(len(first.intersection(second)) / len(union)) if union else 1.0


def mean_pairwise_jaccard(runs: list[set[str]]) -> float:
    """Average all repeated-run set agreements."""
    if len(runs) < 2:
        return float("nan")
    return float(np.mean([set_jaccard(left, right) for left, right in combinations(runs, 2)]))


def fleiss_kappa_multilabel(
    runs_by_profile: dict[str, list[set[str]]],
    *,
    universe: set[str],
) -> float:
    """Treat each profile-code presence as one binary item across repeated runs."""
    items: list[tuple[int, int]] = []
    rater_count: int | None = None
    for runs in runs_by_profile.values():
        if rater_count is None:
            rater_count = len(runs)
        if len(runs) != rater_count:
            raise ValueError("every profile must have the same number of repeated runs")
        for code in sorted(universe):
            present = sum(code in run for run in runs)
            items.append((int(rater_count - present), int(present)))
    if not items or not rater_count or rater_count < 2:
        return float("nan")
    counts = np.asarray(items, dtype=float)
    observed = np.mean(
        (np.sum(counts**2, axis=1) - rater_count)
        / (rater_count * (rater_count - 1))
    )
    proportions = counts.sum(axis=0) / counts.sum()
    expected = float(np.sum(proportions**2))
    return float((observed - expected) / (1.0 - expected)) if expected < 1.0 else float("nan")


def consensus_set(runs: list[set[str]], *, minimum_fraction: float = 0.5) -> set[str]:
    """Return deterministic repeated-run majority labels."""
    if not runs or not 0.0 < float(minimum_fraction) <= 1.0:
        return set()
    counts: dict[str, int] = {}
    for run in runs:
        for value in run:
            counts[value] = counts.get(value, 0) + 1
    threshold = int(np.ceil(float(minimum_fraction) * len(runs)))
    return {value for value, count in counts.items() if count >= threshold}


def interpretation_atom_key(atom: dict[str, Any]) -> str:
    """Canonicalize an interpretation atom without its generated wording or ID."""
    dimensions = ",".join(sorted(map(str, atom["target_dimension_ids"])))
    return "|".join([
        dimensions,
        str(atom["scope"]),
        str(atom["relation"]),
        str(atom["direction"]),
        str(atom["qualifier"]),
    ])


def evidence_edge_set(profile: dict[str, Any]) -> set[str]:
    """Return canonical atom-to-evidence and atom-to-counterevidence edges."""
    edges: set[str] = set()
    for atom in profile.get("interpretation_atoms", []):
        atom_key = interpretation_atom_key(atom)
        edges.update(
            f"{atom_key}|support|{event_id}"
            for event_id in map(str, atom["evidence_event_ids"])
        )
        edges.update(
            f"{atom_key}|counter|{event_id}"
            for event_id in map(str, atom["counterevidence_event_ids"])
        )
    return edges


def idf_weights(document_sets: list[set[str]]) -> dict[str, float]:
    """Fit interpretation-atom IDF weights on discovery outputs only."""
    count = len(document_sets)
    vocabulary = set().union(*document_sets) if document_sets else set()
    return {
        value: float(1.0 + np.log((count + 1) / (1 + sum(value in row for row in document_sets))))
        for value in vocabulary
    }


def weighted_jaccard(
    first: set[str],
    second: set[str],
    *,
    weights: dict[str, float],
) -> float:
    """Return IDF-weighted set agreement with unit weight for unseen atoms."""
    union = first.union(second)
    if not union:
        return 1.0
    numerator = sum(weights.get(value, 1.0) for value in first.intersection(second))
    denominator = sum(weights.get(value, 1.0) for value in union)
    return float(numerator / denominator)


def set_f1(first: set[str], second: set[str]) -> float:
    """Return symmetric set F1, treating two empty sets as exact agreement."""
    if not first and not second:
        return 1.0
    denominator = len(first) + len(second)
    return float(2 * len(first.intersection(second)) / denominator) if denominator else 1.0


def mean_pairwise_weighted_jaccard(
    runs: list[set[str]],
    *,
    weights: dict[str, float],
) -> float:
    """Average IDF-weighted agreement across repeated interpretation runs."""
    if len(runs) < 2:
        return float("nan")
    return float(np.mean([
        weighted_jaccard(left, right, weights=weights)
        for left, right in combinations(runs, 2)
    ]))


def mean_pairwise_set_f1(runs: list[set[str]]) -> float:
    """Average symmetric set F1 across repeated runs."""
    if len(runs) < 2:
        return float("nan")
    return float(np.mean([set_f1(left, right) for left, right in combinations(runs, 2)]))


def pairwise_nominal_kappa(runs: list[dict[str, str]]) -> float:
    """Average nominal Cohen kappa across repeated per-item classifications."""
    if len(runs) < 2:
        return float("nan")
    keys = sorted(set().union(*(set(run) for run in runs)))
    if not keys:
        return 1.0
    kappas: list[float] = []
    for left, right in combinations(runs, 2):
        labels_left = [left.get(key, "<missing>") for key in keys]
        labels_right = [right.get(key, "<missing>") for key in keys]
        if labels_left == labels_right and len(set(labels_left)) == 1:
            kappas.append(1.0)
            continue
        value = float(cohen_kappa_score(labels_left, labels_right))
        if np.isfinite(value):
            kappas.append(value)
        elif labels_left == labels_right:
            kappas.append(1.0)
    return float(np.mean(kappas)) if kappas else float("nan")


def bootstrap_mean_interval(
    values: np.ndarray | list[float],
    *,
    draws: int,
    seed: int,
) -> tuple[float, float, float]:
    """Return mean and percentile bootstrap interval over independent profiles."""
    vector = np.asarray(values, dtype=float)
    vector = vector[np.isfinite(vector)]
    if not len(vector):
        return float("nan"), float("nan"), float("nan")
    if len(vector) == 1:
        value = float(vector[0])
        return value, value, value
    rng = np.random.default_rng(seed)
    samples = vector[rng.integers(0, len(vector), size=(int(draws), len(vector)))]
    means = samples.mean(axis=1)
    return (
        float(vector.mean()),
        float(np.quantile(means, 0.025)),
        float(np.quantile(means, 0.975)),
    )


def interpretation_forbidden_count(payload: dict[str, Any]) -> int:
    """Count prohibited psychological/clinical language in rendered sentences."""
    count = 0
    for profile in payload.get("profiles", []):
        for atom in profile.get("interpretation_atoms", []):
            sentence = str(atom.get("human_readable_sentence", ""))
            count += len(FORBIDDEN_INTERPRETATION_RE.findall(sentence))
    return int(count)


def geometry_interpretation_alignment(
    geometry: np.ndarray,
    interpretation_sets: list[set[str]],
    *,
    neighbor_count: int = 3,
    permutations: int = 1000,
    seed: int = 20260724,
) -> dict[str, float]:
    """Compare anonymous SUICA proximity with bounded interpretation proximity."""
    values = np.asarray(geometry, dtype=float)
    if values.ndim != 2 or len(values) != len(interpretation_sets) or len(values) < 8:
        raise ValueError("geometry and interpretation sets must align for >=8 profiles")
    normalized = values / np.maximum(np.linalg.norm(values, axis=1, keepdims=True), 1e-12)
    geometry_distance = 1.0 - normalized @ normalized.T
    interpretation_distance = np.zeros_like(geometry_distance)
    for left in range(len(values)):
        for right in range(left + 1, len(values)):
            distance = 1.0 - set_jaccard(
                interpretation_sets[left],
                interpretation_sets[right],
            )
            interpretation_distance[left, right] = interpretation_distance[right, left] = distance
    upper = np.triu_indices(len(values), k=1)
    alignment = float(spearmanr(
        geometry_distance[upper],
        interpretation_distance[upper],
    ).statistic)
    scores: list[float] = []
    labels: list[int] = []
    count = min(int(neighbor_count), (len(values) - 1) // 2)
    for index in range(len(values)):
        order = np.argsort(geometry_distance[index], kind="stable")
        order = order[order != index]
        for neighbor in order[:count]:
            labels.append(1)
            scores.append(1.0 - interpretation_distance[index, neighbor])
        for distant in order[-count:]:
            labels.append(0)
            scores.append(1.0 - interpretation_distance[index, distant])
    auc = float(roc_auc_score(labels, scores))
    rng = np.random.default_rng(seed)
    null = np.empty(int(permutations), dtype=float)
    for replicate in range(int(permutations)):
        shuffled = rng.permutation(len(values))
        null[replicate] = spearmanr(
            geometry_distance[upper],
            interpretation_distance[np.ix_(shuffled, shuffled)][upper],
        ).statistic
    p_value = float((1 + np.sum(null >= alignment)) / (len(null) + 1))
    return {
        "distance_spearman": alignment,
        "neighbor_similarity_auc": auc,
        "permutation_p": p_value,
        "null_q95": float(np.quantile(null, 0.95)),
    }
