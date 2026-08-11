#!/usr/bin/env python3
"""M4-M1e -- THE SHAPE: ADDITIVE OR r-MEDIATED (artifact-space).

Registered in docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md ("M4-M1e -- the shape:
additive or r-mediated", commit af4a335) BEFORE this file existed.
Implementation and execution only; the registration is binding.

M1d completed the family with a free intercept and convicted its own winner:
F0's (c, lambda, q) are jointly non-identified, so "q = -0.150" was withdrawn as
structural (appendix Y) and the surviving invariant is the SIGN of the slope at
fixed V.  M1d's r^2 probe still fired, so the shape is open.  This is the leg
that asks what the shape IS.

Does the level field SEPARATE -- field(share, phi) = share-margin + phi-margin --
or does the r-channel carry the cross-structure?  They are distinguishable HERE
because r(share, phi) is strongly non-additive: the within-share r-spans run
0.04714885082631204 -> 0.20320393707216905, a 4.31x range, so any r-mediated
field with a material r-coefficient MUST show share x phi interaction, while a
truly additive field kills r-mediation.

NO NEW WORLDS.  M1c's persisted corpus; the 20 cell means re-derived bit-exactly.

Five models:
    E-add      field = alpha_s + g_phi          (free margins, sum-to-zero)
    E-tax-add  field = c - kappa*V + g_phi      (share margin forced through the tax)
    E-rlin     field = alpha_s + s*r
    E-rq       field = alpha_s + lambda*r^q
    F0         field = c + lambda*r^q - kappa*V (M1d's winner, frozen baseline)

Rule 27 is in force and is the point: selection is not identification, so every
object that could be routed to M2 carries an explicit identification budget and
an object missing its budget is NOT sealable regardless of routing.

    part0     G0e(i) cell means bit-exact; G0e(ii) every M1d number the
              adjudication quotes; G0e(iii) the theory band; the MODEL-FREE
              monotonicity table (before any fit); the five-model table.
    fit       five models, LOO-cell selection, bootstrap, rule-27 budgets.
    rule13    the >=10xB re-run at any flagged boundary.
    finalize  L-1e / L-2e / L-3e, the rule-16 routing.
    report    renders the report from artifacts (rule 24).

Artifacts: results/m4_m1e_shape/ (gitignored)
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

OUT = ROOT / "results" / "m4_m1e_shape"
RES = ROOT / "results"
M1CRES = RES / "m4_m1c_r_at_level"
M1DRES = RES / "m4_m1d_form_completion"

LEG = "M4-M1e"
BANNER = ("artifact-space shape tournament on M1c's persisted 3840-world corpus; "
          "no new worlds, exploratory, label-free")

MASTER_SEED = 20260811
SHARES = (0.10, 0.25, 0.40, 0.60)
PHIS = (0.05, 0.30, 0.60, 0.85, 0.98)
N_WORLDS = 192

B_BOOT = 2000
B_BOOT_HIGH = 20000
TIE_REL = 0.05
BOUNDARY_REL = 0.05

M1D_KAPPA_CI = (0.7482226203832176, 0.8064115044591174)
SEALED_Q = 1.8528700746510731
SEALED_KAPPA_HAT = -0.7220359963712748
SEALED_LAMBDA = 0.17417497661611914
F0_Q_M1D = 1.372031438858951
THEORY_DOC = ROOT / "docs" / "SUICA_IDENTITY_THEORY_V1.md"
THEORY_BAND_STRING = "[1.71, 1.98]"

# --- Rule-27 identification budgets (registration) -------------------------
BUDGET_KAPPA_WIDTH = 0.15
BUDGET_C_WIDTH = 0.05
BUDGET_G_WIDTH = 0.01
BUDGET_S_FRAC = 0.50          # width <= 50% of |point|
BUDGET_Q_WIDTH = 1.0

# --- G0e(ii): every M1d number the adjudication quotes ---------------------
M1D = {
    "F0 c": 0.2234421078663232,
    "F0 lambda": -0.055190882521519,
    "F0 q": 1.372031438858951,
    "F0 kappa": 0.7766770259880144,
    "F0 c CI lo": 0.20818746052333,
    "F0 c CI hi": 1.6803368132111625,
    "F0 lambda CI lo": -1.5059828481846496,
    "F0 lambda CI hi": -0.04256154549067277,
    "F0 q CI lo": 0.021913588793404413,
    "F0 q CI hi": 2.6445200496694605,
    "F0 kappa CI lo": 0.7482226203832176,
    "F0 kappa CI hi": 0.8064115044591174,
    "LOO F0": 0.0030682764618814033,
    "LOO F1e": 0.0031856515917748638,
    "LOO F1": 0.003198131708377386,
    "LOO Fphi": 0.0032498223469787663,
    "LOO F2": 0.0034019365713125944,
    "LOO F3": 0.003877604046883495,
    "tie margin F0 vs F1e": 0.00011737512989346043,
    "F0 vs Fphi separation pct": 5.916868553169516,
    "r2 coef": -0.12563681892698172,
    "r2 CI lo B2000": -0.1772060912696028,
    "r2 CI hi B2000": -0.07219090437007022,
    "r2 CI lo B20000": -0.17935555262608965,
    "r2 CI hi B20000": -0.07097803090981235,
    "q_shadow": 2.24488769944643,
    "q_shadow CI lo": 2.1768337883424214,
    "q_shadow CI hi": 2.318980336007031,
    "legacy winner RMSE": 0.0059526106645589934,
    "legacy sealed RMSE": 0.11259090547752257,
    "legacy ratio": 18.914542176909535,
    "legacy k2f refit LOO": 0.0061559195350209,
}

# ---------------------------------------------------------------------------
# RN-M1E notes (rule 9 / rule 12).  PINNED IN PART 0, BEFORE ANY FIT.
#
# RN-M1E-1 (the sum-to-zero pinning, and a parameter-count reading).  The
#   registration states sum-to-zero pinning for E-add ("8 identifiable params" =
#   9 raw minus the one additive redundancy) and gives "7 params" for E-tax-add,
#   which is that model's RAW count (c, kappa, g_1..g_5).  E-tax-add carries the
#   SAME redundancy -- adding d to c and subtracting d from every g leaves the
#   fit unchanged -- so it too must be pinned or c and every g_phi are
#   individually non-identified, which would make rule 27's own c- and g-budgets
#   unmeetable by construction.  PINNED: sum-to-zero on g_phi in BOTH additive
#   models; identifiable counts are E-add 8 and E-tax-add 6, and both the raw and
#   identifiable counts are reported.  The count wording is recorded as a
#   non-blocking registration ambiguity, resolved before any fit.
#
# RN-M1E-2 (start grids not pinned by the registration).  The registration pins
#   starts only for E-rq (lambda in {-0.5, -0.055, 0.05, 0.5}, q in {0.5, 1.0,
#   1.372031438858951, 2.0, 3.0}).  PINNED for the rest: every share-margin
#   alpha_s starts at its own share's mean field and every g_phi at 0 (the
#   sum-to-zero centre), which is the exact OLS solution's neighbourhood by
#   construction; E-tax-add adds c in {0.1, 0.2, 0.3} x kappa in {0.0,
#   0.7220359963712748, 2.0}; E-rlin adds s in {-0.5, -0.055, 0.0, 0.05}; F0
#   keeps M1d's own 162-start grid verbatim (it is the FROZEN incumbent).
#
# RN-M1E-3 (linear models get a closed-form witness).  E-add, E-tax-add and
#   E-rlin are LINEAR in their parameters, so their least-squares optimum is
#   unique and available in closed form.  Each is therefore ALSO solved by
#   `numpy.linalg.lstsq` on its own design matrix and the two solutions are
#   compared; agreement to 1e-10 is required and reported.  This removes
#   optimizer risk from exactly the models whose identification budgets decide
#   the routing.
#
# RN-M1E-4 (L-2e's "within 5% LOO of E-add").  Read as
#   LOO(E-tax-add) <= 1.05 * LOO(E-add) -- a one-sided allowance for the taxed
#   model to be up to 5% worse, not a two-sided band; the clause's purpose is to
#   ask whether forcing the share margin through the tax COSTS anything.
#
# RN-M1E-5 (rule-16 precedence).  The registered table OVERLAPS: (F0 stands AND
#   probe fires) matches cells 4 and 5, and (winner AND probe fires AND budgets
#   unmet) matches cells 5 and 6.  PINNED precedence, declared before any fit:
#   cell 1 > REPRESENTATION_TIE > cell 4 > cell 5 > cell 6 > cells 2/3.  The
#   choice is immaterial to consequence -- cells 4, 5 and 6 all take the SAME
#   scoped-M2 route, and only cells 2/3 seal -- so the overlap changes the slug
#   and not the routing.  Recorded as a non-blocking rule-15/16 partition defect
#   candidate.
#
# RN-M1E-6 (the L-3e probe).  Inherits M1c's RN-M1C-6 / M1d's RN-M1D-2
#   estimator unchanged so the number is comparable across all three legs: OLS
#   of the winner's 20 cell residuals on [1, r, r^2] WITH share fixed effects,
#   CI from the same within-cell world-block bootstrap draws; fires = CI
#   excludes 0.  For a winner that already carries free share margins the fixed
#   effects are collinear with those margins; the probe is still well defined
#   (the r and r^2 columns are not in the margin span) and is computed the same
#   way regardless of winner, so no winner gets a different test.
#
# RN-M1E-7 (budgets for parameters the registration did not name).  Rule 27's
#   list covers kappa, c, g_phi, s and E-rq's q.  E-add's and E-rlin's and
#   E-rq's SHARE MARGINS alpha_s are consumed by any seal that quotes the model,
#   and no budget is declared for them.  Their widths are computed and reported
#   beside the budgeted ones, marked "no budget declared"; they gate nothing.
#   Recorded as a non-blocking rule-27 completeness candidate.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-M1E-1": "sum-to-zero pinning on g_phi in BOTH additive models (E-tax-add carries "
                "the same c/g redundancy as E-add; without pinning rule 27's own c and g "
                "budgets are unmeetable by construction); identifiable counts E-add 8, "
                "E-tax-add 6, raw counts 9 and 7 -- the registration's '7 params' is the "
                "raw count",
    "RN-M1E-2": "start grids the registration did not pin: alpha_s at its own share's "
                "mean field, g_phi at 0; E-tax-add adds c x kappa grids; E-rlin adds an s "
                "grid; F0 keeps M1d's 162-start grid verbatim as the frozen incumbent",
    "RN-M1E-3": "the three LINEAR models are also solved in closed form by lstsq and the "
                "two solutions compared (agreement to 1e-10 required and reported) -- no "
                "optimizer risk on the models whose budgets decide the routing",
    "RN-M1E-4": "L-2e's 'within 5% LOO of E-add' read one-sided: LOO(E-tax-add) <= 1.05 x "
                "LOO(E-add)",
    "RN-M1E-5": "rule-16 precedence pinned (cell 1 > REPRESENTATION_TIE > 4 > 5 > 6 > "
                "2/3) because the registered table overlaps; immaterial to consequence "
                "since cells 4/5/6 share the scoped-M2 route and only 2/3 seal",
    "RN-M1E-6": "L-3e's probe inherits the M1c/M1d estimator unchanged so the number is "
                "comparable across legs; computed identically regardless of winner",
    "RN-M1E-7": "share margins alpha_s are consumed by any seal but carry NO declared "
                "budget; their widths are reported beside the budgeted ones and gate "
                "nothing",
}

# ---------------------------------------------------------------------------
# Module loading -- ONE importlib loader chain.

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


def m1d() -> Any:
    return _load("run_suica_m4_m1d_form_completion")


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


def cell_tag(share: float, phi: float) -> str:
    return f"s{share:.2f}_p{phi:.2f}"


def _log(event: str, **kw: Any) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rec = {"utc": datetime.now(UTC).isoformat(), "event": event, **kw}
    with (OUT / "run_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True, default=float) + "\n")


# ---------------------------------------------------------------------------
# THE FIVE MODELS.  Every predict takes (theta, D) with D the design bundle.

class Design:
    def __init__(self, cells: pd.DataFrame) -> None:
        self.r = cells["r_pred"].to_numpy(float)
        self.v = cells["V_person"].to_numpy(float)
        self.phi = cells["phi"].to_numpy(float)
        self.share = cells["share"].to_numpy(float)
        self.si = np.array([SHARES.index(round(s, 10)) for s in self.share])
        self.pi = np.array([PHIS.index(round(p, 10)) for p in self.phi])
        self.y = cells["field_mean"].to_numpy(float)

    def sub(self, mask: np.ndarray) -> Design:
        d = object.__new__(Design)
        for k in ("r", "v", "phi", "share", "si", "pi", "y"):
            setattr(d, k, getattr(self, k)[mask])
        return d


def _g_full(g4: np.ndarray) -> np.ndarray:
    """Sum-to-zero: the fifth phi margin is minus the sum of the other four."""
    return np.concatenate([g4, [-float(np.sum(g4))]])


def p_eadd(t: np.ndarray, D: Design) -> np.ndarray:
    a = np.asarray(t[:4], float)
    g = _g_full(np.asarray(t[4:8], float))
    return a[D.si] + g[D.pi]


def p_etaxadd(t: np.ndarray, D: Design) -> np.ndarray:
    c, kap = float(t[0]), float(t[1])
    g = _g_full(np.asarray(t[2:6], float))
    return c - kap * D.v + g[D.pi]


def p_erlin(t: np.ndarray, D: Design) -> np.ndarray:
    a = np.asarray(t[:4], float)
    return a[D.si] + float(t[4]) * D.r


def p_erq(t: np.ndarray, D: Design) -> np.ndarray:
    a = np.asarray(t[:4], float)
    return a[D.si] + float(t[4]) * D.r ** float(t[5])


def p_f0(t: np.ndarray, D: Design) -> np.ndarray:
    return float(t[0]) + float(t[1]) * D.r ** float(t[2]) - float(t[3]) * D.v


GN = [f"alpha_s{ s:.2f}".replace(" ", "") for s in SHARES]
PN = [f"g_phi{p:.2f}" for p in PHIS]

MODELS: dict[str, dict[str, Any]] = {
    "E-add": {"fn": p_eadd, "names": GN + PN[:4],
              "expr": "field = alpha_s + g_phi  (sum-to-zero on g_phi)",
              "kind": "additive", "n_raw": 9, "n_identifiable": 8,
              "linear": True},
    "E-tax-add": {"fn": p_etaxadd, "names": ["c", "kappa"] + PN[:4],
                  "expr": "field = c - kappa*V + g_phi  (sum-to-zero on g_phi)",
                  "kind": "additive", "n_raw": 7, "n_identifiable": 6,
                  "linear": True},
    "E-rlin": {"fn": p_erlin, "names": GN + ["s"],
               "expr": "field = alpha_s + s*r", "kind": "r-mediated",
               "n_raw": 5, "n_identifiable": 5, "linear": True},
    "E-rq": {"fn": p_erq, "names": GN + ["lambda", "q"],
             "expr": "field = alpha_s + lambda*r^q", "kind": "r-mediated",
             "n_raw": 6, "n_identifiable": 6, "linear": False},
    "F0": {"fn": p_f0, "names": ["c", "lambda", "q", "kappa"],
           "expr": "field = c + lambda*r^q - kappa*V",
           "kind": "r-mediated (M1d's frozen incumbent baseline)",
           "n_raw": 4, "n_identifiable": 4, "linear": False},
}
MODEL_ORDER = ("E-add", "E-tax-add", "E-rlin", "E-rq", "F0")
ADDITIVE = ("E-add", "E-tax-add")
R_MEDIATED = ("E-rlin", "E-rq")

OPT = {
    "routine": "scipy.optimize.least_squares", "method": "trf",
    "jac": "2-point (numerical)", "bounds": "unbounded (no model declares bounds)",
    "ftol": 1e-14, "xtol": 1e-14, "gtol": 1e-14, "max_nfev": 20000,
    "loss": "linear (plain least squares)", "scipy_version": None,
}
LSTSQ_TOL = 1e-10
F0_C = (0.0, 0.05, 0.1)
F0_LAMBDA = (0.05, SEALED_LAMBDA, 0.5)
F0_Q = (-1.0, -0.5, -0.15, 0.0, 0.5, SEALED_Q)
F0_KAPPA = (0.0, -SEALED_KAPPA_HAT, 2.0)
ERQ_LAMBDA = (-0.5, -0.055, 0.05, 0.5)
ERQ_Q = (0.5, 1.0, F0_Q_M1D, 2.0, 3.0)
ETAX_C = (0.1, 0.2, 0.3)
ETAX_KAPPA = (0.0, -SEALED_KAPPA_HAT, 2.0)
ERLIN_S = (-0.5, -0.055, 0.0, 0.05)


def starts_for(model: str, D: Design) -> list[list[float]]:
    amean = [float(D.y[D.si == i].mean()) if np.any(D.si == i) else float(D.y.mean())
             for i in range(len(SHARES))]
    if model == "E-add":
        return [amean + [0.0, 0.0, 0.0, 0.0],
                [float(D.y.mean())] * 4 + [0.0, 0.0, 0.0, 0.0]]
    if model == "E-tax-add":
        return [[c, k, 0.0, 0.0, 0.0, 0.0] for c in ETAX_C for k in ETAX_KAPPA]
    if model == "E-rlin":
        return [amean + [s] for s in ERLIN_S]
    if model == "E-rq":
        return [amean + [lam, q] for lam in ERQ_LAMBDA for q in ERQ_Q]
    if model == "F0":
        return [[c, lam, q, kap] for c in F0_C for lam in F0_LAMBDA
                for q in F0_Q for kap in F0_KAPPA]
    raise SystemExit(f"REFUSED: unknown model {model}")   # pragma: no cover


def design_matrix(model: str, D: Design) -> np.ndarray | None:
    """RN-M1E-3: the closed-form witness for the LINEAR models."""
    n = len(D.y)
    if model == "E-add":
        X = np.zeros((n, 8))
        for i in range(4):
            X[:, i] = (D.si == i).astype(float)
        for j in range(4):
            X[:, 4 + j] = (D.pi == j).astype(float) - (D.pi == 4).astype(float)
        return X
    if model == "E-tax-add":
        X = np.zeros((n, 6))
        X[:, 0] = 1.0
        X[:, 1] = -D.v
        for j in range(4):
            X[:, 2 + j] = (D.pi == j).astype(float) - (D.pi == 4).astype(float)
        return X
    if model == "E-rlin":
        X = np.zeros((n, 5))
        for i in range(4):
            X[:, i] = (D.si == i).astype(float)
        X[:, 4] = D.r
        return X
    return None


def fit_model(model: str, D: Design, starts: list[list[float]] | None = None,
              witness: bool = True) -> dict[str, Any]:
    fn = MODELS[model]["fn"]

    def resid(theta: np.ndarray) -> np.ndarray:
        with np.errstate(over="ignore", invalid="ignore"):
            pred = fn(theta, D)
        pred = np.where(np.isfinite(pred), pred, 1e12)
        return pred - D.y

    best: dict[str, Any] | None = None
    sses: list[float] = []
    n_conv = 0
    grid = starts if starts is not None else starts_for(model, D)
    for s0 in grid:
        try:
            res = least_squares(resid, np.asarray(s0, float), method=OPT["method"],
                                jac="2-point", ftol=OPT["ftol"], xtol=OPT["xtol"],
                                gtol=OPT["gtol"], max_nfev=OPT["max_nfev"])
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
        raise SystemExit(f"REFUSED: no converged start for {model}")
    n = len(D.y)
    best.update({
        "model": model, "expr": MODELS[model]["expr"],
        "param_names": list(MODELS[model]["names"]), "n_starts": len(grid),
        "n_converged": n_conv,
        "n_distinct_optima": int(len({round(s, 12) for s in sses})),
        "rmse": float(np.sqrt(best["sse"] / n)), "n_rows": int(n),
        "r2_vs_mean": float(1.0 - best["sse"] / float(np.sum((D.y - D.y.mean()) ** 2))),
        "max_abs_param": float(max(abs(x) for x in best["theta"])),
    })
    if witness and MODELS[model]["linear"]:
        X = design_matrix(model, D)
        beta, *_ = np.linalg.lstsq(X, D.y, rcond=None)
        diff = float(np.max(np.abs(np.asarray(best["theta"], float) - beta)))
        best["closed_form_witness"] = {
            "lstsq_theta": [float(x) for x in beta], "max_abs_diff": diff,
            "tol": LSTSQ_TOL, "agrees": bool(diff <= LSTSQ_TOL),
            "note": RN_NOTES["RN-M1E-3"]}
    return best


def loo_rmse(model: str, D: Design, full_theta: list[float]) -> dict[str, Any]:
    n = len(D.y)
    errs, failed = [], 0
    fn = MODELS[model]["fn"]
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        Dm = D.sub(m)
        grid = starts_for(model, Dm) + [list(full_theta)]
        try:
            f = fit_model(model, Dm, starts=grid, witness=False)
        except SystemExit:
            failed += 1
            errs.append(float("nan"))
            continue
        Di = D.sub(~m)
        with np.errstate(over="ignore", invalid="ignore"):
            p = float(fn(np.asarray(f["theta"], float), Di)[0])
        errs.append(p - float(D.y[i]))
    e = np.asarray(errs, float)
    return {"model": model, "loo_error": errs, "n_failed": int(failed),
            "loo_rmse": float(np.sqrt(np.nanmean(e ** 2))),
            "loo_max_abs": float(np.nanmax(np.abs(e)))}


def _boot_means(per_world: np.ndarray, b_draws: int, seed: int, batch: int = 500):
    n_cells, n_w = per_world.shape
    rng = np.random.default_rng(seed)
    rows = np.arange(n_cells)[None, :, None]
    done = 0
    while done < b_draws:
        take = min(batch, b_draws - done)
        idx = rng.integers(0, n_w, size=(take, n_cells, n_w))
        yield per_world[rows, idx].mean(axis=2)
        done += take


def _quad_coef(resid: np.ndarray, x: np.ndarray, share: np.ndarray) -> float:
    """RN-M1E-6: OLS coefficient on x^2 with share fixed effects."""
    cols = [np.ones_like(x), x, x ** 2]
    for s in sorted(set(share.tolist()))[1:]:
        cols.append((share == s).astype(float))
    beta, *_ = np.linalg.lstsq(np.column_stack(cols), resid, rcond=None)
    return float(beta[2])


def bootstrap_model(model: str, D: Design, per_world: np.ndarray, theta0: list[float],
                    b_draws: int, seed: int, probe: bool = False) -> dict[str, Any]:
    names = list(MODELS[model]["names"])
    fn = MODELS[model]["fn"]
    draws: list[list[float]] = []
    gsum: list[float] = []
    quad: list[float] = []
    nfail = 0
    Dw = D
    for block in _boot_means(per_world, b_draws, seed):
        for means in block:
            Db = object.__new__(Design)
            for k in ("r", "v", "phi", "share", "si", "pi"):
                setattr(Db, k, getattr(Dw, k))
            Db.y = means
            try:
                f = fit_model(model, Db, starts=[list(theta0)], witness=False)
            except SystemExit:
                nfail += 1
                continue
            if not all(abs(x) < 1e6 for x in f["theta"]):
                nfail += 1
                continue
            draws.append(f["theta"])
            if model in ADDITIVE:
                gsum.append(-float(np.sum(f["theta"][-4:])))
            if probe:
                res = means - fn(np.asarray(f["theta"], float), Dw)
                quad.append(_quad_coef(res, Dw.r, Dw.share))
    arr = np.asarray(draws, float)

    def ci(a: np.ndarray) -> list[float]:
        return [float(np.quantile(a, 0.025)), float(np.quantile(a, 0.975))]

    out = {
        "B": int(b_draws), "seed": int(seed), "n_used": int(len(arr)),
        "n_discarded": int(nfail),
        "ci95": {nm: ci(arr[:, j]) for j, nm in enumerate(names)},
        "width": {nm: float(ci(arr[:, j])[1] - ci(arr[:, j])[0])
                  for j, nm in enumerate(names)},
        "median": {nm: float(np.median(arr[:, j])) for j, nm in enumerate(names)},
    }
    if gsum:
        g5 = np.asarray(gsum, float)
        out["ci95"][PN[4]] = ci(g5)
        out["width"][PN[4]] = float(ci(g5)[1] - ci(g5)[0])
        out["median"][PN[4]] = float(np.median(g5))
        out["derived_note"] = (f"{PN[4]} is the sum-to-zero derived margin; its CI is "
                               "bootstrapped from the same draws")
    if probe and quad:
        out["r2_probe_ci95"] = ci(np.asarray(quad, float))
    return out


# ---------------------------------------------------------------------------
# Rule 27.

def budget_table(model: str, fit: dict[str, Any]) -> dict[str, Any]:
    """Every parameter a consumer would quote, against its registered budget."""
    b = fit.get("bootstrap")
    if b is None:
        return {"evaluated": False,
                "reason": "not bootstrapped (only the winner and tie partners are)"}
    th = dict(zip(fit["param_names"], fit["theta"]))
    if model in ADDITIVE:
        th[PN[4]] = -float(np.sum(fit["theta"][-4:]))
    rows, all_met = [], True
    for nm, wid in b["width"].items():
        point = th.get(nm)
        if nm == "kappa":
            bud, kind = BUDGET_KAPPA_WIDTH, f"width <= {BUDGET_KAPPA_WIDTH}"
        elif nm == "c":
            bud, kind = BUDGET_C_WIDTH, f"width <= {BUDGET_C_WIDTH}"
        elif nm.startswith("g_phi"):
            bud, kind = BUDGET_G_WIDTH, f"width <= {BUDGET_G_WIDTH}"
        elif nm == "s":
            bud = BUDGET_S_FRAC * abs(point) if point else 0.0
            kind = f"width <= {int(BUDGET_S_FRAC * 100)}% of |point|"
        elif nm == "q":
            bud, kind = BUDGET_Q_WIDTH, f"width <= {BUDGET_Q_WIDTH}"
        else:
            rows.append({"parameter": nm, "point": point, "width": wid,
                         "budget": None, "budget_kind": "no budget declared "
                                                        "(RN-M1E-7)", "met": None})
            continue
        met = bool(wid <= bud)
        all_met &= met
        rows.append({"parameter": nm, "point": point, "width": wid, "budget": bud,
                     "budget_kind": kind, "met": met})
    return {"evaluated": True, "rows": rows, "all_budgeted_met": bool(all_met),
            "n_budgeted": int(sum(1 for r in rows if r["budget"] is not None)),
            "n_unbudgeted_reported": int(sum(1 for r in rows if r["budget"] is None)),
            "note": "an object missing its budget is NOT sealable regardless of routing "
                    "(rule 27)"}


SIDES = {
    "L-1e": {"clause": "an ADDITIVE form (E-add or E-tax-add) wins LOO outright over all "
                       "r-mediated forms AND F0",
             "sided": "one-sided", "improvement_side": "the additive form wins",
             "prior": "additive .45 / r-mediated .35 / F0 stands .20"},
    "L-2e": {"clause": f"the share margin IS the tax: LOO(E-tax-add) <= 1.05 x "
                       f"LOO(E-add) AND E-tax-add's kappa CI overlaps M1d's "
                       f"{list(M1D_KAPPA_CI)} (the sixth appearance)",
             "sided": "conjunction; the overlap clause two-sided",
             "improvement_side": "neither", "prior": 0.60},
    "L-3e": {"clause": "the winner's within-share r^2 probe -- quiet => SHAPE settled; "
                       "fires => shape remains open",
             "sided": "reading that ROUTES", "improvement_side": "quiet is settled",
             "prior": None},
    "rule 27 budgets": {"clause": f"kappa width <= {BUDGET_KAPPA_WIDTH}; c width <= "
                                  f"{BUDGET_C_WIDTH}; each g_phi width <= "
                                  f"{BUDGET_G_WIDTH}; s width <= "
                                  f"{int(BUDGET_S_FRAC * 100)}% of abs(point); E-rq q "
                                  f"width <= {BUDGET_Q_WIDTH}",
                        "sided": "one-sided per parameter",
                        "improvement_side": "narrower is better"},
}

TRUTH_TABLE = [
    {"n": "1", "condition": "any G0e mismatch", "outcome": "STOP",
     "text": "STOP (citation defect)"},
    {"n": "2", "condition": "additive wins AND winner's probe quiet AND budgets met",
     "outcome": "ADDITIVE_SHAPE_SETTLED",
     "text": "ADDITIVE_SHAPE_SETTLED -- r-mediation dead at level on this family; the "
             "arguments are (V, phi); M2 seals the winner at exterior-share x "
             "interior-phi cells"},
    {"n": "3", "condition": "r-mediated wins AND probe quiet AND budgets met",
     "outcome": "R_MEDIATED_SETTLED", "text": "R_MEDIATED_SETTLED -- M2 seals it"},
    {"n": "4", "condition": "F0 stands (nothing beats it)", "outcome": "NO_BETTER_SHAPE",
     "text": "NO_BETTER_SHAPE -- the M1-series closes at its measured limit: identified = "
             "level band + negative slope + tax; shape = named open; M2 re-charters on "
             "the SCOPED object (kappa-channel + model-free cell predictions)"},
    {"n": "5", "condition": "any winner AND probe fires", "outcome": "SHAPE_OPEN_NAMED",
     "text": "SHAPE_OPEN_NAMED -- same scoped-M2 route as cell 4"},
    {"n": "6", "condition": "routing would seal but budgets unmet",
     "outcome": "IDENTIFIED_INSUFFICIENTLY", "text": "IDENTIFIED_INSUFFICIENTLY -- "
                                                     "scoped-M2 route"},
    {"n": "--", "condition": "tie (<5% LOO) between an additive and an r-mediated form",
     "outcome": "REPRESENTATION_TIE",
     "text": "REPRESENTATION_TIE -- both reported, verdicts co-adjudicated, disagreement "
             "SPLIT; routing takes the SCOPED route (a tie on representation is not a "
             "settled shape)"},
    {"n": "--", "condition": "L-2e kappa disjoint", "outcome": "TAX_SHIFT",
     "text": "modifier TAX_SHIFT -> M3"},
]

STAGE_ESTIMATES_REGISTRATION = {"part0": 120, "fit": 240, "finalize": 60}
STAGE_ESTIMATES_EXECUTOR = {"part0": 120, "fit": 300, "rule13": 300, "finalize": 60,
                            "report": 30}


# ---------------------------------------------------------------------------
# PART 0.

def load_cells() -> tuple[pd.DataFrame, np.ndarray, dict[str, Any]]:
    p0c = read_json(M1CRES / "part0.json")
    persisted = read_csv_rt(M1CRES / "cell_means.csv").set_index("cell_tag")
    rows, per_world, checks = [], [], []
    for d in p0c["G1m''"]["design_points"]:
        tag = d["cell_tag"]
        parts = []
        for nm in (f"cell_{tag}_w000.csv", f"cell_{tag}_w001_191.csv"):
            path = M1CRES / "cells" / nm
            if not path.exists():
                raise SystemExit(f"REFUSED: missing rawest artifact {path}")
            parts.append(read_csv_rt(path))
        df = pd.concat(parts, ignore_index=True)
        if sorted(int(x) for x in df["world"]) != list(range(N_WORLDS)):
            raise SystemExit(f"REFUSED: {tag} world indices are not 0..{N_WORLDS - 1}")
        vals = df.sort_values("world")["recovery_b_only"].to_numpy(float)
        mean = float(vals.mean())
        sem = float(np.std(vals, ddof=1) / np.sqrt(len(vals)))
        checks.append({"cell": tag, "mean_rederived": mean,
                       "mean_persisted": float(persisted.loc[tag, "field_mean"]),
                       "mean_bit_exact": bool(mean == float(
                           persisted.loc[tag, "field_mean"])),
                       "sem_rederived": sem,
                       "sem_bit_exact": bool(sem == float(
                           persisted.loc[tag, "field_sem"]))})
        rows.append({"cell_tag": tag, "share": float(d["share"]), "phi": float(d["phi"]),
                     "r_pred": float(d["r_pred"]), "V_person": float(d["V_person"]),
                     "field_mean": mean, "field_sem": sem, "n_worlds": int(len(vals))})
        per_world.append(vals)
    g0i = {"n_cells": len(checks), "per_cell": checks,
           "PASS": bool(all(c["mean_bit_exact"] and c["sem_bit_exact"] for c in checks)),
           "source": "results/m4_m1c_r_at_level/cells/*.csv (rawest per-world), "
                     "round-trip parsed, mean over 192 worlds"}
    return pd.DataFrame(rows), np.asarray(per_world, float), g0i


def monotonicity_table(cells: pd.DataFrame) -> dict[str, Any]:
    """The Part-0 model-free object: four within-share extreme contrasts."""
    rows = []
    for s in SHARES:
        lo = cells[(cells["share"] == s) & (cells["phi"] == PHIS[0])].iloc[0]
        hi = cells[(cells["share"] == s) & (cells["phi"] == PHIS[-1])].iloc[0]
        d = float(hi["field_mean"] - lo["field_mean"])
        se = float(np.sqrt(lo["field_sem"] ** 2 + hi["field_sem"] ** 2))
        rows.append({"share": float(s), "V_person": float(lo["V_person"]),
                     "phi_lo": PHIS[0], "phi_hi": PHIS[-1],
                     "r_at_phi_lo": float(lo["r_pred"]), "r_at_phi_hi": float(hi["r_pred"]),
                     "r_span": float(lo["r_pred"] - hi["r_pred"]),
                     "field_at_phi_lo": float(lo["field_mean"]),
                     "field_at_phi_hi": float(hi["field_mean"]),
                     "contrast": d, "pooled_SE": se, "contrast_in_SE": float(d / se),
                     "sign": int(np.sign(d)),
                     "exceeds_2SE": bool(abs(d) > 2.0 * se)})
    return {"definition": "field(phi=0.98) - field(phi=0.05) within each share, with the "
                          "pooled SE of the two cell means; NO model is fitted",
            "why_here": "the parameterisation-free record of the slope sign per share -- "
                        "appendix Y's surviving invariant, and the object M1e's shape "
                        "question must explain",
            "rows": rows,
            "n_positive": int(sum(1 for x in rows if x["sign"] > 0)),
            "n_exceeding_2SE": int(sum(1 for x in rows if x["exceeds_2SE"])),
            "note": "a strictly ADDITIVE field predicts the SAME contrast at every share; "
                    "an r-mediated field predicts contrasts proportional to the share's "
                    "own r-span, which run 4.31x across shares"}


def g0e_check(cells: pd.DataFrame, g0i: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"(i) cell means from the rawest artifacts": g0i}
    fits = read_json(M1DRES / "fits.json")
    loos = read_json(M1DRES / "loo.json")
    dec = read_json(M1DRES / "decision.json")
    f0 = fits["fits"]["F0"]
    th = dict(zip(f0["param_names"], f0["theta"]))
    ci = f0["bootstrap"]["ci95"]
    l4 = dec["L-4d"]
    sh = dec["reading_v_shadow"]
    lg = dec["reading_legacy_retrodiction"]
    got = {
        "F0 c": th["c"], "F0 lambda": th["lambda"], "F0 q": th["q"],
        "F0 kappa": th["kappa"],
        "F0 c CI lo": ci["c"][0], "F0 c CI hi": ci["c"][1],
        "F0 lambda CI lo": ci["lambda"][0], "F0 lambda CI hi": ci["lambda"][1],
        "F0 q CI lo": ci["q"][0], "F0 q CI hi": ci["q"][1],
        "F0 kappa CI lo": ci["kappa"][0], "F0 kappa CI hi": ci["kappa"][1],
        "LOO F0": loos["loo"]["F0"]["loo_rmse"],
        "LOO F1e": loos["loo"]["F1e"]["loo_rmse"],
        "LOO F1": loos["loo"]["F1"]["loo_rmse"],
        "LOO Fphi": loos["loo"]["Fphi"]["loo_rmse"],
        "LOO F2": loos["loo"]["F2"]["loo_rmse"],
        "LOO F3": loos["loo"]["F3"]["loo_rmse"],
        "tie margin F0 vs F1e": fits["loo_separation"],
        "F0 vs Fphi separation pct": float(
            100.0 * fits["f0_fphi_separation"]
            / min(loos["loo"]["F0"]["loo_rmse"], loos["loo"]["Fphi"]["loo_rmse"])),
        "r2 coef": l4["r2_coef_with_share_fixed_effects"],
        "r2 CI lo B2000": l4["r2_coef_ci95_with_fixed_effects"][0],
        "r2 CI hi B2000": l4["r2_coef_ci95_with_fixed_effects"][1],
        "r2 CI lo B20000": l4["r2_coef_ci95_B20000"][0],
        "r2 CI hi B20000": l4["r2_coef_ci95_B20000"][1],
        "q_shadow": sh["q_shadow"], "q_shadow CI lo": sh["q_shadow_ci95"][0],
        "q_shadow CI hi": sh["q_shadow_ci95"][1],
        "legacy winner RMSE": lg["winner_no_refit_RMSE"],
        "legacy sealed RMSE": lg["sealed_no_refit_RMSE"],
        "legacy ratio": lg["vs_sealed_ratio"],
        "legacy k2f refit LOO": lg["k2f_refit_LOO"],
    }
    out["(ii) M1d adjudication citations"] = {
        k: {"adjudication": M1D[k], "persisted": got[k],
            "bit_exact": bool(got[k] == M1D[k])} for k in M1D}
    txt = THEORY_DOC.read_text(encoding="utf-8")
    hits = [i + 1 for i, ln in enumerate(txt.split("\n")) if THEORY_BAND_STRING in ln]
    out["(iii) theory band"] = {"string": THEORY_BAND_STRING, "found": bool(hits),
                                "lines": hits[:20], "doc": rel(THEORY_DOC)}
    out["PASS"] = bool(
        g0i["PASS"]
        and all(d["bit_exact"] for d in out["(ii) M1d adjudication citations"].values())
        and out["(iii) theory band"]["found"])
    return out


def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / "fits.json").exists():
        raise SystemExit("STOP (ordering): fits.json exists before Part 0.")
    _log("part0_start")
    cells, per_world, g0i = load_cells()
    cells.to_csv(OUT / "cell_means_rederived.csv", index=False)
    g0 = g0e_check(cells, g0i)
    mono = monotonicity_table(cells)
    D = Design(cells)
    # F0 frozen: reproduce M1d's fit exactly on the same means.
    f0_here = fit_model("F0", D)
    f0_m1d = read_json(M1DRES / "fits.json")["fits"]["F0"]
    frozen = {"theta_here": f0_here["theta"], "theta_m1d": f0_m1d["theta"],
              "sse_here": f0_here["sse"], "sse_m1d": f0_m1d["sse"],
              "bit_exact": bool(f0_here["theta"] == f0_m1d["theta"]
                                and f0_here["sse"] == f0_m1d["sse"]),
              "n_starts": f0_here["n_starts"],
              "note": "F0 is the FROZEN incumbent baseline; its refit here must reproduce "
                      "M1d's bit-exactly or the baseline is not the same object"}

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md (M4-M1e, BEFORE run, "
                        "commit af4a335)",
        "no_new_worlds": True,
        "data_source": "results/m4_m1c_r_at_level/ -- 3840 persisted worlds, 20 cell "
                       "means re-derived round-trip from the rawest per-world artifacts",
        "master_seed": MASTER_SEED, "rn_notes": RN_NOTES,
        "models": {k: {"expr": MODELS[k]["expr"], "kind": MODELS[k]["kind"],
                       "params": list(MODELS[k]["names"])
                       + ([PN[4] + " (derived, sum-to-zero)"] if k in ADDITIVE else []),
                       "n_raw": MODELS[k]["n_raw"],
                       "n_identifiable": MODELS[k]["n_identifiable"],
                       "linear": MODELS[k]["linear"],
                       "n_starts": len(starts_for(k, D))} for k in MODEL_ORDER},
        "model_free_monotonicity_table": mono,
        "f0_frozen_check": frozen,
        "optimizer": {**OPT, "scipy_version": __import__("scipy").__version__,
                      "start_grids": {
                          "E-rq (registration-pinned)": {"lambda": list(ERQ_LAMBDA),
                                                         "q": list(ERQ_Q)},
                          "E-tax-add (RN-M1E-2)": {"c": list(ETAX_C),
                                                   "kappa": list(ETAX_KAPPA)},
                          "E-rlin (RN-M1E-2)": {"s": list(ERLIN_S)},
                          "F0 (M1d verbatim)": {"c": list(F0_C), "lambda": list(F0_LAMBDA),
                                                "q": list(F0_Q), "kappa": list(F0_KAPPA)},
                          "alpha_s (RN-M1E-2)": "each at its own share's mean field"},
                      "selection": "leave-one-CELL-out RMSE across all FIVE models",
                      "closed_form_witness": RN_NOTES["RN-M1E-3"]},
        "bootstrap": {"kind": "within-cell world-block", "B": B_BOOT,
                      "B_high": B_BOOT_HIGH, "seed": MASTER_SEED,
                      "tie_rule": f"top two LOO within {TIE_REL:.0%}",
                      "rule13": f"a verdict within {BOUNDARY_REL:.0%} of its bar re-runs "
                                f"at B={B_BOOT_HIGH}"},
        "rule27_budgets": {"kappa_width_max": BUDGET_KAPPA_WIDTH,
                           "c_width_max": BUDGET_C_WIDTH,
                           "g_phi_width_max": BUDGET_G_WIDTH,
                           "s_width_max_frac_of_abs_point": BUDGET_S_FRAC,
                           "erq_q_width_max": BUDGET_Q_WIDTH,
                           "consequence": "an object missing its budget is NOT sealable "
                                          "regardless of routing",
                           "unbudgeted_reported": RN_NOTES["RN-M1E-7"]},
        "sides_rule22": SIDES,
        "rule16_truth_table": TRUTH_TABLE,
        "rule16_precedence": RN_NOTES["RN-M1E-5"],
        "stage_estimates_seconds_registration": STAGE_ESTIMATES_REGISTRATION,
        "stage_estimates_seconds_executor": STAGE_ESTIMATES_EXECUTOR,
        "environment": {"python": sys.version.split()[0],
                        "python_executable": sys.executable,
                        "platform": platform.platform(), "numpy": np.__version__,
                        "pandas": pd.__version__,
                        "scipy": __import__("scipy").__version__},
        "G0e": g0, "seconds": None,
    }
    part0["seconds"] = time.time() - t0
    write_json(OUT / "part0.json", part0)
    _write_part0_tables(part0, cells)
    _log("part0_done", seconds=part0["seconds"], G0e_PASS=g0["PASS"],
         f0_frozen=frozen["bit_exact"])
    if not g0["PASS"]:
        raise SystemExit("STOP: G0e FAILED (citation defect) -- see part0.json")
    if not frozen["bit_exact"]:
        raise SystemExit("STOP: F0 is not frozen -- its refit does not reproduce M1d's.")
    print(f"part0 OK  G0e PASS ({len(M1D)} citations + 20 means)  F0 frozen bit-exact  "
          f"monotonicity {mono['n_exceeding_2SE']}/4 shares beyond 2 SE  "
          f"{time.time() - t0:.1f}s")
    _ = args


def _cellstr(s: Any) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _md_table(header: list[str], rows: list[list[str]]) -> list[str]:
    return (["| " + " | ".join(_cellstr(h) for h in header) + " |",
             "|" + "|".join(["---"] * len(header)) + "|"]
            + ["| " + " | ".join(_cellstr(c) for c in r) + " |" for r in rows])


def _write_part0_tables(part0: dict[str, Any], cells: pd.DataFrame) -> None:
    lines = ["# M4-M1e Part 0 tables (generated from artifacts -- rule 24)", "",
             "## The five models, written before any fit", ""]
    lines += _md_table(
        ["model", "expression", "kind", "raw params", "identifiable", "linear", "starts"],
        [[k, part0["models"][k]["expr"], part0["models"][k]["kind"],
          str(part0["models"][k]["n_raw"]), str(part0["models"][k]["n_identifiable"]),
          str(part0["models"][k]["linear"]), str(part0["models"][k]["n_starts"])]
         for k in MODEL_ORDER])
    m = part0["model_free_monotonicity_table"]
    lines += ["", "## The model-free monotonicity table (no model fitted)", ""]
    lines += _md_table(
        ["share", "V", "r span", "field at phi=0.05", "field at phi=0.98", "contrast",
         "pooled SE", "contrast / SE", "> 2 SE"],
        [[repr(x["share"]), repr(x["V_person"]), repr(x["r_span"]),
          repr(x["field_at_phi_lo"]), repr(x["field_at_phi_hi"]), repr(x["contrast"]),
          repr(x["pooled_SE"]), repr(x["contrast_in_SE"]), str(x["exceeds_2SE"])]
         for x in m["rows"]])
    (OUT / "part0_tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# FIT.

def stage_fit(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    if not p0["G0e"]["PASS"]:
        raise SystemExit("STOP: G0e did not pass.")
    cells, per_world, _ = load_cells()
    D = Design(cells)

    fits: dict[str, Any] = {}
    loos: dict[str, Any] = {}
    for model in MODEL_ORDER:
        fits[model] = fit_model(model, D)
        loos[model] = loo_rmse(model, D, fits[model]["theta"])
        w = fits[model].get("closed_form_witness")
        print(f"  {model}: rmse={fits[model]['rmse']!r} loo={loos[model]['loo_rmse']!r}"
              + (f" witness_diff={w['max_abs_diff']:.3e}" if w else "")
              + f" ({time.time() - t0:.1f}s)", flush=True)

    order = sorted(MODEL_ORDER, key=lambda f: loos[f]["loo_rmse"])
    winner, runner = order[0], order[1]
    sep = loos[runner]["loo_rmse"] - loos[winner]["loo_rmse"]
    tie = bool(sep < TIE_REL * loos[winner]["loo_rmse"])
    # REPRESENTATION_TIE: a tie ACROSS the additive / r-mediated divide
    def kindof(m: str) -> str:
        return "additive" if m in ADDITIVE else "r-mediated"
    rep_tie = bool(tie and kindof(winner) != kindof(runner))

    boot_for = [winner]
    if tie and runner not in boot_for:
        boot_for.append(runner)
    if "E-tax-add" not in boot_for:
        boot_for.append("E-tax-add")          # L-2e needs its kappa CI
    if "E-add" not in boot_for and "E-add" in MODEL_ORDER:
        pass
    for model in boot_for:
        fits[model]["bootstrap"] = bootstrap_model(
            model, D, per_world, fits[model]["theta"], B_BOOT, MASTER_SEED,
            probe=(model == winner))
        print(f"  {model} bootstrap: {fits[model]['bootstrap']['n_used']}/{B_BOOT} "
              f"({time.time() - t0:.1f}s)", flush=True)

    budgets = {m: budget_table(m, fits[m]) for m in MODEL_ORDER}
    rule26 = {"note": "no model in this leg declares bounds, so rule 26's bound trigger "
                      "cannot fire; the numerical-limit surveillance is reported",
              "checks": [{"model": m, "max_abs_param": fits[m]["max_abs_param"],
                          "presses_numeric_limit": bool(fits[m]["max_abs_param"] >= 1e3),
                          "n_distinct_optima": fits[m]["n_distinct_optima"]}
                         for m in MODEL_ORDER],
              "fired": False}
    rule26["fired"] = bool(any(c["presses_numeric_limit"] for c in rule26["checks"]))

    out = {
        "utc": datetime.now(UTC).isoformat(), "n_cells": int(len(D.y)),
        "fits": fits, "ranking_by_loo": order, "winner": winner, "runner_up": runner,
        "winner_kind": kindof(winner), "runner_kind": kindof(runner),
        "loo_separation": float(sep),
        "loo_separation_rel": float(sep / loos[winner]["loo_rmse"]),
        "tie_rule_active": tie, "representation_tie": rep_tie,
        "best_additive": min(ADDITIVE, key=lambda f: loos[f]["loo_rmse"]),
        "best_r_mediated": min(R_MEDIATED, key=lambda f: loos[f]["loo_rmse"]),
        "additive_beats_all": bool(
            min(loos[f]["loo_rmse"] for f in ADDITIVE)
            < min(loos[f]["loo_rmse"] for f in R_MEDIATED + ("F0",))),
        "f0_stands": bool(winner == "F0"),
        "budgets": budgets, "rule26": rule26, "bootstrapped": boot_for,
        "boundary_flags": _boundary_flags(fits, loos, order),
        "seconds": time.time() - t0,
    }
    write_json(OUT / "fits.json", out)
    write_json(OUT / "loo.json", {"loo": loos, "ranking": order, "winner": winner})
    _log("fit_done", winner=winner, loo=loos[winner]["loo_rmse"], tie=tie,
         rep_tie=rep_tie, seconds=out["seconds"])
    print(f"fit OK  winner={winner} ({kindof(winner)})  LOO={loos[winner]['loo_rmse']!r}  "
          f"tie={tie}  representation_tie={rep_tie}  {time.time() - t0:.1f}s")
    _ = args


def _boundary_flags(fits: dict[str, Any], loos: dict[str, Any],
                    order: list[str]) -> dict[str, Any]:
    recs, flagged = [], False

    def add(name: str, value: float, bar: float, scale: float) -> bool:
        near = bool(abs(value - bar) <= BOUNDARY_REL * max(abs(scale), 1e-300))
        recs.append({"quantity": name, "value": float(value), "bar": float(bar),
                     "gap": float(value - bar), "scale": float(scale),
                     f"within_{int(BOUNDARY_REL * 100)}pct": near})
        return near

    b = fits.get("E-tax-add", {}).get("bootstrap")
    if b and "kappa" in b["ci95"]:
        klo, khi = b["ci95"]["kappa"]
        flagged |= add("E-tax-add: kappa_hi vs M1d ci95 lo", khi, M1D_KAPPA_CI[0],
                       M1D_KAPPA_CI[0])
        flagged |= add("E-tax-add: kappa_lo vs M1d ci95 hi", klo, M1D_KAPPA_CI[1],
                       M1D_KAPPA_CI[1])
    sep = loos[order[1]]["loo_rmse"] - loos[order[0]]["loo_rmse"]
    near = bool(sep <= TIE_REL * loos[order[0]]["loo_rmse"])
    recs.append({"quantity": "LOO separation winner vs runner-up", "value": float(sep),
                 "bar": 0.0, "gap": float(sep), "scale": float(loos[order[0]]["loo_rmse"]),
                 f"within_{int(BOUNDARY_REL * 100)}pct": near})
    flagged |= near
    l2 = loos["E-tax-add"]["loo_rmse"] - 1.05 * loos["E-add"]["loo_rmse"]
    near2 = bool(abs(l2) <= BOUNDARY_REL * 1.05 * loos["E-add"]["loo_rmse"])
    recs.append({"quantity": "L-2e: LOO(E-tax-add) - 1.05*LOO(E-add)", "value": float(l2),
                 "bar": 0.0, "gap": float(l2),
                 "scale": float(1.05 * loos["E-add"]["loo_rmse"]),
                 f"within_{int(BOUNDARY_REL * 100)}pct": near2})
    flagged |= near2
    return {"records": recs, "any_flagged": bool(flagged),
            "models_to_rerun": list(dict.fromkeys([order[0], "E-tax-add"]))
            if flagged else []}


def stage_rule13(args: argparse.Namespace) -> None:
    t0 = time.time()
    fits = read_json(OUT / "fits.json")
    flags = fits["boundary_flags"]
    out: dict[str, Any] = {"utc": datetime.now(UTC).isoformat(),
                           "triggered": bool(flags["any_flagged"]), "B": B_BOOT_HIGH,
                           "seed": MASTER_SEED, "models": {}, "seconds": None}
    if flags["any_flagged"]:
        cells, per_world, _ = load_cells()
        D = Design(cells)
        for model in flags["models_to_rerun"]:
            out["models"][model] = bootstrap_model(
                model, D, per_world, fits["fits"][model]["theta"], B_BOOT_HIGH,
                MASTER_SEED, probe=(model == fits["winner"]))
            print(f"  {model} B={B_BOOT_HIGH}: {out['models'][model]['n_used']} used "
                  f"({time.time() - t0:.1f}s)", flush=True)
    else:
        out["note"] = "no verdict quantity within Monte-Carlo error of its bar"
    out["seconds"] = time.time() - t0
    write_json(OUT / "boot_high.json", out)
    _log("rule13_done", triggered=out["triggered"], seconds=out["seconds"])
    print(f"rule13 OK  triggered={out['triggered']}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# FINALIZE.

def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    fits = read_json(OUT / "fits.json")
    loos = read_json(OUT / "loo.json")
    high = read_json(OUT / "boot_high.json")
    cells, per_world, _ = load_cells()
    D = Design(cells)
    winner, runner = fits["winner"], fits["runner_up"]
    wfit = fits["fits"][winner]
    wb = wfit["bootstrap"]

    # --- L-1e ---------------------------------------------------------------
    l1 = "HOLD" if fits["additive_beats_all"] else (
        "MISS (F0 stands)" if fits["f0_stands"] else "MISS (r-mediated wins)")
    # --- L-2e ---------------------------------------------------------------
    l2_loo = bool(loos["loo"]["E-tax-add"]["loo_rmse"]
                  <= 1.05 * loos["loo"]["E-add"]["loo_rmse"])
    tb = fits["fits"]["E-tax-add"]["bootstrap"]
    tklo, tkhi = tb["ci95"]["kappa"]
    tk_overlap = not (tkhi < M1D_KAPPA_CI[0] or tklo > M1D_KAPPA_CI[1])
    l2_kappa = "overlap" if tk_overlap else ("disjoint-low" if tkhi < M1D_KAPPA_CI[0]
                                             else "disjoint-high")
    l2 = "HOLD" if (l2_loo and tk_overlap) else "MISS"
    l2_high = None
    if high["triggered"] and "E-tax-add" in high["models"]:
        hlo, hhi = high["models"]["E-tax-add"]["ci95"]["kappa"]
        ov = not (hhi < M1D_KAPPA_CI[0] or hlo > M1D_KAPPA_CI[1])
        l2_high = "overlap" if ov else ("disjoint-low" if hhi < M1D_KAPPA_CI[0]
                                        else "disjoint-high")
    # --- L-3e ---------------------------------------------------------------
    resid = D.y - MODELS[winner]["fn"](np.asarray(wfit["theta"], float), D)
    q_fe = _quad_coef(resid, D.r, D.share)
    probe_ci = wb.get("r2_probe_ci95")
    probe_ci_high = (high["models"].get(winner, {}).get("r2_probe_ci95")
                     if high["triggered"] else None)
    fires = bool(probe_ci is not None and not (probe_ci[0] <= 0.0 <= probe_ci[1]))
    fires_high = (None if probe_ci_high is None
                  else bool(not (probe_ci_high[0] <= 0.0 <= probe_ci_high[1])))
    l3 = "fires" if fires else "quiet"

    # --- rule 27 ------------------------------------------------------------
    wbud = fits["budgets"][winner]
    budgets_met = bool(wbud.get("all_budgeted_met", False))

    # --- rule-16 routing, precedence RN-M1E-5 -------------------------------
    if fits["representation_tie"]:
        cell_n, slug = "--", "REPRESENTATION_TIE"
    elif fits["f0_stands"]:
        cell_n, slug = 4, "NO_BETTER_SHAPE"
    elif fires:
        cell_n, slug = 5, "SHAPE_OPEN_NAMED"
    elif not budgets_met:
        cell_n, slug = 6, "IDENTIFIED_INSUFFICIENTLY"
    elif winner in ADDITIVE:
        cell_n, slug = 2, "ADDITIVE_SHAPE_SETTLED"
    else:
        cell_n, slug = 3, "R_MEDIATED_SETTLED"
    modifier = "TAX_SHIFT" if l2_kappa in ("disjoint-low", "disjoint-high") else None
    seals = slug in ("ADDITIVE_SHAPE_SETTLED", "R_MEDIATED_SETTLED")

    # --- interaction structure notes ----------------------------------------
    th = dict(zip(wfit["param_names"], wfit["theta"]))
    if winner in ADDITIVE:
        gvals = list(wfit["theta"][-4:])
        gvals.append(-float(np.sum(gvals)))
        structure = {"kind": "additive",
                     "g_phi_curve": {PN[i]: float(gvals[i]) for i in range(5)},
                     "g_phi_ci95": {nm: wb["ci95"][nm] for nm in PN if nm in wb["ci95"]},
                     "g_phi_span": float(max(gvals) - min(gvals)),
                     "note": "the phi margin, identical at every share by construction; "
                             "the monotonicity table is what it must explain"}
    else:
        rc = ("s" if winner == "E-rlin" else "lambda")
        structure = {"kind": "r-mediated", "r_coefficient_name": rc,
                     "r_coefficient": th.get(rc), "r_coefficient_ci95": wb["ci95"].get(rc),
                     "exponent": th.get("q"), "exponent_ci95": wb["ci95"].get("q"),
                     "note": "an r-mediated field predicts within-share contrasts "
                             "proportional to each share's own r-span"}

    gates = {"G0e": {"PASS": p0["G0e"]["PASS"],
                     "detail": f"(i) all 20 cell means and SEMs bit-exact from the rawest "
                               f"artifacts; (ii) {len(M1D)} M1d adjudication citations; "
                               f"(iii) the theory band"},
             "F0 frozen": {"PASS": p0["f0_frozen_check"]["bit_exact"],
                           "detail": "the incumbent baseline reproduces M1d's fit "
                                     "bit-exactly on the same means"},
             "rule 27": {"PASS": budgets_met,
                         "detail": f"{wbud.get('n_budgeted', 0)} budgeted parameters on "
                                   f"the winner; "
                                   f"{wbud.get('n_unbudgeted_reported', 0)} reported "
                                   f"without a declared budget (RN-M1E-7)"}}

    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "no_new_worlds": True, "n_cells": int(len(D.y)),
        "model_free_monotonicity_table": p0["model_free_monotonicity_table"],
        "winner": winner, "winner_kind": fits["winner_kind"],
        "winner_expr": MODELS[winner]["expr"], "winner_theta": th,
        "winner_ci95": wb["ci95"], "winner_width": wb["width"],
        "runner_up": runner, "runner_kind": fits["runner_kind"],
        "loo_rmse_by_model": {m: loos["loo"][m]["loo_rmse"] for m in MODEL_ORDER},
        "in_sample_rmse_by_model": {m: fits["fits"][m]["rmse"] for m in MODEL_ORDER},
        "loo_separation": fits["loo_separation"],
        "loo_separation_rel": fits["loo_separation_rel"],
        "tie_rule_active": fits["tie_rule_active"],
        "representation_tie": fits["representation_tie"],
        "best_additive": fits["best_additive"], "best_r_mediated": fits["best_r_mediated"],
        "verdicts": {
            "L-1e": {"verdict": l1, "additive_beats_all": fits["additive_beats_all"],
                     "best_additive_loo": loos["loo"][fits["best_additive"]]["loo_rmse"],
                     "best_r_mediated_loo":
                         loos["loo"][fits["best_r_mediated"]]["loo_rmse"],
                     "f0_loo": loos["loo"]["F0"]["loo_rmse"]},
            "L-2e": {"verdict": l2, "loo_clause": l2_loo,
                     "loo_etaxadd": loos["loo"]["E-tax-add"]["loo_rmse"],
                     "loo_eadd": loos["loo"]["E-add"]["loo_rmse"],
                     "bar_1p05_eadd": float(1.05 * loos["loo"]["E-add"]["loo_rmse"]),
                     "kappa_clause": l2_kappa, "kappa_ci": [tklo, tkhi],
                     "m1d_kappa_ci": list(M1D_KAPPA_CI),
                     "kappa_B20000": l2_high,
                     "sixth_appearance": bool(tk_overlap)},
            "L-3e": {"verdict": l3, "r2_coef": q_fe, "r2_ci95": probe_ci,
                     "r2_ci95_B20000": probe_ci_high, "fires_B20000": fires_high,
                     "stable": bool(fires_high is None or fires_high == fires)}},
        "rule27": {"winner_budgets": wbud, "all_budgets": fits["budgets"],
                   "budgets_met": budgets_met,
                   "consequence": "an object missing its budget is NOT sealable "
                                  "regardless of routing"},
        "rule26": fits["rule26"], "rule13": {"triggered": high["triggered"],
                                             "records": fits["boundary_flags"]["records"]},
        "interaction_structure": structure,
        "routing_cell": cell_n, "verdict_slug": slug, "modifier": modifier,
        "seals": seals,
        "routing_text": next((t["text"] for t in TRUTH_TABLE
                              if t["outcome"] == slug), ""),
        "gates": gates, "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    cells.assign(residual_winner=resid).to_csv(OUT / "cell_means_rederived.csv",
                                               index=False)
    _log("finalize_done", slug=slug, seconds=dec["seconds"])
    _write_report_tables(p0, fits, loos, high, cells.assign(residual_winner=resid), dec)
    _write_prose_facts(p0, fits, loos, dec)
    print(f"finalize OK  slug={slug}  cell={cell_n}  L-1e={l1} L-2e={l2} L-3e={l3}  "
          f"budgets_met={budgets_met}  modifier={modifier}")
    _ = args


def _write_report_tables(p0: dict[str, Any], fits: dict[str, Any], loos: dict[str, Any],
                         high: dict[str, Any], cells: pd.DataFrame,
                         dec: dict[str, Any]) -> None:
    sec: dict[str, list[str]] = {}
    g0 = p0["G0e"]

    sec["models"] = _md_table(
        ["model", "expression", "kind", "raw params", "identifiable", "linear", "starts"],
        [[k, p0["models"][k]["expr"], p0["models"][k]["kind"],
          str(p0["models"][k]["n_raw"]), str(p0["models"][k]["n_identifiable"]),
          str(p0["models"][k]["linear"]), str(p0["models"][k]["n_starts"])]
         for k in MODEL_ORDER])

    m = p0["model_free_monotonicity_table"]
    sec["monotonicity"] = _md_table(
        ["share", "V", "r span", "field at phi=0.05", "field at phi=0.98", "contrast",
         "pooled SE", "contrast / SE", "> 2 SE"],
        [[repr(x["share"]), repr(x["V_person"]), repr(x["r_span"]),
          repr(x["field_at_phi_lo"]), repr(x["field_at_phi_hi"]), repr(x["contrast"]),
          repr(x["pooled_SE"]), repr(x["contrast_in_SE"]), str(x["exceeds_2SE"])]
         for x in m["rows"]])

    sec["g0e"] = _md_table(
        ["clause", "adjudication", "persisted", "bit-exact"],
        [[k, repr(d["adjudication"]), repr(d["persisted"]), str(d["bit_exact"])]
         for k, d in g0["(ii) M1d adjudication citations"].items()]
        + [["all 20 cell means and SEMs vs M1c's persisted values", "bit-exact",
            str(g0["(i) cell means from the rawest artifacts"]["PASS"]), "True"],
           [f"theory band `{g0['(iii) theory band']['string']}`",
            g0["(iii) theory band"]["string"],
            f"lines {g0['(iii) theory band']['lines']}",
            str(g0["(iii) theory band"]["found"])]])

    fz = p0["f0_frozen_check"]
    sec["frozen"] = _md_table(
        ["quantity", "this leg", "M1d", "bit-exact"],
        [["F0 theta", repr(fz["theta_here"]), repr(fz["theta_m1d"]),
          str(fz["bit_exact"])],
         ["F0 SSE", repr(fz["sse_here"]), repr(fz["sse_m1d"]), str(fz["bit_exact"])]])

    frows = []
    for mdl in MODEL_ORDER:
        f = fits["fits"][mdl]
        th = dict(zip(f["param_names"], f["theta"]))
        if mdl in ADDITIVE:
            th[PN[4]] = -float(np.sum(f["theta"][-4:]))
        b = f.get("bootstrap")
        wit = f.get("closed_form_witness")
        frows.append([
            ("**" + mdl + " (winner)**") if mdl == fits["winner"] else mdl,
            "`" + MODELS[mdl]["expr"] + "`", MODELS[mdl]["kind"],
            ", ".join(f"{k} = {v!r}" for k, v in th.items()),
            repr(f["rmse"]), repr(loos["loo"][mdl]["loo_rmse"]), repr(f["r2_vs_mean"]),
            str(f["n_distinct_optima"]),
            ("%.2e" % wit["max_abs_diff"]) if wit else "n/a (nonlinear)",
            "yes" if b else "no"])
    sec["fits"] = _md_table(
        ["model", "expression", "kind", "parameters", "in-sample RMSE", "LOO-RMSE",
         "R^2 vs mean", "distinct optima", "lstsq witness diff", "bootstrapped"], frows)

    sec["selection"] = _md_table(
        ["quantity", "value"],
        [["LOO ranking", " < ".join(fits["ranking_by_loo"])],
         ["winner", fits["winner"] + " (" + fits["winner_kind"] + ")"],
         ["runner-up", fits["runner_up"] + " (" + fits["runner_kind"] + ")"],
         ["separation", repr(fits["loo_separation"])],
         ["… as a fraction of the winner's LOO", repr(fits["loo_separation_rel"])],
         [f"tie rule active (< {TIE_REL:.0%})", str(fits["tie_rule_active"])],
         ["REPRESENTATION_TIE (tie ACROSS the additive / r-mediated divide)",
          str(fits["representation_tie"])],
         ["best additive", fits["best_additive"] + " at "
          + repr(loos["loo"][fits["best_additive"]]["loo_rmse"])],
         ["best r-mediated", fits["best_r_mediated"] + " at "
          + repr(loos["loo"][fits["best_r_mediated"]]["loo_rmse"])],
         ["F0 (frozen incumbent)", repr(loos["loo"]["F0"]["loo_rmse"])],
         ["additive beats ALL r-mediated and F0 (L-1e)",
          str(fits["additive_beats_all"])]])

    wb = dec["rule27"]["winner_budgets"]
    if wb.get("evaluated"):
        sec["budgets"] = _md_table(
            ["parameter", "point", "95% CI width", "budget", "budget rule", "met"],
            [[x["parameter"], repr(x["point"]), repr(x["width"]),
              (repr(x["budget"]) if x["budget"] is not None else "—"),
              x["budget_kind"], (str(x["met"]) if x["met"] is not None else "—")]
             for x in wb["rows"]])
    else:
        sec["budgets"] = ["_(winner not bootstrapped)_"]

    v = dec["verdicts"]
    sec["verdicts"] = _md_table(
        ["lean", "clause", "sided", "prior", "measured", "verdict"],
        [["L-1e", SIDES["L-1e"]["clause"], SIDES["L-1e"]["sided"],
          SIDES["L-1e"]["prior"],
          f"best additive {v['L-1e']['best_additive_loo']!r} vs best r-mediated "
          f"{v['L-1e']['best_r_mediated_loo']!r} vs F0 {v['L-1e']['f0_loo']!r}",
          "**" + v["L-1e"]["verdict"] + "**"],
         ["L-2e", SIDES["L-2e"]["clause"], SIDES["L-2e"]["sided"], "0.60",
          f"LOO {v['L-2e']['loo_etaxadd']!r} vs bar {v['L-2e']['bar_1p05_eadd']!r} "
          f"({v['L-2e']['loo_clause']}); kappa CI {v['L-2e']['kappa_ci']!r} vs M1d "
          f"{v['L-2e']['m1d_kappa_ci']!r} ({v['L-2e']['kappa_clause']})",
          "**" + v["L-2e"]["verdict"] + "**"],
         ["L-3e", SIDES["L-3e"]["clause"], SIDES["L-3e"]["sided"], "—",
          f"r^2 {v['L-3e']['r2_coef']!r} CI {v['L-3e']['r2_ci95']!r}",
          "**" + v["L-3e"]["verdict"] + "**"],
         ["rule 27", SIDES["rule 27 budgets"]["clause"], "one-sided per parameter", "—",
          f"{wb.get('n_budgeted', 0)} budgeted parameters on the winner",
          "**" + ("met" if dec["rule27"]["budgets_met"] else "UNMET") + "**"]])

    st = dec["interaction_structure"]
    if st["kind"] == "additive":
        sec["structure"] = _md_table(
            ["phi", "g_phi", "95% CI", "width", f"budget {BUDGET_G_WIDTH}"],
            [[nm.replace("g_phi", ""), repr(st["g_phi_curve"][nm]),
              repr(st["g_phi_ci95"].get(nm)),
              repr(dec["winner_width"].get(nm)),
              str(dec["winner_width"].get(nm, 9e9) <= BUDGET_G_WIDTH)]
             for nm in PN]
            + [["span (max - min)", repr(st["g_phi_span"]), "—", "—", "—"]])
    else:
        sec["structure"] = _md_table(
            ["quantity", "value", "95% CI"],
            [["kind", st["kind"], "—"],
             [st["r_coefficient_name"], repr(st["r_coefficient"]),
              repr(st["r_coefficient_ci95"])],
             ["exponent q", repr(st.get("exponent")), repr(st.get("exponent_ci95"))]])

    sec["truth_table"] = _md_table(
        ["#", "condition", "outcome"],
        [[t["n"], t["condition"],
          ("**" + t["text"] + "**  <-- THIS LEG") if t["outcome"] == dec["verdict_slug"]
          else t["text"]] for t in TRUTH_TABLE])

    sec["rule13"] = _md_table(
        ["quantity", "value", "bar", "scale", f"within {int(BOUNDARY_REL * 100)}%"],
        [[rec["quantity"], repr(rec["value"]), repr(rec["bar"]), repr(rec["scale"]),
          str(rec[f"within_{int(BOUNDARY_REL * 100)}pct"])]
         for rec in dec["rule13"]["records"]])

    sec["rule26"] = _md_table(
        ["model", "max abs(param)", "presses numeric limit", "distinct optima"],
        [[c["model"], repr(c["max_abs_param"]), str(c["presses_numeric_limit"]),
          str(c["n_distinct_optima"])] for c in dec["rule26"]["checks"]])

    sec["cells"] = _md_table(
        ["cell", "share", "phi", "r_pred", "V_person", "mean field", "SEM",
         "residual (winner)"],
        [[c["cell_tag"], repr(c["share"]), repr(c["phi"]), repr(c["r_pred"]),
          repr(c["V_person"]), repr(c["field_mean"]), repr(c["field_sem"]),
          repr(c["residual_winner"])] for _, c in cells.iterrows()])

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
    sec["timing"] = _md_table(
        ["stage", "registration estimate (s)", "executor estimate (s)", "measured (s)"],
        _timing_rows(p0))

    body = ["# M4-M1e report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _timing_rows(p0: dict[str, Any]) -> list[list[str]]:
    reg = p0["stage_estimates_seconds_registration"]
    ex = p0["stage_estimates_seconds_executor"]
    measured: dict[str, float] = {}
    for line in (OUT / "run_log.jsonl").read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        if rec["event"].endswith("_done") and "seconds" in rec:
            measured[rec["event"][:-5]] = float(rec["seconds"])
    return [[st, str(reg.get(st, "--")), str(ex.get(st, "--")),
             ("%.3f" % measured[st]) if st in measured else "-- (not reached)"]
            for st in ("part0", "fit", "rule13", "finalize")]


def _write_prose_facts(p0: dict[str, Any], fits: dict[str, Any], loos: dict[str, Any],
                       dec: dict[str, Any]) -> None:
    v = dec["verdicts"]
    m = dec["model_free_monotonicity_table"]
    st = dec["interaction_structure"]
    wb = dec["rule27"]["winner_budgets"]
    facts = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"], "MODIFIER": dec["modifier"] or "none",
        "SEALS": dec["seals"],
        "WINNER": dec["winner"], "WINNER_KIND": dec["winner_kind"],
        "WINNER_EXPR": dec["winner_expr"], "RUNNER": dec["runner_up"],
        "RUNNER_KIND": dec["runner_kind"],
        "WINNER_THETA": dec["winner_theta"], "WINNER_CI": dec["winner_ci95"],
        "LOO_ALL": dec["loo_rmse_by_model"], "RMSE_ALL": dec["in_sample_rmse_by_model"],
        "LOO_WINNER": loos["loo"][dec["winner"]]["loo_rmse"],
        "LOO_SEP": dec["loo_separation"], "LOO_SEP_REL": dec["loo_separation_rel"],
        "LOO_SEP_PCT": float(100.0 * dec["loo_separation_rel"]),
        "TIE_ACTIVE": dec["tie_rule_active"], "REP_TIE": dec["representation_tie"],
        "BEST_ADDITIVE": dec["best_additive"],
        "BEST_ADDITIVE_LOO": v["L-1e"]["best_additive_loo"],
        "BEST_RMED": dec["best_r_mediated"],
        "BEST_RMED_LOO": v["L-1e"]["best_r_mediated_loo"],
        "F0_LOO": v["L-1e"]["f0_loo"],
        "L1E": v["L-1e"]["verdict"], "L2E": v["L-2e"]["verdict"],
        "L3E": v["L-3e"]["verdict"],
        "L2E_LOO_CLAUSE": v["L-2e"]["loo_clause"],
        "L2E_LOO_TAX": v["L-2e"]["loo_etaxadd"], "L2E_LOO_ADD": v["L-2e"]["loo_eadd"],
        "L2E_BAR": v["L-2e"]["bar_1p05_eadd"],
        "TAX_KAPPA_CI": v["L-2e"]["kappa_ci"], "M1D_KAPPA_CI": v["L-2e"]["m1d_kappa_ci"],
        "KAPPA_CLAUSE": v["L-2e"]["kappa_clause"],
        "SIXTH": v["L-2e"]["sixth_appearance"],
        "R2_COEF": v["L-3e"]["r2_coef"], "R2_CI": v["L-3e"]["r2_ci95"],
        "R2_CI_HIGH": v["L-3e"]["r2_ci95_B20000"], "R2_STABLE": v["L-3e"]["stable"],
        "MONO_ROWS": [x["contrast"] for x in m["rows"]],
        "MONO_SE": [x["pooled_SE"] for x in m["rows"]],
        "MONO_IN_SE": [x["contrast_in_SE"] for x in m["rows"]],
        "MONO_SPANS": [x["r_span"] for x in m["rows"]],
        "MONO_N_POS": m["n_positive"], "MONO_N_2SE": m["n_exceeding_2SE"],
        "STRUCTURE_KIND": st["kind"],
        "G_CURVE": st.get("g_phi_curve"), "G_SPAN": st.get("g_phi_span"),
        "R_COEF_NAME": st.get("r_coefficient_name"), "R_COEF": st.get("r_coefficient"),
        "R_COEF_CI": st.get("r_coefficient_ci95"),
        "BUDGETS_MET": dec["rule27"]["budgets_met"],
        "N_BUDGETED": wb.get("n_budgeted"), "N_UNBUDGETED": wb.get("n_unbudgeted_reported"),
        "RULE13_TRIGGERED": dec["rule13"]["triggered"],
        "RULE26_FIRED": dec["rule26"]["fired"],
        "N_CITATIONS": len(M1D),
        "TAX_KAPPA": dict(zip(fits["fits"]["E-tax-add"]["param_names"],
                              fits["fits"]["E-tax-add"]["theta"]))["kappa"],
        "L2E_COST_PCT": float(100.0 * (v["L-2e"]["loo_etaxadd"]
                                       / v["L-2e"]["loo_eadd"] - 1.0)),
        "EADD_G": [float(x) for x in fits["fits"]["E-add"]["theta"][-4:]]
        + [-float(np.sum(fits["fits"]["E-add"]["theta"][-4:]))],
        "EADD_G_SPAN": float(max(list(fits["fits"]["E-add"]["theta"][-4:])
                                 + [-float(np.sum(fits["fits"]["E-add"]["theta"][-4:]))])
                             - min(list(fits["fits"]["E-add"]["theta"][-4:])
                                   + [-float(np.sum(
                                       fits["fits"]["E-add"]["theta"][-4:]))])),
        "GS_IDENTICAL": bool([round(x, 12) for x in fits["fits"]["E-add"]["theta"][-4:]]
                             == [round(x, 12)
                                 for x in fits["fits"]["E-tax-add"]["theta"][-4:]]),
        "WQ": dec["winner_theta"].get("q"), "WQ_CI": dec["winner_ci95"].get("q"),
        "WQ_WIDTH": dec["winner_width"].get("q"), "Q_BUDGET": BUDGET_Q_WIDTH,
        "WQ_OVER_BUDGET": float(dec["winner_width"].get("q", 0.0) / BUDGET_Q_WIDTH),
        "WLAM": dec["winner_theta"].get("lambda"),
        "WLAM_CI": dec["winner_ci95"].get("lambda"),
        "WLAM_WIDTH": dec["winner_width"].get("lambda"),
        "ALPHA_WIDTHS": [dec["winner_width"][nm] for nm in GN
                         if nm in dec["winner_width"]],
        "KAPPA_ROUTES": [0.715, 0.722, 0.750, 0.760, 0.777],
        "PHI_LADDER": list(PHIS),
        "MONO_S010_SE": m["rows"][0]["contrast_in_SE"],
        "MONO_S010_SPAN": m["rows"][0]["r_span"],
        "MONO_OTHER_MIN_SE": min(x["contrast_in_SE"] for x in m["rows"][1:]),
        "EADD_LOO": loos["loo"]["E-add"]["loo_rmse"],
        "ERLIN_LOO": loos["loo"]["E-rlin"]["loo_rmse"],
        "ERQ_LOO": loos["loo"]["E-rq"]["loo_rmse"],
        "ETAX_LOO": loos["loo"]["E-tax-add"]["loo_rmse"],
        "TAX_KAPPA_CI": v["L-2e"]["kappa_ci"],
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
        "PART0_SECONDS": p0["seconds"],
        "WITNESS_MAX": max((fits["fits"][k]["closed_form_witness"]["max_abs_diff"]
                            for k in MODEL_ORDER
                            if "closed_form_witness" in fits["fits"][k]), default=None),
    }
    write_json(OUT / "prose_facts.json", facts)


REPORT_TEMPLATE = """# M4-M1e — the shape: additive or r-mediated

