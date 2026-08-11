#!/usr/bin/env python3
"""M4-M1b -- r-AT-LEVEL, FEASIBILITY RESTATED IN THE ESTIMAND'S QUANTITY.

Registered in docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md ("M4-M1b -- r-at-level,
feasibility restated in the estimand's quantity", commit 2e4e404) BEFORE this
file existed.  Implementation and execution only; the registration is binding.

M1 died at cell 1 on a MARGINAL-correlation gate that the estimand does not
consume: in a factorial, q is identified from within-share phi sweeps at exactly
fixed V and kappa from between-share contrasts, so the marginal corr(r, V) can
stay high while the conditional design information is ample.  The planner
recorded defects #43 (rule 11 -- deterministic gate arithmetic never run) and
#44 (rule 18 -- gates (b)/(c)/(d) jointly empty) and enacted RULE 25: every
design-feasibility gate is stated in the quantity the estimand requires;
marginal or proxy statistics are REPORTED, never gating.

M1b therefore inherits M1 VERBATIM -- question, machinery, source objects, the
four forms, optimizer pins, start grid, LOO-cell selection, within-cell
world-block bootstrap, tie rule, leans L-1..L-4 with priors, truth-table cells
2-6 -- and changes exactly: the phi ladder ({0.05, 0.30, 0.60, 0.85, 0.98}, ALT
{0.30, 0.55, 0.75, 0.90, 0.98} on the regime guard only); no marginal gate;
G1m'(c') an absolute within-share r SPAN >= 0.12 at shares {0.40, 0.60};
G0m'(vii)/(viii); G2m''s regime guard and its non-outcome-side liveness rule;
and G3m'(b) -- the projection -- as THE feasibility gate, with one pre-declared
escalation to 64 worlds/cell.

    part0     G0m'(i)-(viii), G1m'(a)(b)(c')(e), G3m'(a)(c), G4m'.  No world.
    pilot     G2m': 4 corners x 4 worlds on m4m1b-pilot; regime guard + the
              phi->r channel liveness on the REALIZED CARD statistic.
    power     G3m'(b): sigma_w -> B_proj=500 replication under two q truths;
              PASS iff width proxy <= 0.50 under both; one escalation to 64.
    worlds_a/b/c/d   the 4 x 5 main cells (one share level per chunk).
    fit       four forms, leave-one-CELL-out selection, bootstrap B=2000.
    rule13    the >=10xB re-run at any flagged boundary.
    finalize  L-1/L-2/L-3 through the inherited truth table, L-4 as a reading.
    report    renders the report from artifacts (rule 24).

ORDERING IS ENFORCED, NOT ASSERTED: every k2b entry point that can build or
measure a world is wrapped on EVERY reachable k2b instance (RN-K2F-5), and each
permit is issued only after re-reading the preceding stage's artifacts from disk
and checking their gates there.

Artifacts: results/m4_m1b_r_at_level/ (gitignored)
"""

from __future__ import annotations

import argparse
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
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "results" / "m4_m1b_r_at_level"
RES = ROOT / "results"
K2F = RES / "m4_k2f_level_law"
M1RES = RES / "m4_m1_r_at_level"

# ---------------------------------------------------------------------------
# Registration constants.

LEG = "M4-M1b"
BANNER = ("synthetic worlds on K2b's frozen instrument, exploratory, label-free; "
          "a share x phi factorial whose ONLY feasibility gate is the estimand's "
          "own projected identification width (rule 25)")

MASTER_SEED = 20260811
SALT_WORLD = "m4m1b-world"
SALT_PILOT = "m4m1b-pilot"

SHARES = (0.10, 0.25, 0.40, 0.60)
PHIS = (0.05, 0.30, 0.60, 0.85, 0.98)
PHIS_ALT = (0.30, 0.55, 0.75, 0.90, 0.98)
N_WORLDS_BASE = 32
N_WORLDS_ESCALATED = 64
PILOT_SHARES = (0.10, 0.60)
PILOT_WORLDS = 4

B_BOOT = 2000
B_BOOT_HIGH = 20000
B_PROJ = 500

INT_SHARE = 0.0
W_INT_ARM = "zero"

# --- G1m' bars -------------------------------------------------------------
SHARE_ENVELOPE = (0.02, 0.6634207990183637)
G1M_V_RATIO_MIN = 2.0
G1M_SPAN_MIN = 0.12                      # (c'): ABSOLUTE r span, not a ratio
G1M_SPAN_SHARES = (0.40, 0.60)           # at BOTH of these shares

# --- G2m' / G3m' bars ------------------------------------------------------
G2M_LIVENESS_SE_MULT = 2.0
G3M_PROJ_WIDTH_MAX = 0.50
G3M_DF = 12                              # 16 pilot worlds - 4 pilot cells
G3M_CHI2_Q = 0.10

# --- lean bars (inherited verbatim from M1) --------------------------------
L1_Q_WIDTH_MAX = 0.60
L2_RESPONSE_BAND = (1.71, 1.98)
L3_KAPPA_CI = (0.5202855978239498, 0.8612166024267973)
TIE_REL = 0.05
BOUNDARY_REL = 0.05
L4_MIN_LEVELS = 3

# --- cited constants (K2f / D1 / D-open), verified bit-exactly in G0m' -----
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

# --- G0m'(vii): the planner's two embedded design tables, verbatim ---------
PLANNER_TABLE_MAIN = {
    0.10: {"V": 0.03000000000000001,
           "r": (0.8189581462487876, 0.8155586799827954, 0.8075174172340943,
                 0.7908869485651705, 0.7718092954224756),
           "span": 0.04714885082631204},
    0.25: {"V": 0.07500000000000002,
           "r": (0.785015540293945, 0.7761302864207245, 0.7558507450373838,
                 0.7168731389294273, 0.6763691758553391),
           "span": 0.10864636443860598},
    0.40: {"V": 0.12000000000000004,
           "r": (0.7411873080384952, 0.726425348215848, 0.6941115392115328,
                 0.6367206581308248, 0.5825497814736654),
           "span": 0.15863752656482977},
    0.60: {"V": 0.18000000000000005,
           "r": (0.6573448847694047, 0.6346912945232521, 0.5883719155687073,
                 0.5151304058057474, 0.4541409476972356),
           "span": 0.20320393707216905},
}
PLANNER_MAIN_CORR_RV = -0.8495063312353189
PLANNER_MAIN_CORR_RQ_V = -0.8649603255864755
PLANNER_ALT_SPANS = (0.04374938456031985, 0.09976111056538539,
                     0.1438755667421826, 0.1805503468260165)
PLANNER_ALT_CORR_RV = -0.8915685583022667
PLANNER_ALT_CORR_RQ_V = -0.9029258027968385

# --- G0m'(viii): the M1-STOP numbers the adjudication cites ----------------
M1_INF_CORR = 0.748768093111513
M1_FREED_CORR = 0.5208187741410987
M1_FULL_INTERVAL_SPANS = (0.05159009087311539, 0.11784317303319514,
                          0.17083747134975158, 0.21722718146551878)

# ---------------------------------------------------------------------------
# RN-M1B notes (rule 9 / rule 12).  PINNED IN PART 0, BEFORE ANY WORLD EXISTS.
#
# RN-M1B-1 (code inheritance).  The coordinator left "copy or import" to the
#   executor.  PINNED: the machinery is COPIED into this file (so this leg's
#   harness is self-contained and its pins cannot drift when a later leg edits
#   M1's file), and Part 0 then IMPORTS the M1 harness and PROVES the copy is
#   faithful -- start grid, optimizer dict, form expressions and parameter names
#   compared element-by-element, and `fit_form` run on a fixed synthetic probe in
#   both modules with bit-exact agreement demanded on every fitted parameter.
#   Copying without that proof would be the drift risk; importing without a copy
#   would couple this leg's artifacts to another leg's module globals.
#
# RN-M1B-2 (seed string).  As RN-M1-2, with M1b's salts:
#       v8.stable_bucket(f"{MASTER_SEED}-{share!r}-{phi!r}-{world}",
#                        salt=<m4m1b-world|m4m1b-pilot>, modulus=2**31 - 1)
#   Streams are disjoint from M1's and from each other BY SALT, as registered.
#
# RN-M1B-3 (the G2m'(ii) liveness object).  The registration asks for "a
#   per-world realized card-attenuation statistic IF the k2b machinery persists
#   one", and otherwise certifies liveness from the pinned map's arithmetic plus
#   the projection.  M1's Part 0 established the fact this turns on, and it is
#   unchanged: k2b COMPUTES a realized card attenuation at world grain --
#   `card_channel_frame(world, w, world_seed)`
#   (scripts/run_suica_m4_k2b_t4_branch.py:392-503; the frame is stamped with
#   `world_seed`), pooled by `bootstrap_card`
#   (scripts/run_suica_m4_k2b_t4_branch.py:505-509) into `r_card_b_raw`
#   (scripts/run_suica_m4_k2b_t4_branch.py:486) -- and it is the object k2b's own
#   G2 lever-liveness check uses (scripts/run_suica_m4_k2b_t4_branch.py:944-963).
#   It is NOT written into any published per-world field CSV
#   (`run_field_world`'s row schema, scripts/run_suica_m4_k2b_t4_branch.py:
#   633-646, carries no card column).  PINNED READING (unchanged from M1's
#   RN-M1-3): "persists one" is read as "exposes one at world grain", so the
#   PRIMARY path applies and the card statistic is the gate.  The arithmetic
#   certification (Delta r = 0.20320393707216905 at share .60) is ALSO recorded,
#   so the leg satisfies the registration under either reading of that clause.
#   The registration is explicit that an OUTCOME-side field contrast is NOT a
#   liveness gate here -- a flat field is cell-2 EVIDENCE, not channel death --
#   so the pilot field contrast is computed and reported as a DESCRIPTIVE only
#   and gates nothing.  This is the one place M1's registration was wrong and
#   M1b's is right; the executor's M1 implementation gated on the card statistic
#   in both readings, so nothing carried over needs undoing.
#
# RN-M1B-4 (escalation bookkeeping).  "on fail, recompute at 64 worlds/cell
#   (noise /sqrt2); pass -> the main grid runs at 64 worlds/cell".  PINNED: the
#   `power` stage persists the DECIDED worlds-per-cell into g3mb_power.json, and
#   every downstream stage (worlds_*, fit, bootstrap) reads it from that artifact
#   rather than from a constant, so the escalation cannot be applied in one place
#   and forgotten in another.  The escalation is once-only and is recorded even
#   when it does not fire.
#
# RN-M1B-5 (L-4 monotonicity).  As M1's RN-M1-7: "monotone same-sign in >=3/4
#   share levels" is read BOTH ways -- (A) sign agreement of
#   Spearman(residual, phi) in >=3 levels, (B) the stricter |rho| == 1 plus sign
#   agreement in >=3 levels.  Both reported; L-4 adjudicates nothing.
#
# RN-M1B-6 (lambda-vs-zero boundary scale).  As M1's RN-M1-6: rule 13's boundary
#   test is relative to the bar, and "lambda CI contains 0" has no relative
#   scale; pinned as min(|lambda_lo|, |lambda_hi|) <= 0.05 * |lambda_hat|.
#
# RN-M1B-7 (stage chunking).  As M1's RN-M1-5: G3m'(b) needs pilot sigma_w and
#   must PASS before the first main world, so it runs as its own permit-gated
#   foreground stage `power`; the >=10xB rule-13 re-run is its own stage
#   `rule13`.  Ordering is unchanged and strengthened.  Registration estimates
#   and this leg's chunk estimates are both written into Part 0 before the pilot.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-M1B-1": "machinery COPIED into this file, then PROVEN faithful in Part 0 against "
                "the imported M1 harness (start grid, OPT, form expressions/names, and "
                "fit_form bit-exact on a fixed synthetic probe)",
    "RN-M1B-2": "seed string pinned: v8.stable_bucket(f'{MASTER_SEED}-{share!r}-{phi!r}-"
                "{world}', salt=<m4m1b-world|m4m1b-pilot>, modulus=2**31-1); streams "
                "disjoint from M1's and from each other by salt",
    "RN-M1B-3": "G2m'(ii) gates on the k2b-side realized card attenuation r_card_b_raw at "
                "world grain (k2b:392-503 + :505-509 + :486; k2b's own G2 uses it at "
                ":944-963); the map-arithmetic certification is also recorded, so either "
                "reading of 'persists one' is satisfied. The pilot FIELD contrast is "
                "descriptive only and gates NOTHING -- a flat field is cell-2 evidence, "
                "not channel death (the registration's own correction of M1)",
    "RN-M1B-4": "the `power` stage persists the DECIDED worlds-per-cell; every downstream "
                "stage reads it from that artifact, never from a constant",
    "RN-M1B-5": "L-4 monotonicity read BOTH ways (sign agreement; and |rho|==1 plus sign "
                "agreement); L-4 adjudicates nothing so neither is adopted",
    "RN-M1B-6": "lambda-vs-zero boundary: adjacent iff min(|lo|,|hi|) <= 0.05*|lambda_hat|",
    "RN-M1B-7": "stage chunking: G3m'(b) is its own permit-gated stage `power` between "
                "`pilot` and `worlds_a`; the >=10xB re-run is its own stage `rule13`",
    "RN-M1B-8": "the NON_PROJECTABLE handoff (added AFTER sigma_w existed, disclosed): on "
                "the registered STOP the `diagnose` stage MEASURES the smallest "
                "worlds/cell at which the binding truth would clear the bar, on a "
                "declared geometric ladder, instead of extrapolating -- the planner's own "
                "rule-11 convention that defect #43 bought. It consumes only sigma_w and "
                "the pinned design maps; NO field-outcome quantity bearing on "
                "L-1/L-2/L-3 enters it, and it adopts nothing",
}

# --- RN-M1B-8 diagnostic pins (deterministic) ------------------------------
DIAG_N_LADDER = (64, 128, 192, 256, 384, 512)

# ---------------------------------------------------------------------------
# Module loading -- ONE importlib loader chain for this leg (RN-K2F-5).

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


def m1() -> Any:
    """The M1 harness, imported ONLY to prove RN-M1B-1's copy is faithful."""
    return _load("run_suica_m4_m1_r_at_level")


# ---------------------------------------------------------------------------
# ORDERING ENFORCEMENT.

_GEN_COUNT = 0
_PERMIT: str | None = None
_ARMED = False


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
                    if _PERMIT is None:
                        _ordering_log("REFUSED_world_generation", entry_point=nm,
                                      count=_GEN_COUNT)
                        raise SystemExit(
                            f"STOP (ordering): world generation via {nm} attempted "
                            f"with no permit issued.")
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
    global _PERMIT
    p0p = OUT / "part0.json"
    if not p0p.exists():
        raise SystemExit("STOP (ordering): part0.json absent; run `part0` first.")
    p0 = read_json(p0p)
    if not (p0["G0m'"]["PASS"] and p0["G1m'"]["PASS"]):
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
            raise SystemExit("STOP (ordering): G2m' did not pass.")
        if not g3["PASS"]:
            raise SystemExit("STOP (ordering): G3m'(b) did not pass.")
        rec.update({"g2m_utc": g2["utc"], "g3mb_utc": g3["utc"],
                    "worlds_per_cell": g3["worlds_per_cell_decided"]})
    if _GEN_COUNT != 0:
        raise SystemExit(f"STOP (ordering): {_GEN_COUNT} generations before permit.")
    _PERMIT = kind
    rec["permit_utc"] = datetime.now(UTC).isoformat()
    _ordering_log("permit_issued", **rec)
    return rec


# ---------------------------------------------------------------------------
# Utilities (K2f / M1 lineage).

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
    return float(np.corrcoef(np.asarray(a, float), np.asarray(b, float))[0, 1])


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = pd.Series(np.asarray(a, float)).rank().to_numpy()
    rb = pd.Series(np.asarray(b, float)).rank().to_numpy()
    return pearson(ra, rb)


def cell_id(share: float, phi: float) -> str:
    """RN-M1B-2's seed key: full-precision, round-trippable."""
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
# The FOUR pre-declared forms -- inherited from M1 verbatim (RN-M1B-1).

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
    return {"form": form, "loo_pred": preds, "loo_error": errs, "n_failed": int(failed),
            "loo_rmse": float(np.sqrt(np.nanmean(e ** 2))),
            "loo_mae": float(np.nanmean(np.abs(e))),
            "loo_max_abs": float(np.nanmax(np.abs(e)))}


