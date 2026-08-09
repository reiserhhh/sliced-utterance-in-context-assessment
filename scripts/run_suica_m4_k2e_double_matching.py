#!/usr/bin/env python3
"""M4-K2e -- double matching: does the reader tax RAW person-variance
(H-VAR: field ~ lambda*r^q - kappa*V_person), or is occasion-bound content
intrinsically expensive (H-SPECIES)?  Link-free discriminator.

Registered spec: docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md section "M4-K2e -- Double
matching ..." (REGISTERED 2026-08-09, BEFORE RUN, commit 0db4480), together with
the K2d OUTCOME and planner adjudication immediately above it (defect #22,
standing rule 16, the pilot convention, the instrument boundary on GAP,
kappa_hat = -0.7220359963712748, q = 1.8528700746510731).
Theory: docs/SUICA_IDENTITY_THEORY_V1.md T4 (S3), appendices J and K.

Executor standing: implementation and execution only.  Everything labelled
"RN-n" below is a register-note -- an operationalization of something the
registration left open (standing rule 9) -- fixed and written to
reports/SUICA_M4_K2E_DOUBLE_MATCHING_REPORT.md Part 0 BEFORE any main arm ran.

Reuse boundary (registration: "machinery unchanged"; the dispatch order asked
for K2d's script to be reused WHOLESALE):
  * scripts/run_suica_m4_k2d_frontier_carrier.py (k2d()) -- install_species_weights
    (k2d:206-238), verify_species_weights (k2d:240-267), predicted_attenuation
    (k2d:273-278), solve_slow_for_target (k2d:281-307), solve_int_for_target
    (k2d:310-339), clause_vector (k2d:427-441), assign_cell (k2d:444-465),
    base_of/sign_of, enumerate_cell_space (k2d:479-538), pooled_q (k2d:644-674),
    rederive_anchors (k2d:680-785), read_csv_rt, mde_paired.  Imported and CALLED
    UNMODIFIED.
  * through k2d: k2c's bootstrap_card_pair / ols_slope / T_QUANTILES, and k2b's
    layout / build_k2b_world / emit_panel / card_channel_frame / arm_shares /
    arm_predictions / bootstrap_card / run_field_world / CHANNELS.
  * suica_core/ is READ-ONLY and untouched.

THE ONE NEW MEASUREMENT OBJECT is `realized_person_shares()` -- k2b:698-703's
own arithmetic factored out so it can run on EVERY world (k2b computes realized
variance shares only under `verify=True`).  G1e's post-arms clause needs the
REALIZED V_person share on the adjudicated worlds, not just on a pilot.  Part 0
proves it bit-exact against k2b's verify route on a pilot world.

THE DESIGN (registration's solvability argument, verified numerically in Part 0):
arm a is slow-only with slow signal fraction v_A at phi .90; arm b carries v_B
slow at phi .98 PLUS w_B interaction, with
    v_B + w_B = v_A                     (total non-trait person content matched)
    v_B*kappa(.98) + w_B*kappa_int = v_A*kappa(.90)     (attenuation matched)
    =>  v_B = v_A*(kappa(.90) - kappa_int)/(kappa(.98) - kappa_int),  w_B = v_A - v_B.
kappa(phi) and kappa_int are read straight out of the K2a-validated attenuation
algebra (k2b:533-584): with V_s fixed and the person total matched, the trait
weight A = (1-v)*V_s/2 is IDENTICAL in the two arms, so the attenuation
    r^2 = A*K1 / (N*(A + Bv*kappabar(phi) + C*kappabar_int + E*kappabar_int))
is EXACTLY linear in (Bv, C) across the pair, and the two constraints are an
exactly solvable 2x2 system -- not a linearization.  See `kappa_coefficients()`.

Stages (foreground, chunked, resumable; artifacts under
results/m4_k2e_double_matching/):
  --stage part0     kappa(.90)/kappa(.98)/kappa_int, the solved shares, BOTH
                    matching residuals per DM pair, the VS pair with its
                    registered D_VS prediction, the rule-16 FULL-OBJECT
                    enumeration (cells x leans x L-VS -> routing), and
                    G0e..G5e on RESERVED pilot worlds 9901-9904.  `arms`
                    refuses to run unless every Part-0 gate passes AND the
                    Part-0 report exists on disk.
  --stage arms      the 6 arms x (per-pair N) worlds, chunked by WORLD RANGE
                    (--worlds a-b); an arm runs a world index only if its
                    pair's selected N covers it (per-pair escalation).
  --stage finalize  G1e post-arms double matching, D per pair + CELL, the lean
                    predicate, L-VS, routing, q-update over 25 arms, rule-13
                    stability, decision.json.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import suica_core.v8_realtext_relation_field as v8  # noqa: E402

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"

# --- registration-fixed constants -------------------------------------------
MASTER_SEED = 20260819             # registration: "master_seed 20260819"
WORLDS_PER_ARM = 32                # registration: "32 worlds/arm"
ESCALATION_LADDER = (32, 64)       # registration G2e: "escalate 32->64 once per pair"
# RN-4: the registration offers "4-world pilot per pair (or 2-world with the
# registered chi-square 90% df-inflation -- the agent states which and applies
# it)".  CHOSEN: the 4-WORLD pilot (3 df instead of 1), because K2d's anomaly
# A-5 -- which is what bought this convention -- showed a 2-world pilot
# underestimating the realized paired sd by 2.05x-7.83x on a 1-df estimate.
# The extra cost is 12 arm-worlds (~7 s).  The chi-square 90% inflation factor
# at 3 df is reported alongside as a DISCLOSED conservative companion; the GATE
# is the registered plain 4-world MDE.
PILOT_WORLDS = (9901, 9902, 9903, 9904)   # RESERVED; disjoint from main 0..63
B_BOOT = 2000                      # registration G3e: "B=2000, seed=master"
B_BOOT_HIGH = 20000                # registration G3e: ">=10xB" (rule 13)

PHI_A, PHI_B = 0.90, 0.98
DM_TARGETS: tuple[tuple[str, float], ...] = (("DM-68", 0.68), ("DM-56", 0.56))
VS_PAIR = "VS-62"
VS_TARGET = 0.62

# registration: "K2d's enumeration table verbatim (M1=0.020, M2=0.010)"
M1 = 0.020
M2 = 0.010
# registration G1e
MATCH_TOL_PART0 = 1e-12            # predicted attenuation AND predicted V_person
MATCH_TOL_MEASURED = 0.005         # measured attenuation difference CI
VPERSON_TOL_MEASURED = 0.005       # realized V_person share difference
# registration G2e: "MDE(80%, a=.05, paired, n=32) <= 0.010 per pair"
MDE_TARGET = 0.010

# registration: the estimand promoted to a REGISTERED quantitative prediction
KAPPA_HAT = -0.7220359963712748
L_VS_TOL = 0.010                   # "|D_VS - pred| <= 0.010"

# K2b's arm-independent reader efficiency; the q-update's intercept scale only
# (the OLS slope is invariant to lambda -- verified numerically every run).
K2B_LAMBDA = 0.17417497661611914

# chi-square 90% one-sided df inflation (DISCLOSURE ONLY, never a gate here):
# sigma <= sd_pilot * sqrt(df / chi2.ppf(0.10, df)).  df = len(PILOT_WORLDS) - 1.
# Values from scipy.stats.chi2.ppf, cross-checked against scipy at Part 0 when
# importable (K2c's T_QUANTILES precedent, after K2b's anomaly A-1).
CHI2_PPF_010 = {1: 0.01579077409343122, 3: 0.5843743741551835}


def chi2_inflation(df: int) -> tuple[float, dict[str, Any]]:
    """sqrt(df / chi2.ppf(0.10, df)) -- the 90% one-sided upper bound on sigma
    from a df-degree-of-freedom sd estimate.  DISCLOSURE ONLY in this leg."""
    table = float(CHI2_PPF_010[df])
    check: dict[str, Any] = {"df": df, "chi2_ppf_010_table": table, "scipy": None}
    try:
        from scipy import stats  # noqa: PLC0415
        live = float(stats.chi2.ppf(0.10, df))
        check["scipy"] = live
        check["abs_difference"] = abs(live - table)
        check["bit_exact"] = bool(live == table)
        table = live
    except Exception as exc:                                   # pragma: no cover
        check["scipy_error"] = repr(exc)
    return math.sqrt(df / table), check

OUT = ROOT / "results" / "m4_k2e_double_matching"
REPORT = ROOT / "reports" / "SUICA_M4_K2E_DOUBLE_MATCHING_REPORT.md"
K2D_OUT = ROOT / "results" / "m4_k2d_frontier_carrier"
K2C_OUT = ROOT / "results" / "m4_k2c_matched_pairs"
K2B_OUT = ROOT / "results" / "m4_k2b_t4_branch"
K2B_PRIMARY_ARMS = ("A1", "A2", "A3", "A4", "A5", "A6")
K2D_MASTER_SEED = 20260818

_K2D: Any = None


def k2d() -> Any:
    global _K2D
    if _K2D is None:
        path = ROOT / "scripts" / "run_suica_m4_k2d_frontier_carrier.py"
        spec = importlib.util.spec_from_file_location(
            "run_suica_m4_k2d_frontier_carrier", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _K2D = module
    return _K2D


def k2c() -> Any:
    return k2d().k2c()


def k2b() -> Any:
    return k2d().k2b()


def read_csv_rt(path: Path) -> pd.DataFrame:
    """G5e: every artifact re-read with float_precision='round_trip'."""
    return k2d().read_csv_rt(path)


def mde_paired(sd_diff: float, n: int) -> float:
    return k2d().mde_paired(sd_diff, n)


def world_seed_for(world: int) -> int:
    """RN-5: K2e's OWN seed lineage (master_seed 20260819, salt 'm4k2e-world').
    The seed depends on the WORLD INDEX ONLY, so every arm -- including the two
    arms of a pair, which differ in share / phi / w_int -- shares the trait b,
    the AR innovations, the frame shocks, the interaction loadings a_i and the
    noise bit-for-bit.  Every within-pair D is therefore a within-world
    difference."""
    return int(
        v8.stable_bucket(f"{MASTER_SEED}-{world}", salt="m4k2e-world", modulus=2**31 - 1)
    )


def run_field_world(arm_id: str, world_index: int, world, w, *, verify: bool = False):
    """RN-6 (provenance): k2b.run_field_world is called UNMODIFIED, so the corpus
    tag it builds keeps the literal prefix 'm4k2b-'.  The tag is a hash label
    seeding the deployed transition-null permutation streams (f1:199-206);
    prefixing every K2e arm id with 'K2E-' makes every tag DISJOINT from every
    K2b/K2c/K2d tag.  The returned row's 'arm' field is rewritten to the clean
    K2e id."""
    row = k2b().run_field_world(f"K2E-{arm_id}", world_index, world, w, verify=verify)
    row["arm"] = arm_id
    return row


# ---------------------------------------------------------------------------
# THE ONE NEW MEASUREMENT OBJECT: realized variance shares on EVERY world.

def realized_person_shares(world, w) -> dict[str, float]:
    """k2b:698-703's arithmetic, factored out (k2b computes it only under
    `verify=True`, i.e. on one world per arm).  G1e's post-arms clause is about
    the REALIZED V_person share on the ADJUDICATED worlds, so it must run
    everywhere.  Identical route: per-channel `emit_panel`, mean square over
    every emitted coordinate, normalized by the total.  Part 0 proves it
    BIT-EXACT against k2b's own verify-route output on a pilot world."""
    m = k2b()
    parts = [m.emit_panel(world, w, active=(c,)) for c in m.CHANNELS]
    var_ch = {name: float(np.mean(np.concatenate([b.ravel() for b in p]) ** 2))
              for name, p in zip(m.CHANNELS, parts)}
    total = sum(var_ch.values())
    return {name: value / total for name, value in var_ch.items()}


def person_share_design(share: float, int_share: float) -> float:
    """V_person as the DESIGN variance share (slow + interaction), in exactly the
    currency kappa_hat was fitted in -- k2b.arm_shares, i.e. sqrt-then-square of
    the designed fractions.  Verified bit-exact in G0e against K2d's
    post_hoc_descriptive.json person_var columns."""
    sh = k2b().arm_shares(share, "zero" if int_share == 0.0 else f"int:{int_share!r}")
    return sh["slow"] + sh["int"]


# ---------------------------------------------------------------------------
# PART 0, step 1: the kappa coefficients and the CLOSED-FORM double match.

def kappa_coefficients() -> dict[str, Any]:
    """kappa(phi) and kappa_int, read out of the K2a-validated attenuation
    algebra (k2b:533-584) on THIS panel's (context, m) norm cells.

    k2b:541-543 writes the per-cell card variance as
        var_card = A + Bv*ar_set_var(arange(m), phi) + C/m + E/m
    and the attenuation as  r = sqrt(A)*K1 / sqrt(K1*Vbar * N)  with
        K1 = sum_cell n*kap,  N = sum_cell n,
        K1*Vbar = sum_cell n*kap*var_card.
    Define the kap-weighted averages
        kappa(phi)  = sum n*kap*ar_set_var(arange(m), phi) / sum n*kap
        kappa_int   = sum n*kap*(1/m)                      / sum n*kap
    so that  K1*Vbar = K1*(A + Bv*kappa(phi) + (C+E)*kappa_int).
    Both arms of a DM pair have the SAME A (because v_B + w_B = v_A holds the
    trait weight (1-v)*V_s/2 fixed) and the same E, hence
        r(a) = r(b)  <=>  Bv_a*kappa(.90) = Bv_b*kappa(.98) + C_b*kappa_int
    which, dividing by V_s, is the registration's second constraint.  EXACT, not
    a linearization."""
    m = k2b()
    k2a = m.k2a()
    sizes = m.retained_cell_sizes()
    den = 0.0
    num_phi = {PHI_A: 0.0, PHI_B: 0.0}
    num_int = 0.0
    rows: list[dict[str, Any]] = []
    for key, n_cell in sorted(sizes.items()):
        mm = int(key.split("|m")[1])
        kap = 1.0 - 1.0 / n_cell
        den += n_cell * kap
        v90 = float(k2a.ar_set_var(np.arange(mm), PHI_A))
        v98 = float(k2a.ar_set_var(np.arange(mm), PHI_B))
        num_phi[PHI_A] += n_cell * kap * v90
        num_phi[PHI_B] += n_cell * kap * v98
        num_int += n_cell * kap * (1.0 / mm)
        rows.append({"cell": key, "n_cell": int(n_cell), "m": mm, "kap": kap,
                     "ar_set_var_phi90": v90, "ar_set_var_phi98": v98,
                     "one_over_m": 1.0 / mm})
    k90 = num_phi[PHI_A] / den
    k98 = num_phi[PHI_B] / den
    kint = num_int / den
    return {
        "kappa_phi_090": k90, "kappa_phi_098": k98, "kappa_int": kint,
        "kap_weight_total": den,
        "ordering_kint_lt_k90_lt_k98": bool(kint < k90 < k98),
        "ratio_k98_over_k90": k98 / k90,
        "ratio_k90_over_kint": k90 / kint,
        "cells": rows,
        "derivation": (
            "kappa(phi) = sum_cell n*kap*ar_set_var(arange(m), phi) / sum_cell n*kap; "
            "kappa_int = sum_cell n*kap*(1/m) / sum_cell n*kap; both read out of "
            "k2b:533-584 unchanged.  The double match is EXACT because matching the "
            "person total forces the trait weight A -- hence the attenuation "
            "numerator -- to be identical across the pair."),
    }


