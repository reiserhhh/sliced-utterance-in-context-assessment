#!/usr/bin/env python3
"""M4-K1c -- ownership of the composition effect at the LIVE-AUTHOR knob (kappa=0.5).

Registered spec: docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md section "M4-K1c --
Ownership at the live-author knob (kappa=0.5), and T6'' v2" (REGISTERED
2026-08-09, BEFORE RUN, commit a6d1eb2). Part 0 register-notes
(operationalizations for everything the registration left as an implementation
choice, plus the standing-rule-9 instrument resolutions) are in
reports/SUICA_M4_K1C_OWNERSHIP_LIVE_KNOB_REPORT.md Part 0, written BEFORE any
arm stage ran.

Machinery reuse (no reimplementation of existing constructions):
  * world generator      f2.generate_world_composed  (scripts/run_suica_m4_f2_composition.py:129-198)
  * occasion designs     f2.occasion_labels          (f2:96-118)
  * common-shock draw    f2.shock_vector             (f2:120-126)
  * layout               f2.build_layout_common      (f2:205-222)
  * deployed gauge path  f2.run_axis1_world          (f2:276-370)
  * paired t CI          f2._paired_ci               (f2:1008-1025)
  * channel mirror /     k1b.channels, k1b._gen_remove, k1b._gen_estimated,
    arm surgery          k1b.estimated_occasion_norm
                         (scripts/run_suica_m4_k1b_composition_ownership.py:167-343)
                         -- generalized over kappa here (K1b hard-coded kappa=1.0,
                         where the AR term of the blend vanishes)
  * R-abs reader         k1.build_abs_world / k1.cards_for_arm / k1.reader_metrics
                         (scripts/run_suica_m4_k1_issuer_theorems.py:164-186, 210-250)
  * author-strat boot    k1._author_stratified_bootstrap (k1:832-854)
  * liveness diagnostic  f8._between_author_variance / _g6_state_ablation_events
                         (scripts/run_suica_m4_f8_occasion_axis_live.py:747-800),
                         re-expressed on f2's own generator (G4c)
Nothing in suica_core/ is touched (frozen operators are READ-ONLY).

Stages (foreground, chunked, resumable; artifacts under
results/m4_k1c_ownership_live_knob/):
  --stage part0    G0c, G1bc, G2c, G3c, G4c, G4c-info, G5c -> gates.json  (MUST
                   run, and the report's Part 0 MUST be written, before any arm)
  --stage arms_a   A0 (shared intact) + A2 (free intact), 128 worlds -> then G1c
  --stage gate_g1c the replication gate on A0-A2 (STOP / VOID if it fails)
  --stage arms_b   A1, A3, A4, A5, A6 (+ the rule-9 second reading A1w, A3w)
  --stage sec      the secondary question (reader A vs A', 8 worlds, R-abs, k=0.5)
  --stage finalize lean adjudication + pivots -> decision.json

G2c is a HARD STOP gate (registered): if the A1/A3 decomposition is degenerate
at kappa=0.5, no arm stage may run (pivot P4c).
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

# --- registered constants (docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md, M4-K1c) -----
MASTER_SEED = 20260812
WORLDS = 128
WORLDS_ESCALATED = 256          # G3c's single registered escalation
KAPPA = 0.5                     # the live-author knob
DRAWS = 20
BOOT_DRAWS = 2000
SEC_WORLDS = 8
SIGN_CLEAN = 104                # clean >= 104/128
SIGN_QUALIFIED = 85             # qualified >= 85/128
G3C_BAR = 0.004418076848551262           # 50% share of the kappa=0.5 effect
G3C_ASPIRATIONAL = 0.002209038424275631  # 25% share
LC_MARGIN = 0.004418076848551262         # L-c'' equivalence margin
SHARE_LA = 0.5                  # L-a'': S_frame >= 0.5
RATIO_LD = 0.5                  # L-d'': R_est / R_or >= 0.5
LE_CI_UPPER_BAR = 0.005         # L-e'': pooled CI upper bound < +0.005
LE_ORACLE_STABILITY = 0.01      # L-e'': oracle stability between A and A'
P2C_SHARE_BOUND = 0.25          # P2c: (Delta0-Delta0') CI upper < .25 x Delta0

# Anchors (re-derived before any arm).
F2_K05_CI = (0.004418364530893362, 0.013253942863311687)
F2_K05_PAIRED_MEAN = 0.008836153697102524
F2_K05_FREE_MEAN = 0.0005009098594400375
F2_K05_SHARED_MEAN = 0.009337063556542562
K1B_DELTA0 = 0.02416454033421539
K1B_DELTA1_PRIME = 0.04709060297774369
K1B_LE_RATIO = 0.943890194474869

# --- Part-0 operationalizations (see report Part 0; fixed BEFORE any arm) -----
A4_AUTHORS_PER_CONTEXT = 32   # "|P| = 32 disjoint authors" -- per context
SEC_NORM_POOL = 1024          # two disjoint 512-author sub-pools (reader A')
SEC_EST = 8                   # est8
PILOT_WORLDS = (9101, 9102, 9103, 9104, 9105, 9106, 9107, 9108)  # G3c 8-world pilot
G2C_WORLDS = (9301, 9302)     # G2c construction + gauge-level degeneracy check
BOOT_SEEDS = {
    "delta0": 20260812001,
    "delta1": 20260812002,
    "gap_frame": 20260812003,
    "share_frame": 20260812004,
    "delta0_prime": 20260812005,
    "gap_auth": 20260812006,
    "share_auth": 20260812007,
    "spec_a3": 20260812008,
    "spec_a6": 20260812009,
    "removal": 20260812010,
    "second_reading": 20260812011,
    "le_A": 20260812012,
    "le_Aprime": 20260812013,
}

OUT = ROOT / "results" / "m4_k1c_ownership_live_knob"
F2_OUT = ROOT / "results" / "m4_f2_composition"
K1_OUT = ROOT / "results" / "m4_k1_issuer"
K1B_OUT = ROOT / "results" / "m4_k1b_composition_ownership"
F4_OUT = ROOT / "results" / "m4_f4_author_axis"
F5_OUT = ROOT / "results" / "m4_f5_gauge_validity"
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
    """The same recipe f2.run_axis1_world uses internally (f2:288-291)."""
    return v8.stable_bucket(
        f"{MASTER_SEED}-{group}-w{world}-{knob_tag}",
        salt="m4k1c-world",
        modulus=2**63 - 1,
    )


# ===========================================================================
# Channel extraction -- K1b's line-for-line mirror of
# f2.generate_world_composed:151-197, with the kappa blend SPLIT into its two
# physically distinct terms (K1b could not: at kappa=1.0 the AR term is
# identically 0).
#     state_part = ar_part + common_part
#     ar_part     = sqrt(w_x) a ((sqrt(1-kappa) x   * g) @ L.T)   author AR state
#     common_part = sqrt(w_x) a ((sqrt(kappa)  s_co * g) @ L.T)   occasion-common
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
    ar_x = math.sqrt(max(0.0, 1.0 - kappa_f)) * x
    common_x = math.sqrt(kappa_f) * shock_x
    ar_part = math.sqrt(w_x) * a * ((ar_x * g) @ loadings.T)
    common_part = math.sqrt(w_x) * a * ((common_x * g) @ loadings.T)
    noise_part = math.sqrt(w_e) * sigma_iso * noise                    # f2:197
    return {
        "mean_part": mean_part,          # (n, 64)        author mean channel (w_mu)
        "state_part": state_part,        # (n, t_max, 64) the whole blended state slot
        "ar_part": ar_part,              # (n, t_max, 64) sqrt(1-kappa) author AR state
        "common_part": common_part,      # (n, t_max, 64) sqrt(kappa) occasion-common
        "noise_part": noise_part,        # (n, t_max, 64)
        "labels": labels,
        "loadings": loadings,
        "g": g,
        "a": a,
        "cache": cache,
        "counts": counts,
    }


def common_vector(
    knobs: dict[str, Any], loadings: np.ndarray, g: np.ndarray, a: float,
    world_seed: int, context: str, occ: int, kappa: float
) -> np.ndarray:
    """C(c,o) -- the occasion-common channel for one (context, occasion), at kappa."""
    k = int(knobs["k"])
    s = f2().shock_vector(world_seed, context, occ, k)
    return math.sqrt(float(knobs["w_x"])) * a * (((math.sqrt(kappa) * s) * g) @ loadings.T)


# ===========================================================================
# Arm generators: patches installed over f2.generate_world_composed inside the
# worker (K1b:244-343, generalized over kappa).
# ===========================================================================

_ORIG_GENERATE: Any = None
_ARM_STATE: dict[str, Any] = {}


def _gen_remove(counts, contexts, knobs, kappa, occasion_mode, world_seed):  # noqa: ANN001
    """Exact pre-map subtraction of a named channel.

    remove='common'     -> A1 / A3 : the occasion-common channel only
                          (sqrt(kappa) * shock), the AR state RETAINED
    remove='wholestate' -> A1w/A3w : K1b's literal object, the whole state slot
                          (rule-9 disclosed second reading at this knob)
    remove='authormean' -> A5 / A6 : the author channel (f2:178)
    """
    vectors = _ORIG_GENERATE(counts, contexts, knobs, kappa, occasion_mode, world_seed)
    ch = channels(counts, contexts, knobs, kappa, occasion_mode, world_seed)
    which = _ARM_STATE["remove"]
    if which == "common":
        term = ch["common_part"]
        return [vec - term[i][: len(vec)] for i, vec in enumerate(vectors)]
    if which == "wholestate":
        term = ch["state_part"]
        return [vec - term[i][: len(vec)] for i, vec in enumerate(vectors)]
    if which == "authormean":
        mean_part = ch["mean_part"]
        return [vec - mean_part[i][None, :] for i, vec in enumerate(vectors)]
    raise ValueError(which)


def _gen_estimated(counts, contexts, knobs, kappa, occasion_mode, world_seed):  # noqa: ANN001
    """A4: subtract an ESTIMATED per-(context, occasion) norm built from
    A4_AUTHORS_PER_CONTEXT disjoint authors observed on the same occasions."""
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
    """K1b:278-307, generalized over kappa.

    The pool's own idiosyncratic content is its FULL non-common content --
    author mean + its own sqrt(1-kappa) AR state + noise -- with the pool's own
    occasion channel dropped and the PANEL's C(c,o) put in its place. At
    kappa = 1.0 the AR term is identically 0 and this reduces bit-exactly to
    K1b's construction.
    """
    ctxs = sorted(set(contexts))
    t_max = max(counts)
    n_ctx = len(ctxs)
    ncounts = [t_max] * (A4_AUTHORS_PER_CONTEXT * n_ctx)
    ncontexts = [c for c in ctxs for _ in range(A4_AUTHORS_PER_CONTEXT)]
    norm_seed = v8.stable_bucket(
        f"{world_seed}-normpool", salt="m4k1c-normpool", modulus=2**63 - 1
    )
    nch = channels(ncounts, ncontexts, knobs, kappa, "shared", norm_seed)
    idio = nch["mean_part"][:, None, :] + nch["ar_part"] + nch["noise_part"]
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
            c_vec = common_vector(knobs, loadings_p, g, a, world_seed, ctx, occ, kappa)
            mu_hat[(ctx, occ)] = block[:, occ, :].mean(axis=0) + c_vec
    return mu_hat


ARM_SPEC: dict[str, dict[str, Any]] = {
    # arm    design    generator patch        arm_state
    "A0": {"design": "shared", "patch": None, "state": {}},
    "A2": {"design": "free", "patch": None, "state": {}},
    "A1": {"design": "shared", "patch": "remove", "state": {"remove": "common"}},
    "A3": {"design": "free", "patch": "remove", "state": {"remove": "common"}},
    "A4": {"design": "shared", "patch": "estimated", "state": {}},
    "A5": {"design": "shared", "patch": "remove", "state": {"remove": "authormean"}},
    "A6": {"design": "free", "patch": "remove", "state": {"remove": "authormean"}},
    "A1w": {"design": "shared", "patch": "remove", "state": {"remove": "wholestate"}},
    "A3w": {"design": "free", "patch": "remove", "state": {"remove": "wholestate"}},
}
PATCHES: dict[str, Callable[..., Any]] = {
    "remove": _gen_remove,
    "estimated": _gen_estimated,
}
ARMS_A = ("A0", "A2")
ARMS_B = ("A1", "A3", "A4", "A5", "A6", "A1w", "A3w")


def arm_task(arm: str, world: int, knobs: dict[str, Any], knob_tag: str,
             group: str) -> dict[str, Any]:
    spec = ARM_SPEC[arm]
    return {
        "cell": f"{group}_{arm}",
        "arm": arm,
        "world": world,
        "seed_group": group,
        "corpus_tag": "m4k1c",
        "world_salt": "m4k1c-world",
        "budget_label": "k1c.0",
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

def gate_g0c(knobs: dict[str, Any], knob_tag: str) -> dict[str, Any]:
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
    seed0 = world_seed_for("main", 0, knob_tag)
    vec0 = module.generate_world_composed(common, ctx, knobs, KAPPA, "shared", seed0)
    shapes_ok = all(v.shape == (common[i], 64) for i, v in enumerate(vec0))
    same = {
        "authors": int(len(aid)) == k1_gates["f2_authors_per_world"],
        "events": int(sum(common)) == k1_gates["f2_events_allocated_total"],
        "multiset": hist == {int(k): v for k, v in
                             k1_gates["f2_events_per_author_multiset"].items()},
        "contexts": sorted(set(ctx)) == k1_gates["f2_contexts"],
        "retained": int(len(retained)) == k1_gates["f2_n_retained_by_deployed_gauge"],
    }
    return {
        "gate": "G0c",
        "description": "dims pinned to K1's; verified at the fresh seeds' first world (kappa=0.5)",
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
        "kappa": KAPPA,
        "grain": ("per-world paired design contrasts; 128 worlds as the unit; "
                  "authors nested within world"),
        "pass": bool(all(same.values()) and shapes_ok),
    }


def gate_g1bc() -> dict[str, Any]:
    """Bit-exact re-derivation of K1b's three registered anchors."""
    decision = json.loads((K1B_OUT / "decision.json").read_text(encoding="utf-8"))
    adj = decision["adjudication"]
    frames = [pd.read_csv(K1B_OUT / f) for f in ("arms_a.csv", "arms_b.csv")]
    piv = pd.concat(frames, ignore_index=True).pivot(
        index="world", columns="arm", values="agreement_mean"
    )
    a0, a2 = piv["A0"].to_numpy(), piv["A2"].to_numpy()
    a1p, a3p = piv["A1p"].to_numpy(), piv["A3p"].to_numpy()
    a1, a4 = piv["A1"].to_numpy(), piv["A4"].to_numpy()
    d0 = float((a0 - a2).mean())
    d1p = float((a1p - a3p).mean())
    ratio = float((a0 - a4).mean() / (a0 - a1).mean())
    checks = {
        "delta0_rederived": d0,
        "delta0_persisted": adj["delta0"]["pooled_mean"],
        "delta0_registration": K1B_DELTA0,
        "delta0_bit_exact": bool(d0 == adj["delta0"]["pooled_mean"] == K1B_DELTA0),
        "delta1_prime_rederived": d1p,
        "delta1_prime_persisted": adj["second_reading"]["delta1_prime"]["pooled_mean"],
        "delta1_prime_registration": K1B_DELTA1_PRIME,
        "delta1_prime_bit_exact": bool(
            d1p == adj["second_reading"]["delta1_prime"]["pooled_mean"] == K1B_DELTA1_PRIME
        ),
        "le_ratio_rederived": ratio,
        "le_ratio_persisted": adj["L-e"]["ratio_est_over_or"]["point"],
        "le_ratio_registration": K1B_LE_RATIO,
        "le_ratio_bit_exact": bool(
            ratio == adj["L-e"]["ratio_est_over_or"]["point"] == K1B_LE_RATIO
        ),
    }
    # F2's own kappa=0.5 block, re-verified at artifact precision (G1c's target).
    f2_dec = json.loads((F2_OUT / "decision.json").read_text(encoding="utf-8"))
    k05 = f2_dec["adjudication"]["paired_differences"]["k05"]
    f2_checks = {
        "kappa": k05["kappa"],
        "free_mean": k05["free_mean"],
        "shared_mean": k05["shared_mean"],
        "paired_mean": k05["mean"],
        "ci95": [k05["ci95_low"], k05["ci95_high"]],
        "matches_registration": bool(
            k05["kappa"] == KAPPA
            and k05["free_mean"] == F2_K05_FREE_MEAN
            and k05["shared_mean"] == F2_K05_SHARED_MEAN
            and k05["mean"] == F2_K05_PAIRED_MEAN
            and k05["ci95_low"] == F2_K05_CI[0]
            and k05["ci95_high"] == F2_K05_CI[1]
        ),
        "shared_minus_free_identity_max_ulp_gap": abs(
            (k05["shared_mean"] - k05["free_mean"]) - k05["mean"]
        ),
    }
    return {
        "gate": "G1bc",
        "description": ("K1b's anchors re-derived bit-exactly from "
                        "results/m4_k1b_composition_ownership/ artifacts, before any new arm"),
        **checks,
        "f2_kappa05_block": f2_checks,
        "pass": bool(
            checks["delta0_bit_exact"]
            and checks["delta1_prime_bit_exact"]
            and checks["le_ratio_bit_exact"]
            and f2_checks["matches_registration"]
        ),
    }


