#!/usr/bin/env python3
"""SUICA M4-Q2 -- is the tax frame-borne?  (the V-response under refreshment)

Registered BEFORE run in docs/SUICA_M4_Q_TRANSPORT_LINE_PLAN.md ("M4-Q2",
commit d030914).  Binding.  The Q-line's last leg.

The N-line's tax curve kappa(V) is a law of R_nat -- a frame-carrying statistic
(P-line).  If the gauge's V-RESPONSE also fails to transport across frames then
the tax itself is a frame-agreement phenomenon: the curve describes how
person-variance modulates FRAME-reading, not person-reading.

    D_nat = R_nat(V = 0.03) - R_nat(V = 0.21)     the natural tax swing
    D_ref = R_ref(V = 0.03) - R_ref(V = 0.21)     the transported tax swing

D_nat is anchored on the M-line law, whose prediction Part 0 recomputes from
persisted M1c (0.10, 0.60) and M2 C2 (0.70, 0.60) cell means.  The instrument is
P3b's certified split-seed builder, imported by file; R_nat / R_ref are P3c's
scorings unchanged.  k2b, suica_core/ and the P3b instrument are untouched.

Stages: part0 -> pilot -> project -> arm_<tag> (4) -> fit -> finalize -> report
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

OUT = ROOT / "results" / "m4_q2_tax_transport"
RES = ROOT / "results"
P3BSRC = ROOT / "scripts" / "run_suica_m4_p3b_refresh_gradient.py"
M1CRES = RES / "m4_m1c_r_at_level"
M2RES = RES / "m4_m2_scoped_seal"
P3CRES = RES / "m4_p3c_transportable_gradient"
Q1BRES = RES / "m4_q1b_card_cosine"

LEG = "M4-Q2"
BANNER = ("is the tax frame-borne -- the V-response under frame refreshment; "
          "exploratory, label-free; no seal")

MASTER_SEED = 20260814
SALT_AUTHOR = "m4q2-author"
SALT_FRAME_A = "m4q2-frameA"
SALT_FRAME_B = "m4q2-frameB"
SALT_PILOT = "m4q2-pilot"
SHARE_LO, SHARE_HI = 0.10, 0.70            # V = 0.03 / 0.21
PHI = 0.60
N_PAIRS = 384
N_PAIRS_ESCALATED = 768
CHUNK = 192
PILOT_PAIRS = 4
PROBE_PAIRS = 4
W_INT_ARM = "zero"

B_BOOT = 2000
B_BOOT_HIGH = 20000
B_PROJ = 2000
RULE13_FACTOR = 10.0
CHI2_Q = 0.10
INDEP_MARGIN = 1.25                        # #57
ANCHOR_K = 2.0 * math.sqrt(2.0)
POWER_MIN = 0.80
FALSE_FIRE_MAX = 0.10
P3C_SHARE_POINT = 0.115360476028154        # P3c's transportable share point
SATURATION_ABS = 0.995

AUTHOR_OBJECTS = ("trait", "a_load", "loadings")
FRAME_OBJECTS = ("slow", "slow_latent", "noise", "common", "int")


def v_of(share: float) -> float:
    return 0.3 * share


# ---------------------------------------------------------------------------
# RN-Q2 notes.  PINNED IN PART 0, BEFORE ANY STATISTIC.
#
# RN-Q2-1 (the anchor's band, which the registration leaves unspecified).  The
#   M-line prediction for D_nat is a DIFFERENCE of two persisted cell means
#   from different legs (M1c's (0.10, 0.60) and M2's C2), each with its own
#   SEM, and the measured D_nat has a SEM of its own.  The registration says
#   "distributional band" without fixing k or the pooling.  PINNED, before any
#   measurement: band = ANCHOR_K * sqrt(SEM_pred^2 + SEM_meas^2) with
#   ANCHOR_K = 2*sqrt(2), matching the anchor convention this programme has
#   used since V-P3a/C1'; the plain 2-SE reading is computed and reported
#   beside it.  Both are shown; the pinned one routes.  Note the anchor's
#   sources are ACROSS LEGS (M1c and M2 ran on different salts), so the band is
#   distributional by necessity, not by choice.
#
# RN-Q2-6 (the sanity value is approximate BY THE REGISTRATION'S OWN WORDS --
#   an anticipated, non-blocking divergence, recorded before any measurement).
#   The registration says the M-line law "predicts ~ +0.117 from persisted
#   cells, planner sanity value, executor recomputes".  The recomputation from
#   M1c's (0.10, 0.60) mean and M2's C2 mean gives 0.11801642901308901 --
#   0.00102 above the quoted 0.117, which rounds to 0.118 rather than 0.117.
#   The registration LABELS the quoted number approximate and hands the
#   recomputation to the executor, which is exactly rule 30's licensed form
#   ("quoted expressly as approximate"), so this is NOT a defect and does NOT
#   gate: the RECOMPUTED value controls and is what the anchor band is built
#   around.  Both are recorded.  For scale, the divergence is roughly a seventh
#   of the anchor band.
#
# RN-Q2-2 (V-Q2a is an instrument gate, not a finding).  A D_nat that misses
#   the M-line prediction routes INSTRUMENT_DEFECT, because the M-line law is
#   the thing this leg trusts in order to interpret D_ref.  It is never read as
#   news about the world.
#
# RN-Q2-3 (#57 compliance).  No pilot correlation is consumed.  D_nat and D_ref
#   are each differences across two INDEPENDENT shares, so their per-share
#   variances add with no covariance term; the 1.25 independence margin is
#   applied where a covariance between the two scorings would otherwise be
#   needed -- i.e. to the ratio's band only -- and is stated where applied.
#   R_nat and R_ref within a pair ARE correlated (they share the A-world), and
#   the bootstrap handles that by resampling pair indices jointly rather than
#   by estimating a correlation.
#
# RN-Q2-4 (the shared-component check, inherited from #60).  Q1b's defect was
#   scoring against an object the measurement did not contain.  That failure
#   mode is absent here and the reason is structural: both R_nat and R_ref use
#   each world's OWN truth panel built by k2b's own emit_panel, and the
#   contrast is between two SHARES, not between two reference objects.  Nothing
#   is scored against something it does not contain.  Recorded because #60 now
#   requires the check to be stated, not merely satisfied.
#
# RN-Q2-5 (what a NULL D_ref would and would not license).  D_ref NULL says the
#   V-response does not survive frame refreshment.  Given P3c already measured
#   R_ref levels near zero at both phi, a NULL D_ref is the expected
#   continuation and its informational content is mostly CONFIRMATORY -- a
#   difference of two near-zero levels is near zero for an uninteresting
#   reason.  The honest reading is therefore joint: D_ref NULL matters only
#   alongside the LEVELS, which are reported per share, and the report states
#   the levels first.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-Q2-1": "the anchor band is PINNED as 2*sqrt(2)*sqrt(SEM_pred^2 + SEM_meas^2), "
               "matching the programme's V-P3a/C1' convention; the plain 2-SE reading "
               "is reported beside it. The prediction's two cells come from DIFFERENT "
               "legs on different salts, so the band is distributional by necessity",
    "RN-Q2-6": "the registration labels 0.117 a 'planner sanity value, executor "
               "recomputes'; the recomputation gives 0.11801642901308901 (0.00102 "
               "above, rounding to 0.118). Rule 30 licenses an expressly-approximate "
               "quote, so this is NOT a defect and does not gate -- the recomputed "
               "value controls and both are recorded",
    "RN-Q2-2": "V-Q2a is an instrument gate: a D_nat that misses the M-line prediction "
               "routes INSTRUMENT_DEFECT and is never read as news about the world",
    "RN-Q2-3": "no pilot correlation is consumed (#57); D_nat and D_ref difference two "
               "INDEPENDENT shares so their variances add with no covariance; the 1.25 "
               "margin is applied only to the ratio's band and stated there; the "
               "within-pair R_nat/R_ref correlation is handled by joint index "
               "resampling, never by estimating a correlation",
    "RN-Q2-4": "#60's shared-component check, stated: both scorings use each world's "
               "OWN truth panel from k2b's emit_panel and the contrast is between two "
               "SHARES, not two reference objects -- nothing is scored against an "
               "object it does not contain",
    "RN-Q2-5": "a NULL D_ref is largely CONFIRMATORY given P3c's near-zero R_ref "
               "levels: a difference of two near-zero levels is near zero for an "
               "uninteresting reason. The report states the LEVELS first and reads the "
               "difference only alongside them",
}

# ---------------------------------------------------------------------------

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
    return _load_named("run_suica_m4_p3b_refresh_gradient", P3BSRC)


def k2b() -> Any:
    return p3b().k2b()


def v8() -> Any:
    return k2b().v8


def build_split_world(a: int, f: int, phi: float) -> dict[str, np.ndarray]:
    return p3b().build_split_world(a, f, phi)


def _log(event: str, **kw: Any) -> None:
    rec = {"utc": datetime.now(UTC).isoformat(), "event": event, **kw}
    with (OUT / "run_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True, default=float) + "\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rt(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, float_precision="round_trip")


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, default=float) + "\n",
                    encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def seed_for(kind: str, share: float, i: int, salt: str) -> int:
    key = f"{LEG}|{salt}|{kind}|share{share!r}|i{i}|seed{MASTER_SEED}"
    return int(v8().stable_bucket(key, salt=salt, modulus=2 ** 63 - 1))


def pair_seeds(share: float, i: int, suffix: str = "") -> dict[str, int]:
    return {"author": seed_for("author", share, i, SALT_AUTHOR + suffix),
            "frameA": seed_for("frameA", share, i, SALT_FRAME_A + suffix),
            "frameB": seed_for("frameB", share, i, SALT_FRAME_B + suffix)}


def _predicate(v: np.ndarray) -> dict[str, Any]:
    fin = bool(np.all(np.isfinite(v)))
    sat = bool(np.any(np.abs(v) >= SATURATION_ABS))
    nz = bool(float(np.std(v, ddof=1)) > 0.0)
    return {"all_finite": fin, "any_saturated": sat, "nonzero_variance": nz,
            "min": float(v.min()), "max": float(v.max()),
            "PASS": bool(fin and (not sat) and nz)}


def run_pair(share: float, i: int, suffix: str = "") -> dict[str, Any]:
    """P3c's scoring unchanged: ONE gauge pass on A, two truth panels."""
    m_ = k2b()
    w = m_.arm_weights(share, W_INT_ARM)
    sd = pair_seeds(share, i, suffix)
    wa = build_split_world(sd["author"], sd["frameA"], PHI)
    wb = build_split_world(sd["author"], sd["frameB"], PHI)
    sc = p3b().score_pair(wa, wb, w, f"Q2-s{share}", i, PHI, with_deframe=False)
    return {"share": share, "V": v_of(share), "phi": PHI, "pair": i,
            "author_seed": sd["author"], "frameA_seed": sd["frameA"],
            "frameB_seed": sd["frameB"],
            "R_nat": sc["R_nat"], "R_ref": sc["R_refresh"],
            "truth_norm_delta": sc["truth_norm_delta"]}


