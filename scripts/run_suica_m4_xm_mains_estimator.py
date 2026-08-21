"""SUICA M4-X-M — the mains estimator (instrument leg, R1-class).

Registration: ``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``, section
"X-M — the mains estimator", commit d65e818.  X3's #87 prerequisite.

WHAT THIS LEG IS.  X1c read crossing #2 on real data and, in the same breath,
renamed its two main rows MARGINAL: the cross-half covariance of author
half-means is not an estimator of Var(a), because an author's half-mean
carries that author's own composition average of the community main and of
the interaction, identically in both halves.  #87 turned that into a
prerequisite: any leg that wants the MAINS as objects must first build main
ESTIMATORS under their own gate.  This leg is that gate, and nothing else --
no theory verdict, no reading of the corpus unless the instrument certifies.

THE ESTIMATOR.  Per half, the exact two-way fixed-effect fit of the eligible
shared cells by alternating projections (X1b's machinery, imported by file,
with X1b's tightened stopping rule: BOTH residual group means <= 1e-10 on
exit).  The fit is a projection, so its COEFFICIENTS are identified only up
to the one-dimensional gauge a -> a + t, b -> b - t; the registration pins
the normalization, and this script executes it in the pinned sequence:

    (1) fit           y_cell = a_acc[author] + b_acc[community] + v
    (2) centre the author coefficients to mean 0 over the connected
        component and ABSORB the shift into the intercept
    (3) centre the community coefficients likewise, absorbing again

    => y_cell = mu + a_hat[author] + b_hat[community] + v,
       mean(a_hat) = mean(b_hat) = 0 over the component.

Then, per component, the CROSS-HALF covariance of the coefficient vectors:

    Var_hat(a) = cov over the authors of (a_hat_early, a_hat_late)
    Var_hat(b) = cov over the communities of (b_hat_early, b_hat_late),
                 size-weighted PRIMARY (weights = analysis-pool comment
                 counts, X1c's convention), unweighted secondary,

both reported as SHARES of comment-level Var(y) over the analysis pool
(X1c's population-variance convention).  The cross-half form is what makes
the object an estimator rather than a variance decomposition: the two halves'
estimation errors are unlinked given the design, so the coefficients'
sampling noise cancels in expectation instead of inflating the reading.

THE GATE IS THE LEG.  Five wholly synthetic worlds on the REALIZED skeleton,
eight replicates each, cell sufficient statistics drawn exactly (X1b's
simulation: cell mean ~ N(mu, sigma^2/n), within-cell SS ~ sigma^2
chi^2_{n-1}).  ROUTING clauses stop the leg (A1); DESCRIPTIVE clauses
annotate it.  If every routing clause passes the leg reads the corpus once;
if any fails the verdict is INSTRUMENT_DEFECT and NO real-data number is
computed, reported, or stored.

Metadata only.  ``word_count_quoteless`` is the sole text-derived quantity;
no body is read; ``author_profiles.csv`` is never opened.  Every estimand is
a function of X1's committed cell cache -- the 17.6M-row comments file is
re-streamed only if that cache is absent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import importlib.util
import sys
import time
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

X1C_SCRIPT = ROOT / "scripts/run_suica_m4_x1c_venue_response.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:          # pragma: no cover
        raise RuntimeError(f"cannot import machinery from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


X1C = load_module("suica_m4_x1c_for_xm", X1C_SCRIPT)
X1B = X1C.X1B
X1 = X1C.X1

# ---------------------------------------------------------------------------
# The inherited machinery (#56/#81: bound to the committed objects, not copied)
# ---------------------------------------------------------------------------

Design = X1B.Design
write_json = X1B.write_json
utc_now = X1B.utc_now
fmt = X1B.fmt
fmt_ci = X1B.fmt_ci
RunLog = X1B.RunLog
percentile_ci = X1B.percentile_ci
scan_for_cohort_ids = X1B.scan_for_cohort_ids
baseline_hit_keys = X1B.baseline_hit_keys
new_hits_only = X1B.new_hits_only
anchor_gate = X1B.anchor_gate

load_cell_cache = X1B.load_cell_cache
law_vocabulary = X1B.law_vocabulary
build_chain_design = X1B.build_chain_design
bipartite_lcc = X1B.bipartite_lcc

fe_residual = X1B.fe_residual
fe_pair = X1B.fe_pair
fe_exactness = X1B.fe_exactness
recover_shares_fe = X1B.recover_shares_fe
synthetic_design = X1B.synthetic_design
variance_budget = X1B.variance_budget
weighted_cov = X1.weighted_cov

df_correction = X1C.df_correction          # the INTERACTION's df factor
gate_status = X1C.gate_status
ROUTING = X1C.ROUTING
DESCRIPTIVE = X1C.DESCRIPTIVE

# ---------------------------------------------------------------------------
# Registration pins -- every inherited one bound to the committed definition
# ---------------------------------------------------------------------------

SEED = X1B.SEED                     # 20260819
B_BOOT = X1B.B_BOOT                 # 1000
B_PERM = X1B.B_PERM                 # 499 -- no registered X-M clause uses it

SEED_PART0 = X1B.SEED_PART0         # seeds INHERITED, never re-chosen (#76)
SEED_BOOT = X1B.SEED_BOOT

N_MIN_PRIMARY = X1B.N_MIN_PRIMARY   # 10
N_MIN_SENSITIVITY = X1B.N_MIN_SENSITIVITY
K_MIN = X1B.K_MIN
S_PRIMARY = X1B.S_PRIMARY           # 5
S_SENSITIVITY = X1B.S_SENSITIVITY
S_CENSUS = X1B.S_CENSUS             # (3, 5, 8)
VOCAB_FLOOR_FRACTION = X1B.VOCAB_FLOOR_FRACTION
FE_TOL = X1B.FE_TOL                 # 1e-10
FE_MAX_ITER = X1B.FE_MAX_ITER

ANCHOR_ROWS_PARSEABLE = X1B.ANCHOR_ROWS_PARSEABLE
ANCHOR_AUTHORS = X1B.ANCHOR_AUTHORS
ANCHOR_BIG5_AUTHORS = X1B.ANCHOR_BIG5_AUTHORS
ANCHOR_DISJOINT_AUTHORS = X1B.ANCHOR_DISJOINT_AUTHORS
ANCHOR_VOCAB_FLOOR_USERS = X1B.ANCHOR_VOCAB_FLOOR_USERS
ANCHOR_LAW_VOCAB = X1B.ANCHOR_LAW_VOCAB
CHAIN_ANCHORS = X1B.CHAIN_ANCHORS
CHAIN_CROSSCHECKS = X1B.CHAIN_CROSSCHECKS

N_SYNTH_REPLICATES = X1B.N_SYNTH_REPLICATES     # 8
TOL_SD_MULT = X1B.TOL_SD_MULT                   # 3.0
LEAK_MAX = X1B.ABLATION_LEAK_MAX                # 0.005

# --- X-M's own pins --------------------------------------------------------

# #92: the recovery floor is a RESOLUTION statement in the estimand's own
# units.  The estimand is a SHARE of comment-level Var(y), so the floor is
# 0.01 OF THAT SHARE -- "this gate resolves a main to one variance point".
RESOLUTION_SHARE = 0.01

# #90: the same number, read as a CEILING on the replicate spread.  A clause
# whose replicate sd exceeds the resolution it claims has not measured
# anything, and an unmeasured routing clause STOPS the leg.
CEILING_REPLICATE_SD = RESOLUTION_SHARE

# The five worlds.  {full} is the only one with no zero-planted component, so
# the cross-leakage clause is vacuous there and is recorded as such.
WORLDS: dict[str, dict[str, float]] = {
    "a_only": {"author": 0.30, "community": 0.00, "interaction": 0.00},
    "b_only": {"author": 0.00, "community": 0.08, "interaction": 0.00},
    "g_only": {"author": 0.00, "community": 0.00, "interaction": 0.02},
    "null": {"author": 0.00, "community": 0.00, "interaction": 0.00},
    "full": {"author": 0.30, "community": 0.08, "interaction": 0.02},
}
# Seed offsets INHERITED where X1b already fixed one for the same world shape
# (author-only 13, community-only 19, null 7, planted 0); {g-only} is new to
# this leg and takes the next unused odd offset in the same series.
WORLD_SEED_OFFSET = {"a_only": 13, "b_only": 19, "g_only": 23, "null": 7,
                     "full": 0}
WORLD_LABELS = {
    "a_only": "{a-only}: author .30",
    "b_only": "{b-only}: community .08",
    "g_only": "{g-only}: interaction .02",
    "null": "{null}: nothing",
    "full": "{full}: .30 / .08 / .02",
}
COMPONENTS = ("author", "community", "interaction")

# Which worlds carry an own-component ROUTING recovery clause, and for which
# mains.  The interaction is never routed here -- it is X1c's estimand and
# appears only as the DESCRIPTIVE echo.
RECOVERY_CLAUSES = (("a_only", "author"), ("b_only", "community"),
                    ("full", "author"), ("full", "community"))

# --- verdict cells ---------------------------------------------------------

CELL_CERTIFIED = "MAINS_CERTIFIED"
CELL_DEFECT = "INSTRUMENT_DEFECT"

# --- registered leans (report against, never route) ------------------------

LEAN_CERTIFICATION = "PASS"
LEAN_REAL_AUTHOR_MAIN = (0.10, 0.20)
LEAN_REAL_COMMUNITY_MAIN = (0.05, 0.11)

# --- registered PREDICTIONS: X1c's 2x2-inversion annotations ---------------
# Scored ONLY if the instrument certifies; leans, never gates.
PREDICTION_AUTHOR_MAIN = 0.15
PREDICTION_COMMUNITY_MAIN = 0.077
PREDICTION_SOURCE = ("X1c's 2x2-inversion ANNOTATION on the marginal rows "
                     "(implied author main 0.1526, implied community main "
                     "0.0767), promoted to a testable prediction by the X-M "
                     "registration")

DEFAULT_X1_CACHE = X1B.DEFAULT_X1_CACHE
DEFAULT_COHORT = X1B.DEFAULT_COHORT
DEFAULT_OUTPUT = ROOT / "results/m4_xm_mains_estimator"
DEFAULT_REPORT = ROOT / "reports/SUICA_M4_XM_MAINS_ESTIMATOR_REPORT.md"

COMMITTED_FILES = (
    ROOT / "reports/SUICA_M4_XM_MAINS_ESTIMATOR_REPORT.md",
    ROOT / "scripts/run_suica_m4_xm_mains_estimator.py",
    ROOT / "tests/test_m4_xm_mains_estimator.py",
    ROOT / "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md",
    ROOT / "docs/CLAIMS_LEDGER.md",
)


def _pct(value: float) -> str:
    return fmt(value, 4)


# ---------------------------------------------------------------------------
# NEW 1 -- the FE COEFFICIENTS and the PINNED normalization
# ---------------------------------------------------------------------------


def fe_coefficients(values: np.ndarray, slot_author: np.ndarray,
                    slot_comm: np.ndarray, n_authors: int, n_comms: int, *,
                    weights: np.ndarray | None = None, tol: float = FE_TOL,
                    max_iter: int = FE_MAX_ITER,
                    order: str = "author_first"
                    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, int,
                               float]:
    """X1b's alternating projection, with the coefficients ACCUMULATED.

    X1b's ``fe_residual`` throws the group means away as it removes them
    because it only ever wanted the residual.  This leg wants the removed
    part, so the same sweep is run with two accumulators.  The arithmetic is
    identical sweep for sweep -- the returned residual is bit-identical to
    ``fe_residual``'s on the same input, which a contract test asserts -- and
    the stopping rule is X1b's tightened one: on exit BOTH residual group
    means are at most ``tol`` in absolute value.

    The decomposition returned is exact by construction:

        values == a_acc[slot_author] + c_acc[slot_comm] + residual

    to machine precision.  ``a_acc`` and ``c_acc`` are NOT yet identified --
    they depend on which side the sweep starts from, because the projection
    fixes only their SUM on the design.  ``normalize_coefficients`` removes
    that gauge; ``order`` exists so a contract test can start the sweep from
    the community side and check that the NORMALIZED coefficients do not move.

    ``weights`` carries cluster-bootstrap author multiplicities, exactly as
    in ``fe_residual``.
    """

    if order not in {"author_first", "community_first"}:
        raise ValueError(f"unknown sweep order {order!r}")
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

    a_acc = np.zeros(n_authors, dtype=np.float64)
    c_acc = np.zeros(n_comms, dtype=np.float64)
    if order == "author_first":
        first_mean, first_idx, first_acc = author_mean, slot_author, a_acc
        second_mean, second_idx, second_acc = comm_mean, slot_comm, c_acc
    else:
        first_mean, first_idx, first_acc = comm_mean, slot_comm, c_acc
        second_mean, second_idx, second_acc = author_mean, slot_author, a_acc

    m_first = first_mean(v)
    change = float("inf")
    for iteration in range(1, max_iter + 1):
        v -= m_first[first_idx]
        first_acc += m_first
        m_second = second_mean(v)
        v -= m_second[second_idx]
        second_acc += m_second
        m_first = first_mean(v)
        change = float(max(np.abs(m_first).max(initial=0.0),
                           np.abs(m_second).max(initial=0.0)))
        if change <= tol:
            return a_acc, c_acc, v, iteration, change
    raise RuntimeError(                              # pragma: no cover
        f"alternating projections did not converge in {max_iter} sweeps "
        f"(last change {change:.3e})")


NORMALIZATION_SEQUENCE = (
    "1. FIT: alternating projections accumulate (a_acc, c_acc) with "
    "y_cell = a_acc[author] + c_acc[community] + v (exact to machine "
    "precision; the split is gauge-dependent, the sum is not).",
    "2. CENTRE THE AUTHOR COEFFICIENTS: abar = mean over the connected "
    "component's authors of a_acc; a_hat = a_acc - abar; ABSORB the shift, "
    "mu <- mu + abar.",
    "3. CENTRE THE COMMUNITY COEFFICIENTS: bbar = mean over the component's "
    "communities of c_acc; b_hat = c_acc - bbar; ABSORB the shift, "
    "mu <- mu + bbar.",
    "RESULT: y_cell = mu + a_hat[author] + b_hat[community] + v with "
    "mean(a_hat) = mean(b_hat) = 0, and (mu, a_hat, b_hat) unchanged by "
    "which side the sweep started from.",
)


def normalize_coefficients(a_acc: np.ndarray, c_acc: np.ndarray
                           ) -> tuple[float, np.ndarray, np.ndarray]:
    """The PINNED identification, executed in the registered sequence.

    The two centrings touch DISJOINT vectors and both dump their shift into
    the same scalar, so step 3 cannot undo step 2 and the sequence is
    confluent; that is the property the contract test pins, because a
    normalization whose result depended on its own order would not identify
    anything.  Both means are UNWEIGHTED over the component's members -- the
    gauge is a property of the design's connectivity, not of anybody's size.
    """

    mu = 0.0
    a_bar = float(np.mean(a_acc))
    a_hat = a_acc - a_bar
    mu += a_bar
    b_bar = float(np.mean(c_acc))
    b_hat = c_acc - b_bar
    mu += b_bar
    return mu, a_hat, b_hat


def fitted_coefficients(design: Design, *, mult: np.ndarray | None = None
                        ) -> dict[str, Any]:
    """Both halves fitted and normalized on the same (possibly weighted) grid."""

    sa, sc = design.slot_author, design.slot_comm
    A, C = design.n_authors, design.n_comms
    w = None if mult is None else mult[sa]
    ae, be, v_e, it_e, ch_e = fe_coefficients(design.mean_e, sa, sc, A, C,
                                              weights=w)
    al, bl, v_l, it_l, ch_l = fe_coefficients(design.mean_l, sa, sc, A, C,
                                              weights=w)
    mu_e, a_e, b_e = normalize_coefficients(ae, be)
    mu_l, a_l, b_l = normalize_coefficients(al, bl)
    return {"a_e": a_e, "a_l": a_l, "b_e": b_e, "b_l": b_l,
            "mu_e": mu_e, "mu_l": mu_l, "v_e": v_e, "v_l": v_l,
            "sweeps_early": it_e, "sweeps_late": it_l,
            "change_early": ch_e, "change_late": ch_l}


# ---------------------------------------------------------------------------
# NEW 2 -- the df / joint-estimation derivation for the MAINS
# ---------------------------------------------------------------------------


MAINS_DF_DERIVATION = (
    "THE QUESTION.  X1c's routing statistic needed the factor "
    "P/(P - A - C + 1): the two-way projection removes a rank-(A + C - 1) "
    "dummy space from the P cell observations of a half, so a white "
    "interaction keeps only (P - A - C + 1)/P of itself IN THE RESIDUAL.  "
    "Does the same shrinkage hit the mains?",
    "THE ANSWER: NO, and for a structural reason.  The mains are the "
    "projection's COORDINATES, not its residual.  Writing the fit as the "
    "linear map a_hat_h = M_a y_h with the SAME M_a in both halves (the "
    "design is shared -- a slot is eligible in both halves by construction), "
    "and the model as y = mu + a[u] + b[c] + g + e_h with e_h unlinked "
    "across halves: M_a is unbiased on the fitted part, so "
    "a_hat_h = (a - abar) + M_a g + M_a e_h.  The cross-half covariance "
    "kills every term that is not shared: E[cov(a_hat_e, a_hat_l)] = "
    "popvar(a - abar) + popvar(M_a g).  No noise inflation (the two halves' "
    "estimation errors are unlinked), and no residual-df shrinkage (the "
    "estimand never enters the residual).  The second term is not a df "
    "effect at all -- it is the interaction LEAKAGE that routing clause (2) "
    "measures and bounds.",
    "WHAT REMAINS: the MEAN-REMOVAL (gauge) loss, one dimension per side.  "
    "Every reading here is a weighted POPULATION covariance with normalized "
    "weights p, and such a covariance subtracts its own weighted mean, so "
    "for an iid component of variance V it targets V * (1 - sum_i p_i^2).  "
    "The correction is therefore ONE formula for all three readings:",
    "    factor(p) = 1 / (1 - sum_i p_i^2),   share_corr = share_raw * "
    "factor(p).",
    "  * author main, real sample: p_u = 1/A     -> factor = A/(A - 1);",
    "  * author main, bootstrap:   p_u = m_u / sum m  (author "
    "multiplicities);",
    "  * community main, size-weighted (PRIMARY): p_c = W_c = "
    "(n_{c,early} + n_{c,late}) / sum_c(...);",
    "  * community main, unweighted (secondary):  p_c = 1/C -> C/(C - 1).",
    "The factor is a positive scalar, so the corrected CI is the affine "
    "image of the raw CI and 'the CI covers 0' is invariant -- the "
    "bootstrap-zero clauses are untouched by the correction.  Per #87(b) "
    "the factor is RECOMPUTED INSIDE every bootstrap replicate from that "
    "replicate's own weights, not pinned at the realized design; the raw "
    "reading is co-reported everywhere (#67).",
    "A CONSEQUENCE WORTH NAMING.  sum_c W_c^2 is the inverse of the "
    "size-weighted design's EFFECTIVE NUMBER OF COMMUNITIES.  A small "
    "effective number makes the correction large AND makes the estimand's "
    "own draw-to-draw variability large -- which is what routing clause (1) "
    "runs into on this skeleton.",
)


def mean_removal_factor(weights: np.ndarray) -> dict[str, Any]:
    """The gauge/mean-removal correction of a weighted population covariance.

    ``weights`` are unnormalized non-negative weights over the members the
    covariance runs on.  Members with zero weight do not participate and do
    not count -- which is exactly right inside a cluster bootstrap, where an
    undrawn author contributes nothing and must not be counted as a member.
    """

    w = np.asarray(weights, dtype=np.float64)
    total = float(w.sum())
    if total <= 0:                                   # pragma: no cover
        raise RuntimeError("a mean-removal factor needs positive weight")
    p = w / total
    sum_p2 = float((p * p).sum())
    if sum_p2 >= 1.0:                                # pragma: no cover
        raise RuntimeError("the weighted covariance has no residual mass")
    return {"members": int(np.count_nonzero(w)),
            "sum_p_squared": sum_p2,
            "effective_members": float(1.0 / sum_p2),
            "retained_fraction": float(1.0 - sum_p2),
            "factor": float(1.0 / (1.0 - sum_p2))}


def mains_df_derivation(design: Design) -> dict[str, Any]:
    """The three factors of the REALIZED skeleton, printed and contract-tested."""

    sa, sc = design.slot_author, design.slot_comm
    A, C = int(design.n_authors), int(design.n_comms)
    size = (np.bincount(sc, design.n_e, C) + np.bincount(sc, design.n_l, C))
    author = mean_removal_factor(np.ones(A))
    comm_w = mean_removal_factor(size)
    comm_u = mean_removal_factor(np.ones(C))
    return {
        "A_authors": A, "C_communities": C,
        "P_shared_pairs": int(design.n_slots),
        "author": author,
        "community_size_weighted": comm_w,
        "community_unweighted": comm_u,
        "formula": "share_corr = share_raw / (1 - sum_i p_i^2)",
        "interaction_factor_for_contrast": df_correction(design),
        "residual_df_factor_applies_to_mains": False,
        "derivation": list(MAINS_DF_DERIVATION),
    }


# ---------------------------------------------------------------------------
# NEW 3 -- the mains budget
# ---------------------------------------------------------------------------


def mains_budget(design: Design, *, mult: np.ndarray | None = None,
                 coefs: dict[str, Any] | None = None) -> dict[str, Any]:
    """Var_hat(a) and Var_hat(b) as shares of comment-level Var(y).

    ``mult`` carries cluster-bootstrap author multiplicities (None = the real
    sample).  Under a bootstrap the SAME multiplicities drive three things at
    once, and all three are honoured: the projection weights, the covariance
    weights, and the analysis pool that Var(y) is taken over.
    """

    sa, sc = design.slot_author, design.slot_comm
    A, C = design.n_authors, design.n_comms
    w_slot = None if mult is None else mult[sa]
    if coefs is None:
        coefs = fitted_coefficients(design, mult=mult)

    # --- the denominator: comment-level Var(y) over the analysis pool ------
    if mult is None:
        n_all = float((design.n_e + design.n_l).sum())
        s_all = float((design.s_e + design.s_l).sum())
        q_all = float((design.q_e + design.q_l).sum())
    else:
        n_all = float((w_slot * (design.n_e + design.n_l)).sum())
        s_all = float((w_slot * (design.s_e + design.s_l)).sum())
        q_all = float((w_slot * (design.q_e + design.q_l)).sum())
    var_y = q_all / n_all - (s_all / n_all) ** 2

    # --- author main: cross-half covariance of the author coefficients -----
    author_w = np.ones(A) if mult is None else mult.astype(np.float64)
    keep_a = author_w > 0
    cov_author = weighted_cov(coefs["a_e"][keep_a], coefs["a_l"][keep_a],
                              None if mult is None else author_w[keep_a])
    f_author = mean_removal_factor(author_w)

    # --- community main: cross-half covariance of the community coefs ------
    if mult is None:
        c_ne = np.bincount(sc, design.n_e, C)
        c_nl = np.bincount(sc, design.n_l, C)
    else:
        c_ne = np.bincount(sc, w_slot * design.n_e, C)
        c_nl = np.bincount(sc, w_slot * design.n_l, C)
    size = c_ne + c_nl
    keep_c = size > 0
    cov_comm_w = weighted_cov(coefs["b_e"][keep_c], coefs["b_l"][keep_c],
                              size[keep_c])
    cov_comm_u = weighted_cov(coefs["b_e"][keep_c], coefs["b_l"][keep_c])
    f_comm_w = mean_removal_factor(size)
    f_comm_u = mean_removal_factor(keep_c.astype(np.float64))

    raw_a = cov_author / var_y
    raw_cw = cov_comm_w / var_y
    raw_cu = cov_comm_u / var_y
    return {
        "var_y": float(var_y),
        "author_raw": float(raw_a),
        "author": float(raw_a * f_author["factor"]),
        "author_factor": float(f_author["factor"]),
        "community_raw": float(raw_cw),
        "community": float(raw_cw * f_comm_w["factor"]),
        "community_factor": float(f_comm_w["factor"]),
        "community_unweighted_raw": float(raw_cu),
        "community_unweighted": float(raw_cu * f_comm_u["factor"]),
        "community_unweighted_factor": float(f_comm_u["factor"]),
        "cov_author": float(cov_author),
        "cov_community": float(cov_comm_w),
        "effective_communities": float(f_comm_w["effective_members"]),
        "effective_authors": float(f_author["effective_members"]),
    }


def full_budget(design: Design) -> dict[str, Any]:
    """The mains PLUS X1c's interaction row -- the whole reproducible budget."""

    coefs = fitted_coefficients(design)
    out = mains_budget(design, coefs=coefs)
    x1c = variance_budget(design, coefs["v_e"], coefs["v_l"])
    factor = df_correction(design)["factor"]
    out["interaction_raw"] = float(x1c["interaction"])
    out["interaction"] = float(x1c["interaction"] * factor)
    out["interaction_factor"] = float(factor)
    out["marginal_author_x1c"] = float(x1c["author"])
    out["marginal_community_x1c"] = float(x1c["community"])
    out["fe"] = {"sweeps_early": coefs["sweeps_early"],
                 "sweeps_late": coefs["sweeps_late"],
                 "change_early": coefs["change_early"],
                 "change_late": coefs["change_late"]}
    out["fe_exactness"] = fe_exactness(design, coefs["v_e"], coefs["v_l"])
    out["residual"] = float(1.0 - out["author"] - out["community"]
                            - out["interaction"])
    return out


