#!/usr/bin/env python3
"""M4-F5 -- gauge validity: does split-half agreement CERTIFY the field?

Registered spec: docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md section
"M4-F5 registration (2026-08-03, BEFORE run) -- is the certificate valid?"
together with the preceding "M4-F4 planner adjudication note" (source of the
registered secondary offset-corrected refit and its pre-recorded expectation).
Part 0 register-notes (every implementation choice the registration left
open -- the truth-path operationalization above all -- written BEFORE any
compute) are in reports/SUICA_M4_F5_GAUGE_VALIDITY_REPORT.md Part 0.

Four legs of this line (M4-F1..M4-F4) optimized ONE statistic: the deployed
field's internal split-half agreement. This leg audits whether that
statistic certifies anything, by computing, at EVERY one of M4-F4's own
persisted cells, a SECOND, TRUTH-REFERENCED quantity: the same
field-agreement functional evaluated between the finite-panel ESTIMATED
field and the world's TRUE (noise-free) field, via the IDENTICAL deployed
featurize -> project -> field path, differing ONLY in the input.

Reuse boundary (task's explicit instruction: "reuse its world, sweep, gauge,
and gate helpers; do not reimplement them"):
  - From scripts/run_suica_m4_f1_panel_sizing.py (loaded as f1()):
    load_spec, _directions, e1(), build_layout, featurize_panel,
    half_indices, knob_tag, fit_axis, bootstrap_axis, _log_odds -- all
    called unchanged.
  - From scripts/run_suica_m4_f2_composition.py (loaded as f2()):
    occasion_labels, shock_vector, generate_world_composed, run_gate_g1 --
    all called unchanged.
  - From scripts/run_suica_m4_f3_composition_scaling.py (loaded as f3()):
    world_seed_for, run_gate_g3 -- called unchanged. (f3().run_sweep_world
    itself is NOT called directly, because it does not expose the
    intermediate vectors_list/calibration/retained-set/weights this leg's
    truth computation needs -- see run_truth_sweep_world below, a disclosed
    structural near-duplicate that calls every one of the SAME downstream
    primitives f3().run_sweep_world itself calls, in the same order, with
    the same seed derivation, so it reproduces f3()'s/M4-F4's own numbers
    as a verified byproduct rather than a re-derivation.)
  - From scripts/run_suica_m4_f4_author_axis.py (loaded as f4()):
    build_live_tasks, build_holdout_task, cell_name_live, cell_name_null,
    seed_suffix_for_mult, AUTHOR_MULTS, KAPPAS, HOLDOUT_AUTHOR_MULT, DESIGN
    -- called/read unchanged, guaranteeing byte-identical task construction
    (seed_key strings above all) to what produced M4-F4's own persisted
    cells.csv/null_cells.csv/prediction.json.

NEW in this script (nothing above is reimplemented):
  - run_truth_sweep_world: the per-world engine (Part 0.1 disclosure above).
  - generate_truth_vectors_exact / generate_truth_vectors_long: the two
    registered truth-path variants (Part 0.3/0.4 of the report).
  - field_from_vectors: the shared featurize -> project -> field helper,
    applied identically to the finite sample and to both truth variants.
  - Gates G1 (direct reuse), G2 (continuity vs M4-F4's persisted cells),
    G3 (direct reuse), G4 (truth-path invariance, new).
  - The adjudication code (leans a/b/c, the pivot, the two-variant
    combination rule) and the registered secondary offset-corrected refit.

Stages (resumable, artifacts under results/m4_f5_gauge_validity/):
  --stage sweep       authors x{1,2,4,8,16} shared cells at the requested
                       kappas (--author-mults/--kappas select a subset for
                       chunked execution)
  --stage holdout      the authors x32 (kappa=1.0, shared) cell
  --stage gates        G1-G4, writes gates.json, STOPS on any failure;
                       requires sweep+holdout cells to already exist
  --stage sensitivity  T_LARGE robustness check (150 vs 600) on 2
                       representative cells; not gating, not part of --all
  --stage finalize     adjudication + registered secondary refit;
                       decision.json + cells.csv
  --stage all          sweep + holdout + gates + finalize (sensitivity is
                       run separately, on request)
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
from scipy import stats as _scipy_stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import suica_core.v8_realtext_relation_field as v8  # noqa: E402
from suica_core.v8_context_relation_field import _orthonormal_loadings  # noqa: E402

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"
MASTER_SEED = 20260802  # exactly M4-F1's/M4-F2's/M4-F3's/M4-F4's own MASTER_SEED.
DRAWS = 20
WORLDS_PER_CELL = 8
MIN_RETAINED_EVENTS = 8

# --- Part 0.3/0.4 (report) registered truth-path constants, fixed BEFORE compute. ---
# Pilot measurement (base1x world 0: 67.7s/6.5GB peak RSS at author_mult=32,
# T_LARGE=150, chunk=1500 -- see report Part 0.3 disclosure) showed the
# ORIGINAL 150/1500 pair would risk >6GB/world, unsafe at 8-way parallelism
# on this 24GB machine. T_LARGE_PRIMARY and TRUTH_CHUNK_SIZE were revised
# DOWNWARD, BEFORE any of the 11 registered cells were computed, purely for
# memory safety -- disclosed here as a pre-compute engineering revision, not
# a result-dependent one (no agreement/truth number had been seen yet at the
# time of this edit).
T_LARGE_PRIMARY = 80        # ~5-10x the observed per-author range (8-16 events).
T_LARGE_SENSITIVITY = 320   # 4x T_LARGE_PRIMARY, robustness check only (Part 0.3).
TRUTH_CHUNK_SIZE = 1000     # author-index chunking bound on peak memory (Part 0.3).
G4_TOLERANCE = 1e-9         # Part 0.11: floating-point exactness, not literal bit-0.

OUT = ROOT / "results" / "m4_f5_gauge_validity"
F1_OUT = ROOT / "results" / "m4_f1_panel_sizing"
F4_OUT = ROOT / "results" / "m4_f4_author_axis"
REF_PATH = F1_OUT / "realtext_panel_reference.json"
F1_CELLS_CSV = F1_OUT / "cells.csv"
F1_CALIBRATION = F1_OUT / "calibration_record.json"
F4_CELLS_CSV = F4_OUT / "cells.csv"
F4_NULL_CELLS_CSV = F4_OUT / "null_cells.csv"
F4_PREDICTION_JSON = F4_OUT / "prediction.json"

DESIGN = "shared"
AUTHOR_MULTS = [1, 2, 4, 8, 16]
HOLDOUT_AUTHOR_MULT = 32
KAPPAS = [("k05", 0.5), ("k10", 1.0)]
PRIMARY_KAPPA_TAG = "k10"
CONTEXT_KAPPA_TAG = "k05"

SENSITIVITY_CELLS = [
    ("base1x_shared_k10", 1, "k10"),
    ("authors_x32_holdout_shared_k10", 32, "k10"),
]


def _load_script(name: str) -> Any:
    """Copied verbatim from M4-F4's own Part 0.12 fix (register
    sys.modules[mod_name] = module BEFORE exec_module, so a nested
    ProcessPoolExecutor.map against a function defined in a
    dynamically-loaded module can pickle that function by reference).
    Zero edits to run_suica_m4_f1_panel_sizing.py,
    run_suica_m4_f2_composition.py, run_suica_m4_f3_composition_scaling.py,
    or run_suica_m4_f4_author_axis.py themselves."""
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


# ---------------------------------------------------------------------------
# Part 0.4 (report) -- the shared featurize -> project -> field path, applied
# IDENTICALLY to the finite sample and to both truth variants (the
# registration's own requirement: "the identical deployed featurize ->
# project -> field path... differing ONLY in the input").

def field_from_vectors(
    vectors: list[np.ndarray],
    ids: list[str],
    ctx: np.ndarray,
    resolved: list[str],
    calibration: dict[str, Any],
    spec: v8.RealTextRelationSpec,
    directions: Any,
    corpus: str,
    module: Any,
) -> dict[str, np.ndarray]:
    m, k = f1().featurize_panel(vectors, ids, corpus=corpus, spec=spec, directions=directions)
    panel = SimpleNamespace(raw={"M": m, "K": k})
    projected = module.project_soft(panel, np.ones(len(ids), dtype=bool), calibration)
    return module.deployed_soft_field(projected, ctx, resolved)


# ---------------------------------------------------------------------------
# Part 0.3 (report) -- TRUTH VARIANT A: analytic, exact-T, noise-free.
#
# A bit-identical replay of f2().generate_world_composed's own kappa>0 draw
# sequence (fresh rng=np.random.default_rng(world_seed); loadings, z, zeta,
# phi, the t_max-step AR(1) x, a stream-order-preserving but UNUSED noise
# draw) with the SAME f2().shock_vector calls and the SAME kappa blend --
# producing mean_part and state_part BIT-IDENTICAL to the live world's own
# values. Differs from the live event stream ONLY in that the idiosyncratic
# per-event Gaussian noise term (sqrt(w_e)*sigma_iso*noise) is never added.

def generate_truth_vectors_exact(
    counts: list[int],
    contexts: list[str],
    knobs: dict[str, Any],
    kappa: float,
    occasion_mode: str,
    world_seed: int,
    retained_idx: np.ndarray,
) -> list[np.ndarray]:
    if kappa <= 0.0:
        raise NotImplementedError(
            "kappa<=0 truth-exact path is out of scope: no M4-F5 swept cell uses it "
            "(G1 needs no truth path)."
        )
    rng = np.random.default_rng(world_seed)
    k = int(knobs["k"])
    rho = float(knobs["rho"])
    w_mu, w_x = float(knobs["w_mu"]), float(knobs["w_x"])
    phi_lo, phi_hi = float(knobs["phi_lo"]), float(knobs["phi_hi"])
    n = len(counts)
    t_max = max(counts)
    g = np.linspace(0.85, 0.55, k)
    a = math.sqrt(2.0 / float(np.sum(g**2)))
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
    _unused_noise = rng.normal(size=(n, t_max, 64))  # stream-form symmetry only; never added (Part 0.3).
    del _unused_noise
    mean_part = math.sqrt(w_mu) * a * ((z * g) @ loadings.T)

    labels = f2().occasion_labels(counts, occasion_mode)
    shock_x = np.zeros_like(x)
    cache: dict[tuple[str, int], np.ndarray] = {}
    kappa_f = float(kappa)
    for i in range(n):
        context = contexts[i]
        for t in range(counts[i]):
            occ = int(labels[i][t])
            key = (context, occ)
            vector = cache.get(key)
            if vector is None:
                vector = f2().shock_vector(world_seed, context, occ, k)
                cache[key] = vector
            shock_x[i, t] = vector

    blended_x = math.sqrt(max(0.0, 1.0 - kappa_f)) * x + math.sqrt(kappa_f) * shock_x
    state_part = math.sqrt(w_x) * a * ((blended_x * g) @ loadings.T)
    events_true = mean_part[:, None, :] + state_part  # NOTE: no + sqrt(w_e)*sigma_iso*noise term.
    return [events_true[i, : counts[i]] for i in retained_idx]


# ---------------------------------------------------------------------------
# Part 0.3 (report) -- TRUTH VARIANT B: large-sample asymptotic approximation.
#
# The SAME author-level invariants (loadings/z/zeta/phi/mean_part, replayed
# bit-identically to Variant A/live), but the STATE process is resampled
# over t_large synthetic occasions per RETAINED author instead of the
# observed finite T. The shared context-occasion shock reuses the UNCHANGED
# f2().shock_vector for occasion indices 0..t_large-1 -- the SAME
# deterministic per-(context,occasion) function the live world uses, so
# Variant B stays grounded in the SAME world's actual realized
# context-level process, merely sampled far longer, not a fresh alternate
# world. The author-private AR(1) state is redrawn over t_large steps using
# a freshly, deterministically-seeded stream (salt "m4f5-truth-long", keyed
# off world_seed and the chunk start) with the SAME per-author phi --
# statistically valid because x_i,t is already-stationary from t=0
# (x_i,0 ~ N(0,1) unconditionally), so a fresh long realization
# characterizes the same population moments a literal continuation would.
# Also noise-free, matching Variant A. Processed in author-index chunks to
# bound peak memory at the largest (x32) cell.

def generate_truth_vectors_long(
    counts: list[int],
    knobs: dict[str, Any],
    kappa: float,
    world_seed: int,
    retained_idx: np.ndarray,
    retained_ctx: np.ndarray,
    *,
    t_large: int,
    chunk_size: int = TRUTH_CHUNK_SIZE,
) -> list[np.ndarray]:
    if kappa <= 0.0:
        raise NotImplementedError(
            "kappa<=0 truth-long path is out of scope: no M4-F5 swept cell uses it."
        )
    rng = np.random.default_rng(world_seed)
    k = int(knobs["k"])
    rho = float(knobs["rho"])
    w_mu, w_x = float(knobs["w_mu"]), float(knobs["w_x"])
    phi_lo, phi_hi = float(knobs["phi_lo"]), float(knobs["phi_hi"])
    n = len(counts)
    g = np.linspace(0.85, 0.55, k)
    a = math.sqrt(2.0 / float(np.sum(g**2)))
    loadings = _orthonormal_loadings(rng, 64, k)
    z = rng.normal(size=(n, k))
    zeta = rng.normal(size=(n, k))
    logits = rho * z + math.sqrt(max(0.0, 1.0 - rho**2)) * zeta
    phi = phi_lo + (phi_hi - phi_lo) / (1.0 + np.exp(-logits))
    mean_part = math.sqrt(w_mu) * a * ((z * g) @ loadings.T)  # (n, 64), bit-identical to live's own mean_part.

    kappa_f = float(kappa)
    n_retained = len(retained_idx)
    results: dict[int, np.ndarray] = {}
    shock_cache: dict[tuple[str, int], np.ndarray] = {}
    for start in range(0, n_retained, chunk_size):
        stop = min(start + chunk_size, n_retained)
        chunk_positions = list(range(start, stop))
        chunk_author_idx = [int(retained_idx[p]) for p in chunk_positions]
        chunk_ctx = [str(retained_ctx[p]) for p in chunk_positions]
        n_chunk = len(chunk_author_idx)
        phi_chunk = phi[chunk_author_idx]

        rng_long = np.random.default_rng(
            v8.stable_bucket(f"{world_seed}-truth-long-x-{start}", salt="m4f5-truth-long", modulus=2**63 - 1)
        )
        x_long = np.empty((n_chunk, t_large, k), dtype=float)
        x_long[:, 0] = rng_long.normal(size=(n_chunk, k))
        innovation_scale = np.sqrt(1.0 - phi_chunk**2)
        for t in range(1, t_large):
            x_long[:, t] = phi_chunk * x_long[:, t - 1] + innovation_scale * rng_long.normal(size=(n_chunk, k))

        shock_long = np.empty_like(x_long)
        for row, context in enumerate(chunk_ctx):
            for t in range(t_large):
                key = (context, t)
                vector = shock_cache.get(key)
                if vector is None:
                    vector = f2().shock_vector(world_seed, context, t, k)
                    shock_cache[key] = vector
                shock_long[row, t] = vector

        blended_x = math.sqrt(max(0.0, 1.0 - kappa_f)) * x_long + math.sqrt(kappa_f) * shock_long
        state_part = math.sqrt(w_x) * a * ((blended_x * g) @ loadings.T)
        mean_part_chunk = mean_part[chunk_author_idx]
        events_long = mean_part_chunk[:, None, :] + state_part  # noise-free, as in Variant A.
        for row, position in enumerate(chunk_positions):
            results[position] = events_long[row]
        del x_long, shock_long, blended_x, state_part, events_long

    return [results[p] for p in range(n_retained)]


# ---------------------------------------------------------------------------
# The per-world engine: a disclosed structural near-duplicate of
# f3().run_sweep_world (Part 0.1) -- every downstream primitive it calls
# (f1().build_layout, f2().generate_world_composed, f1().featurize_panel,
# module.calibrate_d0_soft, module.resolved_contexts, f1().half_indices,
# module.project_soft, module.deployed_soft_field, module.field_agreement)
# is the SAME unchanged function f3().run_sweep_world itself uses, in the
# same order, with the same seed derivation (f3().world_seed_for on f4()'s
# own seed_key strings, the SAME corpus string convention
# "m4f3-{seed_key}-w{world}") -- so the split-half agreement this function
# produces reproduces M4-F4's own persisted value as a verified byproduct
# (gate G2), not a re-derivation on a different code path.

def _prepare_world(task: dict[str, Any]) -> dict[str, Any]:
    spec = f1().load_spec()
    directions = f1()._directions(spec)
    module = f1().e1()
    reference = json.loads(Path(task["ref_path"]).read_text(encoding="utf-8"))
    author_ids, contexts, splits, counts = f1().build_layout(
        reference, task["author_mult"], task["event_mult"]
    )
    corpus = f"m4f3-{task['seed_key']}-w{task['world']}"  # IDENTICAL to f3().run_sweep_world's own corpus -- required for G2.
    world_seed = f3().world_seed_for(task["seed_key"], task["world"], task["knob_tag"])
    vectors_list = f2().generate_world_composed(
        counts, contexts, task["knobs"], task["kappa"], task["occasion_mode"], world_seed
    )

    raw_m, raw_k = f1().featurize_panel(
        vectors_list, author_ids, corpus=corpus, spec=spec, directions=directions
    )
    metadata = pd.DataFrame(
        {"author_id": author_ids, "context": contexts, "split": splits, "event_count": counts}
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
        "author_ids": author_ids, "contexts": contexts, "counts": counts,
        "corpus": corpus, "world_seed": world_seed, "vectors_list": vectors_list,
        "raw_m": raw_m, "raw_k": raw_k, "calibration": calibration,
        "resolved": resolved, "retained_idx": retained_idx, "retained_ids": retained_ids,
        "retained_ctx": retained_ctx, "weights": weights,
    }


def run_truth_sweep_world(task: dict[str, Any]) -> dict[str, Any]:
    started = time.time()
    w = _prepare_world(task)
    spec, directions, module = w["spec"], w["directions"], w["module"]
    author_ids, counts, corpus = w["author_ids"], w["counts"], w["corpus"]
    vectors_list, calibration = w["vectors_list"], w["calibration"]
    resolved, retained_idx = w["resolved"], w["retained_idx"]
    retained_ids, retained_ctx, weights = w["retained_ids"], w["retained_ctx"], w["weights"]

    # ---- (A) split-half agreement, IDENTICAL procedure to f3().run_sweep_world. ----
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

    # ---- (B) finite-sample ESTIMATE field: SAME path, fed the actual full (unsplit) retained vectors. ----
    retained_vectors = [vectors_list[i] for i in retained_idx]
    field_est_full = field_from_vectors(
        retained_vectors, retained_ids, retained_ctx, resolved, calibration, spec, directions, corpus, module
    )
    w["vectors_list"] = None  # null the dict's own reference too, not just the local binding.
    del retained_vectors, vectors_list, halves_a, halves_b  # large, no longer needed (memory discipline, Part 0.3).

    # ---- G4 byproduct: an INDEPENDENT route to the identical finite-sample field
    # (mask the ALREADY-computed full-population raw_m/raw_k, rather than a fresh
    # featurize_panel call on the retained-only subset) -- must agree to G4_TOLERANCE.
    final_mask = np.zeros(len(author_ids), dtype=bool)
    final_mask[retained_idx] = True
    projected_via_mask = module.project_soft(SimpleNamespace(raw={"M": w["raw_m"], "K": w["raw_k"]}), final_mask, calibration)
    field_est_full_via_mask = module.deployed_soft_field(projected_via_mask, retained_ctx, resolved)
    g4_diffs = [
        float(np.max(np.abs(field_est_full[c] - field_est_full_via_mask[c])))
        for c in field_est_full
    ]
    g4_max_diff = float(max(g4_diffs)) if g4_diffs else 0.0
    w["raw_m"] = w["raw_k"] = None  # large (n_authors_total, 2, D); done with it (memory discipline).
    del projected_via_mask, field_est_full_via_mask
    gc.collect()

    # ---- (C) Truth Variant A (exact, noise-free, same finite T). ----
    truth_vectors_exact = generate_truth_vectors_exact(
        counts, w["contexts"], task["knobs"], task["kappa"], task["occasion_mode"], w["world_seed"], retained_idx
    )
    field_true_exact = field_from_vectors(
        truth_vectors_exact, retained_ids, retained_ctx, resolved, calibration, spec, directions, corpus, module
    )
    truth_recovery_exact = module.field_agreement(field_est_full, field_true_exact, weights)
    del truth_vectors_exact, field_true_exact
    gc.collect()

    # ---- (D) Truth Variant B (large-sample asymptotic, T_LARGE_PRIMARY). ----
    truth_vectors_long = generate_truth_vectors_long(
        counts, task["knobs"], task["kappa"], w["world_seed"], retained_idx, retained_ctx, t_large=T_LARGE_PRIMARY
    )
    field_true_long = field_from_vectors(
        truth_vectors_long, retained_ids, retained_ctx, resolved, calibration, spec, directions, corpus, module
    )
    truth_recovery_long = module.field_agreement(field_est_full, field_true_long, weights)
    del truth_vectors_long, field_true_long
    gc.collect()

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
        "agreement_mean": agreement_mean,
        "agreement_sd": agreement_sd,
        "draw_values": [float(v) for v in draw_values],
        "truth_recovery_exact": float(truth_recovery_exact),
        "truth_recovery_long": float(truth_recovery_long),
        "t_large": int(T_LARGE_PRIMARY),
        "g4_max_diff": g4_max_diff,
        "world_seed": int(w["world_seed"]),
        "seconds": float(time.time() - started),
    }


# ---------------------------------------------------------------------------
# Sensitivity (Part 0.3): T_LARGE_SENSITIVITY (4x primary) on 2 representative
# cells, NOT gating, run on request only (--stage sensitivity).

def run_sensitivity_world(task: dict[str, Any]) -> dict[str, Any]:
    started = time.time()
    w = _prepare_world(task)
    spec, directions, module = w["spec"], w["directions"], w["module"]
    counts, corpus, calibration = w["counts"], w["corpus"], w["calibration"]
    resolved, retained_idx = w["resolved"], w["retained_idx"]
    retained_ids, retained_ctx, weights = w["retained_ids"], w["retained_ctx"], w["weights"]
    vectors_list = w["vectors_list"]

    retained_vectors = [vectors_list[i] for i in retained_idx]
    field_est_full = field_from_vectors(
        retained_vectors, retained_ids, retained_ctx, resolved, calibration, spec, directions, corpus, module
    )
    truth_vectors_long_primary = generate_truth_vectors_long(
        counts, task["knobs"], task["kappa"], w["world_seed"], retained_idx, retained_ctx, t_large=T_LARGE_PRIMARY
    )
    field_primary = field_from_vectors(
        truth_vectors_long_primary, retained_ids, retained_ctx, resolved, calibration, spec, directions, corpus, module
    )
    recovery_primary = module.field_agreement(field_est_full, field_primary, weights)

    truth_vectors_long_sens = generate_truth_vectors_long(
        counts, task["knobs"], task["kappa"], w["world_seed"], retained_idx, retained_ctx, t_large=T_LARGE_SENSITIVITY
    )
    field_sens = field_from_vectors(
        truth_vectors_long_sens, retained_ids, retained_ctx, resolved, calibration, spec, directions, corpus, module
    )
    recovery_sens = module.field_agreement(field_est_full, field_sens, weights)

    # Column names are DERIVED from the live constants (not hardcoded literals):
    # an earlier draft hardcoded "_t150"/"_t600" while T_LARGE_PRIMARY/
    # T_LARGE_SENSITIVITY were still 150/600; when both were revised down to
    # 80/320 for memory safety (Part 0.3 of the report), the hardcoded labels
    # were NOT updated, producing mislabeled (but numerically CORRECT --
    # `t_large=T_LARGE_PRIMARY`/`t_large=T_LARGE_SENSITIVITY` were always the
    # actual arguments passed) columns in the first sensitivity run. Fixed
    # here to read the value straight off the constants so the label can never
    # drift from the computation again; disclosed in the report.
    primary_col = f"truth_recovery_long_t{T_LARGE_PRIMARY}"
    sens_col = f"truth_recovery_long_t{T_LARGE_SENSITIVITY}"
    return {
        "cell": task["cell"], "world": int(task["world"]), "author_mult": int(task["author_mult"]),
        "kappa": float(task["kappa"]),
        primary_col: float(recovery_primary),
        sens_col: float(recovery_sens),
        "abs_diff": float(abs(recovery_sens - recovery_primary)),
        "seconds": float(time.time() - started),
    }


def run_sensitivity(knobs: dict[str, Any], knob_tag: str, workers: int, draws: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    primary_col = f"truth_recovery_long_t{T_LARGE_PRIMARY}"
    sens_col = f"truth_recovery_long_t{T_LARGE_SENSITIVITY}"
    all_tasks = f4().build_live_tasks(knobs, knob_tag, draws, f4().AUTHOR_MULTS, {"k05", "k10"})
    holdout_tasks = f4().build_holdout_task(knobs, knob_tag, draws)
    by_cell = {}
    for t in all_tasks + holdout_tasks:
        by_cell.setdefault(t["cell"], []).append(t)
    rows: list[dict[str, Any]] = []
    for cell, _mult, _kt in SENSITIVITY_CELLS:
        tasks = by_cell[cell]
        started = time.time()
        with ProcessPoolExecutor(max_workers=min(workers, 4)) as pool:
            cell_rows = list(pool.map(run_sensitivity_world, tasks))
        for row in sorted(cell_rows, key=lambda r: r["world"]):
            print(
                f"[sensitivity {cell} w{row['world']}] t{T_LARGE_PRIMARY}={row[primary_col]:+.4f} "
                f"t{T_LARGE_SENSITIVITY}={row[sens_col]:+.4f} diff={row['abs_diff']:.5f} "
                f"{row['seconds']:.0f}s", flush=True,
            )
        rows.extend(cell_rows)
        print(f"[sensitivity {cell}] done in {time.time() - started:.0f}s")
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "sensitivity_t_large.csv", index=False)
    summary = frame.groupby("cell").agg(
        **{
            f"t{T_LARGE_PRIMARY}_mean": (primary_col, "mean"),
            f"t{T_LARGE_SENSITIVITY}_mean": (sens_col, "mean"),
            "abs_diff_mean": ("abs_diff", "mean"),
            "abs_diff_max": ("abs_diff", "max"),
        }
    ).reset_index()
    summary.to_csv(OUT / "sensitivity_t_large_summary.csv", index=False)
    print(summary.to_string(index=False))


# ---------------------------------------------------------------------------
# Sweep drivers (resumable, chunkable via --author-mults/--kappas).

def _write_cell(cell: str, rows: list[dict[str, Any]], started: float) -> None:
    for row in sorted(rows, key=lambda r: r["world"]):
        print(
            f"[{cell} w{row['world']}] A {row['agreement_mean']:+.4f} "
            f"truthA {row['truth_recovery_exact']:+.4f} truthB {row['truth_recovery_long']:+.4f} "
            f"g4 {row['g4_max_diff']:.2e} n_ret {row['n_retained']} {row['seconds']:.0f}s", flush=True,
        )
    draw_rows = [
        {"cell": cell, "world": row["world"], "draw": d, "agreement": v}
        for row in rows
        for d, v in enumerate(row["draw_values"])
    ]
    pd.DataFrame(rows).drop(columns=["draw_values"]).to_csv(OUT / f"cell_{cell}.csv", index=False)
    pd.DataFrame(draw_rows).to_csv(OUT / f"draws_{cell}.csv", index=False)
    print(f"[{cell}] done in {time.time() - started:.0f}s -> cell_{cell}.csv")


def run_sweep(knobs: dict[str, Any], knob_tag: str, workers: int, draws: int, mults: list[int], kappa_tags: set[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = f4().build_live_tasks(knobs, knob_tag, draws, mults, kappa_tags)
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
            rows = list(pool.map(run_truth_sweep_world, cell_tasks))
        _write_cell(cell, rows, started)


def run_holdout(knobs: dict[str, Any], knob_tag: str, workers: int, draws: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = f4().build_holdout_task(knobs, knob_tag, draws)
    cell = tasks[0]["cell"]
    path = OUT / f"cell_{cell}.csv"
    if path.exists():
        print(f"[skip] {cell} exists")
        return
    started = time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(run_truth_sweep_world, tasks))
    _write_cell(cell, rows, started)


def cell_summary(cell: str) -> dict[str, Any]:
    frame = pd.read_csv(OUT / f"cell_{cell}.csv")
    values = frame["agreement_mean"].to_numpy(dtype=float)
    mean = float(values.mean())
    se = float(values.std(ddof=1) / math.sqrt(len(values)))
    truth_exact = frame["truth_recovery_exact"].to_numpy(dtype=float)
    truth_long = frame["truth_recovery_long"].to_numpy(dtype=float)
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
        "truth_recovery_exact_mean": float(truth_exact.mean()),
        "truth_recovery_exact_se": float(truth_exact.std(ddof=1) / math.sqrt(len(truth_exact))),
        "truth_recovery_long_mean": float(truth_long.mean()),
        "truth_recovery_long_se": float(truth_long.std(ddof=1) / math.sqrt(len(truth_long))),
        "g4_max_diff_over_worlds": float(frame["g4_max_diff"].max()),
        "world_seeds": frame["world_seed"].astype(int).tolist(),
        "world_values": values.tolist(),
    }


# ---------------------------------------------------------------------------
# Gates.

def run_gate_g1(knobs: dict[str, Any], knob_tag: str, workers: int) -> dict[str, Any]:
    """Direct call, unchanged: kappa<=0 free cell reproduces M4-F1's persisted base1x."""
    return f2().run_gate_g1(knobs, knob_tag, workers)


