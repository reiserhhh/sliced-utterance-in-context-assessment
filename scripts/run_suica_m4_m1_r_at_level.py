#!/usr/bin/env python3
"""M4-M1 -- r-AT-LEVEL ON A DECOLLINEARIZED FACTORIAL.

Registered in docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md ("M4-M1 -- r-at-level on a
decollinearized factorial", commit 140e927) BEFORE this file existed.
Implementation and execution only; the registration text is binding.

K2f restored the level law as an intercept minus the variance tax and proved, in
the same breath, that its corpus cannot say whether the intercept hides lam*r^q:
corr(r, V) = -0.9643543785903034 over the 26 compiled rows, because the legacy
legs exercised phi only at {0.90, 0.98} and moved r almost entirely through
share -- which also moves V.  `person_share_design(share, int_share)` has NO phi
argument, so phi moves r at EXACTLY fixed V.  This leg runs the factorial that
K2f could not: share x phi, 20 cells, 32 fresh worlds each.

    part0    G0m anchors (bit-exact) + G1m design arithmetic and its gates
             + G3m(a) sides + G3m(c) stage estimates + G4m truth table.
             NO world may exist.
    pilot    G2m: 4 corner cells x 4 worlds on the pilot salt; finiteness,
             non-saturation, and rule-3 LIVENESS on the realized card channel.
    power    G3m(b): sigma_w from the 16 pilot worlds, df-inflated, then a
             B_proj=500 parametric replication of the 20-cell experiment under
             two q truths.  Gate: q-width proxy <= 0.50 under BOTH.
    worlds_a/b/c/d   the 4 x 5 main cells (one share level per chunk), 32 worlds.
    fit      four pre-declared forms, leave-one-CELL-out selection, within-cell
             world-block bootstrap at B=2000.
    rule13   the >=10xB re-run at any flagged boundary.
    finalize L-1/L-2/L-3 adjudication through the registered truth table, L-4
             as a reading, decision.json and the generated report tables.
    report   renders reports/SUICA_M4_M1_R_AT_LEVEL_REPORT.md from artifacts
             (rule 24: no table cell and no prose number is hand-typed).

ORDERING IS ENFORCED, NOT ASSERTED.  Every k2b entry point that can build or
measure a world is wrapped at arm time on EVERY reachable k2b instance
(RN-K2F-5), and the permit is issued only after re-reading the preceding
stage's artifacts from disk and checking their gates.

Artifacts: results/m4_m1_r_at_level/ (gitignored)
"""

from __future__ import annotations

import argparse
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
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "results" / "m4_m1_r_at_level"
RES = ROOT / "results"
K2F = RES / "m4_k2f_level_law"

# ---------------------------------------------------------------------------
# Registration constants (all pinned in the M1 registration; none invented here).

LEG = "M4-M1"
BANNER = ("synthetic worlds on K2b's frozen instrument, exploratory, label-free; "
          "a share x phi factorial that breaks K2f's -0.964 r/V collinearity")

MASTER_SEED = 20260811
SALT_WORLD = "m4m1-world"
SALT_PILOT = "m4m1-pilot"

SHARES = (0.10, 0.25, 0.40, 0.60)
PHIS = (0.60, 0.70, 0.80, 0.90, 0.98)
PHIS_LADDER_G1M = (0.45, 0.60, 0.75, 0.90, 0.98)      # G1m fallback (rule 17)
PHIS_LADDER_LIVENESS = (0.90, 0.92, 0.94, 0.96, 0.98)  # G2m liveness fallback
N_WORLDS = 32
PILOT_SHARES = (0.10, 0.60)
PILOT_PHIS_INDEX = (0, -1)     # the corner phis of whichever ladder is adopted
PILOT_WORLDS = 4

B_BOOT = 2000
B_BOOT_HIGH = 20000
B_PROJ = 500

INT_SHARE = 0.0                # K2F-FRESH carrier, verbatim
W_INT_ARM = "zero"             # K2F-FRESH carrier, verbatim

# --- G1m gate bars ---------------------------------------------------------
SHARE_ENVELOPE = (0.02, 0.6634207990183637)
G1M_V_RATIO_MIN = 2.0
G1M_R_RATIO_MIN = 1.20
G1M_R_RATIO_MIN_LEVELS = 2
G1M_CORR_MAX = 0.30

# --- G2m / G3m bars --------------------------------------------------------
G2M_LIVENESS_SE_MULT = 2.0
G3M_PROJ_WIDTH_MAX = 0.50
G3M_DF = 12                    # 16 pilot worlds - 4 pilot cells
G3M_CHI2_Q = 0.10

# --- lean bars -------------------------------------------------------------
L1_Q_WIDTH_MAX = 0.60
L2_RESPONSE_BAND = (1.71, 1.98)
L3_KAPPA_CI = (0.5202855978239498, 0.8612166024267973)
TIE_REL = 0.05
BOUNDARY_REL = 0.05
L4_MIN_LEVELS = 3

# --- cited constants (K2f / D1 / D-open), verified bit-exactly in G0m ------
K2F_F2_LAMBDA = 0.18021628978547316
K2F_F2_Q = -0.009622064624441264
K2F_F2_KAPPA = 0.750086268225045
K2F_F2_P = 0.2064406330042716
K2F_F2_LOO = 0.0061559195350209
K2F_F2_Q_CI = (-0.3792124136721057, 0.5313115708778163)
K2F_F2_KAPPA_CI = (0.5202855978239498, 0.8612166024267973)
K2F_CORR_RV = -0.9643543785903034
SEALED_LAMBDA = 0.17417497661611914
SEALED_Q = 1.8528700746510731
SEALED_KAPPA_HAT = -0.7220359963712748

ANCHORS = {
    "r_040_090": 0.6185853753498524,
    "r_045_090": 0.5889058864943755,
    "V_045": 0.13500000000000004,
    "V_040": 0.12000000000000004,
    "dopen_m4_level": 0.09350089316336324,
    "r_030_090": 0.6758917867864564,
    "r_030_098": 0.645057248597175,
    "r_050_090": 0.558364277337817,
    "r_050_098": 0.5193517935368367,
}
THEORY_DOC = ROOT / "docs" / "SUICA_IDENTITY_THEORY_V1.md"
THEORY_BAND_STRING = "[1.71, 1.98]"

# ---------------------------------------------------------------------------
# RN-M1 notes (rule 9 / rule 12).  PINNED IN PART 0, BEFORE ANY WORLD EXISTS.
#
# RN-M1-1 (carrier inheritance).  "Inherits K2F-FRESH's carrier verbatim except
#   (share, phi)" is read as: int_share = 0.0, w_int_arm = "zero", the K1-pinned
#   985-author panel with K2b's F2 m-multiset and 4 contexts, field statistic
#   `recovery_b_only` from `k2b.run_field_world`, cell level = the mean over the
#   cell's worlds (K2f's `_level_from_raw` aggregation).  K2F-FRESH's master_seed
#   (20260826) and salt (m4k2f-world) are NOT inherited: the M1 registration pins
#   its own master_seed 20260811 and its own salts, and those control.  Because
#   int_share = 0 no `int:` carrier appears, so K2d's weight dispatcher -- which
#   K2f had to install on every reachable k2b -- is NOT needed here and is not
#   installed; `k2b.arm_weights(share, "zero")` parses every M1 arm natively.
#
# RN-M1-2 (seed string).  The registration pins "master_seed 20260811; main
#   worlds salt m4m1-world, hash-derived per (cell, world-index 0..31); pilot
#   salt m4m1-pilot, indices 0..3" but not the hashed STRING.  Pinned reading,
#   K2f's `world_seed_for` lineage extended by the cell key:
#       v8.stable_bucket(f"{MASTER_SEED}-{share!r}-{phi!r}-{world}",
#                        salt=<salt>, modulus=2**31 - 1)
#   `repr` of the float is used so the key round-trips exactly.  Pilot and main
#   streams are disjoint by SALT, as the registration states, not by index.
#
# RN-M1-3 (G2m liveness object).  The registration prefers "the k2b-side
#   realized card-attenuation statistic if one is persisted per world ... else
#   the pilot field contrast (catastrophic deadness only)".  Finding: k2b
#   computes a realized card attenuation AT WORLD GRAIN --
#   `card_channel_frame(world, w, world_seed)`
#   (scripts/run_suica_m4_k2b_t4_branch.py:392-503, the frame is stamped with
#   `world_seed`), pooled by `bootstrap_card`
#   (scripts/run_suica_m4_k2b_t4_branch.py:505-509) into `r_card_b_raw`
#   (scripts/run_suica_m4_k2b_t4_branch.py:486) -- and this is the very object
#   k2b's own G2 lever-liveness check uses
#   (scripts/run_suica_m4_k2b_t4_branch.py:944-963).  It is NOT written into any
#   persisted per-world field CSV (`run_field_world`'s row schema,
#   scripts/run_suica_m4_k2b_t4_branch.py:633-646, carries no card column), so a
#   literal reading of "persisted per world" would route to the fallback.
#   PINNED READING: the card statistic is the GATE (it is the rule-3 object --
#   the channel the manipulation must move -- and the registration's parenthetical
#   instructs the executor to pin its source, i.e. to find one); the pilot field
#   contrast is computed and reported as the declared fallback reading.  BOTH are
#   persisted.  If they disagree the disagreement is reported as an anomaly and
#   the card statistic controls.
#
# RN-M1-4 (correlation convention).  "corr" is read as PEARSON, verified in G0m
#   by reproducing K2f's quoted -0.9643543785903034 from `compiled_rows.csv`
#   under that convention before any M1 number is used.
#
# RN-M1-5 (stage chunking).  The registration's stage-estimate list names five
#   stages; the execution convention is "chunked foreground stages, every stage
#   under 600 s".  G3m(b)'s projection needs pilot sigma_w and must PASS before
#   the first main world, so it is run as its own foreground stage `power`
#   between `pilot` and `worlds_a`, and the >=10xB rule-13 re-run as its own
#   stage `rule13` between `fit` and `finalize`.  Ordering is unchanged and
#   strengthened (each is permit-gated).  Both registration estimates and this
#   leg's chunk estimates are written into Part 0 BEFORE the pilot; overruns are
#   reported against the REGISTRATION's estimates where a chunk maps onto one.
#
# RN-M1-6 (lambda-vs-zero boundary scale).  Rule 13's boundary test is relative
#   to the bar; the cell-2/cell-3 split tests "lambda CI contains 0", where a
#   relative tolerance is undefined.  Pinned: boundary-adjacent iff
#   min(|lambda_lo|, |lambda_hi|) <= 0.05 * |lambda_hat|.
#
# RN-M1-7 (L-4 monotonicity).  "a monotone same-sign pattern in >=3/4 share
#   levels" admits two readings: (A) sign agreement of Spearman(residual, phi) in
#   >=3 levels, and (B) the stricter |rho| == 1 (perfect monotonicity) AND sign
#   agreement in >=3 levels.  BOTH are computed and reported; L-4 carries no
#   adjudication weight, so neither is adopted over the other.
#
# RN-M1-8 (the STOP diagnostic; added when G1m failed, BEFORE any world existed
#   and therefore before any hypothesis-relevant number could exist -- zero
#   worlds were generated in this leg).  Truth-table cell 1 obliges the executor
#   to STOP and hand the planner a defect, not a repair.  To make that handoff
#   actionable the `diagnose` stage measures HOW unsatisfiable gate (d) is:
#   (1) the infimum of |corr(r, V)| over every 5-point distinct phi ladder in
#   (0.001, 0.999) at the REGISTERED shares, and (2) the best value reachable
#   when the shares are also freed inside gate (a)'s envelope subject to gate
#   (b)'s V max/min >= 2.  Both are pure design arithmetic on the pinned
#   deterministic maps -- no world, no field, no fit.  Searches are deterministic
#   (fixed grids; the random-share search is seeded with the leg's master seed).
#   NOTHING here is adopted: the leg's verdict is the registered STOP.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-M1-1": "carrier inheritance: int_share 0, w_int_arm 'zero', K2b panel pins, "
               "recovery_b_only, cell level = mean over worlds; M1's OWN master_seed "
               "and salts control; no K2d dispatcher needed (no int: carrier)",
    "RN-M1-2": "seed string pinned: v8.stable_bucket(f'{MASTER_SEED}-{share!r}-{phi!r}-"
               "{world}', salt=<m4m1-world|m4m1-pilot>, modulus=2**31-1); streams "
               "disjoint by salt",
    "RN-M1-3": "G2m liveness gates on the k2b-side realized card attenuation "
               "r_card_b_raw at world grain (k2b:392-503 + :505-509 + :486, the object "
               "k2b's own G2 uses at :944-963); it is not written into any persisted "
               "per-world field CSV (k2b:633-646), so the declared field-contrast "
               "fallback is ALSO computed and reported; the card statistic controls",
    "RN-M1-4": "corr = Pearson, verified by reproducing K2f's -0.9643543785903034 from "
               "compiled_rows.csv before any M1 number is used",
    "RN-M1-5": "stage chunking: G3m(b) runs as its own foreground stage `power` between "
               "`pilot` and `worlds_a`; the >=10xB rule-13 re-run as its own stage "
               "`rule13`; ordering unchanged and permit-gated",
    "RN-M1-6": "lambda-vs-zero boundary: adjacent iff min(|lo|,|hi|) <= 0.05*|lambda_hat|",
    "RN-M1-7": "L-4 monotonicity read BOTH ways (sign-agreement; and |rho|==1 plus sign "
               "agreement); L-4 adjudicates nothing so neither is adopted",
    "RN-M1-8": "the STOP diagnostic: on truth-table cell 1 the `diagnose` stage measures "
               "HOW unsatisfiable gate (d) is (the infimum of |corr(r,V)| over all "
               "5-point phi ladders at the registered shares, and the best reachable "
               "value with shares also freed inside gate (a) subject to gate (b)); pure "
               "design arithmetic, deterministic, adopted as NOTHING -- the verdict is "
               "the registered STOP",
}

# --- RN-M1-8 diagnostic search pins (deterministic) ------------------------
DIAG_PHI_LO, DIAG_PHI_HI, DIAG_PHI_N = 0.001, 0.999, 100
DIAG_PHI_COARSE_STRIDE = 4
DIAG_SHARE_N = 40
DIAG_RANDOM_DRAWS = 4000

# ---------------------------------------------------------------------------
# Module loading -- ONE importlib loader chain for this leg (RN-K2F-5).

_MODS: dict[str, Any] = {}


def _load(name: str) -> Any:
    if name in _MODS:
        return _MODS[name]
    spec = importlib_util().spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    if spec is None or spec.loader is None:      # pragma: no cover
        raise SystemExit(f"REFUSED: cannot load {name}")
    mod = importlib_util().module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    _MODS[name] = mod
    return mod


def importlib_util() -> Any:
    import importlib.util
    return importlib.util


def k2b() -> Any:
    return _load("run_suica_m4_k2b_t4_branch")


def k2c() -> Any:
    return _load("run_suica_m4_k2c_matched_pairs")


def k2e() -> Any:
    return _load("run_suica_m4_k2e_double_matching")


# ---------------------------------------------------------------------------
# ORDERING ENFORCEMENT.  Armed at first world use, never disarmed.

_GEN_COUNT = 0
_PERMIT: str | None = None
_ARMED = False