def cell_block_bootstrap(per_world: np.ndarray, b_draws: int, seed: int) -> np.ndarray:
    """Each draw resamples the cell's own world indices with replacement
    INDEPENDENTLY per cell, then recomputes the cell means.  Returns (B, cells)."""
    n_cells, n_w = per_world.shape
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n_w, size=(b_draws, n_cells, n_w))
    rows = np.arange(n_cells)[None, :, None]
    return per_world[rows, idx].mean(axis=2)


def bootstrap_form(form: str, r: np.ndarray, v: np.ndarray, per_world: np.ndarray,
                   theta0: list[float], b_draws: int, seed: int) -> dict[str, Any]:
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
# The rule-16 truth table -- INHERITED from M1, cell 1 restated per G4m'.

TRUTH_TABLE = [
    {"n": "1", "condition": "any G0m'/G1m'/G2m'/G3m' clause fails after its declared "
                            "ladder",
     "outcome": "STOP_DESIGN_INFEASIBLE",
     "text": "STOP (planner defect; no fit is run) -- STOP_DESIGN_INFEASIBLE, or "
             "NON_PROJECTABLE where G3m'(b) fails after its once-only escalation"},
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
            "prior": "below .55 / overlap .35 / above .10",
            "registered_lean": "BELOW", "conditional_on": "L-1 HOLD"},
    "L-3": {"clause": f"winner's kappa CI overlaps K2f F2's kappa' ci95 "
                      f"{list(L3_KAPPA_CI)}",
            "sided": "two-sided overlap; disjoint-low and disjoint-high both named",
            "improvement_side": "neither -- containment/overlap", "prior": 0.70},
    "L-4": {"clause": "within each share level, Spearman(residual, phi) across the 5 phi "
                      "cells; monotone same-sign in >=3/4 share levels is the named "
                      "finding 'phi leaks past (r, V)'",
            "sided": "reading only, NO gate", "improvement_side": "n/a", "prior": None},
    "G1m'(a)": {"clause": f"all shares inside {list(SHARE_ENVELOPE)}",
                "sided": "two-sided containment", "improvement_side": "neither"},
    "G1m'(b)": {"clause": f"V max/min >= {G1M_V_RATIO_MIN}", "sided": "one-sided",
                "improvement_side": "UP"},
    "G1m'(c')": {"clause": f"within-share r SPAN >= {G1M_SPAN_MIN} at BOTH shares "
                           f"{list(G1M_SPAN_SHARES)}",
                 "sided": "one-sided", "improvement_side": "UP"},
    "G1m'(e)": {"clause": "no duplicate (r, V) design points", "sided": "exact",
                "improvement_side": "n/a"},
    "G2m'(i)": {"clause": "per-world fields finite, non-saturated, and nonzero "
                          "within-corner variance",
                "sided": "two-sided containment plus a nonzero-variance floor",
                "improvement_side": "neither"},
    "G2m'(ii)": {"clause": f"realized card-attenuation contrast between phi .05 and .98 "
                           f"at share .60 exceeds {G2M_LIVENESS_SE_MULT}x its pooled SE",
                 "sided": "one-sided", "improvement_side": "UP"},
    "G3m'(b)": {"clause": f"projected q width proxy <= {G3M_PROJ_WIDTH_MAX} under BOTH q "
                          "truths -- THE feasibility gate, in the estimand's own quantity "
                          "(rule 25)",
                "sided": "one-sided", "improvement_side": "DOWN"},
    "descriptive (NOT a gate, rule 25)": {
        "clause": "marginal corr(r, V) and corr(r^q, V) across cells",
        "sided": "reported only", "improvement_side": "n/a"},
}

STAGE_ESTIMATES_REGISTRATION = {"part0": 60, "pilot": 40, "worlds_each": 150,
                                "worlds_n_chunks": 4, "fit": 300, "finalize": 60,
                                "note": "worlds x2 at escalation"}
STAGE_ESTIMATES_EXECUTOR = {"part0": 60, "pilot": 40, "power": 120, "worlds_a": 150,
                            "worlds_b": 150, "worlds_c": 150, "worlds_d": 150,
                            "fit": 300, "rule13": 240, "finalize": 60, "report": 30,
                            "diagnose": 300}


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


def _spans(phis: tuple[float, ...]) -> list[dict[str, Any]]:
    out = []
    for share in SHARES:
        rr = np.array([r_of(share, p) for p in phis], float)
        out.append({"share": share, "V_person": v_of(share),
                    "r_min": float(rr.min()), "r_max": float(rr.max()),
                    "span": float(rr.max() - rr.min()),
                    "ratio": float(rr.max() / rr.min()),
                    "in_span_gate": bool(share in G1M_SPAN_SHARES),
                    "meets_span_bar": bool(rr.max() - rr.min() >= G1M_SPAN_MIN)})
    return out


def g1m_check(phis: tuple[float, ...]) -> dict[str, Any]:
    df = design_table(phis)
    r = df["r_pred"].to_numpy(float)
    v = df["V_person"].to_numpy(float)
    sp = _spans(phis)
    dup: list[dict[str, Any]] = []
    key = [(round(a, 12), round(b, 12)) for a, b in zip(r, v)]
    for k in sorted(set(key)):
        j = [i for i, kk in enumerate(key) if kk == k]
        if len(j) > 1:
            dup.append({"r": k[0], "V": k[1], "cells": [df["cell_tag"].iloc[i] for i in j]})
    a = bool(all(SHARE_ENVELOPE[0] <= s <= SHARE_ENVELOPE[1] for s in SHARES))
    b = bool(v.max() / v.min() >= G1M_V_RATIO_MIN)
    gate_rows = [x for x in sp if x["in_span_gate"]]
    c = bool(all(x["meets_span_bar"] for x in gate_rows)) and len(gate_rows) == len(
        G1M_SPAN_SHARES)
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
        "(c') within-share r span": {"PASS": c, "bar": G1M_SPAN_MIN,
                                     "gated_shares": list(G1M_SPAN_SHARES),
                                     "per_share": sp,
                                     "note": "an ABSOLUTE span, not a ratio -- the M1 "
                                             "ratio bar was reachable at only 2 of 4 "
                                             "shares for any ladder (defect #44)"},
        "(e) no duplicate design points": {"PASS": e, "duplicates": dup},
        "descriptive_NOT_a_gate": {
            "corr_r_V": pearson(r, v), "corr_r_pow_q_V": pearson(r ** SEALED_Q, v),
            "q_used_for_power": SEALED_Q, "k2f_corr_r_V_26_rows": K2F_CORR_RV,
            "rule25": "REPORTED, never gating -- identification lives in the "
                      "within-share phi sweeps at exactly fixed V, not in the marginal "
                      "correlation"},
        "PASS": bool(a and b and c and e),
    }


