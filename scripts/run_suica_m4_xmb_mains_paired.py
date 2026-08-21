"""SUICA M4-X-Mb — the mains estimator, paired-scored gate (instrument leg).

Registration: ``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``, section
"X-Mb — the mains estimator, paired-scored gate", commit e421072.  The
completion of X-M under defect #93.

WHAT THIS LEG IS, AND WHAT IT IS NOT.  X-M built the main estimators and put
them through a five-world battery.  Nine of its ten routing clauses passed;
the tenth -- R02, the size-weighted community main's own-recovery clause in
``{b-only}`` -- read UNINFORMATIVE, because a #90 ceiling placed on the
replicate spread of an own-recovery clause is measuring the sum of two
different things: the ESTIMATOR's error, and the WORLD's own draw-to-draw
variability.  On this skeleton the second term is thirty times the first, so
the ceiling could not see the estimator at all.  Defect #93 fixes the
ARITHMETIC OF THE GATE and nothing else.  This leg therefore changes GATE
SCORING ONLY:

  (a) #93a PAIRED SCORING.  Each of the four own-recovery clauses is scored
      replicate by replicate against THAT replicate's own REALIZED planted
      component -- the estimator's own functional applied to the vector the
      world actually drew, not to the nominal parameter it was drawn from.
      The routing ceilings become paired |mean error| <= 0.01 AND paired
      replicate sd <= 0.01, both in share units (#92).  The NOMINAL
      (world-limited) reading is co-reported beside it, together with the
      derived probability that it could have been informative at all.
  (b) #93c EFFECTIVE SAMPLES.  Every weighted estimand row publishes its
      effective sample 1/sum_i p_i^2 beside its nominal one.
  (c) #93b REPLICATE BUDGET.  The 8-replicate budget is DERIVED against the
      paired ceiling from X-M's own artifact, and printed, not assumed.
  (d) The #93 dev-prototype note, enforced IN CODE: the real arm is
      unreachable except through a function that demands a certification
      stamp, and the stamp's timestamp is written to an artifact before the
      real arm may start.  The ordering is asserted from the artifacts.

EVERY OTHER CLAUSE INHERITS X-M VERBATIM.  This script does not re-implement
the estimator, the normalization, the world builder, the leakage battery, the
bootstrap or the descriptive echo: it CALLS ``XM.mains_gate`` and re-scores
four rows of its output.  The gate object X-M produced is kept whole inside
this leg's artifact under ``inherited_gate`` so that the re-scoring can be
audited against the thing it re-scored.

Metadata only.  ``word_count_quoteless`` is the sole text-derived quantity; no
body is read; ``author_profiles.csv`` is never opened.  Every estimand is a
function of X1's committed cell cache.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import importlib.util
import math
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

XM_SCRIPT = ROOT / "scripts/run_suica_m4_xm_mains_estimator.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:          # pragma: no cover
        raise RuntimeError(f"cannot import machinery from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


XM = load_module("suica_m4_xm_for_xmb", XM_SCRIPT)
X1C = XM.X1C
X1B = XM.X1B
X1 = XM.X1

# ---------------------------------------------------------------------------
# The inherited machinery (#56/#81: bound to the committed objects, not copied)
# ---------------------------------------------------------------------------

Design = XM.Design
write_json = XM.write_json
utc_now = XM.utc_now
fmt = XM.fmt
fmt_ci = XM.fmt_ci
RunLog = XM.RunLog
anchor_gate = XM.anchor_gate
scan_for_cohort_ids = XM.scan_for_cohort_ids
baseline_hit_keys = XM.baseline_hit_keys
new_hits_only = XM.new_hits_only

load_cell_cache = XM.load_cell_cache
law_vocabulary = XM.law_vocabulary
build_chain_design = XM.build_chain_design
synthetic_design = XM.synthetic_design

fe_coefficients = XM.fe_coefficients
normalize_coefficients = XM.normalize_coefficients
fitted_coefficients = XM.fitted_coefficients
mean_removal_factor = XM.mean_removal_factor
mains_df_derivation = XM.mains_df_derivation
mains_budget = XM.mains_budget
full_budget = XM.full_budget
cluster_bootstrap_mains = XM.cluster_bootstrap_mains
mains_gate = XM.mains_gate
score_recovery = XM.score_recovery
ceiling_power = XM.ceiling_power
score_predictions = XM.score_predictions
evaluate_leans = XM.evaluate_leans
gate_status = XM.gate_status

# ---------------------------------------------------------------------------
# Registration pins -- every inherited one bound to X-M's committed definition
# ---------------------------------------------------------------------------

SEED = XM.SEED                                  # 20260819
SEED_PART0 = XM.SEED_PART0
SEED_BOOT = XM.SEED_BOOT
B_BOOT = XM.B_BOOT                              # 1000
B_PERM = XM.B_PERM

WORLDS = XM.WORLDS
WORLD_LABELS = XM.WORLD_LABELS
WORLD_SEED_OFFSET = XM.WORLD_SEED_OFFSET
COMPONENTS = XM.COMPONENTS
RECOVERY_CLAUSES = XM.RECOVERY_CLAUSES

N_SYNTH_REPLICATES = XM.N_SYNTH_REPLICATES      # 8 -- #93b derives, below
RESOLUTION_SHARE = XM.RESOLUTION_SHARE          # 0.01
CEILING_REPLICATE_SD = XM.CEILING_REPLICATE_SD  # 0.01
TOL_SD_MULT = XM.TOL_SD_MULT
LEAK_MAX = XM.LEAK_MAX                          # 0.005

N_MIN_PRIMARY = XM.N_MIN_PRIMARY
K_MIN = XM.K_MIN
S_PRIMARY = XM.S_PRIMARY
S_CENSUS = XM.S_CENSUS
VOCAB_FLOOR_FRACTION = XM.VOCAB_FLOOR_FRACTION
FE_TOL = XM.FE_TOL

ANCHOR_ROWS_PARSEABLE = XM.ANCHOR_ROWS_PARSEABLE
ANCHOR_AUTHORS = XM.ANCHOR_AUTHORS
ANCHOR_BIG5_AUTHORS = XM.ANCHOR_BIG5_AUTHORS
ANCHOR_DISJOINT_AUTHORS = XM.ANCHOR_DISJOINT_AUTHORS
ANCHOR_VOCAB_FLOOR_USERS = XM.ANCHOR_VOCAB_FLOOR_USERS
ANCHOR_LAW_VOCAB = XM.ANCHOR_LAW_VOCAB
CHAIN_ANCHORS = XM.CHAIN_ANCHORS
CHAIN_CROSSCHECKS = XM.CHAIN_CROSSCHECKS

CELL_CERTIFIED = XM.CELL_CERTIFIED              # MAINS_CERTIFIED
CELL_DEFECT = XM.CELL_DEFECT                    # INSTRUMENT_DEFECT

LEAN_CERTIFICATION = XM.LEAN_CERTIFICATION
LEAN_REAL_AUTHOR_MAIN = XM.LEAN_REAL_AUTHOR_MAIN
LEAN_REAL_COMMUNITY_MAIN = XM.LEAN_REAL_COMMUNITY_MAIN
PREDICTION_AUTHOR_MAIN = XM.PREDICTION_AUTHOR_MAIN
PREDICTION_COMMUNITY_MAIN = XM.PREDICTION_COMMUNITY_MAIN

# --- X-Mb's own pins -------------------------------------------------------

# #93a: the two ROUTING ceilings of a paired clause, both in share units.
CEILING_PAIRED_SD = RESOLUTION_SHARE            # 0.01
CEILING_PAIRED_MEAN = RESOLUTION_SHARE          # 0.01

# #93b: the paired sd X-M's committed artifact measured on the clause that
# stopped it.  The registration quotes ~0.0005; the runner reads the artifact
# when it is present and falls back to this pin, recording which it used.
XM_PRIOR_PAIRED_SD = 0.000496
XM_PRIOR_PAIRED_SD_SOURCE = (
    "X-M's committed artifact results/m4_xm_mains_estimator/"
    "part0_mains_gate.json, diagnostics.paired_error.b_only.community."
    "sd_error -- the clause whose NOMINAL scoring stopped X-M")
XM_ARTIFACT = ROOT / "results/m4_xm_mains_estimator/part0_mains_gate.json"

# #93b: the replicate counts the budget derivation sweeps, to show what the
# NOMINAL clause does as the budget grows.  Diagnostic, never routing.
BUDGET_SWEEP_REPLICATES = (8, 16, 30, 60)
BUDGET_SWEEP_TRIALS = 2000

# The nominal clauses' reliability, mapped to the closed-form diagnostic X-M
# already computes.  {full} carries more than one component, so its closed
# form is the SAME design arithmetic read on the own component; the extra
# terms are named in the report rather than folded in.
NOMINAL_POWER_KEY = {
    "a_only:author": "a_only:author",
    "full:author": "a_only:author",
    "b_only:community": "b_only:community (size-weighted)",
    "full:community": "b_only:community (size-weighted)",
}

DEFAULT_X1_CACHE = XM.DEFAULT_X1_CACHE
DEFAULT_COHORT = XM.DEFAULT_COHORT
DEFAULT_OUTPUT = ROOT / "results/m4_xmb_mains_paired"
DEFAULT_REPORT = ROOT / "reports/SUICA_M4_XMB_MAINS_PAIRED_REPORT.md"

COMMITTED_FILES = (
    ROOT / "reports/SUICA_M4_XMB_MAINS_PAIRED_REPORT.md",
    ROOT / "scripts/run_suica_m4_xmb_mains_paired.py",
    ROOT / "tests/test_m4_xmb_mains_paired.py",
    ROOT / "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md",
    ROOT / "docs/CLAIMS_LEDGER.md",
)


# ---------------------------------------------------------------------------
# NEW 1 -- the REALIZED planted component of a single replicate
# ---------------------------------------------------------------------------


REALIZED_COMPONENT_NOTE = (
    "THE OBJECT.  X1's world builder draws the component vectors first and in "
    "a fixed order -- a (authors), then b (communities), then g (cells) -- "
    "and skips the draw entirely when a share is zero, so the stream is "
    "reproducible from the replicate's seed alone.  The REALIZED planted "
    "component of a replicate is then the ESTIMATOR'S OWN FUNCTIONAL applied "
    "to the vector that was actually drawn: the unweighted population "
    "variance of a for the author main, the W-weighted population variance of "
    "b for the size-weighted community main, each divided by the same "
    "realized comment-level Var(y) the estimator divides by, and each carrying "
    "the same mean-removal factor the estimator carries.  Scoring against it "
    "asks 'did the estimator find the world it was given', which is the "
    "question a #90 ceiling is entitled to ask; scoring against the NOMINAL "
    "share asks 'was the world it was given the world we asked for', which is "
    "a property of the draw and not of the instrument.")


def realized_component_draws(skeleton: Design, shares: dict[str, float],
                             seed: int, replicate: int
                             ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """The a, b, g vectors X1's builder drew for this replicate.

    The stream is consumed in the builder's order and with the builder's
    zero-share short circuit, so the returned vectors are the ones the world
    was built from.  A contract test pins this against a noiseless world where
    the cell means ARE ``a[sa] + b[sc] + g``, bit for bit.
    """

    rng = np.random.default_rng(seed + 1000 * replicate)
    A, C, M = skeleton.n_authors, skeleton.n_comms, skeleton.n_slots
    va = float(shares["author"])
    vc = float(shares["community"])
    vg = float(shares["interaction"])
    a = rng.normal(0.0, math.sqrt(va), A) if va > 0 else np.zeros(A)
    b = rng.normal(0.0, math.sqrt(vc), C) if vc > 0 else np.zeros(C)
    g = rng.normal(0.0, math.sqrt(vg), M) if vg > 0 else np.zeros(M)
    return a, b, g


def weighted_popvar(values: np.ndarray,
                    weights: np.ndarray | None = None) -> float:
    """The population variance a weighted covariance of a vector with itself is."""

    v = np.asarray(values, dtype=np.float64)
    if weights is None:
        p = np.full(v.size, 1.0 / v.size)
    else:
        w = np.asarray(weights, dtype=np.float64)
        p = w / w.sum()
    mean = float((p * v).sum())
    return float((p * v * v).sum() - mean * mean)


def skeleton_weights(skeleton: Design) -> dict[str, np.ndarray]:
    """The three weight vectors the three readings run on."""

    sc = skeleton.slot_comm
    C = skeleton.n_comms
    size = (np.bincount(sc, skeleton.n_e, C) + np.bincount(sc, skeleton.n_l, C))
    return {"author": np.ones(skeleton.n_authors, dtype=np.float64),
            "community": size,
            "community_unweighted": np.ones(C, dtype=np.float64)}


def realized_targets(skeleton: Design, shares: dict[str, float], seed: int,
                     replicate: int, var_y: float) -> dict[str, float]:
    """The realized planted component of one replicate, on BOTH scales.

    ``var_y`` is that replicate's own realized comment-level variance, taken
    from the estimator's own reading of the same world, so the target and the
    estimate are shares of the identical denominator.
    """

    a, b, _ = realized_component_draws(skeleton, shares, seed, replicate)
    weights = skeleton_weights(skeleton)
    f_author = mean_removal_factor(weights["author"])["factor"]
    f_comm = mean_removal_factor(weights["community"])["factor"]
    f_comm_u = mean_removal_factor(weights["community_unweighted"])["factor"]
    raw_a = weighted_popvar(a) / var_y
    raw_c = weighted_popvar(b, weights["community"]) / var_y
    raw_cu = weighted_popvar(b) / var_y
    return {"author_raw": float(raw_a), "author": float(raw_a * f_author),
            "community_raw": float(raw_c), "community": float(raw_c * f_comm),
            "community_unweighted_raw": float(raw_cu),
            "community_unweighted": float(raw_cu * f_comm_u)}


# ---------------------------------------------------------------------------
# NEW 2 -- paired scoring (#93a)
# ---------------------------------------------------------------------------


def paired_recovery(skeleton: Design, world: str, component: str,
                    block: dict[str, Any]) -> dict[str, Any]:
    """One own-recovery clause, scored PAIRED against each replicate's truth.

    ``block`` is the world block X-M's gate already built and already scored
    nominally; its per-replicate estimates are reused, not recomputed, so the
    pairing is bit-exact against the replicates the nominal clause read.  The
    only new arithmetic is the realized target.
    """

    shares = WORLDS[world]
    seed = SEED_PART0 + WORLD_SEED_OFFSET[world]
    stats = block["stats"]
    estimates = np.asarray(stats[component]["values"], dtype=np.float64)
    estimates_raw = np.asarray(stats[f"{component}_raw"]["values"],
                               dtype=np.float64)
    var_y = np.asarray(stats["var_y"]["values"], dtype=np.float64)
    n = estimates.size

    targets = np.empty(n, dtype=np.float64)
    targets_raw = np.empty(n, dtype=np.float64)
    for rep in range(n):
        row = realized_targets(skeleton, shares, seed, rep, float(var_y[rep]))
        targets[rep] = row[component]
        targets_raw[rep] = row[f"{component}_raw"]

    err = estimates - targets
    err_raw = estimates_raw - targets_raw
    return {
        "world": world, "component": component, "replicates": int(n),
        "scale": "corrected (#67: raw co-reported)",
        "estimates": [float(x) for x in estimates],
        "realized_targets": [float(x) for x in targets],
        "errors": [float(x) for x in err],
        "mean_error": float(err.mean()),
        "sd_error": float(err.std(ddof=1)) if n > 1 else 0.0,
        "max_abs_error": float(np.abs(err).max()),
        "se_of_mean_error": (float(err.std(ddof=1) / math.sqrt(n))
                             if n > 1 else 0.0),
        "realized_target_mean": float(targets.mean()),
        "realized_target_sd": (float(targets.std(ddof=1)) if n > 1 else 0.0),
        "nominal_target": float(shares[component]),
        "raw": {"mean_error": float(err_raw.mean()),
                "sd_error": float(err_raw.std(ddof=1)) if n > 1 else 0.0,
                "max_abs_error": float(np.abs(err_raw).max()),
                "realized_target_mean": float(targets_raw.mean()),
                "realized_target_sd": (float(targets_raw.std(ddof=1))
                                       if n > 1 else 0.0)},
    }


def score_paired(row: dict[str, Any]) -> dict[str, Any]:
    """#93a's two ROUTING ceilings, both in share units (#92).

    The sd ceiling now constrains the ESTIMATOR, because the world's own draw
    variability has been differenced away; a paired sd above it means the
    instrument itself cannot resolve what it claims to resolve, and that is a
    real UNINFORMATIVE.  The mean ceiling constrains the estimator's BIAS at
    the same resolution.
    """

    sd = float(row["sd_error"])
    mean = float(row["mean_error"])
    informative = sd <= CEILING_PAIRED_SD
    unbiased = abs(mean) <= CEILING_PAIRED_MEAN
    if not informative:
        status = "UNINFORMATIVE"
    else:
        status = "PASS" if unbiased else "FAIL"
    return {"mean_error": mean, "sd_error": sd,
            "abs_mean_error": abs(mean),
            "ceiling_sd": CEILING_PAIRED_SD,
            "ceiling_mean": CEILING_PAIRED_MEAN,
            "sd_headroom": CEILING_PAIRED_SD - sd,
            "mean_headroom": CEILING_PAIRED_MEAN - abs(mean),
            "informative": bool(informative), "unbiased": bool(unbiased),
            "status": status}


def paired_clause_text(world: str, component: str) -> str:
    return (f"recovery, PAIRED (#93a) in {WORLD_LABELS[world]} — the "
            f"{component} main tracks each replicate's OWN realized planted "
            f"component: paired |mean error| <= {CEILING_PAIRED_MEAN} AND "
            f"paired replicate sd <= {CEILING_PAIRED_SD}, share units "
            f"(#92 resolution, #90 ceiling — now on the ESTIMATOR)")


# ---------------------------------------------------------------------------
# NEW 3 -- effective samples (#93c)
# ---------------------------------------------------------------------------


EFFECTIVE_SAMPLE_NOTE = (
    "#93c.  A covariance over 1,000 communities whose weights concentrate on a "
    "few dozen is not a covariance over 1,000 anything.  The effective sample "
    "of a weighted estimand is 1 / sum_i p_i^2 with p the NORMALIZED weights — "
    "the same sum_i p_i^2 that sets the mean-removal factor, so the two "
    "columns below are one quantity read twice.  Every weighted row this leg "
    "reports publishes it beside its nominal count.")


def effective_sample_rows(derivation: dict[str, Any]) -> list[dict[str, Any]]:
    """Nominal vs effective for every weighted estimand row this leg reports."""

    order = (
        ("R02 / R04 — community main, size-weighted (PRIMARY)",
         "community_size_weighted",
         "analysis-pool comment counts (X1c's convention)"),
        ("R01 / R03 — author main", "author",
         "unweighted over the component's authors"),
        ("secondary — community main, unweighted", "community_unweighted",
         "unweighted over the component's communities"),
    )
    rows = []
    for label, key, weighting in order:
        row = derivation[key]
        rows.append({
            "row": label, "weighting": weighting,
            "nominal_members": int(row["members"]),
            "sum_p_squared": float(row["sum_p_squared"]),
            "effective_members": float(row["effective_members"]),
            "effective_fraction": float(row["effective_members"]
                                        / row["members"]),
            "mean_removal_factor": float(row["factor"]),
        })
    inter = derivation["interaction_factor_for_contrast"]
    rows.append({
        "row": "(contrast) X1c's interaction — residual df, not a weighting",
        "weighting": "cells of the shared grid",
        "nominal_members": int(inter["P_shared_pairs"]),
        "sum_p_squared": None,
        "effective_members": float(inter["residual_df"]),
        "effective_fraction": float(inter["residual_df"]
                                    / inter["P_shared_pairs"]),
        "mean_removal_factor": float(inter["factor"]),
    })
    return rows


# ---------------------------------------------------------------------------
# NEW 4 -- the replicate budget, DERIVED (#93b)
# ---------------------------------------------------------------------------


def chi_square_upper_tail_log10(df: int, x: float) -> float:
    """A log10 Chernoff bound on P(chi^2_df >= x), valid for x > df.

    ``P(chi^2_k >= k t) <= (t * exp(1 - t)) ** (k / 2)`` for t > 1.  The bound
    is used rather than an exact survival function because the quantity it
    bounds underflows double precision by hundreds of orders of magnitude, and
    a printed 0.0 would say less than a printed exponent.
    """

    t = float(x) / float(df)
    if t <= 1.0:                                     # pragma: no cover
        return 0.0
    return float((df / 2.0) * (math.log10(t) + (1.0 - t) * math.log10(math.e)))


def prior_paired_sd() -> dict[str, Any]:
    """X-M's measured paired sd, read from its artifact where it exists."""

    if XM_ARTIFACT.exists():
        blob = json.loads(XM_ARTIFACT.read_text(encoding="utf-8"))
        measured = {
            f"{world}:{comp}": float(
                blob["diagnostics"]["paired_error"][world][comp]["sd_error"])
            for world in ("a_only", "b_only", "full")
            for comp in ("author", "community")
            if not (world == "a_only" and comp == "community")
            and not (world == "b_only" and comp == "author")}
        worst = max(measured.values())
        return {"available": True, "source": XM_PRIOR_PAIRED_SD_SOURCE,
                "per_clause": measured,
                "stopping_clause_sd": measured["b_only:community"],
                "worst_clause_sd": float(worst),
                "registered_pin": XM_PRIOR_PAIRED_SD,
                "pin_agrees": bool(abs(measured["b_only:community"]
                                       - XM_PRIOR_PAIRED_SD) < 1e-6)}
    return {"available": False,                      # pragma: no cover
            "source": ("X-M's artifact is absent from this checkout "
                       "(results/ is gitignored); the registration's pin is "
                       "used and the derivation is unchanged"),
            "per_clause": {}, "stopping_clause_sd": XM_PRIOR_PAIRED_SD,
            "worst_clause_sd": XM_PRIOR_PAIRED_SD,
            "registered_pin": XM_PRIOR_PAIRED_SD, "pin_agrees": True}


