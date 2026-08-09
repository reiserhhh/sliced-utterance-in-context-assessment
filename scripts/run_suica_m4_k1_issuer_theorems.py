#!/usr/bin/env python3
"""M4-K1 -- the issuer theorems (IDT T3/T5) on the deployed machinery.

Registered spec: docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md section "M4-K1 -- Issuer
theorems: the norm field's three-way split on the deployed machinery"
(REGISTERED 2026-08-09, BEFORE RUN, commit c902498). Part 0 register-notes
(operationalizations for everything the registration left as an implementation
choice) are in reports/SUICA_M4_K1_ISSUER_THEOREMS_REPORT.md Part 0, written
BEFORE this script's arm stages were ever run.

Machinery reuse (registration: "import or minimal extraction with file:line
provenance -- no reimplementation of existing constructions"):
  * world generator          f2.generate_world_composed  (scripts/run_suica_m4_f2_composition.py:129-198)
  * occasion designs         f2.occasion_labels          (f2:96-118)
  * common-budget layout     f2.build_layout_common      (f2:205-222)
  * deployed gauge path      f2.run_axis1_world          (f2:276-370)
        -> f1.featurize_panel (scripts/run_suica_m4_f1_panel_sizing.py:166-229)
        -> e1.calibrate_d0_soft / project_soft / deployed_soft_field /
           field_agreement (scripts/run_suica_m4_e1_convention_gap.py:160-264)
  * paired CI                f2._paired_ci               (f2:1008-1025)
Nothing in suica_core/ is touched (frozen operators are READ-ONLY).

Stages (foreground, resumable, artifacts under results/m4_k1_issuer/):
  --stage part0     G0,G1,G2,G3,G4,G5 -> gates.json  (MUST run, and the report's
                    Part 0 MUST be written, before any arm stage)
  --stage abs       R-abs arms ({shared,free} x 5 norm arms x 8 worlds)
  --stage rel       R-rel arms ({shared,free} x {0,0.5,1,2}x shift x 8 worlds)
  --stage finalize  lean adjudication + pivots -> decision.json
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
from scipy import stats
from scipy.spatial.distance import cdist

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import suica_core.v8_realtext_relation_field as v8  # noqa: E402

BANNER = "synthetic worlds calibrated to an opened-panel regime, exploratory"

# --- registered constants (docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md, M4-K1) ------
MASTER_SEED = 20260809          # fresh, for all NEW arms
WORLDS = 8
KAPPA = 1.0                     # the registered shared-occasion / free design
N_ORACLE = 512                  # "norm from N_or = 512 fresh authors"
EST_SIZES = (8, 32, 128)
BIASED_SIZE = 32
EQUIV_MARGIN = 0.006540815826681557   # L5's m, registered to full precision
SHIFT_SCALES = (0.5, 1.0, 2.0)
L5_GATED_SCALES = (0.5, 1.0)
BOOT_DRAWS = 2000
TIE_MARGIN = 1e-6
CARD_DIFF_TOL = 1e-9
L3_SLOPE_BAND = (-1.35, -0.65)

# --- Part-0 operationalizations (see report Part 0; fixed BEFORE any arm) -----
N_OCC = 8            # R-abs occasions per panel author == F2's own MIN_RETAINED_EVENTS
T_FREE = 64          # R-abs free-design occasion universe (finite; f2:96-118 note)
ABS_CONTEXT = "K1"   # single occasion-shock jurisdiction for the norm-field reader
PILOT_WORLD = 9001   # reserved-seed pilot world; never adjudicated

OUT = ROOT / "results" / "m4_k1_issuer"
F2_OUT = ROOT / "results" / "m4_f2_composition"
F1_OUT = ROOT / "results" / "m4_f1_panel_sizing"
F1_CALIBRATION = F1_OUT / "calibration_record.json"
REF_PATH = F1_OUT / "realtext_panel_reference.json"


def _load_script(name: str) -> Any:
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_F2 = None


def f2() -> Any:
    """The M4-F2 script module (verbatim generator/design/gauge machinery)."""
    global _F2
    if _F2 is None:
        _F2 = _load_script("run_suica_m4_f2_composition.py")
    return _F2


def knobs_and_tag() -> tuple[dict[str, Any], str]:
    record = json.loads(F1_CALIBRATION.read_text(encoding="utf-8"))
    if record["status"] != "CALIBRATED":
        raise AssertionError("M4-F1 calibration_record.json is not CALIBRATED.")
    knobs = record["selected"]["knobs"]
    return knobs, f2().f1().knob_tag(knobs)


def world_seed_for(group: str, world: int, knob_tag: str) -> int:
    return v8.stable_bucket(
        f"{MASTER_SEED}-{group}-w{world}-{knob_tag}",
        salt="m4k1-world",
        modulus=2**63 - 1,
    )


# ===========================================================================
# R-abs -- the absolute-card reader, entirely in post-map representation space.
#
# G2 identifies the representation: the 64-dim frozen event vector, the LAST
# object indexed by (author, occasion) that the deployed gauge consumes, and the
# last object COMMON to both of its branches -- `values` in v8.family_features
# (suica_core/v8_realtext_relation_field.py:225), feeding the M branch (v8:229-241)
# and the K branch (v8:243-263); batched as `values` in f1.marginal_features_batch
# (f1:117) / f1.transition_features_batch (f1:138) via f1.featurize_panel (f1:195).
# Everything downstream is per-AUTHOR; the pairwise/relational step is
# e1.deployed_soft_field (e1:235-247) -> v8.soft_relation_matrix (v8:892-895).
# ===========================================================================

_LABEL_OVERRIDE: list[np.ndarray] | None = None
_ORIG_OCCASION_LABELS = None


def _occasion_labels_patched(counts, mode):  # noqa: ANN001
    """f2.occasion_labels with this leg's occasion DESIGN injected.

    The generator body (f2:129-198) runs verbatim; only the object f2's own
    `occasion_labels` (f2:96-118) produces is supplied here, which F2's own
    docstring explicitly names as the alternative it declined ("rather than
    picking an arbitrary finite occasion-universe size").
    """
    if _LABEL_OVERRIDE is not None:
        return _LABEL_OVERRIDE
    return _ORIG_OCCASION_LABELS(counts, mode)


def abs_occasion_labels(design: str, n_panel: int, seed: int) -> list[np.ndarray]:
    rng = np.random.default_rng(seed)
    labels: list[np.ndarray] = []
    for _ in range(n_panel):
        if design == "shared":
            labels.append(np.arange(N_OCC))
        elif design == "free":
            labels.append(np.sort(rng.choice(T_FREE, size=N_OCC, replace=False)))
        else:
            raise ValueError(design)
    labels.extend(np.arange(T_FREE) for _ in range(N_ORACLE))
    return labels


def build_abs_world(
    design: str, n_panel: int, knobs: dict[str, Any], world_seed: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Panel events (n_panel, N_OCC, 64), norm events (N_ORACLE, T_FREE, 64),
    panel occasion labels (n_panel, N_OCC)."""
    global _LABEL_OVERRIDE, _ORIG_OCCASION_LABELS
    module = f2()
    counts = [N_OCC] * n_panel + [T_FREE] * N_ORACLE
    contexts = [ABS_CONTEXT] * len(counts)
    labels = abs_occasion_labels(design, n_panel, world_seed % (2**31 - 1))
    _ORIG_OCCASION_LABELS = module.occasion_labels
    _LABEL_OVERRIDE = labels
    module.occasion_labels = _occasion_labels_patched
    try:
        vectors = module.generate_world_composed(
            counts, contexts, knobs, KAPPA, design, world_seed
        )
    finally:
        module.occasion_labels = _ORIG_OCCASION_LABELS
        _LABEL_OVERRIDE = None
    panel = np.stack(vectors[:n_panel])
    norm = np.stack(vectors[n_panel:])
    return panel, norm, np.stack(labels[:n_panel])


def norm_arm_indices(norm_events: np.ndarray, world_seed: int) -> dict[str, np.ndarray]:
    """Norm samples. est* are nested prefixes of the oracle pool; biased32 is
    drawn from the top half of the pool's author-effect first principal
    coordinate (operationalized post-map: the author's mean event vector)."""
    arms: dict[str, np.ndarray] = {"oracle": np.arange(N_ORACLE)}
    for size in EST_SIZES:
        arms[f"est{size}"] = np.arange(size)
    author_mean = norm_events.mean(axis=1)                      # (N_ORACLE, 64)
    centered = author_mean - author_mean.mean(axis=0, keepdims=True)
    _u, _s, vt = np.linalg.svd(centered, full_matrices=False)
    scores = centered @ vt[0]
    top_half = np.argsort(scores)[N_ORACLE // 2:]
    rng = np.random.default_rng(
        v8.stable_bucket(f"{world_seed}", salt="m4k1-biased", modulus=2**31 - 1)
    )
    arms[f"biased{BIASED_SIZE}"] = np.sort(
        rng.choice(top_half, size=BIASED_SIZE, replace=False)
    )
    return arms


def cards_for_arm(
    panel: np.ndarray, labels: np.ndarray, mu: np.ndarray
) -> dict[str, np.ndarray]:
    """Both registered readers, norms ACTUALLY subtracted (no algebraic cancel).

    reader_B (primary): c_i^(h) = mean_{o in H_h}( x_i(o) - mu(o) ).
    reader_A (T3(c) hypothesis, "a common probe/gallery norm"):
             c_i^(h) = mean_{o in H_h} x_i(o) - mean_{o in O_i} mu(o).
    """
    half = N_OCC // 2
    dev = panel - mu[labels]                       # (n, N_OCC, 64)  norms subtracted
    nu_full = mu[labels].mean(axis=1)              # (n, 64) author-universe norm
    return {
        "B1": dev[:, :half].mean(axis=1),
        "B2": dev[:, half:].mean(axis=1),
        "A1": panel[:, :half].mean(axis=1) - nu_full,
        "A2": panel[:, half:].mean(axis=1) - nu_full,
    }


def reader_metrics(gallery: np.ndarray, probes: np.ndarray) -> dict[str, Any]:
    dist = cdist(probes, gallery)
    order = np.argpartition(dist, 1, axis=1)[:, :2]
    rows = np.arange(len(dist))
    pair = dist[rows[:, None], order]
    swap = pair[:, 0] > pair[:, 1]
    best = np.where(swap, order[:, 1], order[:, 0])
    margin = np.abs(pair[:, 1] - pair[:, 0])
    correct = (best == rows).astype(float)
    cos = np.sum(gallery * probes, axis=1) / np.maximum(
        np.linalg.norm(gallery, axis=1) * np.linalg.norm(probes, axis=1), 1e-300
    )
    return {
        "nn": best,
        "margin": margin,
        "correct": correct,
        "rank1": float(correct.mean()),
        "readability": cos,
        "readability_mean": float(cos.mean()),
        "self_dist_mean": float(dist[rows, rows].mean()),
    }


def run_abs_world(design: str, world: int, n_panel: int, knobs: dict[str, Any],
                  knob_tag: str, group: str = "abs") -> dict[str, Any]:
    started = time.time()
    seed = world_seed_for(group, world, knob_tag)
    panel, norm_events, labels = build_abs_world(design, n_panel, knobs, seed)
    arms = norm_arm_indices(norm_events, seed)
    mu = {name: norm_events[idx].mean(axis=0) for name, idx in arms.items()}

    used = np.unique(labels)
    out: dict[str, Any] = {
        "design": design, "world": world, "world_seed": int(seed),
        "n_panel": int(n_panel), "n_occ": N_OCC,
        "mean_pairwise_occasion_overlap": float(
            _mean_overlap(labels) if design == "free" else float(N_OCC)
        ),
        "arms": {}, "seconds": 0.0,
    }
    ref = {}
    oracle_cards = cards_for_arm(panel, labels, mu["oracle"])
    oracle_pair = {
        key: cdist(value, value) for key, value in oracle_cards.items()
    }
    for name in ("oracle",) + tuple(f"est{s}" for s in EST_SIZES) + (f"biased{BIASED_SIZE}",):
        cards = oracle_cards if name == "oracle" else cards_for_arm(panel, labels, mu[name])
        entry: dict[str, Any] = {}
        for reader in ("B", "A"):
            met = reader_metrics(cards[f"{reader}1"], cards[f"{reader}2"])
            entry[reader] = met
        # norm-field quality (G4 / L3): variance of the norm error on used occasions
        d_mu = mu[name][used] - mu["oracle"][used]
        entry["mu_err_var"] = float(np.mean(d_mu**2))
        entry["mu_err_rms"] = float(np.sqrt(np.mean(d_mu**2)))
        entry["mu_err_occasion_constant_rms"] = float(
            np.sqrt(np.mean(d_mu.mean(axis=0) ** 2))
        )
        if name == "oracle":
            ref = entry
        for reader in ("B", "A"):
            met, base = entry[reader], ref[reader]
            tie = (met["margin"] < TIE_MARGIN) | (base["margin"] < TIE_MARGIN)
            flips = int(np.sum((met["nn"] != base["nn"]) & ~tie))
            entry[f"{reader}_flips_vs_oracle"] = flips
            entry[f"{reader}_ties_excluded"] = int(tie.sum())
            entry[f"{reader}_rank1"] = met["rank1"]
            entry[f"{reader}_readability"] = met["readability_mean"]
            entry[f"{reader}_correct"] = met["correct"]
        # card-difference matrices (T3(b)) vs the oracle arm, both halves
        rels, trans = [], []
        for reader in ("B", "A"):
            for half in ("1", "2"):
                key = f"{reader}{half}"
                c_arm, c_or = cards[key], oracle_cards[key]
                d_arm = cdist(c_arm, c_arm)
                d_or = oracle_pair[key]
                scale = float(d_or.max()) or 1.0
                rels.append(float(np.abs(d_arm - d_or).max() / scale))
                e = c_arm - c_or
                trans.append(
                    float(np.linalg.norm(e - e.mean(axis=0), axis=1).max() / scale)
                )
        entry["carddiff_rel_max_B"] = max(rels[0], rels[1])
        entry["carddiff_rel_max_A"] = max(rels[2], rels[3])
        entry["carddiff_translation_max_B"] = max(trans[0], trans[1])
        entry["carddiff_translation_max_A"] = max(trans[2], trans[3])
        out["arms"][name] = entry
    out["seconds"] = float(time.time() - started)
    return out


def _mean_overlap(labels: np.ndarray) -> float:
    sample = labels[: min(200, len(labels))]
    onehot = np.zeros((len(sample), T_FREE), dtype=float)
    for i, row in enumerate(sample):
        onehot[i, row] = 1.0
    gram = onehot @ onehot.T
    iu = np.triu_indices(len(sample), 1)
    return float(gram[iu].mean())


# ===========================================================================
# R-rel -- the deployed relational gauge, unchanged, under calibrated pre-map
# common occasion shifts.
# ===========================================================================

def _author_deviation_rms(vectors: list[np.ndarray], labels: list[np.ndarray],
                          contexts: list[str]) -> float:
    """RMS over (author, dim) of the author's mean deviation from the
    within-(context,occasion) norm, at the RESPONSE level. Computed on the
    SHARED design's unshifted world (in the free design every occasion has one
    author and the quantity is identically 0)."""
    sums: dict[tuple[str, int], np.ndarray] = {}
    counts: dict[tuple[str, int], int] = {}
    for i, vec in enumerate(vectors):
        for t in range(len(vec)):
            key = (contexts[i], int(labels[i][t]))
            if key in sums:
                sums[key] += vec[t]
                counts[key] += 1
            else:
                sums[key] = vec[t].copy()
                counts[key] = 1
    devs = []
    for i, vec in enumerate(vectors):
        acc = np.zeros(vec.shape[1])
        for t in range(len(vec)):
            key = (contexts[i], int(labels[i][t]))
            acc += vec[t] - sums[key] / counts[key]
        devs.append(acc / len(vec))
    return float(np.sqrt(np.mean(np.stack(devs) ** 2)))


_SHIFT_STATE: dict[str, Any] = {}
_ORIG_GENERATE = None


def _generate_shifted(counts, contexts, knobs, kappa, occasion_mode, world_seed):  # noqa: ANN001
    vectors = _ORIG_GENERATE(counts, contexts, knobs, kappa, occasion_mode, world_seed)
    scale = float(_SHIFT_STATE.get("scale", 0.0))
    if scale == 0.0:
        return vectors
    labels = _ORIG_OCCASION_LABELS_REL(counts, occasion_mode)
    shared_labels = _ORIG_OCCASION_LABELS_REL(counts, "shared")
    base = _ORIG_GENERATE(counts, contexts, knobs, kappa, "shared", world_seed)
    rms = _author_deviation_rms(base, shared_labels, contexts)
    n_lab = int(max(int(lab.max()) for lab in labels)) + 1
    rng = np.random.default_rng(
        v8.stable_bucket(
            f"{world_seed}-{occasion_mode}", salt="m4k1-shift", modulus=2**63 - 1
        )
    )
    delta = rng.normal(size=(n_lab, vectors[0].shape[1])) * (scale * rms)
    _SHIFT_STATE["calibration_rms"] = rms
    _SHIFT_STATE["shift_sigma"] = scale * rms
    return [vec + delta[labels[i]] for i, vec in enumerate(vectors)]


_ORIG_OCCASION_LABELS_REL = None


def _rel_world(task: dict[str, Any]) -> dict[str, Any]:
    global _ORIG_GENERATE, _ORIG_OCCASION_LABELS_REL
    module = f2()
    module.MASTER_SEED = MASTER_SEED
    _ORIG_GENERATE = module.generate_world_composed
    _ORIG_OCCASION_LABELS_REL = module.occasion_labels
    _SHIFT_STATE.clear()
    _SHIFT_STATE["scale"] = float(task.get("shift_scale", 0.0))
    module.generate_world_composed = _generate_shifted
    try:
        row = module.run_axis1_world(task)
    finally:
        module.generate_world_composed = _ORIG_GENERATE
    row["shift_scale"] = float(task.get("shift_scale", 0.0))
    row["calibration_rms"] = float(_SHIFT_STATE.get("calibration_rms", float("nan")))
    row["shift_sigma"] = float(_SHIFT_STATE.get("shift_sigma", 0.0))
    row.pop("draw_values", None)
    return row


def rel_task(design: str, world: int, scale: float, knobs: dict[str, Any],
             knob_tag: str) -> dict[str, Any]:
    return {
        "cell": f"rel_{design}_s{scale:g}",
        "world": world,
        "seed_group": "rel",
        "corpus_tag": "m4k1",
        "world_salt": "m4k1-world",
        "budget_label": "k1.0",
        "layout": "common",
        "kappa": KAPPA,
        "occasion_mode": design,
        "knobs": knobs,
        "knob_tag": knob_tag,
        "draws": 20,
        "ref_path": str(REF_PATH),
        "shift_scale": scale,
    }


# ===========================================================================
# Part 0 gates.
# ===========================================================================

def gate_g0(knobs: dict[str, Any], knob_tag: str) -> dict[str, Any]:
    module = f2()
    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    aid, ctx, spl, common, raw = module.build_layout_common(reference)
    meta = pd.DataFrame(
        {"author_id": aid, "context": ctx, "split": spl, "event_count": common}
    )
    spec = module.f1().load_spec()
    e1 = module.f1().e1()
    eval_mask = meta["split"].isin(["D1", "D2"]).to_numpy()
    resolved = e1.resolved_contexts(meta.loc[eval_mask], spec.minimum_context_authors)
    retained = np.flatnonzero(
        eval_mask
        & meta["context"].astype(str).isin(resolved).to_numpy()
        & (meta["event_count"].to_numpy() >= module.MIN_RETAINED_EVENTS)
    )
    hist = {int(k): int(v) for k, v in sorted(pd.Series(common).value_counts().items())}
    return {
        "gate": "G0",
        "description": "F2 panel dimensions extracted and pinned; analysis grain",
        "source": str(REF_PATH),
        "f2_authors_per_world": int(len(aid)),
        "f2_events_allocated_total": int(sum(common)),
        "f2_events_raw_total": int(sum(raw)),
        "f2_events_per_author_multiset": hist,
        "f2_contexts": sorted(set(ctx)),
        "f2_n_retained_by_deployed_gauge": int(len(retained)),
        "f2_min_retained_events_floor": int(module.MIN_RETAINED_EVENTS),
        "knobs": knobs,
        "knob_tag": knob_tag,
        "rabs_authors_per_world": int(len(aid)),
        "rabs_occasions_per_author": N_OCC,
        "rabs_free_universe": T_FREE,
        "rabs_norm_pool": N_ORACLE,
        "grain": "per-author identification events; authors within world; worlds as strata",
        "pass": True,
    }


def gate_g1() -> dict[str, Any]:
    """Reload F2's persisted axis-1 CSVs and re-derive the paired deltas; must
    equal decision.json bit-exactly at full float precision."""
    module = f2()
    decision = json.loads((F2_OUT / "decision.json").read_text(encoding="utf-8"))
    checks, all_exact = {}, True
    for tag in ("k05", "k10"):
        free = pd.read_csv(F2_OUT / f"axis1_cell_free_{tag}.csv").sort_values("world")
        shared = pd.read_csv(F2_OUT / f"axis1_cell_shared_{tag}.csv").sort_values("world")
        diffs = (
            shared["agreement_mean"].to_numpy() - free["agreement_mean"].to_numpy()
        )
        got = {
            "free_mean": float(free["agreement_mean"].mean()),
            "shared_mean": float(shared["agreement_mean"].mean()),
            **module._paired_ci(diffs),
        }
        ref = decision["adjudication"]["paired_differences"][tag]
        exact = {k: bool(got[k] == ref[k]) for k in got if k in ref}
        all_exact = all_exact and all(exact.values())
        checks[tag] = {
            "rederived": got,
            "persisted": {k: ref[k] for k in got if k in ref},
            "bit_exact": exact,
            "max_abs_diff": max(
                abs(got[k] - ref[k]) for k in got if k in ref and isinstance(ref[k], float)
            ),
        }
    return {
        "gate": "G1",
        "description": "F2 anchor re-derived bit-exactly from persisted axis-1 CSVs",
        "source": str(F2_OUT),
        "checks": checks,
        "equivalence_margin_m": EQUIV_MARGIN,
        "m_equals_quarter_of_k10_paired_mean": bool(
            EQUIV_MARGIN
            == 0.25 * decision["adjudication"]["paired_differences"]["k10"]["mean"]
        ),
        "pass": bool(all_exact),
    }


G2_VERDICT = {
    "gate": "G2",
    "description": (
        "structural audit: does the deployed gauge consume only within-occasion "
        "between-author contrasts post-map?"
    ),
    "representation_for_R_abs": (
        "the 64-dim frozen event vector -- the last object indexed by "
        "(author, occasion) that the gauge consumes, and the last object COMMON "
        "to both of its branches"
    ),
    "representation_citations": [
        "suica_core/v8_realtext_relation_field.py:171-188 frozen_event_vector (text -> R^64)",
        "suica_core/v8_realtext_relation_field.py:303-308 build_feature_panel stacks per-event vectors",
        "suica_core/v8_realtext_relation_field.py:225 family_features `values` (the common per-event object)",
        "suica_core/v8_realtext_relation_field.py:229-241 M branch consumes `values`",
        "suica_core/v8_realtext_relation_field.py:243-263 K branch consumes the same `values`",
        "scripts/run_suica_m4_f1_panel_sizing.py:195 featurize_panel `path = vectors[offset::2]`",
        "scripts/run_suica_m4_f1_panel_sizing.py:117 marginal_features_batch `values`",
        "scripts/run_suica_m4_f1_panel_sizing.py:138 transition_features_batch `values`",
    ],
    "pairwise_relational_step_citations": [
        "scripts/run_suica_m4_e1_convention_gap.py:235-247 deployed_soft_field",
        "suica_core/v8_realtext_relation_field.py:892-895 soft_relation_matrix",
        "suica_core/v8_realtext_relation_field.py:898-902 _soft_cross_covariance",
        "suica_core/v8_realtext_relation_field.py:376-382 _center / _cross_covariance "
        "(the first and only between-author centering, applied to per-AUTHOR feature rows)",
    ],
    "evidence_against_branch_A": [
        "v8:229 `mean = values.mean(axis=0)` -- the author's own ABSOLUTE path mean "
        "enters M directly (v8:241): a first-order norm-position term",
        "v8:239-240 `projections = values @ marginal_directions.T` and their quantiles "
        "are absolute, not contrasts",
        "v8:246 `lag_product = np.mean(previous * following, axis=0)` is quadratic in "
        "absolute position",
        "v8:258 `np.tanh(previous @ first) * np.tanh(following @ second)` is nonlinear "
        "in absolute position",
        "e1:191 project_soft standardizes against a FIXED D0-fit center "
        "(v8:488-493 _fit_standardizer), not an occasion-wise contrast",
        "f1:195 replicate paths are author-specific occasion subsets and f1:235-247 "
        "half_indices are author-seeded, so a common PRE-map occasion shift lands as "
        "an AUTHOR-SPECIFIC post-map displacement even in the linear M-mean term",
    ],
    "branch": "B",
    "branch_meaning": (
        "norm-position enters the deployed gauge directly; L5's leakage has a "
        "first-order term, not only map curvature"
    ),
    "pass": True,
}


def gate_g3(knobs: dict[str, Any], knob_tag: str, n_panel: int,
            pilot: dict[str, Any]) -> dict[str, Any]:
    """Power, on a RESERVED-seed pilot world (never adjudicated).

    Expected issuer effect is derived from the generator's own noise ratios
    (w_e) applied to the pilot's ORACLE-arm card geometry -- no est8 result
    enters the prediction. The pilot's observed contrast is reported for
    transparency and excluded from every adjudication.
    """
    started = time.time()
    per_event_noise_energy = 2.0 * float(knobs["w_e"])      # v8/f1 generator algebra
    half = N_OCC // 2
    eps = 2.0 * per_event_noise_energy / (half * EST_SIZES[0])
    seed = world_seed_for("pilot", PILOT_WORLD, knob_tag)
    panel, norm_events, labels = build_abs_world("free", n_panel, knobs, seed)
    mu_or = norm_events.mean(axis=0)
    cards = cards_for_arm(panel, labels, mu_or)
    rng = np.random.default_rng(20260809)
    rows = np.arange(len(panel))
    dim = panel.shape[2]
    sigma_card = math.sqrt((eps / 2.0) / dim)   # each card carries half the energy
    acc_pred = []
    for _ in range(16):
        g = cards["B1"] + rng.normal(scale=sigma_card, size=cards["B1"].shape)
        p = cards["B2"] + rng.normal(scale=sigma_card, size=cards["B2"].shape)
        acc_pred.append(float((cdist(p, g).argmin(axis=1) == rows).mean()))
    predicted_est8 = float(np.mean(acc_pred))
    oracle_rank1 = pilot["arms"]["oracle"]["B_rank1"]
    expected_effect = float(oracle_rank1 - predicted_est8)

    diff = (
        pilot["arms"]["oracle"]["B_correct"] - pilot["arms"]["est8"]["B_correct"]
    )
    boot = np.array(
        [
            float(diff[rng.integers(0, len(diff), size=len(diff))].mean())
            for _ in range(500)
        ]
    )
    se_world = float(boot.std(ddof=1))
    se_pooled = se_world / math.sqrt(WORLDS)
    t_mult = float(stats.t.ppf(0.975, df=WORLDS - 1) + stats.t.ppf(0.80, df=WORLDS - 1))
    mde = float(t_mult * se_pooled)
    return {
        "gate": "G3",
        "description": "MDE for the L2 contrast (rank-1 oracle vs est8, free design)",
        "pilot_world": PILOT_WORLD,
        "pilot_note": "reserved seed; excluded from every adjudication",
        "per_event_noise_energy_from_knobs": per_event_noise_energy,
        "issuer_variance_added_per_distance_est8": eps,
        "pilot_oracle_rank1": oracle_rank1,
        "predicted_est8_rank1_from_generator_ratios": predicted_est8,
        "expected_issuer_effect": expected_effect,
        "author_bootstrap_se_within_world": se_world,
        "se_pooled_across_8_worlds": se_pooled,
        "t_multiplier_80pct_power": t_mult,
        "mde": mde,
        "requirement": "mde <= expected_issuer_effect",
        "pilot_observed_effect_disclosed": float(diff.mean()),
        "seconds": float(time.time() - started),
        "pass": bool(mde <= expected_effect),
    }


def gate_g4(knobs: dict[str, Any], knob_tag: str, n_panel: int,
            pilot_free: dict[str, Any]) -> dict[str, Any]:
    """Channel verification on the reserved pilot world + post-map displacement."""
    started = time.time()
    var_by_arm = {
        name: pilot_free["arms"][name]["mu_err_var"]
        for name in ("est8", "est32", "est128", f"biased{BIASED_SIZE}")
    }
    ordering = bool(
        var_by_arm["est8"] > var_by_arm["est32"] > var_by_arm["est128"] > 0.0
    )
    flips_est8_free = pilot_free["arms"]["est8"]["B_flips_vs_oracle"]
    bias_rms = pilot_free["arms"][f"biased{BIASED_SIZE}"]["mu_err_rms"]
    samp_rms = pilot_free["arms"]["est32"]["mu_err_rms"]

    module = f2()
    f1 = module.f1()
    spec = f1.load_spec()
    directions = f1._directions(spec)
    reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
    aid, ctx, _spl, common, _raw = module.build_layout_common(reference)
    seed = world_seed_for("g4disp", PILOT_WORLD, knob_tag)
    base = module.generate_world_composed(common, ctx, knobs, KAPPA, "shared", seed)
    labels = module.occasion_labels(common, "shared")
    rms = _author_deviation_rms(base, labels, ctx)
    m0, k0 = f1.featurize_panel(base, aid, corpus="m4k1-g4", spec=spec, directions=directions)
    disp = {}
    n_lab = int(max(int(lab.max()) for lab in labels)) + 1
    for scale in SHIFT_SCALES:
        rng = np.random.default_rng(
            v8.stable_bucket(f"{seed}-shared", salt="m4k1-shift", modulus=2**63 - 1)
        )
        delta = rng.normal(size=(n_lab, base[0].shape[1])) * (scale * rms)
        shifted = [vec + delta[labels[i]] for i, vec in enumerate(base)]
        m1, k1 = f1.featurize_panel(
            shifted, aid, corpus="m4k1-g4", spec=spec, directions=directions
        )
        disp[f"{scale:g}x"] = {
            "shift_sigma": float(scale * rms),
            "rel_frobenius_M": float(np.linalg.norm(m1 - m0) / np.linalg.norm(m0)),
            "rel_frobenius_K": float(np.linalg.norm(k1 - k0) / np.linalg.norm(k0)),
            "positive": bool(np.linalg.norm(m1 - m0) > 0.0),
        }
    return {
        "gate": "G4",
        "description": "channel verification (rule 3): norm arms live, shifts land post-map",
        "pilot_world": PILOT_WORLD,
        "mu_err_var_by_arm": var_by_arm,
        "expected_P_ordering_holds": ordering,
        "decision_flips_est8_free_pilot": int(flips_est8_free),
        "issuer_channel_live": bool(ordering and flips_est8_free > 0),
        "biased32_mu_err_rms": bias_rms,
        "est32_sampling_mu_err_rms": samp_rms,
        "bias_exceeds_sampling": bool(bias_rms > samp_rms),
        "author_deviation_rms_response_level": float(rms),
        "post_map_displacement": disp,
        "all_shifts_displace": bool(all(v["positive"] for v in disp.values())),
        "seconds": float(time.time() - started),
        "pass": bool(
            ordering
            and flips_est8_free > 0
            and bias_rms > samp_rms
            and all(v["positive"] for v in disp.values())
        ),
    }


def run_part0(n_panel: int) -> dict[str, Any]:
    started = time.time()
    knobs, knob_tag = knobs_and_tag()
    OUT.mkdir(parents=True, exist_ok=True)
    g0 = gate_g0(knobs, knob_tag)
    g1 = gate_g1()
    g2 = dict(G2_VERDICT)
    pilot = run_abs_world("free", PILOT_WORLD, n_panel, knobs, knob_tag, group="pilot")
    g3 = gate_g3(knobs, knob_tag, n_panel, pilot)
    g4 = gate_g4(knobs, knob_tag, n_panel, pilot)
    g5 = {
        "gate": "G5",
        "description": "hygiene: manifest, per-stage seeds, wall-times, foreground stages",
        "master_seed": MASTER_SEED,
        "stage_seed_recipe": "stable_bucket(f'{MASTER_SEED}-{group}-w{world}-{knob_tag}', salt='m4k1-world')",
        "groups": ["abs", "rel", "pilot", "g4disp"],
        "background_jobs": 0,
        "pass": True,
    }
    gates = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "leg": "M4-K1",
        "master_seed": MASTER_SEED,
        "knobs": knobs,
        "knob_tag": knob_tag,
        "G0": g0, "G1": g1, "G2": g2, "G3": g3, "G4": g4, "G5": g5,
        "all_pass": bool(g0["pass"] and g1["pass"] and g3["pass"] and g4["pass"]),
        "seconds": float(time.time() - started),
    }
    (OUT / "gates.json").write_text(json.dumps(gates, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v.get("pass") for k, v in gates.items() if isinstance(v, dict)}, indent=2))
    print(f"G3 mde={g3['mde']:.6g} expected={g3['expected_issuer_effect']:.6g} pass={g3['pass']}")
    print(f"G2 branch={g2['branch']}")
    return gates


