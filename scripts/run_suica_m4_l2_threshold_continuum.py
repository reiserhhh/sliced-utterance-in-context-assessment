#!/usr/bin/env python3
"""M4-L2 -- the THRESHOLD, the CONTINUUM, and the LABEL-FREE INSTRUMENTS.

Registered spec: docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md section "M4-L2 -- The
threshold, the continuum, and the label-free instruments (registered on the
repaired theory)" (REGISTERED 2026-08-10, BEFORE RUN, commit 767f464), together
with the "L2 charter + planner derivation" section above it (derivations 1-4:
the projection gain G(eta) = 1/(eta + (1-eta) k_tau/m); the generalized floor
sigma_u^2(eta) = eta sigma_b^2/k_tau + (1-eta) sigma_b^2/m; the spectral
taxometer with its BBP-form detectability caveat; the cross-fitted audit).
Theory: docs/SUICA_IDENTITY_THEORY_V1.md appendix Q (Q.1 the floor-invariance
lemma, Q.3 R2 restated as a LOCALIZATION-threshold claim, Q.5 the audit's one
calibration constant) and appendix P (R1-R3).

Executor standing: implementation and execution ONLY.  Everything labelled
"MN-n" is a register-note -- an operationalization of something the
registration left open (standing rule 9) -- fixed and written to
reports/SUICA_M4_L2_THRESHOLD_CONTINUUM_REPORT.md Part 0 BEFORE any main arm
ran.  Standing rules 18 (JOINT satisfiability across knob-sharing clauses) and
19 (every lean bar shadows the theorem's OWN quantity, stated in a fidelity
table) are FIRST APPLIED here.

CARD SPACE ONLY.  The deployed gauge is never invoked.  Every gate and every
lean compares card-space quantities to card-space quantities (ARI-vs-ARI,
rate-vs-rate, share-vs-share); rule-14 self-check in the report section 0.0.

Reuse boundary (standing rule 12 -- generator SOURCE OBJECTS, not knob names):
  - scripts/run_suica_m4_l1_typed_world.py imported AS A MODULE (`l1`),
    UNMODIFIED.  This leg calls, and does not reimplement:
      l1.TETRAHEDRON            (l1:200-202) the regular simplex
      l1.latent_type_vectors    (l1:247-251) tau_g in R^48
      l1.card_space_type_basis  (l1:284-290) the ORACLE-S target M(S) in R^64
      l1.centred_with_trait     (l1:301-304)
      l1.kmeans_lloyd           (l1:376-412) THE PRIMARY grouping instrument
      l1.adjusted_rand_index    (l1:422-435) / l1.hungarian_accuracy (l1:438-444)
      l1.boundary_error_rate    (l1:447-468) RN-7's per-boundary rate
      l1.group_centre           (l1:551-556) / l1._norm_dot (l1:546-548)
      l1.build_typed_world      (l1:292-298) k2a's channels + a type stream
      l1.run_world_cells        (l1:895-900) used ONLY by the G0M L1 anchor
      l1.MASTER_SEED/N_AUTHORS/G_GROUPS/K_TAU/PHI_SLOW/N_OCC/W_INT_ARM/N_RESTART
    and, transitively, scripts/run_suica_m4_k2a_expressive_world.py (`k2a`,
    UNMODIFIED): build_world, arm_weights('zero'), centered_channels, card,
    splits, ar_mean_var/ar_set_var/ar_cross_cov, read_csv_rt, ci_of,
    mc_sd_of_endpoint, response_panel, K_LATENT/DIM/G_PROFILE/A_SCALE/
    SIGMA_ISO/UNIT_ENTRY_VAR/N_REP; and suica_core's _orthonormal_loadings and
    stable_bucket.  suica_core is NOT touched, and no file outside this one is
    modified.
  - NEW in this leg (rule 12, cited by THIS file's line numbers in the report):
    type_geometry_l2() (TWO independent identity streams -> the eta mixture),
    latent_identity_l2(), typed_trait_l2(), cards_for_cell(), estimated_s(),
    subspace_overlap(), predicted_boundary_error_l2() (the eta floor curve on
    the realized geometry), bbp_quantities(), audit_meter_l2() (the CALIBRATED
    meter, cross-fitted / same-data / oracle), pred_population_l2(),
    ladder_grid()/solve_ladder(), fidelity_table(), joint_satisfiability().

Stages (foreground, chunked, resumable; artifacts under
results/m4_l2_threshold_continuum/):
  --stage part0     G0M/G1M/G2M/G3M/G4M on RESERVED pilot worlds 9901-9904, the
                    Delta-ladder solve, the rule-19 fidelity table, the rule-18
                    JOINT satisfiability enumeration and the rule-16 full-object
                    enumeration.  `arms` REFUSES to run unless every gate passes
                    AND the report exists on disk.
  --stage arms      15 cells (5 T + 10 C) x 8 main worlds x 512 authors.
  --stage finalize  paired world-block bootstrap, leans W-1..W-4, rule-13
                    stability rechecks, the rule-16 routing, decision.json.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import math
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import suica_core.v8_realtext_relation_field as v8  # noqa: E402

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"

OUT = ROOT / "results" / "m4_l2_threshold_continuum"
REPORT = ROOT / "reports" / "SUICA_M4_L2_THRESHOLD_CONTINUUM_REPORT.md"
L1_OUT = ROOT / "results" / "m4_l1_typed_world"

# --- registration-fixed constants -------------------------------------------
MASTER_SEED = 20260823          # registration: "master_seed 20260823"
N_AUTHORS = 512                 # registration: "8 worlds x 512 authors/cell"
WORLDS_PER_CELL = 8
PILOT_WORLDS = (9901, 9902, 9903, 9904)   # RESERVED; disjoint from 0..7
G_GROUPS = 4                    # registration: "G = 4"
K_TAU = 3                       # registration: "k_tau = 3"
PHI_SLOW = 0.90
N_OCC = 8
W_INT_ARM = "zero"
N_RESTART = 64
B_BOOT = 2000                   # registration G2M: "B=2000, seed=master"
B_BOOT_HIGH = 20000             # registration G2M: ">=10xB at boundaries"

# --- L1 anchors, quoted from the registration (G0M; round-trip re-derived) ---
L1_DELTA = 5.928950380606693
L1_ARI_ISO_055 = 0.9664213102607500
L1_ARI_ALIGNED_055 = 0.4205650587388517
L1_TAX_RATIO = 8.145911689523754
L1_AUDIT_OFFSET = 0.002754
L1_B_HAT = 0.245861
L1_FLOOR_ALIGNED_035_MEASURED = 0.027750651041666664
L1_FLOOR_ALIGNED_035_PREDICTED = 0.027118834519294123
L1_FLOOR_ALIGNED_055_MEASURED = 0.107421875
L1_FLOOR_ALIGNED_055_PREDICTED = 0.10068281660598428

# --- the (Delta, sigma_b) DECOUPLING (registration: "INDEPENDENT knobs") -----
# L1 tied them through rho_id (defect #27's root): sigma_b^2 = (3/8) Delta^2
# rho/(1-rho).  L2 keeps Delta free and pins sigma_b^2 at the two ENERGIES L1
# realized at its own Delta -- "L1's rho.35 / rho.55 equivalents".
SIGMA_TAU2_PER_DELTA2 = 3.0 / 8.0          # regular simplex, l1:203
L1_SIGMA_TAU2 = SIGMA_TAU2_PER_DELTA2 * L1_DELTA * L1_DELTA
SB2_RHO55 = L1_SIGMA_TAU2 * 0.55 / 0.45    # 16.111540782194115
SB2_RHO35 = L1_SIGMA_TAU2 * 0.35 / 0.65    # 7.098091393554051

ETA_LEVELS = (0.0, 0.25, 0.5, 0.75, 1.0)   # registration C-arms
C_ENERGIES = (("rho35eq", SB2_RHO35), ("rho55eq", SB2_RHO55))

# --- MN-3: the T-arm ladder rule (rule 9 + rule 17), fixed before any number -
LADDER_TARGETS = (0.10, 0.25, 0.50, 0.75, 0.90)   # AMBIENT ARI targets
LADDER_GRID_LO, LADDER_GRID_HI, LADDER_GRID_N = 0.75, 9.0, 34
LADDER_REPS = 6                 # prediction-stream replicate populations
BRACKET_LO, BRACKET_HI = 0.30, 0.80   # registration G1M: span (<0.3, >0.8)
FLOOR_BAR = 0.005               # registration: "oracle-S floor < 0.005"
PRED_REPS_INSTRUMENT = 8

# --- lean thresholds, verbatim from the registration ------------------------
W1_AMBIENT_BAR = 0.30           # "ambient ARI < 0.3"
W1_ORACLE_BAR = 0.80            # "while oracle-S > 0.8"
W1_MIN_CELLS = 2                # "in >=2 T-cells inside the bracketed window"
W3_MIN_CONTAIN = 7              # "within CI of the floor curve in >=7/10 cells"
W4_MIN_TRACK = 8                # "tracks designed shares in >=8/10 C-cells"

_L1 = None


def l1() -> Any:
    """The M4-L1 leg script, imported as a module and used UNMODIFIED."""
    global _L1
    if _L1 is None:
        path = ROOT / "scripts" / "run_suica_m4_l1_typed_world.py"
        spec = importlib.util.spec_from_file_location("run_suica_m4_l1_typed_world", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _L1 = module
    return _L1


def k2a() -> Any:
    return l1().k2a()


# ---------------------------------------------------------------------------
# MN-1 (rule 9): the cells.  5 T-cells (question A: ISO, sigma_b fixed, Delta
# swept on the Part-0 ladder) + 10 C-cells (question B/C: Delta = L1's, two
# energies x five eta).  Cell ids carry the rung index for T-cells so the id is
# stable while the ladder value is not.

def t_cell_id(rung: int) -> str:
    return f"T{rung}"


def c_cell_id(energy: str, eta: float) -> str:
    return f"C_{energy}_eta{eta:g}"


def all_cells(ladder: list[float]) -> list[dict[str, Any]]:
    cells = [{"cell": t_cell_id(i), "kind": "T", "delta": float(d),
              "sigma_b2": SB2_RHO55, "eta": 0.0, "energy": "rho55eq", "rung": i}
             for i, d in enumerate(ladder)]
    cells += [{"cell": c_cell_id(name, eta), "kind": "C", "delta": L1_DELTA,
               "sigma_b2": sb2, "eta": float(eta), "energy": name, "rung": -1}
              for name, sb2 in C_ENERGIES for eta in ETA_LEVELS]
    return cells


def world_seed_for(world: int) -> int:
    """MN-2: the L2 world seed depends on the WORLD INDEX ONLY (salt disjoint
    from k2a's and l1's), so every cell of a world shares the loadings, the slow
    state, the frame channel, the noise, the group assignment g, the type
    subspace S and BOTH raw identity draws BIT-FOR-BIT.  Every cross-cell
    contrast in this leg is therefore an exactly paired within-world contrast."""
    return int(
        v8.stable_bucket(f"{MASTER_SEED}-{world}", salt="m4l2-world", modulus=2**31 - 1)
    )


# ---------------------------------------------------------------------------
# The TYPE layer with INDEPENDENT (Delta, sigma_b) and the eta mixture.

def type_geometry_l2(world_seed: int, n_authors: int) -> dict[str, Any]:
    """MN-4 (rule 9): the type stream.  Salt 'm4l2-type' is disjoint from every
    k2a and l1 stream.  Draws, in this fixed order: the random 3-frame S (QR of
    a 48x3 Gaussian), the equal-size group assignment, then TWO INDEPENDENT
    identity draws xi (the isotropic component) and zeta (the aligned
    component).  Independence is REQUIRED by derivation 2: only then does the
    boundary-normal variance add as sigma_u^2(eta) = eta sigma_b^2/k_tau +
    (1-eta) sigma_b^2/m and the total energy stay sigma_b^2 for every eta (a
    single shared draw would put a 2 sqrt(eta(1-eta)) sqrt(k_tau/m) cross term
    in both)."""
    m = k2a()
    rng = np.random.default_rng(
        v8.stable_bucket(str(world_seed), salt="m4l2-type", modulus=2**63 - 1)
    )
    basis = np.linalg.qr(rng.normal(size=(m.K_LATENT, K_TAU)))[0]     # (48,3)
    perm = rng.permutation(n_authors)
    group = np.empty(n_authors, dtype=int)
    per = n_authors // G_GROUPS
    for g in range(G_GROUPS):
        group[perm[g * per:(g + 1) * per]] = g
    xi = rng.normal(size=(n_authors, m.K_LATENT))
    zeta = rng.normal(size=(n_authors, m.K_LATENT))
    return {"S": basis, "group": group, "xi": xi, "zeta": zeta}


def latent_identity_l2(typ: dict[str, Any], sigma_b2: float, eta: float) -> np.ndarray:
    """b = sqrt(1-eta) b_iso + sqrt(eta) b_aligned at TOTAL energy sigma_b^2."""
    m = k2a()
    out = np.zeros_like(typ["xi"])
    if eta < 1.0:
        out = out + math.sqrt((1.0 - eta) * sigma_b2 / m.K_LATENT) * typ["xi"]
    if eta > 0.0:
        out = out + math.sqrt(eta * sigma_b2 / K_TAU) * (
            (typ["zeta"] @ typ["S"]) @ typ["S"].T)
    return out


def typed_trait_l2(world: dict[str, np.ndarray], typ: dict[str, Any], delta: float,
                   sigma_b2: float, eta: float, drop_identity: bool = False,
                   drop_type: bool = False) -> np.ndarray:
    m = k2a()
    tau = l1().latent_type_vectors(typ["S"], delta)
    latent = np.zeros((typ["xi"].shape[0], m.K_LATENT))
    if not drop_type:
        latent = latent + tau[typ["group"]]
    if not drop_identity:
        latent = latent + latent_identity_l2(typ, sigma_b2, eta)
    return m.A_SCALE * ((latent * m.G_PROFILE) @ world["loadings"].T)


def build_typed_world_l2(world_seed: int, n_authors: int) -> tuple[dict, dict]:
    world = k2a().build_world(world_seed, n_authors, N_OCC, PHI_SLOW)
    return world, type_geometry_l2(world_seed, n_authors)


# ---------------------------------------------------------------------------
# MN-5 (rule 9): the CROSS-FITTING split scheme.  The registration says
# "cluster on one occasion-half, audit on the other".  Pinned: the FIT half is
# k2a.splits(8)['contiguous'][0] = {0,1,2,3}; the AUDIT half is its complement
# {4,5,6,7}.  The meter's own two splits live INSIDE the audit half:
# interleaved {4,6} vs {5,7} and contiguous {4,5} vs {6,7} -- the same
# interleaved/contiguous pair k2a.splits defines, restricted to that half.
# Both reps enter every card (k2a.card(..., reps=(0,1))).

def occasion_scheme() -> dict[str, Any]:
    m = k2a()
    fit, audit = m.splits(N_OCC)["contiguous"]
    return {
        "fit": np.asarray(fit), "audit": np.asarray(audit),
        "audit_int": (np.asarray(audit[0::2]), np.asarray(audit[1::2])),
        "audit_cont": (np.asarray(audit[: len(audit) // 2]),
                       np.asarray(audit[len(audit) // 2:])),
    }


def cards_for_cell(world: dict, typ: dict, delta: float, sigma_b2: float,
                   eta: float) -> dict[str, Any]:
    """Every card object one cell needs, all via k2a.card (k2a:262-276)."""
    m = k2a()
    w = m.arm_weights(W_INT_ARM)
    sc = occasion_scheme()
    trait = typed_trait_l2(world, typ, delta, sigma_b2, eta)
    cen = l1().centred_with_trait(world, trait)
    both = (0, 1)
    full = m.card(cen, w, np.arange(N_OCC), both, True)
    fit_card = m.card(cen, w, sc["fit"], both, True)
    audit_card = m.card(cen, w, sc["audit"], both, True)
    halves = {
        "interleaved": (m.card(cen, w, sc["audit_int"][0], both, True),
                        m.card(cen, w, sc["audit_int"][1], both, True)),
        "contiguous": (m.card(cen, w, sc["audit_cont"][0], both, True),
                       m.card(cen, w, sc["audit_cont"][1], both, True)),
    }
    # the realized STATE channel through the identical pipeline (MN-6)
    slow_cen = cen["slow"]
    state = {
        "audit": slow_cen[:, sc["audit"], :].mean(axis=1),
        "int": (slow_cen[:, sc["audit_int"][0], :].mean(axis=1),
                slow_cen[:, sc["audit_int"][1], :].mean(axis=1)),
        "cont": (slow_cen[:, sc["audit_cont"][0], :].mean(axis=1),
                 slow_cen[:, sc["audit_cont"][1], :].mean(axis=1)),
    }
    b_lat = latent_identity_l2(typ, sigma_b2, eta)
    b_card_raw = m.A_SCALE * ((b_lat * m.G_PROFILE) @ world["loadings"].T)
    b_card = w["mu"] * (b_card_raw - b_card_raw.mean(axis=0, keepdims=True))
    true_card = w["mu"] * cen["trait"]
    tau = l1().latent_type_vectors(typ["S"], delta)
    tau_card = m.A_SCALE * ((tau * m.G_PROFILE) @ world["loadings"].T)
    shift = (m.A_SCALE * (((tau[typ["group"]] + b_lat) * m.G_PROFILE)
                          @ world["loadings"].T)).mean(axis=0, keepdims=True)
    centroids = w["mu"] * (tau_card - shift)
    proj = l1().card_space_type_basis(world, typ)
    return {"full": full, "fit_card": fit_card, "audit_card": audit_card,
            "halves": halves, "state": state, "true_card": true_card,
            "centroids": centroids, "b_card": b_card, "b_lat": b_lat,
            "proj": proj, "cen": cen, "w": w}


# ---------------------------------------------------------------------------
# The three grouping instruments (question A).
#
# MN-7 (rule 9): the SPIKED-PCA CENTERING convention.  estimated-S subtracts the
# POOLED COLUMN MEAN of the cards explicitly before the SVD (the cards are
# already author-centred by k2a.centered_channels, so the subtracted vector is 0
# to machine precision -- its norm is reported in G0M, not assumed), takes the
# top-k_tau RIGHT singular vectors as S_hat, and runs the SAME Lloyd in those
# k_tau coordinates.  oracle-S uses l1.card_space_type_basis (the true M(S))
# with the same Lloyd in k_tau coordinates.  Both work in the k_tau-dimensional
# COORDINATES (not the 64-dim re-embedding): Lloyd is invariant to that choice
# because the embedding is an isometry, and the coordinate form is what the
# BBP-form dimension count refers to.

def estimated_s(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    xc = x - x.mean(axis=0, keepdims=True)
    _, sv, vt = np.linalg.svd(xc, full_matrices=False)
    return vt[:K_TAU].T, sv, float(np.linalg.norm(x.mean(axis=0)))


def subspace_overlap(u_hat: np.ndarray, u_true: np.ndarray) -> float:
    """Mean squared canonical cosine between two k_tau-frames (1 = identical)."""
    s = np.linalg.svd(u_hat.T @ u_true, compute_uv=False)
    return float(np.mean(np.clip(s, 0.0, 1.0) ** 2))


def bbp_quantities(x: np.ndarray, centroids: np.ndarray, group: np.ndarray,
                   n_authors: int) -> dict[str, float]:
    """The BBP-form detectability constant on the REALIZED cell (G3M).

    Spiked model: pooled card covariance = between-type spike + within bulk.
    gamma = d/n; a spike of population variance lambda_j over bulk sigma^2 is
    label-free detectable iff theta_j := lambda_j/sigma^2 > sqrt(gamma), and the
    squared subspace overlap is then (1 - gamma/theta^2)/(1 + gamma/theta)
    (Baik-Ben Arous-Peche / Paul).  lambda_j are the eigenvalues of the
    between-type covariance (1/G) sum_g tau_g tau_g^T; sigma^2 is the mean
    per-dimension WITHIN-type variance of the same cards."""
    d = x.shape[1]
    gamma = float(d) / float(n_authors)
    cov_between = (centroids.T @ centroids) / float(G_GROUPS)
    lam = np.sort(np.linalg.eigvalsh(cov_between))[::-1][:K_TAU]
    within = x - centroids[group] if centroids.shape[0] == G_GROUPS else x
    sigma2 = float(np.einsum("id,id->", within, within) / (within.shape[0] * d))
    theta = lam / sigma2
    ov = []
    for th in theta:
        ov.append(float((1.0 - gamma / th**2) / (1.0 + gamma / th))
                  if th > math.sqrt(gamma) else 0.0)
    return {"bbp_gamma": gamma, "bbp_sigma2_bulk": sigma2,
            "bbp_lambda_min": float(lam[-1]), "bbp_lambda_max": float(lam[0]),
            "bbp_theta_min": float(theta[-1]), "bbp_theta_max": float(theta[0]),
            "bbp_threshold_theta": math.sqrt(gamma),
            "bbp_ratio_min": float(theta[-1] / math.sqrt(gamma)),
            "bbp_detectable": bool(theta[-1] > math.sqrt(gamma)),
            "bbp_pred_overlap": float(np.mean(ov))}


# ---------------------------------------------------------------------------
# The eta FLOOR CURVE on the realized geometry (question B, derivation 2).

def predicted_boundary_error_l2(world: dict, typ: dict, delta: float,
                                sigma_b2: float, eta: float,
                                identity_only: bool) -> float:
    """Mean over the six boundaries of Phi(-Delta_card/(2 sigma_u)), with

        sigma_u^2(eta) = w_mu^2 [ (1-eta)(sigma_b^2/m) ||M^T u||^2
                                + eta (sigma_b^2/k_tau) ||P_S M^T u||^2 ]

    -- the card-space realization of derivation 2's sigma_u^2(eta) = eta
    sigma_b^2/k_tau + (1-eta) sigma_b^2/m (which it reduces to exactly when M is
    an isometry).  identity_only=True is THE FLOOR (R2/appendix Q's object);
    False adds the slow-state and observation terms (the full Bayes rate)."""
    m = k2a()
    w = m.arm_weights(W_INT_ARM)
    tau = l1().latent_type_vectors(typ["S"], delta)
    mmat = m.A_SCALE * (world["loadings"] * m.G_PROFILE)          # (64,48)
    tau_card = w["mu"] * (tau @ mmat.T)
    v_full = m.ar_mean_var(N_OCC, PHI_SLOW)
    vals = []
    for g in range(G_GROUPS):
        for h in range(g + 1, G_GROUPS):
            diff = tau_card[h] - tau_card[g]
            sep = float(np.linalg.norm(diff))
            u = diff / sep
            mtu = mmat.T @ u
            var_b = w["mu"] ** 2 * (
                (1.0 - eta) * (sigma_b2 / m.K_LATENT) * float(mtu @ mtu)
                + eta * (sigma_b2 / K_TAU) * float(np.sum((typ["S"].T @ mtu) ** 2)))
            var = var_b
            if not identity_only:
                var += w["slow"] ** 2 * v_full * float(mtu @ mtu)
                var += w["noise"] ** 2 * m.SIGMA_ISO**2 / (N_OCC * m.N_REP)
            vals.append(0.0 if var <= 0.0 else
                        0.5 * math.erfc(sep / (2.0 * math.sqrt(var)) / math.sqrt(2.0)))
    return float(np.mean(vals))


def projection_gain(eta: float) -> float:
    """Derivation 1: G(eta) = 1/(eta + (1-eta) k_tau/m)."""
    m = k2a()
    return 1.0 / (eta + (1.0 - eta) * K_TAU / m.K_LATENT)


# ---------------------------------------------------------------------------
# MN-6 (rule 9): the CALIBRATED completeness meter (question C).
#
# Within a partition, the deviation card is d_i = w_mu*(trait dev) + w_slow*
# s_bar_i + w_noise*e_bar_i, and in K2a's normalized units (l1._norm_dot)
#     V_full = A + B*v + E/(n_audit*n_rep),   C_sigma = A + B*c_sigma.
# L1 solved this with the THEORETICAL AR constants c_sigma = k2a.ar_cross_cov
# and found B_hat = 0.245861 instead of w_slow^2 = 0.25 in every cell -- a
# -1.66% systematic, which propagates (0.25 - B_hat)*c_cont = +0.002754 into
# A_hat and cost V-4 its tracking clause (appendix Q.5: "it needs the constant").
#
# THE CALIBRATION, pinned here before any hypothesis number: replace the
# theoretical (v, c_int, c_cont) by the PANEL-EXACT realized ones, measured on
# the same world's own slow channel through the IDENTICAL pipeline (same
# author-centring by k2a.centered_channels, same group-centring by the SAME
# labels the meter uses, same normalization):
#     c_hat_sigma := _norm_dot(P_g s_bar^(sigma,1), P_g s_bar^(sigma,2))
#     B_hat_cal   := (C_int - C_cont)/(c_hat_int - c_hat_cont)      -> w_slow^2
#     A_hat_cal   := C_cont - B_hat_cal * c_hat_cont
#     S_id        := A_hat_cal / V_full
# This is a per-world CALIBRATION CONSTANT supplied to the meter, derived from
# generator truth about the STATE channel (not about the labels); it is the
# meter's upper bound once its state constant is right.  DECLARED READINGS, all
# reported: (2) L1's form with the theoretical AR constants; (3) the design-B
# contiguous form A = C_cont - w_slow^2 * c_cont.
#
# MN-8 (rule 9): the TARGET.  L1's target was the designed b-share of within-
# TRUE-group deviations.  Under an ESTIMATED partition the analogue that R3
# actually defines ("the surviving-identity share of ITS within-group
# deviations") is the PERSISTENT-CONTENT share of the same deviations:
#     target := w_mu^2 <P_g c_trait, P_g c_trait> / V_full
# with c_trait the noise-free trait card (tau + b).  Under a CORRECT partition
# tau cancels exactly and this IS L1's b-share; under an incorrect one it also
# carries the leaked type offsets -- which are part of that typology's
# completeness defect, not of its state or noise.  SECOND READING: the pure
# b-share under the same partition (tau leakage excluded), reported everywhere.

def audit_meter_l2(obj: dict[str, Any], labels: np.ndarray, tag: str) -> dict[str, float]:
    m = k2a()
    lg = l1()
    w = obj["w"]
    sc = occasion_scheme()
    c_int_th = m.ar_cross_cov(sc["audit_int"][0], sc["audit_int"][1], PHI_SLOW)
    c_cont_th = m.ar_cross_cov(sc["audit_cont"][0], sc["audit_cont"][1], PHI_SLOW)

    def gc(x: np.ndarray) -> np.ndarray:
        out = x.copy()
        for g in np.unique(labels):
            sel = labels == g
            out[sel] -= x[sel].mean(axis=0, keepdims=True)
        return out

    d_full = gc(obj["audit_card"])
    v_full = lg._norm_dot(d_full, d_full)
    caps = {}
    for name in ("interleaved", "contiguous"):
        h1, h2 = obj["halves"][name]
        caps[name] = lg._norm_dot(gc(h1), gc(h2))
    c_hat_int = lg._norm_dot(gc(obj["state"]["int"][0]), gc(obj["state"]["int"][1]))
    c_hat_cont = lg._norm_dot(gc(obj["state"]["cont"][0]), gc(obj["state"]["cont"][1]))
    v_hat_state = lg._norm_dot(gc(obj["state"]["audit"]), gc(obj["state"]["audit"]))
    b_cal = (caps["interleaved"] - caps["contiguous"]) / (c_hat_int - c_hat_cont)
    a_cal = caps["contiguous"] - b_cal * c_hat_cont
    b_th = (caps["interleaved"] - caps["contiguous"]) / (c_int_th - c_cont_th)
    a_th = caps["contiguous"] - b_th * c_cont_th
    a_design_b = caps["contiguous"] - (w["slow"] ** 2) * c_cont_th
    trait_dev = gc(w["mu"] * obj["cen"]["trait"])
    b_dev = gc(obj["b_card"])
    return {
        f"{tag}_V_full": v_full,
        f"{tag}_C_int": caps["interleaved"], f"{tag}_C_cont": caps["contiguous"],
        f"{tag}_c_hat_int": c_hat_int, f"{tag}_c_hat_cont": c_hat_cont,
        f"{tag}_v_hat_state": v_hat_state,
        f"{tag}_B_hat_cal": b_cal, f"{tag}_B_hat_theory": b_th,
        f"{tag}_S_id": a_cal / v_full,
        f"{tag}_S_id_theory": a_th / v_full,
        f"{tag}_S_id_designB": a_design_b / v_full,
        f"{tag}_target": lg._norm_dot(trait_dev, trait_dev) / v_full,
        f"{tag}_target_bonly": lg._norm_dot(b_dev, b_dev) / v_full,
    }


# ---------------------------------------------------------------------------
# Part-0 PREDICTION STREAM (G1M/G2M/G3M).  An INDEPENDENT re-implementation of
# the card law on a prediction-only seed stream ('m4l2-pred'): no world of any
# index -- main or pilot -- is generated here.

def pred_population_l2(delta: float, sigma_b2: float, eta: float, seed: int,
                       n_authors: int = N_AUTHORS) -> dict[str, np.ndarray]:
    m = k2a()
    from suica_core.v8_context_relation_field import _orthonormal_loadings
    rng = np.random.default_rng(seed)
    load = _orthonormal_loadings(rng, m.DIM, m.K_LATENT)
    basis = np.linalg.qr(rng.normal(size=(m.K_LATENT, K_TAU)))[0]
    mmat = m.A_SCALE * (load * m.G_PROFILE)
    w = m.arm_weights(W_INT_ARM)
    tau = l1().latent_type_vectors(basis, delta)
    group = np.repeat(np.arange(G_GROUPS), n_authors // G_GROUPS)
    xi = rng.normal(size=(n_authors, m.K_LATENT))
    zeta = rng.normal(size=(n_authors, m.K_LATENT))
    b = np.zeros_like(xi)
    if eta < 1.0:
        b = b + math.sqrt((1.0 - eta) * sigma_b2 / m.K_LATENT) * xi
    if eta > 0.0:
        b = b + math.sqrt(eta * sigma_b2 / K_TAU) * ((zeta @ basis) @ basis.T)
    v_full = m.ar_mean_var(N_OCC, PHI_SLOW)
    s = math.sqrt(v_full) * rng.normal(size=(n_authors, m.K_LATENT))
    card = w["mu"] * ((tau[group] + b) @ mmat.T) + w["slow"] * (s @ mmat.T)
    card = card + w["noise"] * m.SIGMA_ISO / math.sqrt(N_OCC * m.N_REP) * rng.normal(
        size=(n_authors, m.DIM))
    shift = card.mean(axis=0, keepdims=True)
    card = card - shift
    centroids = w["mu"] * (tau @ mmat.T) - shift
    proj = np.linalg.qr(mmat @ basis)[0]
    return {"card": card, "group": group, "centroids": centroids, "proj": proj}


def pred_seed(rep: int) -> int:
    return int(v8.stable_bucket(f"pred-{rep}", salt="m4l2-pred", modulus=2**63 - 1))


def pred_instruments(delta: float, sigma_b2: float, eta: float, reps: int) -> dict[str, float]:
    lg = l1()
    amb, orc, est, ocn, ovl = [], [], [], [], []
    for r in range(reps):
        p = pred_population_l2(delta, sigma_b2, eta, pred_seed(r))
        x, g = p["card"], p["group"]
        seed = int(v8.stable_bucket(f"{r}-{delta:.9f}-{sigma_b2:.9f}-{eta:g}",
                                    salt="m4l2-predkm", modulus=2**63 - 1))
        amb.append(lg.adjusted_rand_index(g, lg.kmeans_lloyd(x, G_GROUPS, N_RESTART, seed)[0]))
        orc.append(lg.adjusted_rand_index(
            g, lg.kmeans_lloyd(x @ p["proj"], G_GROUPS, N_RESTART, seed + 1)[0]))
        u_hat, _, _ = estimated_s(x)
        est.append(lg.adjusted_rand_index(
            g, lg.kmeans_lloyd(x @ u_hat, G_GROUPS, N_RESTART, seed + 2)[0]))
        d = ((x[:, None, :] - p["centroids"][None, :, :]) ** 2).sum(axis=2)
        ocn.append(lg.adjusted_rand_index(g, d.argmin(axis=1)))
        ovl.append(subspace_overlap(u_hat, p["proj"]))
    return {"ambient": float(np.mean(amb)), "oracleS": float(np.mean(orc)),
            "estS": float(np.mean(est)), "oracle_centroid": float(np.mean(ocn)),
            "overlap": float(np.mean(ovl)), "reps": reps,
            "ambient_sd": float(np.std(amb, ddof=1)) if reps > 1 else 0.0,
            "oracleS_sd": float(np.std(orc, ddof=1)) if reps > 1 else 0.0}


def ladder_grid() -> pd.DataFrame:
    """MN-3 step (i): ONE fine Delta grid on the prediction stream, all three
    instruments plus the oracle-centroid (Bayes) curve and both floor readings.
    Everything downstream -- the ladder, the bracket, the rule-18 joint
    satisfiability intervals, the rule-19 fidelity predictions -- is read off
    THIS grid, computed once, before any world of this leg exists."""
    rows = []
    for delta in np.geomspace(LADDER_GRID_LO, LADDER_GRID_HI, LADDER_GRID_N):
        d = float(delta)
        rec = {"delta": d, **pred_instruments(d, SB2_RHO55, 0.0, LADDER_REPS)}
        rec.update(pred_floor_closed_form(d, SB2_RHO55, 0.0))
        rows.append(rec)
    return pd.DataFrame(rows)


def pred_floor_closed_form(delta: float, sigma_b2: float, eta: float) -> dict[str, float]:
    """The Part-0 floor prediction on the PREDICTION-stream geometry (an
    independent draw of the loadings and S, so this is a law-level number, not a
    world-level one).  Averaged over the prediction replicates' own geometries."""
    m = k2a()
    from suica_core.v8_context_relation_field import _orthonormal_loadings
    ids, fulls = [], []
    for r in range(LADDER_REPS):
        rng = np.random.default_rng(pred_seed(r))
        load = _orthonormal_loadings(rng, m.DIM, m.K_LATENT)
        basis = np.linalg.qr(rng.normal(size=(m.K_LATENT, K_TAU)))[0]
        fake_world = {"loadings": load}
        fake_typ = {"S": basis}
        ids.append(predicted_boundary_error_l2(fake_world, fake_typ, delta, sigma_b2, eta, True))
        fulls.append(predicted_boundary_error_l2(fake_world, fake_typ, delta, sigma_b2, eta, False))
    return {"floor_identity": float(np.mean(ids)), "floor_full": float(np.mean(fulls))}


def _isotonic(y: np.ndarray) -> np.ndarray:
    return np.maximum.accumulate(y)


def solve_ladder(grid: pd.DataFrame) -> dict[str, Any]:
    """MN-3 step (ii): the five Delta are the points where the ISOTONIZED
    ambient-ARI grid curve crosses LADDER_TARGETS, by linear interpolation in
    log Delta.  Isotonization (cumulative max in Delta) is the pinned handling
    of replicate noise in a curve the law makes monotone; the raw and isotonized
    curves are both written to the report."""
    d = grid["delta"].to_numpy(float)
    y = _isotonic(grid["ambient"].to_numpy(float))
    ladder, notes = [], []
    for tgt in LADDER_TARGETS:
        if tgt <= y[0]:
            ladder.append(float(d[0])); notes.append("clipped_low")
        elif tgt >= y[-1]:
            ladder.append(float(d[-1])); notes.append("clipped_high")
        else:
            j = int(np.searchsorted(y, tgt))
            y0, y1, d0, d1 = y[j - 1], y[j], d[j - 1], d[j]
            frac = 0.0 if y1 == y0 else (tgt - y0) / (y1 - y0)
            ladder.append(float(math.exp(math.log(d0) + frac * (math.log(d1) - math.log(d0)))))
            notes.append("interpolated")
    return {"targets": list(LADDER_TARGETS), "delta": ladder, "notes": notes,
            "grid_lo": LADDER_GRID_LO, "grid_hi": LADDER_GRID_HI,
            "grid_n": LADDER_GRID_N, "grid_reps": LADDER_REPS}


def _interval(d: np.ndarray, ok: np.ndarray) -> list[float] | None:
    if not ok.any():
        return None
    idx = np.nonzero(ok)[0]
    return [float(d[idx[0]]), float(d[idx[-1]])]


def joint_satisfiability(grid: pd.DataFrame, ladder: list[float]) -> dict[str, Any]:
    """G2M (standing rule 18, FIRST APPLICATION): every clause that shares the
    T-arm knobs (sigma_b^2 fixed, eta = 0, Delta the only free knob) is reduced
    to a SET OF DELTA, and the sets are intersected.  A clause pair with empty
    intersection is jointly unsatisfiable no matter which ladder is chosen."""
    d = grid["delta"].to_numpy(float)
    amb = _isotonic(grid["ambient"].to_numpy(float))
    orc = _isotonic(grid["oracleS"].to_numpy(float))
    ocn = _isotonic(grid["oracle_centroid"].to_numpy(float))
    est = _isotonic(grid["estS"].to_numpy(float))
    fl_id = grid["floor_identity"].to_numpy(float)
    fl_fu = grid["floor_full"].to_numpy(float)
    sets = {
        "G1M_bracket_low  (ambient < 0.30)": amb < BRACKET_LO,
        "G1M_bracket_high (ambient > 0.80)": amb > BRACKET_HI,
        "W-1a (ambient < 0.30)": amb < BRACKET_LO,
        "W-1a (oracle-S > 0.80)": orc > W1_ORACLE_BAR,
        "design: identity-only floor < 0.005": fl_id < FLOOR_BAR,
        "design: full Bayes floor < 0.005": fl_fu < FLOOR_BAR,
        "necessary: Bayes ceiling > 0.80": ocn > W1_ORACLE_BAR,
        "W-1b (oracle-S >= ambient)": orc >= amb,
        "W-2 (|estS - oracleS| <= 0.02)": np.abs(est - orc) <= 0.02,
    }
    out = {"delta_grid": [float(x) for x in d],
           "clause_delta_intervals": {k: _interval(d, v) for k, v in sets.items()}}
    pairs = {}
    keys = list(sets)
    for a, b in itertools.combinations(keys, 2):
        inter = sets[a] & sets[b]
        pairs[f"{a}  AND  {b}"] = {
            "satisfiable": bool(inter.any()), "delta_interval": _interval(d, inter)}
    out["pairwise"] = pairs
    w1 = sets["W-1a (ambient < 0.30)"] & sets["W-1a (oracle-S > 0.80)"]
    w1_floor = w1 & sets["design: identity-only floor < 0.005"]
    ladder_arr = np.asarray(ladder)
    out["W1_window"] = {
        "satisfiable_anywhere_in_delta": bool(w1.any()),
        "delta_interval": _interval(d, w1),
        "n_grid_points": int(w1.sum()),
        "with_floor_clause_satisfiable": bool(w1_floor.any()),
        "with_floor_clause_interval": _interval(d, w1_floor),
        "n_ladder_rungs_inside": int(sum(
            bool(np.interp(x, d, amb) < BRACKET_LO and np.interp(x, d, orc) > W1_ORACLE_BAR)
            for x in ladder_arr)),
        "required_by_W1": W1_MIN_CELLS,
    }
    out["bracket_satisfied_by_ladder"] = {
        "min_ambient_on_ladder": float(min(np.interp(x, d, amb) for x in ladder_arr)),
        "max_ambient_on_ladder": float(max(np.interp(x, d, amb) for x in ladder_arr)),
    }
    out["floor_on_ladder_identity"] = [float(np.interp(x, d, fl_id)) for x in ladder_arr]
    out["floor_on_ladder_full"] = [float(np.interp(x, d, fl_fu)) for x in ladder_arr]
    return out


# ---------------------------------------------------------------------------
# rule-16 enumeration (G4M)

SUB_STATES = ("HOLD", "MISS", "BOUNDARY", "UNREALIZABLE")
LEAN_STATES = ("HOLD", "MISS", "BOUNDARY")
LEAN_SUBCLAUSES = {
    "W-1": [">=2 T-cells with ambient<0.3 AND oracle-S>0.8 (CIs on the stated sides)",
            "no T-cell with the reverse ordering (oracle-S < ambient, CI)"],
    "W-2": ["estimated-S within CI of oracle-S in EVERY detectable T-cell"],
    "W-3": ["floor-curve CI containment >=7/10 C-cells",
            "eta-ordering exact at both energies"],
    "W-4": ["cross-fitted calibrated audit tracks designed share >=8/10 C-cells",
            "same-data bias has the predicted (optimistic) sign, pooled CI excludes 0"],
}


def lean_from_subclauses(states: tuple[str, ...]) -> str:
    """MN-9: CONJUNCTIVE aggregation, identical to L1's RN-11 (K3's rule).  Any
    MISS -> MISS; else any BOUNDARY -> BOUNDARY; else HOLD.  UNREALIZABLE
    sub-clauses are EXCLUDED from the conjunction and disclosed in the lean's
    tag; if every sub-clause is UNREALIZABLE the lean is BOUNDARY."""
    live = [s for s in states if s != "UNREALIZABLE"]
    if not live:
        return "BOUNDARY"
    if "MISS" in live:
        return "MISS"
    if "BOUNDARY" in live:
        return "BOUNDARY"
    return "HOLD"


def route(lean_states: dict[str, str], bracket_ok: bool) -> str:
    if not bracket_ok:
        return "P1M"
    if lean_states["W-1"] == "MISS":
        return "P2M"
    misses = sum(1 for k in ("W-2", "W-3", "W-4") if lean_states[k] == "MISS")
    return "P3M" if misses >= 2 else "P4M"


def build_enumeration() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    rows = []
    for lean, subs in LEAN_SUBCLAUSES.items():
        for combo in itertools.product(SUB_STATES, repeat=len(subs)):
            rows.append({"lean": lean, "n_subclauses": len(subs),
                         "subclause_states": "|".join(combo),
                         "lean_state": lean_from_subclauses(combo)})
    layer_a = pd.DataFrame(rows)
    rows2 = []
    for bracket_ok in (True, False):
        for combo in itertools.product(LEAN_STATES, repeat=4):
            states = dict(zip(["W-1", "W-2", "W-3", "W-4"], combo, strict=True))
            rows2.append({"bracket_ok": bracket_ok,
                          **{f"state_{k}": v for k, v in states.items()},
                          "n_miss": sum(1 for v in combo if v == "MISS"),
                          "n_boundary": sum(1 for v in combo if v == "BOUNDARY"),
                          "route": route(states, bracket_ok)})
    layer_b = pd.DataFrame(rows2)
    reg = layer_b[(layer_b["bracket_ok"]) & (
        layer_b[[f"state_W-{i}" for i in (1, 2, 3, 4)]] != "BOUNDARY").all(axis=1)]
    audit = {
        "layer_a_rows": int(len(layer_a)),
        "layer_a_expected": int(sum(len(SUB_STATES) ** len(s)
                                    for s in LEAN_SUBCLAUSES.values())),
        "layer_a_unique_keys": int(
            layer_a[["lean", "subclause_states"]].drop_duplicates().shape[0]),
        "layer_a_all_assigned": bool(layer_a["lean_state"].isin(LEAN_STATES).all()),
        "layer_b_rows": int(len(layer_b)),
        "layer_b_expected": 2 * len(LEAN_STATES) ** 4,
        "layer_b_unique_keys": int(layer_b[
            ["bracket_ok"] + [f"state_W-{i}" for i in (1, 2, 3, 4)]].drop_duplicates().shape[0]),
        "layer_b_all_assigned": bool(layer_b["route"].isin(
            ["P1M", "P2M", "P3M", "P4M"]).all()),
        "layer_b_route_counts": {k: int(v) for k, v in layer_b["route"].value_counts().items()},
        "layer_b_all_routes_reachable": bool(
            set(layer_b["route"]) == {"P1M", "P2M", "P3M", "P4M"}),
        "registered_2pow4_rows": int(len(reg)),
        "registered_2pow4_route_counts": {
            k: int(v) for k, v in reg["route"].value_counts().items()},
    }
    audit["layer_a_no_gap_no_overlap"] = bool(
        audit["layer_a_rows"] == audit["layer_a_expected"] == audit["layer_a_unique_keys"]
        and audit["layer_a_all_assigned"])
    audit["layer_b_no_gap_no_overlap"] = bool(
        audit["layer_b_rows"] == audit["layer_b_expected"] == audit["layer_b_unique_keys"]
        and audit["layer_b_all_assigned"])
    return layer_a, layer_b, audit


# ---------------------------------------------------------------------------
# per-(cell, world) measurement

def measure_cell_world(world: dict, typ: dict, spec: dict[str, Any],
                       world_seed: int) -> dict[str, Any]:
    m, lg = k2a(), l1()
    cid, delta, sb2, eta = spec["cell"], spec["delta"], spec["sigma_b2"], spec["eta"]
    obj = cards_for_cell(world, typ, delta, sb2, eta)
    group = typ["group"]
    x = obj["full"]
    sd = int(v8.stable_bucket(f"{world_seed}-{cid}", salt="m4l2-kmeans", modulus=2**63 - 1))
    lab_a, in_a = lg.kmeans_lloyd(x, G_GROUPS, N_RESTART, sd)
    lab_o, in_o = lg.kmeans_lloyd(x @ obj["proj"], G_GROUPS, N_RESTART, sd + 1)
    u_hat, sv, gm_norm = estimated_s(x)
    lab_e, in_e = lg.kmeans_lloyd(x @ u_hat, G_GROUPS, N_RESTART, sd + 2)
    d2 = ((x[:, None, :] - obj["centroids"][None, :, :]) ** 2).sum(axis=2)
    lab_c = d2.argmin(axis=1)
    # cross-fitting: cluster on the FIT occasion-half, audit on the AUDIT half
    lab_fit, _ = lg.kmeans_lloyd(obj["fit_card"], G_GROUPS, N_RESTART, sd + 3)
    lab_same, _ = lg.kmeans_lloyd(obj["audit_card"], G_GROUPS, N_RESTART, sd + 4)
    ev = sv**2
    row: dict[str, Any] = {
        "cell": cid, "kind": spec["kind"], "rung": spec["rung"], "energy": spec["energy"],
        "delta": delta, "sigma_b2": sb2, "eta": eta, "world_seed": world_seed,
        "n_authors": int(x.shape[0]),
        "ari_ambient": lg.adjusted_rand_index(group, lab_a),
        "ari_oracleS": lg.adjusted_rand_index(group, lab_o),
        "ari_estS": lg.adjusted_rand_index(group, lab_e),
        "ari_oracle_centroid": lg.adjusted_rand_index(group, lab_c),
        "acc_ambient": lg.hungarian_accuracy(group, lab_a),
        "acc_oracleS": lg.hungarian_accuracy(group, lab_o),
        "acc_estS": lg.hungarian_accuracy(group, lab_e),
        "inertia_ambient": in_a, "inertia_oracleS": in_o, "inertia_estS": in_e,
        "overlap_estS": subspace_overlap(u_hat, obj["proj"]),
        "eigengap_ratio": float(ev[K_TAU - 1] / ev[K_TAU]),
        "eigengap_abs": float(ev[K_TAU - 1] - ev[K_TAU]),
        "pca_grand_mean_norm": gm_norm,
        "ari_fit_half": lg.adjusted_rand_index(group, lab_fit),
        "ari_same_half": lg.adjusted_rand_index(group, lab_same),
        "boundary_err_true_card": lg.boundary_error_rate(
            obj["true_card"], obj["centroids"], group),
        "boundary_err_full_card": lg.boundary_error_rate(x, obj["centroids"], group),
        "floor_pred_identity": predicted_boundary_error_l2(world, typ, delta, sb2, eta, True),
        "floor_pred_full": predicted_boundary_error_l2(world, typ, delta, sb2, eta, False),
        "projection_gain_G_eta": projection_gain(eta),
    }
    row.update(bbp_quantities(x, obj["centroids"], group, N_AUTHORS))
    row.update(audit_meter_l2(obj, lab_fit, "xf"))       # PRIMARY: cross-fitted
    row.update(audit_meter_l2(obj, lab_same, "sd"))      # SECOND: same-data
    row.update(audit_meter_l2(obj, group, "or"))         # oracle groups (L1 calibration)
    # realized design quantities (G0M)
    b_lat = obj["b_lat"]
    tau = lg.latent_type_vectors(typ["S"], delta)
    e_tot = float(np.mean(np.einsum("ij,ij->i", b_lat, b_lat)))
    in_s = (b_lat @ typ["S"])
    e_in_s = float(np.mean(np.einsum("ij,ij->i", in_s, in_s)))
    frac_s = e_in_s / e_tot if e_tot > 0 else 0.0
    kfrac = K_TAU / m.K_LATENT
    row["realized_sigma_b2"] = e_tot
    row["realized_energy_in_S_fraction"] = frac_s
    row["realized_eta"] = (frac_s - kfrac) / (1.0 - kfrac) if e_tot > 0 else 0.0
    pw = np.linalg.norm(tau[:, None, :] - tau[None, :, :], axis=2)[
        np.triu_indices(G_GROUPS, 1)]
    row["realized_delta_latent_min"] = float(pw.min())
    row["realized_delta_latent_max"] = float(pw.max())
    cpw = np.linalg.norm(obj["centroids"][:, None, :] - obj["centroids"][None, :, :],
                         axis=2)[np.triu_indices(G_GROUPS, 1)]
    row["realized_delta_card_min"] = float(cpw.min())
    row["realized_delta_card_mean"] = float(cpw.mean())
    row["card_var_norm"] = lg._norm_dot(x, x)
    return row


def run_world_cells(world: int, cells: list[dict[str, Any]],
                    n_authors: int = N_AUTHORS) -> list[dict[str, Any]]:
    wseed = world_seed_for(world)
    world_obj, typ = build_typed_world_l2(wseed, n_authors)
    return [measure_cell_world(world_obj, typ, spec, wseed) for spec in cells]


# ---------------------------------------------------------------------------
# G3M: the rule-19 FIDELITY TABLE

def fidelity_table(grid: pd.DataFrame, ladder: dict[str, Any],
                   c_pred: pd.DataFrame) -> list[dict[str, str]]:
    m = k2a()
    d = grid["delta"].to_numpy(float)
    amb = _isotonic(grid["ambient"].to_numpy(float))
    ocn = _isotonic(grid["oracle_centroid"].to_numpy(float))
    orc = _isotonic(grid["oracleS"].to_numpy(float))
    lad = ladder["delta"]
    d_amb_break = float(np.interp(0.5, amb, d))
    d_bayes_08 = float(np.interp(W1_ORACLE_BAR, ocn, d))
    d_amb_03 = float(np.interp(BRACKET_LO, amb, d))
    ratio_pred = (K_TAU / m.DIM) ** 0.25
    return [
        {
            "lean": "W-1",
            "theorem_quantity":
                "appendix Q.3 (R2 restated): the centroid-LOCALIZATION threshold "
                "-- the Delta below which AMBIENT distance clustering cannot find "
                "the type structure at all, while the same clustering inside the "
                "k_tau-dim type subspace still can, because projection divides the "
                "working-space identity energy by G(0) = m/k_tau = "
                f"{projection_gain(0.0)!r}",
            "predicted":
                "BBP-form thresholds in the CARD separation: a between-type spike "
                "lambda = Delta_card^2/8 is found against a bulk sigma^2 iff "
                "lambda > sigma^2 sqrt(d/n), so the break scales as Delta ~ "
                "sigma (d/n)^(1/4) and the projected break sits at a factor "
                f"(k_tau/DIM)^(1/4) = {ratio_pred!r} of the ambient one.  Measured "
                f"on the Part-0 grid: ambient ARI = 0.5 at Delta = {d_amb_break!r}, "
                f"ambient ARI = 0.30 at Delta = {d_amb_03!r}; the projection-"
                "invariant Bayes ceiling (oracle-centroid ARI, identical ambient and "
                f"projected by Q.1) reaches 0.80 only at Delta = {d_bayes_08!r}",
            "bar": "in >=2 T-cells: ambient ARI < 0.30 AND oracle-S ARI > 0.80, "
                   "per-cell CIs on the stated sides; no reversed cell",
            "why_this_quantity":
                "Q.3 relocated R2's ISO half from achieved ARI (defect #30) to the "
                "localization threshold, and the only observable that separates "
                "'cannot localize' from 'localized but Bayes-limited' is the PAIR "
                "(ambient ARI, projected ARI) read across the threshold",
        },
        {
            "lean": "W-2",
            "theorem_quantity":
                "derivation 3's detectability caveat: consistency of the top-k_tau "
                "spiked-PCA subspace estimate, whose own quantity is the SUBSPACE "
                "OVERLAP |<S_hat, S>|^2, not an ARI",
            "predicted":
                "theta_j := lambda_j/sigma^2, gamma := d/n = 64/512 = 0.125, "
                f"sqrt(gamma) = {math.sqrt(0.125)!r}; detectable iff theta > "
                "sqrt(gamma); squared overlap = (1 - gamma/theta^2)/(1 + gamma/theta) "
                "(Baik-Ben Arous-Peche / Paul).  Per-rung theta and predicted overlap "
                "are in the Part-0 ladder table; the measured overlap column "
                "`overlap_estS` reads the same quantity in the arms",
            "bar": "estimated-S ARI within CI of oracle-S ARI in EVERY T-cell on "
                   "the detectable side of theta = sqrt(gamma)",
            "why_this_quantity":
                "the registered bar is an ARI equality, which the BBP law does NOT "
                "predict just above threshold (the overlap rises CONTINUOUSLY from "
                "0 there); the overlap row is carried as the theorem-faithful "
                "companion so the bar's outcome can be read against the law it "
                "shadows",
        },
        {
            "lean": "W-3",
            "theorem_quantity":
                "derivation 2 / appendix Q.1: the projection-invariant per-boundary "
                "floor Phi(-Delta/(2 sigma_u(eta))) with sigma_u^2(eta) = "
                "eta sigma_b^2/k_tau + (1-eta) sigma_b^2/m",
            "predicted":
                "the closed-form curve on each world's REALIZED geometry "
                "(predicted_boundary_error_l2, identity_only=True), which reduces to "
                "the latent form exactly when M is an isometry; per-cell values in "
                "the Part-0 C-arm table.  The curve is strictly increasing in eta at "
                "both energies because sigma_b^2/k_tau > sigma_b^2/m (16x at 48/3)",
            "bar": "measured TRUE-CARD per-boundary rate within CI of the curve in "
                   ">=7/10 C-cells AND the eta-ordering exact at both energies",
            "why_this_quantity":
                "the floor IS the theorem's own object (a per-boundary rate), and "
                "L1 already measured it rate-vs-rate at the two poles; the only new "
                "content is the interpolation law in eta",
        },
        {
            "lean": "W-4",
            "theorem_quantity":
                "R3's completeness meter: the surviving-identity SHARE of a "
                "partition's within-group deviations, after appendix Q.5's one "
                "calibration constant (L1: B_hat = " f"{L1_B_HAT!r} vs w_slow^2 = "
                "0.25, propagating (0.25 - B_hat) c_cont = " f"{L1_AUDIT_OFFSET!r} "
                "into A_hat), plus derivation 4's cross-fitting bias",
            "predicted":
                "with the panel-exact per-world state constants (MN-6) B_hat_cal -> "
                "w_slow^2 = 0.25 EXACTLY and S_id -> the designed persistent-content "
                "share (MN-8) of the same within-group deviations; the SAME-DATA "
                "reading is predicted STRICTLY SMALLER than the cross-fitted one "
                "(derivation 4: nearest-centroid assignment truncates the "
                "boundary-crossing part of the deviations, so fitting and auditing "
                "on the same occasions absorbs identity into the partition)",
            "bar": "cross-fitted calibrated audit CI contains the designed share in "
                   ">=8/10 C-cells; pooled (same-data - cross-fitted) CI excludes 0 "
                   "on the NEGATIVE (optimistic) side",
            "why_this_quantity":
                "R3 defines the audit as a SHARE, and the bias derivation predicts a "
                "SIGN on the difference of two shares; the size of the bias is "
                "reported as a measured named quantity and is deliberately NOT a bar",
        },
    ]


# ---------------------------------------------------------------------------
# Stage: part0

def run_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    m, lg = k2a(), l1()
    gates: dict[str, Any] = {
        "leg": "M4-L2", "banner": BANNER,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED, "pilot_worlds": list(PILOT_WORLDS),
        "n_authors": N_AUTHORS, "worlds_per_cell": WORLDS_PER_CELL,
        "G": G_GROUPS, "k_tau": K_TAU, "k_latent": m.K_LATENT, "dim": m.DIM,
        "phi_slow": PHI_SLOW, "n_occ": N_OCC, "w_int_arm": W_INT_ARM,
        "n_restart": N_RESTART,
        "knobs": {"delta_sigma_b_decoupled": True, "L1_delta": L1_DELTA,
                  "L1_sigma_tau2": L1_SIGMA_TAU2, "sigma_b2_rho55eq": SB2_RHO55,
                  "sigma_b2_rho35eq": SB2_RHO35, "eta_levels": list(ETA_LEVELS)},
        "grain": {"analysis_grain": "world (8 independent world blocks per cell)",
                  "rule5_justification": "every registered statistic is a per-world "
                  "scalar (an ARI, a per-boundary rate, a variance share); the paired "
                  "world-block bootstrap over the 8 worlds is the only independent "
                  "resampling unit, and the 4-world pilot MDEs are at that grain"},
    }
    st: dict[str, float] = {}

    # ---- MN-3: the ladder (prediction stream only; no world of this leg exists)
    t = time.time()
    grid = ladder_grid()
    grid.to_csv(OUT / "part0_ladder_grid.csv", index=False)
    lad = solve_ladder(grid)
    ladder = lad["delta"]
    st["ladder_grid"] = time.time() - t
    gates["ladder_rule"] = {
        "rule": "MN-3", "ambient_ari_targets": list(LADDER_TARGETS),
        "delta": ladder, "notes": lad["notes"],
        "grid": {"lo": LADDER_GRID_LO, "hi": LADDER_GRID_HI, "n": LADDER_GRID_N,
                 "reps": LADDER_REPS},
        "sigma_b2_fixed": SB2_RHO55,
        "ladder_shift_rule": (
            "rule 17, EXACTLY ONE step, pre-declared: if the PILOT bracket clause "
            "fails (pilot ambient ARI does not span (<0.30, >0.80) across the five "
            "rungs), the five Delta are re-solved by the identical interpolation "
            "against the PILOT-WORLD ambient curve (RESERVED worlds 9901-9904) "
            "instead of the prediction stream; the shift is disclosed and Part 0 is "
            "re-reported at the shifted ladder."),
        "shift_fired": False,
    }

    # ---- G3M: the rule-19 fidelity table + the C-arm Part-0 predictions
    t = time.time()
    c_rows = []
    for name, sb2 in C_ENERGIES:
        for eta in ETA_LEVELS:
            pr = pred_instruments(L1_DELTA, sb2, eta, PRED_REPS_INSTRUMENT)
            fl = pred_floor_closed_form(L1_DELTA, sb2, eta)
            c_rows.append({"cell": c_cell_id(name, eta), "energy": name, "eta": eta,
                           "delta": L1_DELTA, "sigma_b2": sb2,
                           "sigma_u2_latent": eta * sb2 / K_TAU
                           + (1 - eta) * sb2 / m.K_LATENT,
                           "projection_gain_G_eta": projection_gain(eta), **fl, **pr})
    c_pred = pd.DataFrame(c_rows)
    t_rows = []
    for i, dl in enumerate(ladder):
        pr = pred_instruments(dl, SB2_RHO55, 0.0, PRED_REPS_INSTRUMENT)
        fl = pred_floor_closed_form(dl, SB2_RHO55, 0.0)
        pop = pred_population_l2(dl, SB2_RHO55, 0.0, pred_seed(0))
        bb = bbp_quantities(pop["card"], pop["centroids"], pop["group"], N_AUTHORS)
        t_rows.append({"cell": t_cell_id(i), "rung": i, "delta": dl,
                       "sigma_b2": SB2_RHO55, "eta": 0.0,
                       "ambient_target": LADDER_TARGETS[i], **fl, **pr, **bb})
    t_pred = pd.DataFrame(t_rows)
    pd.concat([t_pred, c_pred], ignore_index=True).to_csv(
        OUT / "part0_predictions.csv", index=False)
    fid = fidelity_table(grid, lad, c_pred)
    st["predictions"] = time.time() - t
    gates["G3M"] = {
        "pass": True, "artifact": "part0_predictions.csv",
        "fidelity_table": fid,
        "bbp_constant": {"gamma": m.DIM / N_AUTHORS,
                         "sqrt_gamma": math.sqrt(m.DIM / N_AUTHORS),
                         "per_rung_theta_min": [float(r["bbp_theta_min"]) for r in t_rows],
                         "per_rung_detectable": [bool(r["bbp_detectable"]) for r in t_rows],
                         "per_rung_pred_overlap": [float(r["bbp_pred_overlap"])
                                                   for r in t_rows]},
        "floor_curve_c_arms": {r["cell"]: float(r["floor_identity"]) for r in c_rows},
        "floor_curve_monotone_in_eta": {
            name: bool(all(a < b for a, b in zip(
                [r["floor_identity"] for r in c_rows if r["energy"] == name],
                [r["floor_identity"] for r in c_rows if r["energy"] == name][1:],
                strict=False))) for name, _ in C_ENERGIES},
    }

    # ---- G0M / G1M on the RESERVED pilot worlds + the L1 anchors
    t = time.time()
    cells = all_cells(ladder)
    pilot_rows = []
    g0: dict[str, Any] = {"recon_residual_max": 0.0, "sigma_b2_rel_dev_max": 0.0,
                          "eta_dev_abs_max": 0.0, "delta_latent_dev_abs_max": 0.0,
                          "pca_grand_mean_norm_max": 0.0, "per_world": [],
                          "eta_mixture_energy_residual_max": 0.0}
    g1: dict[str, Any] = {"per_world": []}
    for world in PILOT_WORLDS:
        wseed = world_seed_for(world)
        world_obj, typ = build_typed_world_l2(wseed, N_AUTHORS)
        w = m.arm_weights(W_INT_ARM)
        trait = typed_trait_l2(world_obj, typ, L1_DELTA, SB2_RHO55, 0.5)
        w2 = dict(world_obj); w2["trait"] = trait
        resp = m.response_panel(w2, w)
        parts = {
            "mu": np.broadcast_to(w["mu"] * trait[:, None, None, :], resp.shape),
            "slow": np.broadcast_to(w["slow"] * world_obj["slow"][:, :, None, :], resp.shape),
            "common": np.broadcast_to(w["common"] * world_obj["common"][None, :, None, :],
                                      resp.shape),
            "noise": w["noise"] * world_obj["noise"],
        }
        recon = float(np.abs(resp - sum(parts.values())).max())
        g0["recon_residual_max"] = max(g0["recon_residual_max"], recon)
        # the eta mixture's designed energy identity, at every eta
        for eta in ETA_LEVELS:
            b = latent_identity_l2(typ, SB2_RHO55, eta)
            g0["eta_mixture_energy_residual_max"] = max(
                g0["eta_mixture_energy_residual_max"],
                abs(float(np.mean(np.einsum("ij,ij->i", b, b))) / SB2_RHO55 - 1.0))
        base = cards_for_cell(world_obj, typ, L1_DELTA, SB2_RHO55, 0.5)["full"]
        no_type = m.card(lg.centred_with_trait(
            world_obj, typed_trait_l2(world_obj, typ, L1_DELTA, SB2_RHO55, 0.5,
                                      drop_type=True)), w, np.arange(N_OCC), (0, 1), True)
        no_id = m.card(lg.centred_with_trait(
            world_obj, typed_trait_l2(world_obj, typ, L1_DELTA, SB2_RHO55, 0.5,
                                      drop_identity=True)), w, np.arange(N_OCC), (0, 1), True)
        eta0 = cards_for_cell(world_obj, typ, L1_DELTA, SB2_RHO55, 0.0)["full"]
        eta1 = cards_for_cell(world_obj, typ, L1_DELTA, SB2_RHO55, 1.0)["full"]
        d_small = cards_for_cell(world_obj, typ, ladder[0], SB2_RHO55, 0.0)["full"]
        g1["per_world"].append({
            "world": world,
            "rms_drop_type": float(np.sqrt(np.mean((base - no_type) ** 2))),
            "rms_drop_identity": float(np.sqrt(np.mean((base - no_id) ** 2))),
            "rms_eta0_vs_eta1": float(np.sqrt(np.mean((eta0 - eta1) ** 2))),
            "rms_eta0_vs_eta05": float(np.sqrt(np.mean((eta0 - base) ** 2))),
            "rms_delta_low_vs_L1": float(np.sqrt(np.mean((d_small - eta0) ** 2))),
        })
        rows = [measure_cell_world(world_obj, typ, spec, wseed) for spec in cells]
        for row in rows:
            row["world"] = world
            g0["sigma_b2_rel_dev_max"] = max(
                g0["sigma_b2_rel_dev_max"],
                abs(row["realized_sigma_b2"] / row["sigma_b2"] - 1.0))
            g0["eta_dev_abs_max"] = max(
                g0["eta_dev_abs_max"], abs(row["realized_eta"] - row["eta"]))
            g0["delta_latent_dev_abs_max"] = max(
                g0["delta_latent_dev_abs_max"],
                max(abs(row["realized_delta_latent_min"] - row["delta"]),
                    abs(row["realized_delta_latent_max"] - row["delta"])))
            g0["pca_grand_mean_norm_max"] = max(
                g0["pca_grand_mean_norm_max"], row["pca_grand_mean_norm"])
        pilot_rows.extend(rows)
        g0["per_world"].append({"world": world, "world_seed": wseed, "recon_residual": recon})
    pilot = pd.DataFrame(pilot_rows)
    pilot.to_csv(OUT / "part0_pilot_cells.csv", index=False)
    st["pilot"] = time.time() - t

    # ---- G0M: the L1 ANCHORS, re-derived bit-exactly from L1's own path
    t = time.time()
    anchors: dict[str, Any] = {}
    persisted = m.read_csv_rt(L1_OUT / "cells.csv")

    def _pers(cell: str, col: str) -> float:
        return float(persisted[persisted["cell"] == cell][col].iloc[0])

    rederived: dict[str, float] = {}
    acc: dict[str, list[float]] = {"ISO": [], "ALIGNED": []}
    for wi in range(lg.WORLDS_PER_CELL):
        wseed_l1 = lg.world_seed_for(wi)
        w_obj, w_typ = lg.build_typed_world(wseed_l1, lg.N_AUTHORS)
        for geom in ("ISO", "ALIGNED"):
            acc[geom].append(lg.measure_cell_world(
                w_obj, w_typ, geom, L1_DELTA, 0.55, "ambient", wseed_l1)["ari_primary"])
    for geom in ("ISO", "ALIGNED"):
        rederived[geom] = float(np.mean(acc[geom]))
    anchors["ISO_rho0.55_ari"] = {
        "registration": L1_ARI_ISO_055, "persisted": _pers("ISO_rho0.55", "ari_primary"),
        "rederived": rederived["ISO"],
        "residual_vs_registration": abs(rederived["ISO"] - L1_ARI_ISO_055),
        "bit_exact": bool(rederived["ISO"] == L1_ARI_ISO_055
                          == _pers("ISO_rho0.55", "ari_primary"))}
    anchors["ALIGNED_rho0.55_ari"] = {
        "registration": L1_ARI_ALIGNED_055,
        "persisted": _pers("ALIGNED_rho0.55", "ari_primary"),
        "rederived": rederived["ALIGNED"],
        "residual_vs_registration": abs(rederived["ALIGNED"] - L1_ARI_ALIGNED_055),
        "bit_exact": bool(rederived["ALIGNED"] == L1_ARI_ALIGNED_055
                          == _pers("ALIGNED_rho0.55", "ari_primary"))}
    iso_drop = _pers("ISO_rho0", "ari_primary") - _pers("ISO_rho0.75", "ari_primary")
    ali_drop = _pers("ALIGNED_rho0", "ari_primary") - _pers("ALIGNED_rho0.75", "ari_primary")
    tax = ali_drop / iso_drop
    anchors["tax_ratio"] = {"registration": L1_TAX_RATIO, "recomputed": tax,
                            "iso_drop": iso_drop, "aligned_drop": ali_drop,
                            "bit_exact": bool(tax == L1_TAX_RATIO)}
    c_cont_l1 = m.ar_cross_cov(*m.splits(N_OCC)["contiguous"], PHI_SLOW)
    offset = (0.25 - L1_B_HAT) * c_cont_l1
    anchors["audit_offset"] = {"registration": L1_AUDIT_OFFSET,
                               "recomputed": offset, "c_cont": c_cont_l1,
                               "B_hat_L1": L1_B_HAT,
                               "agrees_to_1e-6": bool(abs(offset - L1_AUDIT_OFFSET) < 1e-6)}
    anchors["floors"] = {
        "ALIGNED_rho0.35_measured": {"registration": L1_FLOOR_ALIGNED_035_MEASURED,
                                     "persisted": _pers("ALIGNED_rho0.35",
                                                        "boundary_err_true_card")},
        "ALIGNED_rho0.35_predicted": {"registration": L1_FLOOR_ALIGNED_035_PREDICTED,
                                      "persisted": _pers("ALIGNED_rho0.35",
                                                         "pred_boundary_floor_realized")},
        "ALIGNED_rho0.55_measured": {"registration": L1_FLOOR_ALIGNED_055_MEASURED,
                                     "persisted": _pers("ALIGNED_rho0.55",
                                                        "boundary_err_true_card")},
        "ALIGNED_rho0.55_predicted": {"registration": L1_FLOOR_ALIGNED_055_PREDICTED,
                                      "persisted": _pers("ALIGNED_rho0.55",
                                                         "pred_boundary_floor_realized")},
    }
    anchors["floors_bit_exact"] = bool(all(
        v["registration"] == v["persisted"] for v in anchors["floors"].values()))
    anchors["all_bit_exact"] = bool(
        anchors["ISO_rho0.55_ari"]["bit_exact"] and anchors["ALIGNED_rho0.55_ari"]["bit_exact"]
        and anchors["tax_ratio"]["bit_exact"] and anchors["floors_bit_exact"])
    g0["l1_anchors"] = anchors
    st["anchors"] = time.time() - t
    g0["criterion"] = (
        "reconstruction residual <= 1e-12 AND the eta-mixture designed energy exact to "
        "<= 0.03 relative AND |realized eta - designed| <= 0.03 AND all six realized "
        "latent separations equal Delta to <= 1e-9 AND every L1 anchor re-derived "
        "BIT-EXACTLY (ISO/ALIGNED rho.55 ARIs, both floors, the tax ratio) with the "
        "audit offset reproduced from k2a's own AR algebra to < 1e-6")
    g0["pass"] = bool(g0["recon_residual_max"] <= 1e-12
                      and g0["eta_mixture_energy_residual_max"] <= 0.03
                      and g0["sigma_b2_rel_dev_max"] <= 0.03
                      and g0["eta_dev_abs_max"] <= 0.03
                      and g0["delta_latent_dev_abs_max"] <= 1e-9
                      and anchors["all_bit_exact"]
                      and anchors["audit_offset"]["agrees_to_1e-6"])
    gates["G0M"] = g0

    # ---- G1M: rule-10 non-degeneracy + rule-3 liveness + THE BRACKET
    pmean = pilot.groupby("cell", sort=False).agg(
        {"ari_ambient": "mean", "ari_oracleS": "mean", "ari_estS": "mean",
         "ari_oracle_centroid": "mean", "overlap_estS": "mean", "eigengap_abs": "mean",
         "boundary_err_true_card": "mean", "floor_pred_identity": "mean",
         "floor_pred_full": "mean", "kind": "first", "delta": "first",
         "eta": "first", "energy": "first"}).reset_index()
    tmean = pmean[pmean["kind"] == "T"]
    amb_pilot = {r["cell"]: float(r["ari_ambient"]) for _, r in tmean.iterrows()}
    orc_pilot = {r["cell"]: float(r["ari_oracleS"]) for _, r in tmean.iterrows()}
    bracket_ok = bool(min(amb_pilot.values()) < BRACKET_LO
                      and max(amb_pilot.values()) > BRACKET_HI)
    g1.update({
        "min_rms_drop_type": float(min(r["rms_drop_type"] for r in g1["per_world"])),
        "min_rms_drop_identity": float(min(r["rms_drop_identity"] for r in g1["per_world"])),
        "min_rms_eta0_vs_eta1": float(min(r["rms_eta0_vs_eta1"] for r in g1["per_world"])),
        "min_rms_eta0_vs_eta05": float(min(r["rms_eta0_vs_eta05"] for r in g1["per_world"])),
        "min_rms_delta_low_vs_L1": float(min(r["rms_delta_low_vs_L1"] for r in g1["per_world"])),
        "min_eigengap_abs": float(pmean["eigengap_abs"].min()),
        "pilot_T_ambient": amb_pilot, "pilot_T_oracleS": orc_pilot,
        "pilot_T_estS": {r["cell"]: float(r["ari_estS"]) for _, r in tmean.iterrows()},
        "pilot_T_oracle_centroid": {r["cell"]: float(r["ari_oracle_centroid"])
                                    for _, r in tmean.iterrows()},
        "pilot_C_ambient": {r["cell"]: float(r["ari_ambient"])
                            for _, r in pmean[pmean["kind"] == "C"].iterrows()},
        "bracket_lo": BRACKET_LO, "bracket_hi": BRACKET_HI,
        "bracket_min_ambient": float(min(amb_pilot.values())),
        "bracket_max_ambient": float(max(amb_pilot.values())),
        "bracket_ok": bracket_ok, "ladder_shift_fired": False,
        "floor_clause_bar": FLOOR_BAR,
        "floor_identity_on_ladder": {r["cell"]: float(r["floor_pred_identity"])
                                     for _, r in tmean.iterrows()},
        "floor_full_on_ladder": {r["cell"]: float(r["floor_pred_full"])
                                 for _, r in tmean.iterrows()},
        "floor_clause_identity_pass": bool(all(
            float(r["floor_pred_identity"]) < FLOOR_BAR for _, r in tmean.iterrows())),
        "floor_clause_full_pass": bool(all(
            float(r["floor_pred_full"]) < FLOOR_BAR for _, r in tmean.iterrows())),
        "criterion": (
            "rule 10: the type channel, the identity channel, the eta mixture and the "
            "Delta ladder all change the card panel (RMS > 1e-6).  rule 3: the "
            "top-k_tau eigengap is positive in every cell.  THE BRACKET (registration "
            "G1M): the pilot ambient ARI spans (<0.30, >0.80) across the five T rungs; "
            "otherwise the one pre-declared ladder shift fires."),
    })
    g1["pass"] = bool(g1["min_rms_drop_type"] > 1e-6 and g1["min_rms_drop_identity"] > 1e-6
                      and g1["min_rms_eta0_vs_eta1"] > 1e-6
                      and g1["min_eigengap_abs"] > 0.0 and bracket_ok)
    gates["G1M"] = g1

    # ---- G2M: rule-18 JOINT satisfiability + pilot MDEs + rule-13 spec
    t = time.time()
    js = joint_satisfiability(grid, ladder)
    g2: dict[str, Any] = {"rule18_joint": js, "b_draws": B_BOOT, "seed": MASTER_SEED,
                          "b_draws_stability": B_BOOT_HIGH,
                          "pilot_worlds": len(PILOT_WORLDS), "clauses": []}

    def mde(sd: float, n: int) -> float:
        df = len(PILOT_WORLDS) - 1
        return (float(student_t.ppf(0.975, df)) + float(student_t.ppf(0.80, df))) * sd / math.sqrt(n)

    for key, label, direction in (
            ("ari_ambient", "ambient ARI", "one-sided upper (< 0.30) on T-cells"),
            ("ari_oracleS", "oracle-S ARI", "one-sided lower (> 0.80) on T-cells"),
            ("ari_estS", "estimated-S ARI", "two-sided (CI must CONTAIN oracle-S)"),
            ("boundary_err_true_card", "true-card boundary rate",
             "two-sided (CI must CONTAIN the eta floor curve)"),
            ("xf_S_id", "cross-fitted calibrated audit share",
             "two-sided (CI must CONTAIN the designed share)")):
        pv = pilot.pivot_table(index="world", columns="cell", values=key)
        for cid in pv.columns:
            sd = float(pv[cid].std(ddof=1))
            g2["clauses"].append({"clause": f"{label} {cid}",
                                  "pilot_mean": float(pv[cid].mean()),
                                  "pilot_sd_world": sd,
                                  "mde_main": mde(sd, WORLDS_PER_CELL),
                                  "direction": direction})
    pv_sd = pilot.pivot_table(index="world", columns="cell", values="sd_S_id")
    pv_xf = pilot.pivot_table(index="world", columns="cell", values="xf_S_id")
    bias = (pv_sd - pv_xf)
    ccells = [c["cell"] for c in cells if c["kind"] == "C"]
    g2["clauses"].append({
        "clause": "pooled same-data minus cross-fitted audit bias",
        "pilot_mean": float(bias[ccells].mean(axis=1).mean()),
        "pilot_sd_world": float(bias[ccells].mean(axis=1).std(ddof=1)),
        "mde_main": mde(float(bias[ccells].mean(axis=1).std(ddof=1)), WORLDS_PER_CELL),
        "direction": "one-sided upper (< 0, the optimistic side), CI excluding 0"})
    g2["rule13_spec"] = ("B=2000 at seed=master_seed, with a >=10xB (20000) recheck at "
                         "any clause whose boundary lies within 2 Monte-Carlo endpoint "
                         "sds of the estimate")
    g2["rule11_directions"] = {
        "W-1": "one-sided upper on ambient (<0.30) AND one-sided lower on oracle-S "
               "(>0.80), per T-cell, both CIs on the stated sides",
        "W-2": "two-sided containment of oracle-S by the estimated-S CI",
        "W-3": "two-sided containment of the floor curve by the measured-rate CI; "
               "plus an exact ordering predicate",
        "W-4": "two-sided containment of the designed share; one-sided pooled sign "
               "for the bias",
    }
    g2["criterion"] = (
        "rule 18: every clause sharing the T-arm knobs is reduced to a SET OF DELTA and "
        "all pairs are intersected, so joint (not per-clause) satisfiability is on the "
        "record BEFORE the arms; every registered interval clause has a 4-world pilot "
        "MDE at the main-design grain and a stated direction; the rule-13 spec is fixed")
    n_clauses = len(js["clause_delta_intervals"])
    g2["pass"] = bool(
        len(g2["clauses"]) > 0
        and all(np.isfinite(c["mde_main"]) and c["direction"] for c in g2["clauses"])
        and len(js["pairwise"]) == n_clauses * (n_clauses - 1) // 2)
    gates["G2M"] = g2
    st["power"] = time.time() - t

    # ---- G4M: hygiene + rule 16 + rule 14
    layer_a, layer_b, enum_audit = build_enumeration()
    layer_a.to_csv(OUT / "part0_enumeration_leans.csv", index=False)
    layer_b.to_csv(OUT / "part0_enumeration_routing.csv", index=False)
    gates["G4M"] = {
        "pass": bool(enum_audit["layer_a_no_gap_no_overlap"]
                     and enum_audit["layer_b_no_gap_no_overlap"]),
        "round_trip_parsing_everywhere": True, "float_precision": "round_trip",
        "enumeration": enum_audit,
        "rule14_self_check": (
            "CARD SPACE ONLY.  W-1/W-2 compare ARI to ARI; W-3 compares a card-space "
            "per-boundary misassignment RATE to the closed-form rate "
            "Phi(-Delta/(2 sigma_u(eta))); W-4 compares a normalized variance SHARE to "
            "a normalized variance SHARE.  No gate and no lean crosses scales or "
            "instruments, so rule 14 has nothing to bind."),
        "rule12_source_objects": {
            "typed world + type layer": "scripts/run_suica_m4_l1_typed_world.py, imported "
                                        "as a module and called UNMODIFIED "
                                        "(TETRAHEDRON, latent_type_vectors, "
                                        "card_space_type_basis, centred_with_trait, "
                                        "kmeans_lloyd, adjusted_rand_index, "
                                        "hungarian_accuracy, boundary_error_rate, "
                                        "group_centre, _norm_dot, build_typed_world, "
                                        "measure_cell_world/world_seed_for for the anchor)",
            "expressive world": "scripts/run_suica_m4_k2a_expressive_world.py:184-236 "
                                "build_world, called (transitively via l1)",
            "channel weights": "k2a:129-138 arm_weights('zero'), called",
            "author centring": "k2a:250-259 centered_channels, called",
            "the card": "k2a:262-276 card, called",
            "canonical splits": "k2a:335-340 splits, called",
            "AR algebra": "k2a:282-300 ar_mean_var/ar_set_var/ar_cross_cov, called",
            "round-trip parser / CI / MC-sd": "k2a:118-120, k2a:519-521, k2a:524-532",
            "NEW in this leg": "this script -- type_geometry_l2 (TWO identity streams), "
                               "latent_identity_l2, typed_trait_l2, cards_for_cell, "
                               "occasion_scheme, estimated_s, subspace_overlap, "
                               "bbp_quantities, predicted_boundary_error_l2, "
                               "projection_gain, audit_meter_l2, pred_population_l2, "
                               "ladder_grid/solve_ladder, joint_satisfiability, "
                               "fidelity_table",
        },
    }
    gates["part0_all_pass"] = bool(gates["G0M"]["pass"] and gates["G1M"]["pass"]
                                   and gates["G2M"]["pass"] and gates["G3M"]["pass"]
                                   and gates["G4M"]["pass"])
    gates["ladder_final"] = ladder
    gates["stage_seconds"] = st
    gates["stage_seconds"]["part0_total"] = time.time() - t0
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n",
                                    encoding="utf-8")
    write_part0_tables(gates, pd.concat([t_pred, c_pred], ignore_index=True), pilot, grid)
    write_manifest({"part0": time.time() - t0}, {"ladder": ladder})
    print(json.dumps({
        "stage": "part0", "seconds": round(time.time() - t0, 3), "ladder": ladder,
        "part0_all_pass": gates["part0_all_pass"],
        "G0M": gates["G0M"]["pass"], "G1M": gates["G1M"]["pass"],
        "G2M": gates["G2M"]["pass"], "G3M": gates["G3M"]["pass"],
        "G4M": gates["G4M"]["pass"],
        "anchors_bit_exact": anchors["all_bit_exact"],
        "bracket_ok": bracket_ok,
        "pilot_T_ambient": amb_pilot, "pilot_T_oracleS": orc_pilot,
        "W1_window": js["W1_window"],
        "floor_identity_on_ladder": gates["G1M"]["floor_identity_on_ladder"],
        "stage_seconds": st,
    }, indent=2, default=str))


def write_part0_tables(gates: dict[str, Any], preds: pd.DataFrame,
                       pilot: pd.DataFrame, grid: pd.DataFrame) -> None:
    lines: list[str] = []
    lines.append("### G3M rule-19 fidelity table\n")
    lines.append("| lean | theorem quantity | predicted value / curve (derivation) | "
                 "the bar | why the bar is on that quantity |")
    lines.append("|---|---|---|---|---|")
    for r in gates["G3M"]["fidelity_table"]:
        lines.append("| **{lean}** | {theorem_quantity} | {predicted} | {bar} | "
                     "{why_this_quantity} |".format(
                         **{k: v.replace("\n", " ") for k, v in r.items()}))
    lines.append("\n### MN-3 ladder grid (prediction stream, before any world)\n")
    lines.append("| Delta | ambient | oracle-S | est-S | oracle-centroid (Bayes) | "
                 "overlap | floor (identity) | floor (full) |")
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|")
    for _, r in grid.iterrows():
        lines.append(f"| {r['delta']:.6f} | {r['ambient']:.6f} | {r['oracleS']:.6f} | "
                     f"{r['estS']:.6f} | {r['oracle_centroid']:.6f} | {r['overlap']:.6f} | "
                     f"{r['floor_identity']:.8f} | {r['floor_full']:.8f} |")
    lines.append("\n### Part-0 per-cell predictions (all 15 cells, before any arm)\n")
    lines.append("| cell | Delta | sigma_b^2 | eta | pred ambient | pred oracle-S | "
                 "pred est-S | pred Bayes | pred overlap | floor (identity) | floor (full) |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for _, r in preds.iterrows():
        lines.append(
            f"| `{r['cell']}` | {r['delta']:.6f} | {r['sigma_b2']:.6f} | {r['eta']:g} | "
            f"{r['ambient']:.6f} | {r['oracleS']:.6f} | {r['estS']:.6f} | "
            f"{r['oracle_centroid']:.6f} | {r['overlap']:.6f} | "
            f"{r['floor_identity']:.8f} | {r['floor_full']:.8f} |")
    lines.append("\n### G2M rule-18 JOINT satisfiability (T-arm clauses, "
                 "reduced to sets of Delta)\n")
    lines.append("| clause | Delta interval where it holds |")
    lines.append("|---|---|")
    for k, v in gates["G2M"]["rule18_joint"]["clause_delta_intervals"].items():
        lines.append(f"| {k} | {'EMPTY' if v is None else f'[{v[0]:.4f}, {v[1]:.4f}]'} |")
    lines.append("\n| clause pair | jointly satisfiable | Delta interval |")
    lines.append("|---|---|---|")
    for k, v in gates["G2M"]["rule18_joint"]["pairwise"].items():
        iv = v["delta_interval"]
        lines.append(f"| {k} | {v['satisfiable']} | "
                     f"{'EMPTY' if iv is None else f'[{iv[0]:.4f}, {iv[1]:.4f}]'} |")
    lines.append("\n### G2M pilot MDEs (4 pilot worlds -> main design n=8)\n")
    lines.append("| clause | pilot mean | pilot sd (world) | MDE at n=8 | direction |")
    lines.append("|---|---:|---:|---:|---|")
    for c in gates["G2M"]["clauses"]:
        lines.append(f"| {c['clause']} | {c['pilot_mean']:.10f} | {c['pilot_sd_world']:.10f} "
                     f"| {c['mde_main']:.10f} | {c['direction']} |")
    lines.append("\n### G1M rule-10 non-degeneracy (card-panel RMS)\n")
    lines.append("| world | drop type | drop identity | eta0 vs eta1 | eta0 vs eta.5 | "
                 "Delta(T0) vs Delta(L1) |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for r in gates["G1M"]["per_world"]:
        lines.append(f"| {r['world']} | {r['rms_drop_type']:.8e} | "
                     f"{r['rms_drop_identity']:.8e} | {r['rms_eta0_vs_eta1']:.8e} | "
                     f"{r['rms_eta0_vs_eta05']:.8e} | {r['rms_delta_low_vs_L1']:.8e} |")
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
    ladder = [float(x) for x in gates["ladder_final"]]
    t0 = time.time()
    wanted = set(args.cells.split(",")) if args.cells else None
    cells = [c for c in all_cells(ladder) if wanted is None or c["cell"] in wanted]
    rows: list[dict[str, Any]] = []
    for world in range(WORLDS_PER_CELL):
        rows.extend([{**r, "world": world} for r in run_world_cells(world, cells)])
        print(f"  world {world}: {len(cells)} cells  ({time.time() - t0:.1f}s)")
    frame = pd.DataFrame(rows)
    for cid, sub in frame.groupby("cell", sort=False):
        sub.to_csv(OUT / f"cell_{cid}.csv", index=False)
    write_manifest({f"arms[{len(cells)} cells]": time.time() - t0}, {})
    print(json.dumps({"stage": "arms", "cells": [c["cell"] for c in cells],
                      "rows": int(len(frame)),
                      "seconds": round(time.time() - t0, 3)}, indent=2))


# ---------------------------------------------------------------------------
# Stage: finalize

def _boot_index(b_draws: int, seed: int, n_blocks: int) -> np.ndarray:
    """MN-10: ONE paired world-block resample, applied identically to EVERY cell
    (the cells share their worlds bit-for-bit, so every cross-cell contrast is
    paired inside the bootstrap)."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, n_blocks, size=(b_draws, n_blocks))


def run_finalize(args: argparse.Namespace) -> None:
    gates = require_part0()
    m, lg = k2a(), l1()
    t0 = time.time()
    ladder = [float(x) for x in gates["ladder_final"]]
    cells = all_cells(ladder)
    preds = m.read_csv_rt(OUT / "part0_predictions.csv")
    frames = {}
    for spec in cells:
        path = OUT / f"cell_{spec['cell']}.csv"
        if not path.exists():
            raise SystemExit(f"REFUSED: missing arm artifact {path}")
        frames[spec["cell"]] = m.read_csv_rt(path).sort_values("world").reset_index(drop=True)
    idx = _boot_index(B_BOOT, MASTER_SEED, WORLDS_PER_CELL)
    idx_hi = _boot_index(B_BOOT_HIGH, MASTER_SEED, WORLDS_PER_CELL)

    def vals(cid: str, key: str) -> np.ndarray:
        return frames[cid][key].to_numpy(float)

    def boot(cid: str, key: str, index: np.ndarray) -> np.ndarray:
        return vals(cid, key)[index].mean(axis=1)

    KEYS = ("ari_ambient", "ari_oracleS", "ari_estS", "ari_oracle_centroid",
            "acc_ambient", "acc_oracleS", "acc_estS", "overlap_estS",
            "boundary_err_true_card", "boundary_err_full_card",
            "floor_pred_identity", "floor_pred_full", "ari_fit_half", "ari_same_half",
            "xf_S_id", "sd_S_id", "or_S_id", "xf_S_id_theory", "xf_S_id_designB",
            "xf_target", "sd_target", "or_target", "xf_target_bonly", "or_target_bonly",
            "xf_B_hat_cal", "xf_B_hat_theory", "or_B_hat_cal", "or_B_hat_theory",
            "bbp_theta_min", "bbp_ratio_min", "bbp_pred_overlap",
            "realized_eta", "realized_sigma_b2", "eigengap_ratio")
    rows = []
    for spec in cells:
        cid = spec["cell"]
        row: dict[str, Any] = {**spec, "n_worlds": int(len(frames[cid]))}
        for key in KEYS:
            b = boot(cid, key, idx)
            lo, hi = m.ci_of(b)
            row[key] = float(vals(cid, key).mean())
            row[f"{key}_lo"], row[f"{key}_hi"] = lo, hi
            row[f"{key}_se"] = float(np.std(b, ddof=1))
        # floor containment (W-3)
        row["floor_contains_pred"] = bool(
            row["boundary_err_true_card_lo"] <= row["floor_pred_identity"]
            <= row["boundary_err_true_card_hi"])
        # estimated-S vs oracle-S (W-2), paired
        d = boot(cid, "ari_estS", idx) - boot(cid, "ari_oracleS", idx)
        lo, hi = m.ci_of(d)
        row["estS_minus_oracleS"] = float(
            (vals(cid, "ari_estS") - vals(cid, "ari_oracleS")).mean())
        row["estS_minus_oracleS_lo"], row["estS_minus_oracleS_hi"] = lo, hi
        row["estS_within_ci_of_oracleS"] = bool(lo <= 0.0 <= hi)
        # localization gap (W-1's declared theorem-quantity second reading)
        d = boot(cid, "ari_oracleS", idx) - boot(cid, "ari_ambient", idx)
        lo, hi = m.ci_of(d)
        row["localization_gap"] = float(
            (vals(cid, "ari_oracleS") - vals(cid, "ari_ambient")).mean())
        row["localization_gap_lo"], row["localization_gap_hi"] = lo, hi
        d = boot(cid, "ari_oracleS", idx) - boot(cid, "ari_oracle_centroid", idx)
        lo, hi = m.ci_of(d)
        row["oracleS_minus_bayes"] = float(
            (vals(cid, "ari_oracleS") - vals(cid, "ari_oracle_centroid")).mean())
        row["oracleS_minus_bayes_lo"], row["oracleS_minus_bayes_hi"] = lo, hi
        d = boot(cid, "ari_ambient", idx) - boot(cid, "ari_oracle_centroid", idx)
        lo, hi = m.ci_of(d)
        row["ambient_minus_bayes"] = float(
            (vals(cid, "ari_ambient") - vals(cid, "ari_oracle_centroid")).mean())
        row["ambient_minus_bayes_lo"], row["ambient_minus_bayes_hi"] = lo, hi
        # audit tracking (W-4a) and the same-data bias (W-4b)
        d = boot(cid, "xf_S_id", idx) - boot(cid, "xf_target", idx)
        lo, hi = m.ci_of(d)
        row["xf_minus_target"] = float(
            (vals(cid, "xf_S_id") - vals(cid, "xf_target")).mean())
        row["xf_minus_target_lo"], row["xf_minus_target_hi"] = lo, hi
        row["xf_tracks_design"] = bool(lo <= 0.0 <= hi)
        d = boot(cid, "sd_S_id", idx) - boot(cid, "xf_S_id", idx)
        lo, hi = m.ci_of(d)
        row["samedata_bias"] = float((vals(cid, "sd_S_id") - vals(cid, "xf_S_id")).mean())
        row["samedata_bias_lo"], row["samedata_bias_hi"] = lo, hi
        d = boot(cid, "or_S_id", idx) - boot(cid, "or_target", idx)
        lo, hi = m.ci_of(d)
        row["oracle_minus_target"] = float(
            (vals(cid, "or_S_id") - vals(cid, "or_target")).mean())
        row["oracle_minus_target_lo"], row["oracle_minus_target_hi"] = lo, hi
        row["oracle_tracks_design"] = bool(lo <= 0.0 <= hi)
        # second reading: the L1 (theoretical-constant) meter, cross-fitted
        d = boot(cid, "xf_S_id_theory", idx) - boot(cid, "xf_target", idx)
        lo, hi = m.ci_of(d)
        row["xf_theory_minus_target"] = float(
            (vals(cid, "xf_S_id_theory") - vals(cid, "xf_target")).mean())
        row["xf_theory_tracks_design"] = bool(lo <= 0.0 <= hi)
        pr = preds[preds["cell"] == cid]
        for k in ("ambient", "oracleS", "estS", "oracle_centroid", "overlap",
                  "floor_identity", "floor_full"):
            row[f"pred_{k}"] = float(pr[k].iloc[0])
        rows.append(row)
    cdf = pd.DataFrame(rows)
    cdf.to_csv(OUT / "cells.csv", index=False)
    by = {r["cell"]: r for r in rows}
    tcells = [c["cell"] for c in cells if c["kind"] == "T"]
    ccells = [c["cell"] for c in cells if c["kind"] == "C"]

    stability: list[dict[str, Any]] = []

    def rule13(cid: str, clause: str, arr: np.ndarray, arr_hi: np.ndarray,
               boundary: float, kind: str, verdict: bool) -> None:
        alpha = 0.025 if kind == "contains" else 0.05
        mc = m.mc_sd_of_endpoint(arr, B_BOOT, alpha)
        if kind == "contains":
            dist = min(abs(boundary - float(np.percentile(arr, 2.5))),
                       abs(boundary - float(np.percentile(arr, 97.5))))
            v2 = bool(float(np.percentile(arr_hi, 2.5)) <= boundary
                      <= float(np.percentile(arr_hi, 97.5)))
            end = [float(np.percentile(arr_hi, 2.5)), float(np.percentile(arr_hi, 97.5))]
        elif kind == "upper_lt":
            dist = abs(boundary - float(np.percentile(arr, 97.5)))
            v2 = bool(float(np.percentile(arr_hi, 97.5)) < boundary)
            end = [float(np.percentile(arr_hi, 97.5))]
        else:
            dist = abs(boundary - float(np.percentile(arr, 2.5)))
            v2 = bool(float(np.percentile(arr_hi, 2.5)) > boundary)
            end = [float(np.percentile(arr_hi, 2.5))]
        if dist <= 2.0 * mc:
            stability.append({"cell": cid, "clause": clause, "kind": kind,
                              "boundary": boundary, "mc_sd_endpoint_B2000": mc,
                              "distance_to_boundary": dist, "verdict_B2000": verdict,
                              "verdict_B20000": v2, "endpoints_B20000": end,
                              "status": "STABLE" if verdict == v2 else "BOUNDARY"})

    # ---- W-1
    w1_cells = {}
    for cid in tcells:
        amb_ok = bool(by[cid]["ari_ambient_hi"] < W1_AMBIENT_BAR)
        orc_ok = bool(by[cid]["ari_oracleS_lo"] > W1_ORACLE_BAR)
        rule13(cid, "ambient ARI < 0.30", boot(cid, "ari_ambient", idx),
               boot(cid, "ari_ambient", idx_hi), W1_AMBIENT_BAR, "upper_lt", amb_ok)
        rule13(cid, "oracle-S ARI > 0.80", boot(cid, "ari_oracleS", idx),
               boot(cid, "ari_oracleS", idx_hi), W1_ORACLE_BAR, "lower_gt", orc_ok)
        rev = bool(by[cid]["localization_gap_hi"] < 0.0)
        w1_cells[cid] = {"delta": by[cid]["delta"],
                         "ambient": by[cid]["ari_ambient"],
                         "ambient_lo": by[cid]["ari_ambient_lo"],
                         "ambient_hi": by[cid]["ari_ambient_hi"],
                         "oracleS": by[cid]["ari_oracleS"],
                         "oracleS_lo": by[cid]["ari_oracleS_lo"],
                         "oracleS_hi": by[cid]["ari_oracleS_hi"],
                         "ambient_below_bar": amb_ok, "oracleS_above_bar": orc_ok,
                         "in_window": bool(amb_ok and orc_ok), "reversed": rev,
                         "localization_gap": by[cid]["localization_gap"],
                         "localization_gap_lo": by[cid]["localization_gap_lo"],
                         "localization_gap_hi": by[cid]["localization_gap_hi"]}
    n_window = sum(1 for v in w1_cells.values() if v["in_window"])
    n_rev = sum(1 for v in w1_cells.values() if v["reversed"])
    w1_sub = ("HOLD" if n_window >= W1_MIN_CELLS else "MISS",
              "HOLD" if n_rev == 0 else "MISS")
    # declared theorem-quantity SECOND READING (pinned in Part 0, routing-inert)
    gap_pos = {cid: bool(by[cid]["localization_gap_lo"] > 0.0) for cid in tcells}
    bayes_reading = {cid: {"oracleS_minus_bayes": by[cid]["oracleS_minus_bayes"],
                           "oracleS_minus_bayes_lo": by[cid]["oracleS_minus_bayes_lo"],
                           "oracleS_minus_bayes_hi": by[cid]["oracleS_minus_bayes_hi"],
                           "oracleS_at_bayes_ceiling": bool(
                               by[cid]["oracleS_minus_bayes_lo"] <= 0.0
                               <= by[cid]["oracleS_minus_bayes_hi"]),
                           "ambient_minus_bayes": by[cid]["ambient_minus_bayes"],
                           "ambient_minus_bayes_hi": by[cid]["ambient_minus_bayes_hi"],
                           "ambient_below_bayes": bool(
                               by[cid]["ambient_minus_bayes_hi"] < 0.0)}
                     for cid in tcells}
    w1 = {"prior": 0.65, "shadows": "R2-restated's threshold claim (appendix Q.3)",
          "bars": {"ambient": W1_AMBIENT_BAR, "oracleS": W1_ORACLE_BAR,
                   "min_cells": W1_MIN_CELLS},
          "cells": w1_cells, "n_cells_in_window": n_window, "n_reversed": n_rev,
          "second_reading_localization_gap_positive": gap_pos,
          "n_cells_with_positive_gap": int(sum(gap_pos.values())),
          "second_reading_bayes": bayes_reading,
          "subclause_states": list(w1_sub), "state": lean_from_subclauses(w1_sub)}

    # ---- W-2
    detectable = {cid: bool(by[cid]["bbp_ratio_min"] > 1.0) for cid in tcells}
    w2_contain = {cid: by[cid]["estS_within_ci_of_oracleS"]
                  for cid in tcells if detectable[cid]}
    for cid in tcells:
        rule13(cid, "estimated-S within CI of oracle-S",
               boot(cid, "ari_estS", idx) - boot(cid, "ari_oracleS", idx),
               boot(cid, "ari_estS", idx_hi) - boot(cid, "ari_oracleS", idx_hi),
               0.0, "contains", by[cid]["estS_within_ci_of_oracleS"])
    w2_sub = ("HOLD" if (w2_contain and all(w2_contain.values())) else
              ("UNREALIZABLE" if not w2_contain else "MISS"),)
    w2 = {"prior": 0.60, "shadows": "spiked-PCA consistency above the BBP-form threshold",
          "detectable": detectable, "containment": w2_contain,
          "n_detectable": int(sum(detectable.values())),
          "n_contain": int(sum(w2_contain.values())),
          "per_cell": {cid: {"estS": by[cid]["ari_estS"], "oracleS": by[cid]["ari_oracleS"],
                             "diff": by[cid]["estS_minus_oracleS"],
                             "diff_lo": by[cid]["estS_minus_oracleS_lo"],
                             "diff_hi": by[cid]["estS_minus_oracleS_hi"],
                             "theta_min": by[cid]["bbp_theta_min"],
                             "bbp_ratio_min": by[cid]["bbp_ratio_min"],
                             "overlap_measured": by[cid]["overlap_estS"],
                             "overlap_measured_lo": by[cid]["overlap_estS_lo"],
                             "overlap_measured_hi": by[cid]["overlap_estS_hi"],
                             "overlap_predicted": by[cid]["bbp_pred_overlap"],
                             "overlap_contains_pred": bool(
                                 by[cid]["overlap_estS_lo"] <= by[cid]["bbp_pred_overlap"]
                                 <= by[cid]["overlap_estS_hi"])}
                       for cid in tcells},
          "subclause_states": list(w2_sub), "state": lean_from_subclauses(w2_sub)}

    # ---- W-3
    contain = {cid: by[cid]["floor_contains_pred"] for cid in ccells}
    for cid in ccells:
        rule13(cid, "true-card boundary rate contains the eta floor curve",
               boot(cid, "boundary_err_true_card", idx),
               boot(cid, "boundary_err_true_card", idx_hi),
               by[cid]["floor_pred_identity"], "contains", by[cid]["floor_contains_pred"])
    order_ok = {}
    for name, _ in C_ENERGIES:
        seq = [by[c_cell_id(name, e)]["boundary_err_true_card"] for e in ETA_LEVELS]
        order_ok[name] = bool(all(a < b for a, b in zip(seq, seq[1:], strict=False)))
    w3_sub = ("HOLD" if sum(contain.values()) >= W3_MIN_CONTAIN else "MISS",
              "HOLD" if all(order_ok.values()) else "MISS")
    w3 = {"prior": 0.75, "shadows": "the projection-invariant floor sigma_u^2(eta)",
          "containment": contain, "n_contain": int(sum(contain.values())),
          "threshold": W3_MIN_CONTAIN, "eta_ordering_exact": order_ok,
          "measured": {cid: by[cid]["boundary_err_true_card"] for cid in ccells},
          "measured_lo": {cid: by[cid]["boundary_err_true_card_lo"] for cid in ccells},
          "measured_hi": {cid: by[cid]["boundary_err_true_card_hi"] for cid in ccells},
          "predicted": {cid: by[cid]["floor_pred_identity"] for cid in ccells},
          "subclause_states": list(w3_sub), "state": lean_from_subclauses(w3_sub)}

    # ---- W-4
    track = {cid: by[cid]["xf_tracks_design"] for cid in ccells}
    for cid in ccells:
        rule13(cid, "cross-fitted calibrated audit tracks the designed share",
               boot(cid, "xf_S_id", idx) - boot(cid, "xf_target", idx),
               boot(cid, "xf_S_id", idx_hi) - boot(cid, "xf_target", idx_hi),
               0.0, "contains", by[cid]["xf_tracks_design"])
    pooled = np.mean([boot(cid, "sd_S_id", idx) - boot(cid, "xf_S_id", idx)
                      for cid in ccells], axis=0)
    pooled_hi = np.mean([boot(cid, "sd_S_id", idx_hi) - boot(cid, "xf_S_id", idx_hi)
                         for cid in ccells], axis=0)
    p_lo, p_hi = m.ci_of(pooled)
    pooled_point = float(np.mean([by[cid]["samedata_bias"] for cid in ccells]))
    bias_ok = bool(p_hi < 0.0)
    rule13("pooled", "same-data audit optimistic bias < 0", pooled, pooled_hi,
           0.0, "upper_lt", bias_ok)
    w4_sub = ("HOLD" if sum(track.values()) >= W4_MIN_TRACK else "MISS",
              "HOLD" if bias_ok else "MISS")
    w4 = {"prior": 0.75, "shadows": "R3's completeness meter after the B_hat fix",
          "tracking": track, "n_tracking": int(sum(track.values())),
          "threshold": W4_MIN_TRACK,
          "pooled_samedata_bias": pooled_point, "pooled_lo": p_lo, "pooled_hi": p_hi,
          "bias_predicted_sign": "negative (same-data UNDERSTATES surviving identity)",
          "bias_clause": bias_ok,
          "per_cell": {cid: {"xf": by[cid]["xf_S_id"], "xf_lo": by[cid]["xf_S_id_lo"],
                             "xf_hi": by[cid]["xf_S_id_hi"],
                             "target": by[cid]["xf_target"],
                             "diff": by[cid]["xf_minus_target"],
                             "diff_lo": by[cid]["xf_minus_target_lo"],
                             "diff_hi": by[cid]["xf_minus_target_hi"],
                             "same_data": by[cid]["sd_S_id"],
                             "bias": by[cid]["samedata_bias"],
                             "bias_lo": by[cid]["samedata_bias_lo"],
                             "bias_hi": by[cid]["samedata_bias_hi"],
                             "oracle": by[cid]["or_S_id"],
                             "oracle_target": by[cid]["or_target"],
                             "oracle_tracks": by[cid]["oracle_tracks_design"],
                             "B_hat_cal": by[cid]["xf_B_hat_cal"],
                             "B_hat_theory": by[cid]["xf_B_hat_theory"],
                             "theory_tracks": by[cid]["xf_theory_tracks_design"],
                             "ari_fit_half": by[cid]["ari_fit_half"],
                             "ari_same_half": by[cid]["ari_same_half"]}
                       for cid in ccells},
          "second_reading_oracle_groups_track": {
              cid: by[cid]["oracle_tracks_design"] for cid in ccells},
          "second_reading_theory_constants_track": {
              cid: by[cid]["xf_theory_tracks_design"] for cid in ccells},
          "subclause_states": list(w4_sub), "state": lean_from_subclauses(w4_sub)}

    states = {"W-1": w1["state"], "W-2": w2["state"], "W-3": w3["state"], "W-4": w4["state"]}
    bracket_ok = bool(gates["G1M"]["bracket_ok"])
    routing = route(states, bracket_ok)
    boundary = [s for s in stability if s["status"] == "BOUNDARY"]
    slug = {"P1M": "BRACKET_UNREALIZABLE", "P2M": "LOCALIZATION_FAILS",
            "P3M": "INSTRUMENTS_UNRELIABLE", "P4M": "THRESHOLD_MEASURED"}[routing]
    decision = {
        "leg": "M4-L2", "timestamp_utc": datetime.now(UTC).isoformat(), "banner": BANNER,
        "master_seed": MASTER_SEED, "ladder": ladder, "sigma_b2_T": SB2_RHO55,
        "sigma_b2_C": {k: v for k, v in C_ENERGIES}, "eta_levels": list(ETA_LEVELS),
        "delta_C": L1_DELTA, "n_cells": len(cells), "worlds_per_cell": WORLDS_PER_CELL,
        "n_authors_per_world": N_AUTHORS, "bracket_ok": bracket_ok,
        "leans": {"W-1": w1, "W-2": w2, "W-3": w3, "W-4": w4},
        "lean_states": states, "routing": routing,
        "rule13": {"triggered": len(stability), "boundary": len(boundary),
                   "records": stability},
        "verdict_slug": (slug + "__"
                         + "".join(f"{k.replace('-', '')}{v[0]}" for k, v in states.items())
                         + f"__{routing}"),
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2, default=str) + "\n",
                                       encoding="utf-8")
    write_manifest({"finalize": time.time() - t0}, {})
    print(json.dumps({k: v for k, v in decision.items() if k != "rule13"}, indent=2,
                     default=str))
    print(f"rule13 triggered={len(stability)} boundary={len(boundary)}")


def write_manifest(stage_times: dict[str, float], extra: dict[str, Any]) -> None:
    path = OUT / "manifest.json"
    prior = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    prior.setdefault("leg", "M4-L2")
    prior.setdefault("banner", BANNER)
    prior.setdefault("script", "scripts/run_suica_m4_l2_threshold_continuum.py")
    prior.setdefault("registration",
                     "docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md M4-L2 (767f464)")
    prior.setdefault("theory", "docs/SUICA_IDENTITY_THEORY_V1.md appendices P and Q")
    prior.setdefault("master_seed", MASTER_SEED)
    prior.setdefault("worlds_per_cell", WORLDS_PER_CELL)
    prior.setdefault("pilot_worlds", list(PILOT_WORLDS))
    prior.setdefault("n_authors", N_AUTHORS)
    prior.setdefault("G", G_GROUPS)
    prior.setdefault("k_tau", K_TAU)
    prior.setdefault("eta_levels", list(ETA_LEVELS))
    prior.setdefault("sigma_b2_rho55eq", SB2_RHO55)
    prior.setdefault("sigma_b2_rho35eq", SB2_RHO35)
    prior.setdefault("delta_C", L1_DELTA)
    prior.setdefault("phi_slow", PHI_SLOW)
    prior.setdefault("n_occ", N_OCC)
    prior.setdefault("n_restart", N_RESTART)
    prior.setdefault("b_boot", B_BOOT)
    prior.setdefault("b_boot_high", B_BOOT_HIGH)
    prior.setdefault("python", sys.version)
    prior.setdefault("numpy", np.__version__)
    prior.setdefault("pandas", pd.__version__)
    prior.setdefault("stage_seconds", {})
    prior["stage_seconds"].update(stage_times)
    prior.update(extra)
    prior["updated_utc"] = datetime.now(UTC).isoformat()
    path.write_text(json.dumps(prior, indent=2, default=str) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True, choices=("part0", "arms", "finalize"))
    parser.add_argument("--cells", default=None, help="comma-separated cell ids (chunking)")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    {"part0": run_part0, "arms": run_arms, "finalize": run_finalize}[args.stage](args)


if __name__ == "__main__":
    main()
