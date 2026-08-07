#!/usr/bin/env python3
"""M4-F8 -- the decisive occasion cell: live channel, adequate power (authors x16, kappa=0.5).

Registered spec: docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md section
"M4-F8 registration (2026-08-03, BEFORE run) -- the decisive cell: live
channel, adequate power", together with the preceding "M4-F7 planner
adjudication note -- the closure is NOT earned" (why M4-F7's own PIVOT FIRE
was suspended: at kappa=1.0, `blended_x = sqrt(1-kappa)*x + sqrt(kappa)*
shock_x` reduces algebraically to `blended_x = shock_x`, so the author-
specific AR(1) state -- the only quantity an occasion gap can decorrelate --
enters with coefficient EXACTLY 0; the knob was structurally inert, and the
significant decline M4-F7 measured is between-cell sampling variation, not
evidence about occasion spreading). Part 0 register-notes (every
implementation choice this registration left open, written BEFORE any
compute) are in reports/SUICA_M4_F8_OCCASION_AXIS_LIVE_REPORT.md Part 0.

THIS LEG CHANGES ONLY KAPPA relative to M4-F7: kappa=0.5 (not 1.0), where the
AR(1) state enters at sqrt(1-0.5)=.7071 amplitude -- causally live, unlike
M4-F7's kappa=1.0. Author scale (x16), block-count sweep (B in {1,2,4,8}),
the 40-step gap, the common-budget construction, both truth variants, and
the decorrelation check are ALL REUSED VERBATIM from M4-F6/M4-F7, by direct
call into F7's own module (loaded as f7(), exactly as F7 itself loaded f6()).
NEW: the G6 CHANNEL LIVENESS gate (the second new standing rule the M4-F7
planner note added), and G0's target/bar re-pointed at M4-F5's
`authors_x16_shared_k05` cell (.081307 +/- .010920; bar .0407 = half that
level, per this task's own registration).

Reuse boundary (task's explicit instruction: "Reuse its [M4-F7's] machinery
verbatim; kappa is the only design change."):
  - From scripts/run_suica_m4_f1_panel_sizing.py (loaded as f1()): knob_tag
    -- called unchanged in main() only (every other f1() call this leg needs
    happens INSIDE f7()'s own already-loaded functions, not called a second
    time here).
  - From scripts/run_suica_m4_f2_composition.py (loaded as f2()):
    run_gate_g1 (direct call); shock_vector (reused verbatim inside G6's own
    ablation helper below, exactly as f6().generate_world_spread itself
    calls it).
  - From scripts/run_suica_m4_f3_composition_scaling.py (loaded as f3()):
    run_gate_g3 -- called unchanged.
  - From scripts/run_suica_m4_f4_author_axis.py (loaded as f4()):
    build_live_tasks -- called unchanged, to build the byte-identical RAW
    authors-x16 task at kappa_tag="k05" (the G0/G2(b) gate anchor), exactly
    as M4-F7 did at kappa_tag="k10".
  - From scripts/run_suica_m4_f5_gauge_validity.py (loaded as f5()):
    run_truth_sweep_world (called DIRECTLY, unchanged, for the RAW
    authors-x16 gate-anchor cell); G4_TOLERANCE.
  - From scripts/run_suica_m4_f6_occasion_spread.py (loaded as f6()):
    GAP, M_COMMON, _paired_ci, spread_world_seed_for, g5_world_correlation,
    block_layout, block_occasion_labels, _draw_common_state, _draw_ar1_span,
    generate_world_spread (G6's own internal-consistency sanity check calls
    this directly) -- ALL called directly, unchanged.
  - **From scripts/run_suica_m4_f7_occasion_axis_powered.py (loaded as
    f7()): common_layout_scaled, run_spread_sweep_world** -- called
    DIRECTLY, UNCHANGED, for EVERY per-world computation this leg needs
    (construction-check cell at author_mult=1, and all four adjudicated
    sweep cells at author_mult=16). This is the leg's central reuse
    commitment and the reason this script needs NO new per-world engine at
    all (unlike M4-F7, which had to write a disclosed near-duplicate of
    M4-F6's own engine because M4-F6 hardcoded author_mult=1): F7's own
    `run_spread_sweep_world` already reads `task["kappa"]` and
    `task["author_mult"]` dynamically from the task dict rather than from any
    module-level constant, so it is ALREADY kappa- and scale-parametrized,
    and is reused byte-for-byte here at kappa=0.5.

NEW in this script (nothing above is reimplemented):
  - Task/cell-name builder functions parametrized for KAPPA_TAG="k05"
    (`cell_name_spread_x16`, `build_spread_tasks`, `build_construction_check_
    task`, `build_anchor_task`) -- disclosed thin near-duplicates of F7's own
    same-named functions, necessary ONLY because F7 hardcodes KAPPA_TAG="k10"
    /KAPPA=1.0 as MODULE-LEVEL constants inside those four builders (not as
    task-dict parameters) -- the per-world ENGINE they feed
    (`f7().run_spread_sweep_world`) needed no such duplicate, per the reuse
    boundary above.
  - The G0 POWER gate, re-targeted at M4-F5's `authors_x16_shared_k05` cell
    and the registration's own .0407 bar (half of .081307) -- otherwise
    IDENTICAL construction to F7's own G0 (same `f6()._paired_ci` call, same
    b8-b1 paired-by-world statistic).
  - **The G6 CHANNEL LIVENESS gate (wholly new, Part 0.3 of the report)**:
    (i) the AR(1) state's own blend coefficient at kappa=0.5, computed via
    the IDENTICAL expression `f6().generate_world_spread` uses internally;
    (ii) a disclosed structural near-duplicate of `f6().generate_world_
    spread`'s own draw sequence (`_g6_state_ablation_events`, reusing
    `f6()._draw_common_state`/`f6()._draw_ar1_span`/`f6().block_occasion_
    labels`/`f2().shock_vector` UNCHANGED) that assembles TWO events arrays
    per world -- INTACT (bit-identical to `f6().generate_world_spread`'s own
    output, verified as an internal-consistency sanity check) and
    STATE_ZEROED (identical except the AR(1) state's own contribution to the
    kappa-blend, `x_at_labels`, is dropped; `shock_x`/`mean_part`/noise are
    UNCHANGED and IDENTICAL across both variants) -- and reports the
    between-author variance ratio, aggregated across the SAME 8 worlds (same
    seed_key, hence bit-identical draws) that feed the b1_x16/b8_x16
    kappa=0.5 adjudicated sweep cells, plus a non-gating kappa=1.0 context
    row reusing F7's OWN seed_key (hence F7's own bit-identical world draws).
  - G2's target objects re-pointed at kappa=0.5 (M4-F6's persisted
    `b1_shared_k05` for G2(a), M4-F5's persisted `authors_x16_shared_k05` for
    G2(b) -- the SAME row G0 reads, read independently for a different
    purpose in each gate).
  - `cell_summary` / gates G1 (thin direct-call wrapper) / G2 / G3 (thin
    direct-call wrapper) / G4 / G5, OUT-scoped to THIS script's own artifact
    tree (each leg's cell_summary/gates has always been OUT-scoped even when
    the underlying rule is reused verbatim -- see F5's/F6's/F7's own
    cell_summary, each a disclosed near-duplicate of the previous one for
    exactly this reason).
  - The adjudication code (leans a/b/c with F7's own registered lean-(b)
    inapplicable-on-non-positive-gain rule, the pivot -- now gated on BOTH G0
    AND G6 -- and the two-gate-aware finalize branch that adjudicates
    nothing when either gate fails).

Stages (resumable, artifacts under results/m4_f8_occasion_axis_live/):
  --stage g6                  CHANNEL LIVENESS (analytic + empirical), run
                               FIRST and standalone-capable (fail-fast, per
                               Part 0's "before compute" framing); persists
                               g6_gate.json so later --stage gates reuses it
                               rather than recomputing
  --stage anchor               the RAW authors_x16_shared_k05 gate-anchor cell
                               (G0's target AND G2(b)'s comparison target;
                               f5().run_truth_sweep_world, unchanged, on
                               f4()'s own byte-identical mult=16/k05 task)
  --stage construction-check  the mult=1/block_count=1/kappa=0.5 GATE-ONLY
                               cell that must reproduce M4-F6's own persisted
                               b1_shared_k05 (G2(a)'s comparison target)
  --stage sweep                the 4 adjudicated b{1,2,4,8}_x16_k05 cells
                               (COMMON M_COMMON=8 budget, kappa=0.5 only;
                               --block-counts selects a subset for chunked
                               execution)
  --stage gates                G0-G6, writes gates.json; STOPS on G1/G2/G3/
                               G4/G5 failure or a G6 internal-consistency
                               failure (all mechanical/code defects); does
                               NOT stop on G0 or G6-channel-liveness failure
                               alone (Part 0.8, inherited from F7: both are
                               registered, anticipated, VALID scientific
                               outcomes this leg must still report in full)
  --stage finalize             G0-and-G6-gated adjudication + decision.json +
                               cells.csv
  --stage all                  g6 + anchor + construction-check + sweep +
                               gates + finalize
"""
from __future__ import annotations

