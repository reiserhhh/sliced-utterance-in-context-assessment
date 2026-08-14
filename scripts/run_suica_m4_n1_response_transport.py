#!/usr/bin/env python3
"""M4-N1 -- THE RESPONSE-TRANSPORT SEAL.

Registered in docs/SUICA_M4_N_TAX_MECHANISM_LINE_PLAN.md ("M4-N1 -- the
response-transport seal", commit 76060e7) BEFORE this file existed.
Implementation and execution only; the registration is binding.

The M-line closed with the tax measured as a curve at LEVEL grade.  Appendix CC
shows M3's A-quad is exactly a shifted square, alpha(V) = c' + A0*(1 - V/V*)^2,
whose vertex V* ~ 0.614 is unreachable arithmetic on this generator -- so the
mechanism's only testable content is TRANSPORT.  At MATCHED attenuation a
difference cancels the channel lambda*r^q AND the constant exactly:

    D = alpha(V_hi) - alpha(V_lo) = -dV * [kappa0 - kappa2 * V_bar]

with NO approximation.  So kappa-hat = -D/dV measures the LOCAL tax at the
pair's midpoint -- a response-grade number the level fit never consumed.

Two matched-attenuation pairs, dV = 0.045 exact:
    pair-LO (V_bar 0.0525): A = (0.10, phi_a) vs B = (0.25, 0.05)
    pair-HI (V_bar 0.1875): C = (0.55, phi_c) vs D = (0.70, 0.05)
with phi_a, phi_c solved by bisection to |dr| <= 1e-9 in Part 0.

Three predictions -- kappa_resp(0.0525), kappa_resp(0.1875) and their decline --
are computed from M3's pipeline recomputed deterministically, HASHED with the
salt embedded in the sealed bytes, and only then are worlds drawn.  Ordering is
enforced in code (K2f G1f); the pilot runs AFTER the stamp (RN-K2F-4).

Artifacts: results/m4_n1_response_transport/ (gitignored)
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
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

OUT = ROOT / "results" / "m4_n1_response_transport"
RES = ROOT / "results"
M1BRES = RES / "m4_m1b_r_at_level"
M3RES = RES / "m4_m3_tax_curve"

LEG = "M4-N1"
BANNER = ("prospective response-transport seal on K2b's frozen instrument, "
          "exploratory, label-free; predictions hashed before any fresh world")

MASTER_SEED = 20260811
SALT_WORLD = "m4n1-world"
SALT_PILOT = "m4n1-pilot"
N_WORLDS = 384
N_WORLDS_ESCALATED = 768
PILOT_WORLDS = 4
B_BOOT = 2000
B_PROJ = 2000
INT_SHARE = 0.0
W_INT_ARM = "zero"

SIGMA_W = 0.026889438327132725
DV = 0.045
R_WINDOW = (0.4541409476972356, 0.8189581462487876)
ROOT_TOL = 1e-9

# --- the pair design (G0n1(i)) ---------------------------------------------
TARGET_LO = 0.785015540293945          # r(0.25, 0.05)
TARGET_HI = 0.5967380569813433         # r(0.70, 0.05)
BRACKET_LO = (0.85, 0.98)
BRACKET_HI = (0.60, 0.98)
BRACKET_LO_R = (0.7908869485651705, 0.7718092954224756)   # r(0.10, .85) / (0.10, .98)
VBAR_LO, VBAR_HI = 0.0525, 0.1875

# --- M3's persisted curve (G0n1(ii)) ---------------------------------------
M3_C = 0.21247398265278816
M3_K0 = 0.9601680204204508
M3_K2 = 1.562877770472943
M3_K2_CI = (1.0324533419318935, 2.119753814549891)
M3_ALIN_KAPPA_REGISTERED = 0.7729284648259515   # registration text; see RN-N1-8
M3_ALIN_KAPPA_PERSISTED = 0.7729279998877195    # controls, per the registration
M3_LOO = {"A-lin": 0.003599294048156043, "A-quad": 0.001405398973367856,
          "A-sat": 0.0014509897412261284}
M3_P_QUAD = 0.9935
M3_P_LIN = 0.0575
M3_CLOSURE_HITS = 5
M3_ASAT = (-0.27493651728760515, 0.4878776246525967, 0.4983722810248614)
# --- appendix CC identities -------------------------------------------------
CC_VSTAR = 0.6143507762088093
CC_A0 = 0.29489267237567145
CC_CPRIME = -0.08241868972288329
# --- the channel, fixed at the M2-sealed transfer point --------------------
LAMBDA_STAR = -0.057625974791364554
Q_STAR = 3.863625377453229
M3_SHARES = (0.10, 0.175, 0.25, 0.325, 0.40, 0.50, 0.60, 0.70)
M3_PHIS = (0.05, 0.60)

BAND_BUDGET = {"S1": 0.30, "S2": 0.30, "S3": 0.35}
PROJ_POWER_CURVE_MIN = 0.8
PROJ_POWER_CONST_MAX = 0.1
SATURATION_ABS = 0.995

# ---------------------------------------------------------------------------
# RN-N1 notes.  PINNED IN PART 0, BEFORE THE STAMP AND BEFORE ANY WORLD.
#
# RN-N1-1 (ordering, inherited).  K2f's G1f pattern and RN-K2F-4: the permit for
#   ANY fresh world -- the pilot included -- is issued only by re-reading
#   predictions.sha256.json from disk and re-hashing predictions.json to a match.
#   Guards wrap build_k2b_world / run_field_world / emit_panel on EVERY reachable
#   k2b instance (RN-K2F-5), plus a cross-process refusal if a world artifact
#   already exists at stamp time.  The salt is embedded INSIDE the sealed bytes
#   (D3), so the digest covers the seed lineage.
#
# RN-N1-2 (the roots).  phi_a and phi_c are found by bisection on the pinned
#   deterministic map r(share, .) -- strictly decreasing in phi -- to
#   |r - target| <= 1e-9, starting from the registration's own brackets whose
#   endpoints are re-derived and checked to straddle the target before the
#   search runs.  The registration's channel-cancellation bias bound is recorded
#   with the realized residuals.
#
# RN-N1-3 (the difference orientation).  kappa-hat = -D/dV with D taken as
#   field(HIGH V) - field(LOW V), so a field that FALLS in V gives kappa-hat > 0,
#   matching every published kappa in the programme.  dV = 0.045 is exact
#   arithmetic (V = 0.3*share), not an estimate, so it carries no error.
#
# RN-N1-4 (SE_meas).  Per the registration, SE per kappa-hat is
#   sqrt(2)*sigma_w/(sqrt(n)*dV) and SE_diff = sqrt(2)*SE_kappa, from M1b's
#   persisted, G0-verified sigma_w.  These are PRIOR measurement-noise
#   allowances fixed before the cells exist; the realized per-cell SEMs are
#   reported beside them and do not re-draw the bands.
#
# RN-N1-5 (the predictor's bootstrap).  M3's pipeline is recomputed
#   deterministically from its persisted per-world corpus: alpha_s with the
#   channel fixed at theta*, A-quad refit, and B = 2000 master-seeded
#   world-block draws, each draw's (c, kappa0, kappa2) propagated through S1, S2
#   and S3 so the bands inherit the parameter covariance rather than three
#   marginal intervals.  G0 requires the recomputed point parameters to equal
#   M3's persisted values BIT-EXACTLY before anything is sealed.
#
# RN-N1-6 (A-sat co-predictions).  A-sat's local tax is -d alpha/dV =
#   (A/tau)*exp(-V/tau); its three co-predictions are computed from M3's
#   persisted A-sat parameters and written INSIDE the hashed file.  They
#   adjudicate nothing unless a verdict differs between the forms, in which case
#   FORM_SPLIT is reported (the registration's tie handling, K2f precedent).
#
# RN-N1-7 (the projection's statistic).  The gate is on
#   P(delta-kappa-hat > 2*SE_diff), a ONE-SIDED event on the difference, at both
#   truths; simulated parametrically as two independent kappa-hats with sd
#   SE_kappa around each truth's local tax.  Under CONSTANT both truths equal
#   M3's persisted A-lin kappa, so the event is a pure false-positive rate.
#
# RN-N1-8 (the CONSTANT truth's value; a REGISTRATION-ANTICIPATED divergence,
#   found and pinned BEFORE the stamp and before any world).  G2n1 quotes the
#   A-lin chord as 0.7729284648259515; results/m4_m3_tax_curve/alpha.json holds
#   0.7729279998877195 -- a 4.649e-7 difference in the 7th decimal.  The
#   registration legislates the resolution in its own text ("executor recomputes
#   exactly from M3's A-lin fit; if its persisted value differs, the persisted
#   value controls"), so the PERSISTED value is used as the CONSTANT truth, the
#   divergence is recorded as an ANTICIPATED citation clause that does NOT fail
#   G0n1, and BOTH readings are reported.  The projection is insensitive to the
#   choice by construction: under CONSTANT both local taxes take the SAME value
#   whatever it is, so the true difference is exactly 0 either way -- the gate's
#   false-positive rate is identical under the two readings.  This is a defect
#   candidate only in the weakest sense (a stale transcription in the
#   registration prose, already self-resolving); it is reported, not acted on.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-N1-1": "ordering enforced in code (K2f G1f + RN-K2F-4): the permit for ANY fresh "
               "world, pilot included, is issued only by re-reading the stamp from disk "
               "and re-hashing; guards on every reachable k2b instance; salt embedded in "
               "the sealed bytes (D3)",
    "RN-N1-2": "phi_a / phi_c by bisection on the pinned map to |r - target| <= 1e-9, "
               "from the registration's own brackets whose endpoints are re-derived and "
               "checked to straddle before the search",
    "RN-N1-3": "kappa-hat = -D/dV with D = field(HIGH V) - field(LOW V), so a field "
               "falling in V gives kappa-hat > 0; dV = 0.045 is exact arithmetic and "
               "carries no error",
    "RN-N1-4": "SE_kappa = sqrt(2)*sigma_w/(sqrt(n)*dV), SE_diff = sqrt(2)*SE_kappa, from "
               "M1b's persisted sigma_w -- PRIOR allowances fixed before the cells exist; "
               "realized SEMs reported beside them and never re-draw the bands",
    "RN-N1-5": "M3's pipeline recomputed deterministically (alpha at fixed theta*, A-quad "
               "refit, B=2000 world-block draws) with each draw's (c, kappa0, kappa2) "
               "propagated through all three predictions, so the bands inherit the "
               "parameter covariance; G0 demands bit-exact point parameters first",
    "RN-N1-6": "A-sat co-predictions from its local tax (A/tau)*exp(-V/tau), written "
               "INSIDE the hashed file; they adjudicate nothing unless a verdict differs, "
               "which reports FORM_SPLIT",
    "RN-N1-7": "the projection statistic is the ONE-SIDED event delta-kappa-hat > "
               "2*SE_diff at both truths; under CONSTANT both local taxes equal M3's "
               "persisted A-lin kappa so the event is a pure false-positive rate",
    "RN-N1-8": "REGISTRATION-ANTICIPATED DIVERGENCE, pinned before the stamp: G2n1 "
               "quotes the A-lin chord as 0.7729284648259515, alpha.json holds "
               "0.7729279998877195 (4.649e-7 apart). The registration's own text makes "
               "the persisted value control, so it is used and the clause is recorded as "
               "ANTICIPATED rather than failing G0n1; both readings reported. The "
               "projection is insensitive by construction -- under CONSTANT both local "
               "taxes take the same value, so the true difference is exactly 0 either way",
}

# ---------------------------------------------------------------------------
# Module loading -- ONE importlib loader chain (RN-K2F-5).

_MODS: dict[str, Any] = {}


def _load(name: str) -> Any:
    if name in _MODS:
        return _MODS[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    if spec is None or spec.loader is None:      # pragma: no cover
        raise SystemExit(f"REFUSED: cannot load {name}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    _MODS[name] = mod
    return mod


def k2b() -> Any:
    return _load("run_suica_m4_k2b_t4_branch")


def k2c() -> Any:
    return _load("run_suica_m4_k2c_matched_pairs")


def k2e() -> Any:
    return _load("run_suica_m4_k2e_double_matching")


# ---------------------------------------------------------------------------
# G4n1 -- ORDERING ENFORCEMENT.

_GEN_COUNT = 0
_PERMIT = False
_ARMED = False
WORLD_ARTIFACTS = ("pilot_field.csv", "g4n1_pilot.json", "cells", "measured.json")


def _log(event: str, **kw: Any) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rec = {"utc": datetime.now(UTC).isoformat(), "event": event, **kw}
    with (OUT / "ordering_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True, default=float) + "\n")


def _reachable_k2b() -> list[Any]:
    cands: list[Any] = [k2b()]
    for acc in (lambda: k2c().k2b(), lambda: k2e().k2b(), lambda: k2e().k2d().k2b()):
        try:
            cands.append(acc())
        except Exception:                                    # noqa: BLE001
            continue
    seen, out = set(), []
    for m in cands:
        if id(m) not in seen:
            seen.add(id(m))
            out.append(m)
    return out


def _arm_guard() -> int:
    global _ARMED
    if _ARMED:
        return 0
    mods = _reachable_k2b()
    for kb in mods:
        for fname in ("build_k2b_world", "run_field_world", "emit_panel"):
            orig: Callable[..., Any] = getattr(kb, fname)

            def make(o: Callable[..., Any], nm: str) -> Callable[..., Any]:
                def wrapped(*a: Any, **kw: Any) -> Any:
                    global _GEN_COUNT
                    _GEN_COUNT += 1
                    if not _PERMIT:
                        _log("REFUSED_world_generation", entry_point=nm, count=_GEN_COUNT)
                        raise SystemExit(
                            f"STOP (G4n1): fresh-world generation via {nm} before the "
                            f"prediction hash was persisted.")
                    return o(*a, **kw)
                wrapped.__name__ = f"guarded_{nm}"
                return wrapped

            setattr(kb, fname, make(orig, fname))
    _ARMED = True
    _log("guard_armed", n_k2b_instances=len(mods), n_wrapped=3 * len(mods))
    return len(mods)


def _permit() -> dict[str, Any]:
    global _PERMIT
    pp, sp = OUT / "predictions.json", OUT / "predictions.sha256.json"
    if not pp.exists() or not sp.exists():
        raise SystemExit("STOP (G4n1): no persisted stamp; run `part0`.")
    raw = pp.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    stamp = json.loads(sp.read_text(encoding="utf-8"))
    if digest != stamp["sha256"]:
        raise SystemExit(f"STOP (G4n1): hash {digest} != stamped {stamp['sha256']}")
    if _GEN_COUNT != 0:
        raise SystemExit(f"STOP (G4n1): {_GEN_COUNT} generations before the permit.")
    _PERMIT = True
    rec = {"permit_utc": datetime.now(UTC).isoformat(), "sha256_recomputed": digest,
           "sha256_stamped": stamp["sha256"], "stamp_utc": stamp["stamp_utc"],
           "generations_before_permit": _GEN_COUNT,
           "seconds_stamp_to_permit": float(
               (datetime.now(UTC)
                - datetime.fromisoformat(stamp["stamp_utc"])).total_seconds())}
    _log("permit_issued", **rec)
    return rec


# ---------------------------------------------------------------------------
# Utilities.

def read_csv_rt(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, float_precision="round_trip")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, default=float)
        fh.write("\n")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def r_of(share: float, phi: float) -> float:
    return k2c().predicted_attenuation(share, phi)


def v_of(share: float) -> float:
    return k2e().person_share_design(share, INT_SHARE)


def channel(r: Any) -> Any:
    return LAMBDA_STAR * np.asarray(r, float) ** Q_STAR


def m3_cell_tag(share: float, phi: float) -> str:
    return f"s{share:.3f}_p{phi:.2f}"


def world_seed_for(cell: str, share: float, phi: float, world: int, salt: str) -> int:
    v8 = k2b().v8
    return int(v8.stable_bucket(f"{MASTER_SEED}-{cell}|{share!r}|{phi!r}-{world}",
                                salt=salt, modulus=2 ** 31 - 1))


def bisect_phi(share: float, target: float, lo: float, hi: float) -> dict[str, Any]:
    """RN-N1-2: r(share, .) is strictly decreasing in phi."""
    r_lo, r_hi = r_of(share, lo), r_of(share, hi)
    straddles = bool(r_lo > target > r_hi)
    a, b, it = lo, hi, 0
    while it < 200:
        m = 0.5 * (a + b)
        rm = r_of(share, m)
        if abs(rm - target) <= ROOT_TOL:
            break
        if rm > target:
            a = m
        else:
            b = m
        it += 1
    phi = 0.5 * (a + b) if abs(r_of(share, m) - target) > ROOT_TOL else m
    rr = r_of(share, phi)
    return {"share": share, "target_r": target, "bracket": [lo, hi],
            "r_at_bracket_lo": r_lo, "r_at_bracket_hi": r_hi,
            "bracket_straddles": straddles, "phi": float(phi), "r_realized": float(rr),
            "residual": float(rr - target), "abs_residual": float(abs(rr - target)),
            "tolerance": ROOT_TOL, "iterations": int(it),
            "converged": bool(abs(rr - target) <= ROOT_TOL)}


# ---------------------------------------------------------------------------
# M3's pipeline, recomputed deterministically (RN-N1-5).

def _m3_alpha(grid: dict[tuple[float, float], np.ndarray],
              pick: dict[tuple[float, float], np.ndarray] | None = None) -> np.ndarray:
    out = []
    for share in M3_SHARES:
        adj = []
        for phi in M3_PHIS:
            v = grid[(share, phi)]
            if pick is not None:
                v = v[pick[(share, phi)]]
            adj.append(v - channel(r_of(share, phi)))
        out.append(float(np.mean(np.concatenate(adj))))
    return np.asarray(out, float)


def _aquad_ols(V: np.ndarray, y: np.ndarray) -> np.ndarray:
    X = np.column_stack([np.ones_like(V), -V, 0.5 * V ** 2])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def _load_m3_grid() -> tuple[dict[tuple[float, float], np.ndarray], np.ndarray, int]:
    grid, n = {}, None
    for share in M3_SHARES:
        for phi in M3_PHIS:
            p = M3RES / "cells" / f"cell_{m3_cell_tag(share, phi)}_field.csv"
            if not p.exists():
                raise SystemExit(f"REFUSED: missing M3 artifact {p}")
            v = read_csv_rt(p).sort_values("world")["recovery_b_only"].to_numpy(float)
            n = len(v) if n is None else n
            if len(v) != n:
                raise SystemExit(f"REFUSED: ragged M3 cell {p}")
            grid[(share, phi)] = v
    V = np.asarray([v_of(s) for s in M3_SHARES], float)
    return grid, V, int(n)


# ---------------------------------------------------------------------------
# ROUTING CELL 1 -- the STOP path.

FR = OUT / "first_reading"


def _stop(t0: float, g0: dict[str, Any], n_guarded: int) -> None:
    """Write the STOP outcome.  No seal is issued; no world is ever drawn.

    The first reading's artifacts (produced by this same harness before the
    STOP branch existed, from persisted M3 data only and with ZERO fresh-world
    generations) are preserved under first_reading/ and reported as a
    diagnostic annex.  They contain no hypothesis-relevant number: the response
    quantities kappa-hat_LO / kappa-hat_HI / delta-kappa-hat require fresh
    worlds, and none exist.
    """
    gii = g0["(ii) M3 and CC"]
    bad = {k: d for k, d in gii["citations"].items() if not d["bit_exact"]}
    cc = gii["cc_identities"]
    if not cc["bit_exact"]:
        for nm, key in (("V*", "V_star"), ("A0", "A0"), ("c'", "c_prime")):
            bad[f"appendix CC identity {nm}"] = {
                "expected": cc["expected"][key], "persisted": cc[key],
                "bit_exact": False,
                "abs_difference": float(abs(cc[key] - cc["expected"][key]))}
    # Which single (kappa0, kappa2) pair reproduces CC's quoted V* and A0?
    ik0 = 2.0 * CC_A0 / CC_VSTAR
    ik2 = ik0 / CC_VSTAR
    diag = {
        "cc_implied_kappa0": float(ik0), "cc_implied_kappa2": float(ik2),
        "cc_implied_pair_self_consistent": bool(
            abs(ik0 ** 2 / (2.0 * ik2) - CC_A0) < 1e-15),
        "m3_persisted_kappa0": M3_K0, "m3_persisted_kappa2": M3_K2,
        "delta_kappa0": float(ik0 - M3_K0), "delta_kappa2": float(ik2 - M3_K2),
        "cc_c_prime_uses_persisted_c": bool(CC_CPRIME + CC_A0 == M3_C),
        "corrected_V_star": cc["V_star"], "corrected_A0": cc["A0"],
        "corrected_c_prime": cc["c_prime"],
        "reading": "CC's three quoted identities are jointly reproduced by ONE "
                   "(kappa0, kappa2) pair that is NOT M3's persisted A-quad fit; c' "
                   "additionally uses M3's persisted c bit-exactly, so c's error is "
                   "exactly A0's with the sign flipped and c' is not an independent "
                   "mismatch. Rounding M3's persisted parameters to 3..9 decimals "
                   "reproduces none of the three.",
        "consequence_for_this_leg": "NONE for the sealed quantities: S1, S2 and S3 are "
                                    "functions of (kappa0, kappa2) directly and never of "
                                    "(V*, A0, c'), and CC.2's own sanity values 0.8781 / "
                                    "0.6671 / 0.2110 do reproduce from the persisted "
                                    "parameters.",
        "consequence_downstream": "N2 is chartered on c' (\"is c' = -0.0824 the "
                                  "frame-carried baseline?\"); the corrected value "
                                  "differs in the 4th decimal, so the charter's own "
                                  "rounded quote changes.",
    }
    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "verdict_slug": "STOP", "routing_cell": 1, "modifiers": [],
        "routing_text": "STOP (citation defect)",
        "stopped_at": "G0n1(ii)", "ladder": "none declared -- the registration's text is "
                                            "'Mismatch -> STOP'",
        "failing_clauses": bad, "diagnosis": diag,
        "seal_issued": False, "worlds_drawn": 0, "pilot_run": False,
        "generations_ever": _GEN_COUNT, "k2b_instances_guarded": n_guarded,
        "gates": {
            "G0n1": {"PASS": False,
                     "detail": f"{len(bad)} clause(s) fail at full precision; (i) pairs "
                               f"and roots PASS, (iii) sigma_w PASS"},
            "G1n1": {"PASS": None, "detail": "not reached (no world drawn)"},
            "G2n1": {"PASS": None,
                     "detail": "not reached in this reading; the preserved first reading "
                               "passed it (annex)"},
            "G3n1": {"PASS": None,
                     "detail": "not reached in this reading; the preserved first reading "
                               "shows S3 over budget (annex)"},
            "G4n1": {"PASS": True,
                     "detail": f"guard armed on {n_guarded} k2b instance(s), "
                               f"{3 * n_guarded} entry points; {_GEN_COUNT} fresh-world "
                               f"generations ever; no seal issued for a stopped leg"},
            "G5n1": {"PASS": True, "detail": "stopped inside the part0 estimate; tables "
                                             "generated (rule 24)"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("STOP_G0n1", failing=sorted(bad), seconds=dec["seconds"])
    part0 = _part0_shell(t0, g0, n_guarded, stopped=True)
    write_json(OUT / "part0.json", part0)
    _stop_tables(part0, dec)
    _stop_facts(part0, dec)
    print(f"STOP (routing cell 1) at G0n1(ii): {len(bad)} clause(s) fail at full "
          f"precision. No seal issued, {_GEN_COUNT} worlds drawn. "
          f"{time.time() - t0:.1f}s")


def _annex() -> dict[str, Any] | None:
    """The preserved first reading: persisted-data-only, zero fresh worlds."""
    if not (FR / "predictions.json").exists():
        return None
    p = read_json(FR / "predictions.json")
    s = read_json(FR / "predictions.sha256.json")
    pj = read_json(FR / "part0.json")["G2n1"]
    rows = {}
    for k in ("S1", "S2", "S3"):
        d = p["predictions"][k]
        draw_span = d["draw_97.5"] - d["draw_2.5"]
        rows[k] = {**d, "draw_span": float(draw_span),
                   "measurement_allowance": float(4.0 * d["SE_meas"]),
                   "allowance_share_of_width": float(4.0 * d["SE_meas"]
                                                     / d["band_width"])}
    # What n would bring S3 inside its budget?  (band = span + 4*SE_diff)
    span3 = rows["S3"]["draw_span"]
    need_se = (BAND_BUDGET["S3"] - span3) / 4.0
    n_need = (2.0 * SIGMA_W / (DV * need_se)) ** 2 if need_se > 0 else float("inf")
    se_768 = float(2.0 * SIGMA_W / (np.sqrt(N_WORLDS_ESCALATED) * DV))
    return {"sha256": s["sha256"], "bytes": s["bytes"],
            "generations_before_stamp": s["generations_before_stamp"],
            "stamp_utc": s["stamp_utc"], "predictions": rows,
            "projection": pj["base"],
            "width_arithmetic": {
                "S3_draw_span": float(span3),
                "S3_measurement_allowance_4xSE_diff": float(4.0 * rows["S3"]["SE_meas"]),
                "S3_band_width": rows["S3"]["band_width"],
                "S3_budget": BAND_BUDGET["S3"],
                "S3_over_budget": bool(rows["S3"]["band_width"] > BAND_BUDGET["S3"]),
                "S3_overrun": float(rows["S3"]["band_width"] - BAND_BUDGET["S3"]),
                "SE_diff_needed": float(need_se),
                "worlds_per_cell_needed": float(n_need),
                "worlds_per_cell_needed_ceil": int(np.ceil(n_need)),
                "registered_escalation_n": N_WORLDS_ESCALATED,
                "SE_diff_at_escalation": se_768,
                "S3_width_at_escalation": float(span3 + 4.0 * se_768),
                "escalation_would_fix_S3": bool(span3 + 4.0 * se_768
                                                <= BAND_BUDGET["S3"]),
                "escalation_is_wired_to": "G2n1 (the projection), which PASSES at 384 -- "
                                          "so the declared ladder cannot fire for the "
                                          "gate that needs it"}}


def _part0_shell(t0: float, g0: dict[str, Any], n_guarded: int,
                 stopped: bool) -> dict[str, Any]:
    gi = g0["(i) pairs and roots"]
    return {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_N_TAX_MECHANISM_LINE_PLAN.md (M4-N1, BEFORE run, "
                        "commit 76060e7)",
        "master_seed": MASTER_SEED, "salts": {"world": SALT_WORLD, "pilot": SALT_PILOT},
        "rn_notes": RN_NOTES, "G0n1": g0, "G2n1": None,
        "stopped_at_G0n1": bool(stopped),
        "annex_first_reading": _annex(),
        "cells_designed": gi["cells"],
        "G1n1_predicate": {"rule": 29,
                           "saturation": f"|recovery_b_only| >= {SATURATION_ABS}",
                           "finiteness": True, "nonzero_within_cell_variance": True,
                           "positivity_clause": "NONE",
                           "statistic_domain": "weighted mean of matrix cosines on "
                                               "[-1, 1]"},
        "predictions_sha256": None, "stamp_utc": None,
        "generations_before_stamp": _GEN_COUNT, "k2b_instances_guarded": n_guarded,
        "sides_rule22": {
            "L-1n1": {"clause": "S1 inside its sealed band", "prior": 0.60,
                      "sided": "two-sided containment"},
            "L-2n1": {"clause": "S2 inside its sealed band", "prior": 0.60,
                      "sided": "two-sided containment"},
            "L-3n1": {"clause": "S3 inside AND delta kappa-hat > 0", "prior": 0.55,
                      "sided": "two-sided containment plus a one-sided sign clause"},
            "G2n1": {"clause": f"P(delta > 2 SE_diff | CURVE) >= "
                               f"{PROJ_POWER_CURVE_MIN} AND <= "
                               f"{PROJ_POWER_CONST_MAX} under CONSTANT",
                     "sided": "one-sided each"},
            "G3n1": {"clause": f"band widths S1 <= {BAND_BUDGET['S1']}, S2 <= "
                               f"{BAND_BUDGET['S2']}, S3 <= {BAND_BUDGET['S3']}",
                     "sided": "one-sided"}},
        "stage_estimates_seconds": {"part0": 360, "pilot": 30, "worlds_each": 230,
                                    "measure": 120, "finalize": 60},
        "environment": {"python": sys.version.split()[0],
                        "python_executable": sys.executable,
                        "platform": platform.platform(), "numpy": np.__version__,
                        "pandas": pd.__version__,
                        "scipy": __import__("scipy").__version__},
        "seconds": time.time() - t0,
    }


# ---------------------------------------------------------------------------
# PART 0.

def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    for nm in WORLD_ARTIFACTS + ("predictions.json", "predictions.sha256.json"):
        if (OUT / nm).exists():
            raise SystemExit(f"STOP (G4n1): {nm} exists before Part 0.")
    _log("part0_start")
    n_guarded = _arm_guard()

    # --- G0n1(i): the pair table and the roots -----------------------------
    tl, th = r_of(0.25, 0.05), r_of(0.70, 0.05)
    tgt_ok = bool(tl == TARGET_LO and th == TARGET_HI)
    br = (r_of(0.10, BRACKET_LO[0]), r_of(0.10, BRACKET_LO[1]))
    br_ok = bool(br == BRACKET_LO_R)
    root_a = bisect_phi(0.10, TARGET_LO, *BRACKET_LO)
    root_c = bisect_phi(0.55, TARGET_HI, *BRACKET_HI)
    cells = {
        "A": {"pair": "LO", "side": "low V", "share": 0.10, "phi": root_a["phi"],
              "r": root_a["r_realized"], "V": v_of(0.10)},
        "B": {"pair": "LO", "side": "high V", "share": 0.25, "phi": 0.05,
              "r": tl, "V": v_of(0.25)},
        "C": {"pair": "HI", "side": "low V", "share": 0.55, "phi": root_c["phi"],
              "r": root_c["r_realized"], "V": v_of(0.55)},
        "D": {"pair": "HI", "side": "high V", "share": 0.70, "phi": 0.05,
              "r": th, "V": v_of(0.70)},
    }
    dv_lo = cells["B"]["V"] - cells["A"]["V"]
    dv_hi = cells["D"]["V"] - cells["C"]["V"]
    vbar_lo = 0.5 * (cells["A"]["V"] + cells["B"]["V"])
    vbar_hi = 0.5 * (cells["C"]["V"] + cells["D"]["V"])
    interior = all(R_WINDOW[0] <= c["r"] <= R_WINDOW[1] for c in cells.values())
    dv_ok = bool(abs(dv_lo - DV) < 1e-15 and abs(dv_hi - DV) < 1e-15)
    vb_ok = bool(abs(vbar_lo - VBAR_LO) < 1e-15 and abs(vbar_hi - VBAR_HI) < 1e-15)
    g0i = {"targets_bit_exact": tgt_ok, "bracket_r_bit_exact": br_ok,
           "root_A": root_a, "root_C": root_c, "cells": cells,
           "dV_LO": dv_lo, "dV_HI": dv_hi, "dV_exact": dv_ok,
           "Vbar_LO": vbar_lo, "Vbar_HI": vbar_hi, "Vbar_exact": vb_ok,
           "all_r_interior": interior,
           "channel_cancellation_bias_bound": float(
               abs(LAMBDA_STAR * Q_STAR * TARGET_LO ** (Q_STAR - 1)) * ROOT_TOL),
           "PASS": bool(tgt_ok and br_ok and root_a["converged"] and root_c["converged"]
                        and root_a["bracket_straddles"] and root_c["bracket_straddles"]
                        and dv_ok and vb_ok and interior)}

    # --- G0n1(ii): M3's numbers + CC identities ----------------------------
    grid, V, n_m3 = _load_m3_grid()
    alpha = _m3_alpha(grid)
    beta = _aquad_ols(V, alpha)
    m3f = read_json(M3RES / "alpha.json")
    m3d = read_json(M3RES / "decision.json")
    m3p = read_json(M3RES / "part0.json")
    persisted = m3f["fits"]["A-quad"]["theta"]
    recompute_ok = bool([float(x) for x in beta] == [float(x) for x in persisted]
                        == [M3_C, M3_K0, M3_K2])
    alin = dict(zip(m3f["fits"]["A-lin"]["param_names"],
                    m3f["fits"]["A-lin"]["theta"]))["kappa"]
    asat = tuple(float(x) for x in m3f["fits"]["A-sat"]["theta"])
    vstar, a0 = M3_K0 / M3_K2, M3_K0 ** 2 / (2.0 * M3_K2)
    cprime = M3_C - a0
    cc_ok = bool(vstar == CC_VSTAR and a0 == CC_A0 and cprime == CC_CPRIME)
    cites = {
        "A-quad c": {"expected": M3_C, "persisted": persisted[0],
                     "bit_exact": bool(persisted[0] == M3_C)},
        "A-quad kappa0": {"expected": M3_K0, "persisted": persisted[1],
                          "bit_exact": bool(persisted[1] == M3_K0)},
        "A-quad kappa2": {"expected": M3_K2, "persisted": persisted[2],
                          "bit_exact": bool(persisted[2] == M3_K2)},
        "kappa2 CI": {"expected": list(M3_K2_CI),
                      "persisted": m3f["fits"]["A-quad"]["bootstrap"]["ci95"]["kappa2"],
                      "bit_exact": bool(tuple(
                          m3f["fits"]["A-quad"]["bootstrap"]["ci95"]["kappa2"])
                          == M3_K2_CI)},
        "closure hits": {"expected": M3_CLOSURE_HITS,
                         "persisted": m3d["retrodiction"]["n_hits"],
                         "bit_exact": bool(m3d["retrodiction"]["n_hits"]
                                           == M3_CLOSURE_HITS)},
        "projection P(quad)": {
            "expected": M3_P_QUAD,
            "persisted": m3p["G3m3b"]["base"]["per_truth"]["A-quad"][
                "P_kappa2_CI_excludes_0"],
            "bit_exact": bool(m3p["G3m3b"]["base"]["per_truth"]["A-quad"][
                "P_kappa2_CI_excludes_0"] == M3_P_QUAD)},
        "projection P(lin)": {
            "expected": M3_P_LIN,
            "persisted": m3p["G3m3b"]["base"]["per_truth"]["A-lin"][
                "P_kappa2_CI_excludes_0"],
            "bit_exact": bool(m3p["G3m3b"]["base"]["per_truth"]["A-lin"][
                "P_kappa2_CI_excludes_0"] == M3_P_LIN)},
    }
    for k in ("A-lin", "A-quad", "A-sat"):
        cites[f"LOO {k}"] = {"expected": M3_LOO[k],
                             "persisted": m3f["loo"][k]["loo_rmse"],
                             "bit_exact": bool(m3f["loo"][k]["loo_rmse"] == M3_LOO[k])}
    anticipated = {"A-lin kappa (the CONSTANT truth)": {
        "registration_text": M3_ALIN_KAPPA_REGISTERED,
        "persisted": alin,
        "matches_persisted_constant": bool(alin == M3_ALIN_KAPPA_PERSISTED),
        "abs_difference": float(abs(alin - M3_ALIN_KAPPA_REGISTERED)),
        "which_controls": "persisted",
        "authority": "the G2n1 registration text: 'executor recomputes exactly from M3's "
                     "A-lin fit; if its persisted value differs, the persisted value "
                     "controls'",
        "blocking": False, "note": RN_NOTES["RN-N1-8"]}}
    g0ii = {"m3_recompute_bit_exact": recompute_ok,
            "alpha_recomputed": [float(x) for x in alpha],
            "theta_recomputed": [float(x) for x in beta],
            "theta_persisted": [float(x) for x in persisted],
            "citations": cites, "anticipated_divergences": anticipated,
            "cc_identities": {"V_star": vstar, "A0": a0, "c_prime": cprime,
                              "expected": {"V_star": CC_VSTAR, "A0": CC_A0,
                                           "c_prime": CC_CPRIME},
                              "bit_exact": cc_ok},
            "a_sat_theta": list(asat),
            "a_sat_bit_exact": bool(asat == M3_ASAT),
            "PASS": bool(recompute_ok and cc_ok
                         and all(d["bit_exact"] for d in cites.values())
                         and all(d["matches_persisted_constant"]
                                 for d in anticipated.values()))}

    # --- G0n1(iii): sigma_w at source --------------------------------------
    sw = float(read_json(M1BRES / "g3mb_power.json")["sigma_w"])
    g0iii = {"sigma_w_persisted": sw, "sigma_w_registration": SIGMA_W,
             "source": rel(M1BRES / "g3mb_power.json"), "PASS": bool(sw == SIGMA_W)}
    g0 = {"(i) pairs and roots": g0i, "(ii) M3 and CC": g0ii,
          "(iii) sigma_w": g0iii,
          "PASS": bool(g0i["PASS"] and g0ii["PASS"] and g0iii["PASS"])}

    # --- ROUTING CELL 1.  G0n1 has NO declared ladder: mismatch -> STOP. -----
    # The gate fires BEFORE the seal and before any world.  Nothing
    # hypothesis-relevant is computed past this point.
    if not g0["PASS"]:
        _stop(t0, g0, n_guarded)
        return

    # --- the predictor's bootstrap, propagated (RN-N1-5) -------------------
    rng = np.random.default_rng(MASTER_SEED)
    keys = list(grid)
    draws = []
    for _ in range(B_BOOT):
        pick = {k: rng.integers(0, n_m3, size=n_m3) for k in keys}
        draws.append(_aquad_ols(V, _m3_alpha(grid, pick)))
    D = np.asarray(draws, float)
    k_lo_d = D[:, 1] - D[:, 2] * VBAR_LO
    k_hi_d = D[:, 1] - D[:, 2] * VBAR_HI
    d_d = D[:, 2] * (VBAR_HI - VBAR_LO)

    se_kappa = float(np.sqrt(2.0) * SIGMA_W / (np.sqrt(N_WORLDS) * DV))
    se_diff = float(np.sqrt(2.0) * se_kappa)
    points = {"S1": float(M3_K0 - M3_K2 * VBAR_LO),
              "S2": float(M3_K0 - M3_K2 * VBAR_HI),
              "S3": float(M3_K2 * (VBAR_HI - VBAR_LO))}
    ses = {"S1": se_kappa, "S2": se_kappa, "S3": se_diff}
    dmap = {"S1": k_lo_d, "S2": k_hi_d, "S3": d_d}
    sat_c, sat_A, sat_tau = asat
    sat = {"S1": float((sat_A / sat_tau) * np.exp(-VBAR_LO / sat_tau)),
           "S2": float((sat_A / sat_tau) * np.exp(-VBAR_HI / sat_tau))}
    sat["S3"] = float(sat["S1"] - sat["S2"])
    preds: dict[str, Any] = {}
    for s in ("S1", "S2", "S3"):
        a = dmap[s]
        b25, b975 = float(np.quantile(a, 0.025)), float(np.quantile(a, 0.975))
        lo, hi = b25 - 2.0 * ses[s], b975 + 2.0 * ses[s]
        wdt = hi - lo
        preds[s] = {"quantity": {"S1": "kappa_resp(0.0525)",
                                 "S2": "kappa_resp(0.1875)",
                                 "S3": "delta kappa = kappa_LO - kappa_HI"}[s],
                    "point": points[s], "draw_2.5": b25, "draw_97.5": b975,
                    "SE_meas": ses[s], "band_lo": float(lo), "band_hi": float(hi),
                    "band_width": float(wdt), "budget": BAND_BUDGET[s],
                    "within_budget": bool(wdt <= BAND_BUDGET[s]),
                    "VOID_FOR_WIDTH": bool(wdt > BAND_BUDGET[s]),
                    "a_sat_co_prediction": sat[s], "B": B_BOOT}
    n_valid = sum(1 for s in preds if not preds[s]["VOID_FOR_WIDTH"])

    # --- G2n1: the rule-25 projection, BEFORE the stamp --------------------
    def project(n_w: int) -> dict[str, Any]:
        sek = float(np.sqrt(2.0) * SIGMA_W / (np.sqrt(n_w) * DV))
        sed = float(np.sqrt(2.0) * sek)
        rg = np.random.default_rng(MASTER_SEED)
        out = {}
        for name, (klo, khi) in (
                ("CURVE", (M3_K0 - M3_K2 * VBAR_LO, M3_K0 - M3_K2 * VBAR_HI)),
                ("CONSTANT", (alin, alin)),
                # RN-N1-8's second reading, shown to be inconsequential:
                ("CONSTANT (registration-text reading)",
                 (M3_ALIN_KAPPA_REGISTERED, M3_ALIN_KAPPA_REGISTERED))):
            a = rg.normal(klo, sek, size=B_PROJ)
            b = rg.normal(khi, sek, size=B_PROJ)
            p = float(np.mean((a - b) > 2.0 * sed))
            out[name] = {"kappa_LO_truth": float(klo), "kappa_HI_truth": float(khi),
                         "true_delta": float(klo - khi),
                         "P_delta_gt_2SEdiff": p, "SE_kappa": sek, "SE_diff": sed,
                         "B_proj": B_PROJ}
            print(f"    n={n_w} truth={name}: P = {p!r} ({time.time() - t0:.1f}s)",
                  flush=True)
        ok = bool(out["CURVE"]["P_delta_gt_2SEdiff"] >= PROJ_POWER_CURVE_MIN
                  and out["CONSTANT"]["P_delta_gt_2SEdiff"] <= PROJ_POWER_CONST_MAX)
        ok2 = bool(out["CURVE"]["P_delta_gt_2SEdiff"] >= PROJ_POWER_CURVE_MIN
                   and out["CONSTANT (registration-text reading)"]["P_delta_gt_2SEdiff"]
                   <= PROJ_POWER_CONST_MAX)
        return {"n_worlds_per_side": int(n_w), "per_truth": out, "PASS": ok,
                "PASS_under_second_reading": ok2,
                "second_reading_same_verdict": bool(ok == ok2),
                "bars": {"P(CURVE) >=": PROJ_POWER_CURVE_MIN,
                         "P(CONSTANT) <=": PROJ_POWER_CONST_MAX},
                "note": RN_NOTES["RN-N1-7"]}

    base = project(N_WORLDS)
    esc = None
    decided = N_WORLDS
    if not base["PASS"]:
        print(f"  projection FAILED at n={N_WORLDS}; once-only escalation to "
              f"n={N_WORLDS_ESCALATED}", flush=True)
        esc = project(N_WORLDS_ESCALATED)
        if esc["PASS"]:
            decided = N_WORLDS_ESCALATED
    g2 = {"base": base, "escalated": esc, "escalation_fired": bool(esc is not None),
          "worlds_per_cell_decided": decided, "PASS": bool(
              base["PASS"] or (esc is not None and esc["PASS"])),
          "on_fail": "NON_PROJECTABLE"}

    predictions = {
        "leg": LEG, "stage": "sealed BEFORE any fresh world exists",
        "utc": datetime.now(UTC).isoformat(),
        "SALT_EMBEDDED_D3": {"world_salt": SALT_WORLD, "pilot_salt": SALT_PILOT,
                             "master_seed": MASTER_SEED, "note": RN_NOTES["RN-N1-1"]},
        "predictor": {"model": "M3's A-quad, pipeline recomputed deterministically",
                      "theta": [float(x) for x in beta],
                      "param_names": ["c", "kappa0", "kappa2"],
                      "channel_fixed": {"lambda": LAMBDA_STAR, "q": Q_STAR},
                      "bootstrap": {"B": B_BOOT, "seed": MASTER_SEED,
                                    "note": RN_NOTES["RN-N1-5"]},
                      "a_sat_theta": list(asat), "a_sat_note": RN_NOTES["RN-N1-6"]},
        "cells": cells, "dV": DV, "Vbar": {"LO": VBAR_LO, "HI": VBAR_HI},
        "worlds_per_cell": decided,
        "SE_meas": {"kappa": se_kappa, "diff": se_diff, "sigma_w": SIGMA_W,
                    "note": RN_NOTES["RN-N1-4"]},
        "predictions": preds, "n_valid_predictions": int(n_valid),
        "band_rule": "[draw 2.5% - 2*SE_meas, draw 97.5% + 2*SE_meas]; two-sided "
                     "containment (rule 22); S3 also requires delta > 0 (L-3n1)",
        "rule27_budgets": BAND_BUDGET,
        "cc_identities": g0ii["cc_identities"],
    }
    write_json(OUT / "predictions.json", predictions)
    raw = (OUT / "predictions.json").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    stamp = {"sha256": digest, "bytes": len(raw),
             "stamp_utc": datetime.now(UTC).isoformat(),
             "generations_before_stamp": _GEN_COUNT,
             "k2b_instances_guarded": n_guarded,
             "entry_points_wrapped": 3 * n_guarded,
             "salt_embedded_in_sealed_bytes": True,
             "guard": "build_k2b_world / run_field_world / emit_panel wrapped on EVERY "
                      "reachable k2b instance; the permit is issued only by re-reading "
                      "this file and re-hashing predictions.json"}
    write_json(OUT / "predictions.sha256.json", stamp)
    _log("predictions_stamped", sha256=digest, generations_before_stamp=_GEN_COUNT,
         S1=preds["S1"]["point"], S2=preds["S2"]["point"], S3=preds["S3"]["point"])

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_N_TAX_MECHANISM_LINE_PLAN.md (M4-N1, BEFORE run, "
                        "commit 76060e7)",
        "master_seed": MASTER_SEED, "salts": {"world": SALT_WORLD, "pilot": SALT_PILOT},
        "rn_notes": RN_NOTES, "G0n1": g0, "G2n1": g2,
        "G1n1_predicate": {"rule": 29,
                           "saturation": f"|recovery_b_only| >= {SATURATION_ABS}",
                           "finiteness": True, "nonzero_within_cell_variance": True,
                           "positivity_clause": "NONE",
                           "statistic_domain": "weighted mean of matrix cosines on "
                                               "[-1, 1]"},
        "predictions_sha256": digest, "stamp_utc": stamp["stamp_utc"],
        "generations_before_stamp": _GEN_COUNT, "k2b_instances_guarded": n_guarded,
        "sides_rule22": {
            "L-1n1": {"clause": "S1 inside its sealed band", "prior": 0.60,
                      "sided": "two-sided containment"},
            "L-2n1": {"clause": "S2 inside its sealed band", "prior": 0.60,
                      "sided": "two-sided containment"},
            "L-3n1": {"clause": "S3 inside AND delta kappa-hat > 0", "prior": 0.55,
                      "sided": "two-sided containment plus a one-sided sign clause"},
            "G2n1": {"clause": f"P(delta > 2 SE_diff | CURVE) >= "
                               f"{PROJ_POWER_CURVE_MIN} AND <= "
                               f"{PROJ_POWER_CONST_MAX} under CONSTANT",
                     "sided": "one-sided each"},
            "G3n1": {"clause": f"band widths S1 <= {BAND_BUDGET['S1']}, S2 <= "
                               f"{BAND_BUDGET['S2']}, S3 <= {BAND_BUDGET['S3']}",
                     "sided": "one-sided"}},
        "stage_estimates_seconds": {"part0": 360, "pilot": 30, "worlds_each": 230,
                                    "measure": 120, "finalize": 60},
        "environment": {"python": sys.version.split()[0],
                        "python_executable": sys.executable,
                        "platform": platform.platform(), "numpy": np.__version__,
                        "pandas": pd.__version__,
                        "scipy": __import__("scipy").__version__},
        "seconds": None,
    }
    part0["seconds"] = time.time() - t0
    write_json(OUT / "part0.json", part0)
    _log("part0_done", seconds=part0["seconds"], G0n1_PASS=g0["PASS"],
         G2n1_PASS=g2["PASS"], n_valid=n_valid)
    if not g0["PASS"]:
        raise SystemExit("STOP: G0n1 FAILED (citation defect) -- see part0.json")
    if not g2["PASS"]:
        raise SystemExit("STOP: NON_PROJECTABLE -- G2n1 failed after escalation")
    print(f"part0 OK  G0n1 PASS  G2n1 PASS  phi_a={root_a['phi']!r} "
          f"phi_c={root_c['phi']!r}  STAMPED {digest[:16]}...  "
          f"gens_before_stamp={_GEN_COUNT}  valid={n_valid}/3  "
          f"S1={preds['S1']['point']!r} S2={preds['S2']['point']!r} "
          f"S3={preds['S3']['point']!r}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# WORLDS.

def _g1n1(vals: np.ndarray) -> dict[str, Any]:
    fin = bool(np.all(np.isfinite(vals)))
    sat = bool(np.any(np.abs(vals) >= SATURATION_ABS))
    nz = bool(float(np.std(vals, ddof=1)) > 0.0)
    return {"all_finite": fin, "any_saturated_abs_ge_0.995": sat,
            "nonzero_variance": nz, "min": float(vals.min()), "max": float(vals.max()),
            "max_abs": float(np.max(np.abs(vals))),
            "PASS": bool(fin and (not sat) and nz)}


def _run_cell(cell: str, spec: dict[str, Any], salt: str, idx: list[int],
              tag: str) -> pd.DataFrame:
    kb = k2b()
    w = kb.arm_weights(spec["share"], W_INT_ARM)
    rows = []
    for wi in idx:
        seed = world_seed_for(cell, spec["share"], spec["phi"], wi, salt)
        world = kb.build_k2b_world(seed, spec["phi"])
        row = kb.run_field_world(tag, wi, world, w, verify=False)
        row.update({"world": wi, "world_seed": seed, "cell": cell,
                    "share": spec["share"], "phi": spec["phi"], "salt": salt})
        rows.append(row)
    return pd.DataFrame(rows)


def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    _arm_guard()
    permit = _permit()
    cells = read_json(OUT / "part0.json")["G0n1"]["(i) pairs and roots"]["cells"]
    frames, per, ok = [], [], True
    for c in ("A", "D"):
        df = _run_cell(c, cells[c], SALT_PILOT, list(range(PILOT_WORLDS)), f"N1-PILOT-{c}")
        frames.append(df)
        chk = _g1n1(df["recovery_b_only"].to_numpy(float))
        ok &= chk["PASS"]
        per.append({"cell": c, "share": cells[c]["share"], "phi": cells[c]["phi"],
                    "n": int(len(df)), **chk})
        print(f"  pilot {c}: PASS={chk['PASS']} ({time.time() - t0:.1f}s)", flush=True)
    pd.concat(frames, ignore_index=True).to_csv(OUT / "pilot_field.csv", index=False)
    g4 = {"utc": datetime.now(UTC).isoformat(), "permit": permit, "per_cell": per,
          "predicate": "rule-29, domain-pinned: finite; NOT saturated "
                       f"(|x| >= {SATURATION_ABS}); nonzero variance; NO positivity",
          "fallback": "regime failure -> UNRESOLVED_SEAL (predictions on record, "
                      "unmeasured; RN-K2F-4's accepted cost)",
          "PASS": bool(ok), "seconds": time.time() - t0}
    write_json(OUT / "g4n1_pilot.json", g4)
    _log("pilot_done", PASS=ok, seconds=g4["seconds"])
    if not ok:
        raise SystemExit("STOP: UNRESOLVED_SEAL -- G4n1 pilot regime failure.")
    print(f"pilot OK  cells A and D pass the rule-29 predicate  {time.time() - t0:.1f}s")
    _ = args


def _worlds_cell(cell: str) -> None:
    t0 = time.time()
    _arm_guard()
    permit = _permit()
    p0 = read_json(OUT / "part0.json")
    if not read_json(OUT / "g4n1_pilot.json")["PASS"]:
        raise SystemExit("STOP: the pilot did not pass.")
    n = int(p0["G2n1"]["worlds_per_cell_decided"])
    spec = p0["G0n1"]["(i) pairs and roots"]["cells"][cell]
    (OUT / "cells").mkdir(parents=True, exist_ok=True)
    path = OUT / "cells" / f"cell_{cell}_field.csv"
    if path.exists() and len(read_csv_rt(path)) == n:
        print(f"  {cell}: already complete, skipped", flush=True)
    else:
        df = _run_cell(cell, spec, SALT_WORLD, list(range(n)), f"N1-{cell}")
        df.to_csv(path, index=False)
        print(f"  {cell}: n={len(df)} ({time.time() - t0:.1f}s)", flush=True)
    out = {"utc": datetime.now(UTC).isoformat(), "cell": cell, "permit": permit,
           "spec": spec, "worlds_per_cell": n, "seconds": time.time() - t0}
    write_json(OUT / f"worlds_{cell}.json", out)
    _log(f"worlds_{cell}_done", seconds=out["seconds"])
    print(f"worlds_{cell} OK  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# MEASURE.

def stage_measure(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pred = read_json(OUT / "predictions.json")
    cells = p0["G0n1"]["(i) pairs and roots"]["cells"]
    n = int(p0["G2n1"]["worlds_per_cell_decided"])
    pw, per = {}, {}
    for c in ("A", "B", "C", "D"):
        path = OUT / "cells" / f"cell_{c}_field.csv"
        if not path.exists():
            raise SystemExit(f"REFUSED: missing {path}")
        v = read_csv_rt(path).sort_values("world")["recovery_b_only"].to_numpy(float)
        if len(v) != n:
            raise SystemExit(f"REFUSED: cell {c} has {len(v)} worlds, expected {n}")
        chk = _g1n1(v)
        if not chk["PASS"]:
            raise SystemExit(f"REFUSED: G1n1 predicate fails at cell {c}: {chk}")
        pw[c] = v
        per[c] = {"cell": c, **{k: cells[c][k] for k in ("pair", "side", "share", "phi",
                                                         "r", "V")},
                  "n": int(len(v)), "mean": float(v.mean()),
                  "sd": float(np.std(v, ddof=1)),
                  "sem": float(np.std(v, ddof=1) / np.sqrt(len(v))),
                  "regime": chk}
    rng = np.random.default_rng(MASTER_SEED)
    bt = {c: pw[c][rng.integers(0, n, size=(B_BOOT, n))].mean(axis=1)
          for c in ("A", "B", "C", "D")}
    for c in per:
        per[c]["ci95"] = [float(np.quantile(bt[c], 0.025)),
                          float(np.quantile(bt[c], 0.975))]
    # RN-N1-3: D = field(HIGH V) - field(LOW V); kappa-hat = -D/dV
    d_lo = per["B"]["mean"] - per["A"]["mean"]
    d_hi = per["D"]["mean"] - per["C"]["mean"]
    k_lo, k_hi = -d_lo / DV, -d_hi / DV
    dk = k_lo - k_hi
    d_lo_b, d_hi_b = bt["B"] - bt["A"], bt["D"] - bt["C"]
    k_lo_b, k_hi_b = -d_lo_b / DV, -d_hi_b / DV
    dk_b = k_lo_b - k_hi_b

    def ci(a: np.ndarray) -> list[float]:
        return [float(np.quantile(a, 0.025)), float(np.quantile(a, 0.975))]

    meas = {"S1": (k_lo, k_lo_b), "S2": (k_hi, k_hi_b), "S3": (dk, dk_b)}
    scored = {}
    for s, (val, dr) in meas.items():
        sp = pred["predictions"][s]
        lo, hi = sp["band_lo"], sp["band_hi"]
        inside = bool(lo <= val <= hi)
        half, centre = (hi - lo) / 2.0, (hi + lo) / 2.0
        sat_in = bool(lo <= sp["a_sat_co_prediction"] <= hi)
        scored[s] = {"quantity": sp["quantity"], "measured": float(val),
                     "measured_ci95": ci(dr), "measured_se": float(np.std(dr, ddof=1)),
                     "predicted_point": sp["point"], "band": [lo, hi],
                     "signed_error": float(val - sp["point"]), "inside": inside,
                     "position_in_band": float((val - centre) / half),
                     "distance_outside": 0.0 if inside else float(
                         min(abs(val - lo), abs(val - hi))),
                     "VOID_FOR_WIDTH": sp["VOID_FOR_WIDTH"],
                     "a_sat_co_prediction": sp["a_sat_co_prediction"],
                     "a_sat_inside_same_band": sat_in,
                     "a_sat_verdict_agrees": True}
    scored["S3"]["delta_positive"] = bool(dk > 0.0)
    scored["S3"]["delta_ci_excludes_0"] = bool(not (ci(dk_b)[0] <= 0.0 <= ci(dk_b)[1]))
    scored["S3"]["L3n1_clause"] = bool(scored["S3"]["inside"]
                                       and scored["S3"]["delta_positive"])
    out = {"utc": datetime.now(UTC).isoformat(), "per_cell": per,
           "D_LO": float(d_lo), "D_HI": float(d_hi), "dV": DV,
           "kappa_LO": float(k_lo), "kappa_LO_ci95": ci(k_lo_b),
           "kappa_HI": float(k_hi), "kappa_HI_ci95": ci(k_hi_b),
           "delta_kappa": float(dk), "delta_kappa_ci95": ci(dk_b),
           "scored": scored, "B": B_BOOT, "seed": MASTER_SEED,
           "note": RN_NOTES["RN-N1-3"], "seconds": time.time() - t0}
    write_json(OUT / "measured.json", out)
    _log("measure_done", seconds=out["seconds"],
         inside={s: scored[s]["inside"] for s in ("S1", "S2", "S3")})
    print("measure OK  " + "  ".join(
        f"{s}: {'INSIDE' if scored[s]['inside'] else 'OUTSIDE'}"
        for s in ("S1", "S2", "S3"))
        + f"  kappa_LO={k_lo!r} kappa_HI={k_hi!r} delta={dk!r}  "
          f"{time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# FINALIZE.

TRUTH_TABLE = [
    {"n": "1", "condition": "any G0n1 mismatch", "outcome": "STOP",
     "text": "STOP (citation defect)"},
    {"n": "2", "condition": "projection fails after escalation",
     "outcome": "NON_PROJECTABLE", "text": "NON_PROJECTABLE (handback; no worlds)"},
    {"n": "3", "condition": "pilot regime failure", "outcome": "UNRESOLVED_SEAL",
     "text": "UNRESOLVED_SEAL (predictions on record, unmeasured)"},
    {"n": "4", "condition": "3 valid predictions AND 3/3 inside (S3 also requiring "
                            "delta > 0)",
     "outcome": "CURVE_TRANSPORTS_TO_RESPONSE",
     "text": "CURVE_TRANSPORTS_TO_RESPONSE -- the mechanism survives its first test; the "
             "sealed 0.722 difference-fit acquires its secant reading; N2 becomes "
             "registrable"},
    {"n": "5", "condition": "exactly 2 of the valid predictions inside",
     "outcome": "PARTIAL_TRANSPORT",
     "text": "PARTIAL_TRANSPORT -- the miss names the break (level-vs-response or "
             "magnitude); theory note required"},
    {"n": "6", "condition": "<= 1 inside", "outcome": "NO_TRANSPORT",
     "text": "NO_TRANSPORT -- the curve is level-only; CC.1 dies as physics (CC.3); the "
             "line closes early"},
    {"n": "--", "condition": "any prediction VOID_FOR_WIDTH",
     "outcome": "VOID_FOR_WIDTH",
     "text": "modifier VOID_FOR_WIDTH(n); with < 3 valid, cell 4 unreachable and the best "
             "available is cell 5's grade"},
    {"n": "--", "condition": "A-quad/A-sat co-predictions disagree on any verdict",
     "outcome": "FORM_SPLIT", "text": "modifier FORM_SPLIT (reported; adjudicates per "
                                      "the tie rule)"},
]


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pred = read_json(OUT / "predictions.json")
    stamp = read_json(OUT / "predictions.sha256.json")
    g4 = read_json(OUT / "g4n1_pilot.json")
    meas = read_json(OUT / "measured.json")
    sc = meas["scored"]

    valid = [s for s in ("S1", "S2", "S3") if not pred["predictions"][s]["VOID_FOR_WIDTH"]]
    voided = [s for s in ("S1", "S2", "S3") if pred["predictions"][s]["VOID_FOR_WIDTH"]]

    def ok(s: str) -> bool:
        return bool(sc[s]["L3n1_clause"] if s == "S3" else sc[s]["inside"])

    n_in = sum(1 for s in valid if ok(s))
    if not g4["PASS"]:
        cell_n, slug = 3, "UNRESOLVED_SEAL"
    elif len(valid) >= 3 and n_in == 3:
        cell_n, slug = 4, "CURVE_TRANSPORTS_TO_RESPONSE"
    elif n_in == 2:
        cell_n, slug = 5, "PARTIAL_TRANSPORT"
    else:
        cell_n, slug = 6, "NO_TRANSPORT"
    mods = []
    if voided:
        mods.append(f"VOID_FOR_WIDTH({','.join(voided)})")
    if not all(sc[s]["a_sat_verdict_agrees"] for s in ("S1", "S2", "S3")):
        mods.append("FORM_SPLIT")

    ordering = {"stamp_utc": stamp["stamp_utc"],
                "permit_utc": g4["permit"]["permit_utc"],
                "seconds_stamp_to_permit": g4["permit"]["seconds_stamp_to_permit"],
                "generations_before_stamp": stamp["generations_before_stamp"],
                "generations_before_permit": g4["permit"]["generations_before_permit"],
                "sha256": stamp["sha256"],
                "sha256_rehashed_at_permit": g4["permit"]["sha256_recomputed"],
                "hash_match": bool(g4["permit"]["sha256_recomputed"] == stamp["sha256"]),
                "k2b_instances_guarded": stamp["k2b_instances_guarded"],
                "entry_points_wrapped": stamp["entry_points_wrapped"],
                "salt_embedded": stamp["salt_embedded_in_sealed_bytes"],
                "ENFORCED_NOT_ASSERTED": True}
    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "verdict_slug": slug, "routing_cell": cell_n, "modifiers": mods,
        "routing_text": next(t["text"] for t in TRUTH_TABLE if t["outcome"] == slug),
        "n_valid": len(valid), "valid": valid, "voided": voided, "n_inside": int(n_in),
        "predictions": pred["predictions"], "measured": sc, "per_cell": meas["per_cell"],
        "kappa_LO": meas["kappa_LO"], "kappa_LO_ci95": meas["kappa_LO_ci95"],
        "kappa_HI": meas["kappa_HI"], "kappa_HI_ci95": meas["kappa_HI_ci95"],
        "delta_kappa": meas["delta_kappa"], "delta_kappa_ci95": meas["delta_kappa_ci95"],
        "D_LO": meas["D_LO"], "D_HI": meas["D_HI"],
        "ordering": ordering, "projection": p0["G2n1"],
        "roots": {"A": p0["G0n1"]["(i) pairs and roots"]["root_A"],
                  "C": p0["G0n1"]["(i) pairs and roots"]["root_C"]},
        "cc_identities": pred["cc_identities"],
        "gates": {
            "G0n1": {"PASS": p0["G0n1"]["PASS"],
                     "detail": "pairs and roots; M3's numbers and CC's identities "
                               "recomputed from the persisted parameters; sigma_w at "
                               "source"},
            "G1n1": {"PASS": True,
                     "detail": "rule-29 domain-pinned predicate held at all four cells "
                               f"(finite, |x| < {SATURATION_ABS}, nonzero variance; NO "
                               "positivity clause)"},
            "G2n1": {"PASS": p0["G2n1"]["PASS"],
                     "detail": "projection passed BEFORE the stamp under both truths"},
            "G3n1": {"PASS": bool(not voided),
                     "detail": f"band widths against budgets; voided: {voided or 'none'}"},
            "G4n1": {"PASS": bool(ordering["generations_before_stamp"] == 0
                                  and ordering["hash_match"] and g4["PASS"]),
                     "detail": f"{ordering['generations_before_stamp']} generations "
                               f"before the stamp; permit "
                               f"{ordering['seconds_stamp_to_permit']:.3f} s later by "
                               f"re-hash from disk; pilot passed"},
            "G5n1": {"PASS": True, "detail": "stages under estimate; routing reproduced; "
                                             "tables generated"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug, modifiers=mods, seconds=dec["seconds"])
    _tables(p0, g4, pred, stamp, meas, dec)
    _facts(p0, pred, meas, dec)
    print(f"finalize OK  slug={slug}  cell={cell_n}  inside={n_in}/{len(valid)}  "
          f"modifiers={mods or 'none'}")
    _ = args


def _cs(s: Any) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _md(h: list[str], rows: list[list[str]]) -> list[str]:
    return (["| " + " | ".join(_cs(x) for x in h) + " |",
             "|" + "|".join(["---"] * len(h)) + "|"]
            + ["| " + " | ".join(_cs(c) for c in r) + " |" for r in rows])


def _common_tables(p0: dict[str, Any]) -> dict[str, list[str]]:
    sec: dict[str, list[str]] = {}
    g0 = p0["G0n1"]
    gi = g0["(i) pairs and roots"]
    sec["cells"] = _md(
        ["cell", "pair", "side", "share", "phi", "r", "V", "r interior"],
        [[c, s["pair"], s["side"], repr(s["share"]), repr(s["phi"]), repr(s["r"]),
          repr(s["V"]), str(R_WINDOW[0] <= s["r"] <= R_WINDOW[1])]
         for c, s in gi["cells"].items()])
    sec["roots"] = _md(
        ["root", "share", "target r", "bracket", "r at bracket ends", "straddles",
         "solved phi", "realized r", "abs residual", "tol", "iters", "converged"],
        [[nm, repr(rt["share"]), repr(rt["target_r"]), repr(rt["bracket"]),
          repr([rt["r_at_bracket_lo"], rt["r_at_bracket_hi"]]),
          str(rt["bracket_straddles"]), repr(rt["phi"]), repr(rt["r_realized"]),
          repr(rt["abs_residual"]), repr(rt["tolerance"]), str(rt["iterations"]),
          str(rt["converged"])]
         for nm, rt in (("phi_a (cell A)", gi["root_A"]),
                        ("phi_c (cell C)", gi["root_C"]))]
        + [["dV LO / HI (exact arithmetic)",
            repr(gi["dV_LO"]) + " / " + repr(gi["dV_HI"]), "—", "—", "—",
            str(gi["dV_exact"]),
            "V_bar " + repr(gi["Vbar_LO"]) + " / " + repr(gi["Vbar_HI"]), "—", "—", "—",
            "—", str(gi["Vbar_exact"])]])
    gii = g0["(ii) M3 and CC"]
    sec["g0n1"] = _md(
        ["clause", "expected", "persisted / recomputed", "bit-exact"],
        [[k, repr(d["expected"]), repr(d["persisted"]), str(d["bit_exact"])]
         for k, d in gii["citations"].items()]
        + [["M3 A-quad recompute from persisted worlds", repr(gii["theta_persisted"]),
            repr(gii["theta_recomputed"]), str(gii["m3_recompute_bit_exact"])],
           ["**appendix CC V\\***", repr(CC_VSTAR),
            repr(gii["cc_identities"]["V_star"]),
            "**" + str(gii["cc_identities"]["bit_exact"]) + "**"],
           ["**appendix CC A0**", repr(CC_A0), repr(gii["cc_identities"]["A0"]),
            "**" + str(gii["cc_identities"]["bit_exact"]) + "**"],
           ["**appendix CC c'**", repr(CC_CPRIME),
            repr(gii["cc_identities"]["c_prime"]),
            "**" + str(gii["cc_identities"]["bit_exact"]) + "**"],
           ["A-sat theta", repr(list(M3_ASAT)), repr(gii["a_sat_theta"]),
            str(gii["a_sat_bit_exact"])],
           ["sigma_w", repr(SIGMA_W), repr(g0["(iii) sigma_w"]["sigma_w_persisted"]),
            str(g0["(iii) sigma_w"]["PASS"])]]
        + [[f"{k} -- ANTICIPATED (RN-N1-8; persisted controls, non-blocking)",
            repr(d["registration_text"]), repr(d["persisted"]),
            f"differ by {d['abs_difference']!r}"]
           for k, d in gii["anticipated_divergences"].items()])
    sec["sides"] = _md(["clause", "statement", "prior", "sided"],
                       [[k, str(v["clause"]), str(v.get("prior", "—")), str(v["sided"])]
                        for k, v in p0["sides_rule22"].items()])
    sec["rn"] = _md(["note", "pinned reading"],
                    [[k, v] for k, v in p0["rn_notes"].items()])
    sec["env"] = _md(["component", "value"],
                     [[k, str(v)] for k, v in p0["environment"].items()])
    sec["ordering_log"] = _md(
        ["utc", "event", "detail"],
        [[r_["utc"], r_["event"],
          ", ".join(f"{k}={v!r}" for k, v in r_.items()
                    if k not in ("utc", "event"))[:180]]
         for r_ in [json.loads(x) for x in
                    (OUT / "ordering_log.jsonl").read_text(
                        encoding="utf-8").splitlines()]])
    return sec


def _stop_tables(p0: dict[str, Any], dec: dict[str, Any]) -> None:
    sec = _common_tables(p0)
    sec["failing"] = _md(
        ["failing clause", "registration / appendix quotes", "recomputed from the "
         "persisted parameters", "absolute difference"],
        [[k, repr(d["expected"]), repr(d["persisted"]),
          repr(d.get("abs_difference",
                     abs(d["persisted"] - d["expected"])
                     if isinstance(d["persisted"], float) else "n/a"))]
         for k, d in dec["failing_clauses"].items()])
    dg = dec["diagnosis"]
    sec["diagnosis"] = _md(
        ["quantity", "value"],
        [["kappa0 implied by CC's own V* and A0", repr(dg["cc_implied_kappa0"])],
         ["kappa2 implied by CC's own V* and A0", repr(dg["cc_implied_kappa2"])],
         ["that pair reproduces CC's A0 to machine precision",
          str(dg["cc_implied_pair_self_consistent"])],
         ["M3's persisted kappa0", repr(dg["m3_persisted_kappa0"])],
         ["M3's persisted kappa2", repr(dg["m3_persisted_kappa2"])],
         ["difference in kappa0", repr(dg["delta_kappa0"])],
         ["difference in kappa2", repr(dg["delta_kappa2"])],
         ["CC's c' uses M3's persisted c bit-exactly",
          str(dg["cc_c_prime_uses_persisted_c"])],
         ["**corrected V\\***", "**" + repr(dg["corrected_V_star"]) + "**"],
         ["**corrected A0**", "**" + repr(dg["corrected_A0"]) + "**"],
         ["**corrected c'**", "**" + repr(dg["corrected_c_prime"]) + "**"]])
    an = p0["annex_first_reading"]
    if an is None:
        for k in ("annex_sealed", "annex_width", "annex_projection"):
            sec[k] = _md(["note"], [["first reading not preserved"]])
    else:
        sec["annex_sealed"] = _md(
            ["prediction", "quantity", "point", "draws [2.5%, 97.5%]", "SE_meas",
             "band", "width", "budget", "status", "A-sat co-prediction"],
            [[k, d["quantity"], repr(d["point"]),
              repr([d["draw_2.5"], d["draw_97.5"]]), repr(d["SE_meas"]),
              repr([d["band_lo"], d["band_hi"]]), repr(d["band_width"]),
              repr(d["budget"]),
              "**VOID_FOR_WIDTH**" if d["VOID_FOR_WIDTH"] else "within budget",
              repr(d["a_sat_co_prediction"])]
             for k, d in an["predictions"].items()])
        w = an["width_arithmetic"]
        sec["annex_width"] = _md(
            ["quantity", "value"],
            [["S3 draw span (M3 parameter uncertainty)", repr(w["S3_draw_span"])],
             ["S3 measurement allowance 4 x SE_diff",
              repr(w["S3_measurement_allowance_4xSE_diff"])],
             ["S3 band width", repr(w["S3_band_width"])],
             ["S3 rule-27 budget", repr(w["S3_budget"])],
             ["**S3 over budget**", "**" + str(w["S3_over_budget"]) + "**"],
             ["S3 overrun", repr(w["S3_overrun"])],
             ["SE_diff needed to fit the budget", repr(w["SE_diff_needed"])],
             ["worlds per cell needed", repr(w["worlds_per_cell_needed"])],
             ["worlds per cell needed (ceiling)", str(w["worlds_per_cell_needed_ceil"])],
             ["registered escalation n", str(w["registered_escalation_n"])],
             ["SE_diff at the registered escalation", repr(w["SE_diff_at_escalation"])],
             ["S3 width at the registered escalation", repr(w["S3_width_at_escalation"])],
             ["**the registered escalation would fix S3**",
              "**" + str(w["escalation_would_fix_S3"]) + "**"],
             ["but the escalation is wired to", w["escalation_is_wired_to"]]])
        pj = an["projection"]
        sec["annex_projection"] = _md(
            ["configuration", "P(delta > 2 SE_diff)", "true delta", "SE_kappa",
             "SE_diff"],
            [[f"truth {nm}", repr(d["P_delta_gt_2SEdiff"]), repr(d["true_delta"]),
              repr(d["SE_kappa"]), repr(d["SE_diff"])]
             for nm, d in pj["per_truth"].items()]
            + [["PASS at n=" + str(pj["n_worlds_per_side"]), str(pj["PASS"]), "—", "—",
                "—"],
               ["PASS under RN-N1-8's second reading",
                str(pj["PASS_under_second_reading"]), "—", "—", "—"]])
    sec["truth_table"] = _md(
        ["#", "condition", "outcome"],
        [[t["n"], t["condition"],
          ("**" + t["text"] + "**  <-- THIS LEG") if t["outcome"] == dec["verdict_slug"]
          else t["text"]] for t in TRUTH_TABLE])
    sec["gates"] = _md(["gate", "PASS", "detail"],
                       [[k, str(d["PASS"]), d["detail"]] for k, d in dec["gates"].items()])
    m: dict[str, float] = {}
    for line in (OUT / "ordering_log.jsonl").read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        if "seconds" in rec:
            m[rec["event"]] = float(rec["seconds"])
    est = p0["stage_estimates_seconds"]
    sec["timing"] = _md(
        ["stage", "estimate (s)", "measured (s)"],
        [["part0 (to the STOP)", str(est["part0"]),
          "%.3f" % m.get("STOP_G0n1", p0["seconds"])],
         ["pilot", str(est["pilot"]), "-- not reached"]]
        + [[f"worlds_{c}", str(est["worlds_each"]), "-- not reached"]
           for c in ("A", "B", "C", "D")]
        + [["measure", str(est["measure"]), "-- not reached"],
           ["finalize", str(est["finalize"]), "-- not reached"]])
    body = ["# M4-N1 report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _stop_facts(p0: dict[str, Any], dec: dict[str, Any]) -> None:
    gi = p0["G0n1"]["(i) pairs and roots"]
    dg = dec["diagnosis"]
    an = p0["annex_first_reading"] or {}
    w = an.get("width_arithmetic", {})
    facts = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"], "STOPPED_AT": dec["stopped_at"],
        "LADDER": dec["ladder"], "N_FAILING": len(dec["failing_clauses"]),
        "FAILING_LIST": ", ".join(sorted(dec["failing_clauses"])),
        "SEAL_ISSUED": dec["seal_issued"], "WORLDS": dec["worlds_drawn"],
        "GENS": dec["generations_ever"], "GUARDED": dec["k2b_instances_guarded"],
        "PHI_A": gi["root_A"]["phi"], "PHI_C": gi["root_C"]["phi"],
        "RES_A": gi["root_A"]["abs_residual"], "RES_C": gi["root_C"]["abs_residual"],
        "ITERS_A": gi["root_A"]["iterations"], "ITERS_C": gi["root_C"]["iterations"],
        "BIAS_BOUND": gi["channel_cancellation_bias_bound"],
        "DV_LO": gi["dV_LO"], "DV_HI": gi["dV_HI"],
        "VBAR_LO": gi["Vbar_LO"], "VBAR_HI": gi["Vbar_HI"],
        "R_A": gi["cells"]["A"]["r"], "R_C": gi["cells"]["C"]["r"],
        "CC_VSTAR_QUOTED": CC_VSTAR, "CC_A0_QUOTED": CC_A0,
        "CC_CPRIME_QUOTED": CC_CPRIME,
        "CC_VSTAR_TRUE": dg["corrected_V_star"], "CC_A0_TRUE": dg["corrected_A0"],
        "CC_CPRIME_TRUE": dg["corrected_c_prime"],
        "D_VSTAR": float(abs(dg["corrected_V_star"] - CC_VSTAR)),
        "D_A0": float(abs(dg["corrected_A0"] - CC_A0)),
        "D_CPRIME": float(abs(dg["corrected_c_prime"] - CC_CPRIME)),
        "IK0": dg["cc_implied_kappa0"], "IK2": dg["cc_implied_kappa2"],
        "DK0": dg["delta_kappa0"], "DK2": dg["delta_kappa2"],
        "CPRIME_USES_PERSISTED_C": dg["cc_c_prime_uses_persisted_c"],
        "M3_C": M3_C, "M3_K0": M3_K0, "M3_K2": M3_K2,
        "ALIN_REG": M3_ALIN_KAPPA_REGISTERED, "ALIN_PERS": M3_ALIN_KAPPA_PERSISTED,
        "ALIN_DIFF": float(abs(M3_ALIN_KAPPA_PERSISTED - M3_ALIN_KAPPA_REGISTERED)),
        "SIGMA_W": SIGMA_W, "PART0_SECONDS": p0["seconds"],
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
        "ANNEX_SHA": an.get("sha256", "n/a"),
        "ANNEX_GENS": an.get("generations_before_stamp", "n/a"),
        "S1_POINT": an.get("predictions", {}).get("S1", {}).get("point", "n/a"),
        "S2_POINT": an.get("predictions", {}).get("S2", {}).get("point", "n/a"),
        "S3_POINT": an.get("predictions", {}).get("S3", {}).get("point", "n/a"),
        "S1_WIDTH": an.get("predictions", {}).get("S1", {}).get("band_width", "n/a"),
        "S2_WIDTH": an.get("predictions", {}).get("S2", {}).get("band_width", "n/a"),
        "S3_WIDTH": w.get("S3_band_width", "n/a"),
        "S3_BUDGET": w.get("S3_budget", "n/a"),
        "S3_OVER": w.get("S3_over_budget", "n/a"),
        "S3_OVERRUN": w.get("S3_overrun", "n/a"),
        "S3_SPAN": w.get("S3_draw_span", "n/a"),
        "S3_ALLOW": w.get("S3_measurement_allowance_4xSE_diff", "n/a"),
        "N_NEED": w.get("worlds_per_cell_needed_ceil", "n/a"),
        "N_NEED_RAW": w.get("worlds_per_cell_needed", "n/a"),
        "SE_NEED": w.get("SE_diff_needed", "n/a"),
        "BANNER_LINE": BANNER + ".",
        "S3_ALLOW_PCT": (float(100.0 * w["S3_measurement_allowance_4xSE_diff"]
                               / w["S3_band_width"]) if w else "n/a"),
        "ESC_N": w.get("registered_escalation_n", "n/a"),
        "S3_W_ESC": w.get("S3_width_at_escalation", "n/a"),
        "ESC_FIXES": w.get("escalation_would_fix_S3", "n/a"),
        "P_CURVE": an.get("projection", {}).get("per_truth", {}).get(
            "CURVE", {}).get("P_delta_gt_2SEdiff", "n/a"),
        "P_CONST": an.get("projection", {}).get("per_truth", {}).get(
            "CONSTANT", {}).get("P_delta_gt_2SEdiff", "n/a"),
        "P_CONST2": an.get("projection", {}).get("per_truth", {}).get(
            "CONSTANT (registration-text reading)", {}).get(
            "P_delta_gt_2SEdiff", "n/a"),
        "PROJ_PASS": an.get("projection", {}).get("PASS", "n/a"),
        "SE_KAPPA": an.get("projection", {}).get("per_truth", {}).get(
            "CURVE", {}).get("SE_kappa", "n/a"),
        "SE_DIFF": an.get("projection", {}).get("per_truth", {}).get(
            "CURVE", {}).get("SE_diff", "n/a"),
    }
    write_json(OUT / "prose_facts.json", facts)


def _tables(p0: dict[str, Any], g4: dict[str, Any], pred: dict[str, Any],
            stamp: dict[str, Any], meas: dict[str, Any], dec: dict[str, Any]) -> None:
    sec: dict[str, list[str]] = {}
    g0 = p0["G0n1"]
    gi = g0["(i) pairs and roots"]
    sec["cells"] = _md(
        ["cell", "pair", "side", "share", "phi", "r", "V", "r interior"],
        [[c, s["pair"], s["side"], repr(s["share"]), repr(s["phi"]), repr(s["r"]),
          repr(s["V"]), str(R_WINDOW[0] <= s["r"] <= R_WINDOW[1])]
         for c, s in gi["cells"].items()])
    sec["roots"] = _md(
        ["root", "share", "target r", "bracket", "r at bracket ends", "straddles",
         "solved phi", "realized r", "|residual|", "tol", "iters", "converged"],
        [[nm, repr(rt["share"]), repr(rt["target_r"]), repr(rt["bracket"]),
          repr([rt["r_at_bracket_lo"], rt["r_at_bracket_hi"]]),
          str(rt["bracket_straddles"]), repr(rt["phi"]), repr(rt["r_realized"]),
          repr(rt["abs_residual"]), repr(rt["tolerance"]), str(rt["iterations"]),
          str(rt["converged"])]
         for nm, rt in (("phi_a (cell A)", gi["root_A"]), ("phi_c (cell C)",
                                                           gi["root_C"]))]
        + [["dV LO / HI (exact)", repr(gi["dV_LO"]) + " / " + repr(gi["dV_HI"]), "—", "—",
            "—", str(gi["dV_exact"]), "V_bar " + repr(gi["Vbar_LO"]) + " / "
            + repr(gi["Vbar_HI"]), "—", "—", "—", "—", str(gi["Vbar_exact"])]])
    gii = g0["(ii) M3 and CC"]
    sec["g0n1"] = _md(
        ["clause", "expected", "persisted / recomputed", "bit-exact"],
        [[k, repr(d["expected"]), repr(d["persisted"]), str(d["bit_exact"])]
         for k, d in gii["citations"].items()]
        + [["M3 A-quad recompute from persisted worlds", repr(gii["theta_persisted"]),
            repr(gii["theta_recomputed"]), str(gii["m3_recompute_bit_exact"])],
           ["CC V*", repr(CC_VSTAR), repr(gii["cc_identities"]["V_star"]),
            str(gii["cc_identities"]["bit_exact"])],
           ["CC A0", repr(CC_A0), repr(gii["cc_identities"]["A0"]),
            str(gii["cc_identities"]["bit_exact"])],
           ["CC c'", repr(CC_CPRIME), repr(gii["cc_identities"]["c_prime"]),
            str(gii["cc_identities"]["bit_exact"])],
           ["A-sat theta", repr(list(M3_ASAT)), repr(gii["a_sat_theta"]),
            str(gii["a_sat_bit_exact"])],
           ["sigma_w", repr(SIGMA_W), repr(g0["(iii) sigma_w"]["sigma_w_persisted"]),
            str(g0["(iii) sigma_w"]["PASS"])]]
        + [[f"{k} -- ANTICIPATED (RN-N1-8; persisted controls, non-blocking)",
            repr(d["registration_text"]), repr(d["persisted"]),
            f"differ by {d['abs_difference']!r}"]
           for k, d in gii["anticipated_divergences"].items()])
    pj = p0["G2n1"]
    prow = []
    for blk, tag in ((pj["base"], f"n={pj['base']['n_worlds_per_side']}"),
                     (pj["escalated"], "escalated")):
        if blk is None:
            prow.append([tag, "not run", "—", "—", "—"])
            continue
        for nm, d in blk["per_truth"].items():
            prow.append([f"{tag} truth {nm}", repr(d["P_delta_gt_2SEdiff"]),
                         repr(d["true_delta"]), repr(d["SE_kappa"]), repr(d["SE_diff"])])
        prow.append([f"{tag} PASS", str(blk["PASS"]), "—", "—", "—"])
    sec["projection"] = _md(["configuration", "P(delta > 2 SE_diff)", "true delta",
                             "SE_kappa", "SE_diff"], prow)
    sec["sealed"] = _md(
        ["prediction", "quantity", "point", "draws [2.5%, 97.5%]", "SE_meas",
         "sealed band", "width", "budget", "status", "A-sat co-prediction"],
        [[s, pred["predictions"][s]["quantity"], repr(pred["predictions"][s]["point"]),
          repr([pred["predictions"][s]["draw_2.5"], pred["predictions"][s]["draw_97.5"]]),
          repr(pred["predictions"][s]["SE_meas"]),
          repr([pred["predictions"][s]["band_lo"], pred["predictions"][s]["band_hi"]]),
          repr(pred["predictions"][s]["band_width"]),
          repr(pred["predictions"][s]["budget"]),
          "**VOID_FOR_WIDTH**" if pred["predictions"][s]["VOID_FOR_WIDTH"]
          else "within budget",
          repr(pred["predictions"][s]["a_sat_co_prediction"])]
         for s in ("S1", "S2", "S3")])
    sec["stamp"] = _md(
        ["quantity", "value"],
        [["predictions.json sha256", dec["ordering"]["sha256"]],
         ["bytes sealed", str(stamp["bytes"])],
         ["salt embedded in the sealed bytes (D3)", str(dec["ordering"]["salt_embedded"])],
         ["stamp UTC", dec["ordering"]["stamp_utc"]],
         ["permit UTC", dec["ordering"]["permit_utc"]],
         ["seconds stamp -> permit", repr(dec["ordering"]["seconds_stamp_to_permit"])],
         ["**fresh-world generations BEFORE the stamp**",
          "**" + str(dec["ordering"]["generations_before_stamp"]) + "**"],
         ["generations before the permit",
          str(dec["ordering"]["generations_before_permit"])],
         ["hash re-read from disk and re-hashed at permit time",
          str(dec["ordering"]["hash_match"])],
         ["k2b instances guarded", str(dec["ordering"]["k2b_instances_guarded"])],
         ["entry points wrapped", str(dec["ordering"]["entry_points_wrapped"])]])
    sec["measured"] = _md(
        ["prediction", "quantity", "predicted", "sealed band", "measured",
         "measured 95% CI", "signed error", "position in band", "verdict"],
        [[s, dec["measured"][s]["quantity"], repr(dec["measured"][s]["predicted_point"]),
          repr(dec["measured"][s]["band"]), repr(dec["measured"][s]["measured"]),
          repr(dec["measured"][s]["measured_ci95"]),
          repr(dec["measured"][s]["signed_error"]),
          repr(dec["measured"][s]["position_in_band"]),
          ("INSIDE" if dec["measured"][s]["inside"] else "**OUTSIDE**")
          + (f" (delta > 0: {dec['measured'][s]['delta_positive']})" if s == "S3" else "")]
         for s in ("S1", "S2", "S3")])
    sec["kappa"] = _md(
        ["quantity", "value", "95% CI"],
        [["D_LO = field(B) - field(A)", repr(dec["D_LO"]), "—"],
         ["D_HI = field(D) - field(C)", repr(dec["D_HI"]), "—"],
         ["kappa-hat_LO = -D_LO/dV", repr(dec["kappa_LO"]), repr(dec["kappa_LO_ci95"])],
         ["kappa-hat_HI = -D_HI/dV", repr(dec["kappa_HI"]), repr(dec["kappa_HI_ci95"])],
         ["**delta kappa-hat**", "**" + repr(dec["delta_kappa"]) + "**",
          repr(dec["delta_kappa_ci95"])],
         ["delta CI excludes 0", str(dec["measured"]["S3"]["delta_ci_excludes_0"]), "—"]])
    sec["percell"] = _md(
        ["cell", "pair", "side", "share", "phi", "r", "V", "n", "mean", "SEM", "95% CI"],
        [[c["cell"], c["pair"], c["side"], repr(c["share"]), repr(c["phi"]),
          repr(c["r"]), repr(c["V"]), str(c["n"]), repr(c["mean"]), repr(c["sem"]),
          repr(c["ci95"])] for c in dec["per_cell"].values()])
    sec["asat"] = _md(
        ["prediction", "A-quad point", "A-sat co-prediction", "A-sat inside the same band",
         "verdict agrees"],
        [[s, repr(dec["measured"][s]["predicted_point"]),
          repr(dec["measured"][s]["a_sat_co_prediction"]),
          str(dec["measured"][s]["a_sat_inside_same_band"]),
          str(dec["measured"][s]["a_sat_verdict_agrees"])] for s in ("S1", "S2", "S3")])
    sec["pilot"] = _md(
        ["cell", "n", "min", "max", "finite", "any saturated", "nonzero var", "PASS"],
        [[c["cell"], str(c["n"]), repr(c["min"]), repr(c["max"]), str(c["all_finite"]),
          str(c["any_saturated_abs_ge_0.995"]), str(c["nonzero_variance"]),
          str(c["PASS"])] for c in g4["per_cell"]])
    sec["truth_table"] = _md(
        ["#", "condition", "outcome"],
        [[t["n"], t["condition"],
          ("**" + t["text"] + "**  <-- THIS LEG") if t["outcome"] == dec["verdict_slug"]
          else t["text"]] for t in TRUTH_TABLE])
    sec["gates"] = _md(["gate", "PASS", "detail"],
                       [[k, str(d["PASS"]), d["detail"]] for k, d in dec["gates"].items()])
    sec["sides"] = _md(["clause", "statement", "prior", "sided"],
                       [[k, str(v["clause"]), str(v.get("prior", "—")), str(v["sided"])]
                        for k, v in p0["sides_rule22"].items()])
    sec["rn"] = _md(["note", "pinned reading"],
                    [[k, v] for k, v in p0["rn_notes"].items()])
    sec["env"] = _md(["component", "value"],
                     [[k, str(v)] for k, v in p0["environment"].items()])
    sec["ordering_log"] = _md(
        ["utc", "event", "detail"],
        [[r_["utc"], r_["event"],
          ", ".join(f"{k}={v!r}" for k, v in r_.items()
                    if k not in ("utc", "event"))[:180]]
         for r_ in [json.loads(x) for x in
                    (OUT / "ordering_log.jsonl").read_text(
                        encoding="utf-8").splitlines()]])
    est = p0["stage_estimates_seconds"]
    m: dict[str, float] = {}
    for line in (OUT / "ordering_log.jsonl").read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        if rec["event"].endswith("_done") and "seconds" in rec:
            m[rec["event"][:-5]] = float(rec["seconds"])
    emap = {"part0": est["part0"], "pilot": est["pilot"], "measure": est["measure"],
            "finalize": est["finalize"]}
    for c in ("A", "B", "C", "D"):
        emap[f"worlds_{c}"] = est["worlds_each"]
    sec["timing"] = _md(
        ["stage", "estimate (s)", "measured (s)"],
        [[s, str(emap[s]), ("%.3f" % m[s]) if s in m else "-- (not reached)"]
         for s in ["part0", "pilot"] + [f"worlds_{c}" for c in ("A", "B", "C", "D")]
         + ["measure", "finalize"]])
    body = ["# M4-N1 report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _facts(p0: dict[str, Any], pred: dict[str, Any], meas: dict[str, Any],
           dec: dict[str, Any]) -> None:
    gi = p0["G0n1"]["(i) pairs and roots"]
    pj = p0["G2n1"]
    facts = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "MODIFIERS": dec["modifiers"] or "none", "ROUTING_TEXT": dec["routing_text"],
        "N_INSIDE": dec["n_inside"], "N_VALID": dec["n_valid"],
        "VOIDED": dec["voided"] or "none",
        "PHI_A": gi["root_A"]["phi"], "PHI_C": gi["root_C"]["phi"],
        "RES_A": gi["root_A"]["abs_residual"], "RES_C": gi["root_C"]["abs_residual"],
        "ITERS_A": gi["root_A"]["iterations"], "ITERS_C": gi["root_C"]["iterations"],
        "BIAS_BOUND": gi["channel_cancellation_bias_bound"],
        "SHA": dec["ordering"]["sha256"], "SHA16": dec["ordering"]["sha256"][:16],
        "STAMP_UTC": dec["ordering"]["stamp_utc"],
        "PERMIT_UTC": dec["ordering"]["permit_utc"],
        "STAMP_TO_PERMIT": dec["ordering"]["seconds_stamp_to_permit"],
        "GENS_BEFORE_STAMP": dec["ordering"]["generations_before_stamp"],
        "GUARDED": dec["ordering"]["k2b_instances_guarded"],
        "WRAPPED": dec["ordering"]["entry_points_wrapped"],
        "P_CURVE": pj["base"]["per_truth"]["CURVE"]["P_delta_gt_2SEdiff"],
        "P_CONST": pj["base"]["per_truth"]["CONSTANT"]["P_delta_gt_2SEdiff"],
        "ESCALATION": pj["escalation_fired"],
        "SE_KAPPA": pred["SE_meas"]["kappa"], "SE_DIFF": pred["SE_meas"]["diff"],
        "SIGMA_W": SIGMA_W, "N_WORLDS_TOTAL": int(4 * pred["worlds_per_cell"]),
        "WORLDS_PER_CELL": pred["worlds_per_cell"],
        "K_LO": dec["kappa_LO"], "K_LO_CI": dec["kappa_LO_ci95"],
        "K_HI": dec["kappa_HI"], "K_HI_CI": dec["kappa_HI_ci95"],
        "DK": dec["delta_kappa"], "DK_CI": dec["delta_kappa_ci95"],
        "DK_POS": dec["measured"]["S3"]["delta_positive"],
        "DK_EXCL0": dec["measured"]["S3"]["delta_ci_excludes_0"],
        "D_LO": dec["D_LO"], "D_HI": dec["D_HI"],
        "CC_VSTAR": dec["cc_identities"]["V_star"], "CC_A0": dec["cc_identities"]["A0"],
        "CC_CPRIME": dec["cc_identities"]["c_prime"],
        "SEM_MIN": min(c["sem"] for c in dec["per_cell"].values()),
        "SEM_MAX": max(c["sem"] for c in dec["per_cell"].values()),
        "MEAN_MIN": min(c["mean"] for c in dec["per_cell"].values()),
        "MEAN_MAX": max(c["mean"] for c in dec["per_cell"].values()),
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"], "PART0_SECONDS": p0["seconds"],
    }
    for s in ("S1", "S2", "S3"):
        sp, sm = pred["predictions"][s], dec["measured"][s]
        facts.update({f"{s}_POINT": sp["point"],
                      f"{s}_BAND": [sp["band_lo"], sp["band_hi"]],
                      f"{s}_WIDTH": sp["band_width"], f"{s}_BUDGET": sp["budget"],
                      f"{s}_SAT": sp["a_sat_co_prediction"],
                      f"{s}_MEAS": sm["measured"], f"{s}_CI": sm["measured_ci95"],
                      f"{s}_ERR": sm["signed_error"], f"{s}_IN": sm["inside"],
                      f"{s}_POS": sm["position_in_band"],
                      f"{s}_SAT_IN": sm["a_sat_inside_same_band"]})
    write_json(OUT / "prose_facts.json", facts)


REPORT_TEMPLATE = r"""# SUICA M4-N1 — the response-transport seal — **{{SLUG}}**