def solve_dm_pair(pair_id: str, target: float, kap: dict[str, Any]) -> dict[str, Any]:
    """DM-<t>: arm a slow-only (v_A solved for `target` at phi .90, w_int 0) vs
    arm b the DOUBLE-MATCHED recombination (v_B slow at phi .98 + w_B
    interaction), by the registration's closed form."""
    kd = k2d()
    a = kd.solve_slow_for_target(target, PHI_A)
    v_a = a["share"]
    k90, k98, kint = kap["kappa_phi_090"], kap["kappa_phi_098"], kap["kappa_int"]
    v_b = v_a * (k90 - kint) / (k98 - kint)
    w_b = v_a - v_b
    if not (0.0 < v_b < v_a and w_b > 0.0):
        raise SystemExit(
            f"REFUSED: the closed form did not return positive interior shares "
            f"for {pair_id}: v_A={v_a!r}, v_B={v_b!r}, w_B={w_b!r}")
    r_a = a["attenuation"]
    r_b = kd.predicted_attenuation(v_b, w_b, PHI_B)
    pv_a = person_share_design(v_a, 0.0)
    pv_b = person_share_design(v_b, w_b)
    d_att = r_a - r_b
    d_pv = pv_a - pv_b
    m = k2b()
    equal_share_bound = (1.0 - v_b) / 3.0        # K2a's validated w_int ceiling
    return {
        "pair": pair_id, "kind": "double_matched", "target_attenuation": float(target),
        "arm_a": {"arm": f"{pair_id.replace('-', '')}a", "share": v_a, "int_share": 0.0,
                  "phi": PHI_A, "predicted_attenuation": r_a,
                  "predicted_person_share": pv_a,
                  "bisection_iterations": a["bisection_iterations"],
                  "bracket_width_final": a["bracket_width_final"]},
        "arm_b": {"arm": f"{pair_id.replace('-', '')}b", "share": v_b, "int_share": w_b,
                  "phi": PHI_B, "predicted_attenuation": r_b,
                  "predicted_person_share": pv_b,
                  "bisection_iterations": 0, "bracket_width_final": 0.0},
        "closed_form": {
            "v_A": v_a, "v_B": v_b, "w_B": w_b,
            "v_B_formula": "v_A*(kappa(.90) - kappa_int)/(kappa(.98) - kappa_int)",
            "sum_residual_vB_plus_wB_minus_vA": (v_b + w_b) - v_a,
            "linear_constraint_residual": (v_b * kap["kappa_phi_098"]
                                           + w_b * kap["kappa_int"]
                                           - v_a * kap["kappa_phi_090"]),
        },
        "w_int_variance_share_design_b": m.arm_shares(v_b, f"int:{w_b!r}")["int"],
        "w_int_signal_fraction_b": w_b,
        "k2a_equal_share_bound_at_v_B": equal_share_bound,
        "w_int_inside_k2a_validated_range": bool(w_b <= equal_share_bound),
        "predicted_attenuation_difference": d_att,
        "abs_predicted_attenuation_difference": abs(d_att),
        "predicted_person_share_difference": d_pv,
        "abs_predicted_person_share_difference": abs(d_pv),
        "matched_attenuation_part0": bool(abs(d_att) <= MATCH_TOL_PART0),
        "matched_person_part0": bool(abs(d_pv) <= MATCH_TOL_PART0),
        "matched_part0": bool(abs(d_att) <= MATCH_TOL_PART0
                              and abs(d_pv) <= MATCH_TOL_PART0),
        "arm_a_abs_error_vs_target": a["abs_error_vs_target"],
        "sign_convention": ("D = field(slow-only phi .90 arm) - field(double-matched "
                            "recombination arm); the H-SPECIES signature is POSITIVE D"),
    }


def vs_phi_enumeration() -> list[dict[str, Any]]:
    """RN-2's disclosure: the registration says the VS pair is 'slow-only both
    arms, attenuation-matched at ~0.62, Delta V_person MAXIMIZED within
    phi in {.90, .98}'.  There are four ordered assignments; enumerate them all
    (pure card algebra, no world, no field number)."""
    kd = k2d()
    rows: list[dict[str, Any]] = []
    for phi_a in (PHI_A, PHI_B):
        for phi_b in (PHI_A, PHI_B):
            a = kd.solve_slow_for_target(VS_TARGET, phi_a)
            b = kd.solve_slow_for_target(a["attenuation"], phi_b)
            pv_a = person_share_design(a["share"], 0.0)
            pv_b = person_share_design(b["share"], 0.0)
            rows.append({
                "phi_a": phi_a, "phi_b": phi_b,
                "share_a": a["share"], "share_b": b["share"],
                "r_a": a["attenuation"], "r_b": b["attenuation"],
                "abs_predicted_attenuation_difference":
                    abs(a["attenuation"] - b["attenuation"]),
                "person_share_a": pv_a, "person_share_b": pv_b,
                "delta_person_share": pv_a - pv_b,
                "abs_delta_person_share": abs(pv_a - pv_b),
            })
    return rows


def solve_vs_pair(kap: dict[str, Any]) -> dict[str, Any]:
    """VS-62: a FRESH K2c-type pair -- slow-only both arms, attenuation-matched at
    ~0.62, Delta V_person maximized within phi in {.90, .98} (RN-2: the maximum
    of |Delta V| is attained by the two mixed-phi assignments; the SIGNED
    maximum with the leg's D = field(a) - field(b) convention, and continuity
    with K2c/K2d where arm a is always the phi .90 arm, selects phi_a = .90)."""
    kd = k2d()
    a = kd.solve_slow_for_target(VS_TARGET, PHI_A)
    b = kd.solve_slow_for_target(a["attenuation"], PHI_B)
    pv_a = person_share_design(a["share"], 0.0)
    pv_b = person_share_design(b["share"], 0.0)
    d_att = a["attenuation"] - b["attenuation"]
    d_pv = pv_a - pv_b
    del kap
    return {
        "pair": VS_PAIR, "kind": "variance_contrast",
        "target_attenuation": float(VS_TARGET),
        "arm_a": {"arm": "VS62a", "share": a["share"], "int_share": 0.0, "phi": PHI_A,
                  "predicted_attenuation": a["attenuation"],
                  "predicted_person_share": pv_a,
                  "bisection_iterations": a["bisection_iterations"],
                  "bracket_width_final": a["bracket_width_final"]},
        "arm_b": {"arm": "VS62b", "share": b["share"], "int_share": 0.0, "phi": PHI_B,
                  "predicted_attenuation": b["attenuation"],
                  "predicted_person_share": pv_b,
                  "bisection_iterations": b["bisection_iterations"],
                  "bracket_width_final": b["bracket_width_final"]},
        "predicted_attenuation_difference": d_att,
        "abs_predicted_attenuation_difference": abs(d_att),
        "predicted_person_share_difference": d_pv,
        "abs_predicted_person_share_difference": abs(d_pv),
        "matched_attenuation_part0": bool(abs(d_att) <= MATCH_TOL_PART0),
        "matched_person_part0": None,     # RN-3: NOT a matched-V pair BY DESIGN
        "matched_part0": bool(abs(d_att) <= MATCH_TOL_PART0),
        "arm_a_abs_error_vs_target": a["abs_error_vs_target"],
        "sign_convention": "D = field(phi .90 arm) - field(phi .98 arm)",
        "phi_enumeration": vs_phi_enumeration(),
    }


# ---------------------------------------------------------------------------
# The rule-16 adjudication object: cells -> lean predicates -> L-VS -> routing,
# enumerated as ONE truth table.

CELL_ORDER = ("MAT-SIG(+)", "MAT-SIG(-)", "SUB-SIG(+)", "SUB-SIG(-)",
              "NULL", "WEAK-NULL", "INDET")
POS_CELLS = ("MAT-SIG(+)", "SUB-SIG(+)")
NEG_CELLS = ("MAT-SIG(-)", "SUB-SIG(-)")
BOUNDED_CELLS = ("NULL", "WEAK-NULL")
SIG_CELLS = POS_CELLS + NEG_CELLS
# registration: "ties broken in that order, L-NEG > L-SPEC by the written
# precedence.  Precedence is part of the registration."
LEAN_PRECEDENCE = ("L-NEG", "L-SPEC", "L-VAR", "L-UND")
LEAN_PRIORS = {"L-VAR": 0.60, "L-SPEC": 0.30, "L-NEG": 0.05, "L-UND": 0.05}
L_VS_PRIOR = 0.70


def clause_vector(point: float, lo: float, hi: float) -> dict[str, bool]:
    return k2d().clause_vector(point, lo, hi, M1, M2)


def assign_cell(point: float, lo: float, hi: float) -> str:
    return k2d().assign_cell(point, lo, hi, M1, M2)


def lean_predicates_true(cell_a: str, cell_b: str) -> list[str]:
    """The registration's four lean predicates, applied LITERALLY (no precedence
    applied here -- this returns EVERY predicate whose clause is true, so the
    enumeration can look for overlaps).

      L-VAR  := both DM in {NULL, WEAK-NULL}
      L-SPEC := >=1 DM in {MAT-SIG(+), SUB-SIG(+)} and no DM in a negative cell
      L-NEG  := >=1 DM in {MAT-SIG(-), SUB-SIG(-)}
      L-UND  := any other combination
    """
    cells = (cell_a, cell_b)
    out: list[str] = []
    if all(c in BOUNDED_CELLS for c in cells):
        out.append("L-VAR")
    if any(c in POS_CELLS for c in cells) and not any(c in NEG_CELLS for c in cells):
        out.append("L-SPEC")
    if any(c in NEG_CELLS for c in cells):
        out.append("L-NEG")
    if not out:
        out.append("L-UND")            # "any other combination"
    return out


def lean_of(cell_a: str, cell_b: str) -> str:
    """Apply the registered precedence L-NEG > L-SPEC > L-VAR > L-UND."""
    trues = lean_predicates_true(cell_a, cell_b)
    for name in LEAN_PRECEDENCE:
        if name in trues:
            return name
    raise SystemExit(f"REFUSED: no lean predicate fired for ({cell_a}, {cell_b})")


def route(lean: str, l_vs_holds: bool) -> str:
    """The registration's routing table, every (L-., L-VS) combination assigned."""
    if lean == "L-VAR":
        return "P-VAR" if l_vs_holds else "P-VAR-WEAK"
    if lean == "L-SPEC":
        return "P-SPEC"
    if lean == "L-NEG":
        return "P-NEG"
    if lean == "L-UND":
        return "P-UND"
    raise SystemExit(f"REFUSED: unroutable lean {lean!r}")


def enumerate_full_object() -> dict[str, Any]:
    """RULE 16, the leg's defining method obligation: the enumeration extends
    over the FULL adjudication object -- cells, lean predicates AND routing --
    as one truth table, with every realizable combination routed to exactly one
    outcome.

    Layer 1: the per-pair CELL table is a partition (k2d's own enumeration,
             called unmodified: a dense numeric search over (point, lo, hi)
             triples against a 6-clause truth table).
    Layer 2: the four lean predicates over all 7x7 = 49 ordered DM-cell pairs --
             every combination fires EXACTLY ONE predicate (checked before
             precedence is applied, so a nonzero overlap count would be a
             registration defect, not something precedence hides).
    Layer 3: the 49 x 2 = 98 (DM-cell-pair, L-VS) combinations, each routed to
             exactly one P-outcome.
    Also checked: the registration's own gloss that L-UND == "at least one INDET
    and no significant cell"."""
    cell_space = k2d().enumerate_cell_space()

    lean_rows: list[dict[str, Any]] = []
    lean_overlap: list[list[str]] = []
    lean_gap: list[list[str]] = []
    gloss_mismatch: list[list[str]] = []
    for ca in CELL_ORDER:
        for cb in CELL_ORDER:
            trues = lean_predicates_true(ca, cb)
            # the registration's stated characterization of the remainder
            gloss_und = bool(any(c == "INDET" for c in (ca, cb))
                             and not any(c in SIG_CELLS for c in (ca, cb)))
            fired_und = bool(trues == ["L-UND"])
            if gloss_und != fired_und:
                gloss_mismatch.append([ca, cb])
            lean_rows.append({"DM-68": ca, "DM-56": cb, "predicates_true": trues,
                              "n": len(trues), "lean_after_precedence": lean_of(ca, cb),
                              "registration_gloss_L_UND": gloss_und})
            if len(trues) > 1:
                lean_overlap.append([ca, cb])
            if not trues:
                lean_gap.append([ca, cb])

    route_rows: list[dict[str, Any]] = []
    route_gap: list[Any] = []
    outcomes_seen: dict[str, int] = {}
    for row in lean_rows:
        for l_vs in (True, False):
            try:
                out = route(row["lean_after_precedence"], l_vs)
            except SystemExit:
                out = None
            if out is None:
                route_gap.append([row["DM-68"], row["DM-56"], l_vs])
                continue
            outcomes_seen[out] = outcomes_seen.get(out, 0) + 1
            route_rows.append({"DM-68": row["DM-68"], "DM-56": row["DM-56"],
                               "lean": row["lean_after_precedence"],
                               "L-VS": "hold" if l_vs else "miss", "outcome": out})

    leans_seen = sorted({r["lean_after_precedence"] for r in lean_rows})
    return {
        "criterion": (
            "RULE 16: (1) the per-pair cell table is a verified partition; (2) the four "
            "lean predicates partition all 49 ordered DM-cell pairs -- EXACTLY ONE fires "
            "per combination, checked BEFORE precedence; (3) all 98 (cell-pair, L-VS) "
            "combinations route to exactly one named P-outcome; (4) the registration's "
            "own gloss for L-UND agrees with the remainder on all 49"),
        "layer1_cell_space": cell_space,
        "layer2_lean_space": {
            "n_combinations": len(lean_rows),
            "n_unique": sum(1 for r in lean_rows if r["n"] == 1),
            "n_overlap": len(lean_overlap), "overlap_combinations": lean_overlap,
            "n_gap": len(lean_gap), "gap_combinations": lean_gap,
            "leans_realized": leans_seen,
            "all_four_leans_realized": bool(set(leans_seen) == set(LEAN_PRECEDENCE)),
            "lean_counts": {lname: sum(1 for r in lean_rows
                                       if r["lean_after_precedence"] == lname)
                            for lname in LEAN_PRECEDENCE},
            "registration_gloss_L_UND_mismatches": gloss_mismatch,
            "rows": lean_rows,
            "PASS": bool(not lean_overlap and not lean_gap and not gloss_mismatch
                         and set(leans_seen) == set(LEAN_PRECEDENCE)),
        },
        "layer3_routing_space": {
            "n_combinations": len(lean_rows) * 2,
            "n_routed": len(route_rows), "n_gap": len(route_gap),
            "gap_combinations": route_gap,
            "outcomes_realized": sorted(outcomes_seen),
            "outcome_counts": outcomes_seen,
            "all_five_outcomes_realized": bool(
                set(outcomes_seen) == {"P-VAR", "P-VAR-WEAK", "P-SPEC", "P-NEG", "P-UND"}),
            "rows": route_rows,
            "PASS": bool(not route_gap and len(route_rows) == len(lean_rows) * 2
                         and set(outcomes_seen) == {"P-VAR", "P-VAR-WEAK", "P-SPEC",
                                                    "P-NEG", "P-UND"}),
        },
        "PASS": bool(cell_space["PASS"]),
    }


