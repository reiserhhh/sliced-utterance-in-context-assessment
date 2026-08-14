#!/usr/bin/env python3
"""SUICA M4-R2 -- the gauge meets the identity channel.

Registered BEFORE run in docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md
("M4-R2", commit 49b5161).  Binding.

R1/R1b certified a PLANTED identity channel: author-persistent, trait-
independent, card-visible, monotone in dose, quantitatively recoverable.  This
leg puts the gauge in front of it and asks three questions:

  1. INTERFERENCE (SEALED).  Does planted identity crowd out the reading of
     biography, at the price the N-line tax curve names?
         dR_T = R_T_nat(w=1) - R_T_nat(w=0)  vs  alpha(V_eff) - alpha(V_design)
  2. WITHIN-FRAME style reading (DESCRIPTIVE, #59).  At w = 1 trait and style
     enter exchangeably, so R_S ~ R_T is a symmetry, not a finding.
  3. CROSS-FRAME style reading (VERDICT, NULL-first).  Style is author-stream,
     so it is PRESENT in both worlds of a pair.  Can the gauge read it across
     frames?  The P-line predicts no.

Band per #61:  half = 2 * sqrt(SE_pred^2 + SE_meas^2 + SE_approx^2), with the
r-channel shift and every derivation approximation inside SE_approx.  The
prediction and the band are HASHED before any fresh world exists (K2f).

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

LEG = "M4-R2"
OUT = ROOT / "results" / "m4_r2_gauge_meets_identity"
REPORT = ROOT / "reports" / "SUICA_M4_R2_GAUGE_MEETS_IDENTITY_REPORT.md"
PLAN = ROOT / "docs" / "SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md"

R1SRC = ROOT / "scripts" / "run_suica_m4_r1_identity_channel.py"
R1BSRC = ROOT / "scripts" / "run_suica_m4_r1b_reband.py"
P3BSRC = ROOT / "scripts" / "run_suica_m4_p3b_refresh_gradient.py"
K2BSRC = ROOT / "scripts" / "run_suica_m4_k2b_t4_branch.py"
K2ESRC = ROOT / "scripts" / "run_suica_m4_k2e_double_matching.py"
M3DEC = ROOT / "results" / "m4_m3_tax_curve" / "decision.json"

# --- the registered design -------------------------------------------------
SHARE = 0.25
W_INT_ARM = "zero"
PHI = 0.60
W_DOSES = (0.0, 1.0)
N_PAIRS = 192
N_ESCALATED = 384
MASTER_SEED = 20260814
SALT_AUTHOR = "m4r2-author"
SALT_FRAME_A = "m4r2-frameA"
SALT_FRAME_B = "m4r2-frameB"
SALT_PILOT = "m4r2-pilot"
N_PILOT = 4
N_BATTERY = 4            # G1r2's C2-style battery, "4 fresh probes"
N_PROBE = 16             # band-derivation probes (R1b's precedent)
B_BOOT = 2000
B_BOOT_HIGH = 20000
RULE13_FACTOR = 10.0
CI_Q = (2.5, 97.5)
POWER_MIN = 0.80
FALSE_FIRE_MAX = 0.10
B_PROJ = 2000
SATURATION_ABS = 0.999
CHUNKS = 4

# --- pins (rule 12: the choice rule is the registration's own sentence) -----
PIN_TRUTH_PANEL = "scripts/run_suica_m4_k2b_t4_branch.py:359-381 (emit_panel)"
PIN_TRUTH_ACTIVE = "scripts/run_suica_m4_p3b_refresh_gradient.py:409-411"
PIN_TRAIT_SITE = "scripts/run_suica_m4_k2b_t4_branch.py:371"
PIN_SHARE_DESIGN = "scripts/run_suica_m4_k2e_double_matching.py:234-241"
PIN_SHARE_REALIZED = "scripts/run_suica_m4_k2e_double_matching.py:217-231"
PIN_BUILDER = "scripts/run_suica_m4_r1_identity_channel.py:267-326"
PIN_CURVE = "results/m4_m3_tax_curve/decision.json curves.A-quad.theta"

# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-R2-1":
        "REGISTRATION DEFECT CANDIDATE, pinned BEFORE any hypothesis-relevant "
        "number.  The registration derives V_eff from 'the share accounting of "
        "person_share_design's own semantics'.  That function's IMPLEMENTATION is "
        "literally shares['slow'] + shares['int'] (k2e:240), which EXCLUDES the mu "
        "channel where style lives -- so adding style RAISES the denominator and "
        "LOWERS V_eff, making the sealed prediction POSITIVE.  That contradicts the "
        "registration's own mechanism sentence in the same paragraph ('style adds "
        "author-persistent variance, RAISING the effective person share, and the "
        "N-line curve prices that') and its sanity value (~ -0.06).  Three readings "
        "are computed and ALL are reported.  The ROUTING reading is C = (slow + int "
        "+ style)/total: it is the function's SEMANTICS (the author-persistent share "
        "that is NOT the target trait -- slow+int were exactly that set before a "
        "style channel existed; #56, inheritance is not exemption), it REDUCES to "
        "V_design exactly at w = 0, it lands INSIDE M3's fitted domain [0.03, 0.21], "
        "and it is the only reading consistent with the registration's stated "
        "mechanism.  Reading A (literal slow+int) fails the mechanism sentence and "
        "inverts the sign; reading B (slow+int+mu, i.e. counting the target trait as "
        "person) fails the w = 0 reduction and extrapolates outside the fitted "
        "domain.  The sanity value corroborates C but does NOT gate (rule 30: it is "
        "expressly approximate with 'executor recomputes'; the RN-Q2-6 precedent).",
    "RN-R2-2":
        "the corpus string must NOT encode the dose.  RN-P1-8 established that the "
        "corpus label enters the frozen map, so the SAME world under two labels "
        "scores differently by more than the effects at stake; a w-dependent corpus "
        "would contaminate the dR_T contrast at its root.  corpus = "
        "'m4k2b-R2-p{pair}', identical across doses.",
    "RN-R2-3":
        "seeds depend on the PAIR INDEX ONLY, never on w, so the two doses share "
        "author and frame streams bit-for-bit and dR_T is a WITHIN-PAIR paired "
        "difference.  This is forced by the registration's own arithmetic (192 pairs "
        "each, 384 pairs, 768 worlds = 192 indices x 2 doses x 2 worlds) and it is "
        "what makes the sealed test powerful.",
    "RN-R2-4":
        "the style truth panel is fed RAW style, not m_style*style.  At w = 1 the two "
        "coincide (m = 1); at w = 0 the m-scaled version would be an identically zero "
        "truth panel and the null anchor would be degenerate rather than informative. "
        "Both truth panels are otherwise the pipeline's own construction, unchanged: "
        "emit_panel(world, w, active=('mu','common')) with the person slot fed "
        "trait_pure or style.",
    "RN-R2-5":
        "SE_approx carries (i) the R-CHANNEL SHIFT -- this split-seed instrument sits "
        "below M3's own alpha at the same V, so the curve's currency is not exactly "
        "ours; sized as the gap between the additive prediction and the "
        "gain-corrected one, |dPred|*|1 - g| with g = R_T_probe(w=0)/alpha(V_design) "
        "measured on PROBE worlds; (ii) the V_eff estimation spread across probes "
        "propagated through the curve; (iii) the mu-channel NON-ADDITIVITY (the "
        "realized cross term between trait_pure and style) propagated through the "
        "curve.  All three are pre-measurement objects.",
    "RN-R2-6":
        "R_S_nat vs R_T_nat at w = 1 is DESCRIPTIVE and gates nothing (#59): at equal "
        "weights trait and style enter the response exchangeably, so their near "
        "equality is a symmetry of the construction, not a discovery.  R_S_nat(w=0) "
        "is a null ANCHOR, not a verdict.",
    "RN-R2-7":
        "K2f ordering: prediction.json is hashed and stamped before any fresh-arm "
        "world exists; the arms re-read the stamp from disk and re-hash to a match; "
        "the pilot runs AFTER the stamp.  Probe and battery worlds necessarily "
        "precede the stamp -- they are the band's inputs -- and are counted "
        "separately.",
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
    """RN-R2-3: the dose is NOT in the key."""
    key = f"{LEG}|{salt}|{kind}|i{i}|seed{MASTER_SEED}"
    return int(v8().stable_bucket(key, salt=salt, modulus=2 ** 63 - 1))


def pair_seeds(i: int, suffix: str = "") -> dict[str, int]:
    return {"author": seed_for("author", i, SALT_AUTHOR + suffix),
            "frameA": seed_for("frameA", i, SALT_FRAME_A + suffix),
            "frameB": seed_for("frameB", i, SALT_FRAME_B + suffix)}


def _predicate(v: np.ndarray) -> dict[str, Any]:
    fin = bool(np.all(np.isfinite(v)))
    sat = bool(np.any(np.abs(v) >= SATURATION_ABS))
    nz = bool(float(np.std(v, ddof=1)) > 0.0)
    return {"all_finite": fin, "any_saturated": sat, "nonzero_variance": nz,
            "min": float(v.min()), "max": float(v.max()),
            "PASS": bool(fin and (not sat) and nz)}


def df_inflation(df: int) -> float:
    return float(math.sqrt(df / stats.chi2.ppf(0.10, df)))


# ---------------------------------------------------------------------------
# THE CURVE (M3, persisted; consumed, never refitted for the prediction).


def curve() -> dict[str, Any]:
    d = read_json(M3DEC)
    q = d["curves"]["A-quad"]
    pts = [(float(a["V"]), float(a["alpha"]), float(a["se"])) for a in d["alpha"]]
    return {"theta": [float(x) for x in q["theta"]], "expr": q["expr"],
            "param_names": list(q["param_names"]), "points": pts,
            "bootstrap_ci95": q["bootstrap"]["ci95"],
            "winner": d["L-1m3"]["winner"], "slug": d["verdict_slug"],
            "consumption": d["curve_consumption"]}


def alpha_of(V: float | np.ndarray, theta: list[float]) -> Any:
    c, k0, k2 = theta
    return c - k0 * np.asarray(V, dtype=float) + (k2 / 2.0) * np.asarray(V, float) ** 2


def curve_cov(pts: list[tuple[float, float, float]]) -> dict[str, Any]:
    """OLS refit of A-quad on M3's persisted (V, alpha) points, for SE_pred only.

    The prediction itself uses M3's PERSISTED theta; this refit exists to obtain a
    parameter covariance that M3 did not persist.  Agreement with theta is
    reported, not assumed.
    """
    V = np.array([p[0] for p in pts], dtype=float)
    y = np.array([p[1] for p in pts], dtype=float)
    X = np.column_stack([np.ones_like(V), -V, V ** 2 / 2.0])
    xtx_inv = np.linalg.inv(X.T @ X)
    beta = xtx_inv @ (X.T @ y)
    resid = y - X @ beta
    dof = len(V) - 3
    sigma2 = float(resid @ resid) / dof
    return {"beta": [float(b) for b in beta], "cov": (sigma2 * xtx_inv).tolist(),
            "sigma": float(math.sqrt(sigma2)), "dof": int(dof),
            "n_points": int(len(V))}


# ---------------------------------------------------------------------------
# THE SCORING.  ONE gauge pass on A; three truth panels through the pipeline's
# own construction (PIN_TRUTH_PANEL / PIN_TRUTH_ACTIVE).


def _truth_world(world: dict[str, Any], person: np.ndarray) -> dict[str, Any]:
    """The pipeline's own truth construction, fed a chosen person channel."""
    tw = dict(world)
    tw["trait"] = person
    return tw