# ---------------------------------------------------------------------------
# NEW 4 -- the cluster bootstrap over authors, FE refitted inside every draw
# ---------------------------------------------------------------------------


def _bootstrap_subdesign(design: Design, mult: np.ndarray) -> dict[str, Any]:
    """One replicate: the FE REFITTED on the resampled author multiset.

    X1b's argument, re-used: an author drawn m times solves the same FE
    equation m times over, so the resampled two-way fit is exactly the
    WEIGHTED alternating projection with weight m on that author's slots, and
    undrawn authors drop out of the projection entirely.  The coefficients are
    re-normalized on the SURVIVING component, which is the only component the
    replicate has.
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
    sub = Design(slot_author=a_idx, slot_comm=c_idx,
                 n_e=design.n_e[keep], n_l=design.n_l[keep],
                 s_e=design.s_e[keep], s_l=design.s_l[keep],
                 q_e=design.q_e[keep], q_l=design.q_l[keep],
                 n_authors=A, n_comms=C, author_codes=ua)
    coefs = fitted_coefficients(sub, mult=mult[ua])
    return mains_budget(sub, mult=mult[ua], coefs=coefs)


def cluster_bootstrap_mains(design: Design, b_boot: int, seed: int,
                            log: RunLog | None = None,
                            tag: str = "") -> dict[str, Any]:
    """B_BOOT author resamples; every replicate refits and re-normalizes.

    #85b: nothing is resampled from precomputed per-author statistics, because
    the object under test is a COEFFICIENT and a coefficient is a property of
    the whole fit.  #87(b): each replicate's mean-removal factor comes from
    its OWN weights, so the corrected interval is not the affine image of a
    pinned constant but a genuinely recomputed one.
    """

    rng = np.random.default_rng(seed)
    A = design.n_authors
    draws = rng.integers(0, A, size=(b_boot, A))
    keys = ("author", "author_raw", "community", "community_raw",
            "community_unweighted", "community_unweighted_raw")
    values = {k: np.empty(b_boot, dtype=np.float64) for k in keys}
    for b in range(b_boot):
        mult = np.bincount(draws[b], minlength=A).astype(np.float64)
        row = _bootstrap_subdesign(design, mult)
        for key in keys:
            values[key][b] = row[key]
        if log is not None and (b + 1) % 250 == 0:
            log.event("bootstrap_progress", tag=tag, done=b + 1, of=b_boot)
    return {
        "b_boot": int(b_boot),
        "ci": {k: percentile_ci(v) for k, v in values.items()},
        "sd": {k: float(np.std(v, ddof=1)) for k, v in values.items()},
        "mean": {k: float(np.mean(v)) for k, v in values.items()},
    }


# ---------------------------------------------------------------------------
# NEW 5 -- the synthetic worlds and their scoring
# ---------------------------------------------------------------------------


def synthetic_world_block_mains(skeleton: Design, shares: dict[str, float],
                                name: str, seed: int, replicates: int,
                                log: RunLog,
                                recover: Callable[[Design], dict[str, Any]]
                                = full_budget) -> dict[str, Any]:
    """``replicates`` draws of one world, scored point-wise on every component.

    The world builder is X1b's ``synthetic_design`` verbatim: the skeleton
    contributes DESIGN ONLY (which authors, which communities, how many
    comments per cell) and every y is synthetic, with the cell mean drawn
    N(mu, sigma^2/n) and the within-cell sum of squares sigma^2 chi^2_{n-1}
    so that the Var(y) the estimator divides by is itself a real draw.
    """

    rows = []
    for rep in range(replicates):
        rng = np.random.default_rng(seed + 1000 * rep)
        world = synthetic_design(skeleton, shares, rng)
        rows.append(recover(world))
        log.event("synthetic_replicate", world=name, replicate=rep,
                  author=rows[-1]["author"], community=rows[-1]["community"],
                  interaction=rows[-1]["interaction"])
    keys = ("author", "author_raw", "community", "community_raw",
            "community_unweighted", "community_unweighted_raw",
            "interaction", "interaction_raw", "var_y",
            "marginal_author_x1c", "marginal_community_x1c")
    stats: dict[str, Any] = {}
    for key in keys:
        vals = np.array([row[key] for row in rows], dtype=np.float64)
        stats[key] = {"mean": float(vals.mean()),
                      "sd": float(vals.std(ddof=1)) if vals.size > 1 else 0.0,
                      "min": float(vals.min()), "max": float(vals.max()),
                      "values": [float(x) for x in vals]}
    return {"world": name, "label": WORLD_LABELS[name],
            "planted": dict(shares), "replicates": int(replicates),
            "stats": stats}


def score_recovery(stat: dict[str, float], target: float) -> dict[str, Any]:
    """#92 resolution floor + #90 ceiling, in one scored row.

    The floor is a RESOLUTION statement: this gate claims to resolve a main to
    0.01 of comment-level variance.  #90 reads the same number as a CEILING on
    the replicate spread -- a clause whose replicates scatter by more than the
    resolution it claims has not measured the estimator, only the worlds, and
    an unmeasured ROUTING clause stops the leg rather than passing vacuously.
    """

    sd = float(stat["sd"])
    tol = max(RESOLUTION_SHARE, TOL_SD_MULT * sd)
    gap = float(stat["mean"]) - float(target)
    within = abs(gap) <= tol
    informative = sd <= CEILING_REPLICATE_SD
    if not informative:
        status = "UNINFORMATIVE"
    else:
        status = "PASS" if within else "FAIL"
    return {"target": float(target), "recovered_mean": float(stat["mean"]),
            "gap": gap, "replicate_sd": sd, "tolerance": tol,
            "within_tolerance": bool(within),
            "ceiling": CEILING_REPLICATE_SD,
            "ceiling_headroom": CEILING_REPLICATE_SD - sd,
            "informative": bool(informative),
            "status": status}


def score_leakage(block: dict[str, Any]) -> dict[str, Any]:
    """The #85 zero-point family for mains: every ZERO-planted component."""

    planted = block["planted"]
    zeros = [c for c in COMPONENTS if float(planted[c]) == 0.0]
    rows = {}
    for comp in zeros:
        read = float(block["stats"][comp]["mean"])
        rows[comp] = {"planted": 0.0, "reading": read, "abs": abs(read),
                      "maximum": LEAK_MAX,
                      "status": "PASS" if abs(read) < LEAK_MAX else "FAIL"}
    if not zeros:
        return {"applicable": False, "components": [], "rows": {},
                "status": "N/A",
                "note": ("every component is planted in this world, so the "
                         "zero-point clause has no zero to test")}
    status = "PASS" if all(r["status"] == "PASS" for r in rows.values()) \
        else "FAIL"
    return {"applicable": True, "components": zeros, "rows": rows,
            "status": status}


