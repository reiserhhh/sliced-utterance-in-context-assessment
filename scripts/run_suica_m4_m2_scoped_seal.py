#!/usr/bin/env python3
"""M4-M2 -- THE SCOPED EXTRAPOLATION SEAL (predict, hash, then run).

Registered in docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md ("M4-M2 -- the scoped
extrapolation seal", commit 97041cd) BEFORE this file existed.  Implementation
and execution only; the registration is binding.

Five legs built to this one.  M1 died on a proxy gate; M1b priced the budget;
M1c bought it and measured a negative slope at fixed V; M1d completed the family
and dissolved the exponent into a ridge; M1e found the shape (free share margins
plus a steep negative r-power) and rule 27 blocked the seal because the exponent
is not a quotable object.  The ridge lives in PARAMETER space, not in PREDICTION
space over the trained r-window, so what gets sealed here are PREDICTIONS.

    P1  contrast, alpha-free, share EXTERIOR: field(C2) - field(C1)
    P2  level at an interior-new phi:         alpha(0.40) + lambda*r_C3^q
    P3  contrast, phi EXTERIOR, high-r:       field(C5) - field(C4)
    P4  stress reading, NO gate, pre-signed ABOVE: the REJECTED tax-additive
        model's level at C2

THE ORDERING IS THE POINT AND IT IS ENFORCED IN CODE.  Every k2b entry point
that can build or measure a world is wrapped at import-time on every reachable
k2b instance; the permit is issued ONLY by re-reading predictions.sha256.json
from disk and re-hashing predictions.json to a match.  ZERO fresh worlds -- the
pilot included -- may exist before the stamp (RN-K2F-4: a pilot is a measurement
of the sealed arm, so it runs AFTER the stamp; publishing a prediction early
costs nothing, reading the arm early costs the leg).  The salt is embedded
INSIDE the sealed bytes (D3 convention).

    part0     G0m2(i)-(v); the E-rq refit; the B=2000 bootstrap propagated
              through every prediction; the rule-27 band budgets; then
              predictions.json is written AND HASHED.  No world may exist.
    pilot     G2m2: 4 worlds each at C1 and C5 on m4m2-pilot, AFTER the stamp.
    worlds_1/2/3   the five sealed cells (2/2/1), 192 worlds each.
    measure   aggregate, bootstrap the measured values, score containment.
    finalize  route through the registered table; modifiers.
    report    renders the report from artifacts (rule 24).

Artifacts: results/m4_m2_scoped_seal/ (gitignored)
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
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "results" / "m4_m2_scoped_seal"
RES = ROOT / "results"
M1BRES = RES / "m4_m1b_r_at_level"
M1CRES = RES / "m4_m1c_r_at_level"
M1ERES = RES / "m4_m1e_shape"

LEG = "M4-M2"
BANNER = ("prospective scoped seal on K2b's frozen instrument, exploratory, "
          "label-free; predictions hashed before any fresh world exists")

MASTER_SEED = 20260811
SALT_WORLD = "m4m2-world"
SALT_PILOT = "m4m2-pilot"
N_WORLDS = 192
PILOT_WORLDS = 4
B_BOOT = 2000
B_BOOT_HIGH = 20000
INT_SHARE = 0.0
W_INT_ARM = "zero"

SIGMA_W = 0.026889438327132725                       # M1b's persisted sigma_w
R_WINDOW = (0.4541409476972356, 0.8189581462487876)  # M1c's trained r-window
TRAINED_SHARES = (0.10, 0.25, 0.40, 0.60)
TRAINED_PHIS = (0.05, 0.30, 0.60, 0.85, 0.98)
SHARE_ENVELOPE_TOP = 0.6634207990183637

# --- the planner's design table (G0m2(i): reproduce bit-exactly) -----------
CELLS = {
    "C1": {"share": 0.70, "phi": 0.05, "r": 0.5967380569813433,
           "V": 0.21000000000000005,
           "role": "P1 contrast side; share EXTERIOR (envelope top "
                   "0.6634207990183637)"},
    "C2": {"share": 0.70, "phi": 0.60, "r": 0.5197539933932338,
           "V": 0.21000000000000005, "role": "P1 contrast side; P4 stress level"},
    "C3": {"share": 0.40, "phi": 0.45, "r": 0.7131718346406168,
           "V": 0.12000000000000004, "role": "P2 level; phi interior-new"},
    "C4": {"share": 0.25, "phi": 0.05, "r": 0.785015540293945,
           "V": 0.07500000000000002,
           "role": "P3 contrast side; duplicates an M1c cell on a FRESH salt -> "
                   "the seed-replication reading"},
    "C5": {"share": 0.25, "phi": 0.995, "r": 0.6701862156520305,
           "V": 0.07500000000000002, "role": "P3 contrast side; phi EXTERIOR (above .98)"},
}
CELL_ORDER = ("C1", "C2", "C3", "C4", "C5")
REJECTED_AT_REGISTRATION = {0.85: 0.44410111322601925, 0.98: 0.384884059649622}
WORLD_CHUNKS = {1: ("C1", "C2"), 2: ("C3", "C4"), 3: ("C5",)}

# --- M1e's persisted winner (G0m2(v): the refit must equal these bit-exactly)
M1E_ALPHA = (0.18560847593788873, 0.1456494891347315, 0.10934916761257428,
             0.06667603971206824)
M1E_LAMBDA = -0.057625974791364554
M1E_Q = 3.863625377453229
# --- M1e's rejected tax-additive model (P4) --------------------------------
M1E_TAX_C = 0.17942722572114997
M1E_TAX_KAPPA = 0.6761549415814
M1E_TAX_G = {0.05: -0.0048219471766308515, 0.30: -0.0029497424973075753,
             0.60: 0.0008027742599145088, 0.85: 0.003591095421635563,
             0.98: 0.003377819992388355}

# --- G0m2(ii): every M1e number the adjudication quotes --------------------
M1E = {
    "E-rq LOO": 0.0024079360107794926,
    "E-add LOO": 0.002706675155983591,
    "E-rlin LOO": 0.0026942709003566117,
    "E-tax-add LOO": 0.003579020306723271,
    "F0 LOO": 0.0030682764618814033,
    "winner lambda": -0.057625974791364554,
    "winner q": 3.863625377453229,
    "winner q CI lo": 2.0529339475688055,
    "winner q CI hi": 5.921369905297595,
    "r2 coef": -0.007427848773582237,
    "r2 CI lo": -0.03672898793443594,
    "r2 CI hi": 0.018353437794254,
    "tax kappa": 0.6761549415814,
    "tax kappa CI lo": 0.6619291032569563,
    "tax kappa CI hi": 0.6901486195533926,
    "alpha 0.10": 0.18560847593788873,
    "alpha 0.25": 0.1456494891347315,
    "alpha 0.40": 0.10934916761257428,
    "alpha 0.60": 0.06667603971206824,
    "monotonicity share 0.10": 0.0012820301142057455,
    "monotonicity share 0.25": 0.010391443071199338,
    "monotonicity share 0.40": 0.01143698383536769,
    "monotonicity share 0.60": 0.009688611655304012,
}
M1E_ROUNDED = {"E-rq vs E-rlin gap pct": 11.89, "q width over budget": 3.87}
# the adjudication quotes the monotonicity contrasts rounded to 5 dp
M1E_MONO_ROUNDED = {0.10: 0.00128, 0.25: 0.01039, 0.40: 0.01144, 0.60: 0.00969}

# --- rule-27 band budgets (Part 0, BEFORE the stamp) ------------------------
BAND_BUDGET = {"P1": 0.04, "P2": 0.05, "P3": 0.04}

# ---------------------------------------------------------------------------
# RN-M2 notes.  PINNED IN PART 0, BEFORE THE STAMP AND BEFORE ANY WORLD.
#
# RN-M2-1 (ordering, inherited verbatim).  K2f's G1f pattern and RN-K2F-4: the
#   permit to generate ANY fresh world -- the pilot included -- is issued only by
#   re-reading predictions.sha256.json from disk and re-hashing predictions.json
#   to a match, and the rule-17 pilot therefore runs AFTER the stamp.  A pilot is
#   a measurement of the sealed arm; publishing a prediction early costs nothing,
#   reading the arm early costs the leg.  Enforced by wrapping
#   build_k2b_world / run_field_world / emit_panel on EVERY reachable k2b
#   instance (RN-K2F-5), plus a cross-process refusal if any world artifact
#   already exists at stamp time.
#
# RN-M2-2 (the salt inside the sealed bytes -- D3).  predictions.json embeds
#   both salts and the master seed BEFORE hashing, so the digest covers the seed
#   lineage and no later manifest can be reconstructed by guessing it.
#
# RN-M2-3 (bootstrap propagation).  The registration says the winner's
#   within-cell world-block bootstrap is "recomputed and each draw propagated
#   through the formulas".  PINNED: one B=2000 master-seeded pass over M1c's
#   persisted per-world corpus; each draw re-fits E-rq from that draw's 20 cell
#   means starting at the full-data optimum (M1e's bootstrap convention
#   verbatim), and the SAME draw's (alpha, lambda, q) is pushed through P1, P2,
#   P3.  Predictions therefore inherit the parameter covariance rather than a
#   per-parameter interval, which is the only correct way to band a function of
#   a ridge.
#
# RN-M2-4 (SE_meas).  sigma_w = 0.026889438327132725 is M1b's persisted,
#   df-inflated pilot value, used as registered: SE_meas = sigma_w/sqrt(192) for
#   LEVELS (P2, P4) and sqrt(2)*sigma_w/sqrt(192) for CONTRASTS (P1, P3).  It is
#   a PRIOR measurement-noise allowance fixed before the fresh cells exist, not
#   the realized SEM; the realized per-cell SEMs are reported beside it.
#
# RN-M2-5 (the replication reading's SEM).  "|mean(C4) - M1c's persisted cell
#   mean| vs 2*sqrt(2)*SEM" does not say WHICH SEM.  PINNED as the literal
#   reading: SEM = the fresh C4 cell's own realized SEM, so the bar is
#   2*sqrt(2)*SEM_C4.  The exact two-sample alternative
#   (2*sqrt(SEM_C4^2 + SEM_M1c^2)) is computed and reported beside it; both are
#   shown and the literal one gates the SEED_INSTABILITY modifier.
#
# RN-M2-6 (P4's band).  The modifier keys on P4 being above/below/inside "its
#   own reported +-2*SE_meas of the tax-linear value".  PINNED: the band is
#   [tax_value - 2*SE_meas_level, tax_value + 2*SE_meas_level] with the
#   tax-linear value a FIXED arithmetic constant from M1e's persisted
#   tax-additive parameters (no bootstrap: it is a stress reading against a
#   rejected model's point extrapolation, not a seal).
#
# RN-M2-7 (measured CIs).  Each fresh cell's measured mean carries a within-cell
#   world-block bootstrap CI (B=2000, master seed) over its own 192 worlds;
#   contrasts resample their two cells INDEPENDENTLY in the same draw.  These
#   are REPORTED; containment is scored on the measured POINT against the sealed
#   band, exactly as the registration writes it.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-M2-1": "ordering enforced in code (K2f G1f + RN-K2F-4): the permit for ANY fresh "
               "world, pilot included, is issued only by re-reading "
               "predictions.sha256.json from disk and re-hashing; the pilot runs AFTER "
               "the stamp; guards on every reachable k2b instance plus a cross-process "
               "refusal if a world artifact already exists",
    "RN-M2-2": "predictions.json embeds both salts and the master seed BEFORE hashing "
               "(D3 convention), so the digest covers the seed lineage",
    "RN-M2-3": "one B=2000 master-seeded bootstrap over M1c's persisted corpus; each "
               "draw re-fits E-rq from that draw's cell means and the SAME draw's "
               "(alpha, lambda, q) is pushed through P1/P2/P3 -- predictions inherit the "
               "parameter COVARIANCE, the only correct way to band a function of a ridge",
    "RN-M2-4": "SE_meas from M1b's persisted sigma_w as registered: sigma_w/sqrt(192) "
               "for levels, sqrt(2)*sigma_w/sqrt(192) for contrasts -- a PRIOR noise "
               "allowance fixed before the fresh cells exist; realized SEMs reported "
               "beside it",
    "RN-M2-5": "the replication bar is the literal 2*sqrt(2)*SEM with SEM = fresh C4's "
               "own realized SEM (gates the modifier); the exact two-sample alternative "
               "is reported beside it",
    "RN-M2-6": "P4's band is the tax-linear point value +- 2*SE_meas_level, the point "
               "being a fixed arithmetic constant from M1e's rejected tax-additive "
               "parameters (no bootstrap: a stress reading, not a seal)",
    "RN-M2-8": "G2m2's 'non-saturated' pinned to the STATISTIC'S OWN RANGE: "
               "recovery_b_only is a weighted mean of _matrix_cosine "
               "(scripts/run_suica_m4_e1_convention_gap.py:250-264 -> "
               "suica_core/v8_context_relation_field.py _matrix_cosine), so its range is "
               "[-1, 1] and saturation means abs(value) -> 1, NOT value <= 0. Zero is the "
               "statistic's NULL. The inherited 'strictly inside (0,1)' form used by K2f "
               "G2f / M1b G2m' / M1c smoke is an UNREGISTERED addition that was harmless "
               "only where the field sat far above zero; at C1 (share 0.70, V = 0.21 -- "
               "the most person-variance-dominated cell the line has ever run) the b-only "
               "field is expected near zero by design, so a positivity gate there tests "
               "the HYPOTHESIS, not the regime -- precisely the error M1b's own "
               "registration corrected ('an outcome-side flat field is cell-2 EVIDENCE, "
               "not channel death'). BOTH readings are computed; the registered one "
               "gates, the inherited one is reported. FOUND AFTER the pilot ran and "
               "disclosed as such",
    "RN-M2-7": "measured cell CIs are within-cell world-block bootstraps over the fresh "
               "192 worlds (contrasts resample both cells independently); containment is "
               "scored on the measured POINT against the sealed band, as registered",
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
# G1m2 -- ORDERING ENFORCEMENT.  Armed at first world use, never disarmed.

_GEN_COUNT = 0
_PERMIT = False
_ARMED = False
WORLD_ARTIFACTS = ("pilot_field.csv", "g2m2_pilot.json", "cells", "measured.json")


def _ordering_log(event: str, **kw: Any) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rec = {"utc": datetime.now(UTC).isoformat(), "event": event, **kw}
    with (OUT / "ordering_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True, default=float) + "\n")


def _reachable_k2b() -> list[Any]:
    cands: list[Any] = [k2b()]
    for acc in (lambda: k2c().k2b(), lambda: k2e().k2b(), lambda: k2e().k2d().k2b(),
                lambda: k2e().k2d().k2c().k2b()):
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
            original: Callable[..., Any] = getattr(kb, fname)

            def make(orig: Callable[..., Any], nm: str) -> Callable[..., Any]:
                def wrapped(*a: Any, **kw: Any) -> Any:
                    global _GEN_COUNT
                    _GEN_COUNT += 1
                    if not _PERMIT:
                        _ordering_log("REFUSED_world_generation", entry_point=nm,
                                      count=_GEN_COUNT)
                        raise SystemExit(
                            f"STOP (G1m2): fresh-world generation via {nm} attempted "
                            f"before the prediction hash was persisted.")
                    return orig(*a, **kw)
                wrapped.__name__ = f"guarded_{nm}"
                return wrapped

            setattr(kb, fname, make(original, fname))
    _ARMED = True
    _ordering_log("ordering_guard_armed", n_k2b_instances=len(mods),
                  entry_points=["build_k2b_world", "run_field_world", "emit_panel"],
                  n_wrapped=3 * len(mods))
    return len(mods)


def _issue_permit() -> dict[str, Any]:
    """The permit: re-read the stamp from disk and re-hash predictions.json."""
    global _PERMIT
    pp, sp = OUT / "predictions.json", OUT / "predictions.sha256.json"
    if not pp.exists() or not sp.exists():
        raise SystemExit("STOP (G1m2): no persisted prediction stamp; run `part0`.")
    raw = pp.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    stamp = json.loads(sp.read_text(encoding="utf-8"))
    if digest != stamp["sha256"]:
        raise SystemExit(f"STOP (G1m2): predictions.json hash {digest} != stamped "
                         f"{stamp['sha256']}")
    if _GEN_COUNT != 0:
        raise SystemExit(f"STOP (G1m2): {_GEN_COUNT} generations before the permit.")
    _PERMIT = True
    rec = {"permit_utc": datetime.now(UTC).isoformat(),
           "sha256_recomputed": digest, "sha256_stamped": stamp["sha256"],
           "stamp_utc": stamp["stamp_utc"],
           "generations_before_permit": _GEN_COUNT,
           "seconds_stamp_to_permit": float(
               (datetime.now(UTC)
                - datetime.fromisoformat(stamp["stamp_utc"])).total_seconds())}
    _ordering_log("permit_issued", **rec)
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


def world_seed_for(cell: str, world: int, salt: str) -> int:
    c = CELLS[cell]
    v8 = k2b().v8
    return int(v8.stable_bucket(
        f"{MASTER_SEED}-{c['share']!r}|{c['phi']!r}-{world}", salt=salt,
        modulus=2 ** 31 - 1))


# ---------------------------------------------------------------------------
# The predictor: E-rq, refit bit-identically from M1c's persisted cell means.

def erq_predict(theta: np.ndarray, si: np.ndarray, r: np.ndarray) -> np.ndarray:
    a = np.asarray(theta[:4], float)
    return a[si] + float(theta[4]) * r ** float(theta[5])


ERQ_LAMBDA_STARTS = (-0.5, -0.055, 0.05, 0.5)
ERQ_Q_STARTS = (0.5, 1.0, 1.372031438858951, 2.0, 3.0)
OPT = {"routine": "scipy.optimize.least_squares", "method": "trf",
       "jac": "2-point (numerical)", "bounds": "unbounded",
       "ftol": 1e-14, "xtol": 1e-14, "gtol": 1e-14, "max_nfev": 20000,
       "loss": "linear (plain least squares)", "scipy_version": None}


def fit_erq(si: np.ndarray, r: np.ndarray, y: np.ndarray,
            starts: list[list[float]] | None = None) -> dict[str, Any]:
    def resid(t: np.ndarray) -> np.ndarray:
        with np.errstate(over="ignore", invalid="ignore"):
            p = erq_predict(t, si, r)
        return np.where(np.isfinite(p), p, 1e12) - y

    amean = [float(y[si == i].mean()) for i in range(4)]
    grid = starts if starts is not None else [
        amean + [lam, q] for lam in ERQ_LAMBDA_STARTS for q in ERQ_Q_STARTS]
    best, sses, nconv = None, [], 0
    for s0 in grid:
        try:
            res = least_squares(resid, np.asarray(s0, float), method=OPT["method"],
                                jac="2-point", ftol=OPT["ftol"], xtol=OPT["xtol"],
                                gtol=OPT["gtol"], max_nfev=OPT["max_nfev"])
        except Exception:                                   # noqa: BLE001
            continue
        if not res.success and res.status <= 0:
            continue
        nconv += 1
        sse = float(np.sum(res.fun ** 2))
        if not np.isfinite(sse):
            continue
        sses.append(sse)
        if best is None or sse < best["sse"]:
            best = {"theta": [float(x) for x in res.x], "sse": sse}
    if best is None:
        raise SystemExit("REFUSED: no converged start for E-rq")
    best.update({"n_starts": len(grid), "n_converged": nconv,
                 "n_distinct_optima": int(len({round(s, 12) for s in sses})),
                 "rmse": float(np.sqrt(best["sse"] / len(y)))})
    return best


def load_m1c() -> tuple[pd.DataFrame, np.ndarray]:
    p0c = read_json(M1CRES / "part0.json")
    persisted = read_csv_rt(M1CRES / "cell_means.csv").set_index("cell_tag")
    rows, per_world = [], []
    for d in p0c["G1m''"]["design_points"]:
        tag = d["cell_tag"]
        parts = [read_csv_rt(M1CRES / "cells" / nm)
                 for nm in (f"cell_{tag}_w000.csv", f"cell_{tag}_w001_191.csv")]
        df = pd.concat(parts, ignore_index=True)
        vals = df.sort_values("world")["recovery_b_only"].to_numpy(float)
        if len(vals) != N_WORLDS:
            raise SystemExit(f"REFUSED: {tag} has {len(vals)} worlds")
        rows.append({"cell_tag": tag, "share": float(d["share"]), "phi": float(d["phi"]),
                     "r_pred": float(d["r_pred"]), "V_person": float(d["V_person"]),
                     "field_mean": float(vals.mean()),
                     "field_sem": float(np.std(vals, ddof=1) / np.sqrt(len(vals))),
                     "persisted_mean": float(persisted.loc[tag, "field_mean"]),
                     "bit_exact": bool(float(vals.mean())
                                       == float(persisted.loc[tag, "field_mean"]))})
        per_world.append(vals)
    return pd.DataFrame(rows), np.asarray(per_world, float)


# ---------------------------------------------------------------------------
# PART 0 -- gates, refit, bootstrap, predictions, budgets, THE STAMP.

def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    for nm in WORLD_ARTIFACTS + ("predictions.json", "predictions.sha256.json"):
        if (OUT / nm).exists():
            raise SystemExit(f"STOP (G1m2): {nm} exists before Part 0.")
    _ordering_log("part0_start")
    n_guarded = _arm_guard()          # armed BEFORE anything, and never permitted here

    # --- G0m2(i): the planner design table -------------------------------
    design_rows, ok_i = [], True
    for c in CELL_ORDER:
        spec = CELLS[c]
        gr, gv = r_of(spec["share"], spec["phi"]), v_of(spec["share"])
        be = bool(gr == spec["r"] and gv == spec["V"])
        inw = bool(R_WINDOW[0] <= gr <= R_WINDOW[1])
        ok_i &= (be and inw)
        design_rows.append({"cell": c, "share": spec["share"], "phi": spec["phi"],
                            "r_planner": spec["r"], "r_rederived": gr,
                            "V_planner": spec["V"], "V_rederived": gv,
                            "bit_exact": be, "r_interior_to_window": inw,
                            "role": spec["role"]})
    rej = []
    for phi, exp in REJECTED_AT_REGISTRATION.items():
        got = r_of(0.70, phi)
        be = bool(got == exp)
        ok_i &= be
        rej.append({"share": 0.70, "phi": phi, "r_planner": exp, "r_rederived": got,
                    "bit_exact": be, "outside_window": bool(got < R_WINDOW[0])})

    # --- G0m2(iii): M1c cell means ----------------------------------------
    m1c, per_world = load_m1c()
    ok_iii = bool(m1c["bit_exact"].all())

    # --- G0m2(iv): sigma_w and the r-window --------------------------------
    sw = float(read_json(M1BRES / "g3mb_power.json")["sigma_w"])
    rw = (float(m1c["r_pred"].min()), float(m1c["r_pred"].max()))
    ok_iv = bool(sw == SIGMA_W and rw[0] == R_WINDOW[0] and rw[1] == R_WINDOW[1])

    # --- G0m2(ii): every M1e number the adjudication quotes ----------------
    ef = read_json(M1ERES / "fits.json")
    el = read_json(M1ERES / "loo.json")
    ed = read_json(M1ERES / "decision.json")
    wt = dict(zip(ef["fits"]["E-rq"]["param_names"], ef["fits"]["E-rq"]["theta"]))
    tt = dict(zip(ef["fits"]["E-tax-add"]["param_names"], ef["fits"]["E-tax-add"]["theta"]))
    tci = ef["fits"]["E-tax-add"]["bootstrap"]["ci95"]["kappa"]
    wci = ef["fits"]["E-rq"]["bootstrap"]["ci95"]["q"]
    mono = ed["model_free_monotonicity_table"]["rows"]
    an = ["alpha_s0.10", "alpha_s0.25", "alpha_s0.40", "alpha_s0.60"]
    got = {
        "E-rq LOO": el["loo"]["E-rq"]["loo_rmse"],
        "E-add LOO": el["loo"]["E-add"]["loo_rmse"],
        "E-rlin LOO": el["loo"]["E-rlin"]["loo_rmse"],
        "E-tax-add LOO": el["loo"]["E-tax-add"]["loo_rmse"],
        "F0 LOO": el["loo"]["F0"]["loo_rmse"],
        "winner lambda": wt["lambda"], "winner q": wt["q"],
        "winner q CI lo": wci[0], "winner q CI hi": wci[1],
        "r2 coef": ed["verdicts"]["L-3e"]["r2_coef"],
        "r2 CI lo": ed["verdicts"]["L-3e"]["r2_ci95"][0],
        "r2 CI hi": ed["verdicts"]["L-3e"]["r2_ci95"][1],
        "tax kappa": tt["kappa"], "tax kappa CI lo": tci[0], "tax kappa CI hi": tci[1],
        "alpha 0.10": wt[an[0]], "alpha 0.25": wt[an[1]], "alpha 0.40": wt[an[2]],
        "alpha 0.60": wt[an[3]],
        "monotonicity share 0.10": mono[0]["contrast"],
        "monotonicity share 0.25": mono[1]["contrast"],
        "monotonicity share 0.40": mono[2]["contrast"],
        "monotonicity share 0.60": mono[3]["contrast"],
    }
    cites = {k: {"expected": M1E[k], "persisted": got[k],
                 "bit_exact": bool(got[k] == M1E[k])} for k in M1E}
    gap_pct = 100.0 * (el["loo"]["E-rlin"]["loo_rmse"] / el["loo"]["E-rq"]["loo_rmse"] - 1)
    qwid = (wci[1] - wci[0]) / 1.0
    rounded = {
        "E-rq vs E-rlin gap pct": {"adjudication": M1E_ROUNDED["E-rq vs E-rlin gap pct"],
                                   "rederived": gap_pct,
                                   "rounds": bool(round(gap_pct, 2)
                                                  == M1E_ROUNDED["E-rq vs E-rlin gap pct"])},
        "q width over budget": {"adjudication": M1E_ROUNDED["q width over budget"],
                                "rederived": qwid,
                                "rounds": bool(round(qwid, 2)
                                               == M1E_ROUNDED["q width over budget"])}}
    tg = {float(k.replace("g_phi", "")): v for k, v in tt.items() if k.startswith("g_phi")}
    tg[0.98] = -float(sum(tg.values()))
    mono_r = {}
    for i, sh in enumerate((0.10, 0.25, 0.40, 0.60)):
        val = mono[i]["contrast"]
        mono_r[f"monotonicity share {sh} (adjudication rounds to 5dp)"] = {
            "adjudication": M1E_MONO_ROUNDED[sh], "rederived": val,
            "rounds": bool(round(val, 5) == M1E_MONO_ROUNDED[sh])}
    rounded.update(mono_r)
    ok_ii = (all(d["bit_exact"] for d in cites.values())
             and all(d["rounds"] for d in rounded.values())
             and all(abs(tg[p] - M1E_TAX_G[p]) == 0.0 for p in (0.05, 0.30, 0.60, 0.85))
             and tt["c"] == M1E_TAX_C)

    # --- G0m2(v): the refit, bit-identical --------------------------------
    si = np.array([TRAINED_SHARES.index(round(s, 10)) for s in m1c["share"]])
    rr = m1c["r_pred"].to_numpy(float)
    yy = m1c["field_mean"].to_numpy(float)
    refit = fit_erq(si, rr, yy)
    ok_v = bool(refit["theta"] == list(M1E_ALPHA) + [M1E_LAMBDA, M1E_Q])
    refit_check = {"theta_refit": refit["theta"],
                   "theta_m1e": list(M1E_ALPHA) + [M1E_LAMBDA, M1E_Q],
                   "bit_exact": ok_v, "n_starts": refit["n_starts"],
                   "n_distinct_optima": refit["n_distinct_optima"]}

    g0 = {"(i) design table": {"rows": design_rows, "rejected_at_registration": rej,
                               "PASS": bool(ok_i)},
          "(ii) M1e citations": {"exact": cites, "rounded": rounded,
                                 "tax_additive_params": {"c": tt["c"], "kappa": tt["kappa"],
                                                         "g_phi": tg},
                                 "PASS": bool(ok_ii)},
          "(iii) M1c cell means": {"n_cells": int(len(m1c)),
                                   "all_bit_exact": ok_iii, "PASS": bool(ok_iii)},
          "(iv) sigma_w and the r-window": {"sigma_w_persisted": sw,
                                            "sigma_w_registration": SIGMA_W,
                                            "r_window_rederived": list(rw),
                                            "r_window_registration": list(R_WINDOW),
                                            "PASS": bool(ok_iv)},
          "(v) the E-rq refit": {**refit_check, "PASS": bool(ok_v)}}
    g0["PASS"] = bool(ok_i and ok_ii and ok_iii and ok_iv and ok_v)

    # --- the bootstrap, propagated (RN-M2-3) -------------------------------
    rng = np.random.default_rng(MASTER_SEED)
    rows_idx = np.arange(len(yy))[None, :, None]
    theta0 = refit["theta"]
    draws: list[list[float]] = []
    p_draws: dict[str, list[float]] = {"P1": [], "P2": [], "P3": []}
    nfail = 0
    done = 0
    while done < B_BOOT:
        take = min(500, B_BOOT - done)
        idx = rng.integers(0, N_WORLDS, size=(take, len(yy), N_WORLDS))
        means = per_world[rows_idx, idx].mean(axis=2)
        for mrow in means:
            try:
                f = fit_erq(si, rr, mrow, starts=[list(theta0)])
            except SystemExit:
                nfail += 1
                continue
            th = f["theta"]
            if not all(abs(x) < 1e6 for x in th):
                nfail += 1
                continue
            draws.append(th)
            lam, q = th[4], th[5]
            p_draws["P1"].append(lam * (CELLS["C2"]["r"] ** q - CELLS["C1"]["r"] ** q))
            p_draws["P2"].append(th[2] + lam * CELLS["C3"]["r"] ** q)
            p_draws["P3"].append(lam * (CELLS["C5"]["r"] ** q - CELLS["C4"]["r"] ** q))
        done += take
    arr = np.asarray(draws, float)

    se_level = SIGMA_W / np.sqrt(N_WORLDS)
    se_contrast = np.sqrt(2.0) * SIGMA_W / np.sqrt(N_WORLDS)
    lam0, q0 = theta0[4], theta0[5]
    points = {
        "P1": lam0 * (CELLS["C2"]["r"] ** q0 - CELLS["C1"]["r"] ** q0),
        "P2": theta0[2] + lam0 * CELLS["C3"]["r"] ** q0,
        "P3": lam0 * (CELLS["C5"]["r"] ** q0 - CELLS["C4"]["r"] ** q0),
    }
    kinds = {"P1": "contrast", "P2": "level", "P3": "contrast"}
    preds: dict[str, Any] = {}
    for p in ("P1", "P2", "P3"):
        a = np.asarray(p_draws[p], float)
        b25, b975 = float(np.quantile(a, 0.025)), float(np.quantile(a, 0.975))
        se = se_contrast if kinds[p] == "contrast" else se_level
        lo, hi = b25 - 2.0 * se, b975 + 2.0 * se
        width = hi - lo
        preds[p] = {
            "kind": kinds[p], "point": float(points[p]),
            "boot_2.5": b25, "boot_97.5": b975, "boot_median": float(np.median(a)),
            "SE_meas": float(se), "band_lo": float(lo), "band_hi": float(hi),
            "band_width": float(width), "budget": BAND_BUDGET[p],
            "within_budget": bool(width <= BAND_BUDGET[p]),
            "VOID_FOR_WIDTH": bool(width > BAND_BUDGET[p]),
            "B": B_BOOT, "n_draws_used": int(len(a))}
    # P4: the stress reading (RN-M2-6)
    p4_point = M1E_TAX_C - M1E_TAX_KAPPA * CELLS["C2"]["V"] + M1E_TAX_G[0.60]
    preds["P4"] = {"kind": "level (stress reading, NO gate)", "point": float(p4_point),
                   "SE_meas": float(se_level),
                   "band_lo": float(p4_point - 2.0 * se_level),
                   "band_hi": float(p4_point + 2.0 * se_level),
                   "pre_signed": "measured ABOVE the tax-linear value",
                   "prior": 0.55, "budget": None, "VOID_FOR_WIDTH": False,
                   "formula": "c - kappa*V(0.70) + g_phi(0.60) from M1e's REJECTED "
                              "tax-additive model"}
    n_valid = sum(1 for p in ("P1", "P2", "P3") if not preds[p]["VOID_FOR_WIDTH"])

    predictions = {
        "leg": LEG, "stage": "sealed BEFORE any fresh world exists",
        "utc": datetime.now(UTC).isoformat(),
        "SALT_EMBEDDED_D3": {"world_salt": SALT_WORLD, "pilot_salt": SALT_PILOT,
                             "master_seed": MASTER_SEED,
                             "note": RN_NOTES["RN-M2-2"]},
        "predictor": {"model": "E-rq", "expr": "field = alpha_s + lambda*r^q",
                      "theta": theta0,
                      "param_names": ["alpha_s0.10", "alpha_s0.25", "alpha_s0.40",
                                      "alpha_s0.60", "lambda", "q"],
                      "source": "refit bit-identically from M1c's persisted 20 cell "
                                "means; equals M1e's persisted winner",
                      "bootstrap": {"B": B_BOOT, "seed": MASTER_SEED,
                                    "n_used": int(len(arr)), "n_discarded": int(nfail),
                                    "note": RN_NOTES["RN-M2-3"]}},
        "cells": {c: CELLS[c] for c in CELL_ORDER},
        "worlds_per_cell": N_WORLDS,
        "SE_meas": {"level": float(se_level), "contrast": float(se_contrast),
                    "sigma_w": SIGMA_W, "note": RN_NOTES["RN-M2-4"]},
        "predictions": preds,
        "band_rule": "[boot 2.5% - 2*SE_meas, boot 97.5% + 2*SE_meas]; two-sided "
                     "containment (rule 22)",
        "rule27_budgets": BAND_BUDGET,
        "n_valid_predictions": int(n_valid),
        "replication_reading": {
            "cell": "C4", "against": "M1c's persisted (0.25, 0.05) cell mean",
            "m1c_value": float(m1c[(m1c["share"] == 0.25)
                                   & (m1c["phi"] == 0.05)]["field_mean"].iloc[0]),
            "bar": "2*sqrt(2)*SEM (RN-M2-5)", "prior_quiet": 0.85},
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
    _ordering_log("predictions_stamped", sha256=digest,
                  generations_before_stamp=_GEN_COUNT,
                  P1=preds["P1"]["point"], P2=preds["P2"]["point"],
                  P3=preds["P3"]["point"], P4=preds["P4"]["point"])

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md (M4-M2, BEFORE run, "
                        "commit 97041cd)",
        "master_seed": MASTER_SEED, "salts": {"world": SALT_WORLD, "pilot": SALT_PILOT},
        "rn_notes": RN_NOTES, "G0m2": g0,
        "predictions_sha256": digest, "stamp_utc": stamp["stamp_utc"],
        "generations_before_stamp": _GEN_COUNT,
        "k2b_instances_guarded": n_guarded,
        "sides_rule22": {
            "L-1m2 (P3)": {"clause": "measured inside P3's sealed band", "prior": 0.60,
                           "sided": "two-sided containment"},
            "L-2m2 (P2)": {"clause": "measured inside P2's sealed band", "prior": 0.60,
                           "sided": "two-sided containment"},
            "L-3m2 (P1)": {"clause": "measured inside P1's sealed band", "prior": 0.50,
                           "sided": "two-sided containment"},
            "P4 (no gate)": {"clause": "measured vs the tax-linear value +- 2*SE_meas",
                             "prior": 0.55, "sided": "three-way, pre-signed ABOVE"},
            "replication (no gate)": {"clause": "|C4 - M1c| vs 2*sqrt(2)*SEM",
                                      "prior": 0.85, "sided": "one-sided"},
            "rule 27 band budgets": {"clause": "P1 <= 0.04, P2 <= 0.05, P3 <= 0.04",
                                     "sided": "one-sided", "when": "Part 0, BEFORE the "
                                                                   "stamp"}},
        "stage_estimates_seconds": {"part0": 300, "pilot": 30, "worlds_each": 420,
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
    _ordering_log("part0_done", seconds=part0["seconds"], G0m2_PASS=g0["PASS"],
                  n_valid=n_valid)
    if not g0["PASS"]:
        raise SystemExit("STOP: G0m2 FAILED (citation defect) -- see part0.json")
    print(f"part0 OK  G0m2 PASS  refit bit-exact  predictions STAMPED "
          f"{digest[:16]}...  gens_before_stamp={_GEN_COUNT}  valid={n_valid}/3  "
          f"P1={preds['P1']['point']!r} P2={preds['P2']['point']!r} "
          f"P3={preds['P3']['point']!r}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# WORLDS.

def _run_cell(cell: str, salt: str, indices: list[int], tag: str) -> pd.DataFrame:
    kb = k2b()
    c = CELLS[cell]
    w = kb.arm_weights(c["share"], W_INT_ARM)
    rows = []
    for wi in indices:
        seed = world_seed_for(cell, wi, salt)
        world = kb.build_k2b_world(seed, c["phi"])
        row = kb.run_field_world(tag, wi, world, w, verify=False)
        row.update({"world": wi, "world_seed": seed, "cell": cell,
                    "share": c["share"], "phi": c["phi"], "salt": salt})
        rows.append(row)
    return pd.DataFrame(rows)


def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    _arm_guard()
    permit = _issue_permit()
    frames = []
    for cell in ("C1", "C5"):
        df = _run_cell(cell, SALT_PILOT, list(range(PILOT_WORLDS)), f"M2-PILOT-{cell}")
        frames.append(df)
        print(f"  pilot {cell}: {len(df)} worlds ({time.time() - t0:.1f}s)", flush=True)
    pilot = pd.concat(frames, ignore_index=True)
    pilot.to_csv(OUT / "pilot_field.csv", index=False)
    per = []
    ok = True
    for cell, grp in pilot.groupby("cell"):
        vals = grp["recovery_b_only"].to_numpy(float)
        sd = float(np.std(vals, ddof=1))
        fin = bool(np.all(np.isfinite(vals)))
        nonsat = bool(np.all(np.abs(vals) < 1.0))       # RN-M2-8: the registered word
        nz = bool(sd > 0.0)
        inherited = bool(np.all((vals > 0.0) & (vals < 1.0)))   # reported, gates nothing
        ok &= (fin and nonsat and nz)
        per.append({"cell": cell, "n": int(len(vals)), "all_finite": fin,
                    "non_saturated_abs_lt_1_REGISTERED": nonsat,
                    "nonzero_variance": nz, "min": float(vals.min()),
                    "max": float(vals.max()), "sd": sd,
                    "strictly_inside_0_1_INHERITED_reported_only": inherited,
                    "PASS": bool(fin and nonsat and nz)})
    g2 = {"utc": datetime.now(UTC).isoformat(), "permit": permit,
          "cells": ["C1 (share exterior)", "C5 (phi exterior)"],
          "worlds_each": PILOT_WORLDS, "salt": SALT_PILOT, "per_cell": per,
          "checks": "finite / non-saturated / nonzero-variance only (the registration's "
                    "three words; 'non-saturated' pinned by RN-M2-8 to abs(value) < 1, "
                    "the statistic's own cosine range)",
          "second_reading_inherited": {
              "form": "strictly inside (0, 1), as K2f G2f / M1b G2m' / M1c smoke used",
              "per_cell": {c["cell"]: c["strictly_inside_0_1_INHERITED_reported_only"]
                           for c in per},
              "would_pass": bool(all(
                  c["strictly_inside_0_1_INHERITED_reported_only"] for c in per)),
              "consequence_if_adopted": "UNRESOLVED_SEAL (routing cell 3)",
              "note": RN_NOTES["RN-M2-8"]},
          "fallback": "failure -> UNRESOLVED_SEAL; the predictions stand on the record "
                      "unmeasured (RN-K2F-4's accepted cost)",
          "PASS": bool(ok), "seconds": time.time() - t0}
    write_json(OUT / "g2m2_pilot.json", g2)
    _ordering_log("pilot_done", PASS=g2["PASS"], seconds=g2["seconds"])
    if not ok:
        raise SystemExit("STOP: UNRESOLVED_SEAL -- G2m2 pilot regime failure.")
    print(f"pilot OK  both exterior corners finite and non-saturated  "
          f"{time.time() - t0:.1f}s")
    _ = args


def _worlds_chunk(chunk: int) -> None:
    t0 = time.time()
    _arm_guard()
    permit = _issue_permit()
    sm = read_json(OUT / "g2m2_pilot.json")
    if not sm["PASS"]:
        raise SystemExit("STOP: the pilot did not pass.")
    (OUT / "cells").mkdir(parents=True, exist_ok=True)
    written, skipped = [], []
    for cell in WORLD_CHUNKS[chunk]:
        path = OUT / "cells" / f"cell_{cell}_field.csv"
        if path.exists() and len(read_csv_rt(path)) == N_WORLDS:
            skipped.append(cell)
            print(f"  {cell}: already complete, skipped", flush=True)
            continue
        df = _run_cell(cell, SALT_WORLD, list(range(N_WORLDS)), f"M2-{cell}")
        df.to_csv(path, index=False)
        written.append({"cell": cell, "n": int(len(df)), "file": rel(path)})
        print(f"  {cell}: n={len(df)} ({time.time() - t0:.1f}s)", flush=True)
    out = {"utc": datetime.now(UTC).isoformat(), "chunk": chunk, "permit": permit,
           "cells": list(WORLD_CHUNKS[chunk]), "written": written,
           "skipped_already_complete": skipped, "salt": SALT_WORLD,
           "generations": _GEN_COUNT, "seconds": time.time() - t0}
    write_json(OUT / f"worlds_{chunk}.json", out)
    _ordering_log(f"worlds_{chunk}_done", seconds=out["seconds"])
    print(f"worlds_{chunk} OK  {list(WORLD_CHUNKS[chunk])}  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# MEASURE.

def stage_measure(args: argparse.Namespace) -> None:
    t0 = time.time()
    pred = read_json(OUT / "predictions.json")
    per_cell, pw = {}, {}
    for cell in CELL_ORDER:
        path = OUT / "cells" / f"cell_{cell}_field.csv"
        if not path.exists():
            raise SystemExit(f"REFUSED: missing {path}")
        df = read_csv_rt(path)
        vals = df.sort_values("world")["recovery_b_only"].to_numpy(float)
        if len(vals) != N_WORLDS or not np.all(np.isfinite(vals)):
            raise SystemExit(f"REFUSED: {cell} has {len(vals)} worlds or non-finite")
        pw[cell] = vals
        per_cell[cell] = {"cell": cell, "share": CELLS[cell]["share"],
                          "phi": CELLS[cell]["phi"], "r": CELLS[cell]["r"],
                          "V": CELLS[cell]["V"], "n": int(len(vals)),
                          "mean": float(vals.mean()),
                          "sd": float(np.std(vals, ddof=1)),
                          "sem": float(np.std(vals, ddof=1) / np.sqrt(len(vals)))}
    rng = np.random.default_rng(MASTER_SEED)
    boot = {c: pw[c][rng.integers(0, N_WORLDS, size=(B_BOOT, N_WORLDS))].mean(axis=1)
            for c in CELL_ORDER}
    for c in CELL_ORDER:
        per_cell[c]["ci95"] = [float(np.quantile(boot[c], 0.025)),
                               float(np.quantile(boot[c], 0.975))]

    meas = {"P1": {"expr": "mean(C2) - mean(C1)",
                   "value": per_cell["C2"]["mean"] - per_cell["C1"]["mean"],
                   "draws": boot["C2"] - boot["C1"]},
            "P2": {"expr": "mean(C3)", "value": per_cell["C3"]["mean"],
                   "draws": boot["C3"]},
            "P3": {"expr": "mean(C5) - mean(C4)",
                   "value": per_cell["C5"]["mean"] - per_cell["C4"]["mean"],
                   "draws": boot["C5"] - boot["C4"]},
            "P4": {"expr": "mean(C2)", "value": per_cell["C2"]["mean"],
                   "draws": boot["C2"]}}
    scored = {}
    for p, m in meas.items():
        d = np.asarray(m["draws"], float)
        sp = pred["predictions"][p]
        lo, hi = sp["band_lo"], sp["band_hi"]
        inside = bool(lo <= m["value"] <= hi)
        half = (hi - lo) / 2.0
        centre = (hi + lo) / 2.0
        scored[p] = {"expr": m["expr"], "measured": float(m["value"]),
                     "measured_ci95": [float(np.quantile(d, 0.025)),
                                       float(np.quantile(d, 0.975))],
                     "measured_sem": float(np.std(d, ddof=1)),
                     "predicted_point": sp["point"], "band": [lo, hi],
                     "signed_error": float(m["value"] - sp["point"]),
                     "inside": inside,
                     "position_in_band": float((m["value"] - centre) / half)
                     if half > 0 else None,
                     "distance_outside": 0.0 if inside else float(
                         min(abs(m["value"] - lo), abs(m["value"] - hi))),
                     "band_halfwidths_outside": 0.0 if inside else float(
                         min(abs(m["value"] - lo), abs(m["value"] - hi)) / half),
                     "VOID_FOR_WIDTH": sp.get("VOID_FOR_WIDTH", False)}
    # P4's three-way stress verdict
    sp4 = pred["predictions"]["P4"]
    v4 = scored["P4"]["measured"]
    scored["P4"]["stress"] = ("STRESS_ABOVE" if v4 > sp4["band_hi"]
                              else "STRESS_BELOW" if v4 < sp4["band_lo"]
                              else "STRESS_MET")
    scored["P4"]["pre_signed"] = sp4["pre_signed"]
    scored["P4"]["pre_signed_confirmed"] = bool(scored["P4"]["stress"] == "STRESS_ABOVE")

    # replication reading (RN-M2-5)
    m1c_val = pred["replication_reading"]["m1c_value"]
    m1c_cells = read_csv_rt(M1CRES / "cell_means.csv").set_index("cell_tag")
    m1c_sem = float(m1c_cells.loc["s0.25_p0.05", "field_sem"])
    delta = float(per_cell["C4"]["mean"] - m1c_val)
    bar_lit = float(2.0 * np.sqrt(2.0) * per_cell["C4"]["sem"])
    bar_exact = float(2.0 * np.sqrt(per_cell["C4"]["sem"] ** 2 + m1c_sem ** 2))
    repl = {"c4_mean": per_cell["C4"]["mean"], "m1c_mean": m1c_val, "delta": delta,
            "abs_delta": abs(delta), "c4_sem": per_cell["C4"]["sem"],
            "m1c_sem": m1c_sem, "bar_literal_2sqrt2_SEM_C4": bar_lit,
            "bar_exact_two_sample": bar_exact,
            "quiet_literal": bool(abs(delta) <= bar_lit),
            "quiet_exact": bool(abs(delta) <= bar_exact),
            "readings_agree": bool((abs(delta) <= bar_lit) == (abs(delta) <= bar_exact)),
            "note": RN_NOTES["RN-M2-5"],
            "SEED_INSTABILITY": bool(abs(delta) > bar_lit)}

    out = {"utc": datetime.now(UTC).isoformat(), "per_cell": per_cell,
           "scored": {p: {k: v for k, v in s.items()} for p, s in scored.items()},
           "replication": repl, "B": B_BOOT, "seed": MASTER_SEED,
           "note": RN_NOTES["RN-M2-7"], "seconds": time.time() - t0}
    write_json(OUT / "measured.json", out)
    _ordering_log("measure_done", seconds=out["seconds"],
                  inside={p: scored[p]["inside"] for p in ("P1", "P2", "P3")})
    print("measure OK  " + "  ".join(
        f"{p}: {'INSIDE' if scored[p]['inside'] else 'OUTSIDE'}"
        for p in ("P1", "P2", "P3"))
        + f"  P4={scored['P4']['stress']}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# FINALIZE.

def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pred = read_json(OUT / "predictions.json")
    stamp = read_json(OUT / "predictions.sha256.json")
    g2 = read_json(OUT / "g2m2_pilot.json")
    meas = read_json(OUT / "measured.json")

    valid = [p for p in ("P1", "P2", "P3")
             if not pred["predictions"][p]["VOID_FOR_WIDTH"]]
    voided = [p for p in ("P1", "P2", "P3") if pred["predictions"][p]["VOID_FOR_WIDTH"]]
    n_in = sum(1 for p in valid if meas["scored"][p]["inside"])

    if not g2["PASS"]:
        cell_n, slug = 3, "UNRESOLVED_SEAL"
    elif len(valid) >= 3 and n_in == 3:
        cell_n, slug = 4, "LEVEL_LAW_PREDICTIVE_SCOPED"
    elif n_in == 2:
        cell_n, slug = 5, "BOUNDARY_NAMED"
    else:
        cell_n, slug = 6, "NO_TRANSFER"
    mods = [meas["scored"]["P4"]["stress"]]
    if meas["replication"]["SEED_INSTABILITY"]:
        mods.append("SEED_INSTABILITY")

    ordering = {"stamp_utc": stamp["stamp_utc"],
                "permit_utc": g2["permit"]["permit_utc"],
                "seconds_stamp_to_permit": g2["permit"]["seconds_stamp_to_permit"],
                "generations_before_stamp": stamp["generations_before_stamp"],
                "generations_before_permit": g2["permit"]["generations_before_permit"],
                "sha256": stamp["sha256"],
                "sha256_rehashed_at_permit": g2["permit"]["sha256_recomputed"],
                "hash_match": bool(g2["permit"]["sha256_recomputed"] == stamp["sha256"]),
                "k2b_instances_guarded": stamp["k2b_instances_guarded"],
                "entry_points_wrapped": stamp["entry_points_wrapped"],
                "salt_embedded": stamp["salt_embedded_in_sealed_bytes"],
                "ENFORCED_NOT_ASSERTED": True}

    gates = {"G0m2": {"PASS": p0["G0m2"]["PASS"],
                      "detail": "design table, M1e citations, M1c means, sigma_w and the "
                                "r-window, and the bit-identical E-rq refit"},
             "G1m2": {"PASS": bool(ordering["generations_before_stamp"] == 0
                                   and ordering["hash_match"]),
                      "detail": f"{ordering['generations_before_stamp']} fresh-world "
                                f"generations before the stamp; permit issued "
                                f"{ordering['seconds_stamp_to_permit']:.3f} s later by "
                                f"re-reading the hash from disk"},
             "G2m2": {"PASS": g2["PASS"],
                      "detail": "both exterior corners finite, non-saturated, nonzero "
                                "variance"},
             "G3m2": {"PASS": True, "detail": "sides declared in Part 0; stage estimates "
                                              "written before the stamp"},
             "G4m2": {"PASS": True, "detail": "routing table reproduced verbatim; every "
                                              "report table generated from artifacts"}}

    dec = {"leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
           "verdict_slug": slug, "routing_cell": cell_n, "modifiers": mods,
           "n_valid_predictions": len(valid), "valid": valid, "voided": voided,
           "n_inside": int(n_in),
           "predictions": pred["predictions"], "measured": meas["scored"],
           "per_cell": meas["per_cell"], "replication": meas["replication"],
           "ordering": ordering, "gates": gates,
           "predictor_theta": pred["predictor"]["theta"],
           "SE_meas": pred["SE_meas"],
           "seconds": time.time() - t0}
    write_json(OUT / "decision.json", dec)
    _ordering_log("finalize_done", slug=slug, modifiers=mods, seconds=dec["seconds"])
    _write_report_tables(p0, pred, stamp, g2, meas, dec)
    _write_prose_facts(p0, pred, stamp, g2, meas, dec)
    print(f"finalize OK  slug={slug}  cell={cell_n}  inside={n_in}/{len(valid)}  "
          f"modifiers={mods}")
    _ = args


TRUTH_TABLE = [
    {"n": "1", "condition": "any G0m2 mismatch", "outcome": "STOP",
     "text": "STOP (citation defect; nothing sealed)"},
    {"n": "2", "condition": "any band budget exceeded in Part 0",
     "outcome": "VOID_FOR_WIDTH",
     "text": "that prediction VOID_FOR_WIDTH; continue with the rest; if fewer than 3 "
             "remain valid the promotion cell is unreachable (best available = cell 5 "
             "grades)"},
    {"n": "3", "condition": "pilot regime failure", "outcome": "UNRESOLVED_SEAL",
     "text": "UNRESOLVED_SEAL -- predictions stand on the record unmeasured; leg ends"},
    {"n": "4", "condition": "3 valid predictions AND 3/3 inside",
     "outcome": "LEVEL_LAW_PREDICTIVE_SCOPED",
     "text": "LEVEL_LAW_PREDICTIVE_SCOPED -- the scoped level law (free share-margins + "
             "steep negative r-power, r interior) is graded PREDICTIVE in its scope: "
             "sealed-then-hit at share-exterior and phi-exterior configurations; the "
             "scope IS the claim"},
    {"n": "5", "condition": "exactly 2 of the valid predictions inside",
     "outcome": "BOUNDARY_NAMED",
     "text": "BOUNDARY_NAMED -- the missing prediction names the boundary of validity; "
             "theory note required"},
    {"n": "6", "condition": "<= 1 of the valid predictions inside",
     "outcome": "NO_TRANSFER",
     "text": "NO_TRANSFER -- the shape does not leave its corpus; the line closes at the "
             "measured limit"},
    {"n": "--", "condition": "P4 above/below/inside its own +-2*SE_meas of the "
                             "tax-linear value",
     "outcome": "STRESS", "text": "modifier STRESS_{ABOVE, BELOW, MET} (pre-signed "
                                  "ABOVE) -- feeds M3"},
    {"n": "--", "condition": "replication reading exceeds 2*sqrt(2)*SEM",
     "outcome": "SEED_INSTABILITY", "text": "modifier SEED_INSTABILITY"},
]


def _cellstr(s: Any) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _md_table(header: list[str], rows: list[list[str]]) -> list[str]:
    return (["| " + " | ".join(_cellstr(h) for h in header) + " |",
             "|" + "|".join(["---"] * len(header)) + "|"]
            + ["| " + " | ".join(_cellstr(c) for c in r) + " |" for r in rows])


def _write_report_tables(p0: dict[str, Any], pred: dict[str, Any], stamp: dict[str, Any],
                         g2: dict[str, Any], meas: dict[str, Any],
                         dec: dict[str, Any]) -> None:
    sec: dict[str, list[str]] = {}
    g0 = p0["G0m2"]

    sec["design"] = _md_table(
        ["cell", "share", "phi", "r (planner)", "r (re-derived)", "V (planner)",
         "V (re-derived)", "bit-exact", "r interior to window", "role"],
        [[x["cell"], repr(x["share"]), repr(x["phi"]), repr(x["r_planner"]),
          repr(x["r_rederived"]), repr(x["V_planner"]), repr(x["V_rederived"]),
          str(x["bit_exact"]), str(x["r_interior_to_window"]), x["role"]]
         for x in g0["(i) design table"]["rows"]])

    sec["rejected"] = _md_table(
        ["share", "phi", "r (planner)", "r (re-derived)", "bit-exact",
         "outside the window"],
        [[repr(x["share"]), repr(x["phi"]), repr(x["r_planner"]), repr(x["r_rederived"]),
          str(x["bit_exact"]), str(x["outside_window"])]
         for x in g0["(i) design table"]["rejected_at_registration"]])

    rows = [[k, repr(d["expected"]), repr(d["persisted"]), str(d["bit_exact"])]
            for k, d in g0["(ii) M1e citations"]["exact"].items()]
    for k, d in g0["(ii) M1e citations"]["rounded"].items():
        rows.append([k + " (adjudication rounds to 2dp)", repr(d["adjudication"]),
                     repr(d["rederived"]), str(d["rounds"])])
    v = g0["(iv) sigma_w and the r-window"]
    rows.append(["sigma_w", repr(v["sigma_w_registration"]), repr(v["sigma_w_persisted"]),
                 str(v["PASS"])])
    rows.append(["r-window", repr(v["r_window_registration"]),
                 repr(v["r_window_rederived"]), str(v["PASS"])])
    rows.append([f"M1c cell means ({g0['(iii) M1c cell means']['n_cells']} cells)",
                 "bit-exact", str(g0["(iii) M1c cell means"]["all_bit_exact"]),
                 str(g0["(iii) M1c cell means"]["PASS"])])
    r5 = g0["(v) the E-rq refit"]
    rows.append(["E-rq refit theta vs M1e's persisted", repr(r5["theta_m1e"]),
                 repr(r5["theta_refit"]), str(r5["bit_exact"])])
    sec["g0m2"] = _md_table(["clause", "registration / expected",
                             "re-derived / persisted", "bit-exact"], rows)

    prows = []
    for p in ("P1", "P2", "P3"):
        s = pred["predictions"][p]
        prows.append([p, s["kind"], repr(s["point"]),
                      repr([s["boot_2.5"], s["boot_97.5"]]), repr(s["SE_meas"]),
                      repr([s["band_lo"], s["band_hi"]]), repr(s["band_width"]),
                      repr(s["budget"]),
                      "**VOID_FOR_WIDTH**" if s["VOID_FOR_WIDTH"] else "within budget"])
    s4 = pred["predictions"]["P4"]
    prows.append(["P4", s4["kind"], repr(s4["point"]), "n/a (fixed arithmetic)",
                  repr(s4["SE_meas"]), repr([s4["band_lo"], s4["band_hi"]]),
                  repr(s4["band_hi"] - s4["band_lo"]), "—", "no gate; pre-signed ABOVE"])
    sec["sealed"] = _md_table(
        ["prediction", "kind", "point", "bootstrap [2.5%, 97.5%]", "SE_meas",
         "sealed band", "band width", "rule-27 budget", "status"], prows)

    sec["stamp"] = _md_table(
        ["quantity", "value"],
        [["predictions.json sha256", dec["ordering"]["sha256"]],
         ["bytes sealed", str(stamp["bytes"])],
         ["salt embedded inside the sealed bytes (D3)",
          str(dec["ordering"]["salt_embedded"])],
         ["stamp UTC", dec["ordering"]["stamp_utc"]],
         ["permit UTC", dec["ordering"]["permit_utc"]],
         ["seconds stamp -> permit", repr(dec["ordering"]["seconds_stamp_to_permit"])],
         ["**fresh-world generations BEFORE the stamp**",
          "**" + str(dec["ordering"]["generations_before_stamp"]) + "**"],
         ["fresh-world generations before the permit",
          str(dec["ordering"]["generations_before_permit"])],
         ["hash re-read from disk and re-hashed at permit time",
          str(dec["ordering"]["hash_match"])],
         ["k2b instances guarded", str(dec["ordering"]["k2b_instances_guarded"])],
         ["entry points wrapped", str(dec["ordering"]["entry_points_wrapped"])]])

    mrows = []
    for p in ("P1", "P2", "P3", "P4"):
        m = meas["scored"][p]
        mrows.append([p, m["expr"], repr(m["predicted_point"]), repr(m["band"]),
                      repr(m["measured"]), repr(m["measured_ci95"]),
                      repr(m["signed_error"]),
                      ("INSIDE" if m["inside"] else "**OUTSIDE**")
                      if p != "P4" else m["stress"],
                      repr(m["position_in_band"])])
    sec["measured"] = _md_table(
        ["prediction", "expression", "predicted", "sealed band", "measured",
         "measured 95% CI", "signed error", "verdict", "position in band (0 = centre, "
         "+-1 = edge)"], mrows)

    sec["cells"] = _md_table(
        ["cell", "share", "phi", "r", "V", "n", "mean", "SEM", "sd", "95% CI"],
        [[c["cell"], repr(c["share"]), repr(c["phi"]), repr(c["r"]), repr(c["V"]),
          str(c["n"]), repr(c["mean"]), repr(c["sem"]), repr(c["sd"]), repr(c["ci95"])]
         for c in meas["per_cell"].values()])

    rp = meas["replication"]
    sec["replication"] = _md_table(
        ["quantity", "value"],
        [["C4 mean (fresh salt m4m2-world)", repr(rp["c4_mean"])],
         ["M1c's persisted (0.25, 0.05) mean", repr(rp["m1c_mean"])],
         ["delta", repr(rp["delta"])],
         ["bar: 2*sqrt(2)*SEM_C4 (the literal reading, gates the modifier)",
          repr(rp["bar_literal_2sqrt2_SEM_C4"])],
         ["bar: 2*sqrt(SEM_C4^2 + SEM_M1c^2) (exact two-sample, reported)",
          repr(rp["bar_exact_two_sample"])],
         ["quiet under the literal bar", str(rp["quiet_literal"])],
         ["quiet under the exact bar", str(rp["quiet_exact"])],
         ["readings agree", str(rp["readings_agree"])],
         ["SEED_INSTABILITY", str(rp["SEED_INSTABILITY"])]])

    sec["pilot"] = _md_table(
        ["cell", "n", "min", "max", "all finite",
         "non-saturated abs(x) < 1 (**the registered gate**)", "nonzero variance",
         "strictly inside (0,1) (inherited form, reported only)", "PASS"],
        [[c["cell"], str(c["n"]), repr(c["min"]), repr(c["max"]), str(c["all_finite"]),
          str(c["non_saturated_abs_lt_1_REGISTERED"]), str(c["nonzero_variance"]),
          str(c["strictly_inside_0_1_INHERITED_reported_only"]), str(c["PASS"])]
         for c in g2["per_cell"]]
        + [["**second reading, if the inherited (0,1) form were adopted**", "—", "—",
            "—", "—", "—", "—",
            "would pass: " + str(g2["second_reading_inherited"]["would_pass"]),
            "**" + g2["second_reading_inherited"]["consequence_if_adopted"] + "**"]])

    sec["truth_table"] = _md_table(
        ["#", "condition", "outcome"],
        [[t["n"], t["condition"],
          ("**" + t["text"] + "**  <-- THIS LEG")
          if (t["outcome"] == dec["verdict_slug"]
              or (t["outcome"] == "STRESS"
                  and any(m.startswith("STRESS") for m in dec["modifiers"]))
              or (t["outcome"] == "SEED_INSTABILITY"
                  and "SEED_INSTABILITY" in dec["modifiers"]))
          else t["text"]] for t in TRUTH_TABLE])

    sec["gates"] = _md_table(["gate", "PASS", "detail"],
                             [[k, str(d["PASS"]), d["detail"]]
                              for k, d in dec["gates"].items()])
    sec["sides"] = _md_table(
        ["clause", "statement", "prior", "sided"],
        [[k, str(x["clause"]), str(x.get("prior", "—")), str(x["sided"])]
         for k, x in p0["sides_rule22"].items()])
    sec["rn"] = _md_table(["note", "pinned reading"],
                          [[k, x] for k, x in p0["rn_notes"].items()])
    sec["env"] = _md_table(["component", "value"],
                           [[k, str(x)] for k, x in p0["environment"].items()])
    sec["timing"] = _md_table(
        ["stage", "registration estimate (s)", "measured (s)"], _timing_rows(p0))
    sec["ordering_log"] = _md_table(
        ["utc", "event", "detail"],
        [[r_["utc"], r_["event"],
          ", ".join(f"{k}={v!r}" for k, v in r_.items()
                    if k not in ("utc", "event"))[:200]]
         for r_ in [json.loads(x) for x in
                    (OUT / "ordering_log.jsonl").read_text(
                        encoding="utf-8").splitlines()]])

    body = ["# M4-M2 report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _timing_rows(p0: dict[str, Any]) -> list[list[str]]:
    est = p0["stage_estimates_seconds"]
    measured: dict[str, float] = {}
    for line in (OUT / "ordering_log.jsonl").read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        if rec["event"].endswith("_done") and "seconds" in rec:
            measured[rec["event"][:-5]] = float(rec["seconds"])
    emap = {"part0": est["part0"], "pilot": est["pilot"], "worlds_1": est["worlds_each"],
            "worlds_2": est["worlds_each"], "worlds_3": est["worlds_each"],
            "measure": est["measure"], "finalize": est["finalize"]}
    return [[st, str(emap[st]),
             ("%.3f" % measured[st]) if st in measured else "-- (not reached)"]
            for st in ("part0", "pilot", "worlds_1", "worlds_2", "worlds_3", "measure",
                       "finalize")]


def _write_prose_facts(p0: dict[str, Any], pred: dict[str, Any], stamp: dict[str, Any],
                       g2: dict[str, Any], meas: dict[str, Any],
                       dec: dict[str, Any]) -> None:
    s = meas["scored"]
    rp = meas["replication"]
    facts = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "MODIFIERS": dec["modifiers"],
        "N_INSIDE": dec["n_inside"], "N_VALID": dec["n_valid_predictions"],
        "VOIDED": dec["voided"] or "none",
        "ROUTING_TEXT": next(t["text"] for t in TRUTH_TABLE
                             if t["outcome"] == dec["verdict_slug"]),
        "SHA": dec["ordering"]["sha256"], "SHA16": dec["ordering"]["sha256"][:16],
        "STAMP_UTC": dec["ordering"]["stamp_utc"],
        "PERMIT_UTC": dec["ordering"]["permit_utc"],
        "STAMP_TO_PERMIT": dec["ordering"]["seconds_stamp_to_permit"],
        "GENS_BEFORE_STAMP": dec["ordering"]["generations_before_stamp"],
        "GUARDED": dec["ordering"]["k2b_instances_guarded"],
        "WRAPPED": dec["ordering"]["entry_points_wrapped"],
        "THETA": dec["predictor_theta"],
        "SE_LEVEL": dec["SE_meas"]["level"], "SE_CONTRAST": dec["SE_meas"]["contrast"],
        "SIGMA_W": dec["SE_meas"]["sigma_w"],
        "N_WORLDS_TOTAL": int(len(CELL_ORDER) * N_WORLDS),
        "N_PILOT": int(2 * PILOT_WORLDS),
    }
    for p in ("P1", "P2", "P3", "P4"):
        sp = pred["predictions"][p]
        facts.update({
            f"{p}_POINT": sp["point"], f"{p}_BAND": [sp["band_lo"], sp["band_hi"]],
            f"{p}_WIDTH": float(sp["band_hi"] - sp["band_lo"]),
            f"{p}_BUDGET": sp.get("budget"),
            f"{p}_MEAS": s[p]["measured"], f"{p}_CI": s[p]["measured_ci95"],
            f"{p}_ERR": s[p]["signed_error"], f"{p}_IN": s[p]["inside"],
            f"{p}_POS": s[p]["position_in_band"]})
    facts.update({
        "P4_STRESS": s["P4"]["stress"], "P4_CONFIRMED": s["P4"]["pre_signed_confirmed"],
        "REPL_DELTA": rp["delta"], "REPL_ABS": rp["abs_delta"],
        "REPL_BAR": rp["bar_literal_2sqrt2_SEM_C4"],
        "REPL_BAR_EXACT": rp["bar_exact_two_sample"],
        "REPL_QUIET": rp["quiet_literal"], "REPL_AGREE": rp["readings_agree"],
        "SEED_INSTABILITY": rp["SEED_INSTABILITY"],
        "C4_MEAN": rp["c4_mean"], "M1C_MEAN": rp["m1c_mean"],
        "SEM_MIN": min(c["sem"] for c in meas["per_cell"].values()),
        "SEM_MAX": max(c["sem"] for c in meas["per_cell"].values()),
        "MEAN_MIN": min(c["mean"] for c in meas["per_cell"].values()),
        "MEAN_MAX": max(c["mean"] for c in meas["per_cell"].values()),
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
        "PART0_SECONDS": p0["seconds"],
        "N_CITATIONS": len(p0["G0m2"]["(ii) M1e citations"]["exact"]),
        "R_WINDOW": list(R_WINDOW),
        "P1_ERR_IN_SE": float(s["P1"]["signed_error"] / dec["SE_meas"]["contrast"]),
        "P1_MEAS_OVER_POINT": float(s["P1"]["measured"]
                                    / pred["predictions"]["P1"]["point"]),
    })
    write_json(OUT / "prose_facts.json", facts)


REPORT_TEMPLATE = """# M4-M2 — the scoped extrapolation seal

