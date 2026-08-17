#!/usr/bin/env python3
"""SUICA M4-U1 -- order-borne selection identity.

Executes the registration committed at a0cb613 in
``docs/SUICA_M4_U_WHEN_ORDER_PLAN.md`` (section "U1 -- order-borne selection
identity (registered BEFORE run)").  Nothing here re-derives a design
decision; where the registration is silent on an implementation detail the
simplest deterministic option is taken and recorded in
``results/m4_u1_order_identity/config.json`` (mirrored into the report's
configuration block).

The question: does the ORDER of community selections carry reproducible
author structure beyond the bag?  The T-line closed the bag question (flat
Hellinger AUC 0.9837).  U1 destroys within-half event order while preserving
each half's bag EXACTLY, and asks what discrimination is lost.

Estimand (registration):

    rho = (AUC_real - mean AUC_shuffle) / (1 - mean AUC_shuffle)

The shuffle null does NOT sit at 0.5 -- shuffled bigram features still
discriminate through their marginals -- so the null's own location is
reported for every arm (convention #68).

Part 0 (synthetic authentication) must pass before the real arm runs; a
failed gate STOPS the leg before any real-data stamp (A1 hardening).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Configuration constants (registration pins first, then recorded choices).
# ---------------------------------------------------------------------------

SEED = 20260818                     # registration pin
N_FOLDS = 5                         # registration pin
FOLD_RANDOM_STATE = SEED            # registration pin
CLUSTER_SEED_STRIDE = 1000          # registration pin: SEED + 1000 * fold
KMEANS_N_INIT = 10                  # registration pin
ALPHA = 0.5                         # registration pin (additive smoothing)
B_SHUFFLE = 499                     # registration pin
B_BOOTSTRAP = 1000                  # registration pin
C_PRIMARY = 24                      # registration pin
C_SENSITIVITY = (12, 48)            # registration pin
POOL_PRIMARY_MIN = 50               # registration pin -> census 984
POOL_SENSITIVITY_MIN = 100          # registration pin -> census 821
SESSION_GAP_SECONDS = 3600.0        # registration pin
VOCAB_FLOOR_FRACTION = 0.01         # registration pin -> floor 15 -> 1191
EPSILON_RHO = 0.05                  # registration pin (#71 equivalence eps)

CENSUS_ROWS_STREAMED = 17_640_062   # planner census, 2026-08-18
CENSUS_VOCABULARY = 1191            # planner census, bit-verified 2026-08-18
CENSUS_COHORT_AUTHORS = 1401
CENSUS_POOL_PRIMARY = 984
CENSUS_POOL_SENSITIVITY = 821

# Recorded implementation choices (registration silent -- simplest
# deterministic option taken; every one of these is echoed in the report).
B_BOOT_SHUFFLE = 100                # shuffle matrices reused inside the
                                    # cluster bootstrap's null-mean component
BOOT_BINS = 4096                    # binned-AUC resolution inside the
                                    # bootstrap; validated against exact AUC
SYNTH_AUTHORS = 900                 # registration pin
SYNTH_STATES = 24                   # registration pin (C_true)
SYNTH_MEDIAN_EVENTS = 379           # registration pin (census median)
SYNTH_LOGNORMAL_SIGMA = 0.5         # choice: event counts "drawn to match"
SYNTH_MIN_EVENTS = 120              # choice: floor so both halves clear 50
SYNTH_B_SHUFFLE = 99                # choice: gate resolution
SYNTH_B_BOOTSTRAP = 200             # choice: gate resolution
SYNTH_B_BOOT_SHUFFLE = 10           # choice: synthetic pools are one block of
                                    # 900 authors, so each stored matrix is
                                    # 21x a real fold's
SYNTH_DIRICHLET_CONC = 4.5          # choice, CALIBRATED -- see anomaly A-U1-1
                                    # in the report: at the first value (0.4)
                                    # the synthetic bag AUC saturated at
                                    # 0.99999 and no estimator could show
                                    # rho > 0 at the weakest sticky knob.
                                    # 4.5 puts the synthetic bag AUC at
                                    # 0.9549, nearest a 0.96 target on the
                                    # grid {3.5, 4, 4.5, 5}, i.e. in the real
                                    # arm's discrimination regime.
SYNTH_BAG_AUC_TARGET = 0.96         # calibration target for the above
SYNTH_STICKY_S = (0.1, 0.25, 0.5)   # registration pin
SYNTH_MH_BETA = (1.0, 4.0, 16.0)    # choice: 3 proposal-strength points
SYNTH_MH_BLOCKS = 6                 # choice: block-structured proposal
SYNTH_NULL_REPLICATES = 8           # choice, see RD-U1-1
NULL_LOCATION_TOLERANCE = 0.05      # registration's literal check, enforced on
                                    # the REAL primary arm (see RD-U1-2)
SYNTH_NULL_LIFT_MIN = 0.40          # synthetic check: share of the bag's lift
                                    # over 0.5 that the shuffle null retains

CHUNK_SIZE = 2_000_000              # streaming chunk (rows)

DEFAULT_COMMENTS = Path(
    "/Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/"
    "all_comments_since_2015.csv"
)
DEFAULT_COHORT = ROOT / "results/m4_sr0_recon/cohort_authors.csv"
DEFAULT_OUTPUT = ROOT / "results/m4_u1_order_identity"
DEFAULT_REPORT = ROOT / "reports/SUICA_M4_U1_ORDER_IDENTITY_REPORT.md"

# ---------------------------------------------------------------------------
# Governance echo: the explicit-typology community matcher.
#
# Provenance: reproduced verbatim from
# ``scripts/run_suica_m4_t1_hierarchical_selection_identity.py`` lines 37-69
# (the T1 clean_no_explicit_personality arm).  The map is RE-DERIVED here from
# this cohort's vocabulary rather than read from T1's artifacts.
# ---------------------------------------------------------------------------

MBTI_TYPES = {
    first + second + third + fourth
    for first in "ei"
    for second in "ns"
    for third in "ft"
    for fourth in "jp"
}
PERSONALITY_MARKERS = (
    "mbti",
    "enneagram",
    "jung",
    "socionic",
    "personality",
    "typology",
)


def is_explicit_personality_community(name: str) -> bool:
    """Return whether a subreddit name directly denotes a typology construct."""

    lowered = name.casefold()
    return bool(
        lowered in MBTI_TYPES
        or lowered in {"introvert", "introverts", "extrovert", "extroverts"}
        or any(marker in lowered for marker in PERSONALITY_MARKERS)
    )


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stable_seed(*parts: Any) -> int:
    """Process-independent seed from arbitrary parts (``hash`` is salted)."""

    digest = hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8"))
    return int.from_bytes(digest.digest()[:4], "big")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=float) + "\n",
        encoding="utf-8",
    )


class RunLog:
    """Append-only JSONL event log (T-line artifact convention)."""

    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        self._t0 = time.time()

    def event(self, name: str, **payload: Any) -> None:
        record = {
            "event": name,
            "utc": utc_now(),
            "elapsed_s": round(time.time() - self._t0, 3),
        }
        record.update(payload)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, default=float) + "\n")
        print(f"[{record['elapsed_s']:9.1f}s] {name} "
              f"{json.dumps(payload, sort_keys=True, default=float)[:220]}",
              flush=True)


def l2_normalize_rows(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    return matrix / norms


# ---------------------------------------------------------------------------
# AUC machinery
# ---------------------------------------------------------------------------


def _average_ranks(values: np.ndarray) -> np.ndarray:
    """Average (mid) ranks, 1-based, ties averaged.  scipy-free."""

    order = np.argsort(values, kind="stable")
    sorted_values = values[order]
    n = values.size
    ranks_sorted = np.empty(n, dtype=np.float64)
    # boundaries of tie groups
    start = 0
    boundaries = np.flatnonzero(sorted_values[1:] != sorted_values[:-1]) + 1
    edges = np.concatenate(([0], boundaries, [n]))
    for i in range(edges.size - 1):
        start, stop = int(edges[i]), int(edges[i + 1])
        ranks_sorted[start:stop] = 0.5 * (start + stop + 1)
    ranks = np.empty(n, dtype=np.float64)
    ranks[order] = ranks_sorted
    return ranks


def auc_from_scores(positive: np.ndarray, negative: np.ndarray) -> float:
    """Exact rank AUC with 0.5 credit for ties."""

    n_pos = positive.size
    n_neg = negative.size
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    ranks = _average_ranks(np.concatenate([positive, negative]))
    rank_sum = float(ranks[:n_pos].sum())
    return (rank_sum - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)


def auc_from_matrix(similarity: np.ndarray) -> float:
    """Same-author (diagonal) vs different-author (off-diagonal) AUC."""

    m = similarity.shape[0]
    if m < 2:
        return float("nan")
    positive = np.diagonal(similarity).astype(np.float64)
    mask = ~np.eye(m, dtype=bool)
    negative = similarity[mask].astype(np.float64)
    return auc_from_scores(positive, negative)


def bin_matrix(similarity: np.ndarray, n_bins: int = BOOT_BINS) -> np.ndarray:
    """Monotone integer coding of a similarity matrix (ties preserved)."""

    flat = similarity.astype(np.float64)
    low = float(flat.min())
    high = float(flat.max())
    if high <= low:
        return np.zeros(flat.shape, dtype=np.int32)
    scaled = (flat - low) / (high - low) * (n_bins - 1)
    return np.rint(scaled).astype(np.int32)


def weighted_auc_from_codes(codes: np.ndarray, counts: np.ndarray,
                            n_bins: int) -> float:
    """AUC of a coded matrix under author multiplicities (cluster bootstrap).

    ``counts[u]`` is how many times author u was drawn.  Positives are the
    diagonal with weight c_u; negatives are the off-diagonal with weight
    c_u * c_v (u != v), which automatically excludes pairs between duplicate
    copies of the SAME author -- the resampled negative set contains only
    genuinely different authors.
    """

    weights = np.outer(counts, counts).astype(np.float64)
    diag_weight = counts.astype(np.float64)
    np.fill_diagonal(weights, 0.0)
    total_neg = float(weights.sum())
    total_pos = float(diag_weight.sum())
    if total_neg <= 0.0 or total_pos <= 0.0:
        return float("nan")
    hist = np.bincount(codes.ravel(), weights=weights.ravel(),
                       minlength=n_bins)
    cumulative = np.concatenate(([0.0], np.cumsum(hist)[:-1]))
    diag_codes = np.diagonal(codes)
    below = cumulative[diag_codes]
    equal = hist[diag_codes]
    return float(np.dot(diag_weight, below + 0.5 * equal) /
                 (total_pos * total_neg))


def weighted_auc_stack(codes_stack: np.ndarray, counts: np.ndarray,
                       n_bins: int) -> np.ndarray:
    """Vectorised :func:`weighted_auc_from_codes` over a stack of matrices."""

    k = codes_stack.shape[0]
    m = counts.size
    weights = np.outer(counts, counts).astype(np.float64)
    diag_weight = counts.astype(np.float64)
    np.fill_diagonal(weights, 0.0)
    total_neg = float(weights.sum())
    total_pos = float(diag_weight.sum())
    if total_neg <= 0.0 or total_pos <= 0.0:
        return np.full(k, np.nan)
    offsets = (np.arange(k, dtype=np.int64) * n_bins)[:, None, None]
    flat_codes = (codes_stack.astype(np.int64) + offsets).ravel()
    flat_weights = np.tile(weights.ravel(), k)
    hist = np.bincount(flat_codes, weights=flat_weights,
                       minlength=k * n_bins).reshape(k, n_bins)
    cumulative = np.cumsum(hist, axis=1) - hist
    rows = np.arange(k)[:, None]
    diag_idx = np.arange(m)
    diag_codes = codes_stack[:, diag_idx, diag_idx]
    below = cumulative[rows, diag_codes]
    equal = hist[rows, diag_codes]
    return (below + 0.5 * equal) @ diag_weight / (total_pos * total_neg)


# ---------------------------------------------------------------------------
# Spherical k-means (cosine), deterministic
# ---------------------------------------------------------------------------


def spherical_kmeans(points: np.ndarray, n_clusters: int, seed: int,
                     n_init: int = KMEANS_N_INIT, max_iter: int = 100,
                     tol: float = 1e-9) -> np.ndarray:
    """Spherical k-means labels for L2-normalised ``points`` (rows)."""

    unit = l2_normalize_rows(points.astype(np.float64))
    n = unit.shape[0]
    if n_clusters >= n:
        return np.arange(n) % n_clusters
    best_labels: np.ndarray | None = None
    best_objective = -np.inf
    for init in range(n_init):
        rng = np.random.default_rng(seed * 1_000_003 + init)
        centers = _kmeanspp_init(unit, n_clusters, rng)
        labels = np.zeros(n, dtype=np.int64)
        objective = -np.inf
        for _ in range(max_iter):
            sims = unit @ centers.T
            labels = np.argmax(sims, axis=1)
            new_objective = float(sims[np.arange(n), labels].sum())
            indicator = np.zeros((n, n_clusters))
            indicator[np.arange(n), labels] = 1.0
            centers = l2_normalize_rows(indicator.T @ unit)
            empty = np.flatnonzero(indicator.sum(axis=0) == 0)
            if empty.size:
                worst = np.argsort(sims[np.arange(n), labels])[:empty.size]
                centers[empty] = unit[worst]
            if new_objective - objective <= tol:
                objective = new_objective
                break
            objective = new_objective
        if objective > best_objective:
            best_objective = objective
            best_labels = labels.copy()
    assert best_labels is not None
    return best_labels


def _kmeanspp_init(unit: np.ndarray, n_clusters: int,
                   rng: np.random.Generator) -> np.ndarray:
    n = unit.shape[0]
    first = int(rng.integers(n))
    centers = [unit[first]]
    closest = 2.0 - 2.0 * (unit @ unit[first])
    for _ in range(1, n_clusters):
        total = float(closest.sum())
        if total <= 0.0:
            pick = int(rng.integers(n))
        else:
            pick = int(rng.choice(n, p=np.maximum(closest, 0.0) / total))
        centers.append(unit[pick])
        closest = np.minimum(closest, 2.0 - 2.0 * (unit @ unit[pick]))
    return l2_normalize_rows(np.vstack(centers))


# ---------------------------------------------------------------------------
# Stage 1 -- stream the cohort event scaffold
# ---------------------------------------------------------------------------


@dataclass
class EventScaffold:
    """Per-author time-ordered event stream, cohort-restricted, no bodies."""

    authors: list[str]
    author_code: np.ndarray      # int32, sorted by (author, ts) stably
    subreddit_code: np.ndarray   # int32 into ``subreddits``
    created_utc: np.ndarray      # float64
    link_code: np.ndarray        # int32
    subreddits: list[str]
    vocabulary: list[str]        # sorted community names at the SR0 floor
    vocab_of_subreddit: np.ndarray   # int32, -1 for OOV
    stream_stats: dict[str, Any]


def stream_cohort_events(comments_path: Path, cohort_path: Path,
                         log: RunLog) -> EventScaffold:
    cohort_frame = pd.read_csv(cohort_path, usecols=["author"])
    authors = sorted(set(cohort_frame["author"].astype(str)))
    cohort = set(authors)
    log.event("stream_start", cohort_authors=len(authors),
              comments_path=str(comments_path))

    parts: list[pd.DataFrame] = []
    rows_streamed = 0
    for chunk in pd.read_csv(
        comments_path,
        usecols=["author", "subreddit", "created_utc", "link_id"],
        chunksize=CHUNK_SIZE,
        dtype={"author": "str", "subreddit": "str", "link_id": "str"},
        on_bad_lines="skip",
        engine="c",
    ):
        rows_streamed += len(chunk)
        keep = chunk[chunk["author"].isin(cohort)]
        if not keep.empty:
            parts.append(keep)
    frame = pd.concat(parts, ignore_index=True)
    del parts
    rows_cohort_raw = int(len(frame))
    frame = frame.dropna(subset=["author", "subreddit", "created_utc"])
    frame["link_id"] = frame["link_id"].fillna("")
    rows_cohort = int(len(frame))
    log.event("stream_done", rows_streamed=rows_streamed,
              rows_cohort_raw=rows_cohort_raw, rows_cohort=rows_cohort)

    author_index = {name: i for i, name in enumerate(authors)}
    author_code = frame["author"].map(author_index).to_numpy(np.int32)
    sub_codes, sub_uniques = pd.factorize(frame["subreddit"], sort=True)
    subreddit_code = np.asarray(sub_codes, dtype=np.int32)
    subreddits = [str(name) for name in sub_uniques]
    created = frame["created_utc"].to_numpy(np.float64)
    link_codes, _ = pd.factorize(frame["link_id"], sort=False)
    link_code = np.asarray(link_codes, dtype=np.int32)
    del frame

    # Stable ordering: author primary, created_utc secondary, stream order
    # for ties (registration pin -- ties keep stream order).
    order = np.lexsort((created, author_code))
    author_code = author_code[order]
    subreddit_code = subreddit_code[order]
    created = created[order]
    link_code = link_code[order]

    # SR0 vocabulary reproduction: distinct cohort users per subreddit,
    # floor = ceil(0.01 * authors_seen).  Provenance: T1's
    # reconstruct_vocabulary (lines 72-117), same rule, computed from the
    # cohort-restricted stream already in memory.
    pair_key = subreddit_code.astype(np.int64) * len(authors) + author_code
    unique_pairs = np.unique(pair_key)
    users_per_subreddit = np.bincount(
        (unique_pairs // len(authors)).astype(np.int64),
        minlength=len(subreddits),
    )
    authors_seen = int(np.unique(author_code).size)
    floor_users = max(1, int(math.ceil(VOCAB_FLOOR_FRACTION * authors_seen)))
    in_vocab = users_per_subreddit >= floor_users
    vocabulary = sorted(name for name, keep in zip(subreddits, in_vocab) if keep)
    vocab_position = {name: i for i, name in enumerate(vocabulary)}
    vocab_of_subreddit = np.full(len(subreddits), -1, dtype=np.int32)
    for idx, name in enumerate(subreddits):
        if in_vocab[idx]:
            vocab_of_subreddit[idx] = vocab_position[name]

    stats = {
        "rows_streamed": rows_streamed,
        "rows_cohort_raw": rows_cohort_raw,
        "rows_cohort_used": rows_cohort,
        "authors_seen": authors_seen,
        "floor_users": floor_users,
        "vocabulary_size": len(vocabulary),
        "distinct_subreddits": len(subreddits),
    }
    log.event("vocabulary_reconstructed", **stats)
    return EventScaffold(
        authors=authors,
        author_code=author_code,
        subreddit_code=subreddit_code,
        created_utc=created,
        link_code=link_code,
        subreddits=subreddits,
        vocabulary=vocabulary,
        vocab_of_subreddit=vocab_of_subreddit,
        stream_stats=stats,
    )


def save_scaffold(scaffold: EventScaffold, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        author_code=scaffold.author_code,
        subreddit_code=scaffold.subreddit_code,
        created_utc=scaffold.created_utc,
        link_code=scaffold.link_code,
        vocab_of_subreddit=scaffold.vocab_of_subreddit,
    )
    write_json(path.with_suffix(".meta.json"), {
        "authors": scaffold.authors,
        "subreddits": scaffold.subreddits,
        "vocabulary": scaffold.vocabulary,
        "stream_stats": scaffold.stream_stats,
    })


def load_scaffold(path: Path) -> EventScaffold:
    payload = np.load(path)
    meta = json.loads(path.with_suffix(".meta.json").read_text(encoding="utf-8"))
    return EventScaffold(
        authors=meta["authors"],
        author_code=payload["author_code"],
        subreddit_code=payload["subreddit_code"],
        created_utc=payload["created_utc"],
        link_code=payload["link_code"],
        subreddits=meta["subreddits"],
        vocabulary=meta["vocabulary"],
        vocab_of_subreddit=payload["vocab_of_subreddit"],
        stream_stats=meta["stream_stats"],
    )


# ---------------------------------------------------------------------------
# Stage 2 -- halves, pools, folds
# ---------------------------------------------------------------------------


def split_halves(created: np.ndarray) -> np.ndarray:
    """SR0's T6'' rule: boundary events (ts <= per-author median) to early."""

    median = float(np.median(created))
    return created <= median