**Leg:** M4-M1e · **Registered** 2026-08-11 in
`docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md` (section "M4-M1e — the shape: additive
or r-mediated"), commit `af4a335`, BEFORE this run.
**Executor:** dispatched agent (implementation and execution only; the
registration text is binding).
**Harness:** `scripts/run_suica_m4_m1e_shape.py`.
**Artifacts:** `results/m4_m1e_shape/` (gitignored).
**Banner:** artifact-space shape tournament on M1c's persisted 3840-world
corpus; no new worlds, exploratory, label-free.

**Verdict: `{{SLUG}}` (rule-16 cell {{CELL}}), modifier `{{MODIFIER}}`.**
L-1e **{{L1E}}**, L-2e **{{L2E}}**, L-3e **{{L3E}}**. Rule-27 budgets met:
**{{BUDGETS_MET}}**. Sealable: **{{SEALS}}**.

Four results, and the order matters because the last one overturns the most
comfortable thing the line believed.

**One: the field does not separate.** The best additive form (`{{BEST_ADDITIVE}}`,
LOO `{{BEST_ADDITIVE_LOO}}`) loses to the best r-mediated form
(`{{BEST_RMED}}`, `{{BEST_RMED_LOO}}`). **L-1e MISSES**; r-mediation is not dead
at level, it is the better account. The winner is **`{{WINNER}}`** —
`{{WINNER_EXPR}}` — at LOO `{{LOO_WINNER}}`, ahead of the runner-up
`{{RUNNER}}` by {{LOO_SEP_PCT}}%, well outside the tie band.

**Two: the shape probe finally goes quiet.** Under the winner the within-share
r² residual is `{{R2_COEF}}`, CI `{{R2_CI}}` — **containing zero**. The probe
that fired in M1c (−0.199) and again in M1d (−0.126) is silent once the model
carries free share margins *and* a power in r. **L-3e: quiet.** The shape
question, as the registration posed it, is answered.

**Three: and the answer is still not sealable.** Rule 27 — the rule this leg's
predecessor bought — blocks it. The winner's exponent is `q = {{WQ}}` with CI
`{{WQ_CI}}`, **width `{{WQ_WIDTH}}` against a `{{Q_BUDGET}}` budget**, missing it
by a factor of {{WQ_OVER_BUDGET}}. Selection is not identification, and here the
two come apart cleanly: the model that predicts best carries an exponent the
corpus cannot pin. Routing is cell 6, **`IDENTIFIED_INSUFFICIENTLY`** — the
scoped-M2 route, not a seal.

**Four, and this is the one to carry: κ is representation-dependent.** Forcing
the share margin through the linear tax — `E-tax-add` — costs {{L2E_COST_PCT}}%
of LOO and makes it **the worst of the five models**. And the κ it reports is
`{{TAX_KAPPA}}`, CI `{{TAX_KAPPA_CI}}` — **disjoint below** M1d's
`{{M1D_KAPPA_CI}}`. **L-2e MISSES on both clauses**, and the **`TAX_SHIFT`
modifier fires to M3**. The five prior appearances ({{KAPPA_ROUTES}}) were
appearances *within one family of representations*; change the representation
and κ moves off the band. That is M3's question, arriving earlier and sharper
than expected.

---

## Part 0 — written before any fit

### 0.1 Rule 9 / rule 12 — conventions pinned in writing

<<TABLE:rn>>

### 0.2 The five models, and the identifiability bookkeeping

<<TABLE:models>>

### 0.3 The model-free monotonicity table — the Part-0 object

Computed before any model was fitted: the within-share extreme contrast
`field(φ=0.98) − field(φ=0.05)` with the pooled SE of the two cell means. This
is appendix Y's surviving invariant in its rawest form, and it is what the shape
question must explain.

<<TABLE:monotonicity>>

All {{MONO_N_POS}} contrasts are positive; {{MONO_N_2SE}} of 4 exceed 2 SE. The
exception is decisive for the leg: at share 0.10 the contrast is
**{{MONO_S010_SE}} SE** — essentially flat — against a minimum of
{{MONO_OTHER_MIN_SE}} SE at the other three shares, and share 0.10 is exactly
where the r-span is smallest ({{MONO_S010_SPAN}} against spans {{MONO_SPANS}}). **A strictly additive
field predicts the same contrast at every share. The data do not.** The
tournament below is that observation, formalised.

### 0.4 G0e — the citations, and the frozen incumbent

<<TABLE:g0e>>

<<TABLE:frozen>>

---

## The tournament

<<TABLE:fits>>

<<TABLE:selection>>

Three of the five models are linear in their parameters and were therefore also
solved in closed form; the largest disagreement between the optimizer and
`lstsq` across all three is `{{WITNESS_MAX}}` (RN-M1E-3), so no routing decision
here rests on optimizer behaviour.

A quiet internal check worth recording: `E-add` and `E-tax-add` return
**identical** `g_φ` margins ({{GS_IDENTICAL}}) — expected, because the design is
balanced (every φ appears exactly once per share) so the sum-to-zero φ margins
are orthogonal to both the share margins and to V. The two models differ only in
how they represent the share direction, and that is precisely what their LOO gap
measures.

### The φ margin, for the record

`E-add`'s margin is `{{EADD_G}}` across φ = {{PHI_LADDER}}, a span of
`{{EADD_G_SPAN}}` — monotone rising and then flattening. It is a perfectly
reasonable curve. It simply cannot be right at every share simultaneously, which
is what the monotonicity table already said and what the LOO ranking confirms.

---

## Verdicts

<<TABLE:verdicts>>

### L-1e — the field does not separate

Best additive `{{BEST_ADDITIVE_LOO}}` vs best r-mediated `{{BEST_RMED_LOO}}` vs
F0 `{{F0_LOO}}`. The additive family does not beat the r-mediated family, so
**L-1e MISSES** against its .45 prior; the .35 complement (r-mediated wins) is
what paid. Note that `E-add` and `E-rlin` are nearly level
(`{{EADD_LOO}}` vs `{{ERLIN_LOO}}`) — the additive
representation is not *bad*, it is simply beaten, and beaten decisively only by
the model that has both free share margins and an r-power.

### L-2e — the share margin is NOT the tax

Two clauses, both failed. The LOO clause: `E-tax-add` at `{{L2E_LOO_TAX}}`
against the bar `{{L2E_BAR}}` (= 1.05 × `{{L2E_LOO_ADD}}`) — a
{{L2E_COST_PCT}}% cost, not a 5% one. Forcing the four share margins onto a
straight line in V is expensive, because they are not on one: the field's share
margins carry curvature that `−κ·V` cannot represent.

The κ clause: `{{TAX_KAPPA_CI}}` against M1d's `{{M1D_KAPPA_CI}}` —
**{{KAPPA_CLAUSE}}**. There is **no sixth appearance** ({{SIXTH}}); there is a
shift. **Modifier `TAX_SHIFT` fires to M3.**

**The honest qualification, stated because it changes how M3 should read this.**
The κ that shifted belongs to `E-tax-add`, and `E-tax-add` is the model this
same leg ranks LAST. So the finding is not "κ is 0.676"; it is
**"κ's value depends on the representation it is embedded in, and the
dependence is larger than any of its five prior confidence intervals."** The
winning model does not contain a κ at all — its share direction is four free
margins, and the tax is implicit in them. A constant that changes when you
change the surrounding form is not yet an instrument constant.

### L-3e — quiet, and that is real progress

<<TABLE:structure>>

The winner's r-coefficient is `{{WLAM}}`, CI `{{WLAM_CI}}` — **negative and
identified**, which is appendix Y's invariant reappearing in a third
parameterisation. The exponent riding on it is not: `q = {{WQ}}`, CI
`{{WQ_CI}}`.

---

## Rule 27 — the budgets, and why nothing is sealed

<<TABLE:budgets>>

{{N_BUDGETED}} parameter(s) on the winner carry a declared budget and
{{N_UNBUDGETED}} do not (RN-M1E-7, reported and gating nothing). The budgeted
one **fails**: `q`'s width `{{WQ_WIDTH}}` against `{{Q_BUDGET}}`.

This is rule 27 doing exactly the job defect #45 bought it for. Under the
pre-rule-27 routing this leg would have read "r-mediated wins, probe quiet →
`R_MEDIATED_SETTLED`, M2 seals it" and handed M2 an exponent spanning
`{{WQ_CI}}`. The rule intercepts that. The interesting detail is that the
*other* parameters are fine — the share margins run
`{{ALPHA_WIDTHS}}` wide and λ is `{{WLAM_WIDTH}}` — so the object is not
uniformly vague; it has one bad coordinate, and the budget catches precisely
that one.

For contrast, `E-tax-add` — the rejected model — **meets every budget it has**.
Being identifiable and being right are independent properties, and this leg
exhibits both directions of that independence in a single table.

---

## Routing — the rule-16 table, reproduced verbatim

<<TABLE:truth_table>>

Precedence was pinned in Part 0 (RN-M1E-5) because the registered table
overlaps. It did not bite here: with the probe quiet and budgets unmet, only
cell 6 matched. The overlap is recorded as a defect candidate below.

<<TABLE:rule13>>

<<TABLE:rule26>>

Rule 13 did not trigger ({{RULE13_TRIGGERED}}) — no verdict quantity sat within
5% of its bar. Rule 26's bound trigger cannot fire in this leg (no model
declares bounds) and the numerical-limit surveillance was clean
({{RULE26_FIRED}}).

