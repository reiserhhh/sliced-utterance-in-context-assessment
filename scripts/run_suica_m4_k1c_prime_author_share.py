#!/usr/bin/env python3
"""M4-K1c' -- the author-reading share of the composition effect at the LIVE knob.

Registered spec: docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md section "M4-K1c' --
Author-reading share at the live knob: the non-degenerate remainder of K1c"
(REGISTERED 2026-08-09, BEFORE RUN, commit 9a1d877). Part 0 register-notes
(operationalizations for everything the registration left open, plus the
standing-rule-9 instrument resolutions) are in
reports/SUICA_M4_K1C_PRIME_AUTHOR_SHARE_REPORT.md Part 0, written BEFORE any
main arm stage ran.

===========================================================================
STANDING RULE 12 COMPLIANCE HEADER -- every manipulated object by SOURCE OBJECT
===========================================================================
Generator: f2.generate_world_composed, scripts/run_suica_m4_f2_composition.py:129-198.

  * occasion-common channel   `common_part`
        = sqrt(w_x) * a * (((sqrt(kappa) * shock_x) * g) @ loadings.T)
        the sqrt(kappa) half of the blend at f2:195, whose shock_x is built at
        f2:184-193 from f2.occasion_labels (f2:180, the ONLY consumer of
        occasion_mode) and f2.shock_vector (f2:120-126).
        -> arm A1 subtracts it exactly (ORACLE DE-FRAMING REFERENCE).
        -> arm A4 subtracts an ESTIMATED per-(context,occasion) stand-in for it.
  * author MEAN channel       `mean_part`, f2:178
        = sqrt(w_mu) * a * ((z * g) @ loadings.T)
        -> arms A5 (shared) and A6 (free) subtract it exactly. THIS is the
           "author channel" of Delta0' = A5 - A6.
  * author AR state           `x`, f2:151-177 (drawn f2:172-176, phi f2:171),
        entering the response as ar_part = sqrt(w_x)*a*(((sqrt(1-kappa)*x)*g)@L.T),
        the sqrt(1-kappa) half of the blend at f2:195.
        -> NOT manipulated by any arm of this leg; it is the G4' liveness
           second reading (reported, not adjudicated).
  * design                    `occasion_mode` in {"shared","free"} at f2:180.
        -> A0/A5/A4/A1 are shared; A2/A6 are free.
Nothing in suica_core/ is touched (frozen operators are READ-ONLY).
===========================================================================

Machinery reuse (no reimplementation of existing constructions). Everything is
imported from the K1c script, whose arms A0/A2/A5/A6/A4/A1 and secondary
reader machinery are ALREADY IMPLEMENTED and were never run on an adjudicated
world:
  * channel mirror / arm surgery   k1c.channels, k1c._gen_remove,
        k1c._gen_estimated, k1c.estimated_occasion_norm, k1c.common_vector,
        k1c.ARM_SPEC, k1c.PATCHES, k1c._arm_world
        (scripts/run_suica_m4_k1c_ownership_live_knob.py:186-419)
  * construction diagnostics       k1c._design_independence_report (k1c:552-637),
        k1c._between_author_variance (k1c:814-818)
  * statistics                     k1c._paired_world_bootstrap (k1c:1145-1165),
        k1c._contrast_summary (k1c:1168-1187)
  * secondary reader (T6" v2)      k1c.run_sec_world (k1c:1238-1267), which in
        turn reuses k1.build_abs_world / k1.cards_for_arm / k1.reader_metrics
        and k1._author_stratified_bootstrap
  * world generator / designs /    f2.generate_world_composed, f2.occasion_labels,
    deployed gauge / paired CI     f2.shock_vector, f2.build_layout_common,
                                   f2.run_axis1_world, f2._paired_ci
The ONLY fresh-seed lever is MASTER_SEED (20260812 -> 20260813); the K1c seed
salts are inherited verbatim so that one recipe covers the whole leg.

Stages (foreground, chunked; artifacts under results/m4_k1c_prime_author_share/):
  --stage part0    G0', G2', G3', G4', G5' -> gates.json  (MUST run, and the
                   report's Part 0 MUST be written, before any main arm)
  --stage arms_a   A0 (shared intact) + A2 (free intact), 128 worlds
  --stage gate_g1p the replication gate on Delta0 = A0-A2 (VOID/STOP if it fails)
  --stage arms_b   A5, A6, A4, A1, 128 worlds
  --stage sec      T6" v2 secondary: readers A vs A', 8 worlds, R-abs, kappa=0.5
  --stage finalize lean adjudication + pivots -> decision.json

G2' is a HARD STOP gate (registered P4'): if the A5/A6 author-deletion contrast
is degenerate at the fresh seeds, no arm stage may run.
G1' is a HARD STOP gate (registered P1'): non-replication VOIDs the leg.
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
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"

# --- registered constants (docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md, M4-K1c') ----
MASTER_SEED = 20260813          # the registered fresh seed
WORLDS = 128
KAPPA = 0.5                     # the live-author knob
DRAWS = 20
BOOT_DRAWS = 2000
SEC_WORLDS = 8
SIGN_CLEAN = 104                # clean >= 104/128
SIGN_QUALIFIED = 85             # qualified >= 85/128
L2_MARGIN = 0.004418076848551262    # L-2 equivalence margin (50% of the effect)
RATIO_L3 = 0.5                      # L-3: R_est / R_or >= 0.5
L4_CI_UPPER_BAR = 0.005             # L-4: pooled CI upper bound < +0.005
L4_ORACLE_STABILITY = 0.01          # L-4: oracle stability between A and A'
P2P_SHARE_BOUND = 0.25              # P2': (Delta0-Delta0') CI upper < .25 x Delta0
G2P_RMS_BAR = 1e-6                  # G2': A5 vs A6 panel RMS > 1e-6
G3P_SD_TOLERANCE = 2.0              # G3': fresh pilot sd within 2x of K1c's
G3P_BAR = 0.004418076848551262      # G3': the registered MDE bar

# --- G0' inheritance anchors, quoted from the registration text ---------------
K1C_MDE_GAP_FRAME = 0.0015876092906212693
K1C_MDE_GAP_AUTH = 0.0021362771506247724
K1C_SD_GAP_AUTH = 0.008560686670660837      # K1c's own pilot sd for (Delta0-Delta0')
K1C_RATIO_AR_MIN = 1.0772786802493795
K1C_RATIO_AR_MAX = 1.0860125411681176
K1C_RATIO_MU_MIN = 2.8194500501220903
K1C_RATIO_MU_MAX = 2.865341972610127
K1C_PANEL_A5_VS_A6 = 0.3310376783451957
K1C_COMMON_SHARE = 0.27447485652733755
K1C_G2C_WORLD_FOR_PANEL_ANCHOR = 9302        # the world whose gap is the anchor
F2_K05_CI = (0.004418364530893362, 0.013253942863311687)   # G1' replication target
F2_K05_PAIRED_MEAN = 0.008836153697102524
F2_K05_FREE_MEAN = 0.0005009098594400375
F2_K05_SHARED_MEAN = 0.009337063556542562

# --- Part-0 operationalizations (see report Part 0; fixed BEFORE any arm) -----
PILOT_WORLDS = (9401, 9402)   # fresh reserved 2-world pilot: G2', G3', G4', G5'
SEC_NORM_POOL = 1024          # two disjoint 512-author sub-pools (reader A')
SEC_EST = 8                   # est8
BOOT_SEEDS = {
    "delta0": 20260813001,
    "delta0_prime": 20260813002,
    "gap_auth": 20260813003,
    "share_auth": 20260813004,
    "spec_a6": 20260813005,
    "spec_a5": 20260813006,
    "r_or": 20260813007,
    "r_est": 20260813008,
    "ratio_est_over_or": 20260813009,
    "le_A": 20260813010,
    "le_Aprime": 20260813011,
}

OUT = ROOT / "results" / "m4_k1c_prime_author_share"
F2_OUT = ROOT / "results" / "m4_f2_composition"
K1_OUT = ROOT / "results" / "m4_k1_issuer"
K1C_OUT = ROOT / "results" / "m4_k1c_ownership_live_knob"
F1_OUT = ROOT / "results" / "m4_f1_panel_sizing"
F1_CALIBRATION = F1_OUT / "calibration_record.json"
REF_PATH = F1_OUT / "realtext_panel_reference.json"

ARMS_A = ("A0", "A2")
ARMS_B = ("A5", "A6", "A4", "A1")
ALL_ARMS = ("A0", "A2", "A5", "A6", "A4", "A1")


def _load_script(name: str) -> Any:
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_K1C: Any = None


def k1c() -> Any:
    """The predecessor module, with the ONE fresh-seed lever applied.

    k1c.MASTER_SEED is the single global that enters every world seed
    (k1c.world_seed_for and, inside the worker, f2.MASTER_SEED which
    f2.run_axis1_world:288-291 consumes). Patching it here -- in EVERY process
    that touches the module, parent or ProcessPoolExecutor child -- makes this
    leg's worlds fresh while leaving all constructions byte-identical.
    """
    global _K1C
    if _K1C is None:
        module = _load_script("run_suica_m4_k1c_ownership_live_knob.py")
        module.MASTER_SEED = MASTER_SEED
        assert module.KAPPA == KAPPA
        assert module.WORLDS == WORLDS
        assert module.BOOT_DRAWS == BOOT_DRAWS
        assert module.SIGN_CLEAN == SIGN_CLEAN and module.SIGN_QUALIFIED == SIGN_QUALIFIED
        assert module.SEC_NORM_POOL == SEC_NORM_POOL and module.SEC_EST == SEC_EST
        _K1C = module
    return _K1C


def f2() -> Any:
    return k1c().f2()


def knobs_and_tag() -> tuple[dict[str, Any], str]:
    return k1c().knobs_and_tag()


def world_seed_for(group: str, world: int, knob_tag: str) -> int:
    return k1c().world_seed_for(group, world, knob_tag)


# ===========================================================================
# Arm execution -- k1c.arm_task / k1c._arm_world, verbatim, at the fresh seed.
# ===========================================================================

def _arm_world(task: dict[str, Any]) -> dict[str, Any]:
    return k1c()._arm_world(task)


def run_arms(arms: tuple[str, ...], worlds: tuple[int, ...], group: str,
             workers: int, label: str) -> pd.DataFrame:
    module = k1c()
    knobs, knob_tag = knobs_and_tag()
    tasks = [module.arm_task(a, w, knobs, knob_tag, group) for a in arms for w in worlds]
    started = time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(_arm_world, tasks))
    print(f"[{label}] {len(rows)} gauge runs in {time.time() - started:.0f}s", flush=True)
    return pd.DataFrame(rows)


def read_cells(path: Path) -> pd.DataFrame:
    """Every per-cell CSV in this leg is read with float_precision='round_trip'.

    Register-note (rule 9, instrument convention, fixed BEFORE any main arm):
    pandas 3.0.2's DEFAULT csv float parser does NOT round-trip float64 --
    `to_csv` writes the exact repr but `read_csv` returns a neighbouring double
    (measured here: 1.0772786802493795 -> 1.0772786802493797). Persisted
    artifacts are therefore read with `float_precision='round_trip'`, which
    restores exact round-tripping, so (i) G0''s anchor re-derivation from K1c's
    RAW per-cell rows is bit-exact rather than merely 1e-15-close, and (ii) this
    leg's own pooled statistics are exactly reproducible from its own CSVs.
    """
    return pd.read_csv(path, float_precision="round_trip")


def _mde(sd: float, n: int) -> float:
    """MDE(80% power, alpha=.05, paired t) -- k1c.gate_g3c's own formula."""
    mult = float(stats.t.ppf(0.975, df=n - 1) + stats.t.ppf(0.80, df=n - 1))
    return float(mult * sd / math.sqrt(n))


