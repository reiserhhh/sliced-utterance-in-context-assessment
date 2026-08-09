#!/usr/bin/env python3
"""M4-K1b -- ownership of F2's composition effect: author-reading or frame-amplification?

Registered spec: docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md section "M4-K1b --
Ownership of the composition effect: author-reading or frame-amplification?"
(REGISTERED 2026-08-09, BEFORE RUN, commit 678b25a; P3's binding consequence).
Part 0 register-notes (operationalizations for everything the registration left
as an implementation choice, plus the standing-rule-9 instrument resolution) are
in reports/SUICA_M4_K1B_COMPOSITION_OWNERSHIP_REPORT.md Part 0, written BEFORE
any arm stage ran.

Machinery reuse (no reimplementation of existing constructions):
  * world generator      f2.generate_world_composed  (scripts/run_suica_m4_f2_composition.py:129-198)
  * occasion designs     f2.occasion_labels          (f2:96-118)
  * common-shock draw    f2.shock_vector             (f2:120-126)
  * layout               f2.build_layout_common      (f2:205-222)
  * deployed gauge path  f2.run_axis1_world          (f2:276-370)
  * paired t CI          f2._paired_ci               (f2:1008-1025)
  * R-abs reader         k1.build_abs_world / k1.cards_for_arm / k1.reader_metrics
                         (scripts/run_suica_m4_k1_issuer_theorems.py:164-186, 210-250)
  * author-strat boot    k1._author_stratified_bootstrap (k1:832-854)
  * 1x common shift      k1._generate_shifted        (k1:368-386)
  * response-level RMS   k1._author_deviation_rms    (k1:337-361)
Nothing in suica_core/ is touched (frozen operators are READ-ONLY).

Stages (foreground, chunked, resumable; artifacts under
results/m4_k1b_composition_ownership/):
  --stage part0    G0, G1b, G2b, G3b, G4b, G5 -> gates.json  (MUST run, and the
                   report's Part 0 MUST be written, before any arm stage)
  --stage arms_a   A0 (shared intact) + A2 (free intact), 32 worlds -> then G1
  --stage gate_g1  the replication gate on A0-A2 (STOP / VOID if it fails)
  --stage arms_b   A1, A3, A4 (+ the disclosed second reading A1', A3'), 32 worlds
  --stage sec      the secondary question (reader A vs A', 8 worlds, R-abs)
  --stage finalize lean adjudication + pivots -> decision.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import suica_core.v8_realtext_relation_field as v8  # noqa: E402
from suica_core.v8_context_relation_field import _orthonormal_loadings  # noqa: E402

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"

# --- registered constants (docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md, M4-K1b) -----
MASTER_SEED = 20260811
WORLDS = 32
KAPPA = 1.0
DRAWS = 20
BOOT_DRAWS = 2000
SEC_WORLDS = 8                        # "first 8 of the 32 worlds"
EQUIV_MARGIN = 0.006540815826681557   # L-c margin (K1-L5's m)
LD_MARGIN = 0.0251                    # L-d margin (half K1's forged effect)
G3B_BAR = 0.0130816                   # required MDE bar (50% share of F2's effect)
G3B_ASPIRATIONAL = 0.0065408          # aspirational resolution (25% share)
SHARE_LA = 0.25                       # L-a: S_hat >= 0.25
SHARE_P2B = 0.75                      # P2b: S_hat >= 0.75
RATIO_LE = 0.5                        # L-e: R_est / R_or >= 0.5
SIGN_CLEAN = 26                       # per-world signs: clean >= 26/32
SIGN_QUALIFIED = 21                   # qualified >= 21/32

# Anchors (values re-derived bit-exactly by G1b before any arm).
F2_CI = (0.01953599084902978, 0.032790535764422674)
F2_PAIRED_MEAN = 0.026163263306726227
K1_L5_1X = 0.09254304863282958        # registration quotes +0.092543049
K1_L2 = 0.09695431472081219

# --- Part-0 operationalizations (see report Part 0; fixed BEFORE any arm) -----
A4_AUTHORS_PER_CONTEXT = 32   # "32 disjoint authors" -- per (context) occasion grid
SEC_NORM_POOL = 1024          # two disjoint 512-author sub-pools (reader A')
SEC_EST = 8                   # est8
PILOT_WORLDS = (9101, 9102, 9103, 9104)   # G3b power pilot; never adjudicated
G2B_WORLDS = (9301, 9302)                 # G2b surgical verification
G4B_WORLDS = (9201, 9202, 9203)           # G4b channel liveness (as registered)
G4B_SUPP_WORLDS = (9204, 9205, 9206, 9207, 9208)   # G4b power remedy -> K1's own n=8
BOOT_SEEDS = {
    "delta0": 20260811001,
    "delta1": 20260811002,
    "gap": 20260811003,
    "share": 20260811004,
    "spec": 20260811005,
    "removal": 20260811006,
    "second_reading": 20260811007,
    "ld_A": 20260811008,
    "ld_Aprime": 20260811009,
}

OUT = ROOT / "results" / "m4_k1b_composition_ownership"
F2_OUT = ROOT / "results" / "m4_f2_composition"
K1_OUT = ROOT / "results" / "m4_k1_issuer"
F1_OUT = ROOT / "results" / "m4_f1_panel_sizing"
F1_CALIBRATION = F1_OUT / "calibration_record.json"
REF_PATH = F1_OUT / "realtext_panel_reference.json"


def _load_script(name: str) -> Any:
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_F2 = None
_K1 = None


def f2() -> Any:
    global _F2
    if _F2 is None:
        _F2 = _load_script("run_suica_m4_f2_composition.py")
    return _F2


def k1() -> Any:
    global _K1
    if _K1 is None:
        _K1 = _load_script("run_suica_m4_k1_issuer_theorems.py")
    return _K1


def knobs_and_tag() -> tuple[dict[str, Any], str]:
    record = json.loads(F1_CALIBRATION.read_text(encoding="utf-8"))
    if record["status"] != "CALIBRATED":
        raise AssertionError("M4-F1 calibration_record.json is not CALIBRATED.")
    knobs = record["selected"]["knobs"]
    return knobs, f2().f1().knob_tag(knobs)


def world_seed_for(group: str, world: int, knob_tag: str) -> int:
    """The same recipe f2.run_axis1_world uses internally (f2:288-291), so a
    seed computed here equals the one the gauge run will use for that task."""
    return v8.stable_bucket(
        f"{MASTER_SEED}-{group}-w{world}-{knob_tag}",
        salt="m4k1b-world",
        modulus=2**63 - 1,
    )


# ===========================================================================
# Channel extraction -- the generator's three additive terms, recomputed
# EXACTLY (line-for-line mirror of f2.generate_world_composed:151-197, using
# f2's own _orthonormal_loadings / occasion_labels / shock_vector). This is not
# a reimplementation of the world: every arm's events still come out of f2's
# own generator; these terms exist only so a named channel can be SUBTRACTED.
# G2b verifies the reconstruction residual exactly.
# ===========================================================================

def channels(
    counts: list[int],
    contexts: list[str],
    knobs: dict[str, Any],
    kappa: float,
    occasion_mode: str,
    world_seed: int,
) -> dict[str, Any]:
    module = f2()
    rng = np.random.default_rng(world_seed)                       # f2:151
    k = int(knobs["k"])
    rho = float(knobs["rho"])
    w_mu, w_x, w_e = float(knobs["w_mu"]), float(knobs["w_x"]), float(knobs["w_e"])
    phi_lo, phi_hi = float(knobs["phi_lo"]), float(knobs["phi_hi"])
    n = len(counts)
    t_max = max(counts)
    g = np.linspace(0.85, 0.55, k)                                # f2:164
    a = math.sqrt(2.0 / float(np.sum(g**2)))                      # f2:165
    sigma_iso = math.sqrt(2.0 / 64.0)                             # f2:166
    loadings = _orthonormal_loadings(rng, 64, k)                  # f2:167
    z = rng.normal(size=(n, k))                                   # f2:168
    zeta = rng.normal(size=(n, k))                                # f2:169
    logits = rho * z + math.sqrt(max(0.0, 1.0 - rho**2)) * zeta   # f2:170
    phi = phi_lo + (phi_hi - phi_lo) / (1.0 + np.exp(-logits))    # f2:171
    x = np.empty((n, t_max, k), dtype=float)                      # f2:172
    x[:, 0] = rng.normal(size=(n, k))                             # f2:173
    innovation_scale = np.sqrt(1.0 - phi**2)                      # f2:174
    for t in range(1, t_max):                                     # f2:175-176
        x[:, t] = phi * x[:, t - 1] + innovation_scale * rng.normal(size=(n, k))
    noise = rng.normal(size=(n, t_max, 64))                       # f2:177
    mean_part = math.sqrt(w_mu) * a * ((z * g) @ loadings.T)      # f2:178

    labels = module.occasion_labels(counts, occasion_mode)        # f2:180
    shock_x = np.zeros_like(x)                                    # f2:181
    cache: dict[tuple[str, int], np.ndarray] = {}
    kappa_f = float(kappa)
    for i in range(n):                                            # f2:184-193
        context = contexts[i]
        for t in range(counts[i]):
            occ = int(labels[i][t])
            key = (context, occ)
            vector = cache.get(key)
            if vector is None:
                vector = module.shock_vector(world_seed, context, occ, k)
                cache[key] = vector
            shock_x[i, t] = vector
    blended_x = math.sqrt(max(0.0, 1.0 - kappa_f)) * x + math.sqrt(kappa_f) * shock_x  # f2:195
    state_part = math.sqrt(w_x) * a * ((blended_x * g) @ loadings.T)   # f2:196
    noise_part = math.sqrt(w_e) * sigma_iso * noise                    # f2:197 (3rd term)
    return {
        "mean_part": mean_part,          # (n, 64)      author channel  (w_mu)
        "state_part": state_part,        # (n, t_max, 64) occasion channel (w_x);
                                         #   at kappa=1 this IS the common channel
        "noise_part": noise_part,        # (n, t_max, 64)
        "labels": labels,
        "loadings": loadings,
        "g": g,
        "a": a,
        "cache": cache,
    }


def common_vector(
    knobs: dict[str, Any], loadings: np.ndarray, g: np.ndarray, a: float,
    world_seed: int, context: str, occ: int
) -> np.ndarray:
    """C(c,o) for a single (context, occasion) -- the kappa=1 common channel."""
    k = int(knobs["k"])
    s = f2().shock_vector(world_seed, context, occ, k)
    return math.sqrt(float(knobs["w_x"])) * a * ((s * g) @ loadings.T)


# ===========================================================================
# Arm generators: patches installed over f2.generate_world_composed inside the
# worker, exactly as k1._rel_world did for the shift arms (k1:392-409).
# ===========================================================================

_ORIG_GENERATE: Any = None
_ARM_STATE: dict[str, Any] = {}


def _gen_remove(counts, contexts, knobs, kappa, occasion_mode, world_seed):  # noqa: ANN001
    """A1 / A3 (remove='common') and the disclosed second reading A1' / A3'
    (remove='authormean'): exact pre-map subtraction of a named channel."""
    vectors = _ORIG_GENERATE(counts, contexts, knobs, kappa, occasion_mode, world_seed)
    ch = channels(counts, contexts, knobs, kappa, occasion_mode, world_seed)
    which = _ARM_STATE["remove"]
    if which == "common":
        term = ch["state_part"]
        return [vec - term[i][: len(vec)] for i, vec in enumerate(vectors)]
    if which == "authormean":
        mean_part = ch["mean_part"]
        return [vec - mean_part[i][None, :] for i, vec in enumerate(vectors)]
    raise ValueError(which)


def _gen_estimated(counts, contexts, knobs, kappa, occasion_mode, world_seed):  # noqa: ANN001
    """A4: subtract an ESTIMATED per-(context, occasion) norm, built from
    A4_AUTHORS_PER_CONTEXT disjoint authors observed on the same occasions with
    the same common channel."""
    module = f2()
    vectors = _ORIG_GENERATE(counts, contexts, knobs, kappa, occasion_mode, world_seed)
    mu_hat = estimated_occasion_norm(counts, contexts, knobs, kappa, world_seed)
    labels = module.occasion_labels(counts, occasion_mode)
    out = []
    for i, vec in enumerate(vectors):
        sub = np.stack([mu_hat[(contexts[i], int(labels[i][t]))] for t in range(len(vec))])
        out.append(vec - sub)
    return out


def estimated_occasion_norm(
    counts: list[int], contexts: list[str], knobs: dict[str, Any],
    kappa: float, world_seed: int
) -> dict[tuple[str, int], np.ndarray]:
    module = f2()
    ctxs = sorted(set(contexts))
    t_max = max(counts)
    n_ctx = len(ctxs)
    ncounts = [t_max] * (A4_AUTHORS_PER_CONTEXT * n_ctx)
    ncontexts = [c for c in ctxs for _ in range(A4_AUTHORS_PER_CONTEXT)]
    norm_seed = v8.stable_bucket(
        f"{world_seed}-normpool", salt="m4k1b-normpool", modulus=2**63 - 1
    )
    nch = channels(ncounts, ncontexts, knobs, kappa, "shared", norm_seed)
    # the pool's own idiosyncratic content (author channel + noise), with THEIR
    # occasion channel dropped and the PANEL's common channel put in its place
    idio = nch["mean_part"][:, None, :] + nch["noise_part"]
    rng_p = np.random.default_rng(world_seed)
    loadings_p = _orthonormal_loadings(rng_p, 64, int(knobs["k"]))
    g = nch["g"]
    a = nch["a"]
    mu_hat: dict[tuple[str, int], np.ndarray] = {}
    for ci, ctx in enumerate(ctxs):
        lo = ci * A4_AUTHORS_PER_CONTEXT
        hi = lo + A4_AUTHORS_PER_CONTEXT
        block = idio[lo:hi]                       # (32, t_max, 64)
        for occ in range(t_max):
            c_vec = common_vector(knobs, loadings_p, g, a, world_seed, ctx, occ)
            mu_hat[(ctx, occ)] = block[:, occ, :].mean(axis=0) + c_vec
    return mu_hat


def _gen_shift(counts, contexts, knobs, kappa, occasion_mode, world_seed):  # noqa: ANN001
    """G4b: K1's own 1x pre-map common shift (k1:368-386), verbatim."""
    module = k1()
    module._ORIG_GENERATE = _ORIG_GENERATE
    module._ORIG_OCCASION_LABELS_REL = f2().occasion_labels
    module._SHIFT_STATE.clear()
    module._SHIFT_STATE["scale"] = float(_ARM_STATE.get("shift_scale", 1.0))
    out = module._generate_shifted(
        counts, contexts, knobs, kappa, occasion_mode, world_seed
    )
    _ARM_STATE["calibration_rms"] = float(
        module._SHIFT_STATE.get("calibration_rms", float("nan"))
    )
    _ARM_STATE["shift_sigma"] = float(module._SHIFT_STATE.get("shift_sigma", 0.0))
    return out