def replicate_budget_derivation(skeleton: Design, log: RunLog
                                ) -> dict[str, Any]:
    """#93b: the 8-replicate budget, derived against BOTH scorings.

    PAIRED side, closed form.  With R replicates and a paired error sd of
    ``sigma``, the sample sd obeys ``(R - 1) s^2 / sigma^2 ~ chi^2_{R-1}``, so
    the clause breaches its ceiling only if that chi-square exceeds
    ``(R - 1) (ceiling / sigma)^2``.  X-M measured sigma on this very
    skeleton, so the probability is arithmetic, not a guess.

    NOMINAL side, simulated.  The same sweep run at four replicate budgets
    shows what the nominal clause does as the budget grows -- which is the
    part of #93b's worked example that needed checking rather than repeating.
    """

    prior = prior_paired_sd()
    sigma = float(prior["worst_clause_sd"])
    R = N_SYNTH_REPLICATES
    ratio = CEILING_PAIRED_SD / sigma
    threshold = (R - 1) * ratio * ratio
    paired = {
        "replicates": R,
        "paired_sd_prior": sigma,
        "paired_sd_prior_clause": max(prior["per_clause"],
                                      key=prior["per_clause"].get)
        if prior["per_clause"] else None,
        "ceiling": CEILING_PAIRED_SD,
        "ceiling_over_sd": float(ratio),
        "chi_square_df": R - 1,
        "chi_square_threshold": float(threshold),
        "log10_upper_bound_p_breach": chi_square_upper_tail_log10(
            R - 1, threshold),
        "se_of_paired_mean": float(sigma / math.sqrt(R)),
        "mean_ceiling_in_se": float(CEILING_PAIRED_MEAN
                                    / (sigma / math.sqrt(R))),
        "verdict": (f"{R} replicates suffice: the paired sd would have to "
                    f"exceed its expectation by {ratio:.1f}x for the sd "
                    f"ceiling to bind, and the mean ceiling sits "
                    f"{CEILING_PAIRED_MEAN / (sigma / math.sqrt(R)):.0f} "
                    f"standard errors from zero"),
    }

    weights = skeleton_weights(skeleton)
    sweep = {}
    for reps in BUDGET_SWEEP_REPLICATES:
        sweep[str(reps)] = ceiling_power(
            skeleton, WORLDS["b_only"]["community"], weights["community"],
            reps, BUDGET_SWEEP_TRIALS, SEED_PART0 + 401)
        log.event("budget_sweep", replicates=reps,
                  p_under_ceiling=sweep[str(reps)]["p_under_ceiling"])
    ordered = [sweep[str(r)]["p_under_ceiling"]
               for r in BUDGET_SWEEP_REPLICATES]
    monotone_down = all(b <= a + 1e-9 for a, b in zip(ordered, ordered[1:]))
    nominal = {
        "clause": "R02 — the size-weighted community main in {b-only}",
        "closed_form_target_sd": sweep[str(BUDGET_SWEEP_REPLICATES[0])][
            "closed_form_draw_sd"],
        "sweep": sweep,
        "p_under_ceiling_by_replicates": {
            str(r): sweep[str(r)]["p_under_ceiling"]
            for r in BUDGET_SWEEP_REPLICATES},
        "decreases_with_budget": bool(monotone_down),
        "finding": (
            "MORE replicates do not rescue the NOMINAL clause. A sample sd "
            "concentrates on the quantity it estimates, and that quantity is "
            "the target's own draw sd, which is above the ceiling on this "
            "skeleton; so P(informative) falls toward 0 as the budget grows "
            "instead of rising. #93b's worked example (about 60 replicates "
            "would have made R02 reliable at nominal scoring) does not hold "
            "for a ceiling read on the replicate SD — it would hold for a "
            "ceiling read on the standard ERROR of the replicate mean, which "
            "shrinks as 1/sqrt(R). The paired repair is not one option among "
            "several here; for this clause it is the only one that works."),
    }
    return {"paired": paired, "nominal": nominal, "prior": prior,
            "note": ("#93b: the budget is DERIVED from the design and from "
                     "X-M's measured paired sd before the gate is read, and "
                     "printed here rather than asserted")}