def _ordering_log(event: str, **kw: Any) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rec = {"utc": datetime.now(UTC).isoformat(), "event": event, **kw}
    with (OUT / "ordering_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True, default=float) + "\n")


def _reachable_k2b() -> list[Any]:
    """Every DISTINCT k2b module object reachable from this process (RN-K2F-5:
    the published legs use private importlib loaders that ignore sys.modules, so
    a guard on one instance would be enforced in name only)."""
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
                    if _PERMIT is None:
                        _ordering_log("REFUSED_world_generation", entry_point=nm,
                                      count=_GEN_COUNT)
                        raise SystemExit(
                            f"STOP (ordering): world generation via {nm} attempted "
                            f"with no permit issued."
                        )
                    return orig(*a, **kw)
                wrapped.__name__ = f"guarded_{nm}"
                return wrapped

            setattr(kb, fname, make(original, fname))
    _ARMED = True
    _ordering_log("ordering_guard_armed", n_k2b_instances=len(mods),
                  entry_points=["build_k2b_world", "run_field_world", "emit_panel"],
                  n_wrapped=3 * len(mods))
    return len(mods)


def _issue_permit(kind: str) -> dict[str, Any]:
    """Permit ONLY after re-reading the preceding stage's artifacts from disk and
    checking their gates there.  `pilot` needs Part 0; `main` needs Part 0, the
    G2m pilot and the G3m-b projection."""
    global _PERMIT
    p0p = OUT / "part0.json"
    if not p0p.exists():
        raise SystemExit("STOP (ordering): part0.json absent; run `part0` first.")
    p0 = read_json(p0p)
    if not (p0["G0m"]["PASS"] and p0["G1m"]["PASS"]):
        raise SystemExit("STOP (ordering): Part 0 gates did not pass.")
    rec: dict[str, Any] = {"kind": kind, "part0_utc": p0["utc"],
                           "generations_before_permit": _GEN_COUNT}
    if kind == "main":
        g2p, g3p = OUT / "g2m_pilot.json", OUT / "g3mb_power.json"
        if not g2p.exists():
            raise SystemExit("STOP (ordering): g2m_pilot.json absent; run `pilot`.")
        if not g3p.exists():
            raise SystemExit("STOP (ordering): g3mb_power.json absent; run `power`.")
        g2, g3 = read_json(g2p), read_json(g3p)
        if not g2["PASS"]:
            raise SystemExit("STOP (ordering): G2m did not pass.")
        if not g3["PASS"]:
            raise SystemExit("STOP (ordering): G3m-b did not pass.")
        rec.update({"g2m_utc": g2["utc"], "g3mb_utc": g3["utc"],
                    "g2m_PASS": True, "g3mb_PASS": True})
    if _GEN_COUNT != 0:
        raise SystemExit(f"STOP (ordering): {_GEN_COUNT} generations before permit.")
    _PERMIT = kind
    rec["permit_utc"] = datetime.now(UTC).isoformat()
    _ordering_log("permit_issued", **rec)
    return rec


# ---------------------------------------------------------------------------
# Utilities (K2f lineage).

def read_csv_rt(path: Path) -> pd.DataFrame:
    """Round-trip float parsing (k2a:118 / k2b:178-180), every artifact."""
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


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    return float(np.corrcoef(a, b)[0, 1])


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = pd.Series(np.asarray(a, float)).rank().to_numpy()
    rb = pd.Series(np.asarray(b, float)).rank().to_numpy()
    return pearson(ra, rb)


def cell_id(share: float, phi: float) -> str:
    """RN-M1-2's seed key: full-precision, round-trippable."""
    return f"{share!r}|{phi!r}"


def cell_tag(share: float, phi: float) -> str:
    return f"s{share:.2f}_p{phi:.2f}"


def world_seed_for(share: float, phi: float, world: int, salt: str) -> int:
    v8 = k2b().v8
    return int(v8.stable_bucket(f"{MASTER_SEED}-{cell_id(share, phi)}-{world}",
                                salt=salt, modulus=2 ** 31 - 1))


def r_of(share: float, phi: float) -> float:
    """k2c:186-191 -> k2b:533-583.  Pure algebra; no world is generated."""
    return k2c().predicted_attenuation(share, phi)


def v_of(share: float) -> float:
    """k2e:234-241 -> k2b.arm_shares.  NEVER assumed linear in share."""
    return k2e().person_share_design(share, INT_SHARE)


# ---------------------------------------------------------------------------
# The FOUR pre-declared forms (no others).

def f1(theta: np.ndarray, r: np.ndarray, v: np.ndarray) -> np.ndarray:
    lam, q, kap = theta
    return lam * r ** q - kap * v


def f1e(theta: np.ndarray, r: np.ndarray, v: np.ndarray) -> np.ndarray:
    lam, q, kap, eps = theta
    return lam * r ** q - kap * v - eps


def f2(theta: np.ndarray, r: np.ndarray, v: np.ndarray) -> np.ndarray:
    lam, q, kap, p = theta
    return lam * r ** q - kap * v * r ** p


def f3(theta: np.ndarray, r: np.ndarray, v: np.ndarray) -> np.ndarray:
    lam, q, kap = theta
    return (lam - kap * v) * r ** q


FORMS: dict[str, dict[str, Any]] = {
    "F1": {"fn": f1, "names": ("lambda", "q", "kappa"), "k": 3,
           "expr": "field = lambda*r^q - kappa*V", "bounded": False},
    "F1e": {"fn": f1e, "names": ("lambda", "q", "kappa", "epsilon"), "k": 4,
            "expr": "field = lambda*r^q - kappa*V - epsilon, epsilon in [0, 0.05]",
            "bounded": True},
    "F2": {"fn": f2, "names": ("lambda", "q", "kappa", "p"), "k": 4,
           "expr": "field = lambda*r^q - kappa*V*r^p", "bounded": False},
    "F3": {"fn": f3, "names": ("lambda", "q", "kappa"), "k": 3,
           "expr": "field = (lambda - kappa*V)*r^q", "bounded": False},
}
FORM_ORDER = ("F1", "F1e", "F2", "F3")

# Optimizer pins -- K2f's OPT verbatim, plus F1e's epsilon bound.
OPT = {
    "routine": "scipy.optimize.least_squares",
    "method": "trf",
    "jac": "2-point (numerical)",
    "bounds": "unbounded, x_scale=1.0, EXCEPT F1e's epsilon in [0, 0.05]",
    "ftol": 1e-14, "xtol": 1e-14, "gtol": 1e-14,
    "max_nfev": 20000,
    "loss": "linear (plain least squares)",
    "scipy_version": None,
}
START_LAMBDA = (0.05, SEALED_LAMBDA, 0.5)
START_Q = (-0.5, 0.0, 0.5, 1.0, SEALED_Q, 3.0)
START_KAPPA = (0.0, -SEALED_KAPPA_HAT, 2.0)
START_P = (0.0, 1.0, SEALED_Q)
START_EPS = (0.0, 0.01, 0.03)
EPS_BOUNDS = (0.0, 0.05)
OPT_SAME_SSE_TOL = 1e-12


def starts_for(form: str) -> list[list[float]]:
    out: list[list[float]] = []
    for lam in START_LAMBDA:
        for q in START_Q:
            for kap in START_KAPPA:
                if form == "F2":
                    for p in START_P:
                        out.append([lam, q, kap, p])
                elif form == "F1e":
                    for e in START_EPS:
                        out.append([lam, q, kap, e])
                else:
                    out.append([lam, q, kap])
    return out


def bounds_for(form: str) -> tuple[list[float], list[float]] | None:
    if form != "F1e":
        return None
    return ([-np.inf, -np.inf, -np.inf, EPS_BOUNDS[0]],
            [np.inf, np.inf, np.inf, EPS_BOUNDS[1]])


def fit_form(form: str, r: np.ndarray, v: np.ndarray, y: np.ndarray,
             starts: list[list[float]] | None = None) -> dict[str, Any]:
    spec = FORMS[form]
    fn = spec["fn"]
    bnd = bounds_for(form)

    def resid(theta: np.ndarray) -> np.ndarray:
        with np.errstate(over="ignore", invalid="ignore"):
            pred = fn(theta, r, v)
        pred = np.where(np.isfinite(pred), pred, 1e12)
        return pred - y

    best: dict[str, Any] | None = None
    sses: list[float] = []
    n_conv = 0
    grid = starts if starts is not None else starts_for(form)
    for s0 in grid:
        x0 = np.asarray(s0, float)
        if bnd is not None:
            x0 = np.clip(x0, np.asarray(bnd[0], float), np.asarray(bnd[1], float))
        try:
            kw: dict[str, Any] = dict(method=OPT["method"], jac="2-point",
                                      ftol=OPT["ftol"], xtol=OPT["xtol"],
                                      gtol=OPT["gtol"], max_nfev=OPT["max_nfev"])
            if bnd is not None:
                kw["bounds"] = bnd
            res = least_squares(resid, x0, **kw)
        except Exception:                                   # noqa: BLE001
            continue
        if not res.success and res.status <= 0:
            continue
        n_conv += 1
        sse = float(np.sum(res.fun ** 2))
        if not np.isfinite(sse):
            continue
        sses.append(sse)
        if best is None or sse < best["sse"]:
            best = {"theta": [float(x) for x in res.x], "sse": sse,
                    "status": int(res.status), "nfev": int(res.nfev)}
    if best is None:
        raise SystemExit(f"REFUSED: no converged start for {form}")
    n_at_best = int(sum(1 for s in sses
                        if abs(s - best["sse"]) <= OPT_SAME_SSE_TOL * max(1.0, best["sse"])))
    n = len(y)
    best.update({
        "form": form, "expr": spec["expr"], "param_names": list(spec["names"]),
        "n_starts": len(grid), "n_converged": n_conv,
        "n_starts_at_global_sse": n_at_best,
        "n_distinct_optima": int(len({round(s, 12) for s in sses})),
        "rmse": float(np.sqrt(best["sse"] / n)), "n_rows": int(n),
        "r2_vs_mean": float(1.0 - best["sse"] / float(np.sum((y - y.mean()) ** 2))),
    })
    return best


def loo_rmse(form: str, r: np.ndarray, v: np.ndarray, y: np.ndarray,
             full_theta: list[float]) -> dict[str, Any]:
    """Leave-one-CELL-out: refit on n-1 cells with the SAME multi-start grid plus
    the full-data optimum, predict the held-out cell."""
    n = len(y)
    preds, errs, failed = [], [], 0
    grid = starts_for(form) + [list(full_theta)]
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        try:
            f = fit_form(form, r[m], v[m], y[m], starts=grid)
        except SystemExit:
            failed += 1
            preds.append(float("nan"))
            errs.append(float("nan"))
            continue
        th = np.asarray(f["theta"], float)
        with np.errstate(over="ignore", invalid="ignore"):
            p = float(FORMS[form]["fn"](th, r[i:i + 1], v[i:i + 1])[0])
        preds.append(p)
        errs.append(p - float(y[i]))
    e = np.asarray(errs, float)
    return {"form": form, "loo_pred": preds, "loo_error": errs,
            "n_failed": int(failed),
            "loo_rmse": float(np.sqrt(np.nanmean(e ** 2))),
            "loo_mae": float(np.nanmean(np.abs(e))),
            "loo_max_abs": float(np.nanmax(np.abs(e)))}


def cell_block_bootstrap(per_world: np.ndarray, b_draws: int, seed: int) -> np.ndarray:
    """Registered CI machinery: each draw resamples the cell's own 32 world
    indices with replacement INDEPENDENTLY per cell, then recomputes the cell
    means.  Returns (B, n_cells)."""
    n_cells, n_w = per_world.shape
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n_w, size=(b_draws, n_cells, n_w))
    rows = np.arange(n_cells)[None, :, None]
    return per_world[rows, idx].mean(axis=2)


def bootstrap_form(form: str, r: np.ndarray, v: np.ndarray,
                   per_world: np.ndarray, theta0: list[float],
                   b_draws: int, seed: int) -> dict[str, Any]:
    means = cell_block_bootstrap(per_world, b_draws, seed)
    names = FORMS[form]["names"]
    draws: list[list[float]] = []
    nfail = 0
    for b in range(b_draws):
        try:
            f = fit_form(form, r, v, means[b], starts=[list(theta0)])
        except SystemExit:
            nfail += 1
            continue
        if all(abs(x) < 1e6 for x in f["theta"]):
            draws.append(f["theta"])
        else:
            nfail += 1
    arr = np.asarray(draws, float)
    return {
        "B": int(b_draws), "seed": int(seed), "n_used": int(len(arr)),
        "n_discarded": int(nfail),
        "discard_rule": "non-convergence, or |param| >= 1e6 (K2f's rules); cells are "
                        "NEVER dropped -- the design is fixed and the uncertainty is "
                        "world sampling within cells",
        "ci95": {nm: [float(np.quantile(arr[:, j], 0.025)),
                      float(np.quantile(arr[:, j], 0.975))]
                 for j, nm in enumerate(names)},
        "median": {nm: float(np.median(arr[:, j])) for j, nm in enumerate(names)},
        "width": {nm: float(np.quantile(arr[:, j], 0.975) - np.quantile(arr[:, j], 0.025))
                  for j, nm in enumerate(names)},
    }


# ---------------------------------------------------------------------------
# The rule-16 truth table, verbatim from the registration.

TRUTH_TABLE = [
    {"n": "1", "condition": "any Part-0/pilot gate fails after its declared ladder",
     "outcome": "STOP_DESIGN_INFEASIBLE",
     "text": "STOP_DESIGN_INFEASIBLE (planner defect; no fit is run)"},
    {"n": "2", "condition": "L-1 MISS AND winner lambda CI contains 0",
     "outcome": "R_TERM_ABSENT_AT_LEVEL",
     "text": "R_TERM_ABSENT_AT_LEVEL -- the tax-only level law is the COMPLETE level "
             "story on this family; level-response dissociation named; q-at-level "
             "closes as structurally unposed; M2 proceeds on the tax-only form"},
    {"n": "3", "condition": "L-1 MISS AND winner lambda CI excludes 0",
     "outcome": "NON_IDENTIFIED_UNDERPOWERED",
     "text": "NON_IDENTIFIED_UNDERPOWERED -- CI reported, no q claim; M2 blocked; "
             "leverage redesign named"},
    {"n": "4", "condition": "L-1 HOLD AND L-2 below",
     "outcome": "LEVEL_RESPONSE_DISSOCIATION",
     "text": "LEVEL_RESPONSE_DISSOCIATION -- q measured at level, below the response "
             "band; new named phenomenon; M2 seals the measured law"},
    {"n": "5", "condition": "L-1 HOLD AND L-2 overlap",
     "outcome": "SINGLE_EXPONENT_RESTORED",
     "text": "SINGLE_EXPONENT_RESTORED -- T4's level form completed with the response "
             "exponent; M2 seals"},
    {"n": "6", "condition": "L-1 HOLD AND L-2 above",
     "outcome": "ABOVE_BAND_ANOMALY",
     "text": "ABOVE_BAND_ANOMALY -- named; M2 seals the measured law; theory note "
             "required"},
    {"n": "--", "condition": "L-3 disjoint (either side), any cell 2-6",
     "outcome": "TAX_SHIFT_AT_LEVEL",
     "text": "modifier TAX_SHIFT_AT_LEVEL -- pre-registered anomaly fed into M3's charter"},
    {"n": "--", "condition": "L-3 overlap, any cell 2-6",
     "outcome": "KAPPA_FOURTH_APPEARANCE",
     "text": "modifier: kappa's fourth independent appearance is counted"},
]

SIDES = {
    "L-1": {"clause": f"winner's q 95% bootstrap CI width <= {L1_Q_WIDTH_MAX}",
            "sided": "one-sided", "improvement_side": "DOWN (smaller width is better)",
            "prior": 0.55},
    "L-2": {"clause": f"winner's q CI against the response band {list(L2_RESPONSE_BAND)}: "
                      "entirely below / overlap / entirely above",
            "sided": "two-sided", "improvement_side":
                "neither -- all three outcomes are informative and named",
            "prior": {"below": 0.55, "overlap": 0.35, "above": 0.10},
            "registered_lean": "BELOW",
            "conditional_on": "L-1 HOLD"},
    "L-3": {"clause": f"winner's kappa CI overlaps K2f F2's kappa' ci95 "
                      f"{list(L3_KAPPA_CI)}",
            "sided": "two-sided overlap; disjoint-low and disjoint-high both named",
            "improvement_side": "neither -- containment/overlap",
            "prior": 0.70},
    "L-4": {"clause": "within each share level, Spearman(residual, phi) across the 5 phi "
                      "cells; monotone same-sign in >=3/4 share levels is the named "
                      "finding 'phi leaks past (r, V)'",
            "sided": "reading only, NO gate", "improvement_side": "n/a",
            "prior": None},
    "G1m(a)": {"clause": f"all shares inside {list(SHARE_ENVELOPE)}",
               "sided": "two-sided containment", "improvement_side": "neither"},
    "G1m(b)": {"clause": f"V max/min >= {G1M_V_RATIO_MIN}", "sided": "one-sided",
               "improvement_side": "UP"},
    "G1m(c)": {"clause": f"within-share r max/min >= {G1M_R_RATIO_MIN} in at least "
                         f"{G1M_R_RATIO_MIN_LEVELS} share levels",
               "sided": "one-sided", "improvement_side": "UP"},
    "G1m(d)": {"clause": f"cross-cell |corr(r, V)| <= {G1M_CORR_MAX}",
               "sided": "one-sided on the absolute value", "improvement_side": "DOWN"},
    "G1m(e)": {"clause": "no duplicate (r, V) design points", "sided": "exact",
               "improvement_side": "n/a"},
    "G2m(i)": {"clause": "all per-world fields finite and strictly inside (0, 1)",
               "sided": "two-sided containment", "improvement_side": "neither"},
    "G2m(ii)": {"clause": f"at share 0.60, |realized card-attenuation contrast between "
                          f"the corner phis| > {G2M_LIVENESS_SE_MULT}x its pooled SE",
                "sided": "one-sided", "improvement_side": "UP"},
    "G3m(b)": {"clause": f"projected q width proxy <= {G3M_PROJ_WIDTH_MAX} under BOTH "
                         "q truths (stricter than L-1's 0.60 to absorb proxy slack)",
               "sided": "one-sided", "improvement_side": "DOWN"},
}

STAGE_ESTIMATES_REGISTRATION = {"part0": 60, "pilot": 30, "worlds_each": 120,
                                "worlds_n_chunks": 4, "fit": 300, "finalize": 60}
STAGE_ESTIMATES_EXECUTOR = {"part0": 60, "pilot": 30, "power": 120,
                            "worlds_a": 120, "worlds_b": 120, "worlds_c": 120,
                            "worlds_d": 120, "fit": 300, "rule13": 180, "finalize": 60,
                            "report": 30, "diagnose": 120}


# ---------------------------------------------------------------------------
# PART 0.

def design_table(phis: tuple[float, ...]) -> pd.DataFrame:
    rows = []
    for share in SHARES:
        for phi in phis:
            rows.append({"cell_tag": cell_tag(share, phi), "cell_id": cell_id(share, phi),
                         "share": share, "phi": phi, "int_share": INT_SHARE,
                         "r_pred": r_of(share, phi), "V_person": v_of(share)})
    return pd.DataFrame(rows)


def g1m_check(phis: tuple[float, ...]) -> dict[str, Any]:
    df = design_table(phis)
    r = df["r_pred"].to_numpy(float)
    v = df["V_person"].to_numpy(float)
    within = []
    for share in SHARES:
        sub = df[df["share"] == share]
        rr = sub["r_pred"].to_numpy(float)
        within.append({"share": share, "r_min": float(rr.min()), "r_max": float(rr.max()),
                       "ratio": float(rr.max() / rr.min()),
                       "meets_bar": bool(rr.max() / rr.min() >= G1M_R_RATIO_MIN)})
    dup: list[dict[str, Any]] = []
    key = [(round(a, 12), round(b, 12)) for a, b in zip(r, v)]
    for k in sorted(set(key)):
        j = [i for i, kk in enumerate(key) if kk == k]
        if len(j) > 1:
            dup.append({"r": k[0], "V": k[1], "cells": [df["cell_tag"].iloc[i] for i in j]})
    corr_rv = pearson(r, v)
    corr_rq_v = pearson(r ** SEALED_Q, v)
    a = bool(all(SHARE_ENVELOPE[0] <= s <= SHARE_ENVELOPE[1] for s in SHARES))
    b = bool(v.max() / v.min() >= G1M_V_RATIO_MIN)
    n_levels = int(sum(1 for w in within if w["meets_bar"]))
    c = bool(n_levels >= G1M_R_RATIO_MIN_LEVELS)
    d = bool(abs(corr_rv) <= G1M_CORR_MAX)
    e = bool(len(dup) == 0)
    return {
        "phi_ladder": list(phis), "n_cells": int(len(df)),
        "design_points": df.to_dict("records"),
        "(a) shares inside envelope": {"PASS": a, "envelope": list(SHARE_ENVELOPE),
                                       "shares": list(SHARES)},
        "(b) V ratio": {"PASS": b, "V_min": float(v.min()), "V_max": float(v.max()),
                        "ratio": float(v.max() / v.min()), "bar": G1M_V_RATIO_MIN,
                        "V_source": "scripts/run_suica_m4_k2e_double_matching.py:234-241 "
                                    "(person_share_design -> k2b.arm_shares); never "
                                    "assumed linear"},
        "(c) within-share r ratio": {"PASS": c, "bar": G1M_R_RATIO_MIN,
                                     "levels_meeting_bar": n_levels,
                                     "levels_required": G1M_R_RATIO_MIN_LEVELS,
                                     "per_share": within},
        "(d) decollinearization": {"PASS": d, "corr_r_V": corr_rv,
                                   "abs_corr_r_V": float(abs(corr_rv)),
                                   "bar": G1M_CORR_MAX,
                                   "corr_r_pow_q_V": corr_rq_v,
                                   "q_used_for_power": SEALED_Q,
                                   "k2f_corr_r_V_26_rows": K2F_CORR_RV},
        "(e) no duplicate design points": {"PASS": e, "duplicates": dup},
        "PASS": bool(a and b and c and d and e),
        "gates_c_or_d_failed": bool(not (c and d)),
    }


