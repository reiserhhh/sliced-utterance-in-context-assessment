#!/usr/bin/env python3
"""SUICA M4-X5 — the ergodicity atlas (bridge build-out item 2).

Registered BEFORE the run in ``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``
(commit de09409, section "X5 — the ergodicity atlas").  This runner executes
that registration and nothing else.

THE OBJECT.  Not one relation but a MAP: five metadata relations, each measured
THREE-LEVEL-COMPLETE (bridge section 6) with X4's machinery, so the atlas can
say WHICH KINDS of metadata relation carry large level-conflation errors and
where the individual parameters live.

    R1  commonness x volume   x = log10(community share), y = log1p(wcq)
        Delta_erg IMPORTED from X4's committed artifacts (bit-checked);
        ownership RECOMPUTED under the estimability floor.
    R2  gap x volume          x = log10(seconds since the author's previous
                              comment over the full stream), y = log1p(wcq)
    R3  volume x score        x = log1p(wcq), y = slog(score)
    R4  commonness x score    x = log10(community share), y = slog(score)
    R5  commonness x gap      x = log10(community share), y = log10(gap s)

    slog(s) = sign(s) * log1p(|s|)          (score is signed; #70's transform
                                             extended to a signed quantity)

    order  = per-author stable sort by created_utc (ties keep stream order)
    halves = full-stream median of the author's own created_utc (<= early)
    pool   = per relation: >= 50 USABLE events in EACH half AND the #89
             ESTIMABILITY FLOOR den = sum (x - xbar)^2 >= 1 in EACH half,
             den computed by the PINNED two-pass float64 path (cell mean
             first, then the sum of squared deviations)

    level 1  beta_between = OLS slope of person-mean y on person-mean x
    level 2  beta_within  = within-(author, half)-centered pooled slope,
                            computed per half and averaged over the halves
    level 3  beta_{u,h}   = the FLOORED per-(author, half) slope (the pool's
                            own floor makes every scored cell estimable);
                            ownership rho_own = Pearson over authors of
                            (beta_early, beta_late)

    per relation  Delta_erg = beta_between - beta_within, paired author-cluster
                  bootstrap (both slopes recomputed from the SAME author draw)
    VERDICT       the SUMMARY SHAPE of the five Delta cells (the atlas route)

THE THREE DEFECTS THE REGISTRATION BAKED IN (#89-#91, purchased by X4)
---------------------------------------------------------------------
#89  ESTIMABILITY FLOOR.  A pool clause stated as "sd(x) > 0" is not an
     estimability predicate and is float-path sensitive.  X5 states the floor
     in the estimand's own denominator units (den >= 1: the per-half slope's
     sampling sd does not exceed the event-noise sd) and PINS the computation
     path.  The floored per-author slope is the level-3 estimator THROUGHOUT.
#90  PRECISION CEILINGS.  A tolerance of max(floor, 3 x replicate sd) cannot
     tell "recovered" from "too unstable to say".  Every ROUTING RECOVERY
     clause here also asserts rep-sd <= the registered tolerance floor; a
     clause whose replicate spread exceeds its floor is UNINFORMATIVE and,
     being a routing clause, STOPS THE LEG (A1).
#91  LADDER COHERENCE.  Priced #87 regions can overlap and silently empty an
     interior cell.  After pricing, each relation asserts that its regions are
     disjoint with non-empty interior cells; ELSE the ownership classification
     COLLAPSES EXPLICITLY to the binary OWNED (CI > 0) / NOT_OWNED, stated per
     relation.  No silent empty cells.

GOVERNANCE
----------
Metadata only.  The stream reads exactly five columns — ``author``,
``subreddit``, ``created_utc``, ``word_count_quoteless``, ``score``.  NO text
body is ever read.  ``author_profiles.csv`` is NEVER opened; the leg is
label-free end to end (the Big5 cohort enters only as a NAME LIST that splits
the corpus into two disjoint author sets).  Caches live in gitignored
``results/`` and are never committed.  Aggregates only.  EXPLORATORY,
corpus-level; no person claims; no psychological naming (expression VOLUME,
timing and platform feedback are technical objects, not traits).

MACHINERY PROVENANCE (#56/#81 — the inherited object, imported BY FILE)
-----------------------------------------------------------------------
Everything three-level comes from the X4 runner (which imports X2, which
imports X1b -> X1 -> U2/U2b): ``three_levels``, ``cell_moments``,
``per_cell_slopes``, ``paired_level_bootstrap``, ``dispersion``,
``ownership_slope_target``, ``plant_world``, ``synthetic_replicate``,
``run_world``, ``delta_cell``, ``edges_straddled``, the cell names, the world
names, the planted-world constants, ``community_x``, ``pool_author_of_event``
and — through X4 — ``RunLog``, ``write_json``, ``utc_now``, ``fmt``,
``fmt_ci``, ``percentile_ci``, ``rowwise_pearson``, ``ownership_null``,
``cluster_bootstrap_pairs``, ``order_and_halve``, ``anchor_gate``, ``_exact``,
``_table`` and the #83 HEAD-baseline helpers.  They are BOUND, not copied; a
contract test asserts the binding.

X5's event cache is FRESH: X4's carries neither ``score`` nor the inter-event
gap, and X5's pool predicate is per relation and floored.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
from dataclasses import dataclass
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

POOL_FLOOR_EVENTS = 50              # registration pin: >= 50 USABLE per half
ESTIMABILITY_FLOOR_DEN = 1.0        # registration pin (#89): den >= 1

# --- #90 tolerance floors (the CEILING is asserted against these) ----------
# X4 priced the Delta recovery tolerance at 2% of the planted scale (0.005 at
# gamma = 0.25) and the rho recovery tolerance at an absolute 0.02.  #90 turns
# the floor into a CEILING on the replicate spread, so the floor must be a
# resolution statement in the estimand's OWN units rather than a fraction of a
# freely chosen planted scale.  RECORDED CHOICE, made before any real number
# and disclosed in the report: both floors are absolute 0.02 — in Delta units
# (a slope difference of 0.02 is a quarter of X4's realized Delta) and in
# correlation units (X4's, unchanged).  The planted world is X4's, untouched.
TOL_FLOOR_DELTA = 0.02
TOL_FLOOR_RHO = 0.02
TOL_SD_MULT = 3.0                   # inherited: max(floor, 3 x replicate sd)

# --- the level-3 plateau PREDICTION (bridge section 7) ---------------------
# X1c's response-profile persistence 0.279, X2's rhythm ownership 0.259 and
# X4's floored slope ownership 0.277 lie in one narrow band.  The registration
# turns that observation into a PREDICTION for the four new relations.  The
# band is pinned here, before the run, as the rounded interval containing all
# three named values.
PLATEAU_BAND = (0.25, 0.30)
PLATEAU_MIN_RELATIONS = 2           # ">= 2 of the four new relations"

# --- #87 boundary REGIONS: centres are pins, half-widths priced in-leg -----
BOUNDARY_DELTA_CENTRE = 0.0
BOUNDARY_RHO_LOW = 0.15
BOUNDARY_RHO_HIGH = 0.50

# --- atlas routes (NULL-first #55) -----------------------------------------
ATLAS_UNIFORM_ERGODIC = "ATLAS_UNIFORM_ERGODIC"
ATLAS_UNIFORM_NONERGODIC = "ATLAS_UNIFORM_NONERGODIC"
ATLAS_HETEROGENEOUS = "ATLAS_HETEROGENEOUS"
ATLAS_A1_STOP = "A1_STOP__SYNTHETIC_GATE_FAILED"

# --- ownership cells (the ladder, and the #91 collapse) --------------------
CELL_OWNED_BINARY = "OWNED"
CELL_NOT_OWNED_BINARY = "NOT_OWNED"

# --- inherited anchors (BLOCKING under #78) --------------------------------
ANCHOR_ROWS_PARSEABLE = 17_640_062
ANCHOR_AUTHORS = 10_296
ANCHOR_BIG5_AUTHORS = 1_401
ANCHOR_DISJOINT_AUTHORS = 8_895
ANCHOR_COMMUNITIES = 46_214
ANCHOR_X_MIN = -7.25
ANCHOR_X_MAX = -1.14
ANCHOR_SCORE_MISSING = 147

# --- the X5 census (planner arithmetic, BLOCKING under #78) ----------------
# R1's pools are X4's (the sd(x) > 0 path), recomputed here as the strongest
# available check that this leg's fresh cache reproduces X4's universe.
ANCHOR_POOL = {
    "R1": (8_004, 1_112),
    "R2": (7_989, 1_100),
    "R3": (8_008, 1_116),
    "R4": (7_986, 1_096),
    "R5": (7_966, 1_081),
}
ANCHOR_SDX_MEDIAN_DISJOINT = {"R2": 1.138, "R3": 1.031, "R4": 0.966,
                              "R5": 0.966}

# --- X4's committed values imported by R1 (bit-checked) --------------------
X4_RESULTS = ROOT / "results/m4_x4_three_levels"
X4_IMPORT_TOL = 1e-12

# --- recorded implementation choices (registration silent) -----------------
CHUNK_SIZE = 2_000_000
CACHE_VERSION = 1

SEED_PART0 = SEED + 1
SEED_PERM = SEED + 2
SEED_BOOT = SEED + 3

DEFAULT_COMMENTS = Path(
    "/Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/"
    "all_comments_since_2015.csv")
DEFAULT_COHORT = ROOT / "results/m4_sr0_recon/cohort_authors.csv"
DEFAULT_OUTPUT = ROOT / "results/m4_x5_ergodicity_atlas"
DEFAULT_REPORT = ROOT / "reports/SUICA_M4_X5_ERGODICITY_ATLAS_REPORT.md"

X4_SCRIPT = ROOT / "scripts/run_suica_m4_x4_three_levels.py"

COMMITTED_FILES = (
    ROOT / "reports/SUICA_M4_X5_ERGODICITY_ATLAS_REPORT.md",
    ROOT / "scripts/run_suica_m4_x5_ergodicity_atlas.py",
    ROOT / "tests/test_m4_x5_ergodicity_atlas.py",
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


X4 = load_module("suica_m4_x4_for_x5", X4_SCRIPT)

write_json = X4.write_json
utc_now = X4.utc_now
fmt = X4.fmt
fmt_ci = X4.fmt_ci
RunLog = X4.RunLog
percentile_ci = X4.percentile_ci
scan_for_cohort_ids = X4.scan_for_cohort_ids
baseline_hit_keys = X4.baseline_hit_keys
new_hits_only = X4.new_hits_only
anchor_gate = X4.anchor_gate
_exact = X4._exact
_table = X4._table
_Interner = X4._Interner
_sorted_remap = X4._sorted_remap
order_and_halve = X4.order_and_halve
rowwise_pearson = X4.rowwise_pearson
ownership_null = X4.ownership_null
cluster_bootstrap_pairs = X4.cluster_bootstrap_pairs
community_x = X4.community_x
cell_moments = X4.cell_moments
three_levels = X4.three_levels
per_cell_slopes = X4.per_cell_slopes
paired_level_bootstrap = X4.paired_level_bootstrap
dispersion = X4.dispersion
ownership_slope_target = X4.ownership_slope_target
run_world = X4.run_world
delta_cell = X4.delta_cell
edges_straddled = X4.edges_straddled

CELL_INDIST = X4.CELL_INDIST
CELL_SAME_SIGN = X4.CELL_SAME_SIGN
CELL_SIGN_FLIP = X4.CELL_SIGN_FLIP
CELL_SIGN_UNRESOLVED = X4.CELL_SIGN_UNRESOLVED
NONERGODIC_CELLS = (CELL_SAME_SIGN, CELL_SIGN_FLIP, CELL_SIGN_UNRESOLVED)
CELL_NOT_OWNED = X4.CELL_NOT_OWNED
CELL_AT_LOW = X4.CELL_AT_LOW
CELL_WEAK = X4.CELL_WEAK
CELL_AT_HIGH = X4.CELL_AT_HIGH
CELL_STRONG = X4.CELL_STRONG

WORLD_ERGODIC = X4.WORLD_ERGODIC
WORLD_NONERGODIC = X4.WORLD_NONERGODIC
WORLD_OWNED = X4.WORLD_OWNED
WORLD_OWNED_LOW = X4.WORLD_OWNED_LOW
WORLD_NULL = X4.WORLD_NULL

N_SYNTH_REPLICATES = X4.N_SYNTH_REPLICATES
ERGODIC_COVER_FLOOR = X4.ERGODIC_COVER_FLOOR
BETA_PLANT = X4.BETA_PLANT
GAMMA_PLANT = X4.GAMMA_PLANT
SD_A = X4.SD_A
SD_E = X4.SD_E
RHO_TRUE_TARGET = X4.RHO_TRUE_TARGET
RHO_PRICE_LOW = X4.RHO_PRICE_LOW


# ---------------------------------------------------------------------------
# The five relations (transforms pinned #70)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RelationSpec:
    key: str
    title: str
    x: str                      # channel name
    y: str                      # channel name
    imported: bool = False      # R1: Delta imported from X4


RELATIONS = (
    RelationSpec("R1", "commonness x volume", "common", "volume",
                 imported=True),
    RelationSpec("R2", "gap x volume", "gap", "volume"),
    RelationSpec("R3", "volume x score", "volume", "score"),
    RelationSpec("R4", "commonness x score", "common", "score"),
    RelationSpec("R5", "commonness x gap", "common", "gap"),
)
RELATION_BY_KEY = {spec.key: spec for spec in RELATIONS}
NEW_RELATIONS = tuple(spec.key for spec in RELATIONS if not spec.imported)

CHANNEL_TEXT = {
    "common": "log10(community share of all parseable events)",
    "volume": "log1p(word_count_quoteless)",
    "score": "slog(score) = sign(score) * log1p(abs(score))",
    "gap": "log10(seconds since the author's previous comment, full stream)",
}

COHORTS = (("disjoint", "PRIMARY — disjoint pool"),
           ("big5", "REPLICATION — Big5 pool (#73)"))


def slog(values: np.ndarray) -> np.ndarray:
    """The signed log transform for ``score`` (a signed platform counter)."""

    values = np.asarray(values, dtype=np.float64)
    return np.sign(values) * np.log1p(np.abs(values))


# ---------------------------------------------------------------------------
# Stage 1 — the event stream (one pass; no bodies, no labels)
# ---------------------------------------------------------------------------


def stream_events(comments_path: Path, log: RunLog) -> dict[str, Any]:
    """Stream the comments file for the five metadata columns X5 needs.

    PARSEABLE is X4's predicate on FOUR columns (author, subreddit,
    created_utc, word_count_quoteless), so the row count, the author universe
    and the community shares reproduce X4's exactly.  ``score`` rides along and
    is allowed to be missing; the missing count is an anchor.
    """

    columns = ["author", "subreddit", "created_utc", "word_count_quoteless",
               "score"]
    log.event("stream_start", comments_path=str(comments_path),
              columns=columns, note="no body column requested")
    authors = _Interner()
    subreddits = _Interner()
    author_parts: list[np.ndarray] = []
    subreddit_parts: list[np.ndarray] = []
    created_parts: list[np.ndarray] = []
    wcq_parts: list[np.ndarray] = []
    score_parts: list[np.ndarray] = []
    rows_streamed = 0
    rows_parseable = 0
    score_missing = 0
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
        score = pd.to_numeric(chunk["score"], errors="coerce")
        keep = (chunk["author"].notna() & chunk["subreddit"].notna()
                & created.notna() & wcq.notna())
        n_keep = int(keep.sum())
        rows_parseable += n_keep
        if n_keep == 0:
            continue
        wcq_keep = wcq[keep].to_numpy(np.float64)
        score_keep = score[keep].to_numpy(np.float64)
        wcq_zero += int(np.count_nonzero(wcq_keep == 0.0))
        score_missing += int(np.count_nonzero(~np.isfinite(score_keep)))
        author_parts.append(authors.encode(chunk["author"][keep]))
        subreddit_parts.append(subreddits.encode(chunk["subreddit"][keep]))
        created_parts.append(created[keep].to_numpy(np.float64))
        wcq_parts.append(wcq_keep.astype(np.int32))
        score_parts.append(score_keep)
        log.event("stream_chunk", chunk=chunks, rows_streamed=rows_streamed,
                  rows_parseable=rows_parseable)

    author_raw = np.concatenate(author_parts)
    subreddit_raw = np.concatenate(subreddit_parts)
    created = np.concatenate(created_parts)
    wcq = np.concatenate(wcq_parts)
    score = np.concatenate(score_parts)
    del author_parts, subreddit_parts, created_parts, wcq_parts, score_parts

    author_names, author_remap = _sorted_remap(authors.names())
    subreddit_names, subreddit_remap = _sorted_remap(subreddits.names())
    author_code = author_remap[author_raw].astype(np.int32)
    subreddit_code = subreddit_remap[subreddit_raw].astype(np.int32)
    del author_raw, subreddit_raw

    stats = {
        "rows_streamed": rows_streamed,
        "rows_parseable": rows_parseable,
        "rows_unparseable": rows_streamed - rows_parseable,
        "score_missing": score_missing,
        "wcq_zero_rows": wcq_zero,
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
        "score": score,
        "authors": author_names,
        "subreddits": subreddit_names,
        "stream_stats": stats,
    }


CACHE_ARRAYS = ("pool_author_code", "pool_is_big5", "offsets", "n_early",
                "n_total", "ev_common", "ev_volume", "ev_score", "ev_gap",
                "comm_x", "comm_count")


def build_event_cache(scaffold: dict[str, Any], big5_mask: np.ndarray,
                      log: RunLog) -> dict[str, Any]:
    """The CANDIDATE skeleton: every author with >= 50 events in EACH half.

    The candidate predicate is deliberately looser than any relation's pool:
    a relation's usable events are a subset of the author's events, so
    ">= 50 USABLE events in each half" implies ">= 50 events in each half".
    Caching the candidates once lets all five relations be pooled from one
    stream pass, each by its own predicate.

    Every channel is stored ALREADY TRANSFORMED (#70 pinned), with NaN marking
    an event the channel cannot speak for: ``ev_score`` is NaN where the score
    column was missing, ``ev_gap`` is NaN for the first event of an author's
    stream and for any nonpositive gap (a tie in created_utc).
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
    common_sorted = x_by_comm[scaffold["subreddit_code"][order]]
    volume_sorted = np.log1p(scaffold["wcq"][order].astype(np.float64))
    score_sorted = slog(scaffold["score"][order])
    created_sorted = created[order]
    del order
    log.event("halves_assigned", early_rows=int((half == 0).sum()),
              late_rows=int((half == 1).sum()))

    # The inter-event gap over the author's FULL ordered stream.  The first
    # event of each author has no predecessor; a tie in created_utc gives a
    # nonpositive gap.  Both are marked NaN and counted.
    gap_seconds = np.empty(created_sorted.size, dtype=np.float64)
    gap_seconds[0] = np.nan
    gap_seconds[1:] = created_sorted[1:] - created_sorted[:-1]
    first_of_author = np.empty(a_sorted.size, dtype=bool)
    first_of_author[0] = True
    first_of_author[1:] = a_sorted[1:] != a_sorted[:-1]
    gap_seconds[first_of_author] = np.nan
    nonpositive = np.zeros(gap_seconds.size, dtype=bool)
    np.less_equal(gap_seconds, 0.0, out=nonpositive,
                  where=np.isfinite(gap_seconds))
    with np.errstate(divide="ignore", invalid="ignore"):
        gap_sorted = np.log10(gap_seconds)
    gap_sorted[nonpositive] = np.nan
    log.event("gap_channel", first_events=int(first_of_author.sum()),
              nonpositive_gaps=int(nonpositive.sum()),
              defined=int(np.isfinite(gap_sorted).sum()))
    del gap_seconds, created_sorted, first_of_author, nonpositive

    key = a_sorted.astype(np.int64) * 2 + half.astype(np.int64)
    cell_n = np.bincount(key, minlength=2 * n_authors).astype(np.int64)
    del key
    n_early = cell_n[0::2]
    n_late = cell_n[1::2]
    candidate = (n_early >= POOL_FLOOR_EVENTS) & (n_late >= POOL_FLOOR_EVENTS)
    candidate_codes = np.flatnonzero(candidate).astype(np.int32)
    log.event("candidates", floor=POOL_FLOOR_EVENTS,
              authors=int(candidate.sum()),
              disjoint=int((candidate & ~big5_mask).sum()),
              big5=int((candidate & big5_mask).sum()))

    keep_event = candidate[a_sorted]
    cache = {
        "pool_author_code": candidate_codes,
        "pool_is_big5": big5_mask[candidate_codes],
        "n_early": n_early[candidate_codes].astype(np.int64),
        "n_total": counts[candidate_codes].astype(np.int64),
        "ev_common": common_sorted[keep_event],
        "ev_volume": volume_sorted[keep_event],
        "ev_score": score_sorted[keep_event],
        "ev_gap": gap_sorted[keep_event],
        "comm_x": x_by_comm,
        "comm_count": comm_counts,
        "n_subs": n_subs,
        "n_authors": n_authors,
    }
    cache["offsets"] = np.concatenate(
        ([0], np.cumsum(cache["n_total"]))).astype(np.int64)
    log.event("event_cache_built", candidate_authors=int(candidate_codes.size),
              cached_events=int(cache["offsets"][-1]),
              corpus_events=int(a_sorted.size))
    return cache


def save_cache(cache: dict[str, Any], scaffold: dict[str, Any],
               path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, **{k: cache[k] for k in CACHE_ARRAYS})
    write_json(path.with_suffix(".meta.json"), {
        "cache_version": CACHE_VERSION,
        "authors": scaffold["authors"],
        "stream_stats": scaffold["stream_stats"],
        "n_subs": cache["n_subs"],
        "n_authors": cache["n_authors"],
        "candidate_floor": POOL_FLOOR_EVENTS,
        "note": ("gitignored; metadata only; no bodies, no labels; the four "
                 "channels are stored already transformed, NaN where the "
                 "channel cannot speak for the event"),
    })


def load_cache(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = np.load(path)
    meta = json.loads(path.with_suffix(".meta.json").read_text("utf-8"))
    cache = {k: payload[k] for k in CACHE_ARRAYS}
    cache["n_subs"] = int(meta["n_subs"])
    cache["n_authors"] = int(meta["n_authors"])
    return cache, meta


# ---------------------------------------------------------------------------
# Stage 2 — per-relation x-only statistics and the #89 floor
# ---------------------------------------------------------------------------


def event_author_and_half(cache: dict[str, Any]
                          ) -> tuple[np.ndarray, np.ndarray]:
    """Local candidate-author index and half (0 early, 1 late) per event."""

    n_total = cache["n_total"].astype(np.int64)
    who = np.repeat(np.arange(n_total.size, dtype=np.int32), n_total)
    local = np.arange(who.size, dtype=np.int64) - np.repeat(
        cache["offsets"][:-1], n_total)
    half = (local >= np.repeat(cache["n_early"].astype(np.int64), n_total)
            ).astype(np.int8)
    return who, half


def two_pass_den(x: np.ndarray, key: np.ndarray, size: int
                 ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """THE PINNED #89 PATH: cell counts, cell means, and den by two passes.

    Pass 1 accumulates the cell sums and divides by the cell counts.  Pass 2
    accumulates the squared deviations from those means.  Both passes are
    float64 ``np.bincount`` accumulations over the events in stream order, so
    the path is fixed rather than left to whichever equivalent formula a
    reader would have chosen — the exact defect #89 names.  A one-pass
    E[x^2] - E[x]^2 form is NOT used: it cancels catastrophically on the cells
    whose spread is smallest, which are precisely the cells the floor judges.
    """

    cnt = np.bincount(key, minlength=size).astype(np.float64)
    total = np.bincount(key, weights=x, minlength=size)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = np.where(cnt > 0, total / np.maximum(cnt, 1.0), np.nan)
    dev = x - mean[key]
    den = np.bincount(key, weights=dev * dev, minlength=size)
    return cnt, mean, den


class RelationSkeleton:
    """One (relation, cohort) realized skeleton — x-only, no y anywhere.

    The attribute names are X4's Skeleton's, deliberately: X4's
    ``cell_moments``, ``per_cell_slopes``, ``ownership_slope_target``,
    ``plant_world``, ``synthetic_replicate`` and ``run_world`` are BOUND, not
    reimplemented, and they read exactly these fields.  ``degenerate_*`` is
    all-False by construction here — the #89 floor is part of the POOL, so
    every cell that enters is estimable and the level-3 estimator is the
    FLOORED slope throughout.
    """

    def __init__(self, key: str, label: str, relation: RelationSpec,
                 cache: dict[str, Any], sel: np.ndarray,
                 stats: dict[str, np.ndarray], who: np.ndarray,
                 half: np.ndarray, *, with_events: bool) -> None:
        codes = np.flatnonzero(sel).astype(np.int64)
        self.key = key
        self.label = label
        self.relation = relation
        self.codes = codes
        self.n_authors = int(codes.size)
        self.n_e = stats["n_e"][codes]
        self.n_l = stats["n_l"][codes]
        self.den_e = stats["den_e"][codes]
        self.den_l = stats["den_l"][codes]
        self.xbar = stats["xbar"][codes]
        self.n_u = self.n_e + self.n_l
        self.degenerate_e = np.zeros(self.n_authors, dtype=bool)
        self.degenerate_l = np.zeros(self.n_authors, dtype=bool)
        self.ok = np.ones(self.n_authors, dtype=bool)
        self.precise = self.ok
        self.n_events = int(self.n_u.sum())
        self.events = None
        if with_events:
            self.events = self._event_view(cache, stats, who, half)

    def _event_view(self, cache: dict[str, Any], stats: dict[str, np.ndarray],
                    who_all: np.ndarray, half_all: np.ndarray
                    ) -> dict[str, Any]:
        """The usable events of this skeleton's authors, in stream order.

        ``sel_event`` is kept so the caller can lift the SAME events out of the
        y channel with the same mask — the x view and the y vector cannot fall
        out of step.
        """

        in_arm = np.zeros(stats["n_candidates"], dtype=bool)
        in_arm[self.codes] = True
        sel_event = stats["usable"] & in_arm[who_all]
        remap = np.full(stats["n_candidates"], -1, dtype=np.int64)
        remap[self.codes] = np.arange(self.n_authors, dtype=np.int64)
        who = remap[who_all[sel_event]]
        half = half_all[sel_event].astype(np.int64)
        x = cache[f"ev_{self.relation.x}"][sel_event]
        key = who * 2 + half
        size = 2 * self.n_authors
        cell_n = np.bincount(key, minlength=size).astype(np.float64)
        cell_sx = np.bincount(key, weights=x, minlength=size)
        dev_x = x - (cell_sx / cell_n)[key]
        return {"x": x, "key": key, "who": who, "cell_n": cell_n,
                "dev_x": dev_x, "size": size, "n_events": int(x.size),
                "sel_event": sel_event}

    def census(self) -> dict[str, Any]:
        return {
            "relation": self.relation.key,
            "cohort": self.key,
            "label": self.label,
            "authors": self.n_authors,
            "usable_events": self.n_events,
            "cells": 2 * self.n_authors,
            "median_events_per_half": float(np.median(
                0.5 * (self.n_e + self.n_l))),
            "median_den_early": float(np.median(self.den_e)),
            "median_den_late": float(np.median(self.den_l)),
            "min_den_early": float(np.min(self.den_e)),
            "min_den_late": float(np.min(self.den_l)),
        }


def relation_stats(cache: dict[str, Any], relation: RelationSpec,
                   who: np.ndarray, half: np.ndarray) -> dict[str, Any]:
    """Per-(candidate author, half) usable counts and #89 den, x-only.

    The USABLE set is the intersection of the two channels' availability: an
    event enters a relation only if both its x and its y exist.  Everything
    returned here is a function of x alone plus that mask — no x-y quantity is
    evaluated (#57).
    """

    xv = cache[f"ev_{relation.x}"]
    yv = cache[f"ev_{relation.y}"]
    usable = np.isfinite(xv) & np.isfinite(yv)
    x = xv[usable]
    who_u = who[usable].astype(np.int64)
    half_u = half[usable].astype(np.int64)
    n_authors = int(cache["n_total"].size)
    key = who_u * 2 + half_u
    cnt, _, den = two_pass_den(x, key, 2 * n_authors)
    n_e, n_l = cnt[0::2], cnt[1::2]
    den_e, den_l = den[0::2], den[1::2]
    sum_x = np.bincount(who_u, weights=x, minlength=n_authors)
    n_u = n_e + n_l
    with np.errstate(invalid="ignore", divide="ignore"):
        xbar = np.where(n_u > 0, sum_x / np.maximum(n_u, 1.0), np.nan)
    count_floor = (n_e >= POOL_FLOOR_EVENTS) & (n_l >= POOL_FLOOR_EVENTS)
    den_floor = (den_e >= ESTIMABILITY_FLOOR_DEN) & (
        den_l >= ESTIMABILITY_FLOOR_DEN)
    pool = count_floor & den_floor
    with np.errstate(invalid="ignore", divide="ignore"):
        sd_e = np.sqrt(np.where(n_e > 0, den_e / np.maximum(n_e, 1.0), np.nan))
        sd_l = np.sqrt(np.where(n_l > 0, den_l / np.maximum(n_l, 1.0), np.nan))
    return {
        "n_e": n_e, "n_l": n_l, "den_e": den_e, "den_l": den_l, "xbar": xbar,
        "within_sd_x": 0.5 * (sd_e + sd_l),
        "count_floor": count_floor, "den_floor": den_floor, "pool": pool,
        "usable": usable, "n_candidates": n_authors,
        "usable_events": int(x.size),
        "dropped_by_the_count_floor": int((~count_floor).sum()),
        "dropped_by_the_den_floor": int((count_floor & ~den_floor).sum()),
    }


def x4_pool_mask(cache: dict[str, Any]) -> np.ndarray:
    """X4's OWN pool clause, reproduced: ``np.std(x, ddof=1) > 0`` per half.

    R1's registered pools (8,004 / 1,112) are X4's, and X4's anomaly record
    shows the clause is FLOAT-PATH SENSITIVE.  Reproducing it here — on this
    leg's fresh five-column cache — is the strongest available check that the
    new cache is the same universe as the committed one, and it is exactly
    the predicate defect #89 replaces for every other relation.
    """

    n_total = cache["n_total"].astype(np.int64)
    x = cache["ev_common"]
    offsets = cache["offsets"]
    n_early = cache["n_early"].astype(np.int64)
    out = np.zeros(n_total.size, dtype=bool)
    for code in range(n_total.size):
        s0 = int(offsets[code])
        n_e = int(n_early[code])
        n_t = int(n_total[code])
        early = x[s0:s0 + n_e]
        late = x[s0 + n_e:s0 + n_t]
        out[code] = bool(np.std(early, ddof=1) > 0.0
                         and np.std(late, ddof=1) > 0.0)
    return out


# ---------------------------------------------------------------------------
# Stage 3 — Part 0: the per-relation gate on the realized skeleton
# ---------------------------------------------------------------------------


def ceiling_clause(name: str, rep_sd: float, floor: float) -> dict[str, Any]:
    """#90: a routing recovery clause must be INFORMATIVE to certify anything.

    The tolerance ``max(floor, 3 x rep sd)`` cannot distinguish "recovered"
    from "too unstable to say".  The ceiling asserts that the replicate spread
    itself is inside the registered floor; if it is not, the clause reports
    UNINFORMATIVE — a first-class status — and, being a ROUTING clause, stops
    the leg.
    """

    informative = bool(np.isfinite(rep_sd) and rep_sd <= floor)
    return {
        "object": name,
        "replicate_sd": float(rep_sd),
        "ceiling": float(floor),
        "informative": informative,
        "status": "INFORMATIVE" if informative else "UNINFORMATIVE",
        "note": ("the replicate spread is inside the registered tolerance "
                 "floor, so a recovery inside the tolerance is a statement "
                 "about the estimator and not about the spread"
                 if informative else
                 "the replicate spread EXCEEDS the registered tolerance "
                 "floor, so the recovery clause could not have failed for "
                 "the right reason; #90 records it as UNINFORMATIVE and the "
                 "leg stops (A1)"),
    }


def price_regions(relation: str, null_world: dict[str, Any],
                  owned_low: dict[str, Any], owned_high: dict[str, Any]
                  ) -> dict[str, Any]:
    """#88a: the #87 half-widths ARE the matched planted worlds' realized
    bootstrap half-widths, pinned before any real number of this relation."""

    return {
        "relation": relation,
        "priced_utc": utc_now(),
        "source": ("#88a executed IN-LEG: every half-width is the MEAN over "
                   f"Part 0's {N_SYNTH_REPLICATES} replicates of the REALIZED "
                   "bootstrap half-width on the MATCHED planted world, on "
                   "THIS relation's own skeleton, pinned before any real-arm "
                   "number was computed."),
        "delta": {"centre": BOUNDARY_DELTA_CENTRE,
                  "matched_world": WORLD_NULL,
                  "half_width": null_world["delta_half_width_mean"]},
        "rho_low": {"centre": BOUNDARY_RHO_LOW,
                    "matched_world": WORLD_OWNED_LOW,
                    "half_width": owned_low["rho_half_width_mean"],
                    "planted_rho": RHO_PRICE_LOW,
                    "realized_rho_mean": owned_low["rho_own_mean"]},
        "rho_high": {"centre": BOUNDARY_RHO_HIGH,
                     "matched_world": WORLD_OWNED,
                     "half_width": owned_high["rho_half_width_mean"],
                     "planted_rho": RHO_TRUE_TARGET,
                     "realized_rho_mean": owned_high["rho_own_mean"]},
    }


def rho_region_edges(regions: dict[str, Any]) -> tuple[float, float,
                                                       float, float]:
    lo_w = regions["rho_low"]["half_width"]
    hi_w = regions["rho_high"]["half_width"]
    return (BOUNDARY_RHO_LOW - lo_w, BOUNDARY_RHO_LOW + lo_w,
            BOUNDARY_RHO_HIGH - hi_w, BOUNDARY_RHO_HIGH + hi_w)


def ladder_coherence(regions: dict[str, Any]) -> dict[str, Any]:
    """#91: is the PRICED ownership ladder still a ladder?

    Three conditions, each reported: the two regions are DISJOINT; the
    interior cell between them (WEAKLY_OWNED) is NON-EMPTY; and the region
    around 0.15 does not reach down through zero (which would leave the
    point-based NOT_OWNED side empty).  If any fails, the classification
    COLLAPSES EXPLICITLY to the binary OWNED (CI > 0) / NOT_OWNED — the
    coarser partition, stated, never a silent empty cell.
    """

    low_lo, low_hi, high_lo, high_hi = rho_region_edges(regions)
    disjoint = bool(low_hi < high_lo)
    weak_nonempty = disjoint
    below_nonempty = bool(low_lo > 0.0)
    widths_ok = bool(regions["rho_low"]["half_width"] > 0
                     and regions["rho_high"]["half_width"] > 0
                     and np.isfinite(regions["rho_low"]["half_width"])
                     and np.isfinite(regions["rho_high"]["half_width"]))
    coherent = disjoint and weak_nonempty and below_nonempty and widths_ok
    failed = [name for name, ok in (("regions_disjoint", disjoint),
                                    ("weakly_owned_nonempty", weak_nonempty),
                                    ("not_owned_side_nonempty",
                                     below_nonempty),
                                    ("half_widths_positive", widths_ok))
              if not ok]
    return {
        "edges": [low_lo, low_hi, high_lo, high_hi],
        "regions_disjoint": disjoint,
        "weakly_owned_nonempty": weak_nonempty,
        "not_owned_side_nonempty": below_nonempty,
        "half_widths_positive": widths_ok,
        "coherent": coherent,
        "failed_conditions": failed,
        "status": "COHERENT" if coherent else "COLLAPSED_TO_BINARY",
        "classification": "LADDER" if coherent else "BINARY",
        "note": ("the priced regions are disjoint with non-empty interior "
                 "cells, so the registered ownership ladder resolves at this "
                 "design's own precision"
                 if coherent else
                 "the priced regions do not form a ladder ("
                 + ", ".join(failed) + "), so the ownership classification "
                 "COLLAPSES EXPLICITLY to the binary OWNED (CI > 0) / "
                 "NOT_OWNED for this relation"),
    }


def rho_cell(rho: float, ci: Sequence[float], regions: dict[str, Any],
             ladder: dict[str, Any]) -> str:
    """NULL-first, then either the priced ladder or the #91 binary."""

    covers_zero = bool(ci[0] <= 0.0 <= ci[1])
    if not ladder["coherent"]:
        return CELL_OWNED_BINARY if ci[0] > 0.0 else CELL_NOT_OWNED_BINARY
    low_lo, low_hi, high_lo, high_hi = rho_region_edges(regions)
    if covers_zero or rho < low_lo:
        return CELL_NOT_OWNED
    if rho <= low_hi:
        return CELL_AT_LOW
    if rho < high_lo:
        return CELL_WEAK
    if rho <= high_hi:
        return CELL_AT_HIGH
    return CELL_STRONG


def relation_gate(sk: RelationSkeleton, *, b_perm: int, b_boot: int,
                  seed: int, log: RunLog, routes_ownership: bool
                  ) -> dict[str, Any]:
    """The registered Part 0 battery for ONE relation's realized skeleton.

    Wholly synthetic y on the relation's own x sequences, halves and cell
    sizes.  ROUTING: the ERGODIC world's zero reading, the NON-ERGODIC world's
    DERIVED Delta recovery (with the #90 ceiling), the NULL world's four
    zeros, #85b bootstrap-zero on the null world, and the #88a pricing.  The
    OWNED-slopes recovery ROUTES ONCE, on R2's skeleton (the level-3 machinery
    is shared across relations and the registration says so); on the other
    relations the two owned worlds still run, because #88a prices each
    relation's rho regions from ITS OWN matched worlds, and they annotate.
    """

    mapping_high = ownership_slope_target(sk, RHO_TRUE_TARGET)
    mapping_low = ownership_slope_target(sk, RHO_PRICE_LOW)
    log.event("gate_mapping", relation=sk.relation.key,
              **{k: v for k, v in mapping_high.items() if k != "formula"})

    ergodic = run_world(sk, WORLD_ERGODIC, mapping_high, seed + 1000,
                        b_perm=0, b_boot=b_boot, with_ownership=False, log=log)
    nonerg = run_world(sk, WORLD_NONERGODIC, mapping_high, seed + 2000,
                       b_perm=0, b_boot=b_boot, with_ownership=False, log=log)
    null = run_world(sk, WORLD_NULL, mapping_high, seed + 3000,
                     b_perm=b_perm, b_boot=b_boot, with_ownership=True,
                     log=log)
    owned = run_world(sk, WORLD_OWNED, mapping_high, seed + 4000,
                      b_perm=b_perm if routes_ownership else 0, b_boot=b_boot,
                      with_ownership=True, log=log)
    owned_low = run_world(sk, WORLD_OWNED_LOW, mapping_low, seed + 5000,
                          b_perm=0, b_boot=b_boot, with_ownership=True,
                          log=log)

    regions = price_regions(sk.relation.key, null, owned_low, owned)
    ladder = ladder_coherence(regions)

    tol_erg = max(TOL_FLOOR_DELTA, TOL_SD_MULT * ergodic["delta_erg_sd"])
    tol_non = max(TOL_FLOOR_DELTA, TOL_SD_MULT * nonerg["delta_erg_sd"])
    tol_rho = max(TOL_FLOOR_RHO, TOL_SD_MULT * owned["rho_own_sd"])
    gap_non = nonerg["delta_erg_mean"] - GAMMA_PLANT
    gap_rho = owned["rho_own_mean"] - RHO_TRUE_TARGET

    ceil_delta = ceiling_clause("Delta recovery (non-ergodic world)",
                                nonerg["delta_erg_sd"], TOL_FLOOR_DELTA)
    ceil_rho = ceiling_clause("rho_own recovery (owned-slopes world)",
                              owned["rho_own_sd"], TOL_FLOOR_RHO)

    routing = [
        {"id": "i",
         "clause": ("ERGODIC world (one beta for all, person intercepts "
                    "UNCORRELATED with xbar_u): Delta_erg must read 0"),
         "observed": (f"mean Delta {ergodic['delta_erg_mean']:+.6f} over "
                      f"{N_SYNTH_REPLICATES} replicates (sd "
                      f"{ergodic['delta_erg_sd']:.6f}); "
                      f"{ergodic['delta_ci_cover_count']}/"
                      f"{N_SYNTH_REPLICATES} bootstrap CIs cover 0"),
         "required": (f"abs(mean) <= max({TOL_FLOOR_DELTA}, 3 x rep sd) = "
                      f"{tol_erg:.6f} AND >= {ERGODIC_COVER_FLOOR}/"
                      f"{N_SYNTH_REPLICATES} CIs cover 0"),
         "status": "PASS" if (abs(ergodic["delta_erg_mean"]) <= tol_erg
                              and ergodic["delta_ci_cover_count"]
                              >= ERGODIC_COVER_FLOOR) else "FAIL"},
        {"id": "ii",
         "clause": ("NON-ERGODIC world, a_u = gamma * xbar_u + noise: the "
                    "DERIVED Delta is exactly gamma (within-centering "
                    "annihilates a_u so level 2 reads beta, while level 1 "
                    f"reads beta + gamma), planted gamma = {GAMMA_PLANT:+.4f}"),
         "observed": (f"mean Delta {nonerg['delta_erg_mean']:+.6f} (sd "
                      f"{nonerg['delta_erg_sd']:.6f}), gap {gap_non:+.6f} = "
                      f"{abs(gap_non) / max(nonerg['delta_erg_sd'], 1e-12):.2f}"
                      " replicate sd"),
         "required": (f"abs(gap) <= max({TOL_FLOOR_DELTA}, 3 x rep sd) = "
                      f"{tol_non:.6f}"),
         "status": "PASS" if abs(gap_non) <= tol_non else "FAIL"},
        {"id": "ii-ceiling",
         "clause": ("#90 PRECISION CEILING on clause (ii): the replicate "
                    "spread of the recovery must itself be inside the "
                    f"registered tolerance floor ({TOL_FLOOR_DELTA} in Delta "
                    "units), else the clause certifies nothing"),
         "observed": (f"replicate sd {ceil_delta['replicate_sd']:.6f} against "
                      f"the ceiling {TOL_FLOOR_DELTA}"),
         "required": "rep sd <= the tolerance floor (else UNINFORMATIVE)",
         "status": "PASS" if ceil_delta["informative"] else "UNINFORMATIVE"},
        {"id": "iii",
         "clause": ("NULL world (beta = 0 everywhere, intercepts unrelated to "
                    "x): ALL FOUR objects must read 0 within their own band "
                    "or interval"),
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
                      "of the five coverage counts"),
         "status": "PASS" if min(
             null["between_ci_cover_zero_count"],
             null["within_ci_cover_zero_count"],
             null["delta_ci_cover_count"],
             null["rho_ci_cover_zero_count"],
             null["rho_inside_band_count"]) >= ERGODIC_COVER_FLOOR
         else "FAIL"},
        {"id": "iv",
         "clause": ("#85b bootstrap-zero on the NULL world: every interval "
                    "must cover 0 AND cover its own point"),
         "observed": (
             f"Delta CIs covering 0: {null['delta_ci_cover_count']}/"
             f"{N_SYNTH_REPLICATES}; rho_own CIs covering their own point: "
             f"{null['rho_ci_cover_point_count']}/{N_SYNTH_REPLICATES}"),
         "required": (f">= {ERGODIC_COVER_FLOOR}/{N_SYNTH_REPLICATES} on both "
                      "counts"),
         "status": "PASS" if min(
             null["delta_ci_cover_count"],
             null["rho_ci_cover_point_count"]) >= ERGODIC_COVER_FLOOR
         else "FAIL"},
        {"id": "v",
         "clause": ("#88a REGION PRICING executed in-leg on THIS relation's "
                    "skeleton: the boundary half-widths for both routed "
                    "objects are the realized bootstrap half-widths on the "
                    "matched planted worlds, pinned BEFORE any real number"),
         "observed": (
             f"Delta region +-{regions['delta']['half_width']:.6f} (null "
             f"world); rho region at 0.15 "
             f"+-{regions['rho_low']['half_width']:.4f}; at 0.50 "
             f"+-{regions['rho_high']['half_width']:.4f}; pinned "
             f"{regions['priced_utc']}"),
         "required": ("all three finite and positive, artifact written before "
                      "the first real number"),
         "status": "PASS" if all(
             np.isfinite(regions[k]["half_width"])
             and regions[k]["half_width"] > 0
             for k in ("delta", "rho_low", "rho_high")) else "FAIL"},
        {"id": "vi",
         "clause": ("#91 LADDER COHERENCE on the priced regions: disjoint "
                    "regions with non-empty interior cells, ELSE the "
                    "ownership classification collapses EXPLICITLY to the "
                    "binary"),
         "observed": (
             f"edges [{ladder['edges'][0]:.4f}, "
             f"{ladder['edges'][1]:.4f}] around 0.15 and "
             f"[{ladder['edges'][2]:.4f}, {ladder['edges'][3]:.4f}] around "
             f"0.50 -> {ladder['status']}"),
         "required": ("the check is ASSERTED and its outcome RECORDED; a "
                      "collapse is a legitimate outcome and never stops the "
                      "leg (the coarser partition is stated)"),
         "status": "PASS"},
    ]

    if routes_ownership:
        routing.insert(3, {
            "id": "iii-owned",
            "clause": ("OWNED-SLOPES world at the #76 operating point (the "
                       "across-author slope dispersion DERIVED so the true "
                       "ownership correlation is 0.50), FLOORED estimator: "
                       "rho_own recovery — the registration routes this "
                       "clause ONCE, on R2's skeleton"),
            "observed": (f"mean rho_own {owned['rho_own_mean']:+.4f} (sd "
                         f"{owned['rho_own_sd']:.4f}), gap {gap_rho:+.4f} = "
                         f"{abs(gap_rho) / max(owned['rho_own_sd'], 1e-12):.2f}"
                         " replicate sd"),
            "required": (f"abs(gap) <= max({TOL_FLOOR_RHO}, 3 x rep sd) = "
                         f"{tol_rho:.4f}"),
            "status": "PASS" if abs(gap_rho) <= tol_rho else "FAIL"})
        routing.insert(4, {
            "id": "iii-owned-ceiling",
            "clause": ("#90 PRECISION CEILING on the ownership recovery — "
                       "the clause X4's defect #90 was purchased from: it "
                       "passed there on a replicate spread of 0.165"),
            "observed": (f"replicate sd {ceil_rho['replicate_sd']:.4f} against "
                         f"the ceiling {TOL_FLOOR_RHO}"),
            "required": "rep sd <= the tolerance floor (else UNINFORMATIVE)",
            "status": "PASS" if ceil_rho["informative"] else "UNINFORMATIVE"})

    descriptive = [
        {"id": "D1",
         "clause": ("LEVEL VALUE recovery, ergodic world (both levels must "
                    f"read the planted beta = {BETA_PLANT:+.2f})"),
         "observed": (f"beta_between {ergodic['beta_between_mean']:+.4f}, "
                      f"beta_within {ergodic['beta_within_mean']:+.4f}"),
         "required": "annotate only, never stops", "status": "ANNOTATED"},
        {"id": "D2",
         "clause": ("LEVEL VALUE recovery, non-ergodic world (beta_within = "
                    f"{BETA_PLANT:+.2f}, beta_between = "
                    f"{BETA_PLANT + GAMMA_PLANT:+.2f})"),
         "observed": (f"beta_between {nonerg['beta_between_mean']:+.4f}, "
                      f"beta_within {nonerg['beta_within_mean']:+.4f}"),
         "required": "annotate only, never stops", "status": "ANNOTATED"},
        {"id": "D3",
         "clause": ("the #89 den distribution the ownership mapping rides on "
                    "— with the floor in the POOL, A_h = sigma^2 E[1/den] can "
                    "no longer be dominated by a near-degenerate half"),
         "observed": (
             f"A_early {mapping_high['A_early']:.6g} (median-based "
             f"{mapping_high['A_early_median_based']:.6g}), A_late "
             f"{mapping_high['A_late']:.6g} (median-based "
             f"{mapping_high['A_late_median_based']:.6g}); min den "
             f"{sk.census()['min_den_early']:.4g} / "
             f"{sk.census()['min_den_late']:.4g}, median den "
             f"{sk.census()['median_den_early']:.4g} / "
             f"{sk.census()['median_den_late']:.4g}; V = "
             f"{mapping_high['V_slope_variance']:.4g}, sd(beta_u) = "
             f"{mapping_high['sd_beta']:.4g}"),
         "required": "annotate only, never stops", "status": "ANNOTATED"},
        {"id": "D4",
         "clause": ("OWNERSHIP RECOVERY on this relation's skeleton (ROUTES "
                    "only on R2; here it prices the rho regions and "
                    "annotates)"),
         "observed": (f"planted 0.50 -> {owned['rho_own_mean']:+.4f} (sd "
                      f"{owned['rho_own_sd']:.4f}, half-width "
                      f"{owned['rho_half_width_mean']:.4f}); planted 0.15 -> "
                      f"{owned_low['rho_own_mean']:+.4f} (sd "
                      f"{owned_low['rho_own_sd']:.4f}, half-width "
                      f"{owned_low['rho_half_width_mean']:.4f})"),
         "required": "annotate only, never stops", "status": "ANNOTATED"},
    ]

    status = "PASS" if all(c["status"] == "PASS" for c in routing) else "FAIL"
    return {
        "relation": sk.relation.key,
        "status": status,
        "routes_ownership": routes_ownership,
        "routing": routing,
        "descriptive": descriptive,
        "ceilings": {"delta": ceil_delta, "rho": ceil_rho},
        "mapping": mapping_high,
        "mapping_low": mapping_low,
        "regions": regions,
        "ladder": ladder,
        "tolerances": {"ergodic_delta": tol_erg, "nonergodic_delta": tol_non,
                       "owned_rho": tol_rho,
                       "delta_floor": TOL_FLOOR_DELTA,
                       "rho_floor": TOL_FLOOR_RHO},
        "worlds": {WORLD_ERGODIC: ergodic, WORLD_NONERGODIC: nonerg,
                   WORLD_NULL: null, WORLD_OWNED: owned,
                   WORLD_OWNED_LOW: owned_low},
        "skeleton": sk.census(),
    }


def imported_r1_gate() -> dict[str, Any]:
    """R1 inherits X4's PASSED gate; its rho regions are X4's FLOORED pricing.

    X4 routed its ownership pricing on the UNFLOORED level-3 object and the
    ladder collapsed (+-0.3827 at 0.15, +-0.1837 at 0.50).  X5's estimator is
    the floored one throughout, so R1's regions are X4's own committed FLOORED
    annotation worlds — the matched worlds for the estimator actually used.
    """

    part0 = json.loads((X4_RESULTS / "part0_gate.json").read_text("utf-8"))
    x4_regions = part0["regions"]
    ann = x4_regions["annotation_precision_floored"]
    regions = {
        "relation": "R1",
        "priced_utc": x4_regions["priced_utc"],
        "source": ("IMPORTED from X4's committed region pricing (commit "
                   "8ff1f7f).  The Delta half-width is X4's routed null-world "
                   "width; the rho half-widths are X4's FLOORED annotation "
                   "worlds, which are the worlds matched to the estimator X5 "
                   "uses (den >= 1)."),
        "delta": {"centre": BOUNDARY_DELTA_CENTRE,
                  "matched_world": WORLD_NULL,
                  "half_width": x4_regions["delta"]["half_width"]},
        "rho_low": {"centre": BOUNDARY_RHO_LOW,
                    "matched_world": "owned_slopes_precision_floor_at_0.15",
                    "half_width": ann["rho_low_half_width"],
                    "planted_rho": RHO_PRICE_LOW,
                    "realized_rho_mean": ann["rho_low_realized_rho_mean"]},
        "rho_high": {"centre": BOUNDARY_RHO_HIGH,
                     "matched_world": "owned_slopes_precision_floor",
                     "half_width": ann["rho_high_half_width"],
                     "planted_rho": RHO_TRUE_TARGET,
                     "realized_rho_mean": ann["rho_high_realized_rho_mean"]},
    }
    ladder = ladder_coherence(regions)
    return {
        "relation": "R1",
        "status": part0["status"],
        "routes_ownership": False,
        "imported": True,
        "routing": [{"id": "X4", "clause": ("R1 inherits X4's Part 0 gate "
                                            "(6 ROUTING clauses, all PASS) "
                                            "unchanged"),
                     "observed": (f"X4 gate status {part0['status']}; "
                                  f"priced {x4_regions['priced_utc']}"),
                     "required": "the inherited gate PASSED",
                     "status": part0["status"]}],
        "descriptive": [
            {"id": "D1", "clause": ("X4's ergodic-world honesty check (the "
                                    "instrument does not manufacture "
                                    "non-ergodicity)"),
             "observed": (
                 f"mean Delta "
                 f"{part0['worlds'][WORLD_ERGODIC]['delta_erg_mean']:+.6f}, "
                 f"{part0['worlds'][WORLD_ERGODIC]['delta_ci_cover_count']}/"
                 f"{N_SYNTH_REPLICATES} CIs cover 0"),
             "required": "annotate only", "status": "ANNOTATED"},
            {"id": "D2", "clause": ("X4's FLOORED ownership recovery (D6 "
                                    "there): the worlds matched to X5's "
                                    "estimator"),
             "observed": (
                 f"planted 0.50 -> "
                 f"{ann['rho_high_realized_rho_mean']:+.4f} (half-width "
                 f"{ann['rho_high_half_width']:.4f}); planted 0.15 -> "
                 f"{ann['rho_low_realized_rho_mean']:+.4f} (half-width "
                 f"{ann['rho_low_half_width']:.4f})"),
             "required": "annotate only", "status": "ANNOTATED"}],
        "ceilings": {},
        "regions": regions,
        "ladder": ladder,
        "tolerances": {},
        "worlds": {},
    }


# ---------------------------------------------------------------------------
# Stage 4 — the real arms
# ---------------------------------------------------------------------------


def analyse_relation_arm(sk: RelationSkeleton, mom: dict[str, np.ndarray], *,
                         b_perm: int, b_boot: int, seed_perm: int,
                         seed_boot: int, with_levels: bool = True
                         ) -> dict[str, Any]:
    """All three levels plus the verdict statistic for one (relation, cohort).

    The level-3 estimator is the FLOORED per-author slope: the pool's #89
    clause guarantees den >= 1 in both halves for every author scored here, so
    no cell is near-degenerate and no author is silently dropped.

    ``with_levels=False`` computes level 3 ONLY.  R1 uses it: the registration
    says its levels 1-2 are IMPORTED from X4 and not recomputed, so they are
    not computed here at all rather than computed and discarded.
    """

    levels = three_levels(mom) if with_levels else {}
    beta_e, beta_l, ok = per_cell_slopes(sk, mom)
    if not bool(ok.all()):                        # pragma: no cover - #89
        raise RuntimeError("the #89 floor must leave every pool cell "
                           "estimable; a NaN slope survived the pool")
    rho = float(rowwise_pearson(beta_e[ok], beta_l[ok])[0])
    out = {
        "relation": sk.relation.key,
        "cohort": sk.key,
        "label": sk.label,
        "census": sk.census(),
        **levels,
        "rho_own": rho,
        "ownership_null": ownership_null(beta_e, beta_l, ok, b_perm,
                                         seed_perm + 101),
        "ownership_boot": cluster_bootstrap_pairs(beta_e, beta_l, ok, b_boot,
                                                  seed_boot + 501),
        "dispersion": dispersion(beta_e, beta_l, ok),
        "authors_scored_at_level_3": int(ok.sum()),
    }
    band = out["ownership_null"]["band"]
    out["ownership_detected"] = bool(rho < band[0] or rho > band[1])
    out["rho_ci"] = out["ownership_boot"]["ci"]
    out["rho_ci_covers_zero"] = bool(out["rho_ci"][0] <= 0.0
                                     <= out["rho_ci"][1])
    if not with_levels:
        return out
    out["boot"] = paired_level_bootstrap(mom, b_boot, seed_boot)
    ci = out["boot"]["delta_ci"]
    out["delta_ci_covers_zero"] = bool(ci[0] <= 0.0 <= ci[1])
    out["beta_between_detected"] = not (
        out["boot"]["beta_between_ci"][0] <= 0.0
        <= out["boot"]["beta_between_ci"][1])
    out["beta_within_detected"] = not (
        out["boot"]["beta_within_ci"][0] <= 0.0
        <= out["boot"]["beta_within_ci"][1])
    return out


def import_r1_levels(cohort: str) -> dict[str, Any]:
    """R1's levels 1-2 and Delta, IMPORTED from X4's committed artifacts.

    Bit-checked, not recomputed: the registration says so, and recomputing
    them would silently re-decide X4's adjudicated verdict.  The X4 arm key
    for the disjoint cohort is ``primary``.
    """

    arm_key = "primary" if cohort == "disjoint" else "big5"
    cells = json.loads((X4_RESULTS / "cells.json").read_text("utf-8"))
    arms = json.loads((X4_RESULTS / "arms.json").read_text("utf-8"))
    cell = cells[arm_key]
    arm = arms[arm_key]
    return {
        "relation": "R1",
        "cohort": cohort,
        "label": f"IMPORTED from X4 ({arm['label']})",
        "imported": True,
        "x4_arm": arm_key,
        "beta_between": cell["beta_between"],
        "beta_within": cell["beta_within"],
        "beta_within_early": arm["beta_within_early"],
        "beta_within_late": arm["beta_within_late"],
        "r_between": arm["r_between"],
        "delta_erg": cell["delta_erg"],
        "boot": {"b": arm["boot"]["b"],
                 "delta_ci": cell["delta_ci"],
                 "beta_between_ci": arm["boot"]["beta_between_ci"],
                 "beta_within_ci": arm["boot"]["beta_within_ci"],
                 "delta_boot_sd": arm["boot"]["delta_boot_sd"]},
        "delta_ci_covers_zero": cell["delta_ci_covers_zero"],
        "beta_between_detected": arm["beta_between_detected"],
        "beta_within_detected": arm["beta_within_detected"],
        "delta_cell_x4": cell["delta_cell"],
        "x4_authors": arm["census"]["authors"],
        "x4_events": arm["census"]["events"],
        "x4_floored_rho_own": arm["precision_floor"]["rho_own"],
        "x4_floored_rho_ci": arm["precision_floor"]["boot"]["ci"],
        "x4_floored_authors": arm["precision_floor"]["authors"],
    }


def floor_effect(gates: dict[str, Any], arms: dict[str, Any]
                 ) -> dict[str, Any]:
    """What the #89 floor bought, in X4's own committed numbers.

    X4 measured the SAME relation R1 with the same estimator MINUS the floor
    and recorded three pathologies; this leg's artifacts say what each of them
    reads once the floor is a pool clause.  Every number on both sides comes
    from an artifact.
    """

    x4_arms = json.loads((X4_RESULTS / "arms.json").read_text("utf-8"))
    x4_part0 = json.loads((X4_RESULTS / "part0_gate.json").read_text("utf-8"))
    x4_regions = x4_part0["regions"]
    ceilings = [g["ceilings"]["rho"]["replicate_sd"]
                for g in gates.values() if g.get("ceilings")]
    rho_widths = [g["regions"]["rho_high"]["half_width"]
                  for g in gates.values()]
    return {
        "var_beta_R1_disjoint": {
            "x4_unfloored": x4_arms["primary"]["dispersion"][
                "var_true_cross_half"],
            "x5_floored": arms["R1:disjoint"]["dispersion"][
                "var_true_cross_half"],
            "note": ("X4's cross-half Var(beta) came out NEGATIVE on the "
                     "registered (unfloored) object; with the floor in the "
                     "pool it is positive and sd_true is defined")},
        "owned_world_rho_replicate_sd": {
            "x4_unfloored": x4_part0["worlds"]["owned_slopes"]["rho_own_sd"],
            "x5_floored_min": min(ceilings) if ceilings else None,
            "x5_floored_max": max(ceilings) if ceilings else None,
            "note": ("the spread that made X4's clause (iii) UNINFORMATIVE "
                     "under #90; here every ceiling clause is INFORMATIVE")},
        "priced_rho_half_width_at_0.50": {
            "x4_unfloored": x4_regions["rho_high"]["half_width"],
            "x4_floored_annotation": x4_regions[
                "annotation_precision_floored"]["rho_high_half_width"],
            "x5_min": min(rho_widths), "x5_max": max(rho_widths),
            "note": ("X4's routed pricing overlapped the 0.15 region and "
                     "emptied WEAKLY_OWNED (#91); every relation here prices "
                     "a COHERENT ladder")},
        "ladders_coherent": sum(1 for g in gates.values()
                                if g["ladder"]["coherent"]),
        "ladders_total": len(gates),
    }


def r1_import_check(recomputed: dict[str, Any], imported: dict[str, Any]
                    ) -> dict[str, Any]:
    """The R1 IMPORT BIT-CHECK: this leg's fresh cache must reproduce X4's
    committed floored ownership point EXACTLY (same events, same order, same
    two-pass path), which is the strongest available proof that the atlas and
    X4 are measuring the same corpus."""

    got = recomputed["rho_own"]
    want = imported["x4_floored_rho_own"]
    delta = abs(got - want)
    return {
        "object": "R1 floored rho_own recomputed on X5's fresh cache",
        "x4_committed": want,
        "x5_recomputed": got,
        "abs_difference": delta,
        "tolerance": X4_IMPORT_TOL,
        "authors_x4": imported["x4_floored_authors"],
        "authors_x5": recomputed["census"]["authors"],
        "authors_match": bool(recomputed["census"]["authors"]
                              == imported["x4_floored_authors"]),
        "status": "PASS" if (delta <= X4_IMPORT_TOL
                             and recomputed["census"]["authors"]
                             == imported["x4_floored_authors"]) else "FAIL",
    }


# ---------------------------------------------------------------------------
# Stage 5 — cells, the atlas summary, leans
# ---------------------------------------------------------------------------


def classify(result: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    """One atlas cell: the Delta cell and the ownership cell (or the #91
    binary), each with its priced-region straddle report."""

    regions = gate["regions"]
    ladder = gate["ladder"]
    delta_w = regions["delta"]["half_width"]
    delta_edges = (BOUNDARY_DELTA_CENTRE - delta_w,
                   BOUNDARY_DELTA_CENTRE + delta_w)
    d_ci = result["boot"]["delta_ci"]
    d_straddle = edges_straddled(d_ci, delta_edges)
    out = {
        "relation": result["relation"],
        "cohort": result["cohort"],
        "label": result["label"],
        "imported": bool(result.get("imported", False)),
        "beta_between": result["beta_between"],
        "beta_within": result["beta_within"],
        "delta_erg": result["delta_erg"],
        "delta_ci": d_ci,
        "delta_ci_covers_zero": result["delta_ci_covers_zero"],
        "delta_cell": delta_cell(result),
        "delta_inside_priced_region": bool(abs(result["delta_erg"])
                                           <= delta_w),
        "delta_region_edges_straddled": d_straddle,
        "delta_is_straddle": bool(d_straddle),
    }
    if "rho_own" in result:
        r_ci = result["rho_ci"]
        r_straddle = (edges_straddled(r_ci, rho_region_edges(regions))
                      if ladder["coherent"] else [])
        out.update({
            "rho_own": result["rho_own"],
            "rho_ci": r_ci,
            "rho_band": result["ownership_null"]["band"],
            "rho_ci_covers_zero": result["rho_ci_covers_zero"],
            "rho_cell": rho_cell(result["rho_own"], r_ci, regions, ladder),
            "ownership_classification": ladder["classification"],
            "ladder_status": ladder["status"],
            "rho_region_edges_straddled": r_straddle,
            "rho_is_straddle": bool(r_straddle),
            "authors": result["census"]["authors"],
            "usable_events": result["census"]["usable_events"],
        })
    return out


def atlas_summary(cells: dict[str, dict[str, Any]], cohort: str
                  ) -> dict[str, Any]:
    """The registered atlas ROUTES, NULL-first (#55).

    Route 2 is refined to "all five in the SAME nonergodic cell": five
    relations spread over two DIFFERENT nonergodic cells is a map WITH
    structure, which is what route 3 names.  The literal predicate ("all five
    nonergodic", whatever the cells) is recorded alongside so the reader can
    see the refinement rather than infer it.  Recorded implementation choice,
    in X4's precedent of the fourth Delta cell.
    """

    order = [spec.key for spec in RELATIONS]
    by_relation = {key: cells[f"{key}:{cohort}"]["delta_cell"]
                   for key in order}
    distinct = sorted(set(by_relation.values()))
    all_indist = all(c == CELL_INDIST for c in by_relation.values())
    all_nonergodic = all(c in NONERGODIC_CELLS for c in by_relation.values())
    if all_indist:
        route = ATLAS_UNIFORM_ERGODIC
    elif all_nonergodic and len(distinct) == 1:
        route = ATLAS_UNIFORM_NONERGODIC
    else:
        route = ATLAS_HETEROGENEOUS
    return {
        "cohort": cohort,
        "route": route,
        "cells_by_relation": by_relation,
        "distinct_cells": distinct,
        "n_distinct_cells": len(distinct),
        "all_levels_indistinguishable": all_indist,
        "all_nonergodic_literal": all_nonergodic,
        "all_in_one_nonergodic_cell": bool(all_nonergodic
                                           and len(distinct) == 1),
    }


def plateau_prediction(cells: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The registered PREDICTION: the ~0.27 level-3 plateau appears for at
    least two of the four NEW relations on the disjoint cohort."""

    lo, hi = PLATEAU_BAND
    rows = []
    for key in NEW_RELATIONS:
        cell = cells[f"{key}:disjoint"]
        rho = cell["rho_own"]
        ci = cell["rho_ci"]
        rows.append({
            "relation": key,
            "rho_own": rho,
            "rho_ci": ci,
            "point_in_band": bool(lo <= rho <= hi),
            "ci_overlaps_band": bool(ci[0] <= hi and ci[1] >= lo),
        })
    n_point = sum(1 for r in rows if r["point_in_band"])
    n_ci = sum(1 for r in rows if r["ci_overlaps_band"])
    return {
        "band": list(PLATEAU_BAND),
        "band_provenance": ("bridge section 7: X1c response-profile "
                            "persistence 0.279, X2 rhythm ownership 0.259, "
                            "X4 floored slope ownership 0.277"),
        "criterion": (f"the point estimate lies in [{PLATEAU_BAND[0]}, "
                      f"{PLATEAU_BAND[1]}] for >= {PLATEAU_MIN_RELATIONS} of "
                      "the four new relations, disjoint cohort"),
        "rows": rows,
        "n_relations_in_band": n_point,
        "n_relations_ci_overlapping": n_ci,
        "held": bool(n_point >= PLATEAU_MIN_RELATIONS),
        "status": "HELD" if n_point >= PLATEAU_MIN_RELATIONS else "BROKEN",
    }


def evaluate_leans(cells: dict[str, dict[str, Any]], summary: dict[str, Any],
                   plateau: dict[str, Any]) -> list[dict[str, Any]]:
    """The registered leans, scored against the artifacts."""

    def cell(key: str) -> dict[str, Any]:
        return cells[f"{key}:disjoint"]

    r2, r3, r4, r5 = cell("R2"), cell("R3"), cell("R4"), cell("R5")
    rows = [
        {"lean": "R2 (gap x volume): beta_within > 0 — rest precedes longer "
                 "comments",
         "registered": "directional, weakly held",
         "observed": f"{r2['beta_within']:+.6f}",
         "held": bool(r2["beta_within"] > 0.0)},
        {"lean": "R2: Delta cell NONERGODIC_SAME_SIGN",
         "registered": CELL_SAME_SIGN,
         "observed": r2["delta_cell"],
         "held": bool(r2["delta_cell"] == CELL_SAME_SIGN)},
        {"lean": "R3 (volume x score): both slopes positive and small",
         "registered": "both positive",
         "observed": (f"beta_between {r3['beta_between']:+.6f}, beta_within "
                      f"{r3['beta_within']:+.6f}"),
         "held": bool(r3["beta_between"] > 0.0 and r3["beta_within"] > 0.0)},
        {"lean": "R3: Delta cell SAME_SIGN or LEVELS_INDISTINGUISHABLE",
         "registered": f"{CELL_SAME_SIGN} | {CELL_INDIST}",
         "observed": r3["delta_cell"],
         "held": bool(r3["delta_cell"] in (CELL_SAME_SIGN, CELL_INDIST))},
        {"lean": "R4 (commonness x score): beta_within > 0 — bigger venue, "
                 "more eyes, more score",
         "registered": "directional, weakly held",
         "observed": f"{r4['beta_within']:+.6f}",
         "held": bool(r4["beta_within"] > 0.0)},
        {"lean": "R4: Delta cell NONERGODIC_SAME_SIGN",
         "registered": CELL_SAME_SIGN,
         "observed": r4["delta_cell"],
         "held": bool(r4["delta_cell"] == CELL_SAME_SIGN)},
        {"lean": "R5 (commonness x gap): REGISTERED UNLEANED (no defensible "
                 "prior)",
         "registered": "unleaned",
         "observed": (f"beta_between {r5['beta_between']:+.6f}, beta_within "
                      f"{r5['beta_within']:+.6f}, cell {r5['delta_cell']}"),
         "held": None},
        {"lean": "the atlas summary is ATLAS_HETEROGENEOUS",
         "registered": ATLAS_HETEROGENEOUS,
         "observed": summary["route"],
         "held": bool(summary["route"] == ATLAS_HETEROGENEOUS)},
        {"lean": ("the ~0.27 level-3 plateau appears for >= 2 of the four new "
                  "relations (disjoint) — the plateau's first PREDICTION"),
         "registered": (f">= {PLATEAU_MIN_RELATIONS} points in "
                        f"[{PLATEAU_BAND[0]}, {PLATEAU_BAND[1]}]"),
         "observed": (f"{plateau['n_relations_in_band']} of 4 in band; "
                      + ", ".join(f"{r['relation']} {r['rho_own']:+.4f}"
                                  for r in plateau["rows"])),
         "held": plateau["held"]},
    ]
    for row in rows:
        row["status"] = ("N/A — REGISTERED UNLEANED" if row["held"] is None
                         else ("HELD" if row["held"] else "BROKEN"))
    return rows


def flags_73(cells: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Cohort divergences carry #73; the disjoint cohort always routes."""

    flags = []
    for spec in RELATIONS:
        primary = cells[f"{spec.key}:disjoint"]
        replication = cells[f"{spec.key}:big5"]
        if replication["delta_cell"] != primary["delta_cell"]:
            flags.append({"relation": spec.key, "object": "Delta_erg",
                          "primary_cell": primary["delta_cell"],
                          "big5_cell": replication["delta_cell"],
                          "primary": primary["delta_erg"],
                          "primary_ci": primary["delta_ci"],
                          "big5": replication["delta_erg"],
                          "big5_ci": replication["delta_ci"],
                          "note": "#73 divergence; the disjoint cohort routes"})
        if replication.get("rho_cell") != primary.get("rho_cell"):
            flags.append({"relation": spec.key, "object": "rho_own",
                          "primary_cell": primary.get("rho_cell"),
                          "big5_cell": replication.get("rho_cell"),
                          "primary": primary.get("rho_own"),
                          "primary_ci": primary.get("rho_ci"),
                          "big5": replication.get("rho_own"),
                          "big5_ci": replication.get("rho_ci"),
                          "note": "#73 divergence; the disjoint cohort routes"})
        for cell in (primary, replication):
            if cell["delta_is_straddle"]:
                flags.append({"relation": spec.key, "object": "Delta_erg",
                              "cohort": cell["cohort"],
                              "note": ("#87 straddle: the CI crosses the "
                                       "priced region edge(s) "
                                       + ", ".join(
                                           cell["delta_region_edges_straddled"])
                                       )})
            if cell.get("rho_is_straddle"):
                flags.append({"relation": spec.key, "object": "rho_own",
                              "cohort": cell["cohort"],
                              "note": ("#87 straddle: the CI crosses the "
                                       "priced region edge(s) "
                                       + ", ".join(
                                           cell["rho_region_edges_straddled"]))
                              })
    return flags


def build_verdict(gates: dict[str, Any], summary: dict[str, Any],
                  cells: dict[str, dict[str, Any]]) -> dict[str, Any]:
    failed = [key for key, gate in gates.items() if gate["status"] != "PASS"]
    if failed:
        return {"cell": ATLAS_A1_STOP, "routes_on": "Part 0 gate",
                "failed_relations": failed,
                "note": ("A1 stop: a ROUTING clause failed on a realized "
                         "skeleton; NO corpus estimand value is licensed.")}
    return {
        "cell": summary["route"],
        "routes_on": "the five Delta cells, disjoint cohort",
        "cells_by_relation": summary["cells_by_relation"],
        "n_distinct_cells": summary["n_distinct_cells"],
        "ownership_by_relation": {
            spec.key: cells[f"{spec.key}:disjoint"]["rho_cell"]
            for spec in RELATIONS},
        "gate": "PASS",
    }


def honest_anomalies(cells: dict[str, dict[str, Any]],
                     arms: dict[str, dict[str, Any]],
                     gates: dict[str, Any], census: dict[str, Any],
                     plateau: dict[str, Any],
                     summary: dict[str, Any]) -> list[dict[str, Any]]:
    """Everything a reader could mistake, named."""

    out: list[dict[str, Any]] = []
    out.append({
        "anomaly": ("the atlas's five relations are NOT five separate "
                    "measurements"),
        "detail": (
            "three of the five share the commonness channel (R1, R4, R5), two "
            "share the volume channel as y (R1, R2) and two share the score "
            "channel as y (R3, R4). The relations are five PROJECTIONS of one "
            "event stream, so agreement between two of them is partly shared "
            "measurement and never a fresh replication. The atlas reports "
            "the map, not five verdicts.")})
    out.append({
        "anomaly": "slog(score) is PLATFORM FEEDBACK, not quality",
        "detail": (
            "`score` is the net of other users' votes as PANDORA recorded it: "
            "it moves with visibility, timing, subreddit size and vote "
            "dynamics. R3 and R4 measure how much feedback an utterance "
            "attracts, never whether it deserved it, and the sign transform "
            "slog(s) = sign(s) log1p(|s|) is used because the counter is "
            f"signed. {census['score_missing']:,} of "
            f"{census['rows_parseable']:,} parseable rows carry no score and "
            "are dropped from R3 and R4 only.")})
    gap_relations = [spec.key for spec in RELATIONS if "gap" in (spec.x,
                                                                 spec.y)]
    out.append({
        "anomaly": "the gap channel drops events, and the drops are not random",
        "detail": (
            f"the relations that use it ({', '.join(gap_relations)}) lose the "
            "first event of every author's stream and every event whose "
            "created_utc ties its predecessor's — a tie is a burst of "
            "same-second comments, so the drop is concentrated in exactly the "
            f"fastest activity. The cache records {census['nonpositive_gaps']:,}"
            f" nonpositive gaps against {census['first_events']:,} first "
            "events over the candidate stream's predecessors.")})
    for spec in RELATIONS:
        gate = gates[spec.key]
        if not gate["ladder"]["coherent"]:
            out.append({
                "anomaly": (f"{spec.key}: the priced ownership ladder is NOT "
                            "coherent, so the classification collapsed (#91)"),
                "detail": (
                    f"the priced regions run [{gate['ladder']['edges'][0]:.4f},"
                    f" {gate['ladder']['edges'][1]:.4f}] around 0.15 and "
                    f"[{gate['ladder']['edges'][2]:.4f}, "
                    f"{gate['ladder']['edges'][3]:.4f}] around 0.50 "
                    f"({', '.join(gate['ladder']['failed_conditions'])}), so "
                    "the ownership cell for this relation is the BINARY "
                    "OWNED / NOT_OWNED and no ladder cell is claimed.")})
    for spec in RELATIONS:
        for cohort, _ in COHORTS:
            arm = arms.get(f"{spec.key}:{cohort}")
            if arm is None or "dispersion" not in arm:
                continue
            disp = arm["dispersion"]
            if not (disp["var_true_cross_half"] > 0):
                out.append({
                    "anomaly": (f"{spec.key} / {cohort}: Var(beta) by "
                                "cross-half covariance is NEGATIVE"),
                    "detail": (
                        f"Cov(beta_early, beta_late) = "
                        f"{disp['var_true_cross_half']:+.6g}, so sd_true and "
                        "the headroom are undefined and printed n/a. A "
                        "variance cannot be negative in truth; at this "
                        "relation's precision the across-author slope "
                        "variance is not distinguishable from zero.")})
    for spec in RELATIONS:
        arm = arms.get(f"{spec.key}:disjoint")
        if arm is None or "beta_within_early" not in arm:
            continue
        early, late = arm["beta_within_early"], arm["beta_within_late"]
        if abs(early - late) > 2 * abs(arm["beta_within"]):
            out.append({
                "anomaly": (f"{spec.key}: level 2 is a two-number average "
                            "whose two numbers disagree"),
                "detail": (
                    f"the within-person slope reads {early:+.6f} on the early "
                    f"half and {late:+.6f} on the late half against the "
                    f"registered estimand {arm['beta_within']:+.6f}. The "
                    "registration pins the average and that is what routes, "
                    "but level 2 is not a stationary quantity here, and "
                    "nothing in this leg separates calendar drift from a "
                    "composition change or from the half split itself.")})
    for spec in RELATIONS:
        gate = gates[spec.key]
        for ceiling in gate.get("ceilings", {}).values():
            ratio = ceiling["replicate_sd"] / ceiling["ceiling"]
            if ceiling["informative"] and ratio > 0.75:
                out.append({
                    "anomaly": (f"{spec.key}: a #90 ceiling passed with little "
                                "room"),
                    "detail": (
                        f"{ceiling['object']} has replicate sd "
                        f"{ceiling['replicate_sd']:.6f} against the ceiling "
                        f"{ceiling['ceiling']:.4f} — {ratio:.0%} of it. The "
                        "clause is INFORMATIVE as registered, but a design "
                        "with a little less precision would have stopped the "
                        "leg here, and the reader should know the margin was "
                        "thin.")})
    for spec in RELATIONS:
        for cohort, _ in COHORTS:
            cell = cells[f"{spec.key}:{cohort}"]
            if not cell["delta_ci_covers_zero"]:
                continue
            lo, hi = cell["delta_ci"]
            width = hi - lo
            edge = min(abs(lo), abs(hi))
            if width > 0 and edge / width < 0.10:
                out.append({
                    "anomaly": (f"{spec.key} / {cohort}: the "
                                "LEVELS_INDISTINGUISHABLE cell is decided by "
                                "a hair"),
                    "detail": (
                        f"Delta = {cell['delta_erg']:+.6f} with CI "
                        f"[{lo:+.6f}, {hi:+.6f}]: the interval covers zero by "
                        f"{edge:.6f}, which is {edge / width:.1%} of its own "
                        "width. NULL-first routing calls this cell and the "
                        "call stands, but it is a power-limited null and not "
                        "an equivalence claim — the scoped reading in the "
                        "boundaries applies with full force here.")})
    for spec in RELATIONS:
        cell = cells[f"{spec.key}:disjoint"]
        if cell["delta_inside_priced_region"] and not cell[
                "delta_ci_covers_zero"]:
            out.append({
                "anomaly": (f"{spec.key}: the Delta point sits INSIDE its own "
                            "priced null-world region while its CI excludes "
                            "zero"),
                "detail": (
                    f"Delta = {cell['delta_erg']:+.6f} against a priced "
                    f"half-width of "
                    f"{gates[spec.key]['regions']['delta']['half_width']:.6f}."
                    " The detection is real at this sample size and the "
                    "effect is smaller than the width a NULL world's own "
                    "interval spans, so it is a boundary-sensitive detection "
                    "rather than a clean one (#87).")})
    if summary["all_nonergodic_literal"] and not summary[
            "all_in_one_nonergodic_cell"]:
        out.append({
            "anomaly": ("the atlas satisfies the LITERAL wording of route 2 "
                        "and was routed to route 3"),
            "detail": (
                "every relation is in a nonergodic cell, which the "
                "registration's route 2 wording ('all five in nonergodic "
                "cells') admits, but the five sit in "
                f"{summary['n_distinct_cells']} DIFFERENT cells "
                f"({', '.join(summary['distinct_cells'])}), which is what "
                "route 3 names as structure. The refinement is recorded in "
                "the config and in the atlas artifact, and both predicates "
                "are printed.")})
    if plateau["n_relations_ci_overlapping"] != plateau["n_relations_in_band"]:
        out.append({
            "anomaly": ("the plateau prediction is scored on POINTS, and the "
                        "intervals tell a slightly different story"),
            "detail": (
                f"{plateau['n_relations_in_band']} of 4 point estimates lie "
                f"in [{PLATEAU_BAND[0]}, {PLATEAU_BAND[1]}] while "
                f"{plateau['n_relations_ci_overlapping']} of 4 CIs OVERLAP "
                "the band. The registered criterion is the point criterion "
                "and it is what is scored; the interval count is printed so "
                "the reader can see how much of the outcome is precision.")})
    return out


# ---------------------------------------------------------------------------
# Stage 6 — the report (rule 24: every table generated from the artifacts)
# ---------------------------------------------------------------------------


BOUNDARIES = (
    "**Metadata only; VOLUME, TIMING and PLATFORM FEEDBACK, never content "
    "(permanent).** The text-derived quantity in this leg is "
    "`word_count_quoteless`, the author's own-word count per comment. No body "
    "was read, no topic, no style, no sentiment. The other channels are a "
    "community's share of the whole event stream, the seconds between one "
    "comment and the next, and the recorded `score`. Every claim is about HOW "
    "MUCH is written, WHEN, WHERE and WITH WHAT RESPONSE — never about WHAT "
    "is written.",
    "**`slog(score)` is platform feedback, not quality.** The score column is "
    "the net of other users' votes as the corpus recorded it. It moves with "
    "visibility, timing, community size and vote dynamics. R3 and R4 measure "
    "how much feedback an utterance attracts; nothing here says an utterance "
    "deserved its score, and no evaluative reading is licensed.",
    "**The projection caution.** beta_between, beta_within and beta_{u,h} are "
    "STATIC projections of much richer dynamic objects. Five scalar relations "
    "measured at three levels say nothing about lags, about how a relation "
    "moves within a half, or about any coordinate not projected. A level "
    "difference is a statement about these projections at this resolution; a "
    "null is not an equivalence claim.",
    "**No psychological naming.** Expression volume, its community gradient, "
    "its rhythm and its feedback are technical objects. Nothing here is a "
    "trait, a state, a disposition or a preference, and the leg is label-free: "
    "`author_profiles.csv` was never opened.",
    "**EXPLORATORY, corpus-level.** No person-level claim is licensed. The "
    "per-author slopes exist only as the population of a mean, a covariance "
    "and one correlation; no individual's beta is a measurement of that "
    "individual.",
    "**The cohort-selection caveat (carried from X2/X4).** A Big5/disjoint "
    "difference cannot be separated from HOW the 1,401 Big5 authors were "
    "selected. The disjoint cohort is also TYPOLOGY-ENRICHED by construction "
    "(PANDORA's non-Big5 authors are MBTI-labelled users), so both cohorts "
    "are platform samples with a selection, not population samples.",
    "**Pool selection, per relation.** Each relation floors at 50 USABLE "
    "events in EACH half AND at the #89 estimability floor, so each speaks "
    "for authors who are ACTIVE ON BOTH SIDES of their own median AND whose "
    "x actually varies within each half. Nothing here speaks for short-lived, "
    "low-volume or single-community accounts, and the five pools are not the "
    "same set of people.",
    "**The owner's three-level schema, cited and not claimed.** The "
    "between / average-within / single-person trichotomy is the program "
    "OWNER's conference input (relayed 2026-08-19) and the framework of "
    "Saegusa & Geshi (2025). This leg supplies a corpus instance of the "
    "schema on metadata; it does not supply the schema.",
)


def bridge_paragraph(summary: dict[str, Any], cells: dict[str, Any],
                     plateau: dict[str, Any]) -> str:
    """The bridge-vocabulary summary paragraph (build-out item 2)."""

    lines = []
    lines.append(
        "This leg is item 2 of the measurement-series bridge's build-out "
        "(`docs/SUICA_MEASUREMENT_SERIES_BRIDGE.md`, section 5): "
        "*the map of the ergodicity contrast* — not one relation but several, "
        "so the question becomes WHICH KINDS of relation carry a large "
        "level-conflation error. The vocabulary is the owner's conference "
        "input and its source paper: "
        "三枝高大・下司忠大 (2025). 個人差研究における個人間関係の解釈の誤り"
        "——測定系列の混同に対する警鐘. パーソナリティ研究, 34(2), 119–134 "
        "(Saegusa & Geshi 2025, JJP 34(2) 119–134). Its three measurement "
        "series map onto this leg exactly: measuring a group once gives the "
        "BETWEEN-person relation (level 1, beta_between); measuring many "
        "people repeatedly gives the AVERAGE WITHIN-person relation (level 2, "
        "beta_within); measuring one person repeatedly gives THAT person's "
        "relation (level 3, beta_{u,h}), whose reliability as a personal "
        "attribute is rho_own.")
    order = [spec.key for spec in RELATIONS]
    parts = []
    for key in order:
        cell = cells[f"{key}:disjoint"]
        parts.append(f"{key} ({RELATION_BY_KEY[key].title}) "
                     f"{cell['delta_cell']}")
    lines.append(
        f"On the disjoint cohort the atlas reads **{summary['route']}**: "
        + "; ".join(parts) + ". Where the cell is nonergodic, reading the "
        "within-person relation off the between-person one is an error of the "
        "size Delta_erg names — and where the signs differ it is an error of "
        "DIRECTION, not of magnitude. Where the cell is "
        "LEVELS_INDISTINGUISHABLE the two series agree at this resolution, "
        "which is a scoped null and not an equivalence claim.")
    worst = max(order, key=lambda k: abs(cells[f"{k}:disjoint"]["delta_erg"]))
    worst_cell = cells[f"{worst}:disjoint"]
    ratio = (abs(worst_cell["delta_erg"]) / abs(worst_cell["beta_within"])
             if worst_cell["beta_within"] else float("nan"))
    lines.append(
        f"The largest conflation error in the atlas is **{worst}** "
        f"({RELATION_BY_KEY[worst].title}): level 1 reads "
        f"{worst_cell['beta_between']:+.4f} against level 2's "
        f"{worst_cell['beta_within']:+.4f}, a difference of "
        f"{worst_cell['delta_erg']:+.4f} "
        f"{fmt_ci(worst_cell['delta_ci'], 4)} — "
        f"{ratio:.1f} times the within-person slope itself. Reading the "
        "within-person relation off the between-person one would overstate "
        "it by that factor.")
    rhos = sorted((cells[f"{key}:disjoint"]["rho_own"], key)
                  for key in order)
    lines.append(
        "For the level-3 reliability catalogue (build-out item 3) the atlas "
        f"contributes {len(NEW_RELATIONS)} new ownership correlations, of "
        f"which {plateau['n_relations_in_band']} "
        f"{'falls' if plateau['n_relations_in_band'] == 1 else 'fall'} in the "
        f"[{PLATEAU_BAND[0]}, {PLATEAU_BAND[1]}] band that X1c's 0.279, X2's "
        "0.259 and X4's floored 0.277 already occupy. The plateau was "
        "registered here as a PREDICTION rather than an observation, and its "
        f"outcome is **{plateau['status']}**: the five values run from "
        f"{rhos[0][0]:+.4f} ({rhos[0][1]}) to {rhos[-1][0]:+.4f} "
        f"({rhos[-1][1]}), a spread of {rhos[-1][0] - rhos[0][0]:.4f} on one "
        "cohort at one span. Level-3 reliability is therefore a property of "
        "the RELATION and not a constant of the corpus — which is what a "
        "catalogue is for, and it is the atlas's most useful negative result "
        "for the owner's manuscript.")
    return "\n\n".join(lines)


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []

    def add(text: str = "") -> None:
        lines.append(text)

    verdict = payload["verdict"]
    cells = payload["cells"]
    arms = payload["arms"]
    gates = payload["gates_detail"]
    census = payload["census"]

    add("# SUICA M4-X5 — the ergodicity atlas")
    add()
    add(f"**Verdict: `{verdict['cell']}`**")
    add()
    add("Registered BEFORE the run in "
        "`docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md` (section "
        "\"X5 — the ergodicity atlas\", commit de09409). Five metadata "
        "relations, each measured at all three of the owner's measurement "
        "series, with the #89 estimability floor as the pool clause, the #90 "
        "precision ceilings on every routing recovery clause, and the #91 "
        "ladder-coherence check on every priced region set. Bridge build-out "
        "item 2. EXPLORATORY, corpus-level, label-free, metadata-only.")
    add()
    if verdict["cell"] == ATLAS_A1_STOP:
        add("**A1 STOP.** A ROUTING clause failed on a realized skeleton, so "
            "no corpus estimand is licensed. Failed relations: "
            + ", ".join(verdict.get("failed_relations", [])) + ".")
        add()

    # ---- gates ------------------------------------------------------------
    add("## Gates")
    add()
    _table(add, ["gate", "status"],
           [[name, f"`{status}`"] for name, status in
            payload["gate_summary"].items()])

    # ---- the atlas table --------------------------------------------------
    if cells:
        add("## THE ATLAS")
        add()
        add("Five relations x three measurement series x two cohorts. "
            "`beta_b` is level 1 (between-person), `beta_w` is level 2 "
            "(average within-person), `Delta` is their difference under the "
            "paired author-cluster bootstrap, and `rho_own` is the level-3 "
            "ownership correlation of the FLOORED per-author slopes. R1's "
            "levels 1-2 are IMPORTED from X4's committed artifacts; its "
            "ownership is recomputed here under the floor.")
        add()
        for cohort, label in COHORTS:
            add(f"### {label}")
            add()
            rows = []
            for spec in RELATIONS:
                cell = cells[f"{spec.key}:{cohort}"]
                own = (f"`{cell['rho_cell']}`"
                       + ("" if cell["ownership_classification"] == "LADDER"
                          else " (#91 collapsed)"))
                rows.append([
                    f"**{spec.key}** {spec.title}",
                    fmt(cell["authors"], 0),
                    fmt(cell["beta_between"], 6),
                    fmt(cell["beta_within"], 6),
                    f"{fmt(cell['delta_erg'], 6)} "
                    f"{fmt_ci(cell['delta_ci'], 6)}",
                    f"`{cell['delta_cell']}`",
                    f"{fmt(cell['rho_own'])} {fmt_ci(cell['rho_ci'])}",
                    own,
                ])
            _table(add, ["relation", "authors", "beta_b", "beta_w",
                         "Delta [95% CI]", "Delta cell", "rho_own [95% CI]",
                         "ownership"], rows)
        add("R1's author count is its FLOORED level-3 pool "
            f"({fmt(cells['R1:disjoint']['authors'], 0)} disjoint, "
            f"{fmt(cells['R1:big5']['authors'], 0)} Big5); its levels 1-2 and "
            "Delta are X4's, measured on X4's pool "
            f"({fmt(payload['r1_import']['disjoint']['x4_authors'], 0)} / "
            f"{fmt(payload['r1_import']['big5']['x4_authors'], 0)}) and "
            "imported unchanged.")
        add()
        summary = payload["atlas"]
        add(f"**Atlas route (disjoint): `{summary['route']}`** — "
            f"{summary['n_distinct_cells']} distinct Delta cell(s) across the "
            "five relations ("
            + ", ".join(f"`{c}`" for c in summary["distinct_cells"]) + "). "
            "All five LEVELS_INDISTINGUISHABLE: "
            f"{fmt(summary['all_levels_indistinguishable'])}; all five in "
            f"nonergodic cells: {fmt(summary['all_nonergodic_literal'])}; all "
            "five in ONE nonergodic cell: "
            f"{fmt(summary['all_in_one_nonergodic_cell'])}.")
        add()
        add(f"**Atlas route (Big5 replication, #73): "
            f"`{payload['atlas_big5']['route']}`.**")
        add()

    # ---- what the #89 floor bought ---------------------------------------
    fx = payload.get("floor_effect")
    if fx:
        add("## What the #89 estimability floor bought")
        add()
        add("X4 measured R1 with the same estimator MINUS the floor and "
            "recorded three pathologies. Both columns are artifact values.")
        add()
        _table(add, ["object", "X4, no floor", "X5, floored"],
               [["cross-half Var(beta), R1 disjoint",
                 fmt(fx["var_beta_R1_disjoint"]["x4_unfloored"], 6),
                 fmt(fx["var_beta_R1_disjoint"]["x5_floored"], 6)],
                ["owned-world rho replicate sd (the #90 object)",
                 fmt(fx["owned_world_rho_replicate_sd"]["x4_unfloored"]),
                 f"{fmt(fx['owned_world_rho_replicate_sd']['x5_floored_min'])}"
                 f"–{fmt(fx['owned_world_rho_replicate_sd']['x5_floored_max'])}"
                 " over the relations"],
                ["priced rho half-width at 0.50 (the #91 object)",
                 fmt(fx["priced_rho_half_width_at_0.50"]["x4_unfloored"]),
                 f"{fmt(fx['priced_rho_half_width_at_0.50']['x5_min'])}"
                 f"–{fmt(fx['priced_rho_half_width_at_0.50']['x5_max'])}"],
                ["ladders coherent", "0 of 1 (WEAKLY_OWNED was empty)",
                 f"{fx['ladders_coherent']} of {fx['ladders_total']}"]])

    # ---- the plateau prediction ------------------------------------------
    plateau = payload.get("plateau")
    if plateau:
        add("## The level-3 plateau, as a PREDICTION")
        add()
        add(f"Registered criterion: {plateau['criterion']}. Band provenance: "
            f"{plateau['band_provenance']}.")
        add()
        _table(add, ["relation", "rho_own", "95% CI", "point in band",
                     "CI overlaps band"],
               [[row["relation"], fmt(row["rho_own"]), fmt_ci(row["rho_ci"]),
                 fmt(row["point_in_band"]), fmt(row["ci_overlaps_band"])]
                for row in plateau["rows"]])
        add(f"**Outcome: `{plateau['status']}`** — "
            f"{plateau['n_relations_in_band']} of {len(NEW_RELATIONS)} new "
            "relations put their point estimate in the band "
            f"({plateau['n_relations_ci_overlapping']} of "
            f"{len(NEW_RELATIONS)} overlap it with the interval).")
        add()

    # ---- census -----------------------------------------------------------
    add("## Census (#78 blocking anchors)")
    add()
    _table(add, ["predicate", "registered", "observed", "status"],
           [[name, _exact(pin["registered"]), _exact(pin["observed"]),
             f"`{pin['status']}`"]
            for name, pin in payload["census_gate"]["pins"].items()])
    add("Per-relation pool arithmetic (x-only, #57: no x-y quantity is "
        "evaluated in the census):")
    add()
    _table(add, ["relation", "x", "y", "usable events", "disjoint pool",
                 "Big5 pool", "dropped by the count floor",
                 "dropped by the #89 den floor", "within-sd(x) med (disjoint)"],
           [[f"**{spec.key}** {spec.title}",
             CHANNEL_TEXT[spec.x], CHANNEL_TEXT[spec.y],
             fmt(census["relations"][spec.key]["usable_events"], 0),
             fmt(census["relations"][spec.key]["pool_disjoint"], 0),
             fmt(census["relations"][spec.key]["pool_big5"], 0),
             fmt(census["relations"][spec.key]["dropped_by_the_count_floor"],
                 0),
             fmt(census["relations"][spec.key]["dropped_by_the_den_floor"], 0),
             fmt(census["relations"][spec.key]["within_sd_x_median_disjoint"],
                 3)]
            for spec in RELATIONS])

    # ---- the R1 import ----------------------------------------------------
    if payload.get("r1_import"):
        add("## The R1 import (bit-check)")
        add()
        imp = payload["r1_import"]
        chk = payload["r1_import_check"]
        _table(add, ["object", "X4 committed", "X5 here", "status"],
               [["Delta_erg (disjoint)", fmt(imp["disjoint"]["delta_erg"], 6),
                 "imported, not recomputed", "`IMPORTED`"],
                ["Delta_erg (Big5)", fmt(imp["big5"]["delta_erg"], 6),
                 "imported, not recomputed", "`IMPORTED`"],
                ["floored rho_own (disjoint)", fmt(chk["x4_committed"], 12),
                 fmt(chk["x5_recomputed"], 12), f"`{chk['status']}`"],
                ["floored pool authors (disjoint)", fmt(chk["authors_x4"], 0),
                 fmt(chk["authors_x5"], 0),
                 f"`{'PASS' if chk['authors_match'] else 'FAIL'}`"]])
        add("The floored ownership point is recomputed from THIS leg's fresh "
            "five-column cache and must reproduce X4's committed value to "
            f"{chk['tolerance']:g}: same events, same order, same pinned "
            "two-pass path. The observed difference is "
            f"{chk['abs_difference']:.3g}.")
        add()

    # ---- per-relation gates ----------------------------------------------
    add("## Part 0 — the per-relation gate")
    add()
    add("Each relation's battery runs on ITS OWN realized skeleton (real x "
        "sequences, real halves, real cell sizes; wholly synthetic y). R1 "
        "inherits X4's passed gate. The OWNED-slopes recovery ROUTES once, on "
        "R2's skeleton, as registered; the owned worlds still run on every "
        "relation because #88a prices each relation's rho regions from its "
        "own matched worlds.")
    add()
    for spec in RELATIONS:
        gate = gates[spec.key]
        add(f"### {spec.key} — {spec.title} (`{gate['status']}`)")
        add()
        _table(add, ["clause", "requirement", "observed", "status"],
               [[f"**{c['id']}** {c['clause']}", c["required"], c["observed"],
                 f"`{c['status']}`"] for c in gate["routing"]])
        _table(add, ["descriptive", "observed", "status"],
               [[f"**{c['id']}** {c['clause']}", c["observed"],
                 f"`{c['status']}`"] for c in gate["descriptive"]])
        reg = gate["regions"]
        lad = gate["ladder"]
        add(f"Priced regions (#88a, pinned {reg['priced_utc']}): Delta "
            f"+-{fmt(reg['delta']['half_width'], 6)} from the "
            f"`{reg['delta']['matched_world']}` world; rho at 0.15 "
            f"+-{fmt(reg['rho_low']['half_width'])}; rho at 0.50 "
            f"+-{fmt(reg['rho_high']['half_width'])}. "
            f"**#91 ladder: `{lad['status']}`** — edges "
            f"[{fmt(lad['edges'][0])}, {fmt(lad['edges'][1])}] and "
            f"[{fmt(lad['edges'][2])}, {fmt(lad['edges'][3])}]. {lad['note']}.")
        add()
        if gate.get("ceilings"):
            _table(add, ["#90 ceiling", "replicate sd", "ceiling", "status"],
                   [[c["object"], fmt(c["replicate_sd"], 6),
                     fmt(c["ceiling"], 6), f"`{c['status']}`"]
                    for c in gate["ceilings"].values()])

    # ---- three levels in full --------------------------------------------
    if arms:
        add("## The three levels in full (disjoint cohort)")
        add()
        _table(add, ["relation", "level 1 beta_between [CI]",
                     "level 2 beta_within [CI]", "level 2 early / late",
                     "level 3 mean beta", "Var(beta) cross-half",
                     "rho_own pairing band"],
               [[f"**{spec.key}**",
                 f"{fmt(arms[f'{spec.key}:disjoint']['beta_between'], 6)} "
                 f"{fmt_ci(arms[f'{spec.key}:disjoint']['boot']['beta_between_ci'], 6)}",
                 f"{fmt(arms[f'{spec.key}:disjoint']['beta_within'], 6)} "
                 f"{fmt_ci(arms[f'{spec.key}:disjoint']['boot']['beta_within_ci'], 6)}",
                 f"{fmt(arms[f'{spec.key}:disjoint'].get('beta_within_early'), 6)}"
                 f" / {fmt(arms[f'{spec.key}:disjoint'].get('beta_within_late'), 6)}",
                 fmt(payload["level3"][f"{spec.key}:disjoint"]["mean_beta"], 6),
                 fmt(payload["level3"][f"{spec.key}:disjoint"][
                     "var_true_cross_half"], 6),
                 fmt_ci(payload["level3"][f"{spec.key}:disjoint"]["band"])]
                for spec in RELATIONS])

    # ---- leans ------------------------------------------------------------
    if payload.get("leans"):
        add("## Registered leans")
        add()
        _table(add, ["lean", "registered", "observed", "status"],
               [[row["lean"], f"`{row['registered']}`", row["observed"],
                 f"`{row['status']}`"] for row in payload["leans"]])
        held = sum(1 for r in payload["leans"] if r["status"] == "HELD")
        broken = sum(1 for r in payload["leans"] if r["status"] == "BROKEN")
        add(f"**{held} held, {broken} broken**, one registered unleaned.")
        add()

    # ---- #73 flags --------------------------------------------------------
    add("## Cohort divergences (#73) and priced-region straddles (#87)")
    add()
    if payload.get("flags_73"):
        _table(add, ["relation", "object", "note", "detail"],
               [[f["relation"], f["object"], f["note"],
                 (f"disjoint {fmt(f.get('primary'))} vs Big5 "
                  f"{fmt(f.get('big5'))}" if "primary" in f
                  else f.get("cohort", ""))]
                for f in payload["flags_73"]])
    else:
        add("None.")
        add()

    # ---- anomalies --------------------------------------------------------
    add("## Honest anomalies")
    add()
    for item in payload.get("anomalies", []):
        add(f"- **{item['anomaly']}.** {item['detail']}")
    add()

    # ---- the bridge paragraph --------------------------------------------
    add("## The reading, in the bridge's vocabulary")
    add()
    add(payload["bridge_paragraph"])
    add()

    # ---- boundaries and config -------------------------------------------
    add("## Boundaries")
    add()
    for text in BOUNDARIES:
        add(f"- {text}")
    add()
    add("## Configuration")
    add()
    _table(add, ["key", "value"],
           [[f"`{key}`", f"`{json.dumps(value, ensure_ascii=False)}`"
             if isinstance(value, (dict, list)) else f"`{value}`"]
            for key, value in sorted(payload["config"].items())])
    add(f"Config SHA-256 `{payload['config_sha256']}`. Run finished "
        f"{payload['run']['finished_utc']} in "
        f"{payload['run']['runtime_s']:.1f} s.")
    add()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Stage 7 — main
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
    parser.add_argument("--stop-after-census", action="store_true",
                        help="census only; writes no estimand (development)")
    args = parser.parse_args(argv)

    started = time.time()
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    log = RunLog(output / "run_log.jsonl")
    log.event("start", registration=("docs/SUICA_M4_X_EXPRESSION_RESPONSE_"
                                     "PLAN.md#X5 (commit de09409)"),
              seed=SEED, b_perm=args.b_perm, b_boot=args.b_boot)

    config = {
        "leg": "M4-X5",
        "registration": ("docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md, "
                         "section X5, commit de09409"),
        "question_provenance": ("the program OWNER's conference input "
                                "(relayed 2026-08-19) and the measurement-"
                                "series bridge, build-out item 2"),
        "seed": SEED, "seed_part0": SEED_PART0, "seed_perm": SEED_PERM,
        "seed_boot": SEED_BOOT,
        "b_perm": args.b_perm, "b_boot": args.b_boot,
        "relations": {spec.key: {"title": spec.title,
                                 "x": CHANNEL_TEXT[spec.x],
                                 "y": CHANNEL_TEXT[spec.y],
                                 "imported": spec.imported}
                      for spec in RELATIONS},
        "order": ("per-author stable sort by created_utc (ties keep stream "
                  "order)"),
        "halves": "full-stream median of the author's created_utc, <= early",
        "pool": (">= 50 USABLE events in EACH half AND the #89 estimability "
                 "floor den >= 1 in EACH half"),
        "pool_floor_events": POOL_FLOOR_EVENTS,
        "estimability_floor_den": ESTIMABILITY_FLOOR_DEN,
        "estimability_floor_path": ("PINNED two-pass float64: cell mean by "
                                    "bincount sum / bincount count, then "
                                    "bincount of the squared deviations"),
        "level_3_estimator": ("the FLOORED per-author slope throughout; the "
                              "pool's own floor makes every scored cell "
                              "estimable, and authors failing the floor are "
                              "excluded and counted"),
        "gap_rule": ("log10 seconds since the author's previous comment over "
                     "the full stream; the first event of an author is "
                     "dropped and so is any nonpositive gap"),
        "score_rule": ("slog(score) = sign(score) * log1p(abs(score)); rows "
                       "with a missing score are dropped from the relations "
                       "that use it"),
        "boundary_centres": {"delta": BOUNDARY_DELTA_CENTRE,
                             "rho_low": BOUNDARY_RHO_LOW,
                             "rho_high": BOUNDARY_RHO_HIGH},
        "boundary_half_widths": ("PRICED IN-LEG (#88a) per relation from that "
                                 "relation's matched planted worlds"),
        "tol_floor_delta": TOL_FLOOR_DELTA,
        "tol_floor_rho": TOL_FLOOR_RHO,
        "tol_rule": (f"max(floor, {TOL_SD_MULT} x replicate sd), with the #90 "
                     "CEILING replicate sd <= floor asserted on every routing "
                     "recovery clause"),
        "planted_beta": BETA_PLANT, "planted_gamma": GAMMA_PLANT,
        "planted_sd_intercept": SD_A, "planted_sd_noise": SD_E,
        "rho_true_target": RHO_TRUE_TARGET, "rho_price_low": RHO_PRICE_LOW,
        "n_synth_replicates": N_SYNTH_REPLICATES,
        "ergodic_cover_floor": ERGODIC_COVER_FLOOR,
        "ownership_recovery_routes_on": "R2",
        "atlas_route_2_refinement": ("route 2 fires only when all five "
                                     "relations sit in the SAME nonergodic "
                                     "cell; five relations in two different "
                                     "nonergodic cells is route 3, and both "
                                     "predicates are recorded"),
        "plateau_band": list(PLATEAU_BAND),
        "plateau_min_relations": PLATEAU_MIN_RELATIONS,
        "comments": str(args.comments), "cohort": str(args.cohort),
        "columns_read": ["author", "subreddit", "created_utc",
                         "word_count_quoteless", "score"],
        "author_profiles_csv": "NEVER OPENED (label-free)",
    }
    write_json(output / "config.json", config)
    config_sha = hashlib.sha256(
        json.dumps(config, sort_keys=True).encode("utf-8")).hexdigest()
    write_json(output / "config.sha256.json",
               {"sha256": config_sha, "utc": utc_now()})

    # ---- Stage 1: the event cache -----------------------------------------
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
        del scaffold["author_code"], scaffold["subreddit_code"]
        del scaffold["created_utc"], scaffold["wcq"], scaffold["score"]
        save_cache(cache, scaffold, cache_path)
        log.event("cache_saved", path=str(cache_path))

    is_big5 = cache["pool_is_big5"]
    cohort_set = set(cohort_names)
    big5_all = np.array([name in cohort_set for name in author_names])
    who, half = event_author_and_half(cache)

    # ---- Stage 2: the census (#57: x-only) --------------------------------
    stats_by_relation = {spec.key: relation_stats(cache, spec, who, half)
                         for spec in RELATIONS}
    x4_mask = x4_pool_mask(cache)
    r1_x4_pool = x4_mask & stats_by_relation["R1"]["count_floor"]
    comm_x = cache["comm_x"]
    # Every cached author contributes exactly one first event (whole authors
    # are cached), so the remaining undefined gaps are the nonpositive ones.
    first_events = int(cache["n_total"].size)
    census_relations = {}
    for spec in RELATIONS:
        st = stats_by_relation[spec.key]
        pool = st["pool"]
        census_relations[spec.key] = {
            "relation": spec.key,
            "x": CHANNEL_TEXT[spec.x], "y": CHANNEL_TEXT[spec.y],
            "usable_events": st["usable_events"],
            "pool_disjoint": int((pool & ~is_big5).sum()),
            "pool_big5": int((pool & is_big5).sum()),
            "dropped_by_the_count_floor": st["dropped_by_the_count_floor"],
            "dropped_by_the_den_floor": st["dropped_by_the_den_floor"],
            "within_sd_x_median_disjoint": float(
                np.median(st["within_sd_x"][pool & ~is_big5])),
            "within_sd_x_median_big5": float(
                np.median(st["within_sd_x"][pool & is_big5])),
        }
    observed = {
        "rows parseable (author+subreddit+created_utc+wcq)":
            int(stats["rows_parseable"]),
        "authors": int(stats["authors"]),
        "Big5 cohort authors seen": int(big5_all.sum()),
        "disjoint authors": int((~big5_all).sum()),
        "communities": int(stats["subreddits"]),
        "score missing (of parseable)": int(stats["score_missing"]),
        "x = log10(share), min (2 dp)": round(float(comm_x.min()), 2),
        "x = log10(share), max (2 dp)": round(float(comm_x.max()), 2),
        "R1 pool, X4's sd(x) > 0 path, disjoint":
            int((r1_x4_pool & ~is_big5).sum()),
        "R1 pool, X4's sd(x) > 0 path, Big5":
            int((r1_x4_pool & is_big5).sum()),
    }
    expected = {
        "rows parseable (author+subreddit+created_utc+wcq)":
            ANCHOR_ROWS_PARSEABLE,
        "authors": ANCHOR_AUTHORS,
        "Big5 cohort authors seen": ANCHOR_BIG5_AUTHORS,
        "disjoint authors": ANCHOR_DISJOINT_AUTHORS,
        "communities": ANCHOR_COMMUNITIES,
        "score missing (of parseable)": ANCHOR_SCORE_MISSING,
        "x = log10(share), min (2 dp)": ANCHOR_X_MIN,
        "x = log10(share), max (2 dp)": ANCHOR_X_MAX,
        "R1 pool, X4's sd(x) > 0 path, disjoint": ANCHOR_POOL["R1"][0],
        "R1 pool, X4's sd(x) > 0 path, Big5": ANCHOR_POOL["R1"][1],
    }
    for spec in RELATIONS:
        if spec.key == "R1":
            observed["R1 pool, #89 floored, disjoint"] = \
                census_relations["R1"]["pool_disjoint"]
            observed["R1 pool, #89 floored, Big5"] = \
                census_relations["R1"]["pool_big5"]
            continue
        observed[f"{spec.key} pool, disjoint"] = \
            census_relations[spec.key]["pool_disjoint"]
        observed[f"{spec.key} pool, Big5"] = \
            census_relations[spec.key]["pool_big5"]
        observed[f"{spec.key} within-sd(x) median, disjoint (3 dp)"] = round(
            census_relations[spec.key]["within_sd_x_median_disjoint"], 3)
        expected[f"{spec.key} pool, disjoint"] = ANCHOR_POOL[spec.key][0]
        expected[f"{spec.key} pool, Big5"] = ANCHOR_POOL[spec.key][1]
        expected[f"{spec.key} within-sd(x) median, disjoint (3 dp)"] = \
            ANCHOR_SDX_MEDIAN_DISJOINT[spec.key]
    census_gate = anchor_gate(observed, expected)
    census = {
        "rows_parseable": int(stats["rows_parseable"]),
        "score_missing": int(stats["score_missing"]),
        "first_events": first_events,
        "nonpositive_gaps": int(
            np.count_nonzero(~np.isfinite(cache["ev_gap"]))) - first_events,
        "candidate_authors": int(cache["n_total"].size),
        "cached_events": int(cache["offsets"][-1]),
        "relations": census_relations,
        "stream_stats": stats,
    }
    write_json(output / "census.json", {**census_gate, **census})
    log.event("census", status=census_gate["status"])
    if census_gate["status"] != "PASS":
        raise SystemExit("STOP (#78): the census gate FAILED: " + json.dumps(
            {k: v for k, v in census_gate["pins"].items()
             if v["status"] != "PASS"}, indent=2, default=str))
    if args.stop_after_census:
        log.event("stop_after_census")
        return 0

    # ---- Stage 3: Part 0, per relation ------------------------------------
    gates: dict[str, Any] = {}
    for spec in RELATIONS:
        if spec.imported:
            gates[spec.key] = imported_r1_gate()
            log.event("gate_imported", relation=spec.key,
                      status=gates[spec.key]["status"])
            continue
        st = stats_by_relation[spec.key]
        sel = st["pool"] & ~is_big5
        sk = RelationSkeleton("disjoint", "PRIMARY — disjoint pool", spec,
                              cache, sel, st, who, half, with_events=True)
        gates[spec.key] = relation_gate(
            sk, b_perm=args.b_perm, b_boot=args.b_boot,
            seed=SEED_PART0 + 10_000 * (RELATIONS.index(spec) + 1), log=log,
            routes_ownership=(spec.key == "R2"))
        sk.events = None
        log.event("gate_done", relation=spec.key,
                  status=gates[spec.key]["status"],
                  ladder=gates[spec.key]["ladder"]["status"])
    write_json(output / "part0_gate.json", gates)
    write_json(output / "region_pricing.json",
               {key: {"regions": gate["regions"], "ladder": gate["ladder"]}
                for key, gate in gates.items()})
    gate_summary = {
        f"Census / blocking anchors (#78, {len(census_gate['pins'])} "
        "predicates)": census_gate["status"],
    }
    for spec in RELATIONS:
        gate_summary[f"Part 0 gate, {spec.key} ({spec.title})"] = \
            gates[spec.key]["status"]

    if any(gate["status"] != "PASS" for gate in gates.values()):
        verdict = build_verdict(gates, {"route": ATLAS_A1_STOP}, {})
        write_json(output / "verdict.json", verdict)
        payload = {"run": {"finished_utc": utc_now(),
                           "runtime_s": time.time() - started},
                   "config": config, "config_sha256": config_sha,
                   "census": census, "census_gate": census_gate,
                   "gates_detail": gates, "gate_summary": gate_summary,
                   "arms": {}, "cells": {}, "level3": {}, "leans": [],
                   "flags_73": [], "anomalies": [], "atlas": {},
                   "atlas_big5": {}, "plateau": None, "r1_import": None,
                   "verdict": verdict,
                   "bridge_paragraph": ("A1 stop: no corpus number is "
                                        "licensed, so no bridge reading is "
                                        "written."),
                   "ordering": {"status": "A1_STOP"}}
        write_report(args.report, payload)
        write_json(output / "report_payload.json",
                   {k: v for k, v in payload.items() if k != "config"})
        log.event("a1_stop", failed=verdict.get("failed_relations"))
        raise SystemExit("A1 STOP: a Part 0 ROUTING clause failed; no corpus "
                         "estimand was scored.")

    # ---- Stage 4: THE FIRST REAL NUMBER (after every relation is priced) --
    first_real_utc = utc_now()
    log.event("first_real_number", utc=first_real_utc,
              note="every relation's region pricing is already on disk")

    arms: dict[str, Any] = {}
    level3: dict[str, Any] = {}
    r1_import = {cohort: import_r1_levels(cohort) for cohort, _ in COHORTS}
    r1_check: dict[str, Any] = {}
    for i, spec in enumerate(RELATIONS):
        st = stats_by_relation[spec.key]
        pool_all = st["pool"]
        sk_all = RelationSkeleton("pool", "the whole pool", spec, cache,
                                  pool_all, st, who, half, with_events=True)
        y_usable = cache[f"ev_{spec.y}"][sk_all.events["sel_event"]]
        mom_all = cell_moments(sk_all, y_usable)
        sk_all.events = None
        del y_usable
        for cohort, label in COHORTS:
            sel = pool_all & (is_big5 if cohort == "big5" else ~is_big5)
            sk = RelationSkeleton(cohort, label, spec, cache, sel, st, who,
                                  half, with_events=False)
            local = np.searchsorted(sk_all.codes, sk.codes)
            mom = {k: v[local] for k, v in mom_all.items()}
            result = analyse_relation_arm(
                sk, mom, b_perm=args.b_perm, b_boot=args.b_boot,
                seed_perm=SEED_PERM + 1000 * i + 7 * len(cohort),
                seed_boot=SEED_BOOT + 1000 * i + 7 * len(cohort),
                with_levels=not spec.imported)
            key = f"{spec.key}:{cohort}"
            level3[key] = {**result["dispersion"],
                           "band": result["ownership_null"]["band"]}
            if spec.imported:
                imported = r1_import[cohort]
                if cohort == "disjoint":
                    r1_check = r1_import_check(result, imported)
                    log.event("r1_import_check", **r1_check)
                    if r1_check["status"] != "PASS":
                        raise SystemExit(
                            "STOP: the R1 import bit-check FAILED: "
                            + json.dumps(r1_check, indent=2, default=str))
                merged = dict(result)
                merged.update({k: v for k, v in imported.items()
                               if k not in ("relation", "cohort", "label")})
                merged["label"] = (f"{label} — levels 1-2 IMPORTED from X4 "
                                   f"({imported['x4_arm']})")
                arms[key] = merged
            else:
                arms[key] = result
            log.event("arm_done", relation=spec.key, cohort=cohort,
                      beta_between=arms[key]["beta_between"],
                      beta_within=arms[key]["beta_within"],
                      delta_erg=arms[key]["delta_erg"],
                      rho_own=arms[key]["rho_own"])
        del mom_all
    write_json(output / "arms.json", arms)

    ordering = {
        "priced_utc": {key: gate["regions"]["priced_utc"]
                       for key, gate in gates.items()},
        "first_real_number_utc": first_real_utc,
        "status": "PASS" if all(
            gate["regions"]["priced_utc"] < first_real_utc
            for gate in gates.values()) else "FAIL",
        "note": ("#88a: every relation's boundary regions were pinned to disk "
                 "BEFORE any real estimand was computed; the timestamps come "
                 "from the artifacts, not from prose. R1's pricing is X4's "
                 "committed timestamp, which predates this run entirely."),
    }
    write_json(output / "ordering.json", ordering)
    gate_summary["#88a pricing order (every relation priced before the first "
                 "real number)"] = ordering["status"]
    if ordering["status"] != "PASS":
        raise SystemExit("STOP: a region pricing was not pinned before the "
                         "first real number.")

    # ---- Stage 5: cells, the atlas, leans ---------------------------------
    cells = {key: classify(result, gates[result["relation"]])
             for key, result in arms.items()}
    write_json(output / "cells.json", cells)
    summary = atlas_summary(cells, "disjoint")
    summary_big5 = atlas_summary(cells, "big5")
    write_json(output / "atlas.json", {"disjoint": summary,
                                       "big5": summary_big5})
    plateau = plateau_prediction(cells)
    write_json(output / "plateau.json", plateau)
    leans = evaluate_leans(cells, summary, plateau)
    write_json(output / "leans.json", leans)
    flags = flags_73(cells)
    write_json(output / "flags_73.json", flags)
    effect = floor_effect(gates, arms)
    write_json(output / "floor_effect.json", effect)
    anomalies = honest_anomalies(cells, arms, gates, census, plateau, summary)
    write_json(output / "anomalies.json", anomalies)
    verdict = build_verdict(gates, summary, cells)
    write_json(output / "verdict.json", verdict)
    log.event("verdict", cell=verdict["cell"],
              cells_by_relation=summary["cells_by_relation"])

    payload = {
        "run": {"finished_utc": utc_now(), "runtime_s": time.time() - started},
        "config": config, "config_sha256": config_sha,
        "census": census, "census_gate": census_gate,
        "gates_detail": gates, "gate_summary": gate_summary,
        "arms": arms, "cells": cells, "level3": level3, "atlas": summary,
        "atlas_big5": summary_big5, "plateau": plateau, "leans": leans,
        "flags_73": flags, "anomalies": anomalies, "ordering": ordering,
        "r1_import": r1_import, "r1_import_check": r1_check,
        "floor_effect": effect,
        "bridge_paragraph": bridge_paragraph(summary, cells, plateau),
        "verdict": verdict,
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
    gate_summary[
        f"ID-leak scan (0 NEW hits of {len(universe):,} author names over the "
        f"committed files; {scan['n_pre_existing_hits']} pre-existing "
        "dictionary collisions carried unchanged from HEAD)"] = scan["status"]
    payload["id_leak_scan"] = {k: v for k, v in scan.items() if k != "hits"}
    payload["gate_summary"] = gate_summary
    write_report(args.report, payload)
    if scan["status"] != "PASS":
        raise SystemExit(f"STOP: ID-leak scan FAILED on NEW hits: {new_hits}")

    write_json(output / "report_payload.json",
               {k: v for k, v in payload.items() if k != "config"})
    log.event("done", verdict=verdict["cell"],
              runtime_s=round(time.time() - started, 1))
    return 0


if __name__ == "__main__":                       # pragma: no cover
    raise SystemExit(main())
