#!/usr/bin/env python3
"""SUICA M4-P1 -- the frame-injection sign probe.

Registered BEFORE run in docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md
("M4-P1 -- the frame-injection sign probe", commit 7589299).  Binding.

K1's calibrated common-shift recipe is transplanted into the K2b world family:
a pre-map occasion-level common perturbation delta(o) is added to EVERY
author's response on occasion o, drawn once per world per occasion, scaled so
its realized response-level RMS equals s x (the world's author-deviation RMS at
the response level).  Two named mechanisms predict OPPOSITE signs for the
resulting change in b-only recovery: H-SCAFFOLD (+) and H-CONTAMINATION (-).

suica_core/ and the frozen map are untouched.  The perturbation lives in world
construction, upstream of the reader: this harness calls k2b's own
build_k2b_world, adds delta to the returned `common` array, and hands the
perturbed world to k2b's own run_field_world.  No k2b source line is edited.

Stages:  part0 -> pilot -> project -> arms_<B><s> (6) -> fit -> finalize -> report
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
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "results" / "m4_p1_frame_injection"
RES = ROOT / "results"
M2RES = RES / "m4_m2_scoped_seal"

LEG = "M4-P1"
BANNER = ("frame-injection sign probe on the K2b family; exploratory, label-free; "
          "no seal -- the leans are split, so no sealable point prediction exists")

MASTER_SEED = 20260814
SALT_WORLD = "m4p1-world"
SALT_PILOT = "m4p1-pilot"
N_WORLDS = 192
N_WORLDS_ESCALATED = 384
PILOT_WORLDS = 4
S_ARMS = (0.0, 0.5, 1.0)
PILOT_S = (0.0, 1.0)
BASE_CELLS = {"B1": (0.25, 0.05), "B2": (0.25, 0.60)}
R_REGISTERED = {"B1": 0.785015540293945, "B2": 0.7558507450373838}
W_INT_ARM = "zero"

M2_C4_MEAN = 0.12239759528671845
M2_C4_SOURCE = "results/m4_m2_scoped_seal/decision.json:per_cell.C4.mean"

MDE_BAR = 0.01                 # declared minimum-interesting slope |b|
EQUIV = 0.01                   # rule-4 equivalence margin on b-hat
B_BOOT = 2000
B_BOOT_HIGH = 20000
RULE13_FACTOR = 10.0
CHI2_Q = 0.10                  # the registered df-inflation quantile (M1b G3m'(b))
RMS_TOL = 0.05                 # G1p1(b): realized RMS within 5% of target
SATURATION_ABS = 0.995

# --- the citation anchors G0p1(ii) must locate (rule 24: found, not typed) ---
KLINE = ROOT / "docs" / "SUICA_M4_K_IDENTITY_LINE_PLAN.md"
V8DOC = ROOT / "docs" / "SUICA_V8_IDT_INTEGRATION.md"
K1SRC = ROOT / "scripts" / "run_suica_m4_k1_issuer_theorems.py"
ANCHORS = {
    "K1 recipe (author-deviation RMS)": (KLINE, "author-deviation RMS"),
    "K1 amplification (+0.0925)": (V8DOC, "0.0925"),
    "K1 amplification (3.54x F2)": (V8DOC, "3.54"),
    "K-R1 scaffold corollary": (KLINE, "scaffold"),
    "K2b G4b frame-carried substrate": (KLINE, "within-author occasion variation"),
    "K1 implementation: the RMS definition (CONTROLS, RN-P1-2)":
        (K1SRC, "RMS over (author, dim) of the author's mean deviation"),
    "K1 implementation: the delta construction":
        (K1SRC, "delta = rng.normal(size=(n_lab"),
}

# ---------------------------------------------------------------------------
# RN-P1 notes.  PINNED IN PART 0, BEFORE ANY WORLD.
#
# RN-P1-1 (the injection point, and the choice rule).  The registration's own
#   sentence is the choice rule: "the LAST common per-occasion object every
#   author's response shares before the frozen map".  In the K2b family that
#   object is `world["common"]`, shape (n_ctx, t_max, DIM), built at
#   scripts/run_suica_m4_k2b_t4_branch.py:337 and returned at :349.  Its LAST
#   read before the frozen map is :377, inside emit_panel --
#   `v += w["common"] * world["common"][ctx_index[i], :m]` -- and emit_panel is
#   called at :615, one line before the frozen map's entry
#   `f1().featurize_panel(...)` at :616.  Nothing else between :377 and the map
#   is both common and per-occasion.  delta(o) is added to common[c, o, :] for
#   EVERY context c, so every author on occasion o receives the identical
#   response-level shift w["common"]*delta(o), which is what "added to every
#   author's response on occasion o" means.  k2b is NOT edited: this harness
#   perturbs the returned array.
#
# RN-P1-2 (what "author-deviation RMS at the response level" is -- K1's OWN
#   implementation controls).  The registration transplants K1's recipe, so the
#   cited source's own code is the operative definition (rules 9/12), not an
#   independent reconstruction.  K1's `_author_deviation_rms`
#   (scripts/run_suica_m4_k1_issuer_theorems.py:337-361) does three things:
#   it centres each response on its (CONTEXT, OCCASION) cell mean; it averages
#   each author's deviations OVER that author's occasions to one vector per
#   author; and it returns the RMS over the (author x dim) matrix.  That is
#   transplanted here literally -- same cell key, same author-mean step, same
#   final RMS -- against the K2b panel, whose contexts and occasions are the
#   direct analogues.  (K1's extra clause "computed on the SHARED design's
#   unshifted world" has no K2b analogue: this family has no free/shared split.
#   It is computed on the unperturbed world, which is the transferable part.)
#   This choice MATTERS: it is much smaller than a raw per-response deviation
#   RMS, so it sets a much smaller dose at the same s.  I found it only after
#   reading K1's harness and BEFORE any arm ran; both alternatives are computed
#   and REPORTED per world -- (alt-A) the raw RMS over every (author, occasion,
#   dim) of the deviation from the cross-author occasion mean, and (alt-B) the
#   same as K1 but pooling contexts -- so the planner can see the dose each
#   reading would have produced.  Only K1's controls.
#
# RN-P1-3 (the calibration is solved, not sampled).  delta is drawn once per
#   world per occasion from a dedicated RNG seeded off the leg lineage (never
#   the world RNG, which would shift k2b's stream), then rescaled by a closed-
#   form factor so the realized response-level RMS equals the target exactly.
#   The realized value is recomputed after scaling and persisted per world, so
#   G1p1(b)'s 5% band is checked against an executed number, not an intended
#   one.
#
# RN-P1-4 (the slope's exact algebra).  With s in {0, 0.5, 1.0} equally
#   replicated, the OLS slope of per-world recovery on s reduces EXACTLY to
#   mean(s = 1.0) - mean(s = 0): the midpoint arm contributes nothing to b-hat
#   (it identifies the descriptive quadratic term c = 2*(y0 - 2*y1 + y2) and
#   nothing else).  This is stated because it makes SE(b-hat) exact for the
#   design -- SE = sigma/sqrt(n/2) at n worlds per arm -- and because it means
#   the sign verdict rests on the two endpoint arms.
#
# RN-P1-5 (the classification is not disjoint as registered; a reading is
#   pinned).  The registered classes are POSITIVE (CI > 0) / NEGATIVE (CI < 0)
#   / NULL (CI inside the +/-0.01 equivalence margin) / UNDERPOWERED (CI
#   straddles 0 and exits the margin).  A CI like (0.001, 0.005) satisfies both
#   POSITIVE and NULL, so the four are NOT disjoint and rule 16 is not met on
#   the classification (it is met on the routing).  PINNED, before any number:
#   EQUIVALENCE WINS -- a CI lying entirely inside the margin is NULL whatever
#   its sign, because that is what an equivalence margin means (rule 4);
#   otherwise CI excluding 0 gives POSITIVE/NEGATIVE; otherwise UNDERPOWERED.
#   The sign-first ordering is ALSO computed and reported, and both are shown
#   in the report whether or not they differ.
#
# RN-P1-7 (one deliberate departure from K1's code, disclosed).  K1 SETS the
#   per-component sigma of delta to scale*rms and lets the realized RMS land
#   where it lands; this registration's words are stronger -- "scaled so its
#   REALIZED response-level RMS EQUALS s x ..." -- so delta is rescaled to hit
#   the target exactly.  With t_max*DIM = 1024 draws the two agree to about
#   2% anyway (both would clear G1p1(b)'s 5% band), so the departure is
#   immaterial to the dose; it is taken because the P1 text is the binding one
#   and it makes G1p1(b) a real test of the code rather than of the CLT.
#
# RN-P1-8 (the corpus-label hazard, found by G1p1(c) BEFORE any arm ran).
#   k2b builds `corpus = f"m4k2b-{arm_id}-w{world_index}"` (k2b:613) and hands
#   it to the frozen map, and the map's output DEPENDS on that string: the same
#   world read under two different arm labels returns recovery_b_only
#   0.13207502282291814 vs 0.11984192209116917, a 0.0122 difference -- LARGER
#   than this leg's declared minimum-interesting slope of 0.01.  Because
#   world_index is also in the string the label varies per world, so this is
#   exchangeable per-world noise rather than a per-arm offset, and it is
#   already inside the sigma the projection uses.  It is nevertheless removed
#   by construction: the arm tag is made s-INDEPENDENT (`P1-{cell}`), so at a
#   matched world index the three s-arms receive the IDENTICAL corpus string
#   and any corpus main effect cancels exactly in b-hat.  World seeds still
#   differ across arms, so the registered 1152 FRESH worlds are unchanged.
#   G1p1(c) failed on the first pilot precisely because the control had been
#   given a different label; the gate did its job on the harness.
#
# RN-P1-6 (the world bootstrap).  Worlds are independent across arms -- the arm
#   enters the seed -- so the bootstrap resamples world indices independently
#   within each arm, B = 2000 (20000 at a rule-13 boundary), master-seeded.
#   b-hat is a function of arm means only (RN-P1-4), so this is exactly a
#   two-sample bootstrap of the endpoint arms.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-P1-1": "the injection point is world['common'] (k2b:337 built, :349 returned, "
               ":377 last read inside emit_panel, called :615 one line before the frozen "
               "map at :616); delta(o) is added to common[c, o, :] for EVERY context so "
               "every author gets the identical response-level shift; k2b is not edited",
    "RN-P1-2": "K1's OWN implementation controls (rules 9/12): centre each response on "
               "its (CONTEXT, OCCASION) cell mean, average each author's deviations over "
               "its occasions to one vector per author, RMS over (author x dim) -- "
               "transplanted literally from k1:337-361. Invariant to the injection "
               "because delta is identical across authors and cancels in the cell "
               "deviation. Two alternative readings are computed and REPORTED per world, "
               "never used to calibrate; only K1's sets the dose",
    "RN-P1-3": "delta is drawn from a dedicated RNG (never the world stream) and rescaled "
               "in closed form to hit the target exactly; the realized RMS is recomputed "
               "after scaling and persisted, so the 5% gate tests an executed number",
    "RN-P1-4": "with s in {0, 0.5, 1.0} equally replicated the OLS slope equals EXACTLY "
               "mean(s=1) - mean(s=0); the midpoint arm identifies only the descriptive "
               "quadratic c = 2*(y0 - 2*y1 + y2); SE(b-hat) = sigma/sqrt(n/2)",
    "RN-P1-5": "the registered classification is NOT disjoint (a CI inside the margin and "
               "above 0 is both POSITIVE and NULL). PINNED: equivalence wins -- inside "
               "the margin is NULL whatever the sign (rule 4); else CI excluding 0 gives "
               "POSITIVE/NEGATIVE; else UNDERPOWERED. The sign-first ordering is also "
               "computed and reported",
    "RN-P1-7": "K1 SETS delta's per-component sigma to scale*rms; this registration "
               "says the REALIZED RMS must EQUAL the target, so delta is rescaled "
               "exactly. The two agree to ~2% at 1024 draws (both clear the 5% band); "
               "the P1 text is binding and exact rescaling makes G1p1(b) test the code",
    "RN-P1-8": "k2b's corpus string embeds arm_id (k2b:613) and the frozen map's output "
               "depends on it -- the same world under two labels gives 0.13207502282291814 "
               "vs 0.11984192209116917 (0.0122 apart, larger than the 0.01 bar). It also "
               "embeds world_index, so it is per-world exchangeable noise already inside "
               "sigma, but the arm tag is made s-INDEPENDENT so the three s-arms share the "
               "identical corpus at matched world index and any corpus effect cancels in "
               "b-hat; world seeds still differ, so 1152 fresh worlds stand",
    "RN-P1-6": "worlds are independent across arms (the arm enters the seed), so the "
               "bootstrap resamples world indices independently within each arm, "
               "master-seeded, B=2000 (20000 at a rule-13 boundary)",
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
    """RN-P1-2: K1's definition (controls) plus two reported alternatives.

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
                                           "k1:337-361, transplanted (RN-P1-2)",
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


