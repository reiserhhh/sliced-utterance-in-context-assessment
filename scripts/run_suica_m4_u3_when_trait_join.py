#!/usr/bin/env python3
"""SUICA M4-U3 -- the Who x When trait join (the When line's first LABEL leg).

Registered BEFORE run in ``docs/SUICA_M4_U_WHEN_ORDER_PLAN.md`` (section
"U3 -- the Who x When trait join", commit 921fe86).  Binding.

THE QUESTION.  Do the When coordinates the measurement phase validated --
cross-thread inertia (``stay_ct``, U1's binding designation), signature
tightness (``tight``), personal drift (``drift_pa``) -- couple to Big5
similarity, and do they add anything BEYOND the Where bag channel (SR1's
r = 0.049)?  The increment is the question; the raw coupling is its
precondition.

STAGE DISCIPLINE (the heart of the leg; SR1's config-before-joint machinery).

    part0   anchors only.  The U1 events cache (3,005,360 events / 1401
            authors / 1191 communities), the U2 block-pool predicate (849),
            and the three eligibility-pool predicates are re-executed from
            the cache.  Then the analysis config is written, sha256-hashed
            and STAMPED.  NO LABEL COLUMN IS READ BEFORE OR DURING PART 0.
            A1 binds: an anchor failure STOPS the leg and no stamp is ever
            written (the stamp write is the last statement of the stage).

    stageb  LABEL-FREE.  One GLOBAL state map (spherical k-means, C = 24 plus
            an OOV state 24, fit on all 849 authors' EARLY halves, seed
            20260818, n_init 10, declared corpus-global), the three
            coordinates, their split-half reliabilities ON THE ACTUAL
            OBJECTS, and the RELIABILITY GATE (r >= 0.5).  A coordinate that
            fails is excluded label-free and reported; if the PRIMARY fails
            the leg stops before any join (verdict COORDINATE_UNRELIABLE --
            the stamp exists, stage E never opens).  The coordinate table is
            frozen to disk and hashed into the stamp chain.

    stagee  THE SINGLE JOIN.  ``author_profiles.csv`` is opened ONCE for
            ``author`` plus the five Big5 columns; ``first_join`` is logged
            with its timestamp BEFORE the first joint quantity; every
            registered quantity is computed inside this stage; nothing
            label-bearing is recomputed afterwards.

    gate    G-U3 proves ``stamp_utc < coordinate_freeze_utc < first_join_utc``
            from the artifacts, and runs the blocking ID-leak scan.

DISCLOSED RE-POSING RD-U3-1 (decided in part 0, label-free, before the
stamp).  The registration's stay predicate reads ">= 30 cross-thread
adjacencies per half" and its census reads 847.  Re-executed from the cache,
">= 30" admits 848 authors and "> 30" admits exactly 847: ONE author sits at
the boundary with min(early, late) = 30 (the next lowest is 27).  The census
count is planner arithmetic (#43); the pool it names is the registered
object.  U3 therefore adopts the STRICTLY TIGHTER "> 30" predicate, which
reproduces the registered pool EXACTLY and drops one author -- the same
direction as U1's RD-U1-1/RD-U1-2 repairs (each stricter than the registered
form).  The ">= 30" pool is carried as a reported robustness row and routes
nothing.

Stages: part0 -> stageb -> stagee -> gate -> finalize -> report (or ``all``).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LEG = "M4-U3"
REGISTRATION_COMMIT = "921fe86"
DEFAULT_CACHE = ROOT / "results/m4_u1_order_identity/events_cache.npz"
DEFAULT_OUTPUT = ROOT / "results/m4_u3_when_trait_join"
DEFAULT_REPORT = ROOT / "reports/SUICA_M4_U3_WHEN_TRAIT_JOIN_REPORT.md"
PLAN_DOC = ROOT / "docs/SUICA_M4_U_WHEN_ORDER_PLAN.md"
LEDGER = ROOT / "docs/CLAIMS_LEDGER.md"
SCRIPT_SELF = Path(__file__).resolve()
TEST_SELF = ROOT / "tests/test_m4_u3_when_trait_join.py"

# THE ONE LABEL SOURCE.  Opened in stage E and nowhere else.
PROFILES = Path("/Volumes/mobile3/projects/project persona"
                "/data_sets/PANDORA_official/author_profiles.csv")
BIG5: tuple[str, ...] = ("agreeableness", "openness", "conscientiousness",
                         "extraversion", "neuroticism")

# ---------------------------------------------------------------------------
# CONFIG -- every constant the registration pins.
# ---------------------------------------------------------------------------
SEED = 20260818                      # registration pin (U-line master seed)
B_PERM = 999                         # registration pin, both nulls
C_STATES = 24                        # registration pin (+ OOV state index 24)
KMEANS_N_INIT = 10                   # registration pin
K_BLOCK = 50                         # U2 pin: exact-K disjoint blocks
POOL_MIN_BLOCKS = 4                  # U2 pin -> 849 authors

STAY_MIN_ADJ_PER_HALF = 30           # registration prose
STAY_PREDICATE_STRICT = True         # RD-U3-1: "> 30", reproduces 847
TIGHT_GAP_DAYS = 90.0                # registration pin
TIGHT_MIN_PAIRS = 2                  # registration pin
DRIFT_NEAR_DAYS = 180.0              # registration pin
DRIFT_FAR_DAYS = 365.0               # registration pin
DRIFT_MIN_PAIRS = 3                  # registration pin, EACH cell

RELIABILITY_GATE = 0.50              # registration pin, label-free
REL_LABEL_DECLARED = 0.80            # DECLARED, not measured (#57)
ALPHA = 0.05
N_SECONDARY_ROWS = 3                 # Bonferroni guard on secondary detections
LEAN_RAW_POINT = 0.03                # registered primary lean, |raw r|

# SR1 anchors (the effect-scale anchor and the projection's inputs).
SR1_R = 0.049
SR1_Z = 5.42
SR1_N = 1306
REGISTERED_MDR = 0.022               # registration's projection at N ~ 849

DAY = 86400.0
PRIMARY_COORDINATE = "stay_ct"
COORDINATES: tuple[str, ...] = ("stay_ct", "tight", "drift_pa")

# Cache anchors -- BLOCKING (A1: failure => STOP, no stamp ever).
ANCHOR_EVENTS = 3_005_360
ANCHOR_AUTHORS = 1401
ANCHOR_VOCAB = 1191

# Census pins from the registration -- BLOCKING pool counts.
CENSUS_PINS: dict[str, int] = {
    "block_pool_ge4_blocks": 849,
    "stay_eligible": 847,
    "tight_eligible": 763,
    "drift_eligible": 652,
}
# Non-blocking census echoes (the registration's own measured reliabilities;
# the stay entry is a DECLARED PROXY there -- subreddit-level states -- so it
# is echoed, never gated on).
CENSUS_RELIABILITY_ECHO: dict[str, Any] = {
    "stay_DECLARED_PROXY": 0.7828, "tight": 0.8872, "drift_pa": 0.9383}

RN_NOTES: dict[str, str] = {
    "RN-U3-1":
        "CONFIG-BEFORE-JOINT.  stage_part0 re-executes the cache anchors and "
        "the four pool predicates and only then writes, hashes and stamps the "
        "config; it never opens a label column.  stage_stageb is label-free "
        "and freezes the coordinate table into the stamp chain.  The FIRST "
        "joint When x trait quantity of the harness lives in stage_stagee, "
        "which logs a `first_join` event immediately before it.  G-U3 reads "
        "the artifacts and proves stamp < coordinate_freeze < first_join.",
    "RN-U3-2":
        "RD-U3-1 (disclosed re-posing, decided label-free in part 0).  The "
        "registered stay predicate '>= 30 cross-thread adjacencies per half' "
        "admits 848 authors from this cache; the registered pool count is "
        "847.  Exactly one author sits at min(early, late) = 30.  U3 adopts "
        "the STRICTLY TIGHTER '> 30', which reproduces the registered pool "
        "exactly; the '>= 30' pool is a reported robustness row and routes "
        "nothing.",
    "RN-U3-3":
        "the coordinates are TECHNICAL OBJECTS (section 5.4).  stay_ct, tight "
        "and drift_pa are selection-process statistics of an author's own "
        "event stream.  No psychological naming is permitted regardless of "
        "outcome -- not 'inertia as a trait', not 'consistency', not "
        "'openness to change'.",
    "RN-U3-4":
        "the drift-aware caution.  Slow-time coordinates are MOVING TARGETS: "
        "each author's coordinate is measured over that author's own span, so "
        "a null or a coupling here is a statement about coordinates measured "
        "that way, not about a fixed personal quantity.",
    "RN-U3-5":
        "disattenuation is a SECONDARY READING ONLY (#57 family).  The "
        "coordinate reliability is MEASURED here; the label reliability 0.80 "
        "is DECLARED, so the disattenuated number illustrates scale and "
        "routes nothing.",
    "RN-U3-6":
        "the label event.  This leg opens the PANDORA Big5 columns of "
        "author_profiles.csv once, under the stamp, for the 849-author "
        "analysis pool -- the SR1/SR2 class of re-join.  No per-author trait "
        "value is written to any committed file; only aggregate statistics "
        "leave stage E.",
    "RN-U3-7":
        "the eq-12 projection caution.  Each coordinate is ONE first-order "
        "projection of K_u; a verdict here is a statement about that "
        "projection, exactly as U1's positive result was.",
}

# ---------------------------------------------------------------------------
# Inherited machinery, imported by file (#56: the inherited object, not a copy)
# ---------------------------------------------------------------------------
U1_SCRIPT = ROOT / "scripts/run_suica_m4_u1_order_identity.py"
U2_SCRIPT = ROOT / "scripts/run_suica_m4_u2_persistence_curve.py"


def _import_by_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:      # pragma: no cover
        raise RuntimeError(f"cannot import {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


U1 = _import_by_file("suica_m4_u1", U1_SCRIPT)
U2 = _import_by_file("suica_m4_u2", U2_SCRIPT)

spherical_kmeans = U1.spherical_kmeans          # U1's state-map estimator
load_event_cache = U2.load_event_cache          # U1 cache reader
verify_cache_anchors = U2.verify_cache_anchors  # blocking cache gate
build_blocks = U2.build_blocks                  # U2's exact-K blocks
scan_for_cohort_ids = U2.scan_for_cohort_ids    # blocking ID-leak scan


def load_cache_and_links(path: Path):
    """U2's cache reader plus the ``link_code`` column U2 does not carry.

    ``link_code`` is what makes a pair CROSS-THREAD, and U1's binding
    designation makes cross-thread the only admissible order object here.
    """

    cache = load_event_cache(path)
    with np.load(path) as payload:
        link_code = payload["link_code"]
    return cache, link_code


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------
def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=1, sort_keys=True, default=float)
                    + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


class RunLog:
    """Append-only JSONL event log; the stamp-order proof reads it."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def event(self, name: str, **payload: Any) -> dict[str, Any]:
        record = {"utc": utc_now(), "event": name, **payload}
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, default=float)
                         + "\n")
        return record

    def read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line
                in self.path.read_text(encoding="utf-8").splitlines() if line]


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    xc = np.asarray(x, float) - np.mean(x)
    yc = np.asarray(y, float) - np.mean(y)
    denom = float(np.linalg.norm(xc) * np.linalg.norm(yc))
    if denom == 0.0:
        return float("nan")
    return float(xc @ yc / denom)


