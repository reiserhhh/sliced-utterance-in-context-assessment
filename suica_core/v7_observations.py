"""Observation operators for SUICA V7 psychometric projection.

V7 treats slicing as a competing observation design, not as a fixed truth about
language.  The functions in this module never read personality labels.  They
only turn provenance-preserving comment records into repeated textual
observations for an author-level measurement pipeline.
"""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .suica import PERSONALITY_LEAK_RE, sentence_split, tokenize


@dataclass(frozen=True)
class ObservationSpec:
    """A declared way to turn one author's text into observations."""

    name: str
    kind: str
    window_tokens: int = 128
    stride_tokens: int = 128
    max_tokens: int = 160
    min_tokens: int = 12
    max_units_per_user: int = 32
    max_source_comments_per_user: int | None = None
    max_source_tokens_per_user: int | None = None
    source_boundary_mode: str = "cross"
    offset_tokens: int = 0
    offset_strategy: str = "fixed"
    members: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe provenance representation."""
        return asdict(self)


def _stable_int(value: str, *, salt: str) -> int:
    digest = hashlib.sha256(f"{salt}::{value}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def deterministic_author_split(user_id: str, *, seed: int = 20260714) -> str:
    """Assign an author to discovery/calibration/confirmation without labels."""
    bucket = _stable_int(str(user_id), salt=f"suica-v7-split-{seed}") % 10_000
    if bucket < 6_000:
        return "discovery"
    if bucket < 8_000:
        return "calibration"
    return "confirmation"


def _evenly_spaced_indices(length: int, limit: int) -> np.ndarray:
    """Choose chronological records without privileging a single time region."""
    if limit <= 0 or length <= limit:
        return np.arange(length, dtype=int)
    return np.unique(np.linspace(0, length - 1, num=limit, dtype=int))


def canonicalize_comments(
    comments: pd.DataFrame,
    *,
    user_col: str = "author",
    text_col: str = "body",
    order_col: str | None = "created_utc",
    condition_col: str | None = "subreddit",
    min_tokens: int = 12,
    mask_personality_terms: bool = False,
) -> pd.DataFrame:
    """Validate and normalize raw records while retaining context provenance.

    The primary V7 arm keeps text raw.  Term masking is optional and exists for
    future label-linked protocols; it is never silently enabled.
    """
    missing = [col for col in (user_col, text_col) if col not in comments]
    if missing:
        raise ValueError(f"Required raw-comment columns missing: {missing}")
    frame = pd.DataFrame(
        {
            "user_id": comments[user_col].astype(str),
            "text": comments[text_col].fillna("").astype(str),
            "source_row": np.arange(len(comments), dtype=int),
        }
    )
    observed_order = (
        pd.to_numeric(comments[order_col], errors="coerce").reset_index(drop=True)
        if order_col and order_col in comments
        else pd.Series(np.nan, index=frame.index, dtype=float)
    )
    # Retain provenance instead of silently converting input row order into a
    # temporal variable. Other operators may still use stable row order, but a
    # temporal claim must explicitly refuse records without observed ordering.
    observed_mask = observed_order.notna().to_numpy(bool)
    frame["order_observed"] = observed_mask
    frame["order"] = np.where(observed_mask, observed_order.to_numpy(float), frame["source_row"].to_numpy(float))
    frame["condition"] = (
        comments[condition_col].fillna("<unknown>").astype(str)
        if condition_col and condition_col in comments
        else "<unknown>"
    )
    frame["text"] = frame["text"].str.strip()
    frame = frame.loc[frame["user_id"].ne("") & frame["text"].ne("")].copy()
    frame["has_personality_term"] = frame["text"].map(lambda value: bool(PERSONALITY_LEAK_RE.search(value)))
    if mask_personality_terms:
        frame["text"] = frame["text"].map(lambda value: PERSONALITY_LEAK_RE.sub("[PERSONALITY_TERM]", value))
    frame["token_count"] = frame["text"].map(lambda value: len(tokenize(value)))
    frame = frame.loc[frame["token_count"] >= int(min_tokens)].copy()
    return frame.sort_values(["user_id", "order", "source_row"], kind="stable").reset_index(drop=True)


def select_reference_authors(
    comments: pd.DataFrame,
    *,
    min_comments_per_user: int,
    max_users: int | None,
    seed: int,
    exclude_user_ids: set[str] | None = None,
    cohort_salt: str = "",
) -> pd.DataFrame:
    """Create a deterministic local reference cohort from raw observations.

    `exclude_user_ids` supports a truly fresh author cohort after an earlier
    engineering audit. `cohort_salt` changes deterministic selection without
    changing the held-out author split assignment.
    """
    counts = comments.groupby("user_id", observed=True).size()
    eligible = counts.loc[counts >= int(min_comments_per_user)].index.astype(str).tolist()
    excluded = {str(value) for value in (exclude_user_ids or set())}
    eligible = [user for user in eligible if user not in excluded]
    eligible.sort(key=lambda user: _stable_int(user, salt=f"suica-v7-cohort-{seed}-{cohort_salt}"))
    if max_users is not None and max_users > 0:
        eligible = eligible[: int(max_users)]
    selected = comments.loc[comments["user_id"].isin(set(eligible))].copy()
    selected["split"] = selected["user_id"].map(lambda user: deterministic_author_split(user, seed=seed))
    return selected.sort_values(["user_id", "order", "source_row"], kind="stable").reset_index(drop=True)


def _capped_author_rows(group: pd.DataFrame, max_units: int) -> pd.DataFrame:
    ordered = group.sort_values(["order", "source_row"], kind="stable").reset_index(drop=True)
    return ordered.iloc[_evenly_spaced_indices(len(ordered), max_units)].copy()


def cap_author_source_comments(comments: pd.DataFrame, max_comments_per_user: int) -> pd.DataFrame:
    """Cap source comments before slicing with deterministic temporal coverage.

    This cap is deliberately distinct from an operator's output-unit cap.  It
    lets competing operators see the same source-comment panel before their
    own slicing rule changes the number of produced units.
    """
    if int(max_comments_per_user) < 1:
        raise ValueError("max_comments_per_user must be at least one.")
    if comments.empty:
        return comments.copy()
    rows = [
        _capped_author_rows(group, int(max_comments_per_user))
        for _, group in comments.groupby("user_id", sort=False, observed=True)
    ]
    return pd.concat(rows, ignore_index=True).sort_values(
        ["user_id", "order", "source_row"], kind="stable"
    ).reset_index(drop=True)


def _source_limit(spec: ObservationSpec) -> int:
    return int(spec.max_source_comments_per_user or spec.max_units_per_user)


def _apply_source_token_budget(group: pd.DataFrame, spec: ObservationSpec) -> pd.DataFrame:
    """Apply one common sequential source-token budget without changing IDs.

    The budget is an engineering control for operator comparisons, not a text
    cleaning method.  Every operator receives the same capped source stream;
    the final partially retained comment keeps its original provenance.
    """
    budget = spec.max_source_tokens_per_user
    if budget is None or int(budget) <= 0:
        return group.copy()
    remaining = int(budget)
    rows: list[pd.Series] = []
    for _, value in group.sort_values(["order", "source_row"], kind="stable").iterrows():
        if remaining <= 0:
            break
        tokens = tokenize(str(value["text"]))
        kept = tokens[:remaining]
        if not kept:
            continue
        row = value.copy()
        row["text"] = " ".join(kept)
        row["token_count"] = int(len(kept))
        row["has_personality_term"] = bool(PERSONALITY_LEAK_RE.search(str(row["text"])))
        rows.append(row)
        remaining -= len(kept)
    if not rows:
        return group.iloc[0:0].copy()
    return pd.DataFrame(rows).reset_index(drop=True)


def _prepared_author_rows(group: pd.DataFrame, spec: ObservationSpec) -> pd.DataFrame:
    """Return a common source panel for one author under a declared operator."""
    capped = _capped_author_rows(group, _source_limit(spec))
    return _apply_source_token_budget(capped, spec)


def prepare_source_panel(comments: pd.DataFrame, spec: ObservationSpec) -> pd.DataFrame:
    """Freeze the source-comment panel shared by competing V7 operators."""
    if comments.empty:
        return comments.copy()
    rows = [
        _prepared_author_rows(group, spec)
        for _, group in comments.groupby("user_id", sort=False, observed=True)
    ]
    rows = [row for row in rows if not row.empty]
    if not rows:
        return comments.iloc[0:0].copy()
    return pd.concat(rows, ignore_index=True).sort_values(
        ["user_id", "order", "source_row"], kind="stable"
    ).reset_index(drop=True)


def _row(
    *,
    user_id: str,
    split: str,
    text: str,
    source_rows: Iterable[int],
    source_token_weights: Iterable[int] | None = None,
    order_start: float,
    order_end: float,
    condition: str,
    operator: str,
    unit_index: int,
    has_personality_term: bool,
) -> dict[str, Any]:
    source_values = [int(value) for value in source_rows]
    source_weights = [int(value) for value in source_token_weights] if source_token_weights is not None else [1] * len(source_values)
    if len(source_weights) != len(source_values):
        raise ValueError("source_token_weights must align with source_rows.")
    return {
        "user_id": str(user_id),
        "split": str(split),
        "unit_id": f"{operator}:{user_id}:{unit_index}",
        "unit_index": int(unit_index),
        "text": str(text),
        "token_count": int(len(tokenize(text))),
        "source_rows": ",".join(str(value) for value in source_values),
        "source_token_weights": ",".join(str(max(value, 0)) for value in source_weights),
        "source_count": int(len(source_values)),
        "order_start": float(order_start),
        "order_end": float(order_end),
        "condition": str(condition),
        "operator": operator,
        "has_personality_term": bool(has_personality_term),
    }


def _whole_units(comments: pd.DataFrame, spec: ObservationSpec) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for user_id, group in comments.groupby("user_id", sort=False, observed=True):
        capped = _prepared_author_rows(group, spec)
        if capped.empty:
            continue
        source_rows = capped["source_row"].astype(int).tolist()
        rows.append(
            _row(
                user_id=str(user_id), split=str(capped["split"].iloc[0]),
                text="\n\n".join(capped["text"].tolist()), source_rows=source_rows,
                source_token_weights=capped["token_count"].astype(int).tolist(),
                order_start=float(capped["order"].min()), order_end=float(capped["order"].max()),
                condition="<whole_author_text>", operator=spec.name, unit_index=0,
                has_personality_term=bool(capped["has_personality_term"].any()),
            )
        )
    return rows


def _native_units(comments: pd.DataFrame, spec: ObservationSpec) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for user_id, group in comments.groupby("user_id", sort=False, observed=True):
        capped = _prepared_author_rows(group, spec)
        if capped.empty:
            continue
        for index, value in enumerate(capped.itertuples(index=False)):
            rows.append(
                _row(
                    user_id=str(user_id), split=str(value.split), text=str(value.text),
                    source_rows=[int(value.source_row)], source_token_weights=[int(value.token_count)], order_start=float(value.order), order_end=float(value.order),
                    condition=str(value.condition), operator=spec.name, unit_index=index,
                    has_personality_term=bool(value.has_personality_term),
                )
            )
    return rows


def _fixed_offset(user_id: str, spec: ObservationSpec) -> int:
    """Return a deterministic fixed-window phase without changing source text."""
    window = max(1, int(spec.window_tokens))
    if spec.offset_strategy == "fixed":
        return int(spec.offset_tokens) % window
    if spec.offset_strategy == "author_hash":
        return _stable_int(str(user_id), salt=f"suica-v7-offset::{spec.name}") % window
    raise ValueError(f"Unsupported fixed-window offset strategy: {spec.offset_strategy}")


def _fixed_stream(capped: pd.DataFrame, spec: ObservationSpec) -> list[dict[str, Any]]:
    """Build token records with exact source provenance for cross-comment slices."""
    records: list[dict[str, Any]] = []
    values = list(capped.itertuples(index=False))
    for position, value in enumerate(values):
        for token in tokenize(str(value.text)):
            records.append({
                "token": token,
                "source_row": int(value.source_row),
                "order": float(value.order),
                "condition": str(value.condition),
                "has_personality_term": bool(value.has_personality_term),
            })
        if spec.source_boundary_mode == "cross_marker" and position < len(values) - 1:
            records.append({
                "token": "SUICA_BOUNDARY",
                "source_row": None,
                "order": float(value.order),
                "condition": "<boundary_marker>",
                "has_personality_term": False,
            })
    return records


def _fixed_row_from_records(
    *,
    user_id: str,
    split: str,
    records: list[dict[str, Any]],
    spec: ObservationSpec,
    unit_index: int,
) -> dict[str, Any] | None:
    usable = [record for record in records if record["source_row"] is not None]
    if len(usable) < spec.min_tokens:
        return None
    source_rows = list(dict.fromkeys(int(record["source_row"]) for record in usable))
    source_weights = [sum(int(record["source_row"]) == source_row for record in usable) for source_row in source_rows]
    conditions = list(dict.fromkeys(str(record["condition"]) for record in usable))
    condition = conditions[0] if len(conditions) == 1 else "<mixed_source_conditions>"
    return _row(
        user_id=user_id,
        split=split,
        text=" ".join(str(record["token"]) for record in records),
        source_rows=source_rows,
        source_token_weights=source_weights,
        order_start=min(float(record["order"]) for record in usable),
        order_end=max(float(record["order"]) for record in usable),
        condition=condition,
        operator=spec.name,
        unit_index=unit_index,
        has_personality_term=bool(any(record["has_personality_term"] for record in usable)),
    )


def _fixed_cross_units(capped: pd.DataFrame, user_id: str, spec: ObservationSpec) -> list[dict[str, Any]]:
    stream = _fixed_stream(capped, spec)
    if not stream:
        return []
    window = max(1, int(spec.window_tokens))
    stride = max(1, int(spec.stride_tokens))
    offset = _fixed_offset(user_id, spec)
    rows: list[dict[str, Any]] = []
    for start in range(-offset, len(stream), stride):
        end = min(len(stream), start + window)
        left = max(0, start)
        if end <= left:
            continue
        row = _fixed_row_from_records(
            user_id=user_id,
            split=str(capped["split"].iloc[0]),
            records=stream[left:end],
            spec=spec,
            unit_index=len(rows),
        )
        if row is not None:
            rows.append(row)
        if len(rows) >= spec.max_units_per_user:
            break
    return rows


def _fixed_within_comment_units(capped: pd.DataFrame, user_id: str, spec: ObservationSpec) -> list[dict[str, Any]]:
    window = max(1, int(spec.window_tokens))
    stride = max(1, int(spec.stride_tokens))
    offset = _fixed_offset(user_id, spec)
    rows: list[dict[str, Any]] = []
    for value in capped.itertuples(index=False):
        tokens = tokenize(str(value.text))
        for start in range(-offset, len(tokens), stride):
            end = min(len(tokens), start + window)
            left = max(0, start)
            if end - left < spec.min_tokens:
                continue
            row = _row(
                user_id=user_id,
                split=str(value.split),
                text=" ".join(tokens[left:end]),
                source_rows=[int(value.source_row)], source_token_weights=[end - left],
                order_start=float(value.order),
                order_end=float(value.order),
                condition=str(value.condition),
                operator=spec.name,
                unit_index=len(rows),
                has_personality_term=bool(value.has_personality_term),
            )
            rows.append(row)
            if len(rows) >= spec.max_units_per_user:
                return rows
    return rows


def _fixed_units(comments: pd.DataFrame, spec: ObservationSpec) -> list[dict[str, Any]]:
    """Produce fixed-width slices with declared boundary and offset behaviour."""
    if spec.source_boundary_mode not in {"cross", "within", "cross_marker"}:
        raise ValueError(f"Unsupported fixed source-boundary mode: {spec.source_boundary_mode}")
    rows: list[dict[str, Any]] = []
    for user_id, group in comments.groupby("user_id", sort=False, observed=True):
        capped = _prepared_author_rows(group, spec)
        if capped.empty:
            continue
        if spec.source_boundary_mode == "within":
            rows.extend(_fixed_within_comment_units(capped, str(user_id), spec))
        else:
            rows.extend(_fixed_cross_units(capped, str(user_id), spec))
    return rows


def _semantic_units(comments: pd.DataFrame, spec: ObservationSpec) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for user_id, group in comments.groupby("user_id", sort=False, observed=True):
        capped = _prepared_author_rows(group, spec)
        if capped.empty:
            continue
        unit_index = 0
        for value in capped.itertuples(index=False):
            buffer: list[str] = []
            buffer_tokens = 0
            for sentence in sentence_split(str(value.text)):
                sentence_tokens = tokenize(sentence)
                if not sentence_tokens:
                    continue
                if buffer and buffer_tokens + len(sentence_tokens) > spec.max_tokens and buffer_tokens >= spec.min_tokens:
                    rows.append(
                        _row(
                            user_id=str(user_id), split=str(value.split), text=" ".join(buffer),
                            source_rows=[int(value.source_row)], source_token_weights=[buffer_tokens], order_start=float(value.order), order_end=float(value.order),
                            condition=str(value.condition), operator=spec.name, unit_index=unit_index,
                            has_personality_term=bool(value.has_personality_term),
                        )
                    )
                    unit_index += 1
                    if unit_index >= spec.max_units_per_user:
                        break
                    buffer, buffer_tokens = [], 0
                buffer.extend(sentence_tokens)
                buffer_tokens += len(sentence_tokens)
            if unit_index >= spec.max_units_per_user:
                break
            if buffer_tokens >= spec.min_tokens:
                rows.append(
                    _row(
                        user_id=str(user_id), split=str(value.split), text=" ".join(buffer),
                        source_rows=[int(value.source_row)], source_token_weights=[buffer_tokens], order_start=float(value.order), order_end=float(value.order),
                        condition=str(value.condition), operator=spec.name, unit_index=unit_index,
                        has_personality_term=bool(value.has_personality_term),
                    )
                )
                unit_index += 1
            if unit_index >= spec.max_units_per_user:
                break
    return rows


def build_observations(comments: pd.DataFrame, spec: ObservationSpec) -> pd.DataFrame:
    """Apply one declared observation operator to canonicalized comment rows."""
    if spec.kind == "nested":
        raise ValueError("Nested operators are constructed from base author features, not raw units.")
    required = {"user_id", "split", "text", "source_row", "order", "condition", "has_personality_term"}
    missing = sorted(required.difference(comments.columns))
    if missing:
        raise ValueError(f"Canonical comment columns missing: {missing}")
    builders = {"whole": _whole_units, "native": _native_units, "fixed": _fixed_units, "semantic": _semantic_units}
    if spec.kind not in builders:
        raise ValueError(f"Unsupported V7 observation operator: {spec.kind}")
    out = pd.DataFrame(builders[spec.kind](comments, spec))
    if out.empty:
        return pd.DataFrame(columns=["user_id", "split", "unit_id", "unit_index", "text", "token_count"])
    return out.loc[out["token_count"] >= spec.min_tokens].sort_values(
        ["user_id", "unit_index"], kind="stable"
    ).reset_index(drop=True)


def observation_manifest(comments: pd.DataFrame, units: pd.DataFrame, spec: ObservationSpec) -> dict[str, Any]:
    """Summarize a non-sensitive observation build for the run manifest."""
    support = units.groupby("user_id", observed=True).size() if not units.empty else pd.Series(dtype=int)
    return {
        "operator": spec.to_dict(),
        "input_schema": {
            "columns": [str(column) for column in comments.columns],
            "raw_rows": int(len(comments)),
            "raw_users": int(comments["user_id"].nunique()),
            "raw_personality_term_rate": float(comments["has_personality_term"].mean()) if len(comments) else 0.0,
        },
        "n_users": int(units["user_id"].nunique()) if not units.empty else 0,
        "n_units": int(len(units)),
        "support_summary": {
            "min_units_per_user": int(support.min()) if len(support) else 0,
            "median_units_per_user": float(support.median()) if len(support) else 0.0,
            "max_units_per_user": int(support.max()) if len(support) else 0,
            "median_tokens_per_unit": float(units["token_count"].median()) if len(units) else 0.0,
        },
    }