def _half_width(sd: float, n: int = WORLDS) -> float:
    return float(stats.t.ppf(0.975, df=n - 1) * sd / math.sqrt(n))


# ===========================================================================
# Part 0 gates.
# ===========================================================================

def gate_g0p(knobs: dict[str, Any], knob_tag: str) -> dict[str, Any]:
    """G0' -- inheritance anchors, RE-DERIVED (not read off a summary) from the
    persisted K1c artifacts, plus the F2 kappa=0.5 replication target and the
    panel dims."""
    started = time.time()
    module = f2()
    k1c_gates = json.loads((K1C_OUT / "gates.json").read_text(encoding="utf-8"))
    k1c_dec = json.loads((K1C_OUT / "decision.json").read_text(encoding="utf-8"))

    # (1) both G3c MDEs, recomputed from the raw pilot cells.
    piv = read_cells(K1C_OUT / "pilot_cells.csv").pivot(
        index="world", columns="arm", values="agreement_mean"
    )
    d0 = (piv["A0"] - piv["A2"]).to_numpy()
    d1 = (piv["A1"] - piv["A3"]).to_numpy()
    d0p = (piv["A5"] - piv["A6"]).to_numpy()
    sd_gap_frame = float(np.std(d0 - d1, ddof=1))
    sd_gap_auth = float(np.std(d0 - d0p, ddof=1))
    mde_frame = _mde(sd_gap_frame, WORLDS)
    mde_auth = _mde(sd_gap_auth, WORLDS)

    # (2) the G4c liveness ratios, recomputed from the raw liveness rows.
    live = read_cells(K1C_OUT / "g4c_liveness.csv")
    ar = live["ratio_ar_state"].to_numpy()
    mu = live["ratio_author_mean"].to_numpy()
    common_share = float(live["removed_over_response_rms"].mean())

    # (3) the A5-vs-A6 panel gap, RE-DERIVED from the generator at K1c's own
    #     persisted world seed (a bit-exact reconstruction, not a file read).
    anchor_entry = next(
        e for e in k1c_dec["adjudication"]["G2c"]["per_world_construction"]
        if e["world"] == K1C_G2C_WORLD_FOR_PANEL_ANCHOR
    )
    _aid, ctx, _spl, counts, _raw = module.build_layout_common(
        json.loads(REF_PATH.read_text(encoding="utf-8"))
    )
    redone = k1c()._design_independence_report(
        counts, ctx, knobs, int(anchor_entry["world_seed"])
    )
    panel_gap = float(redone["panel_A5_vs_A6_max_abs"])

    # (4) F2's kappa=0.5 block -- G1's replication target, at artifact precision.
    f2_dec = json.loads((F2_OUT / "decision.json").read_text(encoding="utf-8"))
    k05 = f2_dec["adjudication"]["paired_differences"]["k05"]
    f2_ok = bool(
        k05["kappa"] == KAPPA
        and k05["free_mean"] == F2_K05_FREE_MEAN
        and k05["shared_mean"] == F2_K05_SHARED_MEAN
        and k05["mean"] == F2_K05_PAIRED_MEAN
        and k05["ci95_low"] == F2_K05_CI[0]
        and k05["ci95_high"] == F2_K05_CI[1]
    )

    # (5) panel dims, pinned to K1's (which K1c matched field-by-field).
    k1_g0 = json.loads((K1_OUT / "gates.json").read_text(encoding="utf-8"))["G0"]
    hist = {int(k): int(v) for k, v in sorted(pd.Series(counts).value_counts().items())}
    spec = module.f1().load_spec()
    e1 = module.f1().e1()
    meta = pd.DataFrame({"author_id": _aid, "context": ctx, "split": _spl,
                         "event_count": counts})
    eval_mask = meta["split"].isin(["D1", "D2"]).to_numpy()
    resolved = e1.resolved_contexts(meta.loc[eval_mask], spec.minimum_context_authors)
    retained = int(np.sum(
        eval_mask
        & meta["context"].astype(str).isin(resolved).to_numpy()
        & (meta["event_count"].to_numpy() >= module.MIN_RETAINED_EVENTS)
    ))
    dims = {
        "authors": int(len(_aid)), "events_allocated": int(sum(counts)),
        "multiset": hist, "contexts": sorted(set(ctx)), "retained": retained,
        "matches_k1": {
            "authors": int(len(_aid)) == k1_g0["f2_authors_per_world"],
            "events": int(sum(counts)) == k1_g0["f2_events_allocated_total"],
            "multiset": hist == {int(k): v for k, v
                                 in k1_g0["f2_events_per_author_multiset"].items()},
            "contexts": sorted(set(ctx)) == k1_g0["f2_contexts"],
            "retained": retained == k1_g0["f2_n_retained_by_deployed_gauge"],
        },
    }

    checks = {
        "mde_gap_frame_rederived": mde_frame,
        "mde_gap_frame_persisted": k1c_gates["G3c"]["mde_n128_gap_frame"],
        "mde_gap_frame_registration": K1C_MDE_GAP_FRAME,
        "mde_gap_frame_bit_exact": bool(
            mde_frame == k1c_gates["G3c"]["mde_n128_gap_frame"] == K1C_MDE_GAP_FRAME
        ),
        "mde_gap_auth_rederived": mde_auth,
        "mde_gap_auth_persisted": k1c_gates["G3c"]["mde_n128_gap_auth"],
        "mde_gap_auth_registration": K1C_MDE_GAP_AUTH,
        "mde_gap_auth_bit_exact": bool(
            mde_auth == k1c_gates["G3c"]["mde_n128_gap_auth"] == K1C_MDE_GAP_AUTH
        ),
        "sd_gap_auth_rederived": sd_gap_auth,
        "sd_gap_auth_persisted": k1c_gates["G3c"]["sd_gap_auth"],
        "sd_gap_auth_bit_exact": bool(sd_gap_auth == k1c_gates["G3c"]["sd_gap_auth"]
                                      == K1C_SD_GAP_AUTH),
        "sd_gap_frame_rederived": sd_gap_frame,
        "ratio_ar_min_rederived": float(ar.min()),
        "ratio_ar_max_rederived": float(ar.max()),
        "ratio_ar_bit_exact": bool(float(ar.min()) == K1C_RATIO_AR_MIN
                                   and float(ar.max()) == K1C_RATIO_AR_MAX),
        "ratio_author_mean_min_rederived": float(mu.min()),
        "ratio_author_mean_max_rederived": float(mu.max()),
        "ratio_author_mean_bit_exact": bool(float(mu.min()) == K1C_RATIO_MU_MIN
                                            and float(mu.max()) == K1C_RATIO_MU_MAX),
        "common_share_rederived": common_share,
        "common_share_bit_exact": bool(common_share == K1C_COMMON_SHARE),
        "panel_a5_vs_a6_rederived_from_generator": panel_gap,
        "panel_a5_vs_a6_persisted": anchor_entry["panel_A5_vs_A6_max_abs"],
        "panel_a5_vs_a6_registration": K1C_PANEL_A5_VS_A6,
        "panel_a5_vs_a6_bit_exact": bool(
            panel_gap == anchor_entry["panel_A5_vs_A6_max_abs"] == K1C_PANEL_A5_VS_A6
        ),
        "panel_anchor_world": K1C_G2C_WORLD_FOR_PANEL_ANCHOR,
        "panel_anchor_world_seed": int(anchor_entry["world_seed"]),
    }
    all_exact = bool(
        checks["mde_gap_frame_bit_exact"] and checks["mde_gap_auth_bit_exact"]
        and checks["sd_gap_auth_bit_exact"] and checks["ratio_ar_bit_exact"]
        and checks["ratio_author_mean_bit_exact"] and checks["common_share_bit_exact"]
        and checks["panel_a5_vs_a6_bit_exact"]
    )
    return {
        "gate": "G0'",
        "description": ("inheritance anchors re-derived bit-exactly from K1c's "
                        "persisted RAW artifacts (pilot_cells.csv, g4c_liveness.csv) "
                        "and, for the panel gap, re-run from the generator at K1c's "
                        "own persisted world seed -- not read off any summary"),
        "anchor_source_note": (
            "the registration says 'from results/m4_k1c_ownership_live_knob/"
            "decision.json'; that file carries the A5-vs-A6 panel gap (under "
            "adjudication.G2c) but NOT the G3c MDEs or the G4c ratios, which live "
            "in gates.json in the same directory. Disclosed as a registration-text "
            "inaccuracy and satisfied in the STRONGER form: every anchor recomputed "
            "from raw per-cell data or from the generator, then checked against BOTH "
            "the persisted summary AND the registration text."
        ),
        **checks,
        "f2_kappa05_block": {
            "kappa": k05["kappa"], "free_mean": k05["free_mean"],
            "shared_mean": k05["shared_mean"], "paired_mean": k05["mean"],
            "ci95": [k05["ci95_low"], k05["ci95_high"]],
            "matches_registration": f2_ok,
            "shared_minus_free_identity_gap": abs(
                (k05["shared_mean"] - k05["free_mean"]) - k05["mean"]
            ),
        },
        "dims": dims,
        "knobs": knobs, "knob_tag": knob_tag, "kappa": KAPPA,
        "grain": ("per-world paired design contrasts; 128 worlds as the unit; "
                  "authors nested within world (inherited from K1c's G0c, rule 5)"),
        "seconds": float(time.time() - started),
        "pass": bool(all_exact and f2_ok and all(dims["matches_k1"].values())),
    }