def g0m_check() -> dict[str, Any]:
    out: dict[str, Any] = {}
    # (i)-(iii): the deterministic design maps.
    checks = [
        ("(i) predicted_attenuation(0.40, 0.90)", r_of(0.40, 0.90), ANCHORS["r_040_090"]),
        ("(ii-a) predicted_attenuation(0.45, 0.90)", r_of(0.45, 0.90),
         ANCHORS["r_045_090"]),
        ("(ii-b) person_share_design(0.45, 0.0)", v_of(0.45), ANCHORS["V_045"]),
        ("(iii) person_share_design(0.40, 0.0)", v_of(0.40), ANCHORS["V_040"]),
    ]
    out["maps"] = {name: {"rederived": got, "expected": exp, "bit_exact": bool(got == exp)}
                   for name, got, exp in checks}
    out["maps_source"] = {
        "r": "scripts/run_suica_m4_k2c_matched_pairs.py:186-191 "
             "(predicted_attenuation -> k2b:533-583)",
        "V": "scripts/run_suica_m4_k2e_double_matching.py:234-241 "
             "(person_share_design -> k2b.arm_shares)",
    }

    # (iv): every K2f number quoted in the registration, bit-exact.
    fits = read_json(K2F / "fits.json")
    loos = read_json(K2F / "loo.json")
    f2 = fits["fits"]["F2"]
    th = dict(zip(f2["param_names"], f2["theta"]))
    quoted = [
        ("F2 lambda'", th["lambda"], K2F_F2_LAMBDA),
        ("F2 q'", th["q"], K2F_F2_Q),
        ("F2 kappa'", th["kappa"], K2F_F2_KAPPA),
        ("F2 p", th["p"], K2F_F2_P),
        ("F2 LOO-RMSE (fits.json:L-1.best_loo_rmse)", fits["L-1"]["best_loo_rmse"],
         K2F_F2_LOO),
        ("F2 LOO-RMSE (loo.json:loo.F2.loo_rmse)", loos["loo"]["F2"]["loo_rmse"],
         K2F_F2_LOO),
        ("F2 q' ci95 lo", f2["bootstrap"]["ci95"]["q"][0], K2F_F2_Q_CI[0]),
        ("F2 q' ci95 hi", f2["bootstrap"]["ci95"]["q"][1], K2F_F2_Q_CI[1]),
        ("F2 kappa' ci95 lo", f2["bootstrap"]["ci95"]["kappa"][0], K2F_F2_KAPPA_CI[0]),
        ("F2 kappa' ci95 hi", f2["bootstrap"]["ci95"]["kappa"][1], K2F_F2_KAPPA_CI[1]),
    ]
    out["k2f_quoted"] = {n: {"persisted": g, "registration": e, "bit_exact": bool(g == e)}
                         for n, g, e in quoted}
    out["k2f_winner_is_F2"] = bool(fits["winner"] == "F2")

    # (iv-ext): the other artifact numbers this registration cites (rule 8).
    rows = read_csv_rt(K2F / "compiled_rows.csv")
    rr = rows["r_pred"].to_numpy(float)
    vv = rows["V_person"].to_numpy(float)
    ext = [
        ("corr(r, V) over the 26 K2f rows (Pearson, RN-M1-4)", pearson(rr, vv),
         K2F_CORR_RV),
        ("share envelope lo", float(rows["share"].min()), SHARE_ENVELOPE[0]),
        ("share envelope hi", float(rows["share"].max()), SHARE_ENVELOPE[1]),
        ("r(0.30, 0.90)", r_of(0.30, 0.90), ANCHORS["r_030_090"]),
        ("r(0.30, 0.98)", r_of(0.30, 0.98), ANCHORS["r_030_098"]),
        ("r(0.50, 0.90)", r_of(0.50, 0.90), ANCHORS["r_050_090"]),
        ("r(0.50, 0.98)", r_of(0.50, 0.98), ANCHORS["r_050_098"]),
        ("K2f n_rows", float(len(rows)), 26.0),
    ]
    out["registration_citations"] = {
        n: {"rederived": g, "registration": e, "bit_exact": bool(g == e)}
        for n, g, e in ext}

    # (v): D-open's M-4 level, re-derived from its raw CSV round-trip.
    do = read_csv_rt(RES / "dopen_seal_opening" / "m4_field_rows.csv")
    lvl = float(do["recovery_b_only"].to_numpy(float).mean())
    out["dopen_m4_level"] = {
        "rederived": lvl, "expected": ANCHORS["dopen_m4_level"],
        "bit_exact": bool(lvl == ANCHORS["dopen_m4_level"]),
        "n_worlds": int(len(do)),
        "source": "results/dopen_seal_opening/m4_field_rows.csv:recovery_b_only "
                  "(round-trip parsed, mean over worlds -- K2f's _level_from_raw)"}

    # (vi): the response band, verbatim in the theory doc.
    txt = THEORY_DOC.read_text(encoding="utf-8")
    hits = [i + 1 for i, ln in enumerate(txt.split("\n")) if THEORY_BAND_STRING in ln]
    out["theory_band"] = {"string": THEORY_BAND_STRING, "found": bool(hits),
                          "lines": hits[:20], "n_lines": len(hits),
                          "doc": rel(THEORY_DOC),
                          "registration_cites": "docs/SUICA_IDENTITY_THEORY_V1.md:805,841"}

    ok = (all(d["bit_exact"] for d in out["maps"].values())
          and all(d["bit_exact"] for d in out["k2f_quoted"].values())
          and all(d["bit_exact"] for d in out["registration_citations"].values())
          and out["k2f_winner_is_F2"]
          and out["dopen_m4_level"]["bit_exact"]
          and out["theory_band"]["found"])
    out["PASS"] = bool(ok)
    out["failure_meaning"] = ("a mismatch on any clause is a PLANNER CITATION DEFECT: "
                              "STOP, report, do not repair silently")
    return out


def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    for nm in ("g2m_pilot.json", "g3mb_power.json", "cell_means.csv", "fits.json"):
        if (OUT / nm).exists():
            raise SystemExit(f"STOP (ordering): {nm} exists before Part 0.")
    _ordering_log("part0_start")

    g0 = g0m_check()
    g1 = g1m_check(PHIS)
    ladder_note = "base ladder; no fallback needed"
    if g1["gates_c_or_d_failed"]:
        g1_base = g1
        g1 = g1m_check(PHIS_LADDER_G1M)
        g1["fallback_applied"] = True
        g1["base_ladder_result"] = {k: g1_base[k] for k in
                                    ("phi_ladder", "(c) within-share r ratio",
                                     "(d) decollinearization", "PASS")}
        ladder_note = ("rule-17 fallback FIRED: base phi ladder failed (c) or (d); "
                       "extended once to {0.45, 0.60, 0.75, 0.90, 0.98} as pre-declared")
    adopted_phis = tuple(g1["phi_ladder"])

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md (M4-M1, BEFORE run, "
                        "commit 140e927)",
        "master_seed": MASTER_SEED,
        "salts": {"main": SALT_WORLD, "pilot": SALT_PILOT},
        "rn_notes": RN_NOTES,
        "carrier": {
            "inherits": "K2F-FRESH (results/m4_k2f_level_law/part0.json:fresh_arm) "
                        "verbatim except (share, phi)",
            "int_share": INT_SHARE, "w_int_arm": W_INT_ARM,
            "instrument": "k2b.run_field_world (985-author K1-pinned panel, F2 "
                          "m-multiset, 4 contexts)",
            "field_statistic": "recovery_b_only, per world",
            "cell_level": "mean over the cell's worlds (K2f's _level_from_raw)",
            "k2f_fresh_arm_block": read_json(K2F / "part0.json")["fresh_arm"],
        },
        "design": {"shares": list(SHARES), "phi_ladder_registered": list(PHIS),
                   "phi_ladder_adopted": list(adopted_phis),
                   "phi_ladder_note": ladder_note,
                   "n_cells": len(SHARES) * len(adopted_phis),
                   "worlds_per_cell": N_WORLDS,
                   "n_worlds_total": len(SHARES) * len(adopted_phis) * N_WORLDS,
                   "phi_extension_disclosure":
                       "phi at 0.60-0.80 is an EXTENSION beyond the exercised "
                       "{0.90, 0.98}; guarded by the G2m pilot (finiteness, "
                       "non-degeneracy, liveness); the law claim stays scoped to the "
                       "tested grid"},
        "forms": {k: FORMS[k]["expr"] for k in FORM_ORDER},
        "form_notes": {
            "F1e": "the ONLY bounded form (epsilon in [0, 0.05]; 0.05 = 3.3x the fragile "
                   "<=0.015 band ceiling). Near q ~ 0 its (lambda, epsilon) ridge is "
                   "SINGULAR -- disclosed; LOO pays for it.",
            "nesting": "F2 nests F1 at p=0 and F3 at p=q; F1e nests F1 at epsilon=0",
            "grain": "fit on the 20 CELL MEANS; world-level fitting is "
                     "minimizer-identical at equal cell n (noted, not run)",
        },
        "optimizer": {**OPT, "scipy_version": __import__("scipy").__version__,
                      "n_starts": {f: len(starts_for(f)) for f in FORM_ORDER},
                      "start_grid": {"lambda": list(START_LAMBDA), "q": list(START_Q),
                                     "kappa": list(START_KAPPA), "p": list(START_P),
                                     "epsilon": list(START_EPS)},
                      "epsilon_bounds": list(EPS_BOUNDS),
                      "same_optimum_sse_tol": OPT_SAME_SSE_TOL,
                      "selection": "leave-one-CELL-out RMSE (20 refits per form, full "
                                   "grid + full-data optimum)",
                      "loo_starts": "the same grid PLUS the full-data optimum"},
        "bootstrap": {"kind": "within-cell world-block", "B": B_BOOT,
                      "B_high": B_BOOT_HIGH, "seed": MASTER_SEED,
                      "spec": "each draw resamples 32 world indices with replacement "
                              "INDEPENDENTLY per cell, recomputes the 20 cell means, "
                              "refits from the full-data optimum start",
                      "cells_never_dropped": True,
                      "rationale": "the design is fixed; the uncertainty is world "
                                   "sampling within cells (stated against K2f's "
                                   "row-resample, which faced a different object)",
                      "discard_rules": "non-convergence, |param| >= 1e6 (K2f)",
                      "rule13": f"any verdict within {BOUNDARY_REL:.0%} of its boundary "
                                f"re-runs at B={B_BOOT_HIGH} and scores BOUNDARY if "
                                f"unstable",
                      "tie_rule": f"if the top two forms' LOO-RMSE differ by < "
                                  f"{TIE_REL:.0%} of the winner's, every verdict must "
                                  f"agree across both, else that verdict reports SPLIT "
                                  f"with both values"},
        "sides_rule22": SIDES,
        "gate_stages_rule23": {
            "G0m": "inputs exist at Part 0 (persisted K2f/D-open artifacts + the "
                   "deterministic design maps + the theory doc)",
            "G1m": "inputs exist at Part 0 (pure design arithmetic; no worlds needed)",
            "G2m": "inputs exist at the pilot stage (16 pilot worlds), BEFORE any main "
                   "world",
            "G3m(a,c)": "inputs exist at Part 0 (clause sides; stage estimates)",
            "G3m(b)": "inputs exist AFTER the pilot (needs sigma_w) and BEFORE the "
                      "first main world -- its own permit-gated stage (RN-M1-5)",
            "G4m": "inputs exist at Part 0 (the truth table) and at finalize (rule 24)",
        },
        "stage_estimates_seconds_registration": STAGE_ESTIMATES_REGISTRATION,
        "stage_estimates_seconds_executor": STAGE_ESTIMATES_EXECUTOR,
        "stage_overrun_convention": "a stage exceeding 2x its estimate stops and is "
                                    "reported",
        "rule16_truth_table": TRUTH_TABLE,
        "rule16_note": "L-2 is recorded N/A in cell 2 (the q question is unposed); L-3 "
                       "is evaluated in every cell 2-6 since kappa is identified even "
                       "where q is not, and in cell 3 it is reported descriptively, "
                       "adjudicating nothing",
        "environment": {
            "python": sys.version.split()[0],
            "python_executable": sys.executable,
            "platform": platform.platform(),
            "numpy": np.__version__, "pandas": pd.__version__,
            "scipy": __import__("scipy").__version__,
        },
        "G0m": g0, "G1m": g1,
        "seconds": None,
    }
    part0["seconds"] = time.time() - t0
    write_json(OUT / "part0.json", part0)
    _write_part0_tables(part0)
    _ordering_log("part0_done", seconds=part0["seconds"],
                  G0m_PASS=g0["PASS"], G1m_PASS=g1["PASS"],
                  corr_r_V=g1["(d) decollinearization"]["corr_r_V"])
    if not g0["PASS"]:
        _ordering_log("part0_G0m_FAILED")
        raise SystemExit("STOP: G0m FAILED (planner citation defect) -- see part0.json")
    if not g1["PASS"]:
        _ordering_log("part0_G1m_FAILED")
        raise SystemExit("STOP_DESIGN_INFEASIBLE: G1m FAILED after its declared ladder "
                         "-- see part0.json")
    print(f"part0 OK  G0m PASS  G1m PASS  ladder={list(adopted_phis)}  "
          f"corr(r,V)={g1['(d) decollinearization']['corr_r_V']!r}  "
          f"{time.time() - t0:.1f}s")
    _ = args


def _cell(s: str) -> str:
    """A markdown table cell: pipes and newlines would break the row."""
    return str(s).replace("|", "\\|").replace("\n", " ")


def _md_table(header: list[str], rows: list[list[str]]) -> list[str]:
    return (["| " + " | ".join(_cell(h) for h in header) + " |",
             "|" + "|".join(["---"] * len(header)) + "|"]
            + ["| " + " | ".join(_cell(c) for c in r) + " |" for r in rows])


