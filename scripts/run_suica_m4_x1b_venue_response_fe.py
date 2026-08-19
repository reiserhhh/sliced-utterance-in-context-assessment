#!/usr/bin/env python3
"""SUICA M4-X1b — the venue response, repaired design and exact estimator.

Registered BEFORE the run in ``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``
(commit 0f8e43e, section "X1b").  This runner executes that registration and
nothing else.  X1b is the completion of X1's A1 stop: the 4W header, the
census, the half rule, the cells, the leans and the boundaries are inherited
VERBATIM; two things change.

1. THE DESIGN (support conditioning as primary, defect #85c).  The community
   universe is the LAW vocabulary (SR0's distinct-user rule at floor
   ceil(0.01 x 8,895) = 89, giving exactly 1,443 communities), and the
   eligible grid is built by a PINNED predicate chain with NO fixed-point
   iteration: (1) cells at n_min comments, disjoint authors, law communities;
   (2) shared pairs — both halves eligible; (3) a community support floor of
   s authors holding a shared pair; (4) authors with at least k_min surviving
   shared communities; (5) the largest connected component of the
   author x community bipartite graph.

2. THE ESTIMATOR (exact zero on any connected design).  Per half, two-way
   FIXED EFFECTS on the eligible shared cells by ALTERNATING PROJECTIONS —
   the within-transform demeaning of the cell means by author and then by
   community, iterated until the maximum absolute change is at most 1e-10.
   v = the FE residual of the cell mean.  X1's double-centering was exact
   only on a complete grid; the alternating projection is exact on any
   connected one, and the LCC covers 100% of authors at every support floor.
   R and the interaction covariance share are defined on v exactly as in X1;
   the author and community main shares come from the same cross-half
   covariances as in X1 and are estimated PRE-FE on the same pool.

PART 0 — THE GATE THAT FAILED MUST NOW PASS (#76/#85, A1 STOP)
--------------------------------------------------------------
The same realized-skeleton battery that stopped X1 runs again on the X1b
skeleton: a planted world {author .30, community .08, interaction .02}, a
NULL world (interaction 0), and author-only / community-only ablation worlds,
8 replicates each, with the real incidence carrying wholly synthetic y.  PASS
requires EVERY clause: recovery of all three planted shares inside
max(0.01, 3 x replicate sd); null-world non-detection (the interaction
share's cluster-bootstrap CI covers 0, its point sits inside the permutation
band, and R sits inside its band); ablation leakage below 0.005 on the
interaction share; and the #85b BOOTSTRAP-ZERO clause — the null world's
cluster-bootstrap CI covers 0.  Any clause failing fires the A1 stop: no real
estimand is computed, and the honest gate is the whole report.

GOVERNANCE
----------
Metadata only: the leg runs off X1's committed cell cache, whose sufficient
statistics were built from ``author``, ``subreddit``, ``created_utc``,
``word_count_quoteless`` and ``word_count``.  NO text body is ever read.
``author_profiles.csv`` is NEVER opened — the leg is label-free end to end.
Caches and author listings live in gitignored ``results/`` and are never
committed.  Aggregates only.  EXPLORATORY, corpus-level; no person claims; no
psychological naming (expression VOLUME is a technical object, not a trait).
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

N_MIN_PRIMARY = 10                  # registration pin: cell eligibility
N_MIN_SENSITIVITY = 5               # registration pin: sensitivity floor
K_MIN = 3                           # registration pin: shared communities
S_PRIMARY = 5                       # registration pin: community support floor
S_SENSITIVITY = 8                   # registration pin: support sensitivity
S_CENSUS = (3, 5, 8)                # registration pin: the censused floors

VOCAB_FLOOR_FRACTION = 0.01         # SR0's rule, re-instantiated (W1)
BIG5_POWER_FLOOR = 300              # registration pin: the IN-LEG #69 floor

FE_TOL = 1e-10                      # registration pin: alternating-projection
FE_MAX_ITER = 100_000               # recorded guard (never reached in practice)

# --- inherited anchors (X1's census, BLOCKING under #78) -------------------

ANCHOR_ROWS_PARSEABLE = 17_640_062
ANCHOR_AUTHORS = 10_296
ANCHOR_BIG5_AUTHORS = 1_401
ANCHOR_DISJOINT_AUTHORS = 8_895
ANCHOR_VOCAB_FLOOR_USERS = 89
ANCHOR_LAW_VOCAB = 1_443

# --- the X1b predicate-chain census (planner, on X1's committed cache) -----
# BLOCKING (#78): the chain must reproduce the planner's table to the unit.

CHAIN_ANCHORS: dict[int, dict[str, Any]] = {
    3: {"authors": 3_686, "communities": 1_145, "shared_pairs": 32_415},
    5: {"authors": 3_665, "communities": 1_000, "shared_pairs": 31_899,
        "singleton_communities": 0, "lcc_author_coverage": 1.0},
    8: {"authors": 3_595, "communities": 780, "shared_pairs": 30_561},
}

# Non-gating cross-checks the planner's table also publishes.
CHAIN_CROSSCHECKS: dict[int, dict[str, float]] = {
    3: {"fill": 0.0077, "authors_per_community_median": 11.0,
        "singleton_community_share": 0.0009},
    5: {"fill": 0.0087, "authors_per_community_median": 12.5,
        "singleton_community_share": 0.0000},
    8: {"fill": 0.0109, "authors_per_community_median": 16.0,
        "singleton_community_share": 0.0000},
}

# --- verdict cells (inherited from X1 verbatim; #75-keyed on the share) ----

TRACE_MAX = 0.02
IDIOSYNCRATIC_MAX = 0.10

CELL_NO_RESPONSE = "NO_REPRODUCIBLE_RESPONSE"
CELL_TRACE = "RESPONSE_TRACE"
CELL_IDIOSYNCRATIC = "IDIOSYNCRATIC_RESPONSE"
CELL_MAJOR = "RESPONSE_MAJOR"
CELL_A1_STOP = "A1_STOP__SYNTHETIC_GATE_FAILED"

# --- registered leans (inherited; report against, never route) -------------

LEAN_R = (0.05, 0.30)
LEAN_INTERACTION = (0.005, 0.05)
LEAN_AUTHOR_MAIN = (0.15, 0.45)
LEAN_COMMUNITY_MAIN = (0.02, 0.15)

# --- Part 0, the gate that must now pass -----------------------------------

PLANTED_SHARES = {"author": 0.30, "community": 0.08, "interaction": 0.02}
NULL_SHARES = {"author": 0.30, "community": 0.08, "interaction": 0.00}
ABLATION_WORLDS = {
    "author_only": {"author": 0.30, "community": 0.00, "interaction": 0.00},
    "community_only": {"author": 0.00, "community": 0.08, "interaction": 0.00},
}
N_SYNTH_REPLICATES = 8              # registration pin
TOL_SD_MULT = 3.0                   # registration pin: 3 x replicate sd ...
TOL_FLOOR = 0.01                    # ... floored at 0.01 of total variance
ABLATION_LEAK_MAX = 0.005           # registration pin: leakage clause

# --- recorded implementation choices (registration silent) -----------------

CHUNK_SIZE = 2_000_000
MIN_CELL_KEEP = 5
PERM_BATCH = 64

SEED_PART0 = SEED + 1               # world draws (X1's derivation, inherited)
SEED_PERM = SEED + 2                # permutation nulls
SEED_BOOT = SEED + 3                # cluster bootstraps

DEFAULT_COMMENTS = Path(
    "/Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/"
    "all_comments_since_2015.csv")
DEFAULT_COHORT = ROOT / "results/m4_sr0_recon/cohort_authors.csv"
DEFAULT_X1_CACHE = ROOT / "results/m4_x1_venue_response/cell_cache.npz"
DEFAULT_OUTPUT = ROOT / "results/m4_x1b_venue_response_fe"
DEFAULT_REPORT = ROOT / "reports/SUICA_M4_X1B_VENUE_RESPONSE_FE_REPORT.md"

X1_SCRIPT = ROOT / "scripts/run_suica_m4_x1_venue_response.py"

COMMITTED_FILES = (
    ROOT / "reports/SUICA_M4_X1B_VENUE_RESPONSE_FE_REPORT.md",
    ROOT / "scripts/run_suica_m4_x1b_venue_response_fe.py",
    ROOT / "tests/test_m4_x1b_venue_response_fe.py",
    ROOT / "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md",
    ROOT / "docs/CLAIMS_LEDGER.md",
)


# ---------------------------------------------------------------------------
# X1's machinery, imported BY FILE (#56/#81: the inherited object, not a copy)
# ---------------------------------------------------------------------------


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:      # pragma: no cover
        raise RuntimeError(f"cannot import machinery from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


X1 = load_module("suica_m4_x1_for_x1b", X1_SCRIPT)

Design = X1.Design
write_json = X1.write_json
utc_now = X1.utc_now
fmt = X1.fmt
fmt_ci = X1.fmt_ci
RunLog = X1.RunLog
percentile_ci = X1.percentile_ci
scan_for_cohort_ids = X1.scan_for_cohort_ids
baseline_hit_keys = X1.baseline_hit_keys
new_hits_only = X1.new_hits_only
anchor_gate = X1.anchor_gate
double_center = X1.double_center                  # X1's estimator, for the
per_author_correlations = X1.per_author_correlations   # side-by-side repair
weighted_cov = X1.weighted_cov                    # demonstration only
variance_budget = X1.variance_budget
permutation_batch = X1.permutation_batch
synthetic_design = X1.synthetic_design
headroom_report = X1.headroom_report
magnitude_cells = X1.magnitude_cells
point_cell = X1.point_cell


def _pct(value: float) -> str:
    return fmt(value, 4)


# ---------------------------------------------------------------------------
# Stage 1 — the cell cache (X1's committed sufficient statistics)
# ---------------------------------------------------------------------------


def load_cell_cache(cache_path: Path, log: RunLog) -> tuple[dict[str, Any],
                                                            dict[str, Any]]:
    """Load X1's committed cell cache — every X1b estimand is a function of it.

    The cache holds, at the n >= 5 floor, the (author, community, half) cell
    sufficient statistics (counts, sums and sums of squares of y for both
    y-definitions), the FULL (author, community) incidence used by the
    vocabulary rule, and the author metadata.  It is gitignored, and this leg
    re-streams the 17.6M-row comments file ONLY if the cache is absent.
    """

    meta_path = cache_path.with_suffix(".meta.json")
    if cache_path.exists() and meta_path.exists():
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
        log.event("cache_loaded", path=str(cache_path),
                  cells=int(table["n_cells_kept"]),
                  authors=table["n_authors"])
        return table, scaffold
    log.event("cache_absent_restreaming", path=str(cache_path))
    scaffold = X1.stream_metadata(DEFAULT_COMMENTS, log)
    table = X1.build_cell_table(scaffold, log)
    X1.save_cache(table, scaffold, cache_path)
    return table, scaffold


def law_vocabulary(table: dict[str, Any], disjoint_mask: np.ndarray,
                   log: RunLog) -> dict[str, Any]:
    """SR0's distinct-user rule on the FULL incidence — W1's law vocabulary."""

    return X1.law_vocabulary(table, disjoint_mask, log)


# ---------------------------------------------------------------------------
# Stage 2 — the pinned predicate chain (no fixed-point iteration)
# ---------------------------------------------------------------------------


def bipartite_lcc(slot_author: np.ndarray, slot_comm: np.ndarray,
                  n_authors: int, n_comms: int) -> dict[str, Any]:
    """Largest connected component of the author x community bipartite graph.

    Returns the slot mask of the component holding the most AUTHORS, plus the
    author coverage of that component.  Union-find with path halving: the
    graph has tens of thousands of edges, so the loop is cheap and the result
    is exact and dependency-free.
    """

    parent = np.arange(n_authors + n_comms, dtype=np.int64)

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = int(parent[x])
        return x

    for a, c in zip(slot_author.tolist(), slot_comm.tolist()):
        ra, rc = find(int(a)), find(n_authors + int(c))
        if ra != rc:
            parent[ra] = rc
    roots = np.array([find(i) for i in range(n_authors + n_comms)],
                     dtype=np.int64)
    author_roots = roots[:n_authors]
    values, counts = np.unique(author_roots, return_counts=True)
    biggest = int(values[int(np.argmax(counts))])
    coverage = float(counts.max()) / max(1, n_authors)
    mask = author_roots[slot_author] == biggest
    return {"slot_mask": mask,
            "components": int(values.size),
            "lcc_authors": int(counts.max()),
            "lcc_author_coverage": coverage}


def build_chain_design(table: dict[str, Any], author_mask: np.ndarray, *,
                       n_min: int, support: int, vocab_mask: np.ndarray,
                       y_key: str = "wcq",
                       k_min: int = K_MIN) -> tuple[Design, dict[str, Any]]:
    """The X1b predicate chain, applied ONCE in the pinned order.

    (1) cells at n >= n_min, author in the cohort, community in the law
    vocabulary; (2) shared pairs — an (author, community) whose BOTH halves
    are eligible; (3) the community support floor: keep communities holding
    at least ``support`` authors with a shared pair; (4) keep authors with at
    least ``k_min`` SURVIVING shared communities; (5) keep the largest
    connected component.  No step is re-run after a later step bites — the
    registration forbids fixed-point iteration.
    """

    n_subs = int(table["n_subs"])
    step1 = ((table["cell_n"] >= n_min) & author_mask[table["cell_author"]]
             & vocab_mask[table["cell_comm"]])
    author = table["cell_author"][step1].astype(np.int64)
    comm = table["cell_comm"][step1].astype(np.int64)
    half = table["cell_half"][step1]
    n = table["cell_n"][step1].astype(np.float64)
    s = table[f"s_{y_key}"][step1]
    q = table[f"q_{y_key}"][step1]

    key = author * n_subs + comm
    is_e = half == 0
    key_e, key_l = key[is_e], key[~is_e]
    order_e = np.argsort(key_e, kind="stable")
    order_l = np.argsort(key_l, kind="stable")
    key_e_s, key_l_s = key_e[order_e], key_l[order_l]
    shared = np.intersect1d(key_e_s, key_l_s, assume_unique=True)
    n_step2 = int(shared.size)

    # (3) community support floor — authors with a shared pair, per community
    comm_of = shared % n_subs
    uniq_comm, comm_inv = np.unique(comm_of, return_inverse=True)
    comm_inv = comm_inv.reshape(-1)
    support_count = np.bincount(comm_inv, minlength=uniq_comm.size)
    shared = shared[np.isin(comm_of, uniq_comm[support_count >= support])]
    n_step3 = int(shared.size)

    # (4) authors with at least k_min SURVIVING shared communities
    author_of = shared // n_subs
    uniq_auth, auth_inv = np.unique(author_of, return_inverse=True)
    auth_inv = auth_inv.reshape(-1)
    k_count = np.bincount(auth_inv, minlength=uniq_auth.size)
    shared = shared[np.isin(author_of, uniq_auth[k_count >= k_min])]
    n_step4 = int(shared.size)

    # (5) the largest connected component of the bipartite graph
    author_codes, slot_author = np.unique(shared // n_subs,
                                          return_inverse=True)
    comm_codes, slot_comm = np.unique(shared % n_subs, return_inverse=True)
    slot_author = slot_author.reshape(-1)
    slot_comm = slot_comm.reshape(-1)
    lcc = bipartite_lcc(slot_author, slot_comm, int(author_codes.size),
                        int(comm_codes.size))
    shared = shared[lcc["slot_mask"]]
    n_step5 = int(shared.size)

    pos_e = order_e[np.searchsorted(key_e_s, shared)]
    pos_l = order_l[np.searchsorted(key_l_s, shared)]
    idx_e = np.flatnonzero(is_e)[pos_e]
    idx_l = np.flatnonzero(~is_e)[pos_l]

    author_codes, slot_author = np.unique(shared // n_subs,
                                          return_inverse=True)
    comm_codes, slot_comm = np.unique(shared % n_subs, return_inverse=True)
    slot_author = slot_author.reshape(-1).astype(np.int64)
    slot_comm = slot_comm.reshape(-1).astype(np.int64)
    design = Design(
        slot_author=slot_author, slot_comm=slot_comm,
        n_e=n[idx_e], n_l=n[idx_l], s_e=s[idx_e], s_l=s[idx_l],
        q_e=q[idx_e], q_l=q[idx_l],
        n_authors=int(author_codes.size), n_comms=int(comm_codes.size),
        author_codes=author_codes.astype(np.int64))

    per_comm = np.bincount(slot_comm, None, design.n_comms)
    chain = dict(design.summary())
    # NOTE: ``Design.summary`` publishes ``singleton_community_share`` as a
    # share of SLOTS; the planner's census table counts COMMUNITIES, so the
    # chain's own keys are written after the summary and win the clash.
    chain.update({
        "n_min": int(n_min), "support_floor": int(support),
        "k_min": int(k_min), "y_key": y_key,
        "step1_cells": int(step1.sum()),
        "step2_shared_pairs": n_step2,
        "step3_shared_pairs": n_step3,
        "step4_shared_pairs": n_step4,
        "step5_shared_pairs": n_step5,
        "components_before_lcc": int(lcc["components"]),
        "lcc_author_coverage": float(lcc["lcc_author_coverage"]),
        "authors": int(design.n_authors),
        "communities": int(design.n_comms),
        "shared_pairs": int(design.n_slots),
        "fill": float(design.n_slots
                      / max(1, design.n_authors * design.n_comms)),
        "authors_per_community_median": float(np.median(per_comm)),
        "singleton_communities": int(np.sum(per_comm == 1)),
        "singleton_community_share": float(np.mean(per_comm == 1)),
        "singleton_slot_share": float(np.mean(per_comm[slot_comm] == 1)),
    })
    return design, chain


# ---------------------------------------------------------------------------
# Stage 3 — THE REPAIR: exact two-way FE by alternating projections
# ---------------------------------------------------------------------------


def fe_residual(values: np.ndarray, slot_author: np.ndarray,
                slot_comm: np.ndarray, n_authors: int, n_comms: int, *,
                weights: np.ndarray | None = None, tol: float = FE_TOL,
                max_iter: int = FE_MAX_ITER) -> tuple[np.ndarray, int, float]:
    """Two-way fixed-effect residual of the cell means, ALTERNATING PROJECTIONS.

    One sweep is the within-transform demeaning by author followed by the
    within-transform demeaning by community.  The sweep is repeated until the
    maximum absolute change is at most ``tol``: the change measured is the
    community correction just applied AND the author correction the next sweep
    would apply, so on exit BOTH residual group means are at most ``tol`` in
    absolute value (the community means are exactly zero, having just been
    removed).  On a connected design the limit is the exact OLS residual from
    the author + community dummy space — X1's single double-centering is that
    limit only on a COMPLETE grid, which is the defect this repairs.

    ``weights`` carries cluster-bootstrap author multiplicities; with weights
    None every eligible cell counts once, which is the registration's pin.
    """

    v = np.asarray(values, dtype=np.float64).copy()
    if weights is None:
        a_den = np.bincount(slot_author, None, n_authors).astype(np.float64)
        c_den = np.bincount(slot_comm, None, n_comms).astype(np.float64)
    else:
        w = np.asarray(weights, dtype=np.float64)
        a_den = np.bincount(slot_author, w, n_authors)
        c_den = np.bincount(slot_comm, w, n_comms)
    a_safe = np.where(a_den > 0, a_den, 1.0)
    c_safe = np.where(c_den > 0, c_den, 1.0)

    def author_mean(x: np.ndarray) -> np.ndarray:
        num = (np.bincount(slot_author, x, n_authors) if weights is None
               else np.bincount(slot_author, x * weights, n_authors))
        return np.where(a_den > 0, num / a_safe, 0.0)

    def comm_mean(x: np.ndarray) -> np.ndarray:
        num = (np.bincount(slot_comm, x, n_comms) if weights is None
               else np.bincount(slot_comm, x * weights, n_comms))
        return np.where(c_den > 0, num / c_safe, 0.0)

    a_mean = author_mean(v)
    change = float("inf")
    for iteration in range(1, max_iter + 1):
        v -= a_mean[slot_author]
        c_mean = comm_mean(v)
        v -= c_mean[slot_comm]
        a_mean = author_mean(v)
        change = float(max(np.abs(a_mean).max(initial=0.0),
                           np.abs(c_mean).max(initial=0.0)))
        if change <= tol:
            return v, iteration, change
    raise RuntimeError(                            # pragma: no cover
        f"alternating projections did not converge in {max_iter} sweeps "
        f"(last change {change:.3e})")


def fe_pair(design: Design) -> tuple[np.ndarray, np.ndarray, dict[str, int]]:
    """The FE residual of both halves' cell means on the eligible grid."""

    sa, sc = design.slot_author, design.slot_comm
    A, C = design.n_authors, design.n_comms
    v_e, it_e, ch_e = fe_residual(design.mean_e, sa, sc, A, C)
    v_l, it_l, ch_l = fe_residual(design.mean_l, sa, sc, A, C)
    return v_e, v_l, {"sweeps_early": it_e, "sweeps_late": it_l,
                      "change_early": ch_e, "change_late": ch_l}


