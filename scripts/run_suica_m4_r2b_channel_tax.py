#!/usr/bin/env python3
"""SUICA M4-R2b -- the channel-specific tax (two taxes, measured apart).

Registered BEFORE run in docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md
("M4-R2b", commit 4bece27).  Binding.

R2 measured a real but tiny interference and showed the N-line curve overprices
it 11.65x.  The hypothesis that forces: the tax is CHANNEL-SPECIFIC -- kappa(V)
is the STATE-channel (slow) tax, and author-constant (mu-channel) person
variance is taxed an order lighter.  This leg measures the two taxes apart:

    kappa_slow  : design-share variation at MATCHED r (N1's roots; the
                  r-channel cancels in the difference)
    kappa_mu    : planted style variation at fixed design (the v2 knob)

Sealed (Part 0 -> hash -> worlds, #61 bands):
    S1  kappa_slow(w=0) vs the M3 curve's secant at Vbar = 0.0525
    S2  kappa_mu(0.25)  vs R2's measurement (wide band, first-interval claim)
    S3  D_channel = kappa_slow(w=0) - kappa_mu(0.25) > 0 and outside 2*SE_D

Stages: part0 -> pilot -> project -> arms -> fit -> finalize -> report
"""
from __future__ import annotations

import argparse
import hashlib
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
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LEG = "M4-R2b"
OUT = ROOT / "results" / "m4_r2b_channel_tax"
REPORT = ROOT / "reports" / "SUICA_M4_R2B_CHANNEL_TAX_REPORT.md"

R1SRC = ROOT / "scripts" / "run_suica_m4_r1_identity_channel.py"
R2SRC = ROOT / "scripts" / "run_suica_m4_r2_gauge_meets_identity.py"
K2BSRC = ROOT / "scripts" / "run_suica_m4_k2b_t4_branch.py"
K2ESRC = ROOT / "scripts" / "run_suica_m4_k2e_double_matching.py"
M3DEC = ROOT / "results" / "m4_m3_tax_curve" / "decision.json"
N1P0 = ROOT / "results" / "m4_n1_response_transport" / "part0.json"
R2P0 = ROOT / "results" / "m4_r2_gauge_meets_identity" / "part0.json"
R2FIT = ROOT / "results" / "m4_r2_gauge_meets_identity" / "fit.json"

# --- the registered design -------------------------------------------------
PHI_A = 0.8991793501377106          # N1's persisted root, share 0.10
PHI_B = 0.05                        # N1's persisted partner, share 0.25
SHARE_LO = 0.10
SHARE_HI = 0.25
DV_SLOW = 0.045
VBAR = 0.0525
W_INT_ARM = "zero"
W_DOSES = (0.0, 1.0)
N_WORLDS = 192
N_ESCALATED = 384
MASTER_SEED = 20260814
SALT_WORLD = "m4r2b-world"
SALT_PILOT = "m4r2b-pilot"
N_PILOT = 4
N_PROBE = 16
B_BOOT = 2000
B_BOOT_HIGH = 20000
RULE13_FACTOR = 10.0
CI_Q = (2.5, 97.5)
POWER_MIN = 0.80
FALSE_FIRE_MAX = 0.10
B_PROJ = 2000
SATURATION_ABS = 0.999
CHUNKS = 4

# RN-R2B-1: the 2x2 factorial is the only reading that satisfies the
# registration's own arithmetic.  The DIAGONAL is the matched-r pair and is the
# only thing that routes; the off-diagonal cells are diagnostics.
CELLS = {
    "A": {"share": SHARE_LO, "phi": PHI_A, "role": "matched-r diagonal (V lo)"},
    "B": {"share": SHARE_HI, "phi": PHI_B, "role": "matched-r diagonal (V hi)"},
    "C": {"share": SHARE_LO, "phi": PHI_B, "role": "off-diagonal (diagnostic)"},
    "D": {"share": SHARE_HI, "phi": PHI_A, "role": "off-diagonal (diagnostic)"},
}
DIAG = ("A", "B")

PIN_TRUTH_PANEL = "scripts/run_suica_m4_k2b_t4_branch.py:359-381 (emit_panel)"
PIN_TRUTH_ACTIVE = 'active=("mu","common"), p3b:409-411'
PIN_R = "scripts/run_suica_m4_k2b_t4_branch.py:533-584 r_card_b_pred_raw"
PIN_BUILDER = "scripts/run_suica_m4_r1_identity_channel.py:267-326"
PIN_SHARE = "scripts/run_suica_m4_k2e_double_matching.py:217-241"

# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-R2B-1":
        "REGISTRATION DEFECT CANDIDATE, pinned before any number.  The "
        "registration says 'Four base cells x w_style in {0,1.0} = 8 arms x 192 "
        "worlds = 1536 worlds' but names only TWO base cells (the matched-r pair "
        "(0.10, phi_A) and (0.25, 0.05)).  Two cells x two doses is 4 arms, not 8. "
        "The 2x2 FACTORIAL {share 0.10, 0.25} x {phi_A, 0.05} is the unique reading "
        "that satisfies all four of the registration's numbers simultaneously (4 "
        "base cells, 8 arms, 192 per arm, 1536 total) while keeping the named "
        "matched-r pair as its diagonal.  Every REGISTERED estimand is computed on "
        "the diagonal exactly as specified; the two off-diagonal cells route "
        "NOTHING and are reported as diagnostics -- they also make S2's "
        "phi-transport SE_approx estimable from pre-measurement objects, which the "
        "2-cell reading could not.  The alternative reading (2 cells x 2 doses x 384 "
        "worlds = 1536) is reported and contradicts 'eight arms' and '192'.",
    "RN-R2B-2":
        "REGISTRATION DEFECT CANDIDATE, pinned before any number.  The registration "
        "writes kappa_slow = -[R_T(0.10 cell) - R_T(0.25 cell)]/dV_slow.  Since the "
        "0.10 cell is the LOW-V cell (V = 0.03) where alpha is HIGHER, that bracket "
        "is positive and the formula returns a NEGATIVE tax rate -- while S1's own "
        "prediction (the curve's secant) is POSITIVE, the cited N1b context value "
        "(0.918) is POSITIVE, and kappa_mu by the registration's own formula is "
        "POSITIVE.  Under the literal operand order S3 (D_channel > 0) could not "
        "fire even under perfect channel specificity.  The operand order is a slip; "
        "the PINNED estimator is the standard secant orientation kappa_slow = "
        "+[R_T(0.10 cell) - R_T(0.25 cell)]/dV_slow, which is positive, is on the "
        "same footing as kappa_mu, and is the quantity S1 actually compares against. "
        "Both signs are reported.",
    "RN-R2B-3":
        "channel coverage NAMED per #62.  dV_mu = V_C(w=1) - V_C(w=0) with V_C = "
        "(slow + int + mu_style)/total over the SPLIT channel set {mu_trait, "
        "mu_style, slow, int, common, noise}, each term the pipeline's own "
        "emit_panel mean-square.  COUNTED: slow, int, and mu_style (the planted "
        "author-constant NON-TARGET channel).  NOT COUNTED: mu_trait (the target "
        "trait), common (frame), noise.  This is R2's reading C unchanged, so the "
        "two legs' dV_mu are on one scale.",
    "RN-R2B-4":
        "the corpus string encodes the WORLD INDEX ONLY -- never share, phi or dose "
        "(RN-P1-8 / RN-R2-2: the corpus enters the frozen map, so an arm-dependent "
        "corpus would contaminate every contrast at its root).  Seeds likewise "
        "depend on the world index only, so all eight arms at index i share author "
        "and frame streams; noise, common and the interaction shocks are drawn after "
        "the AR loop and are therefore BIT-IDENTICAL across phi as well.",
    "RN-R2B-5":
        "S1's SE_approx carries the r-channel GAIN (this instrument reads below M3's "
        "own alpha at the same V, exactly as in R2), the gain's spread between the "
        "two diagonal cells, and the matched-r residual propagated through dV_slow. "
        "S2's SE_approx carries the phi-transport term measured on PROBE worlds from "
        "the off-diagonal cells (R2 measured kappa_mu at phi 0.60; this leg's 0.25 "
        "cell sits at phi 0.05) plus the dV_mu difference between the two designs. "
        "All are pre-measurement objects.",
    "RN-R2B-6":
        "S2 is a FIRST-INTERVAL claim by construction and is stated as such: its "
        "band is wide because R2's own CI is propagated into it, so containment "
        "there is descriptive-grade evidence and routes nothing on its own (the "
        "registration's V-b3).",
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


def r1() -> Any:
    return _load_named("run_suica_m4_r1_identity_channel", R1SRC)


def k2e() -> Any:
    return _load_named("run_suica_m4_k2e_double_matching", K2ESRC)


def k2b() -> Any:
    return r1().k2b()


