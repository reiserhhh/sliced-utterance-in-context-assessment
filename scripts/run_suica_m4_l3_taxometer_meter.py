#!/usr/bin/env python3
"""M4-L3 -- the TAXOMETER, and the PARTITION-PROPAGATED COMPLETENESS METER.

Registered spec: docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md section "M4-L3 -- The
taxometer, and the partition-propagated completeness meter" (REGISTERED
2026-08-10, BEFORE RUN, commit 034bf48).  Theory:
docs/SUICA_IDENTITY_THEORY_V1.md appendices P, Q and R (R.1 the measured
eta-floor law; R.3 the meter certified on TRUE/GIVEN partitions only, its
estimated-partition form owed to this leg), together with the L2-charter
derivation 3 (the bulk-excess route for eta_hat).

Executor standing: implementation and execution ONLY.  Everything labelled
"PN-n" is a register-note -- an operationalization of something the
registration left open (standing rule 9) -- fixed and written to
reports/SUICA_M4_L3_TAXOMETER_METER_REPORT.md Part 0 BEFORE any main arm ran.
Standing rule 20 is FIRST APPLIED here: if the rule-18 joint check finds ANY
lean's condition-set empty, the leg STOPS before arms as a registration defect
(routing P1N).

CARD SPACE ONLY.  The deployed gauge is never invoked.  Rule-14 self-check:
X-1/X-2 compare eta_hat to eta (both dimensionless mixture fractions), X-3/X-4
compare a normalized variance SHARE to a normalized variance SHARE and regress
a share DEVIATION on a partition-agreement DEFICIT (1 - ARI); no gate and no
lean crosses scales.

Reuse boundary (standing rule 12 -- generator SOURCE OBJECTS, not knob names):
  - scripts/run_suica_m4_l2_threshold_continuum.py imported AS A MODULE (`l2`),
    UNMODIFIED.  This leg calls, and does not reimplement:
      l2.type_geometry_l2       (l2:206-228) S, g, the TWO identity streams
      l2.latent_identity_l2     (l2:231-240) the eta mixture
      l2.typed_trait_l2         (l2:243-253)
      l2.build_typed_world_l2   (l2:256-258)
      l2.occasion_scheme        (l2:270-278) MN-5's cross-fitting split
      l2.cards_for_cell         (l2:281-321) every card object a cell needs
      l2.audit_meter_l2         (l2:464-506) THE CALIBRATED meter (MN-6/MN-8)
      l2.estimated_s            (l2:338-341) / l2.subspace_overlap (l2:344-347)
      l2.predicted_boundary_error_l2 (l2:384-418) the eta floor curve
      l2.projection_gain        (l2:421-424)
      l2.measure_cell_world     (l2:788-855) used ONLY by the G0N L2 anchor
      l2.all_cells / l2.world_seed_for / l2.c_cell_id  (G0N anchor path)
      l2.SB2_RHO35 / l2.SB2_RHO55 / l2.L1_DELTA / l2.ETA_LEVELS / ...
    and, transitively, scripts/run_suica_m4_l1_typed_world.py (`l1`) and
    scripts/run_suica_m4_k2a_expressive_world.py (`k2a`), both UNMODIFIED:
      l1.kmeans_lloyd / l1.spectral_labels  THE TWO GROUPING INSTRUMENTS
      l1.adjusted_rand_index / l1.hungarian_accuracy / l1.boundary_error_rate
      l1.latent_type_vectors / l1.card_space_type_basis / l1.centred_with_trait
      l1._norm_dot / l1.group_centre
      k2a.build_world / arm_weights('zero') / centered_channels / card / splits
      k2a.ar_mean_var / ar_set_var / ar_cross_cov / read_csv_rt / ci_of /
      k2a.mc_sd_of_endpoint / response_panel / K_LATENT / DIM / G_PROFILE /
      k2a.A_SCALE / SIGMA_ISO / UNIT_ENTRY_VAR / N_REP
    plus suica_core's _orthonormal_loadings and stable_bucket.  suica_core is
    NOT touched, and no file outside this one is modified.
  - NEW in this leg (rule 12, cited by THIS file's line numbers in the report):
    full_panel_halves(), split_half_persistent(), whitener_from_state(),
    oracle_whitener(), taxometer(), alignment_angle(), cards_for_cell_l3(),
    pred_panel_l3() (the Part-0 prediction stream WITH a panel, so the meter
    and the taxometer are both predictable before any world exists),
    propagation_fit(), joint_satisfiability_l3(), fidelity_table().

Stages (foreground, chunked, resumable; artifacts under
results/m4_l3_taxometer_meter/):
  --stage part0     G0N/G1N/G2N/G3N/G4N on RESERVED pilot worlds 9901-9904 and
                    a prediction-only seed stream; the rule-19 fidelity table;
                    the rule-18+20 JOINT satisfiability enumeration (a rule-20
                    STOP is written to gates.json and REFUSES the arms); the
                    rule-16 full-object enumeration.  `arms` REFUSES to run
                    unless every gate passes AND the report exists on disk.
  --stage arms      10 cells x 8 main worlds x 512 authors.
  --stage finalize  paired world-block bootstrap, leans X-1..X-4, the
                    propagation fit, rule-13 stability rechecks, the rule-16
                    routing, decision.json.
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

OUT = ROOT / "results" / "m4_l3_taxometer_meter"
REPORT = ROOT / "reports" / "SUICA_M4_L3_TAXOMETER_METER_REPORT.md"
L2_OUT = ROOT / "results" / "m4_l2_threshold_continuum"

# --- registration-fixed constants -------------------------------------------
MASTER_SEED = 20260824          # registration: "master_seed 20260824"
N_AUTHORS = 512                 # registration: "8 worlds x 512 authors/cell"
WORLDS_PER_CELL = 8
PILOT_WORLDS = (9901, 9902, 9903, 9904)   # RESERVED; disjoint from 0..7
G_GROUPS = 4                    # registration: "G=4"
K_TAU = 3                       # registration: "k_tau=3"
PHI_SLOW = 0.90
N_OCC = 8
W_INT_ARM = "zero"
N_RESTART = 64
B_BOOT = 2000                   # registration G3N: "B=2000, seed=master"
B_BOOT_HIGH = 20000             # registration G3N: ">=10xB at boundaries"
ENERGY_BAND_SIGMAS = 4.0        # G0N: design-derived realized-energy band

# --- L2 anchors, quoted from the registration (G0N; round-trip re-derived) ---
L2_POOLED_SAMEDATA_BIAS = -0.005767022729929317
L2_CONDITIONING_RATIO = 2.1537750000000058
L2_BHAT_CAL_BAND = (0.2519, 0.2521)
L2_ANCHOR_CELLS = ("C_rho55eq_eta0", "C_rho55eq_eta1")   # re-derived bit-exactly

# --- lean thresholds, verbatim from the registration ------------------------
X1_SPEARMAN_BAR = 1.0           # "Spearman = 1 per 5-point grid"
X2_TOL = 0.125                  # "|eta_hat - eta| <= 0.125" (grid half-spacing)
X2_MIN_CELLS = 8                # ">=8/10 cells"
X3_R2_BAR = 0.7                 # "pooled fit R^2 >= 0.7"
X3_MIN_TRACK = 8                # "tracks designed shares in >=8/10 cells"
G1N_CI_HALFWIDTH_BAR = 0.3      # registration G1N realizability bar on eta_hat

_L2 = None


def l2() -> Any:
    """The M4-L2 leg script, imported as a module and used UNMODIFIED."""
    global _L2
    if _L2 is None:
        path = ROOT / "scripts" / "run_suica_m4_l2_threshold_continuum.py"
        spec = importlib.util.spec_from_file_location(
            "run_suica_m4_l2_threshold_continuum", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _L2 = module
    return _L2


def l1() -> Any:
    return l2().l1()


def k2a() -> Any:
    return l2().k2a()


# ---------------------------------------------------------------------------
# PN-1 (rule 9): the cells.  The registration fixes the grid completely --
# "L2's C-grid at fresh seeds: eta in {0,.25,.5,.75,1} x two identity energies
# (rho.35/rho.55 equivalents), L1's Delta, G=4, k_tau=3, m=48" -- so there is no
# ladder to solve and no adjustment knob.  10 cells, card space only.

def c_cell_id(energy: str, eta: float) -> str:
    return f"C_{energy}_eta{eta:g}"


def all_cells() -> list[dict[str, Any]]:
    lg2 = l2()
    return [{"cell": c_cell_id(name, eta), "kind": "C", "delta": lg2.L1_DELTA,
             "sigma_b2": sb2, "eta": float(eta), "energy": name}
            for name, sb2 in lg2.C_ENERGIES for eta in lg2.ETA_LEVELS]


def world_seed_for(world: int) -> int:
    """PN-2: the L3 world seed depends on the WORLD INDEX ONLY, under a salt
    disjoint from k2a's, l1's and l2's, so (a) every cell of a world shares the
    loadings, slow state, frame channel, noise, group assignment g, the type
    subspace S and BOTH raw identity draws BIT-FOR-BIT (every cross-cell
    contrast is an exactly paired within-world contrast) and (b) no world of
    this leg coincides with any world of L1 or L2."""
    return int(
        v8.stable_bucket(f"{MASTER_SEED}-{world}", salt="m4l3-world", modulus=2**31 - 1)
    )


# ---------------------------------------------------------------------------
# PN-3 (rule 9): the FULL-PANEL split halves.  L2's cards_for_cell builds its
# split halves INSIDE the audit half {4,5,6,7} because L2's meter is
# cross-fitted.  The TAXOMETER is not the audit: it reads the pooled card
# covariance and needs the panel's full two-split contrast, so it uses k2a's
# canonical splits over ALL EIGHT occasions -- interleaved {0,2,4,6}/{1,3,5,7}
# and contiguous {0,1,2,3}/{4,5,6,7} -- exactly L1's own audit geometry, whose
# contrast c_int - c_cont = 0.0969198750000001 is L2's numerator for the
# 2.1537750000000058x conditioning ratio (G0N anchor).

def full_panel_halves(cen: dict[str, np.ndarray], w: dict[str, float]) -> dict[str, Any]:
    m = k2a()
    sp = m.splits(N_OCC)
    both = (0, 1)
    out: dict[str, Any] = {}
    for name, (s1, s2) in sp.items():
        out[name] = (m.card(cen, w, s1, both, True), m.card(cen, w, s2, both, True))
        out[f"c_{name}"] = m.ar_cross_cov(s1, s2, PHI_SLOW)
    return out


def cards_for_cell_l3(world: dict, typ: dict, delta: float, sigma_b2: float,
                      eta: float) -> dict[str, Any]:
    """L2's cards_for_cell (UNMODIFIED, giving the cross-fitting objects and the
    calibrated meter's inputs) plus the full-panel halves the taxometer needs."""
    obj = l2().cards_for_cell(world, typ, delta, sigma_b2, eta)
    obj["full_halves"] = full_panel_halves(obj["cen"], obj["w"])
    return obj


# ---------------------------------------------------------------------------
# PN-4 (rule 9): THE eta_hat ESTIMATOR, in closed form, fixed before any number.
#
# Derivation (L2 charter derivation 3, carried to a matrix identity).  The card
# is c_i = w_mu M (tau_g + b_i) + w_slow M s_bar_i + w_noise e_bar_i with
# M = A_SCALE * L diag(G_PROFILE) (64x48, full column rank) and
#     Cov(b) = (1-eta) (sigma_b^2/m) I_m + eta (sigma_b^2/k_tau) P_S.
# For the two canonical occasion splits sigma in {interleaved, contiguous},
# form the SYMMETRIZED cross-covariance of the two half-cards,
#     C_sigma = sym[ (1/n) sum_i d_i^(sigma,1) d_i^(sigma,2)T ].
# Observation noise is independent across halves, so it drops out ENTIRELY, and
#     E[C_sigma] = A_mat + c_sigma B_mat,
#     A_mat = w_mu^2 M Cov(trait) M^T   (the PERSISTENT covariance),
#     B_mat = w_slow^2 M M^T            (the STATE-CHANNEL shape),
# with c_sigma = k2a.ar_cross_cov of the two halves.  This is exactly L1's
# validated scalar two-split machinery (RN-8: V_full = A + B v, C_sigma =
# A + B c_sigma) lifted to the covariance matrix, and the trait term cancels
# EXACTLY (not merely in expectation) in C_int - C_cont, because the same t_i
# enters both.  Solve:
#     B_hat_mat = (C_int - C_cont)/(c_int - c_cont),
#     A_hat_mat = C_cont - c_cont B_hat_mat.
# THE WHITENER.  B_hat_mat estimates w_slow^2 M M^T, whose inverse square root
# on its rank-m range satisfies (M M^T)^(-1/2) M = L (orthonormal).  With
# W := U_m Lambda_m^(-1/2) (top m eigenpairs of B_hat_mat) the whitened
# persistent matrix K := W^T A_hat_mat W equals (w_mu^2/w_slow^2) Cov(trait) in
# LATENT coordinates -- i.e. the whitening undoes the G_PROFILE shape, which is
# the only reason the raw card "bulk" is not flat.  Hence, EXACTLY:
#     pooled  K  eigenvalues: 3 spikes (types + aligned identity) and
#                             m - k_tau bulk values c (1-eta) sigma_b^2/m
#     within  K  trace       : c sigma_b^2
# and the estimator is
#     kappa_hat := median of the bottom (m - k_tau) eigenvalues of K_pooled
#     Sigma_hat := trace(K_within)
#     eta_hat   := 1 - m * kappa_hat / Sigma_hat.
# The common factor c = w_mu^2/w_slow^2 cancels, so eta_hat needs NO design
# constant.  In the noiseless limit eta_hat = eta identically at every eta.
# Reported RAW (unclipped); a [0,1]-clipped companion is reported alongside and
# is never used in a lean.  MEDIAN (not mean) over the bulk is the pinned
# robustification: the bulk is flat by the identity above, so the median is
# consistent, and it is insensitive to the few smallest whitened directions
# where the whitener's own estimation error is largest.
#
# WHICH ESTIMATE OF THE STATE-CHANNEL SHAPE (pinned before Part 0, after a
# disclosed 3.2 s feasibility probe on the PREDICTION STREAM ONLY).  The card
# bulk is NOT flat -- derivation 3 wrote "+(1-eta) sigma_b^2/m per dim", which
# is true in LATENT coordinates but not in card coordinates, because
# M M^T = A_SCALE^2 L diag(G_PROFILE^2) L^T spreads every isotropic latent
# channel over a 2.3884x eigenvalue range.  The whitening above is the exact
# repair, and it needs M M^T up to scale.  Four readings, ALL computed in every
# cell and ALL reported:
#   PRIMARY  "state"  -- the PANEL-EXACT realized state channel's INNOVATION
#             second moment, S_innov := sum_{i,t>=1} (s_it - phi s_i,t-1)
#             (...)^T / (n (n_occ-1)(1-phi^2)).  This is the MATRIX analogue of
#             L2's MN-6 per-world panel-exact B_hat calibration, which the L2
#             planner adjudication accepted verbatim as "derived from generator
#             truth about the STATE channel (not about the labels)"; the
#             taxometer is LABEL-FREE in exactly the sense the registration
#             asks, and uses no more generator information than the certified
#             meter it is paired with.  The innovation form is used rather than
#             the marginal second moment because at phi = .90 the eight
#             occasion draws are nearly collinear (marginal condition ratio
#             3.52 against the true 2.3884, innovation 2.63).
#   "split"  -- B_hat_mat itself, the STRICTLY data-only reading.
#   "oracle" -- the generator's own M M^T, the pure upper bound.
#   "flat"   -- NO whitening at all: derivation 3 taken literally, bulk = the
#             median of the pooled persistent spectrum's dimensions
#             k_tau..m-1 in raw card coordinates.  Reported so the planner can
#             see exactly what the shape repair buys.
# GROUPING readings, all computed everywhere:
#   (P) provisional grouping = L1's PRIMARY instrument (Lloyd on the full cards)
#   (S) provisional grouping = L1's SECOND instrument (top-k_tau PCA + Lloyd)
#   (T) TRUE partition (oracle grouping) -- the instrument's upper bound

