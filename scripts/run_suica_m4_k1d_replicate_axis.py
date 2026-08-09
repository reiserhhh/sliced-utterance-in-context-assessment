#!/usr/bin/env python3
"""M4-K1d -- does the author-axis law survive author deletion? (the F4 re-reading)

Registered spec: docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md section "M4-K1d -- Does
the author-axis law survive author deletion? (the F4 re-reading)" (REGISTERED
2026-08-09, BEFORE RUN, commit 234a4d1). Theory: docs/SUICA_IDENTITY_THEORY_V1.md
dated appendices E (world-family lemma) and F (author content is interference;
F.5 states exactly what this leg decides). Part 0 register-notes are in
reports/SUICA_M4_K1D_REPLICATE_AXIS_REPORT.md, written BEFORE any main arm.

Executor standing: implementation and execution only. Every operationalization
below that the registration left open is a "register-note", fixed and written
to the report before any hypothesis-relevant number existed.

Reuse boundary (registration: "importing F4's cell construction and K1b/K1c''s
deletion surgery ... no new fitter"):
  - scripts/run_suica_m4_f4_author_axis.py (f4()): AUTHOR_MULTS, KAPPAS,
    HOLDOUT_AUTHOR_MULT, DESIGN, DRAWS, WORLDS_PER_CELL, seed_suffix_for_mult,
    cell_summary -- read/called unchanged; its own f3()/f2()/f1() module
    handles are reached THROUGH it so the patched object is the one the engine
    actually calls.
  - scripts/run_suica_m4_f3_composition_scaling.py (via f4().f3()):
    run_sweep_world (the per-world engine) and world_seed_for -- called
    unchanged; only the module-level MASTER_SEED is re-pointed to this leg's
    fresh 20260814 (exactly K1b's own `module.MASTER_SEED = MASTER_SEED`
    idiom, k1b:372).
  - scripts/run_suica_m4_f1_panel_sizing.py (via f4().f1()): fit_axis,
    bootstrap_axis, _log_odds -- THE FITTER, called unchanged. No new fitter.
  - scripts/run_suica_m4_k1b_composition_ownership.py (k1b()): channels --
    the canonical line-for-line mirror of f2:151-197; used in Part 0 to prove
    this script's cheap `author_mean_part` extraction is BIT-IDENTICAL to the
    canonical surgery object (f2:178).
  - scripts/run_suica_m4_f2_composition.py (via f4().f3().f2()):
    generate_world_composed -- the deleted arm patches THIS attribute inside
    the worker and restores it in a finally block (K1b's idiom, k1b:369-388).

Stages (foreground, chunked, resumable; artifacts under
results/m4_k1d_replicate_axis/):
  --stage part0    G0d/G2d/G3d/G4d/G5d + G-info-F5; writes gates.json and the
                   Part-0 economy decision (x32 in/out). Touches the deployed
                   gauge ONLY on reserved pilot worlds 9401-9402.
  --stage arms     the main grid: mults x {intact, deleted} x 8 worlds
                   (--mults selects a subset for chunking). Refuses without a
                   passing Part 0.
  --stage g1d      the replication gate on the intact arm (P1d). Refuses to
                   let holdout/finalize run if it fails.
  --stage holdout  the x32 cell, both arms -- ONLY if Part 0 admitted it.
  --stage finalize fits, paired bootstraps, leans, pivots, decision.json.
"""
from __future__ import annotations

import argparse
import gc
import importlib.util
import json
import math
import os
import resource
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v8_context_relation_field import _orthonormal_loadings  # noqa: E402

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"

# --- this leg's own constants (registration-fixed) --------------------------
MASTER_SEED = 20260814              # fresh, registration-fixed
WORLDS_PER_CELL = 8                 # F4's own grain
PILOT_WORLDS = (9401, 9402)         # RESERVED, disjoint from main worlds 0..7
KAPPA = 1.0                         # F4's own knob
KAPPA_TAG = "k10"
DESIGN = "shared"                   # F4's own design
ARMS = ("intact", "deleted")
BOOT_DRAWS = 2000
L1_BAND = 0.25                      # registered equivalence band on |dgamma|
WALL_BUDGET_S = 45 * 60             # registered leg target

# F4 anchors, quoted from the registration text; G0d re-derives them.
F4_GAMMA = 1.0959430140456936
F4_GAMMA_CI = (0.9843434774823611, 1.2176831424523908)
F4_HOLDOUT_PRED = 0.4012353096433611
F4_HOLDOUT_OBS = 0.38612436657934157
F4_MASTER_SEED = 20260802

# bootstrap seeds (disclosed, fixed before any arm)
BOOT_SEED_MARGINAL = {"intact": 2000, "deleted": 2001}   # 2000 == F4's own k10 seed
BOOT_SEED_PAIRED = 20260814

OUT = ROOT / "results" / "m4_k1d_replicate_axis"
F4_OUT = ROOT / "results" / "m4_f4_author_axis"
F5_OUT = ROOT / "results" / "m4_f5_gauge_validity"

G2D_RMS_BAR = 1e-6

_F4 = None
_K1B = None


def _load_script(name: str) -> Any:
    """F3's disclosed sys.modules-before-exec fix, verbatim (f4:106-121)."""
    path = ROOT / "scripts" / name
    mod_name = name.removesuffix(".py")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


def f4() -> Any:
    global _F4
    if _F4 is None:
        _F4 = _load_script("run_suica_m4_f4_author_axis.py")
    return _F4


def k1b() -> Any:
    global _K1B
    if _K1B is None:
        _K1B = _load_script("run_suica_m4_k1b_composition_ownership.py")
    return _K1B


def read_csv_rt(path: Path) -> pd.DataFrame:
    """Standing convention (this line's execution conventions, 2026-08-09):
    every artifact re-derivation that passes through a CSV parse uses
    float_precision='round_trip'."""
    return pd.read_csv(path, float_precision="round_trip")


# ===========================================================================
# The deletion surgery (rule 12 source-object naming).
#
# The deleted arm removes the AUTHOR-MEAN channel
#     mean_part = sqrt(w_mu) * a * ((z * g) @ loadings.T)          f2:178
# by exact pre-map subtraction, exactly as K1b's A1'/A3' and K1c''s A5/A6 do
# (k1b:256-259). At kappa = 1.0 that IS the entire author channel: the author
# AR state x enters only through blended_x = sqrt(1-kappa)*x + sqrt(kappa)*
# shock_x (f2:195) with coefficient sqrt(1-1.0) = 0 exactly (M4-F7), so
# state_part (f2:196) is pure occasion-common content at this knob and the
# noise term (f2:197) is author-anonymous i.i.d.
#
# `author_mean_part` replays ONLY the draws mean_part needs, in f2's own order
# (f2:151 rng, f2:164 g, f2:165 a, f2:167 loadings, f2:168 z, f2:178) -- a
# memory-bounded extraction, NOT a new construction: Part 0 (G2d) proves it is
# bit-identical (max-abs difference exactly 0.0) to k1b.channels(...)
# ["mean_part"], the canonical line-for-line mirror.
# ===========================================================================

def author_mean_part(counts: list[int], knobs: dict[str, Any], world_seed: int) -> np.ndarray:
    rng = np.random.default_rng(world_seed)                       # f2:151
    k = int(knobs["k"])
    w_mu = float(knobs["w_mu"])
    n = len(counts)
    g = np.linspace(0.85, 0.55, k)                                # f2:164
    a = math.sqrt(2.0 / float(np.sum(g**2)))                      # f2:165
    loadings = _orthonormal_loadings(rng, 64, k)                  # f2:167
    z = rng.normal(size=(n, k))                                   # f2:168
    return math.sqrt(w_mu) * a * ((z * g) @ loadings.T)           # f2:178


# ===========================================================================
# Cells and tasks -- F4's own constructors, this leg's own seed lineage.
# ===========================================================================