import argparse
import gc
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

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import suica_core.v8_realtext_relation_field as v8  # noqa: E402,F401

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"
MASTER_SEED = 20260802  # exactly every prior leg's own MASTER_SEED.
DRAWS = 20
WORLDS_PER_CELL = 8
MIN_RETAINED_EVENTS = 8  # the deployed gauge's own split-half retention floor (unused directly here;
                          # inherited automatically via f7().run_spread_sweep_world's own constant).

AUTHOR_MULT = 16  # unchanged from M4-F7.
KAPPA_TAG = "k05"
KAPPA = 0.5  # kappa=0.5 ONLY -- the registration's decisive design change relative to M4-F7's kappa=1.0.
DESIGN = "shared"
BLOCK_COUNTS = [1, 2, 4, 8]

G0_HALF_WIDTH_BAR = 0.0407  # registered: half M4-F5's authors_x16_shared_k05 target (.081307/2=.0406535,
                            # rounded to .0407 exactly as the task's own registration text states).

OUT = ROOT / "results" / "m4_f8_occasion_axis_live"
F1_OUT = ROOT / "results" / "m4_f1_panel_sizing"
F5_OUT = ROOT / "results" / "m4_f5_gauge_validity"
F6_OUT = ROOT / "results" / "m4_f6_occasion_spread"
REF_PATH = F1_OUT / "realtext_panel_reference.json"
F1_CELLS_CSV = F1_OUT / "cells.csv"
F1_CALIBRATION = F1_OUT / "calibration_record.json"
F5_CELLS_CSV = F5_OUT / "cells.csv"
F6_CELLS_CSV = F6_OUT / "cells.csv"

CONSTRUCTION_CHECK_CELL = "construction_check_mult1_b1_k05"
ANCHOR_CELL = "authors_x16_shared_k05"


def _load_script(name: str) -> Any:
    """Copied verbatim from every prior leg's own Part-0.11-style fix
    (register sys.modules[mod_name]=module BEFORE exec_module, so a nested
    ProcessPoolExecutor.map against a function defined in a dynamically-
    loaded module can pickle that function by reference). Zero edits to any
    of the six scripts this leg loads."""
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
_F4 = None
_F5 = None
_F6 = None
_F7 = None


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


def f4() -> Any:
    global _F4
    if _F4 is None:
        _F4 = _load_script("run_suica_m4_f4_author_axis.py")
    return _F4


def f5() -> Any:
    global _F5
    if _F5 is None:
        _F5 = _load_script("run_suica_m4_f5_gauge_validity.py")
    return _F5


def f6() -> Any:
    global _F6
    if _F6 is None:
        _F6 = _load_script("run_suica_m4_f6_occasion_spread.py")
    return _F6


def f7() -> Any:
    global _F7
    if _F7 is None:
        _F7 = _load_script("run_suica_m4_f7_occasion_axis_powered.py")
    return _F7


# ---------------------------------------------------------------------------
# Task/cell-name builders, parametrized for KAPPA_TAG="k05". Disclosed thin
# near-duplicates of F7's own same-named functions -- necessary ONLY because
# F7 hardcodes KAPPA_TAG/KAPPA as module constants inside these four
# builders. The per-world ENGINE they feed (f7().run_spread_sweep_world,
# f7().common_layout_scaled) is reused UNCHANGED (see module docstring).

def cell_name_spread_x16(block_count: int) -> str:
    return f"b{block_count}_x16_shared_{KAPPA_TAG}"


def build_spread_tasks(
    knobs: dict[str, Any], knob_tag: str, draws: int, block_counts: list[int]
) -> list[dict[str, Any]]:
    tasks = []
    gap = f6().GAP
    for block_count in block_counts:
        seed_key = f"b{block_count}_x16_{KAPPA_TAG}"
        cell = cell_name_spread_x16(block_count)
        for world in range(WORLDS_PER_CELL):
            tasks.append(
                {
                    "cell": cell, "seed_key": seed_key, "world": world,
                    "author_mult": AUTHOR_MULT, "block_count": block_count, "gap": gap, "kappa": KAPPA,
                    "knobs": knobs, "knob_tag": knob_tag, "draws": draws,
                    "ref_path": str(REF_PATH), "budget_label": "f8.0", "corpus_prefix": "m4f8-",
                }
            )
    return tasks


def build_construction_check_task(knobs: dict[str, Any], knob_tag: str, draws: int) -> list[dict[str, Any]]:
    """G2(a)'s task: mult=1/block_count=1/kappa=0.5, using F6's OWN
    seed_key/corpus-prefix/budget_label ('b1_k05' / 'm4f6-' / 'f6.0' --
    EXACTLY f6().build_spread_tasks's own values at block_count=1,
    kappa_tag='k05') so this reproduces F6's persisted b1_shared_k05 cell
    bit-for-bit through f7()'s generalized (author_mult-parametrized)
    orchestration -- a code-correctness check, not a scientific/adjudicated
    cell. Directly mirrors F7's own construction-check task at kappa_tag='k10'."""
    seed_key = f"b1_{KAPPA_TAG}"
    return [
        {
            "cell": CONSTRUCTION_CHECK_CELL, "seed_key": seed_key, "world": world,
            "author_mult": 1, "block_count": 1, "gap": f6().GAP, "kappa": KAPPA,
            "knobs": knobs, "knob_tag": knob_tag, "draws": draws,
            "ref_path": str(REF_PATH), "budget_label": "f6.0", "corpus_prefix": "m4f6-",
        }
        for world in range(WORLDS_PER_CELL)
    ]


def build_anchor_task(knobs: dict[str, Any], knob_tag: str, draws: int) -> list[dict[str, Any]]:
    """The RAW authors_x16_shared_k05 gate-anchor task -- BYTE-IDENTICAL to
    M4-F4's/M4-F5's own build_live_tasks(mult=16, kappa_tags={'k05'})."""
    return f4().build_live_tasks(knobs, knob_tag, draws, [AUTHOR_MULT], {KAPPA_TAG})


# ---------------------------------------------------------------------------

def _write_cell(cell: str, rows: list[dict[str, Any]], started: float, *, has_g5: bool) -> None:
    for row in sorted(rows, key=lambda r: r["world"]):
        g5_str = f"g5corr {row['g5_correlation']:+.5f}" if has_g5 and row.get("g5_correlation") is not None else "g5 n/a"
        print(
            f"[{cell} w{row['world']}] A {row['agreement_mean']:+.4f} "
            f"truthA {row['truth_recovery_exact']:+.4f} truthB {row['truth_recovery_long']:+.4f} "
            f"g4 {row['g4_max_diff']:.2e} {g5_str} n_ret {row['n_retained']} {row['seconds']:.0f}s", flush=True,
        )
    draw_rows = [
        {"cell": cell, "world": row["world"], "draw": d, "agreement": v}
        for row in rows
        for d, v in enumerate(row["draw_values"])
    ]
    pd.DataFrame(rows).drop(columns=["draw_values"]).to_csv(OUT / f"cell_{cell}.csv", index=False)
    pd.DataFrame(draw_rows).to_csv(OUT / f"draws_{cell}.csv", index=False)
    print(f"[{cell}] done in {time.time() - started:.0f}s -> cell_{cell}.csv")


def run_anchor(knobs: dict[str, Any], knob_tag: str, workers: int, draws: int) -> None:
    """The RAW authors_x16 gate-anchor cell: DIRECT, unchanged call to
    f5().run_truth_sweep_world on f4()'s own byte-identical mult=16/k05 task
    -- literally M4-F5's own computation, repeated (M4-F5 already persisted
    this exact cell; this recomputes it fresh under THIS leg's own artifact
    tree so G0/G2(b) have a freshly-computed object to diff, mirroring M4-F7's
    own anchor-stage discipline exactly)."""
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = build_anchor_task(knobs, knob_tag, draws)
    cell = tasks[0]["cell"]
    path = OUT / f"cell_{cell}.csv"
    if path.exists():
        print(f"[skip] {cell} exists")
        return
    started = time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(f5().run_truth_sweep_world, tasks))
    _write_cell(cell, rows, started, has_g5=False)