ARM_SPEC: dict[str, dict[str, Any]] = {
    # arm    design    generator patch        arm_state
    "A0": {"design": "shared", "patch": None, "state": {}},
    "A2": {"design": "free", "patch": None, "state": {}},
    "A1": {"design": "shared", "patch": "remove", "state": {"remove": "common"}},
    "A3": {"design": "free", "patch": "remove", "state": {"remove": "common"}},
    "A4": {"design": "shared", "patch": "estimated", "state": {}},
    "A1p": {"design": "shared", "patch": "remove", "state": {"remove": "authormean"}},
    "A3p": {"design": "free", "patch": "remove", "state": {"remove": "authormean"}},
    "G4b0": {"design": "shared", "patch": None, "state": {}},
    "G4b1": {"design": "shared", "patch": "shift", "state": {"shift_scale": 1.0}},
}
PATCHES: dict[str, Callable[..., Any]] = {
    "remove": _gen_remove,
    "estimated": _gen_estimated,
    "shift": _gen_shift,
}


def arm_task(arm: str, world: int, knobs: dict[str, Any], knob_tag: str,
             group: str) -> dict[str, Any]:
    spec = ARM_SPEC[arm]
    return {
        "cell": f"{group}_{arm}",
        "arm": arm,
        "world": world,
        "seed_group": group,
        "corpus_tag": "m4k1b",
        "world_salt": "m4k1b-world",
        "budget_label": "k1b.0",
        "layout": "common",
        "kappa": KAPPA,
        "occasion_mode": spec["design"],
        "knobs": knobs,
        "knob_tag": knob_tag,
        "draws": DRAWS,
        "ref_path": str(REF_PATH),
        "arm_state": spec["state"],
        "patch": spec["patch"],
    }


