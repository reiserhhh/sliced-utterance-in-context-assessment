#!/usr/bin/env python3
"""M4-F9 -- the decisive occasion cell, repaired gate, fresh seeds (authors x16, kappa=0.5).

Registered spec: docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md section
"M4-F9 registration (2026-08-03, BEFORE run) -- the decisive cell, repaired
gate, fresh seeds", together with the preceding "M4-F8 planner adjudication
note -- a defective gate, and the standard the agent set" (why this leg
exists: M4-F8 itself passed G0 power and G6 channel liveness cleanly but
VOIDED on G5, a nil-significance |t|<2.0 test on a residual that is nonzero
by construction (phi^41 = 1.06e-4 at the calibrated phi_hi=.80), whose
failure probability therefore grows with sample size rather than shrinking).
Part 0 register-notes (every implementation choice this registration left
open, written BEFORE any compute) are in
reports/SUICA_M4_F9_OCCASION_AXIS_REPAIRED_REPORT.md Part 0.

THIS SCRIPT REUSES M4-F8 WHOLESALE. Design is IDENTICAL to M4-F8 in every
scientific respect -- shared-occasion design, kappa=0.5, authors x16,
common-budget construction, block count B in {1,2,4,8}, the G5-verified
40-step gap, 8 worlds x 20 draws, gauge/map/D0/halving unchanged, both M4-F5
truth variants at every cell, the SAME G0 POWER target/bar and G6 CHANNEL
LIVENESS design M4-F8 introduced. EXACTLY TWO REGISTERED DESIGN CHANGES:

  1. FRESH WORLD SEEDS for this leg's own adjudicated cells (the 4
     `b{1,2,4,8}_x16_shared_k05` sweep cells and G6's 2 kappa=0.5 gating
     rows) -- a new master-seed offset, MASTER_SEED_OFFSET, folded into the
     seed_key string fed to f6().spread_world_seed_for (UNCHANGED, called
     verbatim). Every ORIGINAL-lineage check (G1's base1x anchor, G2(a)'s
     construction-check against M4-F6's persisted b1_shared_k05, G2(b)'s
     anchor against M4-F5's persisted authors_x16_shared_k05, and G6's
     non-gating kappa=1.0 context row reusing M4-F7's own seed_key) is left
     on the ORIGINAL seed lineage, untouched -- these exist to reproduce
     historical, persisted numbers, and re-seeding them would break the
     thing they check. Part 0.1 discloses the implementation-mechanism
     ambiguity this required resolving (F6's own spread_world_seed_for bakes
     ITS master seed in as a closure constant inside f6.py, not a parameter,
     so a literal numeric override would require reimplementing the
     per-world engine; folding the offset into seed_key instead achieves an
     equally fresh, hash-uncorrelated, disclosed, reproducible lineage with
     ZERO new per-world engine code -- the reading adopted here).
  2. G5 REPAIRED TO AN EQUIVALENCE FORM: the 95% CI of the POOLED
     cross-block correlation (every G5-applicable per-world correlation
     value across ALL THREE block_count>=2 cells, pooled into one n=24
     sample) must lie ENTIRELY inside +/-0.005, replacing M4-F8's own
     (M4-F6-inherited) per-cell nil-significance |t|<2.0 rule. The
     theoretical residual (phi_hi^41 at the calibrated phi range, read from
     the SAME calibration knobs every world uses) is reported beside the
     measured pooled value as a coherence check.

NOTHING ELSE CHANGES: kappa=0.5, authors x16, B in {1,2,4,8}, the 40-step
gap, common-budget construction, 8 worlds x 20 draws, the gauge/map/D0/
halving, both truth variants, and the leans/pivot are carried over WORD FOR
WORD from M4-F8 (reused as the literal SAME function object,
f8().adjudicate, not re-typed).

Reuse boundary -- maximal, by loading M4-F8's OWN script as a seventh frozen
module (f8(), exactly as F8 itself loaded f1()..f7()), not merely as a
design template:
  - f8().cell_name_spread_x16 -- cell NAMING is unchanged (only seed_key
    changes), so this leg's cells remain directly comparable to F8's own by
    identity.
  - f8().build_construction_check_task, f8().build_anchor_task -- called
    UNCHANGED; these two cells stay on the ORIGINAL seed lineage by design
    (see change #1 above) and are reused byte-for-byte, task dict and all.
  - f8()._read_f5_persisted_row, f8()._read_f6_persisted_row, f8()._diff_row
    -- called UNCHANGED for G2's two sub-checks (both read shared, read-only
    F5/F6 artifacts independent of which leg is asking).
  - f8().g6_analytic_coefficient, f8()._g6_world_task, f8()._g6_sanity_check
    -- called UNCHANGED for G6; none of these three functions depends on a
    module-level seed constant -- they consume whatever seed_key a task dict
    supplies, so passing THIS leg's fresh seed_key through an unchanged
    function reuses F8's own ablation mathematics exactly while still
    drawing fresh numbers.
  - f8().adjudicate -- called UNCHANGED, the literal same function object,
    for the leans/pivot (word-for-word reuse, not a re-typed copy).
  - From f1()/f2()/f3()/f5()/f6()/f7() (loaded exactly as F8 itself loaded
    them): f1().knob_tag (main() only); f2().run_gate_g1; f3().run_gate_g3;
    f5().run_truth_sweep_world, f5().G4_TOLERANCE; f6().GAP, f6().M_COMMON,
    f6()._paired_ci, f6().spread_world_seed_for; f7().run_spread_sweep_world,
    f7().common_layout_scaled -- ALL called directly, unchanged, exactly as
    F8 itself called them.

NEW in this script (nothing above is reimplemented):
  - `fresh_seed_key`: folds MASTER_SEED_OFFSET into the seed_key string for
    this leg's own adjudicated draws (change #1).
  - `build_spread_tasks`: a disclosed near-duplicate of f8().build_spread_
    tasks, changing ONLY the seed_key line (fresh_seed_key(...) in place of
    F8's own f"b{block_count}_x16_{KAPPA_TAG}") and this leg's own budget_
    label/corpus_prefix ("f9.0"/"m4f9-", cosmetic namespacing only, matching
    the established per-leg convention).
  - `run_gate_g5`: REWRITTEN to the registered equivalence form (change #2),
    with a disclosed, NOT-adopted per-cell alternative reading and the
    theoretical-residual coherence check, both computed alongside.
  - `run_gate_g6`: a disclosed near-duplicate of f8().run_gate_g6, changing
    ONLY the two kappa=0.5 gating_specs seed_key strings to fresh_seed_key(1)
    /fresh_seed_key(8) (context_specs, F7's own "b1_x16_k10", is UNCHANGED);
    delegates all actual computation to f8()'s own unchanged helpers.
  - `run_gate_g0`, `run_gate_g2`, `run_gate_g4`, `cell_summary`, `_write_cell`,
    `run_anchor`, `run_construction_check`, `run_sweep`, `run_gates`: OUT-
    scoped near-duplicates of F8's own same-named functions (every leg's own
    cell_summary/gates has always been OUT-scoped even when the underlying
    rule is reused verbatim -- see F5's/F6's/F7's/F8's own).
  - `run_finalize`: the mechanical-gate-VOID branch is built in FROM THE
    START (not patched in after observing a failure, unlike F8's own
    disclosed Part 0.9 addition) -- this leg's own Part 0 pre-empts that
    documented need, citing F8's own report directly, since running each
    stage as a separate foreground call is known in advance to require it.

Stages (resumable, artifacts under results/m4_f9_occasion_axis_repaired/):
  --stage g6                  CHANNEL LIVENESS (analytic + empirical), run
                               FIRST and standalone-capable; persists
                               g6_gate.json.
  --stage anchor               the RAW authors_x16_shared_k05 gate-anchor
                               cell (ORIGINAL seed lineage).
  --stage construction-check  the mult=1/block_count=1/kappa=0.5 GATE-ONLY
                               cell (ORIGINAL seed lineage), must reproduce
                               M4-F6's own persisted b1_shared_k05.
  --stage sweep                the 4 adjudicated b{1,2,4,8}_x16_k05 cells
                               (FRESH seed lineage; --block-counts selects a
                               subset for chunked execution).
  --stage gates                G0-G6, writes gates.json; STOPS on G1/G2/G3/
                               G4/G5 failure or a G6 internal-consistency
                               failure; does NOT stop on G0 or G6-channel-
                               liveness failure alone.
  --stage finalize             G0-and-G6-gated adjudication + decision.json +
                               cells.csv.
  --stage all                  g6 + anchor + construction-check + sweep +
                               gates + finalize.
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

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import suica_core.v8_realtext_relation_field as v8  # noqa: E402,F401

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"
MASTER_SEED = 20260802  # identity constant, exactly every prior leg's own MASTER_SEED (unchanged, kept for
                         # provenance/display parity -- NOT itself used to derive this leg's fresh draws; see
                         # MASTER_SEED_OFFSET/FRESH_MASTER_SEED below and Part 0.1 of the report).
MASTER_SEED_OFFSET = 90000000  # NEW, registered here: this leg's own "fresh master-seed offset" (change #1).
                                # Arbitrary-but-fixed-before-compute large increment; disclosed, not tuned.
FRESH_MASTER_SEED = MASTER_SEED + MASTER_SEED_OFFSET  # 110260802 -- folded into seed_key (Part 0.1).
DRAWS = 20
WORLDS_PER_CELL = 8
MIN_RETAINED_EVENTS = 8  # the deployed gauge's own split-half retention floor (unused directly here; inherited
                          # automatically via f7().run_spread_sweep_world's own constant, exactly as in F8).

AUTHOR_MULT = 16  # unchanged from M4-F7/M4-F8.
KAPPA_TAG = "k05"
KAPPA = 0.5  # unchanged from M4-F8 -- kappa is NOT a design change this leg; only seeds and G5's form are.
DESIGN = "shared"
BLOCK_COUNTS = [1, 2, 4, 8]

G0_HALF_WIDTH_BAR = 0.0407  # unchanged from M4-F8: half M4-F5's authors_x16_shared_k05 target (.081307/2).
G5_EQUIVALENCE_DELTA = 0.005  # NEW (change #2): registered equivalence margin, ~50x the largest theoretical
                               # residual (phi_hi**41 = 1.06e-4); see g5_theoretical_residual and Part 0.2.

OUT = ROOT / "results" / "m4_f9_occasion_axis_repaired"
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
    of the seven scripts this leg loads."""
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
_F5 = None
_F6 = None
_F7 = None
_F8 = None


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


