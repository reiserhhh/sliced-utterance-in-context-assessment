"""Text-blind primitives for SUICA's natural joint-process stage.

This module deliberately does not define a personality score.  Its object is
an author-conditioned *natural text process*: what is selected, how it is
expressed, and how neighbouring events transition.  Selection is retained in
the object.  Only explicitly imposed collection or protocol opportunity may be
treated as a guard variable in a caller.
"""
from __future__ import annotations

import hashlib
import math
from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd


GAP_EDGES_SECONDS = np.array([0.0, 86_400.0, 7 * 86_400.0, 30 * 86_400.0, 180 * 86_400.0, np.inf])
GAP_LABELS = (
    "within_day",
    "one_to_seven_days",
    "one_to_thirty_days",
    "one_to_six_months",
    "over_six_months",
)


def stable_bucket(value: str, *, namespace: str, modulus: int = 100) -> int:
    """Return a deterministic hash bucket without exposing a source ID."""
    if modulus < 2:
        raise ValueError("modulus must be at least two")
    digest = hashlib.sha256(f"{namespace}::{value}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % modulus


def cohort_from_bucket(bucket: int) -> str:
    """Map the frozen 50/25/25 author split used by Joint-Process J1."""
    if not 0 <= bucket < 100:
        raise ValueError("bucket must lie in [0, 99]")
    if bucket < 50:
        return "discovery"
    if bucket < 75:
        return "calibration"
    return "confirmation"


def gap_bin(seconds: np.ndarray | Iterable[float]) -> np.ndarray:
    """Bin positive inter-event gaps into the frozen natural-time categories."""
    values = np.asarray(list(seconds) if not isinstance(seconds, np.ndarray) else seconds, dtype=float)
    if values.ndim != 1 or not np.isfinite(values).all() or np.any(values < 0):
        raise ValueError("gaps must be a finite non-negative one-dimensional array")
    indices = np.digitize(values, GAP_EDGES_SECONDS[1:-1], right=False)
    return np.asarray([GAP_LABELS[index] for index in indices], dtype=object)


def _shannon_entropy(values: pd.Series) -> float:
    """Return selection entropy; the selection distribution is never residualized."""
    probabilities = values.value_counts(normalize=True).to_numpy(float)
    return float(-np.sum(probabilities * np.log(probabilities))) if len(probabilities) else 0.0


def metadata_events(comments: pd.DataFrame, *, min_characters: int = 10) -> pd.DataFrame:
    """Build a raw-text-free event table from author, time, and selected forum.

    The returned table contains no comment body.  `selection` is the observed
    subreddit selected by an author, which belongs to the joint process rather
    than a nuisance adjustment.  `text_characters` is retained only for a later
    sensitivity audit and is not an opportunity covariate in the main object.
    """
    required = {"author", "body", "created_utc", "subreddit"}
    missing = sorted(required.difference(comments.columns))
    if missing:
        raise ValueError(f"missing required PANDORA columns: {missing}")
    work = comments.loc[:, ["author", "body", "created_utc", "subreddit"]].copy()
    work["body"] = work["body"].fillna("").astype(str)
    work["text_characters"] = work["body"].str.len()
    work = work.loc[work["text_characters"] >= int(min_characters)].copy()
    work["user_id"] = work["author"].astype(str)
    work["selection"] = work["subreddit"].fillna("__missing__").astype(str)
    work["created_utc"] = pd.to_numeric(work["created_utc"], errors="coerce")
    work = work.dropna(subset=["created_utc"])
    work = work.sort_values(["user_id", "created_utc"], kind="stable").reset_index(drop=True)
    work["event_index"] = work.groupby("user_id", observed=True).cumcount()
    return work.loc[:, ["user_id", "created_utc", "selection", "text_characters", "event_index"]]


def author_support_summary(events: pd.DataFrame) -> pd.DataFrame:
    """Summarize natural event and transition support without scoring text."""
    needed = {"user_id", "created_utc", "selection", "text_characters", "event_index"}
    missing = sorted(needed.difference(events.columns))
    if missing:
        raise ValueError(f"events table lacks columns: {missing}")
    rows: list[dict[str, Any]] = []
    for user_id, group in events.groupby("user_id", observed=True, sort=False):
        ordered = group.sort_values(["created_utc", "event_index"], kind="stable")
        times = ordered["created_utc"].to_numpy(float)
        gaps = np.diff(times)
        bins = gap_bin(gaps) if len(gaps) else np.array([], dtype=object)
        selection_counts = ordered["selection"].value_counts()
        row: dict[str, Any] = {
            "user_id": str(user_id),
            "event_count": int(len(ordered)),
            "transition_count": int(max(0, len(ordered) - 1)),
            "calendar_span_days": float((times[-1] - times[0]) / 86_400.0) if len(times) > 1 else 0.0,
            "selection_count": int(selection_counts.size),
            "selection_entropy": _shannon_entropy(ordered["selection"]),
            "largest_selection_share": float(selection_counts.iloc[0] / len(ordered)),
            "median_text_characters": float(ordered["text_characters"].median()),
            "mean_text_characters": float(ordered["text_characters"].mean()),
        }
        for label in GAP_LABELS:
            row[f"transitions::{label}"] = int(np.sum(bins == label))
        rows.append(row)
    return pd.DataFrame(rows)


def candidate_support_table(
    summary: pd.DataFrame,
    *,
    min_events: int,
    min_transitions: int,
    min_endpoint_authors: int,
    namespace: str,
    replicate_views: int = 1,
    replication_block_size: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Apply a frozen metadata-only support gate to author summaries.

    The gate intentionally does *not* require matched topic/community support:
    author selection remains part of the natural process object.  It returns a
    per-author table, cohort summary, and a machine-readable decision.
    """
    if min_events < 2 or min_transitions < 1 or min_endpoint_authors < 1:
        raise ValueError("support thresholds must be positive and coherent")
    if replicate_views < 1 or replication_block_size < 1:
        raise ValueError("replicate_views and replication_block_size must be positive")
    if replication_block_size == 1:
        blocks_per_view = int(min_events)
        total_event_requirement = int(min_events * replicate_views)
        total_transition_requirement = int(min_transitions * replicate_views)
    else:
        # A block of k consecutive events contributes k events and k-1
        # non-overlapping ordered transitions. This keeps technical views
        # disjoint rather than reusing a raw event on both sides.
        blocks_per_view = max(
            math.ceil(min_events / replication_block_size),
            math.ceil(min_transitions / (replication_block_size - 1)),
        )
        total_event_requirement = int(blocks_per_view * replication_block_size * replicate_views)
        total_transition_requirement = int(
            blocks_per_view * (replication_block_size - 1) * replicate_views
        )
    work = summary.copy()
    work["hash_bucket"] = work["user_id"].astype(str).map(
        lambda value: stable_bucket(value, namespace=namespace)
    )
    work["cohort"] = work["hash_bucket"].map(cohort_from_bucket)
    work["eligible"] = (
        work["event_count"].ge(total_event_requirement)
        & work["transition_count"].ge(total_transition_requirement)
    )
    rows: list[dict[str, Any]] = []
    for cohort, group in work.groupby("cohort", observed=True, sort=True):
        eligible = group.loc[group["eligible"]]
        row: dict[str, Any] = {
            "cohort": cohort,
            "n_authors": int(len(group)),
            "n_eligible_authors": int(len(eligible)),
            "eligible_fraction": float(len(eligible) / len(group)) if len(group) else 0.0,
            "median_events_eligible": float(eligible["event_count"].median()) if len(eligible) else float("nan"),
            "median_transitions_eligible": float(eligible["transition_count"].median()) if len(eligible) else float("nan"),
            "median_selection_count_eligible": float(eligible["selection_count"].median()) if len(eligible) else float("nan"),
        }
        for label in GAP_LABELS:
            column = f"transitions::{label}"
            row[f"total_{column}"] = int(eligible[column].sum()) if len(eligible) else 0
            row[f"authors_with_{column}"] = int(eligible[column].gt(0).sum()) if len(eligible) else 0
        rows.append(row)
    cohorts = pd.DataFrame(rows)
    endpoint = cohorts.loc[cohorts["cohort"].eq("confirmation")]
    endpoint_n = int(endpoint["n_eligible_authors"].iloc[0]) if len(endpoint) else 0
    decision = {
        "joint_process_supported": endpoint_n >= min_endpoint_authors,
        "decision": "PROCEED_J1" if endpoint_n >= min_endpoint_authors else "REFUSE_J1_SUPPORT",
        "reason": (
            "confirmation cohort has sufficient author-level natural-event support"
            if endpoint_n >= min_endpoint_authors
            else "confirmation cohort lacks the calibration-selected author/event support"
        ),
        "n_confirmation_eligible_authors": endpoint_n,
        "minimum_endpoint_authors": int(min_endpoint_authors),
        "minimum_events": int(min_events),
        "minimum_transitions": int(min_transitions),
        "technical_replication_views": int(replicate_views),
        "technical_replication_block_size": int(replication_block_size),
        "blocks_per_view": int(blocks_per_view),
        "minimum_total_events_for_disjoint_views": total_event_requirement,
        "minimum_total_transitions_for_disjoint_views": total_transition_requirement,
        "opportunity_separation_status": "NOT_IDENTIFIED_FROM_RAW_PANDORA_FIELDS",
        "licensed_object": "joint_selection_expression_transition_only",
    }
    return work, cohorts, decision


def rank_auc(positive: np.ndarray, negative: np.ndarray) -> float:
    """Return AUC P(positive > negative) plus half tied probability."""
    positive = np.asarray(positive, dtype=float)
    negative = np.asarray(negative, dtype=float)
    positive = positive[np.isfinite(positive)]
    negative = negative[np.isfinite(negative)]
    if not len(positive) or not len(negative):
        return float("nan")
    ordered = np.sort(negative)
    left = np.searchsorted(ordered, positive, side="left")
    right = np.searchsorted(ordered, positive, side="right")
    return float((left.sum() + 0.5 * (right - left).sum()) / (len(positive) * len(ordered)))


def same_author_auc(left: np.ndarray, right: np.ndarray) -> float:
    """Compare aligned same-author cosine links against all stranger links."""
    a = np.asarray(left, dtype=float)
    b = np.asarray(right, dtype=float)
    if a.ndim != 2 or b.ndim != 2 or a.shape != b.shape or len(a) < 4:
        raise ValueError("left/right must be aligned matrices with at least four authors")
    a = a / np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-12)
    b = b / np.maximum(np.linalg.norm(b, axis=1, keepdims=True), 1e-12)
    similarity = a @ b.T
    return rank_auc(np.diag(similarity), similarity[~np.eye(len(similarity), dtype=bool)])


def selected_candidate(calibration_rows: pd.DataFrame) -> dict[str, int] | None:
    """Choose the smallest simulation-qualified support pair deterministically."""
    required = {"min_events", "min_transitions", "qualified"}
    missing = sorted(required.difference(calibration_rows.columns))
    if missing:
        raise ValueError(f"calibration rows lack columns: {missing}")
    valid = calibration_rows.loc[calibration_rows["qualified"].astype(bool)].copy()
    if valid.empty:
        return None
    winner = valid.sort_values(["min_events", "min_transitions"], kind="stable").iloc[0]
    return {"min_events": int(winner["min_events"]), "min_transitions": int(winner["min_transitions"])}


def softmax(values: np.ndarray) -> np.ndarray:
    """Numerically stable softmax for synthetic calibration only."""
    centered = np.asarray(values, dtype=float) - np.max(values)
    exp = np.exp(centered)
    return exp / np.sum(exp)


def random_fourier_map(values: np.ndarray, weights: np.ndarray, phases: np.ndarray) -> np.ndarray:
    """Fixed random Fourier feature map for a Gaussian-kernel mean embedding."""
    array = np.asarray(values, dtype=float)
    return math.sqrt(2.0 / len(phases)) * np.cos(array @ weights + phases)


def disjoint_block_views(
    comments: pd.DataFrame,
    *,
    min_events_per_view: int,
    min_transitions_per_view: int,
    block_size: int = 3,
) -> pd.DataFrame:
    """Create two deterministic, text-disjoint technical views per author.

    Selected blocks are spread over each author's available chronological block
    sequence, then alternated into `left` and `right`. A block of `k` events
    contributes `k - 1` within-block transitions, so no raw event or transition
    is reused across the two views. The function is a *technical replicate*
    constructor, not a claim that the two views are separate human occasions.
    """
    required = {"author", "body", "created_utc", "subreddit"}
    missing = sorted(required.difference(comments.columns))
    if missing:
        raise ValueError(f"comments lack required columns: {missing}")
    if block_size < 2:
        raise ValueError("block_size must be at least two")
    blocks_per_view = max(
        math.ceil(min_events_per_view / block_size),
        math.ceil(min_transitions_per_view / (block_size - 1)),
    )
    total_blocks = 2 * blocks_per_view
    rows: list[pd.DataFrame] = []
    for author, group in comments.groupby("author", observed=True, sort=False):
        ordered = group.sort_values("created_utc", kind="stable").reset_index(drop=True)
        available_blocks = len(ordered) // block_size
        if available_blocks < total_blocks:
            continue
        # Evenly spaced block starts prevent the two technical views from being
        # arbitrary early/late windows of the same natural history.
        block_positions = np.rint(
            np.linspace(0, available_blocks - 1, num=total_blocks, dtype=float)
        ).astype(int)
        if len(np.unique(block_positions)) != total_blocks:
            raise RuntimeError("eligible event sequence did not yield distinct technical blocks")
        for chosen_index, block_position in enumerate(block_positions):
            start = int(block_position * block_size)
            block = ordered.iloc[start:start + block_size].copy()
            block["technical_view"] = "left" if chosen_index % 2 == 0 else "right"
            block["technical_block"] = chosen_index // 2
            block["within_block_index"] = np.arange(block_size, dtype=int)
            block["author"] = str(author)
            rows.append(block)
    if not rows:
        return pd.DataFrame(columns=[*comments.columns, "technical_view", "technical_block", "within_block_index"])
    return pd.concat(rows, ignore_index=True)


def selection_hash_matrix(
    selections: Iterable[str], *, dimensions: int, namespace: str
) -> np.ndarray:
    """Encode observed selection values with a fixed, non-fitting hash map."""
    if dimensions < 2:
        raise ValueError("dimensions must be at least two")
    values = [str(value) for value in selections]
    matrix = np.zeros((len(values), dimensions), dtype=float)
    indices = [stable_bucket(value, namespace=namespace, modulus=dimensions) for value in values]
    matrix[np.arange(len(values)), indices] = 1.0
    return matrix


def gap_one_hot(seconds: np.ndarray | Iterable[float]) -> np.ndarray:
    """Return a fixed five-bin encoding of non-negative inter-event gaps."""
    labels = gap_bin(seconds)
    matrix = np.zeros((len(labels), len(GAP_LABELS)), dtype=float)
    lookup = {label: index for index, label in enumerate(GAP_LABELS)}
    matrix[np.arange(len(labels)), [lookup[label] for label in labels]] = 1.0
    return matrix


def row_l2_normalize(values: np.ndarray) -> np.ndarray:
    """Normalize rows without changing all-zero rows."""
    array = np.asarray(values, dtype=float)
    return array / np.maximum(np.linalg.norm(array, axis=1, keepdims=True), 1e-12)


def alignment_permutation_test(
    left: np.ndarray,
    right: np.ndarray,
    *,
    permutations: int,
    seed: int,
) -> dict[str, float]:
    """Test aligned same-author geometry against shuffled author alignment.

    The output is a finite randomization p-value for this fixed corpus, not a
    population-level confidence interval and not a personality-effect test.
    """
    if permutations < 1:
        raise ValueError("permutations must be positive")
    observed = same_author_auc(left, right)
    rng = np.random.default_rng(seed)
    null = np.empty(permutations, dtype=float)
    for index in range(permutations):
        null[index] = same_author_auc(left, right[rng.permutation(len(right))])
    return {
        "observed_auc": float(observed),
        "null_auc_median": float(np.median(null)),
        "null_auc_q95": float(np.quantile(null, 0.95)),
        "permutation_p": float((1 + np.sum(null >= observed)) / (permutations + 1)),
    }


def pairwise_cosine_geometry_correlation(first: np.ndarray, second: np.ndarray) -> float:
    """Correlate upper-triangular cosine geometries from two representations."""
    a = row_l2_normalize(first)
    b = row_l2_normalize(second)
    if a.shape[0] != b.shape[0] or a.shape[0] < 4:
        raise ValueError("representations must have aligned rows for at least four authors")
    first_geometry = a @ a.T
    second_geometry = b @ b.T
    upper = np.triu_indices(len(a), k=1)
    x = first_geometry[upper]
    y = second_geometry[upper]
    if np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])
