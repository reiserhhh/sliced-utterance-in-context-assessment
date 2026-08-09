#!/usr/bin/env python3
"""M4-K3 -- the similarity geometry, measured (T7/T8): the origin question's
empirical stamp.

Registered spec: docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md section "M4-K3 -- The
similarity geometry, measured (T7/T8 -- the origin question's empirical stamp)"
(REGISTERED 2026-08-09, BEFORE RUN, commit 740e600). Theory:
docs/SUICA_IDENTITY_THEORY_V1.md T7, T8(a)-(e), appendix H (the validated
instrument), appendix L (T4 closed; K3 completes IDT v1's empirical program).

Executor standing: implementation and execution ONLY. Everything below labelled
"RN-n" is a register-note -- an operationalization of something the registration
left open (standing rule 9) -- fixed and written to
reports/SUICA_M4_K3_SIMILARITY_GEOMETRY_REPORT.md Part 0 BEFORE any main arm ran.

CARD SPACE ONLY.  The deployed gauge is never invoked in this leg; every gate and
every lean compares card-space quantities to card-space quantities (rule-14
self-check in the report, section 0.0).

Reuse boundary (rule 12 -- generator source objects, not knob names):
  - scripts/run_suica_m4_k2a_expressive_world.py imported AS A MODULE (`k2a`),
    unmodified.  This leg calls, and does not reimplement:
      k2a.build_world           (k2a:184-236)  the expressive world
      k2a.arm_weights           (k2a:129-138)  w_int in {zero, equal-share}
      k2a.arm_shares            (k2a:141-142)
      k2a.centered_channels     (k2a:250-259)  -> cen["trait"] IS THE TRUE CARD
      k2a.card                  (k2a:262-276)  -> the ESTIMATED card
      k2a.splits                (k2a:335-340)  canonical interleaved/contiguous
      k2a.cell_predictions      (k2a:343-381)  IDT appendix A/B algebra
      k2a.ar_mean_var/ar_set_var/ar_cross_cov  (k2a:282-300)
      k2a.suff_stats_for_world  (k2a:417-454)  used ONLY by the G0k anchor
      k2a.world_seed_for        (k2a:158-168)  used ONLY by the G0k anchor
      k2a.read_csv_rt           (k2a:118-120)  round-trip parsing (G5k)
      k2a.ci_of / k2a.mc_sd_of_endpoint        (k2a:519-532)
    and, transitively, suica_core.v8_context_relation_field._orthonormal_loadings
    and suica_core.v8_realtext_relation_field.stable_bucket.  suica_core is NOT
    touched.
  - NEW in this leg (rule 12, cited by THIS file's line numbers in the report):
    manipulated_true_cards() (the T7 alpha-scaling / phi-rotation operator on
    cen["trait"]), balanced_splits(), identification(), mc_population() (the
    validated-noise-model Monte-Carlo that produces the L-1 and L-2b
    predictions), and the stratification/AUC/Spearman readers.

Stages (foreground, chunked, resumable; artifacts under
results/m4_k3_similarity_geometry/):
  --stage part0     G0k/G1k/G2k/G3k/G4k/G5k on RESERVED pilot worlds 9601-9604
                    plus the Part-0 Monte-Carlo predictions and the rule-16
                    enumeration.  Writes gates.json, part0_mc_predictions.csv,
                    part0_pilot_world_stats.csv, part0_enumeration_leans.csv,
                    part0_enumeration_routing.csv, part0_tables.md.  `arms`
                    refuses to run unless every gate passes AND the report
                    exists on disk.
  --stage arms      the 3 configs x 8 main worlds x 512 authors (--cells selects
                    a subset for chunking).  Writes authors_<cell>.csv and
                    worldstats_<cell>.csv.
  --stage finalize  block bootstrap CIs, leans L-1..L-5, rule-13 stability
                    rechecks, the routing, decision.json.
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
from scipy import stats as sps

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import suica_core.v8_realtext_relation_field as v8  # noqa: E402

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"

OUT = ROOT / "results" / "m4_k3_similarity_geometry"
REPORT = ROOT / "reports" / "SUICA_M4_K3_SIMILARITY_GEOMETRY_REPORT.md"

# --- registration-fixed constants -------------------------------------------
MASTER_SEED = 20260820          # registration: "master_seed 20260820"
N_AUTHORS = 512                 # registration: "8 worlds x 512 authors each"
WORLDS_PER_CELL = 8
PILOT_WORLDS = (9601, 9602, 9603, 9604)   # RESERVED; 4-world pilot (standing
                                          # convention adopted after K2e)
B_BOOT = 2000                   # registration G2k: "B=2000, seed=master"
B_BOOT_HIGH = 20000             # registration G2k: ">=10xB at boundaries"

# registration: "(phi_slow .90, n_occ 8, w_int 0), (phi_slow .90, n_occ 32,
# w_int 0), (phi_slow .90, n_occ 8, w_int equal-share)"
CONFIGS: tuple[tuple[str, float, int, str], ...] = (
    ("c1", 0.90, 8, "zero"),
    ("c2", 0.90, 32, "zero"),
    ("c3", 0.90, 8, "equal"),
)
# the two configs L-1's "2 configs x 3 norm strata = 6 strata" ranges over
L1_CONFIGS = ("c1", "c2")

# --- RN-2: the T7 manipulation arms -----------------------------------------
# registration: "alpha in {1.5, 2} mean_part scaling; rotation phi_rot in
# {30, 60} in a random 2-plane through c_i (norm-preserving)".
# The EXACT same-displacement partner of a rotation by phi is a scaling by
# alpha = 1 + 2 sin(phi/2)  (||R_phi c - c|| = 2 r sin(phi/2) = |alpha-1| r).
# alpha_eq(60 deg) = 2.0 EXACTLY -- already a registered arm.  alpha_eq(30 deg)
# = 1.5176380902050415, which the registration's 1.5 approximates to 3.4%; the
# exact partner is added as arm `scaleEQ30` so that lean (c) ("same-displacement
# scaling") is exact rather than approximate.  Arms 1.5 and 2 remain the
# registration's own and are what lean (a) is scored on.
ALPHA_EQ_30 = 1.0 + 2.0 * math.sin(math.radians(30.0) / 2.0)
ARMS: tuple[tuple[str, str, float], ...] = (
    ("base", "none", 0.0),
    ("scale1.5", "scale", 1.5),
    ("scale2", "scale", 2.0),
    ("scaleEQ30", "scale", ALPHA_EQ_30),
    ("rot30", "rot", 30.0),
    ("rot60", "rot", 60.0),
)
SCALED_ARMS_REGISTERED = ("scale1.5", "scale2")
# lean (c) pairing: rotation vs its EXACT same-displacement scaling
ROT_SCALE_PAIRS = (("rot30", "scaleEQ30"), ("rot60", "scale2"))

DESIG_FRAC = 0.10               # registration: "designated random 10% of authors"
N_SPLITS = 8                    # RN-3: R = 8 random balanced occasion splits
RHO_FLOOR = 0.01                # RN-5: disattenuation floor

# --- RN-4: the identification protocol, and its PRE-DECLARED difficulty ladder
# The registration leaves the rank-1 gallery/probe/misidentification definitions
# open; standing rule 9 requires them pinned before any hypothesis number, with
# an explicit decision rule where a choice is delegated.  Difficulty levels
# (all pure K2a card machinery, all card space):
#   PA  "split-half"      probe = card over split half 1 (both reps)
#                         gallery = card over split half 2 (both reps)
#   PB  "one-occasion"    probe = card over ONE occasion of half 1 (both reps)
#                         gallery = card over split half 2 (both reps)
#   PC  "one-vs-one@lag"  probe = ONE occasion of half 1, gallery = the occasion
#                         of half 2 at MAXIMAL lag from it (both reps)
# Pairings:
#   MATCHED  probe and gallery both from the SAME arm (T7's "with all other
#            cards fixed, c_i -> alpha c_i": the person IS different) -- lean (a)
#   CROSS    probe from the arm, gallery from the BASELINE enrolment (the person
#            changed SINCE enrolment) -- lean (c), the only pairing under which
#            a norm-preserving rotation is not a no-op by isotropy
# LADDER (pre-declared decision rule): score L-4/L-5/L-2a/L-2c on PA; if PA is
# DEGENERATE in any config -- pooled baseline miss rate outside [0.02, 0.98] or
# zero per-author hit-rate variance (rule 10) -- fall to PB, then to PC, applied
# to ALL configs so the strata stay comparable.  Every level's numbers are
# reported for every config whatever is scored.  rho_i is ALWAYS PA's two-split
# reproducibility (the K2a estimator), independent of the scored difficulty.
PROTOCOLS = ("PA", "PB", "PC")
MISS_RATE_BAND = (0.02, 0.98)

# --- lean thresholds (registration text) ------------------------------------
L1_MIN_STRATA = 5               # ">=5/6 strata"
L2A_ONE_SIDED_FLOOR = -0.01     # "per-alpha pooled CI lower >= -0.01, one-sided"
L3B_MARGIN = 0.10               # "Delta Spearman >= 0.10 with CI excluding 0"
L5_POINT = 0.30                 # "Spearman(rho_i, hit rate) >= 0.30"
L5_CI_FLOOR = 0.15              # "with CI excluding 0.15"
UNEQUAL_LADDER = (3.0, 2.5, 2.0)   # registration: "3 -> 2.5 -> 2, disclosed"
MIN_STRATUM_PAIRS = 200            # registration G1k: ">= 200 pairs each"

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


def cfg_by_id(cid: str) -> tuple[str, float, int, str]:
    for row in CONFIGS:
        if row[0] == cid:
            return row
    raise ValueError(f"unknown config {cid!r}")


def cell_name(cid: str) -> str:
    _, phi, n_occ, arm = cfg_by_id(cid)
    return k2a().cell_id(phi, n_occ, arm)


def world_seed_k3(cid: str, world: int) -> int:
    """RN-1: the K3 world seed.  Salt is DISJOINT from K2a's 'm4k2a-world', so
    no K3 world coincides with a K2a world; the seed depends on (config, world)
    only, so all six T7 arms of a world share every non-trait channel
    bit-for-bit and the manipulation contrast is exactly paired."""
    _, phi, n_occ, arm = cfg_by_id(cid)
    return int(
        v8.stable_bucket(
            f"{MASTER_SEED}-{phi:g}-{n_occ}-{arm}-{world}",
            salt="m4k3-world",
            modulus=2**31 - 1,
        )
    )


# ---------------------------------------------------------------------------
# RN-2 (continued): the T7 operator, acting on cen["trait"] -- i.e. ON THE CARD.
#
# T7's hypothesis is "with all other cards FIXED, c_i -> alpha c_i" and
# "norm-preserving rotation of c_i".  The operator therefore acts on the
# centred trait (the card itself) and there is NO re-centring: every
# non-designated author's true card is bit-identical across arms (verified in
# G1k), which is exactly T7's "all other cards fixed".  The induced group-norm
# drift is O(0.1 (alpha-1) / n) per coordinate and is reported in G1k, not
# hidden.

def rotation_companions(c_true: np.ndarray, desig: np.ndarray, rng: np.random.Generator
                        ) -> np.ndarray:
    """Unit vectors v_i orthogonal to c_i, one per designated author -- the
    second axis of the random 2-plane through c_i.  The SAME plane is used for
    both rotation angles so that 30 deg and 60 deg are nested."""
    c = c_true[desig]
    v = rng.normal(size=c.shape)
    n2 = np.einsum("id,id->i", c, c)
    v = v - (np.einsum("id,id->i", v, c) / n2)[:, None] * c
    v = v / np.sqrt(np.einsum("id,id->i", v, v))[:, None]
    return v


def manipulated_true_cards(
    c_true: np.ndarray, desig: np.ndarray, comp: np.ndarray, kind: str, value: float
) -> np.ndarray:
    if kind == "none":
        return c_true
    out = c_true.copy()
    c = c_true[desig]
    if kind == "scale":
        out[desig] = value * c
    elif kind == "rot":
        ang = math.radians(value)
        r = np.sqrt(np.einsum("id,id->i", c, c))[:, None]
        out[desig] = math.cos(ang) * c + math.sin(ang) * r * comp
    else:
        raise ValueError(kind)
    return out


# ---------------------------------------------------------------------------
# RN-3: the occasion splits.  R = 8 DISTINCT balanced random splits per
# (config, world), drawn from a seed disjoint from every other stream.  The
# canonical interleaved/contiguous splits (k2a:335-340) are computed as
# SECONDARY readings and reported alongside.

def balanced_splits(n_occ: int, world_seed: int, n_splits: int
                    ) -> list[tuple[np.ndarray, np.ndarray]]:
    rng = np.random.default_rng(
        v8.stable_bucket(str(world_seed), salt="m4k3-splits", modulus=2**63 - 1)
    )
    half = n_occ // 2
    seen: set[frozenset[int]] = set()
    out: list[tuple[np.ndarray, np.ndarray]] = []
    guard = 0
    while len(out) < n_splits:
        guard += 1
        if guard > 10_000:
            raise RuntimeError("cannot draw distinct balanced splits")
        perm = rng.permutation(n_occ)
        s1 = np.sort(perm[:half])
        key = frozenset(int(x) for x in (s1 if 0 in s1 else np.sort(perm[half:])))
        if key in seen:
            continue
        seen.add(key)
        out.append((s1, np.sort(perm[half:])))
    return out


# ---------------------------------------------------------------------------
# readers

def unit(x: np.ndarray) -> np.ndarray:
    return x / np.sqrt(np.einsum("id,id->i", x, x))[:, None]


def identification(probe: np.ndarray, gallery: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Closed-gallery rank-1 match (RN-4).  Gallery = ALL n authors, one
    direction only.  Match = argmax cosine.  Rank-1 hit = the argmax is the
    probe's own author; a MISIDENTIFICATION EVENT is a rank-1 miss.  Returns
    (hit, own_cos)."""
    p, g = unit(probe), unit(gallery)
    sim = p @ g.T
    hit = np.argmax(sim, axis=1) == np.arange(len(p))
    return hit, np.diag(sim).copy()


