#!/usr/bin/env python3
"""SUICA M4-X4 — the three-level decomposition and the ergodicity contrast.

Registered BEFORE the run in ``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``
(commit 42f0625, section "X4 — the three-level decomposition and the
ergodicity contrast").  This runner executes that registration and nothing
else.

PROVENANCE OF THE QUESTION (relayed 2026-08-19, the program OWNER's conference
input): the three-designs schema for personality measurement — (1) a one-shot
group measurement yields a BETWEEN-PERSON relation; (2) repeated measurement
of MANY people yields the AVERAGE WITHIN-PERSON relation; (3) repeated
measurement of ONE person yields THAT PERSON's relation.  X4 measures ONE
two-variable relation at all three levels and registers the level comparison —
the ergodicity contrast — as the verdict.

    x = log10(community share of all 17,640,062 parseable events)
        a GLOBAL fixed community attribute (46,214 communities)
    y = log1p(word_count_quoteless)                              (#70, pinned)
    order  = per-author stable sort by created_utc (ties keep stream order)
    halves = full-stream median of the author's own created_utc (<= early)
    pool   = >= 50 events in EACH half AND within-author sd(x) > 0 in EACH half

    level 1  beta_between = OLS slope of person-mean y on person-mean x
    level 2  beta_within  = within-(author, half)-centered pooled OLS slope,
                            computed per half and averaged over the two halves
    level 3  beta_{u,h}   = the per-(author, half) slope; ownership
                            rho_own(beta) = Pearson over authors of
                            (beta_early, beta_late)

    VERDICT  Delta_erg = beta_between - beta_within, paired author-cluster
             bootstrap (both slopes recomputed from the SAME author draw)

GOVERNANCE
----------
Metadata only.  The stream reads exactly four columns — ``author``,
``subreddit``, ``created_utc``, ``word_count_quoteless``.  NO text body is ever
read.  ``author_profiles.csv`` is NEVER opened; the leg is label-free end to
end (the Big5 cohort enters only as a NAME LIST that splits the corpus into two
disjoint author sets).  Caches and author listings live in gitignored
``results/`` and are never committed.  Aggregates only.  EXPLORATORY,
corpus-level; no person claims; no psychological naming (expression VOLUME is
a technical object, not a trait).

MACHINERY PROVENANCE (#56/#81 — the inherited object, imported BY FILE)
-----------------------------------------------------------------------
``RunLog``, ``write_json``, ``utc_now``, ``fmt``, ``fmt_ci``,
``percentile_ci``, ``scan_for_cohort_ids``, ``baseline_hit_keys``,
``new_hits_only``, ``anchor_gate``, ``_exact`` and ``_table`` come from the X2
runner (which imports X1b -> X1 -> U2/U2b).  So do the three pieces of X2
machinery this leg re-points at a NEW per-half scalar: ``ownership_null`` (the
author-pairing permutation), ``cluster_bootstrap_pairs`` (the author cluster
bootstrap on a paired statistic), ``rowwise_pearson``, and
``implied_phi_variance`` — whose quadratic is exactly the ownership mapping
this leg needs, now solved for the across-author SLOPE variance instead of the
across-author AR parameter variance.  ``order_and_halve`` is X2's, unchanged.
They are BOUND, not copied.

X4's event cache is FRESH: X2's cache carries no community attribute x, and
this leg's pool predicate (sd(x) > 0 in each half) is not X2's.
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

# --- Part 0, the realized-skeleton gate ------------------------------------

N_SYNTH_REPLICATES = 8              # registration pin
TOL_SD_MULT = 3.0                   # registration pin
TOL_FLOOR_RHO = 0.02                # registration pin: max(0.02, 3 x rep sd)
TOL_DELTA_SCALE_FRAC = 0.02         # registration pin: 2% of the planted scale
RHO_TRUE_TARGET = 0.50              # registration pin: #76 operating point
RHO_PRICE_LOW = 0.15                # the matched world for the 0.15 region

# Planted world parameters (RECORDED implementation choices; the registration
# fixes the world STRUCTURE, not these numbers.  They are round numbers chosen
# before the run and never tuned: no real-data quantity informs them, and no
# routing threshold depends on their values except through the derived
# analytic Delta = gamma and the derived ownership mapping.)
BETA_PLANT = -0.10                  # the one slope of the ergodic world
GAMMA_PLANT = 0.25                  # a_u = gamma * xbar_u  ->  Delta = gamma
SD_A = 0.5                          # sd of the person intercept
SD_E = 1.0                          # sd of the event noise

# --- #87 boundary REGIONS --------------------------------------------------
# The CENTRES are registration pins.  The HALF-WIDTHS are PRICED IN-LEG from
# Part 0's realized bootstrap half-widths on the matched planted worlds (#88a)
# and are pinned to a timestamped artifact BEFORE any real-arm number exists.

BOUNDARY_RHO_LOW = 0.15             # registration pin (centre)
BOUNDARY_RHO_HIGH = 0.50            # registration pin (centre)
BOUNDARY_DELTA_CENTRE = 0.0         # registration pin (centre)

# --- cells (NULL-first #55) ------------------------------------------------

CELL_INDIST = "LEVELS_INDISTINGUISHABLE"
CELL_SAME_SIGN = "NONERGODIC_SAME_SIGN"
CELL_SIGN_FLIP = "NONERGODIC_SIGN_FLIP"
# Completeness fallback (registration silent; recorded).  The registered cell 3
# requires BOTH slopes detected; a Delta that excludes 0 with point signs that
# differ but a slope whose own CI covers 0 has not established a flip.
CELL_SIGN_UNRESOLVED = "NONERGODIC_SIGN_UNRESOLVED"
CELL_A1_STOP = "A1_STOP__SYNTHETIC_GATE_FAILED"

CELL_NOT_OWNED = "NOT_OWNED"
CELL_AT_LOW = "AT_BOUNDARY(0.15)"
CELL_WEAK = "WEAKLY_OWNED"
CELL_AT_HIGH = "AT_BOUNDARY(0.50)"
CELL_STRONG = "STRONGLY_OWNED"

# --- inherited anchors (BLOCKING under #78) --------------------------------

ANCHOR_ROWS_PARSEABLE = 17_640_062
ANCHOR_AUTHORS = 10_296
ANCHOR_BIG5_AUTHORS = 1_401
ANCHOR_DISJOINT_AUTHORS = 8_895

# --- the X4 census (planner arithmetic, BLOCKING under #78) ----------------

ANCHOR_COMMUNITIES = 46_214
ANCHOR_X_MIN = -7.25
ANCHOR_X_MAX = -1.14
ANCHOR_POOL_DISJOINT = 8_004
ANCHOR_POOL_BIG5 = 1_112
ANCHOR_SDX_DISJOINT = (0.805, 0.965, 1.111)     # q25 / median / q75
ANCHOR_SDX_BIG5 = (0.660, 0.856, 1.013)
ANCHOR_DISTINCT_COMM_DISJOINT = 64.0            # median over authors
ANCHOR_DISTINCT_COMM_BIG5 = 55.0
ANCHOR_TOP1_DISJOINT = (0.259, 0.577)           # median / q90
ANCHOR_TOP1_BIG5 = (0.329, 0.743)

# --- recorded implementation choices (registration silent) -----------------

CHUNK_SIZE = 2_000_000
CACHE_VERSION = 1

SEED_PART0 = SEED + 1               # world draws (#76: derived, never chosen)
SEED_PERM = SEED + 2                # permutation nulls
SEED_BOOT = SEED + 3                # cluster bootstraps

DEFAULT_COMMENTS = Path(
    "/Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/"
    "all_comments_since_2015.csv")
DEFAULT_COHORT = ROOT / "results/m4_sr0_recon/cohort_authors.csv"
DEFAULT_OUTPUT = ROOT / "results/m4_x4_three_levels"
DEFAULT_REPORT = ROOT / "reports/SUICA_M4_X4_THREE_LEVELS_REPORT.md"

X2_SCRIPT = ROOT / "scripts/run_suica_m4_x2_volume_path.py"

COMMITTED_FILES = (
    ROOT / "reports/SUICA_M4_X4_THREE_LEVELS_REPORT.md",
    ROOT / "scripts/run_suica_m4_x4_three_levels.py",
    ROOT / "tests/test_m4_x4_three_levels.py",
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


X2 = load_module("suica_m4_x2_for_x4", X2_SCRIPT)

write_json = X2.write_json
utc_now = X2.utc_now
fmt = X2.fmt
fmt_ci = X2.fmt_ci
RunLog = X2.RunLog
percentile_ci = X2.percentile_ci
scan_for_cohort_ids = X2.scan_for_cohort_ids
baseline_hit_keys = X2.baseline_hit_keys
new_hits_only = X2.new_hits_only
anchor_gate = X2.anchor_gate
_exact = X2._exact
_table = X2._table
_Interner = X2._Interner
_sorted_remap = X2._sorted_remap
order_and_halve = X2.order_and_halve
rowwise_pearson = X2.rowwise_pearson
ownership_null = X2.ownership_null
cluster_bootstrap_pairs = X2.cluster_bootstrap_pairs
implied_phi_variance = X2.implied_phi_variance


# ---------------------------------------------------------------------------
# Stage 1 — the event stream (one pass; no bodies, no labels)
# ---------------------------------------------------------------------------


def stream_events(comments_path: Path, log: RunLog) -> dict[str, Any]:
    """Stream the comments file for the four metadata columns X4 needs."""

    columns = ["author", "subreddit", "created_utc", "word_count_quoteless"]
    log.event("stream_start", comments_path=str(comments_path),
              columns=columns, note="no body column requested")
    authors = _Interner()
    subreddits = _Interner()
    author_parts: list[np.ndarray] = []
    subreddit_parts: list[np.ndarray] = []
    created_parts: list[np.ndarray] = []
    wcq_parts: list[np.ndarray] = []
    rows_streamed = 0
    rows_parseable = 0
    wcq_zero = 0
    chunks = 0

    for chunk in pd.read_csv(
        comments_path,
        usecols=columns,
        chunksize=CHUNK_SIZE,
        dtype={"author": "str", "subreddit": "str"},
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
        author_parts.append(authors.encode(chunk["author"][keep]))
        subreddit_parts.append(subreddits.encode(chunk["subreddit"][keep]))
        created_parts.append(created[keep].to_numpy(np.float64))
        wcq_parts.append(wcq_keep.astype(np.int32))
        log.event("stream_chunk", chunk=chunks, rows_streamed=rows_streamed,
                  rows_parseable=rows_parseable)

    author_raw = np.concatenate(author_parts)
    subreddit_raw = np.concatenate(subreddit_parts)
    created = np.concatenate(created_parts)
    wcq = np.concatenate(wcq_parts)
    del author_parts, subreddit_parts, created_parts, wcq_parts

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
        "authors": author_names,
        "subreddits": subreddit_names,
        "stream_stats": stats,
    }


def community_x(subreddit_code: np.ndarray, n_subs: int
                ) -> tuple[np.ndarray, np.ndarray]:
    """x_c = log10(community share of ALL parseable events).

    The registration fixes x as a GLOBAL community attribute over the full
    stream: every parseable event contributes to the share, pool membership is
    irrelevant to it.  A community that appears at all has count >= 1, so the
    logarithm is always finite and the range is bounded below by
    log10(1 / rows_parseable).
    """

    counts = np.bincount(subreddit_code, minlength=n_subs).astype(np.int64)
    total = float(counts.sum())
    with np.errstate(divide="ignore"):
        x = np.log10(counts.astype(np.float64) / total)
    return x, counts


def build_event_cache(scaffold: dict[str, Any], big5_mask: np.ndarray,
                      log: RunLog) -> dict[str, Any]:
    """The pool skeleton: contiguous per-author event ranges with x attached.

    The pool predicate is the registration's, in two clauses: >= 50 events in
    EACH half (X2's floor, inherited), AND within-author sd(x) > 0 in EACH half
    (X4's own clause — a half in which the author never left one community
    carries no within-half x variation and cannot contribute a level-2 or
    level-3 slope at all).

    THE SD CLAUSE IS EVALUATED THE WAY THE CENSUS EVALUATED IT: ``np.std`` on
    the half's own contiguous x slice, tested ``> 0``.  This matters and is
    recorded rather than hidden.  numpy's two-pass sd uses PAIRWISE summation
    inside the slice; on a half whose x is mathematically constant the computed
    sd is not always exactly 0, and the registered anchors (8,004 / 1,112) are
    the set that float path produces.  A grouped (sequential-summation)
    accumulation gives 8,008 / 1,114 and the mathematically exact clause
    (min == max) gives 8,000 / 1,103.  The anchored path is reproduced here
    EXACTLY; the 13 mathematically constant cells it admits are then handled
    where they belong — by the level-3 estimator's own degeneracy rule, which
    returns NaN for a cell with no x spread and counts it (X2's precedent).
    They contribute exactly 0 to the level-1 and level-2 pooled sums.
    """

    author_code = scaffold["author_code"]
    created = scaffold["created_utc"]
    n_authors = len(scaffold["authors"])
    n_subs = len(scaffold["subreddits"])

    x_by_comm, comm_counts = community_x(scaffold["subreddit_code"], n_subs)
    log.event("community_x", communities=int(n_subs),
              x_min=float(x_by_comm.min()), x_max=float(x_by_comm.max()),
              total_events=int(comm_counts.sum()))

    order, half, medians, counts = order_and_halve(author_code, created,
                                                   n_authors)
    a_sorted = author_code[order]
    comm_sorted = scaffold["subreddit_code"][order]
    wcq_sorted = scaffold["wcq"][order]
    x_sorted = x_by_comm[comm_sorted]
    del order
    log.event("halves_assigned", early_rows=int((half == 0).sum()),
              late_rows=int((half == 1).sum()))

    # Per-(author, half) event counts over the WHOLE stream (x-only; #57: no y
    # quantity is touched here and none is needed to build the pool).
    key = a_sorted.astype(np.int64) * 2 + half.astype(np.int64)
    size = 2 * n_authors
    cell_n = np.bincount(key, minlength=size).astype(np.int64)
    n_early = cell_n[0::2]
    n_late = cell_n[1::2]

    floor_ok = (n_early >= POOL_FLOOR_PRIMARY) & (n_late >= POOL_FLOOR_PRIMARY)
    starts = np.concatenate(([0], np.cumsum(counts)[:-1])).astype(np.int64)
    spread_ok = np.zeros(n_authors, dtype=bool)
    constant_half = np.zeros(n_authors, dtype=bool)
    for code in np.flatnonzero(floor_ok):
        s0 = int(starts[code])
        n_e = int(n_early[code])
        n_t = int(counts[code])
        early = x_sorted[s0:s0 + n_e]
        late = x_sorted[s0 + n_e:s0 + n_t]
        spread_ok[code] = bool(np.std(early, ddof=1) > 0.0
                               and np.std(late, ddof=1) > 0.0)
        constant_half[code] = bool(early.min() == early.max()
                                   or late.min() == late.max())
    pool_mask = floor_ok & spread_ok
    pool_codes = np.flatnonzero(pool_mask).astype(np.int32)
    log.event("pool", floor=POOL_FLOOR_PRIMARY,
              authors_passing_floor=int(floor_ok.sum()),
              authors_passing_floor_and_spread=int(pool_mask.sum()),
              dropped_by_spread_clause=int((floor_ok & ~spread_ok).sum()),
              constant_half_admitted=int((pool_mask & constant_half).sum()),
              disjoint=int((pool_mask & ~big5_mask).sum()),
              big5=int((pool_mask & big5_mask).sum()))

    keep_event = pool_mask[a_sorted]
    cache = {
        "pool_author_code": pool_codes,
        "pool_is_big5": big5_mask[pool_codes],
        "n_early": n_early[pool_codes].astype(np.int64),
        "n_total": counts[pool_codes].astype(np.int64),
        "ev_comm": comm_sorted[keep_event].astype(np.int32),
        "ev_x": x_sorted[keep_event].astype(np.float64),
        "ev_wcq": wcq_sorted[keep_event].astype(np.int32),
        "comm_x": x_by_comm,
        "comm_count": comm_counts,
        "author_median_utc": medians,
        "author_rows": counts.astype(np.int64),
        "n_subs": n_subs,
        "n_authors": n_authors,
    }
    cache["offsets"] = np.concatenate(
        ([0], np.cumsum(cache["n_total"]))).astype(np.int64)
    log.event("event_cache_built", pool_authors=int(pool_codes.size),
              pool_events=int(cache["offsets"][-1]),
              corpus_events=int(a_sorted.size))
    return cache


CACHE_ARRAYS = ("pool_author_code", "pool_is_big5", "offsets", "n_early",
                "n_total", "ev_comm", "ev_x", "ev_wcq", "comm_x",
                "comm_count", "author_median_utc", "author_rows")


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
        "note": "gitignored; metadata only; no bodies, no labels; x attached",
    })


def load_cache(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = np.load(path)
    meta = json.loads(path.with_suffix(".meta.json").read_text("utf-8"))
    cache = {k: payload[k] for k in CACHE_ARRAYS}
    cache["n_subs"] = int(meta["n_subs"])
    cache["n_authors"] = int(meta["n_authors"])
    return cache, meta


# ---------------------------------------------------------------------------
# Stage 2 — the census (x-only; #57: NO x-y quantity is evaluated here)
# ---------------------------------------------------------------------------


def pool_author_of_event(cache: dict[str, Any]) -> np.ndarray:
    """Local pool-author index for every cached event (contiguous ranges)."""

    return np.repeat(np.arange(cache["n_total"].size, dtype=np.int64),
                     cache["n_total"])


def within_author_sd_x(cache: dict[str, Any]) -> np.ndarray:
    """WITHIN-AUTHOR sd(x): the mean of the author's TWO HALF sd(x) values.

    The pool clause is per half, and so is this descriptor: it is the average
    of the early-half and late-half population sd of x, which is the
    definition that reproduces the registered census quantiles
    (0.805 / 0.965 / 1.111 disjoint, 0.660 / 0.856 / 1.013 Big5).  Pooling both
    halves into one sd instead reads 0.834 / 0.999 / 1.148 — a different
    quantity, because an author who drifts between communities across the two
    halves adds BETWEEN-half spread that no within-half slope can use.
    """

    n_total = cache["n_total"].astype(np.int64)
    n_early = cache["n_early"].astype(np.int64)
    n_authors = int(n_total.size)
    who = pool_author_of_event(cache)
    local = np.arange(who.size, dtype=np.int64) - np.repeat(
        cache["offsets"][:-1], n_total)
    half = (local >= np.repeat(n_early, n_total)).astype(np.int64)
    key = who * 2 + half
    size = 2 * n_authors
    x = cache["ev_x"]
    cnt = np.bincount(key, minlength=size).astype(np.float64)
    s = np.bincount(key, weights=x, minlength=size)
    q = np.bincount(key, weights=x * x, minlength=size)
    var = q / cnt - (s / cnt) ** 2
    sd = np.sqrt(np.maximum(var, 0.0))
    return 0.5 * (sd[0::2] + sd[1::2])


def community_profile(cache: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """(distinct communities, top-1 community share) per pool author."""

    who = pool_author_of_event(cache)
    comm = cache["ev_comm"].astype(np.int64)
    n_authors = cache["n_total"].size
    key = who * cache["n_subs"] + comm
    order = np.argsort(key, kind="stable")
    key_sorted = key[order]
    # Run-length encode the (author, community) pairs.
    new_run = np.empty(key_sorted.size, dtype=bool)
    new_run[0] = True
    new_run[1:] = key_sorted[1:] != key_sorted[:-1]
    run_start = np.flatnonzero(new_run)
    run_len = np.diff(np.append(run_start, key_sorted.size))
    run_author = who[order][run_start]
    distinct = np.bincount(run_author, minlength=n_authors).astype(np.int64)
    top1 = np.zeros(n_authors, dtype=np.int64)
    np.maximum.at(top1, run_author, run_len)
    share = top1.astype(np.float64) / cache["n_total"].astype(np.float64)
    return distinct, share


def census_quantities(cache: dict[str, Any], sel: np.ndarray) -> dict[str, Any]:
    """The registered census predicates for one cohort selection."""

    sd_x = within_author_sd_x(cache)[sel]
    distinct, top1 = community_profile(cache)
    return {
        "pool_authors": int(sel.sum()),
        "sd_x_q25": float(np.percentile(sd_x, 25)),
        "sd_x_median": float(np.percentile(sd_x, 50)),
        "sd_x_q75": float(np.percentile(sd_x, 75)),
        "distinct_communities_median": float(np.median(distinct[sel])),
        "top1_share_median": float(np.percentile(top1[sel], 50)),
        "top1_share_q90": float(np.percentile(top1[sel], 90)),
    }


# ---------------------------------------------------------------------------
# Stage 3 — the realized skeleton (x-only) and the three levels
# ---------------------------------------------------------------------------


PRECISION_FLOOR_DEN = 1.0   # recorded, x-only, pinned before any real number


class Skeleton:
    """One arm's realized (author, half) skeleton — x-only, no y anywhere.

    Everything in here is fixed by the corpus's community attribute and the
    half split, so it can be (and is) built BEFORE the region pricing and
    before a single y value is read into an estimand.  The y-carrying
    quantities live in :func:`levels`, which takes a y vector — the real one
    once, and a planted one per Part 0 replicate.
    """

    def __init__(self, key: str, label: str, cache: dict[str, Any],
                 sel: np.ndarray, x_stats: dict[str, np.ndarray],
                 *, with_events: bool) -> None:
        codes = np.flatnonzero(sel).astype(np.int64)
        self.key = key
        self.label = label
        self.codes = codes
        self.n_authors = int(codes.size)
        for name in ("n_e", "n_l", "den_e", "den_l", "degenerate_e",
                     "degenerate_l", "xbar", "n_u"):
            setattr(self, name, x_stats[name][codes])
        self.ok = ~self.degenerate_e & ~self.degenerate_l
        self.precise = (self.ok & (self.den_e >= PRECISION_FLOOR_DEN)
                        & (self.den_l >= PRECISION_FLOOR_DEN))
        self.n_events = int(self.n_u.sum())
        self.events = None
        if with_events:
            self.events = self._event_view(cache)

    def _event_view(self, cache: dict[str, Any]) -> dict[str, Any]:
        offs = cache["offsets"]
        take = np.concatenate([np.arange(offs[c], offs[c + 1], dtype=np.int64)
                               for c in self.codes])
        x = cache["ev_x"][take]
        n_u = self.n_u.astype(np.int64)
        who = np.repeat(np.arange(self.n_authors, dtype=np.int64), n_u)
        local = np.arange(take.size, dtype=np.int64) - np.repeat(
            np.concatenate(([0], np.cumsum(n_u)[:-1])), n_u)
        half = (local >= np.repeat(self.n_e.astype(np.int64), n_u)
                ).astype(np.int64)
        key = who * 2 + half
        size = 2 * self.n_authors
        cell_n = np.bincount(key, minlength=size).astype(np.float64)
        cell_sx = np.bincount(key, weights=x, minlength=size)
        dev_x = x - (cell_sx / cell_n)[key]
        return {"x": x, "key": key, "who": who, "cell_n": cell_n,
                "dev_x": dev_x, "size": size, "n_events": int(take.size)}

    def census(self) -> dict[str, Any]:
        return {
            "arm": self.key,
            "label": self.label,
            "authors": self.n_authors,
            "events": self.n_events,
            "cells": 2 * self.n_authors,
            "authors_with_a_constant_half": int((~self.ok).sum()),
            "authors_scored_at_level_3": int(self.ok.sum()),
            "authors_above_the_precision_floor": int(self.precise.sum()),
            "median_events_per_half": float(np.median(
                0.5 * (self.n_e + (self.n_u - self.n_e)))),
            "median_den_early": float(np.median(self.den_e[self.ok])),
            "median_den_late": float(np.median(self.den_l[self.ok])),
            "min_den_early": float(np.min(self.den_e[self.ok])),
            "min_den_late": float(np.min(self.den_l[self.ok])),
        }


def x_only_stats(cache: dict[str, Any]) -> dict[str, np.ndarray]:
    """Per-(pool author, half) x moments: counts, den, and the exact
    degeneracy flag.  ``den = sum (x - xbar_cell)^2`` by the stable two-pass;
    ``degenerate`` is the EXACT predicate ``min(x) == max(x)`` in the cell."""

    n_total = cache["n_total"].astype(np.int64)
    n_early = cache["n_early"].astype(np.int64)
    n_authors = int(n_total.size)
    who = pool_author_of_event(cache)
    local = np.arange(who.size, dtype=np.int64) - np.repeat(
        cache["offsets"][:-1], n_total)
    half = (local >= np.repeat(n_early, n_total)).astype(np.int64)
    key = who * 2 + half
    size = 2 * n_authors
    x = cache["ev_x"]
    cell_n = np.bincount(key, minlength=size).astype(np.float64)
    cell_sx = np.bincount(key, weights=x, minlength=size)
    dev = x - (cell_sx / cell_n)[key]
    den = np.bincount(key, weights=dev * dev, minlength=size)
    xmin = np.full(size, np.inf)
    xmax = np.full(size, -np.inf)
    np.minimum.at(xmin, key, x)
    np.maximum.at(xmax, key, x)
    degenerate = xmin == xmax
    return {
        "n_e": cell_n[0::2], "n_l": cell_n[1::2],
        "den_e": den[0::2], "den_l": den[1::2],
        "degenerate_e": degenerate[0::2], "degenerate_l": degenerate[1::2],
        "xbar": np.bincount(who, weights=x, minlength=n_authors)
        / n_total.astype(np.float64),
        "n_u": n_total.astype(np.float64),
    }


def cell_moments(sk: Skeleton, y: np.ndarray) -> dict[str, np.ndarray]:
    """The y-carrying per-(author, half) sufficient statistics.

    ``num_{u,h} = sum (x - xbar_{u,h})(y - ybar_{u,h})`` by the stable
    two-pass; ``den`` is x-only and already on the skeleton.  A cell whose x is
    exactly constant contributes 0 to both, which is its exact mathematical
    contribution.
    """

    ev = sk.events
    key = ev["key"]
    size = ev["size"]
    cell_sy = np.bincount(key, weights=y, minlength=size)
    dev_y = y - (cell_sy / ev["cell_n"])[key]
    num = np.bincount(key, weights=ev["dev_x"] * dev_y, minlength=size)
    ybar = np.bincount(ev["who"], weights=y, minlength=sk.n_authors) / sk.n_u
    num_e = np.where(sk.degenerate_e, 0.0, num[0::2])
    num_l = np.where(sk.degenerate_l, 0.0, num[1::2])
    return {"num_e": num_e, "num_l": num_l,
            "den_e": np.where(sk.degenerate_e, 0.0, sk.den_e),
            "den_l": np.where(sk.degenerate_l, 0.0, sk.den_l),
            "ybar": ybar, "xbar": sk.xbar}


def three_levels(mom: dict[str, np.ndarray]) -> dict[str, float]:
    """Levels 1 and 2 and the verdict statistic, from per-author scalars."""

    xb, yb = mom["xbar"], mom["ybar"]
    n = float(xb.size)
    sx, sy = xb.sum(), yb.sum()
    sxy = float(xb @ yb)
    sxx = float(xb @ xb)
    syy = float(yb @ yb)
    cov = sxy - sx * sy / n
    vx = sxx - sx * sx / n
    vy = syy - sy * sy / n
    beta_between = cov / vx
    r_between = cov / math.sqrt(vx * vy) if vx > 0 and vy > 0 else float("nan")
    slope_e = float(mom["num_e"].sum() / mom["den_e"].sum())
    slope_l = float(mom["num_l"].sum() / mom["den_l"].sum())
    beta_within = 0.5 * (slope_e + slope_l)
    return {
        "beta_between": float(beta_between),
        "r_between": float(r_between),
        "beta_within": float(beta_within),
        "beta_within_early": slope_e,
        "beta_within_late": slope_l,
        "delta_erg": float(beta_between - beta_within),
    }


def per_cell_slopes(sk: Skeleton, mom: dict[str, np.ndarray]
                    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Level 3: beta_{u,h}.  A degenerate cell returns NaN and is counted."""

    with np.errstate(invalid="ignore", divide="ignore"):
        beta_e = np.where(sk.degenerate_e, np.nan, mom["num_e"] / sk.den_e)
        beta_l = np.where(sk.degenerate_l, np.nan, mom["num_l"] / sk.den_l)
    ok = np.isfinite(beta_e) & np.isfinite(beta_l)
    return beta_e, beta_l, ok


def dispersion(beta_e: np.ndarray, beta_l: np.ndarray, ok: np.ndarray
               ) -> dict[str, float]:
    """True Var(beta) by CROSS-HALF COVARIANCE, and the headroom about the
    mean it buys.

    The two halves' estimation errors are statistically unrelated given the
    skeleton, so
    Cov(beta_early, beta_late) estimates the across-author variance of the
    underlying slope with the per-half estimation noise removed — the same
    cross-half device the U/W lines use for reproducible variance.  HEADROOM
    (recorded definition): the +-1.96 sd_true interval about the mean slope,
    plus the share of authors a normal approximation would place on the far
    side of zero.  It is an annotation of what the dispersion buys, not an
    estimator of any person's slope.
    """

    e, l = beta_e[ok], beta_l[ok]
    n = e.size
    cov = float(np.cov(e, l, ddof=1)[0, 1])
    var_e = float(np.var(e, ddof=1))
    var_l = float(np.var(l, ddof=1))
    mean_beta = float(np.mean(0.5 * (e + l)))
    sd_true = math.sqrt(cov) if cov > 0 else float("nan")
    out = {
        "authors": int(n),
        "mean_beta": mean_beta,
        "var_observed_early": var_e,
        "var_observed_late": var_l,
        "var_true_cross_half": cov,
        "sd_true": sd_true,
        "reliability_share_early": cov / var_e if var_e > 0 else float("nan"),
        "reliability_share_late": cov / var_l if var_l > 0 else float("nan"),
    }
    if cov > 0:
        out["headroom_lo"] = mean_beta - 1.96 * sd_true
        out["headroom_hi"] = mean_beta + 1.96 * sd_true
        out["share_across_zero"] = float(
            0.5 * math.erfc(abs(mean_beta) / (sd_true * math.sqrt(2.0))))
    else:
        out["headroom_lo"] = float("nan")
        out["headroom_hi"] = float("nan")
        out["share_across_zero"] = float("nan")
    return out


def paired_level_bootstrap(mom: dict[str, np.ndarray], b_boot: int, seed: int
                           ) -> dict[str, Any]:
    """Paired author-cluster bootstrap: ONE author draw, BOTH slopes redone.

    Every quantity the verdict needs is a ratio of SUMS OF PER-AUTHOR SCALARS,
    so a resample of authors is a resample of those scalars and the whole
    bootstrap is vectorized (no per-author Python loop x B).
    """

    rng = np.random.default_rng(seed)
    xb, yb = mom["xbar"], mom["ybar"]
    ne, de = mom["num_e"], mom["den_e"]
    nl, dl = mom["num_l"], mom["den_l"]
    n = int(xb.size)
    between = np.empty(b_boot)
    within = np.empty(b_boot)
    block = 100
    for start in range(0, b_boot, block):
        rows = min(block, b_boot - start)
        idx = rng.integers(0, n, size=(rows, n))
        bx = xb[idx]
        by = yb[idx]
        sx = bx.sum(axis=1)
        sy = by.sum(axis=1)
        cov = (bx * by).sum(axis=1) - sx * sy / n
        vx = (bx * bx).sum(axis=1) - sx * sx / n
        between[start:start + rows] = cov / vx
        within[start:start + rows] = 0.5 * (
            ne[idx].sum(axis=1) / de[idx].sum(axis=1)
            + nl[idx].sum(axis=1) / dl[idx].sum(axis=1))
    delta = between - within
    return {
        "b": b_boot,
        "beta_between_ci": percentile_ci(between),
        "beta_within_ci": percentile_ci(within),
        "delta_ci": percentile_ci(delta),
        "delta_boot_mean": float(np.mean(delta)),
        "delta_boot_sd": float(np.std(delta, ddof=1)),
        "beta_between_boot_sd": float(np.std(between, ddof=1)),
        "beta_within_boot_sd": float(np.std(within, ddof=1)),
    }


def analyse_arm(sk: Skeleton, mom: dict[str, np.ndarray], *, b_perm: int,
                b_boot: int, seed_perm: int, seed_boot: int) -> dict[str, Any]:
    """All three levels plus the verdict statistic for one arm."""

    levels = three_levels(mom)
    beta_e, beta_l, ok = per_cell_slopes(sk, mom)
    rho = float(rowwise_pearson(beta_e[ok], beta_l[ok])[0])
    out = {
        "arm": sk.key,
        "label": sk.label,
        "census": sk.census(),
        **levels,
        "boot": paired_level_bootstrap(mom, b_boot, seed_boot),
        "rho_own": rho,
        "ownership_null": ownership_null(beta_e, beta_l, ok, b_perm,
                                         seed_perm + 101),
        "ownership_boot": cluster_bootstrap_pairs(beta_e, beta_l, ok, b_boot,
                                                  seed_boot + 501),
        "dispersion": dispersion(beta_e, beta_l, ok),
        "authors_scored_at_level_3": int(ok.sum()),
        "authors_dropped_at_level_3": int((~ok).sum()),
    }
    band = out["ownership_null"]["band"]
    out["ownership_detected"] = bool(rho < band[0] or rho > band[1])
    out["rho_ci"] = out["ownership_boot"]["ci"]
    out["rho_ci_covers_zero"] = bool(out["rho_ci"][0] <= 0.0
                                     <= out["rho_ci"][1])
    ci = out["boot"]["delta_ci"]
    out["delta_ci_covers_zero"] = bool(ci[0] <= 0.0 <= ci[1])
    out["beta_between_detected"] = not (
        out["boot"]["beta_between_ci"][0] <= 0.0
        <= out["boot"]["beta_between_ci"][1])
    out["beta_within_detected"] = not (
        out["boot"]["beta_within_ci"][0] <= 0.0
        <= out["boot"]["beta_within_ci"][1])
    # NON-ROUTING sensitivity: the same level-3 object restricted to cells
    # whose x spread makes the slope estimable at all (den >= 1 <=> the
    # slope's sampling sd does not exceed the event-noise sd).  x-only, pinned
    # in the config before any real number; reported, never routed.
    fine = sk.precise
    if int(fine.sum()) > 10:
        rho_fine = float(rowwise_pearson(beta_e[fine], beta_l[fine])[0])
        out["precision_floor"] = {
            "den_floor": PRECISION_FLOOR_DEN,
            "authors": int(fine.sum()),
            "authors_excluded": int(ok.sum() - fine.sum()),
            "rho_own": rho_fine,
            "boot": cluster_bootstrap_pairs(beta_e, beta_l, fine, b_boot,
                                            seed_boot + 907),
            "dispersion": dispersion(beta_e, beta_l, fine),
        }
    return out


# ---------------------------------------------------------------------------
# Stage 4 — Part 0, the gate on the REALIZED skeleton (wholly synthetic y)
# ---------------------------------------------------------------------------


WORLD_ERGODIC = "ergodic"
WORLD_NONERGODIC = "nonergodic"
WORLD_OWNED = "owned_slopes"
WORLD_OWNED_LOW = "owned_slopes_at_0.15"
WORLD_OWNED_FLOOR = "owned_slopes_precision_floor"
WORLD_OWNED_FLOOR_LOW = "owned_slopes_precision_floor_at_0.15"
WORLD_NULL = "null"

OWNED_WORLDS = (WORLD_OWNED, WORLD_OWNED_LOW, WORLD_OWNED_FLOOR,
                WORLD_OWNED_FLOOR_LOW)


def ownership_slope_target(sk: Skeleton, rho_target: float,
                           sd_e: float = SD_E,
                           mask: np.ndarray | None = None) -> dict[str, Any]:
    """Derive the across-author SLOPE dispersion that plants rho_own = target.

    Model (X2's, re-pointed at a slope).  Author u owns one slope beta_u,
    shared by both halves; the per-half OLS estimate is
    beta_{u,h} = beta_u + e_{u,h} with the exact conditional variance
    Var(e_{u,h}) = sigma^2 / den_{u,h}, den = sum (x - xbar_{u,h})^2 on the
    REALIZED skeleton.  The two halves' errors are uncorrelated, so with
    V = Var_u(beta_u) and A_h = E_u[sigma^2 / den_{u,h}]:

        Cov(beta_e, beta_l) = V,  Var(beta_h) = V + A_h,
        rho_own = V / sqrt((V + A_e)(V + A_l))

    Unlike X2's AR(1) case, A_h here does NOT depend on V, so the same
    quadratic X2 solves by bisection closes in one step and the leg BINDS X2's
    solver (``implied_phi_variance``) instead of restating it.  At
    rho = 1/2 and A_e = A_l = A it reduces to the readable V = A: plant exactly
    as much across-author slope variance as the per-half estimator's own
    sampling variance.
    """

    ok = sk.ok if mask is None else mask
    a_e = float(sd_e ** 2 * np.mean(1.0 / sk.den_e[ok]))
    a_l = float(sd_e ** 2 * np.mean(1.0 / sk.den_l[ok]))
    v = implied_phi_variance(rho_target, a_e, a_l)
    return {
        "rho_target": rho_target,
        "authors_in_the_mapping": int(ok.sum()),
        "sigma_e": sd_e,
        "A_early": a_e,
        "A_late": a_l,
        "A_early_median_based": float(
            sd_e ** 2 * np.median(1.0 / sk.den_e[ok])),
        "A_late_median_based": float(
            sd_e ** 2 * np.median(1.0 / sk.den_l[ok])),
        "V_slope_variance": v,
        "sd_beta": math.sqrt(v),
        "rho_implied_by_the_solution": v / math.sqrt((v + a_e) * (v + a_l)),
        "formula": ("rho = V / sqrt((V + A_e)(V + A_l)), "
                    "A_h = sigma^2 * E_u[1 / den_{u,h}]"),
    }


def plant_world(sk: Skeleton, world: str, mapping: dict[str, Any],
                rng: np.random.Generator) -> tuple[np.ndarray, dict[str, Any]]:
    """Wholly synthetic y on the realized skeleton.  No corpus y is touched."""

    who = sk.events["who"]
    x = sk.events["x"]
    n_a = sk.n_authors
    a_u = SD_A * rng.standard_normal(n_a)
    if world == WORLD_NONERGODIC:
        a_u = a_u + GAMMA_PLANT * sk.xbar
    if world == WORLD_NULL:
        beta_u = np.zeros(n_a)
    elif world in OWNED_WORLDS:
        beta_u = rng.normal(BETA_PLANT, mapping["sd_beta"], size=n_a)
    else:
        beta_u = np.full(n_a, BETA_PLANT)
    y = a_u[who] + beta_u[who] * x + SD_E * rng.standard_normal(x.size)
    truth = {
        "planted_beta_mean": float(beta_u.mean()),
        "planted_beta_sd": float(beta_u.std(ddof=1)),
        "planted_intercept_sd": float(a_u.std(ddof=1)),
    }
    return y, truth


def synthetic_replicate(sk: Skeleton, world: str, mapping: dict[str, Any],
                        seed: int, *, b_perm: int, b_boot: int,
                        with_ownership: bool,
                        eval_mask: np.ndarray | None = None) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    y, truth = plant_world(sk, world, mapping, rng)
    mom = cell_moments(sk, y)
    levels = three_levels(mom)
    boot = paired_level_bootstrap(mom, b_boot, seed + 5)
    out = {"world": world, "seed": seed, **truth, **levels, "boot": boot,
           "delta_ci_covers_zero": bool(boot["delta_ci"][0] <= 0.0
                                        <= boot["delta_ci"][1]),
           "between_ci_covers_zero": bool(boot["beta_between_ci"][0] <= 0.0
                                          <= boot["beta_between_ci"][1]),
           "within_ci_covers_zero": bool(boot["beta_within_ci"][0] <= 0.0
                                         <= boot["beta_within_ci"][1])}
    if with_ownership:
        beta_e, beta_l, defined = per_cell_slopes(sk, mom)
        ok = defined if eval_mask is None else (defined & eval_mask)
        out["ownership_authors"] = int(ok.sum())
        rho = float(rowwise_pearson(beta_e[ok], beta_l[ok])[0])
        oboot = cluster_bootstrap_pairs(beta_e, beta_l, ok, b_boot, seed + 23)
        out["rho_own"] = rho
        out["ownership_boot"] = oboot
        out["rho_ci_covers_zero"] = bool(oboot["ci"][0] <= 0.0 <= oboot["ci"][1])
        out["rho_ci_covers_own_point"] = bool(oboot["ci"][0] <= rho
                                              <= oboot["ci"][1])
        out["rho_half_width"] = 0.5 * (oboot["ci"][1] - oboot["ci"][0])
        if b_perm:
            onull = ownership_null(beta_e, beta_l, ok, b_perm, seed + 11)
            out["ownership_null"] = onull
            out["rho_inside_band"] = bool(onull["band"][0] <= rho
                                          <= onull["band"][1])
        out["dispersion"] = dispersion(beta_e, beta_l, ok)
    out["delta_half_width"] = 0.5 * (boot["delta_ci"][1] - boot["delta_ci"][0])
    return out


def run_world(sk: Skeleton, world: str, mapping: dict[str, Any], seed: int, *,
              b_perm: int, b_boot: int, with_ownership: bool,
              log: RunLog, eval_mask: np.ndarray | None = None
              ) -> dict[str, Any]:
    reps = []
    for i in range(N_SYNTH_REPLICATES):
        rep = synthetic_replicate(sk, world, mapping, seed + 7 * i,
                                  b_perm=b_perm, b_boot=b_boot,
                                  with_ownership=with_ownership,
                                  eval_mask=eval_mask)
        reps.append(rep)
        log.event("part0_replicate", world=world, replicate=i,
                  delta=rep["delta_erg"], beta_between=rep["beta_between"],
                  beta_within=rep["beta_within"],
                  rho_own=rep.get("rho_own"))

    def col(name: str) -> np.ndarray:
        return np.array([r[name] for r in reps if name in r], dtype=float)

    summary: dict[str, Any] = {"world": world, "replicates": len(reps),
                               "per_replicate": reps}
    for name in ("delta_erg", "beta_between", "beta_within", "rho_own",
                 "delta_half_width", "rho_half_width"):
        values = col(name)
        if values.size:
            summary[f"{name}_mean"] = float(values.mean())
            summary[f"{name}_sd"] = float(np.std(values, ddof=1))
            summary[f"{name}_values"] = [float(v) for v in values]
    summary["delta_ci_cover_count"] = int(
        sum(1 for r in reps if r["delta_ci_covers_zero"]))
    if with_ownership:
        summary["rho_ci_cover_zero_count"] = int(
            sum(1 for r in reps if r["rho_ci_covers_zero"]))
        summary["rho_ci_cover_point_count"] = int(
            sum(1 for r in reps if r["rho_ci_covers_own_point"]))
        summary["rho_inside_band_count"] = int(
            sum(1 for r in reps if r.get("rho_inside_band")))
    summary["between_ci_cover_zero_count"] = int(
        sum(1 for r in reps if r["between_ci_covers_zero"]))
    summary["within_ci_cover_zero_count"] = int(
        sum(1 for r in reps if r["within_ci_covers_zero"]))
    return summary


# The ERGODIC clause's coverage floor.  The registration says "the Delta CI
# must cover 0"; with 8 separately drawn replicates at a nominal 95% interval
# the honest reading of that sentence is a COVERAGE requirement, not "all 8 or
# the leg dies".  Requiring >= 6 of 8 gives P(fail | correct) = 0.0058
# under Binomial(8, 0.95); requiring 8 of 8 would fail a correct estimator 34%
# of the time.  The observed count is printed either way.
ERGODIC_COVER_FLOOR = 6


def part0_gate(sk: Skeleton, *, b_perm: int, b_boot: int, seed: int,
               log: RunLog) -> dict[str, Any]:
    """The registered Part 0: six ROUTING clauses, one DESCRIPTIVE family."""

    mapping = ownership_slope_target(sk, RHO_TRUE_TARGET)
    mapping_low = ownership_slope_target(sk, RHO_PRICE_LOW)
    mapping_floor = ownership_slope_target(sk, RHO_TRUE_TARGET,
                                           mask=sk.precise)
    mapping_floor_low = ownership_slope_target(sk, RHO_PRICE_LOW,
                                               mask=sk.precise)
    log.event("part0_mapping", **{k: v for k, v in mapping.items()
                                  if k != "formula"})

    delta_scale = abs(GAMMA_PLANT)
    tol_floor_delta = TOL_DELTA_SCALE_FRAC * delta_scale

    ergodic = run_world(sk, WORLD_ERGODIC, mapping, seed + 1000,
                        b_perm=0, b_boot=b_boot, with_ownership=False, log=log)
    nonerg = run_world(sk, WORLD_NONERGODIC, mapping, seed + 2000,
                       b_perm=0, b_boot=b_boot, with_ownership=False, log=log)
    owned = run_world(sk, WORLD_OWNED, mapping, seed + 3000,
                      b_perm=b_perm, b_boot=b_boot, with_ownership=True,
                      log=log)
    owned_low = run_world(sk, WORLD_OWNED_LOW, mapping_low, seed + 4000,
                          b_perm=0, b_boot=b_boot, with_ownership=True,
                          log=log)
    null = run_world(sk, WORLD_NULL, mapping, seed + 5000,
                     b_perm=b_perm, b_boot=b_boot, with_ownership=True,
                     log=log)
    # ANNOTATION worlds (D6): the same ownership question asked of the level-3
    # object once the x-only precision floor has removed the near-degenerate
    # halves.  Nothing routes on these; they exist so the report can say what
    # the registered object's replicate spread is actually made of.
    owned_floor = run_world(sk, WORLD_OWNED_FLOOR, mapping_floor, seed + 6000,
                            b_perm=0, b_boot=b_boot, with_ownership=True,
                            log=log, eval_mask=sk.precise)
    owned_floor_low = run_world(sk, WORLD_OWNED_FLOOR_LOW, mapping_floor_low,
                                seed + 7000, b_perm=0, b_boot=b_boot,
                                with_ownership=True, log=log,
                                eval_mask=sk.precise)

    tol_erg = max(tol_floor_delta, TOL_SD_MULT * ergodic["delta_erg_sd"])
    tol_non = max(tol_floor_delta, TOL_SD_MULT * nonerg["delta_erg_sd"])
    tol_rho = max(TOL_FLOOR_RHO, TOL_SD_MULT * owned["rho_own_sd"])
    gap_non = nonerg["delta_erg_mean"] - GAMMA_PLANT
    gap_rho = owned["rho_own_mean"] - RHO_TRUE_TARGET

    regions = {
        "priced_utc": utc_now(),
        "source": ("#88a executed IN-LEG: every half-width below is the MEAN "
                   "over Part 0's 8 replicates of the REALIZED bootstrap "
                   "half-width on the MATCHED planted world, pinned before "
                   "any real-arm number was computed."),
        "delta": {
            "centre": BOUNDARY_DELTA_CENTRE,
            "matched_world": WORLD_NULL,
            "half_width": null["delta_half_width_mean"],
            "half_width_sd_over_replicates": float(
                np.std(np.array(null["delta_half_width_values"]), ddof=1)),
        },
        "rho_low": {
            "centre": BOUNDARY_RHO_LOW,
            "matched_world": WORLD_OWNED_LOW,
            "half_width": owned_low["rho_half_width_mean"],
            "planted_rho": RHO_PRICE_LOW,
            "realized_rho_mean": owned_low["rho_own_mean"],
        },
        "rho_high": {
            "centre": BOUNDARY_RHO_HIGH,
            "matched_world": WORLD_OWNED,
            "half_width": owned["rho_half_width_mean"],
            "planted_rho": RHO_TRUE_TARGET,
            "realized_rho_mean": owned["rho_own_mean"],
        },
        "annotation_precision_floored": {
            "note": ("NON-ROUTING. The same pricing done on the level-3 "
                     "object read through the x-only precision floor "
                     f"(den >= {PRECISION_FLOOR_DEN}); printed so the reader "
                     "can see how much of the routed region's width is the "
                     "near-degenerate halves."),
            "rho_low_half_width": owned_floor_low["rho_half_width_mean"],
            "rho_low_realized_rho_mean": owned_floor_low["rho_own_mean"],
            "rho_high_half_width": owned_floor["rho_half_width_mean"],
            "rho_high_realized_rho_mean": owned_floor["rho_own_mean"],
        },
    }

    routing = [
        {"id": "i",
         "clause": ("ERGODIC world (one beta for all, person intercepts "
                    "UNCORRELATED with xbar_u): Delta_erg must read 0"),
         "observed": (f"mean Delta {ergodic['delta_erg_mean']:+.6f} over "
                      f"{N_SYNTH_REPLICATES} replicates (sd "
                      f"{ergodic['delta_erg_sd']:.6f}); "
                      f"{ergodic['delta_ci_cover_count']}/"
                      f"{N_SYNTH_REPLICATES} bootstrap CIs cover 0"),
         "required": (f"abs(mean) <= max({tol_floor_delta:.4f}, 3 x rep sd) = "
                      f"{tol_erg:.6f} AND >= {ERGODIC_COVER_FLOOR}/"
                      f"{N_SYNTH_REPLICATES} CIs cover 0"),
         "status": "PASS" if (abs(ergodic["delta_erg_mean"]) <= tol_erg
                              and ergodic["delta_ci_cover_count"]
                              >= ERGODIC_COVER_FLOOR) else "FAIL"},
        {"id": "ii",
         "clause": ("NON-ERGODIC world, a_u = gamma * xbar_u + noise: the "
                    "DERIVED Delta is exactly gamma (beta_within is blind to "
                    "a_u, beta_between reads beta + gamma), planted "
                    f"gamma = {GAMMA_PLANT:+.4f}"),
         "observed": (f"mean Delta {nonerg['delta_erg_mean']:+.6f} (sd "
                      f"{nonerg['delta_erg_sd']:.6f}), gap {gap_non:+.6f}"),
         "required": (f"abs(gap) <= max({TOL_DELTA_SCALE_FRAC:.0%} x "
                      f"{delta_scale:.4f}, 3 x rep sd) = {tol_non:.6f}"),
         "status": "PASS" if abs(gap_non) <= tol_non else "FAIL"},
        {"id": "iii",
         "clause": ("OWNED-SLOPES world at the #76 operating point (the "
                    "across-author slope dispersion DERIVED so the true "
                    "ownership correlation is 0.50): rho_own recovery"),
         "observed": (f"mean rho_own {owned['rho_own_mean']:+.4f} (sd "
                      f"{owned['rho_own_sd']:.4f}), gap {gap_rho:+.4f} = "
                      f"{abs(gap_rho) / max(owned['rho_own_sd'], 1e-12):.2f} "
                      "replicate sd — THE TOLERANCE IS CARRIED BY THE "
                      "REPLICATE SPREAD, NOT BY THE POINT (see D6)"),
         "required": (f"abs(gap) <= max({TOL_FLOOR_RHO}, 3 x rep sd) = "
                      f"{tol_rho:.4f}"),
         "status": "PASS" if abs(gap_rho) <= tol_rho else "FAIL"},
        {"id": "iv",
         "clause": ("NULL world (beta = 0 everywhere, intercepts unrelated "
                    "to x): ALL FOUR objects must read 0 within their own "
                    "band or interval"),
         "observed": (
             f"beta_between {null['beta_between_mean']:+.6f} "
             f"({null['between_ci_cover_zero_count']}/{N_SYNTH_REPLICATES} "
             f"CIs cover 0); beta_within {null['beta_within_mean']:+.6f} "
             f"({null['within_ci_cover_zero_count']}/{N_SYNTH_REPLICATES}); "
             f"Delta {null['delta_erg_mean']:+.6f} "
             f"({null['delta_ci_cover_count']}/{N_SYNTH_REPLICATES}); "
             f"rho_own {null['rho_own_mean']:+.4f} "
             f"({null['rho_ci_cover_zero_count']}/{N_SYNTH_REPLICATES} CIs "
             f"cover 0, {null['rho_inside_band_count']}/"
             f"{N_SYNTH_REPLICATES} points inside the pairing band)"),
         "required": (f">= {ERGODIC_COVER_FLOOR}/{N_SYNTH_REPLICATES} on each "
                      "of the four coverage counts"),
         "status": "PASS" if min(
             null["between_ci_cover_zero_count"],
             null["within_ci_cover_zero_count"],
             null["delta_ci_cover_count"],
             null["rho_ci_cover_zero_count"],
             null["rho_inside_band_count"]) >= ERGODIC_COVER_FLOOR
         else "FAIL"},
        {"id": "v",
         "clause": ("#85b bootstrap-zero on the NULL world: every interval "
                    "must cover 0 AND cover its own point"),
         "observed": (
             f"Delta CIs covering 0: {null['delta_ci_cover_count']}/"
             f"{N_SYNTH_REPLICATES}; rho_own CIs covering their own point: "
             f"{null['rho_ci_cover_point_count']}/{N_SYNTH_REPLICATES}"),
         "required": (f">= {ERGODIC_COVER_FLOOR}/{N_SYNTH_REPLICATES} on "
                      "both counts"),
         "status": "PASS" if min(
             null["delta_ci_cover_count"],
             null["rho_ci_cover_point_count"]) >= ERGODIC_COVER_FLOOR
         else "FAIL"},
        {"id": "vi",
         "clause": ("#88a REGION PRICING executed in-leg: the boundary-region "
                    "half-widths for BOTH routed objects are Part 0's "
                    "REALIZED bootstrap half-widths on the matched planted "
                    "worlds, pinned BEFORE any real-arm number"),
         "observed": (
             f"Delta region +-{regions['delta']['half_width']:.6f} (null "
             f"world); rho region at 0.15 "
             f"+-{regions['rho_low']['half_width']:.4f}; at 0.50 "
             f"+-{regions['rho_high']['half_width']:.4f}; pinned "
             f"{regions['priced_utc']}"),
         "required": ("all three finite and positive, artifact written before "
                      "the first real-arm number"),
         "status": "PASS" if all(
             np.isfinite(regions[k]["half_width"])
             and regions[k]["half_width"] > 0
             for k in ("delta", "rho_low", "rho_high")) else "FAIL"},
    ]

    descriptive = [
        {"id": "D1",
         "clause": ("LEVEL VALUE recovery, ergodic world (both levels must "
                    f"read the planted beta = {BETA_PLANT:+.2f})"),
         "observed": (f"beta_between {ergodic['beta_between_mean']:+.4f}, "
                      f"beta_within {ergodic['beta_within_mean']:+.4f}"),
         "required": "annotate only, never stops", "status": "ANNOTATED"},
        {"id": "D2",
         "clause": ("LEVEL VALUE recovery, non-ergodic world (beta_within = "
                    f"{BETA_PLANT:+.2f}, beta_between = beta + gamma = "
                    f"{BETA_PLANT + GAMMA_PLANT:+.2f}) — this world also "
                    "plants a SIGN FLIP between the levels"),
         "observed": (f"beta_between {nonerg['beta_between_mean']:+.4f}, "
                      f"beta_within {nonerg['beta_within_mean']:+.4f}"),
         "required": "annotate only, never stops", "status": "ANNOTATED"},
        {"id": "D3",
         "clause": "LEVEL VALUE recovery, null world (both levels read 0)",
         "observed": (f"beta_between {null['beta_between_mean']:+.6f}, "
                      f"beta_within {null['beta_within_mean']:+.6f}"),
         "required": "annotate only, never stops", "status": "ANNOTATED"},
        {"id": "D4",
         "clause": ("the DEN DISTRIBUTION the ownership mapping rides on — "
                    "den = sum (x - xbar_cell)^2 is unbounded below in this "
                    "pool, so A_h = sigma^2 E[1/den] can be dominated by a "
                    "handful of near-degenerate halves"),
         "observed": (
             f"A_early {mapping['A_early']:.6g} (median-based "
             f"{mapping['A_early_median_based']:.6g}), A_late "
             f"{mapping['A_late']:.6g} (median-based "
             f"{mapping['A_late_median_based']:.6g}); min den "
             f"{sk.census()['min_den_early']:.4g} / "
             f"{sk.census()['min_den_late']:.4g}, median den "
             f"{sk.census()['median_den_early']:.4g} / "
             f"{sk.census()['median_den_late']:.4g}"),
         "required": "annotate only, never stops", "status": "ANNOTATED"},
        {"id": "D5",
         "clause": ("the x-only PRECISION FLOOR the real arms also carry as a "
                    f"non-routing sensitivity (den >= {PRECISION_FLOOR_DEN}, "
                    "i.e. the per-half slope's sampling sd does not exceed "
                    "the event-noise sd)"),
         "observed": (
             f"{int(sk.precise.sum()):,} of {int(sk.ok.sum()):,} level-3 "
             f"authors clear the floor ({int(sk.ok.sum() - sk.precise.sum())} "
             "excluded); the floored mapping reads A_early "
             f"{mapping_floor['A_early']:.6g} / A_late "
             f"{mapping_floor['A_late']:.6g} against the routed "
             f"{mapping['A_early']:.6g} / {mapping['A_late']:.6g}"),
         "required": "annotate only, never stops", "status": "ANNOTATED"},
        {"id": "D6",
         "clause": ("OWNERSHIP RECOVERY ON THE FLOORED OBJECT — the same "
                    "planted question with the near-degenerate halves out; "
                    "this is what clause (iii)'s replicate spread is made of"),
         "observed": (
             f"planted 0.50 -> {owned_floor['rho_own_mean']:+.4f} (sd "
             f"{owned_floor['rho_own_sd']:.4f}, half-width "
             f"{owned_floor['rho_half_width_mean']:.4f}) against the ROUTED "
             f"object's {owned['rho_own_mean']:+.4f} (sd "
             f"{owned['rho_own_sd']:.4f}, half-width "
             f"{owned['rho_half_width_mean']:.4f}); planted 0.15 -> "
             f"{owned_floor_low['rho_own_mean']:+.4f} (half-width "
             f"{owned_floor_low['rho_half_width_mean']:.4f}) against "
             f"{owned_low['rho_own_mean']:+.4f} (half-width "
             f"{owned_low['rho_half_width_mean']:.4f})"),
         "required": "annotate only, never stops", "status": "ANNOTATED"},
    ]

    status = "PASS" if all(c["status"] == "PASS" for c in routing) else "FAIL"
    return {
        "status": status,
        "routing": routing,
        "descriptive": descriptive,
        "mapping": mapping,
        "mapping_low": mapping_low,
        "mapping_precision_floored": mapping_floor,
        "mapping_precision_floored_low": mapping_floor_low,
        "regions": regions,
        "worlds": {WORLD_ERGODIC: ergodic, WORLD_NONERGODIC: nonerg,
                   WORLD_OWNED: owned, WORLD_OWNED_LOW: owned_low,
                   WORLD_NULL: null, WORLD_OWNED_FLOOR: owned_floor,
                   WORLD_OWNED_FLOOR_LOW: owned_floor_low},
        "derived_delta_nonergodic": GAMMA_PLANT,
        "tolerances": {"ergodic_delta": tol_erg, "nonergodic_delta": tol_non,
                       "owned_rho": tol_rho,
                       "delta_scale_floor": tol_floor_delta},
    }


# ---------------------------------------------------------------------------
# Stage 5 — cells (#55 NULL-first, #75 effect-size keyed, #87 PRICED REGIONS)
# ---------------------------------------------------------------------------


def rho_region_edges(regions: dict[str, Any]) -> tuple[float, ...]:
    lo_w = regions["rho_low"]["half_width"]
    hi_w = regions["rho_high"]["half_width"]
    return (BOUNDARY_RHO_LOW - lo_w, BOUNDARY_RHO_LOW + lo_w,
            BOUNDARY_RHO_HIGH - hi_w, BOUNDARY_RHO_HIGH + hi_w)


def ladder_status(regions: dict[str, Any]) -> dict[str, Any]:
    """Is the PRICED ownership ladder still a ladder?

    #87 puts a region of the estimator's own realized width around each
    boundary.  Nothing guarantees the regions stay disjoint: if the priced
    half-widths are large enough that the 0.15 region reaches past the start of
    the 0.50 region, `WEAKLY_OWNED` becomes an EMPTY interval and the ladder
    has collapsed into "boundary everywhere".  That is a real statement about
    the design's resolution and it is reported rather than papered over.  The
    NULL-first clause is untouched by it: `NOT_OWNED` is decided by whether the
    interval covers 0 and never by a region edge.
    """

    low_lo, low_hi, high_lo, high_hi = rho_region_edges(regions)
    overlap = low_hi >= high_lo
    return {
        "edges": [low_lo, low_hi, high_lo, high_hi],
        "weakly_owned_interval_is_empty": bool(overlap),
        "status": "DEGENERATE_OVERLAP" if overlap else "COHERENT",
        "note": ("the priced 0.15 and 0.50 regions overlap, so WEAKLY_OWNED "
                 "is unreachable and every non-null point lands on a boundary"
                 if overlap else
                 "the priced regions are disjoint and the ladder resolves"),
    }


def rho_cell(rho: float, ci_covers_zero: bool,
             regions: dict[str, Any]) -> str:
    """X2's ladder, NULL-first, with the #88a PRICED half-widths."""

    low_lo, low_hi, high_lo, high_hi = rho_region_edges(regions)
    if ci_covers_zero or rho < low_lo:
        return CELL_NOT_OWNED
    if rho <= low_hi:
        return CELL_AT_LOW
    if rho < high_lo:
        return CELL_WEAK
    if rho <= high_hi:
        return CELL_AT_HIGH
    return CELL_STRONG


def delta_cell(result: dict[str, Any]) -> str:
    """The registered three cells on Delta_erg, NULL-first."""

    if result["delta_ci_covers_zero"]:
        return CELL_INDIST
    same_sign = (result["beta_between"] > 0.0) == (result["beta_within"] > 0.0)
    if same_sign:
        return CELL_SAME_SIGN
    if result["beta_between_detected"] and result["beta_within_detected"]:
        return CELL_SIGN_FLIP
    return CELL_SIGN_UNRESOLVED


def edges_straddled(ci: Sequence[float],
                    edges: Sequence[float]) -> list[str]:
    return [f"{edge:.4f}" for edge in edges if ci[0] < edge < ci[1]]


def classify(result: dict[str, Any], regions: dict[str, Any]) -> dict[str, Any]:
    delta_w = regions["delta"]["half_width"]
    delta_edges = (BOUNDARY_DELTA_CENTRE - delta_w,
                   BOUNDARY_DELTA_CENTRE + delta_w)
    d_ci = result["boot"]["delta_ci"]
    r_ci = result["rho_ci"]
    d_straddle = edges_straddled(d_ci, delta_edges)
    r_straddle = edges_straddled(r_ci, rho_region_edges(regions))
    return {
        "arm": result["arm"],
        "label": result["label"],
        "delta_erg": result["delta_erg"],
        "delta_ci": d_ci,
        "delta_ci_covers_zero": result["delta_ci_covers_zero"],
        "delta_cell": delta_cell(result),
        "delta_inside_priced_region": bool(abs(result["delta_erg"])
                                           <= delta_w),
        "delta_region_edges_straddled": d_straddle,
        "delta_is_straddle": bool(d_straddle),
        "beta_between": result["beta_between"],
        "beta_within": result["beta_within"],
        "rho_own": result["rho_own"],
        "rho_ci": r_ci,
        "rho_band": result["ownership_null"]["band"],
        "rho_ci_covers_zero": result["rho_ci_covers_zero"],
        "rho_cell": rho_cell(result["rho_own"], result["rho_ci_covers_zero"],
                             regions),
        "rho_region_edges_straddled": r_straddle,
        "rho_is_straddle": bool(r_straddle),
    }


def evaluate_leans(cells: dict[str, Any], arms: dict[str, Any],
                   regions: dict[str, Any]) -> list[dict[str, Any]]:
    primary = arms["primary"]
    p_cell = cells["primary"]
    ladder = ladder_status(regions)
    weak_note = ("" if not ladder["weakly_owned_interval_is_empty"] else
                 "; NOTE: at this pricing WEAKLY_OWNED is an EMPTY interval, "
                 "so the lean could not have held whatever the data said")
    floor_note = ""
    if "precision_floor" in primary and "precision_floor" in arms["big5"]:
        floor_note = (
            "; through the x-only precision floor (routes nothing) Big5 "
            f"{arms['big5']['precision_floor']['rho_own']:+.4f} "
            f"{fmt_ci(arms['big5']['precision_floor']['boot']['ci'])} vs "
            f"primary {primary['precision_floor']['rho_own']:+.4f} "
            f"{fmt_ci(primary['precision_floor']['boot']['ci'])}")
    rows = [
        {"lean": "beta_within < 0 (a commoner venue -> shorter comments)",
         "registered": "held moderately",
         "observed": (f"{primary['beta_within']:+.6f} "
                      f"{fmt_ci(primary['boot']['beta_within_ci'], 6)}"),
         "held": bool(primary["beta_within"] < 0.0)},
        {"lean": "beta_between < 0", "registered": "held moderately",
         "observed": (f"{primary['beta_between']:+.6f} "
                      f"{fmt_ci(primary['boot']['beta_between_ci'], 6)}"),
         "held": bool(primary["beta_between"] < 0.0)},
        {"lean": ("Delta_erg NONERGODIC_SAME_SIGN with "
                  "abs(beta_between) > abs(beta_within)"),
         "registered": "held weakly",
         "observed": (f"cell `{p_cell['delta_cell']}`, "
                      f"abs(between) {abs(primary['beta_between']):.6f} vs "
                      f"abs(within) {abs(primary['beta_within']):.6f}"),
         "held": bool(p_cell["delta_cell"] == CELL_SAME_SIGN
                      and abs(primary["beta_between"])
                      > abs(primary["beta_within"]))},
        {"lean": "rho_own(beta) WEAKLY_OWNED",
         "registered": CELL_WEAK,
         "observed": (f"`{p_cell['rho_cell']}` at rho_own "
                      f"{primary['rho_own']:+.4f} "
                      f"{fmt_ci(primary['rho_ci'])}" + weak_note),
         "held": bool(p_cell["rho_cell"] == CELL_WEAK)},
        {"lean": "the Big5 replication lands in the SAME Delta cell",
         "registered": p_cell["delta_cell"],
         "observed": cells["big5"]["delta_cell"],
         "held": bool(cells["big5"]["delta_cell"] == p_cell["delta_cell"])},
        {"lean": "Big5 ownership possibly HIGHER than the primary's",
         "registered": "co-reported, either way is a #73 flag",
         "observed": (f"Big5 {arms['big5']['rho_own']:+.4f} vs primary "
                      f"{primary['rho_own']:+.4f}" + floor_note),
         "held": bool(arms["big5"]["rho_own"] > primary["rho_own"])},
    ]
    for row in rows:
        row["status"] = "HELD" if row["held"] else "BROKEN"
    return rows


def flags_73(cells: dict[str, Any]) -> list[dict[str, Any]]:
    """Arm divergences carry #73; the primary always routes."""

    primary = cells["primary"]
    flags = []
    for key, cell in cells.items():
        if key == "primary":
            continue
        if cell["delta_cell"] != primary["delta_cell"]:
            flags.append({"arm": key, "object": "Delta_erg",
                          "primary_cell": primary["delta_cell"],
                          "arm_cell": cell["delta_cell"],
                          "value": cell["delta_erg"], "ci": cell["delta_ci"],
                          "note": "#73 divergence; the primary routes"})
        if cell["rho_cell"] != primary["rho_cell"]:
            flags.append({"arm": key, "object": "rho_own",
                          "primary_cell": primary["rho_cell"],
                          "arm_cell": cell["rho_cell"],
                          "value": cell["rho_own"], "ci": cell["rho_ci"],
                          "note": "#73 divergence; the primary routes"})
    for key, cell in cells.items():
        if cell["delta_is_straddle"]:
            flags.append({"arm": key, "object": "Delta_erg",
                          "primary_cell": primary["delta_cell"],
                          "arm_cell": cell["delta_cell"],
                          "value": cell["delta_erg"], "ci": cell["delta_ci"],
                          "note": ("#87 straddle: the CI crosses the priced "
                                   "region edge(s) "
                                   + ", ".join(
                                       cell["delta_region_edges_straddled"]))})
        if cell["rho_is_straddle"]:
            flags.append({"arm": key, "object": "rho_own",
                          "primary_cell": primary["rho_cell"],
                          "arm_cell": cell["rho_cell"],
                          "value": cell["rho_own"], "ci": cell["rho_ci"],
                          "note": ("#87 straddle: the CI crosses the priced "
                                   "region edge(s) "
                                   + ", ".join(
                                       cell["rho_region_edges_straddled"]))})
    return flags


def build_verdict(part0: dict[str, Any], cells: dict[str, Any],
                  arms: dict[str, Any]) -> dict[str, Any]:
    if part0["status"] != "PASS":
        return {"cell": CELL_A1_STOP, "routes_on": "Part 0 gate",
                "gate": part0["status"],
                "note": ("A1 stop: a ROUTING clause failed on the realized "
                         "skeleton; NO corpus estimand value is licensed.")}
    primary = cells["primary"]
    arm = arms["primary"]
    return {
        "cell": primary["delta_cell"],
        "co_primary_cell": primary["rho_cell"],
        "routes_on": "Delta_erg, PRIMARY arm (disjoint pool)",
        "gate": part0["status"],
        "delta_erg": primary["delta_erg"],
        "delta_ci": primary["delta_ci"],
        "beta_between": primary["beta_between"],
        "beta_between_ci": arm["boot"]["beta_between_ci"],
        "beta_within": primary["beta_within"],
        "beta_within_ci": arm["boot"]["beta_within_ci"],
        "rho_own": primary["rho_own"],
        "rho_ci": primary["rho_ci"],
        "rho_band": primary["rho_band"],
        "delta_is_straddle": primary["delta_is_straddle"],
        "delta_region_edges_straddled": primary["delta_region_edges_straddled"],
        "rho_is_straddle": primary["rho_is_straddle"],
        "rho_region_edges_straddled": primary["rho_region_edges_straddled"],
        "authors": arm["census"]["authors"],
        "events": arm["census"]["events"],
    }


def honest_anomalies(sk: Skeleton, arms: dict[str, Any],
                     cells: dict[str, Any], part0: dict[str, Any]
                     ) -> list[dict[str, Any]]:
    """Everything a reader could mistake, named with its own number."""

    mapping = part0["mapping"]
    floored = part0["mapping_precision_floored"]
    regions = part0["regions"]
    ann = regions["annotation_precision_floored"]
    owned = part0["worlds"][WORLD_OWNED]
    primary = arms["primary"]
    census = primary["census"]
    worst_late = 1.0 / census["min_den_late"]
    share_of_a = worst_late / (census["authors_scored_at_level_3"]
                               * mapping["A_late"])
    out = [
        {"anomaly": ("the pool predicate is reproduced through the CENSUS's "
                     "own floating-point path, and that path admits "
                     "mathematically constant halves"),
         "detail": (
             "`sd(x) > 0 in EACH half` has three defensible implementations "
             "and they do not agree on this corpus: numpy's per-slice "
             "two-pass sd (pairwise summation) gives 8,004 / 1,112 — the "
             "REGISTERED anchors, reproduced here exactly; a grouped "
             "sequential accumulation gives 8,008 / 1,114; the "
             "mathematically exact test min(x) == max(x) gives 8,000 / "
             "1,103. The anchored path therefore admits 13 halves whose x is "
             "mathematically constant. They are not swept under the rug: "
             "their exact contribution to the level-1 and level-2 pooled sums "
             "is zero and is set to zero, and the level-3 estimator returns "
             "NaN for them and counts them "
             f"({census['authors_with_a_constant_half']} authors dropped on "
             "the primary arm). No estimand value depends on which of the "
             "three paths is used beyond those 13 cells.")},
        {"anomaly": ("the level-3 object is ONE-AUTHOR FRAGILE, and the "
                     "priced ownership regions say so"),
         "detail": (
             "`den = sum (x - xbar_cell)^2` is unbounded below in this pool: "
             f"the median half has den ~ {census['median_den_late']:,.0f} but "
             f"the smallest non-degenerate late half has den = "
             f"{census['min_den_late']:.3g}, so that one author's per-half "
             f"slope carries a sampling variance of {worst_late:,.0f} — about "
             f"{share_of_a:.0%} of the whole arm's A_late = "
             f"{mapping['A_late']:.4g}. The #76 mapping therefore lands on a "
             f"pathological operating point (V = {mapping['V_slope_variance']:.4g}, "
             f"sd(beta_u) = {mapping['sd_beta']:.3g}) and the cluster "
             "bootstrap correctly reports that rho_own on this skeleton can "
             "be moved by a single author: the priced half-widths are "
             f"+-{regions['rho_high']['half_width']:.3f} at 0.50 and "
             f"+-{regions['rho_low']['half_width']:.3f} at 0.15, which is "
             "wide enough that the registered ownership LADDER cannot be "
             "resolved at this design's own precision. This is a true "
             "statement about the registered estimator, not a bug: with the "
             f"x-only precision floor (den >= {PRECISION_FLOOR_DEN}, "
             f"{census['authors_above_the_precision_floor']:,} of "
             f"{census['authors_scored_at_level_3']:,} authors) the same "
             f"worlds price at +-{ann['rho_high_half_width']:.3f} and "
             f"+-{ann['rho_low_half_width']:.3f}. The routed number is the "
             "registered one; the floored arm is co-reported and routes "
             "nothing.")},
        {"anomaly": ("Part 0's ownership clause (iii) passes on its REPLICATE "
                     "SPREAD, not on its point"),
         "detail": (
             f"the planted world's realized rho_own is "
             f"{owned['rho_own_mean']:+.4f} against the derived 0.50 — a gap "
             f"of {abs(owned['rho_own_mean'] - RHO_TRUE_TARGET):+.4f} that "
             f"clears the registered tolerance only because the replicate sd "
             f"is {owned['rho_own_sd']:.4f} and the tolerance is 3 x that. "
             "The clause is recorded as PASSED and simultaneously as "
             "UNINFORMATIVE, which is the honest reading of a "
             "max(floor, 3 x sd) tolerance whose second term has run away. "
             "D6 shows the same recovery on the floored object: "
             f"{part0['worlds'][WORLD_OWNED_FLOOR]['rho_own_mean']:+.4f} "
             f"(sd {part0['worlds'][WORLD_OWNED_FLOOR]['rho_own_sd']:.4f}) "
             "against the same planted 0.50, so the level-3 machinery itself "
             "is sound and it is the pool's den tail that is not.")},
        {"anomaly": ("A_early and A_late differ by three orders of magnitude "
                     "on the same authors"),
         "detail": (
             f"A_early = {mapping['A_early']:.4g} against A_late = "
             f"{mapping['A_late']:.4g}, while the MEDIAN-based versions agree "
             f"to a few percent ({mapping['A_early_median_based']:.4g} vs "
             f"{mapping['A_late_median_based']:.4g}). The two halves are "
             "statistically alike; the asymmetry is one late half in the "
             "extreme tail. The floored mapping removes it entirely "
             f"({floored['A_early']:.4g} vs {floored['A_late']:.4g}).")},
    ]
    ladder = ladder_status(regions)
    if ladder["weakly_owned_interval_is_empty"]:
        out.append(
            {"anomaly": ("the PRICED ownership ladder collapsed: "
                         "`WEAKLY_OWNED` is an empty interval"),
             "detail": (
                 f"the priced regions run [{ladder['edges'][0]:.4f}, "
                 f"{ladder['edges'][1]:.4f}] around 0.15 and "
                 f"[{ladder['edges'][2]:.4f}, {ladder['edges'][3]:.4f}] "
                 "around 0.50, which overlap, so no rho_own value could have "
                 f"been called `{CELL_WEAK}` at this pricing — the exact cell "
                 "the registration LEANED toward. The lean is therefore "
                 "recorded as BROKEN against a ladder that could not have "
                 "produced it, which is a weaker statement than a broken lean "
                 "usually is and is flagged as such. The routed cell "
                 f"`{cells['primary']['rho_cell']}` is decided NULL-first and "
                 "does not depend on any region edge.")})
    disp = primary["dispersion"]
    if not (disp["var_true_cross_half"] > 0):
        out.append(
            {"anomaly": ("Var(beta) by cross-half covariance comes out "
                         "NEGATIVE on the routed level-3 object"),
             "detail": (
                 f"Cov(beta_early, beta_late) = "
                 f"{disp['var_true_cross_half']:+.6g} on the primary arm, so "
                 "sd_true and the headroom are undefined and are printed as "
                 "n/a. A variance estimate cannot be negative in truth; this "
                 "is the same one-author tail read through the covariance "
                 "instead of the correlation. Through the x-only precision "
                 f"floor the same arm reads Var(beta) = "
                 f"{primary['precision_floor']['dispersion']['var_true_cross_half']:+.6g}"
                 f" with rho_own {primary['precision_floor']['rho_own']:+.4f} "
                 f"{fmt_ci(primary['precision_floor']['boot']['ci'])}. "
                 "The routed number is the registered one; the floored one is "
                 "co-reported and routes nothing.")})
    p = primary
    if abs(p["beta_within_early"] - p["beta_within_late"]) > 2 * abs(
            p["beta_within"]):
        out.append(
            {"anomaly": ("level 2 is carried almost entirely by the EARLY "
                         "half"),
             "detail": (
                 f"the within-person slope reads "
                 f"{p['beta_within_early']:+.6f} on the early half and "
                 f"{p['beta_within_late']:+.6f} on the late half; the "
                 f"registered estimand is their mean, "
                 f"{p['beta_within']:+.6f}. The registration pins the "
                 "average of the two halves and that is what routes, but a "
                 "reader should not take level 2 as a stationary quantity: on "
                 "this corpus it is a two-number average whose two numbers "
                 "disagree in magnitude and nearly in sign. Nothing in this "
                 "leg can say whether that is calendar drift, a cohort "
                 "composition change, or the half split itself.")})
    p_cell = cells["primary"]
    if p_cell["delta_inside_priced_region"] and not p_cell[
            "delta_ci_covers_zero"]:
        out.append(
            {"anomaly": ("the Delta_erg point sits INSIDE its own priced "
                         "boundary region while its CI excludes zero"),
             "detail": (
                 f"Delta_erg = {p_cell['delta_erg']:+.6f} against a null-world "
                 f"priced half-width of "
                 f"{regions['delta']['half_width']:.6f}. The detection is "
                 "real at this sample size and the effect is smaller than the "
                 "width a NULL world's own interval spans, so the cell is "
                 "reported as a boundary-sensitive detection rather than a "
                 "clean one (#87).")})
    div = [k for k, c in cells.items()
           if k != "primary" and c["delta_cell"] != p_cell["delta_cell"]]
    if div:
        out.append(
            {"anomaly": ("an arm disagrees with the primary on the Delta "
                         "cell (#73)"),
             "detail": (
                 "arms " + ", ".join(f"`{k}` -> `{cells[k]['delta_cell']}` "
                                     f"(Delta {cells[k]['delta_erg']:+.6f} "
                                     f"{fmt_ci(cells[k]['delta_ci'], 6)})"
                                     for k in div)
                 + f" against the primary's `{p_cell['delta_cell']}` "
                 f"(Delta {p_cell['delta_erg']:+.6f} "
                 f"{fmt_ci(p_cell['delta_ci'], 6)}). The primary routes; the "
                 "divergence is reported and not resolved.")})
    return out


# ---------------------------------------------------------------------------
# Stage 6 — the report (rule 24: every table generated from the artifacts)
# ---------------------------------------------------------------------------


BOUNDARIES = (
    "**Metadata only; expression VOLUME and not content (permanent).** The "
    "only text-derived quantity in this leg is `word_count_quoteless`, the "
    "author's own-word count per comment. No body was read, no topic, no "
    "style, no sentiment. The other variable, `x`, is a community's share of "
    "the whole event stream — a pure activity statistic. Every claim here is "
    "about HOW MUCH is written where, never about WHAT is written.",
    "**The owner's three-level schema, with its provenance.** The "
    "between/average-within/single-person trichotomy this leg measures is the "
    "program OWNER's conference input, relayed 2026-08-19: a one-shot group "
    "measurement yields a BETWEEN-person relation; repeated measurement of "
    "many yields the AVERAGE WITHIN-person relation; repeated measurement of "
    "one yields THAT person's relation. X4 supplies a corpus instance of the "
    "schema on metadata; it does not supply the schema, and the schema is "
    "cited, not claimed.",
    "**The projection caution.** beta_between, beta_within and beta_{u,h} are "
    "STATIC projections of a much richer dynamic object. One scalar relation "
    "measured at three levels says nothing about lags, about how the relation "
    "moves within a half, or about any other coordinate. A level difference "
    "is a statement about these three projections at this resolution; a null "
    "is not an equivalence claim.",
    "**No psychological naming.** Expression volume and its community "
    "gradient are technical objects. Nothing here is a trait, a state, a "
    "disposition or a preference, and the leg is label-free: "
    "`author_profiles.csv` was never opened.",
    "**EXPLORATORY, corpus-level.** No person-level claim is licensed. The "
    "per-author slopes exist only as the population of a mean, a covariance "
    "and one correlation; no individual's beta is a measurement of that "
    "individual.",
    "**The cohort-selection caveat (carried from X2).** A Big5/disjoint "
    "difference cannot be separated from HOW the 1,401 Big5 authors were "
    "selected. The disjoint cohort is also TYPOLOGY-ENRICHED by construction "
    "(PANDORA's non-Big5 authors are MBTI-labelled users), so both cohorts "
    "are platform samples with a selection, not population samples.",
    "**Pool selection.** The pool floors at 50 events in EACH half and "
    "requires within-half x spread, so the leg speaks for authors who are "
    "ACTIVE ON BOTH SIDES of their own median AND who move between "
    "communities. Nothing here speaks for short-lived, low-volume or "
    "single-community accounts.",
)


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []

    def add(text: str = "") -> None:
        lines.append(text)

    verdict = payload["verdict"]
    part0 = payload["part0"]
    arms = payload["arms"]
    cells = payload["cells"]
    primary = arms.get("primary")

    add("# SUICA M4-X4 — the three-level decomposition and the ergodicity "
        "contrast")
    add("")
    if primary is None:
        add(f"**Outcome: `{verdict['cell']}`.** A ROUTING clause of Part 0 "
            "failed on the realized skeleton, so the leg stopped BEFORE any "
            "corpus estimand was scored. Nothing below is a reading of the "
            "corpus; every number in this report is synthetic or design "
            "arithmetic. " + verdict.get("note", ""))
    else:
        add(f"**Outcome: `{verdict['cell']}`** (co-primary ownership: "
            f"`{verdict['co_primary_cell']}`). One relation — how common a "
            "venue is against how much is written there — measured at the "
            "owner's three levels on "
            f"{verdict['authors']:,} disjoint-cohort authors and "
            f"{verdict['events']:,} events. Level 1 (between-person) "
            f"**beta_between = {fmt(verdict['beta_between'], 6)}** "
            f"{fmt_ci(verdict['beta_between_ci'], 6)}; level 2 (average "
            f"within-person) **beta_within = "
            f"{fmt(verdict['beta_within'], 6)}** "
            f"{fmt_ci(verdict['beta_within_ci'], 6)}; the ergodicity contrast "
            f"**Delta_erg = {fmt(verdict['delta_erg'], 6)}** "
            f"{fmt_ci(verdict['delta_ci'], 6)} on the paired author-cluster "
            "bootstrap. Level 3's ownership of the per-person slope reads "
            f"rho_own = {fmt(verdict['rho_own'])} {fmt_ci(verdict['rho_ci'])} "
            f"against a pairing-permutation band "
            f"{fmt_ci(verdict['rho_band'])}.")
    add("")
    add("Registration: `docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md`, section "
        "\"X4 — the three-level decomposition and the ergodicity contrast "
        "(registered BEFORE run, 2026-08-19)\", commit 42f0625. Question "
        "provenance: the program OWNER's conference input, relayed "
        f"2026-08-19. Run {payload['run']['finished_utc']}, "
        f"{payload['run']['runtime_s']:.0f} s.")
    add("")

    add("## Verdict and cells")
    add("")
    regions = part0["regions"]
    _table(add, ["field", "value"], [
        ["Delta cell (PRIMARY, routes)", f"`{verdict['cell']}`"],
        ["rho_own cell (co-primary)",
         f"`{verdict.get('co_primary_cell', 'n/a')}`"],
        ["routes on", verdict["routes_on"]],
        ["Part 0 gate", f"`{part0['status']}`"],
        ["Delta_erg", fmt(verdict.get("delta_erg"), 6)],
        ["Delta_erg CI (paired cluster bootstrap, B = 1000)",
         fmt_ci(verdict.get("delta_ci", [float("nan")] * 2), 6)],
        ["#87 Delta straddle", ", ".join(verdict.get(
            "delta_region_edges_straddled", [])) or "none"],
        ["rho_own", fmt(verdict.get("rho_own"))],
        ["rho_own CI (author cluster bootstrap, B = 1000)",
         fmt_ci(verdict.get("rho_ci", [float("nan")] * 2))],
        ["#87 rho straddle", ", ".join(verdict.get(
            "rho_region_edges_straddled", [])) or "none"],
    ])
    add("Registered cells on Delta_erg (NULL-first): "
        f"`{CELL_INDIST}` = the CI includes 0 (scoped by the realized width; "
        f"NOT an equivalence claim); `{CELL_SAME_SIGN}` = the CI excludes 0 "
        f"and the two slopes share sign; `{CELL_SIGN_FLIP}` = the CI excludes "
        "0, the signs differ AND both slopes are detected against their own "
        f"intervals; `{CELL_SIGN_UNRESOLVED}` = a completeness fallback "
        "(registration silent) for a Delta that excludes 0 with differing "
        "point signs but a slope whose own CI covers 0.")
    add("")
    if primary is not None:
        low_lo, low_hi, high_lo, high_hi = rho_region_edges(regions)
        ladder = ladder_status(regions)
        add(f"Ownership ladder with the #88a PRICED regions, applied in this "
            f"order: `{CELL_NOT_OWNED}` = the CI includes 0, or the point is "
            f"below {low_lo:.4f}; then `{CELL_AT_LOW}` up to {low_hi:.4f}; "
            f"then `{CELL_WEAK}` up to {high_lo:.4f}; then `{CELL_AT_HIGH}` "
            f"up to {high_hi:.4f}; then `{CELL_STRONG}`. The Delta_erg region "
            f"around 0 has half-width {regions['delta']['half_width']:.6f}.")
        add("")
        if ladder["weakly_owned_interval_is_empty"]:
            add(f"**The priced ownership ladder is `{ladder['status']}`.** The "
                f"0.15 region reaches to {low_hi:.4f} while the 0.50 region "
                f"starts at {high_lo:.4f}, so `{CELL_WEAK}` is an EMPTY "
                "interval at this pricing and no point could have landed in "
                "it. This is what #87 is for: the regions are the estimator's "
                "own realized widths, and here they say the ownership ladder "
                "does not resolve on the registered level-3 object. The "
                f"co-primary cell `{verdict['co_primary_cell']}` is NOT "
                "affected by the collapse — it is decided NULL-first, by "
                "whether the interval covers 0, and never by a region edge.")
            add("")

    add("## Census and the blocking anchors (#78)")
    add("")
    _table(add, ["registered predicate", "registered", "observed", "status"],
           [[k, _exact(v["registered"]), _exact(v["observed"]),
             f"`{v['status']}`"]
            for k, v in payload["census"]["pins"].items()])

    add("## Part 0 — the gate on the REALIZED skeleton (wholly synthetic y)")
    add("")
    add("Real per-author x sequences, real half splits, real cell sizes; "
        "every y in this section is planted. No corpus y value enters Part 0, "
        "and the region pricing below was written to disk BEFORE the first "
        "real-arm number existed.")
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

    add("### The derived non-ergodic Delta (clause ii, analytic)")
    add("")
    add("```")
    add("y_{u,i} = a_u + beta * x_{u,i} + e_{u,i},   a_u = gamma * xbar_u + w_u")
    add("  level 2:  within-(u,h) centering annihilates a_u  =>  E[beta_within]"
        " = beta")
    add("  level 1:  ybar_u = (beta + gamma) xbar_u + w_u + ebar_u")
    add("            =>  E[beta_between] = beta + gamma   (w_u uncorrelated "
        "with xbar_u)")
    add("  =>  Delta_erg = beta_between - beta_within = gamma   EXACTLY, with "
        "no free parameter")
    add("```")
    add(f"Planted gamma = {GAMMA_PLANT:+.4f}; the clause requires recovery of "
        f"that number and nothing else.")
    add("")

    mapping = part0["mapping"]
    add("### The ownership mapping (#76 operating point, derived here)")
    add("")
    add("```")
    add(mapping["formula"])
    add("```")
    _table(add, ["quantity", "rho target 0.50", "rho target 0.15",
                 "0.50, precision-floored (annotation)"], [
        ["authors in the mapping",
         f"{mapping['authors_in_the_mapping']:,}",
         f"{part0['mapping_low']['authors_in_the_mapping']:,}",
         f"{part0['mapping_precision_floored']['authors_in_the_mapping']:,}"],
        ["A_early = sigma^2 E[1/den_early]", fmt(mapping["A_early"], 8),
         fmt(part0["mapping_low"]["A_early"], 8),
         fmt(part0["mapping_precision_floored"]["A_early"], 8)],
        ["A_late = sigma^2 E[1/den_late]", fmt(mapping["A_late"], 8),
         fmt(part0["mapping_low"]["A_late"], 8),
         fmt(part0["mapping_precision_floored"]["A_late"], 8)],
        ["V = Var_u(beta_u) solving the target",
         fmt(mapping["V_slope_variance"], 8),
         fmt(part0["mapping_low"]["V_slope_variance"], 8),
         fmt(part0["mapping_precision_floored"]["V_slope_variance"], 8)],
        ["sd(beta_u) planted", fmt(mapping["sd_beta"], 6),
         fmt(part0["mapping_low"]["sd_beta"], 6),
         fmt(part0["mapping_precision_floored"]["sd_beta"], 6)],
        ["rho implied by the solution",
         fmt(mapping["rho_implied_by_the_solution"], 6),
         fmt(part0["mapping_low"]["rho_implied_by_the_solution"], 6),
         fmt(part0["mapping_precision_floored"][
             "rho_implied_by_the_solution"], 6)],
    ])

    add("### #88a region pricing — PINNED BEFORE ANY REAL-ARM NUMBER")
    add("")
    _table(add, ["region", "centre", "matched planted world",
                 "realized bootstrap half-width", "planted / realized rho"], [
        ["Delta_erg", fmt(regions["delta"]["centre"], 4),
         f"`{regions['delta']['matched_world']}`",
         fmt(regions["delta"]["half_width"], 6), "0 / n.a."],
        ["rho_own low", fmt(regions["rho_low"]["centre"], 2),
         f"`{regions['rho_low']['matched_world']}`",
         fmt(regions["rho_low"]["half_width"], 4),
         f"{fmt(regions['rho_low']['planted_rho'], 2)} / "
         f"{fmt(regions['rho_low']['realized_rho_mean'])}"],
        ["rho_own high", fmt(regions["rho_high"]["centre"], 2),
         f"`{regions['rho_high']['matched_world']}`",
         fmt(regions["rho_high"]["half_width"], 4),
         f"{fmt(regions['rho_high']['planted_rho'], 2)} / "
         f"{fmt(regions['rho_high']['realized_rho_mean'])}"],
    ])
    ann = regions["annotation_precision_floored"]
    add("ANNOTATION (routes nothing): the same pricing on the level-3 object "
        f"read through the x-only precision floor den >= "
        f"{PRECISION_FLOOR_DEN} — half-width "
        f"{fmt(ann['rho_low_half_width'], 4)} at 0.15 (realized rho "
        f"{fmt(ann['rho_low_realized_rho_mean'])}) and "
        f"{fmt(ann['rho_high_half_width'], 4)} at 0.50 (realized rho "
        f"{fmt(ann['rho_high_realized_rho_mean'])}).")
    add("")
    add(f"Pricing artifact written {regions['priced_utc']}; first real-arm "
        f"number computed {payload['ordering']['first_real_number_utc']} "
        f"(`{payload['ordering']['status']}`).")
    add("")

    if not arms:
        add("## Arms")
        add("")
        add("NOT SCORED — the A1 stop fired in Part 0. No arm's level-1, "
            "level-2 or level-3 estimand was computed, and "
            f"`{CELL_INDIST}` is expressly NOT the outcome of this leg.")
        add("")
        payload.setdefault("anomalies", [])
        _write_boundaries_and_config(add, payload)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    add("## The three levels, per arm")
    add("")
    _table(add, ["arm", "authors", "events",
                 "level 1 beta_between (CI)", "r_between",
                 "level 2 beta_within (CI)", "Delta_erg (CI)", "cell"],
           [[a["label"], f"{a['census']['authors']:,}",
             f"{a['census']['events']:,}",
             f"{fmt(a['beta_between'], 6)} "
             f"{fmt_ci(a['boot']['beta_between_ci'], 6)}",
             fmt(a["r_between"]),
             f"{fmt(a['beta_within'], 6)} "
             f"{fmt_ci(a['boot']['beta_within_ci'], 6)}",
             f"{fmt(a['delta_erg'], 6)} {fmt_ci(a['boot']['delta_ci'], 6)}",
             f"`{cells[k]['delta_cell']}`"]
            for k, a in arms.items()])
    add("Level 2 is the mean of the two half slopes; both halves are printed "
        "so the average is not a black box:")
    add("")
    _table(add, ["arm", "beta_within (early half)", "beta_within (late half)",
                 "mean = level 2"],
           [[a["label"], fmt(a["beta_within_early"], 6),
             fmt(a["beta_within_late"], 6), fmt(a["beta_within"], 6)]
            for a in arms.values()])

    add("## Level 3 — the per-person slope, its ownership and its true "
        "dispersion")
    add("")
    _table(add, ["arm", "authors scored", "dropped (constant half)",
                 "rho_own", "CI (B = 1000)", "pairing band (B = 499)",
                 "cell", "mean beta", "Var(beta) cross-half", "sd_true",
                 "headroom about the mean"],
           [[a["label"], f"{a['authors_scored_at_level_3']:,}",
             f"{a['authors_dropped_at_level_3']:,}",
             fmt(a["rho_own"]), fmt_ci(a["rho_ci"]),
             fmt_ci(a["ownership_null"]["band"]),
             f"`{cells[k]['rho_cell']}`",
             fmt(a["dispersion"]["mean_beta"], 6),
             fmt(a["dispersion"]["var_true_cross_half"], 8),
             fmt(a["dispersion"]["sd_true"], 6),
             f"[{fmt(a['dispersion']['headroom_lo'], 4)}, "
             f"{fmt(a['dispersion']['headroom_hi'], 4)}]"]
            for k, a in arms.items()])
    add("`Var(beta)` is the CROSS-HALF COVARIANCE of the two per-half slope "
        "estimates — the across-author variance with the per-half estimation "
        "noise removed. `headroom` (recorded definition) is the +-1.96 "
        "sd_true interval about the mean slope: what the owned dispersion "
        "buys around the average person, an annotation and not a measurement "
        "of any individual.")
    add("")
    add("NON-ROUTING sensitivity — the same level-3 object through the x-only "
        f"precision floor den >= {PRECISION_FLOOR_DEN}:")
    add("")
    _table(add, ["arm", "authors above the floor", "excluded", "rho_own",
                 "CI", "Var(beta) cross-half"],
           [[arms[k]["label"], f"{arms[k]['precision_floor']['authors']:,}",
             f"{arms[k]['precision_floor']['authors_excluded']:,}",
             fmt(arms[k]["precision_floor"]["rho_own"]),
             fmt_ci(arms[k]["precision_floor"]["boot"]["ci"]),
             fmt(arms[k]["precision_floor"]["dispersion"][
                 "var_true_cross_half"], 8)]
            for k in arms if "precision_floor" in arms[k]])

    add("## The owner's schema, mapped onto what was measured")
    add("")
    add("| the owner's design | what it yields | this leg's object | reading |")
    add("|---|---|---|---|")
    p = arms["primary"]
    add(f"| one-shot measurement of a GROUP | the BETWEEN-person relation | "
        f"`beta_between`, the OLS slope of person-mean y on person-mean x "
        f"over {p['census']['authors']:,} authors | "
        f"{fmt(p['beta_between'], 6)} "
        f"{fmt_ci(p['boot']['beta_between_ci'], 6)}, r = "
        f"{fmt(p['r_between'])} |")
    add(f"| repeated measurement of MANY | the AVERAGE WITHIN-person relation "
        f"| `beta_within`, the within-(author, half)-centered pooled slope, "
        f"averaged over the two halves | {fmt(p['beta_within'], 6)} "
        f"{fmt_ci(p['boot']['beta_within_ci'], 6)} |")
    add(f"| repeated measurement of ONE | THAT person's relation | "
        f"`beta_{{u,h}}`, one slope per author per half; its ownership "
        f"`rho_own` and its noise-free dispersion `Var(beta)` | rho_own "
        f"{fmt(p['rho_own'])} {fmt_ci(p['rho_ci'])}, Var(beta) = "
        f"{fmt(p['dispersion']['var_true_cross_half'], 8)} |")
    add(f"| **the comparison** | **whether level 1 = level 2** | "
        f"**`Delta_erg`**, paired author-cluster bootstrap | "
        f"**{fmt(p['delta_erg'], 6)} {fmt_ci(p['boot']['delta_ci'], 6)}** -> "
        f"`{cells['primary']['delta_cell']}` |")
    add("")

    add("## Registered leans (report against; they never route)")
    add("")
    _table(add, ["lean", "registered", "observed", "status"],
           [[r["lean"], r["registered"], r["observed"], f"`{r['status']}`"]
            for r in payload["leans"]])

    add("## #73 flags and #87 straddles")
    add("")
    if payload["flags_73"]:
        _table(add, ["arm", "object", "primary cell", "arm cell", "value",
                     "CI", "note"],
               [[f["arm"], f["object"], f"`{f['primary_cell']}`",
                 f"`{f['arm_cell']}`", fmt(f["value"], 6), fmt_ci(f["ci"], 6),
                 f["note"]] for f in payload["flags_73"]])
    else:
        add("None: every arm lands in the primary's cells and no interval "
            "crosses a priced region edge.")
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
        "`results/m4_x4_three_levels/` (gitignored). Every table above is "
        "generated from those artifacts (rule 24).")
    add("")


# ---------------------------------------------------------------------------
# Stage 7 — arms and main
# ---------------------------------------------------------------------------


def build_arms(cache: dict[str, Any], x_stats: dict[str, np.ndarray],
               log: RunLog) -> dict[str, Skeleton]:
    is_big5 = cache["pool_is_big5"]
    n_e = cache["n_early"].astype(np.int64)
    n_l = cache["n_total"].astype(np.int64) - n_e
    disjoint = ~is_big5
    floor100 = disjoint & (n_e >= POOL_FLOOR_SENSITIVITY) \
        & (n_l >= POOL_FLOOR_SENSITIVITY)
    specs = [
        ("primary", "PRIMARY — disjoint pool", disjoint),
        ("big5", "REPLICATION — Big5 pool", is_big5),
        ("floor100", "sensitivity — floor 100 events/half, disjoint pool",
         floor100),
    ]
    arms: dict[str, Skeleton] = {}
    for key, label, sel in specs:
        arms[key] = Skeleton(key, label, cache, sel, x_stats,
                             with_events=False)
        log.event("arm_built", **arms[key].census())
    return arms


def subset_moments(mom: dict[str, np.ndarray], codes: np.ndarray
                   ) -> dict[str, np.ndarray]:
    return {k: v[codes] for k, v in mom.items()}


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
                                     "PLAN.md#X4 (commit 42f0625)"),
              seed=SEED, b_perm=args.b_perm, b_boot=args.b_boot)

    config = {
        "leg": "M4-X4",
        "registration": ("docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md, "
                         "section X4, commit 42f0625"),
        "question_provenance": ("the program OWNER's conference input, "
                                "relayed 2026-08-19"),
        "seed": SEED, "seed_part0": SEED_PART0, "seed_perm": SEED_PERM,
        "seed_boot": SEED_BOOT,
        "b_perm": args.b_perm, "b_boot": args.b_boot,
        "x": ("log10(community share of all parseable events) — a GLOBAL "
              "fixed community attribute over the full stream"),
        "y": "log1p(word_count_quoteless)",
        "order": ("per-author stable sort by created_utc (ties keep stream "
                  "order)"),
        "halves": "full-stream median of the author's created_utc, <= early",
        "pool": (">= 50 events in EACH half AND within-author sd(x) > 0 in "
                 "EACH half (np.std per half slice, the census's own path)"),
        "pool_floor_primary": POOL_FLOOR_PRIMARY,
        "pool_floor_sensitivity": POOL_FLOOR_SENSITIVITY,
        "level_3_degeneracy_rule": ("a cell whose x is exactly constant "
                                    "(min == max) yields NaN and is counted; "
                                    "its contribution to the level-1 and "
                                    "level-2 pooled sums is exactly zero"),
        "precision_floor_den": PRECISION_FLOOR_DEN,
        "precision_floor_role": ("x-only NON-ROUTING sensitivity, pinned "
                                 "before any real number"),
        "boundary_centres": {"delta": BOUNDARY_DELTA_CENTRE,
                             "rho_low": BOUNDARY_RHO_LOW,
                             "rho_high": BOUNDARY_RHO_HIGH},
        "boundary_half_widths": ("PRICED IN-LEG (#88a) from Part 0's realized "
                                 "bootstrap half-widths on the matched "
                                 "planted worlds"),
        "planted_beta": BETA_PLANT, "planted_gamma": GAMMA_PLANT,
        "planted_sd_intercept": SD_A, "planted_sd_noise": SD_E,
        "rho_true_target": RHO_TRUE_TARGET, "rho_price_low": RHO_PRICE_LOW,
        "n_synth_replicates": N_SYNTH_REPLICATES,
        "ergodic_cover_floor": ERGODIC_COVER_FLOOR,
        "tol_rho": f"max({TOL_FLOOR_RHO}, {TOL_SD_MULT} x replicate sd)",
        "tol_delta": (f"max({TOL_DELTA_SCALE_FRAC} x |planted Delta scale|, "
                      f"{TOL_SD_MULT} x replicate sd)"),
        "comments": str(args.comments), "cohort": str(args.cohort),
        "columns_read": ["author", "subreddit", "created_utc",
                         "word_count_quoteless"],
        "author_profiles_csv": "NEVER OPENED (label-free)",
    }
    write_json(output / "config.json", config)
    config_sha = hashlib.sha256(
        json.dumps(config, sort_keys=True).encode("utf-8")).hexdigest()
    write_json(output / "config.sha256.json",
               {"sha256": config_sha, "utc": utc_now()})

    # ---- Stage 1: the event cache (x attached) ----------------------------
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

    # ---- Stage 2: the census (#57: x-only, no estimand value) -------------
    dis = census_quantities(cache, disjoint_sel)
    b5 = census_quantities(cache, is_big5)
    comm_x = cache["comm_x"]
    observed = {
        "rows parseable (author+subreddit+created_utc+wcq)":
            int(stats["rows_parseable"]),
        "authors": int(stats["authors"]),
        "Big5 cohort authors seen": int(big5_all.sum()),
        "disjoint authors": int((~big5_all).sum()),
        "communities": int(stats["subreddits"]),
        "x = log10(share), min (2 dp)": round(float(comm_x.min()), 2),
        "x = log10(share), max (2 dp)": round(float(comm_x.max()), 2),
        "pool (>= 50 each half AND sd(x) > 0 each half), disjoint":
            dis["pool_authors"],
        "pool (>= 50 each half AND sd(x) > 0 each half), Big5":
            b5["pool_authors"],
        "within-author sd(x) q25, disjoint (3 dp)":
            round(dis["sd_x_q25"], 3),
        "within-author sd(x) median, disjoint (3 dp)":
            round(dis["sd_x_median"], 3),
        "within-author sd(x) q75, disjoint (3 dp)":
            round(dis["sd_x_q75"], 3),
        "within-author sd(x) q25, Big5 (3 dp)": round(b5["sd_x_q25"], 3),
        "within-author sd(x) median, Big5 (3 dp)":
            round(b5["sd_x_median"], 3),
        "within-author sd(x) q75, Big5 (3 dp)": round(b5["sd_x_q75"], 3),
        "distinct communities per author, median, disjoint":
            dis["distinct_communities_median"],
        "distinct communities per author, median, Big5":
            b5["distinct_communities_median"],
        "top-1 community share, median, disjoint (3 dp)":
            round(dis["top1_share_median"], 3),
        "top-1 community share, q90, disjoint (3 dp)":
            round(dis["top1_share_q90"], 3),
        "top-1 community share, median, Big5 (3 dp)":
            round(b5["top1_share_median"], 3),
        "top-1 community share, q90, Big5 (3 dp)":
            round(b5["top1_share_q90"], 3),
    }
    expected = {
        "rows parseable (author+subreddit+created_utc+wcq)":
            ANCHOR_ROWS_PARSEABLE,
        "authors": ANCHOR_AUTHORS,
        "Big5 cohort authors seen": ANCHOR_BIG5_AUTHORS,
        "disjoint authors": ANCHOR_DISJOINT_AUTHORS,
        "communities": ANCHOR_COMMUNITIES,
        "x = log10(share), min (2 dp)": ANCHOR_X_MIN,
        "x = log10(share), max (2 dp)": ANCHOR_X_MAX,
        "pool (>= 50 each half AND sd(x) > 0 each half), disjoint":
            ANCHOR_POOL_DISJOINT,
        "pool (>= 50 each half AND sd(x) > 0 each half), Big5":
            ANCHOR_POOL_BIG5,
        "within-author sd(x) q25, disjoint (3 dp)": ANCHOR_SDX_DISJOINT[0],
        "within-author sd(x) median, disjoint (3 dp)": ANCHOR_SDX_DISJOINT[1],
        "within-author sd(x) q75, disjoint (3 dp)": ANCHOR_SDX_DISJOINT[2],
        "within-author sd(x) q25, Big5 (3 dp)": ANCHOR_SDX_BIG5[0],
        "within-author sd(x) median, Big5 (3 dp)": ANCHOR_SDX_BIG5[1],
        "within-author sd(x) q75, Big5 (3 dp)": ANCHOR_SDX_BIG5[2],
        "distinct communities per author, median, disjoint":
            ANCHOR_DISTINCT_COMM_DISJOINT,
        "distinct communities per author, median, Big5":
            ANCHOR_DISTINCT_COMM_BIG5,
        "top-1 community share, median, disjoint (3 dp)":
            ANCHOR_TOP1_DISJOINT[0],
        "top-1 community share, q90, disjoint (3 dp)":
            ANCHOR_TOP1_DISJOINT[1],
        "top-1 community share, median, Big5 (3 dp)": ANCHOR_TOP1_BIG5[0],
        "top-1 community share, q90, Big5 (3 dp)": ANCHOR_TOP1_BIG5[1],
    }
    census = anchor_gate(observed, expected)
    write_json(output / "census.json",
               {**census, "disjoint": dis, "big5": b5,
                "stream_stats": stats})
    log.event("census", status=census["status"])
    if census["status"] != "PASS":
        raise SystemExit(f"STOP (#78): the census gate FAILED: "
                         f"{json.dumps(census['pins'], indent=2, default=str)}")

    # ---- Stage 3: the realized skeletons (x-only) -------------------------
    x_stats = x_only_stats(cache)
    arms = build_arms(cache, x_stats, log)
    write_json(output / "arm_census.json",
               {k: a.census() for k, a in arms.items()})

    # ---- Stage 4: Part 0 on the primary skeleton --------------------------
    sk_part0 = Skeleton("primary", "PRIMARY — disjoint pool", cache,
                        disjoint_sel, x_stats, with_events=True)
    part0 = part0_gate(sk_part0, b_perm=args.b_perm, b_boot=args.b_boot,
                       seed=SEED_PART0, log=log)
    write_json(output / "part0_gate.json", part0)
    write_json(output / "region_pricing.json",
               {**part0["regions"],
                "ladder": ladder_status(part0["regions"])})
    log.event("part0", status=part0["status"],
              priced_utc=part0["regions"]["priced_utc"])
    sk_part0.events = None

    gates = {
        f"Census / blocking anchors (#78, {len(census['pins'])} predicates)":
            census["status"],
        "Part 0 realized-skeleton gate (6 ROUTING clauses)": part0["status"],
    }

    if part0["status"] != "PASS":
        verdict = build_verdict(part0, {}, {})
        write_json(output / "verdict.json", verdict)
        payload = {"run": {"finished_utc": utc_now(),
                           "runtime_s": time.time() - started},
                   "config": config, "config_sha256": config_sha,
                   "census": census, "part0": part0, "arms": {}, "cells": {},
                   "leans": [], "flags_73": [], "anomalies": [],
                   "ordering": {"first_real_number_utc": "never computed",
                                "status": "A1_STOP"},
                   "verdict": verdict, "gates": gates}
        write_report(args.report, payload)
        write_json(output / "report_payload.json",
                   {k: v for k, v in payload.items() if k != "config"})
        log.event("a1_stop", verdict=verdict["cell"])
        raise SystemExit("A1 STOP: Part 0 ROUTING clause failed; no corpus "
                         "estimand was scored.")

    # ---- Stage 5: THE FIRST REAL-ARM NUMBER (after the pricing) -----------
    first_real_utc = utc_now()
    log.event("first_real_number", utc=first_real_utc,
              note="the region pricing artifact is already on disk")
    pool_all = np.ones(cache["n_total"].size, dtype=bool)
    pool_sk = Skeleton("pool", "the whole pool", cache, pool_all, x_stats,
                       with_events=True)
    y_real = np.log1p(cache["ev_wcq"].astype(np.float64))
    mom_all = cell_moments(pool_sk, y_real)
    pool_sk.events = None
    del y_real

    results: dict[str, Any] = {}
    for i, (key, arm) in enumerate(arms.items()):
        results[key] = analyse_arm(
            arm, subset_moments(mom_all, arm.codes), b_perm=args.b_perm,
            b_boot=args.b_boot, seed_perm=SEED_PERM + 1000 * i,
            seed_boot=SEED_BOOT + 1000 * i)
        log.event("arm_done", arm=key,
                  beta_between=results[key]["beta_between"],
                  beta_within=results[key]["beta_within"],
                  delta_erg=results[key]["delta_erg"],
                  rho_own=results[key]["rho_own"])
    write_json(output / "arms.json", results)

    ordering = {
        "priced_utc": part0["regions"]["priced_utc"],
        "first_real_number_utc": first_real_utc,
        "status": "PASS" if part0["regions"]["priced_utc"] < first_real_utc
        else "FAIL",
        "note": ("#88a: the boundary regions were pinned to disk BEFORE any "
                 "real-arm estimand was computed; both timestamps come from "
                 "the artifacts, not from prose."),
    }
    write_json(output / "ordering.json", ordering)
    gates["#88a pricing order (regions pinned before the first real number)"] \
        = ordering["status"]
    if ordering["status"] != "PASS":
        raise SystemExit("STOP: the region pricing was not pinned before the "
                         "first real-arm number.")

    cells = {k: classify(v, part0["regions"]) for k, v in results.items()}
    write_json(output / "cells.json", cells)
    leans = evaluate_leans(cells, results, part0["regions"])
    write_json(output / "leans.json", leans)
    flags = flags_73(cells)
    write_json(output / "flags_73.json", flags)
    anomalies = honest_anomalies(arms["primary"], results, cells, part0)
    write_json(output / "anomalies.json", anomalies)
    verdict = build_verdict(part0, cells, results)
    write_json(output / "verdict.json", verdict)
    log.event("verdict", cell=verdict["cell"],
              co_primary=verdict["co_primary_cell"],
              delta_erg=verdict["delta_erg"])

    payload = {
        "run": {"finished_utc": utc_now(), "runtime_s": time.time() - started},
        "config": config, "config_sha256": config_sha, "census": census,
        "part0": part0, "arms": results, "cells": cells, "leans": leans,
        "flags_73": flags, "anomalies": anomalies, "ordering": ordering,
        "verdict": verdict, "gates": gates,
    }
    write_report(args.report, payload)

    # ---- Stage 6: the ID-leak gate over the widened universe (#83) --------
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