## Gates

<<TABLE:gates>>

## Sides declared in Part 0 (rule 22)

<<TABLE:sides>>

## The cells and the winner's residuals

<<TABLE:cells>>

---

## Anomaly log — every anomaly, with pre/post-hypothesis timing

No worlds were drawn; Part 0 is verification plus the model-free table, and
every RN note was pinned there before any model was fitted.

- **A-1 — the interpreter (before Part 0).** The environment pinned in M4-M1 and
  reused since: CPython {{PYTHON}} from `requirements-lock-main.txt` (numpy
  `{{NUMPY}}`, pandas `{{PANDAS}}`, scipy `{{SCIPY}}`), platform `{{PLATFORM}}`.
- **A-2 — `timeout(1)` absent on this platform (before Part 0).** Every stage ran
  as its own foreground command under an explicit harness-level timeout.
- **A-3 — the registration's parameter counts are inconsistent (Part 0, before
  any fit).** "8 identifiable" for `E-add` is the post-pinning count; "7 params"
  for `E-tax-add` is its raw count, and that model's identifiable count under the
  same pinning is 6. Resolved by RN-M1E-1 before any fit, and reported both ways
  in the model table. Non-blocking.
- **A-4 — κ shifts on a rejected representation (at the fit).** The `TAX_SHIFT`
  modifier fires on `E-tax-add`'s κ while `E-tax-add` is the leg's worst model.
  Reported as registered and qualified above rather than suppressed or
  amplified.
