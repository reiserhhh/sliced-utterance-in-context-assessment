#!/usr/bin/env python3
"""M4-F2 -- the D3 composition law (shared-occasion vs free-response design x
kappa; within-author cross-context pairing Q in {2,4}), at a FIXED total event
budget.

Registered spec: docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md section
"M4-F2 registration (2026-08-03, BEFORE run)". Part 0 register-notes
(operationalizations for everything the registration left as an implementation
choice) are in reports/SUICA_M4_F2_COMPOSITION_REPORT.md Part 0, written BEFORE
this script's compute stages were ever run.

World: M4F1RelationWorld (scripts/run_suica_m4_f1_panel_sizing.py), extended by
ONE new mechanism -- a context-occasion common shock s_{c,t} ~ N(0, I_k),
entered at weight sqrt(kappa) in place of that same weight's worth of the
author's own state contribution (the state term scaled by sqrt(1-kappa), so
total variance is preserved exactly). kappa<=0 delegates to the verbatim
M4-F1 generate_world (bit-for-bit; this is gate G1/G4's foundation).

Reused verbatim, no reimplementation of the gauge (per the registration's
explicit instruction): load_spec, _directions, e1(), featurize_panel,
half_indices, build_layout, generate_world, knob_tag, marginal_features_batch,
transition_features_batch -- all imported from
scripts/run_suica_m4_f1_panel_sizing.py, which itself imports the M4-E1
calibrate_d0_soft / project_soft / deployed_soft_field / field_agreement /
resolved_contexts / split_half_frames verbatim.

Stages (resumable, artifacts under results/m4_f2_composition/):
  --stage gates     G1-G4, writes gates.json, STOPS if G4 fails
  --stage sweep     the 6 adjudicated cells (axis1_cell_<id>.csv etc.)
  --stage finalize  adjudication, decision.json
  --stage all       everything in order
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
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import suica_core.v8_realtext_relation_field as v8  # noqa: E402
from suica_core.v8_context_relation_field import _orthonormal_loadings  # noqa: E402

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"
MASTER_SEED = 20260802  # exactly M4-F1's MASTER_SEED, per registration.
DRAWS = 20
WORLDS_PER_CELL = 8
MIN_FEATURIZABLE = 4  # featurize_panel needs each alternating replicate >=2.
MIN_RETAINED_EVENTS = 8  # the deployed gauge's own split-half retention floor.
OUT = ROOT / "results" / "m4_f2_composition"
F1_OUT = ROOT / "results" / "m4_f1_panel_sizing"
REF_PATH = F1_OUT / "realtext_panel_reference.json"
F1_CELLS_CSV = F1_OUT / "cells.csv"
F1_CALIBRATION = F1_OUT / "calibration_record.json"


def _load_script(name: str) -> Any:
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_F1 = None


def f1() -> Any:
    """The M4-F1 script module (verbatim generator/gauge machinery, reused)."""
    global _F1
    if _F1 is None:
        _F1 = _load_script("run_suica_m4_f1_panel_sizing.py")
    return _F1


# ---------------------------------------------------------------------------
# The context-occasion common shock (Part 0's extension; the ONLY change to
# the generator). kappa<=0 delegates to f1().generate_world bit-for-bit.

def occasion_labels(counts: list[int], mode: str) -> list[np.ndarray]:
    """Per-author occasion-index arrays (length counts[i]) for shock lookup.

    'shared': occasion label = local sequential index t (0..counts[i]-1) --
    every author in a context is literally on the same occasion grid.
    'free': occasion label = a GLOBALLY UNIQUE flat index (running offset
    across all authors in author-then-t order) -- guarantees zero occasion
    collision between any two distinct (author, t) pairs, an exact
    (not merely low-probability) realization of "each author draws their own
    idiosyncratic occasions" (Part 0 register-note: this operationalizes
    "free" as the limit of fully unshared occasions rather than picking an
    arbitrary finite occasion-universe size).
    """
    if mode == "shared":
        return [np.arange(m) for m in counts]
    if mode == "free":
        labels = []
        offset = 0
        for m in counts:
            labels.append(offset + np.arange(m))
            offset += m
        return labels
    raise ValueError(f"unknown occasion_mode {mode!r}")


def shock_vector(world_seed: int, context: str, occasion: int, k: int) -> np.ndarray:
    """s_{c,t} ~ N(0, I_k): one fresh draw per (world, context, occasion)."""
    seed = v8.stable_bucket(
        f"{world_seed}-{context}-{occasion}", salt="m4f2-shock", modulus=2**63 - 1
    )
    return np.random.default_rng(seed).normal(size=k)


def generate_world_composed(
    counts: list[int],
    contexts: list[str] | None,
    knobs: dict[str, Any],
    kappa: float,
    occasion_mode: str,
    world_seed: int,
) -> list[np.ndarray]:
    """M4-F1's generate_world extended by the context-occasion shock.

    kappa<=0 returns f1().generate_world(counts, knobs, world_seed) UNCHANGED
    (literal delegation, not a re-derivation) -- this is what makes gates
    G1/G4 bit-for-bit guarantees rather than numerical-tolerance claims. The
    shock draws use a seed derived independently of the module-level `rng`
    object that produces loadings/z/zeta/x/noise, so at kappa>0 those
    quantities are STILL identical, for a given world_seed, to what kappa=0
    would produce -- only the state term's blend changes.
    """
    if kappa <= 0.0:
        return f1().generate_world(counts, knobs, world_seed)
    if contexts is None:
        raise ValueError("contexts required when kappa > 0")
    rng = np.random.default_rng(world_seed)
    k = int(knobs["k"])
    rho = float(knobs["rho"])
    w_mu, w_x, w_e = (
        float(knobs["w_mu"]),
        float(knobs["w_x"]),
        float(knobs["w_e"]),
    )
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

    labels = occasion_labels(counts, occasion_mode)
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
                vector = shock_vector(world_seed, context, occ, k)
                cache[key] = vector
            shock_x[i, t] = vector

    blended_x = math.sqrt(max(0.0, 1.0 - kappa_f)) * x + math.sqrt(kappa_f) * shock_x
    state_part = math.sqrt(w_x) * a * ((blended_x * g) @ loadings.T)
    events = mean_part[:, None, :] + state_part + math.sqrt(w_e) * sigma_iso * noise
    return [events[i, : counts[i]] for i in range(n)]


# ---------------------------------------------------------------------------
# Layouts: the common (largest-common-multiple-of-4) budget, and the crossed
# pseudo-author expansion (Part 0.2/0.3 register-notes).

def build_layout_common(
    reference: dict[str, Any]
) -> tuple[list[str], list[str], list[str], list[int], list[int]]:
    """f1().build_layout(reference,1,1), counts floored to a multiple of 4.

    Register-note (resolves "distribute remainders deterministically ... use
    the largest common budget across cells"): the largest per-author budget
    simultaneously exact for Q in {2,4} is a multiple of 4. Applied UNIFORMLY
    to all six adjudicated cells (free/shared AND crossed), this makes G2
    (exact total-event equality across every cell) hold by construction, at
    the cost of uniformly dropping m_i mod 4 events per author (0 or 2 events;
    only m in {10,14} are touched, since {8,12,16} are already multiples of
    4). This is NOT applied to the G1 gate computation, which reproduces
    M4-F1's base1x on its own RAW (untruncated) layout.
    """
    author_ids, contexts, splits, raw_counts = f1().build_layout(reference, 1, 1)
    common_counts = [4 * (m // 4) for m in raw_counts]
    return author_ids, contexts, splits, common_counts, raw_counts


def assigned_contexts(home: str, q_count: int, contexts_sorted: list[str]) -> list[str]:
    """Deterministic Q-context rotation starting at the author's home context."""
    idx = contexts_sorted.index(home)
    n_ctx = len(contexts_sorted)
    return [contexts_sorted[(idx + j) % n_ctx] for j in range(q_count)]


def build_crossed_layout(reference: dict[str, Any], q_count: int) -> dict[str, Any]:
    """Each real author -> Q pseudo-author rows, contiguous slices of their
    own m^common-length event stream, tagged with Q rotated context labels.
    """
    author_ids, contexts, splits, common_counts, raw_counts = build_layout_common(
        reference
    )
    contexts_sorted = sorted(set(contexts))
    pseudo_rows: list[dict[str, Any]] = []
    for i, author in enumerate(author_ids):
        m_common = common_counts[i]
        s = m_common // q_count  # exact: m_common is a multiple of 4, hence of Q.
        assigned = assigned_contexts(contexts[i], q_count, contexts_sorted)
        for qi in range(q_count):
            pseudo_rows.append(
                {
                    "pseudo_author_id": f"{author}::x{qi}",
                    "real_author_id": author,
                    "slice_index": qi,
                    "context": assigned[qi],
                    "split": splits[i],
                    "slice_size": s,
                    "slice_start": qi * s,
                    "slice_end": (qi + 1) * s,
                }
            )
    return {
        "author_ids": author_ids,
        "contexts": contexts,
        "splits": splits,
        "common_counts": common_counts,
        "raw_counts": raw_counts,
        "pseudo_rows": pseudo_rows,
        "q": q_count,
        "contexts_sorted": contexts_sorted,
    }


# ---------------------------------------------------------------------------
# Axis-1 (free/shared x kappa) per-world computation: a close structural
# adaptation of f1().run_world, generalized over kappa/occasion_mode and over
# the seed scaffold (so the SAME function can also serve as gate G1's engine
# when pointed at M4-F1's exact seed recipe).

def run_axis1_world(task: dict[str, Any]) -> dict[str, Any]:
    started = time.time()
    spec = f1().load_spec()
    directions = f1()._directions(spec)
    module = f1().e1()
    reference = json.loads(Path(task["ref_path"]).read_text(encoding="utf-8"))
    if task["layout"] == "raw":
        author_ids, contexts, splits, counts = f1().build_layout(reference, 1, 1)
    else:
        author_ids, contexts, splits, counts, _raw = build_layout_common(reference)

    corpus = f"{task['corpus_tag']}-{task['seed_group']}-w{task['world']}"
    world_seed = v8.stable_bucket(
        f"{MASTER_SEED}-{task['seed_group']}-w{task['world']}-{task['knob_tag']}",
        salt=task["world_salt"],
        modulus=2**63 - 1,
    )
    vectors_list = generate_world_composed(
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
            fields.append(
                module.deployed_soft_field(projected, retained_ctx, resolved)
            )
        draw_values.append(module.field_agreement(fields[0], fields[1], weights))

    return {
        "banner": BANNER,
        "cell": task["cell"],
        "world": int(task["world"]),
        "kappa": float(task["kappa"]),
        "occasion_mode": task["occasion_mode"],
        "n_authors_total": int(len(author_ids)),
        "n_events_total": int(sum(counts)),
        "n_retained": int(len(retained_idx)),
        "n_resolved_contexts": int(len(resolved)),
        "d0_eff_rank_M": float(calibration["M"].effective_rank),
        "d0_eff_rank_K": float(calibration["K"].effective_rank),
        "draws": int(task["draws"]),
        "agreement_mean": float(np.mean(draw_values)),
        "agreement_sd": float(np.std(draw_values, ddof=1)),
        "draw_values": [float(value) for value in draw_values],
        "world_seed": int(world_seed),
        "seconds": float(time.time() - started),
    }


# ---------------------------------------------------------------------------
# Axis-2 (crossed_q2/crossed_q4) per-world computation: main per-context
# gauge on pseudo-author rows + the companion cross-context contrast field.

def compute_companion(
    layout: dict[str, Any],
    real_vectors_by_author: dict[str, np.ndarray],
    corpus: str,
    directions: Any,
    *,
    draws: int,
) -> dict[str, Any]:
    """The within-author cross-context contrast field's split-half agreement.

    Part 0 register-note (a DIFFERENT typed object, constructed here, not
    pinned down equation-by-equation in the registration): for each eligible
    D1/D2 author with all Q context-slices >= MIN_FEATURIZABLE events, each
    slice-half (seeded via the verbatim f1().half_indices) is fed AS A SINGLE
    PATH (no alternating-replicate split -- Q is too small to support a
    further 2-way split) to the verbatim f1().marginal_features_batch /
    transition_features_batch, giving one (M_q, K_q) pair per slice-half. The
    per-author contrast matrix is v8._cross_covariance(M-stack, K-stack)
    across the author's own Q slices (the standard-field author axis and this
    field's context axis are swapped) -- unnormalized (no energy/soft
    denominator, since that machinery needs the 2-replicate structure this
    object does not have); agreement between the two halves' contrast
    matrices uses the verbatim v8._matrix_cosine (scale-invariant, so the
    missing normalization does not affect the agreement reading). Aggregated
    to one number per world (mean over eligible authors), then across worlds
    for a t-test against 0, exactly mirroring the main gauge's world-then-cell
    structure so authors (who are NOT independent within a world) are never
    treated as the unit of replication.
    """
    q = layout["q"]
    by_author: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in layout["pseudo_rows"]:
        by_author[row["real_author_id"]].append(row)

    eligible_authors: list[tuple[str, list[dict[str, Any]]]] = []
    for i, author in enumerate(layout["author_ids"]):
        if layout["splits"][i] not in ("D1", "D2"):
            continue
        rows = sorted(by_author[author], key=lambda r: r["slice_index"])
        if len(rows) == q and all(r["slice_size"] >= MIN_FEATURIZABLE for r in rows):
            eligible_authors.append((author, rows))

    if not eligible_authors:
        return {"status": "NO_ELIGIBLE_AUTHORS", "n_eligible": 0, "n_scored": 0}

    per_author_draw_values: dict[str, list[float]] = {a: [] for a, _ in eligible_authors}
    for draw in range(draws):
        by_size: dict[int, list[tuple[str, list[dict[str, Any]]]]] = defaultdict(list)
        for author, rows in eligible_authors:
            by_size[rows[0]["slice_size"]].append((author, rows))
        author_half_features: dict[str, dict[int, tuple]] = {}
        for size, group in by_size.items():
            half_a_paths, half_b_paths, keys = [], [], []
            for author, rows in group:
                for row in rows:
                    pid = row["pseudo_author_id"]
                    vectors = real_vectors_by_author[author][
                        row["slice_start"] : row["slice_end"]
                    ]
                    first, second = f1().half_indices(
                        corpus, pid, f"crossedq{q}", draw, size
                    )
                    half_a_paths.append(vectors[first])
                    half_b_paths.append(vectors[second])
                    keys.append((author, row["slice_index"]))
            batch_a = np.stack(half_a_paths)
            batch_b = np.stack(half_b_paths)
            m_a = f1().marginal_features_batch(batch_a, directions)
            k_a = f1().transition_features_batch(batch_a, directions)
            m_b = f1().marginal_features_batch(batch_b, directions)
            k_b = f1().transition_features_batch(batch_b, directions)
            for row_idx, (author, slice_index) in enumerate(keys):
                author_half_features.setdefault(author, {})[slice_index] = (
                    m_a[row_idx],
                    k_a[row_idx],
                    m_b[row_idx],
                    k_b[row_idx],
                )
        for author, rows in eligible_authors:
            store = author_half_features.get(author)
            if store is None or len(store) != q:
                continue
            ordered = [store[r["slice_index"]] for r in rows]
            m_a_stack = np.stack([o[0] for o in ordered])
            k_a_stack = np.stack([o[1] for o in ordered])
            m_b_stack = np.stack([o[2] for o in ordered])
            k_b_stack = np.stack([o[3] for o in ordered])
            contrast_a = v8._cross_covariance(m_a_stack, k_a_stack)
            contrast_b = v8._cross_covariance(m_b_stack, k_b_stack)
            agreement = v8._matrix_cosine(contrast_a, contrast_b)
            per_author_draw_values[author].append(agreement)

    per_author_mean = {
        a: float(np.mean(v)) for a, v in per_author_draw_values.items() if v
    }
    values = np.asarray(list(per_author_mean.values()), dtype=float)
    return {
        "status": "OK",
        "n_eligible": int(len(eligible_authors)),
        "n_scored": int(len(values)),
        "world_mean_across_authors": float(values.mean()) if len(values) else float("nan"),
        "world_sd_across_authors": (
            float(values.std(ddof=1)) if len(values) > 1 else float("nan")
        ),
    }


def run_axis2_world(task: dict[str, Any]) -> dict[str, Any]:
    started = time.time()
    spec = f1().load_spec()
    directions = f1()._directions(spec)
    module = f1().e1()
    reference = json.loads(Path(task["ref_path"]).read_text(encoding="utf-8"))
    layout = build_crossed_layout(reference, task["q"])
    author_ids = layout["author_ids"]
    common_counts = layout["common_counts"]

    corpus = f"m4f2-{task['cell']}-w{task['world']}"
    world_seed = v8.stable_bucket(
        f"{MASTER_SEED}-axis2-w{task['world']}-{task['knob_tag']}",
        salt="m4f2-world",
        modulus=2**63 - 1,
    )
    # Registered: Axis 2 is "at kappa=0" only.
    real_vectors = generate_world_composed(
        common_counts, None, task["knobs"], 0.0, "free", world_seed
    )
    real_vectors_by_author = dict(zip(author_ids, real_vectors))

    usable_rows = [r for r in layout["pseudo_rows"] if r["slice_size"] >= MIN_FEATURIZABLE]
    dropped_rows = [r for r in layout["pseudo_rows"] if r["slice_size"] < MIN_FEATURIZABLE]

    pseudo_ids = [r["pseudo_author_id"] for r in usable_rows]
    pseudo_ctx = [r["context"] for r in usable_rows]
    pseudo_split = [r["split"] for r in usable_rows]
    pseudo_count = [r["slice_size"] for r in usable_rows]
    pseudo_vectors = [
        real_vectors_by_author[r["real_author_id"]][r["slice_start"] : r["slice_end"]]
        for r in usable_rows
    ]

    d0_eff: dict[str, float] | None = None
    if not pseudo_ids or sum(1 for s in pseudo_split if s == "D0") < 24:
        main_gauge: dict[str, Any] = {
            "status": "D0_CALIBRATION_NOT_COMPUTABLE",
            "n_d0_usable_pseudo_rows": int(sum(1 for s in pseudo_split if s == "D0")),
        }
    else:
        raw_m, raw_k = f1().featurize_panel(
            pseudo_vectors, pseudo_ids, corpus=corpus, spec=spec, directions=directions
        )
        metadata = pd.DataFrame(
            {
                "author_id": pseudo_ids,
                "context": pseudo_ctx,
                "split": pseudo_split,
                "event_count": pseudo_count,
            }
        )
        panel = SimpleNamespace(metadata=metadata, raw={"M": raw_m, "K": raw_k})
        calibration = module.calibrate_d0_soft(panel)
        d0_eff = {
            "M": float(calibration["M"].effective_rank),
            "K": float(calibration["K"].effective_rank),
        }
        eval_mask = metadata["split"].isin(["D1", "D2"]).to_numpy()
        eval_meta = metadata.loc[eval_mask]
        resolved = module.resolved_contexts(eval_meta, spec.minimum_context_authors)
        retained_mask = eval_mask & metadata["context"].astype(str).isin(
            resolved
        ).to_numpy()
        retained_idx = np.flatnonzero(
            retained_mask & (metadata["event_count"].to_numpy() >= MIN_RETAINED_EVENTS)
        )
        if len(retained_idx) == 0 or not resolved:
            main_gauge = {
                "status": "ZERO_RETAINED_PSEUDO_AUTHORS",
                "n_resolved_contexts": int(len(resolved)),
            }
        else:
            retained_ids = [pseudo_ids[i] for i in retained_idx]
            retained_ctx = np.asarray([pseudo_ctx[i] for i in retained_idx], dtype=object)
            ctx_counts = pd.Series(retained_ctx).value_counts()
            weights = {
                c: float(ctx_counts.get(c, 0) / max(1, int(ctx_counts.sum())))
                for c in resolved
            }
            draw_values = []
            for draw in range(int(task["draws"])):
                halves_a, halves_b = [], []
                for position, index in enumerate(retained_idx):
                    b = pseudo_count[index]
                    first, second = f1().half_indices(
                        corpus, retained_ids[position], "f2x.0", draw, b
                    )
                    vectors = pseudo_vectors[index]
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
                    fields.append(
                        module.deployed_soft_field(projected, retained_ctx, resolved)
                    )
                draw_values.append(module.field_agreement(fields[0], fields[1], weights))
            main_gauge = {
                "status": "OK",
                "n_retained": int(len(retained_idx)),
                "n_resolved_contexts": int(len(resolved)),
                "agreement_mean": float(np.mean(draw_values)),
                "agreement_sd": float(np.std(draw_values, ddof=1)),
                "draw_values": [float(v) for v in draw_values],
            }

    companion = compute_companion(
        layout, real_vectors_by_author, corpus, directions, draws=int(task["draws"])
    )

    return {
        "banner": BANNER,
        "cell": task["cell"],
        "world": int(task["world"]),
        "q": int(task["q"]),
        "n_real_authors": int(len(author_ids)),
        "n_events_allocated_total": int(sum(common_counts)),
        "n_pseudo_rows_intended": int(len(layout["pseudo_rows"])),
        "n_pseudo_rows_usable": int(len(usable_rows)),
        "n_pseudo_rows_dropped_lt4": int(len(dropped_rows)),
        "n_events_featurizable_total": int(sum(pseudo_count)),
        "d0_eff_rank_M": None if d0_eff is None else d0_eff["M"],
        "d0_eff_rank_K": None if d0_eff is None else d0_eff["K"],
        "main_gauge_status": main_gauge["status"],
        "main_gauge_agreement_mean": main_gauge.get("agreement_mean"),
        "main_gauge_agreement_sd": main_gauge.get("agreement_sd"),
        "main_gauge_n_retained": main_gauge.get("n_retained"),
        "main_gauge_draw_values": json.dumps(main_gauge.get("draw_values")),
        "companion_status": companion["status"],
        "companion_n_eligible": companion["n_eligible"],
        "companion_n_scored": companion["n_scored"],
        "companion_world_mean": companion.get("world_mean_across_authors"),
        "companion_world_sd": companion.get("world_sd_across_authors"),
        "world_seed": int(world_seed),
        "seconds": float(time.time() - started),
    }


# ---------------------------------------------------------------------------
# Gates.

def _read_f1_base1x_row() -> dict[str, float]:
    frame = pd.read_csv(F1_CELLS_CSV)
    row = frame.loc[frame["cell"] == "base1x"].iloc[0]
    return {
        "agreement_mean": float(row["agreement_mean"]),
        "agreement_se": float(row["agreement_se"]),
        "d0_eff_rank_M_mean": float(row["d0_eff_rank_M_mean"]),
        "d0_eff_rank_K_mean": float(row["d0_eff_rank_K_mean"]),
        "n_retained": int(row["n_retained"]),
    }


def _aggregate_axis1(rows: list[dict[str, Any]]) -> dict[str, Any]:
    agreements = np.asarray([r["agreement_mean"] for r in rows], dtype=float)
    return {
        "agreement_mean": float(agreements.mean()),
        "agreement_se": float(agreements.std(ddof=1) / math.sqrt(len(agreements))),
        "d0_eff_rank_M_mean": float(np.mean([r["d0_eff_rank_M"] for r in rows])),
        "d0_eff_rank_K_mean": float(np.mean([r["d0_eff_rank_K"] for r in rows])),
        "n_retained": int(rows[0]["n_retained"]),
        "n_retained_constant": bool(
            all(r["n_retained"] == rows[0]["n_retained"] for r in rows)
        ),
    }


def run_gate_g1(knobs: dict[str, Any], knob_tag: str, workers: int) -> dict[str, Any]:
    """kappa=0, occasion_mode='free', M4-F1's EXACT seed recipe (seed_group=
    'base1x', corpus_tag='m4f1', world_salt='m4f1-world', budget_label='f1.0',
    RAW/untruncated layout) -- must reproduce M4-F1's persisted base1x row to
    <=1e-12. Values are READ from results/m4_f1_panel_sizing/cells.csv at run
    time, never retyped."""
    target = _read_f1_base1x_row()
    tasks = [
        {
            "cell": "g1_base1x_kappa0_free",
            "world": world,
            "seed_group": "base1x",
            "corpus_tag": "m4f1",
            "world_salt": "m4f1-world",
            "budget_label": "f1.0",
            "layout": "raw",
            "kappa": 0.0,
            "occasion_mode": "free",
            "knobs": knobs,
            "knob_tag": knob_tag,
            "draws": DRAWS,
            "ref_path": str(REF_PATH),
        }
        for world in range(WORLDS_PER_CELL)
    ]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(run_axis1_world, tasks))
    got = _aggregate_axis1(rows)
    diffs = {
        key: abs(got[key] - target[key])
        for key in ("agreement_mean", "agreement_se", "d0_eff_rank_M_mean", "d0_eff_rank_K_mean")
    }
    diffs["n_retained"] = abs(got["n_retained"] - target["n_retained"])
    passed = bool(
        diffs["agreement_mean"] <= 1e-12
        and diffs["agreement_se"] <= 1e-12
        and diffs["d0_eff_rank_M_mean"] <= 1e-12
        and diffs["d0_eff_rank_K_mean"] <= 1e-12
        and diffs["n_retained"] == 0
    )
    return {
        "gate": "G1",
        "description": "kappa<=0 free cell reproduces M4-F1's persisted base1x to <=1e-12",
        "target_from": str(F1_CELLS_CSV),
        "target": target,
        "observed": got,
        "abs_diffs": diffs,
        "tolerance": 1e-12,
        "pass": passed,
    }


def run_gate_g4(knobs: dict[str, Any], knob_tag: str, workers: int) -> dict[str, Any]:
    """Designed null: at kappa=0, shared cell-for-cell equals free, on the
    SAME (common-budget) layout and the SAME shared seed scaffold the six
    adjudicated cells use. Checked at exact numeric equality per world
    (agreement_mean, d0_eff_rank_M/K, n_retained, and the full draw_values
    vector)."""
    tasks = {}
    for mode in ("free", "shared"):
        tasks[mode] = [
            {
                "cell": f"{mode}_k00",
                "world": world,
                "seed_group": "axis1",
                "corpus_tag": "m4f2",
                "world_salt": "m4f2-world",
                "budget_label": "f2.0",
                "layout": "common",
                "kappa": 0.0,
                "occasion_mode": mode,
                "knobs": knobs,
                "knob_tag": knob_tag,
                "draws": DRAWS,
                "ref_path": str(REF_PATH),
            }
            for world in range(WORLDS_PER_CELL)
        ]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        free_rows = list(pool.map(run_axis1_world, tasks["free"]))
        shared_rows = list(pool.map(run_axis1_world, tasks["shared"]))
    per_world = []
    all_match = True
    for free_row, shared_row in zip(free_rows, shared_rows):
        agreement_match = free_row["agreement_mean"] == shared_row["agreement_mean"]
        eff_m_match = free_row["d0_eff_rank_M"] == shared_row["d0_eff_rank_M"]
        eff_k_match = free_row["d0_eff_rank_K"] == shared_row["d0_eff_rank_K"]
        retained_match = free_row["n_retained"] == shared_row["n_retained"]
        draws_match = free_row["draw_values"] == shared_row["draw_values"]
        world_match = bool(
            agreement_match and eff_m_match and eff_k_match and retained_match and draws_match
        )
        all_match = all_match and world_match
        per_world.append(
            {
                "world": free_row["world"],
                "agreement_mean_free": free_row["agreement_mean"],
                "agreement_mean_shared": shared_row["agreement_mean"],
                "exact_match": world_match,
            }
        )
    return {
        "gate": "G4",
        "description": "designed null: kappa=0 shared equals free cell-for-cell (exact)",
        "worlds_checked": len(per_world),
        "per_world": per_world,
        "pass": bool(all_match),
    }


def run_gate_g2(knobs: dict[str, Any], knob_tag: str) -> dict[str, Any]:
    """Budget conservation: total ALLOCATED events exactly equal across every
    one of the six adjudicated cells. (Featurizable/retained totals are a
    separate, disclosed, non-G2 fact -- see the crossed-cell rows.)"""
    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    _author_ids, _contexts, _splits, common_counts, raw_counts = build_layout_common(
        reference
    )
    axis1_total = int(sum(common_counts))
    per_cell = {
        "free_k05": axis1_total,
        "free_k10": axis1_total,
        "shared_k05": axis1_total,
        "shared_k10": axis1_total,
    }
    for q in (2, 4):
        layout = build_crossed_layout(reference, q)
        per_cell[f"crossed_q{q}"] = int(sum(layout["common_counts"]))
    totals = set(per_cell.values())
    return {
        "gate": "G2",
        "description": "exact total ALLOCATED event-count equality across every cell",
        "per_cell_allocated_total": per_cell,
        "raw_base1x_total": int(sum(raw_counts)),
        "events_dropped_by_common_budget_truncation": int(sum(raw_counts) - axis1_total),
        "pass": bool(len(totals) == 1),
    }


def run_gate_g3() -> dict[str, Any]:
    """Gauge invariance, M4-F1's own gate style: batched feature map vs the
    deployed v8.build_feature_panel (bit-identical), and numpy halving vs
    e1().split_half_frames (identical event indices). Duplicated from
    f1().run_gates() rather than calling it directly, because that function
    writes to results/m4_f1_panel_sizing/gates.json -- a prior leg's artifact
    this leg must not touch. The underlying functions checked
    (f1()._directions, f1().featurize_panel, f1().half_indices) are imported
    unchanged, so this re-validates the SAME primitives M4-F1 validated."""
    spec = f1().load_spec()
    directions = f1()._directions(spec)
    module = f1().e1()
    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    author_ids, contexts, splits, counts = f1().build_layout(reference, 1, 1)
    keep = np.random.default_rng(7).choice(len(author_ids), size=40, replace=False)
    keep = np.sort(keep)
    sub_ids = [author_ids[i] for i in keep]
    sub_ctx = [contexts[i] for i in keep]
    sub_counts = [counts[i] for i in keep]
    knobs = {
        "k": 48, "rho": 0.5, "w_mu": 0.25, "w_x": 0.25, "w_e": 0.50,
        "phi_lo": 0.2, "phi_hi": 0.8,
    }
    vectors_list = generate_world_composed(sub_counts, sub_ctx, knobs, 0.0, "free", 12345)
    corpus = "m4f2-gate"

    registry: dict[str, np.ndarray] = {}
    rows = []
    for index, author in enumerate(sub_ids):
        for order in range(sub_counts[index]):
            token = f"{author}::{order}"
            registry[token] = vectors_list[index][order]
            rows.append(
                {"author_id": author, "context": sub_ctx[index], "order": order, "text": token}
            )
    events = pd.DataFrame(rows)

    def lookup_vector(text: str, *, dimensions: int = 32) -> np.ndarray:
        return registry[str(text)]

    original = v8.frozen_event_vector
    v8.frozen_event_vector = lookup_vector
    try:
        deployed_panel = v8.build_feature_panel(
            events, corpus=corpus, context_role="SYNTHETIC", replicate_type="SYNTHETIC", spec=spec
        )
    finally:
        v8.frozen_event_vector = original
    batched_m, batched_k = f1().featurize_panel(
        vectors_list, sub_ids, corpus=corpus, spec=spec, directions=directions
    )
    deployed_order = {
        author: row for row, author in enumerate(deployed_panel.metadata["author_id"].astype(str))
    }
    gaps_m, gaps_k = [], []
    for index, author in enumerate(sub_ids):
        row = deployed_order[author]
        gaps_m.append(float(np.max(np.abs(deployed_panel.raw["M"][row] - batched_m[index]))))
        gaps_k.append(float(np.max(np.abs(deployed_panel.raw["K"][row] - batched_k[index]))))
    gate_features = {
        "max_abs_diff_M": float(max(gaps_m)),
        "max_abs_diff_K": float(max(gaps_k)),
        "pass": bool(max(max(gaps_m), max(gaps_k)) < 1e-9),
    }

    frame = events.copy()
    retained = set(sub_ids)
    mismatches = 0
    checked = 0
    for draw in range(3):
        frame_a, frame_b = module.split_half_frames(
            frame, corpus=corpus, budget_label="f2.0", draw=draw, retained_authors=retained
        )
        for author in sub_ids:
            b = int((frame["author_id"] == author).sum())
            first, second = f1().half_indices(corpus, author, "f2.0", draw, b)
            got_a = frame_a.loc[frame_a["author_id"] == author, "text"].tolist()
            got_b = frame_b.loc[frame_b["author_id"] == author, "text"].tolist()
            want_a = [f"{author}::{i}" for i in first]
            want_b = [f"{author}::{i}" for i in second]
            checked += 1
            if got_a != want_a or got_b != want_b:
                mismatches += 1
    gate_halving = {"checked": int(checked), "mismatches": int(mismatches), "pass": mismatches == 0}
    return {
        "gate": "G3",
        "description": "gauge invariance (M4-F1 gate style): batched map + halving vs deployed",
        "gate_batched_feature_map": gate_features,
        "gate_halving_seed_compatible": gate_halving,
        "pass": bool(gate_features["pass"] and gate_halving["pass"]),
    }


def run_gates(workers: int) -> dict[str, Any]:
    f1_cal = json.loads(F1_CALIBRATION.read_text(encoding="utf-8"))
    if f1_cal["status"] != "CALIBRATED":
        raise AssertionError("M4-F1 calibration_record.json is not CALIBRATED.")
    knobs = f1_cal["selected"]["knobs"]
    knob_tag = f1().knob_tag(knobs)

    g3 = run_gate_g3()
    g1 = run_gate_g1(knobs, knob_tag, workers)
    g2 = run_gate_g2(knobs, knob_tag)
    g4 = run_gate_g4(knobs, knob_tag, workers)

    gates = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "knobs": knobs,
        "knob_tag": knob_tag,
        "G1": g1,
        "G2": g2,
        "G3": g3,
        "G4": g4,
        "all_pass": bool(g1["pass"] and g2["pass"] and g3["pass"] and g4["pass"]),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v["pass"] for k, v in gates.items() if isinstance(v, dict) and "pass" in v}, indent=2))
    if not g4["pass"]:
        raise AssertionError(
            "G4 (designed null: kappa=0 shared==free) FAILED. The leg is VOID "
            "per the registration. See results/m4_f2_composition/gates.json."
        )
    return gates