def _arm_world(task: dict[str, Any]) -> dict[str, Any]:
    global _ORIG_GENERATE
    module = f2()
    module.MASTER_SEED = MASTER_SEED
    _ORIG_GENERATE = module.generate_world_composed
    _ARM_STATE.clear()
    _ARM_STATE.update(task.get("arm_state", {}))
    patch = task.get("patch")
    if patch is not None:
        module.generate_world_composed = PATCHES[patch]
    try:
        row = module.run_axis1_world(task)
    finally:
        module.generate_world_composed = _ORIG_GENERATE
    row["arm"] = task["arm"]
    row["group"] = task["seed_group"]
    row["calibration_rms"] = float(_ARM_STATE.get("calibration_rms", float("nan")))
    row["shift_sigma"] = float(_ARM_STATE.get("shift_sigma", 0.0))
    row.pop("draw_values", None)
    return row


def run_arms(arms: tuple[str, ...], worlds: tuple[int, ...], group: str,
             workers: int, label: str) -> pd.DataFrame:
    knobs, knob_tag = knobs_and_tag()
    tasks = [arm_task(a, w, knobs, knob_tag, group) for a in arms for w in worlds]
    started = time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(_arm_world, tasks))
    print(f"[{label}] {len(rows)} gauge runs in {time.time() - started:.0f}s", flush=True)
    return pd.DataFrame(rows)


# ===========================================================================
# Part 0 gates.
# ===========================================================================

def gate_g0(knobs: dict[str, Any], knob_tag: str) -> dict[str, Any]:
    module = f2()
    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    aid, ctx, spl, common, raw = module.build_layout_common(reference)
    meta = pd.DataFrame(
        {"author_id": aid, "context": ctx, "split": spl, "event_count": common}
    )
    spec = module.f1().load_spec()
    e1 = module.f1().e1()
    eval_mask = meta["split"].isin(["D1", "D2"]).to_numpy()
    resolved = e1.resolved_contexts(meta.loc[eval_mask], spec.minimum_context_authors)
    retained = np.flatnonzero(
        eval_mask
        & meta["context"].astype(str).isin(resolved).to_numpy()
        & (meta["event_count"].to_numpy() >= module.MIN_RETAINED_EVENTS)
    )
    hist = {int(k): int(v) for k, v in sorted(pd.Series(common).value_counts().items())}
    k1_gates = json.loads((K1_OUT / "gates.json").read_text(encoding="utf-8"))["G0"]
    # fresh-seed structural check on world 0 (generation shapes only; no gauge)
    seed0 = world_seed_for("main", 0, knob_tag)
    vec0 = module.generate_world_composed(common, ctx, knobs, KAPPA, "shared", seed0)
    shapes_ok = all(
        v.shape == (common[i], 64) for i, v in enumerate(vec0)
    )
    same = {
        "authors": int(len(aid)) == k1_gates["f2_authors_per_world"],
        "events": int(sum(common)) == k1_gates["f2_events_allocated_total"],
        "multiset": hist == {int(k): v for k, v in k1_gates["f2_events_per_author_multiset"].items()},
        "contexts": sorted(set(ctx)) == k1_gates["f2_contexts"],
        "retained": int(len(retained)) == k1_gates["f2_n_retained_by_deployed_gauge"],
    }
    return {
        "gate": "G0",
        "description": "dims pinned to K1's; verified unchanged at the fresh seeds' first world",
        "authors_per_world": int(len(aid)),
        "events_allocated_total": int(sum(common)),
        "events_raw_total": int(sum(raw)),
        "events_per_author_multiset": hist,
        "contexts": sorted(set(ctx)),
        "n_retained_by_deployed_gauge": int(len(retained)),
        "min_retained_events_floor": int(module.MIN_RETAINED_EVENTS),
        "k1_pinned": {
            "authors": k1_gates["f2_authors_per_world"],
            "events": k1_gates["f2_events_allocated_total"],
            "multiset": k1_gates["f2_events_per_author_multiset"],
            "contexts": k1_gates["f2_contexts"],
            "retained": k1_gates["f2_n_retained_by_deployed_gauge"],
        },
        "matches_k1": same,
        "world0_seed": int(seed0),
        "world0_shapes_ok": bool(shapes_ok),
        "knobs": knobs,
        "knob_tag": knob_tag,
        "grain": "per-world paired design contrasts; 32 worlds as the unit; authors within world",
        "pass": bool(all(same.values()) and shapes_ok),
    }


def gate_g1b() -> dict[str, Any]:
    """Bit-exact re-derivation of K1's L5 1x and L2 values from K1 artifacts."""
    module = f2()
    decision = json.loads((K1_OUT / "decision.json").read_text(encoding="utf-8"))
    rel = pd.read_csv(K1_OUT / "rel_cells.csv")
    base = rel[(rel["occasion_mode"] == "shared") & (rel["shift_scale"] == 0.0)].sort_values("world")
    arm = rel[(rel["occasion_mode"] == "shared") & (rel["shift_scale"] == 1.0)].sort_values("world")
    deltas = arm["agreement_mean"].to_numpy() - base["agreement_mean"].to_numpy()
    l5 = module._paired_ci(deltas)
    l5_ref = decision["adjudication"]["L5"]["shared_1x"]
    store = np.load(K1_OUT / "abs_probe_correct.npz")
    per_world = [
        store[f"free|{w}|oracle|B"].astype(float) - store[f"free|{w}|est8|B"].astype(float)
        for w in range(8)
    ]
    l2_mean = float(np.array([float(v.mean()) for v in per_world]).mean())
    l2_ref = decision["adjudication"]["L2"]["B"]["pooled_mean"]
    l5_exact = {k: bool(l5[k] == l5_ref[k]) for k in ("mean", "sd", "se", "t_stat",
                                                      "ci95_low", "ci95_high")}
    return {
        "gate": "G1b",
        "description": "K1 anchors re-derived bit-exactly from results/m4_k1_issuer/ artifacts",
        "l5_1x_rederived": l5,
        "l5_1x_persisted": {k: l5_ref[k] for k in ("mean", "sd", "se", "t_stat",
                                                   "ci95_low", "ci95_high")},
        "l5_1x_bit_exact": l5_exact,
        "l5_1x_matches_registration_digits": bool(round(l5["mean"], 9) == 0.092543049),
        "l2_rederived": l2_mean,
        "l2_persisted": l2_ref,
        "l2_bit_exact": bool(l2_mean == l2_ref),
        "l2_matches_registration": bool(l2_mean == K1_L2),
        "f2_ci_cited": list(F2_CI),
        "pass": bool(all(l5_exact.values()) and l2_mean == l2_ref),
    }


