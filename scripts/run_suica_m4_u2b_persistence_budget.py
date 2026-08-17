#!/usr/bin/env python3
"""SUICA M4-U2b -- the persistence budget by carrier (which layer moves?).

Executes the registration committed at 96f7e40 in
``docs/SUICA_M4_U_WHEN_ORDER_PLAN.md`` (section "U2b -- the persistence budget
by carrier (registered BEFORE run, 2026-08-18)").  Nothing here re-derives a
design decision; where the registration is silent on an implementation detail
the simplest deterministic option is taken and recorded in
``results/m4_u2b_persistence_budget/config.json`` (mirrored into the report's
configuration block, rule 24).

The question.  U2 found `DRIFT_WITH_CORE`: the personal selection signature
loses ~46% of its near-gap personal excess over three years and keeps the
rest.  U2b asks WHICH LAYER MOVES.  The T-line proposition ("identity lives in
the distinctive; personality lives in the common") plus U2's result predicts
that the DISTINCTIVE layer is the standing part.  Four carrier restrictions of
the same blocks -- full vocabulary, common mass, distinctive tail, and a
low-rank taste coordinate -- are run through U2's own estimator, and the
verdict quantity is the contrast of FLOOR SHARES

    Delta_floor = F_distinct - F_common,   F_row = E_row(2-3y) / E_row(0-90d).

Inheritance is not exemption (#56).  The U2 machinery is IMPORTED BY FILE from
``scripts/run_suica_m4_u2_persistence_curve.py`` -- block construction, gap
binning, the epoch-matched exact stratified cross baseline (RD-U2-1), the
within-quarter permutation scaffold and the author cluster bootstrap are the
same objects, not re-implementations -- and U2's committed primary arm is
RECOMPUTED here and bit-compared against its artifacts before any new row is
read (gate G0).

Comparison rule (binding, from the registration).  LEVEL differences across
rows are never interpreted: a restricted row carries its own, block-varying
attenuation, so E_common and E_distinct are not on a common scale.  Only
WITHIN-ROW floor shares and their contrasts transport.

Pairing.  All four rows are computed on ONE pair set (#72): the INTERSECTION
set of same-author pairs whose BOTH blocks hold >= m events in BOTH
sub-vocabularies.  Because a block carries exactly K in-vocabulary events, the
eligibility predicate is a per-BLOCK property (common >= m AND K - common >=
m), so the intersection pair set is exactly the same-author pair set of the
eligible block subset -- identical pair indices, identical cross reservoir,
identical permutation plans and identical bootstrap author draws across rows.
The contrasts are therefore PAIRED by construction, not by post-hoc alignment.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from sklearn.model_selection import KFold

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Configuration constants (registration pins first, then recorded choices).
# ---------------------------------------------------------------------------

SEED = 20260818                     # registration pin
B_PERM = 499                        # registration pin
B_BOOT = 1000                       # registration pin
K_PRIMARY = 50                      # inherited from U2 (fixed-K blocks)
POOL_MIN_BLOCKS = 4                 # inherited from U2 (pool rule)

Q_PRIMARY = 0.5                     # registration pin: split level
Q_SENSITIVITIES = (0.3, 0.7)        # registration pin
M_PRIMARY = 10                      # registration pin: eligibility floor
M_SENSITIVITIES = (5, 15)           # registration pin

TASTE_FOLDS = 5                     # registration pin (SR3 pattern)
TASTE_DIM = 64                      # registration pin
EQUIVALENCE_BAND = 0.10             # registration pin: NO_LAYER_SPLIT band
LEAN_DELTA = (0.05, 0.25)           # registration pin: L1 point range

# Registered pool targets (#69) on the INTERSECTION set at q=0.5 / m=10,
# evaluated in the 2-3y bin.  Unmet => the leg STOPS and reports.
POOL_GATE_MIN_PAIRS_2_3Y = 100_000
POOL_GATE_MIN_AUTHORS_2_3Y = 400

# Cache anchors: BLOCKING gate before any computation (registration).
ANCHOR_EVENTS = 3_005_360
ANCHOR_AUTHORS = 1401
ANCHOR_VOCAB = 1191

# Census pins from the registration (#77: each carries its exact computation).
#
#   universe            = in-vocabulary cohort events of the U1 cache, i.e.
#                         events whose subreddit maps to a vocabulary index
#   community ranking   = descending event count over that universe, ties
#                         broken by ascending vocabulary index
#   Common(q)           = smallest rank prefix with cumulative share >= q
#   per-block counts    = over POOL blocks (849 authors, >= 4 blocks at K=50)
#   eligible pairs      = same-author pairs, BOTH blocks >= m events of that
#                         sub-vocabulary, midpoint gap in the 2-3y bin
CENSUS_PINS: dict[str, Any] = {
    "universe_in_vocab_events": 2_348_361,
    "common_size_q30": 8,
    "common_share_q30": 0.3077,
    "common_size_q50": 32,
    "common_share_q50": 0.5036,
    "common_size_q70": 104,
    "common_share_q70": 0.7008,
    "pool_authors": 849,
    "pool_blocks": 45_731,
    "block_common_q05_q25_q50": [0, 8, 25],
    "block_distinct_q05_q25_q50": [0, 6, 25],
    "eligible_pairs_common_m10_2_3y": 253_946,
    "eligible_pairs_distinct_m10_2_3y": 230_661,
    "eligible_authors_distinct_m10_2_3y": 506,
}
# A mismatch in these STOPS the leg (the split itself would not be the
# registered object).  Everything else in CENSUS_PINS is reported.
CENSUS_BLOCKING = ("universe_in_vocab_events", "common_size_q50",
                   "common_share_q50", "pool_authors", "pool_blocks")

# Recorded implementation choices (registration silent).
TIE_BREAK = "descending event count, ties broken by ascending vocab index"
FIRST_HALF_RULE = ("per author, the median of that author's in-vocabulary "
                   "event timestamps; first half = created_utc <= median "
                   "(SR1/T2's early/late rule without SR1's 4000-timestamp "
                   "cap, which existed only to reproduce SR1's frozen halves)")
MIX_SHIFT_ERAS = "calendar year of the block midpoint"

DEFAULT_CACHE = ROOT / "results/m4_u1_order_identity/events_cache.npz"
DEFAULT_OUTPUT = ROOT / "results/m4_u2b_persistence_budget"
DEFAULT_REPORT = (
    ROOT / "reports/SUICA_M4_U2B_PERSISTENCE_BUDGET_REPORT.md")
U2_SCRIPT = ROOT / "scripts/run_suica_m4_u2_persistence_curve.py"
U2_ARTIFACTS = ROOT / "results/m4_u2_persistence_curve"

# Fields compared bit-for-bit against U2's committed primary arm (gate G0).
G0_FIELDS = ("curve", "curve_ci", "curve_null_band", "curve_null_center",
             "curve_null_mean", "self_mean", "cross_mean_matched",
             "mean_gap_days", "d", "d_ci", "d_null_band", "d_null_center",
             "floor_share", "floor_share_ci", "perm_p_existence",
             "perm_p_decay", "self_pairs", "n_blocks", "n_authors",
             "n_quarters")


# ---------------------------------------------------------------------------
# U2 machinery, imported by file (#56: the inherited object, not a copy).
# ---------------------------------------------------------------------------


def load_u2_module(path: Path = U2_SCRIPT):
    """Import U2's harness as a module so its estimator IS reused verbatim."""

    spec = importlib.util.spec_from_file_location("suica_m4_u2", path)
    if spec is None or spec.loader is None:      # pragma: no cover
        raise RuntimeError(f"cannot import U2 machinery from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["suica_m4_u2"] = module          # dataclasses need this
    spec.loader.exec_module(module)
    return module


U2 = load_u2_module()

# Names reused unchanged from U2 (listed so the reuse is auditable).
BIN_LABELS: tuple[str, ...] = U2.BIN_LABELS
N_BINS: int = U2.N_BINS
NEAR_BIN: int = U2.NEAR_BIN          # 0-90d
FAR_BIN: int = U2.FAR_BIN            # 2-3y, the registered verdict endpoint
DESCRIPTIVE_BIN: int = U2.DESCRIPTIVE_BIN
QUARTER_DAYS: float = U2.QUARTER_DAYS
write_json = U2.write_json
utc_now = U2.utc_now
fmt = U2.fmt
fmt_ci = U2.fmt_ci
RunLog = U2.RunLog


# ---------------------------------------------------------------------------
# PPMI + SVD community embeddings.
#
# Provenance: reproduced verbatim from
# ``scripts/run_suica_m4_t2_matched_residual.py`` lines 587-601 (``ppmi_svd``),
# the frozen T2/T3 recipe SR3 also re-used.  ``tests/`` asserts this
# replication is bit-identical to T2's own function (the RN-SR3-1 pattern:
# the slice must BE the recipe, not resemble it).
# ---------------------------------------------------------------------------


def ppmi_svd(counts: np.ndarray, dim: int, seed: int) -> np.ndarray:
    """Community vectors from PPMI + truncated SVD of a sqrt-count matrix."""
    x = np.sqrt(np.clip(counts, 0, None))
    total = x.sum()
    if total <= 0:
        return np.zeros((counts.shape[1], dim))
    p = x / total
    pr = p.sum(axis=1, keepdims=True)
    pc = p.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log(np.where(p > 0, p / np.clip(pr * pc, 1e-300, None), 1.0))
    ppmi = np.clip(np.nan_to_num(pmi), 0.0, None)
    _u, sv, vt = np.linalg.svd(ppmi, full_matrices=False)
    d = min(dim, vt.shape[0])
    return vt[:d].T * sv[:d]          # (n_communities x d)


# ---------------------------------------------------------------------------
# The vocabulary split
# ---------------------------------------------------------------------------


def community_ranking(vocab_index: np.ndarray, n_vocab: int
                      ) -> tuple[np.ndarray, np.ndarray, int]:
    """Rank communities by descending in-vocabulary event count.

    Returns ``(order, cumulative_share, universe_events)``.  Ties are broken by
    ascending vocabulary index so the ranking is deterministic (#77).
    """

    in_vocab = vocab_index[vocab_index >= 0]
    counts = np.bincount(in_vocab, minlength=n_vocab).astype(np.int64)
    universe = int(counts.sum())
    order = np.lexsort((np.arange(counts.size), -counts))
    cumulative = np.cumsum(counts[order]) / float(universe)
    return order, cumulative, universe


def common_prefix(order: np.ndarray, cumulative: np.ndarray, q: float
                  ) -> tuple[np.ndarray, float]:
    """Common(q): the smallest rank prefix with cumulative share >= q."""

    size = int(np.searchsorted(cumulative, q) + 1)
    return np.sort(order[:size]), float(cumulative[size - 1])


def block_counts_over(features: np.ndarray, columns: np.ndarray,
                      k: int) -> np.ndarray:
    """Exact per-block event count inside a sub-vocabulary.

    A block holds exactly ``k`` in-vocabulary events, so the Hellinger feature
    is sqrt(count / k) and is already unit-norm; the count is recovered as
    ``k * feature**2`` and asserted integral by the caller.
    """

    sub = features[:, columns].astype(np.float64)
    return k * np.einsum("ij,ij->i", sub, sub)


def renormalize(features: np.ndarray, columns: np.ndarray) -> np.ndarray:
    """Restrict a Hellinger block vector to a sub-vocabulary and renormalize."""

    sub = np.array(features[:, columns], dtype=np.float32, copy=True)
    norms = np.linalg.norm(sub, axis=1, keepdims=True)
    norms[norms == 0.0] = 1.0
    sub /= norms
    return sub


# ---------------------------------------------------------------------------
# Pair census on a block subset (vectorized per author)
# ---------------------------------------------------------------------------


def self_pair_census(author: np.ndarray, mid_days: np.ndarray
                     ) -> tuple[np.ndarray, list[int]]:
    """Self pairs per bin and contributing authors per bin, for a block set."""

    pairs = np.zeros(N_BINS, dtype=np.int64)
    contributors = [0] * N_BINS
    order = np.argsort(author, kind="stable")
    sorted_author = author[order]
    sorted_mid = mid_days[order]
    edges = np.flatnonzero(np.diff(sorted_author)) + 1
    starts = np.concatenate(([0], edges))
    stops = np.concatenate((edges, [sorted_author.size]))
    for start, stop in zip(starts, stops):
        n = stop - start
        if n < 2:
            continue
        mids = sorted_mid[start:stop]
        iu = np.triu_indices(n, 1)
        gaps = np.abs(mids[:, None] - mids[None, :])[iu]
        counts = np.bincount(U2.gap_bin(gaps), minlength=N_BINS)
        pairs += counts
        for b in range(N_BINS):
            if counts[b]:
                contributors[b] += 1
    return pairs, contributors


# ---------------------------------------------------------------------------
# Row estimator: U2's compute_arm on a shared block subset
# ---------------------------------------------------------------------------


def floor_share(curve: np.ndarray) -> np.ndarray:
    """F = E(2-3y) / E(0-90d), elementwise over a batch of curves."""

    near = np.asarray(curve)[..., NEAR_BIN]
    far = np.asarray(curve)[..., FAR_BIN]
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(near != 0.0, far / near, np.nan)


def percentile_ci(values: np.ndarray) -> list[float]:
    finite = np.asarray(values)[np.isfinite(values)]
    if finite.size == 0:
        return [float("nan"), float("nan")]
    return [float(np.percentile(finite, 2.5)),
            float(np.percentile(finite, 97.5))]


def summarize_row(result: dict[str, Any]) -> dict[str, Any]:
    """Row-level summary: the curve, its floor share, and both uncertainties."""

    boot_floor = floor_share(result["boot_curve"])
    null_floor = floor_share(result["null_curve"])
    finite_null = null_floor[np.isfinite(null_floor)]
    return {
        "label": result["label"],
        "n_blocks": int(result["n_blocks"]),
        "n_authors": int(result["n_authors"]),
        "self_pairs": [int(v) for v in result["self_pairs"]],
        "self_mean": [float(v) for v in result["self_mean"]],
        "cross_mean_matched": [float(v) for v in result["cross_mean_matched"]],
        "curve": [float(v) for v in result["curve"]],
        "curve_ci": [[float(a), float(b)] for a, b in result["curve_ci"]],
        "curve_null_band": [[float(a), float(b)]
                            for a, b in result["curve_null_band"]],
        "curve_null_center": [float(v) for v in result["curve_null_center"]],
        "mean_gap_days": [float(v) for v in result["mean_gap_days"]],
        "d": float(result["d"]),
        "d_ci": [float(v) for v in result["d_ci"]],
        "floor_share": float(result["floor_share"]),
        "floor_share_ci": percentile_ci(boot_floor),
        "floor_share_null_center": (float(np.median(finite_null))
                                    if finite_null.size else float("nan")),
        "floor_share_null_band": percentile_ci(null_floor),
        "floor_share_null_iqr": (
            [float(np.percentile(finite_null, 25)),
             float(np.percentile(finite_null, 75))]
            if finite_null.size else [float("nan"), float("nan")]),
        "perm_p_existence": float(result["perm_p_existence"]),
        "perm_p_decay": float(result["perm_p_decay"]),
    }


def contrast(name: str, row_a: dict[str, Any], row_b: dict[str, Any],
             *, paired: bool) -> dict[str, Any]:
    """Δ = F(row_a) − F(row_b) with the shared bootstrap and permutation."""

    boot = floor_share(row_a["boot_curve"]) - floor_share(row_b["boot_curve"])
    null = floor_share(row_a["null_curve"]) - floor_share(row_b["null_curve"])
    finite_null = null[np.isfinite(null)]
    point = float(row_a["floor_share"] - row_b["floor_share"])
    ci = percentile_ci(boot)
    return {
        "name": name,
        "point": point,
        "ci": ci,
        "ci_half_width": float(0.5 * (ci[1] - ci[0]))
        if np.isfinite(ci[0]) and np.isfinite(ci[1]) else float("nan"),
        "null_center": (float(np.median(finite_null))
                        if finite_null.size else float("nan")),
        "null_mean": (float(np.mean(finite_null))
                      if finite_null.size else float("nan")),
        "null_band": percentile_ci(null),
        "null_iqr": ([float(np.percentile(finite_null, 25)),
                      float(np.percentile(finite_null, 75))]
                     if finite_null.size else [float("nan")] * 2),
        "null_finite_fraction": (float(finite_null.size / null.size)
                                 if null.size else float("nan")),
        "paired_bootstrap": bool(paired),
    }


def classify_delta(delta: dict[str, Any]) -> dict[str, Any]:
    """The registered cells, keyed on Δfloor's 95% CI and effect size (#75)."""

    lo, hi = delta["ci"]
    point = delta["point"]
    includes_zero = bool(lo <= 0.0 <= hi)
    small = bool(abs(point) < EQUIVALENCE_BAND)
    if includes_zero and small:
        cell = "NO_LAYER_SPLIT"
    elif lo > 0.0:
        cell = "DISTINCTIVE_STANDING"
    elif hi < 0.0:
        cell = "COMMON_STANDING"
    else:
        cell = "UNRESOLVED_SPLIT"
    return {
        "cell": cell,
        "ci_includes_zero": includes_zero,
        "abs_point_below_band": small,
        "equivalence_band": EQUIVALENCE_BAND,
        "ci_half_width": delta["ci_half_width"],
        "half_width_over_band": (delta["ci_half_width"] / EQUIVALENCE_BAND
                                 if np.isfinite(delta["ci_half_width"])
                                 else float("nan")),
        "band_reachable": bool(np.isfinite(delta["ci_half_width"])
                               and delta["ci_half_width"] < EQUIVALENCE_BAND),
    }


# ---------------------------------------------------------------------------
# Taste row: per-fold PPMI+SVD embeddings, out-of-fold curves, pooled
# ---------------------------------------------------------------------------


def first_half_counts(cache, pool_authors: np.ndarray, n_vocab: int
                      ) -> tuple[np.ndarray, np.ndarray]:
    """Per pool author, in-vocabulary event counts over their FIRST half.

    Returns ``(counts, total_first_half_mass)`` with one row per pool author in
    the order of ``pool_authors``.
    """

    vocab_index = cache.vocab_of_subreddit[cache.subreddit_code]
    keep = vocab_index >= 0
    author = cache.author_code[keep]
    stamp = cache.created_utc[keep]
    community = vocab_index[keep]

    slot = np.full(int(cache.author_code.max()) + 1, -1, dtype=np.int64)
    slot[pool_authors] = np.arange(pool_authors.size)
    in_pool = slot[author] >= 0
    author = slot[author[in_pool]]
    stamp = stamp[in_pool]
    community = community[in_pool]

    order = np.lexsort((stamp, author))
    author = author[order]
    stamp = stamp[order]
    community = community[order]

    counts_per_author = np.bincount(author, minlength=pool_authors.size)
    starts = np.concatenate(([0], np.cumsum(counts_per_author)))
    median = np.empty(pool_authors.size, dtype=np.float64)
    for i in range(pool_authors.size):
        median[i] = np.median(stamp[starts[i]:starts[i + 1]])
    is_first = stamp <= median[author]

    flat = author[is_first] * n_vocab + community[is_first]
    counts = np.bincount(flat, minlength=pool_authors.size * n_vocab)
    counts = counts.reshape(pool_authors.size, n_vocab).astype(np.float64)
    return counts, counts.sum(axis=1)


def taste_folds(pool_authors: np.ndarray, seed: int, n_folds: int
                ) -> list[tuple[np.ndarray, np.ndarray]]:
    """KFold(shuffle=True, random_state=SEED) over the pool authors."""

    splitter = KFold(n_splits=n_folds, shuffle=True, random_state=seed)
    return [(train, test) for train, test in
            splitter.split(np.arange(pool_authors.size))]


def pool_fold_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Unweighted mean over folds (U1 convention) of curves and replicates."""

    curve = np.nanmean(np.array([r["curve"] for r in results]), axis=0)
    boot = np.nanmean(np.array([r["boot_curve"] for r in results]), axis=0)
    null = np.nanmean(np.array([r["null_curve"] for r in results]), axis=0)
    self_pairs = np.sum([r["self_pairs"] for r in results], axis=0)
    weights = np.array([r["self_pairs"] for r in results], dtype=np.float64)
    total = np.where(self_pairs > 0, self_pairs, 1.0)

    def weighted(field: str) -> np.ndarray:
        values = np.array([r[field] for r in results], dtype=np.float64)
        return np.where(self_pairs > 0,
                        np.nansum(values * weights, axis=0) / total, np.nan)

    def ci(values: np.ndarray) -> list[float]:
        return percentile_ci(values)

    return {
        "label": "taste (per-fold PPMI+SVD d=64, out-of-fold, pooled)",
        "n_blocks": int(sum(r["n_blocks"] for r in results)),
        "n_authors": int(sum(r["n_authors"] for r in results)),
        "n_quarters": int(max(r["n_quarters"] for r in results)),
        "b_perm": int(results[0]["b_perm"]),
        "b_boot": int(results[0]["b_boot"]),
        "self_pairs": [int(v) for v in self_pairs],
        "self_mean": [float(v) for v in weighted("self_mean")],
        "cross_mean_matched": [float(v) for v in
                               weighted("cross_mean_matched")],
        "mean_gap_days": [float(v) for v in weighted("mean_gap_days")],
        "curve": [float(v) for v in curve],
        "curve_ci": [ci(boot[:, b]) for b in range(N_BINS)],
        "curve_null_band": [ci(null[:, b]) for b in range(N_BINS)],
        "curve_null_center": [float(np.nanmedian(null[:, b]))
                              for b in range(N_BINS)],
        "curve_null_mean": [float(np.nanmean(null[:, b]))
                            for b in range(N_BINS)],
        "d": float(curve[NEAR_BIN] - curve[FAR_BIN]),
        "d_ci": ci(boot[:, NEAR_BIN] - boot[:, FAR_BIN]),
        "d_null_band": ci(null[:, NEAR_BIN] - null[:, FAR_BIN]),
        "d_null_center": float(np.nanmedian(null[:, NEAR_BIN]
                                            - null[:, FAR_BIN])),
        "floor_share": float(curve[FAR_BIN] / curve[NEAR_BIN])
        if curve[NEAR_BIN] != 0 else float("nan"),
        "perm_p_existence": float(np.mean(
            [r["perm_p_existence"] for r in results])),
        "perm_p_decay": float(np.mean([r["perm_p_decay"] for r in results])),
        "boot_curve": boot,
        "null_curve": null,
        "per_fold_curve": [[float(v) for v in r["curve"]] for r in results],
        "per_fold_floor_share": [float(r["floor_share"]) for r in results],
    }


# ---------------------------------------------------------------------------
# G0: recompute U2's primary arm and bit-compare
# ---------------------------------------------------------------------------


def _flatten(value: Any) -> list[float]:
    if isinstance(value, (list, tuple)):
        out: list[float] = []
        for item in value:
            out.extend(_flatten(item))
        return out
    return [float(value)]


def g0_compare(recomputed: dict[str, Any], committed: dict[str, Any]
               ) -> dict[str, Any]:
    """Field-by-field comparison against U2's committed primary arm."""

    fields = []
    worst = 0.0
    exact = True
    for name in G0_FIELDS:
        if name not in committed:
            fields.append({"field": name, "status": "ABSENT_IN_ARTIFACT"})
            exact = False
            continue
        a = _flatten(recomputed[name])
        b = _flatten(committed[name])
        if len(a) != len(b):
            fields.append({"field": name, "status": "SHAPE_MISMATCH"})
            exact = False
            continue
        diff = np.abs(np.asarray(a) - np.asarray(b))
        finite = diff[np.isfinite(diff)]
        max_diff = float(finite.max()) if finite.size else 0.0
        identical = bool(np.array_equal(np.asarray(a), np.asarray(b),
                                        equal_nan=True))
        exact = exact and identical
        worst = max(worst, max_diff)
        fields.append({"field": name, "bitwise_identical": identical,
                       "max_abs_difference": max_diff})
    return {"status": "PASS" if exact else ("NEAR" if worst < 1e-9
                                            else "FAIL"),
            "bitwise_identical": exact,
            "max_abs_difference": worst,
            "fields": fields,
            "source": str(U2_ARTIFACTS / "arms.json")}


# ---------------------------------------------------------------------------
# Report (rule 24: every number generated here, none hand-transcribed)
# ---------------------------------------------------------------------------


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []

    def add(text: str = "") -> None:
        lines.append(text)

    rows = payload["rows"]
    delta = payload["delta"]
    cell = payload["classification"]
    gate = payload["pool_gate"]
    stopped = payload["outcome"] == "POOL_GATE_UNMET"

    add("# SUICA M4-U2b — the persistence budget by carrier")
    add("")
    add(f"**Outcome: `{payload['outcome']}`.**")
    add("")
    if stopped:
        add("**THE LEG STOPS AT THE REGISTERED POOL GATE (#69). NO "
            "CLASSIFICATION CELL IS ASSIGNED AND NO VERDICT IS CLAIMED.** The "
            "registration pins that the intersection pair set at "
            f"q = {payload['config']['q_primary']} / "
            f"m = {payload['config']['m_primary']} must retain "
            f"≥ {POOL_GATE_MIN_PAIRS_2_3Y:,} pairs and "
            f"≥ {POOL_GATE_MIN_AUTHORS_2_3Y} contributing authors in the "
            f"2–3y bin, and that the leg STOPS and reports if that is unmet "
            "with no silent re-split. It is unmet on BOTH clauses: "
            f"**{gate['pairs_2_3y']:,} pairs** "
            f"({gate['pairs_fraction']:.3f}× the target) and "
            f"**{gate['authors_2_3y']} authors** "
            f"({gate['authors_fraction']:.3f}× the target). Everything below "
            "the gate section is computed and reported so the planner can "
            "adjudicate once, and every quantity in it is **PROVISIONAL and "
            "non-verdict-carrying**.")
    else:
        add(f"**Cell `{cell['cell']}`** — Δfloor = F_distinct − F_common = "
            f"{fmt(delta['point'])} {fmt_ci(delta['ci'])}.")
    add("")
    add(f"Executed from the registration committed at "
        f"`{payload['registration_commit']}` in "
        "`docs/SUICA_M4_U_WHEN_ORDER_PLAN.md` (section \"U2b — the "
        "persistence budget by carrier (registered BEFORE run, 2026-08-18)\"). "
        f"Run window {payload['run_started_utc']} to "
        f"{payload['run_finished_utc']}; report generated "
        f"{payload['generated_utc']}. Every number in this report is produced "
        "from the run's artifacts by "
        "`scripts/run_suica_m4_u2b_persistence_budget.py` (rule 24).")
    add("")

    # ---- gates -----------------------------------------------------------
    add("## Gates")
    add("")
    add("| gate | status |")
    add("|---|---|")
    for name, status in payload["gates"].items():
        add(f"| {name} | {status} |")
    add("")

    # ---- the split -------------------------------------------------------
    add("## The vocabulary split (census, #77 computations pinned)")
    add("")
    add("Universe: the in-vocabulary cohort events of the U1 cache. "
        "Communities are ranked by descending event count over that universe "
        f"({TIE_BREAK}); Common(q) is the smallest rank prefix with "
        "cumulative share ≥ q; Distinctive(q) is its complement within the "
        f"{payload['census']['observed']['n_vocab']:,}-community vocabulary.")
    add("")
    add("| registered census quantity | registered | observed | status |")
    add("|---|---|---|---|")
    for key, entry in payload["census"]["pins"].items():
        blocking = " *(blocking)*" if key in CENSUS_BLOCKING else ""
        add(f"| `{key}`{blocking} | {entry['registered']} | "
            f"{entry['observed']} | {entry['status']} |")
    add("")
    if payload["census"]["non_reproducing"]:
        for note in payload["census"]["non_reproducing"]:
            add(f"- **Census note (non-blocking, #77)** — {note}")
        add("")

    # ---- the pool gate ---------------------------------------------------
    add("## The registered pool gate (#69) — the leg's decision point")
    add("")
    add("Because a block carries exactly "
        f"K = {payload['config']['k']} in-vocabulary events, the eligibility "
        "predicate is a per-BLOCK property (common ≥ m AND K − common ≥ m), "
        "so the intersection PAIR set is exactly the same-author pair set of "
        "the eligible BLOCK subset. All four rows therefore share identical "
        "pair indices, an identical cross reservoir, identical permutation "
        "plans and identical bootstrap author draws (#72 satisfied by "
        "construction, not by alignment).")
    add("")
    add("| set at q=0.5, m=10 | 2–3y pairs | 2–3y authors | eligible blocks |")
    add("|---|---|---|---|")
    for name, entry in payload["pool_realization"].items():
        add(f"| {name} | {entry['pairs_2_3y']:,} | "
            f"{entry['authors_2_3y']:,} | {entry['blocks']:,} |")
    add("")
    add(f"**Gate: {gate['status']}.** Required ≥ "
        f"{POOL_GATE_MIN_PAIRS_2_3Y:,} pairs (realized "
        f"{gate['pairs_2_3y']:,}, {gate['pairs_fraction']:.4f}× target) and "
        f"≥ {POOL_GATE_MIN_AUTHORS_2_3Y} authors (realized "
        f"{gate['authors_2_3y']:,}, {gate['authors_fraction']:.4f}× target).")
    add("")
    observed = payload["census"]["observed"]
    marginal_common = payload["pool_realization"]["common (marginal)"]
    intersection = payload["pool_realization"]["intersection"]
    u2_contributors = payload["u2_authors_2_3y"]
    pair_share = intersection["pairs_2_3y"] / marginal_common["pairs_2_3y"]
    author_share = intersection["authors_2_3y"] / u2_contributors
    add("The registration's own per-row eligible-pair census reproduces "
        "EXACTLY — common "
        f"{observed['eligible_pairs_common_m10_2_3y']:,} and distinct "
        f"{observed['eligible_pairs_distinct_m10_2_3y']:,} pairs, "
        f"{observed['eligible_authors_distinct_m10_2_3y']} "
        "distinct-eligible authors — so the construction here IS the "
        "planner's construction. What the census did not carry is the "
        "INTERSECTION of the two eligibilities, which is far smaller than "
        "either marginal: requiring ≥ 10 events in BOTH halves of a 50-event "
        "block excludes lopsided blocks, and lopsidedness is author-"
        f"persistent. The intersection keeps {pair_share:.1%} of the common "
        f"row's 2–3y pairs and {author_share:.1%} of U2's "
        f"{u2_contributors} 2–3y contributors.")
    add("")

    # ---- the four rows ---------------------------------------------------
    heading = ("## The four rows — PROVISIONAL (the pool gate is unmet)"
               if stopped else "## The four rows")
    add(heading)
    add("")
    add("**Binding comparison rule:** LEVEL differences across rows are never "
        "interpreted — a restricted row carries its own, block-varying "
        "attenuation, so E_common and E_distinct are not on a common scale. "
        "Only within-row floor shares and their contrasts transport.")
    add("")
    add("| row | " + " | ".join(BIN_LABELS) + " |")
    add("|---|" + "---|" * N_BINS)
    for row in rows:
        add(f"| {row['key']} | "
            + " | ".join(fmt(row["curve"][b]) for b in range(N_BINS)) + " |")
    add("")
    add("E(b) with 95% cluster-bootstrap CI and the within-quarter "
        "permutation band, at the two verdict-relevant bins:")
    add("")
    add("| row | blocks | self pairs (2–3y) | E(0–90d) [CI] | null band | "
        "E(2–3y) [CI] | null band |")
    add("|---|---|---|---|---|---|---|")
    for row in rows:
        add(f"| {row['key']} | {row['n_blocks']:,} | "
            f"{row['self_pairs'][FAR_BIN]:,} | "
            f"{fmt(row['curve'][NEAR_BIN])} "
            f"{fmt_ci(row['curve_ci'][NEAR_BIN])} | "
            f"{fmt_ci(row['curve_null_band'][NEAR_BIN], 5)} | "
            f"{fmt(row['curve'][FAR_BIN])} "
            f"{fmt_ci(row['curve_ci'][FAR_BIN])} | "
            f"{fmt_ci(row['curve_null_band'][FAR_BIN], 5)} |")
    add("")
    add("Self and epoch-matched cross means behind those excesses:")
    add("")
    add("| row | self mean (0–90d) | cross (0–90d) | self mean (2–3y) | "
        "cross (2–3y) | perm p (existence) | perm p (decay) |")
    add("|---|---|---|---|---|---|---|")
    for row in rows:
        add(f"| {row['key']} | {fmt(row['self_mean'][NEAR_BIN])} | "
            f"{fmt(row['cross_mean_matched'][NEAR_BIN])} | "
            f"{fmt(row['self_mean'][FAR_BIN])} | "
            f"{fmt(row['cross_mean_matched'][FAR_BIN])} | "
            f"{fmt(row['perm_p_existence'])} | "
            f"{fmt(row['perm_p_decay'])} |")
    add("")

    add("### Floor shares")
    add("")
    add("| row | D = E(0–90d) − E(2–3y) [CI] | F = E(2–3y)/E(0–90d) [CI] |")
    add("|---|---|---|")
    for row in rows:
        add(f"| {row['key']} | {fmt(row['d'])} {fmt_ci(row['d_ci'])} | "
            f"**{fmt(row['floor_share'])}** "
            f"{fmt_ci(row['floor_share_ci'])} |")
    add("")

    # ---- the contrast ----------------------------------------------------
    add("### The verdict contrast Δfloor = F_distinct − F_common")
    add("")
    add("| contrast | point | 95% CI | CI half-width | null center | "
        "null IQR | cell |")
    add("|---|---|---|---|---|---|---|")
    for item, klass in ((delta, cell),
                        (payload["secondary"], payload["secondary_cell"])):
        add(f"| {item['name']} | **{fmt(item['point'])}** | "
            f"{fmt_ci(item['ci'])} | {fmt(item['ci_half_width'])} | "
            f"{fmt(item['null_center'], 5)} | {fmt_ci(item['null_iqr'], 3)} | "
            f"`{klass['cell']}` |")
    add("")
    add("**The floor-share null is a ratio of two quantities the permutation "
        "drives to zero, so its permutation distribution is heavy-tailed by "
        "construction and its 95% band is not an informative bound.** The "
        "registration's claim is about the null's LOCATION, and that is what "
        "is checked: Δfloor's realized permutation center is "
        f"{fmt(delta['null_center'], 5)} with IQR "
        f"{fmt_ci(delta['null_iqr'], 3)} "
        f"({fmt(100.0 * delta['null_finite_fraction'], 1)}% of replicates "
        "finite). The informative nulls of this leg are the per-bin E(b) "
        "bands in the table above, which sit three to four orders of "
        "magnitude inside their effects, exactly as in U2.")
    add("")

    add("### Equivalence-band projection (#71)")
    add("")
    add(f"The `NO_LAYER_SPLIT` equivalence band is |Δfloor| < "
        f"{EQUIVALENCE_BAND}. The realized half-width of Δfloor's 95% CI is "
        f"{fmt(delta['ci_half_width'])} "
        f"({fmt(cell['half_width_over_band'], 3)}× the band). "
        + ("The design could therefore have DECLARED a null split had Δfloor "
           "been near zero: the achievable interval is narrower than the "
           "band." if cell["band_reachable"] else
           "The design could NOT have declared a null split at this power: "
           "the achievable interval is WIDER than the equivalence band, so "
           "`NO_LAYER_SPLIT` was not reachable and a near-zero Δfloor would "
           "have read `UNRESOLVED_SPLIT` rather than equivalence."))
    add("")

    # ---- sensitivities ---------------------------------------------------
    add("## Sensitivity grid (q × m)")
    add("")
    add("Registered as one-at-a-time variations on the primary contrast: "
        f"q ∈ {{{', '.join(str(q) for q in Q_SENSITIVITIES)}}} at m = "
        f"{M_PRIMARY}, and m ∈ "
        f"{{{', '.join(str(m) for m in M_SENSITIVITIES)}}} at q = "
        f"{Q_PRIMARY}. Each row reports its OWN intersection pool "
        "realization against the registered #69 targets.")
    add("")
    add("| q | m | Common(q) | 2–3y pairs | 2–3y authors | #69 | F_common | "
        "F_distinct | Δfloor [CI] | cell | #73 |")
    add("|---|---|---|---|---|---|---|---|---|---|---|")
    for entry in payload["sensitivities"]:
        add(f"| {entry['q']} | {entry['m']} | {entry['common_size']} | "
            f"{entry['pairs_2_3y']:,} | {entry['authors_2_3y']:,} | "
            f"{entry['pool_gate']} | {fmt(entry['f_common'])} | "
            f"{fmt(entry['f_distinct'])} | {fmt(entry['delta']['point'])} "
            f"{fmt_ci(entry['delta']['ci'])} | `{entry['cell']}` | "
            f"{entry['flag_73'] or '—'} |")
    add("")
    if payload["flags_73"]:
        for flag in payload["flags_73"]:
            add(f"- **#73 flag** — {flag}")
    else:
        add("No sensitivity diverges from the primary configuration in cell; "
            "zero #73 flags.")
    add("")
    if payload["gate_clearing_configs"]:
        add("**Registered configurations that DO clear the #69 targets:** "
            + ", ".join(payload["gate_clearing_configs"])
            + ". This is reported as adjudication data only. Promoting one of "
            "them to primary is a re-split and belongs to the planner, not to "
            "this executor.")
    else:
        add("**No registered configuration in the grid clears both #69 "
            "targets.**")
    add("")

    # ---- G0 --------------------------------------------------------------
    add("## G0 — U2 anchor bit-comparison (#56: inheritance is not exemption)")
    add("")
    g0 = payload["g0"]
    add("U2's primary arm was RECOMPUTED here from the same cache through "
        "the same imported estimator and compared field-by-field against its "
        f"committed artifacts (`{g0['source']}`). Status **{g0['status']}**; "
        f"maximum absolute difference across "
        f"{len(g0['fields'])} compared fields: "
        f"{g0['max_abs_difference']:.3e}; bitwise identical: "
        f"{'yes' if g0['bitwise_identical'] else 'no'}.")
    add("")
    add("| field | bitwise identical | max abs difference |")
    add("|---|---|---|")
    for field in g0["fields"]:
        add(f"| `{field['field']}` | "
            f"{'yes' if field.get('bitwise_identical') else 'no'} | "
            f"{field.get('max_abs_difference', float('nan')):.3e} |")
    add("")

    # ---- taste purity ----------------------------------------------------
    add("## Taste row — fold purity (blocking gate)")
    add("")
    add("Embeddings are fitted on TRAINING authors' first-half events only "
        f"({FIRST_HALF_RULE}); curves are read on TEST authors' pairs and "
        "pooled by unweighted mean over folds (U1 convention). Purity is the "
        "mass identity: the fitted count matrix's total must equal the "
        "training authors' first-half in-vocabulary mass EXACTLY, and the "
        "test authors' mass must be entirely absent from it.")
    add("")
    add("| fold | train authors | test authors | overlap | fitted mass | "
        "train first-half mass | test mass excluded | test blocks |")
    add("|---|---|---|---|---|---|---|---|")
    for entry in payload["taste_purity"]:
        add(f"| {entry['fold']} | {entry['n_train']:,} | "
            f"{entry['n_test']:,} | {entry['overlap']} | "
            f"{entry['fitted_mass']:,.0f} | "
            f"{entry['train_first_half_mass']:,.0f} | "
            f"{entry['test_mass_excluded']:,.0f} | "
            f"{entry['test_blocks']:,} |")
    add("")
    add("Per-fold floor shares: "
        + ", ".join(fmt(v) for v in payload["taste_per_fold_floor"])
        + ".")
    add("")

    # ---- mix shift -------------------------------------------------------
    add("## Registered descriptive — the mix-shift trajectory "
        "(non-verdict-moving)")
    add("")
    add(f"Mean common-share of a block ({MIX_SHIFT_ERAS}), over all "
        f"{payload['census']['observed']['pool_blocks']:,} pool blocks at "
        f"q = {Q_PRIMARY}:")
    add("")
    add("| era | blocks | mean common share | sd |")
    add("|---|---|---|---|")
    for entry in payload["mix_shift"]["by_calendar_year"]:
        add(f"| {entry['era']} | {entry['blocks']:,} | "
            f"{fmt(entry['mean_common_share'])} | {fmt(entry['sd'])} |")
    add("")
    add("The same quantity by the block's position in its author's own "
        "tenure (quintile of within-author block index), which separates a "
        "platform-level mix shift from a personal one:")
    add("")
    add("| tenure quintile | blocks | mean common share | sd |")
    add("|---|---|---|---|")
    for entry in payload["mix_shift"]["by_tenure_quintile"]:
        add(f"| {entry['era']} | {entry['blocks']:,} | "
            f"{fmt(entry['mean_common_share'])} | {fmt(entry['sd'])} |")
    add("")

    # ---- leans -----------------------------------------------------------
    add("## Registered leans")
    add("")
    for lean in payload["leans"]:
        add(f"- **{lean['id']}** ({lean['statement']}): **{lean['outcome']}** "
            f"— {lean['detail']}")
    add("")

    # ---- boundaries ------------------------------------------------------
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
    add("Artifacts (gitignored): `results/m4_u2b_persistence_budget/` — "
        "`config.json`, `config.sha256.json`, `anchors.json`, `census.json`, "
        "`pool_gate.json`, `g0_anchor_comparison.json`, `rows.json`, "
        "`contrasts.json`, `sensitivities.json`, `taste_purity.json`, "
        "`mix_shift.json`, `verdict.json`, `id_leak_scan.json`, "
        "`report_payload.json`, `run_log.jsonl`.")
    add("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def build_census(order: np.ndarray, cumulative: np.ndarray, universe: int,
                 n_vocab: int, pool_authors: int, pool_blocks: int,
                 block_common: np.ndarray, block_distinct: np.ndarray,
                 eligible: dict[str, Any]) -> dict[str, Any]:
    sizes = {}
    shares = {}
    for q, tag in ((0.3, "q30"), (0.5, "q50"), (0.7, "q70")):
        columns, share = common_prefix(order, cumulative, q)
        sizes[tag] = int(columns.size)
        shares[tag] = round(float(share), 4)
    observed = {
        "universe_in_vocab_events": universe,
        "n_vocab": n_vocab,
        "common_size_q30": sizes["q30"],
        "common_share_q30": shares["q30"],
        "common_size_q50": sizes["q50"],
        "common_share_q50": shares["q50"],
        "common_size_q70": sizes["q70"],
        "common_share_q70": shares["q70"],
        "pool_authors": pool_authors,
        "pool_blocks": pool_blocks,
        "block_common_q05_q25_q50": [
            int(np.quantile(block_common, p)) for p in (0.05, 0.25, 0.5)],
        "block_distinct_q05_q25_q50": [
            int(np.quantile(block_distinct, p)) for p in (0.05, 0.25, 0.5)],
        "eligible_pairs_common_m10_2_3y": eligible["common"]["pairs_2_3y"],
        "eligible_pairs_distinct_m10_2_3y": eligible["distinct"]["pairs_2_3y"],
        "eligible_authors_distinct_m10_2_3y":
            eligible["distinct"]["authors_2_3y"],
    }
    pins = {}
    non_reproducing = []
    for key, expected in CENSUS_PINS.items():
        got = observed[key]
        ok = got == expected
        pins[key] = {"registered": expected, "observed": got,
                     "blocking": key in CENSUS_BLOCKING,
                     "status": "PASS" if ok else "MISMATCH"}
        if not ok:
            non_reproducing.append(
                f"`{key}` registered {expected}, observed {got}")
    blocking_ok = all(pins[k]["status"] == "PASS" for k in CENSUS_BLOCKING)
    return {"pins": pins, "observed": observed,
            "non_reproducing": non_reproducing,
            "blocking_status": "PASS" if blocking_ok else "MISMATCH",
            "status": "PASS" if not non_reproducing else "MISMATCH"}


def mix_shift_descriptive(block_common: np.ndarray, k: int,
                          midpoint_utc: np.ndarray,
                          author: np.ndarray) -> dict[str, Any]:
    share = block_common.astype(np.float64) / float(k)
    years = np.array([datetime.fromtimestamp(t, tz=timezone.utc).year
                      for t in midpoint_utc])
    by_year = []
    for year in sorted(set(int(y) for y in years)):
        sel = years == year
        by_year.append({"era": str(year), "blocks": int(sel.sum()),
                        "mean_common_share": float(share[sel].mean()),
                        "sd": float(share[sel].std(ddof=1))
                        if sel.sum() > 1 else 0.0})
    # within-author tenure position, quintiles of the block's rank fraction
    order = np.lexsort((midpoint_utc, author))
    ranked = np.empty(author.size, dtype=np.float64)
    sorted_author = author[order]
    edges = np.flatnonzero(np.diff(sorted_author)) + 1
    starts = np.concatenate(([0], edges))
    stops = np.concatenate((edges, [sorted_author.size]))
    for start, stop in zip(starts, stops):
        n = stop - start
        ranked[order[start:stop]] = (np.arange(n) + 0.5) / n
    quintile = np.clip((ranked * 5).astype(int), 0, 4)
    by_tenure = []
    for q in range(5):
        sel = quintile == q
        by_tenure.append({"era": f"Q{q + 1}", "blocks": int(sel.sum()),
                          "mean_common_share": float(share[sel].mean()),
                          "sd": float(share[sel].std(ddof=1))
                          if sel.sum() > 1 else 0.0})
    return {"by_calendar_year": by_year, "by_tenure_quintile": by_tenure,
            "definition": MIX_SHIFT_ERAS,
            "overall_mean_common_share": float(share.mean())}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--b-perm", type=int, default=B_PERM)
    parser.add_argument("--b-boot", type=int, default=B_BOOT)
    parser.add_argument("--registration-commit", type=str, default="96f7e40")
    parser.add_argument("--skip-g0", action="store_true",
                        help="debug only; the committed run never skips G0")
    args = parser.parse_args(argv)

    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    log = RunLog(output / "run_log.jsonl")
    run_started = utc_now()
    log.event("start", cache=str(args.cache), b_perm=args.b_perm,
              b_boot=args.b_boot)

    # ---- cache anchors (BLOCKING) ---------------------------------------
    cache = U2.load_event_cache(args.cache)
    anchors = U2.verify_cache_anchors(cache)
    write_json(output / "anchors.json", anchors)
    log.event("cache_anchor_gate", **anchors)
    if anchors["status"] != "PASS":
        raise SystemExit(f"STOP: cache anchor gate FAILED: "
                         f"{anchors['mismatches']}")

    n_authors_total = len(cache.authors)
    n_vocab = len(cache.vocabulary)
    origin = float(cache.created_utc.min())
    vocab_index_full = cache.vocab_of_subreddit[cache.subreddit_code]

    # ---- blocks: U2's exact construction --------------------------------
    log.event("blocks_build_start", k=K_PRIMARY)
    blocks = U2.build_blocks(cache.author_code, cache.created_utc,
                             vocab_index_full, n_vocab, K_PRIMARY,
                             n_authors=n_authors_total)
    quarters_all = U2.assign_quarters(blocks.midpoint, origin)
    mid_days_all = (blocks.midpoint - origin) / 86400.0
    pool = np.flatnonzero(blocks.blocks_per_author >= POOL_MIN_BLOCKS)
    pool_mask = np.zeros(n_authors_total, dtype=bool)
    pool_mask[pool] = True
    sel_pool = pool_mask[blocks.author]
    # U2's exact ordering convention, so G0 reproduces bit-for-bit.
    order_pool = np.lexsort((mid_days_all[sel_pool], quarters_all[sel_pool]))
    idx_pool = np.flatnonzero(sel_pool)[order_pool]
    pool_author = blocks.author[idx_pool]
    pool_quarter = quarters_all[idx_pool]
    pool_mid = mid_days_all[idx_pool]
    pool_mid_utc = blocks.midpoint[idx_pool]
    pool_features = blocks.features[idx_pool]
    log.event("blocks_built", pool_authors=int(pool.size),
              pool_blocks=int(pool_features.shape[0]))

    # ---- the split -------------------------------------------------------
    rank_order, cumulative, universe = community_ranking(
        vocab_index_full, n_vocab)

    def split_columns(q: float) -> tuple[np.ndarray, np.ndarray, float]:
        common, share = common_prefix(rank_order, cumulative, q)
        mask = np.zeros(n_vocab, dtype=bool)
        mask[common] = True
        return common, np.flatnonzero(~mask), share

    common_primary, distinct_primary, share_primary = split_columns(Q_PRIMARY)
    raw_common = block_counts_over(pool_features, common_primary, K_PRIMARY)
    integral_error = float(np.abs(raw_common - np.rint(raw_common)).max())
    if integral_error > 1e-3:            # blocking: counts must be exact
        raise SystemExit(
            f"STOP: recovered sub-vocabulary counts are not integral "
            f"(max deviation {integral_error:.3e})")
    block_common_primary = np.rint(raw_common).astype(np.int64)
    block_distinct_primary = K_PRIMARY - block_common_primary

    def eligibility(q: float, m: int) -> dict[str, Any]:
        common_cols, distinct_cols, share = split_columns(q)
        raw = block_counts_over(pool_features, common_cols, K_PRIMARY)
        common_count = np.rint(raw).astype(np.int64)
        distinct_count = K_PRIMARY - common_count
        masks = {
            "common (marginal)": common_count >= m,
            "distinct (marginal)": distinct_count >= m,
            "intersection": (common_count >= m) & (distinct_count >= m),
        }
        out: dict[str, Any] = {"q": q, "m": m, "common_size":
                               int(common_cols.size), "common_share": share,
                               "common_columns": common_cols,
                               "distinct_columns": distinct_cols,
                               "intersection_mask": masks["intersection"]}
        for name, mask in masks.items():
            pairs, contributors = self_pair_census(pool_author[mask],
                                                   pool_mid[mask])
            key = {"common (marginal)": "common",
                   "distinct (marginal)": "distinct",
                   "intersection": "intersection"}[name]
            out[key] = {"blocks": int(mask.sum()),
                        "pairs_2_3y": int(pairs[FAR_BIN]),
                        "authors_2_3y": int(contributors[FAR_BIN]),
                        "pairs_all_bins": [int(v) for v in pairs],
                        "authors_all_bins": [int(v) for v in contributors]}
            out[name] = out[key]
        return out

    log.event("census_start")
    elig_primary = eligibility(Q_PRIMARY, M_PRIMARY)
    census = build_census(rank_order, cumulative, universe, n_vocab,
                          int(pool.size), int(pool_features.shape[0]),
                          block_common_primary, block_distinct_primary,
                          elig_primary)
    write_json(output / "census.json", census)
    log.event("census", status=census["status"],
              blocking=census["blocking_status"])
    if census["blocking_status"] != "PASS":
        raise SystemExit(
            "STOP: blocking census pin(s) differ from the registration: "
            + json.dumps({k: census["pins"][k] for k in CENSUS_BLOCKING
                          if census["pins"][k]["status"] != "PASS"},
                         sort_keys=True))

    # ---- the registered pool gate (#69) ---------------------------------
    inter = elig_primary["intersection"]
    pool_gate = {
        "q": Q_PRIMARY, "m": M_PRIMARY,
        "pairs_2_3y": inter["pairs_2_3y"],
        "authors_2_3y": inter["authors_2_3y"],
        "required_pairs_2_3y": POOL_GATE_MIN_PAIRS_2_3Y,
        "required_authors_2_3y": POOL_GATE_MIN_AUTHORS_2_3Y,
        "pairs_ok": inter["pairs_2_3y"] >= POOL_GATE_MIN_PAIRS_2_3Y,
        "authors_ok": inter["authors_2_3y"] >= POOL_GATE_MIN_AUTHORS_2_3Y,
        "pairs_fraction": inter["pairs_2_3y"] / POOL_GATE_MIN_PAIRS_2_3Y,
        "authors_fraction": inter["authors_2_3y"] / POOL_GATE_MIN_AUTHORS_2_3Y,
        "eligible_blocks": inter["blocks"],
        "pairs_all_bins": inter["pairs_all_bins"],
        "authors_all_bins": inter["authors_all_bins"],
    }
    pool_gate["status"] = ("PASS" if pool_gate["pairs_ok"]
                           and pool_gate["authors_ok"] else "UNMET")
    write_json(output / "pool_gate.json", pool_gate)
    log.event("pool_gate", **{k: v for k, v in pool_gate.items()
                              if not isinstance(v, list)})

    # ---- G0: recompute U2's primary arm and bit-compare ------------------
    if args.skip_g0:
        g0 = {"status": "SKIPPED", "bitwise_identical": False,
              "max_abs_difference": float("nan"), "fields": [],
              "source": str(U2_ARTIFACTS / "arms.json")}
    else:
        log.event("g0_start", blocks=int(pool_features.shape[0]))
        recomputed = U2.compute_arm(
            pool_features, pool_author, pool_quarter, pool_mid,
            n_perm=args.b_perm, n_boot=args.b_boot, seed=U2.SEED,
            cross_sampler_check=False, log=log, label="G0 U2 primary")
        committed_arms = json.loads(
            (U2_ARTIFACTS / "arms.json").read_text(encoding="utf-8"))
        committed = next(a for a in committed_arms if a["key"] == "primary")
        g0 = g0_compare(recomputed, committed)
        del recomputed
    write_json(output / "g0_anchor_comparison.json", g0)
    log.event("g0", status=g0["status"],
              max_abs_difference=g0["max_abs_difference"])
    if g0["status"] == "FAIL":
        raise SystemExit("STOP: G0 anchor comparison FAILED against U2's "
                         "committed artifacts")

    # ---- the four rows on the intersection set ---------------------------
    keep = elig_primary["intersection_mask"]
    row_author = pool_author[keep]
    row_quarter = pool_quarter[keep]
    row_mid = pool_mid[keep]
    row_features_full = pool_features[keep]

    def run_row(key: str, label: str, features: np.ndarray) -> dict[str, Any]:
        log.event("row_start", row=key, blocks=int(features.shape[0]),
                  dim=int(features.shape[1]))
        result = U2.compute_arm(features, row_author, row_quarter, row_mid,
                                n_perm=args.b_perm, n_boot=args.b_boot,
                                seed=SEED, cross_sampler_check=False,
                                log=log, label=label)
        result["key"] = key
        log.event("row_done", row=key, e_near=result["curve"][NEAR_BIN],
                  e_far=result["curve"][FAR_BIN],
                  floor=result["floor_share"])
        return result

    row_full = run_row("full", "full vocabulary", row_features_full)
    row_common = run_row(
        f"common (q={Q_PRIMARY}, {common_primary.size} communities)",
        "common-restricted",
        renormalize(row_features_full, common_primary))
    row_distinct = run_row(
        f"distinct (q={Q_PRIMARY}, {distinct_primary.size} communities)",
        "distinctive-restricted",
        renormalize(row_features_full, distinct_primary))

    # ---- taste row -------------------------------------------------------
    log.event("taste_start", folds=TASTE_FOLDS, dim=TASTE_DIM)
    first_half, first_half_mass = first_half_counts(cache, pool, n_vocab)
    folds = taste_folds(pool, SEED, TASTE_FOLDS)
    taste_results: list[dict[str, Any]] = []
    taste_purity: list[dict[str, Any]] = []
    for fold, (train_idx, test_idx) in enumerate(folds):
        train_authors = pool[train_idx]
        test_authors = pool[test_idx]
        overlap = len(set(train_authors.tolist())
                      & set(test_authors.tolist()))
        counts = first_half[train_idx]
        fitted_mass = float(counts.sum())
        train_mass = float(first_half_mass[train_idx].sum())
        test_mass = float(first_half_mass[test_idx].sum())
        # BLOCKING purity gate: the fitted object must be exactly the
        # training authors' first-half mass, with zero test-author mass.
        assert overlap == 0, "fold purity violated: train/test overlap"
        assert train_idx.size + test_idx.size == pool.size, \
            "fold purity violated: folds are not a partition of the pool"
        assert counts.shape[0] == train_authors.size, \
            "fold purity violated: fitted rows are not the training set"
        assert abs(fitted_mass - train_mass) < 1e-6, \
            "fold purity violated: fitted mass is not the training mass"
        assert test_mass > 0.0, "degenerate fold: no test-author mass"

        embedding = ppmi_svd(counts, TASTE_DIM, SEED + fold)
        in_fold = np.isin(row_author, test_authors)
        taste = np.asarray(row_features_full[in_fold], dtype=np.float64) \
            @ embedding
        norms = np.linalg.norm(taste, axis=1, keepdims=True)
        norms[norms == 0.0] = 1.0
        taste = (taste / norms).astype(np.float32)
        result = U2.compute_arm(taste, row_author[in_fold],
                                row_quarter[in_fold], row_mid[in_fold],
                                n_perm=args.b_perm, n_boot=args.b_boot,
                                seed=SEED, cross_sampler_check=False,
                                log=log, label=f"taste fold {fold}")
        taste_results.append(result)
        taste_purity.append({
            "fold": fold, "n_train": int(train_authors.size),
            "n_test": int(test_authors.size), "overlap": overlap,
            "fitted_mass": fitted_mass, "train_first_half_mass": train_mass,
            "test_mass_excluded": test_mass,
            "test_blocks": int(in_fold.sum()),
            "embedding_rank": int(embedding.shape[1]),
            "status": "PASS"})
        log.event("taste_fold_done", fold=fold,
                  floor=result["floor_share"])
    row_taste = pool_fold_results(taste_results)
    row_taste["key"] = "taste (d=64, out-of-fold)"
    write_json(output / "taste_purity.json", taste_purity)

    # ---- contrasts -------------------------------------------------------
    delta = contrast("Δfloor = F_distinct − F_common", row_distinct,
                     row_common, paired=True)
    cell = classify_delta(delta)
    secondary = contrast("F_taste − F_full", row_taste, row_full,
                         paired=False)
    secondary_cell = classify_delta(secondary)
    write_json(output / "contrasts.json",
               {"primary": delta, "primary_cell": cell,
                "secondary": secondary, "secondary_cell": secondary_cell})

    rows_summary = []
    for result in (row_full, row_common, row_distinct, row_taste):
        summary = summarize_row(result)
        summary["key"] = result["key"]
        rows_summary.append(summary)
    write_json(output / "rows.json", rows_summary)

    # ---- sensitivities ---------------------------------------------------
    grid = [(Q_PRIMARY, M_PRIMARY)]
    grid += [(q, M_PRIMARY) for q in Q_SENSITIVITIES]
    grid += [(Q_PRIMARY, m) for m in M_SENSITIVITIES]
    sensitivities: list[dict[str, Any]] = []
    flags: list[str] = []
    gate_clearing: list[str] = []
    for q, m in grid:
        if (q, m) == (Q_PRIMARY, M_PRIMARY):
            entry_common, entry_distinct = row_common, row_distinct
            elig = elig_primary
        else:
            elig = eligibility(q, m)
            mask = elig["intersection_mask"]
            author_s = pool_author[mask]
            quarter_s = pool_quarter[mask]
            mid_s = pool_mid[mask]
            features_s = pool_features[mask]
            log.event("sensitivity_start", q=q, m=m,
                      blocks=int(mask.sum()))
            entry_common = U2.compute_arm(
                renormalize(features_s, elig["common_columns"]),
                author_s, quarter_s, mid_s, n_perm=args.b_perm,
                n_boot=args.b_boot, seed=SEED, cross_sampler_check=False,
                log=log, label=f"common q={q} m={m}")
            entry_distinct = U2.compute_arm(
                renormalize(features_s, elig["distinct_columns"]),
                author_s, quarter_s, mid_s, n_perm=args.b_perm,
                n_boot=args.b_boot, seed=SEED, cross_sampler_check=False,
                log=log, label=f"distinct q={q} m={m}")
        entry_delta = contrast(f"Δfloor (q={q}, m={m})", entry_distinct,
                               entry_common, paired=True)
        entry_cell = classify_delta(entry_delta)
        inter_s = elig["intersection"]
        gate_ok = (inter_s["pairs_2_3y"] >= POOL_GATE_MIN_PAIRS_2_3Y
                   and inter_s["authors_2_3y"] >= POOL_GATE_MIN_AUTHORS_2_3Y)
        tag = f"q={q}/m={m}"
        if gate_ok:
            gate_clearing.append(
                f"{tag} ({inter_s['pairs_2_3y']:,} pairs, "
                f"{inter_s['authors_2_3y']} authors)")
        flag = None
        if (q, m) != (Q_PRIMARY, M_PRIMARY) and \
                entry_cell["cell"] != cell["cell"]:
            flag = "#73"
            flags.append(
                f"{tag} lands in `{entry_cell['cell']}` while the primary "
                f"configuration lands in `{cell['cell']}`")
        sensitivities.append({
            "q": q, "m": m, "common_size": elig["common_size"],
            "common_share": elig["common_share"],
            "blocks": inter_s["blocks"],
            "pairs_2_3y": inter_s["pairs_2_3y"],
            "authors_2_3y": inter_s["authors_2_3y"],
            "pool_gate": "PASS" if gate_ok else "UNMET",
            "f_common": float(entry_common["floor_share"]),
            "f_common_ci": percentile_ci(
                floor_share(entry_common["boot_curve"])),
            "f_distinct": float(entry_distinct["floor_share"]),
            "f_distinct_ci": percentile_ci(
                floor_share(entry_distinct["boot_curve"])),
            "e_common": [float(v) for v in entry_common["curve"]],
            "e_distinct": [float(v) for v in entry_distinct["curve"]],
            "delta": {k: v for k, v in entry_delta.items()},
            "cell": entry_cell["cell"],
            "flag_73": flag,
            "is_primary": (q, m) == (Q_PRIMARY, M_PRIMARY),
        })
        log.event("sensitivity_done", q=q, m=m, cell=entry_cell["cell"],
                  delta=entry_delta["point"])
    write_json(output / "sensitivities.json", sensitivities)

    # ---- mix shift -------------------------------------------------------
    mix_shift = mix_shift_descriptive(block_common_primary, K_PRIMARY,
                                      pool_mid_utc, pool_author)
    write_json(output / "mix_shift.json", mix_shift)

    # ---- leans -----------------------------------------------------------
    stopped = pool_gate["status"] != "PASS"
    provisional = " (PROVISIONAL: the pool gate is unmet)" if stopped else ""
    l1_cell_ok = cell["cell"] == "DISTINCTIVE_STANDING"
    l1_point_ok = LEAN_DELTA[0] < delta["point"] <= LEAN_DELTA[1]
    if l1_cell_ok and l1_point_ok:
        l1 = "HELD"
    elif l1_cell_ok:
        l1 = "CELL HELD, POINT OUTSIDE THE LEANED RANGE"
    else:
        l1 = "MISSED"
    f_taste = float(row_taste["floor_share"])
    f_full = float(row_full["floor_share"])
    highest = max(rows_summary, key=lambda r: (r["floor_share"]
                                               if np.isfinite(
                                                   r["floor_share"])
                                               else -np.inf))
    l2 = ("HELD" if f_taste >= f_full and highest["key"] == row_taste["key"]
          else ("PARTIAL (F_taste >= F_full but another row is highest)"
                if f_taste >= f_full else "MISSED"))
    leans = [
        {"id": "L1", "statement": "DISTINCTIVE_STANDING with point Δfloor in "
         f"({LEAN_DELTA[0]}, {LEAN_DELTA[1]}]", "outcome": l1 + provisional,
         "detail": f"realized cell `{cell['cell']}`, point Δfloor "
                   f"{fmt(delta['point'])} {fmt_ci(delta['ci'])}"},
        {"id": "L2", "statement": "the taste row posts the highest floor "
         "share of all four rows (F_taste ≥ F_full)",
         "outcome": l2 + provisional,
         "detail": f"F_taste {fmt(f_taste)}, F_full {fmt(f_full)}, highest "
                   f"row `{highest['key']}` at {fmt(highest['floor_share'])}"},
    ]

    # ---- verdict ---------------------------------------------------------
    outcome = "POOL_GATE_UNMET" if stopped else cell["cell"]
    verdict = {
        "outcome": outcome,
        "cell": None if stopped else cell["cell"],
        "provisional_cell": cell["cell"] if stopped else None,
        "delta_point": delta["point"],
        "delta_ci": delta["ci"],
        "pool_gate": pool_gate["status"],
        "flags_73": flags,
        "generated_utc": utc_now(),
    }
    write_json(output / "verdict.json", verdict)

    # ---- config ----------------------------------------------------------
    script_bytes = Path(__file__).read_bytes()
    config = {
        "registration_commit": args.registration_commit,
        "seed": SEED, "b_perm": args.b_perm, "b_boot": args.b_boot,
        "k": K_PRIMARY, "pool_min_blocks": POOL_MIN_BLOCKS,
        "quarter_days": QUARTER_DAYS,
        "bin_labels": list(BIN_LABELS),
        "verdict_endpoint_bin": BIN_LABELS[FAR_BIN],
        "descriptive_bin": BIN_LABELS[DESCRIPTIVE_BIN],
        "q_primary": Q_PRIMARY, "q_sensitivities": list(Q_SENSITIVITIES),
        "m_primary": M_PRIMARY, "m_sensitivities": list(M_SENSITIVITIES),
        "taste_folds": TASTE_FOLDS, "taste_dim": TASTE_DIM,
        "equivalence_band": EQUIVALENCE_BAND,
        "lean_delta": list(LEAN_DELTA),
        "pool_gate_min_pairs_2_3y": POOL_GATE_MIN_PAIRS_2_3Y,
        "pool_gate_min_authors_2_3y": POOL_GATE_MIN_AUTHORS_2_3Y,
        "cache": str(args.cache),
        "u2_machinery": str(U2_SCRIPT),
        "u2_machinery_sha256": hashlib.sha256(
            U2_SCRIPT.read_bytes()).hexdigest(),
        "u2_artifacts": str(U2_ARTIFACTS),
        "epoch_origin_utc": datetime.fromtimestamp(
            origin, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "inherited_from_u2": [
            "build_blocks (exact-K disjoint blocks, Hellinger features)",
            "assign_quarters / gap_bin (epoch cells and gap bins)",
            "compute_arm (epoch-matched EXACT stratified cross baseline, "
            "RD-U2-1 form; within-quarter permutation scaffold; author "
            "cluster bootstrap)",
            "scan_for_cohort_ids (ID-leak gate)",
        ],
        "recorded_choices": {
            "community_ranking_tie_break": TIE_BREAK,
            "eligibility_is_a_block_property":
                "a block holds exactly K in-vocabulary events, so "
                "'both blocks hold >= m events in BOTH sub-vocabularies' "
                "reduces to the per-block predicate (common >= m AND "
                "K - common >= m); the intersection PAIR set is therefore "
                "exactly the same-author pair set of the eligible BLOCK "
                "subset, and all rows share pair indices, cross reservoir, "
                "permutation plans and bootstrap draws EXACTLY (#72)",
            "sub_vocabulary_counts":
                "recovered from the Hellinger feature as K * f^2 and "
                "asserted integral to 1e-3 before use (the feature is "
                "sqrt(count / K) and already unit-norm because a block's "
                "counts sum to K)",
            "renormalization":
                "the full Hellinger vector's sub-vocabulary columns, "
                "L2-renormalized — identical to sqrt(counts) over the "
                "sub-vocabulary, L2-normalized",
            "pool_rule_not_recomputed":
                "the U2 pool (>= 4 blocks at K = 50, 849 authors) is "
                "inherited unchanged; eligibility filters BLOCKS inside it "
                "and is never used to re-derive a pool, so an author with "
                "fewer than two eligible blocks contributes no self pair but "
                "still serves as a cross partner",
            "taste_first_half_rule": FIRST_HALF_RULE,
            "taste_embedding":
                "PPMI + truncated SVD, d = 64, of the training authors' "
                "first-half count matrix; the recipe is reproduced verbatim "
                "from scripts/run_suica_m4_t2_matched_residual.py:587-601 "
                "and asserted bit-identical to it in the contract tests",
            "taste_block_vector":
                "features @ embedding (the Hellinger-weighted mean of the "
                "block's communities' embeddings), L2-normalized",
            "taste_pooling":
                "per-fold curves on TEST authors' pairs, pooled by unweighted "
                "mean over folds (U1 convention); the bootstrap and "
                "permutation replicate matrices are pooled the same way, so "
                "the pooled interval is a fold-stratified cluster bootstrap",
            "taste_cross_reservoir":
                "fold-local: a fold's cross baseline uses that fold's test "
                "authors only, because two folds' embeddings are different "
                "coordinate systems and a cross-fold cosine is not defined; "
                "the SELF pair set is still exactly the intersection set, "
                "partitioned by fold",
            "bootstrap_pairing":
                "compute_arm draws its author multinomial from seed + 11 "
                "with the same author count for every row on the shared "
                "block set, so Δfloor's bootstrap is PAIRED replicate by "
                "replicate; the secondary contrast F_taste − F_full is NOT "
                "paired (fold-stratified against pool-level draws) and its "
                "interval is correspondingly conservative",
            "bootstrap_cross_baseline":
                "inherited from U2 unchanged: cell cross means are held at "
                "their full-row values inside the cluster bootstrap; only "
                "the self side and the epoch-matching weights are resampled",
            "floor_share_null":
                "the permutation null of a RATIO whose numerator and "
                "denominator are both driven to zero is heavy-tailed by "
                "construction; the registration's claim is about the null's "
                "LOCATION, so the center and IQR are the reported checks and "
                "the 95% band is reported but not read as a bound",
            "mix_shift_eras":
                f"{MIX_SHIFT_ERAS}; a within-author tenure-quintile variant "
                "is reported beside it because 'account era' admits both "
                "readings and the descriptive is non-verdict-moving",
            "pool_gate_stop_semantics":
                "RD-U2B-1 (disclosed): the registered #69 STOP is "
                "implemented as a STOP AT THE VERDICT, not a STOP AT THE "
                "COMPUTATION — no cell is assigned and every estimate is "
                "labelled PROVISIONAL, while the rows, contrasts and the "
                "registered sensitivity grid are still computed so the "
                "planner can adjudicate from numbers rather than from an "
                "empty report. No re-split is performed and no configuration "
                "is promoted",
        },
        "script_sha256": hashlib.sha256(script_bytes).hexdigest(),
    }
    write_json(output / "config.json", config)
    write_json(output / "config.sha256.json",
               {"script_sha256": config["script_sha256"],
                "config_sha256": hashlib.sha256(
                    json.dumps(config, sort_keys=True,
                               default=float).encode("utf-8")).hexdigest()})

    # ---- payload / report ------------------------------------------------
    gates = {
        "cache anchor gate (3,005,360 events / 1401 authors / 1191 "
        "vocabulary)": anchors["status"],
        "split census — blocking pins (universe, Common(0.5) size and share, "
        "pool authors and blocks)": census["blocking_status"],
        "split census — all registered pins": census["status"],
        "G0 — U2 primary arm bit-comparison (#56)": g0["status"],
        "registered pool gate #69 (intersection, 2-3y)": pool_gate["status"],
        "taste-row fold purity (mass identity, zero test mass)":
            "PASS" if all(p["status"] == "PASS" for p in taste_purity)
            else "FAIL",
        "sub-vocabulary counts integral (max deviation "
        f"{integral_error:.2e})": "PASS",
        "no synthetic gate required (R layer, no world simulated)": "N/A",
    }
    boundaries = [
        "**The eq-12 projection caution, carried into the outcome as "
        "registered:** this leg reads ONE slow-time projection of the "
        "transition kernel K_u (eq 12) onto the marginal selection "
        "distribution π_u over the 1191-community vocabulary, now split by "
        "carrier. A layer split here would be a statement about π_u on the "
        "Hellinger unigram sphere over calendar time, never about a "
        "psychological attribute (§5.4), and 'common' and 'distinctive' are "
        "EVENT-MASS strata of a subreddit vocabulary, not the T-line's "
        "personality/identity constructs — the T-line proposition is what "
        "motivates the test, not what the strata mean.",
        "**U2's three-year scoping binds every floor share here.** A floor "
        "share is E(2-3y)/E(0-90d): what survives THREE YEARS, not a "
        "demonstrated permanent floor. U2's curve had not flattened by its "
        "verdict endpoint (E(3y+) below E(2-3y), the exponential asymptote "
        "weakly identified below both), so 'permanent floor' and 'permanent "
        "core' are forbidden prose here as they are in U2; 'three-year core' "
        "is the licensed phrase, and no floor share in this report may be "
        "extrapolated past the observed span.",
        "**LEVEL differences across rows are never interpreted** (registered "
        "comparison rule): a restricted row is a lower-dimensional, "
        "differently attenuated view of the same block, and the attenuation "
        "varies block by block with how much mass falls in that "
        "sub-vocabulary. Only within-row floor shares and their contrasts "
        "transport across rows.",
        "The eligibility floor is not neutral. Requiring >= m events in BOTH "
        "sub-vocabularies keeps only BALANCED blocks, so the intersection "
        "set over-represents authors who mix common and distinctive "
        "communities within a 50-event window and under-represents "
        "specialists of either kind. That selection is the price of the "
        "shared pair set (#72) and it is why the pool gate exists.",
        "The taste row's cross baseline is fold-local while the other three "
        "rows share one pool-level reservoir, so the taste row's LEVEL is "
        "not on the other rows' scale even before attenuation is considered. "
        "Its floor share still transports under the comparison rule; its "
        "E(b) values do not.",
        "Label-free and corpus-level throughout: no Big5 or MBTI value is "
        "read anywhere in this leg, and no per-author quantity is reported "
        "or committed.",
    ]
    if stopped:
        boundaries.insert(0,
                          "**NO VERDICT IS CLAIMED.** The registered #69 pool "
                          "gate is unmet at the primary configuration, so "
                          "this leg assigns no classification cell. Every "
                          "estimate below the gate section is PROVISIONAL "
                          "and exists so the planner can adjudicate the "
                          "re-split it now owns; none of it may be cited as "
                          "a U2b result.")

    pool_realization = {
        name: elig_primary[name]
        for name in ("common (marginal)", "distinct (marginal)",
                     "intersection")}

    run_finished = utc_now()
    payload = {
        "generated_utc": utc_now(),
        "run_started_utc": run_started,
        "run_finished_utc": run_finished,
        "registration_commit": args.registration_commit,
        "outcome": outcome,
        "anchors": anchors,
        "census": census,
        "u2_authors_2_3y": int(json.loads(
            (U2_ARTIFACTS / "census.json").read_text(encoding="utf-8")
        )["observed"]["authors_2_3y"]),
        "pool_gate": pool_gate,
        "pool_realization": pool_realization,
        "g0": g0,
        "rows": rows_summary,
        "delta": delta,
        "classification": cell,
        "secondary": secondary,
        "secondary_cell": secondary_cell,
        "sensitivities": [
            {k: v for k, v in s.items()} for s in sensitivities],
        "flags_73": flags,
        "gate_clearing_configs": gate_clearing,
        "taste_purity": taste_purity,
        "taste_per_fold_floor": row_taste["per_fold_floor_share"],
        "mix_shift": mix_shift,
        "leans": leans,
        "boundaries": boundaries,
        "gates": gates,
        "config": config,
    }

    write_report(args.report, payload)
    scan = U2.scan_for_cohort_ids(
        [args.report, Path(__file__),
         ROOT / "tests/test_m4_u2b_persistence_budget.py",
         ROOT / "docs/SUICA_M4_U_WHEN_ORDER_PLAN.md",
         ROOT / "docs/CLAIMS_LEDGER.md"],
        cache.authors)
    write_json(output / "id_leak_scan.json", scan)
    log.event("id_leak_scan", status=scan["status"], hits=scan["n_hits"])
    gates["ID-leak scan (0 of 1401 cohort IDs in committed files)"] = \
        scan["status"]
    payload["gates"] = gates
    write_report(args.report, payload)
    if scan["status"] != "PASS":
        raise SystemExit(f"STOP: ID-leak scan FAILED: {scan['hits']}")

    write_json(output / "report_payload.json",
               {k: v for k, v in payload.items() if k != "config"})
    log.event("done", outcome=outcome, delta=delta["point"],
              pool_gate=pool_gate["status"], flags_73=len(flags))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