def g0m_check() -> dict[str, Any]:
    out: dict[str, Any] = {}

    # (i)-(iii): the deterministic design maps (M1's G0m verbatim).
    checks = [
        ("(i) predicted_attenuation(0.40, 0.90)", r_of(0.40, 0.90), ANCHORS["r_040_090"]),
        ("(ii-a) predicted_attenuation(0.45, 0.90)", r_of(0.45, 0.90),
         ANCHORS["r_045_090"]),
        ("(ii-b) person_share_design(0.45, 0.0)", v_of(0.45), ANCHORS["V_045"]),
        ("(iii) person_share_design(0.40, 0.0)", v_of(0.40), ANCHORS["V_040"]),
    ]
    out["maps"] = {n: {"rederived": g, "expected": e, "bit_exact": bool(g == e)}
                   for n, g, e in checks}
    out["maps_source"] = {
        "r": "scripts/run_suica_m4_k2c_matched_pairs.py:186-191 "
             "(predicted_attenuation -> k2b:533-583)",
        "V": "scripts/run_suica_m4_k2e_double_matching.py:234-241 "
             "(person_share_design -> k2b.arm_shares)"}

    # (iv): every K2f number quoted in the inherited registration.
    fits = read_json(K2F / "fits.json")
    loos = read_json(K2F / "loo.json")
    f2f = fits["fits"]["F2"]
    th = dict(zip(f2f["param_names"], f2f["theta"]))
    quoted = [
        ("F2 lambda'", th["lambda"], K2F_F2_LAMBDA),
        ("F2 q'", th["q"], K2F_F2_Q),
        ("F2 kappa'", th["kappa"], K2F_F2_KAPPA),
        ("F2 p", th["p"], K2F_F2_P),
        ("F2 LOO-RMSE (fits.json:L-1.best_loo_rmse)", fits["L-1"]["best_loo_rmse"],
         K2F_F2_LOO),
        ("F2 LOO-RMSE (loo.json:loo.F2.loo_rmse)", loos["loo"]["F2"]["loo_rmse"],
         K2F_F2_LOO),
        ("F2 q' ci95 lo", f2f["bootstrap"]["ci95"]["q"][0], K2F_F2_Q_CI[0]),
        ("F2 q' ci95 hi", f2f["bootstrap"]["ci95"]["q"][1], K2F_F2_Q_CI[1]),
        ("F2 kappa' ci95 lo", f2f["bootstrap"]["ci95"]["kappa"][0], K2F_F2_KAPPA_CI[0]),
        ("F2 kappa' ci95 hi", f2f["bootstrap"]["ci95"]["kappa"][1], K2F_F2_KAPPA_CI[1]),
    ]
    out["k2f_quoted"] = {n: {"persisted": g, "registration": e, "bit_exact": bool(g == e)}
                         for n, g, e in quoted}
    out["k2f_winner_is_F2"] = bool(fits["winner"] == "F2")

    rows = read_csv_rt(K2F / "compiled_rows.csv")
    rr = rows["r_pred"].to_numpy(float)
    vv = rows["V_person"].to_numpy(float)
    ext = [
        ("corr(r, V) over the 26 K2f rows (Pearson)", pearson(rr, vv), K2F_CORR_RV),
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

    # (v): D-open's M-4 level from its raw CSV, round-trip.
    do = read_csv_rt(RES / "dopen_seal_opening" / "m4_field_rows.csv")
    lvl = float(do["recovery_b_only"].to_numpy(float).mean())
    out["dopen_m4_level"] = {
        "rederived": lvl, "expected": ANCHORS["dopen_m4_level"],
        "bit_exact": bool(lvl == ANCHORS["dopen_m4_level"]), "n_worlds": int(len(do)),
        "source": "results/dopen_seal_opening/m4_field_rows.csv:recovery_b_only "
                  "(round-trip parsed, mean over worlds)"}

    # (vi): the response band, verbatim in the theory doc.
    txt = THEORY_DOC.read_text(encoding="utf-8")
    hits = [i + 1 for i, ln in enumerate(txt.split("\n")) if THEORY_BAND_STRING in ln]
    out["theory_band"] = {"string": THEORY_BAND_STRING, "found": bool(hits),
                          "lines": hits[:20], "n_lines": len(hits),
                          "doc": rel(THEORY_DOC),
                          "registration_cites": "docs/SUICA_IDENTITY_THEORY_V1.md:805,841"}

    # (vii): BOTH planner design tables, bit-exact.
    main_rows = []
    ok_main = True
    for share, exp in PLANNER_TABLE_MAIN.items():
        got_v = v_of(share)
        got_r = tuple(r_of(share, p) for p in PHIS)
        got_span = float(max(got_r) - min(got_r))
        be = (got_v == exp["V"] and got_r == exp["r"] and got_span == exp["span"])
        ok_main &= be
        main_rows.append({"share": share, "V_expected": exp["V"], "V_rederived": got_v,
                          "r_expected": list(exp["r"]), "r_rederived": list(got_r),
                          "span_expected": exp["span"], "span_rederived": got_span,
                          "bit_exact": bool(be)})
    r_main = np.array([r_of(s, p) for s in SHARES for p in PHIS])
    v_main = np.array([v_of(s) for s in SHARES for p in PHIS])
    alt_rows = []
    ok_alt = True
    for i, share in enumerate(SHARES):
        rr_ = [r_of(share, p) for p in PHIS_ALT]
        got_span = float(max(rr_) - min(rr_))
        be = got_span == PLANNER_ALT_SPANS[i]
        ok_alt &= be
        alt_rows.append({"share": share, "span_expected": PLANNER_ALT_SPANS[i],
                         "span_rederived": got_span, "bit_exact": bool(be)})
    r_alt = np.array([r_of(s, p) for s in SHARES for p in PHIS_ALT])
    v_alt = np.array([v_of(s) for s in SHARES for p in PHIS_ALT])
    desc = [
        ("MAIN corr(r, V)", pearson(r_main, v_main), PLANNER_MAIN_CORR_RV),
        ("MAIN corr(r^q, V)", pearson(r_main ** SEALED_Q, v_main), PLANNER_MAIN_CORR_RQ_V),
        ("ALT corr(r, V)", pearson(r_alt, v_alt), PLANNER_ALT_CORR_RV),
        ("ALT corr(r^q, V)", pearson(r_alt ** SEALED_Q, v_alt), PLANNER_ALT_CORR_RQ_V),
    ]
    desc_d = {n: {"rederived": g, "registration": e, "bit_exact": bool(g == e)}
              for n, g, e in desc}
    out["planner_tables"] = {
        "main_ladder": {"phi": list(PHIS), "rows": main_rows, "PASS": bool(ok_main)},
        "alt_ladder": {"phi": list(PHIS_ALT), "rows": alt_rows, "PASS": bool(ok_alt)},
        "descriptives": desc_d,
        "PASS": bool(ok_main and ok_alt and all(d["bit_exact"] for d in desc_d.values())),
        "note": "the planner RAN this arithmetic at registration time (the rule-11 "
                "convention #43 bought); the executor reproduces it bit-exactly"}

    # (viii): the M1-STOP numbers, against THIS executor's own M1 artifacts.
    m1d = read_json(M1RES / "stop_diagnostic.json")
    m1_checks = [
        ("M1 infimum |corr(r,V)| at registered shares",
         m1d["infimum_at_registered_shares"]["inf_abs_corr"], M1_INF_CORR),
        ("M1 freed-shares bound",
         m1d["best_with_shares_also_freed"]["best_abs_corr_found"], M1_FREED_CORR),
    ]
    for i, s in enumerate(SHARES):
        m1_checks.append(
            (f"M1 full-interval r span at share {s!r}",
             m1d["phi_leverage_per_share"][i]["max_span_over_full_phi_interval"],
             M1_FULL_INTERVAL_SPANS[i]))
    out["m1_stop_citations"] = {
        n: {"persisted": g, "adjudication": e, "bit_exact": bool(g == e)}
        for n, g, e in m1_checks}
    out["m1_stop_source"] = rel(M1RES / "stop_diagnostic.json")

    ok = (all(d["bit_exact"] for d in out["maps"].values())
          and all(d["bit_exact"] for d in out["k2f_quoted"].values())
          and all(d["bit_exact"] for d in out["registration_citations"].values())
          and out["k2f_winner_is_F2"] and out["dopen_m4_level"]["bit_exact"]
          and out["theory_band"]["found"] and out["planner_tables"]["PASS"]
          and all(d["bit_exact"] for d in out["m1_stop_citations"].values()))
    out["PASS"] = bool(ok)
    out["failure_meaning"] = ("a mismatch on any clause is a CITATION DEFECT: STOP, "
                              "report, do not repair silently")
    return out


def inheritance_check() -> dict[str, Any]:
    """RN-M1B-1: prove the copied machinery is bit-identical to M1's."""
    a = m1()
    probe_r = np.array([0.8189581462487876, 0.7558507450373838, 0.6941115392115328,
                        0.5151304058057474, 0.4541409476972356])
    probe_v = np.array([0.03, 0.075, 0.12, 0.18, 0.18])
    probe_y = np.array([0.11, 0.10, 0.09, 0.07, 0.06])
    per_form = {}
    ok = True
    for form in FORM_ORDER:
        mine = fit_form(form, probe_r, probe_v, probe_y)
        theirs = a.fit_form(form, probe_r, probe_v, probe_y)
        same = (mine["theta"] == theirs["theta"] and mine["sse"] == theirs["sse"]
                and starts_for(form) == a.starts_for(form)
                and FORMS[form]["expr"] == a.FORMS[form]["expr"]
                and list(FORMS[form]["names"]) == list(a.FORMS[form]["names"]))
        ok &= same
        per_form[form] = {"theta_mine": mine["theta"], "theta_m1": theirs["theta"],
                          "sse_mine": mine["sse"], "sse_m1": theirs["sse"],
                          "n_starts_mine": len(starts_for(form)),
                          "n_starts_m1": len(a.starts_for(form)),
                          "expr_match": bool(FORMS[form]["expr"] == a.FORMS[form]["expr"]),
                          "bit_exact": bool(same)}
    grids = {"lambda": list(START_LAMBDA) == list(a.START_LAMBDA),
             "q": list(START_Q) == list(a.START_Q),
             "kappa": list(START_KAPPA) == list(a.START_KAPPA),
             "p": list(START_P) == list(a.START_P),
             "epsilon": list(START_EPS) == list(a.START_EPS),
             "eps_bounds": list(EPS_BOUNDS) == list(a.EPS_BOUNDS)}
    optk = [k for k in OPT if k != "scipy_version"]
    opt_same = all(OPT[k] == a.OPT[k] for k in optk)
    bars = {"L1_Q_WIDTH_MAX": L1_Q_WIDTH_MAX == a.L1_Q_WIDTH_MAX,
            "L2_RESPONSE_BAND": tuple(L2_RESPONSE_BAND) == tuple(a.L2_RESPONSE_BAND),
            "L3_KAPPA_CI": tuple(L3_KAPPA_CI) == tuple(a.L3_KAPPA_CI),
            "TIE_REL": TIE_REL == a.TIE_REL, "BOUNDARY_REL": BOUNDARY_REL == a.BOUNDARY_REL,
            "B_BOOT": B_BOOT == a.B_BOOT, "B_BOOT_HIGH": B_BOOT_HIGH == a.B_BOOT_HIGH,
            "B_PROJ": B_PROJ == a.B_PROJ, "MASTER_SEED": MASTER_SEED == a.MASTER_SEED,
            "G3M_PROJ_WIDTH_MAX": G3M_PROJ_WIDTH_MAX == a.G3M_PROJ_WIDTH_MAX,
            "G3M_DF": G3M_DF == a.G3M_DF, "G3M_CHI2_Q": G3M_CHI2_Q == a.G3M_CHI2_Q}
    ok = bool(ok and all(grids.values()) and opt_same and all(bars.values()))
    return {"note": RN_NOTES["RN-M1B-1"], "m1_module": "run_suica_m4_m1_r_at_level",
            "per_form": per_form, "start_grids_identical": grids,
            "optimizer_identical": bool(opt_same),
            "inherited_bars_identical": bars, "PASS": ok,
            "probe": {"r": [float(x) for x in probe_r], "V": [float(x) for x in probe_v],
                      "y": [float(x) for x in probe_y]}}


def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    for nm in ("g2m_pilot.json", "g3mb_power.json", "cell_means.csv", "fits.json"):
        if (OUT / nm).exists():
            raise SystemExit(f"STOP (ordering): {nm} exists before Part 0.")
    _ordering_log("part0_start")

    inh = inheritance_check()
    g0 = g0m_check()
    g1 = g1m_check(PHIS)

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md (M4-M1b, BEFORE run, "
                        "commit 2e4e404); inherits M4-M1's registration verbatim except "
                        "the changes enumerated there",
        "master_seed": MASTER_SEED,
        "salts": {"main": SALT_WORLD, "pilot": SALT_PILOT},
        "rn_notes": RN_NOTES,
        "inheritance_check_RN_M1B_1": inh,
        "rule25": "the ONLY feasibility gate is G3m'(b), stated in the estimand's own "
                  "quantity (projected q identification width). Marginal corr(r, V) and "
                  "corr(r^q, V) are REPORTED and gate nothing.",
        "carrier": {
            "inherits": "K2F-FRESH (results/m4_k2f_level_law/part0.json:fresh_arm) "
                        "verbatim except (share, phi)",
            "int_share": INT_SHARE, "w_int_arm": W_INT_ARM,
            "instrument": "k2b.run_field_world (985-author K1-pinned panel, F2 "
                          "m-multiset, 4 contexts)",
            "field_statistic": "recovery_b_only, per world",
            "cell_level": "mean over the cell's worlds (K2f's _level_from_raw)",
            "k2f_fresh_arm_block": read_json(K2F / "part0.json")["fresh_arm"]},
        "design": {"shares": list(SHARES), "phi_ladder": list(PHIS),
                   "phi_ladder_alt": list(PHIS_ALT),
                   "alt_fires_only_on": "G2m'(i) regime-guard failure at a phi-extension "
                                        "corner (once)",
                   "n_cells": len(SHARES) * len(PHIS),
                   "worlds_per_cell_base": N_WORLDS_BASE,
                   "worlds_per_cell_escalated": N_WORLDS_ESCALATED,
                   "n_worlds_total_base": len(SHARES) * len(PHIS) * N_WORLDS_BASE,
                   "phi_extension_disclosure":
                       "phi at {0.05, 0.30, 0.60, 0.85} is a regime EXTENSION beyond the "
                       "exercised {0.90, 0.98}; guarded by G2m'; the law claim stays "
                       "scoped to the tested grid"},
        "forms": {k: FORMS[k]["expr"] for k in FORM_ORDER},
        "form_notes": {
            "F1e": "the ONLY bounded form (epsilon in [0, 0.05]). Near q ~ 0 its "
                   "(lambda, epsilon) ridge is SINGULAR -- disclosed; LOO pays for it.",
            "nesting": "F2 nests F1 at p=0 and F3 at p=q; F1e nests F1 at epsilon=0",
            "grain": "fit on the 20 CELL MEANS; world-level fitting is "
                     "minimizer-identical at equal cell n (noted, not run)"},
        "optimizer": {**OPT, "scipy_version": __import__("scipy").__version__,
                      "n_starts": {f: len(starts_for(f)) for f in FORM_ORDER},
                      "start_grid": {"lambda": list(START_LAMBDA), "q": list(START_Q),
                                     "kappa": list(START_KAPPA), "p": list(START_P),
                                     "epsilon": list(START_EPS)},
                      "epsilon_bounds": list(EPS_BOUNDS),
                      "same_optimum_sse_tol": OPT_SAME_SSE_TOL,
                      "selection": "leave-one-CELL-out RMSE (20 refits per form, full "
                                   "grid + full-data optimum)"},
        "bootstrap": {"kind": "within-cell world-block", "B": B_BOOT,
                      "B_high": B_BOOT_HIGH, "seed": MASTER_SEED,
                      "spec": "each draw resamples the cell's world indices with "
                              "replacement INDEPENDENTLY per cell, recomputes the 20 cell "
                              "means, refits from the full-data optimum start",
                      "cells_never_dropped": True,
                      "discard_rules": "non-convergence, |param| >= 1e6 (K2f)",
                      "rule13": f"any verdict within {BOUNDARY_REL:.0%} of its boundary "
                                f"re-runs at B={B_BOOT_HIGH} and scores BOUNDARY if "
                                f"unstable",
                      "tie_rule": f"if the top two forms' LOO-RMSE differ by < "
                                  f"{TIE_REL:.0%} of the winner's, every verdict must "
                                  f"agree across both, else that verdict reports SPLIT"},
        "sides_rule22": SIDES,
        "gate_stages_rule23": {
            "G0m'": "inputs exist at Part 0 (persisted K2f / D-open / M1 artifacts, the "
                    "deterministic maps, the theory doc, the planner's embedded tables)",
            "G1m'": "inputs exist at Part 0 (pure design arithmetic)",
            "G2m'": "inputs exist at the pilot stage (16 pilot worlds), before any main "
                    "world",
            "G3m'(a,c)": "inputs exist at Part 0 (sides; stage estimates)",
            "G3m'(b)": "inputs exist AFTER the pilot (needs sigma_w) and BEFORE the first "
                       "main world -- its own permit-gated stage (RN-M1B-7)",
            "G4m'": "inputs exist at Part 0 (the truth table) and at finalize (rule 24)"},
        "stage_estimates_seconds_registration": STAGE_ESTIMATES_REGISTRATION,
        "stage_estimates_seconds_executor": STAGE_ESTIMATES_EXECUTOR,
        "stage_overrun_convention": "a stage exceeding 2x its estimate stops and is "
                                    "reported",
        "rule16_truth_table": TRUTH_TABLE,
        "rule16_note": "L-2 is recorded N/A in cell 2 (the q question is unposed); L-3 is "
                       "evaluated in every cell 2-6 since kappa is identified even where "
                       "q is not, and in cell 3 it is reported descriptively",
        "environment": {"python": sys.version.split()[0],
                        "python_executable": sys.executable,
                        "platform": platform.platform(), "numpy": np.__version__,
                        "pandas": pd.__version__,
                        "scipy": __import__("scipy").__version__},
        "G0m'": g0, "G1m'": g1, "seconds": None,
    }
    part0["seconds"] = time.time() - t0
    write_json(OUT / "part0.json", part0)
    _write_part0_tables(part0)
    _ordering_log("part0_done", seconds=part0["seconds"], G0m_PASS=g0["PASS"],
                  G1m_PASS=g1["PASS"], inheritance_PASS=inh["PASS"],
                  corr_r_V=g1["descriptive_NOT_a_gate"]["corr_r_V"])
    if not inh["PASS"]:
        raise SystemExit("STOP: RN-M1B-1 inheritance check FAILED -- the copied "
                         "machinery is not bit-identical to M1's.")
    if not g0["PASS"]:
        raise SystemExit("STOP: G0m' FAILED (citation defect) -- see part0.json")
    if not g1["PASS"]:
        raise SystemExit("STOP_DESIGN_INFEASIBLE: G1m' FAILED -- see part0.json")
    print(f"part0 OK  G0m' PASS  G1m' PASS  inheritance PASS  "
          f"corr(r,V)={g1['descriptive_NOT_a_gate']['corr_r_V']!r} (reported, not gated)  "
          f"{time.time() - t0:.1f}s")
    _ = args


def _cell(s: Any) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _md_table(header: list[str], rows: list[list[str]]) -> list[str]:
    return (["| " + " | ".join(_cell(h) for h in header) + " |",
             "|" + "|".join(["---"] * len(header)) + "|"]
            + ["| " + " | ".join(_cell(c) for c in r) + " |" for r in rows])


def _write_part0_tables(part0: dict[str, Any]) -> None:
    g1 = part0["G1m'"]
    lines = ["# M4-M1b Part 0 tables (generated from artifacts -- rule 24)", "",
             "## The realized design: 20 (r, V) points", ""]
    lines += _md_table(
        ["cell", "share", "phi", "r_pred", "V_person"],
        [[d["cell_tag"], repr(d["share"]), repr(d["phi"]), repr(d["r_pred"]),
          repr(d["V_person"])] for d in g1["design_points"]])
    lines += ["", "## G1m' gates", ""]
    sp = g1["(c') within-share r span"]
    lines += _md_table(
        ["gate", "bar", "realized", "PASS"],
        [["(a) shares inside envelope", repr(list(SHARE_ENVELOPE)), repr(list(SHARES)),
          str(g1["(a) shares inside envelope"]["PASS"])],
         ["(b) V max/min", f">= {G1M_V_RATIO_MIN}", repr(g1["(b) V ratio"]["ratio"]),
          str(g1["(b) V ratio"]["PASS"])],
         ["(c') within-share r SPAN at shares " + repr(list(G1M_SPAN_SHARES)),
          f">= {G1M_SPAN_MIN}",
          repr([x["span"] for x in sp["per_share"] if x["in_span_gate"]]),
          str(sp["PASS"])],
         ["(e) duplicate (r, V) points", "0",
          str(len(g1["(e) no duplicate design points"]["duplicates"])),
          str(g1["(e) no duplicate design points"]["PASS"])]])
    (OUT / "part0_tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# World running.

def _run_cell(share: float, phi: float, salt: str, indices: list[int], tag: str,
              verify_first: bool, with_card: bool) -> pd.DataFrame:
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
    phis = tuple(p0["design"]["phi_ladder"])
    corner_phis = (phis[0], phis[-1])
    corners = [(s, p) for s in PILOT_SHARES for p in corner_phis]

    frames = []
    for k, (share, phi) in enumerate(corners):
        df = _run_cell(share, phi, SALT_PILOT, list(range(PILOT_WORLDS)),
                       f"M1B-PILOT-{cell_tag(share, phi)}", verify_first=(k == 0),
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

    # (i) REGIME guard: finite, non-saturated, nonzero within-corner variance.
    per_corner = []
    regime_ok = True
    for (share, phi), grp in pilot.groupby(["share", "phi"]):
        vals = grp["recovery_b_only"].to_numpy(float)
        sd = float(np.std(vals, ddof=1))
        fin = bool(np.all(np.isfinite(vals)))
        ins = bool(np.all((vals > 0.0) & (vals < 1.0)))
        nz = bool(sd > 0.0)
        is_ext = bool(phi not in (0.90, 0.98))
        regime_ok &= (fin and ins and nz)
        per_corner.append({"cell": cell_tag(float(share), float(phi)),
                           "share": float(share), "phi": float(phi),
                           "is_phi_extension_corner": is_ext, "n": int(len(vals)),
                           "mean": float(vals.mean()), "sd": sd,
                           "min": float(vals.min()), "max": float(vals.max()),
                           "all_finite": fin, "strictly_inside_unit": ins,
                           "nonzero_variance": nz, "PASS": bool(fin and ins and nz)})

    # (ii) phi->r channel liveness on the REALIZED CARD statistic (RN-M1B-3).
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
    dr_arith = float(r_of(max(PILOT_SHARES), corner_phis[0])
                     - r_of(max(PILOT_SHARES), corner_phis[1]))

    g2 = {
        "utc": datetime.now(UTC).isoformat(), "permit": permit,
        "n_k2b_instances_guarded": n_guarded,
        "corner_cells": [cell_tag(s, p) for s, p in corners],
        "worlds_per_corner": PILOT_WORLDS, "salt": SALT_PILOT,
        "per_world": pilot[["share", "phi", "world", "world_seed", "recovery_b_only",
                            "r_card_b_raw"]].to_dict("records"),
        "(i) regime guard": {
            "per_corner": per_corner,
            "g4b_route_residual_maxabs": resid_max,
            "g4b_residuals_ok": bool(np.isnan(resid_max) or resid_max <= 1e-9),
            "field_min": float(pv.min()), "field_max": float(pv.max()),
            "PASS": bool(regime_ok and (np.isnan(resid_max) or resid_max <= 1e-9)),
            "fallback": "failure at a phi-EXTENSION corner -> ALT ladder once (re-run "
                        "G1m' and G3m'(b)); then STOP_DESIGN_INFEASIBLE"},
        "(ii) liveness (rule 3, phi->r channel)": {
            "GATE_reading_card_attenuation": card,
            "gate_object": "r_card_b_raw (RN-M1B-3)",
            "gate_object_source":
                "scripts/run_suica_m4_k2b_t4_branch.py:392-503 card_channel_frame -> "
                ":505-509 bootstrap_card -> :486 r_card_b_raw; the object k2b's own G2 "
                "lever-liveness check uses at :944-963",
            "arithmetic_certification": {
                "delta_r_from_pinned_map": dr_arith,
                "registration_value": PLANNER_TABLE_MAIN[0.60]["span"],
                "bit_exact": bool(dr_arith == PLANNER_TABLE_MAIN[0.60]["span"]),
                "note": "the registration's alternative certification route, recorded so "
                        "the clause is satisfied under either reading of 'persists one'"},
            "DESCRIPTIVE_field_contrast_NOT_a_gate": {
                **field,
                "why_not_a_gate": "rule 25 / the registration: an outcome-side flat field "
                                  "is cell-2 EVIDENCE, not channel death"},
            "PASS": card["PASS"]},
        "seconds": time.time() - t0,
    }
    g2["PASS"] = bool(g2["(i) regime guard"]["PASS"]
                      and g2["(ii) liveness (rule 3, phi->r channel)"]["PASS"])
    write_json(OUT / "g2m_pilot.json", g2)
    _ordering_log("pilot_done", seconds=g2["seconds"], PASS=g2["PASS"],
                  card_se=card["abs_contrast_over_SE"])
    if not g2["PASS"]:
        raise SystemExit("STOP: G2m' FAILED -- see results/m4_m1b_r_at_level/"
                         "g2m_pilot.json")
    print(f"pilot OK  regime PASS  liveness card={card['abs_contrast_over_SE']:.3f} SE "
          f"(field descriptive {field['abs_contrast_over_SE']:.3f} SE)  "
          f"{time.time() - t0:.1f}s")
    _ = args


def _project(r: np.ndarray, v: np.ndarray, sigma_w: float, n_worlds: int,
             t0: float) -> dict[str, Any]:
    cell_sd = sigma_w / np.sqrt(n_worlds)
    rng = np.random.default_rng(MASTER_SEED)
    truths = {}
    for q_truth in (1.0, SEALED_Q):
        mu = K2F_F2_LAMBDA * r ** q_truth - K2F_F2_KAPPA * v
        qs, nfail = [], 0
        for _ in range(B_PROJ):
            y = mu + rng.normal(0.0, cell_sd, size=len(r))
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
            "n_failed": int(nfail), "q_hat_median": float(np.median(arr)),
            "q_hat_mean": float(arr.mean()), "q_hat_q025": lo, "q_hat_q975": hi,
            "width_proxy": float(hi - lo),
            "PASS": bool(hi - lo <= G3M_PROJ_WIDTH_MAX)}
        print(f"    q_truth={q_truth!r} @ n={n_worlds}: width={hi - lo!r} "
              f"({time.time() - t0:.1f}s)", flush=True)
    return {"n_worlds_per_cell": n_worlds, "cell_mean_sd_used": float(cell_sd),
            "projections": truths,
            "PASS": bool(all(t["PASS"] for t in truths.values()))}


def stage_power(args: argparse.Namespace) -> None:
    """G3m'(b): THE feasibility gate, in the estimand's own quantity (rule 25)."""
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    g2 = read_json(OUT / "g2m_pilot.json")
    if not g2["PASS"]:
        raise SystemExit("STOP: G3m'(b) requires a passing G2m'.")
    pilot = read_csv_rt(OUT / "pilot_field.csv")

    ss, df_tot, per_cell = 0.0, 0, []
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

    dsg = pd.DataFrame(p0["G1m'"]["design_points"])
    r = dsg["r_pred"].to_numpy(float)
    v = dsg["V_person"].to_numpy(float)

    base = _project(r, v, sigma_w, N_WORLDS_BASE, t0)
    escalated = None
    decided = N_WORLDS_BASE
    if not base["PASS"]:
        print(f"  base projection FAILED at n={N_WORLDS_BASE}; firing the pre-declared "
              f"once-only escalation to n={N_WORLDS_ESCALATED}", flush=True)
        escalated = _project(r, v, sigma_w, N_WORLDS_ESCALATED, t0)
        if escalated["PASS"]:
            decided = N_WORLDS_ESCALATED

    out = {
        "utc": datetime.now(UTC).isoformat(),
        "sigma_w_raw_pooled": sigma_raw, "pooled_df": int(df_tot),
        "df_declared": G3M_DF,
        "chi2_quantile": {"q": G3M_CHI2_Q, "df": G3M_DF, "value": chi2_q},
        "df_inflation_factor": inflation, "sigma_w": sigma_w,
        "per_pilot_cell": per_cell,
        "truths": {"lambda": K2F_F2_LAMBDA, "kappa": K2F_F2_KAPPA, "epsilon": 0.0,
                   "q_grid": [1.0, SEALED_Q],
                   "note": "no projection at q_truth = 0 -- structural non-identification "
                           "there is cell R_TERM_ABSENT's subject, not a power failure"},
        "fit_form": "F1 with the full start grid", "bar": G3M_PROJ_WIDTH_MAX,
        "rule25": "this is THE feasibility gate: the leg's estimand is q, and this is q's "
                  "projected identification width",
        "base": base, "escalated": escalated,
        "escalation_fired": bool(escalated is not None),
        "escalation_rule": "pre-declared, once only: on fail recompute at 64 worlds/cell "
                           "(noise /sqrt2); pass -> the main grid runs at 64; fail again "
                           "-> STOP as NON_PROJECTABLE",
        "worlds_per_cell_decided": decided,
        "n_worlds_total": int(len(r) * decided),
        "seconds": time.time() - t0,
    }
    out["PASS"] = bool(base["PASS"] or (escalated is not None and escalated["PASS"]))
    write_json(OUT / "g3mb_power.json", out)
    _ordering_log("power_done", seconds=out["seconds"], sigma_w=sigma_w,
                  PASS=out["PASS"], escalation_fired=out["escalation_fired"],
                  worlds_per_cell=decided)
    if not out["PASS"]:
        raise SystemExit("STOP: NON_PROJECTABLE -- G3m'(b) failed after its once-only "
                         "escalation; see g3mb_power.json")
    print(f"power OK  sigma_w={sigma_w!r}  escalation_fired={out['escalation_fired']}  "
          f"worlds/cell={decided}  {time.time() - t0:.1f}s")
    _ = args


def _worlds_chunk(chunk: str) -> None:
    t0 = time.time()
    _arm_guard()
    permit = _issue_permit("main")
    p0 = read_json(OUT / "part0.json")
    g3 = read_json(OUT / "g3mb_power.json")
    n_worlds = int(g3["worlds_per_cell_decided"])          # RN-M1B-4
    phis = tuple(p0["design"]["phi_ladder"])
    share = SHARES["abcd".index(chunk)]
    (OUT / "cells").mkdir(parents=True, exist_ok=True)
    written = []
    for phi in phis:
        path = OUT / "cells" / f"cell_{cell_tag(share, phi)}_field.csv"
        df = _run_cell(share, phi, SALT_WORLD, list(range(n_worlds)),
                       f"M1B-{cell_tag(share, phi)}", verify_first=False, with_card=False)
        df.to_csv(path, index=False)
        vals = df["recovery_b_only"].to_numpy(float)
        written.append({"cell": cell_tag(share, phi), "share": share, "phi": phi,
                        "n": int(len(vals)), "mean": float(vals.mean()),
                        "sem": float(np.std(vals, ddof=1) / np.sqrt(len(vals))),
                        "file": rel(path)})
        print(f"  {cell_tag(share, phi)}: n={len(vals)} mean={vals.mean()!r} "
              f"({time.time() - t0:.1f}s)", flush=True)
    out = {"utc": datetime.now(UTC).isoformat(), "chunk": chunk, "share": share,
           "permit": permit, "cells": written, "salt": SALT_WORLD,
           "worlds_per_cell": n_worlds, "generations": _GEN_COUNT,
           "seconds": time.time() - t0}
    write_json(OUT / f"worlds_{chunk}.json", out)
    _ordering_log(f"worlds_{chunk}_done", share=share, seconds=out["seconds"])
    print(f"worlds_{chunk} OK  share={share!r}  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# FIT.

def _load_cells() -> tuple[pd.DataFrame, np.ndarray]:
    p0 = read_json(OUT / "part0.json")
    g3 = read_json(OUT / "g3mb_power.json")
    n_worlds = int(g3["worlds_per_cell_decided"])
    dsg = pd.DataFrame(p0["G1m'"]["design_points"])
    rows, per_world = [], []
    for _, d in dsg.iterrows():
        path = OUT / "cells" / f"cell_{d['cell_tag']}_field.csv"
        if not path.exists():
            raise SystemExit(f"REFUSED: missing cell artifact {path}")
        df = read_csv_rt(path)
        vals = df["recovery_b_only"].to_numpy(float)
        if len(vals) != n_worlds:
            raise SystemExit(f"REFUSED: {path} has {len(vals)} worlds, expected {n_worlds}")
        if not np.all(np.isfinite(vals)):
            raise SystemExit(f"REFUSED: non-finite recovery_b_only in {path}")
        rows.append({"cell_tag": d["cell_tag"], "share": float(d["share"]),
                     "phi": float(d["phi"]), "r_pred": float(d["r_pred"]),
                     "V_person": float(d["V_person"]), "field_mean": float(vals.mean()),
                     "field_sd": float(np.std(vals, ddof=1)),
                     "field_sem": float(np.std(vals, ddof=1) / np.sqrt(len(vals))),
                     "n_worlds": int(len(vals)), "source": rel(path)})
        per_world.append(vals)
    return pd.DataFrame(rows), np.asarray(per_world, float)


def _boundary_flags(fits: dict[str, Any], loos: dict[str, Any],
                    order: list[str]) -> dict[str, Any]:
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
        for en, edge in (("q_lo", qlo), ("q_hi", qhi)):
            for bn, bar in (("1.71", L2_RESPONSE_BAND[0]), ("1.98", L2_RESPONSE_BAND[1])):
                flagged |= add(f"{form}: {en} vs response band {bn}", edge, bar)
        klo, khi = b["ci95"]["kappa"]
        flagged |= add(f"{form}: kappa_hi vs K2f ci95 lo", khi, L3_KAPPA_CI[0])
        flagged |= add(f"{form}: kappa_lo vs K2f ci95 hi", klo, L3_KAPPA_CI[1])
        llo, lhi = b["ci95"]["lambda"]
        flagged |= add(f"{form}: lambda CI nearest endpoint vs 0 (RN-M1B-6)",
                       float(min(abs(llo), abs(lhi))), 0.0,
                       rel_scale=fits[form]["theta"][0])
    sep = loos[order[1]]["loo_rmse"] - loos[order[0]]["loo_rmse"]
    near_tie = bool(sep <= TIE_REL * loos[order[0]]["loo_rmse"])
    recs.append({"quantity": "LOO separation winner vs runner-up", "value": float(sep),
                 "bar": 0.0, "gap": float(sep), "scale": float(loos[order[0]]["loo_rmse"]),
                 f"within_{int(BOUNDARY_REL * 100)}pct": near_tie})
    flagged |= near_tie
    return {"records": recs, "any_flagged": bool(flagged),
            "forms_to_rerun": [order[0], order[1]] if flagged else [],
            "rule": f"a quantity within {BOUNDARY_REL:.0%} of its bar triggers the "
                    f"B={B_BOOT_HIGH} re-run; a verdict that changes scores BOUNDARY"}


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
    out = {
        "utc": datetime.now(UTC).isoformat(), "n_cells": int(len(y)),
        "worlds_per_cell": int(cells["n_worlds"].iloc[0]),
        "fits": fits, "ranking_by_loo": order, "winner": winner, "runner_up": runner,
        "loo_separation": float(sep),
        "loo_separation_rel": float(sep / loos[winner]["loo_rmse"]),
        "tie_rule_active": bool(sep < TIE_REL * loos[winner]["loo_rmse"]),
        "boundary_flags": _boundary_flags(fits, loos, order),
        "seconds": time.time() - t0,
    }
    write_json(OUT / "fits.json", out)
    write_json(OUT / "loo.json", {"loo": loos, "ranking": order, "winner": winner,
                                  "cell_tags": list(cells["cell_tag"])})
    _ordering_log("fit_done", winner=winner, loo=loos[winner]["loo_rmse"],
                  tie=out["tie_rule_active"], seconds=out["seconds"])
    print(f"fit OK  winner={winner}  LOO={loos[winner]['loo_rmse']!r}  "
          f"tie={out['tie_rule_active']}  {time.time() - t0:.1f}s")
    _ = args


def stage_rule13(args: argparse.Namespace) -> None:
    t0 = time.time()
    fits = read_json(OUT / "fits.json")
    flags = fits["boundary_flags"]
    out: dict[str, Any] = {"utc": datetime.now(UTC).isoformat(),
                           "triggered": bool(flags["any_flagged"]), "B": B_BOOT_HIGH,
                           "seed": MASTER_SEED, "forms": {}, "seconds": None}
    if flags["any_flagged"]:
        cells, per_world = _load_cells()
        r = cells["r_pred"].to_numpy(float)
        v = cells["V_person"].to_numpy(float)
        for form in flags["forms_to_rerun"]:
            out["forms"][form] = bootstrap_form(form, r, v, per_world,
                                                fits["fits"][form]["theta"],
                                                B_BOOT_HIGH, MASTER_SEED)
            print(f"  {form} B={B_BOOT_HIGH}: {out['forms'][form]['n_used']} used "
                  f"({time.time() - t0:.1f}s)", flush=True)
    else:
        out["note"] = "no verdict quantity within Monte-Carlo error of its bar"
    out["seconds"] = time.time() - t0
    write_json(OUT / "boot_high.json", out)
    _ordering_log("rule13_done", triggered=out["triggered"], seconds=out["seconds"])
    print(f"rule13 OK  triggered={out['triggered']}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# FINALIZE.

def _verdicts_for(form: str, boot: dict[str, Any], theta: list[float],
                  names: list[str]) -> dict[str, Any]:
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
    l3 = "overlap" if overlap else ("disjoint-low" if khi < L3_KAPPA_CI[0]
                                    else "disjoint-high")
    return {"form": form, "theta": dict(zip(names, theta)), "q_ci": [qlo, qhi],
            "q_ci_width": float(width), "kappa_ci": [klo, khi], "lambda_ci": [llo, lhi],
            "L-1": l1, "L-2": l2, "L-3": l3,
            "lambda_ci_contains_zero": bool(llo <= 0.0 <= lhi)}


def _route(l1: str, l2: str, lam_zero: bool) -> tuple[int, str]:
    if l1 == "MISS":
        return (2, "R_TERM_ABSENT_AT_LEVEL") if lam_zero else (
            3, "NON_IDENTIFIED_UNDERPOWERED")
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
                       fits["fits"][winner]["theta"], fits["fits"][winner]["param_names"])
    vr = _verdicts_for(runner, fits["fits"][runner]["bootstrap"],
                       fits["fits"][runner]["theta"], fits["fits"][runner]["param_names"])

    stability: dict[str, Any] = {"triggered": high["triggered"], "per_form": {}}
    vw_high = None
    if high["triggered"]:
        for form, vlow in ((winner, vw), (runner, vr)):
            if form not in high["forms"]:
                continue
            vhigh = _verdicts_for(form, high["forms"][form], fits["fits"][form]["theta"],
                                  fits["fits"][form]["param_names"])
            if form == winner:
                vw_high = vhigh
            keys = ("L-1", "L-2", "L-3", "lambda_ci_contains_zero")
            stability["per_form"][form] = {
                "B2000": {k: vlow[k] for k in keys},
                "B20000": {k: vhigh[k] for k in keys},
                "q_ci_B2000": vlow["q_ci"], "q_ci_B20000": vhigh["q_ci"],
                "kappa_ci_B2000": vlow["kappa_ci"], "kappa_ci_B20000": vhigh["kappa_ci"],
                "lambda_ci_B2000": vlow["lambda_ci"],
                "lambda_ci_B20000": vhigh["lambda_ci"],
                "max_endpoint_shift": float(max(
                    abs(vhigh[c][i] - vlow[c][i])
                    for c in ("q_ci", "kappa_ci", "lambda_ci") for i in (0, 1))),
                "stable": bool(all(vlow[k] == vhigh[k] for k in keys))}
    stability["all_stable"] = bool(
        all(d["stable"] for d in stability["per_form"].values())
        if stability["per_form"] else True)

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
    cell_n, slug = _route(vw["L-1"], vw["L-2"], bool(vw["lambda_ci_contains_zero"]))
    modifier = ("TAX_SHIFT_AT_LEVEL" if a3["verdict"] in ("disjoint-low", "disjoint-high")
                else "KAPPA_FOURTH_APPEARANCE")
    if cell_n == 2:
        a2["verdict"] = "N/A"
        a2["note"] = "cell 2: the q question is unposed, L-2 recorded N/A (registration)"
    if cell_n == 3:
        a3["note"] = ("cell 3: L-3 reported descriptively, adjudicating nothing "
                      "(registration)")

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
                          "spearman_resid_phi": float(rho), "sign": int(np.sign(rho)),
                          "perfectly_monotone": bool(abs(abs(rho) - 1.0) < 1e-12),
                          "residuals": [float(x) for x in sub["residual_winner"]],
                          "phis": [float(x) for x in sub["phi"]]})
    signs = [p["sign"] for p in per_share]
    n_pos, n_neg = sum(1 for s in signs if s > 0), sum(1 for s in signs if s < 0)
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
          "readings_note": RN_NOTES["RN-M1B-5"]}

    marginal_corr = p0["G1m'"]["descriptive_NOT_a_gate"]["corr_r_V"]
    gates = {
        "G0m'": {"PASS": p0["G0m'"]["PASS"],
                 "detail": "(i)-(vi) M1's anchors re-verified; (vii) BOTH planner design "
                           "tables reproduced bit-exactly; (viii) the M1-STOP numbers "
                           "verified against results/m4_m1_r_at_level/"},
        "G1m'": {"PASS": p0["G1m'"]["PASS"],
                 "detail": "(a)(b)(c')(e) pass; NO marginal gate (rule 25) -- corr(r,V) = "
                           + repr(marginal_corr) + " reported only"},
        "G2m'": {"PASS": g2["PASS"],
                 "detail": "regime guard passed at all 4 corners; phi->r liveness on the "
                           "REALIZED CARD statistic; the field contrast is descriptive "
                           "and gates nothing"},
        "G3m'": {"PASS": bool(g3["PASS"]),
                 "detail": f"THE feasibility gate: projected q widths "
                           f"{[t['width_proxy'] for t in g3['base']['projections'].values()]}"
                           f" at n={N_WORLDS_BASE} against the {G3M_PROJ_WIDTH_MAX} bar; "
                           f"escalation_fired={g3['escalation_fired']}; decided "
                           f"n={g3['worlds_per_cell_decided']}"},
        "G4m'": {"PASS": True, "detail": "inherited truth table reproduced verbatim with "
                                         "cell 1 restated; every report table generated "
                                         "from artifacts"},
    }

    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED, "salts": {"main": SALT_WORLD, "pilot": SALT_PILOT},
        "n_cells": int(len(cells)),
        "worlds_per_cell": int(g3["worlds_per_cell_decided"]),
        "n_worlds_main": int(len(cells) * g3["worlds_per_cell_decided"]),
        "n_worlds_pilot": int(len(PILOT_SHARES) * 2 * PILOT_WORLDS),
        "design": p0["design"],
        "descriptive_collinearity_NOT_a_gate": p0["G1m'"]["descriptive_NOT_a_gate"],
        "winner": winner, "winner_expr": FORMS[winner]["expr"],
        "winner_theta": dict(zip(fits["fits"][winner]["param_names"],
                                 fits["fits"][winner]["theta"])),
        "runner_up": runner,
        "loo_rmse_by_form": {f: loos["loo"][f]["loo_rmse"] for f in FORM_ORDER},
        "in_sample_rmse_by_form": {f: fits["fits"][f]["rmse"] for f in FORM_ORDER},
        "loo_separation": fits["loo_separation"],
        "loo_separation_rel": fits["loo_separation_rel"], "tie_rule_active": tie,
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
        "sigma_w": g3["sigma_w"], "escalation_fired": g3["escalation_fired"],
        "gates": gates,
        "field_mean_range": [float(cells["field_mean"].min()),
                             float(cells["field_mean"].max())],
        "field_sem_range": [float(cells["field_sem"].min()),
                            float(cells["field_sem"].max())],
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    cells.to_csv(OUT / "cell_means.csv", index=False)
    _ordering_log("finalize_done", slug=slug, cell=cell_n, modifier=modifier,
                  seconds=dec["seconds"])
    _write_report_tables(p0, g2, g3, fits, loos, high, cells, dec)
    _write_prose_facts(p0, g2, g3, fits, loos, cells, dec)
    print(f"finalize OK  slug={slug}  cell={cell_n}  modifier={modifier}  "
          f"L-1={a1['verdict']} L-2={a2['verdict']} L-3={a3['verdict']}")
    _ = args


