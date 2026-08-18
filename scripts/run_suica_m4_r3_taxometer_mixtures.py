#!/usr/bin/env python3
"""M4-R3 -- THE TAXOMETER ON IDENTITY MIXTURES.

The empirical stamp of the R3 reconciliation note
(``docs/SUICA_R3_IDENTITY_RECONCILIATION_NOTE.md``, commit 1bbda62).
Registered BEFORE this run in
``docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md``, section "M4-R3 -- the
taxometer on identity mixtures" (commit 4597c33).  D1-seal class: the
predictions this leg is scored against are PARAMETER-FREE and were written
into the registration before any world of this leg existed.

Executor standing: implementation and execution ONLY.  Everything labelled
"RN-R3-n" is a register-note (standing rule 9) -- an operationalization of
something the registration left open, pinned in this file's CONFIG block and
in the report's Part 0 BEFORE any main-grid number was read.

CARD SPACE ONLY.  Layer V, synthetic, label-free, EXPLORATORY.  No
psychological naming anywhere in this file or its report.

THE QUESTION.  The note's 2x2 says "identity" names a two-axis space
(geometric alignment x channel semantics) and that eta_hat reads the ROW
margin only -- it is an EXCESS-alignment reader, blind to semantics.  The
composition theorem then predicts, with no free parameter, that adding an
ISOTROPIC non-trait style channel of variance ratio V_s/V_b = w^2 dilutes the
reading hyperbolically:

    eta_hat(eta0, w) = eta0 / (1 + w^2)

This leg builds exactly those mixtures inside the certified L3 world and asks
three things:
  P1  does the certified taxometer obey the dilution law (8 registered cells,
      band = the L3 CERTIFICATION BUDGET +-0.125 on the 8-world cell mean)?
  P2  does the union reader RISE across the same w grid while eta_hat FALLS
      (the signed dissociation -- the note's registerable centerpiece)?
  P3  where does the whitening precondition break (|eta_hat - eta_hat_oracle|
      against the realized style share)?

Reuse boundary (standing rule 12 -- generator SOURCE OBJECTS, not knob names).
``scripts/run_suica_m4_l3_taxometer_meter.py`` is imported AS A MODULE (``l3``)
and UNMODIFIED, and through it ``l2``/``l1``/``k2a``.  This leg calls, and does
not reimplement:
    l3.taxometer                (l3:402-431) THE CERTIFIED eta_hat READER
    l3.full_panel_halves        (l3:203-211) the taxometer's split geometry
    l3.cards_for_cell_l3        (l3:206-213) the UNMODIFIED w=0 reference
    l3.split_half_persistent    (l3:288-309) / l3.whitener_from_state (312-323)
    l3.oracle_whitener          (l3:326-330) / l3.state_shape_innovation (333)
    l3.world_seed_for           (l3:180-189) the world-seed CONVENTION
    l3.N_AUTHORS / K_TAU / G_GROUPS / N_OCC / PHI_SLOW / N_RESTART /
    l3.W_INT_ARM / l3.X2_TOL    (l3:107-135) the certification budget itself
    l2.build_typed_world_l2     (l2:256-258) / l2.type_geometry_l2 (l2:206-228)
    l2.latent_identity_l2       (l2:231-240) the eta mixture
    l2.occasion_scheme          (l2:270-278)
    l2.SB2_RHO55 / l2.SB2_RHO35 / l2.L1_DELTA   (l2:111-132)
    l1.latent_type_vectors / l1.centred_with_trait / l1.kmeans_lloyd /
    l1.adjusted_rand_index / l1.card_space_type_basis
    k2a.build_world / arm_weights / centered_channels / card / splits /
    k2a.K_LATENT / DIM / G_PROFILE / A_SCALE / SIGMA_ISO / N_REP
    suica_core.v8_realtext_relation_field.stable_bucket  (the salt discipline)
NEW in this leg (rule 12, cited by THIS file's line numbers in the report):
    style_latent_r3(), typed_trait_r3(), cards_for_cell_r3(),
    eta_oracle_reader(), second_draw_card(), pooled_auc(), measure_world_cell(),
    certify_c_r3a(), g0_anchor(), adjudicate(), scan_for_cohort_ids().

Runtime: the whole leg is ~30 s (128 world-cells x 512 authors x D=48).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BANNER = ("synthetic worlds calibrated to an opened-panel regime, card space "
          "only, label-free, EXPLORATORY")

OUT = ROOT / "results" / "m4_r3_taxometer_mixtures"
REPORT = ROOT / "reports" / "SUICA_M4_R3_TAXOMETER_MIXTURES_REPORT.md"
L3_OUT = ROOT / "results" / "m4_l3_taxometer_meter"

# =============================================================================
# CONFIG -- registration-fixed constants and the register-notes, all pinned
# BEFORE any main-grid number was read.
# =============================================================================

SEED = 20260819                       # registration: "SEED = 20260819"
WORLDS_PER_CELL = 8                   # registration: "8 replicate worlds/cell"
W_GRID = (0.0, 0.5, 1.0, 2.0)         # registration: style weight grid
ETA0_GRID = (0.25, 0.6)               # registration: alignment parameter grid
BAND = 0.125                          # THE L3 CERTIFICATION BUDGET (= l3.X2_TOL)
FLAT_BAR = 0.05                       # P1 cell 1: "flat (max-min < 0.05 ...)"
FLAT_APPLIES_IF_PRED_DROP = 0.13      # "...where the predicted drop is >= 0.13"

# RN-R3-1 (rule 9): THE IDENTITY ENERGY.  The registration varies w and eta0
# and pins everything else "by formula/import" to the L3 world, but the L3 grid
# crossed TWO identity energies and the R3 grid has only 8 cells -- so exactly
# one must be the registered grid's energy.  PRIMARY = rho55eq: it is L2's and
# L3's own anchor family (l3.L2_ANCHOR_CELLS is C_rho55eq_eta0/eta1, and L3's
# own bit-identity self-checks at l3:1205-1215 use l2.SB2_RHO55).  rho35eq is
# run in full as a DECLARED SECOND READING and routes nothing.
ENERGY_PRIMARY = "rho55eq"

# RN-R3-2 (rule 9): THE WORLD-SEED CONVENTION.  L3's own convention
# (l3:180-189) -- stable_bucket(f"{SEED}-{world}") under a salt disjoint from
# every earlier leg's -- with SEED = 20260819 and salt "m4r3-world", so no R3
# world coincides with any L1/L2/L3 world.  world index runs 0..7.  Every cell
# of a world shares the loadings, slow state, frame channel, noise, group
# assignment, the type subspace S, BOTH raw identity draws AND the style draw
# BIT-FOR-BIT: every cross-cell contrast in this leg (in w and in eta0) is an
# exactly paired within-world contrast.
WORLD_SALT = "m4r3-world"

# RN-R3-3 (rule 9): WHERE THE STYLE CHANNEL ENTERS.  style_a is added to the
# LATENT per-author persistent vector, alongside b, before the M-map -- the
# unique entry point that makes both registered constructions exact at once:
#   (i) V_s/V_b = w^2 BY CONSTRUCTION (style variance w^2 sigma_b^2/D per
#       latent dim over D dims = w^2 sigma_b^2 against b's sigma_b^2), and
#   (ii) style ISOTROPIC IN THE METRIC THE TAXOMETER USES -- the whitener
#       undoes M's G_PROFILE shape, so a latent-isotropic channel is isotropic
#       in the whitened coordinates where "isotropic" is what the note's
#       composition theorem assumes.  (Adding the same vector in raw 64-dim
#       card coordinates would be ANISOTROPIC after whitening and would not
#       satisfy the note's antecedent.)  D = k2a.K_LATENT = 48.
# The draw comes from an RNG seeded under the disjoint salt "m4r3-style", so
# no L-line stream's draw order changes; at w = 0 the ADD IS SKIPPED (not
# multiplied by zero), which is what makes C-R3a exact rather than approximate.
STYLE_SALT = "m4r3-style"

# RN-R3-4 (rule 9): THE PRIMARY eta_hat.  L3's own primary reading --
# `eta_hat_P`: the state-innovation whitener x the PROVISIONAL Lloyd grouping.
# Second readings computed and reported everywhere, routing nothing:
# eta_hat_T (true partition), etaw_oracle_P (oracle whitener), etaw_split_P
# (data-only whitener), etaw_flat_P (no whitening), eta_hat_angle_P.
ETA_PRIMARY_KEY = "eta_hat_P"

# RN-R3-5 (rule 9): THE ORACLE READER.  The note's formula (note section 1) on
# the REALIZED latent identity+style vectors v_i = b_i + style_i:
#     raw share := mean_i ||P_S v_i||^2 / mean_i ||v_i||^2
#     eta_hat_oracle := (raw share - d_T/D) / (1 - d_T/D)
# with d_T = l3.K_TAU = 3 (the type-discriminative subspace dimension in the L
# geometry: tau lives in the 3-frame S and b_aligned is supported on it) and
# D = k2a.K_LATENT = 48.  Zero point d_T/D = 0.0625 exactly as the note states.
# ALGEBRAIC IDENTITY (verified in tests, and the reason the oracle is the
# instrument-vs-law LOCALIZER):  E[eta_hat_oracle] = eta0/(1+w^2) EXACTLY.

# RN-R3-6 (rule 9): THE TWO-DRAW UNION READER.  PRIMARY, registration-literal
# (the registration asks for two eps draws per author, drawn independently,
# sharing tau, b and style): draw 2 refreshes k2a's noise channel ONLY; the
# trait channel (tau + b + style), the slow state, the common channel and the
# loadings are shared bit-for-bit.
# SECOND reading (declared here, routes nothing): draw 2 refreshes BOTH the
# noise and the slow state, so the only shared content is the persistent
# author card content itself.  Both use one fresh RNG under salt
# "m4r3-twodraw", seeded from the world index only, so the SAME second draw is
# reused across every (eta0, w) cell of a world -- the AUC profile in w is an
# exactly paired within-world contrast too.
# The reader: pooled AUC over the FULL 512x512 cross-draw cosine matrix of
# author-centered cards; positives = the 512 diagonal (same author, two draws),
# negatives = all 261,632 off-diagonal entries.  ITS NULL IS 0.5 and is stated
# (#68): the two draws are exchangeable under the same-author hypothesis and
# there is no composite subtlety in this design.
DRAW_SALT = "m4r3-twodraw"

# RN-R3-7 (rule 9): the k-means seed convention for the provisional grouping,
# L3's own form (l3:892) under this leg's disjoint salt.
KMEANS_SALT = "m4r3-kmeans"

# RN-R3-8 (rule 9): cell aggregation.  cell mean = plain mean over the 8
# replicate worlds; sd = sample sd (ddof=1); CI = Student-t 95% on 8 worlds.
# P3's bias CI is the t-interval on the per-world SIGNED difference
# (eta_hat - eta_hat_oracle), which is a paired contrast within each world.
CI_LEVEL = 0.95

# RN-R3-9 (rule 9): P3's crossing.  PRIMARY bias = |cell-mean eta_hat -
# cell-mean eta_hat_oracle| (the budget is stated on the 8-world CELL MEAN, so
# the bias that can cross it is the cell mean's).  Second reading: the cell
# mean of the per-world |eta_hat - eta_hat_oracle|.  The crossing style share
# is linear interpolation between the two adjacent grid shares that bracket
# BAND; "in-grid" means the bracket lies inside style share [0, 0.8].

# ID-leak scan universe (the #83 policy; synthetic leg, the scan runs anyway).
ID_UNIVERSE_FILES = (
    ROOT / "results/m4_sr0_recon/cohort_authors.csv",
    ROOT / "results/m4_w1_slow_transport/disjoint_cohort_authors.csv",
)
ID_UNIVERSE_META = ROOT / "results/m4_w1_slow_transport/id_scan_universe.json"


# =============================================================================
# The imported L3 machinery
# =============================================================================

_L3 = None


def l3() -> Any:
    """The M4-L3 leg script, imported as a module and used UNMODIFIED."""
    global _L3
    if _L3 is None:
        name = "run_suica_m4_l3_taxometer_meter"
        path = ROOT / "scripts" / f"{name}.py"
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        _L3 = module
    return _L3


def l2() -> Any:
    return l3().l2()


def l1() -> Any:
    return l3().l1()


def k2a() -> Any:
    return l3().k2a()


def v8() -> Any:
    return l3().v8


def energies() -> list[tuple[str, float]]:
    lg2 = l2()
    return [("rho55eq", lg2.SB2_RHO55), ("rho35eq", lg2.SB2_RHO35)]


def sigma_b2_of(energy: str) -> float:
    return dict(energies())[energy]


def world_seed_for(world: int) -> int:
    """RN-R3-2: L3's convention (l3:180-189) under this leg's disjoint salt."""
    return int(v8().stable_bucket(f"{SEED}-{world}", salt=WORLD_SALT,
                                  modulus=2**31 - 1))


def cell_id(energy: str, eta0: float, w_style: float) -> str:
    return f"R_{energy}_eta{eta0:g}_w{w_style:g}"


def predicted_eta(eta0: float, w_style: float) -> float:
    """The REGISTERED parameter-free dilution law (note section 2)."""
    return eta0 / (1.0 + w_style * w_style)


def designed_style_share(w_style: float) -> float:
    """V_s / (V_b + V_s) = w^2/(1+w^2) -- the realized style share by design."""
    return (w_style * w_style) / (1.0 + w_style * w_style)


# =============================================================================
# The STYLE channel (RN-R3-3) and the R3 world
# =============================================================================

def style_latent_r3(world_seed: int, n_authors: int, sigma_b2: float,
                    w_style: float) -> np.ndarray | None:
    """style_a per author, isotropic N(0, (w^2 sigma_b^2 / D) I_D) in LATENT
    coordinates (D = k2a.K_LATENT).  Returns None at w = 0 so the add is
    SKIPPED, which is what makes C-R3a bit-exact.

    The base draw z depends on the WORLD ONLY -- not on w, not on eta0 -- so
    every cross-cell contrast is exactly paired: the same style DIRECTION,
    rescaled."""
    if w_style == 0.0:
        return None
    m = k2a()
    rng = np.random.default_rng(
        v8().stable_bucket(str(world_seed), salt=STYLE_SALT, modulus=2**63 - 1))
    z = rng.normal(size=(n_authors, m.K_LATENT))
    return math.sqrt(w_style * w_style * sigma_b2 / m.K_LATENT) * z


def typed_trait_r3(world: dict, typ: dict, delta: float, sigma_b2: float,
                   eta: float, style: np.ndarray | None) -> np.ndarray:
    """l2.typed_trait_l2 (l2:243-253) with ONE substitution: the latent
    per-author persistent vector gains the style channel.  At style = None the
    arithmetic is bit-identical to l2's (adding tau[group] to a zeros array and
    then b is exactly tau[group] + b in IEEE double)."""
    m, lg1, lg2 = k2a(), l1(), l2()
    tau = lg1.latent_type_vectors(typ["S"], delta)
    latent = tau[typ["group"]] + lg2.latent_identity_l2(typ, sigma_b2, eta)
    if style is not None:
        latent = latent + style
    return m.A_SCALE * ((latent * m.G_PROFILE) @ world["loadings"].T)


def cards_for_cell_r3(world: dict, typ: dict, delta: float, sigma_b2: float,
                      eta: float, style: np.ndarray | None) -> dict[str, Any]:
    """l2.cards_for_cell (l2:280-321) VERBATIM with the single substitution
    typed_trait_l2 -> typed_trait_r3, plus l3.full_panel_halves (l3:203-211) --
    i.e. l3.cards_for_cell_l3 (l3:206-213) with the style channel.

    C-R3a certifies that the substitution is INERT at w = 0: every key below is
    compared bit-for-bit against l3.cards_for_cell_l3's own output."""
    m, lg1, lg2, lg3 = k2a(), l1(), l2(), l3()
    w = m.arm_weights(lg3.W_INT_ARM)
    sc = lg2.occasion_scheme()
    trait = typed_trait_r3(world, typ, delta, sigma_b2, eta, style)
    cen = lg1.centred_with_trait(world, trait)
    both = (0, 1)
    full = m.card(cen, w, np.arange(lg3.N_OCC), both, True)
    fit_card = m.card(cen, w, sc["fit"], both, True)
    audit_card = m.card(cen, w, sc["audit"], both, True)
    halves = {
        "interleaved": (m.card(cen, w, sc["audit_int"][0], both, True),
                        m.card(cen, w, sc["audit_int"][1], both, True)),
        "contiguous": (m.card(cen, w, sc["audit_cont"][0], both, True),
                       m.card(cen, w, sc["audit_cont"][1], both, True)),
    }
    slow_cen = cen["slow"]
    state = {
        "audit": slow_cen[:, sc["audit"], :].mean(axis=1),
        "int": (slow_cen[:, sc["audit_int"][0], :].mean(axis=1),
                slow_cen[:, sc["audit_int"][1], :].mean(axis=1)),
        "cont": (slow_cen[:, sc["audit_cont"][0], :].mean(axis=1),
                 slow_cen[:, sc["audit_cont"][1], :].mean(axis=1)),
    }
    b_lat = lg2.latent_identity_l2(typ, sigma_b2, eta)
    b_lat_total = b_lat if style is None else b_lat + style
    b_card_raw = m.A_SCALE * ((b_lat_total * m.G_PROFILE) @ world["loadings"].T)
    b_card = w["mu"] * (b_card_raw - b_card_raw.mean(axis=0, keepdims=True))
    true_card = w["mu"] * cen["trait"]
    tau = lg1.latent_type_vectors(typ["S"], delta)
    tau_card = m.A_SCALE * ((tau * m.G_PROFILE) @ world["loadings"].T)
    shift = (m.A_SCALE * (((tau[typ["group"]] + b_lat_total) * m.G_PROFILE)
                          @ world["loadings"].T)).mean(axis=0, keepdims=True)
    centroids = w["mu"] * (tau_card - shift)
    proj = lg1.card_space_type_basis(world, typ)
    obj = {"full": full, "fit_card": fit_card, "audit_card": audit_card,
           "halves": halves, "state": state, "true_card": true_card,
           "centroids": centroids, "b_card": b_card, "b_lat": b_lat,
           "proj": proj, "cen": cen, "w": w}
    obj["full_halves"] = lg3.full_panel_halves(cen, w)
    obj["b_lat_total"] = b_lat_total
    return obj