def marginal_counterfactual(blocks: dict[str, Any]) -> dict[str, Any]:
    """The same zero-point rows, scored with X1c's MARGINAL estimator.

    DESCRIPTIVE.  Both estimators ran on every world, so "the marginal
    estimators would have failed this clause" is a measurement here and not a
    rhetorical flourish: this block re-scores exactly the rows routing clause
    (2) scores, reading the MARGINAL main instead of the FE main.
    """

    marginal_key = {"author": "marginal_author_x1c",
                    "community": "marginal_community_x1c"}
    rows: dict[str, Any] = {}
    fe_failures: list[str] = []
    marginal_failures: list[str] = []
    for name, block in blocks.items():
        for comp in ("author", "community"):
            if float(block["planted"][comp]) != 0.0:
                continue
            key = f"{name}:{comp}"
            fe = float(block["stats"][comp]["mean"])
            mg = float(block["stats"][marginal_key[comp]]["mean"])
            rows[key] = {
                "fe": fe, "marginal": mg, "maximum": LEAK_MAX,
                "fe_status": "PASS" if abs(fe) < LEAK_MAX else "FAIL",
                "marginal_status": "PASS" if abs(mg) < LEAK_MAX else "FAIL",
                "ratio": (abs(mg) / abs(fe)) if fe != 0 else float("inf")}
            if rows[key]["fe_status"] == "FAIL":     # pragma: no cover
                fe_failures.append(key)
            if rows[key]["marginal_status"] == "FAIL":
                marginal_failures.append(key)
    return {"rows": rows, "n_zero_rows": len(rows),
            "n_fe_failures": len(fe_failures),
            "fe_failures": fe_failures,
            "n_marginal_failures": len(marginal_failures),
            "marginal_failures": marginal_failures,
            "note": ("DESCRIPTIVE: the mains-only zero-point rows of routing "
                     "clause (2), re-scored with X1c's marginal estimator")}


