#!/usr/bin/env python3
"""M4-F7 -- the occasion axis, properly powered (authors x16).

Registered spec: docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md section
"M4-F7 registration (2026-08-03, BEFORE run) -- the occasion axis, properly
powered", together with the preceding "M4-F6 planner adjudication note" (why
M4-F6's pivot consequence was SUSPENDED: it swept occasions at authors x1,
where long-window truth recovery sits at its own noise floor, ~.02-.05 with
SEs ~.010, and its own paired CI half-width was ~.045 -- a null at the
target's noise floor, not evidence against the occasion axis). Part 0
register-notes (every implementation choice this registration left open,
written BEFORE any compute) are in
reports/SUICA_M4_F7_OCCASION_AXIS_POWERED_REPORT.md Part 0.

THIS LEG CHANGES ONLY THE SCALE relative to M4-F6: authors x16 (not x1),
kappa=1.0 ONLY (the registration's explicit scope restriction -- "M4-F6
established the kappa=0.5 behaviour is qualitatively the same and it is not
worth the compute"). Everything else -- the block+gap generator, the
common-budget construction, the two truth variants, the decorrelation check
-- is REUSED VERBATIM from M4-F6, by direct call into its own module (loaded
as f6(), exactly the way F6 itself loaded f1()...f5()). NEW: the G0 POWER
gate (the standing rule the M4-F6 planner note added after that leg's own
registration omitted a power statement), and a second, small, GATE-ONLY
"construction check" cell (Part 0.2) that recomputes M4-F6's OWN
b1_shared_k10 cell (author_mult=1) through THIS leg's generalized
(author_mult-parametrized) orchestration, to verify the generalization did
not silently diverge from F6's own tested code.

Reuse boundary (task's explicit instruction: "Reuse its generate_world_spread
/ run_spread_sweep_world machinery, its two-tier B=1 resolution, its
common-budget construction, and its G5 decorrelation check VERBATIM. You are
changing the SCALE, nothing else."):
  - From scripts/run_suica_m4_f1_panel_sizing.py (loaded as f1()): load_spec,
    _directions, e1(), build_layout, featurize_panel, half_indices, knob_tag
    -- called unchanged.
  - From scripts/run_suica_m4_f2_composition.py (loaded as f2()): run_gate_g1
    -- called unchanged (direct G1 reuse, as every leg in this line does).
  - From scripts/run_suica_m4_f3_composition_scaling.py (loaded as f3()):
    run_gate_g3 -- called unchanged.
  - From scripts/run_suica_m4_f4_author_axis.py (loaded as f4()):
    build_live_tasks -- called unchanged, to build the byte-identical RAW
    authors-x16 task (the G2(b) gate anchor), exactly as M4-F6 did at mult=1.
  - From scripts/run_suica_m4_f5_gauge_validity.py (loaded as f5()):
    run_truth_sweep_world (called DIRECTLY, unchanged, for the RAW
    authors-x16 gate-anchor cell); field_from_vectors,
    generate_truth_vectors_long, T_LARGE_PRIMARY, G4_TOLERANCE.
  - From scripts/run_suica_m4_f6_occasion_spread.py (loaded as f6()):
    generate_world_spread, generate_truth_vectors_exact_spread,
    g5_world_correlation, spread_world_seed_for, GAP, M_COMMON, _paired_ci --
    ALL called DIRECTLY, UNCHANGED. This is the leg's central reuse
    commitment: the occasion-spread MECHANISM itself is not re-derived at
    all, only re-scaled.

NEW in this script (nothing above is reimplemented):
  - common_layout_scaled(reference, author_mult): F6's own common_layout
    (Part 0.4 of its report), generalized to accept author_mult as a
    parameter instead of hardcoding 1 -- the ONE necessary change to let the
    common-budget construction run at a different author scale (Part 0.2).
  - _prepare_spread_world / run_spread_sweep_world: a disclosed structural
    near-duplicate of f6()'s own same-named functions (exactly as F6 itself
    was a disclosed near-duplicate of f5().run_truth_sweep_world) --
    necessary ONLY because the world-building step now calls
    common_layout_scaled(reference, task["author_mult"]) instead of F6's
    hardcoded common_layout(reference); every downstream primitive is called
    exactly as F6 itself calls it.
  - The G0 POWER gate (wholly new, the standing rule from the M4-F6 planner
    note).
  - The construction-check cell/task builder and gate G2(a) (Part 0.2).
  - cell_summary / gates G1 (thin direct-call wrapper) / G2 / G3 (thin
    direct-call wrapper) / G4 / G5, scoped to THIS script's own OUT
    directory (each leg's cell_summary/gates has always been OUT-scoped,
    even when the underlying rule is reused verbatim -- see F5's/F6's own
    cell_summary, each a disclosed near-duplicate of the previous one for
    exactly this reason).
  - The adjudication code (leans a/b/c with the registered lean-(b)
    inapplicable-on-non-positive-gain rule, the pivot, and the G0-gated
    finalize branch that adjudicates nothing when underpowered).

Stages (resumable, artifacts under results/m4_f7_occasion_axis_powered/):
  --stage anchor              the RAW authors_x16_shared_k10 gate-anchor cell
                               (G2(b)'s comparison target; f5().run_truth_
                               sweep_world, unchanged, on f4()'s own
                               byte-identical mult=16 task)
  --stage construction-check  the mult=1/block_count=1/kappa=1.0 GATE-ONLY
                               cell that must reproduce M4-F6's own persisted
                               b1_shared_k10 (G2(a)'s comparison target)
  --stage sweep                the 4 adjudicated b{1,2,4,8}_x16_k10 cells
                               (COMMON M_COMMON=8 budget, kappa=1.0 only;
                               --block-counts selects a subset for chunked
                               execution)
  --stage gates                G0-G5, writes gates.json; STOPS on G1/G2/G3/
                               G4/G5 failure (matching M4-F6's own G5
                               discipline); does NOT stop on G0 failure alone
                               (Part 0.8: G0 failing is a registered,
                               anticipated, VALID scientific outcome this leg
                               must still report in full, not a mechanical
                               defect)
  --stage finalize             G0-gated adjudication + decision.json +
                               cells.csv
  --stage all                  anchor + construction-check + sweep + gates +
                               finalize
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
from types import SimpleNamespace
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
MIN_RETAINED_EVENTS = 8  # the deployed gauge's own split-half retention floor.

AUTHOR_MULT = 16  # the ONE scale change from M4-F6 (which used mult=1/base1x).
KAPPA_TAG = "k10"
KAPPA = 1.0  # kappa=1.0 ONLY -- the registration's explicit scope restriction.
DESIGN = "shared"
BLOCK_COUNTS = [1, 2, 4, 8]

G0_HALF_WIDTH_BAR = 0.066  # registered: half the target's measured level (.1322/2=.0661).

OUT = ROOT / "results" / "m4_f7_occasion_axis_powered"
F1_OUT = ROOT / "results" / "m4_f1_panel_sizing"
F5_OUT = ROOT / "results" / "m4_f5_gauge_validity"
F6_OUT = ROOT / "results" / "m4_f6_occasion_spread"
REF_PATH = F1_OUT / "realtext_panel_reference.json"
F1_CELLS_CSV = F1_OUT / "cells.csv"
F1_CALIBRATION = F1_OUT / "calibration_record.json"
F5_CELLS_CSV = F5_OUT / "cells.csv"
F6_CELLS_CSV = F6_OUT / "cells.csv"

CONSTRUCTION_CHECK_CELL = "construction_check_mult1_b1_k10"
ANCHOR_CELL = "authors_x16_shared_k10"


def _load_script(name: str) -> Any:
    """Copied verbatim from M4-F3's/M4-F4's/M4-F5's/M4-F6's own Part-0.11-style
    fix (register sys.modules[mod_name]=module BEFORE exec_module, so a nested
    ProcessPoolExecutor.map against a function defined in a dynamically-loaded
    module can pickle that function by reference). Zero edits to
    run_suica_m4_f1_panel_sizing.py, run_suica_m4_f2_composition.py,
    run_suica_m4_f3_composition_scaling.py, run_suica_m4_f4_author_axis.py,
    run_suica_m4_f5_gauge_validity.py, or run_suica_m4_f6_occasion_spread.py
    themselves."""
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


# ---------------------------------------------------------------------------
# Part 0.2 -- the ONE generalization: common_layout, parametrized by author_mult.

def common_layout_scaled(
    reference: dict[str, Any], author_mult: int
) -> tuple[list[str], list[str], list[str], list[int], list[int]]:
    """F6's own common_layout (Part 0.4 of its report), generalized to accept
    author_mult instead of hardcoding 1. Every author's raw event count is
    still replaced by the SAME constant M_COMMON=f6().M_COMMON -- verified
    (not merely assumed) that M_COMMON does not exceed the panel's own
    minimum raw count AT THIS author_mult (replication does not change any
    individual author's own raw count, so this bound is scale-invariant by
    construction, but it is checked against the actual layout produced at
    this author_mult, not assumed from the mult=1 case)."""
    author_ids, contexts, splits, raw_counts = f1().build_layout(reference, author_mult, 1)
    m_common = f6().M_COMMON
    if min(raw_counts) < m_common:
        raise AssertionError(
            f"M_COMMON={m_common} exceeds the panel's own minimum raw count "
            f"{min(raw_counts)} at author_mult={author_mult}"
        )
    common_counts = [m_common] * len(raw_counts)
    return author_ids, contexts, splits, common_counts, raw_counts


# ---------------------------------------------------------------------------
# The per-world engine: a disclosed structural near-duplicate of
# f6().run_spread_sweep_world (necessary ONLY because the world-building step
# calls common_layout_scaled(reference, task["author_mult"]) instead of F6's
# own hardcoded common_layout(reference)); every downstream primitive is
# called EXACTLY as F6 itself calls it, including F6's own
# generate_world_spread / generate_truth_vectors_exact_spread /
# g5_world_correlation / spread_world_seed_for, all via direct f6() calls.

def _prepare_spread_world(task: dict[str, Any]) -> dict[str, Any]:
    spec = f1().load_spec()
    directions = f1()._directions(spec)
    module = f1().e1()
    reference = json.loads(Path(task["ref_path"]).read_text(encoding="utf-8"))
    author_ids, contexts, splits, common_counts, _raw = common_layout_scaled(
        reference, task["author_mult"]
    )
    corpus = f"{task['corpus_prefix']}{task['seed_key']}-w{task['world']}"
    world_seed = f6().spread_world_seed_for(task["seed_key"], task["world"], task["knob_tag"])
    vectors_list, diag = f6().generate_world_spread(
        common_counts, contexts, task["knobs"], task["kappa"], task["block_count"], task["gap"], world_seed
    )

    raw_m, raw_k = f1().featurize_panel(
        vectors_list, author_ids, corpus=corpus, spec=spec, directions=directions
    )
    metadata = pd.DataFrame(
        {"author_id": author_ids, "context": contexts, "split": splits, "event_count": common_counts}
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
    weights = {c: float(ctx_counts.get(c, 0) / max(1, int(ctx_counts.sum()))) for c in resolved}

    return {
        "spec": spec, "directions": directions, "module": module,
        "author_ids": author_ids, "contexts": contexts, "counts": common_counts,
        "corpus": corpus, "world_seed": world_seed, "vectors_list": vectors_list, "diag": diag,
        "raw_m": raw_m, "raw_k": raw_k, "calibration": calibration,
        "resolved": resolved, "retained_idx": retained_idx, "retained_ids": retained_ids,
        "retained_ctx": retained_ctx, "weights": weights,
    }


def run_spread_sweep_world(task: dict[str, Any]) -> dict[str, Any]:
    started = time.time()
    w = _prepare_spread_world(task)
    spec, directions, module = w["spec"], w["directions"], w["module"]
    author_ids, counts, corpus = w["author_ids"], w["counts"], w["corpus"]
    vectors_list, calibration = w["vectors_list"], w["calibration"]
    resolved, retained_idx = w["resolved"], w["retained_idx"]
    retained_ids, retained_ctx, weights = w["retained_ids"], w["retained_ctx"], w["weights"]
    diag = w["diag"]

    # ---- (A) split-half agreement, IDENTICAL procedure to f6()/f5()/f3(). ----
    draw_values: list[float] = []
    for draw in range(int(task["draws"])):
        halves_a: list[np.ndarray] = []
        halves_b: list[np.ndarray] = []
        for position, index in enumerate(retained_idx):
            b = counts[index]
            first, second = f1().half_indices(corpus, retained_ids[position], task["budget_label"], draw, b)
            vectors = vectors_list[index]
            halves_a.append(vectors[first])
            halves_b.append(vectors[second])
        fields = []
        for half in (halves_a, halves_b):
            m_half, k_half = f1().featurize_panel(half, retained_ids, corpus=corpus, spec=spec, directions=directions)
            half_panel = SimpleNamespace(raw={"M": m_half, "K": k_half})
            projected = module.project_soft(half_panel, np.ones(len(retained_idx), dtype=bool), calibration)
            fields.append(module.deployed_soft_field(projected, retained_ctx, resolved))
        draw_values.append(module.field_agreement(fields[0], fields[1], weights))
    agreement_mean = float(np.mean(draw_values))
    agreement_sd = float(np.std(draw_values, ddof=1))

    # ---- (B) finite-sample ESTIMATE field: SAME path, fed the full retained vectors. ----
    retained_vectors = [vectors_list[i] for i in retained_idx]
    field_est_full = f5().field_from_vectors(
        retained_vectors, retained_ids, retained_ctx, resolved, calibration, spec, directions, corpus, module
    )
    del retained_vectors, vectors_list, halves_a, halves_b

    # ---- G4 byproduct: an INDEPENDENT route to the identical finite-sample field. ----
    final_mask = np.zeros(len(author_ids), dtype=bool)
    final_mask[retained_idx] = True
    projected_via_mask = module.project_soft(SimpleNamespace(raw={"M": w["raw_m"], "K": w["raw_k"]}), final_mask, calibration)
    field_est_full_via_mask = module.deployed_soft_field(projected_via_mask, retained_ctx, resolved)
    g4_diffs = [float(np.max(np.abs(field_est_full[c] - field_est_full_via_mask[c]))) for c in field_est_full]
    g4_max_diff = float(max(g4_diffs)) if g4_diffs else 0.0
    w["raw_m"] = w["raw_k"] = None
    del projected_via_mask, field_est_full_via_mask
    gc.collect()

    # ---- (C) Truth Variant A (exact, noise-free, spread-aware; F6's own generator). ----
    truth_vectors_exact = f6().generate_truth_vectors_exact_spread(
        counts, w["contexts"], task["knobs"], task["kappa"], task["block_count"], task["gap"],
        w["world_seed"], retained_idx,
    )
    field_true_exact = f5().field_from_vectors(
        truth_vectors_exact, retained_ids, retained_ctx, resolved, calibration, spec, directions, corpus, module
    )
    truth_recovery_exact = module.field_agreement(field_est_full, field_true_exact, weights)
    del truth_vectors_exact, field_true_exact
    gc.collect()

    # ---- (D) Truth Variant B (large-sample asymptotic, UNCHANGED -- F5's own generator). ----
    truth_vectors_long = f5().generate_truth_vectors_long(
        counts, task["knobs"], task["kappa"], w["world_seed"], retained_idx, retained_ctx,
        t_large=f5().T_LARGE_PRIMARY,
    )
    field_true_long = f5().field_from_vectors(
        truth_vectors_long, retained_ids, retained_ctx, resolved, calibration, spec, directions, corpus, module
    )
    truth_recovery_long = module.field_agreement(field_est_full, field_true_long, weights)
    del truth_vectors_long, field_true_long
    gc.collect()

    # ---- (E) G5: cross-block boundary decorrelation of the RAW (pre-blend) AR(1) state. ----
    g5 = f6().g5_world_correlation(diag["x_before"], diag["x_after"])

    return {
        "banner": BANNER,
        "cell": task["cell"],
        "seed_key": task["seed_key"],
        "author_mult": int(task["author_mult"]),
        "block_count": int(task["block_count"]),
        "gap": int(task["gap"]),
        "design": DESIGN,
        "world": int(task["world"]),
        "kappa": float(task["kappa"]),
        "n_authors_total": int(len(author_ids)),
        "n_events_total": int(sum(counts)),
        "n_retained": int(len(retained_idx)),
        "n_resolved_contexts": int(len(resolved)),
        "d0_eff_rank_M": float(calibration["M"].effective_rank),
        "d0_eff_rank_K": float(calibration["K"].effective_rank),
        "draws": int(task["draws"]),
        "agreement_mean": agreement_mean,
        "agreement_sd": agreement_sd,
        "draw_values": [float(v) for v in draw_values],
        "truth_recovery_exact": float(truth_recovery_exact),
        "truth_recovery_long": float(truth_recovery_long),
        "t_large": int(f5().T_LARGE_PRIMARY),
        "g4_max_diff": g4_max_diff,
        "g5_n_pairs": g5["n_pairs"],
        "g5_correlation": g5["correlation"],
        "t_span": diag["t_span"],
        "block_size": diag["block_size"],
        "world_seed": int(w["world_seed"]),
        "seconds": float(time.time() - started),
    }


# ---------------------------------------------------------------------------
# Cell/task builders.

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
                    "ref_path": str(REF_PATH), "budget_label": "f7.0", "corpus_prefix": "m4f7-",
                }
            )
    return tasks


def build_construction_check_task(knobs: dict[str, Any], knob_tag: str, draws: int) -> list[dict[str, Any]]:
    """G2(a)'s task: mult=1/block_count=1/kappa=1.0, using F6's OWN
    seed_key/corpus-prefix/budget_label ('b1_k10' / 'm4f6-' / 'f6.0' -- EXACTLY
    f6().build_spread_tasks's own values at block_count=1, kappa_tag='k10') so
    this reproduces F6's persisted b1_shared_k10 cell bit-for-bit through THIS
    leg's generalized (author_mult-parametrized) orchestration -- a
    code-correctness check, not a scientific/adjudicated cell."""
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
    """The RAW authors_x16_shared_k10 gate-anchor task -- BYTE-IDENTICAL to
    M4-F5's/M4-F4's own build_live_tasks(mult=16, kappa_tags={'k10'})."""
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
    f5().run_truth_sweep_world on f4()'s own byte-identical mult=16 task --
    literally M4-F5's own computation, repeated (M4-F5 already persisted
    this exact cell; this recomputes it fresh under THIS leg's own artifact
    tree so G2(b) has a freshly-computed object to diff, mirroring M4-F6's
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
        rows = list(pool.map(run_spread_sweep_world, tasks))
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
            rows = list(pool.map(run_spread_sweep_world, cell_tasks))
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
# Gates.

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
    """TWO disclosed sub-checks, BOTH required (Part 0.2/0.8 of the report):
    (a) CONSTRUCTION -- the construction-check cell (mult=1, block_count=1,
    kappa=1.0, using F6's own seed_key/corpus-prefix/budget_label) reproduces
    M4-F6's own persisted b1_shared_k10 cell to <=1e-12 -- validates THIS
    leg's generalized (author_mult-parametrized) orchestration against F6's
    own tested numbers at the one scale where a ground truth already exists.
    (b) ANCHOR -- the RAW authors_x16_shared_k10 gate-anchor cell (a direct,
    unchanged call to f5().run_truth_sweep_world on f4()'s own byte-identical
    mult=16 task) reproduces M4-F5's persisted authors_x16_shared_k10 to
    <=1e-12 -- mirrors M4-F6's own G2 exactly, at the new scale."""
    construction_path = OUT / f"cell_{CONSTRUCTION_CHECK_CELL}.csv"
    if not construction_path.exists():
        raise AssertionError(f"G2(a) requires {construction_path} to exist; run --stage construction-check first.")
    got_construction = cell_summary(CONSTRUCTION_CHECK_CELL)
    target_construction = _read_f6_persisted_row("b1_shared_k10")
    diffs_a, pass_a = _diff_row(got_construction, target_construction)

    anchor_path = OUT / f"cell_{ANCHOR_CELL}.csv"
    if not anchor_path.exists():
        raise AssertionError(f"G2(b) requires {anchor_path} to exist; run --stage anchor first.")
    got_anchor = cell_summary(ANCHOR_CELL)
    target_anchor = _read_f5_persisted_row(ANCHOR_CELL)
    diffs_b, pass_b = _diff_row(got_anchor, target_anchor)

    return {
        "gate": "G2",
        "description": "TWO sub-checks, both required (Part 0.2/0.8): (a) CONSTRUCTION -- the "
        "mult=1/block_count=1/kappa=1.0 cell, computed through THIS leg's generalized orchestration "
        "using F6's own seed_key/corpus-prefix/budget_label, reproduces M4-F6's persisted b1_shared_k10 "
        "to <=1e-12; (b) ANCHOR -- the RAW authors_x16_shared_k10 cell (f5().run_truth_sweep_world, "
        "unchanged, on f4()'s own byte-identical mult=16 task) reproduces M4-F5's persisted "
        "authors_x16_shared_k10 to <=1e-12.",
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
    """Truth-path invariance, as M4-F5/M4-F6: two independent routes to the
    identical finite-sample field agree to <=G4_TOLERANCE, for every world of
    every cell (construction-check + anchor + 4 adjudicated x16 cells)."""
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
        "field agree to <=G4_TOLERANCE, for every world of every cell (matching M4-F5's/M4-F6's own check)",
        "tolerance": f5().G4_TOLERANCE,
        "rows": rows,
        "pass": bool(all_pass),
    }


def run_gate_g5(spread_cells: list[str]) -> dict[str, Any]:
    """Decorrelation check: F6's OWN pre-registered aggregation rule (Part 0.7
    of the M4-F6 report), reused VERBATIM: |t|<2.0 at EVERY block_count>=2
    cell. Only 3 cells here (b2/b4/b8 at x16, kappa=1.0) -- half of F6's own
    6, since this leg drops kappa=0.5 entirely per the registration."""
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
        "kappa=1.0 only.",
        "rows": rows,
        "pooled_context": pooled,
        "pass": bool(all_pass),
    }


def run_gate_g0(target_cell: str = ANCHOR_CELL) -> dict[str, Any]:
    """POWER (the standing rule the M4-F6 planner note added, Part 0.1 of the
    report): report the target's measured level at this scale from M4-F5's
    OWN persisted authors_x16_shared_k10 cell (read verbatim, never
    retyped), and the minimum detectable paired difference THIS design's
    REALIZED SEs actually afford (the b8_x16-b1_x16 paired-by-world CI
    half-width on truth_recovery_long, kappa=1.0, using F6's own _paired_ci
    construction verbatim). FAILS (declared UNDERPOWERED) if that half-width
    exceeds G0_HALF_WIDTH_BAR=.066. Part 0.8 of the report: unlike G1-G5,
    G0 failing does NOT raise/void the run here -- it is a registered,
    anticipated, valid scientific outcome that run_finalize must still
    report in full (adjudicating nothing, per the registration's own text),
    not a mechanical defect that voids the leg."""
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
        "description": "POWER (M4-F6 planner-note standing rule): report the target's measured level at "
        "this scale from M4-F5's own persisted authors_x16_shared_k10 cell, and the minimum detectable "
        "paired difference (B8-B1 truth_recovery_long paired-by-world 95% CI half-width) this design's "
        "REALIZED SEs actually afford. FAILS (UNDERPOWERED) if that half-width exceeds .066 (half the "
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


def run_gates(knobs: dict[str, Any], knob_tag: str, workers: int) -> dict[str, Any]:
    spread_cells = [cell_name_spread_x16(b) for b in BLOCK_COUNTS]
    g1 = run_gate_g1(knobs, knob_tag, workers)
    g3 = run_gate_g3()
    g2 = run_gate_g2()
    all_computed_cells = [CONSTRUCTION_CHECK_CELL, ANCHOR_CELL] + spread_cells
    g4 = run_gate_g4(all_computed_cells)
    g5 = run_gate_g5(spread_cells)
    g0 = run_gate_g0()
    mechanical_pass = bool(g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"] and g5["pass"])
    gates = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "knobs": knobs,
        "knob_tag": knob_tag,
        "gap": f6().GAP,
        "m_common": f6().M_COMMON,
        "author_mult": AUTHOR_MULT,
        "G0": g0, "G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5,
        "mechanical_gates_pass": mechanical_pass,
        "all_pass": bool(mechanical_pass and g0["pass"]),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: v["pass"] for k, v in gates.items() if isinstance(v, dict) and "pass" in v}, indent=2))
    if not g5["pass"]:
        raise AssertionError(
            "G5 (decorrelation check) FAILED -- blocks remain correlated at the chosen gap. Per the "
            "registration (reusing M4-F6's own discipline verbatim) this VOIDS the leg. See "
            "results/m4_f7_occasion_axis_powered/gates.json. Do NOT increase the gap and re-run silently; "
            "write the void outcome."
        )
    if not mechanical_pass:
        raise AssertionError(
            "Mechanical gate(s) (G1/G2/G3/G4) failed; see results/m4_f7_occasion_axis_powered/gates.json."
        )
    if not g0["pass"]:
        print(
            "[G0] UNDERPOWERED: half-width "
            f"{g0['minimum_detectable_paired_difference_half_width']:.6f} > bar {G0_HALF_WIDTH_BAR}. "
            "Per the registration, run_finalize will adjudicate NOTHING and record this determination "
            "plainly -- this is NOT a failure that voids the leg's other gates."
        )
    return gates