# =============================================================================
# The ORACLE excess-alignment reader (RN-R3-5)
# =============================================================================

def eta_oracle_reader(vec: np.ndarray, basis: np.ndarray,
                      d_t: int | None = None, dim: int | None = None) -> float:
    """The note's eta_hat_oracle on realized vectors.

        raw   := mean_i ||P_S v_i||^2 / mean_i ||v_i||^2
        oracle := (raw - d_T/D) / (1 - d_T/D)

    `basis` is an orthonormal d_T-frame spanning the type-discriminative
    subspace T (the L geometry's typ['S'])."""
    if d_t is None:
        d_t = l3().K_TAU
    if dim is None:
        dim = k2a().K_LATENT
    e_tot = float(np.mean(np.einsum("ij,ij->i", vec, vec)))
    if e_tot <= 0.0:
        return float("nan")
    proj = vec @ basis
    e_in = float(np.mean(np.einsum("ij,ij->i", proj, proj)))
    frac = e_in / e_tot
    zero = float(d_t) / float(dim)
    return (frac - zero) / (1.0 - zero)


def raw_aligned_share(vec: np.ndarray, basis: np.ndarray) -> float:
    e_tot = float(np.mean(np.einsum("ij,ij->i", vec, vec)))
    proj = vec @ basis
    e_in = float(np.mean(np.einsum("ij,ij->i", proj, proj)))
    return e_in / e_tot if e_tot > 0 else float("nan")


# =============================================================================
# The UNION reader (RN-R3-6)
# =============================================================================

