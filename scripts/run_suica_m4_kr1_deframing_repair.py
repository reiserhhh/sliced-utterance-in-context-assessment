#!/usr/bin/env python3
"""M4-K-R1 -- the constructive repair test: does de-framing make the reader a
better TRAIT instrument?

Registered spec: docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md section "M4-K-R1 -- The
constructive repair test: does de-framing make the reader a better TRAIT
instrument?" (REGISTERED 2026-08-09, BEFORE RUN, commit fa19b1e), together with
standing rules 1-17 and the execution conventions at the head of that document.
Theory: docs/SUICA_IDENTITY_THEORY_V1.md appendix L (T4's closed form
field ~ lambda*r^q - kappa*V_person - eps_species) and appendix D.2/D.4 (T9's
counter-operations; the certified-unadopted de-framing repair).

Executor standing: implementation and execution only.  Everything labelled
"RN-n" is a register-note -- an operationalization of something the
registration left open (standing rule 9) -- fixed and written to
reports/SUICA_M4_KR1_DEFRAMING_REPAIR_REPORT.md Part 0 BEFORE any main arm ran,
with ALL readings reported.

Reuse boundary (registration: "REUSE the six state arms A1..A6, panels, gauge
invocation, b-only truth construction, card channel" from K2b; "the A4
estimated-subtraction construction" from K1b).  Rule 12 -- source objects:
  * scripts/run_suica_m4_k2b_t4_branch.py (k2b()) -- ARMS (k2b:97-105),
    arm_weights (k2b:194-206), layout (k2b:236-291), build_k2b_world
    (k2b:305-346), emit_panel (k2b:352-375), card_channel_frame (k2b:381-457),
    pooled_card_stats (k2b:463-489), bootstrap_card (k2b:503-508),
    arm_predictions (k2b:552-624), field_from_vectors (k2b:634-647),
    read_csv_rt (k2b:176-178), and the generator constants K_LATENT/DIM/
    G_PROFILE/A_SCALE/SIGMA_ISO (k2b:146-151).  run_field_world (k2b:650-762)
    is NOT called: this leg needs the gauge-variant hook, so its body is
    mirrored in `run_field_world_variant` below with the input-path hook and
    nothing else changed.
  * scripts/run_suica_m4_k1b_composition_ownership.py (k1b()) -- the A4
    ESTIMATED de-framing construction: `_gen_estimated` (k1b:263-276) and
    `estimated_occasion_norm` (k1b:278-307), whose channel arithmetic
    (mu_hat(c,o) := mean over A4_AUTHORS_PER_CONTEXT=32 disjoint donor authors
    of their own mean_part + noise_part, PLUS the PANEL's common vector at
    (c,o); k1b:296-306) is transcribed to the expressive world in
    `mu_hat_field` below, and whose norm-pool seeding
    (stable_bucket(f"{world_seed}-normpool", ...); k1b:290-292) is transcribed
    in `norm_pool_seed`.  k1b._arm_world / k1b.arm_task (k1b:369-388, 347-367)
    are called UNMODIFIED for G4r's F2-composition reproduction.
  * scripts/run_suica_m4_k2d_frontier_carrier.py (k2d()) -- pooled_q
    (k2d:644-670), called unmodified for the q refits.
  * scripts/run_suica_m4_k2e_double_matching.py (k2e()) -- rederive_anchors
    (k2e:596-745), called unmodified for the G0r bit-exact anchors.
  * scripts/run_suica_m4_k2a_expressive_world.py via k2b -- ci_of, bootstrap_cell,
    mc_sd_of_endpoint.
  * suica_core/ is READ-ONLY and untouched.
  * NEW in this leg: world_seed_for, norm_pool_seed, build_pool_world,
    mu_hat_field, deframe_panel, run_field_world_variant, the 12-cell driver,
    and the finalize adjudication.

Stages (foreground, chunked, resumable; artifacts under
results/m4_kr1_deframing_repair/):
  --stage part0    G0r..G5r on RESERVED pilot worlds 9601-9604 plus the rule-16
                   enumeration and all three rule-9 second readings.  Refuses
                   to let `arms` run unless every gate passes AND the Part-0
                   report exists on disk.
  --stage arms     12 cells x N worlds, chunked with --worlds LO:HI.
  --stage finalize per-arm d_a with CIs, (n_up, n_down), the lean, the
                   parameter story, rule-13 stability, routing, decision.json.
"""
from __future__ import annotations

import argparse
import hashlib
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
from scipy import stats as _st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import suica_core.v8_realtext_relation_field as v8  # noqa: E402
from suica_core.v8_context_relation_field import _orthonormal_loadings  # noqa: E402

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"

# --- registration-fixed constants -------------------------------------------
MASTER_SEED = 20260821             # registration: "master_seed 20260821"
WORLDS_DEFAULT = 32                # registration: "32 worlds/arm"
ESCALATION_LADDER = (32, 64)       # registration G1r: "escalate 32->64 once"
PILOT_WORLDS = (9601, 9602, 9603, 9604)   # RESERVED; 4-world pilot (standing)
B_BOOT = 2000                      # registration: "B=2000, seed=master"
B_BOOT_HIGH = 20000                # registration G3r: ">=10xB" (rule 13)
M_REC = 0.010                      # registration: m_rec, per-arm recovery margin
MDE_TARGET = 0.010                 # registration G1r: "MDE <= 0.010 for d_a"
NORM_POOL_AUTHORS_PER_CONTEXT = 32  # k1b:87 A4_AUTHORS_PER_CONTEXT

VARIANTS = ("intact", "deframed")
PRIORS = {"L-R1": 0.45, "L-R2": 0.30, "L-R3": 0.10, "L-R4": 0.15}

OUT = ROOT / "results" / "m4_kr1_deframing_repair"
REPORT = ROOT / "reports" / "SUICA_M4_KR1_DEFRAMING_REPAIR_REPORT.md"
K2B_OUT = ROOT / "results" / "m4_k2b_t4_branch"
K1B_OUT = ROOT / "results" / "m4_k1b_composition_ownership"
K1C_OUT = ROOT / "results" / "m4_k1c_prime_author_share"
K2E_OUT = ROOT / "results" / "m4_k2e_double_matching"

# persisted anchors named by G0r (values quoted from the registration text)
ANCHOR_KAPPA = -0.7220359963712748       # K2e decision.json kappa_hat_registered
ANCHOR_RATIO_K1C = 0.7347498869811525    # K1c' decision.json R_est/R_or
ANCHOR_LAMBDA_K2B = 0.17417497661611914  # K2b decision.json lambda

_MODULES: dict[str, Any] = {}


def _load_script(name: str) -> Any:
    import importlib.util

    if name in _MODULES:
        return _MODULES[name]
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _MODULES[name] = module
    return module


def k2b() -> Any:
    return _load_script("run_suica_m4_k2b_t4_branch.py")


def k2e() -> Any:
    return _load_script("run_suica_m4_k2e_double_matching.py")


def k2d() -> Any:
    return k2e().k2d()


def k1b() -> Any:
    return _load_script("run_suica_m4_k1b_composition_ownership.py")


# --- the six state arms, taken from K2b's own table (rule 12) ----------------
def arms() -> tuple[tuple[str, float, float, str], ...]:
    return tuple((a, s, p, wi) for a, s, p, wi, primary in k2b().ARMS if primary)


def arm_ids() -> tuple[str, ...]:
    return tuple(a[0] for a in arms())


def read_csv_rt(path: Path) -> pd.DataFrame:
    """G5r: every artifact re-read with float_precision='round_trip'."""
    return pd.read_csv(path, float_precision="round_trip")


def t_quantiles(n: int) -> tuple[float, float]:
    """scipy, not a hard-coded table (K2b's t_{.80,31} constant was +1.0e-04
    off -- planner note A-1 under standing rule 15; K2c set the precedent of
    verifying against scipy)."""
    return float(_st.t.ppf(0.975, n - 1)), float(_st.t.ppf(0.80, n - 1))


def mde_paired(sd_diff: float, n: int) -> float:
    t_alpha, t_beta = t_quantiles(n)
    return (t_alpha + t_beta) * sd_diff / math.sqrt(n)


def world_seed_for(world: int) -> int:
    """K2b's RN-8 convention (k2b:222-228) at this leg's master seed and salt:
    the seed depends on the WORLD INDEX ONLY, so every arm AND every gauge
    variant shares the trait, the slow innovations, the frame shocks and the
    noise bit-for-bit -- the intact-vs-deframed contrast is exactly paired."""
    return int(
        v8.stable_bucket(f"{MASTER_SEED}-{world}", salt="m4kr1-world", modulus=2**31 - 1)
    )


def norm_pool_seed(world_seed: int) -> int:
    """k1b:290-292's norm-pool seeding, salt renamed to this leg."""
    return int(
        v8.stable_bucket(f"{world_seed}-normpool", salt="m4kr1-normpool", modulus=2**63 - 1)
    )


def corpus_tag(arm_id: str, world_index: int) -> str:
    """RN-4: the corpus tag is VARIANT-INVARIANT.  `f1.featurize_panel`
    (f1:166-229) seeds its transition-null permutation streams per
    (corpus, author, offset); a variant-dependent tag would change the null
    draws and destroy the pairing.  The tag therefore names the arm and the
    world only, exactly as K2b's did (k2b:673)."""
    return f"m4kr1-{arm_id}-w{world_index}"


# ---------------------------------------------------------------------------
# The de-framing construction: K1b's A4, transcribed to the expressive world.

