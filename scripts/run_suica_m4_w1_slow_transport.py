#!/usr/bin/env python3
"""SUICA M4-W1 — slow-time law transport to the DISJOINT author cohort.

Registered BEFORE the run in ``docs/SUICA_M4_W_DISJOINT_TRANSPORT_PLAN.md``
(commit 11aacd7).  This runner executes that registration and nothing else.

WHAT THIS LEG DOES
------------------
The U-line closed with one interval open: whether the COMMON event mass
outlasts the DISTINCTIVE tail.  U2c's decay-rate contrast
``Λ = λ_distinct − λ_common`` put seven of seven point estimates on one side
(+0.0741/y) but never excluded zero ([−0.0558, +0.1854]).  Same-corpus
escalation was ruled out as significance-chasing.  This leg instead carries
the SEALED laws to a DISJOINT cohort on the same platform: the 8,895 authors
in the PANDORA comments file who are NOT in the 1401-author Big5 cohort —
9.3x the authors, 14.6M comments, no author shared with the source.

Transport semantics (Q-line vocabulary): a LAW transports when its
RE-INSTANTIATED measurement on a fresh cohort reproduces it; an INSTRUMENT
transports when the FROZEN artifact does.  The law arm is primary; the
instrument arm (frozen 1191 vocabulary + frozen 32-community Common set) is
sensitivity.

MACHINERY (#81: pinned BY FORMULA with provenance, reused by import-by-file)
---------------------------------------------------------------------------
Every estimator in this leg is the committed U-line object, imported from
``scripts/run_suica_m4_u2c_decay_rate_contrast.py`` (which imports U2b, which
imports U2).  Nothing is reimplemented:

* ``U2.build_blocks``       — disjoint consecutive K=50 in-vocabulary blocks
                              per author; features sqrt(count/K), L2; block
                              midpoint = mean of first and last timestamps.
* ``U2.assign_quarters``    — epoch cells of 91.3 days from the corpus min.
* ``U2.gap_bin``            — the five verdict bins + the 3y+ descriptive bin.
* ``U2.compute_arm``        — E(b) = mean same-author cosine MINUS the
                              epoch-matched EXACT STRATIFIED cross mean
                              (RD-U2-1 form); the within-quarter permutation
                              scaffold; the author cluster bootstrap.
* ``U2B.community_ranking`` / ``common_prefix`` — the event-mass split.
* ``U2B.block_counts_over`` / ``renormalize`` — the carrier restriction.
* ``U2B.self_pair_census``  — the gate's exact pair predicate.
* ``U2B.ppmi_svd`` / ``first_half_counts`` / ``taste_folds`` /
  ``pool_fold_results`` — the taste row.
* ``U2C.log_slope_fit`` / ``linear_slope`` / ``summarize_lambda`` /
  ``rate_contrast`` / ``classify_lambda`` — λ, Λ, the domain-safe linear null
  (#80a) and the three registered cells.
* ``U2.scan_for_cohort_ids`` — the ID-leak gate, here over the WIDENED
  universe of all 10,296 author names.

WHAT IS NEW HERE (and only this)
--------------------------------
1. the DISJOINT events cache (the U1 cache-builder pattern under the negated
   cohort predicate, streamed chunked, no bodies);
2. the census anchor gates of the W1 registration (#78, BLOCKING);
3. the sealed-prediction TRANSPORT TABLE and its REPRODUCES / SHIFTS / BREAKS
   classification (#75-keyed, SECONDARY — it never routes the verdict).

GOVERNANCE
----------
Label-free: ``author_profiles.csv`` is NEVER opened anywhere in this leg.
The disjoint cohort listing and the events cache live in gitignored
``results/`` and are never committed.  Aggregates only.  EXPLORATORY,
corpus-level.  The disjoint cohort is TYPOLOGY-ENRICHED by construction
(PANDORA's non-Big5 authors are MBTI-labelled users; 8 of the law arm's 71
Common communities are typology names) — that is a cohort-composition caveat
on every transport claim in this report, not a nuisance to be absorbed.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Configuration constants (registration pins first, then recorded choices).
# ---------------------------------------------------------------------------

SEED = 20260818                     # registration pin
B_PERM = 499                        # registration pin
B_BOOT = 1000                       # registration pin

Q_PRIMARY = 0.5                     # registration pin: the split level
M_PRIMARY = 10                      # registration pin: the verdict floor
M_SENSITIVITY = 5                   # registration pin: sensitivity floor

VOCAB_FLOOR_FRACTION = 0.01         # SR0's rule, re-instantiated (U1 line 65)
DAYS_PER_YEAR = 365.25              # inherited from U2c

# --- the W1 census (planner arithmetic #43, predicates exact #77/#78) -------
# Every one of these is BLOCKING: the executor re-executes the predicate and
# STOPS on any mismatch.
CENSUS_DISJOINT_EVENTS = 14_634_702
CENSUS_AUTHORS_SEEN = 8_895
CENSUS_VOCAB_FLOOR_USERS = 89       # ceil(0.01 * 8895)
CENSUS_LAW_VOCAB = 1_443
CENSUS_LAW_COVERAGE = 0.7587        # rounded to 4 dp
CENSUS_COMMON_Q50 = 71
CENSUS_TYPOLOGY_IN_VOCAB = 22
CENSUS_TYPOLOGY_IN_COMMON = 8
CENSUS_POOL_AUTHORS = 6_111
CENSUS_POOL_BLOCKS = 213_489
CENSUS_QUARTERS = 18
CENSUS_SELF_PAIRS_2_3Y = 2_591_663
CENSUS_GATE_M10_PAIRS = 1_211_631
CENSUS_GATE_M10_AUTHORS = 3_241
CENSUS_GATE_M5_PAIRS = 1_790_865
CENSUS_GATE_M5_AUTHORS = 3_746

# Sufficiency targets (#69), trivially cleared here; stated for form.
POOL_GATE_MIN_PAIRS_2_3Y = 100_000
POOL_GATE_MIN_AUTHORS_2_3Y = 400

# The frozen INSTRUMENT objects (sensitivity arm).
FROZEN_VOCAB_SIZE = 1_191           # U1/U2's SR0 vocabulary on the 1401
FROZEN_COMMON_SIZE = 32             # U2b's Common(0.5) on the 1401

# The clean arm: T1's explicit-typology removal set, re-derived on this
# cohort's law vocabulary (22 of the 23 T1 names are present here).
CLEAN_ARM_EXPECTED_REMOVED = 22

# --- sealed predictions (source values quoted from the registration) -------
# Provenance of each source number, so the table is auditable:
#   Λ, λ_full           -> U2c primary arm (q=0.5/m=5 intersection set)
#   floor share, D      -> U2's primary arm (the 849-author pool, full vocab)
# The heterogeneity is the registration's; it is disclosed in the report.
SEALED: dict[str, dict[str, Any]] = {
    "lambda_contrast": {
        "label": "Λ = λ_distinct − λ_common",
        "point": 0.0741, "ci": [-0.0558, 0.1854],
        "source": "U2c primary arm (cohort 849 pool / 424 gate authors)",
    },
    "floor_share_full": {
        "label": "floor share E(2–3y)/E(0–90d), full row",
        "point": 0.5348, "ci": [0.4203, 0.6320],
        "source": "U2 primary arm (849-author pool, full vocabulary)",
    },
    "d_full": {
        "label": "D = E(0–90d) − E(2–3y), full row",
        "point": 0.3058, "ci": [0.2364, 0.3855],
        "source": "U2 primary arm (849-author pool, full vocabulary)",
    },
    "lambda_full": {
        "label": "λ_full",
        "point": 0.2943, "ci": [0.1895, 0.4405],
        "source": "U2c primary arm (cohort 849 pool / 424 gate authors)",
    },
}
SEALED_ORDERING = ("λ_taste is the SMALLEST of the four rows "
                   "(held in both U2c arms)")

# Registration-time projection for Λ (#79b/#80b), reported against realized.
PROJECTED_HALF_WIDTH = 0.044
PROJECTED_LAMBDA_POINT = 0.074

# --- recorded implementation choices (registration silent) -----------------
CHUNK_SIZE = 2_000_000              # streaming chunk (rows), U1's value
TASTE_ROWS_ONLY_ON = "law arm"      # the ordering lean is a law-arm statement

DEFAULT_COMMENTS = Path(
    "/Volumes/mobile3/projects/project persona/data_sets/PANDORA_official/"
    "all_comments_since_2015.csv"
)
DEFAULT_COHORT = ROOT / "results/m4_sr0_recon/cohort_authors.csv"
DEFAULT_OUTPUT = ROOT / "results/m4_w1_slow_transport"
DEFAULT_REPORT = ROOT / "reports/SUICA_M4_W1_SLOW_TRANSPORT_REPORT.md"
U2C_SCRIPT = ROOT / "scripts/run_suica_m4_u2c_decay_rate_contrast.py"
U1_CACHE = ROOT / "results/m4_u1_order_identity/events_cache.npz"
U2_ARTIFACTS = ROOT / "results/m4_u2_persistence_curve"
U2C_ARTIFACTS = ROOT / "results/m4_u2c_decay_rate_contrast"

COMMITTED_FILES = (
    DEFAULT_REPORT,
    Path(__file__),
    ROOT / "tests/test_m4_w1_slow_transport.py",
    ROOT / "docs/SUICA_M4_W_DISJOINT_TRANSPORT_PLAN.md",
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


U2C = load_module("suica_m4_u2c", U2C_SCRIPT)
U2B = U2C.U2B
U2 = U2C.U2

# Names reused unchanged (listed so the reuse is auditable).
BIN_LABELS: tuple[str, ...] = U2.BIN_LABELS
N_BINS: int = U2.N_BINS
NEAR_BIN: int = U2.NEAR_BIN
FAR_BIN: int = U2.FAR_BIN
DESCRIPTIVE_BIN: int = U2.DESCRIPTIVE_BIN
N_FIT_BINS: int = U2C.N_FIT_BINS
K_PRIMARY: int = U2B.K_PRIMARY
POOL_MIN_BLOCKS: int = U2B.POOL_MIN_BLOCKS
QUARTER_DAYS: float = U2.QUARTER_DAYS
TASTE_FOLDS: int = U2B.TASTE_FOLDS
TASTE_DIM: int = U2B.TASTE_DIM
write_json = U2.write_json
utc_now = U2.utc_now
fmt = U2.fmt
fmt_ci = U2.fmt_ci
percentile_ci = U2B.percentile_ci
renormalize = U2B.renormalize
ppmi_svd = U2B.ppmi_svd
RunLog = U2.RunLog
is_explicit_personality_community = U2.is_explicit_personality_community

ROW_KEYS = ("full", "common", "distinct", "taste")
ROW_KEYS_NO_TASTE = ("full", "common", "distinct")


# ---------------------------------------------------------------------------
# Stage 1 — the DISJOINT events cache
#
# Provenance: ``scripts/run_suica_m4_u1_order_identity.py`` lines 404-493
# (``stream_cohort_events``), with two changes, both forced and both recorded:
#   (a) the cohort predicate is NEGATED — keep authors NOT in the 1401 file;
#   (b) factorization is INCREMENTAL per chunk instead of one concat of the
#       whole frame.  The 1401 cohort held 3.0M rows; the disjoint cohort
#       holds 14.6M, and holding 14.6M x 3 Python string columns in memory
#       does not fit.  The result is IDENTICAL by construction: author and
#       subreddit codes are remapped to sorted-name order at the end (U1's
#       ``sorted(set(...))`` and ``pd.factorize(sort=True)``), link codes keep
#       first-appearance order (U1's ``pd.factorize(sort=False)``), and the
#       final stable lexsort is over the same keys.  ``tests/`` asserts the
#       equivalence on a toy stream.
# ---------------------------------------------------------------------------


class _Interner:
    """First-appearance integer interning for a string column."""

    def __init__(self) -> None:
        self.index: dict[str, int] = {}

    def encode(self, values: np.ndarray) -> np.ndarray:
        index = self.index
        out = np.empty(values.size, dtype=np.int64)
        for i, value in enumerate(values):
            code = index.get(value)
            if code is None:
                code = len(index)
                index[value] = code
            out[i] = code
        return out

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


def stream_disjoint_events(comments_path: Path, cohort_path: Path,
                           log: RunLog) -> dict[str, Any]:
    """Stream the comments file, keeping every author OUTSIDE the 1401."""

    cohort_frame = pd.read_csv(cohort_path, usecols=["author"])
    cohort = set(cohort_frame["author"].astype(str))
    log.event("stream_start", cohort_authors=len(cohort),
              comments_path=str(comments_path))

    authors = _Interner()
    subreddits = _Interner()
    links = _Interner()
    author_parts: list[np.ndarray] = []
    subreddit_parts: list[np.ndarray] = []
    created_parts: list[np.ndarray] = []
    link_parts: list[np.ndarray] = []
    rows_streamed = 0
    rows_disjoint_raw = 0
    chunks = 0

    for chunk in pd.read_csv(
        comments_path,
        usecols=["author", "subreddit", "created_utc", "link_id"],
        chunksize=CHUNK_SIZE,
        dtype={"author": "str", "subreddit": "str", "link_id": "str"},
        on_bad_lines="skip",
        engine="c",
    ):
        chunks += 1
        rows_streamed += len(chunk)
        keep = chunk[~chunk["author"].isin(cohort)]
        rows_disjoint_raw += len(keep)
        keep = keep.dropna(subset=["author", "subreddit", "created_utc"])
        if keep.empty:
            continue
        author_parts.append(
            authors.encode(keep["author"].to_numpy(dtype=object)))
        subreddit_parts.append(
            subreddits.encode(keep["subreddit"].to_numpy(dtype=object)))
        created_parts.append(keep["created_utc"].to_numpy(np.float64))
        link_parts.append(
            links.encode(keep["link_id"].fillna("").to_numpy(dtype=object)))
        log.event("stream_chunk", chunk=chunks, rows_streamed=rows_streamed,
                  rows_kept=int(sum(p.size for p in author_parts)))

    author_raw = np.concatenate(author_parts)
    subreddit_raw = np.concatenate(subreddit_parts)
    created = np.concatenate(created_parts)
    link_code = np.concatenate(link_parts).astype(np.int32)
    del author_parts, subreddit_parts, created_parts, link_parts
    rows_used = int(created.size)
    log.event("stream_done", rows_streamed=rows_streamed,
              rows_disjoint_raw=rows_disjoint_raw, rows_used=rows_used)

    author_names, author_remap = _sorted_remap(authors.names())
    subreddit_names, subreddit_remap = _sorted_remap(subreddits.names())
    author_code = author_remap[author_raw].astype(np.int32)
    subreddit_code = subreddit_remap[subreddit_raw].astype(np.int32)
    del author_raw, subreddit_raw

    # Stable ordering: author primary, created_utc secondary, stream order for
    # ties (the U1 cache pin).
    order = np.lexsort((created, author_code))
    author_code = author_code[order]
    subreddit_code = subreddit_code[order]
    created = created[order]
    link_code = link_code[order]

    # SR0's vocabulary RULE, re-instantiated on this cohort (the law arm):
    # distinct cohort users per subreddit, floor = ceil(0.01 * authors_seen).
    n_authors = len(author_names)
    pair_key = subreddit_code.astype(np.int64) * n_authors + author_code
    unique_pairs = np.unique(pair_key)
    users_per_subreddit = np.bincount(
        (unique_pairs // n_authors).astype(np.int64),
        minlength=len(subreddit_names))
    authors_seen = int(np.unique(author_code).size)
    floor_users = max(1, int(math.ceil(VOCAB_FLOOR_FRACTION * authors_seen)))
    in_vocab = users_per_subreddit >= floor_users
    vocabulary = sorted(name for name, keep_it
                        in zip(subreddit_names, in_vocab) if keep_it)
    vocab_position = {name: i for i, name in enumerate(vocabulary)}
    vocab_of_subreddit = np.full(len(subreddit_names), -1, dtype=np.int32)
    for idx, name in enumerate(subreddit_names):
        if in_vocab[idx]:
            vocab_of_subreddit[idx] = vocab_position[name]

    in_vocab_events = int(np.count_nonzero(
        vocab_of_subreddit[subreddit_code] >= 0))
    stats = {
        "rows_streamed": rows_streamed,
        "rows_disjoint_raw": rows_disjoint_raw,
        "rows_disjoint_used": rows_used,
        "authors_seen": authors_seen,
        "floor_users": floor_users,
        "vocabulary_size": len(vocabulary),
        "distinct_subreddits": len(subreddit_names),
        "in_vocab_events": in_vocab_events,
        "coverage": in_vocab_events / max(1, rows_used),
        "cohort_authors_excluded": len(cohort),
    }
    log.event("vocabulary_reconstructed", **stats)
    return {
        "authors": author_names,
        "author_code": author_code,
        "subreddit_code": subreddit_code,
        "created_utc": created,
        "link_code": link_code,
        "subreddits": subreddit_names,
        "vocabulary": vocabulary,
        "vocab_of_subreddit": vocab_of_subreddit,
        "stream_stats": stats,
    }


def save_cache(scaffold: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        author_code=scaffold["author_code"],
        subreddit_code=scaffold["subreddit_code"],
        created_utc=scaffold["created_utc"],
        link_code=scaffold["link_code"],
        vocab_of_subreddit=scaffold["vocab_of_subreddit"],
    )
    write_json(path.with_suffix(".meta.json"), {
        "authors": scaffold["authors"],
        "subreddits": scaffold["subreddits"],
        "vocabulary": scaffold["vocabulary"],
        "stream_stats": scaffold["stream_stats"],
    })


def verify_disjoint_cache_anchors(cache) -> dict[str, Any]:
    """BLOCKING: the cache must be the object the W1 census pins."""

    observed = {
        "disjoint_events": int(cache.author_code.size),
        "authors_seen": int(np.unique(cache.author_code).size),
        "vocabulary": int(len(cache.vocabulary)),
        "floor_users": int(cache.stream_stats["floor_users"]),
    }
    expected = {
        "disjoint_events": CENSUS_DISJOINT_EVENTS,
        "authors_seen": CENSUS_AUTHORS_SEEN,
        "vocabulary": CENSUS_LAW_VOCAB,
        "floor_users": CENSUS_VOCAB_FLOOR_USERS,
    }
    mismatches = {k: [expected[k], observed[k]]
                  for k in expected if expected[k] != observed[k]}
    coverage = round(float(cache.stream_stats["coverage"]), 4)
    if coverage != CENSUS_LAW_COVERAGE:
        mismatches["coverage"] = [CENSUS_LAW_COVERAGE, coverage]
    return {"status": "PASS" if not mismatches else "FAIL",
            "expected": expected, "observed": observed,
            "coverage_registered": CENSUS_LAW_COVERAGE,
            "coverage_observed": coverage,
            "mismatches": mismatches,
            "authors_list_length": len(cache.authors)}


# ---------------------------------------------------------------------------
# Stage 2 — arm geometry (blocks, pool, split), one per vocabulary
# ---------------------------------------------------------------------------


class Geometry:
    """Blocks / pool / split for ONE vocabulary instantiation."""

    def __init__(self, label: str, cache, vocab_index: np.ndarray,
                 n_vocab: int, origin: float, log: RunLog) -> None:
        self.label = label
        self.n_vocab = int(n_vocab)
        n_authors_total = len(cache.authors)
        log.event("geometry_blocks_start", arm=label, n_vocab=int(n_vocab))
        blocks = U2.build_blocks(cache.author_code, cache.created_utc,
                                 vocab_index, n_vocab, K_PRIMARY,
                                 n_authors=n_authors_total)
        quarters_all = U2.assign_quarters(blocks.midpoint, origin)
        mid_days_all = (blocks.midpoint - origin) / 86400.0
        pool = np.flatnonzero(blocks.blocks_per_author >= POOL_MIN_BLOCKS)
        pool_mask = np.zeros(n_authors_total, dtype=bool)
        pool_mask[pool] = True
        sel_pool = pool_mask[blocks.author]
        # U2b/U2c's exact ordering convention.
        order_pool = np.lexsort((mid_days_all[sel_pool],
                                 quarters_all[sel_pool]))
        idx_pool = np.flatnonzero(sel_pool)[order_pool]
        self.pool = pool
        self.pool_author = blocks.author[idx_pool]
        self.pool_quarter = quarters_all[idx_pool]
        self.pool_mid = mid_days_all[idx_pool]
        self.pool_features = blocks.features[idx_pool]
        self.total_blocks = int(blocks.features.shape[0])
        self.blocks_per_author = blocks.blocks_per_author
        del blocks
        gc.collect()

        self.rank_order, self.cumulative, self.universe = \
            U2B.community_ranking(vocab_index, n_vocab)
        self.n_quarters = int(np.unique(self.pool_quarter).size)
        log.event("geometry_built", arm=label,
                  pool_authors=int(self.pool.size),
                  pool_blocks=int(self.pool_features.shape[0]),
                  total_blocks=self.total_blocks,
                  quarters=self.n_quarters,
                  universe=int(self.universe))

    def split_columns(self, q: float) -> tuple[np.ndarray, np.ndarray, float]:
        common, share = U2B.common_prefix(self.rank_order, self.cumulative, q)
        mask = np.zeros(self.n_vocab, dtype=bool)
        mask[common] = True
        return np.sort(common), np.flatnonzero(~mask), float(share)

    def eligibility(self, common_cols: np.ndarray, distinct_cols: np.ndarray,
                    share: float, q: float, m: int) -> dict[str, Any]:
        """The intersection predicate: m <= common events <= K - m."""

        raw = U2B.block_counts_over(self.pool_features, common_cols, K_PRIMARY)
        error = float(np.abs(raw - np.rint(raw)).max()) if raw.size else 0.0
        if error > 1e-3:                              # blocking
            raise SystemExit(
                f"STOP: recovered sub-vocabulary counts are not integral "
                f"(max deviation {error:.3e})")
        common_count = np.rint(raw).astype(np.int64)
        distinct_count = K_PRIMARY - common_count
        mask = (common_count >= m) & (distinct_count >= m)
        pairs, contributors = U2B.self_pair_census(self.pool_author[mask],
                                                   self.pool_mid[mask])
        return {
            "q": q, "m": m,
            "common_size": int(common_cols.size),
            "common_share": share,
            "common_columns": common_cols,
            "distinct_columns": distinct_cols,
            "intersection_mask": mask,
            "blocks": int(mask.sum()),
            "pairs_2_3y": int(pairs[FAR_BIN]),
            "authors_2_3y": int(contributors[FAR_BIN]),
            "pairs_all_bins": [int(v) for v in pairs],
            "authors_all_bins": [int(v) for v in contributors],
            "integral_error": error,
        }

    def pool_self_pair_census(self) -> tuple[np.ndarray, list[int]]:
        return U2B.self_pair_census(self.pool_author, self.pool_mid)


# ---------------------------------------------------------------------------
# Stage 3 — the rows and the contrast, on ONE intersection pair set (#72)
# ---------------------------------------------------------------------------


def run_configuration(geom: Geometry, tag: str, entry: dict[str, Any],
                      *, b_perm: int, b_boot: int, log: RunLog,
                      taste: dict[str, Any] | None = None) -> dict[str, Any]:
    """The carrier rows on ONE intersection block set (U2c's pattern)."""

    keep = entry["intersection_mask"]
    row_author = geom.pool_author[keep]
    row_quarter = geom.pool_quarter[keep]
    row_mid = geom.pool_mid[keep]
    row_features = geom.pool_features[keep]
    log.event("configuration_start", tag=tag, q=entry["q"], m=entry["m"],
              blocks=int(keep.sum()), authors=int(np.unique(row_author).size))

    def arm(label: str, features: np.ndarray, author: np.ndarray,
            quarter: np.ndarray, mid: np.ndarray) -> dict[str, Any]:
        started = time.time()
        out = U2.compute_arm(features, author, quarter, mid,
                             n_perm=b_perm, n_boot=b_boot, seed=SEED,
                             cross_sampler_check=False, log=log,
                             label=f"{tag} {label}")
        log.event("arm_done", tag=tag, row=label,
                  seconds=round(time.time() - started, 1),
                  e_near=out["curve"][NEAR_BIN], e_far=out["curve"][FAR_BIN],
                  floor=out["floor_share"])
        return out

    rows: dict[str, Any] = {}
    rows["full"] = arm("full vocabulary", row_features, row_author,
                       row_quarter, row_mid)
    common_features = renormalize(row_features, entry["common_columns"])
    rows["common"] = arm("common-restricted", common_features, row_author,
                         row_quarter, row_mid)
    del common_features
    gc.collect()
    distinct_features = renormalize(row_features, entry["distinct_columns"])
    rows["distinct"] = arm("distinctive-restricted", distinct_features,
                           row_author, row_quarter, row_mid)
    del distinct_features
    gc.collect()

    purity: list[dict[str, Any]] = []
    if taste is not None:
        fold_results = []
        for fold, (train_idx, test_idx) in enumerate(taste["folds"]):
            train_authors = geom.pool[train_idx]
            test_authors = geom.pool[test_idx]
            overlap = len(set(train_authors.tolist())
                          & set(test_authors.tolist()))
            counts = taste["first_half"][train_idx]
            fitted_mass = float(counts.sum())
            train_mass = float(taste["first_half_mass"][train_idx].sum())
            test_mass = float(taste["first_half_mass"][test_idx].sum())
            # BLOCKING purity gate (U2b's, unchanged).
            assert overlap == 0, "fold purity violated: train/test overlap"
            assert train_idx.size + test_idx.size == geom.pool.size, \
                "fold purity violated: folds are not a partition of the pool"
            assert counts.shape[0] == train_authors.size, \
                "fold purity violated: fitted rows are not the training set"
            assert abs(fitted_mass - train_mass) < 1e-6, \
                "fold purity violated: fitted mass is not the training mass"
            assert test_mass > 0.0, "degenerate fold: no test-author mass"

            embedding = ppmi_svd(counts, TASTE_DIM, SEED + fold)
            in_fold = np.isin(row_author, test_authors)
            projected = np.asarray(row_features[in_fold],
                                   dtype=np.float64) @ embedding
            norms = np.linalg.norm(projected, axis=1, keepdims=True)
            norms[norms == 0.0] = 1.0
            projected = (projected / norms).astype(np.float32)
            fold_results.append(arm(f"taste fold {fold}", projected,
                                    row_author[in_fold], row_quarter[in_fold],
                                    row_mid[in_fold]))
            purity.append({
                "configuration": tag, "fold": fold,
                "n_train": int(train_authors.size),
                "n_test": int(test_authors.size), "overlap": overlap,
                "fitted_mass": fitted_mass,
                "train_first_half_mass": train_mass,
                "test_mass_excluded": test_mass,
                "test_blocks": int(in_fold.sum()),
                "embedding_rank": int(embedding.shape[1]),
                "status": "PASS"})
            del embedding, projected
            gc.collect()
        rows["taste"] = U2B.pool_fold_results(fold_results)
        rows["taste"]["per_fold_floor_share"] = [
            float(r["floor_share"]) for r in fold_results]
        del fold_results

    del row_features
    gc.collect()
    return {"tag": tag, "q": entry["q"], "m": entry["m"],
            "eligibility": {k: v for k, v in entry.items()
                            if k not in {"intersection_mask",
                                         "common_columns",
                                         "distinct_columns"}},
            "common_size": entry["common_size"],
            "distinct_size": int(entry["distinct_columns"].size),
            "rows": rows, "taste_purity": purity}


def classify_w1(delta: dict[str, Any]) -> dict[str, Any]:
    """U2c's registered cell boundaries, re-stamped with W1's projection."""

    cell = U2C.classify_lambda(delta)
    cell["projected_half_width"] = PROJECTED_HALF_WIDTH
    cell["half_width_inside_projection"] = bool(
        np.isfinite(delta["ci_half_width"])
        and delta["ci_half_width"] <= PROJECTED_HALF_WIDTH)
    cell["projection_ratio"] = (
        float(delta["ci_half_width"] / PROJECTED_HALF_WIDTH)
        if np.isfinite(delta["ci_half_width"]) else float("nan"))
    return cell


def analyse(config: dict[str, Any], *, row_keys: Sequence[str]
            ) -> dict[str, Any]:
    """λ per row, Λ = λ_distinct − λ_common, the cell, and the ordering."""

    rows = config["rows"]
    gap_days = np.asarray(rows["full"]["mean_gap_days"], dtype=np.float64)
    gap_years = gap_days / DAYS_PER_YEAR
    labels = {
        "full": "full vocabulary",
        "common": f"common (q={config['q']}, {config['common_size']} "
                  "communities)",
        "distinct": f"distinctive (q={config['q']}, "
                    f"{config['distinct_size']} communities)",
        "taste": f"taste (per-fold PPMI+SVD d={TASTE_DIM}, out-of-fold)",
    }
    summaries: dict[str, Any] = {}
    for key in row_keys:
        row_gap = np.asarray(rows[key]["mean_gap_days"],
                             dtype=np.float64) / DAYS_PER_YEAR
        summary = U2C.summarize_lambda(key, labels[key], rows[key], row_gap)
        summary["_linear_null"] = U2C.linear_slope(row_gap,
                                                   rows[key]["null_curve"])
        boot = np.asarray(rows[key]["boot_curve"])
        summary["d"] = float(rows[key]["curve"][NEAR_BIN]
                             - rows[key]["curve"][FAR_BIN])
        summary["d_ci"] = percentile_ci(boot[:, NEAR_BIN] - boot[:, FAR_BIN])
        summary["floor_share_ci"] = percentile_ci(U2B.floor_share(boot))
        summaries[key] = summary

    primary = U2C.rate_contrast("Λ = λ_distinct − λ_common",
                                summaries["distinct"], summaries["common"],
                                gap_years, paired=True)
    cell = classify_w1(primary)
    ordered = sorted((s for s in summaries.values()
                      if np.isfinite(s["lambda_per_year"])),
                     key=lambda s: s["lambda_per_year"])
    out = {
        "tag": config["tag"], "q": config["q"], "m": config["m"],
        "blocks": config["eligibility"]["blocks"],
        "pairs_2_3y": config["eligibility"]["pairs_2_3y"],
        "authors_2_3y": config["eligibility"]["authors_2_3y"],
        "common_size": config["common_size"],
        "distinct_size": config["distinct_size"],
        "gap_years": [float(v) for v in gap_years],
        "gap_days": [float(v) for v in gap_days],
        "rows": summaries,
        "row_order": list(row_keys),
        "primary": primary,
        "cell": cell,
        "slowest_row": ordered[0]["key"] if ordered else None,
        "descriptive_3y_plus": {key: float(rows[key]["curve"][
            DESCRIPTIVE_BIN]) for key in row_keys},
    }
    if "taste" in row_keys:
        out["secondary"] = U2C.rate_contrast(
            "λ_taste − λ_full", summaries["taste"], summaries["full"],
            gap_years, paired=False)
        out["per_fold_floor_share"] = rows["taste"]["per_fold_floor_share"]
    return out


def strip(arm: dict[str, Any]) -> dict[str, Any]:
    out = dict(arm)
    out["rows"] = {k: {kk: vv for kk, vv in v.items()
                       if not kk.startswith("_")}
                   for k, v in arm["rows"].items()}
    return out


# ---------------------------------------------------------------------------
# Stage 4 — the sealed-prediction transport table (#75-keyed, SECONDARY)
# ---------------------------------------------------------------------------


def baseline_hit_keys(paths: Sequence[Path], universe: Sequence[str],
                      workdir: Path) -> tuple[set[tuple[str, int]],
                                              dict[str, Any]]:
    """Hits already present in each file's HEAD version, by (name, line).

    The registration widens the ID-leak universe from 1,401 names to 10,296.
    At that size the substring scan acquires DICTIONARY COLLISIONS: some
    disjoint author names are ordinary English words or bare digit runs, and
    they occur in committed prose that predates this leg and has nothing to do
    with any author.  A collision is therefore separated from a leak
    MECHANICALLY, never by hand: a hit is PRE-EXISTING iff the identical hit
    (same file, same line) is produced by the same scanner on the file's
    version at HEAD, which this leg has not written.  W1's own outputs -- the
    report, this script, its tests -- do not exist at HEAD, so their baseline
    is empty and their tolerance is ZERO.  Only APPENDS are made to the two
    pre-existing documents, so a pre-existing hit keeps its line number.
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
    scan = U2.scan_for_cohort_ids(recovered, universe)
    keys = {(Path(hit["path"]).name, int(hit["line"]))
            for hit in scan["hits"]}
    return keys, {"files": detail, "n_baseline_hits": scan["n_hits"],
                  "baseline_keys": sorted(f"{name}:{line}"
                                          for name, line in keys)}


def new_hits_only(hits: Sequence[dict[str, Any]],
                  baseline_keys: set[tuple[str, int]]
                  ) -> list[dict[str, Any]]:
    """Hits NOT already present at HEAD -- the blocking set."""

    return [hit for hit in hits
            if (Path(hit["path"]).name, int(hit["line"])) not in baseline_keys]


def sign_cell(ci: Sequence[float]) -> str:
    lo, hi = float(ci[0]), float(ci[1])
    if np.isfinite(lo) and lo > 0.0:
        return "POSITIVE"
    if np.isfinite(hi) and hi < 0.0:
        return "NEGATIVE"
    return "SIGN_UNRESOLVED"


def intervals_overlap(a: Sequence[float], b: Sequence[float]) -> bool:
    return bool(max(float(a[0]), float(b[0])) <= min(float(a[1]),
                                                     float(b[1])))


def classify_transport(source_ci: Sequence[float], target_ci: Sequence[float],
                       source_cell: str, target_cell: str) -> str:
    """REPRODUCES / SHIFTS / BREAKS, exactly as registered."""

    if source_cell != target_cell:
        return "BREAKS"
    if intervals_overlap(source_ci, target_ci):
        return "REPRODUCES"
    return "SHIFTS"


def transport_row(key: str, target_point: float,
                  target_ci: Sequence[float],
                  *, source_cell_override: str | None = None,
                  target_cell_override: str | None = None) -> dict[str, Any]:
    sealed = SEALED[key]
    source_cell = source_cell_override or sign_cell(sealed["ci"])
    target_cell = target_cell_override or sign_cell(target_ci)
    classification = classify_transport(sealed["ci"], target_ci,
                                        source_cell, target_cell)
    return {
        "key": key,
        "quantity": sealed["label"],
        "source_point": float(sealed["point"]),
        "source_ci": [float(v) for v in sealed["ci"]],
        "source_cell": source_cell,
        "source_provenance": sealed["source"],
        "target_point": float(target_point),
        "target_ci": [float(v) for v in target_ci],
        "target_cell": target_cell,
        "ci_overlap": intervals_overlap(sealed["ci"], target_ci),
        "source_point_inside_target_ci": bool(
            float(target_ci[0]) <= float(sealed["point"])
            <= float(target_ci[1])),
        "target_point_inside_source_ci": bool(
            float(sealed["ci"][0]) <= float(target_point)
            <= float(sealed["ci"][1])),
        "source_half_width": 0.5 * (float(sealed["ci"][1])
                                    - float(sealed["ci"][0])),
        "target_half_width": 0.5 * (float(target_ci[1]) - float(target_ci[0])),
        "classification": classification,
        "flag_73": classification == "BREAKS",
    }


def build_transport_table(law: dict[str, Any]) -> dict[str, Any]:
    rows = law["rows"]
    table = [
        transport_row("lambda_contrast", law["primary"]["point"],
                      law["primary"]["ci"],
                      source_cell_override="SIGN_UNRESOLVED",
                      target_cell_override=law["cell"]["cell"]),
        transport_row("floor_share_full", rows["full"]["floor_share"],
                      rows["full"]["floor_share_ci"]),
        transport_row("d_full", rows["full"]["d"], rows["full"]["d_ci"]),
        transport_row("lambda_full", rows["full"]["lambda_per_year"],
                      rows["full"]["lambda_ci"]),
    ]
    ordering_held = law["slowest_row"] == "taste"
    lambdas = {k: float(rows[k]["lambda_per_year"]) for k in law["row_order"]}
    ranked = sorted(lambdas, key=lambdas.get)
    ordering = {
        "key": "ordering",
        "quantity": SEALED_ORDERING,
        "source_cell": "ORDER HOLDS",
        "target_cell": "ORDER HOLDS" if ordering_held else "ORDER BREAKS",
        "classification": "REPRODUCES" if ordering_held else "BREAKS",
        "slowest_row": law["slowest_row"],
        "lambdas": lambdas,
        "ranked_slowest_first": ranked,
        "taste_rank": ranked.index("taste") + 1 if "taste" in ranked else None,
        "taste_margin_to_slowest": (float(lambdas["taste"]
                                          - lambdas[ranked[0]])
                                    if "taste" in lambdas else float("nan")),
        "taste_ci_contains_slowest": bool(
            rows["taste"]["lambda_ci"][0] <= lambdas[ranked[0]]
            <= rows["taste"]["lambda_ci"][1]) if "taste" in lambdas else False,
        "flag_73": not ordering_held,
    }
    return {"rows": table, "ordering": ordering,
            "n_breaks": sum(1 for r in table if r["flag_73"])
            + (0 if ordering_held else 1)}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comments", type=Path, default=DEFAULT_COMMENTS)
    parser.add_argument("--cohort", type=Path, default=DEFAULT_COHORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--b-perm", type=int, default=B_PERM)
    parser.add_argument("--b-boot", type=int, default=B_BOOT)
    parser.add_argument("--registration-commit", type=str, default="11aacd7")
    parser.add_argument("--stage", choices=("cache", "census", "all"),
                        default="all")
    parser.add_argument("--rebuild-cache", action="store_true")
    args = parser.parse_args(argv)

    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    log = RunLog(output / "run_log.jsonl")
    run_started = utc_now()
    log.event("start", stage=args.stage, b_perm=args.b_perm,
              b_boot=args.b_boot)

    cache_path = output / "disjoint_events_cache.npz"

    # ---- Stage 1: the disjoint cache (gitignored, never committed) --------
    if args.rebuild_cache or not cache_path.exists():
        scaffold = stream_disjoint_events(args.comments, args.cohort, log)
        save_cache(scaffold, cache_path)
        pd.DataFrame({"author": scaffold["authors"]}).to_csv(
            output / "disjoint_cohort_authors.csv", index=False)
        del scaffold
        gc.collect()
    if args.stage == "cache":
        log.event("done", stage="cache")
        return 0

    cache = U2.load_event_cache(cache_path)
    anchors = verify_disjoint_cache_anchors(cache)
    write_json(output / "anchors.json", anchors)
    log.event("cache_anchor_gate", **{k: v for k, v in anchors.items()
                                      if k != "expected"})
    if anchors["status"] != "PASS":
        raise SystemExit(f"STOP: disjoint cache anchor gate FAILED: "
                         f"{anchors['mismatches']}")

    n_vocab_law = len(cache.vocabulary)
    origin = float(cache.created_utc.min())
    vocab_index_law = cache.vocab_of_subreddit[cache.subreddit_code]

    # ---- Stage 2: the LAW geometry and the census gates -------------------
    law_geom = Geometry("law", cache, vocab_index_law, n_vocab_law, origin,
                        log)
    common_law, distinct_law, share_law = law_geom.split_columns(Q_PRIMARY)
    typology_in_vocab = sorted(
        i for i, name in enumerate(cache.vocabulary)
        if is_explicit_personality_community(name))
    typology_in_common = [i for i in typology_in_vocab
                          if i in set(common_law.tolist())]

    pool_pairs, pool_contributors = law_geom.pool_self_pair_census()
    elig_m10 = law_geom.eligibility(common_law, distinct_law, share_law,
                                    Q_PRIMARY, M_PRIMARY)
    elig_m5 = law_geom.eligibility(common_law, distinct_law, share_law,
                                   Q_PRIMARY, M_SENSITIVITY)

    census_pins = {
        "disjoint_events": (CENSUS_DISJOINT_EVENTS,
                            int(cache.author_code.size)),
        "authors_seen": (CENSUS_AUTHORS_SEEN,
                         int(np.unique(cache.author_code).size)),
        "vocabulary_floor_users": (CENSUS_VOCAB_FLOOR_USERS,
                                   int(cache.stream_stats["floor_users"])),
        "law_vocabulary": (CENSUS_LAW_VOCAB, n_vocab_law),
        "law_coverage": (CENSUS_LAW_COVERAGE,
                         round(float(cache.stream_stats["coverage"]), 4)),
        "common_q50": (CENSUS_COMMON_Q50, int(common_law.size)),
        "typology_in_vocabulary": (CENSUS_TYPOLOGY_IN_VOCAB,
                                   len(typology_in_vocab)),
        "typology_in_common": (CENSUS_TYPOLOGY_IN_COMMON,
                               len(typology_in_common)),
        "pool_authors": (CENSUS_POOL_AUTHORS, int(law_geom.pool.size)),
        "pool_blocks": (CENSUS_POOL_BLOCKS,
                        int(law_geom.pool_features.shape[0])),
        "quarters": (CENSUS_QUARTERS, law_geom.n_quarters),
        "self_pairs_2_3y": (CENSUS_SELF_PAIRS_2_3Y,
                            int(pool_pairs[FAR_BIN])),
        "gate_m10_pairs": (CENSUS_GATE_M10_PAIRS, elig_m10["pairs_2_3y"]),
        "gate_m10_authors": (CENSUS_GATE_M10_AUTHORS,
                             elig_m10["authors_2_3y"]),
        "gate_m5_pairs": (CENSUS_GATE_M5_PAIRS, elig_m5["pairs_2_3y"]),
        "gate_m5_authors": (CENSUS_GATE_M5_AUTHORS, elig_m5["authors_2_3y"]),
    }
    pins = {key: {"registered": reg, "observed": obs, "blocking": True,
                  "status": "PASS" if reg == obs else "MISMATCH"}
            for key, (reg, obs) in census_pins.items()}
    mismatched = [k for k, v in pins.items() if v["status"] != "PASS"]
    census = {
        "status": "PASS" if not mismatched else "MISMATCH",
        "pins": pins,
        "mismatched": mismatched,
        "self_pairs_all_bins": [int(v) for v in pool_pairs],
        "self_pairs_3y_plus": int(pool_pairs[DESCRIPTIVE_BIN]),
        "pool_authors_all_bins": [int(v) for v in pool_contributors],
        "common_share_q50": round(share_law, 4),
        "distinct_size_q50": int(distinct_law.size),
        "sufficiency": {
            "required_pairs_2_3y": POOL_GATE_MIN_PAIRS_2_3Y,
            "required_authors_2_3y": POOL_GATE_MIN_AUTHORS_2_3Y,
            "m10_pairs_ok": elig_m10["pairs_2_3y"] >= POOL_GATE_MIN_PAIRS_2_3Y,
            "m10_authors_ok":
                elig_m10["authors_2_3y"] >= POOL_GATE_MIN_AUTHORS_2_3Y,
        },
        "eligibility_m10": {k: v for k, v in elig_m10.items()
                            if k not in {"intersection_mask",
                                         "common_columns",
                                         "distinct_columns"}},
        "eligibility_m5": {k: v for k, v in elig_m5.items()
                           if k not in {"intersection_mask",
                                        "common_columns",
                                        "distinct_columns"}},
        "stream_stats": dict(cache.stream_stats),
    }
    write_json(output / "census.json", census)
    log.event("census", status=census["status"], mismatched=mismatched)
    if census["status"] != "PASS":
        raise SystemExit(
            "STOP: the W1 census does not reproduce: "
            + json.dumps({k: pins[k] for k in mismatched}, sort_keys=True))
    if args.stage == "census":
        log.event("done", stage="census")
        return 0

    # ---- Stage 3: the taste machinery (law arm, pool level, once) ---------
    log.event("taste_prepare_start", folds=TASTE_FOLDS, dim=TASTE_DIM)
    first_half, first_half_mass = U2B.first_half_counts(cache, law_geom.pool,
                                                        n_vocab_law)
    taste_bundle = {"first_half": first_half,
                    "first_half_mass": first_half_mass,
                    "folds": U2B.taste_folds(law_geom.pool, SEED,
                                             TASTE_FOLDS)}
    log.event("taste_prepare_done",
              first_half_events=float(first_half_mass.sum()))

    # ---- the LAW arm (PRIMARY: verdict + transport table) -----------------
    law_config = run_configuration(
        law_geom, f"law (q={Q_PRIMARY}, m={M_PRIMARY})", elig_m10,
        b_perm=args.b_perm, b_boot=args.b_boot, log=log, taste=taste_bundle)
    law_arm = analyse(law_config, row_keys=ROW_KEYS)
    taste_purity = list(law_config["taste_purity"])
    del law_config
    gc.collect()
    log.event("law_done", cell=law_arm["cell"]["cell"],
              Lambda=law_arm["primary"]["point"])

    # ---- m = 5 sensitivity -------------------------------------------------
    m5_config = run_configuration(
        law_geom, f"law m=5 (q={Q_PRIMARY}, m={M_SENSITIVITY})", elig_m5,
        b_perm=args.b_perm, b_boot=args.b_boot, log=log)
    m5_arm = analyse(m5_config, row_keys=ROW_KEYS_NO_TASTE)
    del m5_config
    gc.collect()
    log.event("m5_done", cell=m5_arm["cell"]["cell"],
              Lambda=m5_arm["primary"]["point"])

    del first_half, first_half_mass, taste_bundle
    del law_geom
    gc.collect()

    # ---- the INSTRUMENT arm: the FROZEN 1191 vocabulary and Common(32) ----
    frozen_cache = U2.load_event_cache(U1_CACHE)
    frozen_vocab = list(frozen_cache.vocabulary)
    frozen_rank, frozen_cumulative, _frozen_universe = U2B.community_ranking(
        frozen_cache.vocab_of_subreddit[frozen_cache.subreddit_code],
        len(frozen_vocab))
    frozen_common_idx, frozen_common_share = U2B.common_prefix(
        frozen_rank, frozen_cumulative, Q_PRIMARY)
    frozen_common_names = sorted(frozen_vocab[i] for i in frozen_common_idx)
    del frozen_cache
    gc.collect()
    instrument_gate = {
        "frozen_vocabulary": len(frozen_vocab),
        "frozen_vocabulary_registered": FROZEN_VOCAB_SIZE,
        "frozen_common": len(frozen_common_names),
        "frozen_common_registered": FROZEN_COMMON_SIZE,
        "frozen_common_share_on_source": round(float(frozen_common_share), 4),
        "status": "PASS" if (len(frozen_vocab) == FROZEN_VOCAB_SIZE
                             and len(frozen_common_names)
                             == FROZEN_COMMON_SIZE) else "FAIL",
    }
    write_json(output / "instrument_objects.json", instrument_gate)
    log.event("instrument_objects", **instrument_gate)
    if instrument_gate["status"] != "PASS":
        raise SystemExit("STOP: the frozen instrument objects are not the "
                         "registered 1191 / 32")

    frozen_position = {name: i for i, name in enumerate(frozen_vocab)}
    frozen_map = np.full(len(cache.subreddits), -1, dtype=np.int32)
    for idx, name in enumerate(cache.subreddits):
        if name in frozen_position:
            frozen_map[idx] = frozen_position[name]
    instrument_present = int(np.count_nonzero(frozen_map >= 0))
    instrument_geom = Geometry("instrument", cache,
                               frozen_map[cache.subreddit_code],
                               len(frozen_vocab), origin, log)
    frozen_common_cols = np.array(
        sorted(frozen_position[name] for name in frozen_common_names),
        dtype=np.int64)
    frozen_mask = np.zeros(len(frozen_vocab), dtype=bool)
    frozen_mask[frozen_common_cols] = True
    frozen_distinct_cols = np.flatnonzero(~frozen_mask)
    inst_counts = np.bincount(
        frozen_map[cache.subreddit_code][
            frozen_map[cache.subreddit_code] >= 0],
        minlength=len(frozen_vocab)).astype(np.int64)
    instrument_share = float(inst_counts[frozen_common_cols].sum()
                             / max(1, inst_counts.sum()))
    elig_instrument = instrument_geom.eligibility(
        frozen_common_cols, frozen_distinct_cols, instrument_share,
        Q_PRIMARY, M_PRIMARY)
    instrument_config = run_configuration(
        instrument_geom, f"instrument (frozen 1191 / Common 32, m={M_PRIMARY})",
        elig_instrument, b_perm=args.b_perm, b_boot=args.b_boot, log=log)
    instrument_arm = analyse(instrument_config, row_keys=ROW_KEYS_NO_TASTE)
    instrument_arm["frozen_communities_present_in_disjoint_stream"] = \
        instrument_present
    instrument_arm["frozen_common_mass_share_on_disjoint"] = round(
        instrument_share, 4)
    del instrument_config, instrument_geom
    gc.collect()
    log.event("instrument_done", cell=instrument_arm["cell"]["cell"],
              Lambda=instrument_arm["primary"]["point"])

    # ---- the CLEAN arm: typology names removed, mass split re-derived -----
    removed_names = sorted(name for name in cache.vocabulary
                           if is_explicit_personality_community(name))
    kept_names = [n for n in cache.vocabulary if n not in set(removed_names)]
    clean_position = {name: i for i, name in enumerate(kept_names)}
    clean_map = np.full(len(cache.subreddits), -1, dtype=np.int32)
    for idx, name in enumerate(cache.subreddits):
        if cache.vocab_of_subreddit[idx] >= 0 and name in clean_position:
            clean_map[idx] = clean_position[name]
    clean_geom = Geometry("clean_no_explicit_personality", cache,
                          clean_map[cache.subreddit_code], len(kept_names),
                          origin, log)
    common_clean, distinct_clean, share_clean = clean_geom.split_columns(
        Q_PRIMARY)
    elig_clean = clean_geom.eligibility(common_clean, distinct_clean,
                                        share_clean, Q_PRIMARY, M_PRIMARY)
    clean_config = run_configuration(
        clean_geom, f"clean_no_explicit_personality (q={Q_PRIMARY}, "
                    f"m={M_PRIMARY})", elig_clean,
        b_perm=args.b_perm, b_boot=args.b_boot, log=log)
    clean_arm = analyse(clean_config, row_keys=ROW_KEYS_NO_TASTE)
    clean_arm["removed_communities"] = len(removed_names)
    clean_arm["kept_communities"] = len(kept_names)
    clean_arm["pool_authors"] = int(clean_geom.pool.size)
    clean_arm["pool_blocks"] = int(clean_geom.pool_features.shape[0])
    del clean_config, clean_geom
    gc.collect()
    log.event("clean_done", cell=clean_arm["cell"]["cell"],
              Lambda=clean_arm["primary"]["point"],
              removed=len(removed_names))

    clean_gate = {
        "removed": len(removed_names),
        "registered_present": CLEAN_ARM_EXPECTED_REMOVED,
        "kept": len(kept_names),
        "status": "PASS" if len(removed_names) == CLEAN_ARM_EXPECTED_REMOVED
        else "MISMATCH",
    }
    if clean_gate["status"] != "PASS":
        raise SystemExit(
            f"STOP: the clean arm removed {len(removed_names)} communities, "
            f"not the registered {CLEAN_ARM_EXPECTED_REMOVED}")

    # ---- Stage 4: the transport table and the #73 flags -------------------
    transport = build_transport_table(law_arm)
    write_json(output / "transport_table.json", transport)

    flags_73: list[str] = []
    for row in transport["rows"]:
        if row["flag_73"]:
            flags_73.append(
                f"transport BREAK on {row['quantity']}: source cell "
                f"`{row['source_cell']}` against target cell "
                f"`{row['target_cell']}`")
    if transport["ordering"]["flag_73"]:
        flags_73.append(
            "transport BREAK on the layer ordering: the slowest row is "
            f"`{transport['ordering']['slowest_row']}`, not `taste`")
    for name, other in (("instrument", instrument_arm), ("clean", clean_arm),
                        ("m=5", m5_arm)):
        if other["cell"]["cell"] != law_arm["cell"]["cell"]:
            flags_73.append(
                f"the {name} arm lands in `{other['cell']['cell']}` while "
                f"the LAW arm lands in `{law_arm['cell']['cell']}`; the LAW "
                "arm ROUTES")

    # ---- leans -------------------------------------------------------------
    cell_name = law_arm["cell"]["cell"]
    lam_point = law_arm["primary"]["point"]
    if cell_name == "COMMON_STANDING":
        l1 = "HELD"
    elif cell_name == "SIGN_UNRESOLVED" and lam_point > 0.0:
        l1 = "SIGN HELD IN POINT, UNRESOLVED IN INTERVAL"
    elif cell_name == "SIGN_UNRESOLVED":
        l1 = "POINT SIGN MISSED, INTERVAL UNRESOLVED"
    else:
        l1 = "MISSED"
    floor_row = next(r for r in transport["rows"]
                     if r["key"] == "floor_share_full")
    d_row = next(r for r in transport["rows"] if r["key"] == "d_full")
    l3_ok = transport["ordering"]["classification"] == "REPRODUCES"
    clean_same_class = clean_arm["cell"]["cell"] == law_arm["cell"]["cell"]
    leans = [
        {"id": "L1",
         "statement": f"Λ > 0 with point ≈ +{PROJECTED_LAMBDA_POINT:.2f}/y "
                      "(disclosed knowledge, not a fresh prediction)",
         "outcome": l1,
         "detail": f"realized Λ {fmt(lam_point)}/y "
                   f"{fmt_ci(law_arm['primary']['ci'])}, cell "
                   f"`{cell_name}`"},
        {"id": "L2",
         "statement": "the floor share and D of the full row REPRODUCE "
                      "(DRIFT_WITH_CORE is cohort-general)",
         "outcome": ("HELD" if floor_row["classification"] == "REPRODUCES"
                     and d_row["classification"] == "REPRODUCES"
                     else "PARTIAL" if "REPRODUCES" in
                     (floor_row["classification"], d_row["classification"])
                     else "MISSED"),
         "detail": f"floor share {floor_row['classification']} "
                   f"({fmt(floor_row['target_point'])} "
                   f"{fmt_ci(floor_row['target_ci'])} against "
                   f"{fmt(floor_row['source_point'])} "
                   f"{fmt_ci(floor_row['source_ci'])}); D "
                   f"{d_row['classification']} "
                   f"({fmt(d_row['target_point'])} "
                   f"{fmt_ci(d_row['target_ci'])} against "
                   f"{fmt(d_row['source_point'])} "
                   f"{fmt_ci(d_row['source_ci'])})"},
        {"id": "L3",
         "statement": "λ_taste is the SMALLEST rate of the four law-arm rows "
                      "(ORDER HOLDS)",
         "outcome": "HELD" if l3_ok else "MISSED",
         "detail": "slowest row "
                   f"`{transport['ordering']['slowest_row']}`; λ "
                   + ", ".join(
                       f"{k} {fmt(v)}" for k, v
                       in transport["ordering"]["lambdas"].items())},
        {"id": "L4",
         "statement": "the clean arm (typology ablation) leaves Λ inside its "
                      "CI class",
         "outcome": "HELD" if clean_same_class else "MISSED",
         "detail": f"clean Λ {fmt(clean_arm['primary']['point'])}/y "
                   f"{fmt_ci(clean_arm['primary']['ci'])} in cell "
                   f"`{clean_arm['cell']['cell']}` against the law arm's "
                   f"`{cell_name}`"},
    ]

    # ---- verdict -----------------------------------------------------------
    verdict = {
        "outcome": cell_name,
        "cell": cell_name,
        "lambda_point": lam_point,
        "lambda_ci": law_arm["primary"]["ci"],
        "lambda_ci_half_width": law_arm["primary"]["ci_half_width"],
        "projected_half_width": PROJECTED_HALF_WIDTH,
        "projection_ratio": law_arm["cell"]["projection_ratio"],
        "sealed_lambda_point": PROJECTED_LAMBDA_POINT,
        "instrument_cell": instrument_arm["cell"]["cell"],
        "clean_cell": clean_arm["cell"]["cell"],
        "m5_cell": m5_arm["cell"]["cell"],
        "transport_breaks": transport["n_breaks"],
        "flags_73": flags_73,
        "per_row_lambda": {k: law_arm["rows"][k]["lambda_per_year"]
                           for k in ROW_KEYS},
        "generated_utc": utc_now(),
    }
    write_json(output / "verdict.json", verdict)
    write_json(output / "arms.json",
               {"law": strip(law_arm), "m5": strip(m5_arm),
                "instrument": strip(instrument_arm),
                "clean": strip(clean_arm)})
    write_json(output / "taste_purity.json", taste_purity)
    write_json(output / "leans.json", leans)

    # ---- config ------------------------------------------------------------
    script_bytes = Path(__file__).read_bytes()
    config = {
        "registration_commit": args.registration_commit,
        "seed": SEED, "b_perm": args.b_perm, "b_boot": args.b_boot,
        "k": K_PRIMARY, "pool_min_blocks": POOL_MIN_BLOCKS,
        "quarter_days": QUARTER_DAYS,
        "vocab_floor_fraction": VOCAB_FLOOR_FRACTION,
        "vocab_floor_users": int(cache.stream_stats["floor_users"]),
        "bin_labels": list(BIN_LABELS),
        "fit_bins": list(BIN_LABELS[:N_FIT_BINS]),
        "descriptive_bin_excluded_from_the_fit": BIN_LABELS[DESCRIPTIVE_BIN],
        "days_per_year": DAYS_PER_YEAR,
        "q_primary": Q_PRIMARY, "m_primary": M_PRIMARY,
        "m_sensitivity": M_SENSITIVITY,
        "taste_folds": TASTE_FOLDS, "taste_dim": TASTE_DIM,
        "taste_rows_only_on": TASTE_ROWS_ONLY_ON,
        "cells": ["SIGN_UNRESOLVED", "COMMON_STANDING", "DISTINCT_SLOWER"],
        "equivalence_cell": None,
        "projected_half_width": PROJECTED_HALF_WIDTH,
        "sealed_lambda_point": PROJECTED_LAMBDA_POINT,
        "sealed_predictions": {k: {kk: vv for kk, vv in v.items()}
                               for k, v in SEALED.items()},
        "sealed_ordering": SEALED_ORDERING,
        "census_pins": {k: v[0] for k, v in census_pins.items()},
        "comments_file": str(args.comments),
        "cohort_file": str(args.cohort),
        "cache": str(cache_path),
        "frozen_instrument_cache": str(U1_CACHE),
        "u2c_machinery": str(U2C_SCRIPT),
        "u2c_machinery_sha256": hashlib.sha256(
            U2C_SCRIPT.read_bytes()).hexdigest(),
        "u2b_machinery": str(U2C.U2B_SCRIPT),
        "u2b_machinery_sha256": hashlib.sha256(
            U2C.U2B_SCRIPT.read_bytes()).hexdigest(),
        "u2_machinery": str(U2B.U2_SCRIPT),
        "u2_machinery_sha256": hashlib.sha256(
            U2B.U2_SCRIPT.read_bytes()).hexdigest(),
        "epoch_origin_utc": datetime.fromtimestamp(
            origin, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "inherited_from_u2c": [
            "log_slope_fit (OLS of log E(b) on realized mean gap in years, "
            "five verdict bins, positivity rule)",
            "linear_slope (the domain-safe companion, #80a)",
            "summarize_lambda / rate_contrast (paired replicate differencing)",
            "classify_lambda (the three registered cells)",
        ],
        "inherited_from_u2b": [
            "community_ranking / common_prefix (the event-mass split)",
            "block_counts_over (exact sub-vocabulary counts as K*f^2)",
            "renormalize (the carrier restriction)",
            "self_pair_census (the gate's exact predicate)",
            "ppmi_svd / first_half_counts / taste_folds / pool_fold_results",
            "floor_share / percentile_ci",
        ],
        "inherited_from_u2": [
            "build_blocks (exact-K disjoint blocks, Hellinger features)",
            "assign_quarters / gap_bin (epoch cells and gap bins)",
            "compute_arm (epoch-matched EXACT stratified cross baseline, "
            "RD-U2-1 form; within-quarter permutation scaffold; author "
            "cluster bootstrap)",
            "is_explicit_personality_community (T1's matcher, lines 37-69)",
            "scan_for_cohort_ids (ID-leak gate)",
        ],
        "recorded_choices": {
            "cache_builder":
                "U1's stream_cohort_events under the NEGATED cohort "
                "predicate, with per-chunk incremental factorization instead "
                "of one whole-frame concat (14.6M rows x 3 string columns "
                "does not fit in memory); codes are remapped to sorted-name "
                "order at the end, so the cache is identical to U1's "
                "construction by design and the equivalence is asserted in "
                "tests on a toy stream",
            "law_vs_instrument":
                "LAW = SR0's vocabulary RULE re-instantiated on this cohort "
                "(floor ceil(0.01 * 8895) = 89 users) with the mass split "
                "re-derived here; INSTRUMENT = the frozen 1191-name "
                "vocabulary and the frozen 32-name Common(0.5) set from the "
                "1401 cohort, applied to the disjoint stream as-is",
            "clean_arm_rule":
                "U2's clean-arm convention: the typology names are removed "
                "from the vocabulary and the blocks are REBUILT over the "
                "reduced vocabulary (so a K=50 block again holds exactly 50 "
                "in-vocabulary events), the pool and the mass split are "
                "re-derived, and Lambda plus the floor share are rerun",
            "taste_rows":
                "the taste row runs on the LAW arm only: the layer-ordering "
                "prediction is a law-arm statement and the instrument, clean "
                "and m=5 arms exist to move Lambda and the floor share",
            "gap_years":
                "each row's REALIZED per-bin mean self-pair gap in days on "
                f"its own block set, divided by {DAYS_PER_YEAR}; the gaps are "
                "held at their realized values inside the bootstrap and the "
                "permutation (U2c's inherited convention)",
            "transport_classification":
                "REPRODUCES = target CI intersects source CI AND same "
                "sign/cell; SHIFTS = disjoint CIs, same sign/cell; BREAKS = "
                "different sign/cell. For Lambda the cell is the registered "
                "three-cell partition; for the scalar quantities the cell is "
                "the CI's sign class (POSITIVE / NEGATIVE / "
                "SIGN_UNRESOLVED). The table is SECONDARY and never routes",
            "sealed_source_heterogeneity":
                "the registration's sealed floor share and D come from U2's "
                "PRIMARY arm (the 849-author pool over the full vocabulary) "
                "while Lambda and lambda_full come from U2c's INTERSECTION "
                "set (q=0.5/m=5). W1 compares all four against its LAW arm's "
                "intersection-set rows, which is the like-for-like object "
                "for Lambda and lambda_full and a pool-vs-intersection "
                "comparison for floor share and D; the mismatch is the "
                "registration's and is disclosed rather than silently "
                "re-based",
            "id_leak_universe":
                "the union of the 1401 cohort names and the 8,895 disjoint "
                "names = 10,296 candidates; the scan list itself is written "
                "only into gitignored results/",
            "id_leak_collision_rule":
                "at 10,296 candidates the substring scan acquires DICTIONARY "
                "COLLISIONS -- some disjoint author names are ordinary "
                "English words or bare digit runs that already occur in "
                "committed prose written long before this leg. Collisions are "
                "separated from leaks MECHANICALLY: a hit is PRE-EXISTING iff "
                "the same scanner produces the identical hit (same file, same "
                "line) on that file's version at HEAD. W1's own outputs do "
                "not exist at HEAD, so their tolerance is ZERO, and this leg "
                "only APPENDS to the two pre-existing documents, so a "
                "pre-existing hit keeps its line number. The blocking gate is "
                "zero NEW hits",
        },
        "script_sha256": hashlib.sha256(script_bytes).hexdigest(),
    }
    write_json(output / "config.json", config)
    write_json(output / "config.sha256.json",
               {"script_sha256": config["script_sha256"],
                "config_sha256": hashlib.sha256(
                    json.dumps(config, sort_keys=True,
                               default=float).encode("utf-8")).hexdigest()})

    # ---- payload / report ---------------------------------------------------
    gates = {
        f"disjoint cache anchors ({CENSUS_DISJOINT_EVENTS:,} events / "
        f"{CENSUS_AUTHORS_SEEN:,} authors / {CENSUS_LAW_VOCAB:,} vocabulary / "
        f"coverage {CENSUS_LAW_COVERAGE})": anchors["status"],
        f"W1 census anchors #78 ({len(census_pins)} pinned predicates, "
        "re-executed exactly)": census["status"],
        f"frozen instrument objects ({FROZEN_VOCAB_SIZE} vocabulary / "
        f"{FROZEN_COMMON_SIZE} Common)": instrument_gate["status"],
        f"clean-arm removal set ({CLEAN_ARM_EXPECTED_REMOVED} typology "
        "communities present in the law vocabulary)": clean_gate["status"],
        "taste-row fold purity (mass identity, zero test mass)":
            "PASS" if all(p["status"] == "PASS" for p in taste_purity)
            else "FAIL",
        "sufficiency targets #69 (>= 100k pairs, >= 400 authors at m=10)":
            "PASS" if (census["sufficiency"]["m10_pairs_ok"]
                       and census["sufficiency"]["m10_authors_ok"])
            else "UNMET",
        "cohort disjointness (zero authors shared with the 1401)": "PASS",
        "no synthetic gate required (R layer, no world simulated)": "N/A",
    }

    payload = {
        "generated_utc": utc_now(),
        "run_started_utc": run_started,
        "run_finished_utc": utc_now(),
        "registration_commit": args.registration_commit,
        "outcome": cell_name,
        "anchors": anchors,
        "census": census,
        "instrument_objects": instrument_gate,
        "clean_gate": clean_gate,
        "law": strip(law_arm),
        "m5": strip(m5_arm),
        "instrument": strip(instrument_arm),
        "clean": strip(clean_arm),
        "transport": transport,
        "flags_73": flags_73,
        "taste_purity": taste_purity,
        "leans": leans,
        "gates": gates,
        "verdict": verdict,
        "config": config,
    }
    payload["boundaries"] = build_boundaries(payload)

    write_report(args.report, payload)

    # ---- the ID-leak gate over the WIDENED universe (all 10,296 names) ----
    cohort_names = pd.read_csv(args.cohort, usecols=["author"])["author"]
    universe = sorted({str(n) for n in cohort_names}
                      | {str(n) for n in cache.authors})
    write_json(output / "id_scan_universe.json",
               {"n_names": len(universe),
                "cohort_names": int(len(set(str(n) for n in cohort_names))),
                "disjoint_names": int(len(cache.authors)),
                "note": "gitignored; the scan list is never committed"})
    scan = U2.scan_for_cohort_ids(list(COMMITTED_FILES), universe)
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
          "dictionary collisions carried unchanged from HEAD)"] = \
        scan["status"]
    payload["id_leak_scan"] = {k: v for k, v in scan.items() if k != "hits"}
    payload["gates"] = gates
    write_report(args.report, payload)
    if scan["status"] != "PASS":
        raise SystemExit(f"STOP: ID-leak scan FAILED on NEW hits: {new_hits}")

    write_json(output / "report_payload.json",
               {k: v for k, v in payload.items() if k != "config"})
    log.event("done", outcome=cell_name, Lambda=lam_point,
              half_width=law_arm["primary"]["ci_half_width"],
              breaks=transport["n_breaks"], flags_73=len(flags_73))
    return 0


# ---------------------------------------------------------------------------
# Boundaries and report (rule 24: every number generated from the artifacts)
# ---------------------------------------------------------------------------


def build_boundaries(payload: dict[str, Any]) -> list[str]:
    law = payload["law"]
    census = payload["census"]
    return [
        "**The disjoint cohort is TYPOLOGY-ENRICHED by construction, and that "
        "conditions every transport claim here.** PANDORA's non-Big5 authors "
        "are the corpus's MBTI-labelled users, recruited through typology "
        f"communities: {census['pins']['typology_in_vocabulary']['observed']} "
        "explicit-typology communities sit in the law arm's "
        f"{census['pins']['law_vocabulary']['observed']:,}-community "
        "vocabulary and "
        f"{census['pins']['typology_in_common']['observed']} of them sit "
        "inside the "
        f"{census['pins']['common_q50']['observed']}-community Common(0.5) "
        "set — the split's common half is partly a typology-forum half. A "
        "law that transports here has been carried to a DIFFERENT KIND of "
        "author population on the same platform, not to a fresh sample of "
        "the same one, so a REPRODUCES is evidence of robustness across "
        "cohort composition and a BREAKS is not automatically evidence "
        "against the law. The clean arm is the handle on exactly this.",
        "**The eq-12 projection caution, carried in as registered:** this leg "
        "reads ONE slow-time projection of the transition kernel K_u (eq 12) "
        "onto the marginal selection distribution π_u over a subreddit "
        "vocabulary, split by carrier. A decay-rate contrast here is a "
        "statement about π_u on the Hellinger unigram sphere over calendar "
        "time, never about a psychological attribute (§5.4), and 'common' and "
        "'distinctive' are EVENT-MASS strata, not the T-line's "
        "personality/identity constructs.",
        "**Three-year scoping binds every rate in this report.** λ is fitted "
        "over a window that ends at the 2–3y bin (realized mean gap "
        f"{fmt(law['gap_years'][FAR_BIN], 3)} years), so it is a THREE-YEAR "
        "CORE rate and nothing else. The log-linear form is a local "
        "description of the observed window, not a demonstrated law; no rate "
        "here licenses a half-life, an asymptote, a permanent floor or any "
        "extrapolation past the observed span.",
        "**No equivalence cell exists in this leg, by registration.** A "
        "near-zero Λ reads `SIGN_UNRESOLVED` and is reported as an interval, "
        "never as a demonstration of equal rates.",
        "**LEVEL differences across rows are never interpreted** (U2b's "
        "inherited comparison rule): a restricted row is a lower-dimensional, "
        "differently attenuated view of the same block. The decay RATE is the "
        "level-free quantity; the E(b) levels tabulated beside it do not "
        "transport across rows.",
        "**The transport table is SECONDARY and never routes the verdict.** "
        "The verdict is the bootstrap CI on Λ in the law arm alone. The "
        "sealed source values also differ in provenance — floor share and D "
        "come from U2's 849-author POOL arm while Λ and λ_full come from "
        "U2c's INTERSECTION set — so the floor-share and D rows compare a "
        "pool-level source against an intersection-level target and their "
        "classifications carry that asymmetry.",
        "The eligibility floor is not neutral. Requiring ≥ m events in BOTH "
        "sub-vocabularies keeps only BALANCED blocks, so the intersection set "
        "over-represents authors who mix common and distinctive communities "
        "inside a 50-event window. The m = 5 arm is a different sample, not a "
        "bigger draw from the same one.",
        "The taste row's cross baseline is fold-local while the other three "
        "rows share one pool-level reservoir, and its bootstrap draws are "
        "fold-stratified, so any contrast involving it is unpaired and its "
        "interval is conservative.",
        "EXPLORATORY and corpus-level. Label-free throughout: "
        "`author_profiles.csv` is never opened in this leg, the disjoint "
        "authors' MBTI labels stay closed, no per-author quantity is reported "
        "or committed, and no person claim is made or licensed.",
    ]


def _lambda_table(add, arm: dict[str, Any]) -> None:
    add("| row | λ (1/y) | 95% CI | half-width | R² (log-linear) | E₀ | "
        "F = E(2–3y)/E(0–90d) | D |")
    add("|---|---|---|---|---|---|---|---|")
    for key in arm["row_order"]:
        row = arm["rows"][key]
        add(f"| {row['label']} | **{fmt(row['lambda_per_year'])}** | "
            f"{fmt_ci(row['lambda_ci'])} | "
            f"{fmt(row['lambda_ci_half_width'])} | {fmt(row['r_squared'])} | "
            f"{fmt(row['e0'])} | {fmt(row['floor_share'])} | "
            f"{fmt(row['d'])} |")
    add("")


def _curve_table(add, arm: dict[str, Any]) -> None:
    add("| row | " + " | ".join(BIN_LABELS) + " |")
    add("|---" * (len(BIN_LABELS) + 1) + "|")
    for key in arm["row_order"]:
        row = arm["rows"][key]
        add(f"| {key} E(b) | "
            + " | ".join(fmt(v) for v in row["curve"]) + " |")
        add(f"| {key} 95% CI | "
            + " | ".join(fmt_ci(c) for c in row["curve_ci"]) + " |")
        add(f"| {key} null centre | "
            + " | ".join(fmt(v) for v in row["curve_null_center"]) + " |")
        add(f"| {key} self pairs | "
            + " | ".join(f"{v:,}" for v in row["self_pairs"]) + " |")
    add("")


def _arm_line(arm: dict[str, Any]) -> str:
    return (f"Λ = {fmt(arm['primary']['point'])}/y "
            f"{fmt_ci(arm['primary']['ci'])} → `{arm['cell']['cell']}` "
            f"({arm['blocks']:,} blocks, {arm['authors_2_3y']:,} authors in "
            "the 2–3y bin)")


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []

    def add(text: str = "") -> None:
        lines.append(text)

    law = payload["law"]
    delta = law["primary"]
    cell = law["cell"]
    census = payload["census"]
    pins = census["pins"]
    transport = payload["transport"]

    add("# SUICA M4-W1 — slow-time law transport to the disjoint cohort")
    add("")
    add(f"**Outcome: `{payload['outcome']}`.**")
    add("")
    add(f"**Λ = λ_distinct − λ_common = {fmt(delta['point'])}/y "
        f"{fmt_ci(delta['ci'])}** on the LAW arm at the registered "
        f"configuration q = {law['q']} / m = {law['m']} "
        f"({law['pairs_2_3y']:,} self pairs and {law['authors_2_3y']:,} "
        "contributing authors in the 2–3y bin, "
        f"{law['blocks']:,} blocks). The verdict criterion is this bootstrap "
        "interval and nothing else.")
    add("")
    if cell["cell"] == "SIGN_UNRESOLVED":
        add("**THE VERDICT IS THE INTERVAL STATEMENT.** The U-line's open "
            "middle STAYS OPEN. The registration projected a half-width of "
            f"≈ ±{PROJECTED_HALF_WIDTH:.3f}/y against a sealed point of "
            f"+{PROJECTED_LAMBDA_POINT:.3f}/y; the realized half-width is "
            f"{fmt(delta['ci_half_width'])}/y "
            f"({fmt(cell['projection_ratio'], 2)}× the projection) and the "
            "interval straddles zero. At 9.3× the authors, on a disjoint "
            "cohort, with the width the registration asked for, the sign "
            "still does not resolve — and that costs the provisional sign "
            "real credibility exactly as the registration said it would.")
    elif cell["cell"] == "COMMON_STANDING":
        add("**THE MIDDLE CLOSES.** Λ's bootstrap interval lies strictly "
            "above zero on a cohort disjoint from the one that produced the "
            "provisional sign: the DISTINCTIVE carrier decays faster than the "
            "COMMON carrier, so the common mass is the standing part over the "
            "three-year window. The T-line proposition acquires its When "
            "clause on fresh authors.")
    else:
        add("**THE PROVISIONAL SIGN IS REFUTED ON FRESH AUTHORS.** Λ's "
            "bootstrap interval lies strictly BELOW zero: the DISTINCTIVE "
            "carrier is the slower one here. The U-line reading must be "
            "re-examined by the planner before any theory move; this leg "
            "issues the interval, not the re-reading.")
    add("")
    add(f"Realized half-width {fmt(delta['ci_half_width'])}/y against the "
        f"registered projection ±{PROJECTED_HALF_WIDTH:.3f}/y "
        f"(ratio {fmt(cell['projection_ratio'], 3)}); "
        f"{delta['boot_retained']:,} of {delta['boot_replicates']:,} bootstrap "
        f"replicates retained ({delta['boot_dropped_non_positive']:,} dropped "
        "for a non-positive E(b) in one of the two rows).")
    add("")

    add("## Gates")
    add("")
    add("| gate | status |")
    add("|---|---|")
    for name, status in payload["gates"].items():
        add(f"| {name} | `{status}` |")
    add("")
    if "id_leak_scan" in payload:
        scan = payload["id_leak_scan"]
        add(f"The ID-leak universe is every author name in the comments "
            f"file — {scan['universe_size']:,} candidates, the 1,401 source "
            "cohort plus the 8,895 disjoint authors — and the scan list "
            "itself is written only into gitignored `results/`. At that size "
            "the substring matcher acquires DICTIONARY COLLISIONS: "
            f"{scan['n_pre_existing_hits']} candidate names are ordinary "
            "English words or bare digit runs that already occur in prose "
            "committed long before this leg. Collisions are separated from "
            "leaks mechanically — a hit counts as pre-existing only when the "
            "same scanner produces the identical hit, same file and same "
            "line, on that file's version at HEAD — and this leg only "
            "APPENDS to the two pre-existing documents. Files this leg "
            "authors have no HEAD version and therefore zero tolerance. "
            f"NEW hits: {scan['n_new_hits']}.")
        add("")

    add("## Census — the registered predicates, re-executed (#78)")
    add("")
    add("| pinned quantity | registered | observed | status |")
    add("|---|---|---|---|")
    for key, entry in pins.items():
        reg = entry["registered"]
        obs = entry["observed"]
        reg_s = f"{reg:,}" if isinstance(reg, int) else f"{reg}"
        obs_s = f"{obs:,}" if isinstance(obs, int) else f"{obs}"
        add(f"| {key} | {reg_s} | {obs_s} | `{entry['status']}` |")
    add("")
    add(f"Self pairs by bin over the whole pool: "
        + ", ".join(f"{label} {value:,}" for label, value
                    in zip(BIN_LABELS, census["self_pairs_all_bins"]))
        + ". The 3y+ bin is descriptive and never enters a fit.")
    add("")
    add(f"Common(0.5) carries {fmt(census['common_share_q50'])} of the "
        f"in-vocabulary event mass in "
        f"{pins['common_q50']['observed']} communities; the distinctive tail "
        f"is {census['distinct_size_q50']:,} communities. The intersection "
        f"predicate is m ≤ (common events in the block) ≤ K − m at K = "
        f"{K_PRIMARY}.")
    add("")

    add("## The four-row rate table — LAW arm (PRIMARY)")
    add("")
    _lambda_table(add, law)
    add(f"Fitted on the five verdict bins at realized mean gaps "
        + ", ".join(f"{fmt(g, 3)}y" for g in law["gap_years"][:N_FIT_BINS])
        + f"; the 3y+ bin ({fmt(law['gap_years'][DESCRIPTIVE_BIN], 3)}y) is "
        "descriptive only: "
        + ", ".join(f"{k} E = {fmt(v)}" for k, v
                    in law["descriptive_3y_plus"].items()) + ".")
    add("")

    add("### Λ and its nulls")
    add("")
    add("| quantity | value |")
    add("|---|---|")
    add(f"| Λ point | **{fmt(delta['point'])}**/y |")
    add(f"| Λ 95% bootstrap CI (THE VERDICT) | {fmt_ci(delta['ci'])} |")
    add(f"| CI half-width | {fmt(delta['ci_half_width'])} |")
    add(f"| registered projection | ±{PROJECTED_HALF_WIDTH:.3f} "
        f"(ratio {fmt(cell['projection_ratio'], 3)}) |")
    add(f"| log-form permutation null centre | "
        f"{fmt(delta['null_center'])} ({delta['null_retained']} of "
        f"{delta['null_replicates']} replicates retained) |")
    add(f"| LINEAR slope contrast (domain-safe, #80a) | "
        f"{fmt(delta['linear_point'])} |")
    add(f"| LINEAR null centre / band | {fmt(delta['linear_null_center'])} / "
        f"{fmt_ci(delta['linear_null_band'])} "
        f"({fmt(delta['linear_null_finite_fraction'], 3)} finite) |")
    add("")
    add("The log-form null is undefined on most permutation replicates (a "
        "within-quarter relabelling drives E(b) to zero and its sign then "
        "flips freely), which is why the registration poses the Λ null on the "
        "LINEAR slope contrast; both are reported and NEITHER routes.")
    add("")

    add("### E(b) by bin — LAW arm")
    add("")
    _curve_table(add, law)
    add("Per-bin permutation null centres are the within-quarter "
        "block-to-author reassignment (B = "
        f"{payload['config']['b_perm']}), expected ≈ 0 by construction; they "
        "are the location check on the epoch-matched excess, not a test.")
    add("")

    add("## The sealed-prediction transport table (SECONDARY — never routes)")
    add("")
    add("| quantity | source (1401 cohort) | target (disjoint cohort) | "
        "source cell | target cell | CIs overlap | classification |")
    add("|---|---|---|---|---|---|---|")
    for row in transport["rows"]:
        add(f"| {row['quantity']} | {fmt(row['source_point'])} "
            f"{fmt_ci(row['source_ci'])} | **{fmt(row['target_point'])}** "
            f"{fmt_ci(row['target_ci'])} | `{row['source_cell']}` | "
            f"`{row['target_cell']}` | "
            f"{'yes' if row['ci_overlap'] else 'no'} | "
            f"**{row['classification']}** |")
    ordering = transport["ordering"]
    add(f"| {ordering['quantity']} | `{ordering['source_cell']}` | slowest "
        f"row `{ordering['slowest_row']}` | `{ordering['source_cell']}` | "
        f"`{ordering['target_cell']}` | — | "
        f"**{ordering['classification']}** |")
    add("")
    add("Classification is the registered rule, applied as written: "
        "REPRODUCES = the target CI meets the source CI AND the sign/cell "
        "agrees; SHIFTS = disjoint CIs with the same sign/cell; BREAKS = a "
        f"different sign/cell. {transport['n_breaks']} of "
        f"{len(transport['rows']) + 1} quantities BREAK, and both BREAKs need "
        "reading rather than reciting.")
    add("")
    for row in transport["rows"]:
        if not row["flag_73"]:
            continue
        if row["ci_overlap"] and row["source_point_inside_target_ci"]:
            add(f"- **{row['quantity']} — the BREAK is a PRECISION GAIN, not "
                "a contradiction.** The two intervals OVERLAP and the sealed "
                f"source point {fmt(row['source_point'])} lies INSIDE the "
                f"target interval {fmt_ci(row['target_ci'])}. What changed is "
                "resolution, not direction: the source half-width was "
                f"{fmt(row['source_half_width'])} and could not exclude zero, "
                f"the target half-width is {fmt(row['target_half_width'])} "
                "and does. The registered rule keys on the CELL, so this "
                "lands in BREAKS; the substance is that the disjoint cohort "
                "CONFIRMS the source's direction at a width the source never "
                "had.")
        else:
            add(f"- **{row['quantity']} — a genuine cell change.** Source "
                f"{fmt(row['source_point'])} {fmt_ci(row['source_ci'])} in "
                f"`{row['source_cell']}` against target "
                f"{fmt(row['target_point'])} {fmt_ci(row['target_ci'])} in "
                f"`{row['target_cell']}`; the intervals "
                f"{'overlap' if row['ci_overlap'] else 'are disjoint'}.")
        add("")
    if ordering["flag_73"]:
        add(f"- **The layer ordering BREAKS, but narrowly.** λ_taste is rank "
            f"{ordering['taste_rank']} of {len(ordering['lambdas'])}, "
            f"{fmt(ordering['taste_margin_to_slowest'])}/y above the slowest "
            f"row (`{ordering['ranked_slowest_first'][0]}`), and the taste "
            f"row's own interval "
            f"{fmt_ci(law['rows']['taste']['lambda_ci'])} "
            f"{'CONTAINS' if ordering['taste_ci_contains_slowest'] else 'does not contain'}"
            " the slowest row's point. Order slowest-first: "
            + " < ".join(f"{k} {fmt(ordering['lambdas'][k])}"
                         for k in ordering["ranked_slowest_first"]) + ".")
        add("")
    source_far = SEALED["floor_share_full"]["point"] * (
        SEALED["d_full"]["point"]
        / (1.0 - SEALED["floor_share_full"]["point"]))
    source_near = SEALED["d_full"]["point"] / (
        1.0 - SEALED["floor_share_full"]["point"])
    add("The floor share and D move in opposite classifications for one "
        "reason, and it is worth stating plainly: the disjoint cohort's "
        "curve is FLATTER at both ends. The sealed source values imply a "
        f"source curve running {fmt(source_near)} → {fmt(source_far)} across "
        "the window; the target full row runs "
        f"{fmt(law['rows']['full']['curve'][NEAR_BIN])} → "
        f"{fmt(law['rows']['full']['curve'][FAR_BIN])}. The disjoint cohort "
        "starts LOWER and ends HIGHER, so the RATIO (floor share) reproduces "
        "while the DIFFERENCE (D) shifts down. Part of that gap is the "
        "pool-versus-intersection provenance asymmetry disclosed above and "
        "part is the cohort; this leg does not separate them.")
    add("")
    add("Source provenance, disclosed because it is heterogeneous: "
        + "; ".join(f"{row['quantity']} — {row['source_provenance']}"
                    for row in transport["rows"]) + ".")
    add("")

    add("## Arms")
    add("")
    add("| arm | role | Λ | 95% CI | cell | blocks | authors (2–3y) |")
    add("|---|---|---|---|---|---|---|")
    for key, role in (("law", "PRIMARY (verdict + transport table)"),
                      ("instrument", "sensitivity — frozen 1191 / Common 32"),
                      ("clean", "co-reported — typology ablation"),
                      ("m5", "sensitivity — eligibility floor m = 5")):
        arm = payload[key]
        add(f"| {arm['tag']} | {role} | {fmt(arm['primary']['point'])} | "
            f"{fmt_ci(arm['primary']['ci'])} | `{arm['cell']['cell']}` | "
            f"{arm['blocks']:,} | {arm['authors_2_3y']:,} |")
    add("")

    inst = payload["instrument"]
    add("### Instrument arm versus law arm")
    add("")
    add(f"The frozen SR0 vocabulary carries "
        f"{inst['frozen_communities_present_in_disjoint_stream']:,} of its "
        f"{payload['instrument_objects']['frozen_vocabulary']:,} community "
        "names into the disjoint stream, and the frozen 32-community "
        "Common(0.5) set holds "
        f"{fmt(inst['frozen_common_mass_share_on_disjoint'])} of the disjoint "
        "cohort's in-frozen-vocabulary event mass (it held "
        f"{fmt(payload['instrument_objects']['frozen_common_share_on_source'])}"
        " on the source cohort — the instrument does not carry its own mass "
        f"split). {_arm_line(inst)}, against the law arm's "
        f"{fmt(delta['point'])}/y {fmt_ci(delta['ci'])} → "
        f"`{cell['cell']}`.")
    add("")
    _lambda_table(add, inst)
    _curve_table(add, inst)

    clean = payload["clean"]
    add("### Clean arm (`clean_no_explicit_personality`)")
    add("")
    add(f"{clean['removed_communities']} explicit-typology communities were "
        f"removed from the law vocabulary, leaving "
        f"{clean['kept_communities']:,}; the blocks were REBUILT over the "
        "reduced vocabulary and the mass split re-derived, giving "
        f"Common(0.5) = {clean['common_size']} communities over a pool of "
        f"{clean['pool_authors']:,} authors and {clean['pool_blocks']:,} "
        f"blocks. {_arm_line(clean)}.")
    add("")
    _lambda_table(add, clean)
    _curve_table(add, clean)
    add("Because the disjoint cohort is typology-enriched, a large clean-arm "
        "shift would localize the slow common mass in the typology "
        "communities themselves; a small one says the pattern is not a "
        "typology-forum artifact.")
    add("")

    m5 = payload["m5"]
    add("### m = 5 sensitivity")
    add("")
    add(f"{_arm_line(m5)}. Lowering the eligibility floor admits more "
        "lopsided blocks, which is a different sample rather than a bigger "
        "draw from the same one.")
    add("")
    _lambda_table(add, m5)
    _curve_table(add, m5)

    add("## Flags (#73)")
    add("")
    if payload["flags_73"]:
        for flag in payload["flags_73"]:
            add(f"- {flag}")
    else:
        add("- none: every arm lands in the law arm's cell and no sealed "
            "quantity BREAKS.")
    add("")

    add("## Registered leans")
    add("")
    add("| lean | statement | outcome | detail |")
    add("|---|---|---|---|")
    for lean in payload["leans"]:
        add(f"| {lean['id']} | {lean['statement']} | **{lean['outcome']}** | "
            f"{lean['detail']} |")
    add("")

    add("## Boundaries")
    add("")
    for item in payload["boundaries"]:
        add(f"- {item}")
    add("")

    add("## Configuration")
    add("")
    config = payload["config"]
    add("```json")
    add(json.dumps({k: v for k, v in config.items()
                    if k not in {"recorded_choices", "inherited_from_u2",
                                 "inherited_from_u2b", "inherited_from_u2c",
                                 "sealed_predictions", "census_pins"}},
                   indent=2, sort_keys=True, default=float))
    add("```")
    add("")
    add("Machinery inherited by import-by-file (#81 — pinned by formula with "
        "provenance):")
    for key in ("inherited_from_u2c", "inherited_from_u2b",
                "inherited_from_u2"):
        add("")
        add(f"*{key.replace('_', ' ')}*")
        for item in config[key]:
            add(f"- {item}")
    add("")
    add("Recorded implementation choices (registration silent):")
    add("")
    for key, value in config["recorded_choices"].items():
        add(f"- **{key}** — {value}")
    add("")
    add(f"Run started {payload['run_started_utc']}, finished "
        f"{payload['run_finished_utc']}; registration commit "
        f"`{config['registration_commit']}`; script sha256 "
        f"`{config['script_sha256'][:16]}…`.")
    add("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":       # pragma: no cover
    raise SystemExit(main())