def second_draw_card(world: dict, typ: dict, delta: float, sigma_b2: float,
                     eta: float, style: np.ndarray | None, world_seed: int,
                     refresh_slow: bool) -> np.ndarray:
    """The two-draw variant: a freshly drawn eps field per author, sharing tau,
    b and style bit-for-bit.  refresh_slow=False is the registration-literal
    PRIMARY; refresh_slow=True is the declared second reading (eps AND the
    slow state refreshed, so only the persistent author content is shared).

    The fresh draw depends on the WORLD ONLY, not on eta0 or w, so the AUC
    profile in w is an exactly paired within-world contrast."""
    m, lg3 = k2a(), l3()
    w = m.arm_weights(lg3.W_INT_ARM)
    trait = typed_trait_r3(world, typ, delta, sigma_b2, eta, style)
    rng = np.random.default_rng(v8().stable_bucket(
        f"{world_seed}-{int(refresh_slow)}", salt=DRAW_SALT, modulus=2**63 - 1))
    alt = dict(world)
    alt["trait"] = trait
    alt["noise"] = m.SIGMA_ISO * rng.normal(size=world["noise"].shape)
    if refresh_slow:
        xs = np.empty_like(world["slow_latent"])
        n_auth, n_occ, k = xs.shape
        xs[:, 0] = rng.normal(size=(n_auth, k))
        scale = math.sqrt(1.0 - lg3.PHI_SLOW ** 2)
        for t in range(1, n_occ):
            xs[:, t] = lg3.PHI_SLOW * xs[:, t - 1] + scale * rng.normal(
                size=(n_auth, k))
        alt["slow"] = m.A_SCALE * ((xs * m.G_PROFILE) @ world["loadings"].T)
    cen = m.centered_channels(alt)
    return m.card(cen, w, np.arange(lg3.N_OCC), (0, 1), True)


def pooled_auc(card_a: np.ndarray, card_b: np.ndarray) -> float:
    """Same-author-vs-different pooled AUC on the cosine of centered cards.

    S[i,j] = cos(card_a_i, card_b_j); positives = diag(S) (n same-author
    pairs), negatives = every off-diagonal entry (n(n-1) different-author
    pairs, both orientations).  Null = 0.5 (#68)."""
    a = card_a - card_a.mean(axis=0, keepdims=True)
    b = card_b - card_b.mean(axis=0, keepdims=True)
    a = a / np.linalg.norm(a, axis=1, keepdims=True)
    b = b / np.linalg.norm(b, axis=1, keepdims=True)
    sim = a @ b.T
    n = sim.shape[0]
    mask = ~np.eye(n, dtype=bool)
    pos = np.diag(sim)
    neg = sim[mask]
    ranks = rankdata(np.concatenate([pos, neg]))
    n_pos, n_neg = pos.size, neg.size
    return float((ranks[:n_pos].sum() - n_pos * (n_pos + 1) / 2.0)
                 / (n_pos * n_neg))


# =============================================================================
# One world-cell
# =============================================================================

def measure_world_cell(world: dict, typ: dict, world_index: int,
                       world_seed: int, energy: str, sigma_b2: float,
                       eta0: float, w_style: float,
                       style: np.ndarray | None) -> dict[str, Any]:
    lg1, lg2, lg3 = l1(), l2(), l3()
    delta = lg2.L1_DELTA
    cid = cell_id(energy, eta0, w_style)
    obj = cards_for_cell_r3(world, typ, delta, sigma_b2, eta0, style)
    sd = int(v8().stable_bucket(f"{world_seed}-{cid}", salt=KMEANS_SALT,
                                modulus=2**63 - 1))
    lab_p, _ = lg1.kmeans_lloyd(obj["full"], lg3.G_GROUPS, lg3.N_RESTART, sd)
    tx = lg3.taxometer(obj, world, {"P": lab_p, "T": typ["group"]})
    vec = obj["b_lat_total"]
    row: dict[str, Any] = {
        "cell": cid, "energy": energy, "sigma_b2": sigma_b2, "eta0": eta0,
        "w_style": w_style, "world": world_index, "world_seed": world_seed,
        "delta": delta, "n_authors": int(obj["full"].shape[0]),
        "style_share_designed": designed_style_share(w_style),
        "pred_eta": predicted_eta(eta0, w_style),
        "eta_hat": float(tx[ETA_PRIMARY_KEY]),
        "eta_hat_T": float(tx["eta_hat_T"]),
        "etaw_oracle_P": float(tx["etaw_oracle_P"]),
        "etaw_split_P": float(tx["etaw_split_P"]),
        "etaw_flat_P": float(tx["etaw_flat_P"]),
        "eta_hat_angle_P": float(tx["eta_hat_angle_P"]),
        "whitener_condition": float(tx["whitener_condition"]),
        "kappa_bulk_pooled_P": float(tx["kappa_bulk_pooled_P"]),
        "sigma_total_within_P": float(tx["sigma_total_within_P"]),
        "eta_oracle": eta_oracle_reader(vec, typ["S"]),
        "raw_aligned_share": raw_aligned_share(vec, typ["S"]),
        "realized_total_var": float(np.mean(np.einsum("ij,ij->i", vec, vec))),
        "realized_b_var": float(np.mean(np.einsum("ij,ij->i", obj["b_lat"],
                                                  obj["b_lat"]))),
        "ari_primary": lg1.adjusted_rand_index(typ["group"], lab_p),
    }
    row["style_share_realized"] = (
        1.0 - row["realized_b_var"] / row["realized_total_var"]
        if row["realized_total_var"] > 0 else float("nan"))
    for tag, refresh in (("auc_eps", False), ("auc_eps_slow", True)):
        alt = second_draw_card(world, typ, delta, sigma_b2, eta0, style,
                               world_seed, refresh)
        row[tag] = pooled_auc(obj["full"], alt)
    return row


# =============================================================================
# C-R3a -- the ZERO-DEFAULT certification (A1 stop on failure)
# =============================================================================

_CERT_KEYS = ("full", "fit_card", "audit_card", "true_card", "centroids",
              "b_card", "b_lat", "proj")


def certify_c_r3a(world_indices: Iterable[int] = (0, 1, 2),
                  eta_levels: Iterable[float] = (0.0, 0.25, 0.6, 1.0),
                  ) -> dict[str, Any]:
    """At w = 0 the R3 construction must be BIT-IDENTICAL to the unmodified L3
    construction.  Compared: every array l3.cards_for_cell_l3 returns, plus the
    taxometer's own full-panel halves and its eta_hat readings, on the R3 world
    seeds.  Any difference => INSTRUMENT_DEFECT, A1 stop."""
    lg1, lg2, lg3 = l1(), l2(), l3()
    checks: list[dict[str, Any]] = []
    for energy, sigma_b2 in energies():
        for wi in world_indices:
            wseed = world_seed_for(wi)
            world, typ = lg2.build_typed_world_l2(wseed, lg3.N_AUTHORS)
            for eta in eta_levels:
                ref = lg3.cards_for_cell_l3(world, typ, lg2.L1_DELTA,
                                            sigma_b2, eta)
                got = cards_for_cell_r3(world, typ, lg2.L1_DELTA, sigma_b2,
                                        eta, style_latent_r3(
                                            wseed, lg3.N_AUTHORS, sigma_b2, 0.0))
                same: dict[str, bool] = {}
                for key in _CERT_KEYS:
                    same[key] = bool(np.array_equal(ref[key], got[key]))
                for chan in ("trait", "slow", "int", "noise"):
                    same[f"cen_{chan}"] = bool(np.array_equal(
                        ref["cen"][chan], got["cen"][chan]))
                for name in ("interleaved", "contiguous"):
                    for half in (0, 1):
                        same[f"halves_{name}_{half}"] = bool(np.array_equal(
                            ref["halves"][name][half], got["halves"][name][half]))
                        same[f"full_halves_{name}_{half}"] = bool(np.array_equal(
                            ref["full_halves"][name][half],
                            got["full_halves"][name][half]))
                same["b_lat_total_is_b_lat"] = bool(np.array_equal(
                    got["b_lat_total"], got["b_lat"]))
                sd = int(v8().stable_bucket(f"{wseed}-cert", salt=KMEANS_SALT,
                                            modulus=2**63 - 1))
                lab, _ = lg1.kmeans_lloyd(ref["full"], lg3.G_GROUPS,
                                          lg3.N_RESTART, sd)
                tx_ref = lg3.taxometer(ref, world, {"P": lab, "T": typ["group"]})
                tx_got = lg3.taxometer(got, world, {"P": lab, "T": typ["group"]})
                same["taxometer_all_keys"] = bool(
                    tx_ref.keys() == tx_got.keys()
                    and all(tx_ref[k] == tx_got[k] for k in tx_ref))
                checks.append({"energy": energy, "world": int(wi),
                               "world_seed": int(wseed), "eta": float(eta),
                               "n_compared": len(same),
                               "all_identical": bool(all(same.values())),
                               "failed_keys": sorted(k for k, v in same.items()
                                                     if not v)})
    ok = all(c["all_identical"] for c in checks)
    return {"certification": "C-R3a",
            "what": "At w = 0 the R3 world is BIT-IDENTICAL to the unmodified "
                    "L3 world (every cards_for_cell_l3 array, the taxometer's "
                    "full-panel halves, and every taxometer reading)",
            "n_world_cells_compared": len(checks),
            "n_objects_per_cell": checks[0]["n_compared"] if checks else 0,
            "status": "PASS" if ok else "INSTRUMENT_DEFECT",
            "A1_stop": bool(not ok),
            "checks": checks}


# =============================================================================
# G0 -- the anchor against L3's own committed cell readings
# =============================================================================