# ---------------------------------------------------------------------------
# G0e: the anchors, re-derived bit-exactly from persisted artifacts.

def rederive_anchors() -> dict[str, Any]:
    """K2d's rederive_anchors (K2b's A1/A4 + lambda, K2c's three D_k with CIs and
    the pooled q) called UNMODIFIED, plus K2e's own additions: K2d's three D_k
    with CIs and cells, K2d's 19-arm q-update, and the kappa_hat / R2 /
    max-residual of the six-pair companion re-fit from scratch."""
    kd = k2d()
    m = k2b()
    k2a = m.k2a()
    out: dict[str, Any] = kd.rederive_anchors()

    k2b_field = out.pop("_k2b_field")
    out.pop("_k2b_pred_att")
    k2c_field = out.pop("_k2c_field")
    out.pop("_k2c_mixed")
    k2c_x = out.pop("_k2c_x")
    k2c_order = out.pop("_k2c_order")

    # --- K2d's three D_k, their CIs, and their assigned CELLS
    k2d_dec = json.loads((K2D_OUT / "decision.json").read_text(encoding="utf-8"))
    k2d_arms_spec = json.loads((K2D_OUT / "part0_arms.json").read_text(encoding="utf-8"))
    n_d = int(max(k2d_dec["worlds_selected_by_pair"].values()))
    order_d = tuple(a["arm"] for a in k2d_arms_spec["arms"])
    k2d_field = {
        a: pd.concat([read_csv_rt(p) for p in sorted(K2D_OUT.glob(f"arm_{a}_field_w*.csv"))],
                     ignore_index=True).sort_values("world")["recovery_b_only"].to_numpy(float)
        for a in order_d}
    pick_d = np.random.default_rng(K2D_MASTER_SEED).integers(0, n_d, size=(B_BOOT, n_d))
    boot_d = {a: k2d_field[a][pick_d].mean(axis=1) for a in order_d}
    d_rows: list[dict[str, Any]] = []
    for pr in k2d_arms_spec["pairs"]:
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        d = k2d_field[ida] - k2d_field[idb]
        lo, hi = k2a.ci_of(boot_d[ida] - boot_d[idb])
        persisted = next(r for r in k2d_dec["pair_differences"] if r["pair"] == pr["pair"])
        cell_re = assign_cell(float(np.mean(d)), lo, hi)
        d_rows.append({
            "pair": pr["pair"],
            "persisted_D": persisted["D"], "rederived_D": float(np.mean(d)),
            "residual_D": float(np.mean(d)) - persisted["D"],
            "persisted_ci": persisted["ci"], "rederived_ci": [lo, hi],
            "residual_ci": [lo - persisted["ci"][0], hi - persisted["ci"][1]],
            "persisted_cell": persisted["CELL"], "rederived_cell": cell_re,
            "bit_exact": bool(float(np.mean(d)) == persisted["D"]
                              and lo == persisted["ci"][0] and hi == persisted["ci"][1]
                              and cell_re == persisted["CELL"]),
        })

    # --- K2d's 19-arm q-update, through the SAME generalized pooled_q
    k2d_preds = read_csv_rt(K2D_OUT / "part0_predictions.csv").set_index("arm")
    x_d = np.log(np.array([float(k2d_preds.loc[a, "r_card_b_pred_raw"]) for a in order_d]))
    groups19 = [(k2c_x[:6], [k2b_field[a] for a in K2B_PRIMARY_ARMS]),
                (k2c_x[6:], [k2c_field[a] for a in k2c_order]),
                (x_d, [k2d_field[a] for a in order_d])]
    q19 = kd.pooled_q(groups19, K2B_LAMBDA, B_BOOT, K2D_MASTER_SEED)
    q19.pop("q_boot")
    q19_persisted = k2d_dec["leans"]["q_update"]

    # --- the kappa_hat companion, re-fit from scratch over the six K2c+K2d pairs
    post_hoc = json.loads((K2D_OUT / "post_hoc_descriptive.json").read_text(encoding="utf-8"))
    k2c_arms_spec = json.loads((K2C_OUT / "part0_arms.json").read_text(encoding="utf-8"))
    spec_by_arm = {a["arm"]: a for a in k2c_arms_spec["arms"]}
    spec_by_arm.update({a["arm"]: a for a in k2d_arms_spec["arms"]})
    six = [("K2c", "P1", "P1a", "P1b"), ("K2c", "P2", "P2a", "P2b"),
           ("K2c", "P3", "P3a", "P3b"), ("K2d", "FR-45", "FR45a", "FR45b"),
           ("K2d", "SP-68", "SP68slow", "SP68int"),
           ("K2d", "SP-56", "SP56slow", "SP56int")]
    kap_rows: list[dict[str, Any]] = []
    xs, ys = [], []
    for leg, pid, ida, idb in six:
        sa, sb = spec_by_arm[ida], spec_by_arm[idb]
        pv_a = person_share_design(sa["share"], float(sa.get("int_share", 0.0)))
        pv_b = person_share_design(sb["share"], float(sb.get("int_share", 0.0)))
        persisted = next(r for r in post_hoc["rows"] if r["pair"] == pid)
        xs.append(pv_a - pv_b)
        ys.append(persisted["D"])
        kap_rows.append({
            "leg": leg, "pair": pid,
            "person_var_a_rederived": pv_a, "person_var_a_persisted": persisted["person_var_a"],
            "person_var_b_rederived": pv_b, "person_var_b_persisted": persisted["person_var_b"],
            "dvar_rederived": pv_a - pv_b, "dvar_persisted": persisted["dvar"],
            "D": persisted["D"],
            "bit_exact": bool(pv_a == persisted["person_var_a"]
                              and pv_b == persisted["person_var_b"]
                              and (pv_a - pv_b) == persisted["dvar"]),
        })
    x = np.array(xs, dtype=float)
    y = np.array(ys, dtype=float)
    kappa_re = float((x @ y) / (x @ x))
    resid = y - kappa_re * x
    r2_re = float(1.0 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean())))
    maxres_re = float(np.max(np.abs(resid)))

    out["k2d"] = {
        "worlds_per_arm": n_d, "arms": list(order_d),
        "pair_differences": d_rows,
        "all_D_bit_exact": bool(all(r["bit_exact"] for r in d_rows)),
        "cells_persisted": k2d_dec["cells"],
        "q19_persisted": q19_persisted["q"], "q19_rederived": q19["q"],
        "q19_residual": q19["q"] - q19_persisted["q"],
        "q19_ci_persisted": q19_persisted["q_ci"], "q19_ci_rederived": q19["q_ci"],
        "q19_ci_residual": [q19["q_ci"][0] - q19_persisted["q_ci"][0],
                            q19["q_ci"][1] - q19_persisted["q_ci"][1]],
        "q19_bit_exact": bool(q19["q"] == q19_persisted["q"]
                              and q19["q_ci"][0] == q19_persisted["q_ci"][0]
                              and q19["q_ci"][1] == q19_persisted["q_ci"][1]),
        "q19_r2_persisted": q19_persisted["r2"], "q19_r2_rederived": q19["r2"],
        "route": ("round-trip re-read of results/m4_k2d_frontier_carrier/"
                  "arm_*_field_w*.csv and part0_predictions.csv; K2d's own picks "
                  "(default_rng(20260818).integers(0,32,(2000,32))) and its own "
                  "generalized pooled_q, called unmodified"),
    }
    out["kappa_companion"] = {
        "rows": kap_rows,
        "all_person_var_bit_exact": bool(all(r["bit_exact"] for r in kap_rows)),
        "kappa_persisted": post_hoc["kappa_ols_through_origin"],
        "kappa_rederived": kappa_re,
        "kappa_residual": kappa_re - post_hoc["kappa_ols_through_origin"],
        "kappa_constant_in_script": KAPPA_HAT,
        "kappa_constant_matches": bool(kappa_re == KAPPA_HAT),
        "r2_persisted": post_hoc["r2_vs_mean"], "r2_rederived": r2_re,
        "r2_bit_exact": bool(r2_re == post_hoc["r2_vs_mean"]),
        "max_abs_residual_persisted": post_hoc["max_abs_residual"],
        "max_abs_residual_rederived": maxres_re,
        "max_abs_residual_bit_exact": bool(maxres_re == post_hoc["max_abs_residual"]),
        "per_pair_kappa": [float(yy / xx) for xx, yy in zip(x, y)],
        "route": ("V_person re-derived from the two legs' own part0_arms.json shares "
                  "through k2b.arm_shares (the currency kappa was fitted in); D read "
                  "from post_hoc_descriptive.json; OLS through the origin re-fit"),
    }
    out["_k2b_field"] = k2b_field
    out["_k2c_field"] = k2c_field
    out["_k2c_x"] = k2c_x
    out["_k2c_order"] = k2c_order
    out["_k2d_field"] = k2d_field
    out["_k2d_x"] = x_d
    out["_k2d_order"] = order_d
    out["_kappa_x"] = x
    out["_kappa_y"] = y
    out["_kappa_pairs"] = [(leg, pid) for leg, pid, _, _ in six]
    out["all_bit_exact"] = bool(
        out["all_bit_exact"] and out["k2d"]["all_D_bit_exact"]
        and out["k2d"]["q19_bit_exact"] and out["kappa_companion"]["all_person_var_bit_exact"]
        and out["kappa_companion"]["kappa_constant_matches"]
        and out["kappa_companion"]["r2_bit_exact"]
        and out["kappa_companion"]["max_abs_residual_bit_exact"])
    return out


# ---------------------------------------------------------------------------
# Stage: part0

def arms_spec() -> list[dict[str, Any]]:
    path = OUT / "part0_arms.json"
    if not path.exists():
        raise SystemExit("REFUSED: results/m4_k2e_double_matching/part0_arms.json missing.")
    return json.loads(path.read_text(encoding="utf-8"))["arms"]


def pairs_spec() -> list[dict[str, Any]]:
    return json.loads((OUT / "part0_arms.json").read_text(encoding="utf-8"))["pairs"]