def run_construction_check(knobs: dict[str, Any], knob_tag: str, workers: int, draws: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = build_construction_check_task(knobs, knob_tag, draws)
    cell = CONSTRUCTION_CHECK_CELL
    path = OUT / f"cell_{cell}.csv"
    if path.exists():
        print(f"[skip] {cell} exists")
        return
    started = time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(f7().run_spread_sweep_world, tasks))
    _write_cell(cell, rows, started, has_g5=True)


def run_sweep(knobs: dict[str, Any], knob_tag: str, workers: int, draws: int, block_counts: list[int]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = build_spread_tasks(knobs, knob_tag, draws, block_counts)
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
            rows = list(pool.map(f7().run_spread_sweep_world, cell_tasks))
        _write_cell(cell, rows, started, has_g5=True)


def cell_summary(cell: str) -> dict[str, Any]:
    frame = pd.read_csv(OUT / f"cell_{cell}.csv")
    values = frame["agreement_mean"].to_numpy(dtype=float)
    mean = float(values.mean())
    se = float(values.std(ddof=1) / math.sqrt(len(values)))
    truth_exact = frame["truth_recovery_exact"].to_numpy(dtype=float)
    truth_long = frame["truth_recovery_long"].to_numpy(dtype=float)
    has_g5 = "g5_correlation" in frame.columns and frame["g5_correlation"].notna().all()
    out = {
        "cell": cell,
        "kappa": float(frame["kappa"].iloc[0]),
        "block_count": int(frame["block_count"].iloc[0]) if "block_count" in frame.columns else 1,
        "worlds": int(len(frame)),
        "agreement_mean": mean,
        "agreement_se": se,
        "d0_eff_rank_M_mean": float(frame["d0_eff_rank_M"].mean()),
        "d0_eff_rank_K_mean": float(frame["d0_eff_rank_K"].mean()),
        "n_retained": int(frame["n_retained"].iloc[0]),
        "n_retained_constant": bool((frame["n_retained"] == frame["n_retained"].iloc[0]).all()),
        "n_events_total": int(frame["n_events_total"].iloc[0]),
        "truth_recovery_exact_mean": float(truth_exact.mean()),
        "truth_recovery_exact_se": float(truth_exact.std(ddof=1) / math.sqrt(len(truth_exact))),
        "truth_recovery_long_mean": float(truth_long.mean()),
        "truth_recovery_long_se": float(truth_long.std(ddof=1) / math.sqrt(len(truth_long))),
        "g4_max_diff_over_worlds": float(frame["g4_max_diff"].max()),
        "world_seeds": frame["world_seed"].astype(int).tolist(),
        "world_values": values.tolist(),
        "truth_exact_world_values": truth_exact.tolist(),
        "truth_long_world_values": truth_long.tolist(),
    }
    if has_g5:
        g5vals = frame["g5_correlation"].to_numpy(dtype=float)
        g5_se = float(g5vals.std(ddof=1) / math.sqrt(len(g5vals)))
        out["g5_correlation_mean"] = float(g5vals.mean())
        out["g5_correlation_se"] = g5_se
        out["g5_t_stat"] = float(g5vals.mean() / g5_se) if g5_se > 0 else float("inf")
        out["g5_n_pairs_per_world"] = int(frame["g5_n_pairs"].iloc[0])
        out["g5_world_values"] = g5vals.tolist()
    else:
        out["g5_correlation_mean"] = None
        out["g5_correlation_se"] = None
        out["g5_t_stat"] = None
        out["g5_n_pairs_per_world"] = 0
        out["g5_world_values"] = []
    return out


# ---------------------------------------------------------------------------
# Gates G1/G3 (direct calls), G2 (new k05 targets), G4/G5 (OUT-scoped
# near-duplicates), G0 (new k05 target/bar).

def run_gate_g1(knobs: dict[str, Any], knob_tag: str, workers: int) -> dict[str, Any]:
    """Direct call, unchanged: kappa<=0 free cell reproduces M4-F1's persisted base1x."""
    return f2().run_gate_g1(knobs, knob_tag, workers)


def run_gate_g3() -> dict[str, Any]:
    """Direct call, unchanged: gauge invariance."""
    return f3().run_gate_g3()


def _read_f6_persisted_row(cell: str) -> dict[str, float]:
    frame = pd.read_csv(F6_CELLS_CSV)
    row = frame.loc[frame["cell"] == cell].iloc[0]
    return {
        "agreement_mean": float(row["agreement_mean"]),
        "agreement_se": float(row["agreement_se"]),
        "truth_recovery_exact_mean": float(row["truth_recovery_exact_mean"]),
        "truth_recovery_long_mean": float(row["truth_recovery_long_mean"]),
        "d0_eff_rank_M_mean": float(row["d0_eff_rank_M_mean"]),
        "d0_eff_rank_K_mean": float(row["d0_eff_rank_K_mean"]),
        "n_retained": int(row["n_retained"]),
    }


def _read_f5_persisted_row(cell: str) -> dict[str, float]:
    frame = pd.read_csv(F5_CELLS_CSV)
    row = frame.loc[frame["cell"] == cell].iloc[0]
    return {
        "agreement_mean": float(row["agreement_mean"]),
        "agreement_se": float(row["agreement_se"]),
        "truth_recovery_exact_mean": float(row["truth_recovery_exact_mean"]),
        "truth_recovery_long_mean": float(row["truth_recovery_long_mean"]),
        "d0_eff_rank_M_mean": float(row["d0_eff_rank_M_mean"]),
        "d0_eff_rank_K_mean": float(row["d0_eff_rank_K_mean"]),
        "n_retained": int(row["n_retained"]),
    }


def _diff_row(got: dict[str, Any], target: dict[str, float]) -> tuple[dict[str, float], bool]:
    diffs = {k: abs(float(got[k]) - float(target[k])) for k in target if k != "n_retained"}
    diffs["n_retained"] = abs(int(got["n_retained"]) - int(target["n_retained"]))
    row_pass = bool(all(v <= 1e-12 for k, v in diffs.items() if k != "n_retained") and diffs["n_retained"] == 0)
    return diffs, row_pass


def run_gate_g2() -> dict[str, Any]:
    """TWO disclosed sub-checks, BOTH required, mirroring F7's own G2
    structure exactly but re-targeted at kappa=0.5 (Part 0.2 of the report
    states the registration's own "state which object each check uses"
    instruction, and the disclosed ambiguity resolution for "the B=1 sweep
    cell must reproduce M4-F7's construction where comparable" -- F7 itself
    has no kappa=0.5 numbers to compare against, so "where comparable" is
    read as: reproduce F7's own CONSTRUCTION METHOD (its generalized,
    author_mult-parametrized orchestration, reused here via f7()'s own
    functions) applied at kappa=0.5, checked against the one persisted
    object that IS comparable at this kappa -- M4-F6's own `b1_shared_k05`):
    (a) CONSTRUCTION -- the `construction_check_mult1_b1_k05` cell (mult=1,
    block_count=1, kappa=0.5, computed via f7()'s own generalized
    orchestration using F6's own seed_key/corpus-prefix/budget_label)
    reproduces M4-F6's persisted `b1_shared_k05` to <=1e-12. (b) ANCHOR --
    the RAW `authors_x16_shared_k05` cell (a direct, unchanged call to
    f5().run_truth_sweep_world on f4()'s own byte-identical mult=16/k05
    task) reproduces M4-F5's persisted `authors_x16_shared_k05` (agreement +
    BOTH truth variants) to <=1e-12 -- the registration's own explicitly
    stated check."""
    construction_path = OUT / f"cell_{CONSTRUCTION_CHECK_CELL}.csv"
    if not construction_path.exists():
        raise AssertionError(f"G2(a) requires {construction_path} to exist; run --stage construction-check first.")
    got_construction = cell_summary(CONSTRUCTION_CHECK_CELL)
    target_construction = _read_f6_persisted_row("b1_shared_k05")
    diffs_a, pass_a = _diff_row(got_construction, target_construction)

    anchor_path = OUT / f"cell_{ANCHOR_CELL}.csv"
    if not anchor_path.exists():
        raise AssertionError(f"G2(b) requires {anchor_path} to exist; run --stage anchor first.")
    got_anchor = cell_summary(ANCHOR_CELL)
    target_anchor = _read_f5_persisted_row(ANCHOR_CELL)
    diffs_b, pass_b = _diff_row(got_anchor, target_anchor)

    return {
        "gate": "G2",
        "description": "TWO sub-checks, both required: (a) CONSTRUCTION -- the mult=1/block_count=1/"
        "kappa=0.5 cell, computed through f7()'s generalized orchestration using F6's own seed_key/"
        "corpus-prefix/budget_label, reproduces M4-F6's persisted b1_shared_k05 to <=1e-12 (the registered "
        "'B=1 sweep cell must reproduce M4-F7's construction where comparable' check -- ambiguity resolution "
        "disclosed in Part 0.2 of the report: F7 itself has no kappa=0.5 numbers, so 'comparable' is read as "
        "F7's own construction method applied at this kappa, checked against F6's persisted kappa=0.5 cell); "
        "(b) ANCHOR -- the RAW authors_x16_shared_k05 cell (f5().run_truth_sweep_world, unchanged, on f4()'s "
        "own byte-identical mult=16/k05 task) reproduces M4-F5's persisted authors_x16_shared_k05 to <=1e-12 "
        "(the registration's own explicitly stated check).",
        "tolerance": 1e-12,
        "construction_check": {
            "target": target_construction, "observed": {k: got_construction[k] for k in target_construction},
            "abs_diffs": diffs_a, "pass": pass_a,
        },
        "anchor_check": {
            "target": target_anchor, "observed": {k: got_anchor[k] for k in target_anchor},
            "abs_diffs": diffs_b, "pass": pass_b,
        },
        "pass": bool(pass_a and pass_b),
    }


def run_gate_g4(all_cells: list[str]) -> dict[str, Any]:
    """Truth-path invariance, as M4-F5/M4-F6/M4-F7: two independent routes to
    the identical finite-sample field agree to <=G4_TOLERANCE, for every
    world of every cell (construction-check + anchor + 4 adjudicated x16 cells)."""
    rows = []
    all_pass = True
    for cell in all_cells:
        frame = pd.read_csv(OUT / f"cell_{cell}.csv")
        cell_max = float(frame["g4_max_diff"].max())
        cell_pass = bool(cell_max <= f5().G4_TOLERANCE)
        all_pass = all_pass and cell_pass
        rows.append({"cell": cell, "max_diff": cell_max, "pass": cell_pass})
    return {
        "gate": "G4",
        "description": "truth-path invariance: two independent routes to the identical finite-sample "
        "field agree to <=G4_TOLERANCE, for every world of every cell (matching M4-F5's/M4-F6's/M4-F7's "
        "own check)",
        "tolerance": f5().G4_TOLERANCE,
        "rows": rows,
        "pass": bool(all_pass),
    }


def run_gate_g5(spread_cells: list[str]) -> dict[str, Any]:
    """Decorrelation check: F6's OWN pre-registered aggregation rule (Part
    0.7 of the M4-F6 report), reused VERBATIM: |t|<2.0 at EVERY
    block_count>=2 cell. 3 cells here (b2/b4/b8 at x16, kappa=0.5 only)."""
    rows = []
    all_pass = True
    for cell in spread_cells:
        summary = cell_summary(cell)
        if summary["block_count"] <= 1:
            rows.append({"cell": cell, "block_count": summary["block_count"], "applicable": False})
            continue
        t = summary["g5_t_stat"]
        cell_pass = bool(t is not None and abs(t) < 2.0)
        all_pass = all_pass and cell_pass
        rows.append(
            {
                "cell": cell, "block_count": summary["block_count"], "kappa": summary["kappa"],
                "applicable": True,
                "correlation_mean": summary["g5_correlation_mean"],
                "correlation_se": summary["g5_correlation_se"],
                "t_stat": t,
                "n_pairs_per_world": summary["g5_n_pairs_per_world"],
                "pass": cell_pass,
            }
        )
    pooled_vals = [r["correlation_mean"] for r in rows if r.get("applicable")]
    pooled = {
        "grand_mean_across_cells": float(np.mean(pooled_vals)) if pooled_vals else None,
        "note": "supplementary context only, NOT the gating statistic (F6's own Part 0.7 rule, reused "
        "verbatim, is per-cell |t|<2.0 at EVERY tested cell)",
    }
    return {
        "gate": "G5",
        "description": "decorrelation check: F6's own pre-registered per-cell |t|<2.0 rule (Part 0.7 of "
        "the M4-F6 report), reused VERBATIM, applied to the 3 block_count>=2 cells at authors x16, "
        "kappa=0.5 only.",
        "rows": rows,
        "pooled_context": pooled,
        "pass": bool(all_pass),
    }


def run_gate_g0(target_cell: str = ANCHOR_CELL) -> dict[str, Any]:
    """POWER (M4-F6/M4-F7 planner-note standing rule): report the target's
    measured level at this scale from M4-F5's OWN persisted
    authors_x16_shared_k05 cell (read verbatim, never retyped), and the
    minimum detectable paired difference THIS design's REALIZED SEs actually
    afford (the b8_x16-b1_x16 paired-by-world CI half-width on
    truth_recovery_long, kappa=0.5, using F6's own _paired_ci construction
    verbatim). FAILS (declared UNDERPOWERED) if that half-width exceeds
    G0_HALF_WIDTH_BAR=.0407. Like F7's own G0, this does NOT raise/void the
    run here -- it is a registered, anticipated, valid scientific outcome
    that run_finalize must still report in full, not a mechanical defect."""
    f5_frame = pd.read_csv(F5_CELLS_CSV)
    f5_row = f5_frame.loc[f5_frame["cell"] == target_cell].iloc[0]
    target_level_mean = float(f5_row["truth_recovery_long_mean"])
    target_level_se = float(f5_row["truth_recovery_long_se"])

    b1 = cell_summary(cell_name_spread_x16(1))
    b8 = cell_summary(cell_name_spread_x16(8))
    diff_long = np.asarray(b8["truth_long_world_values"], dtype=float) - np.asarray(b1["truth_long_world_values"], dtype=float)
    ci_long = f6()._paired_ci(diff_long)
    half_width = float((ci_long["ci95_high"] - ci_long["ci95_low"]) / 2.0)
    adequately_powered = bool(half_width <= G0_HALF_WIDTH_BAR)

    return {
        "gate": "G0",
        "description": "POWER (M4-F6/M4-F7 planner-note standing rule): report the target's measured level "
        "at this scale from M4-F5's own persisted authors_x16_shared_k05 cell, and the minimum detectable "
        "paired difference (B8-B1 truth_recovery_long paired-by-world 95% CI half-width) this design's "
        "REALIZED SEs actually afford. FAILS (UNDERPOWERED) if that half-width exceeds .0407 (half the "
        "target's measured level, per the registration).",
        "target_source": f"results/m4_f5_gauge_validity/cells.csv row '{target_cell}' (read verbatim, not retyped)",
        "target_level_mean": target_level_mean,
        "target_level_se": target_level_se,
        "half_width_bar": G0_HALF_WIDTH_BAR,
        "paired_diff_b8_minus_b1_truth_long": ci_long,
        "minimum_detectable_paired_difference_half_width": half_width,
        "adequately_powered": adequately_powered,
        "pass": adequately_powered,
    }


# ---------------------------------------------------------------------------
# G6 -- CHANNEL LIVENESS (wholly new, the second M4-F7-planner-note standing rule).

def g6_analytic_coefficient(kappa: float) -> float:
    """The AR(1) state's own blend coefficient, computed via the IDENTICAL
    expression f6().generate_world_spread uses internally
    ('math.sqrt(max(0.0, 1.0 - kappa_f))') -- copied, not retyped-and-hoped,
    and cross-checked empirically below by the internal-consistency sanity
    check (the 'intact' ablation variant must reproduce
    f6().generate_world_spread's own real output bit-for-bit)."""
    kappa_f = float(kappa)
    return math.sqrt(max(0.0, 1.0 - kappa_f))


def _g6_state_ablation_events(
    counts: list[int],
    contexts: list[str],
    knobs: dict[str, Any],
    kappa: float,
    block_count: int,
    gap: int,
    world_seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Disclosed structural near-duplicate of f6().generate_world_spread's
    own draw sequence -- IDENTICAL prefix (f6()._draw_common_state,
    f6()._draw_ar1_span, the noise draw, mean_part, f6().block_occasion_
    labels, the f2().shock_vector cache loop, all in the SAME order with the
    SAME world_seed) so the INTACT reconstruction below is bit-identical to
    what f6().generate_world_spread itself would produce (verified as a
    sanity check by run_gate_g6, not merely asserted). Returns TWO assembled-
    events arrays, shape (n, m_common, 64): INTACT (mean_part + state_part
    computed from the REAL blend, identical to the deployed generator) and
    STATE_ZEROED (identical except x_at_labels's own contribution to the
    kappa-blend is dropped -- shock_x, mean_part, and the noise draw are
    UNCHANGED and IDENTICAL across both variants, isolating exactly what the
    AR(1) state ITSELF, not shock_x and not mean_part, contributes). G6's own
    diagnostic only; never feeds any adjudicated cell."""
    n = len(counts)
    m_common = counts[0]
    if any(c != m_common for c in counts):
        raise ValueError("_g6_state_ablation_events requires uniform per-author counts (Part 0.4, reused)")
    s, _ = f6().block_layout(m_common, block_count)
    t_span = block_count * s + (block_count - 1) * gap
    rng = np.random.default_rng(world_seed)
    k = int(knobs["k"])
    w_mu, w_x, w_e = float(knobs["w_mu"]), float(knobs["w_x"]), float(knobs["w_e"])
    g = np.linspace(0.85, 0.55, k)
    a = math.sqrt(2.0 / float(np.sum(g**2)))
    sigma_iso = math.sqrt(2.0 / 64.0)
    loadings, z, phi = f6()._draw_common_state(n, knobs, rng)
    x = f6()._draw_ar1_span(n, k, phi, t_span, rng)
    noise = rng.normal(size=(n, m_common, 64))
    mean_part = math.sqrt(w_mu) * a * ((z * g) @ loadings.T)

    labels = f6().block_occasion_labels(m_common, block_count, gap)
    shock_x = np.zeros((n, m_common, k), dtype=float)
    cache: dict[tuple[str, int], np.ndarray] = {}
    kappa_f = float(kappa)
    for i in range(n):
        context = contexts[i]
        for j in range(m_common):
            occ = int(labels[j])
            key = (context, occ)
            vector = cache.get(key)
            if vector is None:
                vector = f2().shock_vector(world_seed, context, occ, k)
                cache[key] = vector
            shock_x[i, j] = vector

    x_at_labels = x[:, labels, :]
    blended_intact = math.sqrt(max(0.0, 1.0 - kappa_f)) * x_at_labels + math.sqrt(kappa_f) * shock_x
    blended_zeroed = math.sqrt(kappa_f) * shock_x  # the AR(1) state's own contribution dropped.
    state_part_intact = math.sqrt(w_x) * a * ((blended_intact * g) @ loadings.T)
    state_part_zeroed = math.sqrt(w_x) * a * ((blended_zeroed * g) @ loadings.T)
    noise_term = math.sqrt(w_e) * sigma_iso * noise
    events_intact = mean_part[:, None, :] + state_part_intact + noise_term
    events_zeroed = mean_part[:, None, :] + state_part_zeroed + noise_term
    return events_intact, events_zeroed


def _between_author_variance(events: np.ndarray) -> float:
    """Sum, across the 64 raw event dimensions, of the variance ACROSS
    AUTHORS of each author's own mean event vector (averaged over that
    author's m_common observed occasions) -- the trace of the between-author
    covariance matrix of the assembled events, Part 0.3's registered
    operationalization of 'between-author variance of the assembled events.'
    Computed over ALL authors in the author_mult layout (not the retained/
    resolved D1/D2 subset downstream of D0 calibration), since this is a
    property of the GENERATOR's own output, not the deployed pipeline --
    disclosed choice, Part 0.3."""
    author_mean = events.mean(axis=1)  # (n, 64)
    return float(np.var(author_mean, axis=0, ddof=1).sum())


def _g6_world_task(task: dict[str, Any]) -> dict[str, Any]:
    """Parallel-pool unit for G6: one world, one (kappa, block_count) cell.
    Rebuilds the author_mult=16 common layout via f7().common_layout_scaled
    (reused unchanged) and calls _g6_state_ablation_events with the SAME
    world_seed convention (f6().spread_world_seed_for) the real sweep cells
    use for the identical seed_key -- so this diagnostic runs on the SAME
    random draws that feed the adjudicated cells (kappa=0.5 rows), or on
    F7's OWN already-computed world draws (the kappa=1.0 context row, via
    F7's own seed_key string), never a separately-seeded proxy."""
    reference = json.loads(Path(task["ref_path"]).read_text(encoding="utf-8"))
    _author_ids, contexts, _splits, counts, _raw = f7().common_layout_scaled(reference, task["author_mult"])
    world_seed = f6().spread_world_seed_for(task["seed_key"], task["world"], task["knob_tag"])
    events_intact, events_zeroed = _g6_state_ablation_events(
        counts, contexts, task["knobs"], task["kappa"], task["block_count"], task["gap"], world_seed
    )
    v_intact = _between_author_variance(events_intact)
    v_zeroed = _between_author_variance(events_zeroed)
    ratio = float(v_intact / v_zeroed) if v_zeroed > 0 else float("inf")
    log_ratio = float(math.log(ratio)) if 0 < ratio < float("inf") else float("nan")
    return {
        "seed_key": task["seed_key"], "world": int(task["world"]), "kappa": float(task["kappa"]),
        "block_count": int(task["block_count"]), "world_seed": int(world_seed),
        "between_author_variance_intact": v_intact,
        "between_author_variance_state_zeroed": v_zeroed,
        "ratio": ratio, "log_ratio": log_ratio,
    }


def _g6_sanity_check(
    counts: list[int], contexts: list[str], knobs: dict[str, Any], kappa: float,
    block_count: int, gap: int, world_seed: int,
) -> float:
    """Internal-consistency check (not itself a registered gate; gates the
    pipeline via run_gates' own raise, exactly like G1-G5, since a failure
    here means a code defect in the ablation helper, not a scientific
    finding): the INTACT variant from _g6_state_ablation_events must
    reproduce f6().generate_world_spread's own real output bit-for-bit for
    identical inputs."""
    events_intact, _events_zeroed = _g6_state_ablation_events(counts, contexts, knobs, kappa, block_count, gap, world_seed)
    real_vectors_list, _diag = f6().generate_world_spread(counts, contexts, knobs, kappa, block_count, gap, world_seed)
    real_events = np.stack(real_vectors_list, axis=0)
    return float(np.max(np.abs(events_intact - real_events)))


def run_gate_g6(knobs: dict[str, Any], knob_tag: str, workers: int) -> dict[str, Any]:
    """CHANNEL LIVENESS (new standing-rule gate, M4-F7 planner note). (i)
    ANALYTIC: the AR(1) state's own blend coefficient at kappa=0.5 (non-zero
    iff sqrt(1-kappa)!=0). (ii) EMPIRICAL: the between-author-variance ratio
    (state intact vs. state-zeroed, Part 0.3's operationalization) at BOTH
    block_count in {1,8} (the two endpoints the pivot itself compares),
    kappa=0.5, aggregated across the SAME 8 worlds that feed the adjudicated
    b1_x16/b8_x16 sweep cells (same seed_key -> bit-identical draws). G6
    PASSES (channel LIVE) iff, at BOTH block counts, the log-ratio's
    paired-style 95% CI (f6()._paired_ci reused verbatim, df=7) excludes 0
    on the positive side -- Part 0.3's disclosed operationalization,
    mirroring this line's own established 'indistinguishable from zero'
    idiom in the opposite direction (exactly as F7's own Part 0.7 did for G5
    relative to F1's threshold), with NO separate magnitude bar (disclosed
    ambiguity resolution: the registration gives no numeric materiality bar
    beyond 'indistinguishable from zero', so a pure significance test on the
    log-ratio -- not an added arbitrary magnitude cutoff -- is adopted,
    fixed here BEFORE the numbers were computed). A non-gating kappa=1.0/
    block_count=1 context row reuses F7's OWN seed_key ('b1_x16_k10'), hence
    F7's own bit-identical world draws, as a validation check: M4-F6's/
    M4-F7's own algebra established the channel is EXACTLY inert at
    kappa=1.0 (blended_x=shock_x, zero coefficient on x_at_labels), so this
    row is expected to read close to a ratio of 1.0 (log-ratio CI including
    0) -- confirming the metric itself is sensitive/specific, not merely
    that the number is positive whenever computed."""
    persisted_path = OUT / "g6_gate.json"
    if persisted_path.exists():
        print("[skip] G6 already computed -> g6_gate.json")
        return json.loads(persisted_path.read_text(encoding="utf-8"))

    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    gap = f6().GAP

    gating_specs = [(KAPPA, 1, f"b1_x16_{KAPPA_TAG}"), (KAPPA, 8, f"b8_x16_{KAPPA_TAG}")]
    context_specs = [(1.0, 1, "b1_x16_k10")]  # F7's own seed_key -> F7's own bit-identical world draws.

    tasks = []
    for kappa_v, block_count, seed_key in gating_specs + context_specs:
        for world in range(WORLDS_PER_CELL):
            tasks.append({
                "seed_key": seed_key, "world": world, "author_mult": AUTHOR_MULT,
                "block_count": block_count, "gap": gap, "kappa": kappa_v,
                "knobs": knobs, "knob_tag": knob_tag, "ref_path": str(REF_PATH),
            })

    started = time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(_g6_world_task, tasks))
    elapsed = time.time() - started
    frame = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUT / "g6_worlds.csv", index=False)

    def _agg(kappa_v: float, block_count: int) -> dict[str, Any]:
        sub = frame[(frame["kappa"] == kappa_v) & (frame["block_count"] == block_count)]
        log_ratio = sub["log_ratio"].to_numpy(dtype=float)
        ci = f6()._paired_ci(log_ratio)
        ratio_values = sub["ratio"].to_numpy(dtype=float)
        return {
            "kappa": float(kappa_v), "block_count": int(block_count),
            "between_author_variance_intact_mean": float(sub["between_author_variance_intact"].mean()),
            "between_author_variance_state_zeroed_mean": float(sub["between_author_variance_state_zeroed"].mean()),
            "ratio_values": ratio_values.tolist(),
            "ratio_mean": float(ratio_values.mean()),
            "ratio_geomean_exp_log_ratio_mean": float(math.exp(ci["mean"])),
            "log_ratio_ci": ci,
            "live": bool(ci["ci_excludes_zero_positive"]),
        }

    gating_rows = [_agg(*spec[:2]) for spec in gating_specs]
    context_rows = [_agg(*spec[:2]) for spec in context_specs]
    channel_live = bool(all(r["live"] for r in gating_rows))

    coeff = g6_analytic_coefficient(KAPPA)

    world0_seed = f6().spread_world_seed_for(f"b1_x16_{KAPPA_TAG}", 0, knob_tag)
    _author_ids, contexts0, _splits, counts0, _raw = f7().common_layout_scaled(reference, AUTHOR_MULT)
    max_diff = _g6_sanity_check(counts0, contexts0, knobs, KAPPA, 1, gap, world0_seed)
    internal_consistency_pass = bool(max_diff <= f5().G4_TOLERANCE)

    result = {
        "gate": "G6",
        "description": "CHANNEL LIVENESS: (i) analytic -- AR(1) state blend coefficient sqrt(1-kappa) at "
        "kappa=0.5, computed via the generator's own expression; (ii) empirical -- between-author variance "
        "ratio (state intact / state-zeroed) at block_count in {1,8}, kappa=0.5, aggregated across the same "
        "8 worlds feeding the adjudicated b1_x16/b8_x16 cells, via a one-sample paired-style CI (f6()._paired_ci) "
        "on the log-ratio; PASSES iff the CI excludes 0 on the positive side at BOTH block counts. A "
        "kappa=1.0/block_count=1 context row (F7's own seed_key, F7's own world draws) is non-gating "
        "validation only.",
        "analytic_coefficient_at_kappa": {
            "kappa": KAPPA, "sqrt_1_minus_kappa": coeff, "nonzero": bool(coeff != 0.0),
        },
        "internal_consistency_check": {
            "note": "the ablation helper's own INTACT reconstruction vs. f6().generate_world_spread's real "
            "output, same inputs (kappa=0.5, block_count=1, world 0) -- a code-correctness safeguard, not a "
            "scientific finding; failure here is treated as a mechanical defect (raises in run_gates), not "
            "as evidence about channel liveness.",
            "max_abs_diff_intact_vs_generator": max_diff, "tolerance": f5().G4_TOLERANCE,
            "pass": internal_consistency_pass,
        },
        "gating_rows": gating_rows,
        "context_rows": context_rows,
        "channel_live": channel_live,
        "seconds": elapsed,
        "pass": bool(coeff != 0.0 and channel_live),
    }
    persisted_path.write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({
        "G6_analytic_nonzero": result["analytic_coefficient_at_kappa"]["nonzero"],
        "G6_internal_consistency_pass": internal_consistency_pass,
        "G6_channel_live": channel_live,
        "G6_pass": result["pass"],
    }, indent=2))
    return result


