"""High-resolution, opportunity-conditioned behavior observations for SUICA V8."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

import jsonschema
import numpy as np
import pandas as pd


OPPORTUNITY_CODES = (
    "stance_opportunity",
    "affect_opportunity",
    "self_report_opportunity",
    "action_guidance_opportunity",
    "generativity_opportunity",
    "self_repair_opportunity",
)

EVENT_CODES = (
    "assertion_commitment",
    "epistemic_qualification",
    "explicit_acceptance",
    "explicit_rejection",
    "positive_affect_expression",
    "negative_affect_expression",
    "self_state_report",
    "self_action_report",
    "request_action",
    "recommend_action",
    "alternative_generation",
    "causal_explanation",
    "evidence_example",
    "self_repair",
)

EVENT_OPPORTUNITY = {
    "assertion_commitment": "stance_opportunity",
    "epistemic_qualification": "stance_opportunity",
    "explicit_acceptance": "stance_opportunity",
    "explicit_rejection": "stance_opportunity",
    "positive_affect_expression": "affect_opportunity",
    "negative_affect_expression": "affect_opportunity",
    "self_state_report": "self_report_opportunity",
    "self_action_report": "self_report_opportunity",
    "request_action": "action_guidance_opportunity",
    "recommend_action": "action_guidance_opportunity",
    "alternative_generation": "generativity_opportunity",
    "causal_explanation": "generativity_opportunity",
    "evidence_example": "generativity_opportunity",
    "self_repair": "self_repair_opportunity",
}


def normalize_behavior_v2_payload(
    payload: Any,
    *,
    profiles: list[dict[str, Any]],
) -> tuple[Any, dict[str, int]]:
    """Conservatively canonicalize duplicate binary events before validation.

    The normalizer never creates an opportunity or event. Duplicate
    opportunities/events are collapsed because the downstream object is
    segment-level presence/absence. A self-repair with invalid temporal
    provenance is dropped rather than repaired by inference.
    """
    counts = {
        "merged_duplicate_opportunities": 0,
        "merged_duplicate_events": 0,
        "dropped_invalid_opportunities": 0,
        "dropped_invalid_self_repairs": 0,
        "added_implied_opportunities": 0,
    }
    if not isinstance(payload, dict) or not isinstance(payload.get("profiles"), list):
        return payload, counts
    normalized = deepcopy(payload)
    source_profiles = {
        str(profile["profile_id"]): profile for profile in profiles
    }
    for profile_payload in normalized["profiles"]:
        if not isinstance(profile_payload, dict):
            continue
        source_profile = source_profiles.get(str(profile_payload.get("profile_id", "")))
        if source_profile is None or not isinstance(
            profile_payload.get("segments"), list
        ):
            continue
        source_segments = {
            str(segment["segment_id"]): segment
            for segment in source_profile["segments"]
        }
        for segment_payload in profile_payload["segments"]:
            if not isinstance(segment_payload, dict):
                continue
            segment_id = str(segment_payload.get("segment_id", ""))
            source_segment = source_segments.get(segment_id)
            if source_segment is None:
                continue
            span_order = {
                str(span["span_id"]): index
                for index, span in enumerate(source_segment["spans"])
            }
            opportunities = segment_payload.get("opportunities")
            if isinstance(opportunities, list):
                merged_opportunities: dict[str, set[str]] = {}
                for row in opportunities:
                    if not (
                        isinstance(row, dict)
                        and row.get("opportunity_code") in OPPORTUNITY_CODES
                        and isinstance(row.get("evidence_span_ids"), list)
                        and row["evidence_span_ids"]
                        and all(
                            str(value) in span_order
                            for value in row["evidence_span_ids"]
                        )
                    ):
                        counts["dropped_invalid_opportunities"] += 1
                        continue
                    code = str(row["opportunity_code"])
                    merged_opportunities.setdefault(code, set()).update(
                        map(str, row["evidence_span_ids"])
                    )
                counts["merged_duplicate_opportunities"] += (
                    len(opportunities) - len(merged_opportunities)
                )
                segment_payload["opportunities"] = [
                    {
                        "opportunity_code": code,
                        "evidence_span_ids": sorted(
                            evidence,
                            key=lambda value: (
                                span_order.get(value, len(span_order)),
                                value,
                            ),
                        ),
                    }
                    for code, evidence in merged_opportunities.items()
                ]

            events = segment_payload.get("events")
            if not (
                isinstance(events, list)
                and all(
                    isinstance(row, dict)
                    and row.get("event_code") in EVENT_CODES
                    and isinstance(row.get("evidence_span_ids"), list)
                    and isinstance(row.get("antecedent_span_ids"), list)
                    for row in events
                )
            ):
                continue
            grouped: dict[str, list[dict[str, Any]]] = {}
            for row in events:
                grouped.setdefault(str(row["event_code"]), []).append(row)
            canonical_events: list[dict[str, Any]] = []
            for code, rows in grouped.items():
                if code == "self_repair":
                    valid_rows = []
                    for row in rows:
                        evidence = list(map(str, row["evidence_span_ids"]))
                        antecedent = list(map(str, row["antecedent_span_ids"]))
                        known = all(
                            value in span_order for value in evidence + antecedent
                        )
                        ordered = bool(
                            known
                            and evidence
                            and antecedent
                            and min(span_order[value] for value in evidence)
                            > max(span_order[value] for value in antecedent)
                        )
                        if (
                            row.get("relation_type") == "self_revision"
                            and ordered
                        ):
                            valid_rows.append(row)
                        else:
                            counts["dropped_invalid_self_repairs"] += 1
                    if valid_rows:
                        chosen = min(
                            valid_rows,
                            key=lambda row: min(
                                span_order[str(value)]
                                for value in row["evidence_span_ids"]
                            ),
                        )
                        canonical_events.append({
                            **chosen,
                            "event_id": f"{segment_id}::{code}",
                        })
                        counts["merged_duplicate_events"] += len(valid_rows) - 1
                    continue
                if any(
                    row.get("relation_type") != "none"
                    or bool(row.get("antecedent_span_ids"))
                    for row in rows
                ):
                    canonical_events.extend(rows)
                    continue
                evidence = {
                    str(value)
                    for row in rows
                    for value in row["evidence_span_ids"]
                }
                canonical_events.append({
                    "event_id": f"{segment_id}::{code}",
                    "event_code": code,
                    "evidence_span_ids": sorted(
                        evidence,
                        key=lambda value: (
                            span_order.get(value, len(span_order)),
                            value,
                        ),
                    ),
                    "antecedent_span_ids": [],
                    "relation_type": "none",
                })
                counts["merged_duplicate_events"] += len(rows) - 1
            segment_payload["events"] = canonical_events
            present_opportunities = {
                str(row["opportunity_code"])
                for row in segment_payload.get("opportunities", [])
                if isinstance(row, dict)
            }
            for event in canonical_events:
                required = EVENT_OPPORTUNITY[str(event["event_code"])]
                if required in present_opportunities:
                    continue
                segment_payload.setdefault("opportunities", []).append({
                    "opportunity_code": required,
                    "evidence_span_ids": list(event["evidence_span_ids"]),
                })
                present_opportunities.add(required)
                counts["added_implied_opportunities"] += 1
            segment_payload["abstain"] = not bool(canonical_events)
    return normalized, counts


def validate_behavior_v2_payload(
    payload: Any,
    *,
    schema: dict[str, Any],
    profiles: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate exact profile, segment, span, opportunity, and event bindings."""
    jsonschema.Draft202012Validator(schema).validate(payload)
    expected_profiles = {
        str(profile["profile_id"]): profile for profile in profiles
    }
    observed_profiles = [
        str(profile["profile_id"]) for profile in payload["profiles"]
    ]
    if (
        set(observed_profiles) != set(expected_profiles)
        or len(observed_profiles) != len(expected_profiles)
    ):
        raise ValueError("behavior-v2 output must contain every profile exactly once")
    global_event_ids: set[str] = set()
    for profile_payload in payload["profiles"]:
        profile_id = str(profile_payload["profile_id"])
        source_profile = expected_profiles[profile_id]
        source_segments = {
            str(segment["segment_id"]): segment
            for segment in source_profile["segments"]
        }
        observed_segments = [
            str(segment["segment_id"])
            for segment in profile_payload["segments"]
        ]
        if (
            set(observed_segments) != set(source_segments)
            or len(observed_segments) != len(source_segments)
        ):
            raise ValueError("behavior-v2 must contain every segment exactly once")
        for segment_payload in profile_payload["segments"]:
            segment_id = str(segment_payload["segment_id"])
            source_spans = source_segments[segment_id]["spans"]
            span_order = {
                str(span["span_id"]): index
                for index, span in enumerate(source_spans)
            }
            known_spans = set(span_order)
            opportunities: set[str] = set()
            for row in segment_payload["opportunities"]:
                code = str(row["opportunity_code"])
                if code in opportunities:
                    raise ValueError("duplicate opportunity code within segment")
                cited = set(map(str, row["evidence_span_ids"]))
                if not cited.issubset(known_spans):
                    raise ValueError("opportunity evidence crosses segment boundary")
                opportunities.add(code)
            events: set[str] = set()
            for event in segment_payload["events"]:
                code = str(event["event_code"])
                if code in events:
                    raise ValueError("duplicate event code within segment")
                event_id = str(event["event_id"])
                if event_id != f"{segment_id}::{code}":
                    raise ValueError("event_id must be segment_id::event_code")
                if event_id in global_event_ids:
                    raise ValueError("event_id values must be globally unique")
                evidence = set(map(str, event["evidence_span_ids"]))
                antecedent = set(map(str, event["antecedent_span_ids"]))
                if not evidence.issubset(known_spans) or not antecedent.issubset(
                    known_spans
                ):
                    raise ValueError("event evidence crosses segment boundary")
                if EVENT_OPPORTUNITY[code] not in opportunities:
                    raise ValueError("event is missing its required opportunity")
                relation = str(event["relation_type"])
                if code == "self_repair":
                    if relation != "self_revision" or not antecedent:
                        raise ValueError("self_repair requires an antecedent")
                    if min(span_order[value] for value in evidence) <= max(
                        span_order[value] for value in antecedent
                    ):
                        raise ValueError("self_repair evidence must follow its antecedent")
                elif relation != "none" or antecedent:
                    raise ValueError("non-repair events cannot cite antecedents")
                events.add(code)
                global_event_ids.add(event_id)
            if bool(segment_payload["abstain"]) != (len(events) == 0):
                raise ValueError("abstain must match an empty event list")
    return payload