def seed_key_for(mult: int, holdout: bool = False) -> str:
    """F4's own seed-suffix constructor with a k1d_ prefix: fresh world seeds
    (MASTER_SEED 20260814) AND a fresh corpus tag, so the split-half /
    transition-null nuisance draws are fresh too, while every downstream
    primitive stays F4's."""
    if holdout:
        return f"k1d_authors_x{f4().HOLDOUT_AUTHOR_MULT}_holdout_{KAPPA_TAG}"
    return f"k1d_{f4().seed_suffix_for_mult(mult)}_{KAPPA_TAG}"


def cell_name(arm: str, mult: int) -> str:
    return f"{arm}_x{mult}"


def build_task(arm: str, mult: int, world: int, knobs: dict[str, Any],
               knob_tag: str, draws: int, holdout: bool = False) -> dict[str, Any]:
    return {
        "cell": cell_name(arm, mult),
        "arm": arm,
        "seed_key": seed_key_for(mult, holdout),
        "axis": "authors",
        "world": int(world),
        "author_mult": int(mult),
        "event_mult": 1,
        "kappa": KAPPA,
        "occasion_mode": DESIGN,
        "knobs": knobs,
        "knob_tag": knob_tag,
        "draws": int(draws),
        "ref_path": str(F4_OUT.parent / "m4_f1_panel_sizing" / "realtext_panel_reference.json"),
        "budget_label": "f3.0",          # F4's own halving budget label
        "master_seed": MASTER_SEED,
    }


def _k1d_world(task: dict[str, Any]) -> dict[str, Any]:
    """One world, one arm. The engine is f3().run_sweep_world, unchanged; the
    deleted arm installs the f2:178 subtraction over f2.generate_world_composed
    for the duration of the call (K1b's idiom, k1b:369-388)."""
    f4m = f4()
    f3m = f4m.f3()
    f2m = f3m.f2()
    f3m.MASTER_SEED = int(task["master_seed"])
    orig = f2m.generate_world_composed
    if task["arm"] == "deleted":
        def _patched(counts, contexts, knobs, kappa, occasion_mode, world_seed):  # noqa: ANN001
            vectors = orig(counts, contexts, knobs, kappa, occasion_mode, world_seed)
            mp = author_mean_part(counts, knobs, world_seed)
            return [vec - mp[i][None, :] for i, vec in enumerate(vectors)]
        f2m.generate_world_composed = _patched
    try:
        row = f3m.run_sweep_world(task)
    finally:
        f2m.generate_world_composed = orig
    row["arm"] = task["arm"]
    row["master_seed"] = int(task["master_seed"])
    row["peak_rss_mb"] = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / (1024.0 * 1024.0)
    row.pop("draw_values", None)
    return row


def run_cells(tasks: list[dict[str, Any]], workers: int, label: str) -> pd.DataFrame:
    by_cell: dict[str, list[dict[str, Any]]] = {}
    for t in tasks:
        by_cell.setdefault(t["cell"], []).append(t)
    frames = []
    for cell, cell_tasks in sorted(by_cell.items()):
        path = OUT / f"cell_{cell}.csv"
        if path.exists():
            print(f"[skip] {cell} exists", flush=True)
            frames.append(read_csv_rt(path))
            continue
        started = time.time()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(_k1d_world, cell_tasks))
        rows = sorted(rows, key=lambda r: r["world"])
        for r in rows:
            print(f"[{cell} w{r['world']}] A {r['agreement_mean']:+.6f} "
                  f"(sd {r['agreement_sd']:.4f}) n_ret {r['n_retained']} "
                  f"{r['seconds']:.0f}s", flush=True)
        frame = pd.DataFrame(rows)
        frame.to_csv(path, index=False)
        print(f"[{label}/{cell}] {len(rows)} gauge runs in {time.time() - started:.1f}s "
              f"-> {path.name}", flush=True)
        frames.append(read_csv_rt(path))
    return pd.concat(frames, ignore_index=True)


def cell_summary(arm: str, mult: int) -> dict[str, Any]:
    """F4's own cell_summary shape (f4:503-528), read with round-trip parsing."""
    frame = read_csv_rt(OUT / f"cell_{cell_name(arm, mult)}.csv")
    frame = frame.sort_values("world")
    values = frame["agreement_mean"].to_numpy(dtype=float)
    mean = float(values.mean())
    se = float(values.std(ddof=1) / math.sqrt(len(values)))
    return {
        "cell": cell_name(arm, mult), "arm": arm,
        "author_mult": int(frame["author_mult"].iloc[0]),
        "event_mult": 1, "kappa": float(frame["kappa"].iloc[0]),
        "worlds": int(len(frame)),
        "agreement_mean": mean, "agreement_se": se,
        "t_stat": float(mean / se) if se > 0 else float("inf"),
        "n_authors_total": int(frame["n_authors_total"].iloc[0]),
        "n_retained": int(frame["n_retained"].iloc[0]),
        "n_retained_constant": bool((frame["n_retained"] == frame["n_retained"].iloc[0]).all()),
        "n_events_total": int(frame["n_events_total"].iloc[0]),
        "d0_eff_rank_M_mean": float(frame["d0_eff_rank_M"].mean()),
        "d0_eff_rank_K_mean": float(frame["d0_eff_rank_K"].mean()),
        "world_seeds": frame["world_seed"].astype("int64").tolist(),
        "world_values": values.tolist(),
    }


# ===========================================================================
# F4's fitter (f1:807-865 / f1:869-908), called unchanged, plus the ONE
# diagnostic the registration's L-3 needs.
# ===========================================================================

def fit_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return f4().f1().fit_axis(rows, "author_mult")


def wrmse(fit: dict[str, Any]) -> float | None:
    """Register-note (rule 9). F4's fitter returns no scalar goodness-of-fit.
    Its fit object DOES return its own regression ingredients: the qualifying
    `points` (mult / agreement_mean / agreement_se), plus slope and intercept.
    The registered "F4's fit diagnostic" is operationalized as that fitter's
    OWN objective value -- the weighted RMS residual of its own WLS, using its
    own delta-method weights copied verbatim from f1:826-841:

        WRMSE = sqrt( sum_j w_j r_j^2 / sum_j w_j ),  r_j = y_j - (b + m x_j)

    No new fit, no new weights, no new points. Lower is better."""
    pts = [p for p in fit.get("points", []) if p["qualifies"]]
    if len(pts) < 3 or "exponent" not in fit:
        return None
    log_odds = f4().f1()._log_odds
    x = np.log10(np.asarray([p["mult"] for p in pts], dtype=float))
    y = np.asarray([log_odds(p["agreement_mean"]) for p in pts], dtype=float)
    dvar = np.asarray(
        [
            (
                p["agreement_se"]
                / (
                    math.log(10.0)
                    * max(p["agreement_mean"], 1e-12)
                    * max(1.0 - p["agreement_mean"], 1e-6)
                )
            )
            ** 2
            for p in pts
        ]
    )
    w = 1.0 / np.maximum(dvar, 1e-12)
    resid = y - (fit["intercept"] + fit["exponent"] * x)
    return float(np.sqrt(float(np.sum(w * resid**2)) / float(np.sum(w))))


def _resampled_rows(rows: list[dict[str, Any]], idx: np.ndarray) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        values = np.asarray(row["world_values"], dtype=float)[idx]
        out.append({
            "cell": row["cell"], "author_mult": row["author_mult"],
            "agreement_mean": float(values.mean()),
            "agreement_se": float(values.std(ddof=1) / math.sqrt(len(values))),
        })
    return out


def ci95(values: list[float]) -> list[float] | None:
    if not values:
        return None
    return [float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))]