def run_gates(knobs: dict[str, Any], knob_tag: str, workers: int) -> dict[str, Any]:
    spread_cells = [cell_name_spread_x16(b) for b in BLOCK_COUNTS]
    g1 = run_gate_g1(knobs, knob_tag, workers)
    g3 = run_gate_g3()
    g2 = run_gate_g2()
    all_computed_cells = [CONSTRUCTION_CHECK_CELL, ANCHOR_CELL] + spread_cells
    g4 = run_gate_g4(all_computed_cells)
    g5 = run_gate_g5(spread_cells)
    g0 = run_gate_g0()
    g6 = run_gate_g6(knobs, knob_tag, workers)
    mechanical_pass = bool(g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"] and g5["pass"])
    gates = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "knobs": knobs,
        "knob_tag": knob_tag,
        "gap": f6().GAP,
        "m_common": f6().M_COMMON,
        "author_mult": AUTHOR_MULT,
        "kappa": KAPPA,
        "G0": g0, "G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5, "G6": g6,
        "mechanical_gates_pass": mechanical_pass,
        "all_pass": bool(mechanical_pass and g0["pass"] and g6["pass"]),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: v["pass"] for k, v in gates.items() if isinstance(v, dict) and "pass" in v}, indent=2))
    if not g5["pass"]:
        raise AssertionError(
            "G5 (decorrelation check) FAILED -- blocks remain correlated at the chosen gap. Per the "
            "registration (reusing M4-F6's own discipline verbatim) this VOIDS the leg. See "
            "results/m4_f8_occasion_axis_live/gates.json. Do NOT increase the gap and re-run silently; "
            "write the void outcome."
        )
    if not g6["internal_consistency_check"]["pass"]:
        raise AssertionError(
            "G6 internal-consistency check FAILED -- the ablation helper's INTACT reconstruction does not "
            "reproduce f6().generate_world_spread's own output. This is a code defect, not a scientific "
            "finding about channel liveness. VOIDS the leg. See results/m4_f8_occasion_axis_live/gates.json."
        )
    if not mechanical_pass:
        raise AssertionError(
            "Mechanical gate(s) (G1/G2/G3/G4) failed; see results/m4_f8_occasion_axis_live/gates.json."
        )
    if not g0["pass"]:
        print(
            "[G0] UNDERPOWERED: half-width "
            f"{g0['minimum_detectable_paired_difference_half_width']:.6f} > bar {G0_HALF_WIDTH_BAR}. "
            "Per the registration, run_finalize will adjudicate NOTHING and record this determination "
            "plainly -- this is NOT a failure that voids the leg's other gates."
        )
    if not g6["pass"]:
        print(
            "[G6] VACUOUS: the between-author-variance ratio is not statistically distinguishable from "
            "1.0 at kappa=0.5. Per the registration, run_finalize will adjudicate NOTHING and record this "
            "determination plainly -- this is NOT a failure that voids the leg's other gates."
        )
    return gates


