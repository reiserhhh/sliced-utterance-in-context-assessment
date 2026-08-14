#!/usr/bin/env python3
"""SUICA M4-R1b -- clause (iv), re-banded and tested prospectively.

Registered BEFORE run in docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md
("M4-R1b", commit dec5557).  Binding.

R1 certified the planted identity channel on every clause but one: the
containment clause failed because the band was wrong (defect #61 -- zero width
at the deterministic point, and no term for the derivation's own approximation
error).  The instrument is UNCHANGED here; only clause (iv) is re-posed, and it
is re-posed PROSPECTIVELY: R1's doses are on the record, so a re-banded test on
them adjudicates nothing.  The primary test is a fresh dose, w_style = 0.75,
never measured, with the corrected band derived from PROBE worlds and HASHED
before the fresh arms exist.

    band half-width = 2 * sqrt(SE_pred^2 + SE_meas^2 + SE_approx^2)     (#61)

Stages: part0 -> pilot -> project -> arm -> fit -> finalize -> report
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

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "results" / "m4_r1b_reband"
RES = ROOT / "results"
R1SRC = ROOT / "scripts" / "run_suica_m4_r1_identity_channel.py"
R1RES = RES / "m4_r1_identity_channel"

LEG = "M4-R1b"
BANNER = ("clause (iv) re-banded per defect #61 and tested prospectively at a fresh "
          "dose; the instrument is unchanged")

MASTER_SEED = 20260814
SALT_AUTHOR = "m4r1b-author"
SALT_FRAME_A = "m4r1b-frameA"
SALT_FRAME_B = "m4r1b-frameB"
SALT_PILOT = "m4r1b-pilot"
SHARE = 0.25
PHI = 0.60
W_FRESH = 0.75
N_PAIRS = 128
N_PAIRS_ESCALATED = 256
PILOT_PAIRS = 4
PROBE_PAIRS = 16
W_INT_ARM = "zero"

B_BOOT = 2000
B_PROJ = 2000
POWER_MIN = 0.80
FALSE_FIRE_MAX = 0.10
DISPLACE = 3.0                      # the registered false-fire truth: pred - 3*band
SATURATION_ABS = 0.995

# ---------------------------------------------------------------------------
# RN-R1B notes.  PINNED IN PART 0, BEFORE THE STAMP AND BEFORE ANY FRESH ARM.
#
# RN-R1B-1 (why the primary is a fresh dose).  R1's Delta at w = 0.5 and 1.0 are
#   published.  Any band re-derived now could be checked against them by the
#   person deriving it, so a re-banded test on those doses cannot be
#   prospective however honestly it is run.  w = 0.75 has never been measured;
#   the prediction and band for it are derived from PROBE worlds, hashed, and
#   stamped before the fresh arms exist.  R1's doses are re-scored afterwards
#   and carry the post-hoc label, adjudicating nothing (the registration says
#   so and this harness enforces it by routing on w = 0.75 alone).
#
# RN-R1B-2 (where each SE term comes from -- all pre-measurement).  The #61
#   convention needs three terms and the pilot comes AFTER the stamp, so none
#   of them may come from the pilot:
#     SE_pred   -- the spread of the algebraic prediction across PROBE worlds,
#                  divided by sqrt(n_probes);
#     SE_approx -- the registration's own prescription: the realized per-author
#                  spread of delta_i = b_i/(a_i+b_i+d_i) on the PROBE worlds,
#                  as sd_i(delta_i)/sqrt(n_authors), averaged over probes.  This
#                  is the scale on which a mean-of-ratios can differ from the
#                  ratio-of-means, which is exactly the Jensen/orthogonality
#                  error R1 diagnosed;
#     SE_meas   -- the per-pair spread of the measured Delta across PROBE
#                  A/B pairs, divided by sqrt(n_pairs) at the decided design.
#   Probe worlds carry their own salt suffix and are never reused as arm worlds.
#
# RN-R1B-3 (the prediction's form is NOT changed).  R1's algebraic prediction
#   is the ratio-of-means b/(a+b+d), and #61 fixes the BAND, not the
#   prediction.  This leg keeps the same functional form so the test is of the
#   convention rather than of a quietly improved predictor.  The per-author
#   form mean_i[b_i/(a_i+b_i+d_i)] is computed and REPORTED as a diagnostic --
#   it is what the measurement actually estimates, and the gap between the two
#   is the very quantity SE_approx is meant to cover.
#
# RN-R1B-4 (ordering, K2f pattern).  The prediction and band are written to
#   prediction.json, hashed, and stamped before any fresh-arm world exists; the
#   arm refuses to run unless it can re-read the stamp from disk and re-hash
#   the file to a match, and the stamp records that no arm artifact existed at
#   stamp time.  The pilot runs AFTER the stamp (RN-K2F-4's precedent).  Probe
#   worlds are generated BEFORE the stamp by design -- they are the band's
#   inputs -- and are counted and disclosed separately from arm worlds.
#
# RN-R1B-5 (what a failure would mean).  BAND_STILL_WRONG is a live outcome:
#   it says the #61 error model is inadequate, not that the channel is absent.
#   The channel's other four certificates are R1's and stand regardless; this
#   leg can only close clause (iv) or report that the correction is still
#   short, with the realized decomposition as the handback.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-R1B-1": "the primary is a FRESH dose (w = 0.75, never measured) because R1's "
                "doses are published and a re-banded test on them cannot be prospective; "
                "R1's doses are re-scored afterwards with the post-hoc label and the "
                "routing uses w = 0.75 alone",
    "RN-R1B-2": "all three SE terms come from PROBE worlds, never the pilot (which runs "
                "after the stamp): SE_pred from the prediction's spread across probes, "
                "SE_approx from sd_i(b_i/(a_i+b_i+d_i))/sqrt(n_authors) per the "
                "registration, SE_meas from the per-pair Delta spread across probe pairs",
    "RN-R1B-3": "the prediction's FORM is unchanged (ratio-of-means, as R1) because #61 "
                "fixes the band, not the predictor; the per-author form is reported as a "
                "diagnostic since the gap between them is what SE_approx must cover",
    "RN-R1B-4": "K2f ordering: prediction.json is hashed and stamped before any fresh-arm "
                "world exists, the arm re-reads the stamp from disk and re-hashes to a "
                "match, and the pilot runs after the stamp; probe worlds precede the "
                "stamp by design and are counted separately",
    "RN-R1B-5": "BAND_STILL_WRONG is live and would mean the #61 error model is "
                "inadequate, not that the channel is absent; R1's other four "
                "certificates stand regardless",
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


def seed_for(kind: str, i: int, salt: str) -> int:
    key = f"{LEG}|{salt}|{kind}|w{W_FRESH!r}|i{i}|seed{MASTER_SEED}"
    return int(v8().stable_bucket(key, salt=salt, modulus=2 ** 63 - 1))


def pair_seeds(i: int, suffix: str = "") -> dict[str, int]:
    return {"author": seed_for("author", i, SALT_AUTHOR + suffix),
            "frameA": seed_for("frameA", i, SALT_FRAME_A + suffix),
            "frameB": seed_for("frameB", i, SALT_FRAME_B + suffix)}


def _rowcos(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (np.einsum("id,id->i", a, b)
            / np.sqrt(np.einsum("id,id->i", a, a) * np.einsum("id,id->i", b, b)))


def measure_pair(i: int, suffix: str = "") -> dict[str, Any]:
    """R1's Delta, unchanged: the per-author exact form against the centred trait."""
    m_ = k2b()
    w = m_.arm_weights(SHARE, W_INT_ARM)
    sd = pair_seeds(i, suffix)
    wa = r1().build_split_world_v2(sd["author"], sd["frameA"], PHI, W_FRESH)
    wb = r1().build_split_world_v2(sd["author"], sd["frameB"], PHI, W_FRESH)
    pa, pb = r1().card_parts(wa, w), r1().card_parts(wb, w)
    cab = _rowcos(pa["card"], pb["card"])
    cat = _rowcos(pa["card"], pa["trait_c"])
    cbt = _rowcos(pb["card"], pb["trait_c"])
    ai = np.einsum("id,id->i", pa["t"], pa["t"])
    bi = np.einsum("id,id->i", pa["s"], pa["s"])
    di = np.einsum("id,id->i", pa["n"], pa["n"])
    return {"pair": i, "w_style": W_FRESH,
            "author_seed": sd["author"], "frameA_seed": sd["frameA"],
            "frameB_seed": sd["frameB"],
            "Delta": float(np.mean(cab - cat * cbt)),
            "cos_AB": float(cab.mean()),
            "a_bar": float(ai.mean()), "b_bar": float(bi.mean()),
            "d_bar": float(di.mean()),
            "pred_ratio_of_means": float(bi.mean()
                                         / (ai.mean() + bi.mean() + di.mean())),
            "pred_mean_of_ratios": float(np.mean(bi / (ai + bi + di))),
            "sd_delta_i": float(np.std(bi / (ai + bi + di), ddof=1)),
            "n_authors": int(len(cab))}