def run_gate_g3() -> dict[str, Any]:
    """Direct call, unchanged: gauge invariance (batched feature map vs deployed
    v8.build_feature_panel; numpy halving vs e1().split_half_frames)."""
    return f3().run_gate_g3()


def _read_f4_persisted_row(frame: pd.DataFrame, cell: str) -> dict[str, float]:
    row = frame.loc[frame["cell"] == cell].iloc[0]
    return {
        "agreement_mean": float(row["agreement_mean"]),
        "agreement_se": float(row["agreement_se"]),
        "d0_eff_rank_M_mean": float(row["d0_eff_rank_M_mean"]),
        "d0_eff_rank_K_mean": float(row["d0_eff_rank_K_mean"]),
        "n_retained": int(row["n_retained"]),
    }


def run_gate_g2(all_cells: list[str]) -> dict[str, Any]:
    """Continuity: every one of M4-F4's own 11 persisted cells (10 sweep +
    the x32 holdout), freshly recomputed by THIS script's run_truth_sweep_world
    on IDENTICAL world seeds, reproduces results/m4_f4_author_axis/cells.csv
    to <=1e-12."""
    target_frame = pd.read_csv(F4_CELLS_CSV)
    rows = []
    all_match = True
    for cell in all_cells:
        path = OUT / f"cell_{cell}.csv"
        if not path.exists():
            raise AssertionError(f"G2 requires {path} to exist; run --stage sweep/holdout first.")
        got = cell_summary(cell)
        target = _read_f4_persisted_row(target_frame, cell)
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
        rows.append({"cell": cell, "target": target, "observed": {k: got[k] for k in target}, "abs_diffs": diffs, "pass": row_pass})
    return {
        "gate": "G2",
        "description": "every one of M4-F4's own 11 persisted cells, freshly recomputed by "
        "run_truth_sweep_world on identical world seeds, reproduces results/m4_f4_author_axis/"
        "cells.csv to <=1e-12 -- a mismatch VOIDS the comparison per the registration",
        "tolerance": 1e-12,
        "rows": rows,
        "pass": bool(all_match),
    }