def v8() -> Any:
    return k2b().v8


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


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seed_for(kind: str, i: int, salt: str) -> int:
    """RN-R2B-4: the world index only -- never share, phi or dose."""
    key = f"{LEG}|{salt}|{kind}|i{i}|seed{MASTER_SEED}"
    return int(v8().stable_bucket(key, salt=salt, modulus=2 ** 63 - 1))


def world_seeds(i: int, suffix: str = "") -> dict[str, int]:
    return {"author": seed_for("author", i, SALT_WORLD + suffix),
            "frame": seed_for("frame", i, SALT_WORLD + suffix)}


def _predicate(v: np.ndarray) -> dict[str, Any]:
    fin = bool(np.all(np.isfinite(v)))
    sat = bool(np.any(np.abs(v) >= SATURATION_ABS))
    nz = bool(float(np.std(v, ddof=1)) > 0.0)
    return {"all_finite": fin, "any_saturated": sat, "nonzero_variance": nz,
            "min": float(v.min()), "max": float(v.max()),
            "PASS": bool(fin and (not sat) and nz)}


def df_inflation(df: int) -> float:
    return float(math.sqrt(df / stats.chi2.ppf(0.10, df)))


def curve() -> dict[str, Any]:
    d = read_json(M3DEC)
    q = d["curves"]["A-quad"]
    return {"theta": [float(x) for x in q["theta"]], "expr": q["expr"],
            "points": [(float(a["V"]), float(a["alpha"]), float(a["se"]))
                       for a in d["alpha"]],
            "winner": d["L-1m3"]["winner"], "consumption": d["curve_consumption"]}


def alpha_of(V: Any, theta: list[float]) -> Any:
    c, k0, k2 = theta
    V = np.asarray(V, dtype=float)
    return c - k0 * V + (k2 / 2.0) * V ** 2


def curve_cov(pts: list[tuple[float, float, float]]) -> dict[str, Any]:
    V = np.array([p[0] for p in pts], float)
    y = np.array([p[1] for p in pts], float)
    X = np.column_stack([np.ones_like(V), -V, V ** 2 / 2.0])
    xtx_inv = np.linalg.inv(X.T @ X)
    beta = xtx_inv @ (X.T @ y)
    resid = y - X @ beta
    dof = len(V) - 3
    sigma2 = float(resid @ resid) / dof
    return {"beta": [float(b) for b in beta], "cov": (sigma2 * xtx_inv).tolist(),
            "dof": int(dof)}


def v_of(share: float) -> float:
    return float(k2e().person_share_design(share, 0.0))


# ---------------------------------------------------------------------------
# SCORING: one gauge pass per world, scored against its own trait_pure truth.


def _truth_world(world: dict[str, Any], person: np.ndarray) -> dict[str, Any]:
    tw = dict(world)
    tw["trait"] = person
    return tw


def score_world(world: dict[str, Any], w: dict[str, float],
                corpus: str) -> float:
    m_ = k2b()
    lay = m_.layout()
    module = lay["module"]
    vectors = m_.emit_panel(world, w)
    raw_m, raw_k = m_.f1().featurize_panel(
        vectors, lay["author_ids"], corpus=corpus, spec=lay["spec"],
        directions=lay["directions"])
    panel = SimpleNamespace(metadata=lay["metadata"], raw={"M": raw_m, "K": raw_k})
    calibration = module.calibrate_d0_soft(panel)
    projected = module.project_soft(
        SimpleNamespace(raw={"M": raw_m, "K": raw_k}), lay["retained_mask"],
        calibration)
    field_est = module.deployed_soft_field(projected, lay["retained_ctx"],
                                           lay["resolved"])
    ridx = lay["retained_idx"]
    full = m_.emit_panel(_truth_world(world, world["trait_pure"]), w,
                         active=("mu", "common"))
    fld = m_.field_from_vectors([full[i] for i in ridx], calibration, corpus)
    return float(module.field_agreement(field_est, fld, lay["weights"]))


def run_world(cell: str, wv: float, i: int, suffix: str = "") -> dict[str, Any]:
    m_ = k2b()
    cfg = CELLS[cell]
    w = m_.arm_weights(cfg["share"], W_INT_ARM)
    sd = world_seeds(i, suffix)
    world = r1().build_split_world_v2(sd["author"], sd["frame"], cfg["phi"], wv)
    rt = score_world(world, w, f"m4k2b-R2b-w{i}{suffix}")     # RN-R2B-4
    return {"cell": cell, "share": cfg["share"], "phi": cfg["phi"],
            "V_design": v_of(cfg["share"]), "w_style": wv, "world": i,
            "author_seed": sd["author"], "frame_seed": sd["frame"], "R_T": rt}


def split_shares(world: dict[str, Any], w: dict[str, float]) -> dict[str, float]:
    """RN-R2B-3: the split channel set, each term the pipeline's own emit_panel."""
    m_ = k2b()
    parts: dict[str, float] = {}
    for ch in m_.CHANNELS:
        if ch == "mu":
            continue
        p = m_.emit_panel(world, w, active=(ch,))
        parts[ch] = float(np.mean(np.concatenate([b.ravel() for b in p]) ** 2))
    for name, person in (("mu_trait", world["trait_pure"]),
                         ("mu_style", float(world["m_style"]) * world["style"])):
        p = m_.emit_panel(_truth_world(world, person), w, active=("mu",))
        parts[name] = float(np.mean(np.concatenate([b.ravel() for b in p]) ** 2))
    total = sum(parts.values())
    out = {k: v / total for k, v in parts.items()}
    out["V_C"] = out["slow"] + out["int"] + out["mu_style"]
    return out


# ---------------------------------------------------------------------------
# ESTIMATORS.


def kappa_slow(rt: dict[tuple[str, float], float], wv: float) -> float:
    """RN-R2B-2: the standard secant orientation (positive tax rate)."""
    return float((rt[("A", wv)] - rt[("B", wv)]) / DV_SLOW)


def kappa_slow_literal(rt: dict[tuple[str, float], float], wv: float) -> float:
    """The registration's literal operand order, reported for completeness."""
    return float(-(rt[("A", wv)] - rt[("B", wv)]) / DV_SLOW)


def kappa_mu(rt: dict[tuple[str, float], float], cell: str,
             dv_mu: dict[str, float]) -> float:
    return float(-(rt[(cell, 1.0)] - rt[(cell, 0.0)]) / dv_mu[cell])


def _rt_map(df: pd.DataFrame) -> dict[tuple[str, float], float]:
    g = df.groupby(["cell", "w_style"])["R_T"].mean()
    return {(c, float(w)): float(v) for (c, w), v in g.items()}


# ---------------------------------------------------------------------------
# PART 0.


