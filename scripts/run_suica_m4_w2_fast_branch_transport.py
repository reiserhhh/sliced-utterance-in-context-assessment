#!/usr/bin/env python3
"""M4-W2 — fast-time and branch-code transport (the W line's label-free closer).

Registered BEFORE the run in ``docs/SUICA_M4_W_DISJOINT_TRANSPORT_PLAN.md``,
section "## W2 — fast-time and branch-code transport (registered BEFORE run,
2026-08-18)" (commit 49e1ba5).  Two sealed-prediction families are carried onto
the disjoint cohort that W1 built:

* the ORDER family — U1's fast-time order channel (bigram Hellinger sphere over
  spherical-k-means states, exact-bag within-half shuffle null, rho) — which
  ROUTES the verdict;
* the BRANCH family — T1's hierarchical selection identity (flat / frozen-path
  / terminal-residual AUCs, stable depths) — co-primary, carrying #73 flags but
  never routing.

Machinery is pinned by import (#81): the order pipeline is
``scripts/run_suica_m4_u1_order_identity.py`` loaded by file and CALLED, not
re-typed; the branch pipeline is
``suica_core.hierarchical_selection_identity.cross_fitted_hierarchical_identity``
driven with the T1 driver's argument pattern.

The W1 adjudication's binding design correction is honoured: pooled same-vs-
different AUCs depend on GALLERY SIZE, so the primary transport arms run on
seeded subpools of exactly the source sizes (N = 984 for order, N = 1304 for
branch).  The full-pool order run is a registered sensitivity; the full-pool
branch run is not registered.

Label-free: ``author_profiles.csv`` is never opened.  Author identity never
leaves ``results/`` (gitignored); the ID-leak gate runs over all 10,296 names
under the #83 HEAD-identical pre-existing-hit policy.
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
import warnings
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ---------------------------------------------------------------------------
# Configuration — every registration pin lives here (rule 24 source of truth)
# ---------------------------------------------------------------------------

SEED = 20260818                     # registration pin (both families)
N_FOLDS = 5                         # registration pin
C_PRIMARY = 24                      # registration pin (order states)
B_SHUFFLE = 499                     # registration pin (exact-bag shuffles)
B_BOOTSTRAP = 1000                  # registration pin (cluster bootstrap)
B_BOOT_SHUFFLE = 100                # U1's default null stack depth
B_BOOT_SHUFFLE_FULLPOOL = 10        # executor choice, RD-W2-1 (memory)

ORDER_POOL_MIN_PER_HALF = 50        # registration pin -> census 7,247
BRANCH_MIN_EVENTS = 40              # registration pin -> census 8,625
N_ORDER_SUBPOOL = 984               # size match to U1's gallery
N_BRANCH_SUBPOOL = 1304             # size match to T1's gallery

BRANCH_MAX_DEPTH = 6                # registration pin (T1 d6/l30)
BRANCH_MIN_LEAF = 30                # registration pin
BRANCH_PERMUTATIONS = 499           # registration pin
BRANCH_BOOTSTRAP = 1000             # registration pin (per-depth gain CIs)
BRANCH_AUC_BOOTSTRAP = 300          # executor choice, RD-W2-2 (AUC CI)
BRANCH_AUC_BOOT_PERMUTATIONS = 1    # inside the AUC bootstrap only
BRANCH_AUC_BOOT_INNER = 2           # inside the AUC bootstrap only

VOCAB_FLOOR_FRACTION = 0.01         # SR0's vocabulary RULE (law arm)
SESSION_GAP_SECONDS = 3600.0        # instrument descriptive

# ---- anchor gates (#78): STOP on any mismatch --------------------------------
CENSUS_DISJOINT_EVENTS = 14_634_702
CENSUS_AUTHORS_SEEN = 8_895
CENSUS_VOCAB_FLOOR_USERS = 89       # ceil(0.01 * 8895)
CENSUS_LAW_VOCAB = 1_443
CENSUS_ORDER_POOL = 7_247
CENSUS_BRANCH_POOL = 8_625
CENSUS_TIE_RATE_IN_VOCAB = 0.00882
CENSUS_SESSION_SHARE_IN_VOCAB = 0.56147
CENSUS_CROSS_THREAD_SHARE_ALL = 0.73174
ANCHOR_DECIMALS = 5

# ---- order verdict cell boundaries (U1's registered cells) --------------------
ORDER_CELL_LOW = 0.10
ORDER_CELL_HIGH = 0.33
ORDER_CELL_BOUNDARIES = (0.0, ORDER_CELL_LOW, ORDER_CELL_HIGH)
LEAN_RHO_BAND = (0.25, 0.40)        # registered lean band

# ---- sealed predictions (committed U1 / T1 artifacts) ------------------------
SEALED_ORDER: dict[str, dict[str, Any]] = {
    "primary": {
        "label": "rho, raw-adjacency primary arm",
        "point": 0.2893,
        "ci": [0.2695, 0.3114],
        "source": "results/m4_u1_order_identity/arms.json :: primary (N=984)",
        "gallery": 984,
    },
    "stay_rate": {
        "label": "rho, stay-rate scalar arm",
        "point": 0.1803,
        "ci": [0.1375, 0.2234],
        "source": "results/m4_u1_order_identity/arms.json :: stay_rate (N=984)",
        "gallery": 984,
    },
    "cross_thread": {
        "label": "rho, cross-thread-only arm",
        "point": 0.1626,
        "ci": [0.1373, 0.1895],
        "source": "results/m4_u1_order_identity/arms.json :: cross_thread (N=984)",
        "gallery": 984,
    },
}
SEALED_DWELL_SHARE = 0.7122          # descriptive: same-state adjacency share
SOURCE_TIE_RATE_IN_VOCAB = 0.11522   # registration census, U1's cohort
SEALED_BRANCH: dict[str, dict[str, Any]] = {
    "full.flat_auc": {"label": "flat Hellinger AUC (full arm)",
                      "point": 0.9837, "gallery": 1304},
    "full.hierarchical_path_auc": {"label": "frozen-path AUC (full arm)",
                                   "point": 0.7461, "gallery": 1304},
    "full.terminal_residual_auc": {"label": "terminal residual AUC (full arm)",
                                   "point": 0.9552, "gallery": 1304},
    "clean.flat_auc": {"label": "flat Hellinger AUC (clean arm)",
                       "point": 0.9661, "gallery": 1269},
    "clean.hierarchical_path_auc": {"label": "frozen-path AUC (clean arm)",
                                    "point": 0.7317, "gallery": 1269},
    "clean.terminal_residual_auc": {"label": "terminal residual AUC (clean arm)",
                                    "point": 0.9417, "gallery": 1269},
}
SEALED_DEPTHS = {"full": [1, 2, 3, 4, 5], "clean": [1, 2, 3, 4]}
T1_ARTIFACTS = ROOT / "results/m4_t1_hierarchical_selection_identity"
U1_ARTIFACTS = ROOT / "results/m4_u1_order_identity"

# ---- paths -------------------------------------------------------------------
U1_SCRIPT = ROOT / "scripts/run_suica_m4_u1_order_identity.py"
W1_CACHE = ROOT / "results/m4_w1_slow_transport/disjoint_events_cache.npz"
DEFAULT_COHORT = ROOT / "results/m4_sr0_recon/cohort_authors.csv"
DEFAULT_OUTPUT = ROOT / "results/m4_w2_fast_branch_transport"
DEFAULT_REPORT = ROOT / "reports/SUICA_M4_W2_FAST_BRANCH_TRANSPORT_REPORT.md"

COMMITTED_FILES = (
    DEFAULT_REPORT,
    Path(__file__),
    ROOT / "tests/test_m4_w2_fast_branch_transport.py",
    ROOT / "docs/SUICA_M4_W_DISJOINT_TRANSPORT_PLAN.md",
    ROOT / "docs/CLAIMS_LEDGER.md",
)


# ---------------------------------------------------------------------------
# Machinery pinned by import (#56/#81): the inherited objects, called not retyped
# ---------------------------------------------------------------------------


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:      # pragma: no cover
        raise RuntimeError(f"cannot import machinery from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


U1 = load_module("suica_m4_u1", U1_SCRIPT)

from suica_core.hierarchical_selection_identity import (  # noqa: E402
    cross_fitted_hierarchical_identity,
)

# Names reused unchanged, listed so the reuse is auditable.
EventScaffold = U1.EventScaffold
RunLog = U1.RunLog
load_scaffold = U1.load_scaffold
split_halves = U1.split_halves
build_pool_context = U1.build_pool_context
build_state_maps = U1.build_state_maps
assert_fold_purity = U1.assert_fold_purity
run_arm = U1.run_arm
compute_descriptives = U1.compute_descriptives
scan_for_cohort_ids = U1.scan_for_cohort_ids
is_explicit_personality_community = U1.is_explicit_personality_community
order_cell_of = U1._cell_of          # U1's registered cell partition on one arm
write_json = U1.write_json
utc_now = U1.utc_now

ORDER_ARMS = tuple(spec for spec in U1.ARMS
                   if spec.key in ("primary", "stay_rate", "cross_thread"))


# ---------------------------------------------------------------------------
# Stage 0 — the cache, the law vocabulary, the two censused pools
# ---------------------------------------------------------------------------


def law_vocabulary(cache: EventScaffold) -> dict[str, Any]:
    """Re-instantiate SR0's vocabulary RULE on the disjoint cohort.

    Distinct cohort users per subreddit; floor = ceil(0.01 * authors_seen).
    The recomputed list must be BIT-IDENTICAL to the one carried in the cache.
    """

    n_authors = len(cache.authors)
    pair_key = cache.subreddit_code.astype(np.int64) * n_authors + cache.author_code
    unique_pairs = np.unique(pair_key)
    users_per_subreddit = np.bincount(
        (unique_pairs // n_authors).astype(np.int64),
        minlength=len(cache.subreddits))
    authors_seen = int(np.unique(cache.author_code).size)
    floor_users = max(1, int(math.ceil(VOCAB_FLOOR_FRACTION * authors_seen)))
    keep = users_per_subreddit >= floor_users
    vocabulary = sorted(name for name, k in zip(cache.subreddits, keep) if k)
    return {
        "authors_seen": authors_seen,
        "floor_users": floor_users,
        "vocabulary_size": len(vocabulary),
        "identical_to_cache": bool(vocabulary == list(cache.vocabulary)),
    }


def author_segments(cache: EventScaffold) -> dict[str, Any]:
    """Per-author slices, full-stream-median halves and the two eligibilities."""

    author_code = cache.author_code
    created = cache.created_utc
    event_vocab = cache.vocab_of_subreddit[cache.subreddit_code]
    boundaries = np.flatnonzero(author_code[1:] != author_code[:-1]) + 1
    starts = np.concatenate(([0], boundaries))
    stops = np.concatenate((boundaries, [author_code.size]))
    present = author_code[starts]

    n_authors = len(cache.authors)
    is_early = np.zeros(author_code.size, dtype=bool)
    early_counts = np.zeros(n_authors, dtype=np.int64)
    late_counts = np.zeros(n_authors, dtype=np.int64)
    total_counts = np.zeros(n_authors, dtype=np.int64)
    for start, stop, author in zip(starts, stops, present):
        early = split_halves(created[start:stop])
        is_early[start:stop] = early
        in_vocab = event_vocab[start:stop] >= 0
        early_counts[author] = int(np.count_nonzero(in_vocab & early))
        late_counts[author] = int(np.count_nonzero(in_vocab & ~early))
        total_counts[author] = int(stop - start)
    order_pool = np.flatnonzero(
        (early_counts >= ORDER_POOL_MIN_PER_HALF)
        & (late_counts >= ORDER_POOL_MIN_PER_HALF)).astype(np.int32)
    branch_pool = np.flatnonzero(
        total_counts >= BRANCH_MIN_EVENTS).astype(np.int32)
    slices = {int(a): (int(s), int(e))
              for a, s, e in zip(present, starts, stops)}
    return {
        "event_vocab": event_vocab,
        "is_early": is_early,
        "slices": slices,
        "order_pool": order_pool,
        "branch_pool": branch_pool,
        "early_counts": early_counts,
        "late_counts": late_counts,
        "total_counts": total_counts,
    }


def adjacency_rates(author_code: np.ndarray, created: np.ndarray,
                    link_code: np.ndarray) -> dict[str, float]:
    """Tie / session / cross-thread shares over same-author adjacencies."""

    same_author = author_code[1:] == author_code[:-1]
    denominator = max(1, int(np.count_nonzero(same_author)))
    gaps = created[1:] - created[:-1]
    return {
        "adjacencies": denominator,
        "tie_rate": float(np.count_nonzero(same_author & (gaps == 0.0))
                          / denominator),
        "session_share": float(
            np.count_nonzero(same_author & (gaps <= SESSION_GAP_SECONDS))
            / denominator),
        "cross_thread_share": float(
            np.count_nonzero(same_author & (link_code[1:] != link_code[:-1]))
            / denominator),
    }


def instrument_descriptives(cache: EventScaffold,
                            event_vocab: np.ndarray) -> dict[str, Any]:
    """The cohort-instrument census: spliced in-law-vocab, and all events."""

    in_vocab = event_vocab >= 0
    return {
        "in_law_vocabulary_spliced": adjacency_rates(
            cache.author_code[in_vocab], cache.created_utc[in_vocab],
            cache.link_code[in_vocab]),
        "all_events": adjacency_rates(
            cache.author_code, cache.created_utc, cache.link_code),
    }


def verify_anchors(cache: EventScaffold, vocab: dict[str, Any],
                   segments: dict[str, Any],
                   instrument: dict[str, Any]) -> dict[str, Any]:
    """BLOCKING (#78): every registered anchor must reproduce EXACTLY."""

    observed = {
        "disjoint_events": int(cache.author_code.size),
        "authors_seen": int(vocab["authors_seen"]),
        "vocab_floor_users": int(vocab["floor_users"]),
        "law_vocabulary": int(vocab["vocabulary_size"]),
        "order_pool": int(segments["order_pool"].size),
        "branch_pool": int(segments["branch_pool"].size),
        "tie_rate_in_law_vocab": round(
            instrument["in_law_vocabulary_spliced"]["tie_rate"],
            ANCHOR_DECIMALS),
        "session_share_in_law_vocab": round(
            instrument["in_law_vocabulary_spliced"]["session_share"],
            ANCHOR_DECIMALS),
        "cross_thread_share_all_events": round(
            instrument["all_events"]["cross_thread_share"], ANCHOR_DECIMALS),
    }
    expected = {
        "disjoint_events": CENSUS_DISJOINT_EVENTS,
        "authors_seen": CENSUS_AUTHORS_SEEN,
        "vocab_floor_users": CENSUS_VOCAB_FLOOR_USERS,
        "law_vocabulary": CENSUS_LAW_VOCAB,
        "order_pool": CENSUS_ORDER_POOL,
        "branch_pool": CENSUS_BRANCH_POOL,
        "tie_rate_in_law_vocab": CENSUS_TIE_RATE_IN_VOCAB,
        "session_share_in_law_vocab": CENSUS_SESSION_SHARE_IN_VOCAB,
        "cross_thread_share_all_events": CENSUS_CROSS_THREAD_SHARE_ALL,
    }
    mismatches = {k: [expected[k], observed[k]]
                  for k in expected if expected[k] != observed[k]}
    if not vocab["identical_to_cache"]:
        mismatches["vocabulary_identical_to_cache"] = [True, False]
    return {
        "status": "PASS" if not mismatches else "FAIL",
        "expected": expected,
        "observed": observed,
        "mismatches": mismatches,
        "n_anchors": len(expected) + 1,
        "vocabulary_identical_to_cache": bool(vocab["identical_to_cache"]),
    }


# ---------------------------------------------------------------------------
# Stage 1 — the two seeded, size-matched draws (documented order)
# ---------------------------------------------------------------------------


def seeded_subpools(order_pool: np.ndarray,
                    branch_pool: np.ndarray) -> dict[str, Any]:
    """ONE rng stream, TWO draws, in this order: order first, branch second.

    ``numpy.random.default_rng(SEED)`` is created once.  Draw 1 takes
    ``N_ORDER_SUBPOOL`` author codes uniformly WITHOUT replacement from the
    censused order pool; draw 2 continues the SAME stream and takes
    ``N_BRANCH_SUBPOOL`` from the censused branch pool.  Both results are
    sorted ascending before use, so downstream author order is the cache's.
    The draws are therefore coupled through the stream position: re-ordering
    them would change both.  The draw ORDER is part of the pin.
    """

    if order_pool.size < N_ORDER_SUBPOOL or branch_pool.size < N_BRANCH_SUBPOOL:
        raise SystemExit("STOP: size matching infeasible on the censused pools")
    rng = np.random.default_rng(SEED)
    order_draw = np.sort(rng.choice(order_pool, size=N_ORDER_SUBPOOL,
                                    replace=False)).astype(np.int32)
    branch_draw = np.sort(rng.choice(branch_pool, size=N_BRANCH_SUBPOOL,
                                     replace=False)).astype(np.int32)
    overlap = int(np.intersect1d(order_draw, branch_draw).size)
    return {
        "seed": SEED,
        "draw_order": ["order_subpool", "branch_subpool"],
        "rng": "numpy.random.default_rng(20260818), one stream, two draws",
        "order_subpool": order_draw,
        "branch_subpool": branch_draw,
        "order_n": int(order_draw.size),
        "branch_n": int(branch_draw.size),
        "order_source_pool": int(order_pool.size),
        "branch_source_pool": int(branch_pool.size),
        "order_digest": digest_codes(order_draw),
        "branch_digest": digest_codes(branch_draw),
        "authors_in_both_draws": overlap,
    }


def digest_codes(codes: np.ndarray) -> str:
    """Identity-free fingerprint of a draw (codes are cache indices, not names)."""

    return hashlib.sha256(np.ascontiguousarray(
        codes.astype(np.int64)).tobytes()).hexdigest()[:16]


def restrict_scaffold(cache: EventScaffold,
                      codes: np.ndarray) -> EventScaffold:
    """Author-restricted view of the cache with author codes re-indexed 0..n-1.

    Restriction is per author: halves, eligibility and vocabulary are all
    per-author-local or global, so the restricted scaffold reproduces exactly
    what the full scaffold would give for these authors.
    """

    keep = np.zeros(len(cache.authors), dtype=bool)
    keep[codes] = True
    mask = keep[cache.author_code]
    remap = np.full(len(cache.authors), -1, dtype=np.int32)
    remap[codes] = np.arange(codes.size, dtype=np.int32)
    return EventScaffold(
        authors=[cache.authors[int(c)] for c in codes],
        author_code=remap[cache.author_code[mask]],
        subreddit_code=cache.subreddit_code[mask],
        created_utc=cache.created_utc[mask],
        link_code=cache.link_code[mask],
        subreddits=cache.subreddits,
        vocabulary=cache.vocabulary,
        vocab_of_subreddit=cache.vocab_of_subreddit,
        stream_stats=dict(cache.stream_stats),
    )


# ---------------------------------------------------------------------------
# Stage 2 — the ORDER family (U1's pipeline, called)
# ---------------------------------------------------------------------------


def run_order_family(scaffold: EventScaffold, label: str, log: RunLog,
                     b_boot_shuffle: int,
                     arms: Sequence[Any] = ORDER_ARMS) -> dict[str, Any]:
    pool = build_pool_context(scaffold, "full", ORDER_POOL_MIN_PER_HALF, log)
    purity = assert_fold_purity(pool)
    state_maps, state_info = build_state_maps(pool, C_PRIMARY, log)
    results: dict[str, Any] = {}
    for spec in arms:
        started = time.time()
        results[spec.key] = run_arm(spec, pool, state_maps, log,
                                    b_shuffle=B_SHUFFLE,
                                    b_bootstrap=B_BOOTSTRAP,
                                    b_boot_shuffle=b_boot_shuffle,
                                    collect_bag_reference=True)
        results[spec.key]["wall_seconds"] = round(time.time() - started, 1)
    descriptives = compute_descriptives(pool, state_maps, log)
    return {
        "label": label,
        "gallery_n": int(pool.pool_authors.size),
        "census": pool.census,
        "fold_purity": purity,
        "state_maps": state_info,
        "arms": results,
        "descriptives": descriptives,
        "b_boot_shuffle": int(b_boot_shuffle),
    }


# ---------------------------------------------------------------------------
# Stage 3 — the BRANCH family (T1's pipeline, called)
# ---------------------------------------------------------------------------


def branch_matrices(cache: EventScaffold, codes: np.ndarray,
                    segments: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    """SR0 split-half sqrt-frequency inputs over the law vocabulary.

    Raw per-half community counts; the Hellinger/unit-sphere step happens
    inside ``cross_fitted_hierarchical_identity`` (T1's contract).
    """

    n_vocab = len(cache.vocabulary)
    event_vocab = segments["event_vocab"]
    is_early = segments["is_early"]
    slices = segments["slices"]
    early = np.zeros((codes.size, n_vocab), dtype=np.float64)
    late = np.zeros((codes.size, n_vocab), dtype=np.float64)
    for row, author in enumerate(codes):
        start, stop = slices[int(author)]
        ids = event_vocab[start:stop]
        early_mask = is_early[start:stop]
        in_vocab = ids >= 0
        early[row] = np.bincount(ids[in_vocab & early_mask], minlength=n_vocab)
        late[row] = np.bincount(ids[in_vocab & ~early_mask], minlength=n_vocab)
    return early, late


def stable_depths_from_metrics(metrics: Sequence[dict[str, Any]]) -> list[int]:
    """T1's triple gate, verbatim: centroid gain, local replay, excess bits."""

    return [
        int(row["depth"])
        for row in metrics
        if float(row["gain_ci_low"]) > 0
        and float(row["gain_permutation_p"]) <= 0.01
        and float(row["branch_excess"]) > 0
        and float(row["branch_permutation_p"]) <= 0.01
        and float(row["information_excess_bits"]) > 0
        and float(row["information_permutation_p"]) <= 0.01
    ]


BRANCH_AUC_KEYS = ("flat_auc", "hierarchical_path_auc", "terminal_residual_auc")


def branch_auc_bootstrap(arms_input: dict[str, tuple[np.ndarray, np.ndarray]],
                         b: int, log: RunLog) -> dict[str, Any]:
    """Author-level cluster bootstrap of the three pooled AUCs (RD-W2-2).

    ``cross_fitted_hierarchical_identity`` returns the AUCs as points with no
    interval, and T1's committed artifacts carry no AUC intervals either, so
    the registered fallback (classify by point-in-TARGET-CI) needs a target
    interval that this leg must supply.  The interval is produced by the house
    instrument — a cluster bootstrap over AUTHORS — re-running the SAME pinned
    function on each resample, with its internal permutation/bootstrap counts
    reduced to the minimum (they do not enter the AUCs; verified by a contract
    test).  Both arms share each replicate's author draw, so the arms are
    paired.

    Honest caveat carried into the report: a with-replacement author draw puts
    duplicated authors into the gallery, and a duplicate scores as high as the
    true match while being labelled "different", so the bootstrap distribution
    need not centre on the point estimate.  The bias is MEASURED per row, not
    assumed, and the bias-corrected ("basic") interval is reported alongside
    the percentile interval so every class can be checked under both.
    """

    n = next(iter(arms_input.values()))[0].shape[0]
    rng = np.random.default_rng(SEED + 11)
    draws = np.empty((b, n), dtype=np.int64)
    for replicate in range(b):
        draws[replicate] = rng.integers(0, n, size=n)
    samples = {arm: {key: np.full(b, np.nan) for key in BRANCH_AUC_KEYS}
               for arm in arms_input}
    failures = 0
    started = time.time()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for replicate in range(b):
            index = draws[replicate]
            for arm, (early, late) in arms_input.items():
                try:
                    out = cross_fitted_hierarchical_identity(
                        early[index], late[index],
                        n_splits=N_FOLDS,
                        max_depth=BRANCH_MAX_DEPTH,
                        min_leaf=BRANCH_MIN_LEAF,
                        random_state=SEED,
                        n_permutations=BRANCH_AUC_BOOT_PERMUTATIONS,
                        n_bootstrap=BRANCH_AUC_BOOT_INNER,
                    )
                except Exception:                       # pragma: no cover
                    failures += 1
                    continue
                for key in BRANCH_AUC_KEYS:
                    samples[arm][key][replicate] = float(out["summary"][key])
            if (replicate + 1) % 50 == 0:
                log.event("branch_auc_bootstrap_progress",
                          replicate=replicate + 1, of=b,
                          elapsed_s=round(time.time() - started, 1))
    return {
        "b": int(b),
        "failures": int(failures),
        "wall_seconds": round(time.time() - started, 1),
        "samples": {arm: {key: samples[arm][key] for key in BRANCH_AUC_KEYS}
                    for arm in samples},
    }


def summarise_auc_bootstrap(point: float, draws: np.ndarray) -> dict[str, Any]:
    finite = draws[np.isfinite(draws)]
    lo, hi = (float(v) for v in np.percentile(finite, [2.5, 97.5]))
    mean = float(finite.mean())
    return {
        "point": float(point),
        "ci": [lo, hi],
        "sd": float(finite.std(ddof=1)),
        "bootstrap_mean": mean,
        "bias": mean - float(point),
        "basic_ci": [2.0 * float(point) - hi, 2.0 * float(point) - lo],
        "n_draws": int(finite.size),
    }


def run_branch_family(cache: EventScaffold, codes: np.ndarray,
                      segments: dict[str, Any], log: RunLog,
                      b_auc_bootstrap: int) -> dict[str, Any]:
    early, late = branch_matrices(cache, codes, segments)
    removed_indices = [i for i, name in enumerate(cache.vocabulary)
                       if is_explicit_personality_community(name)]
    clean_early = early.copy()
    clean_late = late.copy()
    clean_early[:, removed_indices] = 0.0
    clean_late[:, removed_indices] = 0.0

    arms_input = {"full": (early, late),
                  "clean_no_explicit_personality": (clean_early, clean_late)}
    arms: dict[str, Any] = {}
    for name, (e_mat, l_mat) in arms_input.items():
        started = time.time()
        out = cross_fitted_hierarchical_identity(
            e_mat, l_mat,
            n_splits=N_FOLDS,
            max_depth=BRANCH_MAX_DEPTH,
            min_leaf=BRANCH_MIN_LEAF,
            random_state=SEED,
            n_permutations=BRANCH_PERMUTATIONS,
            n_bootstrap=BRANCH_BOOTSTRAP,
        )
        arms[name] = {
            "summary": out["summary"],
            "metrics_by_depth": out["metrics_by_depth"],
            "stable_depths": stable_depths_from_metrics(out["metrics_by_depth"]),
            "wall_seconds": round(time.time() - started, 1),
        }
        log.event("branch_arm_done", arm=name,
                  n_valid=out["summary"]["n_valid"],
                  flat=out["summary"]["flat_auc"],
                  path=out["summary"]["hierarchical_path_auc"],
                  residual=out["summary"]["terminal_residual_auc"],
                  stable_depths=arms[name]["stable_depths"])

    boot = branch_auc_bootstrap(arms_input, b_auc_bootstrap, log)
    for name in arms:
        arms[name]["auc_intervals"] = {
            key: summarise_auc_bootstrap(arms[name]["summary"][key],
                                         boot["samples"][name][key])
            for key in BRANCH_AUC_KEYS
        }
    return {
        "gallery_n_input": int(codes.size),
        "arms": arms,
        "removed_typology_communities": [cache.vocabulary[i]
                                         for i in removed_indices],
        "n_removed_typology_communities": len(removed_indices),
        "bootstrap": {k: v for k, v in boot.items() if k != "samples"},
    }


# ---------------------------------------------------------------------------
# Stage 4 — the four-class transport scheme (#75 + RESOLVES, W1 adjudication)
# ---------------------------------------------------------------------------


def intervals_overlap(a: Sequence[float], b: Sequence[float]) -> bool:
    return bool(max(float(a[0]), float(b[0])) <= min(float(a[1]), float(b[1])))


def contained_in(value: float, interval: Sequence[float]) -> bool:
    return bool(float(interval[0]) <= float(value) <= float(interval[1]))


UNRESOLVED = "UNRESOLVED"


def cells_spanned(ci: Sequence[float], cell_of: Any) -> list[str]:
    """Every cell the interval's endpoints touch (a straddle spans >= 2)."""

    return sorted({cell_of(float(ci[0])), cell_of(float(ci[1]))})


def cell_of_interval(ci: Sequence[float], cell_of: Any) -> str:
    """W1's convention: a quantity's CELL is read off its INTERVAL, not its
    point.  An interval whose endpoints fall in different cells straddles a
    boundary and is UNRESOLVED — which is exactly the state a RESOLVES row
    starts from."""

    spanned = cells_spanned(ci, cell_of)
    return spanned[0] if len(spanned) == 1 else UNRESOLVED


def same_direction(source_point: float, target_point: float) -> bool:
    return bool(np.sign(source_point) == np.sign(target_point)
                or float(source_point) == 0.0)


def classify_four_class(source_ci: Sequence[float] | None,
                        target_ci: Sequence[float],
                        source_point: float, target_point: float,
                        cell_of: Any) -> dict[str, Any]:
    """REPRODUCES / RESOLVES / SHIFTS / BREAKS, exactly as adjudicated.

    * REPRODUCES — CIs intersect and the cells agree.
    * RESOLVES   — same direction; the SOURCE CI straddled a cell boundary
                   that the TARGET CI excludes; the source point lies inside
                   the target CI.  A transported precision gain, never a
                   contradiction.
    * SHIFTS     — same cell, disjoint CIs.
    * BREAKS     — different sign / cell.

    When the source CI is ABSENT (registered fallback for T1's AUCs), the
    class is decided by point-in-target-CI within the shared cell, and the
    missing interval is flagged.
    """

    target_spanned = cells_spanned(target_ci, cell_of)
    target_cell = cell_of_interval(target_ci, cell_of)
    if source_ci is None:
        # No source interval exists (T1 published none).  The registered
        # fallback compares the source POINT against the target interval,
        # inside the shared cell, and the missing interval is flagged.
        source_cell = cell_of(float(source_point))
        if source_cell != target_cell:
            classification = "BREAKS"
        elif contained_in(source_point, target_ci):
            classification = "REPRODUCES"
        else:
            classification = "SHIFTS"
        return {
            "classification": classification,
            "source_ci_missing": True,
            "source_cell": source_cell,
            "target_cell": target_cell,
            "target_ci_spans": target_spanned,
            "ci_overlap": None,
            "source_point_inside_target_ci": contained_in(source_point,
                                                          target_ci),
        }

    spanned = cells_spanned(source_ci, cell_of)
    source_cell = cell_of_interval(source_ci, cell_of)
    if source_cell == target_cell and source_cell != UNRESOLVED:
        classification = ("REPRODUCES" if intervals_overlap(source_ci, target_ci)
                          else "SHIFTS")
    elif (source_cell == UNRESOLVED
          and target_cell != UNRESOLVED
          and target_cell in spanned
          and same_direction(source_point, target_point)
          and contained_in(source_point, target_ci)):
        classification = "RESOLVES"
    else:
        classification = "BREAKS"
    return {
        "classification": classification,
        "source_ci_missing": False,
        "source_cell": source_cell,
        "target_cell": target_cell,
        "source_ci_spans": spanned,
        "target_ci_spans": target_spanned,
        "ci_overlap": intervals_overlap(source_ci, target_ci),
        "source_point_inside_target_ci": contained_in(source_point, target_ci),
        "target_point_inside_source_ci": contained_in(target_point, source_ci),
    }


def order_cell_of_rho(rho: float) -> str:
    """The order family's cell partition, keyed on the point (CI support
    is applied separately through U1's ``_cell_of`` on the arm)."""

    if rho <= 0.0:
        return "NO_ORDER_CHANNEL"
    if rho < ORDER_CELL_LOW:
        return "ORDER_TRACE"
    if rho <= ORDER_CELL_HIGH:
        return "ORDER_CHANNEL"
    return "ORDER_MAJOR"


def sign_cell_of(value: float) -> str:
    """W1's sign partition, keyed on a POINT so it composes with ``cells_spanned``.

    Kept so the four-class scheme can be exercised against W1's adjudicated
    Lambda row, which is the reference RESOLVES case.
    """

    if value > 0.0:
        return "POSITIVE"
    if value < 0.0:
        return "NEGATIVE"
    return "ZERO"


def auc_cell_of(auc: float) -> str:
    """The branch family's cell partition: a collapse to chance is the break."""

    if auc > 0.5:
        return "ABOVE_CHANCE"
    if auc < 0.5:
        return "BELOW_CHANCE"
    return "AT_CHANCE"


def order_transport_rows(order: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for key, sealed in SEALED_ORDER.items():
        arm = order["arms"][key]
        verdict = classify_four_class(sealed["ci"], arm["rho_ci"],
                                      sealed["point"], arm["rho"],
                                      order_cell_of_rho)
        rows.append({
            "family": "order",
            "key": key,
            "quantity": sealed["label"],
            "source_point": sealed["point"],
            "source_ci": sealed["ci"],
            "source_gallery_n": sealed["gallery"],
            "source_provenance": sealed["source"],
            "target_point": float(arm["rho"]),
            "target_ci": [float(v) for v in arm["rho_ci"]],
            "target_gallery_n": order["gallery_n"],
            "size_matched": bool(order["gallery_n"] == sealed["gallery"]),
            "delta": float(arm["rho"]) - float(sealed["point"]),
            "auc_real": float(arm["auc_real"]),
            "auc_null_mean": float(arm["auc_null_mean"]),
            "auc_null_band": [float(v) for v in arm["auc_null_band"]],
            "bag_auc_unigram": float(arm.get("bag_auc_unigram", float("nan"))),
            "null_minus_bag": float(arm.get("null_minus_bag", float("nan"))),
            "real_minus_bag": float(arm.get("real_minus_bag", float("nan"))),
            "shuffle_p_value": float(arm["shuffle_p_value"]),
            "bag_invariance_exact": bool(arm["bag_invariance_exact"]),
            "arm_cell_with_ci_support": order_cell_of(arm),
            **verdict,
        })
    return rows


def branch_transport_rows(branch: dict[str, Any],
                          source_cis: dict[str, Any]) -> list[dict[str, Any]]:
    arm_alias = {"full": "full", "clean": "clean_no_explicit_personality"}
    rows = []
    for sealed_key, sealed in SEALED_BRANCH.items():
        arm_key, metric = sealed_key.split(".", 1)
        arm = branch["arms"][arm_alias[arm_key]]
        interval = arm["auc_intervals"][metric]
        source_ci = source_cis.get(sealed_key)
        verdict = classify_four_class(source_ci, interval["ci"],
                                      sealed["point"], interval["point"],
                                      auc_cell_of)
        rows.append({
            "family": "branch",
            "key": sealed_key,
            "arm": arm_key,
            "quantity": sealed["label"],
            "source_point": sealed["point"],
            "source_ci": source_ci,
            "source_gallery_n": sealed["gallery"],
            "source_provenance":
                "results/m4_t1_hierarchical_selection_identity/summary.json",
            "target_point": interval["point"],
            "target_ci": interval["ci"],
            "target_ci_basic": interval["basic_ci"],
            "target_ci_bias": interval["bias"],
            "target_gallery_n": int(arm["summary"]["n_valid"]),
            "target_gallery_n_input": branch["gallery_n_input"],
            "size_matched": bool(branch["gallery_n_input"] == 1304),
            "delta": interval["point"] - float(sealed["point"]),
            **verdict,
        })
    return rows


def depth_transport_rows(branch: dict[str, Any]) -> list[dict[str, Any]]:
    alias = {"full": "full", "clean": "clean_no_explicit_personality"}
    rows = []
    for arm_key, sealed in SEALED_DEPTHS.items():
        observed = branch["arms"][alias[arm_key]]["stable_depths"]
        source = set(sealed)
        target = set(observed)
        symmetric = sorted(source ^ target)
        if source == target:
            classification = "DEPTHS_REPRODUCE"
        elif len(symmetric) <= 1:
            classification = "DEPTHS_SHIFT"
        else:
            classification = "DEPTHS_BREAK"
        rows.append({
            "family": "branch",
            "key": f"{arm_key}.stable_depths",
            "arm": arm_key,
            "quantity": f"stable depths ({arm_key} arm)",
            "source_depths": sorted(source),
            "target_depths": sorted(target),
            "symmetric_difference": symmetric,
            "classification": classification,
        })
    return rows


def load_t1_source_intervals() -> dict[str, Any]:
    """T1's committed artifacts carry per-depth gain CIs but NO AUC CIs.

    Every absent interval is recorded explicitly so the report can flag it,
    as the registration requires.
    """

    present: dict[str, Any] = {}
    missing: list[str] = []
    summary_path = T1_ARTIFACTS / "summary.json"
    payload = (json.loads(summary_path.read_text(encoding="utf-8"))
               if summary_path.exists() else {})
    alias = {"full": "full", "clean": "clean_no_explicit_personality"}
    for sealed_key in SEALED_BRANCH:
        arm_key, metric = sealed_key.split(".", 1)
        arm = payload.get("arms", {}).get(alias[arm_key], {})
        for candidate in (f"{metric}_ci", f"{metric}_ci_low"):
            if candidate in arm:
                present[sealed_key] = [float(arm[f"{metric}_ci_low"]),
                                       float(arm[f"{metric}_ci_high"])]
                break
        else:
            missing.append(sealed_key)
    return {"present": present, "missing": missing,
            "artifact_exists": summary_path.exists(),
            "artifact": str(summary_path.relative_to(ROOT))}


# ---------------------------------------------------------------------------
# Stage 5 — verdict routing and the registered leans
# ---------------------------------------------------------------------------


def route_verdict(order_rows: Sequence[dict[str, Any]],
                  order: dict[str, Any]) -> dict[str, Any]:
    """NULL-first routing on the PRIMARY rho row (the registered router)."""

    primary = next(row for row in order_rows if row["key"] == "primary")
    arm_cell = primary["arm_cell_with_ci_support"]
    if arm_cell != "ORDER_CHANNEL":
        cell, number = "ORDER_BREAKS", 1
        statement = ("the target rho lands OUTSIDE U1's ORDER_CHANNEL cell — "
                     "the order law does not re-instantiate on fresh authors")
    elif primary["classification"] in ("REPRODUCES", "RESOLVES"):
        cell, number = "ORDER_TRANSPORTS", 3
        statement = ("the order channel re-instantiates on authors who share "
                     "nobody with the source cohort")
    else:
        cell, number = "ORDER_SHIFTS", 2
        statement = ("the order channel re-instantiates IN CELL but at a "
                     "different level — same law, different magnitude")
    return {
        "verdict": cell,
        "cell_number": number,
        "statement": statement,
        "router": "primary rho row (raw adjacency, size-matched N=984)",
        "primary_rho": primary["target_point"],
        "primary_rho_ci": primary["target_ci"],
        "primary_classification": primary["classification"],
        "primary_arm_cell": arm_cell,
        "source_cell": primary["source_cell"],
        "gallery_n": order["gallery_n"],
    }


def evaluate_leans(order_rows: Sequence[dict[str, Any]],
                   order: dict[str, Any],
                   branch_rows: Sequence[dict[str, Any]],
                   depth_rows: Sequence[dict[str, Any]],
                   verdict: dict[str, Any]) -> list[dict[str, Any]]:
    primary = next(row for row in order_rows if row["key"] == "primary")
    stay = next(row for row in order_rows if row["key"] == "stay_rate")
    dwell = float(order["descriptives"]["stay_share_of_all_pairs"])
    in_band = (LEAN_RHO_BAND[0] <= primary["target_point"] <= LEAN_RHO_BAND[1])
    leans = [{
        "lean": "L1",
        "statement": ("ORDER_TRANSPORTS with target rho in "
                      f"[{LEAN_RHO_BAND[0]}, {LEAN_RHO_BAND[1]}]; the absent "
                      "tie attenuation (0.9% here vs 11.5% at source) leans "
                      "rho HIGH of source"),
        "observed": (f"verdict {verdict['verdict']}, rho "
                     f"{primary['target_point']:.4f} "
                     f"(source {primary['source_point']:.4f}, delta "
                     f"{primary['delta']:+.4f})"),
        "outcome": ("HELD" if verdict["verdict"] == "ORDER_TRANSPORTS"
                    and in_band else "MISSED"),
        "detail": ("rho landed BELOW source, not above: the direction of the "
                   "lean is wrong as well as its cell"
                   if primary["delta"] < 0 else
                   "rho landed above source as leaned"),
    }, {
        "lean": "L2",
        "statement": ("dwell dominance transports — the stay-rate arm keeps a "
                      "detected rho and same-state adjacency stays the "
                      "majority share"),
        "observed": (f"stay-arm rho {stay['target_point']:.4f} "
                     f"{stay['target_ci']}, dwell share {dwell:.4f} "
                     f"(source {SEALED_DWELL_SHARE:.4f})"),
        "outcome": ("HELD" if stay["target_ci"][0] > 0.0 and dwell > 0.5
                    else "MISSED"),
    }, {
        "lean": "L3",
        "statement": "branch flat and residual REPRODUCE; path SHIFTS plausibly",
        "observed": "; ".join(
            f"{row['key']} {row['classification']}"
            for row in branch_rows if row["arm"] == "full"),
        "outcome": _lean_l3(branch_rows),
    }, {
        "lean": "L4",
        "statement": "stable depths REPRODUCE or SHIFT by one",
        "observed": "; ".join(
            f"{row['arm']} {row['target_depths']} vs {row['source_depths']} "
            f"-> {row['classification']}" for row in depth_rows),
        "outcome": ("HELD" if all(row["classification"] in
                                  ("DEPTHS_REPRODUCE", "DEPTHS_SHIFT")
                                  for row in depth_rows) else "MISSED"),
    }, {
        "lean": "L5",
        "statement": ("clean arm transports in the same cell as the full arm "
                      "(the U/W identity-robust pattern)"),
        "observed": "; ".join(
            f"{row['key']} {row['target_cell']}" for row in branch_rows
            if row["arm"] == "clean"),
        "outcome": ("HELD" if all(row["target_cell"] == "ABOVE_CHANCE"
                                  for row in branch_rows
                                  if row["arm"] == "clean") else "MISSED"),
    }]
    return leans


def _lean_l3(branch_rows: Sequence[dict[str, Any]]) -> str:
    full = {row["key"]: row["classification"] for row in branch_rows
            if row["arm"] == "full"}
    flat_ok = full.get("full.flat_auc") in ("REPRODUCES", "RESOLVES")
    residual_ok = full.get("full.terminal_residual_auc") in ("REPRODUCES",
                                                             "RESOLVES")
    if flat_ok and residual_ok:
        return "HELD"
    if flat_ok or residual_ok:
        return "PARTIAL"
    return "MISSED"


# ---------------------------------------------------------------------------
# Stage 6 — the ID-leak gate under the #83 HEAD-identical policy
# ---------------------------------------------------------------------------


def baseline_hit_keys(paths: Sequence[Path], universe: Sequence[str],
                      workdir: Path) -> tuple[set[tuple[str, int]],
                                              dict[str, Any]]:
    """Hits already present in each file's HEAD version, by (name, line).

    Standing policy adopted at the W1 adjudication (#83): over a 10,296-name
    universe the substring scan acquires DICTIONARY COLLISIONS — ordinary
    words and bare digit runs that happen to be author names and that occur in
    committed prose predating this leg.  A collision is separated from a leak
    MECHANICALLY: a hit is PRE-EXISTING iff the identical hit (same file, same
    line) is produced by the same scanner on the file's version at HEAD.
    Files this leg authors have no HEAD version, so their tolerance is ZERO.
    The blocking gate is NEW hits = 0.
    """

    workdir.mkdir(parents=True, exist_ok=True)
    recovered: list[Path] = []
    detail: dict[str, Any] = {}
    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
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
    keys = {(Path(hit["path"]).name, int(hit["line"])) for hit in scan["hits"]}
    return keys, {"files": detail, "n_baseline_hits": scan["n_hits"],
                  "baseline_keys": sorted(f"{name}:{line}"
                                          for name, line in keys)}


def new_hits_only(hits: Sequence[dict[str, Any]],
                  baseline_keys: set[tuple[str, int]]) -> list[dict[str, Any]]:
    return [hit for hit in hits
            if (Path(hit["path"]).name, int(hit["line"])) not in baseline_keys]


def run_id_gate(universe: Sequence[str], output: Path,
                log: RunLog) -> dict[str, Any]:
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
    scan["policy"] = ("#83 HEAD-identical: a raw hit is pre-existing only if "
                      "the same scanner reproduces the identical hit at the "
                      "same file and line on that file's HEAD version; "
                      "leg-authored files carry zero tolerance")
    write_json(output / "id_leak_scan.json", scan)
    log.event("id_leak_scan", status=scan["status"], raw=scan["n_hits"],
              new_hits=scan["n_new_hits"],
              pre_existing=scan["n_pre_existing_hits"],
              universe=len(universe))
    return scan


def build_universe(cohort_path: Path, cache_authors: Sequence[str],
                   output: Path) -> list[str]:
    cohort_names = pd.read_csv(cohort_path, usecols=["author"])["author"]
    universe = sorted({str(n) for n in cohort_names}
                      | {str(n) for n in cache_authors})
    write_json(output / "id_scan_universe.json",
               {"n_names": len(universe),
                "cohort_names": int(len(set(str(n) for n in cohort_names))),
                "disjoint_names": int(len(cache_authors)),
                "note": "gitignored; the scan list is never committed"})
    return universe


# ---------------------------------------------------------------------------
# Report (rule 24: every number below is generated from the artifacts)
# ---------------------------------------------------------------------------


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        if not np.isfinite(value):
            return "—"
        return f"{value:.{digits}f}"
    return str(value)


def fmt_ci(pair: Sequence[float] | None, digits: int = 4) -> str:
    if pair is None:
        return "absent"
    return f"[{fmt(float(pair[0]), digits)}, {fmt(float(pair[1]), digits)}]"


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []

    def add(text: str = "") -> None:
        lines.append(text)

    verdict = payload["verdict"]
    order = payload["order"]
    order_full = payload["order_full_pool"]
    branch = payload["branch"]
    rows_order = payload["transport"]["order"]
    rows_branch = payload["transport"]["branch"]
    rows_depth = payload["transport"]["depths"]
    anchors = payload["anchors"]
    draws = payload["draws"]
    instrument = payload["instrument"]
    scan = payload["id_leak_scan"]
    primary = next(r for r in rows_order if r["key"] == "primary")

    add("# SUICA M4-W2 — fast-time and branch-code transport")
    add()
    statement = verdict["statement"]
    add(f"**VERDICT: `{verdict['verdict']}` (cell {verdict['cell_number']} of "
        f"3).** {statement[0].upper()}{statement[1:]}.")
    add()
    add(f"The order family routes: the size-matched primary rho is "
        f"{fmt(primary['target_point'])} {fmt_ci(primary['target_ci'])} on "
        f"{verdict['gallery_n']} authors who share nobody with the source "
        f"cohort, against U1's sealed {fmt(primary['source_point'])} "
        f"{fmt_ci(primary['source_ci'])} on 984. Both points sit in U1's "
        f"`ORDER_CHANNEL` cell; the intervals "
        f"{'overlap' if primary['ci_overlap'] else 'are disjoint'}, so the row "
        f"classifies **{primary['classification']}**.")
    add()
    add(f"The branch family is co-primary and carries #73 flags without "
        f"routing: {payload['flags_73_count']} divergence flag(s) are raised "
        f"below. Generated {payload['generated_utc']} from "
        f"`{payload['config']['output_dir']}`.")
    add()

    add("## 1. Anchor gates (#78) — blocking, re-executed on the W1 cache")
    add()
    add("| anchor | registered | observed | status |")
    add("|---|---|---|---|")
    for key, expected in anchors["expected"].items():
        observed = anchors["observed"][key]
        ok = "PASS" if expected == observed else "**FAIL**"
        add(f"| {key} | {expected} | {observed} | {ok} |")
    add(f"| law vocabulary identical to the cache's list | True | "
        f"{anchors['vocabulary_identical_to_cache']} | "
        f"{'PASS' if anchors['vocabulary_identical_to_cache'] else '**FAIL**'} |")
    add()
    add(f"All {anchors['n_anchors']} anchors reproduce ({anchors['status']}). "
        f"The law vocabulary was recomputed from the cache by SR0's rule — "
        f"distinct cohort users per subreddit, floor "
        f"ceil({VOCAB_FLOOR_FRACTION} × {anchors['observed']['authors_seen']}) "
        f"= {anchors['observed']['vocab_floor_users']} — and the resulting "
        f"{anchors['observed']['law_vocabulary']}-community list is identical "
        f"to the one W1 carried, not merely the same length.")
    add()

    add("## 2. The size-matched draws (the W1 adjudication's binding correction)")
    add()
    add("Pooled same-vs-different AUC is a function of GALLERY SIZE: a larger "
        "gallery offers more impostors and drives the pooled AUC down. U1's "
        "and T1's sealed values were measured at N = 984 and N = 1,304, so a "
        "full-pool comparison would confound transport with gallery size. The "
        "primary arms therefore run at exactly the source sizes.")
    add()
    add("| draw | order | source pool (censused) | N drawn | digest |")
    add("|---|---|---|---|---|")
    add(f"| order subpool | 1st | {draws['order_source_pool']} | "
        f"{draws['order_n']} | `{draws['order_digest']}` |")
    add(f"| branch subpool | 2nd | {draws['branch_source_pool']} | "
        f"{draws['branch_n']} | `{draws['branch_digest']}` |")
    add()
    add(f"One stream: `{draws['rng']}`. The order draw is taken FIRST and the "
        f"branch draw continues the same stream, so the draw ORDER is part of "
        f"the pin — swapping them changes both subpools. Both draws are "
        f"uniform without replacement and are sorted ascending before use. "
        f"{draws['authors_in_both_draws']} authors appear in both draws, which "
        f"is expected and harmless: the two families are separate "
        f"instruments, not a joint test.")
    add()

    add("## 3. Order family — the verdict router")
    add()
    add("| arm | gallery N | size-matched | rho (target) | 95% CI | "
        "rho (source) | source CI | delta | class |")
    add("|---|---|---|---|---|---|---|---|---|")
    for row in rows_order:
        add(f"| {row['quantity']} | {row['target_gallery_n']} | "
            f"{'yes' if row['size_matched'] else 'NO'} | "
            f"{fmt(row['target_point'])} | {fmt_ci(row['target_ci'])} | "
            f"{fmt(row['source_point'])} | {fmt_ci(row['source_ci'])} | "
            f"{row['delta']:+.4f} | **{row['classification']}** |")
    add()
    add("Every AUC row above is size-matched: the target gallery is "
        f"{order['gallery_n']} authors and the source gallery was 984, so the "
        "rho comparison is a like-for-like comparison of gallery-matched "
        "pooled AUCs. Nothing in this table compares a 984-author AUC with a "
        f"{order_full['gallery_n']}-author AUC.")
    add()
    add("### 3.1 Null locations against the bag ceiling")
    add()
    add("| arm | AUC real | exact-bag null mean | null 95% band | "
        "unigram bag AUC | null − bag | real − bag | shuffle p | bag exact |")
    add("|---|---|---|---|---|---|---|---|---|")
    for row in rows_order:
        add(f"| {row['key']} | {fmt(row['auc_real'])} | "
            f"{fmt(row['auc_null_mean'])} | {fmt_ci(row['auc_null_band'])} | "
            f"{fmt(row['bag_auc_unigram'])} | {row['null_minus_bag']:+.4f} | "
            f"{row['real_minus_bag']:+.4f} | {fmt(row['shuffle_p_value'], 3)} | "
            f"{row['bag_invariance_exact']} |")
    add()
    target_gap = rows_order[0]["null_minus_bag"]
    source_gap = payload["source_null_locations"]["primary"]
    add("The exact-bag shuffle destroys ORDER while holding each half's "
        "community bag EXACTLY fixed (verified bit-for-bit per fold, the "
        "`bag exact` column). The null therefore sits where a pure bag "
        "instrument sits, and rho reads the excess that only adjacency "
        "carries. The raw-adjacency null lands "
        f"{abs(target_gap):.4f} {'below' if target_gap < 0 else 'above'} the "
        f"unigram bag ceiling; at source the same gap was "
        f"{source_gap:+.4f}, i.e. on the "
        f"{'same' if np.sign(target_gap) == np.sign(source_gap) else 'OPPOSITE'}"
        f" side, and the two differ by {abs(target_gap - source_gap):.4f}.")
    add()
    add("### 3.2 Full-pool sensitivity (registered, NOT size-matched)")
    add()
    add("| arm | gallery N | rho | 95% CI | AUC real | null mean | "
        "cell (with CI support) |")
    add("|---|---|---|---|---|---|---|")
    for key, arm in order_full["arms"].items():
        add(f"| {key} | {order_full['gallery_n']} | {fmt(arm['rho'])} | "
            f"{fmt_ci(arm['rho_ci'])} | {fmt(arm['auc_real'])} | "
            f"{fmt(arm['auc_null_mean'])} | {order_cell_of(arm)} |")
    add()
    if order_full["arms"]:
        full_cell = order_cell_of(order_full["arms"]["primary"])
        matched_cell = primary["arm_cell_with_ci_support"]
        add(f"This row is **not** size-matched and must not be read as a "
            f"transport comparison against U1's 984-author value: the gallery "
            f"is {order_full['gallery_n']} authors, "
            f"{order_full['gallery_n'] / N_ORDER_SUBPOOL:.2f}× the source. It "
            f"answers a different question — whether the channel survives at "
            f"the cohort's full censused scale — and it lands in cell "
            f"`{full_cell}`, "
            f"{'the same as' if full_cell == matched_cell else 'DIFFERENT from'}"
            f" the size-matched arm's `{matched_cell}`. The rho level itself "
            f"moves by "
            f"{order_full['arms']['primary']['rho'] - primary['target_point']:+.4f} "
            f"across the {order_full['gallery_n'] / N_ORDER_SUBPOOL:.2f}× "
            f"gallery change, which is the size effect the W1 adjudication "
            f"required this leg to hold fixed in the primary arms.")
    else:
        add("The full-pool sensitivity arm was SKIPPED in this run.")
    add()

    add("## 4. Branch family — co-primary, #73 flags, never routing")
    add()
    add("| arm | quantity | gallery N (valid) | size-matched | AUC (target) | "
        "95% CI | AUC (source) | source CI | delta | class |")
    add("|---|---|---|---|---|---|---|---|---|---|")
    for row in rows_branch:
        add(f"| {row['arm']} | {row['quantity']} | {row['target_gallery_n']} | "
            f"{'yes' if row['size_matched'] else 'NO'} | "
            f"{fmt(row['target_point'])} | {fmt_ci(row['target_ci'])} | "
            f"{fmt(row['source_point'])} | {fmt_ci(row['source_ci'])} | "
            f"{row['delta']:+.4f} | **{row['classification']}**"
            f"{' ⚑' if row['classification'] in ('SHIFTS', 'BREAKS') else ''} |")
    add()
    add(f"Size-matching statement for every AUC row above: the branch draw is "
        f"N = {branch['gallery_n_input']} authors, exactly T1's input size; "
        f"after the pipeline's own validity filter (both halves must have "
        f"non-zero norm) the realised gallery is "
        f"{rows_branch[0]['target_gallery_n']} against T1's 1,304 for the "
        f"full arm and 1,269 for the clean arm. The residual gallery "
        f"difference is under half a percent and is stated, not corrected.")
    add()
    add(f"**Missing source intervals (registered rule).** T1's committed "
        f"artifacts carry per-depth gain CIs but no interval for any of the "
        f"three AUCs, so all {len(payload['t1_source_intervals']['missing'])} "
        f"branch AUC rows fall to the registered fallback: classify by "
        f"point-in-TARGET-CI and FLAG the missing interval. The flag stands "
        f"for every branch AUC row in the table above.")
    add()
    biases = [row["target_ci_bias"] for row in rows_branch]
    add(f"The target intervals are this leg's own instrument (RD-W2-2): an "
        f"author-level cluster bootstrap, B = {branch['bootstrap']['b']}, "
        f"re-running the SAME pinned function on each resample. A "
        f"with-replacement author draw seeds the gallery with duplicated "
        f"authors, and a duplicate scores as high as the true match while "
        f"being labelled 'different', which perturbs the pooled AUC. The "
        f"measured bias runs from {min(biases):+.4f} to {max(biases):+.4f} "
        f"across the six rows; it is reported per row rather than assumed, "
        f"and the bias-corrected ('basic') interval is carried alongside so "
        f"the class can be checked under both:")
    add()
    add("| arm | quantity | percentile CI | bootstrap bias | basic (recentred) CI"
        " | class under the basic CI |")
    add("|---|---|---|---|---|---|")
    for row in rows_branch:
        alt = classify_four_class(row["source_ci"], row["target_ci_basic"],
                                  row["source_point"], row["target_point"],
                                  auc_cell_of)["classification"]
        add(f"| {row['arm']} | {row['quantity']} | {fmt_ci(row['target_ci'])} | "
            f"{row['target_ci_bias']:+.4f} | {fmt_ci(row['target_ci_basic'])} | "
            f"{alt} |")
    add()
    add("### 4.1 Depth-by-depth gains and the triple gate")
    add()
    add("| arm | depth | n | centroid gain | 95% CI | gain p | branch excess | "
        "branch p | excess bits | bits p | stable |")
    add("|---|---|---|---|---|---|---|---|---|---|---|")
    for arm_name, arm in branch["arms"].items():
        stable = set(arm["stable_depths"])
        for row in arm["metrics_by_depth"]:
            add(f"| {arm_name} | {row['depth']} | {row['n']} | "
                f"{fmt(row['gain_mean'], 5)} | "
                f"[{fmt(row['gain_ci_low'], 5)}, {fmt(row['gain_ci_high'], 5)}] | "
                f"{fmt(row['gain_permutation_p'], 3)} | "
                f"{fmt(row['branch_excess'])} | "
                f"{fmt(row['branch_permutation_p'], 3)} | "
                f"{fmt(row['conditional_information_bits'] - row['information_null_mean'])} | "
                f"{fmt(row['information_permutation_p'], 3)} | "
                f"{'yes' if row['depth'] in stable else 'no'} |")
    add()
    add("| arm | stable depths (target) | stable depths (source) | "
        "symmetric difference | class |")
    add("|---|---|---|---|---|")
    for row in rows_depth:
        add(f"| {row['arm']} | {row['target_depths']} | {row['source_depths']} | "
            f"{row['symmetric_difference'] or '∅'} | "
            f"**{row['classification']}** |")
    add()
    add(f"### 4.2 Clean arm (governance echo)")
    add()
    add(f"The clean arm removes the "
        f"{branch['n_removed_typology_communities']} explicitly named "
        f"typology communities present in the law vocabulary and rebuilds the "
        f"author vectors (the removed columns are zeroed and the Hellinger "
        f"normalisation is re-applied inside the pinned function — T1's exact "
        f"pattern). Its rows appear in the tables above. The removed set is "
        f"in `arms.json`; the names are community names, never author names.")
    add()

    add("## 5. Cohort-instrument notes")
    add()
    add("| instrument quantity | this cohort | source cohort | note |")
    add("|---|---|---|---|")
    spliced = instrument["in_law_vocabulary_spliced"]
    add(f"| timestamp tie rate (in-law-vocab spliced adjacency) | "
        f"{fmt(spliced['tie_rate'], 5)} | {fmt(SOURCE_TIE_RATE_IN_VOCAB, 5)} | "
        f"an attenuation source present at source and essentially ABSENT here "
        f"({SOURCE_TIE_RATE_IN_VOCAB / spliced['tie_rate']:.1f}× lower) |")
    add(f"| session share (gap ≤ 1 h, same denominator) | "
        f"{fmt(spliced['session_share'], 5)} | "
        f"{fmt(payload['source_descriptives']['session_pair_share'], 5)} | "
        f"denominators differ (whole-cohort splice here, pooled test folds at "
        f"source) |")
    add(f"| cross-thread share (all adjacencies) | "
        f"{fmt(instrument['all_events']['cross_thread_share'], 5)} | "
        f"{fmt(payload['source_descriptives']['cross_thread_pair_share'], 5)} | "
        f"same caveat |")
    add(f"| same-state adjacency share (dwell dominance) | "
        f"{fmt(order['descriptives']['stay_share_of_all_pairs'], 4)} | "
        f"{fmt(SEALED_DWELL_SHARE, 4)} | descriptive, pooled over test folds "
        f"in both cohorts |")
    add(f"| OOV state occupancy | "
        f"{fmt(order['descriptives']['oov_state_occupancy'], 4)} | "
        f"{fmt(payload['source_descriptives']['oov_state_occupancy'], 4)} | "
        f"descriptive |")
    add()
    add("The tie rate is the registration's named cohort-instrument "
        "difference. Tied timestamps are order-free events that the shuffle "
        "cannot move informatively, so they attenuate the REAL adjacency "
        "signal at source and barely exist here. The registered lean read "
        "that as a reason to expect rho HIGH of source. The realised "
        f"direction is the opposite ({primary['delta']:+.4f}), which is "
        "recorded as an honest anomaly rather than explained away.")
    add()

    add("## 6. Projection versus lean")
    add()
    add("| lean | statement | observed | outcome |")
    add("|---|---|---|---|")
    for lean in payload["leans"]:
        add(f"| {lean['lean']} | {lean['statement']} | {lean['observed']} | "
            f"**{lean['outcome']}** |")
    add()
    for lean in payload["leans"]:
        if lean.get("detail"):
            add(f"- **{lean['lean']}**: {lean['detail']}.")
    add()

    add("## 7. Boundaries")
    add()
    for boundary in payload["boundaries"]:
        add(f"- {boundary}")
    add()

    add("## 8. Gates")
    add()
    add("| gate | status |")
    add("|---|---|")
    for name, status in payload["gates"].items():
        add(f"| {name} | {status} |")
    add()
    add(f"The ID-leak universe is every author name in the comments file — "
        f"{scan['universe_size']:,} candidates, the "
        f"{scan['baseline']['n_baseline_hits']}-hit HEAD baseline separated "
        f"mechanically under #83. Raw hits on the committed files: "
        f"{scan['n_hits']}; pre-existing (identical file and line at HEAD): "
        f"{scan['n_pre_existing_hits']}; **NEW: {scan['n_new_hits']}**. Only "
        f"NEW hits block.")
    add()

    add("## 9. Configuration")
    add()
    add("```json")
    add(json.dumps(payload["config"], indent=2, sort_keys=True))
    add("```")
    add()
    add(f"Wall clock: order size-matched "
        f"{payload['timings']['order_matched_s']} s, order full-pool "
        f"{payload['timings']['order_full_s']} s, branch arms "
        f"{payload['timings']['branch_arms_s']} s, branch AUC bootstrap "
        f"{payload['timings']['branch_bootstrap_s']} s.")
    add()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_boundaries(payload: dict[str, Any]) -> list[str]:
    primary = next(r for r in payload["transport"]["order"]
                   if r["key"] == "primary")
    branch = payload["branch"]
    return [
        "**EXPLORATORY, corpus-level.** Both families are measured over a "
        "single Reddit comment corpus with one splitting rule. Nothing here "
        "licenses a claim about persons outside this corpus, and nothing here "
        "is preregistered in the confirmatory sense — the sealed predictions "
        "were fixed before the run, but the source values were themselves "
        "produced by exploratory legs.",
        "**Typology-enriched cohort.** The disjoint cohort was recovered from "
        "the same comments file as the source cohort, whose recruitment ran "
        "through typology forums. The law vocabulary contains "
        f"{branch['n_removed_typology_communities']} explicitly named "
        "typology communities, and the clean arm exists precisely because "
        "that enrichment is a live confound for any 'community selection' "
        "reading.",
        "**Size-matching is a correction, not a cure.** Matching the gallery "
        "removes the gallery-size confound from the AUC comparison; it does "
        "not make the two cohorts exchangeable in any other respect. Event "
        "volume, tie structure, session structure and community mix all "
        "differ, and each of them can move a pooled AUC.",
        "**The eq-12 projection caution stands.** Width projections and "
        "level projections are different objects. This leg projected LEVELS "
        "(sealed points and their cells) and made no width projection; the "
        "#79b/#80b width machinery is not exercised here, and its two "
        "consecutive hits at W1 must not be read as licensing level "
        "projection.",
        f"**rho is a ratio against a moving null.** rho = (AUC_real − "
        f"null)/(1 − null) is measured against an exact-bag null that is "
        f"itself cohort-specific (here {fmt(primary['auc_null_mean'])}, at "
        f"source {fmt(payload['source_auc']['primary']['auc_null_mean'])}). A "
        f"rho difference can come from the numerator, the denominator, or "
        f"both; this leg reports the raw AUCs and the null locations so the "
        f"decomposition stays visible.",
        "**Branch AUC intervals are executor-supplied.** The registration "
        "pinned no interval instrument for T1's three AUCs because T1 "
        "produced none. The cluster bootstrap used here is the house "
        "instrument, but it is NOT the sealed source's instrument, and a "
        "REPRODUCES verdict on those rows rests on an interval that the "
        "source leg never had.",
        "**Label-free.** No personality label of any kind was read. "
        "`author_profiles.csv` was never opened. Nothing in this leg speaks "
        "to what any author is like — only to whether two halves of the same "
        "author's stream can be matched, and by what channel.",
    ]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_config(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "leg": "M4-W2",
        "registration": ("docs/SUICA_M4_W_DISJOINT_TRANSPORT_PLAN.md :: "
                         "## W2 — fast-time and branch-code transport "
                         "(registered BEFORE run, 2026-08-18)"),
        "seed": SEED,
        "n_folds": N_FOLDS,
        "order": {
            "c_states": C_PRIMARY,
            "alpha": U1.ALPHA,
            "lens": "hellinger_joint (bigram joint next-state counts)",
            "pool_min_per_half": ORDER_POOL_MIN_PER_HALF,
            "subpool_n": N_ORDER_SUBPOOL,
            "b_shuffle": B_SHUFFLE,
            "b_bootstrap": B_BOOTSTRAP,
            "b_boot_shuffle_matched": B_BOOT_SHUFFLE,
            "b_boot_shuffle_full_pool": B_BOOT_SHUFFLE_FULLPOOL,
            "kmeans_n_init": U1.KMEANS_N_INIT,
            "cluster_seed": "SEED + 1000 * fold",
            "arms": [spec.key for spec in ORDER_ARMS],
        },
        "branch": {
            "max_depth": BRANCH_MAX_DEPTH,
            "min_leaf": BRANCH_MIN_LEAF,
            "subpool_n": N_BRANCH_SUBPOOL,
            "min_events": BRANCH_MIN_EVENTS,
            "permutations": BRANCH_PERMUTATIONS,
            "bootstrap": BRANCH_BOOTSTRAP,
            "auc_bootstrap": BRANCH_AUC_BOOTSTRAP,
            "input": "sqrt frequency / Hellinger unit sphere (inside suica_core)",
        },
        "machinery": {
            "order": "scripts/run_suica_m4_u1_order_identity.py (imported by file)",
            "branch": ("suica_core.hierarchical_selection_identity."
                       "cross_fitted_hierarchical_identity"),
            "cache": str(W1_CACHE.relative_to(ROOT)),
        },
        "vocabulary": {"rule": "SR0 distinct-user floor",
                       "floor_fraction": VOCAB_FLOOR_FRACTION,
                       "floor_users": CENSUS_VOCAB_FLOOR_USERS,
                       "size": CENSUS_LAW_VOCAB},
        "label_free": True,
        "output_dir": relative_to_root(Path(args.output)),
    }


def relative_to_root(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=W1_CACHE)
    parser.add_argument("--cohort", type=Path, default=DEFAULT_COHORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--stage", choices=("all", "id-scan"), default="all")
    parser.add_argument("--auc-bootstrap", type=int,
                        default=BRANCH_AUC_BOOTSTRAP)
    parser.add_argument("--skip-full-pool", action="store_true",
                        help="debug only; the full-pool arm is registered")
    args = parser.parse_args(argv)

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    log = RunLog(output / ("run_log.jsonl" if args.stage == "all"
                           else "run_log_id_scan.jsonl"))

    cache = load_scaffold(Path(args.cache))

    if args.stage == "id-scan":
        universe = build_universe(Path(args.cohort), cache.authors, output)
        scan = run_id_gate(universe, output, log)
        if scan["status"] != "PASS":
            raise SystemExit(
                f"STOP: ID-leak scan FAILED on NEW hits: {scan['new_hits']}")
        print(f"ID-leak gate {scan['status']}: raw {scan['n_hits']}, "
              f"pre-existing {scan['n_pre_existing_hits']}, "
              f"NEW {scan['n_new_hits']}")
        return 0

    log.event("start", cache=str(args.cache), events=int(cache.author_code.size))

    # ---- Stage 0: anchors -------------------------------------------------
    vocab = law_vocabulary(cache)
    segments = author_segments(cache)
    instrument = instrument_descriptives(cache, segments["event_vocab"])
    anchors = verify_anchors(cache, vocab, segments, instrument)
    write_json(output / "anchors.json", anchors)
    log.event("anchors", **{"status": anchors["status"],
                            **anchors["observed"]})
    if anchors["status"] != "PASS":
        raise SystemExit(f"STOP: anchor mismatch {anchors['mismatches']}")

    # ---- Stage 1: draws ---------------------------------------------------
    draws = seeded_subpools(segments["order_pool"], segments["branch_pool"])
    write_json(output / "draws.json",
               {k: v for k, v in draws.items()
                if k not in ("order_subpool", "branch_subpool")})
    np.savez_compressed(output / "subpool_codes.npz",
                        order_subpool=draws["order_subpool"],
                        branch_subpool=draws["branch_subpool"])
    log.event("draws", order_n=draws["order_n"], branch_n=draws["branch_n"],
              order_digest=draws["order_digest"],
              branch_digest=draws["branch_digest"])

    # ---- Stage 2: order family (size-matched primary) ---------------------
    t0 = time.time()
    matched = restrict_scaffold(cache, draws["order_subpool"])
    order = run_order_family(matched, "size-matched N=984", log,
                             B_BOOT_SHUFFLE)
    order_matched_s = round(time.time() - t0, 1)
    if order["gallery_n"] != N_ORDER_SUBPOOL:
        raise SystemExit("STOP: the size-matched order gallery is not 984 "
                         f"({order['gallery_n']})")

    # ---- Stage 2b: order family (full-pool sensitivity) -------------------
    t0 = time.time()
    if args.skip_full_pool:
        order_full = {"label": "SKIPPED", "gallery_n": 0, "arms": {},
                      "census": {}, "descriptives": {}}
    else:
        order_full = run_order_family(
            cache, "full-pool sensitivity", log, B_BOOT_SHUFFLE_FULLPOOL,
            arms=[spec for spec in ORDER_ARMS if spec.key == "primary"])
    order_full_s = round(time.time() - t0, 1)

    # ---- Stage 3: branch family -------------------------------------------
    t0 = time.time()
    branch = run_branch_family(cache, draws["branch_subpool"], segments, log,
                               args.auc_bootstrap)
    branch_total_s = round(time.time() - t0, 1)
    branch_arms_s = round(sum(a["wall_seconds"] for a in branch["arms"].values()), 1)

    write_json(output / "order_arms.json", order)
    write_json(output / "order_full_pool.json", order_full)
    write_json(output / "branch_arms.json", branch)
    write_json(output / "instrument.json", instrument)

    # ---- Stage 4: transport tables ----------------------------------------
    t1_source = load_t1_source_intervals()
    rows_order = order_transport_rows(order)
    rows_branch = branch_transport_rows(branch, t1_source["present"])
    rows_depth = depth_transport_rows(branch)
    transport = {"order": rows_order, "branch": rows_branch,
                 "depths": rows_depth}
    write_json(output / "transport_table.json", transport)

    # ---- Stage 5: verdict and leans ---------------------------------------
    verdict = route_verdict(rows_order, order)
    leans = evaluate_leans(rows_order, order, rows_branch, rows_depth, verdict)
    flags = [row["key"] for row in rows_branch + rows_depth
             if row["classification"] in ("SHIFTS", "BREAKS", "DEPTHS_SHIFT",
                                          "DEPTHS_BREAK")]
    write_json(output / "verdict.json",
               {**verdict, "flags_73": flags, "leans": leans})
    log.event("verdict", **{k: verdict[k] for k in
                            ("verdict", "cell_number", "primary_rho",
                             "primary_classification")})

    # ---- source descriptives for the report (from U1's committed artifacts)
    source_descriptives = json.loads(
        (U1_ARTIFACTS / "descriptives.json").read_text(encoding="utf-8"))
    source_arms = json.loads(
        (U1_ARTIFACTS / "arms.json").read_text(encoding="utf-8"))
    source_null_locations = {a["arm"]: float(a["null_minus_bag"])
                             for a in source_arms
                             if a["arm"] in SEALED_ORDER}
    source_auc = {a["arm"]: {k: float(a[k]) for k in
                             ("auc_real", "auc_null_mean", "bag_auc_unigram")}
                  for a in source_arms if a["arm"] in SEALED_ORDER}

    config = build_config(args)
    gates = {
        f"anchor gates (#78), {anchors['n_anchors']} of them": anchors["status"],
        "fold purity (no test-author mass in any state map)":
            order["fold_purity"]["status"],
        "exact-bag invariance, every order arm":
            "PASS" if all(a["bag_invariance_exact"]
                          for a in order["arms"].values()) else "FAIL",
        "size matching, order gallery == 984":
            "PASS" if order["gallery_n"] == N_ORDER_SUBPOOL else "FAIL",
        "size matching, branch draw == 1304":
            "PASS" if branch["gallery_n_input"] == N_BRANCH_SUBPOOL else "FAIL",
    }

    payload = {
        "generated_utc": utc_now(),
        "verdict": verdict,
        "anchors": anchors,
        "draws": {k: v for k, v in draws.items()
                  if k not in ("order_subpool", "branch_subpool")},
        "instrument": instrument,
        "order": order,
        "order_full_pool": order_full,
        "branch": branch,
        "transport": transport,
        "t1_source_intervals": t1_source,
        "leans": leans,
        "flags_73": flags,
        "flags_73_count": len(flags),
        "source_descriptives": source_descriptives,
        "source_null_locations": source_null_locations,
        "source_auc": source_auc,
        "gates": gates,
        "config": config,
        "timings": {
            "order_matched_s": order_matched_s,
            "order_full_s": order_full_s,
            "branch_arms_s": branch_arms_s,
            "branch_bootstrap_s": branch["bootstrap"]["wall_seconds"],
            "branch_total_s": branch_total_s,
        },
    }
    payload["boundaries"] = build_boundaries(payload)

    # ---- Stage 6: ID gate (a FIXED POINT: the reported numbers are the
    # numbers of the file that carries them) --------------------------------
    universe = build_universe(Path(args.cohort), cache.authors, output)
    payload["id_leak_scan"] = {
        "status": "PENDING", "n_hits": 0, "n_new_hits": 0,
        "n_pre_existing_hits": 0, "universe_size": len(universe),
        "baseline": {"n_baseline_hits": 0}}
    write_report(Path(args.report), payload)
    first = run_id_gate(universe, output, log)
    payload["id_leak_scan"] = first
    payload["gates"][
        f"ID-leak scan (0 NEW hits of {len(universe):,} author names)"] = \
        first["status"]
    write_report(Path(args.report), payload)
    scan = run_id_gate(universe, output, log)
    scan["fixed_point"] = bool(
        (scan["n_hits"], scan["n_new_hits"], scan["n_pre_existing_hits"])
        == (first["n_hits"], first["n_new_hits"],
            first["n_pre_existing_hits"]))
    write_json(output / "id_leak_scan.json", scan)
    payload["id_leak_scan"] = scan
    write_json(output / "report_payload.json", payload)

    if scan["status"] != "PASS":
        raise SystemExit(
            f"STOP: ID-leak scan FAILED on NEW hits: {scan['new_hits']}")
    if not scan["fixed_point"]:
        raise SystemExit(
            "STOP: the ID-scan numbers printed in the report are not the "
            "numbers of the report that carries them")

    log.event("done", verdict=verdict["verdict"],
              rho=verdict["primary_rho"], flags=len(flags))
    print(f"\nVERDICT: {verdict['verdict']} (cell {verdict['cell_number']}) — "
          f"rho {verdict['primary_rho']:.4f} {verdict['primary_rho_ci']}, "
          f"{len(flags)} #73 flag(s)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