- **A-5 — the winner misses its only budget (at the fit).** `q` width
  {{WQ_OVER_BUDGET}}× over. This is the routing-determining number and it is
  reported in full.
- **A-6 — no stage approached its 2× stop-and-report threshold.** Part 0
  `{{PART0_SECONDS}}` s against 120 s; the fit inside its estimate; rule 13 not
  triggered.

<<TABLE:timing>>

<<TABLE:env>>

---

## What the planner should carry forward

**The shape question is answered, and the answer is r-mediated with free share
margins.** `field ≈ α_s + λ·r^q` with λ negative and identified. The additive
separation hypothesis is rejected — not narrowly, and the model-free
monotonicity table rejected it before any model was fitted: an additive field
predicts one contrast per φ-pair everywhere, and share 0.10's contrast is
{{MONO_S010_SE}} SE against a minimum of {{MONO_OTHER_MIN_SE}} SE elsewhere, in
exact correspondence with its r-span being the smallest of the four.

**The probe is quiet for the first time in three legs.** M1c −0.199, M1d −0.126,
M1e `{{R2_COEF}}` `{{R2_CI}}`. Whatever the leftover curvature was, free share
margins plus an r-power absorb it. The M1-series' shape question closes.

**Nothing is sealable, and rule 27 is why.** The winner's exponent is
`{{WQ_CI}}`. M2 must take the scoped route: the κ-channel and model-free cell
predictions, not a shape. Note that this is the *second consecutive leg* whose
winner carries a non-identified exponent while its slope is identified — appendix
Y's reading is now supported by three independent parameterisations, and a
successor should consider registering the SLOPE (∂field/∂r at fixed V, or the
within-share contrast itself) as the sealable object rather than any exponent.

