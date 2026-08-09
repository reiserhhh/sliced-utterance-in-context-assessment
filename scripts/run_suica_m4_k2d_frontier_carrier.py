#!/usr/bin/env python3
"""M4-K2d -- the frontier and the carrier: does the composition term cross
materiality at attenuation ~ 0.45, and which state SPECIES carries it?

Registered spec: docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md section "M4-K2d -- The
frontier and the carrier ..." (REGISTERED 2026-08-09, BEFORE RUN, commit
9565e5f), together with the K2c OUTCOME and planner adjudication immediately
above it (defect #21, standing rule 15, the dual margins, q = 1.9337620539521978).
Theory: docs/SUICA_IDENTITY_THEORY_V1.md T4 (S3), appendices I and J.

Executor standing: implementation and execution only.  Everything labelled
"RN-n" below is a register-note -- an operationalization of something the
registration left open (standing rule 9) -- fixed and written to
reports/SUICA_M4_K2D_FRONTIER_CARRIER_REPORT.md Part 0 BEFORE any main arm ran.

Reuse boundary (registration: "all machinery from K2b/K2c unchanged except the
SP-int arms carry w_int > 0"):
  * scripts/run_suica_m4_k2c_matched_pairs.py (k2c()) -- solve_share_for_target
    (k2c:193-221), bootstrap_card_pair (k2c:264-298), ols_slope (k2c:304-306),
    l3_pooled_q (k2c:309-350), T_QUANTILES/mde_paired (k2c:124-156), read_csv_rt
    (k2c:149-151), EQUIV_FLOOR/B_BOOT conventions.  Imported and CALLED
    UNMODIFIED.
  * scripts/run_suica_m4_k2b_t4_branch.py (k2b()) via k2c -- layout (k2b:238-293),
    retained_cell_sizes (k2b:296-300), build_k2b_world (k2b:316-353), emit_panel
    (k2b:359-381), card_channel_frame (k2b:392-457), pooled_card_stats
    (k2b:463-489), bootstrap_card (k2b:505-509), arm_shares (k2b:212-213),
    arm_predictions (k2b:533-584), run_field_world (k2b:607-704),
    field_from_vectors (k2b:592-604), CHANNELS/DIM/NOISE_SHARE/SIGNAL_SHARE.
  * suica_core/ is READ-ONLY and untouched.

THE INTERACTION CHANNEL (rule 12 -- generator SOURCE OBJECTS, not knob names).
K2d's only new physics is w_int > 0 in two arms.  Every object it uses is
already built, unconditionally, in every K2b world and was typed by K2a:
  * k2a:174-181 `shock_int_matrix(world_seed, occasion, k)` -- S(o) ~ N(0, I_k)
    on salt `m4k2a-shock-int`, DISJOINT from f2's `m4f2-shock`;
  * k2b:338-341 `a_load` -- a_i ~ N(0, I_k) on salt `m4k2b-loading`;
  * k2b:342-343 `u_int = einsum("ij,ojl->iol", a_load, shocks)/sqrt(k)`;
  * k2b:344 `s_int = A_SCALE * ((u_int * G_PROFILE) @ loadings.T)`;
  * k2b:374-375 emit_panel's `if "int" in active and w["int"] != 0.0` branch;
  * k2b:416 / k2b:425-426 card_channel_frame's `int_c` cell-centring and its
    entry into the two-split card;
  * k2b:537/549/559/562 arm_predictions' `C = sh["int"]`, entering the card
    variance as `C/m` (full set) and `C/half` (each split) -- i.e. the
    interaction channel is PERSON content that averages down like noise,
    which is exactly "occasion-bound, zero-persistence person content".
The ONE new object is the arm-weight parameterization that lets an arm carry a
CHOSEN interaction share (k2b:198-210 admits only "zero"/"equal"); see
`install_species_weights()` below, a disclosed single-object dispatcher that
DELEGATES verbatim for "zero"/"equal" and is verified bit-exact against the
original in Part 0.

Stages (foreground, chunked, resumable; artifacts under
results/m4_k2d_frontier_carrier/):
  --stage part0     solved shares (FR pair + two species pairs), every
                    prediction, the rule-15 ENUMERATION of the adjudication
                    space, and G0d'..G5d' on RESERVED pilot worlds 9801-9802.
                    `arms` refuses to run unless every Part-0 gate passes AND
                    the Part-0 report exists on disk.
  --stage arms      the 6 arms x (per-pair N) worlds, chunked by WORLD RANGE
                    (--worlds a-b); an arm runs a world index only if its
                    pair's selected N covers it (per-pair escalation).
  --stage finalize  G1d' post-arms matching, D per pair + CELL assignment,
                    L-F / L-S / L-M, q-update over 19 arms, rule-13 stability,
                    pivots, decision.json.
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
MASTER_SEED = 20260818             # registration: "master_seed 20260818"
WORLDS_PER_ARM = 32                # registration: "32 worlds/arm"
ESCALATION_LADDER = (32, 64)       # registration G2d': "escalate 32->64 once per pair"
PILOT_WORLDS = (9801, 9802)        # RESERVED; disjoint from main indices 0..63
B_BOOT = 2000                      # registration G3d': "B=2000, seed=master"
B_BOOT_HIGH = 20000                # registration G3d': ">=10xB" (rule 13)

PHI_A, PHI_B = 0.90, 0.98
FR_TARGET = 0.45                   # registration: "target attenuation ~ 0.45"
SP_TARGETS: tuple[tuple[str, float], ...] = (("SP-68", 0.68), ("SP-56", 0.56))
FR_PAIR = "FR-45"

# registration, dual margins: "M1 = 0.020, M2 = 0.010"
M1 = 0.020
M2 = 0.010
# registration G1d': predicted <= 1e-12; measured pooled CI inside +/-0.005
MATCH_TOL_PART0 = 1e-12
MATCH_TOL_MEASURED = 0.005
# registration G2d': "MDE(80%, a=.05, paired, n=32) <= 0.010 for the species
# pairs and <= 0.020 for FR-45"
MDE_TARGET_BY_PAIR = {"FR-45": 0.020, "SP-68": 0.010, "SP-56": 0.010}

# RN-1 (rule 9 -- THE ONE DESIGN PARAMETER THE REGISTRATION LEAVES FREE).
# "SP-68-int (mixed species: smaller slow share s68' + w_int chosen so predicted
# attenuation matches SP-68-slow's)" fixes ONE equation (the match) on TWO
# unknowns (s', w_int), so s' must be pinned by a written rule.  The
# registration's own words bound it from both sides: "mixed species" excludes
# s' = 0 (that would be int-ONLY, not mixed), and "smaller" excludes s' = s.
# FIXED, before any world was built: s' = s/2 -- the half-trade, the unique
# scale-free interior fraction, and the one that maximizes the species contrast
# subject to keeping the arm genuinely mixed.  A Part-0 SENSITIVITY table
# (pure card algebra, no worlds, no field numbers) reports the solved
# interaction share at f in {0.25, 0.50, 0.75} so the reader can see what the
# other conventions would have bought at card level.
TRADE_FRACTION = 0.5

# RN-2 (rule 9 -- "CI lower(|D|)").  |D|'s interval lower endpoint is
# min(|lo|,|hi|) when the D-interval excludes 0, and EXACTLY 0 when it includes
# 0 (0 is then an admissible value of |D|).  With this definition the MAT-SIG
# sub-clause "CI lower(|D|) >= M2" implies "CI excludes 0", which is what makes
# the enumeration table's first column non-redundant.  Fixed before any
# hypothesis number; the enumeration in Part 0 is run under it.

# RN-3 (rule 9 -- interval-inclusion endpoints).  "CI inside +/-M" is
# INCLUSIVE: -M <= lo and hi <= M.  ">= M" is inclusive.  Ties therefore fall on
# the null/material side as the symbols are written.

# RN-4: K2b's arm-independent reader efficiency, used ONLY as the q-update's
# intercept scale.  The OLS slope is invariant to lambda; verified numerically.
K2B_LAMBDA = 0.17417497661611914

OUT = ROOT / "results" / "m4_k2d_frontier_carrier"
REPORT = ROOT / "reports" / "SUICA_M4_K2D_FRONTIER_CARRIER_REPORT.md"
K2C_OUT = ROOT / "results" / "m4_k2c_matched_pairs"
K2B_OUT = ROOT / "results" / "m4_k2b_t4_branch"
K2B_PRIMARY_ARMS = ("A1", "A2", "A3", "A4", "A5", "A6")
K2C_MASTER_SEED = 20260817

_K2C: Any = None
_ORIG_ARM_WEIGHTS: Any = None


def k2c() -> Any:
    global _K2C
    if _K2C is None:
        path = ROOT / "scripts" / "run_suica_m4_k2c_matched_pairs.py"
        spec = importlib.util.spec_from_file_location("run_suica_m4_k2c_matched_pairs", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _K2C = module
    return _K2C


def k2b() -> Any:
    return k2c().k2b()


def read_csv_rt(path: Path) -> pd.DataFrame:
    """G5d': every artifact re-read with float_precision='round_trip'."""
    return k2c().read_csv_rt(path)


def mde_paired(sd_diff: float, n: int) -> float:
    return k2c().mde_paired(sd_diff, n)


def world_seed_for(world: int) -> int:
    """RN-5: K2d's OWN seed lineage (master_seed 20260818, salt 'm4k2d-world').
    The seed depends on the WORLD INDEX ONLY, so every arm -- including the two
    arms of a pair, which differ in share / phi / w_int -- shares the trait b,
    the AR innovations, the frame shocks, the interaction loadings a_i and the
    noise bit-for-bit.  Every within-pair D is therefore a within-world
    difference."""
    return int(
        v8.stable_bucket(f"{MASTER_SEED}-{world}", salt="m4k2d-world", modulus=2**31 - 1)
    )


def run_field_world(arm_id: str, world_index: int, world, w, *, verify: bool = False):
    """RN-6 (provenance): k2b.run_field_world is called UNMODIFIED, so the corpus
    tag it builds keeps the literal prefix 'm4k2b-'.  The tag is a hash label
    seeding the deployed transition-null permutation streams (f1:199-206);
    prefixing every K2d arm id with 'K2D-' makes every tag DISJOINT from every
    K2b and K2c tag.  The returned row's 'arm' field is rewritten to the clean
    K2d id."""
    row = k2b().run_field_world(f"K2D-{arm_id}", world_index, world, w, verify=verify)
    row["arm"] = arm_id
    return row