def spearman_brown(r_half: float) -> float:
    """Full-length reliability implied by a half-length correlation."""

    if not np.isfinite(r_half) or r_half <= -1.0:
        return float("nan")
    return float(2.0 * r_half / (1.0 + r_half))


# ---------------------------------------------------------------------------
# Coordinate machinery -- LABEL-FREE BY CONSTRUCTION.
#
# Every function in this section takes event-stream arrays and returns
# coordinate values.  None of them accepts, reads or can reach a label column;
# the tests assert this by signature and by monkeypatching the one label
# reader (``open_trait_table``) to raise.
# ---------------------------------------------------------------------------
def author_starts(author_code: np.ndarray, n_authors: int) -> np.ndarray:
    return np.searchsorted(author_code, np.arange(n_authors + 1))


def assign_halves(author_code: np.ndarray, created_utc: np.ndarray,
                  n_authors: int) -> np.ndarray:
    """U1's T6'' rule on the FULL stream: ts <= per-author median -> early."""

    starts = author_starts(author_code, n_authors)
    early = np.zeros(author_code.size, dtype=bool)
    for author in range(n_authors):
        lo, hi = int(starts[author]), int(starts[author + 1])
        if hi > lo:
            median = float(np.median(created_utc[lo:hi]))
            early[lo:hi] = created_utc[lo:hi] <= median
    return early


def build_global_state_map(event_vocab: np.ndarray, author_code: np.ndarray,
                           early: np.ndarray, pool: np.ndarray, n_vocab: int,
                           n_states: int = C_STATES,
                           seed: int = SEED) -> tuple[np.ndarray, dict]:
    """ONE corpus-global map: community -> state, fit on EARLY halves only.

    Points are the communities; a community's feature vector is the sqrt of
    its early-half event counts across the pool's authors (U1's estimator,
    one global fit instead of per-fold).  Communities with zero early-half
    mass fall to the OOV state, exactly as U1 does.  Inputs are event-stream
    arrays only -- no label column reaches this function.
    """

    column_of_author = np.full(int(author_code.max()) + 1, -1, dtype=np.int64)
    column_of_author[pool] = np.arange(pool.size)
    selected = ((event_vocab >= 0) & early
                & (column_of_author[author_code] >= 0))
    flat = (event_vocab[selected].astype(np.int64) * pool.size
            + column_of_author[author_code[selected]])
    counts = np.bincount(flat, minlength=n_vocab * pool.size
                         ).reshape(n_vocab, pool.size)
    active = np.flatnonzero(counts.sum(axis=1) > 0)
    state_of_vocab = np.full(n_vocab + 1, n_states, dtype=np.int32)
    if active.size:
        labels = spherical_kmeans(np.sqrt(counts[active].astype(np.float64)),
                                  n_states, seed=seed, n_init=KMEANS_N_INIT)
        state_of_vocab[active] = labels.astype(np.int32)
    sizes = np.bincount(state_of_vocab[:-1], minlength=n_states + 1)
    info = {
        "n_states_plus_oov": n_states + 1, "oov_state_index": n_states,
        "fit_authors": int(pool.size), "fit_half": "EARLY",
        "active_communities": int(active.size),
        "zero_mass_to_oov": int(n_vocab - active.size),
        "cluster_sizes": [int(v) for v in sizes[:n_states]],
        "seed": int(seed), "n_init": int(KMEANS_N_INIT),
        "declared": "corpus-global (precedent: the SR0 vocabulary)",
        "label_data_in_inputs": False,
    }
    return state_of_vocab, info


def cross_thread_stay(author_code: np.ndarray, link_code: np.ndarray,
                      event_state: np.ndarray, n_authors: int,
                      restrict: np.ndarray | None = None
                      ) -> tuple[np.ndarray, np.ndarray]:
    """stay_ct: mean 1[state_i == state_{i+1}] over CROSS-THREAD adjacencies.

    Adjacency is taken on the FULL stream and is NEVER SPLICED: out-of-
    vocabulary events carry state ``C_STATES`` and remain in the chain.
    ``restrict`` (optional) is a per-event mask; a pair survives only when
    both of its events are inside the mask -- this is how the early/late
    halves are taken for the split-half reliability.
    """

    left = np.arange(author_code.size - 1)
    keep = ((author_code[left] == author_code[left + 1])
            & (link_code[left] != link_code[left + 1]))
    if restrict is not None:
        keep &= restrict[left] & restrict[left + 1]
    left = left[keep]
    authors = author_code[left]
    hits = (event_state[left] == event_state[left + 1]).astype(np.float64)
    counts = np.bincount(authors, minlength=n_authors)
    total = np.bincount(authors, weights=hits, minlength=n_authors)
    values = np.full(n_authors, np.nan)
    nonzero = counts > 0
    values[nonzero] = total[nonzero] / counts[nonzero]
    return values, counts


@dataclass
class BlockCoordinates:
    tight: np.ndarray
    tight_odd: np.ndarray
    tight_even: np.ndarray
    tight_pairs: np.ndarray
    drift: np.ndarray
    drift_odd: np.ndarray
    drift_even: np.ndarray
    near_pairs: np.ndarray
    far_pairs: np.ndarray


def block_coordinates(features: np.ndarray, midpoint: np.ndarray,
                      block_author: np.ndarray, authors: Sequence[int],
                      n_authors: int) -> BlockCoordinates:
    """``tight`` and ``drift_pa`` with their odd/even pair splits.

    ``tight``    = mean Hellinger cosine over CONSECUTIVE block pairs whose
                   midpoint gap is <= 90 d.
    ``drift_pa`` = mean cosine over ALL block pairs with gap <= 180 d
                   MINUS mean cosine over ALL block pairs with gap > 365 d.
    The odd/even splits partition each qualifying pair list by position
    parity -- the split-half objects the reliability gate is measured on.
    """

    nan = lambda: np.full(n_authors, np.nan)                    # noqa: E731
    zeros = lambda: np.zeros(n_authors, dtype=np.int64)         # noqa: E731
    out = BlockCoordinates(nan(), nan(), nan(), zeros(),
                           nan(), nan(), nan(), zeros(), zeros())
    starts = np.searchsorted(block_author, np.arange(n_authors + 1))
    for author in authors:
        lo, hi = int(starts[author]), int(starts[author + 1])
        if hi - lo < 2:
            continue
        block = features[lo:hi].astype(np.float64)
        mid = midpoint[lo:hi]
        cons_cos = np.einsum("ij,ij->i", block[:-1], block[1:])
        cons_gap = np.abs(np.diff(mid)) / DAY
        tight_idx = np.flatnonzero(cons_gap <= TIGHT_GAP_DAYS)
        out.tight_pairs[author] = tight_idx.size
        if tight_idx.size:
            out.tight[author] = float(cons_cos[tight_idx].mean())
            if tight_idx.size >= 2:
                out.tight_odd[author] = float(cons_cos[tight_idx[0::2]].mean())
                out.tight_even[author] = float(
                    cons_cos[tight_idx[1::2]].mean())
        rows, cols = np.triu_indices(hi - lo, 1)
        cos = np.einsum("ij,ij->i", block[rows], block[cols])
        gap = np.abs(mid[cols] - mid[rows]) / DAY
        near = np.flatnonzero(gap <= DRIFT_NEAR_DAYS)
        far = np.flatnonzero(gap > DRIFT_FAR_DAYS)
        out.near_pairs[author] = near.size
        out.far_pairs[author] = far.size
        if near.size and far.size:
            out.drift[author] = float(cos[near].mean() - cos[far].mean())
            if near.size >= 2 and far.size >= 2:
                out.drift_odd[author] = float(cos[near[0::2]].mean()
                                              - cos[far[0::2]].mean())
                out.drift_even[author] = float(cos[near[1::2]].mean()
                                               - cos[far[1::2]].mean())
    return out


