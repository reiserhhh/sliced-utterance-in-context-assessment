#!/usr/bin/env python3
"""Run the high-resolution SUICA V8 behavior-v2 technical pilot."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import run_suica_v8_canonical_geometry_fresh_panel as fresh_stats  # noqa: E402
import run_suica_v8_interpreter_pandora as pandora  # noqa: E402
import run_suica_v8_interpreter_stability as base  # noqa: E402
import run_suica_v8_spectral_geometry_audit as spectral  # noqa: E402
from suica_core.v7_governance import (  # noqa: E402
    verify_artifact_inventory,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_behavior_v2 import (  # noqa: E402
    EVENT_CODES,
    EVENT_OPPORTUNITY,
    consensus_frame,
    event_macro_f1,
    fit_opportunity_event_baseline,
    normalize_behavior_v2_payload,
    observation_frame,
    pairwise_event_f1,
    profile_rate_features,
    validate_behavior_v2_payload,
)
from suica_core.v8_bridge import cross_modal_author_auc  # noqa: E402
from suica_core.v8_realtext import stable_digest, tokenize  # noqa: E402
from suica_core.v8_semantic import (  # noqa: E402
    OpenAICompatibleProvider,
    load_semantic_spec,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_behavior_v2_pilot.json"
DEFAULT_OUTPUT = ROOT / "results" / "v8_behavior_v2_pilot"

SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?。！？])\s+|\n+")
ANCHOR_PATTERNS = {
    "epistemic_qualification": re.compile(
        r"\b(?:maybe|perhaps|probably|possibly|seems?|appears?|"
        r"i\s+(?:think|guess|suppose)|not\s+always|in\s+some\s+cases)\b",
        re.IGNORECASE,
    ),
    "causal_explanation": re.compile(
        r"\b(?:because|since|therefore|thus|so\s+that|due\s+to|"
        r"leads?\s+to|results?\s+in)\b",
        re.IGNORECASE,
    ),
    "request_action": re.compile(
        r"(?:\?|please\b|\bcan\s+(?:you|someone)\b|"
        r"\bcould\s+(?:you|someone)\b)",
        re.IGNORECASE,
    ),
    "recommend_action": re.compile(
        r"\b(?:should|recommend|suggest|advise|need\s+to|ought\s+to)\b",
        re.IGNORECASE,
    ),
    "self_repair": re.compile(
        r"\b(?:i\s+mean|more\s+precisely|rather|to\s+clarify|"
        r"correction|let\s+me\s+rephrase)\b",
        re.IGNORECASE,
    ),
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _select_metadata(
    source_config: dict[str, Any],
    split_counts: dict[str, int],
    *,
    seed: int,
) -> pd.DataFrame:
    semantic, geometry_panel = pandora._load_panels(source_config)
    metadata, _, _ = pandora._score_geometry(
        semantic,
        geometry_panel,
        max_authors=int(
            source_config["real_text"]["max_authors"]["pandora"]
        ),
    )
    pieces = []
    for split, count in split_counts.items():
        group = metadata.loc[metadata["split"].astype(str).eq(str(split))].copy()
        group["_order"] = group["author_id"].astype(str).map(
            lambda value: hashlib.sha256(
                f"v8-behavior-v2::{seed}::{value}".encode("utf-8")
            ).hexdigest()
        )
        pieces.append(
            group.sort_values("_order", kind="stable").head(int(count))
        )
    selected = pd.concat(pieces, ignore_index=True).drop(columns="_order")
    if len(selected) != sum(map(int, split_counts.values())):
        raise RuntimeError("insufficient geometry-ready authors for pilot")
    return selected


def _spans(text: str, *, maximum: int, prefix: str) -> list[dict[str, str]]:
    pieces = [
        piece.strip()
        for piece in SENTENCE_BOUNDARY_RE.split(str(text))
        if piece.strip()
    ]
    if not pieces:
        pieces = [str(text).strip()]
    if len(pieces) > int(maximum):
        pieces = pieces[: maximum - 1] + [" ".join(pieces[maximum - 1:])]
    return [
        {"span_id": f"{prefix}-x{index:02d}", "text": piece}
        for index, piece in enumerate(pieces)
    ]


def _build_profiles(
    metadata: pd.DataFrame,
    *,
    segments_per_half: int,
    units_per_half: int,
    max_spans: int,
) -> list[dict[str, Any]]:
    eligible = pd.read_csv(
        pandora.ELIGIBLE_AUTHORS_PATH,
        usecols=["user_id"],
        dtype={"user_id": str},
    )
    eligible["author_id"] = eligible["user_id"].map(
        lambda value: stable_digest(str(value), salt="pandora-author")
    )
    selected = set(metadata["author_id"].astype(str))
    raw_users = eligible.loc[
        eligible["author_id"].isin(selected), "user_id"
    ].astype(str).tolist()
    raw = pd.read_parquet(
        pandora.PANDORA_COMMENTS_PATH,
        columns=["author", "body", "created_utc", "subreddit"],
        filters=[("author", "in", raw_users)],
    )
    raw["author"] = raw["author"].astype(str)
    raw["body"] = raw["body"].fillna("").astype(str)
    raw["token_count"] = raw["body"].map(lambda value: len(tokenize(value)))
    raw = raw.loc[raw["token_count"] >= 24].copy()
    metadata_lookup = metadata.set_index("author_id")["split"].astype(str)
    profiles = []
    pool_size = 2 * int(units_per_half)
    for raw_author, group in raw.sort_values(
        ["author", "created_utc"],
        kind="stable",
    ).groupby("author", observed=True, sort=False):
        if len(group) < pool_size:
            continue
        indices = np.unique(
            np.linspace(0, len(group) - 1, num=pool_size, dtype=int)
        )
        if len(indices) != pool_size:
            continue
        pool = group.iloc[indices].reset_index(drop=True)
        author_id = stable_digest(str(raw_author), salt="pandora-author")
        if author_id not in metadata_lookup:
            continue
        for side, side_frame in (
            ("left", pool.iloc[::2].reset_index(drop=True)),
            ("right", pool.iloc[1::2].reset_index(drop=True)),
        ):
            chosen = np.unique(
                np.linspace(
                    0,
                    len(side_frame) - 1,
                    num=int(segments_per_half),
                    dtype=int,
                )
            )
            if len(chosen) != int(segments_per_half):
                continue
            profile_id = "v8b2-" + stable_digest(
                f"{author_id}::{side}",
                salt="v8-behavior-profile-v2",
            )
            segments = []
            for segment_index, row_index in enumerate(chosen):
                row = side_frame.iloc[int(row_index)]
                segment_id = f"{profile_id}-s{segment_index:02d}"
                segments.append({
                    "segment_id": segment_id,
                    "segment_index": segment_index,
                    "condition": str(row["subreddit"]),
                    "token_count": int(row["token_count"]),
                    "spans": _spans(
                        str(row["body"]),
                        maximum=int(max_spans),
                        prefix=segment_id,
                    ),
                })
            profiles.append({
                "profile_id": profile_id,
                "author_id": author_id,
                "side": side,
                "cohort_split": str(metadata_lookup[author_id]),
                "segments": segments,
            })
    expected = 2 * len(metadata)
    if len(profiles) != expected:
        raise RuntimeError(
            f"built {len(profiles)} profiles for {len(metadata)} authors; "
            f"expected {expected}"
        )
    return sorted(profiles, key=lambda row: str(row["profile_id"]))


def _make_spec(
    config: dict[str, Any],
    *,
    model: str,
    prompt_id: str,
):
    runtime = config["runtime"]
    return load_semantic_spec(
        prompt_path=ROOT / "prompts" / "v8_behavior_observer_v2.txt",
        schema_path=ROOT / "schemas" / "v8_behavior_observation_v2.schema.json",
        provider=str(runtime["provider"]),
        model=model,
        model_revision=model,
        prompt_id=prompt_id,
        temperature=float(runtime["temperature"]),
        thinking_mode=str(runtime["thinking_mode"]),
        max_tokens=int(runtime["max_tokens"]),
        timeout_seconds=float(runtime["timeout_seconds"]),
        max_retries=int(runtime["max_retries"]),
        max_validation_retries=int(runtime["max_validation_retries"]),
    )


def _run_observer(
    profiles: list[dict[str, Any]],
    *,
    repetitions: int,
    output_dir: Path,
    provider: OpenAICompatibleProvider,
    spec,
    batch_size: int,
    concurrency: int,
    run_prefix: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    def make_validator(supplied):
        def validator(value):
            normalized, normalization = normalize_behavior_v2_payload(
                value,
                profiles=supplied,
            )
            return (
                validate_behavior_v2_payload(
                    normalized,
                    schema=spec.schema,
                    profiles=supplied,
                ),
                normalization,
            )
        return validator

    outputs = []
    all_results = []
    batches = base._batch_profiles(profiles, batch_size=batch_size)
    for repetition in range(int(repetitions)):
        jobs = []
        for batch_index, batch in enumerate(batches):
            run_id = (
                f"{run_prefix}-r{repetition:02d}-b{batch_index:03d}"
            )
            jobs.append({
                "cache_path": (
                    output_dir / "cache" / run_prefix / f"{run_id}.json"
                ),
                "provider": provider,
                "spec": spec,
                "payload": base._observer_payload(batch),
                "run_id": run_id,
                "validator": make_validator(batch),
            })
        results = base._stage_jobs(jobs, concurrency=concurrency)
        all_results.extend(results)
        ready = []
        for batch_index, (batch, result) in enumerate(
            zip(batches, results, strict=True)
        ):
            if result.get("status") == "STRUCTURED_STAGE_READY":
                ready.append(result)
                continue
            if len(batch) <= 1:
                continue
            singleton_jobs = []
            for singleton_index, profile in enumerate(batch):
                run_id = (
                    f"{run_prefix}-r{repetition:02d}-b{batch_index:03d}"
                    f"-s{singleton_index:02d}"
                )
                supplied = [profile]
                singleton_jobs.append({
                    "cache_path": (
                        output_dir
                        / "cache"
                        / run_prefix
                        / f"{run_id}.json"
                    ),
                    "provider": provider,
                    "spec": spec,
                    "payload": base._observer_payload(supplied),
                    "run_id": run_id,
                    "validator": make_validator(supplied),
                })
            singleton_results = base._stage_jobs(
                singleton_jobs,
                concurrency=min(concurrency, len(singleton_jobs)),
            )
            all_results.extend(singleton_results)
            if all(
                row.get("status") == "STRUCTURED_STAGE_READY"
                for row in singleton_results
            ):
                ready.extend(singleton_results)
        merged = {
            "profiles": [
                profile
                for result in ready
                for profile in result["output"]["profiles"]
            ]
        }
        if len(merged["profiles"]) == len(profiles):
            validate_behavior_v2_payload(
                merged,
                schema=spec.schema,
                profiles=profiles,
            )
            outputs.append(merged)
    return outputs, all_results


def _selected_segments(
    segments: pd.DataFrame,
    resolution: int,
) -> pd.DataFrame:
    rows = []
    for _, group in segments.groupby("profile_id", observed=True, sort=False):
        ordered = group.sort_values("segment_index", kind="stable")
        indices = np.unique(
            np.linspace(
                0,
                len(ordered) - 1,
                num=min(int(resolution), len(ordered)),
                dtype=int,
            )
        )
        rows.append(ordered.iloc[indices])
    return pd.concat(rows, ignore_index=True)


def _standardized_matrix(
    frame: pd.DataFrame,
    columns: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    discovery = frame["cohort_split"].astype(str).eq("discovery").to_numpy()
    values = frame[columns].to_numpy(float)
    medians = np.nanmedian(values[discovery], axis=0)
    medians = np.where(np.isfinite(medians), medians, 0.0)
    complete = np.where(np.isfinite(values), values, medians[None, :])
    scaler = StandardScaler().fit(complete[discovery])
    return (
        scaler.transform(complete),
        frame["author_id"].astype(str).to_numpy(),
        frame["side"].astype(str).to_numpy(),
        discovery,
    )


def _condition_features(
    segments: pd.DataFrame,
    *,
    resolution: int,
    top_dimensions: int,
) -> pd.DataFrame:
    selected = _selected_segments(segments, resolution)
    discovery = selected.loc[
        selected["cohort_split"].astype(str).eq("discovery")
    ]
    conditions = (
        discovery["condition"].value_counts().head(int(top_dimensions)).index
    )
    rows = []
    for profile_id, group in selected.groupby(
        "profile_id",
        observed=True,
        sort=False,
    ):
        first = group.iloc[0]
        row = {
            "profile_id": str(profile_id),
            "author_id": str(first["author_id"]),
            "side": str(first["side"]),
            "cohort_split": str(first["cohort_split"]),
            "mean_token_count": float(group["token_count"].mean()),
            "std_token_count": float(group["token_count"].std(ddof=0)),
            "mean_span_count": float(group["span_count"].mean()),
        }
        frequencies = group["condition"].value_counts(normalize=True)
        row.update({
            f"condition::{condition}": float(frequencies.get(condition, 0.0))
            for condition in conditions
        })
        rows.append(row)
    return pd.DataFrame(rows)


def _anchor_agreement(
    consensus: pd.DataFrame,
    profiles: list[dict[str, Any]],
) -> pd.DataFrame:
    text_by_segment = {
        str(segment["segment_id"]): " ".join(
            str(span["text"]) for span in segment["spans"]
        )
        for profile in profiles
        for segment in profile["segments"]
    }
    rows = []
    for event, pattern in ANCHOR_PATTERNS.items():
        anchor = consensus["segment_id"].map(
            lambda value: int(bool(pattern.search(text_by_segment[str(value)])))
        ).to_numpy(int)
        observed = consensus[f"event::{event}"].to_numpy(int)
        positives = int(anchor.sum())
        recall = (
            float(observed[anchor == 1].mean()) if positives else float("nan")
        )
        rows.append({
            "event_code": event,
            "anchor_positive_segments": positives,
            "llm_recall_on_rule_positive": recall,
            "claim_boundary": "high-precision local agreement, not accuracy",
        })
    return pd.DataFrame(rows)


def _report(decision: dict[str, Any], resolution: pd.DataFrame) -> str:
    return f"""# SUICA V8 High-Resolution Behavior-v2 Pilot