# ---------------------------------------------------------------------------
# The ONE new generator-facing object: an arm weight vector with a CHOSEN
# interaction share.  DISCLOSED single-object dispatcher (the K1/K2b precedent
# for `k2a_pooled_stats_patched`), installed on k2b so that arm_shares
# (k2b:212-213) and arm_predictions (k2b:533-584) inherit it unchanged.

def install_species_weights() -> None:
    global _ORIG_ARM_WEIGHTS
    module = k2b()
    if _ORIG_ARM_WEIGHTS is not None:
        return
    _ORIG_ARM_WEIGHTS = module.arm_weights
    original = _ORIG_ARM_WEIGHTS
    signal, noise = module.SIGNAL_SHARE, module.NOISE_SHARE

    def dispatch(share: float, w_int_arm: str) -> dict[str, float]:
        """k2b:198-210 generalized: the state-species parameterization.

        Non-noise signal variance V_s = 1 - w_e^2 = 0.30 is held FIXED (k2b
        RN-3).  `share` is the SLOW (persistent, AR(phi)) fraction of V_s;
        `int_share` is the INTERACTION (occasion-bound, zero-persistence)
        fraction of V_s; the remaining (1 - share - int_share) V_s is split
        EQUALLY over {mu, common}, preserving F2's 1:1 trait:frame ratio at
        kappa = 1.0 exactly as k2b's "zero" arm does.  Reduces to k2b's "zero"
        at int_share = 0 and to k2b's "equal" at int_share = (1-share)/3."""
        if isinstance(w_int_arm, str) and w_int_arm.startswith("int:"):
            t = float(w_int_arm[4:])
            rest = (1.0 - share - t) * signal
            if rest < 0.0:
                raise SystemExit(
                    f"REFUSED: slow {share!r} + int {t!r} exceeds the signal budget"
                )
            shares = {"mu": rest / 2.0, "slow": share * signal, "int": t * signal,
                      "common": rest / 2.0, "noise": noise}
            return {name: math.sqrt(value) for name, value in shares.items()}
        return original(share, w_int_arm)

    module.arm_weights = dispatch


def verify_species_weights() -> dict[str, Any]:
    """Part-0 proof that the dispatcher is the original on the original's
    domain (bit-exact) and the documented generalization off it."""
    module = k2b()
    grid = [0.0, 0.02, 0.1, 0.25, 0.29267462506992153, 0.4973617623232523, 0.6, 0.9]
    zero_exact = True
    zero_route_exact = True
    equal_dev = 0.0
    for s in grid:
        a = _ORIG_ARM_WEIGHTS(s, "zero")
        b = module.arm_weights(s, "zero")
        c = module.arm_weights(s, "int:0.0")
        zero_exact &= all(a[k] == b[k] for k in a)
        zero_route_exact &= all(a[k] == c[k] for k in a)
        e0 = _ORIG_ARM_WEIGHTS(s, "equal")
        t_equal = (1.0 - s) / 3.0
        e1 = module.arm_weights(s, f"int:{t_equal!r}")
        equal_dev = max(equal_dev, max(abs(e0[k] - e1[k]) for k in e0))
    return {
        "grid_shares": grid,
        "zero_arm_bit_exact_after_patch": bool(zero_exact),
        "int_zero_route_equals_zero_arm_bit_exact": bool(zero_route_exact),
        "equal_arm_max_abs_deviation": float(equal_dev),
        "note": ("the dispatcher DELEGATES verbatim for 'zero'/'equal'; the "
                 "'int:t' route reproduces 'zero' bit-exactly at t=0 and 'equal' "
                 "to the reported floating-point deviation at t=(1-s)/3 (a "
                 "different arithmetic order for the same quantity)"),
    }


# ---------------------------------------------------------------------------
# PART 0, step 1: the SOLVED shares (the designed identity).

def predicted_attenuation(slow_share: float, int_share: float, phi: float) -> float:
    """r(card -> b) from the K2a-validated attenuation algebra (k2b:533-584,
    max relative error 0.30% over K2a's 12 cells), evaluated on THIS panel's
    (context, m) norm cells.  Pure algebra: no world is generated."""
    arm = "zero" if int_share == 0.0 else f"int:{int_share!r}"
    return float(k2b().arm_predictions(slow_share, phi, arm)["r_card_b_pred_raw"])


def solve_slow_for_target(target: float, phi: float) -> dict[str, float]:
    """Bisection to adjacent doubles on the SLOW share at w_int = 0
    (k2c:193-221, reproduced here only because k2c's helper hard-codes the
    'zero' arm string; the algebra called is identical)."""
    lo, hi = 0.0, 0.999999
    r_lo, r_hi = predicted_attenuation(lo, 0.0, phi), predicted_attenuation(hi, 0.0, phi)
    if not (r_hi <= target <= r_lo):
        raise SystemExit(
            f"REFUSED: target {target!r} outside the attainable range "
            f"[{r_hi!r}, {r_lo!r}] at phi={phi!r}, w_int=0"
        )
    iters = 0
    while iters < 400:
        mid = 0.5 * (lo + hi)
        if mid <= lo or mid >= hi:
            break
        if predicted_attenuation(mid, 0.0, phi) > target:
            lo = mid
        else:
            hi = mid
        iters += 1
    cand = min((lo, hi), key=lambda s: abs(predicted_attenuation(s, 0.0, phi) - target))
    return {"share": float(cand), "int_share": 0.0,
            "attenuation": predicted_attenuation(cand, 0.0, phi),
            "target": float(target),
            "abs_error_vs_target": abs(predicted_attenuation(cand, 0.0, phi) - target),
            "bisection_iterations": iters, "bracket_width_final": float(hi - lo)}


def solve_int_for_target(target: float, slow_share: float, phi: float) -> dict[str, float]:
    """Bisection to adjacent doubles on the INTERACTION share at a fixed slow
    share.  r is strictly decreasing in the interaction share: raising t both
    lowers the trait share A = (1-s-t)V_s/2 and adds C/m to the card variance,
    so the bracket [0, 1-s] is unconditional."""
    lo, hi = 0.0, max(0.0, 1.0 - slow_share - 1e-9)
    r_lo = predicted_attenuation(slow_share, lo, phi)
    r_hi = predicted_attenuation(slow_share, hi, phi)
    if not (r_hi <= target <= r_lo):
        raise SystemExit(
            f"REFUSED: target {target!r} outside the attainable interaction range "
            f"[{r_hi!r}, {r_lo!r}] at slow={slow_share!r}, phi={phi!r}"
        )
    iters = 0
    while iters < 400:
        mid = 0.5 * (lo + hi)
        if mid <= lo or mid >= hi:
            break
        if predicted_attenuation(slow_share, mid, phi) > target:
            lo = mid
        else:
            hi = mid
        iters += 1
    cand = min((lo, hi),
               key=lambda t: abs(predicted_attenuation(slow_share, t, phi) - target))
    return {"share": float(slow_share), "int_share": float(cand),
            "attenuation": predicted_attenuation(slow_share, cand, phi),
            "target": float(target),
            "abs_error_vs_target": abs(predicted_attenuation(slow_share, cand, phi) - target),
            "bisection_iterations": iters, "bracket_width_final": float(hi - lo)}


def solve_fr_pair() -> dict[str, Any]:
    """FR-45: (s4a, phi .90, w_int 0) vs (s4b, phi .98, w_int 0), the K2c-series
    pair pushed to attenuation ~ 0.45.  Arm b is solved to arm a's ACHIEVED
    attenuation, so the within-pair predicted difference is bounded by the
    solver's own resolution."""
    a = solve_slow_for_target(FR_TARGET, PHI_A)
    b = solve_slow_for_target(a["attenuation"], PHI_B)
    diff = a["attenuation"] - b["attenuation"]
    return {
        "pair": FR_PAIR, "kind": "frontier", "target_attenuation": float(FR_TARGET),
        "arm_a": {"arm": "FR45a", "share": a["share"], "int_share": 0.0, "phi": PHI_A,
                  "predicted_attenuation": a["attenuation"],
                  "bisection_iterations": a["bisection_iterations"],
                  "bracket_width_final": a["bracket_width_final"]},
        "arm_b": {"arm": "FR45b", "share": b["share"], "int_share": 0.0, "phi": PHI_B,
                  "predicted_attenuation": b["attenuation"],
                  "bisection_iterations": b["bisection_iterations"],
                  "bracket_width_final": b["bracket_width_final"]},
        "share_gap_b_minus_a": b["share"] - a["share"],
        "predicted_attenuation_difference": diff,
        "abs_predicted_difference": abs(diff),
        "matched_part0": bool(abs(diff) <= MATCH_TOL_PART0),
        "arm_a_abs_error_vs_target": a["abs_error_vs_target"],
        "sign_convention": "D = field(phi .90 arm) - field(phi .98 arm)",
    }


def solve_species_pair(pair_id: str, target: float) -> dict[str, Any]:
    """SP-<t>: (s, phi .90, w_int 0) vs (RN-1's s/2, phi .90, w_int solved so the
    PREDICTED attenuation equals the slow twin's)."""
    a = solve_slow_for_target(target, PHI_A)
    s_prime = TRADE_FRACTION * a["share"]
    b = solve_int_for_target(a["attenuation"], s_prime, PHI_A)
    diff = a["attenuation"] - b["attenuation"]
    return {
        "pair": pair_id, "kind": "species", "target_attenuation": float(target),
        "arm_a": {"arm": f"{pair_id.replace('-', '')}slow", "share": a["share"],
                  "int_share": 0.0, "phi": PHI_A,
                  "predicted_attenuation": a["attenuation"],
                  "bisection_iterations": a["bisection_iterations"],
                  "bracket_width_final": a["bracket_width_final"]},
        "arm_b": {"arm": f"{pair_id.replace('-', '')}int", "share": b["share"],
                  "int_share": b["int_share"], "phi": PHI_A,
                  "predicted_attenuation": b["attenuation"],
                  "bisection_iterations": b["bisection_iterations"],
                  "bracket_width_final": b["bracket_width_final"]},
        "trade_fraction_RN1": TRADE_FRACTION,
        "slow_share_removed": a["share"] - b["share"],
        "interaction_share_added": b["int_share"],
        "exchange_rate_int_per_slow": (b["int_share"] / (a["share"] - b["share"])
                                       if a["share"] != b["share"] else float("nan")),
        "predicted_attenuation_difference": diff,
        "abs_predicted_difference": abs(diff),
        "matched_part0": bool(abs(diff) <= MATCH_TOL_PART0),
        "arm_a_abs_error_vs_target": a["abs_error_vs_target"],
        "sign_convention": "D = field(slow arm) - field(int arm)",
    }