def build_pool_world(pool_seed: int, phi_slow: float, n_pool: int,
                     t_max: int) -> dict[str, np.ndarray]:
    """The donor pool's own world, stream-for-stream identical to
    k2b.build_k2b_world (k2b:305-346) but at n_pool authors, all observed on
    all t_max occasions.  The donors' OWN frame channel is never built: k1b's
    construction substitutes the PANEL's common vector (k1b:303-306)."""
    m = k2b()
    k = m.K_LATENT
    rng = np.random.default_rng(pool_seed)
    loadings = _orthonormal_loadings(rng, m.DIM, k)          # k2b:311 / f2:167
    z = rng.normal(size=(n_pool, k))                          # k2b:312 / f2:168
    _zeta = rng.normal(size=(n_pool, k))                      # k2b:313 (stream order)
    xs = np.empty((n_pool, t_max, k), dtype=float)
    xs[:, 0] = rng.normal(size=(n_pool, k))                   # k2b:315
    innovation_scale = math.sqrt(1.0 - phi_slow**2)
    for t in range(1, t_max):                                 # k2b:317-318
        xs[:, t] = phi_slow * xs[:, t - 1] + innovation_scale * rng.normal(size=(n_pool, k))
    noise = rng.normal(size=(n_pool, t_max, m.DIM))           # k2b:319
    trait = m.A_SCALE * ((z * m.G_PROFILE) @ loadings.T)      # k2b:320
    slow = m.A_SCALE * ((xs * m.G_PROFILE) @ loadings.T)      # k2b:321
    return {"trait": trait, "slow": slow, "noise": m.SIGMA_ISO * noise}


def mu_hat_field(world: dict[str, np.ndarray], w: dict[str, float], world_seed: int,
                 phi_slow: float, *, donor_channels: str = "k1b_literal",
                 pool_scheme: str = "per_context") -> np.ndarray:
    """mu_hat(c, o) -- the ESTIMATED per-(context, occasion) norm, shape
    (n_ctx, t_max, DIM).

    RN-3 (standing rule 9, PRIMARY = `k1b_literal`): k1b:296-306 builds the
    donor average out of the pool's `mean_part + noise_part` -- its ENTIRE
    occasion channel is dropped and the panel's common vector put in its place.
    In K1b's world family the occasion channel at kappa=1.0 IS the common
    channel, so the literal channel list is {author, noise}; the expressive
    world's `slow` and `int` are occasion-channel members with no K1b
    counterpart.  PRIMARY transcribes the channel list literally
    (donor = w_mu*trait + w_e*noise); the SECOND READING `expressive` lets the
    donors carry their own state (donor += w_slow*slow + w_int*int), which is
    what 32 real co-occasion authors would emit.  w_int = 0 in all six arms, so
    the two readings differ by the donor slow-state term alone.

    RN-5 (standing rule 9, PRIMARY = `per_context`): k1b holds ONE 32-donor
    block per context and reads it at every occasion (k1b:299-306), so the
    donor trait error is a per-context constant.  The SECOND READING
    `per_occasion` draws a fresh disjoint 32-donor block for every
    (context, occasion).
    """
    m = k2b()
    lay = m.layout()
    n_ctx = len(lay["contexts_sorted"])
    t_max = lay["t_max"]
    if pool_scheme == "per_context":
        n_pool = NORM_POOL_AUTHORS_PER_CONTEXT * n_ctx
    elif pool_scheme == "per_occasion":
        n_pool = NORM_POOL_AUTHORS_PER_CONTEXT * n_ctx * t_max
    else:
        raise ValueError(f"unknown pool_scheme {pool_scheme!r}")
    pool = build_pool_world(norm_pool_seed(world_seed), phi_slow, n_pool, t_max)
    donor = w["mu"] * pool["trait"][:, None, :] + w["noise"] * pool["noise"]
    if donor_channels == "expressive":
        donor = donor + w["slow"] * pool["slow"]
    elif donor_channels != "k1b_literal":
        raise ValueError(f"unknown donor_channels {donor_channels!r}")
    out = np.empty((n_ctx, t_max, m.DIM), dtype=float)
    b = NORM_POOL_AUTHORS_PER_CONTEXT
    for ci in range(n_ctx):
        if pool_scheme == "per_context":
            block = donor[ci * b:(ci + 1) * b]                 # (32, t_max, DIM)
            out[ci] = block.mean(axis=0)
        else:
            for occ in range(t_max):
                lo = (ci * t_max + occ) * b
                out[ci, occ] = donor[lo:lo + b, occ, :].mean(axis=0)
    # k1b:303-306: the PANEL's own common vector, not the donors'.
    out = out + w["common"] * world["common"]
    return out


def deframe_panel(vectors: list[np.ndarray], mu: np.ndarray) -> list[np.ndarray]:
    """k1b:270-275's subtraction: pre-map, per (context, occasion)."""
    lay = k2b().layout()
    ctx_index = lay["ctx_index"]
    return [v - mu[ctx_index[i], : len(v)] for i, v in enumerate(vectors)]


def panel_rms(a: list[np.ndarray], b: list[np.ndarray]) -> float:
    return math.sqrt(
        float(np.mean(np.concatenate([(a[i] - b[i]).ravel() for i in range(len(a))]) ** 2))
    )


# ---------------------------------------------------------------------------
# The FIELD channel with the gauge-variant hook.

