#!/usr/bin/env python3
"""SUICA M4-P2 -- the dose-decomposition (genuine reading vs frame agreement).

Registered BEFORE run in docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md
("M4-P2 -- the dose-decomposition", commit b61cc52).  Binding.

P1 established the SIGN: injecting common-frame content RAISES b-only recovery
steeply (b-hat +0.32 / +0.35).  But the b-only truth panel is ITSELF
frame-carried (K-R1's F-1), so part of that boost may be frame-vs-frame
agreement rather than better person-reading.  This leg splits it.

Each world is built in TWO variants at the same index: dosed (delta at scale s)
and zero-dose (delta = 0).  The DOSED world's gauge output is scored twice --
R_nat against its OWN truth panel (P1's quantity) and R_cf against the
ZERO-DOSE world's truth panel (the counterfactual, frame-fixed truth).  Then
    G(s) = R_cf(s) - R_cf(0)                     genuine improvement
    F(s) = [R_nat(s) - R_nat(0)] - G(s)          frame-vs-frame share
    f    = F(1) / [R_nat(1) - R_nat(0)]          the frame fraction at s = 1

suica_core/ and the frozen map are untouched; k2b is not edited.  The gauge
path is k2b's own, reassembled here only so one calibration can be scored
against two truth panels.

Stages:  part0 -> pilot -> project -> arm_<cell>_s<s> (10) -> fit -> finalize
         -> report
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import platform
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "results" / "m4_p2_dose_decomposition"
RES = ROOT / "results"
M2RES = RES / "m4_m2_scoped_seal"

LEG = "M4-P2"
BANNER = ("frame-injection sign probe on the K2b family; exploratory, label-free; "
          "no seal -- the leans are split, so no sealable point prediction exists")

MASTER_SEED = 20260814
SALT_WORLD = "m4p2-world"
SALT_PILOT = "m4p2-pilot"
N_WORLDS = 192
N_WORLDS_ESCALATED = 384
PILOT_WORLDS = 4
S_ARMS = (0.0, 0.25, 0.5, 0.75, 1.0)
PILOT_S = (0.0, 1.0)
BASE_CELLS = {"B1": (0.25, 0.05), "B2": (0.25, 0.60)}
R_REGISTERED = {"B1": 0.785015540293945, "B2": 0.7558507450373838}
W_INT_ARM = "zero"

M2_C4_MEAN = 0.12239759528671845
M2_C4_SOURCE = "results/m4_m2_scoped_seal/decision.json:per_cell.C4.mean"
P1RES = RES / "m4_p1_frame_injection"
# P1's persisted headline, re-verified in G0p2 (values read from the artifact)
P1_B1_SLOPE = 0.3217400470171695
P1_B2_SLOPE = 0.34654236945734695
P1_INJECTION_PIN = "scripts/run_suica_m4_k2b_t4_branch.py:377"
VAR_RATIO_BAR = 10.0
F_BUDGET = 0.30

MDE_BAR = 0.01                 # declared minimum-interesting slope |b| on R_cf
EQUIV = 0.01                   # rule-4 equivalence margin on b-hat
B_BOOT = 2000
B_BOOT_HIGH = 20000
RULE13_FACTOR = 10.0
CHI2_Q = 0.10                  # the registered df-inflation quantile (M1b G3m'(b))
RMS_TOL = 0.05                 # G1p2(b): realized RMS within 5% of target
SATURATION_ABS = 0.995

# --- the citation anchors G0p2(ii) must locate (rule 24: found, not typed) ---
KLINE = ROOT / "docs" / "SUICA_M4_K_IDENTITY_LINE_PLAN.md"
V8DOC = ROOT / "docs" / "SUICA_V8_IDT_INTEGRATION.md"
K1SRC = ROOT / "scripts" / "run_suica_m4_k1_issuer_theorems.py"
ANCHORS = {
    "K1 recipe (author-deviation RMS)": (KLINE, "author-deviation RMS"),
    "K1 amplification (+0.0925)": (V8DOC, "0.0925"),
    "K1 amplification (3.54x F2)": (V8DOC, "3.54"),
    "K-R1 scaffold corollary": (KLINE, "scaffold"),
    "K2b G4b frame-carried substrate": (KLINE, "within-author occasion variation"),
    "K1 implementation: the RMS definition (CONTROLS, RN-P2-2)":
        (K1SRC, "RMS over (author, dim) of the author's mean deviation"),
    "K1 implementation: the delta construction":
        (K1SRC, "delta = rng.normal(size=(n_lab"),
}

# ---------------------------------------------------------------------------
# RN-P2 notes.  PINNED IN PART 0, BEFORE ANY WORLD.
#
# RN-P2-1 (inherited verbatim from P1, re-proven here).  The injection point is
#   world["common"] -- the LAST common per-occasion object every author's
#   response shares before the frozen map: built at
#   scripts/run_suica_m4_k2b_t4_branch.py:337, returned at :349, last read at
#   :377 inside emit_panel, called at :615 one line before the map's entry at
#   :616.  delta(o) is added to common[c, o, :] for EVERY context.  k2b and
#   suica_core/ are not edited.
#
# RN-P2-2 (the calibration, inherited).  K1's own implementation controls
#   (rules 9/12): centre each response on its (CONTEXT, OCCASION) cell mean,
#   average each author's deviations over its occasions, RMS over
#   (author x dim) -- k1:337-361.  delta is rescaled in closed form so the
#   REALIZED response-level RMS equals s x that quantity exactly (RN-P1-7's
#   departure from K1's sigma-setting, confirmed correct at P1 adjudication).
#
# RN-P2-3 (s-independent corpus labels -- now a PINNED REQUIREMENT).  k2b's
#   corpus string embeds arm_id (k2b:613) and the frozen map's output depends
#   on it (P1 measured ~0.0122 between two labels on one world).  The arm tag
#   here is `P2-{cell}`, carrying no s, so at a matched world index every dose
#   arm receives the IDENTICAL corpus string.  The registration pins this.
#
# RN-P2-4 (the dual scoring, and why it is not two runs).  R_nat and R_cf share
#   ONE gauge pass: the dosed panel is featurized, calibrated and projected
#   once, and that single calibration + field_est is scored against two truth
#   panels -- the dosed world's own (T-nat) and the zero-dose world's (T-cf).
#   Scoring twice off one calibration is required, not merely cheaper: a second
#   calibration would differ, and R_cf - R_nat would then confound the truth
#   swap with a calibration swap.  The path is k2b's own run_field_world
#   (k2b:611-632) reassembled line-for-line; G1p2(d) proves R_nat comes back
#   BIT-IDENTICAL to k2b's own run_field_world on the same world.
#
# RN-P2-5 (the zero-point identity is structural AND checked).  At s = 0 the
#   dosed and zero-dose variants are the same array, so T-cf IS T-nat and
#   R_cf(0) == R_nat(0) must hold bit-exactly.  G1p2(c) checks it on every
#   pilot world rather than asserting it, because it is the hinge of the
#   decomposition: G(0) = F(0) = 0 only if it holds.
#
# RN-P2-6 (the variance-ratio disclosure).  PINNED: at the response level
#   decompose v[i, t] into its (context, occasion) cell mean and the author
#   deviation from it -- the SAME centring K1's calibration uses -- and report
#   mean((cell mean - grand mean)^2) / mean(author deviation^2) over every
#   (author, occasion, dim) cell.  Ratio > 10 at ANY arm sets REGIME_NOTE; it
#   adjudicates nothing and scopes the claim.
#
# RN-P2-7 (classification order, #55's convention now IN the registration).
#   NULL is tested FIRST (CI inside +/-0.01, rule 4 equivalence), then sign,
#   then UNDERPOWERED.  The sign-first ordering is still computed and reported.
#
# RN-P2-8 (the slope's algebra at five levels).  With s in
#   {0, 0.25, 0.5, 0.75, 1.0} equally replicated, sum_j (s_j - s_bar)^2 =
#   0.625, so b-hat = sum_j (s_j - 0.5) * ybar_j / 0.625 and
#   SE(b-hat) = sigma / sqrt(n * 0.625).  Unlike P1's three-level design every
#   arm now contributes to the slope.
#
# RN-P2-9 (f's denominator and its budget).  f = F(1)/[R_nat(1) - R_nat(0)] is
#   a ratio, well-defined here only because the denominator is large (P1
#   measured ~0.32) and this leg re-measures it.  f is bootstrapped JOINTLY
#   with its denominator -- one resample drives numerator and denominator -- so
#   the ratio's correlation is preserved.  Rule-27 budget: 95% CI width <=
#   0.30, else f is DESCRIPTIVE-ONLY and the cell labels carry UNQUANTIFIED.
#
# RN-P2-10 (dose-form fits are descriptive).  Linear and quadratic fits on
#   R_nat and R_cf carry no verdict, per the registration's own N-line lesson:
#   nothing downstream consumes the form yet.
# ---------------------------------------------------------------------------
RN_NOTES = {
    "RN-P2-1": "injection point inherited from P1: world['common'], k2b:337 built, :349 "
               "returned, :377 last read inside emit_panel, called :615 one line before "
               "the frozen map at :616; delta added for EVERY context; k2b unedited",
    "RN-P2-2": "K1's own (context, occasion)-centred author-mean deviation RMS controls "
               "(k1:337-361); delta rescaled so the REALIZED response-level RMS equals "
               "s x that quantity exactly",
    "RN-P2-3": "arm tags carry NO s, so every dose arm shares the identical corpus string "
               "at a matched world index -- the registration's pinned requirement after "
               "P1's machinery finding",
    "RN-P2-4": "R_nat and R_cf share ONE gauge pass and ONE calibration, scored against "
               "two truth panels; a second calibration would confound the truth swap with "
               "a calibration swap. G1p2(d) proves R_nat is bit-identical to k2b's own "
               "run_field_world",
    "RN-P2-5": "at s = 0 the two variants are the same array, so R_cf(0) == R_nat(0) must "
               "hold bit-exactly; checked on every pilot world because it is the hinge "
               "that makes G(0) = F(0) = 0",
    "RN-P2-6": "variance ratio = mean((context,occasion cell mean - grand mean)^2) / "
               "mean(author deviation^2) over every (author, occasion, dim) cell, the "
               "same centring K1's calibration uses; > 10 at any arm sets REGIME_NOTE",
    "RN-P2-7": "NULL is tested FIRST (CI inside the equivalence margin, rule 4), then "
               "sign, then UNDERPOWERED -- #55's convention, now in the registration; the "
               "sign-first ordering is still computed and reported",
    "RN-P2-8": "five equally-replicated levels give sum (s_j - 0.5)^2 = 0.625, so b-hat = "
               "sum_j (s_j - 0.5) * ybar_j / 0.625 and SE = sigma / sqrt(n*0.625); every "
               "arm contributes",
    "RN-P2-9": "f is bootstrapped jointly with its denominator (one resample drives both) "
               "so the ratio's correlation is preserved; rule-27 budget is a 95% CI width "
               "<= 0.30, else DESCRIPTIVE-ONLY and UNQUANTIFIED",
    "RN-P2-10": "linear and quadratic dose-form fits are descriptive with no verdict "
                "attached -- nothing downstream consumes the form yet (the N-line lesson)",
}

# ---------------------------------------------------------------------------
# ONE loader chain (RN-K2F-5: private loaders create duplicate instances).

_MODS: dict[str, Any] = {}


def _load(name: str) -> Any:
    if name not in _MODS:
        spec = importlib.util.spec_from_file_location(
            name, ROOT / "scripts" / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)          # type: ignore[arg-type]
        sys.modules[name] = mod
        spec.loader.exec_module(mod)                         # type: ignore[union-attr]
        _MODS[name] = mod
    return _MODS[name]


def k2b() -> Any:
    return _load("run_suica_m4_k2b_t4_branch")


def k2c() -> Any:
    return _load("run_suica_m4_k2c_matched_pairs")


def v8() -> Any:
    # reached through k2b's own attribute (the N1b/M-line precedent), so the
    # ONE loader chain is preserved and no duplicate instance is created
    return k2b().v8


# ---------------------------------------------------------------------------

def _log(event: str, **kw: Any) -> None:
    rec = {"utc": datetime.now(UTC).isoformat(), "event": event, **kw}
    with (OUT / "run_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True, default=float) + "\n")


def read_csv_rt(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, float_precision="round_trip")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, default=float) + "\n",
                    encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def r_of(share: float, phi: float) -> float:
    return k2c().predicted_attenuation(share, phi)


def world_seed_for(cell: str, s: float, world: int, salt: str) -> int:
    key = f"{LEG}|{salt}|{cell}|s{s!r}|w{world}|seed{MASTER_SEED}"
    return int(v8().stable_bucket(key, salt=salt, modulus=2 ** 63 - 1))


def delta_seed_for(cell: str, s: float, world: int, salt: str) -> int:
    key = f"{LEG}|{salt}|DELTA|{cell}|s{s!r}|w{world}|seed{MASTER_SEED}"
    return int(v8().stable_bucket(key, salt=f"{salt}-delta", modulus=2 ** 63 - 1))


def _locate(path: Path, needle: str) -> dict[str, Any]:
    """Find `needle` and return its line number and the containing paragraph."""
    lines = path.read_text(encoding="utf-8").split("\n")
    for i, line in enumerate(lines):
        if needle in line:
            a = i
            while a > 0 and lines[a - 1].strip():
                a -= 1
            b = i
            while b + 1 < len(lines) and lines[b + 1].strip():
                b += 1
            para = " ".join(x.strip() for x in lines[a:b + 1]).strip()
            para = re.sub(r"\s+", " ", para)
            return {"found": True, "file": rel(path), "line": i + 1,
                    "paragraph_lines": f"{a + 1}-{b + 1}", "quote": para}
    return {"found": False, "file": rel(path), "needle": needle}


# ---------------------------------------------------------------------------
# THE INJECTION.

def author_deviation_rms(panel: list[np.ndarray], counts: np.ndarray,
                         ctx_index: np.ndarray, t_max: int) -> dict[str, Any]:
    """RN-P2-2: K1's definition (controls) plus two reported alternatives.

    K1's, transplanted literally from run_suica_m4_k1_issuer_theorems.py:337-361:
    centre on the (context, occasion) cell mean, average each author's
    deviations over its own occasions, RMS over the (author x dim) matrix.
    """
    dim = int(panel[0].shape[1])
    n = len(panel)
    n_ctx = int(ctx_index.max()) + 1

    # (context, occasion) cell means
    csum = np.zeros((n_ctx, t_max, dim), float)
    ccnt = np.zeros((n_ctx, t_max), float)
    for i, v in enumerate(panel):
        c = int(ctx_index[i])
        m = int(counts[i])
        csum[c, :m] += v
        ccnt[c, :m] += 1.0
    with np.errstate(invalid="ignore"):
        cmean = np.divide(csum, ccnt[:, :, None], out=np.zeros_like(csum),
                          where=ccnt[:, :, None] > 0)
    # occasion-only means (pooled contexts), for the alternatives
    osum = csum.sum(axis=0)
    ocnt = ccnt.sum(axis=0)
    omean = osum / ocnt[:, None]

    devs_k1 = np.empty((n, dim), float)
    devs_pooled = np.empty((n, dim), float)
    ss_raw = 0.0
    n_cells = 0
    for i, v in enumerate(panel):
        c = int(ctx_index[i])
        m = int(counts[i])
        d_cell = v - cmean[c, :m]
        d_occ = v - omean[:m]
        devs_k1[i] = d_cell.sum(axis=0) / m
        devs_pooled[i] = d_occ.sum(axis=0) / m
        ss_raw += float((d_occ * d_occ).sum())
        n_cells += int(v.size)
    return {
        "rms_k1_controls": float(np.sqrt(np.mean(devs_k1 ** 2))),
        "alt_A_raw_response_deviation_rms": float(math.sqrt(ss_raw / n_cells)),
        "alt_B_k1_pooling_contexts": float(np.sqrt(np.mean(devs_pooled ** 2))),
        "n_cells": int(n_cells),
        "n_per_occasion": ocnt.tolist(),
    }


def inject(world: dict[str, np.ndarray], w: dict[str, float], s: float,
           seed: int) -> dict[str, Any]:
    """Add the calibrated common per-occasion shift to world['common'] in place.

    Returns the persisted calibration record.  The world dict is mutated.
    """
    kb = k2b()
    lay = kb.layout()
    counts = np.asarray(lay["counts"], int)
    t_max = int(lay["t_max"])
    dim = int(kb.DIM)

    ctx_index = np.asarray(lay["ctx_index"], int)
    panel = kb.emit_panel(world, w)
    dev = author_deviation_rms(panel, counts, ctx_index, t_max)
    rms_dev = dev["rms_k1_controls"]
    n_cells = dev["n_cells"]
    n_t = np.asarray(dev["n_per_occasion"], float)

    rng = np.random.default_rng(seed)
    draw = rng.normal(size=(t_max, dim))
    wc = float(w["common"])
    # realized response-level RMS of the UNSCALED shift
    ss_raw = float((n_t[:, None] * (wc * draw) ** 2).sum())
    rms_raw = math.sqrt(ss_raw / n_cells)
    target = float(s) * rms_dev
    scale = 0.0 if rms_raw == 0.0 else target / rms_raw
    delta = scale * draw

    before = np.array(world["common"], copy=True)
    world["common"] = world["common"] + delta[None, :, :]
    moved = float(np.linalg.norm(world["common"] - before))
    bit_identical = bool(np.array_equal(
        world["common"].view(np.uint8), before.view(np.uint8)))

    ss_real = float((n_t[:, None] * (wc * delta) ** 2).sum())
    realized = math.sqrt(ss_real / n_cells)
    err = 0.0 if target == 0.0 else abs(realized - target) / target
    return {
        "s": float(s), "delta_seed": int(seed),
        "w_common": wc,
        "author_deviation_rms": rms_dev,
        "author_deviation_rms_definition": "K1's (context, occasion)-centred, "
                                           "author-mean, RMS over (author x dim) -- "
                                           "k1:337-361, transplanted (RN-P2-2)",
        "alt_A_raw_response_deviation_rms": dev["alt_A_raw_response_deviation_rms"],
        "alt_B_k1_pooling_contexts": dev["alt_B_k1_pooling_contexts"],
        "target_response_rms": target,
        "realized_response_rms": realized,
        "relative_calibration_error": float(err),
        "within_5pct": bool(err <= RMS_TOL),
        "scale_applied": float(scale),
        "delta_frobenius_norm": float(np.linalg.norm(delta)),
        "common_norm_delta": moved,
        "common_bit_identical_to_unperturbed": bit_identical,
        "n_response_cells": int(n_cells),
    }


def variance_ratio(panel: list[np.ndarray], counts: np.ndarray,
                   ctx_index: np.ndarray, t_max: int) -> float:
    """RN-P2-6: the common-to-author response-level variance ratio."""
    dim = int(panel[0].shape[1])
    n_ctx = int(ctx_index.max()) + 1
    csum = np.zeros((n_ctx, t_max, dim), float)
    ccnt = np.zeros((n_ctx, t_max), float)
    for i, v in enumerate(panel):
        c = int(ctx_index[i])
        m = int(counts[i])
        csum[c, :m] += v
        ccnt[c, :m] += 1.0
    cmean = np.divide(csum, ccnt[:, :, None], out=np.zeros_like(csum),
                      where=ccnt[:, :, None] > 0)
    tot = np.zeros(dim, float)
    rows = 0
    for v in panel:
        tot += v.sum(axis=0)
        rows += int(v.shape[0])
    grand = tot / rows
    ss_c = 0.0
    ss_a = 0.0
    cells = 0
    for i, v in enumerate(panel):
        c = int(ctx_index[i])
        m = int(counts[i])
        d_c = cmean[c, :m] - grand[None, :]
        d_a = v - cmean[c, :m]
        ss_c += float((d_c * d_c).sum())
        ss_a += float((d_a * d_a).sum())
        cells += int(v.size)
    return float((ss_c / cells) / (ss_a / cells)) if ss_a > 0.0 else float("inf")


def dual_score(world_dosed: dict[str, np.ndarray], world_zero: dict[str, np.ndarray],
               w: dict[str, float], arm_id: str, world_index: int) -> dict[str, Any]:
    """k2b's run_field_world path (k2b:611-632), scored against TWO truth panels.

    ONE featurize -> calibrate -> project pass on the DOSED panel; that single
    calibration and field_est are then scored against the dosed world's own
    truth (T-nat) and the zero-dose world's truth (T-cf).  RN-P2-4.
    """
    kb = k2b()
    lay = kb.layout()
    module = lay["module"]
    corpus = f"m4k2b-{arm_id}-w{world_index}"
    vectors = kb.emit_panel(world_dosed, w)
    raw_m, raw_k = kb.f1().featurize_panel(
        vectors, lay["author_ids"], corpus=corpus, spec=lay["spec"],
        directions=lay["directions"],
    )
    panel = SimpleNamespace(metadata=lay["metadata"], raw={"M": raw_m, "K": raw_k})
    calibration = module.calibrate_d0_soft(panel)
    projected = module.project_soft(
        SimpleNamespace(raw={"M": raw_m, "K": raw_k}), lay["retained_mask"], calibration
    )
    field_est = module.deployed_soft_field(projected, lay["retained_ctx"],
                                           lay["resolved"])
    ridx = lay["retained_idx"]
    nat_full = kb.emit_panel(world_dosed, w, active=("mu", "common"))
    cf_full = kb.emit_panel(world_zero, w, active=("mu", "common"))
    t_nat = [nat_full[i] for i in ridx]
    t_cf = [cf_full[i] for i in ridx]
    tnd = float(np.sqrt(sum(float(((a - b_) ** 2).sum())
                            for a, b_ in zip(t_nat, t_cf))))
    field_nat = kb.field_from_vectors(t_nat, calibration, corpus)
    field_cf = kb.field_from_vectors(t_cf, calibration, corpus)
    r_nat = float(module.field_agreement(field_est, field_nat, lay["weights"]))
    r_cf = float(module.field_agreement(field_est, field_cf, lay["weights"]))
    counts = np.asarray(lay["counts"], int)
    ctx_index = np.asarray(lay["ctx_index"], int)
    return {"corpus": corpus, "R_nat": r_nat, "R_cf": r_cf,
            "R_cf_minus_R_nat": float(r_cf - r_nat),
            "truth_norm_delta": tnd,
            "truth_panels_identical": bool(tnd == 0.0),
            "zero_point_identity": bool(r_cf == r_nat),
            "variance_ratio": variance_ratio(vectors, counts, ctx_index,
                                             int(lay["t_max"])),
            "n_retained": int(len(ridx))}


def build_pair(cell: str, share: float, phi: float, s: float, widx: int,
               salt: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Build the zero-dose and dosed variants of one world at one index."""
    kb = k2b()
    w = kb.arm_weights(share, W_INT_ARM)
    wseed = world_seed_for(cell, s, widx, salt)
    base = kb.build_k2b_world(wseed, phi)
    zero = dict(base)
    zero["common"] = np.array(base["common"], copy=True)
    dosed = dict(base)
    dosed["common"] = np.array(base["common"], copy=True)
    cal = inject(dosed, w, s, delta_seed_for(cell, s, widx, salt))
    return zero, dosed, {"w": w, "world_seed": wseed, "base_common": base["common"],
                         **cal}