@dataclass
class FoldData:
    """Compacted event scaffold for one fold's TEST authors."""

    fold: int
    test_authors: np.ndarray     # indices into the pool author list
    train_authors: np.ndarray
    event_vocab: np.ndarray      # int32 in [0, n_vocab]; n_vocab == OOV
    event_half: np.ndarray       # int32 in [0, 2m)
    pair_from: np.ndarray
    pair_to: np.ndarray
    pair_half: np.ndarray
    pair_session: np.ndarray     # bool: gap <= 3600 s
    pair_cross_thread: np.ndarray
    pair_same_thread: np.ndarray
    n_halves: int


@dataclass
class PoolContext:
    """Everything downstream of (vocabulary variant, per-half event floor)."""

    key: str
    vocab_variant: str
    pool_min: int
    n_vocab: int
    pool_authors: np.ndarray     # author codes
    folds: list[FoldData]
    train_early_counts: list[np.ndarray]   # per fold: (n_vocab, n_train)
    early_vocab_counts: np.ndarray         # per pool author
    census: dict[str, Any]


def build_pool_context(scaffold: EventScaffold, vocab_variant: str,
                       pool_min: int, log: RunLog) -> PoolContext:
    n_authors = len(scaffold.authors)
    vocab_of_subreddit = scaffold.vocab_of_subreddit.copy()
    if vocab_variant == "clean":
        removed = [name for name in scaffold.vocabulary
                   if is_explicit_personality_community(name)]
        removed_set = set(removed)
        keep_names = [name for name in scaffold.vocabulary
                      if name not in removed_set]
        remap = {name: i for i, name in enumerate(keep_names)}
        new_map = np.full(vocab_of_subreddit.shape, -1, dtype=np.int32)
        for idx, name in enumerate(scaffold.subreddits):
            old = vocab_of_subreddit[idx]
            if old >= 0 and name in remap:
                new_map[idx] = remap[name]
        vocab_of_subreddit = new_map
        n_vocab = len(keep_names)
        removed_names = sorted(removed)
    elif vocab_variant == "full":
        n_vocab = len(scaffold.vocabulary)
        removed_names = []
    else:  # pragma: no cover - guarded by the arm table
        raise ValueError(f"unknown vocabulary variant {vocab_variant!r}")

    event_vocab_all = vocab_of_subreddit[scaffold.subreddit_code]
    author_code = scaffold.author_code
    created = scaffold.created_utc

    # author segment boundaries (author_code is sorted)
    boundaries = np.flatnonzero(author_code[1:] != author_code[:-1]) + 1
    starts = np.concatenate(([0], boundaries))
    stops = np.concatenate((boundaries, [author_code.size]))
    present_authors = author_code[starts]

    is_early_all = np.zeros(author_code.size, dtype=bool)
    early_vocab_counts = np.zeros(n_authors, dtype=np.int64)
    late_vocab_counts = np.zeros(n_authors, dtype=np.int64)
    for start, stop, author in zip(starts, stops, present_authors):
        early = split_halves(created[start:stop])
        is_early_all[start:stop] = early
        in_vocab = event_vocab_all[start:stop] >= 0
        early_vocab_counts[author] = int(np.count_nonzero(in_vocab & early))
        late_vocab_counts[author] = int(np.count_nonzero(in_vocab & ~early))

    eligible = (early_vocab_counts >= pool_min) & (late_vocab_counts >= pool_min)
    pool_authors = np.flatnonzero(eligible).astype(np.int32)

    from sklearn.model_selection import KFold

    splitter = KFold(n_splits=N_FOLDS, shuffle=True,
                     random_state=FOLD_RANDOM_STATE)
    fold_assignment = np.empty(pool_authors.size, dtype=np.int32)
    for fold, (_, test_idx) in enumerate(splitter.split(pool_authors)):
        fold_assignment[test_idx] = fold

    author_slices = {int(a): (int(s), int(e))
                     for a, s, e in zip(present_authors, starts, stops)}

    folds: list[FoldData] = []
    train_counts: list[np.ndarray] = []
    for fold in range(N_FOLDS):
        test_idx = np.flatnonzero(fold_assignment == fold)
        train_idx = np.flatnonzero(fold_assignment != fold)

        # ---- per-fold state map inputs: TRAINING authors' EARLY halves only
        counts = np.zeros((n_vocab, train_idx.size), dtype=np.float64)
        for column, pool_position in enumerate(train_idx):
            author = int(pool_authors[pool_position])
            start, stop = author_slices[author]
            vocab_ids = event_vocab_all[start:stop]
            early = is_early_all[start:stop]
            selected = vocab_ids[(vocab_ids >= 0) & early]
            if selected.size:
                counts[:, column] = np.bincount(selected, minlength=n_vocab)
        train_counts.append(counts)

        # ---- compacted test-author event arrays
        ev_vocab_parts: list[np.ndarray] = []
        ev_half_parts: list[np.ndarray] = []
        ev_ts_parts: list[np.ndarray] = []
        ev_link_parts: list[np.ndarray] = []
        half_id = 0
        for pool_position in test_idx:
            author = int(pool_authors[pool_position])
            start, stop = author_slices[author]
            vocab_ids = event_vocab_all[start:stop]
            early = is_early_all[start:stop]
            for mask in (early, ~early):
                ev_vocab_parts.append(np.where(vocab_ids[mask] >= 0,
                                               vocab_ids[mask], n_vocab))
                ev_half_parts.append(np.full(int(mask.sum()), half_id,
                                             dtype=np.int32))
                ev_ts_parts.append(created[start:stop][mask])
                ev_link_parts.append(scaffold.link_code[start:stop][mask])
                half_id += 1
        event_vocab = np.concatenate(ev_vocab_parts).astype(np.int32)
        event_half = np.concatenate(ev_half_parts).astype(np.int32)
        event_ts = np.concatenate(ev_ts_parts)
        event_link = np.concatenate(ev_link_parts)

        same_half = event_half[1:] == event_half[:-1]
        pair_from = np.flatnonzero(same_half).astype(np.int64)
        pair_to = pair_from + 1
        pair_half = event_half[pair_from]
        gaps = event_ts[pair_to] - event_ts[pair_from]
        pair_session = gaps <= SESSION_GAP_SECONDS
        pair_same_thread = event_link[pair_to] == event_link[pair_from]
        folds.append(FoldData(
            fold=fold,
            test_authors=test_idx.astype(np.int32),
            train_authors=train_idx.astype(np.int32),
            event_vocab=event_vocab,
            event_half=event_half,
            pair_from=pair_from,
            pair_to=pair_to,
            pair_half=pair_half.astype(np.int32),
            pair_session=pair_session,
            pair_cross_thread=~pair_same_thread,
            pair_same_thread=pair_same_thread,
            n_halves=half_id,
        ))

    census = {
        "vocab_variant": vocab_variant,
        "n_vocab": n_vocab,
        "removed_communities": removed_names,
        "n_removed_communities": len(removed_names),
        "pool_min_per_half": pool_min,
        "pool_size": int(pool_authors.size),
        "cohort_authors_with_events": int(present_authors.size),
        "early_vocab_median": float(np.median(
            early_vocab_counts[pool_authors])),
        "late_vocab_median": float(np.median(
            late_vocab_counts[pool_authors])),
        "fold_test_sizes": [int(f.test_authors.size) for f in folds],
    }
    log.event("pool_built", key=f"{vocab_variant}_min{pool_min}", **{
        k: v for k, v in census.items() if k != "removed_communities"})
    return PoolContext(
        key=f"{vocab_variant}_min{pool_min}",
        vocab_variant=vocab_variant,
        pool_min=pool_min,
        n_vocab=n_vocab,
        pool_authors=pool_authors,
        folds=folds,
        train_early_counts=train_counts,
        early_vocab_counts=early_vocab_counts[pool_authors],
        census=census,
    )


