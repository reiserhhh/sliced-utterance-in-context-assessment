#!/usr/bin/env python3
"""M4-K2b -- the T4 branch: card algebra or reader floor?

Registered spec: docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md section "M4-K2b -- The T4
branch: card algebra or reader floor? (dissociation on the validated
instrument)" (REGISTERED 2026-08-09, BEFORE RUN, commit 791034e), together with
the K2a planner adjudication immediately above it, whose TWO RIDERS this leg
binds: (i) read the GAP, never a split half alone; (ii) per-half predictions
need world-block resampling.  Theory: docs/SUICA_IDENTITY_THEORY_V1.md T4 (S3),
appendices A, B, E, G (G.3's F5 truth-object compositions), H.

Executor standing: implementation and execution only.  Everything below labelled
"RN-n" is a register-note -- an operationalization of something the registration
left open, or a standing-rule-9 instrument resolution -- fixed and written to
reports/SUICA_M4_K2B_T4_BRANCH_REPORT.md Part 0 BEFORE any main arm ran.

Reuse boundary (registration: reuse the K2a instrument; do not reimplement):
  * scripts/run_suica_m4_k2a_expressive_world.py (k2a()) -- the VALIDATED
    instrument.  Imported and called: ar_set_var (k2a:291-294), ar_cross_cov
    (k2a:297-300), ar_mean_var (k2a:282-288), shock_int_matrix (k2a:174-181),
    splits (k2a:335-340), bootstrap_cell (k2a:489-516), ci_of (k2a:519-521),
    mc_sd_of_endpoint (k2a:524-532), read_csv_rt (k2a:118-120), build_world /
    suff_stats_for_world / world_seed_for / cell_id (k2a:184-236, 417-454,
    158-168, 145-146) for G0b's bit-exact re-derivation, and the generator
    constants K_LATENT/DIM/G_PROFILE/A_SCALE/SIGMA_ISO/UNIT_ENTRY_VAR
    (k2a:89-94).  `k2a.bootstrap_cell` is invoked under ONE disclosed
    single-object patch (`k2a.pooled_stats` -> this file's
    `pooled_card_stats`), the K1 precedent for machinery reuse under a named
    substitution; the resampling scheme itself is k2a's, unmodified.
  * scripts/run_suica_m4_f2_composition.py (f2()) -- build_layout_common
    (f2:205-222) for the K1-pinned panel, shock_vector (f2:121-126) for the
    frame channel, run_axis1_world (f2:276-370) for G0b's pure-F2 sanity world,
    MIN_RETAINED_EVENTS.
  * scripts/run_suica_m4_f1_panel_sizing.py (f1()) -- load_spec, _directions,
    featurize_panel (f1:166-229), build_layout, e1().
  * scripts/run_suica_m4_e1_convention_gap.py via f1().e1() -- calibrate_d0_soft
    (e1:160-180), project_soft (e1:183-192), deployed_soft_field (e1:230-242),
    field_agreement (e1:245-258), resolved_contexts.  The truth-field
    construction follows f5:225-372 / f5:494 / f5:505 (M4-F5's
    field_from_vectors + truth-variant pattern), with mean_part-only responses.
  * suica_core/ is READ-ONLY and untouched.
  * NEW in this leg (rule 12, line numbers cited in the report at commit):
    build_k2b_world, emit_panel, card_channel_frame, pooled_card_stats,
    arm_weights, arm_predictions, run_field_world.

Stages (foreground, chunked, resumable; artifacts under
results/m4_k2b_t4_branch/):
  --stage part0    G0b..G5b on RESERVED pilot worlds 9601-9602 plus ALL Part-0
                   point predictions.  Writes gates.json, part0_predictions.csv,
                   part0_tables.md.  Refuses to let `arms` run unless every gate
                   passes AND the Part-0 report exists on disk (P3a analogue).
  --stage arms     the 6 primary arms + 1 descriptive companion x 8 worlds
                   (--arms selects a subset for chunking).  Writes
                   arm_<id>_card.csv and arm_<id>_field.csv.
  --stage finalize per-arm CIs vs the Part-0 predictions, L-A/L-B/L-C/PARTIAL/
                   L-D, rule-13 stability, pivots, decision.json.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import itertools
import json
import math
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
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
MASTER_SEED = 20260816            # registration: "master_seed 20260816"
WORLDS_PER_CELL = 8               # registration: "8 worlds each"
ESCALATION_LADDER = (8, 16, 32)   # registration G1b: "8->16->32 once each"
PILOT_WORLDS = (9601, 9602)       # RESERVED; disjoint from main indices 0..7
B_BOOT = 2000                     # registration G3b: "B=2000, seed=master"
B_BOOT_HIGH = 20000               # registration G3b: ">=10xB" (rule 13)

# ARMS: (id, state share, phi_slow, w_int arm, primary?)
ARMS: tuple[tuple[str, float, float, str, bool], ...] = (
    ("A1", 0.02, 0.90, "zero", True),
    ("A2", 0.10, 0.90, "zero", True),
    ("A3", 0.30, 0.90, "zero", True),
    ("A4", 0.50, 0.90, "zero", True),
    ("A5", 0.30, 0.98, "zero", True),
    ("A6", 0.50, 0.98, "zero", True),
    ("C1", 0.30, 0.90, "equal", False),   # descriptive companion cell, no gate
)
PRIMARY_ARMS = tuple(a[0] for a in ARMS if a[4])
EXTREME_LO, EXTREME_HI = "A1", "A4"       # registration: "extreme-arm swing (A1 vs A4)"

# --- RN-3: the variance budget, anchored to the deployed gauge's own knobs ----
# f1's calibrated selection (results/m4_f1_panel_sizing/calibration_record.json,
# knob_tag k48-r0.50-mu0.15-x0.15-e0.70-p0.20_0.80) fixes w_e = 0.70 and, at
# F2's kappa=1.0 shared design, an exactly 1:1 trait:frame split of the
# remaining 0.30.  K2b holds BOTH invariants at every arm and spends only the
# state share, which is the registered lever.
NOISE_SHARE = 0.70
SIGNAL_SHARE = 1.0 - NOISE_SHARE     # "non-noise signal variance" = 0.30

# --- generator constants, inherited from K2a/F2's family (rule 12) -----------
_K2A: Any = None
_F2: Any = None
_F1: Any = None


def _load_script(name: str) -> Any:
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def k2a() -> Any:
    global _K2A
    if _K2A is None:
        _K2A = _load_script("run_suica_m4_k2a_expressive_world.py")
    return _K2A


def f2() -> Any:
    global _F2
    if _F2 is None:
        _F2 = _load_script("run_suica_m4_f2_composition.py")
    return _F2


def f1() -> Any:
    global _F1
    if _F1 is None:
        _F1 = f2().f1()
    return _F1


K_LATENT = 48
DIM = 64
G_PROFILE = np.linspace(0.85, 0.55, K_LATENT)            # f2:164
A_SCALE = math.sqrt(2.0 / float(np.sum(G_PROFILE**2)))   # f2:165
SIGMA_ISO = math.sqrt(2.0 / float(DIM))                  # f2:166

OUT = ROOT / "results" / "m4_k2b_t4_branch"
REPORT = ROOT / "reports" / "SUICA_M4_K2B_T4_BRANCH_REPORT.md"
F1_OUT = ROOT / "results" / "m4_f1_panel_sizing"
REF_PATH = F1_OUT / "realtext_panel_reference.json"
F1_CALIBRATION = F1_OUT / "calibration_record.json"
K2A_OUT = ROOT / "results" / "m4_k2a_expressive_world"
K1D_CELLS = ROOT / "results" / "m4_k1d_replicate_axis" / "cell_intact_x1.csv"

# t-quantiles for the registered paired n=8 design (df = 7), so the MDE needs no
# scipy: MDE(80%, alpha=.05, paired, n) = (t_{.975,n-1} + t_{.80,n-1}) sd/sqrt(n).
T_QUANTILES = {
    8: (2.3646242510102993, 0.8964524689399171),
    16: (2.131449545559323, 0.8662460330515046),
    32: (2.0395134463964077, 0.8534705711311653),
}


def mde_paired(sd_diff: float, n: int) -> float:
    t_alpha, t_beta = T_QUANTILES[n]
    return (t_alpha + t_beta) * sd_diff / math.sqrt(n)


def read_csv_rt(path: Path) -> pd.DataFrame:
    """G5b: every artifact re-read with float_precision='round_trip' (k2a:118)."""
    return pd.read_csv(path, float_precision="round_trip")


# ---------------------------------------------------------------------------
# RN-2 -- the arm weight vectors.
#
# Registration: "share = w_slow^2 fraction of non-noise signal variance;
# w_int = 0 primary; one descriptive companion cell (.30, .9, w_int
# equal-share)".  Resolution (rule 9, both readings impossible -- only one is
# arithmetically live):
#   non-noise signal variance V_s := w_mu^2 + w_slow^2 + w_int^2 + w_c^2, held
#   FIXED at 1 - w_e^2 = 0.30 (RN-3); w_slow^2 = share * V_s; the remaining
#   (1-share)*V_s is split EQUALLY over the ACTIVE non-state signal channels --
#   {mu, common} in the primary arms (preserving F2's exact 1:1 trait:frame
#   ratio at kappa=1.0), {mu, int, common} in the companion (which is what
#   "w_int equal-share" means: an equal share WITH the other non-state signal
#   channels, so the registered state share is untouched by the companion).

def arm_weights(share: float, w_int_arm: str) -> dict[str, float]:
    b = share * SIGNAL_SHARE
    rest = (1.0 - share) * SIGNAL_SHARE
    if w_int_arm == "zero":
        a = c = rest / 2.0
        i = 0.0
    elif w_int_arm == "equal":
        a = i = c = rest / 3.0
    else:
        raise ValueError(f"unknown w_int arm {w_int_arm!r}")
    shares = {"mu": a, "slow": b, "int": i, "common": c, "noise": NOISE_SHARE}
    return {name: math.sqrt(value) for name, value in shares.items()}


def arm_shares(share: float, w_int_arm: str) -> dict[str, float]:
    return {n: w**2 for n, w in arm_weights(share, w_int_arm).items()}


def arm_record(arm_id: str) -> tuple[str, float, float, str, bool]:
    for row in ARMS:
        if row[0] == arm_id:
            return row
    raise KeyError(arm_id)


def world_seed_for(world: int) -> int:
    """RN-8: the seed depends on the WORLD INDEX ONLY, so every arm shares the
    trait, the slow innovations, the frame shocks, the interaction loadings and
    the noise bit-for-bit -- the arm contrast is exactly paired (k2a RN-8)."""
    return int(
        v8.stable_bucket(f"{MASTER_SEED}-{world}", salt="m4k2b-world", modulus=2**31 - 1)
    )


# ---------------------------------------------------------------------------
# The K1-pinned panel (registration: "985 authors, F2 m-multiset, 4 contexts").

_LAYOUT: dict[str, Any] | None = None


def layout() -> dict[str, Any]:
    global _LAYOUT
    if _LAYOUT is not None:
        return _LAYOUT
    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    aid, ctx, spl, counts, raw = f2().build_layout_common(reference)
    spec = f1().load_spec()
    module = f1().e1()
    meta = pd.DataFrame(
        {"author_id": aid, "context": ctx, "split": spl, "event_count": counts}
    )
    eval_mask = meta["split"].isin(["D1", "D2"]).to_numpy()
    resolved = module.resolved_contexts(meta.loc[eval_mask], spec.minimum_context_authors)
    retained_mask = (
        eval_mask
        & meta["context"].astype(str).isin(resolved).to_numpy()
        & (np.asarray(counts) >= f2().MIN_RETAINED_EVENTS)
    )
    retained_idx = np.flatnonzero(retained_mask)
    retained_ctx = np.asarray([ctx[i] for i in retained_idx], dtype=object)
    ctx_counts = pd.Series(retained_ctx).value_counts()
    weights = {
        c: float(ctx_counts.get(c, 0) / max(1, int(ctx_counts.sum()))) for c in resolved
    }
    contexts_sorted = sorted(set(ctx))
    ctx_index = np.asarray([contexts_sorted.index(c) for c in ctx], dtype=int)
    # RN-5: the card's reference norm cell = (context, event count).  T3's exact
    # cancellation of the frame channel needs a SHARED OCCASION SET, and in this
    # panel the occasion set is determined by (context, m) -- authors with
    # different m average different prefixes of the same frame stream, so a
    # context-only norm would leave an m-dependent frame residue in the card.
    cell_key = np.asarray(
        [f"{ctx[i]}|m{counts[i]}" for i in range(len(aid))], dtype=object
    )
    _LAYOUT = {
        "author_ids": aid,
        "contexts": ctx,
        "splits": spl,
        "counts": np.asarray(counts, dtype=int),
        "raw_counts": np.asarray(raw, dtype=int),
        "metadata": meta,
        "spec": spec,
        "directions": f1()._directions(spec),
        "module": module,
        "resolved": resolved,
        "retained_mask": retained_mask,
        "retained_idx": retained_idx,
        "retained_ids": [aid[i] for i in retained_idx],
        "retained_ctx": retained_ctx,
        "weights": weights,
        "contexts_sorted": contexts_sorted,
        "ctx_index": ctx_index,
        "cell_key": cell_key,
        "t_max": int(max(counts)),
    }
    return _LAYOUT


def retained_cell_sizes() -> dict[str, int]:
    lay = layout()
    keys = lay["cell_key"][lay["retained_idx"]]
    values, counts = np.unique(keys, return_counts=True)
    return {str(k): int(v) for k, v in zip(values, counts)}


# ---------------------------------------------------------------------------
# The K2b world.  A line-for-line mirror of k2a:184-236's build_world, with the
# TWO changes the deployed gauge's input format forces (RN-1):
#   (a) N_REP = 1 -- one event per occasion, occasion label = the author's own
#       local sequential event index, which IS f2's 'shared' design
#       (f2:96-118); the number of occasions is therefore the author's own
#       m_i in {8, 12, 16} rather than one global n_occ;
#   (b) common(o) is keyed on (CONTEXT, occasion) via f2().shock_vector,
#       exactly as F2's shared design at kappa=1.0 does, because the K1-pinned
#       panel has 4 contexts and the deployed field is computed per context.
# The interaction channel reuses k2a.shock_int_matrix UNCHANGED (occasion-keyed
# only), so the companion cell is the same object K2a typed.

def build_k2b_world(world_seed: int, phi_slow: float) -> dict[str, np.ndarray]:
    lay = layout()
    n = len(lay["author_ids"])
    t_max = lay["t_max"]
    k = K_LATENT
    rng = np.random.default_rng(world_seed)
    loadings = _orthonormal_loadings(rng, DIM, k)                  # f2:167
    z = rng.normal(size=(n, k))                                    # f2:168
    _zeta = rng.normal(size=(n, k))                                # f2:169 (stream order)
    xs = np.empty((n, t_max, k), dtype=float)
    xs[:, 0] = rng.normal(size=(n, k))                             # f2:173
    innovation_scale = math.sqrt(1.0 - phi_slow**2)                # f2:174
    for t in range(1, t_max):                                      # f2:175-176
        xs[:, t] = phi_slow * xs[:, t - 1] + innovation_scale * rng.normal(size=(n, k))
    noise = rng.normal(size=(n, t_max, DIM))                       # f2:177
    trait = A_SCALE * ((z * G_PROFILE) @ loadings.T)               # f2:178
    slow = A_SCALE * ((xs * G_PROFILE) @ loadings.T)               # f2:196 form
    common_lat = np.stack([
        np.stack([f2().shock_vector(world_seed, c, o, k) for o in range(t_max)])
        for c in lay["contexts_sorted"]
    ])                                                             # f2:121-126
    common = A_SCALE * ((common_lat * G_PROFILE) @ loadings.T)     # (n_ctx, t_max, 64)
    a_rng = np.random.default_rng(
        v8.stable_bucket(str(world_seed), salt="m4k2b-loading", modulus=2**63 - 1)
    )
    a_load = a_rng.normal(size=(n, k))
    shocks = np.stack([k2a().shock_int_matrix(world_seed, o, k) for o in range(t_max)])
    u_int = np.einsum("ij,ojl->iol", a_load, shocks) / math.sqrt(k)
    s_int = A_SCALE * ((u_int * G_PROFILE) @ loadings.T)           # (n, t_max, 64)
    return {
        "trait": trait,
        "slow": slow,
        "int": s_int,
        "common": common,
        "noise": SIGMA_ISO * noise,
        "slow_latent": xs,
        "a_load": a_load,
    }


CHANNELS = ("mu", "slow", "int", "common", "noise")


def emit_panel(
    world: dict[str, np.ndarray], w: dict[str, float], active: tuple[str, ...] = CHANNELS
) -> list[np.ndarray]:
    """The deployed gauge's input format: a list of (m_i, 64) event streams."""
    lay = layout()
    counts = lay["counts"]
    ctx_index = lay["ctx_index"]
    out: list[np.ndarray] = []
    for i in range(len(counts)):
        m = int(counts[i])
        v = np.zeros((m, DIM), dtype=float)
        if "mu" in active:
            v += w["mu"] * world["trait"][i][None, :]
        if "slow" in active:
            v += w["slow"] * world["slow"][i, :m]
        if "int" in active and w["int"] != 0.0:
            v += w["int"] * world["int"][i, :m]
        if "common" in active:
            v += w["common"] * world["common"][ctx_index[i], :m]
        if "noise" in active:
            v += w["noise"] * world["noise"][i, :m]
        out.append(v)
    return out