# ===========================================================================
# Arm stages.
# ===========================================================================

def run_abs_stage(n_panel: int) -> None:
    knobs, knob_tag = knobs_and_tag()
    OUT.mkdir(parents=True, exist_ok=True)
    rows, probe_rows = [], []
    started = time.time()
    for design in ("shared", "free"):
        for world in range(WORLDS):
            res = run_abs_world(design, world, n_panel, knobs, knob_tag)
            for arm, entry in res["arms"].items():
                rows.append(
                    {
                        "design": design, "world": world, "arm": arm,
                        "n_panel": res["n_panel"],
                        "mean_occasion_overlap": res["mean_pairwise_occasion_overlap"],
                        "rank1_B": entry["B_rank1"], "rank1_A": entry["A_rank1"],
                        "readability_B": entry["B_readability"],
                        "readability_A": entry["A_readability"],
                        "flips_vs_oracle_B": entry["B_flips_vs_oracle"],
                        "flips_vs_oracle_A": entry["A_flips_vs_oracle"],
                        "ties_excluded_B": entry["B_ties_excluded"],
                        "ties_excluded_A": entry["A_ties_excluded"],
                        "carddiff_rel_max_B": entry["carddiff_rel_max_B"],
                        "carddiff_rel_max_A": entry["carddiff_rel_max_A"],
                        "carddiff_translation_max_B": entry["carddiff_translation_max_B"],
                        "carddiff_translation_max_A": entry["carddiff_translation_max_A"],
                        "mu_err_var": entry["mu_err_var"],
                        "mu_err_rms": entry["mu_err_rms"],
                        "mu_err_occ_const_rms": entry["mu_err_occasion_constant_rms"],
                        "world_seed": res["world_seed"],
                        "seconds": res["seconds"],
                    }
                )
                probe_rows.append(
                    {
                        "design": design, "world": world, "arm": arm,
                        "correct_B": entry["B_correct"].astype(np.int8),
                        "correct_A": entry["A_correct"].astype(np.int8),
                    }
                )
            print(
                f"[abs {design} w{world}] rank1_B "
                + " ".join(
                    f"{a}={res['arms'][a]['B_rank1']:.4f}"
                    for a in ("oracle", "est8", "est32", "est128", "biased32")
                )
                + f" flipsB(est8)={res['arms']['est8']['B_flips_vs_oracle']}"
                + f" {res['seconds']:.1f}s",
                flush=True,
            )
    pd.DataFrame(rows).to_csv(OUT / "abs_cells.csv", index=False)
    np.savez_compressed(
        OUT / "abs_probe_correct.npz",
        **{
            f"{r['design']}|{r['world']}|{r['arm']}|{reader}": r[f"correct_{reader}"]
            for r in probe_rows
            for reader in ("B", "A")
        },
    )
    print(f"[abs] done in {time.time() - started:.0f}s -> {OUT / 'abs_cells.csv'}")