def _write_part0_tables(part0: dict[str, Any]) -> None:
    g1 = part0["G1m"]
    lines = ["# M4-M1 Part 0 tables (generated from artifacts -- rule 24)", "",
             "## The realized design: 20 (r, V) points", ""]
    lines += _md_table(
        ["cell", "share", "phi", "int_share", "r_pred", "V_person"],
        [[d["cell_tag"], repr(d["share"]), repr(d["phi"]), repr(d["int_share"]),
          repr(d["r_pred"]), repr(d["V_person"])] for d in g1["design_points"]])
    lines += ["", "## G0m -- anchors, bit-exact", ""]
    rows = []
    for name, d in part0["G0m"]["maps"].items():
        rows.append([name, repr(d["expected"]), repr(d["rederived"]), str(d["bit_exact"])])
    for name, d in part0["G0m"]["k2f_quoted"].items():
        rows.append([name, repr(d["registration"]), repr(d["persisted"]),
                     str(d["bit_exact"])])
    for name, d in part0["G0m"]["registration_citations"].items():
        rows.append([name, repr(d["registration"]), repr(d["rederived"]),
                     str(d["bit_exact"])])
    d = part0["G0m"]["dopen_m4_level"]
    rows.append(["(v) Dopen:M-4 level from raw CSV", repr(d["expected"]),
                 repr(d["rederived"]), str(d["bit_exact"])])
    d = part0["G0m"]["theory_band"]
    rows.append([f"(vi) response band {d['string']} verbatim in {d['doc']}",
                 d["string"], f"lines {d['lines']}", str(d["found"])])
    lines += _md_table(["clause", "registration / expected", "re-derived / persisted",
                        "bit-exact"], rows)
    lines += ["", "## G1m -- design gates", ""]
    c = g1["(c) within-share r ratio"]
    d_ = g1["(d) decollinearization"]
    lines += _md_table(
        ["gate", "bar", "realized", "PASS"],
        [["(a) shares inside envelope", repr(list(SHARE_ENVELOPE)), repr(list(SHARES)),
          str(g1["(a) shares inside envelope"]["PASS"])],
         ["(b) V max/min", f">= {G1M_V_RATIO_MIN}", repr(g1["(b) V ratio"]["ratio"]),
          str(g1["(b) V ratio"]["PASS"])],
         ["(c) within-share r max/min",
          f">= {G1M_R_RATIO_MIN} in >= {G1M_R_RATIO_MIN_LEVELS} share levels",
          f"{c['levels_meeting_bar']}/{len(SHARES)} levels",
          str(c["PASS"])],
         ["(d) |corr(r, V)|", f"<= {G1M_CORR_MAX}", repr(d_["abs_corr_r_V"]),
          str(d_["PASS"])],
         ["(e) duplicate (r, V) points", "0",
          str(len(g1["(e) no duplicate design points"]["duplicates"])),
          str(g1["(e) no duplicate design points"]["PASS"])]])
    lines += ["", "### within-share r leverage", ""]
    lines += _md_table(["share", "r min", "r max", "max/min", "meets 1.20"],
                       [[repr(w["share"]), repr(w["r_min"]), repr(w["r_max"]),
                         repr(w["ratio"]), str(w["meets_bar"])] for w in c["per_share"]])
    lines += ["", "### decollinearization headline", ""]
    lines += _md_table(
        ["quantity", "value"],
        [["corr(r, V) on M1's design", repr(d_["corr_r_V"])],
         [f"corr(r^{SEALED_Q!r}, V) on M1's design", repr(d_["corr_r_pow_q_V"])],
         ["corr(r, V) on K2f's 26 rows (the object being broken)",
          repr(d_["k2f_corr_r_V_26_rows"])]])
    (OUT / "part0_tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# World running.

def _run_cell(share: float, phi: float, salt: str, indices: list[int],
              tag: str, verify_first: bool, with_card: bool) -> pd.DataFrame:
    kb = k2b()
    w = kb.arm_weights(share, W_INT_ARM)
    rows = []
    for j, wi in enumerate(indices):
        seed = world_seed_for(share, phi, wi, salt)
        world = kb.build_k2b_world(seed, phi)
        row = kb.run_field_world(tag, wi, world, w, verify=(verify_first and j == 0))
        row["world"] = wi
        row["world_seed"] = seed
        row["share"] = share
        row["phi"] = phi
        row["salt"] = salt
        if with_card:
            frame, common_resid = kb.card_channel_frame(world, w, seed)
            point, _ = kb.bootstrap_card(frame, 1, seed)
            row["r_card_b_raw"] = float(point["r_card_b_raw"])
            row["card_frame_centred_residual_max"] = float(common_resid)
        rows.append(row)
    return pd.DataFrame(rows)


def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    n_guarded = _arm_guard()
    permit = _issue_permit("pilot")
    p0 = read_json(OUT / "part0.json")
    phis = tuple(p0["design"]["phi_ladder_adopted"])
    corner_phis = (phis[PILOT_PHIS_INDEX[0]], phis[PILOT_PHIS_INDEX[1]])
    corners = [(s, p) for s in PILOT_SHARES for p in corner_phis]

    frames = []
    for share, phi in corners:
        df = _run_cell(share, phi, SALT_PILOT, list(range(PILOT_WORLDS)),
                       f"M1-PILOT-{cell_tag(share, phi)}",
                       verify_first=(share == corners[0][0] and phi == corners[0][1]),
                       with_card=True)
        frames.append(df)
        print(f"  pilot {cell_tag(share, phi)}: {len(df)} worlds "
              f"({time.time() - t0:.1f}s)", flush=True)
    pilot = pd.concat(frames, ignore_index=True)
    pilot.to_csv(OUT / "pilot_field.csv", index=False)

    pv = pilot["recovery_b_only"].to_numpy(float)
    resid_cols = [c for c in pilot.columns if c.startswith("g4b_")]
    resid_max = (float(np.nanmax(np.abs(pilot[resid_cols].to_numpy(float))))
                 if resid_cols else float("nan"))

    # (ii) LIVENESS at share 0.60 -- RN-M1-3.
    def contrast(col: str) -> dict[str, Any]:
        hi_share = max(PILOT_SHARES)
        a = pilot[(pilot["share"] == hi_share) & (pilot["phi"] == corner_phis[0])][col]
        b = pilot[(pilot["share"] == hi_share) & (pilot["phi"] == corner_phis[1])][col]
        av, bv = a.to_numpy(float), b.to_numpy(float)
        d = float(av.mean() - bv.mean())
        se = float(np.sqrt(np.var(av, ddof=1) / len(av) + np.var(bv, ddof=1) / len(bv)))
        return {"share": hi_share, "phi_lo": corner_phis[0], "phi_hi": corner_phis[1],
                "mean_at_phi_lo": float(av.mean()), "mean_at_phi_hi": float(bv.mean()),
                "contrast": d, "pooled_SE": se,
                "abs_contrast_over_SE": float(abs(d) / se) if se > 0 else float("inf"),
                "bar": G2M_LIVENESS_SE_MULT,
                "PASS": bool(abs(d) > G2M_LIVENESS_SE_MULT * se)}

    card = contrast("r_card_b_raw")
    field = contrast("recovery_b_only")

    g2 = {
        "utc": datetime.now(UTC).isoformat(), "permit": permit,
        "n_k2b_instances_guarded": n_guarded,
        "corner_cells": [cell_tag(s, p) for s, p in corners],
        "worlds_per_corner": PILOT_WORLDS, "salt": SALT_PILOT,
        "per_world": pilot[["share", "phi", "world", "world_seed", "recovery_b_only",
                            "r_card_b_raw"]].to_dict("records"),
        "(i) finiteness / non-saturation": {
            "all_finite": bool(np.all(np.isfinite(pv))),
            "strictly_inside_unit": bool(np.all((pv > 0.0) & (pv < 1.0))),
            "min": float(pv.min()), "max": float(pv.max()),
            "g4b_route_residual_maxabs": resid_max,
            "g4b_residuals_ok": bool(np.isnan(resid_max) or resid_max <= 1e-9),
            "PASS": bool(np.all(np.isfinite(pv)) and np.all((pv > 0.0) & (pv < 1.0))
                         and (np.isnan(resid_max) or resid_max <= 1e-9))},
        "(ii) liveness (rule 3)": {
            "GATE_reading_card_attenuation": card,
            "declared_fallback_reading_field_contrast": field,
            "gate_object": "r_card_b_raw (RN-M1-3)",
            "gate_object_source":
                "scripts/run_suica_m4_k2b_t4_branch.py:392-503 card_channel_frame -> "
                ":505-509 bootstrap_card -> :486 r_card_b_raw; the object k2b's own G2 "
                "lever-liveness check uses at :944-963",
            "readings_agree": bool(card["PASS"] == field["PASS"]),
            "PASS": card["PASS"]},
        "fallback_ladder": "liveness failure -> drop the phi extension, fall back to "
                           f"{list(PHIS_LADDER_LIVENESS)}, re-run G1m + G3m-b; failure "
                           "there -> STOP_DESIGN_INFEASIBLE",
        "seconds": time.time() - t0,
    }
    g2["PASS"] = bool(g2["(i) finiteness / non-saturation"]["PASS"]
                      and g2["(ii) liveness (rule 3)"]["PASS"])
    write_json(OUT / "g2m_pilot.json", g2)
    if not g2["PASS"]:
        _ordering_log("g2m_FAILED", **{k: g2[k] for k in ("PASS",)})
        raise SystemExit("STOP: G2m FAILED -- see results/m4_m1_r_at_level/g2m_pilot.json")
    print(f"pilot OK  liveness card={card['abs_contrast_over_SE']:.3f} SE  "
          f"field={field['abs_contrast_over_SE']:.3f} SE  {time.time() - t0:.1f}s")
    _ordering_log("pilot_done", seconds=time.time() - t0,
                  card_se=card["abs_contrast_over_SE"],
                  field_se=field["abs_contrast_over_SE"])
    _ = args


def stage_power(args: argparse.Namespace) -> None:
    """G3m(b): the rule-11 projected identification power, made real."""
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    g2 = read_json(OUT / "g2m_pilot.json")
    if not g2["PASS"]:
        raise SystemExit("STOP: G3m-b requires a passing G2m.")
    pilot = read_csv_rt(OUT / "pilot_field.csv")

    # pooled per-world sd across the 16 pilot worlds (within-cell, df = 16 - 4)
    ss, df_tot = 0.0, 0
    per_cell = []
    for (share, phi), grp in pilot.groupby(["share", "phi"]):
        vals = grp["recovery_b_only"].to_numpy(float)
        ss += float(np.sum((vals - vals.mean()) ** 2))
        df_tot += len(vals) - 1
        per_cell.append({"cell": cell_tag(float(share), float(phi)), "n": int(len(vals)),
                         "mean": float(vals.mean()), "sd": float(np.std(vals, ddof=1))})
    sigma_raw = float(np.sqrt(ss / df_tot))
    chi2_q = float(chi2.ppf(G3M_CHI2_Q, G3M_DF))
    inflation = float(np.sqrt(G3M_DF / chi2_q))
    sigma_w = sigma_raw * inflation

    dsg = pd.DataFrame(p0["G1m"]["design_points"])
    r = dsg["r_pred"].to_numpy(float)
    v = dsg["V_person"].to_numpy(float)
    n_cells = len(r)
    cell_sd = sigma_w / np.sqrt(N_WORLDS)

    truths = {}
    rng = np.random.default_rng(MASTER_SEED)
    for q_truth in (1.0, SEALED_Q):
        mu = K2F_F2_LAMBDA * r ** q_truth - K2F_F2_KAPPA * v
        qs = []
        nfail = 0
        for _ in range(B_PROJ):
            y = mu + rng.normal(0.0, cell_sd, size=n_cells)
            try:
                f = fit_form("F1", r, v, y)
            except SystemExit:
                nfail += 1
                continue
            qs.append(f["theta"][1])
        arr = np.asarray(qs, float)
        lo, hi = float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975))
        truths[repr(q_truth)] = {
            "q_truth": q_truth, "B_proj": B_PROJ, "n_used": int(len(arr)),
            "n_failed": int(nfail),
            "q_hat_median": float(np.median(arr)), "q_hat_mean": float(arr.mean()),
            "q_hat_q025": lo, "q_hat_q975": hi,
            "width_proxy": float(hi - lo),
            "PASS": bool(hi - lo <= G3M_PROJ_WIDTH_MAX)}
        print(f"  projection q_truth={q_truth!r}: width={hi - lo!r} "
              f"({time.time() - t0:.1f}s)", flush=True)

    out = {
        "utc": datetime.now(UTC).isoformat(),
        "sigma_w_raw_pooled": sigma_raw, "pooled_df": int(df_tot),
        "df_declared": G3M_DF,
        "chi2_quantile": {"q": G3M_CHI2_Q, "df": G3M_DF, "value": chi2_q},
        "df_inflation_factor": inflation,
        "sigma_w": sigma_w, "cell_mean_sd_used": float(cell_sd),
        "per_pilot_cell": per_cell,
        "truths": {"lambda": K2F_F2_LAMBDA, "kappa": K2F_F2_KAPPA, "epsilon": 0.0,
                   "q_grid": [1.0, SEALED_Q],
                   "note": "no projection at q_truth = 0 -- structural non-identification "
                           "there is cell R_TERM_ABSENT's subject, not a power failure"},
        "fit_form": "F1 with the full start grid",
        "bar": G3M_PROJ_WIDTH_MAX,
        "bar_note": "stricter than L-1's 0.60 to absorb proxy slack (disclosed)",
        "projections": truths,
        "seconds": time.time() - t0,
    }
    out["PASS"] = bool(all(t["PASS"] for t in truths.values()))
    write_json(OUT / "g3mb_power.json", out)
    if not out["PASS"]:
        _ordering_log("g3mb_FAILED")
        raise SystemExit("STOP_DESIGN_INFEASIBLE: G3m-b projected power FAILED -- see "
                         "results/m4_m1_r_at_level/g3mb_power.json")
    print(f"power OK  sigma_w={sigma_w!r}  widths="
          f"{[t['width_proxy'] for t in truths.values()]}  {time.time() - t0:.1f}s")
    _ordering_log("power_done", sigma_w=sigma_w, seconds=time.time() - t0)
    _ = args