def split_half_persistent(halves: dict[str, Any], labels: np.ndarray | None
                          ) -> tuple[np.ndarray, np.ndarray]:
    """(A_hat_mat, B_hat_mat) from the two canonical full-panel splits."""
    def dev(x: np.ndarray) -> np.ndarray:
        if labels is None:
            return x - x.mean(axis=0, keepdims=True)
        out = x - x.mean(axis=0, keepdims=True)
        for g in np.unique(labels):
            sel = labels == g
            out[sel] -= out[sel].mean(axis=0, keepdims=True)
        return out

    caps = {}
    for name in ("interleaved", "contiguous"):
        h1, h2 = halves[name]
        d1, d2 = dev(h1), dev(h2)
        cm = (d1.T @ d2) / float(d1.shape[0])
        caps[name] = 0.5 * (cm + cm.T)
    c_int, c_cont = halves["c_interleaved"], halves["c_contiguous"]
    b_mat = (caps["interleaved"] - caps["contiguous"]) / (c_int - c_cont)
    a_mat = caps["contiguous"] - c_cont * b_mat
    return a_mat, b_mat


def whitener_from_state(b_mat: np.ndarray, m_dims: int) -> tuple[np.ndarray, dict[str, float]]:
    ev, evec = np.linalg.eigh(b_mat)
    order = np.argsort(ev)[::-1]
    ev, evec = ev[order], evec[:, order]
    keep = ev[:m_dims]
    diag = {"whitener_eig_min_kept": float(keep[-1]),
            "whitener_eig_max": float(keep[0]),
            "whitener_eig_first_dropped": float(ev[m_dims]) if len(ev) > m_dims else 0.0,
            "whitener_n_nonpositive_kept": int((keep <= 0.0).sum())}
    safe = np.maximum(keep, 1e-12)
    diag["whitener_condition"] = float(safe[0] / safe[-1])
    return evec[:, :m_dims] / np.sqrt(safe)[None, :], diag


def oracle_whitener(world: dict[str, np.ndarray]) -> np.ndarray:
    """(M M^T)^(-1/2) on its rank-m range = L diag(1/(A_SCALE G_PROFILE))."""
    m = k2a()
    return world["loadings"] / (m.A_SCALE * m.G_PROFILE)[None, :]


def state_shape_innovation(cen_slow: np.ndarray) -> np.ndarray:
    """The PRIMARY state-channel shape: the AR innovations' second moment,
    which estimates M M^T with n (n_occ - 1) nearly independent samples."""
    inn = cen_slow[:, 1:, :] - PHI_SLOW * cen_slow[:, :-1, :]
    n, nt, _ = inn.shape
    return np.einsum("itd,ite->de", inn, inn) / (n * nt * (1.0 - PHI_SLOW ** 2))


def state_shape_marginal(cen_slow: np.ndarray) -> np.ndarray:
    n, nt, _ = cen_slow.shape
    return np.einsum("itd,ite->de", cen_slow, cen_slow) / (n * nt)


def _eta_flat(a_pooled: np.ndarray, a_within: np.ndarray, m_dims: int) -> float:
    """Derivation 3 taken LITERALLY: no whitening, a flat card-space bulk."""
    ev = np.sort(np.linalg.eigvalsh(0.5 * (a_pooled + a_pooled.T)))[::-1][:m_dims]
    sigma = float(np.trace(a_within))
    return 1.0 - m_dims * float(np.median(ev[K_TAU:])) / sigma if sigma != 0.0 else float("nan")


def _eta_from_whitened(a_pooled: np.ndarray, a_within: np.ndarray,
                       wht: np.ndarray, m_dims: int) -> dict[str, float]:
    k_pool = wht.T @ a_pooled @ wht
    k_within = wht.T @ a_within @ wht
    mu_pool = np.sort(np.linalg.eigvalsh(0.5 * (k_pool + k_pool.T)))[::-1]
    kappa = float(np.median(mu_pool[K_TAU:]))
    sigma = float(np.trace(k_within))
    eta = 1.0 - m_dims * kappa / sigma if sigma != 0.0 else float("nan")
    mu_within = np.sort(np.linalg.eigvalsh(0.5 * (k_within + k_within.T)))[::-1]
    kappa_w = float(np.median(mu_within[K_TAU:]))
    eta_w = 1.0 - m_dims * kappa_w / sigma if sigma != 0.0 else float("nan")
    return {"eta_hat": float(eta), "kappa_bulk_pooled": kappa,
            "sigma_total_within": sigma, "kappa_bulk_within": kappa_w,
            "eta_hat_withinbulk": float(eta_w),
            "spike_top_within": float(mu_within[0]),
            "spike_ktau_within": float(mu_within[K_TAU - 1])}


def alignment_angle(a_within: np.ndarray, wht: np.ndarray, cards: np.ndarray,
                    labels: np.ndarray, m_dims: int) -> dict[str, float]:
    """PN-5 (rule 9): THE SECOND READING -- the alignment angle between the
    within-provisional-group top-space and the between-group axes, computed in
    the SAME whitened coordinates the bulk-excess route uses (so that "angle"
    means angle in the metric in which the isotropic component is isotropic).

    within top-space  U_w : top-k_tau eigenvectors of K_within = W^T A_w W
    between-group axes U_b: an orthonormal basis of the span of the G
                            provisional group centroids of the whitened cards,
                            grand-mean removed (dimension G-1 = k_tau here)
    overlap := mean squared canonical cosine (l2.subspace_overlap).
    CALIBRATION (pinned): a random k_tau-frame in the m-dim whitened range has
    expected overlap k_tau/m, and a perfectly aligned one has 1, so
        eta_hat_angle := (overlap - k_tau/m)/(1 - k_tau/m).
    This reading is EXPECTED to saturate: the within-group spike-to-bulk ratio
    is eta m /((1-eta) k_tau) = 16 eta/(1-eta), already 5.33 at eta = 0.25, so
    the angle is a DETECTOR of alignment, not a calibrated meter of it.  It is
    reported everywhere and gates nothing."""
    k_within = wht.T @ a_within @ wht
    ev, evec = np.linalg.eigh(0.5 * (k_within + k_within.T))
    u_w = evec[:, np.argsort(ev)[::-1][:K_TAU]]
    y = cards @ wht
    cents = np.stack([y[labels == g].mean(axis=0) for g in np.unique(labels)])
    cents = cents - cents.mean(axis=0, keepdims=True)
    u_b = np.linalg.qr(cents.T)[0][:, :K_TAU]
    ov = l2().subspace_overlap(u_w, u_b)
    frac = K_TAU / float(m_dims)
    return {"angle_overlap": float(ov),
            "eta_hat_angle": float((ov - frac) / (1.0 - frac))}


def taxometer(obj: dict[str, Any], world: dict[str, np.ndarray],
              labels: dict[str, np.ndarray]) -> dict[str, float]:
    m_dims = k2a().K_LATENT
    out: dict[str, float] = {}
    a_pool, b_mat = split_half_persistent(obj["full_halves"], None)
    slow = obj["cen"]["slow"]
    wht_state, diag = whitener_from_state(state_shape_innovation(slow), m_dims)
    out.update(diag)
    wht_split, dsp = whitener_from_state(b_mat, m_dims)
    out["whitener_condition_split"] = dsp["whitener_condition"]
    wht_marg, dmg = whitener_from_state(state_shape_marginal(slow), m_dims)
    out["whitener_condition_marginal"] = dmg["whitener_condition"]
    wht_or = oracle_whitener(world)
    out["whitener_condition_oracle"] = float(
        np.linalg.cond(wht_or.T @ wht_or)) if wht_or.size else 0.0
    a_within: dict[str, np.ndarray] = {}
    for tag, lab in labels.items():
        a_within[tag], _ = split_half_persistent(obj["full_halves"], lab)
    for tag in labels:
        res = _eta_from_whitened(a_pool, a_within[tag], wht_state, m_dims)
        for k, v in res.items():
            out[f"{k}_{tag}"] = v                       # PRIMARY: bare names
        for wname, wmat in (("split", wht_split), ("oracle", wht_or),
                            ("marg", wht_marg)):
            out[f"etaw_{wname}_{tag}"] = _eta_from_whitened(
                a_pool, a_within[tag], wmat, m_dims)["eta_hat"]
        out[f"etaw_flat_{tag}"] = _eta_flat(a_pool, a_within[tag], m_dims)
        out.update({f"{k}_{tag}": v for k, v in
                    alignment_angle(a_within[tag], wht_state, obj["full"],
                                    labels[tag], m_dims).items()})
    out["eta_hat_clipped_P"] = float(min(1.0, max(0.0, out["eta_hat_P"])))
    return out


# ---------------------------------------------------------------------------
# PN-6 (rule 9): THE PROPAGATION MODEL, its regression form, and the correction.
#
# The registration: "audit deviation regressed on (1-ARI) across cells with the
# oracle anchor at ARI = 1".  Pinned:
#   observation unit : one CELL -- the registration's own words are "regressed
#                      on (1-ARI) ACROSS CELLS" -- so n = 10 rows, each row the
#                      cell's world-mean deviation against its world-mean
#                      (1-ARI).  (An earlier draft of this file used the
#                      (cell, world) grain; on the Part-0 prediction stream that
#                      grain is dominated by the per-panel B_hat_cal sampling
#                      noise and attenuates R^2 from 0.83 to 0.07 -- it would
#                      have made X-3a unreachable by construction.  Corrected
#                      to the registration's own grain BEFORE any arm ran; both
#                      grains are reported.)
#   response y       : dev = S_id(estimated partition) - target(same partition)
#                      (both from l2.audit_meter_l2, cross-fitted PRIMARY)
#   regressor x      : 1 - ARI(the partition the audit used, vs generator g)
#   PRIMARY form     : ordinary least squares y = a + b x   (registration-literal)
#   correction       : S_id_corrected := S_id - (a_hat + b_hat x)
#   oracle anchor    : the pooled TRUE-partition deviation on the identical
#                      audit half and the identical calibrated meter (L2's
#                      "or_" reading), which R.3 certified; the clause is
#                      "the anchor lies inside the fit's intercept CI".
# DECLARED SECOND READINGS (fixed here, before any hypothesis number, both
# reported and both checked for routing invariance):
#   (A) y = a + b sqrt(x): ARI is a PAIR-COUNTING index, so near a correct
#       partition 1-ARI grows faster than the misassignment RATE p that the
#       leaked type energy is linear in; the deviation is therefore concave in
#       (1-ARI) and sqrt is the one-parameter concave companion.
#   (B) x = 1 - Hungarian accuracy (the misassignment RATE itself) with the
#       same linear form -- the quantity the leakage derivation is linear in.
# Every fit is refitted INSIDE each paired world-block bootstrap replicate, so
# the corrected meter's CI carries the correction's own uncertainty.

def propagation_fit(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, float]:
    des = np.column_stack([np.ones_like(x), x])
    beta, *_ = np.linalg.lstsq(des, y, rcond=None)
    resid = y - des @ beta
    sst = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float((resid ** 2).sum()) / sst if sst > 0 else float("nan")
    return beta, r2


# ---------------------------------------------------------------------------
# Part-0 PREDICTION STREAM.  An INDEPENDENT re-implementation of the card law
# WITH the occasion panel (salt 'm4l3-pred'): no world of any index -- main or
# pilot -- is generated here.  L2's pred_population_l2 emitted a single card;
# the taxometer and the meter both need the two occasion splits, so this leg's
# prediction stream carries the AR(1) slow state over n_occ ticks and both
# observation reps, exactly as k2a's generator law specifies, without calling
# k2a.build_world.

def pred_seed(rep: int, tag: str) -> int:
    return int(v8.stable_bucket(f"{tag}-{rep}", salt="m4l3-pred", modulus=2**63 - 1))