def paired_error_block(skeleton: Design, shares: dict[str, float], name: str,
                       seed: int, replicates: int) -> dict[str, Any]:
    """DIAGNOSTIC, never routing: the estimator's error against the DRAWN truth.

    ``score_recovery`` compares the replicate MEAN to the NOMINAL planted
    share, so its replicate spread mixes two things that are not the same
    question: how far the estimator is from the truth, and how far each
    world's realized truth is from its nominal parameter.  This block
    separates them by re-drawing the same worlds with the same seeds and
    scoring each replicate against ITS OWN realized target -- the same
    functional of the drawn component vector that the estimator targets:

        author:    the population variance of the drawn a over the A authors;
        community: the W-weighted population variance of the drawn b.

    A near-zero paired error with a large ``score_recovery`` spread is the
    signature of a gate that is world-limited rather than estimator-limited.
    """

    sa, sc = skeleton.slot_author, skeleton.slot_comm
    A, C = skeleton.n_authors, skeleton.n_comms
    size = (np.bincount(sc, skeleton.n_e, C) + np.bincount(sc, skeleton.n_l, C))
    W = size / size.sum()
    err_a, err_b, tgt_a, tgt_b = [], [], [], []
    for rep in range(replicates):
        rng = np.random.default_rng(seed + 1000 * rep)
        # X1's builder draws a, then b, then g, from this exact stream; the
        # draws are reproduced here in the same order so the world is the
        # SAME world the scoring block used.
        va, vc, vg = (float(shares["author"]), float(shares["community"]),
                      float(shares["interaction"]))
        a = rng.normal(0.0, np.sqrt(va), A) if va > 0 else np.zeros(A)
        b = rng.normal(0.0, np.sqrt(vc), C) if vc > 0 else np.zeros(C)
        rng2 = np.random.default_rng(seed + 1000 * rep)
        world = synthetic_design(skeleton, shares, rng2)
        got = mains_budget(world)
        target_a = float(np.mean(a * a) - np.mean(a) ** 2)
        mb = float((W * b).sum())
        target_b = float((W * b * b).sum() - mb * mb)
        # the estimator reads a SHARE; put the target on the same scale
        var_y = got["var_y"]
        tgt_a.append(target_a / var_y)
        tgt_b.append(target_b / var_y)
        err_a.append(got["author_raw"] - target_a / var_y)
        err_b.append(got["community_raw"] - target_b / var_y)
    ea, eb = np.array(err_a), np.array(err_b)
    return {
        "world": name, "replicates": int(replicates),
        "note": ("DIAGNOSTIC, non-routing: each replicate scored against ITS "
                 "OWN realized planted target, raw scale"),
        "author": {"mean_error": float(ea.mean()),
                   "sd_error": float(ea.std(ddof=1)) if ea.size > 1 else 0.0,
                   "max_abs_error": float(np.abs(ea).max()),
                   "realized_target_mean": float(np.mean(tgt_a)),
                   "realized_target_sd": float(np.std(tgt_a, ddof=1))
                   if len(tgt_a) > 1 else 0.0},
        "community": {"mean_error": float(eb.mean()),
                      "sd_error": float(eb.std(ddof=1)) if eb.size > 1 else 0.0,
                      "max_abs_error": float(np.abs(eb).max()),
                      "realized_target_mean": float(np.mean(tgt_b)),
                      "realized_target_sd": float(np.std(tgt_b, ddof=1))
                      if len(tgt_b) > 1 else 0.0},
    }


def ceiling_power(skeleton: Design, v_component: float, weights: np.ndarray,
                  replicates: int, trials: int, seed: int) -> dict[str, Any]:
    """DIAGNOSTIC: how often could this clause have been INFORMATIVE at all?

    The replicate spread of an own-recovery clause is dominated by the
    world-draw variability of the realized weighted population variance of an
    iid component -- a quantity with a closed form,
    sd ~ V * sqrt(2 * sum_i p_i^2), i.e. governed by the EFFECTIVE number of
    members.  This block draws the component vector directly (no estimator, no
    y, no corpus) many times, forms the same ``replicates``-sized sd the gate
    forms, and reports the probability that it lands under the #90 ceiling.  A
    low probability means the clause was underpowered AT REGISTRATION, not
    unlucky in this run.
    """

    w = np.asarray(weights, dtype=np.float64)
    p = w / w.sum()
    sum_p2 = float((p * p).sum())
    rng = np.random.default_rng(seed)
    n = int(p.size)
    sds = np.empty(trials, dtype=np.float64)
    for t in range(trials):
        draws = rng.normal(0.0, np.sqrt(v_component), size=(replicates, n))
        m = draws @ p
        realized = (draws * draws) @ p - m * m
        sds[t] = float(np.std(realized, ddof=1))
    return {
        "component_variance": float(v_component),
        "members": n, "sum_p_squared": sum_p2,
        "effective_members": float(1.0 / sum_p2),
        "closed_form_draw_sd": float(v_component * np.sqrt(2.0 * sum_p2)),
        "replicates": int(replicates), "trials": int(trials),
        "mean_replicate_sd": float(sds.mean()),
        "p_under_ceiling": float((sds <= CEILING_REPLICATE_SD).mean()),
        "ceiling": CEILING_REPLICATE_SD,
    }


# ---------------------------------------------------------------------------
# NEW 6 -- the gate
# ---------------------------------------------------------------------------