# ---------------------------------------------------------------------------
# NEW 5 -- the re-scored gate (SCORING ONLY; the estimator is X-M's)
# ---------------------------------------------------------------------------


def paired_gate(skeleton: Design, b_boot: int, log: RunLog) -> dict[str, Any]:
    """X-M's gate, run verbatim, with its four recovery clauses re-scored."""

    log.event("inherited_gate_start")
    base = mains_gate(skeleton, b_boot, log)
    log.event("inherited_gate_done", routing=base["routing_status"],
              passed=base["n_routing_passed"], of=base["n_routing"])

    paired: dict[str, Any] = {}
    for world, comp in RECOVERY_CLAUSES:
        key = f"{world}:{comp}"
        row = paired_recovery(skeleton, world, comp, base["blocks"][world])
        row["score"] = score_paired(row)
        row["nominal"] = base["recovery"][key]
        power_key = NOMINAL_POWER_KEY[key]
        row["nominal_reliability"] = {
            "key": power_key,
            "p_informative": float(base["diagnostics"]["ceiling_power"][
                power_key]["p_under_ceiling"]),
            "closed_form_draw_sd": float(base["diagnostics"]["ceiling_power"][
                power_key]["closed_form_draw_sd"]),
            "effective_members": float(base["diagnostics"]["ceiling_power"][
                power_key]["effective_members"]),
            "note": ("the closed-form reliability of the NOMINAL reading on "
                     "this component and these weights; in {full} the "
                     "replicate spread also carries the other planted "
                     "components, which this closed form does not model"),
        }
        paired[key] = row
        log.event("paired_clause", clause=key, status=row["score"]["status"],
                  mean_error=row["mean_error"], sd_error=row["sd_error"],
                  nominal_status=row["nominal"]["status"])

    # --- rebuild the routing family: R01-R04 paired, R05-R10 X-M verbatim ---
    routing: dict[str, str] = {}
    for index, (world, comp) in enumerate(RECOVERY_CLAUSES, start=1):
        key = f"{world}:{comp}"
        routing[f"(R{index:02d}) {paired_clause_text(world, comp)}"] = \
            paired[key]["score"]["status"]
    inherited_routing = {k: v for k, v in base["routing_clauses"].items()
                         if not k.startswith(("(R01)", "(R02)", "(R03)",
                                              "(R04)"))}
    if len(inherited_routing) != base["n_routing"] - len(RECOVERY_CLAUSES):
        raise RuntimeError(                          # pragma: no cover
            "the inherited routing family did not have the shape X-M "
            "committed; the re-scoring refuses to guess")
    routing.update(inherited_routing)

    descriptive = dict(base["descriptive_clauses"])
    routing_status, descriptive_status = gate_status(routing, descriptive)

    derivation = base["df_derivation"]
    out = {
        "routing_clauses": routing,
        "descriptive_clauses": descriptive,
        "n_routing": len(routing),
        "n_routing_passed": sum(1 for v in routing.values() if v == "PASS"),
        "n_descriptive": len(descriptive),
        "n_descriptive_passed": sum(1 for v in descriptive.values()
                                    if v == "PASS"),
        "routing_status": routing_status,
        "descriptive_status": descriptive_status,
        "paired_recovery": paired,
        "nominal_recovery": base["recovery"],
        "leakage": base["leakage"],
        "bootstrap_zero": base["bootstrap_zero"],
        "interaction_echo": base["interaction_echo"],
        "interaction_echo_zero_worlds": base["interaction_echo_zero_worlds"],
        "marginal_counterfactual": base["marginal_counterfactual"],
        "df_derivation": derivation,
        "effective_samples": effective_sample_rows(derivation),
        "diagnostics": base["diagnostics"],
        "inherited_gate": {
            "routing_clauses": base["routing_clauses"],
            "routing_status": base["routing_status"],
            "n_routing_passed": base["n_routing_passed"],
            "resolution_rule": base["resolution_rule"],
        },
        "scoring_rule": (
            f"#93a PAIRED: every own-recovery clause is scored replicate by "
            f"replicate against ITS OWN realized planted component (the "
            f"estimator's functional applied to the drawn vector, over the "
            f"same realized Var(y)); ROUTING requires paired |mean error| <= "
            f"{CEILING_PAIRED_MEAN} AND paired replicate sd <= "
            f"{CEILING_PAIRED_SD}. The NOMINAL reading X-M routed on is "
            f"co-reported with its derived P(informative). Clauses R05-R10 "
            f"and D01-D03 are X-M's, unchanged."),
        "delta_from_xm": paired_vs_nominal_delta(paired, base),
    }
    log.event("paired_gate_done", routing=routing_status,
              descriptive=descriptive_status,
              passed=out["n_routing_passed"], of=out["n_routing"])
    return out


def paired_vs_nominal_delta(paired: dict[str, Any],
                            base: dict[str, Any]) -> dict[str, Any]:
    """Exactly which clauses the re-scoring moved, and in which direction."""

    rows = {}
    for key, row in paired.items():
        before = base["recovery"][key]["status"]
        after = row["score"]["status"]
        rows[key] = {"nominal_status": before, "paired_status": after,
                     "changed": bool(before != after),
                     "nominal_replicate_sd": base["recovery"][key][
                         "replicate_sd"],
                     "paired_replicate_sd": row["sd_error"],
                     "sd_ratio": float(base["recovery"][key]["replicate_sd"]
                                       / max(row["sd_error"], 1e-15))}
    return {"rows": rows,
            "n_changed": sum(1 for r in rows.values() if r["changed"]),
            "changed": [k for k, r in rows.items() if r["changed"]],
            "routing_before": base["routing_status"],
            "n_passed_before": base["n_routing_passed"]}


def a1_stop_fires(gate: dict[str, Any]) -> bool:
    """The A1 stop reads the ROUTING family and nothing else (#86a)."""

    return gate["routing_status"] != "PASS"