def gate_g2b(knobs: dict[str, Any], knob_tag: str) -> dict[str, Any]:
    """Surgical verification, 2 pilot worlds: the three-channel reconstruction is
    exact; subtraction == twin generation with the common channel zeroed; the
    author+noise channels are bit-identical across designs; the removed channel
    is exactly the one common to all authors sharing a (context, occasion)."""
    started = time.time()
    module = f2()
    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    aid, ctx, _spl, counts, _raw = module.build_layout_common(reference)
    per_world = []
    orig_shock = module.shock_vector
    for w in G2B_WORLDS:
        seed = world_seed_for("g2b", w, knob_tag)
        entry: dict[str, Any] = {"world": int(w), "world_seed": int(seed)}
        twins: dict[str, list[np.ndarray]] = {}
        for design in ("shared", "free"):
            resp = module.generate_world_composed(counts, ctx, knobs, KAPPA, design, seed)
            ch = channels(counts, ctx, knobs, KAPPA, design, seed)
            recon_res = max(
                float(
                    np.abs(
                        vec
                        - (
                            ch["mean_part"][i][None, :]
                            + ch["state_part"][i][: len(vec)]
                            + ch["noise_part"][i][: len(vec)]
                        )
                    ).max()
                )
                for i, vec in enumerate(resp)
            )
            subtracted = [
                vec - ch["state_part"][i][: len(vec)] for i, vec in enumerate(resp)
            ]
            module.shock_vector = lambda *_a, **_kw: np.zeros(int(knobs["k"]))
            try:
                twin = module.generate_world_composed(
                    counts, ctx, knobs, KAPPA, design, seed
                )
            finally:
                module.shock_vector = orig_shock
            twins[design] = twin
            twin_res = max(
                float(np.abs(subtracted[i] - twin[i]).max()) for i in range(len(twin))
            )
            # the removed channel is exactly common within (context, occasion)
            spread = 0.0
            if design == "shared":
                groups: dict[tuple[str, int], list[np.ndarray]] = {}
                for i in range(len(counts)):
                    for t in range(counts[i]):
                        groups.setdefault((ctx[i], t), []).append(ch["state_part"][i, t])
                spread = max(
                    float(np.abs(np.stack(v) - np.stack(v)[0]).max())
                    for v in groups.values()
                    if len(v) > 1
                )
            entry[design] = {
                "reconstruction_residual_max": recon_res,
                "subtraction_vs_twin_max": twin_res,
                "common_channel_within_occasion_spread_max": spread,
                "additive_at_1e-12": bool(twin_res <= 1e-12 and recon_res <= 1e-12),
            }
        entry["twin_shared_vs_twin_free_max"] = max(
            float(np.abs(twins["shared"][i] - twins["free"][i]).max())
            for i in range(len(counts))
        )
        entry["author_and_noise_channels_bit_identical"] = bool(
            entry["twin_shared_vs_twin_free_max"] == 0.0
        )
        per_world.append(entry)
    additive = all(
        e[d]["additive_at_1e-12"] for e in per_world for d in ("shared", "free")
    )
    return {
        "gate": "G2b",
        "description": (
            "surgical verification of the exact pre-map subtraction; decides the "
            "registered primary/fallback path"
        ),
        "worlds": list(G2B_WORLDS),
        "per_world": per_world,
        "additivity_holds_at_1e-12": bool(additive),
        "path_taken": "PRIMARY_EXACT_SUBTRACTION" if additive else "FALLBACK_TWIN_GENERATION",
        "designed_identity_note": (
            "occasion_mode enters f2.generate_world_composed ONLY through "
            "occasion_labels -> shock_x (f2:180-196); at kappa=1 blended_x == shock_x "
            "exactly, so removing the common channel makes the shared and free panels "
            "bit-identical -- Delta1 = A1 - A3 is therefore identically 0 by "
            "construction (verified here as twin_shared_vs_twin_free_max == 0.0)"
        ),
        "seconds": float(time.time() - started),
        "pass": bool(additive),
    }


def gate_g3b(knobs: dict[str, Any], knob_tag: str, workers: int) -> dict[str, Any]:
    """Power: 4-world pilot, sd of per-world (Delta0 - Delta1); MDE at n=32."""
    started = time.time()
    frame = run_arms(("A0", "A2", "A1", "A3"), PILOT_WORLDS, "pilot", workers, "G3b pilot")
    frame.to_csv(OUT / "pilot_cells.csv", index=False)
    piv = frame.pivot(index="world", columns="arm", values="agreement_mean")
    d0 = (piv["A0"] - piv["A2"]).to_numpy()
    d1 = (piv["A1"] - piv["A3"]).to_numpy()
    gap = d0 - d1
    sd = float(np.std(gap, ddof=1))
    t_mult = float(stats.t.ppf(0.975, df=WORLDS - 1) + stats.t.ppf(0.80, df=WORLDS - 1))
    mde = float(t_mult * sd / math.sqrt(WORLDS))
    return {
        "gate": "G3b",
        "description": "MDE(80%, alpha=.05, paired t, n=32) for (Delta0 - Delta1)",
        "pilot_worlds": list(PILOT_WORLDS),
        "pilot_note": "reserved seeds; excluded from every adjudication",
        "pilot_delta0": [float(v) for v in d0],
        "pilot_delta1": [float(v) for v in d1],
        "pilot_gap": [float(v) for v in gap],
        "pilot_gap_sd": sd,
        "t_multiplier_80pct_power": t_mult,
        "mde_n32": mde,
        "bar": G3B_BAR,
        "aspirational_resolution": G3B_ASPIRATIONAL,
        "meets_bar": bool(mde <= G3B_BAR),
        "meets_aspirational": bool(mde <= G3B_ASPIRATIONAL),
        "escalation": "none" if mde <= G3B_BAR else "escalate 32->64 worlds once",
        "seconds": float(time.time() - started),
        "pass": bool(mde <= G3B_BAR),
    }


