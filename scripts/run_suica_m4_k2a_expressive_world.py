#!/usr/bin/env python3
"""M4-K2a -- instrument leg: an expressive world (slow state + person x occasion
channel) and the two-split probe validated against designed identities.

Registered spec: docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md section "M4-K2a --
Instrument leg: an expressive world (slow state + person x occasion channel) and
the two-split probe validated" (REGISTERED 2026-08-09, BEFORE RUN, commit
a041ceb). Theory: docs/SUICA_IDENTITY_THEORY_V1.md appendix A (T6' two-split
probe), appendix B (the exact AR variance-of-mean formula), appendix E (why this
leg exists: F2's family has NO person x occasion channel), appendix G.5.

Executor standing: implementation and execution only. Everything below labelled
"RN-n" is a register-note -- an operationalization of something the registration
left open, or a standing-rule-9 instrument resolution -- fixed and written to
reports/SUICA_M4_K2A_EXPRESSIVE_WORLD_REPORT.md Part 0 BEFORE any main arm ran.

THIS LEG ADJUDICATES NO THEORY BRANCH. It builds and validates an instrument.

Reuse boundary (registration: "the extended generator lives in the LEG SCRIPT;
suica_core untouched; f2 imported for its objects, rule-12 naming"):
  - scripts/run_suica_m4_f2_composition.py (f2()): shock_vector (f2:121-126) --
    called unchanged for the common(o) frame channel.
  - suica_core.v8_context_relation_field._orthonormal_loadings -- the frozen
    basis constructor (imported, not reimplemented), exactly as f2:167 uses it.
  - suica_core.v8_realtext_relation_field.stable_bucket (v8:138-140) -- the
    deterministic hash used for every occasion-keyed stream, exactly f2's idiom.
  - The mean_part construction (f2:178), the author-AR recursion (f2:172-176)
    and the latent->64 map (f2:196) are mirrored line-for-line in build_world()
    below with their f2 source lines cited inline.  The mean_part + latent->64
    mirror (which transitively covers the loadings, `z`, `g` and `a`) is
    verified BIT-IDENTICAL against f2's own `generate_world_composed` in the
    `diagnostic` stage's construction audit -- see `mirror_audit` in
    post_hoc_world_bootstrap.json and the report's anomaly (vi) for its timing.
    The AR mirror differs from f2's ONLY in that f2's per-author logistic `phi`
    matrix is replaced by the pinned scalar `phi_slow` the registration demands;
    it is verified by G2a's ACF readback against the pinned value.
  - NEW in this leg (rule 12, cited by THIS file's line numbers in the report):
    shock_int_matrix(), the interaction latent u_int, and s_int.

Stages (foreground, chunked, resumable; artifacts under
results/m4_k2a_expressive_world/):
  --stage part0   G0a/G1a/G2a/G3a/G4a/G5a on RESERVED pilot worlds 9501-9502
                  plus the pure-algebra Part-0 point predictions. Writes
                  gates.json + part0_predictions.csv + part0_tables.md.
                  Refuses to let `arms` run unless every gate passes (P3a).
  --stage arms    the 12 main cells x 8 worlds (--cells selects a subset for
                  chunking). Writes cell_<id>.csv (per-author sufficient
                  statistics) and cells.csv.
  --stage finalize  bootstrap CIs vs the Part-0 predictions, leans V-1..V-3,
                  rule-13 stability rechecks, pivots, decision.json.
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
from suica_core.v8_context_relation_field import _orthonormal_loadings  # noqa: E402

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"

# --- registration-fixed constants -------------------------------------------
MASTER_SEED = 20260815          # registration: "master_seed 20260815"
WORLDS_PER_CELL = 8             # registration: "12 cells x 8 worlds"
PILOT_WORLDS = (9501, 9502)     # RESERVED; disjoint from main world indices 0..7
PHI_SLOW_LEVELS = (0.5, 0.9, 0.98)
N_OCC_LEVELS = (8, 32)
W_INT_ARMS = ("zero", "equal")
B_BOOT = 2000                   # registration G3a: "B = 2000, seed = master_seed"
B_BOOT_HIGH = 20000             # registration G3a: ">=10x B" (rule 13)

# --- register-note RN-3: generator constants, inherited from F2's family -----
# f2's calibrated knobs (f2:816-818): k=48, phi_lo/hi 0.2/0.8 (superseded here by
# the PINNED phi_slow the registration requires), 64 output dims.
K_LATENT = 48
DIM = 64
G_PROFILE = np.linspace(0.85, 0.55, K_LATENT)            # f2:164
A_SCALE = math.sqrt(2.0 / float(np.sum(G_PROFILE**2)))   # f2:165
SIGMA_ISO = math.sqrt(2.0 / float(DIM))                  # f2:166
UNIT_ENTRY_VAR = 2.0 / float(DIM)   # every unit-scale channel's pooled entry variance

# --- register-note RN-1: the occasion/event grid ----------------------------
N_AUTHORS = 256                 # per world
N_REP = 2                       # events per occasion (the same-occasion channel)

OUT = ROOT / "results" / "m4_k2a_expressive_world"
REPORT = ROOT / "reports" / "SUICA_M4_K2A_EXPRESSIVE_WORLD_REPORT.md"

_F2 = None


def f2() -> Any:
    """The M4-F2 script module (shock_vector, the frame-channel source object)."""
    global _F2
    if _F2 is None:
        path = ROOT / "scripts" / "run_suica_m4_f2_composition.py"
        spec = importlib.util.spec_from_file_location("run_suica_m4_f2_composition", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _F2 = module
    return _F2


def read_csv_rt(path: Path) -> pd.DataFrame:
    """G5a: every artifact re-read with float_precision='round_trip'."""
    return pd.read_csv(path, float_precision="round_trip")


# ---------------------------------------------------------------------------
# RN-2: the arm weight vectors.  "weights sum-of-squares normalized per arm";
# "w_int in {0, equal-share}".  Resolution: EVERY ACTIVE CHANNEL CARRIES AN
# EQUAL VARIANCE SHARE, and the sum-of-squares normalization is applied per arm
# (which is exactly what changes when the fifth channel joins).

def arm_weights(w_int_arm: str) -> dict[str, float]:
    if w_int_arm == "zero":
        share = 1.0 / 4.0
        shares = {"mu": share, "slow": share, "int": 0.0, "common": share, "noise": share}
    elif w_int_arm == "equal":
        share = 1.0 / 5.0
        shares = {"mu": share, "slow": share, "int": share, "common": share, "noise": share}
    else:
        raise ValueError(f"unknown w_int arm {w_int_arm!r}")
    return {name: math.sqrt(value) for name, value in shares.items()}


def arm_shares(w_int_arm: str) -> dict[str, float]:
    return {name: weight**2 for name, weight in arm_weights(w_int_arm).items()}


def cell_id(phi_slow: float, n_occ: int, w_int_arm: str) -> str:
    return f"phi{phi_slow:g}_occ{n_occ}_int{w_int_arm}"


def all_cells() -> list[tuple[float, int, str]]:
    return [
        (phi, n_occ, arm)
        for phi in PHI_SLOW_LEVELS
        for n_occ in N_OCC_LEVELS
        for arm in W_INT_ARMS
    ]


def world_seed_for(phi_slow: float, n_occ: int, world: int) -> int:
    """RN-8: the seed depends on (phi, n_occ, world) ONLY -- so the two w_int
    arms of a (phi, n_occ) pair share b, slow, common, noise and the loadings
    a_i bit-for-bit, making the w_int contrast exactly paired."""
    return int(
        v8.stable_bucket(
            f"{MASTER_SEED}-{phi_slow:g}-{n_occ}-{world}",
            salt="m4k2a-world",
            modulus=2**31 - 1,
        )
    )


# ---------------------------------------------------------------------------
# The NEW person x occasion channel (rule 12: this leg's own source object).

def shock_int_matrix(world_seed: int, occasion: int, k: int) -> np.ndarray:
    """S(o) ~ N(0, I) in R^{k x k}: one fresh draw per (world, occasion), keyed
    on a salt DISJOINT from f2's 'm4f2-shock', so the interaction stream is
    independent of common(o) by construction (verified numerically in G0a)."""
    seed = v8.stable_bucket(
        f"{world_seed}-{occasion}", salt="m4k2a-shock-int", modulus=2**63 - 1
    )
    return np.random.default_rng(seed).normal(size=(k, k))


def build_world(
    world_seed: int, n_authors: int, n_occ: int, phi_slow: float
) -> dict[str, np.ndarray]:
    """The extended generator.  Channels are returned SEPARATELY (unit scale,
    each with pooled entry variance 2/64 exactly as in f2); the arm weights are
    applied by the caller, which is what makes the ablation exact.

    x(i,t,o) = w_mu*mean_part_i + w_slow*slow_i(t) + w_int*s_int(i,o)
               + w_c*common(o) + w_e*noise(i,t)
    """
    k = K_LATENT
    rng = np.random.default_rng(world_seed)
    loadings = _orthonormal_loadings(rng, DIM, k)                 # f2:167
    z = rng.normal(size=(n_authors, k))                           # f2:168
    _zeta = rng.normal(size=(n_authors, k))                       # f2:169 (stream order kept)
    # --- slow state: f2:172-176's AR recursion with the PINNED scalar phi_slow,
    #     ticking ONCE PER OCCASION (RN-1; forced by G4a's registered m = n_occ).
    xs = np.empty((n_authors, n_occ, k), dtype=float)
    xs[:, 0] = rng.normal(size=(n_authors, k))                    # f2:173
    innovation_scale = math.sqrt(1.0 - phi_slow**2)               # f2:174
    for t in range(1, n_occ):                                     # f2:175-176
        xs[:, t] = phi_slow * xs[:, t - 1] + innovation_scale * rng.normal(
            size=(n_authors, k)
        )
    noise = rng.normal(size=(n_authors, n_occ, N_REP, DIM))       # f2:177
    # --- trait: f2:178's mean_part with w_mu factored to 1 (weight applied by arm)
    trait = A_SCALE * ((z * G_PROFILE) @ loadings.T)              # (n, 64)
    # --- slow, mapped by f2:196's latent->64 form
    slow = A_SCALE * ((xs * G_PROFILE) @ loadings.T)              # (n, n_occ, 64)
    # --- common(o): f2:121-126's shock_vector, one context (a shared-occasion design)
    common_lat = np.stack(
        [f2().shock_vector(world_seed, "K2A_COMMON", o, k) for o in range(n_occ)]
    )
    common = A_SCALE * ((common_lat * G_PROFILE) @ loadings.T)    # (n_occ, 64)
    # --- s_int(i,o) = <a_i, shock_int(o)> / sqrt(k), mapped by the same f2:196 form
    a_rng = np.random.default_rng(
        v8.stable_bucket(str(world_seed), salt="m4k2a-loading", modulus=2**63 - 1)
    )
    a_load = a_rng.normal(size=(n_authors, k))                    # per-author unit loading
    shocks = np.stack([shock_int_matrix(world_seed, o, k) for o in range(n_occ)])
    u_int = np.einsum("ij,ojl->iol", a_load, shocks) / math.sqrt(k)
    s_int = A_SCALE * ((u_int * G_PROFILE) @ loadings.T)          # (n, n_occ, 64)
    noise_part = SIGMA_ISO * noise                                # (n, n_occ, N_REP, 64)
    return {
        "trait": trait,
        "slow": slow,
        "int": s_int,
        "common": common,
        "noise": noise_part,
        "slow_latent": xs,
        "a_load": a_load,
        "loadings": loadings,
    }


def response_panel(world: dict[str, np.ndarray], w: dict[str, float]) -> np.ndarray:
    """(n, n_occ, N_REP, 64) responses under the arm weights."""
    out = w["noise"] * world["noise"].copy()
    out += w["mu"] * world["trait"][:, None, None, :]
    out += w["slow"] * world["slow"][:, :, None, :]
    out += w["common"] * world["common"][None, :, None, :]
    if w["int"] != 0.0:
        out += w["int"] * world["int"][:, :, None, :]
    return out


def centered_channels(world: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """The deviation field is linear, so centre each channel over authors once.
    common(o) is identical across authors -> its centred panel is EXACTLY 0
    (T3's designed cancellation; reported, not hidden)."""
    return {
        "trait": world["trait"] - world["trait"].mean(axis=0, keepdims=True),
        "slow": world["slow"] - world["slow"].mean(axis=0, keepdims=True),
        "int": world["int"] - world["int"].mean(axis=0, keepdims=True),
        "noise": world["noise"] - world["noise"].mean(axis=0, keepdims=True),
    }


def card(
    cen: dict[str, np.ndarray],
    w: dict[str, float],
    occ: np.ndarray,
    reps: tuple[int, ...],
    with_int: bool = True,
) -> np.ndarray:
    """Per-author card = mean over the (occasion, rep) cells of the deviation."""
    rep_idx = list(reps)
    out = w["mu"] * cen["trait"]
    out = out + w["slow"] * cen["slow"][:, occ, :].mean(axis=1)
    if with_int and w["int"] != 0.0:
        out = out + w["int"] * cen["int"][:, occ, :].mean(axis=1)
    out = out + w["noise"] * cen["noise"][:, occ][:, :, rep_idx].mean(axis=(1, 2))
    return out


# ---------------------------------------------------------------------------
# G4a -- the Part-0 point predictions (pure algebra; no world is generated).

def ar_mean_var(m: int, phi: float) -> float:
    """IDT appendix B, exact: Var(s_bar) = (sigma^2/m^2)[m + 2 sum_{d=1}^{m-1}(m-d) phi^d]
    for m CONSECUTIVE ticks of a unit-variance stationary AR(1)."""
    total = float(m)
    for d in range(1, m):
        total += 2.0 * (m - d) * phi**d
    return total / float(m * m)


def ar_set_var(occ: np.ndarray, phi: float) -> float:
    """Var of the mean of the AR over an ARBITRARY occasion set (exact double sum)."""
    lag = np.abs(occ[:, None] - occ[None, :]).astype(float)
    return float(np.power(phi, lag).sum() / (len(occ) ** 2))


def ar_cross_cov(occ_a: np.ndarray, occ_b: np.ndarray, phi: float) -> float:
    """Cov of the two set-means (exact double sum)."""
    lag = np.abs(occ_a[:, None] - occ_b[None, :]).astype(float)
    return float(np.power(phi, lag).sum() / (len(occ_a) * len(occ_b)))


N_ACF_FAMILY = 6   # 6 distinct (phi_slow, n_occ) pairs; the two w_int arms of a
                   # pair share the world seed, hence an IDENTICAL slow latent.
_ACF_EXP_CACHE: dict[tuple[float, int], float] = {}


def acf_expectation(phi: float, m: int, n_series: int = 400_000) -> float:
    """E[phi_hat] for THIS pooled ratio-of-sums estimator at (phi, m), by an
    independent large Monte-Carlo of the pinned AR itself.  A construction
    check: it uses no world of this leg and touches no hypothesis channel."""
    key = (float(phi), int(m))
    if key in _ACF_EXP_CACHE:
        return _ACF_EXP_CACHE[key]
    rng = np.random.default_rng(
        v8.stable_bucket(f"acfexp-{phi:g}-{m}", salt="m4k2a-acfexp", modulus=2**63 - 1)
    )
    num = den = 0.0
    inn = math.sqrt(1.0 - phi**2)
    block = 50_000
    drawn = 0
    while drawn < n_series:
        take = min(block, n_series - drawn)
        x = np.empty((take, m))
        x[:, 0] = rng.normal(size=take)
        for t in range(1, m):
            x[:, t] = phi * x[:, t - 1] + inn * rng.normal(size=take)
        num += float((x[:, :-1] * x[:, 1:]).sum())
        den += float((x[:, :-1] ** 2).sum())
        drawn += take
    _ACF_EXP_CACHE[key] = num / den
    return _ACF_EXP_CACHE[key]


def splits(n_occ: int) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    half = n_occ // 2
    return {
        "interleaved": (np.arange(0, n_occ, 2), np.arange(1, n_occ, 2)),
        "contiguous": (np.arange(0, half), np.arange(half, n_occ)),
    }


def cell_predictions(phi: float, n_occ: int, w_int_arm: str, n_authors: int) -> dict[str, float]:
    """Every Part-0 point prediction for one cell, from the appendix A/B algebra."""
    sh = arm_shares(w_int_arm)
    A, Bv, C, E = sh["mu"], sh["slow"], sh["int"], sh["noise"]
    half = n_occ // 2
    sp = splits(n_occ)
    out: dict[str, float] = {}
    for name, (s1, s2) in sp.items():
        v_half = ar_set_var(s1, phi)
        v_half2 = ar_set_var(s2, phi)
        c_cross = ar_cross_cov(s1, s2, phi)
        # each half card averages `half` occasions x N_REP events
        den1 = A + Bv * v_half + C / half + E / (half * N_REP)
        den2 = A + Bv * v_half2 + C / half + E / (half * N_REP)
        num = A + Bv * c_cross
        out[f"rho_{name}_pred"] = num / math.sqrt(den1 * den2)
        out[f"ar_var_half_{name}"] = v_half
        out[f"ar_cross_{name}"] = c_cross
    out["gap_pred"] = out["rho_interleaved_pred"] - out["rho_contiguous_pred"]
    # --- trait attenuation on the FULL card (all n_occ occasions, both reps)
    v_full = ar_mean_var(n_occ, phi)          # registration: exact AR sum, m = n_occ
    out["ar_var_full"] = v_full
    var_card = A + Bv * v_full + C / n_occ + E / (n_occ * N_REP)
    out["r_card_b_pred_centered"] = math.sqrt(A) / math.sqrt(var_card)
    out["r_card_b_pred_raw"] = math.sqrt((n_authors - 1) / n_authors) * out[
        "r_card_b_pred_centered"
    ]
    out["card_var_norm_pred"] = var_card
    # --- same-occasion (rep) split on ALL occasions: shares trait + slow + int
    den_rep = A + Bv * v_full + C / n_occ + E / n_occ
    out["rho_same_occ_pred"] = (A + Bv * v_full + C / n_occ) / den_rep
    # --- V-3 quantities, in normalized pooled-covariance units (divided by 2/64)
    fin = 1.0 - 1.0 / n_authors
    out["cov_int_contiguous_pred"] = 0.0
    out["cov_int_interleaved_pred"] = 0.0
    out["cov_int_same_occ_pred"] = C / n_occ * fin
    out["cov_int_same_occ_half_pred"] = C / half * fin
    out["delta_int_unit"] = C / (half * half)     # one shared occasion pair out of m_h^2
    return out


# ---------------------------------------------------------------------------
# Per-author sufficient statistics (everything pooled is a ratio of author sums).

PAIRS = ("interleaved", "contiguous", "same_occ", "same_occ_half")


def pair_cards(
    cen: dict[str, np.ndarray], w: dict[str, float], n_occ: int, with_int: bool
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    sp = splits(n_occ)
    half = n_occ // 2
    both = (0, 1)
    out = {
        "interleaved": (
            card(cen, w, sp["interleaved"][0], both, with_int),
            card(cen, w, sp["interleaved"][1], both, with_int),
        ),
        "contiguous": (
            card(cen, w, sp["contiguous"][0], both, with_int),
            card(cen, w, sp["contiguous"][1], both, with_int),
        ),
        "same_occ": (
            card(cen, w, np.arange(n_occ), (0,), with_int),
            card(cen, w, np.arange(n_occ), (1,), with_int),
        ),
        "same_occ_half": (
            card(cen, w, np.arange(half), (0,), with_int),
            card(cen, w, np.arange(half), (1,), with_int),
        ),
    }
    return out


def suff_stats_for_world(
    world_seed: int, phi: float, n_occ: int, w_int_arm: str, n_authors: int
) -> pd.DataFrame:
    world = build_world(world_seed, n_authors, n_occ, phi)
    w = arm_weights(w_int_arm)
    cen = centered_channels(world)
    rows: dict[str, np.ndarray] = {}
    cards = pair_cards(cen, w, n_occ, with_int=True)
    for name, (c1, c2) in cards.items():
        rows[f"{name}_dot"] = np.einsum("id,id->i", c1, c2)
        rows[f"{name}_n1"] = np.einsum("id,id->i", c1, c1)
        rows[f"{name}_n2"] = np.einsum("id,id->i", c2, c2)
        rows[f"{name}_s1"] = c1.sum(axis=1)
        rows[f"{name}_s2"] = c2.sum(axis=1)
        rows[f"{name}_cos"] = rows[f"{name}_dot"] / np.sqrt(
            rows[f"{name}_n1"] * rows[f"{name}_n2"]
        )
    if w["int"] != 0.0:
        cards0 = pair_cards(cen, w, n_occ, with_int=False)
        for name, (c1, c2) in cards0.items():
            rows[f"{name}_dot_abl"] = np.einsum("id,id->i", c1, c2)
    # --- full card vs the trait
    full = card(cen, w, np.arange(n_occ), (0, 1), with_int=True)
    b_raw = world["trait"]
    b_cen = cen["trait"]
    rows["full_b_dot_raw"] = np.einsum("id,id->i", full, b_raw)
    rows["full_b_dot_cen"] = np.einsum("id,id->i", full, b_cen)
    rows["full_n"] = np.einsum("id,id->i", full, full)
    rows["b_raw_n"] = np.einsum("id,id->i", b_raw, b_raw)
    rows["b_cen_n"] = np.einsum("id,id->i", b_cen, b_cen)
    rows["full_s"] = full.sum(axis=1)
    rows["b_raw_s"] = b_raw.sum(axis=1)
    rows["b_cen_s"] = b_cen.sum(axis=1)
    rows["r_cos_raw"] = rows["full_b_dot_raw"] / np.sqrt(rows["full_n"] * rows["b_raw_n"])
    frame = pd.DataFrame(rows)
    frame.insert(0, "world_seed", world_seed)
    frame.insert(0, "author", np.arange(n_authors))
    return frame


# --- pooled statistics from summed sufficient statistics --------------------

def pooled_stats(sums: np.ndarray, cols: dict[str, int], n_rows: float) -> dict[str, float]:
    def s(name: str) -> np.ndarray:
        return sums[..., cols[name]]

    out: dict[str, Any] = {}
    entries = n_rows * DIM
    for name in PAIRS:
        dot, n1, n2 = s(f"{name}_dot"), s(f"{name}_n1"), s(f"{name}_n2")
        out[f"rho_{name}"] = dot / np.sqrt(n1 * n2)
        s1, s2 = s(f"{name}_s1"), s(f"{name}_s2")
        cov_c = dot - s1 * s2 / entries
        v1 = n1 - s1 * s1 / entries
        v2 = n2 - s2 * s2 / entries
        out[f"rho_{name}_pearson"] = cov_c / np.sqrt(v1 * v2)
        out[f"rho_{name}_cos"] = s(f"{name}_cos") / n_rows
        out[f"cov_{name}_norm"] = dot / entries / UNIT_ENTRY_VAR
        if f"{name}_dot_abl" in cols:
            out[f"covint_{name}"] = (dot - s(f"{name}_dot_abl")) / entries / UNIT_ENTRY_VAR
    out["gap"] = out["rho_interleaved"] - out["rho_contiguous"]
    out["gap_cos"] = out["rho_interleaved_cos"] - out["rho_contiguous_cos"]
    out["gap_pearson"] = out["rho_interleaved_pearson"] - out["rho_contiguous_pearson"]
    out["r_card_b_raw"] = s("full_b_dot_raw") / np.sqrt(s("full_n") * s("b_raw_n"))
    out["r_card_b_cen"] = s("full_b_dot_cen") / np.sqrt(s("full_n") * s("b_cen_n"))
    out["r_card_b_cos"] = s("r_cos_raw") / n_rows
    out["card_var_norm"] = s("full_n") / entries / UNIT_ENTRY_VAR
    if "covint_same_occ_half" in out:
        out["lambda_int_contiguous"] = out["covint_contiguous"] / out["covint_same_occ_half"]
    return out


def bootstrap_cell(
    frame: pd.DataFrame, b_draws: int, seed: int
) -> tuple[dict[str, float], dict[str, np.ndarray]]:
    """Registration: bootstrap over AUTHORS WITHIN WORLD, worlds as strata."""
    keep = [c for c in frame.columns if c not in ("author", "world_seed")]
    cols = {c: i for i, c in enumerate(keep)}
    data = frame[keep].to_numpy(float)
    n_rows = float(len(frame))
    point = pooled_stats(data.sum(axis=0), cols, n_rows)
    worlds = frame["world_seed"].to_numpy()
    strata = [np.flatnonzero(worlds == w) for w in np.unique(worlds)]
    rng = np.random.default_rng(seed)
    reps: dict[str, list[np.ndarray]] = {}
    chunk = 500
    done = 0
    while done < b_draws:
        take = min(chunk, b_draws - done)
        mult = np.zeros((take, len(frame)))
        for idx in strata:
            m = len(idx)
            mult[:, idx] = rng.multinomial(m, np.full(m, 1.0 / m), size=take)
        sums = mult @ data
        block = pooled_stats(sums, cols, n_rows)
        for key, value in block.items():
            reps.setdefault(key, []).append(np.atleast_1d(value))
        done += take
    boots = {key: np.concatenate(value) for key, value in reps.items()}
    return point, boots


def ci_of(boots: np.ndarray) -> tuple[float, float]:
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return float(lo), float(hi)


def mc_sd_of_endpoint(boots: np.ndarray, b_draws: int, alpha: float = 0.025) -> float:
    """Monte-Carlo sd of a bootstrap percentile endpoint (rule 13's trigger scale).

    sd(q_alpha) ~ sqrt(alpha(1-alpha)/B) / f(q_alpha); under a normal reference
    f(q_alpha) = phi(z_alpha)/se, giving the closed form below."""
    se = float(np.std(boots, ddof=1))
    z = abs(float(np.sqrt(2.0) * _erfinv(2.0 * alpha - 1.0)))
    density = math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)
    return math.sqrt(alpha * (1.0 - alpha) / b_draws) / density * se


def _erfinv(y: float) -> float:
    from math import erf

    lo, hi = -6.0, 6.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if erf(mid) < y:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------------
# Stage: part0

def run_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    gates: dict[str, Any] = {
        "leg": "M4-K2a",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "pilot_worlds": list(PILOT_WORLDS),
        "n_authors": N_AUTHORS,
        "n_rep": N_REP,
        "k_latent": K_LATENT,
        "dim": DIM,
    }

    # ---- G4a: the point predictions (pure algebra, BEFORE any world exists)
    pred_rows = []
    for phi, n_occ, arm in all_cells():
        pred = cell_predictions(phi, n_occ, arm, N_AUTHORS)
        pred_rows.append({"cell": cell_id(phi, n_occ, arm), "phi_slow": phi,
                          "n_occ": n_occ, "w_int_arm": arm, **pred})
    preds = pd.DataFrame(pred_rows)
    preds.to_csv(OUT / "part0_predictions.csv", index=False)
    gates["G4a"] = {
        "pass": True,
        "note": "point predictions computed from IDT appendix A/B algebra before arms",
        "n_cells": len(preds),
        "artifact": "part0_predictions.csv",
    }

    # ---- G0a / G1a / G2a on the RESERVED pilot worlds
    g0: dict[str, Any] = {"recon_residual_max": 0.0, "share_dev_abs_max": 0.0,
                          "share_dev_rel_max": 0.0, "mirror_residual_max": 0.0,
                          "stream_corr_abs_max": 0.0, "per_cell": []}
    g1: dict[str, Any] = {"per_cell": []}
    g2: dict[str, Any] = {"per_cell": []}
    pilot_frames: dict[str, pd.DataFrame] = {}

    for phi, n_occ, arm in all_cells():
        cid = cell_id(phi, n_occ, arm)
        w = arm_weights(arm)
        design = arm_shares(arm)
        acc_share = {name: 0.0 for name in design}
        recon = 0.0
        rms_resp: dict[str, float] = {name: 0.0 for name in design}
        rms_card: dict[str, float] = {name: 0.0 for name in design}
        acf_num = acf_den = 0.0
        acf_rows: list[np.ndarray] = []
        stream_corr = 0.0
        frames = []
        for wseed in [world_seed_for(phi, n_occ, w) for w in PILOT_WORLDS]:
            world = build_world(wseed, N_AUTHORS, n_occ, phi)
            resp = response_panel(world, w)
            # G0a (i): exact five-channel reconstruction
            parts = {
                "mu": np.broadcast_to(w["mu"] * world["trait"][:, None, None, :], resp.shape),
                "slow": np.broadcast_to(w["slow"] * world["slow"][:, :, None, :], resp.shape),
                "int": np.broadcast_to(w["int"] * world["int"][:, :, None, :], resp.shape),
                "common": np.broadcast_to(
                    w["common"] * world["common"][None, :, None, :], resp.shape
                ),
                "noise": w["noise"] * world["noise"],
            }
            total = sum(parts.values())
            recon = max(recon, float(np.abs(resp - total).max()))
            # G0a (ii): realized variance shares
            var_ch = {name: float(np.mean(part**2)) for name, part in parts.items()}
            tot_var = sum(var_ch.values())
            for name in design:
                acc_share[name] += var_ch[name] / tot_var / len(PILOT_WORLDS)
            # G0a (iii): the two occasion-keyed streams are independent
            com_lat = np.stack(
                [f2().shock_vector(wseed, "K2A_COMMON", o, K_LATENT) for o in range(n_occ)]
            )
            int_lat = np.einsum(
                "ij,ojl->ol", world["a_load"], np.stack(
                    [shock_int_matrix(wseed, o, K_LATENT) for o in range(n_occ)]
                )
            ) / (math.sqrt(K_LATENT) * N_AUTHORS)
            stream_corr = max(
                stream_corr,
                abs(float(np.corrcoef(com_lat.ravel(), int_lat.ravel())[0, 1])),
            )
            # G1a (rule 10): each channel's presence changes the panels
            cen = centered_channels(world)
            base_card = card(cen, w, np.arange(n_occ), (0, 1), with_int=True)
            for name, part in parts.items():
                rms_resp[name] = max(
                    rms_resp[name], float(np.sqrt(np.mean(part**2)))
                )
            for name in ("mu", "slow", "int", "common", "noise"):
                w2 = dict(w)
                w2[name] = 0.0
                cen2 = dict(cen)
                alt = card(cen2, w2, np.arange(n_occ), (0, 1), with_int=(name != "int"))
                rms_card[name] = max(
                    rms_card[name], float(np.sqrt(np.mean((base_card - alt) ** 2)))
                )
            # G2a: measured lag-1 ACF of the slow latent, pooled over authors+coords.
            # Per-author numerator/denominator kept so the CI is a genuine
            # authors-within-world bootstrap (the registered form).
            xs = world["slow_latent"]
            acf_num += float((xs[:, :-1] * xs[:, 1:]).sum())
            acf_den += float((xs[:, :-1] ** 2).sum())
            acf_rows.append(np.column_stack([
                (xs[:, :-1] * xs[:, 1:]).sum(axis=(1, 2)),
                (xs[:, :-1] ** 2).sum(axis=(1, 2)),
            ]))
            frames.append(
                suff_stats_for_world(wseed, phi, n_occ, arm, N_AUTHORS)
            )
        pilot_frames[cid] = pd.concat(frames, ignore_index=True)
        share_dev_abs = {name: acc_share[name] - design[name] for name in design}
        share_dev_rel = {
            name: (acc_share[name] / design[name] - 1.0) if design[name] > 0 else 0.0
            for name in design
        }
        g0["recon_residual_max"] = max(g0["recon_residual_max"], recon)
        g0["share_dev_abs_max"] = max(
            g0["share_dev_abs_max"], max(abs(v) for v in share_dev_abs.values())
        )
        g0["share_dev_rel_max"] = max(
            g0["share_dev_rel_max"], max(abs(v) for v in share_dev_rel.values())
        )
        g0["stream_corr_abs_max"] = max(g0["stream_corr_abs_max"], stream_corr)
        g0["per_cell"].append({
            "cell": cid, "recon_residual": recon,
            "realized_shares": acc_share, "design_shares": design,
            "share_dev_abs": share_dev_abs, "share_dev_rel": share_dev_rel,
            "stream_corr_abs": stream_corr,
        })
        g1["per_cell"].append({
            "cell": cid, "rms_response_by_channel": rms_resp,
            "rms_card_change_by_channel": rms_card,
        })
        # authors-within-world bootstrap CI for the pooled lag-1 ACF
        acf_data = np.concatenate(acf_rows, axis=0)
        acf_strata = [
            np.arange(i * N_AUTHORS, (i + 1) * N_AUTHORS) for i in range(len(PILOT_WORLDS))
        ]
        rng_acf = np.random.default_rng(MASTER_SEED)
        draws = np.empty(B_BOOT)
        for start in range(0, B_BOOT, 500):
            take = min(500, B_BOOT - start)
            mult = np.zeros((take, len(acf_data)))
            for idx in acf_strata:
                m = len(idx)
                mult[:, idx] = rng_acf.multinomial(m, np.full(m, 1.0 / m), size=take)
            sums = mult @ acf_data
            draws[start:start + take] = sums[:, 0] / sums[:, 1]
        acf_lo, acf_hi = ci_of(draws)
        fw = 100.0 * (0.05 / N_ACF_FAMILY) / 2.0          # Bonferroni over the 6
        acf_lo_fw, acf_hi_fw = (float(x) for x in np.percentile(draws, [fw, 100.0 - fw]))
        g2["per_cell"].append({
            "cell": cid, "phi_pinned": phi, "phi_measured_lag1": acf_num / acf_den,
            "phi_ci_lo": acf_lo, "phi_ci_hi": acf_hi,
            "phi_ci_contains_pinned": bool(acf_lo <= phi <= acf_hi),
            "phi_ci_fw_lo": acf_lo_fw, "phi_ci_fw_hi": acf_hi_fw,
            "phi_ci_fw_contains_pinned": bool(acf_lo_fw <= phi <= acf_hi_fw),
            "phi_ci_fw_contains_estimator_expectation": bool(
                acf_lo_fw <= acf_expectation(phi, n_occ) <= acf_hi_fw
            ),
            "phi_ci_contains_estimator_expectation": bool(
                acf_lo <= acf_expectation(phi, n_occ) <= acf_hi
            ),
            "estimator_expectation_mc": acf_expectation(phi, n_occ),
            "live_shares": {n: acc_share[n] for n in design if design[n] > 0},
        })

    # G1a (ii): the two w_int arms differ, paired on identical seeds
    arm_gaps = []
    for phi in PHI_SLOW_LEVELS:
        for n_occ in N_OCC_LEVELS:
            wseed = world_seed_for(phi, n_occ, PILOT_WORLDS[0])
            world = build_world(wseed, N_AUTHORS, n_occ, phi)
            r0 = response_panel(world, arm_weights("zero"))
            r1 = response_panel(world, arm_weights("equal"))
            cen = centered_channels(world)
            c0 = card(cen, arm_weights("zero"), np.arange(n_occ), (0, 1), True)
            c1 = card(cen, arm_weights("equal"), np.arange(n_occ), (0, 1), True)
            arm_gaps.append({
                "phi_slow": phi, "n_occ": n_occ,
                "rms_response_arm_gap": float(np.sqrt(np.mean((r0 - r1) ** 2))),
                "rms_card_arm_gap": float(np.sqrt(np.mean((c0 - c1) ** 2))),
            })
    g1["w_int_arm_contrast"] = arm_gaps

    # gate verdicts
    # analytic sampling scale of a realized variance share (RN-4's disclosure):
    # a channel built from N independent latent k-vectors has relative sd
    # sqrt(2 sum g^4)/(sum g^2 sqrt(N)); the frame channel common(o) has only
    # n_occ draws per world, which is why it dominates the realized-share spread.
    kappa_g = float(math.sqrt(2.0 * np.sum(G_PROFILE**4)) / np.sum(G_PROFILE**2))
    g0["relative_sd_per_latent_draw"] = kappa_g
    g0["analytic_relative_sd"] = {
        "trait (n_authors x W draws)": kappa_g / math.sqrt(N_AUTHORS * len(PILOT_WORLDS)),
        "common n_occ=8 (n_occ x W draws)": kappa_g / math.sqrt(8 * len(PILOT_WORLDS)),
        "common n_occ=32 (n_occ x W draws)": kappa_g / math.sqrt(32 * len(PILOT_WORLDS)),
    }
    g0["stream_corr_sigma_note"] = {
        "n_occ=8 pairs": 8 * K_LATENT, "sd_n_occ8": 1.0 / math.sqrt(8 * K_LATENT),
        "n_occ=32 pairs": 32 * K_LATENT, "sd_n_occ32": 1.0 / math.sqrt(32 * K_LATENT),
    }
    g0["pass"] = bool(g0["recon_residual_max"] <= 1e-12 and g0["share_dev_abs_max"] <= 0.01)
    g0["criterion"] = "recon residual <= 1e-12 AND |realized share - design| <= 0.01 (absolute; RN-4)"
    non_common = []
    for row in g1["per_cell"]:
        for name, value in row["rms_card_change_by_channel"].items():
            design = arm_shares(row["cell"].split("_int")[-1])
            if name == "common":
                continue
            if design.get(name, 0.0) > 0:
                non_common.append(value)
    g1["min_rms_card_change_nonzero_channels"] = float(min(non_common))
    g1["min_rms_response_arm_gap"] = float(min(r["rms_response_arm_gap"] for r in arm_gaps))
    g1["min_rms_card_arm_gap"] = float(min(r["rms_card_arm_gap"] for r in arm_gaps))
    g1["common_channel_card_residual_max"] = float(
        max(r["rms_card_change_by_channel"]["common"] for r in g1["per_cell"])
    )
    g1["pass"] = bool(
        g1["min_rms_card_change_nonzero_channels"] > 1e-6
        and g1["min_rms_response_arm_gap"] > 1e-6
        and g1["min_rms_card_arm_gap"] > 1e-6
    )
    g1["criterion"] = (
        "every NON-ZERO channel changes the card panel RMS > 1e-6, and the two "
        "w_int arms differ in both response and card panels; the common channel's "
        "card residual is a DESIGNED T3 cancellation (reported, not a gate input)"
    )
    g2["max_abs_phi_error"] = float(
        max(abs(r["phi_measured_lag1"] - r["phi_pinned"]) for r in g2["per_cell"])
    )
    g2["min_live_share"] = float(
        min(min(r["live_shares"].values()) for r in g2["per_cell"])
    )
    gates["G0a"], gates["G1a"], gates["G2a"] = g0, g1, g2

    # ---- G3a: power + rule 11 satisfiability + rule 13 spec, on the pilot
    g3: dict[str, Any] = {"b_draws": B_BOOT, "seed": MASTER_SEED,
                          "b_draws_stability": B_BOOT_HIGH, "per_cell": []}
    delta_rule = {"nu_ladder": [1, 2, 4], "headroom_factor": 2.0}
    for phi, n_occ, arm in all_cells():
        cid = cell_id(phi, n_occ, arm)
        point, boots = bootstrap_cell(pilot_frames[cid], 400, MASTER_SEED)
        pred = cell_predictions(phi, n_occ, arm, N_AUTHORS)
        row: dict[str, Any] = {"cell": cid, "phi_slow": phi, "n_occ": n_occ,
                               "w_int_arm": arm, "pilot_worlds": len(PILOT_WORLDS)}
        for key in ("gap", "r_card_b_raw", "rho_interleaved", "rho_contiguous"):
            se = float(np.std(boots[key], ddof=1))
            row[f"se_{key}"] = se
            row[f"mde_{key}"] = 2.8 * se
            row[f"halfwidth_{key}"] = 1.96 * se
        if arm == "equal":
            half = n_occ // 2
            se = float(np.std(boots["covint_contiguous"], ddof=1))
            # the occasion-level component the author bootstrap CANNOT see
            # (analytic: tr(S(o)S(o')^T)/k^2 has sd 1/k per occasion pair)
            occ_sd = 1.0 / (half * K_LATENT) / math.sqrt(WORLDS_PER_CELL)
            occ_sd_pilot = 1.0 / (half * K_LATENT) / math.sqrt(len(PILOT_WORLDS))
            share = arm_shares(arm)["int"]
            tot_hw = 1.96 * math.sqrt(se**2 + occ_sd_pilot**2)
            main_hw = 1.96 * math.sqrt((se * math.sqrt(len(PILOT_WORLDS) / WORLDS_PER_CELL))**2
                                       + occ_sd**2)
            row["se_covint_contiguous_authorboot"] = se
            row["occ_level_sd_analytic_main"] = occ_sd
            row["halfwidth_covint_contiguous_pilot_total"] = tot_hw
            row["halfwidth_covint_contiguous_main_projected"] = main_hw
            chosen = None
            for nu in delta_rule["nu_ladder"]:
                if nu * pred["delta_int_unit"] >= delta_rule["headroom_factor"] * main_hw:
                    chosen = nu
                    break
            row["delta_int_unit"] = pred["delta_int_unit"]
            row["nu_chosen"] = chosen
            row["delta_int_margin"] = (chosen or delta_rule["nu_ladder"][-1]) * pred["delta_int_unit"]
            row["v3a_satisfiable"] = chosen is not None
            se_same = float(np.std(boots["covint_same_occ"], ddof=1))
            row["se_covint_same_occ"] = se_same
            row["v3b_z_predicted"] = pred["cov_int_same_occ_pred"] / max(se_same, 1e-18)
            row["v3b_satisfiable"] = bool(row["v3b_z_predicted"] > 1.96)
        g3["per_cell"].append(row)
    g3["delta_rule"] = delta_rule
    g3["v3a_all_satisfiable"] = all(
        r.get("v3a_satisfiable", True) for r in g3["per_cell"]
    )
    g3["v3b_all_satisfiable"] = all(
        r.get("v3b_satisfiable", True) for r in g3["per_cell"]
    )
    g3["directions"] = {
        "V-1": "two-sided: measured gap CI must CONTAIN the Part-0 prediction (>=10/12 cells); "
               "plus exact ordering match of the 6 (phi,n_occ) cells within each w_int arm",
        "V-2": "two-sided: measured r(card->b) CI must CONTAIN the prediction (>=10/12 cells)",
        "V-3a": "ONE-SIDED UPPER: the int channel cannot add negative reproducible covariance "
                "by construction, so the clause is upper-CI < +delta (two-sided TOST reported "
                "as a second reading)",
        "V-3b": "ONE-SIDED LOWER: predicted positive, so the clause is lower-CI > 0",
    }
    g3["pass"] = bool(g3["v3a_all_satisfiable"] and g3["v3b_all_satisfiable"])
    gates["G3a"] = g3

    # ---- G5a: hygiene
    ordering_pred = {}
    for arm in W_INT_ARMS:
        sub = preds[preds["w_int_arm"] == arm].sort_values("gap_pred", ascending=False)
        ordering_pred[arm] = list(sub["cell"])
    gates["G5a"] = {
        "pass": True,
        "round_trip_parsing_everywhere": True,
        "float_precision": "round_trip",
        "rule12_source_objects": {
            "mean_part (trait b)": "scripts/run_suica_m4_f2_composition.py:178 "
                                   "(mirrored at this script's build_world, w_mu factored to 1)",
            "author AR slow state": "scripts/run_suica_m4_f2_composition.py:172-176 "
                                    "(mirrored with the pinned scalar phi_slow)",
            "common(o) frame channel": "scripts/run_suica_m4_f2_composition.py:121-126 "
                                       "(f2().shock_vector, called unchanged)",
            "latent->64 map": "scripts/run_suica_m4_f2_composition.py:196",
            "noise": "scripts/run_suica_m4_f2_composition.py:177,197",
            "orthonormal basis": "suica_core/v8_context_relation_field.py:78-84",
            "deterministic hash": "suica_core/v8_realtext_relation_field.py:138-140",
            "NEW shock_int_matrix / u_int / s_int": "this script (line numbers cited in the report)",
        },
        "predicted_gap_ordering": ordering_pred,
    }
    gates["part0_all_pass"] = bool(
        gates["G0a"]["pass"] and gates["G1a"]["pass"]
        and gates["G2a"].get("pass", True) and gates["G3a"]["pass"]
    )
    # G2a verdict needs the ACF CI, computed here from the pilot bootstrap of the
    # latent itself; the pooled estimator's ratio bias is O(1/(series*m)) -- see report.
    for key in ("phi_ci_contains_pinned", "phi_ci_fw_contains_pinned",
                "phi_ci_contains_estimator_expectation",
                "phi_ci_fw_contains_estimator_expectation"):
        gates["G2a"][f"cells_{key}"] = int(
            sum(bool(r[key]) for r in gates["G2a"]["per_cell"])
        )
    gates["G2a"]["acf_family_size"] = N_ACF_FAMILY
    gates["G2a"]["max_abs_estimator_bias"] = float(
        max(abs(r["estimator_expectation_mc"] - r["phi_pinned"])
            for r in gates["G2a"]["per_cell"])
    )
    n_cells = len(gates["G2a"]["per_cell"])
    gates["G2a"]["pass"] = bool(
        gates["G2a"]["cells_phi_ci_fw_contains_pinned"] == n_cells
        and gates["G2a"]["min_live_share"] > 0.0
    )
    gates["G2a"]["criterion"] = (
        "registered form ('measured ACF at lag 1 within CI of phi_slow per "
        "cell'), with the CI level and multiplicity treatment pinned by RN-9 "
        "(rule 1: the registration left both open): authors-within-world "
        "bootstrap (B=2000, seed=master_seed), family-wise 95% over the "
        "N_ACF_FAMILY=6 DISTINCT (phi,n_occ) pairs (Bonferroni, per-cell level "
        "0.05/6). The uncorrected per-cell 95% reading is reported alongside "
        "(rule 9: all readings). Plus every non-zero channel's realized share > 0"
    )
    gates["part0_all_pass"] = bool(
        gates["G0a"]["pass"] and gates["G1a"]["pass"]
        and gates["G2a"]["pass"] and gates["G3a"]["pass"]
    )
    gates["stage_seconds"] = time.time() - t0
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n",
                                    encoding="utf-8")
    write_part0_tables(gates, preds)
    write_manifest({"part0": time.time() - t0})
    print(json.dumps({
        "stage": "part0",
        "seconds": round(time.time() - t0, 3),
        "part0_all_pass": gates["part0_all_pass"],
        "G0a": gates["G0a"]["pass"], "G1a": gates["G1a"]["pass"],
        "G2a": gates["G2a"]["pass"], "G3a": gates["G3a"]["pass"],
        "recon_residual_max": gates["G0a"]["recon_residual_max"],
        "share_dev_abs_max": gates["G0a"]["share_dev_abs_max"],
        "share_dev_rel_max": gates["G0a"]["share_dev_rel_max"],
        "max_abs_phi_error": gates["G2a"]["max_abs_phi_error"],
        "min_rms_card_change": gates["G1a"]["min_rms_card_change_nonzero_channels"],
        "common_card_residual_max": gates["G1a"]["common_channel_card_residual_max"],
    }, indent=2))