def fe_exactness(design: Design, v_e: np.ndarray,
                 v_l: np.ndarray) -> dict[str, float]:
    """The residual author and community means — zero to machine tolerance."""

    sa, sc = design.slot_author, design.slot_comm
    A, C = design.n_authors, design.n_comms
    ka = np.maximum(np.bincount(sa, None, A).astype(np.float64), 1.0)
    kc = np.maximum(np.bincount(sc, None, C).astype(np.float64), 1.0)
    out = {}
    for tag, v in (("early", v_e), ("late", v_l)):
        out[f"max_abs_author_mean_{tag}"] = float(
            np.abs(np.bincount(sa, v, A) / ka).max(initial=0.0))
        out[f"max_abs_community_mean_{tag}"] = float(
            np.abs(np.bincount(sc, v, C) / kc).max(initial=0.0))
    return out


# ---------------------------------------------------------------------------
# Stage 4 — the estimands on v (R, the budget), their null and their bootstrap
# ---------------------------------------------------------------------------


def permutation_null_fe(design: Design, b_perm: int, seed: int,
                        log: RunLog | None = None,
                        tag: str = "") -> dict[str, Any]:
    """The mechanism's own null, with the FULL pipeline recomputed per draw.

    Community labels are permuted WITHIN (author, half) among that author's
    eligible cells, independently in the two halves: the design is preserved
    exactly (same slots, same per-author cell counts, same cells per
    community).  The FE is then recomputed from scratch on every permutation —
    the registration's pin, and the reason the null is a null of the estimator
    and not only of the statistic.
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
            ve, _, _ = fe_residual(mean_e[pe[j]], sa, sc, A, C)
            vl, _, _ = fe_residual(mean_l[pl[j]], sa, sc, A, C)
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


def _bootstrap_replicate(design: Design, mult: np.ndarray
                         ) -> tuple[np.ndarray, np.ndarray, float]:
    """One cluster-bootstrap replicate: the FE recomputed on the resample.

    An author drawn m times contributes their slots m times.  Every copy of an
    author solves the same FE equation given the community effects, so the
    resampled two-way FE is exactly the WEIGHTED alternating projection with
    weight m on that author's slots.  Slots of undrawn authors carry weight 0
    and are dropped from the projection entirely.
    """

    sa, sc = design.slot_author, design.slot_comm
    keep = mult[sa] > 0
    sub_a = sa[keep]
    sub_c = sc[keep]
    ua, a_idx = np.unique(sub_a, return_inverse=True)
    uc, c_idx = np.unique(sub_c, return_inverse=True)
    a_idx = a_idx.reshape(-1)
    c_idx = c_idx.reshape(-1)
    w = mult[ua][a_idx]
    A, C = int(ua.size), int(uc.size)
    ve_sub, _, _ = fe_residual(design.mean_e[keep], a_idx, c_idx, A, C,
                               weights=w)
    vl_sub, _, _ = fe_residual(design.mean_l[keep], a_idx, c_idx, A, C,
                               weights=w)
    v_e = np.zeros(design.n_slots, dtype=np.float64)
    v_l = np.zeros(design.n_slots, dtype=np.float64)
    v_e[keep] = ve_sub
    v_l[keep] = vl_sub
    r_sub = per_author_correlations(ve_sub, vl_sub, a_idx, A)
    finite = np.isfinite(r_sub)
    w_auth = mult[ua]
    denom = float(w_auth[finite].sum())
    r_boot = (float((w_auth[finite] * r_sub[finite]).sum()) / denom
              if denom > 0 else float("nan"))
    return v_e, v_l, r_boot


def cluster_bootstrap_fe(design: Design, b_boot: int,
                         seed: int) -> dict[str, Any]:
    """Cluster bootstrap over AUTHORS, with the FE recomputed inside each draw.

    #85b: the zero reference must be bootstrap-stable, so nothing here is
    resampled from precomputed per-author statistics — every replicate rebuilds
    the projection on its own author multiset.
    """

    rng = np.random.default_rng(seed)
    A = design.n_authors
    draws = rng.integers(0, A, size=(b_boot, A))
    keys = ("author", "community", "community_unweighted", "interaction",
            "interaction_weighted", "residual")
    shares = {k: np.empty(b_boot) for k in keys}
    r_boot = np.empty(b_boot, dtype=np.float64)
    for b in range(b_boot):
        mult = np.bincount(draws[b], minlength=A).astype(np.float64)
        v_e, v_l, r = _bootstrap_replicate(design, mult)
        budget = variance_budget(design, v_e, v_l, mult=mult)
        for key in keys:
            shares[key][b] = budget[key]
        r_boot[b] = r
    return {
        "b_boot": int(b_boot),
        "r_ci": percentile_ci(r_boot),
        "r_boot_mean": float(np.nanmean(r_boot)),
        "shares_ci": {k: percentile_ci(v) for k, v in shares.items()},
        "shares_sd": {k: float(np.std(v, ddof=1)) for k, v in shares.items()},
        "shares_mean": {k: float(np.mean(v)) for k, v in shares.items()},
    }


def analyse_design_fe(design: Design, *, b_perm: int, b_boot: int,
                      seed_perm: int, seed_boot: int, tag: str,
                      log: RunLog | None = None,
                      with_inference: bool = True) -> dict[str, Any]:
    """One arm end to end under the repaired estimator."""

    v_e, v_l, sweeps = fe_pair(design)
    r_author = per_author_correlations(v_e, v_l, design.slot_author,
                                       design.n_authors)
    out: dict[str, Any] = {
        "tag": tag,
        "design": design.summary(),
        "fe": sweeps,
        "fe_exactness": fe_exactness(design, v_e, v_l),
        "R": float(np.nanmean(r_author)),
        "budget": variance_budget(design, v_e, v_l),
        "headroom": headroom_report(r_author),
    }
    if with_inference:
        out["null"] = permutation_null_fe(design, b_perm, seed_perm, log, tag)
        out["bootstrap"] = cluster_bootstrap_fe(design, b_boot, seed_boot)
    return out


def recover_shares_fe(design: Design) -> dict[str, float]:
    """The point estimands only — the per-replicate row of a synthetic block."""

    v_e, v_l, _ = fe_pair(design)
    budget = variance_budget(design, v_e, v_l)
    r = per_author_correlations(v_e, v_l, design.slot_author,
                                design.n_authors)
    budget["R"] = float(np.nanmean(r))
    return budget


def recover_shares_x1(design: Design) -> dict[str, float]:
    """X1's DOUBLE-CENTERED estimator on the same world — the repair's control."""

    sa, sc = design.slot_author, design.slot_comm
    A, C = design.n_authors, design.n_comms
    v_e = double_center(design.mean_e, sa, sc, A, C)
    v_l = double_center(design.mean_l, sa, sc, A, C)
    budget = variance_budget(design, v_e, v_l)
    r = per_author_correlations(v_e, v_l, sa, A)
    budget["R"] = float(np.nanmean(r))
    return budget


# ---------------------------------------------------------------------------
# Stage 5 — Part 0: the gate that failed must now pass
# ---------------------------------------------------------------------------


def synthetic_world_block(skeleton: Design, shares: dict[str, float],
                          name: str, seed: int, replicates: int, log: RunLog,
                          recover=recover_shares_fe) -> dict[str, Any]:
    """``replicates`` draws of one synthetic world, scored point-wise."""

    rows = []
    for rep in range(replicates):
        rng = np.random.default_rng(seed + 1000 * rep)
        world = synthetic_design(skeleton, shares, rng)
        rows.append(recover(world))
        log.event("synthetic_replicate", world=name, replicate=rep,
                  interaction=rows[-1]["interaction"], R=rows[-1]["R"])
    keys = ("author", "community", "community_unweighted", "interaction",
            "residual", "R")
    stats = {}
    for key in keys:
        values = np.array([row[key] for row in rows], dtype=np.float64)
        stats[key] = {
            "mean": float(values.mean()),
            "sd": float(values.std(ddof=1)) if values.size > 1 else 0.0,
            "min": float(values.min()), "max": float(values.max()),
            "values": [float(x) for x in values],
        }
    return {"world": name, "planted": dict(shares), "replicates": replicates,
            "stats": stats}


def synthetic_gate(skeleton: Design, b_perm: int, b_boot: int,
                   log: RunLog) -> dict[str, Any]:
    """Part 0.  Every clause is a precondition for every real number here."""

    log.event("part0_start", authors=skeleton.n_authors,
              communities=skeleton.n_comms, slots=skeleton.n_slots,
              replicates=N_SYNTH_REPLICATES)
    planted = synthetic_world_block(skeleton, PLANTED_SHARES, "planted",
                                    SEED_PART0, N_SYNTH_REPLICATES, log)
    null = synthetic_world_block(skeleton, NULL_SHARES, "null",
                                 SEED_PART0 + 7, N_SYNTH_REPLICATES, log)
    ablations = {
        "author_only": synthetic_world_block(
            skeleton, ABLATION_WORLDS["author_only"], "author_only",
            SEED_PART0 + 13, N_SYNTH_REPLICATES, log),
        "community_only": synthetic_world_block(
            skeleton, ABLATION_WORLDS["community_only"], "community_only",
            SEED_PART0 + 19, N_SYNTH_REPLICATES, log),
    }

    # --- clause 1-3: recovery of the three planted shares ------------------
    recovery: dict[str, Any] = {}
    for key, target in PLANTED_SHARES.items():
        stat = planted["stats"][key]
        tol = max(TOL_FLOOR, TOL_SD_MULT * stat["sd"])
        ok = abs(stat["mean"] - target) <= tol
        recovery[key] = {"planted": target, "recovered_mean": stat["mean"],
                         "replicate_sd": stat["sd"], "tolerance": tol,
                         "bias": stat["mean"] - target,
                         "status": "PASS" if ok else "FAIL"}
    recovery_pass = all(r["status"] == "PASS" for r in recovery.values())

    # --- clause 4-6 and 9: the null world, scored with full inference ------
    rng_world = np.random.default_rng(SEED_PART0 + 7)
    null_world = synthetic_design(skeleton, NULL_SHARES, rng_world)
    null_inference = analyse_design_fe(
        null_world, b_perm=b_perm, b_boot=b_boot, seed_perm=SEED_PERM + 101,
        seed_boot=SEED_BOOT + 101, tag="part0_null", log=log)
    share = float(null_inference["budget"]["interaction"])
    share_ci = null_inference["bootstrap"]["shares_ci"]["interaction"]
    share_band = null_inference["null"]["interaction_band"]
    r_point = float(null_inference["R"])
    r_band = null_inference["null"]["r_band"]
    ci_covers_zero = bool(share_ci[0] <= 0.0 <= share_ci[1])
    share_inside_band = bool(share_band[0] <= share <= share_band[1])
    r_inside = bool(r_band[0] <= r_point <= r_band[1])
    ci_covers_point = bool(share_ci[0] <= share <= share_ci[1])
    honesty_pass = ci_covers_zero and share_inside_band and r_inside

    # --- clause 7-8: ablation leakage --------------------------------------
    ablation_clauses = {}
    for name, block in ablations.items():
        leak = abs(block["stats"]["interaction"]["mean"])
        ablation_clauses[name] = {
            "leakage": leak, "maximum": ABLATION_LEAK_MAX,
            "R_leakage": block["stats"]["R"]["mean"],
            "status": "PASS" if leak < ABLATION_LEAK_MAX else "FAIL"}
    ablation_pass = all(c["status"] == "PASS"
                        for c in ablation_clauses.values())

    # --- the planted world scored with full inference (reference) ----------
    rng_planted = np.random.default_rng(SEED_PART0)
    planted_world = synthetic_design(skeleton, PLANTED_SHARES, rng_planted)
    planted_inference = analyse_design_fe(
        planted_world, b_perm=b_perm, b_boot=b_boot, seed_perm=SEED_PERM + 103,
        seed_boot=SEED_BOOT + 103, tag="part0_planted", log=log)

    clauses = {
        "recovery — author main within max(0.01, 3 x replicate sd)":
            recovery["author"]["status"],
        "recovery — community main within max(0.01, 3 x replicate sd)":
            recovery["community"]["status"],
        "recovery — interaction within max(0.01, 3 x replicate sd)":
            recovery["interaction"]["status"],
        "null world — interaction share CI covers 0":
            "PASS" if ci_covers_zero else "FAIL",
        "null world — interaction point inside its permutation band":
            "PASS" if share_inside_band else "FAIL",
        "null world — R inside its permutation band":
            "PASS" if r_inside else "FAIL",
        "ablation — author-only leakage < 0.005 on the interaction share":
            ablation_clauses["author_only"]["status"],
        "ablation — community-only leakage < 0.005 on the interaction share":
            ablation_clauses["community_only"]["status"],
        "#85b bootstrap-zero — the null world's cluster-bootstrap CI covers 0":
            "PASS" if ci_covers_zero else "FAIL",
    }
    status = "PASS" if all(v == "PASS" for v in clauses.values()) else "FAIL"
    out = {
        "status": status,
        "clauses": clauses,
        "n_clauses": len(clauses),
        "n_clauses_passed": sum(1 for v in clauses.values() if v == "PASS"),
        "recovery": recovery,
        "recovery_status": "PASS" if recovery_pass else "FAIL",
        "honesty_status": "PASS" if honesty_pass else "FAIL",
        "ablation_status": "PASS" if ablation_pass else "FAIL",
        "ablation_clauses": ablation_clauses,
        "honesty": {
            "interaction_share": share,
            "interaction_ci": share_ci,
            "ci_covers_zero": ci_covers_zero,
            "ci_covers_point": ci_covers_point,
            "interaction_band": share_band,
            "interaction_inside_band": share_inside_band,
            "author_share": null_inference["budget"]["author"],
            "community_share": null_inference["budget"]["community"],
            "R": r_point, "r_ci": null_inference["bootstrap"]["r_ci"],
            "r_band": r_band, "r_inside_band": r_inside,
            "design": null_inference["design"],
            "fe": null_inference["fe"],
            "fe_exactness": null_inference["fe_exactness"],
        },
        "planted_world_inference": {
            "interaction_share": planted_inference["budget"]["interaction"],
            "interaction_ci":
                planted_inference["bootstrap"]["shares_ci"]["interaction"],
            "interaction_band": planted_inference["null"]["interaction_band"],
            "R": planted_inference["R"],
            "r_ci": planted_inference["bootstrap"]["r_ci"],
            "r_band": planted_inference["null"]["r_band"],
            "headroom": planted_inference["headroom"],
            "fe": planted_inference["fe"],
            "fe_exactness": planted_inference["fe_exactness"],
        },
        "null_world_headroom": null_inference["headroom"],
        "planted_block": planted,
        "null_block": null,
        "ablations": ablations,
        "tolerance_rule": (f"max({TOL_FLOOR}, {TOL_SD_MULT} x replicate sd) "
                           f"over {N_SYNTH_REPLICATES} replicates"),
    }
    log.event("part0_done", status=status,
              passed=out["n_clauses_passed"], of=out["n_clauses"])
    return out


# ---------------------------------------------------------------------------
# Stage 6 — the repair demonstration: X1 vs X1b on the SAME null world
# ---------------------------------------------------------------------------


def estimator_comparison(x1b_skeleton: Design, x1_skeleton: Design,
                         b_perm: int, b_boot: int,
                         log: RunLog) -> dict[str, Any]:
    """The 2x2 of the two repairs, on the SAME synthetic null world draws.

    Rows: X1's registered skeleton (raw community universe, no support floor)
    and the X1b skeleton (law vocabulary + support floor s = 5).  Columns:
    X1's double-centering and X1b's exact alternating-projection FE.  Every
    cell is the NULL world — interaction planted at exactly 0.0000 — under the
    same seed, so the four numbers are directly comparable and isolate what
    the design repair buys from what the estimator repair buys.
    """

    grid: dict[str, Any] = {}
    for skel_name, skel in (("x1_registered_skeleton", x1_skeleton),
                            ("x1b_repaired_skeleton", x1b_skeleton)):
        for est_name, recover in (("x1_double_centering", recover_shares_x1),
                                  ("x1b_exact_fe", recover_shares_fe)):
            block = synthetic_world_block(
                skel, NULL_SHARES, f"{skel_name}/{est_name}",
                SEED_PART0 + 7, N_SYNTH_REPLICATES, log, recover=recover)
            grid[f"{skel_name}|{est_name}"] = {
                "skeleton": skel_name, "estimator": est_name,
                "authors": int(skel.n_authors),
                "communities": int(skel.n_comms),
                "slots": int(skel.n_slots),
                "interaction_mean": block["stats"]["interaction"]["mean"],
                "interaction_sd": block["stats"]["interaction"]["sd"],
                "R_mean": block["stats"]["R"]["mean"],
                "R_sd": block["stats"]["R"]["sd"],
            }
            log.event("estimator_comparison_cell", cell=f"{skel_name}|"
                      f"{est_name}",
                      interaction=grid[f"{skel_name}|{est_name}"]
                      ["interaction_mean"])

    # The scored null world under BOTH estimators, with full inference, so the
    # CI and the band are on the record for the old estimator too.
    rng_world = np.random.default_rng(SEED_PART0 + 7)
    null_world = synthetic_design(x1b_skeleton, NULL_SHARES, rng_world)
    sa, sc = null_world.slot_author, null_world.slot_comm
    A, C = null_world.n_authors, null_world.n_comms
    v_e = double_center(null_world.mean_e, sa, sc, A, C)
    v_l = double_center(null_world.mean_l, sa, sc, A, C)
    budget = variance_budget(null_world, v_e, v_l)
    r_author = per_author_correlations(v_e, v_l, sa, A)
    old_null = X1.permutation_null(null_world, b_perm, SEED_PERM + 101, log,
                                   "x1_estimator_on_x1b_null")
    old_boot = X1.cluster_bootstrap(null_world, v_e, v_l, r_author, b_boot,
                                    SEED_BOOT + 101)
    scored = {
        "x1_double_centering": {
            "interaction_share": budget["interaction"],
            "interaction_ci": old_boot["shares_ci"]["interaction"],
            "interaction_band": old_null["interaction_band"],
            "ci_covers_zero": bool(
                old_boot["shares_ci"]["interaction"][0] <= 0.0
                <= old_boot["shares_ci"]["interaction"][1]),
            "ci_covers_point": bool(
                old_boot["shares_ci"]["interaction"][0]
                <= budget["interaction"]
                <= old_boot["shares_ci"]["interaction"][1]),
            "R": float(np.nanmean(r_author)),
            "r_ci": old_boot["r_ci"], "r_band": old_null["r_band"],
        },
    }
    return {"grid": grid, "scored_null_world": scored,
            "note": ("all four grid cells are the SAME null world "
                     "(interaction planted at exactly 0.0000) under the same "
                     "seed; no real y enters this table")}


# ---------------------------------------------------------------------------
# Stage 7 — classification and leans (inherited from X1 verbatim)
# ---------------------------------------------------------------------------


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
    return X1.evaluate_leans(primary, replication_cell, primary_cell)


# ---------------------------------------------------------------------------
# Stage 8 — the diagnosis (every number read off the gate artifacts)
# ---------------------------------------------------------------------------


def build_diagnosis(part0: dict[str, Any], comparison: dict[str, Any],
                    chain: dict[str, Any],
                    composition: dict[str, Any]) -> list[str]:
    hon = part0["honesty"]
    grid = comparison["grid"]
    old_here = grid["x1b_repaired_skeleton|x1_double_centering"]
    new_here = grid["x1b_repaired_skeleton|x1b_exact_fe"]
    old_there = grid["x1_registered_skeleton|x1_double_centering"]
    new_there = grid["x1_registered_skeleton|x1b_exact_fe"]
    abl = part0["ablation_clauses"]
    rec = part0["recovery"]
    return [
        (f"**The estimator repair works, and it is the whole of the "
         f"registered repair.** On the SAME null world — interaction planted "
         f"at exactly 0.0000 — X1's double-centering reads "
         f"{_pct(old_here['interaction_mean'])} and R = "
         f"{_pct(old_here['R_mean'])}, while the exact alternating-projection "
         f"FE reads {_pct(new_here['interaction_mean'])} +- "
         f"{_pct(new_here['interaction_sd'])} and R = "
         f"{_pct(new_here['R_mean'])}. The scored replicate's "
         f"cluster-bootstrap CI is {fmt_ci(hon['interaction_ci'])} — it covers "
         f"0 and it covers its own point estimate — against the old "
         f"estimator's "
         f"{fmt_ci(comparison['scored_null_world']['x1_double_centering']['interaction_ci'])} "
         f"on the identical world."),
        (f"**The design repair alone would not have sufficed, and the "
         f"estimator repair alone would have.** On X1's own registered "
         f"skeleton the FE already reads "
         f"{_pct(new_there['interaction_mean'])} where double-centering read "
         f"{_pct(old_there['interaction_mean'])}; moving to the "
         f"support-conditioned skeleton without changing the estimator only "
         f"takes double-centering from {_pct(old_there['interaction_mean'])} "
         f"to {_pct(old_here['interaction_mean'])}. Support conditioning is "
         f"still worth having — it is what makes the mains estimable and the "
         f"graph connected — but the leak was the projection, not the grid."),
        (f"**Both ablations are clean.** With ONLY an author main planted the "
         f"interaction share reads {_pct(abl['author_only']['leakage'])} "
         f"(R = {_pct(abl['author_only']['R_leakage'])}); with ONLY a "
         f"community main planted it reads "
         f"{_pct(abl['community_only']['leakage'])} "
         f"(R = {_pct(abl['community_only']['R_leakage'])}). Both sit far "
         f"below the 0.005 clause. The residue that X1 localized — a "
         f"per-community term of the author main surviving the double "
         f"centering — is removed exactly by the projection."),
        (f"**What still fails is the object the registration did NOT repair.** "
         f"The author main share is estimated PRE-FE, from the cross-half "
         f"covariance of author half-means, exactly as in X1. On the planted "
         f"world it recovers {_pct(rec['author']['recovered_mean'])} for a "
         f"planted {_pct(rec['author']['planted'])} — a bias of "
         f"{_pct(rec['author']['bias'])} against a tolerance of "
         f"{_pct(rec['author']['tolerance'])}. The community main recovers "
         f"{_pct(rec['community']['recovered_mean'])} for "
         f"{_pct(rec['community']['planted'])}, inside its (wider) tolerance "
         f"of {_pct(rec['community']['tolerance'])}."),
        (f"**The author-main bias is a COMPOSITION term, and it is "
         f"predictable from the design alone.** An author's half-mean is not "
         f"a_u: it is a_u plus that author's own average of the community "
         f"main and of the interaction over the communities they occupy. That "
         f"average is the SAME in both halves up to cell-size reweighting, so "
         f"the cross-half covariance keeps it. The realized design has "
         f"E[1/k_u] = {fmt(composition['mean_inverse_k'], 4)} over "
         f"{chain['authors']:,} authors, which predicts a bias of "
         f"{_pct(composition['predicted_author_bias'])} against the observed "
         f"{_pct(rec['author']['bias'])}. The support floor raised the "
         f"authors per community from X1's 2.0 to "
         f"{fmt(chain['authors_per_community_median'], 1)} and thereby fixed "
         f"the community main; it does not raise the communities per author, "
         f"so it cannot fix the author main."),
    ]


def build_defect_candidates(part0: dict[str, Any], chain: dict[str, Any],
                            composition: dict[str, Any]) -> list[str]:
    """What a re-registration would have to fix — nothing below was run."""

    rec = part0["recovery"]
    return [
        ("**The main-share estimators are MARGINAL, not main, and the gate "
         "is right to say so.** The cross-half covariance of author "
         "half-means estimates Var(a) PLUS the author's own composition "
         "average of everything else that is persistent — the community main "
         "and the interaction. Its target is therefore not the planted "
         "author share, and no amount of support conditioning moves it, "
         "because the contaminating divisor is the number of communities per "
         "AUTHOR (median "
         f"{fmt(chain['shared_communities_per_author_median'], 1)}, "
         f"E[1/k_u] = {fmt(composition['mean_inverse_k'], 4)}), not the "
         "number of authors per community. The obvious candidates are to "
         "estimate the mains from the SAME two-way projection that now "
         "carries the interaction (author and community effect variances "
         "read off the fitted effects with their sampling variance removed), "
         "or to re-state the registered clause so that the mains are scored "
         "against their own marginal targets rather than against the planted "
         "variance components. Neither was run here."),
        ("**The registration repaired the routing statistic and left the "
         "co-reported ones under the same gate.** The cells route on the "
         "interaction share and R, and BOTH now behave exactly: the null "
         "world reads "
         f"{_pct(part0['honesty']['interaction_share'])} with a CI covering "
         f"0 and R = {_pct(part0['honesty']['R'])} inside its band. The gate "
         "nevertheless fails, because the recovery clause covers all three "
         "planted shares. That is a defensible clause — a budget that "
         "over-reads its largest component is not a budget — but a planner "
         "may wish to separate ROUTING clauses from DESCRIPTIVE ones so that "
         "a descriptive bias downgrades a co-reported number instead of "
         "stopping the leg."),
        ("**The interaction estimator is slightly CONSERVATIVE by "
         "construction, and the amount is computable.** The two-way "
         "projection removes A + C - 1 dimensions from M cells, so a planted "
         "interaction that is white across cells loses that fraction of "
         "itself: here "
         f"{chain['authors']:,} + {chain['communities']:,} - 1 of "
         f"{chain['shared_pairs']:,}, i.e. a retained fraction of "
         f"{fmt(composition['fe_retained_fraction'], 4)}, which predicts "
         f"{_pct(composition['predicted_interaction'])} for a planted "
         f"0.0200 against the observed "
         f"{_pct(rec['interaction']['recovered_mean'])}. A future "
         "registration can either correct for the projection's degrees of "
         "freedom or record the estimand as a LOWER bound. Nothing was "
         "corrected here."),
    ]


def composition_diagnostics(design: Design) -> dict[str, Any]:
    """Design-only quantities that predict the two biases the gate measured."""

    k = np.bincount(design.slot_author, None,
                    design.n_authors).astype(np.float64)
    m = np.bincount(design.slot_comm, None,
                    design.n_comms).astype(np.float64)
    mean_inv_k = float(np.mean(1.0 / np.maximum(k, 1.0)))
    mean_inv_m = float(np.mean(1.0 / np.maximum(m, 1.0)))
    rank = design.n_authors + design.n_comms - 1
    retained = max(0.0, (design.n_slots - rank) / max(1, design.n_slots))
    return {
        "mean_inverse_k": mean_inv_k,
        "mean_inverse_m": mean_inv_m,
        "predicted_author_bias": mean_inv_k * (PLANTED_SHARES["community"]
                                               + PLANTED_SHARES["interaction"]),
        "fe_rank_removed": int(rank),
        "fe_retained_fraction": retained,
        "predicted_interaction": retained * PLANTED_SHARES["interaction"],
    }


# ---------------------------------------------------------------------------
# Stage 9 — the report (rule 24: every table generated from the artifacts)
# ---------------------------------------------------------------------------


BOUNDARIES = (
    "**Metadata only, expression VOLUME and not content (permanent).** The "
    "only text-derived quantity in this leg is `word_count_quoteless`, the "
    "author's own-word count per comment. No body was read, no topic, no "
    "style, no sentiment. Every claim here would have been about HOW MUCH is "
    "written in a venue, never about WHAT is written.",
    "**The response-operator projection caution.** Profile persistence is ONE "
    "static projection of crossing #2's condition-response operator R_v. A "
    "null would be a statement about this projection at this resolution, not "
    "about the operator; a detection would be a lower bound on it.",
    "**No psychological naming.** Verbosity is a technical expression-volume "
    "object. Nothing here is a trait, a state, a disposition or a preference, "
    "and the leg is label-free: `author_profiles.csv` was never opened.",
    "**EXPLORATORY, corpus-level.** No person-level claim is licensed. The "
    "per-author correlations exist only as the population of a mean — which "
    "is the #85 restatement of the #84 headroom clause: the bounded object is "
    "the MEAN over thousands of authors, never the per-author correlation.",
    "**Cohort composition.** The disjoint cohort is TYPOLOGY-ENRICHED by "
    "construction (PANDORA's non-Big5 authors are MBTI-labelled users), so it "
    "is a platform sample with a selection, not a population sample.",
    "**The analysis universe is WELL-SHARED VENUES by construction (new in "
    "X1b).** The community universe is the law vocabulary (1,443 communities "
    "at floor 89) and the eligible grid carries a cross-author support floor "
    "of five authors per community. Whatever this design licenses, it "
    "licenses about venues that many cohort authors share — not about the "
    "long tail of small or private communities, which the chain removes by "
    "construction. The support conditioning is a PRIMARY design parameter "
    "(#85c), not a sensitivity.",
)


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []

    def add(text: str = "") -> None:
        lines.append(text)

    verdict = payload["verdict"]
    config = payload["config"]
    gate = payload["part0"]

    add("# SUICA M4-X1b — the venue response, repaired design and exact "
        "estimator")
    add()
    add(f"Run {config['run_utc']} · registration "
        "`docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md` (X1b, commit 0f8e43e) "
        f"· seed {config['seed']} · B_perm {config['b_perm']} · "
        f"B_boot {config['b_boot']} · runtime "
        f"{fmt(payload['runtime_s'], 1)} s.")
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

    add("## Anchors — the inherited census (#78, BLOCKING)")
    add()
    add("| quantity (exact predicate) | registered | observed | status |")
    add("|---|---|---|---|")
    for key, pin in payload["census"]["pins"].items():
        add(f"| {key} | {fmt(pin['registered'])} | {fmt(pin['observed'])} | "
            f"{pin['status']} |")
    add()
    add("Everything above is read from X1's committed cell cache, whose "
        "17,640,062-row single pass is the only time the comments file was "
        "touched in this line. No text body, no label file.")
    add()

    add("## The predicate chain — reproduced from the planner's census (#78, "
        "BLOCKING)")
    add()
    add("The chain runs ONCE in the pinned order, with no fixed-point "
        "iteration: (1) cells at n ≥ 10 comments, disjoint authors, law "
        "communities; (2) shared pairs, both halves eligible; (3) the "
        "community support floor of s authors holding a shared pair; "
        "(4) authors with ≥ 3 surviving shared communities; (5) the largest "
        "connected component.")
    add()
    add("| s | authors | communities | shared pairs | fill | median authors "
        "per community | singleton communities | LCC author coverage |")
    add("|---|---|---|---|---|---|---|---|")
    for key in sorted(payload["chain_census"], key=int):
        row = payload["chain_census"][key]
        add(f"| {key}{' (PRIMARY)' if int(key) == S_PRIMARY else ''} | "
            f"{row['authors']:,} | {row['communities']:,} | "
            f"{row['shared_pairs']:,} | {fmt(row['fill'], 4)} | "
            f"{fmt(row['authors_per_community_median'], 1)} | "
            f"{row['singleton_communities']} "
            f"({_pct(row['singleton_community_share'])}) | "
            f"{fmt(row['lcc_author_coverage'], 3)} |")
    add()
    add("| s | registered authors | registered communities | registered "
        "shared pairs | all three exact |")
    add("|---|---|---|---|---|")
    for key in sorted(payload["chain_anchor"]["pins_by_s"], key=int):
        row = payload["chain_anchor"]["pins_by_s"][key]
        add(f"| {key} | {row['authors']:,} | {row['communities']:,} | "
            f"{row['shared_pairs']:,} | {row['status']} |")
    add()
    prim = payload["chain_census"][str(S_PRIMARY)]
    add(f"Attrition through the chain at the primary floor (s = {S_PRIMARY}): "
        f"{prim['step1_cells']:,} eligible cells → "
        f"{prim['step2_shared_pairs']:,} shared pairs → "
        f"{prim['step3_shared_pairs']:,} after the support floor → "
        f"{prim['step4_shared_pairs']:,} after the k ≥ 3 author floor → "
        f"{prim['step5_shared_pairs']:,} in the largest connected component. "
        f"The graph was already connected before step 5 "
        f"({prim['components_before_lcc']} component(s), author coverage "
        f"{fmt(prim['lcc_author_coverage'], 3)}), which is what makes the "
        f"alternating projection's exactness argument valid here.")
    add()
    add("Non-gating cross-checks that the planner's census table also "
        "publishes:")
    add()
    add("| cross-check | published | observed | agrees |")
    add("|---|---|---|---|")
    for key, row in payload["chain_crosschecks"].items():
        add(f"| {key} | {row['expected']} | {row['observed']} | "
            f"{'yes' if row['agrees'] else 'NO'} |")
    add()

    add("## Part 0 — the gate that had to pass (#76/#85; A1 stop on failure)")
    add()
    add("The battery is the one that stopped X1, re-run on the X1b skeleton: "
        "the real incidence carries WHOLLY SYNTHETIC y, and no real y enters "
        "Part 0 at any point. Every clause below had to pass before a single "
        "corpus number could be computed.")
    add()
    add(f"Tolerance rule: {gate['tolerance_rule']}. The floor of {TOL_FLOOR} "
        f"of total variance is half the width of the registration's own "
        f"RESPONSE_TRACE / IDIOSYNCRATIC_RESPONSE boundary at {TRACE_MAX}.")
    add()
    add("| # | clause | status |")
    add("|---|---|---|")
    for i, (name, status) in enumerate(gate["clauses"].items(), start=1):
        mark = status if status == "PASS" else f"**{status}**"
        add(f"| {i} | {name} | {mark} |")
    add()
    add(f"Part 0 status: **{gate['status']}** "
        f"({gate['n_clauses_passed']} of {gate['n_clauses']} clauses pass).")
    add()
    add("### Recovery on the planted world")
    add()
    add("| planted share | planted | recovered (mean of "
        f"{gate['planted_block']['replicates']}) | replicate sd | tolerance | "
        "bias | status |")
    add("|---|---|---|---|---|---|---|")
    for key, row in gate["recovery"].items():
        add(f"| {key} | {_pct(row['planted'])} | "
            f"{_pct(row['recovered_mean'])} | {_pct(row['replicate_sd'])} | "
            f"{_pct(row['tolerance'])} | {_pct(row['bias'])} | "
            f"{row['status']} |")
    add()
    add("### The null world, scored with the full pipeline")
    add()
    hon = gate["honesty"]
    add("| null-world clause (nothing planted in the interaction) | value |")
    add("|---|---|")
    add(f"| interaction share (planted 0.0000) "
        f"| {_pct(hon['interaction_share'])} |")
    add(f"| cluster-bootstrap CI (FE recomputed in every replicate) "
        f"| {fmt_ci(hon['interaction_ci'])} |")
    add(f"| CI covers 0 (#85b, the bootstrap-zero clause) "
        f"| {'yes' if hon['ci_covers_zero'] else '**NO**'} |")
    add(f"| CI covers its own point estimate "
        f"| {'yes' if hon['ci_covers_point'] else '**NO**'} |")
    add(f"| permutation band for the share "
        f"| {fmt_ci(hon['interaction_band'])} |")
    add(f"| share inside its own permutation band "
        f"| {'yes' if hon['interaction_inside_band'] else '**NO**'} |")
    add(f"| R | {_pct(hon['R'])} |")
    add(f"| R cluster-bootstrap CI | {fmt_ci(hon['r_ci'])} |")
    add(f"| permutation band for R | {fmt_ci(hon['r_band'])} |")
    add(f"| R inside band | {'yes' if hon['r_inside_band'] else '**NO**'} |")
    add(f"| author main recovered (planted 0.3000) "
        f"| {_pct(hon['author_share'])} |")
    add(f"| community main recovered (planted 0.0800) "
        f"| {_pct(hon['community_share'])} |")
    add()
    add("### Every synthetic world, point-wise")
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
    add("| ablation clause | leakage on the interaction share | maximum | "
        "R leakage | status |")
    add("|---|---|---|---|---|")
    for name, row in gate["ablation_clauses"].items():
        add(f"| {name} | {_pct(row['leakage'])} | {_pct(row['maximum'])} | "
            f"{_pct(row['R_leakage'])} | {row['status']} |")
    add()
    add("### The alternating projection, verified")
    add()
    add("| quantity | early half | late half |")
    add("|---|---|---|")
    fe_null = hon["fe"]
    ex = hon["fe_exactness"]
    add(f"| sweeps to convergence | {fe_null['sweeps_early']} | "
        f"{fe_null['sweeps_late']} |")
    add(f"| final max absolute change | {fe_null['change_early']:.3e} | "
        f"{fe_null['change_late']:.3e} |")
    add(f"| max abs residual AUTHOR mean | "
        f"{ex['max_abs_author_mean_early']:.3e} | "
        f"{ex['max_abs_author_mean_late']:.3e} |")
    add(f"| max abs residual COMMUNITY mean | "
        f"{ex['max_abs_community_mean_early']:.3e} | "
        f"{ex['max_abs_community_mean_late']:.3e} |")
    add()
    add("Both mains are removed to machine tolerance on the realized, "
        "incomplete grid — which is precisely what X1's single double-"
        "centering could not do.")
    add()

    _write_comparison(add, payload)
    _write_headroom(add, payload)

    if payload.get("diagnosis"):
        add("## What Part 0 localizes")
        add()
        for item in payload["diagnosis"]:
            add(f"- {item}")
        add()

    if payload.get("arms"):
        _write_arm_sections(add, payload)
    else:
        _write_unscored(add, payload)

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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_comparison(add, payload: dict[str, Any]) -> None:
    comp = payload["comparison"]
    add("## The repair, demonstrated: X1 versus X1b on the SAME null world")
    add()
    add("Every cell below is the NULL world — the interaction planted at "
        "exactly 0.0000 — drawn under the same seed on the named skeleton and "
        "scored by the named estimator, 8 replicates. A correct estimator "
        "reads 0.0000 in all of them.")
    add()
    add("| skeleton | estimator | authors × communities (slots) | interaction "
        "share (mean ± sd) | R (mean ± sd) |")
    add("|---|---|---|---|---|")
    for key in ("x1_registered_skeleton|x1_double_centering",
                "x1_registered_skeleton|x1b_exact_fe",
                "x1b_repaired_skeleton|x1_double_centering",
                "x1b_repaired_skeleton|x1b_exact_fe"):
        row = comp["grid"][key]
        add(f"| {row['skeleton']} | {row['estimator']} | "
            f"{row['authors']:,} × {row['communities']:,} "
            f"({row['slots']:,}) | {_pct(row['interaction_mean'])} ± "
            f"{_pct(row['interaction_sd'])} | {_pct(row['R_mean'])} ± "
            f"{_pct(row['R_sd'])} |")
    add()
    old = comp["scored_null_world"]["x1_double_centering"]
    new = payload["part0"]["honesty"]
    add("On the single scored replicate of that null world, with the full "
        "inference machinery on both sides:")
    add()
    add("| quantity | X1 (double-centering) | X1b (exact FE) |")
    add("|---|---|---|")
    add(f"| interaction share (planted 0.0000) | "
        f"{_pct(old['interaction_share'])} | "
        f"{_pct(new['interaction_share'])} |")
    add(f"| cluster-bootstrap CI | {fmt_ci(old['interaction_ci'])} | "
        f"{fmt_ci(new['interaction_ci'])} |")
    add(f"| CI covers 0 | {'yes' if old['ci_covers_zero'] else '**NO**'} | "
        f"{'yes' if new['ci_covers_zero'] else '**NO**'} |")
    add(f"| CI covers its own point | "
        f"{'yes' if old['ci_covers_point'] else '**NO**'} | "
        f"{'yes' if new['ci_covers_point'] else '**NO**'} |")
    add(f"| permutation band for the share | "
        f"{fmt_ci(old['interaction_band'])} | "
        f"{fmt_ci(new['interaction_band'])} |")
    add(f"| R | {_pct(old['R'])} | {_pct(new['R'])} |")
    add(f"| permutation band for R | {fmt_ci(old['r_band'])} | "
        f"{fmt_ci(new['r_band'])} |")
    add()


def _write_headroom(add, payload: dict[str, Any]) -> None:
    gate = payload["part0"]
    head = gate["planted_world_inference"]["headroom"]
    null_head = gate["null_world_headroom"]
    add("## Headroom (#84 as restated by #85) — SYNTHETIC, not a corpus "
        "reading")
    add()
    add("The clause is about the MEAN over thousands of authors, not about "
        "the per-author correlation: at k_min = 3 a Pearson correlation over "
        "three points reaches ±1 whenever three points happen to line up, so "
        "saturation in the per-author distribution is EXPECTED and is not a "
        "ceiling on the estimand. The realized distributions on the two Part 0 "
        "worlds are reported so the statement is a number and not an "
        "assertion.")
    add()
    add("| quantile | planted world | null world |")
    add("|---|---|---|")
    for key in head["quantiles"]:
        add(f"| {key} | {_pct(head['quantiles'][key])} | "
            f"{_pct(null_head['quantiles'][key])} |")
    add()
    add(f"Planted world: {head['authors_scored']:,} authors scored, "
        f"{head['authors_undefined']:,} undefined; mean {_pct(head['mean'])}, "
        f"sd {_pct(head['sd'])}; {_pct(head['share_above_0.99'])} above 0.99. "
        f"Null world: mean {_pct(null_head['mean'])}, sd "
        f"{_pct(null_head['sd'])}; {_pct(null_head['share_above_0.99'])} above "
        f"0.99, {_pct(null_head['share_positive'])} positive. The MEAN "
        "separates the two worlds cleanly "
        f"({_pct(head['mean'])} against {_pct(null_head['mean'])}) while the "
        "per-author tails do not — which is the whole content of the "
        "restatement.")
    add()


def _write_unscored(add, payload: dict[str, Any]) -> None:
    add("## No real arm was run")
    add()
    add("Part 0 did not pass, so the A1 stop fired BEFORE any real estimand "
        "was computed. No corpus value of R, of the variance budget or of the "
        "headroom distribution exists in this leg's artifacts, and none is "
        "reported here. The chain census above is design arithmetic that the "
        "registration had already published; it is not an estimand.")
    add()
    add("The registered cells and leans are therefore UNSCORED. "
        "`NO_REPRODUCIBLE_RESPONSE` is not the outcome either: the leg "
        "reached no reading of crossing #2 at all, in either direction.")
    add()
    add("| registered object | value | outcome |")
    add("|---|---|---|")
    add(f"| cell 1 {CELL_NO_RESPONSE} | R inside band AND interaction share "
        "CI includes 0 | UNSCORED |")
    add(f"| cell 2 {CELL_TRACE} | detected, share < {TRACE_MAX} | UNSCORED |")
    add(f"| cell 3 {CELL_IDIOSYNCRATIC} | share in [{TRACE_MAX}, "
        f"{IDIOSYNCRATIC_MAX}] | UNSCORED |")
    add(f"| cell 4 {CELL_MAJOR} | share > {IDIOSYNCRATIC_MAX} | UNSCORED |")
    add(f"| lean: R | ({LEAN_R[0]}, {LEAN_R[1]}] | UNSCORED |")
    add(f"| lean: interaction share | ({LEAN_INTERACTION[0]}, "
        f"{LEAN_INTERACTION[1]}] | UNSCORED |")
    add(f"| lean: author main | [{LEAN_AUTHOR_MAIN[0]}, "
        f"{LEAN_AUTHOR_MAIN[1]}] | UNSCORED |")
    add(f"| lean: community main | [{LEAN_COMMUNITY_MAIN[0]}, "
        f"{LEAN_COMMUNITY_MAIN[1]}] | UNSCORED |")
    add("| lean: Big5 replication in the primary cell | same cell | UNSCORED "
        "(no cell was reached, so no #73 flag exists) |")
    add()
    add("### The four-share budget, per arm")
    add()
    add("| arm | author main | community main | interaction | residual | "
        "R [CI, band] | cell | #73 |")
    add("|---|---|---|---|---|---|---|---|")
    for key, row in payload["arm_designs"].items():
        add(f"| {row['label']} | UNSCORED | UNSCORED | UNSCORED | UNSCORED | "
            f"UNSCORED | UNSCORED | none (no cell exists) |")
    add()
    add("### The arm designs that were built and not scored")
    add()
    add("| arm | eligible authors | communities | shared pairs | comments | "
        "median shared communities | median authors per community | "
        "singleton communities | LCC coverage | #73 |")
    add("|---|---|---|---|---|---|---|---|---|---|")
    for key, row in payload["arm_designs"].items():
        add(f"| {row['label']} | {row['authors']:,} | "
            f"{row['communities']:,} | {row['shared_pairs']:,} | "
            f"{row['comments']:,} | "
            f"{fmt(row['shared_communities_per_author_median'], 1)} | "
            f"{fmt(row['authors_per_community_median'], 1)} | "
            f"{row['singleton_communities']} | "
            f"{fmt(row['lcc_author_coverage'], 3)} | "
            f"{payload['flags_73'].get(key, 'none (no cell exists)')} |")
    add()
    add("Design counts only — no y was read into any estimand. "
        f"{payload['big5_power']['sentence']}")
    add()
    if payload.get("defect_candidates"):
        add("### Defect candidates recorded for the planner")
        add()
        add("Executor candidates, not registered content, and nothing below "
            "was run:")
        add()
        for item in payload["defect_candidates"]:
            add(f"- {item}")
        add()


def _write_arm_sections(add, payload: dict[str, Any]) -> None:  # pragma: no cover
    """The scored path — reached only when Part 0 passes."""

    arms = payload["arms"]
    cells = payload["cells"]
    primary = arms["primary"]
    add("## PRIMARY arm — disjoint cohort, law vocabulary, n ≥ 10, s = 5, "
        "k ≥ 3")
    add()
    design = primary["design"]
    add(f"{design['authors']:,} eligible authors · {design['slots']:,} shared "
        f"pairs · {design['cells']:,} eligible cells · "
        f"{design['comments']:,} comments · {design['communities']:,} "
        f"communities.")
    add()
    add("| quantity | value |")
    add("|---|---|")
    add(f"| R (mean per-author correlation) | {_pct(primary['R'])} |")
    add(f"| cluster-bootstrap CI | {fmt_ci(primary['bootstrap']['r_ci'])} |")
    add(f"| permutation band | {fmt_ci(primary['null']['r_band'])} |")
    add()
    add("| arm | author main | community main | interaction | residual | "
        "R [CI, band] | cell | #73 |")
    add("|---|---|---|---|---|---|---|---|")
    for key, arm in arms.items():
        b = arm["budget"]
        ci = arm["bootstrap"]["shares_ci"]
        add(f"| {arm['tag']} | {_pct(b['author'])} {fmt_ci(ci['author'])} | "
            f"{_pct(b['community'])} {fmt_ci(ci['community'])} | "
            f"{_pct(b['interaction'])} {fmt_ci(ci['interaction'])} "
            f"{fmt_ci(arm['null']['interaction_band'])} | "
            f"{_pct(b['residual'])} | {_pct(arm['R'])} "
            f"{fmt_ci(arm['bootstrap']['r_ci'])} "
            f"{fmt_ci(arm['null']['r_band'])} | {cells[key]['cell']} | "
            f"{payload['flags_73'].get(key, '')} |")
    add()
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


def build_verdict(cells: dict[str, Any], arms: dict[str, Any], gate_ok: bool,
                  part0: dict[str, Any], comparison: dict[str, Any]
                  ) -> dict[str, Any]:
    if not gate_ok:
        failed = [name for name, status in part0["clauses"].items()
                  if status != "PASS"]
        hon = part0["honesty"]
        rec = part0["recovery"]
        old = comparison["grid"][
            "x1b_repaired_skeleton|x1_double_centering"]["interaction_mean"]
        new = comparison["grid"][
            "x1b_repaired_skeleton|x1b_exact_fe"]["interaction_mean"]
        return {
            "cell": CELL_A1_STOP,
            "clauses_failed": failed,
            "sentence": (
                f"Part 0 passed {part0['n_clauses_passed']} of its "
                f"{part0['n_clauses']} clauses and failed "
                f"{len(failed)} ("
                + "; ".join(f"“{name}”" for name in failed)
                + f"), so the A1 stop fired "
                f"BEFORE any real estimand was computed. No corpus value of "
                f"R, of the variance budget or of the headroom distribution "
                f"appears anywhere in this leg. The REGISTERED REPAIR itself "
                f"succeeded completely: on the identical null world the "
                f"exact two-way FE reads {fmt(new)} for the interaction "
                f"share where X1's double-centering reads {fmt(old)}, with a "
                f"cluster-bootstrap CI {fmt_ci(hon['interaction_ci'])} that "
                f"covers 0 and R = {fmt(hon['R'])} inside its permutation "
                f"band {fmt_ci(hon['r_band'])}. What fails is the object the "
                f"registration explicitly did NOT repair: the author main "
                f"share, estimated PRE-FE from the cross-half covariance of "
                f"author half-means, recovers {fmt(rec['author']['recovered_mean'])} "
                f"for a planted {fmt(rec['author']['planted'])} against a "
                f"tolerance of {fmt(rec['author']['tolerance'])}."),
        }
    cell = cells["primary"]                        # pragma: no cover
    arm = arms["primary"]                          # pragma: no cover
    return {                                       # pragma: no cover
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


ARM_LABELS = {
    "primary": "PRIMARY — disjoint, law vocab, n=10, s=5, k=3, wcq",
    "sens_s8": "sensitivity — support floor s=8",
    "sens_n5": "sensitivity — n_min=5 (same chain)",
    "sens_word_count": "sensitivity — y = log(1 + word_count)",
    "replication_big5": "REPLICATION — Big5 cohort, identical chain",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--x1-cache", type=Path, default=DEFAULT_X1_CACHE)
    parser.add_argument("--cohort", type=Path, default=DEFAULT_COHORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--b-perm", type=int, default=B_PERM)
    parser.add_argument("--b-boot", type=int, default=B_BOOT)
    args = parser.parse_args(argv)

    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    log = RunLog(output / "run_log.jsonl")
    started = time.time()

    config = {
        "leg": "M4-X1b",
        "title": "the venue response, repaired design and exact estimator",
        "registration":
            "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md@0f8e43e (X1b)",
        "predecessor": "M4-X1 (A1_STOP__SYNTHETIC_GATE_FAILED, commit ebe4f5b)",
        "run_utc": utc_now(),
        "seed": SEED, "seed_part0": SEED_PART0, "seed_perm": SEED_PERM,
        "seed_boot": SEED_BOOT,
        "b_perm": int(args.b_perm), "b_boot": int(args.b_boot),
        "y": "log(1 + word_count_quoteless)",
        "y_sensitivity": "log(1 + word_count)",
        "halves": "author's FULL-STREAM median created_utc, <= to early",
        "predicate_chain": [
            "1. cells with n >= n_min comments, cohort authors, law "
            "vocabulary communities",
            "2. shared pairs: (author, community) with BOTH halves eligible",
            "3. community support floor: >= s authors holding a shared pair",
            "4. authors with >= k_min surviving shared communities",
            "5. largest connected component of the bipartite graph",
            "NO fixed-point iteration: the chain runs once, in this order",
        ],
        "n_min_primary": N_MIN_PRIMARY,
        "n_min_sensitivity": N_MIN_SENSITIVITY,
        "k_min": K_MIN,
        "support_primary": S_PRIMARY,
        "support_sensitivity": S_SENSITIVITY,
        "support_censused": list(S_CENSUS),
        "vocabulary_floor_fraction": VOCAB_FLOOR_FRACTION,
        "estimator": ("two-way fixed effects per half by ALTERNATING "
                      "PROJECTIONS on the eligible shared cells; v = the FE "
                      "residual of the cell mean"),
        "fe_tolerance": FE_TOL,
        "mains_estimator": ("cross-half covariances of author and community "
                            "half-means, computed PRE-FE on the same pool "
                            "(X1's definition, unchanged by the registration)"),
        "cells": {"trace_max": TRACE_MAX,
                  "idiosyncratic_max": IDIOSYNCRATIC_MAX},
        "planted_shares": PLANTED_SHARES,
        "null_shares": NULL_SHARES,
        "ablation_worlds": ABLATION_WORLDS,
        "ablation_leak_max": ABLATION_LEAK_MAX,
        "synthetic_replicates": N_SYNTH_REPLICATES,
        "tolerance_floor": TOL_FLOOR,
        "tolerance_sd_multiple": TOL_SD_MULT,
        "big5_power_floor_69": BIG5_POWER_FLOOR,
        "min_cell_keep": MIN_CELL_KEEP,
        "columns_read": ["author", "subreddit", "created_utc",
                         "word_count_quoteless", "word_count"],
        "author_profiles_opened": False,
        "bodies_read": False,
        "var_y_denominator": ("comment-level population variance of y over "
                              "the analysis pool = the comments inside "
                              "eligible cells"),
        "bootstrap_semantics": ("cluster bootstrap over authors; the FE is "
                                "RECOMPUTED inside every replicate (#85b), "
                                "with author multiplicity as the projection "
                                "weight"),
    }
    config_blob = json.dumps(config, sort_keys=True, default=float)
    config_hash = hashlib.sha256(config_blob.encode("utf-8")).hexdigest()
    write_json(output / "config.json", config)
    write_json(output / "config.sha256.json", {"sha256": config_hash})
    log.event("config", sha256=config_hash)

    # ---- Stage 1: X1's cell cache -----------------------------------------
    table, scaffold = load_cell_cache(args.x1_cache, log)
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
    log.event("cohorts", big5_seen=int(big5_mask.sum()),
              disjoint=int(disjoint_mask.sum()))

    vocab = law_vocabulary(table, disjoint_mask, log)
    vocab_mask = vocab["mask"]

    observed = {
        "rows parseable (author+subreddit+created_utc+wcq)":
            int(stats["rows_parseable"]),
        "authors": int(stats["authors"]),
        "Big5 cohort authors seen": int(big5_mask.sum()),
        "disjoint authors": int(disjoint_mask.sum()),
        "law vocabulary floor (users)": int(vocab["floor_users"]),
        "law vocabulary (communities)": int(vocab["vocabulary_size"]),
    }
    expected = {
        "rows parseable (author+subreddit+created_utc+wcq)":
            ANCHOR_ROWS_PARSEABLE,
        "authors": ANCHOR_AUTHORS,
        "Big5 cohort authors seen": ANCHOR_BIG5_AUTHORS,
        "disjoint authors": ANCHOR_DISJOINT_AUTHORS,
        "law vocabulary floor (users)": ANCHOR_VOCAB_FLOOR_USERS,
        "law vocabulary (communities)": ANCHOR_LAW_VOCAB,
    }
    census = anchor_gate(observed, expected)
    write_json(output / "census.json", census)
    log.event("census", status=census["status"])
    gates: dict[str, str] = {
        "Inherited census anchors (#78: X1's ten pins, six re-checkable "
        "from the cache)": census["status"],
    }
    if census["status"] != "PASS":                 # pragma: no cover
        failed_pins = {k: v for k, v in census["pins"].items()
                       if v["status"] != "PASS"}
        raise SystemExit(
            f"STOP (#78): inherited census mismatch {failed_pins}")

    # ---- Stage 2: the predicate chain and its BLOCKING census -------------
    chain_designs: dict[int, Design] = {}
    chain_census: dict[str, Any] = {}
    for s in S_CENSUS:
        design, chain = build_chain_design(
            table, disjoint_mask, n_min=N_MIN_PRIMARY, support=s,
            vocab_mask=vocab_mask)
        chain_designs[s] = design
        chain_census[str(s)] = chain
        log.event("chain_census", s=s, authors=chain["authors"],
                  communities=chain["communities"],
                  shared_pairs=chain["shared_pairs"],
                  lcc=chain["lcc_author_coverage"])
    write_json(output / "chain_census.json", chain_census)

    pins_by_s: dict[str, Any] = {}
    chain_ok = True
    for s, want in CHAIN_ANCHORS.items():
        got = chain_census[str(s)]
        row = {k: want[k] for k in ("authors", "communities", "shared_pairs")}
        ok = all(float(got[k]) == float(v) for k, v in want.items())
        chain_ok = chain_ok and ok
        row["status"] = "PASS" if ok else "FAIL"
        row["observed"] = {k: got[k] for k in want}
        pins_by_s[str(s)] = row
    crosschecks: dict[str, Any] = {}
    for s, wants in CHAIN_CROSSCHECKS.items():
        got = chain_census[str(s)]
        for key, want in wants.items():
            digits = 4 if key != "authors_per_community_median" else 1
            observed = round(float(got[key]), digits)
            crosschecks[f"s = {s}: {key}"] = {
                "expected": want, "observed": observed,
                "agrees": bool(observed == round(float(want), digits))}
    write_json(output / "chain_crosschecks.json", crosschecks)
    chain_anchor = {"status": "PASS" if chain_ok else "FAIL",
                    "pins_by_s": pins_by_s,
                    "registered": {str(k): v
                                   for k, v in CHAIN_ANCHORS.items()}}
    write_json(output / "chain_anchor.json", chain_anchor)
    gates["Predicate-chain census (#78: the planner's s = 3/5/8 table exact, "
          "0 singleton communities and LCC 1.000 at s = 5)"] = \
        chain_anchor["status"]
    if not chain_ok:                               # pragma: no cover
        raise SystemExit(f"STOP (#78): predicate-chain census mismatch "
                         f"{pins_by_s}")

    primary = chain_designs[S_PRIMARY]
    lcc_cov = chain_census[str(S_PRIMARY)]["lcc_author_coverage"]
    if lcc_cov != 1.0:                             # pragma: no cover
        raise SystemExit(f"STOP: the LCC does not cover every author "
                         f"({lcc_cov}); the FE's exactness argument is void")
    gates["LCC assertion (the alternating projection is exact only on a "
          "connected design; coverage must be 1.000)"] = "PASS"

    # ---- Stage 3: the remaining arm designs (census only for now) ---------
    arm_designs_obj: dict[str, Design] = {"primary": primary}
    arm_chain: dict[str, Any] = {"primary": chain_census[str(S_PRIMARY)]}
    arm_chain["sens_s8"] = chain_census[str(S_SENSITIVITY)]
    arm_designs_obj["sens_s8"] = chain_designs[S_SENSITIVITY]
    for key, kwargs in (
        ("sens_n5", {"n_min": N_MIN_SENSITIVITY, "support": S_PRIMARY,
                     "y_key": "wcq", "author_mask": disjoint_mask}),
        ("sens_word_count", {"n_min": N_MIN_PRIMARY, "support": S_PRIMARY,
                             "y_key": "wc", "author_mask": disjoint_mask}),
        ("replication_big5", {"n_min": N_MIN_PRIMARY, "support": S_PRIMARY,
                              "y_key": "wcq", "author_mask": big5_mask}),
    ):
        author_mask = kwargs.pop("author_mask")
        design, chain = build_chain_design(table, author_mask,
                                           vocab_mask=vocab_mask, **kwargs)
        arm_designs_obj[key] = design
        arm_chain[key] = chain
        log.event("arm_design", arm=key, authors=chain["authors"],
                  communities=chain["communities"],
                  shared_pairs=chain["shared_pairs"])
    arm_designs = {k: dict(v, label=ARM_LABELS[k]) for k, v in
                   arm_chain.items()}
    write_json(output / "arm_designs.json", arm_designs)

    big5_authors = int(arm_chain["replication_big5"]["authors"])
    big5_power = {
        "authors": big5_authors,
        "floor": BIG5_POWER_FLOOR,
        "meets_floor": bool(big5_authors >= BIG5_POWER_FLOOR),
        "sentence": (
            f"The Big5 replication arm carries {big5_authors:,} eligible "
            f"authors under the identical chain, "
            + (f"at or above the in-leg #69 floor of {BIG5_POWER_FLOOR}, so "
               f"it would have carried a #73 comparison had a cell been "
               f"reached."
               if big5_authors >= BIG5_POWER_FLOOR else
               f"BELOW the in-leg #69 floor of {BIG5_POWER_FLOOR}, so it "
               f"would have reported as underpowered-descriptive with no "
               f"#73 flag.")),
    }
    write_json(output / "big5_power.json", big5_power)
    gates[f"Big5 replication #69 floor ({BIG5_POWER_FLOOR} authors, IN-LEG "
          "census; below it the arm is underpowered-descriptive, not #73)"] = \
        "PASS" if big5_power["meets_floor"] else "UNDERPOWERED_DESCRIPTIVE"

    # ---- Stage 4: PART 0, before any real estimand ------------------------
    part0 = synthetic_gate(primary, args.b_perm, args.b_boot, log)
    write_json(output / "part0_synthetic_gate.json", part0)
    gates["Part 0 — the gate that had to pass (#76/#85; A1 stop on any "
          "failing clause)"] = part0["status"]

    # ---- Stage 5: the repair demonstration --------------------------------
    x1_skeleton = X1.build_design(table, disjoint_mask, N_MIN_PRIMARY)
    comparison = estimator_comparison(primary, x1_skeleton, args.b_perm,
                                      args.b_boot, log)
    comparison["x1_skeleton_summary"] = x1_skeleton.summary()
    write_json(output / "estimator_comparison.json", comparison)

    composition = composition_diagnostics(primary)
    write_json(output / "composition_diagnostics.json", composition)
    diagnosis = build_diagnosis(part0, comparison,
                                chain_census[str(S_PRIMARY)], composition)
    defects = build_defect_candidates(part0, chain_census[str(S_PRIMARY)],
                                      composition)
    write_json(output / "diagnosis.json",
               {"diagnosis": diagnosis, "defect_candidates": defects})

    # ---- Stage 6: the real arms, ONLY if Part 0 passed --------------------
    arms: dict[str, Any] = {}
    cells: dict[str, Any] = {}
    flags_73: dict[str, str] = {}
    leans: list[dict[str, Any]] = []
    if part0["status"] == "PASS":                  # pragma: no cover
        for offset, (key, design) in enumerate(arm_designs_obj.items()):
            arms[key] = analyse_design_fe(
                design, b_perm=args.b_perm, b_boot=args.b_boot,
                seed_perm=SEED_PERM + 17 * offset,
                seed_boot=SEED_BOOT + 17 * offset, tag=ARM_LABELS[key],
                log=log)
            cells[key] = classify(arms[key])
            log.event("arm_done", arm=key, R=arms[key]["R"],
                      interaction=arms[key]["budget"]["interaction"],
                      cell=cells[key]["cell"])
        primary_cell = cells["primary"]["cell"]
        for key in arms:
            if key == "primary":
                continue
            if key == "replication_big5" and not big5_power["meets_floor"]:
                flags_73[key] = "underpowered-descriptive (#69), no #73"
                continue
            if cells[key]["cell"] != primary_cell:
                flags_73[key] = (f"#73 — {cells[key]['cell']} vs primary "
                                 f"{primary_cell}")
        leans = evaluate_leans(
            arms["primary"],
            cells["replication_big5"]["cell"]
            if big5_power["meets_floor"] else None,
            primary_cell)
        write_json(output / "arms.json", arms)
        write_json(output / "cells.json", cells)
        write_json(output / "leans.json", leans)
        write_json(output / "flags_73.json", flags_73)

    verdict = build_verdict(cells, arms, part0["status"] == "PASS", part0,
                            comparison)
    write_json(output / "verdict.json", verdict)

    payload = {
        "config": config,
        "census": census,
        "chain_census": chain_census,
        "chain_anchor": chain_anchor,
        "chain_crosschecks": crosschecks,
        "arm_designs": arm_designs,
        "big5_power": big5_power,
        "part0": part0,
        "comparison": comparison,
        "composition": composition,
        "arms": arms, "cells": cells, "flags_73": flags_73, "leans": leans,
        "gates": gates,
        "verdict": verdict,
        "diagnosis": diagnosis,
        "defect_candidates": defects,
        "boundaries": list(BOUNDARIES),
        "runtime_s": round(time.time() - started, 1),
    }
    write_report(args.report, payload)

    # ---- Stage 7: the ID-leak gate over the WIDENED universe (#83) --------
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
              pre_existing=scan["n_pre_existing_hits"])
    gates[f"ID-leak scan (0 NEW hits of {len(universe):,} author names over "
          f"the committed files; {scan['n_pre_existing_hits']} pre-existing "
          "dictionary collisions carried unchanged from HEAD)"] = scan["status"]
    payload["id_leak_scan"] = {k: v for k, v in scan.items() if k != "hits"}
    payload["gates"] = gates
    payload["runtime_s"] = round(time.time() - started, 1)
    write_report(args.report, payload)
    if scan["status"] != "PASS":                   # pragma: no cover
        raise SystemExit(f"STOP: ID-leak scan FAILED on NEW hits: {new_hits}")

    write_json(output / "report_payload.json",
               {k: v for k, v in payload.items() if k != "config"})
    log.event("done", verdict=verdict["cell"], part0=part0["status"],
              runtime_s=payload["runtime_s"])
    return 0


if __name__ == "__main__":                        # pragma: no cover
    raise SystemExit(main())