def _design_independence_report(
    counts: list[int], contexts: list[str], knobs: dict[str, Any], world_seed: int
) -> dict[str, Any]:
    """Panel-level construction check for G2c: are the post-removal shared and
    free panels the same object?"""
    module = f2()
    out: dict[str, Any] = {}
    resp = {}
    ch = {}
    for design in ("shared", "free"):
        resp[design] = module.generate_world_composed(
            counts, contexts, knobs, KAPPA, design, world_seed
        )
        ch[design] = channels(counts, contexts, knobs, KAPPA, design, world_seed)

    # (0) three/four-channel reconstruction exactness, and the blend split
    recon = max(
        float(np.abs(vec - (ch["shared"]["mean_part"][i][None, :]
                            + ch["shared"]["state_part"][i][: len(vec)]
                            + ch["shared"]["noise_part"][i][: len(vec)])).max())
        for i, vec in enumerate(resp["shared"])
    )
    split = float(np.abs(ch["shared"]["state_part"]
                         - (ch["shared"]["ar_part"] + ch["shared"]["common_part"])).max())
    out["reconstruction_residual_max"] = recon
    out["state_split_ar_plus_common_residual_max"] = split

    # (1) which channels are design-invariant, at machine precision
    for name in ("mean_part", "ar_part", "noise_part", "common_part"):
        out[f"{name}_shared_vs_free_max"] = float(
            np.abs(ch["shared"][name] - ch["free"][name]).max()
        )

    # (2) the removal arms' PANELS
    for tag, term in (("common", "common_part"), ("wholestate", "state_part")):
        pan_s = [vec - ch["shared"][term][i][: len(vec)]
                 for i, vec in enumerate(resp["shared"])]
        pan_f = [vec - ch["free"][term][i][: len(vec)]
                 for i, vec in enumerate(resp["free"])]
        out[f"panel_A1_vs_A3_max_abs__remove_{tag}"] = max(
            float(np.abs(pan_s[i] - pan_f[i]).max()) for i in range(len(pan_s))
        )
        out[f"panel_A1_rms__remove_{tag}"] = float(
            np.sqrt(np.mean(np.concatenate([p.ravel() for p in pan_s]) ** 2))
        )
    # (3) the author-deletion arms' PANELS (A5 vs A6) -- the registered contrast
    #     that is NOT touched by the removal degeneracy
    pan_s5 = [vec - ch["shared"]["mean_part"][i][None, :]
              for i, vec in enumerate(resp["shared"])]
    pan_f6 = [vec - ch["free"]["mean_part"][i][None, :]
              for i, vec in enumerate(resp["free"])]
    out["panel_A5_vs_A6_max_abs"] = max(
        float(np.abs(pan_s5[i] - pan_f6[i]).max()) for i in range(len(pan_s5))
    )
    out["panel_A0_vs_A2_max_abs"] = max(
        float(np.abs(resp["shared"][i] - resp["free"][i]).max())
        for i in range(len(resp["shared"]))
    )
    # (4) twin generation with the shock channel zeroed
    orig_shock = module.shock_vector
    twins = {}
    module.shock_vector = lambda *_a, **_kw: np.zeros(int(knobs["k"]))
    try:
        for design in ("shared", "free"):
            twins[design] = module.generate_world_composed(
                counts, contexts, knobs, KAPPA, design, world_seed
            )
    finally:
        module.shock_vector = orig_shock
    out["twin_shared_vs_twin_free_max"] = max(
        float(np.abs(twins["shared"][i] - twins["free"][i]).max())
        for i in range(len(counts))
    )
    out["subtract_common_vs_twin_max"] = max(
        float(np.abs((resp["shared"][i] - ch["shared"]["common_part"][i][: len(resp["shared"][i])])
                     - twins["shared"][i]).max())
        for i in range(len(counts))
    )
    # (5) the retained common channel's scale, for context
    ev = np.concatenate([ch["shared"]["common_part"][i, : counts[i]].ravel()
                         for i in range(len(counts))])
    ar = np.concatenate([ch["shared"]["ar_part"][i, : counts[i]].ravel()
                         for i in range(len(counts))])
    out["common_part_rms_over_events"] = float(np.sqrt(np.mean(ev**2)))
    out["ar_part_rms_over_events"] = float(np.sqrt(np.mean(ar**2)))
    return out


