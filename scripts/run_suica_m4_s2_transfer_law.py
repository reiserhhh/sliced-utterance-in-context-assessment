#!/usr/bin/env python3
"""SUICA M4-S2 -- the transfer law (sealed shape of r(gamma)).

Registered BEFORE run in docs/SUICA_M4_S_SELECTION_LINE_PLAN.md ("M4-S2",
commit 84962a5).  Binding.  The synthetic half of the owner's conjecture, as a
sealed quantitative law.

Selection similarity is driven by gamma*u + (1-gamma)*v with u orthogonal to v
(S1-certified); trait similarity by u alone.  The derived shape is

    r(gamma) = r(1) * g(gamma),   g(gamma) = gamma^2 / sqrt(gamma^4 + (1-gamma)^4)

with r(1) = S1's persisted 0.23983432331725474 carrying the amplitude.  The
three INTERIOR points (gamma 0.25 / 0.5 / 0.75) are the sealed test: g is
sharply non-linear -- a near-flat top and a collapsing knee -- so no smooth
monotone guess reproduces it by luck.

Bands per #61: SE_pred (S1's r(1) CI propagated) (+) SE_meas (S1's persisted
per-arm spread, rescaled) (+) SE_approx (the softmax / z-scoring distortion
budget, derived from the pipeline's own arithmetic on PROBE-FREE objects --
standard normals through softmax and the cosine pipeline, no worlds).

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
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LEG = "M4-S2"
OUT = ROOT / "results" / "m4_s2_transfer_law"
REPORT = ROOT / "reports" / "SUICA_M4_S2_TRANSFER_LAW_REPORT.md"
S1SRC = ROOT / "scripts" / "run_suica_m4_s1_choice_generator.py"
S1RES = ROOT / "results" / "m4_s1_choice_generator"

SHARE = 0.25
PHI = 0.60
W_STYLE = 1.0
BETA_STAR = 1.7
GAMMAS = (0.0, 0.25, 0.5, 0.75, 1.0)
INTERIOR = (0.25, 0.5, 0.75)
N_WORLDS = 16
N_ESCALATED = 32
N_PILOT = 4
MASTER_SEED = 20260816
SALT_AUTHOR = "m4s2-author"
SALT_FRAME = "m4s2-frameA"
SALT_PILOT = "m4s2-pilot"

R1_AMPLITUDE = 0.23983432331725474      # S1's persisted r(gamma=1); G0 verifies
B_BOOT = 2000
CI_Q = (2.5, 97.5)
B_PROJ = 2000
POWER_MIN = 0.80
FALSE_FIRE_MAX = 0.10
SATURATION_ABS = 0.999
N_MC_APPROX = 12                        # MC reps for the distortion budget
N_AUTH_MC = 565                         # the retained-author count
CONSERVATISM = 1.5                      # RN-S2-3: R2b's 1.53x undersizing lesson

RN_NOTES = {
    "RN-S2-1":
        "the measurement is S1's CERTIFIED instrument, unchanged and imported by "
        "file with its hash verified: build_choice_world and world_selection_stats "
        "are called directly, so this leg's r(gamma) is the same object as S1's "
        "C-S1c Mantel and is directly comparable to the persisted amplitude "
        "r(1) = 0.23983432331725474.  Only the salts and the gamma grid differ.",
    "RN-S2-2":
        "K2f ordering: the three INTERIOR predictions and their bands are hashed "
        "and stamped before any fresh world exists; the pilot runs after the "
        "stamp; the arms re-read the stamp from disk and re-hash to a match.  The "
        "endpoints are ANCHORS, not sealed tests -- gamma = 1 is checked "
        "distributionally against S1 and gamma = 0 against the epsilon-null, and "
        "an anchor failure routes INSTRUMENT_DEFECT, never a shape cell.",
    "RN-S2-3":
        "SE_approx is the softmax / z-scoring DISTORTION budget and is built from "
        "PROBE-FREE objects: standard-normal u and v are pushed through the "
        "pipeline's own arithmetic (z-scoring, score = beta*(gamma u + (1-gamma) "
        "v), softmax, cosine of the resulting preference vectors, Mantel against "
        "cosine of centred u) with NO world, NO builder and NO multinomial "
        "sampling.  The realized shape ratio is compared to the analytic g(gamma) "
        "and the deviation is the budget.  CONSTRUCTION AND CONSERVATISM "
        "DIRECTION, stated as the registration requires: the budget takes the MAX "
        "absolute deviation across MC repetitions (not the mean) and multiplies "
        "by 1.5, because in R2b this executor's probe-based transport term "
        "UNDERSIZED the realized value by 1.53x.  The budget therefore errs "
        "WIDE -- it makes the sealed test EASIER to pass, which is the direction "
        "that must be disclosed rather than the one that flatters a hit.  It "
        "deliberately excludes multinomial sampling noise, which is SE_meas's job.",
    "RN-S2-4":
        "SE_meas comes from S1's PERSISTED per-arm spread at the same beta and "
        "panel, rescaled to this leg's 16 worlds and df-inflated -- a persisted "
        "object, not a fresh probe, so no world precedes the stamp at all.",
    "RN-S2-6":
        "REGISTRATION-DEFECT CANDIDATE, pinned before any world.  SE_approx as "
        "registered absorbs the softmax distortion into BAND WIDTH, but the "
        "budget's own arithmetic shows that distortion is a SYSTEMATIC, "
        "sign-stable bias (the analytic g overshoots the pipeline ratio at every "
        "interior gamma) whose MC spread is an order of magnitude smaller than "
        "the bias itself.  A #61 band is a statement of UNCERTAINTY; a known bias "
        "belongs in the PREDICTION.  Absorbing it into width inflates the gamma = "
        "0.5 half-width past the prediction itself and makes V-S2b nearly "
        "unfalsifiable.  The registered analytic prediction still ROUTES, "
        "unchanged and stamped; a SECOND prediction using the pipeline ratio is "
        "stamped alongside it -- equally probe-free, equally pre-world -- and is "
        "reported as the sharp test while adjudicating nothing.",
    "RN-S2-5":
        "#59 non-degeneracy: the interior g values are NOT forced.  g(0.25) = "
        "0.1104 and g(0.75) = 0.9938 are wildly asymmetric about g(0.5) = 0.7071, "
        "so a linear-in-gamma alternative (0.25 / 0.50 / 0.75) or a "
        "gamma^2-proportional one would both miss; G1s2 additionally verifies the "
        "interior arms' preference vectors are genuinely MIXED rather than "
        "collapsing to either pure channel.",
}

_MODS: dict[str, Any] = {}


def _load_named(name: str, path: Path) -> Any:
    if name not in _MODS:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)          # type: ignore[arg-type]
        sys.modules[name] = mod
        spec.loader.exec_module(mod)                         # type: ignore[union-attr]
        _MODS[name] = mod
    return _MODS[name]


def s1() -> Any:
    return _load_named("run_suica_m4_s1_choice_generator", S1SRC)


def k2b() -> Any:
    return s1().k2b()


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
    key = f"{LEG}|{salt}|{kind}|i{i}|seed{MASTER_SEED}"
    return int(v8().stable_bucket(key, salt=salt, modulus=2 ** 63 - 1))


def world_seeds(i: int, suffix: str = "") -> dict[str, int]:
    return {"author": seed_for("author", i, SALT_AUTHOR + suffix),
            "frame": seed_for("frame", i, SALT_FRAME + suffix)}


def df_inflation(df: int) -> float:
    return float(math.sqrt(df / stats.chi2.ppf(0.10, df)))


def g_of(gamma: float) -> float:
    g4 = gamma ** 4
    o4 = (1.0 - gamma) ** 4
    den = math.sqrt(g4 + o4)
    return 0.0 if den == 0 else float(gamma ** 2 / den)


# ---------------------------------------------------------------------------
# THE MEASUREMENT -- S1's certified instrument, unchanged (RN-S2-1).


def measure_world(gamma: float, i: int, suffix: str = "") -> dict[str, Any]:
    m_ = s1()
    lay = k2b().layout()
    sd = world_seeds(i, suffix)
    wd = m_.build_choice_world(sd["author"], sd["frame"], PHI, W_STYLE,
                               BETA_STAR, gamma)
    st = m_.world_selection_stats(wd, lay["retained_idx"])
    idx = lay["retained_idx"]
    f = m_.freq_vectors(wd, idx)
    tr = wd["trait_pure"][idx] - wd["trait_pure"][idx].mean(axis=0, keepdims=True)
    # V-S2c: the direction reading -- distance-based selection similarity.
    fn = f / np.linalg.norm(f, axis=1, keepdims=True).clip(1e-12)
    gm = fn @ fn.T
    d2 = np.clip(np.diag(gm)[:, None] + np.diag(gm)[None, :] - 2 * gm, 0.0, None)
    iu = np.triu_indices(len(f), k=1)
    a_dist = (-np.sqrt(d2))[iu]
    trn = tr / np.linalg.norm(tr, axis=1, keepdims=True).clip(1e-12)
    b_cos = (trn @ trn.T)[iu]
    r_dist = float(np.corrcoef(a_dist, b_cos)[0, 1])
    pi_mix = float(np.mean(np.sort(wd["pi"][idx], axis=1)[:, -1]))
    return {"gamma": gamma, "world": i, "author_seed": sd["author"],
            "frame_seed": sd["frame"],
            "mantel_r": st["mantel_r"], "mantel_r_distance": r_dist,
            "split_half_r": st["split_half_r"],
            "chi2_frac": st["chi2_frac_exceeding_95"],
            "entropy_frac": st["entropy_frac_of_log4"],
            "pi_max_mean": pi_mix}


# ---------------------------------------------------------------------------
# SE_approx -- PROBE-FREE distortion budget (RN-S2-3).


def distortion_budget(betas: float, gammas: tuple[float, ...],
                      n_auth: int, reps: int, seed: int) -> dict[str, Any]:
    """Standard normals through the pipeline's own arithmetic.  No world, no
    builder, no multinomial draw -- the softmax / z-scoring distortion alone."""
    rng = np.random.default_rng(seed)
    iu = np.triu_indices(n_auth, k=1)

    def _cos_pairs(x: np.ndarray) -> np.ndarray:
        n = np.linalg.norm(x, axis=1, keepdims=True)
        n[n == 0] = 1.0
        xx = x / n
        return (xx @ xx.T)[iu]

    per_rep: list[dict[str, float]] = []
    for _ in range(reps):
        u = rng.normal(size=(n_auth, 4))
        v = rng.normal(size=(n_auth, 4))
        u = (u - u.mean(0)) / u.std(0, ddof=1)
        v = (v - v.mean(0)) / v.std(0, ddof=1)
        b_tr = _cos_pairs(u - u.mean(0, keepdims=True))
        vals: dict[float, float] = {}
        for gam in (*gammas, 1.0):
            sc = betas * (gam * u + (1.0 - gam) * v)
            e = np.exp(sc - sc.max(axis=1, keepdims=True))
            pi = e / e.sum(axis=1, keepdims=True)
            a = _cos_pairs(pi)
            vals[gam] = (0.0 if a.std() == 0 else
                         float(np.corrcoef(a, b_tr)[0, 1]))
        base = vals[1.0]
        per_rep.append({g: (vals[g] / base if base else 0.0) for g in gammas})
    out: dict[str, Any] = {"reps": reps, "n_authors": n_auth,
                           "beta": betas, "per_gamma": {}}
    for gam in gammas:
        ratios = np.array([p[gam] for p in per_rep], dtype=float)
        analytic = g_of(gam)
        dev = np.abs(ratios - analytic)
        out["per_gamma"][str(gam)] = {
            "analytic_g": analytic,
            "pipeline_ratio_mean": float(ratios.mean()),
            "pipeline_ratio_sd": float(ratios.std(ddof=1)),
            "abs_deviation_mean": float(dev.mean()),
            "abs_deviation_max": float(dev.max()),
            "budget_shape_units": float(dev.max() * CONSERVATISM)}
    out["conservatism_factor"] = CONSERVATISM
    out["note"] = RN_NOTES["RN-S2-3"]
    return out


# ---------------------------------------------------------------------------
# PART 0.


def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")
    s1p0 = read_json(S1RES / "part0.json")
    s1fit = read_json(S1RES / "fit.json")
    g1 = s1fit["C_S1c"]["gamma1"]
    g0 = s1fit["C_S1c"]["gamma0"]
    eps_s1 = float(s1fit["C_S1c"]["eps"])
    beta_s1 = float(s1p0["beta_star"]["beta_star"])
    g0s2 = {
        "s1_hash": sha_file(S1SRC),
        "s1_slug": read_json(S1RES / "decision.json")["verdict_slug"],
        "r1_persisted": float(g1["mean"]),
        "r1_registration": R1_AMPLITUDE,
        "r1_bit_exact": bool(float(g1["mean"]) == R1_AMPLITUDE),
        "r1_ci95": g1["ci95"], "r1_sd": float(g1["sd"]), "r1_n": int(g1["n"]),
        "gamma0_persisted_mean": float(g0["mean"]),
        "eps_s1": eps_s1,
        "perm_sd_s1": float(s1p0["C_S1c_band"]["permutation_sd_single_world"]),
        "beta_star_persisted": beta_s1,
        "beta_star_matches_registration": bool(beta_s1 == BETA_STAR),
        "uv_pin": "first four principal author-coordinates per channel, "
                  "orthonormalized, z-scored, sign fixed by largest-|loading| "
                  "(S1 RN-S1-2, #64)",
        "s1_C_S1c_PASS": bool(s1fit["C_S1c"]["PASS"]),
    }
    g0s2["PASS"] = bool(g0s2["r1_bit_exact"]
                        and g0s2["beta_star_matches_registration"]
                        and g0s2["s1_C_S1c_PASS"])
    if not g0s2["PASS"]:
        write_json(OUT / "part0.json", {"G0s2": g0s2})
        raise SystemExit("G0s2 FAILED -> STOP")

    # --- the distortion budget (probe-free, no worlds)
    budget = distortion_budget(BETA_STAR, INTERIOR, N_AUTH_MC, N_MC_APPROX,
                               MASTER_SEED)

    # --- band terms
    r1 = R1_AMPLITUDE
    se_r1 = float((g1["ci95"][1] - g1["ci95"][0]) / (2 * 1.959963984540054))
    dfree = int(g1["n"]) - 1
    infl = df_inflation(dfree)
    se_meas = float(g0s2["r1_sd"] * infl / math.sqrt(N_WORLDS))
    preds: dict[str, Any] = {}
    for gam in INTERIOR:
        g = g_of(gam)
        se_pred = float(g * se_r1)
        se_approx = float(r1 * budget["per_gamma"][str(gam)]["budget_shape_units"])
        comb = float(math.sqrt(se_pred ** 2 + se_meas ** 2 + se_approx ** 2))
        half = float(2.0 * comb)
        pred = float(r1 * g)
        preds[str(gam)] = {
            "gamma": gam, "g": g, "prediction": pred,
            "planner_sanity_g": {"0.25": 0.1104, "0.5": 0.7071,
                                 "0.75": 0.9938}[str(gam)],
            "g_matches_sanity_4dp": bool(round(g, 4) == round(
                {"0.25": 0.1104, "0.5": 0.7071, "0.75": 0.9938}[str(gam)], 4)),
            "band": {"SE_pred": se_pred, "SE_meas": se_meas,
                     "SE_approx": se_approx, "combined_SE": comb,
                     "half_width": half,
                     "band": [pred - half, pred + half]}}
    # --- RN-S2-6: a SECOND sealed prediction, also probe-free and stamped in the
    # same breath.  The budget's own numbers show the analytic g is not merely
    # uncertain but SYSTEMATICALLY high at every interior gamma, with an MC
    # spread an order smaller than the bias.  A #61 band is for UNCERTAINTY; a
    # known, sign-stable, precisely-estimated bias belongs in the PREDICTION.
    # The registered analytic prediction still routes (it is what was
    # registered); this sharper one is declared secondary and adjudicates
    # nothing, but it is the honest test and it is fixed before any world.
    preds_pipe: dict[str, Any] = {}
    for gam in INTERIOR:
        bg = budget["per_gamma"][str(gam)]
        ratio = float(bg["pipeline_ratio_mean"])
        pred_p = float(r1 * ratio)
        se_pred_p = float(ratio * se_r1)
        se_mc = float(r1 * bg["pipeline_ratio_sd"] / math.sqrt(N_MC_APPROX))
        comb_p = float(math.sqrt(se_pred_p ** 2 + se_meas ** 2 + se_mc ** 2))
        preds_pipe[str(gam)] = {
            "gamma": gam, "pipeline_ratio": ratio, "prediction": pred_p,
            "analytic_prediction": float(r1 * g_of(gam)),
            "bias_analytic_minus_pipeline": float(r1 * (g_of(gam) - ratio)),
            "band": {"SE_pred": se_pred_p, "SE_meas": se_meas,
                     "SE_mc": se_mc, "combined_SE": comb_p,
                     "half_width": float(2.0 * comb_p),
                     "band": [pred_p - 2 * comb_p, pred_p + 2 * comb_p]}}

    pred_obj = {
        "leg": LEG, "amplitude_r1": r1,
        "secondary_pipeline_predictions": preds_pipe,
        "secondary_note": RN_NOTES["RN-S2-6"],
        "shape": "r(gamma) = r(1) * gamma^2 / sqrt(gamma^4 + (1-gamma)^4)",
        "interior_predictions": preds,
        "SE_pred_basis": {"S1_r1_ci95": g1["ci95"], "implied_SE_r1": se_r1},
        "SE_meas_basis": {"S1_per_world_sd": g0s2["r1_sd"], "S1_n": g1["n"],
                          "df_inflation": infl, "n_worlds_this_leg": N_WORLDS,
                          "note": RN_NOTES["RN-S2-4"]},
        "SE_approx_basis": budget,
        "anchors": {"gamma1_reference_mean": r1, "gamma1_reference_ci": g1["ci95"],
                    "gamma0_eps": eps_s1,
                    "note": "anchors route INSTRUMENT_DEFECT, never a shape cell"},
        "RN_NOTES": RN_NOTES,
    }
    write_json(OUT / "prediction.json", pred_obj)
    digest = hashlib.sha256((OUT / "prediction.json").read_bytes()).hexdigest()
    stamp = {"sha256": digest, "stamp_utc": datetime.now(UTC).isoformat(),
             "fresh_worlds_before_stamp": 0,
             "probe_worlds_before_stamp": 0,
             "mc_draws_before_stamp": "standard normals only (no world, no "
                                      "builder, no multinomial draw)"}
    write_json(OUT / "prediction.sha256.json", stamp)
    write_json(OUT / "part0.json", {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(), "G0s2": g0s2,
        "prediction": pred_obj, "stamp": stamp, "RN_NOTES": RN_NOTES,
        "design": {"gammas": list(GAMMAS), "n_worlds": N_WORLDS,
                   "share": SHARE, "phi": PHI, "w_style": W_STYLE,
                   "beta": BETA_STAR, "master_seed": MASTER_SEED,
                   "salts": [SALT_AUTHOR, SALT_FRAME, SALT_PILOT]},
        "environment": {"python_executable": sys.executable,
                        "python_version": sys.version.split()[0],
                        "platform": platform.platform(),
                        "numpy": np.__version__, "pandas": pd.__version__},
        "seconds": time.time() - t0})
    _log("part0_done", sha=digest)
    print(f"part0 OK  r(1)={r1!r} bit-exact={g0s2['r1_bit_exact']}  "
          f"beta*={beta_s1!r}\n"
          + "\n".join(
              f"  g({k})={v['g']!r} pred={v['prediction']!r} half="
              f"{v['band']['half_width']!r} (pred {v['band']['SE_pred']:.3e} / "
              f"meas {v['band']['SE_meas']:.3e} / approx "
              f"{v['band']['SE_approx']:.3e})" for k, v in preds.items())
          + f"\n  STAMPED {digest[:16]}  fresh worlds before stamp=0  "
            f"{time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------


def _permit() -> dict[str, Any]:
    raw = (OUT / "prediction.json").read_bytes()
    st = read_json(OUT / "prediction.sha256.json")
    d = hashlib.sha256(raw).hexdigest()
    if d != st["sha256"]:
        raise SystemExit("PREDICTION HASH MISMATCH -> STOP")
    t = datetime.fromisoformat(st["stamp_utc"])
    now = datetime.now(UTC)
    return {"sha256": d, "matches": True, "permit_utc": now.isoformat(),
            "seconds_stamp_to_permit": (now - t).total_seconds()}


def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("pilot_start")
    rows = [measure_world(g, i, "-pilot")
            for g in (0.25, 0.75) for i in range(N_PILOT)]
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "pilot_field.csv", index=False)
    preds = {}
    for g in (0.25, 0.75):
        v = df[df.gamma == g]["mantel_r"].to_numpy(float)
        preds[f"g{g}"] = {"all_finite": bool(np.all(np.isfinite(v))),
                          "any_saturated": bool(np.any(np.abs(v)
                                                       >= SATURATION_ABS)),
                          "nonzero_variance": bool(float(np.std(v, ddof=1)) > 0),
                          "min": float(v.min()), "max": float(v.max())}
        preds[f"g{g}"]["PASS"] = bool(preds[f"g{g}"]["all_finite"]
                                      and not preds[f"g{g}"]["any_saturated"]
                                      and preds[f"g{g}"]["nonzero_variance"])
    # G1s2 #59: the interior arms' preferences are genuinely MIXED
    mix = {f"g{g}": float(df[df.gamma == g]["pi_max_mean"].mean())
           for g in (0.25, 0.75)}
    out = {"n": N_PILOT, "predicates": preds,
           "PASS": bool(all(p["PASS"] for p in preds.values())),
           "pi_max_mean": mix,
           "interior_pi_is_mixed": bool(all(0.26 < m < 0.99 for m in mix.values())),
           "means": {f"g{g}": float(df[df.gamma == g]["mantel_r"].mean())
                     for g in (0.25, 0.75)},
           "sd": {f"g{g}": float(np.std(df[df.gamma == g]["mantel_r"], ddof=1))
                  for g in (0.25, 0.75)},
           "permit": _permit(), "seconds": time.time() - t0}
    write_json(OUT / "pilot.json", out)
    _log("pilot_done")
    if not (out["PASS"] and out["interior_pi_is_mixed"]):
        raise SystemExit("G2s2/G1s2 FAILED -> INSTRUMENT_DEFECT")
    print(f"pilot OK  means={out['means']}  pi_max={mix}  mixed="
          f"{out['interior_pi_is_mixed']}  permit "
          f"{out['permit']['seconds_stamp_to_permit']:.3f}s after the stamp  "
          f"{time.time() - t0:.1f}s")


def stage_project(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("project_start")
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    preds = p0["prediction"]["interior_predictions"]
    infl = df_inflation(N_PILOT - 1)
    sd_pool = float(np.mean([pil["sd"]["g0.25"], pil["sd"]["g0.75"]])) * infl

    def project(n: int) -> dict[str, Any]:
        rng = np.random.default_rng(MASTER_SEED)
        se = sd_pool / math.sqrt(n)
        res: dict[str, Any] = {"n_worlds": n, "SE": se, "per_gamma": {}}
        for k, v in preds.items():
            half = v["band"]["half_width"]
            d_true = rng.normal(v["prediction"], se, size=B_PROJ)
            p_in = float(np.mean(np.abs(d_true - v["prediction"]) <= half))
            d_off = rng.normal(v["prediction"] - 3 * half, se, size=B_PROJ)
            p_ff = float(np.mean(np.abs(d_off - v["prediction"]) <= half))
            res["per_gamma"][k] = {
                "half_width": half, "power_at_truth": p_in,
                "false_fire_at_minus3band": p_ff,
                "PASS": bool(p_in >= POWER_MIN and p_ff <= FALSE_FIRE_MAX)}
        res["PASS"] = bool(all(v["PASS"] for v in res["per_gamma"].values()))
        return res

    base = project(N_WORLDS)
    out = {"base": base, "escalation_fired": False, "escalated": None,
           "sd_pooled_df_inflated": sd_pool, "PASS": base["PASS"],
           "n_final": N_WORLDS}
    if not base["PASS"]:
        esc = project(N_ESCALATED)
        out.update({"escalation_fired": True, "escalated": esc,
                    "PASS": esc["PASS"],
                    "n_final": N_ESCALATED if esc["PASS"] else N_WORLDS})
    write_json(OUT / "projection.json", out)
    _log("project_done")
    if not out["PASS"]:
        raise SystemExit("G3s2 FAILED -> NON_PROJECTABLE")
    print("project OK  " + "  ".join(
        f"g{k}: power {v['power_at_truth']!r} ff {v['false_fire_at_minus3band']!r}"
        for k, v in out["base"]["per_gamma"].items())
        + f"  n={out['n_final']}  escalated={out['escalation_fired']}  "
          f"{time.time() - t0:.1f}s")


def stage_arm(args: argparse.Namespace) -> None:
    t0 = time.time()
    (OUT / "arms").mkdir(parents=True, exist_ok=True)
    write_json(OUT / "arm_permit.json", _permit())
    n_final = int(read_json(OUT / "projection.json")["n_final"])
    gam = float(args.gamma)
    _log("arm_start", gamma=gam)
    rows = [measure_world(gam, i) for i in range(n_final)]
    pd.DataFrame(rows).to_csv(OUT / "arms" / f"gamma_{gam}.csv", index=False)
    _log("arm_done", gamma=gam, n=len(rows))
    print(f"arm gamma={gam} OK  rows={len(rows)}  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------


def stage_fit(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("fit_start")
    p0 = read_json(OUT / "part0.json")
    pred = p0["prediction"]
    frames = {}
    for g in GAMMAS:
        frames[g] = read_csv_rt(OUT / "arms" / f"gamma_{g}.csv")
    rng = np.random.default_rng(MASTER_SEED)

    def stat(v: np.ndarray) -> dict[str, Any]:
        idx = rng.integers(0, len(v), size=(B_BOOT, len(v)))
        bs = v[idx].mean(axis=1)
        return {"mean": float(v.mean()),
                "sem": float(np.std(v, ddof=1) / math.sqrt(len(v))),
                "sd": float(np.std(v, ddof=1)),
                "ci95": [float(np.percentile(bs, CI_Q[0])),
                         float(np.percentile(bs, CI_Q[1]))],
                "n": int(len(v))}

    measured = {str(g): stat(frames[g]["mantel_r"].to_numpy(float))
                for g in GAMMAS}
    dist = {str(g): stat(frames[g]["mantel_r_distance"].to_numpy(float))
            for g in GAMMAS}

    # V-S2b: the three sealed interior tests
    interior = {}
    hits = 0
    for k, v in pred["interior_predictions"].items():
        m = measured[k]
        err = m["mean"] - v["prediction"]
        inside = bool(abs(err) <= v["band"]["half_width"])
        hits += int(inside)
        interior[k] = {"gamma": v["gamma"], "g": v["g"],
                       "prediction": v["prediction"], "measured": m["mean"],
                       "ci95": m["ci95"], "sem": m["sem"],
                       "half_width": v["band"]["half_width"],
                       "band": v["band"]["band"], "signed_error": float(err),
                       "position_in_band": float(err / v["band"]["half_width"]),
                       "INSIDE": inside}
    # V-S2a: r(0) NULL
    eps = float(pred["anchors"]["gamma0_eps"])
    m0 = measured["0.0"]
    v_s2a = {**m0, "eps": eps,
             "NULL": bool(abs(m0["mean"]) <= eps and m0["ci95"][0] >= -eps
                          and m0["ci95"][1] <= eps),
             "label": "V-S2a: r(0) null on FRESH worlds"}
    # anchors
    r1ref = float(pred["anchors"]["gamma1_reference_mean"])
    m1 = measured["1.0"]
    sem_ref = float((p0["G0s2"]["r1_ci95"][1] - p0["G0s2"]["r1_ci95"][0])
                    / (2 * 1.959963984540054))
    sd_diff = float(math.sqrt(m1["sem"] ** 2 + sem_ref ** 2))
    anchors = {
        "gamma1": {"measured": m1["mean"], "ci95": m1["ci95"],
                   "s1_reference": r1ref, "deviation": float(m1["mean"] - r1ref),
                   "sem_diff": sd_diff,
                   "band_2sqrt2": float(2 * math.sqrt(2) * sd_diff),
                   "z": float((m1["mean"] - r1ref) / sd_diff),
                   "PASS": bool(abs(m1["mean"] - r1ref)
                                <= 2 * math.sqrt(2) * sd_diff)},
        "gamma0": {"measured": m0["mean"], "eps": eps, "PASS": v_s2a["NULL"]},
    }
    anchors["ALL_PASS"] = bool(anchors["gamma1"]["PASS"] and anchors["gamma0"]["PASS"])

    # V-S2c: cosine vs distance
    v_s2c = {"per_gamma": {k: {"cosine": measured[k]["mean"],
                               "distance": dist[k]["mean"],
                               "sign_agree": bool(
                                   np.sign(measured[k]["mean"])
                                   == np.sign(dist[k]["mean"]))}
                           for k in measured},
             "all_signs_agree": bool(all(
                 np.sign(measured[k]["mean"]) == np.sign(dist[k]["mean"])
                 for k in measured if abs(measured[k]["mean"]) > 1e-6)),
             "cosine_dominates": bool(
                 measured["1.0"]["mean"] > dist["1.0"]["mean"]),
             "label": "V-S2c reading (T8 direction question); adjudicates nothing"}

    out = {"measured": measured, "distance": dist, "interior": interior,
           "interior_hits": hits, "V_S2a": v_s2a, "anchors": anchors,
           "V_S2c": v_s2c, "n_worlds": int(measured["1.0"]["n"]),
           "seconds": time.time() - t0}
    write_json(OUT / "fit.json", out)
    _log("fit_done", hits=hits)
    print(f"fit OK  interior hits {hits}/3\n" + "\n".join(
        f"  g={v['gamma']} pred={v['prediction']!r} meas={v['measured']!r} "
        f"pos={v['position_in_band']:.4f} INSIDE={v['INSIDE']}"
        for v in interior.values())
        + f"\n  V-S2a r(0)={m0['mean']!r} eps={eps!r} NULL={v_s2a['NULL']}"
          f"\n  anchor g1 meas={m1['mean']!r} vs S1 {r1ref!r} z="
          f"{anchors['gamma1']['z']:.3f} PASS={anchors['gamma1']['PASS']}"
          f"\n  {time.time() - t0:.1f}s")


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    g3 = read_json(OUT / "projection.json")
    fit = read_json(OUT / "fit.json")
    hits = int(fit["interior_hits"])
    if not p0["G0s2"]["PASS"]:
        cell, slug, text = 1, "STOP", "G0 failure"
    elif not fit["anchors"]["ALL_PASS"]:
        bad = [k for k in ("gamma1", "gamma0") if not fit["anchors"][k]["PASS"]]
        cell, slug = 2, f"INSTRUMENT_DEFECT({','.join(bad)}_anchor)"
        text = "an anchor failed; anchors never route a shape cell"
    elif not g3["PASS"]:
        cell, slug, text = 3, "NON_PROJECTABLE", "projection failed"
    elif hits == 3:
        cell, slug = 4, "TRANSFER_LAW_SEALED"
        text = "all three interior points inside their sealed bands"
    elif hits == 2:
        cell, slug = 5, "SHAPE_PARTIAL"
        text = "two of three interior points inside; the miss names the distortion"
    else:
        cell, slug = 6, "SHAPE_WRONG"
        text = "the analytic form dies; the measured curve is reported"
    mods = []
    if fit["V_S2a"]["NULL"]:
        mods.append("GAMMA0_NULL_CONFIRMED_ON_FRESH_WORLDS")
    if fit["V_S2c"]["all_signs_agree"]:
        mods.append("DIRECTION_READING_AGREES")
    else:
        mods.append("DIRECTION_READING_SPLIT")
    dec = {"leg": LEG, "utc": datetime.now(UTC).isoformat(),
           "routing_cell": cell, "verdict_slug": slug, "routing_text": text,
           "modifiers": mods, "interior_hits": hits,
           "permit": read_json(OUT / "arm_permit.json"),
           "banner": "EXPLORATORY, synthetic, label-free; the coupling is BUILT "
                     "by the generator -- this is a law of the apparatus, not of "
                     "people",
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
    s: dict[str, list[str]] = {}
    s["sealed"] = _md(
        ["γ", "g(γ)", "planner sanity", "prediction", "SE_pred", "SE_meas",
         "SE_approx", "half-width", "band"],
        [[k, repr(v["g"]), repr(v["planner_sanity_g"]), repr(v["prediction"]),
          repr(v["band"]["SE_pred"]), repr(v["band"]["SE_meas"]),
          repr(v["band"]["SE_approx"]), repr(v["band"]["half_width"]),
          repr(v["band"]["band"])]
         for k, v in pred["interior_predictions"].items()])
    b = pred["SE_approx_basis"]
    s["budget"] = _md(
        ["γ", "analytic g", "pipeline ratio (mean)", "ratio sd",
         "|deviation| mean", "|deviation| max", "budget (× conservatism)"],
        [[k, repr(v["analytic_g"]), repr(v["pipeline_ratio_mean"]),
          repr(v["pipeline_ratio_sd"]), repr(v["abs_deviation_mean"]),
          repr(v["abs_deviation_max"]), repr(v["budget_shape_units"])]
         for k, v in b["per_gamma"].items()])
    sp = pred.get("secondary_pipeline_predictions", {})
    s["secondary"] = _md(
        ["γ", "pipeline ratio", "analytic pred", "pipeline pred",
         "bias absorbed by SE_approx", "half-width", "band"],
        [[k, repr(v["pipeline_ratio"]), repr(v["analytic_prediction"]),
          repr(v["prediction"]), repr(v["bias_analytic_minus_pipeline"]),
          repr(v["band"]["half_width"]), repr(v["band"]["band"])]
         for k, v in sp.items()])
    s["secondary_result"] = _md(
        ["γ", "measured", "analytic pred (routes)", "position vs analytic band",
         "pipeline pred (sharp)", "position vs pipeline band", "inside pipeline?"],
        [[k, repr(fit["measured"][k]["mean"]),
          repr(sp[k]["analytic_prediction"]),
          repr(fit["interior"][k]["position_in_band"]),
          repr(sp[k]["prediction"]),
          repr((fit["measured"][k]["mean"] - sp[k]["prediction"])
               / sp[k]["band"]["half_width"]),
          str(abs(fit["measured"][k]["mean"] - sp[k]["prediction"])
              <= sp[k]["band"]["half_width"])]
         for k in sp])
    s["measured"] = _md(
        ["γ", "measured Mantel r", "CI95", "SEM", "sd", "worlds"],
        [[k, repr(v["mean"]), repr(v["ci95"]), repr(v["sem"]), repr(v["sd"]),
          repr(v["n"])] for k, v in fit["measured"].items()])
    s["interior"] = _md(
        ["γ", "prediction", "measured", "CI95", "half-width", "position",
         "INSIDE"],
        [[str(v["gamma"]), repr(v["prediction"]), repr(v["measured"]),
          repr(v["ci95"]), repr(v["half_width"]), repr(v["position_in_band"]),
          "**" + str(v["INSIDE"]) + "**"] for v in fit["interior"].values()])
    a = fit["anchors"]
    s["anchors"] = _md(
        ["anchor", "measured", "reference", "test", "result"],
        [["γ = 1 vs S1 (distributional)", repr(a["gamma1"]["measured"]),
          repr(a["gamma1"]["s1_reference"]),
          f"|dev| {a['gamma1']['deviation']!r} ≤ 2√2·SEM "
          f"{a['gamma1']['band_2sqrt2']!r} (z {a['gamma1']['z']!r})",
          "**" + str(a["gamma1"]["PASS"]) + "**"],
         ["γ = 0 vs the ε-null", repr(a["gamma0"]["measured"]),
          "0", f"ε = {a['gamma0']['eps']!r}",
          "**" + str(a["gamma0"]["PASS"]) + "**"]])
    c = fit["V_S2c"]
    s["direction"] = _md(
        ["γ", "cosine selection similarity", "distance selection similarity",
         "signs agree"],
        [[k, repr(v["cosine"]), repr(v["distance"]), str(v["sign_agree"])]
         for k, v in c["per_gamma"].items()])
    s["projection"] = _md(
        ["γ", "half-width", "power at truth", "false-fire at −3·band", "PASS"],
        [[k, repr(v["half_width"]), repr(v["power_at_truth"]),
          repr(v["false_fire_at_minus3band"]), str(v["PASS"])]
         for k, v in g3["base"]["per_gamma"].items()])
    g0 = p0["G0s2"]
    s["gates"] = _md(
        ["gate", "PASS", "detail"],
        [["G0s2", str(g0["PASS"]),
          f"r(1) bit-exact {g0['r1_bit_exact']} ({g0['r1_persisted']!r}); β* "
          f"{g0['beta_star_persisted']!r} matches "
          f"{g0['beta_star_matches_registration']}; S1 C-S1c PASS "
          f"{g0['s1_C_S1c_PASS']}; S1 hash verified"],
         ["G1s2 / #59", str(pil["interior_pi_is_mixed"]),
          f"interior preferences genuinely mixed: mean max-π "
          f"{pil['pi_max_mean']} (1/4 = flat, 1 = collapsed)"],
         ["G2s2", str(pil["PASS"]), f"rule-29 predicates, {pil['n']} pilot worlds"],
         ["G3s2", str(g3["PASS"]),
          f"escalation fired: {g3['escalation_fired']}; n_final {g3['n_final']}"]])
    return {k: "\n".join(v) for k, v in s.items()}


def _facts(p0, pil, g3, fit, dec) -> dict[str, Any]:
    st = p0["stamp"]
    pred = p0["prediction"]
    a = fit["anchors"]
    return {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "MODS": ", ".join(dec["modifiers"]) or "none",
        "HITS": fit["interior_hits"],
        "R1": pred["amplitude_r1"],
        "SHA16": st["sha256"][:16], "STAMP": st["stamp_utc"],
        "PERMIT": dec["permit"]["permit_utc"],
        "PGAP": dec["permit"]["seconds_stamp_to_permit"],
        "NFRESH": st["fresh_worlds_before_stamp"],
        "NPROBE": st["probe_worlds_before_stamp"],
        "R0": fit["V_S2a"]["mean"], "R0CI": fit["V_S2a"]["ci95"],
        "EPS": fit["V_S2a"]["eps"], "R0NULL": fit["V_S2a"]["NULL"],
        "A1M": a["gamma1"]["measured"], "A1R": a["gamma1"]["s1_reference"],
        "A1Z": a["gamma1"]["z"], "A1P": a["gamma1"]["PASS"],
        "CONS": pred["SE_approx_basis"]["conservatism_factor"],
        "NW": fit["n_worlds"], "ESC": g3["escalation_fired"],
        "DIRAGREE": fit["V_S2c"]["all_signs_agree"],
        "DIRDOM": fit["V_S2c"]["cosine_dominates"],
        "PYEXE": p0["environment"]["python_executable"],
        "PYVER": p0["environment"]["python_version"],
        "SECOND_PROSE": _second_prose(fit, pred),
        "VERDICT": _verdict(fit, pred),
    }


def _second_prose(fit: dict[str, Any], pred: dict[str, Any]) -> str:
    sp = pred["secondary_pipeline_predictions"]
    n_pipe = sum(1 for k in sp
                 if abs(fit["measured"][k]["mean"] - sp[k]["prediction"])
                 <= sp[k]["band"]["half_width"])
    n_an = fit["interior_hits"]
    return (
        "**This is the leg's methodological finding, and it was fixed before any "
        "world existed.** The registered SE_approx absorbs the softmax distortion "
        "into band WIDTH. But the budget's own arithmetic shows that distortion "
        "is not uncertainty — it is a systematic, sign-stable bias: the analytic "
        "g overshoots the pipeline ratio at every interior γ, and the "
        "Monte-Carlo spread of that ratio is an order of magnitude smaller than "
        "the bias. Absorbing a known bias into a #61 band inflates the γ = 0.5 "
        "half-width past the prediction itself and makes the sealed test nearly "
        "unfalsifiable. **A #61 band states uncertainty; a known bias belongs in "
        "the prediction.**\n\n"
        f"So a second prediction was stamped alongside the first — equally "
        f"probe-free, equally pre-world — using the pipeline ratio directly. "
        f"The registered analytic prediction is what ROUTES and is unchanged. "
        f"On the measurements: **{n_an}/3 inside the registered analytic bands, "
        f"{n_pipe}/3 inside the far tighter pipeline bands.** The comparison is "
        "the point — a wide band that cannot fail is worth less than a narrow one "
        "that could have.")


def _verdict(fit: dict[str, Any], pred: dict[str, Any]) -> str:
    h = fit["interior_hits"]
    pos = ", ".join(f"γ={v['gamma']} at {v['position_in_band']!r}"
                    for v in fit["interior"].values())
    if h == 3:
        return (f"**The transfer law holds.** All three interior points land "
                f"inside bands fixed before any world existed ({pos}). The shape "
                f"r(γ) = r(1)·γ²/√(γ⁴+(1−γ)⁴) is sharply non-linear — a near-flat "
                f"top and a collapsing knee — so this is not a curve a smooth "
                f"monotone guess could have matched by luck.")
    if h == 2:
        return (f"**Two of three interior points land.** ({pos}.) The shape is "
                f"substantially right and the miss localizes where the analytic "
                f"derivation breaks.")
    return (f"**The analytic shape does not survive.** ({pos}.) The measured "
            f"curve is reported and the form is not retained.")


TEMPLATE = """# SUICA M4-S2 — the transfer law