def _a5_a6_panel_report(counts: list[int], contexts: list[str],
                        knobs: dict[str, Any], world_seed: int) -> dict[str, Any]:
    """G2' -- the REGISTERED contrast's non-degeneracy at panel level.

    The registration's bar is an RMS ('A5 vs A6 panel RMS > 1e-6'); K1c measured
    max-abs. Rule 9: the RMS is the primary reading (root-mean-square of the
    elementwise A5-panel minus A6-panel difference over every (author, event,
    dim) entry); max-abs is reported as the second reading. Built on
    k1c.channels (the line-for-line mirror of f2:151-197).
    """
    module = f2()
    resp, ch = {}, {}
    for design in ("shared", "free"):
        resp[design] = module.generate_world_composed(
            counts, contexts, knobs, KAPPA, design, world_seed
        )
        ch[design] = k1c().channels(counts, contexts, knobs, KAPPA, design, world_seed)
    # A5 = shared - mean_part ; A6 = free - mean_part  (source object f2:178)
    pan5 = [vec - ch["shared"]["mean_part"][i][None, :]
            for i, vec in enumerate(resp["shared"])]
    pan6 = [vec - ch["free"]["mean_part"][i][None, :]
            for i, vec in enumerate(resp["free"])]
    diff = np.concatenate([(pan5[i] - pan6[i]).ravel() for i in range(len(pan5))])
    diff02 = np.concatenate([(resp["shared"][i] - resp["free"][i]).ravel()
                             for i in range(len(resp["shared"]))])
    # A0 vs A1 inputs: the common_part actually subtracted by A1 (f2:184-195).
    common = np.concatenate([ch["shared"]["common_part"][i, : counts[i]].ravel()
                             for i in range(len(counts))])
    resp_all = np.concatenate([v.ravel() for v in resp["shared"]])
    return {
        "panel_A5_vs_A6_rms": float(np.sqrt(np.mean(diff**2))),
        "panel_A5_vs_A6_max_abs": float(np.abs(diff).max()),
        "panel_A0_vs_A2_rms": float(np.sqrt(np.mean(diff02**2))),
        "panel_A0_vs_A2_max_abs": float(np.abs(diff02).max()),
        "a0_vs_a1_input_rms": float(np.sqrt(np.mean(common**2))),
        "a0_vs_a1_input_max_abs": float(np.abs(common).max()),
        "a0_vs_a1_inputs_differ": bool(np.abs(common).max() > 0.0),
        "common_over_response_rms": float(
            np.sqrt(np.mean(common**2)) / np.sqrt(np.mean(resp_all**2))
        ),
    }


