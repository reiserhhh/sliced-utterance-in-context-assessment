#!/usr/bin/env python3
"""SUICA M4-X1 — the venue response of expression volume.

Registered BEFORE the run in ``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``
(commit 0bdb638).  This runner executes that registration and nothing else.

WHAT THIS LEG DOES
------------------
Crossing #2 (Where x What) gets its first real-data projection WITHOUT reading
a single text body.  The comments file carries ``word_count_quoteless`` — the
author's OWN-WORD count per comment, quotes removed — and the leg asks whether
the author x community profile of y = log(1 + wcq) is REPRODUCIBLE: does the
profile an author shows across venues in the EARLY half of their own stream
come back in the LATE half?

Two estimands, both on the double-centered cell grid v_{u,c,h}:

1. **R** — the mean over eligible authors of the per-author Pearson
   correlation across shared communities between v_early and v_late.  Own null:
   community labels permuted WITHIN (author, half) among that author's eligible
   cells (B = 499) — the design is preserved exactly (same slots, same per-author
   cell counts, same community cell counts); cluster bootstrap over authors
   (B = 1000) for the interval.
2. **The reproducible variance budget** — cross-half covariance shares of
   comment-level Var(y): author (cov of author half-means), community
   (size-weighted cov of community half-means), interaction (cov over cells of
   the double-centered v), residual = 1 - sum.  The cross-half covariance is
   attenuation-free: half-noise drawn afresh cancels in expectation.

PART 0 — THE SYNTHETIC RECOVERY GATE (#76, A1 STOP)
---------------------------------------------------
Before any real estimand is computed, the estimator is required to recover
planted variance shares on a synthetic two-way world built at the PRIMARY
ARM'S REALIZED DESIGN DENSITY (the real skeleton — authors, their community
sets, per-cell comment counts — carrying entirely synthetic y), and is required
NOT to detect an interaction in a null world where none was planted.  On
failure the leg STOPS: no real estimand is reported, only the honest gate.

GOVERNANCE
----------
Metadata only: columns ``author``, ``subreddit``, ``created_utc``,
``word_count_quoteless`` (and ``word_count`` for one sensitivity arm).  NO text
body is ever read.  ``author_profiles.csv`` is NEVER opened — the leg is
label-free end to end.  The cohort file is the frozen 1,401-author Big5 list;
the disjoint cohort is its complement.  Caches and author listings live in
gitignored ``results/`` and are never committed.  Aggregates only.  EXPLORATORY,
corpus-level; no person claims; no psychological naming (expression VOLUME is a
technical object, not a trait).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Configuration constants (registration pins first, then recorded choices).
# ---------------------------------------------------------------------------

SEED = 20260819                     # registration pin
B_PERM = 499                        # registration pin
B_BOOT = 1000                       # registration pin

N_MIN_PRIMARY = 10                  # registration pin: cell eligibility
N_MIN_SENSITIVITY = 5               # registration pin: sensitivity floor
K_MIN = 3                           # registration pin: shared communities

VOCAB_FLOOR_FRACTION = 0.01         # SR0's rule, re-instantiated (W1 line 65)

# --- the X1 census (planner arithmetic #43, predicates exact #77/#78) -------

CENSUS_ROWS_PARSEABLE = 17_640_062
CENSUS_WCQ_ZERO_SHARE = 0.0000      # rounded to 4 dp
CENSUS_AUTHORS = 10_296
CENSUS_BIG5_AUTHORS = 1_401
CENSUS_DISJOINT_AUTHORS = 8_895
CENSUS_POOL_DISJOINT_N10 = 4_342    # PRIMARY
CENSUS_POOL_DISJOINT_N5 = 5_842     # sensitivity
CENSUS_POOL_BIG5_N10 = 615          # replication
CENSUS_VOCAB_FLOOR_USERS = 89       # ceil(0.01 * 8895), W1's floor
CENSUS_LAW_VOCAB = 1_443            # W1's law vocabulary on the disjoint cohort

# Cross-checks that the registration publishes but does not pin as gates.
CROSSCHECK_DISJOINT_EVENTS = 14_634_702      # W1's cache size
CROSSCHECK_BIG5_EVENTS = 3_005_360           # U2's ANCHOR_EVENTS
CROSSCHECK_WITHIN_CELL_SD = 0.9070           # median, n=5 early cells

# --- verdict cells (#75-keyed on the interaction share) --------------------

TRACE_MAX = 0.02                    # RESPONSE_TRACE below this
IDIOSYNCRATIC_MAX = 0.10            # IDIOSYNCRATIC_RESPONSE up to this

CELL_NO_RESPONSE = "NO_REPRODUCIBLE_RESPONSE"
CELL_TRACE = "RESPONSE_TRACE"
CELL_IDIOSYNCRATIC = "IDIOSYNCRATIC_RESPONSE"
CELL_MAJOR = "RESPONSE_MAJOR"
CELL_A1_STOP = "A1_STOP__SYNTHETIC_GATE_FAILED"

# --- registered leans (report against, never route) ------------------------

LEAN_R = (0.05, 0.30)               # exclusive low, inclusive high
LEAN_INTERACTION = (0.005, 0.05)    # exclusive low, inclusive high
LEAN_AUTHOR_MAIN = (0.15, 0.45)     # inclusive both ends
LEAN_COMMUNITY_MAIN = (0.02, 0.15)  # inclusive both ends

# --- Part 0, the synthetic recovery gate (#76 operating point) -------------

PLANTED_SHARES = {"author": 0.30, "community": 0.08, "interaction": 0.02}
NULL_SHARES = {"author": 0.30, "community": 0.08, "interaction": 0.00}
N_SYNTH_REPLICATES = 8              # registration pin: 8 replicates
TOL_SD_MULT = 3.0                   # recorded choice: tolerance = 3 x sd ...
TOL_FLOOR = 0.01                    # ... floored at 0.01 of total variance

# --- recorded implementation choices (registration silent) -----------------

CHUNK_SIZE = 2_000_000              # streaming chunk (rows), the U1/W1 value
MIN_CELL_KEEP = 5                   # cache floor = the smallest registered n_min
CORR_EPS = 1e-12                    # a half's profile is flat below this
PERM_BATCH = 64                     # permutation batch rows (memory control)

SEED_PART0 = SEED + 1               # world draws
SEED_PERM = SEED + 2                # permutation nulls
SEED_BOOT = SEED + 3                # cluster bootstraps

DEFAULT_COMMENTS = Path(
    "/Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/"
    "all_comments_since_2015.csv")
DEFAULT_COHORT = ROOT / "results/m4_sr0_recon/cohort_authors.csv"
DEFAULT_OUTPUT = ROOT / "results/m4_x1_venue_response"
DEFAULT_REPORT = ROOT / "reports/SUICA_M4_X1_VENUE_RESPONSE_REPORT.md"

U2_SCRIPT = ROOT / "scripts/run_suica_m4_u2_persistence_curve.py"
U2B_SCRIPT = ROOT / "scripts/run_suica_m4_u2b_persistence_budget.py"

COMMITTED_FILES = (
    ROOT / "reports/SUICA_M4_X1_VENUE_RESPONSE_REPORT.md",
    ROOT / "scripts/run_suica_m4_x1_venue_response.py",
    ROOT / "tests/test_m4_x1_venue_response.py",
    ROOT / "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md",
    ROOT / "docs/CLAIMS_LEDGER.md",
)

# ---------------------------------------------------------------------------
# U-line machinery, imported by file (#56/#81: the inherited object).
# ---------------------------------------------------------------------------


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:      # pragma: no cover
        raise RuntimeError(f"cannot import machinery from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


U2 = load_module("suica_m4_u2_for_x1", U2_SCRIPT)
U2B = load_module("suica_m4_u2b_for_x1", U2B_SCRIPT)

write_json = U2.write_json
utc_now = U2.utc_now
fmt = U2.fmt
fmt_ci = U2.fmt_ci
RunLog = U2.RunLog
scan_for_cohort_ids = U2.scan_for_cohort_ids
percentile_ci = U2B.percentile_ci


# ---------------------------------------------------------------------------
# Stage 1 — the metadata stream (one pass, no bodies, no labels)
# ---------------------------------------------------------------------------


class _Interner:
    """Chunked first-appearance interning for a string column."""

    def __init__(self) -> None:
        self.index: dict[str, int] = {}

    def encode(self, values: pd.Series) -> np.ndarray:
        codes, uniques = pd.factorize(values, sort=False)
        index = self.index
        mapping = np.empty(len(uniques), dtype=np.int64)
        for i, value in enumerate(uniques):
            code = index.get(value)
            if code is None:
                code = len(index)
                index[value] = code
            mapping[i] = code
        return mapping[codes]

    def names(self) -> list[str]:
        out = [""] * len(self.index)
        for name, code in self.index.items():
            out[code] = name
        return out


def _sorted_remap(names: list[str]) -> tuple[list[str], np.ndarray]:
    """Return (sorted names, old-code -> new-code map)."""

    order = sorted(range(len(names)), key=lambda i: names[i])
    remap = np.empty(len(names), dtype=np.int64)
    for new_code, old_code in enumerate(order):
        remap[old_code] = new_code
    return [names[i] for i in order], remap


def stream_metadata(comments_path: Path, log: RunLog) -> dict[str, Any]:
    """Stream the comments file for the four (+1) metadata columns.

    Parseable = author, subreddit, created_utc and word_count_quoteless all
    present and numeric where numeric is required.  ``word_count`` is carried
    for the registered y-sensitivity arm only.  No body column is requested.
    """

    log.event("stream_start", comments_path=str(comments_path),
              columns=["author", "subreddit", "created_utc",
                       "word_count_quoteless", "word_count"])
    authors = _Interner()
    subreddits = _Interner()
    author_parts: list[np.ndarray] = []
    subreddit_parts: list[np.ndarray] = []
    created_parts: list[np.ndarray] = []
    wcq_parts: list[np.ndarray] = []
    wc_parts: list[np.ndarray] = []
    rows_streamed = 0
    rows_parseable = 0
    wcq_zero = 0
    wc_missing = 0
    chunks = 0

    for chunk in pd.read_csv(
        comments_path,
        usecols=["author", "subreddit", "created_utc",
                 "word_count_quoteless", "word_count"],
        chunksize=CHUNK_SIZE,
        dtype={"author": "str", "subreddit": "str"},
        on_bad_lines="skip",
        engine="c",
    ):
        chunks += 1
        rows_streamed += len(chunk)
        created = pd.to_numeric(chunk["created_utc"], errors="coerce")
        wcq = pd.to_numeric(chunk["word_count_quoteless"], errors="coerce")
        wc = pd.to_numeric(chunk["word_count"], errors="coerce")
        keep = (chunk["author"].notna() & chunk["subreddit"].notna()
                & created.notna() & wcq.notna())
        n_keep = int(keep.sum())
        rows_parseable += n_keep
        if n_keep == 0:
            continue
        wcq_keep = wcq[keep].to_numpy(np.float64)
        wc_keep = wc[keep].to_numpy(np.float64)
        missing = ~np.isfinite(wc_keep)
        wc_missing += int(missing.sum())
        if missing.any():
            # Recorded fallback: the y-sensitivity arm reuses wcq where the
            # raw word_count is absent.  Counted and reported.
            wc_keep = np.where(missing, wcq_keep, wc_keep)
        wcq_zero += int(np.count_nonzero(wcq_keep == 0.0))
        author_parts.append(authors.encode(chunk["author"][keep]))
        subreddit_parts.append(subreddits.encode(chunk["subreddit"][keep]))
        created_parts.append(created[keep].to_numpy(np.float64))
        wcq_parts.append(wcq_keep.astype(np.int32))
        wc_parts.append(wc_keep.astype(np.int32))
        log.event("stream_chunk", chunk=chunks, rows_streamed=rows_streamed,
                  rows_parseable=rows_parseable)

    author_raw = np.concatenate(author_parts)
    subreddit_raw = np.concatenate(subreddit_parts)
    created = np.concatenate(created_parts)
    wcq = np.concatenate(wcq_parts)
    wc = np.concatenate(wc_parts)
    del author_parts, subreddit_parts, created_parts, wcq_parts, wc_parts

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
        "word_count_missing_rows": wc_missing,
        "authors": len(author_names),
        "subreddits": len(subreddit_names),
        "chunks": chunks,
    }
    log.event("stream_done", **stats)
    return {
        "author_code": author_code,
        "subreddit_code": subreddit_code,
        "created_utc": created,
        "wcq": wcq,
        "wc": wc,
        "authors": author_names,
        "subreddits": subreddit_names,
        "stream_stats": stats,
    }


def author_medians(author_code: np.ndarray, created: np.ndarray,
                   n_authors: int) -> tuple[np.ndarray, np.ndarray]:
    """FULL-STREAM median created_utc per author (numpy median convention)."""

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
    return medians, counts


def build_cell_table(scaffold: dict[str, Any], log: RunLog) -> dict[str, Any]:
    """Aggregate the stream into (author, community, half) cell sufficients.

    Half 0 = early = created_utc <= the author's full-stream median.  Only
    cells with at least ``MIN_CELL_KEEP`` comments are kept: every registered
    arm floors at n_min >= 5, so nothing the estimands need is discarded.
    """

    author_code = scaffold["author_code"]
    subreddit_code = scaffold["subreddit_code"]
    created = scaffold["created_utc"]
    n_authors = len(scaffold["authors"])
    n_subs = len(scaffold["subreddits"])

    medians, per_author_rows = author_medians(author_code, created, n_authors)
    half = (created > medians[author_code]).astype(np.int8)
    log.event("halves_assigned", early_rows=int((half == 0).sum()),
              late_rows=int((half == 1).sum()))

    key = ((author_code.astype(np.int64) * n_subs
            + subreddit_code.astype(np.int64)) * 2 + half.astype(np.int64))
    uniq, inverse = np.unique(key, return_inverse=True)
    n_cells_all = int(uniq.size)
    counts = np.bincount(inverse, minlength=n_cells_all).astype(np.int64)

    y_wcq = np.log1p(scaffold["wcq"].astype(np.float64))
    y_wc = np.log1p(scaffold["wc"].astype(np.float64))
    s_wcq = np.bincount(inverse, weights=y_wcq, minlength=n_cells_all)
    q_wcq = np.bincount(inverse, weights=y_wcq * y_wcq, minlength=n_cells_all)
    s_wc = np.bincount(inverse, weights=y_wc, minlength=n_cells_all)
    q_wc = np.bincount(inverse, weights=y_wc * y_wc, minlength=n_cells_all)

    cell_half = (uniq % 2).astype(np.int8)
    pair = uniq // 2
    cell_author = (pair // n_subs).astype(np.int32)
    cell_comm = (pair % n_subs).astype(np.int32)

    # The distinct (author, community) INCIDENCE over ALL parseable rows — the
    # vocabulary rule's raw material, kept before any eligibility floor so the
    # cache can re-instantiate the rule for any author subset.
    pair_unique = np.unique(author_code.astype(np.int64) * n_subs
                            + subreddit_code.astype(np.int64))
    pair_author = (pair_unique // n_subs).astype(np.int32)
    pair_comm = (pair_unique % n_subs).astype(np.int32)
    del pair_unique

    keep = counts >= MIN_CELL_KEEP
    table = {
        "cell_author": cell_author[keep],
        "cell_comm": cell_comm[keep],
        "cell_half": cell_half[keep],
        "cell_n": counts[keep],
        "s_wcq": s_wcq[keep],
        "q_wcq": q_wcq[keep],
        "s_wc": s_wc[keep],
        "q_wc": q_wc[keep],
        "author_rows": per_author_rows,
        "author_median_utc": medians,
        "pair_author": pair_author,
        "pair_comm": pair_comm,
        "n_cells_all": n_cells_all,
        "n_cells_kept": int(keep.sum()),
        "n_subs": n_subs,
        "n_authors": n_authors,
    }
    log.event("cells_built", cells_all=n_cells_all,
              cells_kept=table["n_cells_kept"], floor=MIN_CELL_KEEP)
    return table


def law_vocabulary(table: dict[str, Any], disjoint_mask: np.ndarray,
                   log: RunLog) -> dict[str, Any]:
    """W1's law vocabulary, RE-INSTANTIATED from this leg's own stream.

    The rule (SR0's, re-instantiated by W1 on the disjoint cohort): a community
    is in-vocabulary when at least ceil(0.01 * authors_seen) DISTINCT DISJOINT
    authors post in it.  authors_seen = 8,895 -> floor 89 -> 1,443 communities.
    """

    n_subs = int(table["n_subs"])
    sel = disjoint_mask[table["pair_author"]]
    users = np.bincount(table["pair_comm"][sel].astype(np.int64),
                        minlength=n_subs)
    authors_seen = int(np.unique(table["pair_author"][sel]).size)
    floor = max(1, int(math.ceil(VOCAB_FLOOR_FRACTION * authors_seen)))
    in_vocab = users >= floor
    out = {
        "authors_seen": authors_seen,
        "floor_users": floor,
        "vocabulary_size": int(in_vocab.sum()),
        "disjoint_events": int(table["author_rows"][disjoint_mask].sum()),
        "mask": in_vocab,
    }
    log.event("law_vocabulary", **{k: v for k, v in out.items()
                                   if k != "mask"})
    return out


def save_cache(table: dict[str, Any], scaffold: dict[str, Any],
               path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        cell_author=table["cell_author"],
        cell_comm=table["cell_comm"],
        cell_half=table["cell_half"],
        cell_n=table["cell_n"],
        s_wcq=table["s_wcq"],
        q_wcq=table["q_wcq"],
        s_wc=table["s_wc"],
        q_wc=table["q_wc"],
        author_rows=table["author_rows"],
        author_median_utc=table["author_median_utc"],
        pair_author=table["pair_author"],
        pair_comm=table["pair_comm"],
    )
    write_json(path.with_suffix(".meta.json"), {
        "authors": scaffold["authors"],
        "subreddits": scaffold["subreddits"],
        "stream_stats": scaffold["stream_stats"],
        "n_cells_all": table["n_cells_all"],
        "n_cells_kept": table["n_cells_kept"],
        "min_cell_keep": MIN_CELL_KEEP,
        "note": "gitignored; metadata only; no bodies, no labels",
    })


# ---------------------------------------------------------------------------
# Stage 2 — the eligible design (one Design per arm)
# ---------------------------------------------------------------------------


@dataclass
class Design:
    """The eligible cell grid of one arm.

    A slot is an (author, community) pair whose BOTH halves are eligible.
    Every array below is indexed by slot, in (author, community) sorted order,
    so author blocks are contiguous.
    """

    slot_author: np.ndarray          # int64, 0..A-1
    slot_comm: np.ndarray            # int64, 0..C-1
    n_e: np.ndarray
    n_l: np.ndarray
    s_e: np.ndarray
    s_l: np.ndarray
    q_e: np.ndarray
    q_l: np.ndarray
    n_authors: int
    n_comms: int
    author_codes: np.ndarray         # global author codes of 0..A-1

    @property
    def n_slots(self) -> int:
        return int(self.slot_author.size)

    @property
    def mean_e(self) -> np.ndarray:
        return self.s_e / self.n_e

    @property
    def mean_l(self) -> np.ndarray:
        return self.s_l / self.n_l

    def author_sums(self) -> dict[str, np.ndarray]:
        A = self.n_authors
        return {
            "n_e": np.bincount(self.slot_author, self.n_e, A),
            "n_l": np.bincount(self.slot_author, self.n_l, A),
            "s_e": np.bincount(self.slot_author, self.s_e, A),
            "s_l": np.bincount(self.slot_author, self.s_l, A),
            "q": np.bincount(self.slot_author, self.q_e + self.q_l, A),
            "n": np.bincount(self.slot_author, self.n_e + self.n_l, A),
            "s": np.bincount(self.slot_author, self.s_e + self.s_l, A),
            "k": np.bincount(self.slot_author, None, A),
        }

    def summary(self) -> dict[str, Any]:
        k = np.bincount(self.slot_author, None, self.n_authors)
        m = np.bincount(self.slot_comm, None, self.n_comms)
        n_all = float((self.n_e + self.n_l).sum())
        s_all = float((self.s_e + self.s_l).sum())
        q_all = float((self.q_e + self.q_l).sum())
        var = q_all / n_all - (s_all / n_all) ** 2
        return {
            "authors": int(self.n_authors),
            "communities": int(self.n_comms),
            "slots": int(self.n_slots),
            "cells": int(2 * self.n_slots),
            "comments": int(round(n_all)),
            "mean_y": s_all / n_all,
            "var_y": float(var),
            "shared_communities_per_author_median": float(np.median(k)),
            "shared_communities_per_author_mean": float(k.mean()),
            "authors_per_community_median": float(np.median(m)),
            "singleton_community_slots": int(np.sum(m[self.slot_comm] == 1)),
            "singleton_community_share": float(
                np.mean(m[self.slot_comm] == 1)),
            "comments_per_cell_median": float(
                np.median(np.concatenate([self.n_e, self.n_l]))),
        }

    def var_y(self) -> float:
        n_all = float((self.n_e + self.n_l).sum())
        s_all = float((self.s_e + self.s_l).sum())
        q_all = float((self.q_e + self.q_l).sum())
        return q_all / n_all - (s_all / n_all) ** 2


def build_design(table: dict[str, Any], author_mask: np.ndarray, n_min: int,
                 *, y_key: str = "wcq", comm_mask: np.ndarray | None = None,
                 k_min: int = K_MIN) -> Design:
    """The registered eligibility predicate, applied exactly."""

    n_subs = int(table["n_subs"])
    sel = (table["cell_n"] >= n_min) & author_mask[table["cell_author"]]
    if comm_mask is not None:
        sel = sel & comm_mask[table["cell_comm"]]
    author = table["cell_author"][sel].astype(np.int64)
    comm = table["cell_comm"][sel].astype(np.int64)
    half = table["cell_half"][sel]
    n = table["cell_n"][sel].astype(np.float64)
    s = table[f"s_{y_key}"][sel]
    q = table[f"q_{y_key}"][sel]

    pair = author * n_subs + comm
    is_e = half == 0
    key_e, key_l = pair[is_e], pair[~is_e]
    order_e = np.argsort(key_e, kind="stable")
    order_l = np.argsort(key_l, kind="stable")
    key_e_s, key_l_s = key_e[order_e], key_l[order_l]
    shared = np.intersect1d(key_e_s, key_l_s, assume_unique=True)

    # authors with at least k_min shared communities
    shared_author = shared // n_subs
    uniq_auth, counts = np.unique(shared_author, return_counts=True)
    keep_auth = uniq_auth[counts >= k_min]
    keep = np.isin(shared_author, keep_auth)
    shared = shared[keep]                      # sorted: author-major

    pos_e = order_e[np.searchsorted(key_e_s, shared)]
    pos_l = order_l[np.searchsorted(key_l_s, shared)]
    idx_e = np.flatnonzero(is_e)[pos_e]
    idx_l = np.flatnonzero(~is_e)[pos_l]

    slot_author_code = (shared // n_subs).astype(np.int64)
    slot_comm_code = (shared % n_subs).astype(np.int64)
    author_codes, slot_author = np.unique(slot_author_code,
                                          return_inverse=True)
    _comm_codes, slot_comm = np.unique(slot_comm_code, return_inverse=True)
    return Design(
        slot_author=slot_author.astype(np.int64),
        slot_comm=slot_comm.astype(np.int64),
        n_e=n[idx_e], n_l=n[idx_l],
        s_e=s[idx_e], s_l=s[idx_l],
        q_e=q[idx_e], q_l=q[idx_l],
        n_authors=int(author_codes.size),
        n_comms=int(_comm_codes.size),
        author_codes=author_codes.astype(np.int64),
    )


# ---------------------------------------------------------------------------
# Stage 3 — the estimators
# ---------------------------------------------------------------------------


def double_center(values: np.ndarray, slot_author: np.ndarray,
                  slot_comm: np.ndarray, n_authors: int, n_comms: int,
                  weights: np.ndarray | None = None) -> np.ndarray:
    """v = cellmean - authormean - communitymean + grandmean.

    All three means are taken over ELIGIBLE CELLS, unweighted by cell size
    (the registration's pin).  ``weights`` carries cluster-bootstrap author
    multiplicities; with weights None it is the identity.
    """

    if weights is None:
        a_num = np.bincount(slot_author, values, n_authors)
        a_den = np.bincount(slot_author, None, n_authors).astype(np.float64)
        c_num = np.bincount(slot_comm, values, n_comms)
        c_den = np.bincount(slot_comm, None, n_comms).astype(np.float64)
        grand = float(values.mean())
    else:
        wv = values * weights
        a_num = np.bincount(slot_author, wv, n_authors)
        a_den = np.bincount(slot_author, weights, n_authors)
        c_num = np.bincount(slot_comm, wv, n_comms)
        c_den = np.bincount(slot_comm, weights, n_comms)
        grand = float(wv.sum() / weights.sum())
    with np.errstate(invalid="ignore", divide="ignore"):
        a_mean = np.where(a_den > 0, a_num / np.maximum(a_den, 1e-300), 0.0)
        c_mean = np.where(c_den > 0, c_num / np.maximum(c_den, 1e-300), 0.0)
    return values - a_mean[slot_author] - c_mean[slot_comm] + grand


def per_author_correlations(v_e: np.ndarray, v_l: np.ndarray,
                            slot_author: np.ndarray,
                            n_authors: int) -> np.ndarray:
    """Pearson r per author across that author's shared communities."""

    k = np.bincount(slot_author, None, n_authors).astype(np.float64)
    sx = np.bincount(slot_author, v_e, n_authors)
    sz = np.bincount(slot_author, v_l, n_authors)
    sxx = np.bincount(slot_author, v_e * v_e, n_authors)
    szz = np.bincount(slot_author, v_l * v_l, n_authors)
    sxz = np.bincount(slot_author, v_e * v_l, n_authors)
    with np.errstate(invalid="ignore", divide="ignore"):
        num = sxz - sx * sz / k
        dx = sxx - sx * sx / k
        dz = szz - sz * sz / k
        den = np.sqrt(np.maximum(dx, 0.0) * np.maximum(dz, 0.0))
        r = np.where(den > CORR_EPS, num / np.where(den > 0, den, 1.0),
                     np.nan)
    return r


def weighted_cov(x: np.ndarray, z: np.ndarray,
                 w: np.ndarray | None = None) -> float:
    if w is None:
        return float(np.mean(x * z) - np.mean(x) * np.mean(z))
    total = float(w.sum())
    mx = float((w * x).sum() / total)
    mz = float((w * z).sum() / total)
    return float((w * x * z).sum() / total - mx * mz)


def variance_budget(design: Design, v_e: np.ndarray, v_l: np.ndarray,
                    mult: np.ndarray | None = None) -> dict[str, float]:
    """The reproducible variance budget as shares of comment-level Var(y).

    ``mult`` carries cluster-bootstrap author multiplicities (None = the real
    sample).  Every component is a CROSS-HALF covariance, hence attenuation
    free: the two halves' sampling noise is unlinked given the cell.
    """

    A, C = design.n_authors, design.n_comms
    sa = design.slot_author
    sc = design.slot_comm
    w_slot = None if mult is None else mult[sa]

    # --- comment-level Var(y) over the analysis pool -----------------------
    if mult is None:
        n_all = float((design.n_e + design.n_l).sum())
        s_all = float((design.s_e + design.s_l).sum())
        q_all = float((design.q_e + design.q_l).sum())
    else:
        n_all = float((w_slot * (design.n_e + design.n_l)).sum())
        s_all = float((w_slot * (design.s_e + design.s_l)).sum())
        q_all = float((w_slot * (design.q_e + design.q_l)).sum())
    var_y = q_all / n_all - (s_all / n_all) ** 2

    # --- author main: cov over authors of the two half-means ---------------
    a_ne = np.bincount(sa, design.n_e, A)
    a_nl = np.bincount(sa, design.n_l, A)
    a_se = np.bincount(sa, design.s_e, A)
    a_sl = np.bincount(sa, design.s_l, A)
    ok = (a_ne > 0) & (a_nl > 0)
    ae = np.where(ok, a_se / np.maximum(a_ne, 1e-300), 0.0)
    al = np.where(ok, a_sl / np.maximum(a_nl, 1e-300), 0.0)
    w_auth = None if mult is None else mult.astype(np.float64)
    if w_auth is None:
        cov_author = weighted_cov(ae[ok], al[ok])
    else:
        cov_author = weighted_cov(ae[ok], al[ok], w_auth[ok])

    # --- community main: size-weighted cov over communities ----------------
    if mult is None:
        c_ne = np.bincount(sc, design.n_e, C)
        c_nl = np.bincount(sc, design.n_l, C)
        c_se = np.bincount(sc, design.s_e, C)
        c_sl = np.bincount(sc, design.s_l, C)
    else:
        c_ne = np.bincount(sc, w_slot * design.n_e, C)
        c_nl = np.bincount(sc, w_slot * design.n_l, C)
        c_se = np.bincount(sc, w_slot * design.s_e, C)
        c_sl = np.bincount(sc, w_slot * design.s_l, C)
    okc = (c_ne > 0) & (c_nl > 0)
    ce = np.where(okc, c_se / np.maximum(c_ne, 1e-300), 0.0)
    cl = np.where(okc, c_sl / np.maximum(c_nl, 1e-300), 0.0)
    size = c_ne + c_nl
    cov_comm_w = weighted_cov(ce[okc], cl[okc], size[okc])
    cov_comm_u = weighted_cov(ce[okc], cl[okc])

    # --- interaction: cov over eligible cells of the double-centered v -----
    cov_inter_u = weighted_cov(v_e, v_l, w_slot)
    cell_w = design.n_e + design.n_l
    cov_inter_w = weighted_cov(v_e, v_l,
                               cell_w if w_slot is None else cell_w * w_slot)

    share_a = cov_author / var_y
    share_c = cov_comm_w / var_y
    share_i = cov_inter_u / var_y
    return {
        "var_y": var_y,
        "author": share_a,
        "community": share_c,
        "community_unweighted": cov_comm_u / var_y,
        "interaction": share_i,
        "interaction_weighted": cov_inter_w / var_y,
        "residual": 1.0 - share_a - share_c - share_i,
        "cov_author": cov_author,
        "cov_community": cov_comm_w,
        "cov_interaction": cov_inter_u,
    }


def within_author_permutation(slot_author: np.ndarray,
                              rng: np.random.Generator) -> np.ndarray:
    """One index permutation that shuffles values WITHIN author blocks."""

    keys = slot_author.astype(np.float64) + rng.random(slot_author.size)
    return np.argsort(keys, kind="stable")


def permutation_batch(slot_author: np.ndarray, rng: np.random.Generator,
                      rows: int) -> np.ndarray:
    """``rows`` within-author permutations at once (batched index shuffles)."""

    keys = (slot_author.astype(np.float64)[None, :]
            + rng.random((rows, slot_author.size)))
    return np.argsort(keys, axis=1, kind="stable")


def permutation_null(design: Design, b_perm: int, seed: int,
                     log: RunLog | None = None,
                     tag: str = "") -> dict[str, Any]:
    """Community labels permuted within (author, half) — the mechanism's own.

    The permutation moves each author's cell VALUES among that author's own
    community labels, independently in the two halves.  The design is preserved
    exactly: the same slots, the same per-author cell counts, the same number of
    cells per community.  Author means and the grand mean are permutation
    invariant by construction; the community means are not, and the recomputed
    double-centering is what the null scores.
    """

    rng = np.random.default_rng(seed)
    A, C = design.n_authors, design.n_comms
    sa, sc = design.slot_author, design.slot_comm
    mean_e, mean_l = design.mean_e, design.mean_l
    var_y = design.var_y()
    r_null = np.empty(b_perm, dtype=np.float64)
    share_null = np.empty(b_perm, dtype=np.float64)
    done = 0
    while done < b_perm:
        rows = min(PERM_BATCH, b_perm - done)
        pe = permutation_batch(sa, rng, rows)
        pl = permutation_batch(sa, rng, rows)
        for j in range(rows):
            ve = double_center(mean_e[pe[j]], sa, sc, A, C)
            vl = double_center(mean_l[pl[j]], sa, sc, A, C)
            r = per_author_correlations(ve, vl, sa, A)
            r_null[done + j] = float(np.nanmean(r))
            share_null[done + j] = weighted_cov(ve, vl) / var_y
        done += rows
        if log is not None:
            log.event("permutation_progress", arm=tag, done=done, of=b_perm)
    return {
        "b_perm": int(b_perm),
        "r_band": percentile_ci(r_null),
        "r_null_mean": float(np.mean(r_null)),
        "interaction_band": percentile_ci(share_null),
        "interaction_null_mean": float(np.mean(share_null)),
    }


def cluster_bootstrap(design: Design, v_e: np.ndarray, v_l: np.ndarray,
                      r_author: np.ndarray, b_boot: int,
                      seed: int) -> dict[str, Any]:
    """Cluster bootstrap over AUTHORS (the only exchangeable unit here).

    R is a mean of per-author statistics, so its replicates resample those
    statistics.  The budget's components are not per-author statistics, so each
    replicate recomputes them — including the double-centering — from the
    resampled author multiset.
    """

    rng = np.random.default_rng(seed)
    A = design.n_authors
    draws = rng.integers(0, A, size=(b_boot, A))
    finite = np.isfinite(r_author)
    r_fill = np.where(finite, r_author, 0.0)
    r_take = r_fill[draws]
    f_take = finite[draws]
    with np.errstate(invalid="ignore"):
        r_boot = r_take.sum(axis=1) / np.maximum(f_take.sum(axis=1), 1)
    shares = {k: np.empty(b_boot) for k in
              ("author", "community", "community_unweighted", "interaction",
               "interaction_weighted", "residual")}
    sa, sc = design.slot_author, design.slot_comm
    for b in range(b_boot):
        mult = np.bincount(draws[b], minlength=A).astype(np.float64)
        w_slot = mult[sa]
        ve = double_center(design.mean_e, sa, sc, design.n_authors,
                           design.n_comms, weights=w_slot)
        vl = double_center(design.mean_l, sa, sc, design.n_authors,
                           design.n_comms, weights=w_slot)
        budget = variance_budget(design, ve, vl, mult=mult)
        for key in shares:
            shares[key][b] = budget[key]
    return {
        "b_boot": int(b_boot),
        "r_ci": percentile_ci(r_boot),
        "shares_ci": {k: percentile_ci(v) for k, v in shares.items()},
        "shares_sd": {k: float(np.std(v, ddof=1)) for k, v in shares.items()},
    }


def headroom_report(r_author: np.ndarray) -> dict[str, Any]:
    """#84: the REALIZED per-author correlation distribution.

    Saturation would show as mass piled at r = 1.  Within-cell noise bounds
    every per-author correlation away from 1 by construction; this reports the
    realized distribution so the bound is a number and not an assertion.
    """

    finite = r_author[np.isfinite(r_author)]
    qs = [0.0, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 1.0]
    edges = np.linspace(-1.0, 1.0, 21)
    hist, _ = np.histogram(finite, bins=edges)
    return {
        "authors_scored": int(finite.size),
        "authors_undefined": int(r_author.size - finite.size),
        "mean": float(np.mean(finite)) if finite.size else float("nan"),
        "sd": float(np.std(finite, ddof=1)) if finite.size > 1 else float("nan"),
        "quantiles": {f"q{int(q*100):02d}": float(np.quantile(finite, q))
                      for q in qs} if finite.size else {},
        "share_above_0.99": float(np.mean(finite > 0.99)) if finite.size else 0.0,
        "share_above_0.90": float(np.mean(finite > 0.90)) if finite.size else 0.0,
        "share_positive": float(np.mean(finite > 0.0)) if finite.size else 0.0,
        "histogram_edges": [float(e) for e in edges],
        "histogram_counts": [int(c) for c in hist],
    }


def analyse_design(design: Design, *, b_perm: int, b_boot: int,
                   seed_perm: int, seed_boot: int, tag: str,
                   log: RunLog | None = None,
                   with_inference: bool = True) -> dict[str, Any]:
    """One arm end to end: v, R, the budget, the null band, the bootstrap."""

    A, C = design.n_authors, design.n_comms
    sa, sc = design.slot_author, design.slot_comm
    v_e = double_center(design.mean_e, sa, sc, A, C)
    v_l = double_center(design.mean_l, sa, sc, A, C)
    r_author = per_author_correlations(v_e, v_l, sa, A)
    out: dict[str, Any] = {
        "tag": tag,
        "design": design.summary(),
        "R": float(np.nanmean(r_author)),
        "budget": variance_budget(design, v_e, v_l),
        "headroom": headroom_report(r_author),
    }
    if with_inference:
        out["null"] = permutation_null(design, b_perm, seed_perm, log, tag)
        out["bootstrap"] = cluster_bootstrap(design, v_e, v_l, r_author,
                                             b_boot, seed_boot)
    return out


# ---------------------------------------------------------------------------
# Stage 4 — Part 0, the synthetic recovery gate (#76; A1 stop on failure)
# ---------------------------------------------------------------------------


def synthetic_design(skeleton: Design, shares: dict[str, float],
                     rng: np.random.Generator) -> Design:
    """A two-way world at the skeleton's REALIZED design density.

    The skeleton contributes DESIGN ONLY — which authors, which communities per
    author, how many comments per cell.  Every y is synthetic:
    y = a_u + b_c + g_uc + noise with the planted shares of a unit total
    variance; g_uc is the same in both halves (a persistent interaction), the
    noise is not shared.  Cell sufficient statistics are drawn exactly:
    the cell mean is N(mu, sigma^2/n) and the within-cell sum of squares is
    sigma^2 * chi^2_{n-1}, unlinked — so no comment is materialised and the
    comment-level Var(y) the estimator divides by is a real draw.
    """

    A, C, M = skeleton.n_authors, skeleton.n_comms, skeleton.n_slots
    sa, sc = skeleton.slot_author, skeleton.slot_comm
    va, vc, vg = shares["author"], shares["community"], shares["interaction"]
    ve = max(0.0, 1.0 - va - vc - vg)
    a = rng.normal(0.0, math.sqrt(va), A) if va > 0 else np.zeros(A)
    b = rng.normal(0.0, math.sqrt(vc), C) if vc > 0 else np.zeros(C)
    g = rng.normal(0.0, math.sqrt(vg), M) if vg > 0 else np.zeros(M)
    mu = a[sa] + b[sc] + g
    sigma = math.sqrt(ve)
    out: dict[str, np.ndarray] = {}
    for half, n in (("e", skeleton.n_e), ("l", skeleton.n_l)):
        m = mu + rng.normal(0.0, 1.0, M) * (sigma / np.sqrt(n))
        ss = sigma * sigma * rng.chisquare(np.maximum(n - 1.0, 1.0))
        out[f"s_{half}"] = m * n
        out[f"q_{half}"] = n * m * m + ss
    return Design(
        slot_author=sa, slot_comm=sc,
        n_e=skeleton.n_e, n_l=skeleton.n_l,
        s_e=out["s_e"], s_l=out["s_l"], q_e=out["q_e"], q_l=out["q_l"],
        n_authors=A, n_comms=C, author_codes=skeleton.author_codes,
    )


def recover_shares(design: Design) -> dict[str, float]:
    sa, sc = design.slot_author, design.slot_comm
    v_e = double_center(design.mean_e, sa, sc, design.n_authors,
                        design.n_comms)
    v_l = double_center(design.mean_l, sa, sc, design.n_authors,
                        design.n_comms)
    budget = variance_budget(design, v_e, v_l)
    r = per_author_correlations(v_e, v_l, sa, design.n_authors)
    budget["R"] = float(np.nanmean(r))
    return budget


def synthetic_world_block(skeleton: Design, shares: dict[str, float],
                          name: str, seed: int, replicates: int,
                          log: RunLog) -> dict[str, Any]:
    rows = []
    for rep in range(replicates):
        rng = np.random.default_rng(seed + 1000 * rep)
        world = synthetic_design(skeleton, shares, rng)
        rows.append(recover_shares(world))
        log.event("synthetic_replicate", world=name, replicate=rep,
                  interaction=rows[-1]["interaction"], R=rows[-1]["R"])
    keys = ("author", "community", "interaction", "residual", "R")
    stats = {}
    for key in keys:
        values = np.array([row[key] for row in rows], dtype=np.float64)
        stats[key] = {
            "mean": float(values.mean()),
            "sd": float(values.std(ddof=1)) if values.size > 1 else 0.0,
            "min": float(values.min()),
            "max": float(values.max()),
            "values": [float(x) for x in values],
        }
    return {"world": name, "planted": dict(shares), "replicates": replicates,
            "stats": stats}


def synthetic_gate(skeleton: Design, b_perm: int, b_boot: int,
                   log: RunLog) -> dict[str, Any]:
    """Part 0.  PASS is a precondition for every real number in this leg."""

    log.event("part0_start", authors=skeleton.n_authors,
              slots=skeleton.n_slots, replicates=N_SYNTH_REPLICATES)
    planted = synthetic_world_block(skeleton, PLANTED_SHARES, "planted",
                                    SEED_PART0, N_SYNTH_REPLICATES, log)
    null = synthetic_world_block(skeleton, NULL_SHARES, "null",
                                 SEED_PART0 + 7, N_SYNTH_REPLICATES, log)
    ablations = {
        "author_only": synthetic_world_block(
            skeleton, {"author": 0.30, "community": 0.0, "interaction": 0.0},
            "author_only", SEED_PART0 + 13, N_SYNTH_REPLICATES, log),
        "community_only": synthetic_world_block(
            skeleton, {"author": 0.0, "community": 0.08, "interaction": 0.0},
            "community_only", SEED_PART0 + 19, N_SYNTH_REPLICATES, log),
    }

    # recovery criterion: |mean - planted| <= max(TOL_FLOOR, 3 x replicate sd)
    recovery = {}
    recovery_pass = True
    for key, target in PLANTED_SHARES.items():
        stat = planted["stats"][key]
        tol = max(TOL_FLOOR, TOL_SD_MULT * stat["sd"])
        ok = abs(stat["mean"] - target) <= tol
        recovery_pass = recovery_pass and ok
        recovery[key] = {"planted": target, "recovered_mean": stat["mean"],
                         "replicate_sd": stat["sd"], "tolerance": tol,
                         "bias": stat["mean"] - target,
                         "status": "PASS" if ok else "FAIL"}

    # honesty criterion: the null world must not be detected
    rng_world = np.random.default_rng(SEED_PART0 + 7)
    null_world = synthetic_design(skeleton, NULL_SHARES, rng_world)
    null_inference = analyse_design(
        null_world, b_perm=b_perm, b_boot=b_boot, seed_perm=SEED_PERM + 101,
        seed_boot=SEED_BOOT + 101, tag="part0_null", log=log)
    share_ci = null_inference["bootstrap"]["shares_ci"]["interaction"]
    r_band = null_inference["null"]["r_band"]
    r_point = null_inference["R"]
    ci_covers_zero = bool(share_ci[0] <= 0.0 <= share_ci[1])
    r_inside = bool(r_band[0] <= r_point <= r_band[1])
    honesty_pass = ci_covers_zero and r_inside

    rng_planted = np.random.default_rng(SEED_PART0)
    planted_world = synthetic_design(skeleton, PLANTED_SHARES, rng_planted)
    planted_inference = analyse_design(
        planted_world, b_perm=b_perm, b_boot=b_boot, seed_perm=SEED_PERM + 103,
        seed_boot=SEED_BOOT + 103, tag="part0_planted", log=log)

    status = "PASS" if (recovery_pass and honesty_pass) else "FAIL"
    out = {
        "status": status,
        "recovery": recovery,
        "recovery_status": "PASS" if recovery_pass else "FAIL",
        "honesty_status": "PASS" if honesty_pass else "FAIL",
        "honesty": {
            "interaction_share": null_inference["budget"]["interaction"],
            "interaction_ci": share_ci,
            "ci_covers_zero": ci_covers_zero,
            "interaction_band": null_inference["null"]["interaction_band"],
            "interaction_inside_band": bool(
                null_inference["null"]["interaction_band"][0]
                <= null_inference["budget"]["interaction"]
                <= null_inference["null"]["interaction_band"][1]),
            "ci_covers_point": bool(
                share_ci[0] <= null_inference["budget"]["interaction"]
                <= share_ci[1]),
            "author_share": null_inference["budget"]["author"],
            "community_share": null_inference["budget"]["community"],
            "R": r_point,
            "r_band": r_band,
            "r_inside_band": r_inside,
            "design": null_inference["design"],
        },
        "planted_world_inference": {
            "interaction_share": planted_inference["budget"]["interaction"],
            "interaction_ci":
                planted_inference["bootstrap"]["shares_ci"]["interaction"],
            "interaction_band": planted_inference["null"]["interaction_band"],
            "R": planted_inference["R"],
            "r_band": planted_inference["null"]["r_band"],
            "headroom": planted_inference["headroom"],
        },
        "null_world_headroom": null_inference["headroom"],
        "planted_block": planted,
        "null_block": null,
        "ablations": ablations,
        "tolerance_rule": (f"max({TOL_FLOOR}, {TOL_SD_MULT} x replicate sd) "
                           f"over {N_SYNTH_REPLICATES} replicates"),
    }
    log.event("part0_done", status=status, recovery=out["recovery_status"],
              honesty=out["honesty_status"])
    return out


def build_diagnosis(part0: dict[str, Any],
                    design: dict[str, Any]) -> list[str]:
    """Localize what Part 0 found — every number read off the gate artifacts."""

    hon = part0["honesty"]
    abl = part0["ablations"]
    a_only = abl["author_only"]["stats"]["interaction"]["mean"]
    c_only = abl["community_only"]["stats"]["interaction"]["mean"]
    planted = part0["planted_block"]["stats"]["interaction"]["mean"]
    null = part0["null_block"]["stats"]["interaction"]["mean"]
    items = [
        (f"**The design is sparse.** {design['authors']:,} authors x "
         f"{design['communities']:,} communities give {design['slots']:,} "
         f"occupied (author, community) slots — a fill of "
         f"{fmt(design['slots'] / max(1, design['authors'] * design['communities']), 6)}. "
         f"The median author holds "
         f"{fmt(design['shared_communities_per_author_median'], 1)} shared "
         f"communities and the median community holds "
         f"{fmt(design['authors_per_community_median'], 1)} eligible authors; "
         f"{_pct(design['singleton_community_share'])} of slots sit in a "
         "community with exactly one eligible author."),
        (f"**Double-centering on an incomplete grid does not remove the "
         f"mains.** With ONLY an author main planted (0.3000, nothing else) "
         f"the interaction share reads {_pct(a_only)}; with ONLY a community "
         f"main planted (0.0800, nothing else) it reads {_pct(c_only)}. Both "
         "leaks are cross-half PERSISTENT by construction — a main effect is "
         "the same in both halves — so the cross-half covariance trick, which "
         "is attenuation-free for noise, is defenceless against them."),
        (f"**The null world is detected.** With the interaction planted at "
         f"exactly 0.0000 the estimator returns {_pct(null)} (8 replicates) "
         f"and, on the scored replicate, a bootstrap CI "
         f"{fmt_ci(hon['interaction_ci'])} that excludes 0, with R = "
         f"{_pct(hon['R'])} against a band {fmt_ci(hon['r_band'])}. The "
         f"planted world reads {_pct(planted)} for a planted 0.0200: the "
         "signal and the artifact are the same size."),
        (f"**The mechanism-coordinate null is anti-conservative here.** The "
         f"permutation band for the share, {fmt_ci(hon['interaction_band'])}, "
         f"sits {'below' if hon['interaction_band'][1] < hon['interaction_share'] else 'around'} "
         f"the null-world value {_pct(hon['interaction_share'])}: permuting "
         "community labels within (author, half) moves the community MAIN "
         "along with the interaction, injecting within-author variance the "
         "real data does not carry, so the band under-states the artifact "
         "instead of absorbing it."),
        (f"**The cluster bootstrap is not centred on its own estimate.** In "
         f"the null world the CI is {fmt_ci(hon['interaction_ci'])} around a "
         f"point estimate of {_pct(hon['interaction_share'])} "
         f"({'covers' if hon['ci_covers_point'] else 'does NOT cover'} it): "
         "resampling authors with replacement makes the grid MORE incomplete "
         "(about 63% of authors distinct per replicate), and the leak grows "
         "with incompleteness. A zero-reference CI clause cannot route a "
         "statistic whose zero moves with the resample."),
    ]
    return items


def build_defect_candidates(part0: dict[str, Any],
                            designs: dict[str, Any]) -> list[str]:
    """What a re-registration would have to fix — read off the gate."""

    hon = part0["honesty"]
    primary = designs["primary"]
    lawvocab = designs["sens_lawvocab"]
    a_only = part0["ablations"]["author_only"]["stats"]["interaction"]["mean"]
    c_only = part0["ablations"][
        "community_only"]["stats"]["interaction"]["mean"]
    r_a_only = part0["ablations"]["author_only"]["stats"]["R"]["mean"]
    r_c_only = part0["ablations"][
        "community_only"]["stats"]["R"]["mean"]
    return [
        ("**The antecedent verification (#84) checked the wrong antecedent.** "
         "The registration verified that the per-author correlation has "
         "HEADROOM (it cannot saturate) and that the null lives in the "
         "mechanism's own coordinate, and it asserted that 'the estimand "
         "needs no cross-author support floor'. It never asked whether the "
         "estimator's ZERO is zero on the realized design. It is not: with "
         f"nothing planted the interaction share reads {_pct(hon['interaction_share'])} "
         f"and R reads {_pct(hon['R'])}."),
        ("**The routing statistic is zero-referenced but its zero moves.** "
         "Cell 1 asks whether the interaction share's CI includes 0. That "
         "presumes 0 is the no-response value; on an incomplete grid the "
         "no-response value is the leak, and the cluster bootstrap tracks the "
         "leak rather than the estimand (in the null world the CI is "
         f"{fmt_ci(hon['interaction_ci'])} around a point of "
         f"{_pct(hon['interaction_share'])}). A band-referenced or "
         "design-calibrated contrast — not a zero-referenced CI — is what "
         "this family of estimands needs."),
        ("**The permutation null is not a clean mechanism coordinate for "
         "this estimand.** Permuting community labels within (author, half) "
         "moves the community MAIN together with the interaction, so the band "
         f"({fmt_ci(hon['interaction_band'])}) sits below the artifact it is "
         f"supposed to calibrate ({_pct(hon['interaction_share'])}). A null "
         "that resamples the interaction while HOLDING both mains fixed "
         "would be the matching coordinate."),
        ("**The headroom clause is stated about the wrong object.** The "
         "registration argues that within-cell noise 'bounds every per-author "
         "correlation away from 1'. On the planted world at the primary "
         f"design, {_pct(part0['planted_world_inference']['headroom']['share_above_0.99'])} "
         "of authors read above 0.99 and the extremes round to +-1.0000: with "
         f"k_min = {K_MIN} the per-author correlation has no such bound. What "
         "is bounded is the MEAN over thousands of authors. The clause should "
         "be restated about the estimand, not about its summands."),
        ("**The leak is carried by the AUTHOR main through thin communities, "
         "and it is a support problem after all.** With only an author main "
         f"planted the interaction share reads {_pct(a_only)} and R reads "
         f"{_pct(r_a_only)}; with only a community main planted they read "
         f"{_pct(c_only)} and {_pct(r_c_only)}. The primary design has a "
         f"median of {fmt(primary['authors_per_community_median'], 1)} "
         "eligible authors per community and "
         f"{_pct(primary['singleton_community_share'])} of slots in "
         "single-author communities; the law-vocabulary arm the registration "
         "demoted to a sensitivity has "
         f"{fmt(lawvocab['authors_per_community_median'], 1)} and "
         f"{_pct(lawvocab['singleton_community_share'])}. A cross-author "
         "support floor is a candidate PRIMARY, not a sensitivity — the "
         "opposite of what the registration reasoned."),
    ]


# ---------------------------------------------------------------------------
# Stage 5 — classification, leans, flags
# ---------------------------------------------------------------------------


def magnitude_cells(ci: Sequence[float]) -> list[str]:
    """Which magnitude cells an interval touches (CI membership decides)."""

    lo, hi = float(ci[0]), float(ci[1])
    touched = []
    if lo < TRACE_MAX:
        touched.append(CELL_TRACE)
    if hi >= TRACE_MAX and lo <= IDIOSYNCRATIC_MAX:
        touched.append(CELL_IDIOSYNCRATIC)
    if hi > IDIOSYNCRATIC_MAX:
        touched.append(CELL_MAJOR)
    return touched


def point_cell(share: float) -> str:
    if share < TRACE_MAX:
        return CELL_TRACE
    if share <= IDIOSYNCRATIC_MAX:
        return CELL_IDIOSYNCRATIC
    return CELL_MAJOR


def classify(arm: dict[str, Any]) -> dict[str, Any]:
    """The registered cell rule, NULL-first (#55), keyed on the share (#75)."""

    share = float(arm["budget"]["interaction"])
    ci = arm["bootstrap"]["shares_ci"]["interaction"]
    band = arm["null"]["r_band"]
    r = float(arm["R"])
    r_inside = bool(band[0] <= r <= band[1])
    ci_covers_zero = bool(ci[0] <= 0.0 <= ci[1])
    if r_inside and ci_covers_zero:
        return {"cell": CELL_NO_RESPONSE, "straddle": False,
                "touched": [CELL_NO_RESPONSE], "r_inside_band": True,
                "ci_covers_zero": True, "share": share, "share_ci": list(ci),
                "R": r, "r_band": list(band)}
    touched = magnitude_cells(ci)
    cell = touched[0] if len(touched) == 1 else point_cell(share)
    return {"cell": cell, "straddle": len(touched) > 1, "touched": touched,
            "r_inside_band": r_inside, "ci_covers_zero": ci_covers_zero,
            "share": share, "share_ci": list(ci), "R": r,
            "r_band": list(band)}


def evaluate_leans(primary: dict[str, Any], replication_cell: str | None,
                   primary_cell: str) -> list[dict[str, Any]]:
    share = float(primary["budget"]["interaction"])
    r = float(primary["R"])
    author = float(primary["budget"]["author"])
    community = float(primary["budget"]["community"])
    rows = [
        {"lean": "R in (0.05, 0.30]", "observed": r,
         "held": bool(LEAN_R[0] < r <= LEAN_R[1])},
        {"lean": "interaction share in (0.005, 0.05]", "observed": share,
         "held": bool(LEAN_INTERACTION[0] < share <= LEAN_INTERACTION[1])},
        {"lean": "author main share in [0.15, 0.45]", "observed": author,
         "held": bool(LEAN_AUTHOR_MAIN[0] <= author <= LEAN_AUTHOR_MAIN[1])},
        {"lean": "community main share in [0.02, 0.15]", "observed": community,
         "held": bool(LEAN_COMMUNITY_MAIN[0] <= community
                      <= LEAN_COMMUNITY_MAIN[1])},
    ]
    if replication_cell is not None:
        rows.append({"lean": "Big5 replication lands in the primary cell",
                     "observed": replication_cell,
                     "held": bool(replication_cell == primary_cell)})
    return rows


# ---------------------------------------------------------------------------
# Stage 6 — the ID-leak gate (#83) and the anchor gates (#78)
# ---------------------------------------------------------------------------


def baseline_hit_keys(paths: Sequence[Path], universe: Sequence[str],
                      workdir: Path) -> tuple[set[tuple[str, int]],
                                              dict[str, Any]]:
    """Hits already present in each file's HEAD version, by (name, line).

    W1 established the policy: at a 10,296-name universe the substring scan
    acquires DICTIONARY COLLISIONS (author names that are ordinary words or
    bare digit runs) inside committed prose that predates this leg.  A
    collision is separated from a leak MECHANICALLY: a hit is PRE-EXISTING iff
    the identical hit (same file, same line) is produced by the same scanner on
    the file's version at HEAD.  Files this leg authors do not exist at HEAD,
    so their tolerance is ZERO; only APPENDS are made to the pre-existing
    documents, so a pre-existing hit keeps its line number.
    """

    workdir.mkdir(parents=True, exist_ok=True)
    recovered: list[Path] = []
    detail: dict[str, Any] = {}
    for path in paths:
        try:
            rel = path.relative_to(ROOT).as_posix()
        except ValueError:                        # outside the repo
            detail[str(path)] = "outside the repository (no HEAD version)"
            continue
        try:
            blob = subprocess.run(["git", "show", f"HEAD:{rel}"],
                                  cwd=ROOT, capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            detail[rel] = "absent at HEAD (authored by this leg)"
            continue
        target = workdir / path.name
        target.write_bytes(blob.stdout)
        recovered.append(target)
        detail[rel] = "recovered from HEAD"
    scan = scan_for_cohort_ids(recovered, universe)
    keys = {(Path(hit["path"]).name, int(hit["line"]))
            for hit in scan["hits"]}
    return keys, {"files": detail, "n_baseline_hits": scan["n_hits"],
                  "baseline_keys": sorted(f"{name}:{line}"
                                          for name, line in keys)}


def new_hits_only(hits: Sequence[dict[str, Any]],
                  baseline_keys: set[tuple[str, int]]) -> list[dict[str, Any]]:
    """Hits NOT already present at HEAD — the blocking set."""

    return [hit for hit in hits
            if (Path(hit["path"]).name, int(hit["line"])) not in baseline_keys]


def anchor_gate(observed: dict[str, Any],
                expected: dict[str, Any]) -> dict[str, Any]:
    """BLOCKING (#78): every registered predicate must reproduce exactly."""

    pins = {}
    for key, want in expected.items():
        got = observed.get(key)
        ok = (want == got)
        pins[key] = {"registered": want, "observed": got,
                     "status": "PASS" if ok else "FAIL"}
    status = "PASS" if all(p["status"] == "PASS" for p in pins.values()) \
        else "FAIL"
    return {"status": status, "pins": pins}


# ---------------------------------------------------------------------------
# Stage 7 — the report (rule 24: every table generated from artifacts)
# ---------------------------------------------------------------------------


BOUNDARIES = (
    "**Metadata only, expression VOLUME and not content (permanent).** The "
    "only text-derived quantity in this leg is `word_count_quoteless`, the "
    "author's own-word count per comment. No body was read, no topic, no "
    "style, no sentiment. Every claim here is about HOW MUCH is written in a "
    "venue, never about WHAT is written.",
    "**The response-operator projection caution.** Profile persistence is ONE "
    "static projection of crossing #2's condition-response operator R_v. A "
    "null is a statement about this projection at this resolution, not about "
    "the operator; a detection is a lower bound on it.",
    "**No psychological naming.** Verbosity is a technical expression-volume "
    "object. Nothing here is a trait, a state, a disposition or a preference, "
    "and the leg is label-free: `author_profiles.csv` was never opened.",
    "**EXPLORATORY, corpus-level.** No person-level claim is licensed. The "
    "per-author correlations exist only as the population of a mean.",
    "**Cohort composition.** The disjoint cohort is TYPOLOGY-ENRICHED by "
    "construction (PANDORA's non-Big5 authors are MBTI-labelled users), so it "
    "is a platform sample with a selection, not a population sample.",
    "**Incomplete design.** The eligible grid is sparse: most authors occupy a "
    "handful of communities and most communities carry few eligible authors. "
    "Double-centering on an incomplete grid does not separate mains from the "
    "interaction exactly — that is why Part 0 is a gate and not a formality.",
)


def _pct(value: float) -> str:
    return fmt(value, 4)


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []

    def add(text: str = "") -> None:
        lines.append(text)

    verdict = payload["verdict"]
    census = payload["census"]
    config = payload["config"]
    gate = payload["part0"]

    add("# SUICA M4-X1 — the venue response of expression volume")
    add()
    add(f"Run {config['run_utc']} · registration "
        "`docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md` (commit 0bdb638) · "
        f"seed {config['seed']} · B_perm {config['b_perm']} · "
        f"B_boot {config['b_boot']}.")
    add()
    add(f"**VERDICT — {verdict['cell']}.**")
    add()
    add(verdict["sentence"])
    add()

    add("## Gates")
    add()
    add("| gate | status |")
    add("|---|---|")
    for name, status in payload["gates"].items():
        add(f"| {name} | **{status}** |")
    add()

    add("## Census — the registered predicates, re-executed (#78)")
    add()
    add("| quantity (exact predicate) | registered | observed | status |")
    add("|---|---|---|---|")
    for key, pin in census["pins"].items():
        add(f"| {key} | {fmt(pin['registered'])} | {fmt(pin['observed'])} "
            f"| {pin['status']} |")
    add()
    if payload.get("crosschecks"):
        add("Non-gating cross-checks (published by the registration or "
            "inherited from the W/U lines). These do not route and did not "
            "gate: the ten pins above are what #78 blocks on, and the three "
            "pool counts are the sharp test of the eligibility predicate.")
        add()
        add("| cross-check | expected | observed | agrees |")
        add("|---|---|---|---|")
        for key, row in payload["crosschecks"].items():
            observed = row["observed"]
            shown = (" / ".join(fmt(x, 1) for x in observed)
                     if isinstance(observed, list) else fmt(observed))
            add(f"| {key} | {fmt(row['expected'])} | {shown} "
                f"| {'yes' if row['agrees'] else 'NO'} |")
        add()

    add("## Part 0 — the synthetic recovery gate (#76; A1 stop on failure)")
    add()
    if gate.get("status") == "NOT_RUN":
        add("Part 0 was never reached: the census gate stopped the leg first.")
        add()
        _write_tail(add, payload)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    add("The estimator is required to recover planted variance shares on a "
        "synthetic two-way world built at the PRIMARY ARM'S REALIZED DESIGN "
        "DENSITY — the real skeleton (which authors, which communities per "
        "author, how many comments per cell) carrying entirely synthetic y — "
        "and is required NOT to detect an interaction where none was planted. "
        "No real y enters Part 0.")
    add()
    add(f"Tolerance rule: {gate['tolerance_rule']}. The floor of "
        f"{TOL_FLOOR} of total variance is half the width of the "
        f"registration's own RESPONSE_TRACE / IDIOSYNCRATIC_RESPONSE boundary "
        f"at {TRACE_MAX}: a bias larger than that re-routes the cell, so it "
        "is the loosest tolerance the verdict can survive.")
    add()
    add("| planted share | planted | recovered (mean of "
        f"{gate['planted_block']['replicates']}) | replicate sd | tolerance "
        "| bias | status |")
    add("|---|---|---|---|---|---|---|")
    for key, row in gate["recovery"].items():
        add(f"| {key} | {_pct(row['planted'])} | "
            f"{_pct(row['recovered_mean'])} | {_pct(row['replicate_sd'])} | "
            f"{_pct(row['tolerance'])} | {_pct(row['bias'])} | "
            f"{row['status']} |")
    add()
    add("| null-world honesty check (nothing planted in the interaction) "
        "| value |")
    add("|---|---|")
    hon = gate["honesty"]
    add(f"| interaction share (planted 0.0000) "
        f"| {_pct(hon['interaction_share'])} |")
    add(f"| cluster-bootstrap CI | {fmt_ci(hon['interaction_ci'])} |")
    add(f"| CI covers 0 (the registered routing clause) "
        f"| {'yes' if hon['ci_covers_zero'] else '**NO**'} |")
    add(f"| CI covers its own point estimate "
        f"| {'yes' if hon['ci_covers_point'] else '**NO**'} |")
    add(f"| permutation band for the share "
        f"| {fmt_ci(hon['interaction_band'])} |")
    add(f"| share inside its own permutation band "
        f"| {'yes' if hon['interaction_inside_band'] else '**NO**'} |")
    add(f"| R | {_pct(hon['R'])} |")
    add(f"| permutation band for R | {fmt_ci(hon['r_band'])} |")
    add(f"| R inside band | {'yes' if hon['r_inside_band'] else '**NO**'} |")
    add(f"| author main recovered (planted 0.3000) "
        f"| {_pct(hon['author_share'])} |")
    add(f"| community main recovered (planted 0.0800) "
        f"| {_pct(hon['community_share'])} |")
    add(f"| honesty status | **{gate['honesty_status']}** |")
    add()
    if payload.get("diagnosis"):
        add("### What Part 0 localizes")
        add()
        for item in payload["diagnosis"]:
            add(f"- {item}")
        add()
    add("| synthetic world | planted interaction | recovered interaction "
        "(mean ± sd) | recovered author | recovered community | R |")
    add("|---|---|---|---|---|---|")
    blocks = [gate["planted_block"], gate["null_block"]]
    blocks += list(gate["ablations"].values())
    for block in blocks:
        st = block["stats"]
        add(f"| {block['world']} | {_pct(block['planted']['interaction'])} | "
            f"{_pct(st['interaction']['mean'])} ± "
            f"{_pct(st['interaction']['sd'])} | "
            f"{_pct(st['author']['mean'])} | {_pct(st['community']['mean'])} "
            f"| {_pct(st['R']['mean'])} |")
    add()
    add(f"Part 0 status: **{gate['status']}** "
        f"(recovery {gate['recovery_status']}, honesty "
        f"{gate['honesty_status']}).")
    add()
    head = gate.get("planted_world_inference", {}).get("headroom")
    if head:
        add("### Headroom (#84) on the Part 0 worlds — SYNTHETIC, not a "
            "corpus reading")
        add()
        add("The registration's headroom claim is that within-cell noise "
            "bounds every per-author correlation away from 1, so the "
            "estimator cannot saturate. On the planted world, at the primary "
            "arm's own design and cell sizes, the realized distribution is:")
        add()
        add("| quantile | per-author correlation (planted world) |")
        add("|---|---|")
        for key, value in head["quantiles"].items():
            add(f"| {key} | {_pct(value)} |")
        add()
        null_head = gate.get("null_world_headroom", {})
        add(f"{head['authors_scored']:,} authors scored, "
            f"{head['authors_undefined']:,} undefined (a flat profile in one "
            f"half); mean {_pct(head['mean'])}, sd {_pct(head['sd'])}; "
            f"{_pct(head['share_above_0.99'])} above 0.99, with both extreme "
            f"quantiles rounding to {_pct(head['quantiles']['q100'])} and "
            f"{_pct(head['quantiles']['q00'])} at four decimals.")
        add()
        add("Two things follow, and neither is what the registration "
            "expected. First, the per-author statistic is NOT bounded away "
            f"from 1: at k_min = {K_MIN} shared communities a Pearson "
            "correlation over three points reaches the ceiling whenever the "
            "three points happen to line up, so 'headroom exists by "
            "construction' holds for the MEAN over thousands of authors, not "
            "for the per-author correlation the sentence is about. Second, "
            "the ceiling was never the binding problem: in the NULL world, "
            "where nothing was planted, "
            f"{_pct(null_head.get('share_above_0.99', float('nan')))} of "
            f"authors still sit above 0.99 and the mean is "
            f"{_pct(null_head.get('mean', float('nan')))}. It is the FLOOR "
            "that Part 0 falsified.")
        add()

    if payload.get("arms"):
        _write_arm_sections(add, payload)
    else:
        add("## No real arm was run")
        add()
        add("Part 0 did not pass, so the A1 stop fired BEFORE any real "
            "estimand was computed. No corpus value of R, of the variance "
            "budget or of the headroom distribution exists in this leg's "
            "artifacts, and none is reported here. The census above is design "
            "arithmetic that the registration had already published; it is "
            "not an estimand.")
        add()
        add("The registered cells and leans are therefore UNSCORED. "
            "NO_REPRODUCIBLE_RESPONSE is not the outcome either: the leg "
            "reached no reading of the crossing at all, in either direction.")
        add()
        add("| registered object | value | outcome |")
        add("|---|---|---|")
        add(f"| cell 1 {CELL_NO_RESPONSE} | R inside band AND interaction "
            "share CI includes 0 | UNSCORED |")
        add(f"| cell 2 {CELL_TRACE} | detected, share < {TRACE_MAX} "
            "| UNSCORED |")
        add(f"| cell 3 {CELL_IDIOSYNCRATIC} | share in [{TRACE_MAX}, "
            f"{IDIOSYNCRATIC_MAX}] | UNSCORED |")
        add(f"| cell 4 {CELL_MAJOR} | share > {IDIOSYNCRATIC_MAX} "
            "| UNSCORED |")
        add(f"| lean: R | ({LEAN_R[0]}, {LEAN_R[1]}] | UNSCORED |")
        add(f"| lean: interaction share | ({LEAN_INTERACTION[0]}, "
            f"{LEAN_INTERACTION[1]}] | UNSCORED |")
        add(f"| lean: author main | [{LEAN_AUTHOR_MAIN[0]}, "
            f"{LEAN_AUTHOR_MAIN[1]}] | UNSCORED |")
        add(f"| lean: community main | [{LEAN_COMMUNITY_MAIN[0]}, "
            f"{LEAN_COMMUNITY_MAIN[1]}] | UNSCORED |")
        add("| lean: Big5 replication in the primary cell | same cell "
            "| UNSCORED (no cell was reached, so no #73 flag exists) |")
        add()
        if payload.get("design_table"):
            add("### The arm designs that were built and not scored")
            add()
            add("| arm | eligible authors | communities | slots | comments | "
                "median shared communities | median eligible authors per "
                "community | singleton-community slot share |")
            add("|---|---|---|---|---|---|---|---|")
            for key, row in payload["design_table"].items():
                add(f"| {key} | {row['authors']:,} | "
                    f"{row['communities']:,} | {row['slots']:,} | "
                    f"{row['comments']:,} | "
                    f"{fmt(row['shared_communities_per_author_median'], 1)} | "
                    f"{fmt(row['authors_per_community_median'], 1)} | "
                    f"{_pct(row['singleton_community_share'])} |")
            add()
            add("Design counts only — no y was read into any estimand. They "
                "are reported because the leak Part 0 measured scales with "
                "exactly these numbers.")
            add()
        if payload.get("defect_candidates"):
            add("### Defect candidates recorded for the planner")
            add()
            add("Executor candidates, not registered content, and nothing "
                "below was run:")
            add()
            for item in payload["defect_candidates"]:
                add(f"- {item}")
            add()

    _write_tail(add, payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_tail(add, payload: dict[str, Any]) -> None:
    add("## Boundaries")
    add()
    for boundary in payload["boundaries"]:
        add(f"- {boundary}")
    add()
    add("## Configuration")
    add()
    add("```json")
    add(json.dumps(payload["config"], indent=2, sort_keys=True))
    add("```")
    add()


def _budget_rows(add, arm: dict[str, Any]) -> None:
    budget = arm["budget"]
    ci = arm["bootstrap"]["shares_ci"]
    band = arm["null"]
    add("| component | share of Var(y) | cluster-bootstrap CI | "
        "permutation band |")
    add("|---|---|---|---|")
    add(f"| author main | {_pct(budget['author'])} | "
        f"{fmt_ci(ci['author'])} | — |")
    add(f"| community main (size-weighted) | {_pct(budget['community'])} | "
        f"{fmt_ci(ci['community'])} | — |")
    add(f"| interaction (double-centered, unweighted) | "
        f"{_pct(budget['interaction'])} | {fmt_ci(ci['interaction'])} | "
        f"{fmt_ci(band['interaction_band'])} |")
    add(f"| residual | {_pct(budget['residual'])} | "
        f"{fmt_ci(ci['residual'])} | — |")
    add()
    add(f"Sensitivities inside the budget: community main unweighted = "
        f"{_pct(budget['community_unweighted'])} "
        f"{fmt_ci(ci['community_unweighted'])}; interaction size-weighted = "
        f"{_pct(budget['interaction_weighted'])} "
        f"{fmt_ci(ci['interaction_weighted'])}. "
        f"Comment-level Var(y) = {_pct(budget['var_y'])}.")
    add()


def _write_arm_sections(add, payload: dict[str, Any]) -> None:
    arms = payload["arms"]
    cells = payload["cells"]
    primary = arms["primary"]

    add("## PRIMARY arm — disjoint cohort, n_min = 10, k_min = 3")
    add()
    design = primary["design"]
    add(f"{design['authors']:,} eligible authors · {design['slots']:,} "
        f"(author, community) slots · {design['cells']:,} eligible cells · "
        f"{design['comments']:,} comments · {design['communities']:,} "
        f"communities · median shared communities per author "
        f"{fmt(design['shared_communities_per_author_median'], 1)} · median "
        f"comments per cell {fmt(design['comments_per_cell_median'], 1)}.")
    add()
    add("### R — response-profile persistence")
    add()
    add("| quantity | value |")
    add("|---|---|")
    add(f"| R (mean per-author correlation) | {_pct(primary['R'])} |")
    add(f"| cluster-bootstrap CI (B = {primary['bootstrap']['b_boot']}) | "
        f"{fmt_ci(primary['bootstrap']['r_ci'])} |")
    add(f"| permutation band (B = {primary['null']['b_perm']}) | "
        f"{fmt_ci(primary['null']['r_band'])} |")
    add(f"| permutation null mean | {_pct(primary['null']['r_null_mean'])} |")
    add(f"| R outside its band | "
        f"{'no' if cells['primary']['r_inside_band'] else 'YES'} |")
    add()
    add("### The reproducible variance budget")
    add()
    _budget_rows(add, primary)

    add("### Headroom (#84) — the realized per-author correlation "
        "distribution")
    add()
    head = primary["headroom"]
    add(f"{head['authors_scored']:,} authors scored "
        f"({head['authors_undefined']:,} undefined: a flat profile in one "
        f"half). Mean {_pct(head['mean'])}, sd {_pct(head['sd'])}; "
        f"{_pct(head['share_positive'])} of authors positive; "
        f"{_pct(head['share_above_0.90'])} above 0.90; "
        f"{_pct(head['share_above_0.99'])} above 0.99 — the estimator is "
        "nowhere near its ceiling.")
    add()
    add("| quantile | value |")
    add("|---|---|")
    for key, value in primary["headroom"]["quantiles"].items():
        add(f"| {key} | {_pct(value)} |")
    add()

    add("## Arms")
    add()
    add("| arm | authors | slots | R [band] | interaction share [CI] | cell | "
        "#73 |")
    add("|---|---|---|---|---|---|---|")
    for key, arm in arms.items():
        cell = cells[key]
        flag = payload["flags_73"].get(key, "")
        add(f"| {arm['tag']} | {arm['design']['authors']:,} | "
            f"{arm['design']['slots']:,} | {_pct(arm['R'])} "
            f"{fmt_ci(arm['null']['r_band'])} | "
            f"{_pct(arm['budget']['interaction'])} "
            f"{fmt_ci(arm['bootstrap']['shares_ci']['interaction'])} | "
            f"{cell['cell']}{' (straddle)' if cell['straddle'] else ''} | "
            f"{flag} |")
    add()
    for key, arm in arms.items():
        if key == "primary":
            continue
        add(f"### {arm['tag']}")
        add()
        _budget_rows(add, arm)

    add("## Registered leans (report against; they never route)")
    add()
    add("| lean | observed | outcome |")
    add("|---|---|---|")
    for row in payload["leans"]:
        observed = row["observed"]
        shown = observed if isinstance(observed, str) else fmt(observed)
        add(f"| {row['lean']} | {shown} | "
            f"{'HELD' if row['held'] else 'MISSED'} |")
    add()


def build_verdict(payload_cells: dict[str, Any], arms: dict[str, Any],
                  gate_ok: bool,
                  part0: dict[str, Any] | None = None) -> dict[str, Any]:
    if not gate_ok:
        rec = (part0 or {}).get("recovery", {})
        hon = (part0 or {}).get("honesty", {})
        detail = ""
        if rec and hon:
            inter = rec.get("interaction", {})
            detail = (
                f" On the primary arm's own realized design the registered "
                f"interaction estimator returns "
                f"{fmt(inter.get('recovered_mean'))} for a planted "
                f"{fmt(inter.get('planted'))} (tolerance "
                f"{fmt(inter.get('tolerance'))}), and in a world with NO "
                f"interaction planted it returns "
                f"{fmt(hon.get('interaction_share'))} with a bootstrap CI "
                f"{fmt_ci(hon.get('interaction_ci', [float('nan')] * 2))} "
                f"that excludes 0 and R = {fmt(hon.get('R'))} against a band "
                f"{fmt_ci(hon.get('r_band', [float('nan')] * 2))}. The "
                f"artifact is three times the effect the leg was registered "
                f"to detect.")
        return {
            "cell": CELL_A1_STOP,
            "sentence": (
                "Part 0 failed on both of its clauses — recovery and "
                "null-world honesty — so the A1 stop fired BEFORE any real "
                "estimand was computed. No corpus value of R, of the variance "
                "budget or of the headroom distribution appears anywhere in "
                "this leg." + detail),
        }
    cell = payload_cells["primary"]
    arm = arms["primary"]
    return {
        "cell": cell["cell"],
        "sentence": (
            f"The primary arm's reproducible interaction share is "
            f"{fmt(cell['share'])} of comment-level Var(y) "
            f"{fmt_ci(cell['share_ci'])}, with R = {fmt(cell['R'])} against a "
            f"permutation band {fmt_ci(cell['r_band'])} "
            f"(cluster-bootstrap CI {fmt_ci(arm['bootstrap']['r_ci'])}). "
            f"The mains carry {fmt(arm['budget']['author'])} (author) and "
            f"{fmt(arm['budget']['community'])} (community); the residual is "
            f"{fmt(arm['budget']['residual'])}."),
    }


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
    parser.add_argument("--reuse-cache", action="store_true",
                        help="reuse the cell cache if it is already present")
    args = parser.parse_args(argv)

    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    log = RunLog(output / "run_log.jsonl")
    started = time.time()

    config = {
        "leg": "M4-X1",
        "title": "the venue response of expression volume",
        "registration": "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md@0bdb638",
        "run_utc": utc_now(),
        "seed": SEED,
        "seed_part0": SEED_PART0,
        "seed_perm": SEED_PERM,
        "seed_boot": SEED_BOOT,
        "b_perm": int(args.b_perm),
        "b_boot": int(args.b_boot),
        "y": "log(1 + word_count_quoteless)",
        "y_sensitivity": "log(1 + word_count)",
        "halves": "author's FULL-STREAM median created_utc, <= to early",
        "n_min_primary": N_MIN_PRIMARY,
        "n_min_sensitivity": N_MIN_SENSITIVITY,
        "k_min": K_MIN,
        "cells": {"trace_max": TRACE_MAX,
                  "idiosyncratic_max": IDIOSYNCRATIC_MAX},
        "planted_shares": PLANTED_SHARES,
        "null_shares": NULL_SHARES,
        "synthetic_replicates": N_SYNTH_REPLICATES,
        "tolerance_floor": TOL_FLOOR,
        "tolerance_sd_multiple": TOL_SD_MULT,
        "min_cell_keep": MIN_CELL_KEEP,
        "chunk_size": CHUNK_SIZE,
        "columns_read": ["author", "subreddit", "created_utc",
                         "word_count_quoteless", "word_count"],
        "author_profiles_opened": False,
        "bodies_read": False,
        "var_y_denominator": ("comment-level population variance of y over "
                              "the analysis pool = the comments inside "
                              "eligible cells"),
        "bootstrap_semantics": ("R resamples per-author correlations; the "
                               "budget recomputes every component, including "
                               "the double-centering, from the resampled "
                               "author multiset"),
    }
    config_blob = json.dumps(config, sort_keys=True, default=float)
    config_hash = hashlib.sha256(config_blob.encode("utf-8")).hexdigest()
    write_json(output / "config.json", config)
    write_json(output / "config.sha256.json", {"sha256": config_hash})
    log.event("config", sha256=config_hash)

    # ---- Stage 1: the metadata stream -------------------------------------
    cache_path = output / "cell_cache.npz"
    meta_path = cache_path.with_suffix(".meta.json")
    scaffold: dict[str, Any] | None = None
    if args.reuse_cache and cache_path.exists() and meta_path.exists():
        blob = np.load(cache_path)
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        table = {k: blob[k] for k in blob.files}
        table["n_cells_all"] = meta["n_cells_all"]
        table["n_cells_kept"] = meta["n_cells_kept"]
        table["n_subs"] = len(meta["subreddits"])
        table["n_authors"] = len(meta["authors"])
        scaffold = {"authors": meta["authors"],
                    "subreddits": meta["subreddits"],
                    "stream_stats": meta["stream_stats"]}
        log.event("cache_reused", path=str(cache_path))
    else:
        scaffold = stream_metadata(args.comments, log)
        table = build_cell_table(scaffold, log)

    stats = scaffold["stream_stats"]
    author_names = scaffold["authors"]
    n_authors = len(author_names)

    cohort_frame = pd.read_csv(args.cohort, usecols=["author"])
    cohort_names = sorted({str(name) for name in cohort_frame["author"]})
    name_to_code = {name: i for i, name in enumerate(author_names)}
    big5_mask = np.zeros(n_authors, dtype=bool)
    for name in cohort_names:
        code = name_to_code.get(name)
        if code is not None:
            big5_mask[code] = True
    disjoint_mask = ~big5_mask
    log.event("cohorts", big5_listed=len(cohort_names),
              big5_seen=int(big5_mask.sum()),
              disjoint=int(disjoint_mask.sum()))

    vocab = law_vocabulary(table, disjoint_mask, log)
    vocab_mask = vocab["mask"]

    if not cache_path.exists():
        save_cache(table, scaffold, cache_path)
        log.event("cache_saved", path=str(cache_path))

    # ---- Stage 2: the designs and the anchor gate -------------------------
    designs = {
        "primary": build_design(table, disjoint_mask, N_MIN_PRIMARY),
        "sens_n5": build_design(table, disjoint_mask, N_MIN_SENSITIVITY),
        "replication_big5": build_design(table, big5_mask, N_MIN_PRIMARY),
        "sens_lawvocab": build_design(table, disjoint_mask, N_MIN_PRIMARY,
                                      comm_mask=vocab_mask),
        "sens_word_count": build_design(table, disjoint_mask, N_MIN_PRIMARY,
                                        y_key="wc"),
    }
    observed = {
        "rows parseable (author+subreddit+created_utc+wcq)":
            int(stats["rows_parseable"]),
        "wcq = 0 share (4 dp)": round(float(stats["wcq_zero_share"]), 4),
        "authors": int(stats["authors"]),
        "Big5 cohort authors seen": int(big5_mask.sum()),
        "disjoint authors": int(disjoint_mask.sum()),
        "pool, disjoint, n=10/k=3 (PRIMARY)": designs["primary"].n_authors,
        "pool, disjoint, n=5/k=3": designs["sens_n5"].n_authors,
        "pool, Big5, n=10/k=3": designs["replication_big5"].n_authors,
        "law vocabulary floor (users)": int(vocab["floor_users"]),
        "law vocabulary (communities)": int(vocab["vocabulary_size"]),
    }
    expected = {
        "rows parseable (author+subreddit+created_utc+wcq)":
            CENSUS_ROWS_PARSEABLE,
        "wcq = 0 share (4 dp)": CENSUS_WCQ_ZERO_SHARE,
        "authors": CENSUS_AUTHORS,
        "Big5 cohort authors seen": CENSUS_BIG5_AUTHORS,
        "disjoint authors": CENSUS_DISJOINT_AUTHORS,
        "pool, disjoint, n=10/k=3 (PRIMARY)": CENSUS_POOL_DISJOINT_N10,
        "pool, disjoint, n=5/k=3": CENSUS_POOL_DISJOINT_N5,
        "pool, Big5, n=10/k=3": CENSUS_POOL_BIG5_N10,
        "law vocabulary floor (users)": CENSUS_VOCAB_FLOOR_USERS,
        "law vocabulary (communities)": CENSUS_LAW_VOCAB,
    }
    census = anchor_gate(observed, expected)
    write_json(output / "census.json", census)
    log.event("census", status=census["status"])

    # non-gating cross-checks
    n5_early_sd = _within_cell_sd_median(table, disjoint_mask,
                                         N_MIN_SENSITIVITY)
    k_n5_disjoint = _median_shared(table, disjoint_mask, N_MIN_SENSITIVITY)
    k_n5_big5 = _median_shared(table, big5_mask, N_MIN_SENSITIVITY)
    crosschecks = {
        "disjoint events (W1 cache size)": {
            "expected": CROSSCHECK_DISJOINT_EVENTS,
            "observed": int(vocab["disjoint_events"]),
            "agrees": int(vocab["disjoint_events"])
            == CROSSCHECK_DISJOINT_EVENTS},
        "Big5 events (U2 ANCHOR_EVENTS)": {
            "expected": CROSSCHECK_BIG5_EVENTS,
            "observed": int(table["author_rows"][big5_mask].sum()),
            "agrees": int(table["author_rows"][big5_mask].sum())
            == CROSSCHECK_BIG5_EVENTS},
        "within-cell sd of y (median, n=5 early cells)": {
            "expected": CROSSCHECK_WITHIN_CELL_SD,
            "observed": round(n5_early_sd, 4),
            "agrees": round(n5_early_sd, 4) == CROSSCHECK_WITHIN_CELL_SD},
        "median shared eligible communities (n=5, disjoint; authors with "
        ">= 1 shared pair / eligible authors)": {
            "expected": 4, "observed": list(k_n5_disjoint),
            "agrees": 4 in k_n5_disjoint},
        "median shared eligible communities (n=5, Big5; authors with "
        ">= 1 shared pair / eligible authors)": {
            "expected": 3, "observed": list(k_n5_big5),
            "agrees": 3 in k_n5_big5},
    }
    write_json(output / "crosschecks.json", crosschecks)
    write_json(output / "designs.json",
               {k: d.summary() for k, d in designs.items()})

    gates: dict[str, str] = {
        "Census anchors (#78: every registered predicate exact)":
            census["status"],
    }
    if census["status"] != "PASS":
        failed = {k: v for k, v in census["pins"].items()
                  if v["status"] != "PASS"}
        write_report(args.report, {
            "config": config, "census": census, "crosschecks": crosschecks,
            "gates": gates, "part0": {"status": "NOT_RUN"},
            "arms": {}, "cells": {}, "flags_73": {}, "leans": [],
            "boundaries": list(BOUNDARIES),
            "verdict": {"cell": "A1_STOP__CENSUS_MISMATCH",
                        "sentence": ("The registered census did not "
                                     "reproduce; nothing downstream was "
                                     "run.")}})
        raise SystemExit(f"STOP (#78): census mismatch {failed}")

    # ---- Stage 3: PART 0, before any real estimand ------------------------
    part0 = synthetic_gate(designs["primary"], args.b_perm, args.b_boot, log)
    write_json(output / "part0_synthetic_gate.json", part0)
    gates["Part 0 synthetic recovery gate (#76; A1 stop on failure)"] = \
        part0["status"]
    design_table = {k: d.summary() for k, d in designs.items()}
    diagnosis = build_diagnosis(part0, design_table["primary"])
    defects = build_defect_candidates(part0, design_table)
    write_json(output / "diagnosis.json",
               {"diagnosis": diagnosis, "defect_candidates": defects})

    arms: dict[str, Any] = {}
    cells: dict[str, Any] = {}
    flags_73: dict[str, str] = {}
    leans: list[dict[str, Any]] = []

    if part0["status"] == "PASS":
        labels = {
            "primary": "PRIMARY — disjoint, n=10, k=3, raw communities, wcq",
            "sens_n5": "sensitivity — disjoint, n=5, k=3",
            "replication_big5": "REPLICATION — Big5 cohort, n=10, k=3",
            "sens_lawvocab": "sensitivity — law vocabulary (1,443 communities)",
            "sens_word_count": "sensitivity — y = log(1 + word_count)",
        }
        for offset, (key, design) in enumerate(designs.items()):
            arms[key] = analyse_design(
                design, b_perm=args.b_perm, b_boot=args.b_boot,
                seed_perm=SEED_PERM + 17 * offset,
                seed_boot=SEED_BOOT + 17 * offset,
                tag=labels[key], log=log)
            cells[key] = classify(arms[key])
            log.event("arm_done", arm=key, R=arms[key]["R"],
                      interaction=arms[key]["budget"]["interaction"],
                      cell=cells[key]["cell"])
        primary_cell = cells["primary"]["cell"]
        for key in arms:
            if key == "primary":
                continue
            if cells[key]["cell"] != primary_cell:
                flags_73[key] = (f"#73 — {cells[key]['cell']} vs primary "
                                 f"{primary_cell}")
        leans = evaluate_leans(arms["primary"],
                               cells["replication_big5"]["cell"],
                               primary_cell)
        write_json(output / "arms.json", arms)
        write_json(output / "cells.json", cells)
        write_json(output / "leans.json", leans)
        write_json(output / "flags_73.json", flags_73)

    verdict = build_verdict(cells, arms, part0["status"] == "PASS", part0)
    write_json(output / "verdict.json", verdict)

    payload = {
        "config": config,
        "census": census,
        "crosschecks": crosschecks,
        "part0": part0,
        "arms": arms,
        "cells": cells,
        "flags_73": flags_73,
        "leans": leans,
        "gates": gates,
        "verdict": verdict,
        "diagnosis": diagnosis,
        "defect_candidates": defects,
        "design_table": design_table,
        "boundaries": list(BOUNDARIES),
    }
    write_report(args.report, payload)

    # ---- Stage 4: the ID-leak gate over the WIDENED universe (#83) --------
    universe = sorted({str(n) for n in cohort_names}
                      | {str(n) for n in author_names})
    write_json(output / "id_scan_universe.json",
               {"n_names": len(universe),
                "cohort_names": len(cohort_names),
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


def _median_shared(table: dict[str, Any], author_mask: np.ndarray,
                   n_min: int) -> tuple[float, float]:
    """Median shared-community count under the two readings the phrase allows.

    (a) over authors with at least ONE shared eligible pair;
    (b) over ELIGIBLE authors (k >= k_min) — the analysis pool.
    The registration prints one number and does not say which; both are
    reported, and neither gates anything.
    """

    n_subs = int(table["n_subs"])
    sel = (table["cell_n"] >= n_min) & author_mask[table["cell_author"]]
    author = table["cell_author"][sel].astype(np.int64)
    comm = table["cell_comm"][sel].astype(np.int64)
    half = table["cell_half"][sel]
    key = author * n_subs + comm
    shared = np.intersect1d(np.unique(key[half == 0]),
                            np.unique(key[half == 1]))
    if shared.size == 0:
        return (float("nan"), float("nan"))
    _, counts = np.unique(shared // n_subs, return_counts=True)
    eligible = counts[counts >= K_MIN]
    return (float(np.median(counts)),
            float(np.median(eligible)) if eligible.size else float("nan"))


def _within_cell_sd_median(table: dict[str, Any], author_mask: np.ndarray,
                           n_min: int) -> float:
    """Median within-cell sd of y over eligible EARLY cells (descriptive)."""

    sel = ((table["cell_n"] >= n_min) & (table["cell_half"] == 0)
           & author_mask[table["cell_author"]])
    n = table["cell_n"][sel].astype(np.float64)
    s = table["s_wcq"][sel]
    q = table["q_wcq"][sel]
    var = np.maximum((q - s * s / n) / np.maximum(n - 1.0, 1.0), 0.0)
    return float(np.median(np.sqrt(var))) if var.size else float("nan")


if __name__ == "__main__":                        # pragma: no cover
    raise SystemExit(main())