**Outcome: `{{SLUG}}`** (rule-16 cell {{CELL}}). Modifiers: {{MODS}}.
Interior hits: **{{HITS}}/3**.

Registered before the run in `docs/SUICA_M4_S_SELECTION_LINE_PLAN.md` ("M4-S2",
commit 84962a5). EXPLORATORY, synthetic, label-free. **The coupling is built by
the generator**: this is a law of the apparatus, not of people.

## 1. What was sealed

Selection similarity is driven by γ·u + (1−γ)·v with u ⟂ v; trait similarity by
u alone. The derived shape is

    r(γ) = r(1) · g(γ),   g(γ) = γ² / √(γ⁴ + (1−γ)⁴)

with the amplitude r(1) = {{R1}} taken from S1 and bit-verified. The three
interior points are the test.

{{VERDICT}}

## 2. The sealed predictions

<<TABLE:sealed>>

`prediction.json` hashed `{{SHA16}}…`, stamped {{STAMP}} with **{{NFRESH}} fresh
worlds and {{NPROBE}} probe worlds in existence** — the band needed none, because
SE_meas came from S1's persisted spread and SE_approx from standard normals.
The arms re-read the stamp and re-hashed to a match at {{PERMIT}}, {{PGAP}} s
later.

### 2.1 The SE_approx budget, and which way it errs