def trade_sensitivity() -> list[dict[str, Any]]:
    """RN-1's disclosure: pure card algebra at other trade fractions (no world
    is built, no field number exists)."""
    rows: list[dict[str, Any]] = []
    for pid, tgt in SP_TARGETS:
        a = solve_slow_for_target(tgt, PHI_A)
        for f in (0.25, 0.50, 0.75):
            s_prime = f * a["share"]
            b = solve_int_for_target(a["attenuation"], s_prime, PHI_A)
            sh = k2b().arm_shares(b["share"], f"int:{b['int_share']!r}")
            rows.append({"pair": pid, "trade_fraction": f, "slow_share_slow_arm": a["share"],
                         "slow_share_int_arm": s_prime, "int_share_solved": b["int_share"],
                         "abs_predicted_difference": abs(a["attenuation"] - b["attenuation"]),
                         "realized_variance_share_int": sh["int"],
                         "realized_variance_share_slow": sh["slow"],
                         "selected_RN1": bool(f == TRADE_FRACTION)})
    return rows


# ---------------------------------------------------------------------------
# The rule-15 adjudication space: the ENUMERATION IS THE SPACE.

CELL_ORDER = ("MAT-SIG(+)", "MAT-SIG(-)", "SUB-SIG(+)", "SUB-SIG(-)",
              "NULL", "WEAK-NULL", "INDET")


def clause_vector(point: float, lo: float, hi: float,
                  m1: float = M1, m2: float = M2) -> dict[str, bool]:
    excludes_zero = bool(lo > 0.0 or hi < 0.0)
    abs_lower = min(abs(lo), abs(hi)) if excludes_zero else 0.0   # RN-2
    return {
        "c1_ci_excludes_zero": excludes_zero,
        "c2_point_abs_ge_M1": bool(abs(point) >= m1),
        "c3_abs_lower_ge_M2": bool(abs_lower >= m2),
        "c4_ci_inside_M2": bool(-m2 <= lo and hi <= m2),
        "c5_ci_inside_M1": bool(-m1 <= lo and hi <= m1),
        # c6 carries the SIGN, which the registration's table folds into the cell
        # NAME ("MAT-SIG(sign)").  Without it the truth table is under-specified
        # and two opposite-sign results would share a row.
        "c6_D_positive": bool(point > 0.0),
    }


def assign_cell(point: float, lo: float, hi: float,
                m1: float = M1, m2: float = M2) -> str:
    """The registration's enumeration table, verbatim.

    | CI vs 0    | further test                              | cell          |
    | excludes 0 | |D| point >= M1 AND CI lower(|D|) >= M2   | MAT-SIG(sign) |
    | excludes 0 | otherwise                                 | SUB-SIG(sign) |
    | includes 0 | CI subset of +/-M2                        | NULL          |
    | includes 0 | CI subset of +/-M1 but not of +/-M2       | WEAK-NULL     |
    | includes 0 | CI not a subset of +/-M1                  | INDET         |
    """
    c = clause_vector(point, lo, hi, m1, m2)
    if c["c1_ci_excludes_zero"]:
        sign = "+" if lo > 0.0 else "-"
        base = "MAT-SIG" if (c["c2_point_abs_ge_M1"] and c["c3_abs_lower_ge_M2"]) else "SUB-SIG"
        return f"{base}({sign})"
    if c["c4_ci_inside_M2"]:
        return "NULL"
    if c["c5_ci_inside_M1"]:
        return "WEAK-NULL"
    return "INDET"


def base_of(cell: str) -> str:
    return cell.split("(")[0]


def sign_of(cell: str) -> int:
    if cell.endswith("(+)"):
        return 1
    if cell.endswith("(-)"):
        return -1
    return 0


def enumerate_cell_space() -> dict[str, Any]:
    """Rule 15: a truth table over ALL clause combinations, each assigned to
    exactly one named outcome; overlaps and gaps are registration defects.

    The per-pair table is verified by (i) an exhaustive 2^5 truth table whose
    realizability is decided by a dense numeric search, and (ii) the resulting
    combination -> cell map being single-valued and covering every cell."""
    grid = sorted(set(
        [round(x, 6) for x in np.linspace(-0.06, 0.06, 121)]
        + [-M1, M1, -M2, M2, 0.0, -M1 - 1e-9, M1 + 1e-9, -M2 - 1e-9, M2 + 1e-9,
           -M1 + 1e-9, M1 - 1e-9, -M2 + 1e-9, M2 - 1e-9]
    ))
    combo_to_cells: dict[tuple[bool, ...], set[str]] = {}
    cells_seen: dict[str, int] = {}
    n_triples = 0
    for lo in grid:
        for hi in grid:
            if hi < lo:
                continue
            for point in (lo, hi, 0.5 * (lo + hi)):
                n_triples += 1
                c = clause_vector(point, lo, hi)
                key = tuple(c.values())
                cell = assign_cell(point, lo, hi)
                combo_to_cells.setdefault(key, set()).add(cell)
                cells_seen[cell] = cells_seen.get(cell, 0) + 1
    keys = list(clause_vector(0.0, 0.0, 0.0).keys())
    n_clauses = len(keys)
    table: list[dict[str, Any]] = []
    overlaps = 0
    realizable = 0
    for bits in range(2 ** n_clauses):
        combo = tuple(bool((bits >> i) & 1) for i in range(n_clauses))
        cells = sorted(combo_to_cells.get(combo, set()))
        row = {keys[i]: combo[i] for i in range(n_clauses)}
        row["realizable"] = bool(cells)
        row["cells"] = cells
        row["n_cells"] = len(cells)
        if cells:
            realizable += 1
        if len(cells) > 1:
            overlaps += 1
        table.append(row)
    return {
        "criterion": ("every realizable clause combination maps to EXACTLY ONE cell "
                      "(no overlap), the map is total (no gap), and all seven signed "
                      "cells are realized"),
        "n_triples_searched": n_triples,
        "n_clauses": n_clauses,
        "n_combinations": 2 ** n_clauses,
        "n_realizable": realizable,
        "n_overlapping": overlaps,
        "cells_realized": sorted(cells_seen),
        "cells_realized_counts": cells_seen,
        "all_seven_cells_realized": bool(set(cells_seen) == set(CELL_ORDER)),
        "map_is_total": True,
        "map_is_single_valued": bool(overlaps == 0),
        "truth_table": table,
        "PASS": bool(overlaps == 0 and set(cells_seen) == set(CELL_ORDER)),
    }


def ls_outcomes(cell_68: str, cell_56: str) -> list[str]:
    """The registration's L-S predicates, applied literally (no precedence
    invented).  Returns EVERY registered outcome whose predicate is true."""
    cells = (cell_68, cell_56)
    bases = tuple(base_of(c) for c in cells)
    sig = [c for c in cells if base_of(c) in ("MAT-SIG", "SUB-SIG")]
    nul = [c for c in cells if base_of(c) in ("NULL", "WEAK-NULL")]
    ind = [c for c in cells if base_of(c) == "INDET"]
    out: list[str] = []
    if len(nul) == 2:
        out.append("SPECIES-GENERAL")
    if len(sig) >= 1 and len({sign_of(c) for c in sig}) == 1:
        out.append("SPECIES-SPECIFIC")
    if (len(sig) >= 2 and len({sign_of(c) for c in sig}) > 1) or (len(sig) == 1 and len(ind) == 1):
        out.append("SPECIES-MIXED")
    if len(ind) == 2:
        out.append("SPECIES-UNDERPOWERED")
    del bases
    return out


def enumerate_ls_space() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    gaps: list[tuple[str, str]] = []
    overlaps: list[tuple[str, str]] = []
    for a in CELL_ORDER:
        for b in CELL_ORDER:
            outs = ls_outcomes(a, b)
            rows.append({"SP-68": a, "SP-56": b, "outcomes": outs, "n": len(outs)})
            if not outs:
                gaps.append((a, b))
            elif len(outs) > 1:
                overlaps.append((a, b))
    return {
        "n_combinations": len(rows),
        "n_unique": sum(1 for r in rows if r["n"] == 1),
        "n_gap": len(gaps),
        "n_overlap": len(overlaps),
        "gap_combinations": [list(g) for g in gaps],
        "overlap_combinations": [list(o) for o in overlaps],
        "rows": rows,
        "PASS": bool(not gaps and not overlaps),
    }


def enumerate_pivot_space() -> dict[str, Any]:
    routing = {
        "MAT-SIG(-)": ["P2d''"],
        "NULL": ["P3d''"], "WEAK-NULL": ["P3d''"],
        "SUB-SIG(+)": ["P4d''"], "SUB-SIG(-)": ["P4d''"], "INDET": ["P4d''"],
    }
    rows = [{"FR-45 cell": c, "pivot": routing.get(c, []), "n": len(routing.get(c, []))}
            for c in CELL_ORDER]
    gaps = [r["FR-45 cell"] for r in rows if r["n"] == 0]
    overlaps = [r["FR-45 cell"] for r in rows if r["n"] > 1]
    return {"rows": rows, "n_gap": len(gaps), "gap_cells": gaps,
            "n_overlap": len(overlaps), "overlap_cells": overlaps,
            "PASS": bool(not gaps and not overlaps)}


# RN-7 (rule 9 + rule 15, fixed BEFORE any hypothesis number).  The Part-0
# enumeration is run FIRST; these are the pre-declared readings for the
# combinations the registration's LEAN-level predicates fail to partition.
# They follow K2c's RN-4 precedent exactly (the standing convention in this
# line for a result that fits no registered branch, or more than one):
#   * FR-45 == MAT-SIG(+)  -> no pivot is routed: L-F MISSES and the outcome is
#     the NAMED NON-REGISTERED cell `FRONTIER-SIGN-REVERSAL`, reported as such;
#     T4 is not re-typed on it.
#   * SP cells (SIG, INDET) in either order -> SPECIES-SPECIFIC and
#     SPECIES-MIXED BOTH fire -> NAMED NON-REGISTERED outcome
#     `SPECIES-BOTH-FIRE`, both readings reported, no L-S branch claimed.
#   * SP cells (NULL/WEAK-NULL, INDET) in either order -> no registered outcome
#     -> NAMED NON-REGISTERED outcome `SPECIES-PARTIAL-UNDERPOWERED`
#     (one pair bounded null, one pair unresolved), reported as such.