def gate_g2p(knobs: dict[str, Any], knob_tag: str) -> dict[str, Any]:
    """G2' (rule 10): the REGISTERED contrasts are non-degenerate at fresh seeds.

    The A1 degeneracy identity (Delta1 == 0 at every kappa) is a PROVED fact
    (K1c G2c; IDT appendix E.1) and is CITED, not re-tested -- A3 is not an arm
    of this leg and Delta1 is not a quantity of this leg.
    """
    started = time.time()
    module = f2()
    _aid, ctx, _spl, counts, _raw = module.build_layout_common(
        json.loads(REF_PATH.read_text(encoding="utf-8"))
    )
    per_world = []
    for w in PILOT_WORLDS:
        seed = world_seed_for("pilot", w, knob_tag)
        entry = {"world": int(w), "world_seed": int(seed)}
        entry.update(_a5_a6_panel_report(counts, ctx, knobs, seed))
        per_world.append(entry)
    rms_min = min(e["panel_A5_vs_A6_rms"] for e in per_world)
    inputs_differ = all(e["a0_vs_a1_inputs_differ"] for e in per_world)
    return {
        "gate": "G2'",
        "description": ("rule 10 -- non-degeneracy of the REGISTERED contrasts at "
                        "FRESH seeds: A5 vs A6 panels differ (RMS > 1e-6) at both "
                        "pilot worlds, and A0 vs A1 inputs differ"),
        "worlds": list(PILOT_WORLDS),
        "per_world": per_world,
        "rms_bar": G2P_RMS_BAR,
        "min_panel_A5_vs_A6_rms": rms_min,
        "max_panel_A5_vs_A6_rms": max(e["panel_A5_vs_A6_rms"] for e in per_world),
        "min_panel_A5_vs_A6_max_abs": min(e["panel_A5_vs_A6_max_abs"] for e in per_world),
        "a5_a6_non_degenerate": bool(rms_min > G2P_RMS_BAR),
        "a0_a1_inputs_differ_all_worlds": inputs_differ,
        "a1_degeneracy_identity": (
            "CITED, NOT RE-TESTED: response - common_part is design-invariant at "
            "every kappa in (0,1] (K1c G2c source proof, f2:180/184-193/151-177/"
            "178/195/196/197; IDT appendix E.1). A3 is not an arm of this leg and "
            "Delta1 / S_frame are not quantities of this leg. A1 is retained ONLY "
            "as the ORACLE DE-FRAMING REFERENCE: by that identity its gauge value "
            "IS the no-composition baseline, so R_or = A0 - A1 anchors the repair "
            "ratio."
        ),
        "verdict": "NON_DEGENERATE" if (rms_min > G2P_RMS_BAR and inputs_differ)
                   else "DEGENERATE",
        "consequence": ("arms proceed" if (rms_min > G2P_RMS_BAR and inputs_differ)
                        else "P4' FIRES: STOP, defect, NO ARMS"),
        "seconds": float(time.time() - started),
        "pass": bool(rms_min > G2P_RMS_BAR and inputs_differ),
    }


def gate_g3p(workers: int) -> dict[str, Any]:
    """G3' (power): the inherited MDE stands if the fresh 2-world pilot sd is
    within 2x of K1c's; otherwise recompute and re-check the bar."""
    started = time.time()
    frame = run_arms(ALL_ARMS, PILOT_WORLDS, "pilot", workers, "G3' pilot")
    frame.to_csv(OUT / "pilot_cells.csv", index=False)
    piv = frame.pivot(index="world", columns="arm", values="agreement_mean")
    d0 = (piv["A0"] - piv["A2"]).to_numpy()
    d0p = (piv["A5"] - piv["A6"]).to_numpy()
    gap_auth = d0 - d0p
    sd_fresh = float(np.std(gap_auth, ddof=1))
    sd_fresh_pop = float(np.std(gap_auth, ddof=0))
    ratio = float(sd_fresh / K1C_SD_GAP_AUTH)
    within_two_sided = bool(1.0 / G3P_SD_TOLERANCE <= ratio <= G3P_SD_TOLERANCE)
    within_one_sided = bool(ratio <= G3P_SD_TOLERANCE)
    mde_fresh = _mde(sd_fresh, WORLDS)
    return {
        "gate": "G3'",
        "description": ("inherited MDE for (Delta0-Delta0') at n=128; fresh 2-world "
                        "pilot sd confirmed within 2x of K1c's pilot sd, with the "
                        "fresh-sd MDE recomputed and re-checked unconditionally"),
        "pilot_worlds": list(PILOT_WORLDS),
        "pilot_note": "reserved seeds; excluded from every adjudication",
        "pilot_delta0": [float(v) for v in d0],
        "pilot_delta0_prime": [float(v) for v in d0p],
        "pilot_gap_auth": [float(v) for v in gap_auth],
        "pilot_r_or": [float(v) for v in (piv["A0"] - piv["A1"]).to_numpy()],
        "pilot_r_est": [float(v) for v in (piv["A0"] - piv["A4"]).to_numpy()],
        "pilot_a6_minus_a2": [float(v) for v in (piv["A6"] - piv["A2"]).to_numpy()],
        "inherited_mde_gap_auth": K1C_MDE_GAP_AUTH,
        "k1c_pilot_sd_gap_auth": K1C_SD_GAP_AUTH,
        "fresh_pilot_sd_gap_auth_ddof1": sd_fresh,
        "fresh_pilot_sd_gap_auth_ddof0_second_reading": sd_fresh_pop,
        "sd_ratio_fresh_over_k1c": ratio,
        "within_2x_two_sided_primary": within_two_sided,
        "within_2x_one_sided_power_relevant": within_one_sided,
        "recomputed_mde_at_fresh_sd": mde_fresh,
        "bar": G3P_BAR,
        "recomputed_mde_inside_bar": bool(mde_fresh <= G3P_BAR),
        "inherited_mde_inside_bar": bool(K1C_MDE_GAP_AUTH <= G3P_BAR),
        "controlling_mde": max(K1C_MDE_GAP_AUTH, mde_fresh),
        "controlling_mde_rule": (
            "the LARGER (more conservative) of the inherited n=8 MDE and the "
            "fresh n=2 MDE governs the leg's stated resolution, whichever way the "
            "2x band falls; an n=2 sd may never be used to CLAIM more resolution "
            "than the inherited pilot supports"
        ),
        "sd_other_contrasts_fresh": {
            "delta0": float(np.std(d0, ddof=1)),
            "delta0_prime": float(np.std(d0p, ddof=1)),
            "a6_minus_a2": float(np.std((piv["A6"] - piv["A2"]).to_numpy(), ddof=1)),
            "a5_minus_a0": float(np.std((piv["A5"] - piv["A0"]).to_numpy(), ddof=1)),
            "r_or": float(np.std((piv["A0"] - piv["A1"]).to_numpy(), ddof=1)),
            "r_est": float(np.std((piv["A0"] - piv["A4"]).to_numpy(), ddof=1)),
        },
        "n_pilot_worlds": len(PILOT_WORLDS),
        "sd_caveat": ("an sd from n=2 has 1 degree of freedom; this gate is a "
                      "sanity band on the INHERITED sd (n=8), not an estimate that "
                      "replaces it -- which is exactly why the registration frames "
                      "it as 'within 2x' and keeps the K1c MDE as the anchor"),
        "seconds": float(time.time() - started),
        "pass": bool(mde_fresh <= G3P_BAR or K1C_MDE_GAP_AUTH <= G3P_BAR),
    }