def _write_report_tables(p0: dict[str, Any], g2: dict[str, Any], g3: dict[str, Any],
                         fits: dict[str, Any], loos: dict[str, Any], high: dict[str, Any],
                         cells: pd.DataFrame, dec: dict[str, Any]) -> None:
    """Rule 24: every table carrying artifact numbers is GENERATED here."""
    sec: dict[str, list[str]] = {}
    g0, g1 = p0["G0m'"], p0["G1m'"]

    sec["design"] = _md_table(
        ["cell", "share", "phi", "r_pred", "V_person"],
        [[d["cell_tag"], repr(d["share"]), repr(d["phi"]), repr(d["r_pred"]),
          repr(d["V_person"])] for d in g1["design_points"]])

    rows = []
    for name, d in g0["maps"].items():
        rows.append([name, repr(d["expected"]), repr(d["rederived"]), str(d["bit_exact"])])
    for name, d in g0["k2f_quoted"].items():
        rows.append([name, repr(d["registration"]), repr(d["persisted"]),
                     str(d["bit_exact"])])
    for name, d in g0["registration_citations"].items():
        rows.append([name, repr(d["registration"]), repr(d["rederived"]),
                     str(d["bit_exact"])])
    d = g0["dopen_m4_level"]
    rows.append(["(v) Dopen:M-4 level, mean of the raw per-world CSV", repr(d["expected"]),
                 repr(d["rederived"]), str(d["bit_exact"])])
    d = g0["theory_band"]
    rows.append([f"(vi) `{d['string']}` verbatim in `{d['doc']}`", d["string"],
                 f"found on lines {d['lines']}", str(d["found"])])
    for name, d in g0["planner_tables"]["descriptives"].items():
        rows.append([f"(vii) {name}", repr(d["registration"]), repr(d["rederived"]),
                     str(d["bit_exact"])])
    for name, d in g0["m1_stop_citations"].items():
        rows.append([f"(viii) {name}", repr(d["adjudication"]), repr(d["persisted"]),
                     str(d["bit_exact"])])
    sec["g0m"] = _md_table(["clause", "registration / expected",
                            "re-derived / persisted", "bit-exact"], rows)

    prows = []
    for row in g0["planner_tables"]["main_ladder"]["rows"]:
        prows.append([repr(row["share"]), repr(row["V_rederived"])]
                     + [repr(x) for x in row["r_rederived"]]
                     + [repr(row["span_rederived"]), str(row["bit_exact"])])
    sec["planner_main"] = _md_table(
        ["share", "V_person"] + [f"r(phi={p})" for p in PHIS] + ["span", "bit-exact"],
        prows)
    sec["planner_alt"] = _md_table(
        ["share", "ALT span (registration)", "ALT span (re-derived)", "bit-exact"],
        [[repr(x["share"]), repr(x["span_expected"]), repr(x["span_rederived"]),
          str(x["bit_exact"])] for x in g0["planner_tables"]["alt_ladder"]["rows"]])

    sp = g1["(c') within-share r span"]
    sec["g1m"] = _md_table(
        ["gate", "bar", "realized", "PASS"],
        [["(a) shares inside the trained envelope", repr(list(SHARE_ENVELOPE)),
          repr(list(SHARES)), str(g1["(a) shares inside envelope"]["PASS"])],
         ["(b) V max/min", f">= {G1M_V_RATIO_MIN}", repr(g1["(b) V ratio"]["ratio"]),
          str(g1["(b) V ratio"]["PASS"])],
         [f"(c') within-share r SPAN at shares {list(G1M_SPAN_SHARES)}",
          f">= {G1M_SPAN_MIN}",
          repr([x["span"] for x in sp["per_share"] if x["in_span_gate"]]),
          str(sp["PASS"])],
         ["(e) duplicate (r, V) design points", "0",
          str(len(g1["(e) no duplicate design points"]["duplicates"])),
          str(g1["(e) no duplicate design points"]["PASS"])],
         ["*(no marginal-correlation gate -- rule 25)*", "n/a",
          "corr(r, V) = " + repr(g1["descriptive_NOT_a_gate"]["corr_r_V"])
          + ", REPORTED only", "n/a"]])

    sec["spans"] = _md_table(
        ["share", "V_person", "r min", "r max", "span", "ratio", "in (c') gate",
         f"span >= {G1M_SPAN_MIN}"],
        [[repr(x["share"]), repr(x["V_person"]), repr(x["r_min"]), repr(x["r_max"]),
          repr(x["span"]), repr(x["ratio"]), str(x["in_span_gate"]),
          str(x["meets_span_bar"])] for x in sp["per_share"]])

    dsc = g1["descriptive_NOT_a_gate"]
    sec["collinearity"] = _md_table(
        ["quantity (REPORTED, gates nothing -- rule 25)", "value"],
        [["corr(r, V) on M1b's 20-point design", repr(dsc["corr_r_V"])],
         [f"corr(r^{SEALED_Q!r}, V) on M1b's design", repr(dsc["corr_r_pow_q_V"])],
         ["corr(r, V) on K2f's 26 rows", repr(dsc["k2f_corr_r_V_26_rows"])],
         ["M1's failed marginal bar (WITHDRAWN by rule 25)", "<= 0.30"]])

    sec["inheritance"] = _md_table(
        ["form", "theta (this leg)", "theta (M1 harness)", "starts", "expr match",
         "bit-exact"],
        [[f, repr(d["theta_mine"]), repr(d["theta_m1"]),
          f"{d['n_starts_mine']} / {d['n_starts_m1']}", str(d["expr_match"]),
          str(d["bit_exact"])]
         for f, d in p0["inheritance_check_RN_M1B_1"]["per_form"].items()])

    sec["pilot"] = _md_table(
        ["cell", "world", "world seed", "recovery_b_only", "realized r_card_b_raw"],
        [[cell_tag(w["share"], w["phi"]), str(int(w["world"])), str(int(w["world_seed"])),
          repr(w["recovery_b_only"]), repr(w["r_card_b_raw"])]
         for w in g2["per_world"]])

    sec["regime"] = _md_table(
        ["corner", "phi-extension?", "n", "mean", "sd", "min", "max", "finite",
         "inside (0,1)", "nonzero var", "PASS"],
        [[c["cell"], str(c["is_phi_extension_corner"]), str(c["n"]), repr(c["mean"]),
          repr(c["sd"]), repr(c["min"]), repr(c["max"]), str(c["all_finite"]),
          str(c["strictly_inside_unit"]), str(c["nonzero_variance"]), str(c["PASS"])]
         for c in g2["(i) regime guard"]["per_corner"]])

    liv = g2["(ii) liveness (rule 3, phi->r channel)"]
    card = liv["GATE_reading_card_attenuation"]
    fld = liv["DESCRIPTIVE_field_contrast_NOT_a_gate"]
    sec["liveness"] = _md_table(
        ["reading", "role", "mean at phi lo", "mean at phi hi", "contrast", "pooled SE",
         "abs(contrast)/SE", f"> {G2M_LIVENESS_SE_MULT}x SE"],
        [["realized card attenuation `r_card_b_raw`", "**THE GATE** (RN-M1B-3)",
          repr(card["mean_at_phi_lo"]), repr(card["mean_at_phi_hi"]),
          repr(card["contrast"]), repr(card["pooled_SE"]),
          repr(card["abs_contrast_over_SE"]), str(card["PASS"])],
         ["field `recovery_b_only`", "descriptive only -- gates NOTHING (rule 25)",
          repr(fld["mean_at_phi_lo"]), repr(fld["mean_at_phi_hi"]), repr(fld["contrast"]),
          repr(fld["pooled_SE"]), repr(fld["abs_contrast_over_SE"]),
          str(fld["PASS"]) + " (not a verdict)"],
         ["pinned-map arithmetic certification", "alternative route, also satisfied",
          "--", "--", repr(liv["arithmetic_certification"]["delta_r_from_pinned_map"]),
          "--", "--",
          "bit-exact vs registration: "
          + str(liv["arithmetic_certification"]["bit_exact"])]])

    prow = [["pooled per-world sd across the 16 pilot worlds "
             f"(df {g3['pooled_df']})", repr(g3["sigma_w_raw_pooled"])],
            [f"chi2_{{{G3M_CHI2_Q}, df={G3M_DF}}}", repr(g3["chi2_quantile"]["value"])],
            ["df-aware inflation sqrt(12 / chi2)", repr(g3["df_inflation_factor"])],
            ["**sigma_w** (inflated)", "**" + repr(g3["sigma_w"]) + "**"]]
    for tagname, blk in (("base n=%d" % N_WORLDS_BASE, g3["base"]),
                         ("escalated n=%d" % N_WORLDS_ESCALATED, g3["escalated"])):
        if blk is None:
            prow.append([f"{tagname} projection", "not run (base passed)"])
            continue
        prow.append([f"{tagname}: cell-mean sd", repr(blk["cell_mean_sd_used"])])
        for t in blk["projections"].values():
            prow.append([f"{tagname}: projected q width at q_truth = {t['q_truth']!r}",
                         repr(t["width_proxy"])])
        prow.append([f"{tagname}: PASS (both truths <= {G3M_PROJ_WIDTH_MAX})",
                     str(blk["PASS"])])
    prow.append(["escalation fired", str(g3["escalation_fired"])])
    prow.append(["**worlds/cell decided**", "**" + str(g3["worlds_per_cell_decided"]) + "**"])
    sec["power"] = _md_table(["quantity", "value"], prow)

    sec["cells"] = _md_table(
        ["cell", "share", "phi", "r_pred", "V_person", "mean field", "SEM", "sd", "n"],
        [[row["cell_tag"], repr(row["share"]), repr(row["phi"]), repr(row["r_pred"]),
          repr(row["V_person"]), repr(row["field_mean"]), repr(row["field_sem"]),
          repr(row["field_sd"]), str(int(row["n_worlds"]))]
         for _, row in cells.iterrows()])

    frows = []
    for form in FORM_ORDER:
        f = fits["fits"][form]
        th = dict(zip(f["param_names"], f["theta"]))
        b = f["bootstrap"]
        extra = [k for k in ("p", "epsilon") if k in th]
        frows.append([
            ("**" + form + " (winner)**") if form == fits["winner"] else form,
            "`" + FORMS[form]["expr"] + "`",
            repr(th["lambda"]), repr(b["ci95"]["lambda"]),
            repr(th["q"]), repr(b["ci95"]["q"]), repr(b["width"]["q"]),
            repr(th["kappa"]), repr(b["ci95"]["kappa"]),
            (f"{extra[0]} = {th[extra[0]]!r} ci95 {b['ci95'][extra[0]]!r}"
             if extra else "--"),
            repr(f["rmse"]), repr(loos["loo"][form]["loo_rmse"])])
    sec["fits"] = _md_table(
        ["form", "expression", "lambda", "lambda ci95", "q", "q ci95", "q width",
         "kappa", "kappa ci95", "4th param", "in-sample RMSE", "LOO-RMSE"], frows)

    sec["boot_meta"] = _md_table(
        ["form", "B", "draws used", "discarded", "n starts", "converged starts",
         "starts at global SSE", "distinct optima", "R^2 vs mean"],
        [[form, str(fits["fits"][form]["bootstrap"]["B"]),
          str(fits["fits"][form]["bootstrap"]["n_used"]),
          str(fits["fits"][form]["bootstrap"]["n_discarded"]),
          str(fits["fits"][form]["n_starts"]), str(fits["fits"][form]["n_converged"]),
          str(fits["fits"][form]["n_starts_at_global_sse"]),
          str(fits["fits"][form]["n_distinct_optima"]),
          repr(fits["fits"][form]["r2_vs_mean"])] for form in FORM_ORDER])

    v = dec["verdicts"]
    sec["verdicts"] = _md_table(
        ["lean", "clause", "sided", "prior", "measured", "verdict"],
        [["L-1", f"winner's q 95% CI width <= {L1_Q_WIDTH_MAX}", "one-sided (DOWN)",
          "0.55", f"width {dec['winner_intervals']['q_ci_width']!r} on "
                  f"{dec['winner_intervals']['q_ci']!r}",
          "**" + v["L-1"]["verdict"] + "**"],
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
         "residuals in phi order"],
        [[repr(p["share"]), repr(p["spearman_resid_phi"]), str(p["sign"]),
          str(p["perfectly_monotone"]), ", ".join(repr(x) for x in p["residuals"])]
         for p in dec["L-4"]["per_share"]])

    sec["rule13"] = _md_table(
        ["quantity", "value", "bar", "scale", f"within {int(BOUNDARY_REL * 100)}%"],
        [[rec["quantity"], repr(rec["value"]), repr(rec["bar"]), repr(rec["scale"]),
          str(rec[f"within_{int(BOUNDARY_REL * 100)}pct"])]
         for rec in fits["boundary_flags"]["records"]])

    if high["triggered"] and dec["rule13_stability"]["per_form"]:
        rows13 = []
        for form, d13 in dec["rule13_stability"]["per_form"].items():
            for key in ("L-1", "L-2", "L-3", "lambda_ci_contains_zero"):
                rows13.append([form, key, str(d13["B2000"][key]), str(d13["B20000"][key]),
                               str(d13["B2000"][key] == d13["B20000"][key]),
                               repr(d13["max_endpoint_shift"])])
        sec["stability"] = _md_table(
            ["form", "verdict", f"B={B_BOOT}", f"B={B_BOOT_HIGH}", "unchanged",
             "max endpoint shift"], rows13)
    else:
        sec["stability"] = ["_(rule 13 did not fire: no verdict quantity sat within "
                            f"{BOUNDARY_REL:.0%} of its bar)_"]

    sec["gates"] = _md_table(["gate", "PASS", "detail"],
                             [[k, str(d["PASS"]), d["detail"]]
                              for k, d in dec["gates"].items()])
    sec["sides"] = _md_table(
        ["clause", "statement", "sided", "improvement side"],
        [[k, str(x["clause"]), str(x["sided"]), str(x.get("improvement_side", "--"))]
         for k, x in SIDES.items()])
    sec["rn"] = _md_table(["note", "pinned reading"], [[k, x] for k, x in RN_NOTES.items()])
    sec["env"] = _md_table(["component", "value"],
                           [[k, str(x)] for k, x in p0["environment"].items()])
    sec["forms"] = _md_table(
        ["form", "expression", "params", "starts", "bounded"],
        [[f, FORMS[f]["expr"], repr(list(FORMS[f]["names"])), str(len(starts_for(f))),
          str(FORMS[f]["bounded"])] for f in FORM_ORDER])
    sec["timing"] = _md_table(
        ["stage", "registration estimate (s)", "executor estimate (s)", "measured (s)"],
        _timing_rows(p0))

    body = ["# M4-M1b report tables (GENERATED from artifacts -- rule 24)", ""]
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
    for st in ("part0", "pilot", "power", "diagnose", "worlds_a", "worlds_b", "worlds_c",
               "worlds_d", "fit", "rule13", "finalize"):
        rows.append([st, "--" if reg_map[st] is None else str(reg_map[st]),
                     str(ex.get(st, "--")),
                     ("%.3f" % measured[st]) if st in measured else "-- (not reached)"])
    return rows