# ---------------------------------------------------------------------------
# Sweep: the six adjudicated cells.

AXIS1_CELLS: list[tuple[str, float, str]] = [
    ("free_k05", 0.5, "free"),
    ("free_k10", 1.0, "free"),
    ("shared_k05", 0.5, "shared"),
    ("shared_k10", 1.0, "shared"),
]
AXIS2_CELLS: list[tuple[str, int]] = [
    ("crossed_q2", 2),
    ("crossed_q4", 4),
]


def run_sweep(knobs: dict[str, Any], knob_tag: str, workers: int, draws: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for cell, kappa, mode in AXIS1_CELLS:
        path = OUT / f"axis1_cell_{cell}.csv"
        if path.exists():
            print(f"[skip] {cell} exists")
            continue
        tasks = [
            {
                "cell": cell, "world": world, "seed_group": "axis1",
                "corpus_tag": "m4f2", "world_salt": "m4f2-world",
                "budget_label": "f2.0", "layout": "common",
                "kappa": kappa, "occasion_mode": mode,
                "knobs": knobs, "knob_tag": knob_tag, "draws": draws,
                "ref_path": str(REF_PATH),
            }
            for world in range(WORLDS_PER_CELL)
        ]
        started = time.time()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(run_axis1_world, tasks))
        for row in rows:
            print(
                f"[{cell} w{row['world']}] A {row['agreement_mean']:+.4f} "
                f"(sd {row['agreement_sd']:.4f}) effM {row['d0_eff_rank_M']:.1f} "
                f"effK {row['d0_eff_rank_K']:.1f} n_ret {row['n_retained']} "
                f"{row['seconds']:.0f}s", flush=True,
            )
        pd.DataFrame(rows).drop(columns=["draw_values"]).to_csv(path, index=False)
        draw_rows = [
            {"cell": cell, "world": row["world"], "draw": d, "agreement": v}
            for row in rows
            for d, v in enumerate(row["draw_values"])
        ]
        pd.DataFrame(draw_rows).to_csv(OUT / f"axis1_draws_{cell}.csv", index=False)
        print(f"[{cell}] done in {time.time() - started:.0f}s -> {path}")

    for cell, q in AXIS2_CELLS:
        path = OUT / f"axis2_cell_{cell}.csv"
        if path.exists():
            print(f"[skip] {cell} exists")
            continue
        tasks = [
            {
                "cell": cell, "world": world, "q": q,
                "knobs": knobs, "knob_tag": knob_tag, "draws": draws,
                "ref_path": str(REF_PATH),
            }
            for world in range(WORLDS_PER_CELL)
        ]
        started = time.time()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(run_axis2_world, tasks))
        for row in rows:
            print(
                f"[{cell} w{row['world']}] main={row['main_gauge_status']} "
                f"A={row['main_gauge_agreement_mean']} "
                f"companion={row['companion_status']} "
                f"cA={row['companion_world_mean']} "
                f"n_pseudo usable/dropped={row['n_pseudo_rows_usable']}/"
                f"{row['n_pseudo_rows_dropped_lt4']} {row['seconds']:.0f}s", flush=True,
            )
        pd.DataFrame(rows).to_csv(path, index=False)
        print(f"[{cell}] done in {time.time() - started:.0f}s -> {path}")


