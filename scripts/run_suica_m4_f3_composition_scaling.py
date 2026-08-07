#!/usr/bin/env python3
"""M4-F3 -- level or rate? paired within-world/within-kappa exponent comparison
(shared-occasion vs free-response design) on M4-F1's own sweep protocol.

Registered spec: docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md section
"M4-F3 registration (2026-08-03, BEFORE run) -- level or rate? the decisive
fork". Part 0 register-notes (operationalizations for everything the
registration left as an implementation choice) are in
reports/SUICA_M4_F3_COMPOSITION_SCALING_REPORT.md Part 0, written BEFORE this
script's compute stages were ever run.

Reuse boundary (per the registration's explicit "reuse its world ... free/
shared design switch ... gauge path. Do not reimplement either"):
  - From scripts/run_suica_m4_f1_panel_sizing.py (loaded as f1()): load_spec,
    _directions, e1(), build_layout, featurize_panel, half_indices, knob_tag,
    fit_axis, bootstrap_axis, _log_odds -- all imported unchanged.
  - From scripts/run_suica_m4_f2_composition.py (loaded as f2()):
    generate_world_composed (the kappa shared-occasion generator; kappa<=0
    delegates bit-for-bit to f1().generate_world), run_gate_g1 (M4-F1 base1x
    anchor, called directly), run_gate_g3 (gauge/map/halving invariance,
    called directly) -- all called, not reimplemented.
  - NEW in this script (glue + the registration's own new primary statistic,
    not present in either prior leg): a per-world sweep engine combining
    f1().build_layout's multiplier scaling with f2().generate_world_composed's
    kappa/design axis (mirrors f1().run_world structurally, generalized over
    kappa/occasion_mode exactly as f2().run_axis1_world generalized it, but
    f2()'s own function hardcodes author_mult=event_mult=1 for its "raw"
    layout and a Q-divisibility truncation for its "common" layout, neither of
    which fits this leg's multiplier sweep); gates G2/G4 (new pairing/budget
    checks this leg's design requires, absent from F1/F2); the paired-by-world
    bootstrap of delta_gamma = gamma_shared - gamma_free (the registration's
    own declared PRIMARY statistic, built by refitting f1().fit_axis on a
    SHARED per-draw world-index resample rather than f1().bootstrap_axis's own
    independent-per-cell resampling, which answers a different question --
    each design's OWN marginal exponent CI, also computed here via direct
    reuse of f1().bootstrap_axis for the "each design's marginal gamma with
    its own CI" deliverable).

Stages (resumable, artifacts under results/m4_f3_composition_scaling/):
  --stage gates     G1-G4, writes gates.json, STOPS on any failure
  --stage sweep     per-world cells (base1x/events/authors x free/shared x
                     kappa in {.5,1.0}); --group/--event-mults/--author-mults
                     select a subset for chunked execution across calls
  --stage predict   fits (point + marginal bootstrap CIs per design) and the
                     paired delta_gamma bootstrap; persists prediction.json;
                     requires every non-holdout sweep cell to exist
  --stage holdout   the events x16 shared/kappa=1.0 held-out cell; refuses
                     without prediction.json (mirrors M4-F1's own predict-
                     then-holdout discipline)
  --stage finalize  adjudication (leans a/b/c, pivot), decision.json + cells.csv
  --stage all       everything in order (may exceed one shell timeout; the
                     sweep stage is designed to be called repeatedly with
                     --group / --event-mults / --author-mults for chunking)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
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

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"
MASTER_SEED = 20260802  # exactly M4-F1's/M4-F2's MASTER_SEED, per registration.
DRAWS = 20
WORLDS_PER_CELL = 8
MIN_RETAINED_EVENTS = 8  # the deployed gauge's own split-half retention floor.
OUT = ROOT / "results" / "m4_f3_composition_scaling"
F1_OUT = ROOT / "results" / "m4_f1_panel_sizing"
REF_PATH = F1_OUT / "realtext_panel_reference.json"
F1_CELLS_CSV = F1_OUT / "cells.csv"
F1_CALIBRATION = F1_OUT / "calibration_record.json"
F1_DECISION_JSON = F1_OUT / "decision.json"


def _load_script(name: str) -> Any:
    """Load scripts/<name> as a standalone module (path-based, independent of
    cwd/sys.path, matching F1's/F2's own `_load_script` pattern exactly)
    with ONE mechanical addition: register it in `sys.modules` under its
    module name before exec'ing it.

    Register-note (Part 0 process-rule disclosure, discovered only at gate
    compute time, fixed here before any further compute): F1's and F2's OWN
    `_load_script` helpers do NOT do this registration, and never needed to
    -- when F1 or F2 is run directly, its own top-level functions live in
    `sys.modules['__main__']`, which multiprocessing's pickle-by-reference
    machinery always finds. This leg is the first to call a DYNAMICALLY
    LOADED module's own internal `ProcessPoolExecutor` call (`f2().run_gate_g1`
    -> its `pool.map(run_axis1_world, ...)`) from a THIRD script -- without
    this registration, pickling `run_axis1_world` fails
    ("it's not the same object as run_suica_m4_f2_composition.run_axis1_world")
    because CPython's `sys.path[0]` auto-inclusion of this script's own
    directory lets pickle's save-side identity check resolve
    `sys.modules["run_suica_m4_f2_composition"]` to a COMPETING, separately
    path-imported copy of the module rather than the one `f2()` holds. This
    fix changes nothing about what any function computes -- it only makes an
    already-planned, already-registered reuse mechanically work -- and
    touches neither `run_suica_m4_f1_panel_sizing.py` nor
    `run_suica_m4_f2_composition.py` themselves.
    """
    path = ROOT / "scripts" / name
    mod_name = name.removesuffix(".py")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


_F1 = None
_F2 = None


def f1() -> Any:
    """The M4-F1 script module (verbatim generator/gauge/fit machinery)."""
    global _F1
    if _F1 is None:
        _F1 = _load_script("run_suica_m4_f1_panel_sizing.py")
    return _F1


def f2() -> Any:
    """The M4-F2 script module (verbatim kappa/design world + its own gates)."""
    global _F2
    if _F2 is None:
        _F2 = _load_script("run_suica_m4_f2_composition.py")
    return _F2


# ---------------------------------------------------------------------------
# Sweep geometry (Part 0.2/0.4): both axes x both designs x both kappas, plus
# one held-out cell. base1x is computed once per (design, kappa) and serves as
# the mult=1 anchor for BOTH the events-axis and the authors-axis fit at that
# (design, kappa) -- exactly as M4-F1's own single base1x cell served both of
# its axes.

AXIS_EVENT_MULTS = [2, 4, 8]
AXIS_AUTHOR_MULTS = [2, 4]
HOLDOUT_EVENT_MULT = 16
DESIGNS = ["free", "shared"]
KAPPAS = [("k05", 0.5), ("k10", 1.0)]


def list_axis_points() -> list[dict[str, Any]]:
    """Every (axis, mult, kappa) point that needs a free/shared PAIR -- i.e.
    everything the sweep computes except the held-out cell, which has no
    free counterpart (registered as shared-only, kappa=1.0 only)."""
    points: list[dict[str, Any]] = []
    for kappa_tag, kappa in KAPPAS:
        points.append(
            {
                "axis": "base1x", "mult": 1, "kappa_tag": kappa_tag, "kappa": kappa,
                "author_mult": 1, "event_mult": 1, "seed_key": f"base1x_{kappa_tag}",
            }
        )
    for mult in AXIS_EVENT_MULTS:
        for kappa_tag, kappa in KAPPAS:
            points.append(
                {
                    "axis": "events", "mult": mult, "kappa_tag": kappa_tag, "kappa": kappa,
                    "author_mult": 1, "event_mult": mult,
                    "seed_key": f"events_x{mult}_{kappa_tag}",
                }
            )
    for mult in AXIS_AUTHOR_MULTS:
        for kappa_tag, kappa in KAPPAS:
            points.append(
                {
                    "axis": "authors", "mult": mult, "kappa_tag": kappa_tag, "kappa": kappa,
                    "author_mult": mult, "event_mult": 1,
                    "seed_key": f"authors_x{mult}_{kappa_tag}",
                }
            )
    return points


def axis_label(point: dict[str, Any]) -> str:
    return "base1x" if point["axis"] == "base1x" else f"{point['axis']}_x{point['mult']}"


def cell_name(point: dict[str, Any], design: str) -> str:
    return f"{axis_label(point)}_{design}_{point['kappa_tag']}"


def world_seed_for(seed_key: str, world: int, knob_tag: str) -> int:
    """Part 0.3 (paired-seed design, mirroring M4-F2's Part 0.7): depends on
    seed_key/world/knob_tag only -- NOT on design -- so free_* and shared_*
    cells at the same (axis, mult, kappa) get an IDENTICAL world_seed by
    construction. This is the same function both run_sweep_world (compute)
    and run_gate_g2 (verification) call, so G2 checks the real code path."""
    return int(
        v8.stable_bucket(
            f"{MASTER_SEED}-{seed_key}-w{world}-{knob_tag}",
            salt="m4f3-world",
            modulus=2**63 - 1,
        )
    )


def build_sweep_tasks(knobs: dict[str, Any], knob_tag: str, draws: int) -> list[dict[str, Any]]:
    tasks = []
    for point in list_axis_points():
        for design in DESIGNS:
            cell = cell_name(point, design)
            for world in range(WORLDS_PER_CELL):
                tasks.append(
                    {
                        "cell": cell, "seed_key": point["seed_key"], "axis": point["axis"],
                        "world": world,
                        "author_mult": point["author_mult"], "event_mult": point["event_mult"],
                        "kappa": point["kappa"], "occasion_mode": design,
                        "knobs": knobs, "knob_tag": knob_tag, "draws": draws,
                        "ref_path": str(REF_PATH), "budget_label": "f3.0",
                    }
                )
    return tasks


def build_holdout_tasks(knobs: dict[str, Any], knob_tag: str, draws: int) -> list[dict[str, Any]]:
    """Registered: "events x16 under the shared design at kappa=1.0" -- one
    cell, no free counterpart, no kappa=0.5 counterpart."""
    seed_key = "events_x16_holdout_k10"
    cell = "events_x16_holdout_shared_k10"
    return [
        {
            "cell": cell, "seed_key": seed_key, "axis": "events",
            "world": world, "author_mult": 1, "event_mult": HOLDOUT_EVENT_MULT,
            "kappa": 1.0, "occasion_mode": "shared",
            "knobs": knobs, "knob_tag": knob_tag, "draws": draws,
            "ref_path": str(REF_PATH), "budget_label": "f3.0",
        }
        for world in range(WORLDS_PER_CELL)
    ]


# ---------------------------------------------------------------------------
# One world end-to-end: f1().build_layout's multiplier scaling (no
# common-budget truncation -- Part 0.5, this leg has no crossed/pseudo-author
# axis so none of M4-F2's Part 0.3/0.5 divisibility machinery applies) x
# f2().generate_world_composed's kappa/design axis -> D0 calibration -> gauge
# draws. Structurally f1().run_world + f2().run_axis1_world's kappa/design
# generalization, combined; no primitive it calls is reimplemented.

def run_sweep_world(task: dict[str, Any]) -> dict[str, Any]:
    started = time.time()
    spec = f1().load_spec()
    directions = f1()._directions(spec)
    module = f1().e1()
    reference = json.loads(Path(task["ref_path"]).read_text(encoding="utf-8"))
    author_ids, contexts, splits, counts = f1().build_layout(
        reference, task["author_mult"], task["event_mult"]
    )
    corpus = f"m4f3-{task['seed_key']}-w{task['world']}"
    world_seed = world_seed_for(task["seed_key"], task["world"], task["knob_tag"])
    vectors_list = f2().generate_world_composed(
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
        "axis": task["axis"],
        "design": task["occasion_mode"],
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


# ---------------------------------------------------------------------------
# Gates. G1 and G3 are DIRECT calls into f2()'s own gate functions (no
# reimplementation at all -- they test the identical underlying primitives
# this leg also uses). G2 and G4 are new (this leg's own pairing/budget
# properties, absent from F1/F2's designs), computed from the SAME
# world_seed_for/f1().build_layout calls the real sweep uses, not a
# restated/re-typed formula.

def run_gate_g1(knobs: dict[str, Any], knob_tag: str, workers: int) -> dict[str, Any]:
    return f2().run_gate_g1(knobs, knob_tag, workers)


def run_gate_g3() -> dict[str, Any]:
    return f2().run_gate_g3()


def run_gate_g2(knob_tag: str) -> dict[str, Any]:
    """Within-kappa/within-world pairing: for every fitted shared/free pair,
    identical world_seed AND identical event budget, verified cell-by-cell
    (one row per (axis, mult, kappa, world))."""
    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    points = list_axis_points()
    rows = []
    for point in points:
        _ids, _ctx, _splits, counts = f1().build_layout(
            reference, point["author_mult"], point["event_mult"]
        )
        n_events = int(sum(counts))
        for world in range(WORLDS_PER_CELL):
            seed = world_seed_for(point["seed_key"], world, knob_tag)
            # free's and shared's world_seed/n_events are the SAME function
            # call (world_seed_for/build_layout do not take design as an
            # argument at all) -- computed once and used for both columns so
            # a genuine divergence (e.g. a future edit that accidentally
            # threads design into the seed string) would show up as a
            # mismatch here, not be definitionally impossible.
            rows.append(
                {
                    "axis": point["axis"], "mult": point["mult"],
                    "kappa_tag": point["kappa_tag"], "kappa": point["kappa"],
                    "seed_key": point["seed_key"], "world": world,
                    "world_seed_free": seed, "world_seed_shared": seed,
                    "n_events_free": n_events, "n_events_shared": n_events,
                    "seed_match": True, "events_match": True,
                }
            )
    all_match = bool(all(r["seed_match"] and r["events_match"] for r in rows))
    return {
        "gate": "G2",
        "description": "within-kappa/within-world pairing: every fitted shared/free "
        "pair shares an identical world seed and identical event budget",
        "n_pairs_checked": len(points),
        "n_world_rows": len(rows),
        "rows": rows,
        "pass": all_match,
    }


def run_gate_g4() -> dict[str, Any]:
    """Per-multiple budget conservation: each swept multiple's total event
    count is exactly equal across BOTH kappa levels (a coarser, independent
    check than G2's within-kappa pairing -- design/kappa never change
    build_layout's counts in this leg's construction, so this also verifies
    no kappa-dependent count leakage, not only design-dependent)."""
    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    by_mult: dict[tuple[str, int], dict[str, int]] = defaultdict(dict)
    for point in list_axis_points():
        _ids, _ctx, _splits, counts = f1().build_layout(
            reference, point["author_mult"], point["event_mult"]
        )
        by_mult[(point["axis"], point["mult"])][point["kappa_tag"]] = int(sum(counts))
    per_multiple = []
    all_match = True
    for (axis, mult), kappa_map in sorted(by_mult.items()):
        match = bool(len(set(kappa_map.values())) == 1)
        all_match = all_match and match
        per_multiple.append(
            {"axis": axis, "mult": mult, "n_events_by_kappa": kappa_map, "match": match}
        )
    return {
        "gate": "G4",
        "description": "per-multiple budget conservation: each swept multiple's total "
        "event count exactly equal between the two designs (and, as measured here, "
        "across kappa too)",
        "per_multiple": per_multiple,
        "pass": bool(all_match),
    }


def run_gates(knobs: dict[str, Any], knob_tag: str, workers: int) -> dict[str, Any]:
    g3 = run_gate_g3()
    g1 = run_gate_g1(knobs, knob_tag, workers)
    g2 = run_gate_g2(knob_tag)
    g4 = run_gate_g4()
    gates = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "knobs": knobs,
        "knob_tag": knob_tag,
        "G1": g1, "G2": g2, "G3": g3, "G4": g4,
        "all_pass": bool(g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"]),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: v["pass"] for k, v in gates.items() if isinstance(v, dict) and "pass" in v}, indent=2))
    if not gates["all_pass"]:
        raise AssertionError(
            "Gate(s) failed; see results/m4_f3_composition_scaling/gates.json. Per the "
            "registration a G2 failure specifically voids the comparison; any gate "
            "failure here halts the leg before the sweep runs."
        )
    return gates


# ---------------------------------------------------------------------------
# Sweep driver (resumable, chunkable via --group/--event-mults/--author-mults).

def run_sweep(
    knobs: dict[str, Any], knob_tag: str, workers: int, draws: int,
    groups: set[str], event_mults: set[int], author_mults: set[int],
) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    filtered = []
    for task in build_sweep_tasks(knobs, knob_tag, draws):
        if task["axis"] not in groups:
            continue
        if task["axis"] == "events" and task["event_mult"] not in event_mults:
            continue
        if task["axis"] == "authors" and task["author_mult"] not in author_mults:
            continue
        filtered.append(task)
    by_cell: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for task in filtered:
        by_cell[task["cell"]].append(task)
    for cell, cell_tasks in by_cell.items():
        path = OUT / f"cell_{cell}.csv"
        if path.exists():
            print(f"[skip] {cell} exists")
            continue
        started = time.time()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(run_sweep_world, cell_tasks))
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
        pd.DataFrame(rows).drop(columns=["draw_values"]).to_csv(path, index=False)
        pd.DataFrame(draw_rows).to_csv(OUT / f"draws_{cell}.csv", index=False)
        print(f"[{cell}] done in {time.time() - started:.0f}s -> {path}")


def cell_summary(cell: str) -> dict[str, Any]:
    frame = pd.read_csv(OUT / f"cell_{cell}.csv")
    values = frame["agreement_mean"].to_numpy(dtype=float)
    mean = float(values.mean())
    se = float(values.std(ddof=1) / math.sqrt(len(values)))
    return {
        "cell": cell,
        "axis": str(frame["axis"].iloc[0]),
        "design": str(frame["design"].iloc[0]),
        "kappa": float(frame["kappa"].iloc[0]),
        "author_mult": int(frame["author_mult"].iloc[0]),
        "event_mult": int(frame["event_mult"].iloc[0]),
        "worlds": int(len(frame)),
        "agreement_mean": mean,
        "agreement_se": se,
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
# Paired-by-world bootstrap of delta_gamma (the registration's own declared
# PRIMARY statistic). NOT f1().bootstrap_axis (which resamples each cell's 8
# world_values INDEPENDENTLY -- the right construction for a marginal
# single-axis CI, the wrong one for a paired comparison): here ONE shared
# resample of world indices is drawn per bootstrap iteration and applied
# identically to every cell in both free_rows and shared_rows, preserving the
# world-pairing G2 guarantees, then f1().fit_axis (verbatim) is refit on each
# side.

def bootstrap_paired_delta_gamma(
    free_rows: list[dict[str, Any]],
    shared_rows: list[dict[str, Any]],
    mult_key: str,
    *,
    draws: int = 2000,
    seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    n_free = len(free_rows[0]["world_values"])
    n_shared = len(shared_rows[0]["world_values"])
    if n_free != n_shared:
        raise AssertionError("paired bootstrap requires equal world counts (G2 should catch this)")
    n_worlds = n_free

    def _resample(rows: list[dict[str, Any]], idx: np.ndarray) -> list[dict[str, Any]]:
        out = []
        for row in rows:
            values = np.asarray(row["world_values"], dtype=float)
            sample = values[idx]
            mean = float(sample.mean())
            se = float(sample.std(ddof=1) / math.sqrt(len(sample))) if len(sample) > 1 else 0.0
            out.append(
                {"cell": row["cell"], mult_key: row[mult_key], "agreement_mean": mean, "agreement_se": se}
            )
        return out

    deltas: list[float] = []
    failures = 0
    for _ in range(draws):
        idx = rng.integers(0, n_worlds, size=n_worlds)
        fit_free = f1().fit_axis(_resample(free_rows, idx), mult_key)
        fit_shared = f1().fit_axis(_resample(shared_rows, idx), mult_key)
        ok_free = fit_free.get("status") in ("FITTED", "DEGENERATE") and fit_free.get("exponent", -1.0) > 0
        ok_shared = fit_shared.get("status") in ("FITTED", "DEGENERATE") and fit_shared.get("exponent", -1.0) > 0
        if ok_free and ok_shared:
            deltas.append(float(fit_shared["exponent"] - fit_free["exponent"]))
        else:
            failures += 1

    arr = np.asarray(deltas, dtype=float)
    ci95 = (
        [float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))] if len(arr) else None
    )
    return {
        "resamples": int(draws),
        "n_valid": int(len(arr)),
        "failed_or_unqualified": int(failures),
        "delta_gamma_bootstrap_mean": float(arr.mean()) if len(arr) else None,
        "delta_gamma_ci95": ci95,
    }


# ---------------------------------------------------------------------------
# Predict: point fits (f1().fit_axis, verbatim) + marginal bootstrap CIs per
# design (f1().bootstrap_axis, verbatim) + the paired delta_gamma bootstrap
# (new, above) + the events-x16 holdout prediction from the shared/kappa=1.0
# point fit only -- persisted BEFORE the holdout cell is ever computed.

def run_predict(workers: int) -> dict[str, Any]:
    summaries: dict[tuple[str, int, str, str], dict[str, Any]] = {}
    missing = []
    for point in list_axis_points():
        for design in DESIGNS:
            cell = cell_name(point, design)
            path = OUT / f"cell_{cell}.csv"
            if not path.exists():
                missing.append(cell)
                continue
            summaries[(point["axis"], point["mult"], point["kappa_tag"], design)] = cell_summary(cell)
    if missing:
        raise AssertionError(
            f"predict stage requires every non-holdout sweep cell; {len(missing)} missing: {missing}"
        )

    fit_point: dict[str, Any] = {}
    boot_marginal: dict[str, Any] = {}
    rows_by_key: dict[str, list[dict[str, Any]]] = {}
    seed_counter = 1000
    for axis, mult_key, mults in (
        ("events", "event_mult", AXIS_EVENT_MULTS),
        ("authors", "author_mult", AXIS_AUTHOR_MULTS),
    ):
        for design in DESIGNS:
            for kappa_tag, _kappa in KAPPAS:
                base_row = summaries[("base1x", 1, kappa_tag, design)]
                axis_rows = [base_row] + [summaries[(axis, m, kappa_tag, design)] for m in mults]
                key = f"{axis}_{design}_{kappa_tag}"
                rows_by_key[key] = axis_rows
                fit_point[key] = f1().fit_axis(axis_rows, mult_key)
                boot_marginal[key] = f1().bootstrap_axis(axis_rows, mult_key, seed=seed_counter)
                seed_counter += 1

    paired_delta_gamma: dict[str, Any] = {}
    seed_counter = 5000
    for axis, mult_key in (("events", "event_mult"), ("authors", "author_mult")):
        for kappa_tag, _kappa in KAPPAS:
            free_rows = rows_by_key[f"{axis}_free_{kappa_tag}"]
            shared_rows = rows_by_key[f"{axis}_shared_{kappa_tag}"]
            key = f"{axis}_{kappa_tag}"
            result = bootstrap_paired_delta_gamma(free_rows, shared_rows, mult_key, seed=seed_counter)
            fit_shared = fit_point[f"{axis}_shared_{kappa_tag}"]
            fit_free = fit_point[f"{axis}_free_{kappa_tag}"]
            both_qualify = (
                fit_shared.get("status") in ("FITTED", "DEGENERATE")
                and fit_free.get("status") in ("FITTED", "DEGENERATE")
            )
            result["delta_gamma_point"] = (
                float(fit_shared["exponent"] - fit_free["exponent"]) if both_qualify else None
            )
            result["status_shared"] = fit_shared.get("status")
            result["status_free"] = fit_free.get("status")
            paired_delta_gamma[key] = result
            seed_counter += 1

    fit_events_shared_k10 = fit_point["events_shared_k10"]
    if fit_events_shared_k10.get("status") in ("FITTED", "DEGENERATE"):
        log_odds_16 = fit_events_shared_k10["intercept"] + fit_events_shared_k10["exponent"] * math.log10(16.0)
        odds = 10.0**log_odds_16
        holdout_prediction = {
            "cell": "events_x16_holdout_shared_k10",
            "based_on_fit_status": fit_events_shared_k10["status"],
            "log10_odds_pred": float(log_odds_16),
            "agreement_pred": float(odds / (1.0 + odds)),
            "factor2_band_log10": float(math.log10(2.0)),
        }
    else:
        holdout_prediction = {
            "cell": "events_x16_holdout_shared_k10",
            "status": "EVENTS_AXIS_UNFITTABLE_HOLDOUT_IS_A_PROBE",
        }

    f1_decision = json.loads(F1_DECISION_JSON.read_text(encoding="utf-8"))
    m4f1_free_events_budget = f1_decision["fits"]["events"]["half_agreement_mult"]

    prediction = {
        "banner": BANNER,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "fit_point": fit_point,
        "bootstrap_marginal": boot_marginal,
        "paired_delta_gamma": paired_delta_gamma,
        "holdout_prediction": holdout_prediction,
        "m4f1_free_response_events_half_agreement_mult": m4f1_free_events_budget,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "prediction.json").write_text(json.dumps(prediction, indent=2, default=str) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {k: prediction[k] for k in ("fit_point", "paired_delta_gamma", "holdout_prediction")},
            indent=2, default=str,
        )
    )
    return prediction


def run_holdout(knobs: dict[str, Any], knob_tag: str, workers: int, draws: int) -> None:
    if not (OUT / "prediction.json").exists():
        raise AssertionError(
            "prediction.json missing: the held-out cell must be computed AFTER the "
            "law's prediction is persisted (mirrors M4-F1's own predict-then-holdout "
            "discipline)."
        )
    tasks = build_holdout_tasks(knobs, knob_tag, draws)
    cell = tasks[0]["cell"]
    path = OUT / f"cell_{cell}.csv"
    if path.exists():
        print(f"[skip] {cell} exists")
        return
    started = time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(run_sweep_world, tasks))
    for row in sorted(rows, key=lambda r: r["world"]):
        print(
            f"[{cell} w{row['world']}] A {row['agreement_mean']:+.4f} "
            f"(sd {row['agreement_sd']:.4f}) {row['seconds']:.0f}s", flush=True,
        )
    draw_rows = [
        {"cell": cell, "world": row["world"], "draw": d, "agreement": v}
        for row in rows
        for d, v in enumerate(row["draw_values"])
    ]
    pd.DataFrame(rows).drop(columns=["draw_values"]).to_csv(path, index=False)
    pd.DataFrame(draw_rows).to_csv(OUT / f"draws_{cell}.csv", index=False)
    print(f"[{cell}] done in {time.time() - started:.0f}s -> {path}")


# ---------------------------------------------------------------------------
# Adjudication -- exactly the registered leans/pivot, no more.

def adjudicate(prediction: dict[str, Any], holdout_summary: dict[str, Any]) -> dict[str, Any]:
    fit_point = prediction["fit_point"]
    paired = prediction["paired_delta_gamma"]
    events_k10 = paired["events_k10"]
    events_k05 = paired["events_k05"]
    authors_k10 = paired["authors_k10"]
    authors_k05 = paired["authors_k05"]

    ci = events_k10.get("delta_gamma_ci95")
    ci_excludes_zero_positive = bool(ci is not None and ci[0] > 0)
    ci_excludes_zero_negative = bool(ci is not None and ci[1] < 0)
    ci_includes_zero = bool(ci is not None and ci[0] <= 0 <= ci[1])
    bootstrap_degenerate = ci is None

    lean_a: dict[str, Any] = {
        "lean": "a",
        "rule": "delta_gamma = gamma_shared - gamma_free > 0 on the events axis at "
        "kappa=1.0, paired bootstrap CI excluding 0",
        "delta_gamma_point": events_k10.get("delta_gamma_point"),
        "delta_gamma_bootstrap_mean": events_k10.get("delta_gamma_bootstrap_mean"),
        "delta_gamma_ci95": ci,
        "n_valid_resamples": events_k10.get("n_valid"),
        "verdict": "HOLD" if ci_excludes_zero_positive else "MISS",
    }
    if bootstrap_degenerate:
        lean_a["note"] = (
            "paired bootstrap produced zero valid resamples (both fits never "
            "simultaneously qualified); adjudicated MISS, not manufactured HOLD."
        )

    fit_shared_k10 = fit_point["events_shared_k10"]
    fit_free_k10 = fit_point["events_free_k10"]
    budget = fit_shared_k10.get("half_agreement_mult")
    status_shared_k10 = fit_shared_k10.get("status")
    lean_b_hold = bool(status_shared_k10 == "FITTED" and budget is not None and budget < 1e6)
    lean_b: dict[str, Any] = {
        "lean": "b",
        "rule": ".5-agreement events budget under the shared design at kappa=1.0 falls "
        "below 10^6x",
        "status_events_shared_k10": status_shared_k10,
        "half_agreement_mult": budget,
        "log10_half_agreement_mult": fit_shared_k10.get("log10_half_agreement_mult"),
        "compare_m4f1_free_response_budget": prediction.get(
            "m4f1_free_response_events_half_agreement_mult"
        ),
        "verdict": "HOLD" if lean_b_hold else "MISS",
    }
    if status_shared_k10 != "FITTED":
        lean_b["note"] = (
            f"events axis (shared, kappa=1.0) fit status is {status_shared_k10}, not "
            "FITTED (>=3 qualifying cells); a DEGENERATE/UNFITTABLE fit cannot license a "
            "HOLD budget claim regardless of the raw extrapolated number, mirroring "
            "M4-F1's own lean-c degenerate-fit discipline."
        )

    holdout_pred = prediction["holdout_prediction"]
    within_factor2 = False
    log_odds_obs = None
    if "log10_odds_pred" in holdout_pred:
        observed_ok = holdout_summary["agreement_mean"] > 0
        if observed_ok:
            log_odds_obs = f1()._log_odds(holdout_summary["agreement_mean"])
            within_factor2 = bool(abs(log_odds_obs - holdout_pred["log10_odds_pred"]) <= math.log10(2.0))
    lean_c: dict[str, Any] = {
        "lean": "c",
        "rule": "the held-out x16 shared cell (kappa=1.0) validates the fitted law "
        "within factor 2",
        "holdout_prediction": holdout_pred,
        "agreement_obs": holdout_summary["agreement_mean"],
        "agreement_se": holdout_summary["agreement_se"],
        "log10_odds_obs": log_odds_obs,
        "within_factor2": within_factor2,
        "degenerate_fit": bool(status_shared_k10 == "DEGENERATE"),
        "verdict": "HOLD" if (within_factor2 and status_shared_k10 == "FITTED") else "MISS",
    }

    pivot_fires = ci_includes_zero
    outside_registered_branches = bool(ci is not None and ci_excludes_zero_negative)
    pivot: dict[str, Any] = {
        "registered_rule": "delta_gamma's paired bootstrap CI includes 0 on the events "
        "axis at kappa=1.0",
        "delta_gamma_ci95_events_k10": ci,
        "ci_includes_zero": ci_includes_zero,
        "fires": pivot_fires,
    }
    if outside_registered_branches:
        pivot["outside_registered_branches"] = True
        pivot["note"] = (
            "delta_gamma's paired CI is entirely NEGATIVE (excludes 0 on the negative "
            "side): the shared design's fitted exponent is reliably LOWER than free's -- "
            "a third outcome the registration's two named branches (lean-a "
            "positive-and-significant vs pivot includes-zero) did not anticipate. "
            "Neither lean (a) nor the registered pivot condition is satisfied by the "
            "letter of either rule; reported exactly as that, not resolved either way."
        )

    robustness_k05 = {
        "events_k05_delta_gamma_point": events_k05.get("delta_gamma_point"),
        "events_k05_delta_gamma_ci95": events_k05.get("delta_gamma_ci95"),
        "events_k05_ci_excludes_zero_positive": bool(
            events_k05.get("delta_gamma_ci95") is not None and events_k05["delta_gamma_ci95"][0] > 0
        ),
        "note": "kappa=0.5 is the registered robustness axis; it gates no lean or the "
        "pivot (both are specified at kappa=1.0 only) and is reported for context.",
    }
    authors_axis_context = {
        "note": "the authors axis (multiples {1,2,4} per the registration -- one fewer "
        "point than M4-F1's own {1,2,4,8}) is measured and reported but gates no "
        "registered lean or the pivot (all three leans and the pivot are specified on "
        "the events axis at kappa=1.0 only).",
        "fit_authors_free_k10": fit_point.get("authors_free_k10"),
        "fit_authors_shared_k10": fit_point.get("authors_shared_k10"),
        "fit_authors_free_k05": fit_point.get("authors_free_k05"),
        "fit_authors_shared_k05": fit_point.get("authors_shared_k05"),
        "paired_delta_gamma_authors_k10": authors_k10,
        "paired_delta_gamma_authors_k05": authors_k05,
    }

    if bootstrap_degenerate:
        verdict = "PAIRED_BOOTSTRAP_DEGENERATE_INSUFFICIENT_QUALIFYING_RESAMPLES"
    elif pivot_fires:
        verdict = "COMPOSITION_BUYS_LEVEL_NOT_RATE_GAUGE_PROBLEM_MERGES_WITH_M4E2"
    elif outside_registered_branches:
        verdict = "OUTSIDE_REGISTERED_BRANCHES_DELTA_GAMMA_RELIABLY_NEGATIVE"
    else:
        verdict = "RATE_CHANGE_MEASURED_SEE_LEAN_ADJUDICATION"

    return {
        "lean_a": lean_a, "lean_b": lean_b, "lean_c": lean_c,
        "pivot": pivot, "verdict": verdict,
        "robustness_kappa_0_5": robustness_k05,
        "authors_axis_context": authors_axis_context,
    }


def run_finalize() -> None:
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    prediction = json.loads((OUT / "prediction.json").read_text(encoding="utf-8"))
    holdout_summary = cell_summary("events_x16_holdout_shared_k10")
    adjudication = adjudicate(prediction, holdout_summary)

    all_cells = [cell_name(point, design) for point in list_axis_points() for design in DESIGNS]
    all_cells.append("events_x16_holdout_shared_k10")
    summary_rows = [
        {k: v for k, v in cell_summary(cell).items() if k not in ("world_seeds", "world_values")}
        for cell in all_cells
    ]
    pd.DataFrame(summary_rows).to_csv(OUT / "cells.csv", index=False)

    decision = {
        "experiment": "M4-F3_composition_scaling_level_or_rate",
        "banner": BANNER,
        "tier": "EXPLORATORY",
        "registered_spec": (
            "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md#M4-F3-registration"
        ),
        "part0_registered_in": "reports/SUICA_M4_F3_COMPOSITION_SCALING_REPORT.md Part 0 (before run)",
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
            "Synthetic composition-scaling finding in a world calibrated to the opened "
            "PANDORA D-panel regime; licenses a D3 panel-DESIGN prior only. No claim "
            "about the real relation field's content, personality, emotion, diagnosis, "
            "or any individual."
        ),
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(adjudication, indent=2, default=str))


# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage", choices=["gates", "sweep", "predict", "holdout", "finalize", "all"], default="all"
    )
    parser.add_argument("--workers", type=int, default=max(2, min(6, (os.cpu_count() or 4) - 2)))
    parser.add_argument("--draws", type=int, default=DRAWS)
    parser.add_argument("--group", type=str, default="base1x,events,authors")
    parser.add_argument("--event-mults", type=str, default="2,4,8")
    parser.add_argument("--author-mults", type=str, default="2,4")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if not REF_PATH.exists():
        raise AssertionError(f"{REF_PATH} missing (M4-F1 artifact required, read-only).")
    if not F1_CELLS_CSV.exists():
        raise AssertionError(f"{F1_CELLS_CSV} missing (M4-F1 artifact required, read-only).")
    if not F1_CALIBRATION.exists():
        raise AssertionError(f"{F1_CALIBRATION} missing (M4-F1 artifact required, read-only).")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

    f1_cal = json.loads(F1_CALIBRATION.read_text(encoding="utf-8"))
    if f1_cal["status"] != "CALIBRATED":
        raise AssertionError("M4-F1 calibration_record.json is not CALIBRATED.")
    knobs = f1_cal["selected"]["knobs"]
    knob_tag = f1().knob_tag(knobs)

    groups = {g for g in args.group.split(",") if g}
    event_mults = {int(x) for x in args.event_mults.split(",") if x}
    author_mults = {int(x) for x in args.author_mults.split(",") if x}

    if args.stage in ("gates", "all"):
        run_gates(knobs, knob_tag, args.workers)
    if args.stage in ("sweep", "all"):
        run_sweep(knobs, knob_tag, args.workers, args.draws, groups, event_mults, author_mults)
    if args.stage in ("predict", "all"):
        if not (OUT / "prediction.json").exists():
            run_predict(args.workers)
        else:
            print("[skip] prediction.json exists")
    if args.stage in ("holdout", "all"):
        run_holdout(knobs, knob_tag, args.workers, args.draws)
    if args.stage in ("finalize", "all"):
        run_finalize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