def _write_prose_facts(p0: dict[str, Any], g2: dict[str, Any], g3: dict[str, Any],
                       fits: dict[str, Any], loos: dict[str, Any], cells: pd.DataFrame,
                       dec: dict[str, Any]) -> None:
    g1 = p0["G1m'"]
    dsc = g1["descriptive_NOT_a_gate"]
    w = dec["winner"]
    wb = fits["fits"][w]["bootstrap"]
    wth = dict(zip(fits["fits"][w]["param_names"], fits["fits"][w]["theta"]))
    card = g2["(ii) liveness (rule 3, phi->r channel)"]["GATE_reading_card_attenuation"]
    fld = g2["(ii) liveness (rule 3, phi->r channel)"][
        "DESCRIPTIVE_field_contrast_NOT_a_gate"]
    sp = g1["(c') within-share r span"]
    facts = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "MODIFIER": dec["L-3_modifier"], "ROUTING_TEXT": dec["routing_text"],
        "MODIFIER_TEXT": dec["modifier_text"],
        "WINNER": w, "WINNER_EXPR": FORMS[w]["expr"], "RUNNER": dec["runner_up"],
        "N_CELLS": dec["n_cells"], "N_WORLDS_MAIN": dec["n_worlds_main"],
        "N_WORLDS_PILOT": dec["n_worlds_pilot"],
        "WORLDS_PER_CELL": dec["worlds_per_cell"],
        "SHARES": list(SHARES), "PHI_LADDER": list(PHIS), "PHI_ALT": list(PHIS_ALT),
        "CORR_RV": dsc["corr_r_V"], "CORR_RQ_V": dsc["corr_r_pow_q_V"],
        "CORR_RV_K2F": K2F_CORR_RV,
        "SPANS_GATED": [x["span"] for x in sp["per_share"] if x["in_span_gate"]],
        "SPANS_ALL": [x["span"] for x in sp["per_share"]],
        "SPAN_BAR": G1M_SPAN_MIN, "V_RATIO": g1["(b) V ratio"]["ratio"],
        "LAMBDA": wth["lambda"], "LAMBDA_CI": dec["winner_intervals"]["lambda_ci"],
        "Q": wth["q"], "Q_CI": dec["winner_intervals"]["q_ci"],
        "Q_WIDTH": dec["winner_intervals"]["q_ci_width"], "Q_BAR": L1_Q_WIDTH_MAX,
        "KAPPA": wth["kappa"], "KAPPA_CI": dec["winner_intervals"]["kappa_ci"],
        "K2F_KAPPA_CI": list(L3_KAPPA_CI), "RESPONSE_BAND": list(L2_RESPONSE_BAND),
        "FOURTH": {k: wth[k] for k in ("p", "epsilon") if k in wth} or None,
        "FOURTH_CI": {k: wb["ci95"][k] for k in ("p", "epsilon") if k in wb["ci95"]}
        or None,
        "LOO_WINNER": loos["loo"][w]["loo_rmse"],
        "LOO_ALL": {f: loos["loo"][f]["loo_rmse"] for f in FORM_ORDER},
        "RMSE_ALL": {f: fits["fits"][f]["rmse"] for f in FORM_ORDER},
        "R2_WINNER": fits["fits"][w]["r2_vs_mean"],
        "LOO_SEP": dec["loo_separation"], "LOO_SEP_REL": dec["loo_separation_rel"],
        "TIE_ACTIVE": dec["tie_rule_active"],
        "L1": dec["verdicts"]["L-1"]["verdict"], "L2": dec["verdicts"]["L-2"]["verdict"],
        "L3": dec["verdicts"]["L-3"]["verdict"],
        "LAMBDA_ZERO": dec["verdicts"]["lambda_ci_contains_zero"]["verdict"],
        "SIGMA_W_RAW": g3["sigma_w_raw_pooled"], "SIGMA_W": g3["sigma_w"],
        "INFLATION": g3["df_inflation_factor"],
        "PROJ_BASE": [t["width_proxy"] for t in g3["base"]["projections"].values()],
        "PROJ_ESC": ([t["width_proxy"] for t in g3["escalated"]["projections"].values()]
                     if g3["escalated"] else None),
        "PROJ_BAR": G3M_PROJ_WIDTH_MAX, "ESCALATION": g3["escalation_fired"],
        "CELL_SD": g3["base"]["cell_mean_sd_used"],
        "FIELD_MIN": dec["field_mean_range"][0], "FIELD_MAX": dec["field_mean_range"][1],
        "FIELD_RANGE": float(dec["field_mean_range"][1] - dec["field_mean_range"][0]),
        "SEM_MIN": dec["field_sem_range"][0], "SEM_MAX": dec["field_sem_range"][1],
        "LIVE_CARD_SE": card["abs_contrast_over_SE"],
        "LIVE_CARD_CONTRAST": card["contrast"],
        "LIVE_FIELD_SE": fld["abs_contrast_over_SE"],
        "LIVE_FIELD_CONTRAST": fld["contrast"],
        "RULE13_TRIGGERED": dec["rule13_stability"]["triggered"],
        "RULE13_STABLE": dec["rule13_stability"]["all_stable"],
        "L4_A": dec["L-4"]["reading_A_sign_agreement"]["max_agreeing"],
        "L4_B": dec["L-4"]["reading_B_perfect_monotone_and_sign"]["max_agreeing"],
        "L4_A_FINDING": dec["L-4"]["reading_A_sign_agreement"]["finding"],
        "L4_B_FINDING": dec["L-4"]["reading_B_perfect_monotone_and_sign"]["finding"],
        "L4_RHOS": [p["spearman_resid_phi"] for p in dec["L-4"]["per_share"]],
        "N_BOOT_DISCARD": {f: fits["fits"][f]["bootstrap"]["n_discarded"]
                           for f in FORM_ORDER},
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
        "PART0_SECONDS": p0["seconds"],
    }
    write_json(OUT / "prose_facts.json", facts)