def observation_frame(
    profiles: list[dict[str, Any]],
    outputs: list[dict[str, Any]],
) -> pd.DataFrame:
    """Convert repeated structured outputs to one row per segment and run."""
    metadata = {
        str(profile["profile_id"]): profile for profile in profiles
    }
    rows: list[dict[str, Any]] = []
    for repetition, output in enumerate(outputs):
        for profile_payload in output["profiles"]:
            profile_id = str(profile_payload["profile_id"])
            profile = metadata[profile_id]
            source_segments = {
                str(segment["segment_id"]): segment
                for segment in profile["segments"]
            }
            for segment_payload in profile_payload["segments"]:
                segment_id = str(segment_payload["segment_id"])
                segment = source_segments[segment_id]
                opportunities = {
                    str(row["opportunity_code"])
                    for row in segment_payload["opportunities"]
                }
                events = {
                    str(row["event_code"]) for row in segment_payload["events"]
                }
                row: dict[str, Any] = {
                    "repetition": repetition,
                    "profile_id": profile_id,
                    "author_id": str(profile["author_id"]),
                    "side": str(profile["side"]),
                    "cohort_split": str(profile["cohort_split"]),
                    "segment_id": segment_id,
                    "segment_index": int(segment["segment_index"]),
                    "condition": str(segment["condition"]),
                    "token_count": int(segment["token_count"]),
                    "span_count": int(len(segment["spans"])),
                }
                row.update({
                    f"opportunity::{code}": int(code in opportunities)
                    for code in OPPORTUNITY_CODES
                })
                row.update({
                    f"event::{code}": int(code in events) for code in EVENT_CODES
                })
                rows.append(row)
    return pd.DataFrame(rows)