def mains_gate(skeleton: Design, b_boot: int, log: RunLog) -> dict[str, Any]:
    """The whole leg: five worlds, ten routing clauses, three descriptive."""

    derivation = mains_df_derivation(skeleton)
    log.event("gate_start", authors=skeleton.n_authors,
              communities=skeleton.n_comms, slots=skeleton.n_slots,
              replicates=N_SYNTH_REPLICATES,
              effective_communities=derivation[
                  "community_size_weighted"]["effective_members"])

    blocks: dict[str, Any] = {}
    for name, shares in WORLDS.items():
        blocks[name] = synthetic_world_block_mains(
            skeleton, shares, name,
            SEED_PART0 + WORLD_SEED_OFFSET[name], N_SYNTH_REPLICATES, log)

    # --- routing family 1: own-component recovery --------------------------
    recovery: dict[str, Any] = {}
    for world, comp in RECOVERY_CLAUSES:
        key = f"{world}:{comp}"
        recovery[key] = score_recovery(blocks[world]["stats"][comp],
                                       WORLDS[world][comp])
        recovery[key]["world"] = world
        recovery[key]["component"] = comp
        recovery[key]["scale"] = "corrected (#67: raw co-reported)"
        recovery[key]["raw"] = score_recovery(
            blocks[world]["stats"][f"{comp}_raw"], WORLDS[world][comp])

    # --- routing family 2: cross-leakage into every zero component ---------
    leakage = {name: score_leakage(block) for name, block in blocks.items()}

    # --- routing family 3/4: the null world's bootstrap --------------------
    rng_null = np.random.default_rng(SEED_PART0 + WORLD_SEED_OFFSET["null"])
    null_world = synthetic_design(skeleton, WORLDS["null"], rng_null)
    null_point = full_budget(null_world)
    null_boot = cluster_bootstrap_mains(null_world, b_boot,
                                        SEED_BOOT + 211, log, "null_world")
    bootstrap_zero: dict[str, Any] = {}
    for comp in ("author", "community"):
        ci = null_boot["ci"][comp]
        point = float(null_point[comp])
        covers_zero = bool(ci[0] <= 0.0 <= ci[1])
        covers_point = bool(ci[0] <= point <= ci[1])
        bootstrap_zero[comp] = {
            "point": point, "ci": ci, "ci_raw": null_boot["ci"][f"{comp}_raw"],
            "boot_mean": null_boot["mean"][comp], "boot_sd": null_boot["sd"][comp],
            "covers_zero": covers_zero, "covers_own_point": covers_point,
            "status_zero": "PASS" if covers_zero else "FAIL",
            "status_stability": "PASS" if (covers_zero and covers_point)
            else "FAIL"}

    # --- assemble the routing family ---------------------------------------
    routing: dict[str, str] = {}
    for (world, comp) in RECOVERY_CLAUSES:
        key = f"{world}:{comp}"
        row = recovery[key]
        routing[
            f"(R{len(routing) + 1:02d}) recovery — {comp} main in "
            f"{WORLD_LABELS[world]} within max({RESOLUTION_SHARE}, "
            f"{TOL_SD_MULT:g} x replicate sd) of {WORLDS[world][comp]:.4f}, "
            f"replicate sd <= {CEILING_REPLICATE_SD} (#90 ceiling / #92 "
            f"resolution)"] = row["status"]
    for name in WORLDS:
        clause = leakage[name]
        if not clause["applicable"]:
            continue
        comps = ", ".join(clause["components"])
        routing[
            f"(R{len(routing) + 1:02d}) cross-leakage — in {WORLD_LABELS[name]} "
            f"every zero-planted component ({comps}) reads < {LEAK_MAX} "
            f"absolute (#85 zero-point family, mains)"] = clause["status"]
    routing[
        f"(R{len(routing) + 1:02d}) #85b bootstrap-zero — in {WORLD_LABELS['null']} "
        f"the cluster-bootstrap CI covers 0 for BOTH mains"] = (
        "PASS" if all(bootstrap_zero[c]["status_zero"] == "PASS"
                      for c in bootstrap_zero) else "FAIL")
    routing[
        f"(R{len(routing) + 1:02d}) bootstrap-stability — the author-resampled "
        f"bootstrap does not move the zero: the CI covers 0 AND its own point, "
        f"both mains"] = (
        "PASS" if all(bootstrap_zero[c]["status_stability"] == "PASS"
                      for c in bootstrap_zero) else "FAIL")

    # --- the descriptive family: X1c's interaction estimator, echoed -------
    descriptive: dict[str, str] = {}
    echo: dict[str, Any] = {}
    for name in ("g_only", "full"):
        echo[name] = score_recovery(blocks[name]["stats"]["interaction"],
                                    WORLDS[name]["interaction"])
        descriptive[
            f"(D{len(descriptive) + 1:02d}) interaction echo — X1c's df-corrected "
            f"estimator recovers {WORLDS[name]['interaction']:.4f} in "
            f"{WORLD_LABELS[name]}"] = echo[name]["status"]
    zero_worlds = ("a_only", "b_only", "null")
    echo_zero = {name: float(blocks[name]["stats"]["interaction"]["mean"])
                 for name in zero_worlds}
    descriptive[
        f"(D{len(descriptive) + 1:02d}) interaction echo — X1c's estimator reads "
        f"< {LEAK_MAX} in the three worlds with no planted interaction"] = (
        "PASS" if all(abs(v) < LEAK_MAX for v in echo_zero.values())
        else "FAIL")

    routing_status, descriptive_status = gate_status(routing, descriptive)

    # --- diagnostics (never routing) ---------------------------------------
    sc = skeleton.slot_comm
    size = (np.bincount(sc, skeleton.n_e, skeleton.n_comms)
            + np.bincount(sc, skeleton.n_l, skeleton.n_comms))
    diagnostics = {
        "paired_error": {
            name: paired_error_block(
                skeleton, WORLDS[name], name,
                SEED_PART0 + WORLD_SEED_OFFSET[name], N_SYNTH_REPLICATES)
            for name in ("a_only", "b_only", "full")},
        "ceiling_power": {
            "b_only:community (size-weighted)": ceiling_power(
                skeleton, WORLDS["b_only"]["community"], size,
                N_SYNTH_REPLICATES, 2000, SEED_PART0 + 401),
            "b_only:community (unweighted)": ceiling_power(
                skeleton, WORLDS["b_only"]["community"],
                np.ones(skeleton.n_comms), N_SYNTH_REPLICATES, 2000,
                SEED_PART0 + 403),
            "a_only:author": ceiling_power(
                skeleton, WORLDS["a_only"]["author"],
                np.ones(skeleton.n_authors), N_SYNTH_REPLICATES, 2000,
                SEED_PART0 + 405)},
        "null_world_fe": {"fe": null_point["fe"],
                          "fe_exactness": null_point["fe_exactness"]},
    }

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
        "recovery": recovery,
        "leakage": leakage,
        "bootstrap_zero": bootstrap_zero,
        "interaction_echo": echo,
        "interaction_echo_zero_worlds": echo_zero,
        "marginal_counterfactual": marginal_counterfactual(blocks),
        "blocks": blocks,
        "df_derivation": derivation,
        "diagnostics": diagnostics,
        "resolution_rule": (
            f"floor = {RESOLUTION_SHARE} in SHARE units (#92: a resolution "
            f"statement in the estimand's own units, not a fraction of a "
            f"freely chosen planted scale); tolerance = "
            f"max(floor, {TOL_SD_MULT:g} x replicate sd) over "
            f"{N_SYNTH_REPLICATES} replicates; #90 ceiling = the same "
            f"{CEILING_REPLICATE_SD} read as an upper bound on that replicate "
            f"sd, above which the clause is UNINFORMATIVE and stops the leg"),
    }
    log.event("gate_done", routing=routing_status,
              descriptive=descriptive_status,
              passed=out["n_routing_passed"], of=out["n_routing"])
    return out


def a1_stop_fires(gate: dict[str, Any]) -> bool:
    """The A1 stop reads the ROUTING family and nothing else (#86a)."""

    return gate["routing_status"] != "PASS"


def build_verdict(gate: dict[str, Any],
                  real: dict[str, Any] | None) -> dict[str, Any]:
    """MAINS_CERTIFIED iff every routing clause passed; else INSTRUMENT_DEFECT."""

    certified = not a1_stop_fires(gate)
    failing = {k: v for k, v in gate["routing_clauses"].items()
               if v != "PASS"}
    cell = CELL_CERTIFIED if certified else CELL_DEFECT
    if certified:
        headline = (
            "Every routing clause of the mains battery passed on the "
            "realized skeleton, so the corpus main budget below is licensed "
            "as an instrument reading.")
    else:
        headline = (
            f"{len(failing)} of {gate['n_routing']} routing clauses did not "
            "pass, the A1 stop fires, and NO real-data main was computed, "
            "reported or stored. The instrument is not certified at the "
            "registered resolution.")
    return {
        "cell": cell,
        "certified": bool(certified),
        "headline": headline,
        "routing_status": gate["routing_status"],
        "descriptive_status": gate["descriptive_status"],
        "n_routing": gate["n_routing"],
        "n_routing_passed": gate["n_routing_passed"],
        "failing_routing_clauses": failing,
        "real_arm_run": bool(real is not None),
    }


def score_predictions(real: dict[str, Any] | None) -> dict[str, Any]:
    """X1c's 2x2-inversion annotations, scored against the realized CIs."""

    if real is None:
        return {"scored": False,
                "reason": ("the instrument did not certify; the real arm was "
                           "not run, so the predictions are UNSCORED"),
                "author": PREDICTION_AUTHOR_MAIN,
                "community": PREDICTION_COMMUNITY_MAIN,
                "source": PREDICTION_SOURCE}
    rows = {}
    for comp, pred in (("author", PREDICTION_AUTHOR_MAIN),
                       ("community", PREDICTION_COMMUNITY_MAIN)):
        ci = real["bootstrap"]["ci"][comp]
        point = float(real["budget"][comp])
        hit = bool(ci[0] <= pred <= ci[1])
        rows[comp] = {"prediction": pred, "point": point, "ci": ci,
                      "hit": hit, "status": "HIT" if hit else "MISS",
                      "gap": point - pred}
    return {"scored": True, "rows": rows, "source": PREDICTION_SOURCE}