# ---------------------------------------------------------------------------
# The CARD channel (positive control, reader-free) -- K2a's two-split probe and
# attenuation, on the retained set, with the (context, m) norm cell of RN-5.

def occ_splits(m: int) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    return k2a().splits(m)          # k2a:335-340, unchanged


def card_channel_frame(
    world: dict[str, np.ndarray], w: dict[str, float], world_seed: int
) -> tuple[pd.DataFrame, float]:
    """Per-author sufficient statistics (k2a:417-454's schema, restricted to the
    two occasion splits).  Returns the frame and the max |centred frame channel|
    (T3's designed cancellation, measured not assumed)."""
    lay = layout()
    counts = lay["counts"]
    cell_key = lay["cell_key"]
    keys = cell_key[lay["retained_idx"]]
    rows: list[dict[str, Any]] = []
    common_residual = 0.0
    for key in sorted(set(map(str, keys))):
        idx = np.asarray(
            [i for i in lay["retained_idx"] if str(cell_key[i]) == key], dtype=int
        )
        m = int(counts[idx[0]])
        assert np.all(counts[idx] == m)
        trait = world["trait"][idx]
        trait_c = trait - trait.mean(axis=0, keepdims=True)
        slow_c = world["slow"][idx, :m] - world["slow"][idx, :m].mean(axis=0, keepdims=True)
        noise_c = world["noise"][idx, :m] - world["noise"][idx, :m].mean(axis=0, keepdims=True)
        int_c = None
        if w["int"] != 0.0:
            int_c = world["int"][idx, :m] - world["int"][idx, :m].mean(axis=0, keepdims=True)
        frame = world["common"][lay["ctx_index"][idx], :m]
        common_residual = max(
            common_residual, float(np.abs(frame - frame.mean(axis=0, keepdims=True)).max())
        )

        def card(occ: np.ndarray) -> np.ndarray:
            out = w["mu"] * trait_c
            out = out + w["slow"] * slow_c[:, occ, :].mean(axis=1)
            if int_c is not None:
                out = out + w["int"] * int_c[:, occ, :].mean(axis=1)
            out = out + w["noise"] * noise_c[:, occ, :].mean(axis=1)
            return out

        sp = occ_splits(m)
        block: dict[str, np.ndarray] = {}
        for name, (s1, s2) in sp.items():
            c1, c2 = card(s1), card(s2)
            block[f"{name}_dot"] = np.einsum("id,id->i", c1, c2)
            block[f"{name}_n1"] = np.einsum("id,id->i", c1, c1)
            block[f"{name}_n2"] = np.einsum("id,id->i", c2, c2)
            block[f"{name}_s1"] = c1.sum(axis=1)
            block[f"{name}_s2"] = c2.sum(axis=1)
            block[f"{name}_cos"] = block[f"{name}_dot"] / np.sqrt(
                block[f"{name}_n1"] * block[f"{name}_n2"]
            )
        full = card(np.arange(m))
        block["full_b_dot_raw"] = np.einsum("id,id->i", full, trait)
        block["full_b_dot_cen"] = np.einsum("id,id->i", full, trait_c)
        block["full_n"] = np.einsum("id,id->i", full, full)
        block["b_raw_n"] = np.einsum("id,id->i", trait, trait)
        block["b_cen_n"] = np.einsum("id,id->i", trait_c, trait_c)
        block["r_cos_raw"] = block["full_b_dot_raw"] / np.sqrt(
            block["full_n"] * block["b_raw_n"]
        )
        sub = pd.DataFrame(block)
        sub.insert(0, "cell_key", key)
        sub.insert(0, "m", m)
        sub.insert(0, "world_seed", world_seed)
        sub.insert(0, "author", idx)
        rows.append(sub)
    return pd.concat(rows, ignore_index=True), common_residual


CARD_PAIRS = ("interleaved", "contiguous")