def _worlds_chunk(chunk: str) -> None:
    t0 = time.time()
    _arm_guard()
    permit = _issue_permit("main")
    p0 = read_json(OUT / "part0.json")
    phis = tuple(p0["design"]["phi_ladder_adopted"])
    share = SHARES["abcd".index(chunk)]
    (OUT / "cells").mkdir(parents=True, exist_ok=True)
    written = []
    for phi in phis:
        path = OUT / "cells" / f"cell_{cell_tag(share, phi)}_field.csv"
        df = _run_cell(share, phi, SALT_WORLD, list(range(N_WORLDS)),
                       f"M1-{cell_tag(share, phi)}", verify_first=False, with_card=False)
        df.to_csv(path, index=False)
        vals = df["recovery_b_only"].to_numpy(float)
        written.append({"cell": cell_tag(share, phi), "share": share, "phi": phi,
                        "n": int(len(vals)), "mean": float(vals.mean()),
                        "file": rel(path)})
        print(f"  {cell_tag(share, phi)}: n={len(vals)} mean={vals.mean()!r} "
              f"({time.time() - t0:.1f}s)", flush=True)
    out = {"utc": datetime.now(UTC).isoformat(), "chunk": chunk, "share": share,
           "permit": permit, "cells": written, "salt": SALT_WORLD,
           "generations": _GEN_COUNT, "seconds": time.time() - t0}
    write_json(OUT / f"worlds_{chunk}.json", out)
    _ordering_log(f"worlds_{chunk}_done", share=share, seconds=time.time() - t0)
    print(f"worlds_{chunk} OK  share={share!r}  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# FIT.

def _load_cells() -> tuple[pd.DataFrame, np.ndarray]:
    p0 = read_json(OUT / "part0.json")
    dsg = pd.DataFrame(p0["G1m"]["design_points"])
    rows, per_world = [], []
    for _, d in dsg.iterrows():
        path = OUT / "cells" / f"cell_{d['cell_tag']}_field.csv"
        if not path.exists():
            raise SystemExit(f"REFUSED: missing cell artifact {path}")
        df = read_csv_rt(path)
        vals = df["recovery_b_only"].to_numpy(float)
        if len(vals) != N_WORLDS:
            raise SystemExit(f"REFUSED: {path} has {len(vals)} worlds, expected {N_WORLDS}")
        if not np.all(np.isfinite(vals)):
            raise SystemExit(f"REFUSED: non-finite recovery_b_only in {path}")
        rows.append({"cell_tag": d["cell_tag"], "share": float(d["share"]),
                     "phi": float(d["phi"]), "r_pred": float(d["r_pred"]),
                     "V_person": float(d["V_person"]),
                     "field_mean": float(vals.mean()),
                     "field_sd": float(np.std(vals, ddof=1)),
                     "field_sem": float(np.std(vals, ddof=1) / np.sqrt(len(vals))),
                     "n_worlds": int(len(vals)),
                     "source": rel(path)})
        per_world.append(vals)
    return pd.DataFrame(rows), np.asarray(per_world, float)


def stage_fit(args: argparse.Namespace) -> None:
    t0 = time.time()
    cells, per_world = _load_cells()
    cells.to_csv(OUT / "cell_means.csv", index=False)
    r = cells["r_pred"].to_numpy(float)
    v = cells["V_person"].to_numpy(float)
    y = cells["field_mean"].to_numpy(float)

    fits: dict[str, Any] = {}
    loos: dict[str, Any] = {}
    for form in FORM_ORDER:
        fits[form] = fit_form(form, r, v, y)
        loos[form] = loo_rmse(form, r, v, y, fits[form]["theta"])
        print(f"  {form}: rmse={fits[form]['rmse']!r} loo={loos[form]['loo_rmse']!r} "
              f"({time.time() - t0:.1f}s)", flush=True)

    for form in FORM_ORDER:
        fits[form]["bootstrap"] = bootstrap_form(form, r, v, per_world,
                                                 fits[form]["theta"], B_BOOT, MASTER_SEED)
        print(f"  {form} bootstrap: {fits[form]['bootstrap']['n_used']}/{B_BOOT} used "
              f"({time.time() - t0:.1f}s)", flush=True)

    order = sorted(FORM_ORDER, key=lambda f: loos[f]["loo_rmse"])
    winner, runner = order[0], order[1]
    sep = loos[runner]["loo_rmse"] - loos[winner]["loo_rmse"]
    tie = bool(sep < TIE_REL * loos[winner]["loo_rmse"])

    out = {
        "utc": datetime.now(UTC).isoformat(), "n_cells": int(len(y)),
        "fits": fits, "ranking_by_loo": order, "winner": winner,
        "runner_up": runner,
        "loo_separation": float(sep),
        "loo_separation_rel": float(sep / loos[winner]["loo_rmse"]),
        "tie_rule_active": tie,
        "tie_rule": f"top two LOO-RMSE differ by < {TIE_REL:.0%} of the winner's",
        "boundary_flags": _boundary_flags(fits, loos, order),
        "seconds": time.time() - t0,
    }
    write_json(OUT / "fits.json", out)
    write_json(OUT / "loo.json", {"loo": loos, "ranking": order, "winner": winner,
                                  "cell_tags": list(cells["cell_tag"])})
    print(f"fit OK  winner={winner}  LOO={loos[winner]['loo_rmse']!r}  tie={tie}  "
          f"{time.time() - t0:.1f}s")
    _ordering_log("fit_done", winner=winner, loo=loos[winner]["loo_rmse"], tie=tie,
                  seconds=time.time() - t0)
    _ = args


def _boundary_flags(fits: dict[str, Any], loos: dict[str, Any],
                    order: list[str]) -> dict[str, Any]:
    """Rule 13: which verdict quantities sit within Monte-Carlo error of a bar."""
    recs = []
    winner = order[0]

    def add(name: str, value: float, bar: float, rel_scale: float | None = None) -> bool:
        scale = abs(bar) if rel_scale is None else abs(rel_scale)
        near = bool(abs(value - bar) <= BOUNDARY_REL * max(scale, 1e-300))
        recs.append({"quantity": name, "value": float(value), "bar": float(bar),
                     "gap": float(value - bar), "scale": float(scale),
                     f"within_{int(BOUNDARY_REL * 100)}pct": near})
        return near

    flagged = False
    for form in (winner, order[1]):
        b = fits[form]["bootstrap"]
        qlo, qhi = b["ci95"]["q"]
        flagged |= add(f"{form}: q CI width vs L-1 bar", qhi - qlo, L1_Q_WIDTH_MAX)
        for edge_name, edge in (("q_lo", qlo), ("q_hi", qhi)):
            for bar_name, bar in (("1.71", L2_RESPONSE_BAND[0]),
                                  ("1.98", L2_RESPONSE_BAND[1])):
                flagged |= add(f"{form}: {edge_name} vs response band {bar_name}",
                               edge, bar)
        klo, khi = b["ci95"]["kappa"]
        flagged |= add(f"{form}: kappa_hi vs K2f ci95 lo", khi, L3_KAPPA_CI[0])
        flagged |= add(f"{form}: kappa_lo vs K2f ci95 hi", klo, L3_KAPPA_CI[1])
        llo, lhi = b["ci95"]["lambda"]
        lam_hat = fits[form]["theta"][0]
        flagged |= add(f"{form}: lambda CI nearest endpoint vs 0 (RN-M1-6)",
                       float(min(abs(llo), abs(lhi))), 0.0, rel_scale=lam_hat)
    sep = loos[order[1]]["loo_rmse"] - loos[order[0]]["loo_rmse"]
    near_tie = bool(sep <= TIE_REL * loos[order[0]]["loo_rmse"])
    recs.append({"quantity": "LOO separation winner vs runner-up", "value": float(sep),
                 "bar": 0.0, "gap": float(sep),
                 "scale": float(loos[order[0]]["loo_rmse"]),
                 f"within_{int(BOUNDARY_REL * 100)}pct": near_tie})
    flagged |= near_tie
    return {"records": recs, "any_flagged": bool(flagged),
            "forms_to_rerun": [order[0], order[1]] if flagged else [],
            "rule": f"a quantity within {BOUNDARY_REL:.0%} of its bar triggers the "
                    f"B={B_BOOT_HIGH} re-run; a verdict that changes scores BOUNDARY"}


def stage_rule13(args: argparse.Namespace) -> None:
    t0 = time.time()
    fits = read_json(OUT / "fits.json")
    flags = fits["boundary_flags"]
    out: dict[str, Any] = {"utc": datetime.now(UTC).isoformat(),
                           "triggered": bool(flags["any_flagged"]),
                           "B": B_BOOT_HIGH, "seed": MASTER_SEED,
                           "forms": {}, "seconds": None}
    if flags["any_flagged"]:
        cells, per_world = _load_cells()
        r = cells["r_pred"].to_numpy(float)
        v = cells["V_person"].to_numpy(float)
        for form in flags["forms_to_rerun"]:
            th0 = fits["fits"][form]["theta"]
            out["forms"][form] = bootstrap_form(form, r, v, per_world, th0,
                                                B_BOOT_HIGH, MASTER_SEED)
            print(f"  {form} B={B_BOOT_HIGH}: {out['forms'][form]['n_used']} used "
                  f"({time.time() - t0:.1f}s)", flush=True)
    else:
        out["note"] = "no verdict quantity within Monte-Carlo error of its bar"
    out["seconds"] = time.time() - t0
    write_json(OUT / "boot_high.json", out)
    print(f"rule13 OK  triggered={out['triggered']}  {time.time() - t0:.1f}s")
    _ordering_log("rule13_done", triggered=out["triggered"], seconds=time.time() - t0)
    _ = args


# ---------------------------------------------------------------------------
# FINALIZE.

def _verdicts_for(form: str, boot: dict[str, Any],
                  theta: list[float], names: list[str]) -> dict[str, Any]:
    qlo, qhi = boot["ci95"]["q"]
    klo, khi = boot["ci95"]["kappa"]
    llo, lhi = boot["ci95"]["lambda"]
    width = qhi - qlo
    l1 = "HOLD" if width <= L1_Q_WIDTH_MAX else "MISS"
    if qhi < L2_RESPONSE_BAND[0]:
        l2 = "below"
    elif qlo > L2_RESPONSE_BAND[1]:
        l2 = "above"
    else:
        l2 = "overlap"
    overlap = not (khi < L3_KAPPA_CI[0] or klo > L3_KAPPA_CI[1])
    if overlap:
        l3 = "overlap"
    elif khi < L3_KAPPA_CI[0]:
        l3 = "disjoint-low"
    else:
        l3 = "disjoint-high"
    lam_contains_zero = bool(llo <= 0.0 <= lhi)
    return {"form": form, "theta": dict(zip(names, theta)),
            "q_ci": [qlo, qhi], "q_ci_width": float(width),
            "kappa_ci": [klo, khi], "lambda_ci": [llo, lhi],
            "L-1": l1, "L-2": l2, "L-3": l3,
            "lambda_ci_contains_zero": lam_contains_zero}


def _route(l1: str, l2: str, lam_zero: bool) -> tuple[int, str]:
    if l1 == "MISS":
        return (2, "R_TERM_ABSENT_AT_LEVEL") if lam_zero else (3,
                                                               "NON_IDENTIFIED_UNDERPOWERED")
    return {"below": (4, "LEVEL_RESPONSE_DISSOCIATION"),
            "overlap": (5, "SINGLE_EXPONENT_RESTORED"),
            "above": (6, "ABOVE_BAND_ANOMALY")}[l2]


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    g2 = read_json(OUT / "g2m_pilot.json")
    g3 = read_json(OUT / "g3mb_power.json")
    fits = read_json(OUT / "fits.json")
    loos = read_json(OUT / "loo.json")
    high = read_json(OUT / "boot_high.json")
    cells = read_csv_rt(OUT / "cell_means.csv")

    winner, runner = fits["winner"], fits["runner_up"]
    tie = fits["tie_rule_active"]
    vw = _verdicts_for(winner, fits["fits"][winner]["bootstrap"],
                       fits["fits"][winner]["theta"],
                       fits["fits"][winner]["param_names"])
    vr = _verdicts_for(runner, fits["fits"][runner]["bootstrap"],
                       fits["fits"][runner]["theta"],
                       fits["fits"][runner]["param_names"])

    # --- rule 13: stability at B=20000 -------------------------------------
    stability: dict[str, Any] = {"triggered": high["triggered"], "per_form": {}}
    vw_high = vr_high = None
    if high["triggered"]:
        if winner in high["forms"]:
            vw_high = _verdicts_for(winner, high["forms"][winner],
                                    fits["fits"][winner]["theta"],
                                    fits["fits"][winner]["param_names"])
            stability["per_form"][winner] = {
                "B2000": {k: vw[k] for k in ("L-1", "L-2", "L-3",
                                             "lambda_ci_contains_zero")},
                "B20000": {k: vw_high[k] for k in ("L-1", "L-2", "L-3",
                                                   "lambda_ci_contains_zero")},
                "q_ci_B2000": vw["q_ci"], "q_ci_B20000": vw_high["q_ci"],
                "kappa_ci_B2000": vw["kappa_ci"], "kappa_ci_B20000": vw_high["kappa_ci"],
                "lambda_ci_B2000": vw["lambda_ci"],
                "lambda_ci_B20000": vw_high["lambda_ci"],
                "max_endpoint_shift": float(max(
                    abs(vw_high["q_ci"][0] - vw["q_ci"][0]),
                    abs(vw_high["q_ci"][1] - vw["q_ci"][1]),
                    abs(vw_high["kappa_ci"][0] - vw["kappa_ci"][0]),
                    abs(vw_high["kappa_ci"][1] - vw["kappa_ci"][1]),
                    abs(vw_high["lambda_ci"][0] - vw["lambda_ci"][0]),
                    abs(vw_high["lambda_ci"][1] - vw["lambda_ci"][1]))),
                "stable": bool(all(vw[k] == vw_high[k] for k in
                                   ("L-1", "L-2", "L-3", "lambda_ci_contains_zero")))}
        if runner in high["forms"]:
            vr_high = _verdicts_for(runner, high["forms"][runner],
                                    fits["fits"][runner]["theta"],
                                    fits["fits"][runner]["param_names"])
            stability["per_form"][runner] = {
                "B2000": {k: vr[k] for k in ("L-1", "L-2", "L-3",
                                             "lambda_ci_contains_zero")},
                "B20000": {k: vr_high[k] for k in ("L-1", "L-2", "L-3",
                                                   "lambda_ci_contains_zero")},
                "stable": bool(all(vr[k] == vr_high[k] for k in
                                   ("L-1", "L-2", "L-3", "lambda_ci_contains_zero")))}
    stability["all_stable"] = bool(all(d["stable"] for d in stability["per_form"].values())
                                   ) if stability["per_form"] else True

    # --- the adjudicated verdicts, with the tie rule and rule 13 ------------
    def adjudicate(key: str) -> dict[str, Any]:
        w_val, r_val = vw[key], vr[key]
        rec: dict[str, Any] = {"winner_form": winner, "winner_value": w_val,
                               "runner_form": runner, "runner_value": r_val,
                               "tie_rule_active": tie}
        verdict = w_val
        if tie and w_val != r_val:
            verdict = "SPLIT"
            rec["split_values"] = {winner: w_val, runner: r_val}
        hv = (vw_high or {}).get(key)
        if hv is not None:
            rec["B20000_value"] = hv
            if hv != w_val:
                verdict = "BOUNDARY"
                rec["boundary_reason"] = (f"verdict changed between B={B_BOOT} ({w_val}) "
                                          f"and B={B_BOOT_HIGH} ({hv})")
        rec["verdict"] = verdict
        return rec

    a1, a2, a3 = adjudicate("L-1"), adjudicate("L-2"), adjudicate("L-3")
    lam_zero = adjudicate("lambda_ci_contains_zero")

    cell_n, slug = _route(a1["verdict"] if a1["verdict"] in ("HOLD", "MISS") else vw["L-1"],
                          a2["verdict"] if a2["verdict"] in
                          ("below", "overlap", "above") else vw["L-2"],
                          bool(vw["lambda_ci_contains_zero"]))
    modifier = ("TAX_SHIFT_AT_LEVEL" if a3["verdict"] in ("disjoint-low", "disjoint-high")
                else "KAPPA_FOURTH_APPEARANCE")
    if cell_n == 2:
        a2["verdict"] = "N/A"
        a2["note"] = "cell 2: the q question is unposed, L-2 recorded N/A (registration)"
    if cell_n == 3:
        a3["note"] = ("cell 3: L-3 reported descriptively, adjudicating nothing "
                      "(registration)")

    # --- L-4: the (r, V)-sufficiency probe, a reading with no gate ----------
    th = np.asarray(fits["fits"][winner]["theta"], float)
    r = cells["r_pred"].to_numpy(float)
    v = cells["V_person"].to_numpy(float)
    y = cells["field_mean"].to_numpy(float)
    resid = y - FORMS[winner]["fn"](th, r, v)
    cells = cells.assign(residual_winner=resid)
    per_share = []
    for share in sorted(cells["share"].unique()):
        sub = cells[cells["share"] == share].sort_values("phi")
        rho = spearman(sub["residual_winner"].to_numpy(float),
                       sub["phi"].to_numpy(float))
        per_share.append({"share": float(share), "n_phi": int(len(sub)),
                          "spearman_resid_phi": float(rho),
                          "sign": int(np.sign(rho)),
                          "perfectly_monotone": bool(abs(abs(rho) - 1.0) < 1e-12),
                          "residuals": [float(x) for x in sub["residual_winner"]],
                          "phis": [float(x) for x in sub["phi"]]})
    signs = [p["sign"] for p in per_share]
    n_pos = sum(1 for s in signs if s > 0)
    n_neg = sum(1 for s in signs if s < 0)
    mono_pos = sum(1 for p in per_share if p["sign"] > 0 and p["perfectly_monotone"])
    mono_neg = sum(1 for p in per_share if p["sign"] < 0 and p["perfectly_monotone"])
    l4 = {"per_share": per_share,
          "reading_A_sign_agreement": {
              "n_positive": n_pos, "n_negative": n_neg,
              "max_agreeing": max(n_pos, n_neg), "bar": L4_MIN_LEVELS,
              "finding": bool(max(n_pos, n_neg) >= L4_MIN_LEVELS)},
          "reading_B_perfect_monotone_and_sign": {
              "n_positive_monotone": mono_pos, "n_negative_monotone": mono_neg,
              "max_agreeing": max(mono_pos, mono_neg), "bar": L4_MIN_LEVELS,
              "finding": bool(max(mono_pos, mono_neg) >= L4_MIN_LEVELS)},
          "named_finding_if_true": "phi leaks past (r, V) -- T4's form-sufficiency "
                                   "questioned",
          "adjudication_weight": "NONE (registration: L-4 is a reading)",
          "readings_note": RN_NOTES["RN-M1-7"]}

    gates = {
        "G0m": {"PASS": p0["G0m"]["PASS"],
                "detail": "every anchor and every K2f/D-open number quoted in the "
                          "registration re-derived bit-exactly"},
        "G1m": {"PASS": p0["G1m"]["PASS"],
                "detail": f"design arithmetic on {p0['design']['n_cells']} cells; "
                          f"corr(r,V) = "
                          f"{p0['G1m']['(d) decollinearization']['corr_r_V']!r}"},
        "G2m": {"PASS": g2["PASS"], "detail": "16 pilot worlds finite and "
                                              "non-saturated; rule-3 liveness on the "
                                              "realized card channel"},
        "G3m": {"PASS": bool(g3["PASS"]),
                "detail": f"sides declared in Part 0; projected q width "
                          f"{[t['width_proxy'] for t in g3['projections'].values()]} "
                          f"against the {G3M_PROJ_WIDTH_MAX} bar; stage estimates "
                          f"written before the pilot"},
        "G4m": {"PASS": True, "detail": "rule-16 truth table reproduced verbatim; every "
                                        "report table generated from artifacts"},
    }

    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED, "salts": {"main": SALT_WORLD, "pilot": SALT_PILOT},
        "n_cells": int(len(cells)), "worlds_per_cell": N_WORLDS,
        "n_worlds_main": int(len(cells) * N_WORLDS),
        "design": p0["design"],
        "decollinearization": {
            "corr_r_V_M1": p0["G1m"]["(d) decollinearization"]["corr_r_V"],
            "corr_r_pow_q_V_M1": p0["G1m"]["(d) decollinearization"]["corr_r_pow_q_V"],
            "corr_r_V_K2f_26_rows": K2F_CORR_RV},
        "winner": winner, "winner_expr": FORMS[winner]["expr"],
        "winner_theta": dict(zip(fits["fits"][winner]["param_names"],
                                 fits["fits"][winner]["theta"])),
        "runner_up": runner,
        "loo_rmse_by_form": {f: loos["loo"][f]["loo_rmse"] for f in FORM_ORDER},
        "in_sample_rmse_by_form": {f: fits["fits"][f]["rmse"] for f in FORM_ORDER},
        "loo_separation": fits["loo_separation"],
        "loo_separation_rel": fits["loo_separation_rel"],
        "tie_rule_active": tie,
        "verdicts": {"L-1": a1, "L-2": a2, "L-3": a3,
                     "lambda_ci_contains_zero": lam_zero},
        "winner_intervals": {k: vw[k] for k in ("q_ci", "q_ci_width", "kappa_ci",
                                                "lambda_ci")},
        "runner_intervals": {k: vr[k] for k in ("q_ci", "q_ci_width", "kappa_ci",
                                                "lambda_ci")},
        "rule13_stability": stability,
        "routing_cell": cell_n, "verdict_slug": slug, "L-3_modifier": modifier,
        "routing_text": next(t["text"] for t in TRUTH_TABLE if t["n"] == str(cell_n)),
        "modifier_text": next(t["text"] for t in TRUTH_TABLE
                              if t["outcome"] == modifier),
        "L-4": l4,
        "sigma_w": g3["sigma_w"],
        "gates": gates,
        "field_mean_range": [float(cells["field_mean"].min()),
                             float(cells["field_mean"].max())],
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    cells.to_csv(OUT / "cell_means.csv", index=False)
    _write_report_tables(p0, g2, g3, fits, loos, high, cells, dec)
    _write_prose_facts(p0, g2, g3, fits, loos, cells, dec)
    print(f"finalize OK  slug={slug}  cell={cell_n}  modifier={modifier}  "
          f"L-1={a1['verdict']} L-2={a2['verdict']} L-3={a3['verdict']}")
    _ordering_log("finalize_done", slug=slug, cell=cell_n, modifier=modifier)
    _ = args


def _write_report_tables(p0: dict[str, Any], g2: dict[str, Any], g3: dict[str, Any],
                         fits: dict[str, Any], loos: dict[str, Any],
                         high: dict[str, Any], cells: pd.DataFrame,
                         dec: dict[str, Any]) -> None:
    """Rule 24: every table carrying artifact numbers is GENERATED here."""
    sec: dict[str, list[str]] = {}

    g1 = p0["G1m"]
    sec["design"] = _md_table(
        ["cell", "share", "phi", "r_pred", "V_person"],
        [[d["cell_tag"], repr(d["share"]), repr(d["phi"]), repr(d["r_pred"]),
          repr(d["V_person"])] for d in g1["design_points"]])

    rows = []
    for name, d in p0["G0m"]["maps"].items():
        rows.append([name, repr(d["expected"]), repr(d["rederived"]), str(d["bit_exact"])])
    for name, d in p0["G0m"]["k2f_quoted"].items():
        rows.append([name, repr(d["registration"]), repr(d["persisted"]),
                     str(d["bit_exact"])])
    for name, d in p0["G0m"]["registration_citations"].items():
        rows.append([name, repr(d["registration"]), repr(d["rederived"]),
                     str(d["bit_exact"])])
    d = p0["G0m"]["dopen_m4_level"]
    rows.append(["(v) Dopen:M-4 level, mean of the raw CSV", repr(d["expected"]),
                 repr(d["rederived"]), str(d["bit_exact"])])
    d = p0["G0m"]["theory_band"]
    rows.append([f"(vi) `{d['string']}` verbatim in `{d['doc']}`", d["string"],
                 f"found on lines {d['lines']}", str(d["found"])])
    sec["g0m"] = _md_table(["clause", "registration / expected",
                            "re-derived / persisted", "bit-exact"], rows)

    c = g1["(c) within-share r ratio"]
    d_ = g1["(d) decollinearization"]
    sec["g1m"] = _md_table(
        ["gate", "bar", "realized", "PASS"],
        [["(a) shares inside the trained envelope", repr(list(SHARE_ENVELOPE)),
          repr(list(SHARES)), str(g1["(a) shares inside envelope"]["PASS"])],
         ["(b) V max/min", f">= {G1M_V_RATIO_MIN}",
          repr(g1["(b) V ratio"]["ratio"]), str(g1["(b) V ratio"]["PASS"])],
         ["(c) within-share r max/min",
          f">= {G1M_R_RATIO_MIN} in >= {G1M_R_RATIO_MIN_LEVELS} share levels",
          f"{c['levels_meeting_bar']}/{len(SHARES)} levels", str(c["PASS"])],
         ["(d) cross-cell abs(corr(r, V))", f"<= {G1M_CORR_MAX}",
          repr(d_["abs_corr_r_V"]), str(d_["PASS"])],
         ["(e) duplicate (r, V) design points", "0",
          str(len(g1["(e) no duplicate design points"]["duplicates"])),
          str(g1["(e) no duplicate design points"]["PASS"])]])

    sec["leverage"] = _md_table(
        ["share", "V_person", "r min (at the ladder's phi MAX)",
         "r max (at the ladder's phi MIN)", "max/min", "meets 1.20"],
        [[repr(w["share"]),
          repr([d["V_person"] for d in g1["design_points"]
                if d["share"] == w["share"]][0]),
          repr(w["r_min"]), repr(w["r_max"]), repr(w["ratio"]), str(w["meets_bar"])]
         for w in c["per_share"]])

    sec["collinearity"] = _md_table(
        ["quantity", "value"],
        [["corr(r, V) on M1's 20-point design", repr(d_["corr_r_V"])],
         [f"corr(r^{SEALED_Q!r}, V) on M1's design", repr(d_["corr_r_pow_q_V"])],
         ["corr(r, V) on K2f's 26 rows (the object M1 breaks)",
          repr(d_["k2f_corr_r_V_26_rows"])],
         ["G1m(d) bar", f"<= {G1M_CORR_MAX}"]])

    sec["cells"] = _md_table(
        ["cell", "share", "phi", "r_pred", "V_person", "mean field", "SEM", "n"],
        [[row["cell_tag"], repr(row["share"]), repr(row["phi"]), repr(row["r_pred"]),
          repr(row["V_person"]), repr(row["field_mean"]), repr(row["field_sem"]),
          str(int(row["n_worlds"]))] for _, row in cells.iterrows()])

    frows = []
    for form in FORM_ORDER:
        f = fits["fits"][form]
        th = dict(zip(f["param_names"], f["theta"]))
        b = f["bootstrap"]
        frows.append([
            ("**" + form + " (winner)**") if form == fits["winner"] else form,
            "`" + FORMS[form]["expr"] + "`",
            repr(th["lambda"]), repr(b["ci95"]["lambda"]),
            repr(th["q"]), repr(b["ci95"]["q"]), repr(b["width"]["q"]),
            repr(th["kappa"]), repr(b["ci95"]["kappa"]),
            repr(th.get("p", th.get("epsilon", ""))) if len(th) > 3 else "--",
            repr(f["rmse"]), repr(loos["loo"][form]["loo_rmse"])])
    sec["fits"] = _md_table(
        ["form", "expression", "lambda", "lambda ci95", "q", "q ci95", "q width",
         "kappa", "kappa ci95", "4th param", "in-sample RMSE", "LOO-RMSE"], frows)

    sec["boot_meta"] = _md_table(
        ["form", "B", "draws used", "discarded", "n starts", "converged starts",
         "starts at global SSE", "distinct optima"],
        [[form, str(fits["fits"][form]["bootstrap"]["B"]),
          str(fits["fits"][form]["bootstrap"]["n_used"]),
          str(fits["fits"][form]["bootstrap"]["n_discarded"]),
          str(fits["fits"][form]["n_starts"]),
          str(fits["fits"][form]["n_converged"]),
          str(fits["fits"][form]["n_starts_at_global_sse"]),
          str(fits["fits"][form]["n_distinct_optima"])] for form in FORM_ORDER])

    v = dec["verdicts"]
    sec["verdicts"] = _md_table(
        ["lean", "clause", "sided", "prior", "measured", "verdict"],
        [["L-1", f"winner's q 95% CI width <= {L1_Q_WIDTH_MAX}", "one-sided (DOWN)",
          "0.55", f"width {dec['winner_intervals']['q_ci_width']!r} on "
                  f"{dec['winner_intervals']['q_ci']!r}", "**" + v["L-1"]["verdict"] + "**"],
         ["L-2", f"winner's q CI vs the response band {list(L2_RESPONSE_BAND)}",
          "two-sided (below / overlap / above)", "below .55 / overlap .35 / above .10",
          repr(dec["winner_intervals"]["q_ci"]), "**" + str(v["L-2"]["verdict"]) + "**"],
         ["L-3", f"winner's kappa CI overlaps K2f F2's {list(L3_KAPPA_CI)}",
          "two-sided overlap", "0.70", repr(dec["winner_intervals"]["kappa_ci"]),
          "**" + v["L-3"]["verdict"] + "**"],
         ["(routing input)", "winner's lambda CI contains 0", "two-sided", "--",
          repr(dec["winner_intervals"]["lambda_ci"]),
          str(v["lambda_ci_contains_zero"]["verdict"])],
         ["L-4", "Spearman(residual, phi) within share levels", "reading, NO gate", "--",
          f"reading A {dec['L-4']['reading_A_sign_agreement']['max_agreeing']}/4, "
          f"reading B {dec['L-4']['reading_B_perfect_monotone_and_sign']['max_agreeing']}"
          f"/4", "reading only"]])

    sec["truth_table"] = _md_table(
        ["#", "condition", "outcome"],
        [[t["n"], t["condition"],
          ("**" + t["text"] + "**  <-- THIS LEG")
          if (t["n"] == str(dec["routing_cell"]) or t["outcome"] == dec["L-3_modifier"])
          else t["text"]] for t in TRUTH_TABLE])

    sec["l4"] = _md_table(
        ["share", "Spearman(residual, phi)", "sign", "perfectly monotone",
         "residuals by phi"],
        [[repr(p["share"]), repr(p["spearman_resid_phi"]), str(p["sign"]),
          str(p["perfectly_monotone"]),
          ", ".join(repr(x) for x in p["residuals"])]
         for p in dec["L-4"]["per_share"]])

    sec["pilot"] = _md_table(
        ["cell", "world", "world seed", "recovery_b_only", "realized r_card_b_raw"],
        [[cell_tag(w["share"], w["phi"]), str(int(w["world"])), str(int(w["world_seed"])),
          repr(w["recovery_b_only"]), repr(w["r_card_b_raw"])]
         for w in g2["per_world"]])

    liv = g2["(ii) liveness (rule 3)"]
    sec["liveness"] = _md_table(
        ["reading", "mean at phi lo", "mean at phi hi", "contrast", "pooled SE",
         "abs(contrast)/SE", f"> {G2M_LIVENESS_SE_MULT}x SE"],
        [["card attenuation `r_card_b_raw` (GATE, RN-M1-3)",
          repr(liv["GATE_reading_card_attenuation"]["mean_at_phi_lo"]),
          repr(liv["GATE_reading_card_attenuation"]["mean_at_phi_hi"]),
          repr(liv["GATE_reading_card_attenuation"]["contrast"]),
          repr(liv["GATE_reading_card_attenuation"]["pooled_SE"]),
          repr(liv["GATE_reading_card_attenuation"]["abs_contrast_over_SE"]),
          str(liv["GATE_reading_card_attenuation"]["PASS"])],
         ["field `recovery_b_only` (declared fallback reading)",
          repr(liv["declared_fallback_reading_field_contrast"]["mean_at_phi_lo"]),
          repr(liv["declared_fallback_reading_field_contrast"]["mean_at_phi_hi"]),
          repr(liv["declared_fallback_reading_field_contrast"]["contrast"]),
          repr(liv["declared_fallback_reading_field_contrast"]["pooled_SE"]),
          repr(liv["declared_fallback_reading_field_contrast"]["abs_contrast_over_SE"]),
          str(liv["declared_fallback_reading_field_contrast"]["PASS"])]])

    sec["power"] = _md_table(
        ["quantity", "value"],
        [["pooled per-world sd over the 16 pilot worlds (df "
          f"{g3['pooled_df']})", repr(g3["sigma_w_raw_pooled"])],
         [f"chi2_{{{G3M_CHI2_Q}, df={G3M_DF}}}", repr(g3["chi2_quantile"]["value"])],
         ["df-aware inflation sqrt(12 / chi2)", repr(g3["df_inflation_factor"])],
         ["sigma_w (inflated)", repr(g3["sigma_w"])],
         [f"cell-mean sd used, sigma_w / sqrt({N_WORLDS})", repr(g3["cell_mean_sd_used"])]]
        + [[f"projected q width proxy at q_truth = {t['q_truth']!r} "
            f"(B_proj {t['B_proj']})", repr(t["width_proxy"])]
           for t in g3["projections"].values()]
        + [[f"gate: proxy <= {G3M_PROJ_WIDTH_MAX} under BOTH truths", str(g3["PASS"])]])

    sec["rule13"] = _md_table(
        ["quantity", "value", "bar", "scale", f"within {int(BOUNDARY_REL * 100)}%"],
        [[rec["quantity"], repr(rec["value"]), repr(rec["bar"]), repr(rec["scale"]),
          str(rec[f"within_{int(BOUNDARY_REL * 100)}pct"])]
         for rec in fits["boundary_flags"]["records"]])

    if high["triggered"] and dec["rule13_stability"]["per_form"]:
        rows13 = []
        for form, d13 in dec["rule13_stability"]["per_form"].items():
            for key in ("L-1", "L-2", "L-3", "lambda_ci_contains_zero"):
                rows13.append([form, key, str(d13["B2000"][key]),
                               str(d13["B20000"][key]),
                               str(d13["B2000"][key] == d13["B20000"][key])])
        sec["stability"] = _md_table(
            ["form", "verdict", f"B={B_BOOT}", f"B={B_BOOT_HIGH}", "unchanged"], rows13)
    else:
        sec["stability"] = ["_(rule 13 did not fire: no verdict quantity sat within "
                            f"{BOUNDARY_REL:.0%} of its bar)_"]

    sec["gates"] = _md_table(
        ["gate", "PASS", "detail"],
        [[k, str(d["PASS"]), d["detail"]] for k, d in dec["gates"].items()])

    sec["rn"] = _md_table(["note", "pinned reading"],
                          [[k, v_] for k, v_ in RN_NOTES.items()])

    sec["env"] = _md_table(
        ["component", "value"],
        [[k, str(v_)] for k, v_ in p0["environment"].items()])

    sec["timing"] = _md_table(
        ["stage", "registration estimate (s)", "executor estimate (s)", "measured (s)"],
        _timing_rows(p0))

    body = ["# M4-M1 report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _timing_rows(p0: dict[str, Any]) -> list[list[str]]:
    reg = p0["stage_estimates_seconds_registration"]
    ex = p0["stage_estimates_seconds_executor"]
    measured: dict[str, float] = {}
    for line in (OUT / "ordering_log.jsonl").read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        if rec["event"].endswith("_done") and "seconds" in rec:
            measured[rec["event"][:-5]] = float(rec["seconds"])
    reg_map = {"part0": reg["part0"], "pilot": reg["pilot"], "power": None,
               "worlds_a": reg["worlds_each"], "worlds_b": reg["worlds_each"],
               "worlds_c": reg["worlds_each"], "worlds_d": reg["worlds_each"],
               "fit": reg["fit"], "rule13": None, "finalize": reg["finalize"],
               "diagnose": None}
    rows = []
    for st in ("part0", "diagnose", "pilot", "power", "worlds_a", "worlds_b", "worlds_c",
               "worlds_d", "fit", "rule13", "finalize"):
        rows.append([st,
                     "--" if reg_map[st] is None else str(reg_map[st]),
                     str(ex.get(st, "--")),
                     ("%.3f" % measured[st]) if st in measured
                     else "-- (not reached)"])
    return rows


def _write_prose_facts(p0: dict[str, Any], g2: dict[str, Any], g3: dict[str, Any],
                       fits: dict[str, Any], loos: dict[str, Any],
                       cells: pd.DataFrame, dec: dict[str, Any]) -> None:
    """Every number the report's PROSE quotes, generated here (rule 8 + rule 24)."""
    g1 = p0["G1m"]
    d_ = g1["(d) decollinearization"]
    w = dec["winner"]
    wb = fits["fits"][w]["bootstrap"]
    wth = dict(zip(fits["fits"][w]["param_names"], fits["fits"][w]["theta"]))
    liv = g2["(ii) liveness (rule 3)"]
    facts = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "MODIFIER": dec["L-3_modifier"],
        "WINNER": w, "WINNER_EXPR": FORMS[w]["expr"], "RUNNER": dec["runner_up"],
        "N_CELLS": dec["n_cells"], "N_WORLDS_MAIN": dec["n_worlds_main"],
        "WORLDS_PER_CELL": N_WORLDS,
        "CORR_RV": d_["corr_r_V"], "ABS_CORR_RV": d_["abs_corr_r_V"],
        "CORR_RQ_V": d_["corr_r_pow_q_V"], "CORR_RV_K2F": K2F_CORR_RV,
        "V_RATIO": g1["(b) V ratio"]["ratio"],
        "R_RATIO_LEVELS": g1["(c) within-share r ratio"]["levels_meeting_bar"],
        "R_RATIO_MIN": min(x["ratio"] for x in
                           g1["(c) within-share r ratio"]["per_share"]),
        "R_RATIO_MAX": max(x["ratio"] for x in
                           g1["(c) within-share r ratio"]["per_share"]),
        "LAMBDA": wth["lambda"], "LAMBDA_CI": dec["winner_intervals"]["lambda_ci"],
        "Q": wth["q"], "Q_CI": dec["winner_intervals"]["q_ci"],
        "Q_WIDTH": dec["winner_intervals"]["q_ci_width"],
        "KAPPA": wth["kappa"], "KAPPA_CI": dec["winner_intervals"]["kappa_ci"],
        "FOURTH_PARAM": {k: v_ for k, v_ in wth.items()
                         if k in ("p", "epsilon")} or None,
        "LOO_WINNER": loos["loo"][w]["loo_rmse"],
        "LOO_ALL": {f: loos["loo"][f]["loo_rmse"] for f in FORM_ORDER},
        "RMSE_ALL": {f: fits["fits"][f]["rmse"] for f in FORM_ORDER},
        "LOO_SEP": dec["loo_separation"], "LOO_SEP_REL": dec["loo_separation_rel"],
        "TIE_ACTIVE": dec["tie_rule_active"],
        "L1": dec["verdicts"]["L-1"]["verdict"], "L2": dec["verdicts"]["L-2"]["verdict"],
        "L3": dec["verdicts"]["L-3"]["verdict"],
        "LAMBDA_ZERO": dec["verdicts"]["lambda_ci_contains_zero"]["verdict"],
        "SIGMA_W_RAW": g3["sigma_w_raw_pooled"], "SIGMA_W": g3["sigma_w"],
        "INFLATION": g3["df_inflation_factor"],
        "PROJ_WIDTHS": {k: t["width_proxy"] for k, t in g3["projections"].items()},
        "CELL_SD": g3["cell_mean_sd_used"],
        "FIELD_MIN": float(cells["field_mean"].min()),
        "FIELD_MAX": float(cells["field_mean"].max()),
        "FIELD_RANGE": float(cells["field_mean"].max() - cells["field_mean"].min()),
        "SEM_MIN": float(cells["field_sem"].min()),
        "SEM_MAX": float(cells["field_sem"].max()),
        "LIVE_CARD_SE": liv["GATE_reading_card_attenuation"]["abs_contrast_over_SE"],
        "LIVE_CARD_CONTRAST": liv["GATE_reading_card_attenuation"]["contrast"],
        "LIVE_FIELD_SE":
            liv["declared_fallback_reading_field_contrast"]["abs_contrast_over_SE"],
        "LIVE_AGREE": liv["readings_agree"],
        "RULE13_TRIGGERED": dec["rule13_stability"]["triggered"],
        "RULE13_STABLE": dec["rule13_stability"]["all_stable"],
        "L4_A": dec["L-4"]["reading_A_sign_agreement"]["max_agreeing"],
        "L4_B": dec["L-4"]["reading_B_perfect_monotone_and_sign"]["max_agreeing"],
        "L4_A_FINDING": dec["L-4"]["reading_A_sign_agreement"]["finding"],
        "L4_B_FINDING": dec["L-4"]["reading_B_perfect_monotone_and_sign"]["finding"],
        "L4_RHOS": [p["spearman_resid_phi"] for p in dec["L-4"]["per_share"]],
        "PHI_LADDER": p0["design"]["phi_ladder_adopted"],
        "SHARES": list(SHARES),
        "ROUTING_TEXT": dec["routing_text"], "MODIFIER_TEXT": dec["modifier_text"],
        "N_BOOT_DISCARD": {f: fits["fits"][f]["bootstrap"]["n_discarded"]
                           for f in FORM_ORDER},
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
    }
    write_json(OUT / "prose_facts.json", facts)


# ---------------------------------------------------------------------------
# THE STOP PATH (truth-table cell 1).  RN-M1-8.

def stage_diagnose(args: argparse.Namespace) -> None:
    """Measure HOW unsatisfiable the failed gate is, so the planner gets a
    defect it can act on.  Pure design arithmetic: no world, no field, no fit."""
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    if p0["G1m"]["PASS"] and p0["G0m"]["PASS"]:
        raise SystemExit("REFUSED: `diagnose` is the STOP path; Part 0 passed.")
    for nm in ("cells", "g2m_pilot.json", "fits.json"):
        if (OUT / nm).exists():
            raise SystemExit(f"REFUSED: {nm} exists; this is not a clean STOP.")

    phis = np.round(np.linspace(DIAG_PHI_LO, DIAG_PHI_HI, DIAG_PHI_N), 6)
    rmat = np.array([[r_of(s, float(p)) for p in phis] for s in SHARES])
    vvec = np.array([v_of(s) for s in SHARES])

    def corr_at(share_idx: list[int], phi_idx: list[int],
                rm: np.ndarray, vv: np.ndarray) -> float:
        r = rm[np.ix_(share_idx, phi_idx)].ravel()
        v = np.repeat(vv[share_idx], len(phi_idx))
        return float(np.corrcoef(r, v)[0, 1])

    # (1) infimum over 5-point distinct phi ladders at the REGISTERED shares.
    import itertools
    all_shares = list(range(len(SHARES)))
    best_val, best_combo = 1.0, None
    for combo in itertools.combinations(range(0, DIAG_PHI_N, DIAG_PHI_COARSE_STRIDE), 5):
        c = abs(corr_at(all_shares, list(combo), rmat, vvec))
        if c < best_val:
            best_val, best_combo = c, list(combo)
    cur = list(best_combo or [])
    improved = True
    while improved:
        improved = False
        for k in range(5):
            for cand in range(DIAG_PHI_N):
                if cand in cur:
                    continue
                trial = sorted(cur[:k] + [cand] + cur[k + 1:])
                c = abs(corr_at(all_shares, trial, rmat, vvec))
                if c < best_val - 1e-15:
                    best_val, cur = c, trial
                    improved = True
    pinned = {"inf_abs_corr": float(best_val),
              "argmin_phi_ladder": [float(x) for x in phis[cur]],
              "bar": G1M_CORR_MAX,
              "multiple_of_bar": float(best_val / G1M_CORR_MAX),
              "satisfiable": bool(best_val <= G1M_CORR_MAX),
              "search": f"exhaustive over every {DIAG_PHI_COARSE_STRIDE}th of "
                        f"{DIAG_PHI_N} phi grid points in "
                        f"({DIAG_PHI_LO}, {DIAG_PHI_HI}), then greedy 1-swap refinement "
                        f"to convergence over the full grid"}

    # (2) shares ALSO freed inside gate (a), subject to gate (b).
    sgrid = np.round(np.linspace(SHARE_ENVELOPE[0], SHARE_ENVELOPE[1], DIAG_SHARE_N), 6)
    rfree = np.array([[r_of(float(s), float(p)) for p in phis] for s in sgrid])
    vfree = np.array([v_of(float(s)) for s in sgrid])
    rng = np.random.default_rng(MASTER_SEED)
    bf_val, bf_s, bf_p = 1.0, None, None
    n_skipped = 0
    for _ in range(DIAG_RANDOM_DRAWS):
        si = sorted(rng.choice(DIAG_SHARE_N, 4, replace=False))
        pi = sorted(rng.choice(DIAG_PHI_N, 5, replace=False))
        if vfree[si[-1]] / vfree[si[0]] < G1M_V_RATIO_MIN:
            n_skipped += 1
            continue
        c = abs(corr_at(list(si), list(pi), rfree, vfree))
        if c < bf_val:
            bf_val, bf_s, bf_p = c, si, pi
    freed = {"best_abs_corr_found": float(bf_val),
             "shares": [float(x) for x in sgrid[bf_s]] if bf_s else None,
             "V_ratio": float(vfree[bf_s[-1]] / vfree[bf_s[0]]) if bf_s else None,
             "phi_ladder": [float(x) for x in phis[bf_p]] if bf_p else None,
             "bar": G1M_CORR_MAX, "multiple_of_bar": float(bf_val / G1M_CORR_MAX),
             "satisfiable": bool(bf_val <= G1M_CORR_MAX),
             "search": f"{DIAG_RANDOM_DRAWS} seeded random 4-share x 5-phi draws over a "
                       f"{DIAG_SHARE_N}-point share grid on gate (a)'s envelope and the "
                       f"{DIAG_PHI_N}-point phi grid, rejecting draws that fail gate (b)",
             "n_draws_rejected_by_gate_b": int(n_skipped),
             "note": "an UPPER BOUND on the infimum -- a random search, not a proof; it "
                     "is already above the bar, which is the point"}

    # (3) why: phi's leverage against share's.
    lev = []
    for i, s in enumerate(SHARES):
        rr = rmat[i]
        lev.append({"share": s, "V_person": float(vvec[i]),
                    "r_at_phi_max": float(rr[-1]), "r_at_phi_min": float(rr[0]),
                    "max_span_over_full_phi_interval": float(rr.max() - rr.min()),
                    "max_ratio_over_full_phi_interval": float(rr.max() / rr.min()),
                    "reaches_G1m_c_bar_anywhere": bool(rr.max() / rr.min()
                                                       >= G1M_R_RATIO_MIN)})
    between = float(r_of(min(SHARES), 0.90) - r_of(max(SHARES), 0.90))

    # (4) the ladders actually registered, both correlation conventions.
    conv = {}
    for nm, ladder in (("registered base ladder", PHIS),
                       ("pre-declared fallback ladder", PHIS_LADDER_G1M),
                       ("G2m liveness fallback ladder", PHIS_LADDER_LIVENESS)):
        r = np.array([r_of(s, p) for s in SHARES for p in ladder])
        v = np.array([v_of(s) for s in SHARES for p in ladder])
        conv[nm] = {"phi_ladder": list(ladder),
                    "pearson_corr_r_V": pearson(r, v),
                    "spearman_corr_r_V": spearman(r, v),
                    "pearson_corr_r_pow_q_V": pearson(r ** SEALED_Q, v),
                    "abs_pearson": float(abs(pearson(r, v))),
                    "passes_G1m_d": bool(abs(pearson(r, v)) <= G1M_CORR_MAX)}

    vlin = sorted({round(v_of(s) / s, 15) for s in (0.02, 0.10, 0.25, 0.40, 0.60,
                                                    SHARE_ENVELOPE[1])})
    diag = {
        "utc": datetime.now(UTC).isoformat(), "note": RN_NOTES["RN-M1-8"],
        "worlds_generated_in_this_leg": int(_GEN_COUNT),
        "failed_gate": "G1m(d) -- cross-cell |corr(r, V)| <= 0.30",
        "gates_that_passed": ["G0m", "G1m(a)", "G1m(b)", "G1m(c)", "G1m(e)"],
        "ladders": conv,
        "infimum_at_registered_shares": pinned,
        "best_with_shares_also_freed": freed,
        "phi_leverage_per_share": lev,
        "between_share_r_span_at_phi_0.90": between,
        "V_is_exactly_linear_in_share": {"V_over_share_values": vlin,
                                         "linear": bool(len(vlin) == 1)},
        "mechanism": (
            "V is EXACTLY a linear function of share (V/share = "
            f"{vlin[0]!r} at every share tested), and r is monotone decreasing in "
            "share, so share alone drives r and V in lockstep. phi is the only knob "
            "orthogonal to V, and its TOTAL leverage over the full open interval "
            f"(0.001, 0.999) is at most {max(x['max_span_over_full_phi_interval'] for x in lev)!r} "
            f"in r (at share {max(lev, key=lambda x: x['max_span_over_full_phi_interval'])['share']!r}) "
            f"against a between-share r span of {between!r} at fixed phi. Gate (b) "
            "REQUIRES V max/min >= 2, i.e. a share range wide enough to make the "
            "between-share r spread dominate; gate (d) requires the within-share "
            "(phi-driven) spread to dominate instead. In this world family both "
            "cannot hold at once."),
        "defect_class": (
            "Rule-11 satisfiability, and rule-18 JOINT satisfiability across clauses "
            "sharing generative knobs: gate (b) and gate (d) share `share`, and the "
            "registration checked neither jointly nor arithmetically against the bar it "
            "wrote. The registration's own cited facts already contained the warning -- "
            f"it quotes r(0.30, 0.90) = {ANCHORS['r_030_090']!r} vs r(0.30, 0.98) = "
            f"{ANCHORS['r_030_098']!r}, a "
            f"{100 * (ANCHORS['r_030_090'] - ANCHORS['r_030_098']) / ANCHORS['r_030_098']:.2f}"
            "% move, and never asked what correlation a knob that small can buy against "
            f"a share axis that moves r by {between:.4f} at fixed phi."),
        "what_the_registration_got_right": (
            "The DIRECTION is real and verified: phi does move r at exactly fixed V "
            "(gate (c) passes in 2 of 4 share levels on the fallback ladder), and the "
            "factorial does reduce the collinearity -- from K2f's "
            f"{K2F_CORR_RV!r} to {conv['registered base ladder']['pearson_corr_r_V']!r} "
            f"(base) and {conv['pre-declared fallback ladder']['pearson_corr_r_V']!r} "
            "(fallback ladder). What fails is MAGNITUDE, not sign."),
        "seconds": time.time() - t0,
    }
    write_json(OUT / "stop_diagnostic.json", diag)

    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED, "salts": {"main": SALT_WORLD, "pilot": SALT_PILOT},
        "verdict_slug": "STOP_DESIGN_INFEASIBLE", "routing_cell": 1,
        "routing_text": next(t["text"] for t in TRUTH_TABLE if t["n"] == "1"),
        "L-3_modifier": None,
        "modifier_text": "none -- the L-3 modifier is defined only for cells 2-6",
        "worlds_generated": int(_GEN_COUNT),
        "pilot_run": False, "fit_run": False,
        "verdicts": {"L-1": "NOT EVALUATED (cell 1: no fit is run)",
                     "L-2": "NOT EVALUATED (cell 1: no fit is run)",
                     "L-3": "NOT EVALUATED (cell 1: no fit is run)",
                     "L-4": "NOT EVALUATED (cell 1: no fit is run)"},
        "gates": {
            "G0m": {"PASS": p0["G0m"]["PASS"],
                    "detail": "every anchor and every K2f / D-open number quoted in the "
                              "registration re-derived bit-exactly; no citation defect"},
            "G1m": {"PASS": p0["G1m"]["PASS"],
                    "detail": "gates (a), (b), (c) and (e) pass on the fallback ladder; "
                              "gate (d) FAILS on the base ladder and again after the "
                              "pre-declared one-step extension"},
            "G2m": {"PASS": None, "detail": "not reached -- the pilot runs only after "
                                            "G0m/G1m (registration ordering)"},
            "G3m": {"PASS": None, "detail": "(a) sides and (c) stage estimates written "
                                            "in Part 0; (b) the power projection needs "
                                            "pilot sigma_w and was not reached"},
            "G4m": {"PASS": True, "detail": "rule-16 truth table reproduced verbatim; "
                                            "every report table generated from artifacts"},
        },
        "stop_diagnostic": diag,
        "part0_utc": p0["utc"],
    }
    write_json(OUT / "decision.json", dec)
    # logged BEFORE the tables are written: the timing table reads this log
    _ordering_log("diagnose_done", slug="STOP_DESIGN_INFEASIBLE",
                  inf_abs_corr=pinned["inf_abs_corr"], seconds=diag["seconds"])
    _write_stop_tables(p0, diag, dec)
    _write_stop_prose_facts(p0, diag, dec)
    print(f"diagnose OK  slug=STOP_DESIGN_INFEASIBLE  inf|corr| at registered shares="
          f"{pinned['inf_abs_corr']!r} ({pinned['multiple_of_bar']:.2f}x the bar)  "
          f"{time.time() - t0:.1f}s")
    _ = args