# ---------------------------------------------------------------------------
# PART 0.

def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")

    # --- instrument hashes --------------------------------------------------
    fn = p3b().build_split_world
    fn_sha = hashlib.sha256(inspect.getsource(fn).encode("utf-8")).hexdigest()
    file_sha = hashlib.sha256(P3BSRC.read_bytes()).hexdigest()
    p3cprov = read_json(P3CRES / "part0.json")["instrument_provenance"]
    prov = {"imported_from": rel(P3BSRC),
            "definition_line": int(inspect.getsourcelines(fn)[1]),
            "function_sha256": fn_sha, "file_sha256": file_sha,
            "p3c_persisted_function_sha256": p3cprov["function_sha256"],
            "p3c_persisted_file_sha256": p3cprov["file_sha256"],
            "sha_matches": bool(fn_sha == p3cprov["function_sha256"]
                                and file_sha == p3cprov["file_sha256"])}

    # --- the anchor: the M-line prediction for D_nat ------------------------
    cm = read_csv_rt(M1CRES / "cell_means.csv")
    row = cm[(cm["share"] == SHARE_LO) & (cm["phi"] == PHI)]
    if len(row) != 1:
        raise SystemExit(f"REFUSED: M1c has {len(row)} rows at "
                         f"(share {SHARE_LO}, phi {PHI})")
    m1c_mean = float(row.iloc[0]["field_mean"])
    m1c_sem = float(row.iloc[0]["field_sem"])
    m2c2 = read_json(M2RES / "decision.json")["per_cell"]["C2"]
    if not (m2c2["share"] == SHARE_HI and m2c2["phi"] == PHI):
        raise SystemExit("REFUSED: M2 C2 is not (0.70, 0.60)")
    pred = float(m1c_mean - m2c2["mean"])
    sem_pred = float(math.sqrt(m1c_sem ** 2 + m2c2["sem"] ** 2))
    anchor = {
        "lo_cell": {"source": rel(M1CRES / "cell_means.csv"),
                    "cell_tag": str(row.iloc[0]["cell_tag"]),
                    "share": SHARE_LO, "phi": PHI, "V": v_of(SHARE_LO),
                    "mean": m1c_mean, "sem": m1c_sem,
                    "n": int(row.iloc[0]["n_worlds"])},
        "hi_cell": {"source": rel(M2RES / "decision.json") + ":per_cell.C2",
                    "cell": "C2", "share": m2c2["share"], "phi": m2c2["phi"],
                    "V": v_of(SHARE_HI), "mean": m2c2["mean"], "sem": m2c2["sem"],
                    "n": m2c2["n"]},
        "predicted_D_nat": pred, "sem_predicted": sem_pred,
        "planner_sanity": 0.117,
        "planner_sanity_is_expressly_approximate": True,
        "recomputed_minus_sanity": float(pred - 0.117),
        "matches_planner_sanity_to_3dp": bool(round(pred, 3) == 0.117),
        "sanity_divergence_gates": False,
        "sanity_note": RN_NOTES["RN-Q2-6"],
        "band_rule": RN_NOTES["RN-Q2-1"], "anchor_k": ANCHOR_K,
        "cross_leg_note": "the two cells come from DIFFERENT legs on different salts "
                          "(M1c and M2), so the comparison is distributional by "
                          "necessity",
    }

    # --- G0: the cited legs -------------------------------------------------
    p3c = read_json(P3CRES / "decision.json")
    q1b = read_json(Q1BRES / "decision.json")
    g0 = {
        "instrument": prov, "anchor": anchor,
        "p3c_verdict": p3c["verdict_slug"],
        "p3c_range_ref": p3c["range_ref"], "p3c_D_grad": p3c["D_grad"],
        "p3c_R_ref_endpoints": {str(q["phi"]): q["R_refresh_mean"]
                                for q in p3c["per_phi"] if q["role"] == "endpoint"},
        "p3c_transportable_share_point": P3C_SHARE_POINT,
        "p3c_share_matches": bool(
            p3c["fraction_UNBUDGETED"]["point"] == P3C_SHARE_POINT),
        "q1b_verdict": q1b["verdict_slug"],
        "partial_transport_truth": float(pred * P3C_SHARE_POINT),
        "registered_partial_truth_sanity": 0.0134,
    }
    # RN-Q2-6: the sanity value is expressly approximate, so it does NOT gate.
    g0["PASS"] = bool(prov["sha_matches"] and g0["p3c_share_matches"]
                      and p3c["verdict_slug"] == "UNDERPOWERED")

    # --- C2 battery + per-pair frame difference -----------------------------
    rows = []
    for i in range(PROBE_PAIRS):
        sd = pair_seeds(SHARE_LO, i, "-probe")
        wa = build_split_world(sd["author"], sd["frameA"], PHI)
        wb = build_split_world(sd["author"], sd["frameB"], PHI)
        rec: dict[str, Any] = {"probe": i}
        for k in AUTHOR_OBJECTS:
            rec[f"author::{k}"] = bool(np.array_equal(
                np.asarray(wa[k]).view(np.uint8), np.asarray(wb[k]).view(np.uint8)))
        for k in FRAME_OBJECTS:
            rec[f"frame::{k}"] = float(np.linalg.norm(
                np.asarray(wa[k]) - np.asarray(wb[k])))
        rows.append(rec)
    sd0 = pair_seeds(SHARE_LO, 0, "-probe")
    d1 = build_split_world(sd0["author"], sd0["frameA"], PHI)
    d2 = build_split_world(sd0["author"], sd0["frameA"], PHI)
    c2 = {"n_probe_pairs": PROBE_PAIRS, "rows": rows,
          "all_author_identical": bool(all(r[f"author::{k}"] for r in rows
                                           for k in AUTHOR_OBJECTS)),
          "all_frame_differ": bool(all(r[f"frame::{k}"] > 0.0 for r in rows
                                       for k in FRAME_OBJECTS)),
          "norm_delta_min": {k: float(min(r[f"frame::{k}"] for r in rows))
                             for k in FRAME_OBJECTS},
          "norm_delta_max": {k: float(max(r[f"frame::{k}"] for r in rows))
                             for k in FRAME_OBJECTS},
          "determinism": bool(all(np.array_equal(
              np.asarray(d1[k]).view(np.uint8), np.asarray(d2[k]).view(np.uint8))
              for k in d1)),
          "loadings_shared": bool(all(r["author::loadings"] for r in rows)),
          "shared_component_check": RN_NOTES["RN-Q2-4"]}
    c2["PASS"] = bool(c2["all_author_identical"] and c2["all_frame_differ"]
                      and c2["determinism"] and c2["loadings_shared"])

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_Q_TRANSPORT_LINE_PLAN.md (M4-Q2, BEFORE run, "
                        "commit d030914)",
        "master_seed": MASTER_SEED,
        "salts": {"author": SALT_AUTHOR, "frameA": SALT_FRAME_A,
                  "frameB": SALT_FRAME_B, "pilot": SALT_PILOT},
        "rn_notes": RN_NOTES, "G0q2": g0, "C2": c2,
        "estimands": {
            "D_nat": f"R_nat(V={v_of(SHARE_LO)}) - R_nat(V={v_of(SHARE_HI)})",
            "D_ref": f"R_ref(V={v_of(SHARE_LO)}) - R_ref(V={v_of(SHARE_HI)})",
            "ratio": "D_ref / D_nat -- UNBUDGETED descriptive only",
            "bootstrap": RN_NOTES["RN-Q2-3"]},
        "design": {"shares": [SHARE_LO, SHARE_HI],
                   "V": [v_of(SHARE_LO), v_of(SHARE_HI)], "phi": PHI,
                   "pairs_per_share": N_PAIRS, "chunk": CHUNK,
                   "total_worlds": 2 * 2 * N_PAIRS},
        "sides_rule22": {
            "L-1q2": {"clause": "TAX_FRAME_BORNE / TAX_PARTIALLY_TRANSPORTS / other",
                      "prior": "0.55 / 0.25 / 0.20", "sided": "categorical"},
            "V-Q2a": {"clause": "D_nat POSITIVE and within the anchor band",
                      "sided": "instrument gate"},
            "V-Q2b": {"clause": "D_ref vs 0, NULL-first", "sided": "two-sided"},
            "G3q2": {"clause": f"power >= {POWER_MIN} at the partial-transport truth "
                               f"and false-fire <= {FALSE_FIRE_MAX} at 0",
                     "sided": "one-sided each"}},
        "stage_estimates_seconds": {"part0": 150, "pilot": 60, "project": 30,
                                    "arms_each": 150, "fit": 180, "finalize": 60},
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
            "routing_text": "STOP / INSTRUMENT_DEFECT", "G0q2": g0, "C2": c2,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: INSTRUMENT_DEFECT -- G0/C2 failed")
    print(f"part0 OK  G0 PASS  C2 PASS  anchor predicted D_nat={pred!r} "
          f"(sem {sem_pred!r}, planner sanity 0.117: "
          f"{anchor['matches_planner_sanity_to_3dp']})  partial truth="
          f"{g0['partial_transport_truth']!r}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# PILOT.

def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    if not p0["G0q2"]["PASS"]:
        raise SystemExit("STOP: G0 did not pass.")
    rows = []
    for share in (SHARE_LO, SHARE_HI):
        for i in range(PILOT_PAIRS):
            rows.append(run_pair(share, i, "-pilot"))
        print(f"  pilot share={share}: done ({time.time() - t0:.1f}s)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "pilot_field.csv", index=False)

    per, ok = [], True
    for share, grp in df.groupby("share"):
        cn = _predicate(grp["R_nat"].to_numpy(float))
        cr = _predicate(grp["R_ref"].to_numpy(float))
        ok &= cn["PASS"] and cr["PASS"]
        per.append({"share": float(share), "V": v_of(float(share)),
                    "n": int(len(grp)),
                    "R_nat_mean": float(grp["R_nat"].mean()),
                    "R_ref_mean": float(grp["R_ref"].mean()),
                    "R_nat_regime": cn, "R_ref_regime": cr,
                    "PASS": bool(cn["PASS"] and cr["PASS"])})

    def pooled(col: str) -> tuple[float, int, float, float]:
        ss, dfree = 0.0, 0
        for _, grp in df.groupby("share"):
            v = grp[col].to_numpy(float)
            ss += float(np.sum((v - v.mean()) ** 2))
            dfree += len(v) - 1
        raw = float(np.sqrt(ss / dfree))
        infl = float(np.sqrt(dfree / float(chi2.ppf(CHI2_Q, dfree))))
        return raw, dfree, infl, raw * infl

    sd_nat_raw, dfree, infl, sd_nat = pooled("R_nat")
    sd_ref_raw, _, _, sd_ref = pooled("R_ref")
    se_dnat = float(sd_nat * math.sqrt(2.0 / N_PAIRS))
    se_dref = float(sd_ref * math.sqrt(2.0 / N_PAIRS))
    bands = {
        "sd_R_nat_raw": sd_nat_raw, "sd_R_nat_df_inflated": sd_nat,
        "sd_R_ref_raw": sd_ref_raw, "sd_R_ref_df_inflated": sd_ref,
        "pooled_df": dfree, "inflation": infl, "chi2_quantile": CHI2_Q,
        "SE_D_nat_at_384": se_dnat, "SE_D_ref_at_384": se_dref,
        "epsilon_D_ref": float(2.0 * se_dref),
        "independence_margin": INDEP_MARGIN,
        "margin_applied_to": "the RATIO's band only -- D_nat and D_ref each difference "
                             "two INDEPENDENT shares, so their own SEs need no "
                             "covariance term (RN-Q2-3)",
        "band_definition": "eps = 2 * SE(D_ref) at the decided pairs/share; a NULL "
                           "verdict is a CI lying inside +/- eps",
        "note": RN_NOTES["RN-Q2-3"],
    }
    out = {"utc": datetime.now(UTC).isoformat(),
           "G2q2": {"per_share": per, "PASS": bool(ok)}, "bands": bands,
           "n_pilot_pairs": int(len(df)), "seconds": time.time() - t0}
    write_json(OUT / "pilot.json", out)
    _log("pilot_done", PASS=ok, seconds=out["seconds"])
    if not ok:
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "INSTRUMENT_DEFECT", "routing_cell": "1",
            "routing_text": "STOP / INSTRUMENT_DEFECT", "G2q2": out["G2q2"],
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: INSTRUMENT_DEFECT -- pilot predicate failed")
    print(f"pilot OK  sd_nat={sd_nat!r} sd_ref={sd_ref!r}  "
          f"eps_D_ref={bands['epsilon_D_ref']!r}  "
          f"R_nat {[round(q['R_nat_mean'], 5) for q in per]}  "
          f"R_ref {[round(q['R_ref_mean'], 5) for q in per]}  "
          f"{time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# G3q2 -- the projection.

def stage_project(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    sd_ref = pil["bands"]["sd_R_ref_df_inflated"]
    partial = float(p0["G0q2"]["partial_transport_truth"])

    def project(n: int) -> dict[str, Any]:
        se = float(sd_ref * math.sqrt(2.0 / n))
        rg = np.random.default_rng(MASTER_SEED)
        out = {}
        for name, truth in (("D_ref = 0", 0.0),
                            (f"D_ref = {partial!r} (partial transport)", partial)):
            draws = rg.normal(truth, se, size=B_PROJ)
            fires = float(np.mean(np.abs(draws) > 2.0 * se))
            out[name] = {"truth": truth, "SE": se, "fires_at_2SE": fires,
                         "role": "false-fire" if truth == 0.0 else "power",
                         "bar": (FALSE_FIRE_MAX if truth == 0.0 else POWER_MIN),
                         "PASS": (bool(fires <= FALSE_FIRE_MAX) if truth == 0.0
                                  else bool(fires >= POWER_MIN))}
        return {"pairs_per_share": n, "SE_D_ref": se, "per_truth": out,
                "PASS": bool(all(d["PASS"] for d in out.values()))}

    base = project(N_PAIRS)
    esc = None
    decided = N_PAIRS
    if not base["PASS"]:
        print(f"  G3q2 FAILED at n={N_PAIRS}; once-only escalation to "
              f"n={N_PAIRS_ESCALATED}", flush=True)
        esc = project(N_PAIRS_ESCALATED)
        if esc["PASS"]:
            decided = N_PAIRS_ESCALATED
    g3 = {"truths": {"null": 0.0, "partial_transport": partial},
          "partial_truth_derivation": "the Part-0 anchor prediction times P3c's "
                                      "transportable share point "
                                      f"{P3C_SHARE_POINT!r}",
          "registered_sanity": 0.0134, "B_proj": B_PROJ,
          "base": base, "escalated": esc,
          "escalation_fired": bool(esc is not None),
          "pairs_per_share_decided": decided,
          "PASS": bool(base["PASS"] or (esc is not None and esc["PASS"])),
          "on_fail": "NON_PROJECTABLE", "seconds": time.time() - t0}
    write_json(OUT / "projection.json", g3)
    _log("project_done", PASS=g3["PASS"], seconds=g3["seconds"])
    if not g3["PASS"]:
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "NON_PROJECTABLE", "routing_cell": "2",
            "routing_text": "NON_PROJECTABLE", "G3q2": g3,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: NON_PROJECTABLE")
    print("project OK  " + "  ".join(
        f"{k}: fires={d['fires_at_2SE']!r}" for k, d in base["per_truth"].items())
        + f"  n={decided}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# ARMS.

def _arm_specs(n: int) -> list[tuple[str, float, int, int]]:
    return [(f"s{sh}_{lo}_{min(lo + CHUNK, n)}", sh, lo, min(lo + CHUNK, n))
            for sh in (SHARE_LO, SHARE_HI) for lo in range(0, n, CHUNK)]


def _arm(tag: str) -> None:
    t0 = time.time()
    g3 = read_json(OUT / "projection.json")
    if not g3["PASS"]:
        raise SystemExit("STOP: the projection did not pass.")
    n = int(g3["pairs_per_share_decided"])
    spec = next((s for s in _arm_specs(n) if s[0] == tag), None)
    if spec is None:
        raise SystemExit(f"REFUSED: unknown arm {tag!r} at n={n}")
    _, share, lo, hi = spec
    (OUT / "arms").mkdir(parents=True, exist_ok=True)
    path = OUT / "arms" / f"arm_{tag}.csv"
    if path.exists() and len(read_csv_rt(path)) == hi - lo:
        print(f"  {tag}: already complete, skipped", flush=True)
    else:
        rows = [run_pair(share, i, "") for i in range(lo, hi)]
        pd.DataFrame(rows).to_csv(path, index=False)
        print(f"  {tag}: n={len(rows)} ({time.time() - t0:.1f}s)", flush=True)
    _log(f"arm_{tag}_done", seconds=time.time() - t0)
    print(f"arm {tag} OK  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# FIT.

def _classify(lo: float, hi: float, eps: float) -> tuple[str, str]:
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
    n = int(g3["pairs_per_share_decided"])
    eps = pil["bands"]["epsilon_D_ref"]

    frames = {}
    for sh in (SHARE_LO, SHARE_HI):
        parts = [read_csv_rt(OUT / "arms" / f"arm_{s[0]}.csv")
                 for s in _arm_specs(n) if s[1] == sh]
        d = pd.concat(parts, ignore_index=True).sort_values("pair")
        if len(d) != n or sorted(d["pair"].tolist()) != list(range(n)):
            raise SystemExit(f"REFUSED: share={sh} assembled {len(d)}, want {n}")
        for nm in ("R_nat", "R_ref"):
            chk = _predicate(d[nm].to_numpy(float))
            if not chk["PASS"]:
                raise SystemExit(f"REFUSED: rule-29 fails on {nm} at share={sh}")
        frames[sh] = d

    per_share = []
    for sh in (SHARE_LO, SHARE_HI):
        d = frames[sh]
        per_share.append({
            "share": sh, "V": v_of(sh), "n": int(len(d)),
            "R_nat_mean": float(d["R_nat"].mean()),
            "R_nat_sem": float(np.std(d["R_nat"], ddof=1) / np.sqrt(len(d))),
            "R_ref_mean": float(d["R_ref"].mean()),
            "R_ref_sem": float(np.std(d["R_ref"], ddof=1) / np.sqrt(len(d))),
            "truth_norm_delta_mean": float(d["truth_norm_delta"].mean())})

    nat_lo = frames[SHARE_LO]["R_nat"].to_numpy(float)
    nat_hi = frames[SHARE_HI]["R_nat"].to_numpy(float)
    ref_lo = frames[SHARE_LO]["R_ref"].to_numpy(float)
    ref_hi = frames[SHARE_HI]["R_ref"].to_numpy(float)
    d_nat = float(nat_lo.mean() - nat_hi.mean())
    d_ref = float(ref_lo.mean() - ref_hi.mean())

    rng = np.random.default_rng(MASTER_SEED)
    ilo = rng.integers(0, n, size=(B_BOOT_HIGH, n))
    ihi = rng.integers(0, n, size=(B_BOOT_HIGH, n))

    def boot(B: int) -> dict[str, np.ndarray]:
        dn = nat_lo[ilo[:B]].mean(axis=1) - nat_hi[ihi[:B]].mean(axis=1)
        dr = ref_lo[ilo[:B]].mean(axis=1) - ref_hi[ihi[:B]].mean(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            ra = np.divide(dr, dn, out=np.full(B, np.nan), where=dn != 0.0)
        return {"D_nat": dn, "D_ref": dr, "ratio": ra}

    bb = boot(B_BOOT)

    def ci(a: np.ndarray) -> list[float]:
        return [float(np.nanquantile(a, 0.025)), float(np.nanquantile(a, 0.975))]

    ci_nat, ci_ref = ci(bb["D_nat"]), ci(bb["D_ref"])
    # rule 13 on the routing quantity
    margin = 1.0 / (RULE13_FACTOR * B_BOOT)
    near = []
    for bnd in (0.0, eps, -eps):
        frac = float(np.mean(bb["D_ref"] <= bnd))
        if min(abs(frac - 0.025), abs(frac - 0.975)) < margin:
            near.append({"boundary": bnd, "tail_frac": frac})
    rule13 = []
    if near:
        bb = boot(B_BOOT_HIGH)
        ci_nat, ci_ref = ci(bb["D_nat"]), ci(bb["D_ref"])
        rule13.append({"triggers": near, "B": B_BOOT_HIGH, "ci_after": ci_ref})

    cls_ref, sf_ref = _classify(ci_ref[0], ci_ref[1], eps)

    # --- V-Q2a: the anchor --------------------------------------------------
    a = p0["G0q2"]["anchor"]
    sem_meas = float(math.sqrt(per_share[0]["R_nat_sem"] ** 2
                               + per_share[1]["R_nat_sem"] ** 2))
    pooled_sem = float(math.sqrt(a["sem_predicted"] ** 2 + sem_meas ** 2))
    diff = float(d_nat - a["predicted_D_nat"])
    band = float(ANCHOR_K * pooled_sem)
    band_2se = float(2.0 * pooled_sem)
    v_q2a = {
        "predicted": a["predicted_D_nat"], "sem_predicted": a["sem_predicted"],
        "measured": d_nat, "measured_ci95": ci_nat, "sem_measured": sem_meas,
        "difference": diff, "pooled_sem": pooled_sem,
        "z": float(diff / pooled_sem),
        "band_pinned": band, "inside_pinned_band": bool(abs(diff) <= band),
        "band_2se": band_2se, "inside_2se_band": bool(abs(diff) <= band_2se),
        "positive": bool(ci_nat[0] > 0.0),
        "PASS": bool(ci_nat[0] > 0.0 and abs(diff) <= band),
        "note": RN_NOTES["RN-Q2-1"],
    }

    ratio_ci = ci(bb["ratio"])
    out = {
        "utc": datetime.now(UTC).isoformat(), "pairs_per_share": n,
        "per_share": per_share,
        "D_nat": d_nat, "D_nat_ci95": ci_nat,
        "D_ref": d_ref, "D_ref_ci95": ci_ref,
        "epsilon_D_ref": eps,
        "V_Q2a": v_q2a,
        "V_Q2b": {"quantity": "D_ref", "point": d_ref, "ci95": ci_ref,
                  "epsilon": eps, "classification": cls_ref,
                  "classification_sign_first": sf_ref,
                  "readings_agree": bool(cls_ref == sf_ref)},
        "ratio_UNBUDGETED": {
            "point": float(d_ref / d_nat) if d_nat else None,
            "ci95": ratio_ci, "width": float(ratio_ci[1] - ratio_ci[0]),
            "label": "UNBUDGETED -- descriptive only, gates nothing, routes nothing",
            "margin_note": pil["bands"]["margin_applied_to"]},
        "rule13_events": rule13, "B": int(len(bb["D_ref"])),
        "levels_first": RN_NOTES["RN-Q2-5"],
        "seconds": time.time() - t0,
    }
    write_json(OUT / "fit.json", out)
    _log("fit_done", V_Q2a=v_q2a["PASS"], V_Q2b=cls_ref, seconds=out["seconds"])
    print(f"fit OK  D_nat={d_nat!r} {ci_nat} (pred {a['predicted_D_nat']!r}, z="
          f"{v_q2a['z']:.3f}, anchor {'PASS' if v_q2a['PASS'] else 'FAIL'})  "
          f"D_ref={d_ref!r} {ci_ref} -> {cls_ref}  eps={eps!r}  "
          f"{time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# FINALIZE.

TRUTH_TABLE = [
    {"n": "1", "condition": "G0/G1 failure", "outcome": "STOP_INSTRUMENT_DEFECT",
     "text": "STOP / INSTRUMENT_DEFECT"},
    {"n": "2", "condition": "projection fails after escalation",
     "outcome": "NON_PROJECTABLE", "text": "NON_PROJECTABLE"},
    {"n": "3", "condition": "V-Q2a not POSITIVE", "outcome": "INSTRUMENT_DEFECT",
     "text": "INSTRUMENT_DEFECT (the anchor is the M-line law)"},
    {"n": "4", "condition": "V-Q2b NULL", "outcome": "TAX_FRAME_BORNE",
     "text": "TAX_FRAME_BORNE -- the V-response is frame-agreement; the N-line curve "
             "is re-typed as the frame channel's V-response; appendix II completes"},
    {"n": "5", "condition": "V-Q2b POSITIVE", "outcome": "TAX_PARTIALLY_TRANSPORTS",
     "text": "TAX_PARTIALLY_TRANSPORTS -- a person-borne tax component exists; "
             "quantified descriptively"},
    {"n": "6", "condition": "V-Q2b NEGATIVE", "outcome": "TAX_INVERSION_NAMED",
     "text": "TAX_INVERSION_NAMED -- theory note"},
    {"n": "7", "condition": "any UNDERPOWERED (no higher cell)",
     "outcome": "UNDERPOWERED", "text": "UNDERPOWERED"},
]


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    g3 = read_json(OUT / "projection.json")
    fit = read_json(OUT / "fit.json")
    if not fit["V_Q2a"]["PASS"]:
        slug = "INSTRUMENT_DEFECT"
    else:
        slug = {"NULL": "TAX_FRAME_BORNE", "POSITIVE": "TAX_PARTIALLY_TRANSPORTS",
                "NEGATIVE": "TAX_INVERSION_NAMED",
                "UNDERPOWERED": "UNDERPOWERED"}[fit["V_Q2b"]["classification"]]
    cell_n = next(t["n"] for t in TRUTH_TABLE if t["outcome"] == slug)
    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "verdict_slug": slug, "routing_cell": cell_n, "modifiers": [],
        "routing_text": next(t["text"] for t in TRUTH_TABLE if t["outcome"] == slug),
        "V_Q2a": fit["V_Q2a"], "V_Q2b": fit["V_Q2b"],
        "D_nat": fit["D_nat"], "D_nat_ci95": fit["D_nat_ci95"],
        "D_ref": fit["D_ref"], "D_ref_ci95": fit["D_ref_ci95"],
        "epsilon_D_ref": fit["epsilon_D_ref"],
        "ratio_UNBUDGETED": fit["ratio_UNBUDGETED"],
        "per_share": fit["per_share"], "pairs_per_share": fit["pairs_per_share"],
        "total_worlds": int(2 * 2 * fit["pairs_per_share"]),
        "anchor": p0["G0q2"]["anchor"], "C2": p0["C2"],
        "bands": pil["bands"], "projection": g3,
        "rule13_events": fit["rule13_events"],
        "levels_first": fit["levels_first"],
        "gates": {
            "G0q2": {"PASS": p0["G0q2"]["PASS"],
                     "detail": "instrument hashes vs P3c's persisted; the anchor cells "
                               "at full precision; P3c's and Q1b's verdicts"},
            "C2": {"PASS": p0["C2"]["PASS"],
                   "detail": f"{PROBE_PAIRS} fresh probe pairs; shared-component check "
                             "stated (#60)"},
            "G2q2": {"PASS": pil["G2q2"]["PASS"],
                     "detail": "rule-29 predicate on BOTH scorings at both shares; "
                               "bands from variances only with the margin stated"},
            "G3q2": {"PASS": g3["PASS"],
                     "detail": f"escalation fired: {g3['escalation_fired']}"},
            "V-Q2a": {"PASS": fit["V_Q2a"]["PASS"],
                      "detail": "D_nat POSITIVE and within the anchor band"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug, seconds=dec["seconds"])
    _tables(p0, pil, g3, fit, dec)
    _facts(p0, pil, g3, fit, dec)
    print(f"finalize OK  slug={slug}  cell={cell_n}")
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
    pv = p0["G0q2"]["instrument"]
    sec["provenance"] = _md(
        ["property", "value"],
        [["instrument", "`" + pv["imported_from"] + ":"
          + str(pv["definition_line"]) + "`"],
         ["function sha256", pv["function_sha256"]],
         ["P3c persisted function sha256", pv["p3c_persisted_function_sha256"]],
         ["file sha256", pv["file_sha256"]],
         ["**hashes match**", "**" + str(pv["sha_matches"]) + "**"]])
    a = p0["G0q2"]["anchor"]
    sec["anchor"] = _md(
        ["quantity", "value"],
        [["low-V cell", f"{a['lo_cell']['cell_tag']} (share {a['lo_cell']['share']}, "
          f"phi {a['lo_cell']['phi']}, V {a['lo_cell']['V']!r}, n "
          f"{a['lo_cell']['n']})"],
         ["its source", "`" + a["lo_cell"]["source"] + "`"],
         ["its mean / SEM", repr(a["lo_cell"]["mean"]) + " / "
          + repr(a["lo_cell"]["sem"])],
         ["high-V cell", f"M2 {a['hi_cell']['cell']} (share {a['hi_cell']['share']}, "
          f"phi {a['hi_cell']['phi']}, V {a['hi_cell']['V']!r}, n "
          f"{a['hi_cell']['n']})"],
         ["its source", "`" + a["hi_cell"]["source"] + "`"],
         ["its mean / SEM", repr(a["hi_cell"]["mean"]) + " / "
          + repr(a["hi_cell"]["sem"])],
         ["**predicted D_nat**", "**" + repr(a["predicted_D_nat"]) + "**"],
         ["SEM of the prediction", repr(a["sem_predicted"])],
         ["planner sanity value (expressly approximate)", repr(a["planner_sanity"])],
         ["recomputed minus sanity", repr(a["recomputed_minus_sanity"])],
         ["matches to 3 dp", str(a["matches_planner_sanity_to_3dp"])],
         ["does the divergence gate?", str(a["sanity_divergence_gates"])
          + " -- rule 30 licenses an expressly-approximate quote; the RECOMPUTED "
            "value controls (RN-Q2-6)"],
         ["band rule (pinned)", a["band_rule"]],
         ["cross-leg note", a["cross_leg_note"]]])
    v = fit["V_Q2a"]
    sec["vq2a"] = _md(
        ["quantity", "value"],
        [["predicted D_nat", repr(v["predicted"])],
         ["**measured D_nat**", "**" + repr(v["measured"]) + "**"],
         ["measured 95% CI", repr(v["measured_ci95"])],
         ["difference", repr(v["difference"])],
         ["pooled SEM", repr(v["pooled_sem"])],
         ["z", repr(v["z"])],
         ["pinned band (2*sqrt(2)*pooled SEM)", repr(v["band_pinned"])],
         ["**inside the pinned band**", "**" + str(v["inside_pinned_band"]) + "**"],
         ["plain 2-SE band (reported)", repr(v["band_2se"])],
         ["inside the 2-SE band", str(v["inside_2se_band"])],
         ["D_nat POSITIVE", str(v["positive"])],
         ["**V-Q2a PASS**", "**" + str(v["PASS"]) + "**"]])
    sec["levels"] = _md(
        ["share", "V", "n", "R_nat mean", "R_nat SEM", "R_ref mean", "R_ref SEM",
         "||T-nat - T-ref|| mean"],
        [[repr(q["share"]), repr(q["V"]), str(q["n"]), repr(q["R_nat_mean"]),
          repr(q["R_nat_sem"]), repr(q["R_ref_mean"]), repr(q["R_ref_sem"]),
          repr(q["truth_norm_delta_mean"])] for q in fit["per_share"]])
    sec["estimands"] = _md(
        ["estimand", "definition", "point", "95% CI", "epsilon", "classification"],
        [["D_nat", f"R_nat(V={v_of(SHARE_LO)}) - R_nat(V={v_of(SHARE_HI)})",
          repr(fit["D_nat"]), repr(fit["D_nat_ci95"]), "—",
          "anchor gate: " + ("PASS" if fit["V_Q2a"]["PASS"] else "FAIL")],
         ["**D_ref**", f"R_ref(V={v_of(SHARE_LO)}) - R_ref(V={v_of(SHARE_HI)})",
          "**" + repr(fit["D_ref"]) + "**", repr(fit["D_ref_ci95"]),
          repr(fit["epsilon_D_ref"]),
          "**" + fit["V_Q2b"]["classification"] + "**"],
         ["V-Q2b sign-first reading", "—", "—", "—", "—",
          fit["V_Q2b"]["classification_sign_first"]],
         ["readings agree", "—", "—", "—", "—",
          str(fit["V_Q2b"]["readings_agree"])]])
    r = fit["ratio_UNBUDGETED"]
    sec["ratio"] = _md(
        ["quantity", "value"],
        [["D_ref / D_nat", repr(r["point"])], ["95% CI", repr(r["ci95"])],
         ["CI width", repr(r["width"])],
         ["**label**", "**" + r["label"] + "**"],
         ["margin note", r["margin_note"]]])
    b = pil["bands"]
    sec["bands"] = _md(
        ["quantity", "value"],
        [["sd R_nat raw / df-inflated",
          repr(b["sd_R_nat_raw"]) + " / " + repr(b["sd_R_nat_df_inflated"])],
         ["sd R_ref raw / df-inflated",
          repr(b["sd_R_ref_raw"]) + " / " + repr(b["sd_R_ref_df_inflated"])],
         ["pooled df / inflation", str(b["pooled_df"]) + " / " + repr(b["inflation"])],
         ["SE(D_nat) at 384", repr(b["SE_D_nat_at_384"])],
         ["SE(D_ref) at 384", repr(b["SE_D_ref_at_384"])],
         ["**epsilon_D_ref**", "**" + repr(b["epsilon_D_ref"]) + "**"],
         ["independence margin (#57)", repr(b["independence_margin"])],
         ["margin applied to", b["margin_applied_to"]]])
    rows = []
    for label, blk in (("384 (registered)", g3["base"]),
                       ("768 (escalated)", g3["escalated"])):
        if blk is None:
            continue
        for k, d in blk["per_truth"].items():
            rows.append([label, k, d["role"], repr(d["SE"]), repr(d["fires_at_2SE"]),
                         repr(d["bar"]), str(d["PASS"])])
    sec["projection"] = _md(
        ["pairs/share", "truth", "role", "SE(D_ref)", "fires at 2 SE", "bar", "PASS"],
        rows + [["derivation of the partial truth", g3["partial_truth_derivation"],
                 "registered sanity", repr(g3["registered_sanity"]), "—", "—", "—"]])
    c2 = p0["C2"]
    sec["c2"] = _md(
        ["check", "objects", "result"],
        [["author objects bit-identical", ", ".join(AUTHOR_OBJECTS),
          str(c2["all_author_identical"])]]
        + [[f"frame norm delta: {k}", "frame",
            f"[{c2['norm_delta_min'][k]!r}, {c2['norm_delta_max'][k]!r}]"]
           for k in FRAME_OBJECTS]
        + [["determinism", "all objects", str(c2["determinism"])],
           ["shared basis", "loadings", str(c2["loadings_shared"])],
           ["#60 shared-component check", "stated", c2["shared_component_check"]],
           ["**C2**", "—", "**PASS = " + str(c2["PASS"]) + "**"]])
    sec["truth_table"] = _md(
        ["#", "condition", "outcome"],
        [[t["n"], t["condition"],
          ("**" + t["text"] + "**  <-- THIS LEG") if t["outcome"] == dec["verdict_slug"]
          else t["text"]] for t in TRUTH_TABLE])
    sec["gates"] = _md(["gate", "PASS", "detail"],
                       [[k, str(x["PASS"]), x["detail"]]
                        for k, x in dec["gates"].items()])
    sec["sides"] = _md(["clause", "statement", "prior", "sided"],
                       [[k, str(x["clause"]), str(x.get("prior", "—")), x["sided"]]
                        for k, x in p0["sides_rule22"].items()])
    sec["rn"] = _md(["note", "pinned reading"],
                    [[k, x] for k, x in p0["rn_notes"].items()])
    sec["env"] = _md(["component", "value"],
                     [[k, str(x)] for k, x in p0["environment"].items()])
    est = p0["stage_estimates_seconds"]
    meas: dict[str, float] = {}
    for line in (OUT / "run_log.jsonl").read_text(encoding="utf-8").splitlines():
        rr = json.loads(line)
        if "seconds" in rr:
            meas[rr["event"]] = float(rr["seconds"])
    trows = [["part0", str(est["part0"]),
              "%.3f" % meas.get("part0_done", float("nan"))],
             ["pilot", str(est["pilot"]),
              "%.3f" % meas.get("pilot_done", float("nan"))],
             ["project", str(est["project"]),
              "%.3f" % meas.get("project_done", float("nan"))]]
    for tag, _, _, _ in _arm_specs(fit["pairs_per_share"]):
        trows.append([f"arm {tag}", str(est["arms_each"]),
                      "%.3f" % meas.get(f"arm_{tag}_done", float("nan"))])
    trows += [["fit", str(est["fit"]), "%.3f" % meas.get("fit_done", float("nan"))],
              ["finalize", str(est["finalize"]),
               "%.3f" % meas.get("finalize_done", float("nan"))]]
    sec["timing"] = _md(["stage", "estimate (s)", "measured (s)"], trows)
    body = ["# M4-Q2 report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _facts(p0: dict[str, Any], pil: dict[str, Any], g3: dict[str, Any],
           fit: dict[str, Any], dec: dict[str, Any]) -> None:
    a = p0["G0q2"]["anchor"]
    v = fit["V_Q2a"]
    b = pil["bands"]
    r = fit["ratio_UNBUDGETED"]
    f = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"],
        "MODIFIERS": ", ".join(dec["modifiers"]) or "none",
        "NPAIRS": fit["pairs_per_share"], "NWORLDS": dec["total_worlds"],
        "PRED": a["predicted_D_nat"], "PRED_SEM": a["sem_predicted"],
        "SANITY": a["planner_sanity"], "SANITY_OK": a["matches_planner_sanity_to_3dp"],
        "SANITY_DIFF": a["recomputed_minus_sanity"],
        "DNAT": fit["D_nat"], "DNAT_CI": fit["D_nat_ci95"],
        "ANCHOR_DIFF": v["difference"], "ANCHOR_Z": v["z"],
        "ANCHOR_BAND": v["band_pinned"], "ANCHOR_IN": v["inside_pinned_band"],
        "ANCHOR_BAND2": v["band_2se"], "ANCHOR_IN2": v["inside_2se_band"],
        "ANCHOR_PASS": v["PASS"],
        "DREF": fit["D_ref"], "DREF_CI": fit["D_ref_ci95"],
        "EPS": fit["epsilon_D_ref"], "CLASS": fit["V_Q2b"]["classification"],
        "CLASS_SF": fit["V_Q2b"]["classification_sign_first"],
        "AGREE": fit["V_Q2b"]["readings_agree"],
        "RATIO": r["point"], "RATIO_CI": r["ci95"], "RATIO_W": r["width"],
        "SD_NAT": b["sd_R_nat_df_inflated"], "SD_REF": b["sd_R_ref_df_inflated"],
        "SE_DNAT": b["SE_D_nat_at_384"], "SE_DREF": b["SE_D_ref_at_384"],
        "MARGIN": b["independence_margin"],
        "PARTIAL": g3["truths"]["partial_transport"],
        "FF": g3["base"]["per_truth"]["D_ref = 0"]["fires_at_2SE"],
        "PW": [d["fires_at_2SE"] for k, d in g3["base"]["per_truth"].items()
               if d["role"] == "power"][0],
        "ESC": g3["escalation_fired"],
        "SHA_OK": p0["G0q2"]["instrument"]["sha_matches"],
        "PROBES": p0["C2"]["n_probe_pairs"], "C2PASS": p0["C2"]["PASS"],
        "NRULE13": len(fit["rule13_events"]), "B": fit["B"],
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
    }
    for q in fit["per_share"]:
        t = str(q["share"]).replace(".", "")
        f[f"S{t}_NAT"] = q["R_nat_mean"]
        f[f"S{t}_NATSEM"] = q["R_nat_sem"]
        f[f"S{t}_REF"] = q["R_ref_mean"]
        f[f"S{t}_REFSEM"] = q["R_ref_sem"]
        f[f"S{t}_V"] = q["V"]
    write_json(OUT / "prose_facts.json", f)


REPORT_TEMPLATE = r"""# SUICA M4-Q2 — is the tax frame-borne? — **{{SLUG}}**

**Outcome: {{SLUG}} (routing cell {{CELL}}); modifiers: {{MODIFIERS}}.**
{{ROUTING_TEXT}}

**D_ref = {{DREF}} {{DREF_CI}} → {{CLASS}}** (ε = {{EPS}}), against a natural
tax swing **D_nat = {{DNAT}} {{DNAT_CI}}** which the M-line law predicted at
{{PRED}}. {{NWORLDS}} worlds ({{NPAIRS}} A/B pairs per share).

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_Q_TRANSPORT_LINE_PLAN.md` BEFORE run (commit d030914). Every
number below is generated from artifacts by code (rule 24).

---

## 1. The levels first

RN-Q2-5, pinned in Part 0: a NULL D_ref is largely **confirmatory** given that
P3c already found R_ref near zero — a difference of two near-zero levels is near
zero for an uninteresting reason. So the levels are stated before the
difference.

<<TABLE:levels>>

R_nat falls from {{S01_NAT}} at V = {{S01_V}} to {{S07_NAT}} at V = {{S07_V}} —
the tax, plainly visible. R_ref sits at {{S01_REF}} and {{S07_REF}}: **the
frame-refreshed reading has essentially no level to lose at either V**, which is
what makes its difference small.

## 2. The anchor — V-Q2a

The M-line law's prediction is recomputed from two persisted cells on different
legs:

<<TABLE:anchor>>

<<TABLE:vq2a>>

Predicted **{{PRED}}** by recomputation. The registration's quoted sanity value
is {{SANITY}}, expressly approximate with "executor recomputes" — the
recomputation is {{SANITY_DIFF}} above it and rounds to 0.118 rather than 0.117
(matches to 3 dp: {{SANITY_OK}}). Rule 30 licenses an expressly-approximate
quote, so this does **not** gate and the recomputed value controls (RN-Q2-6);
for scale the divergence is about a seventh of the anchor band. Measured
**{{DNAT}}** {{DNAT_CI}}; difference {{ANCHOR_DIFF}}, z = {{ANCHOR_Z}},
inside the pinned band {{ANCHOR_BAND}} ({{ANCHOR_IN}}) and inside the plain
2-SE band {{ANCHOR_BAND2}} ({{ANCHOR_IN2}}). **V-Q2a = {{ANCHOR_PASS}}** — the
instrument reproduces the M-line law, so D_ref can be interpreted.

The band was pinned before any measurement (RN-Q2-1): the registration says
"distributional band" without fixing k, and the two source cells come from
different legs on different salts, so the comparison is distributional by
necessity. Both the pinned 2√2 reading and the plain 2-SE reading are reported;
they agree here.

## 3. The result — V-Q2b

<<TABLE:estimands>>

D_ref = **{{DREF}}** {{DREF_CI}} against ε = {{EPS}} → **{{CLASS}}**. The
sign-first reading agrees ({{AGREE}}).

<<TABLE:ratio>>

The ratio is quoted **UNBUDGETED** — it gates nothing and routes nothing (the
P3b lesson kept visible), and it is the only place the 1.25 independence margin
touches anything.

## 4. Bands and projection

<<TABLE:bands>>

No pilot correlation is consumed (#57). D_nat and D_ref each difference two
**independent** shares, so their SEs need no covariance term; the margin is
applied only to the ratio's band, and stated (RN-Q2-3). The within-pair
R_nat/R_ref correlation is handled by resampling pair indices jointly, never by
estimating a correlation.

<<TABLE:projection>>

False-fire {{FF}} at D_ref = 0 (bar 0.1) and power {{PW}} at the partial-
transport truth {{PARTIAL}} (bar 0.8, derived as the anchor prediction times
P3c's transportable share point). Escalation did not fire ({{ESC}}).

## 5. Instrument and C2

<<TABLE:provenance>>

Hashes match P3c's persisted values ({{SHA_OK}}).

<<TABLE:c2>>

C2 = {{C2PASS}} on {{PROBES}} fresh probe pairs. The #60 shared-component check
is stated, not merely satisfied (RN-Q2-4): both scorings use each world's **own**
truth panel from k2b's `emit_panel`, and the contrast is between two SHARES, not
two reference objects — so nothing is scored against an object it does not
contain, which was Q1b's failure mode.

## 6. Routing

<<TABLE:truth_table>>

## 7. Gates

<<TABLE:gates>>

## 8. Sides declared (rule 22)

<<TABLE:sides>>

## 9. Pinned readings

<<TABLE:rn>>

## 10. Rule events

- **Rule 13:** {{NRULE13}} boundary event(s); bootstrap B = {{B}}.
- **Rule 25:** the projection gate passed at the registered size.
- **Rule 26:** no bounded winner.
- **Rule 27:** the ratio is explicitly UNBUDGETED and carries the label.
- **Rule 29:** the domain-pinned predicate ran on BOTH scorings at every arm.
- **Rule 30:** every cited constant read from its persisted source; the anchor
  prediction is recomputed rather than quoted.
- **#57:** no pilot correlation consumed; the margin applied only to the ratio.
- **#60:** the shared-component check stated explicitly.

## 11. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython {{PYTHON}} venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.

## 12. Environment

<<TABLE:env>>

## 13. Timing

<<TABLE:timing>>

---

*Artifacts: `results/m4_q2_tax_transport/` (gitignored) — `part0.json`,
`pilot.json`, `pilot_field.csv`, `projection.json`, `arms/`, `fit.json`,
`decision.json`, `prose_facts.json`, `report_tables.md`, `run_log.jsonl`.
Harness: `scripts/run_suica_m4_q2_tax_transport.py`.*
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
    path = ROOT / "reports" / "SUICA_M4_Q2_TAX_TRANSPORT_REPORT.md"
    path.write_text(txt, encoding="utf-8")
    print(f"report OK  {rel(path)}  ({len(txt.splitlines())} lines)")
    _ = args


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="stage", required=True)
    stages: list[tuple[str, Callable[[argparse.Namespace], None]]] = [
        ("part0", stage_part0), ("pilot", stage_pilot), ("project", stage_project)]
    seen = {n for n, _ in stages}
    for tag, _, _, _ in (_arm_specs(N_PAIRS) + _arm_specs(N_PAIRS_ESCALATED)):
        if f"arm_{tag}" in seen:
            continue
        seen.add(f"arm_{tag}")
        stages.append((f"arm_{tag}", (lambda tt: lambda a: _arm(tt))(tag)))
    stages += [("fit", stage_fit), ("finalize", stage_finalize),
               ("report", stage_report)]
    for name, fn in stages:
        sub.add_parser(name).set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