def gate_g4p(knobs: dict[str, Any], knob_tag: str) -> dict[str, Any]:
    """G4' (rule 3): the author-MEAN channel -- the channel A5/A6 delete
    (`mean_part`, f2:178) -- is LIVE at the fresh pilot worlds. The AR-state
    reading and the common-channel share are reported alongside."""
    started = time.time()
    module = f2()
    _aid, ctx, _spl, counts, _raw = module.build_layout_common(
        json.loads(REF_PATH.read_text(encoding="utf-8"))
    )
    bav = k1c()._between_author_variance
    rows = []
    for w in PILOT_WORLDS:
        seed = world_seed_for("pilot", w, knob_tag)
        ch = k1c().channels(counts, ctx, knobs, KAPPA, "shared", seed)
        n = len(counts)
        intact = [ch["mean_part"][i][None, :] + ch["ar_part"][i][: counts[i]]
                  + ch["common_part"][i][: counts[i]] + ch["noise_part"][i][: counts[i]]
                  for i in range(n)]
        ar_zeroed = [ch["mean_part"][i][None, :] + ch["common_part"][i][: counts[i]]
                     + ch["noise_part"][i][: counts[i]] for i in range(n)]
        mean_zeroed = [ch["ar_part"][i][: counts[i]] + ch["common_part"][i][: counts[i]]
                       + ch["noise_part"][i][: counts[i]] for i in range(n)]
        v_intact, v_arz, v_mz = bav(intact), bav(ar_zeroed), bav(mean_zeroed)
        common_rms = float(np.sqrt(np.mean(
            np.concatenate([ch["common_part"][i][: counts[i]].ravel()
                            for i in range(n)]) ** 2
        )))
        resp_rms = float(np.sqrt(np.mean(
            np.concatenate([v.ravel() for v in intact]) ** 2
        )))
        rows.append({
            "world": int(w), "world_seed": int(seed),
            "between_author_variance_intact": v_intact,
            "between_author_variance_author_mean_zeroed": v_mz,
            "ratio_author_mean": float(v_intact / v_mz),
            "between_author_variance_ar_state_zeroed": v_arz,
            "ratio_ar_state": float(v_intact / v_arz),
            "common_channel_rms": common_rms,
            "response_rms": resp_rms,
            "common_over_response_rms": float(common_rms / resp_rms),
        })
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "g4p_liveness.csv", index=False)
    mu = frame["ratio_author_mean"].to_numpy()
    ar = frame["ratio_ar_state"].to_numpy()
    live = bool(np.all(mu > 1.0))
    return {
        "gate": "G4'",
        "description": ("author-MEAN channel liveness (the channel arms A5/A6 delete, "
                        "`mean_part` f2:178): between-author variance intact vs "
                        "author-mean-zeroed, ratio > 1 at every fresh pilot world; "
                        "AR-state ratio and common-channel share reported alongside"),
        "worlds": list(PILOT_WORLDS),
        "per_world": rows,
        "ratio_author_mean_min": float(mu.min()),
        "ratio_author_mean_max": float(mu.max()),
        "ratio_author_mean_gt1_all_worlds": live,
        "ratio_ar_state_min": float(ar.min()),
        "ratio_ar_state_max": float(ar.max()),
        "ratio_ar_state_gt1_all_worlds": bool(np.all(ar > 1.0)),
        "common_over_response_rms_mean": float(frame["common_over_response_rms"].mean()),
        "k1c_inherited_bands": {
            "ratio_author_mean": [K1C_RATIO_MU_MIN, K1C_RATIO_MU_MAX],
            "ratio_ar_state": [K1C_RATIO_AR_MIN, K1C_RATIO_AR_MAX],
            "common_share": K1C_COMMON_SHARE,
        },
        "seconds": float(time.time() - started),
        "pass": live,
    }


def gate_g5p(g3p: dict[str, Any], g2p: dict[str, Any]) -> dict[str, Any]:
    """G5' -- hygiene + rule 11 (arithmetic satisfiability of every CI clause of
    the K1c' registration, at the FRESH pilot sd) + the rule-12 header."""
    sd = g3p["sd_other_contrasts_fresh"]
    point = {
        "delta0": float(np.mean(g3p["pilot_delta0"])),
        "gap_auth": float(np.mean(g3p["pilot_gap_auth"])),
        "r_or": float(np.mean(g3p["pilot_r_or"])),
        "r_est": float(np.mean(g3p["pilot_r_est"])),
        "a6_minus_a2": float(np.mean(g3p["pilot_a6_minus_a2"])),
    }
    hw = {k: _half_width(v) for k, v in sd.items()}
    hw_gap = _half_width(g3p["fresh_pilot_sd_gap_auth_ddof1"])
    clauses = [
        {
            "clause": "G1': Delta0 pooled CI (n=128) OVERLAPS F2's kappa=0.5 CI",
            "half_width_at_fresh_pilot_sd": hw["delta0"],
            "reference": list(F2_K05_CI),
            "satisfiable": True,
            "reason": ("an overlap clause is satisfied by any point in "
                       f"[{F2_K05_CI[0]} - hw, {F2_K05_CI[1]} + hw]; wider CIs make "
                       "it EASIER, so no sd can make it unsatisfiable"),
        },
        {
            "clause": "L-1: (Delta0 - Delta0') pooled CI excludes 0",
            "half_width_at_fresh_pilot_sd": hw_gap,
            "pilot_point": point["gap_auth"],
            "satisfiable": bool(hw_gap < abs(point["gap_auth"])),
            "reason": "needs |point| > half-width at n=128",
        },
        {
            "clause": "L-1: S_auth > 0 (a sign clause on a ratio, no CI)",
            "satisfiable": True,
            "reason": "magnitude/sign clause; no interval to be unsatisfiable",
        },
        {
            "clause": f"L-2: |A6-A2| pooled CI inside +/-{L2_MARGIN!r}",
            "half_width_at_fresh_pilot_sd": hw["a6_minus_a2"],
            "pilot_point": point["a6_minus_a2"],
            "satisfiable": bool(hw["a6_minus_a2"] < L2_MARGIN),
            "reason": "a CI centred at 0 fits inside the margin iff hw < margin",
        },
        {
            "clause": "L-3 applicability: R_or CI excludes 0",
            "half_width_at_fresh_pilot_sd": hw["r_or"],
            "pilot_point": point["r_or"],
            "satisfiable": bool(hw["r_or"] < abs(point["r_or"])),
            "reason": "needs |pilot R_or| > half-width at n=128",
        },
        {
            "clause": "L-3: R_est CI excludes 0",
            "half_width_at_fresh_pilot_sd": hw["r_est"],
            "pilot_point": point["r_est"],
            "satisfiable": bool(hw["r_est"] < abs(point["r_est"])),
            "second_reference_k1c_8world_pilot_point": None,   # filled in run_part0
            "second_reference_satisfiable": None,              # filled in run_part0
            "reason": ("needs |pilot R_est| > half-width at n=128; reported at BOTH "
                       "the fresh n=2 pilot point and K1c's inherited n=8 pilot point, "
                       "because an n=2 point estimate of a small quantity is not a "
                       "reliable basis for declaring a registered clause unreachable"),
        },
        {
            "clause": f"L-3: pooled R_est/R_or >= {RATIO_L3}",
            "pilot_ratio": (point["r_est"] / point["r_or"]) if point["r_or"] else None,
            "satisfiable": True,
            "reason": "magnitude clause on a ratio of pooled means; no interval",
        },
        {
            "clause": (f"L-4: reader-A' pooled (est8 - oracle) CI upper bound < "
                       f"+{L4_CI_UPPER_BAR}, 8 worlds"),
            "k1b_anchor_point": None,
            "satisfiable": None,
            "reason": "filled in from K1b's persisted reader-A' anchor below",
        },
        {
            "clause": f"L-4: oracle stability between A and A' < {L4_ORACLE_STABILITY}",
            "satisfiable": None,
            "reason": "filled in from K1b's persisted oracle move below",
        },
        {
            "clause": f"G2': A5 vs A6 panel RMS > {G2P_RMS_BAR}",
            "measured_min_rms": g2p["min_panel_A5_vs_A6_rms"],
            "satisfiable": True,
            "reason": "per-world magnitude clause; measured directly, no CI",
        },
        {
            "clause": f"G3': MDE(80%, n=128) for (Delta0-Delta0') <= {G3P_BAR!r}",
            "inherited_mde": K1C_MDE_GAP_AUTH,
            "fresh_sd_mde": g3p["recomputed_mde_at_fresh_sd"],
            "satisfiable": bool(g3p["pass"]),
            "reason": "checked directly at both the inherited and the fresh sd",
        },
        {
            "clause": "G4': author-mean liveness ratio > 1 at every fresh pilot world",
            "satisfiable": True,
            "reason": "per-world magnitude clause; no CI",
        },
        {
            "clause": (f"P2': (Delta0-Delta0') CI upper < {P2P_SHARE_BOUND} x Delta0 "
                       "point (the pivot's own arithmetic)"),
            "pilot_ci_upper_estimate": point["gap_auth"] + hw_gap,
            "pilot_bound": P2P_SHARE_BOUND * point["delta0"],
            "satisfiable": bool(point["gap_auth"] + hw_gap
                                < P2P_SHARE_BOUND * point["delta0"]),
            "reason": ("a CONSEQUENCE clause, not a gate: satisfiability is reported "
                       "so the pivot's reachability is on the record before arms"),
        },
        {
            "clause": (f"rule 1 aggregation: signs clean >= {SIGN_CLEAN}/{WORLDS}, "
                       f"qualified >= {SIGN_QUALIFIED}/{WORLDS}"),
            "satisfiable": True,
            "reason": "a counting clause; no interval",
        },
    ]
    return {
        "gate": "G5'",
        "description": "hygiene + rule 11 (satisfiability) + rule 12 (source-object naming)",
        "master_seed": MASTER_SEED,
        "stage_seed_recipe": (
            "v8.stable_bucket(f'{MASTER_SEED}-{group}-w{world}-{knob_tag}', "
            "salt='m4k1c-world', modulus=2**63-1) -- K1c's recipe verbatim; the ONLY "
            "changed input is MASTER_SEED 20260812 -> 20260813"
        ),
        "groups": {"main": f"0..{WORLDS - 1}", "pilot": list(PILOT_WORLDS),
                   "abs": f"0..{SEC_WORLDS - 1}"},
        "background_jobs": 0,
        "monitors": 0,
        "kappa": KAPPA,
        "rule12_source_objects": {
            "occasion_common_channel": ("common_part = sqrt(w_x)*a*(((sqrt(kappa)*"
                                        "shock_x)*g)@loadings.T); shock_x built at "
                                        "f2:184-193 from occasion_labels (f2:180) and "
                                        "shock_vector (f2:120-126); blend split at "
                                        "f2:195; removed exactly by A1, estimated by A4"),
            "author_mean_channel": ("mean_part = sqrt(w_mu)*a*((z*g)@loadings.T), "
                                    "f2:178; removed exactly by A5 (shared) and A6 "
                                    "(free) -- the channel of Delta0'"),
            "author_ar_state": ("x, f2:151-177 (x[:,0] f2:173, recursion f2:175-176, "
                                "phi f2:171), entering as ar_part = the sqrt(1-kappa) "
                                "half of f2:195; NOT manipulated by any arm here"),
            "design": "occasion_mode at f2:180 ('shared' | 'free')",
        },
        "rule11_fresh_pilot_sd": {**sd, "gap_auth": g3p["fresh_pilot_sd_gap_auth_ddof1"]},
        "rule11_fresh_pilot_points": point,
        "rule11_clauses": clauses,
        "pass": True,
    }