def _stop_common_sections(p0: dict[str, Any], diag: dict[str, Any],
                          dec: dict[str, Any]) -> dict[str, list[str]]:
    sec: dict[str, list[str]] = {}
    g1 = p0["G1m"]
    sec["design"] = _md_table(
        ["cell", "share", "phi", "r_pred", "V_person"],
        [[d["cell_tag"], repr(d["share"]), repr(d["phi"]), repr(d["r_pred"]),
          repr(d["V_person"])] for d in g1["design_points"]])

    rows = []
    for name, d in p0["G0m"]["maps"].items():
        rows.append([name, repr(d["expected"]), repr(d["rederived"]), str(d["bit_exact"])])
    for name, d in p0["G0m"]["k2f_quoted"].items():
        rows.append([name, repr(d["registration"]), repr(d["persisted"]),
                     str(d["bit_exact"])])
    for name, d in p0["G0m"]["registration_citations"].items():
        rows.append([name, repr(d["registration"]), repr(d["rederived"]),
                     str(d["bit_exact"])])
    d = p0["G0m"]["dopen_m4_level"]
    rows.append(["(v) Dopen:M-4 level, mean of the raw per-world CSV", repr(d["expected"]),
                 repr(d["rederived"]), str(d["bit_exact"])])
    d = p0["G0m"]["theory_band"]
    rows.append([f"(vi) `{d['string']}` verbatim in `{d['doc']}`", d["string"],
                 f"found on lines {d['lines']}", str(d["found"])])
    sec["g0m"] = _md_table(["clause", "registration / expected",
                            "re-derived / persisted", "bit-exact"], rows)

    c = g1["(c) within-share r ratio"]
    d_ = g1["(d) decollinearization"]
    sec["g1m"] = _md_table(
        ["gate", "bar", "realized (fallback ladder)", "PASS"],
        [["(a) shares inside the trained envelope", repr(list(SHARE_ENVELOPE)),
          repr(list(SHARES)), str(g1["(a) shares inside envelope"]["PASS"])],
         ["(b) V max/min", f">= {G1M_V_RATIO_MIN}", repr(g1["(b) V ratio"]["ratio"]),
          str(g1["(b) V ratio"]["PASS"])],
         ["(c) within-share r max/min",
          f">= {G1M_R_RATIO_MIN} in >= {G1M_R_RATIO_MIN_LEVELS} share levels",
          f"{c['levels_meeting_bar']}/{len(SHARES)} levels", str(c["PASS"])],
         ["**(d) cross-cell abs(corr(r, V))**", f"**<= {G1M_CORR_MAX}**",
          "**" + repr(d_["abs_corr_r_V"]) + "**", "**" + str(d_["PASS"]) + "**"],
         ["(e) duplicate (r, V) design points", "0",
          str(len(g1["(e) no duplicate design points"]["duplicates"])),
          str(g1["(e) no duplicate design points"]["PASS"])]])

    sec["ladders"] = _md_table(
        ["phi ladder", "values", "Pearson corr(r, V)", "Spearman corr(r, V)",
         f"Pearson corr(r^{SEALED_Q!r}, V)", f"passes (d) (<= {G1M_CORR_MAX})"],
        [[nm, repr(v_["phi_ladder"]), repr(v_["pearson_corr_r_V"]),
          repr(v_["spearman_corr_r_V"]), repr(v_["pearson_corr_r_pow_q_V"]),
          str(v_["passes_G1m_d"])] for nm, v_ in diag["ladders"].items()]
        + [["K2f's 26 published rows (the object M1 set out to break)", "--",
            repr(K2F_CORR_RV), "--", "--", "--"]])

    sec["leverage"] = _md_table(
        ["share", "V_person", "r min (at the ladder's phi MAX)",
         "r max (at the ladder's phi MIN)", "max/min",
         f"meets (c)'s {G1M_R_RATIO_MIN}"],
        [[repr(w["share"]),
          repr([d2["V_person"] for d2 in g1["design_points"]
                if d2["share"] == w["share"]][0]),
          repr(w["r_min"]), repr(w["r_max"]), repr(w["ratio"]), str(w["meets_bar"])]
         for w in c["per_share"]])

    sec["phi_ceiling"] = _md_table(
        ["share", "V_person", f"r at phi={DIAG_PHI_LO}", f"r at phi={DIAG_PHI_HI}",
         "max r span over the FULL open phi interval", "max r ratio",
         f"can EVER meet (c)'s {G1M_R_RATIO_MIN}"],
        [[repr(x["share"]), repr(x["V_person"]), repr(x["r_at_phi_min"]),
          repr(x["r_at_phi_max"]), repr(x["max_span_over_full_phi_interval"]),
          repr(x["max_ratio_over_full_phi_interval"]),
          str(x["reaches_G1m_c_bar_anywhere"])]
         for x in diag["phi_leverage_per_share"]])

    pin, fre = diag["infimum_at_registered_shares"], diag["best_with_shares_also_freed"]
    sec["satisfiability"] = _md_table(
        ["search", "best abs(corr(r, V)) reachable", "bar", "multiple of the bar",
         "gate (d) satisfiable?"],
        [["all 5-point distinct phi ladders, shares PINNED as registered",
          repr(pin["inf_abs_corr"]), repr(pin["bar"]),
          "%.2fx" % pin["multiple_of_bar"], str(pin["satisfiable"])],
         ["shares ALSO freed inside gate (a), subject to gate (b)'s V max/min >= 2",
          repr(fre["best_abs_corr_found"]), repr(fre["bar"]),
          "%.2fx" % fre["multiple_of_bar"], str(fre["satisfiable"])],
         ["as registered (base ladder)",
          repr(diag["ladders"]["registered base ladder"]["abs_pearson"]),
          repr(G1M_CORR_MAX),
          "%.2fx" % (diag["ladders"]["registered base ladder"]["abs_pearson"]
                     / G1M_CORR_MAX),
          str(diag["ladders"]["registered base ladder"]["passes_G1m_d"])],
         ["after the pre-declared fallback ladder",
          repr(diag["ladders"]["pre-declared fallback ladder"]["abs_pearson"]),
          repr(G1M_CORR_MAX),
          "%.2fx" % (diag["ladders"]["pre-declared fallback ladder"]["abs_pearson"]
                     / G1M_CORR_MAX),
          str(diag["ladders"]["pre-declared fallback ladder"]["passes_G1m_d"])]])

    sec["argmin"] = _md_table(
        ["search", "argmin phi ladder", "argmin shares", "V max/min"],
        [["shares PINNED", repr(pin["argmin_phi_ladder"]), repr(list(SHARES)),
          repr(p0["G1m"]["(b) V ratio"]["ratio"])],
         ["shares freed", repr(fre["phi_ladder"]), repr(fre["shares"]),
          repr(fre["V_ratio"])]])

    sec["truth_table"] = _md_table(
        ["#", "condition", "outcome"],
        [[t["n"], t["condition"],
          ("**" + t["text"] + "**  <-- THIS LEG")
          if t["n"] == str(dec["routing_cell"]) else t["text"]] for t in TRUTH_TABLE])

    sec["verdicts"] = _md_table(
        ["lean", "clause", "sided", "prior", "verdict", "why"],
        [["L-1", SIDES["L-1"]["clause"], SIDES["L-1"]["sided"],
          repr(SIDES["L-1"]["prior"]), "**NOT EVALUATED**",
          "cell 1: no fit is run"],
         ["L-2", SIDES["L-2"]["clause"], SIDES["L-2"]["sided"],
          "below .55 / overlap .35 / above .10", "**NOT EVALUATED**",
          "conditional on L-1; no fit is run"],
         ["L-3", SIDES["L-3"]["clause"], SIDES["L-3"]["sided"],
          repr(SIDES["L-3"]["prior"]), "**NOT EVALUATED**",
          "defined in cells 2-6 only; no fit is run"],
         ["L-4", SIDES["L-4"]["clause"], SIDES["L-4"]["sided"], "--",
          "**NOT EVALUATED**",
          "a reading on the winner's residuals; there is no winner"]])

    sec["sides"] = _md_table(
        ["clause", "statement", "sided", "improvement side"],
        [[k, str(v_["clause"]), str(v_["sided"]), str(v_.get("improvement_side", "--"))]
         for k, v_ in SIDES.items()])

    sec["gates"] = _md_table(
        ["gate", "PASS", "detail"],
        [[k, str(d2["PASS"]), d2["detail"]] for k, d2 in dec["gates"].items()])

    sec["rn"] = _md_table(["note", "pinned reading"],
                          [[k, v_] for k, v_ in RN_NOTES.items()])
    sec["env"] = _md_table(["component", "value"],
                           [[k, str(v_)] for k, v_ in p0["environment"].items()])
    sec["optimizer"] = _md_table(
        ["pin", "value"],
        [[k, repr(v_) if not isinstance(v_, str) else v_]
         for k, v_ in p0["optimizer"].items() if k not in ("start_grid",)]
        + [["start grid", repr(p0["optimizer"]["start_grid"])]])
    sec["forms"] = _md_table(
        ["form", "expression", "params", "starts", "bounded"],
        [[f, FORMS[f]["expr"], repr(list(FORMS[f]["names"])),
          str(len(starts_for(f))), str(FORMS[f]["bounded"])] for f in FORM_ORDER])
    sec["timing"] = _md_table(
        ["stage", "registration estimate (s)", "executor estimate (s)", "measured (s)"],
        _timing_rows(p0))
    return sec