def consensus_frame(
    repeated: pd.DataFrame,
    *,
    required_fraction: float = 1.0,
) -> pd.DataFrame:
    """Create a deterministic repeated-observer consensus per segment."""
    key = [
        "profile_id",
        "author_id",
        "side",
        "cohort_split",
        "segment_id",
        "segment_index",
        "condition",
        "token_count",
        "span_count",
    ]
    columns = [
        column
        for column in repeated
        if column.startswith("opportunity::") or column.startswith("event::")
    ]
    grouped = repeated.groupby(key, observed=True, sort=False)[columns].mean()
    return grouped.ge(float(required_fraction)).astype(int).reset_index()


@dataclass(frozen=True)
class OpportunityBaseline:
    """Discovery-fitted event probabilities conditional on opportunity/context."""

    global_probability: dict[str, float]
    condition_probability: dict[tuple[str, str], float]

    def probability(self, event_code: str, condition: str) -> float:
        return float(
            self.condition_probability.get(
                (event_code, condition),
                self.global_probability[event_code],
            )
        )


@dataclass(frozen=True)
class LeaveOneAuthorOutOpportunityBaseline:
    """Opportunity baseline that excludes the target author's own segments."""

    global_probability: dict[tuple[str, str], float]
    condition_probability: dict[tuple[str, str, str], float]
    fallback: OpportunityBaseline

    def global_value(self, event_code: str, author_id: str) -> float:
        return float(
            self.global_probability.get(
                (event_code, author_id),
                self.fallback.global_probability[event_code],
            )
        )

    def probability(
        self,
        event_code: str,
        condition: str,
        author_id: str,
    ) -> float:
        return float(
            self.condition_probability.get(
                (event_code, condition, author_id),
                self.global_value(event_code, author_id),
            )
        )