def _predicate(v: np.ndarray) -> dict[str, Any]:
    fin = bool(np.all(np.isfinite(v)))
    sat = bool(np.any(np.abs(v) >= SATURATION_ABS))
    nz = bool(float(np.std(v, ddof=1)) > 0.0)
    return {"all_finite": fin, "any_saturated": sat, "nonzero_variance": nz,
            "min": float(v.min()), "max": float(v.max()),
            "PASS": bool(fin and (not sat) and nz)}


# ---------------------------------------------------------------------------
# PART 0 -- the corrected band, then the stamp.

def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    for nm in ("arm.csv", "prediction.json", "prediction.sha256.json"):
        if (OUT / nm).exists():
            raise SystemExit(f"STOP: {nm} exists before Part 0.")
    _log("part0_start")

    # --- G0: the instrument is UNCHANGED -----------------------------------
    fnv2 = r1().build_split_world_v2
    r1_file_sha = hashlib.sha256(R1SRC.read_bytes()).hexdigest()
    r1_fn_sha = hashlib.sha256(inspect.getsource(fnv2).encode("utf-8")).hexdigest()
    r1p0 = read_json(R1RES / "part0.json")
    r1dec = read_json(R1RES / "decision.json")
    r1fit = read_json(R1RES / "fit.json")
    g0 = {
        "instrument_from": rel(R1SRC),
        "builder": "build_split_world_v2",
        "definition_line": int(inspect.getsourcelines(fnv2)[1]),
        "r1_function_sha256": r1_fn_sha, "r1_file_sha256": r1_file_sha,
        "p3b_chain": r1p0["G0"]["instrument"],
        "p3b_sha_matches": bool(r1p0["G0"]["instrument"]["sha_matches"]),
        "w_mu": r1p0["G0"]["w_mu"]["persisted"],
        "w_mu_bit_exact": r1p0["G0"]["w_mu"]["bit_exact"],
        "injection_site": r1p0["G0"]["injection_site"]["file_line"],
        "r1_verdict": r1dec["verdict_slug"],
        "r1_certificates": r1dec["certificates"],
        "r1_clause_i_stands": r1fit["C_R1c"]["(i) null at w=0"]["PASS"],
        "r1_doses": {str(q["w_style"]): {"Delta": q["Delta_mean"],
                                         "ci95": q["Delta_ci95"],
                                         "sem": q["Delta_sem"],
                                         "predicted": q["predicted"]}
                     for q in r1fit["C_R1c"]["per_w"]},
    }
    g0["PASS"] = bool(g0["p3b_sha_matches"] and g0["w_mu_bit_exact"]
                      and g0["r1_certificates"]["C-R1a"]
                      and g0["r1_certificates"]["C-R1b"]
                      and g0["r1_clause_i_stands"])

    # --- the corrected band, from PROBE worlds only (RN-R1B-2) -------------
    probes = [measure_pair(i, "-probe") for i in range(PROBE_PAIRS)]
    n_probe_worlds = 2 * len(probes)
    pr = np.array([q["pred_ratio_of_means"] for q in probes], float)
    pa_ = np.array([q["pred_mean_of_ratios"] for q in probes], float)
    dl = np.array([q["Delta"] for q in probes], float)
    sd_i = np.array([q["sd_delta_i"] for q in probes], float)
    n_auth = int(probes[0]["n_authors"])

    prediction = float(pr.mean())
    se_pred = float(np.std(pr, ddof=1) / np.sqrt(len(pr)))
    se_approx = float(np.mean(sd_i / math.sqrt(n_auth)))
    se_meas = float(np.std(dl, ddof=1) / math.sqrt(N_PAIRS))
    half = float(2.0 * math.sqrt(se_pred ** 2 + se_meas ** 2 + se_approx ** 2))
    band = {
        "w_style": W_FRESH,
        "prediction_form": "ratio of means, b/(a+b+d) -- R1's form, unchanged "
                           "(RN-R1B-3)",
        "prediction": prediction,
        "diagnostic_prediction_mean_of_ratios": float(pa_.mean()),
        "diagnostic_form_gap": float(pa_.mean() - prediction),
        "SE_pred": se_pred, "SE_approx": se_approx, "SE_meas": se_meas,
        "SE_pred_source": "spread of the algebraic prediction across probe worlds / "
                          "sqrt(n_probes)",
        "SE_approx_source": "mean over probes of sd_i(b_i/(a_i+b_i+d_i)) / "
                            "sqrt(n_authors) -- the registration's prescription",
        "SE_meas_source": f"per-pair Delta spread across probe pairs / sqrt({N_PAIRS})",
        "combined_SE": float(math.sqrt(se_pred ** 2 + se_meas ** 2
                                       + se_approx ** 2)),
        "half_width": half,
        "band": [prediction - half, prediction + half],
        "convention": "#61: 2*sqrt(SE_pred^2 + SE_meas^2 + SE_approx^2)",
        "n_probe_pairs": len(probes), "n_probe_worlds": n_probe_worlds,
        "n_authors": n_auth,
        "dominant_term": max((("SE_pred", se_pred), ("SE_meas", se_meas),
                              ("SE_approx", se_approx)), key=lambda x: x[1])[0],
        "note": RN_NOTES["RN-R1B-2"],
    }
    # retro-check: would this band have contained R1's doses?  (reported only)
    retro = {}
    for wv, d in g0["r1_doses"].items():
        if float(wv) == 0.0:
            continue
        gap = float(d["Delta"] - d["predicted"])
        retro[wv] = {"R1_measured": d["Delta"], "R1_predicted": d["predicted"],
                     "gap": gap, "corrected_half_width_here": half,
                     "would_be_inside_if_band_were_this_wide": bool(abs(gap) <= half),
                     "label": "POST-HOC consistency reading; adjudicates nothing "
                              "(RN-R1B-1)"}
    write_json(OUT / "prediction.json", {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "salts": {"author": SALT_AUTHOR, "frameA": SALT_FRAME_A,
                  "frameB": SALT_FRAME_B, "pilot": SALT_PILOT},
        "master_seed": MASTER_SEED, "share": SHARE, "phi": PHI,
        "band": band, "probe_rows": probes})
    raw = (OUT / "prediction.json").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    stamp = {"sha256": digest, "bytes": len(raw),
             "stamp_utc": datetime.now(UTC).isoformat(),
             "arm_artifact_exists_at_stamp": bool((OUT / "arm.csv").exists()),
             "probe_worlds_generated_before_stamp": n_probe_worlds,
             "fresh_arm_worlds_generated_before_stamp": 0,
             "note": RN_NOTES["RN-R1B-4"]}
    write_json(OUT / "prediction.sha256.json", stamp)

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md (M4-R1b, BEFORE "
                        "run, commit dec5557)",
        "master_seed": MASTER_SEED, "rn_notes": RN_NOTES, "G0": g0,
        "band": band, "stamp": stamp, "secondary_retro": retro,
        "design": {"share": SHARE, "phi": PHI, "w_fresh": W_FRESH,
                   "pairs": N_PAIRS, "worlds": 2 * N_PAIRS,
                   "probe_pairs": PROBE_PAIRS},
        "sides_rule22": {
            "V-R1b": {"clause": "measured Delta(0.75) inside the corrected band",
                      "prior": 0.70, "sided": "two-sided containment"},
            "G3r1b": {"clause": f"power >= {POWER_MIN} at the algebraic truth and "
                                f"false-fire <= {FALSE_FIRE_MAX} at prediction - "
                                f"{DISPLACE}*band", "sided": "one-sided each"}},
        "stage_estimates_seconds": {"part0": 120, "pilot": 30, "project": 20,
                                    "arm": 120, "fit": 60, "finalize": 30},
        "environment": {"python": sys.version.split()[0],
                        "python_executable": sys.executable,
                        "platform": platform.platform(), "numpy": np.__version__,
                        "pandas": pd.__version__,
                        "scipy": __import__("scipy").__version__},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "part0.json", part0)
    _log("part0_done", PASS=g0["PASS"], sha256=digest, seconds=part0["seconds"])
    if not g0["PASS"]:
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "STOP", "routing_cell": "1",
            "routing_text": "STOP", "G0": g0,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: G0 failed")
    print(f"part0 OK  prediction={prediction!r}  half={half!r}  "
          f"(SE_pred {se_pred:.3e} / SE_meas {se_meas:.3e} / SE_approx "
          f"{se_approx:.3e}; dominant {band['dominant_term']})  "
          f"STAMPED {digest[:16]}...  arm worlds before stamp=0  "
          f"{time.time() - t0:.1f}s")
    _ = args