def _write_stop_tables(p0: dict[str, Any], diag: dict[str, Any],
                       dec: dict[str, Any]) -> None:
    sec = _stop_common_sections(p0, diag, dec)
    body = ["# M4-M1 report tables (GENERATED from artifacts -- rule 24)",
            "", "STOP path: truth-table cell 1.  No world was generated, so the "
            "per-cell, fit, bootstrap and L-4 tables have no artifact to be generated "
            "from and are absent by the registration's own routing.", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _write_stop_prose_facts(p0: dict[str, Any], diag: dict[str, Any],
                            dec: dict[str, Any]) -> None:
    g1 = p0["G1m"]
    d_ = g1["(d) decollinearization"]
    c = g1["(c) within-share r ratio"]
    pin = diag["infimum_at_registered_shares"]
    fre = diag["best_with_shares_also_freed"]
    lad = diag["ladders"]
    lev = diag["phi_leverage_per_share"]
    facts = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"],
        "N_CELLS": g1["n_cells"], "WORLDS_GENERATED": dec["worlds_generated"],
        "SHARES": list(SHARES), "PHI_BASE": list(PHIS),
        "PHI_LADDER": list(PHIS_LADDER_G1M),
        "PHI_ADOPTED": p0["design"]["phi_ladder_adopted"],
        "CORR_BASE": lad["registered base ladder"]["pearson_corr_r_V"],
        "CORR_LADDER": lad["pre-declared fallback ladder"]["pearson_corr_r_V"],
        "CORR_BASE_ABS": lad["registered base ladder"]["abs_pearson"],
        "CORR_LADDER_ABS": lad["pre-declared fallback ladder"]["abs_pearson"],
        "SPEARMAN_BASE": lad["registered base ladder"]["spearman_corr_r_V"],
        "SPEARMAN_LADDER": lad["pre-declared fallback ladder"]["spearman_corr_r_V"],
        "CORR_RQ_BASE": lad["registered base ladder"]["pearson_corr_r_pow_q_V"],
        "CORR_RQ_LADDER": lad["pre-declared fallback ladder"]["pearson_corr_r_pow_q_V"],
        "CORR_RV_K2F": K2F_CORR_RV, "CORR_BAR": G1M_CORR_MAX,
        "MULT_BASE": float(lad["registered base ladder"]["abs_pearson"] / G1M_CORR_MAX),
        "MULT_LADDER": float(lad["pre-declared fallback ladder"]["abs_pearson"]
                             / G1M_CORR_MAX),
        "INF_CORR": pin["inf_abs_corr"], "INF_MULT": pin["multiple_of_bar"],
        "INF_PHI": pin["argmin_phi_ladder"],
        "FREE_CORR": fre["best_abs_corr_found"], "FREE_MULT": fre["multiple_of_bar"],
        "FREE_SHARES": fre["shares"], "FREE_V_RATIO": fre["V_ratio"],
        "FREE_PHI": fre["phi_ladder"],
        "V_RATIO": g1["(b) V ratio"]["ratio"], "V_RATIO_BAR": G1M_V_RATIO_MIN,
        "V_MIN": g1["(b) V ratio"]["V_min"], "V_MAX": g1["(b) V ratio"]["V_max"],
        "PCT_030": float(100 * (ANCHORS["r_030_090"] - ANCHORS["r_030_098"])
                         / ANCHORS["r_030_098"]),
        "SHARES_CANNOT_MEET_C": [x["share"] for x in lev
                                 if not x["reaches_G1m_c_bar_anywhere"]],
        "V_OVER_SHARE": diag["V_is_exactly_linear_in_share"]["V_over_share_values"][0],
        "C_LEVELS_BASE": g1["base_ladder_result"]["(c) within-share r ratio"][
            "levels_meeting_bar"],
        "C_LEVELS_LADDER": c["levels_meeting_bar"],
        "C_BAR": G1M_R_RATIO_MIN, "C_LEVELS_REQUIRED": G1M_R_RATIO_MIN_LEVELS,
        "R_RATIOS_LADDER": [x["ratio"] for x in c["per_share"]],
        "PHI_MAX_SPAN": max(x["max_span_over_full_phi_interval"] for x in lev),
        "PHI_MAX_SPAN_SHARE": max(
            lev, key=lambda x: x["max_span_over_full_phi_interval"])["share"],
        "PHI_MIN_SPAN": min(x["max_span_over_full_phi_interval"] for x in lev),
        "PHI_MIN_SPAN_SHARE": min(
            lev, key=lambda x: x["max_span_over_full_phi_interval"])["share"],
        "N_SHARES_CAN_EVER_MEET_C": sum(1 for x in lev
                                        if x["reaches_G1m_c_bar_anywhere"]),
        "BETWEEN_SPAN": diag["between_share_r_span_at_phi_0.90"],
        "MECHANISM": diag["mechanism"], "DEFECT_CLASS": diag["defect_class"],
        "GOT_RIGHT": diag["what_the_registration_got_right"],
        "N_DIAG_DRAWS": DIAG_RANDOM_DRAWS,
        "N_DIAG_REJECTED": fre["n_draws_rejected_by_gate_b"],
        "PHI_GRID_N": DIAG_PHI_N,
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
        "PART0_SECONDS": p0["seconds"], "DIAG_SECONDS": diag["seconds"],
        "N_WORLDS_PLANNED": p0["design"]["n_worlds_total"],
    }
    write_json(OUT / "prose_facts.json", facts)


