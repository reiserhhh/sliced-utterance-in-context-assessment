#!/usr/bin/env python3
"""SUICA M4-U2 -- the personal persistence curve (standing wave or moving one?).

Executes the registration committed at b864dc7 in
``docs/SUICA_M4_U_WHEN_ORDER_PLAN.md`` (section "U2 -- the personal
persistence curve (registered BEFORE run, 2026-08-18)").  Nothing here
re-derives a design decision; where the registration is silent on an
implementation detail the simplest deterministic option is taken and recorded
in ``results/m4_u2_persistence_curve/config.json`` (mirrored into the
report's configuration block).

The question.  U1 closed the fast-time question (order carries reproducible
author structure, rho 0.2893).  U2 asks the slow-time one: does the personal
selection signature HOLD over calendar years, or does it move?  Per author,
disjoint blocks of exactly K consecutive in-vocabulary events (so measurement
noise is constant by construction); per calendar-gap bin b,

    E(b) = mean cos(h_i, h_j | same author, gap in b)
         - mean cos(h_i, h_j | different authors, epoch-matched, gap in b)

with the cross term matched to the self pairs' joint (quarter_i, quarter_j)
histogram, so global platform drift is absorbed and E is PERSONAL persistence
in excess of shared-epoch similarity.  Primary contrasts: existence
E(0-90d) > 0 and decay D = E(0-90d) - E(2-3y).  The verdict endpoint is 2-3y
(convention #74); 3y+ is descriptive only.

Own null (#68/#66): B permutations reassigning block->author labels WITHIN
each calendar quarter -- epoch structure preserved exactly, identity
destroyed.  E's expected null location is 0 BY CONSTRUCTION of the contrast
(under a within-quarter relabelling the same-author pair set is a random
subset of the cell's pair set, so self and epoch-matched cross means share an
expectation); the realized null center is reported as the honesty check.

No synthetic gate is registered for this leg: the estimator is a binned mean
contrast with a permutation null, not a fitted discriminator, so defect #76's
operating-point convention does not bind (no world is simulated).  The
honesty checks are the permutation-null center, the census reproduction gate,
the cache anchor gate, the cross-sampler equivalence check, and the contract
tests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Configuration constants (registration pins first, then recorded choices).
# ---------------------------------------------------------------------------

SEED = 20260818                     # registration pin
B_PERM = 499                        # registration pin
B_BOOT = 1000                       # registration pin
K_PRIMARY = 50                      # registration pin: exact-K blocks
K_SENSITIVITY = 100                 # registration pin: block-size arm
POOL_MIN_BLOCKS = 4                 # registration pin: primary pool rule
QUARTER_DAYS = 91.3                 # registration pin: epoch cell width
CROSS_PER_SELF = 20                 # registration pin: sampler rate
EQUIVALENCE_FRACTION = 0.2          # registration pin: FIXED_POINT band
FLOOR_SHARE_LEAN = (0.6, 0.9)       # registration pin: primary lean
TAU_CAP_DAYS = 3650.0               # registration pin: 10 y cap

# Gap bins.  Left-closed / right-open on days; the last bin is descriptive.
BIN_EDGES_DAYS: tuple[float, ...] = (0.0, 90.0, 180.0, 365.0, 730.0, 1095.0)
BIN_LABELS: tuple[str, ...] = (
    "0-90d", "90-180d", "180-365d", "1-2y", "2-3y", "3y+")
N_BINS = len(BIN_LABELS)
VERDICT_BINS = 5                    # registration pin: 3y+ never a verdict bin
NEAR_BIN = 0                        # E(0-90d)
FAR_BIN = 4                         # E(2-3y): registered verdict endpoint
DESCRIPTIVE_BIN = 5                 # E(3y+): descriptive only

# Recorded implementation choices (registration silent).
TERCILE_QUANTILES = (1.0 / 3.0, 2.0 / 3.0)   # on per-author block counts
TERCILE_ASSIGN = "x <= lo | lo < x <= hi | x > hi"
EPOCH_ORIGIN = "corpus minimum created_utc over all cached cohort events"
FIT_GRID_POINTS = 1500              # log grid for tau in the refinement fit
FIT_ABSCISSA = "mean self-pair gap within the bin (days), from artifacts"
BIN_CHUNK_ELEMENTS = 2_000_000      # row-chunk size for the gap/bin matrices

# Cache anchors: BLOCKING gate before any computation (registration).
ANCHOR_EVENTS = 3_005_360
ANCHOR_AUTHORS = 1401
ANCHOR_VOCAB = 1191

# Census pins from the registration; a mismatch STOPS the leg.
CENSUS_PINS: dict[str, Any] = {
    "authors_ge_4_blocks": 849,
    "authors_ge_2_blocks": 1028,
    "authors_ge_8_blocks": 690,
    "total_blocks_all_authors": 46_318,
    "n_quarters": 18,
    "self_pairs_per_bin": [1_005_742, 783_654, 1_198_561,
                           1_248_992, 417_963, 100_150],
    "authors_2_3y": 564,
    "authors_3y_plus": 332,
    "tercile_sizes": [302, 265, 282],
    "tercile_edges_vocab_events": [650, 2050],
}

DEFAULT_CACHE = ROOT / "results/m4_u1_order_identity/events_cache.npz"
DEFAULT_OUTPUT = ROOT / "results/m4_u2_persistence_curve"
DEFAULT_REPORT = (
    ROOT / "reports/SUICA_M4_U2_PERSISTENCE_CURVE_REPORT.md")

# ---------------------------------------------------------------------------
# Governance echo: the explicit-typology community matcher.
#
# Provenance: reproduced verbatim from
# ``scripts/run_suica_m4_t1_hierarchical_selection_identity.py`` lines 37-69
# (the T1 clean_no_explicit_personality arm), as U1 did.  The removal set is
# RE-DERIVED here from this cohort's vocabulary, never read from an artifact.
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


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=float) + "\n",
        encoding="utf-8",
    )


class RunLog:
    """Append-only JSONL event log (T-line / U1 artifact convention)."""

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
            handle.write(
                json.dumps(record, sort_keys=True, default=float) + "\n")
        print(f"[{record['elapsed_s']:9.1f}s] {name} "
              f"{json.dumps(payload, sort_keys=True, default=float)[:220]}",
              flush=True)


def _is_id_char(char: str) -> bool:
    return char.isalnum() or char in {"_", "-"}


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
                    hits.append({"path": str(path),
                                 "line": text.count("\n", 0, index) + 1})
                    break
                start = index + 1
    return {"status": "PASS" if not hits else "FAIL",
            "files_scanned": scanned,
            "candidates_checked": len(candidates),
            "min_length": min_length,
            "n_hits": len(hits),
            "hits": hits}


# ---------------------------------------------------------------------------
# Cache + anchor gate
# ---------------------------------------------------------------------------


@dataclass
class EventCache:
    author_code: np.ndarray
    subreddit_code: np.ndarray
    created_utc: np.ndarray
    vocab_of_subreddit: np.ndarray
    authors: list[str]
    subreddits: list[str]
    vocabulary: list[str]
    stream_stats: dict[str, Any]


def load_event_cache(path: Path) -> EventCache:
    payload = np.load(path)
    meta = json.loads(
        path.with_suffix(".meta.json").read_text(encoding="utf-8"))
    return EventCache(
        author_code=payload["author_code"],
        subreddit_code=payload["subreddit_code"],
        created_utc=payload["created_utc"],
        vocab_of_subreddit=payload["vocab_of_subreddit"],
        authors=meta["authors"],
        subreddits=meta["subreddits"],
        vocabulary=meta["vocabulary"],
        stream_stats=meta["stream_stats"],
    )


def verify_cache_anchors(cache: EventCache) -> dict[str, Any]:
    """BLOCKING gate: the U1 cache must be the object the registration pins."""

    observed = {
        "events": int(cache.author_code.size),
        "authors": int(np.unique(cache.author_code).size),
        "vocabulary": int(cache.vocab_of_subreddit.max()) + 1,
    }
    expected = {"events": ANCHOR_EVENTS, "authors": ANCHOR_AUTHORS,
                "vocabulary": ANCHOR_VOCAB}
    mismatches = {k: [expected[k], observed[k]]
                  for k in expected if expected[k] != observed[k]}
    return {"status": "PASS" if not mismatches else "FAIL",
            "expected": expected, "observed": observed,
            "mismatches": mismatches,
            "vocabulary_list_length": len(cache.vocabulary),
            "authors_list_length": len(cache.authors)}


# ---------------------------------------------------------------------------
# Blocks
# ---------------------------------------------------------------------------


@dataclass
class Blocks:
    """Exact-K disjoint blocks over in-vocabulary events, per author."""

    author: np.ndarray        # int32 global author code, one per block
    midpoint: np.ndarray      # float64 seconds
    features: np.ndarray      # float32 (n_blocks, n_vocab), L2-normalized
    k: int
    n_vocab: int
    vocab_events_per_author: np.ndarray   # int64, length n_authors_total
    blocks_per_author: np.ndarray         # int64, length n_authors_total


def build_blocks(author_code: np.ndarray, created_utc: np.ndarray,
                 vocab_index: np.ndarray, n_vocab: int, k: int,
                 n_authors: int | None = None) -> Blocks:
    """Disjoint consecutive K-event blocks over in-vocabulary events.

    ``author_code`` must be sorted by (author, created_utc) with ties in
    stream order -- the U1 cache pin.  OOV events (``vocab_index < 0``) are
    dropped BEFORE blocking; the trailing remainder of each author is dropped;
    the block midpoint is the mean of its first and last event timestamps;
    features are sqrt(count / K) over the vocabulary, L2-normalized (the
    T-line's Hellinger identity metric).
    """

    if k <= 0:
        raise ValueError("k must be positive")
    keep = vocab_index >= 0
    a = np.asarray(author_code)[keep]
    t = np.asarray(created_utc)[keep]
    v = np.asarray(vocab_index)[keep]
    total_authors = int(n_authors if n_authors is not None
                        else (int(a.max()) + 1 if a.size else 0))
    counts = np.bincount(a, minlength=total_authors).astype(np.int64)
    n_blocks_per_author = counts // k
    starts = np.concatenate(([0], np.cumsum(counts)))

    n_blocks = int(n_blocks_per_author.sum())
    block_author = np.empty(n_blocks, dtype=np.int32)
    block_mid = np.empty(n_blocks, dtype=np.float64)
    rows = np.empty(n_blocks * k, dtype=np.int64)
    cursor = 0
    for author in np.flatnonzero(n_blocks_per_author):
        n = int(n_blocks_per_author[author])
        s = int(starts[author])
        idx = np.arange(s, s + n * k, dtype=np.int64)
        rows[cursor * k:(cursor + n) * k] = idx
        tt = t[s:s + n * k].reshape(n, k)
        block_mid[cursor:cursor + n] = 0.5 * (tt[:, 0] + tt[:, -1])
        block_author[cursor:cursor + n] = author
        cursor += n
    assert cursor == n_blocks

    features = np.zeros((n_blocks, n_vocab), dtype=np.float32)
    if n_blocks:
        block_of_row = np.repeat(np.arange(n_blocks, dtype=np.int64), k)
        flat = block_of_row * n_vocab + v[rows].astype(np.int64)
        counts_flat = np.bincount(flat, minlength=n_blocks * n_vocab)
        features = np.sqrt(
            counts_flat.reshape(n_blocks, n_vocab).astype(np.float32) / k)
        norms = np.linalg.norm(features, axis=1, keepdims=True)
        norms[norms == 0.0] = 1.0
        features /= norms

    return Blocks(author=block_author, midpoint=block_mid, features=features,
                  k=k, n_vocab=n_vocab, vocab_events_per_author=counts,
                  blocks_per_author=n_blocks_per_author)


def assign_quarters(midpoint: np.ndarray, origin: float,
                    quarter_days: float = QUARTER_DAYS) -> np.ndarray:
    return np.floor(
        (midpoint - origin) / (quarter_days * 86400.0)).astype(np.int32)


def gap_bin(gap_days: np.ndarray) -> np.ndarray:
    """Bin index 0..5 for a gap in days (left-closed, right-open)."""

    out = np.zeros(np.shape(gap_days), dtype=np.uint8)
    for edge in BIN_EDGES_DAYS[1:]:
        out += (np.asarray(gap_days) >= edge)
    return out


# ---------------------------------------------------------------------------
# Permutation scaffold (within-quarter block -> author relabelling)
# ---------------------------------------------------------------------------


@dataclass
class QuarterPlan:
    """Per-quarter slot structure shared by every permutation.

    A within-quarter relabelling preserves each author's per-quarter block
    count EXACTLY, so the "slot -> author" map is a permutation invariant and
    only the "slot -> block position" map moves.  Row 0 of ``slot_position``
    is the identity (the real assignment).
    """

    rows: np.ndarray            # local -> arm block index
    slot_author: np.ndarray     # slot -> author (sorted, invariant)
    slot_position: np.ndarray   # (n_perm + 1, size) slot -> local position


def build_quarter_plans(block_quarter: np.ndarray, block_author: np.ndarray,
                        n_perm: int, seed: int) -> dict[int, QuarterPlan]:
    plans: dict[int, QuarterPlan] = {}
    rng = np.random.default_rng(seed)
    for q in np.unique(block_quarter):
        rows = np.flatnonzero(block_quarter == q)
        authors = block_author[rows]
        identity = np.argsort(authors, kind="stable").astype(np.int32)
        size = rows.size
        slot_position = np.empty((n_perm + 1, size), dtype=np.int32)
        slot_position[0] = identity
        for p in range(1, n_perm + 1):
            slot_position[p] = rng.permutation(size).astype(np.int32)
        plans[int(q)] = QuarterPlan(rows=rows,
                                    slot_author=authors[identity],
                                    slot_position=slot_position)
    return plans


def _same_author_slot_pairs(slot_author_a: np.ndarray,
                            slot_author_b: np.ndarray,
                            same_quarter: bool) -> tuple[np.ndarray,
                                                         np.ndarray]:
    """Slot-index pairs sharing an author; invariant across permutations."""

    ua, ca = np.unique(slot_author_a, return_counts=True)
    ub, cb = np.unique(slot_author_b, return_counts=True)
    common, ia, ib = np.intersect1d(ua, ub, assume_unique=True,
                                    return_indices=True)
    if common.size == 0:
        empty = np.empty(0, dtype=np.int64)
        return empty, empty
    na = ca[ia].astype(np.int64)
    nb = cb[ib].astype(np.int64)
    sa = (np.concatenate(([0], np.cumsum(ca)))[ia]).astype(np.int64)
    sb = (np.concatenate(([0], np.cumsum(cb)))[ib]).astype(np.int64)
    counts = na * nb
    total = int(counts.sum())
    if total == 0:
        empty = np.empty(0, dtype=np.int64)
        return empty, empty
    group = np.repeat(np.arange(common.size), counts)
    offset = np.arange(total) - np.repeat(np.cumsum(counts) - counts, counts)
    ai = offset // nb[group]
    bi = offset % nb[group]
    slot_a = sa[group] + ai
    slot_b = sb[group] + bi
    if same_quarter:
        keep = ai < bi
        slot_a = slot_a[keep]
        slot_b = slot_b[keep]
    return slot_a, slot_b


# ---------------------------------------------------------------------------
# The arm estimator
# ---------------------------------------------------------------------------


def _bin_matrix(mid_a_days: np.ndarray, mid_b_days: np.ndarray) -> np.ndarray:
    a = mid_a_days.size
    b = mid_b_days.size
    out = np.empty((a, b), dtype=np.uint8)
    step = max(1, int(BIN_CHUNK_ELEMENTS // max(1, b)))
    for start in range(0, a, step):
        stop = min(a, start + step)
        gap = np.abs(mid_a_days[start:stop, None] - mid_b_days[None, :])
        acc = np.zeros(gap.shape, dtype=np.uint8)
        for edge in BIN_EDGES_DAYS[1:]:
            acc += (gap >= edge)
        out[start:stop] = acc
    return out


def _bin_sums(gram: np.ndarray, bins: np.ndarray) -> np.ndarray:
    out = np.zeros(N_BINS, dtype=np.float64)
    a, b = gram.shape
    step = max(1, int(BIN_CHUNK_ELEMENTS // max(1, b)))
    for start in range(0, a, step):
        stop = min(a, start + step)
        out += np.bincount(bins[start:stop].ravel(),
                           weights=gram[start:stop].ravel().astype(np.float64),
                           minlength=N_BINS)
    return out


def _bin_counts(bins: np.ndarray) -> np.ndarray:
    out = np.zeros(N_BINS, dtype=np.int64)
    a, b = bins.shape
    step = max(1, int(BIN_CHUNK_ELEMENTS // max(1, b)))
    for start in range(0, a, step):
        stop = min(a, start + step)
        out += np.bincount(bins[start:stop].ravel(),
                           minlength=N_BINS).astype(np.int64)
    return out


def compute_arm(features: np.ndarray, block_author: np.ndarray,
                block_quarter: np.ndarray, block_mid_days: np.ndarray,
                *, n_perm: int, n_boot: int, seed: int,
                cross_sampler_check: bool = False,
                log: RunLog | None = None,
                label: str = "arm") -> dict[str, Any]:
    """Epoch-matched personal-excess curve with its own within-quarter null.

    Everything is a gather over per-cell grams.  A "cell" is an unordered
    quarter pair; the epoch match is exact (the cross mean of a cell is taken
    over ALL its different-author pairs), weighted by the self-pair histogram
    -- the zero-variance limit of the registered "up to 20 cross pairs per
    self pair per cell" sampler, whose agreement is verified separately.
    """

    n_blocks = int(features.shape[0])
    authors_present = np.unique(block_author)
    n_authors = authors_present.size
    author_slot = np.searchsorted(authors_present, block_author)
    quarters = np.unique(block_quarter)
    n_quarters = quarters.size
    quarter_slot = {int(q): i for i, q in enumerate(quarters)}

    cells: list[tuple[int, int]] = [(int(qa), int(qb))
                                    for i, qa in enumerate(quarters)
                                    for qb in quarters[i:]]
    cell_index = {c: i for i, c in enumerate(cells)}
    n_cells = len(cells)

    plans = build_quarter_plans(block_quarter, block_author, n_perm, seed)

    all_counts = np.zeros((n_cells, N_BINS), dtype=np.float64)
    all_sums = np.zeros((n_cells, N_BINS), dtype=np.float64)
    perm_counts = np.zeros((n_perm + 1, n_cells, N_BINS), dtype=np.float64)
    perm_sums = np.zeros((n_perm + 1, n_cells, N_BINS), dtype=np.float64)
    author_counts = np.zeros((n_authors, n_cells, N_BINS), dtype=np.float64)
    author_sums = np.zeros((n_authors, n_cells, N_BINS), dtype=np.float64)
    self_gap_sums = np.zeros(N_BINS, dtype=np.float64)
    sampler_sums = np.zeros((n_cells, N_BINS), dtype=np.float64)
    sampler_counts = np.zeros((n_cells, N_BINS), dtype=np.float64)
    cross_candidate_ratio: list[float] = []
    cross_candidate_ratio_cell: list[float] = []
    sampler_requested = np.zeros(1, dtype=np.float64)

    sampler_rng = np.random.default_rng(seed + 7)
    t_start = time.time()

    for cell_id, (qa, qb) in enumerate(cells):
        plan_a = plans[qa]
        plan_b = plans[qb]
        rows_a = plan_a.rows
        rows_b = plan_b.rows
        size_a = rows_a.size
        size_b = rows_b.size
        if size_a == 0 or size_b == 0:
            continue
        same_quarter = qa == qb

        mid_a = block_mid_days[rows_a]
        mid_b = block_mid_days[rows_b]
        gram = features[rows_a] @ features[rows_b].T

        if same_quarter:
            gmin, gmax = 0.0, float(mid_a.max() - mid_a.min())
        else:
            gmin = float(mid_b.min() - mid_a.max())
            gmax = float(mid_b.max() - mid_a.min())
        bin_lo = int(gap_bin(np.array([max(gmin, 0.0)]))[0])
        bin_hi = int(gap_bin(np.array([max(gmax, 0.0)]))[0])
        single_bin = bin_lo == bin_hi
        bins = None if single_bin else _bin_matrix(mid_a, mid_b)

        # ---- all-pairs totals for the cell (the cross reservoir) ----
        if single_bin:
            counts_cell = np.zeros(N_BINS, dtype=np.float64)
            sums_cell = np.zeros(N_BINS, dtype=np.float64)
            counts_cell[bin_lo] = float(size_a) * float(size_b)
            sums_cell[bin_lo] = float(gram.sum(dtype=np.float64))
        else:
            counts_cell = _bin_counts(bins).astype(np.float64)
            sums_cell = _bin_sums(gram, bins)
        if same_quarter:
            counts_cell[0] -= float(size_a)          # the zero-gap diagonal
            sums_cell[0] -= float(np.trace(gram, dtype=np.float64))
            counts_cell *= 0.5
            sums_cell *= 0.5
        all_counts[cell_id] = counts_cell
        all_sums[cell_id] = sums_cell

        # ---- same-author slot pairs: invariant across permutations ----
        slot_a, slot_b = _same_author_slot_pairs(
            plan_a.slot_author, plan_b.slot_author, same_quarter)
        if slot_a.size == 0:
            continue
        gram_flat = gram.ravel()
        bins_flat = None if single_bin else bins.ravel()

        for p in range(n_perm + 1):
            pos_a = plan_a.slot_position[p][slot_a].astype(np.int64)
            pos_b = plan_b.slot_position[p][slot_b].astype(np.int64)
            flat = pos_a * size_b + pos_b
            values = gram_flat[flat]
            if single_bin:
                perm_counts[p, cell_id, bin_lo] += float(values.size)
                perm_sums[p, cell_id, bin_lo] += float(
                    values.sum(dtype=np.float64))
                pair_bins = None
            else:
                pair_bins = bins_flat[flat]
                perm_counts[p, cell_id] += np.bincount(
                    pair_bins, minlength=N_BINS).astype(np.float64)
                perm_sums[p, cell_id] += np.bincount(
                    pair_bins, weights=values.astype(np.float64),
                    minlength=N_BINS)
            if p == 0:
                who = author_slot[rows_a[pos_a]]
                if pair_bins is None:
                    pair_bins = np.full(values.size, bin_lo, dtype=np.uint8)
                key = who.astype(np.int64) * N_BINS + pair_bins
                author_counts[:, cell_id, :] += np.bincount(
                    key, minlength=n_authors * N_BINS
                ).reshape(n_authors, N_BINS).astype(np.float64)
                author_sums[:, cell_id, :] += np.bincount(
                    key, weights=values.astype(np.float64),
                    minlength=n_authors * N_BINS).reshape(n_authors, N_BINS)
                gaps = np.abs(mid_a[pos_a] - mid_b[pos_b])
                self_gap_sums += np.bincount(
                    pair_bins, weights=gaps.astype(np.float64),
                    minlength=N_BINS)
                # epoch-matching feasibility, per the census note; recorded at
                # both resolutions because the registration's 115.4x figure
                # does not name its denominator.
                cell_self = 0.0
                cell_avail = 0.0
                for b in range(N_BINS):
                    n_self = float(np.count_nonzero(pair_bins == b))
                    if n_self <= 0:
                        continue
                    avail = counts_cell[b] - n_self
                    cross_candidate_ratio.append(avail / n_self)
                    cell_self += n_self
                    cell_avail += avail
                if cell_self > 0:
                    cross_candidate_ratio_cell.append(cell_avail / cell_self)
                if cross_sampler_check:
                    self_hist = np.bincount(
                        pair_bins, minlength=N_BINS).astype(np.int64)
                    sampler_requested[0] += float(
                        self_hist.sum() * CROSS_PER_SELF)
                    _sample_cross(
                        gram, bins, bin_lo, rows_a, rows_b, author_slot,
                        self_hist, sampler_rng, sampler_counts[cell_id],
                        sampler_sums[cell_id], same_quarter)

        del gram, bins, gram_flat
        if log is not None and (cell_id % 40 == 0 or cell_id == n_cells - 1):
            log.event("arm_cell_progress", arm=label, cell=cell_id + 1,
                      of=n_cells, elapsed_s=round(time.time() - t_start, 1))

    return _finalize_arm(
        label=label, n_blocks=n_blocks, n_authors=n_authors,
        n_quarters=n_quarters, n_cells=n_cells, n_perm=n_perm,
        n_boot=n_boot, seed=seed, all_counts=all_counts, all_sums=all_sums,
        perm_counts=perm_counts, perm_sums=perm_sums,
        author_counts=author_counts, author_sums=author_sums,
        self_gap_sums=self_gap_sums,
        cross_candidate_ratio=np.asarray(cross_candidate_ratio),
        cross_candidate_ratio_cell=np.asarray(cross_candidate_ratio_cell),
        sampler_counts=sampler_counts, sampler_sums=sampler_sums,
        sampler_requested=float(sampler_requested[0]),
        cross_sampler_check=cross_sampler_check)


def _sample_cross(gram: np.ndarray, bins: np.ndarray | None, bin_lo: int,
                  rows_a: np.ndarray, rows_b: np.ndarray,
                  author_slot: np.ndarray, self_hist: np.ndarray,
                  rng: np.random.Generator, out_counts: np.ndarray,
                  out_sums: np.ndarray, same_quarter: bool) -> None:
    """The REGISTERED cross sampler, run only as an equivalence check.

    Draws ``CROSS_PER_SELF`` different-author pairs per self pair per (cell,
    bin) by rejection, so its expectation is the cell's exact cross mean.
    """

    size_a, size_b = gram.shape
    who_a = author_slot[rows_a]
    who_b = author_slot[rows_b]
    for b in range(N_BINS):
        need = int(self_hist[b]) * CROSS_PER_SELF
        if need <= 0:
            continue
        got = 0
        attempts = 0
        while got < need and attempts < 40:
            attempts += 1
            draw = min(4 * (need - got) + 64, 4_000_000)
            ia = rng.integers(0, size_a, size=draw)
            ib = rng.integers(0, size_b, size=draw)
            keep = who_a[ia] != who_b[ib]
            if same_quarter:
                keep &= ia != ib
            if bins is not None:
                keep &= bins[ia, ib] == b
            elif b != bin_lo:
                keep &= False
            ia = ia[keep][:need - got]
            ib = ib[keep][:need - got]
            if ia.size == 0:
                continue
            out_counts[b] += float(ia.size)
            out_sums[b] += float(gram[ia, ib].sum(dtype=np.float64))
            got += int(ia.size)


def _curve_from_stats(self_counts: np.ndarray, self_sums: np.ndarray,
                      cross_mean: np.ndarray,
                      valid: np.ndarray) -> np.ndarray:
    """E(b) = sum_c w_cb * (selfmean_cb - crossmean_cb), w from the self hist.

    ``self_counts`` / ``self_sums`` may carry a leading batch axis.
    """

    counts = np.where(valid, self_counts, 0.0)
    sums = np.where(valid, self_sums, 0.0)
    weight_total = counts.sum(axis=-2)
    self_total = sums.sum(axis=-2)
    cross_total = (counts * np.where(valid, cross_mean, 0.0)).sum(axis=-2)
    with np.errstate(invalid="ignore", divide="ignore"):
        out = (self_total - cross_total) / weight_total
    return np.where(weight_total > 0, out, np.nan)


def _finalize_arm(*, label: str, n_blocks: int, n_authors: int,
                  n_quarters: int, n_cells: int, n_perm: int, n_boot: int,
                  seed: int, all_counts: np.ndarray, all_sums: np.ndarray,
                  perm_counts: np.ndarray, perm_sums: np.ndarray,
                  author_counts: np.ndarray, author_sums: np.ndarray,
                  self_gap_sums: np.ndarray,
                  cross_candidate_ratio: np.ndarray,
                  cross_candidate_ratio_cell: np.ndarray,
                  sampler_counts: np.ndarray, sampler_sums: np.ndarray,
                  sampler_requested: float,
                  cross_sampler_check: bool) -> dict[str, Any]:
    real_counts = perm_counts[0]
    real_sums = perm_sums[0]

    cross_counts = all_counts - real_counts
    valid = (real_counts > 0) & (cross_counts > 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        cross_mean = (all_sums - real_sums) / cross_counts
    cross_mean = np.where(valid, cross_mean, 0.0)

    curve = _curve_from_stats(real_counts, real_sums, cross_mean, valid)
    self_pairs = real_counts.sum(axis=0)
    dropped = np.where(valid, 0.0, real_counts).sum(axis=0)
    used = self_pairs - dropped
    denom = np.where(used > 0, used, 1.0)
    self_mean = np.where(
        used > 0, np.where(valid, real_sums, 0.0).sum(axis=0) / denom, np.nan)
    matched_cross_mean = np.where(
        used > 0,
        (np.where(valid, real_counts, 0.0) * cross_mean).sum(axis=0) / denom,
        np.nan)
    mean_gap = np.divide(self_gap_sums,
                         np.where(self_pairs > 0, self_pairs, 1.0))

    # ---- permutation null: same estimator, relabelled identity ----
    perm_cross_counts = all_counts[None, :, :] - perm_counts
    perm_valid = (perm_counts > 0) & (perm_cross_counts > 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        perm_cross_mean = (all_sums[None, :, :] - perm_sums) / (
            perm_cross_counts)
    perm_cross_mean = np.where(perm_valid, perm_cross_mean, 0.0)
    perm_curve = _curve_from_stats(perm_counts, perm_sums, perm_cross_mean,
                                   perm_valid)
    null_curve = perm_curve[1:]
    null_d = null_curve[:, NEAR_BIN] - null_curve[:, FAR_BIN]
    real_d = float(curve[NEAR_BIN] - curve[FAR_BIN])

    # ---- cluster bootstrap over authors ----
    agg_self_sums = np.where(valid, author_sums, 0.0).sum(axis=1)
    agg_self_counts = np.where(valid, author_counts, 0.0).sum(axis=1)
    agg_cross = (np.where(valid, author_counts, 0.0) *
                 cross_mean[None, :, :]).sum(axis=1)
    boot_rng = np.random.default_rng(seed + 11)
    mult = boot_rng.multinomial(
        n_authors, np.full(n_authors, 1.0 / n_authors),
        size=n_boot).astype(np.float64)
    boot_num = mult @ (agg_self_sums - agg_cross)
    boot_den = mult @ agg_self_counts
    with np.errstate(invalid="ignore", divide="ignore"):
        boot_curve = np.where(boot_den > 0, boot_num / boot_den, np.nan)
    boot_d = boot_curve[:, NEAR_BIN] - boot_curve[:, FAR_BIN]
    with np.errstate(invalid="ignore", divide="ignore"):
        boot_floor = boot_curve[:, FAR_BIN] / boot_curve[:, NEAR_BIN]

    def ci(values: np.ndarray) -> list[float]:
        finite = values[np.isfinite(values)]
        if finite.size == 0:
            return [float("nan"), float("nan")]
        return [float(np.percentile(finite, 2.5)),
                float(np.percentile(finite, 97.5))]

    def band(values: np.ndarray) -> list[float]:
        return ci(values)

    floor_share = (float(curve[FAR_BIN] / curve[NEAR_BIN])
                   if curve[NEAR_BIN] != 0 else float("nan"))
    perm_p_near = float((np.count_nonzero(
        null_curve[:, NEAR_BIN] >= curve[NEAR_BIN]) + 1) / (n_perm + 1))
    perm_p_d = float((np.count_nonzero(null_d >= real_d) + 1) / (n_perm + 1))

    sampler = None
    if cross_sampler_check:
        with np.errstate(invalid="ignore", divide="ignore"):
            sampled_mean = np.where(sampler_counts > 0,
                                    sampler_sums / np.where(
                                        sampler_counts > 0, sampler_counts,
                                        1.0), 0.0)
        sampler_valid = valid & (sampler_counts > 0)
        sampled_curve = _curve_from_stats(real_counts, real_sums,
                                          sampled_mean, sampler_valid)
        sampler = {
            "sampled_curve": [float(x) for x in sampled_curve],
            "exact_curve": [float(x) for x in curve],
            "abs_difference": [float(abs(a - b)) for a, b
                               in zip(sampled_curve, curve)],
            "max_abs_difference": float(np.nanmax(np.abs(
                np.asarray(sampled_curve) - curve))),
            "cross_pairs_drawn": float(sampler_counts.sum()),
            "cross_pairs_requested": float(sampler_requested),
            "shortfall_fraction": float(
                1.0 - sampler_counts.sum() / max(1.0, sampler_requested)),
            "rate_per_self_pair": CROSS_PER_SELF,
        }

    return {
        "label": label,
        "n_blocks": int(n_blocks),
        "n_authors": int(n_authors),
        "n_quarters": int(n_quarters),
        "n_cells": int(n_cells),
        "b_perm": int(n_perm),
        "b_boot": int(n_boot),
        "bin_labels": list(BIN_LABELS),
        "self_pairs": [int(round(x)) for x in self_pairs],
        "cross_pairs_available": [int(round(x)) for x in
                                  (all_counts - real_counts).sum(axis=0)],
        "self_pairs_dropped_no_cross": [int(round(x)) for x in dropped],
        "self_mean": [float(x) for x in self_mean],
        "cross_mean_matched": [float(x) for x in matched_cross_mean],
        "mean_gap_days": [float(x) for x in mean_gap],
        "curve": [float(x) for x in curve],
        "curve_ci": [ci(boot_curve[:, b]) for b in range(N_BINS)],
        "curve_null_band": [band(null_curve[:, b]) for b in range(N_BINS)],
        "curve_null_center": [float(np.nanmedian(null_curve[:, b]))
                              for b in range(N_BINS)],
        "curve_null_mean": [float(np.nanmean(null_curve[:, b]))
                            for b in range(N_BINS)],
        "d": real_d,
        "d_ci": ci(boot_d),
        "d_null_band": band(null_d),
        "d_null_center": float(np.nanmedian(null_d)),
        "d_null_mean": float(np.nanmean(null_d)),
        "floor_share": floor_share,
        "floor_share_ci": ci(boot_floor),
        "perm_p_existence": perm_p_near,
        "perm_p_decay": perm_p_d,
        "equivalence_margin": float(EQUIVALENCE_FRACTION * curve[NEAR_BIN]),
        "d_ci_half_width": float(0.5 * (ci(boot_d)[1] - ci(boot_d)[0])),
        "cross_candidate_ratio_min": (
            float(cross_candidate_ratio.min())
            if cross_candidate_ratio.size else float("nan")),
        "cross_candidate_ratio_median": (
            float(np.median(cross_candidate_ratio))
            if cross_candidate_ratio.size else float("nan")),
        "cross_candidate_ratio_min_cell": (
            float(cross_candidate_ratio_cell.min())
            if cross_candidate_ratio_cell.size else float("nan")),
        "boot_curve": boot_curve,
        "null_curve": null_curve,
        "cross_sampler_check": sampler,
    }


# ---------------------------------------------------------------------------
# Refinement fit (never verdict-carrying)
# ---------------------------------------------------------------------------


def exponential_fit(x_days: np.ndarray, y: np.ndarray,
                    tau_cap: float = TAU_CAP_DAYS,
                    grid_points: int = FIT_GRID_POINTS) -> dict[str, Any]:
    """Least-squares fit of y = E_inf + A * exp(-x / tau), tau capped."""

    x = np.asarray(x_days, dtype=np.float64)
    y_arr = np.asarray(y, dtype=np.float64)
    batched = y_arr.ndim == 2
    y_mat = y_arr if batched else y_arr[None, :]
    taus = np.geomspace(1.0, tau_cap, grid_points)
    best_sse = np.full(y_mat.shape[0], np.inf)
    best = np.zeros((y_mat.shape[0], 3))
    n = x.size
    for tau in taus:
        e = np.exp(-x / tau)
        s_e = e.sum()
        s_ee = float(e @ e)
        det = n * s_ee - s_e * s_e
        if abs(det) < 1e-15:
            continue
        s_y = y_mat.sum(axis=1)
        s_ey = y_mat @ e
        c0 = (s_ee * s_y - s_e * s_ey) / det
        c1 = (n * s_ey - s_e * s_y) / det
        resid = y_mat - (c0[:, None] + c1[:, None] * e[None, :])
        sse = np.einsum("ij,ij->i", resid, resid)
        better = sse < best_sse
        if np.any(better):
            best_sse = np.where(better, sse, best_sse)
            best[better, 0] = c0[better]
            best[better, 1] = c1[better]
            best[better, 2] = tau
    out = {
        "e_inf": best[:, 0], "amplitude": best[:, 1], "tau_days": best[:, 2],
        "sse": best_sse,
        "cap_hit": best[:, 2] >= tau_cap * (1.0 - 1.0 / grid_points),
    }
    if not batched:
        return {"e_inf": float(out["e_inf"][0]),
                "amplitude": float(out["amplitude"][0]),
                "tau_days": float(out["tau_days"][0]),
                "sse": float(out["sse"][0]),
                "cap_hit": bool(out["cap_hit"][0]),
                "tau_cap_days": float(tau_cap),
                "x_days": [float(v) for v in x]}
    return out


# ---------------------------------------------------------------------------
# Cells and verdict
# ---------------------------------------------------------------------------


def classify(arm: dict[str, Any]) -> dict[str, Any]:
    """NULL-first (#55), effect-size keyed (#75) cell assignment."""

    e_near = arm["curve"][NEAR_BIN]
    e_near_ci = arm["curve_ci"][NEAR_BIN]
    e_near_band = arm["curve_null_band"][NEAR_BIN]
    e_far_ci = arm["curve_ci"][FAR_BIN]
    d = arm["d"]
    d_ci = arm["d_ci"]
    d_band = arm["d_null_band"]
    margin = arm["equivalence_margin"]

    existence_null = (e_near_ci[0] <= 0.0
                      or (e_near_band[0] <= e_near <= e_near_band[1]))
    if existence_null:
        cell = "NO_PERSONAL_PERSISTENCE"
    else:
        d_outside_null = d > d_band[1] or d < d_band[0]
        d_ci_includes_zero = d_ci[0] <= 0.0 <= d_ci[1]
        if d_ci_includes_zero and abs(d) < margin:
            cell = "FIXED_POINT"
        elif d > 0 and d_outside_null:
            cell = "DRIFT_WITH_CORE" if e_far_ci[0] > 0 else "FULL_DRIFT"
        elif d > 0:
            cell = ("DRIFT_WITH_CORE_UNRESOLVED" if e_far_ci[0] > 0
                    else "FULL_DRIFT_UNRESOLVED")
        else:
            cell = "FIXED_POINT" if d_ci_includes_zero else "NEGATIVE_DECAY"

    straddles: list[str] = []
    if d_ci[0] <= 0.0 <= d_ci[1]:
        straddles.append("D = 0")
    if abs(d) < margin <= abs(d) + arm["d_ci_half_width"]:
        straddles.append(f"|D| = {EQUIVALENCE_FRACTION}*E(0-90d)")
    if e_far_ci[0] <= 0.0 <= e_far_ci[1]:
        straddles.append("E(2-3y) = 0")
    return {
        "cell": cell,
        "existence_supported": not existence_null,
        "d_outside_null_band": bool(d > d_band[1] or d < d_band[0]),
        "d_ci_includes_zero": bool(d_ci[0] <= 0.0 <= d_ci[1]),
        "equivalence_margin": float(margin),
        "equivalence_satisfied": bool(abs(d) < margin),
        "ci_straddles": straddles,
        "far_bin_positive": bool(e_far_ci[0] > 0),
    }


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
    if not math.isfinite(number):
        return "n/a"
    return f"{number:.{digits}f}"


def fmt_ci(pair: Sequence[float], digits: int = 4) -> str:
    return f"[{fmt(pair[0], digits)}, {fmt(pair[1], digits)}]"


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []

    def add(text: str = "") -> None:
        lines.append(text)

    primary = payload["arms_by_key"]["primary"]
    verdict = payload["verdict"]
    census = payload["census"]

    add("# SUICA M4-U2 — the personal persistence curve")
    add("")
    add(f"**Outcome: `{verdict['cell']}`** — "
        f"E(0-90d) = {fmt(primary['curve'][NEAR_BIN])} "
        f"{fmt_ci(primary['curve_ci'][NEAR_BIN])}, "
        f"decay D = {fmt(primary['d'])} {fmt_ci(primary['d_ci'])}, "
        f"floor share E(2-3y)/E(0-90d) = {fmt(primary['floor_share'])} "
        f"{fmt_ci(primary['floor_share_ci'])}.")
    add("")
    add(f"Executed from the registration committed at "
        f"`{payload['registration_commit']}` in "
        "`docs/SUICA_M4_U_WHEN_ORDER_PLAN.md` (section \"U2 — the personal "
        "persistence curve (registered BEFORE run, 2026-08-18)\"). Run window "
        f"{payload['run_started_utc']} to {payload['run_finished_utc']}; "
        f"report generated {payload['generated_utc']}. Every number in this "
        "report is produced from the run's artifacts by "
        "`scripts/run_suica_m4_u2_persistence_curve.py` (rule 24).")
    add("")

    add("## Outcome and cell")
    add("")
    add(f"**The personal selection signature is a {payload['plain_reading']}.**")
    add("")
    add(f"- Existence: E(0-90d) = {fmt(primary['curve'][NEAR_BIN])}, 95% "
        f"cluster-bootstrap CI {fmt_ci(primary['curve_ci'][NEAR_BIN])}, "
        f"against a within-quarter permutation band "
        f"{fmt_ci(primary['curve_null_band'][NEAR_BIN])} "
        f"(permutation p = {fmt(primary['perm_p_existence'], 4)}, "
        f"B = {primary['b_perm']}).")
    add(f"- Decay: D = E(0-90d) − E(2-3y) = {fmt(primary['d'])}, CI "
        f"{fmt_ci(primary['d_ci'])}, null band "
        f"{fmt_ci(primary['d_null_band'])} "
        f"(permutation p = {fmt(primary['perm_p_decay'], 4)}).")
    add(f"- Endpoint level: E(2-3y) = {fmt(primary['curve'][FAR_BIN])} "
        f"{fmt_ci(primary['curve_ci'][FAR_BIN])} — the registered verdict "
        "endpoint (#74). The 3y+ bin is descriptive and never carries the "
        "verdict.")
    add(f"- Floor share E(2-3y)/E(0-90d) = {fmt(primary['floor_share'])} "
        f"{fmt_ci(primary['floor_share_ci'])}; registered lean "
        f"[{FLOOR_SHARE_LEAN[0]}, {FLOOR_SHARE_LEAN[1]}] — "
        f"{payload['lean_floor_verdict']}.")
    add("")
    if verdict["ci_straddles"]:
        add("**CI straddle (#75): the interval crosses "
            + ", ".join(verdict["ci_straddles"])
            + ". The verdict takes the interval statement, not the point.**")
    else:
        add("The intervals straddle no cell boundary, so the point and the "
            "interval agree on the cell.")
    add("")
    add("**The 4W projection caution, quoted into the verdict as registered:** "
        "this is a SLOW-TIME PROJECTION of the transition kernel K_u (eq 12), "
        "not K_u itself. `FIXED_POINT` would mean drift is undetected at this "
        "span and this power for this projection — never \"no dynamics\"; and "
        "a detected decay is a statement about the marginal selection "
        "distribution π_u on the Hellinger unigram sphere over calendar time, "
        "not about any psychological attribute (§5.4).")
    add("")

    add("## The null's own location (#68)")
    add("")
    add("E's expected null location is **0 BY CONSTRUCTION**: under a "
        "within-quarter relabelling the same-author pair set of a cell is a "
        "uniformly random subset of that cell's pair set, so the self mean "
        "and the epoch-matched cross mean share an expectation and their "
        "difference has expectation zero. That is an argument, not evidence; "
        "the realized center is the check.")
    add("")
    add("| bin | null center (median) | null mean | null 95% band | "
        "abs(center) ≤ 0.002 |")
    add("|---|---|---|---|---|")
    for b in range(N_BINS):
        centre = primary["curve_null_center"][b]
        add(f"| {BIN_LABELS[b]} | {fmt(centre, 6)} | "
            f"{fmt(primary['curve_null_mean'][b], 6)} | "
            f"{fmt_ci(primary['curve_null_band'][b], 5)} | "
            f"{'PASS' if abs(centre) <= 0.002 else 'CHECK'} |")
    add("")
    add(f"D's own null: center {fmt(primary['d_null_center'], 6)}, mean "
        f"{fmt(primary['d_null_mean'], 6)}, band "
        f"{fmt_ci(primary['d_null_band'], 5)}.")
    add("")

    add("## The curve — primary arm")
    add("")
    add("| bin | self pairs | self mean cos | epoch-matched cross mean | "
        "E(b) | 95% CI | null band | mean gap (d) |")
    add("|---|---|---|---|---|---|---|---|")
    for b in range(N_BINS):
        flag = " *(descriptive)*" if b == DESCRIPTIVE_BIN else ""
        add(f"| {BIN_LABELS[b]}{flag} | {fmt(primary['self_pairs'][b])} | "
            f"{fmt(primary['self_mean'][b])} | "
            f"{fmt(primary['cross_mean_matched'][b])} | "
            f"{fmt(primary['curve'][b])} | "
            f"{fmt_ci(primary['curve_ci'][b])} | "
            f"{fmt_ci(primary['curve_null_band'][b], 5)} | "
            f"{fmt(primary['mean_gap_days'][b], 1)} |")
    add("")
    add(f"Epoch matching feasibility on the primary arm: the minimum "
        f"cross-candidate ratio is "
        f"{fmt(primary['cross_candidate_ratio_min'], 1)}× the self-pair count "
        f"over occupied (quarter-pair × bin) strata and "
        f"{fmt(primary['cross_candidate_ratio_min_cell'], 1)}× at "
        f"quarter-pair resolution (median over strata "
        f"{fmt(primary['cross_candidate_ratio_median'], 1)}×). The "
        "registration censused this as 115.4× without naming its "
        "denominator; both resolutions clear the "
        f"{CROSS_PER_SELF}× the registered sampler needs, so epoch matching "
        "is feasible in every stratum as registered. Self pairs dropped for "
        f"want of any cross partner: "
        f"{fmt(sum(primary['self_pairs_dropped_no_cross']))} of "
        f"{fmt(sum(primary['self_pairs']))}.")
    add("")

    add("## Equivalence-band width projection (#71)")
    add("")
    add(f"The FIXED_POINT equivalence margin is "
        f"{EQUIVALENCE_FRACTION} × E(0-90d) = "
        f"{fmt(primary['equivalence_margin'])}. The realized half-width of "
        f"D's 95% CI is {fmt(primary['d_ci_half_width'])} "
        f"({fmt(primary['d_ci_half_width'] / primary['equivalence_margin'], 3)}"
        f"× the margin). "
        + ("The design could therefore have DECLARED equivalence had D been "
           "near zero: the achievable band is narrower than the margin."
           if primary["d_ci_half_width"] < primary["equivalence_margin"]
           else "The design could NOT have declared equivalence at this "
                "power: the achievable band is wider than the margin, so a "
                "FIXED_POINT reading would have been unresolvable rather "
                "than supported."))
    add("")

    add("## Arms")
    add("")
    add("| arm | role | authors | blocks | E(0-90d) [CI] | E(2-3y) [CI] | "
        "D [CI] | floor share [CI] | cell | #73 |")
    add("|---|---|---|---|---|---|---|---|---|---|")
    for arm in payload["arms"]:
        cell = arm["classification"]["cell"]
        flag = arm.get("divergence_flag") or "—"
        add(f"| {arm['label']} | {arm['role']} | {fmt(arm['n_authors'])} | "
            f"{fmt(arm['n_blocks'])} | {fmt(arm['curve'][NEAR_BIN])} "
            f"{fmt_ci(arm['curve_ci'][NEAR_BIN])} | "
            f"{fmt(arm['curve'][FAR_BIN])} "
            f"{fmt_ci(arm['curve_ci'][FAR_BIN])} | {fmt(arm['d'])} "
            f"{fmt_ci(arm['d_ci'])} | {fmt(arm['floor_share'])} "
            f"{fmt_ci(arm['floor_share_ci'])} | `{cell}` | {flag} |")
    add("")
    add("Full curves, every arm:")
    add("")
    add("| arm | " + " | ".join(BIN_LABELS) + " |")
    add("|---|" + "---|" * N_BINS)
    for arm in payload["arms"]:
        add(f"| {arm['label']} | "
            + " | ".join(fmt(arm["curve"][b]) for b in range(N_BINS)) + " |")
    add("")
    if payload["flags_73"]:
        for flag in payload["flags_73"]:
            add(f"- **#73 flag** — {flag}")
    else:
        add("No arm diverges from the primary in cell; zero #73 flags.")
    add("")

    add("## Registered leans")
    add("")
    add(f"- **Primary lean — DRIFT_WITH_CORE with floor share in "
        f"[{FLOOR_SHARE_LEAN[0]}, {FLOOR_SHARE_LEAN[1]}]: the CELL held, the "
        f"MAGNITUDE did not.** Realized floor share "
        f"{fmt(primary['floor_share'])} "
        f"{fmt_ci(primary['floor_share_ci'])} — "
        f"{payload['lean_floor_verdict']}. The core survives, but it keeps "
        f"{fmt(100.0 * primary['floor_share'], 1)}% of the near-gap excess "
        f"rather than the 60-90% the planner leaned on; the interval's top "
        f"edge ({fmt(primary['floor_share_ci'][1])}) only grazes the lean's "
        "bottom. Recorded as a prediction miss in the OVERCLAIM direction — "
        "the signature moves more than the T-line's early/late AUC and the "
        "S-line's split-half implied.")
    add(f"- **Secondary lean — decay concentrated in the low-activity "
        f"tercile: {payload['lean_tercile_verdict']}.** Decay by activity "
        "tercile: "
        + "; ".join(
            f"{arm['label'].split('(')[0].strip()} D = {fmt(arm['d'])} "
            f"(floor {fmt(arm['floor_share'])})"
            for arm in payload["arms"] if arm["key"].startswith("tercile"))
        + ". The gradient is monotone in activity: thin signatures both "
          "start higher and fall further.")
    add("")
    add("## 3y+ descriptive extension")
    add("")
    add(f"E(3y+) = {fmt(primary['curve'][DESCRIPTIVE_BIN])} "
        f"{fmt_ci(primary['curve_ci'][DESCRIPTIVE_BIN])} over "
        f"{fmt(primary['self_pairs'][DESCRIPTIVE_BIN])} self pairs from "
        f"{fmt(census['authors_3y_plus'])} authors (mean gap "
        f"{fmt(primary['mean_gap_days'][DESCRIPTIVE_BIN], 1)} d). "
        "**Descriptive only — never a verdict endpoint (#74).** The support "
        "is thin and composition-shifted: only the corpus's longest-lived "
        "authors can contribute a pair at this span.")
    add("")

    if payload.get("fit"):
        fit = payload["fit"]
        add("## Exponential refinement (never verdict-carrying)")
        add("")
        add(f"Fit of E(Δt) = E_inf + A·exp(−Δt/τ) on the "
            f"{VERDICT_BINS} verdict bins at their realized mean gaps "
            f"({', '.join(fmt(v, 1) for v in fit['x_days'])} days): "
            f"E_inf = {fmt(fit['e_inf'])} {fmt_ci(fit['e_inf_ci'])}, "
            f"A = {fmt(fit['amplitude'])} {fmt_ci(fit['amplitude_ci'])}, "
            f"τ = {fmt(fit['tau_days'], 1)} d "
            f"{fmt_ci(fit['tau_ci'], 1)} "
            f"({fmt(fit['tau_days'] / 365.25, 2)} y). "
            f"τ cap {fmt(fit['tau_cap_days'], 0)} d; cap hit on the point "
            f"fit: {fmt(fit['cap_hit'])}; cap-hit share across bootstrap "
            f"replicates {fmt(fit['cap_hit_share'], 3)}. "
            f"Residual SSE {fmt(fit['sse'], 8)}.")
        add("")
        add("**The fit does NOT carry the verdict, and on this curve it "
            "could not have.** Three parameters on five points is weakly "
            f"identified: the E_inf interval {fmt_ci(fit['e_inf_ci'])} runs "
            "negative at its bottom — an unphysical value for a floor — and "
            f"{fmt(100.0 * fit['cap_hit_share'], 1)}% of bootstrap replicates "
            f"push tau to the {fmt(fit['tau_cap_days'], 0)}-day cap, i.e. "
            "prefer a straight line to a decay-with-floor over this window. "
            "The floor the VERDICT rests on is the measured E(2-3y) and its "
            "own interval, not this E_inf. Read tau as an order of magnitude "
            "(years, not months), nothing finer.")
        add("")

    add("## Reliability descriptive")
    add("")
    rel = payload["reliability"]
    add(f"Adjacent-block same-author cosine (consecutive disjoint K = "
        f"{K_PRIMARY} blocks, the shortest personal gap the design can see): "
        f"mean {fmt(rel['adjacent_mean'])} over "
        f"{fmt(rel['n_adjacent_pairs'])} pairs from "
        f"{fmt(rel['n_authors'])} authors; median {fmt(rel['adjacent_median'])}"
        f", mean gap {fmt(rel['adjacent_mean_gap_days'], 1)} d. "
        "Attenuation is constant across bins by the fixed-K construction, so "
        "E is an attenuated LEVEL and only D and the floor share are "
        "transportable. Adjacent blocks are the empirical ceiling this "
        "estimator can reach at K = "
        f"{K_PRIMARY}.")
    add("")

    add("## Census reproduction (blocking gate)")
    add("")
    add("| quantity | registered | reproduced | status |")
    add("|---|---|---|---|")
    for key, entry in census["pins"].items():
        add(f"| {key} | {entry['registered']} | {entry['observed']} | "
            f"{entry['status']} |")
    add("")
    add("Cache anchors: "
        + ", ".join(f"{k} = {fmt(v)}"
                    for k, v in payload["anchors"]["observed"].items())
        + f" — gate {payload['anchors']['status']}.")
    add("")

    add("## Honesty checks")
    add("")
    add("| check | result |")
    add("|---|---|")
    for key, value in payload["gates"].items():
        add(f"| {key} | {value} |")
    add("")
    if primary.get("cross_sampler_check"):
        chk = primary["cross_sampler_check"]
        add(f"**Cross-baseline estimator equivalence (disclosed re-posing "
            f"RD-U2-1).** The registration specifies the epoch-matched cross "
            f"term as a sample of up to {CROSS_PER_SELF} different-author "
            "pairs per self pair per cell. This run computes the cell's cross "
            "mean EXACTLY (over all its different-author pairs) and weights "
            "cells by the same self-pair histogram — the zero-variance limit "
            "of the registered sampler, identical in estimand because the "
            "censused feasibility (min "
            f"{fmt(primary['cross_candidate_ratio_min'], 1)}× here) makes "
            f"{CROSS_PER_SELF} × self < available in every stratum. The "
            "registered sampler was ALSO run on the primary arm as a check: "
            f"{fmt(chk['cross_pairs_drawn'])} cross pairs drawn, per-bin "
            f"|sampled − exact| max {fmt(chk['max_abs_difference'], 6)}.")
        add("")

    add("## Boundaries")
    add("")
    for item in payload["boundaries"]:
        add(f"- {item}")
    add("")

    add("## Configuration")
    add("")
    add("```json")
    add(json.dumps(payload["config"], indent=2, sort_keys=True, default=float))
    add("```")
    add("")
    add("Artifacts (gitignored): `results/m4_u2_persistence_curve/` — "
        "`config.json`, `config.sha256.json`, `census.json`, `anchors.json`, "
        "`arms.json`, `curve.json`, `verdict.json`, `fit.json`, "
        "`reliability.json`, `cross_sampler_check.json`, `id_leak_scan.json`, "
        "`report_payload.json`, `run_log.jsonl`.")
    add("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _census(blocks_all: Blocks, quarters: np.ndarray,
            pool: np.ndarray, self_pairs: list[int],
            contributors: dict[str, int],
            tercile_sizes: list[int],
            tercile_edges: list[int]) -> dict[str, Any]:
    nb = blocks_all.blocks_per_author
    observed = {
        "authors_ge_4_blocks": int((nb >= 4).sum()),
        "authors_ge_2_blocks": int((nb >= 2).sum()),
        "authors_ge_8_blocks": int((nb >= 8).sum()),
        "total_blocks_all_authors": int(nb.sum()),
        "n_quarters": int(np.unique(quarters).size),
        "self_pairs_per_bin": [int(x) for x in self_pairs],
        "authors_2_3y": int(contributors["2-3y"]),
        "authors_3y_plus": int(contributors["3y+"]),
        "tercile_sizes": [int(x) for x in tercile_sizes],
        "tercile_edges_vocab_events": [int(x) for x in tercile_edges],
    }
    pins = {}
    for key, expected in CENSUS_PINS.items():
        got = observed[key]
        pins[key] = {"registered": expected, "observed": got,
                     "status": "PASS" if got == expected else "MISMATCH"}
    return {"pins": pins, "observed": observed,
            "pool_size": int(pool.size),
            "pool_blocks": int(nb[pool].sum()),
            "authors_3y_plus": observed["authors_3y_plus"],
            "status": "PASS" if all(v["status"] == "PASS"
                                    for v in pins.values()) else "MISMATCH"}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--b-perm", type=int, default=B_PERM)
    parser.add_argument("--b-boot", type=int, default=B_BOOT)
    parser.add_argument("--arms", type=str, default="all")
    parser.add_argument("--registration-commit", type=str, default="b864dc7")
    args = parser.parse_args(argv)

    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    log = RunLog(output / "run_log.jsonl")
    run_started = utc_now()
    log.event("start", cache=str(args.cache), b_perm=args.b_perm,
              b_boot=args.b_boot, arms=args.arms)

    cache = load_event_cache(args.cache)
    anchors = verify_cache_anchors(cache)
    write_json(output / "anchors.json", anchors)
    log.event("cache_anchor_gate", **anchors)
    if anchors["status"] != "PASS":
        raise SystemExit(f"STOP: cache anchor gate FAILED: "
                         f"{anchors['mismatches']}")

    n_authors_total = len(cache.authors)
    origin = float(cache.created_utc.min())
    vocab_index_full = cache.vocab_of_subreddit[cache.subreddit_code]

    log.event("blocks_build_start", k=K_PRIMARY)
    blocks_all = build_blocks(cache.author_code, cache.created_utc,
                              vocab_index_full, len(cache.vocabulary),
                              K_PRIMARY, n_authors=n_authors_total)
    quarters_all = assign_quarters(blocks_all.midpoint, origin)
    mid_days_all = (blocks_all.midpoint - origin) / 86400.0
    log.event("blocks_built", n_blocks=int(blocks_all.author.size),
              n_quarters=int(np.unique(quarters_all).size),
              in_vocab_events=int(blocks_all.vocab_events_per_author.sum()))

    nb = blocks_all.blocks_per_author
    pool = np.flatnonzero(nb >= POOL_MIN_BLOCKS)
    pool_mask = np.zeros(n_authors_total, dtype=bool)
    pool_mask[pool] = True

    # ---- census: self pairs per bin and 2-3y / 3y+ contributors ----
    sel_pool = pool_mask[blocks_all.author]
    order = np.lexsort((mid_days_all[sel_pool], quarters_all[sel_pool]))
    idx_pool = np.flatnonzero(sel_pool)[order]
    pool_author = blocks_all.author[idx_pool]
    pool_quarter = quarters_all[idx_pool]
    pool_mid = mid_days_all[idx_pool]
    pool_features = blocks_all.features[idx_pool]

    self_pairs_census = np.zeros(N_BINS, dtype=np.int64)
    contributors = {label: set() for label in BIN_LABELS}
    for author in pool:
        mids = mid_days_all[blocks_all.author == author]
        if mids.size < 2:
            continue
        iu = np.triu_indices(mids.size, 1)
        gaps = np.abs(mids[:, None] - mids[None, :])[iu]
        counts = np.bincount(gap_bin(gaps), minlength=N_BINS)
        self_pairs_census += counts
        for b in range(N_BINS):
            if counts[b]:
                contributors[BIN_LABELS[b]].add(int(author))

    block_counts_pool = nb[pool]
    lo_edge = int(np.quantile(block_counts_pool, TERCILE_QUANTILES[0]))
    hi_edge = int(np.quantile(block_counts_pool, TERCILE_QUANTILES[1]))
    tercile_of_author = np.where(block_counts_pool <= lo_edge, 0,
                                 np.where(block_counts_pool <= hi_edge, 1, 2))
    tercile_sizes = [int((tercile_of_author == t).sum()) for t in range(3)]

    census = _census(blocks_all, quarters_all, pool,
                     [int(x) for x in self_pairs_census],
                     {"2-3y": len(contributors["2-3y"]),
                      "3y+": len(contributors["3y+"])},
                     tercile_sizes,
                     [lo_edge * K_PRIMARY, hi_edge * K_PRIMARY])
    write_json(output / "census.json", census)
    log.event("census", status=census["status"],
              pool=census["pool_size"], pool_blocks=census["pool_blocks"])
    if census["status"] != "PASS":
        raise SystemExit(
            "STOP: census reproduction differs from the registration: "
            + json.dumps({k: v for k, v in census["pins"].items()
                          if v["status"] != "PASS"}, sort_keys=True))

    # ---- reliability descriptive: adjacent same-author blocks ----
    adj_cos: list[np.ndarray] = []
    adj_gap: list[np.ndarray] = []
    for author in pool:
        rows = np.flatnonzero(blocks_all.author == author)
        if rows.size < 2:
            continue
        feats = blocks_all.features[rows]
        adj_cos.append(np.einsum("ij,ij->i", feats[:-1], feats[1:]))
        adj_gap.append(np.diff(mid_days_all[rows]))
    adj_cos_all = np.concatenate(adj_cos)
    adj_gap_all = np.concatenate(adj_gap)
    reliability = {
        "adjacent_mean": float(adj_cos_all.mean()),
        "adjacent_median": float(np.median(adj_cos_all)),
        "adjacent_sd": float(adj_cos_all.std(ddof=1)),
        "adjacent_mean_gap_days": float(adj_gap_all.mean()),
        "n_adjacent_pairs": int(adj_cos_all.size),
        "n_authors": int(pool.size),
    }
    write_json(output / "reliability.json", reliability)
    log.event("reliability", **reliability)

    # ---- arms ----
    requested = (None if args.arms == "all"
                 else {s.strip() for s in args.arms.split(",")})

    def wanted(key: str) -> bool:
        return requested is None or key in requested

    arms: list[dict[str, Any]] = []
    arms_by_key: dict[str, dict[str, Any]] = {}

    def run(key: str, label: str, role: str, features: np.ndarray,
            author: np.ndarray, quarter: np.ndarray, mid: np.ndarray,
            *, sampler: bool = False) -> dict[str, Any]:
        log.event("arm_start", arm=key, blocks=int(features.shape[0]),
                  authors=int(np.unique(author).size))
        result = compute_arm(features, author, quarter, mid,
                             n_perm=args.b_perm, n_boot=args.b_boot,
                             seed=SEED, cross_sampler_check=sampler,
                             log=log, label=label)
        result["key"] = key
        result["role"] = role
        result["classification"] = classify(result)
        log.event("arm_done", arm=key, cell=result["classification"]["cell"],
                  e_near=result["curve"][NEAR_BIN], d=result["d"],
                  floor=result["floor_share"])
        arms.append(result)
        arms_by_key[key] = result
        return result

    primary = run("primary", "full vocab, pool 849, verdict bins", "PRIMARY",
                  pool_features, pool_author, pool_quarter, pool_mid,
                  sampler=True)

    if wanted("balanced"):
        panel = np.array(sorted(contributors["2-3y"]), dtype=np.int64)
        keep = np.isin(pool_author, panel)
        run("balanced", f"balanced panel ({panel.size} authors with 2-3y "
            "support)", "sensitivity — composition control",
            pool_features[keep], pool_author[keep], pool_quarter[keep],
            pool_mid[keep])

    for t in range(3):
        key = f"tercile{t + 1}"
        if not wanted(key):
            continue
        members = pool[tercile_of_author == t]
        keep = np.isin(pool_author, members)
        bound = ("<= " + str(lo_edge * K_PRIMARY) if t == 0
                 else (f"{lo_edge * K_PRIMARY}-{hi_edge * K_PRIMARY}"
                       if t == 1 else "> " + str(hi_edge * K_PRIMARY)))
        run(key, f"activity tercile {t + 1} ({members.size} authors, "
            f"{bound} vocab events)", "secondary — decay shape by activity",
            pool_features[keep], pool_author[keep], pool_quarter[keep],
            pool_mid[keep])

    if wanted("clean"):
        removed = sorted(name for name in cache.vocabulary
                         if is_explicit_personality_community(name))
        keep_names = [n for n in cache.vocabulary if n not in set(removed)]
        remap = {name: i for i, name in enumerate(keep_names)}
        clean_map = np.full(cache.vocab_of_subreddit.shape, -1, dtype=np.int32)
        for idx, name in enumerate(cache.subreddits):
            if cache.vocab_of_subreddit[idx] >= 0 and name in remap:
                clean_map[idx] = remap[name]
        log.event("clean_vocab", removed=len(removed),
                  kept=len(keep_names))
        clean_blocks = build_blocks(cache.author_code, cache.created_utc,
                                    clean_map[cache.subreddit_code],
                                    len(keep_names), K_PRIMARY,
                                    n_authors=n_authors_total)
        c_quarter = assign_quarters(clean_blocks.midpoint, origin)
        c_mid = (clean_blocks.midpoint - origin) / 86400.0
        c_pool = np.flatnonzero(
            clean_blocks.blocks_per_author >= POOL_MIN_BLOCKS)
        c_mask = np.zeros(n_authors_total, dtype=bool)
        c_mask[c_pool] = True
        sel = c_mask[clean_blocks.author]
        o = np.lexsort((c_mid[sel], c_quarter[sel]))
        i = np.flatnonzero(sel)[o]
        arm = run("clean", f"clean_no_explicit_personality "
                  f"({len(removed)} communities removed)",
                  "governance echo", clean_blocks.features[i],
                  clean_blocks.author[i], c_quarter[i], c_mid[i])
        arm["removed_communities"] = len(removed)
        del clean_blocks

    if wanted("k100"):
        k_blocks = build_blocks(cache.author_code, cache.created_utc,
                                vocab_index_full, len(cache.vocabulary),
                                K_SENSITIVITY, n_authors=n_authors_total)
        k_quarter = assign_quarters(k_blocks.midpoint, origin)
        k_mid = (k_blocks.midpoint - origin) / 86400.0
        k_pool = np.flatnonzero(
            k_blocks.blocks_per_author >= POOL_MIN_BLOCKS)
        k_mask = np.zeros(n_authors_total, dtype=bool)
        k_mask[k_pool] = True
        sel = k_mask[k_blocks.author]
        o = np.lexsort((k_mid[sel], k_quarter[sel]))
        i = np.flatnonzero(sel)[o]
        run("k100", f"K = {K_SENSITIVITY} blocks", "sensitivity — block size",
            k_blocks.features[i], k_blocks.author[i], k_quarter[i], k_mid[i])
        del k_blocks

    verdict = dict(primary["classification"])
    verdict["arm"] = "primary"
    verdict["generated_utc"] = utc_now()

    flags: list[str] = []
    for arm in arms:
        if arm["key"] == "primary":
            continue
        if arm["classification"]["cell"] != verdict["cell"]:
            flag = (f"{arm['label']} lands in "
                    f"`{arm['classification']['cell']}` while the primary "
                    f"lands in `{verdict['cell']}`")
            arm["divergence_flag"] = "#73"
            flags.append(flag)
    verdict["flags_73"] = flags

    # ---- refinement fit (only if a decay is detected) ----
    fit_payload = None
    if primary["d"] > 0 and (primary["d_ci"][0] > 0
                             or primary["classification"]
                             ["d_outside_null_band"]):
        x = np.asarray(primary["mean_gap_days"][:VERDICT_BINS])
        point = exponential_fit(x, np.asarray(primary["curve"][:VERDICT_BINS]))
        boot = exponential_fit(x, primary["boot_curve"][:, :VERDICT_BINS])
        fit_payload = dict(point)
        fit_payload["e_inf_ci"] = [float(np.percentile(boot["e_inf"], 2.5)),
                                   float(np.percentile(boot["e_inf"], 97.5))]
        fit_payload["amplitude_ci"] = [
            float(np.percentile(boot["amplitude"], 2.5)),
            float(np.percentile(boot["amplitude"], 97.5))]
        fit_payload["tau_ci"] = [float(np.percentile(boot["tau_days"], 2.5)),
                                 float(np.percentile(boot["tau_days"], 97.5))]
        fit_payload["cap_hit_share"] = float(np.mean(boot["cap_hit"]))
        write_json(output / "fit.json", fit_payload)
        log.event("fit", **{k: v for k, v in fit_payload.items()
                            if k != "x_days"})

    floor = primary["floor_share"]
    lean_floor = ("HELD" if FLOOR_SHARE_LEAN[0] <= floor <= FLOOR_SHARE_LEAN[1]
                  else ("EXCEEDED (above the lean's top)"
                        if floor > FLOOR_SHARE_LEAN[1] else
                        "MISSED (below the lean's bottom)"))
    tercile_ds = {arm["key"]: arm["d"] for arm in arms
                  if arm["key"].startswith("tercile")}
    lean_tercile = "not run"
    if len(tercile_ds) == 3:
        worst = max(tercile_ds, key=lambda k: tercile_ds[k])
        lean_tercile = ("HELD (largest decay in the low-activity tercile)"
                        if worst == "tercile1" else
                        f"MISSED (largest decay in {worst}, "
                        f"D = {tercile_ds[worst]:.4f}, against "
                        f"tercile1 D = {tercile_ds['tercile1']:.4f})")

    script_bytes = Path(__file__).read_bytes()
    config = {
        "registration_commit": args.registration_commit,
        "seed": SEED, "b_perm": args.b_perm, "b_boot": args.b_boot,
        "k_primary": K_PRIMARY, "k_sensitivity": K_SENSITIVITY,
        "pool_min_blocks": POOL_MIN_BLOCKS,
        "quarter_days": QUARTER_DAYS,
        "bin_edges_days": list(BIN_EDGES_DAYS),
        "bin_labels": list(BIN_LABELS),
        "bin_interval_convention": "left-closed, right-open on |Δt| in days",
        "verdict_bins": VERDICT_BINS,
        "verdict_endpoint_bin": BIN_LABELS[FAR_BIN],
        "descriptive_bin": BIN_LABELS[DESCRIPTIVE_BIN],
        "equivalence_fraction": EQUIVALENCE_FRACTION,
        "floor_share_lean": list(FLOOR_SHARE_LEAN),
        "tau_cap_days": TAU_CAP_DAYS,
        "cross_per_self_registered": CROSS_PER_SELF,
        "cache": str(args.cache),
        "epoch_origin": EPOCH_ORIGIN,
        "epoch_origin_utc": datetime.fromtimestamp(
            origin, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "recorded_choices": {
            "cross_baseline_estimator":
                "EXACT cell-conditional cross mean over all different-author "
                "pairs of the (quarter-pair, bin) stratum, weighted by the "
                "self-pair histogram — the zero-variance limit of the "
                "registered up-to-20-per-self-pair sampler; the registered "
                "sampler is run on the primary arm as an equivalence check "
                "(disclosed re-posing RD-U2-1)",
            "cell_definition": "unordered quarter pair (min, max)",
            "bootstrap_cross_baseline":
                "cell cross means held at their full-arm values inside the "
                "cluster bootstrap; only the self side and the epoch-matching "
                "weights are resampled (the cross mean is estimated from "
                "~10^9 pairs and carries negligible variance beside the "
                "author-clustered self side)",
            "tercile_rule":
                f"quantiles {TERCILE_QUANTILES} of per-author BLOCK counts, "
                f"assignment {TERCILE_ASSIGN}; edges reported in vocabulary "
                f"events as blocks x K",
            "k100_pool_rule":
                f">= {POOL_MIN_BLOCKS} blocks recomputed at K = "
                f"{K_SENSITIVITY} (the same pool rule, not the K = 50 pool)",
            "clean_arm_rule":
                "explicit-typology communities dropped from the vocabulary, "
                "their events become OOV, blocks and pool recomputed",
            "fit_abscissa": FIT_ABSCISSA,
            "fit_solver": f"log grid of {FIT_GRID_POINTS} tau values in "
                          f"[1, {TAU_CAP_DAYS}] days with the linear "
                          f"least-squares solution for (E_inf, A) at each",
            "permutation_scaffold":
                "within-quarter block->author relabelling implemented as a "
                "fixed slot->author map (an exact permutation invariant) with "
                "a permuted slot->block-position map; row 0 is the identity",
            "empty_stratum_rule":
                "a (cell, bin) stratum with self pairs but no different-"
                "author pair is dropped from both terms and the weights are "
                "renormalized; the dropped self-pair mass is reported",
        },
        "script_sha256": hashlib.sha256(script_bytes).hexdigest(),
    }
    write_json(output / "config.json", config)
    write_json(output / "config.sha256.json",
               {"script_sha256": config["script_sha256"],
                "config_sha256": hashlib.sha256(
                    json.dumps(config, sort_keys=True,
                               default=float).encode("utf-8")).hexdigest()})

    serializable_arms = []
    for arm in arms:
        clean = {k: v for k, v in arm.items()
                 if k not in {"boot_curve", "null_curve"}}
        serializable_arms.append(clean)
    write_json(output / "arms.json", serializable_arms)
    write_json(output / "curve.json",
               {"bins": list(BIN_LABELS),
                "primary": {k: primary[k] for k in
                            ("curve", "curve_ci", "curve_null_band",
                             "curve_null_center", "self_mean",
                             "cross_mean_matched", "self_pairs",
                             "mean_gap_days")}})
    write_json(output / "verdict.json", verdict)
    if primary.get("cross_sampler_check"):
        write_json(output / "cross_sampler_check.json",
                   primary["cross_sampler_check"])

    plain = {
        "DRIFT_WITH_CORE": "MOVING WAVE WITH A STANDING CORE — it drifts, "
                           "and it does not drift away",
        "FIXED_POINT": "STANDING WAVE at this span and power",
        "FULL_DRIFT": "MOVING WAVE — no core survives to the verdict endpoint",
        "NO_PERSONAL_PERSISTENCE": "no personal excess at all",
    }.get(verdict["cell"], f"curve in cell {verdict['cell']}")

    run_finished = utc_now()
    payload: dict[str, Any] = {
        "generated_utc": utc_now(),
        "run_started_utc": run_started,
        "run_finished_utc": run_finished,
        "registration_commit": args.registration_commit,
        "anchors": anchors,
        "census": census,
        "arms": serializable_arms,
        "arms_by_key": {k: {kk: vv for kk, vv in v.items()
                            if kk not in {"boot_curve", "null_curve"}}
                        for k, v in arms_by_key.items()},
        "verdict": verdict,
        "flags_73": flags,
        "fit": fit_payload,
        "reliability": reliability,
        "plain_reading": plain,
        "lean_floor_verdict": lean_floor,
        "lean_tercile_verdict": lean_tercile,
        "config": config,
        "boundaries": [
            "This is ONE slow-time projection of K_u (eq 12) onto the "
            "marginal selection distribution over 1191 communities. A flat "
            "curve would mean drift is undetected in THIS projection at THIS "
            "span and power — never that the process has no dynamics; a "
            "decaying one is a statement about π_u on the Hellinger unigram "
            "sphere, not about any psychological attribute (§5.4).",
            "E is an ATTENUATED level: reliability at K = "
            f"{K_PRIMARY} is bounded by the adjacent-block similarity "
            f"({fmt(reliability['adjacent_mean'])}), so only D and the floor "
            "share are transportable across block sizes; the K = 100 arm is "
            "the check that they are.",
            "THE CURVE HAS NOT FLATTENED BY THE VERDICT ENDPOINT. "
            f"E(3y+) = {fmt(primary['curve'][DESCRIPTIVE_BIN])} sits below "
            f"E(2-3y) = {fmt(primary['curve'][FAR_BIN])}, and the "
            "refinement fit's asymptote — weakly identified, see that "
            "section — sits below both. `DRIFT_WITH_CORE` is therefore a "
            "statement at a THREE-YEAR horizon: the core is what survives "
            "three years, not a demonstrated permanent floor. Extrapolating "
            "the floor past the observed span is not licensed by this leg.",
            "The verdict endpoint is 2-3y because that is the last bin with "
            f"deep support ({fmt(census['pins']['authors_2_3y']['observed'])} "
            "contributing authors, convention #74). The 3y+ bin is reported "
            "and never used for a verdict: its "
            f"{fmt(census['pins']['authors_3y_plus']['observed'])} authors "
            "are a survivorship-selected subpopulation.",
            "Epoch matching absorbs shared platform drift by construction, "
            "so E measures PERSONAL persistence in excess of the epoch. It "
            "cannot separate a personal taste change from a personal change "
            "of which communities exist for that person; both read as decay.",
            "Blocks are event-counted, not time-counted: a 50-event block "
            "spans days for a heavy user and months for a light one. The "
            "activity terciles are the sensitivity that makes that visible; "
            "the bins are calendar gaps between block MIDPOINTS.",
            "The cluster bootstrap resamples authors, so the CIs carry "
            "author-level sampling error. They do not carry error in the "
            "cross baseline, which is held at its full-arm value (recorded "
            "in the configuration block).",
            "Label-free and corpus-level throughout: no Big5 or MBTI value "
            "is read anywhere in this leg, and no per-author quantity is "
            "reported or committed.",
        ],
        "gates": {
            "cache anchor gate (3,005,360 events / 1401 authors / 1191 "
            "vocabulary)": anchors["status"],
            "census reproduction (all registered pins)": census["status"],
            "permutation-null center abs(E) <= 0.002 in every bin":
                "PASS" if all(abs(c) <= 0.002
                              for c in primary["curve_null_center"])
                else "CHECK",
            "permutation-null center for D": fmt(primary["d_null_center"], 6),
            "3y+ excluded from the verdict (#74)": "PASS",
            "no synthetic gate required (registered: R layer, no world "
            "simulated)": "N/A",
        },
    }
    if primary.get("cross_sampler_check"):
        payload["gates"]["cross-sampler equivalence (max abs(sampled − "
                         "exact))"] = fmt(
            primary["cross_sampler_check"]["max_abs_difference"], 6)

    write_report(args.report, payload)
    scan = scan_for_cohort_ids(
        [args.report, Path(__file__),
         ROOT / "tests/test_m4_u2_persistence_curve.py",
         ROOT / "docs/SUICA_M4_U_WHEN_ORDER_PLAN.md",
         ROOT / "docs/CLAIMS_LEDGER.md"],
        cache.authors)
    write_json(output / "id_leak_scan.json", scan)
    log.event("id_leak_scan", status=scan["status"], hits=scan["n_hits"])
    payload["gates"]["ID-leak scan (0 of 1401 cohort IDs in committed files)"]\
        = scan["status"]
    write_report(args.report, payload)
    if scan["status"] != "PASS":
        raise SystemExit(f"STOP: ID-leak scan FAILED: {scan['hits']}")

    write_json(output / "report_payload.json",
               {k: v for k, v in payload.items() if k != "config"})
    log.event("done", cell=verdict["cell"], d=primary["d"],
              floor=primary["floor_share"], flags_73=len(flags))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