def paired_bootstrap(rows_by_arm: dict[str, list[dict[str, Any]]], n_worlds: int,
                     seed: int, draws: int = BOOT_DRAWS) -> dict[str, Any]:
    """Registered aggregation: worlds are the bootstrap unit; both arms share
    the resampled world index vector, which preserves the arm pairing (a cell's
    two arms share a world seed by construction)."""
    rng = np.random.default_rng(seed)
    mults = [r["author_mult"] for r in rows_by_arm["intact"]]
    g_int: list[float] = []
    g_del: list[float] = []
    d_gamma: list[float] = []
    ratios: list[float] = []
    levels: dict[int, list[float]] = {m: [] for m in mults}
    failures = 0
    nonpositive = 0
    for _ in range(draws):
        idx = rng.integers(0, n_worlds, size=n_worlds)
        fi = fit_rows(_resampled_rows(rows_by_arm["intact"], idx))
        fd = fit_rows(_resampled_rows(rows_by_arm["deleted"], idx))
        if fi["status"] == "UNFITTABLE" or fd["status"] == "UNFITTABLE":
            failures += 1
            continue
        if fi["exponent"] <= 0 or fd["exponent"] <= 0:
            nonpositive += 1
        g_int.append(fi["exponent"])
        g_del.append(fd["exponent"])
        d_gamma.append(fd["exponent"] - fi["exponent"])
        wi, wd = wrmse(fi), wrmse(fd)
        if wi is not None and wd is not None and wd > 0:
            ratios.append(wi / wd)
        for ri, rd in zip(rows_by_arm["intact"], rows_by_arm["deleted"]):
            vi = np.asarray(ri["world_values"], dtype=float)[idx]
            vd = np.asarray(rd["world_values"], dtype=float)[idx]
            levels[ri["author_mult"]].append(float((vd - vi).mean()))
    return {
        "draws": draws, "failed": failures, "nonpositive_exponent_draws": nonpositive,
        "gamma_intact_ci95": ci95(g_int), "gamma_deleted_ci95": ci95(g_del),
        "delta_gamma_ci95": ci95(d_gamma),
        "delta_gamma_mean": float(np.mean(d_gamma)) if d_gamma else None,
        "wrmse_ratio_ci95": ci95(ratios),
        "wrmse_ratio_mean": float(np.mean(ratios)) if ratios else None,
        "level_ci95": {int(m): ci95(v) for m, v in levels.items()},
    }


# ===========================================================================
# Part 0.
# ===========================================================================

def knobs_and_tag() -> tuple[dict[str, Any], str]:
    cal = json.loads((ROOT / "results" / "m4_f1_panel_sizing" / "calibration_record.json")
                     .read_text(encoding="utf-8"))
    if cal["status"] != "CALIBRATED":
        raise AssertionError("M4-F1 calibration_record.json is not CALIBRATED.")
    knobs = cal["selected"]["knobs"]
    return knobs, f4().f1().knob_tag(knobs)


def _f4_summary(cell: str, float_precision: str | None) -> dict[str, Any]:
    kw = {} if float_precision is None else {"float_precision": float_precision}
    frame = pd.read_csv(F4_OUT / f"cell_{cell}.csv", **kw)
    values = frame["agreement_mean"].to_numpy(dtype=float)
    mean = float(values.mean())
    se = float(values.std(ddof=1) / math.sqrt(len(values)))
    return {
        "cell": cell, "author_mult": int(frame["author_mult"].iloc[0]),
        "agreement_mean": mean, "agreement_se": se, "world_values": values.tolist(),
        "n_authors_total": int(frame["n_authors_total"].iloc[0]),
        "n_retained": int(frame["n_retained"].iloc[0]),
        "n_events_total": int(frame["n_events_total"].iloc[0]),
        "worlds": int(len(frame)), "seconds_mean": float(frame["seconds"].mean()),
        "seconds_max": float(frame["seconds"].max()),
    }


def gate_g0d() -> dict[str, Any]:
    """Pin F4's cells/dims/fitter and re-verify the cited numbers at full
    precision. Two readings (rule 9): F4's OWN code path (pandas default
    parser -- what F4 actually ran) and the standing round-trip convention."""
    f4m = f4()
    mults = list(f4m.AUTHOR_MULTS)
    cells = [f4m.cell_name_live(m, KAPPA_TAG) for m in mults]
    holdout_cell = f"authors_x{f4m.HOLDOUT_AUTHOR_MULT}_holdout_{f4m.DESIGN}_{KAPPA_TAG}"
    d = json.loads((F4_OUT / "decision.json").read_text(encoding="utf-8"))

    readings: dict[str, Any] = {}
    for label, fp in (("f4_own_path_default_parser", None), ("round_trip", "round_trip")):
        rows = [_f4_summary(c, fp) for c in cells]
        fit = f4m.f1().fit_axis(rows, "author_mult")
        boot = f4m.f1().bootstrap_axis(rows, "author_mult", seed=2000)
        lo32 = fit["intercept"] + fit["exponent"] * math.log10(float(f4m.HOLDOUT_AUTHOR_MULT))
        odds = 10.0 ** lo32
        ho = _f4_summary(holdout_cell, fp)
        readings[label] = {
            "gamma": fit["exponent"], "intercept": fit["intercept"],
            "status": fit["status"], "n_qualifying": fit["n_qualifying"],
            "gamma_ci95": boot["exponent_ci95"],
            "holdout_pred": float(odds / (1.0 + odds)),
            "holdout_obs": ho["agreement_mean"],
            "wrmse": wrmse(fit),
            "bit_exact_vs_registration": {
                "gamma": bool(fit["exponent"] == F4_GAMMA),
                "gamma_ci_lo": bool(boot["exponent_ci95"][0] == F4_GAMMA_CI[0]),
                "gamma_ci_hi": bool(boot["exponent_ci95"][1] == F4_GAMMA_CI[1]),
                "holdout_pred": bool(float(odds / (1.0 + odds)) == F4_HOLDOUT_PRED),
                "holdout_obs": bool(ho["agreement_mean"] == F4_HOLDOUT_OBS),
            },
        }
    # persisted-summary cross-check (independent of any CSV parse)
    persisted = {
        "gamma": d["prediction"]["fit_point"]["k10"]["exponent"],
        "gamma_ci95": d["prediction"]["bootstrap_marginal"]["k10"]["exponent_ci95"],
        "holdout_pred": d["prediction"]["holdout_prediction"]["agreement_pred"],
        "holdout_obs": d["holdout_observed"]["agreement_mean"],
        "master_seed": d["master_seed"], "worlds_per_cell": d["worlds_per_cell"],
        "draws_per_world": d["draws_per_world"],
    }
    persisted_matches_registration = bool(
        persisted["gamma"] == F4_GAMMA
        and tuple(persisted["gamma_ci95"]) == F4_GAMMA_CI
        and persisted["holdout_pred"] == F4_HOLDOUT_PRED
        and persisted["holdout_obs"] == F4_HOLDOUT_OBS
        and persisted["master_seed"] == F4_MASTER_SEED
    )
    own_path = readings["f4_own_path_default_parser"]["bit_exact_vs_registration"]
    rt = readings["round_trip"]
    max_rel = max(
        abs(rt["gamma"] - F4_GAMMA) / abs(F4_GAMMA),
        abs(rt["gamma_ci95"][0] - F4_GAMMA_CI[0]) / abs(F4_GAMMA_CI[0]),
        abs(rt["gamma_ci95"][1] - F4_GAMMA_CI[1]) / abs(F4_GAMMA_CI[1]),
        abs(rt["holdout_pred"] - F4_HOLDOUT_PRED) / abs(F4_HOLDOUT_PRED),
        abs(rt["holdout_obs"] - F4_HOLDOUT_OBS) / abs(F4_HOLDOUT_OBS),
    )
    dims = {
        f"x{r['author_mult']}": {
            "n_authors_total": r["n_authors_total"], "n_retained": r["n_retained"],
            "n_events_total": r["n_events_total"], "worlds": r["worlds"],
            "f4_seconds_per_world_mean": r["seconds_mean"],
            "f4_seconds_per_world_max": r["seconds_max"],
        }
        for r in [_f4_summary(c, "round_trip") for c in cells + [holdout_cell]]
    }
    return {
        "gate": "G0d",
        "description": ("pin F4's cells/dims/fitter; re-verify the cited gamma, CI and "
                        "holdout numbers at full precision"),
        "f4_grid_pinned": mults,
        "f4_cells_pinned": cells,
        "f4_holdout_cell": holdout_cell,
        "f4_fitter": ("f1().fit_axis (scripts/run_suica_m4_f1_panel_sizing.py:807-865, WLS of "
                      "log10-odds on log10(mult), delta-method weights f1:826-841, qualifying "
                      "rule mean>0 and mean-2*se>0) + f1().bootstrap_axis (f1:869-908); called "
                      "unchanged via f4().f1()"),
        "f4_engine": ("f3().run_sweep_world (scripts/run_suica_m4_f3_composition_scaling.py:261), "
                      "seeds via f3().world_seed_for (f3:202, salt 'm4f3-world')"),
        "readings": readings,
        "persisted_summary": persisted,
        "persisted_matches_registration": persisted_matches_registration,
        "round_trip_max_relative_deviation": float(max_rel),
        "dims": dims,
        "pass": bool(persisted_matches_registration and all(own_path.values()) and max_rel < 1e-14),
    }