# ---------------------------------------------------------------------------
# Adjudication -- exactly the registered leans/pivot, no more. Only called by
# run_finalize when G0 PASSES.

def adjudicate(g0: dict[str, Any], summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    b1 = summaries[cell_name_spread_x16(1)]
    b8 = summaries[cell_name_spread_x16(8)]

    diff_long = np.asarray(b8["truth_long_world_values"], dtype=float) - np.asarray(b1["truth_long_world_values"], dtype=float)
    diff_exact = np.asarray(b8["truth_exact_world_values"], dtype=float) - np.asarray(b1["truth_exact_world_values"], dtype=float)
    ci_long = f6()._paired_ci(diff_long)
    ci_exact = f6()._paired_ci(diff_exact)

    lean_a_hold = bool(ci_long["ci_excludes_zero_positive"])
    lean_a = {
        "lean": "a", "rule": "TRAIT AXIS EXISTS: long-window truth recovery (Variant B) RISES with B, "
        "paired-by-world B8-B1 CI excluding 0, kappa=1.0",
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

    kappa10_cells = [summaries[cell_name_spread_x16(b)] for b in BLOCK_COUNTS]
    agreements = {c["block_count"]: c["agreement_mean"] for c in kappa10_cells}
    ref = agreements[1]
    band = 0.20 * abs(ref)
    per_b_within = {b: bool(abs(agreements[b] - ref) <= band) for b in BLOCK_COUNTS}
    lean_c_hold = bool(all(per_b_within.values()))
    max_val, min_val = max(agreements.values()), min(agreements.values())
    reading2_hold = bool((max_val - min_val) <= band)
    lean_c = {
        "lean": "c", "rule": "GAUGE BLINDNESS REPLICATES: split-half agreement remains B-invariant within "
        "+/-20% of its B=1 value at authors x16 (Reading 1, adopted -- per-point band, matching M4-F6's "
        "own adopted reading); Reading 2 (stricter, max-to-min<=20% of B=1) computed alongside per this "
        "line's disclosure convention",
        "agreement_by_block_count": agreements,
        "b1_reference": ref,
        "band_abs": band,
        "max_minus_min": float(max_val - min_val),
        "per_b_within_band": per_b_within,
        "reading2_max_minus_min_le_band": reading2_hold,
        "verdict": "HOLD" if lean_c_hold else "MISS",
    }

    pivot_condition_no_rise = bool(ci_long["ci_includes_zero"] or not ci_long["ci_excludes_zero_positive"])
    pivot_fires = bool(g0["pass"] and pivot_condition_no_rise)
    pivot = {
        "registered_rule": "adequately powered (G0 PASS) AND long-window truth recovery does not rise "
        "with B (paired CI includes 0) -> the closure is EARNED",
        "adequately_powered": g0["pass"],
        "no_rise_condition": pivot_condition_no_rise,
        "paired_diff_B8_minus_B1_ci95": [ci_long["ci95_low"], ci_long["ci95_high"]],
        "fires": pivot_fires,
    }

    if pivot_fires:
        verdict = "CLOSURE_EARNED_TRAIT_LEVEL_UNCERTIFIABLE_ON_ALL_THREE_PANEL_AXES"
    elif lean_a_hold and (lean_b_verdict in ("HOLD", "INAPPLICABLE")) and lean_c_hold:
        verdict = "OCCASION_AXIS_IS_A_LEVER_AT_AUTHORS_X16_CLOSURE_NOT_EARNED"
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
    if not g0["pass"]:
        adjudication = {
            "verdict": "UNDERPOWERED_NO_ADJUDICATION",
            "g0_power_statement": g0,
            "note": "Per the registration's G0 POWER gate: this leg's realized paired CI half-width "
            "exceeds the .066 bar, so it is UNDERPOWERED. Leans (a)/(b)/(c) and the pivot are NOT "
            "adjudicated and NO null is reported -- this is the registered, correct response to this "
            "outcome, not a fallback.",
        }
    else:
        adjudication = adjudicate(g0, summaries)

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
        "experiment": "M4-F7_occasion_axis_powered",
        "banner": BANNER,
        "tier": "EXPLORATORY",
        "registered_spec": "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md#M4-F7-registration",
        "part0_registered_in": "reports/SUICA_M4_F7_OCCASION_AXIS_POWERED_REPORT.md Part 0 (before run)",
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
            "regime, repeated at authors x16 where the long-window target is measurably non-zero; "
            "licenses a finding about whether spreading observation across widely-separated occasion "
            "blocks certifies a trait-like object under this synthetic instrument, AT THIS SCALE. No "
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
        "--stage", choices=["anchor", "construction-check", "sweep", "gates", "finalize", "all"], default="all"
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
