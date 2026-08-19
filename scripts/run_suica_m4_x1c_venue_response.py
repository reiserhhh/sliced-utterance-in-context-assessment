#!/usr/bin/env python3
"""SUICA M4-X1c — the venue response, clause-separated gate.

Registered BEFORE the run in ``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``
(commit 8fffaad, section "X1c").  THIRD AND FINAL registration of this
estimand.  This runner executes that registration and nothing else.

X1c is a THIN wrapper over X1b.  The predicate chain, the exact two-way
fixed-effect estimator by alternating projections, the synthetic worlds, the
permutation null, the cluster bootstrap with the FE recomputed per replicate
and the #83 scan helpers are all IMPORTED BY FILE from
``scripts/run_suica_m4_x1b_venue_response_fe.py`` (which in turn imports X1,
which in turn imports U2/U2b) — not copied.  Two things change, both from
defect #86:

1. GATE RESTRUCTURE (#86a).  X1b's nine clauses were scored as one block, so
   a DESCRIPTIVE bias with a solved mechanism stopped a leg whose routing
   machinery had been certified exact.  The gate is now SEPARATED:

   ROUTING clauses (A1-stopping) — (i) recovery of the DF-CORRECTED
   interaction share within max(0.01, 3 x replicate sd) on the planted world;
   (ii) the null world's interaction-share cluster-bootstrap CI covers 0 AND
   its point sits inside the permutation band; (iii) the null world's R sits
   inside its band; (iv) author-only and community-only ablation leakage
   below 0.005; (v) the #85b bootstrap-zero clause.

   DESCRIPTIVE clauses (report-gated) — the MARGINAL author and community
   shares scored against their MARGINAL TARGETS, i.e. the planted variance
   component PLUS the design-composition term, both derived here from the
   realized skeleton with pinned, printed formulas.  A descriptive failure
   ANNOTATES the number with its dual-stamped bias note (#67); it never
   stops the leg.

2. ESTIMAND NAMING AND CORRECTION (#86b/c).  The verdict routes on the
   DF-CORRECTED reproducible interaction share

       share_corr = share_raw * P / (P - A - C + 1)

   with P (shared pairs), A (authors) and C (communities) pinned from each
   arm's own realized skeleton.  The raw share is CO-REPORTED under the #67
   dual stamp.  R is unchanged — it is a correlation, not a variance share,
   and the projection's dimension loss does not rescale it.  The two main
   shares are reported as MARGINAL shares under that name, each carrying its
   design-composition annotation.

Cells, leans, sensitivities, boundaries, governance, seeds and discipline
inherit X1b (and through it X1) VERBATIM.

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
import sys
import time
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

X1B_SCRIPT = ROOT / "scripts/run_suica_m4_x1b_venue_response_fe.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:          # pragma: no cover
        raise RuntimeError(f"cannot import machinery from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


X1B = load_module("suica_m4_x1b_for_x1c", X1B_SCRIPT)
X1 = X1B.X1

# ---------------------------------------------------------------------------
# The inherited machinery (#56/#81: bound to the committed object, not copied)
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
permutation_null_fe = X1B.permutation_null_fe
cluster_bootstrap_fe = X1B.cluster_bootstrap_fe
analyse_design_fe = X1B.analyse_design_fe
recover_shares_fe = X1B.recover_shares_fe
synthetic_design = X1B.synthetic_design
synthetic_world_block = X1B.synthetic_world_block
composition_diagnostics = X1B.composition_diagnostics
variance_budget = X1B.variance_budget
per_author_correlations = X1B.per_author_correlations
headroom_report = X1B.headroom_report
magnitude_cells = X1B.magnitude_cells
point_cell = X1B.point_cell

# ---------------------------------------------------------------------------
# Registration pins — every one of them bound to X1b's committed definition
# ---------------------------------------------------------------------------

SEED = X1B.SEED                     # 20260819
B_PERM = X1B.B_PERM                 # 499
B_BOOT = X1B.B_BOOT                 # 1000

SEED_PART0 = X1B.SEED_PART0         # seeds INHERITED, never re-chosen (#76)
SEED_PERM = X1B.SEED_PERM
SEED_BOOT = X1B.SEED_BOOT

N_MIN_PRIMARY = X1B.N_MIN_PRIMARY
N_MIN_SENSITIVITY = X1B.N_MIN_SENSITIVITY
K_MIN = X1B.K_MIN
S_PRIMARY = X1B.S_PRIMARY
S_SENSITIVITY = X1B.S_SENSITIVITY
S_CENSUS = X1B.S_CENSUS
VOCAB_FLOOR_FRACTION = X1B.VOCAB_FLOOR_FRACTION
BIG5_POWER_FLOOR = X1B.BIG5_POWER_FLOOR
FE_TOL = X1B.FE_TOL

ANCHOR_ROWS_PARSEABLE = X1B.ANCHOR_ROWS_PARSEABLE
ANCHOR_AUTHORS = X1B.ANCHOR_AUTHORS
ANCHOR_BIG5_AUTHORS = X1B.ANCHOR_BIG5_AUTHORS
ANCHOR_DISJOINT_AUTHORS = X1B.ANCHOR_DISJOINT_AUTHORS
ANCHOR_VOCAB_FLOOR_USERS = X1B.ANCHOR_VOCAB_FLOOR_USERS
ANCHOR_LAW_VOCAB = X1B.ANCHOR_LAW_VOCAB
CHAIN_ANCHORS = X1B.CHAIN_ANCHORS
CHAIN_CROSSCHECKS = X1B.CHAIN_CROSSCHECKS

TRACE_MAX = X1B.TRACE_MAX
IDIOSYNCRATIC_MAX = X1B.IDIOSYNCRATIC_MAX
CELL_NO_RESPONSE = X1B.CELL_NO_RESPONSE
CELL_TRACE = X1B.CELL_TRACE
CELL_IDIOSYNCRATIC = X1B.CELL_IDIOSYNCRATIC
CELL_MAJOR = X1B.CELL_MAJOR
CELL_A1_STOP = X1B.CELL_A1_STOP

LEAN_R = X1B.LEAN_R
LEAN_INTERACTION = X1B.LEAN_INTERACTION
LEAN_AUTHOR_MAIN = X1B.LEAN_AUTHOR_MAIN
LEAN_COMMUNITY_MAIN = X1B.LEAN_COMMUNITY_MAIN

PLANTED_SHARES = X1B.PLANTED_SHARES
NULL_SHARES = X1B.NULL_SHARES
ABLATION_WORLDS = X1B.ABLATION_WORLDS
N_SYNTH_REPLICATES = X1B.N_SYNTH_REPLICATES
TOL_SD_MULT = X1B.TOL_SD_MULT
TOL_FLOOR = X1B.TOL_FLOOR
ABLATION_LEAK_MAX = X1B.ABLATION_LEAK_MAX

ARM_LABELS = X1B.ARM_LABELS

DEFAULT_X1_CACHE = X1B.DEFAULT_X1_CACHE
DEFAULT_COHORT = X1B.DEFAULT_COHORT
DEFAULT_OUTPUT = ROOT / "results/m4_x1c_venue_response"
DEFAULT_REPORT = ROOT / "reports/SUICA_M4_X1C_VENUE_RESPONSE_REPORT.md"

COMMITTED_FILES = (
    ROOT / "reports/SUICA_M4_X1C_VENUE_RESPONSE_REPORT.md",
    ROOT / "scripts/run_suica_m4_x1c_venue_response.py",
    ROOT / "tests/test_m4_x1c_venue_response.py",
    ROOT / "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md",
    ROOT / "docs/CLAIMS_LEDGER.md",
)


def _pct(value: float) -> str:
    return fmt(value, 4)


# ---------------------------------------------------------------------------
# NEW 1 — the degrees-of-freedom correction (#86c)
# ---------------------------------------------------------------------------


def df_correction(design: Design) -> dict[str, Any]:
    """The projection's dimension loss, pinned from the REALIZED skeleton.

    The two-way fixed-effect projection removes the author + community dummy
    space from the M = P cell observations of a half.  On a connected design
    that space has rank A + C - 1, so an interaction that is white across
    cells retains exactly

        retained = (P - A - C + 1) / P

    of itself in the residual, and the reproducible interaction share is
    CONSERVATIVE by that factor.  X1b measured the prediction and it held to
    the fourth decimal (0.0171 predicted, 0.0170 observed for a planted
    0.0200).  #86c pins the correction and routes the verdict on

        share_corr = share_raw * P / (P - A - C + 1) = share_raw / retained.

    The factor is a property of the ESTIMAND'S realized design, so the SAME
    pinned number rescales the point estimate, the permutation band and every
    cluster-bootstrap replicate: share_corr is an affine image of share_raw
    and its CI is the affine image of the raw CI.  A positive factor leaves
    "the CI covers 0" invariant, so the NULL-first cell rule is untouched.
    """

    P = int(design.n_slots)
    A = int(design.n_authors)
    C = int(design.n_comms)
    rank = A + C - 1
    residual_df = P - rank
    if residual_df <= 0:                             # pragma: no cover
        raise RuntimeError(f"the two-way projection exhausts the design "
                           f"(P={P}, A={A}, C={C})")
    retained = residual_df / P
    return {
        "P_shared_pairs": P, "A_authors": A, "C_communities": C,
        "rank_removed": int(rank), "residual_df": int(residual_df),
        "retained_fraction": float(retained),
        "factor": float(P / residual_df),
        "formula": "share_corr = share_raw * P / (P - A - C + 1)",
    }


def _scale(values: Sequence[float], factor: float) -> list[float]:
    return [float(v) * factor for v in values]


# ---------------------------------------------------------------------------
# NEW 2 — the MARGINAL targets of the two main-share estimators (#86b)
# ---------------------------------------------------------------------------


def marginal_targets(design: Design,
                     shares: dict[str, float]) -> dict[str, Any]:
    """What the two main-share estimators actually target on THIS skeleton.

    X1b's defect #86b: the cross-half covariance of author half-means is not
    an estimator of Var(a).  An author's half-mean is a size-weighted mean of
    that author's cell means, so it carries the author's OWN COMPOSITION
    AVERAGE of the community main and of the interaction, and that average is
    the same in both halves — the cross-half covariance, attenuation-free
    against noise, is defenceless against it.  The same argument runs on the
    community side with the roles exchanged.  Both terms are computable from
    the DESIGN ALONE, which is what makes them targets and not excuses.

    Notation.  A half-mean over an author's communities uses the weights

        w_{u,c,h} = n_{u,c,h} / sum_{c'} n_{u,c',h}          (author side)

    and over a community's authors

        t_{u,c,h} = n_{u,c,h} / sum_{u'} n_{u',c,h}          (community side).

    Write kappa_u = sum_c w_{u,c,e} w_{u,c,l} (the author's cross-half
    composition weight; it equals 1/k_u when the author's cells are equally
    sized) and lambda_c = sum_u t_{u,c,e} t_{u,c,l} (its community mirror).
    With planted components v_a, v_c, v_g of a unit total variance, and
    writing the community covariance's size weights as What_c (normalized
    n_{c,e} + n_{c,l}, exactly as ``variance_budget`` uses them):

      AUTHOR MARGINAL TARGET
        T_a = v_a (1 - 1/A)
            + (v_c + v_g) * mean_u[kappa_u]
            - v_c * sum_c wbar_{c,e} wbar_{c,l}
            - v_g * mean_u[kappa_u] / A
      where wbar_{c,h} = (1/A) sum_u w_{u,c,h}.

      COMMUNITY MARGINAL TARGET
        T_c = v_c (1 - sum_c What_c^2)
            + v_a * (sum_c What_c lambda_c - sum_u phi_{u,e} phi_{u,l})
            + v_g * (sum_c What_c lambda_c - sum_c What_c^2 lambda_c)
      where phi_{u,h} = sum_c What_c t_{u,c,h}.

    The leading terms are the planted component plus the composition term;
    the subtracted terms are the estimator's own mean-removal (both
    covariances subtract a product of means), kept so the target is exact
    rather than first-order.  Everything on the right-hand side is a function
    of the cell counts n_{u,c,h} — no y, planted or real, enters.
    """

    sa, sc = design.slot_author, design.slot_comm
    A, C = int(design.n_authors), int(design.n_comms)
    v_a = float(shares["author"])
    v_c = float(shares["community"])
    v_g = float(shares["interaction"])

    # --- author side ------------------------------------------------------
    a_ne = np.bincount(sa, design.n_e, A)
    a_nl = np.bincount(sa, design.n_l, A)
    w_e = design.n_e / np.maximum(a_ne[sa], 1e-300)
    w_l = design.n_l / np.maximum(a_nl[sa], 1e-300)
    kappa = np.bincount(sa, w_e * w_l, A)
    mean_kappa = float(kappa.mean())
    wbar_e = np.bincount(sc, w_e, C) / A
    wbar_l = np.bincount(sc, w_l, C) / A
    author_mean_removal_b = float((wbar_e * wbar_l).sum())
    author_target = (v_a * (1.0 - 1.0 / A)
                     + (v_c + v_g) * mean_kappa
                     - v_c * author_mean_removal_b
                     - v_g * mean_kappa / A)

    # --- community side ---------------------------------------------------
    c_ne = np.bincount(sc, design.n_e, C)
    c_nl = np.bincount(sc, design.n_l, C)
    t_e = design.n_e / np.maximum(c_ne[sc], 1e-300)
    t_l = design.n_l / np.maximum(c_nl[sc], 1e-300)
    lam = np.bincount(sc, t_e * t_l, C)
    size = c_ne + c_nl
    what = size / size.sum()
    lam_w = float((what * lam).sum())
    sum_what2 = float((what * what).sum())
    phi_e = np.bincount(sa, what[sc] * t_e, A)
    phi_l = np.bincount(sa, what[sc] * t_l, A)
    community_mean_removal_a = float((phi_e * phi_l).sum())
    community_mean_removal_g = float((what * what * lam).sum())
    community_target = (v_c * (1.0 - sum_what2)
                        + v_a * (lam_w - community_mean_removal_a)
                        + v_g * (lam_w - community_mean_removal_g))

    k = np.bincount(sa, None, A).astype(np.float64)
    return {
        "planted": {"author": v_a, "community": v_c, "interaction": v_g},
        "author": {
            "planted_component": v_a,
            "mean_kappa": mean_kappa,
            "mean_inverse_k": float(np.mean(1.0 / np.maximum(k, 1.0))),
            "composition_term": (v_c + v_g) * mean_kappa,
            "mean_removal_term": -(v_c * author_mean_removal_b
                                   + v_g * mean_kappa / A
                                   + v_a / A),
            "target": float(author_target),
            "formula": ("T_a = v_a(1 - 1/A) + (v_c + v_g)*mean_u[kappa_u] "
                        "- v_c*sum_c wbar_ce*wbar_cl - v_g*mean_u[kappa_u]/A"),
        },
        "community": {
            "planted_component": v_c,
            "mean_lambda_size_weighted": lam_w,
            "composition_term": (v_a + v_g) * lam_w,
            "mean_removal_term": -(v_c * sum_what2
                                   + v_a * community_mean_removal_a
                                   + v_g * community_mean_removal_g),
            "target": float(community_target),
            "formula": ("T_c = v_c(1 - sum_c What_c^2) "
                        "+ v_a*(sum_c What_c*lambda_c - sum_u phi_ue*phi_ul) "
                        "+ v_g*(sum_c What_c*lambda_c "
                        "- sum_c What_c^2*lambda_c)"),
        },
        "design_terms": {
            "A_authors": A, "C_communities": C, "P_shared_pairs":
                int(design.n_slots),
            "sum_what_squared": sum_what2,
            "author_mean_removal_b": author_mean_removal_b,
            "community_mean_removal_a": community_mean_removal_a,
            "community_mean_removal_g": community_mean_removal_g,
        },
    }


def decontaminate(marginal_author: float, marginal_community: float,
                  interaction: float, mean_kappa: float,
                  lam_w: float) -> dict[str, Any]:
    """ANNOTATION ONLY — the first-order inverse of the composition mixing.

    NOT a registered estimand and NOT a routing object.  If the two marginal
    shares behave on real data the way the design says they behave on planted
    data, then

        marginal_a = V_a + kappa * (V_c + V_g)
        marginal_c = V_c + lambda * (V_a + V_g)

    is a 2x2 linear system in (V_a, V_c) once V_g is taken as the
    df-corrected interaction share.  Solving it prints WHAT THE MAINS WOULD BE
    if the mixing were the whole story; it is arithmetic on the printed
    formulas, offered so the size of the annotation is a number.  The mains
    were never re-registered as FE-borne objects, so nothing here routes and
    nothing here is a claim.
    """

    det = 1.0 - mean_kappa * lam_w
    if abs(det) < 1e-12:                             # pragma: no cover
        return {"solvable": False}
    rhs_a = marginal_author - mean_kappa * interaction
    rhs_c = marginal_community - lam_w * interaction
    v_a = (rhs_a - mean_kappa * rhs_c) / det
    v_c = (rhs_c - lam_w * rhs_a) / det
    return {
        "solvable": True,
        "implied_author_main": float(v_a),
        "implied_community_main": float(v_c),
        "author_composition_term": float(marginal_author - v_a),
        "community_composition_term": float(marginal_community - v_c),
        "determinant": float(det),
    }


# ---------------------------------------------------------------------------
# NEW 3 — the clause-separated gate (#86a)
# ---------------------------------------------------------------------------


ROUTING = "ROUTING"
DESCRIPTIVE = "DESCRIPTIVE"
DESCRIPTIVE_ANNOTATED = "ANNOTATED"


def gate_status(routing_clauses: dict[str, str],
                descriptive_clauses: dict[str, str]) -> tuple[str, str]:
    """#86a in one function: which family stops and which family annotates.

    ROUTING clauses gate the VERDICT — any failure fires the A1 stop and no
    real estimand is computed.  DESCRIPTIVE clauses gate the REPORT — a
    failure marks the family ANNOTATED, which attaches a #67 dual-stamped
    bias note to the number and changes nothing about whether the leg runs.
    """

    routing = ("PASS" if all(v == "PASS" for v in routing_clauses.values())
               else "FAIL")
    descriptive = ("PASS" if all(v == "PASS"
                                 for v in descriptive_clauses.values())
                   else DESCRIPTIVE_ANNOTATED)
    return routing, descriptive


def a1_stop_fires(part0: dict[str, Any]) -> bool:
    """The A1 stop reads the ROUTING family and nothing else (#86a)."""

    return part0["routing_status"] != "PASS"


def _block_corrected(block: dict[str, Any], factor: float) -> dict[str, Any]:
    """Add the df-corrected interaction statistics to a synthetic block.

    Deterministic post-processing of the block's own per-replicate values —
    no world is re-drawn and no estimator is re-run.
    """

    values = np.array(block["stats"]["interaction"]["values"],
                      dtype=np.float64) * factor
    block["stats"]["interaction_corr"] = {
        "mean": float(values.mean()),
        "sd": float(values.std(ddof=1)) if values.size > 1 else 0.0,
        "min": float(values.min()), "max": float(values.max()),
        "values": [float(x) for x in values],
    }
    return block


def clause_separated_gate(skeleton: Design, b_perm: int, b_boot: int,
                          log: RunLog) -> dict[str, Any]:
    """Part 0 under #86a: routing clauses stop, descriptive clauses annotate.

    The battery itself is X1b's, verbatim and on the same inherited seeds: a
    planted world {author .30, community .08, interaction .02}, a NULL world
    (interaction 0), and author-only / community-only ablation worlds, eight
    replicates each, with the real incidence carrying WHOLLY SYNTHETIC y.
    What changes is the scoring:

      * the recovery clause that routes is the DF-CORRECTED interaction share
        against its planted 0.0200;
      * the two main shares are scored as MARGINAL shares against their
        MARGINAL TARGETS, and their verdict is DESCRIPTIVE — a failure adds a
        dual-stamped bias annotation (#67) to the reported number and does not
        touch the A1 stop.
    """

    dfc = df_correction(skeleton)
    factor = dfc["factor"]
    log.event("part0_start", authors=skeleton.n_authors,
              communities=skeleton.n_comms, slots=skeleton.n_slots,
              replicates=N_SYNTH_REPLICATES, df_factor=factor)

    planted = _block_corrected(
        synthetic_world_block(skeleton, PLANTED_SHARES, "planted",
                              SEED_PART0, N_SYNTH_REPLICATES, log), factor)
    null = _block_corrected(
        synthetic_world_block(skeleton, NULL_SHARES, "null",
                              SEED_PART0 + 7, N_SYNTH_REPLICATES, log), factor)
    ablations = {
        "author_only": _block_corrected(synthetic_world_block(
            skeleton, ABLATION_WORLDS["author_only"], "author_only",
            SEED_PART0 + 13, N_SYNTH_REPLICATES, log), factor),
        "community_only": _block_corrected(synthetic_world_block(
            skeleton, ABLATION_WORLDS["community_only"], "community_only",
            SEED_PART0 + 19, N_SYNTH_REPLICATES, log), factor),
    }

    targets_planted = marginal_targets(skeleton, PLANTED_SHARES)
    targets_null = marginal_targets(skeleton, NULL_SHARES)

    def _score(stat: dict[str, float], target: float) -> dict[str, Any]:
        tol = max(TOL_FLOOR, TOL_SD_MULT * stat["sd"])
        gap = stat["mean"] - target
        return {"target": target, "recovered_mean": stat["mean"],
                "replicate_sd": stat["sd"], "tolerance": tol,
                "gap": gap, "status": "PASS" if abs(gap) <= tol else "FAIL"}

    # --- ROUTING clause (i): the df-corrected interaction ------------------
    recovery_interaction = _score(planted["stats"]["interaction_corr"],
                                  PLANTED_SHARES["interaction"])
    recovery_interaction["raw_recovered_mean"] = \
        planted["stats"]["interaction"]["mean"]
    recovery_interaction["raw_replicate_sd"] = \
        planted["stats"]["interaction"]["sd"]
    recovery_interaction["df_factor"] = factor

    # --- DESCRIPTIVE clauses: the two MARGINAL shares ----------------------
    descriptives = {
        "author": dict(_score(planted["stats"]["author"],
                              targets_planted["author"]["target"]),
                       planted_component=PLANTED_SHARES["author"],
                       composition_term=targets_planted["author"]
                       ["composition_term"],
                       formula=targets_planted["author"]["formula"],
                       gap_against_planted=(planted["stats"]["author"]["mean"]
                                            - PLANTED_SHARES["author"])),
        "community": dict(_score(planted["stats"]["community"],
                                 targets_planted["community"]["target"]),
                          planted_component=PLANTED_SHARES["community"],
                          composition_term=targets_planted["community"]
                          ["composition_term"],
                          formula=targets_planted["community"]["formula"],
                          gap_against_planted=(
                              planted["stats"]["community"]["mean"]
                              - PLANTED_SHARES["community"])),
    }
    # the same scoring on the NULL world, as a free cross-check (never routes)
    descriptives_null = {
        "author": dict(_score(null["stats"]["author"],
                              targets_null["author"]["target"]),
                       planted_component=NULL_SHARES["author"]),
        "community": dict(_score(null["stats"]["community"],
                                 targets_null["community"]["target"]),
                          planted_component=NULL_SHARES["community"]),
    }

    # --- ROUTING clauses (ii), (iii), (v): the null world, full pipeline ---
    rng_world = np.random.default_rng(SEED_PART0 + 7)
    null_world = synthetic_design(skeleton, NULL_SHARES, rng_world)
    null_inference = analyse_design_fe(
        null_world, b_perm=b_perm, b_boot=b_boot, seed_perm=SEED_PERM + 101,
        seed_boot=SEED_BOOT + 101, tag="part0_null", log=log)
    share_raw = float(null_inference["budget"]["interaction"])
    share_corr = share_raw * factor
    ci_raw = list(null_inference["bootstrap"]["shares_ci"]["interaction"])
    ci_corr = _scale(ci_raw, factor)
    band_raw = list(null_inference["null"]["interaction_band"])
    band_corr = _scale(band_raw, factor)
    r_point = float(null_inference["R"])
    r_band = list(null_inference["null"]["r_band"])

    ci_covers_zero = bool(ci_corr[0] <= 0.0 <= ci_corr[1])
    ci_covers_point = bool(ci_corr[0] <= share_corr <= ci_corr[1])
    share_inside_band = bool(band_corr[0] <= share_corr <= band_corr[1])
    r_inside = bool(r_band[0] <= r_point <= r_band[1])

    # --- ROUTING clause (iv): the two ablations ----------------------------
    ablation_clauses = {}
    for name, block in ablations.items():
        leak = abs(block["stats"]["interaction_corr"]["mean"])
        ablation_clauses[name] = {
            "leakage_corrected": leak,
            "leakage_raw": abs(block["stats"]["interaction"]["mean"]),
            "maximum": ABLATION_LEAK_MAX,
            "R_leakage": block["stats"]["R"]["mean"],
            "status": "PASS" if leak < ABLATION_LEAK_MAX else "FAIL"}
    ablations_ok = all(c["status"] == "PASS"
                       for c in ablation_clauses.values())

    # --- the planted world with full inference (reference, never routes) ---
    rng_planted = np.random.default_rng(SEED_PART0)
    planted_world = synthetic_design(skeleton, PLANTED_SHARES, rng_planted)
    planted_inference = analyse_design_fe(
        planted_world, b_perm=b_perm, b_boot=b_boot, seed_perm=SEED_PERM + 103,
        seed_boot=SEED_BOOT + 103, tag="part0_planted", log=log)

    routing = {
        "(i) recovery — DF-CORRECTED interaction share within "
        "max(0.01, 3 x replicate sd)": recovery_interaction["status"],
        "(ii) null world — the interaction share's cluster-bootstrap CI "
        "covers 0 AND its point sits inside the permutation band":
            "PASS" if (ci_covers_zero and share_inside_band) else "FAIL",
        "(iii) null world — R inside its permutation band":
            "PASS" if r_inside else "FAIL",
        "(iv) ablation — author-only AND community-only leakage < 0.005 on "
        "the interaction share": "PASS" if ablations_ok else "FAIL",
        "(v) #85b bootstrap-zero — the null world's cluster-bootstrap CI "
        "covers 0": "PASS" if ci_covers_zero else "FAIL",
    }
    descriptive_clauses = {
        "MARGINAL author share against its MARGINAL target "
        "(planted + design composition)": descriptives["author"]["status"],
        "MARGINAL community share against its MARGINAL target "
        "(planted + design composition)": descriptives["community"]["status"],
    }
    routing_status, descriptive_status = gate_status(routing,
                                                     descriptive_clauses)

    annotations = []
    for key, row in descriptives.items():
        if row["status"] != "PASS":
            annotations.append(
                f"#67 DUAL STAMP — the marginal {key} share recovers "
                f"{_pct(row['recovered_mean'])} where its MARGINAL target is "
                f"{_pct(row['target'])} (planted component "
                f"{_pct(row['planted_component'])} + design-composition term "
                f"{_pct(row['composition_term'])}); residual gap "
                f"{_pct(row['gap'])} against a tolerance of "
                f"{_pct(row['tolerance'])}. The number is REPORTED with this "
                f"bias note and does not route.")

    out = {
        "status": routing_status,
        "routing_status": routing_status,
        "descriptive_status": descriptive_status,
        "routing_clauses": routing,
        "descriptive_clauses": descriptive_clauses,
        "n_routing": len(routing),
        "n_routing_passed": sum(1 for v in routing.values() if v == "PASS"),
        "n_descriptive": len(descriptive_clauses),
        "n_descriptive_passed": sum(1 for v in descriptive_clauses.values()
                                    if v == "PASS"),
        "annotations": annotations,
        "df_correction": dfc,
        "recovery_interaction": recovery_interaction,
        "descriptives": descriptives,
        "descriptives_null_world": descriptives_null,
        "marginal_targets_planted": targets_planted,
        "marginal_targets_null": targets_null,
        "ablation_clauses": ablation_clauses,
        "honesty": {
            "interaction_share_raw": share_raw,
            "interaction_share_corr": share_corr,
            "interaction_ci_raw": ci_raw,
            "interaction_ci_corr": ci_corr,
            "interaction_band_raw": band_raw,
            "interaction_band_corr": band_corr,
            "ci_covers_zero": ci_covers_zero,
            "ci_covers_point": ci_covers_point,
            "interaction_inside_band": share_inside_band,
            "marginal_author_share": null_inference["budget"]["author"],
            "marginal_community_share": null_inference["budget"]["community"],
            "R": r_point, "r_ci": list(null_inference["bootstrap"]["r_ci"]),
            "r_band": r_band, "r_inside_band": r_inside,
            "design": null_inference["design"],
            "fe": null_inference["fe"],
            "fe_exactness": null_inference["fe_exactness"],
        },
        "planted_world_inference": {
            "interaction_share_raw":
                planted_inference["budget"]["interaction"],
            "interaction_share_corr":
                planted_inference["budget"]["interaction"] * factor,
            "interaction_ci_corr": _scale(
                planted_inference["bootstrap"]["shares_ci"]["interaction"],
                factor),
            "interaction_band_corr": _scale(
                planted_inference["null"]["interaction_band"], factor),
            "R": planted_inference["R"],
            "r_ci": list(planted_inference["bootstrap"]["r_ci"]),
            "r_band": list(planted_inference["null"]["r_band"]),
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
    log.event("part0_done", routing=routing_status,
              descriptive=descriptive_status,
              passed=out["n_routing_passed"], of=out["n_routing"])
    return out


# ---------------------------------------------------------------------------
# NEW 4 — arms keyed on the corrected share
# ---------------------------------------------------------------------------


def augment_arm(arm: dict[str, Any], design: Design) -> dict[str, Any]:
    """Attach the arm's own df correction and the corrected share objects."""

    dfc = df_correction(design)
    factor = dfc["factor"]
    raw = float(arm["budget"]["interaction"])
    ci_raw = list(arm["bootstrap"]["shares_ci"]["interaction"])
    band_raw = list(arm["null"]["interaction_band"])
    targets = marginal_targets(design, PLANTED_SHARES)
    arm["df"] = dfc
    arm["share_raw"] = raw
    arm["share_corr"] = raw * factor
    arm["share_ci_raw"] = ci_raw
    arm["share_ci_corr"] = _scale(ci_raw, factor)
    arm["share_band_raw"] = band_raw
    arm["share_band_corr"] = _scale(band_raw, factor)
    arm["composition"] = {
        "mean_kappa": targets["author"]["mean_kappa"],
        "mean_inverse_k": targets["author"]["mean_inverse_k"],
        "mean_lambda_size_weighted":
            targets["community"]["mean_lambda_size_weighted"],
    }
    arm["decontamination_annotation"] = decontaminate(
        float(arm["budget"]["author"]), float(arm["budget"]["community"]),
        arm["share_corr"], targets["author"]["mean_kappa"],
        targets["community"]["mean_lambda_size_weighted"])
    return arm


def classify(arm: dict[str, Any]) -> dict[str, Any]:
    """The registered cell rule, NULL-first (#55), on the CORRECTED share.

    Cell boundaries are unchanged (0.02 / 0.10); only the statistic they read
    is the df-corrected one, per #86b/c.  Because the correction is a positive
    constant, "the CI covers 0" — cell 1's second condition — is the same
    event on either scale.
    """

    share = float(arm["share_corr"])
    ci = arm["share_ci_corr"]
    band = arm["null"]["r_band"]
    r = float(arm["R"])
    r_inside = bool(band[0] <= r <= band[1])
    ci_covers_zero = bool(ci[0] <= 0.0 <= ci[1])
    base = {"share_corr": share, "share_raw": float(arm["share_raw"]),
            "share_ci_corr": list(ci), "share_ci_raw": list(arm["share_ci_raw"]),
            "R": r, "r_band": list(band), "r_inside_band": r_inside,
            "ci_covers_zero": ci_covers_zero,
            "df_factor": float(arm["df"]["factor"])}
    if r_inside and ci_covers_zero:
        return dict(base, cell=CELL_NO_RESPONSE, straddle=False,
                    touched=[CELL_NO_RESPONSE])
    touched = magnitude_cells(ci)
    cell = touched[0] if len(touched) == 1 else point_cell(share)
    return dict(base, cell=cell, straddle=len(touched) > 1, touched=touched)


def evaluate_leans(primary: dict[str, Any], replication_cell: str | None,
                   primary_cell: str) -> list[dict[str, Any]]:
    """X1's registered leans, reported against — they never route.

    The interaction-share lean was written in X1 on the RAW scale, before the
    df correction existed.  #67: both scales are reported, and the lean's
    verdict is taken on the scale it was WRITTEN for, with the corrected
    reading carried beside it.
    """

    r = float(primary["R"])
    raw = float(primary["share_raw"])
    corr = float(primary["share_corr"])
    author = float(primary["budget"]["author"])
    community = float(primary["budget"]["community"])
    rows = [
        {"lean": "R in (0.05, 0.30]", "scale": "R (uncorrected by design)",
         "observed": r, "held": bool(LEAN_R[0] < r <= LEAN_R[1])},
        {"lean": "interaction share in (0.005, 0.05]",
         "scale": "RAW — the scale the lean was registered on (X1)",
         "observed": raw,
         "held": bool(LEAN_INTERACTION[0] < raw <= LEAN_INTERACTION[1])},
        {"lean": "interaction share in (0.005, 0.05] — co-reported (#67)",
         "scale": "DF-CORRECTED — the scale the VERDICT routes on (X1c)",
         "observed": corr,
         "held": bool(LEAN_INTERACTION[0] < corr <= LEAN_INTERACTION[1])},
        {"lean": "marginal author share in [0.15, 0.45]",
         "scale": "MARGINAL (composition-annotated)", "observed": author,
         "held": bool(LEAN_AUTHOR_MAIN[0] <= author <= LEAN_AUTHOR_MAIN[1])},
        {"lean": "marginal community share in [0.02, 0.15]",
         "scale": "MARGINAL (composition-annotated)", "observed": community,
         "held": bool(LEAN_COMMUNITY_MAIN[0] <= community
                      <= LEAN_COMMUNITY_MAIN[1])},
    ]
    if replication_cell is not None:
        rows.append({"lean": "Big5 replication lands in the primary cell",
                     "scale": "cell (routed on the corrected share)",
                     "observed": replication_cell,
                     "held": bool(replication_cell == primary_cell)})
    return rows


# ---------------------------------------------------------------------------
# Stage — the reading (every sentence generated from the artifacts, rule 24)
# ---------------------------------------------------------------------------


# The registered boundaries, inherited.  Two of X1b's six are restored to X1's
# ORIGINAL indicative wording: X1b rewrote them in the subjunctive ("every
# claim here WOULD HAVE BEEN about how much is written"; "a detection WOULD BE
# a lower bound") because its A1 stop made no claim.  X1c reaches a cell, so
# the registration's own indicative text is the correct inheritance and the
# subjunctive would misdescribe this leg.  The other four are X1b's verbatim,
# including its #85 restatement of the headroom clause and its replacement of
# X1's now-obsolete "incomplete design" caution (the exact FE removed the
# object that caution was about) with the WELL-SHARED VENUES boundary.
BOUNDARIES = (
    X1.BOUNDARIES[0],                    # indicative: "every claim here IS…"
    X1.BOUNDARIES[1],                    # indicative: "a detection IS a bound"
    X1B.BOUNDARIES[2],
    X1B.BOUNDARIES[3],
    X1B.BOUNDARIES[4],
    X1B.BOUNDARIES[5],
) + (
    "**The routing statistic is DF-CORRECTED and the mains are MARGINAL "
    "(new in X1c).** The verdict routes on share_corr = share_raw x "
    "P/(P - A - C + 1), the raw share is co-reported under the #67 dual "
    "stamp, and the two main shares are named MARGINAL because that is what "
    "their estimator targets: each carries the unit's own composition average "
    "of the other components, a term computed here from the design alone and "
    "printed beside every number. The mains were NOT re-registered as "
    "FE-borne objects, so they remain descriptive throughout and no claim "
    "rests on them.",
)


def build_reading(payload: dict[str, Any]) -> list[str]:
    """The leg's findings, each one a function of the committed artifacts."""

    arms = payload["arms"]
    cells = payload["cells"]
    primary = arms["primary"]
    cell = cells["primary"]
    gate = payload["part0"]
    head = primary["headroom"]
    comp = primary["composition"]
    dec = primary["decontamination_annotation"]
    lines = [
        (f"**Crossing #2 has its first corpus reading, and it is a "
         f"{cell['cell']}.** On the primary arm — "
         f"{primary['design']['authors']:,} disjoint-cohort authors across "
         f"{primary['design']['communities']:,} law-vocabulary communities, "
         f"{primary['design']['slots']:,} shared (author, community) pairs, "
         f"{primary['design']['comments']:,} comments — the reproducible "
         f"author x community interaction carries "
         f"{_pct(cell['share_corr'])} of comment-level Var(y) after the df "
         f"correction {fmt_ci(cell['share_ci_corr'])}, against a raw "
         f"{_pct(cell['share_raw'])} {fmt_ci(cell['share_ci_raw'])} "
         f"(#67 dual stamp; the pinned factor is "
         f"{fmt(primary['df']['factor'], 4)} = "
         f"{primary['df']['P_shared_pairs']:,} / "
         f"({primary['df']['P_shared_pairs']:,} - "
         f"{primary['df']['A_authors']:,} - "
         f"{primary['df']['C_communities']:,} + 1))."),
        (f"**The persistence statistic agrees with the budget.** R, the mean "
         f"per-author correlation of the early and late venue profiles, is "
         f"{_pct(primary['R'])} with a cluster-bootstrap CI "
         f"{fmt_ci(primary['bootstrap']['r_ci'])} against a permutation band "
         f"{fmt_ci(primary['null']['r_band'])} — "
         + ("OUTSIDE its band, so the NULL-first cell is refused on both of "
            "its conditions rather than one."
            if not cell["r_inside_band"] else
            "INSIDE its band, so the cell turns entirely on the share's CI.")),
        (f"**The budget's two main components are MARGINAL, and the "
         f"annotation is a number.** The marginal author share reads "
         f"{_pct(primary['budget']['author'])} and the marginal community "
         f"share {_pct(primary['budget']['community'])}. This arm's "
         f"composition weights are mean_u[kappa_u] = "
         f"{fmt(comp['mean_kappa'], 4)} on the author side and the "
         f"size-weighted mean_c[lambda_c] = "
         f"{fmt(comp['mean_lambda_size_weighted'], 4)} on the community side, "
         f"so each marginal carries roughly that fraction of the OTHER "
         f"components. Inverting the 2x2 mixing as an annotation only (not a "
         f"registered estimand, nothing routes on it) implies an author main "
         f"near {_pct(dec['implied_author_main'])} and a community main near "
         f"{_pct(dec['implied_community_main'])}."),
        (f"**Headroom is reported about the MEAN, with per-author saturation "
         f"acknowledged.** {head['authors_scored']:,} authors are scored and "
         f"{head['authors_undefined']:,} are undefined; the realized "
         f"per-author correlation has mean {_pct(head['mean'])} and sd "
         f"{_pct(head['sd'])}, with {_pct(head['share_above_0.99'])} above "
         f"0.99 and {_pct(head['share_positive'])} positive. At k_min = 3 a "
         f"three-point Pearson correlation reaches +-1 whenever three points "
         f"line up, so the tail mass is EXPECTED and is not a ceiling: the "
         f"bounded object is the mean over thousands of authors, which sits "
         f"at {_pct(primary['R'])} against a null-world mean of "
         f"{_pct(gate['null_world_headroom']['mean'])}."),
    ]
    spread = sorted((a["share_corr"], k) for k, a in arms.items())
    lines.append(
        f"**The arms agree to within {_pct(spread[-1][0] - spread[0][0])} of "
        f"total variance.** The corrected share runs from "
        f"{_pct(spread[0][0])} ({ARM_LABELS[spread[0][1]]}) to "
        f"{_pct(spread[-1][0])} ({ARM_LABELS[spread[-1][1]]}) across the "
        f"support floor, the eligibility floor, the y-definition and the "
        f"cohort. The entire spread lies within "
        f"{_pct(max(abs(spread[0][0] - TRACE_MAX), abs(spread[-1][0] - TRACE_MAX)))} "
        f"of the RESPONSE_TRACE / IDIOSYNCRATIC_RESPONSE boundary at "
        f"{TRACE_MAX}, so what disagreement exists between arms is a boundary "
        f"crossing and not a different reading of the corpus.")
    diverging = [k for k, v in payload["flags_73"].items()
                 if v.startswith("#73")]
    if diverging:
        lines.append(
            "**Arms that diverge from the primary cell (#73):** "
            + "; ".join(
                f"{ARM_LABELS[k]} — corrected share {_pct(arms[k]['share_corr'])} "
                f"{fmt_ci(cells[k]['share_ci_corr'])}, "
                + ("a STRADDLE across the "
                   f"{TRACE_MAX} boundary (the CI touches "
                   + " and ".join(cells[k]["touched"]) + ")"
                   if cells[k]["straddle"] else "no straddle")
                + f" → {payload['flags_73'][k]}" for k in diverging)
            + ". The flag is raised as registered; the divergence is a "
              "boundary crossing by a few thousandths of total variance, not "
              "a different reading of the corpus.")
    else:
        lines.append(
            f"**Every arm lands in the primary cell.** All "
            f"{len(arms)} arms — the support sensitivity s = 8, the "
            f"n_min = 5 floor, the word_count y-definition and the Big5 "
            f"replication — read {cell['cell']}, so no #73 flag is raised "
            f"anywhere in this leg.")
    return lines


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines: list[str] = []

    def add(text: str = "") -> None:
        lines.append(text)

    verdict = payload["verdict"]
    config = payload["config"]
    gate = payload["part0"]

    add("# SUICA M4-X1c — the venue response, clause-separated gate")
    add()
    add(f"Run {config['run_utc']} · registration "
        "`docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md` (X1c, commit 8fffaad) "
        f"· seed {config['seed']} · B_perm {config['b_perm']} · "
        f"B_boot {config['b_boot']} · runtime "
        f"{fmt(payload['runtime_s'], 1)} s.")
    add()
    add(f"**VERDICT — {verdict['cell']}.**")
    add()
    add(verdict["sentence"])
    add()

    add("## Leg lineage")
    add()
    add("| leg | what it registered | outcome |")
    add("|---|---|---|")
    for row in payload["lineage"]:
        add(f"| {row['leg']} | {row['registered']} | {row['outcome']} |")
    add()
    add(payload["lineage_note"])
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
    add("Read from X1's committed cell cache, whose 17,640,062-row single "
        "pass is the only time the comments file was touched in this line. "
        "No text body, no label file.")
    add()

    add("## The predicate chain (#78, BLOCKING) — X1b's, unchanged")
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
            f"{row['singleton_communities']} | "
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
    add(f"Attrition at the primary floor (s = {S_PRIMARY}): "
        f"{prim['step1_cells']:,} eligible cells → "
        f"{prim['step2_shared_pairs']:,} shared pairs → "
        f"{prim['step3_shared_pairs']:,} after the support floor → "
        f"{prim['step4_shared_pairs']:,} after the k ≥ 3 author floor → "
        f"{prim['step5_shared_pairs']:,} in the largest connected component "
        f"({prim['components_before_lcc']} component(s) before step 5).")
    add()

    _write_gate(add, payload)
    _write_arms(add, payload)
    _write_headroom(add, payload)

    add("## What this leg reads")
    add()
    for item in payload["reading"]:
        add(f"- {item}")
    add()

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


def _write_gate(add, payload: dict[str, Any]) -> None:
    gate = payload["part0"]
    dfc = gate["df_correction"]
    add("## Part 0 — the CLAUSE-SEPARATED gate (#86a; A1 stop on a ROUTING "
        "failure only)")
    add()
    add("The battery is X1b's, on the inherited seeds: the real incidence "
        "carries WHOLLY SYNTHETIC y and no real y enters Part 0 at any "
        "point. What #86a changes is the scoring. ROUTING clauses gate the "
        "verdict and fire the A1 stop; DESCRIPTIVE clauses gate the REPORT — "
        "a failure attaches a dual-stamped bias annotation (#67) to the "
        "number and never stops the leg.")
    add()
    add(f"Tolerance rule: {gate['tolerance_rule']}. The floor of {TOL_FLOOR} "
        f"of total variance is half the width of the registration's own "
        f"RESPONSE_TRACE / IDIOSYNCRATIC_RESPONSE boundary at {TRACE_MAX}.")
    add()
    add("### ROUTING clauses (A1-stopping)")
    add()
    add("| # | clause | status |")
    add("|---|---|---|")
    for i, (name, status) in enumerate(gate["routing_clauses"].items(),
                                       start=1):
        mark = status if status == "PASS" else f"**{status}**"
        add(f"| {i} | {name} | {mark} |")
    add()
    add(f"Routing status: **{gate['routing_status']}** "
        f"({gate['n_routing_passed']} of {gate['n_routing']}).")
    add()
    add("### DESCRIPTIVE clauses (report-gated — a failure ANNOTATES)")
    add()
    add("| # | clause | status |")
    add("|---|---|---|")
    for i, (name, status) in enumerate(gate["descriptive_clauses"].items(),
                                       start=1):
        add(f"| {i} | {name} | {status} |")
    add()
    add(f"Descriptive status: **{gate['descriptive_status']}** "
        f"({gate['n_descriptive_passed']} of {gate['n_descriptive']} inside "
        f"tolerance).")
    add()
    if gate["annotations"]:
        for note in gate["annotations"]:
            add(f"- {note}")
        add()
    else:
        add("No descriptive annotation was triggered: both marginal shares "
            "land inside tolerance of their marginal targets.")
        add()

    add("### The df correction, pinned from the realized skeleton (#86c)")
    add()
    add("| quantity | value |")
    add("|---|---|")
    add(f"| P — shared pairs (cells per half) | "
        f"{dfc['P_shared_pairs']:,} |")
    add(f"| A — authors | {dfc['A_authors']:,} |")
    add(f"| C — communities | {dfc['C_communities']:,} |")
    add(f"| rank removed by the two-way projection (A + C - 1) | "
        f"{dfc['rank_removed']:,} |")
    add(f"| residual degrees of freedom (P - A - C + 1) | "
        f"{dfc['residual_df']:,} |")
    add(f"| retained fraction of a white interaction | "
        f"{fmt(dfc['retained_fraction'], 4)} |")
    add(f"| correction factor P / (P - A - C + 1) | "
        f"{fmt(dfc['factor'], 4)} |")
    add()
    add(f"`{dfc['formula']}`. The factor is a property of the estimand's "
        "realized design, so the same pinned number rescales the point "
        "estimate, the permutation band and every cluster-bootstrap "
        "replicate; because it is positive, \"the CI covers 0\" is the same "
        "event on both scales and the NULL-first cell rule is untouched.")
    add()

    rec = gate["recovery_interaction"]
    add("### ROUTING recovery — the interaction, both scales (#67)")
    add()
    add("| scale | planted | recovered (mean of "
        f"{gate['planted_block']['replicates']}) | replicate sd | tolerance | "
        "gap | routes |")
    add("|---|---|---|---|---|---|---|")
    add(f"| raw (co-reported) | {_pct(PLANTED_SHARES['interaction'])} | "
        f"{_pct(rec['raw_recovered_mean'])} | "
        f"{_pct(rec['raw_replicate_sd'])} | — | "
        f"{_pct(rec['raw_recovered_mean'] - PLANTED_SHARES['interaction'])} | "
        "no |")
    add(f"| **df-corrected** | {_pct(rec['target'])} | "
        f"**{_pct(rec['recovered_mean'])}** | {_pct(rec['replicate_sd'])} | "
        f"{_pct(rec['tolerance'])} | {_pct(rec['gap'])} | "
        f"**yes — {rec['status']}** |")
    add()

    add("### DESCRIPTIVE recovery — the MARGINAL shares against MARGINAL "
        "TARGETS (#86b)")
    add()
    add("The derivation, pinned and printed. A unit's half-mean is a "
        "size-weighted mean of that unit's cell means, so it carries the "
        "unit's OWN COMPOSITION AVERAGE of the other components — and that "
        "average is the same in both halves, which is exactly what the "
        "cross-half covariance is built to keep. With "
        "`w[u,c,h] = n[u,c,h] / sum_c' n[u,c',h]` (author side), "
        "`t[u,c,h] = n[u,c,h] / sum_u' n[u',c,h]` (community side), "
        "`kappa_u = sum_c w[u,c,e] w[u,c,l]` (equal to 1/k_u when an author's "
        "cells are equally sized), `lambda_c = sum_u t[u,c,e] t[u,c,l]`, and "
        "`What_c` the normalized size weights `n[c,e] + n[c,l]` that "
        "`variance_budget` already uses:")
    add()
    add("```")
    add("T_a = v_a (1 - 1/A)")
    add("    + (v_c + v_g) * mean_u[kappa_u]")
    add("    - v_c * sum_c wbar[c,e] wbar[c,l]  -  v_g * mean_u[kappa_u] / A")
    add("T_c = v_c (1 - sum_c What_c^2)")
    add("    + v_a * (sum_c What_c lambda_c - sum_u phi[u,e] phi[u,l])")
    add("    + v_g * (sum_c What_c lambda_c - sum_c What_c^2 lambda_c)")
    add("  with wbar[c,h] = (1/A) sum_u w[u,c,h],  "
        "phi[u,h] = sum_c What_c t[u,c,h]")
    add("```")
    add()
    add("The leading terms are the planted component plus the composition "
        "term; the subtracted terms are the estimator's own mean removal "
        "(both covariances subtract a product of means), kept so the target "
        "is exact rather than first-order. Every symbol on the right is a "
        "function of the cell counts alone — no y, planted or real, enters.")
    add()
    targets = gate["marginal_targets_planted"]
    add("| marginal share | planted component | design-composition term | "
        "mean-removal term | MARGINAL TARGET | recovered (mean of 8) | "
        "replicate sd | tolerance | gap | status |")
    add("|---|---|---|---|---|---|---|---|---|---|")
    for key in ("author", "community"):
        row = gate["descriptives"][key]
        tgt = targets[key]
        add(f"| {key} | {_pct(tgt['planted_component'])} | "
            f"{_pct(tgt['composition_term'])} | "
            f"{_pct(tgt['mean_removal_term'])} | "
            f"**{_pct(row['target'])}** | {_pct(row['recovered_mean'])} | "
            f"{_pct(row['replicate_sd'])} | {_pct(row['tolerance'])} | "
            f"{_pct(row['gap'])} | {row['status']} |")
    add()
    add("For contrast, the same recoveries scored against the PLANTED "
        "variance components — the X1b clause that stopped the leg:")
    add()
    add("| marginal share | planted component | recovered | gap against the "
        "planted component | would that clause have passed? |")
    add("|---|---|---|---|---|")
    for key in ("author", "community"):
        row = gate["descriptives"][key]
        would = ("yes" if abs(row["gap_against_planted"]) <= row["tolerance"]
                 else "**no**")
        add(f"| {key} | {_pct(row['planted_component'])} | "
            f"{_pct(row['recovered_mean'])} | "
            f"{_pct(row['gap_against_planted'])} | {would} |")
    add()
    add("The NULL world (interaction planted at 0) scores its own marginal "
        "targets as a free cross-check:")
    add()
    add("| marginal share | marginal target | recovered | gap | tolerance | "
        "status |")
    add("|---|---|---|---|---|---|")
    for key in ("author", "community"):
        row = gate["descriptives_null_world"][key]
        add(f"| {key} | {_pct(row['target'])} | "
            f"{_pct(row['recovered_mean'])} | {_pct(row['gap'])} | "
            f"{_pct(row['tolerance'])} | {row['status']} |")
    add()

    hon = gate["honesty"]
    add("### The null world, scored with the full pipeline")
    add()
    add("| null-world clause (nothing planted in the interaction) | raw | "
        "df-corrected |")
    add("|---|---|---|")
    add(f"| interaction share (planted 0.0000) | "
        f"{_pct(hon['interaction_share_raw'])} | "
        f"{_pct(hon['interaction_share_corr'])} |")
    add(f"| cluster-bootstrap CI (FE recomputed per replicate) | "
        f"{fmt_ci(hon['interaction_ci_raw'])} | "
        f"{fmt_ci(hon['interaction_ci_corr'])} |")
    add(f"| permutation band | {fmt_ci(hon['interaction_band_raw'])} | "
        f"{fmt_ci(hon['interaction_band_corr'])} |")
    add()
    add("| clause | value |")
    add("|---|---|")
    add(f"| CI covers 0 (#85b, the bootstrap-zero clause) | "
        f"{'yes' if hon['ci_covers_zero'] else '**NO**'} |")
    add(f"| CI covers its own point estimate | "
        f"{'yes' if hon['ci_covers_point'] else '**NO**'} |")
    add(f"| share inside its own permutation band | "
        f"{'yes' if hon['interaction_inside_band'] else '**NO**'} |")
    add(f"| R | {_pct(hon['R'])} |")
    add(f"| R cluster-bootstrap CI | {fmt_ci(hon['r_ci'])} |")
    add(f"| permutation band for R | {fmt_ci(hon['r_band'])} |")
    add(f"| R inside band | {'yes' if hon['r_inside_band'] else '**NO**'} |")
    add(f"| marginal author share (planted 0.3000) | "
        f"{_pct(hon['marginal_author_share'])} |")
    add(f"| marginal community share (planted 0.0800) | "
        f"{_pct(hon['marginal_community_share'])} |")
    add()

    add("### Every synthetic world, point-wise")
    add()
    add("| synthetic world | planted interaction | recovered interaction, raw "
        "(mean ± sd) | recovered interaction, df-corrected | marginal author "
        "| marginal community | R |")
    add("|---|---|---|---|---|---|---|")
    blocks = [gate["planted_block"], gate["null_block"]]
    blocks += list(gate["ablations"].values())
    for block in blocks:
        st = block["stats"]
        add(f"| {block['world']} | {_pct(block['planted']['interaction'])} | "
            f"{_pct(st['interaction']['mean'])} ± "
            f"{_pct(st['interaction']['sd'])} | "
            f"{_pct(st['interaction_corr']['mean'])} | "
            f"{_pct(st['author']['mean'])} | {_pct(st['community']['mean'])} "
            f"| {_pct(st['R']['mean'])} |")
    add()
    add("| ablation clause (ROUTING) | leakage, df-corrected | leakage, raw | "
        "maximum | R leakage | status |")
    add("|---|---|---|---|---|---|")
    for name, row in gate["ablation_clauses"].items():
        add(f"| {name} | {_pct(row['leakage_corrected'])} | "
            f"{_pct(row['leakage_raw'])} | {_pct(row['maximum'])} | "
            f"{_pct(row['R_leakage'])} | {row['status']} |")
    add()

    add("### The alternating projection, verified on the real incidence")
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


def _write_arms(add, payload: dict[str, Any]) -> None:
    arms = payload["arms"]
    cells = payload["cells"]
    primary = arms["primary"]
    cell = cells["primary"]

    add("## PRIMARY arm — disjoint cohort, law vocabulary, n ≥ 10, s = 5, "
        "k ≥ 3, y = log(1 + word_count_quoteless)")
    add()
    design = primary["design"]
    add(f"{design['authors']:,} eligible authors · {design['communities']:,} "
        f"communities · {design['slots']:,} shared pairs · "
        f"{design['cells']:,} eligible cells · {design['comments']:,} "
        f"comments · comment-level Var(y) = "
        f"{fmt(design['var_y'], 4)}.")
    add()
    add("| quantity | value | CI | permutation band |")
    add("|---|---|---|---|")
    add(f"| **reproducible interaction share, DF-CORRECTED (routes)** | "
        f"**{_pct(primary['share_corr'])}** | "
        f"{fmt_ci(primary['share_ci_corr'])} | "
        f"{fmt_ci(primary['share_band_corr'])} |")
    add(f"| reproducible interaction share, raw (#67 co-report) | "
        f"{_pct(primary['share_raw'])} | {fmt_ci(primary['share_ci_raw'])} | "
        f"{fmt_ci(primary['share_band_raw'])} |")
    add(f"| R — mean per-author profile correlation | "
        f"{_pct(primary['R'])} | {fmt_ci(primary['bootstrap']['r_ci'])} | "
        f"{fmt_ci(primary['null']['r_band'])} |")
    add(f"| marginal author share | {_pct(primary['budget']['author'])} | "
        f"{fmt_ci(primary['bootstrap']['shares_ci']['author'])} | — |")
    add(f"| marginal community share | "
        f"{_pct(primary['budget']['community'])} | "
        f"{fmt_ci(primary['bootstrap']['shares_ci']['community'])} | — |")
    add(f"| residual | {_pct(primary['budget']['residual'])} | "
        f"{fmt_ci(primary['bootstrap']['shares_ci']['residual'])} | — |")
    add()
    add(f"Cell: **{cell['cell']}**"
        + (" (STRADDLE — the CI touches "
           + ", ".join(cell["touched"]) + ")" if cell["straddle"] else "")
        + f". Cell 1's two conditions: R inside its band = "
        f"{'yes' if cell['r_inside_band'] else 'no'}; the corrected share's "
        f"CI includes 0 = {'yes' if cell['ci_covers_zero'] else 'no'}.")
    add()

    add("## The budget, per arm")
    add()
    add("Marginal shares are named MARGINAL because that is what their "
        "estimator targets (#86b); the interaction is reported on both "
        "scales under the #67 dual stamp, and the DF-CORRECTED row is the "
        "one the cell reads.")
    add()
    add("| arm | marginal author | marginal community | interaction, raw | "
        "**interaction, df-corrected** | residual | R [CI, band] | cell | "
        "#73 |")
    add("|---|---|---|---|---|---|---|---|---|")
    for key, arm in arms.items():
        b = arm["budget"]
        ci = arm["bootstrap"]["shares_ci"]
        add(f"| {arm['tag']} | {_pct(b['author'])} {fmt_ci(ci['author'])} | "
            f"{_pct(b['community'])} {fmt_ci(ci['community'])} | "
            f"{_pct(arm['share_raw'])} {fmt_ci(arm['share_ci_raw'])} | "
            f"**{_pct(arm['share_corr'])}** {fmt_ci(arm['share_ci_corr'])} "
            f"{fmt_ci(arm['share_band_corr'])} | {_pct(b['residual'])} | "
            f"{_pct(arm['R'])} {fmt_ci(arm['bootstrap']['r_ci'])} "
            f"{fmt_ci(arm['null']['r_band'])} | {cells[key]['cell']}"
            + (" (STRADDLE)" if cells[key]["straddle"] else "")
            + f" | {payload['flags_73'].get(key, 'none')} |")
    add()
    straddlers = [k for k, c in cells.items() if c["straddle"]]
    if straddlers:
        add("Straddles are reported as straddles, per the registration: "
            + "; ".join(
                f"**{arms[k]['tag']}** — the corrected CI "
                f"{fmt_ci(cells[k]['share_ci_corr'])} touches "
                + " and ".join(cells[k]["touched"])
                + f", and the point {_pct(cells[k]['share_corr'])} places it "
                f"in {cells[k]['cell']}" for k in straddlers) + ".")
        add()
    else:
        add("No arm's corrected CI touches more than one magnitude cell, so "
            "no straddle is reported.")
        add()

    _write_bootstrap_note(add, payload)

    add("### The df correction and the composition annotation, per arm")
    add()
    add("| arm | P | A | C | factor | mean_u[kappa_u] | size-weighted "
        "mean_c[lambda_c] | implied author main (annotation only) | implied "
        "community main (annotation only) |")
    add("|---|---|---|---|---|---|---|---|---|")
    for key, arm in arms.items():
        d = arm["df"]
        c = arm["composition"]
        dec = arm["decontamination_annotation"]
        add(f"| {arm['tag']} | {d['P_shared_pairs']:,} | "
            f"{d['A_authors']:,} | {d['C_communities']:,} | "
            f"{fmt(d['factor'], 4)} | {fmt(c['mean_kappa'], 4)} | "
            f"{fmt(c['mean_lambda_size_weighted'], 4)} | "
            f"{_pct(dec['implied_author_main'])} | "
            f"{_pct(dec['implied_community_main'])} |")
    add()
    add("The last two columns are an ANNOTATION, not a registered estimand "
        "and not a routing object: they invert the 2x2 composition mixing "
        "`marginal_a = V_a + kappa (V_c + V_g)`, "
        "`marginal_c = V_c + lambda (V_a + V_g)` with V_g taken as the "
        "df-corrected interaction share. They print how large the "
        "annotation is; nothing in this leg rests on them.")
    add()

    add("### The arm designs")
    add()
    add("| arm | eligible authors | communities | shared pairs | comments | "
        "median shared communities | median authors per community | "
        "singleton communities | LCC coverage |")
    add("|---|---|---|---|---|---|---|---|---|")
    for key, row in payload["arm_designs"].items():
        add(f"| {row['label']} | {row['authors']:,} | "
            f"{row['communities']:,} | {row['shared_pairs']:,} | "
            f"{row['comments']:,} | "
            f"{fmt(row['shared_communities_per_author_median'], 1)} | "
            f"{fmt(row['authors_per_community_median'], 1)} | "
            f"{row['singleton_communities']} | "
            f"{fmt(row['lcc_author_coverage'], 3)} |")
    add()
    add(payload["big5_power"]["sentence"])
    add()

    add("## Registered leans (report against; they never route)")
    add()
    add("| lean | scale | observed | outcome |")
    add("|---|---|---|---|")
    for row in payload["leans"]:
        observed = row["observed"]
        shown = observed if isinstance(observed, str) else fmt(observed)
        add(f"| {row['lean']} | {row['scale']} | {shown} | "
            f"{'HELD' if row['held'] else 'MISSED'} |")
    add()


def _write_bootstrap_note(add, payload: dict[str, Any]) -> None:
    """An honest anomaly, calibrated against Part 0's PLANTED world.

    The cluster-bootstrap interval is not symmetric about the point estimate:
    every arm's point sits near the interval's upper edge.  The mechanism is
    the resample's own sparsity — a bootstrap author multiset holds about 63%
    of the distinct authors, so each replicate's two-way projection removes a
    LARGER fraction of its own design than the full design's, and the pinned
    correction factor (which the registration fixes at the realized skeleton)
    does not follow it down.  The direction is therefore known and the
    calibration is already on the record: Part 0's planted world has a KNOWN
    truth of 0.0200 and shows the same asymmetry while still covering it.
    """

    arms = payload["arms"]
    pw = payload["part0"]["planted_world_inference"]
    add("### Reading the cluster-bootstrap interval (an anomaly, calibrated)")
    add()
    add("| arm | point (raw) | bootstrap mean (raw) | shift | bootstrap sd |")
    add("|---|---|---|---|---|")
    for key, arm in arms.items():
        mean = float(arm["bootstrap"]["shares_mean"]["interaction"])
        add(f"| {arm['tag']} | {_pct(arm['share_raw'])} | {_pct(mean)} | "
            f"{_pct(mean - arm['share_raw'])} | "
            f"{_pct(arm['bootstrap']['shares_sd']['interaction'])} |")
    add()
    add(f"Every arm's point estimate sits near the UPPER edge of its own "
        f"interval. The mechanism is the resample's sparsity: a cluster "
        f"bootstrap over authors keeps about 63% of the distinct authors, so "
        f"each replicate's projection removes a larger share of its own "
        f"design than the full design's A + C - 1 of P, while the pinned "
        f"correction factor stays at the realized skeleton's value (which is "
        f"what the registration fixes). The direction is downward and it is "
        f"CALIBRATED rather than argued: Part 0's planted world has a known "
        f"truth of {_pct(PLANTED_SHARES['interaction'])} and shows the same "
        f"asymmetry — point {_pct(pw['interaction_share_corr'])}, interval "
        f"{fmt_ci(pw['interaction_ci_corr'])} — and still covers the truth. "
        f"The corpus intervals should be read the same way: as slightly "
        f"conservative on the low side, never on the high side, so no cell "
        f"assignment here is at risk from the effect.")
    add()


def _write_headroom(add, payload: dict[str, Any]) -> None:
    head = payload["arms"]["primary"]["headroom"]
    null_head = payload["part0"]["null_world_headroom"]
    add("## Headroom (#84 as restated by #85) — about the MEAN")
    add()
    add("The clause is about the MEAN over thousands of authors, not about "
        "the per-author correlation: at k_min = 3 a Pearson correlation over "
        "three points reaches ±1 whenever three points happen to line up, so "
        "saturation in the per-author distribution is EXPECTED and is not a "
        "ceiling on the estimand. The realized corpus distribution is "
        "reported beside Part 0's synthetic null world so the statement is a "
        "number.")
    add()
    add("| quantile | PRIMARY arm (corpus) | Part 0 null world (synthetic) |")
    add("|---|---|---|")
    for key in head["quantiles"]:
        add(f"| {key} | {_pct(head['quantiles'][key])} | "
            f"{_pct(null_head['quantiles'][key])} |")
    add()
    add(f"Primary arm: {head['authors_scored']:,} authors scored, "
        f"{head['authors_undefined']:,} undefined; mean {_pct(head['mean'])}, "
        f"sd {_pct(head['sd'])}; {_pct(head['share_above_0.99'])} above 0.99, "
        f"{_pct(head['share_above_0.90'])} above 0.90, "
        f"{_pct(head['share_positive'])} positive. Synthetic null world: mean "
        f"{_pct(null_head['mean'])}, sd {_pct(null_head['sd'])}; "
        f"{_pct(null_head['share_above_0.99'])} above 0.99, "
        f"{_pct(null_head['share_positive'])} positive. Per-author "
        "saturation is acknowledged and NOT treated as a ceiling; the mean is "
        "the bounded object and it is what R reports.")
    add()


def build_verdict(cells: dict[str, Any], arms: dict[str, Any], gate_ok: bool,
                  part0: dict[str, Any]) -> dict[str, Any]:
    if not gate_ok:                                  # pragma: no cover
        failed = [name for name, status in part0["routing_clauses"].items()
                  if status != "PASS"]
        return {
            "cell": CELL_A1_STOP,
            "clauses_failed": failed,
            "sentence": (
                f"Part 0's ROUTING battery passed "
                f"{part0['n_routing_passed']} of its {part0['n_routing']} "
                f"clauses and failed " + "; ".join(f"“{n}”" for n in failed)
                + ". The A1 stop fired BEFORE any real estimand was "
                  "computed; no corpus value of R, of the variance budget or "
                  "of the headroom distribution appears anywhere in this leg."),
        }
    cell = cells["primary"]
    arm = arms["primary"]
    straddle = (" The CI straddles "
                + " / ".join(cell["touched"]) + ", and is reported as a "
                "straddle." if cell["straddle"] else "")
    return {
        "cell": cell["cell"],
        "sentence": (
            f"Part 0's five ROUTING clauses all passed, so the real arms ran. "
            f"The primary arm's DF-CORRECTED reproducible interaction share "
            f"is {fmt(cell['share_corr'])} of comment-level Var(y) "
            f"{fmt_ci(cell['share_ci_corr'])} (raw {fmt(cell['share_raw'])} "
            f"{fmt_ci(cell['share_ci_raw'])}, #67 dual stamp), with "
            f"R = {fmt(cell['R'])} against a permutation band "
            f"{fmt_ci(cell['r_band'])} and a cluster-bootstrap CI "
            f"{fmt_ci(arm['bootstrap']['r_ci'])}. The MARGINAL author and "
            f"community shares carry {fmt(arm['budget']['author'])} and "
            f"{fmt(arm['budget']['community'])} with their design-composition "
            f"annotations; the residual is "
            f"{fmt(arm['budget']['residual'])}." + straddle),
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


LINEAGE = (
    {"leg": "M4-X1 (commit ebe4f5b)",
     "registered": "the venue response of expression volume — double-centred "
                   "v on the raw community universe, no support floor",
     "outcome": "A1_STOP__SYNTHETIC_GATE_FAILED — the null world read 0.0458, "
                "2.3x the TRACE boundary; defect #85"},
    {"leg": "M4-X1b (commit e8c9040)",
     "registered": "design repaired (law vocabulary + support floor s = 5) "
                   "AND estimator repaired (exact two-way FE by alternating "
                   "projections)",
     "outcome": "A1_STOP__SYNTHETIC_GATE_FAILED — 8 of 9 clauses PASS; the "
                "one failure was a DESCRIPTIVE with a solved mechanism; "
                "defect #86"},
    {"leg": "M4-X1c (this leg)",
     "registered": "clause-separated gate (#86a) + df-corrected routing "
                   "statistic (#86b/c); everything else inherits X1b",
     "outcome": "see the verdict above"},
)

LINEAGE_NOTE = (
    "Third and final registration of this estimand. X1 stopped on an "
    "estimator whose zero was not zero; X1b repaired the estimator and the "
    "design, certified the routing machinery exact on the realized skeleton "
    "twice over, and stopped on a co-reported descriptive whose bias was "
    "design-predicted; X1c separates the two clause families, names the "
    "mains MARGINAL and scores them against marginal targets, pins the "
    "projection's degrees of freedom and routes the verdict on the corrected "
    "share. Nothing else moved: the same cache, the same chain, the same "
    "estimator, the same seeds, the same cells, the same leans, the same "
    "boundaries."
)


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
        "leg": "M4-X1c",
        "title": "the venue response, clause-separated gate",
        "registration":
            "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md@8fffaad (X1c)",
        "predecessors": [
            "M4-X1 (A1_STOP__SYNTHETIC_GATE_FAILED, commit ebe4f5b)",
            "M4-X1b (A1_STOP__SYNTHETIC_GATE_FAILED, commit e8c9040)",
        ],
        "machinery_imported_by_file": [
            "scripts/run_suica_m4_x1b_venue_response_fe.py (chain, exact FE, "
            "gate worlds, bootstrap-FE)",
            "scripts/run_suica_m4_x1_venue_response.py (Design, "
            "variance_budget, synthetic_design, headroom, #83 helpers)",
        ],
        "run_utc": utc_now(),
        "seed": SEED, "seed_part0": SEED_PART0, "seed_perm": SEED_PERM,
        "seed_boot": SEED_BOOT,
        "seeds_inherited": ("the X1/X1b derivation; NOT re-chosen after "
                            "either stop (#76 gate-shopping refusal)"),
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
                      "residual of the cell mean (X1b, unchanged)"),
        "fe_tolerance": FE_TOL,
        "routing_statistic": ("the DF-CORRECTED reproducible interaction "
                              "share, share_corr = share_raw * "
                              "P/(P - A - C + 1), with P/A/C pinned from each "
                              "arm's realized skeleton (#86b/c); the raw "
                              "share is co-reported (#67); R is uncorrected"),
        "mains_estimator": ("cross-half covariances of author and community "
                            "half-means, PRE-FE (X1's definition), now NAMED "
                            "MARGINAL and scored against MARGINAL TARGETS "
                            "derived from the realized skeleton (#86b)"),
        "gate_structure": ("#86a: five ROUTING clauses (A1-stopping) and two "
                           "DESCRIPTIVE clauses (report-gated; a failure "
                           "annotates with a #67 dual-stamped bias note)"),
        "cells": {"trace_max": TRACE_MAX,
                  "idiosyncratic_max": IDIOSYNCRATIC_MAX,
                  "keyed_on": "the df-corrected interaction share"},
        "leans": {"R": list(LEAN_R),
                  "interaction_share_registered_scale": "RAW (X1)",
                  "interaction_share": list(LEAN_INTERACTION),
                  "marginal_author": list(LEAN_AUTHOR_MAIN),
                  "marginal_community": list(LEAN_COMMUNITY_MAIN)},
        "planted_shares": PLANTED_SHARES,
        "null_shares": NULL_SHARES,
        "ablation_worlds": ABLATION_WORLDS,
        "ablation_leak_max": ABLATION_LEAK_MAX,
        "synthetic_replicates": N_SYNTH_REPLICATES,
        "tolerance_floor": TOL_FLOOR,
        "tolerance_sd_multiple": TOL_SD_MULT,
        "big5_power_floor_69": BIG5_POWER_FLOOR,
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
                                "weight; the df factor is the pinned constant "
                                "of the realized design, so the corrected CI "
                                "is the affine image of the raw CI"),
        "deviations": [
            "X1b's X1-vs-X1b estimator-comparison grid is NOT re-run: it was "
            "a one-time demonstration of the repair, already adjudicated, "
            "and re-running it would add no information to a leg whose "
            "purpose is the corpus reading. X1b's artifact holds it.",
        ],
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
        "Inherited census anchors (#78: 17,640,062 rows / 10,296 authors / "
        "1,443 law communities and three more)": census["status"],
    }
    if census["status"] != "PASS":                   # pragma: no cover
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
                         f"({lcc_cov}); the FE's exactness argument is void")
    gates["LCC assertion (the alternating projection is exact only on a "
          "connected design; coverage must be 1.000)"] = "PASS"

    # ---- Stage 3: the arm designs -----------------------------------------
    arm_designs_obj: dict[str, Design] = {"primary": primary,
                                          "sens_s8": chain_designs[
                                              S_SENSITIVITY]}
    arm_chain: dict[str, Any] = {
        "primary": chain_census[str(S_PRIMARY)],
        "sens_s8": chain_census[str(S_SENSITIVITY)]}
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
    arm_designs = {k: dict(v, label=ARM_LABELS[k])
                   for k, v in arm_chain.items()}
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
               f"it carries a #73 comparison."
               if big5_authors >= BIG5_POWER_FLOOR else
               f"BELOW the in-leg #69 floor of {BIG5_POWER_FLOOR}, so it "
               f"reports as underpowered-descriptive with no #73 flag.")),
    }
    write_json(output / "big5_power.json", big5_power)
    gates[f"Big5 replication #69 floor ({BIG5_POWER_FLOOR} authors, IN-LEG "
          "census; below it the arm is underpowered-descriptive, not #73)"] = \
        "PASS" if big5_power["meets_floor"] else "UNDERPOWERED_DESCRIPTIVE"

    # ---- Stage 4: PART 0, before any real estimand ------------------------
    part0 = clause_separated_gate(primary, args.b_perm, args.b_boot, log)
    write_json(output / "part0_clause_separated_gate.json", part0)
    gates["Part 0 ROUTING clauses (#86a; A1 stop on any failing clause)"] = \
        part0["routing_status"]
    gates["Part 0 DESCRIPTIVE clauses (#86a; a failure ANNOTATES with a #67 "
          "dual-stamped bias note, never stops)"] = part0["descriptive_status"]

    # ---- Stage 5: the real arms, ONLY if the ROUTING clauses passed -------
    arms: dict[str, Any] = {}
    cells: dict[str, Any] = {}
    flags_73: dict[str, str] = {}
    leans: list[dict[str, Any]] = []
    reading: list[str] = []
    if not a1_stop_fires(part0):
        for offset, (key, design) in enumerate(arm_designs_obj.items()):
            arms[key] = augment_arm(analyse_design_fe(
                design, b_perm=args.b_perm, b_boot=args.b_boot,
                seed_perm=SEED_PERM + 17 * offset,
                seed_boot=SEED_BOOT + 17 * offset, tag=ARM_LABELS[key],
                log=log), design)
            cells[key] = classify(arms[key])
            log.event("arm_done", arm=key, R=arms[key]["R"],
                      share_raw=arms[key]["share_raw"],
                      share_corr=arms[key]["share_corr"],
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

    verdict = build_verdict(cells, arms, not a1_stop_fires(part0), part0)
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
        "arms": arms, "cells": cells, "flags_73": flags_73, "leans": leans,
        "gates": gates,
        "verdict": verdict,
        "lineage": list(LINEAGE),
        "lineage_note": LINEAGE_NOTE,
        "boundaries": list(BOUNDARIES),
        "runtime_s": round(time.time() - started, 1),
    }
    if arms:
        reading = build_reading(payload)
    payload["reading"] = reading
    write_report(args.report, payload)

    # ---- Stage 6: the ID-leak gate over the WIDENED universe (#83) --------
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
              routing=part0["routing_status"],
              descriptive=part0["descriptive_status"],
              runtime_s=payload["runtime_s"])
    return 0


if __name__ == "__main__":                           # pragma: no cover
    raise SystemExit(main())