def run_field_world_variant(
    arm_id: str, world_index: int, world: dict[str, np.ndarray], w: dict[str, float],
    phi_slow: float, variant: str, *,
    donor_channels: str = "k1b_literal", pool_scheme: str = "per_context",
    deframe_truth: bool = False, verify: bool = False,
) -> dict[str, Any]:
    """k2b.run_field_world (k2b:650-762) with ONE addition: the de-framing hook
    on the gauge's OBSERVED input path.

    RN-2 (standing rule 9, PRIMARY = truth panels INTACT): the estimand is the
    trait field, fixed across gauge variants.  K2b's own G4b measured what
    de-framing a truth panel would do -- the STRICT trait-only panel's field has
    max context norm 0.0006675856745354268 against the b-only panel's minimum
    0.15214367930549447, and its recovery is -0.024495680267977205 (noise).
    De-framing the b-only truth panel leaves w_mu*trait minus a donor residual,
    i.e. that degenerate object, so the both-panels reading measures a
    truth-object collapse, not a reader property.  PRIMARY therefore de-frames
    the OBSERVED panel only; the SECOND READING `deframe_truth=True` de-frames
    the truth panels too and is reported from the pilot.

    RN-2b (disclosed, not a choice): `calibrate_d0_soft` is fitted on whatever
    the operator observes (k2b:679), so under G-deframed the truth panels are
    mapped through the de-framed calibration.  The truth field is therefore not
    bit-identical across variants; the induced difference is measured on the
    pilot and reported.
    """
    m = k2b()
    lay = m.layout()
    module = lay["module"]
    corpus = corpus_tag(arm_id, world_index)
    started = time.time()
    vectors_intact = m.emit_panel(world, w)
    mu = None
    if variant == "deframed":
        mu = mu_hat_field(world, w, world_seed_for(world_index), phi_slow,
                          donor_channels=donor_channels, pool_scheme=pool_scheme)
        vectors = deframe_panel(vectors_intact, mu)
    elif variant == "intact":
        vectors = vectors_intact
    else:
        raise ValueError(f"unknown gauge variant {variant!r}")
    raw_m, raw_k = m.f1().featurize_panel(
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
    full_b = m.emit_panel(world, w, active=("mu", "common"))
    full_mixed = m.emit_panel(world, w, active=("mu", "slow", "int", "common"))
    if deframe_truth and mu is not None:
        full_b = deframe_panel(full_b, mu)
        full_mixed = deframe_panel(full_mixed, mu)
    truth_b = [full_b[i] for i in ridx]
    truth_mixed = [full_mixed[i] for i in ridx]
    field_b = m.field_from_vectors(truth_b, calibration, corpus)
    field_mixed = m.field_from_vectors(truth_mixed, calibration, corpus)
    row: dict[str, Any] = {
        "arm": arm_id,
        "variant": variant,
        "world": world_index,
        "corpus": corpus,
        "donor_channels": donor_channels,
        "pool_scheme": pool_scheme,
        "deframe_truth": bool(deframe_truth),
        "n_retained": int(len(ridx)),
        "d0_eff_rank_M": float(calibration["M"].effective_rank),
        "d0_eff_rank_K": float(calibration["K"].effective_rank),
        "recovery_b_only": float(module.field_agreement(field_est, field_b, lay["weights"])),
        "recovery_mixed": float(module.field_agreement(field_est, field_mixed, lay["weights"])),
        "deframe_panel_rms": 0.0 if variant == "intact" else panel_rms(vectors_intact, vectors),
        "panel_rms_intact": math.sqrt(
            float(np.mean(np.concatenate([v.ravel() for v in vectors_intact]) ** 2))
        ) if verify else float("nan"),
        "truth_b_field_norm_min": float(
            min(float(np.linalg.norm(field_b[c])) for c in field_b)
        ),
        "seconds": float(time.time() - started),
    }
    row["recovery_gap_mixed_minus_b"] = row["recovery_mixed"] - row["recovery_b_only"]
    row["_field_b"] = field_b
    return row


# ---------------------------------------------------------------------------
# The CARD channel (positive control; G2r's designed invariance).

CARD_DROP = ("author", "world_seed", "cell_key", "m")


def card_for_world(world: dict[str, np.ndarray], w: dict[str, float],
                   world_seed: int) -> tuple[dict[str, float], str, int, dict[str, float]]:
    """k2b.card_channel_frame (k2b:381-457) called unchanged, reduced to the
    per-world column sums pooled_card_stats consumes, plus a byte digest of the
    numeric block for the G2r bit-identity check."""
    m = k2b()
    frame, _cres = m.card_channel_frame(world, w, world_seed)
    keep = [c for c in frame.columns if c not in CARD_DROP]
    data = np.ascontiguousarray(frame[keep].to_numpy(float))
    digest = hashlib.sha256(data.tobytes()).hexdigest()
    cols = {c: i for i, c in enumerate(keep)}
    sums = data.sum(axis=0)
    stats = m.pooled_card_stats(sums, cols, float(len(frame)))
    return ({k: float(v) for k, v in stats.items()}, digest, int(len(frame)),
            {f"csum_{c}": float(sums[i]) for c, i in cols.items()})


def pool_card_sums(rows: pd.DataFrame) -> dict[str, float]:
    m = k2b()
    scols = [c for c in rows.columns if c.startswith("csum_")]
    keep = [c[len("csum_"):] for c in scols]
    cols = {c: i for i, c in enumerate(keep)}
    sums = rows[scols].to_numpy(float).sum(axis=0)
    n_rows = float(rows["card_n_rows"].to_numpy(float).sum())
    return {k: float(v) for k, v in m.pooled_card_stats(sums, cols, n_rows).items()}


# ---------------------------------------------------------------------------
# Adjudication helpers.

def ci_of(arr: np.ndarray) -> tuple[float, float]:
    return k2b().k2a().ci_of(arr)


def cell_of(lo: float, hi: float) -> str:
    if lo > 0.0:
        return "UP"
    if hi < 0.0:
        return "DOWN"
    return "FLAT"


def lean_for(n_up: int, n_down: int) -> str:
    """Registration's predicates under the registered precedence
    L-R3 > L-R1 > L-R2 > L-R4."""
    if n_down >= 2:
        return "L-R3"
    if n_up >= 5 and n_down == 0:
        return "L-R1"
    if n_up + n_down <= 1:
        return "L-R2"
    return "L-R4"


def enumeration_table(n_arms: int = 6) -> dict[str, Any]:
    """Rule 16: the FULL adjudication object as one truth table -- every
    realizable (n_up, n_down) routed to exactly one lean and one pivot."""
    rows = []
    counts: dict[str, int] = {}
    raw_overlaps = []
    gaps = []
    for n_up in range(n_arms + 1):
        for n_down in range(n_arms + 1 - n_up):
            fired = [
                name for name, ok in (
                    ("L-R1", n_up >= 5 and n_down == 0),
                    ("L-R2", n_up + n_down <= 1),
                    ("L-R3", n_down >= 2),
                    ("L-R4", False),
                ) if ok
            ]
            lean = lean_for(n_up, n_down)
            if len(fired) > 1:
                raw_overlaps.append({"n_up": n_up, "n_down": n_down, "raw": fired,
                                     "resolved_by_precedence": lean})
            if not fired and lean != "L-R4":
                gaps.append({"n_up": n_up, "n_down": n_down})
            counts[lean] = counts.get(lean, 0) + 1
            rows.append({"n_up": n_up, "n_down": n_down,
                         "raw_predicates_true": fired, "lean": lean,
                         "pivot": {"L-R1": "P-R1", "L-R2": "P-R2",
                                   "L-R3": "P-R3", "L-R4": "P-R4"}[lean]})
    return {
        "n_arms": n_arms,
        "n_cells": len(rows),
        "rows": rows,
        "cells_per_lean": counts,
        "raw_predicate_overlaps_resolved_by_precedence": raw_overlaps,
        "unrouted_cells": gaps,
        "every_cell_routed_exactly_once": bool(not gaps and len(rows) == sum(counts.values())),
        "all_four_leans_reachable": bool(set(counts) == {"L-R1", "L-R2", "L-R3", "L-R4"}),
        "precedence": "L-R3 > L-R1 > L-R2 > L-R4",
    }


# ---------------------------------------------------------------------------
# G0r -- the anchors.

def rederive_anchors() -> dict[str, Any]:
    out: dict[str, Any] = {}
    m = k2b()

    # (0) k2d's disclosed single-object dispatcher (k2d:206-238), which
    #     k2e.rederive_anchors requires because K2c/K2d/K2e arms carry
    #     interaction shares.  It DELEGATES VERBATIM for the "zero" arm this
    #     leg's six arms use; k2d.verify_species_weights proves that bit-exactly
    #     and the proof is recorded here.
    k2d().install_species_weights()
    out["weights_dispatcher"] = k2d().verify_species_weights()

    # (i) K2e's own anchor re-derivation, called UNMODIFIED: K2b's lambda and
    #     A1/A4 recoveries, K2c's D_k and pooled q, K2d's 19-arm q19 and the
    #     six-pair kappa companion (kappa_hat -0.7220359963712748).
    a = k2e().rederive_anchors()
    for key in [k for k in a if k.startswith("_")]:
        a.pop(key)
    out["k2e_chain"] = a

    # (ii) all SIX K2b per-arm b-only recoveries, from K2b's own field CSVs
    dec = json.loads((K2B_OUT / "decision.json").read_text(encoding="utf-8"))
    persisted = dec["second_readings"]["per_arm_field_recovery"]
    rows = []
    for aid in arm_ids():
        field = read_csv_rt(K2B_OUT / f"arm_{aid}_field.csv").sort_values("world")
        re_b = float(np.mean(field["recovery_b_only"].to_numpy(float)))
        re_m = float(np.mean(field["recovery_mixed"].to_numpy(float)))
        rows.append({
            "arm": aid,
            "persisted_b_only": persisted[aid]["b_only_mean"],
            "rederived_b_only": re_b,
            "residual_b_only": re_b - persisted[aid]["b_only_mean"],
            "bit_exact_b_only": bool(re_b == persisted[aid]["b_only_mean"]),
            "persisted_mixed": persisted[aid]["mixed_mean"],
            "rederived_mixed": re_m,
            "bit_exact_mixed": bool(re_m == persisted[aid]["mixed_mean"]),
        })
    out["k2b_six_recoveries"] = {
        "rows": rows,
        "all_bit_exact": bool(all(r["bit_exact_b_only"] and r["bit_exact_mixed"] for r in rows)),
        "route": "round-trip re-read of results/m4_k2b_t4_branch/arm_<a>_field.csv, "
                 "mean over the 8 worlds, against decision.json's per-arm table",
    }

    # (iii) K2b's lambda, re-derived here as well as inside the K2e chain
    preds_persisted = read_csv_rt(K2B_OUT / "part0_predictions.csv").set_index("arm")
    pred_att = np.array([float(preds_persisted.loc[a, "r_card_b_pred_raw"]) for a in arm_ids()])
    meas = np.array([r["rederived_b_only"] for r in rows])
    lam = float(np.mean(meas) / np.mean(pred_att))
    out["k2b_lambda"] = {
        "persisted": dec["second_readings"]["efficiency_normalized_descriptive"]["lambda"],
        "rederived": lam, "registered_in_this_script": ANCHOR_LAMBDA_K2B,
        "bit_exact": bool(lam == ANCHOR_LAMBDA_K2B == dec["second_readings"][
            "efficiency_normalized_descriptive"]["lambda"]),
    }

    # (iv) this leg's Part-0 card predictions, against K2b's persisted ones
    pred_rows = []
    for aid, share, phi, w_int_arm in arms():
        p = m.arm_predictions(share, phi, w_int_arm)
        pred_rows.append({"arm": aid, **p})
    preds = pd.DataFrame(pred_rows)
    resid = {
        c: float(np.max(np.abs(
            preds.set_index("arm").loc[list(arm_ids()), c].to_numpy(float)
            - preds_persisted.loc[list(arm_ids()), c].to_numpy(float))))
        for c in ("r_card_b_pred_raw", "gap_pred", "rho_interleaved_pred",
                  "rho_contiguous_pred")
    }
    out["card_predictions"] = {
        "max_abs_residual_vs_k2b": resid,
        "bit_exact": bool(max(resid.values()) == 0.0),
        "r_card_b_pred_raw": {a: float(preds.set_index("arm").loc[a, "r_card_b_pred_raw"])
                              for a in arm_ids()},
    }

    # (v) K2e's kappa_hat, quoted by the registration
    k2e_dec = json.loads((K2E_OUT / "decision.json").read_text(encoding="utf-8"))
    out["k2e_kappa"] = {
        "persisted": k2e_dec["kappa_hat_registered"],
        "registered_in_this_script": ANCHOR_KAPPA,
        "rederived_via_k2e_chain": a["kappa_companion"]["kappa_rederived"],
        "bit_exact": bool(k2e_dec["kappa_hat_registered"] == ANCHOR_KAPPA
                          == a["kappa_companion"]["kappa_rederived"]),
        "kappa_9pair_companion": k2e_dec["kappa_refit_9pairs"]["kappa"],
    }
    out["k2e_q"] = {
        "q25_persisted": k2e_dec["q_update"]["q"],
        "q25_ci_persisted": k2e_dec["q_update"]["q_ci"],
        "q19_persisted": a["k2d"]["q19_persisted"],
        "q19_rederived": a["k2d"]["q19_rederived"],
        "q19_bit_exact": a["k2d"]["q19_bit_exact"],
    }

    # (vi) K1c' R_est / R_or
    k1c_dec = json.loads((K1C_OUT / "decision.json").read_text(encoding="utf-8"))
    frames = pd.concat([read_csv_rt(K1C_OUT / "arms_a.csv"),
                        read_csv_rt(K1C_OUT / "arms_b.csv")], ignore_index=True)
    piv = frames.pivot_table(index="world", columns="arm", values="agreement_mean")
    a0 = piv["A0"].to_numpy(float)
    a1 = piv["A1"].to_numpy(float)
    a4 = piv["A4"].to_numpy(float)
    ratio = float((a0 - a4).mean() / (a0 - a1).mean())
    persisted_ratio = k1c_dec["adjudication"]["L-3"]["ratio_est_over_or"]["point"]
    out["k1c_prime_ratio"] = {
        "persisted": persisted_ratio, "rederived": ratio,
        "registered_in_this_script": ANCHOR_RATIO_K1C,
        "residual": ratio - persisted_ratio,
        "n_worlds": int(len(piv)),
        "bit_exact": bool(ratio == persisted_ratio == ANCHOR_RATIO_K1C),
        "route": "round-trip re-read of results/m4_k1c_prime_author_share/arms_{a,b}.csv, "
                 "pivot by arm, mean(A0-A4)/mean(A0-A1) over 128 worlds (k1c':999-1003)",
    }

    out["all_bit_exact"] = bool(
        out["weights_dispatcher"]["zero_arm_bit_exact_after_patch"]
        and out["weights_dispatcher"]["int_zero_route_equals_zero_arm_bit_exact"]
        and a["all_bit_exact"] and out["k2b_six_recoveries"]["all_bit_exact"]
        and out["k2b_lambda"]["bit_exact"] and out["card_predictions"]["bit_exact"]
        and out["k2e_kappa"]["bit_exact"] and out["k2e_q"]["q19_bit_exact"]
        and out["k1c_prime_ratio"]["bit_exact"])
    return out


# ---------------------------------------------------------------------------
# G4r (b) -- the F2-composition collapse, through K1b's own machinery.

def g4r_f2_composition() -> dict[str, Any]:
    """K1b's A0 (shared, intact), A1 (shared, ORACLE common removal) and A4
    (shared, ESTIMATED per-(context,occasion) norm) re-run at world 0 through
    k1b._arm_world UNMODIFIED, and compared bit-exactly to K1b's persisted
    per-world rows.  Verifies that the object this leg transcribes IS K1b's,
    and exhibits the composition collapse directionally at that world."""
    kb = k1b()
    knobs, knob_tag = kb.knobs_and_tag()
    f2m = kb.f2()
    saved_seed = f2m.MASTER_SEED
    got: dict[str, float] = {}
    try:
        for arm in ("A0", "A1", "A4"):
            row = kb._arm_world(kb.arm_task(arm, 0, knobs, knob_tag, "main"))
            got[arm] = float(row["agreement_mean"])
    finally:
        f2m.MASTER_SEED = saved_seed
    per = pd.concat([read_csv_rt(K1B_OUT / "arms_a.csv"),
                     read_csv_rt(K1B_OUT / "arms_b.csv")], ignore_index=True)
    per0 = per[per["world"] == 0].set_index("arm")["agreement_mean"]
    persisted = {a: float(per0.loc[a]) for a in ("A0", "A1", "A4")}
    k1b_dec = json.loads((K1B_OUT / "decision.json").read_text(encoding="utf-8"))
    return {
        "world": 0,
        "rederived": got,
        "persisted": persisted,
        "residual": {a: got[a] - persisted[a] for a in got},
        "bit_exact": bool(all(got[a] == persisted[a] for a in got)),
        "R_or_world0": got["A0"] - got["A1"],
        "R_est_world0": got["A0"] - got["A4"],
        "ratio_world0": (got["A0"] - got["A4"]) / (got["A0"] - got["A1"]),
        "collapse_directional": bool((got["A0"] - got["A4"]) > 0.0
                                     and (got["A0"] - got["A1"]) > 0.0),
        "k1b_pooled_ratio_persisted": k1b_dec["adjudication"]["L-e"][
            "ratio_est_over_or"]["point"],
        "k1c_prime_pooled_ratio_persisted": ANCHOR_RATIO_K1C,
        "note": "descriptive (registration: 'consistency with K1b/K1c-prime's A4, "
                "descriptive'); the world-0 ratio is a single world, not a pooled estimate",
    }


# ---------------------------------------------------------------------------
# Stage: part0

def run_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    m = k2b()
    lay = m.layout()
    gates: dict[str, Any] = {
        "leg": "M4-K-R1",
        "banner": BANNER,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "pilot_worlds": list(PILOT_WORLDS),
        "worlds_default": WORLDS_DEFAULT,
        "variants": list(VARIANTS),
        "arms": [list(a) for a in arms()],
        "m_rec": M_REC,
        "mde_target": MDE_TARGET,
    }

    # ---- G0r ---------------------------------------------------------------
    t_g0 = time.time()
    g0 = rederive_anchors()
    g0["criterion"] = (
        "every anchor named by G0r re-derived BIT-EXACTLY from persisted artifacts "
        "under round-trip parsing: K2b's six per-arm b-only recoveries and its lambda; "
        "K2b/K2c/K2d's q chain and K2e's six-pair kappa_hat -0.7220359963712748 "
        "(via k2e.rederive_anchors, unmodified); K1c-prime's R_est/R_or "
        "0.7347498869811525; and this leg's card predictions against K2b's persisted "
        "part0_predictions.csv"
    )
    g0["pass"] = bool(g0["all_bit_exact"])
    g0["seconds"] = time.time() - t_g0
    gates["G0r"] = g0

    # ---- pilot -------------------------------------------------------------
    t_pilot = time.time()
    pilot_rows: list[dict[str, Any]] = []
    card_rows: list[dict[str, Any]] = []
    truth_field_diff: list[dict[str, Any]] = []
    world_cache: dict[tuple[int, float], dict[str, np.ndarray]] = {}

    def get_world(w_idx: int, phi: float) -> dict[str, np.ndarray]:
        key = (w_idx, phi)
        if key not in world_cache:
            if len(world_cache) > 2:
                world_cache.clear()
            world_cache[key] = m.build_k2b_world(world_seed_for(w_idx), phi)
        return world_cache[key]

    for w_idx in PILOT_WORLDS:
        for aid, share, phi, w_int_arm in arms():
            world = get_world(w_idx, phi)
            w = m.arm_weights(share, w_int_arm)
            fields: dict[str, dict[str, Any]] = {}
            for variant in VARIANTS:
                row = run_field_world_variant(aid, w_idx, world, w, phi, variant,
                                              verify=True)
                fields[variant] = row.pop("_field_b")
                pilot_rows.append({k: v for k, v in row.items() if not k.startswith("_")})
                stats, digest, n_rows, sums = card_for_world(world, w, world_seed_for(w_idx))
                card_rows.append({
                    "arm": aid, "variant": variant, "world": w_idx,
                    "card_sha256": digest, "card_n_rows": n_rows,
                    "gap": stats["gap"], "r_card_b_raw": stats["r_card_b_raw"],
                    "rho_interleaved": stats["rho_interleaved"],
                    "rho_contiguous": stats["rho_contiguous"], **sums,
                })
            fi, fd = fields["intact"], fields["deframed"]
            truth_field_diff.append({
                "arm": aid, "world": w_idx,
                "max_abs_truth_b_field_diff": float(
                    max(float(np.max(np.abs(fi[c] - fd[c]))) for c in fi)),
                "min_matrix_cosine_truth_b": float(
                    min(float(v8._matrix_cosine(fi[c], fd[c])) for c in fi)),
            })
    pilot = pd.DataFrame(pilot_rows)
    pilot.to_csv(OUT / "part0_pilot.csv", index=False)
    pd.DataFrame(card_rows).to_csv(OUT / "part0_pilot_card.csv", index=False)
    pilot_seconds = time.time() - t_pilot

    # ---- G2r: designed invariance of the CARD channel ----------------------
    cdf = pd.DataFrame(card_rows)
    inv_rows = []
    for aid in arm_ids():
        for w_idx in PILOT_WORLDS:
            sub = cdf[(cdf["arm"] == aid) & (cdf["world"] == w_idx)]
            a_row = sub[sub["variant"] == "intact"].iloc[0]
            b_row = sub[sub["variant"] == "deframed"].iloc[0]
            scols = [c for c in cdf.columns if c.startswith("csum_")]
            inv_rows.append({
                "arm": aid, "world": w_idx,
                "sha256_equal": bool(a_row["card_sha256"] == b_row["card_sha256"]),
                "max_abs_sum_diff": float(np.max(np.abs(
                    a_row[scols].to_numpy(float) - b_row[scols].to_numpy(float)))),
                "gap_diff": float(a_row["gap"] - b_row["gap"]),
                "r_diff": float(a_row["r_card_b_raw"] - b_row["r_card_b_raw"]),
            })
    g2 = {
        "per_cell": inv_rows,
        "n_checked": len(inv_rows),
        "n_sha256_equal": int(sum(r["sha256_equal"] for r in inv_rows)),
        "max_abs_sum_diff": float(max(r["max_abs_sum_diff"] for r in inv_rows)),
        "max_abs_gap_diff": float(max(abs(r["gap_diff"]) for r in inv_rows)),
        "criterion": "the CARD channel is BIT-IDENTICAL across gauge variants "
                     "(sha256 of the float64 numeric block equal in every cell AND "
                     "max |column-sum difference| == 0.0); ANY difference is an "
                     "implementation defect and STOPS the leg",
        "structural_note": "the card channel (k2b:381-457) is a function of the world "
                           "channels and the arm weights only; it never touches the "
                           "gauge's input path.  The check is a defect detector for "
                           "accidental coupling (e.g. in-place mutation of the world).",
    }
    g2["pass"] = bool(g2["n_sha256_equal"] == g2["n_checked"] and g2["max_abs_sum_diff"] == 0.0)
    gates["G2r"] = g2

    # ---- G4r: de-framing liveness -----------------------------------------
    t_g4 = time.time()
    live_rows = []
    for aid in arm_ids():
        sub = pilot[(pilot["arm"] == aid) & (pilot["variant"] == "deframed")]
        base = pilot[(pilot["arm"] == aid) & (pilot["variant"] == "intact")]
        live_rows.append({
            "arm": aid,
            "deframe_panel_rms_mean": float(sub["deframe_panel_rms"].mean()),
            "deframe_panel_rms_min": float(sub["deframe_panel_rms"].min()),
            "panel_rms_intact_mean": float(base["panel_rms_intact"].mean()),
            "relative_rms": float(sub["deframe_panel_rms"].mean()
                                  / base["panel_rms_intact"].mean()),
        })
    g4: dict[str, Any] = {
        "per_arm": live_rows,
        "min_rms": float(min(r["deframe_panel_rms_min"] for r in live_rows)),
        "truth_field_diff": truth_field_diff,
        "max_truth_b_field_abs_diff": float(
            max(r["max_abs_truth_b_field_diff"] for r in truth_field_diff)),
        "min_truth_b_field_cosine": float(
            min(r["min_matrix_cosine_truth_b"] for r in truth_field_diff)),
    }
    g4["f2_composition"] = g4r_f2_composition()
    g4["criterion"] = ("the subtraction moves the gauge's input panels in EVERY arm "
                       "(RMS > 0) AND K1b's A0/A1/A4 reproduce bit-exactly at world 0 "
                       "with the composition collapse directionally intact (descriptive)")
    g4["pass"] = bool(g4["min_rms"] > 0.0
                      and g4["f2_composition"]["bit_exact"]
                      and g4["f2_composition"]["collapse_directional"])
    g4["seconds"] = time.time() - t_g4
    gates["G4r"] = g4

    # ---- G1r: power --------------------------------------------------------
    rec = {
        (a, v): pilot[(pilot["arm"] == a) & (pilot["variant"] == v)]
        .sort_values("world")["recovery_b_only"].to_numpy(float)
        for a in arm_ids() for v in VARIANTS
    }
    g1: dict[str, Any] = {"per_arm": [], "n_pilot_worlds": len(PILOT_WORLDS),
                          "mde_definition": "MDE(80%, alpha=.05, paired, n) = "
                                            "(t_{.975,n-1}+t_{.80,n-1}) sd_pilot(d_a)/sqrt(n), "
                                            "scipy quantiles"}
    ladder_ok: dict[int, bool] = {}
    for n_worlds in ESCALATION_LADDER:
        ladder_ok[n_worlds] = True
    for aid in arm_ids():
        d = rec[(aid, "deframed")] - rec[(aid, "intact")]
        sd = float(np.std(d, ddof=1))
        entry = {
            "arm": aid,
            "pilot_d": [float(x) for x in d],
            "pilot_d_mean": float(np.mean(d)),
            "pilot_sd_d": sd,
            "pilot_recovery_intact": [float(x) for x in rec[(aid, "intact")]],
            "pilot_recovery_deframed": [float(x) for x in rec[(aid, "deframed")]],
        }
        for n_worlds in ESCALATION_LADDER:
            mde = mde_paired(sd, n_worlds)
            entry[f"mde_n{n_worlds}"] = mde
            entry[f"meets_target_n{n_worlds}"] = bool(mde <= MDE_TARGET)
            ladder_ok[n_worlds] = ladder_ok[n_worlds] and bool(mde <= MDE_TARGET)
        g1["per_arm"].append(entry)
    chosen = next((n for n in ESCALATION_LADDER if ladder_ok[n]), None)
    g1["ladder_all_arms_meet_target"] = {str(n): ladder_ok[n] for n in ESCALATION_LADDER}
    g1["worlds_selected"] = chosen if chosen is not None else ESCALATION_LADDER[-1]
    g1["escalated"] = bool(chosen is not None and chosen != ESCALATION_LADDER[0])
    g1["tiering_required"] = bool(chosen is None)
    g1["max_mde_at_selection"] = float(max(
        e[f"mde_n{g1['worlds_selected']}"] for e in g1["per_arm"]))
    g1["criterion"] = (f"MDE(80%, .05, paired) for d_a <= {MDE_TARGET} in EVERY arm; "
                       "escalate 32->64 once; still short -> RUN AND TIER (registered, "
                       "so the gate passes and the short arms are tiered at adjudication)")
    g1["pass"] = True
    gates["G1r"] = g1

    # ---- rule-9 second readings (all reported, none gating) ----------------
    t_sr = time.time()
    second: dict[str, list[dict[str, Any]]] = {}
    for tag, kwargs in (
        ("RN-3 donor_channels=expressive", {"donor_channels": "expressive"}),
        ("RN-5 pool_scheme=per_occasion", {"pool_scheme": "per_occasion"}),
        ("RN-2 deframe_truth=True", {"deframe_truth": True}),
    ):
        rows = []
        for w_idx in PILOT_WORLDS:
            for aid, share, phi, w_int_arm in arms():
                world = get_world(w_idx, phi)
                w = m.arm_weights(share, w_int_arm)
                r = run_field_world_variant(aid, w_idx, world, w, phi, "deframed", **kwargs)
                r.pop("_field_b")
                rows.append(r)
        second[tag] = rows
    sr_frames = {tag: pd.DataFrame(rows) for tag, rows in second.items()}
    pd.concat([f.assign(reading=tag) for tag, f in sr_frames.items()],
              ignore_index=True).to_csv(OUT / "part0_second_readings.csv", index=False)
    sr_summary = {}
    for tag, frame in sr_frames.items():
        per_arm = []
        for aid in arm_ids():
            sub = frame[frame["arm"] == aid].sort_values("world")
            d = sub["recovery_b_only"].to_numpy(float) - rec[(aid, "intact")]
            prim = rec[(aid, "deframed")] - rec[(aid, "intact")]
            per_arm.append({
                "arm": aid,
                "recovery_mean": float(sub["recovery_b_only"].mean()),
                "d_mean": float(np.mean(d)),
                "d_mean_primary": float(np.mean(prim)),
                "d_shift_vs_primary": float(np.mean(d) - np.mean(prim)),
                "same_sign_as_primary": bool(np.sign(np.mean(d)) == np.sign(np.mean(prim))),
            })
        sr_summary[tag] = {
            "per_arm": per_arm,
            "arms_same_sign_as_primary": int(sum(r["same_sign_as_primary"] for r in per_arm)),
            "max_abs_shift_vs_primary": float(max(abs(r["d_shift_vs_primary"]) for r in per_arm)),
        }
    gates["rule9_second_readings"] = {
        "gate": "NONE (disclosed readings, standing rule 9; the PRIMARY convention is "
                "pinned in the script docstring and RN-2/RN-3/RN-5 above)",
        "summary": sr_summary,
        "seconds": time.time() - t_sr,
    }

    # ---- G3r: rule-11 satisfiability with directions + rule-13 spec --------
    n_sel = int(g1["worlds_selected"])
    clauses = []
    for entry in g1["per_arm"]:
        sd = entry["pilot_sd_d"]
        hw = 1.96 * sd / math.sqrt(n_sel)
        clauses.append({
            "clause": f"d_{entry['arm']} 95% CI excludes 0 (cell UP if lo>0, DOWN if hi<0, "
                      "else FLAT)",
            "direction": "two-sided CI; the SIGN of the excluded interval assigns the cell",
            "satisfiable": bool(sd > 0.0 and math.isfinite(hw)),
            "note": f"pilot sd(d) {sd:.10f}; projected half-width at n={n_sel} "
                    f"{hw:.10f}; realized MDE target {MDE_TARGET}; pilot |d| "
                    f"{abs(entry['pilot_d_mean']):.10f} "
                    f"({abs(entry['pilot_d_mean']) / hw:.3f}x the projected half-width)",
        })
    clauses.append({
        "clause": "Delta lambda 95% CI vs 0 (DESCRIPTIVE, no gate)",
        "direction": "two-sided",
        "satisfiable": True,
        "note": "Delta lambda = (mean_a d_a)/mean_a r_pred(a); r_pred is variant-invariant "
                "card algebra, so the CI is a rescaling of the mean-d CI",
    })
    clauses.append({
        "clause": "Delta q 95% CI vs 0 (DESCRIPTIVE, no gate)",
        "direction": "two-sided",
        "satisfiable": True,
        "note": "q = OLS slope of log(mean recovery) on log(r_pred) over the 6 arms via "
                "k2d.pooled_q, unmodified; x is variant-invariant so Delta q is a pure "
                "y-shift slope difference; log is undefined at a non-positive bootstrap "
                "mean recovery -- the count of such draws is reported at finalize",
    })
    enum = enumeration_table(len(arm_ids()))
    clauses.append({
        "clause": "lean predicates (L-R1..L-R4) partition all (n_up, n_down)",
        "direction": "deterministic",
        "satisfiable": bool(enum["every_cell_routed_exactly_once"]
                            and enum["all_four_leans_reachable"]),
        "note": f"{enum['n_cells']} realizable cells, all routed exactly once under "
                f"precedence {enum['precedence']}; cells per lean "
                f"{enum['cells_per_lean']}; raw-predicate overlaps resolved by "
                f"precedence: {len(enum['raw_predicate_overlaps_resolved_by_precedence'])}",
    })
    g3 = {
        "b_draws": B_BOOT, "seed": MASTER_SEED, "b_draws_stability": B_BOOT_HIGH,
        "resampling": "paired world-block bootstrap: ONE pick matrix "
                      "default_rng(MASTER_SEED).integers(0, n, (B, n)) shared by every arm "
                      "and BOTH gauge variants, so d_a is resampled paired",
        "clauses": clauses,
        "rule13": "every interval clause is checked at B=20000 when the boundary (0) lies "
                  "within 2x the Monte-Carlo sd of the relevant CI endpoint; a verdict flip "
                  "scores the clause BOUNDARY",
        "enumeration": enum,
    }
    g3["pass"] = bool(all(c["satisfiable"] for c in clauses))
    gates["G3r"] = g3

    # ---- G5r: hygiene ------------------------------------------------------
    gates["G5r"] = {
        "pass": True,
        "round_trip_parsing_everywhere": True,
        "float_precision": "round_trip",
        "stages_chunked": ["part0", "arms --worlds LO:HI", "finalize"],
        "background_jobs": 0,
        "monitors": 0,
        "rule12_source_objects": {
            "six state arms A1..A6": "scripts/run_suica_m4_k2b_t4_branch.py:97-105 (ARMS), "
                                     "k2b:194-206 (arm_weights)",
            "expressive world": "scripts/run_suica_m4_k2b_t4_branch.py:305-346 "
                                "(build_k2b_world)",
            "panel emission (gauge input format)": "k2b:352-375 (emit_panel)",
            "frame channel common(context,o)": "scripts/run_suica_m4_f2_composition.py:121-126 "
                                               "(f2.shock_vector, via k2b.build_k2b_world)",
            "mu_hat: 32 disjoint donors per context": "scripts/run_suica_m4_k1b_composition_"
                                                      "ownership.py:87 (A4_AUTHORS_PER_CONTEXT), "
                                                      "k1b:278-307 (estimated_occasion_norm), "
                                                      "k1b:263-276 (_gen_estimated)",
            "mu_hat donor channel list": "k1b:296 (idio := mean_part + noise_part) -- "
                                         "transcribed as w_mu*trait + w_e*noise",
            "mu_hat frame term": "k1b:303-306 (c_vec := the PANEL's common vector) -- "
                                 "transcribed as w_common * world['common'][ctx, occ]",
            "norm-pool seeding": "k1b:290-292 (stable_bucket(f'{world_seed}-normpool', ...))",
            "pre-map subtraction": "k1b:270-275",
            "card channel": "k2b:381-457 (card_channel_frame), k2b:463-489 "
                            "(pooled_card_stats)",
            "b-only / mixed truth construction": "k2b:698-701 (emit_panel channel selection), "
                                                 "pattern from run_suica_m4_f5_gauge_validity.py"
                                                 ":225-372,494,505",
            "deployed featurize": "scripts/run_suica_m4_f1_panel_sizing.py:166-229",
            "deployed field + agreement": "scripts/run_suica_m4_e1_convention_gap.py:230-258",
            "q refit": "scripts/run_suica_m4_k2d_frontier_carrier.py:644-670 (pooled_q)",
            "anchor chain": "scripts/run_suica_m4_k2e_double_matching.py:596-745 "
                            "(rederive_anchors)",
        },
        "rule14_self_check": (
            "Every gated quantity is RECOVERY vs RECOVERY on the same instrument at the "
            "same scale: d_a = recovery_deframed(a) - recovery_intact(a), both produced by "
            "e1.field_agreement against the SAME intact truth field, in the same units, on "
            "the same 32 paired worlds.  The margin m_rec = 0.010 and the MDE target live "
            "in that same recovery scale.  No gate and no lean compares across scales or "
            "instruments, so rule 14's first clause is not engaged.  The (Delta lambda, "
            "Delta q) parameter story IS cross-scale in content (a card-space attenuation "
            "enters as the regressor) and is therefore reported as DESCRIPTIVE with CIs and "
            "NO gate, per the registration's own wording."
        ),
        "rule17_realizability": (
            "Both gauge variants are realizable at every arm by construction: G-intact is "
            "the deployed gauge, and G-deframed's donor pool (32 authors per context, 4 "
            "contexts, 16 occasions) exists in every world of this family.  G4r measures the "
            "liveness rather than assuming it."
        ),
    }

    gates["part0_all_pass"] = bool(
        gates["G0r"]["pass"] and gates["G1r"]["pass"] and gates["G2r"]["pass"]
        and gates["G3r"]["pass"] and gates["G4r"]["pass"] and gates["G5r"]["pass"])
    gates["stage_seconds"] = {"total": time.time() - t0, "G0r": g0["seconds"],
                              "pilot": pilot_seconds, "G4r": g4["seconds"],
                              "second_readings": gates["rule9_second_readings"]["seconds"]}
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n",
                                    encoding="utf-8")
    write_manifest({"part0": time.time() - t0})
    print(json.dumps({
        "stage": "part0",
        "seconds": round(time.time() - t0, 3),
        "part0_all_pass": gates["part0_all_pass"],
        **{g: gates[g]["pass"] for g in ("G0r", "G1r", "G2r", "G3r", "G4r", "G5r")},
        "worlds_selected": g1["worlds_selected"],
        "max_mde": g1["max_mde_at_selection"],
        "per_arm_mde_n32": {e["arm"]: e["mde_n32"] for e in g1["per_arm"]},
        "per_arm_pilot_d": {e["arm"]: e["pilot_d_mean"] for e in g1["per_arm"]},
        "g2r_card_bit_identical": g2["pass"],
        "g4r_min_rms": g4["min_rms"],
        "anchors_bit_exact": g0["all_bit_exact"],
    }, indent=2, default=str))


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
    n_worlds = int(gates["G1r"]["worlds_selected"])
    lo, hi = (int(x) for x in args.worlds.split(":")) if args.worlds else (0, n_worlds)
    hi = min(hi, n_worlds)
    t0 = time.time()
    m = k2b()
    rows: dict[tuple[str, str], list[dict[str, Any]]] = {
        (a, v): [] for a in arm_ids() for v in VARIANTS
    }
    for world_index in range(lo, hi):
        for phi in sorted({a[2] for a in arms()}):
            world = m.build_k2b_world(world_seed_for(world_index), phi)
            for aid, share, a_phi, w_int_arm in arms():
                if a_phi != phi:
                    continue
                w = m.arm_weights(share, w_int_arm)
                for variant in VARIANTS:
                    r = run_field_world_variant(aid, world_index, world, w, phi, variant)
                    r.pop("_field_b")
                    # G2r: the card channel is recomputed AFTER the gauge run in
                    # each variant, so an in-place mutation of the world by the
                    # de-framing path would show up as a digest mismatch.
                    v_stats, v_digest, v_n, v_sums = card_for_world(
                        world, w, world_seed_for(world_index))
                    r.update({
                        "card_sha256": v_digest, "card_n_rows": v_n,
                        "card_gap": v_stats["gap"],
                        "card_r_card_b_raw": v_stats["r_card_b_raw"],
                        "card_rho_interleaved": v_stats["rho_interleaved"],
                        "card_rho_contiguous": v_stats["rho_contiguous"],
                        **v_sums,
                    })
                    rows[(aid, variant)].append(r)
            del world
        print(f"  world {world_index}: {time.time() - t0:.1f}s", flush=True)
    for (aid, variant), rs in rows.items():
        if not rs:
            continue
        pd.DataFrame(rs).to_csv(
            OUT / f"cell_{aid}_{variant}_w{lo:03d}_{hi - 1:03d}.csv", index=False)
    write_manifest({f"arms[w{lo:03d}:{hi:03d}]": time.time() - t0})
    print(json.dumps({"stage": "arms", "worlds": [lo, hi],
                      "cells": len(rows), "seconds": round(time.time() - t0, 3)}, indent=2))


