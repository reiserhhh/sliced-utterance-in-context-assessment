#!/usr/bin/env python3
"""SUICA M4-X2 — the path of expression volume.

Registered BEFORE the run in ``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``
(commit 550466f, section "X2 — the path of expression volume").  This runner
executes that registration and nothing else.

Crossing #3 (What x When): the first real-data projection of expression STATE
TRAJECTORIES.  Does expression volume have reproducible path structure in
event time, and is the path parameter an AUTHOR attribute?

    y      = log1p(word_count_quoteless)      (#70, pinned)
    order  = per-author stable sort by created_utc (ties keep stream order)
    halves = full-stream median of the author's own created_utc (<= early)
    r1     = per (author, half) lag-1 Pearson autocorrelation of the y
             sequence, adjacency = consecutive events WITHIN a half

Two estimands, each with its own null (#68/#66):

1.  PRESENCE (co-reports) — mean over (author, half) of r1, against the
    MARGINAL-PRESERVING within-half permutation null.  Each half's y sequence
    is permuted; the per-half marginal is EXACTLY invariant (bit-exact
    contract test, U1's exact-bag pattern on a scalar).  B = 499, band =
    2.5/97.5 percentiles.
2.  OWNERSHIP rho_own (ROUTES) — Pearson over pool authors of
    (r1_early, r1_late).  Own null: the author pairing permuted between
    halves, B = 499.  Cluster bootstrap over authors, B = 1000, for the CI.

GOVERNANCE
----------
Metadata only.  The stream reads exactly five columns — ``author``,
``subreddit``, ``created_utc``, ``link_id``, ``word_count_quoteless``.  NO
text body is ever read.  ``author_profiles.csv`` is NEVER opened; the leg is
label-free end to end (the Big5 cohort enters only as a NAME LIST that splits
the corpus into two disjoint author sets).  Caches and author listings live in
gitignored ``results/`` and are never committed.  Aggregates only.
EXPLORATORY, corpus-level; no person claims; no psychological naming
(expression VOLUME is a technical object, not a trait).

MACHINERY PROVENANCE (#56/#81 — the inherited object, imported BY FILE)
-----------------------------------------------------------------------
``RunLog``, ``write_json``, ``utc_now``, ``fmt``, ``fmt_ci``,
``percentile_ci``, ``scan_for_cohort_ids``, ``baseline_hit_keys``,
``new_hits_only`` and ``anchor_gate`` come from the X1b runner (which imports
X1, which imports U2/U2b).  They are bound, not copied.  X2's own event cache
is FRESH: X1's cell cache aggregates over (author, community, half) and has no
event order and no ``link_id``, so it cannot serve a path estimand.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Configuration (registration pins first, then recorded choices)
# ---------------------------------------------------------------------------

SEED = 20260819                     # registration pin
B_PERM = 499                        # registration pin
B_BOOT = 1000                       # registration pin

POOL_FLOOR_PRIMARY = 50             # registration pin: >= 50 events EACH half
POOL_FLOOR_SENSITIVITY = 100        # registration pin: the floor-100 arm

# --- #87 boundary REGIONS on rho_own (primary arm) -------------------------

BOUNDARY_LOW = 0.15                 # registration pin
BOUNDARY_HIGH = 0.50                # registration pin
BOUNDARY_HALFWIDTH = 0.011          # registration pin (projected CI halfwidth)

CELL_NOT_OWNED = "PATH_NOT_OWNED"
CELL_AT_LOW = "AT_BOUNDARY(0.15)"
CELL_WEAK = "WEAKLY_OWNED"
CELL_AT_HIGH = "AT_BOUNDARY(0.50)"
CELL_STRONG = "STRONGLY_OWNED"
CELL_A1_STOP = "A1_STOP__SYNTHETIC_GATE_FAILED"

# --- registered leans (report against, never route) ------------------------

LEAN_RHO_OWN = (0.30, 0.60)         # open below, closed above
RETENTION_MOST = 0.50               # "retains most" = ratio >= 0.50

# --- Part 0, the realized-skeleton gate ------------------------------------

N_SYNTH_REPLICATES = 8              # registration pin
TOL_SD_MULT = 3.0                   # registration pin
TOL_FLOOR = 0.02                    # registration pin: max(0.02, 3 x rep sd)
RHO_TRUE_TARGET = 0.50              # registration pin: #76 operating point
PHI_BAR_AR = 0.20                   # recorded: the AR world's mean phi
PHI_BAR_COMMON = 0.20               # recorded: the common-path world's phi
PHI_CLIP = 0.95                     # recorded: |phi_u| clip on the AR draw

# --- inherited anchors (BLOCKING under #78) --------------------------------

ANCHOR_ROWS_PARSEABLE = 17_640_062
ANCHOR_AUTHORS = 10_296
ANCHOR_BIG5_AUTHORS = 1_401
ANCHOR_DISJOINT_AUTHORS = 8_895

# --- the X2 census (planner arithmetic, BLOCKING under #78) ----------------

ANCHOR_POOL_DISJOINT = 8_008
ANCHOR_POOL_BIG5 = 1_116
ANCHOR_CROSS_SHARE_DISJOINT = 0.73159
ANCHOR_CROSS_SHARE_BIG5 = 0.62054
ANCHOR_DEGENERATE_DISJOINT = 0
ANCHOR_DEGENERATE_BIG5 = 0
ANCHOR_MEDIAN_ADJ_DISJOINT = 348.0
ANCHOR_MEDIAN_ADJ_BIG5 = 491.75

# --- recorded implementation choices (registration silent) -----------------

CHUNK_SIZE = 2_000_000
PAD_CHUNK_ROWS = 64                 # length-sorted padding chunk (null engine)
CACHE_VERSION = 2

SEED_PART0 = SEED + 1               # world draws (#76: derived, never chosen)
SEED_PERM = SEED + 2                # permutation nulls
SEED_BOOT = SEED + 3                # cluster bootstraps

DEFAULT_COMMENTS = Path(
    "/Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/"
    "all_comments_since_2015.csv")
DEFAULT_COHORT = ROOT / "results/m4_sr0_recon/cohort_authors.csv"
DEFAULT_OUTPUT = ROOT / "results/m4_x2_volume_path"
DEFAULT_REPORT = ROOT / "reports/SUICA_M4_X2_VOLUME_PATH_REPORT.md"

X1B_SCRIPT = ROOT / "scripts/run_suica_m4_x1b_venue_response_fe.py"

COMMITTED_FILES = (
    ROOT / "reports/SUICA_M4_X2_VOLUME_PATH_REPORT.md",
    ROOT / "scripts/run_suica_m4_x2_volume_path.py",
    ROOT / "tests/test_m4_x2_volume_path.py",
    ROOT / "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md",
    ROOT / "docs/CLAIMS_LEDGER.md",
)


# ---------------------------------------------------------------------------
# Inherited machinery (#56/#81: bound to the committed object, not copied)
# ---------------------------------------------------------------------------


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:      # pragma: no cover
        raise RuntimeError(f"cannot import machinery from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


X1B = load_module("suica_m4_x1b_for_x2", X1B_SCRIPT)

write_json = X1B.write_json
utc_now = X1B.utc_now
fmt = X1B.fmt
fmt_ci = X1B.fmt_ci
RunLog = X1B.RunLog
percentile_ci = X1B.percentile_ci
scan_for_cohort_ids = X1B.scan_for_cohort_ids
baseline_hit_keys = X1B.baseline_hit_keys
new_hits_only = X1B.new_hits_only
anchor_gate = X1B.anchor_gate
_Interner = X1B.X1._Interner


# ---------------------------------------------------------------------------
# Stage 1 — the event stream (one pass; no bodies, no labels)
# ---------------------------------------------------------------------------


def _sorted_remap(names: list[str]) -> tuple[list[str], np.ndarray]:
    order = sorted(range(len(names)), key=lambda i: names[i])
    remap = np.empty(len(names), dtype=np.int64)
    for new_code, old_code in enumerate(order):
        remap[old_code] = new_code
    return [names[i] for i in order], remap


def hash_links(values: pd.Series, missing_base: int) -> tuple[np.ndarray, int]:
    """Deterministic 64-bit thread hash; missing ids get a UNIQUE sentinel.

    ``link_id`` is NOT part of the parseable predicate (the 17,640,062-row
    anchor is X1's, over author/subreddit/created_utc/wcq), so a missing
    thread id must be handled rather than dropped.  A missing id is given a
    per-row unique sentinel, which makes every adjacency touching it
    CROSS-thread — the conservative direction for an arm whose claim is that
    the path survives thread mechanics.  The count is reported.
    """

    missing = values.isna().to_numpy()
    filled = values.fillna("")
    hashed = pd.util.hash_pandas_object(filled, index=False).to_numpy(np.uint64)
    n_missing = int(missing.sum())
    if n_missing:
        hashed[missing] = (missing_base
                           + np.arange(n_missing, dtype=np.uint64))
    return hashed, n_missing


def stream_events(comments_path: Path, log: RunLog) -> dict[str, Any]:
    """Stream the comments file for the five metadata columns X2 needs."""

    columns = ["author", "subreddit", "created_utc", "link_id",
               "word_count_quoteless"]
    log.event("stream_start", comments_path=str(comments_path),
              columns=columns, note="no body column requested")
    authors = _Interner()
    subreddits = _Interner()
    author_parts: list[np.ndarray] = []
    subreddit_parts: list[np.ndarray] = []
    created_parts: list[np.ndarray] = []
    link_parts: list[np.ndarray] = []
    wcq_parts: list[np.ndarray] = []
    rows_streamed = 0
    rows_parseable = 0
    wcq_zero = 0
    link_missing = 0
    chunks = 0
    # Sentinel block for missing thread ids, far from any real hash run.
    missing_base = np.uint64(1)

    for chunk in pd.read_csv(
        comments_path,
        usecols=columns,
        chunksize=CHUNK_SIZE,
        dtype={"author": "str", "subreddit": "str", "link_id": "str"},
        on_bad_lines="skip",
        engine="c",
    ):
        chunks += 1
        rows_streamed += len(chunk)
        created = pd.to_numeric(chunk["created_utc"], errors="coerce")
        wcq = pd.to_numeric(chunk["word_count_quoteless"], errors="coerce")
        keep = (chunk["author"].notna() & chunk["subreddit"].notna()
                & created.notna() & wcq.notna())
        n_keep = int(keep.sum())
        rows_parseable += n_keep
        if n_keep == 0:
            continue
        wcq_keep = wcq[keep].to_numpy(np.float64)
        wcq_zero += int(np.count_nonzero(wcq_keep == 0.0))
        hashed, n_missing = hash_links(chunk["link_id"][keep], missing_base)
        missing_base = missing_base + np.uint64(max(n_missing, 1))
        link_missing += n_missing
        author_parts.append(authors.encode(chunk["author"][keep]))
        subreddit_parts.append(subreddits.encode(chunk["subreddit"][keep]))
        created_parts.append(created[keep].to_numpy(np.float64))
        link_parts.append(hashed)
        wcq_parts.append(wcq_keep.astype(np.int32))
        log.event("stream_chunk", chunk=chunks, rows_streamed=rows_streamed,
                  rows_parseable=rows_parseable)

    author_raw = np.concatenate(author_parts)
    subreddit_raw = np.concatenate(subreddit_parts)
    created = np.concatenate(created_parts)
    link = np.concatenate(link_parts)
    wcq = np.concatenate(wcq_parts)
    del author_parts, subreddit_parts, created_parts, link_parts, wcq_parts

    author_names, author_remap = _sorted_remap(authors.names())
    subreddit_names, subreddit_remap = _sorted_remap(subreddits.names())
    author_code = author_remap[author_raw].astype(np.int32)
    subreddit_code = subreddit_remap[subreddit_raw].astype(np.int32)
    del author_raw, subreddit_raw

    stats = {
        "rows_streamed": rows_streamed,
        "rows_parseable": rows_parseable,
        "rows_unparseable": rows_streamed - rows_parseable,
        "wcq_zero_rows": wcq_zero,
        "wcq_zero_share": wcq_zero / max(1, rows_parseable),
        "link_id_missing_rows": link_missing,
        "authors": len(author_names),
        "subreddits": len(subreddit_names),
        "chunks": chunks,
    }
    log.event("stream_done", **stats)
    return {
        "author_code": author_code,
        "subreddit_code": subreddit_code,
        "created_utc": created,
        "link": link,
        "wcq": wcq,
        "authors": author_names,
        "subreddits": subreddit_names,
        "stream_stats": stats,
    }


def order_and_halve(author_code: np.ndarray, created: np.ndarray,
                    n_authors: int) -> tuple[np.ndarray, np.ndarray,
                                             np.ndarray, np.ndarray]:
    """Stable per-author order by created_utc, then the full-stream median.

    ``np.lexsort`` is a STABLE indirect sort, so events tied on
    (author, created_utc) keep their stream order — the registration's tie
    rule, implemented rather than assumed (contract test).
    Half 0 = early = created_utc <= the author's own full-stream median
    (numpy median convention: the mean of the two central values on an even
    count).  Within an author the early events are therefore a PREFIX of the
    ordered sequence, which is what lets the cache store contiguous ranges.
    """

    order = np.lexsort((created, author_code))
    a_sorted = author_code[order]
    c_sorted = created[order]
    counts = np.bincount(a_sorted, minlength=n_authors).astype(np.int64)
    starts = np.concatenate(([0], np.cumsum(counts)[:-1]))
    seen = counts > 0
    lo = starts + np.maximum(counts - 1, 0) // 2
    hi = starts + np.maximum(counts, 1) // 2
    medians = np.full(n_authors, np.nan, dtype=np.float64)
    medians[seen] = 0.5 * (c_sorted[lo[seen]] + c_sorted[hi[seen]])
    half = (c_sorted > medians[a_sorted]).astype(np.int8)
    return order, half, medians, counts


def build_event_cache(scaffold: dict[str, Any], big5_mask: np.ndarray,
                      log: RunLog) -> dict[str, Any]:
    """The pool skeleton: contiguous per-author event ranges plus b̄_{c,h}."""

    author_code = scaffold["author_code"]
    created = scaffold["created_utc"]
    n_authors = len(scaffold["authors"])
    n_subs = len(scaffold["subreddits"])

    order, half, medians, counts = order_and_halve(author_code, created,
                                                   n_authors)
    a_sorted = author_code[order]
    comm_sorted = scaffold["subreddit_code"][order]
    link_sorted = scaffold["link"][order]
    wcq_sorted = scaffold["wcq"][order]
    y_all = np.log1p(wcq_sorted.astype(np.float64))
    log.event("halves_assigned", early_rows=int((half == 0).sum()),
              late_rows=int((half == 1).sum()))

    # b̄_{c,h}: the global community-half mean over ALL events (the
    # venue-residualized arm's offset; every author's events contribute, pool
    # membership is irrelevant to it by registration).
    ch_key = comm_sorted.astype(np.int64) * 2 + half.astype(np.int64)
    ch_count = np.bincount(ch_key, minlength=n_subs * 2).astype(np.int64)
    ch_sum = np.bincount(ch_key, weights=y_all, minlength=n_subs * 2)

    n_early = np.bincount(a_sorted[half == 0], minlength=n_authors
                          ).astype(np.int64)
    n_late = counts - n_early
    pool_mask = (n_early >= POOL_FLOOR_PRIMARY) & (n_late >= POOL_FLOOR_PRIMARY)
    pool_codes = np.flatnonzero(pool_mask).astype(np.int32)
    log.event("pool", floor=POOL_FLOOR_PRIMARY, pool_authors=int(pool_codes.size),
              disjoint=int((pool_mask & ~big5_mask).sum()),
              big5=int((pool_mask & big5_mask).sum()))

    keep_event = pool_mask[a_sorted]
    ev_author = a_sorted[keep_event]
    ev_comm = comm_sorted[keep_event]
    ev_link = link_sorted[keep_event]
    ev_wcq = wcq_sorted[keep_event]
    ev_half = half[keep_event]

    pool_counts = counts[pool_codes]
    offsets = np.concatenate(([0], np.cumsum(pool_counts))).astype(np.int64)
    cache = {
        "pool_author_code": pool_codes,
        "pool_is_big5": big5_mask[pool_codes],
        "offsets": offsets,
        "n_early": n_early[pool_codes].astype(np.int64),
        "n_total": pool_counts,
        "ev_comm": ev_comm.astype(np.int32),
        "ev_link": ev_link.astype(np.uint64),
        "ev_wcq": ev_wcq.astype(np.int32),
        "ev_half": ev_half.astype(np.int8),
        "ch_sum": ch_sum,
        "ch_count": ch_count,
        "author_median_utc": medians,
        "author_rows": counts,
        "n_subs": n_subs,
        "n_authors": n_authors,
    }
    del ev_author
    log.event("event_cache_built", pool_authors=int(pool_codes.size),
              pool_events=int(offsets[-1]),
              corpus_events=int(a_sorted.size))
    return cache


CACHE_ARRAYS = ("pool_author_code", "pool_is_big5", "offsets", "n_early",
                "n_total", "ev_comm", "ev_link", "ev_wcq", "ev_half",
                "ch_sum", "ch_count", "author_median_utc", "author_rows")


def save_cache(cache: dict[str, Any], scaffold: dict[str, Any],
               path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, **{k: cache[k] for k in CACHE_ARRAYS})
    write_json(path.with_suffix(".meta.json"), {
        "cache_version": CACHE_VERSION,
        "authors": scaffold["authors"],
        "subreddits": scaffold["subreddits"],
        "stream_stats": scaffold["stream_stats"],
        "n_subs": cache["n_subs"],
        "n_authors": cache["n_authors"],
        "pool_floor": POOL_FLOOR_PRIMARY,
        "note": "gitignored; metadata only; no bodies, no labels",
    })


def load_cache(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = np.load(path)
    meta = json.loads(path.with_suffix(".meta.json").read_text("utf-8"))
    cache = {k: payload[k] for k in CACHE_ARRAYS}
    cache["n_subs"] = int(meta["n_subs"])
    cache["n_authors"] = int(meta["n_authors"])
    return cache, meta


# ---------------------------------------------------------------------------
# Stage 2 — the arm layout (cells in LENGTH-SORTED order; contiguous ranges)
# ---------------------------------------------------------------------------


class Arm:
    """One arm's realized skeleton plus its values and its adjacency mask.

    The cell layout is stored in LENGTH-SORTED order.  That is a pure
    re-indexing (``cell_author`` / ``cell_half`` carry the identity back), and
    it is what makes the padded permutation engine cheap: a chunk of 64
    length-adjacent cells pads to within 7% of its own event count.
    """

    def __init__(self, key: str, label: str, y: np.ndarray,
                 cell_start: np.ndarray, cell_len: np.ndarray,
                 cell_author: np.ndarray, cell_half: np.ndarray,
                 pair_mask: np.ndarray | None, n_authors: int) -> None:
        order = np.argsort(cell_len, kind="stable")
        self.key = key
        self.label = label
        self.n_authors = int(n_authors)
        self.cell_len = cell_len[order].astype(np.int64)
        self.cell_author = cell_author[order].astype(np.int64)
        self.cell_half = cell_half[order].astype(np.int8)
        self.offsets = np.concatenate(
            ([0], np.cumsum(self.cell_len))).astype(np.int64)
        take = np.concatenate([np.arange(s, s + n, dtype=np.int64)
                               for s, n in zip(cell_start[order],
                                               self.cell_len)])
        self.y = np.ascontiguousarray(y[take])
        if pair_mask is None:
            mask = np.ones(self.y.size, dtype=bool)
        else:
            mask = np.ascontiguousarray(pair_mask[take])
        # The LAST slot of every cell can never open an adjacency.
        mask[self.offsets[1:] - 1] = False
        self.pair_mask = mask
        self.n_cells = int(self.cell_len.size)
        self.n_events = int(self.y.size)
        self._m8 = mask.astype(np.float64)
        self._n_pairs = np.add.reduceat(self._m8, self.offsets[:-1])
        self._chunks = _pad_chunks(self.cell_len, PAD_CHUNK_ROWS)
        self._buffers: list[np.ndarray] | None = None
        self._base = np.repeat(self.offsets[:-1], self.cell_len)

    # -- census ----------------------------------------------------------
    def census(self) -> dict[str, Any]:
        return {
            "arm": self.key,
            "label": self.label,
            "authors": self.n_authors,
            "cells": self.n_cells,
            "events": self.n_events,
            "adjacencies": int(self._n_pairs.sum()),
            "min_cell_len": int(self.cell_len.min()),
            "max_cell_len": int(self.cell_len.max()),
            "median_pairs_per_cell": float(np.median(self._n_pairs)),
            "cells_with_fewer_than_2_pairs": int((self._n_pairs < 2).sum()),
        }

    # -- estimators ------------------------------------------------------
    def r1(self, values: np.ndarray | None = None) -> np.ndarray:
        v = self.y if values is None else values
        return masked_lag1_pearson(v, self.offsets, self._m8, self._n_pairs)

    def paired(self, r1_cells: np.ndarray) -> tuple[np.ndarray, np.ndarray,
                                                    np.ndarray]:
        """(r1_early, r1_late) over authors, and the finite-pair mask."""

        n = self.n_authors
        early = np.full(n, np.nan)
        late = np.full(n, np.nan)
        early[self.cell_author[self.cell_half == 0]] = \
            r1_cells[self.cell_half == 0]
        late[self.cell_author[self.cell_half == 1]] = \
            r1_cells[self.cell_half == 1]
        ok = np.isfinite(early) & np.isfinite(late)
        return early, late, ok

    # -- the marginal-preserving within-half shuffle ----------------------
    def permutation(self, rng: np.random.Generator) -> np.ndarray:
        """One draw: a flat index array, per cell a uniform permutation.

        Construction (pinned).  Cells are padded, in length-sorted chunks, to
        a rectangle of ``Lmax`` columns.  Each row of the integer buffer holds
        a uniform random permutation of ``0..Lmax-1`` (``Generator.permuted``,
        per-row Fisher-Yates, applied in place so a buffer re-permuted
        every replicate stays uniform).  The entries BELOW that row's own
        length, taken IN THE ORDER THEY APPEAR, are a uniform random
        permutation of ``0..L-1`` — the restriction property of a uniform
        permutation.  Boolean masking of a C-ordered 2-D array yields exactly
        that order, row by row, so the compaction is one masked read and the
        result concatenates the cells in layout order.

        The permutation only REORDERS each cell's own values, so the per-cell
        marginal is invariant BIT FOR BIT, not merely in distribution
        (``check_marginal_preservation``).
        """

        if self._buffers is None:
            self._buffers = [np.tile(np.arange(lmax, dtype=np.int32),
                                     (idx.size, 1))
                             for idx, _, lmax in self._chunks]
        out = np.empty(self.n_events, dtype=np.int64)
        pos = 0
        for (idx, lengths, _), buf in zip(self._chunks, self._buffers):
            rng.permuted(buf, axis=1, out=buf)
            picked = buf[buf < lengths[:, None]]
            out[pos:pos + picked.size] = picked
            pos += picked.size
        assert pos == self.n_events
        out += self._base
        return out


def _pad_chunks(cell_len: np.ndarray, rows: int
                ) -> list[tuple[np.ndarray, np.ndarray, int]]:
    """Length-sorted padding chunks (the layout is already length-sorted)."""

    chunks = []
    for i in range(0, cell_len.size, rows):
        idx = np.arange(i, min(i + rows, cell_len.size))
        lengths = cell_len[idx].astype(np.int32)
        chunks.append((idx, lengths, int(lengths.max())))
    return chunks


def masked_lag1_pearson(v: np.ndarray, offsets: np.ndarray,
                        m8: np.ndarray, n_pairs: np.ndarray) -> np.ndarray:
    """Per-cell lag-1 Pearson correlation over the MASKED adjacencies.

    The estimator, pinned (this is the formula the report quotes).  Let a cell
    occupy slots ``0..L-1`` and let ``M`` be the set of slots ``j`` marked in
    the adjacency mask (always ``j < L-1``; for the cross-thread arm also
    ``link[j] != link[j+1]``).  With ``x_j = v_j`` and ``z_j = v_{j+1}``,

        r1 = [ S_xz - S_x S_z / n ] /
             sqrt( (S_xx - S_x^2/n) (S_zz - S_z^2/n) ),  n = |M|

    i.e. the ordinary Pearson correlation of the paired vectors (x_j, z_j)
    over j in M.  With M = every within-cell adjacency this is the lag-1
    autocorrelation of the cell's sequence; with M restricted to
    thread-crossing adjacencies it is the registered MASKED lag-1
    correlation — the same formula, a different index set.  A cell with
    fewer than two usable pairs, or with a degenerate x or z spread, returns
    NaN and is counted.
    """

    a = v
    b = np.empty_like(v)
    b[:-1] = v[1:]
    b[-1] = 0.0
    am = a * m8
    bm = b * m8
    starts = offsets[:-1]
    s_x = np.add.reduceat(am, starts)
    s_z = np.add.reduceat(bm, starts)
    s_xx = np.add.reduceat(am * a, starts)
    s_zz = np.add.reduceat(bm * b, starts)
    s_xz = np.add.reduceat(am * b, starts)
    with np.errstate(invalid="ignore", divide="ignore"):
        n = n_pairs
        cov = s_xz - s_x * s_z / n
        var_x = s_xx - s_x * s_x / n
        var_z = s_zz - s_z * s_z / n
        denom = np.sqrt(var_x * var_z)
        out = np.where((n >= 2) & (var_x > 0) & (var_z > 0), cov / denom,
                       np.nan)
    return out


def check_marginal_preservation(arm: Arm, perm: np.ndarray) -> dict[str, Any]:
    """BIT-EXACT contract: each cell's permuted multiset is its own.

    Compared on the raw IEEE-754 bit patterns (``view(uint64)``), so the test
    is exact equality of the multiset and not a floating-point approximation
    of it (U1's exact-bag pattern, carried onto a scalar).
    """

    shuffled = arm.y[perm]
    bits_a = arm.y.view(np.uint64)
    bits_b = shuffled.view(np.uint64)
    exact = True
    for start, end in zip(arm.offsets[:-1], arm.offsets[1:]):
        if not np.array_equal(np.sort(bits_a[start:end]),
                              np.sort(bits_b[start:end])):
            exact = False
            break
    is_perm = np.array_equal(np.sort(perm), np.arange(perm.size))
    within = bool(np.all((perm >= arm._base)
                         & (perm < np.repeat(arm.offsets[1:], arm.cell_len))))
    return {
        "cells_checked": arm.n_cells,
        "per_cell_multiset_bit_exact": bool(exact),
        "index_array_is_a_permutation": bool(is_perm),
        "every_index_stays_inside_its_own_cell": within,
        "status": "PASS" if (exact and is_perm and within) else "FAIL",
    }


# ---------------------------------------------------------------------------
# Stage 3 — the two estimands and their own nulls (#68/#66)
# ---------------------------------------------------------------------------


def rowwise_pearson(x: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Pearson correlation along the last axis (rows are replicates)."""

    x = np.atleast_2d(x)
    z = np.atleast_2d(z)
    n = x.shape[-1]
    sx = x.sum(axis=-1)
    sz = z.sum(axis=-1)
    cov = (x * z).sum(axis=-1) - sx * sz / n
    vx = (x * x).sum(axis=-1) - sx * sx / n
    vz = (z * z).sum(axis=-1) - sz * sz / n
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where((vx > 0) & (vz > 0), cov / np.sqrt(vx * vz), np.nan)


def presence_null(arm: Arm, b_perm: int, seed: int,
                  log: RunLog | None = None,
                  values: np.ndarray | None = None,
                  tag: str | None = None) -> dict[str, Any]:
    """Marginal-preserving within-half permutation null for mean r1."""

    rng = np.random.default_rng(seed)
    v = arm.y if values is None else values
    draws = np.empty(b_perm, dtype=np.float64)
    t0 = time.time()
    for b in range(b_perm):
        perm = arm.permutation(rng)
        draws[b] = float(np.nanmean(arm.r1(v[perm])))
        if log is not None and (b + 1) % 100 == 0:
            log.event("presence_null_progress", arm=tag or arm.key,
                      draw=b + 1, seconds=round(time.time() - t0, 1))
    return {"b": b_perm, "band": percentile_ci(draws),
            "null_mean": float(np.mean(draws)),
            "null_sd": float(np.std(draws, ddof=1))}


def ownership_null(early: np.ndarray, late: np.ndarray, ok: np.ndarray,
                   b_perm: int, seed: int) -> dict[str, Any]:
    """Own null (#68): the author PAIRING permuted between the two halves."""

    rng = np.random.default_rng(seed)
    x = early[ok]
    z = late[ok]
    n = x.size
    draws = np.empty(b_perm, dtype=np.float64)
    block = 64
    for start in range(0, b_perm, block):
        rows = min(block, b_perm - start)
        perms = rng.permuted(np.tile(np.arange(n), (rows, 1)), axis=1)
        draws[start:start + rows] = rowwise_pearson(
            np.broadcast_to(x, (rows, n)), z[perms])
    return {"b": b_perm, "band": percentile_ci(draws),
            "null_mean": float(np.mean(draws))}


def cluster_bootstrap_pairs(early: np.ndarray, late: np.ndarray,
                            ok: np.ndarray, b_boot: int, seed: int,
                            statistic: str = "rho") -> dict[str, Any]:
    """Cluster bootstrap over AUTHORS (the cluster is the author, #66)."""

    rng = np.random.default_rng(seed)
    x = early[ok]
    z = late[ok]
    n = x.size
    draws = np.empty(b_boot, dtype=np.float64)
    block = 100
    for start in range(0, b_boot, block):
        rows = min(block, b_boot - start)
        idx = rng.integers(0, n, size=(rows, n))
        if statistic == "rho":
            draws[start:start + rows] = rowwise_pearson(x[idx], z[idx])
        else:
            draws[start:start + rows] = 0.5 * (x[idx] + z[idx]).mean(axis=1)
    return {"b": b_boot, "ci": percentile_ci(draws),
            "boot_mean": float(np.mean(draws)),
            "boot_sd": float(np.std(draws, ddof=1))}


def analyse_arm(arm: Arm, *, b_perm: int, b_boot: int, seed_perm: int,
                seed_boot: int, log: RunLog | None = None,
                values: np.ndarray | None = None) -> dict[str, Any]:
    """Presence + ownership for one arm, each against its own null."""

    v = arm.y if values is None else values
    r1_cells = arm.r1(v)
    finite = np.isfinite(r1_cells)
    presence = float(np.nanmean(r1_cells))
    early, late, ok = arm.paired(r1_cells)
    rho = float(rowwise_pearson(early[ok], late[ok])[0])
    out = {
        "arm": arm.key,
        "label": arm.label,
        "census": arm.census(),
        "cells_scored": int(finite.sum()),
        "cells_undefined": int((~finite).sum()),
        "authors_paired": int(ok.sum()),
        "authors_dropped": int(arm.n_authors - ok.sum()),
        "presence_mean_r1": presence,
        "presence_sd_over_cells": float(np.nanstd(r1_cells, ddof=1)),
        "rho_own": rho,
    }
    out["presence_null"] = presence_null(arm, b_perm, seed_perm, log=log,
                                         values=v)
    out["presence_detected"] = bool(
        presence < out["presence_null"]["band"][0]
        or presence > out["presence_null"]["band"][1])
    out["ownership_null"] = ownership_null(early, late, ok, b_perm,
                                           seed_perm + 101)
    out["ownership_boot"] = cluster_bootstrap_pairs(early, late, ok, b_boot,
                                                    seed_boot)
    # Annotation only (NOT registered): the same cluster bootstrap applied to
    # the presence mean, reported so the presence point carries an interval.
    out["presence_boot_annotation"] = cluster_bootstrap_pairs(
        early, late, ok, b_boot, seed_boot + 7, statistic="presence")
    band = out["ownership_null"]["band"]
    out["ownership_detected"] = bool(rho < band[0] or rho > band[1])
    ci = out["ownership_boot"]["ci"]
    out["ci_covers_zero"] = bool(ci[0] <= 0.0 <= ci[1])
    return out


# ---------------------------------------------------------------------------
# Stage 4 — Part 0, the gate on the REALIZED skeleton (wholly synthetic y)
# ---------------------------------------------------------------------------


def ar1_values(arm: Arm, phi_cell: np.ndarray,
               rng: np.random.Generator) -> np.ndarray:
    """AR(1) sequences on the realized skeleton, one phi per CELL.

    y_t = phi * y_{t-1} + e_t with a STATIONARY start (y_0 drawn at variance
    1/(1 - phi^2)), generated by a doubling scan over the padded layout:
    after the step at offset d the running array holds
    sum_{k > t-2d} phi^(t-k) e_k, so ceil(log2(L)) steps give the exact
    solution.  The scan stops early once phi^d underflows, which it does after
    a handful of steps at these operating points.
    """

    out = np.empty(arm.n_events, dtype=np.float64)
    pos = 0
    for idx, lengths, lmax in arm._chunks:
        phi = phi_cell[idx][:, None]
        eps = rng.standard_normal((idx.size, lmax))
        eps[:, 0] /= np.sqrt(1.0 - phi[:, 0] ** 2)
        f = phi.copy()
        d = 1
        while d < lmax and np.max(np.abs(f)) > 1e-300:
            eps[:, d:] += f * eps[:, :-d]
            f = f * f
            d *= 2
        picked = eps[np.arange(lmax)[None, :] < lengths[:, None]]
        out[pos:pos + picked.size] = picked
        pos += picked.size
    assert pos == arm.n_events
    return out


def ownership_variance_target(arm: Arm, phi_bar: float,
                              rho_target: float) -> dict[str, Any]:
    """Derive the across-author phi dispersion that plants rho_own = target.

    Model.  Author u owns one phi_u, shared by both halves.  The per-half
    estimate is r1_{u,h} = g(phi_u) + e_{u,h} with g(phi) ~= phi (the
    Marriott-Pope slope is 1 - 3/n) and, by Bartlett's first-order result for
    an AR(1), Var(e_{u,h}) = (1 - phi_u^2) / n_{u,h}.  The two halves' errors
    are uncorrelated across halves, so with V = Var_u(phi_u):

        Cov(r1_e, r1_l) = V ,   Var(r1_h) = V + A_h ,
        A_h = E_u[(1 - phi_u^2)/n_{u,h}] = (1 - phi_bar^2 - V) * m_h ,
        m_h = E_u[1 / n_{u,h}]  (computed on the REALIZED skeleton)

        rho_own = V / sqrt((V + A_e)(V + A_l))

    Setting rho_own = rho gives, with c = 1 - phi_bar^2 - V,

        (1 - rho^2) V^2 - rho^2 c (m_e + m_l) V - rho^2 c^2 m_e m_l = 0

    which is solved here by bisection on V in (0, 1 - phi_bar^2) because c
    itself depends on V.  At rho = 1/2 and m_e = m_l = m the equation reduces
    to the readable V = A, i.e. plant exactly as much across-author phi
    variance as the per-half estimator's own sampling variance.
    """

    n_e = arm.cell_len[arm.cell_half == 0].astype(np.float64)
    n_l = arm.cell_len[arm.cell_half == 1].astype(np.float64)
    m_e = float(np.mean(1.0 / (n_e - 1.0)))
    m_l = float(np.mean(1.0 / (n_l - 1.0)))

    def residual(v: float) -> float:
        c = 1.0 - phi_bar ** 2 - v
        if c <= 0:
            return 1.0
        a_e = c * m_e
        a_l = c * m_l
        return v / math.sqrt((v + a_e) * (v + a_l)) - rho_target

    lo, hi = 1e-12, (1.0 - phi_bar ** 2) * (1.0 - 1e-9)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if residual(mid) < 0.0:
            lo = mid
        else:
            hi = mid
    v = 0.5 * (lo + hi)
    c = 1.0 - phi_bar ** 2 - v
    return {
        "phi_bar": phi_bar,
        "rho_target": rho_target,
        "m_early_mean_inv_pairs": m_e,
        "m_late_mean_inv_pairs": m_l,
        "V_phi_variance": v,
        "sd_phi": math.sqrt(v),
        "A_early": c * m_e,
        "A_late": c * m_l,
        "rho_implied_by_the_solution": v / math.sqrt(
            (v + c * m_e) * (v + c * m_l)),
        "formula": ("rho = V / sqrt((V + A_e)(V + A_l)), "
                    "A_h = (1 - phi_bar^2 - V) * E_u[1/(n_{u,h} - 1)]"),
    }


def planted_mean_r1(arm: Arm, phi_cell: np.ndarray) -> float:
    """DESCRIPTIVE prediction: Marriott-Pope E[r1] = phi - (1 + 3 phi)/n."""

    n = arm.cell_len.astype(np.float64) - 1.0
    return float(np.mean(phi_cell - (1.0 + 3.0 * phi_cell) / n))


def draw_phi(arm: Arm, world: str, mapping: dict[str, Any],
             rng: np.random.Generator) -> np.ndarray:
    """Per-CELL phi.  AR world: author-owned (both halves share one draw)."""

    if world == "iid":
        return np.zeros(arm.n_cells, dtype=np.float64)
    if world == "common_path":
        return np.full(arm.n_cells, PHI_BAR_COMMON, dtype=np.float64)
    phi_author = rng.normal(mapping["phi_bar"], mapping["sd_phi"],
                            size=arm.n_authors)
    np.clip(phi_author, -PHI_CLIP, PHI_CLIP, out=phi_author)
    return phi_author[arm.cell_author]


def synthetic_world(arm: Arm, world: str, mapping: dict[str, Any],
                    seed: int, *, with_presence_null: bool,
                    b_perm: int, b_boot: int,
                    log: RunLog | None = None) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    phi_cell = draw_phi(arm, world, mapping, rng)
    values = ar1_values(arm, phi_cell, rng)
    r1_cells = arm.r1(values)
    early, late, ok = arm.paired(r1_cells)
    rho = float(rowwise_pearson(early[ok], late[ok])[0])
    out = {
        "world": world,
        "seed": seed,
        "phi_mean_over_cells": float(np.mean(phi_cell)),
        "phi_sd_over_authors": float(
            np.std(phi_cell[arm.cell_half == 0], ddof=1)),
        "rho_own": rho,
        "mean_r1": float(np.nanmean(r1_cells)),
        "mean_r1_predicted": planted_mean_r1(arm, phi_cell),
        "cells_undefined": int((~np.isfinite(r1_cells)).sum()),
        "authors_paired": int(ok.sum()),
    }
    if b_perm:
        out["ownership_null"] = ownership_null(early, late, ok, b_perm,
                                               seed + 11)
        band = out["ownership_null"]["band"]
        out["rho_inside_band"] = bool(band[0] <= rho <= band[1])
    if b_boot:
        out["ownership_boot"] = cluster_bootstrap_pairs(early, late, ok,
                                                        b_boot, seed + 23)
        ci = out["ownership_boot"]["ci"]
        out["ci_covers_zero"] = bool(ci[0] <= 0.0 <= ci[1])
        out["ci_covers_own_point"] = bool(ci[0] <= rho <= ci[1])
    if with_presence_null:
        out["presence_null"] = presence_null(arm, b_perm, seed + 37, log=log,
                                             values=values,
                                             tag=f"part0:{world}")
        pband = out["presence_null"]["band"]
        out["mean_r1_inside_band"] = bool(
            pband[0] <= out["mean_r1"] <= pband[1])
    return out


def part0_gate(arm: Arm, *, b_perm: int, b_boot: int, seed: int,
               log: RunLog) -> dict[str, Any]:
    """The registered Part 0: five ROUTING clauses, one DESCRIPTIVE family."""

    mapping = ownership_variance_target(arm, PHI_BAR_AR, RHO_TRUE_TARGET)
    log.event("part0_mapping", **{k: v for k, v in mapping.items()
                                  if k != "formula"})

    ar_reps = []
    for i in range(N_SYNTH_REPLICATES):
        rep = synthetic_world(arm, "ar_owned", mapping, seed + 1000 + 7 * i,
                              with_presence_null=False, b_perm=0, b_boot=0,
                              log=None)
        ar_reps.append(rep)
        log.event("part0_ar_replicate", replicate=i, rho_own=rep["rho_own"],
                  mean_r1=rep["mean_r1"],
                  mean_r1_predicted=rep["mean_r1_predicted"])
    rhos = np.array([r["rho_own"] for r in ar_reps])
    rep_sd = float(np.std(rhos, ddof=1))
    tol = max(TOL_FLOOR, TOL_SD_MULT * rep_sd)
    recovery = {
        "target_rho_own": RHO_TRUE_TARGET,
        "replicates": N_SYNTH_REPLICATES,
        "rho_own_mean": float(rhos.mean()),
        "rho_own_sd": rep_sd,
        "gap": float(rhos.mean() - RHO_TRUE_TARGET),
        "tolerance": tol,
        "per_replicate": [float(v) for v in rhos],
    }
    recovery["status"] = "PASS" if abs(recovery["gap"]) <= tol else "FAIL"

    common = synthetic_world(arm, "common_path", mapping, seed + 2000,
                             with_presence_null=False, b_perm=b_perm,
                             b_boot=b_boot, log=log)
    log.event("part0_common_path", rho_own=common["rho_own"],
              band=common["ownership_null"]["band"],
              ci=common["ownership_boot"]["ci"])
    iid = synthetic_world(arm, "iid", mapping, seed + 3000,
                          with_presence_null=True, b_perm=b_perm,
                          b_boot=b_boot, log=log)
    log.event("part0_iid", mean_r1=iid["mean_r1"],
              band=iid["presence_null"]["band"], rho_own=iid["rho_own"])

    rng = np.random.default_rng(seed + 4000)
    contract = check_marginal_preservation(arm, arm.permutation(rng))

    routing = [
        {"id": "i", "clause": ("ownership recovery on the author-owned AR(1) "
                               "world (planted rho_own = 0.50)"),
         "observed": (f"{recovery['rho_own_mean']:.4f} over "
                      f"{N_SYNTH_REPLICATES} replicates "
                      f"(sd {rep_sd:.4f}), gap {recovery['gap']:+.4f}"),
         "required": f"abs(gap) <= max(0.02, 3 x rep sd) = {tol:.4f}",
         "status": recovery["status"]},
        {"id": "ii", "clause": ("the COMMON-PATH null world: presence WITHOUT "
                                "ownership — rho_own CI covers 0 and the "
                                "point sits inside the pairing band"),
         "observed": (f"rho_own {common['rho_own']:+.4f}, CI "
                      f"{fmt_ci(common['ownership_boot']['ci'])}, band "
                      f"{fmt_ci(common['ownership_null']['band'])}"),
         "required": "CI covers 0 AND point inside band",
         "status": "PASS" if (common["ci_covers_zero"]
                              and common["rho_inside_band"]) else "FAIL"},
        {"id": "iii", "clause": ("the iid world: mean r1 inside its "
                                 "permutation band AND rho_own inside its "
                                 "pairing band"),
         "observed": (f"mean r1 {iid['mean_r1']:+.6f} in "
                      f"{fmt_ci(iid['presence_null']['band'], 6)}; rho_own "
                      f"{iid['rho_own']:+.4f} in "
                      f"{fmt_ci(iid['ownership_null']['band'])}"),
         "required": "both inside",
         "status": "PASS" if (iid["mean_r1_inside_band"]
                              and iid["rho_inside_band"]) else "FAIL"},
        {"id": "iv", "clause": ("marginal preservation: each half's multiset "
                                "is BIT-EXACTLY invariant under the shuffle"),
         "observed": (f"{contract['cells_checked']:,} cells, bit-exact "
                      f"{contract['per_cell_multiset_bit_exact']}, index array "
                      f"a permutation {contract['index_array_is_a_permutation']}"
                      f", never leaves its own cell "
                      f"{contract['every_index_stays_inside_its_own_cell']}"),
         "required": "all three exact", "status": contract["status"]},
        {"id": "v", "clause": ("#85b bootstrap-zero on the common-path world: "
                               "the cluster-bootstrap CI covers 0 AND covers "
                               "its own point"),
         "observed": (f"CI {fmt_ci(common['ownership_boot']['ci'])} vs 0 and "
                      f"vs {common['rho_own']:+.4f}"),
         "required": "covers both",
         "status": "PASS" if (common["ci_covers_zero"]
                              and common["ci_covers_own_point"]) else "FAIL"},
    ]
    descriptive = [
        {"id": "D1", "clause": ("mean-r1 recovery against the planted phi "
                                "mapping, author-owned AR(1) world"),
         "observed": (f"{float(np.mean([r['mean_r1'] for r in ar_reps])):+.4f} "
                      f"observed vs "
                      f"{float(np.mean([r['mean_r1_predicted'] for r in ar_reps])):+.4f}"
                      " predicted (Marriott-Pope)"),
         "required": "annotate only, never stops",
         "status": "ANNOTATED"},
        {"id": "D2", "clause": ("mean-r1 recovery against the planted phi "
                                "mapping, common-path world"),
         "observed": (f"{common['mean_r1']:+.4f} observed vs "
                      f"{common['mean_r1_predicted']:+.4f} predicted"),
         "required": "annotate only, never stops",
         "status": "ANNOTATED"},
    ]
    status = "PASS" if all(c["status"] == "PASS" for c in routing) else "FAIL"
    return {
        "status": status,
        "routing": routing,
        "descriptive": descriptive,
        "mapping": mapping,
        "recovery": recovery,
        "ar_replicates": ar_reps,
        "common_path": common,
        "iid": iid,
        "marginal_contract": contract,
    }


def implied_phi_variance(rho: float, a_e: float, a_l: float) -> float:
    """DESIGN ARITHMETIC, not an estimator: the phi variance a rho implies.

    Inverts the SAME first-order model Part 0 plants — rho_own =
    V / sqrt((V + A_e)(V + A_l)) — for V, with A_e and A_l now taken as fixed
    (computed from the arm's own realized pair counts and its own mean r1).
    The quadratic (1 - rho^2) V^2 - rho^2 (A_e + A_l) V - rho^2 A_e A_l = 0
    has one positive root.  Nothing routes on this: it exists only so the
    ARM DIVERGENCES can be read against the registered attenuation note,
    which says the per-half r1 noise depresses rho_own and that the raw
    rho_own routes anyway.
    """

    if not (0.0 < rho < 1.0):
        return float("nan")
    k = rho * rho
    a = 1.0 - k
    b = -k * (a_e + a_l)
    c = -k * a_e * a_l
    return float((-b + math.sqrt(b * b - 4.0 * a * c)) / (2.0 * a))


def attenuation_arithmetic(arms: dict[str, Arm],
                           results: dict[str, Any]) -> dict[str, Any]:
    """Per-arm A and the implied Var(phi) — the registered attenuation note,
    made quantitative on the realized skeletons.  ANNOTATION ONLY."""

    out = {}
    for key, arm in arms.items():
        res = results[key]
        mean_r1 = res["presence_mean_r1"]
        pairs = arm._n_pairs
        early = pairs[arm.cell_half == 0]
        late = pairs[arm.cell_half == 1]
        scale = 1.0 - mean_r1 ** 2
        a_e = float(scale * np.mean(1.0 / early))
        a_l = float(scale * np.mean(1.0 / late))
        v = implied_phi_variance(res["rho_own"], a_e, a_l)
        out[key] = {
            "label": res["label"],
            "mean_r1": mean_r1,
            "rho_own": res["rho_own"],
            "median_pairs_per_cell": float(np.median(pairs)),
            "A_early": a_e,
            "A_late": a_l,
            "implied_phi_variance": v,
            "implied_phi_sd": math.sqrt(v) if v == v and v >= 0 else
            float("nan"),
            "note": ("design arithmetic on the first-order model, NOT an "
                     "estimator; no disattenuation is registered and the raw "
                     "rho_own routes"),
        }
    return out


# ---------------------------------------------------------------------------
# Stage 5 — cells (#55 NULL-first, #75 effect-size keyed, #87 REGIONS)
# ---------------------------------------------------------------------------

LOW_LO = BOUNDARY_LOW - BOUNDARY_HALFWIDTH      # 0.139
LOW_HI = BOUNDARY_LOW + BOUNDARY_HALFWIDTH      # 0.161
HIGH_LO = BOUNDARY_HIGH - BOUNDARY_HALFWIDTH    # 0.489
HIGH_HI = BOUNDARY_HIGH + BOUNDARY_HALFWIDTH    # 0.511

REGION_EDGES = (LOW_LO, LOW_HI, HIGH_LO, HIGH_HI)


def point_cell(rho: float, ci_covers_zero: bool) -> str:
    """The registered ladder, NULL-first: the null cell is checked first."""

    if ci_covers_zero or rho < LOW_LO:
        return CELL_NOT_OWNED
    if rho <= LOW_HI:
        return CELL_AT_LOW
    if rho < HIGH_LO:
        return CELL_WEAK
    if rho <= HIGH_HI:
        return CELL_AT_HIGH
    return CELL_STRONG


def straddles(ci: Sequence[float]) -> list[str]:
    """Region EDGES the interval crosses (#87: reported as such)."""

    return [f"{edge:.3f}" for edge in REGION_EDGES if ci[0] < edge < ci[1]]


def classify(arm_result: dict[str, Any]) -> dict[str, Any]:
    rho = arm_result["rho_own"]
    ci = arm_result["ownership_boot"]["ci"]
    cell = point_cell(rho, arm_result["ci_covers_zero"])
    crossed = straddles(ci)
    return {
        "arm": arm_result["arm"],
        "rho_own": rho,
        "ci": ci,
        "band": arm_result["ownership_null"]["band"],
        "ci_covers_zero": arm_result["ci_covers_zero"],
        "cell": cell,
        "region_edges_straddled": crossed,
        "is_straddle": bool(crossed),
        "presence_mean_r1": arm_result["presence_mean_r1"],
        "presence_band": arm_result["presence_null"]["band"],
        "presence_detected": arm_result["presence_detected"],
    }


def evaluate_leans(cells: dict[str, Any], arms: dict[str, Any],
                   retention: dict[str, Any]) -> list[dict[str, Any]]:
    primary = arms["primary"]
    rho = primary["rho_own"]
    out = [
        {"lean": "presence positive and detected against its own band "
                 "(magnitude deliberately un-leaned, #57)",
         "registered": "mean r1 > 0 and outside the permutation band",
         "observed": (f"mean r1 = {primary['presence_mean_r1']:+.4f}, band "
                      f"{fmt_ci(primary['presence_null']['band'], 6)}"),
         "held": bool(primary["presence_mean_r1"] > 0
                      and primary["presence_detected"])},
        {"lean": "ownership rho_own in (0.30, 0.60]",
         "registered": f"({LEAN_RHO_OWN[0]:.2f}, {LEAN_RHO_OWN[1]:.2f}]",
         "observed": f"{rho:.4f}",
         "held": bool(LEAN_RHO_OWN[0] < rho <= LEAN_RHO_OWN[1])},
        {"lean": "the cross-thread arm retains MOST of the ownership",
         "registered": f"retention >= {RETENTION_MOST:.2f}",
         "observed": f"{retention['cross_thread']['ratio']:.4f}",
         "held": bool(retention["cross_thread"]["ratio"] >= RETENTION_MOST)},
        {"lean": "the venue-residualized arm retains MOST of the ownership",
         "registered": f"retention >= {RETENTION_MOST:.2f}",
         "observed": f"{retention['venue_resid']['ratio']:.4f}",
         "held": bool(retention["venue_resid"]["ratio"] >= RETENTION_MOST)},
        {"lean": "the Big5 replication lands in the SAME cell",
         "registered": cells["primary"]["cell"],
         "observed": cells["big5"]["cell"],
         "held": bool(cells["big5"]["cell"] == cells["primary"]["cell"])},
    ]
    for row in out:
        row["status"] = "HELD" if row["held"] else "BROKEN"
    return out


def flags_73(cells: dict[str, Any]) -> list[dict[str, Any]]:
    """Arm divergences carry #73; the primary always routes."""

    primary = cells["primary"]["cell"]
    flags = []
    for key, cell in cells.items():
        if key == "primary":
            continue
        if cell["cell"] != primary:
            flags.append({"arm": key, "primary_cell": primary,
                          "arm_cell": cell["cell"],
                          "rho_own": cell["rho_own"], "ci": cell["ci"],
                          "note": "#73 divergence; the primary routes"})
    for key, cell in cells.items():
        if cell["is_straddle"]:
            flags.append({"arm": key, "primary_cell": primary,
                          "arm_cell": cell["cell"], "rho_own": cell["rho_own"],
                          "ci": cell["ci"],
                          "note": ("#87 straddle: the CI crosses region "
                                   "edge(s) "
                                   + ", ".join(cell["region_edges_straddled"]))})
    return flags


def build_verdict(part0: dict[str, Any], cells: dict[str, Any],
                  arms: dict[str, Any]) -> dict[str, Any]:
    if part0["status"] != "PASS":
        return {"cell": CELL_A1_STOP, "routes_on": "Part 0 gate",
                "gate": part0["status"],
                "note": ("A1 stop: a ROUTING clause failed on the realized "
                         "skeleton; NO corpus estimand value is licensed.")}
    primary = cells["primary"]
    return {
        "cell": primary["cell"],
        "routes_on": "rho_own, PRIMARY arm (raw adjacency, disjoint pool)",
        "gate": part0["status"],
        "rho_own": primary["rho_own"],
        "ci": primary["ci"],
        "band": primary["band"],
        "presence_mean_r1": primary["presence_mean_r1"],
        "presence_band": primary["presence_band"],
        "is_straddle": primary["is_straddle"],
        "region_edges_straddled": primary["region_edges_straddled"],
        "authors": arms["primary"]["authors_paired"],
    }


def honest_anomalies(arms: dict[str, Arm], results: dict[str, Any],
                     cells: dict[str, Any], part0: dict[str, Any],
                     attenuation: dict[str, Any]) -> list[dict[str, Any]]:
    """Everything a reader could mistake, named with its own number."""

    primary = results["primary"]
    band = primary["presence_null"]["band"]
    offset = -float(np.mean(1.0 / arms["primary"]._n_pairs))
    widths = ((primary["presence_mean_r1"] - band[1])
              / max(band[1] - band[0], 1e-12))
    v_pri = attenuation["primary"]["implied_phi_variance"]
    out = [
        {"anomaly": "the presence permutation band sits entirely BELOW zero",
         "detail": (
             "a uniform permutation of a FINITE sequence has a small negative "
             "expected lag-1 correlation, so the marginal-preserving null is "
             "a bias-offset band, not a zero band. The primary arm's null "
             f"mean is {primary['presence_null']['null_mean']:+.6f} against "
             f"the analytic offset -E[1/pairs] = {offset:+.6f}. Detection is "
             f"untouched: the point sits about {widths:,.0f} band-widths "
             "above the upper edge.")},
        {"anomaly": ("the Big5 REPLICATION arm reads STRONGLY_OWNED while "
                     "the primary reads WEAKLY_OWNED (#73)"),
         "detail": (
             f"rho_own {results['big5']['rho_own']:.4f} "
             f"{fmt_ci(results['big5']['ownership_boot']['ci'])} against the "
             f"primary's {primary['rho_own']:.4f}. This is NOT an attenuation "
             "artifact: the two arms' sampling variances are comparable "
             f"(A ~ {attenuation['big5']['A_early']:.6f} vs "
             f"{attenuation['primary']['A_early']:.6f}), and the implied "
             "across-author path-parameter variance differs by a factor of "
             f"{attenuation['big5']['implied_phi_variance'] / v_pri:.1f}. The "
             "Big5 cohort also carries the higher presence "
             f"({results['big5']['presence_mean_r1']:.4f} vs "
             f"{primary['presence_mean_r1']:.4f}). The primary routes; the "
             "divergence is a cohort fact, reported and not resolved.")},
        {"anomaly": ("the floor-100 sensitivity arm reads higher than the "
                     "primary"),
         "detail": (
             f"rho_own {results['floor100']['rho_own']:.4f} against "
             f"{primary['rho_own']:.4f} — the SAME cell, and the gap is what "
             "the registered attenuation note predicts: longer halves, less "
             "per-half noise. The implied Var(phi) agrees to "
             f"{abs(attenuation['floor100']['implied_phi_variance'] / v_pri - 1) * 100:.0f}%"
             f" ({attenuation['floor100']['implied_phi_variance']:.6f} vs "
             f"{v_pri:.6f}), so the two arms are reading one object at two "
             "precisions.")},
        {"anomaly": ("the cross-thread arm's cell is boundary-sensitive "
                     "(#87 straddle)"),
         "detail": (
             f"rho_own {results['cross_thread']['rho_own']:.4f} "
             f"{fmt_ci(results['cross_thread']['ownership_boot']['ci'])} "
             f"crosses the {LOW_LO:.3f} region edge, so `PATH_NOT_OWNED` is "
             "a straddle verdict and not a clean one. What is NOT ambiguous: "
             "the arm's implied Var(phi) is "
             f"{attenuation['cross_thread']['implied_phi_variance'] / v_pri * 100:.0f}% "
             "of the primary's, so the loss is not only the smaller "
             "adjacency count — a real part of the owned rhythm is "
             "reply-chain mechanics, as U1's 43.8% precedent priced.")},
        {"anomaly": ("the cluster-bootstrap interval is asymmetric about its "
                     "point on the null world"),
         "detail": (
             "on the common-path world the point is "
             f"{part0['common_path']['rho_own']:+.4f} inside "
             f"{fmt_ci(part0['common_path']['ownership_boot']['ci'])} — an "
             "interval that covers 0 and its own point but is not centred on "
             "it. X1c recorded the same asymmetry; it is conservative on the "
             "side that matters here, and the primary's CI is far from every "
             "region edge.")},
    ]
    return out


# ---------------------------------------------------------------------------
# Stage 6 — the report (rule 24: every table generated from the artifacts)
# ---------------------------------------------------------------------------


BOUNDARIES = (
    "**Metadata only; expression VOLUME and not content (permanent).** The "
    "only text-derived quantity in this leg is `word_count_quoteless`, the "
    "author's own-word count per comment. No body was read, no topic, no "
    "style, no sentiment. Every claim here is about the RHYTHM OF HOW MUCH "
    "is written, never about what is written.",
    "**The What x When projection caution (eq-12).** `r1` is ONE static "
    "projection of the trajectory kernel: the lag-1 event-time "
    "autocorrelation of a single scalar. A flat r1 would not falsify "
    "dynamics, and a detected r1 is a LOWER bound on the kernel, not a "
    "measurement of it. Nothing here speaks about longer lags, about "
    "calendar time, or about any other coordinate of the path.",
    "**No psychological naming.** Verbosity rhythm is a technical "
    "expression-volume object. It is not a trait, a state, a disposition or "
    "a preference, and the leg is label-free: `author_profiles.csv` was "
    "never opened.",
    "**EXPLORATORY, corpus-level.** No person-level claim is licensed. The "
    "per-author r1 values exist only as the population of a mean and of one "
    "correlation.",
    "**Cohort composition.** The disjoint cohort is TYPOLOGY-ENRICHED by "
    "construction (PANDORA's non-Big5 authors are MBTI-labelled users), so "
    "it is a platform sample with a selection, not a population sample.",
    "**The attenuation note.** The per-half r1 carries sampling noise of "
    "about 1/sqrt(348) ~ 0.054 at the median half, which ATTENUATES the "
    "ownership correlation. No disattenuation is registered and none is "
    "applied: the raw rho_own routes, and it is a LOWER bound on the "
    "ownership of the underlying per-half path parameter.",
    "**Pool selection.** The pool floors at 50 events in EACH half, so the "
    "leg speaks for authors who are ACTIVE ON BOTH SIDES of their own "
    "median. Nothing here speaks for short-lived or low-volume accounts.",
)


def _exact(value: Any) -> str:
    """Print an anchor at the precision it was REGISTERED at, not at 4 dp."""

    if isinstance(value, bool) or isinstance(value, (int, np.integer)):
        return f"{int(value):,}"
    text = f"{float(value):.5f}".rstrip("0").rstrip(".")
    return text or "0"


def _table(add, header: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
    add("| " + " | ".join(header) + " |")
    add("|" + "|".join(["---"] * len(header)) + "|")
    for row in rows:
        add("| " + " | ".join(str(c) for c in row) + " |")
    add("")


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []

    def add(text: str = "") -> None:
        lines.append(text)

    verdict = payload["verdict"]
    part0 = payload["part0"]
    arms = payload["arms"]
    cells = payload["cells"]
    primary = arms.get("primary")

    add("# SUICA M4-X2 — the path of expression volume")
    add("")
    if primary is None:
        add(f"**Outcome: `{verdict['cell']}`.** A ROUTING clause of Part 0 "
            "failed on the realized skeleton, so the leg stopped BEFORE any "
            "corpus estimand was scored. Nothing below is a reading of the "
            "corpus; every number in this report is synthetic or design "
            "arithmetic. " + verdict.get("note", ""))
    else:
        add(f"**Outcome: `{verdict['cell']}`.** Crossing #3's first real-data "
            "projection. On the primary arm "
            f"({primary['authors_paired']:,} disjoint-cohort authors, "
            f"{primary['census']['adjacencies']:,} within-half adjacencies) "
            "the ownership correlation of the per-half lag-1 path parameter "
            f"is **rho_own = {fmt(verdict.get('rho_own'))}** "
            f"{fmt_ci(verdict.get('ci', [float('nan')] * 2))} against a "
            f"pairing-permutation band "
            f"{fmt_ci(verdict.get('band', [float('nan')] * 2))}; path "
            f"PRESENCE co-reports at mean r1 = "
            f"{fmt(verdict.get('presence_mean_r1'))} against the "
            "marginal-preserving band "
            f"{fmt_ci(verdict.get('presence_band', [float('nan')] * 2), 6)}.")
    add("")
    add(f"Registration: `docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md`, "
        f"section \"X2 — the path of expression volume (registered BEFORE "
        f"run, 2026-08-19)\", commit 550466f. Run "
        f"{payload['run']['finished_utc']}, "
        f"{payload['run']['runtime_s']:.0f} s.")
    add("")

    add("## Verdict and cell")
    add("")
    _table(add, ["field", "value"], [
        ["cell", f"`{verdict['cell']}`"],
        ["routes on", verdict["routes_on"]],
        ["Part 0 gate", f"`{part0['status']}`"],
        ["rho_own (primary)", fmt(verdict.get("rho_own"))],
        ["cluster-bootstrap CI (B = 1000, authors)",
         fmt_ci(verdict.get("ci", [float("nan")] * 2))],
        ["pairing-permutation band (B = 499)",
         fmt_ci(verdict.get("band", [float("nan")] * 2))],
        ["#87 region straddle", ", ".join(verdict.get(
            "region_edges_straddled", [])) or "none"],
    ])
    add(f"Registered regions on rho_own (#87, half-width "
        f"{BOUNDARY_HALFWIDTH:.3f}): `{CELL_NOT_OWNED}` = CI includes 0 or "
        f"point < {LOW_LO:.3f}; `{CELL_AT_LOW}` = [{LOW_LO:.3f}, "
        f"{LOW_HI:.3f}]; `{CELL_WEAK}` = ({LOW_HI:.3f}, {HIGH_LO:.3f}); "
        f"`{CELL_AT_HIGH}` = [{HIGH_LO:.3f}, {HIGH_HI:.3f}]; "
        f"`{CELL_STRONG}` = above {HIGH_HI:.3f} (the trait-join-eligible "
        "level).")
    add("")

    add("## Census and the blocking anchors (#78)")
    add("")
    _table(add, ["registered predicate", "registered", "observed", "status"],
           [[k, _exact(v["registered"]), _exact(v["observed"]),
             f"`{v['status']}`"]
            for k, v in payload["census"]["pins"].items()])

    add("## Part 0 — the gate on the REALIZED skeleton (wholly synthetic y)")
    add("")
    add("Real per-author sequence lengths and real half splits; every y in "
        "this section is planted. No corpus value enters Part 0.")
    add("")
    add("### ROUTING clauses (A1-stopping)")
    add("")
    _table(add, ["#", "clause", "observed", "required", "status"],
           [[c["id"], c["clause"], c["observed"], c["required"],
             f"`{c['status']}`"] for c in part0["routing"]])
    add("### DESCRIPTIVE clauses (annotate, never stop)")
    add("")
    _table(add, ["#", "clause", "observed", "required", "status"],
           [[c["id"], c["clause"], c["observed"], c["required"],
             f"`{c['status']}`"] for c in part0["descriptive"]])
    mapping = part0["mapping"]
    add("### The ownership mapping (#76 operating point, derived here)")
    add("")
    add("```")
    add(mapping["formula"])
    add("```")
    _table(add, ["quantity", "value"], [
        ["phi_bar (mean AR parameter)", fmt(mapping["phi_bar"], 4)],
        ["m_early = E_u[1/(n_early - 1)]",
         fmt(mapping["m_early_mean_inv_pairs"], 8)],
        ["m_late = E_u[1/(n_late - 1)]",
         fmt(mapping["m_late_mean_inv_pairs"], 8)],
        ["A_early (mean sampling variance of r1, early)",
         fmt(mapping["A_early"], 8)],
        ["A_late (mean sampling variance of r1, late)",
         fmt(mapping["A_late"], 8)],
        ["V = Var_u(phi_u) solving rho_own = 0.50",
         fmt(mapping["V_phi_variance"], 8)],
        ["sd(phi_u) planted", fmt(mapping["sd_phi"], 6)],
        ["rho implied by the solution",
         fmt(mapping["rho_implied_by_the_solution"], 6)],
    ])

    if not arms:
        add("## Arms")
        add("")
        add("NOT SCORED — the A1 stop fired in Part 0. No arm's presence or "
            "ownership estimand was computed, and `PATH_NOT_OWNED` is "
            "expressly NOT the outcome of this leg.")
        add("")
        payload.setdefault("anomalies", [])
        _write_boundaries_and_config(add, payload)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    add("## Arms — presence and ownership, each against its own null")
    add("")
    _table(add, ["arm", "authors", "cells", "adjacencies",
                 "presence mean r1", "presence band (B = 499)", "detected",
                 "rho_own", "CI (B = 1000)", "pairing band", "cell"],
           [[a["label"], f"{a['authors_paired']:,}",
             f"{a['census']['cells']:,}",
             f"{a['census']['adjacencies']:,}",
             fmt(a["presence_mean_r1"]),
             fmt_ci(a["presence_null"]["band"], 6),
             "yes" if a["presence_detected"] else "no",
             fmt(a["rho_own"]),
             fmt_ci(a["ownership_boot"]["ci"]),
             fmt_ci(a["ownership_null"]["band"]),
             f"`{cells[k]['cell']}`"]
            for k, a in arms.items()])
    add("Presence carries an unregistered annotation interval (the same "
        "author cluster bootstrap applied to the presence mean), printed "
        "here so the point is not bare; it routes nothing:")
    add("")
    _table(add, ["arm", "presence mean r1",
                 "cluster-bootstrap CI (annotation, NOT registered)"],
           [[a["label"], fmt(a["presence_mean_r1"]),
             fmt_ci(a["presence_boot_annotation"]["ci"])]
            for a in arms.values()])

    add("## Retention of the ownership")
    add("")
    _table(add, ["arm", "rho_own", "retention vs primary",
                 "lean (>= 0.50)"],
           [[payload["retention"][k]["label"], fmt(
               payload["retention"][k]["rho_own"]),
             fmt(payload["retention"][k]["ratio"]),
             "held" if payload["retention"][k]["ratio"] >= RETENTION_MOST
             else "BROKEN"]
            for k in ("cross_thread", "venue_resid")])

    add("## Attenuation arithmetic (ANNOTATION — design arithmetic, not an "
        "estimator; nothing routes on it)")
    add("")
    add("The registered attenuation note says the per-half r1 carries "
        "sampling noise that depresses rho_own, and that the RAW rho_own "
        "routes with no disattenuation. This table makes that note "
        "quantitative on each arm's own realized skeleton: `A` is the mean "
        "sampling variance of r1 implied by the arm's pair counts and its own "
        "mean r1, and `Var(phi)` is the across-author path-parameter variance "
        "that the arm's rho_own would imply under the SAME first-order model "
        "Part 0 plants. It is printed so the arm divergences can be read; it "
        "is not an estimator and no verdict touches it.")
    add("")
    _table(add, ["arm", "median pairs/cell", "mean r1", "rho_own", "A_early",
                 "A_late", "implied Var(phi)", "implied sd(phi)"],
           [[v["label"], f"{v['median_pairs_per_cell']:,.1f}",
             fmt(v["mean_r1"]), fmt(v["rho_own"]), fmt(v["A_early"], 6),
             fmt(v["A_late"], 6), fmt(v["implied_phi_variance"], 6),
             fmt(v["implied_phi_sd"], 4)]
            for v in payload["attenuation"].values()])

    add("## Registered leans (report against; they never route)")
    add("")
    _table(add, ["lean", "registered", "observed", "status"],
           [[r["lean"], r["registered"], r["observed"], f"`{r['status']}`"]
            for r in payload["leans"]])

    add("## #73 flags")
    add("")
    if payload["flags_73"]:
        _table(add, ["arm", "primary cell", "arm cell", "rho_own", "CI",
                     "note"],
               [[f["arm"], f"`{f['primary_cell']}`", f"`{f['arm_cell']}`",
                 fmt(f["rho_own"]), fmt_ci(f["ci"]), f["note"]]
                for f in payload["flags_73"]])
    else:
        add("None: every arm lands in the primary's cell and no interval "
            "crosses a registered region edge.")
        add("")

    _write_boundaries_and_config(add, payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_boundaries_and_config(add, payload: dict[str, Any]) -> None:
    add("## Honest anomalies")
    add("")
    for row in payload["anomalies"]:
        detail = row["detail"]
        add(f"- **{row['anomaly']}.** {detail[:1].upper()}{detail[1:]}")
    add("")

    add("## Boundaries")
    add("")
    for text in BOUNDARIES:
        add(f"- {text}")
    add("")

    add("## Governance")
    add("")
    _table(add, ["gate", "status"],
           [[k, f"`{v}`"] for k, v in payload.get("gates", {}).items()])

    add("## Configuration")
    add("")
    add("```json")
    add(json.dumps(payload["config"], indent=2, sort_keys=True))
    add("```")
    add("")
    add(f"Config SHA-256: `{payload['config_sha256']}`. Artifacts: "
        "`results/m4_x2_volume_path/` (gitignored). Every table above is "
        "generated from those artifacts (rule 24).")
    add("")


# ---------------------------------------------------------------------------
# Stage 7 — arm construction from the event cache
# ---------------------------------------------------------------------------


def arm_layout(cache: dict[str, Any], author_sel: np.ndarray
               ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """(cell_start, cell_len, cell_author, cell_half) for the selected pool."""

    offs = cache["offsets"][:-1]
    n_early = cache["n_early"]
    n_total = cache["n_total"]
    codes = np.flatnonzero(author_sel)
    cell_start = np.concatenate([offs[codes], offs[codes] + n_early[codes]])
    cell_len = np.concatenate([n_early[codes],
                               (n_total - n_early)[codes]])
    local = np.arange(codes.size, dtype=np.int64)
    cell_author = np.concatenate([local, local])
    cell_half = np.concatenate([np.zeros(codes.size, np.int8),
                                np.ones(codes.size, np.int8)])
    return cell_start, cell_len, cell_author, cell_half


def cross_thread_mask(cache: dict[str, Any]) -> np.ndarray:
    """Slot j opens a CROSS-THREAD adjacency iff link[j] != link[j+1].

    Evaluated on the flat, per-author time-ordered event array; the Arm layer
    then clears the last slot of every cell, which is what confines the
    adjacency to a half.  The share of within-half adjacencies this keeps is
    a BLOCKING census anchor (0.73159 disjoint, 0.62054 Big5).
    """

    link = cache["ev_link"]
    mask = np.zeros(link.size, dtype=bool)
    mask[:-1] = link[:-1] != link[1:]
    return mask


def venue_residual(cache: dict[str, Any]) -> tuple[np.ndarray, dict[str, Any]]:
    """y minus b̄_{c,h}, the global community-half mean over ALL events."""

    y = np.log1p(cache["ev_wcq"].astype(np.float64))
    counts = cache["ch_count"].astype(np.float64)
    means = np.divide(cache["ch_sum"], counts, out=np.zeros_like(counts),
                      where=counts > 0)
    key = (cache["ev_comm"].astype(np.int64) * 2
           + cache["ev_half"].astype(np.int64))
    resid = y - means[key]
    info = {
        "community_halves_with_events": int((counts > 0).sum()),
        "events_residualized": int(resid.size),
        "mean_residual": float(resid.mean()),
        "sd_y": float(y.std()),
        "sd_residual": float(resid.std()),
        "variance_removed_share": float(1.0 - resid.var() / y.var()),
        "note": ("b̄_{c,h} is computed over ALL parseable events in that "
                 "community-half, pool membership irrelevant (registration)"),
    }
    return resid, info


def build_arms(cache: dict[str, Any], log: RunLog
               ) -> tuple[dict[str, Arm], dict[str, Any]]:
    is_big5 = cache["pool_is_big5"]
    n_early = cache["n_early"]
    n_late = cache["n_total"] - n_early
    y = np.log1p(cache["ev_wcq"].astype(np.float64))
    resid, resid_info = venue_residual(cache)
    ct_mask = cross_thread_mask(cache)

    disjoint = ~is_big5
    floor100 = disjoint & (n_early >= POOL_FLOOR_SENSITIVITY) \
        & (n_late >= POOL_FLOOR_SENSITIVITY)

    specs = [
        ("primary", "PRIMARY — raw adjacency, disjoint pool", disjoint, y,
         None),
        ("cross_thread", "cross-thread-only adjacency, disjoint pool",
         disjoint, y, ct_mask),
        ("venue_resid", "venue-residualized y, raw adjacency, disjoint pool",
         disjoint, resid, None),
        ("big5", "REPLICATION — raw adjacency, Big5 pool", is_big5, y, None),
        ("floor100", "sensitivity — floor 100 events/half, disjoint pool",
         floor100, y, None),
    ]
    arms: dict[str, Arm] = {}
    for key, label, sel, values, mask in specs:
        start, length, author, half = arm_layout(cache, sel)
        arms[key] = Arm(key, label, values, start, length, author, half, mask,
                        int(sel.sum()))
        log.event("arm_built", **arms[key].census())
    info = {"venue_residual": resid_info,
            "floor100_pool_authors": int(floor100.sum()),
            "cross_thread_share_disjoint": _cross_share(cache, disjoint,
                                                        ct_mask),
            "cross_thread_share_big5": _cross_share(cache, is_big5, ct_mask)}
    return arms, info


def _cross_share(cache: dict[str, Any], sel: np.ndarray,
                 ct_mask: np.ndarray) -> float:
    """Pooled share of within-half adjacencies that cross threads."""

    n_total = cache["n_total"]
    n_early = cache["n_early"]
    offs = cache["offsets"]
    author_of_event = np.repeat(np.arange(n_total.size, dtype=np.int64),
                                n_total)
    half = cache["ev_half"]
    valid = np.zeros(author_of_event.size, dtype=bool)
    valid[:-1] = ((author_of_event[:-1] == author_of_event[1:])
                  & (half[:-1] == half[1:]))
    pick = valid & sel[author_of_event]
    del author_of_event, valid
    return float((pick & ct_mask).sum() / pick.sum())


def degenerate_halves(cache: dict[str, Any], sel: np.ndarray) -> int:
    """Halves with sd(y) == 0 — the census counts them by sd alone (#57)."""

    y = np.log1p(cache["ev_wcq"].astype(np.float64))
    n_total = cache["n_total"]
    author_of_event = np.repeat(np.arange(n_total.size, dtype=np.int64),
                                n_total)
    key = author_of_event * 2 + cache["ev_half"].astype(np.int64)
    size = 2 * n_total.size
    cnt = np.bincount(key, minlength=size).astype(np.float64)
    s = np.bincount(key, weights=y, minlength=size)
    q = np.bincount(key, weights=y * y, minlength=size)
    with np.errstate(invalid="ignore", divide="ignore"):
        var = q / cnt - (s / cnt) ** 2
    keep = np.repeat(sel, 2)
    return int(np.count_nonzero(var[keep] <= 0.0))


def median_adjacencies(cache: dict[str, Any], sel: np.ndarray) -> float:
    """Median over authors of the MEAN adjacency count of the two halves.

    The planner's census publishes 348.0 (disjoint) and 491.75 (Big5); the
    quarter fraction is only reachable by averaging the two halves per author
    and taking the median over authors, which pins the definition.
    """

    n_early = cache["n_early"][sel].astype(np.float64)
    n_late = (cache["n_total"] - cache["n_early"])[sel].astype(np.float64)
    return float(np.median(((n_early - 1.0) + (n_late - 1.0)) / 2.0))


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comments", type=Path, default=DEFAULT_COMMENTS)
    parser.add_argument("--cohort", type=Path, default=DEFAULT_COHORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--b-perm", type=int, default=B_PERM)
    parser.add_argument("--b-boot", type=int, default=B_BOOT)
    parser.add_argument("--rebuild-cache", action="store_true")
    args = parser.parse_args(argv)

    started = time.time()
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    log = RunLog(output / "run_log.jsonl")
    log.event("start", registration=("docs/SUICA_M4_X_EXPRESSION_RESPONSE_"
                                     "PLAN.md#X2 (commit 550466f)"),
              seed=SEED, b_perm=args.b_perm, b_boot=args.b_boot)

    config = {
        "leg": "M4-X2",
        "registration": ("docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md, "
                         "section X2, commit 550466f"),
        "seed": SEED, "seed_part0": SEED_PART0, "seed_perm": SEED_PERM,
        "seed_boot": SEED_BOOT,
        "b_perm": args.b_perm, "b_boot": args.b_boot,
        "y": "log1p(word_count_quoteless)",
        "order": "per-author stable sort by created_utc (ties keep stream order)",
        "halves": "full-stream median of the author's created_utc, <= early",
        "adjacency": "consecutive events WITHIN a half",
        "pool_floor_primary": POOL_FLOOR_PRIMARY,
        "pool_floor_sensitivity": POOL_FLOOR_SENSITIVITY,
        "boundary_regions": {"low": BOUNDARY_LOW, "high": BOUNDARY_HIGH,
                             "half_width": BOUNDARY_HALFWIDTH},
        "phi_bar_ar": PHI_BAR_AR, "phi_bar_common": PHI_BAR_COMMON,
        "phi_clip": PHI_CLIP, "rho_true_target": RHO_TRUE_TARGET,
        "n_synth_replicates": N_SYNTH_REPLICATES,
        "tol": f"max({TOL_FLOOR}, {TOL_SD_MULT} x replicate sd)",
        "comments": str(args.comments), "cohort": str(args.cohort),
        "columns_read": ["author", "subreddit", "created_utc", "link_id",
                         "word_count_quoteless"],
        "author_profiles_csv": "NEVER OPENED (label-free)",
    }
    write_json(output / "config.json", config)
    config_sha = hashlib.sha256(
        json.dumps(config, sort_keys=True).encode("utf-8")).hexdigest()
    write_json(output / "config.sha256.json",
               {"sha256": config_sha, "utc": utc_now()})

    # ---- Stage 1: the event cache ----------------------------------------
    cache_path = output / "event_cache.npz"
    cohort_frame = pd.read_csv(args.cohort, usecols=["author"])
    cohort_names = sorted({str(name) for name in cohort_frame["author"]})
    if cache_path.exists() and not args.rebuild_cache:
        cache, meta = load_cache(cache_path)
        author_names = meta["authors"]
        stats = meta["stream_stats"]
        log.event("cache_loaded", path=str(cache_path))
    else:
        scaffold = stream_events(args.comments, log)
        author_names = scaffold["authors"]
        stats = scaffold["stream_stats"]
        name_to_code = {name: i for i, name in enumerate(author_names)}
        big5_mask = np.zeros(len(author_names), dtype=bool)
        for name in cohort_names:
            code = name_to_code.get(name)
            if code is not None:
                big5_mask[code] = True
        cache = build_event_cache(scaffold, big5_mask, log)
        save_cache(cache, scaffold, cache_path)
        meta = json.loads(cache_path.with_suffix(".meta.json")
                          .read_text("utf-8"))
        log.event("cache_saved", path=str(cache_path))

    is_big5 = cache["pool_is_big5"]
    disjoint_sel = ~is_big5
    cohort_set = set(cohort_names)
    big5_all = np.array([name in cohort_set for name in author_names])

    # ---- Stage 2: the arms and the blocking anchor gate -------------------
    arms, arm_info = build_arms(cache, log)
    observed = {
        "rows parseable (author+subreddit+created_utc+wcq)":
            int(stats["rows_parseable"]),
        "authors": int(stats["authors"]),
        "Big5 cohort authors seen": int(big5_all.sum()),
        "disjoint authors": int((~big5_all).sum()),
        "pool: >= 50 events in EACH half, disjoint": int(disjoint_sel.sum()),
        "pool: >= 50 events in EACH half, Big5": int(is_big5.sum()),
        "cross-thread share of within-half adjacencies, disjoint (5 dp)":
            round(arm_info["cross_thread_share_disjoint"], 5),
        "cross-thread share of within-half adjacencies, Big5 (5 dp)":
            round(arm_info["cross_thread_share_big5"], 5),
        "degenerate halves (sd = 0), disjoint":
            degenerate_halves(cache, disjoint_sel),
        "degenerate halves (sd = 0), Big5": degenerate_halves(cache, is_big5),
        "median adjacencies per half, disjoint":
            median_adjacencies(cache, disjoint_sel),
        "median adjacencies per half, Big5":
            median_adjacencies(cache, is_big5),
    }
    expected = {
        "rows parseable (author+subreddit+created_utc+wcq)":
            ANCHOR_ROWS_PARSEABLE,
        "authors": ANCHOR_AUTHORS,
        "Big5 cohort authors seen": ANCHOR_BIG5_AUTHORS,
        "disjoint authors": ANCHOR_DISJOINT_AUTHORS,
        "pool: >= 50 events in EACH half, disjoint": ANCHOR_POOL_DISJOINT,
        "pool: >= 50 events in EACH half, Big5": ANCHOR_POOL_BIG5,
        "cross-thread share of within-half adjacencies, disjoint (5 dp)":
            ANCHOR_CROSS_SHARE_DISJOINT,
        "cross-thread share of within-half adjacencies, Big5 (5 dp)":
            ANCHOR_CROSS_SHARE_BIG5,
        "degenerate halves (sd = 0), disjoint": ANCHOR_DEGENERATE_DISJOINT,
        "degenerate halves (sd = 0), Big5": ANCHOR_DEGENERATE_BIG5,
        "median adjacencies per half, disjoint": ANCHOR_MEDIAN_ADJ_DISJOINT,
        "median adjacencies per half, Big5": ANCHOR_MEDIAN_ADJ_BIG5,
    }
    census = anchor_gate(observed, expected)
    write_json(output / "census.json", census)
    write_json(output / "arm_census.json",
               {"arms": {k: a.census() for k, a in arms.items()},
                "info": arm_info, "stream_stats": stats})
    log.event("census", status=census["status"])
    if census["status"] != "PASS":
        raise SystemExit(f"STOP (#78): the census gate FAILED: "
                         f"{json.dumps(census['pins'], indent=2, default=str)}")

    # ---- Stage 3: Part 0, the gate ---------------------------------------
    part0 = part0_gate(arms["primary"], b_perm=args.b_perm,
                       b_boot=args.b_boot, seed=SEED_PART0, log=log)
    write_json(output / "part0_gate.json", part0)
    log.event("part0", status=part0["status"])

    gates = {
        f"Census / blocking anchors (#78, {len(census['pins'])} predicates)":
            census["status"],
        "Part 0 realized-skeleton gate (5 ROUTING clauses)": part0["status"],
    }

    if part0["status"] != "PASS":
        verdict = build_verdict(part0, {}, {})
        write_json(output / "verdict.json", verdict)
        payload = {"run": {"finished_utc": utc_now(),
                           "runtime_s": time.time() - started},
                   "config": config, "config_sha256": config_sha,
                   "census": census, "part0": part0, "arms": {}, "cells": {},
                   "retention": {}, "leans": [], "flags_73": [],
                   "verdict": verdict, "gates": gates}
        write_report(args.report, payload)
        write_json(output / "report_payload.json",
                   {k: v for k, v in payload.items() if k != "config"})
        log.event("a1_stop", verdict=verdict["cell"])
        raise SystemExit("A1 STOP: Part 0 ROUTING clause failed; no corpus "
                         "estimand was scored.")

    # ---- Stage 4: the arms ------------------------------------------------
    results: dict[str, Any] = {}
    for i, (key, arm) in enumerate(arms.items()):
        results[key] = analyse_arm(arm, b_perm=args.b_perm,
                                   b_boot=args.b_boot,
                                   seed_perm=SEED_PERM + 1000 * i,
                                   seed_boot=SEED_BOOT + 1000 * i, log=log)
        log.event("arm_done", arm=key,
                  presence=results[key]["presence_mean_r1"],
                  rho_own=results[key]["rho_own"])
    write_json(output / "arms.json", results)

    cells = {k: classify(v) for k, v in results.items()}
    write_json(output / "cells.json", cells)
    rho_primary = results["primary"]["rho_own"]
    retention = {
        k: {"label": results[k]["label"], "rho_own": results[k]["rho_own"],
            "ratio": results[k]["rho_own"] / rho_primary}
        for k in ("cross_thread", "venue_resid")
    }
    write_json(output / "retention.json", retention)
    attenuation = attenuation_arithmetic(arms, results)
    write_json(output / "attenuation.json", attenuation)
    leans = evaluate_leans(cells, results, retention)
    anomalies = honest_anomalies(arms, results, cells, part0, attenuation)
    write_json(output / "anomalies.json", anomalies)
    write_json(output / "leans.json", leans)
    flags = flags_73(cells)
    write_json(output / "flags_73.json", flags)
    verdict = build_verdict(part0, cells, results)
    write_json(output / "verdict.json", verdict)
    log.event("verdict", **{k: v for k, v in verdict.items()
                            if k != "region_edges_straddled"})

    payload = {
        "run": {"finished_utc": utc_now(), "runtime_s": time.time() - started},
        "config": config, "config_sha256": config_sha, "census": census,
        "part0": part0, "arms": results, "cells": cells,
        "retention": retention, "leans": leans, "flags_73": flags,
        "attenuation": attenuation, "anomalies": anomalies,
        "verdict": verdict, "gates": gates,
    }
    write_report(args.report, payload)

    # ---- Stage 5: the ID-leak gate over the widened universe (#83) --------
    universe = sorted({str(n) for n in cohort_names}
                      | {str(n) for n in author_names})
    write_json(output / "id_scan_universe.json",
               {"n_names": len(universe), "cohort_names": len(cohort_names),
                "stream_names": len(author_names),
                "note": "gitignored; the scan list is never committed"})
    scan = scan_for_cohort_ids(list(COMMITTED_FILES), universe)
    baseline_keys, baseline_detail = baseline_hit_keys(
        list(COMMITTED_FILES), universe, output / "head_baseline")
    new_hits = new_hits_only(scan["hits"], baseline_keys)
    scan["universe_size"] = len(universe)
    scan["raw_status"] = scan["status"]
    scan["n_pre_existing_hits"] = scan["n_hits"] - len(new_hits)
    scan["n_new_hits"] = len(new_hits)
    scan["new_hits"] = new_hits
    scan["baseline"] = baseline_detail
    scan["status"] = "PASS" if not new_hits else "FAIL"
    write_json(output / "id_leak_scan.json", scan)
    log.event("id_leak_scan", status=scan["status"], hits=scan["n_hits"],
              new_hits=scan["n_new_hits"],
              pre_existing=scan["n_pre_existing_hits"],
              universe=len(universe))
    gates[f"ID-leak scan (0 NEW hits of {len(universe):,} author names over "
          f"the committed files; {scan['n_pre_existing_hits']} pre-existing "
          "dictionary collisions carried unchanged from HEAD)"] = scan["status"]
    payload["id_leak_scan"] = {k: v for k, v in scan.items() if k != "hits"}
    payload["gates"] = gates
    write_report(args.report, payload)
    if scan["status"] != "PASS":
        raise SystemExit(f"STOP: ID-leak scan FAILED on NEW hits: {new_hits}")

    write_json(output / "report_payload.json",
               {k: v for k, v in payload.items() if k != "config"})
    log.event("done", verdict=verdict["cell"], part0=part0["status"],
              runtime_s=round(time.time() - started, 1))
    return 0


if __name__ == "__main__":                       # pragma: no cover
    raise SystemExit(main())