def _permit() -> dict[str, Any]:
    """K2f pattern: re-read the stamp from disk and re-hash to a match."""
    stamp = read_json(OUT / "prediction.sha256.json")
    raw = (OUT / "prediction.json").read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != stamp["sha256"]:
        raise SystemExit(f"REFUSED: prediction.json re-hash {got} != stamp "
                         f"{stamp['sha256']}")
    return {"permit_utc": datetime.now(UTC).isoformat(),
            "sha256_recomputed": got, "stamp_utc": stamp["stamp_utc"],
            "seconds_stamp_to_permit": (
                datetime.now(UTC)
                - datetime.fromisoformat(stamp["stamp_utc"])).total_seconds()}


# ---------------------------------------------------------------------------

def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    if not read_json(OUT / "part0.json")["G0"]["PASS"]:
        raise SystemExit("STOP: G0 did not pass.")
    permit = _permit()                       # the pilot runs AFTER the stamp
    rows = [measure_pair(i, "-pilot") for i in range(PILOT_PAIRS)]
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "pilot_field.csv", index=False)
    chk = _predicate(df["Delta"].to_numpy(float))
    out = {"utc": datetime.now(UTC).isoformat(), "permit": permit,
           "n_pilot_pairs": len(rows), "Delta_mean": float(df["Delta"].mean()),
           "regime": chk, "PASS": chk["PASS"], "seconds": time.time() - t0}
    write_json(OUT / "pilot.json", out)
    _log("pilot_done", PASS=chk["PASS"], seconds=out["seconds"])
    if not chk["PASS"]:
        raise SystemExit("STOP: pilot predicate failed")
    print(f"pilot OK  Delta={out['Delta_mean']!r}  permit "
          f"{permit['seconds_stamp_to_permit']:.3f}s after the stamp  "
          f"{time.time() - t0:.1f}s")
    _ = args


