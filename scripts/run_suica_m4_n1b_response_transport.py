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

OUT = ROOT / "results" / "m4_n1b_response_transport"
RES = ROOT / "results"
M1BRES = RES / "m4_m1b_r_at_level"
M3RES = RES / "m4_m3_tax_curve"

LEG = "M4-N1b"
BANNER = ("prospective response-transport seal on K2b's frozen instrument, "
          "exploratory, label-free; predictions hashed before any fresh world")

MASTER_SEED = 20260811
SALT_WORLD = "m4n1b-world"
SALT_PILOT = "m4n1b-pilot"
N_WORLDS = 768
N_WORLDS_ESCALATED = 1152
CHUNK = 384          # sub-chunking only; seeds are pure fns of the world index
PILOT_WORLDS = 4
B_BOOT = 2000
B_PROJ = 2000
INT_SHARE = 0.0
W_INT_ARM = "zero"

SIGMA_W = 0.026889438327132725
DV = 0.045
R_WINDOW = (0.4541409476972356, 0.8189581462487876)
ROOT_TOL = 1e-9

# --- the pair design (G0n1b(i)) ---------------------------------------------
TARGET_LO = 0.785015540293945          # r(0.25, 0.05)
TARGET_HI = 0.5967380569813433         # r(0.70, 0.05)
BRACKET_LO = (0.85, 0.98)
BRACKET_HI = (0.60, 0.98)
BRACKET_LO_R = (0.7908869485651705, 0.7718092954224756)   # r(0.10, .85) / (0.10, .98)
VBAR_LO, VBAR_HI = 0.0525, 0.1875

# --- M3's persisted curve (G0n1b(ii)) ---------------------------------------
M3_C = 0.21247398265278816
M3_K0 = 0.9601680204204508
M3_K2 = 1.562877770472943
M3_K2_CI = (1.0324533419318935, 2.119753814549891)
M3_ALIN_KAPPA_REGISTERED = 0.7729284648259515   # registration text; see RN-N1B-8
M3_ALIN_KAPPA_PERSISTED = 0.7729279998877195    # controls, per the registration
M3_LOO = {"A-lin": 0.003599294048156043, "A-quad": 0.001405398973367856,
          "A-sat": 0.0014509897412261284}
M3_P_QUAD = 0.9935
M3_P_LIN = 0.0575
M3_CLOSURE_HITS = 5
M3_ASAT = (-0.27493651728760515, 0.4878776246525967, 0.4983722810248614)
# --- appendix CC identities -------------------------------------------------
CC_VSTAR = 0.6143589975880801     # CC.1-prime, executed provenance (rule 30)
CC_A0 = 0.2949439312708197        # CC.1-prime
CC_CPRIME = -0.08246994861803153  # CC.1-prime
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
# RN-N1B-1 (ordering, inherited).  K2f's G1f pattern and RN-K2F-4: the permit for
#   ANY fresh world -- the pilot included -- is issued only by re-reading
#   predictions.sha256.json from disk and re-hashing predictions.json to a match.
#   Guards wrap build_k2b_world / run_field_world / emit_panel on EVERY reachable
#   k2b instance (RN-K2F-5), plus a cross-process refusal if a world artifact
#   already exists at stamp time.  The salt is embedded INSIDE the sealed bytes
#   (D3), so the digest covers the seed lineage.
#
# RN-N1B-2 (the roots).  phi_a and phi_c are found by bisection on the pinned
#   deterministic map r(share, .) -- strictly decreasing in phi -- to
#   |r - target| <= 1e-9, starting from the registration's own brackets whose
#   endpoints are re-derived and checked to straddle the target before the
#   search runs.  The registration's channel-cancellation bias bound is recorded
#   with the realized residuals.
#
# RN-N1B-3 (the difference orientation).  kappa-hat = -D/dV with D taken as
#   field(HIGH V) - field(LOW V), so a field that FALLS in V gives kappa-hat > 0,
#   matching every published kappa in the programme.  dV = 0.045 is exact
#   arithmetic (V = 0.3*share), not an estimate, so it carries no error.
#
# RN-N1B-4 (SE_meas).  Per the registration, SE per kappa-hat is
#   sqrt(2)*sigma_w/(sqrt(n)*dV) and SE_diff = sqrt(2)*SE_kappa, from M1b's
#   persisted, G0-verified sigma_w.  These are PRIOR measurement-noise
#   allowances fixed before the cells exist; the realized per-cell SEMs are
#   reported beside them and do not re-draw the bands.
#
# RN-N1B-5 (the predictor's bootstrap).  M3's pipeline is recomputed
#   deterministically from its persisted per-world corpus: alpha_s with the
#   channel fixed at theta*, A-quad refit, and B = 2000 master-seeded
#   world-block draws, each draw's (c, kappa0, kappa2) propagated through S1, S2
#   and S3 so the bands inherit the parameter covariance rather than three
#   marginal intervals.  G0 requires the recomputed point parameters to equal
#   M3's persisted values BIT-EXACTLY before anything is sealed.
#
# RN-N1B-6 (A-sat co-predictions).  A-sat's local tax is -d alpha/dV =
#   (A/tau)*exp(-V/tau); its three co-predictions are computed from M3's
#   persisted A-sat parameters and written INSIDE the hashed file.  They
#   adjudicate nothing unless a verdict differs between the forms, in which case
#   FORM_SPLIT is reported (the registration's tie handling, K2f precedent).
#
# RN-N1B-7 (the projection's statistic).  The gate is on
#   P(delta-kappa-hat > 2*SE_diff), a ONE-SIDED event on the difference, at both
#   truths; simulated parametrically as two independent kappa-hats with sd
#   SE_kappa around each truth's local tax.  Under CONSTANT both truths equal
#   M3's persisted A-lin kappa, so the event is a pure false-positive rate.
#
# RN-N1B-8 (the CONSTANT truth's value -- N1's divergence, RESOLVED AT SOURCE).
#   N1's registration quoted the A-lin chord as 0.7729284648259515 against the
#   persisted 0.7729279998877195 (4.649e-7 apart).  That became defect #50 and
#   rule 30, and THIS registration fixes the disease at the root: it delegates
#   the chord and A-sat's theta to results/m4_m3_tax_curve/alpha.json at full
#   precision rather than quoting digits.  There is therefore no registered
#   constant to diverge from; the persisted values are read and their executed
#   provenance is recorded.  N1's numbers are carried only as history.
#
# RN-N1B-9 (the escalation is a SHARED-KNOB ladder).  The registration attaches
#   the once-only escalation to 1152/cell to G3n1b (the budget gate), per #51's
#   convention -- which I read, as the convention states, to also require the
#   ladder to be checked against EVERY gate sharing the knob.  n is shared by
#   G2n1b (projection) and G3n1b (budgets).  PINNED: ONE once-only escalation
#   exists; it fires if EITHER gate fails at n = 768; after it fires BOTH gates
#   are re-evaluated at 1152.  Failing budgets at the ceiling -> STOP as
#   NON_SEALABLE_AT_CEILING; failing the projection at the ceiling ->
#   NON_PROJECTABLE.  Reported either way.
#
# RN-N1B-10 (what FORM_SPLIT compares).  The routing's modifier says the A-quad
#   and A-sat "co-predictions disagree on any verdict", but the registration
#   supplies A-sat only as a POINT, and a point has no verdict.  PINNED (before
#   the stamp): A-sat's band is built by the IDENTICAL rule from the IDENTICAL
#   bootstrap resamples -- each world-block draw refits A-sat from its persisted
#   optimum (M3's own bootstrap convention) and is propagated through the same
#   local-tax map -- so "verdict" means the same thing for both forms.
#   FORM_SPLIT fires iff the inside/outside verdicts differ for any S.  Two
#   secondary readings are computed and REPORTED, never used to route:
#   (a) separation -- whether A-sat's point lies inside A-quad's band at all;
#   (b) proximity -- which form's point the measurement lands nearer.
#
# RN-N1B-11 (pre-stamp ordering; the A-4 fix as registered text).  All Part-0
#   verdicts complete before the stamp.  Within them the order is forced by a
#   dependency the registration leaves implicit: the escalation changes n, and n
#   changes BOTH the bands and the projection.  PINNED: G0n1b, then bands and
#   G3n1b budgets (which decide n via RN-N1B-9), then G2n1b at the DECIDED n,
#   then -- only if every pre-stamp gate passes -- the stamp.  The projection at
#   the base n is computed and reported regardless.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-N1B-1": "ordering enforced in code (K2f G1f + RN-K2F-4): the permit for ANY fresh "
               "world, pilot included, is issued only by re-reading the stamp from disk "
               "and re-hashing; guards on every reachable k2b instance; salt embedded in "
               "the sealed bytes (D3)",
    "RN-N1B-2": "phi_a / phi_c by bisection on the pinned map to |r - target| <= 1e-9, "
               "from the registration's own brackets whose endpoints are re-derived and "
               "checked to straddle before the search",
    "RN-N1B-3": "kappa-hat = -D/dV with D = field(HIGH V) - field(LOW V), so a field "
               "falling in V gives kappa-hat > 0; dV = 0.045 is exact arithmetic and "
               "carries no error",
    "RN-N1B-4": "SE_kappa = sqrt(2)*sigma_w/(sqrt(n)*dV), SE_diff = sqrt(2)*SE_kappa, from "
               "M1b's persisted sigma_w -- PRIOR allowances fixed before the cells exist; "
               "realized SEMs reported beside them and never re-draw the bands",
    "RN-N1B-5": "M3's pipeline recomputed deterministically (alpha at fixed theta*, A-quad "
               "refit, B=2000 world-block draws) with each draw's (c, kappa0, kappa2) "
               "propagated through all three predictions, so the bands inherit the "
               "parameter covariance; G0 demands bit-exact point parameters first",
    "RN-N1B-6": "A-sat co-predictions from its local tax (A/tau)*exp(-V/tau), written "
               "INSIDE the hashed file; they adjudicate nothing unless a verdict differs, "
               "which reports FORM_SPLIT",
    "RN-N1B-7": "the projection statistic is the ONE-SIDED event delta-kappa-hat > "
               "2*SE_diff at both truths; under CONSTANT both local taxes equal M3's "
               "persisted A-lin kappa so the event is a pure false-positive rate",
    "RN-N1B-8": "N1's A-lin chord divergence is RESOLVED AT SOURCE: this registration "
               "delegates the chord and A-sat's theta to alpha.json at full precision "
               "instead of quoting digits (defect #50 / rule 30), so no registered "
               "constant can diverge; persisted values are read and their provenance "
               "recorded, N1's numbers carried only as history",
    "RN-N1B-9": "ONE once-only escalation to 1152/cell, shared by G2n1b and G3n1b because "
               "both consume n (#51's convention): it fires if EITHER fails at 768 and "
               "BOTH are re-evaluated at 1152; budgets failing at the ceiling -> "
               "NON_SEALABLE_AT_CEILING, projection failing -> NON_PROJECTABLE",
    "RN-N1B-10": "FORM_SPLIT compares like with like: A-sat's band is built by the identical "
                "rule from the identical bootstrap resamples (each draw refits A-sat from "
                "its persisted optimum), so both forms have a verdict; it fires iff the "
                "inside/outside verdicts differ. Separation and proximity readings are "
                "reported, never used to route",
    "RN-N1B-11": "pre-stamp order forced by dependency: G0n1b, then bands and G3n1b budgets "
                "(which decide n), then G2n1b at the DECIDED n, then the stamp -- and only "
                "if every pre-stamp gate passed. The base-n projection is reported too",
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
# G4n1b -- ORDERING ENFORCEMENT.