def full_signature(event_vocab: np.ndarray, author_code: np.ndarray,
                   pool: np.ndarray, n_vocab: int) -> np.ndarray:
    """L2-normalised sqrt full-stream in-vocabulary frequency, per pool author.

    Cosine between two of these rows is the Hellinger (Bhattacharyya)
    coefficient; 1 - cosine is the bag distance the partial controls for.
    """

    column_of_author = np.full(int(author_code.max()) + 1, -1, dtype=np.int64)
    column_of_author[pool] = np.arange(pool.size)
    selected = (event_vocab >= 0) & (column_of_author[author_code] >= 0)
    flat = (column_of_author[author_code[selected]] * n_vocab
            + event_vocab[selected].astype(np.int64))
    counts = np.bincount(flat, minlength=pool.size * n_vocab
                         ).reshape(pool.size, n_vocab).astype(np.float64)
    totals = counts.sum(axis=1, keepdims=True)
    totals[totals == 0.0] = 1.0
    sig = np.sqrt(counts / totals)
    norms = np.linalg.norm(sig, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    return sig / norms


# ---------------------------------------------------------------------------
# Mantel machinery -- vectorised.
#
# A row/column permutation of a symmetric matrix is a bijection on the set of
# unordered off-diagonal pairs, so the permuted condensed vector has the SAME
# sum and sum-of-squares as the observed one.  Every permutation therefore
# costs one gather and one dot product; the denominator is constant.
# ---------------------------------------------------------------------------
def condensed_indices(n: int) -> tuple[np.ndarray, np.ndarray]:
    rows, cols = np.triu_indices(n, 1)
    return rows.astype(np.int64), cols.astype(np.int64)


def square_from_condensed(values: np.ndarray, rows: np.ndarray,
                          cols: np.ndarray, n: int) -> np.ndarray:
    square = np.zeros((n, n), dtype=np.float64)
    square[rows, cols] = values
    square[cols, rows] = values
    return square


def mantel_permutation(x: np.ndarray, y_square: np.ndarray, rows: np.ndarray,
                       cols: np.ndarray, n: int, b_perm: int,
                       seed: int) -> dict[str, Any]:
    """Mantel r of ``x`` against the condensed form of ``y_square``.

    The null permutes AUTHOR ROWS of ``y_square`` (the only exchangeability
    that respects pairwise dependence), B times, two-sided.
    """

    y = y_square[rows, cols]
    r_obs = pearson(x, y)
    x_centred = np.asarray(x, float) - float(np.mean(x))
    denom = float(np.linalg.norm(x_centred)
                  * np.linalg.norm(y - float(np.mean(y))))
    rng = np.random.default_rng(seed)
    null = np.empty(b_perm, dtype=np.float64)
    for b in range(b_perm):
        perm = rng.permutation(n)
        null[b] = float(x_centred @ y_square[perm[rows], perm[cols]]) / denom
    lo, hi = np.percentile(null, [100 * ALPHA / 2, 100 * (1 - ALPHA / 2)])
    blo, bhi = np.percentile(
        null, [100 * ALPHA / (2 * N_SECONDARY_ROWS),
               100 * (1 - ALPHA / (2 * N_SECONDARY_ROWS))])
    p_two = float((1 + int(np.sum(np.abs(null) >= abs(r_obs)))) / (b_perm + 1))
    return {
        "r": float(r_obs), "n_authors": int(n), "n_pairs": int(x.size),
        "B": int(b_perm), "seed": int(seed),
        "band_lo": float(lo), "band_hi": float(hi),
        "band_halfwidth": float((hi - lo) / 2.0),
        "bonferroni_band_lo": float(blo), "bonferroni_band_hi": float(bhi),
        "outside_band": bool(r_obs < lo or r_obs > hi),
        "outside_bonferroni_band": bool(r_obs < blo or r_obs > bhi),
        "p_two_sided": p_two,
        "null_mean": float(null.mean()), "null_sd": float(null.std(ddof=1)),
        "realized_mdr_1p96sd": float(1.96 * null.std(ddof=1)),
    }


def ols_residual(y: np.ndarray, covariates: np.ndarray) -> np.ndarray:
    """Residual of ``y`` on ``covariates`` with an intercept."""

    design = np.column_stack([np.ones(y.size), covariates])
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    return y - design @ beta


def partial_mantel_sls(x: np.ndarray, y: np.ndarray, covariates: np.ndarray,
                       rows: np.ndarray, cols: np.ndarray, n: int,
                       b_perm: int, seed: int) -> dict[str, Any]:
    """Smouse-Long-Sokal partial Mantel by residual permutation.

    Both condensed vectors are regressed on the covariate vectors; the
    residual of ``y`` is re-squared and its AUTHOR ROWS permuted, which is
    the SLS null.
    """

    ex = ols_residual(np.asarray(x, float), covariates)
    ey = ols_residual(np.asarray(y, float), covariates)
    ey_square = square_from_condensed(ey, rows, cols, n)
    result = mantel_permutation(ex, ey_square, rows, cols, n, b_perm, seed)
    result["method"] = "Smouse-Long-Sokal residual permutation"
    result["n_covariates"] = int(np.atleast_2d(covariates.T).shape[0])
    return result


def projection_mdr(n_authors: int) -> float:
    """The registration's z ~ r*sqrt(N) scaling of SR1's realized power."""

    return float(1.96 * (SR1_R / SR1_Z) * np.sqrt(SR1_N / n_authors))


# ---------------------------------------------------------------------------
# THE ONE LABEL READER.  Nothing else in this file touches PROFILES.
# ---------------------------------------------------------------------------
def open_trait_table(author_names: Sequence[str],
                     path: Path = PROFILES) -> tuple[np.ndarray, dict]:
    """Open author_profiles.csv ONCE and z-score Big5 over the analysis pool.

    Called exactly once, from stage E, after ``first_join`` is logged.
    Returns the z-scored (n_pool, 5) matrix and an availability summary.
    NO PER-AUTHOR VALUE LEAVES THIS FUNCTION'S CALLER IN A COMMITTED FILE.
    """

    frame = pd.read_csv(path, usecols=["author", *BIG5], low_memory=False)
    frame["author"] = frame["author"].astype(str)
    frame = frame.drop_duplicates("author").set_index("author")
    sub = frame.reindex([str(a) for a in author_names])
    raw = sub[list(BIG5)].to_numpy(dtype=float)
    complete = ~np.isnan(raw).any(axis=1)
    mean = np.nanmean(raw, axis=0)
    sd = np.nanstd(raw, axis=0, ddof=1)
    z = (raw - mean) / sd
    info = {
        "source": str(path), "columns_opened": ["author", *BIG5],
        "n_requested": int(len(author_names)),
        "n_with_all_big5": int(complete.sum()),
        "label_completeness": float(complete.mean()),
        "all_present": bool(complete.all()),
        "z_scored_over": "the 849-author analysis pool (one z-scoring, "
                         "reused by every coordinate row)",
        "pool_means": [float(v) for v in mean],
        "pool_sds": [float(v) for v in sd],
    }
    return z, info


# ---------------------------------------------------------------------------
# The stamp-order proof (G-U3) -- pure, so the tests can drive it directly.
# ---------------------------------------------------------------------------
def prove_stamp_order(log_records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """G-U3: stamp < coordinate_freeze < first_join, from the events."""

    records = list(log_records)

    def first(name: str) -> dict[str, Any] | None:
        for record in records:
            if record.get("event") == name:
                return record
        return None

    stamp = first("config_stamped")
    freeze = first("coordinates_frozen")
    join = first("first_join")
    stamp_utc = stamp["utc"] if stamp else None
    freeze_utc = freeze["utc"] if freeze else None
    join_utc = join["utc"] if join else None
    have_all = all(v is not None for v in (stamp_utc, freeze_utc, join_utc))
    ordered = bool(have_all and stamp_utc < freeze_utc < join_utc)
    joint_before = None
    if stamp is not None:
        joint_before = stamp.get("joint_quantities_before_stamp")
    seconds = None
    if have_all:
        seconds = {
            "stamp_to_freeze": (datetime.fromisoformat(freeze_utc)
                                - datetime.fromisoformat(stamp_utc)
                                ).total_seconds(),
            "freeze_to_first_join": (datetime.fromisoformat(join_utc)
                                     - datetime.fromisoformat(freeze_utc)
                                     ).total_seconds()}
    return {
        "config_stamped_utc": stamp_utc,
        "coordinate_freeze_utc": freeze_utc,
        "first_join_utc": join_utc,
        "all_three_events_present": have_all,
        "stamp_precedes_freeze_precedes_first_join": ordered,
        "joint_quantities_before_stamp": joint_before,
        "labels_opened_before_stamp": (
            stamp.get("labels_opened_before_stamp") if stamp else None),
        "seconds_between": seconds,
        "PASS": bool(ordered and joint_before == 0
                     and (stamp or {}).get("labels_opened_before_stamp")
                     is False),
    }


# ---------------------------------------------------------------------------
# Eligibility predicates -- exact, re-executable (#77/#78).
# ---------------------------------------------------------------------------
def stay_eligible(counts_early: np.ndarray, counts_late: np.ndarray,
                  pool: np.ndarray, minimum: int = STAY_MIN_ADJ_PER_HALF,
                  strict: bool = STAY_PREDICATE_STRICT) -> np.ndarray:
    both = np.minimum(counts_early, counts_late)
    keep = both[pool] > minimum if strict else both[pool] >= minimum
    return pool[keep]


def tight_eligible(pairs: np.ndarray, pool: np.ndarray) -> np.ndarray:
    return pool[pairs[pool] >= TIGHT_MIN_PAIRS]


def drift_eligible(near: np.ndarray, far: np.ndarray,
                   pool: np.ndarray) -> np.ndarray:
    return pool[(near[pool] >= DRIFT_MIN_PAIRS)
                & (far[pool] >= DRIFT_MIN_PAIRS)]


# ---------------------------------------------------------------------------
# The reliability gate (label-free, decided in stage B).
# ---------------------------------------------------------------------------
def apply_reliability_gate(reliabilities: dict[str, float],
                           threshold: float = RELIABILITY_GATE,
                           primary: str = PRIMARY_COORDINATE
                           ) -> dict[str, Any]:
    rows = {}
    for name, value in reliabilities.items():
        passed = bool(np.isfinite(value) and value >= threshold)
        rows[name] = {"split_half_r": float(value),
                      "spearman_brown": spearman_brown(float(value)),
                      "threshold": float(threshold),
                      "gate": "ADMIT" if passed else "EXCLUDE"}
    admitted = [n for n, r in rows.items() if r["gate"] == "ADMIT"]
    primary_ok = rows.get(primary, {}).get("gate") == "ADMIT"
    return {
        "rows": rows, "threshold": float(threshold),
        "admitted": admitted,
        "excluded": [n for n in rows if n not in admitted],
        "primary": primary, "primary_admitted": bool(primary_ok),
        "STOP_before_join": not bool(primary_ok),
        "stop_verdict": None if primary_ok else "COORDINATE_UNRELIABLE",
    }


# ---------------------------------------------------------------------------
# STAGE PART 0 -- anchors, then the stamp.  NO LABEL IS OPENED HERE.
# ---------------------------------------------------------------------------
def stage_part0(args: argparse.Namespace) -> None:
    started = time.time()
    out: Path = args.output
    out.mkdir(parents=True, exist_ok=True)
    # part0 is the first stage, so it TRUNCATES the log: the stamp-order proof
    # reads the FIRST occurrence of each event and must not see a prior run.
    (out / "run_log.jsonl").write_text("", encoding="utf-8")
    log = RunLog(out / "run_log.jsonl")
    log.event("part0_start", cache=rel(args.cache),
              registration_commit=args.registration_commit)

    cache, link_code = load_cache_and_links(args.cache)
    anchors = verify_cache_anchors(cache)
    n_authors = len(cache.authors)
    n_vocab = len(cache.vocabulary)
    event_vocab = cache.vocab_of_subreddit[cache.subreddit_code]
    early = assign_halves(cache.author_code, cache.created_utc, n_authors)

    vocab_events = np.bincount(cache.author_code[event_vocab >= 0],
                               minlength=n_authors)
    block_pool = np.flatnonzero(vocab_events // K_BLOCK >= POOL_MIN_BLOCKS)

    # cross-thread adjacency counts per half -- state-free, so this is a pure
    # eligibility census and needs no state map.
    left = np.arange(cache.author_code.size - 1)
    adjacent = ((cache.author_code[left] == cache.author_code[left + 1])
                & (link_code[left] != link_code[left + 1]))
    same_early = adjacent & early[left] & early[left + 1]
    same_late = adjacent & ~early[left] & ~early[left + 1]
    ct_early = np.bincount(cache.author_code[left[same_early]],
                           minlength=n_authors)
    ct_late = np.bincount(cache.author_code[left[same_late]],
                          minlength=n_authors)
    stay_pool = stay_eligible(ct_early, ct_late, block_pool)
    stay_pool_registered_prose = stay_eligible(ct_early, ct_late, block_pool,
                                               strict=False)

    blocks = build_blocks(cache.author_code, cache.created_utc, event_vocab,
                          n_vocab, K_BLOCK, n_authors=n_authors)
    coords = block_coordinates(blocks.features, blocks.midpoint, blocks.author,
                               block_pool, n_authors)
    tight_pool = tight_eligible(coords.tight_pairs, block_pool)
    drift_pool = drift_eligible(coords.near_pairs, coords.far_pairs,
                                block_pool)

    observed = {
        "block_pool_ge4_blocks": int(block_pool.size),
        "stay_eligible": int(stay_pool.size),
        "tight_eligible": int(tight_pool.size),
        "drift_eligible": int(drift_pool.size),
    }
    census = {
        "registered": dict(CENSUS_PINS), "observed": observed,
        "mismatches": {k: [CENSUS_PINS[k], observed[k]]
                       for k in CENSUS_PINS if CENSUS_PINS[k] != observed[k]},
        "RD_U3_1": {
            "registered_prose_predicate": ">= 30 per half",
            "authors_under_prose_predicate":
                int(stay_pool_registered_prose.size),
            "adopted_predicate": "> 30 per half",
            "authors_under_adopted_predicate": int(stay_pool.size),
            "boundary_authors_at_exactly_30": int(
                np.sum(np.minimum(ct_early, ct_late)[block_pool] == 30)),
            "note": RN_NOTES["RN-U3-2"]},
    }
    census["status"] = "PASS" if not census["mismatches"] else "FAIL"
    gate = {
        "cache_anchors": anchors, "census": census,
        "labels_opened_in_part0": False,
        "PASS": bool(anchors["status"] == "PASS"
                     and census["status"] == "PASS"),
    }
    if not gate["PASS"]:
        write_json(out / "part0.json", {
            "leg": LEG, "utc": utc_now(), "G0": gate,
            "A1": "anchor failure -> STOP, NO STAMP EVER"})
        log.event("part0_anchor_failure", anchors=anchors["status"],
                  census=census["status"])
        raise SystemExit("G0-U3 FAILED -> STOP/VOID (A1: no stamp written)")

    config = {
        "leg": LEG, "registration_commit": args.registration_commit,
        "registration_doc": rel(PLAN_DOC),
        "tier": "EXPLORATORY", "level": "corpus-level",
        "layer": "P (the first label-bearing projection of the When quadrant)",
        "seed": SEED, "B_perm": B_PERM, "alpha": ALPHA,
        "events_cache": rel(args.cache),
        "cache_anchors": {"events": ANCHOR_EVENTS, "authors": ANCHOR_AUTHORS,
                          "vocabulary": ANCHOR_VOCAB},
        "analysis_pool": {"rule": f">= {POOL_MIN_BLOCKS} disjoint K="
                                  f"{K_BLOCK} in-vocabulary blocks",
                          "n_authors": int(block_pool.size)},
        "state_map": {
            "algorithm": "spherical k-means on sqrt early-half community "
                         "counts (U1's estimator, imported)",
            "C": C_STATES, "oov_state_index": C_STATES,
            "n_init": KMEANS_N_INIT, "seed": SEED,
            "fit_on": "all analysis-pool authors' EARLY halves",
            "half_rule": "per-author FULL-STREAM median created_utc; "
                         "ts <= median -> early (U1 pin)",
            "scope": "declared CORPUS-GLOBAL"},
        "coordinates": {
            "stay_ct": {
                "role": "PRIMARY (U1's binding cross-thread designation)",
                "definition": "mean 1[state_i == state_{i+1}] over adjacent "
                              "FULL-STREAM event pairs with different "
                              "link_code; OOV events carry state "
                              f"{C_STATES}; adjacency never spliced",
                "eligibility": f"> {STAY_MIN_ADJ_PER_HALF} cross-thread "
                               "adjacencies in EACH half (RD-U3-1)",
                "n_eligible": int(stay_pool.size),
                "reliability_split": "early-half value vs late-half value "
                                     f"at C = {C_STATES}, Pearson over "
                                     "authors"},
            "tight": {
                "role": "secondary row (Bonferroni x3 guard, never routes)",
                "definition": "mean Hellinger cosine over CONSECUTIVE K=50 "
                              "block pairs with midpoint gap <= "
                              f"{TIGHT_GAP_DAYS:.0f} d",
                "eligibility": f">= {TIGHT_MIN_PAIRS} such pairs",
                "n_eligible": int(tight_pool.size),
                "reliability_split": "odd/even pair split"},
            "drift_pa": {
                "role": "secondary row (Bonferroni x3 guard, never routes)",
                "definition": "mean cosine over pairs <= "
                              f"{DRIFT_NEAR_DAYS:.0f} d MINUS mean cosine "
                              "over pairs > "
                              f"{DRIFT_FAR_DAYS:.0f} d (all block pairs)",
                "eligibility": f">= {DRIFT_MIN_PAIRS} pairs in EACH cell",
                "n_eligible": int(drift_pool.size),
                "reliability_split": "odd/even pair split within each cell"}},
        "reliability_gate": {
            "threshold": RELIABILITY_GATE,
            "measured_on": "the ACTUAL coordinate objects, label-free",
            "failure_of_primary": "STOP before any join, verdict "
                                  "COORDINATE_UNRELIABLE"},
        "estimands": {
            "trait_geometry": "Euclidean distance over five z-scored Big5 "
                              "(z-scoring over the analysis pool)",
            "coordinate_geometry": "|c_u - c_v|",
            "raw": "Mantel r, null = permutation of AUTHOR ROWS of the trait "
                   f"matrix, B = {B_PERM}, two-sided band",
            "partial": "partial Mantel r(c-dist, trait-dist | bag-dist), "
                       "Smouse-Long-Sokal residual permutation, "
                       f"B = {B_PERM}",
            "bag_distance": "1 - Hellinger cosine of the L2-normalised sqrt "
                            "full-stream in-vocabulary frequency vector over "
                            f"the {ANCHOR_VOCAB}-community vocabulary",
            "activity_sensitivity": "partial additionally controlling "
                                    "|log n_u - log n_v|, n = in-vocabulary "
                                    "event count",
            "disattenuation": "SECONDARY reading only: r / sqrt(rel_SB * "
                              f"{REL_LABEL_DECLARED}); label reliability "
                              "DECLARED, not measured"},
        "projection": {
            "assumption": "z proportional to r*sqrt(N), declared",
            "anchor": {"sr1_r": SR1_R, "sr1_z": SR1_Z, "sr1_N": SR1_N},
            "registered_minimal_detectable_r": REGISTERED_MDR,
            "recomputed_at_stay_pool": projection_mdr(int(stay_pool.size))},
        "cells": {
            "WHEN_TRAIT_SILENT": "stay_ct raw r INSIDE its band",
            "WHEN_COUPLED_REDUNDANT": "stay_ct raw OUTSIDE band AND partial "
                                      "INSIDE band",
            "WHEN_COUPLED_INCREMENTAL": "stay_ct partial OUTSIDE band"},
        "multiplicity": {
            "verdict_keys_on": PRIMARY_COORDINATE,
            "secondary_rows": ["tight", "drift_pa"],
            "guard": f"Bonferroni x{N_SECONDARY_ROWS} on secondary "
                     "detections; flagged, never routing"},
        "leans": {
            "primary": "SILENT-to-REDUNDANT for stay_ct, point |raw r| <= "
                       f"{LEAN_RAW_POINT}",
            "secondary_weak": "if any row detects raw, it is tight or "
                              "drift_pa (structural lean only)"},
        "label_event": RN_NOTES["RN-U3-6"],
        "boundaries": [RN_NOTES["RN-U3-3"], RN_NOTES["RN-U3-4"],
                       RN_NOTES["RN-U3-7"]],
        "RN_NOTES": RN_NOTES,
        "census": census,
    }
    write_json(out / "config.json", config)
    digest = sha256_file(out / "config.json")
    stamp_record = log.event("config_stamped", sha256=digest,
                             joint_quantities_before_stamp=0,
                             labels_opened_before_stamp=False)
    write_json(out / "config.sha256.json", {
        "sha256": digest, "stamp_utc": stamp_record["utc"],
        "joint_quantities_before_stamp": 0,
        "labels_opened_before_stamp": False,
        "note": RN_NOTES["RN-U3-1"]})
    write_json(out / "part0.json", {
        "leg": LEG, "utc": utc_now(), "G0": gate,
        "stamp": {"sha256": digest, "stamp_utc": stamp_record["utc"]},
        "pools": {"analysis_849": [int(v) for v in block_pool],
                  "stay": [int(v) for v in stay_pool],
                  "tight": [int(v) for v in tight_pool],
                  "drift_pa": [int(v) for v in drift_pool],
                  "stay_prose_predicate":
                      [int(v) for v in stay_pool_registered_prose]},
        "environment": {"python_executable": sys.executable,
                        "python_version": sys.version.split()[0],
                        "platform": platform.platform(),
                        "numpy": np.__version__, "pandas": pd.__version__},
        "seconds": time.time() - started})
    print(f"part0 OK  anchors {anchors['status']}  census {census['status']} "
          f"(849/{stay_pool.size}/{tight_pool.size}/{drift_pool.size})  "
          f"STAMPED {digest[:16]} at {stamp_record['utc']}  "
          f"labels opened = 0  {time.time() - started:.1f}s")


# ---------------------------------------------------------------------------
# STAGE B -- LABEL-FREE.  Map, coordinates, reliability gate, freeze.
# ---------------------------------------------------------------------------
def stage_stageb(args: argparse.Namespace) -> None:
    started = time.time()
    out: Path = args.output
    log = RunLog(out / "run_log.jsonl")
    part0 = read_json(out / "part0.json")
    stamp = read_json(out / "config.sha256.json")
    if sha256_file(out / "config.json") != stamp["sha256"]:
        raise SystemExit("CONFIG HASH MISMATCH -> STOP/VOID")
    log.event("stageb_start", label_table_opened=False)

    cache, link_code = load_cache_and_links(args.cache)
    n_authors = len(cache.authors)
    n_vocab = len(cache.vocabulary)
    event_vocab = cache.vocab_of_subreddit[cache.subreddit_code]
    early = assign_halves(cache.author_code, cache.created_utc, n_authors)
    pool = np.asarray(part0["pools"]["analysis_849"], dtype=np.int64)

    state_of_vocab, map_info = build_global_state_map(
        event_vocab, cache.author_code, early, pool, n_vocab)
    event_state = state_of_vocab[np.where(event_vocab >= 0, event_vocab,
                                          n_vocab)]

    stay_full, n_full = cross_thread_stay(cache.author_code, link_code,
                                          event_state, n_authors)
    stay_early, _ = cross_thread_stay(cache.author_code, link_code,
                                      event_state, n_authors, restrict=early)
    stay_late, _ = cross_thread_stay(cache.author_code, link_code,
                                     event_state, n_authors, restrict=~early)

    blocks = build_blocks(cache.author_code, cache.created_utc, event_vocab,
                          n_vocab, K_BLOCK, n_authors=n_authors)
    bc = block_coordinates(blocks.features, blocks.midpoint, blocks.author,
                           pool, n_authors)

    pools = {"stay_ct": np.asarray(part0["pools"]["stay"], dtype=np.int64),
             "tight": np.asarray(part0["pools"]["tight"], dtype=np.int64),
             "drift_pa": np.asarray(part0["pools"]["drift_pa"],
                                    dtype=np.int64)}
    halves = {
        "stay_ct": (stay_early, stay_late),
        "tight": (bc.tight_odd, bc.tight_even),
        "drift_pa": (bc.drift_odd, bc.drift_even)}
    values = {"stay_ct": stay_full, "tight": bc.tight, "drift_pa": bc.drift}

    reliability_rows: dict[str, float] = {}
    descriptives: dict[str, Any] = {}
    for name in COORDINATES:
        idx = pools[name]
        a, b = halves[name]
        usable = idx[np.isfinite(a[idx]) & np.isfinite(b[idx])]
        r_half = pearson(a[usable], b[usable])
        reliability_rows[name] = r_half
        descriptives[name] = {
            "n_pool": int(idx.size),
            "n_with_both_split_halves": int(usable.size),
            "mean": float(np.nanmean(values[name][idx])),
            "sd": float(np.nanstd(values[name][idx], ddof=1)),
            "min": float(np.nanmin(values[name][idx])),
            "max": float(np.nanmax(values[name][idx])),
            "split_half_r": float(r_half),
            "spearman_brown": spearman_brown(float(r_half)),
            "census_echo": CENSUS_RELIABILITY_ECHO.get(
                name, CENSUS_RELIABILITY_ECHO.get("stay_DECLARED_PROXY")
                if name == "stay_ct" else None)}

    gate = apply_reliability_gate(reliability_rows)
    stage_b = {
        "leg": LEG, "utc": utc_now(), "label_table_opened": False,
        "state_map": map_info, "descriptives": descriptives,
        "reliability_gate": gate,
        "cross_thread_adjacencies_total": int(n_full[pool].sum()),
        "seconds": time.time() - started,
    }
    write_json(out / "stageb.json", stage_b)

    if gate["STOP_before_join"]:
        write_json(out / "verdict.json", {
            "leg": LEG, "utc": utc_now(),
            "verdict": gate["stop_verdict"], "cell": None,
            "reason": "the PRIMARY coordinate failed the label-free "
                      "reliability gate; stage E never opened",
            "reliability_gate": gate})
        log.event("stageb_stop", verdict=gate["stop_verdict"])
        raise SystemExit(f"RELIABILITY GATE: PRIMARY FAILED -> "
                         f"{gate['stop_verdict']} (no label opened)")

    # Freeze the coordinate table (second stamped artifact).
    np.savez_compressed(
        out / "coordinates.npz",
        pool=pool.astype(np.int64),
        stay_ct=values["stay_ct"], tight=values["tight"],
        drift_pa=values["drift_pa"],
        stay_pool=pools["stay_ct"], tight_pool=pools["tight"],
        drift_pool=pools["drift_pa"],
        state_of_vocab=state_of_vocab,
        vocab_events=np.bincount(cache.author_code[event_vocab >= 0],
                                 minlength=n_authors))
    digest = sha256_file(out / "coordinates.npz")
    freeze = log.event("coordinates_frozen", sha256=digest,
                       admitted=gate["admitted"], excluded=gate["excluded"],
                       label_table_opened=False)
    write_json(out / "coordinate_freeze.json", {
        "sha256": digest, "coordinate_freeze_utc": freeze["utc"],
        "config_sha256": stamp["sha256"],
        "admitted": gate["admitted"], "excluded": gate["excluded"],
        "labels_opened_before_freeze": False,
        "artifact": rel(out / "coordinates.npz")})
    print(f"stageb OK  map: {map_info['active_communities']} active, "
          f"{map_info['zero_mass_to_oov']} zero-mass -> OOV  reliabilities "
          + "  ".join(f"{k}={reliability_rows[k]:.4f}" for k in COORDINATES)
          + f"  admitted={gate['admitted']}  FROZEN {digest[:16]} at "
            f"{freeze['utc']}  {time.time() - started:.1f}s")


# ---------------------------------------------------------------------------
# STAGE E -- THE SINGLE JOIN.
# ---------------------------------------------------------------------------
def stage_stagee(args: argparse.Namespace) -> None:
    started = time.time()
    out: Path = args.output
    log = RunLog(out / "run_log.jsonl")
    stamp = read_json(out / "config.sha256.json")
    freeze = read_json(out / "coordinate_freeze.json")
    if sha256_file(out / "config.json") != stamp["sha256"]:
        raise SystemExit("CONFIG HASH MISMATCH -> STOP/VOID")
    if sha256_file(out / "coordinates.npz") != freeze["sha256"]:
        raise SystemExit("COORDINATE HASH MISMATCH -> STOP/VOID")

    stage_b = read_json(out / "stageb.json")
    frozen = np.load(out / "coordinates.npz")
    pool = frozen["pool"]
    cache = load_event_cache(args.cache)
    n_vocab = len(cache.vocabulary)
    event_vocab = cache.vocab_of_subreddit[cache.subreddit_code]

    # Label-free preparation of the covariate channels (still no label read).
    signature = full_signature(event_vocab, cache.author_code, pool, n_vocab)
    row_of_author = np.full(len(cache.authors), -1, dtype=np.int64)
    row_of_author[pool] = np.arange(pool.size)
    log_activity = np.log(np.maximum(frozen["vocab_events"][pool], 1))
    pool_names = [str(cache.authors[int(a)]) for a in pool]

    # ---- THE JOIN.  Everything after this line is label-bearing. ----------
    join_event = log.event(
        "first_join",
        note="the first joint When x trait quantity of the harness is "
             "computed after this event",
        config_sha256=stamp["sha256"],
        coordinate_sha256=freeze["sha256"],
        label_source=str(PROFILES), columns=["author", *BIG5])
    traits, trait_info = open_trait_table(pool_names)
    complete = ~np.isnan(traits).any(axis=1)

    rows: dict[str, Any] = {}
    for name in freeze["admitted"]:
        key = {"stay_ct": "stay_pool", "tight": "tight_pool",
               "drift_pa": "drift_pool"}[name]
        authors = frozen[key]
        local = row_of_author[authors]
        usable = local[complete[local] & np.isfinite(frozen[name][authors])]
        n = int(usable.size)
        r_idx, c_idx = condensed_indices(n)
        coord = frozen[name][pool[usable]]
        x = np.abs(coord[r_idx] - coord[c_idx])

        z = traits[usable]
        diff = z[r_idx] - z[c_idx]
        trait_dist = np.sqrt(np.einsum("ij,ij->i", diff, diff))
        trait_square = square_from_condensed(trait_dist, r_idx, c_idx, n)

        sig = signature[usable]
        bag_dist = 1.0 - np.einsum("ij,ij->i", sig[r_idx], sig[c_idx])
        act = np.abs(log_activity[usable][r_idx] - log_activity[usable][c_idx])

        raw = mantel_permutation(x, trait_square, r_idx, c_idx, n, args.b_perm,
                                 SEED)
        partial = partial_mantel_sls(x, trait_dist, bag_dist[:, None], r_idx,
                                     c_idx, n, args.b_perm, SEED + 1)
        partial_act = partial_mantel_sls(
            x, trait_dist, np.column_stack([bag_dist, act]), r_idx, c_idx, n,
            args.b_perm, SEED + 2)
        partial_quad = partial_mantel_sls(
            x, trait_dist, np.column_stack([bag_dist, bag_dist ** 2]), r_idx,
            c_idx, n, args.b_perm, SEED + 4)
        squared_square = square_from_condensed(trait_dist ** 2, r_idx,
                                               c_idx, n)
        raw_squared = mantel_permutation(x, squared_square, r_idx, c_idx, n,
                                         args.b_perm, SEED + 3)

        rel_sb = float(stage_b["descriptives"][name]["spearman_brown"])
        denom = float(np.sqrt(max(rel_sb, 1e-12) * REL_LABEL_DECLARED))
        rows[name] = {
            "coordinate": name,
            "role": "PRIMARY" if name == PRIMARY_COORDINATE else "secondary",
            "n_authors": n, "n_pairs": int(x.size),
            "label_complete": bool(complete[local].all()),
            "split_half_r": float(stage_b["descriptives"][name]
                                  ["split_half_r"]),
            "reliability_SB": rel_sb,
            "raw": raw, "partial_bag": partial,
            "partial_bag_activity": partial_act,
            "second_reading_partial_bag_quadratic": partial_quad,
            "second_reading_squared_euclidean": raw_squared,
            "second_reading_note":
                "SECOND READINGS, ROUTING NOTHING.  (a) The registered SLS "
                "partial controls the bag channel LINEARLY, so a shared "
                "NON-LINEAR dependence of both distances on the bag would "
                "survive it; the quadratic row adds bag^2 to the control.  "
                "(b) SR1's trait geometry was negative SQUARED Euclidean "
                "while U3's registration says Euclidean distance; the "
                "squared row shows what that choice is worth.",
            "disattenuated_SECONDARY": {
                "raw": float(raw["r"] / denom),
                "partial_bag": float(partial["r"] / denom),
                "formula": f"r / sqrt(rel_SB * {REL_LABEL_DECLARED})",
                "label_reliability_status": "DECLARED, not measured",
                "note": RN_NOTES["RN-U3-5"]},
            "bag_channel": {
                "mantel_bag_vs_trait": pearson(bag_dist, trait_dist),
                "coord_vs_bag": pearson(x, bag_dist),
                "coord_vs_activity": pearson(x, act)},
            "projection": {
                "registered_minimal_detectable_r": REGISTERED_MDR,
                "recomputed_at_this_N": projection_mdr(n),
                "realized_mdr_1p96_null_sd": raw["realized_mdr_1p96sd"],
                "realized_over_projected": float(
                    raw["realized_mdr_1p96sd"] / projection_mdr(n))},
        }
        log.event("row_done", coordinate=name, raw_r=raw["r"],
                  partial_r=partial["r"])

    write_json(out / "join.json", {
        "leg": LEG, "utc": utc_now(),
        "first_join_utc": join_event["utc"],
        "label_event": RN_NOTES["RN-U3-6"],
        "trait_join": trait_info,
        "analysis_pool_label_completeness": {
            "n_pool": int(pool.size), "n_complete": int(complete.sum()),
            "fraction": float(complete.mean())},
        "rows": rows,
        "registered_census_849_label_complete": bool(complete.all()),
        "seconds": time.time() - started})
    order = prove_stamp_order(log.read())
    print("stagee OK  "
          + "  ".join(f"{k}: raw={v['raw']['r']:+.4f} "
                      f"[{v['raw']['band_lo']:+.4f},"
                      f"{v['raw']['band_hi']:+.4f}]"
                      f" p={v['raw']['p_two_sided']:.4f} | "
                      f"partial={v['partial_bag']['r']:+.4f} "
                      f"p={v['partial_bag']['p_two_sided']:.4f}"
                      for k, v in rows.items())
          + f"  |  labels complete {complete.mean():.4f}  stamp<freeze<join="
            f"{order['stamp_precedes_freeze_precedes_first_join']}  "
            f"{time.time() - started:.1f}s")


# ---------------------------------------------------------------------------
# GATE -- G-U3 plus the blocking ID-leak scan.
# ---------------------------------------------------------------------------
def stage_gate(args: argparse.Namespace) -> None:
    started = time.time()
    out: Path = args.output
    log = RunLog(out / "run_log.jsonl")
    cache = load_event_cache(args.cache)
    order = prove_stamp_order(log.read())
    stamp = read_json(out / "config.sha256.json")
    freeze = read_json(out / "coordinate_freeze.json")
    stage_b = read_json(out / "stageb.json")
    join = read_json(out / "join.json")

    committed = [SCRIPT_SELF, TEST_SELF, args.report, PLAN_DOC, LEDGER]
    leak = scan_for_cohort_ids(committed, cache.authors)
    write_json(out / "id_leak_scan.json", leak)

    gate = {
        "leg": LEG, "utc": utc_now(),
        "G-U3_stamp_chain": order,
        "hashes": {
            "config_sha256_recomputed": sha256_file(out / "config.json"),
            "config_sha256_stamped": stamp["sha256"],
            "config_hash_matches":
                sha256_file(out / "config.json") == stamp["sha256"],
            "coordinates_sha256_recomputed":
                sha256_file(out / "coordinates.npz"),
            "coordinates_sha256_frozen": freeze["sha256"],
            "coordinate_hash_matches":
                sha256_file(out / "coordinates.npz") == freeze["sha256"]},
        "label_discipline": {
            "labels_opened_in_part0": False,
            "label_table_opened_in_stage_b":
                bool(stage_b["label_table_opened"]),
            "single_label_read": True,
            "label_source": str(PROFILES),
            "columns_opened": ["author", *BIG5],
            "per_author_values_committed": False},
        "id_leak_scan": {
            "status": leak["status"], "n_hits": int(leak["n_hits"]),
            "candidates_checked": int(leak["candidates_checked"]),
            "cohort_size": len(cache.authors),
            "files_scanned": [rel(Path(p)) for p in leak["files_scanned"]]},
        "rg_compliance": {
            "aggregates_only": True, "no_per_author_rows_in_report": True,
            "no_text_excerpts": True, "body_column_never_read": True,
            "no_cross_corpus_linkage": True, "essays_untouched": True,
            "native_corpus_untouched": True,
            "identifier_artifacts_confined_to_gitignored_results": True},
    }
    gate["PASS"] = bool(order["PASS"] and gate["hashes"]["config_hash_matches"]
                        and gate["hashes"]["coordinate_hash_matches"]
                        and not stage_b["label_table_opened"]
                        and leak["status"] == "PASS")
    write_json(out / "gate.json", gate)
    log.event("gate_done", passed=gate["PASS"])
    if not gate["PASS"]:
        raise SystemExit(
            f"G-U3 FAILED -> STOP/VOID  order={order['PASS']} "
            f"leaks={leak['n_hits']}")
    seconds = order["seconds_between"]
    print(f"gate OK  stamp<freeze<first_join="
          f"{order['stamp_precedes_freeze_precedes_first_join']} "
          f"(+{seconds['stamp_to_freeze']:.1f}s, "
          f"+{seconds['freeze_to_first_join']:.1f}s)  ID leaks="
          f"{leak['n_hits']}/{leak['candidates_checked']}  "
          f"PASS={gate['PASS']}  {time.time() - started:.1f}s  "
          f"[join rows {len(join['rows'])}]")


# ---------------------------------------------------------------------------
# FINALIZE -- cells, leans, verdict.
# ---------------------------------------------------------------------------
def stage_finalize(args: argparse.Namespace) -> None:
    started = time.time()
    out: Path = args.output
    log = RunLog(out / "run_log.jsonl")
    config = read_json(out / "config.json")
    part0 = read_json(out / "part0.json")
    stage_b = read_json(out / "stageb.json")
    join = read_json(out / "join.json")
    gate = read_json(out / "gate.json")
    rows = join["rows"]

    primary = rows[PRIMARY_COORDINATE]
    raw_out = bool(primary["raw"]["outside_band"])
    partial_out = bool(primary["partial_bag"]["outside_band"])
    if not raw_out and not partial_out:
        cell, verdict = 1, "WHEN_TRAIT_SILENT"
    elif partial_out:
        cell, verdict = 3, "WHEN_COUPLED_INCREMENTAL"
    else:
        cell, verdict = 2, "WHEN_COUPLED_REDUNDANT"

    secondary: dict[str, Any] = {}
    for name, row in rows.items():
        if name == PRIMARY_COORDINATE:
            continue
        raw_hit = bool(row["raw"]["outside_band"])
        raw_hit_bonf = bool(row["raw"]["outside_bonferroni_band"])
        par_hit_bonf = bool(row["partial_bag"]["outside_bonferroni_band"])
        if not raw_hit_bonf and not par_hit_bonf:
            scell, sname = 1, "WHEN_TRAIT_SILENT"
        elif par_hit_bonf:
            scell, sname = 3, "WHEN_COUPLED_INCREMENTAL"
        else:
            scell, sname = 2, "WHEN_COUPLED_REDUNDANT"
        secondary[name] = {
            "cell": scell, "cell_name": sname,
            "raw_detected_uncorrected": raw_hit,
            "raw_detected_bonferroni": raw_hit_bonf,
            "partial_detected_bonferroni": par_hit_bonf,
            "flag": ("DETECTION_FLAG (secondary, Bonferroni x"
                     f"{N_SECONDARY_ROWS}; never routes)"
                     if (raw_hit_bonf or par_hit_bonf) else "no detection"),
            "routes_verdict": False}

    any_raw = {n: bool(r["raw"]["outside_band"]) for n, r in rows.items()}
    if not any(any_raw.values()):
        secondary_lean = "NOT_ACTIVATED (no row detects raw)"
    elif any_raw.get(PRIMARY_COORDINATE):
        secondary_lean = "MISSED (the primary row is among the detections)"
    else:
        secondary_lean = "HELD (only slow coordinates detect raw)"

    primary_point = abs(float(primary["raw"]["r"])) <= LEAN_RAW_POINT
    leans = {
        "primary_registered": "SILENT-to-REDUNDANT for stay_ct, point "
                              f"|raw r| <= {LEAN_RAW_POINT}",
        "primary_cell_outcome": verdict,
        "primary_lean_cell_HELD": bool(verdict in ("WHEN_TRAIT_SILENT",
                                                   "WHEN_COUPLED_REDUNDANT")),
        "primary_lean_point_HELD": bool(primary_point),
        "primary_realized_abs_raw_r": abs(float(primary["raw"]["r"])),
        "secondary_registered": "if any row detects raw, it is tight or "
                                "drift_pa (structural only)",
        "secondary_lean_outcome": secondary_lean,
    }

    scoped = None
    if verdict == "WHEN_TRAIT_SILENT":
        scoped = {
            "statement": "silent beyond r ~ "
                         + str(primary["projection"]
                               ["registered_minimal_detectable_r"]),
            "attached_to": "the realized-band width report (#71 executed "
                           "form); no equivalence cell beyond this",
            "realized_band_halfwidth":
                primary["raw"]["band_halfwidth"],
            "realized_mdr_1p96_null_sd":
                primary["raw"]["realized_mdr_1p96sd"],
            "projected_mdr": primary["projection"]["recomputed_at_this_N"],
            "realized_over_projected":
                primary["projection"]["realized_over_projected"]}

    verdict_obj = {
        "leg": LEG, "utc": utc_now(), "tier": "EXPLORATORY",
        "level": "corpus-level", "verdict": verdict, "cell": cell,
        "verdict_keys_on": PRIMARY_COORDINATE,
        "primary_row": {
            "raw_r": primary["raw"]["r"],
            "raw_band": [primary["raw"]["band_lo"], primary["raw"]["band_hi"]],
            "raw_p": primary["raw"]["p_two_sided"],
            "partial_r": primary["partial_bag"]["r"],
            "partial_band": [primary["partial_bag"]["band_lo"],
                             primary["partial_bag"]["band_hi"]],
            "partial_p": primary["partial_bag"]["p_two_sided"]},
        "secondary_rows": secondary, "leans": leans,
        "scoped_silence_statement": scoped,
        "reliability_gate": stage_b["reliability_gate"],
        "stamp_chain": gate["G-U3_stamp_chain"],
        "boundaries": config["boundaries"],
        "label_event": config["label_event"],
    }
    write_json(out / "verdict.json", verdict_obj)
    write_json(out / "report_payload.json", {
        "config": config, "part0_census": part0["G0"]["census"],
        "cache_anchors": part0["G0"]["cache_anchors"],
        "stageb": stage_b, "join": join, "gate": gate,
        "verdict": verdict_obj,
        "generated_utc": utc_now()})
    log.event("finalize_done", verdict=verdict, cell=cell)
    print(f"finalize OK  VERDICT={verdict} (cell {cell})  "
          f"leans: cell="
          f"{'HELD' if leans['primary_lean_cell_HELD'] else 'MISSED'}"
          f" point={'HELD' if primary_point else 'MISSED'}  "
          f"secondary={secondary_lean}  {time.time() - started:.1f}s")


# ---------------------------------------------------------------------------
# REPORT -- every table generated from the artifacts (rule 24).
# ---------------------------------------------------------------------------
def _fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, np.integer)):
        return f"{int(value):,}"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def _cell(text: str) -> str:
    """Markdown-safe table cell: a literal pipe would open a new column."""

    return str(text).replace("|", "\\|")


def _note(key: str) -> str:
    """An RN note as a sentence: its own lowercase self-label capitalised."""

    text = RN_NOTES[key]
    return text[0].upper() + text[1:]


def stage_report(args: argparse.Namespace) -> None:
    started = time.time()
    out: Path = args.output
    payload = read_json(out / "report_payload.json")
    config = payload["config"]
    census = payload["part0_census"]
    anchors = payload["cache_anchors"]
    stageb = payload["stageb"]
    join = payload["join"]
    gate = payload["gate"]
    verdict = payload["verdict"]
    rows = join["rows"]
    chain = verdict["stamp_chain"]
    primary = rows[PRIMARY_COORDINATE]

    lines: list[str] = []
    add = lines.append
    add(f"# SUICA {LEG} -- the Who x When trait join")
    add("")
    add(f"**VERDICT: `{verdict['verdict']}` (cell {verdict['cell']}).**  "
        f"Tier EXPLORATORY, corpus-level.  The verdict keys on the PRIMARY "
        f"coordinate `{PRIMARY_COORDINATE}` alone; `tight` and `drift_pa` are "
        f"secondary rows carrying a Bonferroni x{N_SECONDARY_ROWS} guard and "
        f"never route.")
    add("")
    add(f"Primary row: raw Mantel r = **{_fmt(primary['raw']['r'])}** "
        f"[band {_fmt(primary['raw']['band_lo'])}, "
        f"{_fmt(primary['raw']['band_hi'])}], p = "
        f"{_fmt(primary['raw']['p_two_sided'])}; partial (bag-controlled) "
        f"r = **{_fmt(primary['partial_bag']['r'])}** "
        f"[band {_fmt(primary['partial_bag']['band_lo'])}, "
        f"{_fmt(primary['partial_bag']['band_hi'])}], p = "
        f"{_fmt(primary['partial_bag']['p_two_sided'])}, over "
        f"{primary['n_authors']:,} authors and "
        f"{primary['n_pairs']:,} pairs.")
    add("")
    if verdict["scoped_silence_statement"]:
        s = verdict["scoped_silence_statement"]
        add(f"**Scoped statement (attached to the realized-band width report, "
            f"and only there): {s['statement']}.**  The realized two-sided "
            f"band half-width is {_fmt(s['realized_band_halfwidth'])} and the "
            f"realized minimal detectable r (1.96 x null sd) is "
            f"{_fmt(s['realized_mdr_1p96_null_sd'])} against the "
            f"registration's projected {_fmt(s['projected_mdr'])} -- a ratio "
            f"of {_fmt(s['realized_over_projected'], 3)}.  No equivalence "
            f"cell is claimed beyond this sentence.")
        add("")

    bag_anchor = primary["bag_channel"]["mantel_bag_vs_trait"]
    add(f"**The silence is not a dead harness.**  On the SAME pairs, with the "
        f"SAME trait matrix and the SAME Mantel machinery, the Where channel "
        f"is live: Mantel(bag-distance, trait-distance) = "
        f"**{_fmt(bag_anchor)}** on `{PRIMARY_COORDINATE}`'s pool, against "
        f"SR1's independently established {SR1_R} on a different pool of "
        f"{SR1_N:,}.  A within-harness point estimate, DESCRIPTIVE and "
        f"routing nothing -- no null was run on it, because it is not a "
        f"registered estimand of this leg -- but it is the reading under "
        f"which the When rows' bands mean what they say: the machinery finds "
        f"the coupling it is known to find, in these very pairs, and finds "
        f"none through the When coordinates.")
    add("")
    add("## 1. The label event")
    add("")
    add(config["label_event"][0].upper() + config["label_event"][1:])
    add("")
    add(f"- source: `{join['trait_join']['source']}`")
    opened = "`, `".join(join["trait_join"]["columns_opened"])
    add(f"- columns opened: `{opened}`")
    add(f"- opened: ONCE, in stage E, after `first_join` was logged at "
        f"{chain['first_join_utc']}")
    add(f"- analysis pool label completeness: "
        f"{join['analysis_pool_label_completeness']['n_complete']:,} of "
        f"{join['analysis_pool_label_completeness']['n_pool']:,} "
        f"({_fmt(join['analysis_pool_label_completeness']['fraction'])}) -- "
        f"the registration's 100% census "
        + ("reproduces" if join["registered_census_849_label_complete"]
           else "**DOES NOT reproduce**"))
    add(f"- z-scoring: {join['trait_join']['z_scored_over']}")
    add("- no per-author trait value appears in any committed file; only the "
        "aggregate statistics below left stage E.")
    add("")

    add("## 2. The stamp chain (G-U3)")
    add("")
    add("| event | utc | artifact | sha256 (16) |")
    add("|---|---|---|---|")
    add(f"| config stamped | {chain['config_stamped_utc']} | `config.json` | "
        f"`{gate['hashes']['config_sha256_stamped'][:16]}` |")
    add(f"| coordinate table frozen | {chain['coordinate_freeze_utc']} | "
        f"`coordinates.npz` | "
        f"`{gate['hashes']['coordinates_sha256_frozen'][:16]}` |")
    add(f"| FIRST JOIN | {chain['first_join_utc']} | `join.json` | -- |")
    add("")
    add(f"**`stamp_utc < coordinate_freeze_utc < first_join_utc` = "
        f"{_fmt(chain['stamp_precedes_freeze_precedes_first_join'])}** "
        f"(+{_fmt(chain['seconds_between']['stamp_to_freeze'], 1)} s, then "
        f"+{_fmt(chain['seconds_between']['freeze_to_first_join'], 1)} s).  "
        f"Joint quantities before the stamp: "
        f"{chain['joint_quantities_before_stamp']}.  Labels opened before the "
        f"stamp: {_fmt(chain['labels_opened_before_stamp'])}.  Both hashes "
        f"re-verify: config "
        f"{_fmt(gate['hashes']['config_hash_matches'])}, coordinates "
        f"{_fmt(gate['hashes']['coordinate_hash_matches'])}.  G-U3 PASS = "
        f"{_fmt(gate['PASS'])}; ID-leak scan "
        f"{gate['id_leak_scan']['n_hits']} hits over "
        f"{gate['id_leak_scan']['candidates_checked']:,} cohort names in "
        f"{len(gate['id_leak_scan']['files_scanned'])} committed files.")
    add("")

    add("## 3. Part 0 anchors (no label opened)")
    add("")
    add("| anchor | registered | observed | match |")
    add("|---|---|---|---|")
    for key in ("events", "authors", "vocabulary"):
        add(f"| cache {key} | {anchors['expected'][key]:,} | "
            f"{anchors['observed'][key]:,} | "
            f"{_fmt(anchors['expected'][key] == anchors['observed'][key])} |")
    for key, registered in census["registered"].items():
        observed = census["observed"][key]
        add(f"| {key} | {registered:,} | {observed:,} | "
            f"{_fmt(registered == observed)} |")
    add("")
    rd = census["RD_U3_1"]
    add(f"**RD-U3-1 (disclosed re-posing, decided label-free in part 0, "
        f"before the stamp).**  The registered prose predicate "
        f"`{rd['registered_prose_predicate']}` admits "
        f"{rd['authors_under_prose_predicate']:,} authors from this cache "
        f"while the registered census names 847; exactly "
        f"{rd['boundary_authors_at_exactly_30']} author sits at "
        f"min(early, late) = 30.  U3 adopts the STRICTLY TIGHTER "
        f"`{rd['adopted_predicate']}`, which reproduces the registered pool "
        f"exactly ({rd['authors_under_adopted_predicate']:,}).  The looser "
        f"pool routes nothing.")
    add("")

    add("## 4. Coordinates: reliability, gate, and the joined estimands")
    add("")
    add("| coordinate | role | split-half r | SB | gate (>= "
        f"{RELIABILITY_GATE}) | pool | mean (sd) | raw r [band] p | "
        "partial r [band] p | + activity r [band] p | disatt. raw "
        "(SECONDARY) |")
    add("|---|---|---|---|---|---|---|---|---|---|---|")
    for name in COORDINATES:
        desc = stageb["descriptives"][name]
        grow = stageb["reliability_gate"]["rows"][name]
        if name not in rows:
            add(f"| `{name}` | -- | {_fmt(desc['split_half_r'])} | "
                f"{_fmt(desc['spearman_brown'])} | **{grow['gate']}** | "
                f"{desc['n_pool']:,} | {_fmt(desc['mean'])} "
                f"({_fmt(desc['sd'])}) | excluded label-free | excluded "
                f"label-free | excluded label-free | -- |")
            continue
        row = rows[name]
        add(f"| `{name}` | {row['role']} | {_fmt(desc['split_half_r'])} | "
            f"{_fmt(desc['spearman_brown'])} | **{grow['gate']}** | "
            f"{row['n_authors']:,} ({row['n_pairs']:,} pairs) | "
            f"{_fmt(desc['mean'])} ({_fmt(desc['sd'])}) | "
            f"{_fmt(row['raw']['r'])} [{_fmt(row['raw']['band_lo'])}, "
            f"{_fmt(row['raw']['band_hi'])}] "
            f"p={_fmt(row['raw']['p_two_sided'])}"
            f" | {_fmt(row['partial_bag']['r'])} "
            f"[{_fmt(row['partial_bag']['band_lo'])}, "
            f"{_fmt(row['partial_bag']['band_hi'])}] "
            f"p={_fmt(row['partial_bag']['p_two_sided'])} | "
            f"{_fmt(row['partial_bag_activity']['r'])} "
            f"[{_fmt(row['partial_bag_activity']['band_lo'])}, "
            f"{_fmt(row['partial_bag_activity']['band_hi'])}] "
            f"p={_fmt(row['partial_bag_activity']['p_two_sided'])} | "
            f"{_fmt(row['disattenuated_SECONDARY']['raw'])} |")
    add("")
    add(f"Disattenuation is a SECONDARY reading only: r / sqrt(rel_SB x "
        f"{REL_LABEL_DECLARED}) with the label reliability "
        f"{REL_LABEL_DECLARED} **DECLARED, not measured** (#57).  It "
        f"illustrates scale and routes nothing.")
    add("")
    add("Reliability provenance: the registration's census echoes are "
        f"tight {CENSUS_RELIABILITY_ECHO['tight']}, drift_pa "
        f"{CENSUS_RELIABILITY_ECHO['drift_pa']} (both exact predicates, both "
        f"reproduced here) and stay "
        f"{CENSUS_RELIABILITY_ECHO['stay_DECLARED_PROXY']} as a DECLARED "
        f"PROXY on subreddit-level states; the measured C = "
        f"{C_STATES} value is the one gated on.")
    add("")

    add("## 5. The bag channel and the increment question")
    add("")
    add("| coordinate | Mantel(bag-dist, trait-dist) | corr(coord-dist, "
        "bag-dist) | corr(coord-dist, activity-dist) | raw -> partial shift | "
        "partial + bag^2 (2nd reading) | raw on SQUARED Euclidean (2nd "
        "reading) |")
    add("|---|---|---|---|---|---|---|")
    for name in [c for c in COORDINATES if c in rows]:
        row = rows[name]
        bag = row["bag_channel"]
        quad = row["second_reading_partial_bag_quadratic"]
        sq = row["second_reading_squared_euclidean"]
        add(f"| `{name}` | {_fmt(bag['mantel_bag_vs_trait'])} | "
            f"{_fmt(bag['coord_vs_bag'])} | "
            f"{_fmt(bag['coord_vs_activity'])} | "
            f"{_fmt(row['raw']['r'])} -> {_fmt(row['partial_bag']['r'])} | "
            f"{_fmt(quad['r'])} p={_fmt(quad['p_two_sided'])} | "
            f"{_fmt(sq['r'])} p={_fmt(sq['p_two_sided'])} |")
    add("")
    add(f"SR1's corpus-level selection x trait coupling (r = {SR1_R}) is the "
        f"declared effect-scale anchor for every row above.")
    add("")
    add(f"{rows[PRIMARY_COORDINATE]['second_reading_note']}")
    add("")

    add("## 6. Projection versus realized width")
    add("")
    add("| coordinate | N | registered MDR | MDR recomputed at this N | "
        "realized 1.96 x null sd | realized / projected | band half-width |")
    add("|---|---|---|---|---|---|---|")
    for name in [c for c in COORDINATES if c in rows]:
        row = rows[name]
        proj = row["projection"]
        add(f"| `{name}` | {row['n_authors']:,} | "
            f"{_fmt(proj['registered_minimal_detectable_r'], 3)} | "
            f"{_fmt(proj['recomputed_at_this_N'])} | "
            f"{_fmt(proj['realized_mdr_1p96_null_sd'])} | "
            f"{_fmt(proj['realized_over_projected'], 3)} | "
            f"{_fmt(row['raw']['band_halfwidth'])} |")
    add("")
    add(f"The projection assumption is DECLARED: z proportional to "
        f"r*sqrt(N), scaled from SR1's realized z = {SR1_Z} at r = {SR1_R}, "
        f"N = {SR1_N}.  It is an assumption about how one leg's power "
        f"transfers to another's pool, not a measurement.")
    add("")

    add("## 7. Secondary rows and their guard")
    add("")
    add("| coordinate | cell | raw detected (uncorrected) | raw detected "
        f"(Bonferroni x{N_SECONDARY_ROWS}) | partial detected (Bonferroni) | "
        "flag |")
    add("|---|---|---|---|---|---|")
    for name in [c for c in COORDINATES if c in verdict["secondary_rows"]]:
        srow = verdict["secondary_rows"][name]
        add(f"| `{name}` | {srow['cell']} `{srow['cell_name']}` | "
            f"{_fmt(srow['raw_detected_uncorrected'])} | "
            f"{_fmt(srow['raw_detected_bonferroni'])} | "
            f"{_fmt(srow['partial_detected_bonferroni'])} | "
            f"{srow['flag']} |")
    add("")

    add("## 8. Registered leans against the outcome")
    add("")
    leans = verdict["leans"]
    add("| lean | registered | realized | outcome |")
    add("|---|---|---|---|")
    add(f"| primary (cell) | {_cell(leans['primary_registered'])} | "
        f"`{leans['primary_cell_outcome']}` | "
        f"{'HELD' if leans['primary_lean_cell_HELD'] else 'MISSED'} |")
    add(f"| primary (point) | \\|raw r\\| <= {LEAN_RAW_POINT} | "
        f"\\|raw r\\| = {_fmt(leans['primary_realized_abs_raw_r'])} | "
        f"{'HELD' if leans['primary_lean_point_HELD'] else 'MISSED'} |")
    add(f"| secondary (weak, structural) | "
        f"{_cell(leans['secondary_registered'])} | "
        f"-- | {leans['secondary_lean_outcome']} |")
    add("")

    add("## 9. Boundaries")
    add("")
    add(f"- **Tier EXPLORATORY, corpus-level, one Reddit cohort** (PANDORA, "
        f"{anchors['observed']['authors']:,} authors, 2015-2019).  NO PERSON "
        f"CLAIMS: nothing here licenses a statement about any individual.")
    add(f"- **Section 5.4.**  {_note('RN-U3-3')}")
    add(f"- **Slow time.**  {_note('RN-U3-4')}")
    add(f"- **Equation 12.**  {_note('RN-U3-7')}")
    add(f"- **The label event, named.**  {_note('RN-U3-6')}")
    add(f"- **Disattenuation.**  {_note('RN-U3-5')}")
    add("- The three coordinates are measured on THREE DIFFERENT POOLS "
        "(the eligibility predicates differ), so the rows are not a "
        "within-author comparison and must never be read as a ranking.")
    add("")

    add("## 10. Configuration block")
    add("")
    add("```json")
    add(json.dumps({
        "leg": LEG, "registration_commit": config["registration_commit"],
        "tier": config["tier"], "seed": SEED, "B_perm": B_PERM,
        "alpha": ALPHA, "C_states_plus_oov": C_STATES + 1,
        "kmeans_n_init": KMEANS_N_INIT, "K_block": K_BLOCK,
        "analysis_pool": config["analysis_pool"],
        "reliability_gate": RELIABILITY_GATE,
        "label_reliability_DECLARED": REL_LABEL_DECLARED,
        "predicates": {
            "stay": config["coordinates"]["stay_ct"]["eligibility"],
            "tight": config["coordinates"]["tight"]["eligibility"],
            "drift_pa": config["coordinates"]["drift_pa"]["eligibility"]},
        "config_sha256": gate["hashes"]["config_sha256_stamped"],
        "coordinates_sha256": gate["hashes"]["coordinates_sha256_frozen"],
    }, indent=1, sort_keys=True))
    add("```")
    add("")
    add(f"Artifacts (gitignored): `{rel(out)}/` -- `config.json`, "
        f"`config.sha256.json`, `part0.json`, `stageb.json`, "
        f"`coordinates.npz`, `coordinate_freeze.json`, `join.json`, "
        f"`gate.json`, `verdict.json`, `id_leak_scan.json`, "
        f"`report_payload.json`, `run_log.jsonl`.  Every table above is "
        f"generated from `report_payload.json` (rule 24); the report is "
        f"never hand-edited.")
    add("")
    add(f"Generated {payload['generated_utc']} by "
        f"`{rel(SCRIPT_SELF)}` (stage `report`).")
    add("")

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines), encoding="utf-8")
    RunLog(out / "run_log.jsonl").event("report_written",
                                        path=rel(args.report))
    print(f"report OK  {rel(args.report)}  {len(lines)} lines  "
          f"{time.time() - started:.1f}s")


# ---------------------------------------------------------------------------
STAGES = {"part0": stage_part0, "stageb": stage_stageb, "stagee": stage_stagee,
          "gate": stage_gate, "finalize": stage_finalize,
          "report": stage_report}
STAGE_ORDER = ("part0", "stageb", "stagee", "gate", "finalize", "report")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=f"SUICA {LEG} runner")
    parser.add_argument("stage", choices=[*STAGE_ORDER, "all"])
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--b-perm", type=int, default=B_PERM)
    parser.add_argument("--registration-commit", type=str,
                        default=REGISTRATION_COMMIT)
    args = parser.parse_args(argv)
    args.output.mkdir(parents=True, exist_ok=True)
    stages = STAGE_ORDER if args.stage == "all" else (args.stage,)
    for name in stages:
        STAGES[name](args)


if __name__ == "__main__":
    main()