def f8() -> Any:
    global _F8
    if _F8 is None:
        _F8 = _load_script("run_suica_m4_f8_occasion_axis_live.py")
    return _F8


# ---------------------------------------------------------------------------
# Change #1 -- FRESH WORLD SEEDS. fresh_seed_key folds MASTER_SEED_OFFSET
# into the seed_key string fed to f6().spread_world_seed_for (called
# UNCHANGED everywhere below). Part 0.1 of the report discloses why this
# mechanism was adopted over reimplementing the per-world engine.

def fresh_seed_key(block_count: int) -> str:
    return f"{FRESH_MASTER_SEED}-b{block_count}_x16_{KAPPA_TAG}"


def build_spread_tasks(
    knobs: dict[str, Any], knob_tag: str, draws: int, block_counts: list[int]
) -> list[dict[str, Any]]:
    """Disclosed near-duplicate of f8().build_spread_tasks, changing ONLY
    the seed_key formula (fresh_seed_key(block_count) in place of F8's own
    f"b{block_count}_x16_{KAPPA_TAG}") and this leg's own budget_label/
    corpus_prefix ("f9.0"/"m4f9-", cosmetic namespacing matching the
    established per-leg convention -- F6 used "f6.0"/"m4f6-", F8 used
    "f8.0"/"m4f8-"). Cell NAME (f8().cell_name_spread_x16) is UNCHANGED.
    The per-world ENGINE (f7().run_spread_sweep_world) that consumes these
    tasks is reused byte-for-byte, unchanged (see module docstring)."""
    tasks = []
    gap = f6().GAP
    for block_count in block_counts:
        seed_key = fresh_seed_key(block_count)
        cell = f8().cell_name_spread_x16(block_count)
        for world in range(WORLDS_PER_CELL):
            tasks.append(
                {
                    "cell": cell, "seed_key": seed_key, "world": world,
                    "author_mult": AUTHOR_MULT, "block_count": block_count, "gap": gap, "kappa": KAPPA,
                    "knobs": knobs, "knob_tag": knob_tag, "draws": draws,
                    "ref_path": str(REF_PATH), "budget_label": "f9.0", "corpus_prefix": "m4f9-",
                }
            )
    return tasks


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
    """The RAW authors_x16 gate-anchor cell: ORIGINAL seed lineage (change #1
    does NOT apply here -- this cell exists to reproduce M4-F5's persisted
    value, G0's target AND G2(b)'s comparison target). Task dict from
    f8().build_anchor_task, UNCHANGED; per-world engine f5().run_truth_
    sweep_world, UNCHANGED."""
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = f8().build_anchor_task(knobs, knob_tag, draws)
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
    """G2(a)'s task: ORIGINAL seed lineage (F6's own seed_key/corpus-prefix/
    budget_label, via f8().build_construction_check_task, UNCHANGED) so this
    reproduces M4-F6's persisted b1_shared_k05 bit-for-bit through f7()'s
    generalized orchestration -- a code-correctness check, not a scientific
    cell, exactly as in F8."""
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = f8().build_construction_check_task(knobs, knob_tag, draws)
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
    """The 4 adjudicated common-budget cells: FRESH seed lineage (change #1,
    via THIS script's own build_spread_tasks). Per-world engine
    f7().run_spread_sweep_world, UNCHANGED -- already kappa- and seed_key-
    parametrized via the task dict, needing no new per-world engine at all,
    exactly as F8 itself established."""
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
    """OUT-scoped near-duplicate of f8().cell_summary (every leg's own
    cell_summary has always been OUT-scoped even when the underlying rule is
    reused verbatim); logic UNCHANGED."""
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
# Gates G1/G3 (direct calls, unchanged), G2 (OUT-scoped, calling f8()'s own
# UNCHANGED read/diff helpers), G4 (OUT-scoped), G0 (OUT-scoped).