def build_verdict(gate: dict[str, Any],
                  real: dict[str, Any] | None) -> dict[str, Any]:
    certified = not a1_stop_fires(gate)
    failing = {k: v for k, v in gate["routing_clauses"].items() if v != "PASS"}
    if certified:
        headline = (
            "Every routing clause of the paired-scored mains battery passed "
            "on the realized skeleton, so the corpus main budget below is "
            "licensed as an instrument reading — the first true main budget "
            "of this design.")
    else:
        headline = (
            f"{len(failing)} of {gate['n_routing']} routing clauses did not "
            "pass, the A1 stop fires, and NO real-data main was computed, "
            "reported or stored. The instrument is not certified at the "
            "registered resolution.")
    return {
        "cell": CELL_CERTIFIED if certified else CELL_DEFECT,
        "certified": bool(certified),
        "headline": headline,
        "routing_status": gate["routing_status"],
        "descriptive_status": gate["descriptive_status"],
        "n_routing": gate["n_routing"],
        "n_routing_passed": gate["n_routing_passed"],
        "failing_routing_clauses": failing,
        "real_arm_run": bool(real is not None),
    }


# ---------------------------------------------------------------------------
# NEW 6 -- the certification stamp and the GATED real arm (#93 dev note)
# ---------------------------------------------------------------------------


DEV_PROTOTYPE_RULE = (
    "#93 note, enforced in code rather than by restraint: a development "
    "prototype never touches the real arm before certification. In this leg "
    "the real arm is unreachable except through ``run_real_arm``, which "
    "refuses any certificate whose cell is not MAINS_CERTIFIED and whose "
    "stamp is not already on disk; the stamp carries both a UTC instant and a "
    "monotonic counter, the real arm records its own, and "
    "``certification_order.json`` asserts the order from the artifacts.")


def stamp_certification(verdict: dict[str, Any], output: Path
                        ) -> dict[str, Any]:
    """Write the certification stamp BEFORE the real arm may be reached."""

    certificate = {
        "cell": verdict["cell"],
        "certified": bool(verdict["certified"]),
        "n_routing": verdict["n_routing"],
        "n_routing_passed": verdict["n_routing_passed"],
        "stamped_utc": utc_now(),
        "stamped_monotonic_ns": int(time.monotonic_ns()),
        "rule": DEV_PROTOTYPE_RULE,
    }
    write_json(output / "certification.json", certificate)
    return certificate


class UncertifiedRealArm(RuntimeError):
    """Raised when anything tries to read the corpus without a certificate."""


def run_real_arm(skeleton: Design, b_boot: int, certificate: dict[str, Any],
                 output: Path, log: RunLog | None = None) -> dict[str, Any]:
    """The ONLY path to a real-data main in this leg.

    The function is total in its refusal: an absent, uncertified or unstamped
    certificate raises, and no corpus estimand is formed on the way to the
    raise.  Callers do not get to decide -- ``main`` has no other route to
    ``full_budget`` on the real skeleton.
    """

    if not isinstance(certificate, dict):            # pragma: no cover
        raise UncertifiedRealArm("the real arm needs a certification stamp")
    if certificate.get("cell") != CELL_CERTIFIED or not certificate.get(
            "certified"):
        raise UncertifiedRealArm(
            f"the real arm is forbidden: the instrument certificate reads "
            f"{certificate.get('cell')!r}")
    if not certificate.get("stamped_monotonic_ns"):
        raise UncertifiedRealArm(
            "the real arm is forbidden: the certificate carries no stamp")
    if not (output / "certification.json").exists():
        raise UncertifiedRealArm(
            "the real arm is forbidden: the certification stamp is not on "
            "disk, so its precedence could not be audited")

    started_ns = int(time.monotonic_ns())
    started_utc = utc_now()
    budget = full_budget(skeleton)
    boot = cluster_bootstrap_mains(skeleton, b_boot, SEED_BOOT + 307, log,
                                   "real_primary")
    weights = skeleton_weights(skeleton)
    real = {
        "design": skeleton.summary(),
        "budget": budget,
        "bootstrap": boot,
        "gauge_factors": {
            "author": mean_removal_factor(weights["author"]),
            "community_size_weighted": mean_removal_factor(
                weights["community"]),
            "community_unweighted": mean_removal_factor(
                weights["community_unweighted"]),
            "interaction_x1c_contrast": budget["interaction_factor"],
            "treatment": ("#87(b) treatment one — the factor is RECOMPUTED "
                          "from each bootstrap replicate's own weights, not "
                          "pinned at the realized design"),
        },
        "effective_samples": {
            "authors_nominal": int(skeleton.n_authors),
            "authors_effective": float(budget["effective_authors"]),
            "communities_nominal": int(skeleton.n_comms),
            "communities_effective": float(budget["effective_communities"]),
        },
        "certificate": {k: certificate[k] for k in
                        ("cell", "certified", "stamped_utc",
                         "stamped_monotonic_ns")},
        "started_utc": started_utc,
        "started_monotonic_ns": started_ns,
        "finished_utc": utc_now(),
    }
    write_json(output / "real_arm.json", real)
    return real


def parse_utc(stamp: str) -> datetime:
    """The artifacts' UTC instants, compared as instants and not as strings."""

    return datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))


def certification_order(certificate: dict[str, Any],
                        real: dict[str, Any] | None) -> dict[str, Any]:
    """The #93 ordering assertion, read back off the artifacts."""

    if real is None:
        return {"status": "PASS",
                "ordered": True,
                "certification_stamped_utc": certificate["stamped_utc"],
                "real_arm_started_utc": None,
                "monotonic_delta_ns": None,
                "reading": ("the real arm did not run, so nothing could "
                            "precede the stamp; the clause holds vacuously "
                            "and no corpus estimand exists in this leg"),
                "rule": DEV_PROTOTYPE_RULE}
    delta = int(real["started_monotonic_ns"]) - int(
        certificate["stamped_monotonic_ns"])
    ordered = delta > 0 and (parse_utc(real["started_utc"])
                             >= parse_utc(certificate["stamped_utc"]))
    return {"status": "PASS" if ordered else "FAIL",
            "ordered": bool(ordered),
            "certification_stamped_utc": certificate["stamped_utc"],
            "real_arm_started_utc": real["started_utc"],
            "monotonic_delta_ns": delta,
            "reading": ("the certification stamp was written to disk before "
                        "the real arm formed its first corpus estimand; the "
                        "order is asserted from the artifacts, not from the "
                        "order the source happens to read in"),
            "rule": DEV_PROTOTYPE_RULE}


# ---------------------------------------------------------------------------
# The report (rule 24: every table below is generated from the artifacts)
# ---------------------------------------------------------------------------


BOUNDARIES = XM.BOUNDARIES + (
    "**A certified instrument is still only an instrument.** MAINS_CERTIFIED "
    "says the estimator recovers a planted main on this skeleton to the "
    "registered resolution. It does not say the corpus main means anything "
    "about anybody, and the real budget below is a description of variance on "
    "an eligible grid, not a statement about persons or venues.",
    "**The gate was repaired, not relaxed.** Paired scoring makes the ceiling "
    "STRICTER on the estimator (the world's draw noise no longer inflates the "
    "spread the clause is compared against) while removing a term the clause "
    "was never entitled to charge the instrument for. A clause that passes "
    "here would also have passed X-M's nominal ceiling had the worlds been "
    "drawn quietly enough.",
)

LINEAGE = XM.LINEAGE[:-1] + (
    "M4-X-M (`INSTRUMENT_DEFECT`, commit 3ee385d) — the estimator built and "
    "9/10 routing clauses passed; R02 read UNINFORMATIVE because a #90 "
    "ceiling on a world-limited clause charges the instrument for the "
    "world's own draw noise (P(informative) = 0.267 for ANY correct "
    "estimator). Defect #93 purchased.",
    "M4-X-Mb (this leg) — the same estimator, the same worlds, the same "
    "seeds, the same six inherited routing clauses and the same three "
    "descriptives. GATE ARITHMETIC ONLY: #93a paired scoring, #93c effective "
    "samples, #93b a derived replicate budget, and the #93 dev-prototype note "
    "enforced by a stamp the real arm cannot bypass.",
)