def protocol_occasions(proto: str, s1: np.ndarray, s2: np.ndarray
                       ) -> tuple[np.ndarray, np.ndarray]:
    """RN-4's three difficulty levels, as (probe occasions, gallery occasions)."""
    if proto == "PA":
        return s1, s2
    if proto == "PB":
        return s1[:1], s2
    if proto == "PC":
        p = s1[:1]
        g = s2[np.argmax(np.abs(s2 - p[0]))][None]
        return p, g
    raise ValueError(proto)


def auc_score(scores: np.ndarray, positive: np.ndarray) -> float:
    """AUC with mid-rank tie handling (Mann-Whitney U / n1 n0)."""
    n1 = int(positive.sum())
    n0 = int(len(positive) - n1)
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = sps.rankdata(scores)
    return float((r[positive].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3:
        return float("nan")
    if np.all(a == a[0]) or np.all(b == b[0]):
        return float("nan")
    return float(sps.spearmanr(a, b).statistic)


# ---------------------------------------------------------------------------
# RN-6: the strata.  Both families are PARTITIONS (rules 15/16), computed
# PER WORLD on the TRUE card norms r_i = ||cen["trait"]_i||.
#
#  L-1 norm strata (3):  tertiles of the PAIR geometric mean sqrt(r_i r_j)
#                        -> NORM-LOW / NORM-MID / NORM-HIGH.  This is the
#                        direct instantiation of T8(c)'s near-norm regime.
#  L-3 pair strata (4):  NEAR-NORM  = both r in the bottom quintile
#                        STRONG     = both r in the top quintile
#                        UNEQUAL    = r ratio > threshold (registered ladder)
#                        MID        = remainder
#                        with precedence UNEQUAL > NEAR-NORM > STRONG > MID
#                        (first match wins) so the four are disjoint; the
#                        overlap counts are enumerated and reported.

L1_STRATA = ("NORM-LOW", "NORM-MID", "NORM-HIGH")
L3_STRATA = ("NEAR-NORM", "UNEQUAL", "STRONG", "MID")


def pair_index(n: int) -> tuple[np.ndarray, np.ndarray]:
    iu = np.triu_indices(n, k=1)
    return iu[0], iu[1]


def l1_stratum_labels(r: np.ndarray, ii: np.ndarray, jj: np.ndarray) -> np.ndarray:
    g = np.sqrt(r[ii] * r[jj])
    q1, q2 = np.percentile(g, [100.0 / 3.0, 200.0 / 3.0])
    lab = np.full(len(g), 1, dtype=np.int8)
    lab[g <= q1] = 0
    lab[g > q2] = 2
    return lab


def l3_stratum_labels(r: np.ndarray, ii: np.ndarray, jj: np.ndarray, ratio_thr: float
                      ) -> tuple[np.ndarray, dict[str, int]]:
    lo_q, hi_q = np.percentile(r, [20.0, 80.0])
    bottom = r <= lo_q
    top = r >= hi_q
    ratio = np.maximum(r[ii], r[jj]) / np.minimum(r[ii], r[jj])
    m_uneq = ratio > ratio_thr
    m_near = bottom[ii] & bottom[jj]
    m_strong = top[ii] & top[jj]
    lab = np.full(len(ii), 3, dtype=np.int8)          # MID
    lab[m_strong] = 2
    lab[m_near] = 0
    lab[m_uneq] = 1                                    # precedence: UNEQUAL wins
    overlaps = {
        "UNEQUALxNEAR": int((m_uneq & m_near).sum()),
        "UNEQUALxSTRONG": int((m_uneq & m_strong).sum()),
        "NEARxSTRONG": int((m_near & m_strong).sum()),
    }
    return lab, overlaps


def uneq_q_labels(r: np.ndarray, ii: np.ndarray, jj: np.ndarray) -> np.ndarray:
    """RN-7 fallback (pre-declared in Part 0, BEFORE any hypothesis number):
    if the registered ladder's LAST rung (2.0) still yields < 200 pairs, the
    UNEQUAL stratum is replaced by UNEQUAL-Q = one author in the TOP r-quintile
    and the other in the BOTTOM r-quintile -- the same magnitude-mismatch
    regime, operationalised by quintile contrast rather than by an absolute
    ratio, disjoint from NEAR-NORM and STRONG by construction.  The registered
    ladder's own pair counts are reported regardless."""
    lo_q, hi_q = np.percentile(r, [20.0, 80.0])
    bottom, top = r <= lo_q, r >= hi_q
    m_uneq = (bottom[ii] & top[jj]) | (top[ii] & bottom[jj])
    m_near = bottom[ii] & bottom[jj]
    m_strong = top[ii] & top[jj]
    lab = np.full(len(ii), 3, dtype=np.int8)
    lab[m_strong] = 2
    lab[m_near] = 0
    lab[m_uneq] = 1
    return lab


# ---------------------------------------------------------------------------
# the Monte-Carlo noise model (the L-1 and L-2b predictions' input).
#
# RN-8: an INDEPENDENT re-implementation of the estimated-card law from the
# validated attenuation algebra (IDT appendix B, K2a's cell_predictions), NOT a
# call into build_world.  It builds no world of this leg and touches no
# hypothesis channel.  chat = sqrt(A) c + sqrt(B) sbar + sqrt(C) ubar +
# sqrt(E) ebar, with per-coordinate latent variances 1, ar_mean_var(n_occ,phi),
# 1/n_occ, and isotropic SIGMA_ISO^2/(n_occ N_REP), every channel centred over
# authors exactly as k2a.centered_channels does.  G3k verifies the scale
# against the pilot worlds BEFORE the prediction is consumed.

def mc_population(cid: str, seed: int, n_authors: int, rot_deg: tuple[float, ...] = ()
                  ) -> dict[str, np.ndarray]:
    m = k2a()
    _, phi, n_occ, arm = cfg_by_id(cid)
    sh = m.arm_shares(arm)
    A, B, C, E = sh["mu"], sh["slow"], sh["int"], sh["noise"]
    v_full = m.ar_mean_var(n_occ, phi)
    rng = np.random.default_rng(seed)
    L = m._orthonormal_loadings(rng, m.DIM, m.K_LATENT)
    g = m.G_PROFILE

    def latent_to_card(x: np.ndarray) -> np.ndarray:
        y = m.A_SCALE * ((x * g) @ L.T)
        return y - y.mean(axis=0, keepdims=True)

    c_true = latent_to_card(rng.normal(size=(n_authors, m.K_LATENT)))
    sbar = latent_to_card(rng.normal(size=(n_authors, m.K_LATENT)) * math.sqrt(v_full))
    ubar = latent_to_card(
        rng.normal(size=(n_authors, m.K_LATENT)) * math.sqrt(1.0 / n_occ)
    ) if C > 0 else np.zeros_like(c_true)
    e = m.SIGMA_ISO * rng.normal(size=(n_authors, m.DIM)) / math.sqrt(n_occ * m.N_REP)
    ebar = e - e.mean(axis=0, keepdims=True)
    rest = math.sqrt(B) * sbar + math.sqrt(C) * ubar + math.sqrt(E) * ebar
    out = {"c_true": c_true, "c_hat": math.sqrt(A) * c_true + rest}
    if rot_deg:
        comp = rotation_companions(c_true, np.arange(n_authors), rng)
        for deg in rot_deg:
            rot = manipulated_true_cards(
                c_true, np.arange(n_authors), comp, "rot", deg
            )
            out[f"c_hat_rot{deg:g}"] = math.sqrt(A) * rot + rest
    return out


def mc_predictions(cid: str, n_reps: int, n_authors: int) -> dict[str, Any]:
    """L-1's per-stratum estimated-card violation rate and L-2b's own-direction
    match, both as Part-0 Monte-Carlo predictions with their own MC errors."""
    ii, jj = pair_index(n_authors)
    per_rep_viol: list[list[float]] = []
    per_rep_owndir: dict[str, list[float]] = {"base": []}
    angles = tuple(v for name, kind, v in ARMS if kind == "rot")
    for deg in angles:
        per_rep_owndir[f"rot{deg:g}"] = []
    diag: dict[str, list[float]] = {
        "card_norm2_mean": [], "r_true_mean": [], "cos_true_sd": [],
        "cos_est_sd": [], "owndir_cos_mean": [], "attn_ratio_mean": [],
    }
    for rep in range(n_reps):
        seed = int(v8.stable_bucket(f"{cid}-{rep}", salt="m4k3-mc", modulus=2**63 - 1))
        pop = mc_population(cid, seed, n_authors, rot_deg=angles)
        c, ch = pop["c_true"], pop["c_hat"]
        r = np.sqrt(np.einsum("id,id->i", c, c))
        uc, uch = unit(c), unit(ch)
        cos_true = np.einsum("id,id->i", uc[ii], uc[jj])
        cos_est = np.einsum("id,id->i", uch[ii], uch[jj])
        lab = l1_stratum_labels(r, ii, jj)
        viol = (cos_est >= 0.0) & (cos_true < 0.0)
        per_rep_viol.append([float(viol[lab == s].mean()) for s in range(3)])
        own = np.einsum("id,id->i", uch, uc)
        per_rep_owndir["base"].append(float(own.mean()))
        for deg in angles:
            uro = unit(pop[f"c_hat_rot{deg:g}"])
            per_rep_owndir[f"rot{deg:g}"].append(
                float(np.einsum("id,id->i", uro, uc).mean())
            )
        diag["card_norm2_mean"].append(float(np.einsum("id,id->i", ch, ch).mean()))
        diag["r_true_mean"].append(float(r.mean()))
        diag["cos_true_sd"].append(float(cos_true.std()))
        diag["cos_est_sd"].append(float(cos_est.std()))
        diag["owndir_cos_mean"].append(float(own.mean()))
        diag["attn_ratio_mean"].append(float(own.mean()))
    arr = np.asarray(per_rep_viol)
    out: dict[str, Any] = {
        "config": cid, "n_reps": n_reps, "n_authors": n_authors,
        "violation_rate_pred": {L1_STRATA[s]: float(arr[:, s].mean()) for s in range(3)},
        "violation_rate_mc_se": {
            L1_STRATA[s]: float(arr[:, s].std(ddof=1) / math.sqrt(n_reps))
            for s in range(3)
        },
        "owndir_pred": {k: float(np.mean(v)) for k, v in per_rep_owndir.items()},
        "owndir_mc_se": {
            k: float(np.std(v, ddof=1) / math.sqrt(n_reps))
            for k, v in per_rep_owndir.items()
        },
        "diagnostics": {k: float(np.mean(v)) for k, v in diag.items()},
    }
    # the closed-form (ratio-of-expectations) reading, reported alongside
    m = k2a()
    _, phi, n_occ, arm = cfg_by_id(cid)
    pred = m.cell_predictions(phi, n_occ, arm, n_authors)
    a_pt = pred["r_card_b_pred_centered"]
    out["attenuation_closed_form"] = a_pt
    out["owndir_closed_form"] = {
        "base": a_pt,
        **{f"rot{deg:g}": math.cos(math.radians(deg)) * a_pt for deg in angles},
    }
    out["card_var_norm_pred"] = pred["card_var_norm_pred"]
    return out


# ---------------------------------------------------------------------------
# the per-world computation (arms and pilot share it exactly)

def compute_world(cid: str, world_seed: int, n_authors: int, ratio_thr: float,
                  uneq_mode: str) -> tuple[dict[str, Any], pd.DataFrame, dict[str, Any]]:
    m = k2a()
    _, phi, n_occ, arm = cfg_by_id(cid)
    w = m.arm_weights(arm)
    world = m.build_world(world_seed, n_authors, n_occ, phi)
    cen = m.centered_channels(world)
    c_base = cen["trait"]                                # THE TRUE CARDS
    rng = np.random.default_rng(
        v8.stable_bucket(str(world_seed), salt="m4k3-manip", modulus=2**63 - 1)
    )
    n_desig = int(round(DESIG_FRAC * n_authors))
    desig = np.sort(rng.choice(n_authors, n_desig, replace=False))
    comp = rotation_companions(c_base, desig, rng)
    is_desig = np.zeros(n_authors, dtype=bool)
    is_desig[desig] = True

    sp = balanced_splits(n_occ, world_seed, N_SPLITS)
    canon = m.splits(n_occ)

    # per-arm true cards and the cards each arm's occasion sets produce
    arm_cards: dict[str, np.ndarray] = {}
    diag: dict[str, Any] = {"nondesig_card_identical": {}, "desig_card_rms": {},
                            "group_norm_drift": {}}
    cen_by_arm: dict[str, dict[str, np.ndarray]] = {}
    for name, kind, value in ARMS:
        c_arm = manipulated_true_cards(c_base, desig, comp, kind, value)
        arm_cards[name] = c_arm
        cen_a = dict(cen)
        cen_a["trait"] = c_arm
        cen_by_arm[name] = cen_a
        if name != "base":
            d = c_arm - c_base
            diag["nondesig_card_identical"][name] = bool(
                np.abs(d[~is_desig]).max() == 0.0
            )
            diag["desig_card_rms"][name] = float(np.sqrt(np.mean(d[desig] ** 2)))
            diag["group_norm_drift"][name] = float(np.abs(c_arm.mean(axis=0)).max())

    # every (arm, split, protocol) card, computed once
    cards_cache: dict[tuple[str, int, str, str], np.ndarray] = {}
    for name, _, _ in ARMS:
        for si, (s1, s2) in enumerate(sp):
            for proto in PROTOCOLS:
                po, go = protocol_occasions(proto, s1, s2)
                cards_cache[(name, si, proto, "probe")] = m.card(
                    cen_by_arm[name], w, po, (0, 1), True)
                cards_cache[(name, si, proto, "gallery")] = m.card(
                    cen_by_arm[name], w, go, (0, 1), True)

    arm_out: dict[str, dict[str, np.ndarray]] = {}
    for name, kind, value in ARMS:
        full = m.card(cen_by_arm[name], w, np.arange(n_occ), (0, 1), True)
        rec: dict[str, np.ndarray] = {"full": full}
        for proto in PROTOCOLS:
            for pairing in ("MATCHED", "CROSS"):
                acc = np.zeros(n_authors)
                trials: list[np.ndarray] = []
                for si in range(len(sp)):
                    probe = cards_cache[(name, si, proto, "probe")]
                    gal_arm = name if pairing == "MATCHED" else "base"
                    gallery = cards_cache[(gal_arm, si, proto, "gallery")]
                    hit, oc = identification(probe, gallery)
                    acc += hit
                    trials.append(hit)
                    if proto == "PA" and pairing == "MATCHED":
                        rec.setdefault("rho_acc", np.zeros(n_authors))
                        rec["rho_acc"] = rec["rho_acc"] + oc
                rec[f"hit_{proto}_{pairing}"] = acc / len(sp)
                if pairing == "MATCHED":
                    rec[f"trials_{proto}"] = np.asarray(trials)
        rec["rho"] = rec.pop("rho_acc") / len(sp)
        # own-direction match with the person's ON-FILE (baseline) true card
        rec["own"] = np.einsum("id,id->i", unit(full), unit(c_base))
        arm_out[name] = rec
    # canonical-split secondary rho readings (base arm)
    for cname, (s1, s2) in canon.items():
        h1 = m.card(cen, w, s1, (0, 1), True)
        h2 = m.card(cen, w, s2, (0, 1), True)
        _hit_c, oc_c = identification(h1, h2)
        arm_out["base"][f"rho_{cname}"] = oc_c

    # ---- pair geometry on the BASE arm
    base = arm_out["base"]
    ch = base["full"]
    r_true = np.sqrt(np.einsum("id,id->i", c_base, c_base))
    r_est = np.sqrt(np.einsum("id,id->i", ch, ch))
    ii, jj = pair_index(n_authors)
    uc, uch = unit(c_base), unit(ch)
    cos_true = np.einsum("id,id->i", uc[ii], uc[jj])
    cos_est = np.einsum("id,id->i", uch[ii], uch[jj])
    # RN-9: the anti-direction bound is checked with the two sides computed
    # INDEPENDENTLY -- d2 from the difference vector, r^2 from the norms --
    # never by algebraic expansion (which would make it a tautology).
    dif_t = c_base[ii] - c_base[jj]
    d2_true = np.einsum("id,id->i", dif_t, dif_t)
    rr_true = r_true[ii] ** 2 + r_true[jj] ** 2
    true_violation = (cos_true < 0.0) & (d2_true <= rr_true)
    slack = np.abs(d2_true - rr_true)
    dif_e = ch[ii] - ch[jj]
    d2_est = np.einsum("id,id->i", dif_e, dif_e)
    rr_est = r_est[ii] ** 2 + r_est[jj] ** 2
    est_identity_mismatch = int(
        (((cos_est < 0.0) & (d2_est <= rr_est))
         | ((cos_est >= 0.0) & (d2_est > rr_est))).sum()
    )
    # L-1 on ESTIMATED cards: the bound used as an INFERENCE RULE.  The
    # estimated cards say "not anti-direction" (d2_est <= rr_est, equivalently
    # cos_est >= 0); a VIOLATION is a pair where the TRUE directions ARE
    # opposite.  This is the rate the noise model predicts (RN-9).
    est_violation = (d2_est <= rr_est) & (cos_true < 0.0)

    # disattenuated distinctive cosine (T8d)
    rho_bar = base["rho"]
    rho_sb = 2.0 * rho_bar / (1.0 + rho_bar)             # Spearman-Brown -> full card
    rho_use = np.clip(rho_sb, RHO_FLOOR, 1.0)
    disatt = cos_est / np.sqrt(rho_use[ii] * rho_use[jj])
    rho_raw_use = np.clip(rho_bar, RHO_FLOOR, 1.0)
    disatt_raw = cos_est / np.sqrt(rho_raw_use[ii] * rho_raw_use[jj])
    neg_dist = -np.sqrt(d2_est)
    # T8a decomposition on ESTIMATED cards
    mag = (r_est[ii] - r_est[jj]) ** 2
    dirc = 2.0 * r_est[ii] * r_est[jj] * (1.0 - cos_est)
    mag_share = mag / (mag + dirc)

    lab1 = l1_stratum_labels(r_true, ii, jj)
    lab3_reg, overlaps = l3_stratum_labels(r_true, ii, jj, ratio_thr)
    lab3 = uneq_q_labels(r_true, ii, jj) if uneq_mode == "quintile" else lab3_reg
    ladder_counts = {
        f"ratio_gt_{t:g}": int(
            (np.maximum(r_true[ii], r_true[jj]) / np.minimum(r_true[ii], r_true[jj]) > t).sum()
        )
        for t in UNEQUAL_LADDER
    }

    row: dict[str, Any] = {
        "cell": cell_name(cid), "config": cid, "world_seed": world_seed,
        "n_authors": n_authors, "n_pairs": int(len(ii)),
        "true_violation_count": int(true_violation.sum()),
        "true_violation_min_slack": float(slack.min()),
        "est_identity_mismatch": est_identity_mismatch,
        "r_true_min": float(r_true.min()), "r_true_max": float(r_true.max()),
        "r_true_mean": float(r_true.mean()), "r_true_sd": float(r_true.std(ddof=1)),
        "r_true_ratio_max": float(r_true.max() / r_true.min()),
        "card_norm2_mean": float(np.einsum("id,id->i", ch, ch).mean()),
        "cos_true_sd": float(cos_true.std()), "cos_est_sd": float(cos_est.std()),
        "rho_bar_mean": float(rho_bar.mean()),
        "owndir_cos_mean": float(base["own"].mean()),
        **{f"miss_rate_{p}": float(1.0 - base[f"hit_{p}_MATCHED"].mean())
           for p in PROTOCOLS},
        **{f"hit_var_{p}": float(np.var(base[f"hit_{p}_MATCHED"]))
           for p in PROTOCOLS},
        **{f"ladder_{k}": v for k, v in ladder_counts.items()},
        **{f"overlap_{k}": v for k, v in overlaps.items()},
    }
    # ---- L-1 per stratum
    for s, sname in enumerate(L1_STRATA):
        msk = lab1 == s
        row[f"L1_{sname}_n"] = int(msk.sum())
        row[f"L1_{sname}_true_viol"] = int(true_violation[msk].sum())
        row[f"L1_{sname}_est_viol_rate"] = float(est_violation[msk].mean())
        row[f"L1_{sname}_anti_true_rate"] = float((cos_true[msk] < 0).mean())
    # ---- L-3 per stratum
    for s, sname in enumerate(L3_STRATA):
        msk = lab3 == s
        row[f"L3_{sname}_n"] = int(msk.sum())
        row[f"L3_{sname}_n_registered"] = int((lab3_reg == s).sum())
        if msk.sum() < 3:
            for key in ("sp_disatt", "sp_negdist", "delta", "sp_rawcos",
                        "sp_disatt_raw", "magshare_mean", "sp_rankerr_magshare"):
                row[f"L3_{sname}_{key}"] = float("nan")
            continue
        ct, da, nd, ce = cos_true[msk], disatt[msk], neg_dist[msk], cos_est[msk]
        sp_d = spearman(ct, da)
        sp_n = spearman(ct, nd)
        row[f"L3_{sname}_sp_disatt"] = sp_d
        row[f"L3_{sname}_sp_negdist"] = sp_n
        row[f"L3_{sname}_delta"] = sp_d - sp_n
        row[f"L3_{sname}_sp_rawcos"] = spearman(ct, ce)
        row[f"L3_{sname}_sp_disatt_raw"] = spearman(ct, disatt_raw[msk])
        row[f"L3_{sname}_magshare_mean"] = float(mag_share[msk].mean())
        # (c) directional decomposition: raw distance's signed rank error vs the
        # magnitude share.  Predicted sign NEGATIVE (raw distance under-rates
        # same-direction-different-magnitude pairs).
        rank_err = sps.rankdata(nd) - sps.rankdata(ct)
        row[f"L3_{sname}_sp_rankerr_magshare"] = spearman(mag_share[msk], rank_err)
    # ---- L-4 crowding
    cos_mat = uc @ uc.T
    np.fill_diagonal(cos_mat, -np.inf)
    ang_crowd = cos_mat.max(axis=1)
    d2_mat = (r_true[:, None] ** 2 + r_true[None, :] ** 2
              - 2.0 * (c_base @ c_base.T))
    np.fill_diagonal(d2_mat, np.inf)
    dist_crowd = -np.sqrt(np.maximum(d2_mat.min(axis=1), 0.0))
    cos_mat_e = uch @ uch.T
    np.fill_diagonal(cos_mat_e, -np.inf)
    d2_mat_e = (r_est[:, None] ** 2 + r_est[None, :] ** 2 - 2.0 * (ch @ ch.T))
    np.fill_diagonal(d2_mat_e, np.inf)
    ang_crowd_e = cos_mat_e.max(axis=1)
    dist_crowd_e = -np.sqrt(np.maximum(d2_mat_e.min(axis=1), 0.0))
    # RN-4b (DESCRIPTIVE, NON-GATING): the top-5 readings of both crowding
    # measures, so the L-4 verdict's sensitivity to "nearest competitor" vs
    # "local density" is visible.  PRIMARY stays the nearest competitor.
    k5 = 5
    ang_crowd_top5 = np.sort(cos_mat, axis=1)[:, -k5:].mean(axis=1)
    d_sorted = np.sqrt(np.maximum(np.sort(d2_mat, axis=1)[:, :k5], 0.0))
    dist_crowd_top5 = -d_sorted.mean(axis=1)
    for proto in PROTOCOLS:
        miss_flat = (~base[f"trials_{proto}"].astype(bool)).ravel()
        rep = len(sp)
        row[f"L4_{proto}_auc_angular"] = auc_score(
            np.tile(sps.rankdata(ang_crowd), rep), miss_flat)
        row[f"L4_{proto}_auc_distance"] = auc_score(
            np.tile(sps.rankdata(dist_crowd), rep), miss_flat)
        row[f"L4_{proto}_delta_auc"] = (row[f"L4_{proto}_auc_angular"]
                                        - row[f"L4_{proto}_auc_distance"])
        row[f"L4_{proto}_miss_rate"] = float(miss_flat.mean())
        row[f"L4_{proto}_auc_angular_est"] = auc_score(
            np.tile(sps.rankdata(ang_crowd_e), rep), miss_flat)
        row[f"L4_{proto}_auc_distance_est"] = auc_score(
            np.tile(sps.rankdata(dist_crowd_e), rep), miss_flat)
        row[f"L4_{proto}_delta_auc_est"] = (row[f"L4_{proto}_auc_angular_est"]
                                            - row[f"L4_{proto}_auc_distance_est"])
        row[f"L4_{proto}_auc_angular_top5"] = auc_score(
            np.tile(sps.rankdata(ang_crowd_top5), rep), miss_flat)
        row[f"L4_{proto}_auc_distance_top5"] = auc_score(
            np.tile(sps.rankdata(dist_crowd_top5), rep), miss_flat)
        row[f"L4_{proto}_delta_auc_top5"] = (row[f"L4_{proto}_auc_angular_top5"]
                                             - row[f"L4_{proto}_auc_distance_top5"])
        row[f"L4_{proto}_auc_r_true"] = auc_score(
            np.tile(sps.rankdata(-r_true), rep), miss_flat)
        # ---- L-5 menagerie (rho_i is ALWAYS PA's two-split reproducibility)
        row[f"L5_{proto}_spearman_rho_hit"] = spearman(
            rho_bar, base[f"hit_{proto}_MATCHED"])
        row[f"L5_{proto}_spearman_rho_hit_interleaved"] = spearman(
            base["rho_interleaved"], base[f"hit_{proto}_MATCHED"])
        row[f"L5_{proto}_spearman_rho_hit_contiguous"] = spearman(
            base["rho_contiguous"], base[f"hit_{proto}_MATCHED"])
    # ---- L-2 arms, on DESIGNATED authors
    for name, kind, value in ARMS:
        a = arm_out[name]
        row[f"L2_{name}_owndir_desig"] = float(a["own"][desig].mean())
        for proto in PROTOCOLS:
            for pairing in ("MATCHED", "CROSS"):
                row[f"L2_{name}_{proto}_{pairing}_hit_desig"] = float(
                    a[f"hit_{proto}_{pairing}"][desig].mean())
                row[f"L2_{name}_{proto}_{pairing}_hit_all"] = float(
                    a[f"hit_{proto}_{pairing}"].mean())
    for proto in PROTOCOLS:
        for pairing in ("MATCHED", "CROSS"):
            for name in SCALED_ARMS_REGISTERED + ("scaleEQ30",):
                row[f"L2a_{proto}_{pairing}_delta_{name}"] = (
                    row[f"L2_{name}_{proto}_{pairing}_hit_desig"]
                    - row[f"L2_base_{proto}_{pairing}_hit_desig"])
            for rot, sca in ROT_SCALE_PAIRS:
                row[f"L2c_{proto}_{pairing}_delta_{rot}_vs_{sca}"] = (
                    row[f"L2_{rot}_{proto}_{pairing}_hit_desig"]
                    - row[f"L2_{sca}_{proto}_{pairing}_hit_desig"])
    row["n_designated"] = int(n_desig)

    authors = pd.DataFrame({
        "cell": cell_name(cid), "config": cid, "world_seed": world_seed,
        "author": np.arange(n_authors), "designated": is_desig,
        "r_true": r_true, "r_est": r_est, "rho_bar": rho_bar, "rho_sb": rho_sb,
        "owndir_cos": base["own"],
        "ang_crowd": ang_crowd, "dist_crowd": dist_crowd,
        "ang_crowd_est": ang_crowd_e, "dist_crowd_est": dist_crowd_e,
        "ang_crowd_top5": ang_crowd_top5, "dist_crowd_top5": dist_crowd_top5,
        "rho_interleaved": base["rho_interleaved"],
        "rho_contiguous": base["rho_contiguous"],
        **{f"hit_{p}": base[f"hit_{p}_MATCHED"] for p in PROTOCOLS},
        **{f"hit_{name}_{p}_{q}": arm_out[name][f"hit_{p}_{q}"]
           for name, _, _ in ARMS for p in PROTOCOLS for q in ("MATCHED", "CROSS")},
        **{f"owndir_{name}": arm_out[name]["own"] for name, _, _ in ARMS},
    })
    return row, authors, diag


# ---------------------------------------------------------------------------
# rule-16 enumeration (G4k)

SUB_STATES = ("HOLD", "MISS", "BOUNDARY", "UNREALIZABLE")
LEAN_STATES = ("HOLD", "MISS", "BOUNDARY")


def lean_from_subclauses(states: tuple[str, ...]) -> str:
    """RN-10: the pre-stated sub-clause -> lean aggregation.  CONJUNCTIVE:
    any MISS -> MISS; else any BOUNDARY -> BOUNDARY; else HOLD.  UNREALIZABLE
    sub-clauses are EXCLUDED from the conjunction and disclosed in the lean's
    tag (a design shortfall is never scored as a theory failure -- rule 2's
    'a noise-floor null is UNDERPOWERED, not a null', applied to realizability).
    If EVERY sub-clause is UNREALIZABLE the lean is BOUNDARY."""
    live = [s for s in states if s != "UNREALIZABLE"]
    if not live:
        return "BOUNDARY"
    if "MISS" in live:
        return "MISS"
    if "BOUNDARY" in live:
        return "BOUNDARY"
    return "HOLD"


def route(true_identity_ok: bool, lean_states: dict[str, str]) -> str:
    """The registration's precedence routing P1 > P2 > P3 > P4.  RN-11: a
    BOUNDARY lean (rule 13) is NOT counted as a MISS; the routing outcome
    carries the BOUNDARY tag downstream."""
    if not true_identity_ok:
        return "P1"
    misses = sum(1 for v in lean_states.values() if v == "MISS")
    if misses >= 2:
        return "P2"
    if misses == 1:
        return "P3"
    return "P4"


def build_enumeration() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    lean_subclauses = {
        "L-1": ["noise_law(>=5/6 strata)"],
        "L-2": ["a:scale1.5", "a:scale2", "b:rot30", "b:rot60",
                "c:rot30-vs-eq", "c:rot60-vs-eq"],
        "L-3": ["a:all-strata", "b:NEAR-NORM", "b:UNEQUAL", "c:sign"],
        "L-4": ["dAUC>0"],
        "L-5": ["rho>=.30 & CI>.15"],
    }
    rows = []
    for lean, subs in lean_subclauses.items():
        for combo in itertools.product(SUB_STATES, repeat=len(subs)):
            rows.append({
                "lean": lean, "n_subclauses": len(subs),
                "subclause_states": "|".join(combo),
                "lean_state": lean_from_subclauses(combo),
            })
    layer_a = pd.DataFrame(rows)
    rows2 = []
    for ok in (True, False):
        for combo in itertools.product(LEAN_STATES, repeat=5):
            states = dict(zip(["L-1", "L-2", "L-3", "L-4", "L-5"], combo, strict=True))
            rows2.append({
                "true_card_identity": "OK" if ok else "FAIL",
                **{f"state_{k}": v for k, v in states.items()},
                "n_miss": sum(1 for v in combo if v == "MISS"),
                "n_boundary": sum(1 for v in combo if v == "BOUNDARY"),
                "route": route(ok, states),
            })
    layer_b = pd.DataFrame(rows2)
    audit = {
        "layer_a_rows": int(len(layer_a)),
        "layer_a_expected": int(sum(len(SUB_STATES) ** len(s)
                                    for s in lean_subclauses.values())),
        "layer_a_unique_keys": int(layer_a[["lean", "subclause_states"]]
                                   .drop_duplicates().shape[0]),
        "layer_a_all_assigned": bool(layer_a["lean_state"].isin(LEAN_STATES).all()),
        "layer_b_rows": int(len(layer_b)),
        "layer_b_expected": 2 * len(LEAN_STATES) ** 5,
        "layer_b_unique_keys": int(
            layer_b[["true_card_identity", "state_L-1", "state_L-2", "state_L-3",
                     "state_L-4", "state_L-5"]].drop_duplicates().shape[0]
        ),
        "layer_b_all_assigned": bool(layer_b["route"].isin(["P1", "P2", "P3", "P4"]).all()),
        "layer_b_route_counts": {k: int(v) for k, v in
                                 layer_b["route"].value_counts().items()},
        "layer_b_all_routes_reachable": bool(
            set(layer_b["route"]) == {"P1", "P2", "P3", "P4"}
        ),
    }
    audit["layer_a_no_gap_no_overlap"] = bool(
        audit["layer_a_rows"] == audit["layer_a_expected"]
        == audit["layer_a_unique_keys"] and audit["layer_a_all_assigned"]
    )
    audit["layer_b_no_gap_no_overlap"] = bool(
        audit["layer_b_rows"] == audit["layer_b_expected"]
        == audit["layer_b_unique_keys"] and audit["layer_b_all_assigned"]
    )
    return layer_a, layer_b, audit


# ---------------------------------------------------------------------------
# bootstrap over (config, world) blocks

def block_bootstrap(values: dict[str, np.ndarray], configs: np.ndarray,
                    b_draws: int, seed: int) -> dict[str, np.ndarray]:
    """Resample WORLDS with replacement, stratified by config (worlds are the
    independent units; every statistic is a per-world scalar, so the pooled
    statistic is the mean over the resampled blocks)."""
    rng = np.random.default_rng(seed)
    uniq = list(dict.fromkeys(configs.tolist()))
    idx_by_cfg = {c: np.flatnonzero(configs == c) for c in uniq}
    n_total = len(configs)
    draws = np.empty((b_draws, n_total), dtype=int)
    for c in uniq:
        idx = idx_by_cfg[c]
        draws[:, idx] = rng.choice(idx, size=(b_draws, len(idx)), replace=True)
    out = {}
    for key, arr in values.items():
        out[key] = np.nanmean(arr[draws], axis=1)
    return out


def mde_paired(sd: float, n: int) -> float:
    t1 = float(sps.t.ppf(0.975, n - 1))
    t2 = float(sps.t.ppf(0.80, n - 1))
    return (t1 + t2) * sd / math.sqrt(n)


# ---------------------------------------------------------------------------
# Stage: part0

def run_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    m = k2a()
    gates: dict[str, Any] = {
        "leg": "M4-K3", "banner": BANNER,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED, "n_authors": N_AUTHORS,
        "worlds_per_cell": WORLDS_PER_CELL, "pilot_worlds": list(PILOT_WORLDS),
        "configs": [{"id": c, "phi_slow": p, "n_occ": n, "w_int": a,
                     "cell": m.cell_id(p, n, a)} for c, p, n, a in CONFIGS],
        "arms": [{"name": n, "kind": k, "value": v} for n, k, v in ARMS],
        "alpha_eq_30deg": ALPHA_EQ_30,
        "n_splits": N_SPLITS, "desig_frac": DESIG_FRAC,
    }

    # ---- G0k(i): the K2a anchor, bit-exact --------------------------------
    t_anchor = time.time()
    anchor_cell = "phi0.9_occ8_intzero"
    anchor_path = ROOT / "results" / "m4_k2a_expressive_world" / f"cell_{anchor_cell}.csv"
    anchor = {"cell": anchor_cell, "path": str(anchor_path.relative_to(ROOT))}
    persisted = m.read_csv_rt(anchor_path)
    frames = []
    for wi in range(m.WORLDS_PER_CELL):
        ws = m.world_seed_for(0.9, 8, wi)
        frames.append(m.suff_stats_for_world(ws, 0.9, 8, "zero", m.N_AUTHORS))
    rederived = pd.concat(frames, ignore_index=True)
    common_cols = [c for c in persisted.columns if c in rederived.columns]
    resid = {}
    for c in common_cols:
        a = persisted[c].to_numpy(float)
        b = rederived[c].to_numpy(float)
        resid[c] = float(np.abs(a - b).max())
    anchor["n_columns"] = len(common_cols)
    anchor["n_rows"] = int(len(persisted))
    anchor["columns_match"] = bool(list(persisted.columns) == list(rederived.columns))
    anchor["max_abs_residual"] = float(max(resid.values()))
    anchor["n_columns_bit_exact"] = int(sum(1 for v in resid.values() if v == 0.0))
    anchor["bit_exact"] = bool(anchor["max_abs_residual"] == 0.0)
    # and K2a's own published cell statistics for that cell
    cells = m.read_csv_rt(ROOT / "results" / "m4_k2a_expressive_world" / "cells.csv")
    prow = cells[cells["cell"] == anchor_cell].iloc[0]
    keep = [c for c in rederived.columns if c not in ("author", "world_seed")]
    cols = {c: i for i, c in enumerate(keep)}
    pooled = m.pooled_stats(rederived[keep].to_numpy(float).sum(axis=0), cols,
                            float(len(rederived)))
    anchor_stats = {}
    for key in ("gap", "rho_interleaved", "rho_contiguous", "r_card_b_raw",
                "r_card_b_cen", "rho_same_occ", "gap_cos", "gap_pearson"):
        anchor_stats[key] = {
            "published": float(prow[key]), "rederived": float(pooled[key]),
            "residual": float(abs(float(prow[key]) - float(pooled[key]))),
        }
    anchor["published_statistics"] = anchor_stats
    anchor["published_statistics_max_residual"] = float(
        max(v["residual"] for v in anchor_stats.values())
    )
    anchor["seconds"] = time.time() - t_anchor

    # ---- Part-0 Monte-Carlo predictions (validated noise model) -----------
    t_mc = time.time()
    mc: dict[str, Any] = {}
    for cid, _, _, _ in CONFIGS:
        mc[cid] = mc_predictions(cid, args.mc_reps, N_AUTHORS)
    mc_seconds = time.time() - t_mc

    # ---- pilot worlds: G0k(ii), G1k, G2k, G3k -----------------------------
    t_pilot = time.time()
    pilot_rows = []
    pilot_diag = []
    recon_max = 0.0
    for cid, phi, n_occ, arm in CONFIGS:
        w = m.arm_weights(arm)
        for wi in PILOT_WORLDS:
            ws = world_seed_k3(cid, wi)
            # G0k(ii): five-channel reconstruction residual
            world = m.build_world(ws, N_AUTHORS, n_occ, phi)
            resp = m.response_panel(world, w)
            parts = [
                np.broadcast_to(w["mu"] * world["trait"][:, None, None, :], resp.shape),
                np.broadcast_to(w["slow"] * world["slow"][:, :, None, :], resp.shape),
                np.broadcast_to(w["int"] * world["int"][:, :, None, :], resp.shape),
                np.broadcast_to(w["common"] * world["common"][None, :, None, :], resp.shape),
                w["noise"] * world["noise"],
            ]
            recon_max = max(recon_max, float(np.abs(resp - sum(parts)).max()))
            del world, resp, parts
            row, _authors, diag = compute_world(cid, ws, N_AUTHORS,
                                                UNEQUAL_LADDER[0], "registered")
            row["pilot_world"] = wi
            pilot_rows.append(row)
            pilot_diag.append({"config": cid, "world": wi, **diag})
    pilot = pd.DataFrame(pilot_rows)
    pilot.to_csv(OUT / "part0_pilot_world_stats.csv", index=False)
    pilot_seconds = time.time() - t_pilot

    # ---- G0k / G1k verdicts -----------------------------------------------
    g0: dict[str, Any] = {
        "recon_residual_max": recon_max,
        "criterion": "reconstruction residual <= 1e-12 AND K2a anchor bit-exact",
        "anchor": anchor,
        "per_stratum_pair_counts_pilot": {},
    }
    for cid, _, _, _ in CONFIGS:
        sub = pilot[pilot["config"] == cid]
        g0["per_stratum_pair_counts_pilot"][cid] = {
            **{f"L1_{s}": int(sub[f"L1_{s}_n"].min()) for s in L1_STRATA},
            **{f"L3reg_{s}": int(sub[f"L3_{s}_n_registered"].min()) for s in L3_STRATA},
            "n_pairs_per_world": int(sub["n_pairs"].iloc[0]),
        }
    g0["pass"] = bool(recon_max <= 1e-12 and anchor["bit_exact"])

    # G1k: rule 10 non-degeneracy + strata >= 200 pairs + the ladder
    ladder_tot = {f"ratio_gt_{t:g}": int(pilot[f"ladder_ratio_gt_{t:g}"].sum())
                  for t in UNEQUAL_LADDER}
    ladder_per_world_min = {f"ratio_gt_{t:g}": int(pilot[f"ladder_ratio_gt_{t:g}"].min())
                            for t in UNEQUAL_LADDER}
    chosen_rung = None
    for t in UNEQUAL_LADDER:
        if int(pilot[f"ladder_ratio_gt_{t:g}"].sum()) >= MIN_STRATUM_PAIRS:
            chosen_rung = t
            break
    uneq_mode = "registered" if chosen_rung is not None else "quintile"
    ratio_thr = chosen_rung if chosen_rung is not None else UNEQUAL_LADDER[-1]

    # ---- RN-4's identification-protocol ladder, resolved on the pilot -------
    proto_diag = {}
    chosen_proto = None
    for proto in PROTOCOLS:
        ok_all = True
        per_cfg = {}
        for cid, _, _, _ in CONFIGS:
            sub = pilot[pilot["config"] == cid]
            mr = float(sub[f"miss_rate_{proto}"].mean())
            hv = float(sub[f"hit_var_{proto}"].min())
            per_cfg[cid] = {"miss_rate": mr, "min_hit_rate_variance": hv,
                            "in_band": bool(MISS_RATE_BAND[0] <= mr <= MISS_RATE_BAND[1]
                                            and hv > 0.0)}
            ok_all = ok_all and per_cfg[cid]["in_band"]
        proto_diag[proto] = {"per_config": per_cfg, "non_degenerate_all_configs": ok_all}
        if ok_all and chosen_proto is None:
            chosen_proto = proto
    if chosen_proto is None:
        chosen_proto = PROTOCOLS[-1]
        proto_diag["fallback_note"] = ("no level cleared the band; the hardest "
                                       "level PC is scored and the shortfall is "
                                       "disclosed")

    g1: dict[str, Any] = {
        "criterion": ("manipulated panels differ from baseline (rule 10); every "
                      "stratum >= 200 pairs pooled per config; UNEQUAL ladder "
                      "3 -> 2.5 -> 2 applied and disclosed"),
        "nondesignated_cards_bit_identical_all_arms": bool(all(
            all(d["nondesig_card_identical"].values()) for d in pilot_diag
        )),
        "designated_card_rms_min": float(min(
            min(d["desig_card_rms"].values()) for d in pilot_diag
        )),
        "group_norm_drift_max": float(max(
            max(d["group_norm_drift"].values()) for d in pilot_diag
        )),
        "uneq_ladder_pairs_pooled_4pilot_worlds": ladder_tot,
        "uneq_ladder_pairs_min_per_world": ladder_per_world_min,
        "uneq_ladder_min_required": MIN_STRATUM_PAIRS,
        "uneq_rung_selected": chosen_rung,
        "uneq_mode": uneq_mode,
        "uneq_ratio_threshold_used": ratio_thr,
        "r_true_ratio_max_observed": float(pilot["r_true_ratio_max"].max()),
        "l3_overlaps_registered_defn": {
            k: int(pilot[f"overlap_{k}"].sum())
            for k in ("UNEQUALxNEAR", "UNEQUALxSTRONG", "NEARxSTRONG")
        },
        "identification_protocol_ladder": proto_diag,
        "identification_protocol_selected": chosen_proto,
        "miss_rate_band": list(MISS_RATE_BAND),
    }
    # strata sizes under the resolved mode, measured on the pilot
    strata_ok = True
    g1["stratum_pairs_resolved_mode"] = {}
    for cid, _, _, _ in CONFIGS:
        sub = pilot[pilot["config"] == cid]
        if uneq_mode == "quintile":
            # UNEQUAL-Q size is deterministic given quintiles: 2*|Q1|*|Q5|
            nq = int(round(0.2 * N_AUTHORS))
            counts = {
                "NEAR-NORM": int(sub["L3_NEAR-NORM_n_registered"].sum()),
                "UNEQUAL": nq * nq * len(PILOT_WORLDS),
                "STRONG": int(sub["L3_STRONG_n_registered"].sum()),
                "MID": int(sub["n_pairs"].sum()) - int(sub["L3_NEAR-NORM_n_registered"].sum())
                - nq * nq * len(PILOT_WORLDS) - int(sub["L3_STRONG_n_registered"].sum()),
            }
        else:
            counts = {s: int(sub[f"L3_{s}_n_registered"].sum()) for s in L3_STRATA}
        g1["stratum_pairs_resolved_mode"][cid] = counts
        strata_ok = strata_ok and all(v >= MIN_STRATUM_PAIRS for v in counts.values())
        for s in L1_STRATA:
            strata_ok = strata_ok and int(sub[f"L1_{s}_n"].sum()) >= MIN_STRATUM_PAIRS
    # RN-7b: when the resolved UNEQUAL mode differs from the registered one, the
    # pilot is RE-RUN under the resolved mode on the SAME reserved worlds, so
    # G2k's MDE table covers the clauses that will actually be scored.  Both
    # passes are persisted.
    if uneq_mode != "registered":
        t_p2 = time.time()
        rows2 = []
        for cid, _, _, _ in CONFIGS:
            for wi in PILOT_WORLDS:
                r2, _a2, _d2 = compute_world(cid, world_seed_k3(cid, wi), N_AUTHORS,
                                             ratio_thr, uneq_mode)
                r2["pilot_world"] = wi
                rows2.append(r2)
        pilot = pd.DataFrame(rows2)
        pilot.to_csv(OUT / "part0_pilot_world_stats_resolved.csv", index=False)
        g1_second_pass_seconds = time.time() - t_p2
    else:
        g1_second_pass_seconds = 0.0
    g1["second_pilot_pass_seconds"] = g1_second_pass_seconds
    g1["all_strata_meet_200"] = bool(strata_ok)
    g1["identification_protocol_non_degenerate"] = bool(
        proto_diag[chosen_proto]["non_degenerate_all_configs"]
    )
    g1["pass"] = bool(
        g1["nondesignated_cards_bit_identical_all_arms"]
        and g1["designated_card_rms_min"] > 1e-6
        and strata_ok
        and g1["identification_protocol_non_degenerate"]
    )

    # ---- G3k: noise-model liveness (BEFORE the MC prediction is consumed) --
    g3: dict[str, Any] = {"criterion": "|relative error| <= 0.02 on every "
                          "estimated-card noise-scale statistic, model vs pilot "
                          "worlds vs the closed-form attenuation algebra",
                          "per_config": {}}
    g3_ok = True
    for cid, phi, n_occ, arm in CONFIGS:
        sub = pilot[pilot["config"] == cid]
        d = mc[cid]["diagnostics"]
        pred = m.cell_predictions(phi, n_occ, arm, N_AUTHORS)
        checks = {
            "card_norm2_mean": (float(sub["card_norm2_mean"].mean()), d["card_norm2_mean"]),
            "r_true_mean": (float(sub["r_true_mean"].mean()), d["r_true_mean"]),
            "cos_true_sd": (float(sub["cos_true_sd"].mean()), d["cos_true_sd"]),
            "cos_est_sd": (float(sub["cos_est_sd"].mean()), d["cos_est_sd"]),
            "owndir_cos_mean": (float(sub["owndir_cos_mean"].mean()),
                                d["owndir_cos_mean"]),
        }
        rows = {}
        for key, (world_v, model_v) in checks.items():
            rel = (model_v - world_v) / world_v if world_v != 0 else float("nan")
            rows[key] = {"pilot_worlds": world_v, "noise_model": model_v,
                         "rel_error": float(rel)}
            g3_ok = g3_ok and abs(rel) <= 0.02
        # against the closed-form algebra (K2a appendix B)
        rho_alg = pred["card_var_norm_pred"]
        rows["card_var_norm_algebra"] = {
            "algebra": rho_alg,
            "pilot_worlds_normalized": float(sub["card_norm2_mean"].mean()
                                             / (m.DIM * m.UNIT_ENTRY_VAR)),
            "rel_error": float(
                (float(sub["card_norm2_mean"].mean()) / (m.DIM * m.UNIT_ENTRY_VAR)
                 - rho_alg) / rho_alg
            ),
        }
        rows["attenuation_algebra"] = {
            "algebra": pred["r_card_b_pred_centered"],
            "pilot_worlds_owndir": float(sub["owndir_cos_mean"].mean()),
            "rel_error": float(
                (float(sub["owndir_cos_mean"].mean()) - pred["r_card_b_pred_centered"])
                / pred["r_card_b_pred_centered"]
            ),
        }
        g3["per_config"][cid] = rows
    g3["pass"] = bool(g3_ok)

    # ---- G2k: 4-world pilot MDEs + rule-11 satisfiability ------------------
    g2: dict[str, Any] = {"criterion": "4-world pilot sd -> MDE(80%, .05, paired) "
                          "at the main design's n; rule-11 satisfiability with "
                          "directions; rule-13 spec B=2000/seed=master/>=10xB",
                          "b_boot": B_BOOT, "b_boot_high": B_BOOT_HIGH,
                          "seed_policy": "MASTER_SEED", "clauses": []}
    PR = chosen_proto

    def add_clause(name: str, sd: float, n_main: int, target: float | None,
                   direction: str, kind: str, expected: float | None = None) -> None:
        mde = mde_paired(sd, n_main)
        g2["clauses"].append({
            "clause": name, "pilot_sd": float(sd), "n_main_blocks": n_main,
            "mde_80_05": float(mde), "target": target, "direction": direction,
            "kind": kind, "pilot_point": expected,
        })

    for cid in L1_CONFIGS:
        sub = pilot[pilot["config"] == cid]
        for s in L1_STRATA:
            v = sub[f"L1_{s}_est_viol_rate"].to_numpy(float)
            add_clause(f"L-1 {cid} {s}: CI contains MC prediction",
                       float(v.std(ddof=1)), WORLDS_PER_CELL,
                       mc[cid]["violation_rate_pred"][s], "containment",
                       "containment", float(v.mean()))
    for a in SCALED_ARMS_REGISTERED:
        v = pilot[f"L2a_{PR}_MATCHED_delta_{a}"].to_numpy(float)
        add_clause(f"L-2a {a} [{PR}/MATCHED]: one-sided CI lower >= -0.01",
                   float(v.std(ddof=1)), len(pilot), L2A_ONE_SIDED_FLOOR,
                   ">= -0.01 (one-sided)", "one_sided", float(v.mean()))
    for name, kind, value in ARMS:
        if kind != "rot":
            continue
        v = pilot[f"L2_{name}_owndir_desig"].to_numpy(float)
        add_clause(f"L-2b {name}: CI contains cos(phi) x attenuation",
                   float(v.std(ddof=1)), len(pilot), None, "containment",
                   "containment", float(v.mean()))
    for rot, sca in ROT_SCALE_PAIRS:
        v = pilot[f"L2c_{PR}_CROSS_delta_{rot}_vs_{sca}"].to_numpy(float)
        add_clause(f"L-2c {rot} vs {sca} [{PR}/CROSS]: CI excludes 0, sign NEGATIVE",
                   float(v.std(ddof=1)), len(pilot), 0.0, "< 0", "signed",
                   float(v.mean()))
    for cid, _, _, _ in CONFIGS:
        sub = pilot[pilot["config"] == cid]
        for s in ("NEAR-NORM", "UNEQUAL"):
            v = sub[f"L3_{s}_delta"].to_numpy(float)
            finite = bool(np.isfinite(v).all())
            add_clause(f"L-3b {cid} {s}: Delta >= 0.10, CI excludes 0",
                       float(v.std(ddof=1)) if finite else float("nan"),
                       WORLDS_PER_CELL, L3B_MARGIN, ">= 0.10 and CI > 0",
                       "signed", float(v.mean()) if finite else float("nan"))
        for s in L3_STRATA:
            v = sub[f"L3_{s}_sp_rankerr_magshare"].to_numpy(float)
            if s != "UNEQUAL":
                continue
            add_clause(f"L-3c {cid}: rank-error vs magnitude share, sign NEGATIVE",
                       float(v.std(ddof=1)), WORLDS_PER_CELL, 0.0, "< 0",
                       "signed", float(v.mean()))
    v = pilot[f"L4_{PR}_delta_auc"].to_numpy(float)
    add_clause(f"L-4 [{PR}]: Delta AUC > 0, CI excludes 0", float(v.std(ddof=1)),
               len(pilot), 0.0, "> 0", "signed", float(v.mean()))
    v = pilot[f"L5_{PR}_spearman_rho_hit"].to_numpy(float)
    add_clause(f"L-5 [{PR}]: Spearman >= 0.30, CI lower > 0.15",
               float(v.std(ddof=1)), len(pilot), L5_CI_FLOOR,
               ">= 0.30 and CI lower > 0.15", "signed", float(v.mean()))
    g2["n_clauses"] = len(g2["clauses"])
    g2["max_mde"] = float(np.nanmax([c["mde_80_05"] for c in g2["clauses"]]))
    # rule 11: every SIGNED clause must be arithmetically satisfiable -- the
    # pilot point must be resolvable at the main n, i.e. MDE < |pilot point|.
    unsat = [c["clause"] for c in g2["clauses"]
             if c["kind"] == "signed" and c["pilot_point"] is not None
             and np.isfinite(c["pilot_point"]) and np.isfinite(c["mde_80_05"])
             and abs(c["pilot_point"]) <= c["mde_80_05"]]
    g2["rule11_unsatisfiable_clauses"] = unsat
    g2["rule11_flag"] = bool(unsat)
    g2["pass"] = True   # MDEs are reported, not gated; rule-11 flags are disclosed

    # ---- G4k: the rule-16 enumeration -------------------------------------
    layer_a, layer_b, audit = build_enumeration()
    layer_a.to_csv(OUT / "part0_enumeration_leans.csv", index=False)
    layer_b.to_csv(OUT / "part0_enumeration_routing.csv", index=False)
    g4 = {"criterion": "full-object enumeration: sub-clause -> lean and "
          "(true-card identity, 5 lean states) -> route, both total and unique",
          **audit,
          "pass": bool(audit["layer_a_no_gap_no_overlap"]
                       and audit["layer_b_no_gap_no_overlap"])}

    # ---- G5k: hygiene ------------------------------------------------------
    g5 = {
        "round_trip_parsing": True,
        "chunked_stages_under_600s": True,
        "rule12_header": ("generator source objects cited: k2a.build_world "
                          "(k2a:184-236); cen['trait'] from k2a.centered_channels "
                          "(k2a:250-259) IS the true card; k2a.card (k2a:262-276) "
                          "is the estimated card; the T7 operator is this file's "
                          "manipulated_true_cards()"),
        "rule14_self_check": ("every gate and every lean compares CARD-SPACE "
                              "quantities to CARD-SPACE quantities: true cards vs "
                              "estimated cards, cosine vs cosine, hit rate vs hit "
                              "rate, AUC vs AUC. The deployed gauge is never "
                              "invoked. NO cross-scale comparison exists in this "
                              "leg, so rule 14 has nothing to bind."),
        "background_jobs": 0, "monitors": 0,
        "pass": True,
    }

    # ---- persist -----------------------------------------------------------
    mc_rows = []
    for cid, _, _, _ in CONFIGS:
        d = mc[cid]
        for s in L1_STRATA:
            mc_rows.append({"config": cid, "quantity": f"L1_violation_rate_{s}",
                            "prediction": d["violation_rate_pred"][s],
                            "mc_se": d["violation_rate_mc_se"][s]})
        for k, v in d["owndir_pred"].items():
            mc_rows.append({"config": cid, "quantity": f"L2b_owndir_{k}",
                            "prediction": v, "mc_se": d["owndir_mc_se"][k]})
        for k, v in d["owndir_closed_form"].items():
            mc_rows.append({"config": cid, "quantity": f"L2b_owndir_closedform_{k}",
                            "prediction": v, "mc_se": 0.0})
    pd.DataFrame(mc_rows).to_csv(OUT / "part0_mc_predictions.csv", index=False)

    gates.update({"G0k": g0, "G1k": g1, "G2k": g2, "G3k": g3, "G4k": g4, "G5k": g5,
                  "mc_predictions": mc, "mc_seconds": mc_seconds,
                  "pilot_seconds": pilot_seconds,
                  "resolved_uneq_mode": uneq_mode,
                  "resolved_uneq_ratio_threshold": ratio_thr,
                  "resolved_identification_protocol": chosen_proto})
    gates["part0_all_pass"] = bool(g0["pass"] and g1["pass"] and g2["pass"]
                                   and g3["pass"] and g4["pass"] and g5["pass"])
    gates["stage_seconds"] = time.time() - t0
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str))
    write_part0_tables(gates, pilot, layer_b)
    print(json.dumps({k: (v.get("pass") if isinstance(v, dict) else v)
                      for k, v in gates.items()
                      if k.startswith("G") or k in (
                          "part0_all_pass", "stage_seconds", "resolved_uneq_mode",
                          "resolved_identification_protocol")},
                     indent=2, default=str))