def gate_g2d(knobs: dict[str, Any], knob_tag: str, mults: list[int]) -> dict[str, Any]:
    """Rule 10 non-degeneracy, per cell, at the RESERVED pilot worlds.

    The deleted arm's panel is the intact panel minus mean_part broadcast over
    each author's events, so the elementwise difference panel IS mean_part and
    its RMS is exact and closed-form -- no gauge run, no full generator needed.
    Also proves `author_mean_part` == k1b.channels(...)['mean_part'] bit-exactly."""
    f4m = f4()
    f3m = f4m.f3()
    f3m.MASTER_SEED = MASTER_SEED
    reference = json.loads((ROOT / "results" / "m4_f1_panel_sizing"
                            / "realtext_panel_reference.json").read_text(encoding="utf-8"))
    per_cell = []
    for mult in mults:
        sk = seed_key_for(mult)
        _aid, _ctx, _spl, counts = f4m.f1().build_layout(reference, mult, 1)
        for world in PILOT_WORLDS:
            ws = f3m.world_seed_for(sk, world, knob_tag)
            mp = author_mean_part(counts, knobs, ws)
            ss = float(np.sum(np.asarray(counts, dtype=float) * np.sum(mp**2, axis=1)))
            n_entries = float(sum(counts) * 64)
            per_cell.append({
                "author_mult": mult, "world": world, "world_seed": int(ws),
                "n_authors": len(counts), "n_events": int(sum(counts)),
                "panel_delta_rms": float(math.sqrt(ss / n_entries)),
                "panel_delta_max_abs": float(np.abs(mp).max()),
            })
    # bit-exactness of the extraction vs the canonical mirror, smallest two cells
    equality = []
    for mult in mults[:2]:
        sk = seed_key_for(mult)
        aid, ctx, _spl, counts = f4m.f1().build_layout(reference, mult, 1)
        ws = f3m.world_seed_for(sk, PILOT_WORLDS[0], knob_tag)
        canonical = k1b().channels(counts, ctx, knobs, KAPPA, DESIGN, ws)["mean_part"]
        mine = author_mean_part(counts, knobs, ws)
        equality.append({
            "author_mult": mult, "world_seed": int(ws),
            "max_abs_difference_vs_k1b_channels": float(np.abs(canonical - mine).max()),
            "shape": list(mine.shape),
        })
        del canonical, mine
        gc.collect()
    rms_min = min(e["panel_delta_rms"] for e in per_cell)
    return {
        "gate": "G2d",
        "rule": f"deleted vs intact panel RMS > {G2D_RMS_BAR} at every grid cell",
        "source_object": ("mean_part = sqrt(w_mu)*a*((z*g)@loadings.T), f2:178; at kappa=1.0 the "
                          "AR term's coefficient sqrt(1-kappa) is exactly 0 in f2:195 (M4-F7), so "
                          "mean_part IS the whole author channel"),
        "per_cell": per_cell,
        "min_panel_delta_rms": rms_min,
        "max_panel_delta_rms": max(e["panel_delta_rms"] for e in per_cell),
        "extraction_equals_k1b_channels": equality,
        "extraction_bit_exact": bool(all(e["max_abs_difference_vs_k1b_channels"] == 0.0
                                         for e in equality)),
        "pass": bool(rms_min > G2D_RMS_BAR
                     and all(e["max_abs_difference_vs_k1b_channels"] == 0.0 for e in equality)),
    }


def gate_g4d(knobs: dict[str, Any], knob_tag: str, pilot_mults: list[int]) -> dict[str, Any]:
    """Rule 3 liveness: mean_part's share of the response RMS at kappa=1.0,
    per pilot world, at both pilot cells. Full generator, run sequentially."""
    f4m = f4()
    f3m = f4m.f3()
    f2m = f3m.f2()
    f3m.MASTER_SEED = MASTER_SEED
    reference = json.loads((ROOT / "results" / "m4_f1_panel_sizing"
                            / "realtext_panel_reference.json").read_text(encoding="utf-8"))
    rows = []
    for mult in pilot_mults:
        sk = seed_key_for(mult)
        _aid, ctx, _spl, counts = f4m.f1().build_layout(reference, mult, 1)
        for world in PILOT_WORLDS:
            ws = f3m.world_seed_for(sk, world, knob_tag)
            resp = f2m.generate_world_composed(counts, ctx, knobs, KAPPA, DESIGN, ws)
            mp = author_mean_part(counts, knobs, ws)
            resp_ss = float(sum(float(np.sum(v**2)) for v in resp))
            n_entries = float(sum(counts) * 64)
            resp_rms = math.sqrt(resp_ss / n_entries)
            mp_ss = float(np.sum(np.asarray(counts, dtype=float) * np.sum(mp**2, axis=1)))
            mp_rms = math.sqrt(mp_ss / n_entries)
            del_rms = math.sqrt(
                float(sum(float(np.sum((v - mp[i][None, :]) ** 2)) for i, v in enumerate(resp)))
                / n_entries
            )
            rows.append({
                "author_mult": mult, "world": world, "world_seed": int(ws),
                "response_rms": resp_rms, "mean_part_rms": mp_rms,
                "mean_part_share_of_response_rms": mp_rms / resp_rms,
                "deleted_panel_rms": del_rms,
                "rms_ratio_intact_over_deleted": resp_rms / del_rms,
            })
            del resp, mp
            gc.collect()
    shares = [r["mean_part_share_of_response_rms"] for r in rows]
    return {
        "gate": "G4d",
        "rule": "mean_part share of response RMS > 0 at every pilot world (rule 3)",
        "per_world": rows,
        "min_share": float(min(shares)), "max_share": float(max(shares)),
        "pass": bool(min(shares) > 0.0),
    }