def gate_g2c(knobs: dict[str, Any], knob_tag: str, workers: int) -> dict[str, Any]:
    """Rule 10: PROVE non-degeneracy from source at kappa=0.5, then verify
    empirically. Degenerate -> STOP, registration defect, no arms (P4c)."""
    started = time.time()
    module = f2()
    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    _aid, ctx, _spl, counts, _raw = module.build_layout_common(reference)
    per_world = []
    for w in G2C_WORLDS:
        seed = world_seed_for("g2c", w, knob_tag)
        entry = {"world": int(w), "world_seed": int(seed)}
        entry.update(_design_independence_report(counts, ctx, knobs, seed))
        per_world.append(entry)

    # gauge-level: per-world Delta1 for BOTH removal readings, reserved seeds
    frame = run_arms(("A1", "A3", "A1w", "A3w", "A0", "A2"), G2C_WORLDS, "g2c",
                     workers, "G2c gauge")
    frame.to_csv(OUT / "g2c_cells.csv", index=False)
    piv = frame.pivot(index="world", columns="arm", values="agreement_mean")
    d1 = (piv["A1"] - piv["A3"]).to_numpy()
    d1w = (piv["A1w"] - piv["A3w"]).to_numpy()
    d0 = (piv["A0"] - piv["A2"]).to_numpy()

    panel_max_common = max(e["panel_A1_vs_A3_max_abs__remove_common"] for e in per_world)
    panel_max_whole = max(e["panel_A1_vs_A3_max_abs__remove_wholestate"] for e in per_world)
    delta1_max = float(np.abs(d1).max())
    delta1w_max = float(np.abs(d1w).max())
    non_degenerate = bool(delta1_max > 1e-12 and panel_max_common > 1e-12)
    non_degenerate_second_reading = bool(delta1w_max > 1e-12 and panel_max_whole > 1e-12)

    proof = {
        "claim": (
            "At EVERY kappa > 0, removing the occasion-common channel collapses the "
            "shared and free panels into the SAME panel, so Delta1 = A1 - A3 is "
            "identically 0. The registration's premise -- that sqrt(1-kappa) > 0 "
            "'keeps the author AR state in the panel' and therefore prevents the "
            "collapse -- is true in its first clause and does not entail its second: "
            "the retained AR state is DESIGN-INVARIANT."
        ),
        "derivation": [
            "f2:180  labels = occasion_labels(counts, occasion_mode) -- the ONLY "
            "consumer of occasion_mode in generate_world_composed.",
            "f2:184-193  labels feed exactly one object: shock_x[i,t] = "
            "shock_vector(world_seed, context, occ, k).",
            "f2:151-177  rng = default_rng(world_seed); loadings, z, zeta, phi, x, "
            "noise are drawn BEFORE the label loop from that single rng, and "
            "shock_vector opens its OWN generator (f2:120-126) -- so loadings, z, "
            "phi, x and noise are bit-identical across occasion_mode at a fixed "
            "world_seed (f2:139-145 states this invariance explicitly).",
            "f2:178  mean_part = f(z, g, loadings)                -> design-invariant.",
            "f2:197  noise_part = f(noise)                        -> design-invariant.",
            "f2:195  blended_x = sqrt(1-kappa) x + sqrt(kappa) shock_x; the first "
            "term is design-invariant, the second is the ONLY design-carrying term.",
            "f2:196  state_part = sqrt(w_x) a ((blended_x g) @ L.T) is LINEAR in "
            "blended_x, hence state_part = ar_part + common_part with "
            "ar_part design-invariant and common_part design-carrying.",
            "Therefore response - common_part = mean_part + ar_part + noise_part is "
            "design-invariant for every kappa in (0,1]; A1 and A3 are the same panel "
            "and Delta1 == 0. The same holds a fortiori for K1b's literal object "
            "(response - state_part = mean_part + noise_part).",
            "Contrapositive, for the record: a non-degenerate 'frame share' arm in "
            "THIS generator must retain some design-carrying content (e.g. an "
            "ESTIMATED / partial common subtraction, or a knob-level change to "
            "occasion_labels), not an exact removal of the common channel.",
        ],
        "kappa_dependence": (
            "kappa scales common_part by sqrt(kappa) but does not change WHICH "
            "channel carries the design; no value of kappa in (0,1] rescues the "
            "decomposition."
        ),
        "unaffected_registered_contrasts": (
            "Delta0 = A0-A2 and Delta0' = A5-A6 both retain common_part and are "
            "NOT degenerate; S_auth = (Delta0-Delta0')/Delta0 is the live "
            "measurement. Only Delta1 / S_frame / L-a'' are identities."
        ),
    }
    return {
        "gate": "G2c",
        "description": ("rule 10 -- non-degeneracy of the registered A1/A3 "
                        "decomposition at kappa=0.5, proved from source then measured"),
        "kappa": KAPPA,
        "sqrt_one_minus_kappa": math.sqrt(1.0 - KAPPA),
        "sqrt_kappa": math.sqrt(KAPPA),
        "source_proof": proof,
        "worlds": list(G2C_WORLDS),
        "per_world_construction": per_world,
        "gauge_worlds": [int(w) for w in piv.index],
        "gauge_delta0": [float(v) for v in d0],
        "gauge_delta1_remove_common": [float(v) for v in d1],
        "gauge_delta1_remove_wholestate": [float(v) for v in d1w],
        "max_abs_delta1_remove_common": delta1_max,
        "max_abs_delta1_remove_wholestate": delta1w_max,
        "max_panel_A1_vs_A3_remove_common": panel_max_common,
        "max_panel_A1_vs_A3_remove_wholestate": panel_max_whole,
        "max_panel_A5_vs_A6": max(e["panel_A5_vs_A6_max_abs"] for e in per_world),
        "max_panel_A0_vs_A2": max(e["panel_A0_vs_A2_max_abs"] for e in per_world),
        "threshold": 1e-12,
        "non_degenerate_registered_reading": non_degenerate,
        "non_degenerate_second_reading": non_degenerate_second_reading,
        "verdict": "NON_DEGENERATE" if non_degenerate else "DEGENERATE",
        "consequence": (
            "arms proceed" if non_degenerate
            else "P4c FIRES: STOP, registration defect, NO ARMS"
        ),
        "seconds": float(time.time() - started),
        "pass": non_degenerate,
    }