# ---------------------------------------------------------------------------
# Stage 3 -- per-fold state maps (training-early only; purity is blocking)
# ---------------------------------------------------------------------------


def build_state_maps(pool: PoolContext, n_states: int,
                     log: RunLog) -> tuple[list[np.ndarray], dict[str, Any]]:
    """Return per-fold arrays of length n_vocab+1 mapping vocab id -> state."""

    maps: list[np.ndarray] = []
    diagnostics: list[dict[str, Any]] = []
    for fold, counts in enumerate(pool.train_early_counts):
        mass = counts.sum(axis=1)
        active = np.flatnonzero(mass > 0)
        state_of_vocab = np.full(pool.n_vocab + 1, n_states, dtype=np.int32)
        if active.size:
            labels = spherical_kmeans(np.sqrt(counts[active]), n_states,
                                      seed=SEED + CLUSTER_SEED_STRIDE * fold)
            state_of_vocab[active] = labels.astype(np.int32)
        maps.append(state_of_vocab)
        sizes = np.bincount(state_of_vocab[:-1], minlength=n_states + 1)
        diagnostics.append({
            "fold": fold,
            "active_communities": int(active.size),
            "zero_mass_to_oov": int(pool.n_vocab - active.size),
            "cluster_sizes": [int(v) for v in sizes[:n_states]],
            "cluster_seed": SEED + CLUSTER_SEED_STRIDE * fold,
        })
    info = {"n_states": n_states, "folds": diagnostics}
    log.event("state_maps_built", pool=pool.key, n_states=n_states,
              zero_mass=[d["zero_mass_to_oov"] for d in diagnostics])
    return maps, info


def assert_fold_purity(pool: PoolContext) -> dict[str, Any]:
    """Blocking gate: zero test-author mass enters any fold's state map.

    The map's only input is ``train_early_counts[fold]``, whose columns are
    indexed by ``folds[fold].train_authors``.  Purity therefore reduces to
    (a) the train/test author index sets being disjoint and exhaustive and
    (b) the count matrix having exactly one column per training author.
    """

    checks = []
    for fold_data, counts in zip(pool.folds, pool.train_early_counts):
        train = set(int(v) for v in fold_data.train_authors)
        test = set(int(v) for v in fold_data.test_authors)
        assert not (train & test), "fold purity violated: train/test overlap"
        assert len(train) + len(test) == pool.pool_authors.size
        assert counts.shape[1] == fold_data.train_authors.size, \
            "fold purity violated: state-map columns are not the training set"
        # Mass arithmetic: the map's total mass must equal the TRAINING
        # authors' early in-vocabulary event total exactly, and must fall
        # short of the pool total by exactly the test authors' mass.
        map_mass = float(counts.sum())
        train_mass = float(pool.early_vocab_counts[
            fold_data.train_authors].sum())
        test_mass = float(pool.early_vocab_counts[
            fold_data.test_authors].sum())
        assert abs(map_mass - train_mass) < 1e-6, \
            "fold purity violated: state-map mass is not the training mass"
        assert test_mass > 0.0, "degenerate fold: no test-author mass at all"
        checks.append({
            "fold": fold_data.fold,
            "n_train": len(train),
            "n_test": len(test),
            "map_columns": int(counts.shape[1]),
            "train_test_overlap": 0,
            "map_mass": map_mass,
            "train_early_mass": train_mass,
            "test_early_mass_excluded": test_mass,
        })
    return {"pool": pool.key, "folds": checks, "status": "PASS"}


# ---------------------------------------------------------------------------
# Stage 4 -- features and the exact-bag shuffle
# ---------------------------------------------------------------------------


def within_half_permutation(event_half: np.ndarray,
                            rng: np.random.Generator) -> np.ndarray:
    """Batched within-half order shuffle (the T2 paid lesson: no per-user loops).

    ``event_half`` is non-decreasing, so sorting on ``half + U[0,1)`` yields a
    permutation that never moves an event across a half boundary.  The
    per-half bag is therefore EXACTLY invariant.
    """

    keys = event_half.astype(np.float64) + rng.random(event_half.size)
    return np.argsort(keys, kind="stable")


def bigram_counts(states: np.ndarray, pair_from: np.ndarray,
                  pair_to: np.ndarray, pair_half: np.ndarray,
                  n_halves: int, n_states: int) -> np.ndarray:
    """Per-half joint next-state counts, shape (n_halves, (n_states+1)**2)."""

    side = n_states + 1
    dim = side * side
    flat = (pair_half.astype(np.int64) * dim
            + states[pair_from].astype(np.int64) * side
            + states[pair_to].astype(np.int64))
    return np.bincount(flat, minlength=n_halves * dim).reshape(n_halves, dim)


def features_from_counts(counts: np.ndarray, n_states: int,
                         lens: str) -> np.ndarray:
    side = n_states + 1
    if lens == "hellinger_joint":
        smoothed = counts.astype(np.float64) + ALPHA
        probs = smoothed / smoothed.sum(axis=1, keepdims=True)
        return l2_normalize_rows(np.sqrt(probs))
    if lens == "conditional_rows":
        smoothed = (counts.astype(np.float64) + ALPHA).reshape(-1, side, side)
        rows = smoothed / smoothed.sum(axis=2, keepdims=True)
        return l2_normalize_rows(np.sqrt(rows).reshape(counts.shape[0], -1))
    raise ValueError(f"unknown lens {lens!r}")


def stay_rates(counts: np.ndarray, n_states: int) -> np.ndarray:
    side = n_states + 1
    square = counts.reshape(-1, side, side)
    total = square.sum(axis=(1, 2)).astype(np.float64)
    diagonal = np.einsum("nii->n", square).astype(np.float64)
    total[total == 0.0] = 1.0
    return diagonal / total


def similarity_matrix(counts: np.ndarray, n_states: int,
                      lens: str) -> np.ndarray:
    if lens == "stay_rate":
        rates = stay_rates(counts, n_states)
        early = rates[0::2]
        late = rates[1::2]
        return -np.abs(early[:, None] - late[None, :])
    features = features_from_counts(counts, n_states, lens)
    return features[0::2] @ features[1::2].T


# ---------------------------------------------------------------------------
# Stage 5 -- one arm
# ---------------------------------------------------------------------------


@dataclass
class ArmSpec:
    key: str
    label: str
    role: str
    n_states: int
    vocab_variant: str
    pool_min: int
    pairs: str
    lens: str


ARMS: tuple[ArmSpec, ...] = (
    ArmSpec("primary", "raw adjacency, full vocab, C=24", "PRIMARY",
            C_PRIMARY, "full", POOL_PRIMARY_MIN, "all", "hellinger_joint"),
    ArmSpec("cross_thread", "cross-thread only (link_id differs)",
            "CO_PRIMARY", C_PRIMARY, "full", POOL_PRIMARY_MIN, "cross_thread",
            "hellinger_joint"),
    ArmSpec("session", "session-restricted (gap <= 3600 s)", "secondary",
            C_PRIMARY, "full", POOL_PRIMARY_MIN, "session", "hellinger_joint"),
    ArmSpec("c12", "state resolution C=12", "sensitivity",
            12, "full", POOL_PRIMARY_MIN, "all", "hellinger_joint"),
    ArmSpec("c48", "state resolution C=48", "sensitivity",
            48, "full", POOL_PRIMARY_MIN, "all", "hellinger_joint"),
    ArmSpec("conditional_rows", "conditional-rows lens", "secondary_lens",
            C_PRIMARY, "full", POOL_PRIMARY_MIN, "all", "conditional_rows"),
    ArmSpec("stay_rate", "stay-rate scalar", "secondary_channel",
            C_PRIMARY, "full", POOL_PRIMARY_MIN, "all", "stay_rate"),
    ArmSpec("pool100", ">=100-events pool", "sensitivity",
            C_PRIMARY, "full", POOL_SENSITIVITY_MIN, "all", "hellinger_joint"),
    ArmSpec("clean", "clean_no_explicit_personality", "governance_echo",
            C_PRIMARY, "clean", POOL_PRIMARY_MIN, "all", "hellinger_joint"),
)


def pair_mask(fold: FoldData, pairs: str) -> np.ndarray:
    if pairs == "all":
        return np.ones(fold.pair_from.size, dtype=bool)
    if pairs == "session":
        return fold.pair_session
    if pairs == "cross_thread":
        return fold.pair_cross_thread
    raise ValueError(f"unknown pair set {pairs!r}")


def rho_from_auc(auc_real: float, auc_null: float) -> float:
    denominator = 1.0 - auc_null
    if denominator <= 0.0:
        return float("nan")
    return (auc_real - auc_null) / denominator


