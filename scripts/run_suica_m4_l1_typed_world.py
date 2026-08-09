#!/usr/bin/env python3
"""M4-L1 -- instrument leg: a TYPED world, the identity tax on grouping, the
ISO/ALIGNED dichotomy, and the completeness audit calibrated.

Registered spec: docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md section "M4-L1 --
Instrument leg: a typed world, the identity tax on grouping, the dichotomy, and
the completeness audit calibrated" (REGISTERED 2026-08-09, BEFORE RUN, commit
e4a0e4e).  Theory: docs/SUICA_IDENTITY_THEORY_V1.md appendix P (R1/R2/R3, the
geometry dichotomy with the SNR factor m/k_tau and the ALIGNED floor
Phi(-Delta/(2 sigma_{b,u})), the completeness audit via T6''), plus appendices
A and H (the two-split probe, the exact AR algebra, the validated instrument).

Executor standing: implementation and execution ONLY.  Everything labelled
"RN-n" is a register-note -- an operationalization of something the
registration left open (standing rule 9) -- fixed and written to
reports/SUICA_M4_L1_TYPED_WORLD_REPORT.md Part 0 BEFORE any main arm ran.

CARD SPACE ONLY.  The deployed gauge is never invoked.  Every gate and every
lean compares card-space quantities to card-space quantities (ARI-vs-ARI,
rate-vs-rate, share-vs-share); rule-14 self-check in the report section 0.0.

Reuse boundary (standing rule 12 -- generator SOURCE OBJECTS, not knob names):
  - scripts/run_suica_m4_k2a_expressive_world.py imported AS A MODULE (`k2a`),
    UNMODIFIED.  This leg calls, and does not reimplement:
      k2a.build_world          (k2a:184-236) the expressive world; its `trait`
                               return value is REPLACED by this leg's type
                               layer, every other channel used bit-for-bit
      k2a.arm_weights          (k2a:129-138) w_int="zero" -> the pinned
                               (mu, slow, common, noise) = sqrt(1/4) weights
      k2a.arm_shares           (k2a:141-142)
      k2a.centered_channels    (k2a:250-259) the author-centring
      k2a.card                 (k2a:262-276) THE CARD (full and half)
      k2a.splits               (k2a:335-340) canonical interleaved/contiguous
      k2a.ar_mean_var          (k2a:282-288) Var(s_bar), exact AR sum
      k2a.ar_set_var           (k2a:291-295) / k2a.ar_cross_cov (k2a:298-300)
      k2a.suff_stats_for_world (k2a:417-454) + k2a.world_seed_for (k2a:158-168)
                               used ONLY by the G0L anchor re-derivation
      k2a.read_csv_rt          (k2a:118-120) round-trip parsing (G5L)
      k2a.ci_of                (k2a:519-521) / k2a.mc_sd_of_endpoint (k2a:524-532)
      k2a.MASTER_SEED/K_LATENT/DIM/G_PROFILE/A_SCALE/SIGMA_ISO/UNIT_ENTRY_VAR/N_REP
    and, transitively, suica_core.v8_context_relation_field._orthonormal_loadings
    and suica_core.v8_realtext_relation_field.stable_bucket.  suica_core is NOT
    touched, and no file outside this one is modified.
  - NEW in this leg (rule 12, cited by THIS file's line numbers in the report):
    TETRAHEDRON / type_geometry() / typed_trait() (the type layer
    mean_part_i = tau_{g(i)} + b_i), cards_for_variant(), kmeans_lloyd()
    (PRIMARY grouping instrument), spectral_labels() (SECOND READING),
    adjusted_rand_index() / hungarian_accuracy(), boundary_error_rate(),
    audit_meter() (the T6''-based surviving-identity meter), pred_population()
    / predict_cell() (the independent Part-0 R2 prediction), delta_search().

Stages (foreground, chunked, resumable; artifacts under
results/m4_l1_typed_world/):
  --stage part0     G0L/G1L/G2L/G3L/G4L/G5L on RESERVED pilot worlds 9901-9904,
                    the Delta choice, the Part-0 R2 predictions and the rule-16
                    enumeration.  Writes gates.json, part0_predictions.csv,
                    part0_pilot_cells.csv, part0_enumeration_leans.csv,
                    part0_enumeration_routing.csv, part0_tables.md.  `arms`
                    REFUSES to run unless every gate passes AND this report
                    exists on disk.
  --stage arms      the 14 cells x 8 main worlds x 512 authors (--cells selects
                    a subset for chunking).  Writes cell_<id>.csv.
  --stage finalize  paired world-block bootstrap CIs against the Part-0
                    predictions, leans V-1..V-4, rule-13 stability rechecks,
                    the rule-16 routing, decision.json.
  --stage diagnostic  POST-HOC, run AFTER the registered adjudication, flagged
                    as such, writing its own artifact and NEVER touching
                    decision.json.
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
from scipy.optimize import linear_sum_assignment
from scipy.special import comb
from scipy.stats import t as student_t

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import suica_core.v8_realtext_relation_field as v8  # noqa: E402

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"

OUT = ROOT / "results" / "m4_l1_typed_world"
REPORT = ROOT / "reports" / "SUICA_M4_L1_TYPED_WORLD_REPORT.md"
K2A_OUT = ROOT / "results" / "m4_k2a_expressive_world"

# --- registration-fixed constants -------------------------------------------
MASTER_SEED = 20260822          # registration: "master_seed 20260822"
N_AUTHORS = 512                 # registration: "8 worlds x 512 authors per cell"
WORLDS_PER_CELL = 8
PILOT_WORLDS = (9901, 9902, 9903, 9904)   # RESERVED, 4-world pilot (rule-16
                                          # convention, standing after K2e);
                                          # disjoint from main indices 0..7
G_GROUPS = 4                    # registration: "G = 4 equal groups"
K_TAU = 3                       # registration: "k_tau = 3-dim subspace S"
RHO_LEVELS = (0.0, 0.15, 0.35, 0.55, 0.75)     # registration grid
GEOMETRIES = ("ISO", "ALIGNED")
COMPANION_RHO = 0.55            # registration: companions on the rho_id=.55 cells
PHI_SLOW = 0.90                 # registration: "occasion/state/noise as in K2a"
N_OCC = 8                       # registration: n_occ 8
W_INT_ARM = "zero"              # registration: w_int 0
N_RESTART = 64                  # registration: "64 seeded restarts"
B_BOOT = 2000                   # registration G3L: "B=2000, seed=master"
B_BOOT_HIGH = 20000             # registration G3L: ">=10xB at boundaries"

# --- lean thresholds, verbatim from the registration ------------------------
V1_ARI_BAR = 0.95               # "ARI >= 0.95 in 8/8 worlds, both geometries"
V2_MIN_CONTAIN = 3              # "within CI of prediction in >=3/4 non-zero cells"
V3_FLOOR_MIN_CONTAIN = 1        # "ALIGNED floor CI containment >=1/2 cells"
V3_PROJ_ISO_FRAC = 0.5          # "restores ISO rho=.55 by >= half its deficit"
V3_PROJ_ALIGNED_FRAC = 0.25     # "while restoring ALIGNED by <= a quarter"
V3_REMOVAL_BAR = 0.95           # "oracle REMOVAL restores both to >= 0.95"
V4_MIN_TRACK = 6                # "tracks designed b-share within CI in >=6/8"

_K2A = None


def k2a() -> Any:
    """The M4-K2a leg script, imported as a module and used UNMODIFIED."""
    global _K2A
    if _K2A is None:
        path = ROOT / "scripts" / "run_suica_m4_k2a_expressive_world.py"
        spec = importlib.util.spec_from_file_location(
            "run_suica_m4_k2a_expressive_world", path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _K2A = module
    return _K2A


# ---------------------------------------------------------------------------
# RN-1 (rule 9): cells.  10 main = 2 geometries x 5 rho_id; 4 companions = the
# two oracle variants on each geometry's rho_id=.55 cell.  A companion is a
# CARD VARIANT of its parent cell (same world, same draws), so the companion
# contrast is exactly paired.

VARIANTS = ("ambient", "removal", "projection")


def cell_id(geom: str, rho: float, variant: str) -> str:
    base = f"{geom}_rho{rho:g}"
    return base if variant == "ambient" else f"{base}_{variant}"


def all_cells() -> list[tuple[str, float, str]]:
    cells = [(g, r, "ambient") for g in GEOMETRIES for r in RHO_LEVELS]
    cells += [(g, COMPANION_RHO, v) for g in GEOMETRIES for v in ("removal", "projection")]
    return cells


def world_seed_for(world: int) -> int:
    """RN-2: the L1 world seed depends on the WORLD INDEX ONLY (salt disjoint
    from k2a's 'm4k2a-world'), so every cell of a world shares the loadings, the
    slow state, the frame channel, the noise, the group assignment g, the type
    subspace S and the raw identity draw xi BIT-FOR-BIT.  Every cross-cell
    contrast in this leg is therefore an exactly paired within-world contrast,
    and the rho_id=0 cells of the two geometries are bit-identical panels."""
    return int(
        v8.stable_bucket(f"{MASTER_SEED}-{world}", salt="m4l1-world", modulus=2**31 - 1)
    )


# ---------------------------------------------------------------------------
# The TYPE LAYER (new in this leg).
#
# RN-3 (rule 9): the four type centroids are the vertices of a REGULAR SIMPLEX
# (a regular tetrahedron, the unique 4-point configuration in k_tau = 3 whose
# pairwise separations are all equal), embedded in the random 3-frame S and
# scaled so that every pairwise separation equals the knob Delta EXACTLY.  The
# registration says "pairwise separation set by knob Delta"; the regular simplex
# is the realization under which "the minimum centroid separation Delta" of R2
# and "the pairwise separation" coincide, and under which the ALIGNED floor
# Phi(-Delta/(2 sigma_{b,u})) is the SAME number on all six boundaries.
# Consequence, exact: sigma_tau^2 := E||tau_{g(i)}||^2 = 3 Delta^2 / 8.

TETRAHEDRON = np.array(
    [[1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [-1.0, 1.0, -1.0], [-1.0, -1.0, 1.0]]
) / (2.0 * math.sqrt(2.0))
SIGMA_TAU2_PER_DELTA2 = 3.0 / 8.0


def identity_only_z(dims: float, rho: float) -> float:
    """The DELTA-FREE identity-only boundary z-score of this parameterization:

        z = (Delta/2) / (sigma_b / sqrt(dims)),  sigma_b^2 = sigma_tau^2 rho/(1-rho),
            sigma_tau^2 = (3/8) Delta^2
          = sqrt(dims / (4 * 3/8)) / sqrt(rho/(1-rho))
          = sqrt(2*dims/3) / sqrt(rho/(1-rho))

    dims = m = 48 (ISO -> 5.65685...) or k_tau = 3 (ALIGNED -> 1.41421...).  The
    ALIGNED per-boundary FLOOR of R2 is Phi(-z) at dims = k_tau; the SNR factor
    m/k_tau of R2 is the ratio of the two z^2."""
    if rho <= 0.0:
        return float("inf")
    return math.sqrt(dims / (4.0 * SIGMA_TAU2_PER_DELTA2)) / math.sqrt(rho / (1.0 - rho))


def sigma_b2_of(delta: float, rho: float) -> float:
    """RN-4 (rule 9): rho_id := sigma_b^2/(sigma_b^2 + sigma_tau^2) is an ENERGY
    share -- sigma_b^2 = E||b_i||^2 is the TOTAL within-type identity energy, the
    same for both geometries (R2's own reading: "energy sigma_b^2 spread over all
    m dimensions" vs "supported IN S").  Delta is held FIXED across the grid
    (registration: "at fixed Delta"), so sweeping rho_id sweeps sigma_b^2 alone:
        sigma_b^2 = sigma_tau^2 * rho/(1-rho),  sigma_tau^2 = 3 Delta^2 / 8."""
    if rho <= 0.0:
        return 0.0
    return SIGMA_TAU2_PER_DELTA2 * delta * delta * rho / (1.0 - rho)


def type_geometry(world_seed: int, n_authors: int) -> dict[str, Any]:
    """RN-5: the type stream.  Salt 'm4l1-type' is disjoint from every k2a
    stream, so k2a's own channels are bit-identical to what k2a.build_world
    would produce alone.  Draws, in this fixed order: the random 3-frame S
    (QR of a 48x3 Gaussian), the equal-size group assignment (a permutation
    split into 4 blocks of n/4), and the RAW identity draw xi ~ N(0, I_48).
    Both geometries consume the SAME xi -- ISO scales it, ALIGNED projects it
    onto S and scales -- so the two arms are maximally paired and coincide
    exactly (b == 0) at rho_id = 0."""
    m = k2a()
    rng = np.random.default_rng(
        v8.stable_bucket(str(world_seed), salt="m4l1-type", modulus=2**63 - 1)
    )
    basis = np.linalg.qr(rng.normal(size=(m.K_LATENT, K_TAU)))[0]     # (48,3)
    perm = rng.permutation(n_authors)
    group = np.empty(n_authors, dtype=int)
    per = n_authors // G_GROUPS
    for g in range(G_GROUPS):
        group[perm[g * per:(g + 1) * per]] = g
    xi = rng.normal(size=(n_authors, m.K_LATENT))
    return {"S": basis, "group": group, "xi": xi}


def latent_type_vectors(basis: np.ndarray, delta: float) -> np.ndarray:
    """tau_g in R^48: the regular tetrahedron scaled to pairwise separation
    Delta and rotated into S."""
    return delta * (TETRAHEDRON @ basis.T)


def latent_identity(typ: dict[str, Any], geom: str, delta: float, rho: float) -> np.ndarray:
    """b_i in R^48 at TOTAL energy sigma_b^2, in the requested geometry."""
    sig_b2 = sigma_b2_of(delta, rho)
    xi, basis = typ["xi"], typ["S"]
    if geom == "ISO":
        return math.sqrt(sig_b2 / xi.shape[1]) * xi
    if geom == "ALIGNED":
        return math.sqrt(sig_b2 / K_TAU) * ((xi @ basis) @ basis.T)
    raise ValueError(geom)


def typed_trait(world: dict[str, np.ndarray], typ: dict[str, Any], geom: str,
                delta: float, rho: float, drop_identity: bool = False,
                drop_type: bool = False) -> np.ndarray:
    """mean_part_i = tau_{g(i)} + b_i, mapped to 64 dims by k2a:210's own form
    (A_SCALE * ((latent * G_PROFILE) @ loadings.T), i.e. f2:178/f2:196), with
    k2a's OWN loadings for this world."""
    m = k2a()
    tau = latent_type_vectors(typ["S"], delta)
    latent = np.zeros((typ["xi"].shape[0], m.K_LATENT))
    if not drop_type:
        latent = latent + tau[typ["group"]]
    if not drop_identity:
        latent = latent + latent_identity(typ, geom, delta, rho)
    return m.A_SCALE * ((latent * m.G_PROFILE) @ world["loadings"].T)


def card_space_type_basis(world: dict[str, np.ndarray], typ: dict[str, Any]) -> np.ndarray:
    """An orthonormal basis of M(S) in R^64, M = A_SCALE * L diag(G): the ORACLE
    PROJECTION target ("projection onto true S")."""
    m = k2a()
    mapped = m.A_SCALE * ((typ["S"].T * m.G_PROFILE) @ world["loadings"].T).T   # (64,3)
    return np.linalg.qr(mapped)[0]


def build_typed_world(world_seed: int, n_authors: int) -> tuple[dict, dict]:
    """k2a.build_world for every channel except the trait, plus this leg's type
    stream.  The k2a call is UNMODIFIED, so slow/int/common/noise/loadings are
    bit-identical to k2a's own world at this seed."""
    world = k2a().build_world(world_seed, n_authors, N_OCC, PHI_SLOW)
    return world, type_geometry(world_seed, n_authors)


# ---------------------------------------------------------------------------
# Cards.

def centred_with_trait(world: dict[str, np.ndarray], trait: np.ndarray) -> dict[str, np.ndarray]:
    w2 = dict(world)
    w2["trait"] = trait
    return k2a().centered_channels(w2)


def cards_for_variant(world: dict, typ: dict, geom: str, delta: float, rho: float,
                      variant: str) -> dict[str, Any]:
    """Every card object one cell needs, all via k2a.card (k2a:262-276).

    variant:
      ambient    -- the card as the world emits it
      removal    -- the ORACLE REMOVAL companion: the generator's own identity
                    contribution to the card subtracted (b_i known)
      projection -- the ORACLE PROJECTION companion: the card projected onto
                    the true type subspace M(S)
    """
    m = k2a()
    w = m.arm_weights(W_INT_ARM)
    trait = typed_trait(world, typ, geom, delta, rho)
    cen = centred_with_trait(world, trait)
    sp = m.splits(N_OCC)
    both = (0, 1)
    full = m.card(cen, w, np.arange(N_OCC), both, True)
    halves = {name: (m.card(cen, w, s1, both, True), m.card(cen, w, s2, both, True))
              for name, (s1, s2) in sp.items()}
    # the identity's own contribution to the card (generator truth)
    b_lat = latent_identity(typ, geom, delta, rho)
    b_card_raw = m.A_SCALE * ((b_lat * m.G_PROFILE) @ world["loadings"].T)
    b_card = w["mu"] * (b_card_raw - b_card_raw.mean(axis=0, keepdims=True))
    # the true (noise-free) card and the true centroids, in the centred frame
    true_card = w["mu"] * cen["trait"]
    tau = latent_type_vectors(typ["S"], delta)
    tau_card = m.A_SCALE * ((tau * m.G_PROFILE) @ world["loadings"].T)
    shift = (m.A_SCALE * (((tau[typ["group"]] + b_lat) * m.G_PROFILE)
                          @ world["loadings"].T)).mean(axis=0, keepdims=True)
    centroids = w["mu"] * (tau_card - shift)
    proj = card_space_type_basis(world, typ)
    if variant == "removal":
        full = full - b_card
        halves = {k: (a - b_card, b - b_card) for k, (a, b) in halves.items()}
        true_card = true_card - b_card
        centroids = w["mu"] * (tau_card - shift + b_card_raw.mean(axis=0, keepdims=True))
    elif variant == "projection":
        full = (full @ proj) @ proj.T
        halves = {k: ((a @ proj) @ proj.T, (b @ proj) @ proj.T) for k, (a, b) in halves.items()}
        true_card = (true_card @ proj) @ proj.T
        centroids = (centroids @ proj) @ proj.T
    return {"full": full, "halves": halves, "true_card": true_card,
            "centroids": centroids, "b_card": b_card, "proj": proj,
            "cen": cen, "w": w}


# ---------------------------------------------------------------------------
# Grouping instruments (RN-6, rule 9: every open convention pinned here).
#
# PRIMARY  = Lloyd's k-means on cards, known G, 64 seeded restarts, best
#            (lowest) within-cluster sum of squares.
#            seeding      : k-means++ (D^2 sampling), all 64 restarts drawn in
#                           one batch from a dedicated stream
#                           stable_bucket("<world_seed>-<cell>-<instrument>",
#                           salt='m4l1-kmeans')
#            assignment   : nearest centroid, ties -> LOWEST cluster index
#                           (np.argmin)
#            empty cluster: re-seeded at the point with the largest distance to
#                           its current centroid
#            convergence  : labels unchanged, or max |centroid coordinate shift|
#                           < 1e-10, or 300 iterations
#            restart tie  : lowest restart index (np.argmin on inertia)
#            scaling      : NONE -- raw cards (the cards are already
#                           author-centred by k2a.centered_channels)
# SECOND   = spectral: top-k_tau PCA of the POOLED cards, then the same
#            k-means in the k_tau-dim projection.  PCA centring: the column
#            mean is subtracted explicitly before the SVD (the cards are
#            already author-centred, so the subtracted vector is 0 to machine
#            precision -- its norm is reported in G0L, not assumed).
# METRIC   = ARI against the generator's g (PRIMARY); Hungarian-matched
#            accuracy (scipy.optimize.linear_sum_assignment on the contingency
#            table, maximizing) as the SECOND READING.

def kmeans_lloyd(x: np.ndarray, k: int, n_restart: int, seed: int,
                 iters: int = 300, tol: float = 1e-10) -> tuple[np.ndarray, float]:
    rng = np.random.default_rng(seed)
    n = x.shape[0]
    xn = np.einsum("id,id->i", x, x)
    cent = np.empty((n_restart, k, x.shape[1]))
    cent[:, 0] = x[rng.integers(0, n, size=n_restart)]
    d2 = np.maximum(
        xn[None, :] - 2.0 * np.einsum("rd,nd->rn", cent[:, 0], x)
        + np.einsum("rd,rd->r", cent[:, 0], cent[:, 0])[:, None], 0.0)
    for j in range(1, k):
        tot = d2.sum(axis=1, keepdims=True)
        p = np.where(tot > 0, d2 / np.maximum(tot, 1e-300), 1.0 / n)
        u = rng.random(n_restart)
        idx = (np.cumsum(p, axis=1) < u[:, None]).sum(axis=1).clip(0, n - 1)
        cent[:, j] = x[idx]
        nd = np.maximum(
            xn[None, :] - 2.0 * np.einsum("rd,nd->rn", cent[:, j], x)
            + np.einsum("rd,rd->r", cent[:, j], cent[:, j])[:, None], 0.0)
        d2 = np.minimum(d2, nd)
    lab = np.full((n_restart, n), -1, dtype=int)
    for _ in range(iters):
        dist = (xn[None, None, :] - 2.0 * np.einsum("rkd,nd->rkn", cent, x)
                + np.einsum("rkd,rkd->rk", cent, cent)[:, :, None])
        new = dist.argmin(axis=1)
        if np.array_equal(new, lab):
            break
        lab = new
        onehot = np.zeros((n_restart, k, n))
        np.put_along_axis(onehot, lab[:, None, :], 1.0, axis=1)
        cnt = onehot.sum(axis=2)
        newc = np.einsum("rkn,nd->rkd", onehot, x) / np.maximum(cnt, 1.0)[:, :, None]
        if (cnt == 0).any():
            far = dist.min(axis=1).argmax(axis=1)
            for r, kk in zip(*np.nonzero(cnt == 0), strict=True):
                newc[r, kk] = x[far[r]]
        shift = float(np.abs(newc - cent).max())
        cent = newc
        if shift < tol:
            break
    dist = (xn[None, None, :] - 2.0 * np.einsum("rkd,nd->rkn", cent, x)
            + np.einsum("rkd,rkd->rk", cent, cent)[:, :, None])
    lab = dist.argmin(axis=1)
    inertia = dist.min(axis=1).sum(axis=1)
    best = int(inertia.argmin())
    return lab[best], float(inertia[best])


def spectral_labels(x: np.ndarray, k: int, k_tau: int, n_restart: int,
                    seed: int) -> tuple[np.ndarray, float, np.ndarray]:
    xc = x - x.mean(axis=0, keepdims=True)
    _, sv, vt = np.linalg.svd(xc, full_matrices=False)
    lab, inertia = kmeans_lloyd(xc @ vt[:k_tau].T, k, n_restart, seed)
    return lab, inertia, sv


def adjusted_rand_index(a: np.ndarray, b: np.ndarray) -> float:
    """ARI from the contingency table (verified against
    sklearn.metrics.adjusted_rand_score in G0L)."""
    n = len(a)
    ca = np.unique(a, return_inverse=True)[1]
    cb = np.unique(b, return_inverse=True)[1]
    cont = np.zeros((int(ca.max()) + 1, int(cb.max()) + 1))
    np.add.at(cont, (ca, cb), 1.0)
    s_ij = float(comb(cont, 2).sum())
    s_i = float(comb(cont.sum(axis=1), 2).sum())
    s_j = float(comb(cont.sum(axis=0), 2).sum())
    exp = s_i * s_j / float(comb(n, 2))
    denom = 0.5 * (s_i + s_j) - exp
    return float((s_ij - exp) / denom) if denom != 0.0 else 0.0


def hungarian_accuracy(a: np.ndarray, b: np.ndarray) -> float:
    ca = np.unique(a, return_inverse=True)[1]
    cb = np.unique(b, return_inverse=True)[1]
    cont = np.zeros((int(ca.max()) + 1, int(cb.max()) + 1))
    np.add.at(cont, (ca, cb), 1.0)
    r, c = linear_sum_assignment(-cont)
    return float(cont[r, c].sum() / len(a))


def boundary_error_rate(cards: np.ndarray, centroids: np.ndarray,
                        group: np.ndarray) -> float:
    """RN-7: THE per-boundary misassignment rate whose probability R2 predicts
    as Phi(-Delta/(2 sigma_u)).  For every author i and every other type h, the
    event is "i is on the wrong side of the (g(i), h) bisecting hyperplane":
        <c_i - (tau_g + tau_h)/2, tau_h - tau_g>  >  0.
    Averaged over authors and over the G-1 boundaries adjacent to each author's
    own type.  Rate-vs-rate against the closed form; no link function."""
    total = 0.0
    count = 0
    for g in range(G_GROUPS):
        sel = group == g
        if not sel.any():
            continue
        for h in range(G_GROUPS):
            if h == g:
                continue
            diff = centroids[h] - centroids[g]
            mid = 0.5 * (centroids[h] + centroids[g])
            total += float(((cards[sel] - mid) @ diff > 0.0).sum())
            count += int(sel.sum())
    return total / float(count)


def predicted_boundary_error(world: dict, typ: dict, geom: str, delta: float,
                             rho: float, identity_only: bool) -> float:
    """Closed form, on the REALIZED geometry of this world: the mean over the
    six boundaries of Phi(-Delta_card/(2 sigma_u)), with sigma_u^2 the
    perturbation variance along the boundary normal -- identity ONLY (the R2
    FLOOR) or identity + slow state + observation noise (the full card)."""
    m = k2a()
    w = m.arm_weights(W_INT_ARM)
    tau = latent_type_vectors(typ["S"], delta)
    mmat = m.A_SCALE * (world["loadings"] * m.G_PROFILE)          # (64,48)
    tau_card = w["mu"] * (tau @ mmat.T)
    sig_b2 = sigma_b2_of(delta, rho)
    v_full = m.ar_mean_var(N_OCC, PHI_SLOW)
    vals = []
    for g in range(G_GROUPS):
        for h in range(g + 1, G_GROUPS):
            diff = tau_card[h] - tau_card[g]
            sep = float(np.linalg.norm(diff))
            u = diff / sep
            mtu = mmat.T @ u
            if geom == "ISO":
                var_b = (sig_b2 / m.K_LATENT) * float(mtu @ mtu)
            else:
                var_b = (sig_b2 / K_TAU) * float(np.sum((typ["S"].T @ mtu) ** 2))
            var_b *= w["mu"] ** 2
            var = var_b
            if not identity_only:
                var += w["slow"] ** 2 * v_full * float(mtu @ mtu)
                var += w["noise"] ** 2 * m.SIGMA_ISO**2 / (N_OCC * m.N_REP)
            if var <= 0.0:
                vals.append(0.0)
            else:
                vals.append(0.5 * math.erfc(sep / (2.0 * math.sqrt(var)) / math.sqrt(2.0)))
    return float(np.mean(vals))


# ---------------------------------------------------------------------------
# RN-8 (rule 9): the completeness-audit meter (T6''/T6' applied to within-TRUE-
# group deviations).
#
# Within a TRUE type, the type vector cancels EXACTLY, so the within-group
# deviation card is d_i = w_mu*b_i + w_slow*s_bar_i + w_noise*e_bar_i.  In K2a's
# normalized pooled-covariance units (dot / entries / UNIT_ENTRY_VAR, k2a:472)
# the exact algebra is
#     V_full = A_b + B*v_full + E/(n_occ*n_rep)
#     C_sigma = A_b + B*c_sigma          (sigma in {interleaved, contiguous})
# with v_full = k2a.ar_mean_var(n_occ, phi) and c_sigma = k2a.ar_cross_cov of the
# split halves -- K2a's own validated algebra (12/12 cells, max rel err 0.30%,
# IDT appendix H).
#
# PRIMARY meter = the TWO-SPLIT (T6') solved form, which needs NO design share:
#     B_hat = (C_int - C_cont)/(c_int - c_cont);  A_hat = C_cont - B_hat*c_cont
#     S_id  = A_hat / V_full          <-- the surviving-identity share
# SECOND READING = the contiguous-only form with B taken from the design
#     S_id_cont = (C_cont - B_design*c_cont)/V_full
# THIRD READING = the raw two-split reproducibilities rho_int, rho_cont and the
#     T6' GAP of the deviation cards (K2a's own estimator, reported unreduced).
# The DESIGNED b-share it must track is the realized-energy share
#     share_b = ||w_mu * (group-centred b card)||^2 / ||d_full||^2
# (both in the same normalized units; share-vs-share, no link).

def _norm_dot(a: np.ndarray, b: np.ndarray) -> float:
    m = k2a()
    return float(np.einsum("id,id->", a, b) / (a.shape[0] * m.DIM) / m.UNIT_ENTRY_VAR)


def group_centre(x: np.ndarray, group: np.ndarray) -> np.ndarray:
    out = x.copy()
    for g in range(G_GROUPS):
        sel = group == g
        out[sel] -= x[sel].mean(axis=0, keepdims=True)
    return out


def audit_meter(card_obj: dict[str, Any], group: np.ndarray) -> dict[str, float]:
    m = k2a()
    w = card_obj["w"]
    sp = m.splits(N_OCC)
    c_int = m.ar_cross_cov(sp["interleaved"][0], sp["interleaved"][1], PHI_SLOW)
    c_cont = m.ar_cross_cov(sp["contiguous"][0], sp["contiguous"][1], PHI_SLOW)
    d_full = group_centre(card_obj["full"], group)
    v_full = _norm_dot(d_full, d_full)
    caps = {}
    for name in ("interleaved", "contiguous"):
        h1, h2 = card_obj["halves"][name]
        d1, d2 = group_centre(h1, group), group_centre(h2, group)
        caps[name] = _norm_dot(d1, d2)
        caps[f"rho_{name}"] = _norm_dot(d1, d2) / math.sqrt(
            _norm_dot(d1, d1) * _norm_dot(d2, d2))
    b_dev = group_centre(card_obj["b_card"], group)
    a_design = _norm_dot(b_dev, b_dev)
    b_hat = (caps["interleaved"] - caps["contiguous"]) / (c_int - c_cont)
    a_hat = caps["contiguous"] - b_hat * c_cont
    a_cont = caps["contiguous"] - (w["slow"] ** 2) * c_cont
    return {
        "audit_V_full": v_full,
        "audit_C_interleaved": caps["interleaved"],
        "audit_C_contiguous": caps["contiguous"],
        "audit_rho_interleaved": caps["rho_interleaved"],
        "audit_rho_contiguous": caps["rho_contiguous"],
        "audit_gap": caps["rho_interleaved"] - caps["rho_contiguous"],
        "audit_B_hat": b_hat,
        "audit_A_hat": a_hat,
        "audit_S_id": a_hat / v_full,
        "audit_S_id_contiguous_reading": a_cont / v_full,
        "audit_A_design": a_design,
        "audit_share_b_design": a_design / v_full,
        "audit_c_int": c_int,
        "audit_c_cont": c_cont,
    }


# ---------------------------------------------------------------------------
# Part-0 R2 PREDICTIONS (G4L).  An INDEPENDENT re-implementation of the card
# LAW on a prediction-only seed stream ('m4l1-pred'): no world of any index --
# main or pilot -- is generated here, and no main-world number exists when the
# predictions are computed.
#
# RN-9 (rule 9): the registration's "Part-0 R2 prediction" of per-cell ARI is
# the ORACLE-CENTROID (nearest-TRUE-centroid) ARI -- R2's own distance rule,
# the achievable ceiling for a distance-based grouper with known G.  The
# INSTRUMENT-BEHAVIOUR prediction (the registered PRIMARY k-means run on draws
# from the same law) is computed alongside and reported as the declared second
# reading; V-2 is scored under BOTH.

def pred_population(delta: float, rho: float, geom: str, seed: int,
                    n_authors: int = N_AUTHORS) -> dict[str, np.ndarray]:
    m = k2a()
    from suica_core.v8_context_relation_field import _orthonormal_loadings
    rng = np.random.default_rng(seed)
    load = _orthonormal_loadings(rng, m.DIM, m.K_LATENT)
    basis = np.linalg.qr(rng.normal(size=(m.K_LATENT, K_TAU)))[0]
    mmat = m.A_SCALE * (load * m.G_PROFILE)
    w = m.arm_weights(W_INT_ARM)
    tau = latent_type_vectors(basis, delta)
    group = np.repeat(np.arange(G_GROUPS), n_authors // G_GROUPS)
    xi = rng.normal(size=(n_authors, m.K_LATENT))
    sig_b2 = sigma_b2_of(delta, rho)
    if geom == "ISO":
        b = math.sqrt(sig_b2 / m.K_LATENT) * xi
    else:
        b = math.sqrt(sig_b2 / K_TAU) * ((xi @ basis) @ basis.T)
    v_full = m.ar_mean_var(N_OCC, PHI_SLOW)
    s = math.sqrt(v_full) * rng.normal(size=(n_authors, m.K_LATENT))
    card = w["mu"] * ((tau[group] + b) @ mmat.T) + w["slow"] * (s @ mmat.T)
    card = card + w["noise"] * m.SIGMA_ISO / math.sqrt(N_OCC * m.N_REP) * rng.normal(
        size=(n_authors, m.DIM))
    shift = card.mean(axis=0, keepdims=True)
    card = card - shift
    centroids = w["mu"] * (tau @ mmat.T) - shift
    b_card = w["mu"] * (b @ mmat.T)
    proj = np.linalg.qr(mmat @ basis)[0]
    return {"card": card, "group": group, "centroids": centroids,
            "b_card": b_card - b_card.mean(axis=0, keepdims=True), "proj": proj}


def pred_seed(rep: int) -> int:
    return int(v8.stable_bucket(f"pred-{rep}", salt="m4l1-pred", modulus=2**63 - 1))


def oracle_ari(pop: dict[str, np.ndarray], variant: str = "ambient") -> float:
    x, cent = pop["card"], pop["centroids"]
    if variant == "removal":
        x = x - pop["b_card"]
    elif variant == "projection":
        x = (x @ pop["proj"]) @ pop["proj"].T
        cent = (cent @ pop["proj"]) @ pop["proj"].T
    d = ((x[:, None, :] - cent[None, :, :]) ** 2).sum(axis=2)
    return adjusted_rand_index(pop["group"], d.argmin(axis=1))


def predict_cell(delta: float, rho: float, geom: str, variant: str, reps: int,
                 with_instrument: bool) -> dict[str, float]:
    orc, ins, spc = [], [], []
    for r in range(reps):
        pop = pred_population(delta, rho, geom, pred_seed(r))
        orc.append(oracle_ari(pop, variant))
        if with_instrument:
            x = pop["card"]
            if variant == "removal":
                x = x - pop["b_card"]
            elif variant == "projection":
                x = (x @ pop["proj"]) @ pop["proj"].T
            seed = int(v8.stable_bucket(f"{r}-{geom}-{rho}-{variant}",
                                        salt="m4l1-predkm", modulus=2**63 - 1))
            lab, _ = kmeans_lloyd(x, G_GROUPS, N_RESTART, seed)
            ins.append(adjusted_rand_index(pop["group"], lab))
            lab2, _, _ = spectral_labels(x, G_GROUPS, K_TAU, N_RESTART, seed + 1)
            spc.append(adjusted_rand_index(pop["group"], lab2))
    out = {"pred_ari_oracle": float(np.mean(orc)),
           "pred_ari_oracle_sd": float(np.std(orc, ddof=1)) if len(orc) > 1 else 0.0,
           "pred_reps": reps}
    if with_instrument:
        out["pred_ari_instrument"] = float(np.mean(ins))
        out["pred_ari_instrument_sd"] = float(np.std(ins, ddof=1)) if len(ins) > 1 else 0.0
        out["pred_ari_spectral"] = float(np.mean(spc))
    return out


# --- RN-10 (rule 9 + rule 17): the Delta rule and its ONE-STEP ladder --------
#
# The registration asks for Delta "set in Part 0 so the ISO rho_id=.35 cell is
# mid-range (pilot ARI in (0.05, 0.95))" AND (V-1) for the rho_id=0 cells to
# reach ARI >= 0.95 in 8/8 worlds.  A PRIORI, before any number was computed:
# the identity-only boundary z-score of this design is DELTA-FREE, because
# sigma_b^2 is tied to Delta by rho_id:
#     ISO      z = (Delta/2) / (sigma_b/sqrt(m))     = sqrt(m/ (2*SIGMA_TAU2)) ...
#              = sqrt(48*8/(4*3)) / sqrt(rho/(1-rho))   =  5.6569 / sqrt(rho/(1-rho))
#     ALIGNED  z = (Delta/2) / (sigma_b/sqrt(k_tau)) =  1.4142 / sqrt(rho/(1-rho))
# so the ISO arm's identity-only per-boundary error never exceeds Phi(-3.266)
# = 5.5e-4 anywhere on the registered grid: the ISO arm CANNOT be brought to
# mid-range by identity at ANY Delta.  Any mid-range ISO ARI must therefore be
# manufactured by the rho-INDEPENDENT state/observation channel, which depresses
# the rho_id = 0 cell by very nearly the same amount -- so the band clause and
# V-1's bar are jointly satisfiable only inside a vanishing ARI window (rule 11).
# Pinned resolution, declared before any pilot ARI existed:
#   (i)  Delta_0 := bisection to make the Part-0 predicted rho_id=0 oracle ARI
#        equal DELTA_TARGET_ARI0 = 0.99 (V-1's bar plus headroom, because V-1 is
#        a per-WORLD 8/8 clause, not a pooled one);
#   (ii) G2L evaluates BOTH the registered band clause on the four mid cells
#        (geometry x rho_id in {.35,.55}) and the machinery section's saturation
#        clause (no main cell at pilot ARI >= 0.999 or <= 0.001);
#   (iii) the ladder has exactly ONE step: Delta_1 = 1.5*Delta_0 if any mid cell
#        is FLOORED, Delta_1 = Delta_0/1.5 if any mid cell is SATURATED;
#   (iv) GUARD: the step is REFUSED, and the triggering clause recorded
#        UNREALIZABLE with the proof above, if it would drive the predicted
#        rho_id=0 ARI below DELTA_GUARD_ARI0 = 0.97 -- manufacturing a V-1 MISS
#        would route the leg to P1L on an instrument artifact, the one outcome
#        the registration reserves for a real instrument defect;
#   (v)  a band clause failing FROM ABOVE on an UNSATURATED cell does not
#        trigger the ladder (a cell at ARI 0.98 is not "saturated at 1"); it is
#        recorded as a rule-11 unsatisfiability with its proof.
DELTA_TARGET_ARI0 = 0.99
DELTA_GUARD_ARI0 = 0.97
DELTA_BISECT_REPS = 24
DELTA_BRACKET = (1.0, 20.0)
DELTA_BISECT_ITERS = 40
PRED_REPS_ORACLE = 64
PRED_REPS_INSTRUMENT = 12
BAND = (0.05, 0.95)
SATURATION = (0.001, 0.999)
MID_RHOS = (0.35, 0.55)


def delta_search(target: float) -> dict[str, Any]:
    lo, hi = DELTA_BRACKET
    trace = []
    for _ in range(DELTA_BISECT_ITERS):
        mid = 0.5 * (lo + hi)
        val = predict_cell(mid, 0.0, "ISO", "ambient", DELTA_BISECT_REPS, False)
        trace.append({"delta": mid, "pred_ari_rho0": val["pred_ari_oracle"]})
        if val["pred_ari_oracle"] < target:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-9:
            break
    return {"delta": 0.5 * (lo + hi), "target_ari_rho0": target,
            "bracket": list(DELTA_BRACKET), "iterations": len(trace),
            "reps_per_evaluation": DELTA_BISECT_REPS, "trace": trace}


# ---------------------------------------------------------------------------
# rule-16 enumeration (G5L)

SUB_STATES = ("HOLD", "MISS", "BOUNDARY", "UNREALIZABLE")
LEAN_STATES = ("HOLD", "MISS", "BOUNDARY")
LEAN_SUBCLAUSES = {
    "V-1": ["ISO rho0 ARI>=.95 in 8/8", "ALIGNED rho0 ARI>=.95 in 8/8"],
    "V-2": ["ISO ordering strictly decreasing", "prediction containment >=3/4"],
    "V-3": ["ALIGNED<ISO pooled CI excludes 0", "ALIGNED floor containment >=1/2",
            "projection ISO>=1/2 deficit AND ALIGNED<=1/4 deficit",
            "removal both >= .95"],
    "V-4": ["rho0 null within pilot margin", "b-share tracking >=6/8"],
}


def lean_from_subclauses(states: tuple[str, ...]) -> str:
    """RN-11: CONJUNCTIVE aggregation (K3's rule, adopted).  Any MISS -> MISS;
    else any BOUNDARY -> BOUNDARY; else HOLD.  UNREALIZABLE sub-clauses are
    EXCLUDED from the conjunction and disclosed in the lean's tag (a design
    shortfall is never scored as a theory failure -- rule 2 applied to
    realizability).  If EVERY sub-clause is UNREALIZABLE the lean is BOUNDARY."""
    live = [s for s in states if s != "UNREALIZABLE"]
    if not live:
        return "BOUNDARY"
    if "MISS" in live:
        return "MISS"
    if "BOUNDARY" in live:
        return "BOUNDARY"
    return "HOLD"


def route(lean_states: dict[str, str]) -> str:
    """The registration's precedence routing.  RN-12: a BOUNDARY lean (rule 13)
    is NOT counted as a MISS; the routing outcome carries the tag downstream."""
    if lean_states["V-1"] == "MISS":
        return "P1L"
    misses = sum(1 for k in ("V-2", "V-3", "V-4") if lean_states[k] == "MISS")
    if misses >= 2:
        return "P2L"
    if misses == 1:
        return "P3L"
    return "P4L"


def build_enumeration() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    rows = []
    for lean, subs in LEAN_SUBCLAUSES.items():
        for combo in itertools.product(SUB_STATES, repeat=len(subs)):
            rows.append({"lean": lean, "n_subclauses": len(subs),
                         "subclause_states": "|".join(combo),
                         "lean_state": lean_from_subclauses(combo)})
    layer_a = pd.DataFrame(rows)
    rows2 = []
    for combo in itertools.product(LEAN_STATES, repeat=4):
        states = dict(zip(["V-1", "V-2", "V-3", "V-4"], combo, strict=True))
        rows2.append({**{f"state_{k}": v for k, v in states.items()},
                      "n_miss": sum(1 for v in combo if v == "MISS"),
                      "n_boundary": sum(1 for v in combo if v == "BOUNDARY"),
                      "route": route(states)})
    layer_b = pd.DataFrame(rows2)
    registered_16 = layer_b[
        (layer_b[[f"state_V-{i}" for i in (1, 2, 3, 4)]] != "BOUNDARY").all(axis=1)
    ]
    audit = {
        "layer_a_rows": int(len(layer_a)),
        "layer_a_expected": int(sum(len(SUB_STATES) ** len(s)
                                    for s in LEAN_SUBCLAUSES.values())),
        "layer_a_unique_keys": int(
            layer_a[["lean", "subclause_states"]].drop_duplicates().shape[0]),
        "layer_a_all_assigned": bool(layer_a["lean_state"].isin(LEAN_STATES).all()),
        "layer_b_rows": int(len(layer_b)),
        "layer_b_expected": len(LEAN_STATES) ** 4,
        "layer_b_unique_keys": int(
            layer_b[[f"state_V-{i}" for i in (1, 2, 3, 4)]].drop_duplicates().shape[0]),
        "layer_b_all_assigned": bool(layer_b["route"].isin(
            ["P1L", "P2L", "P3L", "P4L"]).all()),
        "layer_b_route_counts": {k: int(v) for k, v in
                                 layer_b["route"].value_counts().items()},
        "layer_b_all_routes_reachable": bool(
            set(layer_b["route"]) == {"P1L", "P2L", "P3L", "P4L"}),
        "registered_2pow4_rows": int(len(registered_16)),
        "registered_2pow4_route_counts": {
            k: int(v) for k, v in registered_16["route"].value_counts().items()},
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

def measure_cell_world(world: dict, typ: dict, geom: str, delta: float, rho: float,
                       variant: str, world_seed: int) -> dict[str, Any]:
    m = k2a()
    cid = cell_id(geom, rho, variant)
    obj = cards_for_variant(world, typ, geom, delta, rho, variant)
    group = typ["group"]
    x = obj["full"]
    seed_p = int(v8.stable_bucket(f"{world_seed}-{cid}-primary",
                                  salt="m4l1-kmeans", modulus=2**63 - 1))
    seed_s = int(v8.stable_bucket(f"{world_seed}-{cid}-spectral",
                                  salt="m4l1-kmeans", modulus=2**63 - 1))
    lab_p, inertia_p = kmeans_lloyd(x, G_GROUPS, N_RESTART, seed_p)
    lab_s, inertia_s, sv = spectral_labels(x, G_GROUPS, K_TAU, N_RESTART, seed_s)
    ev = sv**2
    row: dict[str, Any] = {
        "cell": cid, "geometry": geom, "rho_id": rho, "variant": variant,
        "world_seed": world_seed, "n_authors": int(x.shape[0]), "delta": delta,
        "ari_primary": adjusted_rand_index(group, lab_p),
        "ari_spectral": adjusted_rand_index(group, lab_s),
        "acc_primary": hungarian_accuracy(group, lab_p),
        "acc_spectral": hungarian_accuracy(group, lab_s),
        "inertia_primary": inertia_p, "inertia_spectral": inertia_s,
        "eigengap_ratio": float(ev[K_TAU - 1] / ev[K_TAU]),
        "eigengap_abs": float(ev[K_TAU - 1] - ev[K_TAU]),
        "pca_grand_mean_norm": float(np.linalg.norm(x.mean(axis=0))),
        "boundary_err_true_card": boundary_error_rate(obj["true_card"], obj["centroids"], group),
        "boundary_err_full_card": boundary_error_rate(x, obj["centroids"], group),
        "boundary_err_pred_floor": predicted_boundary_error(world, typ, geom, delta, rho, True),
        "boundary_err_pred_full": predicted_boundary_error(world, typ, geom, delta, rho, False),
        "ari_oracle_centroid": adjusted_rand_index(
            group, ((x[:, None, :] - obj["centroids"][None, :, :]) ** 2).sum(axis=2).argmin(axis=1)),
    }
    # realized design quantities (G0L)
    b_lat = latent_identity(typ, geom, delta, rho)
    tau = latent_type_vectors(typ["S"], delta)
    row["realized_sigma_b2"] = float(np.mean(np.einsum("ij,ij->i", b_lat, b_lat)))
    row["realized_sigma_tau2"] = float(
        np.mean(np.einsum("ij,ij->i", tau[group], tau[group])))
    denom = row["realized_sigma_b2"] + row["realized_sigma_tau2"]
    row["realized_rho_id"] = row["realized_sigma_b2"] / denom if denom > 0 else 0.0
    pw = np.linalg.norm(tau[:, None, :] - tau[None, :, :], axis=2)[np.triu_indices(G_GROUPS, 1)]
    row["realized_delta_latent_min"] = float(pw.min())
    row["realized_delta_latent_max"] = float(pw.max())
    cpw = np.linalg.norm(obj["centroids"][:, None, :] - obj["centroids"][None, :, :],
                         axis=2)[np.triu_indices(G_GROUPS, 1)]
    row["realized_delta_card_min"] = float(cpw.min())
    row["realized_delta_card_mean"] = float(cpw.mean())
    row["realized_delta_card_max"] = float(cpw.max())
    row.update(audit_meter(obj, group))
    row["card_var_norm"] = _norm_dot(x, x)
    return row


def run_world_cells(world: int, delta: float, cells: list[tuple[str, float, str]],
                    n_authors: int = N_AUTHORS) -> list[dict[str, Any]]:
    wseed = world_seed_for(world)
    world_obj, typ = build_typed_world(wseed, n_authors)
    return [measure_cell_world(world_obj, typ, g, delta, r, v, wseed) for g, r, v in cells]


# ---------------------------------------------------------------------------
# Stage: part0

def run_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    m = k2a()
    gates: dict[str, Any] = {
        "leg": "M4-L1", "banner": BANNER,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED, "pilot_worlds": list(PILOT_WORLDS),
        "n_authors": N_AUTHORS, "worlds_per_cell": WORLDS_PER_CELL,
        "G": G_GROUPS, "k_tau": K_TAU, "k_latent": m.K_LATENT, "dim": m.DIM,
        "phi_slow": PHI_SLOW, "n_occ": N_OCC, "w_int_arm": W_INT_ARM,
        "n_restart": N_RESTART,
        "grain": {"analysis_grain": "world (8 independent world blocks per cell)",
                  "rule5_justification": "every registered statistic is a per-world "
                  "scalar (ARI, a boundary rate, a variance share); the paired "
                  "world-block bootstrap over the 8 worlds is the only resampling "
                  "unit that is independent, and the 4-world pilot MDEs below are "
                  "computed at that grain (rule-16 convention: >=4 pilot worlds)"},
    }
    stage_times: dict[str, float] = {}

    # ---- RN-10: the Delta choice (pure prediction stream; no world exists yet)
    t = time.time()
    ds = delta_search(DELTA_TARGET_ARI0)
    delta = ds["delta"]
    stage_times["delta_search"] = time.time() - t
    gates["delta_rule"] = {
        "rule": "RN-10", "target_pred_ari_rho0": DELTA_TARGET_ARI0,
        "guard_pred_ari_rho0": DELTA_GUARD_ARI0, "delta_chosen": delta,
        "sigma_tau2": SIGMA_TAU2_PER_DELTA2 * delta * delta,
        "identity_only_z_iso": {
            f"{r:g}": identity_only_z(m.K_LATENT, r) for r in RHO_LEVELS},
        "identity_only_z_aligned": {
            f"{r:g}": identity_only_z(K_TAU, r) for r in RHO_LEVELS},
        "identity_only_floor_iso": {
            f"{r:g}": 0.5 * math.erfc(identity_only_z(m.K_LATENT, r) / math.sqrt(2.0))
            if r > 0 else 0.0 for r in RHO_LEVELS},
        "identity_only_floor_aligned": {
            f"{r:g}": 0.5 * math.erfc(identity_only_z(K_TAU, r) / math.sqrt(2.0))
            if r > 0 else 0.0 for r in RHO_LEVELS},
        "search": ds,
    }

    # ---- G4L: the Part-0 predictions, computed BEFORE any arm
    t = time.time()
    pred_rows = []
    for geom, rho, variant in all_cells():
        pred = predict_cell(delta, rho, geom, variant,
                            PRED_REPS_ORACLE if variant == "ambient" else PRED_REPS_INSTRUMENT,
                            False)
        pred_i = predict_cell(delta, rho, geom, variant, PRED_REPS_INSTRUMENT, True)
        pop = pred_population(delta, rho, geom, pred_seed(0))
        pred_rows.append({
            "cell": cell_id(geom, rho, variant), "geometry": geom, "rho_id": rho,
            "variant": variant, "delta": delta,
            "sigma_b2": sigma_b2_of(delta, rho),
            "sigma_b2_over_delta2": sigma_b2_of(delta, rho) / (delta * delta),
            "identity_energy_projected_fraction": K_TAU / m.K_LATENT if geom == "ISO" else 1.0,
            **pred,
            "pred_ari_instrument": pred_i["pred_ari_instrument"],
            "pred_ari_instrument_sd": pred_i["pred_ari_instrument_sd"],
            "pred_ari_spectral": pred_i["pred_ari_spectral"],
            "pred_boundary_floor": (
                0.0 if rho <= 0.0 else
                0.5 * math.erfc(identity_only_z(m.K_LATENT if geom == "ISO" else K_TAU, rho)
                                / math.sqrt(2.0))),
            "identity_only_z": identity_only_z(
                m.K_LATENT if geom == "ISO" else K_TAU, rho),
            "n_pred_authors": int(pop["card"].shape[0]),
        })
    preds = pd.DataFrame(pred_rows)
    preds.to_csv(OUT / "part0_predictions.csv", index=False)
    stage_times["predictions"] = time.time() - t
    amb = preds[preds["variant"] == "ambient"]
    iso = amb[amb["geometry"] == "ISO"].sort_values("rho_id")
    gates["G4L"] = {
        "pass": True,
        "artifact": "part0_predictions.csv",
        "derivation": (
            "R2 card-space geometry: c_i = M(tau_g + b_i) + w_slow*M s_bar_i + "
            "w_noise*e_bar_i with M = A_SCALE * L diag(G_PROFILE) (f2:196/k2a:210), "
            "Var(s_bar) = k2a.ar_mean_var(8,.90) and the observation term "
            "SIGMA_ISO^2/(n_occ*n_rep) -- K2a's validated algebra.  The predicted "
            "per-cell ARI is the nearest-TRUE-centroid (oracle) ARI of that law, "
            "averaged over independent replicate populations on the 'm4l1-pred' "
            "stream.  Identity enters the boundary-normal variance with its FULL "
            "energy/48 (ISO) or energy/3 (ALIGNED) -- R2's (k_tau/m) reduction is "
            "the ENERGY statement; the per-boundary floor is Phi(-Delta/(2 "
            "sigma_{b,u})) and is DELTA-FREE in this parameterization."),
        "predicted_iso_ordering": list(iso["cell"]),
        "predicted_iso_ari": [float(v) for v in iso["pred_ari_oracle"]],
        "predicted_iso_strictly_decreasing": bool(
            all(a > b for a, b in zip(iso["pred_ari_oracle"], iso["pred_ari_oracle"][1:],
                                      strict=False))),
        "predicted_full_ordering": list(
            amb.sort_values("pred_ari_oracle", ascending=False)["cell"]),
    }

    # ---- G0L / G1L / G2L on the RESERVED pilot worlds
    t = time.time()
    cells = all_cells()
    pilot_rows = []
    g0: dict[str, Any] = {"recon_residual_max": 0.0, "rho_id_dev_abs_max": 0.0,
                          "delta_latent_dev_abs_max": 0.0, "per_world": [],
                          "removal_equals_rho0_residual_max": 0.0,
                          "iso_aligned_rho0_residual_max": 0.0,
                          "ari_vs_sklearn_max_abs": 0.0,
                          "pca_grand_mean_norm_max": 0.0}
    g1: dict[str, Any] = {"per_world": []}
    for world in PILOT_WORLDS:
        wseed = world_seed_for(world)
        world_obj, typ = build_typed_world(wseed, N_AUTHORS)
        w = m.arm_weights(W_INT_ARM)
        # G0L (i): exact five-channel reconstruction with the TYPED trait
        trait = typed_trait(world_obj, typ, "ISO", delta, 0.55)
        w2 = dict(world_obj)
        w2["trait"] = trait
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
        # G0L (ii): the designed coincidences
        c_iso0 = cards_for_variant(world_obj, typ, "ISO", delta, 0.0, "ambient")["full"]
        c_ali0 = cards_for_variant(world_obj, typ, "ALIGNED", delta, 0.0, "ambient")["full"]
        g0["iso_aligned_rho0_residual_max"] = max(
            g0["iso_aligned_rho0_residual_max"], float(np.abs(c_iso0 - c_ali0).max()))
        for geom in GEOMETRIES:
            crem = cards_for_variant(world_obj, typ, geom, delta, COMPANION_RHO,
                                     "removal")["full"]
            g0["removal_equals_rho0_residual_max"] = max(
                g0["removal_equals_rho0_residual_max"], float(np.abs(crem - c_iso0).max()))
        # G1L (rule 10): non-degeneracy of the type channel and of the geometries
        base = cards_for_variant(world_obj, typ, "ISO", delta, 0.55, "ambient")["full"]
        no_type = m.card(centred_with_trait(
            world_obj, typed_trait(world_obj, typ, "ISO", delta, 0.55, drop_type=True)),
            w, np.arange(N_OCC), (0, 1), True)
        ali = cards_for_variant(world_obj, typ, "ALIGNED", delta, 0.55, "ambient")["full"]
        g1["per_world"].append({
            "world": world,
            "rms_card_change_drop_type": float(np.sqrt(np.mean((base - no_type) ** 2))),
            "rms_card_change_iso_vs_aligned": float(np.sqrt(np.mean((base - ali) ** 2))),
            "rms_card_change_rho0_vs_rho55_iso": float(np.sqrt(np.mean((base - c_iso0) ** 2))),
            "rms_card_change_rho0_vs_rho55_aligned": float(np.sqrt(np.mean((ali - c_ali0) ** 2))),
            "rms_card_change_iso_vs_aligned_at_rho0": float(
                np.sqrt(np.mean((c_iso0 - c_ali0) ** 2))),
        })
        rows = [measure_cell_world(world_obj, typ, g, delta, r, v, wseed) for g, r, v in cells]
        for row in rows:
            row["world"] = world
            g0["rho_id_dev_abs_max"] = max(
                g0["rho_id_dev_abs_max"], abs(row["realized_rho_id"] - row["rho_id"]))
            g0["delta_latent_dev_abs_max"] = max(
                g0["delta_latent_dev_abs_max"],
                max(abs(row["realized_delta_latent_min"] - delta),
                    abs(row["realized_delta_latent_max"] - delta)))
            g0["pca_grand_mean_norm_max"] = max(
                g0["pca_grand_mean_norm_max"], row["pca_grand_mean_norm"])
        pilot_rows.extend(rows)
        g0["per_world"].append({"world": world, "world_seed": wseed,
                                "recon_residual": recon})
    pilot = pd.DataFrame(pilot_rows)
    pilot.to_csv(OUT / "part0_pilot_cells.csv", index=False)
    stage_times["pilot"] = time.time() - t

    # G0L (iii): the K2a anchor cell, re-derived bit-exactly from k2a's own path
    t = time.time()
    a_phi, a_occ, a_arm = 0.9, 8, "zero"
    a_cid = m.cell_id(a_phi, a_occ, a_arm)
    persisted = m.read_csv_rt(K2A_OUT / f"cell_{a_cid}.csv")
    rederived = pd.concat(
        [m.suff_stats_for_world(m.world_seed_for(a_phi, a_occ, wi), a_phi, a_occ, a_arm,
                                m.N_AUTHORS)
         for wi in range(m.WORLDS_PER_CELL)], ignore_index=True)
    shared = [c for c in persisted.columns if c in rederived.columns]
    diffs = {c: float(np.max(np.abs(persisted[c].to_numpy(float)
                                    - rederived[c].to_numpy(float)))) for c in shared}
    g0["k2a_anchor"] = {
        "cell": a_cid, "rows": int(len(persisted)), "columns_compared": len(shared),
        "max_abs_residual": float(max(diffs.values())),
        "bit_exact": bool(max(diffs.values()) == 0.0),
        "rho_contiguous_persisted": float(
            m.read_csv_rt(K2A_OUT / "cells.csv").query("cell == @a_cid")["rho_contiguous"].iloc[0]),
        "gap_persisted": float(
            m.read_csv_rt(K2A_OUT / "cells.csv").query("cell == @a_cid")["gap"].iloc[0]),
    }
    # G0L (iv): the in-leg ARI against sklearn's reference implementation
    try:
        from sklearn.metrics import adjusted_rand_score
        rng_chk = np.random.default_rng(MASTER_SEED)
        worst = 0.0
        for _ in range(64):
            a = rng_chk.integers(0, G_GROUPS, size=512)
            b = rng_chk.integers(0, G_GROUPS, size=512)
            worst = max(worst, abs(adjusted_rand_index(a, b) - adjusted_rand_score(a, b)))
        g0["ari_vs_sklearn_max_abs"] = float(worst)
        g0["ari_reference"] = "sklearn.metrics.adjusted_rand_score, 64 random label pairs"
    except Exception as exc:                                    # pragma: no cover
        g0["ari_reference"] = f"UNAVAILABLE: {exc}"
    stage_times["anchor"] = time.time() - t
    g0["criterion"] = ("reconstruction residual <= 1e-12 AND the K2a anchor cell "
                       "bit-exact AND |realized rho_id - designed| <= 0.02 AND all six "
                       "realized latent separations equal Delta to <= 1e-9 AND the ARI "
                       "implementation agrees with sklearn to <= 1e-12")
    g0["pass"] = bool(g0["recon_residual_max"] <= 1e-12 and g0["k2a_anchor"]["bit_exact"]
                      and g0["rho_id_dev_abs_max"] <= 0.02
                      and g0["delta_latent_dev_abs_max"] <= 1e-9
                      and g0["ari_vs_sklearn_max_abs"] <= 1e-12)
    g1["min_rms_drop_type"] = float(min(r["rms_card_change_drop_type"] for r in g1["per_world"]))
    g1["min_rms_iso_vs_aligned"] = float(
        min(r["rms_card_change_iso_vs_aligned"] for r in g1["per_world"]))
    g1["min_rms_rho0_vs_rho55"] = float(min(
        min(r["rms_card_change_rho0_vs_rho55_iso"], r["rms_card_change_rho0_vs_rho55_aligned"])
        for r in g1["per_world"]))
    g1["max_rms_iso_vs_aligned_at_rho0"] = float(
        max(r["rms_card_change_iso_vs_aligned_at_rho0"] for r in g1["per_world"]))
    g1["criterion"] = ("rule 10: the type channel changes the card panel; ISO and "
                       "ALIGNED differ at rho_id>0; b=0 arms differ from b>0 arms "
                       "(all RMS > 1e-6).  The ISO==ALIGNED coincidence AT rho_id=0 is "
                       "a DESIGNED identity (same xi, zero scale) and is reported as an "
                       "exact 0, not used as a gate input")
    g1["pass"] = bool(g1["min_rms_drop_type"] > 1e-6 and g1["min_rms_iso_vs_aligned"] > 1e-6
                      and g1["min_rms_rho0_vs_rho55"] > 1e-6)
    gates["G0L"], gates["G1L"] = g0, g1

    # ---- G2L: rule 3 liveness + rule 17 realizability
    pmean = pilot[pilot["variant"] == "ambient"].groupby("cell", sort=False).agg(
        {"ari_primary": "mean", "ari_spectral": "mean", "eigengap_ratio": "mean",
         "eigengap_abs": "mean", "rho_id": "first", "geometry": "first"}).reset_index()
    mid = pmean[pmean["rho_id"].isin(MID_RHOS)]
    band_ok = {r["cell"]: bool(BAND[0] < r["ari_primary"] < BAND[1]) for _, r in mid.iterrows()}
    saturated = {r["cell"]: bool(r["ari_primary"] >= SATURATION[1]
                                 or r["ari_primary"] <= SATURATION[0])
                 for _, r in pmean.iterrows()}
    ladder_trigger = any(saturated.values())
    g2: dict[str, Any] = {
        "pilot_cell_ari": {r["cell"]: float(r["ari_primary"]) for _, r in pmean.iterrows()},
        "pilot_cell_ari_spectral": {r["cell"]: float(r["ari_spectral"])
                                    for _, r in pmean.iterrows()},
        "eigengap_ratio": {r["cell"]: float(r["eigengap_ratio"]) for _, r in pmean.iterrows()},
        "eigengap_abs": {r["cell"]: float(r["eigengap_abs"]) for _, r in pmean.iterrows()},
        "min_eigengap_ratio": float(pmean["eigengap_ratio"].min()),
        "min_eigengap_abs": float(pmean["eigengap_abs"].min()),
        "band": list(BAND), "saturation_band": list(SATURATION),
        "mid_cells_in_band": band_ok,
        "mid_cells_in_band_count": int(sum(band_ok.values())),
        "any_cell_saturated": bool(ladder_trigger),
        "saturated_cells": [c for c, v in saturated.items() if v],
        "ladder_fired": False,
        "ladder_step_refused": False,
        "delta_final": delta,
    }
    if ladder_trigger:
        floored = [c for c, v in saturated.items()
                   if v and g2["pilot_cell_ari"][c] <= SATURATION[0]]
        factor = 1.5 if floored else (1.0 / 1.5)
        cand = delta * factor
        guard = predict_cell(cand, 0.0, "ISO", "ambient", DELTA_BISECT_REPS, False)
        g2["ladder_candidate_delta"] = cand
        g2["ladder_candidate_pred_ari_rho0"] = guard["pred_ari_oracle"]
        if guard["pred_ari_oracle"] >= DELTA_GUARD_ARI0:
            g2["ladder_fired"] = True
            g2["delta_final"] = cand
        else:
            g2["ladder_step_refused"] = True
    g2["band_clause_failures_from_above"] = [
        c for c, ok in band_ok.items() if not ok and g2["pilot_cell_ari"][c] >= BAND[1]]
    g2["band_clause_failures_from_below"] = [
        c for c, ok in band_ok.items() if not ok and g2["pilot_cell_ari"][c] <= BAND[0]]
    g2["rule11_band_vs_V1_unsatisfiability_proof"] = (
        "identity-only boundary z is Delta-free: ISO 5.65685/sqrt(rho/(1-rho)) "
        "(<= 3.266 at rho=.75 -> per-boundary floor <= 5.5e-4), ALIGNED "
        "1.41421/sqrt(rho/(1-rho)).  An ISO mid cell can only be pushed under "
        "ARI 0.95 by the rho-INDEPENDENT state/observation channel, which "
        "depresses the rho_id=0 cell by very nearly the same amount; the two "
        "registered clauses therefore share a vanishing feasible window in Delta.")
    g2["criterion"] = ("rule 3: every registered knob is live (the type channel, both "
                       "geometries and every rho_id level change the card panel -- G1L) "
                       "and the type subspace is estimable (top-k_tau eigengap > 0 in "
                       "every cell).  rule 17: no main cell saturated at ARI 0 or 1 in "
                       "the pilot; the registered (0.05,0.95) band clause is evaluated "
                       "and reported on all four mid cells, with RN-10's guard")
    g2["pass"] = bool(g2["min_eigengap_abs"] > 0.0 and not g2["any_cell_saturated"])
    gates["G2L"] = g2
    if g2["ladder_fired"]:
        (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n",
                                        encoding="utf-8")
        raise SystemExit(
            "LADDER FIRED (RN-10 step iii): Delta -> "
            f"{g2['delta_final']!r}.  Part 0 must be re-run in full at the new Delta "
            "so that every prediction, pilot gate and MDE is computed at the Delta the "
            "arms will use; the fired step and both Part-0 passes are disclosed in the "
            "report.  Pin DELTA_LADDER_OVERRIDE and re-run --stage part0.")

    # ---- G3L: 4-world pilot MDEs, rule-11 satisfiability, rule-13 spec
    t = time.time()
    g3: dict[str, Any] = {"b_draws": B_BOOT, "seed": MASTER_SEED,
                          "b_draws_stability": B_BOOT_HIGH,
                          "pilot_worlds": len(PILOT_WORLDS), "clauses": []}

    def mde(sd: float, n: int) -> float:
        df = len(PILOT_WORLDS) - 1
        return (float(student_t.ppf(0.975, df)) + float(student_t.ppf(0.80, df))) * sd / math.sqrt(n)

    pw = pilot.pivot_table(index="world", columns="cell", values="ari_primary")
    aud = pilot.pivot_table(index="world", columns="cell", values="audit_S_id")
    audd = pilot.pivot_table(index="world", columns="cell", values="audit_share_b_design")
    bt = pilot.pivot_table(index="world", columns="cell", values="boundary_err_true_card")
    for geom in GEOMETRIES:
        for rho in RHO_LEVELS:
            cid = cell_id(geom, rho, "ambient")
            sd = float(pw[cid].std(ddof=1))
            g3["clauses"].append({
                "clause": f"ARI {cid}", "pilot_mean": float(pw[cid].mean()),
                "pilot_sd_world": sd, "mde_main": mde(sd, WORLDS_PER_CELL),
                "direction": "two-sided (CI must CONTAIN the Part-0 prediction)"})
            sda = float(aud[cid].std(ddof=1))
            g3["clauses"].append({
                "clause": f"audit S_id {cid}", "pilot_mean": float(aud[cid].mean()),
                "pilot_design_mean": float(audd[cid].mean()),
                "pilot_sd_world": sda, "mde_main": mde(sda, WORLDS_PER_CELL),
                "direction": ("two-sided equivalence within margin (rho_id=0)" if rho == 0
                              else "two-sided (CI must CONTAIN the designed b-share)")})
            if geom == "ALIGNED" and rho in MID_RHOS:
                sdb = float(bt[cid].std(ddof=1))
                g3["clauses"].append({
                    "clause": f"floor rate {cid}", "pilot_mean": float(bt[cid].mean()),
                    "pilot_sd_world": sdb, "mde_main": mde(sdb, WORLDS_PER_CELL),
                    "direction": "two-sided (CI must CONTAIN Phi(-Delta/(2 sigma_bu)))"})
    # V-4's rho_id=0 margin, from the pilot (registration: "margin from pilot")
    margins = {}
    for geom in GEOMETRIES:
        cid = cell_id(geom, 0.0, "ambient")
        margins[cid] = mde(float(aud[cid].std(ddof=1)), WORLDS_PER_CELL)
    g3["v4_null_margin"] = margins
    g3["v4_null_margin_used"] = float(max(margins.values()))
    # rule-11 satisfiability, with directions
    iso55, ali55 = cell_id("ISO", 0.55, "ambient"), cell_id("ALIGNED", 0.55, "ambient")
    iso0 = cell_id("ISO", 0.0, "ambient")
    def _pred(cid: str, key: str = "pred_ari_oracle") -> float:
        return float(preds[preds["cell"] == cid][key].iloc[0])
    pooled_pred = 0.5 * sum(
        _pred(cell_id("ALIGNED", r, "ambient")) - _pred(cell_id("ISO", r, "ambient"))
        for r in MID_RHOS)
    sd_diff = float((pw[cell_id("ALIGNED", 0.35, "ambient")]
                     - pw[cell_id("ISO", 0.35, "ambient")]).std(ddof=1))
    proj_iso = (_pred(cell_id("ISO", 0.55, "projection"), "pred_ari_instrument")
                - _pred(iso55, "pred_ari_instrument"))
    def_iso = _pred(iso0, "pred_ari_instrument") - _pred(iso55, "pred_ari_instrument")
    proj_ali = (_pred(cell_id("ALIGNED", 0.55, "projection"), "pred_ari_instrument")
                - _pred(ali55, "pred_ari_instrument"))
    def_ali = _pred(iso0, "pred_ari_instrument") - _pred(ali55, "pred_ari_instrument")
    g3["rule11"] = {
        "V-1": {"satisfiable": bool(float(pw[iso0].mean())
                                    - 3.0 * float(pw[iso0].std(ddof=1)) > V1_ARI_BAR),
                "pilot_mean": float(pw[iso0].mean()),
                "pilot_sd_world": float(pw[iso0].std(ddof=1)),
                "bar": V1_ARI_BAR, "direction": "one-sided lower, per world, 8/8"},
        "V-2": {"satisfiable": True,
                "note": "containment of a Part-0 point prediction by a bootstrap CI; "
                        "satisfiable whenever the CI has positive width",
                "predicted_iso_ordering_strict": gates["G4L"]["predicted_iso_strictly_decreasing"],
                "direction": "two-sided containment + exact ordering"},
        "V-3a": {"predicted_pooled_diff": pooled_pred,
                 "pilot_sd_world_of_diff": sd_diff,
                 "z_predicted": abs(pooled_pred) / max(sd_diff / math.sqrt(WORLDS_PER_CELL), 1e-18),
                 "satisfiable": bool(abs(pooled_pred)
                                     > 1.96 * sd_diff / math.sqrt(WORLDS_PER_CELL)),
                 "direction": "one-sided lower (ALIGNED - ISO < 0), CI excluding 0"},
        "V-3b": {"satisfiable": True,
                 "direction": "two-sided containment of Phi(-Delta/(2 sigma_bu)) by the "
                              "TRUE-CARD per-boundary rate CI"},
        "V-3c": {"predicted_iso_restoration": proj_iso, "predicted_iso_deficit": def_iso,
                 "predicted_iso_fraction": proj_iso / def_iso if def_iso != 0 else float("nan"),
                 "bar_iso": V3_PROJ_ISO_FRAC,
                 "predicted_aligned_restoration": proj_ali,
                 "predicted_aligned_deficit": def_ali,
                 "predicted_aligned_fraction": proj_ali / def_ali if def_ali != 0 else float("nan"),
                 "bar_aligned": V3_PROJ_ALIGNED_FRAC,
                 "satisfiable": True,
                 "prediction": ("PREDICTED MISS on the ISO half: R2's (k_tau/m) reduction "
                                "is an ENERGY statement, and at rho_id=.55 the ambient "
                                "energy condition Delta^2 >~ sigma_b^2 + noise ALREADY "
                                "holds (sigma_b^2/Delta^2 = 0.4583), so the ISO deficit is "
                                "boundary-normal Bayes error, which projection onto S "
                                "cannot touch"),
                 "direction": "one-sided (ISO fraction >= 1/2; ALIGNED fraction <= 1/4)"},
        "V-3d": {"satisfiable": True,
                 "note": "oracle REMOVAL reproduces the rho_id=0 card EXACTLY by "
                         "construction (G0L residual); the clause is a designed identity, "
                         "disclosed as such",
                 "direction": "one-sided lower, ARI >= 0.95"},
        "V-4": {"satisfiable": True, "null_margin": g3["v4_null_margin_used"],
                "direction": "two-sided equivalence at rho_id=0; two-sided containment "
                             "of the designed b-share elsewhere"},
    }
    g3["pass"] = bool(g3["rule11"]["V-1"]["satisfiable"] and g3["rule11"]["V-3a"]["satisfiable"])
    g3["criterion"] = ("every registered interval clause has a 4-world pilot MDE at the "
                       "main-design grain, a stated direction, and an arithmetic "
                       "satisfiability check under the pilot statistics (rule 11); the "
                       "rule-13 spec is B=2000 at seed=master_seed with a >=10xB recheck "
                       "at any clause whose boundary lies within 2 Monte-Carlo endpoint "
                       "sds of the estimate")
    gates["G3L"] = g3
    stage_times["power"] = time.time() - t

    # ---- G5L: hygiene + rule 16 + rule 14
    layer_a, layer_b, enum_audit = build_enumeration()
    layer_a.to_csv(OUT / "part0_enumeration_leans.csv", index=False)
    layer_b.to_csv(OUT / "part0_enumeration_routing.csv", index=False)
    gates["G5L"] = {
        "pass": bool(enum_audit["layer_a_no_gap_no_overlap"]
                     and enum_audit["layer_b_no_gap_no_overlap"]),
        "round_trip_parsing_everywhere": True, "float_precision": "round_trip",
        "enumeration": enum_audit,
        "rule14_self_check": (
            "CARD SPACE ONLY.  V-1/V-2/V-3a/V-3c/V-3d compare ARI to ARI; V-3b "
            "compares a card-space per-boundary misassignment RATE to the closed-form "
            "rate Phi(-Delta/(2 sigma_{b,u})); V-4 compares a normalized variance SHARE "
            "to a normalized variance SHARE.  No gate and no lean crosses scales or "
            "instruments, so rule 14 has nothing to bind."),
        "rule12_source_objects": {
            "expressive world (slow/common/noise/loadings)":
                "scripts/run_suica_m4_k2a_expressive_world.py:184-236 build_world, called",
            "channel weights": "k2a:129-138 arm_weights('zero'), called",
            "author centring": "k2a:250-259 centered_channels, called",
            "the card (full and half)": "k2a:262-276 card, called",
            "canonical splits": "k2a:335-340 splits, called",
            "AR algebra": "k2a:282-300 ar_mean_var/ar_set_var/ar_cross_cov, called",
            "K2a anchor re-derivation": "k2a:417-454 suff_stats_for_world + k2a:158-168 "
                                        "world_seed_for, called",
            "round-trip parser / CI / MC-sd": "k2a:118-120, k2a:519-521, k2a:524-532, called",
            "latent->64 map": "scripts/run_suica_m4_f2_composition.py:196 (mirrored at "
                              "this script's typed_trait, via k2a's own loadings)",
            "mean_part": "scripts/run_suica_m4_f2_composition.py:178 (the TYPE LAYER "
                         "replaces its latent z by tau_{g(i)} + b_i)",
            "NEW in this leg": "this script -- TETRAHEDRON, type_geometry, "
                               "latent_type_vectors, latent_identity, typed_trait, "
                               "card_space_type_basis, cards_for_variant, kmeans_lloyd, "
                               "spectral_labels, adjusted_rand_index, hungarian_accuracy, "
                               "boundary_error_rate, predicted_boundary_error, "
                               "audit_meter, pred_population, predict_cell, delta_search",
        },
    }
    gates["part0_all_pass"] = bool(gates["G0L"]["pass"] and gates["G1L"]["pass"]
                                   and gates["G2L"]["pass"] and gates["G3L"]["pass"]
                                   and gates["G4L"]["pass"] and gates["G5L"]["pass"])
    gates["delta_final"] = delta
    gates["stage_seconds"] = stage_times
    gates["stage_seconds"]["part0_total"] = time.time() - t0
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n",
                                    encoding="utf-8")
    write_part0_tables(gates, preds, pilot)
    write_manifest({"part0": time.time() - t0}, {"delta": delta})
    print(json.dumps({
        "stage": "part0", "seconds": round(time.time() - t0, 3),
        "delta": delta, "part0_all_pass": gates["part0_all_pass"],
        "G0L": gates["G0L"]["pass"], "G1L": gates["G1L"]["pass"],
        "G2L": gates["G2L"]["pass"], "G3L": gates["G3L"]["pass"],
        "G4L": gates["G4L"]["pass"], "G5L": gates["G5L"]["pass"],
        "recon_residual_max": gates["G0L"]["recon_residual_max"],
        "k2a_anchor_bit_exact": gates["G0L"]["k2a_anchor"]["bit_exact"],
        "pilot_cell_ari": gates["G2L"]["pilot_cell_ari"],
        "mid_cells_in_band": gates["G2L"]["mid_cells_in_band"],
        "stage_seconds": stage_times,
    }, indent=2, default=str))


def write_part0_tables(gates: dict[str, Any], preds: pd.DataFrame,
                       pilot: pd.DataFrame) -> None:
    lines: list[str] = []
    lines.append("### G4L Part-0 predictions (all 14 cells, computed before any arm)\n")
    lines.append("| cell | geom | rho_id | variant | sigma_b^2/Delta^2 | pred ARI (R2 oracle) "
                 "| sd | pred ARI (instrument) | pred ARI (spectral) | per-boundary floor |")
    lines.append("|---|---|---:|---|---:|---:|---:|---:|---:|---:|")
    for _, r in preds.iterrows():
        lines.append(
            f"| `{r['cell']}` | {r['geometry']} | {r['rho_id']:g} | {r['variant']} | "
            f"{r['sigma_b2_over_delta2']:.10f} | {r['pred_ari_oracle']:.10f} | "
            f"{r['pred_ari_oracle_sd']:.10f} | {r['pred_ari_instrument']:.10f} | "
            f"{r['pred_ari_spectral']:.10f} | {r['pred_boundary_floor']:.10f} |")
    lines.append("\n### G2L pilot cells (RESERVED worlds 9901-9904)\n")
    lines.append("| cell | pilot ARI (PRIMARY) | pilot ARI (spectral) | eigengap ratio | "
                 "in band | saturated |")
    lines.append("|---|---:|---:|---:|---|---|")
    g2 = gates["G2L"]
    for cell, val in g2["pilot_cell_ari"].items():
        lines.append(
            f"| `{cell}` | {val:.10f} | {g2['pilot_cell_ari_spectral'][cell]:.10f} | "
            f"{g2['eigengap_ratio'][cell]:.6f} | "
            f"{g2['mid_cells_in_band'].get(cell, '-')} | "
            f"{cell in g2['saturated_cells']} |")
    lines.append("\n### G3L pilot MDEs (4 pilot worlds -> main design n=8)\n")
    lines.append("| clause | pilot mean | pilot sd (world) | MDE at n=8 | direction |")
    lines.append("|---|---:|---:|---:|---|")
    for c in gates["G3L"]["clauses"]:
        lines.append(f"| {c['clause']} | {c['pilot_mean']:.10f} | {c['pilot_sd_world']:.10f} "
                     f"| {c['mde_main']:.10f} | {c['direction']} |")
    lines.append("\n### G1L rule-10 non-degeneracy (card-panel RMS)\n")
    lines.append("| world | drop type | ISO vs ALIGNED (rho .55) | rho0 vs rho.55 ISO | "
                 "rho0 vs rho.55 ALIGNED | ISO vs ALIGNED AT rho0 (designed 0) |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for r in gates["G1L"]["per_world"]:
        lines.append(f"| {r['world']} | {r['rms_card_change_drop_type']:.8e} | "
                     f"{r['rms_card_change_iso_vs_aligned']:.8e} | "
                     f"{r['rms_card_change_rho0_vs_rho55_iso']:.8e} | "
                     f"{r['rms_card_change_rho0_vs_rho55_aligned']:.8e} | "
                     f"{r['rms_card_change_iso_vs_aligned_at_rho0']:.3e} |")
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
    delta = float(gates["delta_final"])
    t0 = time.time()
    wanted = set(args.cells.split(",")) if args.cells else None
    cells = [c for c in all_cells() if wanted is None or cell_id(*c) in wanted]
    rows: list[dict[str, Any]] = []
    for world in range(WORLDS_PER_CELL):
        rows.extend([{**r, "world": world} for r in run_world_cells(world, delta, cells)])
        print(f"  world {world}: {len(cells)} cells  ({time.time() - t0:.1f}s)")
    frame = pd.DataFrame(rows)
    for cid, sub in frame.groupby("cell", sort=False):
        sub.to_csv(OUT / f"cell_{cid}.csv", index=False)
    write_manifest({f"arms[{len(cells)} cells]": time.time() - t0}, {})
    print(json.dumps({"stage": "arms", "cells": [cell_id(*c) for c in cells],
                      "rows": int(len(frame)),
                      "seconds": round(time.time() - t0, 3)}, indent=2))


# ---------------------------------------------------------------------------
# Stage: finalize

def _boot_index(b_draws: int, seed: int, n_blocks: int) -> np.ndarray:
    """RN-13: ONE paired world-block resample, applied identically to EVERY
    cell (the cells share their worlds bit-for-bit, so every cross-cell
    contrast is paired inside the bootstrap)."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, n_blocks, size=(b_draws, n_blocks))


def run_finalize(args: argparse.Namespace) -> None:
    gates = require_part0()
    m = k2a()
    t0 = time.time()
    delta = float(gates["delta_final"])
    preds = m.read_csv_rt(OUT / "part0_predictions.csv")
    frames = {}
    for geom, rho, variant in all_cells():
        cid = cell_id(geom, rho, variant)
        path = OUT / f"cell_{cid}.csv"
        if not path.exists():
            raise SystemExit(f"REFUSED: missing arm artifact {path}")
        frames[cid] = m.read_csv_rt(path).sort_values("world").reset_index(drop=True)
    n_blocks = WORLDS_PER_CELL
    idx = _boot_index(B_BOOT, MASTER_SEED, n_blocks)
    idx_hi = _boot_index(B_BOOT_HIGH, MASTER_SEED, n_blocks)

    def vals(cid: str, key: str) -> np.ndarray:
        return frames[cid][key].to_numpy(float)

    def boot(cid: str, key: str, index: np.ndarray) -> np.ndarray:
        return vals(cid, key)[index].mean(axis=1)

    def pred_of(cid: str, key: str) -> float:
        return float(preds[preds["cell"] == cid][key].iloc[0])

    # ---- per-cell table
    rows = []
    for geom, rho, variant in all_cells():
        cid = cell_id(geom, rho, variant)
        row: dict[str, Any] = {"cell": cid, "geometry": geom, "rho_id": rho,
                               "variant": variant, "delta": delta,
                               "n_worlds": int(len(frames[cid]))}
        for key in ("ari_primary", "ari_spectral", "acc_primary", "acc_spectral",
                    "ari_oracle_centroid", "boundary_err_true_card",
                    "boundary_err_full_card", "audit_S_id",
                    "audit_S_id_contiguous_reading", "audit_share_b_design",
                    "audit_rho_interleaved", "audit_rho_contiguous", "audit_gap",
                    "audit_B_hat", "eigengap_ratio", "realized_rho_id",
                    "realized_delta_card_mean", "card_var_norm"):
            b = boot(cid, key, idx)
            lo, hi = m.ci_of(b)
            row[key] = float(vals(cid, key).mean())
            row[f"{key}_lo"], row[f"{key}_hi"] = lo, hi
            row[f"{key}_se"] = float(np.std(b, ddof=1))
        row["ari_primary_min_world"] = float(vals(cid, "ari_primary").min())
        row["ari_primary_worlds_ge_bar"] = int((vals(cid, "ari_primary") >= V1_ARI_BAR).sum())
        row["pred_ari_oracle"] = pred_of(cid, "pred_ari_oracle")
        row["pred_ari_instrument"] = pred_of(cid, "pred_ari_instrument")
        row["pred_ari_spectral"] = pred_of(cid, "pred_ari_spectral")
        row["ari_contains_pred_oracle"] = bool(
            row["ari_primary_lo"] <= row["pred_ari_oracle"] <= row["ari_primary_hi"])
        row["ari_contains_pred_instrument"] = bool(
            row["ari_primary_lo"] <= row["pred_ari_instrument"] <= row["ari_primary_hi"])
        row["pred_boundary_floor_realized"] = float(
            vals(cid, "boundary_err_pred_floor").mean())
        row["pred_boundary_full_realized"] = float(
            vals(cid, "boundary_err_pred_full").mean())
        row["floor_contains_pred"] = bool(
            row["boundary_err_true_card_lo"] <= row["pred_boundary_floor_realized"]
            <= row["boundary_err_true_card_hi"])
        row["full_rate_contains_pred"] = bool(
            row["boundary_err_full_card_lo"] <= row["pred_boundary_full_realized"]
            <= row["boundary_err_full_card_hi"])
        # V-4 tracking: does the CI of the meter contain the designed b-share?
        d_boot = boot(cid, "audit_S_id", idx) - boot(cid, "audit_share_b_design", idx)
        lo, hi = m.ci_of(d_boot)
        row["audit_S_minus_design"] = float(
            (vals(cid, "audit_S_id") - vals(cid, "audit_share_b_design")).mean())
        row["audit_S_minus_design_lo"], row["audit_S_minus_design_hi"] = lo, hi
        row["audit_S_minus_design_se"] = float(np.std(d_boot, ddof=1))
        row["audit_tracks_design"] = bool(lo <= 0.0 <= hi)
        rows.append(row)
    cells_df = pd.DataFrame(rows)
    cells_df.to_csv(OUT / "cells.csv", index=False)
    by = {r["cell"]: r for r in rows}

    stability: list[dict[str, Any]] = []

    def rule13(cid: str, clause: str, arr: np.ndarray, arr_hi: np.ndarray,
               boundary: float, kind: str, verdict: bool) -> bool:
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
            return verdict == v2
        return True

    # ---- V-1
    v1_sub = {}
    for geom in GEOMETRIES:
        cid = cell_id(geom, 0.0, "ambient")
        v1_sub[geom] = {
            "cell": cid, "worlds_ge_bar": by[cid]["ari_primary_worlds_ge_bar"],
            "min_world_ari": by[cid]["ari_primary_min_world"],
            "mean_ari": by[cid]["ari_primary"],
            "state": "HOLD" if by[cid]["ari_primary_worlds_ge_bar"] == WORLDS_PER_CELL else "MISS"}
    v1 = {"prior": 0.85, "bar": V1_ARI_BAR, "subclauses": v1_sub,
          "note": "the two rho_id=0 cells are BIT-IDENTICAL panels by construction "
                  "(same xi at zero scale; G0L residual reported), so this is 8 "
                  "distinct worlds scored twice -- disclosed, not hidden",
          "state": lean_from_subclauses(tuple(v["state"] for v in v1_sub.values()))}

    # ---- V-2
    iso_cells = [cell_id("ISO", r, "ambient") for r in RHO_LEVELS]
    iso_ari = [by[c]["ari_primary"] for c in iso_cells]
    ordering_ok = all(a > b for a, b in zip(iso_ari, iso_ari[1:], strict=False))
    contain = {c: by[c]["ari_contains_pred_oracle"] for c in iso_cells[1:]}
    contain_inst = {c: by[c]["ari_contains_pred_instrument"] for c in iso_cells[1:]}
    for c in iso_cells[1:]:
        rule13(c, "ARI contains R2 oracle prediction", boot(c, "ari_primary", idx),
               boot(c, "ari_primary", idx_hi), by[c]["pred_ari_oracle"], "contains",
               by[c]["ari_contains_pred_oracle"])
    v2_sub = ("HOLD" if ordering_ok else "MISS",
              "HOLD" if sum(contain.values()) >= V2_MIN_CONTAIN else "MISS")
    v2 = {"prior": 0.80, "iso_cells": iso_cells, "iso_ari": iso_ari,
          "ordering_strictly_decreasing": bool(ordering_ok),
          "predicted_ordering": gates["G4L"]["predicted_iso_ordering"],
          "containment_oracle": contain, "n_contain_oracle": int(sum(contain.values())),
          "containment_instrument": contain_inst,
          "n_contain_instrument": int(sum(contain_inst.values())),
          "threshold": V2_MIN_CONTAIN, "subclause_states": list(v2_sub),
          "state": lean_from_subclauses(v2_sub)}

    # ---- V-3
    diff_boot = {}
    per_rho_diff = {}
    for rho in MID_RHOS:
        a, i = cell_id("ALIGNED", rho, "ambient"), cell_id("ISO", rho, "ambient")
        d = boot(a, "ari_primary", idx) - boot(i, "ari_primary", idx)
        diff_boot[rho] = d
        lo, hi = m.ci_of(d)
        per_rho_diff[str(rho)] = {"point": by[a]["ari_primary"] - by[i]["ari_primary"],
                                  "lo": lo, "hi": hi,
                                  "excludes_zero_negative": bool(hi < 0.0)}
    pooled = 0.5 * (diff_boot[MID_RHOS[0]] + diff_boot[MID_RHOS[1]])
    p_lo, p_hi = m.ci_of(pooled)
    pooled_point = 0.5 * sum(per_rho_diff[str(r)]["point"] for r in MID_RHOS)
    v3a_ok = bool(p_hi < 0.0)
    rule13("pooled", "ALIGNED-ISO pooled diff < 0",
           pooled, 0.5 * (boot(cell_id("ALIGNED", MID_RHOS[0], "ambient"), "ari_primary", idx_hi)
                          - boot(cell_id("ISO", MID_RHOS[0], "ambient"), "ari_primary", idx_hi)
                          + boot(cell_id("ALIGNED", MID_RHOS[1], "ambient"), "ari_primary", idx_hi)
                          - boot(cell_id("ISO", MID_RHOS[1], "ambient"), "ari_primary", idx_hi)),
           0.0, "upper_lt", v3a_ok)
    floor_cells = [cell_id("ALIGNED", r, "ambient") for r in MID_RHOS]
    floor_contain = {c: by[c]["floor_contains_pred"] for c in floor_cells}
    for c in floor_cells:
        rule13(c, "true-card boundary rate contains floor",
               boot(c, "boundary_err_true_card", idx),
               boot(c, "boundary_err_true_card", idx_hi),
               by[c]["pred_boundary_floor_realized"], "contains", by[c]["floor_contains_pred"])
    v3b_ok = bool(sum(floor_contain.values()) >= V3_FLOOR_MIN_CONTAIN)
    # projection restoration fractions, inside the bootstrap
    frac = {}
    for geom in GEOMETRIES:
        amb = cell_id(geom, COMPANION_RHO, "ambient")
        prj = cell_id(geom, COMPANION_RHO, "projection")
        ref = cell_id(geom, 0.0, "ambient")
        f = ((boot(prj, "ari_primary", idx) - boot(amb, "ari_primary", idx))
             / (boot(ref, "ari_primary", idx) - boot(amb, "ari_primary", idx)))
        f_hi = ((boot(prj, "ari_primary", idx_hi) - boot(amb, "ari_primary", idx_hi))
                / (boot(ref, "ari_primary", idx_hi) - boot(amb, "ari_primary", idx_hi)))
        lo, hi = m.ci_of(f)
        frac[geom] = {
            "restoration": float(by[prj]["ari_primary"] - by[amb]["ari_primary"]),
            "deficit": float(by[ref]["ari_primary"] - by[amb]["ari_primary"]),
            "fraction": float((by[prj]["ari_primary"] - by[amb]["ari_primary"])
                              / (by[ref]["ari_primary"] - by[amb]["ari_primary"])),
            "fraction_lo": lo, "fraction_hi": hi,
            "boot": f, "boot_hi": f_hi}
    v3c_iso_ok = bool(frac["ISO"]["fraction"] >= V3_PROJ_ISO_FRAC)
    v3c_ali_ok = bool(frac["ALIGNED"]["fraction"] <= V3_PROJ_ALIGNED_FRAC)
    rule13("ISO_rho0.55_projection", "restoration fraction >= 1/2", frac["ISO"]["boot"],
           frac["ISO"]["boot_hi"], V3_PROJ_ISO_FRAC, "lower_gt", v3c_iso_ok)
    rule13("ALIGNED_rho0.55_projection", "restoration fraction <= 1/4",
           frac["ALIGNED"]["boot"], frac["ALIGNED"]["boot_hi"], V3_PROJ_ALIGNED_FRAC,
           "upper_lt", v3c_ali_ok)
    v3c_ok = bool(v3c_iso_ok and v3c_ali_ok)
    rem = {geom: by[cell_id(geom, COMPANION_RHO, "removal")]["ari_primary"]
           for geom in GEOMETRIES}
    v3d_ok = bool(all(v >= V3_REMOVAL_BAR for v in rem.values()))
    v3_sub = ("HOLD" if v3a_ok else "MISS", "HOLD" if v3b_ok else "MISS",
              "HOLD" if v3c_ok else "MISS", "HOLD" if v3d_ok else "MISS")
    v3 = {"prior": 0.75,
          "pooled_diff": pooled_point, "pooled_lo": p_lo, "pooled_hi": p_hi,
          "per_rho_diff": per_rho_diff, "floor_containment": floor_contain,
          "floor_predictions": {c: by[c]["pred_boundary_floor_realized"] for c in floor_cells},
          "floor_measured": {c: by[c]["boundary_err_true_card"] for c in floor_cells},
          "projection": {g: {k: v for k, v in d.items() if k not in ("boot", "boot_hi")}
                         for g, d in frac.items()},
          "projection_iso_clause": v3c_iso_ok, "projection_aligned_clause": v3c_ali_ok,
          "removal_ari": rem, "removal_clause": v3d_ok,
          "subclause_states": list(v3_sub), "state": lean_from_subclauses(v3_sub)}

    # ---- V-4
    margin = float(gates["G3L"]["v4_null_margin_used"])
    null_ok = {}
    for geom in GEOMETRIES:
        cid = cell_id(geom, 0.0, "ambient")
        null_ok[cid] = {"S_id": by[cid]["audit_S_id"], "lo": by[cid]["audit_S_id_lo"],
                        "hi": by[cid]["audit_S_id_hi"], "margin": margin,
                        "within": bool(abs(by[cid]["audit_S_id_lo"]) <= margin
                                       and abs(by[cid]["audit_S_id_hi"]) <= margin)}
    track = {}
    for geom in GEOMETRIES:
        for rho in RHO_LEVELS[1:]:
            cid = cell_id(geom, rho, "ambient")
            track[cid] = by[cid]["audit_tracks_design"]
            rule13(cid, "audit meter tracks designed b-share",
                   boot(cid, "audit_S_id", idx) - boot(cid, "audit_share_b_design", idx),
                   boot(cid, "audit_S_id", idx_hi) - boot(cid, "audit_share_b_design", idx_hi),
                   0.0, "contains", by[cid]["audit_tracks_design"])
    v4_sub = ("HOLD" if all(v["within"] for v in null_ok.values()) else "MISS",
              "HOLD" if sum(track.values()) >= V4_MIN_TRACK else "MISS")
    v4 = {"prior": 0.80, "null_margin": margin, "null": null_ok,
          "tracking": track, "n_tracking": int(sum(track.values())),
          "threshold": V4_MIN_TRACK, "subclause_states": list(v4_sub),
          "state": lean_from_subclauses(v4_sub)}

    states = {"V-1": v1["state"], "V-2": v2["state"], "V-3": v3["state"], "V-4": v4["state"]}
    routing = route(states)
    boundary = [s for s in stability if s["status"] == "BOUNDARY"]
    slug_bits = [
        {"P1L": "INSTRUMENT_DEFECT_OR_UNREALIZABLE_GRID", "P2L": "SHADOWS_FAIL",
         "P3L": "QUALIFIED", "P4L": "INSTRUMENT_CERTIFIED"}[routing],
        "".join(f"{k.replace('-', '')}{v[0]}" for k, v in states.items()),
    ]
    decision = {
        "leg": "M4-L1", "timestamp_utc": datetime.now(UTC).isoformat(), "banner": BANNER,
        "master_seed": MASTER_SEED, "delta": delta,
        "n_cells": len(all_cells()), "worlds_per_cell": WORLDS_PER_CELL,
        "n_authors_per_world": N_AUTHORS,
        "leans": {"V-1": v1, "V-2": v2, "V-3": v3, "V-4": v4},
        "lean_states": states, "routing": routing,
        "rule13": {"triggered": len(stability), "boundary": len(boundary),
                   "records": stability},
        "verdict_slug": "__".join(slug_bits) + f"__{routing}",
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2, default=str) + "\n",
                                       encoding="utf-8")
    write_manifest({"finalize": time.time() - t0}, {})
    print(json.dumps({k: v for k, v in decision.items() if k != "rule13"}, indent=2,
                     default=str))
    print(f"rule13 triggered={len(stability)} boundary={len(boundary)}")


# ---------------------------------------------------------------------------
# Stage: diagnostic (POST-HOC, after the registered adjudication)

def run_diagnostic(args: argparse.Namespace) -> None:
    """POST-HOC diagnostic, run AFTER the registered adjudication and flagged as
    such.  Writes its own artifact and NEVER touches decision.json.

    Question: R2's projection gain is an ENERGY statement, so it should appear
    where the AMBIENT energy condition Delta^2 >~ sigma_b^2 fails.  The
    registered companions sit at rho_id=.55 (sigma_b^2/Delta^2 = 0.4583, ambient
    condition already satisfied).  This diagnostic runs the same two oracle
    companions at rho_id=.75 (sigma_b^2/Delta^2 = 1.125, ambient condition
    violated) -- an UNREGISTERED cell, reported as a reading only."""
    gates = require_part0()
    delta = float(gates["delta_final"])
    t0 = time.time()
    cells = [(g, 0.75, v) for g in GEOMETRIES for v in ("ambient", "removal", "projection")]
    rows = []
    for world in range(WORLDS_PER_CELL):
        rows.extend([{**r, "world": world} for r in run_world_cells(world, delta, cells)])
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "post_hoc_rho075_companions.csv", index=False)
    summary = {"note": "POST-HOC, unregistered cells, NOT a lean input", "rho_id": 0.75,
               "sigma_b2_over_delta2": sigma_b2_of(delta, 0.75) / (delta * delta)}
    for geom in GEOMETRIES:
        amb = frame.query("geometry == @geom and variant == 'ambient'")["ari_primary"].mean()
        prj = frame.query("geometry == @geom and variant == 'projection'")["ari_primary"].mean()
        rem = frame.query("geometry == @geom and variant == 'removal'")["ari_primary"].mean()
        ref = k2a().read_csv_rt(OUT / f"cell_{cell_id(geom, 0.0, 'ambient')}.csv")[
            "ari_primary"].mean()
        summary[geom] = {"ambient": float(amb), "projection": float(prj), "removal": float(rem),
                         "rho0_reference": float(ref),
                         "restoration_fraction": float((prj - amb) / (ref - amb))}
    (OUT / "post_hoc_rho075_companions.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    write_manifest({"diagnostic_post_hoc": time.time() - t0}, {})
    print(json.dumps(summary, indent=2, default=str))


def write_manifest(stage_times: dict[str, float], extra: dict[str, Any]) -> None:
    path = OUT / "manifest.json"
    prior = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    prior.setdefault("leg", "M4-L1")
    prior.setdefault("banner", BANNER)
    prior.setdefault("script", "scripts/run_suica_m4_l1_typed_world.py")
    prior.setdefault("registration", "docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md M4-L1 (e4a0e4e)")
    prior.setdefault("master_seed", MASTER_SEED)
    prior.setdefault("worlds_per_cell", WORLDS_PER_CELL)
    prior.setdefault("pilot_worlds", list(PILOT_WORLDS))
    prior.setdefault("n_authors", N_AUTHORS)
    prior.setdefault("G", G_GROUPS)
    prior.setdefault("k_tau", K_TAU)
    prior.setdefault("rho_levels", list(RHO_LEVELS))
    prior.setdefault("geometries", list(GEOMETRIES))
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
    parser.add_argument("--stage", required=True,
                        choices=("part0", "arms", "finalize", "diagnostic"))
    parser.add_argument("--cells", default=None, help="comma-separated cell ids (chunking)")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    {"part0": run_part0, "arms": run_arms, "finalize": run_finalize,
     "diagnostic": run_diagnostic}[args.stage](args)


if __name__ == "__main__":
    main()