# ---------------------------------------------------------------------------
# Adjudication -- exactly the registered leans/pivot, no more. Only called by
# run_finalize when BOTH G0 and G6 PASS.

def adjudicate(g0: dict[str, Any], g6: dict[str, Any], summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    b1 = summaries[cell_name_spread_x16(1)]
    b8 = summaries[cell_name_spread_x16(8)]

    diff_long = np.asarray(b8["truth_long_world_values"], dtype=float) - np.asarray(b1["truth_long_world_values"], dtype=float)
    diff_exact = np.asarray(b8["truth_exact_world_values"], dtype=float) - np.asarray(b1["truth_exact_world_values"], dtype=float)
    ci_long = f6()._paired_ci(diff_long)
    ci_exact = f6()._paired_ci(diff_exact)

    lean_a_hold = bool(ci_long["ci_excludes_zero_positive"])
    lean_a = {
        "lean": "a", "rule": "TRAIT AXIS EXISTS: long-window truth recovery (Variant B) RISES with B, "
        "paired-by-world B8-B1 CI excluding 0, kappa=0.5",
        "paired_diff_B8_minus_B1": ci_long,
        "verdict": "HOLD" if lean_a_hold else "MISS",
    }

    gain_is_positive = bool(ci_long["mean"] > 0)
    half_of_b_gain = 0.5 * ci_long["mean"]
    if gain_is_positive:
        lean_b_hold = bool(ci_exact["mean"] <= half_of_b_gain)
        lean_b_verdict = "HOLD" if lean_b_hold else "MISS"
    else:
        lean_b_verdict = "INAPPLICABLE"
    lean_b = {
        "lean": "b", "rule": "DIFFERENT OBJECT, NOT BETTER ESTIMATE: same-occasion recovery (Variant A) "
        "rises by less than half of any long-window (Variant B) gain; registered as INAPPLICABLE, not "
        "scored, if the long-window gain is negative or null (point estimate <= 0)",
        "paired_diff_A_B8_minus_B1": ci_exact,
        "long_window_gain_mean": ci_long["mean"],
        "gain_is_positive": gain_is_positive,
        "half_of_lean_a_gain": half_of_b_gain,
        "verdict": lean_b_verdict,
    }

    kappa05_cells = [summaries[cell_name_spread_x16(b)] for b in BLOCK_COUNTS]
    agreements = {c["block_count"]: c["agreement_mean"] for c in kappa05_cells}
    ref = agreements[1]
    band = 0.20 * abs(ref)
    per_b_within = {b: bool(abs(agreements[b] - ref) <= band) for b in BLOCK_COUNTS}
    lean_c_hold = bool(all(per_b_within.values()))
    max_val, min_val = max(agreements.values()), min(agreements.values())
    reading2_hold = bool((max_val - min_val) <= band)
    lean_c = {
        "lean": "c", "rule": "GAUGE BLINDNESS REPLICATES: split-half agreement remains B-invariant within "
        "+/-20% of its B=1 value at authors x16, kappa=0.5 (Reading 1, adopted -- per-point band, matching "
        "M4-F6's/M4-F7's own adopted reading); Reading 2 (stricter, max-to-min<=20% of B=1) computed "
        "alongside per this line's disclosure convention",
        "agreement_by_block_count": agreements,
        "b1_reference": ref,
        "band_abs": band,
        "max_minus_min": float(max_val - min_val),
        "per_b_within_band": per_b_within,
        "reading2_max_minus_min_le_band": reading2_hold,
        "verdict": "HOLD" if lean_c_hold else "MISS",
    }

    pivot_condition_no_rise = bool(ci_long["ci_includes_zero"] or not ci_long["ci_excludes_zero_positive"])
    powered_and_live = bool(g0["pass"] and g6["pass"])
    pivot_fires = bool(powered_and_live and pivot_condition_no_rise)
    pivot = {
        "registered_rule": "adequately powered (G0 PASS) AND causally live (G6 PASS) AND long-window truth "
        "recovery does not rise with B (paired CI includes 0) -> the closure is finally EARNED",
        "adequately_powered": g0["pass"],
        "causally_live": g6["pass"],
        "no_rise_condition": pivot_condition_no_rise,
        "paired_diff_B8_minus_B1_ci95": [ci_long["ci95_low"], ci_long["ci95_high"]],
        "fires": pivot_fires,
    }

    if pivot_fires:
        verdict = "CLOSURE_EARNED_TRAIT_LEVEL_UNCERTIFIABLE_ON_ALL_THREE_PANEL_AXES"
    elif powered_and_live and lean_a_hold and (lean_b_verdict in ("HOLD", "INAPPLICABLE")) and lean_c_hold:
        verdict = "OCCASION_AXIS_IS_THE_TRAIT_CERTIFYING_DIMENSION_D3_REBUILT_AROUND_IT"
    else:
        verdict = "MIXED_SEE_LEAN_ADJUDICATION"

    full_table = [
        {
            "block_count": b,
            "agreement_mean": summaries[cell_name_spread_x16(b)]["agreement_mean"],
            "agreement_se": summaries[cell_name_spread_x16(b)]["agreement_se"],
            "truth_recovery_exact_mean": summaries[cell_name_spread_x16(b)]["truth_recovery_exact_mean"],
            "truth_recovery_exact_se": summaries[cell_name_spread_x16(b)]["truth_recovery_exact_se"],
            "truth_recovery_long_mean": summaries[cell_name_spread_x16(b)]["truth_recovery_long_mean"],
            "truth_recovery_long_se": summaries[cell_name_spread_x16(b)]["truth_recovery_long_se"],
        }
        for b in BLOCK_COUNTS
    ]

    return {
        "lean_a": lean_a, "lean_b": lean_b, "lean_c": lean_c,
        "pivot": pivot, "verdict": verdict,
        "full_b_vs_metrics_table": full_table,
    }


# ---------------------------------------------------------------------------

def run_finalize() -> None:
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    spread_cells = [cell_name_spread_x16(b) for b in BLOCK_COUNTS]
    summaries = {cell: cell_summary(cell) for cell in spread_cells}
    anchor_summary = cell_summary(ANCHOR_CELL)
    construction_summary = cell_summary(CONSTRUCTION_CHECK_CELL)

    g0 = gates["G0"]
    g6 = gates["G6"]

    # ---- Disclosed post-hoc addition (self-reported, added AFTER observing
    # a real G5 failure during this leg's own execution -- see the report's
    # Honest disclosures). The ORIGINAL script, mirroring F7's own structure,
    # assumed run_finalize would never be reached after a G1-G5 failure,
    # because run_gates() raises and halts the SAME invocation before
    # finalize would run (exactly F6's/F7's own discipline). Running each
    # stage as a SEPARATE foreground call (required by this task's own
    # 120s-per-call chunking constraint) exposed a real gap: with gates.json
    # already persisted showing G5 FAILED, invoking --stage finalize
    # independently needs to know NOT to adjudicate. This branch does not
    # alter GAP, the |t|<2.0 threshold, kappa, block counts, or any other
    # design/scientific parameter -- it only prevents adjudication from
    # silently proceeding past a gate whose pre-existing, verbatim-reused
    # M4-F6 Part 0.7 rule says a failure VOIDS the leg. A disclosed,
    # explicitly-labeled "Reading 2" side computation (using the SAME
    # adjudicate() function, unmodified) is included for transparency but is
    # NOT adopted -- see the ambiguity_disclosure field below.
    if not gates.get("mechanical_gates_pass", False):
        failed_gates = [g for g in ("G1", "G2", "G3", "G4", "G5") if not gates.get(g, {}).get("pass", False)]
        reading2_adjudication = adjudicate(g0, g6, summaries)
        adjudication = {
            "verdict": "VOID_MECHANICAL_GATE_FAILURE",
            "failed_gates": failed_gates,
            "g5_detail": gates["G5"],
            "g0_power_statement": g0,
            "g6_channel_liveness_statement": g6,
            "ambiguity_disclosure": {
                "question": "Does a G1-G5 mechanical-gate failure void the leg even though G0 and G6 both "
                "PASS, or does the task prompt's own summary line ('Gates (six; G0 and G6 are the ones that "
                "can void the leg)') mean only G0/G6 govern voidability for this specific registration, so "
                "adjudication should proceed despite the G5 failure?",
                "reading_1_adopted": "G5 retains its pre-existing, verbatim-reused consequence (M4-F6's own "
                "Part 0.7 rule, explicitly required reading for this task, 'A |t|>=2.0 at ANY tested cell "
                "VOIDS the leg per the registration', unchanged through M4-F7 and this leg): the leg is "
                "VOID regardless of G0/G6. Adopted because weakening an established, explicitly-required-"
                "reading safeguard specifically because it produced an inconvenient result here is exactly "
                "the kind of post-hoc softening this task forbids; the task's summary line is read as "
                "flagging the two NEW standing-rule gates this registration adds, not as silently "
                "overriding G5's own pre-existing, cross-leg rule.",
                "reading_2_not_adopted": "the task prompt's summary parenthetical is read as an exhaustive, "
                "leg-specific override making G5 non-voiding for M4-F8 specifically; adjudication proceeds "
                "using the already-collected data, with the G5 failure disclosed as a caveat rather than a "
                "void trigger.",
                "reading_2_would_be_adjudication_NOT_ADOPTED": reading2_adjudication,
            },
            "note": (
                "Per Reading 1 (adopted): a G1-G5 gate failure VOIDS the leg outright regardless of G0/G6's "
                "own determinations (both PASS here, reported above for completeness -- they do not rescue "
                "a mechanical gate failure). Leans (a)/(b)/(c) and the pivot are NOT adjudicated under the "
                "adopted reading. The failing gate's own threshold (|t|<2.0) and the GAP=40 design constant "
                "were NOT altered or re-run after observing this result; per the registration's own explicit "
                "instruction ('Do NOT increase the gap and re-run silently; write the void outcome'), this "
                "is written as observed."
            ),
        }
        all_rows = []
        combined = dict(summaries)
        combined[ANCHOR_CELL] = anchor_summary
        combined[CONSTRUCTION_CHECK_CELL] = construction_summary
        for cell, s in combined.items():
            if cell in summaries:
                role = "adjudicated_common_budget_x16"
            elif cell == ANCHOR_CELL:
                role = "gate_anchor_raw_budget_x16"
            else:
                role = "gate_only_construction_check_mult1"
            row = {k: v for k, v in s.items() if k not in (
                "world_seeds", "world_values", "truth_exact_world_values",
                "truth_long_world_values", "g5_world_values"
            )}
            row["role"] = role
            all_rows.append(row)
        pd.DataFrame(all_rows).to_csv(OUT / "cells.csv", index=False)

        decision = {
            "experiment": "M4-F8_occasion_axis_live",
            "banner": BANNER,
            "tier": "EXPLORATORY",
            "registered_spec": "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md#M4-F8-registration",
            "part0_registered_in": "reports/SUICA_M4_F8_OCCASION_AXIS_LIVE_REPORT.md Part 0 (before run)",
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "master_seed": MASTER_SEED,
            "worlds_per_cell": WORLDS_PER_CELL,
            "draws_per_world": DRAWS,
            "gap": f6().GAP,
            "m_common": f6().M_COMMON,
            "author_mult": AUTHOR_MULT,
            "kappa": KAPPA,
            "base_cell": f"{ANCHOR_CELL} (author_mult=16, event_mult=1)",
            "gates": {k: (v["pass"] if isinstance(v, dict) and "pass" in v else v) for k, v in gates.items()},
            "gates_all_pass": gates["all_pass"],
            "gates_mechanical_pass": gates["mechanical_gates_pass"],
            "adjudication": adjudication,
            "label_free": True,
            "claim_boundary": (
                "VOID: a mechanical gate (G5, decorrelation) failed at authors x16/kappa=0.5, so no "
                "scientific claim about the occasion axis is licensed by this leg's adjudicated sweep under "
                "the adopted reading. See adjudication.note and adjudication.ambiguity_disclosure."
            ),
        }
        (OUT / "decision.json").write_text(json.dumps(decision, indent=2, default=str) + "\n", encoding="utf-8")
        print(json.dumps({"verdict": adjudication["verdict"], "failed_gates": failed_gates}, indent=2, default=str))
        return

    if not g6["pass"]:
        adjudication = {
            "verdict": "VACUOUS_NO_ADJUDICATION",
            "g6_channel_liveness_statement": g6,
            "g0_power_statement": g0,
            "note": "Per the registration's G6 CHANNEL LIVENESS gate: the between-author-variance ratio "
            "(state intact vs. state-zeroed) is not statistically distinguishable from 1.0 at kappa=0.5 "
            "at block_count=1 and/or block_count=8. The leg is VACUOUS -- leans (a)/(b)/(c) and the pivot "
            "are NOT adjudicated and NO null is reported, regardless of G0's own determination.",
        }
    elif not g0["pass"]:
        adjudication = {
            "verdict": "UNDERPOWERED_NO_ADJUDICATION",
            "g0_power_statement": g0,
            "g6_channel_liveness_statement": g6,
            "note": "Per the registration's G0 POWER gate: G6 confirms the channel is causally live, but "
            "this leg's realized paired CI half-width exceeds the .0407 bar, so it is UNDERPOWERED. Leans "
            "(a)/(b)/(c) and the pivot are NOT adjudicated and NO null is reported -- this is the "
            "registered, correct response to this outcome, not a fallback.",
        }
    else:
        adjudication = adjudicate(g0, g6, summaries)

    all_rows = []
    combined = dict(summaries)
    combined[ANCHOR_CELL] = anchor_summary
    combined[CONSTRUCTION_CHECK_CELL] = construction_summary
    for cell, s in combined.items():
        if cell in summaries:
            role = "adjudicated_common_budget_x16"
        elif cell == ANCHOR_CELL:
            role = "gate_anchor_raw_budget_x16"
        else:
            role = "gate_only_construction_check_mult1"
        row = {k: v for k, v in s.items() if k not in (
            "world_seeds", "world_values", "truth_exact_world_values",
            "truth_long_world_values", "g5_world_values"
        )}
        row["role"] = role
        all_rows.append(row)
    pd.DataFrame(all_rows).to_csv(OUT / "cells.csv", index=False)

    decision = {
        "experiment": "M4-F8_occasion_axis_live",
        "banner": BANNER,
        "tier": "EXPLORATORY",
        "registered_spec": "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md#M4-F8-registration",
        "part0_registered_in": "reports/SUICA_M4_F8_OCCASION_AXIS_LIVE_REPORT.md Part 0 (before run)",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "worlds_per_cell": WORLDS_PER_CELL,
        "draws_per_world": DRAWS,
        "gap": f6().GAP,
        "m_common": f6().M_COMMON,
        "author_mult": AUTHOR_MULT,
        "kappa": KAPPA,
        "base_cell": f"{ANCHOR_CELL} (author_mult=16, event_mult=1)",
        "gates": {k: (v["pass"] if isinstance(v, dict) and "pass" in v else v) for k, v in gates.items()},
        "gates_all_pass": gates["all_pass"],
        "gates_mechanical_pass": gates["mechanical_gates_pass"],
        "adjudication": adjudication,
        "label_free": True,
        "claim_boundary": (
            "Synthetic occasion-spread finding in a world calibrated to the opened PANDORA D-panel "
            "regime, repeated at authors x16 (M4-F7's own scale) and kappa=0.5 (the one value where the "
            "manipulation is BOTH causally live and adequately powered); licenses a finding about whether "
            "spreading observation across widely-separated occasion blocks certifies a trait-like object "
            "under this synthetic instrument, AT THIS SCALE AND KAPPA. No claim about the real relation "
            "field's content, personality, emotion, diagnosis, or any individual."
        ),
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(adjudication, indent=2, default=str))


# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage", choices=["g6", "anchor", "construction-check", "sweep", "gates", "finalize", "all"], default="all"
    )
    parser.add_argument("--workers", type=int, default=max(2, min(8, (os.cpu_count() or 4) - 2)))
    parser.add_argument("--draws", type=int, default=DRAWS)
    parser.add_argument("--block-counts", type=str, default="1,2,4,8")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if not REF_PATH.exists():
        raise AssertionError(f"{REF_PATH} missing (M4-F1 artifact required, read-only).")
    if not F1_CELLS_CSV.exists():
        raise AssertionError(f"{F1_CELLS_CSV} missing (M4-F1 artifact required, read-only).")
    if not F5_CELLS_CSV.exists():
        raise AssertionError(f"{F5_CELLS_CSV} missing (M4-F5 artifact required, read-only).")
    if not F6_CELLS_CSV.exists():
        raise AssertionError(f"{F6_CELLS_CSV} missing (M4-F6 artifact required, read-only).")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

    f1_cal = json.loads(F1_CALIBRATION.read_text(encoding="utf-8"))
    if f1_cal["status"] != "CALIBRATED":
        raise AssertionError("M4-F1 calibration_record.json is not CALIBRATED.")
    knobs = f1_cal["selected"]["knobs"]
    knob_tag = f1().knob_tag(knobs)

    block_counts = [int(x) for x in args.block_counts.split(",") if x]

    if args.stage in ("g6", "all"):
        run_gate_g6(knobs, knob_tag, args.workers)
    if args.stage in ("anchor", "all"):
        run_anchor(knobs, knob_tag, args.workers, args.draws)
    if args.stage in ("construction-check", "all"):
        run_construction_check(knobs, knob_tag, args.workers, args.draws)
    if args.stage in ("sweep", "all"):
        run_sweep(knobs, knob_tag, args.workers, args.draws, block_counts)
    if args.stage in ("gates", "all"):
        run_gates(knobs, knob_tag, args.workers)
    if args.stage in ("finalize", "all"):
        run_finalize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