def gate_g3c(workers: int, degenerate: bool) -> dict[str, Any]:
    """Power: 8-world pilot; MDE(80%, alpha=.05, paired t, n=128) for BOTH
    (Delta0 - Delta1) and (Delta0 - Delta0')."""
    started = time.time()
    frame = run_arms(("A0", "A2", "A1", "A3", "A5", "A6", "A4"), PILOT_WORLDS,
                     "pilot", workers, "G3c pilot")
    frame.to_csv(OUT / "pilot_cells.csv", index=False)
    piv = frame.pivot(index="world", columns="arm", values="agreement_mean")
    d0 = (piv["A0"] - piv["A2"]).to_numpy()
    d1 = (piv["A1"] - piv["A3"]).to_numpy()
    d0p = (piv["A5"] - piv["A6"]).to_numpy()
    gap_frame = d0 - d1
    gap_auth = d0 - d0p

    def mde(sd: float, n: int) -> float:
        mult = float(stats.t.ppf(0.975, df=n - 1) + stats.t.ppf(0.80, df=n - 1))
        return float(mult * sd / math.sqrt(n))

    sd_frame = float(np.std(gap_frame, ddof=1))
    sd_auth = float(np.std(gap_auth, ddof=1))
    mde_frame = mde(sd_frame, WORLDS)
    mde_auth = mde(sd_auth, WORLDS)
    both_meet = bool(mde_frame <= G3C_BAR and mde_auth <= G3C_BAR)
    return {
        "gate": "G3c",
        "description": ("MDE(80%, alpha=.05, paired t, n=128) for BOTH "
                        "(Delta0 - Delta1) and (Delta0 - Delta0')"),
        "pilot_worlds": list(PILOT_WORLDS),
        "pilot_note": "reserved seeds; excluded from every adjudication",
        "pilot_delta0": [float(v) for v in d0],
        "pilot_delta1": [float(v) for v in d1],
        "pilot_delta0_prime": [float(v) for v in d0p],
        "pilot_gap_frame": [float(v) for v in gap_frame],
        "pilot_gap_auth": [float(v) for v in gap_auth],
        "sd_gap_frame": sd_frame,
        "sd_gap_auth": sd_auth,
        "sd_delta0": float(np.std(d0, ddof=1)),
        "sd_delta0_prime": float(np.std(d0p, ddof=1)),
        "sd_spec_a3_minus_a2": float(np.std((piv["A3"] - piv["A2"]).to_numpy(), ddof=1)),
        "sd_spec_a6_minus_a2": float(np.std((piv["A6"] - piv["A2"]).to_numpy(), ddof=1)),
        "sd_r_est": float(np.std((piv["A0"] - piv["A4"]).to_numpy(), ddof=1)),
        "sd_r_or": float(np.std((piv["A0"] - piv["A1"]).to_numpy(), ddof=1)),
        "t_multiplier_80pct_power_n128": float(
            stats.t.ppf(0.975, df=WORLDS - 1) + stats.t.ppf(0.80, df=WORLDS - 1)
        ),
        "mde_n128_gap_frame": mde_frame,
        "mde_n128_gap_auth": mde_auth,
        "mde_n256_gap_frame": mde(sd_frame, WORLDS_ESCALATED),
        "mde_n256_gap_auth": mde(sd_auth, WORLDS_ESCALATED),
        "bar": G3C_BAR,
        "aspirational_resolution": G3C_ASPIRATIONAL,
        "meets_bar_gap_frame": bool(mde_frame <= G3C_BAR),
        "meets_bar_gap_auth": bool(mde_auth <= G3C_BAR),
        "meets_aspirational_gap_frame": bool(mde_frame <= G3C_ASPIRATIONAL),
        "meets_aspirational_gap_auth": bool(mde_auth <= G3C_ASPIRATIONAL),
        "escalation": "none" if both_meet else "escalate 128->256 worlds once",
        "degeneracy_note": (
            "Delta1 is an identity at 0 (G2c), so the (Delta0 - Delta1) column is "
            "arithmetically the Delta0 column" if degenerate else ""
        ),
        "seconds": float(time.time() - started),
        "pass": both_meet,
    }


def _between_author_variance(events: list[np.ndarray]) -> float:
    """f8._between_author_variance (f8:~735), on a ragged per-author panel:
    trace of the between-author covariance of each author's own mean event."""
    author_mean = np.stack([vec.mean(axis=0) for vec in events])   # (n, 64)
    return float(np.var(author_mean, axis=0, ddof=1).sum())


def gate_g4c(knobs: dict[str, Any], knob_tag: str) -> dict[str, Any]:
    """Liveness at kappa=0.5 (rule 3), the inverse of M4-F7/F8's inertness test."""
    started = time.time()
    module = f2()
    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    _aid, ctx, _spl, counts, _raw = module.build_layout_common(reference)
    rows = []
    for w in PILOT_WORLDS:
        seed = world_seed_for("pilot", w, knob_tag)
        ch = channels(counts, ctx, knobs, KAPPA, "shared", seed)
        n = len(counts)
        intact = [ch["mean_part"][i][None, :] + ch["ar_part"][i][: counts[i]]
                  + ch["common_part"][i][: counts[i]] + ch["noise_part"][i][: counts[i]]
                  for i in range(n)]
        ar_zeroed = [ch["mean_part"][i][None, :] + ch["common_part"][i][: counts[i]]
                     + ch["noise_part"][i][: counts[i]] for i in range(n)]
        mean_zeroed = [ch["ar_part"][i][: counts[i]] + ch["common_part"][i][: counts[i]]
                       + ch["noise_part"][i][: counts[i]] for i in range(n)]
        v_intact = _between_author_variance(intact)
        v_arz = _between_author_variance(ar_zeroed)
        v_mz = _between_author_variance(mean_zeroed)
        # removal-channel liveness: A0 vs A1 inputs
        a0_a1_max = float(max(np.abs(ch["common_part"][i][: counts[i]]).max()
                              for i in range(n)))
        a0_a1_rms = float(np.sqrt(np.mean(
            np.concatenate([ch["common_part"][i][: counts[i]].ravel() for i in range(n)]) ** 2
        )))
        resp_rms = float(np.sqrt(np.mean(
            np.concatenate([v.ravel() for v in intact]) ** 2
        )))
        rows.append({
            "world": int(w), "world_seed": int(seed),
            "between_author_variance_intact": v_intact,
            "between_author_variance_ar_state_zeroed": v_arz,
            "ratio_ar_state": float(v_intact / v_arz),
            "between_author_variance_author_mean_zeroed": v_mz,
            "ratio_author_mean": float(v_intact / v_mz),
            "removed_common_channel_max_abs": a0_a1_max,
            "removed_common_channel_rms": a0_a1_rms,
            "response_rms": resp_rms,
            "removed_over_response_rms": float(a0_a1_rms / resp_rms),
        })
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "g4c_liveness.csv", index=False)
    ratios_ar = frame["ratio_ar_state"].to_numpy()
    ratios_mu = frame["ratio_author_mean"].to_numpy()
    live_ar = bool(np.all(ratios_ar > 1.0))
    live_removal = bool(np.all(frame["removed_common_channel_max_abs"].to_numpy() > 0.0))
    return {
        "gate": "G4c",
        "description": ("(i) author channel live at kappa=0.5 (between-author "
                        "variance, state intact vs zeroed, > 1 at every pilot world); "
                        "(ii) removal channel live (A0 vs A1 inputs differ); "
                        "(iii) informational: sign of the author-deletion response"),
        "worlds": list(PILOT_WORLDS),
        "per_world": rows,
        "ratio_ar_state_min": float(ratios_ar.min()),
        "ratio_ar_state_max": float(ratios_ar.max()),
        "ratio_ar_state_mean": float(ratios_ar.mean()),
        "ratio_ar_state_gt1_all_worlds": live_ar,
        "ratio_author_mean_min": float(ratios_mu.min()),
        "ratio_author_mean_max": float(ratios_mu.max()),
        "ratio_author_mean_mean": float(ratios_mu.mean()),
        "ratio_author_mean_gt1_all_worlds": bool(np.all(ratios_mu > 1.0)),
        "removal_channel_live": live_removal,
        "removed_over_response_rms_mean": float(
            frame["removed_over_response_rms"].mean()
        ),
        "note": (
            "reading (i) as registered zeroes the AR STATE (the sqrt(1-kappa) term, "
            "f2:195) -- M4-F8's G6 diagnostic re-expressed on f2's generator; the "
            "author-MEAN reading is the channel arms A5/A6 actually delete and is "
            "reported alongside (rule 9)"
        ),
        "seconds": float(time.time() - started),
        "pass": bool(live_ar and live_removal),
    }