def gate_g4b(knobs: dict[str, Any], knob_tag: str, workers: int) -> dict[str, Any]:
    """Channel liveness: the 1x amplification reproduces on 3 fresh worlds, and
    the native common channel is scale-comparable to the author deviation."""
    started = time.time()
    module = f2()
    frame = run_arms(("G4b0", "G4b1"), G4B_WORLDS, "g4b", workers, "G4b liveness")
    frame.to_csv(OUT / "g4b_cells.csv", index=False)
    piv = frame.pivot(index="world", columns="arm", values="agreement_mean")
    deltas = (piv["G4b1"] - piv["G4b0"]).to_numpy()
    ci = module._paired_ci(deltas)
    # scale comparability, computed on a fresh shared world
    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    aid, ctx, _spl, counts, _raw = module.build_layout_common(reference)
    seed = world_seed_for("g4b", G4B_WORLDS[0], knob_tag)
    ch = channels(counts, ctx, knobs, KAPPA, "shared", seed)
    base = module.generate_world_composed(counts, ctx, knobs, KAPPA, "shared", seed)
    labels = module.occasion_labels(counts, "shared")
    author_dev_rms = float(k1()._author_deviation_rms(base, labels, ctx))
    distinct = np.stack([v for v in ch["cache"].values()])
    c_distinct = math.sqrt(float(knobs["w_x"])) * ch["a"] * ((distinct * ch["g"]) @ ch["loadings"].T)
    common_rms_distinct = float(np.sqrt(np.mean(c_distinct**2)))
    ev = np.concatenate([ch["state_part"][i, : counts[i]].ravel() for i in range(len(counts))])
    common_rms_events = float(np.sqrt(np.mean(ev**2)))
    ratio = common_rms_distinct / author_dev_rms
    return {
        "gate": "G4b",
        "description": "1x amplification reproduces on fresh seeds; native common channel is scale-comparable",
        "worlds": list(G4B_WORLDS),
        "per_world_delta": [float(v) for v in deltas],
        "paired": ci,
        "sign_positive": bool(ci["mean"] > 0),
        "ci_excludes_zero": bool(ci["ci95_low"] > 0 or ci["ci95_high"] < 0),
        "k1_l5_1x_reference": K1_L5_1X,
        "shift_sigma": float(frame[frame["arm"] == "G4b1"]["shift_sigma"].mean()),
        "author_deviation_rms_response_level": author_dev_rms,
        "native_common_channel_rms_distinct_occasions": common_rms_distinct,
        "native_common_channel_rms_over_events": common_rms_events,
        "ratio_common_to_author_deviation": ratio,
        "scale_comparable_0p5_to_2": bool(0.5 <= ratio <= 2.0),
        "seconds": float(time.time() - started),
        "pass": bool(
            ci["mean"] > 0
            and (ci["ci95_low"] > 0 or ci["ci95_high"] < 0)
            and 0.5 <= ratio <= 2.0
        ),
    }


def gate_g4b_supplementary(workers: int) -> dict[str, Any]:
    """Power remedy for G4b's CI clause, declared in Part 0 BEFORE any arm.

    The registered clause ("sign + CI excluding 0" on 3 fresh worlds) is
    UNSATISFIABLE at the anchor's own effect size: with K1's persisted per-world
    sd 0.041580915483140586, the n=3 paired-t half-width is 0.10329... > the
    anchor mean 0.09254304863282958, so even an exact reproduction of K1's
    result would fail it. n = 4 is the smallest n at which the clause becomes
    satisfiable at the anchor. The remedy is therefore to read the SAME gate at
    the anchor's own n = 8 (K1's L5 design), not to add worlds until it passes:
    the target n is fixed by the anchor, computed before the extra worlds ran.
    Both readings are reported; the registered 3-world reading stands as the
    registered gate.
    """
    started = time.time()
    module = f2()
    k1_l5 = json.loads((K1_OUT / "decision.json").read_text(encoding="utf-8"))[
        "adjudication"]["L5"]["shared_1x"]
    required_n = None
    for n in range(3, 33):
        hw = float(stats.t.ppf(0.975, n - 1)) * k1_l5["sd"] / math.sqrt(n)
        if hw < k1_l5["mean"]:
            required_n = n
            break
    frame_old = pd.read_csv(OUT / "g4b_cells.csv")
    frame_new = run_arms(("G4b0", "G4b1"), G4B_SUPP_WORLDS, "g4b", workers, "G4b supp")
    frame = pd.concat([frame_old, frame_new], ignore_index=True)
    frame.to_csv(OUT / "g4b_cells.csv", index=False)
    piv = frame.pivot(index="world", columns="arm", values="agreement_mean")
    deltas = (piv["G4b1"] - piv["G4b0"]).to_numpy()
    ci = module._paired_ci(deltas)
    return {
        "gate": "G4b_supplementary",
        "description": (
            "the registered G4b liveness read at the anchor's own n=8 (power remedy; "
            "the n=3 clause is unsatisfiable at the anchor effect size)"
        ),
        "worlds": list(G4B_WORLDS) + list(G4B_SUPP_WORLDS),
        "k1_anchor_sd": k1_l5["sd"],
        "k1_anchor_mean": k1_l5["mean"],
        "n3_halfwidth_at_anchor_sd": float(
            float(stats.t.ppf(0.975, 2)) * k1_l5["sd"] / math.sqrt(3)
        ),
        "smallest_satisfiable_n_at_anchor": required_n,
        "per_world_delta": [float(v) for v in deltas],
        "paired": ci,
        "signs_positive": int(np.sum(deltas > 0)),
        "ci_excludes_zero_positive": bool(ci["ci95_low"] > 0),
        "seconds": float(time.time() - started),
        "pass": bool(ci["ci95_low"] > 0),
    }


def run_part0(workers: int) -> dict[str, Any]:
    started = time.time()
    knobs, knob_tag = knobs_and_tag()
    OUT.mkdir(parents=True, exist_ok=True)
    g0 = gate_g0(knobs, knob_tag)
    g1b = gate_g1b()
    g2b = gate_g2b(knobs, knob_tag)
    g3b = gate_g3b(knobs, knob_tag, workers)
    g4b = gate_g4b(knobs, knob_tag, workers)
    g5 = {
        "gate": "G5",
        "description": "hygiene: manifest, per-stage seeds, wall-times, foreground chunks",
        "master_seed": MASTER_SEED,
        "stage_seed_recipe": (
            "v8.stable_bucket(f'{MASTER_SEED}-{group}-w{world}-{knob_tag}', "
            "salt='m4k1b-world', modulus=2**63-1)"
        ),
        "groups": ["main", "pilot", "g2b", "g4b", "abs"],
        "background_jobs": 0,
        "monitors": 0,
        "pass": True,
    }
    gates = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "leg": "M4-K1b",
        "master_seed": MASTER_SEED,
        "worlds": WORLDS,
        "knobs": knobs,
        "knob_tag": knob_tag,
        "G0": g0, "G1b": g1b, "G2b": g2b, "G3b": g3b, "G4b": g4b, "G5": g5,
        "part0_all_pass": bool(
            g0["pass"] and g1b["pass"] and g2b["pass"] and g3b["pass"] and g4b["pass"]
        ),
        "seconds": float(time.time() - started),
    }
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v.get("pass") for k, v in gates.items() if isinstance(v, dict)}, indent=2))
    print(f"G2b path={g2b['path_taken']} twin_shared_vs_free={g2b['per_world'][0]['twin_shared_vs_twin_free_max']}")
    print(f"G3b mde={g3b['mde_n32']:.8g} bar={G3B_BAR} pass={g3b['pass']}")
    print(f"G4b delta={g4b['paired']['mean']:.8g} CI=({g4b['paired']['ci95_low']:.8g},"
          f"{g4b['paired']['ci95_high']:.8g}) ratio={g4b['ratio_common_to_author_deviation']:.6g}")
    return gates


# ===========================================================================
# Gate G1 -- the replication gate (evaluated on A0/A2 before anything else).
# ===========================================================================

def _paired_world_bootstrap(values: dict[str, np.ndarray], statistic: Callable[[dict[str, np.ndarray]], float],
                            seed: int) -> dict[str, Any]:
    keys = list(values)
    n = len(values[keys[0]])
    rng = np.random.default_rng(seed)
    point = float(statistic(values))
    draws = np.empty(BOOT_DRAWS)
    for b in range(BOOT_DRAWS):
        idx = rng.integers(0, n, size=n)
        draws[b] = statistic({k: values[k][idx] for k in keys})
    lo, hi = float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))
    return {
        "point": point,
        "boot_draws": BOOT_DRAWS,
        "ci95_low": lo,
        "ci95_high": hi,
        "excludes_zero": bool(lo > 0.0 or hi < 0.0),
        "excludes_zero_positive": bool(lo > 0.0),
        "n_worlds": int(n),
    }