**κ is the finding M3 must absorb.** Five prior routes gave {{KAPPA_ROUTES}};
this leg's taxed representation gives `{{TAX_KAPPA}}` `{{TAX_KAPPA_CI}}`,
disjoint below all of them, while the winning representation contains no κ at
all. M3 was chartered to ask whether κ is one instrument constant. This leg
supplies a sharp prior answer: **κ's point value is representation-dependent at
a magnitude exceeding its own intervals**, so M3's design must vary the
surrounding form deliberately rather than accumulate more appearances within one
family.

**Registration-defect candidates: four, all non-blocking.**
1. **The rule-16 table overlaps** (RN-M1E-5): (F0 stands AND probe fires) matches
   cells 4 and 5; (winner AND probe fires AND budgets unmet) matches cells 5 and
   6. Immaterial to consequence — cells 4/5/6 share the scoped-M2 route — but it
   is a rule-15/16 partition failure and a successor should enumerate.
2. **Rule 27's budget list is incomplete** (RN-M1E-7): the share margins α_s and
   `E-rq`'s λ are consumed by any seal and carry no declared budget. They happen
   to be well identified here, so nothing turned on it — the same "nothing turned
   on it" that preceded defect #45.
3. **The `TAX_SHIFT` modifier is not conditioned on its host model being
   competitive.** It fires on `E-tax-add`'s κ regardless of `E-tax-add` ranking
   last. That may well be intended, but the registration does not say, and the
   evidentiary weight of a shift measured on a rejected representation is
   materially different from one measured on a winner. A successor should state
   which it means.
4. **The parameter-count wording** (A-3 above).
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
    path = ROOT / "reports" / "SUICA_M4_M1E_SHAPE_REPORT.md"
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
    for name, fn in (("part0", stage_part0), ("fit", stage_fit),
                     ("rule13", stage_rule13), ("finalize", stage_finalize),
                     ("report", stage_report)):
        s = sub.add_parser(name)
        s.set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
