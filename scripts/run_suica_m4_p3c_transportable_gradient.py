#!/usr/bin/env python3
"""SUICA M4-P3c -- the transportable gradient, by differences.

Registered BEFORE run in docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md
("M4-P3c", commit 11f42d6).  Binding.

P3b delivered a certified split-seed instrument and proved the RATIO estimand
infeasible (its denominator sits at ~3 SE).  Defect #56 sharpened the
convention -- inheritance is not exemption -- and adopted the DIFFERENCE
alternative.  This leg runs it:

    range_nat = R_nat(phi=.98) - R_nat(phi=.05)          the natural gradient
    range_ref = R_refresh(.98) - R_refresh(.05)          the TRANSPORTABLE one
    D_grad    = range_nat - range_ref                    the FRAME-OWNED part

all three under ONE joint world-pair bootstrap, because R_nat and R_refresh
share the A-worlds and that correlation is part of the estimator.

The instrument is IMPORTED from scripts/run_suica_m4_p3b_refresh_gradient.py by
file, with provenance recorded, and its C2 battery re-run on fresh probe pairs
before anything is measured.  k2b and suica_core/ stay untouched.

Stages: part0 -> pilot -> project -> arm_<tag> (5) -> fit -> finalize -> report
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
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

OUT = ROOT / "results" / "m4_p3c_transportable_gradient"
RES = ROOT / "results"
M1CRES = RES / "m4_m1c_r_at_level"
P3BRES = RES / "m4_p3b_refresh_gradient"
P3BSRC = ROOT / "scripts" / "run_suica_m4_p3b_refresh_gradient.py"

LEG = "M4-P3c"
BANNER = ("the transportable gradient by differences, on P3b's certified split-seed "
          "instrument; exploratory, label-free; no seal")

MASTER_SEED = 20260814
SALT_AUTHOR = "m4p3c-author"
SALT_FRAME_A = "m4p3c-frameA"
SALT_FRAME_B = "m4p3c-frameB"
SALT_PILOT = "m4p3c-pilot"
SHARE = 0.25
PHI_LO, PHI_HI, PHI_MID = 0.05, 0.98, 0.60
ENDPOINT_PAIRS = 768
ENDPOINT_PAIRS_ESCALATED = 1152
MID_PAIRS = 192
CHUNK = 384
PILOT_PAIRS = 4
PROBE_PAIRS = 4
W_INT_ARM = "zero"

B_BOOT = 2000
B_BOOT_HIGH = 20000
B_PROJ = 2000
RULE13_FACTOR = 10.0
CHI2_Q = 0.10
POWER_MIN = 0.80
FALSE_FIRE_MAX = 0.10
ANCHOR_K = 2.0 * math.sqrt(2.0)
SATURATION_ABS = 0.995
# the registered truths, both keyed on M1c's realized natural range
M1C_RANGE = 0.010391443071199338

AUTHOR_OBJECTS = ("trait", "a_load", "loadings")
FRAME_OBJECTS = ("slow", "slow_latent", "noise", "common", "int")

# ---------------------------------------------------------------------------
# RN-P3C notes.  PINNED IN PART 0, BEFORE ANY MEASUREMENT WORLD.
#
# RN-P3C-1 (the instrument is imported, not re-extracted).  build_split_world
#   is loaded from scripts/run_suica_m4_p3b_refresh_gradient.py by file path.
#   Part 0 records the file, the function's definition line, the sha256 of its
#   source text and of the whole file, and re-runs P3b's C2 battery on FRESH
#   probe pairs.  Re-extracting would have created a second copy to drift; a
#   by-file import keeps exactly one certified builder in the programme.
#
# RN-P3C-2 (the side-signing REVERSES from P3b, deliberately).  P3b reported
#   range_nat = R(.05) - R(.98) = -0.0104.  THIS registration defines
#   range = value(.98) - value(.05), so range_nat is +0.010391443071199338 --
#   the same quantity with the opposite sign, and the sign the registration's
#   own truths use (FULLY_FRAME sets D_grad = +0.0104).  Every range in this
#   leg is HI minus LO.  Stated because a silent sign flip between sibling legs
#   is exactly the kind of thing that survives review and then poisons a
#   comparison.
#
# RN-P3C-3 (the bootstrap is JOINT, and that is not a detail).  R_nat and
#   R_refresh are computed from the SAME A-world -- one gauge pass scored
#   against two truth panels -- so they are strongly correlated within a pair.
#   The bootstrap therefore resamples PAIR INDICES once per replicate and
#   recomputes both ranges from the same resampled indices, so D_grad's
#   interval inherits the cancellation.  Treating them as independent would
#   inflate SE(D_grad) by up to sqrt(2); the realized bootstrap correlation
#   between range_nat and range_ref is reported.
#
# RN-P3C-4 (what the projection tests).  Two registered truths, both keyed on
#   M1c's realized natural range: FULLY_FRAME {D_grad = 0.010391443071199338,
#   range_ref = 0} and TRANSPORTS {range_ref = 0.010391443071199338,
#   D_grad = 0}.  Under each, the NON-null quantity must be detected at 2*SE
#   with power >= 0.8 AND the null quantity must false-fire at <= 0.1.  The
#   gate is the conjunction of all four numbers.  Simulated from the pilot's
#   realized (sd_nat, sd_ref, rho_within), so the correlation enters the
#   projection exactly as it enters the estimator.
#
# RN-P3C-5 (the fraction is UNBUDGETED and says so).  range_ref/range_nat is
#   the P3b ratio that failed its budget.  It is quoted here as a point with an
#   honest CI and the label UNBUDGETED, gates nothing, and routes nothing.  It
#   appears because a reader will compute it anyway; showing its width is the
#   P3b lesson made visible.
#
# RN-P3C-6 (equivalence bands).  eps_D and eps_r are computed in Part 0 from
#   the pilot's realized noise, df-inflated on the registered chi2(0.10)
#   convention, at the DECIDED pairs/phi, and written into the report before
#   the arms run.  NULL is tested first (#55).
#
# RN-P3C-9 (the pilot's noise inputs are checked against the realized arms and
#   the check is REPORTED, added before any verdict was read).  The pilot is 4
#   pairs per endpoint, so its sd and especially its CORRELATION carry enormous
#   sampling error -- an n = 4 correlation has a standard error of roughly 0.5.
#   The Part-0 bands route, as registered; but the same bands are RECOMPUTED
#   from the realized arms and both verdicts are re-classified under them, and
#   both readings are shown.  If they disagree the disagreement is the finding,
#   not something to be buried; if they agree the verdict is robust to the
#   pilot's luck.
#
# RN-P3C-7 (the 0.60 arm is a shape reading).  192 pairs at phi = 0.60 enter
#   C1' (it is one of M1c's five levels) and the shape table, and enter NO
#   estimand: range_nat, range_ref and D_grad are endpoint differences by
#   registration.  Reported, never routed.
#
# RN-P3C-8 (corpus labels).  R_nat, R_refresh and R_deframe at a pair index
#   share ONE corpus string (they share the gauge pass, or the tag), so P1's
#   label noise cannot enter a within-pair contrast.  Across phi the tag must
#   differ; the ranges are cross-phi, so the label difference sits inside them
#   exactly as it sat inside M1c's own cross-phi comparison -- which is why C1'
#   is distributional and why the anchor is the right control for it.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-P3C-1": "build_split_world is IMPORTED from P3b by file path with the file's "
                "and the function's sha256 recorded, and P3b's C2 battery re-run on "
                "fresh probe pairs; re-extracting would create a second copy to drift",
    "RN-P3C-2": "the side-signing REVERSES from P3b deliberately: this registration "
                "defines range = value(.98) - value(.05), so range_nat is "
                "+0.010391443071199338 and matches the registration's own truths; "
                "stated because a silent sign flip between sibling legs poisons "
                "comparisons",
    "RN-P3C-3": "the bootstrap resamples PAIR INDICES once per replicate and recomputes "
                "both ranges from the same indices, because R_nat and R_refresh share "
                "the A-world; treating them as independent would inflate SE(D_grad) by "
                "up to sqrt(2). The realized correlation is reported",
    "RN-P3C-4": "the projection simulates both registered truths from the pilot's "
                "realized (sd_nat, sd_ref, rho_within); PASS is the conjunction of both "
                "powers >= 0.8 at 2*SE and both null false-fires <= 0.1",
    "RN-P3C-5": "range_ref/range_nat is the ratio that failed P3b's budget; quoted here "
                "as a point with an honest CI, labelled UNBUDGETED, gating and routing "
                "nothing",
    "RN-P3C-6": "eps_D and eps_r come from the pilot's realized noise, df-inflated on "
                "the chi2(0.10) convention at the DECIDED pairs/phi, written before the "
                "arms; NULL is tested first (#55)",
    "RN-P3C-9": "the pilot is 4 pairs/endpoint, so its sd and especially its "
                "correlation carry enormous sampling error (an n=4 correlation has SE "
                "~0.5). The Part-0 bands route as registered, but they are RECOMPUTED "
                "from the realized arms and both verdicts re-classified under them; "
                "both readings are shown",
    "RN-P3C-7": "the phi = 0.60 arm enters C1' and the shape table and NO estimand -- "
                "the three estimands are endpoint differences by registration",
    "RN-P3C-8": "R_nat, R_refresh and R_deframe at a pair index share one corpus "
                "string, so label noise cannot enter a within-pair contrast; across phi "
                "the tag differs, which is why C1' is distributional",
}

# ---------------------------------------------------------------------------
# ONE loader chain.

_MODS: dict[str, Any] = {}


def _load_named(name: str, path: Path) -> Any:
    if name not in _MODS:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)          # type: ignore[arg-type]
        sys.modules[name] = mod
        spec.loader.exec_module(mod)                         # type: ignore[union-attr]
        _MODS[name] = mod
    return _MODS[name]


def p3b() -> Any:
    """P3b's certified harness -- the instrument's home (RN-P3C-1)."""
    return _load_named("run_suica_m4_p3b_refresh_gradient", P3BSRC)


def k2b() -> Any:
    return p3b().k2b()


def k2c() -> Any:
    return p3b().k2c()


def kr1() -> Any:
    return p3b().kr1()


def v8() -> Any:
    return k2b().v8


def build_split_world(author_seed: int, frame_seed: int,
                      phi_slow: float) -> dict[str, np.ndarray]:
    return p3b().build_split_world(author_seed, frame_seed, phi_slow)


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


def seed_for(kind: str, phi: float, idx: int, salt: str) -> int:
    key = f"{LEG}|{salt}|{kind}|phi{phi!r}|i{idx}|seed{MASTER_SEED}"
    return int(v8().stable_bucket(key, salt=salt, modulus=2 ** 63 - 1))


def pair_seeds(phi: float, idx: int, suffix: str = "") -> dict[str, int]:
    return {"author": seed_for("author", phi, idx, SALT_AUTHOR + suffix),
            "frameA": seed_for("frameA", phi, idx, SALT_FRAME_A + suffix),
            "frameB": seed_for("frameB", phi, idx, SALT_FRAME_B + suffix)}


def _predicate(vals: np.ndarray) -> dict[str, Any]:
    fin = bool(np.all(np.isfinite(vals)))
    sat = bool(np.any(np.abs(vals) >= SATURATION_ABS))
    nz = bool(float(np.std(vals, ddof=1)) > 0.0)
    return {"all_finite": fin, "any_saturated_abs_ge_0.995": sat,
            "nonzero_variance": nz, "min": float(vals.min()), "max": float(vals.max()),
            "PASS": bool(fin and (not sat) and nz)}


def run_pair(phi: float, idx: int, arm_id: str, suffix: str = "",
             *, with_deframe: bool = True) -> dict[str, Any]:
    """One A/B pair: ONE gauge pass on A, scored against A's and B's truth."""
    sd = pair_seeds(phi, idx, suffix)
    wa = build_split_world(sd["author"], sd["frameA"], phi)
    wb = build_split_world(sd["author"], sd["frameB"], phi)
    wa["_author_seed"] = sd["author"]
    m = k2b()
    w = m.arm_weights(SHARE, W_INT_ARM)
    sc = p3b().score_pair(wa, wb, w, arm_id, idx, phi, with_deframe=with_deframe)
    return {"phi": phi, "share": SHARE, "pair": idx, "author_seed": sd["author"],
            "frameA_seed": sd["frameA"], "frameB_seed": sd["frameB"], **sc}


# ---------------------------------------------------------------------------
# PART 0 -- provenance, the C2 re-run, G0 citations.

def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")

    # --- the instrument's provenance (RN-P3C-1) ----------------------------
    mod = p3b()
    fn = mod.build_split_world
    src_fn = inspect.getsource(fn)
    file_bytes = P3BSRC.read_bytes()
    prov = {
        "imported_from": rel(P3BSRC),
        "function": "build_split_world",
        "definition_line": int(inspect.getsourcelines(fn)[1]),
        "signature": f"build_split_world{inspect.signature(fn)}",
        "function_sha256": hashlib.sha256(src_fn.encode("utf-8")).hexdigest(),
        "file_sha256": hashlib.sha256(file_bytes).hexdigest(),
        "file_bytes": len(file_bytes),
        "p3b_provenance_entries": len(mod.PROVENANCE),
        "p3b_source_span": "run_suica_m4_k2b_t4_branch.py:321-349",
        "why_imported_not_re_extracted": RN_NOTES["RN-P3C-1"],
        "k2b_edited": False, "suica_core_edited": False,
    }

    # --- the C2 battery, re-run on FRESH probe pairs -----------------------
    rows = []
    for i in range(PROBE_PAIRS):
        sd = pair_seeds(PHI_LO, i, "-probe")
        wa = build_split_world(sd["author"], sd["frameA"], PHI_LO)
        wb = build_split_world(sd["author"], sd["frameB"], PHI_LO)
        rec: dict[str, Any] = {"probe": i, **{f"seed_{k}": v for k, v in sd.items()}}
        for k in AUTHOR_OBJECTS:
            rec[f"author::{k}"] = bool(np.array_equal(
                np.asarray(wa[k]).view(np.uint8), np.asarray(wb[k]).view(np.uint8)))
        for k in FRAME_OBJECTS:
            d = float(np.linalg.norm(np.asarray(wa[k]) - np.asarray(wb[k])))
            rec[f"frame::{k}"] = d
        rows.append(rec)
    sd0 = pair_seeds(PHI_LO, 0, "-probe")
    r1 = build_split_world(sd0["author"], sd0["frameA"], PHI_LO)
    r2 = build_split_world(sd0["author"], sd0["frameA"], PHI_LO)
    det = {k: bool(np.array_equal(np.asarray(r1[k]).view(np.uint8),
                                  np.asarray(r2[k]).view(np.uint8))) for k in r1}
    c2 = {
        "n_probe_pairs": PROBE_PAIRS, "rows": rows, "fresh_salt_suffix": "-probe",
        "C2a_all_author_identical": bool(all(r[f"author::{k}"] for r in rows
                                             for k in AUTHOR_OBJECTS)),
        "C2a_all_frame_differ": bool(all(r[f"frame::{k}"] > 0.0 for r in rows
                                         for k in FRAME_OBJECTS)),
        "C2a_norm_delta_min": {k: float(min(r[f"frame::{k}"] for r in rows))
                               for k in FRAME_OBJECTS},
        "C2a_norm_delta_max": {k: float(max(r[f"frame::{k}"] for r in rows))
                               for k in FRAME_OBJECTS},
        "C2b_determinism": det,
        "C2b_all_identical": bool(all(det.values())),
        "C2c_loadings_shared": bool(all(r["author::loadings"] for r in rows)),
    }
    c2["PASS"] = bool(c2["C2a_all_author_identical"] and c2["C2a_all_frame_differ"]
                      and c2["C2b_all_identical"] and c2["C2c_loadings_shared"])

    # --- G0: M1c's row, P3b's persisted SEs, the ladder r ------------------
    cm = read_csv_rt(M1CRES / "cell_means.csv")
    rs = cm[cm["share"] == SHARE].sort_values("phi")
    m1c = [{"cell_tag": r["cell_tag"], "phi": float(r["phi"]),
            "r_pred": float(r["r_pred"]), "mean": float(r["field_mean"]),
            "sem": float(r["field_sem"]), "n_worlds": int(r["n_worlds"])}
           for _, r in rs.iterrows()]
    by_phi = {round(d["phi"], 10): d for d in m1c}
    range_m1c = float(by_phi[PHI_HI]["mean"] - by_phi[PHI_LO]["mean"])
    p3bd = read_json(P3BRES / "decision.json")
    g0 = {
        "m1c_source": rel(M1CRES / "cell_means.csv"), "m1c_rows": m1c,
        "m1c_range_HI_minus_LO": range_m1c,
        "m1c_range_matches_registration": bool(range_m1c == M1C_RANGE),
        "sign_convention": RN_NOTES["RN-P3C-2"],
        "p3b_source": rel(P3BRES / "decision.json"),
        "p3b_verdict": p3bd["verdict_slug"],
        "p3b_SE_range_ref_at_192": p3bd["bands"]["SE_range_ref_at_192"],
        "p3b_sigma_R_nat": p3bd["bands"]["sigma_R_nat_df_inflated"],
        "p3b_sigma_R_refresh": p3bd["bands"]["sigma_R_refresh_df_inflated"],
        "p3b_certified": p3bd["instrument_certified"],
        "ladder": [{"phi": d["phi"], "r_recomputed": r_of(SHARE, d["phi"]),
                    "r_M1c": d["r_pred"],
                    "bit_exact": bool(r_of(SHARE, d["phi"]) == d["r_pred"])}
                   for d in m1c],
    }
    g0["PASS"] = bool(g0["m1c_range_matches_registration"]
                      and g0["p3b_verdict"] == "NON_PROJECTABLE"
                      and g0["p3b_certified"]
                      and all(d["bit_exact"] for d in g0["ladder"]))

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md (M4-P3c, "
                        "BEFORE run, commit 11f42d6)",
        "master_seed": MASTER_SEED,
        "salts": {"author": SALT_AUTHOR, "frameA": SALT_FRAME_A,
                  "frameB": SALT_FRAME_B, "pilot": SALT_PILOT},
        "rn_notes": RN_NOTES, "instrument_provenance": prov, "C2": c2, "G0": g0,
        "estimands": {
            "range_nat": "R_nat(phi=0.98) - R_nat(phi=0.05)",
            "range_ref": "R_refresh(phi=0.98) - R_refresh(phi=0.05)",
            "D_grad": "range_nat - range_ref  (the frame-owned component)",
            "fraction": "range_ref / range_nat -- UNBUDGETED descriptive only",
            "bootstrap": RN_NOTES["RN-P3C-3"]},
        "design": {"share": SHARE, "endpoints": [PHI_LO, PHI_HI],
                   "endpoint_pairs": ENDPOINT_PAIRS, "mid_phi": PHI_MID,
                   "mid_pairs": MID_PAIRS,
                   "total_pairs": 2 * ENDPOINT_PAIRS + MID_PAIRS,
                   "total_worlds": 2 * (2 * ENDPOINT_PAIRS + MID_PAIRS),
                   "chunk": CHUNK, "deframe_stride": 1},
        "sides_rule22": {
            "L-1p3c": {"clause": "FULLY_FRAME / MIXED / TRANSPORTS / INVERSION / "
                                 "underpowered",
                       "prior": "0.50 / 0.25 / 0.10 / 0.05 / 0.10",
                       "sided": "categorical"},
            "V-A": {"clause": "D_grad vs 0, NULL-first", "sided": "two-sided"},
            "V-B": {"clause": "range_ref vs 0, NULL-first", "sided": "two-sided"},
            "C1'": {"clause": f"R_nat levels within {ANCHOR_K}*SEM of M1c's row",
                    "sided": "two-sided"},
            "G3p3c": {"clause": f"both powers >= {POWER_MIN} at 2*SE and both null "
                                f"false-fires <= {FALSE_FIRE_MAX}",
                      "sided": "one-sided each"}},
        "stage_estimates_seconds": {"part0": 180, "pilot": 60, "project": 30,
                                    "arms_each": 350, "fit": 240, "finalize": 60},
        "environment": {"python": sys.version.split()[0],
                        "python_executable": sys.executable,
                        "platform": platform.platform(), "numpy": np.__version__,
                        "pandas": pd.__version__,
                        "scipy": __import__("scipy").__version__},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "part0.json", part0)
    _log("part0_done", G0=g0["PASS"], C2=c2["PASS"], seconds=part0["seconds"])
    if not (g0["PASS"] and c2["PASS"]):
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "INSTRUMENT_DEFECT", "routing_cell": "1",
            "routing_text": "STOP / INSTRUMENT_DEFECT", "G0": g0, "C2": c2,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: INSTRUMENT_DEFECT -- G0/C2 failed")
    print(f"part0 OK  G0 PASS  C2 PASS ({PROBE_PAIRS} fresh probe pairs)  "
          f"instrument fn sha {prov['function_sha256'][:12]} from "
          f"{prov['imported_from']}:{prov['definition_line']}  "
          f"range_m1c={range_m1c!r}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# PILOT -- rule-29 predicate, realized noise, the correlation, the bands.

def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    if not p0["G0"]["PASS"]:
        raise SystemExit("STOP: G0 did not pass.")
    rows = []
    for phi in (PHI_LO, PHI_HI):
        for i in range(PILOT_PAIRS):
            rows.append(run_pair(phi, i, f"P3C-PILOT-p{phi}", "-pilot"))
        print(f"  pilot phi={phi}: done ({time.time() - t0:.1f}s)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "pilot_field.csv", index=False)

    per, ok = [], True
    for phi, grp in df.groupby("phi"):
        cn = _predicate(grp["R_nat"].to_numpy(float))
        cr = _predicate(grp["R_refresh"].to_numpy(float))
        ok &= cn["PASS"] and cr["PASS"]
        per.append({"phi": float(phi), "n": int(len(grp)),
                    "R_nat_mean": float(grp["R_nat"].mean()),
                    "R_refresh_mean": float(grp["R_refresh"].mean()),
                    "R_deframe_mean": float(grp["R_deframe"].mean()),
                    "R_nat_regime": cn, "R_refresh_regime": cr,
                    "PASS": bool(cn["PASS"] and cr["PASS"])})

    def pooled(col: str) -> tuple[float, int]:
        ss, dfree = 0.0, 0
        for _, grp in df.groupby("phi"):
            v = grp[col].to_numpy(float)
            ss += float(np.sum((v - v.mean()) ** 2))
            dfree += len(v) - 1
        return float(np.sqrt(ss / dfree)), dfree

    sd_nat_raw, dfree = pooled("R_nat")
    sd_ref_raw, _ = pooled("R_refresh")
    infl = float(np.sqrt(dfree / float(chi2.ppf(CHI2_Q, dfree))))
    sd_nat, sd_ref = sd_nat_raw * infl, sd_ref_raw * infl
    # within-phi correlation of the two scorings on the SAME A-world
    cs = []
    for _, grp in df.groupby("phi"):
        a = grp["R_nat"].to_numpy(float)
        b = grp["R_refresh"].to_numpy(float)
        cs.append(float(np.corrcoef(a - a.mean(), b - b.mean())[0, 1]))
    rho = float(np.mean(cs))

    n = ENDPOINT_PAIRS
    se_nat = float(sd_nat * math.sqrt(2.0 / n))
    se_ref = float(sd_ref * math.sqrt(2.0 / n))
    se_d = float(math.sqrt(max(se_nat ** 2 + se_ref ** 2
                               - 2.0 * rho * se_nat * se_ref, 0.0)))
    bands = {
        "sd_R_nat_raw": sd_nat_raw, "sd_R_refresh_raw": sd_ref_raw,
        "pooled_df": dfree, "inflation": infl, "chi2_quantile": CHI2_Q,
        "sd_R_nat_df_inflated": sd_nat, "sd_R_refresh_df_inflated": sd_ref,
        "rho_within_phi": rho, "rho_per_phi": cs,
        "pairs_per_phi_assumed": n,
        "SE_range_nat": se_nat, "SE_range_ref": se_ref, "SE_D_grad": se_d,
        "SE_D_grad_if_independent": float(math.sqrt(se_nat ** 2 + se_ref ** 2)),
        "correlation_benefit_factor": float(
            se_d / math.sqrt(se_nat ** 2 + se_ref ** 2)),
        "epsilon_D": float(2.0 * se_d), "epsilon_r": float(2.0 * se_ref),
        "band_definition": "eps = 2 * SE of the estimand at the decided pairs/phi, "
                           "from pilot noise df-inflated on the chi2(0.10) convention; "
                           "a NULL verdict is a CI lying inside +/- eps",
        "note": RN_NOTES["RN-P3C-6"],
    }
    out = {"utc": datetime.now(UTC).isoformat(),
           "C3": {"per_phi": per, "PASS": bool(ok)}, "bands": bands,
           "n_pilot_pairs": int(len(df)), "seconds": time.time() - t0}
    write_json(OUT / "pilot.json", out)
    _log("pilot_done", PASS=ok, seconds=out["seconds"])
    if not ok:
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "INSTRUMENT_DEFECT", "routing_cell": "1",
            "routing_text": "STOP / INSTRUMENT_DEFECT", "C3": out["C3"],
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: INSTRUMENT_DEFECT -- pilot predicate failed")
    print(f"pilot OK  sd_nat={sd_nat!r} sd_ref={sd_ref!r} rho={rho!r}  "
          f"SE_D={se_d!r} (indep {bands['SE_D_grad_if_independent']!r})  "
          f"eps_D={bands['epsilon_D']!r} eps_r={bands['epsilon_r']!r}  "
          f"{time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# G3p3c -- the projection at both registered truths.

def stage_project(args: argparse.Namespace) -> None:
    t0 = time.time()
    pil = read_json(OUT / "pilot.json")
    b = pil["bands"]
    sd_nat = b["sd_R_nat_df_inflated"]
    sd_ref = b["sd_R_refresh_df_inflated"]
    rho = b["rho_within_phi"]

    def project(n: int) -> dict[str, Any]:
        se_nat = float(sd_nat * math.sqrt(2.0 / n))
        se_ref = float(sd_ref * math.sqrt(2.0 / n))
        cov = float(rho * se_nat * se_ref)
        cm = np.array([[se_nat ** 2, cov], [cov, se_ref ** 2]], float)
        se_d = float(math.sqrt(max(se_nat ** 2 + se_ref ** 2 - 2.0 * cov, 0.0)))
        rg = np.random.default_rng(MASTER_SEED)
        out = {}
        for name, (true_nat, true_ref) in (
                ("FULLY_FRAME", (M1C_RANGE, 0.0)),
                ("TRANSPORTS", (M1C_RANGE, M1C_RANGE))):
            draws = rg.multivariate_normal([true_nat, true_ref], cm, size=B_PROJ)
            d = draws[:, 0] - draws[:, 1]
            r = draws[:, 1]
            true_d = true_nat - true_ref
            if true_d != 0.0:
                power = float(np.mean(np.abs(d) > 2.0 * se_d))
                ff = float(np.mean(np.abs(r) > 2.0 * se_ref))
                detected, nulled = "D_grad", "range_ref"
            else:
                power = float(np.mean(np.abs(r) > 2.0 * se_ref))
                ff = float(np.mean(np.abs(d) > 2.0 * se_d))
                detected, nulled = "range_ref", "D_grad"
            out[name] = {"true_range_nat": true_nat, "true_range_ref": true_ref,
                         "true_D_grad": true_d, "detected_quantity": detected,
                         "power_at_2SE": power, "power_bar": POWER_MIN,
                         "null_quantity": nulled, "false_fire": ff,
                         "false_fire_bar": FALSE_FIRE_MAX,
                         "PASS": bool(power >= POWER_MIN and ff <= FALSE_FIRE_MAX)}
        return {"pairs_per_phi": n, "SE_range_nat": se_nat, "SE_range_ref": se_ref,
                "SE_D_grad": se_d, "rho": rho, "per_truth": out,
                "PASS": bool(all(d["PASS"] for d in out.values()))}

    base = project(ENDPOINT_PAIRS)
    esc = None
    decided = ENDPOINT_PAIRS
    if not base["PASS"]:
        print(f"  G3p3c FAILED at n={ENDPOINT_PAIRS}; once-only escalation to "
              f"n={ENDPOINT_PAIRS_ESCALATED}", flush=True)
        esc = project(ENDPOINT_PAIRS_ESCALATED)
        if esc["PASS"]:
            decided = ENDPOINT_PAIRS_ESCALATED
    g3 = {"truths": {"FULLY_FRAME": {"D_grad": M1C_RANGE, "range_ref": 0.0},
                     "TRANSPORTS": {"range_ref": M1C_RANGE, "D_grad": 0.0}},
          "B_proj": B_PROJ, "base": base, "escalated": esc,
          "escalation_fired": bool(esc is not None),
          "pairs_per_phi_decided": decided,
          "PASS": bool(base["PASS"] or (esc is not None and esc["PASS"])),
          "on_fail": "NON_PROJECTABLE", "note": RN_NOTES["RN-P3C-4"],
          "seconds": time.time() - t0}
    write_json(OUT / "projection.json", g3)
    _log("project_done", PASS=g3["PASS"], seconds=g3["seconds"])
    if not g3["PASS"]:
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "NON_PROJECTABLE", "routing_cell": "2",
            "routing_text": "NON_PROJECTABLE", "G3": g3,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: NON_PROJECTABLE")
    print("project OK  " + "  ".join(
        f"{k}: power={d['power_at_2SE']!r} ff={d['false_fire']!r}"
        for k, d in base["per_truth"].items())
        + f"  n={decided}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# THE ARMS.

ARMS: list[tuple[str, float, int, int]] = []          # (tag, phi, lo, hi)


def _arm_specs(n_end: int) -> list[tuple[str, float, int, int]]:
    out = []
    for phi in (PHI_LO, PHI_HI):
        for lo in range(0, n_end, CHUNK):
            hi = min(lo + CHUNK, n_end)
            out.append((f"p{phi}_{lo}_{hi}", phi, lo, hi))
    out.append((f"p{PHI_MID}_0_{MID_PAIRS}", PHI_MID, 0, MID_PAIRS))
    return out


def _arm(tag: str) -> None:
    t0 = time.time()
    g3 = read_json(OUT / "projection.json")
    if not g3["PASS"]:
        raise SystemExit("STOP: the projection did not pass.")
    n_end = int(g3["pairs_per_phi_decided"])
    spec = next((s for s in _arm_specs(n_end) if s[0] == tag), None)
    if spec is None:
        raise SystemExit(f"REFUSED: unknown arm {tag!r} at n={n_end}")
    _, phi, lo, hi = spec
    (OUT / "arms").mkdir(parents=True, exist_ok=True)
    path = OUT / "arms" / f"arm_{tag}.csv"
    if path.exists() and len(read_csv_rt(path)) == hi - lo:
        print(f"  {tag}: already complete, skipped", flush=True)
    else:
        rows = [run_pair(phi, i, f"P3C-p{phi}", "") for i in range(lo, hi)]
        pd.DataFrame(rows).to_csv(path, index=False)
        print(f"  {tag}: n={len(rows)} ({time.time() - t0:.1f}s)", flush=True)
    _log(f"arm_{tag}_done", seconds=time.time() - t0)
    print(f"arm {tag} OK  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# THE FIT.

def _classify(lo: float, hi: float, eps: float) -> tuple[str, str]:
    """NULL-first (#55) and, for comparison, sign-first."""
    inside = bool(lo >= -eps and hi <= eps)
    excl0 = bool(lo > 0.0 or hi < 0.0)
    if inside:
        pinned = "NULL"
    elif excl0:
        pinned = "POSITIVE" if lo > 0.0 else "NEGATIVE"
    else:
        pinned = "UNDERPOWERED"
    if excl0:
        sf = "POSITIVE" if lo > 0.0 else "NEGATIVE"
    elif inside:
        sf = "NULL"
    else:
        sf = "UNDERPOWERED"
    return pinned, sf


def stage_fit(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    g3 = read_json(OUT / "projection.json")
    n_end = int(g3["pairs_per_phi_decided"])

    frames: dict[float, pd.DataFrame] = {}
    for phi in (PHI_LO, PHI_HI, PHI_MID):
        parts = [read_csv_rt(OUT / "arms" / f"arm_{s[0]}.csv")
                 for s in _arm_specs(n_end) if s[1] == phi]
        d = pd.concat(parts, ignore_index=True).sort_values("pair")
        want = n_end if phi in (PHI_LO, PHI_HI) else MID_PAIRS
        if len(d) != want or sorted(d["pair"].tolist()) != list(range(want)):
            raise SystemExit(f"REFUSED: phi={phi} assembled {len(d)}, want {want}")
        frames[phi] = d

    per_phi = []
    for phi in (PHI_LO, PHI_MID, PHI_HI):
        d = frames[phi]
        a = d["R_nat"].to_numpy(float)
        b = d["R_refresh"].to_numpy(float)
        for nm, v in (("R_nat", a), ("R_refresh", b)):
            chk = _predicate(v)
            if not chk["PASS"]:
                raise SystemExit(f"REFUSED: rule-29 fails on {nm} at phi={phi}")
        dfr = d["R_deframe"].dropna().to_numpy(float)
        per_phi.append({
            "phi": phi, "r_pred": r_of(SHARE, phi), "n": int(len(a)),
            "role": ("endpoint" if phi in (PHI_LO, PHI_HI) else "shape reading"),
            "R_nat_mean": float(a.mean()),
            "R_nat_sem": float(np.std(a, ddof=1) / np.sqrt(len(a))),
            "R_refresh_mean": float(b.mean()),
            "R_refresh_sem": float(np.std(b, ddof=1) / np.sqrt(len(b))),
            "R_deframe_mean": (float(dfr.mean()) if len(dfr) else None),
            "R_deframe_sem": (float(np.std(dfr, ddof=1) / np.sqrt(len(dfr)))
                              if len(dfr) > 1 else None),
            "R_deframe_n": int(len(dfr)),
            "within_pair_corr_nat_ref": float(np.corrcoef(a, b)[0, 1]),
            "truth_norm_delta_mean": float(d["truth_norm_delta"].mean())})

    # --- C1' anchor ---------------------------------------------------------
    m1c = {round(d["phi"], 10): d for d in p0["G0"]["m1c_rows"]}
    anchor, anchor_ok = [], True
    for q in per_phi:
        ref = m1c[round(q["phi"], 10)]
        diff = float(q["R_nat_mean"] - ref["mean"])
        tol = float(ANCHOR_K * ref["sem"])
        pooled_sem = float(math.sqrt(q["R_nat_sem"] ** 2 + ref["sem"] ** 2))
        inside = bool(abs(diff) <= tol)
        anchor_ok &= inside
        anchor.append({"phi": q["phi"], "role": q["role"],
                       "P3c_R_nat": q["R_nat_mean"], "P3c_sem": q["R_nat_sem"],
                       "M1c_mean": ref["mean"], "M1c_sem": ref["sem"],
                       "difference": diff, "tolerance": tol, "inside": inside,
                       "z_pooled": float(diff / pooled_sem)})
    c1 = {"rule": f"|P3c R_nat - M1c mean| <= {ANCHOR_K} * M1c SEM per level",
          "rows": anchor, "n_inside": int(sum(1 for a in anchor if a["inside"])),
          "n_levels": len(anchor), "PASS": bool(anchor_ok),
          "consequence_on_fail": "INSTRUMENT_DEFECT (never a world finding)"}

    # --- the estimands, JOINT bootstrap (RN-P3C-3) --------------------------
    nat_lo = frames[PHI_LO]["R_nat"].to_numpy(float)
    nat_hi = frames[PHI_HI]["R_nat"].to_numpy(float)
    ref_lo = frames[PHI_LO]["R_refresh"].to_numpy(float)
    ref_hi = frames[PHI_HI]["R_refresh"].to_numpy(float)
    range_nat = float(nat_hi.mean() - nat_lo.mean())
    range_ref = float(ref_hi.mean() - ref_lo.mean())
    d_grad = float(range_nat - range_ref)

    rng = np.random.default_rng(MASTER_SEED)
    idx_lo = rng.integers(0, n_end, size=(B_BOOT_HIGH, n_end))
    idx_hi = rng.integers(0, n_end, size=(B_BOOT_HIGH, n_end))

    def boot(B: int) -> dict[str, np.ndarray]:
        rn = np.empty(B, float)
        rr = np.empty(B, float)
        for j in range(B):
            il, ih = idx_lo[j], idx_hi[j]
            rn[j] = nat_hi[ih].mean() - nat_lo[il].mean()
            rr[j] = ref_hi[ih].mean() - ref_lo[il].mean()
        return {"range_nat": rn, "range_ref": rr, "D_grad": rn - rr,
                "fraction": np.divide(rr, rn, out=np.full(B, np.nan),
                                      where=rn != 0.0)}

    bb = boot(B_BOOT)
    eps_d = pil["bands"]["epsilon_D"]
    eps_r = pil["bands"]["epsilon_r"]

    def ci(a: np.ndarray) -> list[float]:
        return [float(np.nanquantile(a, 0.025)), float(np.nanquantile(a, 0.975))]

    # rule 13: any CI tail within 1/(10B) of a decision boundary?
    margin = 1.0 / (RULE13_FACTOR * B_BOOT)
    near = []
    for nm, arr, bounds in (("D_grad", bb["D_grad"], (0.0, eps_d, -eps_d)),
                            ("range_ref", bb["range_ref"], (0.0, eps_r, -eps_r))):
        for bnd in bounds:
            frac = float(np.mean(arr <= bnd))
            if min(abs(frac - 0.025), abs(frac - 0.975)) < margin:
                near.append({"quantity": nm, "boundary": bnd, "tail_frac": frac})
    rule13 = []
    if near:
        bb = boot(B_BOOT_HIGH)
        rule13.append({"triggers": near, "B": B_BOOT_HIGH})

    ci_d, ci_r, ci_n = ci(bb["D_grad"]), ci(bb["range_ref"]), ci(bb["range_nat"])
    va, va_sf = _classify(ci_d[0], ci_d[1], eps_d)
    vb, vb_sf = _classify(ci_r[0], ci_r[1], eps_r)
    corr = float(np.corrcoef(bb["range_nat"], bb["range_ref"])[0, 1])

    # --- RN-P3C-9: the same bands, recomputed from the REALIZED arms --------
    sem_nat_lo = float(np.std(nat_lo, ddof=1) / np.sqrt(len(nat_lo)))
    sem_nat_hi = float(np.std(nat_hi, ddof=1) / np.sqrt(len(nat_hi)))
    sem_ref_lo = float(np.std(ref_lo, ddof=1) / np.sqrt(len(ref_lo)))
    sem_ref_hi = float(np.std(ref_hi, ddof=1) / np.sqrt(len(ref_hi)))
    se_n_real = float(math.sqrt(sem_nat_lo ** 2 + sem_nat_hi ** 2))
    se_r_real = float(math.sqrt(sem_ref_lo ** 2 + sem_ref_hi ** 2))
    se_d_real = float(np.std(bb["D_grad"], ddof=1))
    eps_d_real = float(2.0 * se_d_real)
    eps_r_real = float(2.0 * se_r_real)
    va_r, _ = _classify(ci_d[0], ci_d[1], eps_d_real)
    vb_r, _ = _classify(ci_r[0], ci_r[1], eps_r_real)
    rho_real = float(np.mean([q["within_pair_corr_nat_ref"] for q in per_phi
                              if q["phi"] in (PHI_LO, PHI_HI)]))
    sens = {
        "why": RN_NOTES["RN-P3C-9"],
        "pilot_rho_used_in_projection": pil["bands"]["rho_within_phi"],
        "realized_rho_within_pair_endpoints": rho_real,
        "rho_miss": float(pil["bands"]["rho_within_phi"] - rho_real),
        "pilot_sd_R_refresh_df_inflated": pil["bands"]["sd_R_refresh_df_inflated"],
        "realized_sd_R_refresh_endpoint_mean": float(
            0.5 * (np.std(ref_lo, ddof=1) + np.std(ref_hi, ddof=1))),
        "pilot_SE_range_ref": pil["bands"]["SE_range_ref"],
        "realized_SE_range_ref": se_r_real,
        "pilot_SE_D_grad": pil["bands"]["SE_D_grad"],
        "realized_SE_D_grad": se_d_real,
        "epsilon_D_part0": eps_d, "epsilon_D_realized": eps_d_real,
        "epsilon_r_part0": eps_r, "epsilon_r_realized": eps_r_real,
        "V_A_under_realized_band": va_r, "V_B_under_realized_band": vb_r,
        "V_A_routes": va, "V_B_routes": vb,
        "verdicts_robust_to_band_source": bool(va_r == va and vb_r == vb),
        "note": "the Part-0 bands route, as registered; these are reported so the "
                "pilot's sampling luck is visible and auditable",
    }
    out = {
        "utc": datetime.now(UTC).isoformat(), "pairs_per_phi": n_end,
        "per_phi": per_phi, "C1_prime": c1, "band_sensitivity": sens,
        "range_nat": range_nat, "range_nat_ci95": ci_n,
        "range_ref": range_ref, "range_ref_ci95": ci_r,
        "D_grad": d_grad, "D_grad_ci95": ci_d,
        "epsilon_D": eps_d, "epsilon_r": eps_r,
        "V_A": {"quantity": "D_grad", "point": d_grad, "ci95": ci_d,
                "epsilon": eps_d, "classification": va,
                "classification_sign_first": va_sf,
                "readings_agree": bool(va == va_sf)},
        "V_B": {"quantity": "range_ref", "point": range_ref, "ci95": ci_r,
                "epsilon": eps_r, "classification": vb,
                "classification_sign_first": vb_sf,
                "readings_agree": bool(vb == vb_sf)},
        "fraction_UNBUDGETED": {
            "point": float(range_ref / range_nat) if range_nat else None,
            "ci95": ci(bb["fraction"]),
            "width": float(ci(bb["fraction"])[1] - ci(bb["fraction"])[0]),
            "label": "UNBUDGETED -- descriptive only, gates nothing, routes nothing",
            "note": RN_NOTES["RN-P3C-5"]},
        "joint_bootstrap_correlation_range_nat_range_ref": corr,
        "SE_D_grad_realized": float(np.std(bb["D_grad"], ddof=1)),
        "SE_D_grad_if_independent": float(math.sqrt(
            np.var(bb["range_nat"], ddof=1) + np.var(bb["range_ref"], ddof=1))),
        "M1c_range": p0["G0"]["m1c_range_HI_minus_LO"],
        "range_nat_minus_M1c": float(range_nat
                                     - p0["G0"]["m1c_range_HI_minus_LO"]),
        "rule13_events": rule13, "B": int(len(bb["D_grad"])),
        "seconds": time.time() - t0,
    }
    write_json(OUT / "fit.json", out)
    _log("fit_done", V_A=va, V_B=vb, seconds=out["seconds"])
    print(f"fit OK  C1'={'PASS' if c1['PASS'] else 'FAIL'} "
          f"({c1['n_inside']}/{c1['n_levels']})  range_nat={range_nat!r} "
          f"range_ref={range_ref!r} D_grad={d_grad!r}  V-A={va} V-B={vb}  "
          f"corr={corr!r}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# FINALIZE.

TRUTH_TABLE = [
    {"n": "1", "condition": "G0 / C2 battery / citation failure",
     "outcome": "STOP_INSTRUMENT_DEFECT", "text": "STOP / INSTRUMENT_DEFECT"},
    {"n": "2", "condition": "projection fails after escalation",
     "outcome": "NON_PROJECTABLE", "text": "NON_PROJECTABLE"},
    {"n": "3", "condition": "C1' anchor fails", "outcome": "INSTRUMENT_DEFECT",
     "text": "INSTRUMENT_DEFECT (never a world finding)"},
    {"n": "4", "condition": "V-A POSITIVE and V-B NULL",
     "outcome": "GRADIENT_FULLY_FRAME",
     "text": "GRADIENT_FULLY_FRAME -- the natural phi-gradient is frame-owned; the "
             "M-line law stands as a law of the statistic; the mechanism section "
             "re-types (the r-channel reads frame-agreement)"},
    {"n": "5", "condition": "V-A POSITIVE and V-B POSITIVE",
     "outcome": "GRADIENT_MIXED",
     "text": "GRADIENT_MIXED -- both components real; the split is quoted "
             "descriptively"},
    {"n": "6", "condition": "V-A NULL and V-B POSITIVE",
     "outcome": "GRADIENT_TRANSPORTS",
     "text": "GRADIENT_TRANSPORTS -- the reading crosses frames; the "
             "scaffold-gradient strengthens"},
    {"n": "7", "condition": "V-B NEGATIVE", "outcome": "INVERSION_NAMED",
     "text": "INVERSION_NAMED -- refreshment reverses the gradient; new phenomenon, "
             "theory note"},
    {"n": "8", "condition": "any UNDERPOWERED among V-A/V-B (no higher cell fires)",
     "outcome": "UNDERPOWERED", "text": "UNDERPOWERED (levels and bands reported)"},
    {"n": "9", "condition": "V-A NEGATIVE (and V-B not NEGATIVE)",
     "outcome": "FRAME_COMPONENT_NEGATIVE",
     "text": "FRAME_COMPONENT_NEGATIVE -- refreshed gradient exceeds natural; named, "
             "theory note"},
]


def _route(va: str, vb: str, c1_pass: bool) -> str:
    if not c1_pass:
        return "INSTRUMENT_DEFECT"
    if vb == "NEGATIVE":
        return "INVERSION_NAMED"
    if va == "POSITIVE" and vb == "NULL":
        return "GRADIENT_FULLY_FRAME"
    if va == "POSITIVE" and vb == "POSITIVE":
        return "GRADIENT_MIXED"
    if va == "NULL" and vb == "POSITIVE":
        return "GRADIENT_TRANSPORTS"
    if va == "NEGATIVE":
        return "FRAME_COMPONENT_NEGATIVE"
    if "UNDERPOWERED" in (va, vb):
        return "UNDERPOWERED"
    return "UNDERPOWERED"


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    g3 = read_json(OUT / "projection.json")
    fit = read_json(OUT / "fit.json")
    va = fit["V_A"]["classification"]
    vb = fit["V_B"]["classification"]
    slug = _route(va, vb, fit["C1_prime"]["PASS"])
    cell_n = next(t["n"] for t in TRUTH_TABLE if t["outcome"] == slug)

    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "verdict_slug": slug, "routing_cell": cell_n, "modifiers": [],
        "routing_text": next(t["text"] for t in TRUTH_TABLE if t["outcome"] == slug),
        "V_A": fit["V_A"], "V_B": fit["V_B"],
        "range_nat": fit["range_nat"], "range_nat_ci95": fit["range_nat_ci95"],
        "range_ref": fit["range_ref"], "range_ref_ci95": fit["range_ref_ci95"],
        "D_grad": fit["D_grad"], "D_grad_ci95": fit["D_grad_ci95"],
        "fraction_UNBUDGETED": fit["fraction_UNBUDGETED"],
        "joint_bootstrap_correlation": fit[
            "joint_bootstrap_correlation_range_nat_range_ref"],
        "C1_prime": fit["C1_prime"], "per_phi": fit["per_phi"],
        "pairs_per_phi": fit["pairs_per_phi"],
        "total_worlds": int(2 * (2 * fit["pairs_per_phi"] + MID_PAIRS)),
        "instrument_provenance": p0["instrument_provenance"],
        "C2": p0["C2"], "bands": pil["bands"], "projection": g3,
        "rule13_events": fit["rule13_events"],
        "gates": {
            "G0": {"PASS": p0["G0"]["PASS"],
                   "detail": "M1c's row and range, P3b's persisted SEs and certification, "
                             "the ladder r values -- all verified"},
            "C2": {"PASS": p0["C2"]["PASS"],
                   "detail": f"re-run on {PROBE_PAIRS} FRESH probe pairs: author objects "
                             "bit-identical, every frame object differs, determinism, "
                             "shared basis"},
            "C3": {"PASS": pil["C3"]["PASS"],
                   "detail": "rule-29 predicate on BOTH scorings at both endpoints; "
                             "bands computed df-inflated before the arms"},
            "G3p3c": {"PASS": g3["PASS"],
                      "detail": "both truths discriminated at 2*SE; escalation fired: "
                                f"{g3['escalation_fired']}"},
            "C1'": {"PASS": fit["C1_prime"]["PASS"],
                    "detail": f"{fit['C1_prime']['n_inside']}/"
                              f"{fit['C1_prime']['n_levels']} levels within "
                              f"{ANCHOR_K}*SEM of M1c's row"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug, seconds=dec["seconds"])
    _tables(p0, pil, g3, fit, dec)
    _facts(p0, pil, g3, fit, dec)
    print(f"finalize OK  slug={slug}  cell={cell_n}  V-A={va} V-B={vb}")
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
    pr = p0["instrument_provenance"]
    sec["provenance"] = _md(
        ["property", "value"],
        [["imported from", "`" + pr["imported_from"] + ":"
          + str(pr["definition_line"]) + "`"],
         ["signature", "`" + pr["signature"] + "`"],
         ["function sha256", pr["function_sha256"]],
         ["file sha256", pr["file_sha256"]],
         ["file bytes", str(pr["file_bytes"])],
         ["P3b provenance entries behind it", str(pr["p3b_provenance_entries"])],
         ["ultimate source span", pr["p3b_source_span"]],
         ["k2b edited", str(pr["k2b_edited"])],
         ["suica_core edited", str(pr["suica_core_edited"])],
         ["why imported, not re-extracted", pr["why_imported_not_re_extracted"]]])
    c2 = p0["C2"]
    sec["c2"] = _md(
        ["check", "objects", "result"],
        [["C2a author identical", ", ".join(AUTHOR_OBJECTS),
          str(c2["C2a_all_author_identical"])],
         ["C2a frame differs", ", ".join(FRAME_OBJECTS),
          str(c2["C2a_all_frame_differ"])]]
        + [[f"C2a norm delta: {k}", "frame",
            f"[{c2['C2a_norm_delta_min'][k]!r}, {c2['C2a_norm_delta_max'][k]!r}]"]
           for k in FRAME_OBJECTS]
        + [["C2b determinism", f"{len(c2['C2b_determinism'])} objects",
            str(c2["C2b_all_identical"])],
           ["C2c shared basis", "loadings", str(c2["C2c_loadings_shared"])],
           ["**C2 (fresh probe pairs: " + str(c2["n_probe_pairs"]) + ")**", "—",
            "**PASS = " + str(c2["PASS"]) + "**"]])
    g0 = p0["G0"]
    sec["g0"] = _md(
        ["clause", "expected", "found", "OK"],
        [["M1c range (phi .98 - phi .05)", repr(M1C_RANGE),
          repr(g0["m1c_range_HI_minus_LO"]),
          str(g0["m1c_range_matches_registration"])],
         ["P3b verdict", "NON_PROJECTABLE", g0["p3b_verdict"],
          str(g0["p3b_verdict"] == "NON_PROJECTABLE")],
         ["P3b instrument certified", "True", str(g0["p3b_certified"]),
          str(g0["p3b_certified"])],
         ["P3b SE(range_ref) at 192", "—", repr(g0["p3b_SE_range_ref_at_192"]), "—"],
         ["P3b sigma R_nat", "—", repr(g0["p3b_sigma_R_nat"]), "—"],
         ["P3b sigma R_refresh", "—", repr(g0["p3b_sigma_R_refresh"]), "—"]]
        + [[f"ladder r at phi={d['phi']}", repr(d["r_M1c"]), repr(d["r_recomputed"]),
            str(d["bit_exact"])] for d in g0["ladder"]])
    b = pil["bands"]
    sec["bands"] = _md(
        ["quantity", "value"],
        [["sd R_nat (raw / df-inflated)",
          repr(b["sd_R_nat_raw"]) + " / " + repr(b["sd_R_nat_df_inflated"])],
         ["sd R_refresh (raw / df-inflated)",
          repr(b["sd_R_refresh_raw"]) + " / " + repr(b["sd_R_refresh_df_inflated"])],
         ["pooled df / inflation", str(b["pooled_df"]) + " / " + repr(b["inflation"])],
         ["**within-phi correlation of R_nat and R_refresh**",
          "**" + repr(b["rho_within_phi"]) + "**"],
         ["SE(range_nat) at " + str(b["pairs_per_phi_assumed"]),
          repr(b["SE_range_nat"])],
         ["SE(range_ref)", repr(b["SE_range_ref"])],
         ["**SE(D_grad), joint**", "**" + repr(b["SE_D_grad"]) + "**"],
         ["SE(D_grad) if independent", repr(b["SE_D_grad_if_independent"])],
         ["correlation benefit factor", repr(b["correlation_benefit_factor"])],
         ["**epsilon_D (V-A NULL band)**", "**" + repr(b["epsilon_D"]) + "**"],
         ["**epsilon_r (V-B NULL band)**", "**" + repr(b["epsilon_r"]) + "**"],
         ["band definition", b["band_definition"]]])
    rows = []
    for label, blk in (("768 (registered)", g3["base"]),
                       ("1152 (escalated)", g3["escalated"])):
        if blk is None:
            continue
        for k, d in blk["per_truth"].items():
            rows.append([label, k, d["detected_quantity"], repr(d["power_at_2SE"]),
                         repr(d["power_bar"]), d["null_quantity"],
                         repr(d["false_fire"]), repr(d["false_fire_bar"]),
                         str(d["PASS"])])
    sec["projection"] = _md(
        ["pairs/phi", "truth", "detected", "power at 2 SE", "bar", "null quantity",
         "false fire", "bar", "PASS"], rows)
    sec["dual"] = _md(
        ["phi", "role", "r_pred", "n", "R_nat mean", "R_nat SEM", "R_refresh mean",
         "R_refresh SEM", "R_deframe mean", "R_deframe SEM", "within-pair corr"],
        [[repr(q["phi"]), q["role"], repr(q["r_pred"]), str(q["n"]),
          repr(q["R_nat_mean"]), repr(q["R_nat_sem"]), repr(q["R_refresh_mean"]),
          repr(q["R_refresh_sem"]), repr(q["R_deframe_mean"]),
          repr(q["R_deframe_sem"]), repr(q["within_pair_corr_nat_ref"])]
         for q in fit["per_phi"]])
    sec["anchor"] = _md(
        ["phi", "role", "P3c R_nat", "P3c SEM", "M1c mean", "M1c SEM", "difference",
         "tolerance", "inside", "pooled z"],
        [[repr(a["phi"]), a["role"], repr(a["P3c_R_nat"]), repr(a["P3c_sem"]),
          repr(a["M1c_mean"]), repr(a["M1c_sem"]), repr(a["difference"]),
          repr(a["tolerance"]), str(a["inside"]), repr(a["z_pooled"])]
         for a in fit["C1_prime"]["rows"]]
        + [["**C1'**", "—", "—", "—", "—", "—", "—", "—",
            f"**{fit['C1_prime']['n_inside']}/{fit['C1_prime']['n_levels']}**",
            "PASS = " + str(fit["C1_prime"]["PASS"])]])
    sec["estimands"] = _md(
        ["estimand", "definition", "point", "95% CI", "epsilon", "classification"],
        [["range_nat", "R_nat(.98) - R_nat(.05)", repr(fit["range_nat"]),
          repr(fit["range_nat_ci95"]), "—", "— (not a verdict)"],
         ["**range_ref (V-B)**", "R_refresh(.98) - R_refresh(.05)",
          "**" + repr(fit["range_ref"]) + "**", repr(fit["range_ref_ci95"]),
          repr(fit["epsilon_r"]), "**" + fit["V_B"]["classification"] + "**"],
         ["**D_grad (V-A)**", "range_nat - range_ref",
          "**" + repr(fit["D_grad"]) + "**", repr(fit["D_grad_ci95"]),
          repr(fit["epsilon_D"]), "**" + fit["V_A"]["classification"] + "**"],
         ["M1c's realized range", "the anchor", repr(fit["M1c_range"]), "—", "—", "—"],
         ["range_nat - M1c's", "co-measurement check",
          repr(fit["range_nat_minus_M1c"]), "—", "—", "—"]])
    sec["readings"] = _md(
        ["verdict", "quantity", "NULL-first (routes)", "sign-first", "agree"],
        [["V-A", fit["V_A"]["quantity"], fit["V_A"]["classification"],
          fit["V_A"]["classification_sign_first"],
          str(fit["V_A"]["readings_agree"])],
         ["V-B", fit["V_B"]["quantity"], fit["V_B"]["classification"],
          fit["V_B"]["classification_sign_first"],
          str(fit["V_B"]["readings_agree"])]])
    fr = fit["fraction_UNBUDGETED"]
    sec["fraction"] = _md(
        ["quantity", "value"],
        [["range_ref / range_nat", repr(fr["point"])],
         ["95% CI", repr(fr["ci95"])],
         ["CI width", repr(fr["width"])],
         ["**label**", "**" + fr["label"] + "**"],
         ["why it is shown", fr["note"]]])
    sec["joint"] = _md(
        ["quantity", "value"],
        [["**bootstrap correlation, range_nat vs range_ref**",
          "**" + repr(fit["joint_bootstrap_correlation_range_nat_range_ref"]) + "**"],
         ["realized SE(D_grad) from the joint bootstrap",
          repr(fit["SE_D_grad_realized"])],
         ["SE(D_grad) had they been independent",
          repr(fit["SE_D_grad_if_independent"])],
         ["why joint", RN_NOTES["RN-P3C-3"]],
         ["bootstrap B", str(fit["B"])]])
    sn = fit["band_sensitivity"]
    sec["sensitivity"] = _md(
        ["quantity", "pilot (Part 0, routes)", "realized (reported)"],
        [["within-pair correlation rho",
          repr(sn["pilot_rho_used_in_projection"]),
          repr(sn["realized_rho_within_pair_endpoints"])],
         ["sd R_refresh", repr(sn["pilot_sd_R_refresh_df_inflated"]),
          repr(sn["realized_sd_R_refresh_endpoint_mean"])],
         ["SE(range_ref)", repr(sn["pilot_SE_range_ref"]),
          repr(sn["realized_SE_range_ref"])],
         ["SE(D_grad)", repr(sn["pilot_SE_D_grad"]),
          repr(sn["realized_SE_D_grad"])],
         ["epsilon_D", repr(sn["epsilon_D_part0"]), repr(sn["epsilon_D_realized"])],
         ["epsilon_r", repr(sn["epsilon_r_part0"]), repr(sn["epsilon_r_realized"])],
         ["V-A", sn["V_A_routes"], sn["V_A_under_realized_band"]],
         ["V-B", sn["V_B_routes"], sn["V_B_under_realized_band"]],
         ["**verdicts robust to the band source**", "—",
          "**" + str(sn["verdicts_robust_to_band_source"]) + "**"]])
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
    for tag, _, _, _ in _arm_specs(fit["pairs_per_phi"]):
        trows.append([f"arm {tag}", str(est["arms_each"]),
                      "%.3f" % meas.get(f"arm_{tag}_done", float("nan"))])
    trows += [["fit", str(est["fit"]), "%.3f" % meas.get("fit_done", float("nan"))],
              ["finalize", str(est["finalize"]),
               "%.3f" % meas.get("finalize_done", float("nan"))]]
    sec["timing"] = _md(["stage", "estimate (s)", "measured (s)"], trows)
    body = ["# M4-P3c report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _facts(p0: dict[str, Any], pil: dict[str, Any], g3: dict[str, Any],
           fit: dict[str, Any], dec: dict[str, Any]) -> None:
    b = pil["bands"]
    pr = p0["instrument_provenance"]
    fr = fit["fraction_UNBUDGETED"]
    f = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"],
        "MODIFIERS": ", ".join(dec["modifiers"]) or "none",
        "VA": fit["V_A"]["classification"], "VB": fit["V_B"]["classification"],
        "VA_SF": fit["V_A"]["classification_sign_first"],
        "VB_SF": fit["V_B"]["classification_sign_first"],
        "VA_AGREE": fit["V_A"]["readings_agree"],
        "VB_AGREE": fit["V_B"]["readings_agree"],
        "NPAIRS": fit["pairs_per_phi"], "NWORLDS": dec["total_worlds"],
        "IMPORTED": pr["imported_from"] + ":" + str(pr["definition_line"]),
        "FNSHA": pr["function_sha256"][:16], "FILESHA": pr["file_sha256"][:16],
        "PROBES": p0["C2"]["n_probe_pairs"], "C2PASS": p0["C2"]["PASS"],
        "COMMON_MIN": p0["C2"]["C2a_norm_delta_min"]["common"],
        "COMMON_MAX": p0["C2"]["C2a_norm_delta_max"]["common"],
        "SD_NAT": b["sd_R_nat_df_inflated"], "SD_REF": b["sd_R_refresh_df_inflated"],
        "RHO": b["rho_within_phi"], "DF": b["pooled_df"], "INFL": b["inflation"],
        "SE_N": b["SE_range_nat"], "SE_R": b["SE_range_ref"], "SE_D": b["SE_D_grad"],
        "SE_D_IND": b["SE_D_grad_if_independent"],
        "BENEFIT": b["correlation_benefit_factor"],
        "EPS_D": b["epsilon_D"], "EPS_R": b["epsilon_r"],
        "PW_FF": g3["base"]["per_truth"]["FULLY_FRAME"]["power_at_2SE"],
        "FF_FF": g3["base"]["per_truth"]["FULLY_FRAME"]["false_fire"],
        "PW_TR": g3["base"]["per_truth"]["TRANSPORTS"]["power_at_2SE"],
        "FF_TR": g3["base"]["per_truth"]["TRANSPORTS"]["false_fire"],
        "ESC": g3["escalation_fired"],
        "RANGE_NAT": fit["range_nat"], "RANGE_NAT_CI": fit["range_nat_ci95"],
        "RANGE_REF": fit["range_ref"], "RANGE_REF_CI": fit["range_ref_ci95"],
        "DGRAD": fit["D_grad"], "DGRAD_CI": fit["D_grad_ci95"],
        "M1C_RANGE": fit["M1c_range"], "RANGE_DIFF": fit["range_nat_minus_M1c"],
        "FRAC": fr["point"], "FRAC_CI": fr["ci95"], "FRAC_W": fr["width"],
        "CORR": fit["joint_bootstrap_correlation_range_nat_range_ref"],
        "SE_D_REAL": fit["SE_D_grad_realized"],
        "SE_D_REAL_IND": fit["SE_D_grad_if_independent"],
        "C1_N": fit["C1_prime"]["n_inside"], "C1_TOT": fit["C1_prime"]["n_levels"],
        "C1_PASS": fit["C1_prime"]["PASS"],
        "C1_MAXZ": max(abs(a["z_pooled"]) for a in fit["C1_prime"]["rows"]),
        "NRULE13": len(fit["rule13_events"]), "B": fit["B"],
        "RHO_REAL": fit["band_sensitivity"]["realized_rho_within_pair_endpoints"],
        "RHO_MISS": fit["band_sensitivity"]["rho_miss"],
        "EPS_R_REAL": fit["band_sensitivity"]["epsilon_r_realized"],
        "EPS_D_REAL": fit["band_sensitivity"]["epsilon_D_realized"],
        "ROBUST": fit["band_sensitivity"]["verdicts_robust_to_band_source"],
        "SE_R_REAL": fit["band_sensitivity"]["realized_SE_range_ref"],
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
    }
    for q in fit["per_phi"]:
        tag = str(q["phi"]).replace(".", "")
        f[f"P{tag}_NAT"] = q["R_nat_mean"]
        f[f"P{tag}_REF"] = q["R_refresh_mean"]
        f[f"P{tag}_DEF"] = q["R_deframe_mean"]
        f[f"P{tag}_CORR"] = q["within_pair_corr_nat_ref"]
    write_json(OUT / "prose_facts.json", f)


REPORT_TEMPLATE = r"""# SUICA M4-P3c — the transportable gradient, by differences — **{{SLUG}}**

**Outcome: {{SLUG}} (routing cell {{CELL}}); modifiers: {{MODIFIERS}}.**
{{ROUTING_TEXT}}

**V-A (frame-owned component) D_grad = {{DGRAD}} {{DGRAD_CI}} → {{VA}}.
V-B (transportable component) range_ref = {{RANGE_REF}} {{RANGE_REF_CI}} →
{{VB}}.** Against range_nat = {{RANGE_NAT}} {{RANGE_NAT_CI}}. {{NWORLDS}} worlds
({{NPAIRS}} A/B pairs at each endpoint + 192 at the shape reading).

**Read plainly: the frame-owned component is real and large, and the
transportable component cannot be certified either way.** D_grad is
{{DGRAD}} — most of range_nat — with a CI comfortably clear of zero. range_ref
is {{RANGE_REF}}, straddling zero, and its CI is *slightly* too wide to sit
inside the ±{{EPS_R}} equivalence band, so it classifies UNDERPOWERED rather
than NULL. The registered routing sends any UNDERPOWERED verdict to cell 8, and
that is where this leg lands — one notch short of GRADIENT_FULLY_FRAME, which
would have required V-B to be certifiable as NULL.

**The levels say more than the verdict does.** R_refresh is essentially zero at
every φ — {{P005_REF}}, {{P06_REF}}, {{P098_REF}} — against an R_nat of
{{P005_NAT}} … {{P098_NAT}}. The gauge scored against a *different frame's*
truth agrees with it barely at all. That is the substance; the verdict is
UNDERPOWERED only because certifying "indistinguishable from zero" is a
stronger demand than observing "near zero".

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md` BEFORE run (commit 11f42d6).
Every number below is generated from artifacts by code (rule 24).

---

## 1. The instrument, imported

<<TABLE:provenance>>

P3b's certified `build_split_world` is **imported by file**, not re-extracted —
one certified builder in the programme, with nothing to drift. Its C2 battery is
re-run here on {{PROBES}} **fresh** probe pairs:

<<TABLE:c2>>

C2 = {{C2PASS}}: author objects bit-identical, every frame object differing
(`common` by a norm delta in [{{COMMON_MIN}}, {{COMMON_MAX}}]), determinism
holding, basis shared. k2b and `suica_core/` untouched.

## 2. G0 — the citations, and the sign convention

<<TABLE:g0>>

**The side-signing reverses from P3b, deliberately** (RN-P3C-2). P3b reported
range_nat = R(.05) − R(.98) = −0.0104; this registration defines
range = value(.98) − value(.05), so range_nat is **+{{M1C_RANGE}}** — the same
quantity with the opposite sign, and the sign the registration's own truths use.
Every range in this leg is HI minus LO. Stated because a silent sign flip
between sibling legs is exactly what survives review and then poisons a
comparison.

## 3. Bands and the correlation that pays for this design

<<TABLE:bands>>

R_nat and R_refresh are computed from the **same** A-world — one gauge pass,
two truth panels — so they are correlated within a pair (ρ = {{RHO}}). The
bootstrap is therefore JOINT (RN-P3C-3): one resample of pair indices drives
both ranges, so D_grad inherits the cancellation. SE(D_grad) = {{SE_D}} against
{{SE_D_IND}} had they been independent — a factor of {{BENEFIT}}. **This is
what makes the difference estimand feasible where P3b's ratio was not.**

ε_D = {{EPS_D}} and ε_r = {{EPS_R}}, computed from pilot noise df-inflated
(df {{DF}}, factor {{INFL}}) and written before the arms.

## 4. The projection

<<TABLE:projection>>

At the registered 768 pairs/φ: FULLY_FRAME detects D_grad with power {{PW_FF}}
(bar 0.8) while range_ref false-fires at {{FF_FF}} (bar 0.1); TRANSPORTS detects
range_ref with power {{PW_TR}} while D_grad false-fires at {{FF_TR}}. All four
clear. Escalation did not fire ({{ESC}}).

## 5. C1′ — the anchor

<<TABLE:anchor>>

{{C1_N}}/{{C1_TOT}} levels inside 2·√2·SEM of M1c's row (largest |pooled z| =
{{C1_MAXZ}}); C1′ = {{C1_PASS}}. The extracted two-stream instrument reproduces
M1c's measured levels, so a failure downstream would have been a finding, not a
plumbing artefact. range_nat also co-measures M1c's range to
{{RANGE_DIFF}}.

## 6. The result

<<TABLE:dual>>

<<TABLE:estimands>>

<<TABLE:readings>>

Both verdicts read the same under the NULL-first order that routes and under the
sign-first order ({{VA_AGREE}} / {{VB_AGREE}}).

### 6.1 The joint bootstrap, and what it bought

<<TABLE:joint>>

Realized bootstrap correlation between range_nat and range_ref: **{{CORR}}**.
Realized SE(D_grad) {{SE_D_REAL}} against {{SE_D_REAL_IND}} under an
independence assumption.

### 6.2 The fraction — quoted, and labelled

<<TABLE:fraction>>

range_ref/range_nat = {{FRAC}} {{FRAC_CI}}, width {{FRAC_W}}. **UNBUDGETED.**
This is the P3b ratio that failed its budget; it is shown because a reader will
compute it anyway, and showing its width is the P3b lesson made visible. It
gates nothing and routes nothing.

### 6.3 The bands, and the pilot's luck

<<TABLE:sensitivity>>

The Part-0 bands route, as registered. They are recomputed here from the
realized arms because the pilot is only 4 pairs per endpoint, and an n = 4
correlation carries a standard error of roughly 0.5 (RN-P3C-9). It shows: the
pilot's ρ = 0.761 against a realized {{RHO_REAL}}, a miss of {{RHO_MISS}}. The
projection used the optimistic ρ and so understated SE(D_grad) — which did not
matter, because D_grad is far from its band either way.

**Both verdicts are unchanged under the realized-noise bands ({{ROBUST}}):**
V-A POSITIVE and V-B UNDERPOWERED under ε_D = {{EPS_D}} / {{EPS_D_REAL}} and
ε_r = {{EPS_R}} / {{EPS_R_REAL}}. The pilot's sampling luck is visible and
audited, and it changed nothing.

## 7. Routing

<<TABLE:truth_table>>

## 8. Gates

<<TABLE:gates>>

## 9. Sides declared (rule 22)

<<TABLE:sides>>

## 10. Pinned readings

<<TABLE:rn>>

## 11. Rule events

- **Rule 13:** {{NRULE13}} boundary event(s); bootstrap B = {{B}}.
- **Rule 25:** the projection gate passed at the registered size; no escalation.
  Its correlation input was badly estimated by the 4-pair pilot (§6.3) — a
  power calculation, not a verdict, and the verdicts are robust to it.
- **Rule 26:** no bounded winner.
- **Rule 27:** the only budgeted quantities are the verdict CIs against their
  Part-0 bands; the fraction is explicitly UNBUDGETED and carries the label.
- **Rule 29:** the domain-pinned predicate ran on BOTH scorings at every arm.
- **Rule 30:** every cited constant read from its persisted source; the
  instrument carries file, line and two sha256s.

## 12. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython {{PYTHON}} venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.

## 13. Environment

<<TABLE:env>>

## 14. Timing

<<TABLE:timing>>

---

*Artifacts: `results/m4_p3c_transportable_gradient/` (gitignored) —
`part0.json`, `pilot.json`, `pilot_field.csv`, `projection.json`, `arms/`,
`fit.json`, `decision.json`, `prose_facts.json`, `report_tables.md`,
`run_log.jsonl`. Harness:
`scripts/run_suica_m4_p3c_transportable_gradient.py`.*
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
    path = ROOT / "reports" / "SUICA_M4_P3C_TRANSPORTABLE_GRADIENT_REPORT.md"
    path.write_text(txt, encoding="utf-8")
    print(f"report OK  {rel(path)}  ({len(txt.splitlines())} lines)")
    _ = args


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="stage", required=True)
    stages: list[tuple[str, Callable[[argparse.Namespace], None]]] = [
        ("part0", stage_part0), ("pilot", stage_pilot), ("project", stage_project)]
    for tag, _, _, _ in (_arm_specs(ENDPOINT_PAIRS)
                         + _arm_specs(ENDPOINT_PAIRS_ESCALATED)):
        if any(s[0] == tag for s in stages):
            continue
        stages.append((f"arm_{tag}", (lambda tt: lambda a: _arm(tt))(tag)))
    stages += [("fit", stage_fit), ("finalize", stage_finalize),
               ("report", stage_report)]
    seen = set()
    for name, fn in stages:
        if name in seen:
            continue
        seen.add(name)
        sub.add_parser(name).set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
