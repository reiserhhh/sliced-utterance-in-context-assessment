#!/usr/bin/env python3
"""Run the SUICA V8 evidence-bound interpreter stability experiments."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    append_ledger_event,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_interpreter import (  # noqa: E402
    BEHAVIOR_CODES,
    bootstrap_mean_interval,
    consensus_set,
    evidence_edge_set,
    fleiss_kappa_multilabel,
    geometry_interpretation_alignment,
    idf_weights,
    interpretation_atom_key,
    interpretation_forbidden_count,
    mean_pairwise_set_f1,
    mean_pairwise_weighted_jaccard,
    pairwise_nominal_kappa,
    run_structured_stage,
    set_f1,
    set_jaccard,
    validate_behavior_payload,
    validate_critique_payload,
    validate_interpretation_payload,
)
from suica_core.v8_semantic import (  # noqa: E402
    OpenAICompatibleProvider,
    SemanticProvider,
    SemanticTransducerSpec,
    load_semantic_spec,
)


EVENT_ORDER = (
    "discourse_stance",
    "affect_expression",
    "self_reference",
    "directive_expression",
    "novelty_expression",
    "interaction_response",
)

EVENT_SENTENCES = {
    "discourse_stance": (
        "I think this approach is preferable, although I would revise it if the evidence changes.",
        "My position is that this option is workable, but I do not treat it as certain.",
        "I reject that conclusion because the stated premise does not support it.",
        "I accept the proposal with one qualification about how it will be applied.",
    ),
    "affect_expression": (
        "I feel relieved that the immediate problem has become manageable.",
        "I am frustrated by how abruptly the plan changed.",
        "This outcome makes me uneasy even though the practical risk is small.",
        "I feel encouraged by the progress we made.",
    ),
    "self_reference": (
        "I noticed that I usually pause before I commit to a decision.",
        "I changed my own plan after checking the evidence again.",
        "I am trying to separate what I know from what I merely expect.",
        "I tend to write down the alternatives before choosing one.",
    ),
    "directive_expression": (
        "Please compare the two options before changing the implementation.",
        "We should verify the source and record the result before proceeding.",
        "Try the smaller test first, then expand only if it passes.",
        "The next step must preserve the existing evidence trail.",
    ),
    "novelty_expression": (
        "Another possibility is to reverse the order and test the assumption from the opposite side.",
        "We could combine the two views instead of choosing either one.",
        "A less conventional option would be to model the transition rather than the endpoint.",
        "I want to explore an alternative that is not part of the current template.",
    ),
    "interaction_response": (
        "Your objection changes my view, so I will narrow the claim.",
        "I understand the suggestion, but I disagree with the proposed reason.",
        "That clarification resolves my earlier misunderstanding.",
        "I will adapt the plan to the constraint you just introduced.",
    ),
}

NEUTRAL_SENTENCES = (
    "The document contains several sections and a short appendix.",
    "The meeting is scheduled for the afternoon in the same room.",
    "The file was created after the earlier version and before the archive.",
    "The table lists the entries in chronological order.",
)


def _source_env(path: Path) -> None:
    """Load a simple dotenv file without logging secret values."""
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'").strip('"'))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _sigmoid(value: float) -> float:
    return float(1.0 / (1.0 + np.exp(-value)))


def _band(value: float) -> str:
    if value >= 0.45:
        return "upper_reference_band"
    if value <= -0.45:
        return "lower_reference_band"
    return "central_reference_band"


def _planted_profiles(
    *,
    count: int,
    segments_per_profile: int,
    seed: int,
) -> list[dict[str, Any]]:
    """Generate planted score/event relations without psychological labels."""
    rng = np.random.default_rng(seed)
    latent = rng.normal(size=(count, len(EVENT_ORDER)))
    profiles: list[dict[str, Any]] = []
    for profile_index in range(count):
        profile_id = f"PLANTED-{profile_index:04d}"
        dimensions = []
        registered_links = []
        for dimension_index, event_code in enumerate(EVENT_ORDER):
            value = float(latent[profile_index, dimension_index])
            dimensions.append({
                "dimension_id": f"D{dimension_index + 1:03d}",
                "reference_band": _band(value),
                "uncertainty_band": (
                    "clear" if abs(value) >= 0.70 else
                    "borderline" if abs(value) >= 0.35 else
                    "central"
                ),
                "support_status": "supported",
            })
            registered_links.append({
                "dimension_id": f"D{dimension_index + 1:03d}",
                "event_code": event_code,
                "association_direction": "positive",
                "registration_source": "planted_discovery_contract",
                "upper_band_event_rate_minimum": 0.50,
            })

        segments: list[dict[str, Any]] = []
        expected_events: set[str] = set()
        event_counts = {code: 0 for code in EVENT_ORDER}
        for segment_index in range(segments_per_profile):
            segment_id = f"{profile_id}-S{segment_index:02d}"
            selected: list[str] = []
            for dimension_index, event_code in enumerate(EVENT_ORDER):
                probability = _sigmoid(
                    -1.15 + 1.35 * latent[profile_index, dimension_index]
                    + 0.12 * np.sin(segment_index + dimension_index)
                )
                if rng.random() < probability:
                    selected.append(event_code)
            if len(selected) > 3:
                ranks = sorted(
                    selected,
                    key=lambda code: latent[profile_index, EVENT_ORDER.index(code)],
                    reverse=True,
                )
                selected = ranks[:3]
            spans: list[dict[str, str]] = []
            if selected:
                for span_index, event_code in enumerate(selected):
                    sentence_index = (
                        profile_index + segment_index + EVENT_ORDER.index(event_code)
                    ) % len(EVENT_SENTENCES[event_code])
                    span_id = f"{segment_id}-X{span_index:02d}"
                    spans.append({
                        "span_id": span_id,
                        "text": EVENT_SENTENCES[event_code][sentence_index],
                    })
                    expected_events.add(f"{segment_id}::{event_code}")
                    event_counts[event_code] += 1
            else:
                spans.append({
                    "span_id": f"{segment_id}-X00",
                    "text": NEUTRAL_SENTENCES[
                        (profile_index + segment_index) % len(NEUTRAL_SENTENCES)
                    ],
                })
            segments.append({"segment_id": segment_id, "spans": spans})

        eligible_targets = [
            code for code in EVENT_ORDER
            if event_counts[code] >= 2
            and latent[profile_index, EVENT_ORDER.index(code)] >= 0.45
        ]
        if not eligible_targets:
            eligible_targets = [
                code for code in EVENT_ORDER if event_counts[code] >= 1
            ]
        target_code = max(
            eligible_targets,
            key=lambda code: (
                latent[profile_index, EVENT_ORDER.index(code)],
                event_counts[code],
            ),
            default="",
        )
        profiles.append({
            "profile_id": profile_id,
            "segments": segments,
            "suica_packet": {
                "reference_population_id": "PLANTED-REF-V8-I1",
                "measurement_channel": "frozen_suica",
                "overall_support": "supported",
                "dimensions": dimensions,
            },
            "registered_links": registered_links,
            "expected_events": sorted(expected_events),
            "target_event_code": target_code,
            "target_dimension_id": (
                f"D{EVENT_ORDER.index(target_code) + 1:03d}" if target_code else ""
            ),
            "latent": latent[profile_index].tolist(),
        })
    return profiles


def _observer_payload(
    profiles: list[dict[str, Any]],
    *,
    irrelevant_note: bool = False,
) -> dict[str, Any]:
    rows = []
    for profile in profiles:
        row = {
            "profile_id": profile["profile_id"],
            "segments": profile["segments"],
        }
        if irrelevant_note:
            row["collection_note"] = "Anonymous material; order has no interpretive meaning."
        rows.append(row)
    return {
        "task": "Code explicit behavior events from every supplied profile.",
        "profiles": rows,
    }


def _behavior_validation_context(
    profiles: list[dict[str, Any]],
) -> tuple[set[str], dict[str, set[str]], dict[str, set[str]]]:
    expected_profiles = {str(profile["profile_id"]) for profile in profiles}
    spans_by_segment: dict[str, set[str]] = {}
    segments_by_profile: dict[str, set[str]] = {}
    for profile in profiles:
        profile_id = str(profile["profile_id"])
        segments_by_profile[profile_id] = set()
        for segment in profile["segments"]:
            segment_id = str(segment["segment_id"])
            segments_by_profile[profile_id].add(segment_id)
            spans_by_segment[segment_id] = {
                str(span["span_id"]) for span in segment["spans"]
            }
    return expected_profiles, spans_by_segment, segments_by_profile


def _events_by_profile(payload: dict[str, Any] | None) -> dict[str, list[dict[str, Any]]]:
    if not payload:
        return {}
    return {
        str(profile["profile_id"]): list(profile["events"])
        for profile in payload["profiles"]
    }


def _event_summary(
    events: list[dict[str, Any]],
    *,
    segments_per_profile: int,
) -> list[dict[str, Any]]:
    rows = []
    for event_code in EVENT_ORDER:
        selected = [
            event for event in events if str(event["event_code"]) == event_code
        ]
        rows.append({
            "event_code": event_code,
            "observed_segment_rate": float(len(selected) / segments_per_profile),
            "event_ids": [str(event["event_id"]) for event in selected],
        })
    return rows


def _candidate_atoms(
    profile: dict[str, Any],
    events: list[dict[str, Any]],
    *,
    max_candidates: int = 8,
) -> list[dict[str, Any]]:
    """Compile admissible interpretation candidates before the LLM stage."""
    dimensions = {
        str(row["dimension_id"]): row
        for row in profile["suica_packet"]["dimensions"]
    }
    summaries = {
        str(row["event_code"]): row
        for row in _event_summary(
            events,
            segments_per_profile=len(profile["segments"]),
        )
    }
    ranked_candidates: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    for link in profile["registered_links"]:
        dimension_id = str(link["dimension_id"])
        event_code = str(link["event_code"])
        dimension = dimensions[dimension_id]
        summary = summaries[event_code]
        event_ids = list(map(str, summary["event_ids"]))
        threshold = float(
            link.get(
                "event_rate_threshold",
                link.get("upper_band_event_rate_minimum", 0.50),
            )
        )
        association_direction = str(link["association_direction"])
        relation = ""
        direction = ""
        band_matches = False
        if (
            association_direction == "positive"
            and dimension["reference_band"] == "upper_reference_band"
        ):
            relation = "elevated"
            direction = "positive"
            band_matches = True
        elif (
            association_direction == "negative"
            and dimension["reference_band"] == "lower_reference_band"
        ):
            relation = "reduced"
            direction = "negative"
            band_matches = True
        if (
            dimension["support_status"] == "supported"
            and band_matches
            and float(summary["observed_segment_rate"]) >= threshold
            and event_ids
        ):
            candidate = {
                "candidate_id": f"C::{dimension_id}::{event_code}",
                "target_dimension_ids": [dimension_id],
                "scope": "author_relative",
                "relation": relation,
                "direction": direction,
                "evidence_event_ids": event_ids,
                "registered_event_code": event_code,
                "support_hint": (
                    "strong"
                    if float(summary["observed_segment_rate"]) >= 0.75
                    else "moderate"
                ),
            }
            priority = (
                -int(candidate["support_hint"] == "strong"),
                -int(dimension.get("uncertainty_band") == "clear"),
                -len(event_ids),
                -abs(float(link.get("discovery_spearman_r", 0.0))),
                str(candidate["candidate_id"]),
            )
            ranked_candidates.append((priority, candidate))
    limit = max(0, int(max_candidates))
    if len(ranked_candidates) <= limit:
        return [candidate for _, candidate in ranked_candidates]
    return [
        candidate
        for _, candidate in sorted(ranked_candidates, key=lambda row: row[0])[
            :limit
        ]
    ]


def _interpreter_profile(
    profile: dict[str, Any],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "profile_id": profile["profile_id"],
        "suica_packet": profile["suica_packet"],
        "registered_links": profile["registered_links"],
        "behavior_events": events,
        "candidate_atoms": _candidate_atoms(profile, events),
        "event_summary": _event_summary(
            events,
            segments_per_profile=len(profile["segments"]),
        ),
        "interpretation_rule": (
            "An atom requires a supported SUICA dimension, a registered link, "
            "and at least one cited observed event from that linked code. "
            "The compiler has already applied this rule in candidate_atoms. "
            "The interpreter may only accept, qualify, or reject those candidates."
        ),
    }


def _interpreter_payload(
    profiles: list[dict[str, Any]],
    events: dict[str, list[dict[str, Any]]],
    *,
    irrelevant_note: bool = False,
) -> dict[str, Any]:
    rows = [
        _interpreter_profile(
            profile,
            events.get(str(profile["profile_id"]), []),
        )
        for profile in profiles
    ]
    if irrelevant_note:
        for row in rows:
            row["collection_note"] = (
                "The source order was randomized for storage; this note carries no evidence."
            )
            row["behavior_events"] = list(reversed(row["behavior_events"]))
            row["event_summary"] = list(reversed(row["event_summary"]))
    return {
        "task": "Produce only registered, evidence-bound interpretation atoms.",
        "profiles": rows,
    }


def _critique_payload(
    interpreter_payload: dict[str, Any],
    interpretation: dict[str, Any],
) -> dict[str, Any]:
    inputs = {
        str(profile["profile_id"]): profile
        for profile in interpreter_payload["profiles"]
    }
    rows = []
    for result in interpretation["profiles"]:
        profile_id = str(result["profile_id"])
        source = inputs[profile_id]
        rows.append({
            "profile_id": profile_id,
            "suica_packet": source["suica_packet"],
            "registered_links": source["registered_links"],
            "behavior_events": source["behavior_events"],
            "candidate_atoms": source["candidate_atoms"],
            "event_summary": source["event_summary"],
            "submitted_interpretation": result,
        })
    return {
        "task": "Judge every submitted atom exactly once without rewriting.",
        "profiles": rows,
    }


def _profile_lookup(payload: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not payload:
        return {}
    return {
        str(profile["profile_id"]): profile for profile in payload["profiles"]
    }


def _cached_stage(
    *,
    cache_path: Path,
    provider: SemanticProvider,
    spec: SemanticTransducerSpec,
    payload: dict[str, Any],
    run_id: str,
    validator: Callable[[Any], dict[str, Any]],
) -> dict[str, Any]:
    if cache_path.exists():
        cached = _read_json(cache_path)
        cached_runtime = cached.get("ledger", {}).get("runtime", {})
        expected_input_sha256 = hashlib.sha256(
            json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        expected_runtime = spec.public_runtime()
        identity_keys = (
            "provider",
            "model",
            "model_revision",
            "prompt_id",
            "prompt_sha256",
            "schema_id",
            "schema_sha256",
            "temperature",
            "thinking_mode",
            "max_tokens",
        )
        identity_matches = all(
            cached_runtime.get(key) == expected_runtime.get(key)
            for key in identity_keys
        ) and (
            cached.get("ledger", {}).get("input_sha256")
            == expected_input_sha256
        )
        if cached.get("status") == "STRUCTURED_STAGE_READY" and identity_matches:
            try:
                validator(cached["output"])
                cached["ledger"]["cache_hit"] = True
                return cached
            except Exception:
                cache_path.unlink()
    result = run_structured_stage(
        provider,
        spec,
        payload,
        run_id=run_id,
        validator=validator,
    )
    result["ledger"]["cache_hit"] = False
    _write_json(cache_path, result)
    return result


def _stage_jobs(
    jobs: list[dict[str, Any]],
    *,
    concurrency: int,
) -> list[dict[str, Any]]:
    completed: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, int(concurrency))) as executor:
        futures = {
            executor.submit(_cached_stage, **job): job["run_id"]
            for job in jobs
        }
        for future in as_completed(futures):
            result = future.result()
            result["_run_id"] = futures[future]
            completed.append(result)
    return sorted(completed, key=lambda row: row["_run_id"])


def _make_specs(
    config: dict[str, Any],
) -> tuple[SemanticTransducerSpec, SemanticTransducerSpec, SemanticTransducerSpec]:
    runtime = config["runtime"]
    primary_model = os.environ.get(
        runtime["primary_model_env"],
        runtime["default_primary_model"],
    )
    audit_model = os.environ.get(
        runtime["audit_model_env"],
        runtime["default_audit_model"],
    )
    common = {
        "provider": str(runtime["provider"]),
        "temperature": float(runtime["temperature"]),
        "thinking_mode": str(runtime["thinking_mode"]),
        "max_tokens": int(runtime["max_tokens"]),
        "timeout_seconds": float(runtime["timeout_seconds"]),
        "max_retries": int(runtime["max_retries"]),
        "max_validation_retries": int(runtime["max_validation_retries"]),
    }
    observer = load_semantic_spec(
        prompt_path=ROOT / "prompts" / "v8_behavior_observer_v1.txt",
        schema_path=ROOT / "schemas" / "v8_behavior_observation.schema.json",
        model=primary_model,
        model_revision=primary_model,
        prompt_id="v8-behavior-observer-v1",
        **common,
    )
    interpreter = load_semantic_spec(
        prompt_path=ROOT / "prompts" / "v8_interpreter_v1.txt",
        schema_path=ROOT / "schemas" / "v8_interpretation.schema.json",
        model=primary_model,
        model_revision=primary_model,
        prompt_id="v8-interpreter-v1",
        **common,
    )
    critic = load_semantic_spec(
        prompt_path=ROOT / "prompts" / "v8_interpreter_critic_v1.txt",
        schema_path=ROOT / "schemas" / "v8_interpretation_critique.schema.json",
        model=audit_model,
        model_revision=audit_model,
        prompt_id="v8-interpreter-critic-v1",
        **common,
    )
    return observer, interpreter, critic


def _batch_profiles(
    profiles: list[dict[str, Any]],
    *,
    batch_size: int,
) -> list[list[dict[str, Any]]]:
    return [
        profiles[start:start + int(batch_size)]
        for start in range(0, len(profiles), int(batch_size))
    ]


def _run_pipeline_repetition(
    *,
    profiles: list[dict[str, Any]],
    repetition: int,
    output_dir: Path,
    provider: SemanticProvider,
    observer_spec: SemanticTransducerSpec,
    interpreter_spec: SemanticTransducerSpec,
    critic_spec: SemanticTransducerSpec,
    batch_size: int,
    concurrency: int,
) -> dict[str, Any]:
    batches = _batch_profiles(profiles, batch_size=batch_size)
    observer_jobs = []
    for batch_index, batch in enumerate(batches):
        expected, spans, segments = _behavior_validation_context(batch)
        validator = lambda value, e=expected, s=spans, p=segments: validate_behavior_payload(
            value,
            schema=observer_spec.schema,
            expected_profiles=e,
            spans_by_segment=s,
            segments_by_profile=p,
            return_audit=True,
        )
        run_id = f"baseline-r{repetition:02d}-observer-b{batch_index:03d}"
        observer_jobs.append({
            "cache_path": output_dir / "cache" / "observer" / f"{run_id}.json",
            "provider": provider,
            "spec": observer_spec,
            "payload": _observer_payload(batch),
            "run_id": run_id,
            "validator": validator,
        })
    observer_results = _stage_jobs(observer_jobs, concurrency=concurrency)

    observer_outputs: dict[str, list[dict[str, Any]]] = {}
    for result in observer_results:
        observer_outputs.update(_events_by_profile(result.get("output")))

    interpreter_jobs = []
    interpreter_inputs: dict[int, dict[str, Any]] = {}
    for batch_index, batch in enumerate(batches):
        payload = _interpreter_payload(batch, observer_outputs)
        interpreter_inputs[batch_index] = payload
        expected = {str(profile["profile_id"]) for profile in batch}
        event_ids = {
            str(profile["profile_id"]): {
                str(event["event_id"])
                for event in observer_outputs.get(str(profile["profile_id"]), [])
            }
            for profile in batch
        }
        event_codes = {
            str(profile["profile_id"]): {
                str(event["event_id"]): str(event["event_code"])
                for event in observer_outputs.get(str(profile["profile_id"]), [])
            }
            for profile in batch
        }
        registered = {
            str(profile["profile_id"]): {
                (str(link["dimension_id"]), str(link["event_code"]))
                for link in profile["registered_links"]
            }
            for profile in batch
        }
        candidates = {
            str(row["profile_id"]): {
                str(candidate["candidate_id"]): candidate
                for candidate in row["candidate_atoms"]
            }
            for row in payload["profiles"]
        }
        validator = lambda value, e=expected, ids=event_ids, codes=event_codes, links=registered, allowed=candidates: validate_interpretation_payload(
            value,
            schema=interpreter_spec.schema,
            expected_profiles=e,
            event_ids_by_profile=ids,
            event_codes_by_profile=codes,
            registered_links_by_profile=links,
            candidate_atoms_by_profile=allowed,
        )
        run_id = f"baseline-r{repetition:02d}-interpreter-b{batch_index:03d}"
        interpreter_jobs.append({
            "cache_path": output_dir / "cache" / "interpreter" / f"{run_id}.json",
            "provider": provider,
            "spec": interpreter_spec,
            "payload": payload,
            "run_id": run_id,
            "validator": validator,
        })
    interpreter_results = _stage_jobs(interpreter_jobs, concurrency=concurrency)

    interpretation_outputs: dict[str, dict[str, Any]] = {}
    critic_jobs = []
    for batch_index, (batch, result) in enumerate(zip(batches, interpreter_results)):
        interpretation_outputs.update(_profile_lookup(result.get("output")))
        if result.get("status") != "STRUCTURED_STAGE_READY":
            continue
        payload = _critique_payload(interpreter_inputs[batch_index], result["output"])
        expected = {str(profile["profile_id"]) for profile in batch}
        atom_ids = {
            str(profile["profile_id"]): {
                str(atom["atom_id"]) for atom in profile["interpretation_atoms"]
            }
            for profile in result["output"]["profiles"]
        }
        validator = lambda value, e=expected, ids=atom_ids: validate_critique_payload(
            value,
            schema=critic_spec.schema,
            expected_profiles=e,
            atom_ids_by_profile=ids,
        )
        run_id = f"baseline-r{repetition:02d}-critic-b{batch_index:03d}"
        critic_jobs.append({
            "cache_path": output_dir / "cache" / "critic" / f"{run_id}.json",
            "provider": provider,
            "spec": critic_spec,
            "payload": payload,
            "run_id": run_id,
            "validator": validator,
        })
    critic_results = _stage_jobs(critic_jobs, concurrency=concurrency)
    critique_outputs: dict[str, dict[str, Any]] = {}
    for result in critic_results:
        critique_outputs.update(_profile_lookup(result.get("output")))
    return {
        "observer": observer_outputs,
        "interpretation": interpretation_outputs,
        "critique": critique_outputs,
        "stage_results": observer_results + interpreter_results + critic_results,
    }


def _run_interpreter_variant(
    *,
    variant: str,
    profiles: list[dict[str, Any]],
    events: dict[str, list[dict[str, Any]]],
    output_dir: Path,
    provider: SemanticProvider,
    interpreter_spec: SemanticTransducerSpec,
    critic_spec: SemanticTransducerSpec,
    batch_size: int,
    concurrency: int,
    irrelevant_note: bool = False,
) -> dict[str, Any]:
    batches = _batch_profiles(profiles, batch_size=batch_size)
    jobs = []
    inputs: dict[int, dict[str, Any]] = {}
    for batch_index, batch in enumerate(batches):
        payload = _interpreter_payload(
            batch,
            events,
            irrelevant_note=irrelevant_note,
        )
        inputs[batch_index] = payload
        expected = {str(profile["profile_id"]) for profile in batch}
        event_ids = {
            str(profile["profile_id"]): {
                str(event["event_id"])
                for event in events.get(str(profile["profile_id"]), [])
            }
            for profile in batch
        }
        event_codes = {
            str(profile["profile_id"]): {
                str(event["event_id"]): str(event["event_code"])
                for event in events.get(str(profile["profile_id"]), [])
            }
            for profile in batch
        }
        registered = {
            str(profile["profile_id"]): {
                (str(link["dimension_id"]), str(link["event_code"]))
                for link in profile["registered_links"]
            }
            for profile in batch
        }
        candidates = {
            str(row["profile_id"]): {
                str(candidate["candidate_id"]): candidate
                for candidate in row["candidate_atoms"]
            }
            for row in payload["profiles"]
        }
        validator = lambda value, e=expected, ids=event_ids, codes=event_codes, links=registered, allowed=candidates: validate_interpretation_payload(
            value,
            schema=interpreter_spec.schema,
            expected_profiles=e,
            event_ids_by_profile=ids,
            event_codes_by_profile=codes,
            registered_links_by_profile=links,
            candidate_atoms_by_profile=allowed,
        )
        run_id = f"{variant}-interpreter-b{batch_index:03d}"
        jobs.append({
            "cache_path": output_dir / "cache" / variant / f"{run_id}.json",
            "provider": provider,
            "spec": interpreter_spec,
            "payload": payload,
            "run_id": run_id,
            "validator": validator,
        })
    interpreter_results = _stage_jobs(jobs, concurrency=concurrency)
    outputs: dict[str, dict[str, Any]] = {}
    critic_jobs = []
    for batch_index, (batch, result) in enumerate(zip(batches, interpreter_results)):
        outputs.update(_profile_lookup(result.get("output")))
        if result.get("status") != "STRUCTURED_STAGE_READY":
            continue
        payload = _critique_payload(inputs[batch_index], result["output"])
        expected = {str(profile["profile_id"]) for profile in batch}
        atom_ids = {
            str(profile["profile_id"]): {
                str(atom["atom_id"]) for atom in profile["interpretation_atoms"]
            }
            for profile in result["output"]["profiles"]
        }
        validator = lambda value, e=expected, ids=atom_ids: validate_critique_payload(
            value,
            schema=critic_spec.schema,
            expected_profiles=e,
            atom_ids_by_profile=ids,
        )
        run_id = f"{variant}-critic-b{batch_index:03d}"
        critic_jobs.append({
            "cache_path": output_dir / "cache" / variant / f"{run_id}.json",
            "provider": provider,
            "spec": critic_spec,
            "payload": payload,
            "run_id": run_id,
            "validator": validator,
        })
    critic_results = _stage_jobs(critic_jobs, concurrency=concurrency)
    critiques: dict[str, dict[str, Any]] = {}
    for result in critic_results:
        critiques.update(_profile_lookup(result.get("output")))
    return {
        "interpretation": outputs,
        "critique": critiques,
        "stage_results": interpreter_results + critic_results,
    }


def _atom_set(profile: dict[str, Any] | None) -> set[str]:
    if not profile:
        return set()
    return {
        interpretation_atom_key(atom)
        for atom in profile.get("interpretation_atoms", [])
    }


def _edge_set(profile: dict[str, Any] | None) -> set[str]:
    return evidence_edge_set(profile or {})


def _verdict_map(
    interpretation: dict[str, Any] | None,
    critique: dict[str, Any] | None,
) -> dict[str, str]:
    if not interpretation or not critique:
        return {}
    keys = {
        str(atom["atom_id"]): interpretation_atom_key(atom)
        for atom in interpretation.get("interpretation_atoms", [])
    }
    return {
        keys[str(verdict["atom_id"])]: str(verdict["verdict"])
        for verdict in critique.get("atom_verdicts", [])
        if str(verdict["atom_id"]) in keys
    }


def _bootstrap_stat_interval(
    values: list[float],
    *,
    draws: int,
    seed: int,
    statistic: str,
) -> tuple[float, float, float]:
    vector = np.asarray(values, dtype=float)
    vector = vector[np.isfinite(vector)]
    if not len(vector):
        return float("nan"), float("nan"), float("nan")
    function = np.median if statistic == "median" else np.mean
    estimate = float(function(vector))
    if len(vector) == 1:
        return estimate, estimate, estimate
    rng = np.random.default_rng(seed)
    samples = vector[rng.integers(0, len(vector), size=(int(draws), len(vector)))]
    draw_values = function(samples, axis=1)
    return (
        estimate,
        float(np.quantile(draw_values, 0.025)),
        float(np.quantile(draw_values, 0.975)),
    )


def _event_macro_f1(
    profiles: list[dict[str, Any]],
    outputs: list[dict[str, Any]],
) -> float:
    values = []
    for event_code in EVENT_ORDER:
        truth: set[str] = set()
        predicted: set[str] = set()
        for profile in profiles:
            profile_id = str(profile["profile_id"])
            truth.update(
                f"{profile_id}|{event_id}"
                for event_id in profile["expected_events"]
                if event_id.endswith(f"::{event_code}")
            )
        for output in outputs:
            for profile_id, events in output.items():
                predicted.update(
                    f"{profile_id}|{event['event_id']}"
                    for event in events
                    if event["event_code"] == event_code
                )
        if len(outputs):
            truth = {
                f"r{run}|{value}"
                for run in range(len(outputs))
                for value in truth
            }
            predicted = {
                f"r{run}|{profile_id}|{event['event_id']}"
                for run, output in enumerate(outputs)
                for profile_id, events in output.items()
                for event in events
                if event["event_code"] == event_code
            }
        values.append(set_f1(truth, predicted))
    return float(np.mean(values))


def _variant_event_sets(
    profiles: list[dict[str, Any]],
    baseline: dict[str, list[dict[str, Any]]],
    *,
    seed: int,
) -> tuple[
    dict[str, list[dict[str, Any]]],
    dict[str, list[dict[str, Any]]],
]:
    rng = np.random.default_rng(seed)
    targeted: dict[str, list[dict[str, Any]]] = {}
    random_control: dict[str, list[dict[str, Any]]] = {}
    for profile in profiles:
        profile_id = str(profile["profile_id"])
        events = list(baseline.get(profile_id, []))
        target_code = str(profile["target_event_code"])
        target_events = [
            event for event in events if str(event["event_code"]) == target_code
        ]
        targeted[profile_id] = [
            event for event in events if str(event["event_code"]) != target_code
        ]
        candidates = [
            index for index, event in enumerate(events)
            if str(event["event_code"]) != target_code
        ]
        remove_count = min(len(target_events), len(candidates))
        removed = set(
            map(int, rng.choice(candidates, size=remove_count, replace=False))
        ) if remove_count else set()
        random_control[profile_id] = [
            event for index, event in enumerate(events) if index not in removed
        ]
    return targeted, random_control


def _summarize_planted(
    *,
    profiles: list[dict[str, Any]],
    repetitions: list[dict[str, Any]],
    irrelevant: dict[str, Any],
    targeted: dict[str, Any],
    random_control: dict[str, Any],
    config: dict[str, Any],
    quick: bool,
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    seed = int(config["seed"])
    planted = config["planted"]
    gates = config["gates"]
    draws = min(1000, int(planted["bootstrap_draws"])) if quick else int(
        planted["bootstrap_draws"]
    )
    atom_documents = [
        _atom_set(profile)
        for repetition in repetitions
        for profile in repetition["interpretation"].values()
    ]
    weights = idf_weights(atom_documents)

    stability_rows = []
    complete_profiles = []
    for profile in profiles:
        profile_id = str(profile["profile_id"])
        interpretations = [
            repetition["interpretation"].get(profile_id)
            for repetition in repetitions
        ]
        observations = [
            repetition["observer"].get(profile_id)
            for repetition in repetitions
        ]
        critiques = [
            repetition["critique"].get(profile_id)
            for repetition in repetitions
        ]
        if (
            not all(value is not None for value in interpretations)
            or not all(value is not None for value in observations)
        ):
            continue
        complete_profiles.append(profile_id)
        atom_runs = [_atom_set(value) for value in interpretations]
        edge_runs = [_edge_set(value) for value in interpretations]
        candidate_runs = [
            {
                str(candidate["candidate_id"])
                for candidate in _candidate_atoms(profile, observation)
            }
            for observation in observations
        ]
        candidate_eligible = bool(set().union(*candidate_runs))
        interpreted_any = bool(set().union(*atom_runs))
        interpreted_consensus = bool(
            consensus_set(atom_runs, minimum_fraction=0.8)
        )
        verdict_runs = [
            _verdict_map(interpretation, critique)
            for interpretation, critique in zip(interpretations, critiques)
        ]
        stability_rows.append({
            "profile_id": profile_id,
            "candidate_eligible": candidate_eligible,
            "interpreted_any": interpreted_any,
            "interpreted_consensus": interpreted_consensus,
            "atom_weighted_jaccard": (
                mean_pairwise_weighted_jaccard(atom_runs, weights=weights)
                if interpreted_any else 0.0
            ),
            "evidence_edge_f1": (
                mean_pairwise_set_f1(edge_runs) if interpreted_any else 0.0
            ),
            "critic_kappa": pairwise_nominal_kappa(verdict_runs),
            "atom_count_mean": float(np.mean(list(map(len, atom_runs)))),
            "consensus_atom_count": len(consensus_set(atom_runs, minimum_fraction=0.8)),
        })
    stability = pd.DataFrame(stability_rows)
    eligible_stability = stability.loc[
        stability.get("candidate_eligible", pd.Series(dtype=bool)).fillna(False)
    ].copy()
    atom_estimate = _bootstrap_stat_interval(
        eligible_stability.get(
            "atom_weighted_jaccard",
            pd.Series(dtype=float),
        ).tolist(),
        draws=draws,
        seed=seed + 1,
        statistic="median",
    )
    edge_estimate = _bootstrap_stat_interval(
        eligible_stability.get(
            "evidence_edge_f1",
            pd.Series(dtype=float),
        ).tolist(),
        draws=draws,
        seed=seed + 2,
        statistic="mean",
    )
    critic_estimate = _bootstrap_stat_interval(
        stability.get("critic_kappa", pd.Series(dtype=float)).tolist(),
        draws=draws,
        seed=seed + 3,
        statistic="mean",
    )

    runs_by_profile = {
        profile_id: [
            _atom_set(repetition["interpretation"].get(profile_id))
            for repetition in repetitions
        ]
        for profile_id in eligible_stability["profile_id"].astype(str)
    }
    atom_universe = set().union(
        *[
            atom_set
            for runs in runs_by_profile.values()
            for atom_set in runs
        ]
    ) if runs_by_profile else set()
    multilabel_kappa = fleiss_kappa_multilabel(
        runs_by_profile,
        universe=atom_universe,
    ) if atom_universe else float("nan")
    interpreted_profile_rate = float(
        eligible_stability["interpreted_consensus"].mean()
    ) if len(eligible_stability) else 0.0

    baseline_interpretation = repetitions[0]["interpretation"]
    baseline_critique = repetitions[0]["critique"]
    perturbation_rows = []
    sensitivity_rows = []
    for profile in profiles:
        profile_id = str(profile["profile_id"])
        baseline = baseline_interpretation.get(profile_id)
        changed = irrelevant["interpretation"].get(profile_id)
        baseline_critic = baseline_critique.get(profile_id)
        changed_critic = irrelevant["critique"].get(profile_id)
        if baseline is not None and changed is not None:
            baseline_verdict = _verdict_map(baseline, baseline_critic)
            changed_verdict = _verdict_map(changed, changed_critic)
            verdict_keys = set(baseline_verdict).union(changed_verdict)
            verdict_invariance = (
                np.mean([
                    baseline_verdict.get(key, "<missing>")
                    == changed_verdict.get(key, "<missing>")
                    for key in verdict_keys
                ])
                if verdict_keys else 1.0
            )
            perturbation_rows.append({
                "profile_id": profile_id,
                "atom_jaccard": set_jaccard(
                    _atom_set(baseline),
                    _atom_set(changed),
                ),
                "evidence_f1": set_f1(
                    _edge_set(baseline),
                    _edge_set(changed),
                ),
                "critic_invariance": float(verdict_invariance),
                "support_flip": (
                    baseline["assessment_status"] != changed["assessment_status"]
                ),
            })

        target_result = targeted["interpretation"].get(profile_id)
        random_result = random_control["interpretation"].get(profile_id)
        target_dimension = str(profile["target_dimension_id"])
        if baseline is None or target_result is None or random_result is None or not target_dimension:
            continue
        baseline_atoms = _atom_set(baseline)
        target_atoms = _atom_set(target_result)
        random_atoms = _atom_set(random_result)
        baseline_target = {
            value for value in baseline_atoms
            if target_dimension in value.split("|", 1)[0].split(",")
        }
        target_after = {
            value for value in target_atoms
            if target_dimension in value.split("|", 1)[0].split(",")
        }
        baseline_nontarget = baseline_atoms - baseline_target
        targeted_nontarget = {
            value for value in target_atoms
            if target_dimension not in value.split("|", 1)[0].split(",")
        }
        sensitivity_rows.append({
            "profile_id": profile_id,
            "target_dimension_id": target_dimension,
            "baseline_target_present": bool(baseline_target),
            "target_response": bool(
                baseline_target
                and (
                    not target_after
                    or target_after != baseline_target
                    or target_result["assessment_status"] != baseline["assessment_status"]
                )
            ),
            "nontarget_retention": set_f1(
                baseline_nontarget,
                targeted_nontarget,
            ),
            "targeted_effect": 1.0 - set_jaccard(baseline_atoms, target_atoms),
            "random_effect": 1.0 - set_jaccard(baseline_atoms, random_atoms),
            "targeted_minus_random": (
                set_jaccard(baseline_atoms, random_atoms)
                - set_jaccard(baseline_atoms, target_atoms)
            ),
        })
    perturbation = pd.DataFrame(perturbation_rows)
    sensitivity = pd.DataFrame(sensitivity_rows)
    eligible = sensitivity.loc[sensitivity["baseline_target_present"]].copy() if not sensitivity.empty else sensitivity
    target_rate = float(eligible["target_response"].mean()) if len(eligible) else float("nan")
    retention = float(eligible["nontarget_retention"].mean()) if len(eligible) else float("nan")
    effect = _bootstrap_stat_interval(
        eligible.get("targeted_minus_random", pd.Series(dtype=float)).tolist(),
        draws=draws,
        seed=seed + 4,
        statistic="mean",
    )

    stage_results = [
        result
        for repetition in repetitions
        for result in repetition["stage_results"]
    ]
    stage_results += irrelevant["stage_results"]
    stage_results += targeted["stage_results"]
    stage_results += random_control["stage_results"]
    ready_calls = sum(
        result.get("status") == "STRUCTURED_STAGE_READY"
        for result in stage_results
    )
    parse_rate = float(ready_calls / len(stage_results)) if stage_results else 0.0
    first_attempt_valid = sum(
        result.get("status") == "STRUCTURED_STAGE_READY"
        and result.get("ledger", {}).get("attempt_history", [{}])[0].get("status")
        == "VALID"
        for result in stage_results
    )
    first_attempt_valid_rate = (
        float(first_attempt_valid / len(stage_results)) if stage_results else 0.0
    )
    retried_calls = sum(
        int(result.get("ledger", {}).get("validation_attempts", 1)) > 1
        for result in stage_results
    )
    normalization_counts = {
        key: int(sum(
            result.get("ledger", {}).get("validator_metadata", {}).get(key, 0)
            for result in stage_results
        ))
        for key in (
            "canonicalized_event_ids",
            "merged_duplicate_events",
            "dropped_abstain_markers",
            "corrected_abstain_flags",
        )
    }
    normalized_calls = sum(
        any(
            int(result.get("ledger", {}).get("validator_metadata", {}).get(key, 0)) > 0
            for key in normalization_counts
        )
        for result in stage_results
    )
    normalization_call_rate = (
        float(normalized_calls / len(stage_results)) if stage_results else 0.0
    )
    forbidden = sum(
        interpretation_forbidden_count({
            "profiles": list(repetition["interpretation"].values())
        })
        for repetition in repetitions
    )
    forbidden += interpretation_forbidden_count({
        "profiles": list(irrelevant["interpretation"].values())
    })
    forbidden += interpretation_forbidden_count({
        "profiles": list(targeted["interpretation"].values())
    })
    forbidden += interpretation_forbidden_count({
        "profiles": list(random_control["interpretation"].values())
    })
    fabricated = 0

    event_f1 = _event_macro_f1(
        profiles,
        [repetition["observer"] for repetition in repetitions],
    )
    latent = np.asarray([profile["latent"] for profile in profiles], dtype=float)
    consensus = [
        consensus_set(
            [
                _atom_set(repetition["interpretation"].get(str(profile["profile_id"])))
                for repetition in repetitions
            ],
            minimum_fraction=0.8,
        )
        for profile in profiles
    ]
    geometry = geometry_interpretation_alignment(
        latent,
        consensus,
        neighbor_count=max(1, min(5, len(profiles) // 20)),
        permutations=min(1000, int(planted["permutations"])) if quick else int(
            planted["permutations"]
        ),
        seed=seed,
    )

    metrics = {
        "profiles": len(profiles),
        "complete_profiles": len(complete_profiles),
        "pipeline_repetitions": len(repetitions),
        "parse_rate": parse_rate,
        "first_attempt_valid_rate": first_attempt_valid_rate,
        "retried_call_count": int(retried_calls),
        "bookkeeping_normalization_call_rate": normalization_call_rate,
        **normalization_counts,
        "observer_macro_f1": event_f1,
        "same_input_weighted_jaccard_median": atom_estimate[0],
        "same_input_weighted_jaccard_ci_lower": atom_estimate[1],
        "same_input_weighted_jaccard_ci_upper": atom_estimate[2],
        "multilabel_fleiss_kappa": float(multilabel_kappa),
        "candidate_eligible_profiles": int(len(eligible_stability)),
        "interpreted_profile_rate": interpreted_profile_rate,
        "evidence_edge_f1_mean": edge_estimate[0],
        "evidence_edge_f1_ci_lower": edge_estimate[1],
        "evidence_edge_f1_ci_upper": edge_estimate[2],
        "critic_kappa_mean": critic_estimate[0],
        "critic_kappa_ci_lower": critic_estimate[1],
        "critic_kappa_ci_upper": critic_estimate[2],
        "forbidden_field_count": int(forbidden),
        "irrelevant_atom_jaccard": float(
            perturbation["atom_jaccard"].mean()
        ) if len(perturbation) else float("nan"),
        "irrelevant_evidence_f1": float(
            perturbation["evidence_f1"].mean()
        ) if len(perturbation) else float("nan"),
        "irrelevant_critic_invariance": float(
            perturbation["critic_invariance"].mean()
        ) if len(perturbation) else float("nan"),
        "irrelevant_support_flip_rate": float(
            perturbation["support_flip"].mean()
        ) if len(perturbation) else float("nan"),
        "key_evidence_eligible_profiles": int(len(eligible)),
        "key_evidence_response_rate": target_rate,
        "key_evidence_nontarget_retention": retention,
        "targeted_minus_random_effect": effect[0],
        "targeted_minus_random_ci_lower": effect[1],
        "targeted_minus_random_ci_upper": effect[2],
        "fabricated_evidence_count": fabricated,
        **geometry,
    }
    if quick:
        checks = {
            "runtime_parse": parse_rate >= 0.90,
            "first_attempt_runtime": first_attempt_valid_rate >= 0.80,
            "bookkeeping_normalization": normalization_call_rate <= 0.20,
            "safety": forbidden == 0 and fabricated == 0,
            "observer_not_degenerate": event_f1 >= 0.60,
            "same_input_point_stability": atom_estimate[0] >= 0.70,
            "key_evidence_directional": (
                np.isfinite(target_rate)
                and target_rate >= 0.60
                and np.isfinite(effect[0])
                and effect[0] > 0
            ),
        }
        status = (
            "V8_INTERPRETER_QUICK_GATE_PASS"
            if all(checks.values())
            else "V8_INTERPRETER_QUICK_GATE_NOT_CLOSED"
        )
    else:
        checks = {
            "runtime_parse": parse_rate >= float(gates["min_parse_rate"]),
            "first_attempt_runtime": (
                first_attempt_valid_rate
                >= float(gates["min_first_attempt_valid_rate"])
            ),
            "bookkeeping_normalization": (
                normalization_call_rate
                <= float(gates["max_bookkeeping_normalization_call_rate"])
            ),
            "same_input_stability": (
                atom_estimate[1]
                >= float(gates["min_same_input_weighted_jaccard_lcb"])
            ),
            "multilabel_fleiss_kappa": (
                multilabel_kappa
                >= float(gates["min_multilabel_fleiss_kappa"])
            ),
            "interpretation_coverage": (
                interpreted_profile_rate
                >= float(gates["min_interpreted_profile_rate"])
            ),
            "evidence_edge_stability": (
                edge_estimate[1] >= float(gates["min_evidence_edge_f1_lcb"])
            ),
            "critic_stability": (
                critic_estimate[0] >= float(gates["min_critic_kappa"])
            ),
            "safety": (
                forbidden <= int(gates["max_forbidden_field_count"])
                and fabricated <= int(gates["max_fabricated_evidence_count"])
            ),
            "irrelevant_robustness": (
                len(perturbation) > 0
                and metrics["irrelevant_atom_jaccard"]
                >= float(gates["min_irrelevant_atom_jaccard"])
                and metrics["irrelevant_evidence_f1"]
                >= float(gates["min_irrelevant_evidence_f1"])
                and metrics["irrelevant_critic_invariance"]
                >= float(gates["min_irrelevant_critic_invariance"])
                and metrics["irrelevant_support_flip_rate"]
                <= float(gates["max_irrelevant_support_flip"])
            ),
            "key_evidence_sensitivity": (
                len(eligible) > 0
                and target_rate >= float(gates["min_key_evidence_response_rate"])
                and retention
                >= float(gates["min_key_evidence_nontarget_retention"])
                and effect[0] >= float(gates["min_targeted_minus_random_effect"])
                and effect[1] > float(gates["min_targeted_minus_random_lcb"])
            ),
        }
        status = (
            "V8_INTERPRETER_PLANTED_GATE_PASS"
            if all(checks.values())
            else "V8_INTERPRETER_PLANTED_GATE_NOT_CLOSED"
        )
    decision = {
        "status": status,
        "quick": bool(quick),
        "metrics": metrics,
        "checks": checks,
        "next_action": (
            "RUN_FORMAL_PLANTED"
            if status == "V8_INTERPRETER_QUICK_GATE_PASS"
            else "RUN_PANDORA_PRIMARY"
            if status == "V8_INTERPRETER_PLANTED_GATE_PASS"
            else "STOP_AND_DIAGNOSE_INTERPRETER"
        ),
        "claim_boundary": config["claim_boundary"],
    }
    return decision, stability, pd.concat(
        [
            perturbation.assign(experiment="irrelevant_perturbation"),
            sensitivity.assign(experiment="key_evidence_removal"),
        ],
        ignore_index=True,
        sort=False,
    )


def run_planted(
    *,
    config: dict[str, Any],
    env_file: Path,
    output_dir: Path,
    quick: bool,
) -> dict[str, Any]:
    _source_env(env_file)
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is missing")
    runtime = config["runtime"]
    planted = config["planted"]
    count = int(planted["quick_profiles"] if quick else planted["profiles"])
    repetitions_count = int(
        planted["quick_repetitions"] if quick else planted["pipeline_repetitions"]
    )
    profiles = _planted_profiles(
        count=count,
        segments_per_profile=int(planted["segments_per_profile"]),
        seed=int(config["seed"]),
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "config.resolved.json", config)
    manifest = write_run_manifest(
        output_dir / "manifest.json",
        repository_root=ROOT,
        input_paths=[
            ROOT / "configs" / "v8_interpreter_stability.json",
            ROOT / "prompts" / "v8_behavior_observer_v1.txt",
            ROOT / "prompts" / "v8_interpreter_v1.txt",
            ROOT / "prompts" / "v8_interpreter_critic_v1.txt",
            ROOT / "schemas" / "v8_behavior_observation.schema.json",
            ROOT / "schemas" / "v8_interpretation.schema.json",
            ROOT / "schemas" / "v8_interpretation_critique.schema.json",
        ],
        config_path=ROOT / "configs" / "v8_interpreter_stability.json",
        code_paths=[Path(__file__), ROOT / "suica_core" / "v8_interpreter.py"],
        estimand_id="V8-I1-evidence-bound-interpreter-stability-planted",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    provider = OpenAICompatibleProvider(base_url=base_url, api_key=api_key)
    observer_spec, interpreter_spec, critic_spec = _make_specs(config)
    repetitions = []
    batch_size = int(
        runtime.get("quick_batch_size", runtime["batch_size"])
        if quick
        else runtime["batch_size"]
    )
    for repetition in range(repetitions_count):
        repetitions.append(_run_pipeline_repetition(
            profiles=profiles,
            repetition=repetition,
            output_dir=output_dir,
            provider=provider,
            observer_spec=observer_spec,
            interpreter_spec=interpreter_spec,
            critic_spec=critic_spec,
            batch_size=batch_size,
            concurrency=int(runtime["concurrency"]),
        ))

    baseline_events = repetitions[0]["observer"]
    targeted_events, random_events = _variant_event_sets(
        profiles,
        baseline_events,
        seed=int(config["seed"]) + 90,
    )
    irrelevant = _run_interpreter_variant(
        variant="irrelevant",
        profiles=profiles,
        events=baseline_events,
        output_dir=output_dir,
        provider=provider,
        interpreter_spec=interpreter_spec,
        critic_spec=critic_spec,
        batch_size=batch_size,
        concurrency=int(runtime["concurrency"]),
        irrelevant_note=True,
    )
    targeted = _run_interpreter_variant(
        variant="targeted_removal",
        profiles=profiles,
        events=targeted_events,
        output_dir=output_dir,
        provider=provider,
        interpreter_spec=interpreter_spec,
        critic_spec=critic_spec,
        batch_size=batch_size,
        concurrency=int(runtime["concurrency"]),
    )
    random_control = _run_interpreter_variant(
        variant="random_removal",
        profiles=profiles,
        events=random_events,
        output_dir=output_dir,
        provider=provider,
        interpreter_spec=interpreter_spec,
        critic_spec=critic_spec,
        batch_size=batch_size,
        concurrency=int(runtime["concurrency"]),
    )
    decision, stability, variants = _summarize_planted(
        profiles=profiles,
        repetitions=repetitions,
        irrelevant=irrelevant,
        targeted=targeted,
        random_control=random_control,
        config=config,
        quick=quick,
    )
    stability.to_csv(output_dir / "stability_by_profile.csv", index=False)
    variants.to_csv(output_dir / "perturbation_and_sensitivity.csv", index=False)
    pd.DataFrame([decision["metrics"]]).to_csv(
        output_dir / "metrics.csv",
        index=False,
    )
    all_stage_results = [
        result
        for repetition in repetitions
        for result in repetition["stage_results"]
    ]
    all_stage_results += irrelevant["stage_results"]
    all_stage_results += targeted["stage_results"]
    all_stage_results += random_control["stage_results"]
    with (output_dir / "execution_ledger.jsonl").open("w", encoding="utf-8") as handle:
        for result in all_stage_results:
            handle.write(json.dumps(result["ledger"], ensure_ascii=False) + "\n")
    manifest.update({
        "status": decision["status"],
        "runtime": {
            "observer": observer_spec.public_runtime(),
            "interpreter": interpreter_spec.public_runtime(),
            "critic": critic_spec.public_runtime(),
        },
        "profile_count": len(profiles),
        "quick": bool(quick),
    })
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(output_dir / "decision.json", decision)
    append_ledger_event(
        output_dir / "evidence_ledger.jsonl",
        {"estimand_id": manifest["estimand_id"], **decision},
    )
    report = (
        "# SUICA V8 Interpreter Stability: Planted Gate\n\n"
        f"Status: `{decision['status']}`\n\n"
        f"Quick mode: `{quick}`; profiles: `{len(profiles)}`; "
        f"pipeline repetitions: `{repetitions_count}`.\n\n"
        "## Metrics\n\n"
        f"{pd.DataFrame([decision['metrics']]).round(4).T.to_markdown()}\n\n"
        "## Checks\n\n"
        + "\n".join(
            f"- `{name}`: {'PASS' if passed else 'FAIL'}"
            for name, passed in decision["checks"].items()
        )
        + "\n\n## Boundary\n\n"
        + str(decision["claim_boundary"])
        + "\n"
    )
    (output_dir / "report.md").write_text(report, encoding="utf-8")
    write_artifact_inventory(output_dir, output_dir / "artifact_inventory.json")
    return decision


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "v8_interpreter_stability.json",
    )
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results" / "v8_interpreter_stability" / "planted_formal",
    )
    parser.add_argument(
        "--phase",
        choices=("planted",),
        default="planted",
    )
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    config = _read_json(args.config)
    if args.phase != "planted":
        raise NotImplementedError(args.phase)
    decision = run_planted(
        config=config,
        env_file=args.env_file,
        output_dir=args.output_dir,
        quick=args.quick,
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