def _contrast_summary(diffs: np.ndarray, seed: int, name: str) -> dict[str, Any]:
    module = f2()
    boot = _paired_world_bootstrap({"d": diffs}, lambda v: float(v["d"].mean()), seed)
    positive = int(np.sum(diffs > 0))
    negative = int(np.sum(diffs < 0))
    band = (
        "clean" if max(positive, negative) >= SIGN_CLEAN
        else ("qualified" if max(positive, negative) >= SIGN_QUALIFIED else "fail")
    )
    return {
        "name": name,
        "pooled_mean": float(diffs.mean()),
        "bootstrap": boot,
        "paired_t": module._paired_ci(diffs),
        "per_world": [float(v) for v in diffs],
        "signs_positive": positive,
        "signs_negative": negative,
        "sign_band": band,
        "sign_rule": f"clean >= {SIGN_CLEAN}/32, qualified >= {SIGN_QUALIFIED}/32, else fail",
    }


def _load_main() -> pd.DataFrame:
    frames = [pd.read_csv(OUT / f) for f in ("arms_a.csv", "arms_b.csv") if (OUT / f).exists()]
    return pd.concat(frames, ignore_index=True)


def gate_g1() -> dict[str, Any]:
    frame = pd.read_csv(OUT / "arms_a.csv")
    piv = frame.pivot(index="world", columns="arm", values="agreement_mean")
    d0 = (piv["A0"] - piv["A2"]).to_numpy()
    summary = _contrast_summary(d0, BOOT_SEEDS["delta0"], "Delta0 = A0 - A2")
    lo, hi = summary["bootstrap"]["ci95_low"], summary["bootstrap"]["ci95_high"]
    overlap_boot = bool(lo <= F2_CI[1] and hi >= F2_CI[0])
    tlo, thi = summary["paired_t"]["ci95_low"], summary["paired_t"]["ci95_high"]
    overlap_t = bool(tlo <= F2_CI[1] and thi >= F2_CI[0])
    gate = {
        "gate": "G1",
        "description": "replication gate: Delta0 pooled CI must OVERLAP F2's CI",
        "f2_ci": list(F2_CI),
        "f2_paired_mean": F2_PAIRED_MEAN,
        "delta0": summary,
        "a0_mean": float(piv["A0"].mean()),
        "a2_mean": float(piv["A2"].mean()),
        "overlap_bootstrap_ci": overlap_boot,
        "overlap_paired_t_ci": overlap_t,
        "readings_agree": bool(overlap_boot == overlap_t),
        "decision_rule": (
            "verdict taken on the registered bootstrap CI; the paired-t CI is reported "
            "as a second reading and any disagreement is disclosed"
        ),
        "pass": overlap_boot,
    }
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    gates["G1"] = gate
    gates["G1_timestamp_utc"] = datetime.now(UTC).isoformat()
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: gate[k] for k in ("overlap_bootstrap_ci", "overlap_paired_t_ci", "pass")}, indent=2))
    print(f"Delta0 = {summary['pooled_mean']!r} CI [{gate['delta0']['bootstrap']['ci95_low']!r}, "
          f"{gate['delta0']['bootstrap']['ci95_high']!r}] vs F2 {F2_CI}")
    if not overlap_boot:
        print("G1 FAIL -> LEG VOID ON NON-REPLICATION (P1b). STOP.")
    return gate


# ===========================================================================
# Secondary question -- reader A vs A' (frame-refreshed), R-abs, free design.
# ===========================================================================

def run_sec_world(world: int, knobs: dict[str, Any], knob_tag: str) -> dict[str, Any]:
    module = k1()
    module.N_ORACLE = SEC_NORM_POOL
    seed = world_seed_for("abs", world, knob_tag)
    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    n_panel = len(f2().build_layout_common(reference)[0])
    panel, norm_events, labels = module.build_abs_world("free", n_panel, knobs, seed)
    half = SEC_NORM_POOL // 2
    pool_a, pool_b = norm_events[:half], norm_events[half:]
    mus = {
        ("oracle", "a"): pool_a.mean(axis=0),
        ("oracle", "b"): pool_b.mean(axis=0),
        ("est8", "a"): pool_a[:SEC_EST].mean(axis=0),
        ("est8", "b"): pool_b[:SEC_EST].mean(axis=0),
    }
    out: dict[str, Any] = {"world": int(world), "world_seed": int(seed),
                           "n_panel": int(n_panel), "arms": {}}
    for arm in ("oracle", "est8"):
        cards_a = module.cards_for_arm(panel, labels, mus[(arm, "a")])
        cards_b = module.cards_for_arm(panel, labels, mus[(arm, "b")])
        # reader A  : ONE norm shared across halves (T3(c) hypothesis)
        met_A = module.reader_metrics(cards_a["A1"], cards_a["A2"])
        # reader A' : INDEPENDENT norm samples per occasion half (frame refreshed)
        met_Ap = module.reader_metrics(cards_a["A1"], cards_b["A2"])
        out["arms"][arm] = {
            "rank1_A": met_A["rank1"], "rank1_Aprime": met_Ap["rank1"],
            "correct_A": met_A["correct"], "correct_Aprime": met_Ap["correct"],
            "readability_A": met_A["readability_mean"],
            "readability_Aprime": met_Ap["readability_mean"],
        }
    return out


def run_sec_stage(knobs: dict[str, Any], knob_tag: str) -> None:
    rows, probes = [], {}
    started = time.time()
    for world in range(SEC_WORLDS):
        res = run_sec_world(world, knobs, knob_tag)
        for arm, entry in res["arms"].items():
            rows.append({
                "world": world, "arm": arm, "n_panel": res["n_panel"],
                "world_seed": res["world_seed"],
                "rank1_A": entry["rank1_A"], "rank1_Aprime": entry["rank1_Aprime"],
                "readability_A": entry["readability_A"],
                "readability_Aprime": entry["readability_Aprime"],
            })
            for reader in ("A", "Aprime"):
                probes[f"{world}|{arm}|{reader}"] = entry[f"correct_{reader}"].astype(np.int8)
        print(
            f"[sec w{world}] A: oracle={res['arms']['oracle']['rank1_A']:.4f} "
            f"est8={res['arms']['est8']['rank1_A']:.4f} | A': "
            f"oracle={res['arms']['oracle']['rank1_Aprime']:.4f} "
            f"est8={res['arms']['est8']['rank1_Aprime']:.4f}",
            flush=True,
        )
    pd.DataFrame(rows).to_csv(OUT / "sec_cells.csv", index=False)
    np.savez_compressed(OUT / "sec_probe_correct.npz", **probes)
    print(f"[sec] done in {time.time() - started:.0f}s")


# ===========================================================================
# Adjudication.
# ===========================================================================