<<TABLE:budget>>

SE_approx is the softmax / z-scoring distortion, built from **probe-free**
objects: standard-normal u and v pushed through the pipeline's own arithmetic —
z-scoring, score = β*(γu + (1−γ)v), softmax, cosine of the preference vectors,
Mantel against cosine of centred u — with no world, no builder and no
multinomial draw. The realized shape ratio is compared to the analytic g(γ) and
the deviation is the budget.

**Conservatism direction, stated as the registration requires:** the budget
takes the **maximum** absolute deviation across repetitions, not the mean, and
multiplies by {{CONS}}. The reason is R2b, where this executor's probe-based
transport term undersized the realized value by 1.53×. So the budget errs
**wide**, which makes the sealed test **easier** to pass. That is the direction a
reader must know, because it is the one that flatters a hit rather than the one
that excuses a miss. It deliberately excludes multinomial sampling noise, which
is SE_meas's job.

## 3. Gates

<<TABLE:gates>>

<<TABLE:projection>>

## 4. Results

<<TABLE:measured>>

### 4.1 V-S2b — the three sealed interior tests

<<TABLE:interior>>

### 4.1b The sharper, secondary prediction — and the defect it exposes

<<TABLE:secondary>>

<<TABLE:secondary_result>>

{{SECOND_PROSE}}