def score_ls(cell_68: str, cell_56: str) -> dict[str, Any]:
    outs = ls_outcomes(cell_68, cell_56)
    if len(outs) == 1:
        verdict, status = outs[0], "REGISTERED"
    elif len(outs) > 1:
        verdict, status = "SPECIES-BOTH-FIRE", "NAMED_NON_REGISTERED_OVERLAP"
    else:
        verdict, status = "SPECIES-PARTIAL-UNDERPOWERED", "NAMED_NON_REGISTERED_GAP"
    return {"cell_SP68": cell_68, "cell_SP56": cell_56,
            "registered_predicates_true": outs, "verdict": verdict, "status": status}


def score_frontier(cell_fr: str) -> dict[str, Any]:
    l_f = bool(cell_fr == "MAT-SIG(-)")
    if l_f:
        pivot, status = "P2d''", "REGISTERED"
    elif cell_fr in ("NULL", "WEAK-NULL"):
        pivot, status = "P3d''", "REGISTERED"
    elif cell_fr in ("SUB-SIG(+)", "SUB-SIG(-)", "INDET"):
        pivot, status = "P4d''", "REGISTERED"
    else:
        pivot, status = "FRONTIER-SIGN-REVERSAL", "NAMED_NON_REGISTERED_GAP"
    return {"cell": cell_fr, "L_F_holds": l_f, "pivot": pivot, "status": status}


# ---------------------------------------------------------------------------
# The q-update: pooled log-log slope over all 19 arms (DESCRIPTIVE, no gate).

def pooled_q(groups: list[tuple[np.ndarray, list[np.ndarray]]], lam: float,
             b_draws: int, seed: int) -> dict[str, Any]:
    """`groups` = [(x_log for the group's arms, [per-arm per-world field arrays])].
    Worlds are resampled in BLOCKS within each group, shared across that group's
    arms (they are world-paired by construction).  Draw order is one rng
    consumed group by group -- identical to k2c:309-350 for two groups, verified
    bit-exactly in Part 0's G0d'."""
    x = np.concatenate([g[0] for g in groups])
    y_point = np.log(np.concatenate(
        [np.array([float(np.mean(f)) for f in g[1]]) for g in groups]) / lam)
    q_point = k2c().ols_slope(x, y_point)
    rng = np.random.default_rng(seed)
    mats = []
    for x_g, fields in groups:
        n_g = len(fields[0])
        pick = rng.integers(0, n_g, size=(b_draws, n_g))
        mats.append(np.stack([f[pick].mean(axis=1) for f in fields], axis=1))
        del x_g
    y_boot = np.log(np.concatenate(mats, axis=1) / lam)
    xc = x - x.mean()
    q_boot = ((y_boot - y_boot.mean(axis=1, keepdims=True)) @ xc) / (xc @ xc)
    lo, hi = k2b().k2a().ci_of(q_boot)
    resid = y_point - (y_point.mean() + q_point * xc)
    return {"q": q_point, "q_ci": [lo, hi], "q_boot": q_boot,
            "n_points": int(len(x)),
            "r2": float(1.0 - (resid @ resid)
                        / ((y_point - y_point.mean()) @ (y_point - y_point.mean()))),
            "one_sided_lower95": float(np.percentile(q_boot, 5.0)),
            "clause_q_gt_1": bool(q_point > 1.0),
            "clause_ci_excludes_1": bool(lo > 1.0 or hi < 1.0),
            "lambda": float(lam)}


# ---------------------------------------------------------------------------
# G0d': the anchors, re-derived bit-exactly from persisted artifacts.

def rederive_anchors() -> dict[str, Any]:
    m = k2b()
    k2a = m.k2a()
    kc = k2c()
    out: dict[str, Any] = {}

    # --- K2b's A1/A4 fields and lambda, by K2c's own G0c' route
    k2b_dec = json.loads((K2B_OUT / "decision.json").read_text(encoding="utf-8"))
    k2b_pred = read_csv_rt(K2B_OUT / "part0_predictions.csv").set_index("arm")
    k2b_field = {a: read_csv_rt(K2B_OUT / f"arm_{a}_field.csv").sort_values("world")[
        "recovery_b_only"].to_numpy(float) for a in K2B_PRIMARY_ARMS}
    rec_a1 = float(np.mean(k2b_field["A1"]))
    rec_a4 = float(np.mean(k2b_field["A4"]))
    pred_att_k2b = np.array([float(k2b_pred.loc[a, "r_card_b_pred_raw"])
                             for a in K2B_PRIMARY_ARMS])
    meas_rec = np.array([float(np.mean(k2b_field[a])) for a in K2B_PRIMARY_ARMS])
    lam_re = float(np.mean(meas_rec) / np.mean(pred_att_k2b))
    k2b_persisted = {
        "A1_field_recovery": k2b_dec["second_readings"]["per_arm_field_recovery"]["A1"]["b_only_mean"],
        "A4_field_recovery": k2b_dec["second_readings"]["per_arm_field_recovery"]["A4"]["b_only_mean"],
        "lambda": k2b_dec["second_readings"]["efficiency_normalized_descriptive"]["lambda"],
    }
    k2b_rederived = {"A1_field_recovery": rec_a1, "A4_field_recovery": rec_a4,
                     "lambda": lam_re}
    out["k2b"] = {
        "persisted": k2b_persisted, "rederived": k2b_rederived,
        "residual": {k: k2b_rederived[k] - k2b_persisted[k] for k in k2b_persisted},
        "bit_exact": {k: bool(k2b_rederived[k] == k2b_persisted[k]) for k in k2b_persisted},
        "all_bit_exact": bool(all(k2b_rederived[k] == k2b_persisted[k] for k in k2b_persisted)),
        "lambda_constant_in_script": K2B_LAMBDA,
        "lambda_constant_matches": bool(lam_re == K2B_LAMBDA),
    }

    # --- K2c's three D_k with CIs and the pooled q with CI
    k2c_dec = json.loads((K2C_OUT / "decision.json").read_text(encoding="utf-8"))
    k2c_arms = json.loads((K2C_OUT / "part0_arms.json").read_text(encoding="utf-8"))
    n_c = int(k2c_dec["worlds_per_arm"])
    order_c = tuple(a["arm"] for a in k2c_arms["arms"])
    k2c_field = {
        a: pd.concat([read_csv_rt(p) for p in sorted(K2C_OUT.glob(f"arm_{a}_field_w*.csv"))],
                     ignore_index=True).sort_values("world")["recovery_b_only"].to_numpy(float)
        for a in order_c}
    k2c_mixed = {
        a: pd.concat([read_csv_rt(p) for p in sorted(K2C_OUT.glob(f"arm_{a}_field_w*.csv"))],
                     ignore_index=True).sort_values("world")["recovery_mixed"].to_numpy(float)
        for a in order_c}
    pick_c = np.random.default_rng(K2C_MASTER_SEED).integers(0, n_c, size=(kc.B_BOOT, n_c))
    boot_c = {a: k2c_field[a][pick_c].mean(axis=1) for a in order_c}
    d_rows = []
    for pr in k2c_arms["pairs"]:
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        d = k2c_field[ida] - k2c_field[idb]
        lo, hi = k2a.ci_of(boot_c[ida] - boot_c[idb])
        persisted = next(r for r in k2c_dec["pair_differences"] if r["pair"] == pr["pair"])
        d_rows.append({
            "pair": pr["pair"],
            "persisted_D": persisted["D_k"], "rederived_D": float(np.mean(d)),
            "residual_D": float(np.mean(d)) - persisted["D_k"],
            "persisted_ci": persisted["ci"], "rederived_ci": [lo, hi],
            "residual_ci": [lo - persisted["ci"][0], hi - persisted["ci"][1]],
            "bit_exact": bool(float(np.mean(d)) == persisted["D_k"]
                              and lo == persisted["ci"][0] and hi == persisted["ci"][1]),
        })
    k2c_preds = read_csv_rt(K2C_OUT / "part0_predictions.csv").set_index("arm")
    x_pred = np.log(np.array(
        [float(k2b_pred.loc[a, "r_card_b_pred_raw"]) for a in K2B_PRIMARY_ARMS]
        + [float(k2c_preds.loc[a, "r_card_b_pred_raw"]) for a in order_c]))
    q_re = kc.l3_pooled_q(x_pred, k2b_field, k2c_field, K2B_PRIMARY_ARMS, order_c,
                          K2B_LAMBDA, kc.B_BOOT, K2C_MASTER_SEED)
    q_persisted = k2c_dec["leans"]["L-3"]
    # the SAME fit through K2d's generalized `pooled_q` -- must be bit-identical
    q_gen = pooled_q(
        [(x_pred[:6], [k2b_field[a] for a in K2B_PRIMARY_ARMS]),
         (x_pred[6:], [k2c_field[a] for a in order_c])],
        K2B_LAMBDA, kc.B_BOOT, K2C_MASTER_SEED)
    out["k2c"] = {
        "worlds_per_arm": n_c, "arms": list(order_c),
        "pair_differences": d_rows,
        "all_D_bit_exact": bool(all(r["bit_exact"] for r in d_rows)),
        "q_persisted": q_persisted["q"], "q_rederived": q_re["q"],
        "q_residual": q_re["q"] - q_persisted["q"],
        "q_ci_persisted": q_persisted["q_ci"], "q_ci_rederived": q_re["q_ci"],
        "q_ci_residual": [q_re["q_ci"][0] - q_persisted["q_ci"][0],
                          q_re["q_ci"][1] - q_persisted["q_ci"][1]],
        "q_bit_exact": bool(q_re["q"] == q_persisted["q"]
                            and q_re["q_ci"][0] == q_persisted["q_ci"][0]
                            and q_re["q_ci"][1] == q_persisted["q_ci"][1]),
        "lambda_persisted": q_persisted["lambda"],
        "lambda_bit_exact": bool(q_persisted["lambda"] == K2B_LAMBDA),
        "generalized_pooled_q_matches_k2c": bool(
            q_gen["q"] == q_re["q"] and q_gen["q_ci"] == q_re["q_ci"]),
        "route": ("round-trip re-read of results/m4_k2c_matched_pairs/arm_*_field_w*.csv "
                  "and part0_predictions.csv; K2c's own l3_pooled_q called unmodified at "
                  "its own seed (20260817) and B (2000)"),
    }
    out["_k2b_field"] = k2b_field
    out["_k2b_pred_att"] = pred_att_k2b
    out["_k2c_field"] = k2c_field
    out["_k2c_mixed"] = k2c_mixed
    out["_k2c_x"] = x_pred
    out["_k2c_order"] = order_c
    out["all_bit_exact"] = bool(out["k2b"]["all_bit_exact"] and out["k2b"]["lambda_constant_matches"]
                                and out["k2c"]["all_D_bit_exact"] and out["k2c"]["q_bit_exact"]
                                and out["k2c"]["lambda_bit_exact"])
    return out


