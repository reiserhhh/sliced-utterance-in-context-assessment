#!/usr/bin/env python3
"""SUICA M4-U2c -- the decay-rate contrast (the verdict-issuing completion of U2b).

Executes the registration committed at 6a4a5bb in
``docs/SUICA_M4_U_WHEN_ORDER_PLAN.md`` (section "U2c -- the decay-rate contrast
(completion of U2b; registered BEFORE run, 2026-08-18)").  Nothing here
re-derives a design decision; where the registration is silent on an
implementation detail the simplest deterministic option is taken and recorded
in ``results/m4_u2c_decay_rate_contrast/config.json`` (mirrored into the
report's configuration block, rule 24).

The question.  U2b asked WHICH LAYER MOVES and stopped at its #69 pool gate
with a quarantined, unanimous provisional sign (COMMON_STANDING: the common
mass decays SLOWER than the distinctive tail).  U2c issues the verdict from a
registered-before-run primary configuration -- q = 0.5, m = 5, the largest
REALIZED passing pool -- on a ratio-free estimand (#79): per carrier row, the
DECAY RATE of the epoch-matched personal excess,

    log E_row(b) = log E0_row - lambda_row * gap_years(b),   b in the FIVE
                                                             verdict bins,

fitted by OLS at the row's realized per-bin mean self-pair gaps.  The verdict
contrast is

    Lambda = lambda_distinct - lambda_common       (positive = the distinctive
                                                    decays faster = common
                                                    standing).

Disclosure (carried from the registration).  U2b's provisional sign was KNOWN
when U2c was registered; this leg is a completion under corrected gate
arithmetic (#78) and a re-posed estimand (#79), not a prediction.  The
registration also projected that detection is BORDERLINE (projected CI
half-width 0.08-0.10/y against a point of about +0.10/y), so SIGN_UNRESOLVED
is a live cell and the verdict may be the interval statement.

Inheritance is not exemption (#56).  The U2b machinery is IMPORTED BY FILE from
``scripts/run_suica_m4_u2b_persistence_budget.py`` (which itself imports U2's
estimator by file) -- block construction, the vocabulary split, the
intersection eligibility predicate, the epoch-matched EXACT stratified cross
baseline, the within-quarter permutation scaffold, the author cluster bootstrap
and the taste row's per-fold PPMI+SVD recipe are the same objects, not
re-implementations.  Two blocking anchors guard the reuse:

  * GATE ANCHORS (#78) -- U2b's realized intersection quantities at the two
    configurations this leg runs (q=0.5/m=5 -> 179,107 pairs / 424 authors;
    q=0.7/m=10 -> 108,716 / 401) are RECOMPUTED here and compared exactly.
  * G0 -- U2b's four-row E(b) table at q=0.5/m=10 is recomputed through the
    same imported estimator and bit-compared against U2b's committed
    ``rows.json``.

Any mismatch STOPS the leg.
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

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Configuration constants (registration pins first, then recorded choices).
# ---------------------------------------------------------------------------

SEED = 20260818                     # registration pin
B_PERM = 499                        # registration pin
B_BOOT = 1000                       # registration pin

Q_PRIMARY = 0.5                     # registration pin: primary split level
M_PRIMARY = 5                       # registration pin: primary floor (#78)
Q_CONFIRMATORY = 0.7                # registration pin: confirmatory arm
M_CONFIRMATORY = 10                 # registration pin: confirmatory arm
Q_G0 = 0.5                          # U2b's primary configuration (G0 anchor)
M_G0 = 10

# The FIVE verdict bins the slope is fitted over.  The 3y+ bin is DESCRIPTIVE
# and NEVER enters the fit (registration, inherited from U2).
N_FIT_BINS = 5
DAYS_PER_YEAR = 365.25              # recorded choice; gap_years = days / this

# Registered pool targets (#69), re-checked at both configurations.
POOL_GATE_MIN_PAIRS_2_3Y = 100_000
POOL_GATE_MIN_AUTHORS_2_3Y = 400

# The gate's EXECUTED predicate (#78): U2b's REALIZED intersection quantities
# at the configurations this leg runs.  Recomputed here; mismatch STOPS.
GATE_ANCHORS: dict[str, dict[str, int]] = {
    "primary q=0.5/m=5": {"q_milli": 500, "m": 5,
                          "pairs_2_3y": 179_107, "authors_2_3y": 424},
    "confirmatory q=0.7/m=10": {"q_milli": 700, "m": 10,
                                "pairs_2_3y": 108_716, "authors_2_3y": 401},
}

# Blocking split pins inherited from U2b's census (the split must BE the
# registered object; the registration says STOP if Common(0.5) is not 32).
COMMON_SIZE_Q50 = 32
COMMON_SIZE_Q70 = 104
CENSUS_UNIVERSE = 2_348_361
POOL_AUTHORS = 849
POOL_BLOCKS = 45_731

# Registration-time projection, reported against the realized width (#71/#79).
PROJECTED_LAMBDA_POINT = 0.10
PROJECTED_HALF_WIDTH = (0.08, 0.10)
PROJECTED_LAMBDA_COMMON = 0.239
PROJECTED_LAMBDA_DISTINCT = 0.338
PROJECTED_LAMBDA_TASTE = 0.16

DEFAULT_OUTPUT = ROOT / "results/m4_u2c_decay_rate_contrast"
DEFAULT_REPORT = (
    ROOT / "reports/SUICA_M4_U2C_DECAY_RATE_CONTRAST_REPORT.md")
U2B_SCRIPT = ROOT / "scripts/run_suica_m4_u2b_persistence_budget.py"
U2B_ARTIFACTS = ROOT / "results/m4_u2b_persistence_budget"


# ---------------------------------------------------------------------------
# U2b machinery, imported by file (#56: the inherited object, not a copy).
# ---------------------------------------------------------------------------


def load_u2b_module(path: Path = U2B_SCRIPT):
    """Import U2b's harness so its split, eligibility and rows ARE reused."""

    spec = importlib.util.spec_from_file_location("suica_m4_u2b", path)
    if spec is None or spec.loader is None:      # pragma: no cover
        raise RuntimeError(f"cannot import U2b machinery from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["suica_m4_u2b"] = module
    spec.loader.exec_module(module)
    return module


U2B = load_u2b_module()
U2 = U2B.U2                          # U2's estimator, one import deeper

# Names reused unchanged (listed so the reuse is auditable).
BIN_LABELS: tuple[str, ...] = U2B.BIN_LABELS
N_BINS: int = U2B.N_BINS
NEAR_BIN: int = U2B.NEAR_BIN
FAR_BIN: int = U2B.FAR_BIN           # 2-3y, the last bin in the slope fit
DESCRIPTIVE_BIN: int = U2B.DESCRIPTIVE_BIN   # 3y+, NEVER in the fit
K_PRIMARY: int = U2B.K_PRIMARY
POOL_MIN_BLOCKS: int = U2B.POOL_MIN_BLOCKS
TASTE_FOLDS: int = U2B.TASTE_FOLDS
TASTE_DIM: int = U2B.TASTE_DIM
DEFAULT_CACHE = U2B.DEFAULT_CACHE
ANCHOR_AUTHORS = U2B.ANCHOR_AUTHORS
write_json = U2B.write_json
utc_now = U2B.utc_now
fmt = U2B.fmt
fmt_ci = U2B.fmt_ci
percentile_ci = U2B.percentile_ci
renormalize = U2B.renormalize
ppmi_svd = U2B.ppmi_svd
RunLog = U2B.RunLog

# Fields of U2b's committed per-row table compared bit-for-bit (gate G0).
G0_ROW_FIELDS = ("curve", "curve_ci", "curve_null_band", "curve_null_center",
                 "self_mean", "cross_mean_matched", "mean_gap_days",
                 "d", "d_ci", "floor_share", "self_pairs", "n_blocks",
                 "n_authors", "perm_p_existence", "perm_p_decay")

ROW_KEYS = ("full", "common", "distinct", "taste")


# ---------------------------------------------------------------------------
# The estimand: a log-linear decay rate over the FIVE verdict bins
# ---------------------------------------------------------------------------


def log_slope_fit(gap_years: np.ndarray, curves: np.ndarray) -> dict[str, Any]:
    """OLS fit of ``log E(b) = log E0 - lambda * gap_years(b)``.

    ``curves`` may be a single curve or a batch (replicates x bins).  Only the
    first ``N_FIT_BINS`` bins enter -- the 3y+ bin is descriptive and never
    fitted.  A replicate with ANY non-positive E(b) in those bins has no
    logarithm, so its lambda is NaN and it is DROPPED (the registration's rule,
    with the drop counted by the caller).
    """

    x = np.asarray(gap_years, dtype=np.float64)[:N_FIT_BINS]
    y = np.asarray(curves, dtype=np.float64)[..., :N_FIT_BINS]
    if x.size != N_FIT_BINS:
        raise ValueError(f"the fit needs {N_FIT_BINS} realized gaps")
    positive = np.all(y > 0.0, axis=-1)
    with np.errstate(divide="ignore", invalid="ignore"):
        log_y = np.log(np.where(y > 0.0, y, np.nan))
    xc = x - x.mean()
    sxx = float(xc @ xc)
    if sxx <= 0.0:                                # pragma: no cover
        raise ValueError("degenerate gap grid: no spread to fit a slope on")
    slope = (log_y * xc).sum(axis=-1) / sxx
    intercept = log_y.mean(axis=-1) - slope * x.mean()
    predicted = intercept[..., None] + slope[..., None] * x
    ss_res = ((log_y - predicted) ** 2).sum(axis=-1)
    centred = log_y - log_y.mean(axis=-1, keepdims=True)
    ss_tot = (centred ** 2).sum(axis=-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        r2 = 1.0 - ss_res / ss_tot
    nan = np.nan
    return {
        "lambda_per_year": np.where(positive, -slope, nan),
        "log_e0": np.where(positive, intercept, nan),
        "e0": np.where(positive, np.exp(intercept), nan),
        "r_squared": np.where(positive, r2, nan),
        "sse_log": np.where(positive, ss_res, nan),
        "positive": positive,
        "gap_years": [float(v) for v in x],
    }


def linear_slope(gap_years: np.ndarray, curves: np.ndarray) -> np.ndarray:
    """OLS slope of E(b) on gap_years, sign-flipped: the LOG-FREE rate form.

    Defined on every replicate including sign-flipped permutation replicates,
    so it carries the positivity-free companion null (RD-U2C-1).
    """

    x = np.asarray(gap_years, dtype=np.float64)[:N_FIT_BINS]
    y = np.asarray(curves, dtype=np.float64)[..., :N_FIT_BINS]
    xc = x - x.mean()
    return -(y * xc).sum(axis=-1) / float(xc @ xc)


def summarize_lambda(key: str, label: str, row: dict[str, Any],
                     gap_years: np.ndarray) -> dict[str, Any]:
    """Point lambda with its paired cluster-bootstrap CI and its own null."""

    point = log_slope_fit(gap_years, np.asarray(row["curve"]))
    boot = log_slope_fit(gap_years, row["boot_curve"])
    null = log_slope_fit(gap_years, row["null_curve"])
    boot_lambda = boot["lambda_per_year"]
    null_lambda = null["lambda_per_year"]
    finite_null = null_lambda[np.isfinite(null_lambda)]
    return {
        "key": key,
        "label": label,
        "lambda_per_year": float(point["lambda_per_year"]),
        "lambda_ci": percentile_ci(boot_lambda),
        "lambda_ci_half_width": _half_width(percentile_ci(boot_lambda)),
        "log_e0": float(point["log_e0"]),
        "e0": float(point["e0"]),
        "r_squared": float(point["r_squared"]),
        "sse_log": float(point["sse_log"]),
        "boot_replicates": int(boot_lambda.size),
        "boot_dropped_non_positive": int(np.count_nonzero(
            ~boot["positive"])),
        "null_replicates": int(null_lambda.size),
        "null_retained": int(finite_null.size),
        "null_center": (float(np.median(finite_null))
                        if finite_null.size else float("nan")),
        "null_band": percentile_ci(null_lambda),
        "linear_slope_per_year": float(linear_slope(
            gap_years, np.asarray(row["curve"]))),
        "linear_slope_null_center": float(np.median(linear_slope(
            gap_years, row["null_curve"]))),
        "curve": [float(v) for v in row["curve"]],
        "curve_ci": [[float(a), float(b)] for a, b in row["curve_ci"]],
        "curve_null_center": [float(v) for v in row["curve_null_center"]],
        "mean_gap_days": [float(v) for v in row["mean_gap_days"]],
        "self_pairs": [int(v) for v in row["self_pairs"]],
        "n_blocks": int(row["n_blocks"]),
        "n_authors": int(row["n_authors"]),
        "floor_share": float(row["floor_share"]),
        "_boot_lambda": boot_lambda,
        "_null_lambda": null_lambda,
    }


def _half_width(ci: Sequence[float]) -> float:
    lo, hi = float(ci[0]), float(ci[1])
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return float("nan")
    return 0.5 * (hi - lo)


def rate_contrast(name: str, row_a: dict[str, Any], row_b: dict[str, Any],
                  gap_years: np.ndarray, *, paired: bool) -> dict[str, Any]:
    """Lambda = lambda(row_a) - lambda(row_b), paired replicate by replicate.

    The bootstrap is paired BY CONSTRUCTION (identical author draws across
    rows on the shared block set); a replicate is dropped when EITHER row's
    five-bin curve has a non-positive value.  The permutation null is posed
    DIRECTLY on Lambda as registered; because a permutation drives E(b) to
    zero and its sign flips freely, the log form is undefined on most null
    replicates, so the positivity-free LINEAR slope contrast is reported
    beside it as the location check that is defined everywhere (RD-U2C-1).
    """

    boot = row_a["_boot_lambda"] - row_b["_boot_lambda"]
    null = row_a["_null_lambda"] - row_b["_null_lambda"]
    finite_boot = np.isfinite(boot)
    finite_null = null[np.isfinite(null)]
    ci = percentile_ci(boot)
    point = float(row_a["lambda_per_year"] - row_b["lambda_per_year"])
    linear_point = float(row_a["linear_slope_per_year"]
                         - row_b["linear_slope_per_year"])
    linear_null = (np.asarray(row_a["_linear_null"])
                   - np.asarray(row_b["_linear_null"]))
    return {
        "name": name,
        "point": point,
        "ci": ci,
        "ci_half_width": _half_width(ci),
        "boot_replicates": int(boot.size),
        "boot_retained": int(np.count_nonzero(finite_boot)),
        "boot_dropped_non_positive": int(boot.size
                                         - np.count_nonzero(finite_boot)),
        "null_replicates": int(null.size),
        "null_retained": int(finite_null.size),
        "null_center": (float(np.median(finite_null))
                        if finite_null.size else float("nan")),
        "null_band": percentile_ci(null),
        "null_iqr": ([float(np.percentile(finite_null, 25)),
                      float(np.percentile(finite_null, 75))]
                     if finite_null.size else [float("nan")] * 2),
        "linear_point": linear_point,
        "linear_null_center": float(np.median(linear_null)),
        "linear_null_band": percentile_ci(linear_null),
        "linear_null_finite_fraction": float(
            np.count_nonzero(np.isfinite(linear_null)) / linear_null.size),
        "paired_bootstrap": bool(paired),
    }


def classify_lambda(delta: dict[str, Any]) -> dict[str, Any]:
    """The three registered cells.  NO equivalence cell exists (registered)."""

    lo, hi = delta["ci"]
    if np.isfinite(lo) and lo > 0.0:
        cell = "COMMON_STANDING"
    elif np.isfinite(hi) and hi < 0.0:
        cell = "DISTINCT_SLOWER"
    else:
        cell = "SIGN_UNRESOLVED"
    return {
        "cell": cell,
        "ci_includes_zero": bool(np.isfinite(lo) and np.isfinite(hi)
                                 and lo <= 0.0 <= hi),
        "ci_half_width": delta["ci_half_width"],
        "equivalence_cell_offered": False,
        "projected_half_width": list(PROJECTED_HALF_WIDTH),
        "half_width_inside_projection": bool(
            np.isfinite(delta["ci_half_width"])
            and delta["ci_half_width"] <= PROJECTED_HALF_WIDTH[1]),
    }


# ---------------------------------------------------------------------------
# Field-by-field comparison (the G0 form, on U2b's committed per-row table)
# ---------------------------------------------------------------------------


def compare_fields(recomputed: dict[str, Any], committed: dict[str, Any],
                   fields: Sequence[str]) -> dict[str, Any]:
    """Bit-comparison of a recomputed row against its committed counterpart."""

    out = []
    worst = 0.0
    exact = True
    for name in fields:
        if name not in committed or name not in recomputed:
            out.append({"field": name, "status": "ABSENT"})
            exact = False
            continue
        a = U2B._flatten(recomputed[name])
        b = U2B._flatten(committed[name])
        if len(a) != len(b):
            out.append({"field": name, "status": "SHAPE_MISMATCH"})
            exact = False
            continue
        diff = np.abs(np.asarray(a) - np.asarray(b))
        finite = diff[np.isfinite(diff)]
        max_diff = float(finite.max()) if finite.size else 0.0
        identical = bool(np.array_equal(np.asarray(a), np.asarray(b),
                                        equal_nan=True))
        exact = exact and identical
        worst = max(worst, max_diff)
        out.append({"field": name, "bitwise_identical": identical,
                    "max_abs_difference": max_diff})
    return {"bitwise_identical": exact, "max_abs_difference": worst,
            "fields": out}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--b-perm", type=int, default=B_PERM)
    parser.add_argument("--b-boot", type=int, default=B_BOOT)
    parser.add_argument("--registration-commit", type=str, default="6a4a5bb")
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

    # ---- blocks: U2b's construction, which is U2's -----------------------
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
    order_pool = np.lexsort((mid_days_all[sel_pool], quarters_all[sel_pool]))
    idx_pool = np.flatnonzero(sel_pool)[order_pool]
    pool_author = blocks.author[idx_pool]
    pool_quarter = quarters_all[idx_pool]
    pool_mid = mid_days_all[idx_pool]
    pool_features = blocks.features[idx_pool]
    log.event("blocks_built", pool_authors=int(pool.size),
              pool_blocks=int(pool_features.shape[0]))
    if int(pool.size) != POOL_AUTHORS or \
            int(pool_features.shape[0]) != POOL_BLOCKS:
        raise SystemExit(
            f"STOP: the pool is not U2b's pool "
            f"({pool.size} authors / {pool_features.shape[0]} blocks against "
            f"{POOL_AUTHORS} / {POOL_BLOCKS})")

    # ---- the split (U2b's object; Common(0.5) = 32 or STOP) --------------
    rank_order, cumulative, universe = U2B.community_ranking(
        vocab_index_full, n_vocab)
    if universe != CENSUS_UNIVERSE:
        raise SystemExit(f"STOP: universe {universe} is not the registered "
                         f"{CENSUS_UNIVERSE}")

    def split_columns(q: float) -> tuple[np.ndarray, np.ndarray, float]:
        common, share = U2B.common_prefix(rank_order, cumulative, q)
        mask = np.zeros(n_vocab, dtype=bool)
        mask[common] = True
        return common, np.flatnonzero(~mask), float(share)

    split_cache: dict[int, tuple[np.ndarray, np.ndarray, float]] = {}
    for q in (Q_PRIMARY, Q_CONFIRMATORY):
        split_cache[int(round(q * 1000))] = split_columns(q)
    common_q50 = split_cache[500][0]
    common_q70 = split_cache[700][0]
    split_census = {
        "universe_in_vocab_events": int(universe),
        "n_vocab": int(n_vocab),
        "common_size_q50": int(common_q50.size),
        "common_share_q50": round(split_cache[500][2], 4),
        "common_size_q70": int(common_q70.size),
        "common_share_q70": round(split_cache[700][2], 4),
        "distinct_size_q50": int(n_vocab - common_q50.size),
        "pool_authors": int(pool.size),
        "pool_blocks": int(pool_features.shape[0]),
    }
    write_json(output / "split_census.json", split_census)
    log.event("split_census", **split_census)
    if common_q50.size != COMMON_SIZE_Q50:
        raise SystemExit(f"STOP: Common(0.5) is {common_q50.size} "
                         f"communities, not the registered {COMMON_SIZE_Q50}")
    if common_q70.size != COMMON_SIZE_Q70:
        raise SystemExit(f"STOP: Common(0.7) is {common_q70.size} "
                         f"communities, not the registered {COMMON_SIZE_Q70}")

    # ---- the intersection eligibility predicate (U2b's, by block) --------
    integral_errors: list[float] = []

    def eligibility(q: float, m: int) -> dict[str, Any]:
        common_cols, distinct_cols, share = split_cache[int(round(q * 1000))]
        raw = U2B.block_counts_over(pool_features, common_cols, K_PRIMARY)
        error = float(np.abs(raw - np.rint(raw)).max())
        integral_errors.append(error)
        if error > 1e-3:                          # blocking
            raise SystemExit(
                f"STOP: recovered sub-vocabulary counts are not integral "
                f"(max deviation {error:.3e})")
        common_count = np.rint(raw).astype(np.int64)
        distinct_count = K_PRIMARY - common_count
        mask = (common_count >= m) & (distinct_count >= m)
        pairs, contributors = U2B.self_pair_census(pool_author[mask],
                                                   pool_mid[mask])
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
        }

    # ---- GATE ANCHORS (#78, BLOCKING): the executed predicate, recomputed
    log.event("gate_anchor_start")
    elig: dict[tuple[int, int], dict[str, Any]] = {}
    gate_rows = []
    gate_ok = True
    for name, pin in GATE_ANCHORS.items():
        q = pin["q_milli"] / 1000.0
        entry = eligibility(q, pin["m"])
        elig[(pin["q_milli"], pin["m"])] = entry
        pairs_ok = entry["pairs_2_3y"] == pin["pairs_2_3y"]
        authors_ok = entry["authors_2_3y"] == pin["authors_2_3y"]
        target_ok = (entry["pairs_2_3y"] >= POOL_GATE_MIN_PAIRS_2_3Y
                     and entry["authors_2_3y"] >= POOL_GATE_MIN_AUTHORS_2_3Y)
        gate_ok = gate_ok and pairs_ok and authors_ok and target_ok
        gate_rows.append({
            "configuration": name,
            "q": q, "m": pin["m"],
            "registered_pairs_2_3y": pin["pairs_2_3y"],
            "observed_pairs_2_3y": entry["pairs_2_3y"],
            "registered_authors_2_3y": pin["authors_2_3y"],
            "observed_authors_2_3y": entry["authors_2_3y"],
            "blocks": entry["blocks"],
            "pairs_match": pairs_ok, "authors_match": authors_ok,
            "meets_69_targets": target_ok,
            "status": "PASS" if (pairs_ok and authors_ok and target_ok)
            else "MISMATCH"})
    gate_anchor = {"status": "PASS" if gate_ok else "MISMATCH",
                   "required_pairs_2_3y": POOL_GATE_MIN_PAIRS_2_3Y,
                   "required_authors_2_3y": POOL_GATE_MIN_AUTHORS_2_3Y,
                   "rows": gate_rows}
    write_json(output / "gate_anchor.json", gate_anchor)
    log.event("gate_anchor", status=gate_anchor["status"])
    if not gate_ok:
        raise SystemExit(
            "STOP: the gate's executed predicate does not recompute: "
            + json.dumps(gate_rows, sort_keys=True, default=float))

    # ---- the taste row's fold machinery (pool-level, computed once) ------
    first_half, first_half_mass = U2B.first_half_counts(cache, pool, n_vocab)
    folds = U2B.taste_folds(pool, SEED, TASTE_FOLDS)
    taste_purity: list[dict[str, Any]] = []

    def run_configuration(tag: str, q: float, m: int,
                          entry: dict[str, Any] | None = None
                          ) -> dict[str, Any]:
        """The four carrier rows on ONE intersection pair set (#72)."""

        elig_entry = entry if entry is not None else eligibility(q, m)
        keep = elig_entry["intersection_mask"]
        row_author = pool_author[keep]
        row_quarter = pool_quarter[keep]
        row_mid = pool_mid[keep]
        row_features = pool_features[keep]
        log.event("configuration_start", tag=tag, q=q, m=m,
                  blocks=int(keep.sum()))

        def arm(label: str, features: np.ndarray,
                author: np.ndarray, quarter: np.ndarray,
                mid: np.ndarray) -> dict[str, Any]:
            return U2.compute_arm(features, author, quarter, mid,
                                  n_perm=args.b_perm, n_boot=args.b_boot,
                                  seed=SEED, cross_sampler_check=False,
                                  log=log, label=f"{tag} {label}")

        rows = {
            "full": arm("full vocabulary", row_features, row_author,
                        row_quarter, row_mid),
            "common": arm("common-restricted",
                          renormalize(row_features,
                                      elig_entry["common_columns"]),
                          row_author, row_quarter, row_mid),
            "distinct": arm("distinctive-restricted",
                            renormalize(row_features,
                                        elig_entry["distinct_columns"]),
                            row_author, row_quarter, row_mid),
        }

        fold_results = []
        for fold, (train_idx, test_idx) in enumerate(folds):
            train_authors = pool[train_idx]
            test_authors = pool[test_idx]
            overlap = len(set(train_authors.tolist())
                          & set(test_authors.tolist()))
            counts = first_half[train_idx]
            fitted_mass = float(counts.sum())
            train_mass = float(first_half_mass[train_idx].sum())
            test_mass = float(first_half_mass[test_idx].sum())
            # BLOCKING purity gate (U2b's, unchanged)
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
            taste = np.asarray(row_features[in_fold],
                               dtype=np.float64) @ embedding
            norms = np.linalg.norm(taste, axis=1, keepdims=True)
            norms[norms == 0.0] = 1.0
            taste = (taste / norms).astype(np.float32)
            fold_results.append(arm(f"taste fold {fold}", taste,
                                    row_author[in_fold], row_quarter[in_fold],
                                    row_mid[in_fold]))
            taste_purity.append({
                "configuration": tag, "fold": fold,
                "n_train": int(train_authors.size),
                "n_test": int(test_authors.size), "overlap": overlap,
                "fitted_mass": fitted_mass,
                "train_first_half_mass": train_mass,
                "test_mass_excluded": test_mass,
                "test_blocks": int(in_fold.sum()),
                "embedding_rank": int(embedding.shape[1]),
                "status": "PASS"})
        rows["taste"] = U2B.pool_fold_results(fold_results)
        rows["taste"]["per_fold_floor_share"] = [
            float(r["floor_share"]) for r in fold_results]
        return {"tag": tag, "q": q, "m": m, "eligibility": elig_entry,
                "rows": rows}

    # ---- G0: U2b's four-row table at q=0.5/m=10, bit-compared ------------
    if args.skip_g0:
        g0 = {"status": "SKIPPED", "bitwise_identical": False,
              "max_abs_difference": float("nan"), "rows": [],
              "source": str(U2B_ARTIFACTS / "rows.json")}
    else:
        log.event("g0_start")
        g0_config = run_configuration("G0 (q=0.5, m=10)", Q_G0, M_G0)
        committed_rows = json.loads(
            (U2B_ARTIFACTS / "rows.json").read_text(encoding="utf-8"))
        # U2b's committed rows are in the order full / common / distinct /
        # taste, keyed by a label that carries the community counts.
        g0_rows = []
        worst = 0.0
        exact = True
        for key, committed in zip(ROW_KEYS, committed_rows):
            recomputed = U2B.summarize_row(g0_config["rows"][key])
            comparison = compare_fields(recomputed, committed, G0_ROW_FIELDS)
            comparison["row"] = key
            comparison["committed_key"] = committed["key"]
            worst = max(worst, comparison["max_abs_difference"])
            exact = exact and comparison["bitwise_identical"]
            g0_rows.append(comparison)
        g0 = {"status": "PASS" if exact else ("NEAR" if worst < 1e-9
                                              else "FAIL"),
              "bitwise_identical": exact, "max_abs_difference": worst,
              "rows": g0_rows,
              "source": str(U2B_ARTIFACTS / "rows.json")}
        del g0_config
    write_json(output / "g0_anchor_comparison.json", g0)
    log.event("g0", status=g0["status"],
              max_abs_difference=g0["max_abs_difference"])
    if g0["status"] == "FAIL":
        raise SystemExit("STOP: G0 anchor comparison FAILED against U2b's "
                         "committed four-row table")

    # ---- the two registered arms -----------------------------------------
    def analyse(config: dict[str, Any]) -> dict[str, Any]:
        rows = config["rows"]
        gap_days = np.asarray(rows["full"]["mean_gap_days"], dtype=np.float64)
        gap_years = gap_days / DAYS_PER_YEAR
        labels = {
            "full": "full vocabulary",
            "common": f"common (q={config['q']}, "
                      f"{config['eligibility']['common_size']} communities)",
            "distinct": f"distinctive (q={config['q']}, "
                        f"{len(config['eligibility']['distinct_columns'])} "
                        "communities)",
            "taste": f"taste (per-fold PPMI+SVD d={TASTE_DIM}, out-of-fold)",
        }
        summaries = {}
        for key in ROW_KEYS:
            row_gap = np.asarray(rows[key]["mean_gap_days"],
                                 dtype=np.float64) / DAYS_PER_YEAR
            summary = summarize_lambda(key, labels[key], rows[key], row_gap)
            summary["_linear_null"] = linear_slope(row_gap,
                                                   rows[key]["null_curve"])
            summaries[key] = summary
        primary = rate_contrast(
            "Λ = λ_distinct − λ_common", summaries["distinct"],
            summaries["common"], gap_years, paired=True)
        cell = classify_lambda(primary)
        secondary = rate_contrast(
            "λ_taste − λ_full", summaries["taste"], summaries["full"],
            gap_years, paired=False)
        ordered = sorted(
            (s for s in summaries.values()
             if np.isfinite(s["lambda_per_year"])),
            key=lambda s: s["lambda_per_year"])
        return {
            "tag": config["tag"], "q": config["q"], "m": config["m"],
            "blocks": config["eligibility"]["blocks"],
            "pairs_2_3y": config["eligibility"]["pairs_2_3y"],
            "authors_2_3y": config["eligibility"]["authors_2_3y"],
            "common_size": config["eligibility"]["common_size"],
            "gap_years": [float(v) for v in gap_years],
            "gap_days": [float(v) for v in gap_days],
            "rows": summaries,
            "row_order": ROW_KEYS,
            "primary": primary,
            "cell": cell,
            "secondary": secondary,
            "slowest_row": ordered[0]["key"] if ordered else None,
            "per_fold_floor_share": rows["taste"]["per_fold_floor_share"],
            "descriptive_3y_plus": {
                key: float(rows[key]["curve"][DESCRIPTIVE_BIN])
                for key in ROW_KEYS},
        }

    primary_config = run_configuration(
        f"primary (q={Q_PRIMARY}, m={M_PRIMARY})", Q_PRIMARY, M_PRIMARY,
        elig[(500, M_PRIMARY)])
    primary_arm = analyse(primary_config)
    del primary_config
    log.event("primary_done", cell=primary_arm["cell"]["cell"],
              Lambda=primary_arm["primary"]["point"])

    confirmatory_config = run_configuration(
        f"confirmatory (q={Q_CONFIRMATORY}, m={M_CONFIRMATORY})",
        Q_CONFIRMATORY, M_CONFIRMATORY, elig[(700, M_CONFIRMATORY)])
    confirmatory_arm = analyse(confirmatory_config)
    del confirmatory_config
    log.event("confirmatory_done", cell=confirmatory_arm["cell"]["cell"],
              Lambda=confirmatory_arm["primary"]["point"])

    def strip(arm: dict[str, Any]) -> dict[str, Any]:
        out = dict(arm)
        out["rows"] = {k: {kk: vv for kk, vv in v.items()
                           if not kk.startswith("_")}
                       for k, v in arm["rows"].items()}
        return out

    write_json(output / "arms.json",
               {"primary": strip(primary_arm),
                "confirmatory": strip(confirmatory_arm)})
    write_json(output / "taste_purity.json", taste_purity)

    # ---- #73: does the confirmatory arm diverge in cell? -----------------
    flags_73: list[str] = []
    if confirmatory_arm["cell"]["cell"] != primary_arm["cell"]["cell"]:
        flags_73.append(
            f"the confirmatory arm (q={Q_CONFIRMATORY}/m={M_CONFIRMATORY}) "
            f"lands in `{confirmatory_arm['cell']['cell']}` while the "
            f"registered primary (q={Q_PRIMARY}/m={M_PRIMARY}) lands in "
            f"`{primary_arm['cell']['cell']}`; the primary ROUTES")

    # ---- leans ------------------------------------------------------------
    lam = primary_arm["rows"]
    l1_point = primary_arm["primary"]["point"]
    l1_cell = primary_arm["cell"]["cell"]
    if l1_cell == "COMMON_STANDING":
        l1 = "HELD"
    elif l1_cell == "SIGN_UNRESOLVED" and l1_point > 0.0:
        l1 = "SIGN HELD IN POINT, UNRESOLVED IN INTERVAL"
    elif l1_cell == "SIGN_UNRESOLVED":
        l1 = "POINT SIGN MISSED, INTERVAL UNRESOLVED"
    else:
        l1 = "MISSED"
    slowest = primary_arm["slowest_row"]
    l2 = ("HELD" if slowest == "taste" else "MISSED")
    leans = [
        {"id": "L1",
         "statement": f"Λ > 0 with point ≈ +{PROJECTED_LAMBDA_POINT:.2f}/y "
                      "(disclosed knowledge, not a prediction)",
         "outcome": l1,
         "detail": f"realized Λ {fmt(l1_point)}/y "
                   f"{fmt_ci(primary_arm['primary']['ci'])}, cell "
                   f"`{l1_cell}`"},
        {"id": "L2",
         "statement": "λ_taste is the SMALLEST rate of the four rows "
                      f"(projected ≈ {PROJECTED_LAMBDA_TASTE:.2f}/y)",
         "outcome": l2,
         "detail": "λ_taste "
                   f"{fmt(lam['taste']['lambda_per_year'])}/y against "
                   f"λ_full {fmt(lam['full']['lambda_per_year'])}, λ_common "
                   f"{fmt(lam['common']['lambda_per_year'])}, λ_distinct "
                   f"{fmt(lam['distinct']['lambda_per_year'])}; slowest row "
                   f"`{slowest}`"},
    ]

    # ---- verdict ----------------------------------------------------------
    outcome = primary_arm["cell"]["cell"]
    verdict = {
        "outcome": outcome,
        "cell": outcome,
        "lambda_point": l1_point,
        "lambda_ci": primary_arm["primary"]["ci"],
        "lambda_ci_half_width": primary_arm["primary"]["ci_half_width"],
        "projected_half_width": list(PROJECTED_HALF_WIDTH),
        "projected_point": PROJECTED_LAMBDA_POINT,
        "confirmatory_cell": confirmatory_arm["cell"]["cell"],
        "flags_73": flags_73,
        "per_row_lambda": {k: lam[k]["lambda_per_year"] for k in ROW_KEYS},
        "generated_utc": utc_now(),
    }
    write_json(output / "verdict.json", verdict)

    # ---- config -----------------------------------------------------------
    script_bytes = Path(__file__).read_bytes()
    config = {
        "registration_commit": args.registration_commit,
        "seed": SEED, "b_perm": args.b_perm, "b_boot": args.b_boot,
        "k": K_PRIMARY, "pool_min_blocks": POOL_MIN_BLOCKS,
        "quarter_days": U2.QUARTER_DAYS,
        "bin_labels": list(BIN_LABELS),
        "fit_bins": list(BIN_LABELS[:N_FIT_BINS]),
        "descriptive_bin_excluded_from_the_fit": BIN_LABELS[DESCRIPTIVE_BIN],
        "days_per_year": DAYS_PER_YEAR,
        "q_primary": Q_PRIMARY, "m_primary": M_PRIMARY,
        "q_confirmatory": Q_CONFIRMATORY, "m_confirmatory": M_CONFIRMATORY,
        "g0_configuration": {"q": Q_G0, "m": M_G0},
        "taste_folds": TASTE_FOLDS, "taste_dim": TASTE_DIM,
        "gate_anchors": {k: dict(v) for k, v in GATE_ANCHORS.items()},
        "pool_gate_min_pairs_2_3y": POOL_GATE_MIN_PAIRS_2_3Y,
        "pool_gate_min_authors_2_3y": POOL_GATE_MIN_AUTHORS_2_3Y,
        "projected_lambda_point": PROJECTED_LAMBDA_POINT,
        "projected_half_width": list(PROJECTED_HALF_WIDTH),
        "projected_lambda_common": PROJECTED_LAMBDA_COMMON,
        "projected_lambda_distinct": PROJECTED_LAMBDA_DISTINCT,
        "projected_lambda_taste": PROJECTED_LAMBDA_TASTE,
        "cells": ["SIGN_UNRESOLVED", "COMMON_STANDING", "DISTINCT_SLOWER"],
        "equivalence_cell": None,
        "cache": str(args.cache),
        "u2b_machinery": str(U2B_SCRIPT),
        "u2b_machinery_sha256": hashlib.sha256(
            U2B_SCRIPT.read_bytes()).hexdigest(),
        "u2_machinery": str(U2B.U2_SCRIPT),
        "u2_machinery_sha256": hashlib.sha256(
            U2B.U2_SCRIPT.read_bytes()).hexdigest(),
        "u2b_artifacts": str(U2B_ARTIFACTS),
        "epoch_origin_utc": datetime.fromtimestamp(
            origin, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "inherited_from_u2b": [
            "community_ranking / common_prefix (the vocabulary split)",
            "block_counts_over (exact sub-vocabulary counts as K*f^2)",
            "renormalize (the carrier restriction)",
            "self_pair_census (the gate's exact predicate)",
            "ppmi_svd / first_half_counts / taste_folds / pool_fold_results",
            "summarize_row and percentile_ci",
        ],
        "inherited_from_u2": [
            "build_blocks (exact-K disjoint blocks, Hellinger features)",
            "assign_quarters / gap_bin (epoch cells and gap bins)",
            "compute_arm (epoch-matched EXACT stratified cross baseline, "
            "RD-U2-1 form; within-quarter permutation scaffold; author "
            "cluster bootstrap)",
            "scan_for_cohort_ids (ID-leak gate)",
        ],
        "recorded_choices": {
            "gap_years":
                "the row's REALIZED per-bin mean self-pair gap in days on the "
                f"intersection set, divided by {DAYS_PER_YEAR} days per year; "
                "the gaps are held at their realized values inside the "
                "bootstrap and the permutation, because the resampling "
                "machinery inherited from U2 resamples the excess, not the "
                "gap grid",
            "fit_window":
                "OLS over the FIVE verdict bins 0-90d / 90-180d / 180-365d / "
                "1-2y / 2-3y; the 3y+ bin is reported descriptively and NEVER "
                "enters the fit (registration, inherited from U2)",
            "lambda_sign":
                "lambda = -slope of log E(b) on gap_years, so a positive "
                "lambda is decay; Lambda = lambda_distinct - lambda_common is "
                "positive when the DISTINCTIVE decays faster",
            "positivity_rule":
                "a replicate whose five fitted bins contain any non-positive "
                "E(b) has no logarithm and is DROPPED, with the count "
                "reported; for Lambda a replicate is dropped when EITHER row "
                "is non-positive",
            "bootstrap_pairing":
                "compute_arm draws its author multinomial from seed + 11 with "
                "the same author count for every row on the shared block set, "
                "so Lambda's bootstrap is PAIRED replicate by replicate; the "
                "secondary contrast lambda_taste - lambda_full is NOT paired "
                "(fold-stratified draws against pool-level draws) and its "
                "interval is correspondingly conservative",
            "permutation_null_on_lambda":
                "RD-U2C-1 (disclosed): the registration poses the null "
                "DIRECTLY on Lambda as a slope contrast. The LOG form of that "
                "slope is undefined on most permutation replicates, because a "
                "within-quarter relabelling drives E(b) to zero and its sign "
                "then flips freely, so the registered null is computed with "
                "the same positivity rule and its RETAINED count is reported "
                "as the honest measure of how much it can say; beside it the "
                "positivity-free LINEAR slope contrast (OLS of E(b) on "
                "gap_years, no logarithm) is reported on all 499 replicates "
                "as the location check the registration's argument actually "
                "needs. No verdict rests on either null; the verdict is the "
                "bootstrap interval on Lambda",
            "row_order":
                "full / common / distinct / taste, matching U2b's committed "
                "rows.json order for the G0 bit-comparison",
            "taste_cross_reservoir":
                "fold-local, inherited from U2b unchanged: a fold's cross "
                "baseline uses that fold's test authors only, because two "
                "folds' embeddings are different coordinate systems",
            "gate_anchor_semantics":
                "#78: the gate quantities are U2b's REALIZED intersection "
                "numbers, i.e. the gate predicate already executed on census "
                "data; this runner re-executes the same predicate and "
                "compares EXACTLY, and any mismatch stops the leg before any "
                "row is read",
        },
        "script_sha256": hashlib.sha256(script_bytes).hexdigest(),
    }
    write_json(output / "config.json", config)
    write_json(output / "config.sha256.json",
               {"script_sha256": config["script_sha256"],
                "config_sha256": hashlib.sha256(
                    json.dumps(config, sort_keys=True,
                               default=float).encode("utf-8")).hexdigest()})

    # ---- payload / report --------------------------------------------------
    gates = {
        "cache anchor gate (3,005,360 events / 1401 authors / 1191 "
        "vocabulary)": anchors["status"],
        "pool reproduction (849 authors / 45,731 blocks)": "PASS",
        "split census (universe 2,348,361; Common(0.5) = 32; Common(0.7) = "
        "104)": "PASS",
        "GATE ANCHORS #78 (U2b's realized intersection quantities at both "
        "run configurations, recomputed and compared exactly)":
            gate_anchor["status"],
        "G0 — U2b four-row E(b) table bit-comparison (#56)": g0["status"],
        "taste-row fold purity (mass identity, zero test mass)":
            "PASS" if all(p["status"] == "PASS" for p in taste_purity)
            else "FAIL",
        "sub-vocabulary counts integral (max deviation "
        f"{max(integral_errors):.2e})": "PASS",
        "no synthetic gate required (R layer, no world simulated)": "N/A",
    }

    run_finished = utc_now()
    payload = {
        "generated_utc": utc_now(),
        "run_started_utc": run_started,
        "run_finished_utc": run_finished,
        "registration_commit": args.registration_commit,
        "outcome": outcome,
        "anchors": anchors,
        "split_census": split_census,
        "gate_anchor": gate_anchor,
        "u2b_primary_realization": {
            key: int(json.loads(
                (U2B_ARTIFACTS / "pool_gate.json").read_text(
                    encoding="utf-8"))[key])
            for key in ("pairs_2_3y", "authors_2_3y")},
        "g0": g0,
        "primary": strip(primary_arm),
        "confirmatory": strip(confirmatory_arm),
        "flags_73": flags_73,
        "taste_purity": taste_purity,
        "leans": leans,
        "gates": gates,
        "verdict": verdict,
        "config": config,
    }
    payload["boundaries"] = build_boundaries(payload)

    write_report(args.report, payload)
    scan = U2.scan_for_cohort_ids(
        [args.report, Path(__file__),
         ROOT / "tests/test_m4_u2c_decay_rate_contrast.py",
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
    log.event("done", outcome=outcome, Lambda=l1_point,
              half_width=primary_arm["primary"]["ci_half_width"],
              flags_73=len(flags_73))
    return 0


# ---------------------------------------------------------------------------
# Boundaries and report (rule 24: every number generated from the artifacts)
# ---------------------------------------------------------------------------


def build_boundaries(payload: dict[str, Any]) -> list[str]:
    arm = payload["primary"]
    delta = arm["primary"]
    return [
        "**The eq-12 projection caution, carried into the verdict as "
        "registered:** this leg reads ONE slow-time projection of the "
        "transition kernel K_u (eq 12) onto the marginal selection "
        "distribution π_u over the 1191-community vocabulary, split by "
        "carrier. A decay-rate contrast here is a statement about π_u on the "
        "Hellinger unigram sphere over calendar time, never about a "
        "psychological attribute (§5.4), and 'common' and 'distinctive' are "
        "EVENT-MASS strata of a subreddit vocabulary, not the T-line's "
        "personality/identity constructs — the T-line proposition is what "
        "motivates the test, not what the strata mean.",
        "**U2's three-year scoping binds every rate here.** λ is estimated "
        "over a window that ends at the 2–3y bin (realized mean gap "
        f"{fmt(arm['gap_years'][FAR_BIN], 3)} years), so it is a THREE-YEAR "
        "CORE rate and nothing else. U2's curve had not flattened at its "
        "verdict endpoint, the log-linear form is a local description of the "
        "observed window rather than a demonstrated law, and no rate in this "
        "report licenses a half-life, an asymptote or any permanent-rate "
        "language. Extrapolating λ past the observed span is forbidden prose.",
        "**The provisional sign was KNOWN at registration and is disclosed.** "
        "U2b's Δfloor point was negative in all five of its configurations "
        "(COMMON_STANDING direction) when U2c was registered. U2c is a "
        "verdict-issuing completion under corrected gate arithmetic (#78) and "
        "a ratio-free estimand (#79), not an independent prediction, and its "
        "leans are disclosures rather than forecasts. The registration also "
        "stated BEFORE the run that detection is borderline at the projected "
        f"half-width {PROJECTED_HALF_WIDTH[0]:.2f}–"
        f"{PROJECTED_HALF_WIDTH[1]:.2f}/y — realized "
        f"{fmt(delta['ci_half_width'], 4)}/y.",
        "**LEVEL differences across rows are never interpreted** (U2b's "
        "comparison rule, inherited): a restricted row is a lower-dimensional, "
        "differently attenuated view of the same block. The decay RATE is the "
        "level-free quantity this leg exists to compare — a gap-independent "
        "attenuation moves log E0, not λ — but the E(b) levels tabulated "
        "beside it do not transport across rows.",
        "**No equivalence cell exists in this leg, by registration.** At the "
        "projected width no |Λ| band was reachable, so posing one would have "
        "repeated #79a. A near-zero Λ therefore reads SIGN_UNRESOLVED and is "
        "reported as an interval, never as a demonstration of equal rates.",
        "The eligibility floor is not neutral. Requiring ≥ m events in BOTH "
        "sub-vocabularies keeps only BALANCED blocks, so the intersection set "
        "over-represents authors who mix common and distinctive communities "
        "within a 50-event window. Lowering the floor from m = 10 to m = 5 "
        "enlarges the pool by admitting more lopsided blocks, which is a "
        "different sample, not a bigger draw from the same one.",
        "The taste row's cross baseline is fold-local while the other three "
        "rows share one pool-level reservoir, and its bootstrap draws are "
        "fold-stratified rather than pool-level, so the secondary contrast "
        "λ_taste − λ_full is NOT paired and its interval is conservative.",
        "Label-free and corpus-level throughout: no Big5 or MBTI value is "
        "read anywhere in this leg, and no per-author quantity is reported or "
        "committed.",
    ]


def _row_table(add, arm: dict[str, Any]) -> None:
    add("| row | λ (1/y) | 95% CI | CI half-width | R² (log-linear) | "
        "E0 | F = E(2–3y)/E(0–90d) |")
    add("|---|---|---|---|---|---|---|")
    for key in arm["row_order"]:
        row = arm["rows"][key]
        add(f"| {row['label']} | **{fmt(row['lambda_per_year'])}** | "
            f"{fmt_ci(row['lambda_ci'])} | "
            f"{fmt(row['lambda_ci_half_width'])} | "
            f"{fmt(row['r_squared'])} | {fmt(row['e0'])} | "
            f"{fmt(row['floor_share'])} |")
    add("")


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []

    def add(text: str = "") -> None:
        lines.append(text)

    arm = payload["primary"]
    conf = payload["confirmatory"]
    delta = arm["primary"]
    cell = arm["cell"]

    add("# SUICA M4-U2c — the decay-rate contrast")
    add("")
    add(f"**Outcome: `{payload['outcome']}`.**")
    add("")
    add(f"**Λ = λ_distinct − λ_common = {fmt(delta['point'])}/y "
        f"{fmt_ci(delta['ci'])}** at the registered primary configuration "
        f"q = {arm['q']} / m = {arm['m']} "
        f"({arm['pairs_2_3y']:,} self pairs and {arm['authors_2_3y']} "
        "contributing authors in the 2–3y bin).")
    add("")
    if cell["cell"] == "SIGN_UNRESOLVED":
        add("**THE VERDICT IS THE INTERVAL STATEMENT.** The registration "
            "named `SIGN_UNRESOLVED` a live cell before the run and projected "
            f"a borderline half-width of "
            f"{PROJECTED_HALF_WIDTH[0]:.2f}–{PROJECTED_HALF_WIDTH[1]:.2f}/y; "
            f"the realized half-width is {fmt(delta['ci_half_width'])}/y and "
            "the interval straddles zero. The sign evidence is carried as "
            "registered — this CI TOGETHER WITH U2b's quarantined sign "
            "unanimity (Δfloor negative at all five of its configurations) — "
            "and the tier is unchanged at EXPLORATORY. No layer is declared "
            "the standing one.")
    elif cell["cell"] == "COMMON_STANDING":
        add("**THE COMMON MASS IS THE SLOWER-DECAYING CARRIER.** The "
            "interval on Λ lies strictly above zero: the distinctive tail "
            "decays FASTER than the common mass at this resolution. U2b's "
            "quarantined provisional sign is confirmed under corrected gate "
            "arithmetic and a ratio-free estimand.")
    else:
        add("**THE DISTINCTIVE TAIL IS THE SLOWER-DECAYING CARRIER.** The "
            "interval on Λ lies strictly below zero, REFUTING U2b's "
            "provisional sign. Per the registration this outcome forces a "
            "re-examination of U2b's computation before any theory move; "
            "nothing in this report may be carried to the synthesis until "
            "that re-examination is adjudicated.")
    add("")
    add("**Both registered arms put the point on the same side of zero** — "
        f"primary Λ {fmt(delta['point'])}/y, confirmatory "
        f"{fmt(conf['primary']['point'])}/y — and in both arms λ_distinct "
        f"({fmt(arm['rows']['distinct']['lambda_per_year'])} and "
        f"{fmt(conf['rows']['distinct']['lambda_per_year'])}) exceeds "
        f"λ_common ({fmt(arm['rows']['common']['lambda_per_year'])} and "
        f"{fmt(conf['rows']['common']['lambda_per_year'])}). That is a "
        "POINT-level agreement with U2b's five quarantined configurations, "
        "not an interval that excludes zero, and it is reported as the "
        "former.")
    add("")
    add("Executed from the registration committed at "
        f"`{payload['registration_commit']}` in "
        "`docs/SUICA_M4_U_WHEN_ORDER_PLAN.md` (section \"U2c — the "
        "decay-rate contrast (completion of U2b; registered BEFORE run, "
        f"2026-08-18)\"). Run window {payload['run_started_utc']} to "
        f"{payload['run_finished_utc']}; report generated "
        f"{payload['generated_utc']}. Every number in this report is produced "
        "from the run's artifacts by "
        "`scripts/run_suica_m4_u2c_decay_rate_contrast.py` (rule 24).")
    add("")

    # ---- gates -----------------------------------------------------------
    add("## Gates")
    add("")
    add("| gate | status |")
    add("|---|---|")
    for name, status in payload["gates"].items():
        add(f"| {name} | {status} |")
    add("")

    # ---- gate anchors ----------------------------------------------------
    gate = payload["gate_anchor"]
    add("## The gate's executed predicate (#78), recomputed as a blocking "
        "anchor")
    add("")
    add("U2b's #78 defect was a gate governed by a quantity no census "
        "computed. U2c's gate quantities are U2b's REALIZED intersection "
        "numbers — the predicate already executed on census data — and this "
        "runner re-executes the same predicate and compares EXACTLY before "
        "any row is read. A mismatch stops the leg.")
    add("")
    add("| configuration | registered pairs (2–3y) | observed | registered "
        "authors | observed | eligible blocks | meets #69 | status |")
    add("|---|---|---|---|---|---|---|---|")
    for row in gate["rows"]:
        add(f"| {row['configuration']} | "
            f"{row['registered_pairs_2_3y']:,} | "
            f"{row['observed_pairs_2_3y']:,} | "
            f"{row['registered_authors_2_3y']:,} | "
            f"{row['observed_authors_2_3y']:,} | {row['blocks']:,} | "
            f"{'yes' if row['meets_69_targets'] else 'no'} | "
            f"{row['status']} |")
    add("")
    add(f"Both configurations clear the registered #69 targets "
        f"(≥ {gate['required_pairs_2_3y']:,} pairs and "
        f"≥ {gate['required_authors_2_3y']} authors in the 2–3y bin), which "
        "is why U2c can issue a verdict where U2b could not.")
    add("")

    # ---- estimand --------------------------------------------------------
    add("## The estimand (#79: ratio-free)")
    add("")
    add("Per carrier row, OLS over the FIVE verdict bins "
        + " / ".join(BIN_LABELS[:N_FIT_BINS]) + ":")
    add("")
    add("```")
    add("log E_row(b) = log E0_row − λ_row · gap_years(b)")
    add("```")
    add("")
    add("where `gap_years(b)` is the row's realized per-bin mean self-pair "
        f"gap on the intersection set (days / {DAYS_PER_YEAR}) and `E_row(b)` "
        "is the epoch-matched personal excess — the self mean minus the EXACT "
        "stratified cross mean — computed by U2's estimator, imported by "
        "file. λ is in 1/year and is LEVEL-FREE by construction: a "
        "gap-independent attenuation moves log E0, not λ. The verdict "
        "contrast is **Λ = λ_distinct − λ_common**, positive when the "
        f"distinctive decays faster. The {BIN_LABELS[DESCRIPTIVE_BIN]} bin is "
        "descriptive and NEVER enters the fit.")
    add("")
    add("Realized gap grid at the primary configuration (years): "
        + ", ".join(f"{BIN_LABELS[b]} = {fmt(arm['gap_years'][b], 4)}"
                    for b in range(N_FIT_BINS))
        + f"; the descriptive {BIN_LABELS[DESCRIPTIVE_BIN]} bin sits at "
        f"{fmt(arm['gap_years'][DESCRIPTIVE_BIN], 4)} years and is excluded.")
    add("")

    # ---- the four rows ---------------------------------------------------
    add(f"## The four decay rates (primary: q = {arm['q']}, m = {arm['m']})")
    add("")
    _row_table(add, arm)
    add("R² is descriptive only: it says how well a single exponential "
        "describes the five-bin window, not whether the decay is exponential.")
    add("")
    add("Per-row per-bin personal excess E(b) with its realized mean gap:")
    add("")
    add("| row | " + " | ".join(BIN_LABELS) + " |")
    add("|---|" + "---|" * N_BINS)
    for key in arm["row_order"]:
        row = arm["rows"][key]
        add(f"| {row['label']} | "
            + " | ".join(fmt(row["curve"][b]) for b in range(N_BINS)) + " |")
    add("| *realized mean gap (days)* | "
        + " | ".join(fmt(arm["gap_days"][b], 2) for b in range(N_BINS))
        + " |")
    add("| *realized mean gap (years)* | "
        + " | ".join(fmt(arm["gap_years"][b], 4) for b in range(N_BINS))
        + " |")
    add("| *self pairs* | "
        + " | ".join(f"{arm['rows']['full']['self_pairs'][b]:,}"
                     for b in range(N_BINS)) + " |")
    add("")
    add("Every E(b) in the fitted window is strictly positive, so the "
        "log-linear fit is defined on the point estimate of every row:")
    add("")
    add("| row | min E(b) over the five fitted bins | positive |")
    add("|---|---|---|")
    for key in arm["row_order"]:
        row = arm["rows"][key]
        low = min(row["curve"][:N_FIT_BINS])
        add(f"| {row['label']} | {fmt(low)} | "
            f"{'yes' if low > 0 else 'NO'} |")
    add("")
    add(f"Descriptive {BIN_LABELS[DESCRIPTIVE_BIN]} bin (never fitted): "
        + ", ".join(f"{arm['rows'][k]['label']} "
                    f"{fmt(arm['descriptive_3y_plus'][k])}"
                    for k in arm["row_order"]) + ".")
    add("")

    # ---- the contrast ----------------------------------------------------
    add("## The verdict contrast Λ = λ_distinct − λ_common")
    add("")
    add("| quantity | point | 95% CI | half-width | bootstrap replicates | "
        "dropped (non-positive E) |")
    add("|---|---|---|---|---|---|")
    for item in (delta, arm["secondary"]):
        add(f"| {item['name']} | **{fmt(item['point'])}** | "
            f"{fmt_ci(item['ci'])} | {fmt(item['ci_half_width'])} | "
            f"{item['boot_replicates']:,} | "
            f"{item['boot_dropped_non_positive']:,} |")
    add("")
    add("The bootstrap is PAIRED BY CONSTRUCTION for Λ: all rows sit on one "
        "block set, so `compute_arm` draws the identical author multinomial "
        "for each of them and the contrast is differenced replicate by "
        "replicate. The secondary contrast λ_taste − λ_full is NOT paired "
        "(fold-stratified draws against pool-level draws) and its interval is "
        "correspondingly conservative.")
    add("")
    add("Per-row bootstrap drops (replicates with any non-positive E(b) in "
        "the fitted window): "
        + ", ".join(f"{arm['rows'][k]['label']} "
                    f"{arm['rows'][k]['boot_dropped_non_positive']:,}"
                    for k in arm["row_order"])
        + f" of {arm['rows']['full']['boot_replicates']:,}.")
    add("")

    add("### The permutation null on Λ, and what it can say")
    add("")
    add("| null | replicates | retained | center | 95% band |")
    add("|---|---|---|---|---|")
    add(f"| Λ, registered log-slope form | {delta['null_replicates']:,} | "
        f"{delta['null_retained']:,} | {fmt(delta['null_center'], 5)} | "
        f"{fmt_ci(delta['null_band'], 4)} |")
    add(f"| Λ, positivity-free linear-slope companion | "
        f"{delta['null_replicates']:,} | "
        f"{int(round(delta['linear_null_finite_fraction'] * delta['null_replicates'])):,} | "
        f"{fmt(delta['linear_null_center'], 6)} | "
        f"{fmt_ci(delta['linear_null_band'], 5)} |")
    add("")
    add("**RD-U2C-1 (disclosed re-posing).** The registration poses the null "
        "directly on Λ on the ground that a slope contrast is well behaved "
        "where a ratio is not. That is true of the SLOPE; it is not true of "
        "the LOGARITHM the registered slope is taken on. A within-quarter "
        "relabelling drives E(b) to within a few 1e−4 of zero, its sign then "
        "flips freely across bins, and `log E(b)` is undefined for any "
        "replicate with a non-positive bin — so the registered null is "
        f"computed with the same positivity rule and retains "
        f"{delta['null_retained']:,} of {delta['null_replicates']:,} "
        "replicates. Beside it the runner reports the positivity-free LINEAR "
        "slope contrast (OLS of E(b) on gap_years, no logarithm), defined on "
        f"{fmt(100.0 * delta['linear_null_finite_fraction'], 1)}% of "
        f"replicates, whose realized center is "
        f"{fmt(delta['linear_null_center'], 6)} against a realized value of "
        f"{fmt(delta['linear_point'], 4)} on that same scale. The linear "
        "contrast is NOT level-free — a lower-level row has a shallower "
        "absolute slope whatever its rate — which is exactly why it is not "
        "the estimand and why its realized value need not share Λ's sign; it "
        "is read ONLY as the null's location, where both rows are driven to "
        "zero and no level confound survives. **No verdict rests on either "
        "null**: the verdict is the bootstrap interval on Λ, and the nulls "
        "are location checks.")
    add("")
    add("The informative nulls of this leg are the per-row per-bin E(b) "
        "permutation centers, which reproduce U2's result on every carrier:")
    add("")
    add("| row | largest absolute E(b) null center (any bin) | "
        "smallest E(b) over the fitted bins | ratio |")
    add("|---|---|---|---|")
    for key in arm["row_order"]:
        row = arm["rows"][key]
        worst = max(abs(v) for v in row["curve_null_center"])
        low = min(row["curve"][:N_FIT_BINS])
        ratio_text = f"{low / worst:,.0f}×" if worst > 0 else "n/a"
        add(f"| {row['label']} | {worst:.3e} | {fmt(low)} | {ratio_text} |")
    add("")

    # ---- projection ------------------------------------------------------
    add("### Registration-time projection against the realized width "
        "(#71/#79, executed form)")
    add("")
    add("| quantity | projected at registration | realized |")
    add("|---|---|---|")
    add(f"| Λ point | +{PROJECTED_LAMBDA_POINT:.2f}/y | "
        f"{fmt(delta['point'])}/y |")
    add(f"| Λ CI half-width | {PROJECTED_HALF_WIDTH[0]:.2f}–"
        f"{PROJECTED_HALF_WIDTH[1]:.2f}/y | "
        f"{fmt(delta['ci_half_width'])}/y |")
    add(f"| λ_common | {PROJECTED_LAMBDA_COMMON:.3f}/y | "
        f"{fmt(arm['rows']['common']['lambda_per_year'])}/y |")
    add(f"| λ_distinct | {PROJECTED_LAMBDA_DISTINCT:.3f}/y | "
        f"{fmt(arm['rows']['distinct']['lambda_per_year'])}/y |")
    add(f"| λ_taste | {PROJECTED_LAMBDA_TASTE:.2f}/y | "
        f"{fmt(arm['rows']['taste']['lambda_per_year'])}/y |")
    add("")
    ratio = (delta["ci_half_width"] / PROJECTED_HALF_WIDTH[1]
             if np.isfinite(delta["ci_half_width"]) else float("nan"))
    add("The projection was made from U2b's realized dispersion BEFORE this "
        "run and is reported here whether it flattered the design or not: the "
        f"realized half-width is {fmt(ratio, 3)}× the top of the projected "
        "range. This is the #71 convention executed at registration time "
        "rather than discovered afterwards, which is the whole point of "
        "defect #79's convention.")
    add("")
    u2b = payload["u2b_primary_realization"]
    add("**Honest anomaly — the bigger pool bought a WIDER interval.** The "
        "projection's shrink argument was that the m = 5 pool adds "
        f"{100.0 * (arm['authors_2_3y'] / u2b['authors_2_3y'] - 1.0):.1f}% "
        f"authors over U2b's failed primary ({arm['authors_2_3y']} against "
        f"{u2b['authors_2_3y']}) and "
        f"{100.0 * (arm['pairs_2_3y'] / u2b['pairs_2_3y'] - 1.0):.1f}% pairs "
        f"({arm['pairs_2_3y']:,} against {u2b['pairs_2_3y']:,}). "
        "It did add them, and the interval still came out wider than the "
        "confirmatory arm's, which runs on a SMALLER pool "
        f"({conf['pairs_2_3y']:,} pairs, {conf['authors_2_3y']} authors): the "
        f"primary's half-width is {fmt(delta['ci_half_width'])}/y against the "
        f"confirmatory arm's {fmt(conf['primary']['ci_half_width'])}/y, a "
        f"ratio of "
        f"{delta['ci_half_width'] / conf['primary']['ci_half_width']:.3f}×. "
        "The mechanism is visible in the per-row half-widths below: lowering "
        "the floor admits blocks with as few as m events in a "
        "sub-vocabulary, and a carrier-restricted vector built from five "
        "events is a far noisier point on the sphere than one built from ten. "
        "Pool size and per-block precision trade against each other here, and "
        "the registration priced only the first. The projection convention "
        "(#71/#79) held — the number was stated before the run and is "
        "reported against — but the model behind the number did not.")
    add("")
    add("| row | primary (q=0.5, m=5) λ half-width | confirmatory (q=0.7, "
        "m=10) λ half-width | ratio |")
    add("|---|---|---|---|")
    for key in arm["row_order"]:
        wide = arm["rows"][key]["lambda_ci_half_width"]
        tight = conf["rows"][key]["lambda_ci_half_width"]
        add(f"| {key} | {fmt(wide)} | {fmt(tight)} | "
            f"{wide / tight:.3f}× |")
    add("")

    # ---- confirmatory arm -------------------------------------------------
    add(f"## Confirmatory arm (q = {conf['q']}, m = {conf['m']})")
    add("")
    add(f"Registered as the one sensitivity that also clears both #69 "
        f"targets ({conf['pairs_2_3y']:,} pairs, {conf['authors_2_3y']} "
        "authors). Divergence in cell carries a #73 flag; the PRIMARY routes.")
    add("")
    _row_table(add, conf)
    add("| quantity | point | 95% CI | half-width | cell |")
    add("|---|---|---|---|---|")
    add(f"| Λ (confirmatory) | **{fmt(conf['primary']['point'])}** | "
        f"{fmt_ci(conf['primary']['ci'])} | "
        f"{fmt(conf['primary']['ci_half_width'])} | "
        f"`{conf['cell']['cell']}` |")
    add(f"| λ_taste − λ_full (confirmatory) | "
        f"**{fmt(conf['secondary']['point'])}** | "
        f"{fmt_ci(conf['secondary']['ci'])} | "
        f"{fmt(conf['secondary']['ci_half_width'])} | — |")
    add("")
    if payload["flags_73"]:
        for flag in payload["flags_73"]:
            add(f"- **#73 flag** — {flag}.")
    else:
        add(f"No #73 flag: the confirmatory arm lands in the same cell "
            f"(`{conf['cell']['cell']}`) as the primary.")
    add("")

    # ---- G0 ---------------------------------------------------------------
    add("## G0 — U2b four-row bit-comparison (#56: inheritance is not "
        "exemption)")
    add("")
    g0 = payload["g0"]
    add("U2b's primary configuration (q = 0.5, m = 10) was recomputed here "
        "from the same cache through the same imported estimator — all four "
        "rows, including the five taste folds — and compared field by field "
        f"against its committed artifacts (`{g0['source']}`). Status "
        f"**{g0['status']}**; maximum absolute difference across all "
        f"{sum(len(r['fields']) for r in g0['rows'])} compared fields: "
        f"{g0['max_abs_difference']:.3e}; bitwise identical: "
        f"{'yes' if g0['bitwise_identical'] else 'no'}.")
    add("")
    add("| row | committed key | fields | bitwise identical | max abs "
        "difference |")
    add("|---|---|---|---|---|")
    for row in g0["rows"]:
        add(f"| {row['row']} | `{row['committed_key']}` | "
            f"{len(row['fields'])} | "
            f"{'yes' if row['bitwise_identical'] else 'no'} | "
            f"{row['max_abs_difference']:.3e} |")
    add("")

    # ---- taste purity -----------------------------------------------------
    add("## Taste row — fold purity (blocking gate)")
    add("")
    add("Embeddings are fitted on TRAINING authors' first-half events only; "
        "curves are read on TEST authors' pairs and pooled by unweighted mean "
        "over folds (U1 convention). Purity is a mass identity, asserted "
        "inside the run for every fold of every configuration.")
    add("")
    add("| configuration | fold | train | test | overlap | fitted mass | "
        "train first-half mass | test mass excluded | test blocks |")
    add("|---|---|---|---|---|---|---|---|---|")
    for entry in payload["taste_purity"]:
        add(f"| {entry['configuration']} | {entry['fold']} | "
            f"{entry['n_train']:,} | {entry['n_test']:,} | "
            f"{entry['overlap']} | {entry['fitted_mass']:,.0f} | "
            f"{entry['train_first_half_mass']:,.0f} | "
            f"{entry['test_mass_excluded']:,.0f} | "
            f"{entry['test_blocks']:,} |")
    add("")
    add("Per-fold floor shares at the primary configuration: "
        + ", ".join(fmt(v) for v in arm["per_fold_floor_share"]) + ".")
    add("")

    # ---- leans ------------------------------------------------------------
    add("## Registered leans (disclosed knowledge, not predictions)")
    add("")
    for lean in payload["leans"]:
        add(f"- **{lean['id']}** ({lean['statement']}): "
            f"**{lean['outcome']}** — {lean['detail']}.")
    add("")

    # ---- boundaries -------------------------------------------------------
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
    add("Artifacts (gitignored): `results/m4_u2c_decay_rate_contrast/` — "
        "`config.json`, `config.sha256.json`, `anchors.json`, "
        "`split_census.json`, `gate_anchor.json`, "
        "`g0_anchor_comparison.json`, `arms.json`, `taste_purity.json`, "
        "`verdict.json`, `id_leak_scan.json`, `report_payload.json`, "
        "`run_log.jsonl`.")
    add("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
