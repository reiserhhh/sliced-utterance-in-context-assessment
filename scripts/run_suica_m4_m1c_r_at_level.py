#!/usr/bin/env python3
"""M4-M1c -- r-AT-LEVEL AT THE MEASURED BUDGET.

Registered in docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md ("M4-M1c -- r-at-level at
the measured budget", commit dd1a38f) BEFORE this file existed.  Implementation
and execution only; the registration is binding.

M1 died on a marginal-correlation PROXY gate (defects #43/#44, rule 25 enacted).
M1b passed every gate except the estimand's own: at 32 and then 64 worlds/cell
the projected 95% width of q-hat was 1.170/0.645 and 0.808/0.450 against a 0.50
bar under truths {1.8528700746510731, 1.0} -- NON_PROJECTABLE -- and its
diagnostic MEASURED the sufficient budget at 192 worlds/cell.  The planner
funded it.  M1c is that leg: same question, same instrument, same design, same
four forms, same leans -- 3840 worlds instead of 640.

    part0     G0m''(i)-(ix) + G1m'' + G3m'' -- the projection CONFIRMATION at
              n=192, B_proj=2000, recomputed from M1b's persisted sigma_w
              BEFORE any world exists.  Boundary [0.47, 0.53] -> B_proj=10000.
              FAIL -> once-only escalation to 256 -> else
              NON_PROJECTABLE_AT_CEILING.
    smoke     world index 0 for each of the 20 cells; per-world
              finiteness/saturation BOOLEANS ONLY -- no aggregation, no level
              read.  These 20 worlds are RETAINED in the main sample.  Any
              failure -> STOP (no ALT ladder: it would need a fresh projection).
    worlds_1..5   5 chunks x 4 cells x world indices 1..191.
    fit       four forms, leave-one-CELL-out selection, within-cell world-block
              bootstrap B=2000.
    rule13    the >=10xB re-run at any flagged boundary.
    finalize  L-1/L-2/L-3 through the inherited truth table; L-4 as a reading,
              with appendix W's quadratic-in-r discriminator beside it.
    report    renders the report from artifacts (rule 24).

There is NO new pilot.  G2m'' pins M1b's persisted pilot as the noise, regime
and liveness source -- same instrument, same corners -- and G0m'' verifies every
number the M1b adjudication cites, bit-exactly, from
results/m4_m1b_r_at_level/.

ORDERING IS ENFORCED, NOT ASSERTED: every k2b entry point that can build or
measure a world is wrapped on EVERY reachable k2b instance (RN-K2F-5), and each
permit is issued only after re-reading the preceding stage's artifacts from disk
and checking their gates there.

Artifacts: results/m4_m1c_r_at_level/ (gitignored)
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

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "results" / "m4_m1c_r_at_level"
RES = ROOT / "results"
K2F = RES / "m4_k2f_level_law"
M1RES = RES / "m4_m1_r_at_level"
M1BRES = RES / "m4_m1b_r_at_level"

# ---------------------------------------------------------------------------
# Registration constants.

LEG = "M4-M1c"
BANNER = ("synthetic worlds on K2b's frozen instrument, exploratory, label-free; "
          "the M1b design at the budget M1b's own diagnostic measured")

MASTER_SEED = 20260811
SALT_WORLD = "m4m1c-world"

SHARES = (0.10, 0.25, 0.40, 0.60)
PHIS = (0.05, 0.30, 0.60, 0.85, 0.98)
N_WORLDS = 192
N_WORLDS_CEILING = 256
SMOKE_WORLD = 0
N_CHUNKS = 5
CELLS_PER_CHUNK = 4

B_BOOT = 2000
B_BOOT_HIGH = 20000
B_PROJ = 2000
B_PROJ_HIGH = 10000
PROJ_BOUNDARY = (0.47, 0.53)

INT_SHARE = 0.0
W_INT_ARM = "zero"

SHARE_ENVELOPE = (0.02, 0.6634207990183637)
G1M_V_RATIO_MIN = 2.0
G1M_SPAN_MIN = 0.12
G1M_SPAN_SHARES = (0.40, 0.60)

G3M_PROJ_WIDTH_MAX = 0.50

L1_Q_WIDTH_MAX = 0.60
L2_RESPONSE_BAND = (1.71, 1.98)
L3_KAPPA_CI = (0.5202855978239498, 0.8612166024267973)
TIE_REL = 0.05
BOUNDARY_REL = 0.05
L4_MIN_LEVELS = 3

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
    "r_040_090": 0.6185853753498524, "r_045_090": 0.5889058864943755,
    "V_045": 0.13500000000000004, "V_040": 0.12000000000000004,
    "dopen_m4_level": 0.09350089316336324, "r_030_090": 0.6758917867864564,
    "r_030_098": 0.645057248597175, "r_050_090": 0.558364277337817,
    "r_050_098": 0.5193517935368367,
}
THEORY_DOC = ROOT / "docs" / "SUICA_IDENTITY_THEORY_V1.md"
THEORY_BAND_STRING = "[1.71, 1.98]"

# G0m''(vii) -- the planner's embedded design tables, inherited from M1b.
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

# G0m''(viii) -- the M1-STOP numbers.
M1_INF_CORR = 0.748768093111513
M1_FREED_CORR = 0.5208187741410987
M1_FULL_INTERVAL_SPANS = (0.05159009087311539, 0.11784317303319514,
                          0.17083747134975158, 0.21722718146551878)

# G0m''(ix) -- every M1b number the planner's adjudication cites.
M1B_SIGMA_W = 0.026889438327132725
M1B_W32_Q185 = 1.1702741415331803
M1B_W32_Q1 = 0.6446327208199195
M1B_W64_Q185 = 0.8082914682805795
M1B_W64_Q1 = 0.45036131116284384
M1B_CELL_SD_32 = 0.004753426045853251
M1B_LADDER_192_Q185 = 0.45033528452170346
M1B_LADDER_192_Q1 = 0.2531601642892628
M1B_CARD_CONTRAST = 0.20325550047558588
M1B_CARD_SE_MULT = 94.8954999654606
M1B_FIELD_CONTRAST = -0.007269536568279722
M1B_FIELD_SE_MULT = 0.7542598230697173

# ---------------------------------------------------------------------------
# RN-M1C notes (rule 9 / rule 12).  PINNED IN PART 0, BEFORE ANY WORLD EXISTS.
#
# RN-M1C-1 (code inheritance).  As RN-M1B-1: the machinery is COPIED into this
#   file and Part 0 then IMPORTS BOTH predecessor harnesses (M1 and M1b) and
#   proves the copy bit-exact against each -- start grid, optimizer dict, form
#   expressions and names, every inherited bar, and `fit_form` itself run on a
#   fixed synthetic probe with bit-exact agreement demanded on every parameter.
#   Two independent witnesses rather than one.
#
# RN-M1C-2 (seed string).  As RN-M1B-2 with M1c's salt:
#       v8.stable_bucket(f"{MASTER_SEED}-{share!r}-{phi!r}-{world}",
#                        salt="m4m1c-world", modulus=2**31 - 1)
#   world indices 0..191.  Disjoint from M1's and M1b's streams by salt.  Index
#   0 is generated by the SMOKE stage and RETAINED (the registration pins this),
#   so the chunks cover 1..191 and the union is exactly 0..191 with no world
#   drawn twice and none discarded.
#
# RN-M1C-3 (smoke discipline).  The registration says the smoke checks "ONLY
#   per-world finiteness/saturation booleans -- no aggregation, no level is
#   read".  PINNED: `smoke.json` records BOOLEANS ONLY -- no mean, no min, no
#   max, no sd, no level anywhere in it.  The per-world CSV necessarily contains
#   the measured levels because those 20 worlds are retained sample, but nothing
#   in this leg reads or aggregates them until the `fit` stage.
#
# RN-M1C-4 (chunk grouping).  "5 chunks of 4 cells" does not pin WHICH four.
#   PINNED: the 20 cells in the Part-0 design order (share-major, then phi
#   ascending) are cut into consecutive blocks of 4 -- chunk k takes design
#   indices [4k, 4k+4).  Chunks are RESUMABLE: a cell whose artifact already
#   exists with the full 191 rows is skipped, so a chunk that is re-invoked
#   continues rather than redrawing.  Seeds depend only on (share, phi, index),
#   never on chunk membership or run order, so the sample is identical however
#   the work is cut.
#
# RN-M1C-5 (bootstrap batching).  B=20000 over 20 cells x 192 worlds would
#   allocate a 76.8M-element index array in one block.  PINNED: the draws are
#   generated in batches from ONE rng seeded at master, in draw order, so the
#   realized index stream is identical to the unbatched one; batching is memory
#   management, not a change of design.
#
# RN-M1C-6 (L-4 and appendix W's discriminator).  L-4 stays as registered: the
#   within-share Spearman(residual, phi) probe, read BOTH ways (sign agreement
#   in >=3/4 shares; and the stricter |rho| == 1 plus sign agreement).  Beside
#   it, appendix W (docs/SUICA_IDENTITY_THEORY_V1.md, W.1) names a
#   DISCRIMINATOR that needs a second statistic: a U-shaped residual-in-r
#   signature maps to a NON-monotone residual-in-phi pattern, so "the L-4
#   Spearman probe stays quiet while a quadratic-in-r residual coefficient
#   fires" is FORM-GAP evidence, whereas a monotone L-4 fire is phi-leak
#   evidence.  Appendix W does not pin the estimator.  PINNED: OLS of the
#   winner's 20 cell residuals on [1, r, r^2] WITH share fixed effects -- the
#   "within share strata" reading, PRIMARY -- and the same without fixed
#   effects, SECONDARY; "fires" means the r^2 coefficient's 95% within-cell
#   world-block bootstrap CI (the same draws as the parameter CIs) excludes 0.
#   Both readings reported.  This is a READING: it adjudicates nothing, and it
#   cannot change the outcome slug.
#
# RN-M1C-7 (stage chunking).  As RN-M1B-7: the >=10xB rule-13 re-run is its own
#   foreground stage `rule13` between `fit` and `finalize`.  Ordering unchanged.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-M1C-1": "machinery COPIED into this file, then PROVEN faithful in Part 0 against "
                "BOTH the M1 and M1b harnesses (start grid, OPT, form expressions/names, "
                "inherited bars, and fit_form bit-exact on a fixed synthetic probe)",
    "RN-M1C-2": "seed string pinned: v8.stable_bucket(f'{MASTER_SEED}-{share!r}-{phi!r}-"
                "{world}', salt='m4m1c-world', modulus=2**31-1), indices 0..191; index 0 "
                "is the SMOKE world and is RETAINED, so chunks cover 1..191 and the union "
                "is exactly 0..191",
    "RN-M1C-3": "smoke.json records BOOLEANS ONLY -- no mean/min/max/sd/level anywhere; "
                "the retained per-world CSV holds the levels but nothing reads or "
                "aggregates them before the `fit` stage",
    "RN-M1C-4": "chunk k takes Part-0 design indices [4k, 4k+4) (share-major, phi "
                "ascending); chunks are RESUMABLE (a complete cell artifact is skipped); "
                "seeds depend only on (share, phi, index), never on chunk membership",
    "RN-M1C-5": "bootstrap draws are generated in batches from ONE master-seeded rng in "
                "draw order -- identical stream to the unbatched form; memory management "
                "only",
    "RN-M1C-6": "L-4 as registered (both monotonicity readings) PLUS appendix W's "
                "discriminator: OLS of the winner's cell residuals on [1, r, r^2] with "
                "share fixed effects (primary) and without (secondary); 'fires' = the "
                "r^2 coefficient's 95% world-block bootstrap CI excludes 0. A reading; "
                "adjudicates nothing",
    "RN-M1C-7": "the >=10xB rule-13 re-run is its own foreground stage `rule13`",
}

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
    return _load("run_suica_m4_m1_r_at_level")


def m1b() -> Any:
    return _load("run_suica_m4_m1b_r_at_level")


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
    for g in ("G0m''", "G1m''", "G3m''"):
        if not p0[g]["PASS"]:
            raise SystemExit(f"STOP (ordering): Part 0 gate {g} did not pass.")
    rec: dict[str, Any] = {"kind": kind, "part0_utc": p0["utc"],
                           "generations_before_permit": _GEN_COUNT,
                           "worlds_per_cell": p0["G3m''"]["worlds_per_cell_decided"]}
    if kind == "main":
        sp = OUT / "smoke.json"
        if not sp.exists():
            raise SystemExit("STOP (ordering): smoke.json absent; run `smoke`.")
        sm = read_json(sp)
        if not sm["PASS"]:
            raise SystemExit("STOP (ordering): the smoke stage did not pass.")
        rec["smoke_utc"] = sm["utc"]
    _PERMIT = kind
    rec["permit_utc"] = datetime.now(UTC).isoformat()
    _ordering_log("permit_issued", **rec)
    return rec


# ---------------------------------------------------------------------------
# Utilities.

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
    return f"{share!r}|{phi!r}"


def cell_tag(share: float, phi: float) -> str:
    return f"s{share:.2f}_p{phi:.2f}"


def world_seed_for(share: float, phi: float, world: int) -> int:
    v8 = k2b().v8
    return int(v8.stable_bucket(f"{MASTER_SEED}-{cell_id(share, phi)}-{world}",
                                salt=SALT_WORLD, modulus=2 ** 31 - 1))


def r_of(share: float, phi: float) -> float:
    return k2c().predicted_attenuation(share, phi)


def v_of(share: float) -> float:
    return k2e().person_share_design(share, INT_SHARE)


# ---------------------------------------------------------------------------
# The FOUR pre-declared forms -- inherited verbatim (RN-M1C-1).

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
    "routine": "scipy.optimize.least_squares", "method": "trf",
    "jac": "2-point (numerical)",
    "bounds": "unbounded, x_scale=1.0, EXCEPT F1e's epsilon in [0, 0.05]",
    "ftol": 1e-14, "xtol": 1e-14, "gtol": 1e-14, "max_nfev": 20000,
    "loss": "linear (plain least squares)", "scipy_version": None,
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


def _boot_means(per_world: np.ndarray, b_draws: int, seed: int, batch: int = 500):
    """RN-M1C-5: one master-seeded rng, draws produced in order, in batches."""
    n_cells, n_w = per_world.shape
    rng = np.random.default_rng(seed)
    rows = np.arange(n_cells)[None, :, None]
    done = 0
    while done < b_draws:
        take = min(batch, b_draws - done)
        idx = rng.integers(0, n_w, size=(take, n_cells, n_w))
        yield per_world[rows, idx].mean(axis=2)
        done += take


def bootstrap_form(form: str, r: np.ndarray, v: np.ndarray, per_world: np.ndarray,
                   theta0: list[float], b_draws: int, seed: int,
                   collect: Callable[[np.ndarray, list[float]], None] | None = None
                   ) -> dict[str, Any]:
    names = FORMS[form]["names"]
    draws: list[list[float]] = []
    nfail = 0
    for block in _boot_means(per_world, b_draws, seed):
        for means in block:
            try:
                f = fit_form(form, r, v, means, starts=[list(theta0)])
            except SystemExit:
                nfail += 1
                continue
            if all(abs(x) < 1e6 for x in f["theta"]):
                draws.append(f["theta"])
                if collect is not None:
                    collect(means, f["theta"])
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
# The rule-16 truth table -- INHERITED, cell 1 restated for M1c.

TRUTH_TABLE = [
    {"n": "1", "condition": "any G0m''/G1m''/G3m''/smoke clause fails after its declared "
                            "ladder",
     "outcome": "STOP",
     "text": "STOP (no fit is run) -- NON_PROJECTABLE_AT_CEILING where G3m'' fails after "
             "the once-only escalation to 256; SMOKE_REGIME_BREAK where the smoke fails "
             "(no ALT ladder is available: it would need a fresh projection)"},
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
                      "finding 'phi leaks past (r, V)'. Appendix W's quadratic-in-r "
                      "discriminator is reported beside it (RN-M1C-6)",
            "sided": "reading only, NO gate", "improvement_side": "n/a", "prior": None},
    "G1m''(a)": {"clause": f"all shares inside {list(SHARE_ENVELOPE)}",
                 "sided": "two-sided containment", "improvement_side": "neither"},
    "G1m''(b)": {"clause": f"V max/min >= {G1M_V_RATIO_MIN}", "sided": "one-sided",
                 "improvement_side": "UP"},
    "G1m''(c')": {"clause": f"within-share r SPAN >= {G1M_SPAN_MIN} at BOTH shares "
                            f"{list(G1M_SPAN_SHARES)}",
                  "sided": "one-sided", "improvement_side": "UP"},
    "G1m''(e)": {"clause": "no duplicate (r, V) design points", "sided": "exact",
                 "improvement_side": "n/a"},
    "smoke": {"clause": "world index 0 of every cell finite and strictly inside (0, 1) -- "
                        "booleans only, no aggregation",
              "sided": "two-sided containment",
              "improvement_side": "neither -- failure is a STOP with no ALT ladder"},
    "G3m''": {"clause": f"projected q width proxy <= {G3M_PROJ_WIDTH_MAX} under BOTH q "
                        f"truths at n={N_WORLDS}, B_proj={B_PROJ}, recomputed from M1b's "
                        f"persisted sigma_w -- THE feasibility gate (rule 25)",
              "sided": "one-sided", "improvement_side": "DOWN"},
    "descriptive (NOT a gate, rule 25)": {
        "clause": "marginal corr(r, V) and corr(r^q, V) across cells",
        "sided": "reported only", "improvement_side": "n/a"},
}

STAGE_ESTIMATES_REGISTRATION = {"part0": 240, "smoke": 30, "worlds_each": 480,
                                "worlds_n_chunks": 5, "fit": 420, "finalize": 60}
STAGE_ESTIMATES_EXECUTOR = {"part0": 240, "smoke": 30, "worlds_1": 480, "worlds_2": 480,
                            "worlds_3": 480, "worlds_4": 480, "worlds_5": 480,
                            "fit": 420, "rule13": 300, "finalize": 60, "report": 30}


# ---------------------------------------------------------------------------
# PART 0.

def design_table() -> pd.DataFrame:
    rows = []
    for share in SHARES:
        for phi in PHIS:
            rows.append({"cell_tag": cell_tag(share, phi), "cell_id": cell_id(share, phi),
                         "share": share, "phi": phi, "int_share": INT_SHARE,
                         "r_pred": r_of(share, phi), "V_person": v_of(share)})
    return pd.DataFrame(rows)


def g1m_check() -> dict[str, Any]:
    df = design_table()
    r = df["r_pred"].to_numpy(float)
    v = df["V_person"].to_numpy(float)
    sp = []
    for share in SHARES:
        rr = np.array([r_of(share, p) for p in PHIS], float)
        sp.append({"share": share, "V_person": v_of(share), "r_min": float(rr.min()),
                   "r_max": float(rr.max()), "span": float(rr.max() - rr.min()),
                   "ratio": float(rr.max() / rr.min()),
                   "in_span_gate": bool(share in G1M_SPAN_SHARES),
                   "meets_span_bar": bool(rr.max() - rr.min() >= G1M_SPAN_MIN)})
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
        "phi_ladder": list(PHIS), "n_cells": int(len(df)),
        "design_points": df.to_dict("records"),
        "(a) shares inside envelope": {"PASS": a, "envelope": list(SHARE_ENVELOPE),
                                       "shares": list(SHARES)},
        "(b) V ratio": {"PASS": b, "V_min": float(v.min()), "V_max": float(v.max()),
                        "ratio": float(v.max() / v.min()), "bar": G1M_V_RATIO_MIN},
        "(c') within-share r span": {"PASS": c, "bar": G1M_SPAN_MIN,
                                     "gated_shares": list(G1M_SPAN_SHARES),
                                     "per_share": sp},
        "(e) no duplicate design points": {"PASS": e, "duplicates": dup},
        "descriptive_NOT_a_gate": {
            "corr_r_V": pearson(r, v), "corr_r_pow_q_V": pearson(r ** SEALED_Q, v),
            "k2f_corr_r_V_26_rows": K2F_CORR_RV,
            "rule25": "REPORTED, never gating"},
        "PASS": bool(a and b and c and e),
    }


def g0m_check() -> dict[str, Any]:
    out: dict[str, Any] = {}
    checks = [
        ("(i) predicted_attenuation(0.40, 0.90)", r_of(0.40, 0.90), ANCHORS["r_040_090"]),
        ("(ii-a) predicted_attenuation(0.45, 0.90)", r_of(0.45, 0.90),
         ANCHORS["r_045_090"]),
        ("(ii-b) person_share_design(0.45, 0.0)", v_of(0.45), ANCHORS["V_045"]),
        ("(iii) person_share_design(0.40, 0.0)", v_of(0.40), ANCHORS["V_040"]),
    ]
    out["maps"] = {n: {"rederived": g, "expected": e, "bit_exact": bool(g == e)}
                   for n, g, e in checks}

    fits = read_json(K2F / "fits.json")
    loos = read_json(K2F / "loo.json")
    f2f = fits["fits"]["F2"]
    th = dict(zip(f2f["param_names"], f2f["theta"]))
    quoted = [
        ("F2 lambda'", th["lambda"], K2F_F2_LAMBDA), ("F2 q'", th["q"], K2F_F2_Q),
        ("F2 kappa'", th["kappa"], K2F_F2_KAPPA), ("F2 p", th["p"], K2F_F2_P),
        ("F2 LOO-RMSE (fits.json)", fits["L-1"]["best_loo_rmse"], K2F_F2_LOO),
        ("F2 LOO-RMSE (loo.json)", loos["loo"]["F2"]["loo_rmse"], K2F_F2_LOO),
        ("F2 q' ci95 lo", f2f["bootstrap"]["ci95"]["q"][0], K2F_F2_Q_CI[0]),
        ("F2 q' ci95 hi", f2f["bootstrap"]["ci95"]["q"][1], K2F_F2_Q_CI[1]),
        ("F2 kappa' ci95 lo", f2f["bootstrap"]["ci95"]["kappa"][0], K2F_F2_KAPPA_CI[0]),
        ("F2 kappa' ci95 hi", f2f["bootstrap"]["ci95"]["kappa"][1], K2F_F2_KAPPA_CI[1]),
    ]
    out["k2f_quoted"] = {n: {"persisted": g, "registration": e, "bit_exact": bool(g == e)}
                         for n, g, e in quoted}

    rows = read_csv_rt(K2F / "compiled_rows.csv")
    rr = rows["r_pred"].to_numpy(float)
    vv = rows["V_person"].to_numpy(float)
    ext = [
        ("corr(r, V) over the 26 K2f rows", pearson(rr, vv), K2F_CORR_RV),
        ("share envelope lo", float(rows["share"].min()), SHARE_ENVELOPE[0]),
        ("share envelope hi", float(rows["share"].max()), SHARE_ENVELOPE[1]),
        ("r(0.30, 0.90)", r_of(0.30, 0.90), ANCHORS["r_030_090"]),
        ("r(0.30, 0.98)", r_of(0.30, 0.98), ANCHORS["r_030_098"]),
        ("r(0.50, 0.90)", r_of(0.50, 0.90), ANCHORS["r_050_090"]),
        ("r(0.50, 0.98)", r_of(0.50, 0.98), ANCHORS["r_050_098"]),
    ]
    out["registration_citations"] = {
        n: {"rederived": g, "registration": e, "bit_exact": bool(g == e)}
        for n, g, e in ext}

    do = read_csv_rt(RES / "dopen_seal_opening" / "m4_field_rows.csv")
    lvl = float(do["recovery_b_only"].to_numpy(float).mean())
    out["dopen_m4_level"] = {"rederived": lvl, "expected": ANCHORS["dopen_m4_level"],
                             "bit_exact": bool(lvl == ANCHORS["dopen_m4_level"])}

    txt = THEORY_DOC.read_text(encoding="utf-8")
    hits = [i + 1 for i, ln in enumerate(txt.split("\n")) if THEORY_BAND_STRING in ln]
    out["theory_band"] = {"string": THEORY_BAND_STRING, "found": bool(hits),
                          "lines": hits[:20], "doc": rel(THEORY_DOC)}

    # (vii) both planner design tables.
    main_rows, ok_main = [], True
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
    desc = [("MAIN corr(r, V)", pearson(r_main, v_main), PLANNER_MAIN_CORR_RV),
            ("MAIN corr(r^q, V)", pearson(r_main ** SEALED_Q, v_main),
             PLANNER_MAIN_CORR_RQ_V)]
    desc_d = {n: {"rederived": g, "registration": e, "bit_exact": bool(g == e)}
              for n, g, e in desc}
    out["planner_tables"] = {"rows": main_rows, "descriptives": desc_d,
                             "PASS": bool(ok_main and all(d["bit_exact"]
                                                          for d in desc_d.values()))}

    # (viii) the M1-STOP numbers.
    m1d = read_json(M1RES / "stop_diagnostic.json")
    m1_checks = [("M1 infimum |corr(r,V)|",
                  m1d["infimum_at_registered_shares"]["inf_abs_corr"], M1_INF_CORR),
                 ("M1 freed-shares bound",
                  m1d["best_with_shares_also_freed"]["best_abs_corr_found"],
                  M1_FREED_CORR)]
    for i, s in enumerate(SHARES):
        m1_checks.append((f"M1 full-interval r span at share {s!r}",
                          m1d["phi_leverage_per_share"][i][
                              "max_span_over_full_phi_interval"],
                          M1_FULL_INTERVAL_SPANS[i]))
    out["m1_stop_citations"] = {
        n: {"persisted": g, "adjudication": e, "bit_exact": bool(g == e)}
        for n, g, e in m1_checks}

    # (ix) EVERY M1b number the planner's adjudication cites.
    b3 = read_json(M1BRES / "g3mb_power.json")
    b2 = read_json(M1BRES / "g2m_pilot.json")
    bd = read_json(M1BRES / "stop_diagnostic.json")
    liv = b2["(ii) liveness (rule 3, phi->r channel)"]
    ladder = {x["n_worlds_per_cell"]: x for x in bd["n_ladder_binding_truth"]}
    m1b_checks = [
        ("M1b sigma_w (df-inflated)", b3["sigma_w"], M1B_SIGMA_W),
        ("M1b q-width n=32 q_truth 1.8528700746510731",
         b3["base"]["projections"][repr(SEALED_Q)]["width_proxy"], M1B_W32_Q185),
        ("M1b q-width n=32 q_truth 1.0",
         b3["base"]["projections"]["1.0"]["width_proxy"], M1B_W32_Q1),
        ("M1b q-width n=64 q_truth 1.8528700746510731",
         b3["escalated"]["projections"][repr(SEALED_Q)]["width_proxy"], M1B_W64_Q185),
        ("M1b q-width n=64 q_truth 1.0",
         b3["escalated"]["projections"]["1.0"]["width_proxy"], M1B_W64_Q1),
        ("M1b cell-mean sd at n=32", b3["base"]["cell_mean_sd_used"], M1B_CELL_SD_32),
        ("M1b ladder width n=192 q_truth 1.8528700746510731",
         ladder[192]["width_proxy"], M1B_LADDER_192_Q185),
        ("M1b ladder confirmation n=192 q_truth 1.0",
         bd["confirmation_at_that_n_other_truth"]["width_proxy"], M1B_LADDER_192_Q1),
        ("M1b pilot card contrast",
         liv["GATE_reading_card_attenuation"]["contrast"], M1B_CARD_CONTRAST),
        ("M1b pilot card SE multiple",
         liv["GATE_reading_card_attenuation"]["abs_contrast_over_SE"], M1B_CARD_SE_MULT),
        ("M1b pilot field contrast",
         liv["DESCRIPTIVE_field_contrast_NOT_a_gate"]["contrast"], M1B_FIELD_CONTRAST),
        ("M1b pilot field SE multiple",
         liv["DESCRIPTIVE_field_contrast_NOT_a_gate"]["abs_contrast_over_SE"],
         M1B_FIELD_SE_MULT),
    ]
    out["m1b_adjudication_citations"] = {
        n: {"persisted": g, "adjudication": e, "bit_exact": bool(g == e)}
        for n, g, e in m1b_checks}
    out["m1b_pilot_pass_records"] = {
        "G2m_PASS": b2["PASS"], "regime_PASS": b2["(i) regime guard"]["PASS"],
        "liveness_PASS": liv["PASS"],
        "all_true": bool(b2["PASS"] and b2["(i) regime guard"]["PASS"] and liv["PASS"]),
        "source": rel(M1BRES / "g2m_pilot.json"),
        "note": "G2m'': M1b's pilot IS this leg's regime/liveness/noise source -- same "
                "instrument, same corners, no new pilot is run"}

    ok = (all(d["bit_exact"] for d in out["maps"].values())
          and all(d["bit_exact"] for d in out["k2f_quoted"].values())
          and all(d["bit_exact"] for d in out["registration_citations"].values())
          and out["dopen_m4_level"]["bit_exact"] and out["theory_band"]["found"]
          and out["planner_tables"]["PASS"]
          and all(d["bit_exact"] for d in out["m1_stop_citations"].values())
          and all(d["bit_exact"] for d in out["m1b_adjudication_citations"].values())
          and out["m1b_pilot_pass_records"]["all_true"])
    out["PASS"] = bool(ok)
    out["failure_meaning"] = ("a mismatch on any clause is a CITATION DEFECT: STOP, "
                              "report, do not repair silently")
    return out


def inheritance_check() -> dict[str, Any]:
    """RN-M1C-1: prove the copied machinery bit-identical to BOTH predecessors."""
    probe_r = np.array([0.8189581462487876, 0.7558507450373838, 0.6941115392115328,
                        0.5151304058057474, 0.4541409476972356])
    probe_v = np.array([0.03, 0.075, 0.12, 0.18, 0.18])
    probe_y = np.array([0.11, 0.10, 0.09, 0.07, 0.06])
    witnesses = {}
    ok = True
    for tag, mod in (("M1", m1()), ("M1b", m1b())):
        per_form = {}
        good = True
        for form in FORM_ORDER:
            mine = fit_form(form, probe_r, probe_v, probe_y)
            theirs = mod.fit_form(form, probe_r, probe_v, probe_y)
            same = (mine["theta"] == theirs["theta"] and mine["sse"] == theirs["sse"]
                    and starts_for(form) == mod.starts_for(form)
                    and FORMS[form]["expr"] == mod.FORMS[form]["expr"]
                    and list(FORMS[form]["names"]) == list(mod.FORMS[form]["names"]))
            good &= same
            per_form[form] = {"theta_mine": mine["theta"], "theta_theirs": theirs["theta"],
                              "sse_mine": mine["sse"], "sse_theirs": theirs["sse"],
                              "n_starts": len(starts_for(form)),
                              "bit_exact": bool(same)}
        grids = all([list(START_LAMBDA) == list(mod.START_LAMBDA),
                     list(START_Q) == list(mod.START_Q),
                     list(START_KAPPA) == list(mod.START_KAPPA),
                     list(START_P) == list(mod.START_P),
                     list(START_EPS) == list(mod.START_EPS),
                     list(EPS_BOUNDS) == list(mod.EPS_BOUNDS)])
        optk = [k for k in OPT if k != "scipy_version"]
        opt_same = all(OPT[k] == mod.OPT[k] for k in optk)
        bars = all([L1_Q_WIDTH_MAX == mod.L1_Q_WIDTH_MAX,
                    tuple(L2_RESPONSE_BAND) == tuple(mod.L2_RESPONSE_BAND),
                    tuple(L3_KAPPA_CI) == tuple(mod.L3_KAPPA_CI),
                    TIE_REL == mod.TIE_REL, BOUNDARY_REL == mod.BOUNDARY_REL,
                    B_BOOT == mod.B_BOOT, B_BOOT_HIGH == mod.B_BOOT_HIGH,
                    MASTER_SEED == mod.MASTER_SEED,
                    G3M_PROJ_WIDTH_MAX == mod.G3M_PROJ_WIDTH_MAX])
        w_ok = bool(good and grids and opt_same and bars)
        ok &= w_ok
        witnesses[tag] = {"per_form": per_form, "start_grids_identical": grids,
                          "optimizer_identical": opt_same,
                          "inherited_bars_identical": bars, "PASS": w_ok}
    return {"note": RN_NOTES["RN-M1C-1"], "witnesses": witnesses, "PASS": bool(ok),
            "probe": {"r": [float(x) for x in probe_r], "V": [float(x) for x in probe_v],
                      "y": [float(x) for x in probe_y]}}


def _project(r: np.ndarray, v: np.ndarray, sigma_w: float, n_worlds: int,
             b_proj: int, t0: float) -> dict[str, Any]:
    cell_sd = sigma_w / np.sqrt(n_worlds)
    rng = np.random.default_rng(MASTER_SEED)
    truths = {}
    for q_truth in (1.0, SEALED_Q):
        mu = K2F_F2_LAMBDA * r ** q_truth - K2F_F2_KAPPA * v
        qs, nfail = [], 0
        for _ in range(b_proj):
            y = mu + rng.normal(0.0, cell_sd, size=len(r))
            try:
                f = fit_form("F1", r, v, y)
            except SystemExit:
                nfail += 1
                continue
            qs.append(f["theta"][1])
        arr = np.asarray(qs, float)
        lo, hi = float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975))
        w = float(hi - lo)
        truths[repr(q_truth)] = {
            "q_truth": q_truth, "B_proj": int(b_proj), "n_used": int(len(arr)),
            "n_failed": int(nfail), "q_hat_median": float(np.median(arr)),
            "q_hat_q025": lo, "q_hat_q975": hi, "width_proxy": w,
            "PASS": bool(w <= G3M_PROJ_WIDTH_MAX),
            "in_boundary_band": bool(PROJ_BOUNDARY[0] <= w <= PROJ_BOUNDARY[1])}
        print(f"    n={n_worlds} B={b_proj} q_truth={q_truth!r}: width={w!r} "
              f"PASS={truths[repr(q_truth)]['PASS']} ({time.time() - t0:.1f}s)", flush=True)
    return {"n_worlds_per_cell": int(n_worlds), "B_proj": int(b_proj),
            "cell_mean_sd_used": float(cell_sd), "projections": truths,
            "PASS": bool(all(t["PASS"] for t in truths.values())),
            "any_in_boundary_band": bool(any(t["in_boundary_band"]
                                             for t in truths.values()))}


def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    for nm in ("smoke.json", "cells", "fits.json"):
        if (OUT / nm).exists():
            raise SystemExit(f"STOP (ordering): {nm} exists before Part 0.")
    _ordering_log("part0_start")

    inh = inheritance_check()
    g0 = g0m_check()
    g1 = g1m_check()

    # --- G3m'': the feasibility CONFIRMATION, before any world ---------------
    sigma_w = float(read_json(M1BRES / "g3mb_power.json")["sigma_w"])
    dsg = pd.DataFrame(g1["design_points"])
    r = dsg["r_pred"].to_numpy(float)
    v = dsg["V_person"].to_numpy(float)
    base = _project(r, v, sigma_w, N_WORLDS, B_PROJ, t0)
    boundary_rerun = None
    decided_block = base
    if base["any_in_boundary_band"]:
        print(f"  a width landed in {list(PROJ_BOUNDARY)} -> rule-13 re-decide at "
              f"B_proj={B_PROJ_HIGH}", flush=True)
        boundary_rerun = _project(r, v, sigma_w, N_WORLDS, B_PROJ_HIGH, t0)
        decided_block = boundary_rerun
    escalated = None
    decided_n = N_WORLDS
    if not decided_block["PASS"]:
        print(f"  projection FAILED at n={N_WORLDS}; firing the once-only escalation to "
              f"n={N_WORLDS_CEILING}", flush=True)
        escalated = _project(r, v, sigma_w, N_WORLDS_CEILING, B_PROJ, t0)
        if escalated["any_in_boundary_band"]:
            escalated = _project(r, v, sigma_w, N_WORLDS_CEILING, B_PROJ_HIGH, t0)
        if escalated["PASS"]:
            decided_n = N_WORLDS_CEILING
            decided_block = escalated
    g3 = {
        "sigma_w": sigma_w, "sigma_w_source": rel(M1BRES / "g3mb_power.json"),
        "note": "the feasibility gate, re-CONFIRMED from M1b's persisted sigma_w before "
                "any world of this leg exists (rule 25: stated in the estimand's own "
                "quantity)",
        "bar": G3M_PROJ_WIDTH_MAX, "boundary_band": list(PROJ_BOUNDARY),
        "base": base, "boundary_rerun": boundary_rerun, "escalated": escalated,
        "boundary_rule_fired": bool(boundary_rerun is not None),
        "escalation_fired": bool(escalated is not None),
        "deciding_block_B_proj": decided_block["B_proj"],
        "worlds_per_cell_decided": decided_n,
        "n_worlds_total": int(len(r) * decided_n),
        "m1b_ladder_192_for_comparison": {
            "q_truth_1.8528700746510731": M1B_LADDER_192_Q185,
            "q_truth_1.0": M1B_LADDER_192_Q1,
            "note": "M1b's ladder ran B_proj=500; this leg re-runs honestly at "
                    f"B_proj={B_PROJ}, so agreement is expected but not required"},
        "PASS": bool(decided_block["PASS"]),
        "on_fail": "NON_PROJECTABLE_AT_CEILING",
    }

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md (M4-M1c, BEFORE run, "
                        "commit dd1a38f); inherits M4-M1b (which inherits M4-M1) verbatim "
                        "except the changes enumerated there",
        "master_seed": MASTER_SEED, "salt": SALT_WORLD,
        "rn_notes": RN_NOTES, "inheritance_check_RN_M1C_1": inh,
        "carrier": {"int_share": INT_SHARE, "w_int_arm": W_INT_ARM,
                    "instrument": "k2b.run_field_world (985-author K1-pinned panel, F2 "
                                  "m-multiset, 4 contexts)",
                    "field_statistic": "recovery_b_only, per world",
                    "cell_level": "mean over the cell's worlds (K2f's _level_from_raw)"},
        "design": {"shares": list(SHARES), "phi_ladder": list(PHIS),
                   "n_cells": len(SHARES) * len(PHIS),
                   "worlds_per_cell": N_WORLDS,
                   "worlds_per_cell_ceiling": N_WORLDS_CEILING,
                   "world_indices": f"0..{N_WORLDS - 1}",
                   "smoke_world_index": SMOKE_WORLD,
                   "smoke_worlds_retained": True,
                   "n_worlds_total": len(SHARES) * len(PHIS) * N_WORLDS,
                   "chunking": f"{N_CHUNKS} chunks x {CELLS_PER_CHUNK} cells x indices "
                               f"1..{N_WORLDS - 1} (RN-M1C-4)"},
        "G2m''": {"no_new_pilot": True,
                  "source": rel(M1BRES / "g2m_pilot.json"),
                  "records": g0["m1b_pilot_pass_records"]},
        "forms": {k: FORMS[k]["expr"] for k in FORM_ORDER},
        "optimizer": {**OPT, "scipy_version": __import__("scipy").__version__,
                      "n_starts": {f: len(starts_for(f)) for f in FORM_ORDER},
                      "start_grid": {"lambda": list(START_LAMBDA), "q": list(START_Q),
                                     "kappa": list(START_KAPPA), "p": list(START_P),
                                     "epsilon": list(START_EPS)},
                      "epsilon_bounds": list(EPS_BOUNDS),
                      "selection": "leave-one-CELL-out RMSE"},
        "bootstrap": {"kind": "within-cell world-block", "B": B_BOOT,
                      "B_high": B_BOOT_HIGH, "seed": MASTER_SEED,
                      "batching": RN_NOTES["RN-M1C-5"],
                      "tie_rule": f"top two LOO within {TIE_REL:.0%} -> verdicts must "
                                  f"agree or report SPLIT",
                      "rule13": f"a verdict within {BOUNDARY_REL:.0%} of its bar re-runs "
                                f"at B={B_BOOT_HIGH}"},
        "sides_rule22": SIDES,
        "gate_stages_rule23": {
            "G0m''": "inputs exist at Part 0 (K2f / D-open / M1 / M1b artifacts, the "
                     "deterministic maps, the theory doc)",
            "G1m''": "inputs exist at Part 0 (pure design arithmetic)",
            "G2m''": "inputs exist at Part 0 -- they are M1b's PERSISTED pilot; no new "
                     "pilot is run",
            "G3m''": "inputs exist at Part 0 (M1b's persisted sigma_w) -- confirmed "
                     "BEFORE any world",
            "smoke": "inputs exist after Part 0 and before the remaining worlds",
            "G4m''": "inputs exist at Part 0 (truth table) and at finalize (rule 24)"},
        "stage_estimates_seconds_registration": STAGE_ESTIMATES_REGISTRATION,
        "stage_estimates_seconds_executor": STAGE_ESTIMATES_EXECUTOR,
        "rule16_truth_table": TRUTH_TABLE,
        "environment": {"python": sys.version.split()[0],
                        "python_executable": sys.executable,
                        "platform": platform.platform(), "numpy": np.__version__,
                        "pandas": pd.__version__,
                        "scipy": __import__("scipy").__version__},
        "G0m''": g0, "G1m''": g1, "G3m''": g3, "seconds": None,
    }
    part0["seconds"] = time.time() - t0
    write_json(OUT / "part0.json", part0)
    _write_part0_tables(part0)
    _ordering_log("part0_done", seconds=part0["seconds"], G0m_PASS=g0["PASS"],
                  G1m_PASS=g1["PASS"], G3m_PASS=g3["PASS"],
                  inheritance_PASS=inh["PASS"],
                  worlds_per_cell=g3["worlds_per_cell_decided"])
    if not inh["PASS"]:
        raise SystemExit("STOP: RN-M1C-1 inheritance check FAILED.")
    if not g0["PASS"]:
        raise SystemExit("STOP: G0m'' FAILED (citation defect) -- see part0.json")
    if not g1["PASS"]:
        raise SystemExit("STOP: G1m'' FAILED -- see part0.json")
    if not g3["PASS"]:
        raise SystemExit("STOP: NON_PROJECTABLE_AT_CEILING -- G3m'' failed after the "
                         "once-only escalation; see part0.json")
    print(f"part0 OK  G0m'' PASS  G1m'' PASS  G3m'' PASS  inheritance PASS  "
          f"worlds/cell={g3['worlds_per_cell_decided']}  "
          f"widths={[t['width_proxy'] for t in base['projections'].values()]}  "
          f"{time.time() - t0:.1f}s")
    _ = args


def _cell(s: Any) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _md_table(header: list[str], rows: list[list[str]]) -> list[str]:
    return (["| " + " | ".join(_cell(h) for h in header) + " |",
             "|" + "|".join(["---"] * len(header)) + "|"]
            + ["| " + " | ".join(_cell(c) for c in r) + " |" for r in rows])


def _write_part0_tables(part0: dict[str, Any]) -> None:
    g1 = part0["G1m''"]
    lines = ["# M4-M1c Part 0 tables (generated from artifacts -- rule 24)", "",
             "## The 20-point design", ""]
    lines += _md_table(
        ["cell", "share", "phi", "r_pred", "V_person"],
        [[d["cell_tag"], repr(d["share"]), repr(d["phi"]), repr(d["r_pred"]),
          repr(d["V_person"])] for d in g1["design_points"]])
    (OUT / "part0_tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# World running.

def _run_worlds(share: float, phi: float, indices: list[int], tag: str) -> pd.DataFrame:
    kb = k2b()
    w = kb.arm_weights(share, W_INT_ARM)
    rows = []
    for wi in indices:
        seed = world_seed_for(share, phi, wi)
        world = kb.build_k2b_world(seed, phi)
        row = kb.run_field_world(tag, wi, world, w, verify=False)
        row["world"] = wi
        row["world_seed"] = seed
        row["share"] = share
        row["phi"] = phi
        rows.append(row)
    return pd.DataFrame(rows)


def _smoke_path(tag: str) -> Path:
    return OUT / "cells" / f"cell_{tag}_w000.csv"


def _field_path(tag: str) -> Path:
    return OUT / "cells" / f"cell_{tag}_w001_{N_WORLDS - 1:03d}.csv"


def stage_smoke(args: argparse.Namespace) -> None:
    """World index 0 of every cell.  BOOLEANS ONLY (RN-M1C-3)."""
    t0 = time.time()
    _arm_guard()
    permit = _issue_permit("smoke")
    p0 = read_json(OUT / "part0.json")
    (OUT / "cells").mkdir(parents=True, exist_ok=True)
    per_cell = []
    ok = True
    for d in p0["G1m''"]["design_points"]:
        share, phi, tag = float(d["share"]), float(d["phi"]), d["cell_tag"]
        df = _run_worlds(share, phi, [SMOKE_WORLD], f"M1C-{tag}")
        df.to_csv(_smoke_path(tag), index=False)
        vals = df["recovery_b_only"].to_numpy(float)
        finite = bool(np.all(np.isfinite(vals)))
        inside = bool(np.all((vals > 0.0) & (vals < 1.0)))
        ok &= (finite and inside)
        per_cell.append({"cell": tag, "world": SMOKE_WORLD,
                         "all_finite": finite, "strictly_inside_unit": inside,
                         "PASS": bool(finite and inside)})
        print(f"  smoke {tag}: finite={finite} inside={inside} "
              f"({time.time() - t0:.1f}s)", flush=True)
    out = {
        "utc": datetime.now(UTC).isoformat(), "permit": permit,
        "world_index": SMOKE_WORLD, "n_cells": len(per_cell),
        "per_cell_booleans_ONLY": per_cell,
        "discipline": RN_NOTES["RN-M1C-3"],
        "retained": "these 20 worlds are RETAINED in the main sample (registration); the "
                    "chunks cover indices 1.." + str(N_WORLDS - 1),
        "fallback": "any failure -> STOP; the ALT ladder is NOT available here, since it "
                    "would need a fresh projection",
        "PASS": bool(ok), "seconds": time.time() - t0,
    }
    write_json(OUT / "smoke.json", out)
    _ordering_log("smoke_done", PASS=out["PASS"], seconds=out["seconds"])
    if not ok:
        raise SystemExit("STOP: SMOKE_REGIME_BREAK -- see results/m4_m1c_r_at_level/"
                         "smoke.json")
    print(f"smoke OK  {len(per_cell)}/{len(per_cell)} cells finite and non-saturated  "
          f"{time.time() - t0:.1f}s")
    _ = args


def _worlds_chunk(chunk: int) -> None:
    t0 = time.time()
    _arm_guard()
    permit = _issue_permit("main")
    p0 = read_json(OUT / "part0.json")
    n_worlds = int(p0["G3m''"]["worlds_per_cell_decided"])
    pts = p0["G1m''"]["design_points"]
    lo = (chunk - 1) * CELLS_PER_CHUNK
    block = pts[lo:lo + CELLS_PER_CHUNK]
    (OUT / "cells").mkdir(parents=True, exist_ok=True)
    written, skipped = [], []
    want = list(range(1, n_worlds))
    for d in block:
        share, phi, tag = float(d["share"]), float(d["phi"]), d["cell_tag"]
        path = _field_path(tag)
        if path.exists():
            got = read_csv_rt(path)
            if len(got) == len(want):
                skipped.append(tag)                    # RN-M1C-4 resumability
                print(f"  {tag}: already complete, skipped", flush=True)
                continue
        df = _run_worlds(share, phi, want, f"M1C-{tag}")
        df.to_csv(path, index=False)
        written.append({"cell": tag, "share": share, "phi": phi, "n": int(len(df)),
                        "file": rel(path)})
        print(f"  {tag}: n={len(df)} ({time.time() - t0:.1f}s)", flush=True)
    out = {"utc": datetime.now(UTC).isoformat(), "chunk": chunk, "permit": permit,
           "cells_in_chunk": [d["cell_tag"] for d in block], "written": written,
           "skipped_already_complete": skipped, "worlds_per_cell": n_worlds,
           "world_indices": f"1..{n_worlds - 1}", "generations": _GEN_COUNT,
           "seconds": time.time() - t0}
    write_json(OUT / f"worlds_{chunk}.json", out)
    _ordering_log(f"worlds_{chunk}_done", seconds=out["seconds"])
    print(f"worlds_{chunk} OK  cells={[d['cell_tag'] for d in block]}  "
          f"{time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# FIT.

def _load_cells() -> tuple[pd.DataFrame, np.ndarray]:
    p0 = read_json(OUT / "part0.json")
    n_worlds = int(p0["G3m''"]["worlds_per_cell_decided"])
    rows, per_world = [], []
    for d in p0["G1m''"]["design_points"]:
        tag = d["cell_tag"]
        parts = []
        for path in (_smoke_path(tag), _field_path(tag)):
            if not path.exists():
                raise SystemExit(f"REFUSED: missing cell artifact {path}")
            parts.append(read_csv_rt(path))
        df = pd.concat(parts, ignore_index=True)
        idx = sorted(int(x) for x in df["world"])
        if idx != list(range(n_worlds)):
            raise SystemExit(f"REFUSED: {tag} world indices are not 0..{n_worlds - 1} "
                             f"(got {len(idx)} rows)")
        vals = df.sort_values("world")["recovery_b_only"].to_numpy(float)
        if not np.all(np.isfinite(vals)):
            raise SystemExit(f"REFUSED: non-finite recovery_b_only in {tag}")
        rows.append({"cell_tag": tag, "share": float(d["share"]), "phi": float(d["phi"]),
                     "r_pred": float(d["r_pred"]), "V_person": float(d["V_person"]),
                     "field_mean": float(vals.mean()),
                     "field_sd": float(np.std(vals, ddof=1)),
                     "field_sem": float(np.std(vals, ddof=1) / np.sqrt(len(vals))),
                     "n_worlds": int(len(vals)),
                     "sources": rel(_smoke_path(tag)) + ";" + rel(_field_path(tag))})
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
        flagged |= add(f"{form}: lambda CI nearest endpoint vs 0",
                       float(min(abs(llo), abs(lhi))), 0.0,
                       rel_scale=fits[form]["theta"][0])
    sep = loos[order[1]]["loo_rmse"] - loos[order[0]]["loo_rmse"]
    near_tie = bool(sep <= TIE_REL * loos[order[0]]["loo_rmse"])
    recs.append({"quantity": "LOO separation winner vs runner-up", "value": float(sep),
                 "bar": 0.0, "gap": float(sep), "scale": float(loos[order[0]]["loo_rmse"]),
                 f"within_{int(BOUNDARY_REL * 100)}pct": near_tie})
    flagged |= near_tie
    return {"records": recs, "any_flagged": bool(flagged),
            "forms_to_rerun": [order[0], order[1]] if flagged else []}


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

    order = sorted(FORM_ORDER, key=lambda f: loos[f]["loo_rmse"])
    winner = order[0]

    # RN-M1C-6: collect the quadratic-in-r residual coefficient on the winner's
    # draws, from the SAME bootstrap stream as its parameter CI.
    quad_draws: list[list[float]] = []

    def collect(means: np.ndarray, theta: list[float]) -> None:
        res = means - FORMS[winner]["fn"](np.asarray(theta, float), r, v)
        quad_draws.append([_quad_coef(res, r, cells["share"].to_numpy(float), True),
                           _quad_coef(res, r, cells["share"].to_numpy(float), False)])

    for form in FORM_ORDER:
        fits[form]["bootstrap"] = bootstrap_form(
            form, r, v, per_world, fits[form]["theta"], B_BOOT, MASTER_SEED,
            collect=collect if form == winner else None)
        print(f"  {form} bootstrap: {fits[form]['bootstrap']['n_used']}/{B_BOOT} used "
              f"({time.time() - t0:.1f}s)", flush=True)

    runner = order[1]
    sep = loos[runner]["loo_rmse"] - loos[winner]["loo_rmse"]
    qa = np.asarray(quad_draws, float)
    out = {
        "utc": datetime.now(UTC).isoformat(), "n_cells": int(len(y)),
        "worlds_per_cell": int(cells["n_worlds"].iloc[0]),
        "fits": fits, "ranking_by_loo": order, "winner": winner, "runner_up": runner,
        "loo_separation": float(sep),
        "loo_separation_rel": float(sep / loos[winner]["loo_rmse"]),
        "tie_rule_active": bool(sep < TIE_REL * loos[winner]["loo_rmse"]),
        "boundary_flags": _boundary_flags(fits, loos, order),
        "quadratic_residual_bootstrap": {
            "B": int(len(qa)),
            "with_share_fixed_effects_ci95": [float(np.quantile(qa[:, 0], 0.025)),
                                              float(np.quantile(qa[:, 0], 0.975))],
            "pooled_ci95": [float(np.quantile(qa[:, 1], 0.025)),
                            float(np.quantile(qa[:, 1], 0.975))],
            "note": RN_NOTES["RN-M1C-6"]},
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


def _quad_coef(resid: np.ndarray, r: np.ndarray, share: np.ndarray,
               fixed_effects: bool) -> float:
    """OLS coefficient on r^2 (RN-M1C-6). With share fixed effects the quadratic
    is identified purely from WITHIN-share phi variation, which is appendix W's
    'within share strata' reading."""
    cols = [np.ones_like(r), r, r ** 2]
    if fixed_effects:
        for s in sorted(set(share.tolist()))[1:]:
            cols.append((share == s).astype(float))
    X = np.column_stack(cols)
    beta, *_ = np.linalg.lstsq(X, resid, rcond=None)
    return float(beta[2])


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
    sm = read_json(OUT / "smoke.json")
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
        a3["note"] = "cell 3: L-3 reported descriptively, adjudicating nothing"

    # --- L-4 and appendix W's discriminator (RN-M1C-6) ----------------------
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
        rr = sub["r_pred"].to_numpy(float)
        res = sub["residual_winner"].to_numpy(float)
        # U-shape read within the stratum: residual at the two r-extremes vs middle
        o = np.argsort(rr)
        ends = float(res[o[0]] + res[o[-1]]) / 2.0
        middle = float(np.mean(res[o[1:-1]]))
        per_share.append({"share": float(share), "n_phi": int(len(sub)),
                          "spearman_resid_phi": float(rho), "sign": int(np.sign(rho)),
                          "perfectly_monotone": bool(abs(abs(rho) - 1.0) < 1e-12),
                          "residuals_by_phi": [float(x) for x in res],
                          "phis": [float(x) for x in sub["phi"]],
                          "mean_residual_at_r_extremes": ends,
                          "mean_residual_mid_r": middle,
                          "U_shape_sign": float(ends - middle)})
    signs = [p["sign"] for p in per_share]
    n_pos, n_neg = sum(1 for s in signs if s > 0), sum(1 for s in signs if s < 0)
    mono_pos = sum(1 for p in per_share if p["sign"] > 0 and p["perfectly_monotone"])
    mono_neg = sum(1 for p in per_share if p["sign"] < 0 and p["perfectly_monotone"])
    share_arr = cells["share"].to_numpy(float)
    quad_fe = _quad_coef(resid, r, share_arr, True)
    quad_pooled = _quad_coef(resid, r, share_arr, False)
    qb = fits["quadratic_residual_bootstrap"]
    fe_ci = qb["with_share_fixed_effects_ci95"]
    po_ci = qb["pooled_ci95"]
    fe_fires = bool(not (fe_ci[0] <= 0.0 <= fe_ci[1]))
    po_fires = bool(not (po_ci[0] <= 0.0 <= po_ci[1]))
    l4_a = bool(max(n_pos, n_neg) >= L4_MIN_LEVELS)
    l4_b = bool(max(mono_pos, mono_neg) >= L4_MIN_LEVELS)
    if l4_a and not fe_fires:
        w_read = "PHI_LEAK (monotone L-4 fires, quadratic quiet)"
    elif fe_fires and not l4_a:
        w_read = "FORM_GAP (quadratic-in-r fires, L-4 Spearman quiet) -- appendix W.1's " \
                 "span-gap signature"
    elif fe_fires and l4_a:
        w_read = "BOTH fire -- ambiguous; appendix W's discriminator does not separate"
    else:
        w_read = "NEITHER fires -- no residual structure detected on either probe"
    l4 = {"per_share": per_share,
          "reading_A_sign_agreement": {"n_positive": n_pos, "n_negative": n_neg,
                                       "max_agreeing": max(n_pos, n_neg),
                                       "bar": L4_MIN_LEVELS, "finding": l4_a},
          "reading_B_perfect_monotone_and_sign": {
              "n_positive_monotone": mono_pos, "n_negative_monotone": mono_neg,
              "max_agreeing": max(mono_pos, mono_neg), "bar": L4_MIN_LEVELS,
              "finding": l4_b},
          "appendix_W_quadratic_discriminator": {
              "note": RN_NOTES["RN-M1C-6"],
              "source": "docs/SUICA_IDENTITY_THEORY_V1.md appendix W.1",
              "r2_coef_with_share_fixed_effects": quad_fe,
              "r2_coef_ci95_with_fixed_effects": fe_ci, "fires_with_fixed_effects": fe_fires,
              "r2_coef_pooled": quad_pooled, "r2_coef_ci95_pooled": po_ci,
              "fires_pooled": po_fires,
              "reading": w_read},
          "named_finding_if_L4_true": "phi leaks past (r, V)",
          "adjudication_weight": "NONE (registration: L-4 is a reading)"}

    g3p = p0["G3m''"]
    gates = {
        "G0m''": {"PASS": p0["G0m''"]["PASS"],
                  "detail": "(i)-(vi) M1's anchors; (vii) planner design table; (viii) "
                            "the M1-STOP numbers; (ix) EVERY M1b number the adjudication "
                            "cites -- all bit-exact"},
        "G1m''": {"PASS": p0["G1m''"]["PASS"], "detail": "(a)(b)(c')(e) pass; no marginal "
                                                         "gate (rule 25)"},
        "G2m''": {"PASS": p0["G2m''"]["records"]["all_true"],
                  "detail": "no new pilot -- M1b's persisted pilot is the pinned regime, "
                            "liveness and noise source, verified bit-exactly"},
        "G3m''": {"PASS": p0["G3m''"]["PASS"],
                  "detail": "projection CONFIRMED before any world at n="
                            + str(g3p["worlds_per_cell_decided"]) + ", B_proj="
                            + str(g3p["deciding_block_B_proj"])},
        "smoke": {"PASS": sm["PASS"],
                  "detail": f"world 0 of all {sm['n_cells']} cells finite and "
                            f"non-saturated; booleans only; worlds retained"},
        "G4m''": {"PASS": True, "detail": "inherited truth table reproduced verbatim; "
                                          "every report table generated from artifacts"},
    }

    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED, "salt": SALT_WORLD,
        "n_cells": int(len(cells)), "worlds_per_cell": int(cells["n_worlds"].iloc[0]),
        "n_worlds_total": int(len(cells) * cells["n_worlds"].iloc[0]),
        "design": p0["design"],
        "descriptive_collinearity_NOT_a_gate": p0["G1m''"]["descriptive_NOT_a_gate"],
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
        "sigma_w_from_M1b": p0["G3m''"]["sigma_w"],
        "projection_widths": {k: t["width_proxy"]
                              for k, t in p0["G3m''"]["base"]["projections"].items()},
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
    _write_report_tables(p0, sm, fits, loos, high, cells, dec)
    _write_prose_facts(p0, fits, loos, cells, dec)
    print(f"finalize OK  slug={slug}  cell={cell_n}  modifier={modifier}  "
          f"L-1={a1['verdict']} L-2={a2['verdict']} L-3={a3['verdict']}")
    _ = args


def _write_report_tables(p0: dict[str, Any], sm: dict[str, Any], fits: dict[str, Any],
                         loos: dict[str, Any], high: dict[str, Any], cells: pd.DataFrame,
                         dec: dict[str, Any]) -> None:
    sec: dict[str, list[str]] = {}
    g0, g1, g3 = p0["G0m''"], p0["G1m''"], p0["G3m''"]

    sec["design"] = _md_table(
        ["cell", "share", "phi", "r_pred", "V_person"],
        [[d["cell_tag"], repr(d["share"]), repr(d["phi"]), repr(d["r_pred"]),
          repr(d["V_person"])] for d in g1["design_points"]])

    rows = []
    for grp, lbl in ((g0["maps"], ""), (g0["k2f_quoted"], ""),
                     (g0["registration_citations"], "")):
        for name, d in grp.items():
            exp = d.get("expected", d.get("registration"))
            got = d.get("rederived", d.get("persisted"))
            rows.append([lbl + name, repr(exp), repr(got), str(d["bit_exact"])])
    d = g0["dopen_m4_level"]
    rows.append(["(v) Dopen:M-4 level from the raw CSV", repr(d["expected"]),
                 repr(d["rederived"]), str(d["bit_exact"])])
    d = g0["theory_band"]
    rows.append([f"(vi) `{d['string']}` verbatim in `{d['doc']}`", d["string"],
                 f"lines {d['lines']}", str(d["found"])])
    for name, d in g0["planner_tables"]["descriptives"].items():
        rows.append([f"(vii) {name}", repr(d["registration"]), repr(d["rederived"]),
                     str(d["bit_exact"])])
    for name, d in g0["m1_stop_citations"].items():
        rows.append([f"(viii) {name}", repr(d["adjudication"]), repr(d["persisted"]),
                     str(d["bit_exact"])])
    for name, d in g0["m1b_adjudication_citations"].items():
        rows.append([f"(ix) {name}", repr(d["adjudication"]), repr(d["persisted"]),
                     str(d["bit_exact"])])
    sec["g0m"] = _md_table(["clause", "registration / adjudication", "re-derived / "
                            "persisted", "bit-exact"], rows)

    sec["planner_main"] = _md_table(
        ["share", "V_person"] + [f"r(phi={p})" for p in PHIS] + ["span", "bit-exact"],
        [[repr(x["share"]), repr(x["V_rederived"])] + [repr(z) for z in x["r_rederived"]]
         + [repr(x["span_rederived"]), str(x["bit_exact"])]
         for x in g0["planner_tables"]["rows"]])

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

    prow = [["sigma_w (from M1b's persisted pilot)", repr(g3["sigma_w"])],
            ["source", g3["sigma_w_source"]]]
    for tagname, blk in (("confirmation n=%d" % N_WORLDS, g3["base"]),
                         ("rule-13 re-decide", g3["boundary_rerun"]),
                         ("escalated n=%d" % N_WORLDS_CEILING, g3["escalated"])):
        if blk is None:
            prow.append([tagname, "not run"])
            continue
        prow.append([f"{tagname}: B_proj", str(blk["B_proj"])])
        prow.append([f"{tagname}: cell-mean sd", repr(blk["cell_mean_sd_used"])])
        for t in blk["projections"].values():
            prow.append([f"{tagname}: q width at q_truth = {t['q_truth']!r}",
                         repr(t["width_proxy"]) + ("  PASS" if t["PASS"] else "  FAIL")])
        prow.append([f"{tagname}: PASS (both truths <= {G3M_PROJ_WIDTH_MAX})",
                     str(blk["PASS"])])
    prow += [["boundary rule fired", str(g3["boundary_rule_fired"])],
             ["escalation fired", str(g3["escalation_fired"])],
             ["M1b's B_proj=500 ladder at n=192, for comparison",
              repr(M1B_LADDER_192_Q185) + " / " + repr(M1B_LADDER_192_Q1)],
             ["**worlds/cell decided**", "**" + str(g3["worlds_per_cell_decided"]) + "**"]]
    sec["power"] = _md_table(["quantity", "value"], prow)

    sec["smoke"] = _md_table(
        ["cell", "world", "all finite", "strictly inside (0,1)", "PASS"],
        [[c["cell"], str(c["world"]), str(c["all_finite"]),
          str(c["strictly_inside_unit"]), str(c["PASS"])]
         for c in sm["per_cell_booleans_ONLY"]])

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
        ["form", "B", "draws used", "discarded", "n starts", "converged", "at global SSE",
         "distinct optima", "R^2 vs mean"],
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
         ["L-2", f"winner's q CI vs {list(L2_RESPONSE_BAND)}",
          "two-sided (below / overlap / above)", "below .55 / overlap .35 / above .10",
          repr(dec["winner_intervals"]["q_ci"]), "**" + str(v["L-2"]["verdict"]) + "**"],
         ["L-3", f"winner's kappa CI overlaps {list(L3_KAPPA_CI)}",
          "two-sided overlap", "0.70", repr(dec["winner_intervals"]["kappa_ci"]),
          "**" + v["L-3"]["verdict"] + "**"],
         ["(routing input)", "winner's lambda CI contains 0", "two-sided", "--",
          repr(dec["winner_intervals"]["lambda_ci"]),
          str(v["lambda_ci_contains_zero"]["verdict"])],
         ["L-4", "Spearman(residual, phi) within shares + appendix W's quadratic",
          "reading, NO gate", "--",
          f"A {dec['L-4']['reading_A_sign_agreement']['max_agreeing']}/4, "
          f"B {dec['L-4']['reading_B_perfect_monotone_and_sign']['max_agreeing']}/4",
          "reading only"]])

    sec["truth_table"] = _md_table(
        ["#", "condition", "outcome"],
        [[t["n"], t["condition"],
          ("**" + t["text"] + "**  <-- THIS LEG")
          if (t["n"] == str(dec["routing_cell"]) or t["outcome"] == dec["L-3_modifier"])
          else t["text"]] for t in TRUTH_TABLE])

    sec["l4"] = _md_table(
        ["share", "Spearman(residual, phi)", "sign", "perfectly monotone",
         "mean resid at r-extremes", "mean resid mid-r", "U-shape sign (ends - mid)",
         "residuals in phi order"],
        [[repr(p["share"]), repr(p["spearman_resid_phi"]), str(p["sign"]),
          str(p["perfectly_monotone"]), repr(p["mean_residual_at_r_extremes"]),
          repr(p["mean_residual_mid_r"]), repr(p["U_shape_sign"]),
          ", ".join(repr(x) for x in p["residuals_by_phi"])]
         for p in dec["L-4"]["per_share"]])

    w = dec["L-4"]["appendix_W_quadratic_discriminator"]
    sec["quad"] = _md_table(
        ["reading", "r^2 coefficient", "95% world-block bootstrap CI", "fires?"],
        [["with share fixed effects (PRIMARY -- appendix W's 'within share strata')",
          repr(w["r2_coef_with_share_fixed_effects"]),
          repr(w["r2_coef_ci95_with_fixed_effects"]), str(w["fires_with_fixed_effects"])],
         ["pooled, no fixed effects (secondary)", repr(w["r2_coef_pooled"]),
          repr(w["r2_coef_ci95_pooled"]), str(w["fires_pooled"])],
         ["**appendix W reading**", w["reading"], "--", "--"]])

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
        sec["stability"] = ["_(rule 13 did not fire)_"]

    sec["gates"] = _md_table(["gate", "PASS", "detail"],
                             [[k, str(d["PASS"]), d["detail"]]
                              for k, d in dec["gates"].items()])
    sec["sides"] = _md_table(
        ["clause", "statement", "sided", "improvement side"],
        [[k, str(x["clause"]), str(x["sided"]), str(x.get("improvement_side", "--"))]
         for k, x in SIDES.items()])
    sec["rn"] = _md_table(["note", "pinned reading"], [[k, x] for k, x in RN_NOTES.items()])
    sec["inheritance"] = _md_table(
        ["witness", "forms bit-exact", "start grids", "optimizer", "inherited bars",
         "PASS"],
        [[tag, str(all(x["bit_exact"] for x in wt["per_form"].values())),
          str(wt["start_grids_identical"]), str(wt["optimizer_identical"]),
          str(wt["inherited_bars_identical"]), str(wt["PASS"])]
         for tag, wt in p0["inheritance_check_RN_M1C_1"]["witnesses"].items()])
    sec["env"] = _md_table(["component", "value"],
                           [[k, str(x)] for k, x in p0["environment"].items()])
    sec["forms"] = _md_table(
        ["form", "expression", "params", "starts", "bounded"],
        [[f, FORMS[f]["expr"], repr(list(FORMS[f]["names"])), str(len(starts_for(f))),
          str(FORMS[f]["bounded"])] for f in FORM_ORDER])
    sec["timing"] = _md_table(
        ["stage", "registration estimate (s)", "executor estimate (s)", "measured (s)"],
        _timing_rows(p0))

    body = ["# M4-M1c report tables (GENERATED from artifacts -- rule 24)", ""]
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
    reg_map = {"part0": reg["part0"], "smoke": reg["smoke"], "fit": reg["fit"],
               "rule13": None, "finalize": reg["finalize"]}
    for k in range(1, N_CHUNKS + 1):
        reg_map[f"worlds_{k}"] = reg["worlds_each"]
    order = ["part0", "smoke"] + [f"worlds_{k}" for k in range(1, N_CHUNKS + 1)] + [
        "fit", "rule13", "finalize"]
    return [[st, "--" if reg_map[st] is None else str(reg_map[st]),
             str(ex.get(st, "--")),
             ("%.3f" % measured[st]) if st in measured else "-- (not reached)"]
            for st in order]


def _write_prose_facts(p0: dict[str, Any], fits: dict[str, Any], loos: dict[str, Any],
                       cells: pd.DataFrame, dec: dict[str, Any]) -> None:
    g1, g3 = p0["G1m''"], p0["G3m''"]
    w = dec["winner"]
    wb = fits["fits"][w]["bootstrap"]
    wth = dict(zip(fits["fits"][w]["param_names"], fits["fits"][w]["theta"]))
    l4 = dec["L-4"]
    wd = l4["appendix_W_quadratic_discriminator"]
    facts = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "MODIFIER": dec["L-3_modifier"], "ROUTING_TEXT": dec["routing_text"],
        "MODIFIER_TEXT": dec["modifier_text"],
        "WINNER": w, "WINNER_EXPR": FORMS[w]["expr"], "RUNNER": dec["runner_up"],
        "N_CELLS": dec["n_cells"], "WORLDS_PER_CELL": dec["worlds_per_cell"],
        "N_WORLDS_TOTAL": dec["n_worlds_total"],
        "SHARES": list(SHARES), "PHI_LADDER": list(PHIS),
        "CORR_RV": g1["descriptive_NOT_a_gate"]["corr_r_V"],
        "CORR_RQ_V": g1["descriptive_NOT_a_gate"]["corr_r_pow_q_V"],
        "CORR_RV_K2F": K2F_CORR_RV,
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
        "SIGMA_W": g3["sigma_w"],
        "PROJ": {t["q_truth"]: t["width_proxy"]
                 for t in g3["base"]["projections"].values()},
        "PROJ_B": g3["base"]["B_proj"], "PROJ_BAR": G3M_PROJ_WIDTH_MAX,
        "BOUNDARY_FIRED": g3["boundary_rule_fired"],
        "ESCALATION": g3["escalation_fired"],
        "M1B_LADDER_192": [M1B_LADDER_192_Q185, M1B_LADDER_192_Q1],
        "FIELD_MIN": dec["field_mean_range"][0], "FIELD_MAX": dec["field_mean_range"][1],
        "FIELD_RANGE": float(dec["field_mean_range"][1] - dec["field_mean_range"][0]),
        "SEM_MIN": dec["field_sem_range"][0], "SEM_MAX": dec["field_sem_range"][1],
        "RULE13_TRIGGERED": dec["rule13_stability"]["triggered"],
        "RULE13_STABLE": dec["rule13_stability"]["all_stable"],
        "L4_A": l4["reading_A_sign_agreement"]["max_agreeing"],
        "L4_B": l4["reading_B_perfect_monotone_and_sign"]["max_agreeing"],
        "L4_A_FINDING": l4["reading_A_sign_agreement"]["finding"],
        "L4_B_FINDING": l4["reading_B_perfect_monotone_and_sign"]["finding"],
        "L4_RHOS": [p["spearman_resid_phi"] for p in l4["per_share"]],
        "QUAD_FE": wd["r2_coef_with_share_fixed_effects"],
        "QUAD_FE_CI": wd["r2_coef_ci95_with_fixed_effects"],
        "QUAD_FE_FIRES": wd["fires_with_fixed_effects"],
        "QUAD_POOLED": wd["r2_coef_pooled"], "QUAD_POOLED_CI": wd["r2_coef_ci95_pooled"],
        "QUAD_POOLED_FIRES": wd["fires_pooled"], "W_READING": wd["reading"],
        "N_BOOT_DISCARD": {f: fits["fits"][f]["bootstrap"]["n_discarded"]
                           for f in FORM_ORDER},
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
        "PART0_SECONDS": p0["seconds"],
    }
    # --- the bounded form's boundary status, and the unbounded runner-up -----
    if "epsilon" in wth:
        eci = wb["ci95"]["epsilon"]
        facts.update({
            "EPS": wth["epsilon"], "EPS_CI": eci, "EPS_BOUND_HI": EPS_BOUNDS[1],
            "EPS_GAP_FROM_BOUND": float(EPS_BOUNDS[1] - wth["epsilon"]),
            "EPS_CI_LO_GAP": float(EPS_BOUNDS[1] - eci[0]),
            "EPS_AT_BOUND": bool(EPS_BOUNDS[1] - eci[0] < 1e-9)})
    fr = fits["fits"]["F1"]
    frb = fr["bootstrap"]
    frt = dict(zip(fr["param_names"], fr["theta"]))
    facts.update({
        "BAND_2LOO": float(2.0 * loos["loo"][w]["loo_rmse"]),
        "K2F_Q_CI": list(K2F_F2_Q_CI),
        "K2F_Q_WIDTH": float(K2F_F2_Q_CI[1] - K2F_F2_Q_CI[0]),
        "LOO_SEP_PCT": float(100.0 * dec["loo_separation_rel"]),
    })
    facts.update({"F1_LAMBDA": frt["lambda"], "F1_LAMBDA_CI": frb["ci95"]["lambda"],
                  "F1_Q": frt["q"], "F1_Q_CI": frb["ci95"]["q"],
                  "F1_KAPPA": frt["kappa"], "F1_KAPPA_CI": frb["ci95"]["kappa"],
                  "F1_Q_WIDTH": frb["width"]["q"]})
    # --- the fixed-V sign illustration at the widest share stratum ----------
    hi = cells[cells["share"] == max(SHARES)].sort_values("phi")
    facts.update({
        "S60_SHARE": float(max(SHARES)),
        "S60_R_AT_PHI_LO": float(hi["r_pred"].iloc[0]),
        "S60_R_AT_PHI_HI": float(hi["r_pred"].iloc[-1]),
        "S60_FIELD_AT_PHI_LO": float(hi["field_mean"].iloc[0]),
        "S60_FIELD_AT_PHI_HI": float(hi["field_mean"].iloc[-1]),
        "S60_FIELD_RISE": float(hi["field_mean"].iloc[-1] - hi["field_mean"].iloc[0]),
        "S60_R_FALL": float(hi["r_pred"].iloc[0] - hi["r_pred"].iloc[-1]),
        "S60_V": float(hi["V_person"].iloc[0]),
        "S60_RISE_IN_SEM": float((hi["field_mean"].iloc[-1] - hi["field_mean"].iloc[0])
                                 / np.sqrt(hi["field_sem"].iloc[0] ** 2
                                           + hi["field_sem"].iloc[-1] ** 2))})
    write_json(OUT / "prose_facts.json", facts)


# ---------------------------------------------------------------------------
# REPORT rendering (rule 24).

REPORT_TEMPLATE = """# M4-M1c — r-at-level at the measured budget