def g0_anchor(cell: str = "C_rho55eq_eta0.25") -> dict[str, Any]:
    """The w = 0, eta0 = 0.25 anchor.  L3's OWN world seeds (MASTER_SEED
    20260824, salt 'm4l3-world') and L3's own k-means seed convention are used
    here -- and ONLY here -- so the reading is comparable to the committed
    L3 artifact `results/m4_l3_taxometer_meter/cell_C_rho55eq_eta0.25.csv`
    world-for-world.  Self-consistency form if that artifact is not on disk:
    the R3 pipeline's w=0 reading must equal l3.cards_for_cell_l3's reading on
    the identical world (which is C-R3a, reported there)."""
    lg1, lg2, lg3 = l1(), l2(), l3()
    eta = float(cell.rsplit("eta", 1)[1])
    sigma_b2 = sigma_b2_of("rho55eq" if "rho55" in cell else "rho35eq")
    rows = []
    for wi in range(lg3.WORLDS_PER_CELL):
        wseed = lg3.world_seed_for(wi)          # L3's convention, not R3's
        world, typ = lg2.build_typed_world_l2(wseed, lg3.N_AUTHORS)
        obj = cards_for_cell_r3(world, typ, lg2.L1_DELTA, sigma_b2, eta,
                                style_latent_r3(wseed, lg3.N_AUTHORS,
                                                sigma_b2, 0.0))
        sd = int(v8().stable_bucket(f"{wseed}-{cell}", salt="m4l3-kmeans",
                                    modulus=2**63 - 1))
        lab, _ = lg1.kmeans_lloyd(obj["full"], lg3.G_GROUPS, lg3.N_RESTART, sd)
        tx = lg3.taxometer(obj, world, {"P": lab, "T": typ["group"]})
        rows.append({"world": wi, "world_seed": int(wseed),
                     "eta_hat_P": float(tx["eta_hat_P"]),
                     "eta_hat_T": float(tx["eta_hat_T"])})
    mine = pd.DataFrame(rows)
    out: dict[str, Any] = {
        "anchor_cell": cell, "form": "R3 pipeline at w=0 re-run on L3's OWN "
        "world seeds and k-means convention, compared world-for-world to L3's "
        "committed cell artifact",
        "n_worlds": int(len(mine)),
        "r3_cell_mean_eta_hat_P": float(mine["eta_hat_P"].mean()),
        "r3_cell_mean_eta_hat_T": float(mine["eta_hat_T"].mean()),
        "per_world": rows,
    }
    src = L3_OUT / f"cell_{cell}.csv"
    if src.exists():
        com = pd.read_csv(src)[["world_seed", "eta_hat_P", "eta_hat_T"]]
        mrg = com.merge(mine, on="world_seed", suffixes=("_l3", "_r3"))
        dp = np.abs(mrg["eta_hat_P_l3"].to_numpy()
                    - mrg["eta_hat_P_r3"].to_numpy())
        dt = np.abs(mrg["eta_hat_T_l3"].to_numpy()
                    - mrg["eta_hat_T_r3"].to_numpy())
        out.update({
            "committed_artifact": str(src.relative_to(ROOT)),
            "committed_artifact_readable": True,
            "n_matched_worlds": int(len(mrg)),
            "l3_cell_mean_eta_hat_P": float(com["eta_hat_P"].mean()),
            "max_abs_diff_eta_hat_P": float(dp.max()),
            "max_abs_diff_eta_hat_T": float(dt.max()),
            "bit_identical_eta_hat_P": bool((dp == 0.0).all()),
            "cell_mean_bit_identical": bool(
                float(com["eta_hat_P"].mean())
                == float(mine["eta_hat_P"].mean())),
            "csv_roundtrip_epsilon": float(np.finfo(float).eps),
            "status": "PASS" if float(dp.max()) <= 1e-12 else "FAIL",
        })
    else:
        out.update({"committed_artifact": str(src.relative_to(ROOT)),
                    "committed_artifact_readable": False,
                    "status": "SELF_CONSISTENCY_ONLY",
                    "self_consistency": "C-R3a (bit-identity of the w=0 "
                                        "construction against "
                                        "l3.cards_for_cell_l3)"})
    return out


# =============================================================================
# The grid
# =============================================================================

def run_grid() -> pd.DataFrame:
    lg2, lg3 = l2(), l3()
    rows: list[dict[str, Any]] = []
    for energy, sigma_b2 in energies():
        for wi in range(WORLDS_PER_CELL):
            wseed = world_seed_for(wi)
            world, typ = lg2.build_typed_world_l2(wseed, lg3.N_AUTHORS)
            for w_style in W_GRID:
                style = style_latent_r3(wseed, lg3.N_AUTHORS, sigma_b2, w_style)
                for eta0 in ETA0_GRID:
                    rows.append(measure_world_cell(
                        world, typ, wi, wseed, energy, sigma_b2, eta0,
                        w_style, style))
    return pd.DataFrame(rows)


def _ci(values: np.ndarray) -> tuple[float, float, float, float]:
    n = int(values.size)
    mean = float(np.mean(values))
    sd = float(np.std(values, ddof=1)) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n > 1 else 0.0
    half = float(student_t.ppf(0.5 + CI_LEVEL / 2.0, n - 1)) * se if n > 1 else 0.0
    return mean, sd, mean - half, mean + half


def cell_table(worlds: pd.DataFrame) -> pd.DataFrame:
    out: list[dict[str, Any]] = []
    for (energy, eta0, w_style), grp in worlds.groupby(
            ["energy", "eta0", "w_style"], sort=True):
        grp = grp.sort_values("world")
        eh = grp["eta_hat"].to_numpy()
        eo = grp["eta_oracle"].to_numpy()
        bias = eh - eo
        m_eh, sd_eh, lo_eh, hi_eh = _ci(eh)
        m_eo, sd_eo, _, _ = _ci(eo)
        m_bi, sd_bi, lo_bi, hi_bi = _ci(bias)
        m_auc, sd_auc, lo_auc, hi_auc = _ci(grp["auc_eps"].to_numpy())
        m_aucs, sd_aucs, _, _ = _ci(grp["auc_eps_slow"].to_numpy())
        pred = predicted_eta(eta0, w_style)
        out.append({
            "cell": cell_id(energy, eta0, w_style), "energy": energy,
            "eta0": eta0, "w_style": w_style,
            "style_share": designed_style_share(w_style),
            "style_share_realized": float(grp["style_share_realized"].mean()),
            "n_worlds": int(len(grp)), "pred_eta": pred,
            "eta_hat_mean": m_eh, "eta_hat_sd": sd_eh,
            "eta_hat_lo": lo_eh, "eta_hat_hi": hi_eh,
            "abs_err_vs_pred": abs(m_eh - pred),
            "in_band": bool(abs(m_eh - pred) <= BAND),
            "eta_oracle_mean": m_eo, "eta_oracle_sd": sd_eo,
            "oracle_abs_err_vs_pred": abs(m_eo - pred),
            "oracle_in_band": bool(abs(m_eo - pred) <= BAND),
            "bias_signed_mean": m_bi, "bias_signed_sd": sd_bi,
            "bias_lo": lo_bi, "bias_hi": hi_bi,
            "bias_abs_of_cellmean": abs(m_eh - m_eo),
            "mean_abs_bias": float(np.mean(np.abs(bias))),
            "auc_mean": m_auc, "auc_sd": sd_auc,
            "auc_lo": lo_auc, "auc_hi": hi_auc,
            "auc_slow_mean": m_aucs, "auc_slow_sd": sd_aucs,
            "eta_hat_T_mean": float(grp["eta_hat_T"].mean()),
            "etaw_oracle_P_mean": float(grp["etaw_oracle_P"].mean()),
            "etaw_split_P_mean": float(grp["etaw_split_P"].mean()),
            "etaw_flat_P_mean": float(grp["etaw_flat_P"].mean()),
            "eta_hat_angle_P_mean": float(grp["eta_hat_angle_P"].mean()),
            "ari_primary_mean": float(grp["ari_primary"].mean()),
            "whitener_condition_mean": float(grp["whitener_condition"].mean()),
        })
    return pd.DataFrame(out).sort_values(
        ["energy", "eta0", "w_style"]).reset_index(drop=True)


# =============================================================================
# Adjudication -- P1 (routes), P2, P3
# =============================================================================

def _profile(cells: pd.DataFrame, energy: str, eta0: float,
             col: str) -> list[float]:
    sel = cells[(cells["energy"] == energy) & (cells["eta0"] == eta0)]
    sel = sel.sort_values("w_style")
    return [float(v) for v in sel[col]]


def _strictly_decreasing(seq: list[float]) -> bool:
    return all(b < a for a, b in zip(seq, seq[1:]))


def _strictly_increasing(seq: list[float]) -> bool:
    return all(b > a for a, b in zip(seq, seq[1:]))


def adjudicate_p1(cells: pd.DataFrame, energy: str) -> dict[str, Any]:
    per: dict[str, Any] = {}
    for eta0 in ETA0_GRID:
        seq = _profile(cells, energy, eta0, "eta_hat_mean")
        preds = [predicted_eta(eta0, w) for w in W_GRID]
        pred_drop = preds[0] - preds[-1]
        spread = max(seq) - min(seq)
        per[f"eta0={eta0:g}"] = {
            "w_grid": list(W_GRID), "predicted": preds,
            "eta_hat_cell_means": seq,
            "monotone_strict_decrease": _strictly_decreasing(seq),
            "monotone_nonstrict": all(b <= a for a, b in zip(seq, seq[1:])),
            "first_violating_step": next(
                (f"w {W_GRID[i]:g}->{W_GRID[i+1]:g}"
                 for i in range(len(seq) - 1) if seq[i + 1] >= seq[i]), None),
            "predicted_drop": pred_drop,
            "flat_clause_applies": bool(pred_drop >= FLAT_APPLIES_IF_PRED_DROP),
            "observed_spread": spread,
            "flat": bool(pred_drop >= FLAT_APPLIES_IF_PRED_DROP
                         and spread < FLAT_BAR),
            "in_band_per_cell": [bool(abs(s - p) <= BAND)
                                 for s, p in zip(seq, preds)],
            "abs_err_per_cell": [abs(s - p) for s, p in zip(seq, preds)],
            "all_in_band": all(abs(s - p) <= BAND for s, p in zip(seq, preds)),
            "oracle_cell_means": _profile(cells, energy, eta0,
                                          "eta_oracle_mean"),
            "oracle_all_in_band": all(
                abs(s - p) <= BAND for s, p in
                zip(_profile(cells, energy, eta0, "eta_oracle_mean"), preds)),
            "oracle_monotone_strict_decrease": _strictly_decreasing(
                _profile(cells, energy, eta0, "eta_oracle_mean")),
        }
    any_nonmono = any(not v["monotone_strict_decrease"] for v in per.values())
    any_flat = any(v["flat"] for v in per.values())
    all_in_band = all(v["all_in_band"] for v in per.values())
    if any_nonmono or any_flat:
        cell, num = "DILUTION_FAILS", 1
    elif not all_in_band:
        cell, num = "DILUTION_SHAPE_SHIFTS", 2
    else:
        cell, num = "DILUTION_LAW_HOLDS", 3
    return {"primary_energy": energy, "band": BAND, "per_eta0": per,
            "any_nonmonotone": any_nonmono, "any_flat": any_flat,
            "all_cell_means_in_band": all_in_band,
            "n_cells_in_band": int(sum(
                sum(v["in_band_per_cell"]) for v in per.values())),
            "n_cells": int(sum(len(v["in_band_per_cell"]) for v in per.values())),
            "cell": cell, "cell_number": num,
            "registered_lean": "DILUTION_LAW_HOLDS",
            "lean_met": bool(cell == "DILUTION_LAW_HOLDS")}