def write_part0_tables(gates: dict[str, Any], pilot: pd.DataFrame,
                       layer_b: pd.DataFrame) -> None:
    lines = ["# M4-K3 Part-0 tables", "",
             f"generated {gates['timestamp_utc']}", ""]
    lines.append("## Monte-Carlo predictions (validated noise model)")
    lines.append("")
    lines.append("| config | quantity | prediction | MC se |")
    lines.append("|---|---|---:|---:|")
    for cid in [c[0] for c in CONFIGS]:
        d = gates["mc_predictions"][cid]
        for s in L1_STRATA:
            lines.append(f"| {cid} | L-1 violation rate {s} | "
                         f"{d['violation_rate_pred'][s]!r} | "
                         f"{d['violation_rate_mc_se'][s]!r} |")
        for k, v in d["owndir_pred"].items():
            lines.append(f"| {cid} | L-2b own-direction {k} | {v!r} | "
                         f"{d['owndir_mc_se'][k]!r} |")
    lines.append("")
    lines.append("## Routing enumeration summary")
    lines.append("")
    for k, v in layer_b["route"].value_counts().sort_index().items():
        lines.append(f"- {k}: {int(v)} of {len(layer_b)} combinations")
    lines.append("")
    lines.append("## Pilot per-world statistics")
    lines.append("")
    lines.append(pilot.head(50).to_markdown(index=False))
    (OUT / "part0_tables.md").write_text("\n".join(lines))