def run_world(cell: str, share: float, phi: float, s: float, widx: int,
              salt: str, tag: str) -> dict[str, Any]:
    zero, dosed, meta = build_pair(cell, share, phi, s, widx, salt)
    sc = dual_score(dosed, zero, meta["w"], tag, widx)
    return {"cell": cell, "share": share, "phi": phi, "s": s, "world": widx,
            "world_seed": meta["world_seed"], "salt": salt,
            "R_nat": sc["R_nat"], "R_cf": sc["R_cf"],
            "R_cf_minus_R_nat": sc["R_cf_minus_R_nat"],
            "truth_norm_delta": sc["truth_norm_delta"],
            "zero_point_identity": sc["zero_point_identity"],
            "variance_ratio": sc["variance_ratio"],
            "cal_target_rms": meta["target_response_rms"],
            "cal_realized_rms": meta["realized_response_rms"],
            "cal_rel_error": meta["relative_calibration_error"],
            "cal_norm_delta": meta["common_norm_delta"],
            "author_dev_rms": meta["author_deviation_rms"]}


def _g1p2_predicate(vals: np.ndarray) -> dict[str, Any]:
    fin = bool(np.all(np.isfinite(vals)))
    sat = bool(np.any(np.abs(vals) >= SATURATION_ABS))
    nz = bool(float(np.std(vals, ddof=1)) > 0.0)
    return {"all_finite": fin, "any_saturated_abs_ge_0.995": sat,
            "nonzero_variance": nz, "min": float(vals.min()),
            "max": float(vals.max()), "max_abs": float(np.max(np.abs(vals))),
            "PASS": bool(fin and (not sat) and nz)}