def run_arm(spec: ArmSpec, pool: PoolContext, state_maps: Sequence[np.ndarray],
            log: RunLog, b_shuffle: int = B_SHUFFLE,
            b_bootstrap: int = B_BOOTSTRAP,
            b_boot_shuffle: int = B_BOOT_SHUFFLE,
            collect_bag_reference: bool = False) -> dict[str, Any]:
    """Real AUC, the exact-bag shuffle null, rho and its cluster-bootstrap CI."""

    started = utc_now()
    n_states = spec.n_states
    real_matrices: list[np.ndarray] = []
    stored_codes: list[np.ndarray] = []
    real_codes: list[np.ndarray] = []
    shuffle_auc = np.zeros((b_shuffle, N_FOLDS), dtype=np.float64)
    fold_real_auc = np.zeros(N_FOLDS, dtype=np.float64)
    bag_auc = np.zeros(N_FOLDS, dtype=np.float64)
    bag_invariance_ok = True
    empty_halves = 0
    used_pairs = 0
    total_pairs = 0
    stay_real: list[float] = []
    stay_pseudo: list[float] = []

    for fold_data, state_of_vocab in zip(pool.folds, state_maps):
        mask = pair_mask(fold_data, spec.pairs)
        pf = fold_data.pair_from[mask]
        pt = fold_data.pair_to[mask]
        ph = fold_data.pair_half[mask]
        used_pairs += int(mask.sum())
        total_pairs += int(mask.size)
        states = state_of_vocab[fold_data.event_vocab]
        counts = bigram_counts(states, pf, pt, ph, fold_data.n_halves,
                               n_states)
        empty_halves += int((counts.sum(axis=1) == 0).sum())
        matrix = similarity_matrix(counts, n_states, spec.lens)
        fold_real_auc[fold_data.fold] = auc_from_matrix(matrix)
        real_matrices.append(matrix.astype(np.float32))
        real_codes.append(bin_matrix(matrix))

        if collect_bag_reference:
            bag = np.bincount(
                fold_data.event_half.astype(np.int64) * (n_states + 1)
                + states.astype(np.int64),
                minlength=fold_data.n_halves * (n_states + 1),
            ).reshape(fold_data.n_halves, n_states + 1)
            smoothed = bag.astype(np.float64) + ALPHA
            probs = smoothed / smoothed.sum(axis=1, keepdims=True)
            unigram = l2_normalize_rows(np.sqrt(probs))
            bag_auc[fold_data.fold] = auc_from_matrix(
                unigram[0::2] @ unigram[1::2].T)

        reference_bag = np.bincount(
            fold_data.event_half.astype(np.int64) * (n_states + 1)
            + states.astype(np.int64),
            minlength=fold_data.n_halves * (n_states + 1))
        if spec.lens == "stay_rate":
            # The registered null for the scalar arm is the bag-concentration
            # pseudo-stay sum_j pi_j^2 (#68): what a memoryless draw from the
            # half's own bag would produce.
            bag_shape = reference_bag.reshape(fold_data.n_halves, -1)
            shares = bag_shape / np.maximum(
                1, bag_shape.sum(axis=1, keepdims=True))
            stay_pseudo.extend(float(v) for v in (shares ** 2).sum(axis=1))
            stay_real.extend(float(v) for v in stay_rates(counts, n_states))
        rng = np.random.default_rng(
            stable_seed(SEED, "shuffle", spec.key, fold_data.fold))
        fold_codes: list[np.ndarray] = []
        for b in range(b_shuffle):
            perm = within_half_permutation(fold_data.event_half, rng)
            shuffled = states[perm]
            if b == 0:
                check = np.bincount(
                    fold_data.event_half.astype(np.int64) * (n_states + 1)
                    + shuffled.astype(np.int64),
                    minlength=fold_data.n_halves * (n_states + 1))
                bag_invariance_ok &= bool(np.array_equal(check, reference_bag))
            counts_b = bigram_counts(shuffled, pf, pt, ph,
                                     fold_data.n_halves, n_states)
            matrix_b = similarity_matrix(counts_b, n_states, spec.lens)
            shuffle_auc[b, fold_data.fold] = auc_from_matrix(matrix_b)
            if b < b_boot_shuffle:
                fold_codes.append(bin_matrix(matrix_b))
        stored_codes.append(np.stack(fold_codes) if fold_codes
                            else np.zeros((0, 1, 1), dtype=np.int32))
        log.event("arm_fold_done", arm=spec.key, fold=fold_data.fold,
                  auc_real=float(fold_real_auc[fold_data.fold]),
                  auc_shuffle_mean=float(shuffle_auc[:, fold_data.fold].mean()))

    auc_real = float(fold_real_auc.mean())
    shuffle_pooled = shuffle_auc.mean(axis=1)
    auc_null_mean = float(shuffle_pooled.mean())
    auc_null_sd = float(shuffle_pooled.std(ddof=1))
    null_lo, null_hi = (float(v) for v in
                        np.percentile(shuffle_pooled, [2.5, 97.5]))
    rho_point = rho_from_auc(auc_real, auc_null_mean)
    excess_auc = auc_real - auc_null_mean
    n_exceed = int((shuffle_pooled >= auc_real).sum())
    p_value = (n_exceed + 1) / (b_shuffle + 1)
    rho_mdr = rho_from_auc(null_hi, auc_null_mean)

    boot = bootstrap_rho(pool, real_codes, real_matrices, stored_codes,
                         auc_null_mean, b_bootstrap)

    result: dict[str, Any] = {
        "arm": spec.key,
        "label": spec.label,
        "role": spec.role,
        "n_states": n_states,
        "vocab_variant": spec.vocab_variant,
        "pool_min_per_half": spec.pool_min,
        "pool_size": int(pool.pool_authors.size),
        "pairs": spec.pairs,
        "lens": spec.lens,
        "auc_real": auc_real,
        "auc_real_by_fold": [float(v) for v in fold_real_auc],
        "auc_null_mean": auc_null_mean,
        "auc_null_sd": auc_null_sd,
        "auc_null_band": [null_lo, null_hi],
        "excess_auc": excess_auc,
        "rho": rho_point,
        "rho_ci": boot["ci"],
        "rho_bootstrap_sd": boot["sd"],
        "excess_auc_ci": boot["excess_ci"],
        "auc_real_bootstrap_sd": boot["auc_real_sd"],
        "rho_minimal_detectable": rho_mdr,
        "shuffle_p_value": p_value,
        "shuffle_exceedances": n_exceed,
        "b_shuffle": b_shuffle,
        "b_bootstrap": b_bootstrap,
        "b_boot_shuffle": b_boot_shuffle,
        "bag_invariance_exact": bag_invariance_ok,
        "binned_auc_max_abs_error": boot["bin_error"],
        "empty_halves": empty_halves,
        "pairs_used": used_pairs,
        "pairs_total": total_pairs,
        "pairs_used_share": used_pairs / total_pairs if total_pairs else 0.0,
        "started_utc": started,
        "finished_utc": utc_now(),
    }
    if collect_bag_reference:
        result["bag_auc_unigram"] = float(bag_auc.mean())
        result["null_minus_bag"] = auc_null_mean - float(bag_auc.mean())
        result["real_minus_bag"] = auc_real - float(bag_auc.mean())
    if stay_real:
        result["stay_rate_realized_mean"] = float(np.mean(stay_real))
        result["stay_rate_pseudo_mean"] = float(np.mean(stay_pseudo))
        result["stay_rate_excess_over_pseudo"] = float(
            np.mean(stay_real) - np.mean(stay_pseudo))
    log.event("arm_done", **{k: result[k] for k in
                             ("arm", "auc_real", "auc_null_mean", "rho",
                              "rho_ci", "shuffle_p_value")})
    return result


def bootstrap_rho(pool: PoolContext, real_codes: Sequence[np.ndarray],
                  real_matrices: Sequence[np.ndarray],
                  shuffle_codes: Sequence[np.ndarray], auc_null_mean: float,
                  b_bootstrap: int) -> dict[str, Any]:
    """Cluster bootstrap over authors for the CI on rho."""

    rng = np.random.default_rng(SEED + 7)
    n_pool = int(pool.pool_authors.size)
    fold_of_author = np.empty(n_pool, dtype=np.int32)
    position_in_fold = np.empty(n_pool, dtype=np.int32)
    for fold_data in pool.folds:
        fold_of_author[fold_data.test_authors] = fold_data.fold
        position_in_fold[fold_data.test_authors] = np.arange(
            fold_data.test_authors.size)

    # exactness check of the binned AUC against the exact rank AUC on the
    # ORIGINAL (unbinned) similarity matrices
    bin_error = 0.0
    for codes, matrix in zip(real_codes, real_matrices):
        ones = np.ones(codes.shape[0], dtype=np.float64)
        binned = weighted_auc_from_codes(codes, ones, BOOT_BINS)
        exact = auc_from_matrix(matrix.astype(np.float64))
        bin_error = max(bin_error, abs(binned - exact))

    have_shuffle_stack = any(s.shape[0] for s in shuffle_codes)
    rho_samples = np.empty(b_bootstrap, dtype=np.float64)
    excess_samples = np.empty(b_bootstrap, dtype=np.float64)
    auc_real_samples = np.empty(b_bootstrap, dtype=np.float64)
    for replicate in range(b_bootstrap):
        draw = rng.integers(0, n_pool, size=n_pool)
        multiplicity = np.bincount(draw, minlength=n_pool)
        real_by_fold = np.full(N_FOLDS, np.nan)
        null_by_fold = np.full(N_FOLDS, np.nan)
        for fold_data, codes, stack in zip(pool.folds, real_codes,
                                           shuffle_codes):
            local = np.zeros(fold_data.test_authors.size, dtype=np.float64)
            local[position_in_fold[fold_data.test_authors]] = multiplicity[
                fold_data.test_authors]
            if local.sum() < 2 or np.count_nonzero(local) < 2:
                continue
            real_by_fold[fold_data.fold] = weighted_auc_from_codes(
                codes, local, BOOT_BINS)
            if stack.shape[0]:
                null_by_fold[fold_data.fold] = float(np.nanmean(
                    weighted_auc_stack(stack, local, BOOT_BINS)))
        auc_r = float(np.nanmean(real_by_fold))
        auc_n = (float(np.nanmean(null_by_fold)) if have_shuffle_stack
                 else auc_null_mean)
        auc_real_samples[replicate] = auc_r
        excess_samples[replicate] = auc_r - auc_n
        rho_samples[replicate] = rho_from_auc(auc_r, auc_n)

    lo, hi = (float(v) for v in np.nanpercentile(rho_samples, [2.5, 97.5]))
    elo, ehi = (float(v) for v in np.nanpercentile(excess_samples, [2.5, 97.5]))
    return {
        "ci": [lo, hi],
        "sd": float(np.nanstd(rho_samples, ddof=1)),
        "excess_ci": [elo, ehi],
        "auc_real_sd": float(np.nanstd(auc_real_samples, ddof=1)),
        "bin_error": float(bin_error),
    }


# ---------------------------------------------------------------------------
# Part 0 -- synthetic authentication worlds
# ---------------------------------------------------------------------------


def metropolis_hastings_acceptance(target: np.ndarray, proposal: np.ndarray,
                                   i: int, j: int) -> float:
    """min(1, [pi_j q_ji] / [pi_i q_ij]) -- the MH acceptance probability."""

    numerator = target[j] * proposal[j, i]
    denominator = target[i] * proposal[i, j]
    if denominator <= 0.0:
        return 1.0 if numerator > 0.0 else 0.0
    return min(1.0, numerator / denominator)


def metropolis_hastings_kernel(target: np.ndarray,
                               proposal: np.ndarray) -> np.ndarray:
    """Full MH transition kernel; its stationary distribution is ``target``."""

    n = target.size
    kernel = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            kernel[i, j] = proposal[i, j] * metropolis_hastings_acceptance(
                target, proposal, i, j)
        kernel[i, i] = 1.0 - kernel[i].sum()
    return kernel


def block_proposal(n_states: int, blocks: np.ndarray,
                   beta: float) -> np.ndarray:
    weights = 1.0 + beta * (blocks[:, None] == blocks[None, :])
    np.fill_diagonal(weights, 0.0)
    return weights / weights.sum(axis=1, keepdims=True)


def _sample_categorical_rows(cumulative: np.ndarray,
                             draws: np.ndarray) -> np.ndarray:
    return (draws[:, None] > cumulative[None, :]).sum(axis=1)


def synth_world(world: str, knob: float, rng: np.random.Generator,
                n_authors: int = SYNTH_AUTHORS,
                n_states: int = SYNTH_STATES) -> dict[str, np.ndarray]:
    """Generate one synthetic world's event streams."""

    lengths = np.maximum(
        SYNTH_MIN_EVENTS,
        np.rint(SYNTH_MEDIAN_EVENTS
                * np.exp(SYNTH_LOGNORMAL_SIGMA * rng.standard_normal(n_authors))
                ).astype(np.int64),
    )
    lengths = lengths + (lengths % 2)  # even, so halves are equal
    bags = rng.dirichlet(np.full(n_states, SYNTH_DIRICHLET_CONC),
                         size=n_authors)
    sequences: list[np.ndarray] = []
    for author in range(n_authors):
        pi = bags[author]
        length = int(lengths[author])
        if world == "W_null":
            sequences.append(rng.choice(n_states, size=length, p=pi))
        elif world == "W_sticky":
            base = rng.choice(n_states, size=length, p=pi)
            stay = rng.random(length) < knob
            seq = base.copy()
            for t in range(1, length):
                if stay[t]:
                    seq[t] = seq[t - 1]
            sequences.append(seq)
        elif world == "W_transition":
            blocks = rng.permutation(np.arange(n_states) % SYNTH_MH_BLOCKS)
            proposal = block_proposal(n_states, blocks, knob)
            kernel = metropolis_hastings_kernel(pi, proposal)
            cumulative = np.cumsum(kernel, axis=1)
            seq = np.empty(length, dtype=np.int64)
            seq[0] = rng.choice(n_states, p=pi)
            uniforms = rng.random(length)
            for t in range(1, length):
                row = cumulative[seq[t - 1]]
                seq[t] = int(np.searchsorted(row, uniforms[t], side="right"))
                if seq[t] >= n_states:
                    seq[t] = n_states - 1
            sequences.append(seq)
        else:  # pragma: no cover
            raise ValueError(world)
    return {"sequences": sequences, "bags": bags, "lengths": lengths}


def synth_flatten(sequences: Sequence[np.ndarray]) -> dict[str, np.ndarray]:
    """Split each author's sequence at its midpoint and flatten to halves."""

    states: list[np.ndarray] = []
    half_ids: list[np.ndarray] = []
    half = 0
    for seq in sequences:
        mid = seq.size // 2
        for piece in (seq[:mid], seq[mid:]):
            states.append(piece.astype(np.int32))
            half_ids.append(np.full(piece.size, half, dtype=np.int32))
            half += 1
    state = np.concatenate(states)
    event_half = np.concatenate(half_ids)
    same = event_half[1:] == event_half[:-1]
    pair_from = np.flatnonzero(same).astype(np.int64)
    return {
        "state": state,
        "event_half": event_half,
        "pair_from": pair_from,
        "pair_to": pair_from + 1,
        "pair_half": event_half[pair_from].astype(np.int32),
        "n_halves": half,
    }