Decision: `{decision["status"]}`

## Design

- mode: `{decision["mode"]}`;
- authors/profiles: {decision["authors"]}/{decision["profiles"]};
- comments per author half: {decision["segments_per_half"]};
- primary observer repetitions: {decision["observer_repetitions"]};
- new personality or clinical labels: none.

The LLM emitted only explicit event/opportunity codes and exact source-span
bindings. Deterministic code performed every author-level aggregation.

## Observer

- structured parse rate: {decision["observer"]["parse_rate"]:.3f};
- repeated event-set F1:
  {decision["observer"]["repeated_event_f1"]};
- cross-model event-set F1:
  {decision["observer"]["cross_model_event_f1"]};
- usable event atoms: {decision["observer"]["usable_events"]}.

## Resolution ablation

{resolution.to_markdown(index=False)}

## Boundary

{decision["claim_boundary"]}

Passing this technical pilot licenses an adjudicated human-coding study, not a
geometry bridge or psychological interpretation.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--mode", choices=("smoke", "pilot"), default="pilot")
    args = parser.parse_args()
    config = _read_json(args.config)
    mode_config = config[args.mode]
    source = ROOT / str(config["source_run"])
    inventory = verify_artifact_inventory(source / "artifact_inventory.json")
    if inventory["status"] != "INVENTORY_PASS":
        raise RuntimeError("source interpreter inventory failed")
    source_config = _read_json(source / "config.resolved.json")
    metadata = _select_metadata(
        source_config,
        mode_config["split_counts"],
        seed=int(config["seed"]),
    )
    profiles = _build_profiles(
        metadata,
        segments_per_half=int(config["segments_per_half"]),
        units_per_half=int(config["geometry_units_per_half"]),
        max_spans=int(config["max_spans_per_segment"]),
    )

    runtime = config["runtime"]
    api_key = os.environ.get(str(runtime["api_key_env"]), "")
    base_url = os.environ.get(str(runtime["base_url_env"]), "")
    if not api_key or not base_url:
        raise RuntimeError("DeepSeek runtime environment is not configured")
    primary_model = os.environ.get(
        str(runtime["primary_model_env"]),
        str(runtime["default_primary_model"]),
    )
    audit_model = os.environ.get(
        str(runtime["audit_model_env"]),
        str(runtime["default_audit_model"]),
    )
    provider = OpenAICompatibleProvider(base_url=base_url, api_key=api_key)
    primary_spec = _make_spec(
        config,
        model=primary_model,
        prompt_id="v8-behavior-observer-v2-primary",
    )
    audit_spec = _make_spec(
        config,
        model=audit_model,
        prompt_id="v8-behavior-observer-v2-audit",
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    primary_outputs, primary_results = _run_observer(
        profiles,
        repetitions=int(mode_config["observer_repetitions"]),
        output_dir=args.output_dir,
        provider=provider,
        spec=primary_spec,
        batch_size=int(runtime["batch_size"]),
        concurrency=int(runtime["concurrency"]),
        run_prefix="primary",
    )
    audit_author_count = int(mode_config["audit_authors"])
    audit_profiles = []
    if audit_author_count:
        audit_authors = sorted({
            str(profile["author_id"]) for profile in profiles
        })[:audit_author_count]
        audit_profiles = [
            profile for profile in profiles
            if str(profile["author_id"]) in set(audit_authors)
        ]
    audit_outputs, audit_results = (
        _run_observer(
            audit_profiles,
            repetitions=1,
            output_dir=args.output_dir,
            provider=provider,
            spec=audit_spec,
            batch_size=int(runtime["batch_size"]),
            concurrency=int(runtime["concurrency"]),
            run_prefix="audit",
        )
        if audit_profiles else ([], [])
    )
    all_results = primary_results + audit_results
    ready_calls = sum(
        result.get("status") == "STRUCTURED_STAGE_READY"
        for result in all_results
    )
    raw_call_parse_rate = ready_calls / max(1, len(all_results))
    expected_profiles = (
        len(profiles) * int(mode_config["observer_repetitions"])
        + len(audit_profiles)
    )
    ready_profiles = (
        len(profiles) * len(primary_outputs)
        + len(audit_profiles) * len(audit_outputs)
    )
    parse_rate = ready_profiles / max(1, expected_profiles)

    if not primary_outputs:
        decision = {
            "status": "V8_BEHAVIOR_V2_RUNTIME_STOP",
            "mode": args.mode,
            "authors": int(len(metadata)),
            "profiles": int(len(profiles)),
            "segments_per_half": int(config["segments_per_half"]),
            "observer_repetitions": int(mode_config["observer_repetitions"]),
            "observer": {
                "parse_rate": parse_rate,
                "repeated_event_f1": None,
                "cross_model_event_f1": None,
                "usable_events": 0,
            },
            "claim_boundary": str(config["claim_boundary"]),
        }
        _write_json(args.output_dir / "decision.json", decision)
        return 2

    repeated = observation_frame(profiles, primary_outputs)
    consensus = consensus_frame(
        repeated,
        required_fraction=float(config["consensus_required_fraction"]),
    )
    repeated_f1 = pairwise_event_f1(repeated)
    cross_model_f1 = float("nan")
    if audit_outputs:
        audit_frame = observation_frame(audit_profiles, audit_outputs)
        primary_subset = consensus.loc[
            consensus["author_id"].isin({
                str(profile["author_id"]) for profile in audit_profiles
            })
        ]
        cross_model_f1 = event_macro_f1(primary_subset, audit_frame)

    discovery_segments = consensus.loc[
        consensus["cohort_split"].astype(str).eq("discovery")
    ]
    prevalence_rows = []
    minimum_opportunities = int(config["pilot_min_opportunities_per_half"])
    gates = config["gates"]
    usable_events = []
    for event in EVENT_CODES:
        prevalence = float(discovery_segments[f"event::{event}"].mean())
        opportunity = EVENT_OPPORTUNITY[event]
        profile_opportunity = discovery_segments.groupby(
            "profile_id",
            observed=True,
        )[f"opportunity::{opportunity}"].sum()
        coverage = float(
            profile_opportunity.ge(minimum_opportunities).mean()
        )
        usable = bool(
            float(gates["minimum_event_prevalence"])
            <= prevalence
            <= float(gates["maximum_event_prevalence"])
            and coverage
            >= float(gates["minimum_author_opportunity_coverage"])
        )
        if usable:
            usable_events.append(event)
        prevalence_rows.append({
            "event_code": event,
            "discovery_prevalence": prevalence,
            "author_opportunity_coverage": coverage,
            "usable_for_rate_pilot": usable,
        })
    event_inventory = pd.DataFrame(prevalence_rows)
    baseline = fit_opportunity_event_baseline(
        discovery_segments,
        shrinkage=float(config["opportunity_shrinkage"]),
    )

    resolution_rows = []
    behavior_values_by_resolution: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    for resolution in map(int, config["resolutions"]):
        rates = profile_rate_features(
            consensus,
            baseline,
            resolution=resolution,
        )
        residual_columns = [
            f"residual::{event}" for event in usable_events
        ]
        if not residual_columns:
            continue
        behavior_values, authors, sides, _ = _standardized_matrix(
            rates,
            residual_columns,
        )
        condition = _condition_features(
            consensus,
            resolution=resolution,
            top_dimensions=int(config["condition_control_dimensions"]),
        )
        condition_columns = [
            column for column in condition
            if column.startswith("condition::")
            or column in {
                "mean_token_count",
                "std_token_count",
                "mean_span_count",
            }
        ]
        condition_values, condition_authors, condition_sides, _ = (
            _standardized_matrix(condition, condition_columns)
        )
        if not (
            np.array_equal(authors, condition_authors)
            and np.array_equal(sides, condition_sides)
        ):
            raise RuntimeError("behavior and condition profile order differ")
        behavior_auc = cross_modal_author_auc(
            behavior_values,
            behavior_values,
            authors,
            sides,
            metric="cosine",
        )
        condition_auc = cross_modal_author_auc(
            condition_values,
            condition_values,
            authors,
            sides,
            metric="cosine",
        )
        interval = spectral._bootstrap_interval(
            behavior_values,
            authors,
            sides,
            metric="cosine",
            seed=int(config["seed"]) + resolution,
            draws=int(config["bootstrap_draws"]),
        )
        delta = spectral._paired_auc_delta_interval(
            behavior_values,
            condition_values,
            authors,
            sides,
            metric="cosine",
            seed=int(config["seed"]) + 100 + resolution,
            draws=int(config["bootstrap_draws"]),
        )
        p_value = fresh_stats._fast_pairing_permutation_p(
            behavior_values,
            authors,
            sides,
            metric="cosine",
            observed=behavior_auc,
            seed=int(config["seed"]) + 200 + resolution,
            permutations=int(config["permutations"]),
        )
        resolution_rows.append({
            "resolution": resolution,
            "behavior_self_auc": behavior_auc,
            "behavior_cluster_estimate": interval[0],
            "behavior_ci_lower": interval[1],
            "behavior_ci_upper": interval[2],
            "author_permutation_p": p_value,
            "condition_length_self_auc": condition_auc,
            "behavior_minus_condition": delta[0],
            "delta_ci_lower": delta[1],
            "delta_ci_upper": delta[2],
            "behavior_dimensions": len(residual_columns),
        })
        behavior_values_by_resolution[resolution] = (
            behavior_values,
            authors,
            sides,
        )
    resolution_frame = pd.DataFrame(resolution_rows)
    anchors = _anchor_agreement(consensus, profiles)

    if args.mode == "smoke":
        status = (
            "V8_BEHAVIOR_V2_SMOKE_PASS"
            if parse_rate >= float(gates["minimum_parse_rate"])
            else "V8_BEHAVIOR_V2_SMOKE_STOP"
        )
        checks = {"parse_rate": status.endswith("PASS")}
    else:
        final_rows = resolution_frame.loc[
            resolution_frame["resolution"].eq(
                max(map(int, config["resolutions"]))
            )
        ] if not resolution_frame.empty else pd.DataFrame()
        final = final_rows.iloc[0] if len(final_rows) else None
        checks = {
            "parse_rate": parse_rate >= float(gates["minimum_parse_rate"]),
            "primary_repetitions_complete": (
                len(primary_outputs)
                == int(mode_config["observer_repetitions"])
            ),
            "repeated_event_f1": (
                np.isfinite(repeated_f1)
                and repeated_f1 >= float(gates["minimum_repeated_event_f1"])
            ),
            "cross_model_event_f1": (
                np.isfinite(cross_model_f1)
                and cross_model_f1
                >= float(gates["minimum_cross_model_event_f1"])
            ),
            "usable_events": (
                len(usable_events) >= int(gates["minimum_usable_events"])
            ),
            "behavior_self_auc": (
                final is not None
                and float(final["behavior_self_auc"])
                >= float(gates["minimum_behavior_self_auc"])
            ),
            "behavior_minus_condition": (
                final is not None
                and float(final["behavior_minus_condition"])
                >= float(gates["minimum_behavior_minus_condition_auc"])
            ),
            "author_permutation": (
                final is not None
                and float(final["author_permutation_p"])
                <= float(gates["maximum_author_permutation_p"])
            ),
        }
        status = (
            "V8_BEHAVIOR_V2_TECHNICAL_PILOT_PASS_HUMAN_GOLD_REQUIRED"
            if all(checks.values())
            else "V8_BEHAVIOR_V2_TECHNICAL_PILOT_STOP"
        )
    usage = {}
    for result in all_results:
        for key, value in (
            result.get("ledger", {})
            .get("provider_metadata", {})
            .get("usage", {})
            .items()
        ):
            usage[key] = usage.get(key, 0) + int(value)
    decision = {
        "status": status,
        "mode": args.mode,
        "checks": checks,
        "authors": int(len(metadata)),
        "profiles": int(len(profiles)),
        "segments_per_half": int(config["segments_per_half"]),
        "observer_repetitions": int(mode_config["observer_repetitions"]),
        "observer": {
            "calls": int(len(all_results)),
            "ready_calls": int(ready_calls),
            "parse_rate": parse_rate,
            "raw_call_parse_rate": raw_call_parse_rate,
            "completed_primary_repetitions": int(len(primary_outputs)),
            "repeated_event_f1": (
                float(repeated_f1) if np.isfinite(repeated_f1) else None
            ),
            "cross_model_event_f1": (
                float(cross_model_f1) if np.isfinite(cross_model_f1) else None
            ),
            "usable_events": int(len(usable_events)),
            "usable_event_codes": usable_events,
            "human_gold_available": False,
        },
        "provider_usage": usage,
        "new_llm_calls": int(sum(
            not result.get("ledger", {}).get("cache_hit", False)
            for result in all_results
        )),
        "external_labels_read": False,
        "claim_boundary": str(config["claim_boundary"]),
    }

    _write_json(args.output_dir / "config.resolved.json", {
        **config,
        "execution_mode": args.mode,
    })
    _write_json(args.output_dir / "decision.json", decision)
    event_inventory.to_csv(args.output_dir / "event_inventory.csv", index=False)
    anchors.to_csv(args.output_dir / "anchor_agreement.csv", index=False)
    resolution_frame.to_csv(
        args.output_dir / "resolution_metrics.csv",
        index=False,
    )
    (args.output_dir / "report.md").write_text(
        _report(decision, resolution_frame),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            source / "artifact_inventory.json",
            source / "config.resolved.json",
            pandora.PANDORA_COMMENTS_PATH,
            pandora.ELIGIBLE_AUTHORS_PATH,
        ],
        config_path=args.config,
        code_paths=[
            Path(__file__),
            ROOT / "suica_core" / "v8_behavior_v2.py",
            ROOT / "suica_core" / "v8_semantic.py",
            ROOT / "prompts" / "v8_behavior_observer_v2.txt",
            ROOT / "schemas" / "v8_behavior_observation_v2.schema.json",
        ],
        estimand_id=f"V8-I7-pandora-behavior-v2-{args.mode}",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0 if "PASS" in status else 2


if __name__ == "__main__":
    raise SystemExit(main())