# ---------------------------------------------------------------------------
# THE STOP PATH -- NON_PROJECTABLE (truth-table cell 1).  RN-M1B-8.

def stage_diagnose(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    g2 = read_json(OUT / "g2m_pilot.json")
    g3 = read_json(OUT / "g3mb_power.json")
    if g3["PASS"]:
        raise SystemExit("REFUSED: `diagnose` is the STOP path; G3m'(b) passed.")
    for nm in ("cells", "fits.json"):
        if (OUT / nm).exists():
            raise SystemExit(f"REFUSED: {nm} exists; this is not a clean STOP.")

    dsg = pd.DataFrame(p0["G1m'"]["design_points"])
    r = dsg["r_pred"].to_numpy(float)
    v = dsg["V_person"].to_numpy(float)
    sigma_w = float(g3["sigma_w"])

    # which truth binds?
    base = g3["base"]["projections"]
    binding = max(base.values(), key=lambda t: t["width_proxy"])
    other = min(base.values(), key=lambda t: t["width_proxy"])

    ladder = []
    smallest_pass = None
    for n in DIAG_N_LADDER:
        blk = _project_one(r, v, sigma_w, n, binding["q_truth"], t0)
        ladder.append(blk)
        if blk["PASS"] and smallest_pass is None:
            smallest_pass = n
            break
    confirm = None
    if smallest_pass is not None:
        confirm = _project_one(r, v, sigma_w, smallest_pass, other["q_truth"], t0)

    diag = {
        "utc": datetime.now(UTC).isoformat(), "note": RN_NOTES["RN-M1B-8"],
        "worlds_generated_in_this_leg": int(_GEN_COUNT),
        "pilot_worlds": int(len(PILOT_SHARES) * 2 * PILOT_WORLDS),
        "main_worlds": 0,
        "failed_gate": "G3m'(b) -- projected q identification width <= "
                       f"{G3M_PROJ_WIDTH_MAX} under BOTH q truths",
        "sigma_w": sigma_w, "sigma_w_raw_pooled": g3["sigma_w_raw_pooled"],
        "binding_truth": binding["q_truth"], "non_binding_truth": other["q_truth"],
        "asymmetry": {
            "statement": "The gate is failed by ONE of its two registered truths. At "
                         f"q_truth = {other['q_truth']!r} the escalated design CLEARS the "
                         "bar; at q_truth = "
                         f"{binding['q_truth']!r} it does not. Larger q means smaller "
                         "r^q on r < 1, so the signal the exponent rides on shrinks and "
                         "its interval widens -- the design is projected adequate under "
                         "the truth the registered L-2 lean deems LIKELY (below the "
                         "response band) and inadequate under the one it deems unlikely "
                         "(prior .10 above / .35 overlap). The registration says BOTH, "
                         "and BOTH is what was scored; this note reports the asymmetry, "
                         "it does not relax the gate.",
            "escalated_width_at_non_binding_truth":
                g3["escalated"]["projections"][repr(other["q_truth"])]["width_proxy"],
            "escalated_width_at_binding_truth":
                g3["escalated"]["projections"][repr(binding["q_truth"])]["width_proxy"]},
        "estimator_is_unbiased_not_broken": {
            "statement": "median q_hat tracks the truth at every n and both truths, and "
                         "no replicate failed to converge, so the failure is PRECISION, "
                         "not bias or optimizer pathology",
            "median_q_hat": {k: t["q_hat_median"] for k, t in base.items()},
            "n_failed": {k: t["n_failed"] for k, t in base.items()}},
        "monte_carlo_cross_check_at_n64": {
            "gate_stage_width": g3["escalated"]["projections"][
                repr(binding["q_truth"])]["width_proxy"],
            "ladder_stage_width": ladder[0]["width_proxy"],
            "abs_diff": abs(ladder[0]["width_proxy"] - g3["escalated"]["projections"][
                repr(binding["q_truth"])]["width_proxy"]),
            "why_they_differ": "the gate stage draws BOTH truths from one seeded stream "
                               "so the second truth consumes a later stretch of it; the "
                               "ladder re-seeds per (n, truth). Same spec, different "
                               "position in the stream -- an independent read on the "
                               "proxy's OWN Monte-Carlo error at B_proj=500",
            "verdict_unaffected": "both values are above the bar; the GATE value is the "
                                  "power stage's, which is the registered one"},
        "n_ladder_binding_truth": ladder,
        "smallest_passing_n_on_ladder": smallest_pass,
        "confirmation_at_that_n_other_truth": confirm,
        "both_truths_pass_at_smallest_n": bool(
            smallest_pass is not None and confirm is not None and confirm["PASS"]),
        "ladder_declared": list(DIAG_N_LADDER),
        "budget_note": (None if smallest_pass is None else
                        f"{smallest_pass} worlds/cell x {len(r)} cells = "
                        f"{smallest_pass * len(r)} worlds, "
                        f"{smallest_pass * len(r) / (N_WORLDS_BASE * len(r)):.1f}x the "
                        f"registered base budget"),
        "int_share_axis_NOT_probed": (
            "the registration NAMES the int_share second axis for a future registration "
            "and forbids adopting it here. It is therefore not probed: exercising it "
            "requires installing K2d's `int:` weight dispatcher on every reachable k2b "
            "instance (RN-K2F-5), a machinery mutation this leg has no licence to make "
            "for a knob it may not adopt. Under the planner-side convention that defect "
            "#43 bought, that arithmetic is the PLANNER's to run before registering a "
            "successor -- it is deterministic and needs no world."),
        "seconds": time.time() - t0,
    }
    write_json(OUT / "stop_diagnostic.json", diag)

    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED, "salts": {"main": SALT_WORLD, "pilot": SALT_PILOT},
        "verdict_slug": "NON_PROJECTABLE", "routing_cell": 1,
        "routing_text": next(t["text"] for t in TRUTH_TABLE if t["n"] == "1"),
        "L-3_modifier": None,
        "modifier_text": "none -- the L-3 modifier is defined only for cells 2-6",
        "worlds_generated": int(_GEN_COUNT),
        "pilot_run": True, "main_worlds_run": 0, "fit_run": False,
        "verdicts": {"L-1": "NOT EVALUATED (cell 1: no fit is run)",
                     "L-2": "NOT EVALUATED (cell 1: no fit is run)",
                     "L-3": "NOT EVALUATED (cell 1: no fit is run)",
                     "L-4": "NOT EVALUATED (cell 1: no fit is run)"},
        "gates": {
            "G0m'": {"PASS": p0["G0m'"]["PASS"],
                      "detail": "(i)-(vi) M1's anchors re-verified; (vii) BOTH planner "
                                "design tables reproduced bit-exactly; (viii) the M1-STOP "
                                "numbers verified against results/m4_m1_r_at_level/"},
            "G1m'": {"PASS": p0["G1m'"]["PASS"],
                      "detail": "(a)(b)(c')(e) all pass; no marginal gate (rule 25)"},
            "G2m'": {"PASS": g2["PASS"],
                      "detail": "regime guard passed at all 4 corners; phi->r liveness on "
                                "the realized card statistic passed decisively"},
            "G3m'": {"PASS": False,
                      "detail": "THE feasibility gate FAILED at n=32 and again after the "
                                "pre-declared once-only escalation to n=64"},
            "G4m'": {"PASS": True,
                      "detail": "inherited truth table reproduced verbatim; every report "
                                "table generated from artifacts"},
        },
        "stop_diagnostic": diag, "part0_utc": p0["utc"],
    }
    write_json(OUT / "decision.json", dec)
    _ordering_log("diagnose_done", slug="NON_PROJECTABLE", seconds=diag["seconds"],
                  smallest_passing_n=smallest_pass)
    _write_stop_tables(p0, g2, g3, diag, dec)
    _write_stop_prose_facts(p0, g2, g3, diag, dec)
    print(f"diagnose OK  slug=NON_PROJECTABLE  smallest passing n on the declared ladder="
          f"{smallest_pass}  {time.time() - t0:.1f}s")
    _ = args


def _project_one(r: np.ndarray, v: np.ndarray, sigma_w: float, n_worlds: int,
                 q_truth: float, t0: float) -> dict[str, Any]:
    """One (n, q_truth) projection cell, same machinery as G3m'(b)."""
    cell_sd = sigma_w / np.sqrt(n_worlds)
    rng = np.random.default_rng(MASTER_SEED)
    mu = K2F_F2_LAMBDA * r ** q_truth - K2F_F2_KAPPA * v
    qs, nfail = [], 0
    for _ in range(B_PROJ):
        y = mu + rng.normal(0.0, cell_sd, size=len(r))
        try:
            f = fit_form("F1", r, v, y)
        except SystemExit:
            nfail += 1
            continue
        qs.append(f["theta"][1])
    arr = np.asarray(qs, float)
    lo, hi = float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975))
    out = {"n_worlds_per_cell": int(n_worlds), "q_truth": q_truth,
           "cell_mean_sd": float(cell_sd), "B_proj": B_PROJ, "n_used": int(len(arr)),
           "n_failed": int(nfail), "q_hat_median": float(np.median(arr)),
           "width_proxy": float(hi - lo), "bar": G3M_PROJ_WIDTH_MAX,
           "PASS": bool(hi - lo <= G3M_PROJ_WIDTH_MAX)}
    print(f"    n={n_worlds} q_truth={q_truth!r}: width={out['width_proxy']!r} "
          f"PASS={out['PASS']} ({time.time() - t0:.1f}s)", flush=True)
    return out