def gate_g4c_info() -> dict[str, Any]:
    """Report-only: which kappa did F4 and F5 actually run at? Re-derived from
    their persisted artifacts at artifact precision. No adjudication."""
    out: dict[str, Any] = {
        "gate": "G4c-info",
        "description": ("report-only re-derivation of F4's and F5's kappa facts "
                        "from persisted artifacts; feeds a future retrospective"),
        "adjudicates": "nothing",
    }
    for tag, path in (("F4", F4_OUT), ("F5", F5_OUT)):
        cells = pd.read_csv(path / "cells.csv")
        decision = json.loads((path / "decision.json").read_text(encoding="utf-8"))
        gates = json.loads((path / "gates.json").read_text(encoding="utf-8"))
        by_kappa = (
            cells.groupby("kappa")
            .agg(n_cells=("cell", "count"), worlds=("worlds", "sum"))
            .reset_index()
        )
        entry: dict[str, Any] = {
            "experiment": decision["experiment"],
            "artifact_dir": str(path.relative_to(ROOT)),
            "master_seed": decision.get("master_seed"),
            "worlds_per_cell": decision.get("worlds_per_cell"),
            "draws_per_world": decision.get("draws_per_world"),
            "knob_tag": gates.get("knob_tag"),
            "kappas_present_in_cells_csv": [float(v) for v in by_kappa["kappa"]],
            "cells_per_kappa": {str(float(r.kappa)): int(r.n_cells)
                                for r in by_kappa.itertuples()},
            "world_runs_per_kappa": {str(float(r.kappa)): int(r.worlds)
                                     for r in by_kappa.itertuples()},
            "cell_names": sorted(cells["cell"].astype(str).tolist()),
            "manifest_json_present": (path / "manifest.json").exists(),
        }
        adj = decision["adjudication"]
        entry["lean_rules"] = {
            k: {"rule": str(v.get("rule")), "verdict": v.get("verdict")}
            for k, v in adj.items()
            if isinstance(v, dict) and "rule" in v
        }
        if tag == "F4":
            entry["adjudicated_kappa"] = 1.0
            entry["kappa_0_5_status"] = "registered robustness axis; gates no lean, no pivot"
            entry["kappa_0_5_note_verbatim"] = adj["kappa_0_5_context"]["note"]
            entry["kappa_1_0_fit"] = {
                key: adj["lean_a"][key] for key in adj["lean_a"] if key != "rule"
            } if "lean_a" in adj else {}
            entry["kappa_0_5_fit_point"] = adj["kappa_0_5_context"]["fit_point"]
            entry["holdout_cell"] = adj["lean_c"].get("cell")
        else:
            entry["adjudicated_kappa"] = "both (kappa=1.0 primary; kappa=0.5 is lean_c's own subject)"
            entry["lean_c_kappa_stability"] = {
                k: v for k, v in adj["lean_c"].items() if k in ("rule", "verdict")
            }
            entry["t_large_primary"] = decision.get("t_large_primary")
        out[tag] = entry
    out["pass"] = True
    return out


def gate_g5c(g3c: dict[str, Any]) -> dict[str, Any]:
    """Hygiene + rule 11: every CI clause of the registration checked
    ARITHMETICALLY SATISFIABLE at the pilot sd, before arms."""
    def hw(sd: float, n: int = WORLDS) -> float:
        return float(stats.t.ppf(0.975, df=n - 1) * sd / math.sqrt(n))

    sd = {
        "delta0": g3c["sd_delta0"],
        "gap_frame": g3c["sd_gap_frame"],
        "gap_auth": g3c["sd_gap_auth"],
        "spec_a3": g3c["sd_spec_a3_minus_a2"],
        "spec_a6": g3c["sd_spec_a6_minus_a2"],
        "r_est": g3c["sd_r_est"],
    }
    pilot_point = {
        "delta0": float(np.mean(g3c["pilot_delta0"])),
        "gap_frame": float(np.mean(g3c["pilot_gap_frame"])),
        "gap_auth": float(np.mean(g3c["pilot_gap_auth"])),
    }
    k1b_dec = json.loads((K1B_OUT / "decision.json").read_text(encoding="utf-8"))
    ld = k1b_dec["adjudication"]["L-d"]
    clauses = [
        {
            "clause": "G1c: Delta0 pooled CI (n=128) OVERLAPS F2's kappa=0.5 CI",
            "half_width_at_pilot_sd": hw(sd["delta0"]),
            "satisfiable": True,
            "reason": (
                "an overlap clause is satisfied by any point estimate in "
                f"[{F2_K05_CI[0]} - hw, {F2_K05_CI[1]} + hw]; hw = {hw(sd['delta0'])!r}; "
                "wider CIs make it EASIER, so no sd can make it unsatisfiable"
            ),
        },
        {
            "clause": "L-a'': (Delta0 - Delta1) CI excludes 0",
            "half_width_at_pilot_sd": hw(sd["gap_frame"]),
            "pilot_point": pilot_point["gap_frame"],
            "satisfiable": bool(hw(sd["gap_frame"]) < abs(pilot_point["gap_frame"])),
            "reason": "needs |point| > half-width at n=128",
        },
        {
            "clause": "L-b'': (Delta0 - Delta0') CI excludes 0",
            "half_width_at_pilot_sd": hw(sd["gap_auth"]),
            "pilot_point": pilot_point["gap_auth"],
            "satisfiable": bool(hw(sd["gap_auth"]) < abs(pilot_point["gap_auth"])),
            "reason": "needs |point| > half-width at n=128",
        },
        {
            "clause": f"L-c'': |A3-A2| pooled CI inside +/-{LC_MARGIN!r}",
            "half_width_at_pilot_sd": hw(sd["spec_a3"]),
            "satisfiable": bool(hw(sd["spec_a3"]) < LC_MARGIN),
            "reason": "a CI centred at 0 fits inside the margin iff hw < margin",
        },
        {
            "clause": f"L-c'': |A6-A2| pooled CI inside +/-{LC_MARGIN!r}",
            "half_width_at_pilot_sd": hw(sd["spec_a6"]),
            "satisfiable": bool(hw(sd["spec_a6"]) < LC_MARGIN),
            "reason": "a CI centred at 0 fits inside the margin iff hw < margin",
        },
        {
            "clause": "L-d'': R_est CI excludes 0",
            "half_width_at_pilot_sd": hw(sd["r_est"]),
            "pilot_point": None,
            "satisfiable": None,
            "reason": "filled in from the pilot R_est point below (run_part0)",
        },
        {
            "clause": ("L-e'': pooled (est8 - oracle) CI upper bound < +0.005 under "
                       "reader A', 8 worlds"),
            "k1b_anchor_point": ld["Aprime"]["pooled_mean"],
            "k1b_anchor_ci": [ld["Aprime"]["ci95_low"], ld["Aprime"]["ci95_high"]],
            "k1b_anchor_ci_upper_below_bar": bool(
                ld["Aprime"]["ci95_high"] < LE_CI_UPPER_BAR
            ),
            "satisfiable": bool(ld["Aprime"]["ci95_high"] < LE_CI_UPPER_BAR),
            "reason": ("satisfiable at the anchor's own n=8 and its own dispersion "
                       "(K1b's reader-A' CI upper is far below +0.005)"),
        },
        {
            "clause": f"L-e'': oracle stability between A and A' < {LE_ORACLE_STABILITY}",
            "k1b_anchor_move": ld["oracle_move"],
            "satisfiable": True,
            "reason": "a magnitude clause with no CI; satisfiable by construction",
        },
        {
            "clause": ("G3c: MDE(80%, n=128) <= "
                       f"{G3C_BAR!r} for BOTH gaps"),
            "mde_gap_frame": g3c["mde_n128_gap_frame"],
            "mde_gap_auth": g3c["mde_n128_gap_auth"],
            "satisfiable": bool(
                g3c["mde_n128_gap_frame"] <= G3C_BAR
                and g3c["mde_n128_gap_auth"] <= G3C_BAR
            ),
            "reason": "checked directly at the pilot sd",
        },
        {
            "clause": "G4c: liveness ratio > 1 at every pilot world",
            "satisfiable": True,
            "reason": "no CI; a per-world magnitude clause",
        },
    ]
    unsatisfiable = [c["clause"] for c in clauses if c["satisfiable"] is False]
    return {
        "gate": "G5c",
        "description": "hygiene + rule 11 (arithmetic satisfiability of every CI clause)",
        "master_seed": MASTER_SEED,
        "stage_seed_recipe": (
            "v8.stable_bucket(f'{MASTER_SEED}-{group}-w{world}-{knob_tag}', "
            "salt='m4k1c-world', modulus=2**63-1)"
        ),
        "groups": ["main", "pilot", "g2c", "abs"],
        "background_jobs": 0,
        "monitors": 0,
        "kappa": KAPPA,
        "rule11_pilot_sd": sd,
        "rule11_clauses": clauses,
        "rule11_unsatisfiable_clauses": unsatisfiable,
        "rule11_all_satisfiable": bool(not unsatisfiable),
        "pass": True,
    }