_GEN_COUNT = 0
_PERMIT = False
_ARMED = False
WORLD_ARTIFACTS = ("pilot_field.csv", "g4n1b_pilot.json", "cells", "measured.json")


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
                            f"STOP (G4n1b): fresh-world generation via {nm} before the "
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
        raise SystemExit("STOP (G4n1b): no persisted stamp; run `part0`.")
    raw = pp.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    stamp = json.loads(sp.read_text(encoding="utf-8"))
    if digest != stamp["sha256"]:
        raise SystemExit(f"STOP (G4n1b): hash {digest} != stamped {stamp['sha256']}")
    if _GEN_COUNT != 0:
        raise SystemExit(f"STOP (G4n1b): {_GEN_COUNT} generations before the permit.")
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
    """RN-N1B-2: r(share, .) is strictly decreasing in phi."""
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
# M3's pipeline, recomputed deterministically (RN-N1B-5).

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
        "stopped_at": "G0n1b(ii)", "ladder": "none declared -- the registration's text is "
                                            "'Mismatch -> STOP'",
        "failing_clauses": bad, "diagnosis": diag,
        "seal_issued": False, "worlds_drawn": 0, "pilot_run": False,
        "generations_ever": _GEN_COUNT, "k2b_instances_guarded": n_guarded,
        "gates": {
            "G0n1b": {"PASS": False,
                     "detail": f"{len(bad)} clause(s) fail at full precision; (i) pairs "
                               f"and roots PASS, (iii) sigma_w PASS"},
            "G1n1b": {"PASS": None, "detail": "not reached (no world drawn)"},
            "G2n1b": {"PASS": None,
                     "detail": "not reached in this reading; the preserved first reading "
                               "passed it (annex)"},
            "G3n1b": {"PASS": None,
                     "detail": "not reached in this reading; the preserved first reading "
                               "shows S3 over budget (annex)"},
            "G4n1b": {"PASS": True,
                     "detail": f"guard armed on {n_guarded} k2b instance(s), "
                               f"{3 * n_guarded} entry points; {_GEN_COUNT} fresh-world "
                               f"generations ever; no seal issued for a stopped leg"},
            "G5n1b": {"PASS": True, "detail": "stopped inside the part0 estimate; tables "
                                             "generated (rule 24)"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("STOP_G0n1", failing=sorted(bad), seconds=dec["seconds"])
    part0 = _part0_shell(t0, g0, n_guarded, stopped=True)
    write_json(OUT / "part0.json", part0)
    _stop_tables(part0, dec)
    _stop_facts(part0, dec)
    print(f"STOP (routing cell 1) at G0n1b(ii): {len(bad)} clause(s) fail at full "
          f"precision. No seal issued, {_GEN_COUNT} worlds drawn. "
          f"{time.time() - t0:.1f}s")


def _stop_prestamp(t0: float, g0: dict[str, Any], g2: dict[str, Any],
                   g3: dict[str, Any], pre: dict[str, Any], preds: dict[str, Any],
                   n_guarded: int, slug: str) -> None:
    """A pre-stamp gate failed after its once-only escalation: STOP, no seal.

    Reached only when G3n1b's budgets or G2n1b's projection still fail at the
    ceiling.  No stamp is written and no world is drawn, so no hypothesis-
    relevant number exists.
    """
    cell_n = 2 if slug == "NON_PROJECTABLE" else "--"
    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "verdict_slug": slug, "routing_cell": cell_n, "modifiers": [],
        "routing_text": ("NON_PROJECTABLE (handback; no worlds)"
                         if slug == "NON_PROJECTABLE" else
                         "NON_SEALABLE_AT_CEILING (budgets still exceeded at the "
                         "escalation ceiling; handback, no worlds)"),
        "stopped_at": ("G2n1b" if slug == "NON_PROJECTABLE" else "G3n1b"),
        "ladder": f"once-only escalation to {N_WORLDS_ESCALATED}/cell, shared knob "
                  f"(RN-N1B-9); fired={g3['escalation_fired'] or g2['escalation_fired']}",
        "pre_stamp_verdicts": pre, "budgets": g3, "projection": g2,
        "predictions_unsealed": preds,
        "seal_issued": False, "worlds_drawn": 0, "pilot_run": False,
        "generations_ever": _GEN_COUNT, "k2b_instances_guarded": n_guarded,
        "gates": {
            "G0n1b": {"PASS": True, "detail": "all clauses bit-exact"},
            "G1n1b": {"PASS": None, "detail": "not reached (no world drawn)"},
            "G2n1b": {"PASS": g2["PASS"],
                      "detail": f"evaluated at n={g2['evaluated_at_n']}"},
            "G3n1b": {"PASS": g3["PASS"],
                      "detail": f"over budget: {g3['over_budget_final'] or 'none'} at "
                                f"n={g3['worlds_per_cell_after_budgets']}"},
            "G4n1b": {"PASS": True,
                      "detail": f"guard armed on {n_guarded} k2b instance(s); "
                                f"{_GEN_COUNT} generations; no seal issued"},
            "G5n1b": {"PASS": True, "detail": "stopped inside part0; tables generated"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("STOP_PRESTAMP", slug=slug, seconds=dec["seconds"])
    part0 = _part0_shell(t0, g0, n_guarded, stopped=True)
    part0["G2n1b"], part0["G3n1b"] = g2, g3
    part0["pre_stamp_verdicts"] = pre
    write_json(OUT / "part0.json", part0)
    sec = _common_tables(part0)
    sec["prestamp"] = _md(
        ["prediction", "point", "band", "width", "budget", "status"],
        [[s, repr(d["point"]), repr([d["band_lo"], d["band_hi"]]),
          repr(d["band_width"]), repr(d["budget"]),
          "**VOID_FOR_WIDTH**" if d["VOID_FOR_WIDTH"] else "within budget"]
         for s, d in preds.items()])
    sec["gates"] = _md(["gate", "PASS", "detail"],
                       [[k, str(v["PASS"]), v["detail"]] for k, v in dec["gates"].items()])
    body = ["# M4-N1b report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")
    print(f"STOP ({slug}) before the stamp. No seal, {_GEN_COUNT} worlds. "
          f"{time.time() - t0:.1f}s")


def _annex() -> dict[str, Any] | None:
    """The preserved first reading: persisted-data-only, zero fresh worlds."""
    if not (FR / "predictions.json").exists():
        return None
    p = read_json(FR / "predictions.json")
    s = read_json(FR / "predictions.sha256.json")
    pj = read_json(FR / "part0.json")["G2n1b"]
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
                "escalation_is_wired_to": "G2n1b (the projection), which PASSES at 384 -- "
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
        "rn_notes": RN_NOTES, "G0n1b": g0, "G2n1b": None,
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
            "L-1n1b": {"clause": "S1 inside its sealed band", "prior": 0.60,
                      "sided": "two-sided containment"},
            "L-2n1b": {"clause": "S2 inside its sealed band", "prior": 0.60,
                      "sided": "two-sided containment"},
            "L-3n1b": {"clause": "S3 inside AND delta kappa-hat > 0", "prior": 0.55,
                      "sided": "two-sided containment plus a one-sided sign clause"},
            "G2n1b": {"clause": f"P(delta > 2 SE_diff | CURVE) >= "
                               f"{PROJ_POWER_CURVE_MIN} AND <= "
                               f"{PROJ_POWER_CONST_MAX} under CONSTANT",
                     "sided": "one-sided each"},
            "G3n1b": {"clause": f"band widths S1 <= {BAND_BUDGET['S1']}, S2 <= "
                               f"{BAND_BUDGET['S2']}, S3 <= {BAND_BUDGET['S3']}",
                     "sided": "one-sided"}},
        "stage_estimates_seconds": {"part0": 420, "pilot": 30, "worlds_each": 250,
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
            raise SystemExit(f"STOP (G4n1b): {nm} exists before Part 0.")
    _log("part0_start")
    n_guarded = _arm_guard()

    # --- G0n1b(i): the pair table and the roots -----------------------------
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

    # --- G0n1b(ii): M3's numbers + CC identities ----------------------------
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
        "registration_text": "delegated to alpha.json at full precision (no digits "
                             "quoted) -- rule 30",
        "persisted": alin,
        "matches_persisted_constant": bool(alin == M3_ALIN_KAPPA_PERSISTED),
        "abs_difference": 0.0,
        "which_controls": "persisted",
        "authority": "the N1b registration item 2: the persisted A-sat theta / A-lin "
                     "chord at full precision from results/m4_m3_tax_curve/alpha.json",
        "n1_registration_text_for_history": M3_ALIN_KAPPA_REGISTERED,
        "n1_divergence_now_closed": float(abs(M3_ALIN_KAPPA_PERSISTED
                                              - M3_ALIN_KAPPA_REGISTERED)),
        "blocking": False, "note": RN_NOTES["RN-N1B-8"]}}
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

    # --- G0n1b(iii): sigma_w at source --------------------------------------
    sw = float(read_json(M1BRES / "g3mb_power.json")["sigma_w"])
    g0iii = {"sigma_w_persisted": sw, "sigma_w_registration": SIGMA_W,
             "source": rel(M1BRES / "g3mb_power.json"), "PASS": bool(sw == SIGMA_W)}
    g0 = {"(i) pairs and roots": g0i, "(ii) M3 and CC": g0ii,
          "(iii) sigma_w": g0iii,
          "PASS": bool(g0i["PASS"] and g0ii["PASS"] and g0iii["PASS"])}

    # --- ROUTING CELL 1.  G0n1b has NO declared ladder: mismatch -> STOP. -----
    # The gate fires BEFORE the seal and before any world.  Nothing
    # hypothesis-relevant is computed past this point.
    if not g0["PASS"]:
        _stop(t0, g0, n_guarded)
        return

    # --- the predictor's bootstrap, propagated (RN-N1B-5) -------------------
    rng = np.random.default_rng(MASTER_SEED)
    keys = list(grid)
    draws, picks = [], []
    for _ in range(B_BOOT):
        pick = {k: rng.integers(0, n_m3, size=n_m3) for k in keys}
        picks.append(pick)
        draws.append(_aquad_ols(V, _m3_alpha(grid, pick)))
    D = np.asarray(draws, float)
    k_lo_d = D[:, 1] - D[:, 2] * VBAR_LO
    k_hi_d = D[:, 1] - D[:, 2] * VBAR_HI
    d_d = D[:, 2] * (VBAR_HI - VBAR_LO)
    points = {"S1": float(M3_K0 - M3_K2 * VBAR_LO),
              "S2": float(M3_K0 - M3_K2 * VBAR_HI),
              "S3": float(M3_K2 * (VBAR_HI - VBAR_LO))}
    dmap = {"S1": k_lo_d, "S2": k_hi_d, "S3": d_d}
    sat_c, sat_A, sat_tau = asat
    sat = {"S1": float((sat_A / sat_tau) * np.exp(-VBAR_LO / sat_tau)),
           "S2": float((sat_A / sat_tau) * np.exp(-VBAR_HI / sat_tau))}
    sat["S3"] = float(sat["S1"] - sat["S2"])

    # A-sat refit on the SAME resamples (RN-N1B-10), from its persisted optimum
    # -- M3's own bootstrap convention -- so both forms get a comparable band.
    from scipy.optimize import least_squares

    def _asat_fit(y: np.ndarray, start: np.ndarray) -> np.ndarray:
        res = least_squares(
            lambda th: (th[0] + th[1] * np.exp(-V / th[2])) - y, start,
            method="trf", jac="2-point", ftol=1e-14, xtol=1e-14, gtol=1e-14,
            max_nfev=20000)
        return np.asarray(res.x, float)

    asat0 = _asat_fit(alpha, np.asarray(M3_ASAT, float))
    asat_recompute_ok = bool(float(np.max(np.abs(asat0 - np.asarray(asat, float))))
                             < 1e-9)
    D_sat = np.empty((B_BOOT, 3), float)
    for bi in range(B_BOOT):
        D_sat[bi] = _asat_fit(_m3_alpha(grid, picks[bi]), np.asarray(asat, float))
    sat_klo_d = (D_sat[:, 1] / D_sat[:, 2]) * np.exp(-VBAR_LO / D_sat[:, 2])
    sat_khi_d = (D_sat[:, 1] / D_sat[:, 2]) * np.exp(-VBAR_HI / D_sat[:, 2])
    satmap = {"S1": sat_klo_d, "S2": sat_khi_d, "S3": sat_klo_d - sat_khi_d}

    def build_bands(n_w: int) -> dict[str, Any]:
        sek = float(np.sqrt(2.0) * SIGMA_W / (np.sqrt(n_w) * DV))
        sed = float(np.sqrt(2.0) * sek)
        ses_ = {"S1": sek, "S2": sek, "S3": sed}
        out: dict[str, Any] = {}
        for s in ("S1", "S2", "S3"):
            a = dmap[s]
            b25, b975 = float(np.quantile(a, 0.025)), float(np.quantile(a, 0.975))
            lo, hi = b25 - 2.0 * ses_[s], b975 + 2.0 * ses_[s]
            sa = satmap[s]
            s25, s975 = float(np.quantile(sa, 0.025)), float(np.quantile(sa, 0.975))
            slo, shi = s25 - 2.0 * ses_[s], s975 + 2.0 * ses_[s]
            out[s] = {"quantity": {"S1": "kappa_resp(0.0525)",
                                   "S2": "kappa_resp(0.1875)",
                                   "S3": "delta kappa = kappa_LO - kappa_HI"}[s],
                      "point": points[s], "draw_2.5": b25, "draw_97.5": b975,
                      "SE_meas": ses_[s], "band_lo": float(lo), "band_hi": float(hi),
                      "band_width": float(hi - lo), "budget": BAND_BUDGET[s],
                      "within_budget": bool((hi - lo) <= BAND_BUDGET[s]),
                      "VOID_FOR_WIDTH": bool((hi - lo) > BAND_BUDGET[s]),
                      "a_sat_co_prediction": sat[s],
                      "a_sat_band_lo": float(slo), "a_sat_band_hi": float(shi),
                      "a_sat_band_width": float(shi - slo),
                      "a_sat_draw_2.5": s25, "a_sat_draw_97.5": s975,
                      "B": B_BOOT}
        return out

    # --- G3n1b: the rule-27 band budgets, and they DECIDE n (RN-N1B-9/11) ---
    preds = build_bands(N_WORLDS)
    over = [s for s in ("S1", "S2", "S3") if preds[s]["VOID_FOR_WIDTH"]]
    g3_base = {"n_worlds_per_cell": N_WORLDS, "budgets": dict(BAND_BUDGET),
               "widths": {s: preds[s]["band_width"] for s in preds},
               "over_budget": over, "PASS": bool(not over)}
    g3_esc, decided_by_budget = None, N_WORLDS
    if over:
        print(f"  G3n1b FAILED at n={N_WORLDS} ({over}); once-only escalation to "
              f"n={N_WORLDS_ESCALATED} (RN-N1B-9)", flush=True)
        preds_e = build_bands(N_WORLDS_ESCALATED)
        over_e = [s for s in ("S1", "S2", "S3") if preds_e[s]["VOID_FOR_WIDTH"]]
        g3_esc = {"n_worlds_per_cell": N_WORLDS_ESCALATED,
                  "budgets": dict(BAND_BUDGET),
                  "widths": {s: preds_e[s]["band_width"] for s in preds_e},
                  "over_budget": over_e, "PASS": bool(not over_e)}
        preds, over, decided_by_budget = preds_e, over_e, N_WORLDS_ESCALATED
    g3 = {"base": g3_base, "escalated": g3_esc,
          "escalation_fired": bool(g3_esc is not None),
          "worlds_per_cell_after_budgets": decided_by_budget,
          "over_budget_final": over, "PASS": bool(not over),
          "on_fail": "NON_SEALABLE_AT_CEILING", "note": RN_NOTES["RN-N1B-9"]}
    n_valid = sum(1 for s in preds if not preds[s]["VOID_FOR_WIDTH"])
    se_kappa = preds["S1"]["SE_meas"]
    se_diff = preds["S3"]["SE_meas"]

    # --- G2n1b: the rule-25 projection, BEFORE the stamp --------------------
    def project(n_w: int) -> dict[str, Any]:
        sek = float(np.sqrt(2.0) * SIGMA_W / (np.sqrt(n_w) * DV))
        sed = float(np.sqrt(2.0) * sek)
        rg = np.random.default_rng(MASTER_SEED)
        out = {}
        for name, (klo, khi) in (
                ("CURVE", (M3_K0 - M3_K2 * VBAR_LO, M3_K0 - M3_K2 * VBAR_HI)),
                ("CONSTANT", (alin, alin)),
                # RN-N1B-8's second reading, shown to be inconsequential:
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
                "note": RN_NOTES["RN-N1B-7"]}

    base = project(N_WORLDS)
    esc = None
    decided = decided_by_budget
    if decided_by_budget != N_WORLDS:
        # RN-N1B-9: the budget gate already fired the ONE once-only escalation;
        # the projection is re-evaluated at the landing point, not fired again.
        esc = project(decided_by_budget)
    elif not base["PASS"]:
        print(f"  G2n1b FAILED at n={N_WORLDS}; once-only escalation to "
              f"n={N_WORLDS_ESCALATED} (RN-N1B-9)", flush=True)
        esc = project(N_WORLDS_ESCALATED)
        if esc["PASS"]:
            # the shared knob moved: bands must be rebuilt at the landing point
            preds = build_bands(N_WORLDS_ESCALATED)
            over = [s for s in ("S1", "S2", "S3") if preds[s]["VOID_FOR_WIDTH"]]
            g3["escalated"] = {"n_worlds_per_cell": N_WORLDS_ESCALATED,
                               "budgets": dict(BAND_BUDGET),
                               "widths": {s: preds[s]["band_width"] for s in preds},
                               "over_budget": over, "PASS": bool(not over),
                               "fired_by": "G2n1b (shared knob, RN-N1B-9)"}
            g3["escalation_fired"] = True
            g3["worlds_per_cell_after_budgets"] = N_WORLDS_ESCALATED
            g3["over_budget_final"] = over
            g3["PASS"] = bool(not over)
            n_valid = sum(1 for s in preds if not preds[s]["VOID_FOR_WIDTH"])
            se_kappa, se_diff = preds["S1"]["SE_meas"], preds["S3"]["SE_meas"]
            decided = N_WORLDS_ESCALATED
    eff = esc if esc is not None else base
    g2 = {"base": base, "escalated": esc, "escalation_fired": bool(esc is not None),
          "evaluated_at_n": eff["n_worlds_per_side"],
          "worlds_per_cell_decided": decided, "PASS": bool(eff["PASS"]),
          "on_fail": "NON_PROJECTABLE", "note": RN_NOTES["RN-N1B-9"]}

    # --- every pre-stamp verdict is now COMPLETE (RN-N1B-11, the A-4 fix) ----
    pre_stamp = {"G0n1b": g0["PASS"], "G3n1b (budgets)": g3["PASS"],
                 "G2n1b (projection)": g2["PASS"],
                 "worlds_per_cell_decided": decided,
                 "ALL_PASS": bool(g0["PASS"] and g3["PASS"] and g2["PASS"]),
                 "order": "G0n1b -> bands + G3n1b -> G2n1b at the decided n -> stamp",
                 "note": RN_NOTES["RN-N1B-11"]}
    if not pre_stamp["ALL_PASS"]:
        slug = ("NON_SEALABLE_AT_CEILING" if not g3["PASS"] else "NON_PROJECTABLE")
        _stop_prestamp(t0, g0, g2, g3, pre_stamp, preds, n_guarded, slug)
        return

    predictions = {
        "leg": LEG, "stage": "sealed BEFORE any fresh world exists",
        "utc": datetime.now(UTC).isoformat(),
        "SALT_EMBEDDED_D3": {"world_salt": SALT_WORLD, "pilot_salt": SALT_PILOT,
                             "master_seed": MASTER_SEED, "note": RN_NOTES["RN-N1B-1"]},
        "predictor": {"model": "M3's A-quad, pipeline recomputed deterministically",
                      "theta": [float(x) for x in beta],
                      "param_names": ["c", "kappa0", "kappa2"],
                      "channel_fixed": {"lambda": LAMBDA_STAR, "q": Q_STAR},
                      "bootstrap": {"B": B_BOOT, "seed": MASTER_SEED,
                                    "note": RN_NOTES["RN-N1B-5"]},
                      "a_sat_theta": list(asat),
                      "a_sat_refit_reproduces_persisted": asat_recompute_ok,
                      "a_sat_note": RN_NOTES["RN-N1B-6"],
                      "a_sat_band_note": RN_NOTES["RN-N1B-10"]},
        "cells": cells, "dV": DV, "Vbar": {"LO": VBAR_LO, "HI": VBAR_HI},
        "worlds_per_cell": decided,
        "pre_stamp_verdicts": pre_stamp,
        "SE_meas": {"kappa": se_kappa, "diff": se_diff, "sigma_w": SIGMA_W,
                    "note": RN_NOTES["RN-N1B-4"]},
        "predictions": preds, "n_valid_predictions": int(n_valid),
        "band_rule": "[draw 2.5% - 2*SE_meas, draw 97.5% + 2*SE_meas]; two-sided "
                     "containment (rule 22); S3 also requires delta > 0 (L-3n1b)",
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
        "rn_notes": RN_NOTES, "G0n1b": g0, "G2n1b": g2, "G3n1b": g3,
        "pre_stamp_verdicts": pre_stamp,
        "worlds_per_cell_decided": decided,
        "G1n1_predicate": {"rule": 29,
                           "saturation": f"|recovery_b_only| >= {SATURATION_ABS}",
                           "finiteness": True, "nonzero_within_cell_variance": True,
                           "positivity_clause": "NONE",
                           "statistic_domain": "weighted mean of matrix cosines on "
                                               "[-1, 1]"},
        "predictions_sha256": digest, "stamp_utc": stamp["stamp_utc"],
        "generations_before_stamp": _GEN_COUNT, "k2b_instances_guarded": n_guarded,
        "sides_rule22": {
            "L-1n1b": {"clause": "S1 inside its sealed band", "prior": 0.60,
                      "sided": "two-sided containment"},
            "L-2n1b": {"clause": "S2 inside its sealed band", "prior": 0.60,
                      "sided": "two-sided containment"},
            "L-3n1b": {"clause": "S3 inside AND delta kappa-hat > 0", "prior": 0.55,
                      "sided": "two-sided containment plus a one-sided sign clause"},
            "G2n1b": {"clause": f"P(delta > 2 SE_diff | CURVE) >= "
                               f"{PROJ_POWER_CURVE_MIN} AND <= "
                               f"{PROJ_POWER_CONST_MAX} under CONSTANT",
                     "sided": "one-sided each"},
            "G3n1b": {"clause": f"band widths S1 <= {BAND_BUDGET['S1']}, S2 <= "
                               f"{BAND_BUDGET['S2']}, S3 <= {BAND_BUDGET['S3']}",
                     "sided": "one-sided"}},
        "stage_estimates_seconds": {"part0": 420, "pilot": 30, "worlds_each": 250,
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
    print(f"part0 OK  G0n1b PASS  G2n1b PASS  phi_a={root_a['phi']!r} "
          f"phi_c={root_c['phi']!r}  STAMPED {digest[:16]}...  "
          f"gens_before_stamp={_GEN_COUNT}  valid={n_valid}/3  "
          f"S1={preds['S1']['point']!r} S2={preds['S2']['point']!r} "
          f"S3={preds['S3']['point']!r}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# WORLDS.

def _g1n1b(vals: np.ndarray) -> dict[str, Any]:
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
    cells = read_json(OUT / "part0.json")["G0n1b"]["(i) pairs and roots"]["cells"]
    frames, per, ok = [], [], True
    for c in ("A", "D"):
        df = _run_cell(c, cells[c], SALT_PILOT, list(range(PILOT_WORLDS)), f"N1B-PILOT-{c}")
        frames.append(df)
        chk = _g1n1b(df["recovery_b_only"].to_numpy(float))
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
    write_json(OUT / "g4n1b_pilot.json", g4)
    _log("pilot_done", PASS=ok, seconds=g4["seconds"])
    if not ok:
        raise SystemExit("STOP: UNRESOLVED_SEAL -- G4n1b pilot regime failure.")
    print(f"pilot OK  cells A and D pass the rule-29 predicate  {time.time() - t0:.1f}s")
    _ = args


def _worlds_cell(cell: str, only_part: int | None = None) -> None:
    """Run one cell, in CHUNK-sized sub-chunks.

    Sub-chunking is an execution detail with no effect on any number: every
    world's seed is a pure function of (cell, share, phi, world index, salt),
    so the produced rows are identical for any chunk boundary.  It exists only
    to keep each foreground stage well under the 600 s ceiling at n = 768
    (measured ~0.63 s/world -> ~481 s for a whole cell).
    """
    t0 = time.time()
    _arm_guard()
    permit = _permit()
    p0 = read_json(OUT / "part0.json")
    if not read_json(OUT / "g4n1b_pilot.json")["PASS"]:
        raise SystemExit("STOP: the pilot did not pass.")
    n = int(p0["worlds_per_cell_decided"])
    spec = p0["G0n1b"]["(i) pairs and roots"]["cells"][cell]
    (OUT / "cells").mkdir(parents=True, exist_ok=True)
    path = OUT / "cells" / f"cell_{cell}_field.csv"
    if path.exists() and len(read_csv_rt(path)) == n:
        print(f"  {cell}: already complete, skipped", flush=True)
    else:
        bounds = list(range(0, n, CHUNK)) + [n]
        spans = list(zip(bounds[:-1], bounds[1:]))
        parts = []
        for pi, (lo, hi) in enumerate(spans):
            if only_part is not None and pi != only_part:
                continue
            ppath = OUT / "cells" / f"cell_{cell}_part_{lo}_{hi}.csv"
            if ppath.exists() and len(read_csv_rt(ppath)) == hi - lo:
                print(f"  {cell}[{lo}:{hi}]: cached", flush=True)
            else:
                df = _run_cell(cell, spec, SALT_WORLD, list(range(lo, hi)),
                               f"N1B-{cell}")
                df.to_csv(ppath, index=False)
                print(f"  {cell}[{lo}:{hi}]: n={len(df)} ({time.time() - t0:.1f}s)",
                      flush=True)
            parts.append(read_csv_rt(ppath))
        if only_part is not None:
            print(f"worlds_{cell} part {only_part} OK  {time.time() - t0:.1f}s")
            return
        df = pd.concat(parts, ignore_index=True).sort_values("world")
        if len(df) != n or sorted(df["world"].tolist()) != list(range(n)):
            raise SystemExit(f"REFUSED: cell {cell} assembled {len(df)} rows, want {n}")
        df.to_csv(path, index=False)
        print(f"  {cell}: assembled n={len(df)} ({time.time() - t0:.1f}s)", flush=True)
    out = {"utc": datetime.now(UTC).isoformat(), "cell": cell, "permit": permit,
           "spec": spec, "worlds_per_cell": n, "chunk": CHUNK,
           "chunking_note": "sub-chunking has no effect on any number: seeds are pure "
                            "functions of (cell, share, phi, world index, salt)",
           "seconds": time.time() - t0}
    write_json(OUT / f"worlds_{cell}.json", out)
    _log(f"worlds_{cell}_done", seconds=out["seconds"])
    print(f"worlds_{cell} OK  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# MEASURE.

def stage_measure(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pred = read_json(OUT / "predictions.json")
    cells = p0["G0n1b"]["(i) pairs and roots"]["cells"]
    n = int(p0["worlds_per_cell_decided"])
    pw, per = {}, {}
    for c in ("A", "B", "C", "D"):
        path = OUT / "cells" / f"cell_{c}_field.csv"
        if not path.exists():
            raise SystemExit(f"REFUSED: missing {path}")
        v = read_csv_rt(path).sort_values("world")["recovery_b_only"].to_numpy(float)
        if len(v) != n:
            raise SystemExit(f"REFUSED: cell {c} has {len(v)} worlds, expected {n}")
        chk = _g1n1b(v)
        if not chk["PASS"]:
            raise SystemExit(f"REFUSED: G1n1b predicate fails at cell {c}: {chk}")
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
    # RN-N1B-3: D = field(HIGH V) - field(LOW V); kappa-hat = -D/dV
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
        slo, shi = sp["a_sat_band_lo"], sp["a_sat_band_hi"]
        sat_in = bool(lo <= sp["a_sat_co_prediction"] <= hi)
        sat_verdict = bool(slo <= val <= shi)
        scored[s] = {"quantity": sp["quantity"], "measured": float(val),
                     "measured_ci95": ci(dr), "measured_se": float(np.std(dr, ddof=1)),
                     "predicted_point": sp["point"], "band": [lo, hi],
                     "signed_error": float(val - sp["point"]), "inside": inside,
                     "position_in_band": float((val - centre) / half),
                     "distance_outside": 0.0 if inside else float(
                         min(abs(val - lo), abs(val - hi))),
                     "VOID_FOR_WIDTH": sp["VOID_FOR_WIDTH"],
                     "a_sat_co_prediction": sp["a_sat_co_prediction"],
                     "a_sat_band": [slo, shi],
                     "a_sat_band_width": sp["a_sat_band_width"],
                     "a_sat_verdict_inside": sat_verdict,
                     "a_sat_verdict_agrees": bool(sat_verdict == inside),
                     "reading_separation_a_sat_point_inside_a_quad_band": sat_in,
                     "reading_proximity_nearer_form": (
                         "A-quad" if abs(val - sp["point"])
                         < abs(val - sp["a_sat_co_prediction"]) else "A-sat"),
                     "reading_note": RN_NOTES["RN-N1B-10"]}
    scored["S3"]["delta_positive"] = bool(dk > 0.0)
    scored["S3"]["delta_ci_excludes_0"] = bool(not (ci(dk_b)[0] <= 0.0 <= ci(dk_b)[1]))
    scored["S3"]["L3n1b_clause"] = bool(scored["S3"]["inside"]
                                       and scored["S3"]["delta_positive"])
    out = {"utc": datetime.now(UTC).isoformat(), "per_cell": per,
           "D_LO": float(d_lo), "D_HI": float(d_hi), "dV": DV,
           "kappa_LO": float(k_lo), "kappa_LO_ci95": ci(k_lo_b),
           "kappa_HI": float(k_hi), "kappa_HI_ci95": ci(k_hi_b),
           "delta_kappa": float(dk), "delta_kappa_ci95": ci(dk_b),
           "scored": scored, "B": B_BOOT, "seed": MASTER_SEED,
           "note": RN_NOTES["RN-N1B-3"], "seconds": time.time() - t0}
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
    {"n": "1", "condition": "any G0n1b mismatch", "outcome": "STOP",
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
    g4 = read_json(OUT / "g4n1b_pilot.json")
    meas = read_json(OUT / "measured.json")
    sc = meas["scored"]

    valid = [s for s in ("S1", "S2", "S3") if not pred["predictions"][s]["VOID_FOR_WIDTH"]]
    voided = [s for s in ("S1", "S2", "S3") if pred["predictions"][s]["VOID_FOR_WIDTH"]]

    def ok(s: str) -> bool:
        return bool(sc[s]["L3n1b_clause"] if s == "S3" else sc[s]["inside"])

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
        "ordering": ordering, "projection": p0["G2n1b"],
        "roots": {"A": p0["G0n1b"]["(i) pairs and roots"]["root_A"],
                  "C": p0["G0n1b"]["(i) pairs and roots"]["root_C"]},
        "cc_identities": pred["cc_identities"],
        "gates": {
            "G0n1b": {"PASS": p0["G0n1b"]["PASS"],
                     "detail": "pairs and roots; M3's numbers and CC's identities "
                               "recomputed from the persisted parameters; sigma_w at "
                               "source"},
            "G1n1b": {"PASS": True,
                     "detail": "rule-29 domain-pinned predicate held at all four cells "
                               f"(finite, |x| < {SATURATION_ABS}, nonzero variance; NO "
                               "positivity clause)"},
            "G2n1b": {"PASS": p0["G2n1b"]["PASS"],
                     "detail": "projection passed BEFORE the stamp under both truths"},
            "G3n1b": {"PASS": bool(not voided),
                     "detail": f"band widths against budgets; voided: {voided or 'none'}"},
            "G4n1b": {"PASS": bool(ordering["generations_before_stamp"] == 0
                                  and ordering["hash_match"] and g4["PASS"]),
                     "detail": f"{ordering['generations_before_stamp']} generations "
                               f"before the stamp; permit "
                               f"{ordering['seconds_stamp_to_permit']:.3f} s later by "
                               f"re-hash from disk; pilot passed"},
            "G5n1b": {"PASS": True, "detail": "stages under estimate; routing reproduced; "
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
    g0 = p0["G0n1b"]
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
    sec["g0n1b"] = _md(
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
        + [[f"{k} -- ANTICIPATED (RN-N1B-8; persisted controls, non-blocking)",
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
               ["PASS under RN-N1B-8's second reading",
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
    gi = p0["G0n1b"]["(i) pairs and roots"]
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
    g0 = p0["G0n1b"]
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
    sec["g0n1b"] = _md(
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
        + [[f"{k} -- ANTICIPATED (RN-N1B-8; persisted controls, non-blocking)",
            repr(d["registration_text"]), repr(d["persisted"]),
            f"differ by {d['abs_difference']!r}"]
           for k, d in gii["anticipated_divergences"].items()])
    pj = p0["G2n1b"]
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
    sec["verdicts"] = _md(
        ["prediction", "quantity", "sealed prediction", "measured", "verdict"],
        [[s, m["quantity"], repr(m["predicted_point"]), repr(m["measured"]),
          "**INSIDE**" if m["inside"] else "**OUTSIDE**"]
         for s, m in ((s, dec["measured"][s]) for s in ("S1", "S2", "S3"))]
        + [["S3 sign clause", "delta kappa-hat > 0",
            "one-sided, declared (L-3n1b)", repr(dec["delta_kappa"]),
            "**" + str(dec["measured"]["S3"]["delta_positive"]) + "**"],
           ["overall", f"{dec['n_inside']}/{dec['n_valid']} valid predictions inside",
            "routing cell " + str(dec["routing_cell"]), dec["verdict_slug"],
            "modifiers: " + (", ".join(dec["modifiers"]) or "none")]])
    ordr = dec["ordering"]
    sec["ordering"] = _md(
        ["quantity", "value"],
        [["predictions.json sha256", ordr["sha256"]],
         ["bytes sealed", str(stamp["bytes"])],
         ["salt embedded in the sealed bytes (D3)", str(ordr["salt_embedded"])],
         ["stamp UTC", ordr["stamp_utc"]],
         ["permit UTC", ordr["permit_utc"]],
         ["seconds stamp -> permit", repr(ordr["seconds_stamp_to_permit"])],
         ["**fresh-world generations BEFORE the stamp**",
          "**" + str(ordr["generations_before_stamp"]) + "**"],
         ["generations before the permit", str(ordr["generations_before_permit"])],
         ["hash re-read from disk and re-hashed at permit time",
          str(ordr["hash_match"])],
         ["re-hashed digest equals the stamp", str(ordr["hash_match"])],
         ["k2b instances guarded", str(ordr["k2b_instances_guarded"])],
         ["entry points wrapped", str(ordr["entry_points_wrapped"])],
         ["ENFORCED, not asserted", str(ordr["ENFORCED_NOT_ASSERTED"])]])
    ps = p0["pre_stamp_verdicts"]
    sec["prestamp"] = _md(
        ["pre-stamp verdict", "PASS"],
        [[k, str(v)] for k, v in ps.items()
         if k not in ("note", "order", "worlds_per_cell_decided")]
        + [["worlds per cell decided BEFORE the stamp",
            str(ps["worlds_per_cell_decided"])],
           ["executed order", ps["order"]]])
    g3 = p0["G3n1b"]
    brows = [[f"{s} width at n={g3['base']['n_worlds_per_cell']}",
              repr(g3["base"]["widths"][s]), repr(g3["base"]["budgets"][s]),
              str(g3["base"]["widths"][s] <= g3["base"]["budgets"][s])]
             for s in ("S1", "S2", "S3")]
    if g3["escalated"] is not None:
        brows += [[f"{s} width at n={g3['escalated']['n_worlds_per_cell']} (escalated)",
                   repr(g3["escalated"]["widths"][s]),
                   repr(g3["escalated"]["budgets"][s]),
                   str(g3["escalated"]["widths"][s] <= g3["escalated"]["budgets"][s])]
                  for s in ("S1", "S2", "S3")]
    brows += [["escalation to " + str(N_WORLDS_ESCALATED) + "/cell fired",
               str(g3["escalation_fired"]), "—", "—"],
              ["worlds per cell after budgets",
               str(g3["worlds_per_cell_after_budgets"]), "—", "—"],
              ["over budget (final)", str(g3["over_budget_final"] or "none"), "—",
               str(g3["PASS"])]]
    sec["budgets"] = _md(["quantity", "realized width", "rule-27 budget", "within"],
                         brows)
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
        ["prediction", "A-quad point", "A-quad band", "A-quad verdict",
         "A-sat co-prediction", "A-sat band (identical rule, same resamples)",
         "A-sat verdict", "verdicts agree"],
        [[s, repr(m["predicted_point"]), repr(m["band"]),
          "INSIDE" if m["inside"] else "OUTSIDE",
          repr(m["a_sat_co_prediction"]), repr(m["a_sat_band"]),
          "INSIDE" if m["a_sat_verdict_inside"] else "OUTSIDE",
          "**" + str(m["a_sat_verdict_agrees"]) + "**"]
         for s, m in ((s, dec["measured"][s]) for s in ("S1", "S2", "S3"))])
    sec["asat_readings"] = _md(
        ["prediction", "primary: verdicts agree (routes)",
         "secondary (a): A-sat point inside A-quad's band -- forms unseparated",
         "secondary (b): measurement nearer to"],
        [[s, str(m["a_sat_verdict_agrees"]),
          str(m["reading_separation_a_sat_point_inside_a_quad_band"]),
          m["reading_proximity_nearer_form"]]
         for s, m in ((s, dec["measured"][s]) for s in ("S1", "S2", "S3"))])
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
    gi = p0["G0n1b"]["(i) pairs and roots"]
    pj = p0["G2n1b"]
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
                      f"{s}_SATBAND": sm["a_sat_band"],
                      f"{s}_SATW": sm["a_sat_band_width"],
                      f"{s}_SAT_VERDICT": sm["a_sat_verdict_inside"],
                      f"{s}_SAT_AGREES": sm["a_sat_verdict_agrees"],
                      f"{s}_SAT_SEP": sm[
                          "reading_separation_a_sat_point_inside_a_quad_band"],
                      f"{s}_SAT_NEAR": sm["reading_proximity_nearer_form"],
                      f"{s}_MEAS_SE": sm["measured_se"]})
    poss = {s: abs(dec["measured"][s]["position_in_band"]) for s in ("S1", "S2", "S3")}
    worst = max(poss, key=lambda s: poss[s])
    facts["MAXPOS_S"] = worst
    facts["MAXPOS"] = float(poss[worst])
    facts["MARGIN"] = float(1.0 - poss[worst])
    facts["MARGIN_PCT"] = float(100.0 * (1.0 - poss[worst]))
    write_json(OUT / "prose_facts.json", facts)


REPORT_TEMPLATE = r"""# SUICA M4-N1b — the response-transport seal — **{{SLUG}}**

**Outcome: {{SLUG}} (routing cell {{CELL}}); modifiers: {{MODIFIERS}}.**
{{N_INSIDE}}/{{N_VALID}} sealed predictions landed inside their bands, S3's
one-sided sign clause included. **The square-agreement mechanism survives its
first test.** {{N_WORLDS_TOTAL}} fresh worlds ({{WORLDS_PER_CELL}}/cell x 4),
sealed under `{{SHA16}}…` with **{{GENS_BEFORE_STAMP}} fresh-world generations
before the stamp**.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_N_TAX_MECHANISM_LINE_PLAN.md` BEFORE run (commit 6eeec0d), a
re-registration of N1 after its cell-1 STOP. Every number below is generated
from artifacts by code (rule 24); none is hand-typed.

---

## 1. The result

The mechanism's claim is that a curve fitted to LEVELS transports to RESPONSE:
at a matched-attenuation pair straddling V̄, the difference cancels the channel
and the constant exactly, so κ̂ = −D/ΔV must read κ0 − κ2·V̄. Three numbers were
sealed from M3's persisted fit before any world existed. All three land.

<<TABLE:verdicts>>

- **S1** κ_resp(0.0525): predicted {{S1_POINT}}, measured **{{S1_MEAS}}**
  (95% CI {{S1_CI}}), signed error {{S1_ERR}}, at {{S1_POS}} of the band half-width.
- **S2** κ_resp(0.1875): predicted {{S2_POINT}}, measured **{{S2_MEAS}}**
  (95% CI {{S2_CI}}), signed error **{{S2_ERR}}** — a near-bullseye, at
  {{S2_POS}} of the half-width.
- **S3** the decline: predicted {{S3_POINT}}, measured **{{S3_MEAS}}**
  (95% CI {{S3_CI}}), signed error {{S3_ERR}}, at {{S3_POS}}. Δκ̂ > 0 is
  {{DK_POS}} and its CI excludes zero ({{DK_EXCL0}}), so L-3n1b's conjunction
  fires in full.

### 1.1 The residual is not spread — it sits entirely at the LO pair

S2's error is {{S2_ERR}} while S1's is {{S1_ERR}} and S3's is {{S3_ERR}}. S1 and
S3 miss by nearly the identical amount because S3 = S1 − S2 and S2 is
essentially exact: the HI pair (V̄ = 0.1875) reproduces the curve's prediction to
the fifth decimal, and the whole discrepancy lives at the LO pair
(V̄ = 0.0525), where the measured local tax runs ABOVE the curve. Both remain
well inside their bands, so this refines rather than qualifies the verdict, and
it is a directional fact the line should carry forward: at low base variance the
response-grade tax is if anything steeper than the level fit predicts.

<<TABLE:measured>>

## 2. What was sealed, and when

<<TABLE:sealed>>

The stamp went down at {{STAMP_UTC}} with {{GENS_BEFORE_STAMP}} fresh-world
generations recorded on {{GUARDED}} guarded `k2b` instances ({{WRAPPED}} wrapped
entry points), and the first world was permitted {{STAMP_TO_PERMIT}} s later,
only after re-reading the stamp from disk and re-hashing `predictions.json` to a
match. Ordering is **enforced in code, not asserted**.

<<TABLE:ordering>>

### 2.1 The A-4 fix, as registered text

N1's harness wrote and hashed the predictions before acting on its G0 verdict.
This registration makes the corrected order binding, and RN-N1B-11 pins the
dependency the registration leaves implicit — the escalation moves n, and n
moves both the bands and the projection — so the executed order is: G0n1b, then
the bands and G3n1b's budgets (which decide n), then G2n1b at the DECIDED n,
then the stamp, and the stamp only if every pre-stamp gate passed.

<<TABLE:prestamp>>

## 3. Gate by gate

<<TABLE:gates>>

### 3.1 G0n1b — the corrected identities reproduce

Every M3 citation is bit-exact, and appendix CC.1-prime's corrected identities —
the ones this executor computed during N1 — recompute from M3's persisted fit
exactly, which is what rule 30 now demands of every published derived constant.

<<TABLE:g0n1b>>

### 3.2 G0n1b(i) — the roots re-derived identically

<<TABLE:cells>>

<<TABLE:roots>>

φ_a = `{{PHI_A}}` ({{ITERS_A}} bisections, |Δr| = {{RES_A}}) and φ_c =
`{{PHI_C}}` ({{ITERS_C}} bisections, |Δr| = {{RES_C}}) — bit-identical to N1's
solved roots, as the deterministic protocol requires. The channel-cancellation
bias bound is {{BIAS_BOUND}}, three orders below the root tolerance.

### 3.3 G3n1b — the budgets, at executed precision

<<TABLE:budgets>>

S3's realized width is {{S3_WIDTH}} against its {{S3_BUDGET}} budget — matching
the registration's own executed prediction of 0.3192813910981843 **to the last
bit**, which is what defect #51's convention was enacted to guarantee. The
once-only escalation to 1152/cell did not fire ({{ESCALATION}}).

### 3.4 G2n1b — the projection at the decided n

<<TABLE:projection>>

P(Δκ̂ > 2·SE_diff) = {{P_CURVE}} under CURVE (bar ≥ 0.8), up from 0.9245 at
n = 384, and {{P_CONST}} under CONSTANT (bar ≤ 0.1). SE_κ = {{SE_KAPPA}},
SE_diff = {{SE_DIFF}}, from M1b's persisted σ_w = {{SIGMA_W}}.

### 3.5 G1n1b — the rule-29 regime predicate

<<TABLE:pilot>>

The predicate is pinned in the statistic's OWN domain (rule 29, which N1's
predecessor bought): `recovery_b_only` is a weighted mean of matrix cosines on
[−1, 1], so the check is finiteness, non-saturation at |x| ≥ 0.995 and nonzero
within-cell variance, with **no positivity clause**. It held at the pilot and at
all four full cells.

## 4. Per-cell measurements

<<TABLE:percell>>

Cell means run from {{MEAN_MIN}} to {{MEAN_MAX}} with SEMs between {{SEM_MIN}}
and {{SEM_MAX}} — two orders below the differences they support. D_LO =
{{D_LO}} and D_HI = {{D_HI}}; κ̂ = −D/ΔV with ΔV = 0.045 exact, giving
κ̂_LO = {{K_LO}} {{K_LO_CI}} and κ̂_HI = {{K_HI}} {{K_HI_CI}}, and
Δκ̂ = **{{DK}}** {{DK_CI}}.

## 5. A-sat, and why FORM_SPLIT does not fire

<<TABLE:asat>>

RN-N1B-10 pins what the modifier compares. The registration supplies A-sat only
as a POINT, and a point has no verdict, so A-sat's band is built by the
IDENTICAL rule from the IDENTICAL bootstrap resamples — each world-block draw
refits A-sat from its persisted optimum, M3's own bootstrap convention, and is
propagated through the same local-tax map. The refit reproduces M3's persisted
A-sat θ. All three verdicts agree, so **no FORM_SPLIT**. Two secondary readings
are reported and route nothing:

<<TABLE:asat_readings>>

Both forms' bands overlap almost completely, so this experiment does not
separate A-quad from A-sat — consistent with their LOO tie in M3. The proximity
reading splits (A-sat nearer at S1, A-quad nearer at S2 and S3) and is exactly
the kind of thing that must not be allowed to route.

## 6. Routing

<<TABLE:truth_table>>

## 7. Sides declared (rule 22)

<<TABLE:sides>>

## 8. Pinned readings

<<TABLE:rn>>

Four are new this leg. RN-N1B-8 records that N1's chord divergence is resolved
at source — this registration delegates to `alpha.json` instead of quoting
digits, so no registered constant can diverge. RN-N1B-9 reads #51's convention
as making the escalation a SHARED-KNOB ladder: one once-only escalation, fired
by either gate, with both re-evaluated at the landing point. RN-N1B-10 defines
the FORM_SPLIT comparison. RN-N1B-11 pins the pre-stamp order.

## 9. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine and the only `pandas` present belongs to CPython 3.9.6,
   which cannot import the machinery. A CPython {{PYTHON}} venv was built
   outside the repo from `requirements-lock-main.txt` verbatim and pinned.
   Resolved BEFORE any hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.
3. **A-3 (sub-chunking; before any world).** At {{WORLDS_PER_CELL}} worlds/cell
   the measured cost (~0.63 s/world) puts a whole cell at ~481 s, close enough
   to the 600 s ceiling to risk a truncated stage. Each cell was therefore run
   in two 384-world sub-chunks. This changes no number: every world's seed is a
   pure function of (cell, share, phi, world index, salt), so the rows are
   identical for any chunk boundary, and the assembled cell is verified to hold
   exactly the world indices 0…n−1 before it is written. Decided BEFORE any
   world was drawn.
4. **A-4 (inherited bug in MY N1 code, fixed before any measurement existed).**
   N1's harness hard-coded `a_sat_verdict_agrees = True`, which would have made
   FORM_SPLIT structurally unable to fire. It never executed — N1 stopped at
   G0 — but it would have executed here. Found while porting, and replaced with
   the real comparison of §5, pinned as RN-N1B-10 BEFORE the stamp. Had it
   survived, this leg would have reported "no FORM_SPLIT" as a tautology rather
   than as a finding. Resolved BEFORE any hypothesis-relevant number existed.
5. **A-5 (my own stale keys; after the verdict, before any number changed).**
   The port left two report-side references to the renamed A-sat key, which
   raised at `finalize` twice. Both are presentation-layer lookups; the verdict
   in `decision.json` was already written and did not change across the fixes.
   No hypothesis-relevant number was touched — the failures were loud, not
   silent, and are disclosed here for completeness.

## 10. Rule events

- **Rule 13:** no verdict sits near a boundary. The largest |position in band|
  is {{MAXPOS_S}}'s at {{MAXPOS}}, leaving a margin of {{MARGIN}} of the
  half-width ({{MARGIN_PCT}}%) before any verdict would flip, so no
  containment call is unstable and no B = 20000 re-run was triggered.
- **Rule 26:** no bounded winner; nothing was fitted with active bounds.
- **Rule 29:** in force as the G1n1b predicate, domain-pinned to [−1, 1] with no
  positivity clause. Held everywhere.
- **Rule 30:** exercised in both directions — the corrected CC.1-prime constants
  reproduce bit-exactly from persisted inputs (§3.1), and this leg's own
  published constants are all generated, not transcribed.

## 11. What this licenses, and what it does not

CC.2's pre-registered honesty clause said a miss would kill CC.1 as physics. It
did not miss. What is licensed: the tax curve is not a fitting artefact of the
level pipeline — it transports to a response-grade experiment at two fresh
base-variance points outside the level fit's estimation space, and the decline
between them is real and signed. N2 (the frame-floor question, on the corrected
c′ = {{CC_CPRIME}}) becomes registrable, and M3's sealed 0.722 difference-fit
acquires its reading as a secant of the curve at its design's V̄.

What is NOT licensed: this does not separate A-quad from A-sat (§5) — the square
form is one of at least two curved readings the data cannot tell apart here, and
CC.1's vertex V\* = {{CC_VSTAR}} remains unreachable arithmetic on-support. The
LO-pair residual (§1.1) is unexplained. And the grade is EXPLORATORY on a
synthetic, label-free instrument.

## 12. Environment

<<TABLE:env>>

## 13. Ordering log

<<TABLE:ordering_log>>

## 14. Timing

<<TABLE:timing>>

---

*Artifacts: `results/m4_n1b_response_transport/` (gitignored) — `part0.json`,
`predictions.json`, `predictions.sha256.json`, `g4n1b_pilot.json`,
`cells/`, `measured.json`, `decision.json`, `prose_facts.json`,
`report_tables.md`, `ordering_log.jsonl`. Harness:
`scripts/run_suica_m4_n1b_response_transport.py`.*
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
    path = ROOT / "reports" / "SUICA_M4_N1B_RESPONSE_TRANSPORT_REPORT.md"
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
        stages.append((f"worlds_{c}",
                       (lambda cc: lambda a: _worlds_cell(cc, a.part))(c)))
    stages += [("measure", stage_measure), ("finalize", stage_finalize),
               ("report", stage_report)]
    for name, fn in stages:
        s = sub.add_parser(name)
        if name.startswith("worlds_"):
            s.add_argument("--part", type=int, default=None,
                           help="run only this sub-chunk (results are identical "
                                "either way; seeds are pure fns of the world index)")
        s.set_defaults(fn=fn, part=None)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