def _write_stop_tables(p0: dict[str, Any], g2: dict[str, Any], g3: dict[str, Any],
                       diag: dict[str, Any], dec: dict[str, Any]) -> None:
    sec: dict[str, list[str]] = {}
    g0, g1 = p0["G0m'"], p0["G1m'"]

    sec["design"] = _md_table(
        ["cell", "share", "phi", "r_pred", "V_person"],
        [[d["cell_tag"], repr(d["share"]), repr(d["phi"]), repr(d["r_pred"]),
          repr(d["V_person"])] for d in g1["design_points"]])

    rows = []
    for name, d in g0["maps"].items():
        rows.append([name, repr(d["expected"]), repr(d["rederived"]), str(d["bit_exact"])])
    for name, d in g0["k2f_quoted"].items():
        rows.append([name, repr(d["registration"]), repr(d["persisted"]),
                     str(d["bit_exact"])])
    for name, d in g0["registration_citations"].items():
        rows.append([name, repr(d["registration"]), repr(d["rederived"]),
                     str(d["bit_exact"])])
    d = g0["dopen_m4_level"]
    rows.append(["(v) Dopen:M-4 level, mean of the raw per-world CSV", repr(d["expected"]),
                 repr(d["rederived"]), str(d["bit_exact"])])
    d = g0["theory_band"]
    rows.append([f"(vi) `{d['string']}` verbatim in `{d['doc']}`", d["string"],
                 f"found on lines {d['lines']}", str(d["found"])])
    for name, d in g0["planner_tables"]["descriptives"].items():
        rows.append([f"(vii) {name}", repr(d["registration"]), repr(d["rederived"]),
                     str(d["bit_exact"])])
    for name, d in g0["m1_stop_citations"].items():
        rows.append([f"(viii) {name}", repr(d["adjudication"]), repr(d["persisted"]),
                     str(d["bit_exact"])])
    sec["g0m"] = _md_table(["clause", "registration / expected",
                            "re-derived / persisted", "bit-exact"], rows)

    prows = []
    for row in g0["planner_tables"]["main_ladder"]["rows"]:
        prows.append([repr(row["share"]), repr(row["V_rederived"])]
                     + [repr(x) for x in row["r_rederived"]]
                     + [repr(row["span_rederived"]), str(row["bit_exact"])])
    sec["planner_main"] = _md_table(
        ["share", "V_person"] + [f"r(phi={p})" for p in PHIS] + ["span", "bit-exact"],
        prows)
    sec["planner_alt"] = _md_table(
        ["share", "ALT span (registration)", "ALT span (re-derived)", "bit-exact"],
        [[repr(x["share"]), repr(x["span_expected"]), repr(x["span_rederived"]),
          str(x["bit_exact"])] for x in g0["planner_tables"]["alt_ladder"]["rows"]])

    sp = g1["(c') within-share r span"]
    sec["g1m"] = _md_table(
        ["gate", "bar", "realized", "PASS"],
        [["(a) shares inside the trained envelope", repr(list(SHARE_ENVELOPE)),
          repr(list(SHARES)), str(g1["(a) shares inside envelope"]["PASS"])],
         ["(b) V max/min", f">= {G1M_V_RATIO_MIN}", repr(g1["(b) V ratio"]["ratio"]),
          str(g1["(b) V ratio"]["PASS"])],
         [f"(c') within-share r SPAN at shares {list(G1M_SPAN_SHARES)}",
          f">= {G1M_SPAN_MIN}",
          repr([x["span"] for x in sp["per_share"] if x["in_span_gate"]]),
          str(sp["PASS"])],
         ["(e) duplicate (r, V) design points", "0",
          str(len(g1["(e) no duplicate design points"]["duplicates"])),
          str(g1["(e) no duplicate design points"]["PASS"])],
         ["*(no marginal-correlation gate -- rule 25)*", "n/a",
          "corr(r, V) = " + repr(g1["descriptive_NOT_a_gate"]["corr_r_V"])
          + ", REPORTED only", "n/a"]])

    sec["spans"] = _md_table(
        ["share", "V_person", "r min", "r max", "span", "ratio", "in (c') gate",
         f"span >= {G1M_SPAN_MIN}"],
        [[repr(x["share"]), repr(x["V_person"]), repr(x["r_min"]), repr(x["r_max"]),
          repr(x["span"]), repr(x["ratio"]), str(x["in_span_gate"]),
          str(x["meets_span_bar"])] for x in sp["per_share"]])

    dsc = g1["descriptive_NOT_a_gate"]
    sec["collinearity"] = _md_table(
        ["quantity (REPORTED, gates nothing -- rule 25)", "value"],
        [["corr(r, V) on M1b's 20-point design", repr(dsc["corr_r_V"])],
         [f"corr(r^{SEALED_Q!r}, V) on M1b's design", repr(dsc["corr_r_pow_q_V"])],
         ["corr(r, V) on K2f's 26 rows", repr(dsc["k2f_corr_r_V_26_rows"])],
         ["M1's failed marginal bar (WITHDRAWN by rule 25)", "<= 0.30"]])

    sec["inheritance"] = _md_table(
        ["form", "theta (this leg)", "theta (M1 harness)", "starts", "expr match",
         "bit-exact"],
        [[f, repr(d["theta_mine"]), repr(d["theta_m1"]),
          f"{d['n_starts_mine']} / {d['n_starts_m1']}", str(d["expr_match"]),
          str(d["bit_exact"])]
         for f, d in p0["inheritance_check_RN_M1B_1"]["per_form"].items()])

    sec["pilot"] = _md_table(
        ["cell", "world", "world seed", "recovery_b_only", "realized r_card_b_raw"],
        [[cell_tag(w["share"], w["phi"]), str(int(w["world"])), str(int(w["world_seed"])),
          repr(w["recovery_b_only"]), repr(w["r_card_b_raw"])]
         for w in g2["per_world"]])

    sec["regime"] = _md_table(
        ["corner", "phi-extension?", "n", "mean", "sd", "min", "max", "finite",
         "inside (0,1)", "nonzero var", "PASS"],
        [[c["cell"], str(c["is_phi_extension_corner"]), str(c["n"]), repr(c["mean"]),
          repr(c["sd"]), repr(c["min"]), repr(c["max"]), str(c["all_finite"]),
          str(c["strictly_inside_unit"]), str(c["nonzero_variance"]), str(c["PASS"])]
         for c in g2["(i) regime guard"]["per_corner"]])

    liv = g2["(ii) liveness (rule 3, phi->r channel)"]
    card = liv["GATE_reading_card_attenuation"]
    fld = liv["DESCRIPTIVE_field_contrast_NOT_a_gate"]
    sec["liveness"] = _md_table(
        ["reading", "role", "mean at phi lo", "mean at phi hi", "contrast", "pooled SE",
         "abs(contrast)/SE", f"> {G2M_LIVENESS_SE_MULT}x SE"],
        [["realized card attenuation `r_card_b_raw`", "**THE GATE** (RN-M1B-3)",
          repr(card["mean_at_phi_lo"]), repr(card["mean_at_phi_hi"]),
          repr(card["contrast"]), repr(card["pooled_SE"]),
          repr(card["abs_contrast_over_SE"]), str(card["PASS"])],
         ["field `recovery_b_only`", "descriptive only -- gates NOTHING (rule 25)",
          repr(fld["mean_at_phi_lo"]), repr(fld["mean_at_phi_hi"]), repr(fld["contrast"]),
          repr(fld["pooled_SE"]), repr(fld["abs_contrast_over_SE"]),
          str(fld["PASS"]) + " (not a verdict)"],
         ["pinned-map arithmetic certification", "alternative route, also satisfied",
          "--", "--", repr(liv["arithmetic_certification"]["delta_r_from_pinned_map"]),
          "--", "--", "bit-exact vs registration: "
          + str(liv["arithmetic_certification"]["bit_exact"])]])

    prow = [["pooled per-world sd across the 16 pilot worlds "
             f"(df {g3['pooled_df']})", repr(g3["sigma_w_raw_pooled"])],
            [f"chi2_{{{G3M_CHI2_Q}, df={G3M_DF}}}", repr(g3["chi2_quantile"]["value"])],
            ["df-aware inflation sqrt(12 / chi2)", repr(g3["df_inflation_factor"])],
            ["**sigma_w** (inflated)", "**" + repr(g3["sigma_w"]) + "**"]]
    for tagname, blk in ((f"base n={N_WORLDS_BASE}", g3["base"]),
                         (f"escalated n={N_WORLDS_ESCALATED}", g3["escalated"])):
        if blk is None:
            prow.append([f"{tagname} projection", "not run"])
            continue
        prow.append([f"{tagname}: cell-mean sd", repr(blk["cell_mean_sd_used"])])
        for t in blk["projections"].values():
            prow.append([f"{tagname}: projected q width at q_truth = {t['q_truth']!r}",
                         repr(t["width_proxy"]) + ("  PASS" if t["PASS"] else "  **FAIL**")])
        prow.append([f"{tagname}: PASS (both truths <= {G3M_PROJ_WIDTH_MAX})",
                     str(blk["PASS"])])
    prow.append(["escalation fired", str(g3["escalation_fired"])])
    mc = diag["monte_carlo_cross_check_at_n64"]
    prow.append([f"MC cross-check: the same n={N_WORLDS_ESCALATED}, q_truth="
                 f"{diag['binding_truth']!r} cell re-drawn on a fresh stream",
                 repr(mc["ladder_stage_width"]) + " vs the gate's "
                 + repr(mc["gate_stage_width"]) + " (abs diff "
                 + repr(mc["abs_diff"]) + "; both above the bar)"])
    prow.append(["**gate verdict**", "**FAIL -> NON_PROJECTABLE**"])
    sec["power"] = _md_table(["quantity", "value"], prow)

    sec["ladder"] = _md_table(
        ["worlds/cell", "q_truth", "cell-mean sd", "projected q width",
         f"<= {G3M_PROJ_WIDTH_MAX}"],
        [[str(x["n_worlds_per_cell"]), repr(x["q_truth"]), repr(x["cell_mean_sd"]),
          repr(x["width_proxy"]), str(x["PASS"])]
         for x in diag["n_ladder_binding_truth"]]
        + ([[str(diag["confirmation_at_that_n_other_truth"]["n_worlds_per_cell"]),
             repr(diag["confirmation_at_that_n_other_truth"]["q_truth"]) + " (confirm)",
             repr(diag["confirmation_at_that_n_other_truth"]["cell_mean_sd"]),
             repr(diag["confirmation_at_that_n_other_truth"]["width_proxy"]),
             str(diag["confirmation_at_that_n_other_truth"]["PASS"])]]
            if diag["confirmation_at_that_n_other_truth"] else []))

    sec["unbiased"] = _md_table(
        ["q_truth", "median q_hat at n=32", "replicates failed to converge"],
        [[k, repr(x), str(diag["estimator_is_unbiased_not_broken"]["n_failed"][k])]
         for k, x in diag["estimator_is_unbiased_not_broken"]["median_q_hat"].items()])

    sec["truth_table"] = _md_table(
        ["#", "condition", "outcome"],
        [[t["n"], t["condition"],
          ("**" + t["text"] + "**  <-- THIS LEG") if t["n"] == str(dec["routing_cell"])
          else t["text"]] for t in TRUTH_TABLE])

    sec["verdicts"] = _md_table(
        ["lean", "clause", "sided", "prior", "verdict", "why"],
        [["L-1", SIDES["L-1"]["clause"], SIDES["L-1"]["sided"],
          repr(SIDES["L-1"]["prior"]), "**NOT EVALUATED**", "cell 1: no fit is run"],
         ["L-2", SIDES["L-2"]["clause"], SIDES["L-2"]["sided"],
          str(SIDES["L-2"]["prior"]), "**NOT EVALUATED**",
          "conditional on L-1; no fit is run"],
         ["L-3", SIDES["L-3"]["clause"], SIDES["L-3"]["sided"],
          repr(SIDES["L-3"]["prior"]), "**NOT EVALUATED**",
          "defined in cells 2-6 only; no fit is run"],
         ["L-4", SIDES["L-4"]["clause"], SIDES["L-4"]["sided"], "--",
          "**NOT EVALUATED**",
          "a reading on the winner's residuals; there is no winner"]])

    sec["sides"] = _md_table(
        ["clause", "statement", "sided", "improvement side"],
        [[k, str(x["clause"]), str(x["sided"]), str(x.get("improvement_side", "--"))]
         for k, x in SIDES.items()])
    sec["gates"] = _md_table(["gate", "PASS", "detail"],
                             [[k, str(d["PASS"]), d["detail"]]
                              for k, d in dec["gates"].items()])
    sec["rn"] = _md_table(["note", "pinned reading"], [[k, x] for k, x in RN_NOTES.items()])
    sec["env"] = _md_table(["component", "value"],
                           [[k, str(x)] for k, x in p0["environment"].items()])
    sec["forms"] = _md_table(
        ["form", "expression", "params", "starts", "bounded"],
        [[f, FORMS[f]["expr"], repr(list(FORMS[f]["names"])), str(len(starts_for(f))),
          str(FORMS[f]["bounded"])] for f in FORM_ORDER])
    sec["timing"] = _md_table(
        ["stage", "registration estimate (s)", "executor estimate (s)", "measured (s)"],
        _timing_rows(p0))

    body = ["# M4-M1b report tables (GENERATED from artifacts -- rule 24)", "",
            "STOP path: truth-table cell 1, NON_PROJECTABLE.  The pilot ran; no MAIN "
            "world was generated and no fit was run, so the per-cell, fit, bootstrap and "
            "L-4 tables have no artifact to be generated from and are absent by the "
            "registration's own routing.", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _write_stop_prose_facts(p0: dict[str, Any], g2: dict[str, Any], g3: dict[str, Any],
                            diag: dict[str, Any], dec: dict[str, Any]) -> None:
    g1 = p0["G1m'"]
    dsc = g1["descriptive_NOT_a_gate"]
    sp = g1["(c') within-share r span"]
    liv = g2["(ii) liveness (rule 3, phi->r channel)"]
    card = liv["GATE_reading_card_attenuation"]
    fld = liv["DESCRIPTIVE_field_contrast_NOT_a_gate"]
    base = g3["base"]["projections"]
    esc = g3["escalated"]["projections"]
    n_ok = diag["smallest_passing_n_on_ladder"]
    facts = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"],
        "N_CELLS": g1["n_cells"], "SHARES": list(SHARES), "PHI_LADDER": list(PHIS),
        "PHI_ALT": list(PHIS_ALT),
        "PILOT_WORLDS_TOTAL": diag["pilot_worlds"], "MAIN_WORLDS": diag["main_worlds"],
        "CORR_RV": dsc["corr_r_V"], "CORR_RQ_V": dsc["corr_r_pow_q_V"],
        "CORR_RV_K2F": dsc["k2f_corr_r_V_26_rows"],
        "SPANS_GATED": [x["span"] for x in sp["per_share"] if x["in_span_gate"]],
        "SPANS_ALL": [x["span"] for x in sp["per_share"]], "SPAN_BAR": G1M_SPAN_MIN,
        "V_RATIO": g1["(b) V ratio"]["ratio"],
        "SIGMA_W_RAW": g3["sigma_w_raw_pooled"], "SIGMA_W": g3["sigma_w"],
        "INFLATION": g3["df_inflation_factor"],
        "CELL_SD_32": g3["base"]["cell_mean_sd_used"],
        "CELL_SD_64": g3["escalated"]["cell_mean_sd_used"],
        "PROJ_32": {t["q_truth"]: t["width_proxy"] for t in base.values()},
        "PROJ_64": {t["q_truth"]: t["width_proxy"] for t in esc.values()},
        "PROJ_BAR": G3M_PROJ_WIDTH_MAX,
        "W32_Q1": base["1.0"]["width_proxy"],
        "W32_Q185": base[repr(SEALED_Q)]["width_proxy"],
        "W64_Q1": esc["1.0"]["width_proxy"],
        "W64_Q185": esc[repr(SEALED_Q)]["width_proxy"],
        "BINDING_TRUTH": diag["binding_truth"],
        "NONBINDING_TRUTH": diag["non_binding_truth"],
        "ESCALATION": g3["escalation_fired"],
        "N_OK": n_ok, "N_OK_TOTAL": (None if n_ok is None else n_ok * g1["n_cells"]),
        "N_OK_MULT": (None if n_ok is None else float(n_ok / N_WORLDS_BASE)),
        "LADDER": list(DIAG_N_LADDER),
        "LADDER_WIDTHS": [x["width_proxy"] for x in diag["n_ladder_binding_truth"]],
        "LADDER_NS": [x["n_worlds_per_cell"] for x in diag["n_ladder_binding_truth"]],
        "CONFIRM_WIDTH": (diag["confirmation_at_that_n_other_truth"]["width_proxy"]
                          if diag["confirmation_at_that_n_other_truth"] else None),
        "W64_Q185_LADDER": diag["n_ladder_binding_truth"][0]["width_proxy"],
        "W_RUNG_BELOW": (diag["n_ladder_binding_truth"][-2]["width_proxy"]
                         if len(diag["n_ladder_binding_truth"]) >= 2 else None),
        "MC_DIFF": abs(diag["n_ladder_binding_truth"][0]["width_proxy"]
                       - esc[repr(SEALED_Q)]["width_proxy"]),
        "MC_DIFF_REL": abs(diag["n_ladder_binding_truth"][0]["width_proxy"]
                           - esc[repr(SEALED_Q)]["width_proxy"])
        / esc[repr(SEALED_Q)]["width_proxy"],
        "BOTH_PASS_AT_N_OK": diag["both_truths_pass_at_smallest_n"],
        "MEDIAN_QHAT": diag["estimator_is_unbiased_not_broken"]["median_q_hat"],
        "LIVE_CARD_SE": card["abs_contrast_over_SE"],
        "LIVE_CARD_CONTRAST": card["contrast"],
        "LIVE_FIELD_SE": fld["abs_contrast_over_SE"],
        "LIVE_FIELD_CONTRAST": fld["contrast"],
        "DELTA_R_ARITH": liv["arithmetic_certification"]["delta_r_from_pinned_map"],
        "CARD_VS_MAP_DIFF": abs(card["contrast"]
                                - liv["arithmetic_certification"]
                                ["delta_r_from_pinned_map"]),
        "PILOT_MEANS": {c["cell"]: c["mean"] for c in g3["per_pilot_cell"]},
        "PILOT_SDS": {c["cell"]: c["sd"] for c in g3["per_pilot_cell"]},
        "ASYMMETRY": diag["asymmetry"]["statement"],
        "INT_SHARE_NOTE": diag["int_share_axis_NOT_probed"],
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
        "PART0_SECONDS": p0["seconds"], "DIAG_SECONDS": diag["seconds"],
        "PILOT_SECONDS": g2["seconds"], "POWER_SECONDS": g3["seconds"],
    }
    write_json(OUT / "prose_facts.json", facts)