def run_part0(workers: int) -> dict[str, Any]:
    started = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    knobs, knob_tag = knobs_and_tag()
    g0p = gate_g0p(knobs, knob_tag)
    g2p = gate_g2p(knobs, knob_tag)
    g3p = gate_g3p(workers)
    g4p = gate_g4p(knobs, knob_tag)
    g5p = gate_g5p(g3p, g2p)

    # K1b's reader-A' anchor closes L-4's two satisfiability clauses.
    k1b_dec = json.loads(
        (ROOT / "results" / "m4_k1b_composition_ownership" / "decision.json")
        .read_text(encoding="utf-8")
    )
    ld = k1b_dec["adjudication"]["L-d"]
    for clause in g5p["rule11_clauses"]:
        if clause["clause"].startswith("L-4: reader-A'"):
            clause["k1b_anchor_point"] = ld["Aprime"]["pooled_mean"]
            clause["k1b_anchor_ci"] = [ld["Aprime"]["ci95_low"], ld["Aprime"]["ci95_high"]]
            clause["satisfiable"] = bool(ld["Aprime"]["ci95_high"] < L4_CI_UPPER_BAR)
            clause["reason"] = ("satisfiable at K1b's own n=8 dispersion: its reader-A' "
                                "CI upper is far below +0.005")
        elif clause["clause"].startswith("L-4: oracle stability"):
            clause["k1b_anchor_move"] = ld["oracle_move"]
            clause["satisfiable"] = bool(ld["oracle_move"] < L4_ORACLE_STABILITY)
            clause["reason"] = "satisfiable at K1b's own measured oracle move"
        elif clause["clause"] == "L-3: R_est CI excludes 0":
            # K1c's inherited 8-world pilot supplies the second reference point.
            k1c_pilot = read_cells(K1C_OUT / "pilot_cells.csv").pivot(
                index="world", columns="arm", values="agreement_mean"
            )
            k1c_r_est = float((k1c_pilot["A0"] - k1c_pilot["A4"]).mean())
            k1c_hw = _half_width(float(np.std(
                (k1c_pilot["A0"] - k1c_pilot["A4"]).to_numpy(), ddof=1)))
            clause["second_reference_k1c_8world_pilot_point"] = k1c_r_est
            clause["second_reference_half_width"] = k1c_hw
            clause["second_reference_satisfiable"] = bool(k1c_hw < abs(k1c_r_est))
    g5p["rule11_unsatisfiable_clauses"] = [
        c["clause"] for c in g5p["rule11_clauses"] if c["satisfiable"] is False
    ]
    g5p["rule11_all_satisfiable"] = bool(not g5p["rule11_unsatisfiable_clauses"])
    g5p["rule11_n_clauses"] = len(g5p["rule11_clauses"])

    gates = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "leg": "M4-K1c'",
        "master_seed": MASTER_SEED,
        "worlds": WORLDS,
        "kappa": KAPPA,
        "knobs": knobs,
        "knob_tag": knob_tag,
        "G0'": g0p, "G2'": g2p, "G3'": g3p, "G4'": g4p, "G5'": g5p,
        "part0_all_pass": bool(g0p["pass"] and g2p["pass"] and g3p["pass"]
                               and g4p["pass"] and g5p["pass"]),
        "arms_blocked_by_G2prime": bool(not g2p["pass"]),
        "P4prime_fires": bool(not g2p["pass"]),
        "seconds": float(time.time() - started),
    }
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v.get("pass") for k, v in gates.items() if isinstance(v, dict)},
                     indent=2))
    print(f"G0' all-anchors-bit-exact={g0p['pass']} "
          f"panel_gap={g0p['panel_a5_vs_a6_rederived_from_generator']!r}")
    print(f"G2' verdict={g2p['verdict']} minRMS={g2p['min_panel_A5_vs_A6_rms']!r}")
    print(f"G3' sd_fresh={g3p['fresh_pilot_sd_gap_auth_ddof1']!r} "
          f"ratio={g3p['sd_ratio_fresh_over_k1c']!r} "
          f"mde_fresh={g3p['recomputed_mde_at_fresh_sd']!r} bar={G3P_BAR}")
    print(f"G4' ratio_mu=[{g4p['ratio_author_mean_min']!r}, "
          f"{g4p['ratio_author_mean_max']!r}] ratio_ar=[{g4p['ratio_ar_state_min']!r}, "
          f"{g4p['ratio_ar_state_max']!r}]")
    print(f"rule11 unsatisfiable={g5p['rule11_unsatisfiable_clauses']} "
          f"of {g5p['rule11_n_clauses']}")
    if not g2p["pass"]:
        print("G2' DEGENERATE -> P4' FIRES -> STOP, NO ARMS.")
    return gates


# ===========================================================================
# G1' -- the replication gate (evaluated on A0/A2 before arms_b).
# ===========================================================================

def gate_g1p() -> dict[str, Any]:
    frame = read_cells(OUT / "arms_a.csv")
    piv = frame.pivot(index="world", columns="arm", values="agreement_mean")
    d0 = (piv["A0"] - piv["A2"]).to_numpy()
    summary = k1c()._contrast_summary(d0, BOOT_SEEDS["delta0"], "Delta0 = A0 - A2")
    lo, hi = summary["bootstrap"]["ci95_low"], summary["bootstrap"]["ci95_high"]
    overlap_boot = bool(lo <= F2_K05_CI[1] and hi >= F2_K05_CI[0])
    tlo, thi = summary["paired_t"]["ci95_low"], summary["paired_t"]["ci95_high"]
    overlap_t = bool(tlo <= F2_K05_CI[1] and thi >= F2_K05_CI[0])
    gate = {
        "gate": "G1'",
        "description": "replication: Delta0 pooled CI must OVERLAP F2's kappa=0.5 CI",
        "f2_ci": list(F2_K05_CI),
        "f2_paired_mean": F2_K05_PAIRED_MEAN,
        "delta0": summary,
        "a0_mean": float(piv["A0"].mean()),
        "a2_mean": float(piv["A2"].mean()),
        "overlap_bootstrap_ci": overlap_boot,
        "overlap_paired_t_ci": overlap_t,
        "readings_agree": bool(overlap_boot == overlap_t),
        "decision_rule": ("verdict on the registered bootstrap CI; the paired-t CI is "
                          "a second reading and any disagreement is disclosed"),
        "pass": overlap_boot,
    }
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    gates["G1'"] = gate
    gates["G1prime_timestamp_utc"] = datetime.now(UTC).isoformat()
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2) + "\n", encoding="utf-8")
    print(f"Delta0 = {summary['pooled_mean']!r} boot CI [{lo!r}, {hi!r}] "
          f"t CI [{tlo!r}, {thi!r}] vs F2 {list(F2_K05_CI)}")
    print(f"overlap_boot={overlap_boot} overlap_t={overlap_t} signs="
          f"{summary['signs_positive']}/{WORLDS} band={summary['sign_band']}")
    if not overlap_boot:
        print("G1' FAIL -> LEG VOID ON NON-REPLICATION (P1'). STOP.")
    return gate