# ---------------------------------------------------------------------------
# Adjudication.

def _paired_ci(diffs: np.ndarray) -> dict[str, Any]:
    n = len(diffs)
    mean = float(diffs.mean())
    sd = float(diffs.std(ddof=1))
    se = sd / math.sqrt(n)
    t_stat = mean / se if se > 0 else float("inf")
    t_crit = float(stats.t.ppf(0.975, df=n - 1))
    return {
        "n": int(n),
        "mean": mean,
        "sd": sd,
        "se": se,
        "t_stat": float(t_stat),
        "t_crit_95": t_crit,
        "ci95_low": float(mean - t_crit * se),
        "ci95_high": float(mean + t_crit * se),
        "ci_excludes_zero_positive": bool(mean - t_crit * se > 0),
    }


def load_axis1(cell: str) -> pd.DataFrame:
    return pd.read_csv(OUT / f"axis1_cell_{cell}.csv")


def load_axis2(cell: str) -> pd.DataFrame:
    return pd.read_csv(OUT / f"axis2_cell_{cell}.csv")


def adjudicate() -> dict[str, Any]:
    frames = {cell: load_axis1(cell) for cell, _, _ in AXIS1_CELLS}
    paired = {}
    for kappa_tag, kappa in (("k05", 0.5), ("k10", 1.0)):
        free = frames[f"free_{kappa_tag}"].sort_values("world")
        shared = frames[f"shared_{kappa_tag}"].sort_values("world")
        assert (free["world"].to_numpy() == shared["world"].to_numpy()).all()
        diffs = shared["agreement_mean"].to_numpy() - free["agreement_mean"].to_numpy()
        paired[kappa_tag] = {
            "kappa": kappa,
            "free_mean": float(free["agreement_mean"].mean()),
            "shared_mean": float(shared["agreement_mean"].mean()),
            **_paired_ci(diffs),
        }

    lean_a = {
        "lean": "a",
        "rule": "shared - free paired-world CI excludes 0 (>0) at kappa=1.0 at minimum",
        "kappa_1_0": paired["k10"],
        "kappa_0_5": paired["k05"],
        "verdict": "HOLD" if paired["k10"]["ci_excludes_zero_positive"] else "MISS",
    }

    lean_b = {
        "lean": "b",
        "rule": "gain(kappa=1.0) > gain(kappa=0.5)",
        "gain_k10": paired["k10"]["mean"],
        "gain_k05": paired["k05"]["mean"],
        "verdict": "HOLD" if paired["k10"]["mean"] > paired["k05"]["mean"] else "MISS",
    }

    pivot_fires = bool(
        (not paired["k05"]["ci_excludes_zero_positive"])
        and (not paired["k10"]["ci_excludes_zero_positive"])
    )
    pivot = {
        "registered_rule": "neither kappa shows a shared-minus-free gain with a CI excluding 0",
        "kappa_0_5_ci_excludes_zero_positive": paired["k05"]["ci_excludes_zero_positive"],
        "kappa_1_0_ci_excludes_zero_positive": paired["k10"]["ci_excludes_zero_positive"],
        "fires": pivot_fires,
    }

    # Lean (c): crossed cells vs the kappa=0 axis-1 reference (free_k00==shared_k00
    # by G4; either serves as the Q=1 baseline).
    reference_g4 = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    ref_agreements = [
        row["agreement_mean_free"] for row in reference_g4["G4"]["per_world"]
    ]
    ref_mean = float(np.mean(ref_agreements))
    ref_se = float(np.std(ref_agreements, ddof=1) / math.sqrt(len(ref_agreements)))

    crossed = {cell: load_axis2(cell) for cell, _ in AXIS2_CELLS}
    main_gauge_summary = {}
    companion_summary = {}
    for cell, q in AXIS2_CELLS:
        frame = crossed[cell]
        ok_rows = frame.loc[frame["main_gauge_status"] == "OK"]
        if len(ok_rows) > 0:
            values = ok_rows["main_gauge_agreement_mean"].to_numpy(dtype=float)
            main_gauge_summary[cell] = {
                "status": "OK" if len(ok_rows) == len(frame) else "PARTIAL",
                "n_worlds_ok": int(len(ok_rows)),
                "n_worlds_total": int(len(frame)),
                "agreement_mean": float(values.mean()),
                "agreement_se": (
                    float(values.std(ddof=1) / math.sqrt(len(values))) if len(values) > 1 else None
                ),
                "n_retained_first_ok_world": int(ok_rows.iloc[0]["main_gauge_n_retained"]),
            }
        else:
            statuses = frame["main_gauge_status"].unique().tolist()
            main_gauge_summary[cell] = {
                "status": statuses[0] if len(statuses) == 1 else "MIXED_UNDEFINED",
                "n_worlds_ok": 0,
                "n_worlds_total": int(len(frame)),
                "statuses_seen": statuses,
            }
        comp_rows = frame.loc[frame["companion_status"] == "OK"]
        comp_values = comp_rows["companion_world_mean"].to_numpy(dtype=float)
        if len(comp_values) > 1:
            comp_se = float(comp_values.std(ddof=1) / math.sqrt(len(comp_values)))
            comp_mean = float(comp_values.mean())
            comp_t = comp_mean / comp_se if comp_se > 0 else float("inf")
        else:
            comp_se = None
            comp_mean = float(comp_values.mean()) if len(comp_values) else None
            comp_t = None
        companion_summary[cell] = {
            "n_worlds_ok": int(len(comp_rows)),
            "n_worlds_total": int(len(frame)),
            "n_eligible_authors_first_world": (
                int(comp_rows.iloc[0]["companion_n_eligible"]) if len(comp_rows) else None
            ),
            "mean": comp_mean,
            "se": comp_se,
            "t_vs_zero": comp_t,
            "non_nil_t_gt_2": bool(comp_t is not None and comp_t > 2.0),
        }

    c1_declines = {}
    for cell, _q in AXIS2_CELLS:
        summary = main_gauge_summary[cell]
        if summary["status"] in ("OK", "PARTIAL"):
            c1_declines[cell] = {
                "reference_kappa0_mean": ref_mean,
                "reference_kappa0_se": ref_se,
                "crossed_mean": summary["agreement_mean"],
                "declined": bool(summary["agreement_mean"] < ref_mean),
            }
        else:
            c1_declines[cell] = {
                "reference_kappa0_mean": ref_mean,
                "crossed_status": summary["status"],
                "declined": True,
                "note": "main gauge structurally undefined (0 retained pseudo-authors "
                "under the deployed >=8-event floor) -- the extreme end of 'crossed hurts "
                "the gauge', not a further point on a numeric monotone curve",
            }

    c1_hold = all(v["declined"] for v in c1_declines.values())
    c2_hold_per_cell = {
        cell: companion_summary[cell]["non_nil_t_gt_2"] for cell, _q in AXIS2_CELLS
    }
    c2_hold = all(c2_hold_per_cell.values())

    lean_c = {
        "lean": "c",
        "rule_c1": "crossed cells decline vs the kappa=0 axis-1 reference (monotone in Q, "
        "including structural non-computability as the extreme case)",
        "rule_c2": "companion split-half agreement non-nil (t>2 vs 0) at Q in {2,4}",
        "kappa0_reference": {"mean": ref_mean, "se": ref_se, "n_worlds": len(ref_agreements)},
        "main_gauge": main_gauge_summary,
        "c1_per_cell": c1_declines,
        "c1_hold": c1_hold,
        "companion": companion_summary,
        "c2_hold_per_cell": c2_hold_per_cell,
        "c2_hold": c2_hold,
        "verdict": "HOLD" if (c1_hold and c2_hold) else ("PARTIAL" if (c1_hold or c2_hold) else "MISS"),
    }

    if pivot_fires:
        verdict = "COMPOSITION_AT_FIXED_BUDGET_ALSO_FAILS_GAUGE_PROBLEM_MERGES_WITH_M4E2"
    else:
        verdict = "COMPOSITION_GAIN_MEASURED_SEE_LEAN_ADJUDICATION"

    return {
        "paired_differences": paired,
        "lean_a": lean_a,
        "lean_b": lean_b,
        "lean_c": lean_c,
        "pivot": pivot,
        "verdict": verdict,
    }