def pooled_card_stats(
    sums: np.ndarray, cols: dict[str, int], n_rows: float
) -> dict[str, float]:
    """k2a:459-486's pooled_stats, restricted to the two occasion splits (there
    is no same-occasion replicate at N_REP=1).  Identical algebra otherwise."""

    def s(name: str) -> np.ndarray:
        return sums[..., cols[name]]

    out: dict[str, Any] = {}
    entries = n_rows * DIM
    for name in CARD_PAIRS:
        dot, n1, n2 = s(f"{name}_dot"), s(f"{name}_n1"), s(f"{name}_n2")
        out[f"rho_{name}"] = dot / np.sqrt(n1 * n2)
        s1, s2 = s(f"{name}_s1"), s(f"{name}_s2")
        cov_c = dot - s1 * s2 / entries
        v1 = n1 - s1 * s1 / entries
        v2 = n2 - s2 * s2 / entries
        out[f"rho_{name}_pearson"] = cov_c / np.sqrt(v1 * v2)
        out[f"rho_{name}_cos"] = s(f"{name}_cos") / n_rows
    out["gap"] = out["rho_interleaved"] - out["rho_contiguous"]
    out["gap_cos"] = out["rho_interleaved_cos"] - out["rho_contiguous_cos"]
    out["gap_pearson"] = out["rho_interleaved_pearson"] - out["rho_contiguous_pearson"]
    out["r_card_b_raw"] = s("full_b_dot_raw") / np.sqrt(s("full_n") * s("b_raw_n"))
    out["r_card_b_cen"] = s("full_b_dot_cen") / np.sqrt(s("full_n") * s("b_cen_n"))
    out["r_card_b_cos"] = s("r_cos_raw") / n_rows
    return out


@contextlib.contextmanager
def k2a_pooled_stats_patched():
    """DISCLOSED single-object patch (K1 precedent): k2a.bootstrap_cell's
    resampling scheme is reused verbatim with this leg's pooled statistic."""
    module = k2a()
    original = module.pooled_stats
    module.pooled_stats = pooled_card_stats
    try:
        yield
    finally:
        module.pooled_stats = original


def bootstrap_card(frame: pd.DataFrame, b_draws: int, seed: int):
    drop = ("author", "world_seed", "cell_key", "m")
    slim = frame[[c for c in frame.columns if c not in drop] + ["world_seed"]]
    with k2a_pooled_stats_patched():
        return k2a().bootstrap_cell(slim, b_draws, seed)


def bootstrap_card_worldblock(frame: pd.DataFrame, b_draws: int, seed: int):
    """Rider (ii)'s second reading: resample WORLD BLOCKS, not authors."""
    drop = ("author", "world_seed", "cell_key", "m")
    keep = [c for c in frame.columns if c not in drop]
    cols = {c: i for i, c in enumerate(keep)}
    data = frame[keep].to_numpy(float)
    worlds = frame["world_seed"].to_numpy()
    blocks = [np.flatnonzero(worlds == u) for u in np.unique(worlds)]
    per_world = np.stack([data[b].sum(axis=0) for b in blocks])
    n_rows = float(len(frame))
    point = pooled_card_stats(per_world.sum(axis=0), cols, n_rows)
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(blocks), size=(b_draws, len(blocks)))
    boots = pooled_card_stats(per_world[pick].sum(axis=1), cols, n_rows)
    return point, boots


# ---------------------------------------------------------------------------
# Part-0 point predictions (pure algebra; k2a:343-381 generalized over the
# heterogeneous m-multiset and the finite (context, m) norm cell).

def arm_predictions(share: float, phi: float, w_int_arm: str) -> dict[str, float]:
    lay = layout()
    counts = lay["counts"]
    sh = arm_shares(share, w_int_arm)
    A, Bv, C, E = sh["mu"], sh["slow"], sh["int"], sh["noise"]
    sizes = retained_cell_sizes()
    ar_set_var = k2a().ar_set_var
    ar_cross_cov = k2a().ar_cross_cov
    num_b = den_full = den_braw = den_bcen = 0.0
    gnum = {p: 0.0 for p in CARD_PAIRS}
    gd1 = {p: 0.0 for p in CARD_PAIRS}
    gd2 = {p: 0.0 for p in CARD_PAIRS}
    for key, n_cell in sizes.items():
        m = int(key.split("|m")[1])
        kap = 1.0 - 1.0 / n_cell
        v_full = ar_set_var(np.arange(m), phi)
        var_card = A + Bv * v_full + C / m + E / m
        num_b += n_cell * kap * math.sqrt(A)
        den_full += n_cell * kap * var_card
        den_braw += n_cell * 1.0
        den_bcen += n_cell * kap
        half = m // 2
        sp = occ_splits(m)
        for name, (s1, s2) in sp.items():
            gnum[name] += n_cell * kap * (A + Bv * ar_cross_cov(s1, s2, phi))
            gd1[name] += n_cell * kap * (
                A + Bv * ar_set_var(s1, phi) + C / half + E / half
            )
            gd2[name] += n_cell * kap * (
                A + Bv * ar_set_var(s2, phi) + C / half + E / half
            )
    out: dict[str, float] = {
        "share_design": share,
        "phi_slow": phi,
        "w_int_arm": w_int_arm,
        "A_mu": A,
        "B_slow": Bv,
        "C_int": C,
        "Cc_common": sh["common"],
        "E_noise": E,
    }
    for name in CARD_PAIRS:
        out[f"rho_{name}_pred"] = gnum[name] / math.sqrt(gd1[name] * gd2[name])
    out["gap_pred"] = out["rho_interleaved_pred"] - out["rho_contiguous_pred"]
    out["r_card_b_pred_raw"] = num_b / math.sqrt(den_full * den_braw)
    out["r_card_b_pred_cen"] = num_b / math.sqrt(den_full * den_bcen)
    # --- T4-simple's field-recovery prediction (RN-6, PRIMARY = identity link)
    out["field_recovery_pred_identity"] = out["r_card_b_pred_raw"]
    out["field_recovery_pred_squared"] = out["r_card_b_pred_raw"] ** 2
    out["n_authors_retained"] = float(len(lay["retained_idx"]))
    out["n_events_panel"] = float(int(counts.sum()))
    return out


# ---------------------------------------------------------------------------
# The FIELD channel (the deployed gauge).  f5:225-372 / f5:494 / f5:505's
# pattern: the IDENTICAL featurize -> project -> field path, differing only in
# the input.

def field_from_vectors(vectors: list[np.ndarray], calibration: dict[str, Any],
                       corpus: str) -> dict[str, np.ndarray]:
    lay = layout()
    module = lay["module"]
    m, k = f1().featurize_panel(
        vectors, lay["retained_ids"], corpus=corpus, spec=lay["spec"],
        directions=lay["directions"],
    )
    panel = SimpleNamespace(raw={"M": m, "K": k})
    projected = module.project_soft(
        panel, np.ones(len(lay["retained_ids"]), dtype=bool), calibration
    )
    return module.deployed_soft_field(projected, lay["retained_ctx"], lay["resolved"])


def run_field_world(
    arm_id: str, world_index: int, world: dict[str, np.ndarray], w: dict[str, float],
    *, verify: bool = False,
) -> dict[str, Any]:
    lay = layout()
    module = lay["module"]
    corpus = f"m4k2b-{arm_id}-w{world_index}"
    started = time.time()
    vectors = emit_panel(world, w)
    raw_m, raw_k = f1().featurize_panel(
        vectors, lay["author_ids"], corpus=corpus, spec=lay["spec"],
        directions=lay["directions"],
    )
    panel = SimpleNamespace(metadata=lay["metadata"], raw={"M": raw_m, "K": raw_k})
    calibration = module.calibrate_d0_soft(panel)
    projected = module.project_soft(
        SimpleNamespace(raw={"M": raw_m, "K": raw_k}), lay["retained_mask"], calibration
    )
    field_est = module.deployed_soft_field(projected, lay["retained_ctx"], lay["resolved"])
    ridx = lay["retained_idx"]
    full_b = emit_panel(world, w, active=("mu", "common"))
    full_mixed = emit_panel(world, w, active=("mu", "slow", "int", "common"))
    truth_b = [full_b[i] for i in ridx]
    truth_mixed = [full_mixed[i] for i in ridx]
    field_b = field_from_vectors(truth_b, calibration, corpus)
    field_mixed = field_from_vectors(truth_mixed, calibration, corpus)
    row: dict[str, Any] = {
        "arm": arm_id,
        "world": world_index,
        "corpus": corpus,
        "n_authors_total": int(len(lay["author_ids"])),
        "n_retained": int(len(ridx)),
        "n_resolved_contexts": int(len(lay["resolved"])),
        "d0_eff_rank_M": float(calibration["M"].effective_rank),
        "d0_eff_rank_K": float(calibration["K"].effective_rank),
        "recovery_b_only": float(module.field_agreement(field_est, field_b, lay["weights"])),
        "recovery_mixed": float(module.field_agreement(field_est, field_mixed, lay["weights"])),
        "seconds": float(time.time() - started),
    }
    row["recovery_gap_mixed_minus_b"] = row["recovery_mixed"] - row["recovery_b_only"]
    if verify:
        # --- G4b (i): the b-only truth panel, by the LITERAL registered route
        #     (arm weights with w_slow = w_int = w_e = 0), bit-exact vs the
        #     channel-selection route actually used above.
        w_zero = dict(w)
        w_zero["slow"] = w_zero["int"] = w_zero["noise"] = 0.0
        alt_full_b = emit_panel(world, w_zero)
        row["g4b_truth_b_route_residual"] = float(
            max(float(np.abs(truth_b[j] - alt_full_b[i]).max()) for j, i in enumerate(ridx))
        )
        w_ne = dict(w)
        w_ne["noise"] = 0.0
        alt_full_mixed = emit_panel(world, w_ne)
        row["g4b_truth_mixed_route_residual"] = float(
            max(float(np.abs(truth_mixed[j] - alt_full_mixed[i]).max())
                for j, i in enumerate(ridx))
        )
        # --- G4b (ii): five-channel reconstruction of the live panel.
        parts = [emit_panel(world, w, active=(c,)) for c in CHANNELS]
        row["g4b_reconstruction_residual"] = float(
            max(
                float(np.abs(vectors[i] - sum(p[i] for p in parts)).max())
                for i in range(len(vectors))
            )
        )
        # --- G4b (iii): the estimated field via an INDEPENDENT route
        #     (fresh featurize of the retained subset) -- f5:475-486's check.
        field_alt = field_from_vectors([vectors[i] for i in ridx], calibration, corpus)
        row["g4b_estimated_field_route_residual"] = float(
            max(float(np.max(np.abs(field_est[c] - field_alt[c]))) for c in field_est)
        )
        # --- rule-9 disclosure: the STRICT mean_part-only reading of "b-only".
        full_strict = emit_panel(world, w, active=("mu",))
        strict = [full_strict[i] for i in ridx]
        m_s, k_s = f1().featurize_panel(
            strict, lay["retained_ids"], corpus=corpus, spec=lay["spec"],
            directions=lay["directions"],
        )
        field_strict = field_from_vectors(strict, calibration, corpus)
        row["strict_b_only_K_maxabs"] = float(np.max(np.abs(k_s)))
        row["strict_b_only_M_maxabs"] = float(np.max(np.abs(m_s)))
        row["strict_b_only_field_norm_max"] = float(
            max(float(np.linalg.norm(field_strict[c])) for c in field_strict)
        )
        row["b_only_field_norm_min"] = float(
            min(float(np.linalg.norm(field_b[c])) for c in field_b)
        )
        row["recovery_strict_b_only"] = float(
            module.field_agreement(field_est, field_strict, lay["weights"])
        )
        # --- realized variance shares of the emitted panel (G2b).
        var_ch = {
            name: float(np.mean(np.concatenate([b.ravel() for b in p]) ** 2))
            for name, p in zip(CHANNELS, parts)
        }
        total = sum(var_ch.values())
        row["realized_shares"] = {name: value / total for name, value in var_ch.items()}
    return row