def pred_panel_l3(delta: float, sigma_b2: float, eta: float, seed: int,
                  n_authors: int = N_AUTHORS) -> dict[str, Any]:
    m = k2a()
    from suica_core.v8_context_relation_field import _orthonormal_loadings
    rng = np.random.default_rng(seed)
    load = _orthonormal_loadings(rng, m.DIM, m.K_LATENT)
    basis = np.linalg.qr(rng.normal(size=(m.K_LATENT, K_TAU)))[0]
    mmat = m.A_SCALE * (load * m.G_PROFILE)                     # (64,48)
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
    xs = np.empty((n_authors, N_OCC, m.K_LATENT))
    xs[:, 0] = rng.normal(size=(n_authors, m.K_LATENT))
    inn = math.sqrt(1.0 - PHI_SLOW**2)
    for t in range(1, N_OCC):
        xs[:, t] = PHI_SLOW * xs[:, t - 1] + inn * rng.normal(
            size=(n_authors, m.K_LATENT))
    trait = (tau[group] + b) @ mmat.T
    slow = (xs @ mmat.T)
    noise = m.SIGMA_ISO * rng.normal(size=(n_authors, N_OCC, m.N_REP, m.DIM))
    cen = {"trait": trait - trait.mean(axis=0, keepdims=True),
           "slow": slow - slow.mean(axis=0, keepdims=True),
           "noise": noise - noise.mean(axis=0, keepdims=True)}

    def mk(occ: np.ndarray) -> np.ndarray:
        return (w["mu"] * cen["trait"] + w["slow"] * cen["slow"][:, occ, :].mean(axis=1)
                + w["noise"] * cen["noise"][:, occ].mean(axis=(1, 2)))

    sp = m.splits(N_OCC)
    halves: dict[str, Any] = {}
    for name, (s1, s2) in sp.items():
        halves[name] = (mk(s1), mk(s2))
        halves[f"c_{name}"] = m.ar_cross_cov(s1, s2, PHI_SLOW)
    fit_occ, aud_occ = sp["contiguous"]
    tau_card = w["mu"] * (tau @ mmat.T)
    shift = (w["mu"] * ((tau[group] + b) @ mmat.T)).mean(axis=0, keepdims=True)
    return {"full": mk(np.arange(N_OCC)), "halves": halves, "group": group,
            "fit_card": mk(fit_occ), "audit_card": mk(aud_occ),
            "centroids": tau_card - shift,
            "b_card": w["mu"] * ((b @ mmat.T) - (b @ mmat.T).mean(axis=0, keepdims=True)),
            "cen": cen, "w": w, "loadings": load, "S": basis,
            "proj": np.linalg.qr(mmat @ basis)[0], "mmat": mmat}