def run_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    kd = k2d()
    kd.install_species_weights()
    m = k2b()
    lay = m.layout()
    gates: dict[str, Any] = {
        "leg": "M4-K2e",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "pilot_worlds": list(PILOT_WORLDS),
        "worlds_per_arm_registered": WORLDS_PER_ARM,
        "margins": {"M1": M1, "M2": M2},
        "kappa_hat_registered": KAPPA_HAT,
        "l_vs_tolerance": L_VS_TOL,
        "noise_share": m.NOISE_SHARE,
        "signal_share": m.SIGNAL_SHARE,
        "rule14_self_check": (
            "NO GATE AND NO BRANCH LEAN IN THIS LEG COMPARES QUANTITIES ACROSS SCALES "
            "WITHOUT A REGISTRATION-PINNED LINK. G0e re-derives K2b/K2c/K2d numbers "
            "against themselves; G1e compares card attenuation to card attenuation and "
            "variance share to variance share; G2e/G4e, every cell, and L-VAR/L-SPEC/"
            "L-NEG/L-UND compare field agreement to field agreement (within-pair, same "
            "instrument, same units). L-VS DOES compare a field difference to a "
            "design-variance quantity -- and satisfies rule 14 by its FIRST clause: the "
            "registration PINS the link function and its coefficient explicitly "
            "(D_VS_pred = -0.7220359963712748 x Delta V_person), so the link is part of "
            "the lean, not an executor choice. The only unpinned cross-scale object is "
            "the q-update, which the registration declares DESCRIPTIVE with NO GATE and "
            "which pins its own link (a log-log power law whose exponent q IS the "
            "estimand)."
        ),
        "rule12_source_objects": {
            "interaction shock stream S(o)": "k2a:174-181 shock_int_matrix, salt m4k2a-shock-int",
            "person loadings a_i": "k2b:338-341 a_load, salt m4k2b-loading",
            "u_int": "k2b:342-343", "s_int": "k2b:344",
            "panel emission of int": "k2b:374-375",
            "card centring of int": "k2b:416, 425-426",
            "attenuation algebra entry C/m, C/half": "k2b:537, 549, 559, 562",
            "slow AR(phi) latent": "k2b:333-337 xs, f2:173-176 form",
            "kappa(phi) / kappa_int": "this script kappa_coefficients(), read out of k2b:533-584",
            "arm weight generalization": "k2d:206-238 install_species_weights (unmodified)",
            "realized variance shares": ("k2b:698-703, factored into this script's "
                                         "realized_person_shares() so it runs on every world"),
        },
        "pilot_convention_RN4": {
            "chosen": "4-world pilot per pair (the registration's primary option)",
            "why": ("K2d anomaly A-5 -- which bought this convention -- showed a 2-world "
                    "pilot estimating the paired sd on ONE degree of freedom and "
                    "underestimating the realized sd by 2.05x-7.83x. Four worlds give "
                    "3 df at a cost of 12 extra arm-worlds."),
            "df": len(PILOT_WORLDS) - 1,
            "chi2_90_inflation_factor_disclosed": chi2_inflation(len(PILOT_WORLDS) - 1)[0],
            "chi2_90_inflation_at_df1_for_reference": chi2_inflation(1)[0],
            "chi2_scipy_crosscheck": [chi2_inflation(1)[1],
                                      chi2_inflation(len(PILOT_WORLDS) - 1)[1]],
            "gate": "the plain 4-world MDE, as registered; the inflated value is DISCLOSED only",
        },
    }

    # ---- step 1: kappa coefficients + the SOLVED shares (pure algebra)
    t_shares = time.time()
    kap = kappa_coefficients()
    if not kap["ordering_kint_lt_k90_lt_k98"]:
        raise SystemExit("REFUSED: kappa_int < kappa(.90) < kappa(.98) does not hold; "
                         "the registration's solvability argument fails on this panel.")
    pairs = [solve_dm_pair(pid, tgt, kap) for pid, tgt in DM_TARGETS] + [solve_vs_pair(kap)]
    arms: list[dict[str, Any]] = []
    for pr in pairs:
        for side in ("arm_a", "arm_b"):
            spec = pr[side]
            w_int_arm = "zero" if spec["int_share"] == 0.0 else f"int:{spec['int_share']!r}"
            arms.append({"arm": spec["arm"], "pair": pr["pair"], "side": side[-1],
                         "kind": pr["kind"], "share": spec["share"],
                         "int_share": spec["int_share"], "phi": spec["phi"],
                         "w_int_arm": w_int_arm,
                         "target_attenuation": pr["target_attenuation"]})
    shares_seconds = time.time() - t_shares

    pred_rows = []
    for a in arms:
        pred = m.arm_predictions(a["share"], a["phi"], a["w_int_arm"])
        pred_rows.append({"arm": a["arm"], "pair": a["pair"], "side": a["side"],
                          "kind": a["kind"], "int_share": a["int_share"],
                          "target_attenuation": a["target_attenuation"],
                          "person_share_design": person_share_design(a["share"],
                                                                     a["int_share"]),
                          **pred})
    preds = pd.DataFrame(pred_rows)
    preds.to_csv(OUT / "part0_predictions.csv", index=False)
    pd.DataFrame(kap["cells"]).to_csv(OUT / "part0_kappa_cells.csv", index=False)
    pd.DataFrame(pairs[-1]["phi_enumeration"]).to_csv(
        OUT / "part0_vs_phi_enumeration.csv", index=False)

    # ---- G0e: anchors, bit-exact
    anchors = rederive_anchors()
    k2b_field = anchors.pop("_k2b_field")
    k2c_field = anchors.pop("_k2c_field")
    k2c_x = anchors.pop("_k2c_x")
    k2c_order = anchors.pop("_k2c_order")
    k2d_field = anchors.pop("_k2d_field")
    k2d_x = anchors.pop("_k2d_x")
    k2d_order = anchors.pop("_k2d_order")
    anchors.pop("_kappa_x")
    anchors.pop("_kappa_y")
    anchors.pop("_kappa_pairs")
    anchors["criterion"] = (
        "K2d's three D and their CIs and CELLS, K2d's 19-arm q-update and its CI, the "
        "six-pair kappa companion (kappa, R2, max |residual|, every person-variance "
        "column), K2c's three D_k and CIs, K2c's pooled q and CI, lambda, and K2b's "
        "A1/A4 field recoveries all re-derived from persisted artifacts (round-trip "
        "parsed) EQUAL bit-exactly")
    anchors["weights_dispatcher"] = kd.verify_species_weights()
    anchors["pass"] = bool(anchors["all_bit_exact"]
                           and anchors["weights_dispatcher"]["zero_arm_bit_exact_after_patch"]
                           and anchors["weights_dispatcher"]["int_zero_route_equals_zero_arm_bit_exact"])
    anchors["panel"] = {
        "authors_per_world": int(len(lay["author_ids"])),
        "retained_authors": int(len(lay["retained_idx"])),
        "events_total": int(lay["counts"].sum()),
        "m_multiset": {int(k): int(v) for k, v in
                       sorted(pd.Series(lay["counts"]).value_counts().items())},
        "contexts": sorted(set(lay["contexts"])),
    }
    gates["G0e"] = anchors

    # ---- G1e (Part-0 half): the DOUBLE designed identity
    dm_pairs = [p for p in pairs if p["kind"] == "double_matched"]
    g1: dict[str, Any] = {
        "kappa_coefficients": {k: v for k, v in kap.items() if k != "cells"},
        "pairs": pairs,
        "tolerance_part0": MATCH_TOL_PART0,
        "tolerance_measured_attenuation": MATCH_TOL_MEASURED,
        "tolerance_measured_person_share": VPERSON_TOL_MEASURED,
        "max_abs_predicted_attenuation_difference": float(
            max(p["abs_predicted_attenuation_difference"] for p in pairs)),
        "max_abs_predicted_person_difference_DM": float(
            max(p["abs_predicted_person_share_difference"] for p in dm_pairs)),
        "criterion_part0": (
            "per DM pair BOTH residuals <= 1e-12: |Delta predicted attenuation| and "
            "|Delta predicted V_person share|; the VS pair carries the attenuation "
            "clause only (RN-3: its Delta V_person is MAXIMIZED by design, so the "
            "person clause is inapplicable to it and applying it would void the pair "
            "the registration built)"),
        "criterion_post_arms": (
            "per pair, measured within-pair card-attenuation difference 95% CI inside "
            "+/-0.005; per DM pair, realized V_person share difference inside +/-0.005 "
            "(point, as written; its CI reported alongside). A pair failing either "
            "applicable clause is VOID"),
        "part0_pass": bool(all(p["matched_attenuation_part0"] for p in pairs)
                           and all(p["matched_person_part0"] for p in dm_pairs)),
    }
    g1["pass"] = g1["part0_pass"]
    gates["G1e"] = g1

    # ---- the REGISTERED VS prediction (rule 9: both currencies, primary named)
    vs = pairs[-1]
    dv_design = vs["predicted_person_share_difference"]
    gates["VS_prediction"] = {
        "pair": VS_PAIR,
        "kappa_hat": KAPPA_HAT,
        "primary_currency_RN1": (
            "DESIGN V_person share via k2b.arm_shares -- the EXACT currency kappa_hat "
            "was fitted in (G0e re-derives all six fitted person-variance columns "
            "bit-exactly in it). PRIMARY."),
        "secondary_currency_RN1": (
            "pilot-EMPIRICALLY-realized V_person share (mean over the 4 reserved pilot "
            "worlds), reported as the second reading required by rule 9."),
        "delta_person_design": dv_design,
        "D_VS_pred_design": KAPPA_HAT * dv_design,
        "clause": ("L-VS holds iff the measured D_VS CI CONTAINS the predicted value AND "
                   "|D_VS - pred| <= 0.010"),
        "tolerance": L_VS_TOL,
        "prior": L_VS_PRIOR,
    }

    # ---- the rule-16 FULL-OBJECT enumeration (before any hypothesis number)
    enum = enumerate_full_object()
    gates["rule16_enumeration"] = enum

    # ---- pilot: both channels, all 6 arms, on the RESERVED worlds
    t_pilot = time.time()
    build_times: list[float] = []
    pilot_worlds: dict[tuple[int, float], Any] = {}
    phis = sorted({a["phi"] for a in arms})
    for w_idx in PILOT_WORLDS:
        for phi in phis:
            tb = time.time()
            pilot_worlds[(w_idx, phi)] = m.build_k2b_world(world_seed_for(w_idx), phi)
            build_times.append(time.time() - tb)
    pilot_card: dict[str, pd.DataFrame] = {}
    pilot_field: dict[str, list[dict[str, Any]]] = {}
    pilot_panels: dict[str, list[np.ndarray]] = {}
    realized: dict[str, dict[str, float]] = {}
    realized_all: dict[str, list[dict[str, float]]] = {}
    frame_residual_max = 0.0
    share_route_residual = 0.0
    for a in arms:
        w = m.arm_weights(a["share"], a["w_int_arm"])
        frames, rows = [], []
        realized_all[a["arm"]] = []
        for w_idx in PILOT_WORLDS:
            world = pilot_worlds[(w_idx, a["phi"])]
            frame, cres = m.card_channel_frame(world, w, world_seed_for(w_idx))
            frame_residual_max = max(frame_residual_max, cres)
            frames.append(frame)
            row = run_field_world(a["arm"], w_idx, world, w,
                                  verify=(w_idx == PILOT_WORLDS[0]))
            rs = realized_person_shares(world, w)
            realized_all[a["arm"]].append(rs)
            if "realized_shares" in row:
                share_route_residual = max(
                    share_route_residual,
                    max(abs(rs[k] - row["realized_shares"][k]) for k in rs))
            row = {k: v for k, v in row.items() if k != "realized_shares"}
            row.update({f"realized_{k}": v for k, v in rs.items()})
            row["realized_person"] = rs["slow"] + rs["int"]
            rows.append(row)
        pilot_card[a["arm"]] = pd.concat(frames, ignore_index=True)
        pilot_field[a["arm"]] = rows
        pilot_panels[a["arm"]] = m.emit_panel(pilot_worlds[(PILOT_WORLDS[0], a["phi"])], w)
        realized[a["arm"]] = realized_all[a["arm"]][0]
    pilot_seconds = time.time() - t_pilot
    pilot_work_seconds = pilot_seconds - float(np.sum(build_times))

    # the SECONDARY reading of the VS prediction (rule 9)
    pv_pilot = {aid: float(np.mean([r["slow"] + r["int"] for r in realized_all[aid]]))
                for aid in realized_all}
    dv_realized = pv_pilot[vs["arm_a"]["arm"]] - pv_pilot[vs["arm_b"]["arm"]]
    gates["VS_prediction"].update({
        "delta_person_pilot_realized": dv_realized,
        "D_VS_pred_pilot_realized": KAPPA_HAT * dv_realized,
        "design_minus_realized_delta": dv_design - dv_realized,
        "prediction_spread_between_readings": abs(KAPPA_HAT * dv_design
                                                  - KAPPA_HAT * dv_realized),
        "realized_person_share_pilot_by_arm": pv_pilot,
    })

    # ---- G4e: liveness (rule 3) + within-pair non-degeneracy (rule 10)
    g4: dict[str, Any] = {"within_pair": [], "across_pair": {}, "interaction_channel": [],
                          "no_gap_gate": (
                              "REGISTERED: no GAP-based clause gates anything in this leg "
                              "(K2d A-2's instrument boundary). GAP containment is "
                              "reported descriptively in finalize only.")}
    pilot_card_point = {}
    for a in arms:
        pt, _ = m.bootstrap_card(pilot_card[a["arm"]], 1, MASTER_SEED)
        pilot_card_point[a["arm"]] = {"gap": float(pt["gap"]),
                                      "attenuation": float(pt["r_card_b_raw"])}
    for pr in pairs:
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        pa, pb = pilot_panels[ida], pilot_panels[idb]
        rms = math.sqrt(float(np.mean(np.concatenate(
            [(pa[i] - pb[i]).ravel() for i in range(len(pa))]) ** 2)))
        g4["within_pair"].append({
            "pair": pr["pair"], "kind": pr["kind"], "rms_panel_change": rms,
            "slow_share_a": pr["arm_a"]["share"], "slow_share_b": pr["arm_b"]["share"],
            "int_share_a": pr["arm_a"]["int_share"], "int_share_b": pr["arm_b"]["int_share"],
            "phi_a": pr["arm_a"]["phi"], "phi_b": pr["arm_b"]["phi"],
            "realized_slow_a": realized[ida]["slow"], "realized_slow_b": realized[idb]["slow"],
            "realized_int_a": realized[ida]["int"], "realized_int_b": realized[idb]["int"],
            "realized_person_a": pv_pilot[ida], "realized_person_b": pv_pilot[idb],
            "realized_person_difference": pv_pilot[ida] - pv_pilot[idb],
            "pilot_field_a": float(np.mean([r["recovery_b_only"] for r in pilot_field[ida]])),
            "pilot_field_b": float(np.mean([r["recovery_b_only"] for r in pilot_field[idb]])),
            "non_degenerate": bool(rms > 1e-6),
        })
    for a in arms:
        g4["interaction_channel"].append({
            "arm": a["arm"], "design_int_fraction_of_signal": a["int_share"],
            "design_int_variance_share": m.arm_shares(a["share"], a["w_int_arm"])["int"],
            "realized_int_variance_share": realized[a["arm"]]["int"],
            "live": bool(realized[a["arm"]]["int"] > 0.0),
        })
    int_arms = [r for r in g4["interaction_channel"] if r["design_int_fraction_of_signal"] > 0.0]
    zero_arms = [r for r in g4["interaction_channel"] if r["design_int_fraction_of_signal"] == 0.0]
    g4["interaction_live_in_all_DM_b_arms"] = bool(all(r["live"] for r in int_arms))
    g4["n_int_arms"] = len(int_arms)
    g4["interaction_exactly_zero_in_zero_arms"] = bool(
        all(r["realized_int_variance_share"] == 0.0 for r in zero_arms))
    order = sorted(pairs, key=lambda p: p["target_attenuation"])
    card_levels, field_levels, labels = [], [], []
    for pr in order:
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        card_levels.append(0.5 * (pilot_card_point[ida]["attenuation"]
                                  + pilot_card_point[idb]["attenuation"]))
        field_levels.append(0.5 * (
            float(np.mean([r["recovery_b_only"] for r in pilot_field[ida]]))
            + float(np.mean([r["recovery_b_only"] for r in pilot_field[idb]]))))
        labels.append(f"{pr['pair']}({pr['target_attenuation']:g})")
    g4["across_pair"] = {
        "levels_ascending_by_design": labels,
        "pilot_card_attenuation": card_levels,
        "pilot_field_recovery": field_levels,
        "card_strictly_increasing": bool(all(card_levels[i] < card_levels[i + 1]
                                             for i in range(len(card_levels) - 1))),
        "field_strictly_increasing": bool(all(field_levels[i] < field_levels[i + 1]
                                              for i in range(len(field_levels) - 1))),
    }
    g4["frame_channel_centred_residual_max"] = frame_residual_max
    g4["realized_share_route_residual_vs_k2b_verify"] = share_route_residual
    g4["realized_share_route_bit_exact"] = bool(share_route_residual == 0.0)
    g4["realized_share_dev_abs_max"] = float(max(
        max(abs(realized[a["arm"]][k] - m.arm_shares(a["share"], a["w_int_arm"])[k])
            for k in m.arm_shares(a["share"], a["w_int_arm"]))
        for a in arms))
    g4["criterion"] = (
        "the interaction channel's REALIZED variance share is > 0 in both DM-b arms and "
        "exactly 0 in the four w_int=0 arms; within every pair the emitted panels differ "
        "(RMS > 1e-6); across the three designed attenuation levels (.56 < .62 < .68) the "
        "pilot card attenuation AND pilot field recovery both move per prediction "
        "(strictly increasing); realized variance shares within 0.01 of design; and the "
        "new realized-share route is bit-exact against k2b's verify route")
    g4["pass"] = bool(g4["interaction_live_in_all_DM_b_arms"]
                      and g4["interaction_exactly_zero_in_zero_arms"]
                      and all(r["non_degenerate"] for r in g4["within_pair"])
                      and g4["across_pair"]["card_strictly_increasing"]
                      and g4["across_pair"]["field_strictly_increasing"]
                      and g4["realized_share_dev_abs_max"] <= 0.01
                      and g4["realized_share_route_bit_exact"])
    gates["G4e"] = g4

    # ---- G2e: power (rule 2), PER PAIR, on the 4-world pilot
    g2: dict[str, Any] = {"per_pair": [], "ladder": [], "target": MDE_TARGET,
                          "pilot_worlds": list(PILOT_WORLDS),
                          "convention": gates["pilot_convention_RN4"]}
    pilot_d: dict[str, np.ndarray] = {}
    for pr in pairs:
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        fa = np.array([r["recovery_b_only"] for r in pilot_field[ida]])
        fb = np.array([r["recovery_b_only"] for r in pilot_field[idb]])
        pilot_d[pr["pair"]] = fa - fb
    infl = gates["pilot_convention_RN4"]["chi2_90_inflation_factor_disclosed"]
    for n_worlds in ESCALATION_LADDER:
        rows = []
        for pr in pairs:
            sd = float(np.std(pilot_d[pr["pair"]], ddof=1))
            rows.append({"pair": pr["pair"], "pilot_paired_sd": sd,
                         "mde": mde_paired(sd, n_worlds), "target": MDE_TARGET,
                         "meets": bool(mde_paired(sd, n_worlds) <= MDE_TARGET),
                         "mde_chi2_inflated_disclosed": mde_paired(sd * infl, n_worlds)})
        g2["ladder"].append({"n_worlds": n_worlds, "per_pair": rows})
    selected: dict[str, int] = {}
    for pr in pairs:
        pid = pr["pair"]
        sd = float(np.std(pilot_d[pid], ddof=1))
        n_sel = ESCALATION_LADDER[0]
        escalated = False
        if mde_paired(sd, ESCALATION_LADDER[0]) > MDE_TARGET:
            n_sel = ESCALATION_LADDER[1]
            escalated = True
        short = bool(mde_paired(sd, n_sel) > MDE_TARGET)
        selected[pid] = n_sel
        g2["per_pair"].append({
            "pair": pid, "kind": pr["kind"],
            "pilot_paired_diffs": [float(x) for x in pilot_d[pid]],
            "pilot_paired_sd": sd, "mde_target": MDE_TARGET,
            "mde_at_32": mde_paired(sd, 32), "mde_at_64": mde_paired(sd, 64),
            "worlds_selected": n_sel, "escalated_32_to_64": escalated,
            "mde_at_selected": mde_paired(sd, n_sel),
            "short_at_max": short, "claims_tiered": short,
            "mde_chi2_inflated_at_selected_disclosed": mde_paired(sd * infl, n_sel),
            "chi2_inflated_would_escalate_disclosed": bool(
                mde_paired(sd * infl, ESCALATION_LADDER[0]) > MDE_TARGET),
            "chi2_inflated_short_at_64_disclosed": bool(
                mde_paired(sd * infl, ESCALATION_LADDER[1]) > MDE_TARGET),
        })
    g2["worlds_selected_by_pair"] = selected
    g2["n_escalated"] = int(sum(r["escalated_32_to_64"] for r in g2["per_pair"]))
    g2["n_short_at_max"] = int(sum(r["short_at_max"] for r in g2["per_pair"]))
    g2["criterion"] = (
        "MDE(80%, alpha=.05, paired, n) for the within-pair field difference <= 0.010 for "
        "EVERY pair, from a 4-WORLD pilot (RN-4); escalate 32->64 ONCE PER FAILING PAIR; "
        "still short at 64 -> RUN and TIER that pair's claims (registered)")
    g2["pass"] = True   # registered: a shortfall tiers claims, it does not block the run
    g2["power_met_all_pairs"] = bool(g2["n_short_at_max"] == 0)
    gates["G2e"] = g2

    # ---- G3e: rule 11 satisfiability with directions + rule 13 spec
    g3: dict[str, Any] = {"b_draws": B_BOOT, "seed": MASTER_SEED,
                          "b_draws_stability": B_BOOT_HIGH, "clauses": []}
    card_se = {}
    for a in arms:
        _, bt = m.bootstrap_card(pilot_card[a["arm"]], 400, MASTER_SEED)
        card_se[a["arm"]] = float(np.std(bt["r_card_b_raw"], ddof=1))
    proj_pair_hw, d_se_proj = {}, {}
    for pr in pairs:
        pid = pr["pair"]
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        se_pair = math.sqrt(card_se[ida] ** 2 + card_se[idb] ** 2)   # conservative: unpaired
        proj_pair_hw[pid] = 1.96 * se_pair * math.sqrt(len(PILOT_WORLDS) / selected[pid])
        d_se_proj[pid] = float(np.std(pilot_d[pid], ddof=1)) / math.sqrt(selected[pid])
    g3["projected_pair_attenuation_halfwidth"] = proj_pair_hw
    g3["projected_D_se"] = d_se_proj
    vs_pred = gates["VS_prediction"]["D_VS_pred_design"]
    g3["clauses"] = [
        {"lean": "G1e (attenuation)",
         "clause": "within-pair MEASURED card attenuation difference 95% CI inside +/-0.005",
         "direction": "two-sided (equivalence)",
         "satisfiable": bool(max(proj_pair_hw.values()) < MATCH_TOL_MEASURED),
         "note": "projected (conservative, unpaired) half-widths " + ", ".join(
             f"{k}={v:.8f}" for k, v in proj_pair_hw.items()) +
             f" against +/-{MATCH_TOL_MEASURED}; the paired bootstrap actually used is "
             "strictly tighter"},
        {"lean": "G1e (V_person)",
         "clause": "realized V_person share difference inside +/-0.005 on the DM pairs",
         "direction": "two-sided (equivalence)",
         "satisfiable": bool(max(abs(r["realized_person_difference"])
                                 for r in g4["within_pair"]
                                 if r["kind"] == "double_matched") < VPERSON_TOL_MEASURED),
         "note": "pilot realized |Delta V_person| on the DM pairs " + ", ".join(
             f"{r['pair']}={abs(r['realized_person_difference']):.8f}"
             for r in g4["within_pair"] if r["kind"] == "double_matched") +
             f" against +/-{VPERSON_TOL_MEASURED}"},
        {"lean": "cell MAT-SIG",
         "clause": "CI excludes 0 AND |D| >= M1=0.020 AND lower(|D|) >= M2=0.010",
         "direction": "two-sided exclusion + one-sided magnitude",
         "satisfiable": bool(all(1.96 * v < M1 - M2 for v in d_se_proj.values())),
         "note": "reachable iff 1.96*se < M1 - M2 = 0.010; projected 1.96*se " + ", ".join(
             f"{k}={1.96 * v:.8f}" for k, v in d_se_proj.items())},
        {"lean": "cell NULL", "clause": "CI includes 0 AND CI inside +/-M2=0.010",
         "direction": "two-sided (equivalence)",
         "satisfiable": bool(all(1.96 * v < M2 for v in d_se_proj.values())),
         "note": ("reachable iff 1.96*se < M2 for a D near 0; projected " + ", ".join(
             f"{k}={1.96 * v:.8f}" for k, v in d_se_proj.items()) +
             " -- THIS IS THE CLAUSE L-VAR NEEDS, so it is the leg's binding "
             "satisfiability requirement")},
        {"lean": "cell WEAK-NULL", "clause": "CI includes 0, inside +/-M1 but not +/-M2",
         "direction": "two-sided", "satisfiable": True,
         "note": "an annulus between the two margins; always reachable for some (D, se)"},
        {"lean": "cell SUB-SIG / INDET", "clause": "complement cells",
         "direction": "deterministic given the others", "satisfiable": True,
         "note": "the per-pair table is a verified partition (rule16_enumeration layer 1)"},
        {"lean": "L-VAR [.60]", "clause": "both DM cells in {NULL, WEAK-NULL}",
         "direction": "two-sided equivalence on both pairs",
         "satisfiable": bool(all(1.96 * d_se_proj[p["pair"]] < M1
                                 for p in pairs if p["kind"] == "double_matched")),
         "note": "pilot D " + ", ".join(
             f"{p['pair']}={float(np.mean(pilot_d[p['pair']])):+.8f}"
             for p in pairs if p["kind"] == "double_matched") +
             "; WEAK-NULL needs 1.96*se < M1, NULL needs 1.96*se < M2"},
        {"lean": "L-SPEC [.30]",
         "clause": ">=1 DM in {MAT-SIG(+), SUB-SIG(+)} and no DM negative",
         "direction": ("one-sided in content -- under H-SPECIES the int-carrying b arm is "
                       "worse, so the species signature is POSITIVE D -- scored on the "
                       "two-sided CI as registered"),
         "satisfiable": True,
         "note": "SUB-SIG(+) needs only CI exclusion of 0 on the positive side"},
        {"lean": "L-NEG [.05]", "clause": ">=1 DM in {MAT-SIG(-), SUB-SIG(-)}",
         "direction": "two-sided", "satisfiable": True,
         "note": "fits neither hypothesis; named and routed to P-NEG"},
        {"lean": "L-UND [.05]", "clause": "remainder (>=1 INDET, no significant cell)",
         "direction": "deterministic given the others", "satisfiable": True,
         "note": "INDET needs a CI wider than +/-M1, reachable at any n by chance"},
        {"lean": "L-VS [.70]",
         "clause": (f"measured D_VS CI contains pred={vs_pred!r} AND "
                    f"|D_VS - pred| <= {L_VS_TOL}"),
         "direction": ("one-sided in content (kappa_hat < 0 and Delta V_person > 0, so the "
                       "prediction is NEGATIVE); scored two-sided as registered"),
         "satisfiable": bool(1.96 * d_se_proj[VS_PAIR] < float("inf")),
         "note": (f"projected 1.96*se(D_VS) = {1.96 * d_se_proj[VS_PAIR]:.8f} against the "
                  f"tolerance {L_VS_TOL}; both a HOLD and a MISS are reachable. "
                  "INFORMATIVENESS (disclosed, not a gate): the containment clause is the "
                  "weaker of the two whenever 1.96*se exceeds the tolerance, in which case "
                  "the |D-pred| clause is the binding one; ratio 1.96*se/tol = "
                  f"{1.96 * d_se_proj[VS_PAIR] / L_VS_TOL:.4f}")},
        {"lean": "q-update", "clause": "pooled q over 25 arms (6 K2b + 7 K2c + 6 K2d + 6 K2e)",
         "direction": "descriptive, NO GATE", "satisfiable": True,
         "note": "K2d's 19-arm value q = 1.8528700746510731 [1.7147417060355998, "
                 "1.999586491101811]"},
        {"lean": "GAP", "clause": "NONE -- no GAP-based clause gates anything (registered)",
         "direction": "n/a", "satisfiable": True,
         "note": "K2d A-2's instrument boundary; GAP reported descriptively only"},
    ]
    g3["pass"] = bool(all(c["satisfiable"] for c in g3["clauses"]))
    gates["G3e"] = g3

    # ---- G5e: hygiene
    build_mean = float(np.mean(build_times))
    per_arm_world = pilot_work_seconds / (len(arms) * len(PILOT_WORLDS))
    n_arm_worlds = sum(selected[a["pair"]] for a in arms)
    n_world_idx = max(selected.values())
    est_total = per_arm_world * n_arm_worlds + build_mean * (
        len(phis) * n_world_idx)
    gates["G5e"] = {
        "pass": True,
        "round_trip_parsing_everywhere": True,
        "float_precision": "round_trip",
        "stages_chunked": ["part0", "arms --worlds a-b", "finalize"],
        "background_jobs": 0, "monitors": 0,
        "world_build_seconds_mean": build_mean,
        "pilot_seconds": pilot_seconds,
        "shares_solve_seconds": shares_seconds,
        "stage_estimate_seconds": {
            "per_arm_world": per_arm_world,
            "arm_worlds_total": n_arm_worlds,
            "arms_total": est_total,
            "recommended_chunk_worlds": 16,
            "stop_and_report_at": 2.0 * est_total,
        },
        "predicted_attenuation_desc": list(
            preds.sort_values("r_card_b_pred_raw", ascending=False)["arm"]),
    }

    gates["part0_all_pass"] = bool(
        gates["G0e"]["pass"] and gates["G1e"]["pass"] and gates["G2e"]["pass"]
        and gates["G3e"]["pass"] and gates["G4e"]["pass"] and gates["G5e"]["pass"]
        and gates["rule16_enumeration"]["PASS"]
        and gates["rule16_enumeration"]["layer2_lean_space"]["PASS"]
        and gates["rule16_enumeration"]["layer3_routing_space"]["PASS"])
    gates["stage_seconds"] = time.time() - t0
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n",
                                    encoding="utf-8")
    (OUT / "part0_arms.json").write_text(
        json.dumps({"master_seed": MASTER_SEED, "worlds_selected_by_pair": selected,
                    "arms": arms, "pairs": pairs}, indent=2, default=str) + "\n",
        encoding="utf-8")
    pd.DataFrame([r for a in arms for r in pilot_field[a["arm"]]]).to_csv(
        OUT / "part0_pilot_field.csv", index=False)
    write_part0_tables(gates, preds, pairs, kap)
    write_manifest({"part0": time.time() - t0})
    del k2b_field, k2c_field, k2c_x, k2c_order, k2d_field, k2d_x, k2d_order
    print(json.dumps({
        "stage": "part0", "seconds": round(time.time() - t0, 3),
        "part0_all_pass": gates["part0_all_pass"],
        **{g: gates[g]["pass"] for g in ("G0e", "G1e", "G2e", "G3e", "G4e", "G5e")},
        "rule16_layer1_cells": gates["rule16_enumeration"]["layer1_cell_space"]["PASS"],
        "rule16_layer2_leans": gates["rule16_enumeration"]["layer2_lean_space"]["PASS"],
        "rule16_layer3_routing": gates["rule16_enumeration"]["layer3_routing_space"]["PASS"],
        "kappa": {k: v for k, v in gates["G1e"]["kappa_coefficients"].items()
                  if k.startswith("kappa") or k.startswith("ordering")},
        "solved": {p["pair"]: {"s_a": p["arm_a"]["share"], "s_b": p["arm_b"]["share"],
                               "t_b": p["arm_b"]["int_share"],
                               "r_a": p["arm_a"]["predicted_attenuation"],
                               "r_b": p["arm_b"]["predicted_attenuation"],
                               "abs_dr": p["abs_predicted_attenuation_difference"],
                               "abs_dV": p["abs_predicted_person_share_difference"]}
                   for p in pairs},
        "vs_prediction": {k: gates["VS_prediction"][k] for k in
                          ("delta_person_design", "D_VS_pred_design",
                           "delta_person_pilot_realized", "D_VS_pred_pilot_realized")},
        "worlds_selected_by_pair": selected,
        "anchors_bit_exact": gates["G0e"]["all_bit_exact"],
        "stage_estimate": gates["G5e"]["stage_estimate_seconds"],
    }, indent=2, default=str))