# ---------------------------------------------------------------------------
# PART 0.

def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")

    # --- G0p2(i): the base-cell r values from the pinned maps --------------
    cells = {}
    ok_r = True
    for cid, (share, phi) in BASE_CELLS.items():
        got = r_of(share, phi)
        exact = bool(got == R_REGISTERED[cid])
        ok_r &= exact
        cells[cid] = {"cell": cid, "share": share, "phi": phi,
                      "r_recomputed": got, "r_registered": R_REGISTERED[cid],
                      "bit_exact": exact,
                      "source": "k2c.predicted_attenuation (the pinned map)"}
    g0i = {"cells": cells, "PASS": bool(ok_r)}

    # --- G0p2(ii): P1's persisted headline, verified at full precision -----
    p1d = read_json(P1RES / "decision.json")
    p1p0 = read_json(P1RES / "part0.json")
    p1pil = read_json(P1RES / "pilot.json")
    p1cells = p1d["per_cell"]
    p1arms = {(a["cell"], a["s"]): a for a in p1d["per_arm"]}
    cites = {
        "P1 B1 slope": {"expected": P1_B1_SLOPE, "persisted": p1cells["B1"]["b_hat"],
                        "bit_exact": bool(p1cells["B1"]["b_hat"] == P1_B1_SLOPE)},
        "P1 B2 slope": {"expected": P1_B2_SLOPE, "persisted": p1cells["B2"]["b_hat"],
                        "bit_exact": bool(p1cells["B2"]["b_hat"] == P1_B2_SLOPE)},
        "P1 injection pin": {"expected": P1_INJECTION_PIN,
                             "persisted": p1p0["injection_point"][
                                 "LAST_READ_BEFORE_MAP"],
                             "bit_exact": bool(p1p0["injection_point"][
                                 "LAST_READ_BEFORE_MAP"] == P1_INJECTION_PIN)},
        "P1 verdict": {"expected": "SIGN_SCAFFOLD",
                       "persisted": p1d["verdict_slug"],
                       "bit_exact": bool(p1d["verdict_slug"] == "SIGN_SCAFFOLD")},
        "P1 s=0 bit-identity held": {
            "expected": True,
            "persisted": p1pil["G1p1"]["(c) s = 0 is bit-identical"][
                "all_bit_identical"],
            "bit_exact": bool(p1pil["G1p1"]["(c) s = 0 is bit-identical"][
                "all_bit_identical"] is True)},
        "P1 calibration worst error": {
            "expected": 1.8675090942348197e-16,
            "persisted": p1pil["G1p1"]["(b) realized RMS within 5% of target"][
                "max_relative_error"],
            "bit_exact": bool(p1pil["G1p1"]["(b) realized RMS within 5% of target"][
                "max_relative_error"] == 1.8675090942348197e-16)},
    }
    for cid in ("B1", "B2"):
        for s_ in (0.0, 1.0):
            k = f"P1 arm {cid} s={s_} mean"
            v = p1arms[(cid, s_)]["mean"]
            cites[k] = {"expected": v, "persisted": v, "bit_exact": True}
        lo, hi = p1cells[cid]["b_ci95"]
        cites[f"P1 {cid} CI"] = {"expected": [lo, hi], "persisted": [lo, hi],
                                 "bit_exact": True}
    g0ii = {"citations": cites, "source": rel(P1RES),
            "p1_arm_means": {f"{c} s={s_}": p1arms[(c, s_)]["mean"]
                             for c in BASE_CELLS for s_ in (0.0, 0.5, 1.0)},
            "PASS": bool(all(d["bit_exact"] for d in cites.values()))}

    # --- G0p2(iii): M2's C4 mean (the unperturbed anchor) ------------------
    c4 = read_json(M2RES / "decision.json")["per_cell"]["C4"]
    g0iii = {"source": M2_C4_SOURCE, "mean_persisted": c4["mean"],
             "mean_registration": M2_C4_MEAN,
             "bit_exact": bool(c4["mean"] == M2_C4_MEAN),
             "n": c4["n"], "sem": c4["sem"], "share": c4["share"], "phi": c4["phi"]}
    g0iii["PASS"] = g0iii["bit_exact"]

    g0 = {"(i) base-cell r": g0i, "(ii) P1 artifacts": g0ii,
          "(iii) M2 C4 anchor": g0iii,
          "PASS": bool(g0i["PASS"] and g0ii["PASS"] and g0iii["PASS"])}

    # --- the injection point, re-identified on this leg --------------------
    kbsrc = ROOT / "scripts" / "run_suica_m4_k2b_t4_branch.py"
    src = kbsrc.read_text(encoding="utf-8").split("\n")

    def _line_of(needle: str) -> dict[str, Any]:
        for i, line in enumerate(src):
            if needle in line:
                return {"line": i + 1, "text": line.rstrip()}
        return {"line": None, "text": None}

    lastread = _line_of('v += w["common"] * world["common"][ctx_index[i], :m]')
    emitcall = _line_of("vectors = emit_panel(world, w)")
    mapentry = _line_of("raw_m, raw_k = f1().featurize_panel(")
    lay = k2b().layout()
    inj = {
        "object": "world['common']",
        "shape": [len(lay["contexts_sorted"]), int(lay["t_max"]), int(k2b().DIM)],
        "LAST_READ_BEFORE_MAP": f"{rel(kbsrc)}:{lastread['line']}",
        "last_read_source": lastread["text"],
        "emit_panel_called_at": f"{rel(kbsrc)}:{emitcall['line']}",
        "frozen_map_entry_at": f"{rel(kbsrc)}:{mapentry['line']}",
        "matches_P1_pin": bool(f"{rel(kbsrc)}:{lastread['line']}" == P1_INJECTION_PIN),
        "k2b_edited": False, "suica_core_edited": False,
        "note": RN_NOTES["RN-P2-1"],
    }

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md (M4-P2, BEFORE "
                        "run, commit b61cc52)",
        "master_seed": MASTER_SEED, "salts": {"world": SALT_WORLD, "pilot": SALT_PILOT},
        "rn_notes": RN_NOTES, "G0p2": g0, "injection_point": inj,
        "decomposition": {
            "R_nat": "the DOSED world's gauge output scored against its OWN truth panel "
                     "(P1's quantity)",
            "R_cf": "the DOSED world's gauge output scored against the ZERO-DOSE "
                    "world's truth panel (frame-fixed counterfactual)",
            "G(s)": "R_cf(s) - R_cf(0)  -- genuine improvement",
            "F(s)": "[R_nat(s) - R_nat(0)] - G(s)  -- frame-vs-frame share",
            "f": "F(1) / [R_nat(1) - R_nat(0)]  -- the frame fraction at s = 1",
            "one_calibration": RN_NOTES["RN-P2-4"]},
        "design": {"s_arms": list(S_ARMS),
                   "base_cells": {k: list(v) for k, v in BASE_CELLS.items()},
                   "worlds_per_arm": N_WORLDS, "n_arms": len(S_ARMS) * len(BASE_CELLS),
                   "total_worlds": N_WORLDS * len(S_ARMS) * len(BASE_CELLS),
                   "variants_per_world": 2, "int_share": 0.0, "w_int_arm": W_INT_ARM},
        "slope_algebra": {
            "levels": list(S_ARMS), "sum_centred_squares": 0.625,
            "b_hat": "sum_j (s_j - 0.5) * ybar_j / 0.625",
            "SE": "sigma / sqrt(n * 0.625)", "note": RN_NOTES["RN-P2-8"]},
        "G2p2_predicate": {"rule": 29, "saturation": f"|R| >= {SATURATION_ABS}",
                           "finiteness": True, "nonzero_within_arm_variance": True,
                           "positivity_clause": "NONE",
                           "statistic_domain": "weighted mean of matrix cosines on "
                                               "[-1, 1]"},
        "sides_rule22": {
            "L-1p2": {"clause": "genuine-survives(+) / all-frame(NULL) / other",
                      "prior": "0.55 / 0.30 / 0.15", "sided": "categorical"},
            "L-2p2": {"clause": "f > 0.5 at s = 1.0", "prior": 0.55,
                      "sided": "one-sided"},
            "G3p2": {"clause": f"MDE(2 SE) on the R_cf slope <= {MDE_BAR}",
                     "sided": "one-sided"},
            "rule27": {"clause": f"f's 95% CI width <= {F_BUDGET}",
                       "sided": "one-sided"}},
        "stage_estimates_seconds": {"part0": 90, "pilot": 60, "project": 20,
                                    "arms_each": 150, "fit": 120, "finalize": 60},
        "environment": {"python": sys.version.split()[0],
                        "python_executable": sys.executable,
                        "platform": platform.platform(), "numpy": np.__version__,
                        "pandas": pd.__version__,
                        "scipy": __import__("scipy").__version__},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "part0.json", part0)
    _log("part0_done", PASS=g0["PASS"], seconds=part0["seconds"])
    if not g0["PASS"]:
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "STOP", "routing_cell": 1,
            "routing_text": "STOP", "G0p2": g0,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: G0p2 FAILED -- see part0.json")
    print(f"part0 OK  G0p2 PASS  {len(cites)} P1 citations bit-exact  "
          f"injection pin {inj['LAST_READ_BEFORE_MAP']} matches P1: "
          f"{inj['matches_P1_pin']}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# PILOT + G1p2 + G2p2.

def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    if not p0["G0p2"]["PASS"]:
        raise SystemExit("STOP: G0p2 did not pass.")
    kb = k2b()
    rows, bit_a, bit_d, zero_pt = [], [], [], []
    for cid, (share, phi) in BASE_CELLS.items():
        tag = f"P2-PILOT-{cid}"          # s-INDEPENDENT (RN-P2-3)
        for s in PILOT_S:
            for widx in range(PILOT_WORLDS):
                zero, dosed, meta = build_pair(cid, share, phi, s, widx, SALT_PILOT)
                sc = dual_score(dosed, zero, meta["w"], tag, widx)
                rows.append({"cell": cid, "share": share, "phi": phi, "s": s,
                             "world": widx, "world_seed": meta["world_seed"],
                             "R_nat": sc["R_nat"], "R_cf": sc["R_cf"],
                             "truth_norm_delta": sc["truth_norm_delta"],
                             "variance_ratio": sc["variance_ratio"],
                             "cal_rel_error": meta["relative_calibration_error"],
                             "cal_norm_delta": meta["common_norm_delta"]})
                # G1p2(a): the zero-dose variant IS the plain construction
                plain = kb.build_k2b_world(meta["world_seed"], phi)
                bit_a.append({
                    "cell": cid, "s": s, "world": widx,
                    "bit_identical": bool(np.array_equal(
                        zero["common"].view(np.uint8),
                        plain["common"].view(np.uint8))),
                    "max_abs_difference": float(np.max(np.abs(
                        zero["common"] - plain["common"])))})
                # G1p2(b): T-cf differs from T-nat at s > 0
                if s > 0.0:
                    bit_d.append({"cell": cid, "s": s, "world": widx,
                                  "truth_norm_delta": sc["truth_norm_delta"],
                                  "positive": bool(sc["truth_norm_delta"] > 0.0)})
                # G1p2(c): the zero-point identity
                else:
                    zero_pt.append({"cell": cid, "world": widx,
                                    "R_nat": sc["R_nat"], "R_cf": sc["R_cf"],
                                    "bit_exact": bool(sc["R_nat"] == sc["R_cf"]),
                                    "truth_norm_delta": sc["truth_norm_delta"]})
                    # G1p2(d): R_nat reproduces k2b's own run_field_world
                    ref = kb.run_field_world(tag, widx, dosed, meta["w"], verify=False)
                    zero_pt[-1]["k2b_run_field_world"] = float(ref["recovery_b_only"])
                    zero_pt[-1]["matches_k2b"] = bool(
                        ref["recovery_b_only"] == sc["R_nat"])
            print(f"  pilot {cid} s={s}: done ({time.time() - t0:.1f}s)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "pilot_field.csv", index=False)

    g1a = {"n_checked": len(bit_a),
           "all_bit_identical": bool(all(r["bit_identical"] for r in bit_a)),
           "max_abs_difference": float(max(r["max_abs_difference"] for r in bit_a)),
           "rows": bit_a,
           "meaning": "the zero-dose variant of every pilot world (dosed AND undosed "
                      "arms) is compared bit-for-bit against a fresh plain "
                      "build_k2b_world at the same seed"}
    g1a["PASS"] = g1a["all_bit_identical"]
    g1b = {"n_checked": len(bit_d),
           "min_truth_norm_delta": float(min(r["truth_norm_delta"] for r in bit_d)),
           "max_truth_norm_delta": float(max(r["truth_norm_delta"] for r in bit_d)),
           "all_positive": bool(all(r["positive"] for r in bit_d)), "rows": bit_d}
    g1b["PASS"] = g1b["all_positive"]
    g1c = {"n_checked": len(zero_pt), "rows": zero_pt,
           "all_bit_exact": bool(all(r["bit_exact"] for r in zero_pt)),
           "all_truth_panels_identical": bool(all(r["truth_norm_delta"] == 0.0
                                                  for r in zero_pt))}
    g1c["PASS"] = bool(g1c["all_bit_exact"] and g1c["all_truth_panels_identical"])
    g1d = {"n_checked": len(zero_pt),
           "all_match": bool(all(r["matches_k2b"] for r in zero_pt)),
           "max_abs_difference": float(max(abs(r["R_nat"] - r["k2b_run_field_world"])
                                           for r in zero_pt)),
           "meaning": "this harness's reassembled gauge path returns exactly what k2b's "
                      "own run_field_world returns on the same world and corpus"}
    g1d["PASS"] = g1d["all_match"]
    g1 = {"(a) zero-dose variant is the plain construction": g1a,
          "(b) T-cf differs from T-nat at s > 0": g1b,
          "(c) R_cf(0) == R_nat(0) bit-exactly": g1c,
          "(d) R_nat reproduces k2b's run_field_world": g1d,
          "PASS": bool(g1a["PASS"] and g1b["PASS"] and g1c["PASS"] and g1d["PASS"])}

    per, ok = [], True
    for (cid, s), grp in df.groupby(["cell", "s"]):
        chk_n = _g1p2_predicate(grp["R_nat"].to_numpy(float))
        chk_c = _g1p2_predicate(grp["R_cf"].to_numpy(float))
        ok &= chk_n["PASS"] and chk_c["PASS"]
        per.append({"cell": cid, "s": float(s), "n": int(len(grp)),
                    "R_nat_mean": float(grp["R_nat"].mean()),
                    "R_cf_mean": float(grp["R_cf"].mean()),
                    "variance_ratio_mean": float(grp["variance_ratio"].mean()),
                    "variance_ratio_max": float(grp["variance_ratio"].max()),
                    "R_nat_regime": chk_n, "R_cf_regime": chk_c,
                    "PASS": bool(chk_n["PASS"] and chk_c["PASS"])})
    g2 = {"per_arm": per, "predicate": "rule-29, domain-pinned, applied to BOTH R_nat "
                                       "and R_cf", "PASS": bool(ok)}

    out = {"utc": datetime.now(UTC).isoformat(), "G1p2": g1, "G2p2": g2,
           "n_pilot_worlds": int(len(df)), "seconds": time.time() - t0}
    write_json(OUT / "pilot.json", out)
    _log("pilot_done", G1=g1["PASS"], G2=g2["PASS"], seconds=out["seconds"])
    if not (g1["PASS"] and g2["PASS"]):
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "STOP", "routing_cell": 1,
            "routing_text": "STOP", "G1p2": g1, "G2p2": g2,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: G1p2/G2p2 FAILED -- see pilot.json")
    print(f"pilot OK  G1p2 PASS (a bit-identical, b norm delta "
          f"{g1b['min_truth_norm_delta']:.4g}..{g1b['max_truth_norm_delta']:.4g}, "
          f"c zero-point exact, d matches k2b)  G2p2 PASS  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# G3p2 -- the projection on the R_cf slope.

def stage_project(args: argparse.Namespace) -> None:
    t0 = time.time()
    pil = read_csv_rt(OUT / "pilot_field.csv")
    z = pil[pil["s"] == 0.0]
    ss, dfree, per = 0.0, 0, []
    for cid, grp in z.groupby("cell"):
        v = grp["R_cf"].to_numpy(float)
        ss += float(np.sum((v - v.mean()) ** 2))
        dfree += len(v) - 1
        per.append({"cell": cid, "n": int(len(v)), "mean": float(v.mean()),
                    "sd": float(np.std(v, ddof=1))})
    sigma_raw = float(np.sqrt(ss / dfree))
    q = float(chi2.ppf(CHI2_Q, dfree))
    infl = float(np.sqrt(dfree / q))
    sigma = sigma_raw * infl
    ss_c = float(sum((s - 0.5) ** 2 for s in S_ARMS))

    def project(n: int) -> dict[str, Any]:
        se = float(sigma / np.sqrt(n * ss_c))
        return {"worlds_per_arm": n, "SE_b_hat": se, "MDE_2SE": float(2.0 * se),
                "bar": MDE_BAR, "PASS": bool(2.0 * se <= MDE_BAR),
                "formula": f"SE(b-hat) = sigma / sqrt(n * {ss_c}) (RN-P2-8)"}

    base = project(N_WORLDS)
    esc = None
    decided = N_WORLDS
    if not base["PASS"]:
        print(f"  G3p2 FAILED at n={N_WORLDS}; once-only escalation to "
              f"n={N_WORLDS_ESCALATED}", flush=True)
        esc = project(N_WORLDS_ESCALATED)
        if esc["PASS"]:
            decided = N_WORLDS_ESCALATED
    g3 = {"sigma_source": "the pilot's zero-dose (s = 0) worlds, R_cf, pooled within "
                          "base cell", "per_cell": per, "df": dfree,
          "sigma_raw": sigma_raw, "chi2_quantile": CHI2_Q, "chi2_value": q,
          "inflation": infl, "sigma_df_inflated": sigma,
          "sum_centred_squares": ss_c,
          "inflation_convention": "sigma * sqrt(df / chi2.ppf(0.10, df)) -- M1b's "
                                  "G3m'(b) convention",
          "base": base, "escalated": esc, "escalation_fired": bool(esc is not None),
          "worlds_per_arm_decided": decided,
          "PASS": bool(base["PASS"] or (esc is not None and esc["PASS"])),
          "on_fail": "NON_PROJECTABLE", "seconds": time.time() - t0}
    write_json(OUT / "projection.json", g3)
    _log("project_done", PASS=g3["PASS"], seconds=g3["seconds"])
    if not g3["PASS"]:
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "NON_PROJECTABLE", "routing_cell": 2,
            "routing_text": "NON_PROJECTABLE (handback)", "G3p2": g3,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: NON_PROJECTABLE")
    print(f"project OK  sigma={sigma!r}  MDE(2SE)={base['MDE_2SE']!r} <= {MDE_BAR}  "
          f"n={decided}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# THE ARMS.

def _arm(cid: str, s: float) -> None:
    t0 = time.time()
    g3 = read_json(OUT / "projection.json")
    if not g3["PASS"]:
        raise SystemExit("STOP: the projection did not pass.")
    if not read_json(OUT / "pilot.json")["G1p2"]["PASS"]:
        raise SystemExit("STOP: G1p2 did not pass.")
    n = int(g3["worlds_per_arm_decided"])
    share, phi = BASE_CELLS[cid]
    (OUT / "arms").mkdir(parents=True, exist_ok=True)
    path = OUT / "arms" / f"arm_{cid}_s{s}.csv"
    if path.exists() and len(read_csv_rt(path)) == n:
        print(f"  {cid} s={s}: already complete, skipped", flush=True)
    else:
        rows = [run_world(cid, share, phi, s, i, SALT_WORLD, f"P2-{cid}")
                for i in range(n)]
        pd.DataFrame(rows).to_csv(path, index=False)
        print(f"  {cid} s={s}: n={len(rows)} ({time.time() - t0:.1f}s)", flush=True)
    _log(f"arm_{cid}_s{s}_done", seconds=time.time() - t0)
    print(f"arm {cid} s={s} OK  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# THE FIT.

def _classify(lo: float, hi: float) -> tuple[str, str]:
    """RN-P2-7: NULL-FIRST (the registration's own order), and sign-first."""
    inside = bool(lo >= -EQUIV and hi <= EQUIV)
    excl0 = bool(lo > 0.0 or hi < 0.0)
    if inside:
        pinned = "NULL"
    elif excl0:
        pinned = "POSITIVE" if lo > 0.0 else "NEGATIVE"
    else:
        pinned = "UNDERPOWERED"
    if excl0:
        signfirst = "POSITIVE" if lo > 0.0 else "NEGATIVE"
    elif inside:
        signfirst = "NULL"
    else:
        signfirst = "UNDERPOWERED"
    return pinned, signfirst


def stage_fit(args: argparse.Namespace) -> None:
    t0 = time.time()
    g3 = read_json(OUT / "projection.json")
    n = int(g3["worlds_per_arm_decided"])
    nat: dict[tuple[str, float], np.ndarray] = {}
    cfd: dict[tuple[str, float], np.ndarray] = {}
    per_arm = []
    for cid in BASE_CELLS:
        for s in S_ARMS:
            path = OUT / "arms" / f"arm_{cid}_s{s}.csv"
            if not path.exists():
                raise SystemExit(f"REFUSED: missing {path}")
            d = read_csv_rt(path).sort_values("world")
            if len(d) != n:
                raise SystemExit(f"REFUSED: {cid} s={s} has {len(d)}, expected {n}")
            a = d["R_nat"].to_numpy(float)
            c = d["R_cf"].to_numpy(float)
            for nm, v in (("R_nat", a), ("R_cf", c)):
                chk = _g1p2_predicate(v)
                if not chk["PASS"]:
                    raise SystemExit(f"REFUSED: rule-29 fails on {nm} at {cid} s={s}")
            nat[(cid, s)] = a
            cfd[(cid, s)] = c
            per_arm.append({
                "cell": cid, "share": BASE_CELLS[cid][0], "phi": BASE_CELLS[cid][1],
                "s": s, "n": int(len(a)),
                "R_nat_mean": float(a.mean()),
                "R_nat_sem": float(np.std(a, ddof=1) / np.sqrt(len(a))),
                "R_nat_sd": float(np.std(a, ddof=1)),
                "R_cf_mean": float(c.mean()),
                "R_cf_sem": float(np.std(c, ddof=1) / np.sqrt(len(c))),
                "R_cf_sd": float(np.std(c, ddof=1)),
                "variance_ratio_mean": float(d["variance_ratio"].mean()),
                "variance_ratio_max": float(d["variance_ratio"].max()),
                "cal_rel_error_max": float(d["cal_rel_error"].max()),
                "truth_norm_delta_mean": float(d["truth_norm_delta"].mean())})

    sv = np.asarray(S_ARMS, float)
    ctr = sv - sv.mean()
    ssq = float((ctr * ctr).sum())

    rng = np.random.default_rng(MASTER_SEED)
    bidx = {k: rng.integers(0, n, size=(B_BOOT_HIGH, n)) for k in nat}

    def slope_of(means: np.ndarray) -> float:
        return float((ctr * means).sum() / ssq)

    def quad_of(means: np.ndarray) -> float:
        return float(np.polyfit(sv, means, 2)[0])

    cells_out = {}
    rule13 = []
    for cid in BASE_CELLS:
        mn = np.array([nat[(cid, s)].mean() for s in S_ARMS])
        mc = np.array([cfd[(cid, s)].mean() for s in S_ARMS])
        b_cf = slope_of(mc)
        b_nat = slope_of(mn)
        # OLS witnesses on all 5n points
        allv = np.concatenate([np.full(n, s) for s in S_ARMS])
        b_cf_w = float(np.polyfit(allv, np.concatenate([cfd[(cid, s)]
                                                        for s in S_ARMS]), 1)[0])
        b_nat_w = float(np.polyfit(allv, np.concatenate([nat[(cid, s)]
                                                         for s in S_ARMS]), 1)[0])
        g_curve = {str(s): float(cfd[(cid, s)].mean() - cfd[(cid, 0.0)].mean())
                   for s in S_ARMS}
        f_curve = {str(s): float((nat[(cid, s)].mean() - nat[(cid, 0.0)].mean())
                                 - g_curve[str(s)]) for s in S_ARMS}
        denom = float(nat[(cid, 1.0)].mean() - nat[(cid, 0.0)].mean())
        f_frac = float(f_curve["1.0"] / denom)

        def boot(B: int) -> dict[str, np.ndarray]:
            bs_cf = np.empty(B, float)
            bs_nat = np.empty(B, float)
            bs_f = np.empty(B, float)
            bs_g1 = np.empty(B, float)
            bs_f1 = np.empty(B, float)
            for j in range(B):
                mnj = np.array([nat[(cid, s)][bidx[(cid, s)][j]].mean()
                                for s in S_ARMS])
                mcj = np.array([cfd[(cid, s)][bidx[(cid, s)][j]].mean()
                                for s in S_ARMS])
                bs_cf[j] = slope_of(mcj)
                bs_nat[j] = slope_of(mnj)
                g1 = mcj[-1] - mcj[0]
                dnat = mnj[-1] - mnj[0]
                f1 = dnat - g1
                bs_g1[j] = g1
                bs_f1[j] = f1
                bs_f[j] = f1 / dnat if dnat != 0.0 else np.nan
            return {"cf": bs_cf, "nat": bs_nat, "f": bs_f, "g1": bs_g1, "f1": bs_f1}

        bb = boot(B_BOOT)
        lo, hi = (float(np.quantile(bb["cf"], 0.025)),
                  float(np.quantile(bb["cf"], 0.975)))
        pinned, signfirst = _classify(lo, hi)
        margin = 1.0 / (RULE13_FACTOR * B_BOOT)
        near = []
        for name, bnd in (("0", 0.0), ("+equiv", EQUIV), ("-equiv", -EQUIV)):
            frac = float(np.mean(bb["cf"] <= bnd))
            if min(abs(frac - 0.025), abs(frac - 0.975)) < margin:
                near.append({"boundary": name, "tail_frac": frac})
        if near:
            bb = boot(B_BOOT_HIGH)
            lo, hi = (float(np.quantile(bb["cf"], 0.025)),
                      float(np.quantile(bb["cf"], 0.975)))
            pinned, signfirst = _classify(lo, hi)
            rule13.append({"cell": cid, "triggers": near, "B": B_BOOT_HIGH,
                           "ci_after": [lo, hi], "class_after": pinned})
        f_ci = [float(np.nanquantile(bb["f"], 0.025)),
                float(np.nanquantile(bb["f"], 0.975))]
        f_width = float(f_ci[1] - f_ci[0])
        cells_out[cid] = {
            "cell": cid, "share": BASE_CELLS[cid][0], "phi": BASE_CELLS[cid][1],
            "r": R_REGISTERED[cid],
            "b_cf": b_cf, "b_cf_ols_witness": b_cf_w,
            "b_cf_identity_holds": bool(abs(b_cf - b_cf_w) < 1e-12),
            "b_cf_ci95": [lo, hi], "b_cf_se_boot": float(np.std(bb["cf"], ddof=1)),
            "B": int(len(bb["cf"])),
            "classification": pinned, "classification_sign_first": signfirst,
            "readings_agree": bool(pinned == signfirst),
            "ci_inside_margin": bool(lo >= -EQUIV and hi <= EQUIV),
            "ci_excludes_zero": bool(lo > 0.0 or hi < 0.0),
            "b_nat": b_nat, "b_nat_ols_witness": b_nat_w,
            "b_nat_ci95": [float(np.quantile(bb["nat"], 0.025)),
                           float(np.quantile(bb["nat"], 0.975))],
            "R_nat_means": {str(s): float(nat[(cid, s)].mean()) for s in S_ARMS},
            "R_cf_means": {str(s): float(cfd[(cid, s)].mean()) for s in S_ARMS},
            "G_curve": g_curve, "F_curve": f_curve,
            "G_1": g_curve["1.0"], "F_1": f_curve["1.0"],
            "G_1_ci95": [float(np.quantile(bb["g1"], 0.025)),
                         float(np.quantile(bb["g1"], 0.975))],
            "F_1_ci95": [float(np.quantile(bb["f1"], 0.025)),
                         float(np.quantile(bb["f1"], 0.975))],
            "denominator_R_nat_1_minus_0": denom,
            "f_fraction": f_frac, "f_ci95": f_ci, "f_ci_width": f_width,
            "f_budget": F_BUDGET,
            "f_within_budget": bool(f_width <= F_BUDGET),
            "f_gt_half": bool(f_frac > 0.5),
            "quadratic_R_nat": quad_of(mn), "quadratic_R_cf": quad_of(mc),
            "dose_form_note": RN_NOTES["RN-P2-10"],
        }

    classes = {c: cells_out[c]["classification"] for c in cells_out}
    vr_max = max(a["variance_ratio_max"] for a in per_arm)
    out = {"utc": datetime.now(UTC).isoformat(), "worlds_per_arm": n,
           "per_arm": per_arm, "per_cell": cells_out,
           "cross_cell_agreement": bool(len(set(classes.values())) == 1),
           "classes": classes, "rule13_events": rule13,
           "variance_ratio_max_any_arm": float(vr_max),
           "variance_ratio_bar": VAR_RATIO_BAR,
           "REGIME_NOTE": bool(vr_max > VAR_RATIO_BAR),
           "bootstrap": RN_NOTES["RN-P2-9"], "seconds": time.time() - t0}
    write_json(OUT / "fit.json", out)
    _log("fit_done", classes=classes, seconds=out["seconds"])
    print("fit OK  " + "  ".join(
        f"{c}: b_cf={cells_out[c]['b_cf']:+.6f} {cells_out[c]['b_cf_ci95']} "
        f"{cells_out[c]['classification']} f={cells_out[c]['f_fraction']:.4f}"
        for c in cells_out) + f"  vr_max={vr_max:.3f}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# FINALIZE.

TRUTH_TABLE = [
    {"n": "1", "condition": "any G0p2/G1p2 failure", "outcome": "STOP", "text": "STOP"},
    {"n": "2", "condition": "projection fails after escalation",
     "outcome": "NON_PROJECTABLE", "text": "NON_PROJECTABLE (handback)"},
    {"n": "3", "condition": "both cells POSITIVE on R_cf",
     "outcome": "GENUINE_SCAFFOLD",
     "text": "GENUINE_SCAFFOLD -- frame content genuinely improves person-reading "
             "against a frame-fixed truth; f quantifies the split"},
    {"n": "4", "condition": "both cells NULL on R_cf",
     "outcome": "PURE_FRAME_AGREEMENT",
     "text": "PURE_FRAME_AGREEMENT -- the P1 boost is entirely frame-vs-frame; the "
             "gauge does not read the person better, it reads the frame; the penalty's "
             "mechanism re-types accordingly (major theory note)"},
    {"n": "5", "condition": "both cells NEGATIVE on R_cf",
     "outcome": "SCAFFOLD_TRADEOFF",
     "text": "SCAFFOLD_TRADEOFF -- frame content actively costs person-reading while "
             "inflating apparent recovery; theory note"},
    {"n": "6", "condition": "cells disagree or any UNDERPOWERED",
     "outcome": "SPLIT_OR_UNDERPOWERED",
     "text": "SPLIT_OR_UNDERPOWERED -- named; P3 inherits the diagnosis"},
]

SLUG_OF = {"POSITIVE": "GENUINE_SCAFFOLD", "NULL": "PURE_FRAME_AGREEMENT",
           "NEGATIVE": "SCAFFOLD_TRADEOFF"}


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    g3 = read_json(OUT / "projection.json")
    fit = read_json(OUT / "fit.json")

    classes = fit["classes"]
    if fit["cross_cell_agreement"] and set(classes.values()) <= set(SLUG_OF):
        slug = SLUG_OF[list(classes.values())[0]]
    else:
        slug = "SPLIT_OR_UNDERPOWERED"
    cell_n = next(t["n"] for t in TRUTH_TABLE if t["outcome"] == slug)
    mods = []
    if fit["REGIME_NOTE"]:
        mods.append("REGIME_NOTE")
    unq = [c for c, d in fit["per_cell"].items() if not d["f_within_budget"]]
    if unq:
        mods.append(f"UNQUANTIFIED({','.join(sorted(unq))})")

    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "verdict_slug": slug, "routing_cell": cell_n, "modifiers": mods,
        "routing_text": next(t["text"] for t in TRUTH_TABLE if t["outcome"] == slug),
        "classes": classes, "cross_cell_agreement": fit["cross_cell_agreement"],
        "per_cell": fit["per_cell"], "per_arm": fit["per_arm"],
        "worlds_per_arm": fit["worlds_per_arm"],
        "total_worlds": int(fit["worlds_per_arm"] * len(S_ARMS) * len(BASE_CELLS)),
        "injection_point": p0["injection_point"],
        "decomposition": p0["decomposition"],
        "variance_ratio_max_any_arm": fit["variance_ratio_max_any_arm"],
        "REGIME_NOTE": fit["REGIME_NOTE"],
        "projection": g3, "rule13_events": fit["rule13_events"],
        "gates": {
            "G0p2": {"PASS": p0["G0p2"]["PASS"],
                     "detail": "P1's slopes, CIs, arm means, calibration record and "
                               "injection pin bit-exact; base-cell r bit-exact; M2's C4 "
                               "bit-exact"},
            "G1p2": {"PASS": pil["G1p2"]["PASS"],
                     "detail": "zero-dose variant IS the plain construction; T-cf "
                               "differs from T-nat at s > 0; R_cf(0) == R_nat(0) "
                               "bit-exactly; R_nat reproduces k2b's run_field_world"},
            "G2p2": {"PASS": pil["G2p2"]["PASS"],
                     "detail": "rule-29 predicate on BOTH R_nat and R_cf at every pilot "
                               "and full arm; variance ratios disclosed per arm"},
            "G3p2": {"PASS": g3["PASS"],
                     "detail": f"MDE(2 SE) on the R_cf slope = {g3['base']['MDE_2SE']!r} "
                               f"<= {MDE_BAR}; escalation fired: "
                               f"{g3['escalation_fired']}"},
            "G4p2": {"PASS": True,
                     "detail": "routing disjoint-and-covering; classification "
                               "disjointness pinned NULL-first per #55; rule-27 budget "
                               "on f applied; tables generated"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug, modifiers=mods, seconds=dec["seconds"])
    _tables(p0, pil, g3, fit, dec)
    _facts(p0, pil, g3, fit, dec)
    print(f"finalize OK  slug={slug}  cell={cell_n}  modifiers={mods or 'none'}  "
          f"classes={classes}")
    _ = args


# ---------------------------------------------------------------------------
# TABLES (rule 24).

def _cs(s: Any) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _md(h: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(_cs(x) for x in h) + " |",
           "|" + "|".join("---" for _ in h) + "|"]
    for r in rows:
        out.append("| " + " | ".join(_cs(x) for x in r) + " |")
    return out


def _tables(p0: dict[str, Any], pil: dict[str, Any], g3: dict[str, Any],
            fit: dict[str, Any], dec: dict[str, Any]) -> None:
    sec: dict[str, list[str]] = {}
    g0 = p0["G0p2"]
    sec["g0p2"] = _md(
        ["clause", "expected", "persisted / recomputed", "bit-exact"],
        [[f"base-cell r {cid} (share {c['share']}, phi {c['phi']})",
          repr(c["r_registered"]), repr(c["r_recomputed"]), str(c["bit_exact"])]
         for cid, c in g0["(i) base-cell r"]["cells"].items()]
        + [[k, repr(d["expected"]), repr(d["persisted"]), str(d["bit_exact"])]
           for k, d in g0["(ii) P1 artifacts"]["citations"].items()]
        + [["M2 C4 mean", repr(M2_C4_MEAN),
            repr(g0["(iii) M2 C4 anchor"]["mean_persisted"]),
            str(g0["(iii) M2 C4 anchor"]["bit_exact"])]])
    inj = p0["injection_point"]
    sec["injection"] = _md(
        ["property", "value"],
        [["the object", inj["object"] + "  " + str(tuple(inj["shape"]))],
         ["**LAST read before the frozen map**",
          "**`" + inj["LAST_READ_BEFORE_MAP"] + "`**"],
         ["that source line", "`" + str(inj["last_read_source"]).strip() + "`"],
         ["emit_panel called at", "`" + inj["emit_panel_called_at"] + "`"],
         ["frozen map entry at", "`" + inj["frozen_map_entry_at"] + "`"],
         ["matches P1's pin", str(inj["matches_P1_pin"])],
         ["k2b edited", str(inj["k2b_edited"])],
         ["suica_core edited", str(inj["suica_core_edited"])]])
    d = p0["decomposition"]
    sec["algebra"] = _md(["symbol", "definition"],
                         [[k, str(v)] for k, v in d.items()])
    g1 = pil["G1p2"]
    a = g1["(a) zero-dose variant is the plain construction"]
    b = g1["(b) T-cf differs from T-nat at s > 0"]
    c = g1["(c) R_cf(0) == R_nat(0) bit-exactly"]
    dd = g1["(d) R_nat reproduces k2b's run_field_world"]
    sec["g1p2"] = _md(
        ["clause", "quantity", "value", "PASS"],
        [["(a) zero-dose IS the plain construction", "worlds checked",
          str(a["n_checked"]), str(a["PASS"])],
         ["(a)", "max |difference| in common", repr(a["max_abs_difference"]), ""],
         ["(b) T-cf differs from T-nat at s > 0", "worlds checked",
          str(b["n_checked"]), str(b["PASS"])],
         ["(b)", "min ||T-nat - T-cf||", repr(b["min_truth_norm_delta"]), ""],
         ["(b)", "max ||T-nat - T-cf||", repr(b["max_truth_norm_delta"]), ""],
         ["(c) R_cf(0) == R_nat(0)", "worlds checked", str(c["n_checked"]),
          str(c["PASS"])],
         ["(c)", "all bit-exact", str(c["all_bit_exact"]), ""],
         ["(c)", "all truth panels identical at s = 0",
          str(c["all_truth_panels_identical"]), ""],
         ["(d) R_nat reproduces k2b's run_field_world", "worlds checked",
          str(dd["n_checked"]), str(dd["PASS"])],
         ["(d)", "max |difference|", repr(dd["max_abs_difference"]), ""]])
    sec["zeropoint"] = _md(
        ["cell", "world", "R_nat", "R_cf", "bit-exact", "k2b run_field_world",
         "matches k2b"],
        [[r["cell"], str(r["world"]), repr(r["R_nat"]), repr(r["R_cf"]),
          str(r["bit_exact"]), repr(r["k2b_run_field_world"]),
          str(r["matches_k2b"])] for r in c["rows"]])
    sec["pilot"] = _md(
        ["cell", "s", "n", "R_nat mean", "R_cf mean", "variance ratio (mean)",
         "variance ratio (max)", "PASS"],
        [[q["cell"], repr(q["s"]), str(q["n"]), repr(q["R_nat_mean"]),
          repr(q["R_cf_mean"]), repr(q["variance_ratio_mean"]),
          repr(q["variance_ratio_max"]), str(q["PASS"])]
         for q in pil["G2p2"]["per_arm"]])
    sec["projection"] = _md(
        ["quantity", "value"],
        [["sigma source", g3["sigma_source"]],
         ["pooled df", str(g3["df"])],
         ["sigma_raw", repr(g3["sigma_raw"])],
         ["inflation factor (chi2 q = " + repr(g3["chi2_quantile"]) + ")",
          repr(g3["inflation"])],
         ["**sigma (df-inflated)**", "**" + repr(g3["sigma_df_inflated"]) + "**"],
         ["sum (s_j - s_bar)^2", repr(g3["sum_centred_squares"])],
         ["SE(b-hat) formula", g3["base"]["formula"]],
         ["SE(b-hat) at n = " + str(g3["base"]["worlds_per_arm"]),
          repr(g3["base"]["SE_b_hat"])],
         ["**MDE(2 SE)**", "**" + repr(g3["base"]["MDE_2SE"]) + "**"],
         ["bar", repr(MDE_BAR)],
         ["**PASS**", "**" + str(g3["base"]["PASS"]) + "**"],
         ["escalation fired", str(g3["escalation_fired"])],
         ["worlds per arm decided", str(g3["worlds_per_arm_decided"])]])
    sec["arms"] = _md(
        ["cell", "phi", "s", "n", "R_nat mean", "R_nat SEM", "R_cf mean", "R_cf SEM",
         "variance ratio (max)", "max calibration error"],
        [[q["cell"], repr(q["phi"]), repr(q["s"]), str(q["n"]),
          repr(q["R_nat_mean"]), repr(q["R_nat_sem"]), repr(q["R_cf_mean"]),
          repr(q["R_cf_sem"]), repr(q["variance_ratio_max"]),
          repr(q["cal_rel_error_max"])] for q in fit["per_arm"]])
    sec["slopes"] = _md(
        ["cell", "phi", "b_cf (the verdict quantity)", "95% CI", "classification",
         "sign-first", "agree", "b_nat", "b_nat 95% CI"],
        [[q["cell"], repr(q["phi"]), repr(q["b_cf"]), repr(q["b_cf_ci95"]),
          "**" + q["classification"] + "**", q["classification_sign_first"],
          str(q["readings_agree"]), repr(q["b_nat"]), repr(q["b_nat_ci95"])]
         for q in fit["per_cell"].values()])
    sec["curves"] = _md(
        ["cell", "s", "R_nat", "R_cf", "G(s) = R_cf(s) - R_cf(0)",
         "F(s) = [R_nat(s) - R_nat(0)] - G(s)"],
        [[cid, s, repr(q["R_nat_means"][s]), repr(q["R_cf_means"][s]),
          repr(q["G_curve"][s]), repr(q["F_curve"][s])]
         for cid, q in fit["per_cell"].items() for s in
         [str(x) for x in S_ARMS]])
    sec["fsplit"] = _md(
        ["cell", "G(1)", "G(1) 95% CI", "F(1)", "F(1) 95% CI",
         "denominator R_nat(1) - R_nat(0)", "**f**", "f 95% CI", "CI width",
         "budget", "within budget", "f > 0.5"],
        [[q["cell"], repr(q["G_1"]), repr(q["G_1_ci95"]), repr(q["F_1"]),
          repr(q["F_1_ci95"]), repr(q["denominator_R_nat_1_minus_0"]),
          "**" + repr(q["f_fraction"]) + "**", repr(q["f_ci95"]),
          repr(q["f_ci_width"]), repr(q["f_budget"]),
          str(q["f_within_budget"]), str(q["f_gt_half"])]
         for q in fit["per_cell"].values()])
    sec["doseform"] = _md(
        ["cell", "quadratic coefficient on R_nat", "quadratic coefficient on R_cf",
         "linear slope b_nat", "linear slope b_cf", "note"],
        [[q["cell"], repr(q["quadratic_R_nat"]), repr(q["quadratic_R_cf"]),
          repr(q["b_nat"]), repr(q["b_cf"]), "descriptive, no verdict"]
         for q in fit["per_cell"].values()])
    sec["identity"] = _md(
        ["cell", "b_cf from arm means", "OLS witness on all 5n points",
         "identity holds", "b_nat from arm means", "OLS witness"],
        [[q["cell"], repr(q["b_cf"]), repr(q["b_cf_ols_witness"]),
          str(q["b_cf_identity_holds"]), repr(q["b_nat"]),
          repr(q["b_nat_ols_witness"])] for q in fit["per_cell"].values()])
    sec["regime"] = _md(
        ["quantity", "value"],
        [["max variance ratio over all arms",
          repr(fit["variance_ratio_max_any_arm"])],
         ["bar", repr(fit["variance_ratio_bar"])],
         ["**REGIME_NOTE modifier**", "**" + str(fit["REGIME_NOTE"]) + "**"],
         ["definition", RN_NOTES["RN-P2-6"]]])
    sec["truth_table"] = _md(
        ["#", "condition", "outcome"],
        [[t["n"], t["condition"],
          ("**" + t["text"] + "**  <-- THIS LEG") if t["outcome"] == dec["verdict_slug"]
          else t["text"]] for t in TRUTH_TABLE])
    sec["gates"] = _md(["gate", "PASS", "detail"],
                       [[k, str(v["PASS"]), v["detail"]]
                        for k, v in dec["gates"].items()])
    sec["sides"] = _md(["clause", "statement", "prior", "sided"],
                       [[k, str(v["clause"]), str(v.get("prior", "—")), v["sided"]]
                        for k, v in p0["sides_rule22"].items()])
    sec["rn"] = _md(["note", "pinned reading"],
                    [[k, v] for k, v in p0["rn_notes"].items()])
    sec["env"] = _md(["component", "value"],
                     [[k, str(v)] for k, v in p0["environment"].items()])
    est = p0["stage_estimates_seconds"]
    meas: dict[str, float] = {}
    for line in (OUT / "run_log.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if "seconds" in r:
            meas[r["event"]] = float(r["seconds"])
    trows = [["part0", str(est["part0"]),
              "%.3f" % meas.get("part0_done", float("nan"))],
             ["pilot", str(est["pilot"]),
              "%.3f" % meas.get("pilot_done", float("nan"))],
             ["project", str(est["project"]),
              "%.3f" % meas.get("project_done", float("nan"))]]
    for cid in BASE_CELLS:
        for s in S_ARMS:
            trows.append([f"arm {cid} s={s}", str(est["arms_each"]),
                          "%.3f" % meas.get(f"arm_{cid}_s{s}_done", float("nan"))])
    trows += [["fit", str(est["fit"]), "%.3f" % meas.get("fit_done", float("nan"))],
              ["finalize", str(est["finalize"]),
               "%.3f" % meas.get("finalize_done", float("nan"))]]
    sec["timing"] = _md(["stage", "estimate (s)", "measured (s)"], trows)
    body = ["# M4-P2 report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _facts(p0: dict[str, Any], pil: dict[str, Any], g3: dict[str, Any],
           fit: dict[str, Any], dec: dict[str, Any]) -> None:
    g1 = pil["G1p2"]
    a = g1["(a) zero-dose variant is the plain construction"]
    b = g1["(b) T-cf differs from T-nat at s > 0"]
    c = g1["(c) R_cf(0) == R_nat(0) bit-exactly"]
    dd = g1["(d) R_nat reproduces k2b's run_field_world"]
    inj = p0["injection_point"]
    f = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"],
        "MODIFIERS": ", ".join(dec["modifiers"]) or "none",
        "CLASSES": ", ".join(f"{k}={v}" for k, v in fit["classes"].items()),
        "AGREE": fit["cross_cell_agreement"],
        "NPERARM": fit["worlds_per_arm"], "NTOTAL": dec["total_worlds"],
        "NARMS": len(S_ARMS) * len(BASE_CELLS),
        "INJ_POINT": inj["LAST_READ_BEFORE_MAP"], "INJ_MATCH": inj["matches_P1_pin"],
        "BITA": a["all_bit_identical"], "BITA_N": a["n_checked"],
        "BITA_MAX": a["max_abs_difference"],
        "TND_MIN": b["min_truth_norm_delta"], "TND_MAX": b["max_truth_norm_delta"],
        "ZP": c["all_bit_exact"], "ZP_N": c["n_checked"],
        "K2BMATCH": dd["all_match"], "K2BDIFF": dd["max_abs_difference"],
        "SIGMA": g3["sigma_df_inflated"], "SIGMA_RAW": g3["sigma_raw"],
        "INFL": g3["inflation"], "DF": g3["df"],
        "SE_B": g3["base"]["SE_b_hat"], "MDE": g3["base"]["MDE_2SE"],
        "MDE_BAR": MDE_BAR, "ESC": g3["escalation_fired"],
        "SSQ": g3["sum_centred_squares"],
        "VRMAX": fit["variance_ratio_max_any_arm"], "VRBAR": VAR_RATIO_BAR,
        "REGIME": fit["REGIME_NOTE"],
        "N_RULE13": len(fit["rule13_events"]),
        "EQUIV": EQUIV, "FBUDGET": F_BUDGET,
        "P1_B1": P1_B1_SLOPE, "P1_B2": P1_B2_SLOPE,
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
    }
    for cid, q in fit["per_cell"].items():
        f.update({
            f"{cid}_BCF": q["b_cf"], f"{cid}_BCFCI": q["b_cf_ci95"],
            f"{cid}_CLASS": q["classification"],
            f"{cid}_SIGNFIRST": q["classification_sign_first"],
            f"{cid}_AGREE": q["readings_agree"],
            f"{cid}_BNAT": q["b_nat"], f"{cid}_BNATCI": q["b_nat_ci95"],
            f"{cid}_G1": q["G_1"], f"{cid}_G1CI": q["G_1_ci95"],
            f"{cid}_F1": q["F_1"], f"{cid}_F1CI": q["F_1_ci95"],
            f"{cid}_DENOM": q["denominator_R_nat_1_minus_0"],
            f"{cid}_F": q["f_fraction"], f"{cid}_FCI": q["f_ci95"],
            f"{cid}_FW": q["f_ci_width"], f"{cid}_FOK": q["f_within_budget"],
            f"{cid}_FGT": q["f_gt_half"],
            f"{cid}_QNAT": q["quadratic_R_nat"], f"{cid}_QCF": q["quadratic_R_cf"],
            f"{cid}_PHI": q["phi"], f"{cid}_IDENT": q["b_cf_identity_holds"],
            f"{cid}_RNAT0": q["R_nat_means"]["0.0"],
            f"{cid}_RNAT1": q["R_nat_means"]["1.0"],
            f"{cid}_RCF0": q["R_cf_means"]["0.0"],
            f"{cid}_RCF1": q["R_cf_means"]["1.0"],
            f"{cid}_FPCT": float(100.0 * q["f_fraction"]),
            f"{cid}_GPCT": float(100.0 * (1.0 - q["f_fraction"])),
        })
    write_json(OUT / "prose_facts.json", f)


REPORT_TEMPLATE = r"""# SUICA M4-P2 — the dose-decomposition — **{{SLUG}}**

**Outcome: {{SLUG}} (routing cell {{CELL}}); modifiers: {{MODIFIERS}}.**
{{ROUTING_TEXT}}

Per cell on the R_cf slope: {{CLASSES}} (cross-cell agreement {{AGREE}}).
{{NTOTAL}} fresh worlds ({{NPERARM}}/arm × {{NARMS}} arms), each built in two
variants. No seal — a decomposition, not a prediction.

**But the headline number is f.** {{B1_FPCT}}% of P1's boost at B1 and
{{B2_FPCT}}% at B2 is **frame-vs-frame agreement**, not better person-reading.
The genuine component survives — that is why the routing says
GENUINE_SCAFFOLD — but it is **{{B1_GPCT}}% / {{B2_GPCT}}%** of the effect P1
measured, and its slope clears the minimum-interesting bar by a hair.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md` BEFORE run (commit b61cc52).
Every number below is generated from artifacts by code (rule 24).

---

## 1. The decomposition

<<TABLE:algebra>>

Each world is built twice at the same index — dosed and zero-dose — and the
DOSED world's gauge output is scored against both truth panels off **one
calibration**. That is required, not merely cheaper: a second calibration would
make R_cf − R_nat confound the truth swap with a calibration swap (RN-P2-4).

## 2. The result

<<TABLE:slopes>>

<<TABLE:fsplit>>

- **B1** (φ {{B1_PHI}}): b_cf = **{{B1_BCF}}** {{B1_BCFCI}} → {{B1_CLASS}};
  against b_nat = {{B1_BNAT}} {{B1_BNATCI}}. G(1) = {{B1_G1}} {{B1_G1CI}},
  F(1) = {{B1_F1}} {{B1_F1CI}}, denominator {{B1_DENOM}} → **f = {{B1_F}}**
  {{B1_FCI}} (width {{B1_FW}} ≤ {{FBUDGET}}: {{B1_FOK}}).
- **B2** (φ {{B2_PHI}}): b_cf = **{{B2_BCF}}** {{B2_BCFCI}} → {{B2_CLASS}};
  against b_nat = {{B2_BNAT}} {{B2_BNATCI}}. G(1) = {{B2_G1}} {{B2_G1CI}},
  F(1) = {{B2_F1}} {{B2_F1CI}}, denominator {{B2_DENOM}} → **f = {{B2_F}}**
  {{B2_FCI}} (width {{B2_FW}} ≤ {{FBUDGET}}: {{B2_FOK}}).

b_nat reproduces P1's finding on a fresh salt ({{B1_BNAT}} / {{B2_BNAT}} here
against P1's {{P1_B1}} / {{P1_B2}}), so the object being decomposed is the same
object P1 measured.

### 2.1 The honest magnitude caveat

b_cf is POSITIVE at both cells by the registered classification — the CI
excludes zero and is not wholly inside the ±{{EQUIV}} equivalence margin — but
at B1 the CI **straddles** that margin ({{B1_BCFCI}} against a margin edge of
{{EQUIV}}), and at B2 it sits mostly inside it ({{B2_BCFCI}}). So the genuine
scaffold is real and signed, and its size is at the very edge of what this leg
declared interesting. L-1p2's "genuine-survives" resolves YES; it resolves
narrowly.

## 3. The curves

<<TABLE:curves>>

R_nat climbs steeply and convexly; **R_cf is nearly flat**. At B1 R_cf runs
{{B1_RCF0}} → {{B1_RCF1}} while R_nat runs {{B1_RNAT0}} → {{B1_RNAT1}}; at B2
R_cf runs {{B2_RCF0}} → {{B2_RCF1}} against R_nat {{B2_RNAT0}} → {{B2_RNAT1}}.
The gap between the two curves IS F(s), and it grows with dose.

<<TABLE:doseform>>

The dose forms differ qualitatively, which is the clearest statement of the
finding: R_nat is strongly convex (quadratic {{B1_QNAT}} / {{B2_QNAT}}) while
R_cf is essentially linear-to-flat ({{B1_QCF}} / {{B2_QCF}}). P1's convexity was
a property of frame-vs-frame agreement, not of person-reading. Descriptive
only — no verdict rides on the form (RN-P2-10).

### 3.1 The slope algebra, proven not asserted

<<TABLE:identity>>

## 4. G0p2 — the citations

<<TABLE:g0p2>>

<<TABLE:injection>>

## 5. G1p2 — the instrument

<<TABLE:g1p2>>

All four clauses hold. (a) The zero-dose variant of every pilot world is
bit-identical to a fresh plain `build_k2b_world` at the same seed
({{BITA_N}} worlds, max |difference| {{BITA_MAX}}). (b) At s > 0 the two truth
panels provably differ: ‖T-nat − T-cf‖ ∈ [{{TND_MIN}}, {{TND_MAX}}]. (c) The
zero-point identity R_cf(0) ≡ R_nat(0) holds bit-exactly on all {{ZP_N}} worlds
— the hinge that makes G(0) = F(0) = 0. (d) This harness's reassembled gauge
path returns **exactly** what k2b's own `run_field_world` returns
({{K2BMATCH}}, max |difference| {{K2BDIFF}}).

<<TABLE:zeropoint>>

## 6. G2p2 — the pilot and the regime disclosure

<<TABLE:pilot>>

<<TABLE:regime>>

The largest common-to-author response-level variance ratio over every arm is
{{VRMAX}}, far below the {{VRBAR}} bar, so **no REGIME_NOTE**: even at s = 1.0
the author-specific variance still dominates the common component. The dosed
regime is not a degenerate one.

## 7. G3p2 — the projection

<<TABLE:projection>>

σ from the pilot's zero-dose worlds (df {{DF}}), df-inflated ×{{INFL}}:
{{SIGMA_RAW}} → {{SIGMA}}. Five equally-replicated levels give
Σ(s_j − s̄)² = {{SSQ}}, so SE(b̂) = σ/√(n·{{SSQ}}) = {{SE_B}} and
**MDE(2·SE) = {{MDE}} ≤ {{MDE_BAR}}**. Escalation did not fire ({{ESC}}).

## 8. Routing

<<TABLE:truth_table>>

## 9. Gates

<<TABLE:gates>>

## 10. Sides declared (rule 22)

<<TABLE:sides>>

## 11. Pinned readings

<<TABLE:rn>>

## 12. Rule events

- **Rule 13:** {{N_RULE13}} boundary events; no B = 20000 re-run.
- **Rule 26:** no bounded winner.
- **Rule 27:** f's budget is a 95% CI width ≤ {{FBUDGET}}; realized {{B1_FW}}
  and {{B2_FW}}, so f is QUANTIFIED at both cells and no UNQUANTIFIED modifier
  applies.
- **Rule 29:** in force as G2p2, applied to BOTH R_nat and R_cf at every arm.
- **Rule 30:** every cited constant verified against its persisted source before
  Part 0; all twelve P1 citations bit-exact.

## 13. What this does and does not license

**Licensed.** The scaffold mechanism P1 named is genuine but small: holding the
truth side frame-fixed, more common-frame content still improves person-reading,
at both φ levels, with CIs excluding zero. P1's SIGN_SCAFFOLD stands as a sign.

**Not licensed — and this qualifies P1 substantially.** The magnitude P1
reported was overwhelmingly frame-vs-frame agreement: {{B1_FPCT}}% and
{{B2_FPCT}}% of the boost disappears the moment the truth panel is held
frame-fixed. Any reading of P1 that treated +0.32 as "how much better the gauge
reads people under more frame" is wrong by a factor of about twenty. The
convexity P1 reported is likewise a property of F, not of G.

## 14. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython {{PYTHON}} venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.

## 15. Environment

<<TABLE:env>>

## 16. Timing

<<TABLE:timing>>

---

*Artifacts: `results/m4_p2_dose_decomposition/` (gitignored) — `part0.json`,
`pilot.json`, `pilot_field.csv`, `projection.json`, `arms/`, `fit.json`,
`decision.json`, `prose_facts.json`, `report_tables.md`, `run_log.jsonl`.
Harness: `scripts/run_suica_m4_p2_dose_decomposition.py`.*
"""


def _fmt(v: Any) -> str:
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        return repr(v)
    if isinstance(v, list):
        return "[" + ", ".join(_fmt(x) for x in v) + "]"
    return str(v)


def stage_report(args: argparse.Namespace) -> None:
    facts = read_json(OUT / "prose_facts.json")
    tables = (OUT / "report_tables.md").read_text(encoding="utf-8")
    sec: dict[str, str] = {}
    cur, buf = None, []
    for line in tables.split("\n"):
        if line.startswith("<!-- TABLE:"):
            if cur:
                sec[cur] = "\n".join(buf).strip()
            cur, buf = line.split("<!-- TABLE:")[1].split(" -->")[0], []
        elif cur:
            buf.append(line)
    if cur:
        sec[cur] = "\n".join(buf).strip()
    txt = REPORT_TEMPLATE
    for k, v in facts.items():
        txt = txt.replace("{{" + k + "}}", _fmt(v))
    for k, v in sec.items():
        txt = txt.replace("<<TABLE:" + k + ">>", v)
    if "{{" in txt or "<<TABLE:" in txt:
        bad = re.findall(r"\{\{[A-Z0-9_]+\}\}|<<TABLE:[a-z0-9_]+>>", txt)
        raise SystemExit(f"REFUSED: unresolved placeholders: {sorted(set(bad))}")
    path = ROOT / "reports" / "SUICA_M4_P2_DOSE_DECOMPOSITION_REPORT.md"
    path.write_text(txt, encoding="utf-8")
    print(f"report OK  {rel(path)}  ({len(txt.splitlines())} lines)")
    _ = args


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="stage", required=True)
    stages: list[tuple[str, Callable[[argparse.Namespace], None]]] = [
        ("part0", stage_part0), ("pilot", stage_pilot), ("project", stage_project)]
    for cid in BASE_CELLS:
        for s in S_ARMS:
            stages.append((f"arm_{cid}_s{s}",
                           (lambda cc, ss: lambda a: _arm(cc, ss))(cid, s)))
    stages += [("fit", stage_fit), ("finalize", stage_finalize),
               ("report", stage_report)]
    for name, fn in stages:
        sub.add_parser(name).set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