def adjudicate() -> dict[str, Any]:
    frame = _load_main()
    piv = frame.pivot(index="world", columns="arm", values="agreement_mean")
    a0, a1, a2, a3, a4 = (piv[c].to_numpy() for c in ("A0", "A1", "A2", "A3", "A4"))
    a1p, a3p = piv["A1p"].to_numpy(), piv["A3p"].to_numpy()
    d0 = a0 - a2
    d1 = a1 - a3
    gap = d0 - d1
    out: dict[str, Any] = {"arm_means": {c: float(piv[c].mean()) for c in piv.columns}}

    out["delta0"] = _contrast_summary(d0, BOOT_SEEDS["delta0"], "Delta0 = A0 - A2")
    out["delta1"] = _contrast_summary(d1, BOOT_SEEDS["delta1"], "Delta1 = A1 - A3")
    out["gap"] = _contrast_summary(gap, BOOT_SEEDS["gap"], "Delta0 - Delta1")
    share = _paired_world_bootstrap(
        {"d0": d0, "d1": d1},
        lambda v: float((v["d0"].mean() - v["d1"].mean()) / v["d0"].mean()),
        BOOT_SEEDS["share"],
    )
    out["share_S_hat"] = share
    out["degeneracy"] = {
        "max_abs_delta1": float(np.abs(d1).max()),
        "delta1_is_zero_to_1e-6": bool(np.abs(d1).max() < 1e-6),
        "note": (
            "at kappa=1 occasion_mode enters the generator ONLY through the common "
            "channel (f2:180-196), so any removal of that channel makes A1 and A3 the "
            "same panel; Delta1 == 0 is a designed identity, not a measurement"
        ),
    }

    # ---- L-a ------------------------------------------------------------
    la = {
        "lean": "L-a",
        "rule": "(Delta0 - Delta1) pooled CI excludes 0 AND S_hat >= 0.25",
        "gap": out["gap"]["bootstrap"],
        "share_point": share["point"],
        "share_ci": [share["ci95_low"], share["ci95_high"]],
        "sign_band": out["gap"]["sign_band"],
        "verdict": "HOLD" if (out["gap"]["bootstrap"]["excludes_zero"]
                              and share["point"] >= SHARE_LA) else "MISS",
    }
    out["L-a"] = la

    # ---- L-b ------------------------------------------------------------
    lb = {
        "lean": "L-b",
        "rule": "Delta1 pooled CI > 0 (a jurisdiction-alignment share survives)",
        "delta1": out["delta1"]["bootstrap"],
        "sign_band": out["delta1"]["sign_band"],
        "verdict": "HOLD" if out["delta1"]["bootstrap"]["excludes_zero_positive"] else "MISS",
    }
    out["L-b"] = lb

    # ---- L-c ------------------------------------------------------------
    spec = _contrast_summary(a3 - a2, BOOT_SEEDS["spec"], "A3 - A2 (specificity)")
    lc = {
        "lean": "L-c",
        "rule": f"A3 - A2 pooled CI inside +/- {EQUIV_MARGIN!r}",
        "contrast": spec,
        "margin": EQUIV_MARGIN,
        "ci_inside_margin": bool(
            spec["bootstrap"]["ci95_low"] > -EQUIV_MARGIN
            and spec["bootstrap"]["ci95_high"] < EQUIV_MARGIN
        ),
    }
    lc["verdict"] = "HOLD" if lc["ci_inside_margin"] else "MISS"
    out["L-c"] = lc

    # ---- removals + L-e --------------------------------------------------
    r_or = _contrast_summary(a0 - a1, BOOT_SEEDS["removal"], "R_or = A0 - A1")
    r_est = _contrast_summary(a0 - a4, BOOT_SEEDS["removal"] + 1, "R_est = A0 - A4")
    ratio = _paired_world_bootstrap(
        {"e": a0 - a4, "o": a0 - a1},
        lambda v: float(v["e"].mean() / v["o"].mean()),
        BOOT_SEEDS["removal"] + 2,
    )
    applicable = bool(out["gap"]["bootstrap"]["excludes_zero"])
    le = {
        "lean": "L-e",
        "rule": "R_est CI excludes 0 AND pooled R_est/R_or >= 0.5; INAPPLICABLE unless (Delta0-Delta1) CI excludes 0",
        "applicable": applicable,
        "R_or": r_or,
        "R_est": r_est,
        "ratio_est_over_or": ratio,
        "verdict": (
            "INAPPLICABLE" if not applicable
            else ("HOLD" if (r_est["bootstrap"]["excludes_zero"]
                             and ratio["point"] >= RATIO_LE) else "MISS")
        ),
    }
    out["L-e"] = le

    # ---- disclosed second reading (author-channel removal) ---------------
    d1p = a1p - a3p
    second = {
        "note": (
            "standing rule 9: the registration names the removed channel 'w_mu' while "
            "its semantics name the occasion-common channel; in f2's generator these "
            "are different terms (w_mu = the per-author mean, f2:178; the kappa=1 "
            "common channel = the state slot, f2:196). The registered arm is the "
            "semantic one (A1/A3); this is the literal-w_mu reading, computed and "
            "reported in full, adjudicating nothing."
        ),
        "delta1_prime": _contrast_summary(d1p, BOOT_SEEDS["second_reading"],
                                          "Delta1' = A1' - A3' (author channel deleted)"),
        "gap_prime": _contrast_summary(d0 - d1p, BOOT_SEEDS["second_reading"] + 1,
                                       "Delta0 - Delta1'"),
        "author_reading_share": _paired_world_bootstrap(
            {"d0": d0, "d1p": d1p},
            lambda v: float((v["d0"].mean() - v["d1p"].mean()) / v["d0"].mean()),
            BOOT_SEEDS["second_reading"] + 2,
        ),
        "frame_share_of_delta0": _paired_world_bootstrap(
            {"d0": d0, "d1p": d1p},
            lambda v: float(v["d1p"].mean() / v["d0"].mean()),
            BOOT_SEEDS["second_reading"] + 3,
        ),
    }
    out["second_reading"] = second

    # ---- L-d -------------------------------------------------------------
    cells = pd.read_csv(OUT / "sec_cells.csv")
    store = np.load(OUT / "sec_probe_correct.npz")
    ld: dict[str, Any] = {
        "lean": "L-d",
        "rule": (
            f"under reader A' the forged advantage collapses: |rank1(est8) - "
            f"rank1(oracle)| pooled CI inside +/- {LD_MARGIN}; AND |oracle rank1(A') - "
            "oracle rank1(A)| < 0.01"
        ),
        "margin": LD_MARGIN,
    }
    for reader in ("A", "Aprime"):
        per_world = [
            store[f"{w}|est8|{reader}"].astype(float) - store[f"{w}|oracle|{reader}"].astype(float)
            for w in range(SEC_WORLDS)
        ]
        boot = k1()._author_stratified_bootstrap(
            per_world, seed=BOOT_SEEDS["ld_A" if reader == "A" else "ld_Aprime"]
        )
        ld[reader] = {
            **boot,
            "inside_margin": bool(
                boot["ci95_low"] > -LD_MARGIN and boot["ci95_high"] < LD_MARGIN
            ),
        }
    oracle_A = float(cells[cells["arm"] == "oracle"]["rank1_A"].mean())
    oracle_Ap = float(cells[cells["arm"] == "oracle"]["rank1_Aprime"].mean())
    ld["oracle_rank1_A"] = oracle_A
    ld["oracle_rank1_Aprime"] = oracle_Ap
    ld["oracle_move"] = abs(oracle_Ap - oracle_A)
    ld["oracle_move_below_0p01"] = bool(abs(oracle_Ap - oracle_A) < 0.01)
    ld["est8_rank1_A"] = float(cells[cells["arm"] == "est8"]["rank1_A"].mean())
    ld["est8_rank1_Aprime"] = float(cells[cells["arm"] == "est8"]["rank1_Aprime"].mean())
    ld["k1_forged_effect_reference"] = -0.05012690355329949
    ld["verdict"] = (
        "HOLD" if (ld["Aprime"]["inside_margin"] and ld["oracle_move_below_0p01"]) else "MISS"
    )
    out["L-d"] = ld

    # ---- pivots -----------------------------------------------------------
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    out["pivots"] = {
        "P1b": {
            "rule": "G1 fails -> leg VOID on non-replication",
            "fires": bool(not gates["G1"]["pass"]),
        },
        "P2b": {
            "rule": "L-a HOLD, L-b MISS, S_hat >= 0.75 -> append-only retrospective "
                    "downgrade opens for every consumer of 'composition works at fixed budget'",
            "fires": bool(
                la["verdict"] == "HOLD" and lb["verdict"] == "MISS"
                and share["point"] >= SHARE_P2B
            ),
        },
        "P3b": {
            "rule": "L-d MISS -> T6'' wrong as stated; the forged component is not "
                    "issuer-sampling content; its localization becomes the next registration",
            "fires": bool(ld["verdict"] == "MISS"),
        },
        "P4b": {
            "rule": "G2b fails on BOTH paths -> leg blocked, report, redesign",
            "fires": bool(not gates["G2b"]["pass"]),
        },
    }
    return out