def gate_g3d(pilot_frame: pd.DataFrame, pilot_mults: list[int]) -> dict[str, Any]:
    """Power (rule 2) + rule 11 satisfiability, from the reserved 2-world pilot
    at the smallest and largest grid cells, both arms.

    Register-note (rule 9, written before any main arm): the pilot has only two
    grid points, so its 2-point log-odds slope
        gamma_2 = [L(A_hi) - L(A_lo)] / log10(hi/lo),  L = f1()._log_odds
    is computed PER WORLD for each arm, and Delta gamma_2 per world is the
    paired quantity whose between-world sd drives every gamma clause. This is a
    CONSERVATIVE proxy for the registered 5-point fit (no averaging over the
    interior of the grid), and the projection to the main design uses
    hw = t_{.975, n-1} * sd / sqrt(n) at n = 8 worlds. All clause directions are
    stated explicitly; one-sided clauses are marked one-sided (defect #15)."""
    from scipy import stats as sstats
    log_odds = f4().f1()._log_odds
    lo, hi = min(pilot_mults), max(pilot_mults)
    span = math.log10(hi / lo)
    piv = pilot_frame.pivot_table(index="world", columns=["arm", "author_mult"],
                                  values="agreement_mean")
    worlds = list(piv.index)
    per_world = []
    for w in worlds:
        gi = (log_odds(piv.loc[w, ("intact", hi)]) - log_odds(piv.loc[w, ("intact", lo)])) / span
        gd = (log_odds(piv.loc[w, ("deleted", hi)]) - log_odds(piv.loc[w, ("deleted", lo)])) / span
        per_world.append({
            "world": int(w), "gamma2_intact": float(gi), "gamma2_deleted": float(gd),
            "delta_gamma2": float(gd - gi),
            "level_lo": float(piv.loc[w, ("deleted", lo)] - piv.loc[w, ("intact", lo)]),
            "level_hi": float(piv.loc[w, ("deleted", hi)] - piv.loc[w, ("intact", hi)]),
        })
    n_pilot = len(per_world)
    n_main = WORLDS_PER_CELL
    tcrit = float(sstats.t.ppf(0.975, n_main - 1))

    def proj(key: str) -> dict[str, Any]:
        vals = np.asarray([p[key] for p in per_world], dtype=float)
        sd = float(vals.std(ddof=1))
        return {"pilot_mean": float(vals.mean()), "pilot_sd": sd,
                "projected_halfwidth_n8": float(tcrit * sd / math.sqrt(n_main)),
                "mde_n8": float(tcrit * sd / math.sqrt(n_main))}

    dg = proj("delta_gamma2")
    gi = proj("gamma2_intact")
    gd = proj("gamma2_deleted")
    lvl_lo = proj("level_lo")
    lvl_hi = proj("level_hi")

    clauses = [
        {"clause": "L-1a: |Delta gamma| bootstrap CI inside +/-0.25",
         "direction": "two-sided EQUIVALENCE band (correct form: an equivalence "
                      "clause is two-sided by construction)",
         "requirement": f"projected halfwidth {dg['projected_halfwidth_n8']!r} < {L1_BAND}",
         "satisfiable": bool(dg["projected_halfwidth_n8"] < L1_BAND)},
        {"clause": "L-1b: gamma_deleted CI overlaps F4's [0.984, 1.218]",
         "direction": "two-sided OVERLAP (non-disjointness); its negation (P2d) is "
                      "the DISJOINT case",
         "requirement": "a CI of the projected halfwidth can both overlap and miss the band",
         "satisfiable": bool(gd["projected_halfwidth_n8"] > 0.0
                             and gd["projected_halfwidth_n8"] < 10.0)},
        {"clause": "G1d: gamma_intact CI overlaps F4's [0.984, 1.218]",
         "direction": "two-sided OVERLAP",
         "requirement": "projected halfwidth finite and > 0",
         "satisfiable": bool(gi["projected_halfwidth_n8"] > 0.0)},
        {"clause": "L-2: per-point level contrast CI LOWER edge > 0",
         "direction": "ONE-SIDED (lower edge strictly above zero) -- stated one-sided "
                      "on purpose (defect #15)",
         "requirement": (f"|pilot level| must exceed the projected halfwidth at at least "
                         f"one pilot point: lo |{lvl_lo['pilot_mean']!r}| vs "
                         f"{lvl_lo['projected_halfwidth_n8']!r}; hi "
                         f"|{lvl_hi['pilot_mean']!r}| vs {lvl_hi['projected_halfwidth_n8']!r}"),
         "satisfiable": bool(abs(lvl_lo["pilot_mean"]) > lvl_lo["projected_halfwidth_n8"]
                             or abs(lvl_hi["pilot_mean"]) > lvl_hi["projected_halfwidth_n8"])},
        {"clause": "L-3: WRMSE ratio (intact/deleted) CI UPPER edge >= 1",
         "direction": "ONE-SIDED (the lean's MISS branch requires the whole CI BELOW 1) -- "
                      "stated one-sided on purpose (defect #15)",
         "requirement": "the pilot cannot bound a 5-point WRMSE (2 points, 2 parameters, "
                        "0 residual dof); satisfiability is structural: with 5 grid points "
                        "and 3 residual dof both branches are reachable",
         "satisfiable": True},
    ]
    return {
        "gate": "G3d",
        "pilot_worlds": list(PILOT_WORLDS), "pilot_cells": [lo, hi],
        "pilot_gauge_runs": int(len(pilot_frame)),
        "n_pilot_worlds": n_pilot, "n_main_worlds": n_main, "t_crit_n8": tcrit,
        "per_world": per_world,
        "delta_gamma2": dg, "gamma2_intact": gi, "gamma2_deleted": gd,
        "level_lo": lvl_lo, "level_hi": lvl_hi,
        "equivalence_band": L1_BAND,
        "band_justification": ("~2x F4's own bootstrap CI half-width "
                               f"({(F4_GAMMA_CI[1] - F4_GAMMA_CI[0]) / 2.0!r})"),
        "clauses": clauses,
        "all_clauses_satisfiable": bool(all(c["satisfiable"] for c in clauses)),
        "pass": bool(dg["projected_halfwidth_n8"] < L1_BAND
                     and all(c["satisfiable"] for c in clauses)),
    }


def gate_info_f5() -> dict[str, Any]:
    """G-info-F5, REPORT-ONLY (no adjudication): what do F5's truth_recovery_*
    correlate against, and is that object common-channel, author, or mixed?"""
    knobs, _ = knobs_and_tag()
    w_mu, w_x, w_e = float(knobs["w_mu"]), float(knobs["w_x"]), float(knobs["w_e"])
    cells = sorted(p.name for p in F5_OUT.glob("cell_*.csv"))
    f5_dec = json.loads((F5_OUT / "decision.json").read_text(encoding="utf-8")) \
        if (F5_OUT / "decision.json").exists() else {}
    return {
        "gate": "G-info-F5",
        "status": "REPORT_ONLY_NO_ADJUDICATION",
        "quantities": {
            "truth_recovery_exact": {
                "defined_at": "scripts/run_suica_m4_f5_gauge_validity.py:494",
                "form": ("module.field_agreement(field_est_full, field_true_exact, weights) -- "
                         "the deployed field functional between the finite-sample ESTIMATED "
                         "field (f5:463-465, built from the actual noisy panel) and a TRUTH "
                         "field built from generate_truth_vectors_exact (f5:225-280)"),
                "truth_object": ("events_true = mean_part + state_part (f5:279); the noise term "
                                 "sqrt(w_e)*sigma_iso*noise is explicitly NOT added"),
                "components": {
                    "mean_part (f5:260)": "AUTHOR content (per-author, event-invariant; f2:178's object)",
                    "state_part (f5:278) via blended_x (f5:277)":
                        ("sqrt(1-kappa)*x + sqrt(kappa)*shock_x: x is the AUTHOR-private AR(1) "
                         "state, shock_x is the OCCASION-COMMON shock from f2().shock_vector "
                         "(f2:121-126) shared by every author on the same (context, occasion)"),
                    "noise": "EXCLUDED",
                },
            },
            "truth_recovery_long": {
                "defined_at": "scripts/run_suica_m4_f5_gauge_validity.py:505",
                "form": ("same functional against generate_truth_vectors_long "
                         "(f5:303-372), t_large occasions per retained author"),
                "truth_object": "events_long = mean_part_chunk + state_part (f5:367), noise-free",
                "components": {
                    "mean_part (f5:331)": ("AUTHOR content, explicitly 'bit-identical to live's "
                                           "own mean_part'"),
                    "x_long (f5:348-352)": ("AUTHOR-private AR(1) state, REDRAWN over t_large with "
                                            "the SAME per-author phi (f5:330)"),
                    "shock_long (f5:354-362)": ("OCCASION-COMMON content: the UNCHANGED "
                                                "f2().shock_vector on the same world_seed, "
                                                "occasions 0..t_large-1 (f5:360)"),
                    "noise": "EXCLUDED (f5:367 comment)",
                },
            },
        },
        "verdict_common_author_or_mixed": "MIXED",
        "derivation": {
            "variance_shares_from_F1_calibration": {"w_mu": w_mu, "w_x": w_x, "w_e": w_e},
            "at_kappa_1.0": {
                "author_mean_share_of_truth_variance": w_mu / (w_mu + w_x),
                "occasion_common_share_of_truth_variance": w_x / (w_mu + w_x),
                "author_ar_share_of_truth_variance": 0.0,
                "note": ("sqrt(1-kappa) = 0 exactly at kappa=1.0 (f5:277), so the AR term "
                         "drops out and the truth object is exactly half AUTHOR content "
                         "(mean_part) and half OCCASION-COMMON content (shock)"),
            },
            "at_kappa_0.5": {
                "author_mean_share_of_truth_variance": w_mu / (w_mu + w_x),
                "author_ar_share_of_truth_variance": (w_x * 0.5) / (w_mu + w_x),
                "occasion_common_share_of_truth_variance": (w_x * 0.5) / (w_mu + w_x),
            },
            "excluded": (f"the isotropic noise channel w_e = {w_e} -- {w_e / (w_mu + w_x + w_e):.0%} "
                         "of the RESPONSE variance is absent from both truth objects"),
        },
        "f5_cells_present": cells,
        "f5_kappas_swept": sorted({("0.5" if "k05" in c else "1.0") for c in cells}),
        "f5_decision_present": bool(f5_dec),
        "no_adjudication": True,
    }