def run_gate_g1(knobs: dict[str, Any], knob_tag: str, workers: int) -> dict[str, Any]:
    """Direct call, unchanged: kappa<=0 free cell reproduces M4-F1's persisted base1x. ORIGINAL lineage."""
    return f2().run_gate_g1(knobs, knob_tag, workers)


def run_gate_g3() -> dict[str, Any]:
    """Direct call, unchanged: gauge invariance."""
    return f3().run_gate_g3()


def run_gate_g2() -> dict[str, Any]:
    """TWO disclosed sub-checks, BOTH required, mirroring F8's own G2
    structure exactly, BOTH on the ORIGINAL seed lineage (change #1 does not
    apply to gate-anchor/construction-check cells): (a) CONSTRUCTION -- the
    construction_check_mult1_b1_k05 cell (mult=1, block_count=1, kappa=0.5,
    computed via f7()'s own generalized orchestration using F6's own
    seed_key/corpus-prefix/budget_label) reproduces M4-F6's persisted
    b1_shared_k05 to <=1e-12. (b) ANCHOR -- the RAW authors_x16_shared_k05
    cell (a direct, unchanged call to f5().run_truth_sweep_world on f4()'s
    own byte-identical mult=16/k05 task, via f8().build_anchor_task)
    reproduces M4-F5's persisted authors_x16_shared_k05 (agreement + BOTH
    truth variants) to <=1e-12 -- the registration's own explicitly stated
    check. Both read/diff helpers (f8()._read_f6_persisted_row,
    f8()._read_f5_persisted_row, f8()._diff_row) are reused UNCHANGED --
    they only read shared, read-only F5/F6 artifacts, independent of which
    leg is asking."""
    construction_path = OUT / f"cell_{CONSTRUCTION_CHECK_CELL}.csv"
    if not construction_path.exists():
        raise AssertionError(f"G2(a) requires {construction_path} to exist; run --stage construction-check first.")
    got_construction = cell_summary(CONSTRUCTION_CHECK_CELL)
    target_construction = f8()._read_f6_persisted_row("b1_shared_k05")
    diffs_a, pass_a = f8()._diff_row(got_construction, target_construction)

    anchor_path = OUT / f"cell_{ANCHOR_CELL}.csv"
    if not anchor_path.exists():
        raise AssertionError(f"G2(b) requires {anchor_path} to exist; run --stage anchor first.")
    got_anchor = cell_summary(ANCHOR_CELL)
    target_anchor = f8()._read_f5_persisted_row(ANCHOR_CELL)
    diffs_b, pass_b = f8()._diff_row(got_anchor, target_anchor)

    return {
        "gate": "G2",
        "description": "TWO sub-checks, both required, both on the ORIGINAL seed lineage (change #1 -- fresh "
        "seeds -- applies only to this leg's own adjudicated sweep cells and G6's gating rows, never to "
        "gate-anchor/reproduction checks): (a) CONSTRUCTION -- the mult=1/block_count=1/kappa=0.5 cell, "
        "computed through f7()'s generalized orchestration using F6's own seed_key/corpus-prefix/budget_label "
        "(via f8().build_construction_check_task, unchanged), reproduces M4-F6's persisted b1_shared_k05 to "
        "<=1e-12; (b) ANCHOR -- the RAW authors_x16_shared_k05 cell (f5().run_truth_sweep_world, unchanged, "
        "on f4()'s own byte-identical mult=16/k05 task, via f8().build_anchor_task, unchanged) reproduces "
        "M4-F5's persisted authors_x16_shared_k05 to <=1e-12 (the registration's own explicitly stated check, "
        "the SAME row G0 reads, for a different purpose).",
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
    """Truth-path invariance, as M4-F5/M4-F6/M4-F7/M4-F8: two independent
    routes to the identical finite-sample field agree to <=G4_TOLERANCE, for
    every world of every cell (construction-check + anchor + 4 adjudicated
    x16 cells) -- regardless of which seed lineage that cell used."""
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
        "field agree to <=G4_TOLERANCE, for every world of every cell (matching M4-F5's/M4-F6's/M4-F7's/"
        "M4-F8's own check)",
        "tolerance": f5().G4_TOLERANCE,
        "rows": rows,
        "pass": bool(all_pass),
    }