def build_reading(payload: dict[str, Any]) -> list[str]:
    """The verdict in sentences, every number pulled from the artifacts."""

    gate = payload["gate"]
    verdict = payload["verdict"]
    delta = gate["delta_from_xm"]
    dfd = gate["df_derivation"]
    budget = payload["replicate_budget"]
    out: list[str] = []

    passed, total = gate["n_routing_passed"], gate["n_routing"]
    if verdict["certified"]:
        out.append(
            f"**The instrument certifies.** All {total} routing clauses pass "
            "under paired scoring, so the corpus main budget in this report "
            "is licensed as an instrument reading and X3's #87 prerequisite "
            "is discharged for both mains.")
    else:
        failing = "; ".join(f"`{v}` on {k.split(')')[0]})"
                            for k, v in
                            verdict["failing_routing_clauses"].items())
        out.append(
            f"**The instrument does NOT certify.** {passed} of {total} "
            f"routing clauses passed and the rest did not: {failing}. The A1 "
            "stop fires, the real arm did not run, and no corpus main exists "
            "in this leg's record.")

    r02 = gate["paired_recovery"]["b_only:community"]
    moved = delta["n_changed"]
    out.append(
        "**What the repair actually did.** X-M's routing family read "
        f"`{delta['routing_before']}` with {delta['n_passed_before']} of "
        f"{total} clauses passing; re-scored paired, "
        f"{moved} clause{'' if moved == 1 else 's'} moved "
        f"({', '.join(delta['changed']) if delta['changed'] else 'none'}). "
        "The clause that stopped X-M is the size-weighted community main in "
        f"`{{b-only}}`: its NOMINAL replicate sd is "
        f"{fmt(r02['nominal']['replicate_sd'], 4)} against a ceiling of "
        f"{fmt(CEILING_PAIRED_SD, 2)}, while its PAIRED sd is "
        f"{fmt(r02['sd_error'], 6)} — a factor of "
        f"{fmt(delta['rows']['b_only:community']['sd_ratio'], 0)} between the "
        "two, which is the world's draw noise being charged to the "
        "instrument and then not being charged to it.")

    out.append(
        "**The estimator was never the problem, and the numbers say so "
        "twice.** Paired, the four own-recovery clauses read mean errors of "
        + ", ".join(f"{fmt(gate['paired_recovery'][f'{w}:{c}']['mean_error'], 6)}"
                    for w, c in RECOVERY_CLAUSES)
        + " with paired sds of "
        + ", ".join(f"{fmt(gate['paired_recovery'][f'{w}:{c}']['sd_error'], 6)}"
                    for w, c in RECOVERY_CLAUSES)
        + f" — against ceilings of {fmt(CEILING_PAIRED_MEAN, 2)} on both. The "
        "same worlds, the same seeds, the same estimates: only the thing they "
        "are compared to changed.")

    nom = budget["nominal"]
    out.append(
        "**And #93b's own worked example needed checking.** The adjudication "
        "reasoned that about 60 replicates would have made R02 reliable at "
        "nominal scoring. Swept directly on this skeleton, the probability "
        "that the nominal clause lands under its ceiling reads "
        + ", ".join(f"{r} → {fmt(p, 3)}" for r, p in
                    nom["p_under_ceiling_by_replicates"].items())
        + ". It FALLS with the budget, because a sample sd concentrates on "
        "the quantity it estimates and that quantity — the target's own draw "
        f"sd, {fmt(nom['closed_form_target_sd'], 4)} — is above the ceiling "
        "on this skeleton. More replicates would have made the nominal clause "
        "more reliably UNINFORMATIVE, not less. The paired repair is not one "
        "option among several for this clause; it is the only one that works.")

    paired_budget = budget["paired"]
    out.append(
        "**The paired budget, derived rather than inherited.** With X-M's "
        f"measured paired sd of {fmt(paired_budget['paired_sd_prior'], 6)} on "
        f"its widest clause, {paired_budget['replicates']} replicates put the "
        f"sd ceiling {fmt(paired_budget['ceiling_over_sd'], 1)}x away and the "
        f"mean ceiling {fmt(paired_budget['mean_ceiling_in_se'], 0)} standard "
        "errors away; the chance of breaching the sd ceiling by replicate "
        f"noise alone is bounded above by 10^"
        f"{fmt(paired_budget['log10_upper_bound_p_breach'], 0)}.")

    # the {full} author clause's paired mean error IS the measured leakage
    full_author = gate["paired_recovery"]["full:author"]
    g_leak = gate["leakage"]["g_only"]["rows"]["author"]["reading"]
    out.append(
        "**One paired clause carries a real bias, and paired scoring is what "
        "makes it legible.** The author main in "
        f"`{{full}}` has a paired mean error of "
        f"{fmt(full_author['mean_error'], 6)} against a standard error of "
        f"{fmt(full_author['se_of_mean_error'], 6)} — inside the registered "
        f"{fmt(CEILING_PAIRED_MEAN, 2)} resolution, and therefore a PASS, but "
        "not noise. It has a name and a measured value elsewhere in this same "
        f"battery: the interaction's bleed into the author coefficient reads "
        f"{fmt(g_leak, 5)} in `{{g-only}}`, the largest of the "
        "six zero-point rows. The two agree to the fifth decimal, which is "
        "the df derivation's `popvar(M_a·g)` term appearing twice: once as "
        "leakage in a world with no author effect, once as bias in a world "
        "that has one. Nominal scoring hid it inside a replicate spread six "
        "times its size.")

    out.append(
        "**The effective-sample disclosure (#93c) is where the whole episode "
        "came from.** The size-weighted community main runs on an effective "
        f"{fmt(dfd['community_size_weighted']['effective_members'], 1)} "
        f"communities of a nominal {dfd['C_communities']:,} — "
        f"{fmt(100 * dfd['community_size_weighted']['effective_members'] / dfd['C_communities'], 1)}% "
        "— and every table in this report that prints the nominal count now "
        "prints the effective one beside it.")

    if verdict["certified"] and payload.get("real") is not None:
        real = payload["real"]
        pred = payload["predictions"]
        out.append(
            "**The first true main budget of this design.** The author main "
            f"reads {fmt(real['budget']['author'], 4)} "
            f"{fmt_ci(real['bootstrap']['ci']['author'], 4)} and the "
            "size-weighted community main "
            f"{fmt(real['budget']['community'], 4)} "
            f"{fmt_ci(real['bootstrap']['ci']['community'], 4)}, as shares of "
            "comment-level Var(y) on the eligible shared grid. X1c's "
            "2x2-inversion annotations, promoted to predictions by the X-M "
            "registration, score "
            + "; ".join(f"{comp} {row['status']} (predicted "
                        f"{fmt(row['prediction'], 3)}, read "
                        f"{fmt(row['point'], 4)})"
                        for comp, row in pred["rows"].items())
            + ".")
        gaps = {comp: row["gap"] for comp, row in pred["rows"].items()}
        out.append(
            "**Both predictions miss, and they miss by almost exactly the "
            "same amount.** The author gap is "
            f"{fmt(gaps['author'], 4)} and the community gap "
            f"{fmt(gaps['community'], 4)} — a difference between the two of "
            f"{fmt(abs(gaps['author'] - gaps['community']), 5)}. X1c's 2x2 "
            "inversion was an algebraic annotation on contaminated rows, and "
            "it over-corrected both mains by about two variance points in the "
            "same direction. That is a property of the inversion, not of "
            "either main, and it is reported here rather than smoothed: a "
            "prediction that breaks the same way twice is more informative "
            "than one that breaks once.")
        unweighted = float(payload["real"]["budget"]["community_unweighted"])
        out.append(
            "**And the weighting choice is doing the work on the community "
            "side.** The registered PRIMARY community main is size-weighted "
            f"and reads {fmt(payload['real']['budget']['community'], 4)}; the "
            f"UNWEIGHTED secondary reads {fmt(unweighted, 4)}, which lands "
            f"{fmt(abs(unweighted - PREDICTION_COMMUNITY_MAIN), 4)} from the "
            f"predicted {fmt(PREDICTION_COMMUNITY_MAIN, 3)}. The registration "
            "named the size-weighted reading as primary before the run and "
            "that is what routes and what is scored; the coincidence on the "
            "secondary is recorded as an observation about the weighting, "
            "with no claim attached. On a design whose size-weighted "
            "community side has an effective sample of "
            f"{fmt(payload['gate']['df_derivation']['community_size_weighted']['effective_members'], 1)}, "
            "the two weightings are not estimating a common number, and "
            "which one a downstream leg wants is a question that has to be "
            "asked deliberately.")
    return out


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []

    def add(text: str = "") -> None:
        lines.append(text)

    verdict = payload["verdict"]
    config = payload["config"]

    add("# SUICA M4-X-Mb — the mains estimator, paired-scored")
    add()
    add(f"**VERDICT — {verdict['cell']}.** {verdict['headline']}")
    add()
    add(f"Run (UTC): `{config['run_utc']}` · seed `{config['seed']}` · "
        f"B_boot `{config['b_boot']}` · runtime "
        f"{fmt(payload['runtime_s'], 1)} s · config sha256 "
        f"`{payload['config_sha256'][:16]}…`")
    add()
    add("## The reading")
    add()
    for item in payload["reading"]:
        add(item)
        add()
    add("## Leg lineage")
    add()
    for item in payload["lineage"]:
        add(f"- {item}")
    add()

    _write_gates(add, payload)
    _write_delta(add, payload)
    _write_gate_table(add, payload)
    _write_effective(add, payload)
    _write_budget(add, payload)
    _write_inherited(add, payload)
    _write_certification(add, payload)
    _write_real(add, payload)
    _write_leans(add, payload)
    _write_deviations(add, payload)

    add("## Boundaries")
    add()
    for item in payload["boundaries"]:
        add(f"- {item}")
    add()
    add("## Configuration")
    add()
    add("```json")
    add(json.dumps(config, indent=2, sort_keys=True, default=float))
    add("```")
    add()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_gates(add, payload: dict[str, Any]) -> None:
    add("## Preconditions")
    add()
    add("| gate | status |")
    add("| --- | --- |")
    for name, status in payload["gates"].items():
        add(f"| {name} | **{status}** |")
    add()
    chain = payload["chain_census"]
    add("### The predicate-chain census (#78, BLOCKING)")
    add()
    add("| support floor s | authors | communities | shared pairs | "
        "singleton communities | LCC author coverage |")
    add("| --- | --- | --- | --- | --- | --- |")
    for s in sorted(chain, key=int):
        row = chain[s]
        add(f"| s = {s} | {row['authors']:,} | {row['communities']:,} | "
            f"{row['shared_pairs']:,} | {row['singleton_communities']:,} | "
            f"{fmt(row['lcc_author_coverage'], 3)} |")
    add()
    add("The primary skeleton is the `s = 5` row, at `n_min = "
        f"{payload['config']['n_min_primary']}` cells; every number in this "
        "report is a function of it and of X1's committed cell cache. The "
        "skeleton, the estimator, the normalization, the worlds and the seeds "
        "are X-M's, unchanged.")
    add()


def _write_delta(add, payload: dict[str, Any]) -> None:
    gate = payload["gate"]
    delta = gate["delta_from_xm"]
    add("## What X-Mb changes, and what it does not")
    add()
    add("| element | X-M | X-Mb |")
    add("| --- | --- | --- |")
    add("| skeleton, estimator, pinned normalization | the certified ones | "
        "**identical** (imported by file, contract-tested) |")
    add("| worlds, seeds, replicate count | 5 worlds, offsets 13/19/23/7/0, "
        "8 replicates | **identical** |")
    add("| own-recovery scoring (R01–R04) | replicate mean vs the NOMINAL "
        "planted share | **PAIRED**: each replicate vs ITS OWN realized "
        "planted component (#93a) |")
    add("| own-recovery ceilings | replicate sd ≤ 0.01, gap ≤ max(0.01, "
        "3×sd) | paired sd ≤ 0.01 AND \\|paired mean error\\| ≤ 0.01 |")
    add("| cross-leakage, bootstrap-zero, bootstrap-stability (R05–R10) | "
        "6 clauses | **inherited verbatim** |")
    add("| interaction echo (D01–D03) | 3 descriptive clauses | "
        "**inherited verbatim** |")
    add("| effective samples | named in the diagnosis | **published beside "
        "every nominal count** (#93c) |")
    add("| replicate budget | inherited from X1b | **derived and printed** "
        "(#93b) |")
    add("| real-arm access | source order | **a certification stamp the real "
        "arm cannot bypass**, order asserted from artifacts (#93 note) |")
    add()
    add("| clause | X-M (nominal) | X-Mb (paired) | moved | nominal "
        "replicate sd | paired replicate sd | ratio |")
    add("| --- | --- | --- | --- | --- | --- | --- |")
    for key, row in delta["rows"].items():
        add(f"| {key} | **{row['nominal_status']}** | "
            f"**{row['paired_status']}** | {fmt(row['changed'])} | "
            f"{fmt(row['nominal_replicate_sd'], 4)} | "
            f"{fmt(row['paired_replicate_sd'], 6)} | "
            f"{fmt(row['sd_ratio'], 1)}x |")
    add()
    add(payload["realized_component_note"])
    add()