def run_part0(workers: int) -> dict[str, Any]:
    started = time.time()
    knobs, knob_tag = knobs_and_tag()
    OUT.mkdir(parents=True, exist_ok=True)
    g0c = gate_g0c(knobs, knob_tag)
    g1bc = gate_g1bc()
    g2c = gate_g2c(knobs, knob_tag, workers)
    degenerate = not g2c["pass"]
    g3c = gate_g3c(workers, degenerate)
    g4c = gate_g4c(knobs, knob_tag)
    g4c_info = gate_g4c_info()
    g5c = gate_g5c(g3c)
    # the pilot R_est satisfiability line, now that the pilot exists
    piv = pd.read_csv(OUT / "pilot_cells.csv").pivot(
        index="world", columns="arm", values="agreement_mean"
    )
    r_est_pilot = float((piv["A0"] - piv["A4"]).mean())
    hw_r_est = float(stats.t.ppf(0.975, df=WORLDS - 1) * g3c["sd_r_est"] / math.sqrt(WORLDS))
    for clause in g5c["rule11_clauses"]:
        if clause["clause"] == "L-d'': R_est CI excludes 0":
            clause["pilot_point"] = r_est_pilot
            clause["satisfiable"] = bool(hw_r_est < abs(r_est_pilot))
            clause["reason"] = "needs |pilot R_est| > half-width at n=128"
    g5c["rule11_unsatisfiable_clauses"] = [
        c["clause"] for c in g5c["rule11_clauses"] if c["satisfiable"] is False
    ]
    g5c["rule11_all_satisfiable"] = bool(not g5c["rule11_unsatisfiable_clauses"])

    gates = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "leg": "M4-K1c",
        "master_seed": MASTER_SEED,
        "worlds": WORLDS,
        "kappa": KAPPA,
        "knobs": knobs,
        "knob_tag": knob_tag,
        "G0c": g0c, "G1bc": g1bc, "G2c": g2c, "G3c": g3c, "G4c": g4c,
        "G4c-info": g4c_info, "G5c": g5c,
        "part0_all_pass": bool(
            g0c["pass"] and g1bc["pass"] and g2c["pass"] and g3c["pass"] and g4c["pass"]
        ),
        "arms_blocked_by_G2c": bool(degenerate),
        "P4c_fires": bool(degenerate),
        "seconds": float(time.time() - started),
    }
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v.get("pass") for k, v in gates.items() if isinstance(v, dict)},
                     indent=2))
    print(f"G2c verdict={g2c['verdict']} maxDelta1={g2c['max_abs_delta1_remove_common']!r} "
          f"panel={g2c['max_panel_A1_vs_A3_remove_common']!r} "
          f"A5vsA6panel={g2c['max_panel_A5_vs_A6']!r}")
    print(f"G3c mde_frame={g3c['mde_n128_gap_frame']:.8g} mde_auth={g3c['mde_n128_gap_auth']:.8g} "
          f"bar={G3C_BAR}")
    print(f"G4c ratio_ar min={g4c['ratio_ar_state_min']:.6g} "
          f"ratio_mu min={g4c['ratio_author_mean_min']:.6g}")
    print(f"rule11 unsatisfiable={g5c['rule11_unsatisfiable_clauses']}")
    if degenerate:
        print("G2c DEGENERATE -> P4c FIRES -> STOP, NO ARMS.")
    return gates


# ===========================================================================
# Gate G1c -- the replication gate (evaluated on A0/A2 before anything else).
# ===========================================================================

def _paired_world_bootstrap(values: dict[str, np.ndarray],
                            statistic: Callable[[dict[str, np.ndarray]], float],
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
        "sign_rule": f"clean >= {SIGN_CLEAN}/{WORLDS}, qualified >= {SIGN_QUALIFIED}/{WORLDS}, else fail",
    }


def _load_main() -> pd.DataFrame:
    frames = [pd.read_csv(OUT / f) for f in ("arms_a.csv", "arms_b.csv")
              if (OUT / f).exists()]
    return pd.concat(frames, ignore_index=True)


def gate_g1c() -> dict[str, Any]:
    frame = pd.read_csv(OUT / "arms_a.csv")
    piv = frame.pivot(index="world", columns="arm", values="agreement_mean")
    d0 = (piv["A0"] - piv["A2"]).to_numpy()
    summary = _contrast_summary(d0, BOOT_SEEDS["delta0"], "Delta0 = A0 - A2")
    lo, hi = summary["bootstrap"]["ci95_low"], summary["bootstrap"]["ci95_high"]
    overlap_boot = bool(lo <= F2_K05_CI[1] and hi >= F2_K05_CI[0])
    tlo, thi = summary["paired_t"]["ci95_low"], summary["paired_t"]["ci95_high"]
    overlap_t = bool(tlo <= F2_K05_CI[1] and thi >= F2_K05_CI[0])
    gate = {
        "gate": "G1c",
        "description": "replication gate: Delta0 pooled CI must OVERLAP F2's kappa=0.5 CI",
        "f2_ci": list(F2_K05_CI),
        "f2_paired_mean": F2_K05_PAIRED_MEAN,
        "delta0": summary,
        "a0_mean": float(piv["A0"].mean()),
        "a2_mean": float(piv["A2"].mean()),
        "overlap_bootstrap_ci": overlap_boot,
        "overlap_paired_t_ci": overlap_t,
        "readings_agree": bool(overlap_boot == overlap_t),
        "decision_rule": (
            "verdict taken on the registered bootstrap CI; the paired-t CI is a "
            "second reading and any disagreement is disclosed"
        ),
        "pass": overlap_boot,
    }
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    gates["G1c"] = gate
    gates["G1c_timestamp_utc"] = datetime.now(UTC).isoformat()
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: gate[k] for k in
                      ("overlap_bootstrap_ci", "overlap_paired_t_ci", "pass")}, indent=2))
    print(f"Delta0 = {summary['pooled_mean']!r} CI [{lo!r}, {hi!r}] vs F2 {F2_K05_CI}")
    if not overlap_boot:
        print("G1c FAIL -> LEG VOID ON NON-REPLICATION (P1c). STOP.")
    return gate


# ===========================================================================
# Secondary question -- reader A vs A' (frame-refreshed), R-abs, kappa=0.5.
# ===========================================================================