def score_pair(wa: dict[str, Any], wb: dict[str, Any], w: dict[str, float],
               corpus: str) -> dict[str, Any]:
    m_ = k2b()
    lay = m_.layout()
    module = lay["module"]
    vectors = m_.emit_panel(wa, w)
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
    out: dict[str, Any] = {}
    panels: dict[str, list[np.ndarray]] = {}
    for name, world, person in (("T_nat", wa, wa["trait_pure"]),
                                ("S_nat", wa, wa["style"]),
                                ("S_ref", wb, wb["style"])):
        full = m_.emit_panel(_truth_world(world, person), w, active=("mu", "common"))
        tv = [full[i] for i in ridx]
        panels[name] = tv
        fld = m_.field_from_vectors(tv, calibration, corpus)
        out["R_" + name] = float(module.field_agreement(field_est, fld,
                                                        lay["weights"]))
    out["truth_norm_delta_S"] = float(np.sqrt(sum(
        float(((a - b) ** 2).sum())
        for a, b in zip(panels["S_nat"], panels["S_ref"]))))
    out["truth_norm_delta_TS"] = float(np.sqrt(sum(
        float(((a - b) ** 2).sum())
        for a, b in zip(panels["T_nat"], panels["S_nat"]))))
    return out


def run_pair(wv: float, i: int, suffix: str = "") -> dict[str, Any]:
    m_ = k2b()
    w = m_.arm_weights(SHARE, W_INT_ARM)
    sd = pair_seeds(i, suffix)
    wa = r1().build_split_world_v2(sd["author"], sd["frameA"], PHI, wv)
    wb = r1().build_split_world_v2(sd["author"], sd["frameB"], PHI, wv)
    sc = score_pair(wa, wb, w, f"m4k2b-R2-p{i}{suffix}")      # RN-R2-2
    return {"w_style": wv, "pair": i, "author_seed": sd["author"],
            "frameA_seed": sd["frameA"], "frameB_seed": sd["frameB"], **sc}


# ---------------------------------------------------------------------------
# THE SHARE ACCOUNTING (three readings; RN-R2-1).


def split_shares(world: dict[str, Any], w: dict[str, float]) -> dict[str, float]:
    """k2e:217-231's route, with the mu channel SPLIT into its trait and style
    parts by the same emit_panel call fed each part in turn."""
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
    out["_total_raw"] = total
    return out


def v_readings(sh: dict[str, float]) -> dict[str, float]:
    base = sh["slow"] + sh["int"]
    return {"A_literal_slow_int": base,
            "C_routing_slow_int_style": base + sh["mu_style"],
            "B_slow_int_mu": base + sh["mu_style"] + sh["mu_trait"]}


# ---------------------------------------------------------------------------
# PART 0.