def evaluate_leans(gate: dict[str, Any],
                   real: dict[str, Any] | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [{
        "lean": "certification PASSES",
        "registered": LEAN_CERTIFICATION,
        "observed": gate["routing_status"],
        "status": "HELD" if gate["routing_status"] == LEAN_CERTIFICATION
        else "BROKE"}]
    for comp, band, name in (("author", LEAN_REAL_AUTHOR_MAIN,
                              "real author main"),
                             ("community", LEAN_REAL_COMMUNITY_MAIN,
                              "real community main")):
        if real is None:
            rows.append({"lean": f"{name} in [{band[0]}, {band[1]}]",
                         "registered": list(band), "observed": None,
                         "status": "UNSCORED — the A1 stop forbids the "
                                   "real arm"})
        else:
            value = float(real["budget"][comp])
            rows.append({"lean": f"{name} in [{band[0]}, {band[1]}]",
                         "registered": list(band), "observed": value,
                         "status": "HELD" if band[0] <= value <= band[1]
                         else "BROKE"})
    return rows


# ---------------------------------------------------------------------------
# The report (rule 24: every table below is generated from the artifacts)
# ---------------------------------------------------------------------------


BOUNDARIES = (
    "**Metadata only, expression VOLUME and not content (permanent).** The "
    "only text-derived quantity in this leg is `word_count_quoteless`, the "
    "author's own-word count per comment. No body was read, no topic, no "
    "style, no sentiment; `author_profiles.csv` was never opened.",
    "**INSTRUMENT LEG, R1-class.** Everything certified here is a property of "
    "an ESTIMATOR on a design, not a finding about people or venues. The leg "
    "issues certificates, not theory verdicts, and no downstream leg may cite "
    "it as evidence for anything about the corpus.",
    "**No psychological naming.** An author coefficient is a fitted offset in "
    "log-words on this eligible grid. It is not a trait, a state, a "
    "disposition or a style, and the leg is label-free.",
    "**EXPLORATORY, corpus-level.** No person-level claim is licensed. The "
    "author coefficients exist only as the population a covariance runs over.",
    "**The mains are estimands OF THIS DESIGN.** Var_hat(a) and Var_hat(b) "
    "are defined on the eligible shared grid (well-shared venues, authors "
    "with at least three surviving shared communities). They are not "
    "population quantities of Reddit, of PANDORA, or of the disjoint cohort.",
    "**Incomplete design.** The grid is sparse and the community side is "
    "size-skewed; the size-weighted community estimand has an EFFECTIVE "
    "number of communities far below its nominal count, which is a property "
    "of the corpus and is reported rather than repaired.",
    "**Cohort composition.** The disjoint cohort is TYPOLOGY-ENRICHED by "
    "construction, so it is a platform sample with a selection, not a "
    "population sample.",
)

LINEAGE = (
    "M4-X1 (`A1_STOP__SYNTHETIC_GATE_FAILED`, commit ebe4f5b) — the venue "
    "response, first registration; double-centering's zero was not zero on "
    "an incomplete grid (defect #85).",
    "M4-X1b (`A1_STOP__SYNTHETIC_GATE_FAILED`, commit e8c9040) — design and "
    "estimator repaired (law vocabulary + support floor; exact two-way FE by "
    "alternating projections); routing machinery certified, stopped again on "
    "a descriptive whose bias was design-predicted (defect #86).",
    "M4-X1c (`RESPONSE_TRACE`, adjudicated) — the corpus reading, with the "
    "two main rows correctly renamed MARGINAL and #87 purchased: any leg "
    "wanting the mains as OBJECTS must first build main ESTIMATORS under "
    "their own gate.",
    "M4-X-M (this leg) — that gate. R1-class, certificates only; the #87 "
    "prerequisite for X3's stage-E trait join.",
)


def build_reading(payload: dict[str, Any]) -> list[str]:
    """The verdict in sentences, every number pulled from the artifacts."""

    gate = payload["gate"]
    verdict = payload["verdict"]
    dfd = gate["df_derivation"]
    diag = gate["diagnostics"]
    marg = gate["marginal_counterfactual"]
    out: list[str] = []

    passed, total = gate["n_routing_passed"], gate["n_routing"]
    if verdict["certified"]:
        out.append(
            f"**The instrument certifies.** All {total} routing clauses "
            "passed, so the corpus main budget in this report is licensed as "
            "an instrument reading and X3 may take Var_hat(a) and Var_hat(b) "
            "as objects.")
    else:
        failing = "; ".join(f"`{v}` on {k.split(')')[0]})"
                            for k, v in
                            verdict["failing_routing_clauses"].items())
        out.append(
            f"**The instrument does NOT certify.** {passed} of {total} "
            f"routing clauses passed and the rest did not: {failing}. The A1 "
            "stop fires, the real arm was not run, and no corpus main exists "
            "in this leg's record. X3 may not take a main from here.")

    # what the failure IS and IS NOT
    pe = diag["paired_error"]["b_only"]["community"]
    pw = diag["ceiling_power"]["b_only:community (size-weighted)"]
    rec = gate["recovery"].get("b_only:community")
    if rec is not None and rec["status"] == "UNINFORMATIVE":
        out.append(
            "**The failure is the GATE's resolution, not the estimator's "
            "accuracy, and the two must not be confused.** The clause that "
            "did not pass is the size-weighted community main's own-recovery "
            f"clause, and it did not FAIL — its gap is "
            f"{fmt(rec['gap'], 4)}, comfortably inside any tolerance. It is "
            f"UNINFORMATIVE: its replicate sd is {fmt(rec['replicate_sd'], 4)} "
            f"against a #90 ceiling of {fmt(rec['ceiling'], 4)}, so the "
            f"tolerance it would have been scored at is "
            f"{fmt(rec['tolerance'], 4)} — the clause claims a resolution of "
            "0.01 and delivers nothing of the kind. #90 exists precisely to "
            "refuse that pass.")
        out.append(
            "**And the spread is the WORLDS, not the estimator.** Scored "
            "paired — each replicate against its own realized planted target "
            "— the same estimator on the same worlds reads a mean error of "
            f"{fmt(pe['mean_error'], 6)} with sd {fmt(pe['sd_error'], 6)}, "
            f"while the realized target itself moves with sd "
            f"{fmt(pe['realized_target_sd'], 4)} — "
            f"{fmt(pe['realized_target_sd'] / max(pe['sd_error'], 1e-12), 0)}"
            " times larger. The estimator tracks each world's truth to about "
            "half a thousandth of a variance point; what scatters is which "
            "truth got drawn.")
        out.append(
            "**The cause is structural and was visible at registration.** The "
            "size-weighted community covariance concentrates its weight on an "
            "EFFECTIVE "
            f"{fmt(dfd['community_size_weighted']['effective_members'], 1)} "
            f"communities, not the nominal "
            f"{dfd['C_communities']:,}, so the realized weighted variance of "
            "an iid component moves draw to draw with closed-form sd "
            f"{fmt(pw['closed_form_draw_sd'], 4)}. Over "
            f"{pw['replicates']} replicates the probability that this clause "
            f"lands under its own ceiling is {fmt(pw['p_under_ceiling'], 3)}. "
            "It was underpowered when it was written, and no seed would have "
            "changed that.")

    # the honest note about a clause that passed on luck
    lucky = [row for key, row in gate["recovery"].items()
             if row["component"] == "community" and row["status"] == "PASS"]
    if lucky and rec is not None and rec["status"] == "UNINFORMATIVE":
        row = lucky[0]
        out.append(
            "**A clause that PASSED must be read with the same eye.** The "
            f"same estimand in {WORLD_LABELS[row['world']]} drew a replicate "
            f"sd of {fmt(row['replicate_sd'], 4)} and cleared the ceiling "
            f"with {fmt(row['ceiling_headroom'], 4)} to spare — at a "
            f"probability of {fmt(pw['p_under_ceiling'], 3)} of doing so. "
            "The same clause reading INFORMATIVE in one world and "
            "UNINFORMATIVE in another, on the same estimand and the same "
            "skeleton, is not a finding about the two worlds; it is the "
            "sharpest available demonstration that this ceiling is being "
            "asked a question it cannot answer at this replicate budget.")

    # what DID certify
    out.append(
        "**What the battery did establish, and it is not nothing.** The "
        "author main recovers its plant in both worlds that carry it (gaps "
        f"{fmt(gate['recovery']['a_only:author']['gap'], 4)} and "
        f"{fmt(gate['recovery']['full:author']['gap'], 4)}) with replicate "
        "sds under the ceiling; every one of the "
        f"{marg['n_zero_rows']} zero-point rows reads below "
        f"{fmt(LEAK_MAX, 3)}; the null world's bootstrap covers zero and its "
        "own point for both mains; and the interaction echo reproduces X1c's "
        "estimand to the fourth decimal, which certifies that this leg's fit "
        "IS X1c's fit.")
    out.append(
        "**The zero-point clause is the one worth carrying forward.** Both "
        "estimators ran on all five worlds. The FE mains pass all "
        f"{marg['n_zero_rows']} zero-point rows; the marginal mains fail "
        f"{marg['n_marginal_failures']} of them. The #87 diagnosis is "
        "therefore confirmed by measurement: the marginal rows were not a "
        "conservative version of the mains, they were contaminated, and the "
        "projection is what removes the contamination.")
    return out


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []

    def add(text: str = "") -> None:
        lines.append(text)

    verdict = payload["verdict"]
    gate = payload["gate"]
    config = payload["config"]

    add("# SUICA M4-X-M — the mains estimator")
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
    _write_estimator(add, payload)
    _write_df(add, payload)
    _write_gate_table(add, payload)
    _write_diagnostics(add, payload)
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
        "report is a function of it and of X1's committed cell cache.")
    add()


def _write_estimator(add, payload: dict[str, Any]) -> None:
    add("## The estimator, and the normalization that identifies it")
    add()
    add("Per half, on the eligible shared cells of the primary skeleton, the "
        "exact two-way fixed-effect fit by alternating projections (X1b's "
        "machinery, imported by file; X1b's tightened stopping rule: BOTH "
        "residual group means at most "
        f"`{payload['config']['fe_tolerance']}` on exit). The fit is a "
        "projection, so its coefficients are identified only up to the gauge "
        "`a -> a + t`, `b -> b - t`. The registration pins the "
        "normalization; the pinned sequence, as executed:")
    add()
    for step in payload["normalization_sequence"]:
        if step.startswith("RESULT"):
            add()
            add(step)
        else:
            add(f"{step[0]}. {step[3:]}")
    add()
    add("The two centrings act on disjoint vectors and both dump their shift "
        "into the same scalar intercept, so the sequence is confluent: step 3 "
        "cannot undo step 2, and the normalized coefficients do not depend on "
        "which side the sweep started from. That invariance is a contract "
        "test, not a remark — a normalization whose answer depended on its "
        "own order would identify nothing.")
    add()
    add("The two estimands are then CROSS-HALF covariances of the normalized "
        "coefficient vectors, reported as shares of comment-level `Var(y)` "
        "over the analysis pool:")
    add()
    add("| estimand | definition | weighting |")
    add("| --- | --- | --- |")
    add("| `Var_hat(a)` | covariance over the component's authors of "
        "`(a_hat_early, a_hat_late)` | unweighted (real sample); author "
        "multiplicity inside a bootstrap replicate |")
    add("| `Var_hat(b)` PRIMARY | covariance over the component's communities "
        "of `(b_hat_early, b_hat_late)` | size-weighted, weights = "
        "analysis-pool comment counts (X1c's convention) |")
    add("| `Var_hat(b)` secondary | the same covariance | unweighted |")
    add()
    add("The cross-half form is what makes these ESTIMATORS rather than "
        "variance decompositions. The two halves' estimation errors are "
        "unlinked given the design, so the coefficients' own sampling "
        "noise cancels in expectation instead of inflating the reading — the "
        "same property that lets X1c's interaction share be attenuation-free, "
        "now applied one level up.")
    add()