def fit_weighted_opportunity_event_baseline(
    segments: pd.DataFrame,
    *,
    shrinkage: float = 8.0,
) -> OpportunityBaseline:
    """Fit a baseline to binary or repeated-observer mean event indicators."""
    global_probability: dict[str, float] = {}
    condition_probability: dict[tuple[str, str], float] = {}
    for event in EVENT_CODES:
        opportunity = EVENT_OPPORTUNITY[event]
        weights = segments[f"opportunity::{opportunity}"].to_numpy(float)
        outcomes = segments[f"event::{event}"].to_numpy(float)
        total = float(weights.sum())
        positives = float(outcomes.sum())
        global_value = (positives + 1.0) / (total + 2.0)
        global_probability[event] = global_value
        for condition, group in segments.groupby(
            "condition",
            observed=True,
            sort=False,
        ):
            group_weights = group[
                f"opportunity::{opportunity}"
            ].to_numpy(float)
            group_outcomes = group[f"event::{event}"].to_numpy(float)
            denominator = float(
                group_weights.sum() + float(shrinkage)
            )
            condition_probability[(event, str(condition))] = (
                float(
                    (
                        group_outcomes.sum()
                        + float(shrinkage) * global_value
                    )
                    / denominator
                )
                if denominator > 0
                else global_value
            )
    return OpportunityBaseline(
        global_probability=global_probability,
        condition_probability=condition_probability,
    )


def fit_leave_one_author_out_baseline(
    segments: pd.DataFrame,
    *,
    target_authors: list[str],
    shrinkage: float = 8.0,
) -> LeaveOneAuthorOutOpportunityBaseline:
    """Fit P(event | opportunity, condition) without target-author leakage."""
    fallback = fit_weighted_opportunity_event_baseline(
        segments,
        shrinkage=shrinkage,
    )
    global_probability: dict[tuple[str, str], float] = {}
    condition_probability: dict[tuple[str, str, str], float] = {}
    author_values = segments["author_id"].astype(str)
    for author_id in map(str, target_authors):
        training = segments.loc[author_values.ne(author_id)]
        for event in EVENT_CODES:
            opportunity = EVENT_OPPORTUNITY[event]
            weights = training[
                f"opportunity::{opportunity}"
            ].to_numpy(float)
            outcomes = training[f"event::{event}"].to_numpy(float)
            global_value = float(
                (outcomes.sum() + 1.0) / (weights.sum() + 2.0)
            )
            global_probability[(event, author_id)] = global_value
            for condition, group in training.groupby(
                "condition",
                observed=True,
                sort=False,
            ):
                group_weights = group[
                    f"opportunity::{opportunity}"
                ].to_numpy(float)
                group_outcomes = group[f"event::{event}"].to_numpy(float)
                denominator = float(
                    group_weights.sum() + float(shrinkage)
                )
                condition_probability[(
                    event,
                    str(condition),
                    author_id,
                )] = (
                    float(
                        (
                            group_outcomes.sum()
                            + float(shrinkage) * global_value
                        )
                        / denominator
                    )
                    if denominator > 0
                    else global_value
                )
    return LeaveOneAuthorOutOpportunityBaseline(
        global_probability=global_probability,
        condition_probability=condition_probability,
        fallback=fallback,
    )


def fit_opportunity_event_baseline(
    segments: pd.DataFrame,
    *,
    shrinkage: float = 8.0,
) -> OpportunityBaseline:
    """Fit P(event | required opportunity, condition) on discovery rows only."""
    global_probability: dict[str, float] = {}
    condition_probability: dict[tuple[str, str], float] = {}
    for event in EVENT_CODES:
        opportunity = EVENT_OPPORTUNITY[event]
        available = segments.loc[
            segments[f"opportunity::{opportunity}"].eq(1)
        ]
        positives = float(available[f"event::{event}"].sum())
        total = float(len(available))
        global_value = (positives + 1.0) / (total + 2.0)
        global_probability[event] = global_value
        for condition, group in available.groupby(
            "condition",
            observed=True,
            sort=False,
        ):
            condition_probability[(event, str(condition))] = float(
                (
                    group[f"event::{event}"].sum()
                    + float(shrinkage) * global_value
                )
                / (len(group) + float(shrinkage))
            )
    return OpportunityBaseline(
        global_probability=global_probability,
        condition_probability=condition_probability,
    )