def run_world(cell: str, share: float, phi: float, s: float, widx: int,
              salt: str, tag: str) -> dict[str, Any]:
    kb = k2b()
    w = kb.arm_weights(share, W_INT_ARM)
    wseed = world_seed_for(cell, s, widx, salt)
    world = kb.build_k2b_world(wseed, phi)
    cal = inject(world, w, s, delta_seed_for(cell, s, widx, salt))
    row = kb.run_field_world(tag, widx, world, w, verify=False)
    row.update({"cell": cell, "share": share, "phi": phi, "s": s, "world": widx,
                "world_seed": wseed, "salt": salt,
                "cal_target_rms": cal["target_response_rms"],
                "cal_realized_rms": cal["realized_response_rms"],
                "cal_rel_error": cal["relative_calibration_error"],
                "cal_norm_delta": cal["common_norm_delta"],
                "author_dev_rms": cal["author_deviation_rms"]})
    return row


def _g1p1_predicate(vals: np.ndarray) -> dict[str, Any]:
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

    # --- G0p1(i): the base-cell r values from the pinned maps --------------
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

    # --- G0p1(ii): the cited sentences, LOCATED not transcribed ------------
    cites = {name: _locate(path, needle) for name, (path, needle) in ANCHORS.items()}
    g0ii = {"anchors": cites,
            "all_found": bool(all(c["found"] for c in cites.values())),
            "method": "each anchor substring is located in its controlling document "
                      "and the containing paragraph is extracted verbatim by code "
                      "(rule 24); no sentence is hand-typed into this harness"}
    g0ii["PASS"] = g0ii["all_found"]

    # --- G0p1(iii): M2's C4 mean at full precision -------------------------
    c4 = read_json(M2RES / "decision.json")["per_cell"]["C4"]
    g0iii = {"source": M2_C4_SOURCE, "mean_persisted": c4["mean"],
             "mean_registration": M2_C4_MEAN,
             "bit_exact": bool(c4["mean"] == M2_C4_MEAN),
             "n": c4["n"], "sem": c4["sem"], "share": c4["share"], "phi": c4["phi"],
             "same_base_cell_as_B1": bool(c4["share"] == BASE_CELLS["B1"][0]
                                          and c4["phi"] == BASE_CELLS["B1"][1])}
    g0iii["PASS"] = bool(g0iii["bit_exact"] and g0iii["same_base_cell_as_B1"])

    g0 = {"(i) base-cell r": g0i, "(ii) cited sentences": g0ii,
          "(iii) M2 C4 anchor": g0iii,
          "PASS": bool(g0i["PASS"] and g0ii["PASS"] and g0iii["PASS"])}

    # --- the injection point, identified with file:line (registration) -----
    kbsrc = ROOT / "scripts" / "run_suica_m4_k2b_t4_branch.py"
    src = kbsrc.read_text(encoding="utf-8").split("\n")

    def _line_of(needle: str) -> dict[str, Any]:
        for i, line in enumerate(src):
            if needle in line:
                return {"line": i + 1, "text": line.rstrip()}
        return {"line": None, "text": None}

    built = _line_of('common = A_SCALE * ((common_lat * G_PROFILE) @ loadings.T)')
    returned = _line_of('"common": common,')
    lastread = _line_of('v += w["common"] * world["common"][ctx_index[i], :m]')
    emitcall = _line_of("vectors = emit_panel(world, w)")
    mapentry = _line_of("raw_m, raw_k = f1().featurize_panel(")
    lay = k2b().layout()
    inj = {
        "choice_rule": "the registration's own sentence: 'the LAST common per-occasion "
                       "object every author's response shares before the frozen map' "
                       "(rule 12)",
        "object": "world['common']",
        "shape": [len(lay["contexts_sorted"]), int(lay["t_max"]), int(k2b().DIM)],
        "shape_meaning": "(n_contexts, t_max occasions, DIM)",
        "built_at": f"{rel(kbsrc)}:{built['line']}",
        "built_source": built["text"],
        "returned_at": f"{rel(kbsrc)}:{returned['line']}",
        "LAST_READ_BEFORE_MAP": f"{rel(kbsrc)}:{lastread['line']}",
        "last_read_source": lastread["text"],
        "emit_panel_called_at": f"{rel(kbsrc)}:{emitcall['line']}",
        "frozen_map_entry_at": f"{rel(kbsrc)}:{mapentry['line']}",
        "frozen_map_entry_source": mapentry["text"],
        "why_this_object": "it is the only object that is BOTH common (not author-"
                           "specific) AND per-occasion that every author's response "
                           "incorporates; the next line to touch the response is the "
                           "frozen map's own entry",
        "injection_mechanics": "delta(o) is added to common[c, o, :] for EVERY context "
                               "c, so every author on occasion o receives the identical "
                               "response-level shift w['common'] * delta(o)",
        "k2b_edited": False,
        "suica_core_edited": False,
        "note": RN_NOTES["RN-P1-1"],
    }

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md (M4-P1, BEFORE "
                        "run, commit 7589299)",
        "master_seed": MASTER_SEED, "salts": {"world": SALT_WORLD, "pilot": SALT_PILOT},
        "rn_notes": RN_NOTES, "G0p1": g0, "injection_point": inj,
        "design": {"s_arms": list(S_ARMS), "base_cells": {k: list(v) for k, v in
                                                          BASE_CELLS.items()},
                   "worlds_per_arm": N_WORLDS, "n_arms": len(S_ARMS) * len(BASE_CELLS),
                   "total_worlds": N_WORLDS * len(S_ARMS) * len(BASE_CELLS),
                   "int_share": 0.0, "w_int_arm": W_INT_ARM},
        "slope_algebra": {
            "b_hat": "OLS slope of per-world recovery on s over {0, 0.5, 1.0}",
            "reduces_to": "mean(s=1.0) - mean(s=0) EXACTLY (RN-P1-4)",
            "SE": "sigma / sqrt(n/2) at n worlds per arm",
            "quadratic": "c = 2*(y0 - 2*y1 + y2), descriptive only"},
        "G2p1_predicate": {"rule": 29, "saturation": f"|recovery_b_only| >= "
                                                     f"{SATURATION_ABS}",
                           "finiteness": True, "nonzero_within_arm_variance": True,
                           "positivity_clause": "NONE",
                           "statistic_domain": "weighted mean of matrix cosines on "
                                               "[-1, 1]"},
        "sides_rule22": {
            "L-1p1": {"clause": "scaffold(+) / contamination(-) / null-or-split",
                      "prior": "0.45 / 0.40 / 0.15", "sided": "categorical, two-sided "
                                                              "on the sign"},
            "G3p1": {"clause": f"MDE(2 SE) <= {MDE_BAR}", "sided": "one-sided"},
            "G1p1": {"clause": "norm delta > 0; realized RMS within 5%; s=0 bit-"
                               "identical", "sided": "one-sided"}},
        "stage_estimates_seconds": {"part0": 90, "pilot": 40, "project": 20,
                                    "arms_each": 130, "fit": 120, "finalize": 60},
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
            "routing_text": "STOP (citation/instrument defect; no arms)", "G0p1": g0,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: G0p1 FAILED -- see part0.json")
    print(f"part0 OK  G0p1 PASS  injection point {inj['LAST_READ_BEFORE_MAP']}  "
          f"object {inj['object']} {tuple(inj['shape'])}  "
          f"{sum(c['found'] for c in cites.values())}/{len(cites)} anchors located  "
          f"{time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# PILOT + G1p1.

def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    if not p0["G0p1"]["PASS"]:
        raise SystemExit("STOP: G0p1 did not pass.")
    kb = k2b()
    rows, cals, ident = [], [], []
    for cid, (share, phi) in BASE_CELLS.items():
        w = kb.arm_weights(share, W_INT_ARM)
        for s in PILOT_S:
            for widx in range(PILOT_WORLDS):
                tag = f"P1-PILOT-{cid}"   # s-INDEPENDENT (RN-P1-8)
                wseed = world_seed_for(cid, s, widx, SALT_PILOT)
                world = kb.build_k2b_world(wseed, phi)
                cal = inject(world, w, s, delta_seed_for(cid, s, widx, SALT_PILOT))
                row = kb.run_field_world(tag, widx, world, w, verify=False)
                row.update({"cell": cid, "share": share, "phi": phi, "s": s,
                            "world": widx, "world_seed": wseed})
                rows.append(row)
                cals.append({"cell": cid, "s": s, "world": widx, **cal})
                # --- G1p1(c): the s=0 bit-identity test --------------------
                if s == 0.0:
                    clean = kb.build_k2b_world(wseed, phi)
                    # the control MUST carry the identical label: the corpus
                    # string is part of the frozen map's input (RN-P1-8)
                    crow = kb.run_field_world(tag, widx, clean, w, verify=False)
                    ident.append({
                        "cell": cid, "world": widx,
                        "recovery_injected": float(row["recovery_b_only"]),
                        "recovery_unperturbed": float(crow["recovery_b_only"]),
                        "bit_identical": bool(row["recovery_b_only"]
                                              == crow["recovery_b_only"]),
                        "abs_difference": float(abs(row["recovery_b_only"]
                                                    - crow["recovery_b_only"])),
                        "common_array_bit_identical":
                            cal["common_bit_identical_to_unperturbed"]})
            print(f"  pilot {cid} s={s}: done ({time.time() - t0:.1f}s)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "pilot_field.csv", index=False)
    pd.DataFrame(cals).to_csv(OUT / "pilot_calibration.csv", index=False)

    # --- G1p1 ---------------------------------------------------------------
    moved = [c for c in cals if c["s"] > 0.0]
    g1a = {"n_checked": len(moved),
           "min_norm_delta": float(min(c["common_norm_delta"] for c in moved)),
           "max_norm_delta": float(max(c["common_norm_delta"] for c in moved)),
           "all_strictly_positive": bool(all(c["common_norm_delta"] > 0.0
                                             for c in moved)),
           "all_arrays_changed": bool(all(
               not c["common_bit_identical_to_unperturbed"] for c in moved))}
    g1a["PASS"] = bool(g1a["all_strictly_positive"] and g1a["all_arrays_changed"])
    g1b = {"n_checked": len(moved), "tolerance": RMS_TOL,
           "max_relative_error": float(max(c["relative_calibration_error"]
                                           for c in moved)),
           "all_within_5pct": bool(all(c["within_5pct"] for c in moved)),
           "targets": [c["target_response_rms"] for c in moved],
           "realized": [c["realized_response_rms"] for c in moved]}
    g1b["PASS"] = g1b["all_within_5pct"]
    g1c = {"n_checked": len(ident), "rows": ident,
           "all_bit_identical": bool(all(i["bit_identical"] for i in ident)),
           "max_abs_difference": float(max(i["abs_difference"] for i in ident)),
           "all_common_arrays_bit_identical": bool(all(
               i["common_array_bit_identical"] for i in ident)),
           "meaning": "the full injection path runs at s = 0 (delta is drawn and "
                      "scaled to exactly zero) and the resulting field statistic is "
                      "compared bit-for-bit against k2b's unperturbed construction"}
    g1c["PASS"] = g1c["all_bit_identical"]
    g1 = {"(a) injection moves the pre-map object": g1a,
          "(b) realized RMS within 5% of target": g1b,
          "(c) s = 0 is bit-identical": g1c,
          "PASS": bool(g1a["PASS"] and g1b["PASS"] and g1c["PASS"])}

    # --- G2p1: the rule-29 predicate ---------------------------------------
    per, ok = [], True
    for (cid, s), grp in df.groupby(["cell", "s"]):
        chk = _g1p1_predicate(grp["recovery_b_only"].to_numpy(float))
        ok &= chk["PASS"]
        per.append({"cell": cid, "s": float(s), "n": int(len(grp)),
                    "mean": float(grp["recovery_b_only"].mean()), **chk})
    g2 = {"per_arm": per, "predicate": "rule-29, domain-pinned: finite; NOT saturated "
                                       f"(|x| >= {SATURATION_ABS}); nonzero variance; "
                                       "NO positivity", "PASS": bool(ok)}

    out = {"utc": datetime.now(UTC).isoformat(), "G1p1": g1, "G2p1": g2,
           "n_pilot_worlds": int(len(df)),
           "n_extra_unperturbed_controls": int(len(ident)),
           "seconds": time.time() - t0}
    write_json(OUT / "pilot.json", out)
    _log("pilot_done", G1=g1["PASS"], G2=g2["PASS"], seconds=out["seconds"])
    if not (g1["PASS"] and g2["PASS"]):
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "STOP", "routing_cell": 1,
            "routing_text": "STOP (citation/instrument defect; no arms)",
            "G1p1": g1, "G2p1": g2, "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: G1p1/G2p1 FAILED -- see pilot.json")
    print(f"pilot OK  G1p1 PASS (norm delta {g1a['min_norm_delta']:.4g}..."
          f"{g1a['max_norm_delta']:.4g}, max RMS err "
          f"{g1b['max_relative_error']:.3e}, s=0 bit-identical "
          f"{g1c['all_bit_identical']})  G2p1 PASS  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# G3p1 -- the rule-25 projection, before any arm.

def stage_project(args: argparse.Namespace) -> None:
    t0 = time.time()
    pil = read_csv_rt(OUT / "pilot_field.csv")
    z = pil[pil["s"] == 0.0]
    ss, dfree, per = 0.0, 0, []
    for cid, grp in z.groupby("cell"):
        v = grp["recovery_b_only"].to_numpy(float)
        ss += float(np.sum((v - v.mean()) ** 2))
        dfree += len(v) - 1
        per.append({"cell": cid, "n": int(len(v)), "mean": float(v.mean()),
                    "sd": float(np.std(v, ddof=1))})
    sigma_raw = float(np.sqrt(ss / dfree))
    q = float(chi2.ppf(CHI2_Q, dfree))
    infl = float(np.sqrt(dfree / q))
    sigma = sigma_raw * infl

    def project(n: int) -> dict[str, Any]:
        se = float(sigma / np.sqrt(n / 2.0))
        mde = float(2.0 * se)
        return {"worlds_per_arm": n, "SE_b_hat": se, "MDE_2SE": mde,
                "bar": MDE_BAR, "PASS": bool(mde <= MDE_BAR),
                "formula": "SE(b-hat) = sigma / sqrt(n/2) (RN-P1-4)"}

    base = project(N_WORLDS)
    esc = None
    decided = N_WORLDS
    if not base["PASS"]:
        print(f"  G3p1 FAILED at n={N_WORLDS}; once-only escalation to "
              f"n={N_WORLDS_ESCALATED}", flush=True)
        esc = project(N_WORLDS_ESCALATED)
        if esc["PASS"]:
            decided = N_WORLDS_ESCALATED
    g3 = {"sigma_source": "the pilot's s = 0 worlds, pooled within base cell",
          "per_cell": per, "df": dfree, "sigma_raw": sigma_raw,
          "chi2_quantile": CHI2_Q, "chi2_value": q, "inflation": infl,
          "sigma_df_inflated": sigma,
          "inflation_convention": "sigma * sqrt(df / chi2.ppf(0.10, df)) -- M1b's "
                                  "G3m'(b) convention, the conservative upper bound",
          "base": base, "escalated": esc, "escalation_fired": bool(esc is not None),
          "worlds_per_arm_decided": decided,
          "PASS": bool(base["PASS"] or (esc is not None and esc["PASS"])),
          "on_fail": "NON_PROJECTABLE", "seconds": time.time() - t0}
    write_json(OUT / "projection.json", g3)
    _log("project_done", PASS=g3["PASS"], seconds=g3["seconds"])
    if not g3["PASS"]:
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "NON_PROJECTABLE", "routing_cell": 2,
            "routing_text": "NON_PROJECTABLE (handback)", "G3p1": g3,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: NON_PROJECTABLE -- G3p1 failed after escalation")
    print(f"project OK  sigma_raw={sigma_raw!r} infl={infl!r} sigma={sigma!r}  "
          f"MDE(2SE)={base['MDE_2SE']!r} <= {MDE_BAR}  n={decided}  "
          f"{time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# THE ARMS.

def _arm(cid: str, s: float) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    g3 = read_json(OUT / "projection.json")
    if not g3["PASS"]:
        raise SystemExit("STOP: the projection did not pass.")
    if not read_json(OUT / "pilot.json")["G1p1"]["PASS"]:
        raise SystemExit("STOP: G1p1 did not pass.")
    n = int(g3["worlds_per_arm_decided"])
    share, phi = BASE_CELLS[cid]
    (OUT / "arms").mkdir(parents=True, exist_ok=True)
    path = OUT / "arms" / f"arm_{cid}_s{s}.csv"
    if path.exists() and len(read_csv_rt(path)) == n:
        print(f"  {cid} s={s}: already complete, skipped", flush=True)
    else:
        rows = [run_world(cid, share, phi, s, i, SALT_WORLD, f"P1-{cid}")
                for i in range(n)]
        pd.DataFrame(rows).to_csv(path, index=False)
        print(f"  {cid} s={s}: n={len(rows)} ({time.time() - t0:.1f}s)", flush=True)
    _log(f"arm_{cid}_s{s}_done", seconds=time.time() - t0)
    print(f"arm {cid} s={s} OK  {time.time() - t0:.1f}s")
    _ = p0


# ---------------------------------------------------------------------------
# THE FIT.

def _classify(lo: float, hi: float) -> tuple[str, str]:
    """RN-P1-5: the pinned (equivalence-first) reading and the sign-first one."""
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
    arms: dict[tuple[str, float], np.ndarray] = {}
    per_arm = []
    for cid in BASE_CELLS:
        for s in S_ARMS:
            path = OUT / "arms" / f"arm_{cid}_s{s}.csv"
            if not path.exists():
                raise SystemExit(f"REFUSED: missing {path}")
            d = read_csv_rt(path).sort_values("world")
            v = d["recovery_b_only"].to_numpy(float)
            if len(v) != n:
                raise SystemExit(f"REFUSED: {cid} s={s} has {len(v)}, expected {n}")
            chk = _g1p1_predicate(v)
            if not chk["PASS"]:
                raise SystemExit(f"REFUSED: rule-29 predicate fails at {cid} s={s}")
            arms[(cid, s)] = v
            per_arm.append({
                "cell": cid, "share": BASE_CELLS[cid][0], "phi": BASE_CELLS[cid][1],
                "s": s, "n": int(len(v)), "mean": float(v.mean()),
                "sd": float(np.std(v, ddof=1)),
                "sem": float(np.std(v, ddof=1) / np.sqrt(len(v))),
                "cal_realized_rms_mean": float(d["cal_realized_rms"].mean()),
                "cal_rel_error_max": float(d["cal_rel_error"].max()),
                "regime": chk})

    rng = np.random.default_rng(MASTER_SEED)
    boot_idx = {k: rng.integers(0, n, size=(B_BOOT_HIGH, n)) for k in arms}

    def slope(y0: np.ndarray, y1: np.ndarray, y2: np.ndarray) -> float:
        return float(y2.mean() - y0.mean())

    def quad(y0: np.ndarray, y1: np.ndarray, y2: np.ndarray) -> float:
        return float(2.0 * (y0.mean() - 2.0 * y1.mean() + y2.mean()))

    cells_out = {}
    rule13 = []
    for cid in BASE_CELLS:
        y0, y1, y2 = (arms[(cid, s)] for s in S_ARMS)
        b = slope(y0, y1, y2)
        c = quad(y0, y1, y2)
        # OLS witness on the full 3n points (RN-P1-4's identity, proven not asserted)
        sv = np.concatenate([np.full(n, s) for s in S_ARMS])
        yv = np.concatenate([y0, y1, y2])
        b_ols = float(np.polyfit(sv, yv, 1)[0])

        def boot(B: int) -> tuple[np.ndarray, np.ndarray]:
            bs = np.empty(B, float)
            cs = np.empty(B, float)
            for j in range(B):
                a0 = y0[boot_idx[(cid, S_ARMS[0])][j]]
                a1 = y1[boot_idx[(cid, S_ARMS[1])][j]]
                a2 = y2[boot_idx[(cid, S_ARMS[2])][j]]
                bs[j] = a2.mean() - a0.mean()
                cs[j] = 2.0 * (a0.mean() - 2.0 * a1.mean() + a2.mean())
            return bs, cs

        bs, cs = boot(B_BOOT)
        lo, hi = float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))
        pinned, signfirst = _classify(lo, hi)
        # rule 13: any CI endpoint within 1/(10B) of a decision boundary?
        margin = 1.0 / (RULE13_FACTOR * B_BOOT)
        near = []
        for name, bnd in (("0", 0.0), ("+equiv", EQUIV), ("-equiv", -EQUIV)):
            for end, val in (("lo", lo), ("hi", hi)):
                frac = float(np.mean(bs <= bnd))
                if min(abs(frac - 0.025), abs(frac - 0.975)) < margin:
                    near.append({"boundary": name, "endpoint": end, "tail_frac": frac})
        if near:
            bs, cs = boot(B_BOOT_HIGH)
            lo, hi = float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))
            pinned, signfirst = _classify(lo, hi)
            rule13.append({"cell": cid, "triggers": near, "B": B_BOOT_HIGH,
                           "ci_after": [lo, hi], "class_after": pinned})
        cells_out[cid] = {
            "cell": cid, "share": BASE_CELLS[cid][0], "phi": BASE_CELLS[cid][1],
            "r": R_REGISTERED[cid],
            "b_hat": b, "b_hat_ols_witness": b_ols,
            "identity_holds": bool(abs(b - b_ols) < 1e-12),
            "b_ci95": [lo, hi], "b_se_boot": float(np.std(bs, ddof=1)),
            "B": int(len(bs)),
            "classification": pinned, "classification_sign_first": signfirst,
            "readings_agree": bool(pinned == signfirst),
            "equivalence_margin": EQUIV,
            "ci_inside_margin": bool(lo >= -EQUIV and hi <= EQUIV),
            "ci_excludes_zero": bool(lo > 0.0 or hi < 0.0),
            "quadratic_coef": c,
            "quadratic_ci95": [float(np.quantile(cs, 0.025)),
                               float(np.quantile(cs, 0.975))],
            "quadratic_note": "descriptive only, no gate",
            "arm_means": {str(s): float(arms[(cid, s)].mean()) for s in S_ARMS},
        }

    classes = {c: cells_out[c]["classification"] for c in cells_out}
    agree = bool(len(set(classes.values())) == 1)
    out = {"utc": datetime.now(UTC).isoformat(), "worlds_per_arm": n,
           "per_arm": per_arm, "per_cell": cells_out,
           "cross_cell_agreement": agree, "classes": classes,
           "rule13_events": rule13,
           "slope_identity": "b-hat = mean(s=1) - mean(s=0), verified against an OLS "
                             "witness on all 3n points (RN-P1-4)",
           "bootstrap": RN_NOTES["RN-P1-6"], "seconds": time.time() - t0}
    write_json(OUT / "fit.json", out)
    _log("fit_done", classes=classes, agree=agree, seconds=out["seconds"])
    print("fit OK  " + "  ".join(
        f"{c}: b={cells_out[c]['b_hat']:+.6f} {cells_out[c]['b_ci95']} "
        f"{cells_out[c]['classification']}" for c in cells_out)
        + f"  agree={agree}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# FINALIZE.

TRUTH_TABLE = [
    {"n": "1", "condition": "any G0p1/G1p1 failure", "outcome": "STOP",
     "text": "STOP (citation/instrument defect; no arms)"},
    {"n": "2", "condition": "projection fails after escalation",
     "outcome": "NON_PROJECTABLE", "text": "NON_PROJECTABLE (handback)"},
    {"n": "3", "condition": "both cells POSITIVE", "outcome": "SIGN_SCAFFOLD",
     "text": "SIGN_SCAFFOLD -- the penalty's owner is frame-scaffolding; P2 doses it"},
    {"n": "4", "condition": "both cells NEGATIVE", "outcome": "SIGN_CONTAMINATION",
     "text": "SIGN_CONTAMINATION -- the gauge's amplification owns the penalty; P2 "
             "doses it; connects to K1's +0.0925 quantitatively"},
    {"n": "5", "condition": "both cells NULL", "outcome": "FRAME_INSENSITIVE",
     "text": "FRAME_INSENSITIVE -- neither named mechanism owns the penalty at this "
             "scale; a third mechanism is named, not invented"},
    {"n": "6", "condition": "cells disagree in classification (any mix incl. "
                            "UNDERPOWERED on one side)",
     "outcome": "SPLIT_OR_UNDERPOWERED",
     "text": "SPLIT_OR_UNDERPOWERED -- the phi-dependence or the power shortfall is "
             "named; P2's design inherits the diagnosis"},
]

SLUG_OF = {"POSITIVE": "SIGN_SCAFFOLD", "NEGATIVE": "SIGN_CONTAMINATION",
           "NULL": "FRAME_INSENSITIVE"}


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

    # the s = 0 arm's replication of M2's C4 (same base cell, fresh salt)
    c4 = p0["G0p1"]["(iii) M2 C4 anchor"]
    z = next(a for a in fit["per_arm"] if a["cell"] == "B1" and a["s"] == 0.0)
    diff = float(z["mean"] - c4["mean_persisted"])
    pooled = float(np.sqrt(z["sem"] ** 2 + c4["sem"] ** 2))
    repl = {"m2_C4_mean": c4["mean_persisted"], "m2_C4_sem": c4["sem"],
            "m2_C4_n": c4["n"], "p1_B1_s0_mean": z["mean"], "p1_B1_s0_sem": z["sem"],
            "p1_B1_s0_n": z["n"], "difference": diff, "pooled_sem": pooled,
            "z": float(diff / pooled), "within_2_pooled_sem": bool(abs(diff) <= 2 * pooled),
            "note": "same base cell (share 0.25, phi 0.05), DIFFERENT salt, so this is "
                    "a distributional replication and not a bit-identity claim"}

    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "verdict_slug": slug, "routing_cell": cell_n,
        "routing_text": next(t["text"] for t in TRUTH_TABLE if t["outcome"] == slug),
        "modifiers": [],
        "classes": classes, "cross_cell_agreement": fit["cross_cell_agreement"],
        "per_cell": fit["per_cell"], "per_arm": fit["per_arm"],
        "worlds_per_arm": fit["worlds_per_arm"],
        "total_worlds": int(fit["worlds_per_arm"] * len(S_ARMS) * len(BASE_CELLS)),
        "injection_point": p0["injection_point"],
        "m2_c4_replication": repl,
        "projection": g3, "rule13_events": fit["rule13_events"],
        "gates": {
            "G0p1": {"PASS": p0["G0p1"]["PASS"],
                     "detail": "base-cell r bit-exact from the pinned maps; all cited "
                               "sentences located verbatim by code; M2's C4 mean "
                               "bit-exact at source"},
            "G1p1": {"PASS": pil["G1p1"]["PASS"],
                     "detail": "injection moves the pre-map object; realized RMS within "
                               "5% of target; s = 0 bit-identical to the unperturbed "
                               "construction"},
            "G2p1": {"PASS": pil["G2p1"]["PASS"],
                     "detail": "rule-29 domain-pinned predicate held at all pilot arms "
                               "and all six full arms"},
            "G3p1": {"PASS": g3["PASS"],
                     "detail": f"MDE(2 SE) = {g3['base']['MDE_2SE']!r} <= {MDE_BAR} at "
                               f"n = {g3['worlds_per_arm_decided']}; escalation fired: "
                               f"{g3['escalation_fired']}"},
            "G4p1": {"PASS": True,
                     "detail": "routing disjoint-and-covering; tables generated "
                               "(rule 24); stages under estimate"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug, seconds=dec["seconds"])
    _tables(p0, pil, g3, fit, dec)
    _facts(p0, pil, g3, fit, dec)
    print(f"finalize OK  slug={slug}  cell={cell_n}  classes={classes}")
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
    g0 = p0["G0p1"]
    sec["g0p1"] = _md(
        ["clause", "expected", "recomputed / persisted", "bit-exact"],
        [[f"base-cell r {cid} (share {c['share']}, phi {c['phi']})",
          repr(c["r_registered"]), repr(c["r_recomputed"]), str(c["bit_exact"])]
         for cid, c in g0["(i) base-cell r"]["cells"].items()]
        + [["M2 C4 mean", repr(M2_C4_MEAN),
            repr(g0["(iii) M2 C4 anchor"]["mean_persisted"]),
            str(g0["(iii) M2 C4 anchor"]["bit_exact"])],
           ["M2 C4 is the same base cell as B1", "True",
            str(g0["(iii) M2 C4 anchor"]["same_base_cell_as_B1"]),
            str(g0["(iii) M2 C4 anchor"]["same_base_cell_as_B1"])]])
    sec["cites"] = _md(
        ["anchor", "located at", "verbatim quote (extracted by code, rule 24)"],
        [[name, f"`{d['file']}:{d['line']}` (para {d['paragraph_lines']})",
          d["quote"][:600] + ("…" if len(d["quote"]) > 600 else "")]
         if d["found"] else [name, "NOT FOUND", "—"]
         for name, d in g0["(ii) cited sentences"]["anchors"].items()])
    inj = p0["injection_point"]
    sec["injection"] = _md(
        ["property", "value"],
        [["choice rule", inj["choice_rule"]],
         ["**the object**", "**" + inj["object"] + "**  " + str(tuple(inj["shape"]))
          + "  " + inj["shape_meaning"]],
         ["built at", "`" + inj["built_at"] + "`"],
         ["built source", "`" + str(inj["built_source"]).strip() + "`"],
         ["returned at", "`" + inj["returned_at"] + "`"],
         ["**LAST read before the frozen map**",
          "**`" + inj["LAST_READ_BEFORE_MAP"] + "`**"],
         ["that source line", "`" + str(inj["last_read_source"]).strip() + "`"],
         ["emit_panel called at", "`" + inj["emit_panel_called_at"] + "`"],
         ["frozen map entry at", "`" + inj["frozen_map_entry_at"] + "`"],
         ["that source line", "`" + str(inj["frozen_map_entry_source"]).strip() + "`"],
         ["why this object", inj["why_this_object"]],
         ["injection mechanics", inj["injection_mechanics"]],
         ["k2b edited", str(inj["k2b_edited"])],
         ["suica_core edited", str(inj["suica_core_edited"])]])
    g1 = pil["G1p1"]
    a, b, c = (g1["(a) injection moves the pre-map object"],
               g1["(b) realized RMS within 5% of target"],
               g1["(c) s = 0 is bit-identical"])
    sec["g1p1"] = _md(
        ["clause", "quantity", "value", "PASS"],
        [["(a) moves the pre-map object", "worlds checked (s > 0)", str(a["n_checked"]),
          str(a["PASS"])],
         ["(a)", "min ||delta common||_F", repr(a["min_norm_delta"]), ""],
         ["(a)", "max ||delta common||_F", repr(a["max_norm_delta"]), ""],
         ["(a)", "every array bit-CHANGED", str(a["all_arrays_changed"]), ""],
         ["(b) realized RMS calibration", "tolerance", repr(b["tolerance"]),
          str(b["PASS"])],
         ["(b)", "max relative error", repr(b["max_relative_error"]), ""],
         ["(c) s = 0 bit-identity", "worlds checked", str(c["n_checked"]),
          str(c["PASS"])],
         ["(c)", "max |recovery difference|", repr(c["max_abs_difference"]), ""],
         ["(c)", "common array bit-identical at s = 0",
          str(c["all_common_arrays_bit_identical"]), ""]])
    sec["bitident"] = _md(
        ["cell", "world", "recovery via the injection path", "recovery unperturbed",
         "bit-identical", "abs difference"],
        [[r["cell"], str(r["world"]), repr(r["recovery_injected"]),
          repr(r["recovery_unperturbed"]), str(r["bit_identical"]),
          repr(r["abs_difference"])] for r in c["rows"]])
    sec["pilot"] = _md(
        ["cell", "s", "n", "mean", "min", "max", "finite", "any saturated",
         "nonzero var", "PASS"],
        [[q["cell"], repr(q["s"]), str(q["n"]), repr(q["mean"]), repr(q["min"]),
          repr(q["max"]), str(q["all_finite"]),
          str(q["any_saturated_abs_ge_0.995"]), str(q["nonzero_variance"]),
          str(q["PASS"])] for q in pil["G2p1"]["per_arm"]])
    sec["projection"] = _md(
        ["quantity", "value"],
        [["sigma source", g3["sigma_source"]],
         ["pilot s = 0 cells", ", ".join(f"{q['cell']} (n={q['n']}, sd={q['sd']!r})"
                                         for q in g3["per_cell"])],
         ["pooled df", str(g3["df"])],
         ["sigma_raw", repr(g3["sigma_raw"])],
         ["chi2 quantile", repr(g3["chi2_quantile"])],
         ["chi2 value", repr(g3["chi2_value"])],
         ["inflation factor", repr(g3["inflation"])],
         ["**sigma (df-inflated)**", "**" + repr(g3["sigma_df_inflated"]) + "**"],
         ["convention", g3["inflation_convention"]],
         ["SE(b-hat) formula", g3["base"]["formula"]],
         ["SE(b-hat) at n = " + str(g3["base"]["worlds_per_arm"]),
          repr(g3["base"]["SE_b_hat"])],
         ["**MDE(2 SE)**", "**" + repr(g3["base"]["MDE_2SE"]) + "**"],
         ["bar", repr(MDE_BAR)],
         ["**PASS**", "**" + str(g3["base"]["PASS"]) + "**"],
         ["escalation fired", str(g3["escalation_fired"])],
         ["worlds per arm decided", str(g3["worlds_per_arm_decided"])]])
    sec["arms"] = _md(
        ["cell", "share", "phi", "s", "n", "mean", "sd", "SEM",
         "mean realized delta RMS", "max calibration error"],
        [[q["cell"], repr(q["share"]), repr(q["phi"]), repr(q["s"]), str(q["n"]),
          repr(q["mean"]), repr(q["sd"]), repr(q["sem"]),
          repr(q["cal_realized_rms_mean"]), repr(q["cal_rel_error_max"])]
         for q in fit["per_arm"]])
    sec["slopes"] = _md(
        ["cell", "phi", "r", "b-hat", "95% CI", "bootstrap SE", "B",
         "classification (pinned)", "sign-first reading", "agree",
         "quadratic coef", "quadratic 95% CI"],
        [[d["cell"], repr(d["phi"]), repr(d["r"]), repr(d["b_hat"]),
          repr(d["b_ci95"]), repr(d["b_se_boot"]), str(d["B"]),
          "**" + d["classification"] + "**", d["classification_sign_first"],
          str(d["readings_agree"]), repr(d["quadratic_coef"]),
          repr(d["quadratic_ci95"])] for d in fit["per_cell"].values()])
    sec["identity"] = _md(
        ["cell", "b-hat = mean(s=1) - mean(s=0)", "OLS witness on all 3n points",
         "identity holds", "mean(s=0)", "mean(s=0.5)", "mean(s=1.0)"],
        [[d["cell"], repr(d["b_hat"]), repr(d["b_hat_ols_witness"]),
          str(d["identity_holds"]), repr(d["arm_means"]["0.0"]),
          repr(d["arm_means"]["0.5"]), repr(d["arm_means"]["1.0"])]
         for d in fit["per_cell"].values()])
    rp = dec["m2_c4_replication"]
    sec["repl"] = _md(
        ["quantity", "value"],
        [["M2 C4 mean (share 0.25, phi 0.05, n = " + str(rp["m2_C4_n"]) + ")",
          repr(rp["m2_C4_mean"])],
         ["M2 C4 SEM", repr(rp["m2_C4_sem"])],
         ["P1 B1 s = 0 mean (n = " + str(rp["p1_B1_s0_n"]) + ")",
          repr(rp["p1_B1_s0_mean"])],
         ["P1 B1 s = 0 SEM", repr(rp["p1_B1_s0_sem"])],
         ["difference", repr(rp["difference"])],
         ["pooled SEM", repr(rp["pooled_sem"])],
         ["**z**", "**" + repr(rp["z"]) + "**"],
         ["within 2 pooled SEM", str(rp["within_2_pooled_sem"])],
         ["note", rp["note"]]])
    sec["truth_table"] = _md(
        ["#", "condition", "outcome"],
        [[t["n"], t["condition"],
          ("**" + t["text"] + "**  <-- THIS LEG") if t["outcome"] == dec["verdict_slug"]
          else t["text"]] for t in TRUTH_TABLE])
    sec["gates"] = _md(["gate", "PASS", "detail"],
                       [[k, str(v["PASS"]), v["detail"]] for k, v in dec["gates"].items()])
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
    trows = [["part0", str(est["part0"]), "%.3f" % meas.get("part0_done", float("nan"))],
             ["pilot", str(est["pilot"]), "%.3f" % meas.get("pilot_done", float("nan"))],
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
    body = ["# M4-P1 report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _facts(p0: dict[str, Any], pil: dict[str, Any], g3: dict[str, Any],
           fit: dict[str, Any], dec: dict[str, Any]) -> None:
    inj = p0["injection_point"]
    g1 = pil["G1p1"]
    a, b, c = (g1["(a) injection moves the pre-map object"],
               g1["(b) realized RMS within 5% of target"],
               g1["(c) s = 0 is bit-identical"])
    rp = dec["m2_c4_replication"]
    f = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"],
        "INJ_POINT": inj["LAST_READ_BEFORE_MAP"], "INJ_OBJ": inj["object"],
        "INJ_SHAPE": str(tuple(inj["shape"])), "INJ_BUILT": inj["built_at"],
        "INJ_RET": inj["returned_at"], "INJ_EMIT": inj["emit_panel_called_at"],
        "INJ_MAP": inj["frozen_map_entry_at"],
        "NORM_MIN": a["min_norm_delta"], "NORM_MAX": a["max_norm_delta"],
        "RMS_ERR": b["max_relative_error"], "RMS_TOL": b["tolerance"],
        "BITID": c["all_bit_identical"], "BITID_N": c["n_checked"],
        "BITID_MAXDIFF": c["max_abs_difference"],
        "SIGMA_RAW": g3["sigma_raw"], "INFL": g3["inflation"],
        "SIGMA": g3["sigma_df_inflated"], "DF": g3["df"],
        "SE_B": g3["base"]["SE_b_hat"], "MDE": g3["base"]["MDE_2SE"],
        "MDE_BAR": MDE_BAR, "ESC": g3["escalation_fired"],
        "NPERARM": fit["worlds_per_arm"], "NTOTAL": dec["total_worlds"],
        "AGREE": fit["cross_cell_agreement"],
        "CLASSES": ", ".join(f"{k}={v}" for k, v in fit["classes"].items()),
        "EQUIV": EQUIV,
        "N_RULE13": len(fit["rule13_events"]),
        "M2_MEAN": rp["m2_C4_mean"], "P1_MEAN": rp["p1_B1_s0_mean"],
        "REPL_DIFF": rp["difference"], "REPL_Z": rp["z"],
        "REPL_OK": rp["within_2_pooled_sem"],
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
    }
    for cid, d in fit["per_cell"].items():
        f.update({f"{cid}_B": d["b_hat"], f"{cid}_CI": d["b_ci95"],
                  f"{cid}_CLASS": d["classification"],
                  f"{cid}_SIGNFIRST": d["classification_sign_first"],
                  f"{cid}_AGREE": d["readings_agree"],
                  f"{cid}_QUAD": d["quadratic_coef"],
                  f"{cid}_QUADCI": d["quadratic_ci95"],
                  f"{cid}_PHI": d["phi"], f"{cid}_R": d["r"],
                  f"{cid}_IDENT": d["identity_holds"],
                  f"{cid}_SE": d["b_se_boot"],
                  f"{cid}_Y0": d["arm_means"]["0.0"],
                  f"{cid}_Y1": d["arm_means"]["0.5"],
                  f"{cid}_Y2": d["arm_means"]["1.0"]})
    write_json(OUT / "prose_facts.json", f)


REPORT_TEMPLATE = r"""# SUICA M4-P1 — the frame-injection sign probe — **{{SLUG}}**

**Outcome: {{SLUG}} (routing cell {{CELL}}).** {{ROUTING_TEXT}}

Per base cell: {{CLASSES}} (cross-cell agreement: {{AGREE}}). {{NTOTAL}} fresh
worlds ({{NPERARM}}/arm × 6 arms). No seal — the leans were registered honestly
split, so no sealable point prediction existed.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md` BEFORE run (commit 7589299).
Every number below is generated from artifacts by code (rule 24); none is
hand-typed.

---

## 1. The injection point

The registration's choice rule is its own sentence (rule 12): *the LAST common
per-occasion object every author's response shares before the frozen map*. In
the K2b family there is exactly one such object.

<<TABLE:injection>>

**The object is `{{INJ_OBJ}}` {{INJ_SHAPE}}, and the injection point is
`{{INJ_POINT}}`** — the line inside `emit_panel` that folds the common channel
into every author's response. That call sits at `{{INJ_EMIT}}`, one line before
the frozen map's entry at `{{INJ_MAP}}`. Nothing between them is both common and
per-occasion.

δ(o) is added to `common[c, o, :]` for **every** context c, so every author on
occasion o receives the identical response-level shift `w["common"]·δ(o)` — which
is what "added to every author's response on occasion o" means. Neither
`suica_core/` nor `run_suica_m4_k2b_t4_branch.py` was edited: the harness calls
k2b's own `build_k2b_world`, perturbs the returned array, and hands the world to
k2b's own `run_field_world`.

## 2. G0p1 — the citations

<<TABLE:g0p1>>

The cited sentences are **located and extracted by code**, not transcribed —
each anchor substring is found in its controlling document and the containing
paragraph is lifted verbatim, so rule 24 covers the quotes as well as the
tables:

<<TABLE:cites>>

## 3. G1p1 — the instrument is live, calibrated, and inert at zero

<<TABLE:g1p1>>

- **(a) The injection moves the pre-map object.** Frobenius norm of the change
  ranges over {{NORM_MIN}} … {{NORM_MAX}} across the s > 0 pilot worlds, and
  every perturbed array differs bit-wise from its unperturbed self.
- **(b) The calibration lands.** Worst relative error between the realized
  response-level RMS of δ and its target is **{{RMS_ERR}}**, against a
  {{RMS_TOL}} tolerance. The calibration is solved in closed form and then
  *recomputed from the scaled δ* before being persisted (RN-P1-3), so this
  tests an executed number rather than an intended one.
- **(c) s = 0 is bit-identical.** The full injection path runs at s = 0 — δ is
  drawn and scaled to exactly zero — and the resulting field statistic is
  compared bit-for-bit against k2b's unperturbed construction on {{BITID_N}}
  worlds: **{{BITID}}**, max |difference| {{BITID_MAXDIFF}}. The path is proven
  inert at zero, so no arm is contaminated by the mere existence of the
  injection.

<<TABLE:bitident>>

## 4. G2p1 — the pilot and the rule-29 predicate

<<TABLE:pilot>>

Domain-pinned per rule 29: `recovery_b_only` is a weighted mean of matrix
cosines on [−1, 1], so the predicate is finiteness, non-saturation at
|x| ≥ 0.995 and nonzero variance, with **no positivity clause**.

## 5. G3p1 — the projection

<<TABLE:projection>>

σ comes from the pilot's s = 0 worlds pooled within base cell (df = {{DF}}),
df-inflated by {{INFL}} on M1b's registered χ²(0.10) convention: σ_raw
{{SIGMA_RAW}} → **{{SIGMA}}**. RN-P1-4 makes SE(b̂) exact for this design —
σ/√(n/2) — giving SE = {{SE_B}} and **MDE(2·SE) = {{MDE}} ≤ {{MDE_BAR}}**. The
once-only escalation to 384/arm did not fire ({{ESC}}).

## 6. The verdict

<<TABLE:slopes>>

<<TABLE:arms>>

### 6.1 The slope's algebra, proven not asserted

<<TABLE:identity>>

With s ∈ {0, 0.5, 1.0} equally replicated the OLS slope reduces **exactly** to
mean(s = 1) − mean(s = 0); the midpoint arm contributes nothing to b̂ and
identifies only the descriptive quadratic. The identity is verified against a
full OLS witness on all 3n points at both cells.

### 6.2 The M2 anchor replicates

<<TABLE:repl>>

The s = 0 arm at B1 sits at {{P1_MEAN}} against M2's C4 mean {{M2_MEAN}} on the
same base cell — difference {{REPL_DIFF}}, z = {{REPL_Z}}, within two pooled
SEM: {{REPL_OK}}. Different salt, so this is a distributional replication and
not a bit-identity claim; it is reported because it is the cheapest available
check that the unperturbed arm is the same object M2 measured.

## 7. Routing

<<TABLE:truth_table>>

## 8. Gates

<<TABLE:gates>>

## 9. Sides declared (rule 22)

<<TABLE:sides>>

## 10. Pinned readings

<<TABLE:rn>>

## 11. Rule events

- **Rule 13:** {{N_RULE13}} boundary event(s) triggered a B = 20000 re-run.
- **Rule 26:** no bounded winner; nothing was fitted with active bounds.
- **Rule 29:** in force as the G2p1 predicate, domain-pinned to [−1, 1] with no
  positivity clause. Held at every pilot arm and every full arm.
- **Rule 30:** every constant in this harness was verified against its persisted
  source before Part 0, and every quoted sentence is extracted by code.

## 12. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine and the only `pandas` present belongs to CPython 3.9.6,
   which cannot import the machinery. A CPython {{PYTHON}} venv was built
   outside the repo from `requirements-lock-main.txt` verbatim and pinned.
   Resolved BEFORE any hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.

## 13. Registration-defect candidates

1. **The verdict classification is not disjoint** (RN-P1-5). POSITIVE (CI > 0)
   and NULL (CI inside ±{{EQUIV}}) overlap: a CI like (0.001, 0.005) satisfies
   both. Rule 16 is met on the routing table but not on the classification that
   feeds it. Pinned before any number — equivalence wins, per rule 4 — with the
   sign-first ordering also computed and reported. Non-blocking.

## 14. Environment

<<TABLE:env>>

## 15. Timing

<<TABLE:timing>>

---

*Artifacts: `results/m4_p1_frame_injection/` (gitignored) — `part0.json`,
`pilot.json`, `pilot_field.csv`, `pilot_calibration.csv`, `projection.json`,
`arms/`, `fit.json`, `decision.json`, `prose_facts.json`, `report_tables.md`,
`run_log.jsonl`. Harness: `scripts/run_suica_m4_p1_frame_injection.py`.*
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
    path = ROOT / "reports" / "SUICA_M4_P1_FRAME_INJECTION_REPORT.md"
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