# ===========================================================================
# Secondary -- T6" v2: readers A vs A' (frame-refreshed), R-abs, kappa=0.5.
# ===========================================================================

def run_sec_stage(knobs: dict[str, Any], knob_tag: str) -> None:
    """k1c.run_sec_stage (k1c:1270-1294) with this leg's OUT directory; the
    per-world reader work is k1c.run_sec_world verbatim."""
    module = k1c()
    rows, probes = [], {}
    started = time.time()
    for world in range(SEC_WORLDS):
        res = module.run_sec_world(world, knobs, knob_tag)
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
        print(f"[sec w{world}] A: oracle={res['arms']['oracle']['rank1_A']:.4f} "
              f"est8={res['arms']['est8']['rank1_A']:.4f} | A': "
              f"oracle={res['arms']['oracle']['rank1_Aprime']:.4f} "
              f"est8={res['arms']['est8']['rank1_Aprime']:.4f}", flush=True)
    pd.DataFrame(rows).to_csv(OUT / "sec_cells.csv", index=False)
    np.savez_compressed(OUT / "sec_probe_correct.npz", **probes)
    print(f"[sec] done in {time.time() - started:.0f}s")


# ===========================================================================
# Adjudication.
# ===========================================================================

def adjudicate() -> dict[str, Any]:
    module = k1c()
    frame = pd.concat([read_cells(OUT / f) for f in ("arms_a.csv", "arms_b.csv")],
                      ignore_index=True)
    piv = frame.pivot(index="world", columns="arm", values="agreement_mean")
    a0, a1, a2 = (piv[c].to_numpy() for c in ("A0", "A1", "A2"))
    a4, a5, a6 = (piv[c].to_numpy() for c in ("A4", "A5", "A6"))
    d0 = a0 - a2
    d0p = a5 - a6
    gap_auth = d0 - d0p
    cs = module._contrast_summary
    out: dict[str, Any] = {
        "arm_means": {c: float(piv[c].mean()) for c in piv.columns},
        "n_worlds": int(len(piv)),
    }
    out["delta0"] = cs(d0, BOOT_SEEDS["delta0"], "Delta0 = A0 - A2")
    out["delta0_prime"] = cs(d0p, BOOT_SEEDS["delta0_prime"], "Delta0' = A5 - A6")
    out["gap_auth"] = cs(gap_auth, BOOT_SEEDS["gap_auth"], "Delta0 - Delta0'")
    s_auth = module._paired_world_bootstrap(
        {"d0": d0, "d0p": d0p},
        lambda v: float((v["d0"].mean() - v["d0p"].mean()) / v["d0"].mean()),
        BOOT_SEEDS["share_auth"],
    )
    out["S_auth"] = s_auth

    # ---- L-1 -------------------------------------------------------------
    out["L-1"] = {
        "lean": "L-1", "prior": 0.35,
        "rule": "(Delta0 - Delta0') pooled CI excludes 0 AND S_auth > 0",
        "gap": out["gap_auth"]["bootstrap"],
        "share_point": s_auth["point"],
        "share_ci": [s_auth["ci95_low"], s_auth["ci95_high"]],
        "sign_band": out["gap_auth"]["sign_band"],
        "signs_positive": out["gap_auth"]["signs_positive"],
        "signs_negative": out["gap_auth"]["signs_negative"],
        "verdict": "HOLD" if (out["gap_auth"]["bootstrap"]["excludes_zero"]
                              and s_auth["point"] > 0.0) else "MISS",
    }

    # ---- L-2 -------------------------------------------------------------
    spec_a6 = cs(a6 - a2, BOOT_SEEDS["spec_a6"], "A6 - A2")
    inside = bool(spec_a6["bootstrap"]["ci95_low"] > -L2_MARGIN
                  and spec_a6["bootstrap"]["ci95_high"] < L2_MARGIN)
    out["L-2"] = {
        "lean": "L-2", "prior": 0.70,
        "rule": f"|A6-A2| pooled CI inside +/-{L2_MARGIN!r}",
        "margin": L2_MARGIN,
        "a6_minus_a2": spec_a6,
        "inside_margin": inside,
        "verdict": "HOLD" if inside else "MISS",
    }

    # ---- L-3 -------------------------------------------------------------
    r_or = cs(a0 - a1, BOOT_SEEDS["r_or"], "R_or = A0 - A1")
    r_est = cs(a0 - a4, BOOT_SEEDS["r_est"], "R_est = A0 - A4")
    ratio = module._paired_world_bootstrap(
        {"e": a0 - a4, "o": a0 - a1},
        lambda v: float(v["e"].mean() / v["o"].mean()),
        BOOT_SEEDS["ratio_est_over_or"],
    )
    applicable = bool(r_or["bootstrap"]["excludes_zero"])
    out["L-3"] = {
        "lean": "L-3", "prior": 0.80,
        "rule": (f"R_est CI excludes 0 AND pooled R_est/R_or >= {RATIO_L3}; "
                 "ADJUDICATED ONLY IF R_or CI excludes 0, else INAPPLICABLE"),
        "applicable": applicable,
        "R_or": r_or, "R_est": r_est,
        "ratio_est_over_or": ratio,
        "oracle_reference_note": (
            "A1 is the ORACLE DE-FRAMING REFERENCE: by the proved family lemma "
            "(IDT E.1) its panel is design-invariant, so its gauge value IS the "
            "no-composition baseline and R_or = A0 - A1 is the full de-framing move. "
            "S_frame is NOT a quantity of this leg."
        ),
        "verdict": ("INAPPLICABLE" if not applicable
                    else ("HOLD" if (r_est["bootstrap"]["excludes_zero"]
                                     and ratio["point"] >= RATIO_L3) else "MISS")),
    }

    # ---- descriptives ----------------------------------------------------
    out["descriptives"] = {
        "author_deletion_response_shared": cs(a5 - a0, BOOT_SEEDS["spec_a5"],
                                              "A5 - A0 (shared, author mean deleted)"),
        "author_deletion_response_free": out["L-2"]["a6_minus_a2"],
    }

    # ---- L-4 (T6" v2, sign form) -----------------------------------------
    cells = read_cells(OUT / "sec_cells.csv")
    store = np.load(OUT / "sec_probe_correct.npz")
    le: dict[str, Any] = {
        "lean": "L-4", "prior": 0.80,
        "rule": (f"under reader A', pooled (est8 - oracle) <= 0 with CI upper bound "
                 f"< +{L4_CI_UPPER_BAR}; AND |oracle rank1(A') - oracle rank1(A)| < "
                 f"{L4_ORACLE_STABILITY}"),
        "ci_upper_bar": L4_CI_UPPER_BAR,
        "oracle_stability_bar": L4_ORACLE_STABILITY,
    }
    for reader in ("A", "Aprime"):
        per_world = [store[f"{w}|est8|{reader}"].astype(float)
                     - store[f"{w}|oracle|{reader}"].astype(float)
                     for w in range(SEC_WORLDS)]
        le[reader] = module.k1()._author_stratified_bootstrap(
            per_world, seed=BOOT_SEEDS["le_A" if reader == "A" else "le_Aprime"]
        )
    oracle_A = float(cells[cells["arm"] == "oracle"]["rank1_A"].mean())
    oracle_Ap = float(cells[cells["arm"] == "oracle"]["rank1_Aprime"].mean())
    le["oracle_rank1_A"] = oracle_A
    le["oracle_rank1_Aprime"] = oracle_Ap
    le["oracle_move"] = abs(oracle_Ap - oracle_A)
    le["oracle_move_below_bar"] = bool(abs(oracle_Ap - oracle_A) < L4_ORACLE_STABILITY)
    le["est8_rank1_A"] = float(cells[cells["arm"] == "est8"]["rank1_A"].mean())
    le["est8_rank1_Aprime"] = float(cells[cells["arm"] == "est8"]["rank1_Aprime"].mean())
    le["no_profit_under_refreshment"] = bool(le["Aprime"]["pooled_mean"] <= 0.0)
    le["ci_upper_below_bar"] = bool(le["Aprime"]["ci95_high"] < L4_CI_UPPER_BAR)
    le["verdict"] = ("HOLD" if (le["no_profit_under_refreshment"]
                                and le["ci_upper_below_bar"]
                                and le["oracle_move_below_bar"]) else "MISS")
    out["L-4"] = le

    # ---- pivots ----------------------------------------------------------
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    p2_bound = P2P_SHARE_BOUND * out["delta0"]["pooled_mean"]
    out["pivots"] = {
        "P1'": {"rule": "G1' fails -> VOID on non-replication",
                "fires": bool(not gates.get("G1'", {}).get("pass", False))},
        "P2'": {
            "rule": ("L-1 MISS with (Delta0-Delta0') CI upper < 0.25 x Delta0 point "
                     "-> author share bounded below 25% at the live knob; REGISTERED "
                     "CONSEQUENCE: the retrospective widens WITH the family lemma, "
                     "and the F4/F5 review becomes the next registration "
                     "(planner executes; the executor only reports)"),
            "bound": p2_bound,
            "gap_auth_ci_high": out["gap_auth"]["bootstrap"]["ci95_high"],
            "fires": bool(out["L-1"]["verdict"] == "MISS"
                          and out["gap_auth"]["bootstrap"]["ci95_high"] < p2_bound),
        },
        "P3'": {"rule": "L-4 fails -> T6\" v2 dead; forged-component localization next",
                "fires": bool(le["verdict"] == "MISS")},
        "P4'": {"rule": "G2' fails on A5/A6 at fresh seeds -> STOP, defect, no arms",
                "fires": bool(not gates["G2'"]["pass"])},
    }
    return out