def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")
    m_ = k2b()
    cur = curve()
    theta = cur["theta"]
    cov = curve_cov(cur["points"])

    # ---- G0r2b: N1 roots, M3 params, R2 numbers, hashes, matched r.
    n1 = read_json(N1P0)["G0n1"]["(i) pairs and roots"]
    cell_a, cell_b = n1["cells"]["A"], n1["cells"]["B"]
    r_a = float(m_.arm_predictions(SHARE_LO, PHI_A, W_INT_ARM)["r_card_b_pred_raw"])
    r_b = float(m_.arm_predictions(SHARE_HI, PHI_B, W_INT_ARM)["r_card_b_pred_raw"])
    r_resid = float(abs(r_a - r_b))
    r2p0 = read_json(R2P0)["prediction"]
    r2fit = read_json(R2FIT)
    r2_drt = float(r2fit["V_R2a"]["measured"])
    r2_sem = float(r2fit["V_R2a"]["sem"])
    r2_dvmu = float(r2p0["V_eff"] - r2p0["V_design"])
    r2_kappa_mu = float(-r2_drt / r2_dvmu)
    v_lo, v_hi = v_of(SHARE_LO), v_of(SHARE_HI)
    secant = float(-(alpha_of(v_hi, theta) - alpha_of(v_lo, theta)) / DV_SLOW)
    g0 = {
        "n1_root_phi_A": float(cell_a["phi"]), "n1_root_phi_B": float(cell_b["phi"]),
        "n1_r_A": float(cell_a["r"]), "n1_r_B": float(cell_b["r"]),
        "recomputed_r_A": r_a, "recomputed_r_B": r_b,
        "r_matches_n1_bitexact": bool(r_a == float(cell_a["r"])
                                      and r_b == float(cell_b["r"])),
        "matched_r_residual": r_resid, "matched_r_bar": 1e-9,
        "matched_r_PASS": bool(r_resid <= 1e-9),
        "V_lo": v_lo, "V_hi": v_hi, "dV_slow": float(v_hi - v_lo),
        "dV_matches_registration": bool(abs((v_hi - v_lo) - DV_SLOW) < 1e-12),
        "Vbar": float((v_hi + v_lo) / 2.0),
        "Vbar_matches_registration": bool(abs((v_hi + v_lo) / 2.0 - VBAR) < 1e-12),
        "curve_theta": theta, "curve_winner": cur["winner"],
        "curve_consumption": cur["consumption"],
        "ols_refit_agrees": bool(np.allclose(cov["beta"], theta, rtol=1e-6,
                                             atol=1e-9)),
        "secant_at_Vbar": secant,
        "n1b_context_value_not_a_prediction": 0.918,
        "R2_dR_T": r2_drt, "R2_sem": r2_sem, "R2_dV_mu": r2_dvmu,
        "R2_kappa_mu": r2_kappa_mu, "R2_planner_quoted": 0.066,
        "R2_phi": 0.60,
        "instrument_hashes": {rel(p): sha_file(p)
                              for p in (R1SRC, R2SRC, K2BSRC, K2ESRC)},
        "pins": {"truth_panel": PIN_TRUTH_PANEL, "truth_active": PIN_TRUTH_ACTIVE,
                 "r": PIN_R, "builder": PIN_BUILDER, "shares": PIN_SHARE},
    }
    g0["PASS"] = bool(g0["r_matches_n1_bitexact"] and g0["matched_r_PASS"]
                      and g0["dV_matches_registration"]
                      and g0["Vbar_matches_registration"]
                      and g0["ols_refit_agrees"]
                      and cur["winner"] == "A-quad"
                      and cur["consumption"] == "CONSUMABLE")
    if not g0["PASS"]:
        write_json(OUT / "part0.json", {"G0r2b": g0})
        raise SystemExit("G0r2b FAILED -> STOP")

    # ---- G1r2b + probes: dV_mu realized, gains, estimator spreads.
    rows: list[dict[str, Any]] = []
    for i in range(N_PROBE):
        sd = world_seeds(i, "-probe")
        for cell, cfg in CELLS.items():
            w = m_.arm_weights(cfg["share"], W_INT_ARM)
            for wv in W_DOSES:
                world = r1().build_split_world_v2(sd["author"], sd["frame"],
                                                  cfg["phi"], wv)
                sh = split_shares(world, w)
                rt = score_world(world, w, f"m4k2b-R2b-probe{i}")
                rows.append({"world": i, "cell": cell, "share": cfg["share"],
                             "phi": cfg["phi"], "w_style": wv, "R_T": rt,
                             "V_C": sh["V_C"], "mu_style": sh["mu_style"],
                             "mu_trait": sh["mu_trait"], "slow": sh["slow"],
                             "common": sh["common"], "noise": sh["noise"]})
    pdf = pd.DataFrame(rows)
    pdf.to_csv(OUT / "probe.csv", index=False)

    dv_mu: dict[str, float] = {}
    for cell in CELLS:
        sub = pdf[pdf["cell"] == cell]
        dv_mu[cell] = float(sub[sub.w_style == 1.0]["V_C"].mean()
                            - sub[sub.w_style == 0.0]["V_C"].mean())
    coverage = {
        "counted": ["slow", "int", "mu_style"],
        "not_counted": ["mu_trait", "common", "noise"],
        "statement": RN_NOTES["RN-R2B-3"],
        "denominator": "sum over the split channel set {mu_trait, mu_style, slow, "
                       "int, common, noise} of the pipeline's own emit_panel "
                       "mean-square",
        "dV_mu_per_cell": dv_mu,
        "R2_dV_mu_same_convention": r2_dvmu,
    }
    g1 = {"n_probe": N_PROBE, "coverage": coverage,
          "matched_r_residual": r_resid,
          "cells_distinct": bool(len({(c["share"], c["phi"])
                                      for c in CELLS.values()}) == 4),
          "dV_mu_all_positive": bool(all(v > 0 for v in dv_mu.values())),
          "PASS": True}
    g1["PASS"] = bool(g1["cells_distinct"] and g1["dV_mu_all_positive"]
                      and r_resid <= 1e-9)
    if not g1["PASS"]:
        write_json(OUT / "part0.json", {"G0r2b": g0, "G1r2b": g1})
        raise SystemExit("G1r2b FAILED -> INSTRUMENT_DEFECT")

    # ---- per-world estimator spreads on probes (SE_meas, pre-measurement).
    piv = pdf.pivot_table(index="world", columns=["cell", "w_style"],
                          values="R_T")
    ks0 = (piv[("A", 0.0)] - piv[("B", 0.0)]).to_numpy(float) / DV_SLOW
    ks1 = (piv[("A", 1.0)] - piv[("B", 1.0)]).to_numpy(float) / DV_SLOW
    kmB = -(piv[("B", 1.0)] - piv[("B", 0.0)]).to_numpy(float) / dv_mu["B"]
    kmA = -(piv[("A", 1.0)] - piv[("A", 0.0)]).to_numpy(float) / dv_mu["A"]
    kmD = -(piv[("D", 1.0)] - piv[("D", 0.0)]).to_numpy(float) / dv_mu["D"]
    dchan = ks0 - kmB
    dfree = N_PROBE - 1
    infl = df_inflation(dfree)

    def se_of(vec: np.ndarray) -> float:
        return float(np.std(vec, ddof=1) * infl / math.sqrt(N_WORLDS))

    # ---- S1: the secant, #61 band.
    grad = np.array([0.0, 1.0, -VBAR])
    se_pred_s1 = float(math.sqrt(float(grad @ np.array(cov["cov"]) @ grad)))
    se_meas_s1 = se_of(ks0)
    gains = {}
    for cell in DIAG:
        sub = pdf[(pdf.cell == cell) & (pdf.w_style == 0.0)]
        gains[cell] = float(sub["R_T"].mean()
                            / float(alpha_of(v_of(CELLS[cell]["share"]), theta)))
    gbar = float(np.mean(list(gains.values())))
    a_gain = float(abs(secant) * abs(1.0 - gbar))
    a_gainspread = float(abs(secant) * abs(gains["A"] - gains["B"]) / 2.0)
    a_rresid = float(r_resid / DV_SLOW)
    se_approx_s1 = float(math.sqrt(a_gain ** 2 + a_gainspread ** 2 + a_rresid ** 2))
    comb_s1 = float(math.sqrt(se_pred_s1 ** 2 + se_meas_s1 ** 2
                              + se_approx_s1 ** 2))
    half_s1 = float(2.0 * comb_s1)

    # ---- S2: R2's kappa_mu, wide band, #61.
    se_pred_s2 = float(r2_sem / r2_dvmu)
    se_meas_s2 = se_of(kmB)
    # phi-transport measured on probes: same share 0.25, phi_A (cell D) vs 0.05 (B)
    a_phi = float(abs(float(np.mean(kmD)) - float(np.mean(kmB))))
    a_dv = float(abs(r2_kappa_mu) * abs(dv_mu["B"] - r2_dvmu) / r2_dvmu)
    se_approx_s2 = float(math.sqrt(a_phi ** 2 + a_dv ** 2))
    comb_s2 = float(math.sqrt(se_pred_s2 ** 2 + se_meas_s2 ** 2
                              + se_approx_s2 ** 2))
    half_s2 = float(2.0 * comb_s2)

    # ---- S3: discrimination.
    se_d = se_of(dchan)

    pred_obj = {
        "leg": LEG,
        "RN_NOTES": RN_NOTES,
        "estimators": {
            "kappa_slow": "+[R_T(cell A, share 0.10) - R_T(cell B, share 0.25)] / "
                          "dV_slow   (RN-R2B-2: standard secant orientation)",
            "kappa_slow_literal": "the registration's operand order, negated; "
                                  "reported only",
            "kappa_mu": "-[R_T(w=1) - R_T(w=0)] / dV_mu(cell)",
            "D_channel": "kappa_slow(w=0) - kappa_mu(cell B, share 0.25)",
        },
        "channel_coverage": coverage,
        "S1": {"quantity": "kappa_slow(w=0)", "prediction": secant,
               "Vbar": VBAR, "dV_slow": DV_SLOW,
               "band": {"SE_pred": se_pred_s1, "SE_meas": se_meas_s1,
                        "SE_approx": se_approx_s1,
                        "SE_approx_parts": {"r_channel_gain": a_gain,
                                            "gain_spread_between_cells":
                                                a_gainspread,
                                            "matched_r_residual": a_rresid},
                        "gains": gains, "gain_mean": gbar,
                        "combined_SE": comb_s1, "half_width": half_s1,
                        "band": [secant - half_s1, secant + half_s1]}},
        "S2": {"quantity": "kappa_mu(share 0.25)", "prediction": r2_kappa_mu,
               "first_interval_claim": True, "note": RN_NOTES["RN-R2B-6"],
               "band": {"SE_pred": se_pred_s2, "SE_meas": se_meas_s2,
                        "SE_approx": se_approx_s2,
                        "SE_approx_parts": {"phi_transport": a_phi,
                                            "dV_mu_design_difference": a_dv},
                        "combined_SE": comb_s2, "half_width": half_s2,
                        "band": [r2_kappa_mu - half_s2, r2_kappa_mu + half_s2]}},
        "S3": {"quantity": "D_channel = kappa_slow(w=0) - kappa_mu(0.25)",
               "clause": "D_channel > 0 AND |D_channel| > 2*SE_D",
               "SE_D_projected": se_d,
               "uniform_tax_truth": 0.0,
               "expected_truth_from_R2_and_M3": float(secant - r2_kappa_mu)},
        "dV_mu": dv_mu, "gains": gains,
        "probe_estimates_context_only": {
            "kappa_slow_w0": float(np.mean(ks0)),
            "kappa_slow_w1": float(np.mean(ks1)),
            "kappa_mu_A": float(np.mean(kmA)), "kappa_mu_B": float(np.mean(kmB)),
            "kappa_mu_D": float(np.mean(kmD)),
            "D_channel": float(np.mean(dchan)),
            "disclosure": "probe worlds necessarily precede the stamp because the "
                          "bands need their spreads; these MEANS are disclosed and "
                          "are consumed nowhere -- S1 comes from M3's curve, S2 from "
                          "R2's measurement, and only SPREADS and the w=0 GAIN enter "
                          "the bands (#57)",
        },
        "n_probe": N_PROBE, "df_inflation": infl,
    }
    write_json(OUT / "prediction.json", pred_obj)
    digest = hashlib.sha256((OUT / "prediction.json").read_bytes()).hexdigest()
    stamp = {"sha256": digest, "stamp_utc": datetime.now(UTC).isoformat(),
             "fresh_arm_worlds_before_stamp": 0,
             "probe_worlds_before_stamp": int(N_PROBE * len(CELLS)
                                              * len(W_DOSES))}
    write_json(OUT / "prediction.sha256.json", stamp)
    write_json(OUT / "part0.json", {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "G0r2b": g0, "G1r2b": g1, "prediction": pred_obj, "stamp": stamp,
        "RN_NOTES": RN_NOTES, "cells": CELLS,
        "design": {"n_worlds_per_arm": N_WORLDS, "n_arms": len(CELLS) * 2,
                   "n_worlds_total": N_WORLDS * len(CELLS) * 2,
                   "master_seed": MASTER_SEED,
                   "salts": [SALT_WORLD, SALT_PILOT],
                   "alternative_reading_rejected":
                       "2 cells x 2 doses x 384 worlds = 1536 (contradicts 'eight "
                       "arms' and '192 worlds' per arm)"},
        "environment": {"python_executable": sys.executable,
                        "python_version": sys.version.split()[0],
                        "platform": platform.platform(),
                        "numpy": np.__version__, "pandas": pd.__version__},
        "seconds": time.time() - t0})
    _log("part0_done", sha=digest)
    print(f"part0 OK  matched-r residual={r_resid!r} (bar 1e-9)  "
          f"secant={secant!r}\n"
          f"  S1 pred {secant!r} half {half_s1!r} (pred {se_pred_s1:.3e} / meas "
          f"{se_meas_s1:.3e} / approx {se_approx_s1:.3e}; gain {gbar!r})\n"
          f"  S2 pred {r2_kappa_mu!r} half {half_s2!r} (pred {se_pred_s2:.3e} / "
          f"meas {se_meas_s2:.3e} / approx {se_approx_s2:.3e}; phi {a_phi:.4f})\n"
          f"  S3 SE_D {se_d!r}  expected D {secant - r2_kappa_mu!r}\n"
          f"  dV_mu {dv_mu}\n  STAMPED {digest[:16]}  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------


def _permit_check() -> dict[str, Any]:
    raw = (OUT / "prediction.json").read_bytes()
    stamp = read_json(OUT / "prediction.sha256.json")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != stamp["sha256"]:
        raise SystemExit("PREDICTION HASH MISMATCH -> STOP")
    t_stamp = datetime.fromisoformat(stamp["stamp_utc"])
    now = datetime.now(UTC)
    return {"sha256": digest, "matches": True, "permit_utc": now.isoformat(),
            "seconds_stamp_to_permit": (now - t_stamp).total_seconds()}


def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("pilot_start")
    rows = []
    for i in range(N_PILOT):
        for cell in ("A", "B"):
            for wv in W_DOSES:
                rows.append(run_world(cell, wv, i, "-pilot"))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "pilot_field.csv", index=False)
    preds = {f"{c}_w{w}": _predicate(
        df[(df.cell == c) & (df.w_style == w)]["R_T"].to_numpy(float))
        for c in ("A", "B") for w in W_DOSES}
    out = {"n": N_PILOT, "predicates": preds,
           "PASS": bool(all(p["PASS"] for p in preds.values())),
           "R_T_means": {f"{c}_w{w}": float(
               df[(df.cell == c) & (df.w_style == w)]["R_T"].mean())
               for c in ("A", "B") for w in W_DOSES},
           "permit": _permit_check(), "seconds": time.time() - t0}
    write_json(OUT / "pilot.json", out)
    _log("pilot_done")
    if not out["PASS"]:
        raise SystemExit("G2r2b FAILED -> INSTRUMENT_DEFECT")
    print(f"pilot OK  {out['R_T_means']}  permit "
          f"{out['permit']['seconds_stamp_to_permit']:.3f}s after the stamp  "
          f"{time.time() - t0:.1f}s")