def run_part0(workers: int, draws: int, pilot_only_small: bool) -> dict[str, Any]:
    started = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    knobs, knob_tag = knobs_and_tag()
    f4m = f4()
    mults = list(f4m.AUTHOR_MULTS)

    t0 = time.time()
    g0d = gate_g0d()
    print(f"[part0] G0d {'PASS' if g0d['pass'] else 'FAIL'} ({time.time() - t0:.1f}s)", flush=True)

    t0 = time.time()
    g2d = gate_g2d(knobs, knob_tag, mults)
    print(f"[part0] G2d {'PASS' if g2d['pass'] else 'FAIL'} minRMS="
          f"{g2d['min_panel_delta_rms']!r} ({time.time() - t0:.1f}s)", flush=True)

    pilot_mults = [min(mults)] if pilot_only_small else [min(mults), max(mults)]
    t0 = time.time()
    g4d = gate_g4d(knobs, knob_tag, pilot_mults)
    print(f"[part0] G4d {'PASS' if g4d['pass'] else 'FAIL'} share="
          f"[{g4d['min_share']!r}, {g4d['max_share']!r}] ({time.time() - t0:.1f}s)", flush=True)

    # the registered pilot: 2 worlds x {smallest, largest} x both arms
    t0 = time.time()
    pilot_path = OUT / "pilot_cells.csv"
    if pilot_path.exists():
        pilot = read_csv_rt(pilot_path)
        print("[part0] pilot_cells.csv exists, reusing", flush=True)
    else:
        tasks = [build_task(arm, mult, world, knobs, knob_tag, draws)
                 for mult in pilot_mults for arm in ARMS for world in PILOT_WORLDS]
        for t in tasks:
            t["cell"] = f"pilot_{t['cell']}"
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(_k1d_world, tasks))
        pilot = pd.DataFrame(rows).sort_values(["author_mult", "arm", "world"])
        pilot.to_csv(pilot_path, index=False)
        pilot = read_csv_rt(pilot_path)
    pilot_seconds = time.time() - t0
    for _, r in pilot.iterrows():
        print(f"[pilot x{int(r['author_mult'])} {r['arm']} w{int(r['world'])}] "
              f"A {r['agreement_mean']:+.6f} {r['seconds']:.0f}s", flush=True)

    g3d = gate_g3d(pilot, pilot_mults)
    print(f"[part0] G3d {'PASS' if g3d['pass'] else 'FAIL'} "
          f"hw(dgamma,n8)={g3d['delta_gamma2']['projected_halfwidth_n8']!r} "
          f"({pilot_seconds:.1f}s pilot)", flush=True)

    ginfo = gate_info_f5()

    # ---- economy: stage estimates and the x32 decision (Part 0, never mid-run)
    per_world_s = {int(r["author_mult"]): float(
        pilot.loc[pilot["author_mult"] == r["author_mult"], "seconds"].mean()
    ) for _, r in pilot.iterrows()}
    lo, hi = min(pilot_mults), max(pilot_mults)
    # scaling is linear in author count (F4's own persisted seconds confirm it):
    # calibrate the per-world cost from the pilot's largest cell.
    unit = per_world_s[hi] / hi if hi in per_world_s else per_world_s[lo] / lo
    est = {}
    for m in mults:
        waves = math.ceil(len(ARMS) * WORLDS_PER_CELL / workers)
        est[f"x{m}"] = {"per_world_s": unit * m,
                        "cell_wall_s_est": waves * unit * m}
    arms_est = float(sum(v["cell_wall_s_est"] for v in est.values()))
    ho_mult = f4m.HOLDOUT_AUTHOR_MULT
    ho_waves = math.ceil(len(ARMS) * WORLDS_PER_CELL / max(1, workers // 2))
    holdout_est = ho_waves * unit * ho_mult
    part0_s = time.time() - started
    total_wo = part0_s + arms_est + 60.0
    total_with = total_wo + holdout_est
    include_x32 = bool(total_with < WALL_BUDGET_S)
    peak_by_mult = {int(mm): float(pilot.loc[pilot["author_mult"] == mm, "peak_rss_mb"].max())
                    for mm in sorted(set(pilot["author_mult"]))}
    economy = {
        "rule_as_registered": ("include x32 iff the Part-0 pilot shows the x16 cell's wall-time "
                               "x 2 arms keeps the LEG under budget"),
        "measured_peak_rss_mb_per_worker": peak_by_mult,
        "projected_peak_rss_mb_x32_per_worker": (peak_by_mult.get(hi, 0.0) * 2.0),
        "reading_1_literal_x16_clause": {
            "x16_cell_wall_s_est_2_arms": est[f"x{hi}"]["cell_wall_s_est"] if f"x{hi}" in est else None,
            "leg_wall_budget_s": WALL_BUDGET_S,
            "satisfied": bool(total_wo < WALL_BUDGET_S),
        },
        "reading_2_total_projection": {
            "part0_s_measured": part0_s,
            "arms_wall_s_est": arms_est,
            "finalize_s_allowance": 60.0,
            "holdout_x32_wall_s_est": holdout_est,
            "total_without_x32_s": total_wo,
            "total_with_x32_s": total_with,
        },
        "controlling_reading": ("reading 2 -- the registered clause asks whether the leg stays "
                                "under budget, so the projection that decides it must be the "
                                "TOTAL including the optional cell"),
        "include_x32": include_x32,
        "workers": workers,
        "unit_seconds_per_world_per_author_mult": unit,
        "per_cell_estimates": est,
    }
    print(f"[part0] economy: arms est {arms_est:.0f}s, x32 est {holdout_est:.0f}s, "
          f"total {'with' if include_x32 else 'without'} x32 = "
          f"{(total_with if include_x32 else total_wo):.0f}s -> include_x32={include_x32}",
          flush=True)

    g5d = {
        "gate": "G5d",
        "hygiene": {
            "master_seed": MASTER_SEED,
            "worlds_per_cell": WORLDS_PER_CELL,
            "pilot_worlds_reserved": list(PILOT_WORLDS),
            "draws_per_world": draws,
            "kappa": KAPPA, "design": DESIGN,
            "knobs": knobs, "knob_tag": knob_tag,
            "round_trip_parsing_everywhere": True,
            "background_jobs": 0, "monitors": 0, "smoke_runs": 0,
            "label_free": True, "tier": "EXPLORATORY",
        },
        "rule_12_source_objects": {
            "deleted channel": ("author MEAN `mean_part` = sqrt(w_mu)*a*((z*g)@loadings.T), "
                                "f2:178; removed by exact pre-map subtraction"),
            "author AR channel": ("`x` f2:172-176, entering only via blended_x f2:195 with "
                                  "coefficient sqrt(1-kappa) = 0 at kappa=1.0 (M4-F7) -- nothing "
                                  "to delete at this knob"),
            "occasion-common channel": ("`shock_x` from f2().shock_vector f2:121-126, fed by "
                                        "occasion_labels f2:180 into f2:184-193, blended f2:195, "
                                        "mapped f2:196 -- UNTOUCHED by this leg"),
            "noise channel": "sqrt(w_e)*sigma_iso*noise, f2:177/197 -- UNTOUCHED",
            "grid cells": ("f4().seed_suffix_for_mult / f4().AUTHOR_MULTS / "
                           "f4().HOLDOUT_AUTHOR_MULT, F4's own constructors"),
            "fitter": "f1().fit_axis + f1().bootstrap_axis, F4's own, unchanged",
        },
        "grain_rule_5": ("worlds are the bootstrap unit (8 per cell); arms paired within world by "
                         "construction (identical seed_key/world/knob_tag -> identical world_seed "
                         "and corpus); per-point sign counts over the 8 worlds"),
        "pass": True,
    }

    gates = {
        "leg": "M4-K1d",
        "banner": BANNER,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "G0d": g0d, "G2d": g2d, "G3d": g3d, "G4d": g4d, "G5d": g5d,
        "G_info_F5": ginfo,
        "economy": economy,
        "part0_seconds": part0_s,
        "part0_all_pass": bool(g0d["pass"] and g2d["pass"] and g3d["pass"]
                               and g4d["pass"] and g5d["pass"]),
    }
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n",
                                    encoding="utf-8")
    print(json.dumps({k: v.get("pass") for k, v in gates.items()
                      if isinstance(v, dict) and "pass" in v}, indent=2))
    if not (g2d["pass"] and g4d["pass"]):
        raise AssertionError(
            "P3d FIRES: G2d/G4d failed -- the deletion is inert at this knob. STOP, defect. "
            "See results/m4_k1d_replicate_axis/gates.json."
        )
    if not gates["part0_all_pass"]:
        raise AssertionError("Part 0 gate(s) failed; see gates.json.")
    return gates


def _require_part0() -> dict[str, Any]:
    path = OUT / "gates.json"
    if not path.exists():
        raise AssertionError("Part 0 has not run: gates.json missing.")
    gates = json.loads(path.read_text(encoding="utf-8"))
    if not gates.get("part0_all_pass"):
        raise AssertionError("Part 0 did not pass; no arm may run.")
    return gates


# ===========================================================================
# G1d -- the replication gate (P1d), evaluated on the intact arm after the
# main grid and BEFORE the holdout / finalize stages.
# ===========================================================================

def run_g1d(mults: list[int]) -> dict[str, Any]:
    rows = [cell_summary("intact", m) for m in mults]
    fit = fit_rows(rows)
    boot = f4().f1().bootstrap_axis(rows, "author_mult", seed=BOOT_SEED_MARGINAL["intact"])
    ci = boot["exponent_ci95"]
    overlaps = bool(ci is not None and ci[0] <= F4_GAMMA_CI[1] and ci[1] >= F4_GAMMA_CI[0])
    out = {
        "gate": "G1d",
        "rule": "intact-arm fitted gamma CI (fresh seeds) overlaps F4's [0.984, 1.218]",
        "f4_band": list(F4_GAMMA_CI),
        "gamma_intact_point": fit.get("exponent"),
        "gamma_intact_ci95": ci,
        "fit_status": fit.get("status"), "n_qualifying": fit.get("n_qualifying"),
        "overlap": overlaps,
        "overlap_interval": ([max(ci[0], F4_GAMMA_CI[0]), min(ci[1], F4_GAMMA_CI[1])]
                             if overlaps else None),
        "pass": overlaps,
    }
    path = OUT / "gates.json"
    gates = json.loads(path.read_text(encoding="utf-8"))
    gates["G1d"] = out
    gates["G1d_timestamp_utc"] = datetime.now(UTC).isoformat()
    path.write_text(json.dumps(gates, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, default=str))
    if not overlaps:
        raise AssertionError(
            "P1d FIRES: G1d failed -- F4's author-axis law does NOT reproduce at fresh seeds. "
            "The leg is VOID on non-replication. Write the void outcome; do not proceed."
        )
    return out


def _require_g1d() -> None:
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    if "G1d" not in gates:
        raise AssertionError("G1d has not been evaluated; run --stage g1d first.")
    if not gates["G1d"]["pass"]:
        raise AssertionError("G1d FAILED (P1d): the leg is VOID; no further stage may run.")


# ===========================================================================
# Finalize.
# ===========================================================================

def run_finalize(mults: list[int], include_x32: bool) -> dict[str, Any]:
    _require_g1d()
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    rows_by_arm = {arm: [cell_summary(arm, m) for m in mults] for arm in ARMS}

    fits, boots, wr = {}, {}, {}
    for arm in ARMS:
        fits[arm] = fit_rows(rows_by_arm[arm])
        boots[arm] = f4().f1().bootstrap_axis(rows_by_arm[arm], "author_mult",
                                              seed=BOOT_SEED_MARGINAL[arm])
        wr[arm] = wrmse(fits[arm])

    paired = paired_bootstrap(rows_by_arm, WORLDS_PER_CELL, BOOT_SEED_PAIRED)

    # per-point level contrasts + sign counts
    contrasts = []
    for m in mults:
        vi = np.asarray([r for r in rows_by_arm["intact"] if r["author_mult"] == m][0]["world_values"])
        vd = np.asarray([r for r in rows_by_arm["deleted"] if r["author_mult"] == m][0]["world_values"])
        diff = vd - vi
        ci = paired["level_ci95"][int(m)]
        contrasts.append({
            "author_mult": int(m),
            "agreement_intact": float(vi.mean()), "agreement_deleted": float(vd.mean()),
            "level_contrast": float(diff.mean()),
            "level_contrast_ci95": ci,
            "ci_lower_above_zero": bool(ci is not None and ci[0] > 0.0),
            "positive_worlds": int(np.sum(diff > 0)), "n_worlds": int(len(diff)),
            "per_world": [float(v) for v in diff],
        })
    pd.DataFrame([{k: v for k, v in c.items() if k != "per_world"} for c in contrasts]).to_csv(
        OUT / "level_contrasts.csv", index=False)
    pd.DataFrame([{k: v for k, v in cell_summary(a, m).items()
                   if k not in ("world_values", "world_seeds")}
                  for a in ARMS for m in mults]).to_csv(OUT / "cells.csv", index=False)

    # ---- leans ----
    dg_ci = paired["delta_gamma_ci95"]
    gd_ci = boots["deleted"]["exponent_ci95"]
    l1_band_ok = bool(dg_ci is not None and dg_ci[0] >= -L1_BAND and dg_ci[1] <= L1_BAND)
    l1_overlap = bool(gd_ci is not None and gd_ci[0] <= F4_GAMMA_CI[1] and gd_ci[1] >= F4_GAMMA_CI[0])
    l1 = {
        "lean": "L-1", "prior": 0.70,
        "rule": ("|Delta gamma| bootstrap CI inside +/-0.25 AND gamma_deleted CI overlaps "
                 "F4's [0.984, 1.218]"),
        "gamma_intact": fits["intact"].get("exponent"),
        "gamma_intact_ci95": boots["intact"]["exponent_ci95"],
        "gamma_deleted": fits["deleted"].get("exponent"),
        "gamma_deleted_ci95": gd_ci,
        "delta_gamma_point": (fits["deleted"]["exponent"] - fits["intact"]["exponent"]
                              if "exponent" in fits["deleted"] and "exponent" in fits["intact"]
                              else None),
        "delta_gamma_ci95": dg_ci,
        "delta_gamma_ci_inside_band": l1_band_ok,
        "gamma_deleted_overlaps_f4_band": l1_overlap,
        "gamma_deleted_disjoint_from_f4_band": bool(gd_ci is not None and not l1_overlap),
        "paired_bootstrap_gamma_intact_ci95": paired["gamma_intact_ci95"],
        "paired_bootstrap_gamma_deleted_ci95": paired["gamma_deleted_ci95"],
        "verdict": "HOLD" if (l1_band_ok and l1_overlap) else "MISS",
    }
    n_points_positive = sum(1 for c in contrasts if c["ci_lower_above_zero"])
    l2 = {
        "lean": "L-2", "prior": 0.75,
        "rule": ("deleted level exceeds intact at every grid point; HOLD iff per-point CI "
                 "LOWER edge > 0 at >= 4 of 5 points (ONE-SIDED clause)"),
        "points_with_ci_lower_above_zero": n_points_positive,
        "n_points": len(contrasts),
        "per_point": [{k: v for k, v in c.items() if k != "per_world"} for c in contrasts],
        "verdict": "HOLD" if n_points_positive >= 4 else "MISS",
    }
    ratio_ci = paired["wrmse_ratio_ci95"]
    l3_ok = bool(ratio_ci is not None and ratio_ci[1] >= 1.0)
    l3 = {
        "lean": "L-3", "prior": 0.55,
        "rule": ("deleted arm's fit quality no worse: ratio = WRMSE_intact / WRMSE_deleted, "
                 "CI including or above 1 (ONE-SIDED: MISS iff the whole CI lies BELOW 1)"),
        "wrmse_intact": wr["intact"], "wrmse_deleted": wr["deleted"],
        "wrmse_ratio_point": (wr["intact"] / wr["deleted"]
                              if wr["intact"] is not None and wr["deleted"] else None),
        "wrmse_ratio_ci95": ratio_ci,
        "ci_upper_at_or_above_1": l3_ok,
        "ci_entirely_above_1": bool(ratio_ci is not None and ratio_ci[0] > 1.0),
        "verdict": "HOLD" if l3_ok else "MISS",
    }

    # ---- holdout (optional) ----
    holdout: dict[str, Any] = {"included": include_x32}
    if include_x32:
        ho_mult = f4().HOLDOUT_AUTHOR_MULT
        for arm in ARMS:
            fit = fits[arm]
            lo32 = fit["intercept"] + fit["exponent"] * math.log10(float(ho_mult))
            odds = 10.0 ** lo32
            obs = cell_summary(arm, ho_mult)
            gap = math.log10(obs["agreement_mean"] / (1.0 - obs["agreement_mean"])) - lo32
            holdout[arm] = {
                "predicted": float(odds / (1.0 + odds)),
                "observed": obs["agreement_mean"], "observed_se": obs["agreement_se"],
                "log_odds_gap": float(gap),
                "within_factor2": bool(abs(gap) <= math.log10(2.0)),
            }

    # ---- pivots ----
    pivots = {
        "P1d": {"rule": "G1d fails -> VOID on non-replication",
                "fires": bool(not gates["G1d"]["pass"])},
        "P2d": {"rule": ("L-1 MISS with gamma_deleted CI DISJOINT from F4's band -> "
                         "ownership/scaling dissociation"),
                "fires": bool(l1["verdict"] == "MISS" and l1["gamma_deleted_disjoint_from_f4_band"])},
        "P3d": {"rule": "G2d/G4d fail (deletion inert) -> STOP defect",
                "fires": bool(not (gates["G2d"]["pass"] and gates["G4d"]["pass"]))},
    }

    if pivots["P1d"]["fires"]:
        verdict = "VOID_ON_NON_REPLICATION"
    elif pivots["P2d"]["fires"]:
        verdict = "OWNERSHIP_AND_SCALING_DISSOCIATE__P2D_FIRES"
    elif l1["verdict"] == "HOLD" and l2["verdict"] == "HOLD" and l3["verdict"] == "HOLD":
        verdict = ("AUTHOR_AXIS_IS_A_REPLICATE_AXIS__EXPONENT_SURVIVES_AUTHOR_DELETION__"
                   "DELETION_RAISES_LEVEL_AT_EVERY_SCALE__FIT_QUALITY_NO_WORSE")
    elif l1["verdict"] == "HOLD":
        verdict = "AUTHOR_AXIS_IS_A_REPLICATE_AXIS__EXPONENT_SURVIVES__SEE_LEAN_ADJUDICATION"
    else:
        verdict = "MIXED_SEE_LEAN_ADJUDICATION"

    decision = {
        "experiment": "M4-K1d_replicate_axis",
        "banner": BANNER, "tier": "EXPLORATORY", "label_free": True,
        "registered_spec": "docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md#M4-K1d",
        "part0_registered_in": "reports/SUICA_M4_K1D_REPLICATE_AXIS_REPORT.md Part 0 (before arms)",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED, "worlds_per_cell": WORLDS_PER_CELL,
        "kappa": KAPPA, "design": DESIGN, "grid": mults,
        "gates": {k: gates[k]["pass"] for k in ("G0d", "G1d", "G2d", "G3d", "G4d", "G5d")
                  if k in gates},
        "fits": {arm: {k: v for k, v in fits[arm].items() if k != "points"} for arm in ARMS},
        "bootstrap_marginal": boots,
        "paired_bootstrap": {k: v for k, v in paired.items() if k != "level_ci95"},
        "level_contrasts": contrasts,
        "leans": {"L-1": l1, "L-2": l2, "L-3": l3},
        "holdout": holdout,
        "pivots": pivots,
        "verdict": verdict,
        "claim_boundary": (
            "Synthetic re-reading of M4-F4's author-scaling law under exact pre-map deletion of "
            "the generator's author-mean channel, in a world calibrated to the opened PANDORA "
            "D-panel regime. Licenses a panel-DESIGN prior only. No claim about the real "
            "relation field's content, personality, emotion, diagnosis, or any individual."
        ),
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2, default=str) + "\n",
                                       encoding="utf-8")
    print(json.dumps({"verdict": verdict,
                      "L-1": l1["verdict"], "L-2": l2["verdict"], "L-3": l3["verdict"],
                      "gamma_intact": l1["gamma_intact"], "gamma_deleted": l1["gamma_deleted"],
                      "delta_gamma_ci95": dg_ci}, indent=2, default=str))
    return decision