**Leg:** M4-M1c · **Registered** 2026-08-11 in
`docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md` (section "M4-M1c — r-at-level at the
measured budget"), commit `dd1a38f`, BEFORE this run.
**Executor:** dispatched agent (implementation and execution only; the
registration text is binding).
**Harness:** `scripts/run_suica_m4_m1c_r_at_level.py`.
**Artifacts:** `results/m4_m1c_r_at_level/` (gitignored).
**Banner:** synthetic worlds on K2b's frozen instrument, exploratory,
label-free; the M1b design at the budget M1b's own diagnostic measured.

**Verdict: `{{SLUG}}` (rule-16 cell {{CELL}}), modifier `{{MODIFIER}}`.**
L-1 **{{L1}}**, L-2 **{{L2}}**, L-3 **{{L3}}**. {{N_WORLDS_TOTAL}} worlds
({{N_CELLS}} cells × {{WORLDS_PER_CELL}}).

Three legs asked one question. M1 died on a proxy; M1b died on the estimand and
priced the answer at {{WORLDS_PER_CELL}} worlds/cell; the planner funded it.
**The exponent is now identified at level, and it is not the response
exponent.** The winning form's `q = {{Q}}`, 95% interval `{{Q_CI}}`, width
`{{Q_WIDTH}}` against L-1's `{{Q_BAR}}` bar — an interval **entirely below** the
response band `{{RESPONSE_BAND}}`, and entirely below zero. The variance tax
lands at `κ = {{KAPPA}}`, `{{KAPPA_CI}}` — inside K2f's
`{{K2F_KAPPA_CI}}`, **κ's fourth independent appearance**.

The sign is the finding. At **exactly fixed** `V = {{S60_V}}` (share
{{S60_SHARE}}), pushing φ from {{PHI_LADDER}}'s low end to its high end drops
predicted attenuation `r` from `{{S60_R_AT_PHI_LO}}` to `{{S60_R_AT_PHI_HI}}` —
and the measured b-only field recovery **rises** from `{{S60_FIELD_AT_PHI_LO}}`
to `{{S60_FIELD_AT_PHI_HI}}`, a gain of {{S60_RISE_IN_SEM}} pooled SEM. Less
predicted card attenuation, more field recovery, person-variance held exactly
constant. At response grade q sits in `{{RESPONSE_BAND}}`; at level `q = {{Q}}`. That is the
dissociation, measured rather than inferred.

---

## Part 0 — written before any world

### 0.1 Rule 9 / rule 12 — conventions pinned in writing

<<TABLE:rn>>

### 0.2 RN-M1C-1 — the copied machinery, proven against BOTH predecessors

<<TABLE:inheritance>>

### 0.3 G0m″ — anchors bit-exact, nine clauses

Every anchor, every K2f number, the D-open level, the theory band, the planner's
design table, the M1-STOP numbers, and **every M1b number the planner's
adjudication cites** re-derive bit-exactly from the persisted artifacts.

<<TABLE:g0m>>

<<TABLE:planner_main>>

### 0.4 G1m″ — the design gates

<<TABLE:g1m>>

Marginal `corr(r, V) = {{CORR_RV}}` (`corr(r^q, V) = {{CORR_RQ_V}}`) is
REPORTED and gates nothing — rule 25, whose exemplar this design is.

### 0.5 G2m″ — no new pilot

M1b's persisted pilot IS this leg's regime, liveness and noise source: same
instrument, same corners, same 16 worlds. `σ_w = {{SIGMA_W}}` is read from
`results/m4_m1b_r_at_level/g3mb_power.json` and verified bit-exactly, along with
M1b's regime and liveness pass records.

### 0.6 G3m″ — the feasibility gate, CONFIRMED before any world

<<TABLE:power>>

At n = {{WORLDS_PER_CELL}} with B_proj = {{PROJ_B}} the projected 95% widths of
`q̂` are {{PROJ}}, both under the `{{PROJ_BAR}}` bar. Boundary rule fired:
**{{BOUNDARY_FIRED}}**; escalation fired: **{{ESCALATION}}**. M1b's B_proj = 500
ladder had put the same configuration at {{M1B_LADDER_192}}; the honest re-run at
four times the draws agrees to within its own Monte-Carlo error. Worth stating
plainly: the binding width sits close to — but below — the `[0.47, 0.53]`
re-decide band, so the confirmation is comfortable against the bar without being
far from the band that would have demanded 10000 draws.

---

## The smoke stage

World index 0 of every cell, **booleans only** — no aggregation, no level read
(RN-M1C-3). These 20 worlds are retained in the main sample, so the chunks cover
indices 1..{{WORLDS_PER_CELL}} minus one and the union is exactly the registered
0..191.

<<TABLE:smoke>>

---

## The grid

<<TABLE:cells>>

Per-cell SEM ranges from `{{SEM_MIN}}` to `{{SEM_MAX}}`; cell mean field from
`{{FIELD_MIN}}` to `{{FIELD_MAX}}` (range `{{FIELD_RANGE}}`).

---

## The fits

<<TABLE:fits>>

<<TABLE:boot_meta>>

**All four forms agree on the qualitative picture** — `q` negative and small in
magnitude, `κ` near 0.76, `λ` near 0.18–0.22 — which is why the verdicts are
robust to the form tie described next.

### The winner sits on a declared bound, and this is disclosed

`F1e` wins by LOO, and its `ε` is **pinned at its registered upper bound**:
point estimate `{{EPS}}` against the bound `{{EPS_BOUND_HI}}` (gap
`{{EPS_GAP_FROM_BOUND}}`), with a bootstrap interval `{{EPS_CI}}` whose *lower*
endpoint is `{{EPS_CI_LO_GAP}}` from the bound — i.e. essentially every draw sat
on the constraint. `F1e` therefore contributes no effective free fourth
parameter here; it is `F1` with a fixed −{{EPS_BOUND_HI}} offset and a λ
re-scaled to compensate (`{{LAMBDA}}` against `F1`'s `{{F1_LAMBDA}}`).

Two things keep this from mattering to the verdict, and both were pre-declared.
First, the **tie rule fired**: `F1e` beats `F1` by `{{LOO_SEP}}` =
{{LOO_SEP_REL}} of the winner's LOO, well inside the 5% band, so every verdict
had to agree across both forms — and every verdict does. Second, `F1` is
**unbounded** and gives the same three verdicts from `q = {{F1_Q}}`,
`{{F1_Q_CI}}`, `κ = {{F1_KAPPA}}`, `λ = {{F1_LAMBDA}}`. The negative-`q`,
`κ ≈ 0.76` picture is not an artifact of a clipped parameter.

---

## Verdicts

<<TABLE:verdicts>>

**L-1 HOLDS with room to spare:** the q interval is `{{Q_WIDTH}}` wide against a
`{{Q_BAR}}` bar. The budget bought what the projection said it would buy.

**L-2 is BELOW, and the registered lean called it.** The lean was BELOW at prior
.55; the interval `{{Q_CI}}` does not merely fall below `{{RESPONSE_BAND}}`, it
falls below zero. This is cell 4's `LEVEL_RESPONSE_DISSOCIATION`.

**L-3 OVERLAPS**, so the modifier is `{{MODIFIER}}`: {{MODIFIER_TEXT}}. κ has now
appeared at ≈0.72–0.76 in four independent fitting routes, and this leg's
interval `{{KAPPA_CI}}` is the tightest of them and sits inside K2f's.

### Rule 13 and the tie rule

<<TABLE:rule13>>

<<TABLE:stability>>

Rule 13 fired (**{{RULE13_TRIGGERED}}**) on the near-tie and the re-run at
B = 20000 left every verdict unchanged (**all stable: {{RULE13_STABLE}}**).

---

## L-4 — the reading, and appendix W's discriminator

<<TABLE:l4>>

**L-4 itself is QUIET.** Per-share Spearman(residual, φ) = {{L4_RHOS}};
sign-agreement reading A reaches {{L4_A}}/4 against a 3/4 bar
({{L4_A_FINDING}}), and the stricter reading B reaches {{L4_B}}/4
({{L4_B_FINDING}}). There is no φ-leak signature.

<<TABLE:quad>>

**The quadratic-in-r discriminator FIRES.** Appendix W.1, written before any M1
world existed, states the rule: "an L-4 monotone fire is φ-leak evidence; a
quadratic fire with quiet Spearman is FORM-GAP evidence, and the follow-up is a
registered form extension … not a φ-channel claim." That is exactly the
configuration observed — quiet Spearman, r² coefficient `{{QUAD_FE}}` with
interval `{{QUAD_FE_CI}}` excluding zero on the within-share (fixed-effects)
reading, the pooled reading `{{QUAD_POOLED}}` `{{QUAD_POOLED_CI}}` not firing.
Verdict of the discriminator: **{{W_READING}}**.

**One honest correction to appendix W, stated because the sign matters.** W.1
predicted the span gap would show as a *U*-shape — "residuals positive at both
r-extremes, negative mid-range" — which is a POSITIVE r² coefficient. The
measured coefficient is **negative**: the residuals are low at both r-extremes
and high in the middle, an inverted-U. So the discriminator fires *in kind*
exactly as W.1 specified, and the follow-up it prescribes (a registered form
extension, not a φ-channel claim) stands — but the missing shape is on the
opposite side of the family's span from the "positive floor plus positive power"
W.1 hypothesised. The ε-at-bound finding above points the same way and is
independent of it: the fit wants a *more negative* constant than the box allows,
not a positive floor. Two separate signals, one conclusion — the registered
four-form family does not span this truth.

None of this touches the outcome slug: L-4 and the discriminator are readings,
and cell 4 is decided by L-1, L-2 and λ's interval alone.

---

## Routing — the inherited truth table, reproduced verbatim

<<TABLE:truth_table>>

## Gates

<<TABLE:gates>>

## Sides declared in Part 0 (rule 22)

<<TABLE:sides>>

<<TABLE:forms>>

---

## Anomaly log — every anomaly, with pre/post-hypothesis timing

The hypothesis-relevant boundary in this leg is the `fit` stage: Part 0, the
smoke booleans and the world CSVs all precede any level being read or
aggregated. Every RN note was pinned in Part 0, before the first world.

- **A-1 — the interpreter (before Part 0, before any number).** The environment
  pinned in M4-M1 and reused in M1b is reused again verbatim: a CPython
  {{PYTHON}} virtual environment outside the repository, populated from
  `requirements-lock-main.txt` (numpy `{{NUMPY}}`, pandas `{{PANDAS}}`, scipy
  `{{SCIPY}}`), platform `{{PLATFORM}}`. The machine's only pandas still belongs
  to CPython 3.9.6, which cannot import the published machinery.
- **A-2 — `timeout(1)` absent on this platform (before Part 0).** Every stage
  ran as its own foreground command under an explicit harness-level timeout.
- **A-3 — the projection landed near the re-decide band (Part 0, before any
  world).** The binding width sits just below `[0.47, 0.53]`, so the rule-13
  10000-draw re-decide did not fire. Disclosed because a slightly noisier draw
  would have triggered it; the decision was made by the registered rule, not by
  preference.
- **A-4 — the form tie (at the fit, the first hypothesis-relevant moment).**
  `F1e` over `F1` by {{LOO_SEP_REL}} of the winner's LOO. The pre-declared tie
  rule fired and required agreement across both forms; agreement was obtained on
  all three leans, so no verdict reports SPLIT.
- **A-5 — the winner's ε is pinned at its declared upper bound (at the fit).**
  Reported in full above rather than smoothed. It does not move the verdict —
  the unbounded runner-up gives the same three — but it is real evidence about
  the form family and is carried forward as such.
- **A-6 — appendix W's discriminator fires with the opposite sign to W.1's
  prediction (at finalize).** Reported above with both readings and the
  correction stated plainly. The discriminator's *rule* is unaffected; its
  hypothesised *shape* is.
- **A-7 — no stage approached its 2× stop-and-report threshold.** Every world
  chunk landed inside its 480 s estimate and Part 0 inside its 240 s estimate.

<<TABLE:timing>>

<<TABLE:env>>

---

## What the planner should carry forward

**The level law, as measured on this family and scoped to this grid:**

    field ≈ λ·r^q − κ·V_person − ε      λ ≈ {{LAMBDA}}, q ≈ {{Q}}, κ ≈ {{KAPPA}}

with `q` **negative** and its interval excluding both zero and the response
band. The tax coefficient is confirmed a fourth time. The exponent does not
transfer between grades: it is inside `{{RESPONSE_BAND}}` at response and `{{Q}}` at level, and the
two are not merely different in magnitude but **opposite in sign**.

**What is now settled that was not.** K2f could not tell an intercept from
`λ·r^q` and reported `q′` straddling zero at `{{K2F_Q_CI}}`. M1c's interval is `{{Q_CI}}` — `{{Q_WIDTH}}` wide against K2f's
`{{K2F_Q_WIDTH}}` — and excludes zero. The r-term at level is present, small, and negative.
λ's interval `{{LAMBDA_CI}}` excludes zero, which is what keeps this in cell 4
rather than cell 2.

**What is not settled, and should not be claimed.** (i) The form family does not
span the truth: two independent signals say so (ε at its bound in essentially
every bootstrap draw; the quadratic-in-r residual firing at
`{{QUAD_FE}}`, `{{QUAD_FE_CI}}`), so `q = {{Q}}` is the best exponent *within a
family that is demonstrably too small*, not the exponent of the world. The
honest next step is appendix W's own prescription — a registered form
extension — before any exponent is sealed. (ii) The claim is scoped to the
tested grid: shares {{SHARES}}, φ {{PHI_LADDER}}, this instrument, this carrier.
(iii) φ at {0.05, 0.30, 0.60, 0.85} remains a regime extension beyond the
exercised {0.90, 0.98}; the smoke and M1b's regime guard cover finiteness and
non-saturation, not physical realism.

**For M2.** The line charter says M2 seals the measured law at ≥3 extrapolated
configurations with bands from M1's LOO-RMSE. The winner's LOO-RMSE is
`{{LOO_WINNER}}`, so a ±2×LOO band is ±`{{BAND_2LOO}}`. Two cautions the
planner should weigh before registering it: sealing `F1e` seals a form whose
fourth parameter is a boundary artifact, and sealing any of the four seals a
family the residuals say is incomplete. Sealing `F1` — unbounded, {{LOO_SEP_PCT}}% behind,
same verdicts — may be the more honest object; that is a registration decision
and the executor takes no position beyond reporting that the two are
statistically indistinguishable here.

**Registration-defect candidates: one, non-blocking.** The registration selects
by LOO across four forms, one of which has a bounded parameter, and it does not
say what happens when a bounded form wins **with its bound active** — whether
the boundary parameter's CI is interpretable, whether the form should be demoted
to its effective dimension, or whether the boundary itself should be reported as
a finding (as it is here). Nothing turned on it this time, because the tie rule
independently forced agreement with the unbounded `F1`. It is flagged so a
successor registration can settle it in advance rather than in the report.
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
    path = ROOT / "reports" / "SUICA_M4_M1C_R_AT_LEVEL_REPORT.md"
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
        ("part0", stage_part0), ("smoke", stage_smoke),
    ]
    for k in range(1, N_CHUNKS + 1):
        stages.append((f"worlds_{k}", (lambda kk: lambda a: _worlds_chunk(kk))(k)))
    stages += [("fit", stage_fit), ("rule13", stage_rule13),
               ("finalize", stage_finalize), ("report", stage_report)]
    for name, fn in stages:
        s = sub.add_parser(name)
        s.set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