def pred_meter(p: dict[str, Any], labels: np.ndarray) -> dict[str, float]:
    """The calibrated meter's ALGEBRA (l2.audit_meter_l2's form) evaluated on the
    prediction stream: cross-fitted onto the audit half {4,5,6,7} with the
    meter's own two splits inside it."""
    m, lg = k2a(), l1()
    w = p["w"]
    aud = np.arange(N_OCC)[N_OCC // 2:]
    ai = (aud[0::2], aud[1::2])
    ac = (aud[: len(aud) // 2], aud[len(aud) // 2:])

    def mk(occ: np.ndarray) -> np.ndarray:
        return (w["mu"] * p["cen"]["trait"] + w["slow"] * p["cen"]["slow"][:, occ, :].mean(axis=1)
                + w["noise"] * p["cen"]["noise"][:, occ].mean(axis=(1, 2)))

    def st(occ: np.ndarray) -> np.ndarray:
        return p["cen"]["slow"][:, occ, :].mean(axis=1)

    def gc(x: np.ndarray) -> np.ndarray:
        out = x.copy()
        for g in np.unique(labels):
            sel = labels == g
            out[sel] -= x[sel].mean(axis=0, keepdims=True)
        return out

    d_full = gc(mk(aud))
    v_full = lg._norm_dot(d_full, d_full)
    c_i = lg._norm_dot(gc(mk(ai[0])), gc(mk(ai[1])))
    c_c = lg._norm_dot(gc(mk(ac[0])), gc(mk(ac[1])))
    ch_i = lg._norm_dot(gc(st(ai[0])), gc(st(ai[1])))
    ch_c = lg._norm_dot(gc(st(ac[0])), gc(st(ac[1])))
    b_cal = (c_i - c_c) / (ch_i - ch_c)
    a_cal = c_c - b_cal * ch_c
    trait_dev = gc(w["mu"] * p["cen"]["trait"])
    return {"S_id": a_cal / v_full, "B_hat_cal": b_cal,
            "target": lg._norm_dot(trait_dev, trait_dev) / v_full}


def pred_cell(delta: float, sigma_b2: float, eta: float, rep: int,
              full: bool = True) -> dict[str, float]:
    lg1, lg2 = l1(), l2()
    p = pred_panel_l3(delta, sigma_b2, eta, pred_seed(rep, "panel"))
    sd = int(v8.stable_bucket(f"{rep}-{delta:.9f}-{sigma_b2:.9f}-{eta:g}",
                              salt="m4l3-predkm", modulus=2**63 - 1))
    lab_p, _ = lg1.kmeans_lloyd(p["full"], G_GROUPS, N_RESTART, sd)
    labels = {"P": lab_p, "T": p["group"]}
    obj = {"full_halves": p["halves"], "full": p["full"], "cen": p["cen"]}
    tx = taxometer(obj, {"loadings": p["loadings"]}, labels)
    out = {"eta_hat_P": tx["eta_hat_P"], "eta_hat_T": tx["eta_hat_T"],
           "etaw_oracle_P": tx["etaw_oracle_P"], "etaw_oracle_T": tx["etaw_oracle_T"],
           "etaw_split_P": tx["etaw_split_P"], "etaw_flat_P": tx["etaw_flat_P"],
           "eta_hat_angle_P": tx["eta_hat_angle_P"],
           "ari_full": lg1.adjusted_rand_index(p["group"], lab_p),
           "whitener_condition": tx["whitener_condition"],
           "whitener_eig_min_kept": tx["whitener_eig_min_kept"]}
    if full:
        lab_fit, _ = lg1.kmeans_lloyd(p["fit_card"], G_GROUPS, N_RESTART, sd + 3)
        lab_same, _ = lg1.kmeans_lloyd(p["audit_card"], G_GROUPS, N_RESTART, sd + 4)
        mx = pred_meter(p, lab_fit)
        ms = pred_meter(p, lab_same)
        mo = pred_meter(p, p["group"])
        out.update({
            "ari_fit_half": lg1.adjusted_rand_index(p["group"], lab_fit),
            "acc_fit_half": lg1.hungarian_accuracy(p["group"], lab_fit),
            "ari_same_half": lg1.adjusted_rand_index(p["group"], lab_same),
            "xf_S_id": mx["S_id"], "xf_target": mx["target"],
            "xf_dev": mx["S_id"] - mx["target"],
            "sd_S_id": ms["S_id"], "sd_target": ms["target"],
            "sd_dev": ms["S_id"] - ms["target"],
            "or_S_id": mo["S_id"], "or_target": mo["target"],
            "or_dev": mo["S_id"] - mo["target"],
            "xf_B_hat_cal": mx["B_hat_cal"]})
    return out


# ---------------------------------------------------------------------------
# G2N: standing rules 18 + 20.  Every lean's clause-set is reduced to a SET OF
# DESIGN POINTS over the (Delta, sigma_b^2) plane -- the only generative knobs
# the leans share once the eta grid is fixed by the registration -- and the
# clauses of each lean are INTERSECTED.  Rule 20: ANY empty intersection STOPS
# the leg before the arms.  The registered design point is marked but is NOT
# what decides emptiness: emptiness is decided over the whole plane.

JS_DELTA_FACTORS = (0.7, 1.0, 1.4)
JS_ENERGY_FACTORS = (0.5, 1.0, 2.0)
JS_REPS = 8


def joint_satisfiability_l3() -> dict[str, Any]:
    """PN-9: every clause is evaluated with the SAME PAIRED structure the
    finalize stage uses -- a quantity the lean forms as a within-replicate
    DIFFERENCE (the X-4 bias) or as a pooled REGRESSION COEFFICIENT (the X-3
    intercept) takes its uncertainty from the spread of that same
    within-replicate object across replicates, never from the marginal spread
    of one of its terms.  The prediction-stream replicate plays the role the
    world block plays in the arms."""
    lg2 = l2()
    etas = list(lg2.ETA_LEVELS)
    grid_rows: list[dict[str, Any]] = []
    points: list[dict[str, Any]] = []
    for df in JS_DELTA_FACTORS:
        delta = lg2.L1_DELTA * df
        for ef in JS_ENERGY_FACTORS:
            energies = [("rho35eq", lg2.SB2_RHO35 * ef), ("rho55eq", lg2.SB2_RHO55 * ef)]
            per_cell = []
            for name, sb2 in energies:
                for eta in etas:
                    reps = [pred_cell(delta, sb2, eta, r) for r in range(JS_REPS)]
                    rec: dict[str, Any] = {
                        "delta_factor": df, "energy_factor": ef, "delta": delta,
                        "energy": name, "sigma_b2": sb2, "eta": eta}
                    for key in ("eta_hat_P", "etaw_oracle_P", "eta_hat_T",
                                "eta_hat_angle_P", "ari_fit_half", "acc_fit_half",
                                "xf_dev", "or_dev", "sd_dev"):
                        arr = np.array([r[key] for r in reps], dtype=float)
                        rec[key] = float(arr.mean())
                        rec[f"{key}_sd"] = float(arr.std(ddof=1))
                        rec[f"{key}_reps"] = arr
                    per_cell.append(rec)
                    grid_rows.append({k: v for k, v in rec.items()
                                      if not k.endswith("_reps")})
            points.append({"delta_factor": df, "energy_factor": ef,
                           "delta": delta, "cells": per_cell})
    grid = pd.DataFrame(grid_rows)

    def half_width(sd: float) -> float:
        """A JS_REPS-replicate prediction-stream sd converted to a main-design
        (n=8) CI half-width, at the t-quantile the pilot MDEs use."""
        return float(student_t.ppf(0.975, JS_REPS - 1)) * sd / math.sqrt(WORLDS_PER_CELL)

    clause_sets: dict[str, list[bool]] = {}
    diagnostics: list[dict[str, Any]] = []
    keys = [f"d{p['delta_factor']:g}_e{p['energy_factor']:g}" for p in points]
    for cname in ("X-1a monotone (Spearman=1) at BOTH energies",
                  "X-1b pole CI contains 0 at eta=0 (both energies)",
                  "X-1c pole CI contains 1 at eta=1 (both energies)",
                  "X-2 |eta_hat - eta| <= 0.125 in >=8/10 cells",
                  "X-3a propagation fit R^2 >= 0.7",
                  "X-3b oracle anchor inside the intercept CI",
                  "X-3c corrected meter tracks in >=8/10 cells",
                  "X-4 corrected same-data bias CI excludes 0 (optimistic)"):
        clause_sets[cname] = []
    for key, p in zip(keys, points, strict=True):
        cells = p["cells"]
        ok_mono = True
        for name in ("rho35eq", "rho55eq"):
            seq = [c["eta_hat_P"] for c in cells if c["energy"] == name]
            ok_mono = ok_mono and all(a < b for a, b in zip(seq, seq[1:], strict=False))
        clause_sets["X-1a monotone (Spearman=1) at BOTH energies"].append(bool(ok_mono))
        ok0 = all(abs(c["eta_hat_P"] - 0.0) <= half_width(c["eta_hat_P_sd"])
                  for c in cells if c["eta"] == 0.0)
        ok1 = all(abs(c["eta_hat_P"] - 1.0) <= half_width(c["eta_hat_P_sd"])
                  for c in cells if c["eta"] == 1.0)
        clause_sets["X-1b pole CI contains 0 at eta=0 (both energies)"].append(bool(ok0))
        clause_sets["X-1c pole CI contains 1 at eta=1 (both energies)"].append(bool(ok1))
        n_ok = sum(1 for c in cells if abs(c["eta_hat_P"] - c["eta"]) <= X2_TOL)
        clause_sets["X-2 |eta_hat - eta| <= 0.125 in >=8/10 cells"].append(
            bool(n_ok >= X2_MIN_CELLS))
        x_rep = np.stack([1.0 - c["ari_fit_half_reps"] for c in cells])
        y_rep = np.stack([c["xf_dev_reps"] for c in cells])
        s_rep = np.stack([c["sd_dev_reps"] for c in cells])
        o_rep = np.stack([c["or_dev_reps"] for c in cells])
        beta, r2 = propagation_fit(x_rep.mean(axis=1), y_rep.mean(axis=1))
        r2_rowgrain = propagation_fit(x_rep.reshape(-1), y_rep.reshape(-1))[1]
        ints, corr_cols, bias_r = [], [], []
        for r in range(JS_REPS):
            br, _ = propagation_fit(x_rep[:, r], y_rep[:, r])
            ints.append(float(br[0]))
            cx = y_rep[:, r] - (br[0] + br[1] * x_rep[:, r])
            cs = s_rep[:, r] - (br[0] + br[1] * x_rep[:, r])
            corr_cols.append(cx)
            bias_r.append(float(np.mean(cs - cx)))
        corr_r = np.stack(corr_cols, axis=1)
        anchor = float(o_rep.mean())
        int_hw = half_width(float(np.std(ints, ddof=1)))
        clause_sets["X-3a propagation fit R^2 >= 0.7"].append(bool(r2 >= X3_R2_BAR))
        clause_sets["X-3b oracle anchor inside the intercept CI"].append(
            bool(abs(anchor - beta[0]) <= int_hw))
        n_track = sum(1 for i in range(len(cells))
                      if abs(float(corr_r[i].mean()))
                      <= half_width(float(np.std(corr_r[i], ddof=1))))
        clause_sets["X-3c corrected meter tracks in >=8/10 cells"].append(
            bool(n_track >= X3_MIN_TRACK))
        bias_pt = float(np.mean(bias_r))
        bias_hw = half_width(float(np.std(bias_r, ddof=1)))
        clause_sets["X-4 corrected same-data bias CI excludes 0 (optimistic)"].append(
            bool(bias_pt + bias_hw < 0.0))
        diagnostics.append({
            "point": key, "r2_linear": float(r2),
            "r2_at_row_grain": float(r2_rowgrain), "intercept": float(beta[0]),
            "slope": float(beta[1]), "intercept_halfwidth": int_hw,
            "oracle_anchor": anchor, "n_corrected_tracking": int(n_track),
            "n_eta_within_tol": int(n_ok), "monotone": bool(ok_mono),
            "pole0_ok": bool(ok0), "pole1_ok": bool(ok1),
            "corrected_bias": bias_pt, "corrected_bias_halfwidth": bias_hw,
            "raw_bias": float(np.mean(s_rep - y_rep))})

    lean_clauses = {
        "X-1": ["X-1a monotone (Spearman=1) at BOTH energies",
                "X-1b pole CI contains 0 at eta=0 (both energies)",
                "X-1c pole CI contains 1 at eta=1 (both energies)"],
        "X-2": ["X-2 |eta_hat - eta| <= 0.125 in >=8/10 cells"],
        "X-3": ["X-3a propagation fit R^2 >= 0.7",
                "X-3b oracle anchor inside the intercept CI",
                "X-3c corrected meter tracks in >=8/10 cells"],
        "X-4": ["X-4 corrected same-data bias CI excludes 0 (optimistic)"],
    }
    registered_key = "d1_e1"
    reg_idx = keys.index(registered_key)
    lean_sets: dict[str, Any] = {}
    empty: list[str] = []
    for lean, cls in lean_clauses.items():
        inter = np.ones(len(keys), dtype=bool)
        for c in cls:
            inter = inter & np.asarray(clause_sets[c], dtype=bool)
        pts = [keys[i] for i in np.nonzero(inter)[0]]
        lean_sets[lean] = {
            "clauses": cls, "n_points": int(inter.sum()), "points": pts,
            "satisfiable": bool(inter.any()),
            "registered_point_inside": bool(inter[reg_idx]),
            "per_clause_points": {c: [keys[i] for i in
                                      np.nonzero(np.asarray(clause_sets[c]))[0]]
                                  for c in cls},
        }
        if not inter.any():
            empty.append(lean)
    pairwise = {}
    cnames = list(clause_sets)
    for a, b in itertools.combinations(cnames, 2):
        inter = np.asarray(clause_sets[a]) & np.asarray(clause_sets[b])
        pairwise[f"{a}  AND  {b}"] = {
            "satisfiable": bool(inter.any()),
            "points": [keys[i] for i in np.nonzero(inter)[0]]}
    return {"grid_points": keys, "delta_factors": list(JS_DELTA_FACTORS),
            "energy_factors": list(JS_ENERGY_FACTORS), "reps": JS_REPS,
            "registered_point": registered_key,
            "clause_sets": {k: [keys[i] for i in np.nonzero(np.asarray(v))[0]]
                            for k, v in clause_sets.items()},
            "clause_n_points": {k: int(np.asarray(v).sum()) for k, v in clause_sets.items()},
            "pairwise": pairwise, "lean_sets": lean_sets,
            "per_point_diagnostics": diagnostics,
            "rule20_empty_leans": empty, "rule20_stop": bool(len(empty) > 0),
            "grid_table": grid.to_dict(orient="records")}


# ---------------------------------------------------------------------------
# rule-16 enumeration (G4N)

SUB_STATES = ("HOLD", "MISS", "BOUNDARY", "UNREALIZABLE")
LEAN_STATES = ("HOLD", "MISS", "BOUNDARY")
LEAN_SUBCLAUSES = {
    "X-1": ["eta_hat (PRIMARY) strictly monotone in designed eta (Spearman=1) "
            "at BOTH energies",
            "pole calibration: eta_hat CI contains 0 at eta=0 and 1 at eta=1, "
            "all four pole cells"],
    "X-2": ["|eta_hat - eta| <= 0.125 in >=8/10 cells"],
    "X-3": ["pooled deviation~(1-ARI) fit R^2 >= 0.7",
            "oracle anchor inside the fit's CI at ARI=1 (the intercept CI)",
            "corrected meter tracks designed shares in >=8/10 cells on "
            "ESTIMATED partitions"],
    "X-4": ["pooled same-data optimistic bias under the CORRECTED meter, "
            "CI excluding 0 on the optimistic side"],
}


def lean_from_subclauses(states: tuple[str, ...]) -> str:
    """PN-7: CONJUNCTIVE aggregation, identical to L1's RN-11 and L2's MN-9."""
    live = [s for s in states if s != "UNREALIZABLE"]
    if not live:
        return "BOUNDARY"
    if "MISS" in live:
        return "MISS"
    if "BOUNDARY" in live:
        return "BOUNDARY"
    return "HOLD"


def route(lean_states: dict[str, str], rule20_stop: bool) -> str:
    """Registration routing, made TOTAL (a BOUNDARY lean is not a HOLD)."""
    if rule20_stop:
        return "P1N"
    if lean_states["X-1"] != "HOLD":
        return "P2N"
    if lean_states["X-3"] != "HOLD":
        return "P3N"
    return "P4N"


def build_enumeration() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    rows = []
    for lean, subs in LEAN_SUBCLAUSES.items():
        for combo in itertools.product(SUB_STATES, repeat=len(subs)):
            rows.append({"lean": lean, "n_subclauses": len(subs),
                         "subclause_states": "|".join(combo),
                         "lean_state": lean_from_subclauses(combo)})
    layer_a = pd.DataFrame(rows)
    rows2 = []
    for stop in (False, True):
        for combo in itertools.product(LEAN_STATES, repeat=4):
            states = dict(zip(["X-1", "X-2", "X-3", "X-4"], combo, strict=True))
            rows2.append({"rule20_stop": stop,
                          **{f"state_{k}": v for k, v in states.items()},
                          "n_miss": sum(1 for v in combo if v == "MISS"),
                          "n_boundary": sum(1 for v in combo if v == "BOUNDARY"),
                          "route": route(states, stop)})
    layer_b = pd.DataFrame(rows2)
    reg = layer_b[(~layer_b["rule20_stop"]) & (
        layer_b[[f"state_X-{i}" for i in (1, 2, 3, 4)]] != "BOUNDARY").all(axis=1)]
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
            ["rule20_stop"] + [f"state_X-{i}" for i in (1, 2, 3, 4)]
        ].drop_duplicates().shape[0]),
        "layer_b_all_assigned": bool(layer_b["route"].isin(
            ["P1N", "P2N", "P3N", "P4N"]).all()),
        "layer_b_route_counts": {k: int(v) for k, v in layer_b["route"].value_counts().items()},
        "layer_b_all_routes_reachable": bool(
            set(layer_b["route"]) == {"P1N", "P2N", "P3N", "P4N"}),
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
    m, lg1, lg2 = k2a(), l1(), l2()
    cid, delta, sb2, eta = spec["cell"], spec["delta"], spec["sigma_b2"], spec["eta"]
    obj = cards_for_cell_l3(world, typ, delta, sb2, eta)
    group = typ["group"]
    x = obj["full"]
    sd = int(v8.stable_bucket(f"{world_seed}-{cid}", salt="m4l3-kmeans", modulus=2**63 - 1))
    lab_p, in_p = lg1.kmeans_lloyd(x, G_GROUPS, N_RESTART, sd)
    lab_s, in_s, _sv = lg1.spectral_labels(x, G_GROUPS, K_TAU, N_RESTART, sd + 1)
    lab_fit, _ = lg1.kmeans_lloyd(obj["fit_card"], G_GROUPS, N_RESTART, sd + 3)
    lab_same, _ = lg1.kmeans_lloyd(obj["audit_card"], G_GROUPS, N_RESTART, sd + 4)
    lab_fit_s, _, _ = lg1.spectral_labels(obj["fit_card"], G_GROUPS, K_TAU, N_RESTART, sd + 5)
    row: dict[str, Any] = {
        "cell": cid, "kind": spec["kind"], "energy": spec["energy"],
        "delta": delta, "sigma_b2": sb2, "eta": eta, "world_seed": world_seed,
        "n_authors": int(x.shape[0]),
        "ari_primary": lg1.adjusted_rand_index(group, lab_p),
        "ari_spectral": lg1.adjusted_rand_index(group, lab_s),
        "acc_primary": lg1.hungarian_accuracy(group, lab_p),
        "acc_spectral": lg1.hungarian_accuracy(group, lab_s),
        "inertia_primary": in_p, "inertia_spectral": in_s,
        "ari_fit_half": lg1.adjusted_rand_index(group, lab_fit),
        "acc_fit_half": lg1.hungarian_accuracy(group, lab_fit),
        "ari_fit_half_spectral": lg1.adjusted_rand_index(group, lab_fit_s),
        "acc_fit_half_spectral": lg1.hungarian_accuracy(group, lab_fit_s),
        "ari_same_half": lg1.adjusted_rand_index(group, lab_same),
        "acc_same_half": lg1.hungarian_accuracy(group, lab_same),
        "boundary_err_true_card": lg1.boundary_error_rate(
            obj["true_card"], obj["centroids"], group),
        "floor_pred_identity": lg2.predicted_boundary_error_l2(
            world, typ, delta, sb2, eta, True),
        "projection_gain_G_eta": lg2.projection_gain(eta),
    }
    # --- the TAXOMETER (question A)
    row.update(taxometer(obj, world, {"P": lab_p, "S": lab_s, "T": group}))
    # --- the calibrated METER (question B), L2's own audit_meter_l2, UNMODIFIED
    row.update(lg2.audit_meter_l2(obj, lab_fit, "xf"))     # PRIMARY cross-fitted
    row.update(lg2.audit_meter_l2(obj, lab_same, "sd"))    # SECOND same-data
    row.update(lg2.audit_meter_l2(obj, group, "or"))       # oracle/true partition
    row.update(lg2.audit_meter_l2(obj, lab_fit_s, "xs"))   # spectral cross-fitted
    for tag in ("xf", "sd", "or", "xs"):
        row[f"{tag}_dev"] = row[f"{tag}_S_id"] - row[f"{tag}_target"]
    # --- realized design quantities (G0N)
    b_lat = obj["b_lat"]
    tau = lg1.latent_type_vectors(typ["S"], delta)
    e_tot = float(np.mean(np.einsum("ij,ij->i", b_lat, b_lat)))
    in_s_e = (b_lat @ typ["S"])
    e_in_s = float(np.mean(np.einsum("ij,ij->i", in_s_e, in_s_e)))
    frac_s = e_in_s / e_tot if e_tot > 0 else 0.0
    kfrac = K_TAU / m.K_LATENT
    row["realized_sigma_b2"] = e_tot
    row["realized_energy_in_S_fraction"] = frac_s
    row["realized_eta"] = (frac_s - kfrac) / (1.0 - kfrac) if e_tot > 0 else 0.0
    pw = np.linalg.norm(tau[:, None, :] - tau[None, :, :], axis=2)[
        np.triu_indices(G_GROUPS, 1)]
    row["realized_delta_latent_min"] = float(pw.min())
    row["realized_delta_latent_max"] = float(pw.max())
    row["card_var_norm"] = lg1._norm_dot(x, x)
    return row


def run_world_cells(world: int, cells: list[dict[str, Any]],
                    n_authors: int = N_AUTHORS) -> list[dict[str, Any]]:
    wseed = world_seed_for(world)
    world_obj, typ = l2().build_typed_world_l2(wseed, n_authors)
    return [measure_cell_world(world_obj, typ, spec, wseed) for spec in cells]


# ---------------------------------------------------------------------------
# G3N: the rule-19 FIDELITY TABLE

def fidelity_table(pred: pd.DataFrame) -> list[dict[str, str]]:
    m = k2a()
    reg = pred[pred["source"] == "registered"]

    def curve(col: str) -> str:
        return ", ".join(f"{r['energy']}/eta={r['eta']:g}: {r[col]!r}"
                         for _, r in reg.iterrows())

    return [
        {
            "lean": "X-1",
            "theorem_quantity":
                "eta ITSELF -- the aligned fraction of identity energy in the "
                "L2-charter mixture b = sqrt(1-eta) b_iso + sqrt(eta) b_aligned. "
                "The registration states the shadowed quantity explicitly: "
                "'shadows: eta itself'.",
            "predicted":
                "the bulk-excess identity (PN-4) is EXACT in the noiseless limit: "
                "eta_hat = 1 - m kappa/Sigma = eta at every eta, because the "
                "whitened persistent covariance is (w_mu^2/w_slow^2) Cov(b) in "
                "latent coordinates, whose bulk is (1-eta) sigma_b^2/m on m-k_tau "
                "dimensions and whose trace is sigma_b^2.  Prediction-stream "
                f"curve at the registered design point: {curve('eta_hat_P')}; "
                f"pure-oracle whitener {curve('etaw_oracle_P')}; strictly "
                f"data-only whitener {curve('etaw_split_P')}; NO whitening "
                f"(derivation 3 literal) {curve('etaw_flat_P')}.  "
                "Monotone by construction; the pole values are the calibration "
                "test, since at eta=0 the bulk IS the whole signal and at eta=1 "
                "the bulk is pure estimation error.",
            "bar": "Spearman rank correlation of eta_hat with designed eta = 1 "
                   "on each 5-point grid (both energies), AND the eta_hat CI "
                   "contains 0 at eta=0 and 1 at eta=1 in all four pole cells",
            "why_this_quantity":
                "rule 19: the taxometer's own estimand is eta, on eta's own "
                "[0,1] scale; the bar is an ordering plus two point-calibrations "
                "OF THAT SAME NUMBER, not of any downstream ARI or share",
        },
        {
            "lean": "X-2",
            "theorem_quantity":
                "eta again, now at the CALIBRATION grain: the absolute error "
                "|eta_hat - eta| of the same estimator",
            "predicted":
                "zero bias in the noiseless limit (PN-4's identity), so the error "
                "is pure estimation error with two identified sources: (i) the "
                "whitener's own error, which enters kappa multiplicatively and is "
                "isolated by the ORACLE-WHITENER reading; (ii) provisional-"
                "grouping error, which both truncates Sigma (group-centring on "
                "estimated labels removes real within-group variance) and leaks "
                "type energy into the S directions -- BOTH push eta_hat UP, so "
                "the predicted sign of the bias is POSITIVE and growing as ARI "
                f"falls.  Prediction-stream values: {curve('eta_hat_P')} against "
                f"the TRUE-partition reading {curve('eta_hat_T')}",
            "bar": f"|eta_hat - eta| <= {X2_TOL} (half the grid spacing) in >= "
                   f"{X2_MIN_CELLS}/10 cells",
            "why_this_quantity":
                "the bar is on the estimator's error IN THE UNITS OF ITS OWN "
                "ESTIMAND, at the resolution the 5-point grid itself defines "
                "(half-spacing); no other scale is involved",
        },
        {
            "lean": "X-3",
            "theorem_quantity":
                "appendix R.3's open object: the ESTIMATED-partition audit "
                "deviation, dev = S_id - target, as a function of PARTITION "
                "QUALITY -- and the corrected meter built from that function. "
                "R.3 certified the meter on true/given partitions ONLY and named "
                "the residual PARTITION-borne; the propagation model is the "
                "claim that the partition-borne part is a FUNCTION of (1-ARI) "
                "with the true-partition deviation as its value at ARI=1",
            "predicted":
                "leaked type energy enters the within-group deviations in "
                "proportion to the misassignment rate, so dev is monotone "
                "decreasing in (1-ARI) and CONCAVE in it (ARI is a pair-counting "
                "index, so 1-ARI grows faster than the rate).  On L2's own "
                "persisted 10 C-cells the registration-literal LINEAR fit gives "
                "R^2 = 0.8272, slope -0.036000, intercept -0.013395 against an "
                "oracle anchor of -0.0074985 -- i.e. the fit's shape clause is "
                "predicted to pass and the ANCHOR clause is the one at risk, "
                "exactly because of the predicted concavity (the sqrt companion "
                "gives R^2 = 0.9276 and intercept -0.006227 there).  Fresh-seed "
                f"prediction-stream fit: see the Part-0 propagation row.",
            "bar": f"pooled fit R^2 >= {X3_R2_BAR} AND the oracle anchor inside "
                   "the fit's CI at ARI=1 (the intercept's paired world-block CI) "
                   f"AND the corrected meter's CI contains the designed share in "
                   f">= {X3_MIN_TRACK}/10 cells on ESTIMATED partitions",
            "why_this_quantity":
                "share-vs-share throughout: the response is a difference of two "
                "normalized variance shares, the regressor is a dimensionless "
                "partition-agreement deficit, and the anchor is the SAME share "
                "difference measured on the true partition (L2's 'or_' reading), "
                "so the clause at ARI=1 compares like with like",
        },
        {
            "lean": "X-4",
            "theorem_quantity":
                "L2-charter derivation 4's SIGN: same-data auditing (cluster and "
                "audit on the same occasions) understates surviving identity, "
                "because nearest-centroid assignment truncates the "
                "boundary-crossing part of the within-group deviations.  L2 "
                f"measured it at {L2_POOLED_SAMEDATA_BIAS!r} pooled over the same "
                "10 cells; the question here is whether the CORRECTION removes it "
                "(it should not: the correction models partition QUALITY, and the "
                "truncation is a property of same-data FITTING at any quality)",
            "predicted":
                "the corrected bias stays negative and of the same order as L2's, "
                "because the propagation term is fitted on the cross-fitted "
                "deviations and applied to each reading at ITS OWN (1-ARI), and "
                "the two ARIs are nearly equal (L2: fit-half vs same-half ARI "
                "differ by <0.02 in every cell) -- so the correction subtracts "
                "almost the same number from both and cannot cancel the "
                "truncation term",
            "bar": "pooled (same-data corrected - cross-fitted corrected) CI "
                   "excludes 0 on the NEGATIVE (optimistic) side",
            "why_this_quantity":
                "derivation 4 predicts a SIGN on a difference of two shares; the "
                "bar is that sign, on that difference, with the size reported as "
                "a measured named quantity and deliberately NOT gated",
        },
    ]


# ---------------------------------------------------------------------------
# Stage: part0

def run_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    m, lg1, lg2 = k2a(), l1(), l2()
    gates: dict[str, Any] = {
        "leg": "M4-L3", "banner": BANNER,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED, "pilot_worlds": list(PILOT_WORLDS),
        "n_authors": N_AUTHORS, "worlds_per_cell": WORLDS_PER_CELL,
        "G": G_GROUPS, "k_tau": K_TAU, "k_latent": m.K_LATENT, "dim": m.DIM,
        "phi_slow": PHI_SLOW, "n_occ": N_OCC, "w_int_arm": W_INT_ARM,
        "n_restart": N_RESTART,
        "knobs": {"delta": lg2.L1_DELTA, "sigma_b2_rho55eq": lg2.SB2_RHO55,
                  "sigma_b2_rho35eq": lg2.SB2_RHO35,
                  "eta_levels": list(lg2.ETA_LEVELS),
                  "grid_fixed_by_registration": True},
        "grain": {"analysis_grain": "world (8 independent world blocks per cell)",
                  "rule5_justification": "every registered statistic is a per-world "
                  "scalar (an eta_hat, a variance share, a share deviation, an ARI); "
                  "the paired world-block bootstrap over the 8 worlds is the only "
                  "independent resampling unit, and the 4-world pilot MDEs are at "
                  "that grain"},
    }
    st: dict[str, float] = {}
    cells = all_cells()

    # ---- G0N: the L2 ANCHORS -------------------------------------------------
    t = time.time()
    anchors: dict[str, Any] = {}
    persisted = m.read_csv_rt(L2_OUT / "cells.csv")
    l2_cellrows = m.read_csv_rt(L2_OUT / "cell_C_rho55eq_eta0.csv")  # round-trip probe
    anchors["round_trip_probe_rows"] = int(len(l2_cellrows))
    ccells_l2 = [c for c in persisted["cell"] if str(c).startswith("C_")]
    # (a) pooled same-data bias, recomputed from L2's persisted PER-WORLD cells
    biases = []
    for cid in ccells_l2:
        f = m.read_csv_rt(L2_OUT / f"cell_{cid}.csv")
        biases.append(float((f["sd_S_id"] - f["xf_S_id"]).mean()))
    pooled_bias = float(np.mean(biases))
    anchors["pooled_samedata_bias"] = {
        "registration": L2_POOLED_SAMEDATA_BIAS, "recomputed": pooled_bias,
        "residual": abs(pooled_bias - L2_POOLED_SAMEDATA_BIAS),
        "bit_exact": bool(pooled_bias == L2_POOLED_SAMEDATA_BIAS)}
    # (b) the conditioning ratio, re-derived from k2a's OWN AR algebra
    sp_full = m.splits(N_OCC)
    c_int_full = m.ar_cross_cov(*sp_full["interleaved"], PHI_SLOW)
    c_cont_full = m.ar_cross_cov(*sp_full["contiguous"], PHI_SLOW)
    sc = lg2.occasion_scheme()
    c_int_aud = m.ar_cross_cov(*sc["audit_int"], PHI_SLOW)
    c_cont_aud = m.ar_cross_cov(*sc["audit_cont"], PHI_SLOW)
    ratio = (c_int_full - c_cont_full) / (c_int_aud - c_cont_aud)
    anchors["conditioning_ratio"] = {
        "registration": L2_CONDITIONING_RATIO, "recomputed": ratio,
        "L1_contrast": c_int_full - c_cont_full, "L2_audit_contrast": c_int_aud - c_cont_aud,
        "bit_exact": bool(ratio == L2_CONDITIONING_RATIO)}
    # (c) the B_hat_cal band
    bh = persisted[persisted["kind"] == "C"]["xf_B_hat_cal"].to_numpy(float)
    anchors["B_hat_cal_band"] = {
        "registration_band": list(L2_BHAT_CAL_BAND),
        "min": float(bh.min()), "max": float(bh.max()),
        "min_rounded_4dp": round(float(bh.min()), 4),
        "max_rounded_4dp": round(float(bh.max()), 4),
        "note": ("the registration quotes the band to FOUR DECIMALS "
                 "('B_hat_cal band 0.2519-0.2521'); L2's realized extremes are "
                 "0.2519088212714649 and 0.2521478508144498, so the anchor test "
                 "is equality of the 4-decimal rounding, not an interval "
                 "containment of the unrounded extremes"),
        "inside_band": bool(round(float(bh.min()), 4) == L2_BHAT_CAL_BAND[0]
                            and round(float(bh.max()), 4) == L2_BHAT_CAL_BAND[1])}
    # (d) the FLOOR-CURVE cells and the AUDIT table, RE-DERIVED bit-exactly by
    #     calling L2's own measurement path on L2's own worlds
    rederived: dict[str, Any] = {}
    l2_specs = {c["cell"]: c for c in lg2.all_cells([lg2.L1_DELTA] * 5)}
    for cid in L2_ANCHOR_CELLS:
        spec = l2_specs[cid]
        acc: dict[str, list[float]] = {}
        for wi in range(lg2.WORLDS_PER_CELL):
            ws = lg2.world_seed_for(wi)
            wo, ty = lg2.build_typed_world_l2(ws, lg2.N_AUTHORS)
            r = lg2.measure_cell_world(wo, ty, spec, ws)
            for k in ("boundary_err_true_card", "floor_pred_identity", "xf_S_id",
                      "xf_target", "sd_S_id", "or_S_id", "or_target", "xf_B_hat_cal"):
                acc.setdefault(k, []).append(float(r[k]))
        pf = m.read_csv_rt(L2_OUT / f"cell_{cid}.csv").sort_values("world")
        rederived[cid] = {k: {"rederived_mean": float(np.mean(v)),
                              "persisted_mean": float(pf[k].mean()),
                              "max_abs_row_residual": float(
                                  np.abs(np.asarray(v) - pf[k].to_numpy(float)).max()),
                              "bit_exact_rows": bool(np.all(
                                  np.asarray(v) == pf[k].to_numpy(float)))}
                          for k, v in acc.items()}
    anchors["l2_cells_rederived"] = rederived
    anchors["l2_cells_bit_exact"] = bool(all(
        col["bit_exact_rows"] for cell in rederived.values() for col in cell.values()))
    anchors["all_bit_exact"] = bool(
        anchors["pooled_samedata_bias"]["bit_exact"]
        and anchors["conditioning_ratio"]["bit_exact"]
        and anchors["B_hat_cal_band"]["inside_band"]
        and anchors["l2_cells_bit_exact"])
    st["anchors"] = time.time() - t

    # ---- G0N: construction on the RESERVED pilot worlds -----------------------
    t = time.time()
    g0: dict[str, Any] = {"recon_residual_max": 0.0, "sigma_b2_rel_dev_max": 0.0,
                          "eta_dev_abs_max": 0.0, "delta_latent_dev_abs_max": 0.0,
                          "per_world": [], "l2_anchors": anchors}
    g1: dict[str, Any] = {"per_world": []}
    pilot_rows = []
    for world in PILOT_WORLDS:
        wseed = world_seed_for(world)
        world_obj, typ = lg2.build_typed_world_l2(wseed, N_AUTHORS)
        w = m.arm_weights(W_INT_ARM)
        trait = lg2.typed_trait_l2(world_obj, typ, lg2.L1_DELTA, lg2.SB2_RHO55, 0.5)
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
        base = cards_for_cell_l3(world_obj, typ, lg2.L1_DELTA, lg2.SB2_RHO55, 0.5)
        no_id = m.card(lg1.centred_with_trait(
            world_obj, lg2.typed_trait_l2(world_obj, typ, lg2.L1_DELTA, lg2.SB2_RHO55,
                                          0.5, drop_identity=True)),
            w, np.arange(N_OCC), (0, 1), True)
        no_type = m.card(lg1.centred_with_trait(
            world_obj, lg2.typed_trait_l2(world_obj, typ, lg2.L1_DELTA, lg2.SB2_RHO55,
                                          0.5, drop_type=True)),
            w, np.arange(N_OCC), (0, 1), True)
        eta0 = cards_for_cell_l3(world_obj, typ, lg2.L1_DELTA, lg2.SB2_RHO55, 0.0)["full"]
        eta1 = cards_for_cell_l3(world_obj, typ, lg2.L1_DELTA, lg2.SB2_RHO55, 1.0)["full"]
        # the two full-panel splits must actually differ (the taxometer's contrast)
        hv = base["full_halves"]
        g1["per_world"].append({
            "world": world,
            "rms_drop_type": float(np.sqrt(np.mean((base["full"] - no_type) ** 2))),
            "rms_drop_identity": float(np.sqrt(np.mean((base["full"] - no_id) ** 2))),
            "rms_eta0_vs_eta1": float(np.sqrt(np.mean((eta0 - eta1) ** 2))),
            "c_int_minus_c_cont": float(hv["c_interleaved"] - hv["c_contiguous"]),
            "rms_int_vs_cont_half": float(np.sqrt(np.mean(
                (hv["interleaved"][0] - hv["contiguous"][0]) ** 2))),
        })
        rows = [measure_cell_world(world_obj, typ, spec, wseed) for spec in cells]
        for row in rows:
            row["world"] = world
            rel = abs(row["realized_sigma_b2"] / row["sigma_b2"] - 1.0)
            band = ENERGY_BAND_SIGMAS * math.sqrt(
                2.0 * ((1.0 - row["eta"]) ** 2 / m.K_LATENT
                       + row["eta"] ** 2 / K_TAU) / N_AUTHORS)
            g0["sigma_b2_rel_dev_max"] = max(g0["sigma_b2_rel_dev_max"], rel)
            g0["sigma_b2_band_violations"] = g0.get("sigma_b2_band_violations", 0) + int(
                rel > band)
            g0.setdefault("sigma_b2_per_cell", {})[row["cell"]] = {
                "realized": row["realized_sigma_b2"], "designed": row["sigma_b2"],
                "rel_dev": rel, "design_band": band, "inside": bool(rel <= band)}
            g0["eta_dev_abs_max"] = max(
                g0["eta_dev_abs_max"], abs(row["realized_eta"] - row["eta"]))
            g0["delta_latent_dev_abs_max"] = max(
                g0["delta_latent_dev_abs_max"],
                max(abs(row["realized_delta_latent_min"] - row["delta"]),
                    abs(row["realized_delta_latent_max"] - row["delta"])))
        pilot_rows.extend(rows)
        g0["per_world"].append({"world": world, "world_seed": wseed,
                                "recon_residual": recon})
    pilot = pd.DataFrame(pilot_rows)
    pilot.to_csv(OUT / "part0_pilot_cells.csv", index=False)
    st["pilot"] = time.time() - t
    g0["criterion"] = (
        "reconstruction residual <= 1e-12 AND the eta-mixture realized energy inside "
        "its DESIGN-DERIVED 4-sigma sampling band "
        "4 sqrt(2[(1-eta)^2/m + eta^2/k_tau]/n) -- 0.0361 at eta=0 rising to 0.1443 at "
        "eta=1, because the aligned component has only k_tau=3 effective dimensions "
        "(L2's flat 3% constant was a realized-luck bar, defect-class #35) -- AND "
        "|realized eta - designed| <= 0.03 AND all six realized latent "
        "separations equal Delta to <= 1e-9 AND every L2 anchor re-derived "
        "BIT-EXACTLY (pooled same-data bias, conditioning ratio from k2a's own AR "
        "algebra, B_hat_cal band, and two full L2 C-cells re-measured through L2's "
        "own path on L2's own worlds)")
    g0["pass"] = bool(g0["recon_residual_max"] <= 1e-12
                      and g0.get("sigma_b2_band_violations", 0) == 0
                      and g0["eta_dev_abs_max"] <= 0.03
                      and g0["delta_latent_dev_abs_max"] <= 1e-9
                      and anchors["all_bit_exact"])
    gates["G0N"] = g0

    # ---- G1N: rules 10 + 3 + 17 (non-degeneracy, liveness, REALIZABILITY) -----
    pmean = pilot.groupby("cell", sort=False).agg(
        {"eta_hat_P": "mean", "etaw_oracle_P": "mean", "eta_hat_T": "mean",
         "eta_hat_angle_P": "mean", "ari_primary": "mean", "ari_fit_half": "mean",
         "xf_dev": "mean", "or_dev": "mean", "whitener_condition": "mean",
         "whitener_eig_min_kept": "mean", "eta": "first", "energy": "first"}).reset_index()
    pv_eta = pilot.pivot_table(index="world", columns="cell", values="eta_hat_P")
    pv_eta_or = pilot.pivot_table(index="world", columns="cell", values="etaw_oracle_P")
    df_pilot = len(PILOT_WORLDS) - 1
    tq = float(student_t.ppf(0.975, df_pilot))

    def hw(sd: float) -> float:
        return tq * sd / math.sqrt(WORLDS_PER_CELL)

    hw_primary = {c: hw(float(pv_eta[c].std(ddof=1))) for c in pv_eta.columns}
    hw_oracle = {c: hw(float(pv_eta_or[c].std(ddof=1))) for c in pv_eta_or.columns}
    route_primary_ok = bool(max(hw_primary.values()) < G1N_CI_HALFWIDTH_BAR)
    route_oracle_ok = bool(max(hw_oracle.values()) < G1N_CI_HALFWIDTH_BAR)
    if route_primary_ok:
        eta_route, route_note = "primary_state_innovation_whitener", "no fallback fired"
    elif route_oracle_ok:
        eta_route = "fallback_pure_oracle_whitener"
        route_note = ("rule-17 pre-declared fallback FIRED: the split-half whitener's "
                      "pilot CI half-width exceeded 0.3 in at least one cell, so the "
                      "PURE-ORACLE whitener variant of the same bulk-excess estimator "
                      "is promoted to PRIMARY and disclosed")
    else:
        eta_route = "dropped"
        route_note = ("rule-17 pre-declared fallback EXHAUSTED: both bulk-excess routes "
                      "exceed the 0.3 half-width bar; X-1 and X-2 are UNREALIZABLE")
    g1.update({
        "min_rms_drop_type": float(min(r["rms_drop_type"] for r in g1["per_world"])),
        "min_rms_drop_identity": float(min(r["rms_drop_identity"] for r in g1["per_world"])),
        "min_rms_eta0_vs_eta1": float(min(r["rms_eta0_vs_eta1"] for r in g1["per_world"])),
        "c_int_minus_c_cont": g1["per_world"][0]["c_int_minus_c_cont"],
        "pilot_eta_hat_P": {r["cell"]: float(r["eta_hat_P"]) for _, r in pmean.iterrows()},
        "pilot_eta_hat_T": {r["cell"]: float(r["eta_hat_T"]) for _, r in pmean.iterrows()},
        "pilot_orw_eta_hat_P": {r["cell"]: float(r["etaw_oracle_P"])
                                for _, r in pmean.iterrows()},
        "pilot_eta_hat_angle_P": {r["cell"]: float(r["eta_hat_angle_P"])
                                  for _, r in pmean.iterrows()},
        "pilot_ari_fit_half": {r["cell"]: float(r["ari_fit_half"])
                               for _, r in pmean.iterrows()},
        "pilot_xf_dev": {r["cell"]: float(r["xf_dev"]) for _, r in pmean.iterrows()},
        "pilot_or_dev": {r["cell"]: float(r["or_dev"]) for _, r in pmean.iterrows()},
        "eta_hat_ci_halfwidth_primary": hw_primary,
        "eta_hat_ci_halfwidth_oracle_whitener": hw_oracle,
        "ci_halfwidth_bar": G1N_CI_HALFWIDTH_BAR,
        "route_primary_realizable": route_primary_ok,
        "route_oracle_whitener_realizable": route_oracle_ok,
        "eta_route": eta_route, "fallback_note": route_note,
        "whitener_condition_max": float(pmean["whitener_condition"].max()),
        "whitener_eig_min_kept_min": float(pmean["whitener_eig_min_kept"].min()),
        "fallback_rule": (
            "rule 17, EXACTLY ONE step, pre-declared BEFORE any pilot number: if the "
            "PRIMARY bulk-excess route (the panel-exact state-INNOVATION whitener, "
            "PN-4) has a pilot eta_hat CI half-width >= 0.3 in ANY of the ten cells, "
            "that route is DROPPED and the PURE-ORACLE whitener (the generator's own "
            "M M^T) variant of the identical estimator is promoted to PRIMARY and "
            "disclosed; if that route also fails the bar, both are dropped and "
            "X-1/X-2 are scored UNREALIZABLE, which routes to P2N by the total "
            "routing function.  The STRICTLY DATA-ONLY whitener (B_hat_mat) and the "
            "NO-WHITENING reading (derivation 3 taken literally) are reported in "
            "every cell but are companions, never the PRIMARY: the 3.2 s "
            "prediction-stream feasibility probe recorded in the report's anomaly "
            "list showed the data-only whitener's eigenvalue spread (condition ratio "
            "16.07 against the true 2.3884, from the 1/(c_int - c_cont) = 10.3x "
            "amplification of a d/n = 0.125 covariance) and that decision was taken "
            "BEFORE any pilot or main world of this leg was generated."),
        "criterion": (
            "rule 10: the type channel, the identity channel and the eta mixture all "
            "change the card panel (RMS > 1e-6), and the two canonical occasion "
            "splits have a non-zero AR contrast (the taxometer's denominator).  "
            "rule 3: the whitener keeps m = 48 strictly positive eigenvalues in every "
            "cell.  rule 17: the eta_hat route is REALIZABLE at the registered "
            "0.3 CI half-width bar, or the pre-declared fallback fires."),
    })
    g1["pass"] = bool(g1["min_rms_drop_type"] > 1e-6
                      and g1["min_rms_drop_identity"] > 1e-6
                      and g1["min_rms_eta0_vs_eta1"] > 1e-6
                      and abs(g1["c_int_minus_c_cont"]) > 1e-9
                      and g1["whitener_eig_min_kept_min"] > 0.0)
    gates["G1N"] = g1

    # ---- G2N: standing rules 18 + 20 -----------------------------------------
    t = time.time()
    js = joint_satisfiability_l3()
    pd.DataFrame(js.pop("grid_table")).to_csv(OUT / "part0_joint_grid.csv", index=False)
    g2: dict[str, Any] = {"rule18_rule20_joint": js,
                          "rule20_stop": bool(js["rule20_stop"]),
                          "rule20_empty_leans": js["rule20_empty_leans"],
                          "criterion": (
                              "rule 18: every lean's clauses are reduced to SETS OF "
                              "DESIGN POINTS over the (Delta, sigma_b^2) plane on the "
                              "prediction stream and INTERSECTED within each lean; "
                              "rule 20: ANY empty intersection STOPS the leg before "
                              "the arms as a registration defect (routing P1N)."),
                          "pass": True}
    gates["G2N"] = g2
    st["joint"] = time.time() - t

    # ---- G3N: rule-19 fidelity table + Part-0 predictions + MDEs + rule 13 ----
    t = time.time()
    pred_rows = []
    for name, sb2 in lg2.C_ENERGIES:
        for eta in lg2.ETA_LEVELS:
            reps = [pred_cell(lg2.L1_DELTA, sb2, eta, r) for r in range(JS_REPS)]
            rec: dict[str, Any] = {"cell": c_cell_id(name, eta), "source": "registered",
                                   "energy": name, "eta": eta, "delta": lg2.L1_DELTA,
                                   "sigma_b2": sb2}
            for key in reps[0]:
                arr = np.array([r[key] for r in reps], dtype=float)
                rec[key] = float(arr.mean())
                rec[f"{key}_sd"] = float(arr.std(ddof=1))
            pred_rows.append(rec)
    pred = pd.DataFrame(pred_rows)
    x_pred = 1.0 - pred["ari_fit_half"].to_numpy(float)
    y_pred = pred["xf_dev"].to_numpy(float)
    beta_pred, r2_pred = propagation_fit(x_pred, y_pred)
    beta_sqrt, r2_sqrt = propagation_fit(np.sqrt(x_pred), y_pred)
    beta_acc, r2_acc = propagation_fit(1.0 - pred["acc_fit_half"].to_numpy(float), y_pred)
    pred.to_csv(OUT / "part0_predictions.csv", index=False)
    fid = fidelity_table(pred)
    g3: dict[str, Any] = {
        "pass": True, "artifact": "part0_predictions.csv", "fidelity_table": fid,
        "prediction_stream_reps": JS_REPS,
        "propagation_prediction": {
            "linear_intercept": float(beta_pred[0]), "linear_slope": float(beta_pred[1]),
            "linear_r2": float(r2_pred),
            "sqrt_intercept": float(beta_sqrt[0]), "sqrt_slope": float(beta_sqrt[1]),
            "sqrt_r2": float(r2_sqrt),
            "acc_intercept": float(beta_acc[0]), "acc_slope": float(beta_acc[1]),
            "acc_r2": float(r2_acc),
            "oracle_anchor": float(pred["or_dev"].mean())},
        "l2_persisted_propagation_prediction": {},
    }
    # the same three fits on L2's own persisted C-cells (a prior-leg prediction)
    l2c = persisted[persisted["kind"] == "C"]
    xl = 1.0 - l2c["ari_fit_half"].to_numpy(float)
    yl = (l2c["xf_S_id"] - l2c["xf_target"]).to_numpy(float)
    for tag, xv in (("linear", xl), ("sqrt", np.sqrt(xl))):
        bb, rr = propagation_fit(xv, yl)
        g3["l2_persisted_propagation_prediction"][tag] = {
            "intercept": float(bb[0]), "slope": float(bb[1]), "r2": float(rr)}
    g3["l2_persisted_propagation_prediction"]["oracle_anchor"] = float(
        (l2c["or_S_id"] - l2c["or_target"]).mean())

    # 4-world pilot MDEs at the main grain, with directions (rule 11)
    clauses = []

    def mde(sd: float, n: int) -> float:
        return (float(student_t.ppf(0.975, df_pilot))
                + float(student_t.ppf(0.80, df_pilot))) * sd / math.sqrt(n)

    for key, label, direction in (
            ("eta_hat_P", "eta_hat (PRIMARY)", "two-sided (poles: CI must CONTAIN 0/1)"),
            ("etaw_oracle_P", "eta_hat (oracle whitener)", "two-sided"),
            ("eta_hat_angle_P", "eta_hat (alignment angle)", "two-sided, reported only"),
            ("xf_dev", "cross-fitted audit deviation",
             "two-sided (corrected CI must CONTAIN 0)"),
            ("or_dev", "true-partition audit deviation (the anchor)", "two-sided"),
            ("ari_fit_half", "ARI of the audit's partition", "two-sided, regressor")):
        pv = pilot.pivot_table(index="world", columns="cell", values=key)
        for cid in pv.columns:
            sd = float(pv[cid].std(ddof=1))
            clauses.append({"clause": f"{label} {cid}", "pilot_mean": float(pv[cid].mean()),
                            "pilot_sd_world": sd, "mde_main": mde(sd, WORLDS_PER_CELL),
                            "direction": direction})
    pv_sd = pilot.pivot_table(index="world", columns="cell", values="sd_dev")
    pv_xf = pilot.pivot_table(index="world", columns="cell", values="xf_dev")
    bias = (pv_sd - pv_xf).mean(axis=1)
    clauses.append({"clause": "pooled same-data minus cross-fitted deviation (X-4)",
                    "pilot_mean": float(bias.mean()),
                    "pilot_sd_world": float(bias.std(ddof=1)),
                    "mde_main": mde(float(bias.std(ddof=1)), WORLDS_PER_CELL),
                    "direction": "one-sided upper (< 0, the optimistic side)"})
    g3["clauses"] = clauses
    g3["rule13_spec"] = ("B=2000 at seed=master_seed, with a >=10xB (20000) recheck at "
                         "any clause whose boundary lies within 2 Monte-Carlo endpoint "
                         "sds of the estimate")
    g3["rule11_directions"] = {
        "X-1": "ordering predicate (Spearman) + two-sided pole CIs containing 0 and 1",
        "X-2": "two-sided absolute-error count against a 0.125 bar",
        "X-3": "one-sided lower on R^2; two-sided containment of the anchor by the "
               "intercept CI; two-sided containment of 0 by the corrected deviation CI",
        "X-4": "one-sided upper (pooled corrected bias < 0)",
    }
    g3["pass"] = bool(clauses and all(np.isfinite(c["mde_main"]) for c in clauses))
    gates["G3N"] = g3
    st["predictions"] = time.time() - t

    # ---- G4N: hygiene + rule 16 + rule 14 -------------------------------------
    layer_a, layer_b, enum_audit = build_enumeration()
    layer_a.to_csv(OUT / "part0_enumeration_leans.csv", index=False)
    layer_b.to_csv(OUT / "part0_enumeration_routing.csv", index=False)
    gates["G4N"] = {
        "pass": bool(enum_audit["layer_a_no_gap_no_overlap"]
                     and enum_audit["layer_b_no_gap_no_overlap"]),
        "round_trip_parsing_everywhere": True, "float_precision": "round_trip",
        "enumeration": enum_audit,
        "rule14_self_check": (
            "CARD SPACE ONLY.  X-1 and X-2 compare eta_hat to eta -- the same "
            "dimensionless mixture fraction on the same [0,1] scale.  X-3 regresses a "
            "normalized variance-SHARE deviation on a dimensionless partition-"
            "agreement deficit and compares the corrected SHARE to a designed SHARE.  "
            "X-4 compares a share difference to zero.  No gate and no lean crosses "
            "scales or instruments, so rule 14 has nothing to bind."),
        "rule12_source_objects": {
            "the eta-mixture typed world, the cross-fitting scheme, the CALIBRATED "
            "meter and the floor curve":
                "scripts/run_suica_m4_l2_threshold_continuum.py, imported as a module "
                "and called UNMODIFIED (type_geometry_l2, latent_identity_l2, "
                "typed_trait_l2, build_typed_world_l2, occasion_scheme, cards_for_cell, "
                "audit_meter_l2, estimated_s, subspace_overlap, "
                "predicted_boundary_error_l2, projection_gain; measure_cell_world / "
                "all_cells / world_seed_for for the G0N anchor)",
            "the two grouping instruments and the metrics":
                "scripts/run_suica_m4_l1_typed_world.py, called UNMODIFIED "
                "(kmeans_lloyd, spectral_labels, adjusted_rand_index, "
                "hungarian_accuracy, boundary_error_rate, latent_type_vectors, "
                "card_space_type_basis, centred_with_trait, _norm_dot, group_centre)",
            "expressive world / channels / card / splits / AR algebra":
                "scripts/run_suica_m4_k2a_expressive_world.py, called UNMODIFIED "
                "(build_world via l2, arm_weights('zero'), centered_channels, card, "
                "splits, ar_mean_var/ar_set_var/ar_cross_cov, response_panel, "
                "read_csv_rt, ci_of, mc_sd_of_endpoint)",
            "NEW in this leg": "this script -- full_panel_halves, cards_for_cell_l3, "
                               "split_half_persistent, whitener_from_state, "
                               "oracle_whitener, _eta_from_whitened, alignment_angle, "
                               "taxometer, propagation_fit, pred_panel_l3, pred_meter, "
                               "pred_cell, joint_satisfiability_l3, fidelity_table",
        },
    }
    gates["part0_all_pass"] = bool(gates["G0N"]["pass"] and gates["G1N"]["pass"]
                                   and gates["G2N"]["pass"] and gates["G3N"]["pass"]
                                   and gates["G4N"]["pass"])
    gates["rule20_stop"] = bool(js["rule20_stop"])
    gates["eta_route"] = eta_route
    gates["stage_seconds"] = st
    gates["stage_seconds"]["part0_total"] = time.time() - t0
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n",
                                    encoding="utf-8")
    write_part0_tables(gates, pred, pilot)
    write_manifest({"part0": time.time() - t0}, {})
    print(json.dumps({
        "stage": "part0", "seconds": round(time.time() - t0, 3),
        "part0_all_pass": gates["part0_all_pass"],
        "G0N": gates["G0N"]["pass"], "G1N": gates["G1N"]["pass"],
        "G2N": gates["G2N"]["pass"], "G3N": gates["G3N"]["pass"],
        "G4N": gates["G4N"]["pass"],
        "anchors_bit_exact": anchors["all_bit_exact"],
        "rule20_stop": gates["rule20_stop"],
        "rule20_empty_leans": js["rule20_empty_leans"],
        "lean_condition_sets": {k: v["n_points"] for k, v in js["lean_sets"].items()},
        "eta_route": eta_route,
        "pilot_eta_hat_P": g1["pilot_eta_hat_P"],
        "eta_hat_ci_halfwidth_primary": hw_primary,
        "propagation_prediction": g3["propagation_prediction"],
        "stage_seconds": st,
    }, indent=2, default=str))


