#!/usr/bin/env python3
"""M4-F1 — the D3 panel sizing law (author-axis vs events-axis scaling).

Registered spec: docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md section
M4-F1; generator adjudication, composed-world equations, calibration bars, fit
form, leans/pivot operationalizations all registered in
reports/SUICA_M4_F1_PANEL_SIZING_REPORT.md Part 0 BEFORE this run.

World: M4F1RelationWorld — the V8 relation-field (HJIC) latent/loadings/taper
structure lifted to event level, order-sensitive family carried by per-factor
latent AR(1) chains; the deployed V8 realtext frozen feature map (batched,
equality-gated), the deployed penalty-free soft relation field, and the M4-E1
split-half agreement gauge (verbatim imports + seed-compatible halving).

Stages (resumable, artifacts under results/m4_f1_panel_sizing/):
  --stage gates      run numeric equality gates only
  --stage calibrate  knob search on the 1x panel (calibration_record.json)
  --stage sweep      the 7 sweep cells (cell_<id>.csv, draws_<id>.csv)
  --stage predict    fit both axes, persist prediction_16x.json (pre-holdout)
  --stage holdout    run events_x16 (refuses without prediction_16x.json)
  --stage finalize   fits, leans, pivot, decision.json + cells.csv
  --stage all        everything in order
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
from suica_core.v8_context_relation_field import _orthonormal_loadings  # noqa: E402

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"
MASTER_SEED = 20260802
DRAWS = 20
WORLDS_PER_CELL = 8
CAL_DRAWS = 12
OUT = ROOT / "results" / "m4_f1_panel_sizing"
REF_PATH = OUT / "realtext_panel_reference.json"
SPEC_CONFIG = ROOT / "configs" / "v8_realtext_relation_field.json"
REPORT_PART0 = ROOT / "reports" / "SUICA_M4_F1_PANEL_SIZING_REPORT.md"

# Real-panel calibration targets (Part 0.1; persisted artifacts).
TARGET_EFF_M = 42.166460
TARGET_EFF_K = 38.534629
EFF_BAND = 3.0
AGREE_ABS_BAR = 0.02
AGREE_T_BAR = 2.5

SWEEP_CELLS: list[tuple[str, int, int]] = [
    ("base1x", 1, 1),
    ("authors_x2", 2, 1),
    ("authors_x4", 4, 1),
    ("authors_x8", 8, 1),
    ("events_x2", 1, 2),
    ("events_x4", 1, 4),
    ("events_x8", 1, 8),
]
HOLDOUT_CELL = ("events_x16_holdout", 1, 16)


def _load_script(name: str) -> Any:
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_E1 = None


def e1() -> Any:
    """The M4-E1 script module (verbatim gauge/estimator helpers)."""
    global _E1
    if _E1 is None:
        _E1 = _load_script("run_suica_m4_e1_convention_gap.py")
    return _E1


def load_spec() -> v8.RealTextRelationSpec:
    config = json.loads(SPEC_CONFIG.read_text(encoding="utf-8"))
    return v8.RealTextRelationSpec(**config["spec"])


# ---------------------------------------------------------------------------
# Batched deployed feature map (equality-gated against v8.build_feature_panel).

def _directions(spec: v8.RealTextRelationSpec):
    return v8.frozen_random_directions(
        event_dimensions=2 * spec.hash_dimensions,
        count=spec.random_directions,
        seed=spec.seed + 17,
    )


def marginal_features_batch(paths: np.ndarray, directions) -> np.ndarray:
    """Batched v8.family_features 'M' branch. paths: (B, L, D), L >= 2."""
    marginal_directions = directions[0]
    values = np.asarray(paths, dtype=float)
    mean = values.mean(axis=1)
    centered = values - mean[:, None, :]
    variance = np.mean(centered**2, axis=1)
    marginal_phase = centered @ marginal_directions.T
    marginal_rff = np.concatenate(
        [
            np.mean(np.cos(marginal_phase), axis=1),
            np.mean(np.sin(marginal_phase), axis=1),
        ],
        axis=1,
    )
    projections = values @ marginal_directions.T
    quantiles = np.quantile(projections, (0.25, 0.50, 0.75), axis=1)
    quantiles = np.moveaxis(quantiles, 0, 1).reshape(len(values), -1)
    return np.concatenate([mean, variance, marginal_rff, quantiles], axis=1)


def transition_features_batch(paths: np.ndarray, directions) -> np.ndarray:
    """Batched v8.family_features 'K' branch (pre null-subtraction)."""
    _, transition_directions, current_directions = directions
    values = np.asarray(paths, dtype=float)
    previous = values[:, :-1]
    following = values[:, 1:]
    delta = following - previous
    lag_product = np.mean(previous * following, axis=1)
    delta_variance = np.mean(
        (delta - delta.mean(axis=1, keepdims=True)) ** 2, axis=1
    )
    pairs = np.concatenate([previous, following], axis=2)
    transition_phase = pairs @ transition_directions.T
    transition_rff = np.concatenate(
        [
            np.mean(np.cos(transition_phase), axis=1),
            np.mean(np.sin(transition_phase), axis=1),
        ],
        axis=1,
    )
    currents = []
    for first, second in current_directions:
        forward = np.tanh(previous @ first) * np.tanh(following @ second)
        reverse = np.tanh(previous @ second) * np.tanh(following @ first)
        currents.append(np.mean(forward - reverse, axis=1))
    return np.concatenate(
        [lag_product, delta_variance, transition_rff, np.stack(currents, axis=1)],
        axis=1,
    )


def featurize_panel(
    vectors_list: list[np.ndarray],
    author_ids: list[str],
    *,
    corpus: str,
    spec: v8.RealTextRelationSpec,
    directions,
    chunk: int = 256,
) -> tuple[np.ndarray, np.ndarray]:
    """Deployed build_feature_panel semantics on event-vector streams.

    Alternating source-disjoint replicates; observed M/K per replicate; K minus
    the mean of spec.transition_null_draws permuted-path K features, with the
    per-(corpus, author, offset) RNG streams constructed exactly as deployed.
    Returns raw arrays M (n, 2, 168) and K (n, 2, 152).
    """
    n = len(vectors_list)
    dim_m = 2 * (2 * spec.hash_dimensions) + 2 * spec.random_directions + 3 * spec.random_directions
    dim_k = 2 * (2 * spec.hash_dimensions) + 2 * spec.random_directions + spec.random_directions
    out_m = np.empty((n, 2, dim_m), dtype=float)
    out_k = np.empty((n, 2, dim_k), dtype=float)
    draws = int(spec.transition_null_draws)
    for start in range(0, n, chunk):
        stop = min(start + chunk, n)
        obs_groups: dict[int, list[tuple[int, int, np.ndarray]]] = defaultdict(list)
        null_groups: dict[int, list[tuple[int, int, np.ndarray]]] = defaultdict(list)
        for index in range(start, stop):
            vectors = vectors_list[index]
            for offset in (0, 1):
                path = vectors[offset::2]
                length = len(path)
                if length < 2:
                    raise ValueError("replicate path shorter than 2 events")
                obs_groups[length].append((index, offset, path))
                if draws:
                    rng = np.random.default_rng(
                        spec.seed
                        + v8.stable_bucket(
                            f"{corpus}-{author_ids[index]}-{offset}",
                            salt="v8rt-transition-null",
                            modulus=2**31 - 1,
                        )
                    )
                    permuted = np.stack(
                        [path[rng.permutation(length)] for _ in range(draws)]
                    )
                    null_groups[length].append((index, offset, permuted))
        for length, items in obs_groups.items():
            batch = np.stack([item[2] for item in items])
            m_features = marginal_features_batch(batch, directions)
            k_features = transition_features_batch(batch, directions)
            for row, (index, offset, _) in enumerate(items):
                out_m[index, offset] = m_features[row]
                out_k[index, offset] = k_features[row]
        for length, items in null_groups.items():
            batch = np.concatenate([item[2] for item in items])
            k_features = transition_features_batch(batch, directions)
            k_features = k_features.reshape(len(items), draws, dim_k)
            null_means = k_features.mean(axis=1)
            for row, (index, offset, _) in enumerate(items):
                out_k[index, offset] = out_k[index, offset] - null_means[row]
    if not (np.isfinite(out_m).all() and np.isfinite(out_k).all()):
        raise ValueError("non-finite features")
    return out_m, out_k


# ---------------------------------------------------------------------------
# M4-E1-seed-compatible event halving (equality-gated vs e1.split_half_frames).

def half_indices(
    corpus: str, author: str, budget_label: str, draw: int, b: int
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(
        v8.stable_bucket(
            f"{corpus}-{author}-{budget_label}-{draw}",
            salt="m4e1-half-perm",
            modulus=2**31 - 1,
        )
    )
    perm = rng.permutation(b)
    half = b // 2
    return np.sort(perm[:half]), np.sort(perm[half:])


# ---------------------------------------------------------------------------
# The composed world (Part 0.3) and the panel layout (Part 0.4).

def build_layout(
    reference: dict[str, Any], author_mult: int, event_mult: int
) -> tuple[list[str], list[str], list[str], list[int]]:
    """Exact persisted split-by-context table x author_mult; m x event_mult."""
    author_ids: list[str] = []
    contexts: list[str] = []
    splits: list[str] = []
    counts: list[int] = []
    for key in sorted(reference["split_context_m_multisets"]):
        split, context = key.split("|", 1)
        multiset = list(reference["split_context_m_multisets"][key]) * author_mult
        for serial, m in enumerate(multiset):
            author_ids.append(f"a-{split}-{context}-{serial:05d}")
            contexts.append(context)
            splits.append(split)
            counts.append(int(m) * event_mult)
    order = np.argsort(np.asarray(author_ids, dtype=object), kind="stable")
    return (
        [author_ids[i] for i in order],
        [contexts[i] for i in order],
        [splits[i] for i in order],
        [counts[i] for i in order],
    )


def generate_world(
    counts: list[int], knobs: dict[str, Any], world_seed: int
) -> list[np.ndarray]:
    """M4F1RelationWorld event streams (Part 0.3 equations, exact order of draws)."""
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
    state_part = math.sqrt(w_x) * a * ((x * g) @ loadings.T)
    events = mean_part[:, None, :] + state_part + math.sqrt(w_e) * sigma_iso * noise
    return [events[i, : counts[i]] for i in range(n)]


# ---------------------------------------------------------------------------
# One world end-to-end: panel -> D0 calibration -> gauge draws.

def run_world(
    task: dict[str, Any],
) -> dict[str, Any]:
    started = time.time()
    spec = load_spec()
    directions = _directions(spec)
    module = e1()
    reference = json.loads(Path(task["ref_path"]).read_text(encoding="utf-8"))
    author_ids, contexts, splits, counts = build_layout(
        reference, task["author_mult"], task["event_mult"]
    )
    corpus = f"m4f1-{task['cell']}-w{task['world']}"
    world_seed = v8.stable_bucket(
        f"{MASTER_SEED}-{task['cell']}-w{task['world']}-{task['knob_tag']}",
        salt="m4f1-world",
        modulus=2**63 - 1,
    )
    vectors_list = generate_world(counts, task["knobs"], world_seed)

    raw_m, raw_k = featurize_panel(
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
        retained_mask & (metadata["event_count"].to_numpy() >= 8)
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
            first, second = half_indices(
                corpus, retained_ids[position], "f1.0", draw, b
            )
            vectors = vectors_list[index]
            halves_a.append(vectors[first])
            halves_b.append(vectors[second])
        fields = []
        for half in (halves_a, halves_b):
            m_half, k_half = featurize_panel(
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

    result = {
        "banner": BANNER,
        "cell": task["cell"],
        "world": int(task["world"]),
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
        "draw_values": [float(value) for value in draw_values],
        "world_seed": int(world_seed),
        "seconds": float(time.time() - started),
    }
    if task.get("quarter_diagnostic"):
        quarter_vectors = []
        for index in range(len(author_ids)):
            m = counts[index]
            b = int(min(m, max(4, 2 * int(0.25 * m / 2 + 0.5))))
            rng = np.random.default_rng(
                v8.stable_bucket(
                    f"{corpus}-{author_ids[index]}",
                    salt="m4e1-budget-perm",
                    modulus=2**31 - 1,
                )
            )
            keep = np.sort(rng.permutation(m)[:b])
            quarter_vectors.append(vectors_list[index][keep])
        q_m, q_k = featurize_panel(
            quarter_vectors,
            author_ids,
            corpus=corpus,
            spec=spec,
            directions=directions,
        )
        q_panel = SimpleNamespace(metadata=metadata, raw={"M": q_m, "K": q_k})
        q_cal = module.calibrate_d0_soft(q_panel)
        result["quarter_d0_eff_rank_M"] = float(q_cal["M"].effective_rank)
        result["quarter_d0_eff_rank_K"] = float(q_cal["K"].effective_rank)
    return result


# ---------------------------------------------------------------------------
# Equality gates (Part 0.5).

def run_gates() -> dict[str, Any]:
    spec = load_spec()
    directions = _directions(spec)
    module = e1()
    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    author_ids, contexts, splits, counts = build_layout(reference, 1, 1)
    keep = np.random.default_rng(7).choice(len(author_ids), size=40, replace=False)
    keep = np.sort(keep)
    sub_ids = [author_ids[i] for i in keep]
    sub_ctx = [contexts[i] for i in keep]
    sub_counts = [counts[i] for i in keep]
    knobs = {
        "k": 48,
        "rho": 0.5,
        "w_mu": 0.25,
        "w_x": 0.25,
        "w_e": 0.50,
        "phi_lo": 0.2,
        "phi_hi": 0.8,
    }
    vectors_list = generate_world(sub_counts, knobs, 12345)
    corpus = "m4f1-gate"

    # Gate 1: batched map vs the deployed build_feature_panel (registry patch).
    registry: dict[str, np.ndarray] = {}
    rows = []
    for index, author in enumerate(sub_ids):
        for order in range(sub_counts[index]):
            token = f"{author}::{order}"
            registry[token] = vectors_list[index][order]
            rows.append(
                {
                    "author_id": author,
                    "context": sub_ctx[index],
                    "order": order,
                    "text": token,
                }
            )
    events = pd.DataFrame(rows)

    def lookup_vector(text: str, *, dimensions: int = 32) -> np.ndarray:
        return registry[str(text)]

    original = v8.frozen_event_vector
    v8.frozen_event_vector = lookup_vector
    try:
        deployed_panel = v8.build_feature_panel(
            events,
            corpus=corpus,
            context_role="SYNTHETIC",
            replicate_type="SYNTHETIC",
            spec=spec,
        )
    finally:
        v8.frozen_event_vector = original
    batched_m, batched_k = featurize_panel(
        vectors_list, sub_ids, corpus=corpus, spec=spec, directions=directions
    )
    deployed_order = {
        author: row
        for row, author in enumerate(deployed_panel.metadata["author_id"].astype(str))
    }
    gaps_m, gaps_k = [], []
    for index, author in enumerate(sub_ids):
        row = deployed_order[author]
        gaps_m.append(
            float(np.max(np.abs(deployed_panel.raw["M"][row] - batched_m[index])))
        )
        gaps_k.append(
            float(np.max(np.abs(deployed_panel.raw["K"][row] - batched_k[index])))
        )
    gate_features = {
        "max_abs_diff_M": float(max(gaps_m)),
        "max_abs_diff_K": float(max(gaps_k)),
        "pass": bool(max(max(gaps_m), max(gaps_k)) < 1e-9),
    }

    # Gate 2: numpy halving vs e1.split_half_frames (identical event indices).
    frame = events.copy()
    retained = set(sub_ids)
    mismatches = 0
    checked = 0
    for draw in range(3):
        frame_a, frame_b = module.split_half_frames(
            frame,
            corpus=corpus,
            budget_label="f1.0",
            draw=draw,
            retained_authors=retained,
        )
        for author in sub_ids:
            b = int((frame["author_id"] == author).sum())
            first, second = half_indices(corpus, author, "f1.0", draw, b)
            got_a = frame_a.loc[frame_a["author_id"] == author, "text"].tolist()
            got_b = frame_b.loc[frame_b["author_id"] == author, "text"].tolist()
            want_a = [f"{author}::{i}" for i in first]
            want_b = [f"{author}::{i}" for i in second]
            checked += 1
            if got_a != want_a or got_b != want_b:
                mismatches += 1
    gate_halving = {"checked": int(checked), "mismatches": int(mismatches), "pass": mismatches == 0}

    gates = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "gate_batched_feature_map": gate_features,
        "gate_halving_seed_compatible": gate_halving,
        "all_pass": bool(gate_features["pass"] and gate_halving["pass"]),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(gates, indent=2))
    if not gates["all_pass"]:
        raise AssertionError("Equality gates failed; aborting.")
    return gates


# ---------------------------------------------------------------------------
# Calibration search (Part 0.6).

def knob_tag(knobs: dict[str, Any]) -> str:
    return (
        f"k{knobs['k']}-r{knobs['rho']:.2f}-mu{knobs['w_mu']:.2f}"
        f"-x{knobs['w_x']:.2f}-e{knobs['w_e']:.2f}"
        f"-p{knobs['phi_lo']:.2f}_{knobs['phi_hi']:.2f}"
    )


def trial(knobs: dict[str, Any], *, draws: int, world: int = 0) -> dict[str, Any]:
    task = {
        "cell": "cal1x",
        "world": world,
        "author_mult": 1,
        "event_mult": 1,
        "knobs": knobs,
        "knob_tag": knob_tag(knobs),
        "draws": draws,
        "ref_path": str(REF_PATH),
        "quarter_diagnostic": True,
    }
    result = run_world(task)
    mean = result["agreement_mean"]
    se = result["agreement_sd"] / math.sqrt(result["draws"])
    t_stat = mean / se if se > 0 else float("inf")
    eff_m, eff_k = result["d0_eff_rank_M"], result["d0_eff_rank_K"]
    pass_m = abs(eff_m - TARGET_EFF_M) <= EFF_BAND
    pass_k = abs(eff_k - TARGET_EFF_K) <= EFF_BAND
    pass_agree = abs(mean) <= AGREE_ABS_BAR and abs(t_stat) <= AGREE_T_BAR
    score = (
        ((eff_m - TARGET_EFF_M) / EFF_BAND) ** 2
        + ((eff_k - TARGET_EFF_K) / EFF_BAND) ** 2
        + (mean / AGREE_ABS_BAR) ** 2
    )
    return {
        "knobs": knobs,
        "knob_tag": task["knob_tag"],
        "d0_eff_rank_M": eff_m,
        "d0_eff_rank_K": eff_k,
        "quarter_d0_eff_rank_M": result["quarter_d0_eff_rank_M"],
        "quarter_d0_eff_rank_K": result["quarter_d0_eff_rank_K"],
        "agreement_mean": mean,
        "agreement_sd": result["agreement_sd"],
        "agreement_t": t_stat,
        "pass_eff_M": bool(pass_m),
        "pass_eff_K": bool(pass_k),
        "pass_agreement": bool(pass_agree),
        "pass_all": bool(pass_m and pass_k and pass_agree),
        "match_score": float(score),
        "seconds": result["seconds"],
    }


def run_calibration(workers: int) -> dict[str, Any]:
    started = time.time()
    stage_a: list[dict[str, Any]] = []
    for k in (32, 48, 64):
        for w_mu, w_x in ((0.15, 0.15), (0.25, 0.15), (0.25, 0.25), (0.35, 0.20), (0.20, 0.30)):
            stage_a.append(
                {
                    "k": k,
                    "rho": 0.5,
                    "w_mu": w_mu,
                    "w_x": w_x,
                    "w_e": round(1.0 - w_mu - w_x, 10),
                    "phi_lo": 0.2,
                    "phi_hi": 0.8,
                }
            )
    trials: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for row in pool.map(_trial_star, [(k, CAL_DRAWS) for k in stage_a]):
            trials.append(row)
            print(
                f"[cal A] {row['knob_tag']}: effM {row['d0_eff_rank_M']:.1f} "
                f"effK {row['d0_eff_rank_K']:.1f} A {row['agreement_mean']:+.4f} "
                f"(t {row['agreement_t']:+.2f}) pass={row['pass_all']}",
                flush=True,
            )

    def stage_b_candidates(base: dict[str, Any]) -> list[dict[str, Any]]:
        out = []
        for rho in (0.3, 0.5, 0.7):
            for scale in (0.7, 1.0, 1.3):
                w_mu = min(0.6, base["knobs"]["w_mu"] * scale)
                w_x = min(0.6, base["knobs"]["w_x"] * scale)
                if w_mu + w_x >= 0.9:
                    continue
                knobs = dict(base["knobs"])
                knobs.update(
                    {
                        "rho": rho,
                        "w_mu": round(w_mu, 4),
                        "w_x": round(w_x, 4),
                        "w_e": round(1.0 - w_mu - w_x, 10),
                    }
                )
                if knob_tag(knobs) not in {t["knob_tag"] for t in trials}:
                    out.append(knobs)
        return out

    passing = [t for t in trials if t["pass_all"]]
    if not passing:
        eff_passing = sorted(
            (t for t in trials if t["pass_eff_M"] and t["pass_eff_K"]),
            key=lambda t: t["match_score"],
        )
        seeds = eff_passing[:2] if eff_passing else sorted(
            trials, key=lambda t: t["match_score"]
        )[:2]
        extra: list[dict[str, Any]] = []
        for seed_trial in seeds:
            extra.extend(stage_b_candidates(seed_trial))
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for row in pool.map(_trial_star, [(k, CAL_DRAWS) for k in extra]):
                trials.append(row)
                print(
                    f"[cal B] {row['knob_tag']}: effM {row['d0_eff_rank_M']:.1f} "
                    f"effK {row['d0_eff_rank_K']:.1f} A {row['agreement_mean']:+.4f} "
                    f"pass={row['pass_all']}",
                    flush=True,
                )
        passing = [t for t in trials if t["pass_all"]]

    record: dict[str, Any] = {
        "banner": BANNER,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "targets": {
            "d0_eff_rank_M": TARGET_EFF_M,
            "d0_eff_rank_K": TARGET_EFF_K,
            "band": EFF_BAND,
            "agreement_abs_bar": AGREE_ABS_BAR,
            "agreement_t_bar": AGREE_T_BAR,
        },
        "trial_draws": CAL_DRAWS,
        "trials": trials,
        "seconds": float(time.time() - started),
    }
    if passing:
        best = min(passing, key=lambda t: t["match_score"])
        record["status"] = "CALIBRATED"
        record["selected"] = best
    else:
        best = min(trials, key=lambda t: t["match_score"])
        record["status"] = "CALIBRATION_FAILED_REGIME_UNREACHED"
        record["closest"] = best
    (OUT / "calibration_record.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )
    print(f"calibration status: {record['status']}")
    if passing:
        print(json.dumps(best, indent=2))
    return record


def _trial_star(args: tuple[dict[str, Any], int]) -> dict[str, Any]:
    knobs, draws = args
    return trial(knobs, draws=draws)


# ---------------------------------------------------------------------------
# Sweep, prediction, holdout, finalize (Part 0.4, 0.7).

def load_calibrated_knobs() -> tuple[dict[str, Any], str]:
    record = json.loads((OUT / "calibration_record.json").read_text(encoding="utf-8"))
    if record["status"] != "CALIBRATED":
        raise AssertionError(
            "Calibration did not reach the regime; the registered escape fires "
            "before the sweep. See calibration_record.json."
        )
    knobs = record["selected"]["knobs"]
    return knobs, knob_tag(knobs)


def run_cells(cells: list[tuple[str, int, int]], workers: int, draws: int) -> None:
    knobs, tag = load_calibrated_knobs()
    for cell, author_mult, event_mult in cells:
        cell_path = OUT / f"cell_{cell}.csv"
        if cell_path.exists():
            print(f"[skip] {cell} exists")
            continue
        tasks = [
            {
                "cell": cell,
                "world": world,
                "author_mult": author_mult,
                "event_mult": event_mult,
                "knobs": knobs,
                "knob_tag": tag,
                "draws": draws,
                "ref_path": str(REF_PATH),
                "quarter_diagnostic": bool(cell == "base1x" and world == 0),
            }
            for world in range(WORLDS_PER_CELL)
        ]
        started = time.time()
        rows: list[dict[str, Any]] = []
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for row in pool.map(run_world, tasks):
                rows.append(row)
                print(
                    f"[{cell} w{row['world']}] A {row['agreement_mean']:+.4f} "
                    f"(sd {row['agreement_sd']:.4f}) effM {row['d0_eff_rank_M']:.1f} "
                    f"effK {row['d0_eff_rank_K']:.1f} {row['seconds']:.0f}s",
                    flush=True,
                )
        draw_rows = []
        for row in rows:
            for draw, value in enumerate(row.pop("draw_values")):
                draw_rows.append(
                    {
                        "cell": cell,
                        "world": row["world"],
                        "draw": draw,
                        "agreement": value,
                    }
                )
        pd.DataFrame(rows).to_csv(cell_path, index=False)
        pd.DataFrame(draw_rows).to_csv(OUT / f"draws_{cell}.csv", index=False)
        print(f"[{cell}] done in {time.time() - started:.0f}s -> {cell_path}")


def cell_summary(cell: str) -> dict[str, Any]:
    frame = pd.read_csv(OUT / f"cell_{cell}.csv")
    values = frame["agreement_mean"].to_numpy(dtype=float)
    mean = float(values.mean())
    se = float(values.std(ddof=1) / math.sqrt(len(values)))
    return {
        "cell": cell,
        "author_mult": int(frame["author_mult"].iloc[0]),
        "event_mult": int(frame["event_mult"].iloc[0]),
        "worlds": int(len(frame)),
        "agreement_mean": mean,
        "agreement_se": se,
        "rise": bool(mean > 0 and se > 0 and mean / se >= 2.0),
        "d0_eff_rank_M_mean": float(frame["d0_eff_rank_M"].mean()),
        "d0_eff_rank_K_mean": float(frame["d0_eff_rank_K"].mean()),
        "n_retained": int(frame["n_retained"].iloc[0]),
        "world_values": values.tolist(),
    }


def _log_odds(a: float) -> float:
    a = min(max(a, 1e-12), 1.0 - 1e-6)
    return math.log10(a / (1.0 - a))


def fit_axis(
    summaries: list[dict[str, Any]], mult_key: str
) -> dict[str, Any]:
    """WLS of log10(odds) on log10(mult) over qualifying cells (Part 0.7)."""
    points = []
    for row in summaries:
        mean, se = row["agreement_mean"], row["agreement_se"]
        qualifies = bool(mean > 0 and mean - 2.0 * se > 0)
        points.append(
            {
                "cell": row["cell"],
                "mult": row[mult_key],
                "agreement_mean": mean,
                "agreement_se": se,
                "qualifies": qualifies,
            }
        )
    qualifying = [p for p in points if p["qualifies"]]
    out: dict[str, Any] = {"points": points, "n_qualifying": len(qualifying)}
    if len(qualifying) < 2:
        out["status"] = "UNFITTABLE"
        return out
    x = np.log10([p["mult"] for p in qualifying])
    y = np.asarray([_log_odds(p["agreement_mean"]) for p in qualifying])
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
            for p in qualifying
        ]
    )
    w = 1.0 / np.maximum(dvar, 1e-12)
    x_bar = float(np.sum(w * x) / np.sum(w))
    y_bar = float(np.sum(w * y) / np.sum(w))
    denominator = float(np.sum(w * (x - x_bar) ** 2))
    if denominator <= 0:
        out["status"] = "UNFITTABLE"
        return out
    slope = float(np.sum(w * (x - x_bar) * (y - y_bar)) / denominator)
    intercept = y_bar - slope * x_bar
    log10_budget = (-intercept / slope) if slope > 0 else float("inf")
    out.update(
        {
            "status": "FITTED" if len(qualifying) >= 3 else "DEGENERATE",
            "exponent": slope,
            "intercept": float(intercept),
            "log10_half_agreement_mult": float(log10_budget),
            "half_agreement_mult": (
                float(10.0**log10_budget) if log10_budget < 300 else float("inf")
            ),
        }
    )
    return out


def bootstrap_axis(
    summaries: list[dict[str, Any]], mult_key: str, *, draws: int = 2000, seed: int = 11
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    slopes, budgets, predictions16 = [], [], []
    failures = 0
    for _ in range(draws):
        resampled = []
        for row in summaries:
            values = np.asarray(row["world_values"], dtype=float)
            sample = values[rng.integers(0, len(values), size=len(values))]
            mean = float(sample.mean())
            se = float(sample.std(ddof=1) / math.sqrt(len(sample)))
            resampled.append(
                {
                    "cell": row["cell"],
                    mult_key: row[mult_key],
                    "agreement_mean": mean,
                    "agreement_se": se,
                }
            )
        fit = fit_axis(resampled, mult_key)
        if fit["status"] in ("FITTED", "DEGENERATE") and fit["exponent"] > 0:
            slopes.append(fit["exponent"])
            budgets.append(min(fit["log10_half_agreement_mult"], 300.0))
            predictions16.append(fit["intercept"] + fit["exponent"] * math.log10(16.0))
        else:
            failures += 1
    def pct(values: list[float]) -> list[float] | None:
        if not values:
            return None
        return [float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))]
    return {
        "resamples": draws,
        "failed_or_nonpositive": failures,
        "exponent_ci95": pct(slopes),
        "log10_half_agreement_mult_ci95": pct(budgets),
        "log_odds_pred_16x_ci95": pct(predictions16),
    }


def run_predict() -> dict[str, Any]:
    summaries = {cell: cell_summary(cell) for cell, _, _ in SWEEP_CELLS}
    author_rows = [summaries[c] for c in ("base1x", "authors_x2", "authors_x4", "authors_x8")]
    event_rows = [summaries[c] for c in ("base1x", "events_x2", "events_x4", "events_x8")]
    fit_authors = fit_axis(author_rows, "author_mult")
    fit_events = fit_axis(event_rows, "event_mult")
    boot_authors = bootstrap_axis(author_rows, "author_mult")
    boot_events = bootstrap_axis(event_rows, "event_mult")
    prediction: dict[str, Any] = {
        "banner": BANNER,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "fit_authors": fit_authors,
        "fit_events": fit_events,
        "bootstrap_authors": boot_authors,
        "bootstrap_events": boot_events,
    }
    if fit_events.get("status") in ("FITTED", "DEGENERATE"):
        log_odds_16 = fit_events["intercept"] + fit_events["exponent"] * math.log10(16.0)
        odds = 10.0 ** log_odds_16
        prediction["holdout_prediction"] = {
            "cell": HOLDOUT_CELL[0],
            "log10_odds_pred": float(log_odds_16),
            "agreement_pred": float(odds / (1.0 + odds)),
            "factor2_band_log10": float(math.log10(2.0)),
        }
    else:
        prediction["holdout_prediction"] = {
            "cell": HOLDOUT_CELL[0],
            "status": "EVENTS_AXIS_UNFITTABLE_HOLDOUT_IS_A_PROBE",
        }
    (OUT / "prediction_16x.json").write_text(
        json.dumps(prediction, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: prediction[k] for k in ("fit_authors", "fit_events", "holdout_prediction")}, indent=2))
    return prediction


def run_holdout(workers: int, draws: int) -> None:
    if not (OUT / "prediction_16x.json").exists():
        raise AssertionError(
            "prediction_16x.json missing: the held-out cell must be computed "
            "AFTER the law's prediction is persisted (Part 0.4)."
        )
    run_cells([HOLDOUT_CELL], workers, draws)


def adjudicate() -> dict[str, Any]:
    prediction = json.loads((OUT / "prediction_16x.json").read_text(encoding="utf-8"))
    summaries = {cell: cell_summary(cell) for cell, _, _ in SWEEP_CELLS}
    holdout = cell_summary(HOLDOUT_CELL[0])
    fit_authors, fit_events = prediction["fit_authors"], prediction["fit_events"]

    rise_cells = [
        c for c, s in summaries.items() if s["rise"] and c != "base1x"
    ]
    lean_a = {
        "lean": "a",
        "rule": "at least one swept cell (mult >= 2) rises off zero (mean/SE >= 2)",
        "rising_cells": rise_cells,
        "verdict": "HOLD" if rise_cells else "MISS",
    }

    # Part 0.7 letter: FITTABLE requires >= 3 qualifying cells; DEGENERATE
    # (2-cell) fits report a slope but cannot carry lean (b), dominance at
    # registered standard, or a lean (c) hold.
    fa, fe = fit_authors.get("status"), fit_events.get("status")
    author_fitted = fa == "FITTED"
    events_fitted = fe == "FITTED"
    author_any = fa in ("FITTED", "DEGENERATE")
    events_any = fe in ("FITTED", "DEGENERATE")
    lean_b: dict[str, Any] = {
        "lean": "b",
        "rule": "author-axis exponent exceeds events-axis exponent "
        "(both axes FITTABLE per Part 0.7: >= 3 qualifying cells)",
        "gamma_authors": fit_authors.get("exponent"),
        "gamma_events": fit_events.get("exponent"),
        "status_authors": fa,
        "status_events": fe,
    }
    if author_fitted and events_fitted:
        lean_b["verdict"] = (
            "HOLD" if fit_authors["exponent"] > fit_events["exponent"] else "MISS"
        )
    elif events_fitted and not author_fitted:
        lean_b["verdict"] = "MISS"
        lean_b["note"] = (
            "events axis FITTED; author axis not FITTABLE at the registered "
            ">= 3-qualifying-cell standard"
            + (
                " (DEGENERATE 2-cell slope reported as companion only)"
                if fa == "DEGENERATE"
                else " (author axis never leaves the floor)"
            )
        )
    elif author_fitted and not events_fitted:
        lean_b["verdict"] = (
            "HOLD"
            if fe == "UNFITTABLE"
            else "MISS"
        )
        lean_b["note"] = (
            "author axis FITTED; events axis "
            + ("never leaves the floor" if fe == "UNFITTABLE" else "DEGENERATE only")
        )
        if fe == "DEGENERATE":
            lean_b["note"] += (
                " — comparison not measurable at registered standard, "
                "adjudicated MISS (cannot demonstrate the hold)"
            )
    else:
        lean_b["verdict"] = "NOT_MEASURABLE"
        lean_b["note"] = "neither axis FITTED at the registered standard"

    if author_fitted and events_fitted:
        dominant = (
            ("authors", fit_authors)
            if fit_authors["exponent"] >= fit_events["exponent"]
            else ("events", fit_events)
        )
    elif author_fitted:
        dominant = ("authors", fit_authors)
    elif events_fitted:
        dominant = ("events", fit_events)
    elif author_any or events_any:
        dominant = (
            ("authors", fit_authors)
            if author_any and (
                not events_any
                or fit_authors["exponent"] >= fit_events["exponent"]
            )
            else ("events", fit_events)
        )
    else:
        dominant = (None, None)

    holdout_check: dict[str, Any] = {"cell": holdout["cell"]}
    pred = prediction.get("holdout_prediction", {})
    if "log10_odds_pred" in pred:
        observed_ok = holdout["agreement_mean"] > 0
        log_odds_obs = _log_odds(holdout["agreement_mean"]) if observed_ok else None
        holdout_check.update(
            {
                "agreement_obs": holdout["agreement_mean"],
                "agreement_se": holdout["agreement_se"],
                "agreement_pred": pred["agreement_pred"],
                "log10_odds_pred": pred["log10_odds_pred"],
                "log10_odds_obs": log_odds_obs,
                "within_factor2": bool(
                    observed_ok
                    and abs(log_odds_obs - pred["log10_odds_pred"]) <= math.log10(2.0)
                ),
            }
        )
    else:
        holdout_check.update(
            {
                "status": "PROBE_ONLY_NO_PREDICTION",
                "agreement_obs": holdout["agreement_mean"],
                "agreement_se": holdout["agreement_se"],
                "within_factor2": False,
            }
        )

    lean_c: dict[str, Any] = {
        "lean": "c",
        "rule": ".5-agreement budget in [4,50] on the dominant axis AND 16x "
        "held-out within factor-2 (odds domain); DEGENERATE fits cannot hold",
        "dominant_axis": dominant[0],
    }
    if dominant[0] is None:
        lean_c["verdict"] = "NOT_MEASURABLE"
    else:
        budget = dominant[1].get("half_agreement_mult", float("inf"))
        lean_c["half_agreement_mult"] = budget
        in_band = bool(4.0 <= budget <= 50.0)
        lean_c["budget_in_band"] = in_band
        degenerate = dominant[1]["status"] == "DEGENERATE"
        lean_c["degenerate_fit"] = degenerate
        lean_c["holdout_within_factor2"] = holdout_check.get("within_factor2", False)
        lean_c["verdict"] = (
            "HOLD"
            if in_band and holdout_check.get("within_factor2") and not degenerate
            else "MISS"
        )

    pivot_fires = bool(
        not summaries["authors_x8"]["rise"] and not summaries["events_x8"]["rise"]
    )
    pivot = {
        "registered_rule": "agreement stays ~0 at the largest swept cells "
        "(both 8x cells fail the rise criterion)",
        "authors_x8_rise": summaries["authors_x8"]["rise"],
        "events_x8_rise": summaries["events_x8"]["rise"],
        "fires": pivot_fires,
    }
    if pivot_fires:
        verdict = "SIZE_ONLY_RESCUE_FALSIFIED_D3_MUST_CHANGE_COMPOSITION_NOT_SCALE"
        handoff = (
            "Registered hand-off: the D3 design question becomes COMPOSITION "
            "(shared-context events, within-author condition pairing), not scale."
        )
    else:
        verdict = (
            f"PANEL_SIZING_LAW_MEASURED_DOMINANT_AXIS_"
            f"{(dominant[0] or 'NONE').upper()}"
        )
        handoff = ""

    return {
        "lean_a": lean_a,
        "lean_b": lean_b,
        "lean_c": lean_c,
        "pivot": pivot,
        "holdout_validation": holdout_check,
        "verdict": verdict,
        "handoff": handoff,
        "cell_summaries": {**summaries, holdout["cell"]: holdout},
    }


def run_finalize() -> None:
    calibration = json.loads((OUT / "calibration_record.json").read_text(encoding="utf-8"))
    prediction = json.loads((OUT / "prediction_16x.json").read_text(encoding="utf-8"))
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    adjudication = adjudicate()
    all_cells = [c for c, _, _ in SWEEP_CELLS] + [HOLDOUT_CELL[0]]
    pd.DataFrame(
        [
            {k: v for k, v in adjudication["cell_summaries"][c].items() if k != "world_values"}
            for c in all_cells
        ]
    ).to_csv(OUT / "cells.csv", index=False)
    decision = {
        "experiment": "M4-F1_panel_sizing_law",
        "banner": BANNER,
        "tier": "EXPLORATORY",
        "registered_spec": "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md#M4-F1",
        "part0_registered_in": "reports/SUICA_M4_F1_PANEL_SIZING_REPORT.md Part 0 (before run)",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "worlds_per_cell": WORLDS_PER_CELL,
        "draws_per_world": DRAWS,
        "gates": gates,
        "calibration": {
            "status": calibration["status"],
            "selected": calibration.get("selected"),
            "n_trials": len(calibration["trials"]),
        },
        "fits": {
            "authors": prediction["fit_authors"],
            "events": prediction["fit_events"],
            "bootstrap_authors": prediction["bootstrap_authors"],
            "bootstrap_events": prediction["bootstrap_events"],
            "holdout_prediction_persisted_at": prediction["timestamp_utc"],
        },
        "adjudication": {
            k: v for k, v in adjudication.items() if k != "cell_summaries"
        },
        "label_free": True,
        "claim_boundary": (
            "Synthetic sizing law in a composed world calibrated to the opened "
            "PANDORA D-panel regime; licenses a D3 panel-size DESIGN prior only. "
            "No claim about the real relation field's content, personality, "
            "emotion, diagnosis, or any individual."
        ),
    }
    (OUT / "decision.json").write_text(
        json.dumps(decision, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(decision["adjudication"], indent=2))


# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=["gates", "calibrate", "sweep", "predict", "holdout", "finalize", "all"],
        default="all",
    )
    parser.add_argument("--workers", type=int, default=max(2, min(6, (os.cpu_count() or 4) - 2)))
    parser.add_argument("--draws", type=int, default=DRAWS)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if not REF_PATH.exists():
        raise AssertionError(
            "realtext_panel_reference.json missing; run the reference extraction "
            "first (session log)."
        )
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    if args.stage in ("gates", "all"):
        run_gates()
    if args.stage in ("calibrate", "all"):
        if not (OUT / "calibration_record.json").exists():
            run_calibration(args.workers)
        else:
            print("[skip] calibration_record.json exists")
    if args.stage in ("sweep", "all"):
        run_cells(SWEEP_CELLS, args.workers, args.draws)
    if args.stage in ("predict", "all"):
        if not (OUT / "prediction_16x.json").exists():
            run_predict()
        else:
            print("[skip] prediction_16x.json exists")
    if args.stage in ("holdout", "all"):
        run_holdout(args.workers, args.draws)
    if args.stage in ("finalize", "all"):
        run_finalize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