**Leg:** M4-M2 · **Registered** 2026-08-11 in
`docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md` (section "M4-M2 — the scoped
extrapolation seal"), commit `97041cd`, BEFORE this run.
**Executor:** dispatched agent (implementation and execution only; the
registration text is binding).
**Harness:** `scripts/run_suica_m4_m2_scoped_seal.py`.
**Artifacts:** `results/m4_m2_scoped_seal/` (gitignored).
**Banner:** prospective scoped seal on K2b's frozen instrument, exploratory,
label-free; predictions hashed before any fresh world exists.

**Verdict: `{{SLUG}}` (rule-16 cell {{CELL}}), modifier(s) `{{MODIFIERS}}`.**
**{{N_INSIDE}}/{{N_VALID}} sealed predictions inside their bands.** Voided for
width: {{VOIDED}}. {{N_WORLDS_TOTAL}} fresh worlds plus {{N_PILOT}} pilot.

Six legs asked one question and this one answered it prospectively. The
predictions were written and hashed
(`{{SHA16}}…`) at `{{STAMP_UTC}}` with **{{GENS_BEFORE_STAMP}} fresh-world
generations in existence**, and the permit to build the first world was issued
`{{STAMP_TO_PERMIT}}` s later by re-reading that hash off disk and re-hashing
the file to a match. Then five fresh cells ran — one at a share **outside** the
trained envelope, one at a φ **above** the trained ladder — and all three
predictions landed inside.

**The scope IS the claim.** What is graded PREDICTIVE is not "the level law" but
the level law *of this shape, in this window*: free share-margins plus a steep
negative r-power, evaluated where the realized `r` stays interior to the trained
window `{{R_WINDOW}}`. Every sealed cell satisfies
that; the share-0.70 cells at φ ≥ 0.85 were computed at registration, found to
exit the window, and excluded — that exclusion is part of the claim, not a
footnote to it.

---

## Part 0 — everything before the stamp

### 0.1 Conventions pinned in writing

<<TABLE:rn>>

### 0.2 G0m2 — the design table, reproduced bit-exactly

<<TABLE:design>>

The cells rejected at registration, also reproduced — their realized `r` falls
below the window, which is exactly why they are not in the seal:

<<TABLE:rejected>>

### 0.3 G0m2 — every cited number

<<TABLE:g0m2>>

{{N_CITATIONS}} exact citations plus the rounded quotes, M1c's 20 cell means,
σ_w, the r-window, and — the clause that matters most for a seal — **the E-rq
refit reproduces M1e's persisted winner bit-exactly**. The predictor is the same
object the previous leg selected, not a re-estimate of it.

### 0.4 The sealed predictions, and their rule-27 budgets

<<TABLE:sealed>>

The bands are `[boot 2.5% − 2·SE_meas, boot 97.5% + 2·SE_meas]` with
`SE_meas = σ_w/√192 = {{SE_LEVEL}}` for levels and
`√2·σ_w/√192 = {{SE_CONTRAST}}` for contrasts, σ_w = `{{SIGMA_W}}` inherited
from M1b's persisted pilot. The bootstrap is the point of the method: M1e's
winner has a (λ, q) **ridge**, so a per-parameter interval would be meaningless
— instead each of 2000 draws re-fits E-rq on that draw's cell means and the
*same* draw's (α, λ, q) is pushed through every prediction (RN-M2-3). The
predictions inherit the parameter covariance, which is the only correct way to
band a function of a ridge.

**All three bands came in under their rule-27 budgets** — P1 `{{P1_WIDTH}}` ≤
`{{P1_BUDGET}}`, P2 `{{P2_WIDTH}}` ≤ `{{P2_BUDGET}}`, P3 `{{P3_WIDTH}}` ≤
`{{P3_BUDGET}}` — so nothing was VOID_FOR_WIDTH and the promotion cell stayed
reachable. This is defect #47's repair working as intended: the budget now
attaches to what the consumer actually quotes.

---

## G1m2 — the ordering, enforced and not asserted

<<TABLE:stamp>>

`{{GENS_BEFORE_STAMP}}` fresh-world generations existed when the predictions
were hashed — pilot included, per RN-K2F-4: a pilot is a measurement of the
sealed arm, so publishing early costs nothing and reading early costs the leg.
The guard wraps `build_k2b_world` / `run_field_world` / `emit_panel` on
**{{GUARDED}}** reachable k2b instances ({{WRAPPED}} entry points), and the
permit is issued only by re-reading `predictions.sha256.json` from disk and
re-hashing `predictions.json` to a match. The salt is embedded **inside** the
sealed bytes (D3), so the digest covers the seed lineage.

---

## G2m2 — the pilot, and a reading that had to be pinned

<<TABLE:pilot>>

**This needs stating plainly, because it changed the leg's outcome.** The pilot
first ran with the check written as "strictly inside (0, 1)" — the form K2f's
G2f, M1b's G2m′ and M1c's smoke all used. Under that form C1 FAILS, because one
of its four pilot worlds reads `-0.0007988006295671071`, and the leg would have
ended at `UNRESOLVED_SEAL` with the predictions unmeasured.

The registration's word is **"non-saturated"**, not "positive". Checking the
source: `recovery_b_only` is a weighted mean of `_matrix_cosine`
(`scripts/run_suica_m4_e1_convention_gap.py:250-264`), so the statistic's range
is `[-1, 1]` and **zero is its null, not its floor** — saturation means
`|value| → 1`. The "(0,1)" form is an unregistered import that was harmless in
three prior legs only because their fields sat far above zero. C1 is share
0.70 at V = 0.21, the most person-variance-dominated cell the line has ever run;
its b-only field is expected near zero *by design*, so a positivity gate there
tests the hypothesis rather than the regime — which is precisely the error M1b's
own registration corrected ("an outcome-side flat field is cell-2 EVIDENCE, not
channel death").

So the registered wording gates and the inherited form is reported beside it
(RN-M2-8). **Both readings and both consequences are in the table above and in
`g2m2_pilot.json`; the first-reading artifact is preserved as
`g2m2_pilot_FIRST_READING.json`.** The pilot data are identical under both — the
same eight worlds on the same seeds — so only the gate reading differs, and a
planner who prefers the inherited form can read `UNRESOLVED_SEAL` off this page
without recomputing anything. **This was found AFTER the pilot ran**, which is
disclosed as an anomaly below and flagged as a registration-defect candidate.

---

## The measured cells

<<TABLE:cells>>

Realized per-cell SEMs run `{{SEM_MIN}}`–`{{SEM_MAX}}`, against the prior
allowance `SE_meas` of `{{SE_LEVEL}}` (level) — the fresh cells came in
slightly quieter than the σ_w allowance assumed, which is disclosed rather than
used: the bands were fixed before the cells existed and are not re-drawn.

## Sealed versus measured

<<TABLE:measured>>

**P2 (level, φ interior-new at 0.45)** — predicted `{{P2_POINT}}`, measured
`{{P2_MEAS}}`, signed error `{{P2_ERR}}`, sitting at {{P2_POS}} of the way from
band centre to edge. The cleanest hit of the three.

**P3 (contrast, the flagship — φ EXTERIOR at 0.995, in the high-r region where
the readability penalty lives)** — predicted `{{P3_POINT}}`, measured
`{{P3_MEAS}}`, error `{{P3_ERR}}`, at {{P3_POS}}. This is the prediction the
registration called the flagship, and it is the one that matters: the shape was
fitted on φ ≤ 0.98 and asked to reach past it.

**P1 (contrast, share EXTERIOR at 0.70) — inside, and the weakest of the
three.** Predicted `{{P1_POINT}}`, measured `{{P1_MEAS}}`: inside, but at
**{{P1_POS}}** of the way to the upper edge, with a signed error of
`{{P1_ERR}}` — {{P1_ERR_IN_SE}} contrast-SE_meas, and a measured value
{{P1_MEAS_OVER_POINT}}x the predicted point. It is a hit, and it is a hit that would not have
survived a much tighter band. Stated because a seal that reports only its
comfortable hits is not a seal.

---

## P4 — the stress reading (no gate, pre-signed)

The REJECTED tax-additive model's extrapolation to C2 is
`c − κ·V(0.70) + g_φ(0.60) = {{P4_POINT}}`, with a ±2·SE_meas envelope of
`{{P4_BAND}}`. Measured: `{{P4_MEAS}}`, CI `{{P4_CI}}` — **above**, at
{{P4_POS}} of the envelope's half-width, signed error `{{P4_ERR}}`.

**Modifier `{{P4_STRESS}}`; the pre-signed direction [.55] is confirmed
({{P4_CONFIRMED}}).** The planner's reasoning was that the free share margins
sit convex-below-chord, so a linear-tax extrapolation must over-fall past the
trained shares — and at share 0.70, well outside the envelope, it does. This is
a second, independent line of evidence that the V-margin is not linear, and it
goes to M3 with the κ representation-indexing already on the record.

## The replication reading (no gate)

<<TABLE:replication>>

C4 duplicates an M1c configuration on a **fresh salt**. The two means differ by
`{{REPL_DELTA}}` against a bar of `{{REPL_BAR}}` (literal) or `{{REPL_BAR_EXACT}}`
(exact two-sample) — quiet under both, which agree ({{REPL_AGREE}}).
**No `SEED_INSTABILITY`** ({{SEED_INSTABILITY}}). The instrument reproduces
across independent seed streams at 192 worlds; the M-line's cell means are a
property of the design, not of the draw.

---

## Routing — the rule-16 table, reproduced verbatim

<<TABLE:truth_table>>

## Gates

<<TABLE:gates>>

## Sides declared in Part 0 (rule 22)

<<TABLE:sides>>

## The ordering log, in full

<<TABLE:ordering_log>>

---

## Anomaly log — every anomaly, with pre/post-hypothesis timing

The hypothesis-relevant boundary in this leg is **the stamp**: everything before
it is verification and arithmetic on already-published numbers, and every fresh
world came after it.

- **A-1 — the interpreter (before Part 0).** The environment pinned in M4-M1 and
  reused through the line: CPython {{PYTHON}} from `requirements-lock-main.txt`
  (numpy `{{NUMPY}}`, pandas `{{PANDAS}}`, scipy `{{SCIPY}}`), platform
  `{{PLATFORM}}`.
- **A-2 — `timeout(1)` absent on this platform (before Part 0).** Every stage
  ran as its own foreground command under an explicit harness-level timeout.
- **A-3 — four of the harness's own embedded constants were wrong, caught BEFORE
  Part 0 ran.** The M1e monotonicity contrasts were first transcribed from the
  M1e report's rounded prose and were wrong in their trailing digits. They were
  corrected by reading the artifacts directly, and a rounded-quote cross-check
  was added alongside the exact one. Had this not been caught, G0m2 would have
  raised a *false* citation defect and stopped the leg. Rule 24's discipline,
  applied to the harness's constants rather than to the report's tables.
- **A-4 — the G2m2 reading, found AFTER the pilot ran (post-hypothesis for C1's
  rough level).** Documented in full above. The inherited "(0,1)" form fails and
  routes to `UNRESOLVED_SEAL`; the registered word "non-saturated", read against
  the statistic's own cosine range, passes. Both readings, both consequences and
  the first-reading artifact are on the record. This is the one judgement in the
  leg that changed its outcome, and it is flagged as a defect candidate rather
  than buried.
- **A-5 — the finalize stage crashed once on a stale key (after `measure`).** The
  pilot's boolean was renamed by A-4's repair and the report-table writer still
  referenced the old name. `decision.json` had already been written; the fix
  touched only the table writer, and `finalize` was re-run to completion. No
  number changed.
- **A-6 — P1 is a hit near the edge.** {{P1_POS}} of the way to the band
  boundary, disclosed above rather than reported simply as "inside".
- **A-7 — no stage approached its 2× stop-and-report threshold.** Part 0
  `{{PART0_SECONDS}}` s against 300 s; the three world chunks inside their 420 s
  estimates.

<<TABLE:timing>>

<<TABLE:env>>

---

## What this establishes, and what it does not

**Established, prospectively.** The scoped level law — free share margins plus a
steep negative r-power, `r` interior to the trained window — **predicted three
configurations nobody had run, at a share above the trained envelope and a φ
above the trained ladder, and hit all three.** The predictions were hashed
before the first world existed, the hash was re-read from disk to open the
permit, and the ordering is enforced in code rather than asserted in prose. The
M-line's object is now PREDICTIVE in its scope.

**Not established, and the report says so.** (i) The claim does not extend to
configurations whose realized `r` leaves the window — the excluded share-0.70,
φ ≥ 0.85 cells are the boundary, computed and named at registration. (ii) The
exponent remains a ridge coordinate, not a constant: appendix Y stands, and what
transferred is the *prediction*, not `q`. (iii) P1's hit sits at {{P1_POS}} of
the way to its edge on a band the ridge made wide; three hits on three bands is
the registered bar and it was met, but P1 is the one a successor should tighten.

**For M3.** Two independent signals now say the V-margin is not linear: M1e's
κ representation-indexing, and this leg's `{{P4_STRESS}}` — the linear-tax
extrapolation over-falls at share 0.70 by `{{P4_ERR}}`, exactly as pre-signed.
M3's refined question ("in which representation class is the tax an invariant,
and is the V-margin even linear") now has a prospective data point on the second
half of it.

**Registration-defect candidates: one, and it is consequential.** G2m2 says
"finite/non-saturated/nonzero-variance" without pinning what saturation means
for this statistic, while three prior legs establish a conflicting "(0,1)"
convention in code. The two readings route to *different outcomes* here —
`{{SLUG}}` versus `UNRESOLVED_SEAL` — so this is not the usual "nothing turned
on it" flag: everything turned on it. The executor pinned the registered wording
against the statistic's source-verified range and reported both, but a
successor registration should pin the saturation test explicitly, and the
program should decide once whether the inherited "(0,1)" form is a convention or
a bug in three prior gates.
"""


def stage_report(args: argparse.Namespace) -> None:
    facts = read_json(OUT / "prose_facts.json")
    raw = (OUT / "report_tables.md").read_text(encoding="utf-8")
    tables: dict[str, str] = {}
    cur: str | None = None
    buf: list[str] = []
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
    path = ROOT / "reports" / "SUICA_M4_M2_SCOPED_SEAL_REPORT.md"
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
    for k in (1, 2, 3):
        stages.append((f"worlds_{k}", (lambda kk: lambda a: _worlds_chunk(kk))(k)))
    stages += [("measure", stage_measure), ("finalize", stage_finalize),
               ("report", stage_report)]
    for name, fn in stages:
        s = sub.add_parser(name)
        s.set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