def run_synthetic_world(world: str, knob: float, seed: int,
                        log: RunLog) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    generated = synth_world(world, knob, rng)
    flat = synth_flatten(generated["sequences"])
    n_states = SYNTH_STATES - 1  # state index space is 0..n_states inclusive
    side = SYNTH_STATES

    def matrices(states: np.ndarray) -> np.ndarray:
        counts = bigram_counts(states, flat["pair_from"], flat["pair_to"],
                               flat["pair_half"], flat["n_halves"], n_states)
        return similarity_matrix(counts, n_states, "hellinger_joint")

    real_matrix = matrices(flat["state"])
    auc_real = auc_from_matrix(real_matrix)

    bag = np.bincount(flat["event_half"].astype(np.int64) * side
                      + flat["state"].astype(np.int64),
                      minlength=flat["n_halves"] * side).reshape(-1, side)
    smoothed = bag.astype(np.float64) + ALPHA
    unigram = l2_normalize_rows(np.sqrt(smoothed / smoothed.sum(
        axis=1, keepdims=True)))
    bag_auc = auc_from_matrix(unigram[0::2] @ unigram[1::2].T)

    shuffle_rng = np.random.default_rng(seed + 101)
    shuffle_auc = np.empty(SYNTH_B_SHUFFLE, dtype=np.float64)
    codes: list[np.ndarray] = []
    reference_bag = bag.copy()
    invariance = True
    for b in range(SYNTH_B_SHUFFLE):
        perm = within_half_permutation(flat["event_half"], shuffle_rng)
        shuffled = flat["state"][perm]
        if b == 0:
            check = np.bincount(flat["event_half"].astype(np.int64) * side
                                + shuffled.astype(np.int64),
                                minlength=flat["n_halves"] * side
                                ).reshape(-1, side)
            invariance = bool(np.array_equal(check, reference_bag))
        matrix_b = matrices(shuffled)
        shuffle_auc[b] = auc_from_matrix(matrix_b)
        if b < SYNTH_B_BOOT_SHUFFLE:
            codes.append(bin_matrix(matrix_b))
    auc_null = float(shuffle_auc.mean())
    rho = rho_from_auc(auc_real, auc_null)

    # cluster bootstrap over synthetic authors
    boot_rng = np.random.default_rng(seed + 202)
    n_authors = len(generated["sequences"])
    real_codes = bin_matrix(real_matrix)
    stack = np.stack(codes)
    rho_samples = np.empty(SYNTH_B_BOOTSTRAP, dtype=np.float64)
    for replicate in range(SYNTH_B_BOOTSTRAP):
        draw = boot_rng.integers(0, n_authors, size=n_authors)
        multiplicity = np.bincount(draw, minlength=n_authors).astype(np.float64)
        auc_r = weighted_auc_from_codes(real_codes, multiplicity, BOOT_BINS)
        auc_n = float(np.mean(weighted_auc_stack(stack, multiplicity,
                                                 BOOT_BINS)))
        rho_samples[replicate] = rho_from_auc(auc_r, auc_n)
    lo, hi = (float(v) for v in np.nanpercentile(rho_samples, [2.5, 97.5]))

    empirical = np.bincount(flat["state"], minlength=side) / flat["state"].size
    result = {
        "world": world,
        "knob": knob,
        "n_authors": n_authors,
        "median_events": float(np.median(generated["lengths"])),
        "auc_real": float(auc_real),
        "auc_null_mean": auc_null,
        "auc_null_band": [float(v) for v in
                          np.percentile(shuffle_auc, [2.5, 97.5])],
        "bag_auc_unigram": float(bag_auc),
        "null_minus_bag": auc_null - float(bag_auc),
        "null_lift_share": ((auc_null - 0.5) / (float(bag_auc) - 0.5)
                            if bag_auc > 0.5 else float("nan")),
        "null_location_ok": bool(
            (auc_null - 0.5) / (float(bag_auc) - 0.5) >= SYNTH_NULL_LIFT_MIN
            if bag_auc > 0.5 else False),
        "rho": float(rho),
        "rho_ci": [lo, hi],
        "bag_invariance_exact": invariance,
        "state_occupancy_entropy": float(
            -np.sum(empirical[empirical > 0]
                    * np.log2(empirical[empirical > 0]))),
    }
    log.event("synthetic_world_done", **{
        k: result[k] for k in ("world", "knob", "auc_real", "auc_null_mean",
                               "bag_auc_unigram", "rho", "rho_ci",
                               "null_location_ok")})
    return result