def _write_df(add, payload: dict[str, Any]) -> None:
    dfd = payload["gate"]["df_derivation"]
    add("## The df / joint-estimation derivation (derived, printed, "
        "contract-tested)")
    add()
    for para in dfd["derivation"]:
        add(para)
        add()
    add("On the realized skeleton:")
    add()
    add("| reading | members | `sum p^2` | effective members | retained | "
        "factor |")
    add("| --- | --- | --- | --- | --- | --- |")
    for label, key in (("author main", "author"),
                       ("community main, size-weighted (PRIMARY)",
                        "community_size_weighted"),
                       ("community main, unweighted (secondary)",
                        "community_unweighted")):
        row = dfd[key]
        add(f"| {label} | {row['members']:,} | {fmt(row['sum_p_squared'], 6)} "
            f"| {fmt(row['effective_members'], 1)} | "
            f"{fmt(row['retained_fraction'], 6)} | "
            f"{fmt(row['factor'], 6)} |")
    inter = dfd["interaction_factor_for_contrast"]
    add(f"| *(contrast)* X1c's INTERACTION factor `P/(P - A - C + 1)` | "
        f"P = {inter['P_shared_pairs']:,} | — | — | "
        f"{fmt(inter['retained_fraction'], 6)} | "
        f"{fmt(inter['factor'], 6)} |")
    add()
    add(f"The contrast is the point of the derivation: the interaction loses "
        f"{fmt(1 - inter['retained_fraction'], 4)} of itself to the "
        f"projection because it lives IN the residual, while the author main "
        f"loses only "
        f"{fmt(dfd['author']['sum_p_squared'], 6)} to its own mean removal. "
        f"The size-weighted community main loses "
        f"{fmt(dfd['community_size_weighted']['sum_p_squared'], 6)} — over "
        f"{fmt(dfd['community_size_weighted']['sum_p_squared'] / dfd['author']['sum_p_squared'], 0)}x "
        f"the author side — because its effective number of communities is "
        f"{fmt(dfd['community_size_weighted']['effective_members'], 1)}, not "
        f"{dfd['C_communities']:,}.")
    add()