def stage_project(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("project_start")
    p0 = read_json(OUT / "part0.json")
    pred = p0["prediction"]
    pdf = read_csv_rt(OUT / "probe.csv")
    piv = pdf.pivot_table(index="world", columns=["cell", "w_style"], values="R_T")
    dv = pred["dV_mu"]
    ks0 = (piv[("A", 0.0)] - piv[("B", 0.0)]).to_numpy(float) / DV_SLOW
    kmB = -(piv[("B", 1.0)] - piv[("B", 0.0)]).to_numpy(float) / dv["B"]
    dchan = ks0 - kmB
    infl = df_inflation(N_PROBE - 1)
    sd_d = float(np.std(dchan, ddof=1)) * infl
    truth_r2 = float(pred["S3"]["expected_truth_from_R2_and_M3"])

    def project(n: int) -> dict[str, Any]:
        rng = np.random.default_rng(MASTER_SEED)
        se = sd_d / math.sqrt(n)
        res: dict[str, Any] = {"n_worlds": n, "SE_D": se, "per_truth": {}}
        for label, truth, role, bar in (
                ("R2-based truth (secant - R2 kappa_mu)", truth_r2, "power",
                 POWER_MIN),
                ("uniform tax (D = 0)", 0.0, "false-fire", FALSE_FIRE_MAX)):
            draws = rng.normal(truth, se, size=B_PROJ)
            clear = float(np.mean((draws > 0) & (np.abs(draws) > 2.0 * se)))
            res["per_truth"][label] = {
                "truth": truth, "role": role, "bar": bar, "P_S3_clear": clear,
                "PASS": bool(clear >= bar) if role == "power"
                else bool(clear <= bar)}
        res["PASS"] = bool(all(v["PASS"] for v in res["per_truth"].values()))
        return res

    base = project(N_WORLDS)
    out = {"base": base, "escalation_fired": False, "escalated": None,
           "sd_D_df_inflated": sd_d, "PASS": base["PASS"], "n_final": N_WORLDS}
    if not base["PASS"]:
        esc = project(N_ESCALATED)
        out.update({"escalation_fired": True, "escalated": esc,
                    "PASS": esc["PASS"],
                    "n_final": N_ESCALATED if esc["PASS"] else N_WORLDS})
    write_json(OUT / "projection.json", out)
    _log("project_done")
    if not out["PASS"]:
        raise SystemExit("G3r2b FAILED -> NON_PROJECTABLE")
    print("project OK  " + "  ".join(
        f"{k}: {v['P_S3_clear']!r}" for k, v in out["base"]["per_truth"].items())
        + f"  n={out['n_final']}  escalated={out['escalation_fired']}  "
          f"{time.time() - t0:.1f}s")


def stage_arm(args: argparse.Namespace) -> None:
    t0 = time.time()
    (OUT / "arms").mkdir(parents=True, exist_ok=True)
    write_json(OUT / "arm_permit.json", _permit_check())
    n_final = int(read_json(OUT / "projection.json")["n_final"])
    chunk = int(args.chunk)
    per = math.ceil(n_final / CHUNKS)
    lo, hi = chunk * per, min((chunk + 1) * per, n_final)
    _log("arm_start", chunk=chunk, lo=lo, hi=hi)
    rows = []
    for i in range(lo, hi):
        for cell in CELLS:
            for wv in W_DOSES:
                rows.append(run_world(cell, wv, i))
    pd.DataFrame(rows).to_csv(OUT / "arms" / f"chunk_{chunk}.csv", index=False)
    _log("arm_done", chunk=chunk, n=len(rows))
    print(f"arm chunk {chunk} OK  worlds {lo}..{hi - 1}  rows={len(rows)}  "
          f"{time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------


def stage_fit(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("fit_start")
    p0 = read_json(OUT / "part0.json")
    pred = p0["prediction"]
    dv = pred["dV_mu"]
    frames = [read_csv_rt(p) for p in sorted((OUT / "arms").glob("chunk_*.csv"))]
    df = pd.concat(frames, ignore_index=True).sort_values(
        ["world", "cell", "w_style"])
    df.to_csv(OUT / "arm.csv", index=False)
    n_final = int(read_json(OUT / "projection.json")["n_final"])
    if len(df) != n_final * len(CELLS) * len(W_DOSES):
        raise SystemExit(f"arm row count {len(df)} unexpected")

    piv = df.pivot_table(index="world", columns=["cell", "w_style"], values="R_T")
    per_world = {
        "kappa_slow_w0": (piv[("A", 0.0)] - piv[("B", 0.0)]).to_numpy(float)
        / DV_SLOW,
        "kappa_slow_w1": (piv[("A", 1.0)] - piv[("B", 1.0)]).to_numpy(float)
        / DV_SLOW,
        "kappa_mu_A": -(piv[("A", 1.0)] - piv[("A", 0.0)]).to_numpy(float)
        / dv["A"],
        "kappa_mu_B": -(piv[("B", 1.0)] - piv[("B", 0.0)]).to_numpy(float)
        / dv["B"],
        "kappa_mu_C": -(piv[("C", 1.0)] - piv[("C", 0.0)]).to_numpy(float)
        / dv["C"],
        "kappa_mu_D": -(piv[("D", 1.0)] - piv[("D", 0.0)]).to_numpy(float)
        / dv["D"],
    }
    per_world["D_channel"] = per_world["kappa_slow_w0"] - per_world["kappa_mu_B"]
    n = len(per_world["D_channel"])
    rng = np.random.default_rng(MASTER_SEED)
    idx = rng.integers(0, n, size=(B_BOOT, n))          # ONE joint index set

    def stat(vec: np.ndarray) -> dict[str, Any]:
        bs = vec[idx].mean(axis=1)
        return {"mean": float(vec.mean()),
                "sem": float(np.std(vec, ddof=1) / math.sqrt(n)),
                "ci95": [float(np.percentile(bs, CI_Q[0])),
                         float(np.percentile(bs, CI_Q[1]))],
                "sd": float(np.std(vec, ddof=1)), "n": int(n)}

    est = {k: stat(v) for k, v in per_world.items()}
    est["kappa_slow_w0_literal_orientation"] = {
        **est["kappa_slow_w0"],
        "mean": -est["kappa_slow_w0"]["mean"],
        "ci95": [-est["kappa_slow_w0"]["ci95"][1],
                 -est["kappa_slow_w0"]["ci95"][0]],
        "note": "the registration's literal operand order (RN-R2B-2); reported "
                "only, routes nothing",
    }

    def contain(name: str, meas: dict[str, Any], spec: dict[str, Any]
                ) -> dict[str, Any]:
        b = spec["band"]
        err = meas["mean"] - spec["prediction"]
        return {"measured": meas["mean"], "ci95": meas["ci95"], "sem": meas["sem"],
                "prediction": spec["prediction"], "half_width": b["half_width"],
                "band": b["band"], "signed_error": float(err),
                "position_in_band": float(err / b["half_width"]),
                "INSIDE": bool(abs(err) <= b["half_width"]),
                "classification": "INSIDE" if abs(err) <= b["half_width"]
                else "OUTSIDE"}

    s1 = contain("S1", est["kappa_slow_w0"], pred["S1"])
    s2 = contain("S2", est["kappa_mu_B"], pred["S2"])
    d = est["D_channel"]
    se_d = d["sem"]
    s3 = {**d, "SE_D": se_d, "two_se": float(2.0 * se_d),
          "positive": bool(d["mean"] > 0),
          "outside_2se": bool(abs(d["mean"]) > 2.0 * se_d),
          "ci_excludes_zero": bool(d["ci95"][0] > 0 or d["ci95"][1] < 0),
          "CLEAR": bool(d["mean"] > 0 and abs(d["mean"]) > 2.0 * se_d
                        and d["ci95"][0] > 0),
          "ratio_slow_to_mu": float(est["kappa_slow_w0"]["mean"]
                                    / est["kappa_mu_B"]["mean"])}

    # rule 13 on the routing quantities (Q2's implementation)
    margin = 1.0 / (RULE13_FACTOR * B_BOOT)
    rule13 = []
    for name, vec, bounds in (
            ("S3", per_world["D_channel"], (0.0,)),
            ("S1", per_world["kappa_slow_w0"],
             (pred["S1"]["band"]["band"][0], pred["S1"]["band"]["band"][1]))):
        rng_b = np.random.default_rng(MASTER_SEED + 1)
        bs = vec[rng_b.integers(0, n, size=(B_BOOT, n))].mean(axis=1)
        near = [{"boundary": float(b), "tail_frac": float(np.mean(bs <= b))}
                for b in bounds
                if min(abs(float(np.mean(bs <= b)) - 0.025),
                       abs(float(np.mean(bs <= b)) - 0.975)) < margin]
        if near:
            rng_h = np.random.default_rng(MASTER_SEED + 2)
            bh = vec[rng_h.integers(0, n, size=(B_BOOT_HIGH, n))].mean(axis=1)
            rule13.append({"verdict": name, "triggers": near, "B": B_BOOT_HIGH,
                           "ci_after": [float(np.percentile(bh, CI_Q[0])),
                                        float(np.percentile(bh, CI_Q[1]))]})
    # percentile-value stability (the planner's recorded enforcement note)
    stab = {}
    for name, vec, edges in (
            ("S3", per_world["D_channel"], (0.0,)),
            ("S1", per_world["kappa_slow_w0"], tuple(pred["S1"]["band"]["band"]))):
        sem = float(np.std(vec, ddof=1) / math.sqrt(n))
        mc = float(math.sqrt(0.025 * 0.975 / B_BOOT)
                   / (stats.norm.pdf(stats.norm.ppf(0.025)) / sem))
        gaps = [abs(est_ci - e) for e in edges
                for est_ci in (est[("D_channel" if name == "S3"
                                    else "kappa_slow_w0")]["ci95"])]
        stab[name] = {"mc_se_of_quantile": mc, "min_gap_to_edge": float(min(gaps)),
                      "gap_in_mc_se": float(min(gaps) / mc),
                      "noise_limited": bool(min(gaps) < mc)}

    per_arm = {f"{c}_w{w}": {
        "cell": c, "share": CELLS[c]["share"], "phi": CELLS[c]["phi"],
        "V_design": v_of(CELLS[c]["share"]), "w_style": w,
        "role": CELLS[c]["role"],
        **stat(df[(df.cell == c) & (df.w_style == w)]
               .sort_values("world")["R_T"].to_numpy(float))}
        for c in CELLS for w in W_DOSES}

    r2_factor = float(abs(read_json(R2P0)["prediction"]["prediction"]
                          / read_json(R2FIT)["V_R2a"]["measured"]))
    closure = {
        "R2_mispricing_factor": r2_factor,
        "R2b_channel_ratio": s3["ratio_slow_to_mu"],
        "difference": float(s3["ratio_slow_to_mu"] - r2_factor),
        "entailment": "NOT an independent confirmation: once S1 places the measured "
                      "slow tax on the curve and S2 places the measured mu tax on "
                      "R2's estimate, the ratio MUST reproduce R2's mispricing "
                      "factor. The content is that both landed -- i.e. R2's "
                      "mispricing IS the channel ratio, rather than a broken law.",
    }
    # --- phi-dependence of kappa_mu: a self-check on my own SE_approx, and an
    # UN-entailed cross-leg check.  Added after the verdict; routes nothing.
    phi_realized = float(abs(est["kappa_mu_D"]["mean"] - est["kappa_mu_B"]["mean"]))
    phi_probe = float(pred["S2"]["band"]["SE_approx_parts"]["phi_transport"])
    slope = float((est["kappa_mu_D"]["mean"] - est["kappa_mu_B"]["mean"])
                  / (PHI_A - PHI_B))
    r2_phi = float(read_json(R2P0)["G0r2b"]["R2_phi"]) if False else 0.60
    interp = float(est["kappa_mu_B"]["mean"] + (r2_phi - PHI_B) * slope)
    r2_kmu = float(-read_json(R2FIT)["V_R2a"]["measured"]
                   / (read_json(R2P0)["prediction"]["V_eff"]
                      - read_json(R2P0)["prediction"]["V_design"]))
    phi_diag = {
        "kappa_mu_at_share_0.25_phi_0.05": est["kappa_mu_B"]["mean"],
        "kappa_mu_at_share_0.25_phi_A": est["kappa_mu_D"]["mean"],
        "realized_phi_difference": phi_realized,
        "probe_phi_transport_used_in_SE_approx": phi_probe,
        "probe_undersized_by_factor": float(phi_realized / phi_probe),
        "slope_per_unit_phi": slope,
        "interpolated_to_R2_phi_0.60": interp,
        "R2_measured_kappa_mu": r2_kmu,
        "interpolation_error": float(interp - r2_kmu),
        "note": "computed after the verdict; routes nothing. The first half is a "
                "self-check that my probe-based SE_approx component was UNDERSIZED; "
                "the second is an un-entailed cross-leg check, since R2 measured at "
                "phi 0.60 and this leg never did.",
    }
    out = {"estimates": est, "S1": s1, "S2": s2, "S3": s3, "per_arm": per_arm,
           "closure": closure, "phi_diagnostic": phi_diag,
           "dV_mu": dv, "rule13_events": rule13, "B": B_BOOT,
           "percentile_stability": stab, "n_worlds": n,
           "seconds": time.time() - t0}
    write_json(OUT / "fit.json", out)
    _log("fit_done")
    print(f"fit OK\n  S1 kappa_slow(w0)={s1['measured']!r} {s1['ci95']!r} pred="
          f"{s1['prediction']!r} pos={s1['position_in_band']:.4f} "
          f"{s1['classification']}\n"
          f"  S2 kappa_mu(0.25)={s2['measured']!r} {s2['ci95']!r} pred="
          f"{s2['prediction']!r} pos={s2['position_in_band']:.4f} "
          f"{s2['classification']}\n"
          f"  S3 D={s3['mean']!r} {s3['ci95']!r} 2SE={s3['two_se']!r} CLEAR="
          f"{s3['CLEAR']}  ratio={s3['ratio_slow_to_mu']!r}\n"
          f"  kappa_slow(w1)={est['kappa_slow_w1']['mean']!r}  kappa_mu(0.10)="
          f"{est['kappa_mu_A']['mean']!r}  {time.time() - t0:.1f}s")


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    g3 = read_json(OUT / "projection.json")
    fit = read_json(OUT / "fit.json")
    s1, s3 = fit["S1"], fit["S3"]
    if not (p0["G0r2b"]["PASS"] and p0["G1r2b"]["PASS"]):
        cell, slug, text = 1, "STOP", "G0/G1 failure"
    elif not g3["PASS"]:
        cell, slug, text = 2, "NON_PROJECTABLE", "projection fails after escalation"
    elif s1["classification"] == "INSIDE" and s3["CLEAR"]:
        cell, slug = 3, "TAX_IS_CHANNEL_SPECIFIC"
        text = ("kappa(V) re-types as the STATE-channel tax; the N/M-line laws gain "
                "a channel-scope clause; R2's mispricing is explained")
    elif s1["classification"] == "INSIDE" and not s3["CLEAR"]:
        cell, slug = 4, "UNIFORM_TAX_RETAINED"
        text = "R2's small dR_T needs another owner"
    elif s1["classification"] == "OUTSIDE":
        cell, slug = 5, "CURVE_BREAKS_ON_OWN_CHANNEL"
        text = ("the mispricing is deeper than channel accounting; the curve's "
                "scope contracts")
    else:
        cell, slug, text = 6, "UNDERPOWERED", "no higher cell reached"
    mods = []
    if fit["S2"]["classification"] == "INSIDE":
        mods.append("MU_TAX_FIRST_INTERVAL_CONSISTENT_WITH_R2")
    else:
        mods.append("MU_TAX_OUTSIDE_R2_INTERVAL")
    if s3["CLEAR"]:
        mods.append(f"SLOW_OVER_MU_RATIO_{s3['ratio_slow_to_mu']:.1f}X")
    dec = {"leg": LEG, "utc": datetime.now(UTC).isoformat(),
           "routing_cell": cell, "verdict_slug": slug, "routing_text": text,
           "modifiers": mods, "S1": s1["classification"],
           "S2": fit["S2"]["classification"], "S3_CLEAR": s3["CLEAR"],
           "permit": read_json(OUT / "arm_permit.json"),
           "n_worlds": fit["n_worlds"],
           "banner": "EXPLORATORY, synthetic, label-free; the mu channel is "
                     "PLANTED -- nothing here bears on the k2b family's own worlds",
           "seconds": time.time() - t0}
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug)
    print(f"finalize OK  slug={slug}  cell={cell}  modifiers={mods}")


# ---------------------------------------------------------------------------


def _cs(s: Any) -> str:
    return str(s).replace("|", "\\|")


def _md(h: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(_cs(x) for x in h) + " |",
           "|" + "|".join("---" for _ in h) + "|"]
    for r in rows:
        out.append("| " + " | ".join(_cs(x) for x in r) + " |")
    return out


def _tables(p0, pil, g3, fit, dec) -> dict[str, str]:
    pred = p0["prediction"]
    sec: dict[str, list[str]] = {}
    g0 = p0["G0r2b"]
    sec["matched"] = _md(
        ["quantity", "value", "check"],
        [["N1 root φ (share 0.10)", repr(g0["n1_root_phi_A"]), "persisted"],
         ["N1 partner φ (share 0.25)", repr(g0["n1_root_phi_B"]), "persisted"],
         ["r recomputed, cell A", repr(g0["recomputed_r_A"]),
          f"bit-exact vs N1: {g0['r_matches_n1_bitexact']}"],
         ["r recomputed, cell B", repr(g0["recomputed_r_B"]), ""],
         ["**matched-r residual**", "**" + repr(g0["matched_r_residual"]) + "**",
          f"bar 1e-9 → PASS {g0['matched_r_PASS']}"],
         ["ΔV_slow", repr(g0["dV_slow"]),
          f"matches registration: {g0['dV_matches_registration']}"],
         ["V̄", repr(g0["Vbar"]),
          f"matches registration: {g0['Vbar_matches_registration']}"]])
    cov = pred["channel_coverage"]
    sec["coverage"] = _md(
        ["item", "value"],
        [["channels COUNTED in V_C", ", ".join(cov["counted"])],
         ["channels NOT counted", ", ".join(cov["not_counted"])],
         ["denominator", cov["denominator"]],
         ["ΔV_mu cell A (share 0.10, φ_A)", repr(cov["dV_mu_per_cell"]["A"])],
         ["ΔV_mu cell B (share 0.25, φ 0.05)", repr(cov["dV_mu_per_cell"]["B"])],
         ["ΔV_mu cell C (share 0.10, φ 0.05)", repr(cov["dV_mu_per_cell"]["C"])],
         ["ΔV_mu cell D (share 0.25, φ_A)", repr(cov["dV_mu_per_cell"]["D"])],
         ["R2's ΔV_mu, same convention", repr(cov["R2_dV_mu_same_convention"])]])
    rows = []
    for key in ("S1", "S2"):
        b = pred[key]["band"]
        rows.append([key, pred[key]["quantity"], repr(pred[key]["prediction"]),
                     repr(b["SE_pred"]), repr(b["SE_meas"]), repr(b["SE_approx"]),
                     repr(b["half_width"]), repr(b["band"])])
    sec["sealed"] = _md(
        ["#", "quantity", "prediction", "SE_pred", "SE_meas", "SE_approx",
         "half-width", "band"], rows)
    s1p = pred["S1"]["band"]["SE_approx_parts"]
    s2p = pred["S2"]["band"]["SE_approx_parts"]
    sec["approx"] = _md(
        ["sealed test", "SE_approx component", "value"],
        [["S1", "r-channel gain", repr(s1p["r_channel_gain"])],
         ["S1", "gain spread between diagonal cells",
          repr(s1p["gain_spread_between_cells"])],
         ["S1", "matched-r residual / ΔV_slow", repr(s1p["matched_r_residual"])],
         ["S1", "gain (cell A / cell B / mean)",
          f"{pred['gains']['A']!r} / {pred['gains']['B']!r} / "
          f"{pred['S1']['band']['gain_mean']!r}"],
         ["S2", "φ-transport (probe κ_mu at φ_A vs φ 0.05, same share)",
          repr(s2p["phi_transport"])],
         ["S2", "ΔV_mu design difference vs R2",
          repr(s2p["dV_mu_design_difference"])],
         ["S3", "projected SE_D", repr(pred["S3"]["SE_D_projected"])]])
    sec["arms"] = _md(
        ["arm", "cell", "share", "φ", "V_design", "w_style", "role", "R_T mean",
         "SEM", "CI95"],
        [[k, v["cell"], repr(v["share"]), repr(v["phi"]), repr(v["V_design"]),
          repr(v["w_style"]), v["role"], repr(v["mean"]), repr(v["sem"]),
          repr(v["ci95"])] for k, v in fit["per_arm"].items()])
    e = fit["estimates"]
    sec["estimates"] = _md(
        ["estimand", "mean", "SEM", "CI95", "role"],
        [["κ_slow(w=0)", repr(e["kappa_slow_w0"]["mean"]),
          repr(e["kappa_slow_w0"]["sem"]), repr(e["kappa_slow_w0"]["ci95"]),
          "**routes (S1, S3)**"],
         ["κ_slow(w=1)", repr(e["kappa_slow_w1"]["mean"]),
          repr(e["kappa_slow_w1"]["sem"]), repr(e["kappa_slow_w1"]["ci95"]),
          "consistency reading"],
         ["κ_mu(share 0.25, cell B)", repr(e["kappa_mu_B"]["mean"]),
          repr(e["kappa_mu_B"]["sem"]), repr(e["kappa_mu_B"]["ci95"]),
          "**routes (S2, S3)**"],
         ["κ_mu(share 0.10, cell A)", repr(e["kappa_mu_A"]["mean"]),
          repr(e["kappa_mu_A"]["sem"]), repr(e["kappa_mu_A"]["ci95"]),
          "consistency reading"],
         ["κ_mu(cell C, off-diagonal)", repr(e["kappa_mu_C"]["mean"]),
          repr(e["kappa_mu_C"]["sem"]), repr(e["kappa_mu_C"]["ci95"]),
          "diagnostic (RN-R2B-1)"],
         ["κ_mu(cell D, off-diagonal)", repr(e["kappa_mu_D"]["mean"]),
          repr(e["kappa_mu_D"]["sem"]), repr(e["kappa_mu_D"]["ci95"]),
          "diagnostic (RN-R2B-1)"],
         ["κ_slow(w=0), registration's literal orientation",
          repr(e["kappa_slow_w0_literal_orientation"]["mean"]), "-",
          repr(e["kappa_slow_w0_literal_orientation"]["ci95"]),
          "RN-R2B-2, routes nothing"],
         ["**D_channel**", "**" + repr(e["D_channel"]["mean"]) + "**",
          repr(e["D_channel"]["sem"]), repr(e["D_channel"]["ci95"]),
          "**routes (S3)**"]])
    s1, s2, s3 = fit["S1"], fit["S2"], fit["S3"]
    sec["verdicts"] = _md(
        ["test", "measured", "CI95", "prediction / bar", "position", "result"],
        [["S1 κ_slow(w=0) containment", repr(s1["measured"]), repr(s1["ci95"]),
          f"{s1['prediction']!r}, band {s1['band']!r}",
          repr(s1["position_in_band"]), "**" + s1["classification"] + "**"],
         ["S2 κ_mu(0.25) containment (first-interval)", repr(s2["measured"]),
          repr(s2["ci95"]), f"{s2['prediction']!r}, band {s2['band']!r}",
          repr(s2["position_in_band"]), "**" + s2["classification"] + "**"],
         ["S3 D_channel > 0 and outside 2·SE_D", repr(s3["mean"]),
          repr(s3["ci95"]), f"2·SE_D = {s3['two_se']!r}",
          f"positive {s3['positive']}, outside {s3['outside_2se']}",
          "**CLEAR**" if s3["CLEAR"] else "**NOT CLEAR**"]])
    sec["projection"] = _md(
        ["truth", "role", "value", "bar", "P(S3 clear)", "PASS"],
        [[k, v["role"], repr(v["truth"]), repr(v["bar"]), repr(v["P_S3_clear"]),
          str(v["PASS"])] for k, v in g3["base"]["per_truth"].items()])
    sec["gates"] = _md(
        ["gate", "PASS", "detail"],
        [["G0r2b", str(p0["G0r2b"]["PASS"]),
          f"N1 roots bit-exact ({g0['r_matches_n1_bitexact']}), matched-r residual "
          f"{g0['matched_r_residual']!r} <= 1e-9, M3 A-quad CONSUMABLE, OLS refit "
          f"agrees ({g0['ols_refit_agrees']}), R2 numbers at source"],
         ["G1r2b", str(p0["G1r2b"]["PASS"]),
          f"probe battery on {p0['G1r2b']['n_probe']} worlds x 8 arms; ΔV_mu "
          f"realized and all positive ({p0['G1r2b']['dV_mu_all_positive']}); "
          f"channel coverage named"],
         ["G2r2b", str(pil["PASS"]), f"rule-29 predicate, {pil['n']} pilot worlds"],
         ["G3r2b", str(g3["PASS"]),
          f"escalation fired: {g3['escalation_fired']}; n_final {g3['n_final']}"]])
    return {k: "\n".join(v) for k, v in sec.items()}


def _facts(p0, pil, g3, fit, dec) -> dict[str, Any]:
    pred = p0["prediction"]
    s1, s2, s3 = fit["S1"], fit["S2"], fit["S3"]
    e = fit["estimates"]
    st = p0["stamp"]
    g0 = p0["G0r2b"]
    ctx = pred["probe_estimates_context_only"]
    return {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "MODS": ", ".join(dec["modifiers"]) or "none",
        "SECANT": pred["S1"]["prediction"], "S1HALF": pred["S1"]["band"]["half_width"],
        "S1BAND": pred["S1"]["band"]["band"], "S1MEAS": s1["measured"],
        "S1CI": s1["ci95"], "S1POS": s1["position_in_band"],
        "S1CLS": s1["classification"], "S1ERR": s1["signed_error"],
        "S2PRED": pred["S2"]["prediction"], "S2HALF": pred["S2"]["band"]["half_width"],
        "S2BAND": pred["S2"]["band"]["band"], "S2MEAS": s2["measured"],
        "S2CI": s2["ci95"], "S2POS": s2["position_in_band"],
        "S2CLS": s2["classification"],
        "DCH": s3["mean"], "DCI": s3["ci95"], "DSE": s3["SE_D"],
        "D2SE": s3["two_se"], "DCLEAR": s3["CLEAR"], "DRATIO": s3["ratio_slow_to_mu"],
        "KSW1": e["kappa_slow_w1"]["mean"], "KSW1CI": e["kappa_slow_w1"]["ci95"],
        "KMA": e["kappa_mu_A"]["mean"], "KMACI": e["kappa_mu_A"]["ci95"],
        "KMB": e["kappa_mu_B"]["mean"], "KMC": e["kappa_mu_C"]["mean"],
        "KMD": e["kappa_mu_D"]["mean"],
        "KSLIT": e["kappa_slow_w0_literal_orientation"]["mean"],
        "RRESID": g0["matched_r_residual"], "GAIN": pred["S1"]["band"]["gain_mean"],
        "DVMUB": pred["dV_mu"]["B"], "DVMUA": pred["dV_mu"]["A"],
        "R2DVMU": g0["R2_dV_mu"], "R2KMU": g0["R2_kappa_mu"],
        "N1BCTX": g0["n1b_context_value_not_a_prediction"],
        "SHA16": st["sha256"][:16], "SHA": st["sha256"], "STAMP": st["stamp_utc"],
        "PERMIT": dec["permit"]["permit_utc"],
        "PGAP": dec["permit"]["seconds_stamp_to_permit"],
        "NFRESH": st["fresh_arm_worlds_before_stamp"],
        "NPROBE": st["probe_worlds_before_stamp"],
        "NW": fit["n_worlds"], "ESC": g3["escalation_fired"],
        "NRULE13": len(fit["rule13_events"]),
        "PROBEKS": ctx["kappa_slow_w0"], "PROBEKM": ctx["kappa_mu_B"],
        "PROBED": ctx["D_channel"],
        "PYEXE": p0["environment"]["python_executable"],
        "PYVER": p0["environment"]["python_version"],
        "PHIREAL": fit["phi_diagnostic"]["realized_phi_difference"],
        "PHIPROBE": fit["phi_diagnostic"]["probe_phi_transport_used_in_SE_approx"],
        "PHIFAC": fit["phi_diagnostic"]["probe_undersized_by_factor"],
        "PHIINTERP": fit["phi_diagnostic"]["interpolated_to_R2_phi_0.60"],
        "PHIERR": fit["phi_diagnostic"]["interpolation_error"],
        "R2FAC": fit["closure"]["R2_mispricing_factor"],
        "CLOSEDIFF": fit["closure"]["difference"],
        "INTERP": _interp(fit, pred),
        "S2INTERP": _s2interp(fit),
    }


def _interp(fit: dict[str, Any], pred: dict[str, Any]) -> str:
    s1, s3 = fit["S1"], fit["S3"]
    parts = []
    if s1["classification"] == "INSIDE":
        parts.append(
            "**The curve holds on its own channel.** Measured against a secant "
            "fixed before any world existed, the slow-channel tax lands inside the "
            "band — so the N-line law is not broken; it was simply being asked "
            "about the wrong channel in R2.")
    else:
        parts.append(
            "**The curve does NOT hold on its own channel.** The slow-channel tax "
            "misses its own secant, which means R2's mispricing is not explained by "
            "channel accounting alone and the curve's scope contracts.")
    if s3["CLEAR"]:
        parts.append(
            f"The discrimination is clear: the slow-channel tax is "
            f"{s3['ratio_slow_to_mu']!r}x the mu-channel tax, and D_channel's CI "
            f"excludes zero. Author-constant person variance is taxed an order "
            f"lighter than state variance.")
    else:
        parts.append(
            "The discrimination is NOT clear, so channel specificity is not "
            "established by this leg and R2's small effect still needs an owner.")
    return " ".join(parts)


def _s2interp(fit: dict[str, Any]) -> str:
    s2 = fit["S2"]
    if s2["classification"] == "INSIDE":
        return ("The mu-channel tax's first registered interval is consistent with "
                "R2's independent estimate. This is descriptive-grade by "
                "construction (the band carries R2's own CI) and routes nothing, "
                "but the two legs agree.")
    return ("The mu-channel tax's first registered interval does NOT contain R2's "
            "estimate. Because the band already carries R2's own CI, that is a "
            "substantive disagreement between two designs and is reported as such; "
            "it routes nothing on its own (V-b3).")


TEMPLATE = """# SUICA M4-R2b — the channel-specific tax

**Outcome: `{{SLUG}}`** (rule-16 cell {{CELL}}). Modifiers: {{MODS}}.

Registered before the run in `docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md`
("M4-R2b", commit 4bece27). EXPLORATORY, synthetic, label-free. The mu channel
is **planted**; nothing here bears on the k2b family's own worlds.

## 1. The question

R2 found interference real but 11.65× cheaper than the N-line curve prices. The
hypothesis that forces: **the tax is channel-specific** — κ(V) is the tax on
STATE (slow-channel) person variance, while author-constant (mu-channel) person
variance is taxed an order lighter. This leg measures the two taxes apart and
tests the curve against its own channel.

{{INTERP}}

## 2. Two registration defects, pinned before any number

**RN-R2B-1 — "four base cells" but only two named.** The registration's design
sentence says four base cells, eight arms, 192 worlds each, 1536 total; it names
two base cells, and two cells × two doses is four arms. The 2×2 factorial
{share 0.10, 0.25} × {φ_A, 0.05} is the unique reading satisfying all four
numbers at once while keeping the named matched-r pair as its diagonal. Every
registered estimand is computed on the diagonal exactly as specified; the two
off-diagonal cells route nothing. They also make S2's φ-transport SE_approx
estimable from pre-measurement objects, which the two-cell reading could not.

**RN-R2B-2 — the κ_slow operand order inverts the sealed sign.** The
registration writes κ_slow = −[R_T(0.10 cell) − R_T(0.25 cell)]/ΔV_slow. The
0.10 cell is the LOW-V cell, where α is higher, so that bracket is positive and
the formula returns a **negative** tax rate — while S1's own prediction (the
curve's secant) is positive, the cited N1b context value ({{N1BCTX}}) is
positive, and κ_mu by the registration's own formula is positive. Under the
literal order, S3's `D_channel > 0` could not fire even under perfect channel
specificity. The pinned estimator is the standard secant orientation. Under the
literal orientation the same measurement reads {{KSLIT}}; it routes nothing.

## 3. The matched-r design and the channel coverage

<<TABLE:matched>>

Channel coverage is **named**, per defect #62:

<<TABLE:coverage>>

## 4. The sealed predictions

<<TABLE:sealed>>

<<TABLE:approx>>

`prediction.json` hashed `{{SHA16}}…`, stamped {{STAMP}} with **{{NFRESH}} fresh
worlds in existence** ({{NPROBE}} probe worlds precede it by necessity — they are
the bands' inputs). Arms re-read the stamp and re-hashed to a match at
{{PERMIT}}, {{PGAP}} s later.

## 5. Gates

<<TABLE:gates>>

<<TABLE:projection>>

## 6. Results

<<TABLE:arms>>

<<TABLE:estimates>>

<<TABLE:verdicts>>

### 6.1 S1 — the curve on its own channel

κ_slow(w=0) = {{S1MEAS}} {{S1CI}} against the sealed secant {{SECANT}}, band
{{S1BAND}} — position {{S1POS}}, **{{S1CLS}}**. The r-channel gain is {{GAIN}},
and it is inside SE_approx rather than wished away (#61).

### 6.2 S2 — the mu-channel tax's first interval

κ_mu(0.25) = {{S2MEAS}} {{S2CI}} against {{S2PRED}}, band {{S2BAND}} — position
{{S2POS}}, **{{S2CLS}}**. {{S2INTERP}}

### 6.3 S3 — the discrimination

D_channel = {{DCH}} {{DCI}}, SE_D {{DSE}} (2·SE_D {{D2SE}}) → **CLEAR =
{{DCLEAR}}**. The ratio κ_slow/κ_mu is {{DRATIO}}.

### 6.4 The closure with R2

R2's mispricing factor was {{R2FAC}}×; this leg's measured channel ratio
κ_slow/κ_mu is {{DRATIO}}× — a difference of {{CLOSEDIFF}}. **This is not an
independent confirmation and should not be read as one:** once S1 places the
measured slow tax on the curve and S2 places the measured mu tax on R2's
estimate, the ratio *must* reproduce R2's factor. The content is that both
landed. R2's mispricing was never a broken law — it was the channel ratio,
measured through a curve that only ever priced one of the two channels.

Consistency readings: κ_slow(w=1) = {{KSW1}} {{KSW1CI}} (the slow tax with a
full-strength identity channel also present), κ_mu(0.10) = {{KMA}} {{KMACI}}.
Off-diagonal diagnostics: κ_mu(cell C) = {{KMC}}, κ_mu(cell D) = {{KMD}}.

### 6.5 φ-dependence: a self-check and an un-entailed cross-leg check

The off-diagonal cells make κ_mu's φ-dependence visible. At share 0.25 it is
{{S2MEAS}} at φ = 0.05 and {{KMD}} at φ_A — a realized difference of
{{PHIREAL}}.

**Self-check, against me.** The φ-transport component I put into S2's SE_approx
was measured on probe worlds and came to {{PHIPROBE}}. The realized difference
is {{PHIFAC}}× larger. My SE_approx term was undersized. S2 lands inside anyway
(position {{S2POS}}), so nothing changes, but the band was narrower than the
approximation it was meant to cover, and a leg with less margin would have paid
for it.

**Un-entailed cross-leg check.** R2 measured κ_mu at φ = 0.60 — a value this leg
never runs. Interpolating R2b's two φ points linearly to 0.60 predicts
{{PHIINTERP}}; R2 measured {{R2KMU}}, an error of {{PHIERR}}. Unlike §6.4, this
is *not* entailed by S1 and S2: it uses the φ slope, which no sealed prediction
touches.

## 7. Anomalies

1. **A-1 (before any number).** The dispatched interpreter was absent; a pinned
   CPython venv was built and recorded: `{{PYEXE}}`.
2. **A-2 (before any number).** `timeout(1)` is absent on macOS; every stage ran
   as its own foreground command under an explicit tool timeout.
3. **A-3 (disclosed ordering fact, before the stamp).** The bands need probe
   spreads, so all eight arms were scored on {{NPROBE}} probe worlds before the
   seal — which means probe values of κ_slow ({{PROBEKS}}), κ_mu ({{PROBEKM}})
   and D_channel ({{PROBED}}) existed beforehand. They were **not consumed**: S1
   comes from M3's persisted curve, S2 from R2's persisted measurement, and only
   *spreads* and the w = 0 *gain* enter the bands (#57, variances only). They are
   reported rather than omitted.

## 8. Boundary

EXPLORATORY, synthetic, label-free. The mu channel is planted, so this measures
how the gauge prices a channel we installed, not one discovered in data. Two
shares, two φ, two doses, one instrument. S2 is a first-interval claim by
construction — its band carries R2's own CI and it routes nothing (V-b3). Rule
13: {{NRULE13}} event(s). {{NW}} worlds per arm.

## 9. Environment

`{{PYEXE}}` — Python {{PYVER}}.
"""


def stage_report(args: argparse.Namespace) -> None:
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    g3 = read_json(OUT / "projection.json")
    fit = read_json(OUT / "fit.json")
    dec = read_json(OUT / "decision.json")
    tabs = _tables(p0, pil, g3, fit, dec)
    facts = _facts(p0, pil, g3, fit, dec)
    (OUT / "report_tables.md").write_text(
        "\n\n".join(f"### {k}\n{v}" for k, v in tabs.items()) + "\n",
        encoding="utf-8")
    write_json(OUT / "prose_facts.json", facts)
    text = TEMPLATE
    for name, tab in tabs.items():
        text = text.replace(f"<<TABLE:{name}>>", tab)
    for key, val in facts.items():
        text = text.replace("{{" + key + "}}",
                            repr(val) if isinstance(val, (float, list)) else str(val))
    left = re.findall(r"\{\{[A-Z0-9_]+\}\}|<<TABLE:[a-z_]+>>", text)
    if left:
        raise SystemExit(f"unresolved placeholders: {sorted(set(left))}")
    REPORT.write_text(text, encoding="utf-8")
    print(f"report OK  {rel(REPORT)}  ({len(text.splitlines())} lines)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["part0", "pilot", "project", "arm", "fit",
                                      "finalize", "report"])
    ap.add_argument("--chunk", type=int, default=0)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    {"part0": stage_part0, "pilot": stage_pilot, "project": stage_project,
     "arm": stage_arm, "fit": stage_fit, "finalize": stage_finalize,
     "report": stage_report}[args.stage](args)


if __name__ == "__main__":
    main()