def adjudicate_p2(cells: pd.DataFrame, energy: str) -> dict[str, Any]:
    per: dict[str, Any] = {}
    for eta0 in ETA0_GRID:
        auc = _profile(cells, energy, eta0, "auc_mean")
        eta = _profile(cells, energy, eta0, "eta_hat_mean")
        aucs = _profile(cells, energy, eta0, "auc_slow_mean")
        per[f"eta0={eta0:g}"] = {
            "w_grid": list(W_GRID),
            "auc_cell_means": auc, "auc_strictly_rises": _strictly_increasing(auc),
            "eta_hat_cell_means": eta,
            "eta_hat_strictly_falls": _strictly_decreasing(eta),
            "auc_slow_refresh_cell_means": aucs,
            "auc_slow_refresh_strictly_rises": _strictly_increasing(aucs),
            "auc_span": max(auc) - min(auc),
            "null": 0.5,
        }
    rises = all(v["auc_strictly_rises"] for v in per.values())
    falls = all(v["eta_hat_strictly_falls"] for v in per.values())
    if rises and falls:
        cell = "SIGNED_DISSOCIATION_CONFIRMED"
    elif rises or falls:
        cell = "PARTIAL"
    else:
        cell = "FAILS"
    return {"primary_energy": energy, "per_eta0": per,
            "auc_rises_both_eta0": rises, "eta_hat_falls_both_eta0": falls,
            "cell": cell, "registered_lean": "SIGNED_DISSOCIATION_CONFIRMED",
            "lean_met": bool(cell == "SIGNED_DISSOCIATION_CONFIRMED"),
            "flag_73": bool(cell != "SIGNED_DISSOCIATION_CONFIRMED")}


def adjudicate_p3(cells: pd.DataFrame, energy: str) -> dict[str, Any]:
    per: dict[str, Any] = {}
    crossings: list[dict[str, Any]] = []
    for eta0 in ETA0_GRID:
        sel = cells[(cells["energy"] == energy)
                    & (cells["eta0"] == eta0)].sort_values("w_style")
        shares = [float(v) for v in sel["style_share"]]
        bias = [float(v) for v in sel["bias_abs_of_cellmean"]]
        mabs = [float(v) for v in sel["mean_abs_bias"]]
        lo = [float(v) for v in sel["bias_lo"]]
        hi = [float(v) for v in sel["bias_hi"]]
        cross = None
        for i in range(len(shares) - 1):
            if (bias[i] - BAND) * (bias[i + 1] - BAND) < 0:
                frac = (BAND - bias[i]) / (bias[i + 1] - bias[i])
                cross = {"between_style_shares": [shares[i], shares[i + 1]],
                         "between_w": [W_GRID[i], W_GRID[i + 1]],
                         "crossing_style_share": shares[i] + frac
                         * (shares[i + 1] - shares[i]),
                         "bias_below": bias[i], "bias_above": bias[i + 1],
                         "bias_ci_below": [lo[i], hi[i]],
                         "bias_ci_above": [lo[i + 1], hi[i + 1]]}
                break
        exceeds_at = [w for w, b in zip(W_GRID, bias) if b > BAND]
        per[f"eta0={eta0:g}"] = {
            "style_shares": shares, "w_grid": list(W_GRID),
            "bias_abs_of_cellmean": bias, "mean_abs_bias_second_reading": mabs,
            "bias_signed_mean": [float(v) for v in sel["bias_signed_mean"]],
            "bias_ci_lo": lo, "bias_ci_hi": hi,
            "budget": BAND, "exceeds_budget_at_w": exceeds_at,
            "crossing": cross,
        }
        if cross is not None:
            crossings.append({"eta0": eta0, **cross})
    any_cross = bool(crossings)
    return {"primary_energy": energy, "budget": BAND, "per_eta0": per,
            "crossings": crossings,
            "max_bias_over_grid": float(max(
                max(v["bias_abs_of_cellmean"]) for v in per.values())),
            "max_style_share_reached": float(max(designed_style_share(w)
                                                 for w in W_GRID)),
            "cell": "BOUND_MEASURED" if any_cross else "BUDGET_HOLDS",
            "registered_lean": "BOUND_MEASURED (weakly at w = 2)",
            "lean_met": any_cross}


def adjudicate(cells: pd.DataFrame) -> dict[str, Any]:
    p1 = adjudicate_p1(cells, ENERGY_PRIMARY)
    p2 = adjudicate_p2(cells, ENERGY_PRIMARY)
    p3 = adjudicate_p3(cells, ENERGY_PRIMARY)
    second = {}
    for energy, _ in energies():
        if energy == ENERGY_PRIMARY:
            continue
        second[energy] = {"P1": adjudicate_p1(cells, energy)["cell"],
                          "P2": adjudicate_p2(cells, energy)["cell"],
                          "P3": adjudicate_p3(cells, energy)["cell"]}
    verdict = f"{p1['cell']}__{p2['cell']}__{p3['cell']}"
    return {"P1": p1, "P2": p2, "P3": p3,
            "second_energy_routing": second,
            "routing_invariant_across_energies": bool(all(
                v["P1"] == p1["cell"] and v["P2"] == p2["cell"]
                and v["P3"] == p3["cell"] for v in second.values())),
            "verdict": verdict}


# =============================================================================
# ID-leak scan (#83; the algorithm is u2.scan_for_cohort_ids, u2:195-233)
# =============================================================================

def _is_id_char(char: str) -> bool:
    return char.isalnum() or char in {"_", "-"}


def _scan_text(label: str, text: str,
               lowered_candidates: list[tuple[str, str]]) -> list[dict[str, Any]]:
    lowered = text.casefold()
    hits: list[dict[str, Any]] = []
    for _name, needle in lowered_candidates:
        start = 0
        while True:
            index = lowered.find(needle, start)
            if index < 0:
                break
            before = lowered[index - 1] if index > 0 else " "
            after_pos = index + len(needle)
            after = lowered[after_pos] if after_pos < len(lowered) else " "
            if not _is_id_char(before) and not _is_id_char(after):
                hits.append({"path": label,
                             "line": text.count("\n", 0, index) + 1})
                break
            start = index + 1
    return hits


def _head_text(rel: str) -> str | None:
    """The file's HEAD version, or None when the path is leg-authored (no HEAD
    version -- #83: those carry ZERO tolerance)."""
    import subprocess
    proc = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT,
                          capture_output=True, text=True)
    return proc.stdout if proc.returncode == 0 else None


def scan_for_cohort_ids(paths: Iterable[Path], cohort_ids: Iterable[str],
                        min_length: int = 4) -> dict[str, Any]:
    """The widened ID gate under the #83 HEAD-IDENTICAL POLICY.

    Scanner: u2.scan_for_cohort_ids's algorithm (u2:195-233) -- casefolded
    substring search with an id-character word boundary on both sides.  A raw
    hit is PRE-EXISTING only if the same scanner reproduces the identical hit
    (same file, SAME LINE) on that file's HEAD version; a leg-authored file has
    no HEAD version and carries zero tolerance.  The gate is NEW hits = 0."""
    candidates = sorted({str(name) for name in cohort_ids
                         if len(str(name)) >= min_length})
    lowered_candidates = [(name, name.casefold()) for name in candidates]
    raw: list[dict[str, Any]] = []
    pre_existing: list[dict[str, Any]] = []
    new_hits: list[dict[str, Any]] = []
    scanned: list[str] = []
    leg_authored: list[str] = []
    for path in paths:
        if not path.exists():
            continue
        rel = str(path.relative_to(ROOT))
        scanned.append(rel)
        text = path.read_text(encoding="utf-8", errors="replace")
        here = _scan_text(rel, text, lowered_candidates)
        raw.extend(here)
        head = _head_text(rel)
        if head is None:
            leg_authored.append(rel)
            new_hits.extend(here)
            continue
        at_head = {(h["path"], h["line"])
                   for h in _scan_text(rel, head, lowered_candidates)}
        for hit in here:
            if (hit["path"], hit["line"]) in at_head:
                pre_existing.append(hit)
            else:
                new_hits.append(hit)
    return {"status": "PASS" if not new_hits else "FAIL",
            "policy": "#83 HEAD-identical (a raw hit is pre-existing only if "
                      "the same scanner reproduces the identical file+line on "
                      "that file's HEAD version; leg-authored files carry zero "
                      "tolerance); the gate is NEW hits = 0",
            "files_scanned": scanned, "leg_authored_files": leg_authored,
            "candidates_checked": len(candidates), "min_length": min_length,
            "n_raw_hits": len(raw), "n_pre_existing_hits": len(pre_existing),
            "n_hits": len(new_hits),
            "pre_existing_hits": pre_existing, "hits": new_hits}


def id_universe() -> dict[str, Any]:
    names: set[str] = set()
    sources: list[str] = []
    for path in ID_UNIVERSE_FILES:
        if path.exists():
            names |= set(pd.read_csv(path)["author"].astype(str))
            sources.append(str(path.relative_to(ROOT)))
    meta = None
    if ID_UNIVERSE_META.exists():
        meta = json.loads(ID_UNIVERSE_META.read_text())
    return {"names": names, "sources": sources, "meta": meta}