def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")
    m_ = k2b()
    w = m_.arm_weights(SHARE, W_INT_ARM)
    cur = curve()

    # ---- G0r2: certified values, hashes, curve at source, machinery pinned.
    r1dec = read_json(ROOT / "results/m4_r1_identity_channel/decision.json")
    r1bdec = read_json(ROOT / "results/m4_r1b_reband/decision.json")
    hashes = {rel(p): sha_file(p) for p in (R1SRC, R1BSRC, P3BSRC, K2BSRC, K2ESRC)}
    v_design = float(k2e().person_share_design(SHARE, 0.0))
    design_shares = {k: float(v) for k, v in m_.arm_shares(SHARE, W_INT_ARM).items()}
    fit_pts = cur["points"]
    v_lo, v_hi = min(p[0] for p in fit_pts), max(p[0] for p in fit_pts)
    persisted_alpha_at_design = [p[1] for p in fit_pts
                                 if abs(p[0] - v_design) < 1e-12]
    cov = curve_cov(fit_pts)
    theta_agrees = bool(np.allclose(cov["beta"], cur["theta"], rtol=1e-6, atol=1e-9))
    g0 = {
        "r1_slug": r1dec["verdict_slug"], "r1b_slug": r1bdec["verdict_slug"],
        "r1_certificates": {k: bool(v) for k, v in
                            (r1dec.get("certificates") or {}).items()},
        "instrument_hashes": hashes,
        "curve_source": PIN_CURVE, "curve_expr": cur["expr"],
        "curve_theta": cur["theta"], "curve_winner": cur["winner"],
        "curve_consumption": cur["consumption"],
        "curve_fitted_domain": [v_lo, v_hi],
        "ols_refit_beta": cov["beta"], "ols_refit_agrees_with_theta": theta_agrees,
        "ols_refit_sigma": cov["sigma"], "ols_refit_dof": cov["dof"],
        "V_design": v_design, "design_shares": design_shares,
        "persisted_alpha_at_V_design": persisted_alpha_at_design,
        "alpha_at_V_design_from_theta": float(alpha_of(v_design, cur["theta"])),
        "pins": {"truth_panel": PIN_TRUTH_PANEL, "truth_active": PIN_TRUTH_ACTIVE,
                 "trait_site": PIN_TRAIT_SITE, "share_design": PIN_SHARE_DESIGN,
                 "share_realized": PIN_SHARE_REALIZED, "builder": PIN_BUILDER},
    }
    g0["PASS"] = bool(
        g0["r1_slug"] == "INSTRUMENT_DEFECT(C-R1c)"
        and g0["r1b_slug"] == "IDENTITY_CHANNEL_CERTIFIED"
        and cur["winner"] == "A-quad"
        and cur["consumption"] == "CONSUMABLE"
        and len(persisted_alpha_at_design) == 1
        and theta_agrees
        and abs(v_design - SHARE * 0.30) < 1e-12)
    if not g0["PASS"]:
        write_json(OUT / "part0.json", {"G0r2": g0})
        raise SystemExit("G0r2 FAILED -> STOP")

    # ---- G1r2: C2-style battery on 4 fresh probes.
    bat: list[dict[str, Any]] = []
    for i in range(N_BATTERY):
        sd = pair_seeds(i, "-battery")
        row: dict[str, Any] = {"probe": i}
        w0a = r1().build_split_world_v2(sd["author"], sd["frameA"], PHI, 0.0)
        w1a = r1().build_split_world_v2(sd["author"], sd["frameA"], PHI, 1.0)
        w1b = r1().build_split_world_v2(sd["author"], sd["frameB"], PHI, 1.0)
        row["backward_identity_w0"] = bool(
            np.array_equal(w0a["trait"], w0a["trait_pure"]))
        row["style_is_author_stream"] = bool(
            np.array_equal(w1a["style"], w1b["style"]))
        row["trait_pure_shared_across_frames"] = bool(
            np.array_equal(w1a["trait_pure"], w1b["trait_pure"]))
        row["frames_differ"] = bool(not np.array_equal(w1a["common"], w1b["common"]))
        row["trait_eff_carries_style"] = bool(np.allclose(
            w1a["trait"], w1a["trait_pure"] + w1a["style"], rtol=0, atol=0))
        tp = m_.emit_panel(_truth_world(w1a, w1a["trait_pure"]), w,
                           active=("mu", "common"))
        sp = m_.emit_panel(_truth_world(w1a, w1a["style"]), w, active=("mu", "common"))
        row["truth_panels_differ_norm"] = float(np.sqrt(sum(
            float(((a - b) ** 2).sum()) for a, b in zip(tp, sp))))
        row["truth_panels_differ"] = bool(row["truth_panels_differ_norm"] > 0.0)
        bat.append(row)
    g1 = {"probes": bat, "n": N_BATTERY,
          "PASS": bool(all(r["backward_identity_w0"] and r["style_is_author_stream"]
                           and r["trait_pure_shared_across_frames"]
                           and r["frames_differ"] and r["trait_eff_carries_style"]
                           and r["truth_panels_differ"] for r in bat))}
    if not g1["PASS"]:
        write_json(OUT / "part0.json", {"G0r2": g0, "G1r2": g1})
        raise SystemExit("G1r2 FAILED -> INSTRUMENT_DEFECT")

    # ---- the V_eff derivation and the band, on PROBE worlds only.
    probe: list[dict[str, Any]] = []
    for i in range(N_PROBE):
        sd = pair_seeds(i, "-probe")
        row: dict[str, Any] = {"probe": i}
        for wv in W_DOSES:
            wa = r1().build_split_world_v2(sd["author"], sd["frameA"], PHI, wv)
            wb = r1().build_split_world_v2(sd["author"], sd["frameB"], PHI, wv)
            sh = split_shares(wa, w)
            vr = v_readings(sh)
            sc = score_pair(wa, wb, w, f"m4k2b-R2-probe{i}")
            tag = f"w{wv}"
            row[f"{tag}_R_T_nat"] = sc["R_T_nat"]
            row[f"{tag}_R_S_nat"] = sc["R_S_nat"]
            row[f"{tag}_R_S_ref"] = sc["R_S_ref"]
            for k, v in vr.items():
                row[f"{tag}_V_{k}"] = float(v)
            row[f"{tag}_share_mu_trait"] = sh["mu_trait"]
            row[f"{tag}_share_mu_style"] = sh["mu_style"]
            # mu-channel non-additivity: whole-mu share vs the split parts.
            whole = k2e().realized_person_shares(wa, w)["mu"]
            row[f"{tag}_mu_nonadditivity"] = float(
                abs(whole - (sh["mu_trait"] + sh["mu_style"])))
        row["dR_T_paired"] = row["w1.0_R_T_nat"] - row["w0.0_R_T_nat"]
        probe.append(row)
    pdf = pd.DataFrame(probe)
    pdf.to_csv(OUT / "probe.csv", index=False)

    theta = cur["theta"]
    v_eff = float(pdf["w1.0_V_C_routing_slow_int_style"].mean())
    readings = {}
    for key, col in (("A_literal_slow_int", "A_literal_slow_int"),
                     ("C_routing_slow_int_style", "C_routing_slow_int_style"),
                     ("B_slow_int_mu", "B_slow_int_mu")):
        ve = float(pdf[f"w1.0_V_{col}"].mean())
        v0 = float(pdf[f"w0.0_V_{col}"].mean())
        readings[key] = {
            "V_eff_w1": ve, "V_at_w0": v0,
            "reduces_to_V_design_at_w0": bool(abs(v0 - v_design) < 5e-3),
            "inside_fitted_domain": bool(v_lo <= ve <= v_hi),
            "alpha_V_eff": float(alpha_of(ve, theta)),
            "prediction": float(alpha_of(ve, theta) - alpha_of(v_design, theta)),
        }
    prediction = readings["C_routing_slow_int_style"]["prediction"]

    # SE_pred: M3 parameter uncertainty propagated to the DIFFERENCE (c cancels).
    grad = np.array([0.0, -(v_eff - v_design), (v_eff ** 2 - v_design ** 2) / 2.0])
    se_pred = float(math.sqrt(float(grad @ np.array(cov["cov"]) @ grad)))

    # SE_meas: paired dR_T spread on probes, scaled to the arm's n, df-inflated.
    dprobe = pdf["dR_T_paired"].to_numpy(float)
    dfree = len(dprobe) - 1
    infl = df_inflation(dfree)
    sd_d = float(np.std(dprobe, ddof=1))
    se_meas = float(sd_d * infl / math.sqrt(N_PAIRS))

    # SE_approx (RN-R2-5): r-channel shift, V_eff spread, mu non-additivity.
    alpha_design = float(alpha_of(v_design, theta))
    r_probe_w0 = float(pdf["w0.0_R_T_nat"].mean())
    gain = r_probe_w0 / alpha_design
    a_shift = float(abs(prediction) * abs(1.0 - gain))
    per_probe_pred = np.array([
        float(alpha_of(v, theta) - alpha_of(v_design, theta))
        for v in pdf["w1.0_V_C_routing_slow_int_style"].to_numpy(float)])
    a_veff = float(np.std(per_probe_pred, ddof=1) * infl / math.sqrt(N_PAIRS))
    na = float(pdf["w1.0_mu_nonadditivity"].mean())
    slope = float(-theta[1] + theta[2] * v_eff)
    a_nonadd = float(abs(slope) * na)
    se_approx = float(math.sqrt(a_shift ** 2 + a_veff ** 2 + a_nonadd ** 2))

    combined = float(math.sqrt(se_pred ** 2 + se_meas ** 2 + se_approx ** 2))
    half = float(2.0 * combined)
    band = [float(prediction - half), float(prediction + half)]

    # V-R2c's epsilon: pilot-free, variances only (#57) -- from PROBE spread.
    eps_c = float(2.0 * np.std(pdf["w1.0_R_S_ref"].to_numpy(float), ddof=1)
                  * infl / math.sqrt(N_PAIRS))

    pred_obj = {
        "leg": LEG, "quantity": "dR_T = R_T_nat(w=1) - R_T_nat(w=0)",
        "routing_reading": "C_routing_slow_int_style",
        "routing_reading_note": RN_NOTES["RN-R2-1"],
        "V_design": v_design, "V_eff": v_eff,
        "curve_theta": theta, "curve_expr": cur["expr"],
        "alpha_V_design": alpha_design,
        "alpha_V_eff": float(alpha_of(v_eff, theta)),
        "prediction": prediction,
        "all_readings": readings,
        "band": {"SE_pred": se_pred, "SE_meas": se_meas, "SE_approx": se_approx,
                 "SE_approx_parts": {"r_channel_shift": a_shift,
                                     "V_eff_spread": a_veff,
                                     "mu_nonadditivity": a_nonadd},
                 "gain_g": gain, "R_T_probe_w0": r_probe_w0,
                 "combined_SE": combined, "half_width": half, "band": band},
        "eps_V_R2c": eps_c,
        "n_probe_pairs": N_PROBE, "df_inflation": infl, "dof": dfree,
        "planner_sanity_approx": -0.06,
        "planner_sanity_is_non_gating": True,
    }
    write_json(OUT / "prediction.json", pred_obj)
    raw = (OUT / "prediction.json").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    n_fresh = len(list((OUT / "arms").glob("*.csv"))) if (OUT / "arms").exists() else 0
    stamp = {"sha256": digest, "stamp_utc": datetime.now(UTC).isoformat(),
             "fresh_arm_files_before_stamp": int(n_fresh),
             "fresh_arm_worlds_before_stamp": 0,
             "probe_worlds_before_stamp": int(2 * N_PROBE * len(W_DOSES)),
             "battery_worlds_before_stamp": int(3 * N_BATTERY)}
    write_json(OUT / "prediction.sha256.json", stamp)

    write_json(OUT / "part0.json", {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "G0r2": g0, "G1r2": g1, "prediction": pred_obj, "stamp": stamp,
        "RN_NOTES": RN_NOTES,
        "design": {"share": SHARE, "phi": PHI, "w_doses": list(W_DOSES),
                   "n_pairs": N_PAIRS, "master_seed": MASTER_SEED,
                   "salts": [SALT_AUTHOR, SALT_FRAME_A, SALT_FRAME_B, SALT_PILOT]},
        "environment": {"python_executable": sys.executable,
                        "python_version": sys.version.split()[0],
                        "platform": platform.platform(),
                        "numpy": np.__version__, "pandas": pd.__version__},
        "seconds": time.time() - t0,
    })
    _log("part0_done", sha=digest)
    print(f"part0 OK  V_design={v_design!r}  V_eff(C)={v_eff!r}  "
          f"prediction={prediction!r}  half={half!r}\n"
          f"  readings: " + "  ".join(
              f"{k.split('_')[0]}={v['prediction']:+.6f}" for k, v in readings.items())
          + f"\n  SE_pred {se_pred:.3e} / SE_meas {se_meas:.3e} / "
            f"SE_approx {se_approx:.3e} (shift {a_shift:.3e}, veff {a_veff:.3e}, "
            f"nonadd {a_nonadd:.3e})\n"
          f"  gain g={gain!r}  eps_c={eps_c!r}  STAMPED {digest[:16]}  "
          f"{time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# PILOT (after the stamp).


def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("pilot_start")
    p0 = read_json(OUT / "part0.json")
    rows = []
    for i in range(N_PILOT):
        for wv in W_DOSES:
            rows.append(run_pair(wv, i, "-pilot"))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "pilot_field.csv", index=False)
    preds = {}
    for wv in W_DOSES:
        sub = df[df["w_style"] == wv]
        for col in ("R_T_nat", "R_S_nat", "R_S_ref"):
            preds[f"w{wv}_{col}"] = _predicate(sub[col].to_numpy(float))
    piv = df.pivot(index="pair", columns="w_style", values="R_T_nat")
    d_pilot = (piv[1.0] - piv[0.0]).to_numpy(float)
    out = {"n": N_PILOT, "predicates": preds,
           "PASS": bool(all(p["PASS"] for p in preds.values())),
           "dR_T_pilot_mean": float(d_pilot.mean()),
           "R_S_ref_w1_pilot_mean": float(
               df[df["w_style"] == 1.0]["R_S_ref"].mean()),
           "R_S_nat_w1_pilot_mean": float(
               df[df["w_style"] == 1.0]["R_S_nat"].mean()),
           "R_T_nat_w1_pilot_mean": float(
               df[df["w_style"] == 1.0]["R_T_nat"].mean()),
           "permit": _permit_check(),
           "seconds": time.time() - t0}
    write_json(OUT / "pilot.json", out)
    _log("pilot_done")
    if not out["PASS"]:
        raise SystemExit("G2r2 FAILED -> INSTRUMENT_DEFECT")
    print(f"pilot OK  dR_T={out['dR_T_pilot_mean']!r}  "
          f"R_S_ref(w1)={out['R_S_ref_w1_pilot_mean']!r}  "
          f"permit {out['permit']['seconds_stamp_to_permit']:.3f}s after the stamp  "
          f"{time.time() - t0:.1f}s")


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