def verdict_slug(adj: dict[str, Any], gates: dict[str, Any]) -> str:
    """Deterministic slug recipe, fixed in code before any arm ran."""
    if not gates.get("G1", {}).get("pass", False):
        return "LEG_VOID_ON_NON_REPLICATION"
    parts = []
    if adj["degeneracy"]["delta1_is_zero_to_1e-6"]:
        parts.append("REGISTERED_DECOMPOSITION_DEGENERATE_BY_CONSTRUCTION__SHARE_IS_UNITY_BY_IDENTITY")
    else:
        share = adj["share_S_hat"]["point"]
        parts.append(f"AMPLIFICATION_SHARE_{share:.2f}".replace(".", "p"))
    frame = adj["second_reading"]["frame_share_of_delta0"]
    if adj["second_reading"]["delta1_prime"]["bootstrap"]["excludes_zero_positive"]:
        if frame["point"] >= SHARE_P2B:
            parts.append("COMPOSITION_EFFECT_SURVIVES_AUTHOR_DELETION__FRAME_OWNED")
        else:
            parts.append("COMPOSITION_EFFECT_PARTLY_SURVIVES_AUTHOR_DELETION")
    else:
        parts.append("COMPOSITION_EFFECT_REQUIRES_THE_AUTHOR_CHANNEL")
    parts.append("T6dd_HOLDS" if adj["L-d"]["verdict"] == "HOLD" else "T6dd_MISS")
    if adj["pivots"]["P2b"]["fires"]:
        parts.append("P2B_FIRES")
    return "__".join(parts)


def run_finalize() -> None:
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    adj = adjudicate()
    slug = verdict_slug(adj, gates)
    decision = {
        "experiment": "M4-K1b_composition_ownership",
        "banner": BANNER,
        "tier": "EXPLORATORY",
        "registered_spec": "docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md#M4-K1b",
        "part0_registered_in": (
            "reports/SUICA_M4_K1B_COMPOSITION_OWNERSHIP_REPORT.md Part 0 (before arms)"
        ),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "worlds": WORLDS,
        "knobs": gates["knobs"],
        "knob_tag": gates["knob_tag"],
        "gates": {
            k: gates[k].get("pass")
            for k in ("G0", "G1", "G1b", "G2b", "G3b", "G4b", "G5")
            if k in gates
        },
        "g2b_path": gates["G2b"]["path_taken"],
        "adjudication": adj,
        "verdict": slug,
        "label_free": True,
        "claim_boundary": (
            "Synthetic decomposition of a synthetic composition effect in a world "
            "calibrated to the opened PANDORA D-panel regime, through the deployed "
            "frozen machinery; licenses IDT grammar (typing rules and design priors) "
            "only. No claim about any corpus, construct, person, or diagnosis."
        ),
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(
        {k: v.get("verdict") for k, v in adj.items() if isinstance(v, dict) and "verdict" in v},
        indent=2,
    ))
    print(json.dumps(adj["pivots"], indent=2))
    print("VERDICT:", slug)


def write_manifest(stage: str, seconds: float, extra: dict[str, Any] | None = None) -> None:
    path = OUT / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
        "leg": "M4-K1b",
        "banner": BANNER,
        "master_seed": MASTER_SEED,
        "worlds": WORLDS,
        "seed_recipe": (
            "v8.stable_bucket(f'{MASTER_SEED}-{group}-w{world}-{knob_tag}', "
            "salt='m4k1b-world', modulus=2**63-1)"
        ),
        "per_stage_seeds": {
            "main": "group='main', worlds 0..31 (A0,A1,A2,A3,A4,A1p,A3p share the world seed)",
            "pilot": f"group='pilot', worlds {list(PILOT_WORLDS)} (reserved, never adjudicated)",
            "g2b": f"group='g2b', worlds {list(G2B_WORLDS)}",
            "g4b": f"group='g4b', worlds {list(G4B_WORLDS)}",
            "abs": f"group='abs', worlds 0..{SEC_WORLDS - 1} (secondary question)",
            "a4_norm_pool": "v8.stable_bucket(f'{world_seed}-normpool', salt='m4k1b-normpool')",
            "shift": "k1's own v8.stable_bucket(f'{world_seed}-{occasion_mode}', salt='m4k1-shift')",
            "bootstrap": BOOT_SEEDS,
        },
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "stages": {},
    }
    manifest["stages"][stage] = {
        "wall_seconds": round(float(seconds), 3),
        "finished_utc": datetime.now(UTC).isoformat(),
        **(extra or {}),
    }
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=["part0", "part0_supp", "arms_a", "gate_g1", "arms_b", "sec", "finalize"],
        required=True,
    )
    parser.add_argument("--workers", type=int, default=max(2, min(6, (os.cpu_count() or 4) - 2)))
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    for path in (REF_PATH, F1_CALIBRATION, F2_OUT / "decision.json",
                 K1_OUT / "decision.json", K1_OUT / "rel_cells.csv",
                 K1_OUT / "abs_probe_correct.npz"):
        if not path.exists():
            raise AssertionError(f"{path} missing (read-only predecessor artifact).")

    started = time.time()
    if args.stage == "part0":
        run_part0(args.workers)
    else:
        if not (OUT / "gates.json").exists():
            raise AssertionError("Part 0 gates must run (and be reported) before arms.")
        knobs, knob_tag = knobs_and_tag()
        if args.stage == "part0_supp":
            gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
            gates["G4b_supplementary"] = gate_g4b_supplementary(args.workers)
            (OUT / "gates.json").write_text(
                json.dumps(gates, indent=2) + "\n", encoding="utf-8"
            )
            supp = gates["G4b_supplementary"]
            print(json.dumps({k: supp[k] for k in (
                "smallest_satisfiable_n_at_anchor", "per_world_delta",
                "signs_positive", "pass")}, indent=2))
            print("paired:", json.dumps(supp["paired"], indent=2))
        elif args.stage == "arms_a":
            frame = run_arms(("A0", "A2"), tuple(range(WORLDS)), "main", args.workers, "arms_a")
            frame.to_csv(OUT / "arms_a.csv", index=False)
        elif args.stage == "gate_g1":
            gate_g1()
        elif args.stage == "arms_b":
            gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
            if not gates.get("G1", {}).get("pass", False):
                raise AssertionError("G1 did not pass: leg VOID on non-replication (P1b).")
            frame = run_arms(
                ("A1", "A3", "A4", "A1p", "A3p"), tuple(range(WORLDS)), "main",
                args.workers, "arms_b",
            )
            frame.to_csv(OUT / "arms_b.csv", index=False)
        elif args.stage == "sec":
            run_sec_stage(knobs, knob_tag)
        elif args.stage == "finalize":
            run_finalize()
    write_manifest(args.stage, time.time() - started)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