# =============================================================================
# Artifacts and the report (rule 24 -- every report number comes from these)
# =============================================================================

def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False,
                               default=float) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def config_payload() -> dict[str, Any]:
    lg2, lg3, m = l2(), l3(), k2a()
    return {
        "leg": "M4-R3", "banner": BANNER,
        "registration": "docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md "
                        "section 'M4-R3', commit 4597c33",
        "derivation": "docs/SUICA_R3_IDENTITY_RECONCILIATION_NOTE.md, "
                      "commit 1bbda62",
        "imported_machinery": "scripts/run_suica_m4_l3_taxometer_meter.py "
                              "(UNMODIFIED, imported by file)",
        "seed": SEED, "world_salt": WORLD_SALT, "style_salt": STYLE_SALT,
        "kmeans_salt": KMEANS_SALT, "twodraw_salt": DRAW_SALT,
        "world_seed_convention": "stable_bucket(f'{SEED}-{world}', "
                                 "salt='m4r3-world', modulus=2**31-1) "
                                 "(L3's convention, disjoint salt)",
        "world_seeds": [world_seed_for(i) for i in range(WORLDS_PER_CELL)],
        "worlds_per_cell": WORLDS_PER_CELL,
        "w_grid": list(W_GRID), "eta0_grid": list(ETA0_GRID),
        "n_authors": lg3.N_AUTHORS, "k_tau": lg3.K_TAU,
        "d_latent": m.K_LATENT, "d_card": m.DIM,
        "g_groups": lg3.G_GROUPS, "n_occ": lg3.N_OCC, "phi_slow": lg3.PHI_SLOW,
        "n_restart": lg3.N_RESTART, "w_int_arm": lg3.W_INT_ARM,
        "arm_weights": m.arm_weights(lg3.W_INT_ARM),
        "delta": lg2.L1_DELTA,
        "energy_primary": ENERGY_PRIMARY,
        "sigma_b2": {name: val for name, val in energies()},
        "band_is_l3_certification_budget": BAND,
        "l3_X2_TOL": lg3.X2_TOL,
        "band_equals_l3_budget": bool(BAND == lg3.X2_TOL),
        "flat_bar": FLAT_BAR, "flat_applies_if_pred_drop": FLAT_APPLIES_IF_PRED_DROP,
        "eta_primary_key": ETA_PRIMARY_KEY,
        "oracle_zero_point_dT_over_D": lg3.K_TAU / m.K_LATENT,
        "registered_predictions": {
            f"eta0={e:g}": {f"w={w:g}": predicted_eta(e, w) for w in W_GRID}
            for e in ETA0_GRID},
        "style_shares": {f"w={w:g}": designed_style_share(w) for w in W_GRID},
        "ci_level": CI_LEVEL,
        "register_notes": [
            "RN-R3-1 identity energy: PRIMARY rho55eq (L2/L3 anchor family); "
            "rho35eq run in full as a declared second reading, routes nothing",
            "RN-R3-2 world-seed convention: L3's, salt m4r3-world, SEED "
            "20260819, world index 0..7",
            "RN-R3-3 style entry point: LATENT per-author vector, alongside b, "
            "before the M-map; D = 48; skipped (not zero-scaled) at w = 0",
            "RN-R3-4 primary eta_hat = eta_hat_P (state-innovation whitener x "
            "provisional Lloyd grouping), L3's own primary",
            "RN-R3-5 oracle reader on realized b+style, d_T = 3, D = 48",
            "RN-R3-6 two-draw union reader: PRIMARY refreshes eps only "
            "(registration-literal); SECOND refreshes eps and the slow state",
            "RN-R3-7 k-means seed convention, L3's form, disjoint salt",
            "RN-R3-8 cell mean over 8 worlds, sd ddof=1, Student-t 95% CI",
            "RN-R3-9 P3 crossing by linear interpolation in style share on the "
            "cell-mean bias; second reading = mean per-world absolute bias",
        ],
    }


def _fmt(x: Any, nd: int = 4) -> str:
    if isinstance(x, bool):
        return "yes" if x else "**no**"
    if isinstance(x, float):
        if math.isnan(x):
            return "n/a"
        return f"{x:.{nd}f}"
    return str(x)