# ---------------------------------------------------------------------------
# REPORT rendering (rule 24: no number in this report is hand-typed).

REPORT_TEMPLATE = """# M4-M1 — r-at-level on a decollinearized factorial

**Leg:** M4-M1 · **Registered** 2026-08-11 in
`docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md` (section "M4-M1 — r-at-level on a
decollinearized factorial"), commit `140e927`, BEFORE this run.
**Executor:** dispatched agent (implementation and execution only; the
registration text is binding).
**Harness:** `scripts/run_suica_m4_m1_r_at_level.py`.
**Artifacts:** `results/m4_m1_r_at_level/` (gitignored).
**Banner:** synthetic worlds on K2b's frozen instrument, exploratory, label-free;
a share × φ factorial that sets out to break K2f's −0.964 r/V collinearity.

**Verdict: `{{SLUG}}` (rule-16 cell {{CELL}}).** {{ROUTING_TEXT}}

**{{WORLDS_GENERATED}} worlds were generated.** The leg stopped inside Part 0,
before the pilot, on the registration's own pre-declared ladder.

K2f left one question: the level law's intercept might hide `λ·r^q`, but its 26
rows could not say, because `corr(r, V) = {{CORR_RV_K2F}}`. M1's design answer
was a share × φ factorial — φ moves `r` at exactly fixed `V`, since
`person_share_design` has no φ argument. That premise is **true and verified
here**. What fails is its magnitude. On the registered grid the factorial moves
the collinearity only from `{{CORR_RV_K2F}}` to `{{CORR_BASE}}`; after the
pre-declared one-step φ extension it reaches `{{CORR_LADDER}}`. Gate G1m(d)
demands `|corr(r, V)| ≤ {{CORR_BAR}}`. The realized value is
**{{MULT_LADDER}}× the bar**, and the diagnostic below shows the bar is not
merely missed but **unreachable**: over *every* 5-point φ ladder at the
registered shares the infimum of `|corr(r, V)|` is `{{INF_CORR}}` —
**{{INF_MULT}}× the bar**. No φ schedule exists that satisfies the gate the
registration wrote.

Per the registration, that routes to cell 1 and the planner owns the defect.
No pilot ran; no fit ran; no lean was evaluated.

---

## Part 0 — written before any world

Part 0 was computed and persisted (`results/m4_m1_r_at_level/part0.json`,
`part0_tables.md`) before a single world could exist; the world-building entry
points are wrapped by a permit gate that Part 0 never opened.

### 0.1 Rule 9 / rule 12 — open conventions, pinned in writing

<<TABLE:rn>>

RN-M1-8 was added **after** G1m failed and **before** any world existed — zero
worlds were generated in this leg, so no hypothesis-relevant number existed at
any point in its authorship. It adopts nothing; it measures the defect.

### 0.2 G0m — the anchors, bit-exact

Every anchor and **every K2f, D-open and theory-document number the
registration quotes** re-derives bit-exactly. There is no citation defect: the
registration's facts are accurate, and the design premise they support is real.

<<TABLE:g0m>>

The correlation convention is pinned by this table, not asserted: Pearson
reproduces K2f's quoted `{{CORR_RV_K2F}}` from `compiled_rows.csv` bit-exactly
(RN-M1-4), which is what licenses reading gate (d)'s "corr" as Pearson.

### 0.3 G1m — the realized {{N_CELLS}}-point design

Shares `{{SHARES}}` × φ `{{PHI_ADOPTED}}` (the ladder after the pre-declared
extension). `r` from `predicted_attenuation`
(`scripts/run_suica_m4_k2c_matched_pairs.py:186-191` → `k2b:533-583`);
`V_person` from `person_share_design`
(`scripts/run_suica_m4_k2e_double_matching.py:234-241` → `k2b.arm_shares`),
never assumed linear.

<<TABLE:design>>

### 0.4 The gates — four pass, one fails

<<TABLE:g1m>>

Gate (c) is the near miss that the ladder repaired. On the **registered base**
ladder only **{{C_LEVELS_BASE}}** of 4 share levels reached the
`{{C_BAR}}` within-share `r` ratio, against a requirement of
**{{C_LEVELS_REQUIRED}}**; the pre-declared extension to `{{PHI_LADDER}}`
lifted that to **{{C_LEVELS_LADDER}}**, realized ratios
`{{R_RATIOS_LADDER}}`. So the fallback ladder did exactly the job it was
written for — and gate (d) still fails behind it.

<<TABLE:leverage>>

### 0.5 Gate (d) — the failure, under both correlation conventions

<<TABLE:ladders>>

Pearson `{{CORR_LADDER}}`, Spearman `{{SPEARMAN_LADDER}}`, and
`corr(r^q, V)` at the sealed response exponent `{{CORR_RQ_LADDER}}`: the
failure is not an artifact of the convention. The registration's own headline
comparison — M1's number "against K2f's `{{CORR_RV_K2F}}`" — is the right
comparison, and it shows the factorial buying a reduction of
`{{CORR_RV_K2F}}` → `{{CORR_LADDER}}` where the gate needed
`{{CORR_BAR}}`.

---

## The satisfiability diagnostic (RN-M1-8) — how far from satisfiable

Cell 1 obliges a STOP, not a repair. To make the handoff actionable, the
`diagnose` stage measures *how* unsatisfiable gate (d) is. This is pure design
arithmetic on the pinned deterministic maps: no world, no field, no fit.

<<TABLE:satisfiability>>

**At the registered shares, gate (d) is unsatisfiable by construction.** The
infimum of `|corr(r, V)|` over every 5-point distinct φ ladder in
`(0.001, 0.999)` is `{{INF_CORR}}` = **{{INF_MULT}}× the bar**, attained at the
degenerate ladder `{{INF_PHI}}` — three points crushed against one end of the φ
interval and two against the other, i.e. the most extreme φ leverage the family
can produce. Freeing the shares as well, inside gate (a)'s envelope and subject
to gate (b)'s `V max/min ≥ {{V_RATIO_BAR}}`, the best of
{{N_DIAG_DRAWS}} seeded draws ({{N_DIAG_REJECTED}} rejected by gate (b)) is
`{{FREE_CORR}}` = **{{FREE_MULT}}× the bar** — an upper bound on that infimum,
already above it.

### Why: φ's ceiling against share's floor

<<TABLE:phi_ceiling>>

{{MECHANISM}}

Two consequences worth naming separately. First, gate (c)'s `{{C_BAR}}` bar is
reachable in only **{{N_SHARES_CAN_EVER_MEET_C}} of the 4 registered share
levels for any φ ladder whatsoever** — at shares
`{{SHARES_CANNOT_MEET_C}}` the full open φ interval cannot produce a
`{{C_BAR}}` ratio — so the registration's "at least
{{C_LEVELS_REQUIRED}} share levels" was, unknowingly, demanding *all* of the
levels that can ever comply. Second, gate (b) and gate (d) pull on the same
knob in opposite directions: (b) needs a wide share range so `V` varies, and a
wide share range is exactly what makes `r` track `V`.

<<TABLE:argmin>>

---

## What was not run, and why

The registration's cell 1 reads "no fit is run", and the ordering discipline
puts the pilot after the Part-0 gates. Accordingly:

- **G2m (the 16-world pilot): not reached.** No liveness measurement, no
  `σ_w`, no per-world field value exists for this leg.
- **G3m(b) (the power projection): not reached** — it needs pilot `σ_w`.
- **The {{N_WORLDS_PLANNED}} main worlds: not generated.** The permit gate was
  never opened; `ordering_log.jsonl` records the refusal path unused because
  the leg stopped before arming.
- **The fit: not run.** No winner form, no bootstrap CI, no LOO-RMSE.

The report therefore carries **no per-cell results table, no fit table, no
bootstrap CIs and no L-4 residual pattern** — those tables have no artifact to
be generated from, and rule 24 forbids typing them. The four pre-declared forms
and the optimizer pins were nevertheless fixed in Part 0 before the stop, and
are recorded here so the next registration inherits them unchanged:

<<TABLE:forms>>

<<TABLE:optimizer>>

---

## Routing — the rule-16 truth table, reproduced verbatim

<<TABLE:truth_table>>

The L-3 modifier row is defined only for cells 2-6 and therefore does not
apply. The enumeration is the registration's own; cell 1 is the cell this leg
lands in, and it is reached through the gate ladder rather than through any
lean.

## Leans

<<TABLE:verdicts>>

## Sides declared in Part 0 (rule 22)

<<TABLE:sides>>

## Gates

<<TABLE:gates>>

---

## Anomaly log — every anomaly, with pre/post-hypothesis timing

**No hypothesis-relevant number ever existed in this leg: {{WORLDS_GENERATED}}
worlds were generated and no fit was run.** Every anomaly below is therefore
*pre-hypothesis* by construction, and each is stated with the point in the run
at which it was resolved.

- **A-1 — the interpreter did not exist (resolved BEFORE Part 0, i.e. before
  any number of any kind).** The dispatch said a working interpreter with
  pandas/scipy/numpy/pytest was present. It was not: the only pandas on this
  machine belongs to `/usr/bin/python3` (CPython 3.9.6), and the published
  machinery imports `datetime.UTC`, which is 3.11+. `k2b`, `k2c`, `k2d`, `k2e`
  and the K2f harness all fail to import there. A CPython {{PYTHON}} virtual
  environment was built outside the repository and populated from
  `requirements-lock-main.txt` verbatim, reproducing the lock exactly
  (numpy `{{NUMPY}}`, pandas `{{PANDAS}}`, scipy `{{SCIPY}}` — the same pins the
  lock records for the environment that passed the 970-test suite). Platform
  `{{PLATFORM}}`. The suite was run on it BEFORE any leg code was written, as a
  baseline.
- **A-2 — `timeout(1)` is absent on this platform (resolved before Part 0).**
  The execution convention requires explicit per-stage timeouts. macOS ships no
  `timeout`; every stage was instead run as its own foreground command under an
  explicit harness-level timeout, all well under the 600 s ceiling.
- **A-3 — G1m failed on the base ladder (Part 0, before the pilot).** Gates (c)
  and (d) both failed; the pre-declared rule-17 ladder fired automatically
  inside `part0`, repaired (c), and left (d) failing. This is the leg's outcome,
  not an incident, and it is recorded here because the ladder firing is itself a
  reportable event.
- **A-4 — Part 0 was executed more than once (every run before any world).**
  The first run produced the STOP; the `diagnose` stage and RN-M1-8 were then
  added to the harness, and `part0` was re-run so the persisted artifact matches
  the committed script. `ordering_log.jsonl` was reset once before the final
  clean pass so the log it carries is the run that produced the committed
  artifacts, end to end; the earlier runs are therefore not in it, and this note
  is the record of them. The arithmetic is deterministic and identical across
  every run — `corr(r, V)` was `{{CORR_LADDER}}` each time — and no world
  existed during any of them.
- **A-5 — an exploratory diagnostic overran and was killed (before the
  `diagnose` stage was written).** A first, unbatched search called
  `predicted_attenuation` inside an optimizer loop and exceeded its foreground
  timeout; it was killed and rewritten to precompute `r` on a fixed
  {{PHI_GRID_N}}-point φ grid, which runs in `{{DIAG_SECONDS}}` s. No number
  from the killed run appears anywhere in this leg; the committed `diagnose`
  stage is deterministic and reproduces the reported values from scratch.
- **A-6 — rule 24 caught two of this leg's own errors before commit.** (i) The
  diagnostic's prose originally described the registration's cited φ leverage
  at share 0.30 as "a 4.6% move"; recomputed from the anchors it is
  `{{PCT_030}}`%. The string is now generated from the anchor values rather
  than typed. (ii) The within-share leverage table's column headers read "r at
  phi min" / "r at phi max" while the cells carry `r.min()` / `r.max()` — and
  because `r` is monotone DECREASING in φ these are the opposite φ endpoints,
  so the headers were mislabelled (the numbers were right). Both were caught by
  reading the generated table back against the artifact, which is exactly the
  K2f convention doing its job on the executor. A third, `V max/min ≥ 6.0`,
  where 6.0 is the design's REALIZED ratio and the gate's bar is
  `{{V_RATIO_BAR}}`, was caught the same way and is now a generated
  placeholder.
- **A-7 — no stage approached its 2× stop-and-report threshold.** Part 0 ran in
  `{{PART0_SECONDS}}` s against a 60 s estimate; `diagnose` in
  `{{DIAG_SECONDS}}` s against a 120 s executor estimate.

<<TABLE:timing>>

<<TABLE:env>>

---

## What the planner should carry forward

**The defect.** {{DEFECT_CLASS}}

**What the registration got right, and it matters.** {{GOT_RIGHT}} The M1
mechanism section is not wrong about the physics of the design — φ really does
move `r` at exactly fixed `V`, and G0m confirms every number it cites. The
registration's error is that it never converted its own cited φ leverage into
the correlation the gate would see.

**What this rules out.** Any share × φ factorial in this world family, at the
registered shares, cannot decollinearize `r` from `V` to `{{CORR_BAR}}` — the
floor is `{{INF_CORR}}`. Widening φ does not help: the infimum above already
uses the whole open interval. Re-choosing shares inside the trained envelope
does not rescue it either while gate (b) stands, since the best reachable value
found is `{{FREE_CORR}}`.

**Where the leverage would have to come from.** `V` is an exact linear function
of share in this family (`V/share = {{V_OVER_SHARE}}`), so as long as the only
two knobs are share and φ, `V` is share and the design has one effective axis
plus a weak second. Decollinearizing `r` from `V` at level needs a knob that
moves `r` *without* moving share — or a `V` that is not a function of share
alone. The `int_share` carrier that M1 pinned to zero (inheriting K2F-FRESH) is
the obvious candidate: `person_share_design(share, int_share)` sums the slow and
interaction shares, so a non-zero interaction carrier moves `V` at fixed share,
which is a second axis in exactly the place the current design has none. That is
a re-registration question, not an executor's choice, and nothing here adopts
it.

**Also worth re-registering with the bar.** Gate (c)'s
`{{C_BAR}}` within-share ratio is reachable in only
{{N_SHARES_CAN_EVER_MEET_C}} of the 4 registered share levels for any φ
whatsoever, and gate (d)'s bar is unreachable at any. Both bars want a
generator-derived feasibility argument (rule 17) or an arithmetic satisfiability
check (rule 11) computed jointly (rule 18) before the next registration is
committed — which is precisely the arithmetic this leg's Part 0 performs in
`{{PART0_SECONDS}}` s.
"""


def stage_report(args: argparse.Namespace) -> None:
    facts = read_json(OUT / "prose_facts.json")
    tables_raw = (OUT / "report_tables.md").read_text(encoding="utf-8")
    tables: dict[str, str] = {}
    cur: str | None = None
    buf: list[str] = []
    for line in tables_raw.split("\n"):
        if line.startswith("<!-- TABLE:"):
            if cur is not None:
                tables[cur] = "\n".join(buf).strip("\n")
            cur = line[len("<!-- TABLE:"):].split(" ")[0].rstrip("-->").strip()
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
    missing = [tok for tok in ("{{", "<<TABLE:") if tok in text]
    if missing:
        bad = [ln for ln in text.split("\n") if any(m in ln for m in missing)]
        raise SystemExit(f"REFUSED: unresolved placeholders: {bad[:5]}")
    path = ROOT / "reports" / "SUICA_M4_M1_R_AT_LEVEL_REPORT.md"
    path.write_text(text, encoding="utf-8")
    print(f"report OK  {rel(path)}  ({len(text.splitlines())} lines)")
    _ = args


def _fmt(v: Any) -> str:
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        return repr(v)
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(_fmt(x) for x in v) + "]"
    if isinstance(v, dict):
        return ", ".join(f"{k} {_fmt(x)}" for k, x in v.items())
    return str(v)


# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="stage", required=True)
    stages: list[tuple[str, Callable[[argparse.Namespace], None]]] = [
        ("part0", stage_part0), ("pilot", stage_pilot), ("power", stage_power),
        ("worlds_a", lambda a: _worlds_chunk("a")),
        ("worlds_b", lambda a: _worlds_chunk("b")),
        ("worlds_c", lambda a: _worlds_chunk("c")),
        ("worlds_d", lambda a: _worlds_chunk("d")),
        ("fit", stage_fit), ("rule13", stage_rule13), ("finalize", stage_finalize),
        ("diagnose", stage_diagnose), ("report", stage_report),
    ]
    for name, fn in stages:
        s = sub.add_parser(name)
        s.set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