def stage_project(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    b = p0["band"]
    half, pred = b["half_width"], b["prediction"]
    se_pair = float(b["SE_meas"] * math.sqrt(N_PAIRS))    # per-pair sd, recovered

    def project(n: int) -> dict[str, Any]:
        se = float(se_pair / math.sqrt(n))
        rg = np.random.default_rng(MASTER_SEED)
        out = {}
        for name, truth, role in (
                ("algebraic truth", pred, "power"),
                (f"displaced: prediction - {DISPLACE}*band", pred - DISPLACE * half,
                 "false-fire")):
            draws = rg.normal(truth, se, size=B_PROJ)
            contained = float(np.mean(np.abs(draws - pred) <= half))
            out[name] = {"truth": truth, "SE_mean": se, "role": role,
                         "P_contained": contained,
                         "bar": POWER_MIN if role == "power" else FALSE_FIRE_MAX,
                         "PASS": (bool(contained >= POWER_MIN) if role == "power"
                                  else bool(contained <= FALSE_FIRE_MAX))}
        return {"pairs": n, "SE_mean_Delta": se, "half_width": half,
                "per_truth": out, "PASS": bool(all(d["PASS"] for d in out.values()))}

    base = project(N_PAIRS)
    esc = None
    decided = N_PAIRS
    if not base["PASS"]:
        print(f"  G3r1b FAILED at n={N_PAIRS}; escalation to {N_PAIRS_ESCALATED}",
              flush=True)
        esc = project(N_PAIRS_ESCALATED)
        if esc["PASS"]:
            decided = N_PAIRS_ESCALATED
    g3 = {"base": base, "escalated": esc, "escalation_fired": bool(esc is not None),
          "pairs_decided": decided, "B_proj": B_PROJ,
          "PASS": bool(base["PASS"] or (esc is not None and esc["PASS"])),
          "seconds": time.time() - t0}
    write_json(OUT / "projection.json", g3)
    _log("project_done", PASS=g3["PASS"], seconds=g3["seconds"])
    if not g3["PASS"]:
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "NON_PROJECTABLE", "routing_cell": "2",
            "routing_text": "NON_PROJECTABLE", "G3r1b": g3,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: NON_PROJECTABLE")
    print("project OK  " + "  ".join(
        f"{k}: P(contained)={d['P_contained']!r}" for k, d in base["per_truth"].items())
        + f"  n={decided}  {time.time() - t0:.1f}s")
    _ = args


def stage_arm(args: argparse.Namespace) -> None:
    t0 = time.time()
    g3 = read_json(OUT / "projection.json")
    if not g3["PASS"]:
        raise SystemExit("STOP: the projection did not pass.")
    permit = _permit()
    n = int(g3["pairs_decided"])
    path = OUT / "arm.csv"
    if path.exists() and len(read_csv_rt(path)) == n:
        print("  arm: already complete, skipped", flush=True)
    else:
        pd.DataFrame([measure_pair(i, "") for i in range(n)]).to_csv(path, index=False)
    write_json(OUT / "arm_permit.json", permit)
    _log("arm_done", seconds=time.time() - t0)
    print(f"arm OK  n={n}  {time.time() - t0:.1f}s")
    _ = args


def stage_fit(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    g3 = read_json(OUT / "projection.json")
    b = p0["band"]
    n = int(g3["pairs_decided"])
    d = read_csv_rt(OUT / "arm.csv").sort_values("pair")
    if len(d) != n:
        raise SystemExit(f"REFUSED: arm has {len(d)}, want {n}")
    v = d["Delta"].to_numpy(float)
    chk = _predicate(v)
    if not chk["PASS"]:
        raise SystemExit("REFUSED: rule-29 predicate fails on the arm")
    rng = np.random.default_rng(MASTER_SEED)
    bs = v[rng.integers(0, n, size=(B_BOOT, n))].mean(axis=1)
    mean = float(v.mean())
    ci = [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))]
    half, pred = b["half_width"], b["prediction"]
    inside = bool(abs(mean - pred) <= half)
    v_r1b = {
        "measured": mean, "ci95": ci,
        "sem": float(np.std(v, ddof=1) / np.sqrt(n)),
        "prediction": pred, "band": b["band"], "half_width": half,
        "signed_error": float(mean - pred),
        "position_in_band": float((mean - pred) / half),
        "inside": inside,
        "distance_outside": 0.0 if inside else float(abs(mean - pred) - half),
        "realized_pred_ratio_of_means": float(d["pred_ratio_of_means"].mean()),
        "realized_pred_mean_of_ratios": float(d["pred_mean_of_ratios"].mean()),
        "measured_minus_mean_of_ratios": float(
            mean - d["pred_mean_of_ratios"].mean()),
    }
    # A-3: added AFTER the verdict existed; REPORTING ONLY.  Neither the band nor
    # the prediction nor the routing is touched -- prediction.json is unchanged and
    # still re-hashes to the stamp.  Two questions a reader must be able to check:
    # (a) does the residual actually need SE_approx, or would R1's band form have
    # sufficed?  (b) was the pre-pinned choice of prediction form (RN-R1B-3) the
    # one that happened to help?
    mor = float(d["pred_mean_of_ratios"].mean())
    rom = float(d["pred_ratio_of_means"].mean())
    r1_style_half = float(2.0 * math.sqrt(b["SE_pred"] ** 2 + b["SE_meas"] ** 2))
    v_r1b["diagnostics"] = {
        "residual_over_SE_approx": float(v_r1b["signed_error"] / b["SE_approx"]),
        "residual_over_SEM_of_measurement": float(v_r1b["signed_error"]
                                                  / v_r1b["sem"]),
        "r1_style_half_width_no_SE_approx": r1_style_half,
        "would_pass_under_r1_style_band": bool(
            abs(v_r1b["signed_error"]) <= r1_style_half),
        "position_under_r1_style_band": float(v_r1b["signed_error"]
                                              / r1_style_half),
        "alt_form_residual_vs_arm_mean_of_ratios": float(mean - mor),
        "alt_form_position": float((mean - mor) / half),
        "alt_form_would_pass": bool(abs(mean - mor) <= half),
        "residual_vs_arm_ratio_of_means": float(mean - rom),
        "note": "computed after the verdict; reporting only, routes nothing (A-3)",
    }
    secondary = {k: dict(vv) for k, vv in p0["secondary_retro"].items()}
    for wv, rec in secondary.items():
        rec["note"] = ("re-scored against THIS leg's corrected half-width; "
                       "POST-HOC, adjudicates nothing (RN-R1B-1)")
    out = {"utc": datetime.now(UTC).isoformat(), "pairs": n, "V_R1b": v_r1b,
           "secondary_post_hoc": secondary, "B": B_BOOT,
           "regime": chk, "seconds": time.time() - t0}
    write_json(OUT / "fit.json", out)
    _log("fit_done", inside=inside, seconds=out["seconds"])
    print(f"fit OK  Delta(0.75)={mean!r} {ci}  pred={pred!r}  band={b['band']!r}  "
          f"position={v_r1b['position_in_band']:+.4f}  INSIDE={inside}  "
          f"{time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------

TRUTH_TABLE = [
    {"n": "1", "condition": "G0 / hash mismatch", "outcome": "STOP", "text": "STOP"},
    {"n": "2", "condition": "projection fails after escalation",
     "outcome": "NON_PROJECTABLE", "text": "NON_PROJECTABLE"},
    {"n": "3", "condition": "V-R1b inside the corrected band",
     "outcome": "IDENTITY_CHANNEL_CERTIFIED",
     "text": "IDENTITY_CHANNEL_CERTIFIED -- C-R1c closes; with C-R1a/b standing the "
             "instrument is certified and R2 becomes registrable"},
    {"n": "4", "condition": "V-R1b outside", "outcome": "BAND_STILL_WRONG",
     "text": "BAND_STILL_WRONG -- the derivation error model is inadequate; handback "
             "with the realized decomposition"},
]


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    g3 = read_json(OUT / "projection.json")
    fit = read_json(OUT / "fit.json")
    slug = ("IDENTITY_CHANNEL_CERTIFIED" if fit["V_R1b"]["inside"]
            else "BAND_STILL_WRONG")
    cell_n = "3" if fit["V_R1b"]["inside"] else "4"
    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "verdict_slug": slug, "routing_cell": cell_n, "modifiers": [],
        "routing_text": next(t["text"] for t in TRUTH_TABLE if t["outcome"] == slug),
        "V_R1b": fit["V_R1b"], "band": p0["band"], "stamp": p0["stamp"],
        "permit": read_json(OUT / "arm_permit.json"),
        "secondary_post_hoc": fit["secondary_post_hoc"],
        "G0": p0["G0"], "projection": g3, "pairs": fit["pairs"],
        "total_worlds": int(2 * fit["pairs"]),
        "r1_certificates_standing": p0["G0"]["r1_certificates"],
        "gates": {
            "G0": {"PASS": p0["G0"]["PASS"],
                   "detail": "instrument unchanged: R1 builder hashes recorded, the "
                             "P3b chain verified, w_mu bit-exact, R1's C-R1a/C-R1b and "
                             "clause (i) standing"},
            "G2r1b": {"PASS": pil["PASS"],
                      "detail": "rule-29 predicate; pilot AFTER the stamp"},
            "G3r1b": {"PASS": g3["PASS"],
                      "detail": f"escalation fired: {g3['escalation_fired']}"},
            "V-R1b": {"PASS": fit["V_R1b"]["inside"],
                      "detail": "prospective containment at the fresh dose w = 0.75"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug, seconds=dec["seconds"])
    _tables(p0, pil, g3, fit, dec)
    _facts(p0, pil, g3, fit, dec)
    print(f"finalize OK  slug={slug}  cell={cell_n}")
    _ = args


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
    g0 = p0["G0"]
    sec["instrument"] = _md(
        ["property", "value"],
        [["builder", "`" + g0["instrument_from"] + ":"
          + str(g0["definition_line"]) + "` (`" + g0["builder"] + "`)"],
         ["R1 function sha256", g0["r1_function_sha256"]],
         ["R1 file sha256", g0["r1_file_sha256"]],
         ["P3b chain hashes match", str(g0["p3b_sha_matches"])],
         ["w_mu", repr(g0["w_mu"]) + " (bit-exact: " + str(g0["w_mu_bit_exact"]) + ")"],
         ["injection site", "`" + g0["injection_site"] + "`"],
         ["R1 verdict", g0["r1_verdict"]],
         ["R1 certificates standing", repr(g0["r1_certificates"])],
         ["R1 clause (i) stands (the w = 0 equivalence)",
          str(g0["r1_clause_i_stands"])]])
    b = p0["band"]
    sec["band"] = _md(
        ["term", "value", "source"],
        [["prediction (ratio of means)", repr(b["prediction"]),
          b["prediction_form"]],
         ["SE_pred", repr(b["SE_pred"]), b["SE_pred_source"]],
         ["SE_meas", repr(b["SE_meas"]), b["SE_meas_source"]],
         ["SE_approx", repr(b["SE_approx"]), b["SE_approx_source"]],
         ["combined SE", repr(b["combined_SE"]), "sqrt of the sum of squares"],
         ["**half-width**", "**" + repr(b["half_width"]) + "**", b["convention"]],
         ["**band**", "**" + repr(b["band"]) + "**", "prediction +/- half-width"],
         ["dominant term", b["dominant_term"], "—"],
         ["diagnostic: mean-of-ratios prediction",
          repr(b["diagnostic_prediction_mean_of_ratios"]),
          "reported, NOT used -- the form is unchanged (RN-R1B-3)"],
         ["diagnostic: form gap", repr(b["diagnostic_form_gap"]),
          "the Jensen/orthogonality gap SE_approx must cover"],
         ["probe pairs / worlds / authors",
          f"{b['n_probe_pairs']} / {b['n_probe_worlds']} / {b['n_authors']}",
          "all pre-measurement (RN-R1B-2)"]])
    st, pm = p0["stamp"], dec["permit"]
    sec["ordering"] = _md(
        ["quantity", "value"],
        [["prediction.json sha256", st["sha256"]],
         ["bytes", str(st["bytes"])],
         ["stamp UTC", st["stamp_utc"]],
         ["**fresh-arm worlds generated before the stamp**",
          "**" + str(st["fresh_arm_worlds_generated_before_stamp"]) + "**"],
         ["probe worlds before the stamp (by design)",
          str(st["probe_worlds_generated_before_stamp"])],
         ["arm artifact existed at stamp time",
          str(st["arm_artifact_exists_at_stamp"])],
         ["permit UTC", pm["permit_utc"]],
         ["seconds stamp -> permit", repr(pm["seconds_stamp_to_permit"])],
         ["permit re-hash matches the stamp",
          str(pm["sha256_recomputed"] == st["sha256"])]])
    rows = []
    for label, blk in (("128 (registered)", g3["base"]),
                       ("256 (escalated)", g3["escalated"])):
        if blk is None:
            continue
        for k, d in blk["per_truth"].items():
            rows.append([label, k, d["role"], repr(d["truth"]), repr(d["SE_mean"]),
                         repr(d["P_contained"]), repr(d["bar"]), str(d["PASS"])])
    sec["projection"] = _md(
        ["pairs", "truth", "role", "truth value", "SE(mean)", "P(contained)", "bar",
         "PASS"], rows)
    v = fit["V_R1b"]
    sec["verdict"] = _md(
        ["quantity", "value"],
        [["**measured Delta(0.75)**", "**" + repr(v["measured"]) + "**"],
         ["95% CI", repr(v["ci95"])], ["SEM", repr(v["sem"])],
         ["prediction", repr(v["prediction"])],
         ["band", repr(v["band"])],
         ["half-width", repr(v["half_width"])],
         ["signed error", repr(v["signed_error"])],
         ["**position in band**", "**" + repr(v["position_in_band"]) + "**"],
         ["**INSIDE**", "**" + str(v["inside"]) + "**"],
         ["distance outside", repr(v["distance_outside"])],
         ["realized ratio-of-means on the arm",
          repr(v["realized_pred_ratio_of_means"])],
         ["realized mean-of-ratios on the arm",
          repr(v["realized_pred_mean_of_ratios"])],
         ["measured - mean-of-ratios", repr(v["measured_minus_mean_of_ratios"])]])
    dg = v["diagnostics"]
    sec["diagnostics"] = _md(
        ["question", "quantity", "value"],
        [["is SE_approx load-bearing?", "residual / SE_approx",
          repr(dg["residual_over_SE_approx"])],
         ["", "residual / SEM of the measurement",
          repr(dg["residual_over_SEM_of_measurement"])],
         ["", "R1-style half-width, 2*sqrt(SE_pred^2 + SE_meas^2)",
          repr(dg["r1_style_half_width_no_SE_approx"])],
         ["", "**would this leg PASS under R1's band form?**",
          "**" + str(dg["would_pass_under_r1_style_band"]) + "**"],
         ["", "position under R1's band form",
          repr(dg["position_under_r1_style_band"])],
         ["did the pinned form choice help?", "realized ratio-of-means on the arm",
          repr(v["realized_pred_ratio_of_means"])],
         ["", "realized mean-of-ratios on the arm",
          repr(v["realized_pred_mean_of_ratios"])],
         ["", "residual vs the arm's ratio-of-means",
          repr(dg["residual_vs_arm_ratio_of_means"])],
         ["", "residual vs the arm's mean-of-ratios",
          repr(dg["alt_form_residual_vs_arm_mean_of_ratios"])],
         ["", "position had the mean-of-ratios form been stamped",
          repr(dg["alt_form_position"])],
         ["", "would the alternative form still PASS?",
          str(dg["alt_form_would_pass"])]])
    sec["secondary"] = _md(
        ["R1 dose", "R1 measured", "R1 predicted", "gap",
         "this leg's half-width", "would be inside", "label"],
        [[k, repr(x["R1_measured"]), repr(x["R1_predicted"]), repr(x["gap"]),
          repr(x["corrected_half_width_here"]),
          str(x["would_be_inside_if_band_were_this_wide"]), x["note"]]
         for k, x in fit["secondary_post_hoc"].items()])
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
    sec["timing"] = _md(
        ["stage", "estimate (s)", "measured (s)"],
        [["part0 (band + stamp)", str(est["part0"]),
          "%.3f" % meas.get("part0_done", float("nan"))],
         ["pilot", str(est["pilot"]), "%.3f" % meas.get("pilot_done", float("nan"))],
         ["project", str(est["project"]),
          "%.3f" % meas.get("project_done", float("nan"))],
         ["arm", str(est["arm"]), "%.3f" % meas.get("arm_done", float("nan"))],
         ["fit", str(est["fit"]), "%.3f" % meas.get("fit_done", float("nan"))],
         ["finalize", str(est["finalize"]),
          "%.3f" % meas.get("finalize_done", float("nan"))]])
    body = ["# M4-R1b report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _facts(p0: dict[str, Any], pil: dict[str, Any], g3: dict[str, Any],
           fit: dict[str, Any], dec: dict[str, Any]) -> None:
    b, v, st = p0["band"], fit["V_R1b"], p0["stamp"]
    pm = dec["permit"]
    f = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"], "PAIRS": fit["pairs"],
        "WORLDS": dec["total_worlds"], "W": W_FRESH,
        "PRED": b["prediction"], "SEP": b["SE_pred"], "SEM": b["SE_meas"],
        "SEA": b["SE_approx"], "COMB": b["combined_SE"], "HALF": b["half_width"],
        "BAND": b["band"], "DOM": b["dominant_term"],
        "PMOR": b["diagnostic_prediction_mean_of_ratios"],
        "FORMGAP": b["diagnostic_form_gap"],
        "NPROBE": b["n_probe_pairs"], "NPW": b["n_probe_worlds"],
        "MEAS": v["measured"], "CI": v["ci95"], "SEMV": v["sem"],
        "ERR": v["signed_error"], "POS": v["position_in_band"],
        "INSIDE": v["inside"],
        "MMOR": v["measured_minus_mean_of_ratios"],
        "RSA": v["diagnostics"]["residual_over_SE_approx"],
        "RSM": v["diagnostics"]["residual_over_SEM_of_measurement"],
        "R1HALF": v["diagnostics"]["r1_style_half_width_no_SE_approx"],
        "R1PASS": v["diagnostics"]["would_pass_under_r1_style_band"],
        "R1POS": v["diagnostics"]["position_under_r1_style_band"],
        "ALTPOS": v["diagnostics"]["alt_form_position"],
        "ALTPASS": v["diagnostics"]["alt_form_would_pass"],
        "ROMARM": v["realized_pred_ratio_of_means"],
        "MORARM": v["realized_pred_mean_of_ratios"],
        "SHA": st["sha256"], "SHA16": st["sha256"][:16],
        "STAMP": st["stamp_utc"], "PERMIT": pm["permit_utc"],
        "GAP_S2P": pm["seconds_stamp_to_permit"],
        "ARMW0": st["fresh_arm_worlds_generated_before_stamp"],
        "PW_ALG": g3["base"]["per_truth"]["algebraic truth"]["P_contained"],
        "FF_DIS": [d["P_contained"] for k, d in g3["base"]["per_truth"].items()
                   if d["role"] == "false-fire"][0],
        "ESC": g3["escalation_fired"],
        "R1CERT": repr(p0["G0"]["r1_certificates"]),
        "SITE": p0["G0"]["injection_site"], "WMU": p0["G0"]["w_mu"],
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
    }
    for k, x in fit["secondary_post_hoc"].items():
        t = k.replace(".", "")
        f[f"S{t}_GAP"] = x["gap"]
        f[f"S{t}_IN"] = x["would_be_inside_if_band_were_this_wide"]
    write_json(OUT / "prose_facts.json", f)


REPORT_TEMPLATE = r"""# SUICA M4-R1b — clause (iv), re-banded — **{{SLUG}}**

**Outcome: {{SLUG}} (routing cell {{CELL}}).** {{ROUTING_TEXT}}

**Measured Δ(w = {{W}}) = {{MEAS}}** {{CI}} against a prediction of {{PRED}} and
a corrected band of {{BAND}} — position **{{POS}}** of the half-width, INSIDE:
**{{INSIDE}}**. {{WORLDS}} fresh worlds ({{PAIRS}} A/B pairs).

The instrument is UNCHANGED. Tier EXPLORATORY, label-free, synthetic. Registered
in `docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md` BEFORE run (commit dec5557).
Every number below is generated from artifacts by code (rule 24).

---

## 1. Why a fresh dose

R1's Δ at w = 0.5 and 1.0 are published, so a re-banded test on those doses
cannot be prospective however honestly it is run — the person deriving the band
can already see the answers. **w = 0.75 has never been measured.** Its
prediction and band were derived from probe worlds, hashed, and stamped before
any fresh-arm world existed (RN-R1B-1/4). R1's doses are re-scored afterwards
under the post-hoc label and route nothing.

<<TABLE:instrument>>

## 2. The corrected band, per defect #61

<<TABLE:band>>

All three terms come from **probe worlds** — none from the pilot, which runs
after the stamp (RN-R1B-2). The dominant term is **{{DOM}}**: SE_pred {{SEP}},
SE_meas {{SEM}}, SE_approx {{SEA}}, combining to {{COMB}} and a half-width of
**{{HALF}}**.

**The prediction's form is deliberately unchanged** (RN-R1B-3). R1's algebraic
prediction is the ratio-of-means b/(a+b+d), and #61 fixes the *band*, not the
predictor — so keeping the form makes this a test of the convention rather than
of a quietly improved predictor. The per-author form is reported as a
diagnostic: {{PMOR}}, a gap of {{FORMGAP}} from the prediction, which is exactly
the Jensen/orthogonality error SE_approx exists to cover.

## 3. Ordering

<<TABLE:ordering>>

The band was stamped with **{{ARMW0}} fresh-arm worlds in existence**, and the
arm refused to run until it re-read the stamp from disk and re-hashed
`prediction.json` to a match ({{GAP_S2P}} s later). Probe worlds necessarily
precede the stamp — they are the band's inputs — and are counted separately.

## 4. The projection

<<TABLE:projection>>

At the corrected band's width: containment holds with probability {{PW_ALG}} at
the algebraic truth (bar 0.8) and only {{FF_DIS}} at a truth displaced three
band-widths below it (bar 0.1). The band is simultaneously wide enough to accept
the truth and tight enough to reject a displaced one — which is what a
containment test has to be. Escalation did not fire ({{ESC}}).

## 5. The verdict

<<TABLE:verdict>>

Measured **{{MEAS}}** {{CI}} against prediction {{PRED}}: signed error {{ERR}},
**{{POS}}** of the half-width. **INSIDE = {{INSIDE}}.**

### 5.1 Is the correction load-bearing, and did the pinned form choice help?

<<TABLE:diagnostics>>

Two things a reader is owed, and neither is flattering by construction.

**SE_approx is load-bearing.** The residual is {{RSA}} of SE_approx — but
{{RSM}} of the measurement's own SEM. The measurement is far more precise than
the prediction is accurate, which is the entire content of defect #61. Under
R1's band form — 2·√(SE_pred² + SE_meas²), half-width {{R1HALF}} — this leg
would have landed at {{R1POS}} and **PASSED = {{R1PASS}}**. The identical
failure would have recurred at a fresh dose. The correction is not cosmetic.

**The pre-pinned form choice was the favourable one, and I did not know that
when I pinned it.** RN-R1B-3 kept R1's ratio-of-means, and Part 0 named the
mean-of-ratios as "what the measurement actually estimates". It is not: the
measurement sits below *both* forms — {{ERR}} from the stamped ratio-of-means
and {{MMOR}} from the arm's mean-of-ratios ({{MORARM}}). Had the mean-of-ratios
been stamped instead, the position would have been {{ALTPOS}} — still inside
({{ALTPASS}}), but near the edge. So the containment verdict is robust to the
form choice, while the comfort of the margin is not. The residual is therefore
**not** the Jensen form gap; it runs the other way and is larger, and SE_approx
covers it because that spread sets the right *scale* for the derivation's error,
not because it names its mechanism.

## 6. Secondary — R1's doses re-scored (post-hoc, adjudicating nothing)

<<TABLE:secondary>>

Reported as consistency readings only. The registration is explicit that these
cannot adjudicate, and the routing uses w = 0.75 alone.

## 7. Routing

<<TABLE:truth_table>>

## 8. Gates

<<TABLE:gates>>

## 9. Sides declared (rule 22)

<<TABLE:sides>>

## 10. Pinned readings

<<TABLE:rn>>

## 11. Rule events

- **Rule 13:** no verdict sits near a boundary in the bootstrap tail sense; the
  containment call is at {{POS}} of the half-width.
- **Rule 25:** the projection gate passed at the registered size.
- **Rule 26:** no bounded winner.
- **Rule 29:** the domain-pinned predicate ran on the pilot and the arm.
- **Rule 30:** the band's three terms are all MEASURED on probe worlds and
  persisted before the arm; the instrument's hashes are verified at source.
- **Rule 31/32 family (#61):** the convention under test — a containment band
  carries 2·√(SE_pred² + SE_meas² + SE_approx²), and the deterministic w = 0
  point is tested by equivalence (R1's clause (i)), never containment.

## 12. What this settles

With C-R1a, C-R1b and R1's clauses (i)–(iii) standing, and clause (iv) now
tested prospectively at a dose never previously measured, **the identity channel
is certified**: planted, inert at zero, author-stream, trait-independent,
card-visible, monotone in dose, and quantitatively recoverable inside a band
derived before the measurement existed.

What it does **not** settle: nothing about the k2b family's own worlds. The
channel is planted, not discovered; appendix KK's structural boundary is
unmoved. This buys the ability to ask the founding question, not an answer to it.

## 13. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython {{PYTHON}} venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.
3. **A-3 (my own report prose was wrong; AFTER the verdict existed).** The
   report template — written before the run — asserted that the measurement
   would sit closer to the per-author mean-of-ratios, that being "what the
   measurement actually estimates" (Part 0's own words). The data contradict it:
   the measurement is {{MMOR}} from the mean-of-ratios and only {{ERR}} from the
   stamped ratio-of-means, so the pre-pinned form was the *closer* one. The
   sentence was replaced with §5.1's generated decomposition, which reports the
   contradiction and the counterfactual position under the alternative form.
   This was discovered and corrected AFTER the containment verdict existed. It
   changed no number: `prediction.json` is untouched and still re-hashes to the
   stamp {{SHA16}}, the band, the routing and the verdict are as computed. What
   changed is that a claim I could not support was removed.

## 14. Environment

<<TABLE:env>>

## 15. Timing

<<TABLE:timing>>

---

*Artifacts: `results/m4_r1b_reband/` (gitignored) — `part0.json`,
`prediction.json`, `prediction.sha256.json`, `pilot.json`, `pilot_field.csv`,
`projection.json`, `arm.csv`, `arm_permit.json`, `fit.json`, `decision.json`,
`prose_facts.json`, `report_tables.md`, `run_log.jsonl`. Harness:
`scripts/run_suica_m4_r1b_reband.py`.*
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
    path = ROOT / "reports" / "SUICA_M4_R1B_REBAND_REPORT.md"
    path.write_text(txt, encoding="utf-8")
    print(f"report OK  {rel(path)}  ({len(txt.splitlines())} lines)")
    _ = args


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="stage", required=True)
    for name, fn in [("part0", stage_part0), ("pilot", stage_pilot),
                     ("project", stage_project), ("arm", stage_arm),
                     ("fit", stage_fit), ("finalize", stage_finalize),
                     ("report", stage_report)]:
        sub.add_parser(name).set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