# ---------------------------------------------------------------------------
# Spearman with an exact permutation p-value (n = 6 -> 720 orderings).

def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    return float(ra @ rb / math.sqrt((ra @ ra) * (rb @ rb)))


def spearman_exact_p(pred: np.ndarray, meas: np.ndarray) -> tuple[float, float, int]:
    obs = spearman(pred, meas)
    n = len(pred)
    total = 0
    hits = 0
    for perm in itertools.permutations(range(n)):
        total += 1
        if spearman(pred, meas[list(perm)]) >= obs - 1e-12:
            hits += 1
    return obs, hits / total, total


# ---------------------------------------------------------------------------
# Stage: part0

def run_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    lay = layout()
    gates: dict[str, Any] = {
        "leg": "M4-K2b",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "pilot_worlds": list(PILOT_WORLDS),
        "worlds_per_cell": WORLDS_PER_CELL,
        "noise_share": NOISE_SHARE,
        "signal_share": SIGNAL_SHARE,
    }

    # ---- point predictions (pure algebra, BEFORE any world exists)
    pred_rows = []
    for arm_id, share, phi, w_int_arm, primary in ARMS:
        pred = arm_predictions(share, phi, w_int_arm)
        pred_rows.append({"arm": arm_id, "primary": primary, **pred})
    preds = pd.DataFrame(pred_rows)
    preds.to_csv(OUT / "part0_predictions.csv", index=False)

    # ---- G0b: format + consistency anchors
    g0: dict[str, Any] = {}
    calib = json.loads(F1_CALIBRATION.read_text(encoding="utf-8"))
    g0["knob_tag"] = f2().f1().knob_tag(calib["selected"]["knobs"])
    g0["knobs"] = calib["selected"]["knobs"]
    g0["authors_per_world"] = int(len(lay["author_ids"]))
    g0["events_total"] = int(lay["counts"].sum())
    g0["m_multiset"] = {
        int(k): int(v)
        for k, v in sorted(pd.Series(lay["counts"]).value_counts().items())
    }
    g0["contexts"] = sorted(set(lay["contexts"]))
    g0["retained_cell_sizes"] = retained_cell_sizes()

    # (i) K2a bit-exact re-derivation at K2a's seeds
    anchor_cell = ("phi0.9_occ8_intzero", 0.9, 8, "zero")
    cid, a_phi, a_occ, a_arm = anchor_cell
    persisted = read_csv_rt(K2A_OUT / f"cell_{cid}.csv")
    frames = [
        k2a().suff_stats_for_world(
            k2a().world_seed_for(a_phi, a_occ, w), a_phi, a_occ, a_arm, k2a().N_AUTHORS
        )
        for w in range(k2a().WORLDS_PER_CELL)
    ]
    rederived = pd.concat(frames, ignore_index=True)
    shared_cols = [c for c in persisted.columns if c in rederived.columns]
    diffs = {
        c: float(np.max(np.abs(persisted[c].to_numpy(float) - rederived[c].to_numpy(float))))
        for c in shared_cols
    }
    g0["k2a_anchor"] = {
        "cell": cid,
        "rows": int(len(persisted)),
        "columns_compared": len(shared_cols),
        "max_abs_residual": float(max(diffs.values())),
        "bit_exact": bool(max(diffs.values()) == 0.0),
        "worst_column": max(diffs, key=diffs.get),
    }

    # (ii) the gauge accepts the expressive world's panels (pilot world)
    world_pilot = build_k2b_world(world_seed_for(PILOT_WORLDS[0]), 0.9)
    probe = run_field_world(
        "A3", PILOT_WORLDS[0], world_pilot, arm_weights(0.30, "zero"), verify=True
    )
    g0["gauge_accepts_panels"] = True
    g0["retained_authors"] = int(probe["n_retained"])
    g0["resolved_contexts"] = int(probe["n_resolved_contexts"])
    g0["probe_row"] = {k: v for k, v in probe.items() if k != "realized_shares"}

    # (iii) pure-F2 sanity world vs K1d's x1 intact per-world range
    k1d = read_csv_rt(K1D_CELLS)
    k1d_lo = float(k1d["agreement_mean"].min())
    k1d_hi = float(k1d["agreement_mean"].max())
    sanity = {}
    for tag, layout_mode in (("raw", "raw"), ("common", "common")):
        task = {
            "cell": f"k2b_sanity_{tag}", "world": 0, "kappa": 1.0,
            "occasion_mode": "shared", "layout": layout_mode,
            "corpus_tag": "m4k2b-sanity", "seed_group": "k2b_sanity",
            "world_salt": "m4k2b-sanity", "knob_tag": g0["knob_tag"],
            "knobs": g0["knobs"], "draws": 20, "ref_path": str(REF_PATH),
            "budget_label": "base1x",
        }
        res = f2().run_axis1_world(task)
        sanity[tag] = {
            "agreement_mean": res["agreement_mean"],
            "agreement_sd": res["agreement_sd"],
            "n_retained": res["n_retained"],
            "n_events_total": res["n_events_total"],
            "inside_k1d_range": bool(k1d_lo <= res["agreement_mean"] <= k1d_hi),
        }
    g0["pure_f2_sanity"] = {
        "k1d_x1_intact_per_world_range": [k1d_lo, k1d_hi],
        "k1d_x1_intact_cell_mean": float(k1d["agreement_mean"].mean()),
        **sanity,
    }
    g0["criterion"] = (
        "gauge accepts panels AND K2a anchor cell re-derived bit-exactly (residual "
        "== 0.0) AND the raw-layout pure-F2 sanity world's agreement lies inside "
        "K1d's x1 intact per-world range (consistency, not bit-anchor)"
    )
    g0["pass"] = bool(
        g0["k2a_anchor"]["bit_exact"]
        and sanity["raw"]["inside_k1d_range"]
        and g0["retained_authors"] > 0
    )
    gates["G0b"] = g0

    # ---- G4b: truth construction (verified in Part 0, per the K2a convention)
    g4: dict[str, Any] = {
        "truth_b_route_residual": probe["g4b_truth_b_route_residual"],
        "truth_mixed_route_residual": probe["g4b_truth_mixed_route_residual"],
        "reconstruction_residual": probe["g4b_reconstruction_residual"],
        "estimated_field_route_residual": probe["g4b_estimated_field_route_residual"],
        "strict_b_only_K_maxabs": probe["strict_b_only_K_maxabs"],
        "strict_b_only_M_maxabs": probe["strict_b_only_M_maxabs"],
        "strict_b_only_field_norm_max": probe["strict_b_only_field_norm_max"],
        "b_only_field_norm_min": probe["b_only_field_norm_min"],
        "recovery_strict_b_only_pilot": probe["recovery_strict_b_only"],
        "rule12_source_objects": {
            "trait b := mean_part": "scripts/run_suica_m4_f2_composition.py:178 "
                                    "(mirrored in build_k2b_world, w_mu factored out)",
            "slow state (AR, pinned phi)": "scripts/run_suica_m4_f2_composition.py:172-176",
            "frame channel common(context,o)": "scripts/run_suica_m4_f2_composition.py:121-126 "
                                               "(f2().shock_vector, called unchanged)",
            "person x occasion channel": "scripts/run_suica_m4_k2a_expressive_world.py:174-181 "
                                         "(k2a.shock_int_matrix, called unchanged)",
            "latent->64 map": "scripts/run_suica_m4_f2_composition.py:196",
            "orthonormal basis": "suica_core/v8_context_relation_field.py:78-84",
            "panel layout": "scripts/run_suica_m4_f2_composition.py:205-222",
            "deployed featurize": "scripts/run_suica_m4_f1_panel_sizing.py:166-229",
            "deployed field + agreement": "scripts/run_suica_m4_e1_convention_gap.py:230-258",
            "truth-object pattern": "scripts/run_suica_m4_f5_gauge_validity.py:225-372,494,505",
            "two-split probe + attenuation": "scripts/run_suica_m4_k2a_expressive_world.py:"
                                             "282-381,417-486",
        },
    }
    g4["criterion"] = (
        "b-only and mixed truth panels bit-exact (residual == 0.0) against the "
        "LITERAL registered generation (arm weights with w_slow=w_int=w_e=0, and "
        "w_e=0 respectively); five-channel reconstruction exact; estimated field "
        "route-invariant"
    )
    g4["pass"] = bool(
        g4["truth_b_route_residual"] == 0.0
        and g4["truth_mixed_route_residual"] == 0.0
        and g4["reconstruction_residual"] == 0.0
        and g4["estimated_field_route_residual"] <= 1e-12
    )
    gates["G4b"] = g4

    # ---- G2b: rule 10 (arms differ) + rule 3 (lever liveness) on the pilot
    g2: dict[str, Any] = {"per_arm": [], "panel_contrasts": []}
    pilot_worlds_by_phi: dict[tuple[int, float], dict[str, np.ndarray]] = {}

    def pilot_world(w_idx: int, phi: float) -> dict[str, np.ndarray]:
        key = (w_idx, phi)
        if key not in pilot_worlds_by_phi:
            pilot_worlds_by_phi[key] = build_k2b_world(world_seed_for(w_idx), phi)
        return pilot_worlds_by_phi[key]

    pilot_panels: dict[str, list[np.ndarray]] = {}
    pilot_card: dict[str, pd.DataFrame] = {}
    pilot_field: dict[str, list[dict[str, Any]]] = {}
    common_residual_max = 0.0
    for arm_id, share, phi, w_int_arm, primary in ARMS:
        w = arm_weights(share, w_int_arm)
        frames = []
        rows = []
        for w_idx in PILOT_WORLDS:
            world = pilot_world(w_idx, phi)
            frame, cres = card_channel_frame(world, w, world_seed_for(w_idx))
            common_residual_max = max(common_residual_max, cres)
            frames.append(frame)
            rows.append(run_field_world(arm_id, w_idx, world, w,
                                        verify=(w_idx == PILOT_WORLDS[0])))
        pilot_card[arm_id] = pd.concat(frames, ignore_index=True)
        pilot_field[arm_id] = rows
        pilot_panels[arm_id] = emit_panel(pilot_world(PILOT_WORLDS[0], phi), w)
        design = arm_shares(share, w_int_arm)
        realized = rows[0]["realized_shares"]
        g2["per_arm"].append({
            "arm": arm_id,
            "design_shares": design,
            "realized_shares": realized,
            "share_dev_abs": {k: realized[k] - design[k] for k in design},
            "share_dev_abs_max": max(abs(realized[k] - design[k]) for k in design),
            "state_share_design": design["slow"],
            "state_share_realized": realized["slow"],
            "state_share_dev_abs": abs(realized["slow"] - design["slow"]),
        })
    g2["frame_channel_centred_residual_max"] = common_residual_max
    base = pilot_panels[PRIMARY_ARMS[0]]
    for arm_id in PRIMARY_ARMS[1:] + ("C1",):
        other = pilot_panels[arm_id]
        rms = math.sqrt(
            float(np.mean(np.concatenate([
                (base[i] - other[i]).ravel() for i in range(len(base))
            ]) ** 2))
        )
        g2["panel_contrasts"].append({"vs": arm_id, "rms_panel_change": rms})
    g2["min_rms_panel_change"] = float(min(r["rms_panel_change"] for r in g2["panel_contrasts"]))
    g2["share_dev_abs_max"] = float(max(r["share_dev_abs_max"] for r in g2["per_arm"]))
    g2["state_share_dev_abs_max"] = float(max(r["state_share_dev_abs"] for r in g2["per_arm"]))
    # lever liveness: does the manipulation move the CARD channel per prediction?
    pilot_gap = {}
    pilot_r = {}
    for arm_id in PRIMARY_ARMS:
        point, _ = bootstrap_card(pilot_card[arm_id], 1, MASTER_SEED)
        pilot_gap[arm_id] = float(point["gap"])
        pilot_r[arm_id] = float(point["r_card_b_raw"])
    pred_by_arm = {r["arm"]: r for _, r in preds.iterrows()}
    g2["pilot_card_gap"] = pilot_gap
    g2["pilot_card_r"] = pilot_r
    g2["pilot_gap_spearman_vs_pred"] = spearman(
        np.array([pred_by_arm[a]["gap_pred"] for a in PRIMARY_ARMS]),
        np.array([pilot_gap[a] for a in PRIMARY_ARMS]),
    )
    g2["pilot_r_spearman_vs_pred"] = spearman(
        np.array([pred_by_arm[a]["r_card_b_pred_raw"] for a in PRIMARY_ARMS]),
        np.array([pilot_r[a] for a in PRIMARY_ARMS]),
    )
    g2["criterion"] = (
        "arms differ in the emitted panels (RMS > 1e-6); the designed lever moves "
        "the card channel in the PREDICTED order on the pilot (Spearman = 1 on both "
        "gap and attenuation); realized shares within 0.01 ABSOLUTE of design "
        "(K2a/defect-#19's resolution of the ambiguous '1%')"
    )
    g2["pass"] = bool(
        g2["min_rms_panel_change"] > 1e-6
        and g2["share_dev_abs_max"] <= 0.01
        and g2["pilot_gap_spearman_vs_pred"] == 1.0
        and g2["pilot_r_spearman_vs_pred"] == 1.0
    )
    gates["G2b"] = g2

    # ---- G1b: power (rule 2 + the charter's >=3xMDE requirement)
    g1: dict[str, Any] = {"per_arm": [], "link": "identity (RN-6 PRIMARY)"}
    rec = {a: np.array([r["recovery_b_only"] for r in pilot_field[a]]) for a in PRIMARY_ARMS}
    diff = rec[EXTREME_LO] - rec[EXTREME_HI]
    sd_pilot = float(np.std(diff, ddof=1))
    p_identity = float(
        pred_by_arm[EXTREME_LO]["field_recovery_pred_identity"]
        - pred_by_arm[EXTREME_HI]["field_recovery_pred_identity"]
    )
    p_squared = float(
        pred_by_arm[EXTREME_LO]["field_recovery_pred_squared"]
        - pred_by_arm[EXTREME_HI]["field_recovery_pred_squared"]
    )
    ladder = []
    chosen_n = None
    for n_worlds in ESCALATION_LADDER:
        mde = mde_paired(sd_pilot, n_worlds)
        ok = bool(p_identity >= 3.0 * mde)
        ladder.append({"n_worlds": n_worlds, "mde": mde, "ratio_P_over_MDE": p_identity / mde,
                       "meets_3x": ok})
        if ok and chosen_n is None:
            chosen_n = n_worlds
    for arm_id in PRIMARY_ARMS:
        g1["per_arm"].append({
            "arm": arm_id,
            "pred_field_recovery_identity": float(pred_by_arm[arm_id]["field_recovery_pred_identity"]),
            "pred_field_recovery_squared": float(pred_by_arm[arm_id]["field_recovery_pred_squared"]),
            "pred_card_gap": float(pred_by_arm[arm_id]["gap_pred"]),
            "pilot_recovery_b_only": [float(x) for x in rec[arm_id]],
            "pilot_recovery_b_only_mean": float(np.mean(rec[arm_id])),
        })
    g1.update({
        "pilot_worlds": len(PILOT_WORLDS),
        "pilot_paired_diff_A1_minus_A4": [float(x) for x in diff],
        "pilot_paired_sd": sd_pilot,
        "P_identity": p_identity,
        "P_squared": p_squared,
        "mde_ladder": ladder,
        "worlds_selected": chosen_n or ESCALATION_LADDER[-1],
        "abort_report": chosen_n is None,
        "criterion": "predicted extreme-arm swing P (A1 vs A4, identity link) >= "
                     "3 x MDE(80%, alpha=.05, paired, n worlds); escalate 8->16->32 "
                     "once each; ABORT-report if still short at 32",
    })
    g1["pass"] = bool(chosen_n is not None)
    gates["G1b"] = g1

    # ---- G3b: rule 11 satisfiability with directions + rule 13 spec
    g3: dict[str, Any] = {"b_draws": B_BOOT, "seed": MASTER_SEED,
                          "b_draws_stability": B_BOOT_HIGH, "clauses": []}
    n_sel = g1["worlds_selected"]
    se_swing = sd_pilot / math.sqrt(n_sel)   # projected se of the paired swing at n_sel worlds
    card_hw = {}
    for arm_id in PRIMARY_ARMS:
        _, boots = bootstrap_card(pilot_card[arm_id], 400, MASTER_SEED)
        card_hw[arm_id] = {
            "se_gap_pilot": float(np.std(boots["gap"], ddof=1)),
            "se_r_pilot": float(np.std(boots["r_card_b_raw"], ddof=1)),
            "hw_gap_main_projected": 1.96 * float(np.std(boots["gap"], ddof=1)) * math.sqrt(
                len(PILOT_WORLDS) / n_sel
            ),
            "hw_r_main_projected": 1.96 * float(np.std(boots["r_card_b_raw"], ddof=1)) * math.sqrt(
                len(PILOT_WORLDS) / n_sel
            ),
        }
    g3["card_halfwidths"] = card_hw
    g3["clauses"] = [
        {"lean": "L-A", "clause": "per-arm 95% CI of the pooled card GAP CONTAINS the "
                                  "Part-0 prediction, >=5/6 arms",
         "direction": "two-sided (containment)",
         "satisfiable": True,
         "note": f"projected main half-width {min(v['hw_gap_main_projected'] for v in card_hw.values()):.8f}"
                 f"..{max(v['hw_gap_main_projected'] for v in card_hw.values()):.8f}; a "
                 "containment clause is satisfiable for any non-degenerate CI"},
        {"lean": "L-A", "clause": "per-arm 95% CI of the pooled card attenuation "
                                  "r(card->b) CONTAINS the prediction, >=5/6 arms",
         "direction": "two-sided (containment)", "satisfiable": True,
         "note": f"projected main half-width {min(v['hw_r_main_projected'] for v in card_hw.values()):.8f}"
                 f"..{max(v['hw_r_main_projected'] for v in card_hw.values()):.8f}"},
        {"lean": "L-A", "clause": "predicted vs measured ORDERING of the 6 arms exact, on "
                                  "gap and on attenuation",
         "direction": "deterministic", "satisfiable": True,
         "note": "the two predicted orderings differ from each other and neither is the "
                 "share order alone (phi interleaves A5 between A3 and A4 on attenuation)"},
        {"lean": "L-B", "clause": "Spearman(predicted attenuation, measured field recovery) "
                                  "= 1 with exact permutation p <= .005",
         "direction": "one-sided (positive association)", "satisfiable": True,
         "note": "min attainable exact p at n=6 is 1/720 = 0.0013888888888888889 <= .005"},
        {"lean": "L-B", "clause": "S/P in [0.5, 2] AND pooled CI of S/P inside [0.33, 3]",
         "direction": "two-sided", "satisfiable": bool(1.96 * se_swing / p_identity < (3.0 - 0.33) / 2.0),
         "note": f"projected half-width of S/P = {1.96 * se_swing / p_identity:.8f} against "
                 f"the [0.33,3] containment budget 1.335"},
        {"lean": "L-C", "clause": "S < P/3 AND the pooled CI upper endpoint of S < P/2",
         "direction": "one-sided in content (upper bound); evaluated on the 97.5th "
                      "percentile of the registered two-sided CI, with the one-sided 95th "
                      "percentile reported as a second reading",
         "satisfiable": bool(1.96 * se_swing < p_identity / 2.0),
         "note": f"projected 1.96*se(S) = {1.96 * se_swing:.8f}; P/2 = {p_identity / 2.0:.8f}"},
        {"lean": "L-D", "clause": "mixed-truth recovery > b-only recovery in 6/6 arms, with "
                                  "the per-arm 95% CI of the difference excluding 0 in >=5/6",
         "direction": "one-sided in content (predicted positive); evaluated two-sided as "
                      "registered ('CI excluding 0'), one-sided reported alongside",
         "satisfiable": True,
         "note": "pilot per-arm mixed-minus-b differences: " + ", ".join(
             f"{a}={np.mean([r['recovery_gap_mixed_minus_b'] for r in pilot_field[a]]):.6f}"
             for a in PRIMARY_ARMS)},
    ]
    g3["se_swing_projected"] = se_swing
    g3["pass"] = bool(all(c["satisfiable"] for c in g3["clauses"]))
    gates["G3b"] = g3

    # ---- G5b: hygiene
    gates["G5b"] = {
        "pass": True,
        "round_trip_parsing_everywhere": True,
        "float_precision": "round_trip",
        "stages_chunked": ["part0", "arms (--arms selects a subset)", "finalize"],
        "background_jobs": 0,
        "monitors": 0,
        "predicted_orderings": {
            "gap_desc": list(
                preds[preds["primary"]].sort_values("gap_pred", ascending=False)["arm"]
            ),
            "attenuation_desc": list(
                preds[preds["primary"]].sort_values("r_card_b_pred_raw", ascending=False)["arm"]
            ),
        },
    }

    gates["part0_all_pass"] = bool(
        gates["G0b"]["pass"] and gates["G1b"]["pass"] and gates["G2b"]["pass"]
        and gates["G3b"]["pass"] and gates["G4b"]["pass"] and gates["G5b"]["pass"]
    )
    gates["stage_seconds"] = time.time() - t0
    (OUT / "gates.json").write_text(
        json.dumps(gates, indent=2, default=str) + "\n", encoding="utf-8"
    )
    pd.DataFrame([
        {k: v for k, v in r.items() if k != "realized_shares"}
        for arm in ARMS for r in pilot_field[arm[0]]
    ]).to_csv(OUT / "part0_pilot_field.csv", index=False)
    write_part0_tables(gates, preds)
    write_manifest({"part0": time.time() - t0})
    print(json.dumps({
        "stage": "part0",
        "seconds": round(time.time() - t0, 3),
        "part0_all_pass": gates["part0_all_pass"],
        **{g: gates[g]["pass"] for g in ("G0b", "G1b", "G2b", "G3b", "G4b", "G5b")},
        "P_identity": g1["P_identity"],
        "pilot_paired_sd": g1["pilot_paired_sd"],
        "worlds_selected": g1["worlds_selected"],
        "mde_ladder": g1["mde_ladder"],
        "k2a_anchor_residual": g0["k2a_anchor"]["max_abs_residual"],
        "sanity_raw": g0["pure_f2_sanity"]["raw"],
        "k1d_range": g0["pure_f2_sanity"]["k1d_x1_intact_per_world_range"],
    }, indent=2, default=str))