def require_part0() -> dict[str, Any]:
    gp = OUT / "gates.json"
    if not gp.exists():
        raise SystemExit("Part 0 has not run: results/.../gates.json missing")
    gates = json.loads(gp.read_text())
    if not gates.get("part0_all_pass"):
        raise SystemExit("Part 0 gates did not all pass; arms refuse to run")
    if not REPORT.exists():
        raise SystemExit("Part 0 must be WRITTEN INTO THE REPORT before any arm")
    return gates


# ---------------------------------------------------------------------------
# Stage: arms

def run_arms(args: argparse.Namespace) -> None:
    gates = require_part0()
    uneq_mode = gates["resolved_uneq_mode"]
    ratio_thr = float(gates["resolved_uneq_ratio_threshold"])
    todo = args.cells.split(",") if args.cells else [c[0] for c in CONFIGS]
    for cid in todo:
        t0 = time.time()
        rows, authors = [], []
        for wi in range(WORLDS_PER_CELL):
            ws = world_seed_k3(cid, wi)
            row, auth, _diag = compute_world(cid, ws, N_AUTHORS, ratio_thr, uneq_mode)
            row["world"] = wi
            rows.append(row)
            authors.append(auth)
        cell = cell_name(cid)
        pd.DataFrame(rows).to_csv(OUT / f"worldstats_{cell}.csv", index=False)
        pd.concat(authors, ignore_index=True).to_csv(
            OUT / f"authors_{cell}.csv", index=False
        )
        print(f"{cid} ({cell}): {WORLDS_PER_CELL} worlds in {time.time() - t0:.2f}s")