# ---------------------------------------------------------------------------
# Stage: finalize

def load_cells(n_worlds: int) -> dict[tuple[str, str], pd.DataFrame]:
    out: dict[tuple[str, str], pd.DataFrame] = {}
    for aid in arm_ids():
        for variant in VARIANTS:
            parts = sorted(OUT.glob(f"cell_{aid}_{variant}_w*.csv"))
            if not parts:
                raise SystemExit(f"REFUSED: missing cell artifact for {aid}/{variant}")
            frame = pd.concat([read_csv_rt(p) for p in parts], ignore_index=True)
            frame = frame.sort_values("world").reset_index(drop=True)
            seen = sorted(int(x) for x in frame["world"])
            if len(frame) != n_worlds or seen != list(range(n_worlds)):
                raise SystemExit(
                    f"REFUSED: {aid}/{variant} has {len(frame)} worlds, expected {n_worlds}")
            out[(aid, variant)] = frame
    return out


def run_finalize(args: argparse.Namespace) -> None:
    gates = require_part0()
    t0 = time.time()
    n_worlds = int(gates["G1r"]["worlds_selected"])
    cells = load_cells(n_worlds)
    k2a = k2b().k2a()

    # ---- G2r on the FULL run (every main cell, not just the pilot)
    inv = []
    scols = [c for c in cells[(arm_ids()[0], "intact")].columns if c.startswith("csum_")]
    for aid in arm_ids():
        a_f, b_f = cells[(aid, "intact")], cells[(aid, "deframed")]
        eq = bool((a_f["card_sha256"].to_numpy() == b_f["card_sha256"].to_numpy()).all())
        dmax = float(np.max(np.abs(a_f[scols].to_numpy(float) - b_f[scols].to_numpy(float))))
        inv.append({"arm": aid, "worlds": int(len(a_f)), "sha256_equal_all_worlds": eq,
                    "max_abs_sum_diff": dmax,
                    "max_abs_gap_diff": float(np.max(np.abs(
                        a_f["card_gap"].to_numpy(float) - b_f["card_gap"].to_numpy(float))))})
    g2_main = {
        "per_arm": inv,
        "n_worlds_checked": int(sum(r["worlds"] for r in inv)) * 1,
        "all_bit_identical": bool(all(r["sha256_equal_all_worlds"] for r in inv)
                                  and max(r["max_abs_sum_diff"] for r in inv) == 0.0),
        "max_abs_sum_diff": float(max(r["max_abs_sum_diff"] for r in inv)),
    }
    if not g2_main["all_bit_identical"]:
        raise SystemExit("STOP (G2r): the card channel differs across gauge variants — "
                         "implementation defect, per the registration.")

    # ---- the paired world-block bootstrap (ONE pick matrix, shared everywhere)
    pick = np.random.default_rng(MASTER_SEED).integers(0, n_worlds, size=(B_BOOT, n_worlds))
    pick_hi = np.random.default_rng(MASTER_SEED).integers(
        0, n_worlds, size=(B_BOOT_HIGH, n_worlds))
    rec = {(a, v): cells[(a, v)]["recovery_b_only"].to_numpy(float)
           for a in arm_ids() for v in VARIANTS}
    mix = {(a, v): cells[(a, v)]["recovery_mixed"].to_numpy(float)
           for a in arm_ids() for v in VARIANTS}
    boot = {k: arr[pick].mean(axis=1) for k, arr in rec.items()}
    boot_hi = {k: arr[pick_hi].mean(axis=1) for k, arr in rec.items()}
    boot_mix = {k: arr[pick].mean(axis=1) for k, arr in mix.items()}

    per_arm: list[dict[str, Any]] = []
    rule13: list[dict[str, Any]] = []
    for aid in arm_ids():
        di = rec[(aid, "deframed")] - rec[(aid, "intact")]
        db = boot[(aid, "deframed")] - boot[(aid, "intact")]
        lo, hi = ci_of(db)
        cell = cell_of(lo, hi)
        i_lo, i_hi = ci_of(boot[(aid, "intact")])
        d_lo, d_hi = ci_of(boot[(aid, "deframed")])
        mi_lo, mi_hi = ci_of(boot_mix[(aid, "intact")])
        md_lo, md_hi = ci_of(boot_mix[(aid, "deframed")])
        dm = boot_mix[(aid, "deframed")] - boot_mix[(aid, "intact")]
        dm_lo, dm_hi = ci_of(dm)
        sd = float(np.std(di, ddof=1))
        entry = {
            "arm": aid,
            "recovery_intact": float(np.mean(rec[(aid, "intact")])),
            "recovery_intact_ci": [i_lo, i_hi],
            "recovery_intact_sd_worlds": float(np.std(rec[(aid, "intact")], ddof=1)),
            "recovery_deframed": float(np.mean(rec[(aid, "deframed")])),
            "recovery_deframed_ci": [d_lo, d_hi],
            "recovery_deframed_sd_worlds": float(np.std(rec[(aid, "deframed")], ddof=1)),
            "d": float(np.mean(di)),
            "d_ci": [lo, hi],
            "d_se": float(np.std(db, ddof=1)),
            "d_cell": cell,
            "d_per_world_positive": int(np.sum(di > 0.0)),
            "d_realized_sd": sd,
            "d_realized_mde": mde_paired(sd, n_worlds),
            "d_material_vs_m_rec": bool(abs(float(np.mean(di))) >= M_REC),
            "d_ci_inside_margin": bool(lo > -M_REC and hi < M_REC),
            "mixed_intact": float(np.mean(mix[(aid, "intact")])),
            "mixed_intact_ci": [mi_lo, mi_hi],
            "mixed_deframed": float(np.mean(mix[(aid, "deframed")])),
            "mixed_deframed_ci": [md_lo, md_hi],
            "d_mixed": float(np.mean(mix[(aid, "deframed")]) - np.mean(mix[(aid, "intact")])),
            "d_mixed_ci": [dm_lo, dm_hi],
            "d_mixed_cell": cell_of(dm_lo, dm_hi),
            "deframe_panel_rms": float(cells[(aid, "deframed")]["deframe_panel_rms"].mean()),
            "card_gap_pooled": pool_card_sums(cells[(aid, "intact")])["gap"],
            "card_r_pooled": pool_card_sums(cells[(aid, "intact")])["r_card_b_raw"],
        }
        # rule 13 on the gated interval clause
        mc = k2a.mc_sd_of_endpoint(db, B_BOOT, 0.025)
        dist = min(abs(lo), abs(hi))
        db_hi = boot_hi[(aid, "deframed")] - boot_hi[(aid, "intact")]
        lo2, hi2 = ci_of(db_hi)
        cell2 = cell_of(lo2, hi2)
        triggered = bool(dist <= 2.0 * mc)
        rule13.append({
            "clause": f"d_{aid} CI vs 0",
            "boundary": 0.0,
            "mc_sd_endpoint_B2000": mc,
            "distance_to_boundary": dist,
            "distance_in_mc_sd": dist / mc if mc > 0 else float("inf"),
            "triggered": triggered,
            "cell_B2000": cell, "cell_B20000": cell2,
            "endpoints_B20000": [lo2, hi2],
            "status": ("STABLE" if cell == cell2 else "BOUNDARY") if triggered else "NOT_TRIGGERED",
        })
        entry["rule13_status"] = rule13[-1]["status"]
        per_arm.append(entry)

    n_up = int(sum(1 for e in per_arm if e["d_cell"] == "UP"))
    n_down = int(sum(1 for e in per_arm if e["d_cell"] == "DOWN"))
    lean = lean_for(n_up, n_down)
    pivot = {"L-R1": "P-R1", "L-R2": "P-R2", "L-R3": "P-R3", "L-R4": "P-R4"}[lean]

    # ---- parameter story ---------------------------------------------------
    preds = {a: v for a, v in
             json.loads((OUT / "gates.json").read_text(encoding="utf-8"))["G0r"][
                 "card_predictions"]["r_card_b_pred_raw"].items()}
    pred_att = np.array([float(preds[a]) for a in arm_ids()])
    x_log = np.log(pred_att)
    lam_den = float(np.mean(pred_att))
    lam: dict[str, Any] = {}
    q: dict[str, Any] = {}
    boot_lam = {}
    for variant in VARIANTS:
        meas = np.array([float(np.mean(rec[(a, variant)])) for a in arm_ids()])
        lam_pt = float(np.mean(meas) / lam_den)
        bl = np.stack([boot[(a, variant)] for a in arm_ids()], axis=1).mean(axis=1) / lam_den
        boot_lam[variant] = bl
        l_lo, l_hi = ci_of(bl)
        lam[variant] = {"lambda": lam_pt, "ci": [l_lo, l_hi],
                        "se": float(np.std(bl, ddof=1))}
        with np.errstate(invalid="ignore", divide="ignore"):
            res = k2d().pooled_q([(x_log, [rec[(a, variant)] for a in arm_ids()])],
                                 ANCHOR_LAMBDA_K2B, B_BOOT, MASTER_SEED)
        qb = res.pop("q_boot")
        finite = np.isfinite(qb)
        q[variant] = {k: v for k, v in res.items()}
        # The closed form's log-log link needs a POSITIVE pooled recovery in
        # every arm.  Report estimability explicitly instead of a NaN.
        neg = {a: float(np.mean(rec[(a, variant)])) for a in arm_ids()
               if float(np.mean(rec[(a, variant)])) <= 0.0}
        q[variant]["estimable"] = bool(not neg and np.isfinite(res["q"]))
        q[variant]["non_positive_arm_recoveries"] = neg
        q[variant]["nonfinite_bootstrap_draws"] = int(np.sum(~finite))
        q[variant]["conditional_subset_ci_NOT_A_CI"] = (
            list(ci_of(qb[finite])) if not q[variant]["estimable"] else None)
        q[variant]["_boot"] = qb
    d_lam = boot_lam["deframed"] - boot_lam["intact"]
    dl_lo, dl_hi = ci_of(d_lam)
    d_q = q["deframed"]["_boot"] - q["intact"]["_boot"]
    dq_finite = np.isfinite(d_q)
    dq_lo, dq_hi = ci_of(d_q[dq_finite])
    n_bad = int(np.sum(~dq_finite))
    for variant in VARIANTS:
        q[variant].pop("_boot")

    # kappa: is a K2e-style pair regression admissible on THIS leg's arms?
    pairs = [(a, b, float(abs(preds[a] - preds[b])))
             for a, b in itertools.combinations(arm_ids(), 2)]
    min_gap = min(p[2] for p in pairs)
    kappa_block = {
        "estimable": False,
        "reason": (
            "the K2e-style kappa regression regresses the WITHIN-PAIR field-recovery "
            "difference D on the within-pair person-variance difference Delta V_person, "
            "and is identified only when the pair's predicted CARD ATTENUATION is MATCHED "
            "so that the lambda*r^q term cancels (K2c/K2d/K2e built such pairs by "
            "construction).  This leg reuses K2b's six state arms, which are NOT "
            "attenuation-matched: the 15 pairwise |Delta r_pred| range from "
            f"{min_gap:.10f} to {max(p[2] for p in pairs):.10f}, none is 0, and the "
            "smallest is 2 orders of magnitude above the matched-pair tolerance K2e "
            "achieved (<=1e-16).  Moreover the de-framing manipulation changes NEITHER r "
            "NOR V_person -- it changes only the gauge's input -- so no intact-vs-deframed "
            "contrast carries Delta V_person leverage at all.  Per the registration "
            "('IF the leg's arms admit it (if not, state so and report the pieces that are "
            "estimable — do not invent pairs)'), no pair is invented and no kappa is "
            "reported for either variant."),
        "pairwise_abs_delta_r_pred": [
            {"pair": f"{a}-{b}", "abs_delta_r_pred": g} for a, b, g in pairs],
        "min_abs_delta_r_pred": min_gap,
        "k2e_anchor_kappa": ANCHOR_KAPPA,
    }
    param = {
        "lambda": lam,
        "delta_lambda": {"point": lam["deframed"]["lambda"] - lam["intact"]["lambda"],
                         "ci": [dl_lo, dl_hi], "se": float(np.std(d_lam, ddof=1)),
                         "cell": cell_of(dl_lo, dl_hi)},
        "q": q,
        "delta_q": ({
            "estimable": True,
            "point": q["deframed"]["q"] - q["intact"]["q"],
            "ci": [dq_lo, dq_hi], "se": float(np.std(d_q[dq_finite], ddof=1)),
            "cell": cell_of(dq_lo, dq_hi),
            "non_finite_bootstrap_draws": n_bad,
        } if all(q[v]["estimable"] for v in VARIANTS) else {
            "estimable": False,
            "point": None, "ci": None, "cell": "NOT_ESTIMABLE",
            "non_finite_bootstrap_draws": n_bad,
            "conditional_subset_ci_NOT_A_CI": [dq_lo, dq_hi],
            "reason": (
                "T4's closed form is a POWER LAW, field = lambda*r^q, whose q is "
                "identified by a log-log slope; that requires a POSITIVE pooled "
                "recovery in every arm.  Under G-deframed the pooled recovery is at "
                "or below zero in "
                + ", ".join(f"{a} ({v!r})" for a, v in
                            q["deframed"]["non_positive_arm_recoveries"].items())
                + f", and {n_bad} of {B_BOOT} paired bootstrap draws are non-finite, so "
                "q_deframed and therefore Delta q do NOT exist.  The bracketed interval "
                "is the spread over the finite draws ONLY -- a selected subset, not a "
                "confidence interval, and it is reported for disclosure, not for use.  "
                "Per the registration's instruction for the parameter story, the "
                "estimable pieces are reported and nothing is invented: q_intact stands "
                "with its CI, Delta lambda stands with its CI."),
        }),
        "delta_kappa": kappa_block,
        "gate": "NONE (registration: 'Parameter story (descriptive, no gate)')",
        "x_convention": "Part-0 PREDICTED card attenuation r_card_b_pred_raw, variant-"
                        "invariant by G2r; identical to the K2c/K2d/K2e convention",
    }
    for name, block in (("delta_lambda", param["delta_lambda"]), ("delta_q", param["delta_q"])):
        if block.get("ci") is None:
            rule13.append({"clause": f"{name} CI vs 0 (DESCRIPTIVE)", "boundary": 0.0,
                           "triggered": False, "status": "NOT_APPLICABLE",
                           "reason": "the quantity is not estimable (see "
                                     "parameter_story.delta_q.reason)"})
            continue
        arr = d_lam if name == "delta_lambda" else d_q[dq_finite]
        mc = k2a.mc_sd_of_endpoint(arr, B_BOOT, 0.025)
        dist = min(abs(block["ci"][0]), abs(block["ci"][1]))
        if name == "delta_lambda":
            arr_hi = (np.stack([boot_hi[(a, "deframed")] for a in arm_ids()], axis=1).mean(axis=1)
                      - np.stack([boot_hi[(a, "intact")] for a in arm_ids()], axis=1).mean(axis=1)
                      ) / lam_den
        else:
            arr_hi = None
        triggered = bool(dist <= 2.0 * mc)
        row = {"clause": f"{name} CI vs 0 (DESCRIPTIVE)", "boundary": 0.0,
               "mc_sd_endpoint_B2000": mc, "distance_to_boundary": dist,
               "distance_in_mc_sd": dist / mc if mc > 0 else float("inf"),
               "triggered": triggered}
        if triggered and arr_hi is not None:
            l2, h2 = ci_of(arr_hi)
            row.update({"cell_B2000": block["cell"], "cell_B20000": cell_of(l2, h2),
                        "endpoints_B20000": [l2, h2],
                        "status": "STABLE" if block["cell"] == cell_of(l2, h2) else "BOUNDARY"})
        elif triggered:
            with np.errstate(invalid="ignore", divide="ignore"):
                r2 = k2d().pooled_q([(x_log, [rec[(a, "deframed")] for a in arm_ids()])],
                                    ANCHOR_LAMBDA_K2B, B_BOOT_HIGH, MASTER_SEED)
                r1 = k2d().pooled_q([(x_log, [rec[(a, "intact")] for a in arm_ids()])],
                                    ANCHOR_LAMBDA_K2B, B_BOOT_HIGH, MASTER_SEED)
            dq2 = r2["q_boot"] - r1["q_boot"]
            l2, h2 = ci_of(dq2[np.isfinite(dq2)])
            row.update({"cell_B2000": block["cell"], "cell_B20000": cell_of(l2, h2),
                        "endpoints_B20000": [l2, h2],
                        "status": "STABLE" if block["cell"] == cell_of(l2, h2) else "BOUNDARY"})
        else:
            row["status"] = "NOT_TRIGGERED"
        rule13.append(row)

    # ---- mixed-recovery descriptives --------------------------------------
    mixed_desc = {
        "per_arm": [{k: e[k] for k in ("arm", "mixed_intact", "mixed_intact_ci",
                                       "mixed_deframed", "mixed_deframed_ci",
                                       "d_mixed", "d_mixed_ci", "d_mixed_cell")}
                    for e in per_arm],
        "arms_mixed_down": int(sum(1 for e in per_arm if e["d_mixed_cell"] == "DOWN")),
        "arms_mixed_up": int(sum(1 for e in per_arm if e["d_mixed_cell"] == "UP")),
        "gate": "NONE (registration: 'mixed recovery (descriptive)')",
    }

    # ---- POST-HOC descriptive (no gate, no lean input): the relative collapse
    post_hoc = {
        "gate": "NONE -- POST-HOC descriptive, computed after the lean was assigned; "
                "no branch, no gate and no lean consumes it (the K2b precedent)",
        "per_arm": [{
            "arm": e["arm"],
            "frame_variance_share_design": float(
                k2b().arm_shares(dict(zip(arm_ids(), [a[1] for a in arms()]))[e["arm"]],
                                 "zero")["common"]),
            "state_variance_share_design": float(
                k2b().arm_shares(dict(zip(arm_ids(), [a[1] for a in arms()]))[e["arm"]],
                                 "zero")["slow"]),
            "recovery_intact": e["recovery_intact"],
            "recovery_deframed": e["recovery_deframed"],
            "relative_collapse_b_only": e["d"] / e["recovery_intact"],
            "relative_collapse_mixed": e["d_mixed"] / e["mixed_intact"],
        } for e in per_arm],
        "note": "K2b's G4b already measured why the b-only target cannot survive the "
                "subtraction on the ESTIMATE side: the strict trait-only panel's field "
                "has max context norm 0.0006675856745354268 against the b-only panel's "
                "minimum 0.15214367930549447 (recovery -0.024495680267977205).  In this "
                "world family the b-only truth panel's only within-author occasion "
                "variation IS the frame, so the b-only field is a frame field modulated "
                "by the trait.  What the frame content scaffolds is a named charter under "
                "P-R3, not a claim of this leg.",
    }

    verdict = {
        "L-R1": "DEFRAMING_HELPS_THE_TRAIT_INSTRUMENT",
        "L-R2": "DEFRAMING_IS_HYGIENE_NOT_ENHANCEMENT",
        "L-R3": "DEFRAMING_HARMS_TRAIT_READING",
        "L-R4": "DEFRAMING_IS_ARM_DEPENDENT",
    }[lean]
    n_bound = sum(1 for r in rule13 if r["status"] == "BOUNDARY")
    slug = f"{lean}__{verdict}__nup{n_up}_ndown{n_down}__{pivot}"
    if n_bound:
        slug += f"__RULE13_BOUNDARY_{n_bound}"

    decision = {
        "leg": "M4-K-R1",
        "banner": BANNER,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "worlds_per_cell": n_worlds,
        "cells": len(arm_ids()) * len(VARIANTS),
        "n_authors_per_world": int(len(k2b().layout()["author_ids"])),
        "n_retained": int(cells[(arm_ids()[0], "intact")]["n_retained"].iloc[0]),
        "G2r_main": g2_main,
        "per_arm": per_arm,
        "n_up": n_up, "n_down": n_down,
        "n_flat": int(sum(1 for e in per_arm if e["d_cell"] == "FLAT")),
        "lean": lean, "lean_prior": PRIORS[lean],
        "enumeration": enumeration_table(len(arm_ids())),
        "routing": pivot,
        "parameter_story": param,
        "mixed_recovery": mixed_desc,
        "post_hoc_descriptive": post_hoc,
        "rule13": {"clauses": len(rule13), "n_triggered": int(sum(r["triggered"] for r in rule13)),
                   "n_boundary": n_bound, "rows": rule13},
        "verdict_slug": slug,
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2, default=str) + "\n",
                                       encoding="utf-8")
    pd.DataFrame(per_arm).to_csv(OUT / "per_arm.csv", index=False)
    write_manifest({"finalize": time.time() - t0})
    print(json.dumps({
        "stage": "finalize", "seconds": round(time.time() - t0, 3),
        "n_up": n_up, "n_down": n_down, "lean": lean, "routing": pivot,
        "verdict_slug": slug,
        "per_arm": [{k: e[k] for k in ("arm", "recovery_intact", "recovery_deframed",
                                       "d", "d_ci", "d_cell")} for e in per_arm],
        "delta_lambda": param["delta_lambda"], "delta_q": param["delta_q"],
        "rule13_boundary": n_bound,
    }, indent=2, default=str))


# ---------------------------------------------------------------------------

def write_manifest(stage_times: dict[str, float]) -> None:
    path = OUT / "manifest.json"
    prior = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    prior.setdefault("leg", "M4-K-R1")
    prior.setdefault("banner", BANNER)
    prior.setdefault("script", "scripts/run_suica_m4_kr1_deframing_repair.py")
    prior.setdefault("master_seed", MASTER_SEED)
    prior.setdefault("pilot_worlds", list(PILOT_WORLDS))
    prior.setdefault("variants", list(VARIANTS))
    prior.setdefault("arms", [list(a) for a in arms()])
    prior.setdefault("b_boot", B_BOOT)
    prior.setdefault("b_boot_high", B_BOOT_HIGH)
    prior.setdefault("norm_pool_authors_per_context", NORM_POOL_AUTHORS_PER_CONTEXT)
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
    parser.add_argument("--worlds", default=None, help="LO:HI world chunk for --stage arms")
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