def _write_gate_table(add, payload: dict[str, Any]) -> None:
    gate = payload["gate"]
    add("## The gate — PAIRED and NOMINAL, side by side")
    add()
    add(gate["scoring_rule"])
    add()
    add("### ROUTING clauses (A1-stopping)")
    add()
    add("| clause | status |")
    add("| --- | --- |")
    for name, status in gate["routing_clauses"].items():
        add(f"| {name} | **{status}** |")
    add()
    add(f"**{gate['n_routing_passed']} of {gate['n_routing']} routing clauses "
        f"passed → routing status `{gate['routing_status']}`.**")
    add()
    add("### Own-component recovery — the two scorings on the same replicates")
    add()
    add("| clause | world | component | PAIRED mean error | PAIRED sd | "
        "PAIRED status | NOMINAL gap | NOMINAL sd | NOMINAL status | "
        "NOMINAL P(informative) |")
    add("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for index, (world, comp) in enumerate(RECOVERY_CLAUSES, start=1):
        row = gate["paired_recovery"][f"{world}:{comp}"]
        nominal = row["nominal"]
        add(f"| R{index:02d} | {WORLD_LABELS[world]} | {comp} | "
            f"{fmt(row['mean_error'], 6)} | {fmt(row['sd_error'], 6)} | "
            f"**{row['score']['status']}** | {fmt(nominal['gap'], 4)} | "
            f"{fmt(nominal['replicate_sd'], 4)} | "
            f"**{nominal['status']}** | "
            f"{fmt(row['nominal_reliability']['p_informative'], 3)} |")
    add()
    add("`P(informative)` is the closed-form reliability of the NOMINAL "
        "reading, computed from the design alone: the realized weighted "
        "population variance of an iid component moves draw to draw with "
        "`sd ≈ V·sqrt(2·Σ p_i²)`, and the column reports how often a sample "
        f"sd formed from {payload['config']['synthetic_replicates']} "
        "replicates of that quantity lands under the ceiling. It is a "
        "property of the WORLDS and of the weights — no estimator appears "
        "in it.")
    add()
    add("| clause | realized target, mean | realized target, sd | "
        "nominal target | max abs paired error | se of paired mean |")
    add("| --- | --- | --- | --- | --- | --- |")
    for world, comp in RECOVERY_CLAUSES:
        row = gate["paired_recovery"][f"{world}:{comp}"]
        add(f"| {world}:{comp} | {fmt(row['realized_target_mean'], 4)} | "
            f"{fmt(row['realized_target_sd'], 4)} | "
            f"{fmt(row['nominal_target'], 4)} | "
            f"{fmt(row['max_abs_error'], 6)} | "
            f"{fmt(row['se_of_mean_error'], 6)} |")
    add()
    add("Corrected scale routes; the raw scale is co-reported (#67). Both "
        "the estimate and the realized target carry the SAME constant "
        "mean-removal factor on a fixed skeleton, so the paired error on the "
        "corrected scale is exactly the raw paired error times that factor — "
        "the routing decision is scale-invariant here, which is a property "
        "worth stating rather than a coincidence worth hiding:")
    add()
    add("| clause | paired mean error, RAW | paired sd, RAW | "
        "realized target, RAW |")
    add("| --- | --- | --- | --- |")
    for world, comp in RECOVERY_CLAUSES:
        raw = gate["paired_recovery"][f"{world}:{comp}"]["raw"]
        add(f"| {world}:{comp} | {fmt(raw['mean_error'], 6)} | "
            f"{fmt(raw['sd_error'], 6)} | "
            f"{fmt(raw['realized_target_mean'], 4)} |")
    add()


def _write_effective(add, payload: dict[str, Any]) -> None:
    gate = payload["gate"]
    add("## Effective samples (#93c)")
    add()
    add(payload["effective_sample_note"])
    add()
    add("| estimand row | weighting | nominal members | `Σ p²` | "
        "EFFECTIVE members | effective / nominal | mean-removal factor |")
    add("| --- | --- | --- | --- | --- | --- | --- |")
    for row in gate["effective_samples"]:
        sump2 = ("—" if row["sum_p_squared"] is None
                 else fmt(row["sum_p_squared"], 6))
        add(f"| {row['row']} | {row['weighting']} | "
            f"{row['nominal_members']:,} | {sump2} | "
            f"{fmt(row['effective_members'], 1)} | "
            f"{fmt(row['effective_fraction'], 4)} | "
            f"{fmt(row['mean_removal_factor'], 6)} |")
    add()
    real = payload.get("real")
    if real is not None:
        eff = real["effective_samples"]
        add("On the REAL skeleton, the same disclosure for the corpus "
            "reading:")
        add()
        add("| side | nominal | effective |")
        add("| --- | --- | --- |")
        add(f"| authors | {eff['authors_nominal']:,} | "
            f"{fmt(eff['authors_effective'], 1)} |")
        add(f"| communities (size-weighted) | {eff['communities_nominal']:,} | "
            f"{fmt(eff['communities_effective'], 1)} |")
        add()


def _write_budget(add, payload: dict[str, Any]) -> None:
    budget = payload["replicate_budget"]
    paired = budget["paired"]
    nominal = budget["nominal"]
    prior = budget["prior"]
    add("## The replicate budget, derived (#93b)")
    add()
    add(budget["note"] + ".")
    add()
    add(f"**Prior.** {prior['source']}. The measured paired sds are "
        + ", ".join(f"`{k}` {fmt(v, 6)}"
                    for k, v in sorted(prior["per_clause"].items()))
        + f"; the registration's pin of {fmt(prior['registered_pin'], 6)} "
        f"{'agrees' if prior['pin_agrees'] else 'DISAGREES'} with the "
        "stopping clause's measured value.")
    add()
    add("**Paired side, closed form.** With `R` replicates and a paired error "
        "sd of `σ`, the sample sd obeys `(R−1)·s²/σ² ~ χ²_{R−1}`, so the "
        "clause breaches its ceiling only if that chi-square exceeds "
        "`(R−1)·(ceiling/σ)²`.")
    add()
    add("| quantity | value |")
    add("| --- | --- |")
    add(f"| replicates R | {paired['replicates']} |")
    add(f"| paired sd σ (worst X-M clause) | "
        f"{fmt(paired['paired_sd_prior'], 6)} |")
    add(f"| ceiling / σ | {fmt(paired['ceiling_over_sd'], 1)}x |")
    add(f"| χ² threshold at df = {paired['chi_square_df']} | "
        f"{fmt(paired['chi_square_threshold'], 1)} |")
    add(f"| log10 upper bound on P(sd ceiling breached) | "
        f"{fmt(paired['log10_upper_bound_p_breach'], 1)} |")
    add(f"| se of the paired mean | {fmt(paired['se_of_paired_mean'], 6)} |")
    add(f"| mean ceiling, in standard errors | "
        f"{fmt(paired['mean_ceiling_in_se'], 0)} |")
    add()
    add(f"**Conclusion.** {paired['verdict']}.")
    add()
    add("**Nominal side, simulated — and this is where #93b's worked example "
        "does not survive contact with the design.**")
    add()
    add("| replicates | mean replicate sd | P(replicate sd ≤ ceiling) |")
    add("| --- | --- | --- |")
    for reps, row in nominal["sweep"].items():
        add(f"| {reps} | {fmt(row['mean_replicate_sd'], 4)} | "
            f"{fmt(row['p_under_ceiling'], 3)} |")
    add()
    add(nominal["finding"])
    add()


def _write_inherited(add, payload: dict[str, Any]) -> None:
    gate = payload["gate"]
    add("## The inherited clauses (X-M verbatim)")
    add()
    add("### Cross-leakage — the #85 zero-point family, for mains")
    add()
    add("| world | zero-planted component | reading | maximum | status |")
    add("| --- | --- | --- | --- | --- |")
    for name in WORLDS:
        clause = gate["leakage"][name]
        if not clause["applicable"]:
            add(f"| {WORLD_LABELS[name]} | — | — | — | **N/A** "
                f"({clause['note']}) |")
            continue
        for comp, row in clause["rows"].items():
            add(f"| {WORLD_LABELS[name]} | {comp} | "
                f"{fmt(row['reading'], 5)} | {fmt(row['maximum'], 3)} | "
                f"**{row['status']}** |")
    add()
    marg = gate["marginal_counterfactual"]
    add(f"Scored against the same {fmt(LEAK_MAX, 3)} bound, the FE mains pass "
        f"all {marg['n_zero_rows']} zero-point rows and X1c's MARGINAL "
        f"estimators fail {marg['n_marginal_failures']} of them "
        f"({', '.join(marg['marginal_failures'])}) — #87's diagnosis as a "
        "measurement, carried forward unchanged.")
    add()
    add("### The null world's bootstrap")
    add()
    add("| main | point | CI (corrected) | CI (raw, #67) | covers 0 | "
        "covers own point |")
    add("| --- | --- | --- | --- | --- | --- |")
    for comp, row in gate["bootstrap_zero"].items():
        add(f"| {comp} | {fmt(row['point'], 5)} | {fmt_ci(row['ci'], 5)} | "
            f"{fmt_ci(row['ci_raw'], 5)} | {fmt(row['covers_zero'])} | "
            f"{fmt(row['covers_own_point'])} |")
    add()
    add("### DESCRIPTIVE clauses (annotate, never stop)")
    add()
    add("| clause | status |")
    add("| --- | --- |")
    for name, status in gate["descriptive_clauses"].items():
        add(f"| {name} | **{status}** |")
    add()
    add("| world | interaction target | recovered mean (df-corrected) | gap | "
        "replicate sd |")
    add("| --- | --- | --- | --- | --- |")
    for name, row in gate["interaction_echo"].items():
        add(f"| {WORLD_LABELS[name]} | {fmt(row['target'], 4)} | "
            f"{fmt(row['recovered_mean'], 4)} | {fmt(row['gap'], 4)} | "
            f"{fmt(row['replicate_sd'], 4)} |")
    for name, value in gate["interaction_echo_zero_worlds"].items():
        add(f"| {WORLD_LABELS[name]} | 0.0000 | {fmt(value, 5)} | "
            f"{fmt(value, 5)} | — |")
    add()
    add("### The gauge factors on the realized skeleton")
    add()
    dfd = gate["df_derivation"]
    add("| reading | members | `Σ p²` | effective members | factor |")
    add("| --- | --- | --- | --- | --- |")
    for label, key in (("author main", "author"),
                       ("community main, size-weighted (PRIMARY)",
                        "community_size_weighted"),
                       ("community main, unweighted (secondary)",
                        "community_unweighted")):
        row = dfd[key]
        add(f"| {label} | {row['members']:,} | {fmt(row['sum_p_squared'], 6)} "
            f"| {fmt(row['effective_members'], 1)} | "
            f"{fmt(row['factor'], 6)} |")
    inter = dfd["interaction_factor_for_contrast"]
    add(f"| *(contrast)* X1c's INTERACTION factor `P/(P − A − C + 1)` | "
        f"P = {inter['P_shared_pairs']:,} | — | "
        f"{inter['residual_df']:,} | {fmt(inter['factor'], 6)} |")
    add()
    add("The mains carry NO residual-df shrinkage — X-M derived it, printed "
        "it and contract-tested it, and this leg inherits the derivation "
        "with the estimator.")
    add()


def _write_certification(add, payload: dict[str, Any]) -> None:
    cert = payload["certificate"]
    order = payload["certification_order"]
    add("## The certification stamp and the gated real arm (#93 note)")
    add()
    add(order["rule"])
    add()
    add("| field | value |")
    add("| --- | --- |")
    add(f"| certificate cell | **{cert['cell']}** |")
    add(f"| certified | {fmt(cert['certified'])} |")
    add(f"| stamped (UTC) | `{cert['stamped_utc']}` |")
    add(f"| real arm started (UTC) | "
        f"`{order['real_arm_started_utc'] or '— (did not run)'}` |")
    add(f"| monotonic delta (ns) | "
        f"{'—' if order['monotonic_delta_ns'] is None else format(order['monotonic_delta_ns'], ',')} |")
    add(f"| order assertion | **{order['status']}** |")
    add()
    add(order["reading"] + ".")
    add()


def _write_real(add, payload: dict[str, Any]) -> None:
    add("## The corpus main budget")
    add()
    real = payload.get("real")
    if real is None:
        add("**NOT COMPUTED.** The A1 stop fired: at least one routing clause "
            "did not pass, so the registration forbids the real arm and no "
            "corpus main was computed, reported or stored. The failing "
            "clauses are:")
        add()
        for name, status in payload["verdict"][
                "failing_routing_clauses"].items():
            add(f"- `{status}` — {name}")
        add()
        add("The registered PREDICTIONS from X1c's 2x2 inversion (author main "
            f"≈ {PREDICTION_AUTHOR_MAIN}, community main ≈ "
            f"{PREDICTION_COMMUNITY_MAIN}) are therefore **UNSCORED**.")
        add()
        return
    budget = real["budget"]
    boot = real["bootstrap"]
    add("Every routing clause passed, the certificate was stamped, and the "
        "real arm ran ONCE through the gated path — the first TRUE main "
        "budget of this design, superseding X1c's marginal-annotated reading "
        "as the interpretable one (X1c's rows remain valid under their "
        "marginal name).")
    add()
    add("| component | share (corrected) | CI | share (raw, #67) | CI (raw) | "
        "gauge factor |")
    add("| --- | --- | --- | --- | --- | --- |")
    for comp, label, gauge in (
            ("author", "author main `Var_hat(a)`", "author"),
            ("community", "community main `Var_hat(b)`, size-weighted",
             "community_size_weighted"),
            ("community_unweighted", "community main, unweighted (secondary)",
             "community_unweighted")):
        add(f"| {label} | {fmt(budget[comp], 4)} | "
            f"{fmt_ci(boot['ci'][comp], 4)} | {fmt(budget[comp + '_raw'], 4)} "
            f"| {fmt_ci(boot['ci'][comp + '_raw'], 4)} | "
            f"{fmt(real['gauge_factors'][gauge]['factor'], 6)} |")
    add(f"| interaction (X1c's estimand, df-corrected) | "
        f"{fmt(budget['interaction'], 4)} | — | "
        f"{fmt(budget['interaction_raw'], 4)} | — | "
        f"{fmt(budget['interaction_factor'], 6)} |")
    add(f"| residual | {fmt(budget['residual'], 4)} | — | — | — | — |")
    add()
    add(f"Bootstrap: cluster over authors, `B = {boot['b_boot']:,}`, the FE "
        "refitted and the coefficients re-normalized inside every replicate, "
        f"and the gauge factor recomputed from each replicate's own weights "
        f"({real['gauge_factors']['treatment']}).")
    add()
    add("For contrast, X1c's MARGINAL rows on the same skeleton read "
        f"author {fmt(budget['marginal_author_x1c'], 4)} and community "
        f"{fmt(budget['marginal_community_x1c'], 4)} — the difference between "
        "them and the mains above is the contamination the projection "
        "removes, which the zero-point battery measured on synthetic worlds "
        "and which appears here at corpus scale.")
    add()
    add("### The registered predictions, scored")
    add()
    pred = payload["predictions"]
    add("| prediction | value | realized point | realized CI | result |")
    add("| --- | --- | --- | --- | --- |")
    for comp, row in pred["rows"].items():
        add(f"| {comp} main | {fmt(row['prediction'], 4)} | "
            f"{fmt(row['point'], 4)} | {fmt_ci(row['ci'], 4)} | "
            f"**{row['status']}** |")
    add()
    add(f"Source of the predictions: {pred['source']}.")
    add()


def _write_leans(add, payload: dict[str, Any]) -> None:
    add("## Registered leans")
    add()
    add("| lean | registered | observed | status |")
    add("| --- | --- | --- | --- |")
    for row in payload["leans"]:
        observed = row["observed"]
        add(f"| {row['lean']} | {row['registered']} | "
            f"{fmt(observed) if observed is not None else '—'} | "
            f"**{row['status']}** |")
    add()


def _write_deviations(add, payload: dict[str, Any]) -> None:
    add("## Deviations and anomalies, all recorded")
    add()
    for item in payload["deviations"]:
        add(f"- {item}")
    add()
    add("## Defect candidates for the planner (nothing below was run)")
    add()
    for item in payload["defect_candidates"]:
        add(f"- {item}")
    add()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--x1-cache", type=Path, default=DEFAULT_X1_CACHE)
    parser.add_argument("--cohort", type=Path, default=DEFAULT_COHORT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--b-boot", type=int, default=B_BOOT)
    args = parser.parse_args(argv)

    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    log = RunLog(output / "run_log.jsonl")
    started = time.time()

    config = {
        "leg": "M4-X-Mb",
        "title": "the mains estimator, paired-scored gate",
        "class": "R1 (instrument leg; certificates only, no theory verdict)",
        "role": ("the completion of X-M under defect #93: GATE ARITHMETIC "
                 "ONLY. The estimator, the skeleton, the normalization, the "
                 "worlds and the seeds are X-M's committed ones"),
        "registration":
            "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md@e421072 (X-Mb)",
        "predecessors": [
            "M4-X1 (A1_STOP__SYNTHETIC_GATE_FAILED, commit ebe4f5b)",
            "M4-X1b (A1_STOP__SYNTHETIC_GATE_FAILED, commit e8c9040)",
            "M4-X1c (RESPONSE_TRACE, adjudicated; defect #87)",
            "M4-X-M (INSTRUMENT_DEFECT, commit 3ee385d; defect #93)",
        ],
        "machinery_imported_by_file": [
            "scripts/run_suica_m4_xm_mains_estimator.py (the mains estimator, "
            "the pinned normalization, the df derivation, the five-world "
            "gate, the leakage battery, the bootstrap, the descriptive echo)",
            "scripts/run_suica_m4_x1c_venue_response.py (df correction, "
            "clause-separated gate status)",
            "scripts/run_suica_m4_x1b_venue_response_fe.py (predicate chain, "
            "exact-FE alternating projections, synthetic world builder, cell "
            "cache, law vocabulary)",
            "scripts/run_suica_m4_x1_venue_response.py (Design, "
            "variance_budget, weighted_cov, #83 helpers)",
        ],
        "changed_from_xm": [
            "#93a own-recovery clauses are scored PAIRED against each "
            "replicate's own realized planted component; ROUTING ceilings "
            "are paired |mean error| <= 0.01 AND paired sd <= 0.01",
            "#93a the NOMINAL reading is co-reported with its derived "
            "P(informative) from the closed-form target sd",
            "#93c every weighted estimand row publishes its effective sample "
            "beside its nominal one",
            "#93b the replicate budget is derived and printed, on both "
            "scorings",
            "#93 note: the real arm is reachable only through a certification "
            "stamp written to disk first, and the order is asserted from the "
            "artifacts",
        ],
        "unchanged_from_xm": [
            "the skeleton and its #78 census",
            "the two-way FE estimator and the pinned normalization",
            "the five worlds, their planted shares and their seed offsets",
            "the 8-replicate budget (now derived rather than inherited)",
            "routing clauses R05-R10 (cross-leakage, bootstrap-zero, "
            "bootstrap-stability) and descriptives D01-D03",
            "the df derivation and the gauge factors",
            "the cells, the leans, the predictions and the boundaries",
        ],
        "run_utc": utc_now(),
        "seed": SEED, "seed_part0": SEED_PART0, "seed_boot": SEED_BOOT,
        "b_boot": int(args.b_boot),
        "b_perm_not_used": (
            f"B_perm = {B_PERM} is registered 'where applicable'; no X-Mb "
            "clause is defined against a permutation band"),
        "y": "log(1 + word_count_quoteless)",
        "halves": "author's FULL-STREAM median created_utc, <= to early",
        "skeleton": ("X1c's primary design: law vocabulary (floor 89 users -> "
                     "1,443 communities), support floor s = 5, n_min = 10 "
                     "cells, k_min = 3, largest connected component"),
        "n_min_primary": N_MIN_PRIMARY,
        "k_min": K_MIN,
        "support_primary": S_PRIMARY,
        "support_censused": list(S_CENSUS),
        "vocabulary_floor_fraction": VOCAB_FLOOR_FRACTION,
        "fe_tolerance": FE_TOL,
        "normalization": list(XM.NORMALIZATION_SEQUENCE),
        "worlds": WORLDS,
        "world_seed_offsets": WORLD_SEED_OFFSET,
        "synthetic_replicates": N_SYNTH_REPLICATES,
        "resolution_floor_share": RESOLUTION_SHARE,
        "ceiling_paired_sd": CEILING_PAIRED_SD,
        "ceiling_paired_mean_error": CEILING_PAIRED_MEAN,
        "ceiling_replicate_sd_nominal": CEILING_REPLICATE_SD,
        "tolerance_sd_multiple_nominal": TOL_SD_MULT,
        "leakage_maximum": LEAK_MAX,
        "paired_scoring": REALIZED_COMPONENT_NOTE,
        "effective_sample_rule": EFFECTIVE_SAMPLE_NOTE,
        "dev_prototype_rule": DEV_PROTOTYPE_RULE,
        "replicate_budget_sweep": list(BUDGET_SWEEP_REPLICATES),
        "replicate_budget_sweep_trials": BUDGET_SWEEP_TRIALS,
        "xm_prior_paired_sd": XM_PRIOR_PAIRED_SD,
        "xm_prior_paired_sd_source": XM_PRIOR_PAIRED_SD_SOURCE,
        "cells": {"certified": CELL_CERTIFIED, "defect": CELL_DEFECT,
                  "rule": ("MAINS_CERTIFIED iff EVERY routing clause passes; "
                           "any failure is INSTRUMENT_DEFECT + A1, and the "
                           "real arm is not run")},
        "leans": {"certification": LEAN_CERTIFICATION,
                  "real_author_main": list(LEAN_REAL_AUTHOR_MAIN),
                  "real_community_main": list(LEAN_REAL_COMMUNITY_MAIN)},
        "predictions": {"author_main": PREDICTION_AUTHOR_MAIN,
                        "community_main": PREDICTION_COMMUNITY_MAIN,
                        "source": XM.PREDICTION_SOURCE},
        "columns_read": ["author", "subreddit", "created_utc",
                         "word_count_quoteless", "word_count"],
        "author_profiles_opened": False,
        "bodies_read": False,
        "data_source": ("X1's committed cell cache "
                        "results/m4_x1_venue_response/cell_cache.npz "
                        "(sufficient statistics); the 17.6M-row comments CSV "
                        "is re-streamed ONLY if the cache is absent"),
    }
    config_blob = json.dumps(config, sort_keys=True, default=float)
    config_hash = hashlib.sha256(config_blob.encode("utf-8")).hexdigest()
    write_json(output / "config.json", config)
    write_json(output / "config.sha256.json", {"sha256": config_hash})
    log.event("config", sha256=config_hash)

    # ---- Stage 1: X1's cell cache and the inherited census ----------------
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
        "Inherited census anchors (#78: 17,640,062 parseable rows / 10,296 "
        "authors / 1,443 law communities and three more)": census["status"],
    }
    if census["status"] != "PASS":                   # pragma: no cover
        failed = {k: v for k, v in census["pins"].items()
                  if v["status"] != "PASS"}
        raise SystemExit(f"STOP (#78): inherited census mismatch {failed}")

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
        ok = all(float(got[k]) == float(v) for k, v in want.items())
        chain_ok = chain_ok and ok
        pins_by_s[str(s)] = {"status": "PASS" if ok else "FAIL",
                             "registered": want,
                             "observed": {k: got[k] for k in want}}
    crosschecks: dict[str, Any] = {}
    for s, wants in CHAIN_CROSSCHECKS.items():
        got = chain_census[str(s)]
        for key, want in wants.items():
            digits = 4 if key != "authors_per_community_median" else 1
            obs = round(float(got[key]), digits)
            crosschecks[f"s = {s}: {key}"] = {
                "expected": want, "observed": obs,
                "agrees": bool(obs == round(float(want), digits))}
    write_json(output / "chain_crosschecks.json", crosschecks)
    chain_anchor = {"status": "PASS" if chain_ok else "FAIL",
                    "pins_by_s": pins_by_s,
                    "registered": {str(k): v
                                   for k, v in CHAIN_ANCHORS.items()}}
    write_json(output / "chain_anchor.json", chain_anchor)
    gates["Predicate-chain census (#78: s = 3/5/8 exact; 0 singleton "
          "communities and LCC 1.000 at s = 5)"] = chain_anchor["status"]
    if not chain_ok:                                 # pragma: no cover
        raise SystemExit(f"STOP (#78): predicate-chain census mismatch "
                         f"{pins_by_s}")

    primary = chain_designs[S_PRIMARY]
    lcc_cov = chain_census[str(S_PRIMARY)]["lcc_author_coverage"]
    if lcc_cov != 1.0:                               # pragma: no cover
        raise SystemExit(f"STOP: the LCC does not cover every author "
                         f"({lcc_cov})")
    gates["LCC assertion (the alternating projection is exact, and the "
          "coefficient gauge is one-dimensional, only on a connected "
          "design)"] = "PASS"

    # ---- Stage 3: the replicate budget, DERIVED BEFORE the gate is read ---
    budget_derivation = replicate_budget_derivation(primary, log)
    write_json(output / "replicate_budget.json", budget_derivation)
    log.event("replicate_budget",
              paired_sd=budget_derivation["paired"]["paired_sd_prior"],
              ceiling_over_sd=budget_derivation["paired"]["ceiling_over_sd"])

    # ---- Stage 4: THE GATE (synthetic worlds only) ------------------------
    gate = paired_gate(primary, args.b_boot, log)
    write_json(output / "part0_mains_gate_paired.json", gate)
    write_json(output / "effective_samples.json",
               {"note": EFFECTIVE_SAMPLE_NOTE,
                "rows": gate["effective_samples"]})
    gates["Mains gate — ROUTING clauses, PAIRED (#93a; A1 stop on any "
          "failure; the real arm is forbidden unless every one "
          "passes)"] = gate["routing_status"]
    gates["Mains gate — DESCRIPTIVE clauses (the X1c interaction echo; "
          "annotate, never stop)"] = gate["descriptive_status"]

    # ---- Stage 5: the certification STAMP, then the gated real arm --------
    verdict = build_verdict(gate, None)
    certificate = stamp_certification(verdict, output)
    log.event("certification_stamped", cell=certificate["cell"],
              certified=certificate["certified"])

    real: dict[str, Any] | None = None
    if certificate["certified"]:
        real = run_real_arm(primary, args.b_boot, certificate, output, log)
        log.event("real_arm_done", author=real["budget"]["author"],
                  community=real["budget"]["community"])
    else:
        log.event("real_arm_skipped",
                  reason="A1 stop: a routing clause did not pass")

    order = certification_order(certificate, real)
    write_json(output / "certification_order.json", order)
    gates["Certification precedes the real arm (#93 dev-prototype note; "
          "asserted from the artifacts' own timestamps)"] = order["status"]
    if order["status"] != "PASS":                    # pragma: no cover
        raise SystemExit(f"STOP (#93): the real arm did not follow the "
                         f"certification stamp: {order}")

    verdict = build_verdict(gate, real)
    write_json(output / "verdict.json", verdict)
    predictions = score_predictions(real)
    write_json(output / "predictions.json", predictions)
    leans = evaluate_leans(gate, real)
    write_json(output / "leans.json", leans)

    deviations = [
        "**No permutation null was run.** `B_perm = 499` is registered "
        "'where applicable'; every X-Mb clause is a recovery, a leakage "
        "bound or a bootstrap statement.",
        "**The paired block reuses the gate's own per-replicate estimates.** "
        "X-M's diagnostic paired block re-drew each world and recomputed the "
        "estimator; this leg reads the per-replicate values the scored block "
        "already stored and computes only the realized target, so the pairing "
        "is bit-exact against the replicates the nominal clause read rather "
        "than a re-derivation of them. The realized-component reconstruction "
        "is contract-tested against a noiseless world where the cell means "
        "ARE the drawn components.",
        "**Paired errors route on the corrected scale, raw co-reported "
        "(#67).** On a fixed skeleton the estimate and the realized target "
        "carry the same constant mean-removal factor, so the corrected paired "
        "error is exactly the raw one times that factor and the routing "
        "decision is scale-invariant; the identity is contract-tested.",
        "**#93b's worked example is corrected in-leg.** The adjudication's "
        "'about 60 replicates' would not have rescued the nominal clause: "
        "swept on this skeleton, P(informative) FALLS with the replicate "
        "budget. The correction is reported as a measurement, and the paired "
        "budget is derived separately and holds.",
        "**The {full} author clause passes with a bias, not with noise.** "
        "Its paired mean error is several standard errors from zero and "
        "matches the interaction's measured bleed into the author "
        "coefficient; the clause passes because that bias is inside the "
        "registered resolution, and the agreement is reported in the reading "
        "above rather than left as a rounding coincidence.",
        "**Both registered predictions MISS, in the same direction and by "
        "nearly the same amount**, and the unweighted community secondary "
        "sits close to the community prediction while the registered "
        "size-weighted primary does not. The primary was named before the "
        "run and is what routes; the secondary's proximity is recorded as an "
        "observation with no claim attached.",
        "**No development prototype touched the real arm.** The #93 note is "
        "enforced in code: the real arm is reachable only through "
        "`run_real_arm`, which refuses an uncertified or unstamped "
        "certificate, and `certification_order.json` asserts from the "
        "artifacts that the stamp preceded the first corpus estimand.",
    ]
    defect_candidates = [
        "**A gate ceiling should declare which VARIANCE it is bounding.** "
        "#93a fixed own-recovery clauses by pairing, but the general shape of "
        "the mistake is a clause whose statistic mixes estimator error with "
        "design-side draw noise. A registration convention could require "
        "every ceiling to name the variance component it constrains "
        "(estimator / world / both) so the arithmetic is checkable before the "
        "run rather than after the stop.",
        "**A worked example inside an adopted defect deserves the same "
        "pre-registration arithmetic as a clause.** #93b's own illustration "
        "('about 60 replicates') was not derived, and it does not hold for "
        "the ceiling it illustrates. Convention to consider: an illustrative "
        "number in a defect note is either derived in the note or marked "
        "explicitly as an unchecked sketch.",
        "**An own-recovery clause could report its realized target's spread "
        "as a routing DIAGNOSTIC.** Paired scoring hides the world variation "
        "that made the nominal reading unreliable; publishing the realized "
        "target sd beside the paired sd (as this leg's table does) keeps the "
        "design's own instability visible rather than differenced away.",
    ]

    payload = {
        "config": config,
        "config_sha256": config_hash,
        "census": census,
        "chain_census": chain_census,
        "chain_anchor": chain_anchor,
        "chain_crosschecks": crosschecks,
        "gate": gate,
        "replicate_budget": budget_derivation,
        "certificate": certificate,
        "certification_order": order,
        "real": real,
        "predictions": predictions,
        "leans": leans,
        "verdict": verdict,
        "gates": gates,
        "lineage": list(LINEAGE),
        "boundaries": list(BOUNDARIES),
        "realized_component_note": REALIZED_COMPONENT_NOTE,
        "effective_sample_note": EFFECTIVE_SAMPLE_NOTE,
        "deviations": deviations,
        "defect_candidates": defect_candidates,
        "runtime_s": round(time.time() - started, 1),
    }
    payload["reading"] = build_reading(payload)
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
              pre_existing=scan["n_pre_existing_hits"])
    gates[f"ID-leak scan (0 NEW hits of {len(universe):,} author names over "
          f"the committed files; {scan['n_pre_existing_hits']} pre-existing "
          "dictionary collisions carried unchanged from HEAD)"] = scan["status"]
    payload["id_leak_scan"] = {k: v for k, v in scan.items() if k != "hits"}
    payload["gates"] = gates
    payload["runtime_s"] = round(time.time() - started, 1)
    write_report(args.report, payload)
    if scan["status"] != "PASS":                     # pragma: no cover
        raise SystemExit(f"STOP: ID-leak scan FAILED on NEW hits: {new_hits}")

    write_json(output / "report_payload.json",
               {k: v for k, v in payload.items() if k != "config"})
    log.event("done", verdict=verdict["cell"],
              routing=gate["routing_status"],
              descriptive=gate["descriptive_status"],
              runtime_s=payload["runtime_s"])
    return 0


if __name__ == "__main__":                           # pragma: no cover
    raise SystemExit(main())