def run_gate_g0(target_cell: str = ANCHOR_CELL) -> dict[str, Any]:
    """POWER (M4-F6/M4-F7/M4-F8 planner-note standing rule), UNCHANGED
    construction and target from F8: report the target's measured level at
    this scale from M4-F5's OWN persisted authors_x16_shared_k05 cell (read
    verbatim, never retyped -- ORIGINAL lineage), and the minimum detectable
    paired difference THIS leg's own REALIZED SEs afford on its FRESH-seeded
    b8_x16/b1_x16 sweep cells (the b8_x16-b1_x16 paired-by-world CI
    half-width on truth_recovery_long, kappa=0.5, using F6's own _paired_ci
    construction verbatim). FAILS (declared UNDERPOWERED) if that half-width
    exceeds G0_HALF_WIDTH_BAR=.0407. Does NOT raise/void the run -- a
    registered, anticipated, valid scientific outcome that run_finalize
    must still report in full, not a mechanical defect."""
    f5_frame = pd.read_csv(F5_CELLS_CSV)
    f5_row = f5_frame.loc[f5_frame["cell"] == target_cell].iloc[0]
    target_level_mean = float(f5_row["truth_recovery_long_mean"])
    target_level_se = float(f5_row["truth_recovery_long_se"])

    b1 = cell_summary(f8().cell_name_spread_x16(1))
    b8 = cell_summary(f8().cell_name_spread_x16(8))
    diff_long = np.asarray(b8["truth_long_world_values"], dtype=float) - np.asarray(b1["truth_long_world_values"], dtype=float)
    ci_long = f6()._paired_ci(diff_long)
    half_width = float((ci_long["ci95_high"] - ci_long["ci95_low"]) / 2.0)
    adequately_powered = bool(half_width <= G0_HALF_WIDTH_BAR)

    return {
        "gate": "G0",
        "description": "POWER (M4-F6/M4-F7/M4-F8 planner-note standing rule, unchanged): report the target's "
        "measured level at this scale from M4-F5's own persisted authors_x16_shared_k05 cell (ORIGINAL "
        "lineage), and the minimum detectable paired difference (B8-B1 truth_recovery_long paired-by-world "
        "95% CI half-width, on THIS leg's own fresh-seeded sweep cells) this design's REALIZED SEs actually "
        "afford. FAILS (UNDERPOWERED) if that half-width exceeds .0407 (half the target's measured level, "
        "per the registration).",
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
# Change #2 -- G5 REPAIRED TO AN EQUIVALENCE FORM.

def g5_theoretical_residual(knobs: dict[str, Any], gap: int) -> dict[str, Any]:
    """The theoretical residual cross-block-boundary correlation of the raw
    AR(1) state, computed from the generator's own calibrated phi range --
    NOT retyped from the registration text, but read from the SAME
    calibration knobs every world this leg computes actually uses. Adjacent
    block-boundary pairs are always GAP+1 steps apart regardless of
    block_count (f6().block_boundary_label_pairs: (blk*(s+gap)+s-1,
    (blk+1)*(s+gap)) differ by exactly gap+1), so the theoretical residual
    autocorrelation at the calibrated phi_hi is phi_hi**(gap+1); phi_lo**(gap+1)
    is reported alongside as the OTHER end of the per-author phi range (the
    registration's own illustrative "4.5e-13 at phi=.50" reference point is
    ALSO reported for direct comparison -- it is not phi_lo, which is 0.20 at
    this leg's own calibration, but an independently-checkable illustrative
    value the registration text itself cites)."""
    phi_lo = float(knobs["phi_lo"])
    phi_hi = float(knobs["phi_hi"])
    lag = int(gap) + 1
    return {
        "gap": int(gap), "lag_steps": lag,
        "phi_lo": phi_lo, "phi_hi": phi_hi,
        "residual_at_phi_hi": phi_hi ** lag,
        "residual_at_phi_lo": phi_lo ** lag,
        "registration_illustrative_residual_at_phi_0.50": 0.50 ** lag,
    }


def run_gate_g5(spread_cells: list[str], knobs: dict[str, Any]) -> dict[str, Any]:
    """Decorrelation check, REPAIRED TO AN EQUIVALENCE FORM (M4-F9
    registration, repairing M4-F8's planner-adjudicated defective
    nil-significance gate -- see module docstring and the M4-F8 planner
    adjudication note). READING 1 (ADOPTED): the 95% CI of the POOLED
    cross-block correlation -- every G5-applicable per-world correlation
    value across ALL THREE block_count>=2 cells (b2/b4/b8), pooled into ONE
    n=24 sample via f6()._paired_ci (the SAME one-sample t-CI construction
    used by every paired statistic in this line) -- must lie ENTIRELY inside
    +/-G5_EQUIVALENCE_DELTA=0.005. Adopted because the registration's own
    text says "the 95% CI of THE POOLED correlation" (singular, definite
    article), directly promoting the exact quantity M4-F8's own G5 gate
    already computed and explicitly labeled "pooled_context"/
    "grand_mean_across_cells" as supplementary, not-yet-gating context; it is
    also the statistically natural reading, since the raw AR(1) state's
    cross-block residual autocorrelation at a fixed GAP+1-step lag does not
    depend on block_count (kappa enters only in the SUBSEQUENT blending
    step, and block_count only changes how many boundary pairs exist, not
    the per-pair lag), so all three cells' worlds are exchangeable draws of
    the SAME underlying quantity -- pooling more of them makes the CI
    TIGHTER, which is exactly the property an equivalence form should
    reward, unlike the nil-significance form the M4-F8 planner note
    diagnosed as defective. READING 2 (NOT ADOPTED, disclosed alongside):
    per-cell equivalence -- each cell's OWN 8-world CI must independently
    lie inside +/-0.005, mirroring the OLD rule's "at every cell" structure
    with only the test form (equivalence vs. nil-significance) swapped.
    Also reports the theoretical residual (g5_theoretical_residual) beside
    the measured pooled value as a mandatory coherence check, per the
    registration's own explicit instruction, stating plainly whether they
    are consistent."""
    rows = []
    pooled_values: list[float] = []
    for cell in spread_cells:
        summary = cell_summary(cell)
        if summary["block_count"] <= 1:
            rows.append({"cell": cell, "block_count": summary["block_count"], "applicable": False})
            continue
        world_vals = np.asarray(summary["g5_world_values"], dtype=float)
        pooled_values.extend(world_vals.tolist())
        cell_ci = f6()._paired_ci(world_vals)
        cell_equiv_pass = bool(
            cell_ci["ci95_low"] >= -G5_EQUIVALENCE_DELTA and cell_ci["ci95_high"] <= G5_EQUIVALENCE_DELTA
        )
        rows.append(
            {
                "cell": cell, "block_count": summary["block_count"], "kappa": summary["kappa"],
                "applicable": True,
                "correlation_mean": summary["g5_correlation_mean"],
                "correlation_se": summary["g5_correlation_se"],
                "t_stat_vs_zero_context_only_not_gating": summary["g5_t_stat"],
                "n_pairs_per_world": summary["g5_n_pairs_per_world"],
                "per_cell_ci95_low": cell_ci["ci95_low"],
                "per_cell_ci95_high": cell_ci["ci95_high"],
                "per_cell_equivalence_pass_reading2_not_adopted": cell_equiv_pass,
            }
        )

    applicable_rows = [r for r in rows if r.get("applicable")]
    pooled_arr = np.asarray(pooled_values, dtype=float)
    pooled_ci = f6()._paired_ci(pooled_arr)
    pooled_equiv_pass = bool(
        pooled_ci["ci95_low"] >= -G5_EQUIVALENCE_DELTA and pooled_ci["ci95_high"] <= G5_EQUIVALENCE_DELTA
    )
    reading2_all_pass = bool(
        all(r["per_cell_equivalence_pass_reading2_not_adopted"] for r in applicable_rows)
    ) if applicable_rows else False

    theoretical = g5_theoretical_residual(knobs, f6().GAP)
    measured_abs = abs(pooled_ci["mean"])
    theoretical_worst = theoretical["residual_at_phi_hi"]
    ratio = float(measured_abs / theoretical_worst) if theoretical_worst > 0 else float("inf")
    # Disclosed, fixed-before-compute coherence bar: "same order of magnitude" read as within 10x, calibrated
    # from M4-F8's OWN already-published measured/theoretical ratios (1.7x/5.2x/2.1x at its three cells) --
    # prior, independently-published data, not this leg's own soon-to-be-observed numbers.
    coherence_bar_x = 10.0
    coherent = bool(ratio <= coherence_bar_x)
    coherence_check = {
        "theoretical_residual_at_phi_hi": theoretical_worst,
        "measured_pooled_correlation_mean": pooled_ci["mean"],
        "measured_pooled_correlation_mean_abs": measured_abs,
        "ratio_measured_to_theoretical": ratio,
        "coherence_bar_x": coherence_bar_x,
        "coherence_bar_note": "disclosed before compute: 'same order of magnitude' read as within 10x, "
        "calibrated from M4-F8's own already-published per-cell measured/theoretical ratios (approx. "
        "1.7x/5.2x/2.1x), not from this leg's own data.",
        "consistent_with_theoretical_residual": coherent,
        "statement": (
            f"measured |pooled correlation mean| ({measured_abs:.6e}) is "
            f"{'CONSISTENT' if coherent else 'INCONSISTENT'} with the theoretical worst-case residual "
            f"phi_hi^{theoretical['lag_steps']} = {theoretical_worst:.6e} at the calibrated phi_hi="
            f"{theoretical['phi_hi']} (ratio {ratio:.3f}x against a {coherence_bar_x:.0f}x bar)."
        ),
    }

    return {
        "gate": "G5",
        "description": "decorrelation check, REPAIRED TO AN EQUIVALENCE FORM (M4-F9 registration): READING 1 "
        "(ADOPTED, gating) -- the 95% CI of the POOLED cross-block correlation (all G5-applicable per-world "
        "values across the 3 block_count>=2 cells, n=24, via f6()._paired_ci) must lie entirely inside "
        "+/-0.005. READING 2 (disclosed, NOT adopted) -- per-cell equivalence at each of the 3 cells "
        "independently. A theoretical-residual coherence check (phi_hi**(gap+1)) is reported beside the "
        "measured pooled value.",
        "equivalence_delta": G5_EQUIVALENCE_DELTA,
        "rows": rows,
        "pooled": {
            "n_pooled_values": int(len(pooled_arr)),
            "cells_pooled": [r["cell"] for r in applicable_rows],
            "mean": pooled_ci["mean"], "sd": pooled_ci["sd"], "se": pooled_ci["se"],
            "t_stat_vs_zero_context_only": pooled_ci["t_stat"], "t_crit_95": pooled_ci["t_crit_95"],
            "n": pooled_ci["n"],
            "ci95_low": pooled_ci["ci95_low"], "ci95_high": pooled_ci["ci95_high"],
            "equivalence_pass": pooled_equiv_pass,
        },
        "theoretical_residual": theoretical,
        "coherence_check": coherence_check,
        "reading_2_per_cell_equivalence_not_adopted": {
            "all_cells_pass": reading2_all_pass,
            "note": "disclosed alongside, NOT the gating statistic -- Reading 1 (pooled) is adopted; see "
            "the gate description and the report's Part 0.2.",
        },
        "pass": pooled_equiv_pass,
    }


# ---------------------------------------------------------------------------
# G6 -- CHANNEL LIVENESS. A disclosed near-duplicate of f8().run_gate_g6,
# changing ONLY the two kappa=0.5 gating_specs seed_key strings to this
# leg's own fresh_seed_key (change #1); context_specs (F7's own
# "b1_x16_k10", ORIGINAL lineage) is UNCHANGED. All actual computation
# delegates to f8()'s own unchanged helpers (_g6_world_task,
# g6_analytic_coefficient, _g6_sanity_check) -- none of which depends on a
# module-level seed constant, so passing fresh seed_key through them reuses
# F8's own ablation mathematics exactly while drawing fresh numbers.

def run_gate_g6(knobs: dict[str, Any], knob_tag: str, workers: int) -> dict[str, Any]:
    persisted_path = OUT / "g6_gate.json"
    if persisted_path.exists():
        print("[skip] G6 already computed -> g6_gate.json")
        return json.loads(persisted_path.read_text(encoding="utf-8"))

    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    gap = f6().GAP

    gating_specs = [(KAPPA, 1, fresh_seed_key(1)), (KAPPA, 8, fresh_seed_key(8))]  # FRESH (change #1).
    context_specs = [(1.0, 1, "b1_x16_k10")]  # UNCHANGED: F7's own seed_key -> F7's own bit-identical world
                                               # draws (non-gating validation, ORIGINAL lineage -- this is a
                                               # check against history, not an adjudicated draw; per the
                                               # task's own note, anchors on the original lineage are not
                                               # re-seeded).

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
        rows = list(pool.map(f8()._g6_world_task, tasks))
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

    coeff = f8().g6_analytic_coefficient(KAPPA)

    world0_seed = f6().spread_world_seed_for(fresh_seed_key(1), 0, knob_tag)
    _author_ids, contexts0, _splits, counts0, _raw = f7().common_layout_scaled(reference, AUTHOR_MULT)
    max_diff = f8()._g6_sanity_check(counts0, contexts0, knobs, KAPPA, 1, gap, world0_seed)
    internal_consistency_pass = bool(max_diff <= f5().G4_TOLERANCE)

    result = {
        "gate": "G6",
        "description": "CHANNEL LIVENESS, UNCHANGED design from M4-F8 (analytic AR(1)-state blend "
        "coefficient + empirical between-author-variance ratio ablation), computed on THIS leg's own FRESH "
        "seed_key (change #1) for the kappa=0.5 gating rows (block_count in {1,8}), so G6 certifies the "
        "SAME draws the leans/pivot are computed on, not a separately-seeded proxy. The kappa=1.0 "
        "block_count=1 context row reuses F7's OWN seed_key (ORIGINAL lineage, non-gating validation only). "
        "All computation delegates to f8()'s own unchanged helpers (_g6_world_task, g6_analytic_coefficient, "
        "_g6_sanity_check).",
        "analytic_coefficient_at_kappa": {
            "kappa": KAPPA, "sqrt_1_minus_kappa": coeff, "nonzero": bool(coeff != 0.0),
        },
        "internal_consistency_check": {
            "note": "f8()'s own ablation helper's INTACT reconstruction vs. f6().generate_world_spread's real "
            "output, same inputs (kappa=0.5, block_count=1, world 0, THIS leg's own fresh seed_key) -- a "
            "code-correctness safeguard, not a scientific finding; failure here is treated as a mechanical "
            "defect (raises in run_gates), not as evidence about channel liveness.",
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
    spread_cells = [f8().cell_name_spread_x16(b) for b in BLOCK_COUNTS]
    g1 = run_gate_g1(knobs, knob_tag, workers)
    g3 = run_gate_g3()
    g2 = run_gate_g2()
    all_computed_cells = [CONSTRUCTION_CHECK_CELL, ANCHOR_CELL] + spread_cells
    g4 = run_gate_g4(all_computed_cells)
    g5 = run_gate_g5(spread_cells, knobs)
    g0 = run_gate_g0()
    g6 = run_gate_g6(knobs, knob_tag, workers)
    mechanical_pass = bool(g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"] and g5["pass"])
    gates = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "master_seed_offset": MASTER_SEED_OFFSET,
        "fresh_master_seed": FRESH_MASTER_SEED,
        "knobs": knobs,
        "knob_tag": knob_tag,
        "gap": f6().GAP,
        "m_common": f6().M_COMMON,
        "author_mult": AUTHOR_MULT,
        "kappa": KAPPA,
        "g5_equivalence_delta": G5_EQUIVALENCE_DELTA,
        "G0": g0, "G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5, "G6": g6,
        "mechanical_gates_pass": mechanical_pass,
        "all_pass": bool(mechanical_pass and g0["pass"] and g6["pass"]),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: v["pass"] for k, v in gates.items() if isinstance(v, dict) and "pass" in v}, indent=2))
    if not g5["pass"]:
        raise AssertionError(
            "G5 (decorrelation, repaired equivalence form) FAILED -- the pooled cross-block correlation's "
            "95% CI does not lie entirely inside +/-0.005. Per the registration this VOIDS the leg. See "
            "results/m4_f9_occasion_axis_repaired/gates.json. Do NOT widen delta and re-run silently; write "
            "the void outcome."
        )
    if not g6["internal_consistency_check"]["pass"]:
        raise AssertionError(
            "G6 internal-consistency check FAILED -- the ablation helper's INTACT reconstruction does not "
            "reproduce f6().generate_world_spread's own output. This is a code defect, not a scientific "
            "finding about channel liveness. VOIDS the leg. See results/m4_f9_occasion_axis_repaired/gates.json."
        )
    if not mechanical_pass:
        raise AssertionError(
            "Mechanical gate(s) (G1/G2/G3/G4) failed; see results/m4_f9_occasion_axis_repaired/gates.json."
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
# Adjudication -- f8().adjudicate is reused as the LITERAL SAME FUNCTION
# OBJECT (leans/pivot word-for-word, per the registration), not re-typed.
# Only called by run_finalize when BOTH G0 and G6 PASS.

def run_finalize() -> None:
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    spread_cells = [f8().cell_name_spread_x16(b) for b in BLOCK_COUNTS]
    summaries = {cell: cell_summary(cell) for cell in spread_cells}
    anchor_summary = cell_summary(ANCHOR_CELL)
    construction_summary = cell_summary(CONSTRUCTION_CHECK_CELL)

    g0 = gates["G0"]
    g6 = gates["G6"]

    # ---- Mechanical-gate VOID branch, built in FROM THE START (Part 0 of
    # the report), pre-empting a documented need: F8's own report (Part 0.9)
    # disclosed that running each stage as a SEPARATE foreground call (this
    # task's own chunking constraint) exposes a code path where --stage
    # finalize is invoked independently after gates.json already shows a
    # mechanical failure, and the ORIGINAL run_finalize (mirroring F6's/F7's
    # single-invocation discipline) has no branch for it. This leg's own
    # Part 0 cites that report directly and builds the branch in from the
    # start rather than discovering the gap live. This branch does not alter
    # GAP, G5_EQUIVALENCE_DELTA, kappa, block counts, or any other design/
    # scientific parameter -- it only prevents adjudication from silently
    # proceeding past a gate whose established consequence is to void the
    # leg. Unlike M4-F8's own report, this leg's own task text carries no
    # conflicting "which gates void" summary parenthetical, so there is no
    # analogous ambiguity about WHETHER G5 voids -- it does, unconditionally,
    # matching F6's/F7's/F8's own unbroken discipline. The adjudication that
    # WOULD have resulted is still computed and disclosed below (using
    # f8().adjudicate, the unmodified, literal same function), purely for
    # this line's own established full-disclosure convention, NOT because of
    # any ambiguity about whether it is adopted -- it is not.
    if not gates.get("mechanical_gates_pass", False):
        failed_gates = [g for g in ("G1", "G2", "G3", "G4", "G5") if not gates.get(g, {}).get("pass", False)]
        informational_adjudication = f8().adjudicate(g0, g6, summaries)
        adjudication = {
            "verdict": "VOID_MECHANICAL_GATE_FAILURE",
            "failed_gates": failed_gates,
            "g5_detail": gates["G5"],
            "g0_power_statement": g0,
            "g6_channel_liveness_statement": g6,
            "informational_adjudication_on_collected_data_NOT_ADOPTED": informational_adjudication,
            "note": (
                "A G1-G5 gate failure VOIDS the leg outright, per this whole line's unbroken discipline "
                "(F6's own Part 0.7 rule for G5, unchanged in FORM -- now equivalence rather than "
                "nil-significance -- but unchanged in CONSEQUENCE). Leans (a)/(b)/(c) and the pivot are NOT "
                "adjudicated. G5_EQUIVALENCE_DELTA and the GAP=40 design constant were NOT altered or "
                "re-run after observing this result; per the registration's own explicit instruction, this "
                "is written as observed. The informational_adjudication field above is reported for this "
                "line's own full-disclosure convention only -- it is NOT an adopted finding, and (unlike "
                "M4-F8's own report) there is no genuine ambiguity being resolved here: this leg's own task "
                "text carries no conflicting scope parenthetical, so G5 voids unconditionally."
            ),
        }
        all_rows = []
        combined = dict(summaries)
        combined[ANCHOR_CELL] = anchor_summary
        combined[CONSTRUCTION_CHECK_CELL] = construction_summary
        for cell, s in combined.items():
            if cell in summaries:
                role = "adjudicated_common_budget_x16_fresh_seed"
            elif cell == ANCHOR_CELL:
                role = "gate_anchor_raw_budget_x16_original_seed"
            else:
                role = "gate_only_construction_check_mult1_original_seed"
            row = {k: v for k, v in s.items() if k not in (
                "world_seeds", "world_values", "truth_exact_world_values",
                "truth_long_world_values", "g5_world_values"
            )}
            row["role"] = role
            all_rows.append(row)
        pd.DataFrame(all_rows).to_csv(OUT / "cells.csv", index=False)

        decision = {
            "experiment": "M4-F9_occasion_axis_repaired",
            "banner": BANNER,
            "tier": "EXPLORATORY",
            "registered_spec": "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md#M4-F9-registration",
            "part0_registered_in": "reports/SUICA_M4_F9_OCCASION_AXIS_REPAIRED_REPORT.md Part 0 (before run)",
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "master_seed": MASTER_SEED,
            "master_seed_offset": MASTER_SEED_OFFSET,
            "fresh_master_seed": FRESH_MASTER_SEED,
            "worlds_per_cell": WORLDS_PER_CELL,
            "draws_per_world": DRAWS,
            "gap": f6().GAP,
            "m_common": f6().M_COMMON,
            "author_mult": AUTHOR_MULT,
            "kappa": KAPPA,
            "g5_equivalence_delta": G5_EQUIVALENCE_DELTA,
            "base_cell": f"{ANCHOR_CELL} (author_mult=16, event_mult=1, ORIGINAL seed lineage)",
            "gates": {k: (v["pass"] if isinstance(v, dict) and "pass" in v else v) for k, v in gates.items()},
            "gates_all_pass": gates["all_pass"],
            "gates_mechanical_pass": gates["mechanical_gates_pass"],
            "adjudication": adjudication,
            "label_free": True,
            "claim_boundary": (
                "VOID: a mechanical gate (G5, decorrelation, repaired equivalence form) failed at authors "
                "x16/kappa=0.5 on this leg's own fresh seeds, so no scientific claim about the occasion axis "
                "is licensed by this leg's adjudicated sweep. See adjudication.note."
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
            "at block_count=1 and/or block_count=8, on this leg's own fresh seeds. The leg is VACUOUS -- "
            "leans (a)/(b)/(c) and the pivot are NOT adjudicated and NO null is reported, regardless of "
            "G0's own determination.",
        }
    elif not g0["pass"]:
        adjudication = {
            "verdict": "UNDERPOWERED_NO_ADJUDICATION",
            "g0_power_statement": g0,
            "g6_channel_liveness_statement": g6,
            "note": "Per the registration's G0 POWER gate: G6 confirms the channel is causally live, but "
            "this leg's realized paired CI half-width (on its own fresh seeds) exceeds the .0407 bar, so it "
            "is UNDERPOWERED. Leans (a)/(b)/(c) and the pivot are NOT adjudicated and NO null is reported -- "
            "this is the registered, correct response to this outcome, not a fallback.",
        }
    else:
        adjudication = f8().adjudicate(g0, g6, summaries)

    all_rows = []
    combined = dict(summaries)
    combined[ANCHOR_CELL] = anchor_summary
    combined[CONSTRUCTION_CHECK_CELL] = construction_summary
    for cell, s in combined.items():
        if cell in summaries:
            role = "adjudicated_common_budget_x16_fresh_seed"
        elif cell == ANCHOR_CELL:
            role = "gate_anchor_raw_budget_x16_original_seed"
        else:
            role = "gate_only_construction_check_mult1_original_seed"
        row = {k: v for k, v in s.items() if k not in (
            "world_seeds", "world_values", "truth_exact_world_values",
            "truth_long_world_values", "g5_world_values"
        )}
        row["role"] = role
        all_rows.append(row)
    pd.DataFrame(all_rows).to_csv(OUT / "cells.csv", index=False)

    decision = {
        "experiment": "M4-F9_occasion_axis_repaired",
        "banner": BANNER,
        "tier": "EXPLORATORY",
        "registered_spec": "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md#M4-F9-registration",
        "part0_registered_in": "reports/SUICA_M4_F9_OCCASION_AXIS_REPAIRED_REPORT.md Part 0 (before run)",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "master_seed_offset": MASTER_SEED_OFFSET,
        "fresh_master_seed": FRESH_MASTER_SEED,
        "worlds_per_cell": WORLDS_PER_CELL,
        "draws_per_world": DRAWS,
        "gap": f6().GAP,
        "m_common": f6().M_COMMON,
        "author_mult": AUTHOR_MULT,
        "kappa": KAPPA,
        "g5_equivalence_delta": G5_EQUIVALENCE_DELTA,
        "base_cell": f"{ANCHOR_CELL} (author_mult=16, event_mult=1, ORIGINAL seed lineage)",
        "gates": {k: (v["pass"] if isinstance(v, dict) and "pass" in v else v) for k, v in gates.items()},
        "gates_all_pass": gates["all_pass"],
        "gates_mechanical_pass": gates["mechanical_gates_pass"],
        "adjudication": adjudication,
        "label_free": True,
        "claim_boundary": (
            "Synthetic occasion-spread finding in a world calibrated to the opened PANDORA D-panel "
            "regime, repeated at authors x16 (M4-F7's own scale) and kappa=0.5 (the one value where the "
            "manipulation is BOTH causally live and adequately powered), on FRESH world seeds (a new sample, "
            "not a re-adjudication of M4-F8's own observed draws) and G5's repaired equivalence form; "
            "licenses a finding about whether spreading observation across widely-separated occasion blocks "
            "certifies a trait-like object under this synthetic instrument, AT THIS SCALE AND KAPPA. No "
            "claim about the real relation field's content, personality, emotion, diagnosis, or any "
            "individual."
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