def run_sec_world(world: int, knobs: dict[str, Any], knob_tag: str) -> dict[str, Any]:
    module = k1()
    module.N_ORACLE = SEC_NORM_POOL
    module.KAPPA = KAPPA            # the live knob (K1/K1b ran this reader at 1.0)
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
        met_A = module.reader_metrics(cards_a["A1"], cards_a["A2"])
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
                "world_seed": res["world_seed"], "kappa": KAPPA,
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
    a0, a1, a2, a3 = (piv[c].to_numpy() for c in ("A0", "A1", "A2", "A3"))
    a4, a5, a6 = (piv[c].to_numpy() for c in ("A4", "A5", "A6"))
    a1w, a3w = piv["A1w"].to_numpy(), piv["A3w"].to_numpy()
    d0 = a0 - a2
    d1 = a1 - a3
    d0p = a5 - a6
    gap_frame = d0 - d1
    gap_auth = d0 - d0p
    out: dict[str, Any] = {"arm_means": {c: float(piv[c].mean()) for c in piv.columns}}

    out["delta0"] = _contrast_summary(d0, BOOT_SEEDS["delta0"], "Delta0 = A0 - A2")
    out["delta1"] = _contrast_summary(d1, BOOT_SEEDS["delta1"], "Delta1 = A1 - A3")
    out["delta0_prime"] = _contrast_summary(d0p, BOOT_SEEDS["delta0_prime"],
                                            "Delta0' = A5 - A6")
    out["gap_frame"] = _contrast_summary(gap_frame, BOOT_SEEDS["gap_frame"],
                                         "Delta0 - Delta1")
    out["gap_auth"] = _contrast_summary(gap_auth, BOOT_SEEDS["gap_auth"],
                                        "Delta0 - Delta0'")
    s_frame = _paired_world_bootstrap(
        {"d0": d0, "d1": d1},
        lambda v: float((v["d0"].mean() - v["d1"].mean()) / v["d0"].mean()),
        BOOT_SEEDS["share_frame"],
    )
    s_auth = _paired_world_bootstrap(
        {"d0": d0, "d0p": d0p},
        lambda v: float((v["d0"].mean() - v["d0p"].mean()) / v["d0"].mean()),
        BOOT_SEEDS["share_auth"],
    )
    out["S_frame"] = s_frame
    out["S_auth"] = s_auth
    out["degeneracy"] = {
        "max_abs_delta1": float(np.abs(d1).max()),
        "delta1_is_zero_to_1e-12": bool(np.abs(d1).max() < 1e-12),
        "max_abs_delta1_second_reading": float(np.abs(a1w - a3w).max()),
    }

    la = {
        "lean": "L-a''",
        "rule": "(Delta0 - Delta1) CI excludes 0 AND S_frame >= 0.5",
        "gap": out["gap_frame"]["bootstrap"],
        "share_point": s_frame["point"],
        "share_ci": [s_frame["ci95_low"], s_frame["ci95_high"]],
        "sign_band": out["gap_frame"]["sign_band"],
        "verdict": "HOLD" if (out["gap_frame"]["bootstrap"]["excludes_zero"]
                              and s_frame["point"] >= SHARE_LA) else "MISS",
    }
    out["L-a''"] = la

    lb = {
        "lean": "L-b''",
        "rule": "(Delta0 - Delta0') CI excludes 0 with S_auth > 0",
        "gap": out["gap_auth"]["bootstrap"],
        "share_point": s_auth["point"],
        "share_ci": [s_auth["ci95_low"], s_auth["ci95_high"]],
        "sign_band": out["gap_auth"]["sign_band"],
        "verdict": "HOLD" if (out["gap_auth"]["bootstrap"]["excludes_zero"]
                              and s_auth["point"] > 0.0) else "MISS",
    }
    out["L-b''"] = lb

    spec_a3 = _contrast_summary(a3 - a2, BOOT_SEEDS["spec_a3"], "A3 - A2")
    spec_a6 = _contrast_summary(a6 - a2, BOOT_SEEDS["spec_a6"], "A6 - A2")
    inside_a3 = bool(spec_a3["bootstrap"]["ci95_low"] > -LC_MARGIN
                     and spec_a3["bootstrap"]["ci95_high"] < LC_MARGIN)
    inside_a6 = bool(spec_a6["bootstrap"]["ci95_low"] > -LC_MARGIN
                     and spec_a6["bootstrap"]["ci95_high"] < LC_MARGIN)
    out["L-c''"] = {
        "lean": "L-c''",
        "rule": f"|A3-A2| and |A6-A2| pooled CIs inside +/-{LC_MARGIN!r}",
        "margin": LC_MARGIN,
        "a3_minus_a2": spec_a3,
        "a6_minus_a2": spec_a6,
        "a3_inside_margin": inside_a3,
        "a6_inside_margin": inside_a6,
        "verdict": "HOLD" if (inside_a3 and inside_a6) else "MISS",
    }

    r_or = _contrast_summary(a0 - a1, BOOT_SEEDS["removal"], "R_or = A0 - A1")
    r_est = _contrast_summary(a0 - a4, BOOT_SEEDS["removal"] + 1, "R_est = A0 - A4")
    ratio = _paired_world_bootstrap(
        {"e": a0 - a4, "o": a0 - a1},
        lambda v: float(v["e"].mean() / v["o"].mean()),
        BOOT_SEEDS["removal"] + 2,
    )
    applicable = bool(out["gap_frame"]["bootstrap"]["excludes_zero"])
    out["L-d''"] = {
        "lean": "L-d''",
        "rule": ("R_est CI excludes 0 AND pooled R_est/R_or >= 0.5; INAPPLICABLE "
                 "unless (Delta0-Delta1) CI excludes 0"),
        "applicable": applicable,
        "R_or": r_or,
        "R_est": r_est,
        "ratio_est_over_or": ratio,
        "verdict": (
            "INAPPLICABLE" if not applicable
            else ("HOLD" if (r_est["bootstrap"]["excludes_zero"]
                             and ratio["point"] >= RATIO_LD) else "MISS")
        ),
    }

    out["second_reading"] = {
        "note": ("rule 9: 'K1b's verified exact surgery' names the WHOLE state slot "
                 "(f2:196), which at kappa=0.5 also deletes the author AR state; the "
                 "registered arm is the semantic one (occasion-common channel only). "
                 "This is the literal-K1b reading, computed in full, adjudicating "
                 "nothing."),
        "delta1_wholestate": _contrast_summary(a1w - a3w, BOOT_SEEDS["second_reading"],
                                               "Delta1(whole state) = A1w - A3w"),
        "gap_wholestate": _contrast_summary(d0 - (a1w - a3w),
                                            BOOT_SEEDS["second_reading"] + 1,
                                            "Delta0 - Delta1(whole state)"),
    }
    out["descriptives"] = {
        "author_deletion_response_shared": _contrast_summary(
            a5 - a0, BOOT_SEEDS["second_reading"] + 2, "A5 - A0 (shared, authors deleted)"),
        "author_deletion_response_free": _contrast_summary(
            a6 - a2, BOOT_SEEDS["second_reading"] + 3, "A6 - A2 (free, authors deleted)"),
    }

    # ---- L-e'' (T6'' v2, sign form) ---------------------------------------
    cells = pd.read_csv(OUT / "sec_cells.csv")
    store = np.load(OUT / "sec_probe_correct.npz")
    le: dict[str, Any] = {
        "lean": "L-e''",
        "rule": (f"under reader A', pooled (est8 - oracle) <= 0 with CI upper bound "
                 f"< +{LE_CI_UPPER_BAR}; AND |oracle rank1(A') - oracle rank1(A)| < "
                 f"{LE_ORACLE_STABILITY}"),
        "ci_upper_bar": LE_CI_UPPER_BAR,
        "oracle_stability_bar": LE_ORACLE_STABILITY,
    }
    for reader in ("A", "Aprime"):
        per_world = [
            store[f"{w}|est8|{reader}"].astype(float)
            - store[f"{w}|oracle|{reader}"].astype(float)
            for w in range(SEC_WORLDS)
        ]
        boot = k1()._author_stratified_bootstrap(
            per_world, seed=BOOT_SEEDS["le_A" if reader == "A" else "le_Aprime"]
        )
        le[reader] = boot
    oracle_A = float(cells[cells["arm"] == "oracle"]["rank1_A"].mean())
    oracle_Ap = float(cells[cells["arm"] == "oracle"]["rank1_Aprime"].mean())
    le["oracle_rank1_A"] = oracle_A
    le["oracle_rank1_Aprime"] = oracle_Ap
    le["oracle_move"] = abs(oracle_Ap - oracle_A)
    le["oracle_move_below_bar"] = bool(abs(oracle_Ap - oracle_A) < LE_ORACLE_STABILITY)
    le["est8_rank1_A"] = float(cells[cells["arm"] == "est8"]["rank1_A"].mean())
    le["est8_rank1_Aprime"] = float(cells[cells["arm"] == "est8"]["rank1_Aprime"].mean())
    le["no_profit_under_refreshment"] = bool(le["Aprime"]["pooled_mean"] <= 0.0)
    le["ci_upper_below_bar"] = bool(le["Aprime"]["ci95_high"] < LE_CI_UPPER_BAR)
    le["verdict"] = (
        "HOLD" if (le["no_profit_under_refreshment"] and le["ci_upper_below_bar"]
                   and le["oracle_move_below_bar"]) else "MISS"
    )
    out["L-e''"] = le

    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    p2c_bound = P2C_SHARE_BOUND * out["delta0"]["pooled_mean"]
    out["pivots"] = {
        "P1c": {
            "rule": "G1c fails -> VOID on non-replication",
            "fires": bool(not gates.get("G1c", {}).get("pass", False)),
        },
        "P2c": {
            "rule": ("L-b'' MISS with (Delta0-Delta0') CI upper < 0.25 x Delta0 point "
                     "-> author share bounded below 25% at the live knob"),
            "bound": p2c_bound,
            "gap_auth_ci_high": out["gap_auth"]["bootstrap"]["ci95_high"],
            "fires": bool(lb["verdict"] == "MISS"
                          and out["gap_auth"]["bootstrap"]["ci95_high"] < p2c_bound),
        },
        "P3c": {
            "rule": "L-e'' fails -> T6'' v2 dead; discriminator flagged unsafe",
            "fires": bool(le["verdict"] == "MISS"),
        },
        "P4c": {
            "rule": "G2c degenerate -> STOP (planner defect, no arms)",
            "fires": bool(not gates["G2c"]["pass"]),
        },
    }
    return out