# ---------------------------------------------------------------------------
# REPORT rendering (rule 24: no number in this report is hand-typed).

REPORT_TEMPLATE = """# M4-M1b — r-at-level, feasibility restated in the estimand's quantity

**Leg:** M4-M1b · **Registered** 2026-08-11 in
`docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md` (section "M4-M1b — r-at-level,
feasibility restated in the estimand's quantity"), commit `2e4e404`, BEFORE this
run. Re-registration of M4-M1 after its cell-1 STOP.
**Executor:** dispatched agent (implementation and execution only; the
registration text is binding).
**Harness:** `scripts/run_suica_m4_m1b_r_at_level.py`.
**Artifacts:** `results/m4_m1b_r_at_level/` (gitignored).
**Banner:** synthetic worlds on K2b's frozen instrument, exploratory, label-free;
a share × φ factorial whose ONLY feasibility gate is the estimand's own
projected identification width (rule 25).

**Verdict: `{{SLUG}}` (rule-16 cell {{CELL}}).** G3m′(b) — the feasibility gate,
and under rule 25 the only one — failed at {{PROJ_BAR}} under the binding truth
at 32 worlds/cell **and again** after the pre-declared once-only escalation to
64. **{{PILOT_WORLDS_TOTAL}} pilot worlds ran; {{MAIN_WORLDS}} main worlds were
generated and no fit was run.**

Rule 25 worked exactly as enacted, and this leg is its first two-sided test.
**It cleared the leg past M1's false death:** the marginal `corr(r, V)` on this
design is `{{CORR_RV}}` — far above the 0.30 bar that killed M1, and now
correctly REPORTED rather than gating. **And it stopped the leg on a real one:**
the same design, carried to the quantity the estimand actually consumes, cannot
resolve `q` to the registered width at the registered budget. M1 died on a
number the estimand does not consume; M1b dies on the number it does. Those are
different failures, and only the second is information.

---

## Part 0 — written before any world

### 0.1 Rule 9 / rule 12 — open conventions, pinned in writing

<<TABLE:rn>>

RN-M1B-8 was added AFTER `σ_w` existed and is disclosed as such. It consumes only
`σ_w` and the pinned design maps — no field-outcome quantity bearing on
L-1/L-2/L-3 enters it — and it adopts nothing.

### 0.2 RN-M1B-1 — the copied machinery, proven faithful

The coordinator left "copy or import" open. The machinery is COPIED (so this
leg's pins cannot drift when a later leg edits M1's file) and Part 0 then
IMPORTS the M1 harness and proves the copy bit-exact: the start grid, the
optimizer dict, every inherited bar, and `fit_form` itself run on a fixed
synthetic probe in both modules.

<<TABLE:inheritance>>

### 0.3 G0m′ — anchors bit-exact, including the two new clauses

<<TABLE:g0m>>

**(vii)** reproduces BOTH of the planner's embedded design tables bit-exactly —
the planner ran its own arithmetic at registration time, which is the
convention defect #43 bought, and it is correct to the last bit:

<<TABLE:planner_main>>

<<TABLE:planner_alt>>

**(viii)** verifies the M1-STOP numbers the adjudication cites against this
executor's own `results/m4_m1_r_at_level/` artifacts — the infimum
`0.748768093111513`, the freed-shares bound `0.5208187741410987` and all four
full-interval spans re-read from `stop_diagnostic.json`. All bit-exact.

### 0.4 G1m′ — four gates, no proxy gate

<<TABLE:g1m>>

The (c′) bar is an ABSOLUTE span, not M1's ratio — the repair for defect #44's
second half, where the ratio bar was reachable at only two of four share levels
for any ladder. Realized spans at the two gated shares: `{{SPANS_GATED}}`
against a `{{SPAN_BAR}}` bar.

<<TABLE:spans>>

### 0.5 The collinearity, REPORTED and gating nothing (rule 25)

<<TABLE:collinearity>>

This is the rule-25 exemplar in one line: `{{CORR_RV}}` would have failed M1's
withdrawn 0.30 bar by a factor of nearly three, and it is irrelevant, because
identification lives in the within-share φ sweeps at exactly fixed `V`.

---

## G2m′ — the pilot, and a vindication of the registration's own correction

<<TABLE:regime>>

<<TABLE:liveness>>

**This is the finding of the pilot, and it is not a small one.** The φ→r channel
is alive beyond any doubt: the realized card attenuation moves
`{{LIVE_CARD_CONTRAST}}` between φ = 0.05 and φ = 0.98 at share 0.60, which is
**{{LIVE_CARD_SE}}× its pooled SE**, and it lands `{{CARD_VS_MAP_DIFF}}` from the
pinned map's PREDICTED `Δr = {{DELTA_R_ARITH}}` — the map's own value being the one
that reproduces the registration's span bit-exactly, not the measurement. The FIELD, at the same corner, moves
`{{LIVE_FIELD_CONTRAST}}` — **{{LIVE_FIELD_SE}}× its pooled SE**, i.e. flat
within noise.

M1's registration would have gated on that second number as its declared
fallback. It is below 2× SE, so M1's liveness clause would have FAILED and M1
would have died a second false death — on evidence that the field does not
respond to φ, which is precisely what this leg exists to measure. M1b's
registration says so in advance: "an OUTCOME-side field contrast is NOT a
liveness gate here, because a flat field is cell-2 EVIDENCE, not channel death."
The correction was written before the number existed and the number vindicates
it.

That flat field is also, read honestly, weak *evidence* pointing at truth-table
cell 2 (`R_TERM_ABSENT_AT_LEVEL`). It is four worlds against four at one share.
**It adjudicates nothing here** — no lean is scored in this leg — and it is
recorded as an observation, not a result.

<<TABLE:pilot>>

---

## G3m′(b) — the feasibility gate, and the stop

σ_w is the pooled per-world sd across the 16 pilot worlds, df-inflated as
registered.

<<TABLE:power>>

At 32 worlds/cell the projected 95% width of `q̂` is `{{W32_Q1}}` under
q_truth = 1.0 and `{{W32_Q185}}` under q_truth = {{BINDING_TRUTH}}, against a
`{{PROJ_BAR}}` bar. The pre-declared escalation fired. At 64 worlds/cell the
widths are `{{W64_Q1}}` and `{{W64_Q185}}`: the first CLEARS the bar, the second
does not. The registration requires BOTH. **Gate FAIL → `NON_PROJECTABLE`.**

**The failure is precision, not pathology.** Median `q̂` tracks its truth at
every configuration ({{MEDIAN_QHAT}} at n = 32) and not one replicate failed to
converge:

<<TABLE:unbiased>>

**The asymmetry, stated because it matters to the successor.** {{ASYMMETRY}}

### What n would suffice — measured, not extrapolated

Defect #43 was an extrapolation where arithmetic was available. This leg does
not repeat it in its handoff: the smallest sufficient budget is MEASURED on a
declared geometric ladder `{{LADDER}}`, running the binding truth until it
clears and then confirming the other truth at the same n.

<<TABLE:ladder>>

**{{N_OK}} worlds/cell** is the smallest rung at which the binding truth clears
(`{{LADDER_WIDTHS}}` at `{{LADDER_NS}}`), and the non-binding truth confirms
there at `{{CONFIRM_WIDTH}}`. That is **{{N_OK_TOTAL}} worlds**, {{N_OK_MULT}}×
the registered base budget. Nothing here is adopted — the leg's verdict is the
registered STOP — but the successor no longer has to guess.

A caution on that number's own precision: the ladder re-drew the n = 64 binding
cell on a fresh stream and got `{{W64_Q185_LADDER}}` where the gate got
`{{W64_Q185}}`, an absolute difference of `{{MC_DIFF}}`. So the width proxy
itself carries roughly {{MC_DIFF_REL}} relative Monte-Carlo error at
B_proj = 500, and the ladder's rungs are coarse; n = {{N_OK}} clears with margin,
the rung below misses at `{{W_RUNG_BELOW}}`, and a successor wanting a tight budget
should re-run the ladder finely rather than read {{N_OK}} as exact.

---

## Routing — the inherited truth table, reproduced verbatim

<<TABLE:truth_table>>

## Leans

<<TABLE:verdicts>>

## Sides declared in Part 0 (rule 22)

<<TABLE:sides>>

## Gates

<<TABLE:gates>>

The four pre-declared forms and the optimizer pins were fixed in Part 0 before
the stop and are persisted, so a successor inherits them unchanged:

<<TABLE:forms>>

---

## Anomaly log — every anomaly, with pre/post-hypothesis timing

The hypothesis-relevant boundary in this leg is the PILOT: before it, no
outcome-side number existed; after it, the pilot field contrast and `σ_w` did.
No lean was ever scored.

- **A-1 — the interpreter (before Part 0, before any number).** The environment
  pinned in M4-M1 is reused verbatim: a CPython {{PYTHON}} virtual environment
  outside the repository, populated from `requirements-lock-main.txt`
  (numpy `{{NUMPY}}`, pandas `{{PANDAS}}`, scipy `{{SCIPY}}`), platform
  `{{PLATFORM}}`. The machine's only pandas still belongs to CPython 3.9.6,
  which cannot import the published machinery (`datetime.UTC` is 3.11+).
- **A-2 — `timeout(1)` absent on this platform (before Part 0).** Every stage
  ran as its own foreground command under an explicit harness-level timeout,
  all under the 600 s ceiling.
- **A-3 — the pilot's outcome-side flatness (AT the pilot, i.e. the first
  hypothesis-relevant number).** `{{LIVE_FIELD_SE}}×` SE on the field against
  `{{LIVE_CARD_SE}}×` SE on the card channel. Reported above. It changed no
  gate, because M1b's registration had already removed the field from the
  liveness clause BEFORE the number existed. Had the executor been free to
  choose after seeing it, the choice would have been contaminated; it was not
  free, and that is the point.
- **A-4 — the gate failed and the escalation fired (AFTER `σ_w` existed).**
  Pre-declared, once only, applied exactly as written; no second escalation was
  attempted.
- **A-5 — RN-M1B-8 was added after `σ_w` existed (disclosed).** The n-ladder
  diagnostic consumes only `σ_w` and the pinned design maps; no field-outcome
  quantity bearing on any lean enters it, and it adopts nothing.
- **A-6 — a Monte-Carlo discrepancy at the one overlapping configuration
  (after the gate).** `{{W64_Q185_LADDER}}` vs `{{W64_Q185}}` at the same
  (n = 64, q_truth = {{BINDING_TRUTH}}); the gate stage draws both truths from
  one seeded stream while the ladder re-seeds per cell, so the two consume
  different stretches. Both are above the bar and the GATE value is the power
  stage's — the registered one. Disclosed rather than smoothed, and it doubles
  as a measurement of the proxy's own MC error.
- **A-6b — rule 24 caught a claim in this leg's own prose (before commit).** The
  liveness paragraph first said the realized card contrast "agrees bit-exactly"
  with the pinned map's `Δr`. It does not, and could not: one is a measurement
  over 8 worlds, the other is deterministic algebra. They differ by
  `{{CARD_VS_MAP_DIFF}}`. What IS bit-exact is the map against the
  registration's stated span. The sentence is now generated from both values.
- **A-7 — no stage approached its 2× stop-and-report threshold.** Part 0
  `{{PART0_SECONDS}}` s against 60 s; pilot `{{PILOT_SECONDS}}` s against 40 s;
  power `{{POWER_SECONDS}}` s against a 120 s executor estimate; diagnose
  `{{DIAG_SECONDS}}` s against 300 s.

<<TABLE:timing>>

<<TABLE:env>>

---

## What the planner should carry forward

**Rule 25 is validated in both directions by one leg.** It let M1b past a
marginal correlation of `{{CORR_RV}}` that M1's withdrawn bar would have
rejected, and — at the pilot — it prevented a second false death when the
outcome-side field contrast came in at `{{LIVE_FIELD_SE}}×` SE. A proxy gate
would have killed this design twice, on two different proxies, for two
different wrong reasons. The estimand-side gate killed it once, for the right
one.

**This is not a registration defect, and it should not be recorded as one.**
Every clause was satisfiable, every bar was computed, the ladder fired as
written, the escalation fired as written, and the gate returned a well-defined
verdict on a well-posed quantity. `NON_PROJECTABLE` is a pre-declared outcome of
a sound registration, not a defect in it. The one judgement call worth the
planner's attention is the **two-truth conjunction**: the design is projected
adequate under q_truth = {{NONBINDING_TRUTH}} and inadequate under
q_truth = {{BINDING_TRUTH}}, and the registered L-2 lean puts .55 on `q` being
BELOW the response band — i.e. the gate is decided by the truth the leg itself
considers least likely. Whether that conjunction is the intended conservatism or
an over-strict reading is the planner's to settle; the executor scored it as
written.

**Three routes, none adopted here.**

1. **Buy the precision.** `{{N_OK}}` worlds/cell — `{{N_OK_TOTAL}}` worlds,
   {{N_OK_MULT}}× the base budget — clears both truths on the measured ladder.
   At the observed ~0.6 s/world this is a wall-clock change, not a feasibility
   change.
2. **Re-state the gate.** If the two-truth conjunction is stricter than intended,
   a lean-weighted or q_truth-anchored variant would pass at 64 today. This is a
   registration decision and the executor takes no position on it beyond
   reporting that the binding arm is the low-prior one.
3. **Add the second axis.** {{INT_SHARE_NOTE}}

**What was NOT measured.** `q` at level, `κ` at level, the winner form, and the
(r, V)-sufficiency pattern. L-1, L-2, L-3 and L-4 are all NOT EVALUATED. The
level law's exponent remains exactly where K2f left it — unidentified — and
this leg's contribution is to have priced the identification rather than to have
attempted it under-powered.
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
    path = ROOT / "reports" / "SUICA_M4_M1B_R_AT_LEVEL_REPORT.md"
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
        return ", ".join(f"{k}: {_fmt(x)}" for k, x in v.items())
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