# ---------------------------------------------------------------------------
# PROJECTION.


def stage_project(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("project_start")
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    pred = p0["prediction"]
    half = pred["band"]["half_width"]
    pdf = read_csv_rt(OUT / "probe.csv")
    dfree = N_PROBE - 1
    infl = df_inflation(dfree)
    sd_d = float(np.std(pdf["dR_T_paired"].to_numpy(float), ddof=1)) * infl
    sd_c = float(np.std(pdf["w1.0_R_S_ref"].to_numpy(float), ddof=1)) * infl
    eps_c = pred["eps_V_R2c"]
    r_s_ref_alt = float(pdf["w1.0_R_S_nat"].mean())

    def project(n: int) -> dict[str, Any]:
        rng = np.random.default_rng(MASTER_SEED)
        se_d = sd_d / math.sqrt(n)
        se_c = sd_c / math.sqrt(n)
        res: dict[str, Any] = {"n_pairs": n, "per_truth": {}}
        for label, truth, role, bar in (
                ("curve truth", pred["prediction"], "power", POWER_MIN),
                ("no interference (dR_T = 0)", 0.0, "false-fire", FALSE_FIRE_MAX)):
            draws = rng.normal(truth, se_d, size=B_PROJ)
            p_in = float(np.mean(np.abs(draws - pred["prediction"]) <= half))
            res["per_truth"][label] = {"truth": truth, "role": role, "bar": bar,
                                       "P_contained": p_in,
                                       "PASS": bool(p_in >= bar) if role == "power"
                                       else bool(p_in <= bar)}
        for label, truth, role, bar in (
                ("R_S_ref = 0", 0.0, "false-fire", FALSE_FIRE_MAX),
                ("R_S_ref = R_S_nat(w=1)", r_s_ref_alt, "power", POWER_MIN)):
            draws = rng.normal(truth, se_c, size=B_PROJ)
            p_pos = float(np.mean(np.abs(draws) > eps_c))
            res["per_truth"]["V-R2c: " + label] = {
                "truth": truth, "role": role, "bar": bar, "P_positive": p_pos,
                "PASS": bool(p_pos <= bar) if role == "false-fire"
                else bool(p_pos >= bar)}
        res["PASS"] = bool(all(v["PASS"] for v in res["per_truth"].values()))
        return res

    base = project(N_PAIRS)
    out = {"base": base, "escalation_fired": False, "escalated": None,
           "sd_dR_T_df_inflated": sd_d, "sd_R_S_ref_df_inflated": sd_c,
           "eps_V_R2c": eps_c, "power_alt_R_S_ref": r_s_ref_alt,
           "df_inflation": infl, "PASS": base["PASS"], "n_final": N_PAIRS}
    if not base["PASS"]:
        esc = project(N_ESCALATED)
        out.update({"escalation_fired": True, "escalated": esc,
                    "PASS": esc["PASS"],
                    "n_final": N_ESCALATED if esc["PASS"] else N_PAIRS})
    write_json(OUT / "projection.json", out)
    _log("project_done")
    if not out["PASS"]:
        raise SystemExit("G3r2 FAILED -> NON_PROJECTABLE")
    print("project OK  " + "  ".join(
        f"{k}: {v.get('P_contained', v.get('P_positive'))!r}"
        for k, v in out["base"]["per_truth"].items())
        + f"  n={out['n_final']}  escalated={out['escalation_fired']}  "
          f"{time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# ARMS.


def stage_arm(args: argparse.Namespace) -> None:
    t0 = time.time()
    (OUT / "arms").mkdir(parents=True, exist_ok=True)
    permit = _permit_check()
    write_json(OUT / "arm_permit.json", permit)
    n_final = int(read_json(OUT / "projection.json")["n_final"])
    chunk = int(args.chunk)
    per = math.ceil(n_final / CHUNKS)
    lo, hi = chunk * per, min((chunk + 1) * per, n_final)
    _log("arm_start", chunk=chunk, lo=lo, hi=hi)
    rows = []
    for i in range(lo, hi):
        for wv in W_DOSES:
            rows.append(run_pair(wv, i))
    pd.DataFrame(rows).to_csv(OUT / "arms" / f"chunk_{chunk}.csv", index=False)
    _log("arm_done", chunk=chunk, n=len(rows))
    print(f"arm chunk {chunk} OK  pairs {lo}..{hi - 1}  rows={len(rows)}  "
          f"{time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# FIT.


def stage_fit(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("fit_start")
    p0 = read_json(OUT / "part0.json")
    pred = p0["prediction"]
    frames = [read_csv_rt(p) for p in sorted((OUT / "arms").glob("chunk_*.csv"))]
    df = pd.concat(frames, ignore_index=True).sort_values(["pair", "w_style"])
    df.to_csv(OUT / "arm.csv", index=False)
    n_final = int(read_json(OUT / "projection.json")["n_final"])
    if len(df) != 2 * n_final:
        raise SystemExit(f"arm row count {len(df)} != {2 * n_final}")

    piv = df.pivot(index="pair", columns="w_style", values="R_T_nat")
    d_paired = (piv[1.0] - piv[0.0]).to_numpy(float)
    rng = np.random.default_rng(MASTER_SEED)
    n = len(d_paired)

    def boot(vec: np.ndarray) -> dict[str, Any]:
        idx = rng.integers(0, len(vec), size=(B_BOOT, len(vec)))
        bs = vec[idx].mean(axis=1)
        return {"mean": float(vec.mean()),
                "sem": float(np.std(vec, ddof=1) / math.sqrt(len(vec))),
                "ci95": [float(np.percentile(bs, CI_Q[0])),
                         float(np.percentile(bs, CI_Q[1]))],
                "sd": float(np.std(vec, ddof=1)), "n": int(len(vec))}

    d_stat = boot(d_paired)
    half = pred["band"]["half_width"]
    prediction = pred["prediction"]
    err = d_stat["mean"] - prediction
    inside = bool(abs(err) <= half)
    # NULL-first (#55): is dR_T itself distinguishable from zero?
    d_null_eps = float(2.0 * d_stat["sem"])
    v_r2a = {
        "measured": d_stat["mean"], "ci95": d_stat["ci95"], "sem": d_stat["sem"],
        "sd": d_stat["sd"], "n": d_stat["n"],
        "prediction": prediction, "half_width": half,
        "band": pred["band"]["band"], "signed_error": float(err),
        "position_in_band": float(err / half), "INSIDE": inside,
        "is_null_vs_zero": bool(abs(d_stat["mean"]) <= d_null_eps),
        "null_eps_2sem": d_null_eps,
        "ci_excludes_zero": bool(d_stat["ci95"][0] > 0 or d_stat["ci95"][1] < 0),
        "sign": "negative" if d_stat["mean"] < 0 else "positive",
        "classification": ("INSIDE" if inside else
                           ("NULL" if abs(d_stat["mean"]) <= d_null_eps
                            else "OUTSIDE")),
    }

    # V-R2c: R_S_ref(w=1) vs 0, NULL-first.
    w1 = df[df["w_style"] == 1.0]
    w0 = df[df["w_style"] == 0.0]
    c_stat = boot(w1["R_S_ref"].to_numpy(float))
    eps_c = pred["eps_V_R2c"]
    c_null = bool(abs(c_stat["mean"]) <= eps_c
                  and c_stat["ci95"][0] >= -eps_c and c_stat["ci95"][1] <= eps_c)
    v_r2c = {**c_stat, "eps": eps_c, "NULL": c_null,
             "POSITIVE": bool(not c_null and c_stat["ci95"][0] > eps_c),
             "classification": "NULL" if c_null else (
                 "POSITIVE" if c_stat["ci95"][0] > eps_c else "INDETERMINATE")}

    per_arm = {}
    for wv in W_DOSES:
        sub = df[df["w_style"] == wv]
        per_arm[f"w{wv}"] = {col: boot(sub[col].to_numpy(float))
                             for col in ("R_T_nat", "R_S_nat", "R_S_ref")}

    # Descriptive (#59, RN-R2-6): exchangeability at w = 1; null anchor at w = 0.
    ex_vec = (w1["R_S_nat"].to_numpy(float) - w1["R_T_nat"].to_numpy(float))
    exch = {**boot(ex_vec),
            "R_S_nat": per_arm["w1.0"]["R_S_nat"]["mean"],
            "R_T_nat": per_arm["w1.0"]["R_T_nat"]["mean"],
            "ratio": float(per_arm["w1.0"]["R_S_nat"]["mean"]
                           / per_arm["w1.0"]["R_T_nat"]["mean"]),
            "label": "DESCRIPTIVE ONLY -- exchangeability, gates nothing (#59)"}
    anchor = {**boot(w0["R_S_nat"].to_numpy(float)),
              "R_S_ref_w0": per_arm["w0.0"]["R_S_ref"]["mean"],
              "label": "null ANCHOR, not a verdict"}

    # All three readings re-scored against the measurement (reporting; RN-R2-1).
    alt = {}
    for key, r in pred["all_readings"].items():
        alt[key] = {"prediction": r["prediction"],
                    "signed_error": float(d_stat["mean"] - r["prediction"]),
                    "position": float((d_stat["mean"] - r["prediction"]) / half),
                    "would_be_inside": bool(
                        abs(d_stat["mean"] - r["prediction"]) <= half)}

    # --- rule 13, Q2's implementation unchanged (q2:670-681) ----------------
    # Fires when a decision boundary sits inside the bootstrap's own Monte-Carlo
    # noise.  Applied AFTER every base statistic, with its own rng, so no base
    # number moves; the high-B interval then CONTROLS the classification.
    margin = 1.0 / (RULE13_FACTOR * B_BOOT)
    rule13: list[dict[str, Any]] = []
    for name, vec, bounds in (
            ("V-R2c", w1["R_S_ref"].to_numpy(float), (0.0, eps_c, -eps_c)),
            ("V-R2a", d_paired,
             (prediction - half, prediction + half, 0.0))):
        rng_b = np.random.default_rng(MASTER_SEED + 1)
        idx = rng_b.integers(0, len(vec), size=(B_BOOT, len(vec)))
        bs = vec[idx].mean(axis=1)
        near = []
        for bnd in bounds:
            frac = float(np.mean(bs <= bnd))
            if min(abs(frac - 0.025), abs(frac - 0.975)) < margin:
                near.append({"boundary": float(bnd), "tail_frac": frac})
        if near:
            rng_h = np.random.default_rng(MASTER_SEED + 2)
            ih = rng_h.integers(0, len(vec), size=(B_BOOT_HIGH, len(vec)))
            bh = vec[ih].mean(axis=1)
            ci_h = [float(np.percentile(bh, CI_Q[0])),
                    float(np.percentile(bh, CI_Q[1]))]
            rule13.append({"verdict": name, "triggers": near, "B": B_BOOT_HIGH,
                           "ci_before": (v_r2c["ci95"] if name == "V-R2c"
                                         else v_r2a["ci95"]),
                           "ci_after": ci_h})
            if name == "V-R2c":
                v_r2c["ci95"] = ci_h
                v_r2c["B"] = B_BOOT_HIGH
                nn = bool(abs(v_r2c["mean"]) <= eps_c
                          and ci_h[0] >= -eps_c and ci_h[1] <= eps_c)
                v_r2c["NULL"] = nn
                v_r2c["POSITIVE"] = bool(not nn and ci_h[0] > eps_c)
                v_r2c["classification"] = "NULL" if nn else (
                    "POSITIVE" if ci_h[0] > eps_c else "INDETERMINATE")
            else:
                v_r2a["ci95"] = ci_h
                v_r2a["B"] = B_BOOT_HIGH

    # --- quantile-edge stability DIAGNOSTIC (routes nothing) ----------------
    # Q2's rule-13 trigger asks whether a boundary's TAIL FRACTION is within
    # Monte-Carlo noise.  It is silent when the instability lives in the
    # PERCENTILE VALUE instead, which is this leg's case.  The diagnostic below
    # reports it rather than acting on it: the routing classification stays the
    # registered B = 2000 one, and the routing CELL is unchanged either way.
    def _mc_se_quantile(vec: np.ndarray, q: float, B: int) -> float:
        sem = float(np.std(vec, ddof=1) / math.sqrt(len(vec)))
        dens = float(stats.norm.pdf(stats.norm.ppf(q)) / sem)
        return float(math.sqrt(q * (1.0 - q) / B) / dens)

    vec_c = w1["R_S_ref"].to_numpy(float)
    rng_h = np.random.default_rng(MASTER_SEED + 2)
    ih = rng_h.integers(0, len(vec_c), size=(B_BOOT_HIGH, len(vec_c)))
    bh = vec_c[ih].mean(axis=1)
    ci_high = [float(np.percentile(bh, CI_Q[0])),
               float(np.percentile(bh, CI_Q[1]))]
    null_high = bool(abs(v_r2c["mean"]) <= eps_c
                     and ci_high[0] >= -eps_c and ci_high[1] <= eps_c)
    gap_lo = float(v_r2c["ci95"][0] + eps_c)
    mc_se = _mc_se_quantile(vec_c, 0.025, B_BOOT)
    v_r2c["stability_diagnostic"] = {
        "B_registered": B_BOOT, "classification_at_B_registered":
            v_r2c["classification"],
        "B_high": B_BOOT_HIGH, "ci95_at_B_high": ci_high,
        "classification_at_B_high": "NULL" if null_high else (
            "POSITIVE" if ci_high[0] > eps_c else "INDETERMINATE"),
        "lower_edge_minus_neg_eps": gap_lo,
        "mc_se_of_2.5pct_quantile_at_B_registered": mc_se,
        "gap_in_mc_se": float(gap_lo / mc_se) if mc_se else None,
        "classification_is_bootstrap_noise_limited": bool(abs(gap_lo) < mc_se),
        "q2_rule13_tail_trigger_fired": bool(
            any(e["verdict"] == "V-R2c" for e in rule13)),
        "note": "DIAGNOSTIC ONLY -- routes nothing; the routing classification is "
                "the registered B=2000 one and the routing CELL is identical under "
                "both, because cell 6 fires on V-R2a alone",
    }

    # --- the frame-controlled cross-frame increment (diagnostic, RN-R2-8) ---
    # The truth panels are the pipeline's own, active=("mu","common"), so they
    # CARRY THE FRAME.  R_S_ref(w=1) vs 0 therefore conflates "cannot read style
    # across frames" with "the frame itself does not transport".  The paired
    # increment over the w = 0 arm removes the frame term, because at w = 0 the
    # gauge is shown no style at all while the frame path is identical.
    pv_ref = df.pivot(index="pair", columns="w_style", values="R_S_ref")
    d_cross = (pv_ref[1.0] - pv_ref[0.0]).to_numpy(float)
    pv_nat = df.pivot(index="pair", columns="w_style", values="R_S_nat")
    d_within = (pv_nat[1.0] - pv_nat[0.0]).to_numpy(float)
    cross = {**boot(d_cross), "label": "DIAGNOSTIC -- frame-controlled cross-frame "
             "style increment, R_S_ref(w=1) - R_S_ref(w=0), paired; routes nothing",
             "within_frame_increment": boot(d_within),
             "excludes_zero": bool(False)}
    cross["excludes_zero"] = bool(cross["ci95"][0] > 0 or cross["ci95"][1] < 0)
    cross["ratio_cross_to_within"] = float(
        cross["mean"] / cross["within_frame_increment"]["mean"])

    probe_d = float(read_csv_rt(OUT / "probe.csv")["dR_T_paired"].mean())
    out = {"V_R2a": v_r2a, "V_R2c": v_r2c, "per_arm": per_arm,
           "probe_dR_T_mean_disclosed_not_consumed": probe_d,
           "rule13_events": rule13, "B": B_BOOT,
           "cross_frame_increment": cross,
           "exchangeability_descriptive": exch, "null_anchor": anchor,
           "all_readings_rescored": alt,
           "n_pairs": n, "seconds": time.time() - t0}
    write_json(OUT / "fit.json", out)
    _log("fit_done")
    print(f"fit OK  dR_T={v_r2a['measured']!r} {v_r2a['ci95']!r}  "
          f"pred={prediction!r}  pos={v_r2a['position_in_band']:.4f}  "
          f"{v_r2a['classification']}\n"
          f"  V-R2c R_S_ref(w1)={c_stat['mean']!r} {c_stat['ci95']!r} "
          f"eps={eps_c!r} -> {v_r2c['classification']}\n"
          f"  exch R_S/R_T(w1)={exch['ratio']!r}  anchor R_S_nat(w0)="
          f"{anchor['mean']!r}  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# FINALIZE.


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    g3 = read_json(OUT / "projection.json")
    fit = read_json(OUT / "fit.json")
    a, c = fit["V_R2a"], fit["V_R2c"]
    cell, slug, text = None, None, None
    if not (p0["G0r2"]["PASS"] and p0["G1r2"]["PASS"]):
        cell, slug, text = 1, "STOP", "G0/G1 failure"
    elif not g3["PASS"]:
        cell, slug, text = 2, "NON_PROJECTABLE", "projection fails after escalation"
    elif a["classification"] == "INSIDE" and c["classification"] == "NULL":
        cell, slug = 3, "IDENTITY_CROWDS_BIOGRAPHY_AND_STAYS_UNREADABLE"
        text = ("the tax curve transports to the new channel; the gauge pays the "
                "identity tax yet cannot read the identity")
    elif a["classification"] == "INSIDE" and c["classification"] == "POSITIVE":
        cell, slug = 4, "IDENTITY_PARTIALLY_READABLE"
        text = ("the gauge reads planted identity across frames; the P-line's "
                "limitation is trait-specific")
    elif a["classification"] == "NULL" and c["classification"] == "NULL":
        cell, slug = 5, "LAW_DOES_NOT_TRANSPORT"
        text = ("the curve is design-V-specific; the gauge still cannot read "
                "identity")
    elif a["classification"] == "OUTSIDE":
        cell, slug = 6, "INTERFERENCE_MISPRICED"
        text = ("interference is real but the law's price is wrong; the band "
                "decomposition names the gap")
    else:
        cell, slug = 7, "MIXED_OR_UNDERPOWERED"
        text = "every verdict reported; nothing upgraded"
    modifiers = []
    if c["classification"] == "POSITIVE":
        modifiers.append("CROSS_FRAME_IDENTITY_READABLE")
    if a["classification"] == "OUTSIDE" and a["sign"] == "negative":
        modifiers.append("INTERFERENCE_REAL_BUT_SMALLER_THAN_PRICED"
                         if abs(a["measured"]) < abs(a["prediction"])
                         else "INTERFERENCE_LARGER_THAN_PRICED")
    dec = {"leg": LEG, "utc": datetime.now(UTC).isoformat(),
           "routing_cell": cell, "verdict_slug": slug, "routing_text": text,
           "modifiers": modifiers,
           "V_R2a": a["classification"], "V_R2c": c["classification"],
           "permit": read_json(OUT / "arm_permit.json"),
           "n_pairs": fit["n_pairs"],
           "banner": "EXPLORATORY, synthetic, label-free; a PLANTED channel -- "
                     "nothing here bears on the k2b family's own worlds",
           "seconds": time.time() - t0}
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug)
    print(f"finalize OK  slug={slug}  cell={cell}  modifiers={modifiers}")


# ---------------------------------------------------------------------------
# REPORT (rule 24: every table generated from artifacts).


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
    b = pred["band"]
    sec: dict[str, list[str]] = {}
    sec["readings"] = _md(
        ["reading", "V_eff(w=1)", "V at w=0", "reduces to V_design?",
         "inside fitted domain?", "prediction", "routing?"],
        [[k, repr(v["V_eff_w1"]), repr(v["V_at_w0"]),
          str(v["reduces_to_V_design_at_w0"]), str(v["inside_fitted_domain"]),
          repr(v["prediction"]),
          "**YES**" if k == pred["routing_reading"] else "no"]
         for k, v in pred["all_readings"].items()])
    sec["band"] = _md(
        ["term", "value", "note"],
        [["prediction alpha(V_eff) - alpha(V_design)", repr(pred["prediction"]),
          f"V_design {pred['V_design']!r} -> V_eff {pred['V_eff']!r}"],
         ["SE_pred", repr(b["SE_pred"]), "M3 parameter covariance, c cancels"],
         ["SE_meas", repr(b["SE_meas"]),
          f"paired probe spread scaled to n={p0['design']['n_pairs']}"],
         ["SE_approx", repr(b["SE_approx"]), "RN-R2-5, three parts below"],
         ["  r-channel shift", repr(b["SE_approx_parts"]["r_channel_shift"]),
          f"gain g = {b['gain_g']!r} (R_T probe w0 {b['R_T_probe_w0']!r})"],
         ["  V_eff spread", repr(b["SE_approx_parts"]["V_eff_spread"]), "across probes"],
         ["  mu non-additivity", repr(b["SE_approx_parts"]["mu_nonadditivity"]),
          "realized trait/style cross term through the curve"],
         ["combined SE", repr(b["combined_SE"]), "root sum of squares"],
         ["**half-width**", "**" + repr(b["half_width"]) + "**", "2 x combined (#61)"],
         ["band", repr(b["band"]), "two-sided containment"]])
    sec["arms"] = _md(
        ["dose", "quantity", "mean", "SEM", "CI95"],
        [[w, q, repr(v["mean"]), repr(v["sem"]), repr(v["ci95"])]
         for w, qs in fit["per_arm"].items() for q, v in qs.items()])
    a = fit["V_R2a"]
    sec["verdicts"] = _md(
        ["verdict", "measured", "CI95", "reference", "result"],
        [["V-R2a (sealed containment)", repr(a["measured"]), repr(a["ci95"]),
          f"band {a['band']!r}", "**" + a["classification"] + "**"],
         ["V-R2a position in band", repr(a["position_in_band"]), "-",
          "inside iff |pos| <= 1", str(a["INSIDE"])],
         ["V-R2c (R_S_ref at w=1, NULL-first)", repr(fit["V_R2c"]["mean"]),
          repr(fit["V_R2c"]["ci95"]), f"eps {fit['V_R2c']['eps']!r}",
          "**" + fit["V_R2c"]["classification"] + "**"]])
    ex, an = fit["exchangeability_descriptive"], fit["null_anchor"]
    sec["descriptive"] = _md(
        ["reading", "value", "CI95", "label"],
        [["R_S_nat(w=1)", repr(ex["R_S_nat"]), "-", "descriptive"],
         ["R_T_nat(w=1)", repr(ex["R_T_nat"]), "-", "descriptive"],
         ["R_S_nat - R_T_nat (w=1)", repr(ex["mean"]), repr(ex["ci95"]), ex["label"]],
         ["ratio R_S/R_T (w=1)", repr(ex["ratio"]), "-", "exchangeability"],
         ["R_S_nat(w=0)", repr(an["mean"]), repr(an["ci95"]), an["label"]],
         ["R_S_ref(w=0)", repr(an["R_S_ref_w0"]), "-", "null anchor"]])
    xf = fit["cross_frame_increment"]
    sec["crossframe"] = _md(
        ["contrast", "mean", "CI95", "excludes zero?", "reading"],
        [["R_S_ref(w=1) - R_S_ref(w=0)  [cross-frame, frame-controlled]",
          repr(xf["mean"]), repr(xf["ci95"]), str(xf["excludes_zero"]),
          "style bought across frames"],
         ["R_S_nat(w=1) - R_S_nat(w=0)  [within-frame, same control]",
          repr(xf["within_frame_increment"]["mean"]),
          repr(xf["within_frame_increment"]["ci95"]),
          str(bool(xf["within_frame_increment"]["ci95"][0] > 0)),
          "style bought within frame"],
         ["ratio cross / within", repr(xf["ratio_cross_to_within"]), "-", "-",
          "fraction of the readable identity that survives a frame refresh"]])
    sec["rescored"] = _md(
        ["reading", "prediction", "signed error", "position", "would be inside?"],
        [[k, repr(v["prediction"]), repr(v["signed_error"]), repr(v["position"]),
          str(v["would_be_inside"])]
         for k, v in fit["all_readings_rescored"].items()])
    rows = []
    for k, v in g3["base"]["per_truth"].items():
        rows.append([k, v["role"], repr(v["truth"]), repr(v["bar"]),
                     repr(v.get("P_contained", v.get("P_positive"))),
                     str(v["PASS"])])
    sec["projection"] = _md(
        ["truth", "role", "value", "bar", "P", "PASS"], rows)
    sec["gates"] = _md(
        ["gate", "PASS", "detail"],
        [["G0r2", str(p0["G0r2"]["PASS"]),
          f"R1 {p0['G0r2']['r1_slug']}; R1b {p0['G0r2']['r1b_slug']}; curve "
          f"{p0['G0r2']['curve_winner']} {p0['G0r2']['curve_consumption']}; OLS refit "
          f"agrees with persisted theta: {p0['G0r2']['ols_refit_agrees_with_theta']}"],
         ["G1r2", str(p0["G1r2"]["PASS"]),
          f"C2-style battery on {p0['G1r2']['n']} fresh probes; truth panels differ "
          f"(norm {p0['G1r2']['probes'][0]['truth_panels_differ_norm']!r})"],
         ["G2r2", str(pil["PASS"]),
          f"rule-29 predicate on all three scorings, {pil['n']} pilot pairs"],
         ["G3r2", str(g3["PASS"]),
          f"escalation fired: {g3['escalation_fired']}; n_final {g3['n_final']}"]])
    return {k: "\n".join(v) for k, v in sec.items()}


def _facts(p0, pil, g3, fit, dec) -> dict[str, Any]:
    pred = p0["prediction"]
    b = pred["band"]
    a, c = fit["V_R2a"], fit["V_R2c"]
    st = p0["stamp"]
    return {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "MODS": ", ".join(dec["modifiers"]) or "none",
        "VDES": pred["V_design"], "VEFF": pred["V_eff"],
        "PRED": pred["prediction"], "HALF": b["half_width"], "BAND": b["band"],
        "SEP": b["SE_pred"], "SEM": b["SE_meas"], "SEA": b["SE_approx"],
        "SHIFT": b["SE_approx_parts"]["r_channel_shift"],
        "GAIN": b["gain_g"], "RPW0": b["R_T_probe_w0"],
        "ADES": pred["alpha_V_design"], "AEFF": pred["alpha_V_eff"],
        "MEAS": a["measured"], "CI": a["ci95"], "POS": a["position_in_band"],
        "ERR": a["signed_error"], "CLS": a["classification"],
        "SEMM": a["sem"], "NULLEPS": a["null_eps_2sem"],
        "CMEAS": c["mean"], "CCI": c["ci95"], "CEPS": c["eps"],
        "CCLS": c["classification"],
        "EXR": fit["exchangeability_descriptive"]["ratio"],
        "EXS": fit["exchangeability_descriptive"]["R_S_nat"],
        "EXT": fit["exchangeability_descriptive"]["R_T_nat"],
        "ANCH": fit["null_anchor"]["mean"],
        "ANCHREF": fit["null_anchor"]["R_S_ref_w0"],
        "RTW0": fit["per_arm"]["w0.0"]["R_T_nat"]["mean"],
        "RTW1": fit["per_arm"]["w1.0"]["R_T_nat"]["mean"],
        "SHA16": st["sha256"][:16], "SHA": st["sha256"],
        "STAMP": st["stamp_utc"], "PERMIT": dec["permit"]["permit_utc"],
        "PGAP": dec["permit"]["seconds_stamp_to_permit"],
        "NFRESH": st["fresh_arm_worlds_before_stamp"],
        "NPROBE": st["probe_worlds_before_stamp"],
        "NPAIRS": fit["n_pairs"],
        "PA": pred["all_readings"]["A_literal_slow_int"]["prediction"],
        "PB": pred["all_readings"]["B_slow_int_mu"]["prediction"],
        "PC": pred["all_readings"]["C_routing_slow_int_style"]["prediction"],
        "VA": pred["all_readings"]["A_literal_slow_int"]["V_eff_w1"],
        "VB": pred["all_readings"]["B_slow_int_mu"]["V_eff_w1"],
        "ESC": g3["escalation_fired"], "SANITY": pred["planner_sanity_approx"],
        "PYEXE": p0["environment"]["python_executable"],
        "PYVER": p0["environment"]["python_version"],
        "GAPLO": c["stability_diagnostic"]["lower_edge_minus_neg_eps"],
        "GAPSE": c["stability_diagnostic"]["gap_in_mc_se"],
        "MCSE": c["stability_diagnostic"]["mc_se_of_2.5pct_quantile_at_B_registered"],
        "BREG": c["stability_diagnostic"]["B_registered"],
        "BHIGH": c["stability_diagnostic"]["B_high"],
        "CIH": c["stability_diagnostic"]["ci95_at_B_high"],
        "CB2": c["stability_diagnostic"]["classification_at_B_high"],
        "R13F": c["stability_diagnostic"]["q2_rule13_tail_trigger_fired"],
        "NRULE13": len(fit["rule13_events"]),
        "PROBED": fit["probe_dR_T_mean_disclosed_not_consumed"],
        "XINC": fit["cross_frame_increment"]["mean"],
        "XCI": fit["cross_frame_increment"]["ci95"],
        "XEX": fit["cross_frame_increment"]["excludes_zero"],
        "WINC": fit["cross_frame_increment"]["within_frame_increment"]["mean"],
        "WCI": fit["cross_frame_increment"]["within_frame_increment"]["ci95"],
        "XRAT": fit["cross_frame_increment"]["ratio_cross_to_within"],
        "NULLSTR": ("NULL (indistinguishable from zero)" if a["is_null_vs_zero"]
                    else "not null — the effect is distinguishable from zero"),
        "INTERP": _interp(a),
        "RESCUE": _rescue(fit),
        "BOUND": (
            "V-R2a's miss is a failure of the LAW'S TRANSPORT, not of the "
            "instrument — the channel is certified by R1/R1b and the r-channel "
            "shift is inside the band, so the curve is what did not carry."
            if a["classification"] == "OUTSIDE" else
            "V-R2a's result is a statement about the curve's reach, and it rests "
            "on the RN-R2-1 share-accounting pin, which is a judgement call made "
            "before the measurement and reported with both alternatives."),
    }


def _interp(a: dict[str, Any]) -> str:
    """§5.1's verdict sentence, written from the measurement (never pre-written)."""
    if a["classification"] == "INSIDE":
        return ("Interference is real and priced correctly: the N-line tax curve, "
                "fitted on worlds with no style channel at all, predicts the "
                "consequence of planting one to within the band.")
    if a["classification"] == "NULL":
        return ("There is no detectable interference: planting identity did not "
                "measurably change how well the gauge reads biography, so the "
                "curve's price does not transport to this channel.")
    direction = "less" if a["measured"] < 0 else "better"
    if abs(a["measured"]) < abs(a["prediction"]):
        size = (f"but the curve OVERPRICES it by a factor of "
                f"{abs(a['prediction'] / a['measured'])!r}")
    else:
        size = (f"but the curve UNDERPRICES it by a factor of "
                f"{abs(a['measured'] / a['prediction'])!r}")
    return (f"Interference is real and the gauge reads biography {direction} well "
            f"when identity is planted, {size}.")


def _rescue(fit: dict[str, Any]) -> str:
    """Whether any share reading would have contained the measurement."""
    alt = fit["all_readings_rescored"]
    inside = [k for k, v in alt.items() if v["would_be_inside"]]
    if fit["V_R2a"]["classification"] == "INSIDE":
        others = [k for k in alt if k != "C_routing_slow_int_style"]
        also = [k for k in others if alt[k]["would_be_inside"]]
        return ("The routing reading contains the measurement. "
                + (f"So would {', '.join(also)} — the verdict is therefore robust "
                   "to the RN-R2-1 ambiguity."
                   if also else
                   "Neither alternative reading would have — the verdict DEPENDS on "
                   "the RN-R2-1 pin, which is why that pin was made before any "
                   "number existed and all three readings are reported."))
    if inside:
        a = fit["V_R2a"]
        bits = []
        for k in inside:
            v = alt[k]
            same_sign = (v["prediction"] < 0) == (a["measured"] < 0)
            bits.append(
                f"**{k}** (prediction {v['prediction']!r}, position "
                f"{v['position']!r}"
                + (f", inside by only {1.0 - abs(v['position'])!r} of the "
                   f"half-width" if abs(v["position"]) > 0.9 else "")
                + (", and with the WRONG SIGN" if not same_sign else "")
                + ")")
        return (
            "**This is the disclosure that matters most in this leg.** The routing "
            "reading misses, but " + "; ".join(bits) + " would have contained the "
            "measurement. Had that reading been pinned, the leg would have routed "
            "to a different cell entirely. The pin was made in Part 0 before any "
            "hypothesis-relevant number existed, on four stated grounds, and all "
            "three readings were persisted then — which is the only reason this "
            "sentence can be written at all rather than discovered by a reader.\n\n"
            "Two things keep that from rescuing reading A on the merits. Its "
            "prediction has the **opposite sign** to the measurement "
            f"({alt['A_literal_slow_int']['prediction']!r} against a measured "
            f"{a['measured']!r}, whose CI {a['ci95']!r} excludes zero), so it is "
            "not describing the effect that occurred. And it clears the bar by "
            f"grazing it: the half-width {a['half_width']!r} is "
            f"{abs(a['half_width'] / a['measured'])!r} times the whole measured "
            "effect, so at this scale the band is too wide to discriminate a small "
            "negative interference from a small positive one. The honest reading is "
            "that BOTH candidate prices are wrong and the band is too coarse to "
            "adjudicate between them — not that the literal reading was right.")
    return ("No reading of the share accounting rescues the prediction: every "
            "candidate V_eff misses the measurement by more than the band. The gap "
            "is therefore NOT the RN-R2-1 ambiguity — it is the law itself failing "
            "to transport to a channel it was never fitted on.")


TEMPLATE = """# SUICA M4-R2 — the gauge meets the identity channel

**Outcome: `{{SLUG}}`** (rule-16 cell {{CELL}}). Modifiers: {{MODS}}.

Registered before the run in `docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md`
("M4-R2", commit 49b5161). EXPLORATORY, synthetic, label-free. The identity
channel here is **planted**, not discovered: nothing in this leg bears on the
k2b family's own worlds.

## 1. What was asked

R1/R1b certified a planted identity channel. This leg puts the gauge in front
of it and asks whether the program's own laws predict what happens.

1. **Interference (SEALED).** Does identity crowd out biography at the price
   the N-line tax curve names?
2. **Within-frame style reading (DESCRIPTIVE, #59).** At equal weights trait
   and style are exchangeable, so R_S ≈ R_T is a symmetry, not a finding.
3. **Cross-frame style reading (VERDICT, NULL-first).** Style is present in
   both worlds of a pair. Can the gauge read it across frames?

## 2. The registration defect that had to be pinned first

The registration derives V_eff from "the share accounting of
`person_share_design`'s own semantics". That function's **implementation**
({{PYVER}} run, `scripts/run_suica_m4_k2e_double_matching.py:240`) is literally
`shares["slow"] + shares["int"]` — which excludes the `mu` channel where style
lives. Under that literal reading, adding style *raises the denominator* and
**lowers** V_eff, making the sealed prediction **positive** ({{PA}}). That
contradicts the registration's own mechanism sentence in the same paragraph —
style "adds author-persistent variance, **raising** the effective person share"
— and its sanity value ({{SANITY}}).

This was pinned as **RN-R2-1 before any hypothesis-relevant number existed**,
with all three readings computed and reported:

<<TABLE:readings>>

The routing reading is **C**, on four independent grounds: it is the function's
*semantics* (the author-persistent share that is **not** the target trait —
`slow`+`int` were exactly that set before a style channel existed; #56,
inheritance is not exemption); it reduces to V_design exactly at w = 0; it lands
inside M3's fitted domain; and it is the only reading consistent with the
registration's stated mechanism. Reading A inverts the sign; reading B fails the
w = 0 reduction and extrapolates outside the fitted domain. The planner's sanity
value corroborates C but does **not** gate it (rule 30 — expressly approximate,
"executor recomputes"; the RN-Q2-6 precedent).

## 3. The sealed prediction and its band

α(V) = c − κ0·V + (κ2/2)·V² from M3's persisted A-quad, consumed not refitted.
α({{VDES}}) = {{ADES}} → α({{VEFF}}) = {{AEFF}}.

<<TABLE:band>>

The **r-channel shift** is the honest part: this split-seed instrument reads
{{RPW0}} at w = 0 where M3's own curve says {{ADES}}, a gain of {{GAIN}}. The
curve's currency is not exactly ours, and the #61 convention requires that to
sit inside SE_approx rather than be wished away.

`prediction.json` was hashed `{{SHA16}}…` and stamped {{STAMP}} with
**{{NFRESH}} fresh-arm worlds in existence** ({{NPROBE}} probe worlds
necessarily precede it — they are the band's inputs). The arms re-read the stamp
from disk and re-hashed to a match at {{PERMIT}}, {{PGAP}} s later.

## 4. Gates

<<TABLE:gates>>

<<TABLE:projection>>

## 5. Results

<<TABLE:arms>>

<<TABLE:verdicts>>

### 5.1 The sealed test

Measured ΔR_T = {{MEAS}} {{CI}} against a predicted {{PRED}} — position
{{POS}} of the half-width, **{{CLS}}**. Against zero: the 2·SEM equivalence
scale is {{NULLEPS}}, so the null-first classification is {{NULLSTR}}.

{{INTERP}} R_T_nat moves {{RTW0}} → {{RTW1}}.

<<TABLE:rescored>>

{{RESCUE}}

### 5.2 The cross-frame identity reading

R_S_ref(w=1) = {{CMEAS}} {{CCI}} against ε = {{CEPS}} → **{{CCLS}}**.

The gauge reads essentially nothing of the planted identity across frames: the
point estimate is {{CMEAS}} against a null anchor of {{ANCHREF}}, and identity
is unambiguously present in both worlds (C-R1b, re-certified in G1r2).

**A stability disclosure that cuts against the tidy reading.** The classification
sits on a knife edge. The lower CI edge misses −ε by {{GAPLO}}, which is
{{GAPSE}} of the Monte-Carlo standard error of that percentile at the registered
B = {{BREG}} ({{MCSE}}). At B = {{BHIGH}} the interval is {{CIH}} and the
classification would be **{{CB2}}**. Q2's rule-13 trigger asks whether a
boundary's *tail fraction* is within Monte-Carlo noise and is silent here,
because this instability lives in the *percentile value* instead — it did not
fire ({{R13F}}). The registered B = 2000 classification is what is reported and
what routes; the high-B reading is a disclosed diagnostic, **not** a
re-resolution. Nothing turns on the choice: cell {{CELL}} fires on V-R2a alone,
so the outcome slug is identical under both. This is offered to the planner as a
convention candidate, not resolved here.

### 5.3 Descriptive readings (gate nothing)

<<TABLE:descriptive>>

At w = 1 trait and style enter exchangeably, and the measured ratio R_S/R_T =
{{EXR}} is that symmetry, not a discovery (#59, RN-R2-6).

**The registration's expectation for the w = 0 anchor is not met, and the reason
is structural.** It expected R_S_nat(w = 0) ≈ 0 — style drawn but weightless, so
nothing to read. The measured anchor is {{ANCH}}, close to R_T_nat's own
{{RTW0}}. The cause is the pipeline's truth-panel convention, which this leg
inherited unchanged and pinned in Part 0: truth panels are
`emit_panel(world, w, active=("mu","common"))`, so **they carry the frame**. At
w = 0 the gauge is shown no style whatsoever, yet the style truth panel still
contains that world's `common` channel, and the gauge agrees with *that*. The
anchor is measuring frame agreement, not style reading. It is an anchor and not
a verdict, so nothing routes on it — but the expectation was wrong and the
number should not be read as the registration framed it.

This matters for §5.2. `R_S_ref(w=1) vs 0` conflates "the gauge cannot read
style across frames" with "the frame does not transport" — the latter already
established by the whole P-line. The frame-controlled contrast is the paired
increment over the w = 0 arm, which holds the frame path fixed and varies only
whether the gauge was shown any style:

<<TABLE:crossframe>>

The cross-frame increment is {{XINC}} {{XCI}} (excludes zero: {{XEX}}), against
a within-frame increment of {{WINC}} {{WCI}} — a ratio of {{XRAT}}. Showing the
gauge a full-strength identity channel buys it **nothing** it can read through a
refreshed frame, while the same channel is plainly readable within frame. That
is the sharper statement of the P-line's limitation, and it is a diagnostic
offered alongside the registered verdict, not a replacement for it.

## 6. Anomalies

1. **A-1 (before any number).** The dispatched interpreter was absent; a pinned
   CPython venv was built from `requirements-lock-main.txt` and recorded:
   `{{PYEXE}}`.
2. **A-2 (before any number).** `timeout(1)` is absent on macOS; every stage ran
   as its own foreground command under an explicit tool timeout.
3. **A-4 (disclosed ordering fact, before the stamp).** The band's SE_meas has
   to come from pre-measurement objects, so the 16 probe pairs were scored at
   *both* doses before `prediction.json` was sealed — which means a paired
   probe ΔR_T ({{PROBED}}) existed before the stamp. It was **never consumed**:
   the prediction is `α(V_eff) − α(V_design)`, built from variance shares and
   M3's persisted θ with no R term in it at all; SE_meas takes only the probe
   difference's *standard deviation*; the gain g takes only the *w = 0 level*.
   The probe difference's **mean** enters no expression that routes (#57 —
   variances only). It is reported here rather than omitted, because the
   alternative to disclosing it is asking the reader to trust that it was not
   used.
4. **A-3 (before any number).** Two machinery hazards were caught while writing
   the harness, both from prior legs' scars: the corpus string must not encode
   the dose (RN-P1-8 — it enters the frozen map, and a w-dependent corpus would
   contaminate ΔR_T at its root), and seeds must depend on the pair index only
   so the doses are bit-paired (RN-R2-3). Both were fixed before any world was
   built.

## 7. Boundary

EXPLORATORY, synthetic, label-free. One share, one φ, two doses. The identity
channel is planted; appendix KK's structural boundary is unmoved. {{BOUND}} The
measurement itself is precise: {{NPAIRS}} paired pairs, SEM {{SEMM}}.

## 8. Environment

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

    def fmt(v: Any) -> str:
        if isinstance(v, bool):
            return str(v)
        if isinstance(v, float):
            return repr(v)
        if isinstance(v, list):
            return repr(v)
        return str(v)

    for key, val in facts.items():
        text = text.replace("{{" + key + "}}", fmt(val))
    left = re.findall(r"\{\{[A-Z0-9_]+\}\}|<<TABLE:[a-z_]+>>", text)
    if left:
        raise SystemExit(f"unresolved placeholders: {sorted(set(left))}")
    REPORT.write_text(text, encoding="utf-8")
    print(f"report OK  {rel(REPORT)}  ({len(text.splitlines())} lines)")


# ---------------------------------------------------------------------------


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