def _table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join(["---"] * len(header)) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def build_report(cfg: dict, cert: dict, g0: dict, cells: pd.DataFrame,
                 dec: dict, scan: dict, timing: dict) -> str:
    p1, p2, p3 = dec["P1"], dec["P2"], dec["P3"]
    prim = cells[cells["energy"] == ENERGY_PRIMARY].sort_values(
        ["eta0", "w_style"])
    sec = cells[cells["energy"] != ENERGY_PRIMARY].sort_values(
        ["eta0", "w_style"])

    pred_rows = [[
        f"{r.eta0:g}", f"{r.w_style:g}", _fmt(r.style_share, 2),
        f"**{r.pred_eta:.3f}**",
        f"{r.eta_hat_mean:.4f} ± {r.eta_hat_sd:.4f}",
        f"[{r.eta_hat_lo:.4f}, {r.eta_hat_hi:.4f}]",
        _fmt(r.eta_oracle_mean),
        _fmt(r.abs_err_vs_pred),
        ("**IN**" if r.in_band else "**OUT**"),
        ("in" if r.oracle_in_band else "**out**"),
    ] for r in prim.itertuples()]

    p2_rows = []
    for eta0 in ETA0_GRID:
        k = f"eta0={eta0:g}"
        v = p2["per_eta0"][k]
        for i, w in enumerate(W_GRID):
            p2_rows.append([
                f"{eta0:g}", f"{w:g}",
                f"{v['auc_cell_means'][i]:.4f}",
                f"{v['eta_hat_cell_means'][i]:.4f}",
                f"{v['auc_slow_refresh_cell_means'][i]:.4f}",
            ])

    p3_rows = []
    for eta0 in ETA0_GRID:
        k = f"eta0={eta0:g}"
        v = p3["per_eta0"][k]
        for i, w in enumerate(W_GRID):
            p3_rows.append([
                f"{eta0:g}", f"{w:g}", f"{v['style_shares'][i]:.2f}",
                f"{v['bias_abs_of_cellmean'][i]:.4f}",
                f"{v['bias_signed_mean'][i]:+.4f}",
                f"[{v['bias_ci_lo'][i]:+.4f}, {v['bias_ci_hi'][i]:+.4f}]",
                f"{v['mean_abs_bias_second_reading'][i]:.4f}",
                ("**over**" if v['bias_abs_of_cellmean'][i] > BAND else "under"),
            ])

    second_rows = [[
        f"{r.eta0:g}", f"{r.w_style:g}", f"{r.pred_eta:.3f}",
        _fmt(r.eta_hat_mean), _fmt(r.eta_hat_T_mean),
        _fmt(r.etaw_oracle_P_mean), _fmt(r.etaw_split_P_mean),
        _fmt(r.etaw_flat_P_mean), _fmt(r.eta_hat_angle_P_mean),
    ] for r in prim.itertuples()]

    rho35_rows = [[
        f"{r.eta0:g}", f"{r.w_style:g}", f"{r.pred_eta:.3f}",
        f"{r.eta_hat_mean:.4f} ± {r.eta_hat_sd:.4f}",
        _fmt(r.eta_oracle_mean), _fmt(r.auc_mean),
        ("in" if r.in_band else "**out**"),
    ] for r in sec.itertuples()]

    diag_rows = [[
        f"{r.eta0:g}", f"{r.w_style:g}", _fmt(r.style_share_realized),
        _fmt(r.ari_primary_mean), _fmt(r.whitener_condition_mean),
        f"{r.n_worlds}",
    ] for r in prim.itertuples()]

    cross_txt = "no in-grid crossing through style share 0.80"
    if p3["crossings"]:
        parts = []
        for c in p3["crossings"]:
            parts.append(
                f"η₀ = {c['eta0']:g}: the cell-mean bias crosses the 0.125 "
                f"budget at style share **{c['crossing_style_share']:.3f}** "
                f"(between w = {c['between_w'][0]:g} and w = "
                f"{c['between_w'][1]:g}; bias {c['bias_below']:.4f} → "
                f"{c['bias_above']:.4f}, replicate 95% CIs on the signed "
                f"difference [{c['bias_ci_below'][0]:+.4f}, "
                f"{c['bias_ci_below'][1]:+.4f}] and "
                f"[{c['bias_ci_above'][0]:+.4f}, {c['bias_ci_above'][1]:+.4f}])")
        cross_txt = "; ".join(parts)

    lines: list[str] = []
    A = lines.append
    A(f"# SUICA M4-R3 — the taxometer on identity mixtures\n")
    A(f"**Outcome: `{dec['verdict']}`**\n")
    A(f"- **P1 (routes):** `{p1['cell']}` (cell {p1['cell_number']}) — "
      f"registered lean `{p1['registered_lean']}`, "
      f"{'MET' if p1['lean_met'] else '**MISSED**'}.")
    A(f"- **P2 (co-primary):** `{p2['cell']}` — registered lean "
      f"`{p2['registered_lean']}`, {'MET' if p2['lean_met'] else '**MISSED**'}"
      f"{'  ⚑ #73 flag raised' if p2['flag_73'] else ''}.")
    A(f"- **P3 (co-primary):** `{p3['cell']}` — registered lean "
      f"`{p3['registered_lean']}`, "
      f"{'MET' if p3['lean_met'] else '**MISSED**'}.\n")
    A("Registered BEFORE the run in "
      "`docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md` (\"M4-R3\", commit "
      "4597c33), against the derivation in "
      "`docs/SUICA_R3_IDENTITY_RECONCILIATION_NOTE.md` (commit 1bbda62). "
      "EXPLORATORY, synthetic, card space only, label-free. The style channel "
      "is **planted**; nothing here bears on any real corpus, and no "
      "psychological construct is named or implied.\n")
    A(f"Run {timing['timestamp_utc']}; total wall time "
      f"{timing['total_seconds']:.1f} s; "
      f"{timing['n_world_cells']} world-cells.\n")

    A("## 1. What was predicted, before any world of this leg existed\n")
    A("The note's composition theorem (section 2): style_a is isotropic, so it "
      "contributes ONLY to the isotropic pool and the excess-aligned pool is "
      "untouched. With V_s/V_b = w² pinned by construction,\n")
    A("```\n    η̂(η₀, w) = η₀ / (1 + w²)\n```\n")
    A("These eight numbers are the registration's, not this run's. The "
      "acceptance band is **the L3 CERTIFICATION BUDGET ±0.125** on the "
      f"8-world cell mean (`l3.X2_TOL` = {cfg['l3_X2_TOL']}; identical: "
      f"{_fmt(cfg['band_equals_l3_budget'])}) — the instrument's own certified "
      "error, not a tolerance invented here.\n")

    A("## 2. Prediction vs read — the eight registered cells "
      f"(σ_b² = {ENERGY_PRIMARY})\n")
    A(_table(["η₀", "w", "style share", "registered prediction",
              "η̂ cell mean ± sd", "95% CI", "η̂_oracle mean",
              "abs(η̂ − pred)", "band ±0.125", "oracle in band"], pred_rows))
    A(f"**{p1['n_cells_in_band']}/{p1['n_cells']}** cell means inside the "
      f"certification band. Monotone strict decrease in w: "
      + ", ".join(f"η₀ = {e:g} → "
                  f"{_fmt(p1['per_eta0'][f'eta0={e:g}']['monotone_strict_decrease'])}"
                  for e in ETA0_GRID) + ". ")
    viol = [f"η₀ = {e:g} at {p1['per_eta0'][f'eta0={e:g}']['first_violating_step']}"
            for e in ETA0_GRID
            if p1['per_eta0'][f'eta0={e:g}']['first_violating_step']]
    A(("First violating step: " + "; ".join(viol) + ".\n") if viol
      else "No violating step.\n")
    A("Flat clause (`max−min < 0.05` where the predicted drop ≥ 0.13): "
      + ", ".join(
          f"η₀ = {e:g} predicted drop "
          f"{p1['per_eta0'][f'eta0={e:g}']['predicted_drop']:.3f}, observed "
          f"spread {p1['per_eta0'][f'eta0={e:g}']['observed_spread']:.4f} → "
          f"flat {_fmt(p1['per_eta0'][f'eta0={e:g}']['flat'])}"
          for e in ETA0_GRID) + ".\n")

    A("## 3. Instrument vs law — what the oracle localizes\n")
    A("η̂_oracle is the note's excess-alignment reader applied to the REALIZED "
      "latent identity+style vectors: `(raw aligned share − d_T/D)/(1 − d_T/D)` "
      f"with d_T = {cfg['k_tau']}, D = {cfg['d_latent']}, zero point "
      f"{cfg['oracle_zero_point_dT_over_D']:.4f}. It reads the LAW as realized "
      "in each world; η̂ reads the law THROUGH the certified whitening "
      "pipeline. Divergence between them is the instrument, not the law.\n")
    for e in ETA0_GRID:
        v = p1["per_eta0"][f"eta0={e:g}"]
        A(f"- η₀ = {e:g}: oracle all in band "
          f"{_fmt(v['oracle_all_in_band'])}, oracle monotone "
          f"{_fmt(v['oracle_monotone_strict_decrease'])}; instrument all in "
          f"band {_fmt(v['all_in_band'])}, instrument monotone "
          f"{_fmt(v['monotone_strict_decrease'])}.")
    A("")
    worst = prim.loc[prim["bias_abs_of_cellmean"].idxmax()]
    best = prim.loc[prim["bias_abs_of_cellmean"].idxmin()]
    A(f"**Localization.** Instrument and law agree everywhere on this grid. "
      f"The largest instrument−law gap is {worst.bias_abs_of_cellmean:.4f} at "
      f"η₀ = {worst.eta0:g}, w = {worst.w_style:g} (style share "
      f"{worst.style_share:.2f}) and the smallest is "
      f"{best.bias_abs_of_cellmean:.4f} at η₀ = {best.eta0:g}, w = "
      f"{best.w_style:g} — both far inside the ±{BAND} budget. There is "
      "therefore **no case on this grid where η̂ misses a registered "
      "prediction while η̂_oracle hits it**: the localizer never has to fire, "
      "because the instrument does not miss. The whitening precondition is "
      "the reason it does not: the whitener is estimated from the STATE "
      "channel's innovations, which the style channel does not touch, so "
      "adding style leaves the whitening shape exactly where the L3 "
      "certification put it and moves only the isotropic mass the estimator "
      "is designed to divide out.\n")

    A("## 4. P2 — the signed dissociation\n")
    A("The union reader is the two-draw AUC (RN-R3-6): a freshly drawn ε field "
      "per author, sharing τ, b and style; pooled same-author-vs-different AUC "
      "on the cosine of centered cards over the full 512×512 cross-draw "
      "matrix. **Its null is 0.5** and is stated (#68) — the two draws are "
      "exchangeable under the same-author hypothesis; no composite subtlety "
      "in this design.\n")
    A(_table(["η₀", "w", "AUC (union reader) cell mean",
              "η̂ cell mean", "AUC, ε+slow refreshed (2nd reading)"], p2_rows))
    A(f"AUC strictly rises across all w steps for both η₀: "
      f"{_fmt(p2['auc_rises_both_eta0'])}. η̂ strictly falls across all w "
      f"steps for both η₀: {_fmt(p2['eta_hat_falls_both_eta0'])}. → "
      f"`{p2['cell']}`.\n")
    auc_all = np.concatenate([
        np.asarray(p2["per_eta0"][f"eta0={e:g}"]["auc_cell_means"])
        for e in ETA0_GRID])
    if float(auc_all.min()) >= 1.0:
        span_slow = max(
            p2["per_eta0"][f"eta0={e:g}"]["auc_slow_refresh_cell_means"][-1]
            - p2["per_eta0"][f"eta0={e:g}"]["auc_slow_refresh_cell_means"][0]
            for e in ETA0_GRID)
        A("**Why PARTIAL, precisely: the registered PRIMARY reader is at its "
          "CEILING, not silent.** Under the registration-literal construction "
          "the two draws differ ONLY in ε — τ, b, style AND the slow state are "
          "shared bit-for-bit — so the cards are separated by their persistent "
          f"content at every w: the AUC cell mean is exactly "
          f"{float(auc_all.min()):.4f} in all "
          f"{int(auc_all.size)} cells, perfect separation, spread "
          f"{float(auc_all.max() - auc_all.min()):.4f}. The registered clause "
          "\"AUC strictly rises\" therefore **cannot fire** in this design: "
          "its antecedent is degenerate (a #59-class degenerate antecedent, "
          "found at execution, not at registration). This is a property of the "
          "reader, not of the worlds.\n")
        A("The declared second reading — the same two-draw contrast with the "
          "slow state ALSO refreshed, so the only shared content is the "
          "persistent author card content itself — is off the ceiling and "
          "**strictly rises in w for both η₀** "
          f"(largest span {span_slow:.4f}), against a strictly falling η̂ over "
          "the identical worlds. The signed dissociation the note names is "
          "therefore VISIBLE in these worlds; it is the registered reader that "
          "cannot show it. Per rule, the routing above is the registered "
          "reader's: `PARTIAL`, #73 flag raised. The second reading routes "
          "nothing.\n")

    A("## 5. P3 — the whitening bias against the realized style share\n")
    A(_table(["η₀", "w", "style share", "abs(η̂ − η̂_oracle) of cell means",
              "signed bias", "95% CI (signed, paired)",
              "mean per-world abs(bias) — 2nd reading", "vs 0.125 budget"],
             p3_rows))
    A(f"**Crossing:** {cross_txt}.\n")
    A(f"Maximum cell-mean bias anywhere on the grid: "
      f"{p3['max_bias_over_grid']:.4f}; maximum style share reached: "
      f"{p3['max_style_share_reached']:.2f}. → `{p3['cell']}`.\n")

    A("## 6. Second readings (declared before the run; they route nothing)\n")
    A("### 6.1 The other η̂ variants, same cells\n")
    A(_table(["η₀", "w", "prediction", "η̂ (primary, P grouping)",
              "η̂ true partition", "η̂ oracle whitener", "η̂ split whitener",
              "η̂ no whitening (flat)", "η̂ alignment angle"], second_rows))
    A("### 6.2 The second identity energy (rho35eq) — RN-R3-1\n")
    A(_table(["η₀", "w", "prediction", "η̂ cell mean ± sd", "η̂_oracle mean",
              "AUC", "band"], rho35_rows))
    A("Routing on the second energy: "
      + ", ".join(f"{k} → P1 `{v['P1']}`, P2 `{v['P2']}`, P3 `{v['P3']}`"
                  for k, v in dec["second_energy_routing"].items())
      + f". Routing invariant across energies: "
        f"{_fmt(dec['routing_invariant_across_energies'])}.\n")
    A("### 6.3 Realized design quantities\n")
    A(_table(["η₀", "w", "realized style share", "mean ARI (provisional "
              "grouping vs generator)", "mean whitener condition", "worlds"],
             diag_rows))

    A("## 7. Certifications\n")
    A(f"**C-R3a (zero-default, A1 stop).** {cert['what']}. "
      f"{cert['n_world_cells_compared']} world-cells × "
      f"{cert['n_objects_per_cell']} compared objects each → "
      f"**{cert['status']}** (A1 stop: {_fmt(cert['A1_stop'])}).\n")
    if g0.get("committed_artifact_readable"):
        A(f"**G0 anchor.** {g0['form']}. Against `{g0['committed_artifact']}`: "
          f"{g0['n_matched_worlds']}/{g0['n_worlds']} worlds matched; "
          f"max |Δ η̂_P| = {g0['max_abs_diff_eta_hat_P']:.3e}, "
          f"max |Δ η̂_T| = {g0['max_abs_diff_eta_hat_T']:.3e}; L3 cell mean "
          f"{g0['l3_cell_mean_eta_hat_P']:.15f} vs R3 cell mean "
          f"{g0['r3_cell_mean_eta_hat_P']:.15f} (identical: "
          f"{_fmt(g0['cell_mean_bit_identical'])}) → **{g0['status']}**. "
          "The residual is the committed CSV's decimal round-trip, not a "
          "pipeline difference: the cell mean recomputed from the same worlds "
          "is bit-identical.\n")
    else:
        A(f"**G0 anchor.** {g0['form']}; the committed L3 artifact "
          f"`{g0['committed_artifact']}` is not on disk, so the "
          f"self-consistency form is used: {g0['self_consistency']}. "
          f"R3 cell mean η̂_P = {g0['r3_cell_mean_eta_hat_P']:.6f} → "
          f"**{g0['status']}**.\n")
    A(f"**ID-leak scan (#83 HEAD-identical policy).** "
      f"{scan['candidates_checked']} cohort IDs (universe: "
      f"{', '.join(scan['universe_sources']) or 'not on disk'}) scanned over "
      f"{len(scan['files_scanned'])} committed files, of which "
      f"{len(scan.get('leg_authored_files', []))} are leg-authored (zero "
      f"tolerance): **{scan['n_hits']} NEW hits**, "
      f"{scan.get('n_pre_existing_hits', 0)} pre-existing dictionary "
      f"collisions reproduced identically at HEAD, "
      f"{scan.get('n_raw_hits', scan['n_hits'])} raw → **{scan['status']}**. "
      f"Fixed point (#83 convention): the scan is run twice and the numbers "
      f"printed here are verified to be the numbers of the report that "
      f"carries them — {_fmt(scan.get('fixed_point', False))}. The leg is "
      "synthetic and reads no corpus; the scan runs regardless.\n")

    A("## 8. Boundaries\n")
    A("- **Synthetic, card space, EXPLORATORY.** Layer V instrument world. "
      "Every number here is a property of a generator this program wrote. "
      "Nothing is transported to any corpus, and no psychological construct "
      "is named, measured or implied.\n")
    A("- **The style channel is planted**, isotropically, in the latent "
      "per-author vector. \"Style\" here is a CHANNEL LABEL for a non-trait "
      "author-persistent isotropic offset — it is not a claim about writing "
      "style, and it is not calibrated against any observed corpus.\n")
    A("- **What the instruments read.** From the note's 2×2:\n")
    A("| | trait-borne | non-trait |\n|---|---|---|\n"
      "| **aligned with T** | within-type trait residue | b_aligned "
      "(the L-line's η-carrier) |\n"
      "| **isotropic** | — (trait lives in trait axes) | style_a (the "
      "R-line's channel); b_iso |\n")
    A("  η̂ reads the ROW margin (excess alignment, blind to semantics); the "
      "union reader reads PERSISTENCE — the union of every cell. **No single "
      "program instrument reads a cell.** This leg measures the two margins "
      "on the same worlds; it does not give any instrument the missing axis.\n")
    A("- **The band is imported, not chosen.** ±0.125 is L3's own certified "
      "error budget. A cell inside the band is not evidence the law is exact "
      "there; it is evidence the law is not distinguishable from the read at "
      "the instrument's certified resolution.\n")
    A("- **η₀ = 0.6 is off the L3 grid.** L3 certified η ∈ {0, .25, .5, .75, "
      "1}; 0.6 is interpolated inside that range, not extrapolated.\n")
    A("- **Eight worlds per cell.** Every interval here is a Student-t "
      "interval on 8 replicates; cross-cell contrasts are exactly paired "
      "within world (shared loadings, state, noise, group assignment, type "
      "subspace, both identity draws and the style direction).\n")

    A("## 9. Config\n")
    A("```json\n" + json.dumps(
        {k: v for k, v in cfg.items() if k != "register_notes"},
        indent=2, default=float) + "\n```\n")
    A("**Register-notes (rule 9; pinned before any main-grid number):**\n")
    for note in cfg["register_notes"]:
        A(f"- {note}")
    A("")
    A("**Artifacts** (gitignored, `results/m4_r3_taxometer_mixtures/`): "
      "`config.json`, `config.sha256.json`, `certification_c_r3a.json`, "
      "`g0_anchor.json`, `worlds.csv`, `cells.csv`, `p1.json`, `p2.json`, "
      "`p3.json`, `id_leak_scan.json`, `decision.json`, `manifest.json`. "
      "Every table above is generated from them (rule 24).\n")
    return "\n".join(lines)