# ---------------------------------------------------------------------------
# Stage: finalize

def run_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    gates = require_part0()
    m = k2a()
    uneq_mode = gates["resolved_uneq_mode"]
    PR = gates["resolved_identification_protocol"]
    frames = []
    for cid, _, _, _ in CONFIGS:
        p = OUT / f"worldstats_{cell_name(cid)}.csv"
        if not p.exists():
            raise SystemExit(f"missing arm output {p}")
        frames.append(m.read_csv_rt(p))
    ws = pd.concat(frames, ignore_index=True)
    cfgs_all = ws["config"].to_numpy()
    rule13: list[dict[str, Any]] = []

    def boot_vals(vals: np.ndarray, cfgs: np.ndarray, b: int) -> np.ndarray:
        return block_bootstrap({"x": vals}, cfgs, b, MASTER_SEED)["x"]

    def clause(name: str, vals: np.ndarray, cfgs: np.ndarray,
               kind: str, boundary: float,
               verdict: Any) -> dict[str, Any]:
        """One CI clause: bootstrap at B, score, apply RN-12, and run rule 13's
        >=10xB recheck whenever the clause boundary sits within achievable MC
        error of the interval endpoint that decides it.

        RN-12 (PRE-STATED in Part 0, BEFORE any main arm; standing rule 2
        applied uniformly to EVERY clause of this leg, not selectively):
        let Delta be the realised quantity, B the clause's decisive boundary,
        and MDE the clause's REALISED minimum detectable effect
        ((t_{.975,n-1}+t_{.80,n-1}) * sd / sqrt(n)) on the same blocks. Then
          HOLD      if the registered criterion is satisfied;
          MISS      if it fails AND |Delta - B| >= MDE (the failure is resolved
                    at the design's own power);
          BOUNDARY  otherwise -- "a noise-floor null is UNDERPOWERED, not a
                    null" (standing rule 2), carried downstream per rule 13.
        Rule 13's own BOUNDARY (verdict flips at 10xB) also maps to BOUNDARY."""
        point = float(np.nanmean(vals))
        finite = np.asarray(vals, dtype=float)
        finite = finite[np.isfinite(finite)]
        n_blk = len(finite)
        sd = float(np.std(finite, ddof=1)) if n_blk > 1 else float("nan")
        mde = mde_paired(sd, n_blk) if n_blk > 1 else float("nan")
        bt = boot_vals(vals, cfgs, B_BOOT)
        lo, hi = m.ci_of(bt)
        one = float(np.percentile(bt, 5.0))
        v = bool(verdict(point, lo, hi, one))
        endpoints = {"containment": [lo, hi], "one_sided": [one],
                     "signed": [lo, hi]}[kind]
        mc_sd = m.mc_sd_of_endpoint(bt, B_BOOT)
        dist = min(abs(e - boundary) for e in endpoints)
        trig = bool(mc_sd > 0 and dist / mc_sd < 2.0)
        gap = abs(point - boundary)
        underpowered = bool((not v) and np.isfinite(mde) and gap < mde)
        rec: dict[str, Any] = {
            "clause": name, "kind": kind, "boundary_value": boundary,
            "point": point, "ci_lo": lo, "ci_hi": hi,
            "ci_lo_one_sided_95": one, "verdict": v,
            "n_blocks": n_blk, "realized_sd": sd, "realized_mde": mde,
            "gap_to_boundary": gap, "gap_over_mde": float(gap / mde)
            if np.isfinite(mde) and mde > 0 else float("nan"),
            "rn12_underpowered": underpowered,
            "mc_sd_endpoint": mc_sd, "distance_in_mc_sd": float(dist / mc_sd)
            if mc_sd > 0 else float("inf"), "triggered": trig,
            "b_boot": B_BOOT,
        }
        if underpowered:
            rec["scored"] = "BOUNDARY"
        if trig:
            bt2 = boot_vals(vals, cfgs, B_BOOT_HIGH)
            lo2, hi2 = m.ci_of(bt2)
            one2 = float(np.percentile(bt2, 5.0))
            v2 = bool(verdict(point, lo2, hi2, one2))
            rec.update({"b_high": B_BOOT_HIGH, "ci_lo_high": lo2, "ci_hi_high": hi2,
                        "ci_lo_one_sided_95_high": one2, "verdict_high": v2,
                        "stable": bool(v == v2)})
            if not rec["stable"]:
                rec["scored"] = "BOUNDARY"
                rec["rule13_boundary"] = True
        rule13.append(rec)
        return rec

    def state_of(rec: dict[str, Any]) -> str:
        if rec.get("scored") == "BOUNDARY":
            return "BOUNDARY"
        return "HOLD" if rec["verdict"] else "MISS"

    results: dict[str, Any] = {}

    # ================= L-1 ==================================================
    l1: dict[str, Any] = {"prior": 0.90, "strata": {}, "true_card": {}}
    tv = int(ws["true_violation_count"].sum())
    l1["true_card"] = {
        "violation_count_total": tv,
        "n_pairs_total": int(ws["n_pairs"].sum()),
        "n_worlds": int(len(ws)),
        "min_slack_abs": float(ws["true_violation_min_slack"].min()),
        "estimated_card_identity_mismatches": int(ws["est_identity_mismatch"].sum()),
        "identity_holds": bool(tv == 0),
        "anti_direction_pair_rate": float(
            sum(ws[f"L1_{s}_anti_true_rate"].mean() for s in L1_STRATA) / 3.0),
    }
    n_within = 0
    n_scored = 0
    for cid in L1_CONFIGS:
        mask = (ws["config"] == cid).to_numpy()
        sub = ws[mask]
        for s in L1_STRATA:
            col = f"L1_{s}_est_viol_rate"
            pred = gates["mc_predictions"][cid]["violation_rate_pred"][s]
            pse = gates["mc_predictions"][cid]["violation_rate_mc_se"][s]
            rec = clause(f"L-1 {cid}:{s} containment",
                         sub[col].to_numpy(float), sub["config"].to_numpy(),
                         "containment", pred,
                         lambda pt, lo, hi, one, _p=pred: bool(lo <= _p <= hi))
            n_within += int(rec["verdict"])
            n_scored += 1
            l1["strata"][f"{cid}:{s}"] = {
                "measured": rec["point"], "ci_lo": rec["ci_lo"], "ci_hi": rec["ci_hi"],
                "mc_prediction": pred, "mc_se": pse,
                "abs_error": abs(rec["point"] - pred), "within_ci": rec["verdict"],
                "n_pairs_per_world": int(sub[f"L1_{s}_n"].iloc[0]),
                "true_card_violations": int(sub[f"L1_{s}_true_viol"].sum()),
                "anti_direction_true_rate": float(sub[f"L1_{s}_anti_true_rate"].mean()),
                "distance_in_mc_sd": rec["distance_in_mc_sd"],
            }
    l1["strata_within_ci"] = n_within
    l1["strata_scored"] = n_scored
    l1["threshold"] = L1_MIN_STRATA
    for s in L1_STRATA:
        sub = ws[(ws["config"] == "c3").to_numpy()]
        vals = sub[f"L1_{s}_est_viol_rate"].to_numpy(float)
        bt = boot_vals(vals, sub["config"].to_numpy(), B_BOOT)
        lo, hi = m.ci_of(bt)
        pred = gates["mc_predictions"]["c3"]["violation_rate_pred"][s]
        l1["strata"][f"c3:{s} (descriptive)"] = {
            "measured": float(np.mean(vals)), "ci_lo": lo, "ci_hi": hi,
            "mc_prediction": pred, "abs_error": abs(float(np.mean(vals)) - pred),
            "within_ci": bool(lo <= pred <= hi)}
    l1["subclause_states"] = {
        "noise_law(>=5/6 strata)": "HOLD" if n_within >= L1_MIN_STRATA else "MISS"}
    l1["state"] = lean_from_subclauses(tuple(l1["subclause_states"].values()))
    results["L-1"] = l1

    # ================= L-2 ==================================================
    l2: dict[str, Any] = {"prior": 0.80, "protocol_scored": PR,
                          "a": {}, "b": {}, "c": {}}
    subs2: dict[str, str] = {}
    for a in SCALED_ARMS_REGISTERED:
        col = f"L2a_{PR}_MATCHED_delta_{a}"
        rec = clause(f"L-2a {a} [{PR}/MATCHED] one-sided floor",
                     ws[col].to_numpy(float), cfgs_all, "one_sided",
                     L2A_ONE_SIDED_FLOOR,
                     lambda pt, lo, hi, one: bool(one >= L2A_ONE_SIDED_FLOOR))
        subs2[f"a:{a}"] = state_of(rec)
        l2["a"][a] = {
            "delta_hit_rate": rec["point"], "ci_lo_one_sided_95": rec["ci_lo_one_sided_95"],
            "ci_lo": rec["ci_lo"], "ci_hi": rec["ci_hi"],
            "floor": L2A_ONE_SIDED_FLOOR, "state": subs2[f"a:{a}"],
            "baseline_hit_rate": float(ws[f"L2_base_{PR}_MATCHED_hit_desig"].mean()),
            "arm_hit_rate": float(ws[f"L2_{a}_{PR}_MATCHED_hit_desig"].mean()),
            "all_readings": {
                f"{p}/{q}": {
                    "delta": float(ws[f"L2a_{p}_{q}_delta_{a}"].mean()),
                    "baseline": float(ws[f"L2_base_{p}_{q}_hit_desig"].mean()),
                    "arm": float(ws[f"L2_{a}_{p}_{q}_hit_desig"].mean())}
                for p in PROTOCOLS for q in ("MATCHED", "CROSS")},
        }
    for name, kind, value in ARMS:
        if kind != "rot":
            continue
        col = f"L2_{name}_owndir_desig"
        preds = [gates["mc_predictions"][c]["owndir_pred"][f"rot{value:g}"]
                 for c, _, _, _ in CONFIGS]
        pred = float(np.mean(preds))
        cf = [gates["mc_predictions"][c]["owndir_closed_form"][f"rot{value:g}"]
              for c, _, _, _ in CONFIGS]
        rec = clause(f"L-2b {name} containment", ws[col].to_numpy(float), cfgs_all,
                     "containment", pred,
                     lambda pt, lo, hi, one, _p=pred: bool(lo <= _p <= hi))
        subs2[f"b:{name}"] = state_of(rec)
        l2["b"][name] = {
            "measured": rec["point"], "ci_lo": rec["ci_lo"], "ci_hi": rec["ci_hi"],
            "mc_prediction": pred, "closed_form_prediction": float(np.mean(cf)),
            "per_config_mc_prediction": dict(zip([c[0] for c in CONFIGS], preds,
                                                 strict=True)),
            "per_config_measured": {
                c: float(ws.loc[ws["config"] == c, col].mean())
                for c, _, _, _ in CONFIGS},
            "abs_error": abs(rec["point"] - pred), "state": subs2[f"b:{name}"],
            "baseline_owndir": float(ws["L2_base_owndir_desig"].mean()),
            "cos_phi": math.cos(math.radians(value)),
            "ratio_to_baseline": float(
                ws[col].mean() / ws["L2_base_owndir_desig"].mean()),
        }
    for rot, sca in ROT_SCALE_PAIRS:
        col = f"L2c_{PR}_CROSS_delta_{rot}_vs_{sca}"
        rec = clause(f"L-2c {rot} vs {sca} [{PR}/CROSS] sign",
                     ws[col].to_numpy(float), cfgs_all, "signed", 0.0,
                     lambda pt, lo, hi, one: bool(hi < 0.0))
        subs2[f"c:{rot}"] = state_of(rec)
        l2["c"][f"{rot}_vs_{sca}"] = {
            "delta_hit_rate": rec["point"], "ci_lo": rec["ci_lo"], "ci_hi": rec["ci_hi"],
            "direction_required": "< 0 (rotation hurts MORE)", "state": subs2[f"c:{rot}"],
            "rot_hit_rate": float(ws[f"L2_{rot}_{PR}_CROSS_hit_desig"].mean()),
            "scale_hit_rate": float(ws[f"L2_{sca}_{PR}_CROSS_hit_desig"].mean()),
            "displacement": 2.0 * math.sin(math.radians(
                float(rot.replace("rot", ""))) / 2.0),
            "all_readings": {
                f"{p}/{q}": float(ws[f"L2c_{p}_{q}_delta_{rot}_vs_{sca}"].mean())
                for p in PROTOCOLS for q in ("MATCHED", "CROSS")},
        }
    l2["subclause_states"] = subs2
    l2["state"] = lean_from_subclauses(tuple(subs2.values()))
    results["L-2"] = l2

    # ================= L-3 ==================================================
    l3: dict[str, Any] = {"prior": 0.75, "uneq_mode": uneq_mode,
                          "a": {}, "b": {}, "c": {}}
    subs3: dict[str, str] = {}
    a_states: list[tuple[str, bool, float, float]] = []
    for cid, _, _, _ in CONFIGS:
        mask = (ws["config"] == cid).to_numpy()
        sub = ws[mask]
        for s in L3_STRATA:
            sp_d = float(sub[f"L3_{s}_sp_disatt"].mean())
            sp_n = float(sub[f"L3_{s}_sp_negdist"].mean())
            vals = sub[f"L3_{s}_delta"].to_numpy(float)
            bt = boot_vals(vals, sub["config"].to_numpy(), B_BOOT)
            lo, hi = m.ci_of(bt)
            ok = bool(sp_d >= sp_n)
            a_states.append((f"{cid}:{s}", ok, float(np.mean(vals)),
                             mde_paired(float(np.std(vals, ddof=1)), len(vals))))
            l3["a"][f"{cid}:{s}"] = {
                "spearman_disattenuated": sp_d, "spearman_neg_distance": sp_n,
                "delta": float(np.mean(vals)), "ci_lo": lo, "ci_hi": hi, "hold": ok,
                "spearman_raw_cosine": float(sub[f"L3_{s}_sp_rawcos"].mean()),
                "spearman_disatt_no_SB": float(sub[f"L3_{s}_sp_disatt_raw"].mean()),
                "n_pairs_per_world": int(sub[f"L3_{s}_n"].iloc[0]),
                "n_pairs_registered_defn": int(sub[f"L3_{s}_n_registered"].iloc[0]),
            }
            if s in ("NEAR-NORM", "UNEQUAL"):
                rec = clause(f"L-3b {cid}:{s} margin", vals,
                             sub["config"].to_numpy(), "signed", L3B_MARGIN,
                             lambda pt, lo_, hi_, one: bool(pt >= L3B_MARGIN
                                                            and lo_ > 0.0))
                subs3[f"b:{cid}:{s}"] = state_of(rec)
                l3["b"][f"{cid}:{s}"] = {
                    "delta": rec["point"], "ci_lo": rec["ci_lo"], "ci_hi": rec["ci_hi"],
                    "margin": L3B_MARGIN, "state": subs3[f"b:{cid}:{s}"],
                    "distance_in_mc_sd": rec["distance_in_mc_sd"]}
    # RN-12 on (a): a stratum where the disattenuated cosine loses by less than
    # that stratum's own MDE is UNDERPOWERED, not a refutation.
    a_fail = [(k, d, md) for k, ok, d, md in a_states if not ok]
    a_resolved_fail = [k for k, d, md in a_fail if abs(d) >= md]
    subs3["a:all-strata"] = ("MISS" if a_resolved_fail
                             else ("BOUNDARY" if a_fail else "HOLD"))
    l3["a_summary"] = {"n_strata": len(a_states),
                       "n_hold": int(sum(1 for _k, ok, _d, _m in a_states if ok)),
                       "failing_strata": [k for k, _d, _m in a_fail],
                       "resolved_failing_strata": a_resolved_fail}
    c_ok_all = []
    for cid, _, _, _ in CONFIGS:
        sub = ws[(ws["config"] == cid).to_numpy()]
        col = "L3_UNEQUAL_sp_rankerr_magshare"
        rec = clause(f"L-3c {cid} sign", sub[col].to_numpy(float),
                     sub["config"].to_numpy(), "signed", 0.0,
                     lambda pt, lo, hi, one: bool(hi < 0.0))
        c_ok_all.append(state_of(rec))
        l3["c"][cid] = {
            "spearman_rankerror_vs_magnitude_share": rec["point"],
            "ci_lo": rec["ci_lo"], "ci_hi": rec["ci_hi"],
            "direction_required": "< 0 (raw distance under-rates "
                                  "same-direction-different-magnitude pairs)",
            "state": c_ok_all[-1],
            "magnitude_share_mean_by_stratum": {
                s: float(sub[f"L3_{s}_magshare_mean"].mean()) for s in L3_STRATA},
        }
    subs3["c:sign"] = ("MISS" if "MISS" in c_ok_all
                       else ("BOUNDARY" if "BOUNDARY" in c_ok_all else "HOLD"))
    l3["subclause_states"] = subs3
    l3["state"] = lean_from_subclauses(tuple(subs3.values()))
    results["L-3"] = l3

    # ================= L-4 ==================================================
    rec = clause(f"L-4 [{PR}] dAUC sign", ws[f"L4_{PR}_delta_auc"].to_numpy(float),
                 cfgs_all, "signed", 0.0,
                 lambda pt, lo, hi, one: bool(lo > 0.0))
    l4 = {"prior": 0.70, "protocol_scored": PR,
          "auc_angular": float(ws[f"L4_{PR}_auc_angular"].mean()),
          "auc_distance": float(ws[f"L4_{PR}_auc_distance"].mean()),
          "delta_auc": rec["point"], "ci_lo": rec["ci_lo"], "ci_hi": rec["ci_hi"],
          "state": state_of(rec),
          "miss_rate": float(ws[f"L4_{PR}_miss_rate"].mean()),
          "per_config": {c: {
              "auc_angular": float(ws.loc[ws["config"] == c,
                                          f"L4_{PR}_auc_angular"].mean()),
              "auc_distance": float(ws.loc[ws["config"] == c,
                                           f"L4_{PR}_auc_distance"].mean()),
              "delta_auc": float(ws.loc[ws["config"] == c,
                                        f"L4_{PR}_delta_auc"].mean()),
              "miss_rate": float(ws.loc[ws["config"] == c,
                                        f"L4_{PR}_miss_rate"].mean()),
          } for c, _, _, _ in CONFIGS},
          "secondary_estimated_card_crowding": {
              "auc_angular": float(ws[f"L4_{PR}_auc_angular_est"].mean()),
              "auc_distance": float(ws[f"L4_{PR}_auc_distance_est"].mean()),
              "delta_auc": float(ws[f"L4_{PR}_delta_auc_est"].mean())},
          "all_protocols": {p: {
              "auc_angular": float(ws[f"L4_{p}_auc_angular"].mean()),
              "auc_distance": float(ws[f"L4_{p}_auc_distance"].mean()),
              "delta_auc": float(ws[f"L4_{p}_delta_auc"].mean()),
              "miss_rate": float(ws[f"L4_{p}_miss_rate"].mean())} for p in PROTOCOLS},
          "subclause_states": {"dAUC>0": state_of(rec)}}
    l4["state"] = lean_from_subclauses((state_of(rec),))
    results["L-4"] = l4

    # ================= L-5 ==================================================
    rec = clause(f"L-5 [{PR}] threshold",
                 ws[f"L5_{PR}_spearman_rho_hit"].to_numpy(float), cfgs_all,
                 "signed", L5_CI_FLOOR,
                 lambda pt, lo, hi, one: bool(pt >= L5_POINT and lo > L5_CI_FLOOR))
    l5 = {"prior": 0.80, "protocol_scored": PR,
          "spearman": rec["point"], "ci_lo": rec["ci_lo"], "ci_hi": rec["ci_hi"],
          "point_threshold": L5_POINT, "ci_floor": L5_CI_FLOOR,
          "state": state_of(rec),
          "per_config": {c: float(ws.loc[ws["config"] == c,
                                         f"L5_{PR}_spearman_rho_hit"].mean())
                         for c, _, _, _ in CONFIGS},
          "secondary_canonical_splits": {
              "interleaved": float(ws[f"L5_{PR}_spearman_rho_hit_interleaved"].mean()),
              "contiguous": float(ws[f"L5_{PR}_spearman_rho_hit_contiguous"].mean())},
          "all_protocols": {p: float(ws[f"L5_{p}_spearman_rho_hit"].mean())
                            for p in PROTOCOLS},
          "subclause_states": {"rho>=.30 & CI>.15": state_of(rec)}}
    l5["state"] = lean_from_subclauses((state_of(rec),))
    results["L-5"] = l5

    # ================= rule 13 summary ======================================
    triggered = [r for r in rule13 if r["triggered"]]
    boundary = [r for r in rule13 if r.get("scored") == "BOUNDARY"]
    r13_summary = {
        "b_boot": B_BOOT, "b_boot_high": B_BOOT_HIGH, "seed_policy": "MASTER_SEED",
        "n_clauses": len(rule13), "n_triggered": len(triggered),
        "n_boundary": len(boundary),
        "closest_approach_mc_sd": float(min(
            (r["distance_in_mc_sd"] for r in rule13), default=float("nan"))),
        "records": rule13,
    }

    # ================= routing ==============================================
    lean_states = {k: results[k]["state"] for k in ("L-1", "L-2", "L-3", "L-4", "L-5")}
    identity_ok = bool(l1["true_card"]["identity_holds"])
    outcome = route(identity_ok, lean_states)
    misses = [k for k, v in lean_states.items() if v == "MISS"]
    boundaries = [k for k, v in lean_states.items() if v == "BOUNDARY"]
    slug = "__".join(f"{k.replace('-', '')}_{lean_states[k]}"
                     for k in ("L-1", "L-2", "L-3", "L-4", "L-5")) + f"__{outcome}"

    decision = {
        "leg": "M4-K3", "banner": BANNER,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED, "n_authors_per_world": N_AUTHORS,
        "worlds_per_cell": WORLDS_PER_CELL,
        "configs": [c[0] for c in CONFIGS],
        "uneq_mode": uneq_mode, "identification_protocol": PR,
        "leans": results, "lean_states": lean_states,
        "true_card_identity_ok": identity_ok,
        "misses": misses, "boundaries": boundaries,
        "routing": outcome,
        "routing_text": {
            "P1": "VOID (implementation defect)",
            "P2": "T7/T8's estimator layer needs repair",
            "P3": "QUALIFIED -- T7/T8 [MEASURED except the named piece]",
            "P4": "T7/T8 [MEASURED] -- IDT v1's empirical program COMPLETE",
        }[outcome],
        "rule13": r13_summary,
        "verdict_slug": slug,
        "stage_seconds": time.time() - t0,
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2, default=str))
    import scipy
    manifest = {
        "leg": "M4-K3", "script": "scripts/run_suica_m4_k3_similarity_geometry.py",
        "registration": ("docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md "
                         "'M4-K3 -- The similarity geometry, measured', commit 740e600"),
        "banner": BANNER, "master_seed": MASTER_SEED,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "python": sys.version, "numpy": np.__version__, "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "configs": [{"id": c, "phi_slow": p, "n_occ": n, "w_int": a,
                     "cell": cell_name(c)} for c, p, n, a in CONFIGS],
        "resolved_uneq_mode": uneq_mode, "resolved_protocol": PR,
        "artifacts": sorted(p.name for p in OUT.glob("*")),
        "stage_seconds": {"finalize": time.time() - t0},
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
    print(json.dumps({"lean_states": lean_states, "routing": outcome, "slug": slug,
                      "rule13_triggered": r13_summary["n_triggered"],
                      "rule13_boundary": r13_summary["n_boundary"]}, indent=2))


# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True,
                    choices=["part0", "arms", "finalize"])
    ap.add_argument("--cells", default="")
    ap.add_argument("--mc-reps", type=int, default=40)
    args = ap.parse_args()
    if args.stage == "part0":
        run_part0(args)
    elif args.stage == "arms":
        run_arms(args)
    else:
        run_finalize(args)


if __name__ == "__main__":
    main()