def write_manifest(stage_times: dict[str, float]) -> None:
    path = OUT / "manifest.json"
    prior = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    prior.setdefault("leg", "M4-K1d")
    prior.setdefault("banner", BANNER)
    prior.setdefault("script", "scripts/run_suica_m4_k1d_replicate_axis.py")
    prior.setdefault("master_seed", MASTER_SEED)
    prior.setdefault("worlds_per_cell", WORLDS_PER_CELL)
    prior.setdefault("pilot_worlds", list(PILOT_WORLDS))
    prior.setdefault("kappa", KAPPA)
    prior.setdefault("design", DESIGN)
    prior.setdefault("arms", list(ARMS))
    prior.setdefault("python", sys.version)
    prior.setdefault("numpy", np.__version__)
    prior.setdefault("pandas", pd.__version__)
    prior.setdefault("stage_seconds", {})
    prior["stage_seconds"].update(stage_times)
    prior["updated_utc"] = datetime.now(UTC).isoformat()
    path.write_text(json.dumps(prior, indent=2, default=str) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["part0", "arms", "g1d", "holdout", "finalize"],
                        required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--draws", type=int, default=None)
    parser.add_argument("--mults", type=str, default=None)
    parser.add_argument("--pilot-small-only", action="store_true")
    args = parser.parse_args()

    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    OUT.mkdir(parents=True, exist_ok=True)

    f4m = f4()
    draws = args.draws if args.draws is not None else f4m.DRAWS
    all_mults = list(f4m.AUTHOR_MULTS)
    mults = [int(x) for x in args.mults.split(",")] if args.mults else all_mults

    started = time.time()
    if args.stage == "part0":
        run_part0(args.workers, draws, args.pilot_small_only)
        write_manifest({"part0": time.time() - started})
    elif args.stage == "arms":
        _require_part0()
        knobs, knob_tag = knobs_and_tag()
        tasks = [build_task(arm, m, w, knobs, knob_tag, draws)
                 for m in mults for arm in ARMS for w in range(WORLDS_PER_CELL)]
        run_cells(tasks, args.workers, "arms")
        write_manifest({f"arms_{'_'.join(str(m) for m in mults)}": time.time() - started})
    elif args.stage == "g1d":
        _require_part0()
        run_g1d(all_mults)
        write_manifest({"g1d": time.time() - started})
    elif args.stage == "holdout":
        _require_part0()
        _require_g1d()
        gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
        if not gates["economy"]["include_x32"]:
            raise AssertionError("Part 0's economy rule excluded the x32 holdout; "
                                 "the decision is Part-0-fixed and may not change mid-run.")
        knobs, knob_tag = knobs_and_tag()
        ho = f4m.HOLDOUT_AUTHOR_MULT
        tasks = [build_task(arm, ho, w, knobs, knob_tag, draws, holdout=True)
                 for arm in ARMS for w in range(WORLDS_PER_CELL)]
        run_cells(tasks, args.workers, "holdout")
        write_manifest({"holdout": time.time() - started})
    elif args.stage == "finalize":
        gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
        run_finalize(all_mults, bool(gates["economy"]["include_x32"]))
        write_manifest({"finalize": time.time() - started})
    print(f"[stage {args.stage}] {time.time() - started:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