# ---------------------------------------------------------------------------
# Stage: part0

def arms_spec() -> list[dict[str, Any]]:
    path = OUT / "part0_arms.json"
    if not path.exists():
        raise SystemExit("REFUSED: results/m4_k2d_frontier_carrier/part0_arms.json missing.")
    return json.loads(path.read_text(encoding="utf-8"))["arms"]


def pairs_spec() -> list[dict[str, Any]]:
    path = OUT / "part0_arms.json"
    return json.loads(path.read_text(encoding="utf-8"))["pairs"]


def run_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    install_species_weights()
    m = k2b()
    lay = m.layout()
    gates: dict[str, Any] = {
        "leg": "M4-K2d",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "pilot_worlds": list(PILOT_WORLDS),
        "worlds_per_arm_registered": WORLDS_PER_ARM,
        "margins": {"M1": M1, "M2": M2},
        "noise_share": m.NOISE_SHARE,
        "signal_share": m.SIGNAL_SHARE,
        "rule14_self_check": (
            "NO GATE AND NO BRANCH LEAN IN THIS LEG COMPARES QUANTITIES ACROSS SCALES. "
            "G0d' re-derives K2b/K2c numbers against themselves; G1d' compares card "
            "attenuation to card attenuation; G2d'/G4d' and every cell assignment, L-F, "
            "L-S and L-M compare field agreement to field agreement (within-pair, same "
            "instrument, same units).  The single cross-scale object is the q-update, "
            "which the registration declares DESCRIPTIVE with NO GATE and which pins its "
            "own link (a log-log power law whose exponent q IS the estimand)."
        ),
        "rule12_source_objects": {
            "interaction shock stream S(o)": "k2a:174-181 shock_int_matrix, salt m4k2a-shock-int",
            "person loadings a_i": "k2b:338-341 a_load, salt m4k2b-loading",
            "u_int": "k2b:342-343", "s_int": "k2b:344",
            "panel emission of int": "k2b:374-375",
            "card centring of int": "k2b:416, 425-426",
            "prediction entry C/m, C/half": "k2b:537, 549, 559, 562",
            "arm weight generalization": "this script install_species_weights()",
        },
    }

    # ---- step 1: the SOLVED shares (pure algebra, before any world exists)
    t_shares = time.time()
    pairs = [solve_fr_pair()] + [solve_species_pair(pid, tgt) for pid, tgt in SP_TARGETS]
    sensitivity = trade_sensitivity()
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
                          "target_attenuation": a["target_attenuation"], **pred})
    preds = pd.DataFrame(pred_rows)
    preds.to_csv(OUT / "part0_predictions.csv", index=False)
    pd.DataFrame(sensitivity).to_csv(OUT / "part0_trade_sensitivity.csv", index=False)

    # ---- G0d': anchors, bit-exact
    anchors = rederive_anchors()
    k2b_field = anchors.pop("_k2b_field")
    k2b_pred_att = anchors.pop("_k2b_pred_att")
    k2c_field = anchors.pop("_k2c_field")
    anchors.pop("_k2c_mixed")
    k2c_x = anchors.pop("_k2c_x")
    k2c_order = anchors.pop("_k2c_order")
    anchors["criterion"] = (
        "K2c's three D_k AND their CIs, K2c's pooled q AND its CI, lambda, and K2b's "
        "A1/A4 field recoveries all re-derived from persisted artifacts (round-trip "
        "parsed) EQUAL bit-exactly"
    )
    anchors["weights_dispatcher"] = verify_species_weights()
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
    gates["G0d_prime"] = anchors

    # ---- G1d' (Part-0 half): the designed identity
    g1: dict[str, Any] = {
        "pairs": pairs,
        "tolerance_part0": MATCH_TOL_PART0,
        "tolerance_measured_post_arms": MATCH_TOL_MEASURED,
        "max_abs_predicted_difference": float(max(p["abs_predicted_difference"] for p in pairs)),
        "criterion_part0": "within-pair PREDICTED attenuation difference <= 1e-12 for 3/3 pairs",
        "criterion_post_arms": (
            "within-pair MEASURED card attenuation difference pooled 95% CI inside "
            "+/-0.005 (5x K2a's max attenuation error 0.00065); a pair failing the "
            "match is VOID for its claims"
        ),
        "part0_pass": bool(all(p["matched_part0"] for p in pairs)),
    }
    g1["pass"] = g1["part0_pass"]
    gates["G1d_prime"] = g1

    # ---- the rule-15 ENUMERATION (before any hypothesis number exists)
    enum_cell = enumerate_cell_space()
    enum_ls = enumerate_ls_space()
    enum_piv = enumerate_pivot_space()
    gates["rule15_enumeration"] = {
        "per_pair_cell_space": enum_cell,
        "L_S_predicate_space": enum_ls,
        "pivot_routing_space": enum_piv,
        "verdict": (
            "The PER-PAIR cell table IS a partition (verified by enumeration). "
            "The LEAN-level predicates are NOT: the L-S space has "
            f"{enum_ls['n_overlap']} OVERLAP and {enum_ls['n_gap']} GAP combinations of "
            f"{enum_ls['n_combinations']}, and the pivot routing leaves "
            f"{enum_piv['n_gap']} FR-45 cell(s) unrouted ({enum_piv['gap_cells']}). "
            "Recorded as a registration defect; RN-7 pre-declares the named "
            "non-registered readings BEFORE any hypothesis number."
        ),
        "RN7_readings": {
            "FR-45 == MAT-SIG(+)": "FRONTIER-SIGN-REVERSAL (named non-registered; L-F MISSES; no pivot)",
            "SP (SIG, INDET) either order": "SPECIES-BOTH-FIRE (named non-registered overlap; both readings reported)",
            "SP (NULL/WEAK-NULL, INDET) either order": "SPECIES-PARTIAL-UNDERPOWERED (named non-registered gap)",
        },
        "pass": bool(enum_cell["PASS"]),
    }

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
    frame_residual_max = 0.0
    for a in arms:
        w = m.arm_weights(a["share"], a["w_int_arm"])
        frames, rows = [], []
        for w_idx in PILOT_WORLDS:
            world = pilot_worlds[(w_idx, a["phi"])]
            frame, cres = m.card_channel_frame(world, w, world_seed_for(w_idx))
            frame_residual_max = max(frame_residual_max, cres)
            frames.append(frame)
            rows.append(run_field_world(a["arm"], w_idx, world, w,
                                        verify=(w_idx == PILOT_WORLDS[0])))
        pilot_card[a["arm"]] = pd.concat(frames, ignore_index=True)
        pilot_field[a["arm"]] = rows
        pilot_panels[a["arm"]] = m.emit_panel(pilot_worlds[(PILOT_WORLDS[0], a["phi"])], w)
        realized[a["arm"]] = rows[0]["realized_shares"]
    pilot_seconds = time.time() - t_pilot
    pilot_work_seconds = pilot_seconds - float(np.sum(build_times))

    # ---- G4d': liveness (rule 3) + within-pair non-degeneracy (rule 10)
    g4: dict[str, Any] = {"within_pair": [], "across_pair": {}, "interaction_channel": []}
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
    g4["interaction_live_in_all_int_arms"] = bool(all(r["live"] for r in int_arms))
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
    g4["realized_share_dev_abs_max"] = float(max(
        max(abs(realized[a["arm"]][k] - m.arm_shares(a["share"], a["w_int_arm"])[k])
            for k in m.arm_shares(a["share"], a["w_int_arm"]))
        for a in arms))
    g4["criterion"] = (
        "the interaction channel's REALIZED variance share is > 0 in both SP-int arms "
        "and exactly 0 in the four w_int=0 arms; within every pair the emitted panels "
        "differ (RMS > 1e-6); across the three designed attenuation levels the pilot "
        "card attenuation AND pilot field recovery both move per prediction (strictly "
        "increasing with the target); realized variance shares within 0.01 of design"
    )
    g4["pass"] = bool(g4["interaction_live_in_all_int_arms"]
                      and g4["interaction_exactly_zero_in_zero_arms"]
                      and all(r["non_degenerate"] for r in g4["within_pair"])
                      and g4["across_pair"]["card_strictly_increasing"]
                      and g4["across_pair"]["field_strictly_increasing"]
                      and g4["realized_share_dev_abs_max"] <= 0.01)
    gates["G4d_prime"] = g4

    # ---- G2d': power (rule 2), PER PAIR
    g2: dict[str, Any] = {"per_pair": [], "ladder": [],
                          "targets": dict(MDE_TARGET_BY_PAIR)}
    pilot_d: dict[str, np.ndarray] = {}
    for pr in pairs:
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        fa = np.array([r["recovery_b_only"] for r in pilot_field[ida]])
        fb = np.array([r["recovery_b_only"] for r in pilot_field[idb]])
        pilot_d[pr["pair"]] = fa - fb
    for n_worlds in ESCALATION_LADDER:
        rows = []
        for pr in pairs:
            sd = float(np.std(pilot_d[pr["pair"]], ddof=1))
            tgt = MDE_TARGET_BY_PAIR[pr["pair"]]
            rows.append({"pair": pr["pair"], "pilot_paired_sd": sd,
                         "mde": mde_paired(sd, n_worlds), "target": tgt,
                         "meets": bool(mde_paired(sd, n_worlds) <= tgt)})
        g2["ladder"].append({"n_worlds": n_worlds, "per_pair": rows})
    selected: dict[str, int] = {}
    for pr in pairs:
        pid = pr["pair"]
        sd = float(np.std(pilot_d[pid], ddof=1))
        tgt = MDE_TARGET_BY_PAIR[pid]
        n_sel = ESCALATION_LADDER[0]
        escalated = False
        if mde_paired(sd, ESCALATION_LADDER[0]) > tgt:
            n_sel = ESCALATION_LADDER[1]
            escalated = True
        short = bool(mde_paired(sd, n_sel) > tgt)
        selected[pid] = n_sel
        g2["per_pair"].append({
            "pair": pid, "kind": pr["kind"],
            "pilot_paired_diffs": [float(x) for x in pilot_d[pid]],
            "pilot_paired_sd": sd, "mde_target": tgt,
            "mde_at_32": mde_paired(sd, 32), "mde_at_64": mde_paired(sd, 64),
            "worlds_selected": n_sel, "escalated_32_to_64": escalated,
            "mde_at_selected": mde_paired(sd, n_sel),
            "short_at_max": short,
            "claims_tiered": short,
        })
    g2["worlds_selected_by_pair"] = selected
    g2["n_escalated"] = int(sum(r["escalated_32_to_64"] for r in g2["per_pair"]))
    g2["n_short_at_max"] = int(sum(r["short_at_max"] for r in g2["per_pair"]))
    g2["criterion"] = (
        "MDE(80%, alpha=.05, paired, n) for the within-pair field difference <= 0.010 "
        "for the two SPECIES pairs and <= 0.020 for FR-45; escalate 32->64 ONCE PER "
        "FAILING PAIR; still short at 64 -> RUN and TIER that pair's claims (registered)"
    )
    g2["pass"] = True   # registered: a shortfall tiers claims, it does not block the run
    g2["power_met_all_pairs"] = bool(g2["n_short_at_max"] == 0)
    gates["G2d_prime"] = g2

    # ---- G3d': rule 11 satisfiability with directions + rule 13 spec
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
    g3["clauses"] = [
        {"lean": "G1d'", "clause": "within-pair MEASURED card attenuation difference 95% "
                                   "CI inside +/-0.005",
         "direction": "two-sided (equivalence)",
         "satisfiable": bool(max(proj_pair_hw.values()) < MATCH_TOL_MEASURED),
         "note": "projected (conservative, unpaired) half-widths " + ", ".join(
             f"{k}={v:.8f}" for k, v in proj_pair_hw.items()) +
             f" against the +/-{MATCH_TOL_MEASURED} margin; the paired bootstrap actually "
             "used is strictly tighter"},
        {"lean": "cell MAT-SIG", "clause": "CI excludes 0 AND |D| >= M1=0.020 AND "
                                           "lower(|D|) >= M2=0.010",
         "direction": "two-sided exclusion + one-sided magnitude",
         "satisfiable": bool(all(1.96 * v < M1 - M2 for v in d_se_proj.values())),
         "note": "reachable iff a point at |D| = M1 can have its CI lower endpoint at or "
                 "above M2, i.e. 1.96*se < M1 - M2 = 0.010; projected 1.96*se " + ", ".join(
                     f"{k}={1.96 * v:.8f}" for k, v in d_se_proj.items())},
        {"lean": "cell NULL", "clause": "CI includes 0 AND CI inside +/-M2=0.010",
         "direction": "two-sided (equivalence)",
         "satisfiable": bool(all(1.96 * v < M2 for v in d_se_proj.values())),
         "note": "reachable iff 1.96*se < M2 for a D near 0; projected " + ", ".join(
             f"{k}={1.96 * v:.8f}" for k, v in d_se_proj.items())},
        {"lean": "cell WEAK-NULL", "clause": "CI includes 0, inside +/-M1 but not +/-M2",
         "direction": "two-sided", "satisfiable": True,
         "note": "an annulus between the two margins; always reachable for some (D, se)"},
        {"lean": "cell SUB-SIG / INDET", "clause": "complement cells",
         "direction": "deterministic given the others", "satisfiable": True,
         "note": "the per-pair table is a verified partition (see rule15_enumeration), so "
                 "the complement cells are reachable by construction"},
        {"lean": "L-F", "clause": "FR-45 lands in MAT-SIG(-)",
         "direction": "one-sided in content (K2c's unanimous NEGATIVE sign extended to "
                      "attenuation 0.45); scored on the two-sided CI as registered",
         "satisfiable": bool(1.96 * d_se_proj[FR_PAIR] < M1 - M2),
         "note": f"pilot D(FR-45) = {float(np.mean(pilot_d[FR_PAIR])):+.8f}; "
                 f"projected 1.96*se = {1.96 * d_se_proj[FR_PAIR]:.8f}"},
        {"lean": "L-S", "clause": "predicates over the two SP pairs' cells",
         "direction": "sign is itself a finding, either direction",
         "satisfiable": True,
         "note": "pilot D " + ", ".join(
             f"{p['pair']}={float(np.mean(pilot_d[p['pair']])):+.8f}"
             for p in pairs if p["kind"] == "species") +
             "; NOTE the L-S predicate space is NOT a partition (8 overlaps, 4 gaps of "
             "49) -- RN-7 pre-declares the readings"},
        {"lean": "L-M", "clause": "FR-45's Delta_mixed has the K2c direction (POSITIVE: "
                                  "the higher-state arm recovers MORE of the mixture) "
                                  "with CI excluding 0",
         "direction": "one-sided in content, two-sided CI", "satisfiable": True,
         "note": "K2c's Delta_mixed was +0.0069/+0.0247/+0.0585, every CI excluding 0, "
                 "growing with state content; an exclusion clause is satisfiable for any "
                 "non-degenerate CI"},
        {"lean": "q-update", "clause": "pooled q over 19 arms (6 K2b + 7 K2c + 6 K2d)",
         "direction": "descriptive, NO GATE", "satisfiable": True,
         "note": "K2c's 13-arm value q = 1.9337620539521978 [1.7337, 2.1933]"},
    ]
    g3["pass"] = bool(all(c["satisfiable"] for c in g3["clauses"]))
    gates["G3d_prime"] = g3

    # ---- G5d': hygiene
    build_mean = float(np.mean(build_times))
    per_arm_world = pilot_work_seconds / (len(arms) * len(PILOT_WORLDS))
    n_arm_worlds = sum(selected[a["pair"]] for a in arms)
    n_world_idx = max(selected.values())
    est_total = per_arm_world * n_arm_worlds + build_mean * (
        len(phis) * min(selected.values()) + 1 * (n_world_idx - min(selected.values()))
    )
    gates["G5d_prime"] = {
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
        gates["G0d_prime"]["pass"] and gates["G1d_prime"]["pass"]
        and gates["G2d_prime"]["pass"] and gates["G3d_prime"]["pass"]
        and gates["G4d_prime"]["pass"] and gates["G5d_prime"]["pass"]
        and gates["rule15_enumeration"]["pass"])
    gates["stage_seconds"] = time.time() - t0
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n",
                                    encoding="utf-8")
    (OUT / "part0_arms.json").write_text(
        json.dumps({"master_seed": MASTER_SEED, "worlds_selected_by_pair": selected,
                    "arms": arms, "pairs": pairs}, indent=2, default=str) + "\n",
        encoding="utf-8")
    pd.DataFrame([{k: v for k, v in r.items() if k != "realized_shares"}
                  for a in arms for r in pilot_field[a["arm"]]]).to_csv(
        OUT / "part0_pilot_field.csv", index=False)
    write_part0_tables(gates, preds, pairs, sensitivity)
    write_manifest({"part0": time.time() - t0})
    del k2b_field, k2b_pred_att, k2c_field, k2c_x, k2c_order
    print(json.dumps({
        "stage": "part0", "seconds": round(time.time() - t0, 3),
        "part0_all_pass": gates["part0_all_pass"],
        **{g: gates[g]["pass"] for g in ("G0d_prime", "G1d_prime", "G2d_prime",
                                         "G3d_prime", "G4d_prime", "G5d_prime")},
        "rule15_cell_space_pass": gates["rule15_enumeration"]["per_pair_cell_space"]["PASS"],
        "rule15_LS_gaps": gates["rule15_enumeration"]["L_S_predicate_space"]["n_gap"],
        "rule15_LS_overlaps": gates["rule15_enumeration"]["L_S_predicate_space"]["n_overlap"],
        "rule15_pivot_gaps": gates["rule15_enumeration"]["pivot_routing_space"]["gap_cells"],
        "solved": {p["pair"]: {"s_a": p["arm_a"]["share"], "s_b": p["arm_b"]["share"],
                               "t_b": p["arm_b"]["int_share"],
                               "r_a": p["arm_a"]["predicted_attenuation"],
                               "r_b": p["arm_b"]["predicted_attenuation"],
                               "abs_diff": p["abs_predicted_difference"]} for p in pairs},
        "worlds_selected_by_pair": selected,
        "anchors_bit_exact": gates["G0d_prime"]["all_bit_exact"],
        "stage_estimate": gates["G5d_prime"]["stage_estimate_seconds"],
    }, indent=2, default=str))