def write_part0_tables(gates: dict[str, Any], pred: pd.DataFrame,
                       pilot: pd.DataFrame) -> None:
    lines: list[str] = []
    lines.append("### G3N rule-19 fidelity table\n")
    lines.append("| lean | theorem quantity | predicted value / curve (derivation) | "
                 "the bar | why the bar is on that quantity |")
    lines.append("|---|---|---|---|---|")
    for r in gates["G3N"]["fidelity_table"]:
        lines.append("| **{lean}** | {theorem_quantity} | {predicted} | {bar} | "
                     "{why_this_quantity} |".format(
                         **{k: v.replace("\n", " ") for k, v in r.items()}))
    lines.append("\n### G2N rule-18 + rule-20 JOINT satisfiability "
                 "(clause -> set of design points)\n")
    js = gates["G2N"]["rule18_rule20_joint"]
    lines.append(f"Grid: Delta factors {js['delta_factors']} x energy factors "
                 f"{js['energy_factors']} ({len(js['grid_points'])} points, "
                 f"{js['reps']} prediction replicates each); the registered design "
                 f"point is `{js['registered_point']}`.\n")
    lines.append("| clause | # points where it holds | points |")
    lines.append("|---|---:|---|")
    for k, v in js["clause_sets"].items():
        lines.append(f"| {k} | {len(v)} | {', '.join(v) if v else '**EMPTY**'} |")
    lines.append("\n| lean | clauses | JOINT condition-set | registered point inside? |")
    lines.append("|---|---:|---|---|")
    for k, v in js["lean_sets"].items():
        lines.append(f"| **{k}** | {len(v['clauses'])} | "
                     f"{', '.join(v['points']) if v['points'] else '**EMPTY (rule 20)**'} "
                     f"| {v['registered_point_inside']} |")
    lines.append(f"\n**rule-20 verdict: "
                 f"{'STOP -- ' + ', '.join(js['rule20_empty_leans']) if js['rule20_stop'] else 'NO STOP (every lean has a non-empty condition-set)'}**\n")
    lines.append("\n### Part-0 per-cell predictions (prediction stream, before any world)\n")
    lines.append("| cell | eta | eta_hat (P) | eta_hat (T) | eta_hat (oracle wht) | "
                 "eta_hat (angle) | ARI fit-half | xf dev | or dev |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for _, r in pred.iterrows():
        lines.append(f"| `{r['cell']}` | {r['eta']:g} | {r['eta_hat_P']:.6f} | "
                     f"{r['eta_hat_T']:.6f} | {r['etaw_oracle_P']:.6f} | "
                     f"{r['eta_hat_angle_P']:.6f} | {r['ari_fit_half']:.6f} | "
                     f"{r['xf_dev']:.6f} | {r['or_dev']:.6f} |")
    lines.append("\n### G1N pilot eta_hat and the rule-17 realizability check\n")
    lines.append("| cell | pilot eta_hat (P) | CI half-width (n=8) | "
                 "oracle-whitener half-width | pilot eta_hat (T) | pilot angle |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    g1 = gates["G1N"]
    for cid in g1["pilot_eta_hat_P"]:
        lines.append(f"| `{cid}` | {g1['pilot_eta_hat_P'][cid]:.6f} | "
                     f"{g1['eta_hat_ci_halfwidth_primary'][cid]:.6f} | "
                     f"{g1['eta_hat_ci_halfwidth_oracle_whitener'][cid]:.6f} | "
                     f"{g1['pilot_eta_hat_T'][cid]:.6f} | "
                     f"{g1['pilot_eta_hat_angle_P'][cid]:.6f} |")
    lines.append(f"\nBar: CI half-width < {g1['ci_halfwidth_bar']}.  Route selected: "
                 f"**{g1['eta_route']}** ({g1['fallback_note']}).\n")
    lines.append("\n### G3N pilot MDEs (4 pilot worlds -> main design n=8)\n")
    lines.append("| clause | pilot mean | pilot sd (world) | MDE at n=8 | direction |")
    lines.append("|---|---:|---:|---:|---|")
    for c in gates["G3N"]["clauses"]:
        lines.append(f"| {c['clause']} | {c['pilot_mean']:.10f} | "
                     f"{c['pilot_sd_world']:.10f} | {c['mde_main']:.10f} | "
                     f"{c['direction']} |")
    lines.append("\n### G0N L2 anchors\n")
    a = gates["G0N"]["l2_anchors"]
    lines.append("| anchor | registration | re-derived | bit-exact |")
    lines.append("|---|---|---|---|")
    lines.append(f"| pooled same-data bias | {a['pooled_samedata_bias']['registration']!r} "
                 f"| {a['pooled_samedata_bias']['recomputed']!r} | "
                 f"{a['pooled_samedata_bias']['bit_exact']} |")
    lines.append(f"| conditioning ratio | {a['conditioning_ratio']['registration']!r} | "
                 f"{a['conditioning_ratio']['recomputed']!r} | "
                 f"{a['conditioning_ratio']['bit_exact']} |")
    lines.append(f"| B_hat_cal band | {a['B_hat_cal_band']['registration_band']} | "
                 f"[{a['B_hat_cal_band']['min']!r}, {a['B_hat_cal_band']['max']!r}] | "
                 f"{a['B_hat_cal_band']['inside_band']} |")
    for cid, cols in a["l2_cells_rederived"].items():
        for col, v in cols.items():
            lines.append(f"| L2 `{cid}` `{col}` | {v['persisted_mean']!r} | "
                         f"{v['rederived_mean']!r} | {v['bit_exact_rows']} |")
    (OUT / "part0_tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Stage: arms

def require_part0() -> dict[str, Any]:
    path = OUT / "gates.json"
    if not path.exists():
        raise SystemExit("REFUSED: Part 0 has not run (results/.../gates.json missing).")
    gates = json.loads(path.read_text(encoding="utf-8"))
    if gates.get("rule20_stop"):
        raise SystemExit("REFUSED (standing rule 20): a lean's JOINT condition-set is "
                         "empty; the leg STOPS before the arms as a registration "
                         "defect -> P1N.")
    if not gates.get("part0_all_pass"):
        raise SystemExit("REFUSED: a Part-0 gate failed; no arms may run.")
    if not REPORT.exists():
        raise SystemExit("REFUSED: the Part-0 report has not been written to disk.")
    return gates


def run_arms(args: argparse.Namespace) -> None:
    require_part0()
    t0 = time.time()
    wanted = set(args.cells.split(",")) if args.cells else None
    cells = [c for c in all_cells() if wanted is None or c["cell"] in wanted]
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
    """PN-8: ONE paired world-block resample, applied identically to EVERY cell
    (the cells share their worlds bit-for-bit)."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, n_blocks, size=(b_draws, n_blocks))


def _spearman(a: list[float], b: list[float]) -> float:
    ra = np.argsort(np.argsort(np.asarray(a, dtype=float))).astype(float)
    rb = np.argsort(np.argsort(np.asarray(b, dtype=float))).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    den = math.sqrt(float((ra ** 2).sum()) * float((rb ** 2).sum()))
    return float((ra * rb).sum() / den) if den > 0 else 0.0


def run_finalize(args: argparse.Namespace) -> None:
    gates = require_part0()
    m, lg2 = k2a(), l2()
    t0 = time.time()
    cells = all_cells()
    ccells = [c["cell"] for c in cells]
    eta_route = gates.get("eta_route", "primary_split_half_whitener")
    eta_key = "etaw_oracle_P" if eta_route == "fallback_pure_oracle_whitener" else "eta_hat_P"
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

    KEYS = ("eta_hat_P", "eta_hat_S", "eta_hat_T", "etaw_oracle_P", "etaw_oracle_S",
            "etaw_oracle_T", "etaw_split_P", "etaw_split_T", "etaw_flat_P",
            "etaw_flat_T", "etaw_marg_P", "eta_hat_angle_P", "eta_hat_angle_T",
            "angle_overlap_P",
            "eta_hat_withinbulk_P", "kappa_bulk_pooled_P", "sigma_total_within_P",
            "whitener_condition", "whitener_condition_split", "whitener_eig_min_kept",
            "ari_primary", "ari_spectral", "acc_primary", "ari_fit_half",
            "acc_fit_half", "ari_fit_half_spectral", "ari_same_half", "acc_same_half",
            "xf_S_id", "xf_target", "xf_dev", "sd_S_id", "sd_target", "sd_dev",
            "or_S_id", "or_target", "or_dev", "xs_S_id", "xs_target", "xs_dev",
            "xf_B_hat_cal", "or_B_hat_cal", "boundary_err_true_card",
            "floor_pred_identity", "realized_eta", "realized_sigma_b2")
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
        row["eta_hat_err"] = row[eta_key] - spec["eta"]
        row["eta_hat_abs_err"] = abs(row["eta_hat_err"])
        row["eta_within_tol"] = bool(row["eta_hat_abs_err"] <= X2_TOL)
        row["samedata_bias_raw"] = float(
            (vals(cid, "sd_dev") - vals(cid, "xf_dev")).mean())
        rows.append(row)
    cdf = pd.DataFrame(rows)
    by = {r["cell"]: r for r in rows}

    # ---------------- the PROPAGATION FIT (X-3), refit inside every bootstrap --
    def stack(key: str) -> np.ndarray:
        return np.stack([vals(cid, key) for cid in ccells])            # (10, 8)

    x_all = 1.0 - stack("ari_fit_half")
    y_all = stack("xf_dev")
    x_sd = 1.0 - stack("ari_same_half")
    y_sd = stack("sd_dev")
    y_or = stack("or_dev")
    x_acc = 1.0 - stack("acc_fit_half")

    def fit_on(index_row: np.ndarray, xm: np.ndarray, ym: np.ndarray,
               transform: str) -> tuple[np.ndarray, float]:
        """PN-6: ONE ROW PER CELL (the registration's 'across cells'); each row
        is that cell's mean over the resampled world block."""
        xv = xm[:, index_row].mean(axis=1)
        yv = ym[:, index_row].mean(axis=1)
        if transform == "sqrt":
            xv = np.sqrt(np.maximum(xv, 0.0))
        return propagation_fit(xv, yv)

    beta_pt, r2_pt = fit_on(np.arange(WORLDS_PER_CELL), x_all, y_all, "linear")
    beta_sq, r2_sq = fit_on(np.arange(WORLDS_PER_CELL), x_all, y_all, "sqrt")
    beta_ac, r2_ac = propagation_fit(x_acc.mean(axis=1), y_all.mean(axis=1))
    r2_rowgrain = propagation_fit(x_all.reshape(-1), y_all.reshape(-1))[1]
    anchor_pt = float(y_or.mean())

    boot_int = np.empty(B_BOOT); boot_slope = np.empty(B_BOOT); boot_r2 = np.empty(B_BOOT)
    boot_anchor = np.empty(B_BOOT)
    corr_xf = np.empty((B_BOOT, len(ccells))); corr_sd = np.empty((B_BOOT, len(ccells)))
    for bi in range(B_BOOT):
        sel = idx[bi]
        bb, rr = fit_on(sel, x_all, y_all, "linear")
        boot_int[bi], boot_slope[bi], boot_r2[bi] = bb[0], bb[1], rr
        boot_anchor[bi] = float(y_or[:, sel].mean())
        corr_xf[bi] = y_all[:, sel].mean(axis=1) - (
            bb[0] + bb[1] * x_all[:, sel].mean(axis=1))
        corr_sd[bi] = y_sd[:, sel].mean(axis=1) - (
            bb[0] + bb[1] * x_sd[:, sel].mean(axis=1))
    boot_int_hi = np.empty(B_BOOT_HIGH); corr_xf_hi = np.empty((B_BOOT_HIGH, len(ccells)))
    corr_sd_hi = np.empty((B_BOOT_HIGH, len(ccells)))
    for bi in range(B_BOOT_HIGH):
        sel = idx_hi[bi]
        bb, _ = fit_on(sel, x_all, y_all, "linear")
        boot_int_hi[bi] = bb[0]
        corr_xf_hi[bi] = y_all[:, sel].mean(axis=1) - (
            bb[0] + bb[1] * x_all[:, sel].mean(axis=1))
        corr_sd_hi[bi] = y_sd[:, sel].mean(axis=1) - (
            bb[0] + bb[1] * x_sd[:, sel].mean(axis=1))
    int_lo, int_hi = m.ci_of(boot_int)
    anchor_in_ci = bool(int_lo <= anchor_pt <= int_hi)
    corrected_point = (y_all.mean(axis=1) - (beta_pt[0] + beta_pt[1] * x_all.mean(axis=1)))
    track = {}
    for j, cid in enumerate(ccells):
        lo, hi = m.ci_of(corr_xf[:, j])
        by[cid]["corrected_dev"] = float(corr_xf[:, j].mean())
        by[cid]["corrected_dev_lo"], by[cid]["corrected_dev_hi"] = lo, hi
        track[cid] = bool(lo <= 0.0 <= hi)
    bias_corr = (corr_sd - corr_xf).mean(axis=1)
    bias_corr_hi = (corr_sd_hi - corr_xf_hi).mean(axis=1)
    bc_lo, bc_hi = m.ci_of(bias_corr)
    bias_raw = np.mean([boot(cid, "sd_dev", idx) - boot(cid, "xf_dev", idx)
                        for cid in ccells], axis=0)
    br_lo, br_hi = m.ci_of(bias_raw)

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

    # ---------------- X-1 ------------------------------------------------------
    unrealizable = (eta_route == "dropped")
    mono = {}
    for name, _ in lg2.C_ENERGIES:
        seq = [by[c_cell_id(name, e)][eta_key] for e in lg2.ETA_LEVELS]
        mono[name] = {"eta_hat_sequence": seq,
                      "spearman": _spearman(list(lg2.ETA_LEVELS), seq),
                      "strictly_increasing": bool(all(a < b for a, b in
                                                      zip(seq, seq[1:], strict=False)))}
    poles = {}
    for name, _ in lg2.C_ENERGIES:
        for e, target in ((0.0, 0.0), (1.0, 1.0)):
            cid = c_cell_id(name, e)
            lo, hi = by[cid][f"{eta_key}_lo"], by[cid][f"{eta_key}_hi"]
            ok = bool(lo <= target <= hi)
            poles[cid] = {"target": target, "eta_hat": by[cid][eta_key],
                          "lo": lo, "hi": hi, "contains": ok}
            rule13(cid, f"eta_hat CI contains {target:g}", boot(cid, eta_key, idx),
                   boot(cid, eta_key, idx_hi), target, "contains", ok)
    x1_sub = ("UNREALIZABLE" if unrealizable else
              ("HOLD" if all(v["spearman"] >= X1_SPEARMAN_BAR for v in mono.values())
               else "MISS"),
              "UNREALIZABLE" if unrealizable else
              ("HOLD" if all(v["contains"] for v in poles.values()) else "MISS"))
    x1 = {"prior": 0.70, "shadows": "eta itself", "eta_route": eta_route,
          "estimator_key": eta_key, "monotone": mono, "poles": poles,
          "n_poles_calibrated": int(sum(v["contains"] for v in poles.values())),
          "second_reading_alignment_angle": {
              cid: {"eta_hat_angle": by[cid]["eta_hat_angle_P"],
                    "overlap": by[cid]["angle_overlap_P"]} for cid in ccells},
          "second_reading_angle_monotone": {
              name: _spearman(list(lg2.ETA_LEVELS),
                              [by[c_cell_id(name, e)]["eta_hat_angle_P"]
                               for e in lg2.ETA_LEVELS])
              for name, _ in lg2.C_ENERGIES},
          "second_reading_spectral_grouping": {
              name: _spearman(list(lg2.ETA_LEVELS),
                              [by[c_cell_id(name, e)]["eta_hat_S"]
                               for e in lg2.ETA_LEVELS])
              for name, _ in lg2.C_ENERGIES},
          "second_reading_true_partition": {
              name: _spearman(list(lg2.ETA_LEVELS),
                              [by[c_cell_id(name, e)]["eta_hat_T"]
                               for e in lg2.ETA_LEVELS])
              for name, _ in lg2.C_ENERGIES},
          "subclause_states": list(x1_sub), "state": lean_from_subclauses(x1_sub)}

    # ---------------- X-2 ------------------------------------------------------
    within = {cid: bool(by[cid]["eta_within_tol"]) for cid in ccells}
    x2_sub = ("UNREALIZABLE" if unrealizable else
              ("HOLD" if sum(within.values()) >= X2_MIN_CELLS else "MISS"),)
    x2 = {"prior": 0.55, "shadows": "eta", "tolerance": X2_TOL,
          "threshold": X2_MIN_CELLS,
          "per_cell": {cid: {"eta": by[cid]["eta"], "eta_hat": by[cid][eta_key],
                             "lo": by[cid][f"{eta_key}_lo"],
                             "hi": by[cid][f"{eta_key}_hi"],
                             "abs_err": by[cid]["eta_hat_abs_err"],
                             "within": within[cid],
                             "eta_hat_true_partition": by[cid]["eta_hat_T"],
                             "eta_hat_oracle_whitener": by[cid]["etaw_oracle_P"],
                             "eta_hat_spectral": by[cid]["eta_hat_S"]}
                       for cid in ccells},
          "n_within": int(sum(within.values())),
          "second_reading_true_partition_n_within": int(sum(
              abs(by[cid]["eta_hat_T"] - by[cid]["eta"]) <= X2_TOL for cid in ccells)),
          "second_reading_oracle_whitener_n_within": int(sum(
              abs(by[cid]["etaw_oracle_P"] - by[cid]["eta"]) <= X2_TOL for cid in ccells)),
          "subclause_states": list(x2_sub), "state": lean_from_subclauses(x2_sub)}

    # ---------------- X-3 ------------------------------------------------------
    for j, cid in enumerate(ccells):
        rule13(cid, "corrected meter CI contains 0", corr_xf[:, j], corr_xf_hi[:, j],
               0.0, "contains", track[cid])
    rule13("pooled", "oracle anchor inside the intercept CI", boot_int, boot_int_hi,
           anchor_pt, "contains", anchor_in_ci)
    x3_sub = ("HOLD" if r2_pt >= X3_R2_BAR else "MISS",
              "HOLD" if anchor_in_ci else "MISS",
              "HOLD" if sum(track.values()) >= X3_MIN_TRACK else "MISS")
    x3 = {"prior": 0.60, "shadows": "the deviation-(1-ARI) relation",
          "fit": {"form": "OLS dev = a + b (1 - ARI), ONE ROW PER CELL (world-means), n=10, refit inside every paired world-block bootstrap replicate",
                  "intercept": float(beta_pt[0]), "slope": float(beta_pt[1]),
                  "r2": float(r2_pt), "r2_bar": X3_R2_BAR,
                  "r2_at_cell_world_row_grain": float(r2_rowgrain),
                  "intercept_lo": int_lo, "intercept_hi": int_hi,
                  "slope_lo": float(np.percentile(boot_slope, 2.5)),
                  "slope_hi": float(np.percentile(boot_slope, 97.5)),
                  "r2_lo": float(np.percentile(boot_r2, 2.5)),
                  "r2_hi": float(np.percentile(boot_r2, 97.5))},
          "oracle_anchor": {"value": anchor_pt,
                            "lo": float(np.percentile(boot_anchor, 2.5)),
                            "hi": float(np.percentile(boot_anchor, 97.5)),
                            "inside_intercept_ci": anchor_in_ci},
          "corrected_tracking": track, "n_tracking": int(sum(track.values())),
          "threshold": X3_MIN_TRACK,
          "per_cell": {cid: {"x_1_minus_ari": float(1.0 - by[cid]["ari_fit_half"]),
                             "dev": by[cid]["xf_dev"],
                             "dev_lo": by[cid]["xf_dev_lo"],
                             "dev_hi": by[cid]["xf_dev_hi"],
                             "fitted": float(beta_pt[0] + beta_pt[1]
                                             * (1.0 - by[cid]["ari_fit_half"])),
                             "corrected": by[cid]["corrected_dev"],
                             "corrected_lo": by[cid]["corrected_dev_lo"],
                             "corrected_hi": by[cid]["corrected_dev_hi"],
                             "tracks": track[cid],
                             "or_dev": by[cid]["or_dev"],
                             "uncorrected_tracks": bool(
                                 by[cid]["xf_dev_lo"] <= 0.0 <= by[cid]["xf_dev_hi"])}
                       for cid in ccells},
          "second_reading_sqrt": {"intercept": float(beta_sq[0]),
                                  "slope": float(beta_sq[1]), "r2": float(r2_sq)},
          "second_reading_misassignment_rate": {"intercept": float(beta_ac[0]),
                                                "slope": float(beta_ac[1]),
                                                "r2": float(r2_ac)},
          "n_uncorrected_tracking": int(sum(
              1 for cid in ccells if by[cid]["xf_dev_lo"] <= 0.0 <= by[cid]["xf_dev_hi"])),
          "subclause_states": list(x3_sub), "state": lean_from_subclauses(x3_sub)}

    # ---------------- X-4 ------------------------------------------------------
    bias_ok = bool(bc_hi < 0.0)
    rule13("pooled", "corrected same-data optimistic bias < 0", bias_corr, bias_corr_hi,
           0.0, "upper_lt", bias_ok)
    x4_sub = ("HOLD" if bias_ok else "MISS",)
    x4 = {"prior": 0.80,
          "shadows": "derivation 4's SIGN, under the corrected meter",
          "pooled_corrected_bias": float(bias_corr.mean()),
          "pooled_corrected_lo": bc_lo, "pooled_corrected_hi": bc_hi,
          "pooled_raw_bias": float(np.mean([by[cid]["samedata_bias_raw"]
                                            for cid in ccells])),
          "pooled_raw_lo": br_lo, "pooled_raw_hi": br_hi,
          "L2_pooled_raw_bias": L2_POOLED_SAMEDATA_BIAS,
          "per_cell": {cid: {"raw_bias": by[cid]["samedata_bias_raw"],
                             "sd_dev": by[cid]["sd_dev"], "xf_dev": by[cid]["xf_dev"],
                             "ari_fit_half": by[cid]["ari_fit_half"],
                             "ari_same_half": by[cid]["ari_same_half"]}
                       for cid in ccells},
          "n_negative_cells": int(sum(1 for cid in ccells
                                      if by[cid]["samedata_bias_raw"] < 0.0)),
          "subclause_states": list(x4_sub), "state": lean_from_subclauses(x4_sub)}

    for cid in ccells:
        by[cid]["corrected_dev_tracks"] = track[cid]
    pd.DataFrame(rows).to_csv(OUT / "cells.csv", index=False)

    states = {"X-1": x1["state"], "X-2": x2["state"],
              "X-3": x3["state"], "X-4": x4["state"]}
    rule20_stop = bool(gates.get("rule20_stop"))
    routing = route(states, rule20_stop)
    boundary = [s for s in stability if s["status"] == "BOUNDARY"]
    slug = {"P1N": "REGISTRATION_DEFECT_EMPTY_SET", "P2N": "TAXOMETER_DEAD",
            "P3N": "METER_RETIRED_TO_TRUE_PARTITIONS",
            "P4N": "INSTRUMENT_SET_COMPLETE"}[routing]
    decision = {
        "leg": "M4-L3", "timestamp_utc": datetime.now(UTC).isoformat(), "banner": BANNER,
        "master_seed": MASTER_SEED, "n_cells": len(cells),
        "worlds_per_cell": WORLDS_PER_CELL, "n_authors_per_world": N_AUTHORS,
        "delta": lg2.L1_DELTA, "eta_levels": list(lg2.ETA_LEVELS),
        "sigma_b2": {k: v for k, v in lg2.C_ENERGIES},
        "rule20_stop": rule20_stop, "eta_route": eta_route,
        "leans": {"X-1": x1, "X-2": x2, "X-3": x3, "X-4": x4},
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
    lg2 = l2()
    path = OUT / "manifest.json"
    prior = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    prior.setdefault("leg", "M4-L3")
    prior.setdefault("banner", BANNER)
    prior.setdefault("script", "scripts/run_suica_m4_l3_taxometer_meter.py")
    prior.setdefault("registration",
                     "docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md M4-L3 (034bf48)")
    prior.setdefault("theory",
                     "docs/SUICA_IDENTITY_THEORY_V1.md appendices P, Q and R")
    prior.setdefault("master_seed", MASTER_SEED)
    prior.setdefault("worlds_per_cell", WORLDS_PER_CELL)
    prior.setdefault("pilot_worlds", list(PILOT_WORLDS))
    prior.setdefault("n_authors", N_AUTHORS)
    prior.setdefault("G", G_GROUPS)
    prior.setdefault("k_tau", K_TAU)
    prior.setdefault("eta_levels", list(lg2.ETA_LEVELS))
    prior.setdefault("sigma_b2_rho55eq", lg2.SB2_RHO55)
    prior.setdefault("sigma_b2_rho35eq", lg2.SB2_RHO35)
    prior.setdefault("delta", lg2.L1_DELTA)
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