def run_gate_g4(all_cells: list[str]) -> dict[str, Any]:
    """Truth-path invariance: for every world of every cell, the finite-sample
    field computed via field_from_vectors (a fresh featurize_panel call on the
    retained-only subset) must agree with the SAME finite-sample field computed
    via an INDEPENDENT route (masking the already-computed full-population
    raw_m/raw_k through the same calibration) to <=G4_TOLERANCE -- i.e. the
    truth path, fed the finite sample instead of a noise-free input,
    reproduces the finite-sample field (Part 0.5/0.11 of the report)."""
    rows = []
    all_pass = True
    for cell in all_cells:
        frame = pd.read_csv(OUT / f"cell_{cell}.csv")
        cell_max = float(frame["g4_max_diff"].max())
        cell_pass = bool(cell_max <= G4_TOLERANCE)
        all_pass = all_pass and cell_pass
        rows.append({"cell": cell, "max_diff": cell_max, "pass": cell_pass})
    highlighted = rows[0] if rows else None
    return {
        "gate": "G4",
        "description": "truth-path invariance: two independent routes to the identical "
        "finite-sample field (fresh field_from_vectors call vs. masking the already-computed "
        "full-population raw_m/raw_k) agree to <=G4_TOLERANCE, for every world of every cell",
        "tolerance": G4_TOLERANCE,
        "highlighted_degenerate_case": highlighted,
        "rows": rows,
        "pass": bool(all_pass),
    }