def write_part0_tables(gates: dict[str, Any], preds: pd.DataFrame,
                       pairs: list[dict[str, Any]], kap: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("### G1e — the kappa coefficients (read out of the validated algebra)\n")
    lines.append("| quantity | value |")
    lines.append("|---|---|")
    lines.append(f"| `kappa(.90)` | {kap['kappa_phi_090']!r} |")
    lines.append(f"| `kappa(.98)` | {kap['kappa_phi_098']!r} |")
    lines.append(f"| `kappa_int` | {kap['kappa_int']!r} |")
    lines.append(f"| ordering `kappa_int < kappa(.90) < kappa(.98)` "
                 f"| {kap['ordering_kint_lt_k90_lt_k98']} |")
    lines.append(f"| `kappa(.98)/kappa(.90)` | {kap['ratio_k98_over_k90']!r} |")
    lines.append(f"| `kappa(.90)/kappa_int` | {kap['ratio_k90_over_kint']!r} |")

    lines.append("\n### G1e — the SOLVED shares and BOTH matching residuals\n")
    lines.append("| pair | kind | target r | arm a (share, int, phi) | r(a) | V_person(a) | "
                 "arm b (share, int, phi) | r(b) | V_person(b) | \\|Δr\\| | \\|ΔV\\| | matched |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for p in pairs:
        a, b = p["arm_a"], p["arm_b"]
        lines.append(
            f"| `{p['pair']}` | {p['kind']} | {p['target_attenuation']:g} | "
            f"`{a['arm']}` ({a['share']!r}, {a['int_share']!r}, {a['phi']:g}) | "
            f"{a['predicted_attenuation']!r} | {a['predicted_person_share']!r} | "
            f"`{b['arm']}` ({b['share']!r}, {b['int_share']!r}, {b['phi']:g}) | "
            f"{b['predicted_attenuation']!r} | {b['predicted_person_share']!r} | "
            f"{p['abs_predicted_attenuation_difference']:.6e} | "
            f"{p['abs_predicted_person_share_difference']:.6e} | {p['matched_part0']} |")

    lines.append("\n### RN-2 — the VS-62 phi enumeration (pure card algebra)\n")
    lines.append("| phi(a) | phi(b) | share a | share b | r(a) | r(b) | \\|Δr\\| | "
                 "V_person(a) | V_person(b) | ΔV_person | selected |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    sel = (PHI_A, PHI_B)
    for r in pairs[-1]["phi_enumeration"]:
        lines.append(
            f"| {r['phi_a']:g} | {r['phi_b']:g} | {r['share_a']:.12g} | {r['share_b']:.12g} | "
            f"{r['r_a']:.12g} | {r['r_b']:.12g} | "
            f"{r['abs_predicted_attenuation_difference']:.3e} | "
            f"{r['person_share_a']:.12g} | {r['person_share_b']:.12g} | "
            f"{r['delta_person_share']:+.12g} | "
            f"{(r['phi_a'], r['phi_b']) == sel} |")

    lines.append("\n### Part-0 point predictions — all 6 arms, computed before any world\n")
    lines.append("| arm | pair | share | int | phi | A (mu) | B (slow) | C (int) | "
                 "Cc (frame) | E (noise) | V_person | GAP pred | r(card→b) pred |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for _, r in preds.iterrows():
        lines.append(
            f"| `{r['arm']}` | {r['pair']} | {r['share_design']:.12g} | "
            f"{r['int_share']:.12g} | {r['phi_slow']:g} | {r['A_mu']:.8f} | "
            f"{r['B_slow']:.8f} | {r['C_int']:.8f} | {r['Cc_common']:.8f} | "
            f"{r['E_noise']:.8f} | {r['person_share_design']:.8f} | "
            f"{r['gap_pred']:.10f} | {r['r_card_b_pred_raw']:.12f} |")

    enum = gates["rule16_enumeration"]
    cs = enum["layer1_cell_space"]
    lines.append("\n### Rule-16 enumeration, LAYER 1 — the per-pair cell space\n")
    lines.append(f"Searched {cs['n_triples_searched']} (point, lo, hi) triples; "
                 f"{cs['n_realizable']}/{cs['n_combinations']} clause combinations "
                 f"realizable; overlaps {cs['n_overlapping']}; all seven signed cells "
                 f"realized: {cs['all_seven_cells_realized']}. PASS={cs['PASS']}.\n")
    lines.append("| c1 excludes 0 | c2 \\|D\\|≥M1 | c3 lower(\\|D\\|)≥M2 | c4 CI in ±M2 | "
                 "c5 CI in ±M1 | c6 D>0 | cell |")
    lines.append("|---|---|---|---|---|---|---|")
    for row in cs["truth_table"]:
        if not row["realizable"]:
            continue
        lines.append(
            f"| {row['c1_ci_excludes_zero']} | {row['c2_point_abs_ge_M1']} | "
            f"{row['c3_abs_lower_ge_M2']} | {row['c4_ci_inside_M2']} | "
            f"{row['c5_ci_inside_M1']} | {row['c6_D_positive']} | "
            f"{', '.join(row['cells'])} |")

    ls = enum["layer2_lean_space"]
    lines.append("\n### Rule-16 enumeration, LAYER 2 — the lean predicates over 49 "
                 "ordered DM-cell pairs\n")
    lines.append(f"unique {ls['n_unique']} / overlap {ls['n_overlap']} / gap {ls['n_gap']} "
                 f"of {ls['n_combinations']}; registration-gloss mismatches "
                 f"{len(ls['registration_gloss_L_UND_mismatches'])}; lean counts "
                 f"{ls['lean_counts']}. PASS={ls['PASS']}.\n")
    lines.append("| DM-68 cell | DM-56 cell | predicates true | lean (after precedence) |")
    lines.append("|---|---|---|---|")
    for row in ls["rows"]:
        lines.append(f"| {row['DM-68']} | {row['DM-56']} | "
                     f"{', '.join(row['predicates_true'])} | "
                     f"{row['lean_after_precedence']} |")

    rs = enum["layer3_routing_space"]
    lines.append("\n### Rule-16 enumeration, LAYER 3 — routing over "
                 f"{rs['n_combinations']} (cell-pair, L-VS) combinations\n")
    lines.append(f"routed {rs['n_routed']} / gap {rs['n_gap']}; outcomes "
                 f"{rs['outcome_counts']}. PASS={rs['PASS']}.\n")
    lines.append("| lean | L-VS | outcome | # cell-pairs |")
    lines.append("|---|---|---|---|")
    seen: dict[tuple[str, str, str], int] = {}
    for row in rs["rows"]:
        key = (row["lean"], row["L-VS"], row["outcome"])
        seen[key] = seen.get(key, 0) + 1
    for (lean, lvs, out), n in sorted(seen.items()):
        lines.append(f"| {lean} | {lvs} | **{out}** | {n} |")

    lines.append("\n### G4e liveness (pilot worlds "
                 f"{PILOT_WORLDS[0]}–{PILOT_WORLDS[-1]})\n")
    lines.append("| pair | kind | panel RMS a vs b | realized slow a | realized slow b | "
                 "realized int a | realized int b | realized V_person a | "
                 "realized V_person b | ΔV realized | pilot field a | pilot field b |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in gates["G4e"]["within_pair"]:
        lines.append(
            f"| `{r['pair']}` | {r['kind']} | {r['rms_panel_change']:.8f} | "
            f"{r['realized_slow_a']:.8f} | {r['realized_slow_b']:.8f} | "
            f"{r['realized_int_a']:.8f} | {r['realized_int_b']:.8f} | "
            f"{r['realized_person_a']:.8f} | {r['realized_person_b']:.8f} | "
            f"{r['realized_person_difference']:+.8f} | "
            f"{r['pilot_field_a']:.8f} | {r['pilot_field_b']:.8f} |")
    ap = gates["G4e"]["across_pair"]
    lines.append("\n| designed level | pilot card attenuation | pilot field recovery |")
    lines.append("|---|---|---|")
    for lvl, c, f in zip(ap["levels_ascending_by_design"], ap["pilot_card_attenuation"],
                         ap["pilot_field_recovery"]):
        lines.append(f"| {lvl} | {c:.8f} | {f:.8f} |")

    lines.append("\n### G2e power ladder (4-WORLD pilot, RN-4)\n")
    lines.append("| pair | pilot paired sd | MDE target | MDE @32 | MDE @64 | selected n | "
                 "escalated | short at max | χ²-inflated MDE @sel (disclosed) |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for r in gates["G2e"]["per_pair"]:
        lines.append(f"| `{r['pair']}` | {r['pilot_paired_sd']:.8f} | {r['mde_target']:g} | "
                     f"{r['mde_at_32']:.8f} | {r['mde_at_64']:.8f} | {r['worlds_selected']} | "
                     f"{r['escalated_32_to_64']} | {r['short_at_max']} | "
                     f"{r['mde_chi2_inflated_at_selected_disclosed']:.8f} |")

    lines.append("\n### G3e clause satisfiability with DIRECTIONS (rule 11)\n")
    lines.append("| lean | clause | direction | satisfiable | note |")
    lines.append("|---|---|---|---|---|")
    for c in gates["G3e"]["clauses"]:
        lines.append(f"| {c['lean']} | {c['clause']} | {c['direction']} | "
                     f"{c['satisfiable']} | {c['note']} |")
    (OUT / "part0_tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Stage: arms

def require_part0() -> dict[str, Any]:
    path = OUT / "gates.json"
    if not path.exists():
        raise SystemExit("REFUSED: Part 0 has not run (results/.../gates.json missing).")
    gates = json.loads(path.read_text(encoding="utf-8"))
    if not gates.get("part0_all_pass"):
        raise SystemExit("REFUSED: a Part-0 gate failed; no arms may run.")
    if not REPORT.exists():
        raise SystemExit("REFUSED: the Part-0 report has not been written to disk.")
    return gates


def run_arms(args: argparse.Namespace) -> None:
    gates = require_part0()
    k2d().install_species_weights()
    m = k2b()
    selected = {k: int(v) for k, v in gates["G2e"]["worlds_selected_by_pair"].items()}
    n_max = max(selected.values())
    lo, hi = (0, n_max - 1)
    if args.worlds:
        a, _, b = args.worlds.partition("-")
        lo, hi = int(a), int(b or a)
    if hi >= n_max:
        raise SystemExit(f"REFUSED: world range {lo}-{hi} exceeds n_max={n_max}")
    arms = arms_spec()
    t0 = time.time()
    card_acc: dict[str, list[pd.DataFrame]] = {a["arm"]: [] for a in arms}
    field_acc: dict[str, list[dict[str, Any]]] = {a["arm"]: [] for a in arms}
    weights = {a["arm"]: m.arm_weights(a["share"], a["w_int_arm"]) for a in arms}
    for world_index in range(lo, hi + 1):
        active = [a for a in arms if world_index < selected[a["pair"]]]
        if not active:
            continue
        seed = world_seed_for(world_index)
        worlds = {phi: m.build_k2b_world(seed, phi)
                  for phi in sorted({a["phi"] for a in active})}
        for a in active:
            world = worlds[a["phi"]]
            w = weights[a["arm"]]
            frame, _ = m.card_channel_frame(world, w, seed)
            card_acc[a["arm"]].append(frame)
            row = run_field_world(a["arm"], world_index, world, w)
            rs = realized_person_shares(world, w)
            row.update({f"realized_{k}": v for k, v in rs.items()})
            row["realized_person"] = rs["slow"] + rs["int"]
            field_acc[a["arm"]].append(row)
        del worlds
        print(f"  world {world_index}: {len(active)} arms  ({time.time() - t0:.1f}s)")
    tag = f"w{lo:03d}_{hi:03d}"
    written = []
    for a in arms:
        aid = a["arm"]
        if not field_acc[aid]:
            continue
        pd.concat(card_acc[aid], ignore_index=True).to_csv(
            OUT / f"arm_{aid}_card_{tag}.csv", index=False)
        pd.DataFrame(field_acc[aid]).to_csv(OUT / f"arm_{aid}_field_{tag}.csv", index=False)
        written.append(aid)
    write_manifest({f"arms[{tag}]": time.time() - t0})
    print(json.dumps({"stage": "arms", "worlds": [lo, hi], "arms": written,
                      "seconds": round(time.time() - t0, 3)}, indent=2))


def load_arm(aid: str, n_worlds: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    card = pd.concat([read_csv_rt(p) for p in sorted(OUT.glob(f"arm_{aid}_card_w*.csv"))],
                     ignore_index=True)
    field = pd.concat([read_csv_rt(p) for p in sorted(OUT.glob(f"arm_{aid}_field_w*.csv"))],
                      ignore_index=True).sort_values("world").reset_index(drop=True)
    if len(field) != n_worlds:
        raise SystemExit(f"REFUSED: arm {aid} has {len(field)} worlds, expected {n_worlds}")
    return card, field


# ---------------------------------------------------------------------------
# Stage: finalize

def run_finalize(args: argparse.Namespace) -> None:
    gates = require_part0()
    kd = k2d()
    kd.install_species_weights()
    m = k2b()
    k2a = m.k2a()
    kc = k2c()
    t0 = time.time()
    selected = {k: int(v) for k, v in gates["G2e"]["worlds_selected_by_pair"].items()}
    arms = arms_spec()
    pairs = pairs_spec()
    preds = read_csv_rt(OUT / "part0_predictions.csv").set_index("arm")

    card_by_arm: dict[str, pd.DataFrame] = {}
    field_by_arm: dict[str, np.ndarray] = {}
    mixed_by_arm: dict[str, np.ndarray] = {}
    person_by_arm: dict[str, np.ndarray] = {}
    cells: list[dict[str, Any]] = []
    stability: list[dict[str, Any]] = []
    for a in arms:
        aid = a["arm"]
        n_worlds = selected[a["pair"]]
        card, field = load_arm(aid, n_worlds)
        card_by_arm[aid] = card
        field_by_arm[aid] = field["recovery_b_only"].to_numpy(float)
        mixed_by_arm[aid] = field["recovery_mixed"].to_numpy(float)
        person_by_arm[aid] = field["realized_person"].to_numpy(float)
        point, boots = m.bootstrap_card(card, B_BOOT, MASTER_SEED)
        row: dict[str, Any] = {"arm": aid, "pair": a["pair"], "side": a["side"],
                               "kind": a["kind"], "share": a["share"],
                               "int_share": a["int_share"], "phi": a["phi"],
                               "n_authors_pooled": int(len(card)),
                               "n_worlds": int(len(field))}
        for key, pkey in (("gap", "gap_pred"), ("r_card_b_raw", "r_card_b_pred_raw")):
            lo, hi = k2a.ci_of(boots[key])
            row[key] = float(point[key])
            row[f"{key}_lo"], row[f"{key}_hi"] = lo, hi
            row[f"{key}_se"] = float(np.std(boots[key], ddof=1))
            row[f"{key}_pred"] = float(preds.loc[aid, pkey])
            row[f"{key}_err"] = float(point[key]) - float(preds.loc[aid, pkey])
            row[f"{key}_rel_err"] = row[f"{key}_err"] / float(preds.loc[aid, pkey])
            row[f"{key}_contains_pred"] = bool(lo <= float(preds.loc[aid, pkey]) <= hi)
        row["recovery_b_only_mean"] = float(np.mean(field_by_arm[aid]))
        row["recovery_b_only_sd"] = float(np.std(field_by_arm[aid], ddof=1))
        row["recovery_mixed_mean"] = float(np.mean(mixed_by_arm[aid]))
        row["recovery_mixed_sd"] = float(np.std(mixed_by_arm[aid], ddof=1))
        row["realized_person_mean"] = float(np.mean(person_by_arm[aid]))
        row["realized_person_sd"] = float(np.std(person_by_arm[aid], ddof=1))
        row["person_share_design"] = float(preds.loc[aid, "person_share_design"])
        row["realized_minus_design_person"] = (row["realized_person_mean"]
                                               - row["person_share_design"])
        cells.append(row)
        print(f"  finalized {aid} ({time.time() - t0:.1f}s)")
    pd.DataFrame(cells).to_csv(OUT / "cells.csv", index=False)
    cell_by_arm = {r["arm"]: r for r in cells}

    # ---- world-block paired bootstrap (shared picks within an n; per-pair n)
    picks = {n: np.random.default_rng(MASTER_SEED).integers(0, n, size=(B_BOOT, n))
             for n in sorted(set(selected.values()))}
    picks_hi = {n: np.random.default_rng(MASTER_SEED).integers(0, n, size=(B_BOOT_HIGH, n))
                for n in sorted(set(selected.values()))}
    boot_field = {a["arm"]: field_by_arm[a["arm"]][picks[selected[a["pair"]]]].mean(axis=1)
                  for a in arms}
    boot_mixed = {a["arm"]: mixed_by_arm[a["arm"]][picks[selected[a["pair"]]]].mean(axis=1)
                  for a in arms}
    boot_person = {a["arm"]: person_by_arm[a["arm"]][picks[selected[a["pair"]]]].mean(axis=1)
                   for a in arms}

    # ---- G1e post-arms: the MEASURED DOUBLE matching
    g1_post: list[dict[str, Any]] = []
    for pr in pairs:
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        is_dm = bool(pr["kind"] == "double_matched")
        pa, pb, ba, bb = kc.bootstrap_card_pair(card_by_arm[ida], card_by_arm[idb],
                                                B_BOOT, MASTER_SEED)
        d_boot = ba["r_card_b_raw"] - bb["r_card_b_raw"]
        d_point = float(pa["r_card_b_raw"] - pb["r_card_b_raw"])
        lo, hi = k2a.ci_of(d_boot)
        att_ok = bool(-MATCH_TOL_MEASURED <= lo and hi <= MATCH_TOL_MEASURED)
        dpv = float(np.mean(person_by_arm[ida] - person_by_arm[idb]))
        plo, phi_ = k2a.ci_of(boot_person[ida] - boot_person[idb])
        pv_ok = bool(abs(dpv) <= VPERSON_TOL_MEASURED) if is_dm else None
        void = bool(not att_ok or (is_dm and not pv_ok))
        g1_post.append({
            "pair": pr["pair"], "kind": pr["kind"], "arm_a": ida, "arm_b": idb,
            "measured_attenuation_a": float(pa["r_card_b_raw"]),
            "measured_attenuation_b": float(pb["r_card_b_raw"]),
            "predicted_attenuation": pr["arm_a"]["predicted_attenuation"],
            "measured_attenuation_difference": d_point, "attenuation_ci": [lo, hi],
            "attenuation_se": float(np.std(d_boot, ddof=1)),
            "attenuation_margin": MATCH_TOL_MEASURED, "attenuation_inside": att_ok,
            "attenuation_tightness_ratio": (MATCH_TOL_MEASURED / max(abs(lo), abs(hi))
                                            if max(abs(lo), abs(hi)) > 0 else float("inf")),
            "realized_person_a": float(np.mean(person_by_arm[ida])),
            "realized_person_b": float(np.mean(person_by_arm[idb])),
            "realized_person_difference": dpv,
            "realized_person_difference_ci": [plo, phi_],
            "realized_person_ci_inside_margin_descriptive": bool(
                -VPERSON_TOL_MEASURED <= plo and phi_ <= VPERSON_TOL_MEASURED),
            "person_margin": VPERSON_TOL_MEASURED,
            "person_clause_applies": is_dm, "person_inside": pv_ok,
            "person_tightness_ratio": (VPERSON_TOL_MEASURED / abs(dpv)
                                       if dpv != 0.0 else float("inf")),
            "VOID": void,
        })
        mc = k2a.mc_sd_of_endpoint(d_boot, B_BOOT, 0.025)
        dist = min(abs(MATCH_TOL_MEASURED - hi), abs(-MATCH_TOL_MEASURED - lo))
        if dist <= 2.0 * mc:
            _, _, ba2, bb2 = kc.bootstrap_card_pair(card_by_arm[ida], card_by_arm[idb],
                                                    B_BOOT_HIGH, MASTER_SEED)
            d2 = ba2["r_card_b_raw"] - bb2["r_card_b_raw"]
            lo2, hi2 = k2a.ci_of(d2)
            v2 = bool(-MATCH_TOL_MEASURED <= lo2 and hi2 <= MATCH_TOL_MEASURED)
            stability.append({"scope": f"G1e[{pr['pair']}]",
                              "clause": "measured within-pair attenuation diff CI inside +/-0.005",
                              "direction": "two-sided (equivalence)",
                              "boundary": MATCH_TOL_MEASURED, "mc_sd_endpoint_B2000": mc,
                              "distance_to_boundary": dist, "verdict_B2000": att_ok,
                              "verdict_B20000": v2, "endpoints_B20000": [lo2, hi2],
                              "status": "STABLE" if att_ok == v2 else "BOUNDARY"})
    n_void = sum(r["VOID"] for r in g1_post)

    # ---- D per pair + the CELL assignment
    d_rows: list[dict[str, Any]] = []
    for pr in pairs:
        pid = pr["pair"]
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        n_worlds = selected[pid]
        d = field_by_arm[ida] - field_by_arm[idb]
        db = boot_field[ida] - boot_field[idb]
        lo, hi = k2a.ci_of(db)
        point = float(np.mean(d))
        sd_real = float(np.std(d, ddof=1))
        mde_real = mde_paired(sd_real, n_worlds)
        clauses = clause_vector(point, lo, hi)
        cell = assign_cell(point, lo, hi)
        dm = mixed_by_arm[ida] - mixed_by_arm[idb]
        dmb = boot_mixed[ida] - boot_mixed[idb]
        mlo, mhi = k2a.ci_of(dmb)
        pilot = next(r for r in gates["G2e"]["per_pair"] if r["pair"] == pid)
        rec = {
            "pair": pid, "kind": pr["kind"], "arm_a": ida, "arm_b": idb,
            "sign_convention": pr["sign_convention"], "n_worlds": n_worlds,
            "field_a": float(np.mean(field_by_arm[ida])),
            "field_b": float(np.mean(field_by_arm[idb])),
            "D": point, "ci": [lo, hi], "se": float(np.std(db, ddof=1)),
            "abs_D": abs(point),
            "abs_lower_RN2": (min(abs(lo), abs(hi)) if clauses["c1_ci_excludes_zero"] else 0.0),
            "sd_paired_realized": sd_real,
            "mde_realized": mde_real, "mde_pilot": pilot["mde_at_selected"],
            "mde_target": pilot["mde_target"],
            "mde_realized_meets_target": bool(mde_real <= pilot["mde_target"]),
            "pilot_sd_underestimate_factor": (sd_real / pilot["pilot_paired_sd"]
                                              if pilot["pilot_paired_sd"] > 0 else float("inf")),
            "sign": int(np.sign(point)),
            "per_world_positive": int(np.sum(d > 0.0)),
            "paired_t_ci": [point - kc.T_QUANTILES[n_worlds][0] * sd_real / math.sqrt(n_worlds),
                            point + kc.T_QUANTILES[n_worlds][0] * sd_real / math.sqrt(n_worlds)],
            "level": 0.5 * (float(np.mean(field_by_arm[ida]))
                            + float(np.mean(field_by_arm[idb]))),
            "abs_D_pct_of_level": abs(point) / (0.5 * (float(np.mean(field_by_arm[ida]))
                                                       + float(np.mean(field_by_arm[idb])))),
            "delta_mixed": float(np.mean(dm)), "delta_mixed_ci": [mlo, mhi],
            "delta_mixed_se": float(np.std(dmb, ddof=1)),
            "delta_mixed_excludes_zero": bool(mlo > 0.0 or mhi < 0.0),
            "VOID": bool(next(r["VOID"] for r in g1_post if r["pair"] == pid)),
            **clauses,
            "CELL": cell,
            "point_sign_consistent_with_ci": bool(
                (not clauses["c1_ci_excludes_zero"])
                or (point > 0.0 and lo > 0.0) or (point < 0.0 and hi < 0.0)),
        }
        d_rows.append(rec)
        db_hi = (field_by_arm[ida][picks_hi[n_worlds]].mean(axis=1)
                 - field_by_arm[idb][picks_hi[n_worlds]].mean(axis=1))
        dmb_hi = (mixed_by_arm[ida][picks_hi[n_worlds]].mean(axis=1)
                  - mixed_by_arm[idb][picks_hi[n_worlds]].mean(axis=1))
        mc = k2a.mc_sd_of_endpoint(db, B_BOOT, 0.025)
        mc_m = k2a.mc_sd_of_endpoint(dmb, B_BOOT, 0.025)
        checks = [
            ("CELL[c1] CI excludes 0", 0.0, min(abs(lo), abs(hi)),
             clauses["c1_ci_excludes_zero"],
             lambda l2, h2: bool(l2 > 0.0 or h2 < 0.0), db_hi, mc),
            ("CELL[c3] lower(|D|) >= M2", M2,
             abs((min(abs(lo), abs(hi)) if clauses["c1_ci_excludes_zero"] else 0.0) - M2),
             clauses["c3_abs_lower_ge_M2"],
             lambda l2, h2: bool((min(abs(l2), abs(h2)) if (l2 > 0 or h2 < 0) else 0.0) >= M2),
             db_hi, mc),
            ("CELL[c4] CI inside +/-M2", M2, min(abs(M2 - hi), abs(-M2 - lo)),
             clauses["c4_ci_inside_M2"],
             lambda l2, h2: bool(-M2 <= l2 and h2 <= M2), db_hi, mc),
            ("CELL[c5] CI inside +/-M1", M1, min(abs(M1 - hi), abs(-M1 - lo)),
             clauses["c5_ci_inside_M1"],
             lambda l2, h2: bool(-M1 <= l2 and h2 <= M1), db_hi, mc),
            ("Delta_mixed CI excludes 0 (descriptive)", 0.0, min(abs(mlo), abs(mhi)),
             rec["delta_mixed_excludes_zero"],
             lambda l2, h2: bool(l2 > 0.0 or h2 < 0.0), dmb_hi, mc_m),
        ]
        if pid == VS_PAIR:
            pred_vs = gates["VS_prediction"]["D_VS_pred_design"]
            checks.append(
                ("L-VS CI contains pred", pred_vs, min(abs(pred_vs - lo), abs(pred_vs - hi)),
                 bool(lo <= pred_vs <= hi),
                 lambda l2, h2, _p=pred_vs: bool(l2 <= _p <= h2), db_hi, mc))
        for name, boundary, dist, v1, test, boots_hi, mc_use in checks:
            if dist <= 2.0 * mc_use:
                lo2, hi2 = k2a.ci_of(boots_hi)
                v2 = test(lo2, hi2)
                stability.append({"scope": f"{name}[{pid}]", "clause": name,
                                  "direction": "two-sided", "boundary": boundary,
                                  "mc_sd_endpoint_B2000": mc_use,
                                  "distance_to_boundary": dist, "verdict_B2000": bool(v1),
                                  "verdict_B20000": bool(v2),
                                  "endpoints_B20000": [lo2, hi2],
                                  "status": "STABLE" if bool(v1) == bool(v2) else "BOUNDARY"})
        rec["rule13_closest_approach_mc_sd"] = min(
            (dist / mc_use if mc_use > 0 else float("inf"))
            for _, _, dist, _, _, _, mc_use in checks)
    pd.DataFrame(d_rows).to_csv(OUT / "pair_differences.csv", index=False)
    by_pair = {r["pair"]: r for r in d_rows}

    # ---- the lean predicate over the two DM cells (RN-7: VOID -> INDET)
    dm_ids = [p["pair"] for p in pairs if p["kind"] == "double_matched"]
    cell_used = {}
    for pid in dm_ids:
        r = by_pair[pid]
        cell_used[pid] = "INDET" if r["VOID"] else r["CELL"]
    lean_trues = lean_predicates_true(cell_used[dm_ids[0]], cell_used[dm_ids[1]])
    lean = lean_of(cell_used[dm_ids[0]], cell_used[dm_ids[1]])
    lean_obj = {
        "cells_used": cell_used,
        "cells_raw": {pid: by_pair[pid]["CELL"] for pid in dm_ids},
        "void": {pid: by_pair[pid]["VOID"] for pid in dm_ids},
        "predicates_true": lean_trues,
        "n_predicates_true": len(lean_trues),
        "lean": lean, "prior": LEAN_PRIORS[lean], "priors": dict(LEAN_PRIORS),
        "precedence": list(LEAN_PRECEDENCE),
        "enumeration_check": (
            "the four predicates partition all 7x7 = 49 ordered DM-cell pairs -- verified "
            "by enumeration in Part 0 (rule16_enumeration.layer2_lean_space): exactly one "
            "predicate fires on every combination BEFORE precedence is applied, the "
            "registration's own gloss for L-UND agrees on all 49, and all four leans are "
            "realized"),
        "D": {pid: by_pair[pid]["D"] for pid in dm_ids},
        "ci": {pid: by_pair[pid]["ci"] for pid in dm_ids},
    }

    # ---- L-VS: the registered quantitative test of the estimand
    vs = by_pair[VS_PAIR]
    vsg = gates["VS_prediction"]
    l_vs_readings = {}
    for label, pred_value in (("design_PRIMARY", vsg["D_VS_pred_design"]),
                              ("pilot_realized_SECONDARY", vsg["D_VS_pred_pilot_realized"])):
        contains = bool(vs["ci"][0] <= pred_value <= vs["ci"][1])
        within = bool(abs(vs["D"] - pred_value) <= L_VS_TOL)
        l_vs_readings[label] = {
            "predicted": pred_value, "measured": vs["D"], "ci": vs["ci"],
            "clause_ci_contains_pred": contains,
            "abs_difference": abs(vs["D"] - pred_value),
            "clause_abs_diff_le_tol": within, "tolerance": L_VS_TOL,
            "holds": bool(contains and within and not vs["VOID"]),
        }
    # RN-8: a VOID VS pair cannot license a HOLD
    l_vs = {
        "prior": L_VS_PRIOR,
        "clause": ("measured D_VS CI contains the Part-0 predicted "
                   "-0.7220359963712748 x Delta V_person AND |D_VS - pred| <= 0.010"),
        "kappa_hat": KAPPA_HAT,
        "delta_person_design": vsg["delta_person_design"],
        "delta_person_pilot_realized": vsg["delta_person_pilot_realized"],
        "delta_person_arms_realized": next(
            r["realized_person_difference"] for r in g1_post if r["pair"] == VS_PAIR),
        "readings": l_vs_readings,
        "primary_reading": "design_PRIMARY",
        "VOID": vs["VOID"],
        "holds": l_vs_readings["design_PRIMARY"]["holds"],
        "both_readings_agree": bool(l_vs_readings["design_PRIMARY"]["holds"]
                                    == l_vs_readings["pilot_realized_SECONDARY"]["holds"]),
    }

    # ---- ROUTING (the registration's table, every combination assigned)
    outcome = route(lean, l_vs["holds"])
    routing = {
        "lean": lean, "L_VS": "hold" if l_vs["holds"] else "miss",
        "outcome": outcome,
        "table": {
            "(L-VAR, L-VS hold)": "P-VAR", "(L-VAR, L-VS miss)": "P-VAR-WEAK",
            "(L-SPEC, any)": "P-SPEC", "(L-NEG, any)": "P-NEG", "(L-UND, any)": "P-UND"},
        "consequences": {
            "P-VAR": ("the estimand is CONFIRMED as the registered form -- T4 CLOSES as "
                      "T4-reader-amplified-variance: field ~ lambda*r^q - kappa*V_person "
                      "(q ~ 1.85 [1.71, 2.00], kappa ~ 0.722) -- reader-borne in "
                      "substance, species-blind, taxing raw person variance. Next "
                      "registration: the constructive repair test (de-framing vs kappa "
                      "and lambda)."),
            "P-VAR-WEAK": ("DM nulls without the quantitative law -- H-VAR survives "
                           "qualitatively, the coefficient form does not; re-estimate "
                           "before closure (one more leg)."),
            "P-SPEC": ("species-specific reader -- occasion-bound content is intrinsically "
                       "expensive beyond (r, V); T4 closes in the composition form; the "
                       "repair design becomes interaction-specific."),
            "P-NEG": ("fits neither; the estimand and the species account are both wrong "
                      "as stated; modeling leg next; no closure."),
            "P-UND": ("escalation already spent -> report resolution attained; the DM "
                      "question carries to a 64-world K2e' only if the user asks."),
        }[outcome],
    }

    # ---- q-update over all 25 arms (DESCRIPTIVE, no gate)
    anchors = rederive_anchors()
    k2b_field = anchors.pop("_k2b_field")
    k2c_field = anchors.pop("_k2c_field")
    k2c_x = anchors.pop("_k2c_x")
    k2c_order = anchors.pop("_k2c_order")
    k2d_field = anchors.pop("_k2d_field")
    k2d_x = anchors.pop("_k2d_x")
    k2d_order = anchors.pop("_k2d_order")
    kap_x = anchors.pop("_kappa_x")
    kap_y = anchors.pop("_kappa_y")
    kap_pairs = anchors.pop("_kappa_pairs")
    order_e = tuple(a["arm"] for a in arms)
    x_e = np.log(np.array([float(preds.loc[a, "r_card_b_pred_raw"]) for a in order_e]))
    groups_by_n: dict[int, list[str]] = {}
    for a in arms:
        groups_by_n.setdefault(selected[a["pair"]], []).append(a["arm"])
    e_groups = []
    for n in sorted(groups_by_n):
        ids = groups_by_n[n]
        idx = [order_e.index(i) for i in ids]
        e_groups.append((x_e[idx], [field_by_arm[i] for i in ids]))
    groups = [(k2c_x[:6], [k2b_field[a] for a in K2B_PRIMARY_ARMS]),
              (k2c_x[6:], [k2c_field[a] for a in k2c_order]),
              (k2d_x, [k2d_field[a] for a in k2d_order])] + e_groups
    q25 = kd.pooled_q(groups, K2B_LAMBDA, B_BOOT, MASTER_SEED)
    q25_lam1 = kd.pooled_q(groups, 1.0, B_BOOT, MASTER_SEED)
    q25.pop("q_boot")
    q25_lam1.pop("q_boot")
    q25.update({
        "scope": "25 arms = 6 K2b + 7 K2c + 6 K2d + 6 K2e",
        "x_convention": "Part-0 PREDICTED attenuation (deterministic x), as in K2c/K2d",
        "lambda_invariance_check": {"q_at_lambda_k2b": q25["q"], "q_at_lambda_1": q25_lam1["q"],
                                    "abs_difference": abs(q25["q"] - q25_lam1["q"])},
        "k2d_19_arm_value": anchors["k2d"]["q19_rederived"],
        "k2d_19_arm_ci": anchors["k2d"]["q19_ci_rederived"],
        "shift_vs_k2d": q25["q"] - anchors["k2d"]["q19_rederived"],
        "gate": "NONE (registered descriptive)",
    })

    # ---- the kappa companion extended to 9 pairs (DECLARED DESCRIPTIVE in Part 0)
    x9 = np.concatenate([kap_x, np.array([
        next(p for p in pairs if p["pair"] == pid)["predicted_person_share_difference"]
        for pid in (dm_ids[0], dm_ids[1], VS_PAIR)])])
    y9 = np.concatenate([kap_y, np.array([by_pair[pid]["D"]
                                          for pid in (dm_ids[0], dm_ids[1], VS_PAIR)])])
    kappa9 = float((x9 @ y9) / (x9 @ x9))
    resid9 = y9 - kappa9 * x9
    kappa_refit = {
        "gate": "NONE (declared DESCRIPTIVE in Part 0, no branch weight)",
        "scope": "9 pairs = 3 K2c + 3 K2d + 3 K2e",
        "kappa": kappa9,
        "kappa_k2d_6pair": anchors["kappa_companion"]["kappa_rederived"],
        "shift_vs_k2d": kappa9 - anchors["kappa_companion"]["kappa_rederived"],
        "r2_vs_mean": float(1.0 - (resid9 @ resid9) / ((y9 - y9.mean()) @ (y9 - y9.mean()))),
        "max_abs_residual": float(np.max(np.abs(resid9))),
        "rows": [{"pair": p, "dvar": float(xx), "D": float(yy),
                  "residual": float(yy - kappa9 * xx),
                  "kappa_pair": (float(yy / xx) if xx != 0.0 else None)}
                 for p, xx, yy in zip([pid for _, pid in kap_pairs]
                                      + [dm_ids[0], dm_ids[1], VS_PAIR], x9, y9)],
        "note": ("the two DM pairs sit at dvar 0 (to <=1.4e-17) by design, so they carry "
                 "essentially NO leverage on an origin-forced slope: their residual IS "
                 "their D, which is precisely the H-VAR test. Reported for completeness."),
    }

    if stability:
        pd.DataFrame(stability).to_csv(OUT / "rule13_stability.csv", index=False)
    boundary = [s for s in stability if s["status"] == "BOUNDARY"]

    # ---- verdict slug
    def slugify(cell: str) -> str:
        return (cell.replace("MAT-SIG", "MATSIG").replace("SUB-SIG", "SUBSIG")
                .replace("WEAK-NULL", "WEAKNULL").replace("(", "_").replace(")", "")
                .replace("+", "POS").replace("-", "NEG"))

    slug = (f"DM68_{slugify(cell_used[dm_ids[0]])}__DM56_{slugify(cell_used[dm_ids[1]])}"
            f"__{lean.replace('-', '_')}"
            f"__LVS_{'HOLD' if l_vs['holds'] else 'MISS'}"
            f"__MATCH_{'EXACT' if n_void == 0 else f'VOID{n_void}'}"
            f"__{outcome.replace('-', '_')}")

    descriptive = {
        "per_arm": {
            a["arm"]: {
                "pair": a["pair"], "side": a["side"], "kind": a["kind"],
                "share": a["share"], "int_share": a["int_share"], "phi": a["phi"],
                "n_worlds": selected[a["pair"]],
                "predicted_attenuation": float(preds.loc[a["arm"], "r_card_b_pred_raw"]),
                "measured_attenuation": cell_by_arm[a["arm"]]["r_card_b_raw"],
                "measured_attenuation_ci": [cell_by_arm[a["arm"]]["r_card_b_raw_lo"],
                                            cell_by_arm[a["arm"]]["r_card_b_raw_hi"]],
                "attenuation_rel_err": cell_by_arm[a["arm"]]["r_card_b_raw_rel_err"],
                "attenuation_contains_pred": cell_by_arm[a["arm"]]["r_card_b_raw_contains_pred"],
                "card_gap": cell_by_arm[a["arm"]]["gap"],
                "card_gap_pred": cell_by_arm[a["arm"]]["gap_pred"],
                "card_gap_contains_pred": cell_by_arm[a["arm"]]["gap_contains_pred"],
                "card_gap_rel_err": cell_by_arm[a["arm"]]["gap_rel_err"],
                "person_share_design": cell_by_arm[a["arm"]]["person_share_design"],
                "realized_person_mean": cell_by_arm[a["arm"]]["realized_person_mean"],
                "field_b_only": float(np.mean(field_by_arm[a["arm"]])),
                "field_b_only_ci": list(k2a.ci_of(boot_field[a["arm"]])),
                "field_mixed": float(np.mean(mixed_by_arm[a["arm"]])),
                "field_mixed_ci": list(k2a.ci_of(boot_mixed[a["arm"]])),
                "mixed_minus_b": float(np.mean(mixed_by_arm[a["arm"]] - field_by_arm[a["arm"]])),
            } for a in arms},
        "card_positive_control": {
            "arms_attenuation_containing_prediction": int(sum(
                cell_by_arm[a["arm"]]["r_card_b_raw_contains_pred"] for a in arms)),
            "arms_gap_containing_prediction": int(sum(
                cell_by_arm[a["arm"]]["gap_contains_pred"] for a in arms)),
            "n_arms": len(arms),
            "max_abs_attenuation_rel_err": float(max(
                abs(cell_by_arm[a["arm"]]["r_card_b_raw_rel_err"]) for a in arms)),
            "max_abs_gap_rel_err": float(max(
                abs(cell_by_arm[a["arm"]]["gap_rel_err"]) for a in arms)),
            "note": ("NOT a registered gate anywhere in this leg, and GAP in particular "
                     "gates NOTHING (K2d A-2's instrument boundary); continuity only")},
        "card_gap_ratio_within_pair": {
            pr["pair"]: (cell_by_arm[pr["arm_a"]["arm"]]["gap"]
                         / cell_by_arm[pr["arm_b"]["arm"]]["gap"]) for pr in pairs},
        "delta_mixed_by_pair": {r["pair"]: {"delta_mixed": r["delta_mixed"],
                                            "ci": r["delta_mixed_ci"],
                                            "excludes_zero": r["delta_mixed_excludes_zero"],
                                            "ratio_to_abs_D": (abs(r["delta_mixed"]) / r["abs_D"]
                                                               if r["abs_D"] > 0 else None)}
                                for r in d_rows},
    }

    decision = {
        "leg": "M4-K2e",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "banner": BANNER,
        "master_seed": MASTER_SEED,
        "worlds_selected_by_pair": selected,
        "margins": {"M1": M1, "M2": M2},
        "kappa_hat_registered": KAPPA_HAT,
        "n_authors_per_world": int(len(m.layout()["author_ids"])),
        "n_retained": int(len(m.layout()["retained_idx"])),
        "arms": arms,
        "G0e_anchors": anchors,
        "G1e_post_arms": {"per_pair": g1_post, "pairs_void": n_void,
                          "pass": bool(n_void == 0)},
        "pair_differences": d_rows,
        "cells": {r["pair"]: r["CELL"] for r in d_rows},
        "lean": lean_obj,
        "L_VS": l_vs,
        "routing": routing,
        "q_update": q25,
        "kappa_refit_9pairs": kappa_refit,
        "rule13": {"triggered": len(stability), "boundary": len(boundary),
                   "records": stability},
        "rule16_enumeration": gates["rule16_enumeration"],
        "descriptive": descriptive,
        "verdict_slug": slug,
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2, default=str) + "\n",
                                       encoding="utf-8")
    write_manifest({"finalize": time.time() - t0})
    print(json.dumps({k: v for k, v in decision.items()
                      if k not in ("rule13", "descriptive", "arms", "rule16_enumeration",
                                   "G0e_anchors")}, indent=2, default=str))
    print(f"rule13 triggered={len(stability)} boundary={len(boundary)}")


def write_manifest(stage_times: dict[str, float]) -> None:
    path = OUT / "manifest.json"
    prior = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    prior.setdefault("leg", "M4-K2e")
    prior.setdefault("banner", BANNER)
    prior.setdefault("script", "scripts/run_suica_m4_k2e_double_matching.py")
    prior.setdefault("master_seed", MASTER_SEED)
    prior.setdefault("worlds_per_arm_registered", WORLDS_PER_ARM)
    prior.setdefault("pilot_worlds", list(PILOT_WORLDS))
    prior.setdefault("dm_targets", [list(p) for p in DM_TARGETS])
    prior.setdefault("vs_target", VS_TARGET)
    prior.setdefault("phi_a", PHI_A)
    prior.setdefault("phi_b", PHI_B)
    prior.setdefault("margins", {"M1": M1, "M2": M2})
    prior.setdefault("kappa_hat", KAPPA_HAT)
    prior.setdefault("l_vs_tolerance", L_VS_TOL)
    prior.setdefault("b_boot", B_BOOT)
    prior.setdefault("b_boot_high", B_BOOT_HIGH)
    prior.setdefault("python", sys.version)
    prior.setdefault("numpy", np.__version__)
    prior.setdefault("pandas", pd.__version__)
    prior.setdefault("stage_seconds", {})
    prior["stage_seconds"].update(stage_times)
    prior["updated_utc"] = datetime.now(UTC).isoformat()
    path.write_text(json.dumps(prior, indent=2, default=str) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, choices=("part0", "arms", "finalize"))
    parser.add_argument("--worlds", default=None, help="world range 'a-b' (chunking)")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.stage == "part0":
        run_part0(args)
    elif args.stage == "arms":
        run_arms(args)
    else:
        run_finalize(args)


if __name__ == "__main__":
    main()
