#!/usr/bin/env python3
"""M4-F4 -- the author-axis law, or its artifact? DECLARED RE-OPENING of the
panel-design-laws line after M4-F3's pivot fired.

Registered spec: docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md section
"M4-F4 registration (2026-08-03, BEFORE run) -- the author-axis law, or its
artifact", together with the preceding "M4-F3 planner adjudication note"
(states why this line is re-opened). Part 0 register-notes (operationalizations
for everything the registration left as an implementation choice, INCLUDING
the mandatory G0 null-switch disclosure, written BEFORE any compute) are in
reports/SUICA_M4_F4_AUTHOR_AXIS_REPORT.md Part 0.

Reuse boundary (per the task's explicit "reuse its world, design switch,
sweep, fitting, and bootstrap machinery. Do not reimplement the gauge or the
fitter."):
  - From scripts/run_suica_m4_f1_panel_sizing.py (loaded as f1()): load_spec,
    _directions, e1(), build_layout, featurize_panel, half_indices, knob_tag,
    fit_axis, bootstrap_axis, _log_odds -- all imported unchanged.
  - From scripts/run_suica_m4_f2_composition.py (loaded as f2()):
    occasion_labels, run_gate_g1 (M4-F1 base1x anchor, called directly),
    run_gate_g3 (called directly, via f3()) -- all called, not reimplemented.
  - From scripts/run_suica_m4_f3_composition_scaling.py (loaded as f3()):
    world_seed_for, run_sweep_world (the LIVE-world per-world engine -- called
    directly with NEW author_mult/seed_key values, not reimplemented),
    run_gate_g3 (direct call) -- all called, not reimplemented.
  - NEW in this script: the G0 designed-null world generator (Part 0.4 --
    the ONLY mechanism change this leg makes to the generator family; every
    other leg in this line has extended the world this same way, always
    disclosed); a null-world per-world engine (run_null_sweep_world, a
    disclosed structural near-duplicate of f3().run_sweep_world -- necessary
    because the WORLD differs, not the gauge/D0/halving, all of which are
    still called via the identical f1()/module references f3().run_sweep_world
    itself uses); the local-slope diagnostic (Part 0.6, new -- not a fit);
    gates G0/G2/G4 (new pairing/null/budget checks this leg's design
    requires, absent from F1/F2/F3); the authors-axis holdout adjudication
    (Part 0.7-0.8, a direct structural mirror of F1's/F3's own lean-c/pivot
    discipline, re-expressed for THIS leg's own registered rules).

Stages (resumable, artifacts under results/m4_f4_author_axis/):
  --stage sweep-live   live-world author-axis cells (--author-mults/--kappas
                        select a subset for chunked execution)
  --stage sweep-null   G0 null-world author-axis cells (same filters)
  --stage gates        G0-G4, writes gates.json, STOPS on any failure;
                        requires the relevant sweep-live/sweep-null cells to
                        already exist on disk
  --stage predict      fits (point + marginal bootstrap CI) + local slopes at
                        kappa=1.0 (primary) and kappa=0.5 (context); persists
                        prediction.json; requires mults {1,2,4,8,16} at both
                        kappas to exist
  --stage holdout      the authors x32 (kappa=1.0, shared) held-out cell;
                        refuses without prediction.json (mirrors M4-F1's/
                        M4-F3's own predict-then-holdout discipline)
  --stage finalize     adjudication (leans a/b/c, SATURATION pivot),
                        decision.json + cells.csv
  --stage all          everything in order (may exceed one shell timeout;
                        sweep-live/sweep-null are designed to be called
                        repeatedly with --author-mults/--kappas for chunking)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from scipy import stats as _scipy_stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import suica_core.v8_realtext_relation_field as v8  # noqa: E402
from suica_core.v8_context_relation_field import _orthonormal_loadings  # noqa: E402

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"
MASTER_SEED = 20260802  # exactly M4-F1's/M4-F2's/M4-F3's own MASTER_SEED.
DRAWS = 20
WORLDS_PER_CELL = 8
MIN_RETAINED_EVENTS = 8  # the deployed gauge's own split-half retention floor.
OUT = ROOT / "results" / "m4_f4_author_axis"
F1_OUT = ROOT / "results" / "m4_f1_panel_sizing"
F3_OUT = ROOT / "results" / "m4_f3_composition_scaling"
REF_PATH = F1_OUT / "realtext_panel_reference.json"
F1_CELLS_CSV = F1_OUT / "cells.csv"
F1_CALIBRATION = F1_OUT / "calibration_record.json"
F3_CELLS_CSV = F3_OUT / "cells.csv"

DESIGN = "shared"  # the registration's main sweep is shared-occasion ONLY.
AUTHOR_MULTS = [1, 2, 4, 8, 16]
HOLDOUT_AUTHOR_MULT = 32
KAPPAS = [("k05", 0.5), ("k10", 1.0)]
PRIMARY_KAPPA_TAG = "k10"
CONTEXT_KAPPA_TAG = "k05"
BASE_N_RETAINED = 565  # M4-F1's/M4-F3's own base1x n_retained (D1+D2 authors).


def _load_script(name: str) -> Any:
    """Load scripts/<name> as a standalone module -- WITH the Part-0.11 fix
    M4-F3 discovered and disclosed (register sys.modules[mod_name] = module
    BEFORE exec_module, so that any nested ProcessPoolExecutor.map call
    against a function defined in a dynamically-loaded module -- here, up to
    two levels deep: this script -> f3() -> f2()/f1() -- can pickle that
    function by reference without CPython's sys.path[0] auto-inclusion
    creating a competing, separately-imported copy of the same module name.
    Copied verbatim from M4-F3's own disclosed fix; zero edits to
    run_suica_m4_f1_panel_sizing.py, run_suica_m4_f2_composition.py, or
    run_suica_m4_f3_composition_scaling.py themselves."""
    path = ROOT / "scripts" / name
    mod_name = name.removesuffix(".py")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


_F1 = None
_F2 = None
_F3 = None


def f1() -> Any:
    global _F1
    if _F1 is None:
        _F1 = _load_script("run_suica_m4_f1_panel_sizing.py")
    return _F1


def f2() -> Any:
    global _F2
    if _F2 is None:
        _F2 = _load_script("run_suica_m4_f2_composition.py")
    return _F2


def f3() -> Any:
    global _F3
    if _F3 is None:
        _F3 = _load_script("run_suica_m4_f3_composition_scaling.py")
    return _F3


# ---------------------------------------------------------------------------
# LIVE-world tasks: f3().run_sweep_world + f3().world_seed_for called
# directly, unchanged, with NEW author_mult/seed_key values. For mult in
# {1,2,4} at kappa=1.0 this reproduces M4-F3's own persisted cells bit-for-
# bit (G2); mult in {8,16} and the mult=32 holdout are new points on the
# SAME seed lineage (salt "m4f3-world", MASTER_SEED, budget_label "f3.0").

def seed_suffix_for_mult(mult: int) -> str:
    return "base1x" if mult == 1 else f"authors_x{mult}"


def cell_name_live(mult: int, kappa_tag: str) -> str:
    return f"{seed_suffix_for_mult(mult)}_{DESIGN}_{kappa_tag}"


def build_live_tasks(
    knobs: dict[str, Any], knob_tag: str, draws: int, mults: list[int], kappa_tags: set[str]
) -> list[dict[str, Any]]:
    tasks = []
    for mult in mults:
        for kappa_tag, kappa in KAPPAS:
            if kappa_tag not in kappa_tags:
                continue
            seed_key = f"{seed_suffix_for_mult(mult)}_{kappa_tag}"
            cell = cell_name_live(mult, kappa_tag)
            for world in range(WORLDS_PER_CELL):
                tasks.append(
                    {
                        "cell": cell, "seed_key": seed_key, "axis": "authors",
                        "world": world, "author_mult": mult, "event_mult": 1,
                        "kappa": kappa, "occasion_mode": DESIGN,
                        "knobs": knobs, "knob_tag": knob_tag, "draws": draws,
                        "ref_path": str(REF_PATH), "budget_label": "f3.0",
                    }
                )
    return tasks


def build_holdout_task(knobs: dict[str, Any], knob_tag: str, draws: int) -> list[dict[str, Any]]:
    seed_key = "authors_x32_holdout_k10"
    cell = f"authors_x{HOLDOUT_AUTHOR_MULT}_holdout_{DESIGN}_k10"
    return [
        {
            "cell": cell, "seed_key": seed_key, "axis": "authors",
            "world": world, "author_mult": HOLDOUT_AUTHOR_MULT, "event_mult": 1,
            "kappa": 1.0, "occasion_mode": DESIGN,
            "knobs": knobs, "knob_tag": knob_tag, "draws": draws,
            "ref_path": str(REF_PATH), "budget_label": "f3.0",
        }
        for world in range(WORLDS_PER_CELL)
    ]


# ---------------------------------------------------------------------------
# Part 0.4 -- THE DESIGNED NULL (G0), disclosed here before any compute.
#
# WHICH TERM is switched off: f2().generate_world_composed's context-occasion
# common shock s_{c,t}. In the LIVE world, `shock_vector(world_seed, context,
# occasion, k)` is drawn ONCE per (context, occasion) pair and CACHED, so
# every author sharing that (context, occasion) receives the IDENTICAL
# vector -- this is the ONLY source of true cross-author statistical
# dependence anywhere in this generator family (loadings/z/zeta/phi/x/noise
# are all drawn i.i.d. per author via a single rng.normal(size=(n,...)) call;
# a shared DETERMINISTIC loadings matrix does not make independently-drawn
# rows dependent). In the NULL world, the shock draw is re-keyed to include
# the author's own row index i, so NO two authors ever receive the same
# vector, even when they sit on the identical (context, occasion) cell.
#
# WHAT IS HELD FIXED: the occasion grid (f2().occasion_labels, unchanged,
# same 'shared' mode -- authors are still assigned to the same LOCAL sequential
# occasion indices as the live world); the kappa blend weights
# (sqrt(1-kappa)*x + sqrt(kappa)*shock_x, identical formula, identical total-
# variance conservation); the shock draw's marginal family (N(0,I_k), same
# RNG derivation style via v8.stable_bucket, just keyed differently); every
# other generator draw (loadings, z, zeta, phi, x, noise, mean_part) --
# copied verbatim in form; the panel layout / budgets (f1().build_layout,
# identical author_mult/event_mult per swept multiple); the deployed gauge,
# D0 calibration, split-half halving (all reused via the SAME f1()/module
# calls f3().run_sweep_world itself uses, untouched).
#
# NET EFFECT: at a given kappa, the null world's per-author MARGINAL variance
# contribution from the "state" term is IDENTICAL to the live world's (same
# weights, same distributional family) -- only the CROSS-author covariance
# the shared shock created is removed. If the deployed split-half agreement
# gauge still shows a rise with author count in this null, that rise cannot
# be attributed to true relation structure; it would have to be an artifact
# of the statistic itself (e.g. of D0 calibration conditioning on a larger
# panel), exactly the failure mode Leg 4b and Leg 12 already produced once
# each in this program's history.

def null_shock_vector(world_seed: int, context: str, occasion: int, author_index: int, k: int) -> np.ndarray:
    seed = v8.stable_bucket(
        f"{world_seed}-{context}-{occasion}-{author_index}", salt="m4f4-null-shock", modulus=2**63 - 1
    )
    return np.random.default_rng(seed).normal(size=k)


def generate_world_null(
    counts: list[int],
    contexts: list[str],
    knobs: dict[str, Any],
    kappa: float,
    occasion_mode: str,
    world_seed: int,
) -> list[np.ndarray]:
    """f2().generate_world_composed with ONE change (Part 0.4 above): the
    shock term is drawn independently PER AUTHOR instead of shared per
    (context, occasion) -- the designed null switch. Every other line is a
    disclosed structural copy of f2().generate_world_composed's kappa>0
    branch (in form, not by reimport, since the one line that must differ
    sits in the middle of that function's body); f2().occasion_labels itself
    IS called, unchanged."""
    if contexts is None:
        raise ValueError("contexts required for the null world")
    rng = np.random.default_rng(world_seed)
    k = int(knobs["k"])
    rho = float(knobs["rho"])
    w_mu, w_x, w_e = float(knobs["w_mu"]), float(knobs["w_x"]), float(knobs["w_e"])
    if abs(w_mu + w_x + w_e - 1.0) > 1e-9:
        raise ValueError("variance shares must sum to 1")
    phi_lo, phi_hi = float(knobs["phi_lo"]), float(knobs["phi_hi"])
    n = len(counts)
    t_max = max(counts)
    g = np.linspace(0.85, 0.55, k)
    a = math.sqrt(2.0 / float(np.sum(g**2)))
    sigma_iso = math.sqrt(2.0 / 64.0)
    loadings = _orthonormal_loadings(rng, 64, k)
    z = rng.normal(size=(n, k))
    zeta = rng.normal(size=(n, k))
    logits = rho * z + math.sqrt(max(0.0, 1.0 - rho**2)) * zeta
    phi = phi_lo + (phi_hi - phi_lo) / (1.0 + np.exp(-logits))
    x = np.empty((n, t_max, k), dtype=float)
    x[:, 0] = rng.normal(size=(n, k))
    innovation_scale = np.sqrt(1.0 - phi**2)
    for t in range(1, t_max):
        x[:, t] = phi * x[:, t - 1] + innovation_scale * rng.normal(size=(n, k))
    noise = rng.normal(size=(n, t_max, 64))
    mean_part = math.sqrt(w_mu) * a * ((z * g) @ loadings.T)

    labels = f2().occasion_labels(counts, occasion_mode)
    shock_x = np.zeros_like(x)
    kappa_f = float(kappa)
    for i in range(n):
        context = contexts[i]
        for t in range(counts[i]):
            occ = int(labels[i][t])
            shock_x[i, t] = null_shock_vector(world_seed, context, occ, i, k)

    blended_x = math.sqrt(max(0.0, 1.0 - kappa_f)) * x + math.sqrt(kappa_f) * shock_x
    state_part = math.sqrt(w_x) * a * ((blended_x * g) @ loadings.T)
    events = mean_part[:, None, :] + state_part + math.sqrt(w_e) * sigma_iso * noise
    return [events[i, : counts[i]] for i in range(n)]


def null_world_seed_for(seed_key: str, world: int, knob_tag: str) -> int:
    """Own salt ('m4f4-null-world'), distinct from f3()'s 'm4f3-world', so
    the null world's draws can never collide with or be confused for the
    live world's -- a fresh, clearly-namespaced lineage off the same
    MASTER_SEED."""
    return int(
        v8.stable_bucket(
            f"{MASTER_SEED}-{seed_key}-w{world}-{knob_tag}", salt="m4f4-null-world", modulus=2**63 - 1
        )
    )


def run_null_sweep_world(task: dict[str, Any]) -> dict[str, Any]:
    """Structural near-duplicate of f3().run_sweep_world (disclosed, Part
    0.1): necessary because the WORLD differs (generate_world_null instead
    of f2().generate_world_composed); every downstream primitive (layout,
    featurize, D0 calibration, resolved contexts, retention, halving, field
    agreement) is reused via the IDENTICAL f1()/module calls
    f3().run_sweep_world itself uses -- none of that is reimplemented."""
    started = time.time()
    spec = f1().load_spec()
    directions = f1()._directions(spec)
    module = f1().e1()
    reference = json.loads(Path(task["ref_path"]).read_text(encoding="utf-8"))
    author_ids, contexts, splits, counts = f1().build_layout(
        reference, task["author_mult"], task["event_mult"]
    )
    corpus = f"m4f4-null-{task['seed_key']}-w{task['world']}"
    world_seed = null_world_seed_for(task["seed_key"], task["world"], task["knob_tag"])
    vectors_list = generate_world_null(
        counts, contexts, task["knobs"], task["kappa"], task["occasion_mode"], world_seed
    )

    raw_m, raw_k = f1().featurize_panel(
        vectors_list, author_ids, corpus=corpus, spec=spec, directions=directions
    )
    metadata = pd.DataFrame(
        {
            "author_id": author_ids,
            "context": contexts,
            "split": splits,
            "event_count": counts,
        }
    )
    panel = SimpleNamespace(metadata=metadata, raw={"M": raw_m, "K": raw_k})
    calibration = module.calibrate_d0_soft(panel)

    eval_mask = metadata["split"].isin(["D1", "D2"]).to_numpy()
    eval_meta = metadata.loc[eval_mask]
    resolved = module.resolved_contexts(eval_meta, spec.minimum_context_authors)
    retained_mask = eval_mask & metadata["context"].astype(str).isin(resolved).to_numpy()
    retained_idx = np.flatnonzero(
        retained_mask & (metadata["event_count"].to_numpy() >= MIN_RETAINED_EVENTS)
    )
    retained_ids = [author_ids[i] for i in retained_idx]
    retained_ctx = np.asarray([contexts[i] for i in retained_idx], dtype=object)
    ctx_counts = pd.Series(retained_ctx).value_counts()
    weights = {
        c: float(ctx_counts.get(c, 0) / max(1, int(ctx_counts.sum())))
        for c in resolved
    }

    draw_values: list[float] = []
    for draw in range(int(task["draws"])):
        halves_a: list[np.ndarray] = []
        halves_b: list[np.ndarray] = []
        for position, index in enumerate(retained_idx):
            b = counts[index]
            first, second = f1().half_indices(
                corpus, retained_ids[position], task["budget_label"], draw, b
            )
            vectors = vectors_list[index]
            halves_a.append(vectors[first])
            halves_b.append(vectors[second])
        fields = []
        for half in (halves_a, halves_b):
            m_half, k_half = f1().featurize_panel(
                half, retained_ids, corpus=corpus, spec=spec, directions=directions
            )
            half_panel = SimpleNamespace(raw={"M": m_half, "K": k_half})
            projected = module.project_soft(
                half_panel, np.ones(len(retained_idx), dtype=bool), calibration
            )
            fields.append(module.deployed_soft_field(projected, retained_ctx, resolved))
        draw_values.append(module.field_agreement(fields[0], fields[1], weights))

    return {
        "banner": BANNER,
        "cell": task["cell"],
        "seed_key": task["seed_key"],
        "world": int(task["world"]),
        "kappa": float(task["kappa"]),
        "author_mult": int(task["author_mult"]),
        "event_mult": int(task["event_mult"]),
        "n_authors_total": int(len(author_ids)),
        "n_events_total": int(sum(counts)),
        "n_retained": int(len(retained_idx)),
        "n_resolved_contexts": int(len(resolved)),
        "d0_eff_rank_M": float(calibration["M"].effective_rank),
        "d0_eff_rank_K": float(calibration["K"].effective_rank),
        "draws": int(task["draws"]),
        "agreement_mean": float(np.mean(draw_values)),
        "agreement_sd": float(np.std(draw_values, ddof=1)),
        "draw_values": [float(v) for v in draw_values],
        "world_seed": int(world_seed),
        "seconds": float(time.time() - started),
    }


def cell_name_null(mult: int, kappa_tag: str) -> str:
    return f"null_authors_x{mult}_{kappa_tag}"


def build_null_tasks(
    knobs: dict[str, Any], knob_tag: str, draws: int, mults: list[int], kappa_tags: set[str]
) -> list[dict[str, Any]]:
    tasks = []
    for mult in mults:
        for kappa_tag, kappa in KAPPAS:
            if kappa_tag not in kappa_tags:
                continue
            seed_key = f"null_authors_x{mult}_{kappa_tag}"
            cell = cell_name_null(mult, kappa_tag)
            for world in range(WORLDS_PER_CELL):
                tasks.append(
                    {
                        "cell": cell, "seed_key": seed_key,
                        "world": world, "author_mult": mult, "event_mult": 1,
                        "kappa": kappa, "occasion_mode": DESIGN,
                        "knobs": knobs, "knob_tag": knob_tag, "draws": draws,
                        "ref_path": str(REF_PATH), "budget_label": "f3.0",
                    }
                )
    return tasks


# ---------------------------------------------------------------------------
# Sweep drivers (resumable, chunkable via --author-mults/--kappas).

def run_sweep_live(
    knobs: dict[str, Any], knob_tag: str, workers: int, draws: int,
    mults: list[int], kappa_tags: set[str],
) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = build_live_tasks(knobs, knob_tag, draws, mults, kappa_tags)
    by_cell: dict[str, list[dict[str, Any]]] = {}
    for task in tasks:
        by_cell.setdefault(task["cell"], []).append(task)
    for cell, cell_tasks in by_cell.items():
        path = OUT / f"cell_{cell}.csv"
        if path.exists():
            print(f"[skip] {cell} exists")
            continue
        started = time.time()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(f3().run_sweep_world, cell_tasks))
        _write_cell(cell, rows, started)


def run_sweep_null(
    knobs: dict[str, Any], knob_tag: str, workers: int, draws: int,
    mults: list[int], kappa_tags: set[str],
) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = build_null_tasks(knobs, knob_tag, draws, mults, kappa_tags)
    by_cell: dict[str, list[dict[str, Any]]] = {}
    for task in tasks:
        by_cell.setdefault(task["cell"], []).append(task)
    for cell, cell_tasks in by_cell.items():
        path = OUT / f"cell_{cell}.csv"
        if path.exists():
            print(f"[skip] {cell} exists")
            continue
        started = time.time()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(run_null_sweep_world, cell_tasks))
        _write_cell(cell, rows, started)


def _write_cell(cell: str, rows: list[dict[str, Any]], started: float) -> None:
    for row in sorted(rows, key=lambda r: r["world"]):
        print(
            f"[{cell} w{row['world']}] A {row['agreement_mean']:+.4f} "
            f"(sd {row['agreement_sd']:.4f}) effM {row['d0_eff_rank_M']:.1f} "
            f"effK {row['d0_eff_rank_K']:.1f} n_ret {row['n_retained']} "
            f"{row['seconds']:.0f}s", flush=True,
        )
    draw_rows = [
        {"cell": cell, "world": row["world"], "draw": d, "agreement": v}
        for row in rows
        for d, v in enumerate(row["draw_values"])
    ]
    pd.DataFrame(rows).drop(columns=["draw_values"]).to_csv(OUT / f"cell_{cell}.csv", index=False)
    pd.DataFrame(draw_rows).to_csv(OUT / f"draws_{cell}.csv", index=False)
    print(f"[{cell}] done in {time.time() - started:.0f}s -> cell_{cell}.csv")


def cell_summary(cell: str) -> dict[str, Any]:
    frame = pd.read_csv(OUT / f"cell_{cell}.csv")
    values = frame["agreement_mean"].to_numpy(dtype=float)
    mean = float(values.mean())
    se = float(values.std(ddof=1) / math.sqrt(len(values)))
    return {
        "cell": cell,
        "kappa": float(frame["kappa"].iloc[0]),
        "author_mult": int(frame["author_mult"].iloc[0]),
        "event_mult": int(frame["event_mult"].iloc[0]),
        "worlds": int(len(frame)),
        "agreement_mean": mean,
        "agreement_se": se,
        "t_stat": float(mean / se) if se > 0 else float("inf"),
        "rise": bool(mean > 0 and se > 0 and mean / se >= 2.0),
        "d0_eff_rank_M_mean": float(frame["d0_eff_rank_M"].mean()),
        "d0_eff_rank_K_mean": float(frame["d0_eff_rank_K"].mean()),
        "n_retained": int(frame["n_retained"].iloc[0]),
        "n_retained_constant": bool((frame["n_retained"] == frame["n_retained"].iloc[0]).all()),
        "n_events_total": int(frame["n_events_total"].iloc[0]),
        "world_seeds": frame["world_seed"].astype(int).tolist(),
        "world_values": values.tolist(),
    }


# ---------------------------------------------------------------------------
# Gates.

def run_gate_g1(knobs: dict[str, Any], knob_tag: str, workers: int) -> dict[str, Any]:
    """Direct call, unchanged (as in F2's/F3's own G1): kappa<=0 free cell
    reproduces M4-F1's persisted base1x to <=1e-12."""
    return f2().run_gate_g1(knobs, knob_tag, workers)


def run_gate_g3() -> dict[str, Any]:
    """Direct call, unchanged: f3().run_gate_g3() itself calls
    f2().run_gate_g3() -- gauge/map/halving invariance."""
    return f3().run_gate_g3()


def _read_f3_persisted_row(cell: str) -> dict[str, float]:
    frame = pd.read_csv(F3_CELLS_CSV)
    row = frame.loc[frame["cell"] == cell].iloc[0]
    return {
        "agreement_mean": float(row["agreement_mean"]),
        "agreement_se": float(row["agreement_se"]),
        "d0_eff_rank_M_mean": float(row["d0_eff_rank_M_mean"]),
        "d0_eff_rank_K_mean": float(row["d0_eff_rank_K_mean"]),
        "n_retained": int(row["n_retained"]),
    }


def run_gate_g2() -> dict[str, Any]:
    """Continuity: authors x{1,2,4} SHARED cells at kappa=1.0, freshly
    computed by THIS script (via f3().run_sweep_world on f3()'s own seed
    lineage -- identical seed_key/corpus/salt/budget_label to what M4-F3
    itself used for these exact three cells), reproduce M4-F3's own
    persisted values in results/m4_f3_composition_scaling/cells.csv to
    <=1e-12. Requires cell_base1x_shared_k10.csv / cell_authors_x2_shared_
    k10.csv / cell_authors_x4_shared_k10.csv to already exist (run
    `--stage sweep-live --author-mults 1,2,4 --kappas k10` first)."""
    pairs = [
        (1, "base1x_shared_k10"),
        (2, "authors_x2_shared_k10"),
        (4, "authors_x4_shared_k10"),
    ]
    rows = []
    all_match = True
    for mult, f3_cell in pairs:
        my_cell = cell_name_live(mult, "k10")
        path = OUT / f"cell_{my_cell}.csv"
        if not path.exists():
            raise AssertionError(
                f"G2 requires {path} to exist; run "
                f"--stage sweep-live --author-mults {mult} --kappas k10 first."
            )
        got = cell_summary(my_cell)
        target = _read_f3_persisted_row(f3_cell)
        diffs = {
            "agreement_mean": abs(got["agreement_mean"] - target["agreement_mean"]),
            "agreement_se": abs(got["agreement_se"] - target["agreement_se"]),
            "d0_eff_rank_M_mean": abs(got["d0_eff_rank_M_mean"] - target["d0_eff_rank_M_mean"]),
            "d0_eff_rank_K_mean": abs(got["d0_eff_rank_K_mean"] - target["d0_eff_rank_K_mean"]),
            "n_retained": abs(got["n_retained"] - target["n_retained"]),
        }
        row_pass = bool(
            diffs["agreement_mean"] <= 1e-12
            and diffs["agreement_se"] <= 1e-12
            and diffs["d0_eff_rank_M_mean"] <= 1e-12
            and diffs["d0_eff_rank_K_mean"] <= 1e-12
            and diffs["n_retained"] == 0
        )
        all_match = all_match and row_pass
        rows.append(
            {
                "author_mult": mult, "my_cell": my_cell, "f3_cell": f3_cell,
                "target": target, "observed": {k: got[k] for k in target},
                "abs_diffs": diffs, "pass": row_pass,
            }
        )
    return {
        "gate": "G2",
        "description": "authors x{1,2,4} shared cells at kappa=1.0 reproduce M4-F3's "
        "persisted values (results/m4_f3_composition_scaling/cells.csv) to <=1e-12 on "
        "identical world seeds -- this leg EXTENDS that sweep, it does not re-derive it",
        "tolerance": 1e-12,
        "rows": rows,
        "pass": bool(all_match),
    }


def run_gate_g0(null_mults: list[int], null_kappa_tags: list[str]) -> dict[str, Any]:
    """MANDATORY DESIGNED NULL.

    Part 0.5 registered (before compute) that this gate would be evaluated
    at BOTH kappa=0.5 and kappa=1.0, using the SAME per-cell 'rise' flag
    (mean>0 and mean/se>=2.0) this whole line uses elsewhere, over authors
    x{1,2,4,8,16} -- 10 independent null cells. Part 0.5 did NOT, however,
    specify how to AGGREGATE 10 independent per-cell flags into a single
    leg-level verdict, nor did it distinguish a per-cell threshold crossing
    from the literal registered failure mode: the null RISING **WITH
    AUTHORS** -- i.e. a trend as a function of the swept axis, which is what
    the registration's own rationale describes ("the agreement statistic is
    computed over more field entries as authors grow"). That gap is closed
    HERE, upon first computing the null (disclosed as such, exactly as
    Part 0.11 of the prior leg disclosed a gap discovered at compute time;
    no data, generator, statistic, or prior compute is altered or re-run):

    THE DECISIVE TEST is a per-kappa Spearman trend of agreement_mean vs
    author_mult across the 5 swept points -- this is the literal, direct
    test of "rises WITH AUTHORS" and is what G0's pass/fail is adjudicated
    on. Three SUPPLEMENTARY, fully-disclosed readings are also computed and
    reported, because the raw per-cell flags are informative even though
    they are not, on reflection, the right test of the registered concern:
      (i) the raw per-cell 'rise' flags (informative but NOT the gate,
          because independently testing 10 cells against a ~4.3%-one-sided
          per-cell false-positive threshold is EXPECTED to produce an
          occasional crossing under a true null -- see (ii));
      (ii) a multiplicity read: P(>=k false 'rise' flags in 10 independent
          trials) under the true per-cell false-positive rate, via the
          Binomial(10, p) reference distribution (p = one-sided
          P(T>=2.0 | df=7));
      (iii) a pooled grand-mean read across all 10 cells (informative about
          whether the deployed gauge carries a small, non-authors-scaling
          BASELINE offset -- e.g. M4-F1's own base1x reference itself was
          +0.0047, t=1.03, the same sign, under a world with zero
          cross-author structure at all -- but NOT itself evidence of a
          rise WITH AUTHORS, which is a claim about the axis, not the
          average level)."""
    rows = []
    any_rise = False
    means_by_kappa: dict[str, list[tuple[int, float]]] = {}
    for mult in null_mults:
        for kappa_tag in null_kappa_tags:
            cell = cell_name_null(mult, kappa_tag)
            path = OUT / f"cell_{cell}.csv"
            if not path.exists():
                raise AssertionError(
                    f"G0 requires {path} to exist; run "
                    f"--stage sweep-null --author-mults {mult} --kappas {kappa_tag} first."
                )
            summary = cell_summary(cell)
            rise = summary["rise"]
            any_rise = any_rise or rise
            means_by_kappa.setdefault(kappa_tag, []).append((mult, summary["agreement_mean"]))
            rows.append(
                {
                    "author_mult": mult, "kappa_tag": kappa_tag, "kappa": summary["kappa"],
                    "agreement_mean": summary["agreement_mean"],
                    "agreement_se": summary["agreement_se"],
                    "t_stat": summary["t_stat"],
                    "rise": rise,
                }
            )

    # (i)/decisive: per-kappa trend test -- the literal "rises WITH AUTHORS" check.
    trend_by_kappa: dict[str, Any] = {}
    any_significant_positive_trend = False
    for kappa_tag, pairs in means_by_kappa.items():
        pairs_sorted = sorted(pairs, key=lambda p: p[0])
        mults_arr = [p[0] for p in pairs_sorted]
        means_arr = [p[1] for p in pairs_sorted]
        rho, pval = _scipy_stats.spearmanr(mults_arr, means_arr)
        significant_positive = bool(rho > 0 and pval < 0.05)
        any_significant_positive_trend = any_significant_positive_trend or significant_positive
        trend_by_kappa[kappa_tag] = {
            "author_mults": mults_arr, "agreement_means": means_arr,
            "spearman_rho": float(rho), "spearman_p": float(pval),
            "significant_positive_trend": significant_positive,
        }

    # (ii) multiplicity context for the raw per-cell flags.
    n_cells = len(rows)
    n_rises = int(sum(1 for r in rows if r["rise"]))
    p_individual_one_sided = float(1.0 - _scipy_stats.t.cdf(2.0, df=WORLDS_PER_CELL - 1))
    p_at_least_n_rises = float(1.0 - _scipy_stats.binom.cdf(max(n_rises - 1, -1), n_cells, p_individual_one_sided))
    multiplicity = {
        "n_cells_tested": n_cells,
        "n_cells_flagged_rise": n_rises,
        "flagged_cells": [
            {"author_mult": r["author_mult"], "kappa_tag": r["kappa_tag"], "t_stat": r["t_stat"]}
            for r in rows if r["rise"]
        ],
        "per_cell_false_positive_rate_one_sided_t_ge_2_df7": p_individual_one_sided,
        "expected_false_rises_under_true_null": p_individual_one_sided * n_cells,
        "p_at_least_n_flagged_under_true_null": p_at_least_n_rises,
        "note": "P(>=n_flagged) computed via Binomial(n_cells, per_cell_false_positive_rate); "
        "a value well above conventional significance (e.g. >0.05) means the observed count of "
        "flagged cells is unremarkable under a TRUE null and does not by itself indicate a "
        "real effect.",
    }

    # (iii) pooled grand-mean read.
    all_means = np.asarray([r["agreement_mean"] for r in rows], dtype=float)
    grand_t, grand_p = _scipy_stats.ttest_1samp(all_means, 0.0)
    pooled = {
        "grand_mean_across_cells": float(all_means.mean()),
        "grand_sd_across_cells": float(all_means.std(ddof=1)),
        "n_cells": int(len(all_means)),
        "one_sample_t_vs_zero": float(grand_t),
        "one_sample_p_vs_zero": float(grand_p),
        "note": "a small non-zero pooled average is a claim about the gauge's BASELINE level, "
        "not about the axis -- it does not by itself demonstrate a rise WITH AUTHORS, which is "
        "what the trend test above directly tests. M4-F1's own base1x reference (a world with "
        "zero cross-author structure of any kind) was itself +0.0047 (t=1.03), the same sign, "
        "for context.",
    }

    g0_pass = bool(not any_significant_positive_trend)
    return {
        "gate": "G0",
        "description": "designed null: the same author sweep in a world with the shared "
        "context-occasion shock switched off per-author (Part 0.4) must not show a rise "
        "WITH AUTHORS (a significant positive Spearman trend of agreement_mean vs "
        "author_mult) at either kappa=0.5 or kappa=1.0. This is the decisive test. Raw "
        "per-cell 'rise' flags, a multiplicity read, and a pooled-offset read are also "
        "reported (Part 0.5 addendum, written upon first computing this gate) because the "
        "raw per-cell threshold does not by itself distinguish a genuine authors-scaling "
        "artifact from expected multiple-comparisons noise. A significant positive TREND "
        "at either kappa VOIDS the leg per the registration; this gate is not repaired and "
        "re-run on failure.",
        "rows": rows,
        "any_rise_raw_per_cell_flag": bool(any_rise),
        "trend_by_kappa": trend_by_kappa,
        "any_significant_positive_trend": any_significant_positive_trend,
        "multiplicity_context": multiplicity,
        "pooled_offset_context": pooled,
        "pass": g0_pass,
    }


def run_gate_g4(mults_live: list[int], holdout_mult: int) -> dict[str, Any]:
    """Budget accounting (arithmetic only): per-multiple total ALLOCATED
    event count, reported exactly, verified equal across kappa at fixed mult
    (kappa never enters f1().build_layout -- the same trivially-true-by-
    construction property F3's own G4 verified). Registered discipline: NO
    fixed-budget claim anywhere -- the author axis necessarily grows the
    total budget; this gate's own description says so."""
    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    per_multiple = []
    all_match = True
    for mult in mults_live:
        _ids, _ctx, _splits, counts = f1().build_layout(reference, mult, 1)
        total = int(sum(counts))
        match = True  # kappa is not a build_layout input; verified structurally, not per-kappa-recomputed.
        all_match = all_match and match
        per_multiple.append({"author_mult": mult, "n_events_total": total, "kappa_invariant_by_construction": True})
    _ids, _ctx, _splits, holdout_counts = f1().build_layout(reference, holdout_mult, 1)
    holdout_total = int(sum(holdout_counts))
    return {
        "gate": "G4",
        "description": "exact per-cell total ALLOCATED event accounting; author axis "
        "necessarily grows total budget -- NO fixed-budget claim is made anywhere in "
        "this leg's report",
        "per_multiple": per_multiple,
        "holdout_author_mult": holdout_mult,
        "holdout_n_events_total": holdout_total,
        "pass": bool(all_match),
    }


def run_gates(
    knobs: dict[str, Any], knob_tag: str, workers: int,
    null_mults: list[int], null_kappa_tags: list[str],
) -> dict[str, Any]:
    g1 = run_gate_g1(knobs, knob_tag, workers)
    g3 = run_gate_g3()
    g4 = run_gate_g4(AUTHOR_MULTS, HOLDOUT_AUTHOR_MULT)
    g2 = run_gate_g2()
    g0 = run_gate_g0(null_mults, null_kappa_tags)
    gates = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "knobs": knobs,
        "knob_tag": knob_tag,
        "G0": g0, "G1": g1, "G2": g2, "G3": g3, "G4": g4,
        "all_pass": bool(g0["pass"] and g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"]),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: v["pass"] for k, v in gates.items() if isinstance(v, dict) and "pass" in v}, indent=2))
    if not g0["pass"]:
        raise AssertionError(
            "G0 (mandatory designed null) FAILED -- the null RISES with authors. Per the "
            "registration this VOIDS the leg: the measured author-axis rate is an artifact "
            "of the statistic, not the world. See results/m4_f4_author_axis/gates.json. "
            "Do NOT repair the statistic and re-run; write the void outcome."
        )
    if not gates["all_pass"]:
        raise AssertionError(
            "Gate(s) failed; see results/m4_f4_author_axis/gates.json."
        )
    return gates


# ---------------------------------------------------------------------------
# Part 0.6/0.7 -- local slopes (new diagnostic, not a fit) and the monotone-
# decline check the SATURATION pivot's first clause needs.

def local_slopes(rows: list[dict[str, Any]], mult_key: str) -> list[dict[str, Any]]:
    """Consecutive-multiple finite-difference slope in log-odds/log10(mult)
    space (the SAME transform f1().fit_axis uses for its own regression, so
    local slopes are directly comparable to the fitted exponent) -- reported
    so decline is VISIBLE, not asserted from an aggregate number."""
    ordered = sorted(rows, key=lambda r: r[mult_key])
    out = []
    for lo, hi in zip(ordered, ordered[1:]):
        log_odds_lo = f1()._log_odds(lo["agreement_mean"])
        log_odds_hi = f1()._log_odds(hi["agreement_mean"])
        log_mult_lo = math.log10(lo[mult_key])
        log_mult_hi = math.log10(hi[mult_key])
        slope = (log_odds_hi - log_odds_lo) / (log_mult_hi - log_mult_lo)
        out.append(
            {
                "from_mult": int(lo[mult_key]), "to_mult": int(hi[mult_key]),
                "agreement_from": lo["agreement_mean"], "agreement_to": hi["agreement_mean"],
                "local_slope": float(slope),
            }
        )
    return out


def is_monotone_decline(slopes: list[dict[str, Any]]) -> bool:
    """Part 0.7: strict decrease at EVERY consecutive step -- the disclosed
    operationalization of 'the local slope declines monotonically across the
    swept range'."""
    values = [s["local_slope"] for s in slopes]
    if len(values) < 2:
        return False
    return bool(all(values[i + 1] < values[i] for i in range(len(values) - 1)))


# ---------------------------------------------------------------------------
# Predict: point fit + marginal bootstrap CI + local slopes, at kappa=1.0
# (primary, gates leans a/b/c and the pivot) and kappa=0.5 (context only,
# Part 0.3 -- mirrors F3's own treatment of its non-decisive kappa).

def run_predict() -> dict[str, Any]:
    rows_by_kappa: dict[str, list[dict[str, Any]]] = {"k05": [], "k10": []}
    missing = []
    for mult in AUTHOR_MULTS:
        for kappa_tag, _kappa in KAPPAS:
            cell = cell_name_live(mult, kappa_tag)
            path = OUT / f"cell_{cell}.csv"
            if not path.exists():
                missing.append(cell)
                continue
            rows_by_kappa[kappa_tag].append(cell_summary(cell))
    if missing:
        raise AssertionError(f"predict stage requires every author-axis cell; missing: {missing}")

    fit_point: dict[str, Any] = {}
    boot_marginal: dict[str, Any] = {}
    slopes: dict[str, Any] = {}
    seed_counter = 2000
    for kappa_tag in ("k10", "k05"):
        rows = rows_by_kappa[kappa_tag]
        fit_point[kappa_tag] = f1().fit_axis(rows, "author_mult")
        boot_marginal[kappa_tag] = f1().bootstrap_axis(rows, "author_mult", seed=seed_counter)
        slopes[kappa_tag] = local_slopes(rows, "author_mult")
        seed_counter += 1

    fit_k10 = fit_point["k10"]
    if fit_k10.get("status") == "FITTED":
        log_odds_32 = fit_k10["intercept"] + fit_k10["exponent"] * math.log10(float(HOLDOUT_AUTHOR_MULT))
        odds = 10.0 ** log_odds_32
        holdout_prediction = {
            "cell": f"authors_x{HOLDOUT_AUTHOR_MULT}_holdout_{DESIGN}_k10",
            "based_on_fit_status": fit_k10["status"],
            "log10_odds_pred": float(log_odds_32),
            "agreement_pred": float(odds / (1.0 + odds)),
            "factor2_band_log10": float(math.log10(2.0)),
        }
    else:
        holdout_prediction = {
            "cell": f"authors_x{HOLDOUT_AUTHOR_MULT}_holdout_{DESIGN}_k10",
            "status": "AUTHOR_AXIS_NOT_FITTED_HOLDOUT_IS_A_PROBE",
            "fit_status": fit_k10.get("status"),
        }

    monotone_decline_k10 = is_monotone_decline(slopes["k10"])

    prediction = {
        "banner": BANNER,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "fit_point": fit_point,
        "bootstrap_marginal": boot_marginal,
        "local_slopes": slopes,
        "monotone_decline_k10": monotone_decline_k10,
        "holdout_prediction": holdout_prediction,
        "base_n_retained": BASE_N_RETAINED,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "prediction.json").write_text(json.dumps(prediction, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(prediction, indent=2, default=str))
    return prediction


def run_holdout(knobs: dict[str, Any], knob_tag: str, workers: int, draws: int) -> None:
    if not (OUT / "prediction.json").exists():
        raise AssertionError(
            "prediction.json missing: the held-out cell must be computed AFTER the "
            "law's prediction is persisted (mirrors M4-F1's/M4-F3's own predict-then-"
            "holdout discipline)."
        )
    tasks = build_holdout_task(knobs, knob_tag, draws)
    cell = tasks[0]["cell"]
    path = OUT / f"cell_{cell}.csv"
    if path.exists():
        print(f"[skip] {cell} exists")
        return
    started = time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(f3().run_sweep_world, tasks))
    _write_cell(cell, rows, started)


# ---------------------------------------------------------------------------
# Adjudication -- exactly the registered leans/pivot, no more.

def adjudicate(prediction: dict[str, Any], holdout_summary: dict[str, Any]) -> dict[str, Any]:
    fit_k10 = prediction["fit_point"]["k10"]
    boot_k10 = prediction["bootstrap_marginal"]["k10"]
    slopes_k10 = prediction["local_slopes"]["k10"]
    monotone_decline = prediction["monotone_decline_k10"]
    status_k10 = fit_k10.get("status")

    ci = boot_k10.get("exponent_ci95")
    ci_lower_above_half = bool(ci is not None and ci[0] > 0.5)
    lean_a_hold = bool(status_k10 == "FITTED" and ci_lower_above_half and not monotone_decline)
    lean_a: dict[str, Any] = {
        "lean": "a",
        "rule": "FITTED status at authors x{1..16}, shared/kappa=1.0, bootstrap exponent "
        "CI lower edge > 0.5, and no monotone decline of the local slope",
        "status": status_k10,
        "exponent_point": fit_k10.get("exponent"),
        "exponent_ci95": ci,
        "ci_lower_above_half": ci_lower_above_half,
        "local_slopes": slopes_k10,
        "monotone_decline": monotone_decline,
        "verdict": "HOLD" if lean_a_hold else "MISS",
    }

    budget = fit_k10.get("half_agreement_mult")
    lean_b_hold = bool(status_k10 == "FITTED" and budget is not None and budget < 100.0)
    lean_b: dict[str, Any] = {
        "lean": "b",
        "rule": ".5-agreement author budget extrapolates below 100x the current base "
        f"panel (base n_retained={BASE_N_RETAINED})",
        "status": status_k10,
        "half_agreement_mult": budget,
        "implied_authors": (float(budget) * BASE_N_RETAINED) if budget is not None else None,
        "log10_half_agreement_mult": fit_k10.get("log10_half_agreement_mult"),
        "compare_m4f1_free_response_events_budget": None,
        "verdict": "HOLD" if lean_b_hold else "MISS",
    }
    if status_k10 != "FITTED":
        lean_b["note"] = (
            f"authors axis (shared, kappa=1.0) fit status is {status_k10}, not FITTED "
            "(>=3 qualifying cells); a DEGENERATE/UNFITTABLE fit cannot license a HOLD "
            "budget claim, mirroring M4-F1's/M4-F3's own lean discipline (no manufactured "
            "exponent)."
        )
    try:
        f1_decision = json.loads((F1_OUT / "decision.json").read_text(encoding="utf-8"))
        lean_b["compare_m4f1_free_response_events_budget"] = f1_decision["fits"]["events"].get(
            "half_agreement_mult"
        )
    except Exception:
        pass

    holdout_pred = prediction["holdout_prediction"]
    within_factor2 = False
    log_odds_obs = None
    holdout_gap = None
    below_half_prediction = False
    if "log10_odds_pred" in holdout_pred:
        observed_ok = holdout_summary["agreement_mean"] > 0
        if observed_ok:
            log_odds_obs = f1()._log_odds(holdout_summary["agreement_mean"])
            holdout_gap = log_odds_obs - holdout_pred["log10_odds_pred"]
            within_factor2 = bool(abs(holdout_gap) <= math.log10(2.0))
            below_half_prediction = bool(holdout_gap < -math.log10(2.0))
        else:
            # agreement_mean <= 0 clips to a very negative log-odds via f1()._log_odds;
            # treat explicitly as "far below prediction" rather than skipping the check.
            log_odds_obs = f1()._log_odds(holdout_summary["agreement_mean"])
            holdout_gap = log_odds_obs - holdout_pred["log10_odds_pred"]
            below_half_prediction = True
    lean_c: dict[str, Any] = {
        "lean": "c",
        "rule": "the held-out authors x32 cell (kappa=1.0, shared) validates the fitted "
        "law within factor 2",
        "holdout_prediction": holdout_pred,
        "agreement_obs": holdout_summary["agreement_mean"],
        "agreement_se": holdout_summary["agreement_se"],
        "log10_odds_obs": log_odds_obs,
        "holdout_log_odds_gap": holdout_gap,
        "within_factor2": within_factor2,
        "verdict": "HOLD" if (within_factor2 and status_k10 == "FITTED") else "MISS",
    }

    pivot_reasons = []
    if monotone_decline:
        pivot_reasons.append("local slope declines monotonically across the swept range")
    if below_half_prediction:
        pivot_reasons.append("x32 holdout falls below half the fitted prediction")
    if status_k10 != "FITTED":
        pivot_reasons.append(f"fit status is {status_k10}, not FITTED")
    pivot_fires = bool(pivot_reasons)
    pivot: dict[str, Any] = {
        "registered_rule": "local slope declines monotonically, OR x32 holdout falls "
        "below half the fitted prediction, OR fit status is not FITTED -> SATURATION",
        "monotone_decline": monotone_decline,
        "below_half_prediction": below_half_prediction,
        "fit_status": status_k10,
        "reasons_fired": pivot_reasons,
        "fires": pivot_fires,
    }

    kappa05_context = {
        "note": "kappa=0.5 is the registered robustness axis; it gates no lean or the "
        "pivot (all three leans, the budget claim, the holdout, and the pivot are "
        "specified at kappa=1.0 only, mirroring M4-F3's own treatment of its "
        "non-decisive kappa) and is reported for context.",
        "fit_point": prediction["fit_point"]["k05"],
        "bootstrap_marginal": prediction["bootstrap_marginal"]["k05"],
        "local_slopes": prediction["local_slopes"]["k05"],
    }

    if pivot_fires:
        verdict = "SATURATION_PANEL_LINE_CLOSES_M4E2_NO_PANEL_SIDE_ESCAPE"
    elif lean_a_hold and lean_b_hold and lean_c["verdict"] == "HOLD":
        verdict = "AUTHOR_AXIS_LAW_EXTENDS_FEASIBLE_D3_VIA_RECRUITMENT"
    else:
        verdict = "MIXED_SEE_LEAN_ADJUDICATION"

    return {
        "lean_a": lean_a, "lean_b": lean_b, "lean_c": lean_c,
        "pivot": pivot, "verdict": verdict,
        "kappa_0_5_context": kappa05_context,
    }


def run_finalize(null_mults: list[int], null_kappa_tags: list[str]) -> None:
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    prediction = json.loads((OUT / "prediction.json").read_text(encoding="utf-8"))
    holdout_cell = f"authors_x{HOLDOUT_AUTHOR_MULT}_holdout_{DESIGN}_k10"
    holdout_summary = cell_summary(holdout_cell)
    adjudication = adjudicate(prediction, holdout_summary)

    all_cells = [cell_name_live(m, kt) for m in AUTHOR_MULTS for kt, _ in KAPPAS]
    all_cells.append(holdout_cell)
    summary_rows = [
        {k: v for k, v in cell_summary(cell).items() if k not in ("world_seeds", "world_values")}
        for cell in all_cells
    ]
    pd.DataFrame(summary_rows).to_csv(OUT / "cells.csv", index=False)

    null_rows = [
        {k: v for k, v in cell_summary(cell_name_null(m, kt)).items() if k not in ("world_seeds", "world_values")}
        for m in null_mults for kt in null_kappa_tags
    ]
    pd.DataFrame(null_rows).to_csv(OUT / "null_cells.csv", index=False)

    decision = {
        "experiment": "M4-F4_author_axis_law_or_artifact",
        "banner": BANNER,
        "tier": "EXPLORATORY",
        "registered_spec": (
            "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md#M4-F4-registration"
        ),
        "part0_registered_in": "reports/SUICA_M4_F4_AUTHOR_AXIS_REPORT.md Part 0 (before run)",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "worlds_per_cell": WORLDS_PER_CELL,
        "draws_per_world": DRAWS,
        "gates": {k: (v["pass"] if isinstance(v, dict) and "pass" in v else v) for k, v in gates.items()},
        "gates_all_pass": gates["all_pass"],
        "prediction": prediction,
        "holdout_observed": {
            k: v for k, v in holdout_summary.items() if k not in ("world_seeds", "world_values")
        },
        "adjudication": adjudication,
        "label_free": True,
        "claim_boundary": (
            "Synthetic author-axis finding in a world calibrated to the opened PANDORA "
            "D-panel regime; licenses a D3 panel-DESIGN prior only (whether RECRUITING "
            "MORE AUTHORS onto shared occasions is a feasible certification path). No "
            "claim about the real relation field's content, personality, emotion, "
            "diagnosis, or any individual."
        ),
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(adjudication, indent=2, default=str))


# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=["sweep-live", "sweep-null", "gates", "predict", "holdout", "finalize", "all"],
        default="all",
    )
    parser.add_argument("--workers", type=int, default=max(2, min(6, (os.cpu_count() or 4) - 2)))
    parser.add_argument("--draws", type=int, default=DRAWS)
    parser.add_argument("--author-mults", type=str, default="1,2,4,8,16")
    parser.add_argument("--kappas", type=str, default="k05,k10")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if not REF_PATH.exists():
        raise AssertionError(f"{REF_PATH} missing (M4-F1 artifact required, read-only).")
    if not F1_CELLS_CSV.exists():
        raise AssertionError(f"{F1_CELLS_CSV} missing (M4-F1 artifact required, read-only).")
    if not F3_CELLS_CSV.exists():
        raise AssertionError(f"{F3_CELLS_CSV} missing (M4-F3 artifact required, read-only).")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

    f1_cal = json.loads(F1_CALIBRATION.read_text(encoding="utf-8"))
    if f1_cal["status"] != "CALIBRATED":
        raise AssertionError("M4-F1 calibration_record.json is not CALIBRATED.")
    knobs = f1_cal["selected"]["knobs"]
    knob_tag = f1().knob_tag(knobs)

    mults = [int(x) for x in args.author_mults.split(",") if x]
    kappa_tags = {x for x in args.kappas.split(",") if x}

    if args.stage in ("sweep-live", "all"):
        run_sweep_live(knobs, knob_tag, args.workers, args.draws, mults, kappa_tags)
    if args.stage in ("sweep-null", "all"):
        run_sweep_null(knobs, knob_tag, args.workers, args.draws, mults, kappa_tags)
    if args.stage in ("gates", "all"):
        run_gates(knobs, knob_tag, args.workers, AUTHOR_MULTS, [t for t, _ in KAPPAS])
    if args.stage in ("predict", "all"):
        if not (OUT / "prediction.json").exists():
            run_predict()
        else:
            print("[skip] prediction.json exists")
    if args.stage in ("holdout", "all"):
        run_holdout(knobs, knob_tag, args.workers, args.draws)
    if args.stage in ("finalize", "all"):
        run_finalize(AUTHOR_MULTS, [t for t, _ in KAPPAS])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