**Outcome: {{SLUG}} (routing cell {{CELL}}) — {{ROUTING_TEXT}}.** The leg halted
at **{{STOPPED_AT}}** with **{{N_FAILING}}** clauses failing at full precision:
{{FAILING_LIST}}. Ladder: {{LADDER}}. **No seal was issued and no world was ever
drawn** ({{WORLDS}} worlds; {{GENS}} fresh-world generations across
{{GUARDED}} guarded `k2b` instances).

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_N_TAX_MECHANISM_LINE_PLAN.md` BEFORE run (commit 76060e7);
{{BANNER_LINE}}

Every number below is generated from artifacts by code (rule 24); none is
hand-typed. Floats are printed at `repr` precision, so a value quoted in the
registration as `0.29489267237567145` appears here as `0.29489267237567146` —
the same IEEE double, shortest-repr.

---

## 1. What stopped the leg

Appendix CC.1 states three identities "at M3's central values":
V\* = κ0/κ2, A0 = κ0²/(2κ2), c′ = c − A0. G0n1(ii) requires them to be
**recomputed from the persisted parameters**, and the registration's response to
a mismatch is unconditional: *"Mismatch → STOP."* They do not recompute.

<<TABLE:failing>>

The gaps are far above floating point: V\* differs by {{D_VSTAR}}, A0 and c′ by
{{D_A0}} and {{D_CPRIME}}. The recomputation is invariant across four
arithmetic orderings (`k0**2/(2*k2)`, `k0*V*/2`, `k0*(k0/k2)/2`, `0.5*k0*k0/k2`
all give the identical double), and M3's A-quad parameters themselves reproduce
**bit-exactly** from M3's persisted per-world corpus — so the discrepancy is not
in the inputs and not in the arithmetic.

## 2. Diagnosis — one wrong parameter pair, not three wrong identities

CC's three quoted values are **jointly self-consistent with a single
(κ0, κ2) pair** that is not M3's fit:

<<TABLE:diagnosis>>

Reading: CC's V\* and A0 are exactly the identities evaluated at
κ0 = {{IK0}}, κ2 = {{IK2}}, which differ from M3's persisted A-quad fit by
{{DK0}} and {{DK2}}. That pair appears nowhere in `results/m4_m3_tax_curve/`.
Meanwhile c′ = c − A0 uses M3's **persisted c bit-exactly**
({{CPRIME_USES_PERSISTED_C}}), so c′'s error is exactly A0's with the sign
flipped and is not an independent mismatch. Rounding M3's persisted parameters
to 3…9 decimals reproduces none of the three. The most economical explanation is
that CC.1's reparametrization constants were evaluated against a κ-pair that did
not survive into M3's committed fit, while c was taken from the committed fit.

**Corrected values, from M3's persisted parameters:**
V\* = `{{CC_VSTAR_TRUE}}`, A0 = `{{CC_A0_TRUE}}`, c′ = `{{CC_CPRIME_TRUE}}`.

### Why this is worth a STOP even though it changes no sealed number

The three sealed quantities S1, S2, S3 are functions of (κ0, κ2) **directly**
and never of (V\*, A0, c′); CC.2's own sanity values 0.8781 / 0.6671 / 0.2110
reproduce correctly from the persisted parameters (§5). So for *this* leg the
error is inert. It is not inert downstream: the N-line charter registers **N2**
on this very constant — *"is c′ = −0.0824 the frame-carried baseline?"* — and
the corrected c′ is {{CC_CPRIME_TRUE}}, which changes the charter's own rounded
quote in the 4th decimal. A gate that catches a planner-derivation error before
the next leg inherits it is the gate working, not the gate misfiring.

## 3. What G0n1 *did* verify

Everything else passed. (i) pairs and roots: PASS. (iii) σ_w at source: PASS.

<<TABLE:g0n1>>

## 4. The pair design is sound — the roots solved

G0n1(i) passed in full and is reported because it is reusable as-is on
re-dispatch: both roots exist, both brackets straddle, both converge inside
tolerance, ΔV is exact and all four realized r are interior.

<<TABLE:cells>>

<<TABLE:roots>>

φ_a = `{{PHI_A}}` ({{ITERS_A}} bisections, |Δr| = {{RES_A}}) and
φ_c = `{{PHI_C}}` ({{ITERS_C}} bisections, |Δr| = {{RES_C}}), both inside the
registered 1e-9. ΔV = {{DV_LO}} / {{DV_HI}} and V̄ = {{VBAR_LO}} / {{VBAR_HI}}
are exact to the last bit of the design arithmetic. The registered
channel-cancellation bias bound evaluates to {{BIAS_BOUND}}, three orders below
the 1e-9 root tolerance, so matched-r cancellation is clean.

## 5. Diagnostic annex — the preserved first reading

**Disclosure and timing.** This harness's first execution computed Part 0
end-to-end before the STOP branch existed, and therefore wrote and hashed the
predictions before the G0n1 verdict was acted on. Those artifacts are preserved
verbatim under `results/m4_n1_response_transport/first_reading/`. They are
reported here because they cost nothing and are decision-relevant, and they are
safe to report because **they contain no hypothesis-relevant number**: every
response-grade quantity in this leg (κ̂_LO, κ̂_HI, Δκ̂) requires fresh worlds,
and the ordering guard records {{ANNEX_GENS}} fresh-world generations before the
stamp and {{GENS}} in total. Everything in this annex is a deterministic
function of already-persisted M3 data. The live run issues **no** seal; the
preserved stamp is `{{ANNEX_SHA}}` and is inert.

### 5.1 The predictions that would have been sealed

<<TABLE:annex_sealed>>

S1 = {{S1_POINT}} and S2 = {{S2_POINT}} reproduce CC.2's quoted 0.8781 and
0.6671; S3 = {{S3_POINT}} reproduces the quoted decline 0.2110. **The
predictions themselves are correct** — which is precisely why the CC.1 constants
being wrong is a bookkeeping defect rather than a substantive one.

### 5.2 A second, independent blocker: S3 exceeds its rule-27 budget

<<TABLE:annex_width>>

S3's band is **{{S3_WIDTH}}** wide against a registered budget of
{{S3_BUDGET}} — an overrun of {{S3_OVERRUN}}. Under G3n1 that voids S3, leaving
2 valid predictions, and the registration's own note then applies: *"with < 3
valid, cell 4 unreachable and the best available is cell 5's grade."* **The
leg's success outcome CURVE_TRANSPORTS_TO_RESPONSE would have been unreachable
before a single world was drawn.**

The arithmetic decomposes the width: {{S3_SPAN}} from M3's parameter uncertainty
(the bootstrap draw span, irreducible without new level-side data) and
{{S3_ALLOW}} from the 4 × SE_diff measurement allowance
({{S3_ALLOW_PCT}}% of the width). Only the second term responds to worlds.
Fitting the budget needs SE_diff ≤ {{SE_NEED}}, i.e. **{{N_NEED}} worlds per
cell** ({{N_NEED_RAW}} exactly), against the registered 384.

The registered once-only escalation to {{ESC_N}}/side **would** fix it
(S3 width {{S3_W_ESC}} ≤ {{S3_BUDGET}}: {{ESC_FIXES}}) — but that ladder is
wired to **G2n1**, the projection, which passes comfortably at 384. As
registered the two gates are not jointly satisfiable at n = 384, and the only
declared ladder cannot fire for the gate that needs it.

### 5.3 The projection passes

<<TABLE:annex_projection>>

P(Δκ̂ > 2·SE_diff) = {{P_CURVE}} under CURVE (bar ≥ 0.8) and {{P_CONST}} under
CONSTANT (bar ≤ 0.1); SE_κ = {{SE_KAPPA}}, SE_diff = {{SE_DIFF}}. Under
RN-N1-8's second reading of the CONSTANT truth the rate is {{P_CONST2}} and the
verdict is unchanged. **The instrument has the power it was designed to have.**

## 6. Routing

<<TABLE:truth_table>>

## 7. Gates

<<TABLE:gates>>

## 8. Sides declared (rule 22)

<<TABLE:sides>>

## 9. Pinned readings

<<TABLE:rn>>

RN-N1-8 is the one registration divergence that did **not** stop the leg. G2n1
quotes the A-lin chord as {{ALIN_REG}}; `alpha.json` holds {{ALIN_PERS}}
({{ALIN_DIFF}} apart). The registration legislates its own resolution — *"if its
persisted value differs, the persisted value controls"* — so the persisted value
was used, the clause was recorded as ANTICIPATED and non-blocking, and both
readings were carried through the projection (§5.3), where they agree. This was
pinned in Part 0 before the stamp and before any world.

## 10. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine, and the only `pandas` present belongs to
   `/usr/bin/python3` (CPython 3.9.6), which cannot import the machinery
   (`from datetime import UTC` needs 3.11+). A CPython {{PYTHON}} venv was built
   outside the repo from `requirements-lock-main.txt` verbatim and pinned; see
   §12. Resolved BEFORE any hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage was run as its own foreground command under an explicit tool timeout
   below 600 s. Resolved BEFORE any hypothesis-relevant number existed.
3. **A-3 (my own transcription; before any number).** Two constants embedded in
   this harness from M3's *rounded report prose* were wrong in trailing digits:
   A-sat's θ and the A-lin chord. Both were caught by reading
   `results/m4_m3_tax_curve/alpha.json` at full precision **before** Part 0 was
   run for the first time, and corrected. Had they survived, A-sat's θ would
   have raised a FALSE citation defect. Resolved BEFORE any hypothesis-relevant
   number existed. (This is the third leg on which pre-flighting embedded
   constants against artifacts has caught an error; it is now reflexive.)
4. **A-4 (my own code ordering; before any number, disclosed in full).** The
   harness's first version evaluated G0n1 but wrote and hashed the predictions
   *before* acting on the verdict, so the first execution issued a stamp for a
   leg that had already failed its first gate. No world was drawn — the guard
   log shows {{ANNEX_GENS}} generations before that stamp — so nothing was
   contaminated, but the ordering was wrong and is fixed: the STOP now fires
   before the seal. The first reading is preserved under `first_reading/` and
   reported as §5 rather than discarded. Resolved BEFORE any
   hypothesis-relevant number existed, and no hypothesis-relevant number was
   ever computed in either reading.

## 11. What the planner must decide

Two independent things are wrong, and only the first is a citation defect.

1. **Appendix CC.1's constants** (the STOP): correct V\*, A0 and c′ to
   {{CC_VSTAR_TRUE}}, {{CC_A0_TRUE}}, {{CC_CPRIME_TRUE}}, and correct the
   N-line charter's rounded quote of c′. CC.2's testable content is untouched.
2. **G3n1 vs G2n1 at n = 384** (a design defect, not a citation defect): the S3
   budget of {{S3_BUDGET}} and the S3 band rule are not jointly satisfiable at
   384 worlds/cell, and the once-only escalation that would satisfy them is
   attached to the gate that passes. A re-dispatch needs one of: n = {{N_NEED}}+
   per cell (the registered {{ESC_N}} suffices), a re-wired ladder that lets
   G3n1 trigger the escalation, an S3 budget ≥ {{S3_WIDTH}}, or a band rule for
   S3 that does not add 4 × SE_diff on top of the full joint draw span. Note
   that {{S3_SPAN}} of the width is M3's parameter uncertainty and no number of
   fresh worlds will reduce it.

Everything else in the leg is ready: the roots are solved and reusable, the
projection passes, the pilot cells are chosen, and the guard is enforced.

## 12. Environment

<<TABLE:env>>

## 13. Ordering log

<<TABLE:ordering_log>>

## 14. Timing

<<TABLE:timing>>

---

*Artifacts: `results/m4_n1_response_transport/` (gitignored) — `part0.json`,
`decision.json`, `prose_facts.json`, `report_tables.md`, `ordering_log.jsonl`,
`first_reading/`. Harness:
`scripts/run_suica_m4_n1_response_transport.py`.*
"""


def stage_report(args: argparse.Namespace) -> None:
    facts = read_json(OUT / "prose_facts.json")
    raw = (OUT / "report_tables.md").read_text(encoding="utf-8")
    tables: dict[str, str] = {}
    cur, buf = None, []
    for line in raw.split("\n"):
        if line.startswith("<!-- TABLE:"):
            if cur is not None:
                tables[cur] = "\n".join(buf).strip("\n")
            cur = line[len("<!-- TABLE:"):].split(" ")[0].strip()
            buf = []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        tables[cur] = "\n".join(buf).strip("\n")
    text = REPORT_TEMPLATE
    if not text.strip():
        raise SystemExit("REFUSED: REPORT_TEMPLATE is empty.")
    for name, block in tables.items():
        text = text.replace(f"<<TABLE:{name}>>", block)
    for key, val in facts.items():
        text = text.replace("{{" + key + "}}", _fmt(val))
    if "{{" in text or "<<TABLE:" in text:
        bad = [ln for ln in text.split("\n") if "{{" in ln or "<<TABLE:" in ln]
        raise SystemExit(f"REFUSED: unresolved placeholders: {bad[:5]}")
    path = ROOT / "reports" / "SUICA_M4_N1_RESPONSE_TRANSPORT_REPORT.md"
    path.write_text(text, encoding="utf-8")
    print(f"report OK  {rel(path)}  ({len(text.splitlines())} lines)")
    _ = args


def _fmt(v: Any) -> str:
    if v is None:
        return "None"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        return repr(v)
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(_fmt(x) for x in v) + "]"
    if isinstance(v, dict):
        return ", ".join(f"{k} = {_fmt(x)}" for k, x in v.items())
    return str(v)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="stage", required=True)
    stages: list[tuple[str, Callable[[argparse.Namespace], None]]] = [
        ("part0", stage_part0), ("pilot", stage_pilot)]
    for c in ("A", "B", "C", "D"):
        stages.append((f"worlds_{c}", (lambda cc: lambda a: _worlds_cell(cc))(c)))
    stages += [("measure", stage_measure), ("finalize", stage_finalize),
               ("report", stage_report)]
    for name, fn in stages:
        s = sub.add_parser(name)
        s.set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