def write_part0_tables(gates: dict[str, Any], preds: pd.DataFrame,
                       pairs: list[dict[str, Any]], sensitivity: list[dict[str, Any]]) -> None:
    lines: list[str] = []
    lines.append("### G1d' -- the SOLVED shares and the designed identity\n")
    lines.append("| pair | kind | target r | arm a (share, int, phi) | r(a) | "
                 "arm b (share, int, phi) | r(b) | |r(a)-r(b)| | matched (<=1e-12) |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for p in pairs:
        a, b = p["arm_a"], p["arm_b"]
        lines.append(
            f"| `{p['pair']}` | {p['kind']} | {p['target_attenuation']:g} | "
            f"`{a['arm']}` ({a['share']!r}, {a['int_share']!r}, {a['phi']:g}) | "
            f"{a['predicted_attenuation']!r} | "
            f"`{b['arm']}` ({b['share']!r}, {b['int_share']!r}, {b['phi']:g}) | "
            f"{b['predicted_attenuation']!r} | {p['abs_predicted_difference']:.6e} | "
            f"{p['matched_part0']} |")
    lines.append("\n### RN-1 trade sensitivity (pure card algebra; no world, no field number)\n")
    lines.append("| pair | trade fraction | slow share (slow arm) | slow share (int arm) | "
                 "solved int fraction | realized var share int | |dr| | selected |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in sensitivity:
        lines.append(
            f"| `{r['pair']}` | {r['trade_fraction']:g} | {r['slow_share_slow_arm']:.12g} | "
            f"{r['slow_share_int_arm']:.12g} | {r['int_share_solved']:.12g} | "
            f"{r['realized_variance_share_int']:.8f} | "
            f"{r['abs_predicted_difference']:.3e} | {r['selected_RN1']} |")
    lines.append("\n### Part-0 point predictions -- all 6 arms, computed before any world\n")
    lines.append("| arm | pair | share | int | phi | A (mu) | B (slow) | C (int) | "
                 "Cc (frame) | E (noise) | GAP pred | r(card->b) pred |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for _, r in preds.iterrows():
        lines.append(
            f"| `{r['arm']}` | {r['pair']} | {r['share_design']:.12g} | "
            f"{r['int_share']:.12g} | {r['phi_slow']:g} | {r['A_mu']:.8f} | "
            f"{r['B_slow']:.8f} | {r['C_int']:.8f} | {r['Cc_common']:.8f} | "
            f"{r['E_noise']:.8f} | {r['gap_pred']:.10f} | {r['r_card_b_pred_raw']:.12f} |")
    enum = gates["rule15_enumeration"]
    lines.append("\n### Rule-15 enumeration, per-pair cell space (the adjudication space)\n")
    cs = enum["per_pair_cell_space"]
    lines.append(f"Searched {cs['n_triples_searched']} (point, lo, hi) triples; "
                 f"{cs['n_realizable']}/{cs['n_combinations']} clause combinations "
                 f"realizable; overlaps {cs['n_overlapping']}; all seven signed cells "
                 f"realized: {cs['all_seven_cells_realized']}.\n")
    lines.append("| c1 excludes 0 | c2 |D|>=M1 | c3 lower(|D|)>=M2 | c4 CI in ±M2 | "
                 "c5 CI in ±M1 | c6 D>0 | realizable | cell |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for row in cs["truth_table"]:
        if not row["realizable"]:
            continue
        cells = ", ".join(row["cells"])
        lines.append(
            f"| {row['c1_ci_excludes_zero']} | {row['c2_point_abs_ge_M1']} | "
            f"{row['c3_abs_lower_ge_M2']} | {row['c4_ci_inside_M2']} | "
            f"{row['c5_ci_inside_M1']} | {row['c6_D_positive']} | "
            f"{row['realizable']} | {cells} |")
    lines.append(f"\n({cs['n_combinations'] - cs['n_realizable']} of the "
                 f"{cs['n_combinations']} clause combinations are logically UNREALIZABLE "
                 "— e.g. |D| ≥ M1 with the CI inside ±M2, which needs the point outside "
                 "its own interval — and are omitted from the table above; the full "
                 "truth table is in gates.json.)")
    lines.append("\n### Rule-15 enumeration, L-S predicate space (49 ordered cell pairs)\n")
    ls = enum["L_S_predicate_space"]
    lines.append(f"unique {ls['n_unique']} / overlap {ls['n_overlap']} / gap {ls['n_gap']} "
                 f"of {ls['n_combinations']}.\n")
    lines.append("| SP-68 cell | SP-56 cell | registered predicates true | status |")
    lines.append("|---|---|---|---|")
    for row in ls["rows"]:
        status = ("unique" if row["n"] == 1 else "OVERLAP" if row["n"] > 1 else "GAP")
        lines.append(f"| {row['SP-68']} | {row['SP-56']} | "
                     f"{', '.join(row['outcomes']) if row['outcomes'] else '—'} | {status} |")
    lines.append("\n### Rule-15 enumeration, pivot routing over FR-45's cell\n")
    lines.append("| FR-45 cell | pivot | status |")
    lines.append("|---|---|---|")
    for row in enum["pivot_routing_space"]["rows"]:
        lines.append(f"| {row['FR-45 cell']} | {', '.join(row['pivot']) if row['pivot'] else '—'} "
                     f"| {'routed' if row['n'] == 1 else 'GAP'} |")
    lines.append("\n### G4d' liveness (pilot worlds 9801-9802)\n")
    lines.append("| pair | kind | panel RMS a vs b | realized slow a | realized slow b | "
                 "realized int a | realized int b | pilot field a | pilot field b | non-degenerate |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in gates["G4d_prime"]["within_pair"]:
        lines.append(
            f"| `{r['pair']}` | {r['kind']} | {r['rms_panel_change']:.8f} | "
            f"{r['realized_slow_a']:.8f} | {r['realized_slow_b']:.8f} | "
            f"{r['realized_int_a']:.8f} | {r['realized_int_b']:.8f} | "
            f"{r['pilot_field_a']:.8f} | {r['pilot_field_b']:.8f} | {r['non_degenerate']} |")
    ap = gates["G4d_prime"]["across_pair"]
    lines.append("\n| designed level | pilot card attenuation | pilot field recovery |")
    lines.append("|---|---|---|")
    for lvl, c, f in zip(ap["levels_ascending_by_design"], ap["pilot_card_attenuation"],
                         ap["pilot_field_recovery"]):
        lines.append(f"| {lvl} | {c:.8f} | {f:.8f} |")
    lines.append("\n### G2d' power ladder (2-world pilot, PER PAIR)\n")
    lines.append("| pair | pilot paired sd | MDE target | MDE @32 | MDE @64 | selected n | "
                 "escalated | short at max |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for r in gates["G2d_prime"]["per_pair"]:
        lines.append(f"| `{r['pair']}` | {r['pilot_paired_sd']:.8f} | {r['mde_target']:g} | "
                     f"{r['mde_at_32']:.8f} | {r['mde_at_64']:.8f} | {r['worlds_selected']} | "
                     f"{r['escalated_32_to_64']} | {r['short_at_max']} |")
    lines.append("\n### G3d' clause satisfiability with DIRECTIONS (rule 11)\n")
    lines.append("| lean | clause | direction | satisfiable | note |")
    lines.append("|---|---|---|---|---|")
    for c in gates["G3d_prime"]["clauses"]:
        lines.append(f"| {c['lean']} | {c['clause']} | {c['direction']} | {c['satisfiable']} | "
                     f"{c['note']} |")
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
    install_species_weights()
    m = k2b()
    selected = {k: int(v) for k, v in gates["G2d_prime"]["worlds_selected_by_pair"].items()}
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
            frame, _ = m.card_channel_frame(world, weights[a["arm"]], seed)
            card_acc[a["arm"]].append(frame)
            field_acc[a["arm"]].append(
                run_field_world(a["arm"], world_index, world, weights[a["arm"]]))
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
    install_species_weights()
    m = k2b()
    k2a = m.k2a()
    kc = k2c()
    t0 = time.time()
    selected = {k: int(v) for k, v in gates["G2d_prime"]["worlds_selected_by_pair"].items()}
    arms = arms_spec()
    pairs = pairs_spec()
    preds = read_csv_rt(OUT / "part0_predictions.csv").set_index("arm")

    card_by_arm: dict[str, pd.DataFrame] = {}
    field_by_arm: dict[str, np.ndarray] = {}
    mixed_by_arm: dict[str, np.ndarray] = {}
    cells: list[dict[str, Any]] = []
    stability: list[dict[str, Any]] = []
    for a in arms:
        aid = a["arm"]
        n_worlds = selected[a["pair"]]
        card, field = load_arm(aid, n_worlds)
        card_by_arm[aid] = card
        field_by_arm[aid] = field["recovery_b_only"].to_numpy(float)
        mixed_by_arm[aid] = field["recovery_mixed"].to_numpy(float)
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

    # ---- G1d' post-arms: the MEASURED matching
    g1_post: list[dict[str, Any]] = []
    for pr in pairs:
        ida, idb = pr["arm_a"]["arm"], pr["arm_b"]["arm"]
        pa, pb, ba, bb = kc.bootstrap_card_pair(card_by_arm[ida], card_by_arm[idb],
                                                B_BOOT, MASTER_SEED)
        d_boot = ba["r_card_b_raw"] - bb["r_card_b_raw"]
        d_point = float(pa["r_card_b_raw"] - pb["r_card_b_raw"])
        lo, hi = k2a.ci_of(d_boot)
        inside = bool(-MATCH_TOL_MEASURED <= lo and hi <= MATCH_TOL_MEASURED)
        g1_post.append({"pair": pr["pair"], "arm_a": ida, "arm_b": idb,
                        "measured_attenuation_a": float(pa["r_card_b_raw"]),
                        "measured_attenuation_b": float(pb["r_card_b_raw"]),
                        "predicted_attenuation": pr["arm_a"]["predicted_attenuation"],
                        "measured_difference": d_point, "ci": [lo, hi],
                        "se": float(np.std(d_boot, ddof=1)),
                        "margin": MATCH_TOL_MEASURED, "inside_margin": inside,
                        "VOID": bool(not inside)})
        mc = k2a.mc_sd_of_endpoint(d_boot, B_BOOT, 0.025)
        dist = min(abs(MATCH_TOL_MEASURED - hi), abs(-MATCH_TOL_MEASURED - lo))
        if dist <= 2.0 * mc:
            _, _, ba2, bb2 = kc.bootstrap_card_pair(card_by_arm[ida], card_by_arm[idb],
                                                    B_BOOT_HIGH, MASTER_SEED)
            d2 = ba2["r_card_b_raw"] - bb2["r_card_b_raw"]
            lo2, hi2 = k2a.ci_of(d2)
            v2 = bool(-MATCH_TOL_MEASURED <= lo2 and hi2 <= MATCH_TOL_MEASURED)
            stability.append({"scope": f"G1d'[{pr['pair']}]",
                              "clause": "measured within-pair attenuation diff CI inside +/-0.005",
                              "direction": "two-sided (equivalence)",
                              "boundary": MATCH_TOL_MEASURED, "mc_sd_endpoint_B2000": mc,
                              "distance_to_boundary": dist, "verdict_B2000": inside,
                              "verdict_B20000": v2, "endpoints_B20000": [lo2, hi2],
                              "status": "STABLE" if inside == v2 else "BOUNDARY"})
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
        pilot = next(r for r in gates["G2d_prime"]["per_pair"] if r["pair"] == pid)
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
            "sign": int(np.sign(point)),
            "per_world_positive": int(np.sum(d > 0.0)),
            "paired_t_ci": [point - kc.T_QUANTILES[n_worlds][0] * sd_real / math.sqrt(n_worlds),
                            point + kc.T_QUANTILES[n_worlds][0] * sd_real / math.sqrt(n_worlds)],
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
        # rule 13 on every gated CI-endpoint clause of this pair
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
            ("L-M Delta_mixed CI excludes 0", 0.0, min(abs(mlo), abs(mhi)),
             rec["delta_mixed_excludes_zero"],
             lambda l2, h2: bool(l2 > 0.0 or h2 < 0.0), dmb_hi, mc_m),
        ]
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

    # ---- L-F (frontier)
    fr = by_pair[FR_PAIR]
    frontier = score_frontier(fr["CELL"] if not fr["VOID"] else "INDET")
    frontier.update({"prior": 0.55, "D": fr["D"], "ci": fr["ci"],
                     "VOID": fr["VOID"], "cell_raw": fr["CELL"],
                     "clause": "FR-45 in MAT-SIG(-)",
                     "note": ("a VOID pair is scored as unresolved for its claims (P1d''); "
                              "cell_raw records what the numbers alone would have said")})

    # ---- L-S (species)
    sp = [by_pair[p] for p in ("SP-68", "SP-56")]
    if any(r["VOID"] for r in sp):
        species = {"verdict": "SPECIES-VOID", "status": "PAIR_VOID",
                   "cell_SP68": sp[0]["CELL"], "cell_SP56": sp[1]["CELL"],
                   "registered_predicates_true": []}
    else:
        species = score_ls(sp[0]["CELL"], sp[1]["CELL"])
    species.update({
        "priors": {"SPECIES-GENERAL": 0.35, "SPECIES-SPECIFIC": 0.45, "SPECIES-MIXED": 0.20},
        "signs": {"SP-68": sp[0]["sign"], "SP-56": sp[1]["sign"]},
        "D": {"SP-68": sp[0]["D"], "SP-56": sp[1]["D"]},
        "ci": {"SP-68": sp[0]["ci"], "SP-56": sp[1]["ci"]},
        "carrier_reading": (
            "sign < 0 (slow arm recovers LESS) => the persistent slow species costs the "
            "reader MORE than the card-equivalent occasion-bound species; sign > 0 => the "
            "occasion-bound species costs more; NULL/WEAK-NULL => species-general (c() "
            "counts non-trait person content in the card's own currency)"),
    })

    # ---- L-M (mixture, secondary)
    l_m = {
        "prior": 0.70,
        "clause": "FR-45's Delta_mixed has the K2c direction (POSITIVE) with CI excluding 0",
        "delta_mixed": fr["delta_mixed"], "ci": fr["delta_mixed_ci"],
        "se": fr["delta_mixed_se"],
        "excludes_zero": fr["delta_mixed_excludes_zero"],
        "sign": int(np.sign(fr["delta_mixed"])),
        "k2c_direction": "+1 (higher-state arm recovers MORE of the mixture)",
        "holds": bool(fr["delta_mixed"] > 0.0 and fr["delta_mixed_excludes_zero"]
                      and not fr["VOID"]),
        "sp_pairs_descriptive": {r["pair"]: {"delta_mixed": r["delta_mixed"],
                                             "ci": r["delta_mixed_ci"],
                                             "excludes_zero": r["delta_mixed_excludes_zero"]}
                                 for r in sp},
    }

    # ---- q-update over all 19 arms (DESCRIPTIVE, no gate)
    anchors = rederive_anchors()
    k2b_field = anchors.pop("_k2b_field")
    anchors.pop("_k2b_pred_att")
    k2c_field = anchors.pop("_k2c_field")
    anchors.pop("_k2c_mixed")
    k2c_x = anchors.pop("_k2c_x")
    k2c_order = anchors.pop("_k2c_order")
    order_d = tuple(a["arm"] for a in arms)
    x_d = np.log(np.array([float(preds.loc[a, "r_card_b_pred_raw"]) for a in order_d]))
    groups_by_n: dict[int, list[str]] = {}
    for a in arms:
        groups_by_n.setdefault(selected[a["pair"]], []).append(a["arm"])
    d_groups = []
    for n in sorted(groups_by_n):
        ids = groups_by_n[n]
        idx = [order_d.index(i) for i in ids]
        d_groups.append((x_d[idx], [field_by_arm[i] for i in ids]))
    groups = [(k2c_x[:6], [k2b_field[a] for a in K2B_PRIMARY_ARMS]),
              (k2c_x[6:], [k2c_field[a] for a in k2c_order])] + d_groups
    q19 = pooled_q(groups, K2B_LAMBDA, B_BOOT, MASTER_SEED)
    q19_lam1 = pooled_q(groups, 1.0, B_BOOT, MASTER_SEED)
    q_boot19 = q19.pop("q_boot")
    q19_lam1.pop("q_boot")
    q19.update({
        "scope": "19 arms = 6 K2b + 7 K2c + 6 K2d",
        "x_convention": "Part-0 PREDICTED attenuation (deterministic x), as in K2c",
        "lambda_invariance_check": {"q_at_lambda_k2b": q19["q"], "q_at_lambda_1": q19_lam1["q"],
                                    "abs_difference": abs(q19["q"] - q19_lam1["q"])},
        "k2c_13_arm_value": anchors["k2c"]["q_rederived"],
        "k2c_13_arm_ci": anchors["k2c"]["q_ci_rederived"],
        "shift_vs_k2c": q19["q"] - anchors["k2c"]["q_rederived"],
        "gate": "NONE (registered descriptive)",
    })

    if stability:
        pd.DataFrame(stability).to_csv(OUT / "rule13_stability.csv", index=False)
    boundary = [s for s in stability if s["status"] == "BOUNDARY"]

    # ---- pivots
    pivots = {
        "P1d''": {"fires": bool(n_void >= 2),
                  "clause": ">=2 pairs VOID on G1d' matching",
                  "consequence": "leg reports and stops (instrument question)"},
        "P2d''": {"fires": bool(frontier["pivot"] == "P2d''" and n_void < 2),
                  "clause": "L-F HOLDS (FR-45 in MAT-SIG(-))",
                  "consequence": "T4 re-types to T4-reader-amplified-composition; the T4 "
                                 "branch CLOSES as reader-borne-in-substance; the "
                                 "constructive repair test becomes the next registration"},
        "P3d''": {"fires": bool(frontier["pivot"] == "P3d''" and n_void < 2),
                  "clause": "FR-45 in {NULL, WEAK-NULL}",
                  "consequence": "T4 re-types T4-simple-with-link (q~2) + sub-material "
                                 "composition correction; the repair question targets the LINK"},
        "P4d''": {"fires": bool(frontier["pivot"] == "P4d''" and n_void < 2),
                  "clause": "FR-45 in {SUB-SIG, INDET}",
                  "consequence": "frontier unresolved; K2e extends the frontier or the "
                                 "worlds once, enumeration carried over"},
    }

    # ---- verdict slug
    cell_slug = (frontier["cell"].replace("MAT-SIG", "MATSIG").replace("SUB-SIG", "SUBSIG")
                 .replace("WEAK-NULL", "WEAKNULL").replace("(", "_").replace(")", "")
                 .replace("+", "POS").replace("-", "NEG"))
    slug = f"FRONTIER_{cell_slug}__L_F_{'HOLD' if frontier['L_F_holds'] else 'MISS'}"
    slug += "__" + species["verdict"].replace("SPECIES-", "SPECIES_").replace("-", "_")
    slug += "__MATCH_" + ("EXACT" if n_void == 0 else f"VOID{n_void}")
    slug += "__LM_" + ("HOLD" if l_m["holds"] else "MISS")

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
            "note": "not a registered gate (K2a/K2b certified the instrument); continuity only"},
        "card_gap_ratio_within_pair": {
            pr["pair"]: (cell_by_arm[pr["arm_a"]["arm"]]["gap"]
                         / cell_by_arm[pr["arm_b"]["arm"]]["gap"]) for pr in pairs},
    }

    decision = {
        "leg": "M4-K2d",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "banner": BANNER,
        "master_seed": MASTER_SEED,
        "worlds_selected_by_pair": selected,
        "margins": {"M1": M1, "M2": M2},
        "n_authors_per_world": int(len(m.layout()["author_ids"])),
        "n_retained": int(len(m.layout()["retained_idx"])),
        "arms": arms,
        "G0d_prime_anchors": anchors,
        "G1d_prime_post_arms": {"per_pair": g1_post, "pairs_void": n_void,
                                "pass": bool(n_void == 0)},
        "pair_differences": d_rows,
        "cells": {r["pair"]: r["CELL"] for r in d_rows},
        "leans": {"L-F": frontier, "L-S": species, "L-M": l_m, "q_update": q19},
        "pivots": pivots,
        "rule13": {"triggered": len(stability), "boundary": len(boundary),
                   "records": stability},
        "rule15_enumeration": gates["rule15_enumeration"],
        "descriptive": descriptive,
        "verdict_slug": slug,
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2, default=str) + "\n",
                                       encoding="utf-8")
    write_manifest({"finalize": time.time() - t0})
    print(json.dumps({k: v for k, v in decision.items()
                      if k not in ("rule13", "descriptive", "arms", "rule15_enumeration",
                                   "G0d_prime_anchors")}, indent=2, default=str))
    print(f"rule13 triggered={len(stability)} boundary={len(boundary)}")
    del q_boot19


def write_manifest(stage_times: dict[str, float]) -> None:
    path = OUT / "manifest.json"
    prior = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    prior.setdefault("leg", "M4-K2d")
    prior.setdefault("banner", BANNER)
    prior.setdefault("script", "scripts/run_suica_m4_k2d_frontier_carrier.py")
    prior.setdefault("master_seed", MASTER_SEED)
    prior.setdefault("worlds_per_arm_registered", WORLDS_PER_ARM)
    prior.setdefault("pilot_worlds", list(PILOT_WORLDS))
    prior.setdefault("fr_target", FR_TARGET)
    prior.setdefault("sp_targets", [list(p) for p in SP_TARGETS])
    prior.setdefault("phi_a", PHI_A)
    prior.setdefault("phi_b", PHI_B)
    prior.setdefault("trade_fraction_RN1", TRADE_FRACTION)
    prior.setdefault("margins", {"M1": M1, "M2": M2})
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
