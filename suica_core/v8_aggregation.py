"""Deterministic aggregation for frozen V8 semantic observations.

The semantic transducer may label observation-level events. It may not emit or
aggregate person-level personality, diagnostic, or clinical judgements.
"""
from __future__ import annotations

from collections import Counter
import math
from typing import Any, Iterable


ALLOWED_EVENT_FIELDS = frozenset({
    "observation_id",
    "segment_id",
    "event_type",
    "source_span_ids",
    "polarity",
    "intensity",
    "confidence",
    "abstain",
})

ALLOWED_EVENT_TYPES = frozenset({
    "discourse_stance",
    "affect_expression",
    "self_reference",
    "directive_expression",
    "novelty_expression",
    "interaction_response",
    "abstain",
})


def aggregate_semantic_observations(
    observations: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Aggregate validated event records into a technical observation summary."""
    rows = list(observations)
    if not rows:
        return {
            "observation_count": 0,
            "abstention_rate": 1.0,
            "event_type_counts": {},
            "mean_confidence": None,
            "mean_intensity": None,
        }

    for index, row in enumerate(rows):
        unknown = set(row).difference(ALLOWED_EVENT_FIELDS)
        if unknown:
            raise ValueError(f"observation[{index}] has forbidden fields: {sorted(unknown)}")
        missing = ALLOWED_EVENT_FIELDS.difference(row)
        if missing:
            raise ValueError(f"observation[{index}] is missing fields: {sorted(missing)}")
        if row["event_type"] not in ALLOWED_EVENT_TYPES:
            raise ValueError(f"observation[{index}] has unsupported event_type")
        for field in ("observation_id", "segment_id"):
            if not isinstance(row[field], str) or not row[field]:
                raise ValueError(f"observation[{index}].{field} must be a non-empty string")
        spans = row["source_span_ids"]
        if (
            not isinstance(spans, list)
            or not spans
            or len(set(spans)) != len(spans)
            or any(not isinstance(value, str) or not value for value in spans)
        ):
            raise ValueError(f"observation[{index}].source_span_ids must be non-empty and unique")
        for field, lower, upper in (
            ("polarity", -1.0, 1.0),
            ("intensity", 0.0, 1.0),
            ("confidence", 0.0, 1.0),
        ):
            value = row[field]
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(float(value))
                or not lower <= float(value) <= upper
            ):
                raise ValueError(
                    f"observation[{index}].{field} must be finite in [{lower}, {upper}]"
                )
        if not isinstance(row["abstain"], bool):
            raise ValueError(f"observation[{index}].abstain must be boolean")

    usable = [row for row in rows if not bool(row["abstain"])]
    confidences = [float(row["confidence"]) for row in usable]
    intensities = [float(row["intensity"]) for row in usable]
    counts = Counter(str(row["event_type"]) for row in usable)
    return {
        "observation_count": len(rows),
        "abstention_rate": 1.0 - (len(usable) / len(rows)),
        "event_type_counts": dict(sorted(counts.items())),
        "mean_confidence": sum(confidences) / len(confidences) if confidences else None,
        "mean_intensity": sum(intensities) / len(intensities) if intensities else None,
    }