def write_part0_tables(gates: dict[str, Any], preds: pd.DataFrame) -> None:
    lines: list[str] = []
    lines.append("### Part-0 point predictions (all 7 cells, computed before arms)\n")
    lines.append("| arm | share | phi | w_int | A (mu) | B (slow) | C (int) | Cc (frame) | "
                 "rho_int pred | rho_cont pred | GAP pred | r(card->b) pred | "
                 "T4-simple field recovery pred (identity) | (squared) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for _, r in preds.iterrows():
        lines.append(
            f"| `{r['arm']}`{'' if r['primary'] else ' (companion)'} | {r['share_design']:g} | "
            f"{r['phi_slow']:g} | {r['w_int_arm']} | {r['A_mu']:.6f} | {r['B_slow']:.6f} | "
            f"{r['C_int']:.6f} | {r['Cc_common']:.6f} | {r['rho_interleaved_pred']:.10f} | "
            f"{r['rho_contiguous_pred']:.10f} | {r['gap_pred']:.10f} | "
            f"{r['r_card_b_pred_raw']:.10f} | {r['field_recovery_pred_identity']:.10f} | "
            f"{r['field_recovery_pred_squared']:.10f} |"
        )
    lines.append("\n### G2b realized variance shares (pilot world 9601)\n")
    lines.append("| arm | mu | slow | int | common | noise | max |dev| (abs) | state-share dev |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for row in gates["G2b"]["per_arm"]:
        r = row["realized_shares"]
        lines.append(
            f"| `{row['arm']}` | {r['mu']:.8f} | {r['slow']:.8f} | {r['int']:.8f} | "
            f"{r['common']:.8f} | {r['noise']:.8f} | {row['share_dev_abs_max']:.8f} | "
            f"{row['state_share_dev_abs']:.8f} |"
        )
    lines.append("\n### G1b power ladder\n")
    lines.append("| n worlds | MDE(80%, .05, paired) | P/MDE | meets 3x |")
    lines.append("|---|---|---|---|")
    for row in gates["G1b"]["mde_ladder"]:
        lines.append(f"| {row['n_worlds']} | {row['mde']:.8f} | {row['ratio_P_over_MDE']:.4f} | "
                     f"{row['meets_3x']} |")
    lines.append("\n### G3b clause satisfiability with DIRECTIONS (rule 11)\n")
    lines.append("| lean | clause | direction | satisfiable | note |")
    lines.append("|---|---|---|---|---|")
    for c in gates["G3b"]["clauses"]:
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
    n_worlds = int(gates["G1b"]["worlds_selected"])
    t0 = time.time()
    wanted = set(args.arms.split(",")) if args.arms else None
    world_cache: dict[tuple[int, float], dict[str, np.ndarray]] = {}
    done = []
    for arm_id, share, phi, w_int_arm, primary in ARMS:
        if wanted and arm_id not in wanted:
            continue
        w = arm_weights(share, w_int_arm)
        frames, field_rows = [], []
        for world_index in range(n_worlds):
            key = (world_index, phi)
            if key not in world_cache:
                world_cache.clear()
                world_cache[key] = build_k2b_world(world_seed_for(world_index), phi)
            world = world_cache[key]
            frame, _ = card_channel_frame(world, w, world_seed_for(world_index))
            frames.append(frame)
            field_rows.append(run_field_world(arm_id, world_index, world, w))
        pd.concat(frames, ignore_index=True).to_csv(OUT / f"arm_{arm_id}_card.csv", index=False)
        pd.DataFrame(field_rows).to_csv(OUT / f"arm_{arm_id}_field.csv", index=False)
        done.append(arm_id)
        print(f"  arm {arm_id}: {n_worlds} worlds  ({time.time() - t0:.1f}s)")
    write_manifest({f"arms[{','.join(done)}]": time.time() - t0})
    print(json.dumps({"stage": "arms", "arms": done, "worlds": n_worlds,
                      "seconds": round(time.time() - t0, 3)}, indent=2))


# ---------------------------------------------------------------------------
# Stage: finalize

def run_finalize(args: argparse.Namespace) -> None:
    gates = require_part0()
    t0 = time.time()
    preds = read_csv_rt(OUT / "part0_predictions.csv")
    pred_by_arm = {r["arm"]: r for _, r in preds.iterrows()}
    n_worlds = int(gates["G1b"]["worlds_selected"])

    rows: list[dict[str, Any]] = []
    stability: list[dict[str, Any]] = []
    field_by_arm: dict[str, np.ndarray] = {}
    mixed_by_arm: dict[str, np.ndarray] = {}
    for arm_id, share, phi, w_int_arm, primary in ARMS:
        card_path = OUT / f"arm_{arm_id}_card.csv"
        field_path = OUT / f"arm_{arm_id}_field.csv"
        if not card_path.exists() or not field_path.exists():
            raise SystemExit(f"REFUSED: missing arm artifact for {arm_id}")
        card = read_csv_rt(card_path)
        field = read_csv_rt(field_path).sort_values("world")
        field_by_arm[arm_id] = field["recovery_b_only"].to_numpy(float)
        mixed_by_arm[arm_id] = field["recovery_mixed"].to_numpy(float)
        point, boots = bootstrap_card(card, B_BOOT, MASTER_SEED)
        wpoint, wboots = bootstrap_card_worldblock(card, B_BOOT, MASTER_SEED)
        pred = pred_by_arm[arm_id]
        row: dict[str, Any] = {
            "arm": arm_id, "primary": bool(primary), "share_design": share,
            "phi_slow": phi, "w_int_arm": w_int_arm,
            "n_authors_pooled": int(len(card)), "n_worlds": int(len(field)),
        }
        clause_specs: list[tuple[str, float]] = []
        for key, pkey in (("gap", "gap_pred"), ("r_card_b_raw", "r_card_b_pred_raw"),
                          ("rho_interleaved", "rho_interleaved_pred"),
                          ("rho_contiguous", "rho_contiguous_pred"),
                          ("r_card_b_cen", "r_card_b_pred_cen"),
                          ("gap_pearson", "gap_pred"), ("gap_cos", "gap_pred")):
            lo, hi = k2a().ci_of(boots[key])
            row[key] = float(point[key])
            row[f"{key}_lo"], row[f"{key}_hi"] = lo, hi
            row[f"{key}_se"] = float(np.std(boots[key], ddof=1))
            row[f"{key}_pred"] = float(pred[pkey])
            row[f"{key}_err"] = float(point[key]) - float(pred[pkey])
            row[f"{key}_contains_pred"] = bool(lo <= pred[pkey] <= hi)
            wlo, whi = k2a().ci_of(wboots[key])
            row[f"{key}_world_lo"], row[f"{key}_world_hi"] = wlo, whi
            row[f"{key}_world_contains_pred"] = bool(wlo <= pred[pkey] <= whi)
            if key in ("gap", "r_card_b_raw"):
                clause_specs.append((key, float(pred[pkey])))
        row["recovery_b_only_mean"] = float(np.mean(field_by_arm[arm_id]))
        row["recovery_b_only_sd"] = float(np.std(field_by_arm[arm_id], ddof=1))
        row["recovery_mixed_mean"] = float(np.mean(mixed_by_arm[arm_id]))
        row["recovery_mixed_sd"] = float(np.std(mixed_by_arm[arm_id], ddof=1))
        row["pred_field_recovery_identity"] = float(pred["field_recovery_pred_identity"])
        row["pred_field_recovery_squared"] = float(pred["field_recovery_pred_squared"])
        rows.append(row)
        # rule 13 on the two gated card clauses
        for key, boundary in clause_specs:
            arr = boots[key]
            mc = k2a().mc_sd_of_endpoint(arr, B_BOOT, 0.025)
            dist = min(abs(boundary - float(np.percentile(arr, 2.5))),
                       abs(boundary - float(np.percentile(arr, 97.5))))
            if dist <= 2.0 * mc:
                _, hi_boots = bootstrap_card(card, B_BOOT_HIGH, MASTER_SEED)
                lo2, hi2 = k2a().ci_of(hi_boots[key])
                v2 = bool(lo2 <= boundary <= hi2)
                stability.append({
                    "arm": arm_id, "clause": f"{key} contains prediction",
                    "direction": "two-sided", "boundary": boundary,
                    "mc_sd_endpoint_B2000": mc, "distance_to_boundary": dist,
                    "verdict_B2000": row[f"{key}_contains_pred"], "verdict_B20000": v2,
                    "endpoints_B20000": [lo2, hi2],
                    "status": "STABLE" if row[f"{key}_contains_pred"] == v2 else "BOUNDARY",
                })
        print(f"  finalized {arm_id} ({time.time() - t0:.1f}s)")

    cells = pd.DataFrame(rows)
    cells.to_csv(OUT / "cells.csv", index=False)
    prim = cells[cells["primary"]].set_index("arm").loc[list(PRIMARY_ARMS)].reset_index()

    # ---- world-block paired bootstrap over the field channel (shared indices)
    rng = np.random.default_rng(MASTER_SEED)
    pick = rng.integers(0, n_worlds, size=(B_BOOT, n_worlds))
    boot_rec = {a: field_by_arm[a][pick].mean(axis=1) for a in PRIMARY_ARMS}
    boot_mix = {a: mixed_by_arm[a][pick].mean(axis=1) for a in PRIMARY_ARMS}
    rng_hi = np.random.default_rng(MASTER_SEED)
    pick_hi = rng_hi.integers(0, n_worlds, size=(B_BOOT_HIGH, n_worlds))

    # ---- L-A: the positive control
    gap_contain = int(prim["gap_contains_pred"].sum())
    r_contain = int(prim["r_card_b_raw_contains_pred"].sum())
    ordering = {}
    for key in ("gap", "r_card_b_raw"):
        pkey = f"{key}_pred"
        pred_order = list(prim.sort_values(pkey, ascending=False)["arm"])
        meas_order = list(prim.sort_values(key, ascending=False)["arm"])
        ordering[key] = {"predicted": pred_order, "measured": meas_order,
                         "match": pred_order == meas_order}
    l_a = {
        "prior": 0.85,
        "gap_cells_containing_prediction": gap_contain,
        "attenuation_cells_containing_prediction": r_contain,
        "threshold": 5,
        "ordering": ordering,
        "gap_cells_containing_prediction_worldblock": int(prim["gap_world_contains_pred"].sum()),
        "attenuation_cells_containing_prediction_worldblock": int(
            prim["r_card_b_raw_world_contains_pred"].sum()
        ),
        "clause_containment": bool(gap_contain >= 5 and r_contain >= 5),
        "clause_ordering": bool(ordering["gap"]["match"] and ordering["r_card_b_raw"]["match"]),
    }
    l_a["verdict"] = "HOLD" if (l_a["clause_containment"] and l_a["clause_ordering"]) else "MISS"

    # ---- the swing and the ordering of the field channel
    p_identity = float(gates["G1b"]["P_identity"])
    p_squared = float(gates["G1b"]["P_squared"])
    s_point = float(np.mean(field_by_arm[EXTREME_LO]) - np.mean(field_by_arm[EXTREME_HI]))
    s_boot = boot_rec[EXTREME_LO] - boot_rec[EXTREME_HI]
    s_lo, s_hi = k2a().ci_of(s_boot)
    s_one_sided_hi = float(np.percentile(s_boot, 95.0))
    diffs = field_by_arm[EXTREME_LO] - field_by_arm[EXTREME_HI]
    sd_realized = float(np.std(diffs, ddof=1))
    mde_realized = mde_paired(sd_realized, n_worlds)
    pred_att = np.array([float(pred_by_arm[a]["r_card_b_pred_raw"]) for a in PRIMARY_ARMS])
    meas_rec = np.array([float(np.mean(field_by_arm[a])) for a in PRIMARY_ARMS])
    rho_s, p_perm, n_perm = spearman_exact_p(pred_att, meas_rec)
    ratio = s_point / p_identity
    ratio_lo, ratio_hi = s_lo / p_identity, s_hi / p_identity

    l_b = {
        "prior": 0.25,
        "spearman_pred_attenuation_vs_measured_recovery": rho_s,
        "exact_permutation_p_one_sided": p_perm,
        "n_permutations": n_perm,
        "S": s_point, "P_identity": p_identity,
        "S_over_P": ratio, "S_over_P_ci": [ratio_lo, ratio_hi],
        "S_ci": [s_lo, s_hi],
        "clause_spearman": bool(rho_s == 1.0 and p_perm <= 0.005),
        "clause_ratio": bool(0.5 <= ratio <= 2.0 and 0.33 <= ratio_lo and ratio_hi <= 3.0),
    }
    l_b["verdict"] = "HOLD" if (l_b["clause_spearman"] and l_b["clause_ratio"]) else "MISS"

    l_c = {
        "prior": 0.65,
        "S": s_point, "P_over_3": p_identity / 3.0, "P_over_2": p_identity / 2.0,
        "S_ci_upper_two_sided": s_hi, "S_ci_upper_one_sided95": s_one_sided_hi,
        "clause_point": bool(s_point < p_identity / 3.0),
        "clause_ci": bool(s_hi < p_identity / 2.0),
        "requires_L_A": l_a["verdict"] == "HOLD",
    }
    l_c["verdict"] = (
        "HOLD" if (l_c["clause_point"] and l_c["clause_ci"] and l_c["requires_L_A"]) else "MISS"
    )

    partial = {
        "clause_ratio_band": bool(1.0 / 3.0 <= ratio <= 0.5),
        "clause_partial_ordering": bool(0.0 < rho_s < 1.0 and p_perm < 0.05),
    }
    partial["fires"] = bool(
        (partial["clause_ratio_band"] or partial["clause_partial_ordering"])
        and l_b["verdict"] == "MISS" and l_c["verdict"] == "MISS"
    )

    # ---- L-D: the gauge reads the mixture better than the trait
    l_d_rows = []
    for arm_id in PRIMARY_ARMS:
        d = mixed_by_arm[arm_id] - field_by_arm[arm_id]
        db = boot_mix[arm_id] - boot_rec[arm_id]
        lo, hi = k2a().ci_of(db)
        l_d_rows.append({
            "arm": arm_id, "mixed_mean": float(np.mean(mixed_by_arm[arm_id])),
            "b_only_mean": float(np.mean(field_by_arm[arm_id])),
            "difference": float(np.mean(d)), "ci_lo": lo, "ci_hi": hi,
            "ci_excludes_zero": bool(lo > 0.0 or hi < 0.0),
            "one_sided_lower95": float(np.percentile(db, 5.0)),
            "positive": bool(np.mean(d) > 0.0),
            "per_world_positive": int(np.sum(d > 0.0)),
        })
    l_d = {
        "prior": 0.60,
        "per_arm": l_d_rows,
        "arms_positive": int(sum(r["positive"] for r in l_d_rows)),
        "arms_ci_excludes_zero": int(sum(r["ci_excludes_zero"] for r in l_d_rows)),
    }
    l_d["verdict"] = "HOLD" if (l_d["arms_positive"] == 6 and l_d["arms_ci_excludes_zero"] >= 5) else "MISS"

    # ---- rule 13 on the field-channel clauses
    def stability_check(name: str, boots_lo: np.ndarray, arr_hi: np.ndarray,
                        boundary: float, kind: str, verdict: bool) -> None:
        alpha = 0.025 if kind == "contains" else 0.025
        mc = k2a().mc_sd_of_endpoint(boots_lo, B_BOOT, alpha)
        if kind == "upper_lt":
            dist = abs(boundary - float(np.percentile(boots_lo, 97.5)))
            v2 = bool(float(np.percentile(arr_hi, 97.5)) < boundary)
            end = [float(np.percentile(arr_hi, 97.5))]
        elif kind == "excludes_zero":
            lo2, hi2 = k2a().ci_of(arr_hi)
            dist = min(abs(float(np.percentile(boots_lo, 2.5))),
                       abs(float(np.percentile(boots_lo, 97.5))))
            v2 = bool(lo2 > 0.0 or hi2 < 0.0)
            end = [lo2, hi2]
        else:
            lo2, hi2 = k2a().ci_of(arr_hi)
            dist = min(abs(boundary - float(np.percentile(boots_lo, 2.5))),
                       abs(boundary - float(np.percentile(boots_lo, 97.5))))
            v2 = bool(lo2 <= boundary <= hi2)
            end = [lo2, hi2]
        if dist <= 2.0 * mc:
            stability.append({
                "arm": "pooled", "clause": name, "direction": kind, "boundary": boundary,
                "mc_sd_endpoint_B2000": mc, "distance_to_boundary": dist,
                "verdict_B2000": verdict, "verdict_B20000": v2, "endpoints_B20000": end,
                "status": "STABLE" if verdict == v2 else "BOUNDARY",
            })

    s_boot_hi = (field_by_arm[EXTREME_LO][pick_hi].mean(axis=1)
                 - field_by_arm[EXTREME_HI][pick_hi].mean(axis=1))
    stability_check("L-C: S CI upper < P/2", s_boot, s_boot_hi, p_identity / 2.0,
                    "upper_lt", l_c["clause_ci"])
    stability_check("L-B: S/P CI inside [0.33,3] (upper)", s_boot, s_boot_hi,
                    3.0 * p_identity, "upper_lt", bool(ratio_hi <= 3.0))
    for arm_id, r in zip(PRIMARY_ARMS, l_d_rows):
        db = boot_mix[arm_id] - boot_rec[arm_id]
        db_hi = (mixed_by_arm[arm_id][pick_hi].mean(axis=1)
                 - field_by_arm[arm_id][pick_hi].mean(axis=1))
        stability_check(f"L-D[{arm_id}]: CI excludes 0", db, db_hi, 0.0,
                        "excludes_zero", r["ci_excludes_zero"])

    if stability:
        pd.DataFrame(stability).to_csv(OUT / "rule13_stability.csv", index=False)
    boundary = [s for s in stability if s["status"] == "BOUNDARY"]

    # ---- second readings (rule 9: all readings reported)
    second = {
        "squared_link": {
            "P_squared": p_squared,
            "S_over_P_squared": s_point / p_squared,
            "L-B_clause_ratio": bool(0.5 <= s_point / p_squared <= 2.0
                                     and 0.33 <= s_lo / p_squared
                                     and s_hi / p_squared <= 3.0),
            "L-C_clause_point": bool(s_point < p_squared / 3.0),
            "L-C_clause_ci": bool(s_hi < p_squared / 2.0),
        },
        "efficiency_normalized_descriptive": {
            "note": "DESCRIPTIVE, fits no registered branch: the gauge's measured "
                    "recovery level is far below the card attenuation level, so a "
                    "purely multiplicative reader efficiency would compress a "
                    "faithfully-tracked swing. lambda := mean measured recovery / "
                    "mean predicted attenuation; S/(lambda*P) tests tracking AFTER "
                    "removing an arm-independent efficiency.",
            "lambda": float(np.mean(meas_rec) / np.mean(pred_att)),
            "S_over_lambda_P": float(s_point / (np.mean(meas_rec) / np.mean(pred_att) * p_identity)),
        },
        "paired_t_interval_S": {
            "mean": s_point, "sd_paired": sd_realized,
            "t_ci": [s_point - T_QUANTILES[n_worlds][0] * sd_realized / math.sqrt(n_worlds),
                     s_point + T_QUANTILES[n_worlds][0] * sd_realized / math.sqrt(n_worlds)],
            "mde_realized": mde_realized,
            "P_over_MDE_realized": p_identity / mde_realized,
            "meets_3x_realized": bool(p_identity >= 3.0 * mde_realized),
        },
        "companion_cell_C1": {
            k: (float(v) if isinstance(v, (int, float, np.floating)) else v)
            for k, v in cells[cells["arm"] == "C1"].iloc[0].to_dict().items()
            if k in ("gap", "gap_pred", "gap_lo", "gap_hi", "gap_contains_pred",
                     "r_card_b_raw", "r_card_b_raw_pred", "r_card_b_raw_lo",
                     "r_card_b_raw_hi", "r_card_b_raw_contains_pred",
                     "recovery_b_only_mean", "recovery_mixed_mean")
        },
        "per_arm_field_recovery": {
            a: {"b_only_mean": float(np.mean(field_by_arm[a])),
                "b_only_ci": list(k2a().ci_of(boot_rec[a])),
                "mixed_mean": float(np.mean(mixed_by_arm[a])),
                "mixed_ci": list(k2a().ci_of(boot_mix[a]))}
            for a in PRIMARY_ARMS
        },
        "field_recovery_measured_ordering_desc": [
            PRIMARY_ARMS[i] for i in np.argsort(-meas_rec)
        ],
        "field_recovery_predicted_ordering_desc": [
            PRIMARY_ARMS[i] for i in np.argsort(-pred_att)
        ],
    }

    pivots = {
        "P1b": {"fires": l_a["verdict"] == "MISS",
                "consequence": "INSTRUMENT-FAIL: STOP, no theory reading; K2a' next"},
        "P2b": {"fires": bool(l_c["verdict"] == "HOLD" and l_a["verdict"] == "HOLD"),
                "consequence": "T4-reader-mediated becomes the registered form in IDT "
                               "(planner executes the re-typing)"},
        "P3b": {"fires": l_b["verdict"] == "HOLD",
                "consequence": "T4-simple lives; K2c is the quantitative gap law"},
        "P4b": {"fires": partial["fires"],
                "consequence": "K2c is the decomposition design; no re-typing of T4"},
    }

    if l_a["verdict"] == "MISS":
        slug = "INSTRUMENT_FAIL__POSITIVE_CONTROL_MISS"
    elif l_b["verdict"] == "HOLD":
        slug = "T4_SIMPLE_HOLDS__FIELD_TRACKS_CARD_ALGEBRA"
    elif l_c["verdict"] == "HOLD":
        slug = "T4_READER_MEDIATED__CARD_LEVER_LIVE_GAUGE_FLOORED"
    elif partial["fires"]:
        slug = "PARTIAL__BOTH_MECHANISMS_LIVE"
    else:
        slug = "NO_REGISTERED_BRANCH__REPORTED_AS_SUCH"
    if l_a["verdict"] == "HOLD":
        slug += "__POSITIVE_CONTROL_" + (
            "EXACT" if (l_a["gap_cells_containing_prediction"] == 6
                        and l_a["attenuation_cells_containing_prediction"] == 6) else "PASS"
        )
    slug += "__LD_" + ("HOLD" if l_d["verdict"] == "HOLD" else "MISS")

    decision = {
        "leg": "M4-K2b",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "banner": BANNER,
        "master_seed": MASTER_SEED,
        "worlds_per_arm": n_worlds,
        "n_authors_per_world": int(len(layout()["author_ids"])),
        "n_retained": int(len(layout()["retained_idx"])),
        "leans": {"L-A": l_a, "L-B": l_b, "L-C": l_c, "PARTIAL": partial, "L-D": l_d},
        "pivots": pivots,
        "rule13": {"triggered": len(stability), "boundary": len(boundary),
                   "records": stability},
        "second_readings": second,
        "verdict_slug": slug,
    }
    (OUT / "decision.json").write_text(
        json.dumps(decision, indent=2, default=str) + "\n", encoding="utf-8"
    )
    write_manifest({"finalize": time.time() - t0})
    print(json.dumps({k: v for k, v in decision.items() if k != "rule13"},
                     indent=2, default=str))
    print(f"rule13 triggered={len(stability)} boundary={len(boundary)}")


def run_diagnostic(args: argparse.Namespace) -> None:
    """POST-HOC DIAGNOSTIC, run AFTER the registered adjudication and flagged as
    such (K2a's precedent).  It writes its own artifact and NEVER touches
    decision.json or gates.json.

    Question raised by the outcome: the measured pooled card GAP sits a nearly
    constant +0.002 above its Part-0 prediction in all six arms (contained 6/6,
    but at ~0.85 of the CI half-width every time).  Is that an estimator bias, an
    algebra error, or one shared noise realization propagated into every arm by
    RN-4's common world seeds?
    """
    gates = require_part0()
    t0 = time.time()
    n_worlds = int(gates["G1b"]["worlds_selected"])
    out: dict[str, Any] = {
        "note": "POST-HOC diagnostic; NOT a lean input; decision.json untouched",
        "n_worlds": n_worlds,
    }
    w_a1 = arm_weights(0.02, "zero")
    controls = {
        # B = 0: the algebra's predicted gap is EXACTLY 0 (both splits share the
        # same numerator A and the same denominators once the AR term vanishes).
        "state_off": {**w_a1, "slow": 0.0},
        # B = 0 and A = 0: a pure centred-noise card; predicted gap EXACTLY 0.
        "noise_only": {**w_a1, "slow": 0.0, "mu": 0.0},
        # B = 0 and E = 0: a pure trait card; predicted rho = 1 on both splits.
        "trait_only": {**w_a1, "slow": 0.0, "noise": 0.0},
    }
    drop = ("author", "world_seed", "cell_key", "m")
    for name, w in controls.items():
        frames = []
        for world_index in range(n_worlds):
            world = build_k2b_world(world_seed_for(world_index), 0.90)
            frame, _ = card_channel_frame(world, w, world_seed_for(world_index))
            frames.append(frame)
        frame = pd.concat(frames, ignore_index=True)
        point, _ = bootstrap_card(frame, 1, MASTER_SEED)
        keep = [c for c in frame.columns if c not in drop]
        cols = {c: i for i, c in enumerate(keep)}
        per_m = {}
        for m in sorted(frame["m"].unique()):
            sub = frame[frame["m"] == m]
            p = pooled_card_stats(sub[keep].to_numpy(float).sum(axis=0), cols, float(len(sub)))
            per_m[int(m)] = {"n_rows": int(len(sub)), "gap": float(p["gap"]),
                             "rho_interleaved": float(p["rho_interleaved"]),
                             "rho_contiguous": float(p["rho_contiguous"])}
        out[name] = {
            "weights": w, "predicted_gap": 0.0,
            "gap": float(point["gap"]),
            "rho_interleaved": float(point["rho_interleaved"]),
            "rho_contiguous": float(point["rho_contiguous"]),
            "per_m": per_m,
        }
    # --- is the pooled GAP estimator itself biased on centred iid noise?
    rng = np.random.default_rng(MASTER_SEED)
    mc = {}
    sizes = retained_cell_sizes()
    for m in (8, 12, 16):
        n_cell_total = sum(v for k, v in sizes.items() if k.endswith(f"m{m}"))
        h = m // 2
        gaps = []
        for _ in range(400):
            x = rng.normal(size=(n_cell_total, m, DIM))
            x = x - x.mean(axis=0, keepdims=True)

            def rho(s1, s2):
                c1, c2 = x[:, s1].mean(1), x[:, s2].mean(1)
                dot = float(np.einsum("id,id->i", c1, c2).sum())
                n1 = float(np.einsum("id,id->i", c1, c1).sum())
                n2 = float(np.einsum("id,id->i", c2, c2).sum())
                return dot / math.sqrt(n1 * n2)

            gaps.append(rho(np.arange(0, m, 2), np.arange(1, m, 2))
                        - rho(np.arange(0, h), np.arange(h, m)))
        g = np.asarray(gaps)
        mc[m] = {"n_authors": n_cell_total, "reps": len(g), "mean": float(g.mean()),
                 "sd": float(g.std(ddof=1)), "se_mean": float(g.std(ddof=1) / math.sqrt(len(g))),
                 "analytic_sd_1_over_sqrt_ND": 1.0 / math.sqrt(n_cell_total * DIM)}
    out["pooled_gap_estimator_unbiasedness_mc"] = mc
    # --- descriptive readings for the report (from persisted artifacts only)
    decision = json.loads((OUT / "decision.json").read_text(encoding="utf-8"))
    rec = {}
    for arm_id in PRIMARY_ARMS:
        rec[arm_id] = read_csv_rt(OUT / f"arm_{arm_id}_field.csv").sort_values("world")[
            "recovery_b_only"
        ].to_numpy(float)
    pick = np.random.default_rng(MASTER_SEED).integers(0, n_worlds, size=(B_BOOT, n_worlds))
    d53 = rec["A5"] - rec["A3"]
    b53 = rec["A5"][pick].mean(axis=1) - rec["A3"][pick].mean(axis=1)
    out["ordering_violation_A5_vs_A3"] = {
        "predicted_attenuation_A3": 0.6758917867864564,
        "predicted_attenuation_A5": 0.645057248597175,
        "predicted_difference_A5_minus_A3": 0.645057248597175 - 0.6758917867864564,
        "measured_recovery_A3": float(rec["A3"].mean()),
        "measured_recovery_A5": float(rec["A5"].mean()),
        "measured_difference_A5_minus_A3": float(d53.mean()),
        "ci": list(k2a().ci_of(b53)),
        "per_world_sign_positive": int(np.sum(d53 > 0)),
        "ci_excludes_zero": bool(min(k2a().ci_of(b53)) > 0 or max(k2a().ci_of(b53)) < 0),
    }
    pred = read_csv_rt(OUT / "part0_predictions.csv").set_index("arm")
    out["relative_swing"] = {
        "measured_recovery_A1": float(rec["A1"].mean()),
        "measured_recovery_A4": float(rec["A4"].mean()),
        "measured_relative_drop": float(1.0 - rec["A4"].mean() / rec["A1"].mean()),
        "predicted_attenuation_A1": float(pred.loc["A1", "r_card_b_pred_raw"]),
        "predicted_attenuation_A4": float(pred.loc["A4", "r_card_b_pred_raw"]),
        "predicted_relative_drop": float(
            1.0 - pred.loc["A4", "r_card_b_pred_raw"] / pred.loc["A1", "r_card_b_pred_raw"]
        ),
        "note": "DESCRIPTIVE: the absolute swing is 0.38x the prediction while the "
                "RELATIVE drop is larger than predicted -- the gauge is more than "
                "proportionally hurt by the state channel. Fits no registered branch.",
    }
    out["verdict_slug_unchanged"] = decision["verdict_slug"]
    (OUT / "post_hoc_diagnostic.json").write_text(
        json.dumps(out, indent=2, default=str) + "\n", encoding="utf-8"
    )
    write_manifest({"diagnostic_post_hoc": time.time() - t0})
    print(json.dumps(out, indent=2, default=str))


def write_manifest(stage_times: dict[str, float]) -> None:
    path = OUT / "manifest.json"
    prior = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    prior.setdefault("leg", "M4-K2b")
    prior.setdefault("banner", BANNER)
    prior.setdefault("script", "scripts/run_suica_m4_k2b_t4_branch.py")
    prior.setdefault("master_seed", MASTER_SEED)
    prior.setdefault("worlds_per_cell", WORLDS_PER_CELL)
    prior.setdefault("pilot_worlds", list(PILOT_WORLDS))
    prior.setdefault("arms", [list(a) for a in ARMS])
    prior.setdefault("noise_share", NOISE_SHARE)
    prior.setdefault("signal_share", SIGNAL_SHARE)
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
    parser.add_argument("--arms", default=None, help="comma-separated arm ids (chunking)")
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