def run_gates(knobs: dict[str, Any], knob_tag: str, workers: int, all_cells: list[str]) -> dict[str, Any]:
    g1 = run_gate_g1(knobs, knob_tag, workers)
    g3 = run_gate_g3()
    g2 = run_gate_g2(all_cells)
    g4 = run_gate_g4(all_cells)
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
        raise AssertionError("Gate(s) failed; see results/m4_f5_gauge_validity/gates.json.")
    return gates


# ---------------------------------------------------------------------------
# Adjudication -- Part 0.6-0.10 (report) operationalizations, exactly.

def _linear_fit(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    slope, intercept = np.polyfit(x, y, 1)
    return {"slope": float(slope), "intercept": float(intercept)}


def _linear_eval(fit: dict[str, float], x: float) -> float:
    return float(fit["slope"] * x + fit["intercept"])


def check_pairwise_comovement(points: list[dict[str, float]]) -> dict[str, Any]:
    """No cell pair where agreement rises and truth recovery falls (Part 0
    lean-a rule, all C(n,2) pairs)."""
    violations = []
    for i in range(len(points)):
        for j in range(len(points)):
            if i == j:
                continue
            a, b = points[i], points[j]
            if a["agreement"] < b["agreement"] and a["truth"] > b["truth"]:
                violations.append({"lower_agreement_cell": a["cell"], "higher_agreement_cell": b["cell"],
                                    "agreement_lower": a["agreement"], "agreement_higher": b["agreement"],
                                    "truth_lower": a["truth"], "truth_higher": b["truth"]})
    return {"n_pairs_checked": len(points) * (len(points) - 1), "violations": violations, "any_violation": bool(violations)}


def adjudicate_variant(points: list[dict[str, float]], k05_points: list[dict[str, float]], k10_points: list[dict[str, float]]) -> dict[str, Any]:
    agreement = np.asarray([p["agreement"] for p in points], dtype=float)
    truth = np.asarray([p["truth"] for p in points], dtype=float)
    rho, pval = _scipy_stats.spearmanr(agreement, truth)
    comovement = check_pairwise_comovement(points)
    lean_a_hold = bool(rho >= 0.9 and not comovement["any_violation"])

    fit10 = _linear_fit(np.asarray([p["agreement"] for p in k10_points]), np.asarray([p["truth"] for p in k10_points]))
    max_agreement_k10 = float(max(p["agreement"] for p in k10_points))
    target_agreement = 0.5
    truth_at_target = _linear_eval(fit10, target_agreement)
    extrapolated = bool(target_agreement > max_agreement_k10)
    lean_b_hold = bool(truth_at_target >= 0.7)

    fit_k10_for_interp = fit10
    matched = []
    for p05 in k05_points:
        truth_k10_interp = _linear_eval(fit_k10_for_interp, p05["agreement"])
        diff = abs(p05["truth"] - truth_k10_interp)
        matched.append({
            "cell_k05": p05["cell"], "agreement": p05["agreement"],
            "truth_k05_observed": p05["truth"], "truth_k10_interpolated": truth_k10_interp,
            "abs_diff": diff, "within_0_1": bool(diff <= 0.1),
        })
    lean_c_hold = bool(all(m["within_0_1"] for m in matched)) if matched else False

    pivot_reasons = []
    if comovement["any_violation"]:
        pivot_reasons.append("agreement rose while truth recovery fell for at least one cell pair")
    if truth_at_target < 0.5:
        pivot_reasons.append("truth recovery at the .5-agreement point is below .5")
    pivot_fires = bool(pivot_reasons)

    return {
        "spearman_rho_pooled": float(rho), "spearman_p_pooled": float(pval),
        "comovement": comovement,
        "lean_a": {"rule": "Spearman>=.9 pooled AND no agreement-up/truth-down cell pair", "verdict": "HOLD" if lean_a_hold else "MISS"},
        "linear_fit_k10": fit10,
        "max_measured_agreement_k10": max_agreement_k10,
        "truth_recovery_at_p5_agreement": truth_at_target,
        "extrapolated_beyond_measured_range": extrapolated,
        "lean_b": {"rule": "truth recovery >=.7 at the .5-agreement point (interpolated/extrapolated linear fit)", "verdict": "HOLD" if lean_b_hold else "MISS"},
        "kappa_matched_points": matched,
        "lean_c": {"rule": "|truth(k05) - truth(k10 interpolated)| <=.1 at every one of kappa=0.5's own 5 agreement values", "verdict": "HOLD" if lean_c_hold else "MISS"},
        "pivot_local": {"reasons_fired": pivot_reasons, "fires": pivot_fires},
    }


def adjudicate(all_summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    def pts(kappa_tag: str | None, variant_key: str) -> list[dict[str, float]]:
        out = []
        for cell, s in all_summaries.items():
            if kappa_tag is not None and s["kappa_tag"] != kappa_tag:
                continue
            out.append({"cell": cell, "agreement": s["agreement_mean"], "truth": s[variant_key]})
        return sorted(out, key=lambda p: p["agreement"])

    variants = {}
    for variant_key, label in (("truth_recovery_exact_mean", "exact"), ("truth_recovery_long_mean", "asymptotic")):
        pooled = pts(None, variant_key)
        k05 = pts("k05", variant_key)
        k10 = pts("k10", variant_key)
        variants[label] = adjudicate_variant(pooled, k05, k10)

    # Part 0.7 (report): two-variant combination rule -- HOLD requires BOTH variants;
    # pivot fires if EITHER variant triggers either registered pivot condition.
    lean_a_hold = bool(variants["exact"]["lean_a"]["verdict"] == "HOLD" and variants["asymptotic"]["lean_a"]["verdict"] == "HOLD")
    lean_b_hold = bool(variants["exact"]["lean_b"]["verdict"] == "HOLD" and variants["asymptotic"]["lean_b"]["verdict"] == "HOLD")
    lean_c_hold = bool(variants["exact"]["lean_c"]["verdict"] == "HOLD" and variants["asymptotic"]["lean_c"]["verdict"] == "HOLD")
    pivot_fires = bool(variants["exact"]["pivot_local"]["fires"] or variants["asymptotic"]["pivot_local"]["fires"])
    pivot_reasons = [f"[{label}] {r}" for label in ("exact", "asymptotic") for r in variants[label]["pivot_local"]["reasons_fired"]]

    if pivot_fires:
        verdict = "GAUGE_INVALID_CERTIFICATE_WITHDRAWN_46_1X_BUDGET_AND_26K_RECOMMENDATION_WITHDRAWN"
    elif lean_a_hold and lean_b_hold and lean_c_hold:
        verdict = "GAUGE_VALID_CERTIFICATE_HOLDS"
    else:
        verdict = "MIXED_SEE_LEAN_ADJUDICATION"

    return {
        "variants": variants,
        "combination_rule": "lean HOLD requires BOTH variants HOLD (conservative AND); pivot fires if EITHER "
        "variant triggers either registered condition (conservative OR) -- Part 0.7 of the report, registered "
        "before compute",
        "lean_a": {"lean": "a", "rule": "co-movement", "verdict": "HOLD" if lean_a_hold else "MISS"},
        "lean_b": {"lean": "b", "rule": "target adequacy", "verdict": "HOLD" if lean_b_hold else "MISS"},
        "lean_c": {"lean": "c", "rule": "kappa stability", "verdict": "HOLD" if lean_c_hold else "MISS"},
        "pivot": {"reasons_fired": pivot_reasons, "fires": pivot_fires},
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Registered secondary check (not a lean): refit M4-F4's author-axis law
# after subtracting the per-cell G0 null offset (Part 0.10 of the report).

def refit_with_null_offset() -> dict[str, Any]:
    live = pd.read_csv(F4_CELLS_CSV)
    null = pd.read_csv(F4_NULL_CELLS_CSV)
    results = {}
    for kappa_tag, kappa_val in (("k10", 1.0), ("k05", 0.5)):
        rows_unchanged_se = []
        rows_quadrature_se = []
        detail = []
        for mult in f4().AUTHOR_MULTS:
            live_cell = f4().cell_name_live(mult, kappa_tag)
            null_cell = f4().cell_name_null(mult, kappa_tag)
            live_row = live.loc[live["cell"] == live_cell].iloc[0]
            null_row = null.loc[null["cell"] == null_cell].iloc[0]
            live_mean, live_se = float(live_row["agreement_mean"]), float(live_row["agreement_se"])
            null_mean, null_se = float(null_row["agreement_mean"]), float(null_row["agreement_se"])
            corrected_mean = live_mean - null_mean
            quadrature_se = math.sqrt(live_se**2 + null_se**2)
            detail.append({
                "author_mult": mult, "live_mean": live_mean, "live_se": live_se,
                "null_mean": null_mean, "null_se": null_se, "corrected_mean": corrected_mean,
                "se_unchanged": live_se, "se_quadrature": quadrature_se,
            })
            rows_unchanged_se.append({"cell": live_cell, "author_mult": mult, "agreement_mean": corrected_mean, "agreement_se": live_se})
            rows_quadrature_se.append({"cell": live_cell, "author_mult": mult, "agreement_mean": corrected_mean, "agreement_se": quadrature_se})
        fit_unchanged = f1().fit_axis(rows_unchanged_se, "author_mult")
        fit_quadrature = f1().fit_axis(rows_quadrature_se, "author_mult")
        results[kappa_tag] = {"detail": detail, "fit_se_unchanged": fit_unchanged, "fit_se_quadrature": fit_quadrature}

    primary = results["k10"]["fit_se_unchanged"]
    original_budget = None
    try:
        pred = json.loads(F4_PREDICTION_JSON.read_text(encoding="utf-8"))
        original_budget = pred["fit_point"]["k10"]["half_agreement_mult"]
    except Exception:
        pass
    corrected_budget = primary.get("half_agreement_mult")
    factor_vs_original = (corrected_budget / original_budget) if (original_budget and corrected_budget not in (None, float("inf"))) else None
    return {
        "by_kappa": results,
        "primary_reading": "se_unchanged (Part 0.10 of the report: subtract the null offset from the MEAN only)",
        "original_m4f4_budget_k10": original_budget,
        "corrected_budget_k10_primary": corrected_budget,
        "corrected_vs_original_factor": factor_vs_original,
        "exceeds_factor_2": bool(factor_vs_original is not None and factor_vs_original > 2.0),
    }


# ---------------------------------------------------------------------------

def run_finalize() -> None:
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    all_cells = [f4().cell_name_live(m, kt) for m in AUTHOR_MULTS for kt, _ in KAPPAS]
    holdout_cell = f"authors_x{HOLDOUT_AUTHOR_MULT}_holdout_{DESIGN}_k10"
    all_cells.append(holdout_cell)

    summaries = {}
    for cell in all_cells:
        s = cell_summary(cell)
        s["kappa_tag"] = "k10" if abs(s["kappa"] - 1.0) < 1e-9 else "k05"
        summaries[cell] = s

    adjudication = adjudicate(summaries)
    secondary = refit_with_null_offset()

    summary_rows = [{k: v for k, v in s.items() if k not in ("world_seeds", "world_values")} for s in summaries.values()]
    pd.DataFrame(summary_rows).to_csv(OUT / "cells.csv", index=False)

    decision = {
        "experiment": "M4-F5_gauge_validity",
        "banner": BANNER,
        "tier": "EXPLORATORY",
        "registered_spec": "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md#M4-F5-registration",
        "part0_registered_in": "reports/SUICA_M4_F5_GAUGE_VALIDITY_REPORT.md Part 0 (before run)",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "worlds_per_cell": WORLDS_PER_CELL,
        "draws_per_world": DRAWS,
        "t_large_primary": T_LARGE_PRIMARY,
        "t_large_sensitivity": T_LARGE_SENSITIVITY,
        "gates": {k: (v["pass"] if isinstance(v, dict) and "pass" in v else v) for k, v in gates.items()},
        "gates_all_pass": gates["all_pass"],
        "adjudication": adjudication,
        "registered_secondary_offset_corrected_refit": secondary,
        "label_free": True,
        "claim_boundary": (
            "Synthetic gauge-validity audit in a world calibrated to the opened PANDORA "
            "D-panel regime; licenses a finding about whether the DEPLOYED split-half "
            "agreement statistic certifies truth-referenced recovery under this synthetic "
            "instrument. No claim about the real relation field's content, personality, "
            "emotion, diagnosis, or any individual."
        ),
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(adjudication, indent=2, default=str))
    print(json.dumps(secondary, indent=2, default=str))


# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["sweep", "holdout", "gates", "sensitivity", "finalize", "all"], default="all")
    parser.add_argument("--workers", type=int, default=max(2, min(8, (os.cpu_count() or 4) - 2)))
    parser.add_argument("--draws", type=int, default=DRAWS)
    parser.add_argument("--author-mults", type=str, default="1,2,4,8,16")
    parser.add_argument("--kappas", type=str, default="k05,k10")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if not REF_PATH.exists():
        raise AssertionError(f"{REF_PATH} missing (M4-F1 artifact required, read-only).")
    if not F1_CELLS_CSV.exists():
        raise AssertionError(f"{F1_CELLS_CSV} missing (M4-F1 artifact required, read-only).")
    if not F4_CELLS_CSV.exists() or not F4_NULL_CELLS_CSV.exists():
        raise AssertionError("M4-F4 artifacts missing (results/m4_f4_author_axis/, required, read-only).")
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

    if args.stage in ("sweep", "all"):
        run_sweep(knobs, knob_tag, args.workers, args.draws, mults, kappa_tags)
    if args.stage in ("holdout", "all"):
        run_holdout(knobs, knob_tag, args.workers, args.draws)
    if args.stage in ("gates", "all"):
        all_cells = [f4().cell_name_live(m, kt) for m in AUTHOR_MULTS for kt, _ in KAPPAS]
        all_cells.append(f"authors_x{HOLDOUT_AUTHOR_MULT}_holdout_{DESIGN}_k10")
        run_gates(knobs, knob_tag, args.workers, all_cells)
    if args.stage == "sensitivity":
        run_sensitivity(knobs, knob_tag, args.workers, args.draws)
    if args.stage in ("finalize", "all"):
        run_finalize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