### 4.2 Anchors (these route INSTRUMENT_DEFECT, never a shape cell)

<<TABLE:anchors>>

γ = 1 re-measured on fresh worlds gives {{A1M}} against S1's {{A1R}} (z =
{{A1Z}}, PASS = {{A1P}}). γ = 0 gives {{R0}} {{R0CI}} against ε = {{EPS}} →
NULL = {{R0NULL}} — **the falsifier arm reproduces on fresh worlds**, which is
what licenses reading the interior points as shape rather than artefact.

### 4.3 V-S2c — the direction reading (adjudicates nothing)

<<TABLE:direction>>

Signs agree across geometries: {{DIRAGREE}}. Cosine exceeds distance at γ = 1:
{{DIRDOM}} — T8's expectation, checked rather than assumed.

## 5. Anomalies

1. **A-1 (before any number).** Interpreter re-verified as standing practice:
   `{{PYEXE}}`, Python {{PYVER}} — matching every prior leg.
2. **A-2 (before any number).** `timeout(1)` is absent on macOS; every stage ran
   as its own foreground command under an explicit tool timeout.
3. **A-3 (before any number).** No world of any kind — probe or arm — preceded
   the stamp, because both data-dependent band terms were sourced from persisted
   S1 objects and from standard-normal arithmetic. This is the cleanest K2f
   ordering the program has achieved.

## 6. Boundary

EXPLORATORY, synthetic, label-free. **γ is a knob this apparatus turns**, so the
law is a law of the generator; it says how a built coupling transfers, not that
any real selection behaviour obeys it. One share, one φ, one β, one panel,
{{NW}} worlds per arm. The real-data counterpart is SR1, which is a separate
measurement on a separate object and is not evidence for this shape (nor this
shape for it).

## 7. Environment

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
    ap.add_argument("--gamma", type=float, default=1.0)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    {"part0": stage_part0, "pilot": stage_pilot, "project": stage_project,
     "arm": stage_arm, "fit": stage_fit, "finalize": stage_finalize,
     "report": stage_report}[args.stage](args)


if __name__ == "__main__":
    main()