def verdict_slug(adj: dict[str, Any], gates: dict[str, Any]) -> str:
    """Deterministic slug recipe, fixed in code before any arm ran."""
    if not gates["G2c"]["pass"]:
        return ("REGISTERED_FRAME_SHARE_DECOMPOSITION_DEGENERATE_AT_EVERY_KAPPA"
                "__PROVED_FROM_SOURCE_BEFORE_ARMS__P4C_FIRES__NO_ARMS_RUN")
    if not gates.get("G1c", {}).get("pass", False):
        return "LEG_VOID_ON_NON_REPLICATION"
    parts = []
    s_auth = adj["S_auth"]["point"]
    if adj["L-b''"]["verdict"] == "HOLD":
        parts.append(f"AUTHOR_READING_SHARE_{s_auth:.2f}".replace(".", "p")
                     .replace("-", "NEG"))
    else:
        parts.append("NO_AUTHOR_READING_SHARE_AT_THE_LIVE_KNOB")
    parts.append("FRAME_SHARE_IS_UNITY_BY_IDENTITY"
                 if adj["degeneracy"]["delta1_is_zero_to_1e-12"]
                 else f"FRAME_SHARE_{adj['S_frame']['point']:.2f}".replace(".", "p"))
    parts.append("T6dd_V2_HOLDS" if adj["L-e''"]["verdict"] == "HOLD" else "T6dd_V2_MISS")
    if adj["pivots"]["P2c"]["fires"]:
        parts.append("P2C_FIRES")
    return "__".join(parts)


def run_finalize() -> None:
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    if not gates["G2c"]["pass"]:
        decision = {
            "experiment": "M4-K1c_ownership_live_knob",
            "banner": BANNER,
            "tier": "EXPLORATORY",
            "registered_spec": "docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md#M4-K1c",
            "part0_registered_in": (
                "reports/SUICA_M4_K1C_OWNERSHIP_LIVE_KNOB_REPORT.md Part 0 (before arms)"
            ),
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "master_seed": MASTER_SEED,
            "worlds_planned": WORLDS,
            "worlds_run_adjudicated": 0,
            "kappa": KAPPA,
            "knobs": gates["knobs"],
            "knob_tag": gates["knob_tag"],
            "gates": {k: gates[k].get("pass") for k in
                      ("G0c", "G1bc", "G2c", "G3c", "G4c", "G4c-info", "G5c")
                      if k in gates},
            "stopped_at": "G2c",
            "adjudication": {
                "status": "NO ARMS RUN -- registered hard stop at G2c (rule 10)",
                "G2c": gates["G2c"],
                "leans": {name: "NOT ADJUDICATED (leg stopped before arms)"
                          for name in ("L-a''", "L-b''", "L-c''", "L-d''", "L-e''")},
                "pivots": {
                    "P1c": {"rule": "G1c fails -> VOID on non-replication",
                            "fires": False,
                            "note": "G1c never evaluated (needs the 128-world arms)"},
                    "P2c": {"rule": "L-b'' MISS with a bounded author share",
                            "fires": False, "note": "L-b'' never measured"},
                    "P3c": {"rule": "L-e'' fails -> T6'' v2 dead",
                            "fires": False, "note": "L-e'' never measured"},
                    "P4c": {"rule": "G2c degenerate -> STOP (planner defect, no arms)",
                            "fires": True},
                },
            },
            "verdict": verdict_slug({}, gates),
            "label_free": True,
            "claim_boundary": (
                "Synthetic; a source-level structural result about M4-F2's generator "
                "plus Part-0 diagnostics on reserved seeds. Licenses IDT grammar only. "
                "No claim about any corpus, construct, person, or diagnosis."
            ),
        }
        (OUT / "decision.json").write_text(json.dumps(decision, indent=2) + "\n",
                                           encoding="utf-8")
        print("VERDICT:", decision["verdict"])
        return
    adj = adjudicate()
    slug = verdict_slug(adj, gates)
    decision = {
        "experiment": "M4-K1c_ownership_live_knob",
        "banner": BANNER,
        "tier": "EXPLORATORY",
        "registered_spec": "docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md#M4-K1c",
        "part0_registered_in": (
            "reports/SUICA_M4_K1C_OWNERSHIP_LIVE_KNOB_REPORT.md Part 0 (before arms)"
        ),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "worlds": WORLDS,
        "kappa": KAPPA,
        "knobs": gates["knobs"],
        "knob_tag": gates["knob_tag"],
        "gates": {k: gates[k].get("pass") for k in
                  ("G0c", "G1c", "G1bc", "G2c", "G3c", "G4c", "G4c-info", "G5c")
                  if k in gates},
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
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2) + "\n",
                                       encoding="utf-8")
    print(json.dumps({k: v.get("verdict") for k, v in adj.items()
                      if isinstance(v, dict) and "verdict" in v}, indent=2))
    print(json.dumps(adj["pivots"], indent=2))
    print("VERDICT:", slug)


def write_manifest(stage: str, seconds: float, extra: dict[str, Any] | None = None) -> None:
    path = OUT / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
        "leg": "M4-K1c",
        "banner": BANNER,
        "master_seed": MASTER_SEED,
        "worlds": WORLDS,
        "kappa": KAPPA,
        "seed_recipe": (
            "v8.stable_bucket(f'{MASTER_SEED}-{group}-w{world}-{knob_tag}', "
            "salt='m4k1c-world', modulus=2**63-1)"
        ),
        "per_stage_seeds": {
            "main": f"group='main', worlds 0..{WORLDS - 1} (all arms share the world seed)",
            "pilot": f"group='pilot', worlds {list(PILOT_WORLDS)} (reserved, never adjudicated)",
            "g2c": f"group='g2c', worlds {list(G2C_WORLDS)}",
            "abs": f"group='abs', worlds 0..{SEC_WORLDS - 1} (secondary question)",
            "a4_norm_pool": "v8.stable_bucket(f'{world_seed}-normpool', salt='m4k1c-normpool')",
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


def _require_g2c_pass() -> dict[str, Any]:
    gates_path = OUT / "gates.json"
    if not gates_path.exists():
        raise AssertionError("Part 0 gates must run (and be reported) before arms.")
    gates = json.loads(gates_path.read_text(encoding="utf-8"))
    if not gates["G2c"]["pass"]:
        raise AssertionError(
            "G2c returned DEGENERATE: pivot P4c fires -> STOP, no arms may run."
        )
    return gates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=["part0", "arms_a", "gate_g1c", "arms_b", "sec", "finalize"],
        required=True,
    )
    parser.add_argument("--workers", type=int,
                        default=max(2, min(8, (os.cpu_count() or 4) - 2)))
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    for path in (REF_PATH, F1_CALIBRATION, F2_OUT / "decision.json",
                 K1_OUT / "gates.json", K1B_OUT / "decision.json",
                 K1B_OUT / "arms_a.csv", K1B_OUT / "arms_b.csv",
                 F4_OUT / "decision.json", F4_OUT / "cells.csv",
                 F5_OUT / "decision.json", F5_OUT / "cells.csv"):
        if not path.exists():
            raise AssertionError(f"{path} missing (read-only predecessor artifact).")

    started = time.time()
    if args.stage == "part0":
        run_part0(args.workers)
    elif args.stage == "finalize":
        run_finalize()
    else:
        gates = _require_g2c_pass()
        knobs, knob_tag = knobs_and_tag()
        if args.stage == "arms_a":
            frame = run_arms(ARMS_A, tuple(range(WORLDS)), "main", args.workers, "arms_a")
            frame.to_csv(OUT / "arms_a.csv", index=False)
        elif args.stage == "gate_g1c":
            gate_g1c()
        elif args.stage == "arms_b":
            if not gates.get("G1c", {}).get("pass", False):
                raise AssertionError("G1c did not pass: leg VOID on non-replication (P1c).")
            frame = run_arms(ARMS_B, tuple(range(WORLDS)), "main", args.workers, "arms_b")
            frame.to_csv(OUT / "arms_b.csv", index=False)
        elif args.stage == "sec":
            run_sec_stage(knobs, knob_tag)
    write_manifest(args.stage, time.time() - started)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