def write_part0_tables(gates: dict[str, Any], preds: pd.DataFrame) -> None:
    lines: list[str] = []
    lines.append("### G4a prediction table (all 12 cells, computed before arms)\n")
    lines.append("| cell | phi | n_occ | w_int | rho_int pred | rho_cont pred | gap pred | "
                 "r(card->b) pred (raw b) | r pred (centred b) | Var(s_bar) m=n_occ | "
                 "rho same-occ pred |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for _, r in preds.iterrows():
        lines.append(
            f"| `{r['cell']}` | {r['phi_slow']:g} | {int(r['n_occ'])} | {r['w_int_arm']} | "
            f"{r['rho_interleaved_pred']:.10f} | {r['rho_contiguous_pred']:.10f} | "
            f"{r['gap_pred']:.10f} | {r['r_card_b_pred_raw']:.10f} | "
            f"{r['r_card_b_pred_centered']:.10f} | {r['ar_var_full']:.10f} | "
            f"{r['rho_same_occ_pred']:.10f} |"
        )
    lines.append("\n### G0a per-cell construction\n")
    lines.append("| cell | recon residual | max |share dev| (abs) | max |share dev| (rel) | "
                 "stream corr |")
    lines.append("|---|---|---|---|---|")
    for row in gates["G0a"]["per_cell"]:
        lines.append(
            f"| `{row['cell']}` | {row['recon_residual']:.3e} | "
            f"{max(abs(v) for v in row['share_dev_abs'].values()):.6f} | "
            f"{max(abs(v) for v in row['share_dev_rel'].values()):.6f} | "
            f"{row['stream_corr_abs']:.6f} |"
        )
    lines.append("\n### G1a rule-10 non-degeneracy (card-panel RMS change on channel removal)\n")
    lines.append("| cell | mu | slow | int | common (designed T3 cancellation) | noise |")
    lines.append("|---|---|---|---|---|---|")
    for row in gates["G1a"]["per_cell"]:
        c = row["rms_card_change_by_channel"]
        lines.append(
            f"| `{row['cell']}` | {c['mu']:.6e} | {c['slow']:.6e} | {c['int']:.6e} | "
            f"{c['common']:.3e} | {c['noise']:.6e} |"
        )
    lines.append("\n### G1a w_int arm contrast (paired on identical world seeds)\n")
    lines.append("| phi | n_occ | RMS response gap | RMS card gap |")
    lines.append("|---|---|---|---|")
    for row in gates["G1a"]["w_int_arm_contrast"]:
        lines.append(f"| {row['phi_slow']:g} | {row['n_occ']} | "
                     f"{row['rms_response_arm_gap']:.8f} | {row['rms_card_arm_gap']:.8f} |")
    lines.append("\n### G2a rule-3 liveness\n")
    lines.append("| cell | phi pinned | E[phi_hat] (MC, 4e5 series) | phi measured | "
                 "CI95 per-cell | contains | CI family-wise 95% (6 tests) | contains | "
                 "min live share |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for row in gates["G2a"]["per_cell"]:
        lines.append(
            f"| `{row['cell']}` | {row['phi_pinned']:g} | "
            f"{row['estimator_expectation_mc']:.8f} | {row['phi_measured_lag1']:.8f} | "
            f"[{row['phi_ci_lo']:.8f}, {row['phi_ci_hi']:.8f}] | "
            f"{row['phi_ci_contains_pinned']} | "
            f"[{row['phi_ci_fw_lo']:.8f}, {row['phi_ci_fw_hi']:.8f}] | "
            f"{row['phi_ci_fw_contains_pinned']} | "
            f"{min(row['live_shares'].values()):.6f} |"
        )
    lines.append("\n### G3a per-cell MDEs (2-world pilot, B=400 author bootstrap)\n")
    lines.append("| cell | se(gap) | MDE(gap) | se(r) | MDE(r) | delta_int unit | nu | "
                 "margin | V-3a satisfiable | V-3b z | V-3b satisfiable |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for row in gates["G3a"]["per_cell"]:
        lines.append(
            f"| `{row['cell']}` | {row['se_gap']:.8f} | {row['mde_gap']:.8f} | "
            f"{row['se_r_card_b_raw']:.8f} | {row['mde_r_card_b_raw']:.8f} | "
            f"{row.get('delta_int_unit', float('nan')):.8f} | {row.get('nu_chosen')} | "
            f"{row.get('delta_int_margin', float('nan')):.8f} | "
            f"{row.get('v3a_satisfiable')} | {row.get('v3b_z_predicted', float('nan')):.2f} | "
            f"{row.get('v3b_satisfiable')} |"
        )
    (OUT / "part0_tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Stage: arms

def require_part0() -> dict[str, Any]:
    path = OUT / "gates.json"
    if not path.exists():
        raise SystemExit("REFUSED: Part 0 has not run (results/.../gates.json missing).")
    gates = json.loads(path.read_text(encoding="utf-8"))
    if not gates.get("part0_all_pass"):
        raise SystemExit("REFUSED: P3a -- a Part-0 gate failed; no arms may run.")
    if not REPORT.exists():
        raise SystemExit("REFUSED: the Part-0 report has not been written to disk.")
    return gates


def run_arms(args: argparse.Namespace) -> None:
    require_part0()
    t0 = time.time()
    wanted = set(args.cells.split(",")) if args.cells else None
    done = []
    for phi, n_occ, arm in all_cells():
        cid = cell_id(phi, n_occ, arm)
        if wanted and cid not in wanted:
            continue
        frames = [
            suff_stats_for_world(world_seed_for(phi, n_occ, w), phi, n_occ, arm, N_AUTHORS)
            for w in range(WORLDS_PER_CELL)
        ]
        frame = pd.concat(frames, ignore_index=True)
        frame.to_csv(OUT / f"cell_{cid}.csv", index=False)
        done.append(cid)
        print(f"  cell {cid}: {len(frame)} authors  ({time.time() - t0:.1f}s)")
    write_manifest({f"arms[{','.join(done)}]": time.time() - t0})
    print(json.dumps({"stage": "arms", "cells": done,
                      "seconds": round(time.time() - t0, 3)}, indent=2))


# ---------------------------------------------------------------------------
# Stage: finalize

def run_finalize(args: argparse.Namespace) -> None:
    gates = require_part0()
    t0 = time.time()
    preds = read_csv_rt(OUT / "part0_predictions.csv")
    g3_by_cell = {r["cell"]: r for r in gates["G3a"]["per_cell"]}

    rows: list[dict[str, Any]] = []
    stability: list[dict[str, Any]] = []
    for phi, n_occ, arm in all_cells():
        cid = cell_id(phi, n_occ, arm)
        path = OUT / f"cell_{cid}.csv"
        if not path.exists():
            raise SystemExit(f"REFUSED: missing arm artifact {path}")
        frame = read_csv_rt(path)
        point, boots = bootstrap_cell(frame, B_BOOT, MASTER_SEED)
        pred = preds[preds["cell"] == cid].iloc[0].to_dict()
        row: dict[str, Any] = {"cell": cid, "phi_slow": phi, "n_occ": n_occ,
                               "w_int_arm": arm, "n_authors_pooled": len(frame)}
        clause_specs: list[tuple[str, str, float, str]] = []
        for key, pkey in (
            ("gap", "gap_pred"),
            ("rho_interleaved", "rho_interleaved_pred"),
            ("rho_contiguous", "rho_contiguous_pred"),
            ("r_card_b_raw", "r_card_b_pred_raw"),
            ("r_card_b_cen", "r_card_b_pred_centered"),
            ("rho_same_occ", "rho_same_occ_pred"),
            ("gap_cos", "gap_pred"),
            ("gap_pearson", "gap_pred"),
        ):
            lo, hi = ci_of(boots[key])
            row[key] = float(point[key])
            row[f"{key}_lo"] = lo
            row[f"{key}_hi"] = hi
            row[f"{key}_se"] = float(np.std(boots[key], ddof=1))
            row[f"{key}_pred"] = float(pred[pkey])
            row[f"{key}_boot_bias"] = float(np.mean(boots[key]) - point[key])
            row[f"{key}_contains_pred"] = bool(lo <= pred[pkey] <= hi)
            clause_specs.append((key, "contains", float(pred[pkey]), "two-sided"))
        if arm == "equal":
            for key in ("covint_contiguous", "covint_interleaved", "covint_same_occ",
                        "covint_same_occ_half", "lambda_int_contiguous"):
                lo, hi = ci_of(boots[key])
                row[key] = float(point[key])
                row[f"{key}_lo"] = lo
                row[f"{key}_hi"] = hi
                row[f"{key}_se"] = float(np.std(boots[key], ddof=1))
            row["delta_int_margin"] = float(g3_by_cell[cid]["delta_int_margin"])
            row["nu_chosen"] = g3_by_cell[cid]["nu_chosen"]
            row["occ_level_sd_analytic_main"] = float(
                g3_by_cell[cid]["occ_level_sd_analytic_main"]
            )
            # V-3a, ONE-SIDED UPPER at 95%
            up = float(np.percentile(boots["covint_contiguous"], 95.0))
            row["covint_contiguous_upper95_1sided"] = up
            row["v3a_pass_registered"] = bool(up < row["delta_int_margin"])
            # second reading: widen by the analytic occasion-level sd the author
            # bootstrap cannot see (disclosed in Part 0)
            up_wide = row["covint_contiguous"] + 1.6448536269514722 * math.sqrt(
                row["covint_contiguous_se"] ** 2 + row["occ_level_sd_analytic_main"] ** 2
            )
            row["covint_contiguous_upper95_occ_inflated"] = up_wide
            row["v3a_pass_occ_inflated"] = bool(up_wide < row["delta_int_margin"])
            # two-sided TOST second reading
            row["v3a_pass_tost"] = bool(
                row["covint_contiguous_lo"] > -row["delta_int_margin"]
                and row["covint_contiguous_hi"] < row["delta_int_margin"]
            )
            # V-3b, ONE-SIDED LOWER at 95%
            lo5 = float(np.percentile(boots["covint_same_occ"], 5.0))
            row["covint_same_occ_lower95_1sided"] = lo5
            row["v3b_pass"] = bool(lo5 > 0.0)
            row["covint_same_occ_pred"] = float(pred["cov_int_same_occ_pred"])
            row["covint_same_occ_half_pred"] = float(pred["cov_int_same_occ_half_pred"])
            row["covint_interleaved_upper95_1sided"] = float(
                np.percentile(boots["covint_interleaved"], 95.0)
            )
            clause_specs.append(("covint_contiguous", "upper_lt",
                                 row["delta_int_margin"], "one-sided upper"))
            clause_specs.append(("covint_same_occ", "lower_gt", 0.0, "one-sided lower"))
        # rule 13: Monte-Carlo verdict stability
        boots_hi_cache: dict[str, np.ndarray] | None = None
        for key, kind, boundary, direction in clause_specs:
            arr = boots[key]
            alpha = 0.025 if kind == "contains" else 0.05
            mc = mc_sd_of_endpoint(arr, B_BOOT, alpha)
            if kind == "contains":
                dist = min(abs(boundary - float(np.percentile(arr, 2.5))),
                           abs(boundary - float(np.percentile(arr, 97.5))))
            elif kind == "upper_lt":
                dist = abs(boundary - float(np.percentile(arr, 95.0)))
            else:
                dist = abs(boundary - float(np.percentile(arr, 5.0)))
            if dist <= 2.0 * mc:
                if boots_hi_cache is None:
                    _, boots_hi_cache = bootstrap_cell(frame, B_BOOT_HIGH, MASTER_SEED)
                arr2 = boots_hi_cache[key]
                if kind == "contains":
                    lo2, hi2 = ci_of(arr2)
                    v1 = row[f"{key}_contains_pred"]
                    v2 = bool(lo2 <= boundary <= hi2)
                    endpoints = [lo2, hi2]
                elif kind == "upper_lt":
                    u2 = float(np.percentile(arr2, 95.0))
                    v1 = row["v3a_pass_registered"]
                    v2 = bool(u2 < boundary)
                    endpoints = [u2]
                else:
                    l2 = float(np.percentile(arr2, 5.0))
                    v1 = row["v3b_pass"]
                    v2 = bool(l2 > 0.0)
                    endpoints = [l2]
                stability.append({
                    "cell": cid, "clause": key, "direction": direction,
                    "boundary": boundary, "mc_sd_endpoint_B2000": mc,
                    "distance_to_boundary": dist,
                    "verdict_B2000": v1, "verdict_B20000": v2,
                    "endpoints_B20000": endpoints,
                    "status": "STABLE" if v1 == v2 else "BOUNDARY",
                })
        rows.append(row)
        print(f"  finalized {cid} ({time.time() - t0:.1f}s)")

    cells = pd.DataFrame(rows)
    cells.to_csv(OUT / "cells.csv", index=False)
    if stability:
        pd.DataFrame(stability).to_csv(OUT / "rule13_stability.csv", index=False)

    # ---- leans
    v1_cells = int(cells["gap_contains_pred"].sum())
    ordering: dict[str, Any] = {}
    for arm in W_INT_ARMS:
        sub = cells[cells["w_int_arm"] == arm]
        pred_order = list(sub.sort_values("gap_pred", ascending=False)["cell"])
        meas_order = list(sub.sort_values("gap", ascending=False)["cell"])
        ordering[arm] = {"predicted": pred_order, "measured": meas_order,
                         "match": pred_order == meas_order}
    ordering["all12"] = {
        "predicted": list(cells.sort_values("gap_pred", ascending=False)["cell"]),
        "measured": list(cells.sort_values("gap", ascending=False)["cell"]),
    }
    ordering["all12"]["match"] = (
        ordering["all12"]["predicted"] == ordering["all12"]["measured"]
    )
    v1 = {
        "prior": 0.80,
        "cells_containing_prediction": v1_cells,
        "threshold": 10,
        "ordering": ordering,
        "clause_a": bool(v1_cells >= 10),
        "clause_b": bool(ordering["zero"]["match"] and ordering["equal"]["match"]),
    }
    v1["verdict"] = "HOLD" if (v1["clause_a"] and v1["clause_b"]) else "MISS"
    v2_cells = int(cells["r_card_b_raw_contains_pred"].sum())
    v2 = {
        "prior": 0.80,
        "cells_containing_prediction": v2_cells,
        "cells_containing_prediction_centred_reading": int(
            cells["r_card_b_cen_contains_pred"].sum()
        ),
        "threshold": 10,
        "verdict": "HOLD" if v2_cells >= 10 else "MISS",
    }
    eq = cells[cells["w_int_arm"] == "equal"]
    v3 = {
        "prior": 0.75,
        "n_cells": int(len(eq)),
        "v3a_pass_cells_registered": int(eq["v3a_pass_registered"].sum()),
        "v3a_pass_cells_occ_inflated": int(eq["v3a_pass_occ_inflated"].sum()),
        "v3a_pass_cells_tost": int(eq["v3a_pass_tost"].sum()),
        "v3b_pass_cells": int(eq["v3b_pass"].sum()),
    }
    v3["clause_a"] = bool(v3["v3a_pass_cells_registered"] == len(eq))
    v3["clause_b"] = bool(v3["v3b_pass_cells"] == len(eq))
    v3["verdict"] = "HOLD" if (v3["clause_a"] and v3["clause_b"]) else "MISS"

    v1_fail_cells = list(cells.loc[~cells["gap_contains_pred"], "cell"])
    pivots = {
        "P1a": {"fires": bool(len(v1_fail_cells) >= 3), "failing_cells": v1_fail_cells,
                "consequence": "STOP the K2 line pending theory repair"},
        "P2a": {"fires": bool(v3["verdict"] == "MISS"),
                "consequence": "interaction-channel redesign; NO theory consequence"},
        "P3a": {"fires": False, "consequence": "n/a -- Part 0 passed"},
    }
    boundary = [s for s in stability if s["status"] == "BOUNDARY"]
    verdict_bits = [
        "TWO_SPLIT_PROBE_VALIDATED" if v1["verdict"] == "HOLD" else "TWO_SPLIT_PROBE_MISS",
        "ATTENUATION_ALGEBRA_EXACT" if v2["verdict"] == "HOLD" else "ATTENUATION_ALGEBRA_MISS",
        "INTERACTION_OCCASION_BOUND" if v3["verdict"] == "HOLD" else "INTERACTION_NOT_OCCASION_BOUND",
    ]
    decision = {
        "leg": "M4-K2a",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "banner": BANNER,
        "master_seed": MASTER_SEED,
        "n_cells": int(len(cells)),
        "n_authors_per_world": N_AUTHORS,
        "worlds_per_cell": WORLDS_PER_CELL,
        "leans": {"V-1": v1, "V-2": v2, "V-3": v3},
        "pivots": pivots,
        "rule13": {"triggered": len(stability), "boundary": len(boundary),
                   "records": stability},
        "verdict_slug": "__".join(verdict_bits),
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2, default=str) + "\n",
                                       encoding="utf-8")
    write_manifest({"finalize": time.time() - t0})
    print(json.dumps({k: v for k, v in decision.items() if k != "rule13"}, indent=2,
                     default=str))
    print(f"rule13 triggered={len(stability)} boundary={len(boundary)}")


def run_diagnostic(args: argparse.Namespace) -> None:
    """POST-HOC DIAGNOSTIC, run AFTER the registered adjudication and flagged as
    such.  It writes its own artifact and NEVER touches decision.json.

    Question: the registered CI resamples AUTHORS WITHIN WORLD with worlds as
    strata, so it CONDITIONS on each world's realized occasion-level draws --
    including the interaction channel's per-occasion shock matrices S(o), whose
    realized second moments fluctuate with relative sd ~sqrt(2/k) per occasion.
    A world-level (block) resample includes that component.  Reported as a
    reading only; no lean is re-scored on it.
    """
    require_part0()
    t0 = time.time()
    preds = read_csv_rt(OUT / "part0_predictions.csv")
    keys = ("gap", "rho_interleaved", "rho_contiguous", "r_card_b_raw")
    pkeys = ("gap_pred", "rho_interleaved_pred", "rho_contiguous_pred",
             "r_card_b_pred_raw")
    rows = []
    for phi, n_occ, arm in all_cells():
        cid = cell_id(phi, n_occ, arm)
        frame = read_csv_rt(OUT / f"cell_{cid}.csv")
        cols = {c: i for i, c in enumerate(
            [c for c in frame.columns if c not in ("author", "world_seed")])}
        data = frame[[c for c in frame.columns
                      if c not in ("author", "world_seed")]].to_numpy(float)
        worlds = frame["world_seed"].to_numpy()
        blocks = [np.flatnonzero(worlds == w) for w in np.unique(worlds)]
        per_world = np.stack([data[idx].sum(axis=0) for idx in blocks])
        n_per = float(len(blocks[0]))
        point = pooled_stats(per_world.sum(axis=0), cols, n_per * len(blocks))
        rng = np.random.default_rng(MASTER_SEED)
        pick = rng.integers(0, len(blocks), size=(B_BOOT, len(blocks)))
        sums = per_world[pick].sum(axis=1)
        boots = pooled_stats(sums, cols, n_per * len(blocks))
        pred = preds[preds["cell"] == cid].iloc[0].to_dict()
        row: dict[str, Any] = {"cell": cid, "phi_slow": phi, "n_occ": n_occ,
                               "w_int_arm": arm, "n_world_blocks": len(blocks)}
        for key, pkey in zip(keys, pkeys):
            lo, hi = ci_of(boots[key])
            row[key] = float(point[key])
            row[f"{key}_pred"] = float(pred[pkey])
            row[f"{key}_world_lo"] = lo
            row[f"{key}_world_hi"] = hi
            row[f"{key}_world_se"] = float(np.std(boots[key], ddof=1))
            row[f"{key}_world_contains_pred"] = bool(lo <= pred[pkey] <= hi)
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "post_hoc_world_bootstrap.csv", index=False)
    # --- construction audit (rule 8: a claim about code is a factual claim).
    # f2's OWN generate_world_composed with w_mu=1, w_x=0, w_e=0 emits exactly
    # `mean_part` (f2:196-197's other two terms carry coefficients sqrt(0)=0),
    # so it is a bit-exact oracle for this leg's trait + latent->64 mirror.
    mirror = {"cells": [], "max_abs_residual": 0.0}
    for phi, n_occ in [(p, n) for p in PHI_SLOW_LEVELS for n in N_OCC_LEVELS]:
        wseed = world_seed_for(phi, n_occ, 0)
        mine = build_world(wseed, N_AUTHORS, n_occ, phi)["trait"]
        theirs = f2().generate_world_composed(
            counts=[n_occ] * N_AUTHORS,
            contexts=["K2A_MIRROR"] * N_AUTHORS,
            knobs={"k": K_LATENT, "rho": 0.5, "w_mu": 1.0, "w_x": 0.0,
                   "w_e": 0.0, "phi_lo": phi, "phi_hi": phi},
            kappa=0.5, occasion_mode="shared", world_seed=wseed,
        )
        ref = np.stack([row[0] for row in theirs])       # mean_part, per author
        resid = float(np.abs(mine - ref).max())
        mirror["cells"].append({"phi_slow": phi, "n_occ": n_occ,
                                "max_abs_residual": resid,
                                "bit_identical": bool(resid == 0.0)})
        mirror["max_abs_residual"] = max(mirror["max_abs_residual"], resid)
    mirror["all_bit_identical"] = all(c["bit_identical"] for c in mirror["cells"])
    summary = {
        "note": "POST-HOC diagnostic + post-arms construction audit; NOT a lean "
                "input; registered CI is authors-within-world with worlds as strata",
        "b_draws": B_BOOT, "n_world_blocks": int(WORLDS_PER_CELL),
        "mirror_audit": mirror,
    }
    for key in keys:
        summary[f"{key}_cells_containing_pred_world_block"] = int(
            out[f"{key}_world_contains_pred"].sum()
        )
        summary[f"{key}_cells_containing_pred_world_block_wint0"] = int(
            out.loc[out["w_int_arm"] == "zero", f"{key}_world_contains_pred"].sum()
        )
        summary[f"{key}_cells_containing_pred_world_block_wintEQ"] = int(
            out.loc[out["w_int_arm"] == "equal", f"{key}_world_contains_pred"].sum()
        )
    (OUT / "post_hoc_world_bootstrap.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_manifest({"diagnostic_post_hoc": time.time() - t0})
    print(json.dumps(summary, indent=2))


def write_manifest(stage_times: dict[str, float]) -> None:
    path = OUT / "manifest.json"
    prior = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    prior.setdefault("leg", "M4-K2a")
    prior.setdefault("banner", BANNER)
    prior.setdefault("script", "scripts/run_suica_m4_k2a_expressive_world.py")
    prior.setdefault("master_seed", MASTER_SEED)
    prior.setdefault("worlds_per_cell", WORLDS_PER_CELL)
    prior.setdefault("pilot_worlds", list(PILOT_WORLDS))
    prior.setdefault("n_authors", N_AUTHORS)
    prior.setdefault("n_rep", N_REP)
    prior.setdefault("k_latent", K_LATENT)
    prior.setdefault("phi_slow_levels", list(PHI_SLOW_LEVELS))
    prior.setdefault("n_occ_levels", list(N_OCC_LEVELS))
    prior.setdefault("w_int_arms", list(W_INT_ARMS))
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
    parser.add_argument("--stage", required=True,
                        choices=("part0", "arms", "finalize", "diagnostic"))
    parser.add_argument("--cells", default=None, help="comma-separated cell ids (arms chunking)")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.stage == "part0":
        run_part0(args)
    elif args.stage == "arms":
        run_arms(args)
    elif args.stage == "diagnostic":
        run_diagnostic(args)
    else:
        run_finalize(args)


if __name__ == "__main__":
    main()
