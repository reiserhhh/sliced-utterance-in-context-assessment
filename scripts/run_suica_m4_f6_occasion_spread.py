#!/usr/bin/env python3
"""M4-F6 -- can occasion SPREAD certify the trait-level object?

Registered spec: docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md section
"M4-F6 registration (2026-08-03, BEFORE run) -- can occasion SPREAD certify
the trait-level object?" Part 0 register-notes (every implementation choice
the registration left open -- the gap derivation and the B=1 budget
resolution above all -- written BEFORE any compute) are in
reports/SUICA_M4_F6_OCCASION_SPREAD_REPORT.md Part 0.

M4-F5 found: at kappa=1.0 over authors x1->x32, split-half agreement rises
63x while truth recovery against a NOISE-FREE SAME-OCCASION target
(Variant A) rises only 4.3x and truth recovery against a LONG-WINDOW target
(Variant B) plateaus near .15 and does not move under a 4x window increase.
Authors and events-per-author are both WITHIN-window axes. This leg tests the
third, classical axis: spreading observation across widely-separated
occasion BLOCKS so the realized AR(1) state decorrelates.

Reuse boundary (task's explicit instruction: "reuse its two truth variants,
its truth-path, its gates (G1/G3/G4), and its cell machinery. Do not
reimplement them."):
  - From scripts/run_suica_m4_f1_panel_sizing.py (loaded as f1()): load_spec,
    _directions, e1(), build_layout, featurize_panel, half_indices, knob_tag
    -- called unchanged.
  - From scripts/run_suica_m4_f2_composition.py (loaded as f2()):
    generate_world_composed, occasion_labels, shock_vector, run_gate_g1,
    run_gate_g3 -- called unchanged (shock_vector is reused VERBATIM inside
    the new spread generator below; occasion_labels/generate_world_composed
    are called unchanged only for the RAW gate-anchor cells).
  - From scripts/run_suica_m4_f3_composition_scaling.py (loaded as f3()):
    world_seed_for, run_gate_g3 -- called unchanged.
  - From scripts/run_suica_m4_f4_author_axis.py (loaded as f4()):
    build_live_tasks, cell_name_live, seed_suffix_for_mult -- called/read
    unchanged, to build the byte-identical RAW base1x task (the G2 gate
    anchor).
  - From scripts/run_suica_m4_f5_gauge_validity.py (loaded as f5()):
    run_truth_sweep_world (called DIRECTLY, unchanged, for the RAW base1x
    gate-anchor cells -- this IS M4-F4/M4-F5's own computation, nothing new);
    field_from_vectors (the shared featurize -> project -> field helper,
    reused unchanged for the new spread cells too);
    generate_truth_vectors_long (Truth Variant B -- reused COMPLETELY
    UNCHANGED for the spread cells: Part 0.6 below explains why Variant B,
    which resamples the AR(1) state over T_LARGE fresh synthetic occasions
    independent of the observed panel's own occasion layout, does not need
    to know about block/gap structure at all); T_LARGE_PRIMARY,
    TRUTH_CHUNK_SIZE, G4_TOLERANCE -- the same registered constants.

NEW in this script (nothing above is reimplemented):
  - generate_world_spread / generate_truth_vectors_exact_spread: the
    block+gap occasion generator and its noise-free Truth-Variant-A
    counterpart (Part 0.5) -- needed because, unlike Variant B, both the live
    world and Variant A must be aware of exactly which occasions were
    observed, and the existing generator family has no gap concept: its
    AR(1) state x always evolves one step per OBSERVED event, never skips
    steps for an unobserved occasion (Part 0.5's central technical finding).
  - block_layout / block_occasion_labels / block_boundary_label_pairs: the
    uniform (same for every author, Part 0.4) block+gap occasion-index
    arithmetic.
  - common_layout: the M_COMMON=8 uniform per-author event floor (Part 0.4)
    that keeps every one of the panel's 985 authors while giving every
    author IDENTICAL block boundaries -- required for the shared-occasion
    cross-author correlation mechanism to survive block spreading at all.
  - run_spread_sweep_world: the per-world engine for the b1/b2/b4/b8
    (COMMON-budget) cells -- a disclosed structural near-duplicate of
    f5().run_truth_sweep_world (same pattern f5() itself used relative to
    f3().run_sweep_world), substituting generate_world_spread for
    f2().generate_world_composed and generate_truth_vectors_exact_spread for
    f5().generate_truth_vectors_exact, calling every other primitive
    (featurize_panel, calibrate_d0_soft, resolved_contexts, half_indices,
    project_soft, deployed_soft_field, field_agreement,
    generate_truth_vectors_long, field_from_vectors) unchanged.
  - Gates G2 (continuity, new comparison target), G5 (decorrelation, wholly
    new). G1/G3/G4 are direct calls into the prior legs' own gate functions.
  - The adjudication code (leans a/b/c, the pivot) and the two-tier B=1
    resolution (Part 0.2).

Stages (resumable, artifacts under results/m4_f6_occasion_spread/):
  --stage anchor       the RAW base1x_shared_k05/k10 gate-anchor cells (G2's
                        comparison target; f5().run_truth_sweep_world,
                        unchanged, on M4-F4's own byte-identical task)
  --stage sweep        the 8 adjudicated b{1,2,4,8}_shared_k{05,10} cells
                        (COMMON M_COMMON=8 budget; --block-counts/--kappas
                        select a subset for chunked execution)
  --stage gates         G1-G5, writes gates.json, STOPS on any failure;
                        requires anchor+sweep cells to already exist
  --stage finalize      adjudication + decision.json + cells.csv
  --stage all           anchor + sweep + gates + finalize
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
MASTER_SEED = 20260802  # exactly M4-F1's/.../M4-F5's own MASTER_SEED.
DRAWS = 20
WORLDS_PER_CELL = 8
MIN_RETAINED_EVENTS = 8  # the deployed gauge's own split-half retention floor.

# --- Part 0.4 (report): the uniform common-budget floor. ---------------
# M_COMMON = 8 = the panel-wide MINIMUM raw per-author event count (base1x,
# ALL 985 authors across D0/D1/D2 -- verified in Part 0.4 of the report
# BEFORE compute). Applying the SAME constant to every author (not a
# per-author floor-to-nearest-multiple, which would give DIFFERENT block
# sizes for different raw counts and break cross-author occasion-label
# alignment -- Part 0.4's central design finding) keeps every one of the 565
# D1/D2-eligible authors retained while giving EVERY author IDENTICAL block
# boundaries at every swept B.
M_COMMON = 8

# --- Part 0.3 (report): the inter-block gap, derived from the world's own
# phi range BEFORE any compute. ---------------------------------------------
# Calibrated knobs (results/m4_f1_panel_sizing/calibration_record.json):
# phi_lo=.20, phi_hi=.80. The AR(1) state x is stationary with
# corr(x_t, x_{t+h}) = phi^h; the worst case (slowest-decorrelating) author
# has phi=phi_hi=.80. block_occasion_labels' own arithmetic (below) puts
# GAP+1 occasion-label STEPS between the last label of one block and the
# first label of the next (a discrete-indexing +1, not tunable away).
# GAP=40 -> label step 41 -> worst-case theoretical autocorrelation
# 0.8**41 = 1.065e-4 -- roughly four orders of magnitude below the smallest
# per-cell SE measured anywhere in this line at comparable panel scale
# (M4-F5's base1x agreement_se ~ .0017-.0026; a single-world G5 correlation
# estimate pooling n*(B-1)*k >= 985*1*48=47,280 (author,factor) pairs at
# B=2 alone has an intrinsic sampling SE of order 1/sqrt(47280)~=.0046,
# itself ~43x the theoretical correlation). GAP is held FIXED across every
# swept B (one registered constant, verified by G5, not tuned per B).
GAP = 40

OUT = ROOT / "results" / "m4_f6_occasion_spread"
F1_OUT = ROOT / "results" / "m4_f1_panel_sizing"
F5_OUT = ROOT / "results" / "m4_f5_gauge_validity"
REF_PATH = F1_OUT / "realtext_panel_reference.json"
F1_CELLS_CSV = F1_OUT / "cells.csv"
F1_CALIBRATION = F1_OUT / "calibration_record.json"
F5_CELLS_CSV = F5_OUT / "cells.csv"

DESIGN = "shared"
BLOCK_COUNTS = [1, 2, 4, 8]
KAPPAS = [("k05", 0.5), ("k10", 1.0)]
PRIMARY_KAPPA_TAG = "k10"
CONTEXT_KAPPA_TAG = "k05"
G4_TOLERANCE = 1e-9  # identical to M4-F5's own constant.


def _load_script(name: str) -> Any:
    """Copied verbatim from M4-F3's/M4-F4's/M4-F5's own Part-0.11-style fix
    (register sys.modules[mod_name]=module BEFORE exec_module, so a nested
    ProcessPoolExecutor.map against a function defined in a
    dynamically-loaded module can pickle that function by reference). Zero
    edits to run_suica_m4_f1_panel_sizing.py, run_suica_m4_f2_composition.py,
    run_suica_m4_f3_composition_scaling.py, run_suica_m4_f4_author_axis.py,
    or run_suica_m4_f5_gauge_validity.py themselves."""
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


# ---------------------------------------------------------------------------
# Part 0.4 -- the uniform common-budget layout.

def common_layout(reference: dict[str, Any]) -> tuple[list[str], list[str], list[str], list[int], list[int]]:
    """base1x layout (author_mult=1, event_mult=1), every author's count
    replaced by the SAME constant M_COMMON (Part 0.4). Verified (not merely
    assumed) that M_COMMON does not exceed the panel's own minimum raw count,
    so no author is excluded."""
    author_ids, contexts, splits, raw_counts = f1().build_layout(reference, 1, 1)
    if min(raw_counts) < M_COMMON:
        raise AssertionError(
            f"M_COMMON={M_COMMON} exceeds the panel's own minimum raw count {min(raw_counts)}"
        )
    common_counts = [M_COMMON] * len(raw_counts)
    return author_ids, contexts, splits, common_counts, raw_counts


# ---------------------------------------------------------------------------
# Part 0.5 -- the block+gap occasion generator (the ONLY new generator
# mechanism this leg introduces).

def block_layout(m_common: int, block_count: int) -> tuple[int, int]:
    """block size s and block_count; asserts exact divisibility (Part 0.4:
    'each author's events are divided EQUALLY among B blocks' -- exact, not
    near-equal)."""
    if m_common % block_count != 0:
        raise ValueError(f"m_common={m_common} not divisible by block_count={block_count}")
    return m_common // block_count, block_count


def block_occasion_labels(m_common: int, block_count: int, gap: int) -> np.ndarray:
    """Uniform block+gap occasion labels, IDENTICAL for every author (Part
    0.4: uniform block boundaries preserve the cross-author occasion-label
    ALIGNMENT the 'shared' design's cross-author correlation mechanism
    depends on -- a per-author floor-to-nearest-multiple would give
    DIFFERENT block sizes, hence different absolute label values, for
    authors of different raw counts, breaking that alignment for every block
    but the first). block_count=1 degenerates to plain arange(m_common),
    matching 'shared' mode's own occasion_labels exactly (no gap needed with
    only one block)."""
    s, b = block_layout(m_common, block_count)
    labels = np.empty(m_common, dtype=np.int64)
    for blk in range(b):
        start = blk * (s + gap)
        labels[blk * s:(blk + 1) * s] = np.arange(start, start + s)
    return labels


def block_boundary_label_pairs(m_common: int, block_count: int, gap: int) -> list[tuple[int, int]]:
    """(last occasion-label of block b, first occasion-label of block b+1)
    for b=0..block_count-2 -- G5's own diagnostic positions. Empty for
    block_count=1 (nothing to decorrelate with only one block)."""
    s, b = block_layout(m_common, block_count)
    return [(blk * (s + gap) + s - 1, (blk + 1) * (s + gap)) for blk in range(b - 1)]


def _draw_common_state(n: int, knobs: dict[str, Any], rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """loadings, z, phi -- the FIRST rng draws, IDENTICAL prefix (in form) to
    f1().generate_world's / f2().generate_world_composed's own opening
    draws. Shared by generate_world_spread and
    generate_truth_vectors_exact_spread so the two functions replay
    BIT-IDENTICALLY given the same world_seed (Part 0.5's own reuse
    discipline, mirroring how M4-F5's generate_truth_vectors_exact replays
    generate_world_composed's opening draws)."""
    k = int(knobs["k"])
    rho = float(knobs["rho"])
    loadings = _orthonormal_loadings(rng, 64, k)
    z = rng.normal(size=(n, k))
    zeta = rng.normal(size=(n, k))
    logits = rho * z + math.sqrt(max(0.0, 1.0 - rho**2)) * zeta
    phi_lo, phi_hi = float(knobs["phi_lo"]), float(knobs["phi_hi"])
    phi = phi_lo + (phi_hi - phi_lo) / (1.0 + np.exp(-logits))
    return loadings, z, phi


def _draw_ar1_span(n: int, k: int, phi: np.ndarray, t_span: int, rng: np.random.Generator) -> np.ndarray:
    """The AR(1) state x drawn over the FULL occasion-time axis t=0..t_span-1
    (including gap positions never observed by any author) -- the technical
    change this leg's generator makes relative to every prior leg's own
    generator, where x always evolved one step per OBSERVED event."""
    x = np.empty((n, t_span, k), dtype=float)
    x[:, 0] = rng.normal(size=(n, k))
    innovation_scale = np.sqrt(1.0 - phi**2)
    for t in range(1, t_span):
        x[:, t] = phi * x[:, t - 1] + innovation_scale * rng.normal(size=(n, k))
    return x


def generate_world_spread(
    counts: list[int],
    contexts: list[str],
    knobs: dict[str, Any],
    kappa: float,
    block_count: int,
    gap: int,
    world_seed: int,
) -> tuple[list[np.ndarray], dict[str, Any]]:
    """M4F1RelationWorld's kappa>0 mechanism, extended so the AR(1) state x
    evolves over the FULL occasion-time axis (block positions + gaps),
    observed only at the block positions. Returns (vectors_list,
    diagnostic), where diagnostic carries the RAW (pre-kappa-blend) x state
    at every adjacent block-boundary pair -- G5's own input, computed as a
    free byproduct of this function's own x array rather than a separate
    replay.

    Requires uniform counts (every author == m_common), per Part 0.4 --
    asserted, not silently handled, since a heterogeneous-count input would
    silently break cross-author occasion-label alignment."""
    n = len(counts)
    m_common = counts[0]
    if any(c != m_common for c in counts):
        raise ValueError("generate_world_spread requires uniform per-author counts (Part 0.4)")
    s, _ = block_layout(m_common, block_count)
    t_span = block_count * s + (block_count - 1) * gap
    rng = np.random.default_rng(world_seed)
    k = int(knobs["k"])
    w_mu, w_x, w_e = float(knobs["w_mu"]), float(knobs["w_x"]), float(knobs["w_e"])
    if abs(w_mu + w_x + w_e - 1.0) > 1e-9:
        raise ValueError("variance shares must sum to 1")
    g = np.linspace(0.85, 0.55, k)
    a = math.sqrt(2.0 / float(np.sum(g**2)))
    sigma_iso = math.sqrt(2.0 / 64.0)
    loadings, z, phi = _draw_common_state(n, knobs, rng)
    x = _draw_ar1_span(n, k, phi, t_span, rng)
    noise = rng.normal(size=(n, m_common, 64))
    mean_part = math.sqrt(w_mu) * a * ((z * g) @ loadings.T)

    labels = block_occasion_labels(m_common, block_count, gap)  # (m_common,), SAME for every author.
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
    blended_x = math.sqrt(max(0.0, 1.0 - kappa_f)) * x_at_labels + math.sqrt(kappa_f) * shock_x
    state_part = math.sqrt(w_x) * a * ((blended_x * g) @ loadings.T)
    events = mean_part[:, None, :] + state_part + math.sqrt(w_e) * sigma_iso * noise
    vectors_list = [events[i] for i in range(n)]

    boundary_pairs = block_boundary_label_pairs(m_common, block_count, gap)
    if boundary_pairs:
        x_before = np.stack([x[:, occ_b, :] for occ_b, _ in boundary_pairs], axis=1)  # (n, B-1, k)
        x_after = np.stack([x[:, occ_a, :] for _, occ_a in boundary_pairs], axis=1)
    else:
        x_before = np.empty((n, 0, k), dtype=float)
        x_after = np.empty((n, 0, k), dtype=float)
    diagnostic = {
        "x_before": x_before, "x_after": x_after,
        "t_span": t_span, "gap": gap, "block_size": s, "n_boundary_pairs": len(boundary_pairs),
    }
    del x
    return vectors_list, diagnostic


def generate_truth_vectors_exact_spread(
    counts: list[int],
    contexts: list[str],
    knobs: dict[str, Any],
    kappa: float,
    block_count: int,
    gap: int,
    world_seed: int,
    retained_idx: np.ndarray,
) -> list[np.ndarray]:
    """Truth Variant A under block+gap spreading: bit-identical replay of
    generate_world_spread's own draw sequence (loadings/z/zeta/phi/x
    IDENTICAL by construction -- same helpers, same order, same world_seed),
    omitting the per-event noise term (an unused same-shaped draw is still
    consumed for stream-order-preserving symmetry, mirroring M4-F5's own
    generate_truth_vectors_exact discipline, Part 0.5)."""
    n = len(counts)
    m_common = counts[0]
    if any(c != m_common for c in counts):
        raise ValueError("generate_truth_vectors_exact_spread requires uniform per-author counts (Part 0.4)")
    s, _ = block_layout(m_common, block_count)
    t_span = block_count * s + (block_count - 1) * gap
    rng = np.random.default_rng(world_seed)
    k = int(knobs["k"])
    w_mu, w_x = float(knobs["w_mu"]), float(knobs["w_x"])
    g = np.linspace(0.85, 0.55, k)
    a = math.sqrt(2.0 / float(np.sum(g**2)))
    loadings, z, phi = _draw_common_state(n, knobs, rng)
    x = _draw_ar1_span(n, k, phi, t_span, rng)
    _unused_noise = rng.normal(size=(n, m_common, 64))  # stream-order-preserving symmetry only, never added.
    del _unused_noise
    mean_part = math.sqrt(w_mu) * a * ((z * g) @ loadings.T)

    labels = block_occasion_labels(m_common, block_count, gap)
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
    blended_x = math.sqrt(max(0.0, 1.0 - kappa_f)) * x_at_labels + math.sqrt(kappa_f) * shock_x
    state_part = math.sqrt(w_x) * a * ((blended_x * g) @ loadings.T)
    events_true = mean_part[:, None, :] + state_part  # NOTE: no + sqrt(w_e)*sigma_iso*noise term.
    return [events_true[i] for i in retained_idx]


def g5_world_correlation(x_before: np.ndarray, x_after: np.ndarray) -> dict[str, Any]:
    """Pearson correlation between x_before and x_after, POOLING every
    (author, boundary-pair, factor) triple into ONE correlation per world
    (Part 0.7's registered aggregation) -- these are exchangeable draws
    under the SAME world/gap/phi-distribution, so pooling is the natural
    per-world statistic."""
    n_pairs = int(x_before.size)
    if n_pairs == 0:
        return {"n_pairs": 0, "correlation": None}
    before_flat = x_before.reshape(-1)
    after_flat = x_after.reshape(-1)
    r = float(np.corrcoef(before_flat, after_flat)[0, 1])
    return {"n_pairs": n_pairs, "correlation": r}


def spread_world_seed_for(seed_key: str, world: int, knob_tag: str) -> int:
    """Own salt ('m4f6-spread-world'), distinct from every prior leg's own
    world salt -- a fresh, clearly-namespaced lineage off the same
    MASTER_SEED, since block+gap spreading is a genuinely new generator
    mechanism (not required to reproduce any prior leg's numbers -- only the
    RAW base1x gate-anchor cells, computed via f5().run_truth_sweep_world
    on M4-F4's OWN seed lineage, carry that obligation)."""
    return int(
        v8.stable_bucket(
            f"{MASTER_SEED}-{seed_key}-w{world}-{knob_tag}", salt="m4f6-spread-world", modulus=2**63 - 1
        )
    )


# ---------------------------------------------------------------------------
# The per-world engine for the b1/b2/b4/b8 (COMMON-budget) adjudicated cells:
# a disclosed structural near-duplicate of f5().run_truth_sweep_world (Part
# 0.1), substituting generate_world_spread / generate_truth_vectors_exact_spread
# for f2().generate_world_composed / f5().generate_truth_vectors_exact and
# calling every other primitive (featurize_panel, calibrate_d0_soft,
# resolved_contexts, half_indices, project_soft, deployed_soft_field,
# field_agreement, field_from_vectors, generate_truth_vectors_long) UNCHANGED.

def _prepare_spread_world(task: dict[str, Any]) -> dict[str, Any]:
    spec = f1().load_spec()
    directions = f1()._directions(spec)
    module = f1().e1()
    reference = json.loads(Path(task["ref_path"]).read_text(encoding="utf-8"))
    author_ids, contexts, splits, common_counts, _raw = common_layout(reference)
    corpus = f"m4f6-{task['seed_key']}-w{task['world']}"
    world_seed = spread_world_seed_for(task["seed_key"], task["world"], task["knob_tag"])
    vectors_list, diag = generate_world_spread(
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

    # ---- (A) split-half agreement, IDENTICAL procedure to f5()/f3(). ----
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

    # ---- (C) Truth Variant A (exact, noise-free, spread-aware). ----
    truth_vectors_exact = generate_truth_vectors_exact_spread(
        counts, w["contexts"], task["knobs"], task["kappa"], task["block_count"], task["gap"],
        w["world_seed"], retained_idx,
    )
    field_true_exact = f5().field_from_vectors(
        truth_vectors_exact, retained_ids, retained_ctx, resolved, calibration, spec, directions, corpus, module
    )
    truth_recovery_exact = module.field_agreement(field_est_full, field_true_exact, weights)
    del truth_vectors_exact, field_true_exact
    gc.collect()

    # ---- (D) Truth Variant B (large-sample asymptotic, UNCHANGED -- Part 0.6). ----
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
    g5 = g5_world_correlation(diag["x_before"], diag["x_after"])

    return {
        "banner": BANNER,
        "cell": task["cell"],
        "seed_key": task["seed_key"],
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

def cell_name_spread(block_count: int, kappa_tag: str) -> str:
    return f"b{block_count}_shared_{kappa_tag}"


def build_spread_tasks(
    knobs: dict[str, Any], knob_tag: str, draws: int, block_counts: list[int], kappa_tags: set[str]
) -> list[dict[str, Any]]:
    tasks = []
    for block_count in block_counts:
        for kappa_tag, kappa in KAPPAS:
            if kappa_tag not in kappa_tags:
                continue
            seed_key = f"b{block_count}_{kappa_tag}"
            cell = cell_name_spread(block_count, kappa_tag)
            for world in range(WORLDS_PER_CELL):
                tasks.append(
                    {
                        "cell": cell, "seed_key": seed_key, "world": world,
                        "block_count": block_count, "gap": GAP, "kappa": kappa,
                        "knobs": knobs, "knob_tag": knob_tag, "draws": draws,
                        "ref_path": str(REF_PATH), "budget_label": "f6.0",
                    }
                )
    return tasks


def build_anchor_tasks(knobs: dict[str, Any], knob_tag: str, draws: int, kappa_tags: set[str]) -> list[dict[str, Any]]:
    """The RAW base1x_shared_k05/k10 gate-anchor tasks -- BYTE-IDENTICAL to
    M4-F4's own build_live_tasks(mult=1) (Part 0.2: this is the ONLY way to
    satisfy G2's bit-identical reproduction requirement)."""
    return f4().build_live_tasks(knobs, knob_tag, draws, [1], kappa_tags)


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


def run_anchor(knobs: dict[str, Any], knob_tag: str, workers: int, draws: int, kappa_tags: set[str]) -> None:
    """The RAW base1x gate-anchor cells: DIRECT, unchanged call to
    f5().run_truth_sweep_world on M4-F4's own byte-identical task."""
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = build_anchor_tasks(knobs, knob_tag, draws, kappa_tags)
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
            rows = list(pool.map(f5().run_truth_sweep_world, cell_tasks))
        _write_cell(cell, rows, started, has_g5=False)


def run_sweep(
    knobs: dict[str, Any], knob_tag: str, workers: int, draws: int, block_counts: list[int], kappa_tags: set[str]
) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = build_spread_tasks(knobs, knob_tag, draws, block_counts, kappa_tags)
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


def run_gate_g2() -> dict[str, Any]:
    """Continuity: the RAW base1x_shared_k05/k10 gate-anchor cells (computed
    via f5().run_truth_sweep_world on M4-F4's own byte-identical task)
    reproduce M4-F5's persisted agreement AND both truth-variant values to
    <=1e-12. A mismatch VOIDS the comparison per the registration."""
    pairs = [("base1x_shared_k05", "k05"), ("base1x_shared_k10", "k10")]
    rows = []
    all_match = True
    for cell, kappa_tag in pairs:
        path = OUT / f"cell_{cell}.csv"
        if not path.exists():
            raise AssertionError(f"G2 requires {path} to exist; run --stage anchor first.")
        got = cell_summary(cell)
        target = _read_f5_persisted_row(cell)
        diffs = {
            "agreement_mean": abs(got["agreement_mean"] - target["agreement_mean"]),
            "agreement_se": abs(got["agreement_se"] - target["agreement_se"]),
            "truth_recovery_exact_mean": abs(got["truth_recovery_exact_mean"] - target["truth_recovery_exact_mean"]),
            "truth_recovery_long_mean": abs(got["truth_recovery_long_mean"] - target["truth_recovery_long_mean"]),
            "d0_eff_rank_M_mean": abs(got["d0_eff_rank_M_mean"] - target["d0_eff_rank_M_mean"]),
            "d0_eff_rank_K_mean": abs(got["d0_eff_rank_K_mean"] - target["d0_eff_rank_K_mean"]),
            "n_retained": abs(got["n_retained"] - target["n_retained"]),
        }
        row_pass = bool(all(v <= 1e-12 for k, v in diffs.items() if k != "n_retained") and diffs["n_retained"] == 0)
        all_match = all_match and row_pass
        rows.append({"cell": cell, "target": target, "observed": {k: got[k] for k in target}, "abs_diffs": diffs, "pass": row_pass})
    return {
        "gate": "G2",
        "description": "the RAW base1x_shared_k05/k10 gate-anchor cells (f5().run_truth_sweep_world on "
        "M4-F4's own byte-identical task) reproduce M4-F5's persisted agreement AND both truth-variant "
        "values to <=1e-12 -- a mismatch VOIDS the comparison per the registration",
        "tolerance": 1e-12,
        "rows": rows,
        "pass": bool(all_match),
    }


def run_gate_g4(all_cells: list[str]) -> dict[str, Any]:
    """Truth-path invariance, as M4-F5: two independent routes to the
    identical finite-sample field agree to <=G4_TOLERANCE, for every world of
    every cell (anchor cells included -- they carry this field too, via
    f5().run_truth_sweep_world's own g4_max_diff)."""
    rows = []
    all_pass = True
    for cell in all_cells:
        frame = pd.read_csv(OUT / f"cell_{cell}.csv")
        cell_max = float(frame["g4_max_diff"].max())
        cell_pass = bool(cell_max <= G4_TOLERANCE)
        all_pass = all_pass and cell_pass
        rows.append({"cell": cell, "max_diff": cell_max, "pass": cell_pass})
    return {
        "gate": "G4",
        "description": "truth-path invariance: two independent routes to the identical finite-sample "
        "field agree to <=G4_TOLERANCE, for every world of every cell (matching M4-F5's own check)",
        "tolerance": G4_TOLERANCE,
        "rows": rows,
        "pass": bool(all_pass),
    }


def run_gate_g5(spread_cells: list[str]) -> dict[str, Any]:
    """Decorrelation check (Part 0.7's pre-registered aggregation rule,
    written BEFORE the run): for each of the (block_count, kappa)
    combinations with block_count>=2 (block_count=1 has zero boundary pairs
    -- nothing to check), pool the realized cross-block-boundary correlation
    of the RAW (pre-kappa-blend) AR(1) state x across ALL authors x ALL
    factors x ALL adjacent boundary pairs WITHIN each of the 8 worlds (one
    Pearson correlation per world), then aggregate across the 8 worlds via
    mean/SE (t-test vs 0, df=7) -- a PER-CELL rule (not a trend-across-B
    rule: the fixed GAP is designed to decorrelate at EVERY block_count
    independently, so there is no reason to expect the residual to trend
    with B). G5 PASSES iff |t|<2.0 at EVERY ONE of the tested cells,
    mirroring this line's own established 'indistinguishable from zero' bar
    (f1().cell_summary's 'rise' threshold, applied in the opposite
    direction: NOT crossing the bar, rather than crossing it). x's own
    autocorrelation does not depend on kappa by construction (kappa only
    enters the SUBSEQUENT blending step), so both kappas are expected to
    agree; both are checked anyway under this leg's own convention of
    independent draws per (block_count, kappa) cell, for thoroughness. A
    |t|>=2.0 at ANY tested cell VOIDS the leg per the registration."""
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
        "note": "supplementary context only, NOT the gating statistic (Part 0.7's registered rule is "
        "per-cell |t|<2.0 at EVERY tested cell)",
    }
    return {
        "gate": "G5",
        "description": "decorrelation check: the realized cross-block-boundary autocorrelation of the "
        "AR(1) state x must be indistinguishable from zero at every block_count>=2 cell (Part 0.7's "
        "pre-registered per-cell |t|<2.0 aggregation rule)",
        "rows": rows,
        "pooled_context": pooled,
        "pass": bool(all_pass),
    }


def run_gates(knobs: dict[str, Any], knob_tag: str, workers: int, spread_cells: list[str], anchor_cells: list[str]) -> dict[str, Any]:
    g1 = run_gate_g1(knobs, knob_tag, workers)
    g3 = run_gate_g3()
    g2 = run_gate_g2()
    g4 = run_gate_g4(anchor_cells + spread_cells)
    g5 = run_gate_g5(spread_cells)
    gates = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "knobs": knobs,
        "knob_tag": knob_tag,
        "gap": GAP,
        "m_common": M_COMMON,
        "G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5,
        "all_pass": bool(g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"] and g5["pass"]),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: v["pass"] for k, v in gates.items() if isinstance(v, dict) and "pass" in v}, indent=2))
    if not g5["pass"]:
        raise AssertionError(
            "G5 (decorrelation check) FAILED -- blocks remain correlated at the chosen gap. Per the "
            "registration this VOIDS the leg: the sweep is a relabelled within-window sweep. See "
            "results/m4_f6_occasion_spread/gates.json. Do NOT increase the gap and re-run silently; "
            "write the void outcome."
        )
    if not gates["all_pass"]:
        raise AssertionError("Gate(s) failed; see results/m4_f6_occasion_spread/gates.json.")
    return gates


# ---------------------------------------------------------------------------
# Adjudication -- exactly the registered leans/pivot, no more.

def _paired_ci(diffs: np.ndarray) -> dict[str, Any]:
    """Identical construction to f2()._paired_ci."""
    n = len(diffs)
    mean = float(diffs.mean())
    sd = float(diffs.std(ddof=1))
    se = sd / math.sqrt(n)
    t_stat = mean / se if se > 0 else float("inf")
    t_crit = float(_scipy_stats.t.ppf(0.975, df=n - 1))
    return {
        "n": int(n), "mean": mean, "sd": sd, "se": se, "t_stat": float(t_stat), "t_crit_95": t_crit,
        "ci95_low": float(mean - t_crit * se), "ci95_high": float(mean + t_crit * se),
        "ci_excludes_zero_positive": bool(mean - t_crit * se > 0),
        "ci_includes_zero": bool(mean - t_crit * se <= 0 <= mean + t_crit * se),
    }


def adjudicate(summaries: dict[str, dict[str, Any]]) -> dict[str, Any]:
    b1 = summaries[cell_name_spread(1, PRIMARY_KAPPA_TAG)]
    b8 = summaries[cell_name_spread(8, PRIMARY_KAPPA_TAG)]

    diff_long = np.asarray(b8["truth_long_world_values"], dtype=float) - np.asarray(b1["truth_long_world_values"], dtype=float)
    diff_exact = np.asarray(b8["truth_exact_world_values"], dtype=float) - np.asarray(b1["truth_exact_world_values"], dtype=float)
    ci_long = _paired_ci(diff_long)
    ci_exact = _paired_ci(diff_exact)

    lean_a_hold = bool(ci_long["ci_excludes_zero_positive"])
    lean_a = {
        "lean": "a", "rule": "long-window truth recovery (Variant B) RISES with B at fixed budget, "
        "paired-by-world CI excluding 0 from B=1 to B=8, kappa=1.0 primary",
        "paired_diff_B8_minus_B1": ci_long,
        "verdict": "HOLD" if lean_a_hold else "MISS",
    }

    half_of_b_gain = 0.5 * ci_long["mean"]
    lean_b_hold = bool(ci_exact["mean"] <= half_of_b_gain)
    lean_b = {
        "lean": "b", "rule": "same-occasion truth recovery (Variant A) does NOT rise with B by more than "
        "half the long-window (Variant B) gain -- point-estimate comparison of the two paired diffs",
        "paired_diff_A_B8_minus_B1": ci_exact,
        "half_of_lean_a_gain": half_of_b_gain,
        "verdict": "HOLD" if lean_b_hold else "MISS",
    }
    if not lean_a_hold:
        lean_b["caveat"] = (
            "lean (a) itself MISSED (or the gain is non-positive) -- 'half the long-window gain' is not "
            "a meaningful positive target in that case; the point-estimate rule is still applied exactly "
            "as registered and reported plainly, but this context matters for interpretation."
        )

    kappa10_cells = [summaries[cell_name_spread(b, PRIMARY_KAPPA_TAG)] for b in BLOCK_COUNTS]
    agreements = {c["block_count"]: c["agreement_mean"] for c in kappa10_cells}
    ref = agreements[1]
    band = 0.20 * abs(ref)
    per_b_within = {b: bool(abs(agreements[b] - ref) <= band) for b in BLOCK_COUNTS}
    lean_c_hold = bool(all(per_b_within.values()))
    max_val, min_val = max(agreements.values()), min(agreements.values())
    lean_c = {
        "lean": "c", "rule": "split-half agreement is approximately B-invariant: every B's agreement "
        "within +/-20% of the B=1 value, kappa=1.0 primary",
        "agreement_by_block_count": agreements,
        "b1_reference": ref,
        "band_abs": band,
        "max_minus_min": float(max_val - min_val),
        "per_b_within_band": per_b_within,
        "verdict": "HOLD" if lean_c_hold else "MISS",
    }

    pivot_fires = bool(ci_long["ci_includes_zero"] or not ci_long["ci_excludes_zero_positive"])
    pivot = {
        "registered_rule": "long-window truth recovery does not rise with B (paired CI includes 0)",
        "paired_diff_B8_minus_B1_ci95": [ci_long["ci95_low"], ci_long["ci95_high"]],
        "ci_includes_zero": ci_long["ci_includes_zero"],
        "fires": pivot_fires,
    }

    kappa05_context = {
        "note": "kappa=0.5 is the registered robustness axis; it gates no lean or the pivot (all three "
        "leans and the pivot are specified at kappa=1.0 primary, mirroring M4-F3's/M4-F4's own treatment "
        "of their non-decisive kappa) and is reported for context.",
        "cells": {b: {k: v for k, v in summaries[cell_name_spread(b, CONTEXT_KAPPA_TAG)].items()
                       if k not in ("world_seeds", "world_values", "truth_exact_world_values",
                                    "truth_long_world_values", "g5_world_values")}
                  for b in BLOCK_COUNTS},
    }

    if pivot_fires:
        verdict = "OCCASION_SPREAD_NOT_THE_LEVER_TRAIT_LEVEL_UNCERTIFIABLE_ON_ALL_THREE_AXES"
    elif lean_a_hold and lean_b_hold and lean_c_hold:
        verdict = "OCCASION_SPREAD_CERTIFIES_TRAIT_LEVEL_OBJECT"
    else:
        verdict = "MIXED_SEE_LEAN_ADJUDICATION"

    full_table = [
        {
            "block_count": b, "kappa_tag": kt,
            "agreement_mean": summaries[cell_name_spread(b, kt)]["agreement_mean"],
            "agreement_se": summaries[cell_name_spread(b, kt)]["agreement_se"],
            "truth_recovery_exact_mean": summaries[cell_name_spread(b, kt)]["truth_recovery_exact_mean"],
            "truth_recovery_exact_se": summaries[cell_name_spread(b, kt)]["truth_recovery_exact_se"],
            "truth_recovery_long_mean": summaries[cell_name_spread(b, kt)]["truth_recovery_long_mean"],
            "truth_recovery_long_se": summaries[cell_name_spread(b, kt)]["truth_recovery_long_se"],
        }
        for b in BLOCK_COUNTS for kt, _ in KAPPAS
    ]

    return {
        "lean_a": lean_a, "lean_b": lean_b, "lean_c": lean_c,
        "pivot": pivot, "verdict": verdict,
        "kappa_0_5_context": kappa05_context,
        "full_b_vs_metrics_table": full_table,
    }


# ---------------------------------------------------------------------------

def run_finalize() -> None:
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    spread_cells = [cell_name_spread(b, kt) for b in BLOCK_COUNTS for kt, _ in KAPPAS]
    anchor_cells = ["base1x_shared_k05", "base1x_shared_k10"]

    summaries = {cell: cell_summary(cell) for cell in spread_cells}
    anchor_summaries = {cell: cell_summary(cell) for cell in anchor_cells}

    adjudication = adjudicate(summaries)

    all_rows = []
    for cell, s in {**summaries, **anchor_summaries}.items():
        role = "gate_anchor_raw_budget" if cell in anchor_cells else "adjudicated_common_budget"
        row = {k: v for k, v in s.items() if k not in (
            "world_seeds", "world_values", "truth_exact_world_values",
            "truth_long_world_values", "g5_world_values"
        )}
        row["role"] = role
        all_rows.append(row)
    pd.DataFrame(all_rows).to_csv(OUT / "cells.csv", index=False)

    decision = {
        "experiment": "M4-F6_occasion_spread",
        "banner": BANNER,
        "tier": "EXPLORATORY",
        "registered_spec": "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md#M4-F6-registration",
        "part0_registered_in": "reports/SUICA_M4_F6_OCCASION_SPREAD_REPORT.md Part 0 (before run)",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "worlds_per_cell": WORLDS_PER_CELL,
        "draws_per_world": DRAWS,
        "gap": GAP,
        "m_common": M_COMMON,
        "base_cell": "base1x (author_mult=1, event_mult=1)",
        "gates": {k: (v["pass"] if isinstance(v, dict) and "pass" in v else v) for k, v in gates.items()},
        "gates_all_pass": gates["all_pass"],
        "adjudication": adjudication,
        "label_free": True,
        "claim_boundary": (
            "Synthetic occasion-spread finding in a world calibrated to the opened PANDORA D-panel "
            "regime; licenses a finding about whether spreading observation across widely-separated "
            "occasion blocks certifies a trait-like object under this synthetic instrument. No claim "
            "about the real relation field's content, personality, emotion, diagnosis, or any individual."
        ),
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(adjudication, indent=2, default=str))


# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["anchor", "sweep", "gates", "finalize", "all"], default="all")
    parser.add_argument("--workers", type=int, default=max(2, min(8, (os.cpu_count() or 4) - 2)))
    parser.add_argument("--draws", type=int, default=DRAWS)
    parser.add_argument("--block-counts", type=str, default="1,2,4,8")
    parser.add_argument("--kappas", type=str, default="k05,k10")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if not REF_PATH.exists():
        raise AssertionError(f"{REF_PATH} missing (M4-F1 artifact required, read-only).")
    if not F1_CELLS_CSV.exists():
        raise AssertionError(f"{F1_CELLS_CSV} missing (M4-F1 artifact required, read-only).")
    if not F5_CELLS_CSV.exists():
        raise AssertionError(f"{F5_CELLS_CSV} missing (M4-F5 artifact required, read-only).")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

    f1_cal = json.loads(F1_CALIBRATION.read_text(encoding="utf-8"))
    if f1_cal["status"] != "CALIBRATED":
        raise AssertionError("M4-F1 calibration_record.json is not CALIBRATED.")
    knobs = f1_cal["selected"]["knobs"]
    knob_tag = f1().knob_tag(knobs)

    block_counts = [int(x) for x in args.block_counts.split(",") if x]
    kappa_tags = {x for x in args.kappas.split(",") if x}

    if args.stage in ("anchor", "all"):
        run_anchor(knobs, knob_tag, args.workers, args.draws, kappa_tags)
    if args.stage in ("sweep", "all"):
        run_sweep(knobs, knob_tag, args.workers, args.draws, block_counts, kappa_tags)
    if args.stage in ("gates", "all"):
        spread_cells = [cell_name_spread(b, kt) for b in BLOCK_COUNTS for kt, _ in KAPPAS]
        anchor_cells = ["base1x_shared_k05", "base1x_shared_k10"]
        run_gates(knobs, knob_tag, args.workers, spread_cells, anchor_cells)
    if args.stage in ("finalize", "all"):
        run_finalize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