def profile_rate_features(
    segments: pd.DataFrame,
    baseline: OpportunityBaseline,
    *,
    resolution: int,
) -> pd.DataFrame:
    """Aggregate opportunity-standardized event residuals per profile."""
    selected_rows = []
    for _, group in segments.groupby("profile_id", observed=True, sort=False):
        ordered = group.sort_values("segment_index", kind="stable")
        count = min(int(resolution), len(ordered))
        indices = np.unique(
            np.linspace(0, len(ordered) - 1, num=count, dtype=int)
        )
        selected_rows.append(ordered.iloc[indices])
    selected = pd.concat(selected_rows, ignore_index=True)
    rows: list[dict[str, Any]] = []
    for profile_id, group in selected.groupby(
        "profile_id",
        observed=True,
        sort=False,
    ):
        first = group.iloc[0]
        row: dict[str, Any] = {
            "profile_id": str(profile_id),
            "author_id": str(first["author_id"]),
            "side": str(first["side"]),
            "cohort_split": str(first["cohort_split"]),
        }
        for event in EVENT_CODES:
            opportunity = EVENT_OPPORTUNITY[event]
            available = group.loc[
                group[f"opportunity::{opportunity}"].eq(1)
            ]
            probabilities = np.asarray([
                baseline.probability(event, str(condition))
                for condition in available["condition"]
            ])
            outcomes = available[f"event::{event}"].to_numpy(float)
            variance = float(np.sum(probabilities * (1.0 - probabilities)))
            residual = (
                float(np.sum(outcomes - probabilities))
                / np.sqrt(variance + 1e-8)
                if len(available)
                else float("nan")
            )
            row[f"residual::{event}"] = residual
            row[f"rate::{event}"] = (
                float(outcomes.mean()) if len(outcomes) else float("nan")
            )
            row[f"opportunities::{event}"] = int(len(available))
        rows.append(row)
    return pd.DataFrame(rows)


def pairwise_event_f1(repeated: pd.DataFrame) -> float:
    """Mean pairwise macro-F1 across observable event codes and runs.

    Event codes that are absent from both runs are excluded rather than counted
    as perfect agreement. This prevents sparse all-negative segments from
    inflating observer reliability.
    """
    repetitions = sorted(repeated["repetition"].unique())
    if len(repetitions) < 2:
        return float("nan")
    values = []
    event_columns = [f"event::{code}" for code in EVENT_CODES]
    indexed = {
        repetition: repeated.loc[
            repeated["repetition"].eq(repetition)
        ].set_index(["profile_id", "segment_id"])[event_columns]
        for repetition in repetitions
    }
    for left_index, left_rep in enumerate(repetitions):
        for right_rep in repetitions[left_index + 1:]:
            values.append(
                event_macro_f1(
                    indexed[left_rep].reset_index(),
                    indexed[right_rep].reset_index(),
                )
            )
    return float(np.mean(values)) if values else float("nan")


def event_macro_f1(
    first: pd.DataFrame,
    second: pd.DataFrame,
) -> float:
    """Return event-wise macro-F1 after exact profile/segment alignment."""
    keys = ["profile_id", "segment_id"]
    event_columns = [f"event::{code}" for code in EVENT_CODES]
    left = first.set_index(keys)[event_columns]
    right = second.set_index(keys)[event_columns]
    shared = left.index.intersection(right.index)
    if not len(shared):
        return float("nan")
    scores = []
    for column in event_columns:
        left_values = left.loc[shared, column].to_numpy(int)
        right_values = right.loc[shared, column].to_numpy(int)
        true_positive = int(np.sum((left_values == 1) & (right_values == 1)))
        false_positive = int(np.sum((left_values == 0) & (right_values == 1)))
        false_negative = int(np.sum((left_values == 1) & (right_values == 0)))
        denominator = 2 * true_positive + false_positive + false_negative
        if denominator:
            scores.append(2.0 * true_positive / denominator)
    return float(np.mean(scores)) if scores else float("nan")