def run_finalize(knobs: dict[str, Any], knob_tag: str) -> None:
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    adjudication = adjudicate()
    decision = {
        "experiment": "M4-F2_composition_law",
        "banner": BANNER,
        "tier": "EXPLORATORY",
        "registered_spec": (
            "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md#M4-F2-registration"
        ),
        "part0_registered_in": "reports/SUICA_M4_F2_COMPOSITION_REPORT.md Part 0 (before run)",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "worlds_per_cell": WORLDS_PER_CELL,
        "draws_per_world": DRAWS,
        "knobs": knobs,
        "knob_tag": knob_tag,
        "gates": {k: (v["pass"] if isinstance(v, dict) and "pass" in v else v) for k, v in gates.items()},
        "gates_all_pass": gates["all_pass"],
        "adjudication": adjudication,
        "label_free": True,
        "claim_boundary": (
            "Synthetic composition-law finding in a world calibrated to the opened "
            "PANDORA D-panel regime; licenses a D3 panel-DESIGN prior only. No claim "
            "about the real relation field's content, personality, emotion, "
            "diagnosis, or any individual."
        ),
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(adjudication, indent=2, default=str))


# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["gates", "sweep", "finalize", "all"], default="all")
    parser.add_argument("--workers", type=int, default=max(2, min(6, (os.cpu_count() or 4) - 2)))
    parser.add_argument("--draws", type=int, default=DRAWS)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if not REF_PATH.exists():
        raise AssertionError(f"{REF_PATH} missing (M4-F1 artifact required, read-only).")
    if not F1_CELLS_CSV.exists():
        raise AssertionError(f"{F1_CELLS_CSV} missing (M4-F1 artifact required, read-only).")
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

    f1_cal = json.loads(F1_CALIBRATION.read_text(encoding="utf-8"))
    knobs = f1_cal["selected"]["knobs"]
    knob_tag = f1().knob_tag(knobs)

    if args.stage in ("gates", "all"):
        run_gates(args.workers)
    if args.stage in ("sweep", "all"):
        run_sweep(knobs, knob_tag, args.workers, args.draws)
    if args.stage in ("finalize", "all"):
        run_finalize(knobs, knob_tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