def run_rel_stage(workers: int) -> None:
    knobs, knob_tag = knobs_and_tag()
    OUT.mkdir(parents=True, exist_ok=True)
    tasks = [
        rel_task(design, world, scale, knobs, knob_tag)
        for design in ("shared", "free")
        for scale in (0.0,) + SHIFT_SCALES
        for world in range(WORLDS)
    ]
    started = time.time()
    with ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(_rel_world, tasks))
    for row in rows:
        print(
            f"[{row['cell']} w{row['world']}] A {row['agreement_mean']:+.6f} "
            f"n_ret {row['n_retained']} sigma {row['shift_sigma']:.5f} "
            f"{row['seconds']:.0f}s",
            flush=True,
        )
    pd.DataFrame(rows).to_csv(OUT / "rel_cells.csv", index=False)
    print(f"[rel] done in {time.time() - started:.0f}s -> {OUT / 'rel_cells.csv'}")


# ===========================================================================
# Adjudication.
# ===========================================================================

def _load_probe(store: Any, design: str, world: int, arm: str, reader: str) -> np.ndarray:
    return store[f"{design}|{world}|{arm}|{reader}"].astype(float)


def _author_stratified_bootstrap(per_world: list[np.ndarray], seed: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    means = np.array([float(v.mean()) for v in per_world])
    draws = np.empty(BOOT_DRAWS)
    for b in range(BOOT_DRAWS):
        acc = 0.0
        for values in per_world:
            idx = rng.integers(0, len(values), size=len(values))
            acc += float(values[idx].mean())
        draws[b] = acc / len(per_world)
    return {
        "pooled_mean": float(means.mean()),
        "per_world_means": [float(x) for x in means],
        "per_world_positive": int(np.sum(means > 0)),
        "n_worlds": int(len(means)),
        "boot_draws": BOOT_DRAWS,
        "ci95_low": float(np.percentile(draws, 2.5)),
        "ci95_high": float(np.percentile(draws, 97.5)),
        "excludes_zero_positive": bool(np.percentile(draws, 2.5) > 0.0),
        "excludes_zero": bool(
            np.percentile(draws, 2.5) > 0.0 or np.percentile(draws, 97.5) < 0.0
        ),
    }


def adjudicate() -> dict[str, Any]:
    module = f2()
    cells = pd.read_csv(OUT / "abs_cells.csv")
    store = np.load(OUT / "abs_probe_correct.npz")
    rel = pd.read_csv(OUT / "rel_cells.csv")
    out: dict[str, Any] = {}

    # ---- L1 -------------------------------------------------------------
    shared = cells[cells["design"] == "shared"]
    non_oracle = shared[shared["arm"] != "oracle"]
    l1 = {
        "lean": "L1",
        "rule": (
            "shared design, norms actually subtracted: 0 rank-1 decision flips vs "
            "oracle across ALL norm arms (ties with top-2 margin < 1e-6 excluded and "
            "counted); card-difference matrices agree within 1e-9 relative; 8/8 worlds"
        ),
        "reader_A_is_T3c_hypothesis": (
            "T3(c) conditions on 'a common probe/gallery norm'; reader A satisfies it "
            "(one norm vector per author, shared by both halves), reader B does not "
            "(each half subtracts its own occasions' norms)"
        ),
        "flips_total_A": int(non_oracle["flips_vs_oracle_A"].sum()),
        "flips_total_B": int(non_oracle["flips_vs_oracle_B"].sum()),
        "ties_excluded_A": int(non_oracle["ties_excluded_A"].sum()),
        "ties_excluded_B": int(non_oracle["ties_excluded_B"].sum()),
        "carddiff_rel_max_A": float(non_oracle["carddiff_rel_max_A"].max()),
        "carddiff_rel_max_B": float(non_oracle["carddiff_rel_max_B"].max()),
        "carddiff_translation_max_A": float(non_oracle["carddiff_translation_max_A"].max()),
        "carddiff_translation_max_B": float(non_oracle["carddiff_translation_max_B"].max()),
        "worlds_clean_A": int(
            non_oracle.groupby("world")["flips_vs_oracle_A"].sum().eq(0).sum()
        ),
        "worlds_clean_B": int(
            non_oracle.groupby("world")["flips_vs_oracle_B"].sum().eq(0).sum()
        ),
        "tolerance": CARD_DIFF_TOL,
    }
    l1["verdict"] = (
        "HOLD"
        if (
            l1["flips_total_A"] == 0
            and l1["worlds_clean_A"] == WORLDS
            and l1["carddiff_rel_max_A"] < CARD_DIFF_TOL
            and l1["carddiff_rel_max_B"] < CARD_DIFF_TOL
        )
        else "MISS"
    )
    out["L1"] = l1

    # ---- L2 -------------------------------------------------------------
    l2: dict[str, Any] = {
        "lean": "L2",
        "rule": (
            "free design: rank-1(oracle) > rank-1(est8); per-world sign 8/8 clean "
            "(7/8 qualified, <=6/8 fail); pooled author-stratified bootstrap "
            "(2000 draws) 95% CI excludes 0; Spearman monotone in |P| over "
            "{est8,est32,est128,oracle} == 1.0 in >=6/8 worlds"
        ),
    }
    for reader in ("B", "A"):
        per_world = [
            _load_probe(store, "free", w, "oracle", reader)
            - _load_probe(store, "free", w, "est8", reader)
            for w in range(WORLDS)
        ]
        boot = _author_stratified_bootstrap(per_world, seed=20260809 + 1)
        spear = []
        free = cells[cells["design"] == "free"]
        for w in range(WORLDS):
            sub = free[free["world"] == w].set_index("arm")
            sizes = [8, 32, 128, N_ORACLE]
            accs = [sub.loc[a, f"rank1_{reader}"] for a in ("est8", "est32", "est128", "oracle")]
            spear.append(float(stats.spearmanr(sizes, accs).statistic))
        l2[reader] = {
            **boot,
            "sign_count": boot["per_world_positive"],
            "spearman_by_world": spear,
            "n_worlds_spearman_1": int(sum(1 for s in spear if s == 1.0)),
            "monotone_hold": bool(sum(1 for s in spear if s == 1.0) >= 6),
        }
        sign = boot["per_world_positive"]
        band = "clean" if sign == 8 else ("qualified" if sign == 7 else "fail")
        l2[reader]["sign_band"] = band
        l2[reader]["verdict"] = (
            "HOLD" if (band == "clean" and boot["excludes_zero_positive"]
                       and l2[reader]["monotone_hold"])
            else ("QUALIFIED_HOLD" if (band == "qualified" and boot["excludes_zero_positive"])
                  else "MISS")
        )
    l2["verdict"] = l2["B"]["verdict"]
    out["L2"] = l2

    # ---- L3 -------------------------------------------------------------
    pts = cells[(cells["design"] == "free") & cells["arm"].isin(["est8", "est32", "est128"])]
    x = np.log10(pts["arm"].str.replace("est", "").astype(float).to_numpy())
    y = np.log10(pts["mu_err_var"].to_numpy())
    slope = float(np.polyfit(x, y, 1)[0])
    rng = np.random.default_rng(20260809 + 3)
    slopes = []
    worlds = pts["world"].unique()
    for _ in range(BOOT_DRAWS):
        pick = rng.integers(0, len(worlds), size=len(worlds))
        sub = pd.concat([pts[pts["world"] == worlds[i]] for i in pick])
        xs = np.log10(sub["arm"].str.replace("est", "").astype(float).to_numpy())
        ys = np.log10(sub["mu_err_var"].to_numpy())
        slopes.append(float(np.polyfit(xs, ys, 1)[0]))
    lo, hi = float(np.percentile(slopes, 2.5)), float(np.percentile(slopes, 97.5))
    l3 = {
        "lean": "L3",
        "rule": "pooled log Var(mu_hat - mu_oracle) vs log |P| slope CI within [-1.35,-0.65]",
        "note": "manipulation check, not a discovery (near-by-construction for iid sampling)",
        "slope": slope, "ci95_low": lo, "ci95_high": hi,
        "band": list(L3_SLOPE_BAND),
        "verdict": "HOLD" if (lo >= L3_SLOPE_BAND[0] and hi <= L3_SLOPE_BAND[1]) else "MISS",
    }
    out["L3"] = l3

    # ---- L4 -------------------------------------------------------------
    l4: dict[str, Any] = {
        "lean": "L4",
        "rule": (
            "(oracle - est8 deficit in FREE) - (same in SHARED) > 0; per-world sign "
            ">=7/8; pooled CI excludes 0"
        ),
    }
    for reader in ("B", "A"):
        per_world = [
            (
                _load_probe(store, "free", w, "oracle", reader)
                - _load_probe(store, "free", w, "est8", reader)
            )
            - (
                _load_probe(store, "shared", w, "oracle", reader)
                - _load_probe(store, "shared", w, "est8", reader)
            )
            for w in range(WORLDS)
        ]
        boot = _author_stratified_bootstrap(per_world, seed=20260809 + 4)
        l4[reader] = {
            **boot,
            "verdict": "HOLD"
            if (boot["per_world_positive"] >= 7 and boot["excludes_zero_positive"])
            else "MISS",
        }
    l4["verdict"] = l4["B"]["verdict"]
    out["L4"] = l4

    # ---- L5 -------------------------------------------------------------
    l5: dict[str, Any] = {
        "lean": "L5",
        "rule": (
            "equivalence: pooled 95% CI for Delta agreement (shifted - unshifted), "
            f"shared design, inside +/- {EQUIV_MARGIN!r} at shifts 0.5x and 1x; "
            "additionally per-world |Delta| < 2m in 8/8"
        ),
        "margin_m": EQUIV_MARGIN,
    }
    for design in ("shared", "free"):
        base = rel[(rel["occasion_mode"] == design) & (rel["shift_scale"] == 0.0)]
        base = base.sort_values("world")
        for scale in SHIFT_SCALES:
            arm = rel[
                (rel["occasion_mode"] == design) & (rel["shift_scale"] == scale)
            ].sort_values("world")
            deltas = (
                arm["agreement_mean"].to_numpy() - base["agreement_mean"].to_numpy()
            )
            ci = module._paired_ci(deltas)
            key = f"{design}_{scale:g}x"
            l5[key] = {
                **ci,
                "per_world_delta": [float(d) for d in deltas],
                "per_world_abs_lt_2m": int(np.sum(np.abs(deltas) < 2 * EQUIV_MARGIN)),
                "ci_inside_margin": bool(
                    ci["ci95_low"] > -EQUIV_MARGIN and ci["ci95_high"] < EQUIV_MARGIN
                ),
                "unshifted_mean": float(base["agreement_mean"].mean()),
                "shifted_mean": float(arm["agreement_mean"].mean()),
                "gated": bool(design == "shared" and scale in L5_GATED_SCALES),
            }
    gated = [l5[f"shared_{s:g}x"] for s in L5_GATED_SCALES]
    l5["verdict"] = (
        "HOLD"
        if all(g["ci_inside_margin"] and g["per_world_abs_lt_2m"] == WORLDS for g in gated)
        else "MISS"
    )
    out["L5"] = l5

    # ---- pivots ---------------------------------------------------------
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    out["pivots"] = {
        "P1": {
            "rule": "L1 fails after the bug-hunt gate -> leg VOID",
            "fires": bool(l1["verdict"] == "MISS"),
        },
        "P2": {
            "rule": "L2 fails WITH a G4-verified live channel -> T5's absolute-reader "
                    "price demoted to 'sub-MDE at this scale'; line proceeds to K2",
            "channel_live": bool(gates["G4"]["issuer_channel_live"]),
            "fires": bool(l2["verdict"] == "MISS" and gates["G4"]["issuer_channel_live"]),
        },
        "P3": {
            "rule": "L5 fails -> T3(f) DEAD for the deployed gauge; K1b replaces K2",
            "fires": bool(l5["verdict"] == "MISS"),
        },
        "P4": {
            "rule": "L4 fails while L1/L2 hold -> re-run the structural audit; if clean, "
                    "record a theory hit on T3(e)",
            "fires": bool(
                l4["verdict"] == "MISS"
                and l1["verdict"] == "HOLD"
                and l2["verdict"] in ("HOLD", "QUALIFIED_HOLD")
            ),
        },
    }

    # ---- descriptive cross-reader magnitudes (no gate) -------------------
    out["descriptive"] = {
        "note": "cross-reader magnitude comparisons are DESCRIPTIVE this leg",
        "rank1_by_design_arm_readerB": {
            f"{d}|{a}": float(
                cells[(cells["design"] == d) & (cells["arm"] == a)]["rank1_B"].mean()
            )
            for d in ("shared", "free")
            for a in ("oracle", "est8", "est32", "est128", f"biased{BIASED_SIZE}")
        },
        "rank1_by_design_arm_readerA": {
            f"{d}|{a}": float(
                cells[(cells["design"] == d) & (cells["arm"] == a)]["rank1_A"].mean()
            )
            for d in ("shared", "free")
            for a in ("oracle", "est8", "est32", "est128", f"biased{BIASED_SIZE}")
        },
        "readability_by_design_arm_readerB": {
            f"{d}|{a}": float(
                cells[(cells["design"] == d) & (cells["arm"] == a)]["readability_B"].mean()
            )
            for d in ("shared", "free")
            for a in ("oracle", "est8", "est32", "est128", f"biased{BIASED_SIZE}")
        },
        "biased32_vs_est32_mu_err_rms": {
            "biased32": float(cells[cells["arm"] == "biased32"]["mu_err_rms"].mean()),
            "est32": float(cells[cells["arm"] == "est32"]["mu_err_rms"].mean()),
            "biased32_occ_const_component": float(
                cells[cells["arm"] == "biased32"]["mu_err_occ_const_rms"].mean()
            ),
            "est32_occ_const_component": float(
                cells[cells["arm"] == "est32"]["mu_err_occ_const_rms"].mean()
            ),
        },
        "rel_agreement_means": {
            f"{d}_{s:g}x": float(
                rel[(rel["occasion_mode"] == d) & (rel["shift_scale"] == s)][
                    "agreement_mean"
                ].mean()
            )
            for d in ("shared", "free")
            for s in (0.0,) + SHIFT_SCALES
        },
    }
    return out


VERDICT_SLUGS = {
    ("HOLD", "HOLD"): "ISSUER_THEOREMS_CONFIRMED_ON_THE_DEPLOYED_MACHINERY",
    ("HOLD", "MISS"): (
        "CARD_SPACE_CANCELLATION_EXACT__DEPLOYED_GAUGE_AMPLIFIES_THE_COMMON_SHIFT"
        "__T3f_DEAD__K1b_REPLACES_K2"
    ),
    ("MISS", "HOLD"): "L1_IRREDUCIBLE__LEG_VOID_PENDING_FIX",
    ("MISS", "MISS"): "L1_IRREDUCIBLE__LEG_VOID_PENDING_FIX",
}


def run_finalize() -> None:
    gates = json.loads((OUT / "gates.json").read_text(encoding="utf-8"))
    adj = adjudicate()
    slug = VERDICT_SLUGS[(adj["L1"]["verdict"], adj["L5"]["verdict"])]
    if adj["L1"]["verdict"] == "HOLD" and adj["L5"]["verdict"] == "HOLD":
        if adj["L2"]["verdict"] == "MISS":
            slug = "DESIGNED_CANCELLATION_EXACT_AND_GAUGE_ROBUST__ISSUER_PRICE_NOT_PAID_AT_THIS_SCALE"
    decision = {
        "experiment": "M4-K1_issuer_theorems",
        "banner": BANNER,
        "tier": "EXPLORATORY",
        "registered_spec": "docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md#M4-K1",
        "part0_registered_in": "reports/SUICA_M4_K1_ISSUER_THEOREMS_REPORT.md Part 0 (before arms)",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED,
        "worlds": WORLDS,
        "knobs": gates["knobs"],
        "knob_tag": gates["knob_tag"],
        "gates": {k: gates[k].get("pass") for k in ("G0", "G1", "G2", "G3", "G4", "G5")},
        "gates_all_pass": gates["all_pass"],
        "g2_branch": gates["G2"]["branch"],
        "adjudication": adj,
        "verdict": slug,
        "label_free": True,
        "claim_boundary": (
            "Synthetic issuer-theorem measurement in a world calibrated to the opened "
            "PANDORA D-panel regime, through the deployed frozen machinery; licenses "
            "IDT grammar (typing rules and design priors) only. No claim about any "
            "corpus, construct, person, or diagnosis."
        ),
    }
    (OUT / "decision.json").write_text(json.dumps(decision, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v.get("verdict") for k, v in adj.items() if isinstance(v, dict) and "verdict" in v}, indent=2))
    print(json.dumps(adj["pivots"], indent=2))
    print("VERDICT:", slug)