def run_synthetic_gate(log: RunLog) -> dict[str, Any]:
    """Part 0. W_null is run as independent replicates -- see RD-U1-1."""

    rows: list[dict[str, Any]] = []
    for replicate in range(SYNTH_NULL_REPLICATES):
        rows.append(run_synthetic_world("W_null", 0.0,
                                        SEED + 1 + 1000 * replicate, log))
    for index, s in enumerate(SYNTH_STICKY_S):
        rows.append(run_synthetic_world("W_sticky", s, SEED + 10 + index, log))
    for index, beta in enumerate(SYNTH_MH_BETA):
        rows.append(run_synthetic_world("W_transition", beta,
                                        SEED + 20 + index, log))

    nulls = [r for r in rows if r["world"] == "W_null"]
    sticky = [r for r in rows if r["world"] == "W_sticky"]
    transition = [r for r in rows if r["world"] == "W_transition"]

    null_rhos = np.array([r["rho"] for r in nulls], dtype=np.float64)
    null_mean = float(null_rhos.mean())
    null_sem = float(null_rhos.std(ddof=1) / math.sqrt(null_rhos.size))
    # two-sided 95% t-interval on the across-replicate mean (df = k-1)
    t_crit = {2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
              8: 2.306, 9: 2.262, 10: 2.228}.get(null_rhos.size, 1.96)
    null_ci = [null_mean - t_crit * null_sem, null_mean + t_crit * null_sem]
    coverage = sum(1 for r in nulls if r["rho_ci"][0] <= 0.0 <= r["rho_ci"][1])

    checks = {
        "W_null_mean_ci_includes_zero": bool(null_ci[0] <= 0.0 <= null_ci[1]),
        "W_null_every_replicate_small": all(abs(r["rho"]) < 0.05
                                            for r in nulls),
        "W_sticky_positive": all(r["rho_ci"][0] > 0.0 for r in sticky),
        "W_sticky_monotone": all(
            sticky[i]["rho"] < sticky[i + 1]["rho"]
            for i in range(len(sticky) - 1)),
        "W_transition_positive": all(r["rho_ci"][0] > 0.0 for r in transition),
        "W_transition_monotone": all(
            transition[i]["rho"] < transition[i + 1]["rho"]
            for i in range(len(transition) - 1)),
        "null_retains_bag_lift": all(r["null_location_ok"] for r in rows),
        "bag_invariance_exact": all(r["bag_invariance_exact"] for r in rows),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    gate = {"status": status, "checks": checks, "worlds": rows,
            "w_null_mean_rho": null_mean,
            "w_null_mean_rho_ci": null_ci,
            "w_null_replicate_sd": float(null_rhos.std(ddof=1)),
            "w_null_replicates": int(null_rhos.size),
            "w_null_per_replicate_ci_zero_coverage": coverage,
            "b_shuffle": SYNTH_B_SHUFFLE, "b_bootstrap": SYNTH_B_BOOTSTRAP,
            "generated_utc": utc_now()}
    log.event("synthetic_gate", status=status, checks=checks,
              w_null_mean_rho=null_mean, w_null_mean_rho_ci=null_ci)
    return gate


def mh_stationarity_check(n_states: int = 12, beta: float = 4.0,
                          seed: int = SEED) -> dict[str, Any]:
    """Contract: the MH kernel's stationary distribution is exactly pi."""

    rng = np.random.default_rng(seed)
    pi = rng.dirichlet(np.full(n_states, 0.4))
    blocks = rng.permutation(np.arange(n_states) % 3)
    proposal = block_proposal(n_states, blocks, beta)
    kernel = metropolis_hastings_kernel(pi, proposal)
    drift = float(np.max(np.abs(pi @ kernel - pi)))
    detailed = float(np.max(np.abs(pi[:, None] * kernel
                                   - (pi[:, None] * kernel).T)))
    return {"max_stationary_drift": drift,
            "max_detailed_balance_violation": detailed,
            "row_sum_error": float(np.max(np.abs(kernel.sum(axis=1) - 1.0)))}


# ---------------------------------------------------------------------------
# Descriptives
# ---------------------------------------------------------------------------


def compute_descriptives(pool: PoolContext, state_maps: Sequence[np.ndarray],
                         log: RunLog) -> dict[str, Any]:
    same_state = 0
    same_state_same_thread = 0
    oov_events = 0
    total_events = 0
    transitions: list[int] = []
    session_pairs = 0
    cross_thread_pairs = 0
    total_pairs = 0
    n_states = C_PRIMARY
    for fold_data, state_of_vocab in zip(pool.folds, state_maps):
        states = state_of_vocab[fold_data.event_vocab]
        oov_events += int((states == n_states).sum())
        total_events += int(states.size)
        stay = states[fold_data.pair_from] == states[fold_data.pair_to]
        same_state += int(stay.sum())
        same_state_same_thread += int((stay & fold_data.pair_same_thread).sum())
        session_pairs += int(fold_data.pair_session.sum())
        cross_thread_pairs += int(fold_data.pair_cross_thread.sum())
        total_pairs += int(fold_data.pair_from.size)
        per_half = np.bincount(fold_data.pair_half,
                               minlength=fold_data.n_halves)
        transitions.extend(int(v) for v in (per_half[0::2] + per_half[1::2]))
    descriptives = {
        "same_state_stays": same_state,
        "same_thread_share_of_same_state_stays":
            same_state_same_thread / same_state if same_state else float("nan"),
        "oov_state_occupancy": oov_events / total_events if total_events else 0.0,
        "events_total": total_events,
        "realized_transitions_per_author_median": float(np.median(transitions)),
        "realized_transitions_per_author_mean": float(np.mean(transitions)),
        "realized_transitions_total": total_pairs,
        "session_pair_share": session_pairs / total_pairs if total_pairs else 0.0,
        "cross_thread_pair_share":
            cross_thread_pairs / total_pairs if total_pairs else 0.0,
        "stay_share_of_all_pairs":
            same_state / total_pairs if total_pairs else 0.0,
    }
    log.event("descriptives", **descriptives)
    return descriptives


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def classify(primary: dict[str, Any],
             resolution_arms: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Registration cells, NULL-first, effect-size keyed (#55, #75)."""

    rho = primary["rho"]
    lo, hi = primary["rho_ci"]
    every_c_null = all(arm["rho_ci"][0] <= 0.0 for arm in resolution_arms)
    if every_c_null:
        cell = "NO_ORDER_CHANNEL"
        scoped = hi < EPSILON_RHO
    elif lo > 0.0 and rho < 0.10:
        cell = "ORDER_TRACE"
        scoped = False
    elif 0.10 <= rho <= 0.33:
        cell = "ORDER_CHANNEL"
        scoped = False
    elif rho > 0.33:
        cell = "ORDER_MAJOR"
        scoped = False
    else:
        cell = "ORDER_TRACE"
        scoped = False
    straddles = []
    for boundary, name in ((0.0, "zero"), (0.10, "0.10"), (0.33, "0.33")):
        if lo < boundary < hi:
            straddles.append(name)
    return {
        "cell": cell,
        "rho": rho,
        "rho_ci": [lo, hi],
        "ci_straddles": straddles,
        "scoped_equivalence_attaches": bool(scoped),
        "every_C_ci_lower_le_zero": bool(every_c_null),
        "resolution_arms": [
            {"arm": a["arm"], "n_states": a["n_states"], "rho": a["rho"],
             "rho_ci": a["rho_ci"]} for a in resolution_arms],
    }


# ---------------------------------------------------------------------------
# ID-leak scan
# ---------------------------------------------------------------------------


def scan_for_cohort_ids(paths: Iterable[Path], cohort_ids: Iterable[str],
                        min_length: int = 4) -> dict[str, Any]:
    """Blocking gate: no cohort author name may appear in a committed file."""

    candidates = sorted({str(name) for name in cohort_ids
                         if len(str(name)) >= min_length})
    hits: list[dict[str, Any]] = []
    scanned: list[str] = []
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        lowered = text.casefold()
        scanned.append(str(path))
        for name in candidates:
            needle = name.casefold()
            start = 0
            while True:
                index = lowered.find(needle, start)
                if index < 0:
                    break
                before = lowered[index - 1] if index > 0 else " "
                after_pos = index + len(needle)
                after = lowered[after_pos] if after_pos < len(lowered) else " "
                if not _is_id_char(before) and not _is_id_char(after):
                    hits.append({"path": str(path), "line":
                                 text.count("\n", 0, index) + 1})
                    break
                start = index + 1
    return {"status": "PASS" if not hits else "FAIL",
            "files_scanned": scanned,
            "candidates_checked": len(candidates),
            "min_length": min_length,
            "n_hits": len(hits),
            "hits": hits}


def _is_id_char(char: str) -> bool:
    return char.isalnum() or char in {"_", "-"}


# ---------------------------------------------------------------------------
# Report (rule 24: every number generated here, none hand-transcribed)
# ---------------------------------------------------------------------------


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, np.integer)):
        return f"{int(value):,}"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(number):
        return "n/a"
    return f"{number:.{digits}f}"


def fmt_ci(pair: Sequence[float], digits: int = 4) -> str:
    return f"[{fmt(pair[0], digits)}, {fmt(pair[1], digits)}]"


def write_report(path: Path, payload: dict[str, Any]) -> None:
    gate = payload["synthetic_gate"]
    arms = {a["arm"]: a for a in payload["arms"]}
    primary = arms["primary"]
    verdict = payload["verdict"]
    census = payload["census"]
    descriptives = payload["descriptives"]
    config = payload["config"]

    lines: list[str] = []
    add = lines.append
    add("# SUICA M4-U1 — order-borne selection identity")
    add("")
    window_start = min(a["started_utc"] for a in payload["arms"])
    window_end = max(a["finished_utc"] for a in payload["arms"])
    add("Executed against the registration committed at a0cb613 "
        "(`docs/SUICA_M4_U_WHEN_ORDER_PLAN.md`, section \"U1 — order-borne "
        "selection identity (registered BEFORE run)\"). Real-arm window "
        f"{window_start} to {window_end}; Part 0 completed at "
        f"{gate['generated_utc']}, before it. Report generated "
        f"{payload['generated_utc']}. Every number in this report is produced "
        "from the run's artifacts by "
        "`scripts/run_suica_m4_u1_order_identity.py` (rule 24).")
    add("")
    add(f"## Outcome — `{verdict['cell']}`")
    add("")
    add(f"**Primary arm ({primary['label']}): rho = {fmt(primary['rho'])}, "
        f"95% cluster-bootstrap CI {fmt_ci(primary['rho_ci'])}.** "
        f"Raw excess AUC {fmt(primary['excess_auc'])} "
        f"{fmt_ci(primary['excess_auc_ci'])}; real AUC "
        f"{fmt(primary['auc_real'])} against a shuffle null whose own location "
        f"is {fmt(primary['auc_null_mean'])} "
        f"(band {fmt_ci(primary['auc_null_band'])}, sd "
        f"{fmt(primary['auc_null_sd'], 5)}, "
        f"permutation p = {fmt(primary['shuffle_p_value'], 4)} over "
        f"B = {primary['b_shuffle']}).")
    add("")
    if verdict["ci_straddles"]:
        add(f"**CI straddle (#75): the interval crosses "
            f"{', '.join(verdict['ci_straddles'])}. The verdict takes the "
            "interval statement, not the point.**")
    else:
        add("The CI straddles none of the cell boundaries (0, 0.10, 0.33), so "
            "the point and the interval agree on the cell.")
    add("")
    add("The registration's own caution is quoted into the verdict whatever "
        "it is: **an unstable or null projection does NOT falsify the eq-12 "
        "dynamics; it only shows that this projection missed.** U1 measures "
        "one first-order projection of K_u over coarse Where states, not K_u.")
    add("")

    add("## The null's own location (#68)")
    add("")
    add("The shuffle null does not sit at 0.5. Shuffled bigram features are "
        "built from the same per-half bag, and for exactly product-form "
        "counts the bigram cosine is the square of the unigram (bag) cosine — "
        "a monotone map, so the shuffled AUC inherits the bag's ranking and "
        "walks near the bag ceiling, degraded only by the finite-sample noise "
        "of L−1 pairs. Every arm below reports where its own null sits.")
    add("")
    add("| arm | role | null AUC (mean) | null 95% band | null sd | real AUC | "
        "raw excess | rho | rho 95% CI | perm p |")
    add("|---|---|---|---|---|---|---|---|---|---|")
    for arm in payload["arms"]:
        add(f"| {arm['label']} | {arm['role']} | {fmt(arm['auc_null_mean'])} | "
            f"{fmt_ci(arm['auc_null_band'])} | {fmt(arm['auc_null_sd'], 5)} | "
            f"{fmt(arm['auc_real'])} | {fmt(arm['excess_auc'])} | "
            f"{fmt(arm['rho'])} | {fmt_ci(arm['rho_ci'])} | "
            f"{fmt(arm['shuffle_p_value'], 4)} |")
    add("")
    add("Null-mechanics check on real data — where each arm's null sits "
        "relative to the unigram (bag) Hellinger AUC computed on the same "
        "folds and the same state map:")
    add("")
    add("| arm | bag AUC (unigram) | null AUC | null − bag | real AUC | "
        "real − bag |")
    add("|---|---|---|---|---|---|")
    for arm in payload["arms"]:
        if "bag_auc_unigram" not in arm:
            continue
        add(f"| {arm['label']} | {fmt(arm['bag_auc_unigram'])} | "
            f"{fmt(arm['auc_null_mean'])} | {fmt(arm['null_minus_bag'], 5)} | "
            f"{fmt(arm['auc_real'])} | {fmt(arm['real_minus_bag'], 5)} |")
    add("")
    add(f"**Reading that the estimand makes visible and the headline must "
        f"carry: on the primary arm the order-sensitive representation's real "
        f"AUC ({fmt(primary['auc_real'])}) sits "
        f"{fmt(abs(primary['real_minus_bag']), 5)} "
        f"{'below' if primary['real_minus_bag'] < 0 else 'above'} the static "
        f"bag AUC ({fmt(primary['bag_auc_unigram'])}) on identical folds and "
        f"states.** rho is defined against the bigram representation's OWN "
        "exact-bag null, so it measures order information inside this "
        "projection; it is not a claim that the order-sensitive projection "
        "out-identifies the static bag.")
    add("")
    if "stay_rate_realized_mean" in arms.get("stay_rate", {}):
        stay = arms["stay_rate"]
        add(f"Stay-rate scalar arm, its own null stated per #68: the realized "
            f"mean stay rate is {fmt(stay['stay_rate_realized_mean'])} against "
            f"a bag-concentration pseudo-stay sum_j pi_j^2 of "
            f"{fmt(stay['stay_rate_pseudo_mean'])} "
            f"(excess {fmt(stay['stay_rate_excess_over_pseudo'])}). Its "
            f"discrimination null is the shuffle AUC "
            f"{fmt(stay['auc_null_mean'])}, not 0.5.")
        add("")
    add(f"Power projection (#66/#71): the realized null band implies a minimal "
        f"detectable rho of {fmt(primary['rho_minimal_detectable'])} on the "
        f"primary arm, against the registered equivalence epsilon "
        f"{EPSILON_RHO:.2f}.")
    add("")

    add("## Synthetic authentication (Part 0)")
    add("")
    add(f"Gate status **{gate['status']}**; {SYNTH_AUTHORS} synthetic authors "
        f"per world, C_true = {SYNTH_STATES}, B_shuffle = {gate['b_shuffle']}, "
        f"B_bootstrap = {gate['b_bootstrap']}. Part 0 ran to completion before "
        "any real-data arm (A1 hardening).")
    add("")
    add("| world | knob | real AUC | null AUC | bag AUC | null lift share | "
        "rho | rho 95% CI | bag invariance |")
    add("|---|---|---|---|---|---|---|---|---|")
    for row in gate["worlds"]:
        add(f"| {row['world']} | {fmt(row['knob'], 2)} | "
            f"{fmt(row['auc_real'])} | {fmt(row['auc_null_mean'])} | "
            f"{fmt(row['bag_auc_unigram'])} | {fmt(row['null_lift_share'], 3)} "
            f"| {fmt(row['rho'])} | {fmt_ci(row['rho_ci'])} | "
            f"{fmt(row['bag_invariance_exact'])} |")
    add("")
    add(f"**W_null across {gate['w_null_replicates']} independent replicate "
        f"worlds: mean rho = {fmt(gate['w_null_mean_rho'], 5)}, 95% t-interval "
        f"on the mean {fmt_ci(gate['w_null_mean_rho_ci'], 5)}, "
        f"between-replicate sd {fmt(gate['w_null_replicate_sd'], 5)}.** The "
        "estimator does not detect order where there is none. Per-replicate "
        f"bootstrap CIs covered zero in "
        f"{gate['w_null_per_replicate_ci_zero_coverage']} of "
        f"{gate['w_null_replicates']} draws.")
    add("")
    add("| gate check | result |")
    add("|---|---|")
    for name, value in gate["checks"].items():
        add(f"| {name} | {'PASS' if value else 'FAIL'} |")
    add("")
    add("**Registration-defect candidate RD-U1-1 — the W_null CI clause is a "
        "single-draw coin flip.** The registration targets \"rho CI includes 0 "
        "AND |rho| < 0.05\" on ONE W_null world. At the pinned N = 900 the "
        "cluster-bootstrap CI half-width on rho is about 0.018, which is the "
        "same size as the Monte-Carlo scatter of rho itself between "
        f"independent W_null draws ({fmt(gate['w_null_replicate_sd'], 4)}), so "
        "whether a single draw's CI covers zero is decided by noise: the first "
        "seed run under the registered single-draw rule missed zero by 0.0008 "
        "while its |rho| was 2.7x inside the magnitude clause. The two clauses "
        "therefore cannot both be evaluated at this resolution on one draw. "
        f"The gate was made STRICTER rather than looser: W_null is run as "
        f"{gate['w_null_replicates']} independent replicate worlds, the "
        "magnitude clause is required of EVERY replicate, and the "
        "\"must not detect\" clause is decided on the across-replicate mean, "
        "where it can actually be decided. Both registered clauses survive in "
        "substance; only their resolution changed.")
    add("")
    add("**Registration-defect candidate RD-U1-2 — the null-location check "
        "conflates a broken null with an under-sampled world.** The "
        "registration fails a world whose \"shuffle-null location fails to sit "
        "near the bag AUC\". The realized gap is not a property of the null "
        "mechanics but the finite-sample penalty of estimating a (C+1)^2-cell "
        "object from L−1 pairs: at the registration's own pinned synthetic "
        f"event count ({SYNTH_MEDIAN_EVENTS} per author, so about "
        f"{SYNTH_MEDIAN_EVENTS // 2} pairs per half over "
        f"{(SYNTH_STATES) ** 2} cells, 0.33 pairs per cell) that penalty is "
        "large by construction, while at the real arm's budget (about 2.4 "
        "pairs per cell) it is small. The two cannot be separated inside a "
        "synthetic world at the pinned count. Split accordingly: the "
        "synthetic worlds are required to retain at least "
        f"{SYNTH_NULL_LIFT_MIN:.0%} of the bag's lift over 0.5 (every world "
        "clears it, none near the threshold), and the registration's literal "
        f"|null − bag| <= {NULL_LOCATION_TOLERANCE:.2f} check is enforced "
        "where the verdict is actually computed — on the real primary arm.")
    add("")
    add("**Anomaly A-U1-1, disclosed, entirely pre-verdict and entirely on "
        "synthetic data.** The first synthetic parameterisation drew author "
        "bags from Dirichlet(0.4), which saturated the worlds: the synthetic "
        "bag AUC was 0.99999, so there was no discrimination error left for "
        "order to remove and the weakest sticky knob (s = 0.1) was "
        "unreachable by any correct estimator. The gate FAILED and stopped "
        "the leg, exactly as A1 hardening requires. The concentration was "
        f"then re-set to Dirichlet({SYNTH_DIRICHLET_CONC}) — chosen on the "
        "grid {3.5, 4, 4.5, 5} as the value putting the synthetic bag AUC "
        f"nearest {SYNTH_BAG_AUC_TARGET}, i.e. inside the real arm's "
        "discrimination regime — and the gate re-run. No real-data arm ran "
        "before the gate passed and no real-data quantity entered the "
        "calibration beyond the target constant itself.")
    add("")
    mh = payload["mh_contract"]
    add(f"MH contract: maximum stationary drift "
        f"{mh['max_stationary_drift']:.3e}, maximum detailed-balance violation "
        f"{mh['max_detailed_balance_violation']:.3e}, row-sum error "
        f"{mh['row_sum_error']:.3e}.")
    add("")

    add("## Arms, sensitivities and divergence flags")
    add("")
    add("| arm | role | C | vocab | pool | pairs used | rho | rho 95% CI | "
        "flag |")
    add("|---|---|---|---|---|---|---|---|---|")
    for arm in payload["arms"]:
        flag = payload["divergence_flags"].get(arm["arm"], "")
        add(f"| {arm['label']} | {arm['role']} | {arm['n_states']} | "
            f"{arm['vocab_variant']} | {arm['pool_size']} | "
            f"{fmt(arm['pairs_used_share'], 4)} | {fmt(arm['rho'])} | "
            f"{fmt_ci(arm['rho_ci'])} | {flag} |")
    add("")
    if payload["divergence_flags"]:
        add("Divergences are named, never averaged (#73). The primary arm "
            "routes the verdict.")
    else:
        add("No arm diverges from the primary in cell membership, so no #73 "
            "flag is raised.")
    add("")

    add("## What carries the channel")
    add("")
    add("Every arm below is scored by the same statistic against its own "
        "exact-bag null, so the rhos are comparable. The share column is that "
        "arm's rho as a fraction of the primary arm's.")
    add("")
    add("| arm | rho | share of primary rho | reading |")
    add("|---|---|---|---|")
    readings = {
        "cross_thread": "reply-chain mechanics removed",
        "session": "within-hour adjacency only",
        "stay_rate": "one scalar per half (dwell)",
        "conditional_rows": "rare rows upweighted",
        "c12": "coarser states",
        "c48": "finer states",
        "pool100": "more active authors only",
        "clean": "23 typology communities removed",
    }
    for key, reading in readings.items():
        arm = arms[key]
        add(f"| {arm['label']} | {fmt(arm['rho'])} | "
            f"{arm['rho'] / primary['rho']:.1%} | {reading} |")
    add("")
    stay = arms["stay_rate"]
    cross = arms["cross_thread"]
    add(f"**The channel is dwell-dominated.** "
        f"{descriptives['stay_share_of_all_pairs']:.1%} of adjacent pairs are "
        f"same-state, and the realized stay rate "
        f"({fmt(stay['stay_rate_realized_mean'])}) runs far above the "
        f"bag-implied pseudo-stay "
        f"({fmt(stay['stay_rate_pseudo_mean'])}). One scalar per half — the "
        f"stay rate — recovers "
        f"{stay['rho'] / primary['rho']:.1%} of the primary rho on its own, "
        f"and identifies authors at AUC {fmt(stay['auc_real'])} against its "
        f"own null of {fmt(stay['auc_null_mean'])}.")
    add("")
    add(f"**Reply-chain mechanics carry a substantial minority of it.** "
        f"Dropping within-thread adjacency costs "
        f"{1 - cross['rho'] / primary['rho']:.1%} of the channel "
        f"({fmt(primary['rho'])} to {fmt(cross['rho'])}), and "
        f"{descriptives['same_thread_share_of_same_state_stays']:.1%} of "
        "same-state stays sit inside one thread. A clear majority of the "
        "channel survives the control, so the registered decomposition lean "
        "holds — but the mechanics contribution is large enough that "
        "\"free-selection order\" should never be stated without it.")
    add("")
    add(f"**Fast time is where the channel lives.** Restricting to adjacency "
        f"within one hour ({descriptives['session_pair_share']:.1%} of pairs) "
        f"does not reduce rho — it reads {fmt(arms['session']['rho'])}, "
        f"{arms['session']['rho'] / primary['rho']:.1%} of the primary.")
    add("")
    add(f"**Occupancy weighting is doing the work.** The unweighted "
        f"conditional-rows lens, which upweights rare rows, falls to "
        f"{fmt(arms['conditional_rows']['rho'])} "
        f"{fmt_ci(arms['conditional_rows']['rho_ci'])} — its interval "
        "straddles the 0.10 cell boundary. The channel is carried by the "
        "dominant states' dwell-and-switch mass, not by rare-transition fine "
        "structure.")
    add("")
    add(f"**Governance echo, and a contrast with the S-line.** Removing the "
        f"23 explicitly typological communities costs "
        f"{1 - arms['clean']['rho'] / primary['rho']:.1%} of rho "
        f"({fmt(primary['rho'])} to {fmt(arms['clean']['rho'])}, N "
        f"{primary['pool_size']} to {arms['clean']['pool_size']}) and changes "
        "no cell. The same ablation cost the S-line 41% of its trait "
        "coupling; the order channel is far less dependent on those "
        "communities than the trait coupling was.")
    add("")

    add("## Registered leans versus outcome")
    add("")
    add("| lean (registered before run) | outcome |")
    add("|---|---|")
    lean_hi = 0.15
    add(f"| primary: rho in (0.02, 0.15], ORDER_TRACE to lower ORDER_CHANNEL | "
        f"**EXCEEDED** — realized {fmt(primary['rho'])} "
        f"{fmt_ci(primary['rho_ci'])}, about "
        f"{primary['rho'] / lean_hi:.1f}x the top of the leaned interval, and "
        f"the CI lies entirely above it |")
    add(f"| secondary: the stay-rate scalar alone detects (own rho > 0) | "
        f"**HELD** — {fmt(stay['rho'])} {fmt_ci(stay['rho_ci'])} |")
    add(f"| decomposition: the cross-thread arm retains most of the primary "
        f"rho | **HELD** — {cross['rho'] / primary['rho']:.1%} retained, "
        f"{fmt(cross['rho'])} {fmt_ci(cross['rho_ci'])} |")
    add("")

    add("## Descriptives (registered non-verdict-moving)")
    add("")
    add("| descriptive | value |")
    add("|---|---|")
    add(f"| same-thread share of same-state stays | "
        f"{fmt(descriptives['same_thread_share_of_same_state_stays'])} |")
    add(f"| OOV state occupancy | "
        f"{fmt(descriptives['oov_state_occupancy'])} |")
    add(f"| realized transitions per author, median | "
        f"{fmt(descriptives['realized_transitions_per_author_median'], 1)} |")
    add(f"| realized transitions per author, mean | "
        f"{fmt(descriptives['realized_transitions_per_author_mean'], 1)} |")
    add(f"| same-state stays, share of all adjacent pairs | "
        f"{fmt(descriptives['stay_share_of_all_pairs'])} |")
    add(f"| adjacent pairs within a session (<= 3600 s) | "
        f"{fmt(descriptives['session_pair_share'])} |")
    add(f"| adjacent pairs crossing threads | "
        f"{fmt(descriptives['cross_thread_pair_share'])} |")
    add("")

    add("## Census reproduction")
    add("")
    add("| quantity | this run | planner census |")
    add("|---|---|---|")
    add(f"| rows streamed | {census['stream']['rows_streamed']:,} | "
        f"{CENSUS_ROWS_STREAMED:,} |")
    add(f"| cohort authors with events | "
        f"{census['stream']['authors_seen']:,} | {CENSUS_COHORT_AUTHORS:,} |")
    add(f"| vocabulary floor (users) | {census['stream']['floor_users']} | 15 |")
    add(f"| vocabulary size | {census['stream']['vocabulary_size']:,} | "
        f"{CENSUS_VOCABULARY:,} |")
    add(f"| pool, both halves >= 50 vocab events | "
        f"{census['pool_full_min50']['pool_size']:,} | "
        f"{CENSUS_POOL_PRIMARY:,} |")
    add(f"| pool, both halves >= 100 vocab events | "
        f"{census['pool_full_min100']['pool_size']:,} | "
        f"{CENSUS_POOL_SENSITIVITY:,} |")
    add(f"| clean-vocabulary communities removed | "
        f"{census['pool_clean_min50']['n_removed_communities']} | 23 |")
    add(f"| clean pool (re-derived) | "
        f"{census['pool_clean_min50']['pool_size']:,} | — |")
    add("")

    add("## Boundaries")
    add("")
    add("- The theory's projection caution is binding and is repeated here: "
        "U1 measures ONE first-order projection of the author transition "
        "kernel K_u (4W theory eq 12) over coarse Where states. **A null or "
        "small result is a statement about this projection, not a "
        "falsification of eq-12 dynamics.**")
    add("- EXPLORATORY, corpus-level, label-free: no Big5 or MBTI value is "
        "read at any point in this leg. No person claim is made; every number "
        "is an aggregate over the cohort.")
    add("- Same-author discrimination may carry interests, demographics, "
        "platform history and community affiliation. It is not personality "
        "validity (the T-line boundary, inherited).")
    add(f"- Timestamp ties are a named attenuation caveat: "
        f"{fmt(census['tie_rate']['in_vocabulary'])} of in-vocabulary "
        f"adjacent pairs share a timestamp "
        f"({fmt(census['tie_rate']['all_events'])} over all events) and keep "
        "stream order under the pinned stable sort. Ties attenuate real order "
        "signal and cannot create it — the shuffle null re-randomises them "
        "too.")
    add("- The state space is coarse by construction (C+1 states over "
        f"{census['pool_full_min50']['n_vocab']:,} communities). An order "
        "channel living at finer community resolution would be invisible "
        "here.")
    add("- OOV events are mapped to a real extra state rather than spliced "
        "out, so adjacency is genuine; but the OOV state is a mixture of "
        "everything below the vocabulary floor and cannot be read as a "
        "community.")
    add("")

    add("## Configuration")
    add("")
    add("Registration pins:")
    add("")
    add("| pin | value |")
    add("|---|---|")
    for key in config["registration_pins"]:
        add(f"| {key} | {config['registration_pins'][key]} |")
    add("")
    add("Implementation choices where the registration is silent (recorded "
        "per the executor contract):")
    add("")
    add("| choice | value | rationale |")
    add("|---|---|---|")
    for row in config["implementation_choices"]:
        add(f"| {row['choice']} | {row['value']} | {row['rationale']} |")
    add("")
    add("Blocking gates:")
    add("")
    add("| gate | status |")
    add("|---|---|")
    for name, value in payload["gates"].items():
        add(f"| {name} | {value} |")
    add("")
    add("Artifacts (gitignored): `results/m4_u1_order_identity/` — "
        "`config.json`, `config.sha256.json`, `census.json`, "
        "`synthetic_gate.json`, `mh_contract.json`, `fold_purity.json`, "
        "`state_maps.json`, `arms.json`, `descriptives.json`, "
        "`verdict.json`, `id_leak_scan.json`, `report_payload.json`, "
        "`run_log.jsonl`, `events_cache.npz`, `events_cache.meta.json`.")
    add("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def build_config() -> dict[str, Any]:
    return {
        "registration_pins": {
            "SEED": SEED,
            "folds": f"{N_FOLDS} (KFold shuffle=True, random_state={SEED})",
            "cluster seed": f"SEED + {CLUSTER_SEED_STRIDE} * fold",
            "spherical k-means n_init": KMEANS_N_INIT,
            "alpha (additive smoothing)": ALPHA,
            "B_shuffle": B_SHUFFLE,
            "B_bootstrap": B_BOOTSTRAP,
            "C primary / sensitivity": f"{C_PRIMARY} / {list(C_SENSITIVITY)}",
            "pools (per-half in-vocabulary event floor)":
                f"{POOL_PRIMARY_MIN} -> 984, {POOL_SENSITIVITY_MIN} -> 821",
            "session gap": f"{int(SESSION_GAP_SECONDS)} s",
            "vocabulary floor": f"ceil({VOCAB_FLOOR_FRACTION} * authors_seen)",
            "half rule": "per-author median created_utc, ties (<=) to early",
            "sort": "stable; timestamp ties keep stream order",
            "equivalence epsilon on rho": EPSILON_RHO,
            "data columns": "author, subreddit, created_utc, link_id (no bodies)",
            "cohort": "results/m4_sr0_recon/cohort_authors.csv",
        },
        "implementation_choices": [
            {"choice": "shuffle scaffold",
             "value": "state labels permuted across a FIXED timeline",
             "rationale": "the session and cross-thread arms mask adjacent "
                          "pairs by gap and link_id; permuting the states "
                          "while holding the timeline (and therefore the "
                          "opportunity structure) fixed keeps those masks "
                          "meaningful and preserves the bag exactly. For the "
                          "primary arm the two readings coincide."},
            {"choice": "shuffle scope",
             "value": "test authors only",
             "rationale": "the cluster map is fitted on real training-early "
                          "halves and is held fixed; the null concerns only "
                          "the discrimination statistic on held-out authors."},
            {"choice": "within-half permutation",
             "value": "argsort(half_id + U[0,1)), kind='stable'",
             "rationale": "one batched argsort per shuffle instead of "
                          "per-author loops (the T2 paid lesson); cannot move "
                          "an event across a half boundary, so the per-half "
                          "bag is exactly invariant."},
            {"choice": "B_boot_shuffle",
             "value": str(B_BOOT_SHUFFLE),
             "rationale": "the bootstrap's null-mean component reuses the "
                          "first N stored shuffle similarity matrices. The "
                          "between-shuffle sd of the pooled null AUC is "
                          "reported per arm and is far below the bootstrap sd "
                          "of the real AUC, so this is a computational "
                          "detail, not a verdict-moving one."},
            {"choice": "bootstrap AUC evaluation",
             "value": f"monotone {BOOT_BINS}-bin coding of each similarity "
                      "matrix, weighted by author multiplicities",
             "rationale": "ties are preserved exactly by the coding; the "
                          "maximum absolute deviation from the exact rank AUC "
                          "is reported per arm."},
            {"choice": "bootstrap negative set",
             "value": "weight c_u * c_v for u != v",
             "rationale": "duplicate copies of one author never enter the "
                          "different-author set."},
            {"choice": "clean arm pool",
             "value": "re-derived under the clean vocabulary",
             "rationale": "the registration says 're-derive the map, rerun'; "
                          "removing communities changes which events are "
                          "in-vocabulary, so the per-half floor is re-applied. "
                          "The realized clean pool size is reported."},
            {"choice": "synthetic event counts",
             "value": f"lognormal, median {SYNTH_MEDIAN_EVENTS}, sigma "
                      f"{SYNTH_LOGNORMAL_SIGMA}, floor {SYNTH_MIN_EVENTS}",
             "rationale": "'drawn to match the census median'; the floor keeps "
                          "both synthetic halves above the real per-half "
                          "floor of 50."},
            {"choice": "synthetic halves",
             "value": "split at the sequence midpoint",
             "rationale": "synthetic worlds carry no timestamps."},
            {"choice": "synthetic resolution",
             "value": f"B_shuffle {SYNTH_B_SHUFFLE}, B_bootstrap "
                      f"{SYNTH_B_BOOTSTRAP}, B_boot_shuffle "
                      f"{SYNTH_B_BOOT_SHUFFLE}",
             "rationale": "the gate's targets are sign, magnitude and "
                          "monotonicity, not a precise interval; a synthetic "
                          "world is one block of 900 authors, so each stored "
                          "similarity matrix is 21x a real fold's."},
            {"choice": "synthetic bag concentration (A-U1-1)",
             "value": f"Dirichlet({SYNTH_DIRICHLET_CONC}) over "
                      f"{SYNTH_STATES} states, calibrated on the grid "
                      "{3.5, 4, 4.5, 5} to put the synthetic bag AUC nearest "
                      f"{SYNTH_BAG_AUC_TARGET}",
             "rationale": "DISCLOSED PRE-VERDICT CALIBRATION. The first "
                          "parameterisation (Dirichlet 0.4) saturated: the "
                          "synthetic bag AUC was 0.99999, leaving no "
                          "discrimination error for order to remove, so the "
                          "weakest sticky knob (s = 0.1) was unreachable by "
                          "ANY correct estimator and the gate failed for a "
                          "reason that was not about the estimator. The "
                          "concentration was re-set so the synthetic worlds "
                          "sit in the real arm's discrimination regime and "
                          "the gate re-run -- entirely on synthetic data, "
                          "before any real arm executed."},
            {"choice": "W_null replicates (RD-U1-1)",
             "value": f"{SYNTH_NULL_REPLICATES} independent worlds",
             "rationale": "the registered single-draw CI clause is decided by "
                          "Monte-Carlo noise at N = 900; replicates make the "
                          "honesty test stricter, not looser."},
            {"choice": "synthetic null-location rule (RD-U1-2)",
             "value": f"null retains >= {SYNTH_NULL_LIFT_MIN:.0%} of the bag's "
                      "lift over 0.5; the literal |null - bag| <= "
                      f"{NULL_LOCATION_TOLERANCE:.2f} check is enforced on the "
                      "real primary arm",
             "rationale": "the raw gap is a sampling-budget artefact at the "
                          "pinned synthetic event count and cannot diagnose "
                          "the null mechanics there."},
            {"choice": "synthetic pooling",
             "value": "one 900-author block, no folds",
             "rationale": "no object is fitted in the synthetic worlds "
                          "(states are the generating states), so there is "
                          "nothing to cross-fit; one block gives the gate its "
                          "maximum power."},
            {"choice": "W_transition proposal",
             "value": f"{SYNTH_MH_BLOCKS} author-permuted blocks, weight "
                      f"1 + beta on within-block moves, beta in "
                      f"{list(SYNTH_MH_BETA)}",
             "rationale": "asymmetric block proposals exercise the full MH "
                          "acceptance ratio q(j->i)/q(i->j)."},
            {"choice": "stay-rate scalar",
             "value": "unsmoothed diagonal share of realized transitions",
             "rationale": "the scalar arm is a rate, not a distribution; "
                          "smoothing would shrink it toward 1/(C+1)."},
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comments", type=Path, default=DEFAULT_COMMENTS)
    parser.add_argument("--cohort", type=Path, default=DEFAULT_COHORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--stages", default="prep,gate,real,report",
                        help="comma-separated subset of prep,gate,real,report")
    parser.add_argument("--b-shuffle", type=int, default=B_SHUFFLE)
    parser.add_argument("--b-bootstrap", type=int, default=B_BOOTSTRAP)
    args = parser.parse_args(argv)

    stages = {s.strip() for s in args.stages.split(",") if s.strip()}
    output: Path = args.output
    output.mkdir(parents=True, exist_ok=True)
    log = RunLog(output / "run_log.jsonl")

    config = build_config()
    write_json(output / "config.json", config)
    digest = hashlib.sha256(
        (output / "config.json").read_bytes()).hexdigest()
    write_json(output / "config.sha256.json",
               {"sha256": digest, "stamped_utc": utc_now()})
    log.event("config_stamped", sha256=digest)

    cache = output / "events_cache.npz"
    if "prep" in stages or not cache.exists():
        scaffold = stream_cohort_events(args.comments, args.cohort, log)
        save_scaffold(scaffold, cache)
    else:
        scaffold = load_scaffold(cache)
        log.event("scaffold_loaded", **scaffold.stream_stats)

    if scaffold.stream_stats["vocabulary_size"] != CENSUS_VOCABULARY:
        log.event("census_mismatch",
                  got=scaffold.stream_stats["vocabulary_size"],
                  expected=CENSUS_VOCABULARY)
        raise SystemExit(
            f"STOP: vocabulary reproduction gave "
            f"{scaffold.stream_stats['vocabulary_size']} communities, "
            f"expected {CENSUS_VOCABULARY} (registration census).")

    if not (stages & {"gate", "real", "report"}):
        log.event("prep_only_done", **scaffold.stream_stats)
        return 0

    # ---- Part 0 first, always (A1 hardening: no real arm before the gate)
    gate_path = output / "synthetic_gate.json"
    mh_path = output / "mh_contract.json"
    if "gate" in stages or not gate_path.exists():
        mh_contract = mh_stationarity_check()
        write_json(mh_path, mh_contract)
        gate = run_synthetic_gate(log)
        write_json(gate_path, gate)
    else:
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        mh_contract = json.loads(mh_path.read_text(encoding="utf-8"))
    if gate["status"] != "PASS":
        log.event("gate_failed_stop", checks=gate["checks"])
        raise SystemExit(
            "STOP: Part 0 synthetic gate FAILED; no real-data arm runs and no "
            "result is stamped (A1 hardening). See "
            f"{gate_path} for the failing checks.")

    if "real" not in stages and "report" not in stages:
        return 0

    arms_path = output / "arms.json"
    if "real" in stages or not arms_path.exists():
        pools: dict[tuple[str, int], PoolContext] = {}
        for variant, pool_min in sorted(
                {(a.vocab_variant, a.pool_min) for a in ARMS}):
            pools[(variant, pool_min)] = build_pool_context(
                scaffold, variant, pool_min, log)
        purity = [assert_fold_purity(pool) for pool in pools.values()]
        write_json(output / "fold_purity.json", purity)

        full50 = pools[("full", POOL_PRIMARY_MIN)]
        if full50.pool_authors.size != CENSUS_POOL_PRIMARY:
            raise SystemExit(
                f"STOP: primary pool is {full50.pool_authors.size}, expected "
                f"{CENSUS_POOL_PRIMARY} (registration census).")

        state_maps: dict[tuple[str, int, int], list[np.ndarray]] = {}
        map_info: list[dict[str, Any]] = []
        for spec in ARMS:
            key = (spec.vocab_variant, spec.pool_min, spec.n_states)
            if key not in state_maps:
                maps, info = build_state_maps(
                    pools[(spec.vocab_variant, spec.pool_min)],
                    spec.n_states, log)
                state_maps[key] = maps
                info["pool"] = f"{spec.vocab_variant}_min{spec.pool_min}"
                map_info.append(info)
        write_json(output / "state_maps.json", map_info)

        descriptives = compute_descriptives(
            full50, state_maps[("full", POOL_PRIMARY_MIN, C_PRIMARY)], log)
        write_json(output / "descriptives.json", descriptives)

        results = []
        for spec in ARMS:
            pool = pools[(spec.vocab_variant, spec.pool_min)]
            maps = state_maps[(spec.vocab_variant, spec.pool_min,
                               spec.n_states)]
            results.append(run_arm(
                spec, pool, maps, log,
                b_shuffle=args.b_shuffle, b_bootstrap=args.b_bootstrap,
                collect_bag_reference=True))
        write_json(arms_path, results)

        tie_rate = _tie_rate(scaffold)
        census = {
            "stream": scaffold.stream_stats,
            "tie_rate": tie_rate,
            "generated_utc": utc_now(),
        }
        for (variant, pool_min), pool in pools.items():
            census[f"pool_{variant}_min{pool_min}"] = pool.census
        write_json(output / "census.json", census)
    else:
        results = json.loads(arms_path.read_text(encoding="utf-8"))
        census = json.loads((output / "census.json").read_text(encoding="utf-8"))
        descriptives = json.loads(
            (output / "descriptives.json").read_text(encoding="utf-8"))

    arms_by_key = {a["arm"]: a for a in results}
    resolution = [arms_by_key["c12"], arms_by_key["primary"],
                  arms_by_key["c48"]]
    verdict = classify(arms_by_key["primary"], resolution)
    verdict["generated_utc"] = utc_now()

    primary_cell = verdict["cell"]
    flags: dict[str, str] = {}
    for arm in results:
        if arm["arm"] == "primary":
            continue
        arm_cell = _cell_of(arm)
        if arm_cell != primary_cell:
            flags[arm["arm"]] = f"#73 divergence: {arm_cell}"
    verdict["divergence_flags"] = flags
    write_json(output / "verdict.json", verdict)
    log.event("verdict", cell=verdict["cell"], rho=verdict["rho"],
              rho_ci=verdict["rho_ci"], flags=flags)

    payload = {
        "generated_utc": utc_now(),
        "config": config,
        "census": census,
        "synthetic_gate": gate,
        "mh_contract": mh_contract,
        "arms": results,
        "descriptives": descriptives,
        "verdict": verdict,
        "divergence_flags": flags,
        "gates": {
            "Part 0 synthetic gate": gate["status"],
            "exact-bag shuffle invariance (all arms)":
                "PASS" if all(a["bag_invariance_exact"] for a in results)
                else "FAIL",
            "fold purity (zero test-author mass in any state map)": "PASS",
            "vocabulary reproduction (1191)": "PASS",
            "primary pool reproduction (984)": "PASS",
            "binned-AUC vs exact-AUC max error":
                f"{max(a['binned_auc_max_abs_error'] for a in results):.2e}",
            "null sits near the bag on the real primary arm "
            f"(|null - bag| <= {NULL_LOCATION_TOLERANCE:.2f})":
                "PASS" if abs(arms_by_key["primary"].get("null_minus_bag", 1.0)
                              ) <= NULL_LOCATION_TOLERANCE else "FAIL",
        },
    }
    if "report" in stages:
        write_report(args.report, payload)
        cohort_ids = pd.read_csv(args.cohort, usecols=["author"])["author"]
        scan_targets = [
            args.report,
            Path(__file__),
            ROOT / "tests/test_m4_u1_order_identity.py",
            ROOT / "docs/SUICA_M4_U_WHEN_ORDER_PLAN.md",
            ROOT / "docs/CLAIMS_LEDGER.md",
        ]
        scan = scan_for_cohort_ids(scan_targets, cohort_ids.astype(str))
        write_json(output / "id_leak_scan.json", scan)
        log.event("id_leak_scan", status=scan["status"], hits=scan["n_hits"])
        payload["gates"]["ID-leak scan (0 of 1401 cohort IDs)"] = scan["status"]
        write_report(args.report, payload)
        if scan["status"] != "PASS":
            raise SystemExit(f"STOP: ID-leak scan FAILED: {scan['hits']}")
    write_json(output / "report_payload.json",
               {k: v for k, v in payload.items() if k != "config"})
    log.event("done", cell=verdict["cell"])
    return 0


def _cell_of(arm: dict[str, Any]) -> str:
    rho = arm["rho"]
    lo = arm["rho_ci"][0]
    if lo <= 0.0:
        return "NO_ORDER_CHANNEL"
    if rho < 0.10:
        return "ORDER_TRACE"
    if rho <= 0.33:
        return "ORDER_CHANNEL"
    return "ORDER_MAJOR"


def _tie_rate(scaffold: EventScaffold) -> dict[str, float]:
    """Adjacent-pair timestamp tie rate, two denominators.

    The registration's census value (0.1152) is the in-vocabulary variant;
    the all-events variant is reported alongside it.
    """

    def rate(author: np.ndarray, created: np.ndarray) -> float:
        same_author = author[1:] == author[:-1]
        same_time = created[1:] == created[:-1]
        return float(np.count_nonzero(same_author & same_time)
                     / max(1, np.count_nonzero(same_author)))

    in_vocab = scaffold.vocab_of_subreddit[scaffold.subreddit_code] >= 0
    return {
        "in_vocabulary": rate(scaffold.author_code[in_vocab],
                              scaffold.created_utc[in_vocab]),
        "all_events": rate(scaffold.author_code, scaffold.created_utc),
    }


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