def verdict_slug(adj: dict[str, Any], gates: dict[str, Any]) -> str:
    """Deterministic slug recipe, fixed in code BEFORE any arm ran."""
    if not gates["G2'"]["pass"]:
        return ("REGISTERED_AUTHOR_DELETION_CONTRAST_DEGENERATE_AT_FRESH_SEEDS"
                "__P4PRIME_FIRES__NO_ARMS_RUN")
    if not gates.get("G1'", {}).get("pass", False):
        return "LEG_VOID_ON_NON_REPLICATION__P1PRIME_FIRES"
    parts = []
    share = adj["S_auth"]["point"]
    if adj["L-1"]["verdict"] == "HOLD":
        parts.append(f"AUTHOR_READING_SHARE_{share:.2f}"
                     .replace(".", "p").replace("-", "NEG"))
    else:
        parts.append("NO_AUTHOR_READING_SHARE_AT_THE_LIVE_KNOB")
        if share < 0.0:
            parts.append("AUTHOR_DELETION_ENLARGES_THE_COMPOSITION_EFFECT")
    parts.append("FREE_SIDE_SPECIFIC" if adj["L-2"]["verdict"] == "HOLD"
                 else "FREE_SIDE_NOT_SPECIFIC")
    if adj["L-3"]["verdict"] == "INAPPLICABLE":
        parts.append("DEFRAMING_REPAIR_INAPPLICABLE")
    elif adj["L-3"]["verdict"] == "HOLD":
        parts.append(f"DEFRAMING_REPAIR_DEPLOYABLE_{adj['L-3']['ratio_est_over_or']['point']:.2f}"
                     .replace(".", "p"))
    else:
        parts.append("DEFRAMING_REPAIR_MISS")
    parts.append("T6dd_V2_HOLDS" if adj["L-4"]["verdict"] == "HOLD" else "T6dd_V2_MISS")
    if adj["pivots"]["P2'"]["fires"]:
        parts.append("P2PRIME_FIRES")
    if adj["pivots"]["P3'"]["fires"]:
        parts.append("P3PRIME_FIRES")
    return "__".join(parts)


def run_finalize() -> None:
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    adj = adjudicate()
    slug = verdict_slug(adj, gates)
    decision = {
        "experiment": "M4-K1c_prime_author_share",
        "banner": BANNER,
        "tier": "EXPLORATORY",
        "registered_spec": "docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md#M4-K1c-prime",
        "part0_registered_in": (
            "reports/SUICA_M4_K1C_PRIME_AUTHOR_SHARE_REPORT.md Part 0 (before arms)"
        ),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "worlds": WORLDS,
        "kappa": KAPPA,
        "knobs": gates["knobs"],
        "knob_tag": gates["knob_tag"],
        "gates": {k: gates[k].get("pass") for k in
                  ("G0'", "G1'", "G2'", "G3'", "G4'", "G5'") if k in gates},
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
        "leg": "M4-K1c'",
        "banner": BANNER,
        "master_seed": MASTER_SEED,
        "worlds": WORLDS,
        "kappa": KAPPA,
        "arms": list(ALL_ARMS),
        "seed_recipe": (
            "v8.stable_bucket(f'{MASTER_SEED}-{group}-w{world}-{knob_tag}', "
            "salt='m4k1c-world', modulus=2**63-1) -- K1c's recipe verbatim, "
            "MASTER_SEED 20260813"
        ),
        "per_stage_seeds": {
            "main": f"group='main', worlds 0..{WORLDS - 1} (all arms share the world seed)",
            "pilot": f"group='pilot', worlds {list(PILOT_WORLDS)} (reserved, never adjudicated)",
            "abs": f"group='abs', worlds 0..{SEC_WORLDS - 1} (secondary, T6\" v2)",
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


def _require_g2p_pass() -> dict[str, Any]:
    gates_path = OUT / "gates.json"
    if not gates_path.exists():
        raise AssertionError("Part 0 gates must run (and be reported) before arms.")
    gates = json.loads(gates_path.read_text(encoding="utf-8"))
    if not gates["G2'"]["pass"]:
        raise AssertionError("G2' DEGENERATE: pivot P4' fires -> STOP, no arms may run.")
    return gates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=["part0", "arms_a", "gate_g1p", "arms_b", "sec", "finalize"],
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
                 K1_OUT / "gates.json",
                 K1C_OUT / "decision.json", K1C_OUT / "gates.json",
                 K1C_OUT / "pilot_cells.csv", K1C_OUT / "g4c_liveness.csv",
                 ROOT / "results" / "m4_k1b_composition_ownership" / "decision.json"):
        if not path.exists():
            raise AssertionError(f"{path} missing (read-only predecessor artifact).")

    started = time.time()
    if args.stage == "part0":
        run_part0(args.workers)
    elif args.stage == "finalize":
        run_finalize()
    else:
        gates = _require_g2p_pass()
        knobs, knob_tag = knobs_and_tag()
        if args.stage == "arms_a":
            frame = run_arms(ARMS_A, tuple(range(WORLDS)), "main", args.workers, "arms_a")
            frame.to_csv(OUT / "arms_a.csv", index=False)
        elif args.stage == "gate_g1p":
            gate_g1p()
        elif args.stage == "arms_b":
            if not gates.get("G1'", {}).get("pass", False):
                raise AssertionError("G1' did not pass: leg VOID on non-replication (P1').")
            frame = run_arms(ARMS_B, tuple(range(WORLDS)), "main", args.workers, "arms_b")
            frame.to_csv(OUT / "arms_b.csv", index=False)
        elif args.stage == "sec":
            run_sec_stage(knobs, knob_tag)
    write_manifest(args.stage, time.time() - started)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