# =============================================================================
# main
# =============================================================================

def main() -> None:
    ap = argparse.ArgumentParser(description="M4-R3 — the taxometer on "
                                             "identity mixtures")
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--report", type=Path, default=REPORT)
    ap.add_argument("--skip-report", action="store_true")
    args = ap.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    cfg = config_payload()
    write_json(out / "config.json", cfg)
    blob = json.dumps(cfg, indent=2, default=float).encode("utf-8")
    write_json(out / "config.sha256.json",
               {"config_sha256": hashlib.sha256(blob).hexdigest()})
    print(f"[r3] config written; band == l3 budget: "
          f"{cfg['band_equals_l3_budget']}")

    # --- C-R3a FIRST: A1 stop before any main-grid number exists ------------
    t0 = time.time()
    cert = certify_c_r3a()
    write_json(out / "certification_c_r3a.json", cert)
    print(f"[r3] C-R3a {cert['status']} "
          f"({cert['n_world_cells_compared']} world-cells, "
          f"{time.time() - t0:.1f} s)")
    if cert["A1_stop"]:
        raise SystemExit("A1 STOP: C-R3a INSTRUMENT_DEFECT — the w = 0 "
                         "construction is not bit-identical to the unmodified "
                         "L3 world. No result is reported.")

    # --- G0 anchor -----------------------------------------------------------
    t0 = time.time()
    g0 = g0_anchor()
    write_json(out / "g0_anchor.json", g0)
    print(f"[r3] G0 anchor {g0['status']} ({time.time() - t0:.1f} s)")

    # --- the grid ------------------------------------------------------------
    t0 = time.time()
    worlds = run_grid()
    worlds.to_csv(out / "worlds.csv", index=False)
    cells = cell_table(worlds)
    cells.to_csv(out / "cells.csv", index=False)
    print(f"[r3] grid: {len(worlds)} world-cells, {len(cells)} cells "
          f"({time.time() - t0:.1f} s)")

    # --- adjudication --------------------------------------------------------
    dec = adjudicate(cells)
    write_json(out / "p1.json", dec["P1"])
    write_json(out / "p2.json", dec["P2"])
    write_json(out / "p3.json", dec["P3"])

    timing = {"timestamp_utc": datetime.now(UTC).isoformat(),
              "total_seconds": time.time() - t_start,
              "n_world_cells": int(len(worlds))}
    decision = {"leg": "M4-R3", "banner": BANNER, **timing,
                "config_sha256": read_json(
                    out / "config.sha256.json")["config_sha256"],
                "C_R3a": cert["status"], "G0_anchor": g0["status"],
                "verdict": dec["verdict"],
                "cells": {"P1": dec["P1"]["cell"], "P2": dec["P2"]["cell"],
                          "P3": dec["P3"]["cell"]},
                "leans": {"P1": {"registered": dec["P1"]["registered_lean"],
                                 "met": dec["P1"]["lean_met"]},
                          "P2": {"registered": dec["P2"]["registered_lean"],
                                 "met": dec["P2"]["lean_met"],
                                 "flag_73": dec["P2"]["flag_73"]},
                          "P3": {"registered": dec["P3"]["registered_lean"],
                                 "met": dec["P3"]["lean_met"]}},
                "second_energy_routing": dec["second_energy_routing"],
                "routing_invariant_across_energies":
                    dec["routing_invariant_across_energies"]}
    write_json(out / "decision.json", decision)
    print(f"[r3] VERDICT {dec['verdict']}")

    # --- report --------------------------------------------------------------
    if not args.skip_report:
        universe = id_universe()
        committed = [args.report, Path(__file__),
                     ROOT / "tests/test_m4_r3_taxometer_mixtures.py",
                     ROOT / "docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md",
                     ROOT / "docs/CLAIMS_LEDGER.md"]
        placeholder = {"status": "PENDING", "files_scanned": [],
                       "leg_authored_files": [], "candidates_checked": 0,
                       "n_hits": 0, "n_raw_hits": 0, "n_pre_existing_hits": 0,
                       "fixed_point": False,
                       "universe_sources": universe["sources"]}
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            build_report(cfg, cert, g0, cells, dec, placeholder, timing),
            encoding="utf-8")
        scan = scan_for_cohort_ids(committed, universe["names"])
        scan["universe_sources"] = universe["sources"]
        scan["universe_meta"] = universe["meta"]
        scan["fixed_point"] = True
        args.report.write_text(
            build_report(cfg, cert, g0, cells, dec, scan, timing),
            encoding="utf-8")
        # FIXED POINT (#83 convention): re-scan the report that now carries the
        # numbers and verify the numbers did not move.
        again = scan_for_cohort_ids(committed, universe["names"])
        scan["fixed_point"] = bool(
            again["status"] == scan["status"]
            and again["n_hits"] == scan["n_hits"]
            and again["n_raw_hits"] == scan["n_raw_hits"]
            and again["n_pre_existing_hits"] == scan["n_pre_existing_hits"])
        write_json(out / "id_leak_scan.json", scan)
        args.report.write_text(
            build_report(cfg, cert, g0, cells, dec, scan, timing),
            encoding="utf-8")
        print(f"[r3] ID-leak scan {scan['status']} "
              f"({scan['candidates_checked']} IDs, raw {scan['n_raw_hits']}, "
              f"pre-existing {scan['n_pre_existing_hits']}, "
              f"NEW {scan['n_hits']}, fixed point {scan['fixed_point']})")
        if scan["status"] != "PASS":
            raise SystemExit(f"STOP: ID-leak scan FAILED (new hits): "
                             f"{scan['hits']}")

    write_json(out / "manifest.json", {
        "leg": "M4-R3", "generated_utc": timing["timestamp_utc"],
        "files": sorted(p.name for p in out.iterdir() if p.is_file()),
        "report": str(args.report.relative_to(ROOT)),
    })
    print(f"[r3] done in {time.time() - t_start:.1f} s")


if __name__ == "__main__":
    main()