def write_manifest(stage: str, seconds: float, extra: dict[str, Any] | None = None) -> None:
    path = OUT / "manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
        "leg": "M4-K1",
        "banner": BANNER,
        "master_seed": MASTER_SEED,
        "worlds": WORLDS,
        "seed_recipe": "v8.stable_bucket(f'{MASTER_SEED}-{group}-w{world}-{knob_tag}', salt='m4k1-world', modulus=2**63-1)",
        "per_stage_seeds": {
            "abs": "group='abs', worlds 0..7",
            "rel": "group='rel', worlds 0..7 (F2 MASTER_SEED overridden to 20260809)",
            "pilot": f"group='pilot', world {PILOT_WORLD} (reserved, never adjudicated)",
            "g4disp": f"group='g4disp', world {PILOT_WORLD}",
            "shift": "v8.stable_bucket(f'{world_seed}-{occasion_mode}', salt='m4k1-shift')",
            "biased32": "v8.stable_bucket(f'{world_seed}', salt='m4k1-biased')",
            "bootstrap": {"L2": 20260810, "L3": 20260812, "L4": 20260813},
        },
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "stages": {},
    }
    manifest["stages"][stage] = {
        "wall_seconds": round(float(seconds), 3),
        "finished_utc": datetime.now(UTC).isoformat(),
        **(extra or {}),
    }
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["part0", "abs", "rel", "finalize"], required=True)
    parser.add_argument("--workers", type=int, default=max(2, min(6, (os.cpu_count() or 4) - 2)))
    parser.add_argument("--authors", type=int, default=0, help="0 = F2's pinned authors/world")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    for path in (REF_PATH, F1_CALIBRATION, F2_OUT / "decision.json"):
        if not path.exists():
            raise AssertionError(f"{path} missing (read-only predecessor artifact).")

    n_panel = args.authors
    if n_panel == 0:
        reference = json.loads(REF_PATH.read_text(encoding="utf-8"))
        n_panel = len(f2().build_layout_common(reference)[0])

    started = time.time()
    if args.stage == "part0":
        run_part0(n_panel)
    elif args.stage == "abs":
        if not (OUT / "gates.json").exists():
            raise AssertionError("Part 0 gates must run (and be reported) before arms.")
        run_abs_stage(n_panel)
    elif args.stage == "rel":
        if not (OUT / "gates.json").exists():
            raise AssertionError("Part 0 gates must run (and be reported) before arms.")
        run_rel_stage(args.workers)
    elif args.stage == "finalize":
        run_finalize()
    write_manifest(args.stage, time.time() - started, {"authors_per_world": int(n_panel)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