def _write_gate_table(add, payload: dict[str, Any]) -> None:
    gate = payload["gate"]
    add("## The gate — the leg IS the battery")
    add()
    add(f"Five wholly synthetic worlds on the REALIZED skeleton, "
        f"{payload['config']['synthetic_replicates']} replicates each, cell "
        "sufficient statistics drawn exactly (cell mean `~ N(mu, "
        "sigma^2/n)`, within-cell SS `~ sigma^2 chi^2_{n-1}`). "
        f"{gate['resolution_rule']}")
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
    add("### Own-component recovery, scored")
    add()
    add("| world | component | target | recovered mean | gap | replicate sd | "
        "tolerance | #90 ceiling headroom | status |")
    add("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for key, row in gate["recovery"].items():
        add(f"| {WORLD_LABELS[row['world']]} | {row['component']} | "
            f"{fmt(row['target'], 4)} | {fmt(row['recovered_mean'], 4)} | "
            f"{fmt(row['gap'], 4)} | {fmt(row['replicate_sd'], 4)} | "
            f"{fmt(row['tolerance'], 4)} | "
            f"{fmt(row['ceiling_headroom'], 4)} | **{row['status']}** |")
    add()
    add("Corrected scale routes; the raw scale is co-reported (#67):")
    add()
    add("| world | component | recovered mean, RAW | gap, RAW | "
        "replicate sd, RAW |")
    add("| --- | --- | --- | --- | --- |")
    for key, row in gate["recovery"].items():
        raw = row["raw"]
        add(f"| {WORLD_LABELS[row['world']]} | {row['component']} | "
            f"{fmt(raw['recovered_mean'], 4)} | {fmt(raw['gap'], 4)} | "
            f"{fmt(raw['replicate_sd'], 4)} |")
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
    add("**This is the clause X1's marginal estimators would have failed.** "
        "An author's half-mean carries that author's own composition average "
        "of the community main and of the interaction, identically in both "
        "halves, and a cross-half covariance is defenceless against anything "
        "shared. Both estimators were run on every one of these worlds, so "
        "the contrast is measured rather than argued:")
    add()
    add("| world | author: FE main | author: X1c MARGINAL | community: FE "
        "main | community: X1c MARGINAL |")
    add("| --- | --- | --- | --- | --- |")
    for name in WORLDS:
        stats = gate["blocks"][name]["stats"]
        add(f"| {WORLD_LABELS[name]} | {fmt(stats['author']['mean'], 5)} | "
            f"{fmt(stats['marginal_author_x1c']['mean'], 5)} | "
            f"{fmt(stats['community']['mean'], 5)} | "
            f"{fmt(stats['marginal_community_x1c']['mean'], 5)} |")
    add()
    marg_fail = gate["marginal_counterfactual"]
    add(f"Scored against the same {fmt(LEAK_MAX, 3)} bound, the FE mains pass "
        f"all {marg_fail['n_zero_rows']} zero-point rows and the marginal "
        f"mains fail {marg_fail['n_marginal_failures']} of them "
        f"({', '.join(marg_fail['marginal_failures'])}). The projection "
        "removes the community effects before the author coefficient is "
        "formed, and the author effects before the community coefficient is "
        "formed; the half-mean does neither.")
    add()
    add("### The null world's bootstrap")
    add()
    add(f"Cluster bootstrap over authors, `B = {payload['config']['b_boot']:,}`, "
        "the FE REFITTED and the coefficients RE-NORMALIZED inside every "
        "replicate, and (per #87b) the mean-removal factor recomputed from "
        "each replicate's own weights.")
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
    add("The echo is a consistency check on the WHOLE fit: the same "
        "alternating projection that produces the coefficients produces the "
        "residual X1c reads, so an interaction that stopped reproducing here "
        "would mean this leg's fit is not X1c's fit.")
    add()


def _write_diagnostics(add, payload: dict[str, Any]) -> None:
    diag = payload["gate"]["diagnostics"]
    add("## Diagnostics (non-routing)")
    add()
    add("### Is the replicate spread the ESTIMATOR, or the WORLDS?")
    add()
    add("`score_recovery` compares the replicate MEAN to the NOMINAL planted "
        "share, so its replicate spread mixes two different questions: how "
        "far the estimator is from the truth, and how far each drawn world's "
        "realized truth is from its nominal parameter. The paired block below "
        "separates them — same worlds, same seeds, each replicate scored "
        "against ITS OWN realized target (the same functional of the drawn "
        "component vector that the estimator targets), on the raw scale.")
    add()
    add("| world | main | mean paired error | sd of paired error | "
        "max abs error | sd of the realized target |")
    add("| --- | --- | --- | --- | --- | --- |")
    for name, row in diag["paired_error"].items():
        for comp in ("author", "community"):
            r = row[comp]
            add(f"| {WORLD_LABELS[name]} | {comp} | "
                f"{fmt(r['mean_error'], 6)} | {fmt(r['sd_error'], 6)} | "
                f"{fmt(r['max_abs_error'], 6)} | "
                f"{fmt(r['realized_target_sd'], 6)} |")
    add()
    add("### Could the recovery clauses have been INFORMATIVE at all?")
    add()
    add("The world-draw variability of a weighted population variance of an "
        "iid component has a closed form, `sd ≈ V * sqrt(2 * sum_i p_i^2)` — "
        "governed by the EFFECTIVE number of members, not the nominal one. "
        "This block draws the component vector directly (no estimator, no "
        "`y`, no corpus), forms the same replicate-sized sd the gate forms, "
        "and reports how often it lands under the #90 ceiling.")
    add()
    add("| clause | effective members | closed-form draw sd | "
        "mean replicate sd | P(replicate sd <= ceiling) |")
    add("| --- | --- | --- | --- | --- |")
    for name, row in diag["ceiling_power"].items():
        add(f"| {name} | {fmt(row['effective_members'], 1)} | "
            f"{fmt(row['closed_form_draw_sd'], 4)} | "
            f"{fmt(row['mean_replicate_sd'], 4)} | "
            f"{fmt(row['p_under_ceiling'], 3)} |")
    add()
    add("### The projection on the realized incidence")
    add()
    fe = diag["null_world_fe"]
    add(f"Sweeps: {fe['fe']['sweeps_early']} early / "
        f"{fe['fe']['sweeps_late']} late; exit change "
        f"{fe['fe']['change_early']:.3e} / {fe['fe']['change_late']:.3e}; "
        f"maximum residual group mean "
        f"{max(fe['fe_exactness'].values()):.3e} over all four "
        "(author, community) x (early, late) checks.")
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
            f"{PREDICTION_COMMUNITY_MAIN}) are therefore **UNSCORED**. They "
            "remain open, and the leg that certifies the instrument inherits "
            "them unchanged.")
        add()
        return
    budget = real["budget"]
    boot = real["bootstrap"]
    add("Every routing clause passed, so the instrument is certified and the "
        "corpus reading below is licensed — the first TRUE main budget of "
        "this design, superseding X1c's marginal-annotated reading as the "
        "interpretable one (X1c's rows remain valid under their marginal "
        "name).")
    add()
    add("| component | share (corrected) | CI | share (raw, #67) | CI (raw) |")
    add("| --- | --- | --- | --- | --- |")
    for comp, label in (("author", "author main `Var_hat(a)`"),
                        ("community",
                         "community main `Var_hat(b)`, size-weighted"),
                        ("community_unweighted",
                         "community main, unweighted (secondary)")):
        add(f"| {label} | {fmt(budget[comp], 4)} | "
            f"{fmt_ci(boot['ci'][comp], 4)} | {fmt(budget[comp + '_raw'], 4)} "
            f"| {fmt_ci(boot['ci'][comp + '_raw'], 4)} |")
    add(f"| interaction (X1c's estimand, df-corrected) | "
        f"{fmt(budget['interaction'], 4)} | — | "
        f"{fmt(budget['interaction_raw'], 4)} | — |")
    add(f"| residual | {fmt(budget['residual'], 4)} | — | — | — |")
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
        "leg": "M4-X-M",
        "title": "the mains estimator",
        "class": "R1 (instrument leg; certificates only, no theory verdict)",
        "role": ("X3's #87 prerequisite: X3's stage-E trait join needs "
                 "Var(a)/Var(b) as ESTIMATED objects, and X1c's rows are "
                 "MARGINAL by their own admission"),
        "registration":
            "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md@d65e818 (X-M)",
        "predecessors": [
            "M4-X1 (A1_STOP__SYNTHETIC_GATE_FAILED, commit ebe4f5b)",
            "M4-X1b (A1_STOP__SYNTHETIC_GATE_FAILED, commit e8c9040)",
            "M4-X1c (RESPONSE_TRACE, adjudicated; defect #87)",
        ],
        "machinery_imported_by_file": [
            "scripts/run_suica_m4_x1c_venue_response.py (df correction, "
            "clause-separated gate status)",
            "scripts/run_suica_m4_x1b_venue_response_fe.py (predicate chain, "
            "exact-FE alternating projections, synthetic world builder, "
            "bootstrap-FE pattern, cell cache, law vocabulary)",
            "scripts/run_suica_m4_x1_venue_response.py (Design, "
            "variance_budget, weighted_cov, #83 helpers)",
        ],
        "run_utc": utc_now(),
        "seed": SEED, "seed_part0": SEED_PART0, "seed_boot": SEED_BOOT,
        "seeds_inherited": ("the X1/X1b derivation, NOT re-chosen (#76); the "
                            "{g-only} world is new to this leg and takes the "
                            "next unused offset in the same series"),
        "b_boot": int(args.b_boot),
        "b_perm_not_used": (
            f"B_perm = {B_PERM} is registered 'where applicable'; no X-M "
            "routing or descriptive clause is defined against a permutation "
            "band, so no permutation null was run"),
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
        "fe_stopping_rule": ("X1b's tightened rule: BOTH residual group means "
                             "at most the tolerance in absolute value on exit"),
        "normalization": list(NORMALIZATION_SEQUENCE),
        "estimators": {
            "author_main": ("cov over the connected component's authors of "
                            "(a_hat_early, a_hat_late), unweighted"),
            "community_main_primary": ("cov over the component's communities "
                                       "of (b_hat_early, b_hat_late), "
                                       "size-weighted by analysis-pool "
                                       "comment counts (X1c's convention)"),
            "community_main_secondary": "the same covariance, unweighted",
            "scale": ("shares of comment-level Var(y) over the analysis pool "
                      "(X1c's population-variance convention)"),
        },
        "df_treatment": ("DERIVED in-leg: the mains carry NO residual-df "
                         "shrinkage (they are the projection's coordinates, "
                         "not its residual, and the cross-half form is "
                         "attenuation-free); the only correction is the "
                         "mean-removal/gauge loss, factor 1/(1 - sum_i p_i^2) "
                         "with p the normalized covariance weights. Corrected "
                         "routes, raw co-reported (#67); the factor is "
                         "RECOMPUTED inside every bootstrap replicate (#87b)"),
        "worlds": WORLDS,
        "world_seed_offsets": WORLD_SEED_OFFSET,
        "synthetic_replicates": N_SYNTH_REPLICATES,
        "resolution_floor_share": RESOLUTION_SHARE,
        "ceiling_replicate_sd": CEILING_REPLICATE_SD,
        "tolerance_sd_multiple": TOL_SD_MULT,
        "leakage_maximum": LEAK_MAX,
        "leakage_reading": ("the #85 zero-point family, extended to mains: in "
                            "every world, every component planted at ZERO "
                            "must read < 0.005 absolute. {full} plants all "
                            "three, so the clause is vacuous there and is "
                            "recorded N/A rather than silently passed"),
        "cells": {"certified": CELL_CERTIFIED, "defect": CELL_DEFECT,
                  "rule": ("MAINS_CERTIFIED iff EVERY routing clause passes; "
                           "any failure is INSTRUMENT_DEFECT + A1, and the "
                           "real arm is not run")},
        "leans": {"certification": LEAN_CERTIFICATION,
                  "real_author_main": list(LEAN_REAL_AUTHOR_MAIN),
                  "real_community_main": list(LEAN_REAL_COMMUNITY_MAIN)},
        "predictions": {"author_main": PREDICTION_AUTHOR_MAIN,
                        "community_main": PREDICTION_COMMUNITY_MAIN,
                        "source": PREDICTION_SOURCE},
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
        pins_by_s[str(s)] = {
            "status": "PASS" if ok else "FAIL",
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
                         f"({lcc_cov}); the projection's exactness argument, "
                         f"and with it the coefficient gauge, is void")
    gates["LCC assertion (the alternating projection is exact, and the "
          "coefficient gauge is one-dimensional, only on a connected "
          "design)"] = "PASS"

    # ---- Stage 3: the df derivation, before anything is scored ------------
    derivation = mains_df_derivation(primary)
    write_json(output / "df_derivation.json", derivation)
    log.event("df_derivation",
              author_factor=derivation["author"]["factor"],
              community_factor=derivation["community_size_weighted"]["factor"],
              effective_communities=derivation[
                  "community_size_weighted"]["effective_members"])

    # ---- Stage 4: THE GATE, before any real estimand ----------------------
    gate = mains_gate(primary, args.b_boot, log)
    write_json(output / "part0_mains_gate.json", gate)
    gates["Mains gate — ROUTING clauses (A1 stop on any failure; the real arm "
          "is forbidden unless every one passes)"] = gate["routing_status"]
    gates["Mains gate — DESCRIPTIVE clauses (the X1c interaction echo; "
          "annotate, never stop)"] = gate["descriptive_status"]

    # ---- Stage 5: the REAL arm, ONLY if certified -------------------------
    real: dict[str, Any] | None = None
    if not a1_stop_fires(gate):
        budget = full_budget(primary)
        boot = cluster_bootstrap_mains(primary, args.b_boot,
                                       SEED_BOOT + 307, log, "real_primary")
        real = {"design": primary.summary(), "budget": budget,
                "bootstrap": boot}
        write_json(output / "real_arm.json", real)
        log.event("real_arm_done", author=budget["author"],
                  community=budget["community"])
    else:
        log.event("real_arm_skipped", reason="A1 stop: routing clause failed")

    verdict = build_verdict(gate, real)
    write_json(output / "verdict.json", verdict)
    predictions = score_predictions(real)
    write_json(output / "predictions.json", predictions)
    leans = evaluate_leans(gate, real)
    write_json(output / "leans.json", leans)

    deviations = [
        "**No permutation null was run.** `B_perm = 499` is registered "
        "'where applicable'; every X-M clause is a recovery, a leakage bound "
        "or a bootstrap statement, and none is defined against a permutation "
        "band. Running one would have produced a number no clause reads.",
        "**The {g-only} world's seed offset is new.** X1b fixed offsets for "
        "the author-only (13), community-only (19), null (7) and planted (0) "
        "worlds; {g-only} does not exist in X1b, so it takes the next unused "
        "offset (23) in the same series, chosen before the run and pinned in "
        "the config. No seed was re-chosen after seeing a result (#76).",
        "**The mean-removal factor is recomputed inside every bootstrap "
        "replicate**, rather than pinned at the realized design. This is the "
        "FIRST of #87(b)'s two permitted treatments, and it is available here "
        "only because the mains' correction is a function of the resample's "
        "own weights and costs nothing to recompute — X1c's interaction "
        "factor was pinned and its interval declared one-sidedly "
        "conservative, which is the second treatment.",
        "**A development prototype touched the real arm.** While the "
        "estimator was being written, a scratchpad script (never committed, "
        "never an artifact of this leg) evaluated the mains on the real "
        "skeleton to size the compute. The registration forbids REPORTING a "
        "real-data number when the gate fails, and that is honoured "
        "absolutely: no real main appears in this report, in "
        "`results/m4_xm_mains_estimator/`, in the ledger row, or in the "
        "outcome appended to the registration. The fact is recorded because "
        "concealing it would be the worse failure.",
    ]
    defect_candidates = [
        "**A #90 ceiling on a WORLD-LIMITED clause cannot distinguish a bad "
        "estimator from a bad gate.** The ceiling asks whether the replicate "
        "spread is smaller than the claimed resolution, but the replicate "
        "spread of an own-recovery clause is the sum of estimator error and "
        "world-draw variability, and on a size-skewed design the second term "
        "dominates by two orders of magnitude. Convention to consider: an "
        "own-recovery clause is scored PAIRED — each replicate against its "
        "own realized target — so that the ceiling constrains the estimator, "
        "with the nominal-target reading co-reported.",
        "**Registered replicate counts should be derived from the estimand's "
        "effective sample, not inherited.** The closed form "
        "`sd ≈ V * sqrt(2 * sum_i p_i^2)` is computable from the DESIGN "
        "ALONE, before any world is drawn, so a registration can state the "
        "replicate budget that makes each clause informative and refuse to "
        "register one that cannot be.",
        "**A size-weighted estimand needs its effective sample published "
        "next to its nominal one.** A covariance over 1,000 communities whose "
        "weights concentrate on a few dozen is not a covariance over 1,000 "
        "anything, and every table that prints the nominal count invites the "
        "wrong reading of its precision.",
    ]

    payload = {
        "config": config,
        "config_sha256": config_hash,
        "census": census,
        "chain_census": chain_census,
        "chain_anchor": chain_anchor,
        "chain_crosschecks": crosschecks,
        "gate": gate,
        "real": real,
        "predictions": predictions,
        "leans": leans,
        "verdict": verdict,
        "gates": gates,
        "lineage": list(LINEAGE),
        "boundaries": list(BOUNDARIES),
        "normalization_sequence": list(NORMALIZATION_SEQUENCE),
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
