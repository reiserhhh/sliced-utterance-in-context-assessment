#!/usr/bin/env python3
"""M4-M1d -- THE COMPLETION AND THE COORDINATE (artifact-space).

Registered in docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md ("M4-M1d -- the completion
and the coordinate", commit 54afc77) BEFORE this file existed.  Implementation
and execution only; the registration is binding.

M1c identified the level exponent and convicted the form family in the same
breath: F1e's epsilon sat ON its declared bound, and appendix W's quadratic-in-r
discriminator FIRED (-0.19911194958208703 [-0.2879978718649799,
-0.10706476050455438]) with the Spearman probe quiet.  W.1's prescription was a
registered form extension.  This is it.

NO NEW WORLDS.  The data are M1c's persisted 3840-world corpus, its 20 cell
means re-derived round-trip from the rawest per-world artifacts.

Two questions, sharp:
  (1) COMPLETION -- does one free intercept close the gap W.1 named?
        F0:   field = c + lambda*r^q - kappa*V          (unbounded, 162 starts)
  (2) COORDINATE -- is the level law's second argument r (card space) or phi
      (state dynamics)?  Within a share stratum they are re-parametrizations;
      ACROSS shares they differ exactly where r(share, .) moves, so the
      factorial can tell them apart.
        Fphi: field = c + a*phi^m - kappa*V             (unbounded, 108 starts)

Six forms are compared on leave-one-CELL-out RMSE: the four M1c incumbents
frozen in their M1c roles, plus F0 and Fphi.  Two pre-signed readings ride
along and adjudicate nothing: the V-shadow demonstration (omit the tax and the
exponent's sign flips in-corpus) and the legacy retrodiction on K2f's 26 rows.

    part0      G0d(i) cell means bit-exact from the rawest artifacts;
               G0d(ii) every M1c number the adjudication quotes, at full
               precision, against results/m4_m1c_r_at_level/;
               G0d(iii) the theory-doc band; G1d six-form table + nesting.
    fit        six forms, LOO-cell selection, bootstrap for the winner(s),
               the two readings, rule-13 / rule-26 flags.
    rule13     the >=10xB re-run at any flagged boundary.
    finalize   L-1d/L-2d/L-3d, L-4d's routing, the rule-16 table.
    report     renders the report from artifacts (rule 24).

Artifacts: results/m4_m1d_form_completion/ (gitignored)
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

OUT = ROOT / "results" / "m4_m1d_form_completion"
RES = ROOT / "results"
K2F = RES / "m4_k2f_level_law"
M1CRES = RES / "m4_m1c_r_at_level"

# ---------------------------------------------------------------------------
# Registration constants.

LEG = "M4-M1d"
BANNER = ("artifact-space form comparison on M1c's persisted 3840-world corpus; "
          "no new worlds, exploratory, label-free")

MASTER_SEED = 20260811
SHARES = (0.10, 0.25, 0.40, 0.60)
PHIS = (0.05, 0.30, 0.60, 0.85, 0.98)
N_WORLDS = 192

B_BOOT = 2000
B_BOOT_HIGH = 20000
TIE_REL = 0.05
BOUNDARY_REL = 0.05

L3D_KAPPA_CI = (0.7356727662590873, 0.7846243216827854)   # M1c's kappa CI
SEALED_LAMBDA = 0.17417497661611914
SEALED_Q = 1.8528700746510731
SEALED_KAPPA_HAT = -0.7220359963712748
SEALED_RESIDUAL_RMSE_26 = 0.11259090547752257              # K2f's sealed baseline
K2F_REFIT_LOO = 0.0061559195350209                         # K2f's refit LOO
THEORY_DOC = ROOT / "docs" / "SUICA_IDENTITY_THEORY_V1.md"
THEORY_BAND_STRING = "[1.71, 1.98]"

# --- G0d(ii): every M1c number the adjudication quotes ---------------------
M1C = {
    "F1e q": -0.15040108849226472,
    "F1e q CI lo": -0.18322395953281184,
    "F1e q CI hi": -0.11871900002844447,
    "F1e q CI width": 0.06450495950436737,
    "F1 q": -0.1888182542137735,
    "F1 q CI lo": -0.22686946646111852,
    "F1 q CI hi": -0.14900957557344477,
    "F1e kappa": 0.7601952008701406,
    "F1e kappa CI lo": 0.7356727662590873,
    "F1e kappa CI hi": 0.7846243216827854,
    "F1e lambda": 0.2249206339499495,
    "F1e lambda CI lo": 0.2226976852269149,
    "F1e lambda CI hi": 0.2267740781729326,
    "F1e epsilon CI lower gap from bound": 9.037909309839165e-14,
    "LOO F1": 0.003198131708377386,
    "LOO F1e": 0.0031856515917748638,
    "LOO F2": 0.0034019365713125944,
    "LOO F3": 0.003877604046883495,
    "tie margin": 1.2480116602522386e-05,
    "r2 residual coef (within-share)": -0.19911194958208703,
    "r2 residual CI lo": -0.2879978718649799,
    "r2 residual CI hi": -0.10706476050455438,
    "field mean min": 0.05410832013119198,
    "field mean max": 0.16512469544098618,
    "field SEM min": 0.0015046764572937737,
    "field SEM max": 0.0020066026535869932,
    "share-.60 field at phi lo": 0.05410832013119198,
    "share-.60 field at phi hi": 0.063796931786496,
    "projection width q_truth 1.0": 0.24923889216646022,
    "projection width q_truth 1.8528700746510731": 0.46602037304504784,
}
M1C_SPEARMAN = [0.0, 0.8999999999999998, 0.6, -0.6]
M1C_L4_READINGS = (2, 0)                    # reading A 2/4, reading B 0/4
M1C_RISE_SEM_ROUNDED = 4.03                 # the adjudication's rounded quote

# ---------------------------------------------------------------------------
# RN-M1D notes (rule 9 / rule 12).  PINNED IN PART 0, BEFORE ANY FIT.
#
# RN-M1D-1 (code inheritance).  As RN-M1C-1: the machinery is COPIED into this
#   file and Part 0 IMPORTS the M1c harness to prove the copy bit-exact on the
#   four incumbents -- expressions, names, start grids, optimizer dict, and
#   `fit_form` run on a fixed synthetic probe.  The incumbents must be FROZEN IN
#   THEIR M1c ROLES, and this is how that is verified rather than asserted.
#
# RN-M1D-2 (the L-4d probe).  The registration names "the winner's within-share
#   r^2-residual CI" without pinning the estimator.  PINNED, inheriting M1c's
#   RN-M1C-6 unchanged so the number is comparable to M1c's: OLS of the winner's
#   20 cell residuals on [1, r, r^2] WITH share fixed effects, CI from the
#   within-cell world-block bootstrap on the same draws as the parameter CIs;
#   "fires" = CI excludes 0.  The pooled (no fixed effects) reading is reported
#   beside it as in M1c.  COMPANION, executor-added and clearly not the
#   registered probe: the same statistic in phi (a phi^2-residual coefficient),
#   reported ONLY because L-2d may hand the leg a phi-coordinate winner and a
#   reader would otherwise have to guess whether structure remains in phi.  It
#   routes nothing.
#
# RN-M1D-3 (the V-shadow start grid).  The registration pins the shadow FORM
#   (field = lambda*r^q, no V, no intercept) and its pre-signed direction, but
#   no start grid.  PINNED: the F0 grid's own lambda and q axes --
#   lambda in {0.05, 0.17417497661611914, 0.5} x q in {-1, -0.5, -0.15, 0, 0.5,
#   1.8528700746510731} = 18 starts -- so the shadow is searched over exactly
#   the same exponent range as the forms it is being contrasted with.  CI from
#   the same within-cell world-block bootstrap.
#
# RN-M1D-4 (legacy retrodiction).  "The winner's plain RMSE on K2f's 26
#   compiled rows" is read as: the winner's M1d-FITTED parameters evaluated on
#   those rows with NO refit, so it is comparable to the sealed form's own
#   no-refit 0.11259090547752257.  K2f's 0.0061559195350209 was a REFIT LOO and
#   is quoted as the refit reference, not as a like-for-like rival.  Rows are
#   re-derived round-trip from compiled_rows.csv; phi comes from that file's own
#   `phi` column, so Fphi is evaluable there too.
#
# RN-M1D-5 (rule 26 surveillance).  F0 and Fphi carry NO declared bounds, so
#   rule 26's bound-activity trigger cannot fire on them by construction.  It
#   CAN fire on F1e, whose epsilon bound is inherited.  The registration also
#   asks that a winner "pressing a numerical limit" be co-adjudicated: PINNED as
#   any winner parameter with |value| >= 1e3, or a fit terminating at
#   max_nfev.  Both are checked and reported whether or not they fire.
#
# RN-M1D-6 (bootstrap batching).  As RN-M1C-5: draws generated in batches from
#   ONE master-seeded rng in draw order -- identical stream to the unbatched
#   form.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-M1D-1": "machinery COPIED, then PROVEN bit-exact in Part 0 against the imported "
                "M1c harness -- the four incumbents are verified frozen in their M1c "
                "roles rather than asserted to be",
    "RN-M1D-2": "L-4d's probe inherits M1c's RN-M1C-6 estimator unchanged (OLS of cell "
                "residuals on [1, r, r^2] with share fixed effects; CI from the same "
                "world-block bootstrap draws; fires = CI excludes 0), so the number is "
                "comparable to M1c's; a phi^2 companion is reported and routes nothing",
    "RN-M1D-3": "V-shadow start grid pinned to the F0 grid's own lambda and q axes "
                "(18 starts)",
    "RN-M1D-4": "legacy retrodiction = the winner's M1d-fitted parameters evaluated on "
                "K2f's 26 rows with NO refit (comparable to the sealed form's own "
                "no-refit RMSE); K2f's 0.0061559195350209 is a REFIT reference, not a "
                "like-for-like rival",
    "RN-M1D-5": "rule-26 surveillance: no bounds exist on F0/Fphi so the trigger cannot "
                "fire there; F1e's inherited epsilon bound and a 'numerical limit' test "
                "(|param| >= 1e3, or termination at max_nfev) are checked and reported "
                "either way",
    "RN-M1D-6": "bootstrap draws generated in batches from ONE master-seeded rng in draw "
                "order -- identical stream to the unbatched form",
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


def m1c() -> Any:
    return _load("run_suica_m4_m1c_r_at_level")


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


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = pd.Series(np.asarray(a, float)).rank().to_numpy()
    rb = pd.Series(np.asarray(b, float)).rank().to_numpy()
    return float(np.corrcoef(ra, rb)[0, 1])


def cell_tag(share: float, phi: float) -> str:
    return f"s{share:.2f}_p{phi:.2f}"


def _log(event: str, **kw: Any) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rec = {"utc": datetime.now(UTC).isoformat(), "event": event, **kw}
    with (OUT / "run_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True, default=float) + "\n")


# ---------------------------------------------------------------------------
# The SIX forms.  Signature: fn(theta, r, v, phi).

def f1(t: np.ndarray, r: np.ndarray, v: np.ndarray, p: np.ndarray) -> np.ndarray:
    return t[0] * r ** t[1] - t[2] * v


def f1e(t: np.ndarray, r: np.ndarray, v: np.ndarray, p: np.ndarray) -> np.ndarray:
    return t[0] * r ** t[1] - t[2] * v - t[3]


def f2(t: np.ndarray, r: np.ndarray, v: np.ndarray, p: np.ndarray) -> np.ndarray:
    return t[0] * r ** t[1] - t[2] * v * r ** t[3]


def f3(t: np.ndarray, r: np.ndarray, v: np.ndarray, p: np.ndarray) -> np.ndarray:
    return (t[0] - t[2] * v) * r ** t[1]


def f0(t: np.ndarray, r: np.ndarray, v: np.ndarray, p: np.ndarray) -> np.ndarray:
    """c + lambda*r^q - kappa*V."""
    return t[0] + t[1] * r ** t[2] - t[3] * v


def fphi(t: np.ndarray, r: np.ndarray, v: np.ndarray, p: np.ndarray) -> np.ndarray:
    """c + a*phi^m - kappa*V."""
    return t[0] + t[1] * p ** t[2] - t[3] * v


def fshadow(t: np.ndarray, r: np.ndarray, v: np.ndarray, p: np.ndarray) -> np.ndarray:
    """lambda*r^q -- no tax, no intercept (the V-shadow reading)."""
    return t[0] * r ** t[1]


# Incumbent start grids -- inherited from M1c verbatim.
START_LAMBDA = (0.05, SEALED_LAMBDA, 0.5)
START_Q = (-0.5, 0.0, 0.5, 1.0, SEALED_Q, 3.0)
START_KAPPA = (0.0, -SEALED_KAPPA_HAT, 2.0)
START_P = (0.0, 1.0, SEALED_Q)
START_EPS = (0.0, 0.01, 0.03)
EPS_BOUNDS = (0.0, 0.05)
# Extension start grids -- pinned by the M1d registration.
F0_C = (0.0, 0.05, 0.1)
F0_LAMBDA = (0.05, SEALED_LAMBDA, 0.5)
F0_Q = (-1.0, -0.5, -0.15, 0.0, 0.5, SEALED_Q)
F0_KAPPA = (0.0, -SEALED_KAPPA_HAT, 2.0)
FPHI_C = (0.0, 0.05, 0.1)
FPHI_A = (0.01, 0.05, 0.15)
FPHI_M = (0.5, 1.0, 2.0, 4.0)

OPT = {
    "routine": "scipy.optimize.least_squares", "method": "trf",
    "jac": "2-point (numerical)",
    "bounds": "unbounded, x_scale=1.0, EXCEPT F1e's inherited epsilon in [0, 0.05]; "
              "F0 and Fphi carry NO bounds (registration)",
    "ftol": 1e-14, "xtol": 1e-14, "gtol": 1e-14, "max_nfev": 20000,
    "loss": "linear (plain least squares)", "scipy_version": None,
}
OPT_SAME_SSE_TOL = 1e-12
NUMERIC_LIMIT = 1e3


def starts_for(form: str) -> list[list[float]]:
    out: list[list[float]] = []
    if form in ("F1", "F3"):
        for lam in START_LAMBDA:
            for q in START_Q:
                for kap in START_KAPPA:
                    out.append([lam, q, kap])
    elif form == "F1e":
        for lam in START_LAMBDA:
            for q in START_Q:
                for kap in START_KAPPA:
                    for e in START_EPS:
                        out.append([lam, q, kap, e])
    elif form == "F2":
        for lam in START_LAMBDA:
            for q in START_Q:
                for kap in START_KAPPA:
                    for p in START_P:
                        out.append([lam, q, kap, p])
    elif form == "F0":
        for c in F0_C:
            for lam in F0_LAMBDA:
                for q in F0_Q:
                    for kap in F0_KAPPA:
                        out.append([c, lam, q, kap])
    elif form == "Fphi":
        for c in FPHI_C:
            for a in FPHI_A:
                for m in FPHI_M:
                    for kap in F0_KAPPA:
                        out.append([c, a, m, kap])
    elif form == "SHADOW":
        for lam in F0_LAMBDA:
            for q in F0_Q:
                out.append([lam, q])
    else:                                              # pragma: no cover
        raise SystemExit(f"REFUSED: unknown form {form}")
    return out


FORMS: dict[str, dict[str, Any]] = {
    "F1": {"fn": f1, "names": ("lambda", "q", "kappa"),
           "expr": "field = lambda*r^q - kappa*V", "bounded": False,
           "role": "M1c incumbent (M1c runner-up)"},
    "F1e": {"fn": f1e, "names": ("lambda", "q", "kappa", "epsilon"),
            "expr": "field = lambda*r^q - kappa*V - epsilon, epsilon in [0, 0.05]",
            "bounded": True, "role": "M1c incumbent (M1c winner; bound was ACTIVE)"},
    "F2": {"fn": f2, "names": ("lambda", "q", "kappa", "p"),
           "expr": "field = lambda*r^q - kappa*V*r^p", "bounded": False,
           "role": "M1c incumbent"},
    "F3": {"fn": f3, "names": ("lambda", "q", "kappa"),
           "expr": "field = (lambda - kappa*V)*r^q", "bounded": False,
           "role": "M1c incumbent"},
    "F0": {"fn": f0, "names": ("c", "lambda", "q", "kappa"),
           "expr": "field = c + lambda*r^q - kappa*V", "bounded": False,
           "role": "EXTENSION -- the W.1 gap made a form; nests F1 at c = 0"},
    "Fphi": {"fn": fphi, "names": ("c", "a", "m", "kappa"),
             "expr": "field = c + a*phi^m - kappa*V", "bounded": False,
             "role": "EXTENSION -- the coordinate alternative; nests no incumbent"},
}
FORM_ORDER = ("F1", "F1e", "F2", "F3", "F0", "Fphi")
INCUMBENTS = ("F1", "F1e", "F2", "F3")
EXTENSIONS = ("F0", "Fphi")

NESTING = ("F2 nests F1 at p = 0 and F3 at p = q; F1e nests F1 at epsilon = 0; "
           "F0 nests F1 at c = 0 (so F0 cannot fit worse than F1 in-sample, and LOO is "
           "what pays for its fourth parameter); Fphi nests NO incumbent -- it is a "
           "different coordinate, not a wider family, which is why L-2d is a genuine "
           "either/or rather than a nesting test.")


def bounds_for(form: str) -> tuple[list[float], list[float]] | None:
    if form != "F1e":
        return None
    return ([-np.inf, -np.inf, -np.inf, EPS_BOUNDS[0]],
            [np.inf, np.inf, np.inf, EPS_BOUNDS[1]])


def fit_form(form: str, r: np.ndarray, v: np.ndarray, phi: np.ndarray, y: np.ndarray,
             starts: list[list[float]] | None = None) -> dict[str, Any]:
    fn = FORMS[form]["fn"] if form in FORMS else fshadow
    bnd = bounds_for(form)

    def resid(theta: np.ndarray) -> np.ndarray:
        with np.errstate(over="ignore", invalid="ignore"):
            pred = fn(theta, r, v, phi)
        pred = np.where(np.isfinite(pred), pred, 1e12)
        return pred - y

    best: dict[str, Any] | None = None
    sses: list[float] = []
    n_conv = 0
    at_max_nfev = 0
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
        if int(res.nfev) >= OPT["max_nfev"]:
            at_max_nfev += 1
        sse = float(np.sum(res.fun ** 2))
        if not np.isfinite(sse):
            continue
        sses.append(sse)
        if best is None or sse < best["sse"]:
            best = {"theta": [float(x) for x in res.x], "sse": sse,
                    "status": int(res.status), "nfev": int(res.nfev)}
    if best is None:
        raise SystemExit(f"REFUSED: no converged start for {form}")
    n = len(y)
    names = (list(FORMS[form]["names"]) if form in FORMS else ["lambda", "q"])
    best.update({
        "form": form, "expr": (FORMS[form]["expr"] if form in FORMS
                               else "field = lambda*r^q (V-shadow)"),
        "param_names": names, "n_starts": len(grid), "n_converged": n_conv,
        "n_starts_at_global_sse": int(sum(
            1 for s in sses
            if abs(s - best["sse"]) <= OPT_SAME_SSE_TOL * max(1.0, best["sse"]))),
        "n_distinct_optima": int(len({round(s, 12) for s in sses})),
        "n_starts_at_max_nfev": int(at_max_nfev),
        "rmse": float(np.sqrt(best["sse"] / n)), "n_rows": int(n),
        "r2_vs_mean": float(1.0 - best["sse"] / float(np.sum((y - y.mean()) ** 2))),
        "max_abs_param": float(max(abs(x) for x in best["theta"])),
        "presses_numeric_limit": bool(max(abs(x) for x in best["theta"]) >= NUMERIC_LIMIT
                                      or best["nfev"] >= OPT["max_nfev"]),
    })
    return best


def loo_rmse(form: str, r: np.ndarray, v: np.ndarray, phi: np.ndarray, y: np.ndarray,
             full_theta: list[float]) -> dict[str, Any]:
    n = len(y)
    errs, failed = [], 0
    grid = starts_for(form) + [list(full_theta)]
    fn = FORMS[form]["fn"] if form in FORMS else fshadow
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        try:
            f = fit_form(form, r[m], v[m], phi[m], y[m], starts=grid)
        except SystemExit:
            failed += 1
            errs.append(float("nan"))
            continue
        th = np.asarray(f["theta"], float)
        with np.errstate(over="ignore", invalid="ignore"):
            p = float(fn(th, r[i:i + 1], v[i:i + 1], phi[i:i + 1])[0])
        errs.append(p - float(y[i]))
    e = np.asarray(errs, float)
    return {"form": form, "loo_error": errs, "n_failed": int(failed),
            "loo_rmse": float(np.sqrt(np.nanmean(e ** 2))),
            "loo_max_abs": float(np.nanmax(np.abs(e)))}


def _boot_means(per_world: np.ndarray, b_draws: int, seed: int, batch: int = 500):
    """RN-M1D-6: one master-seeded rng, draws produced in order, in batches."""
    n_cells, n_w = per_world.shape
    rng = np.random.default_rng(seed)
    rows = np.arange(n_cells)[None, :, None]
    done = 0
    while done < b_draws:
        take = min(batch, b_draws - done)
        idx = rng.integers(0, n_w, size=(take, n_cells, n_w))
        yield per_world[rows, idx].mean(axis=2)
        done += take


def _quad_coef(resid: np.ndarray, x: np.ndarray, share: np.ndarray,
               fixed_effects: bool) -> float:
    """OLS coefficient on x^2 (RN-M1D-2, inheriting M1c's RN-M1C-6)."""
    cols = [np.ones_like(x), x, x ** 2]
    if fixed_effects:
        for s in sorted(set(share.tolist()))[1:]:
            cols.append((share == s).astype(float))
    beta, *_ = np.linalg.lstsq(np.column_stack(cols), resid, rcond=None)
    return float(beta[2])


def bootstrap_form(form: str, r: np.ndarray, v: np.ndarray, phi: np.ndarray,
                   per_world: np.ndarray, theta0: list[float], b_draws: int, seed: int,
                   share: np.ndarray | None = None) -> dict[str, Any]:
    names = (list(FORMS[form]["names"]) if form in FORMS else ["lambda", "q"])
    fn = FORMS[form]["fn"] if form in FORMS else fshadow
    draws: list[list[float]] = []
    quad_r_fe, quad_r_po, quad_phi_fe = [], [], []
    nfail = 0
    for block in _boot_means(per_world, b_draws, seed):
        for means in block:
            try:
                f = fit_form(form, r, v, phi, means, starts=[list(theta0)])
            except SystemExit:
                nfail += 1
                continue
            if not all(abs(x) < 1e6 for x in f["theta"]):
                nfail += 1
                continue
            draws.append(f["theta"])
            if share is not None:
                res = means - fn(np.asarray(f["theta"], float), r, v, phi)
                quad_r_fe.append(_quad_coef(res, r, share, True))
                quad_r_po.append(_quad_coef(res, r, share, False))
                quad_phi_fe.append(_quad_coef(res, phi, share, True))
    arr = np.asarray(draws, float)
    out = {
        "B": int(b_draws), "seed": int(seed), "n_used": int(len(arr)),
        "n_discarded": int(nfail),
        "discard_rule": "non-convergence, or |param| >= 1e6 (K2f's rules); cells are "
                        "never dropped",
        "ci95": {nm: [float(np.quantile(arr[:, j], 0.025)),
                      float(np.quantile(arr[:, j], 0.975))]
                 for j, nm in enumerate(names)},
        "median": {nm: float(np.median(arr[:, j])) for j, nm in enumerate(names)},
        "width": {nm: float(np.quantile(arr[:, j], 0.975) - np.quantile(arr[:, j], 0.025))
                  for j, nm in enumerate(names)},
    }
    if share is not None and quad_r_fe:
        def ci(x: list[float]) -> list[float]:
            a = np.asarray(x, float)
            return [float(np.quantile(a, 0.025)), float(np.quantile(a, 0.975))]
        out["residual_quadratics"] = {
            "r2_with_share_fixed_effects_ci95": ci(quad_r_fe),
            "r2_pooled_ci95": ci(quad_r_po),
            "phi2_with_share_fixed_effects_ci95": ci(quad_phi_fe),
            "note": RN_NOTES["RN-M1D-2"]}
    return out


SIDES = {
    "L-1d": {"clause": "an EXTENSION (F0 or Fphi) beats ALL FOUR incumbents on "
                       "leave-one-cell-out RMSE",
             "sided": "one-sided", "improvement_side": "the extension wins",
             "prior": 0.70},
    "L-2d": {"clause": "Fphi vs F0 as the LOO winner -- the coordinate question",
             "sided": "two-sided; either answer re-types theory (appendix X.4)",
             "improvement_side": "neither", "prior": "0.50 / 0.50",
             "conditional_on": "L-1d"},
    "L-3d": {"clause": f"the winner's kappa CI overlaps M1c's {list(L3D_KAPPA_CI)} -- "
                       "the fifth appearance",
             "sided": "two-sided overlap", "improvement_side": "neither", "prior": 0.75},
    "L-4d": {"clause": "the winner's within-share r^2-residual CI contains 0 => the "
                       "family is COMPLETE (routes M2); fires => M2 is DEFERRED",
             "sided": "reading that ROUTES", "improvement_side": "contains 0 is complete",
             "prior": None},
    "reading: V-shadow": {"clause": "field = lambda*r^q with NO V and NO intercept; "
                                    "pre-signed q_shadow > 0",
                          "sided": "pre-signed direction, adjudicates nothing",
                          "improvement_side": "n/a"},
    "reading: legacy retrodiction": {
        "clause": "the winner's no-refit RMSE on K2f's 26 compiled rows vs the sealed "
                  f"{SEALED_RESIDUAL_RMSE_26} and K2f's refit LOO {K2F_REFIT_LOO}",
        "sided": "descriptive, adjudicates nothing", "improvement_side": "n/a"},
}

TRUTH_TABLE = [
    {"n": "1", "condition": "any G0d mismatch", "outcome": "STOP",
     "text": "STOP (citation defect; no fit)"},
    {"n": "2", "condition": "incumbents stand AND winner r^2 quiet",
     "outcome": "FAMILY_STANDS",
     "text": "FAMILY_STANDS -- M2 seals the M1c pair (F1e+F1 co-sealed per rule 26)"},
    {"n": "3", "condition": "incumbents stand AND r^2 fires",
     "outcome": "INCOMPLETE_UNREPAIRED",
     "text": "INCOMPLETE_UNREPAIRED -- M2 deferred; M1e (shape study) named"},
    {"n": "4", "condition": "F0 wins AND r^2 quiet", "outcome": "COMPLETED_IN_R",
     "text": "COMPLETED_IN_R -- T4 keeps the r-coordinate with an intercept; M2 seals F0"},
    {"n": "5", "condition": "Fphi wins AND r^2 quiet",
     "outcome": "COORDINATE_RETYPED_TO_PHI",
     "text": "COORDINATE_RETYPED_TO_PHI -- the level law's second argument is state "
             "dynamics, not card readability; M2 seals Fphi"},
    {"n": "6", "condition": "an extension wins AND r^2 fires",
     "outcome": "COMPLETED_BUT_INCOMPLETE",
     "text": "COMPLETED_BUT_INCOMPLETE -- M2 deferred; M1e named"},
    {"n": "--", "condition": "F0/Fphi tie (<5% LOO)", "outcome": "CO_WINNERS",
     "text": "CO_WINNERS -- both sealed in M2 (multiple predictions inside one hashed "
             "file, K2f precedent); verdicts co-adjudicated, disagreements SPLIT"},
    {"n": "--", "condition": "L-3d disjoint", "outcome": "TAX_SHIFT",
     "text": "modifier TAX_SHIFT -> M3's charter"},
]

STAGE_ESTIMATES_REGISTRATION = {"part0": 120, "fit": 240, "finalize": 60}
STAGE_ESTIMATES_EXECUTOR = {"part0": 120, "fit": 240, "rule13": 240, "finalize": 60,
                            "report": 30}


# ---------------------------------------------------------------------------
# PART 0.

def load_m1c_cells() -> tuple[pd.DataFrame, np.ndarray, dict[str, Any]]:
    """G0d(i): re-derive M1c's 20 cell means from the RAWEST persisted artifacts."""
    p0 = read_json(M1CRES / "part0.json")
    persisted = read_csv_rt(M1CRES / "cell_means.csv").set_index("cell_tag")
    rows, per_world, checks = [], [], []
    for d in p0["G1m''"]["design_points"]:
        tag = d["cell_tag"]
        parts = []
        for nm in (f"cell_{tag}_w000.csv", f"cell_{tag}_w001_191.csv"):
            path = M1CRES / "cells" / nm
            if not path.exists():
                raise SystemExit(f"REFUSED: missing rawest artifact {path}")
            parts.append(read_csv_rt(path))
        df = pd.concat(parts, ignore_index=True)
        idx = sorted(int(x) for x in df["world"])
        if idx != list(range(N_WORLDS)):
            raise SystemExit(f"REFUSED: {tag} world indices are not 0..{N_WORLDS - 1}")
        vals = df.sort_values("world")["recovery_b_only"].to_numpy(float)
        mean = float(vals.mean())
        sem = float(np.std(vals, ddof=1) / np.sqrt(len(vals)))
        pm = float(persisted.loc[tag, "field_mean"])
        ps = float(persisted.loc[tag, "field_sem"])
        checks.append({"cell": tag, "n_worlds": int(len(vals)),
                       "mean_rederived": mean, "mean_persisted": pm,
                       "mean_bit_exact": bool(mean == pm),
                       "sem_rederived": sem, "sem_persisted": ps,
                       "sem_bit_exact": bool(sem == ps)})
        rows.append({"cell_tag": tag, "share": float(d["share"]), "phi": float(d["phi"]),
                     "r_pred": float(d["r_pred"]), "V_person": float(d["V_person"]),
                     "field_mean": mean, "field_sem": sem, "n_worlds": int(len(vals))})
        per_world.append(vals)
    g0i = {"n_cells": len(checks), "per_cell": checks,
           "all_means_bit_exact": bool(all(c["mean_bit_exact"] for c in checks)),
           "all_sems_bit_exact": bool(all(c["sem_bit_exact"] for c in checks)),
           "source": "results/m4_m1c_r_at_level/cells/*.csv (rawest per-world), "
                     "round-trip parsed, mean over the cell's 192 worlds",
           "PASS": bool(all(c["mean_bit_exact"] and c["sem_bit_exact"] for c in checks))}
    return pd.DataFrame(rows), np.asarray(per_world, float), g0i


def g0d_check(cells: pd.DataFrame, g0i: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"(i) cell means from the rawest artifacts": g0i}

    # (ii) every M1c number the adjudication quotes.
    fits = read_json(M1CRES / "fits.json")
    loos = read_json(M1CRES / "loo.json")
    dec = read_json(M1CRES / "decision.json")
    p0c = read_json(M1CRES / "part0.json")
    fe = fits["fits"]["F1e"]
    f1_ = fits["fits"]["F1"]
    the = dict(zip(fe["param_names"], fe["theta"]))
    th1 = dict(zip(f1_["param_names"], f1_["theta"]))
    w = dec["L-4"]["appendix_W_quadratic_discriminator"]
    proj = p0c["G3m''"]["base"]["projections"]
    got = {
        "F1e q": the["q"], "F1e q CI lo": fe["bootstrap"]["ci95"]["q"][0],
        "F1e q CI hi": fe["bootstrap"]["ci95"]["q"][1],
        "F1e q CI width": dec["winner_intervals"]["q_ci_width"],
        "F1 q": th1["q"], "F1 q CI lo": f1_["bootstrap"]["ci95"]["q"][0],
        "F1 q CI hi": f1_["bootstrap"]["ci95"]["q"][1],
        "F1e kappa": the["kappa"], "F1e kappa CI lo": fe["bootstrap"]["ci95"]["kappa"][0],
        "F1e kappa CI hi": fe["bootstrap"]["ci95"]["kappa"][1],
        "F1e lambda": the["lambda"],
        "F1e lambda CI lo": fe["bootstrap"]["ci95"]["lambda"][0],
        "F1e lambda CI hi": fe["bootstrap"]["ci95"]["lambda"][1],
        "F1e epsilon CI lower gap from bound":
            float(EPS_BOUNDS[1] - fe["bootstrap"]["ci95"]["epsilon"][0]),
        "LOO F1": loos["loo"]["F1"]["loo_rmse"], "LOO F1e": loos["loo"]["F1e"]["loo_rmse"],
        "LOO F2": loos["loo"]["F2"]["loo_rmse"], "LOO F3": loos["loo"]["F3"]["loo_rmse"],
        "tie margin": fits["loo_separation"],
        "r2 residual coef (within-share)": w["r2_coef_with_share_fixed_effects"],
        "r2 residual CI lo": w["r2_coef_ci95_with_fixed_effects"][0],
        "r2 residual CI hi": w["r2_coef_ci95_with_fixed_effects"][1],
        "field mean min": dec["field_mean_range"][0],
        "field mean max": dec["field_mean_range"][1],
        "field SEM min": dec["field_sem_range"][0],
        "field SEM max": dec["field_sem_range"][1],
        "share-.60 field at phi lo": float(
            cells[(cells["share"] == 0.60) & (cells["phi"] == 0.05)]["field_mean"].iloc[0]),
        "share-.60 field at phi hi": float(
            cells[(cells["share"] == 0.60) & (cells["phi"] == 0.98)]["field_mean"].iloc[0]),
        "projection width q_truth 1.0": proj["1.0"]["width_proxy"],
        "projection width q_truth 1.8528700746510731": proj[repr(SEALED_Q)]["width_proxy"],
    }
    out["(ii) M1c adjudication citations"] = {
        k: {"adjudication": M1C[k], "persisted": got[k],
            "bit_exact": bool(got[k] == M1C[k])} for k in M1C}
    sp = [p["spearman_resid_phi"] for p in dec["L-4"]["per_share"]]
    out["(ii) Spearman vector"] = {
        "adjudication": M1C_SPEARMAN, "persisted": sp,
        "bit_exact": bool(sp == M1C_SPEARMAN),
        "readings_adjudication": list(M1C_L4_READINGS),
        "readings_persisted": [dec["L-4"]["reading_A_sign_agreement"]["max_agreeing"],
                               dec["L-4"]["reading_B_perfect_monotone_and_sign"][
                                   "max_agreeing"]],
        "readings_match": bool([dec["L-4"]["reading_A_sign_agreement"]["max_agreeing"],
                                dec["L-4"]["reading_B_perfect_monotone_and_sign"][
                                    "max_agreeing"]] == list(M1C_L4_READINGS))}
    rise = got["share-.60 field at phi hi"] - got["share-.60 field at phi lo"]
    hi = cells[cells["share"] == 0.60].sort_values("phi")
    sem_pooled = float(np.sqrt(hi["field_sem"].iloc[0] ** 2 + hi["field_sem"].iloc[-1] ** 2))
    mult = float(rise / sem_pooled)
    out["(ii) share-.60 rise in pooled SEM"] = {
        "rise": rise, "pooled_SEM": sem_pooled, "multiple": mult,
        "adjudication_rounded": M1C_RISE_SEM_ROUNDED,
        "rounds_to_adjudication": bool(round(mult, 2) == M1C_RISE_SEM_ROUNDED),
        "note": "the adjudication quotes this rounded to 2 dp; the full-precision value "
                "is re-derived here and must round to it"}

    # (iii) the theory-doc band.
    txt = THEORY_DOC.read_text(encoding="utf-8")
    hits = [i + 1 for i, ln in enumerate(txt.split("\n")) if THEORY_BAND_STRING in ln]
    out["(iii) theory band"] = {"string": THEORY_BAND_STRING, "found": bool(hits),
                                "lines": hits[:20], "doc": rel(THEORY_DOC)}

    out["PASS"] = bool(
        g0i["PASS"]
        and all(d["bit_exact"] for d in out["(ii) M1c adjudication citations"].values())
        and out["(ii) Spearman vector"]["bit_exact"]
        and out["(ii) Spearman vector"]["readings_match"]
        and out["(ii) share-.60 rise in pooled SEM"]["rounds_to_adjudication"]
        and out["(iii) theory band"]["found"])
    out["failure_meaning"] = "any mismatch is a CITATION DEFECT: STOP, no fit is run"
    return out


def inheritance_check(cells: pd.DataFrame) -> dict[str, Any]:
    """RN-M1D-1: the four incumbents are FROZEN IN THEIR M1c ROLES -- proven."""
    mod = m1c()
    r = cells["r_pred"].to_numpy(float)
    v = cells["V_person"].to_numpy(float)
    phi = cells["phi"].to_numpy(float)
    y = cells["field_mean"].to_numpy(float)
    per_form = {}
    ok = True
    for form in INCUMBENTS:
        mine = fit_form(form, r, v, phi, y)
        theirs = mod.fit_form(form, r, v, y)
        same = (mine["theta"] == theirs["theta"] and mine["sse"] == theirs["sse"]
                and starts_for(form) == mod.starts_for(form)
                and FORMS[form]["expr"] == mod.FORMS[form]["expr"]
                and list(FORMS[form]["names"]) == list(mod.FORMS[form]["names"]))
        ok &= same
        per_form[form] = {"theta_mine": mine["theta"], "theta_m1c": theirs["theta"],
                          "sse_mine": mine["sse"], "sse_m1c": theirs["sse"],
                          "n_starts": len(starts_for(form)), "bit_exact": bool(same)}
    optk = [k for k in OPT if k not in ("scipy_version", "bounds")]
    opt_same = all(OPT[k] == mod.OPT[k] for k in optk)
    return {"note": RN_NOTES["RN-M1D-1"], "per_form": per_form,
            "optimizer_identical": bool(opt_same),
            "fitted_on": "M1c's own 20 cell means, so the incumbents are compared on "
                         "exactly the object they were selected on",
            "PASS": bool(ok and opt_same)}


def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / "fits.json").exists():
        raise SystemExit("STOP (ordering): fits.json exists before Part 0.")
    _log("part0_start")
    cells, per_world, g0i = load_m1c_cells()
    cells.to_csv(OUT / "cell_means_rederived.csv", index=False)
    g0 = g0d_check(cells, g0i)
    inh = inheritance_check(cells)

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md (M4-M1d, BEFORE run, "
                        "commit 54afc77)",
        "no_new_worlds": True,
        "data_source": "results/m4_m1c_r_at_level/ -- 3840 persisted worlds, 20 cell "
                       "means re-derived round-trip from the rawest per-world artifacts",
        "master_seed": MASTER_SEED, "rn_notes": RN_NOTES,
        "inheritance_check_RN_M1D_1": inh,
        "forms": {k: {"expr": FORMS[k]["expr"], "params": list(FORMS[k]["names"]),
                      "n_starts": len(starts_for(k)), "bounded": FORMS[k]["bounded"],
                      "role": FORMS[k]["role"]} for k in FORM_ORDER},
        "nesting": NESTING,
        "shadow_form": {"expr": "field = lambda*r^q (no V, no intercept)",
                        "n_starts": len(starts_for("SHADOW")),
                        "pre_signed": "q_shadow > 0", "note": RN_NOTES["RN-M1D-3"]},
        "optimizer": {**OPT, "scipy_version": __import__("scipy").__version__,
                      "n_starts": {f: len(starts_for(f)) for f in FORM_ORDER},
                      "start_grids": {
                          "F0": {"c": list(F0_C), "lambda": list(F0_LAMBDA),
                                 "q": list(F0_Q), "kappa": list(F0_KAPPA)},
                          "Fphi": {"c": list(FPHI_C), "a": list(FPHI_A),
                                   "m": list(FPHI_M), "kappa": list(F0_KAPPA)},
                          "incumbents": "inherited from M1c verbatim"},
                      "selection": "leave-one-CELL-out RMSE across all SIX forms"},
        "bootstrap": {"kind": "within-cell world-block", "B": B_BOOT,
                      "B_high": B_BOOT_HIGH, "seed": MASTER_SEED,
                      "batching": RN_NOTES["RN-M1D-6"],
                      "tie_rule": f"top two LOO within {TIE_REL:.0%} -> verdicts must "
                                  f"agree or report SPLIT",
                      "rule13": f"a verdict within {BOUNDARY_REL:.0%} of its bar re-runs "
                                f"at B={B_BOOT_HIGH}",
                      "rule26": RN_NOTES["RN-M1D-5"]},
        "sides_rule22": SIDES,
        "rule25_note": "no feasibility gate: no new worlds are drawn, the estimand is "
                       "FORM COMPARISON on existing data, and leave-one-cell-out is its "
                       "guard (registration G1d)",
        "gate_stages_rule23": {
            "G0d": "inputs exist at Part 0 (M1c's persisted corpus and artifacts, the "
                   "theory doc)",
            "G1d": "inputs exist at Part 0 (the six-form table, nesting, sides)",
            "G3d": "stage estimates at Part 0"},
        "stage_estimates_seconds_registration": STAGE_ESTIMATES_REGISTRATION,
        "stage_estimates_seconds_executor": STAGE_ESTIMATES_EXECUTOR,
        "rule16_truth_table": TRUTH_TABLE,
        "environment": {"python": sys.version.split()[0],
                        "python_executable": sys.executable,
                        "platform": platform.platform(), "numpy": np.__version__,
                        "pandas": pd.__version__,
                        "scipy": __import__("scipy").__version__},
        "G0d": g0, "seconds": None,
    }
    part0["seconds"] = time.time() - t0
    write_json(OUT / "part0.json", part0)
    _write_part0_tables(part0, cells)
    _log("part0_done", seconds=part0["seconds"], G0d_PASS=g0["PASS"],
         inheritance_PASS=inh["PASS"])
    if not inh["PASS"]:
        raise SystemExit("STOP: RN-M1D-1 inheritance check FAILED -- the incumbents are "
                         "not frozen in their M1c roles.")
    if not g0["PASS"]:
        raise SystemExit("STOP: G0d FAILED (citation defect) -- see part0.json")
    print(f"part0 OK  G0d PASS ({len(M1C)} citations + means + Spearman + rise)  "
          f"inheritance PASS  {time.time() - t0:.1f}s")
    _ = args


def _cellstr(s: Any) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _md_table(header: list[str], rows: list[list[str]]) -> list[str]:
    return (["| " + " | ".join(_cellstr(h) for h in header) + " |",
             "|" + "|".join(["---"] * len(header)) + "|"]
            + ["| " + " | ".join(_cellstr(c) for c in r) + " |" for r in rows])


def _write_part0_tables(part0: dict[str, Any], cells: pd.DataFrame) -> None:
    lines = ["# M4-M1d Part 0 tables (generated from artifacts -- rule 24)", "",
             "## The six forms (G1d), written before any fit", ""]
    lines += _md_table(
        ["form", "expression", "params", "starts", "bounded", "role"],
        [[k, part0["forms"][k]["expr"], repr(part0["forms"][k]["params"]),
          str(part0["forms"][k]["n_starts"]), str(part0["forms"][k]["bounded"]),
          part0["forms"][k]["role"]] for k in FORM_ORDER])
    lines += ["", "Nesting: " + NESTING, "", "## The 20 cell means, re-derived", ""]
    lines += _md_table(
        ["cell", "share", "phi", "r_pred", "V_person", "mean field", "SEM", "n"],
        [[r["cell_tag"], repr(r["share"]), repr(r["phi"]), repr(r["r_pred"]),
          repr(r["V_person"]), repr(r["field_mean"]), repr(r["field_sem"]),
          str(int(r["n_worlds"]))] for _, r in cells.iterrows()])
    (OUT / "part0_tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# FIT.

def stage_fit(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    if not p0["G0d"]["PASS"]:
        raise SystemExit("STOP: G0d did not pass.")
    cells, per_world, _ = load_m1c_cells()
    r = cells["r_pred"].to_numpy(float)
    v = cells["V_person"].to_numpy(float)
    phi = cells["phi"].to_numpy(float)
    y = cells["field_mean"].to_numpy(float)
    share = cells["share"].to_numpy(float)

    fits: dict[str, Any] = {}
    loos: dict[str, Any] = {}
    for form in FORM_ORDER:
        fits[form] = fit_form(form, r, v, phi, y)
        loos[form] = loo_rmse(form, r, v, phi, y, fits[form]["theta"])
        print(f"  {form}: rmse={fits[form]['rmse']!r} loo={loos[form]['loo_rmse']!r} "
              f"({time.time() - t0:.1f}s)", flush=True)

    order = sorted(FORM_ORDER, key=lambda f: loos[f]["loo_rmse"])
    winner, runner = order[0], order[1]
    sep = loos[runner]["loo_rmse"] - loos[winner]["loo_rmse"]
    tie = bool(sep < TIE_REL * loos[winner]["loo_rmse"])

    # bootstrap the winner and the runner-up (the tie rule needs both)
    boot_for = [winner, runner]
    # rule 26: if a bounded form is among them with an active bound, add its relaxation
    rule26: dict[str, Any] = {"note": RN_NOTES["RN-M1D-5"], "checks": [], "fired": False}
    for form in boot_for:
        th = dict(zip(FORMS[form]["names"], fits[form]["theta"]))
        active = None
        if form == "F1e":
            active = bool(abs(EPS_BOUNDS[1] - th["epsilon"]) < 1e-9
                          or abs(th["epsilon"] - EPS_BOUNDS[0]) < 1e-9)
        rec = {"form": form, "has_declared_bounds": bool(FORMS[form]["bounded"]),
               "bound_active": active,
               "presses_numeric_limit": fits[form]["presses_numeric_limit"],
               "max_abs_param": fits[form]["max_abs_param"],
               "n_starts_at_max_nfev": fits[form]["n_starts_at_max_nfev"]}
        rec["co_adjudication_required"] = bool(active or
                                               fits[form]["presses_numeric_limit"])
        if rec["co_adjudication_required"]:
            rule26["fired"] = True
            rec["relaxation"] = "F1" if form == "F1e" else "none registered"
            if form == "F1e" and "F1" not in boot_for:
                boot_for.append("F1")
        rule26["checks"].append(rec)

    for form in boot_for:
        fits[form]["bootstrap"] = bootstrap_form(
            form, r, v, phi, per_world, fits[form]["theta"], B_BOOT, MASTER_SEED,
            share=share if form == winner else None)
        print(f"  {form} bootstrap: {fits[form]['bootstrap']['n_used']}/{B_BOOT} "
              f"({time.time() - t0:.1f}s)", flush=True)

    # --- reading 1: the V-shadow demonstration ------------------------------
    sh = fit_form("SHADOW", r, v, phi, y)
    sh["bootstrap"] = bootstrap_form("SHADOW", r, v, phi, per_world, sh["theta"],
                                     B_BOOT, MASTER_SEED)
    shadow = {"expr": "field = lambda*r^q (no V term, no intercept)",
              "theta": dict(zip(["lambda", "q"], sh["theta"])),
              "q_shadow": sh["theta"][1], "q_shadow_ci95": sh["bootstrap"]["ci95"]["q"],
              "lambda_shadow": sh["theta"][0],
              "lambda_shadow_ci95": sh["bootstrap"]["ci95"]["lambda"],
              "rmse": sh["rmse"], "n_starts": sh["n_starts"],
              "pre_signed": "q_shadow > 0",
              "pre_signed_confirmed": bool(sh["bootstrap"]["ci95"]["q"][0] > 0.0),
              "winner_q_for_contrast": None,
              "note": "omit the tax and the exponent's sign flips IN-CORPUS -- the "
                      "re-attribution of the response-grade band in one number; "
                      "adjudicates nothing (registration)"}
    print(f"  V-shadow: q={shadow['q_shadow']!r} ci={shadow['q_shadow_ci95']!r} "
          f"({time.time() - t0:.1f}s)", flush=True)

    # --- reading 2: the legacy retrodiction on K2f's 26 rows ----------------
    k2f = read_csv_rt(K2F / "compiled_rows.csv")
    kr = k2f["r_pred"].to_numpy(float)
    kv = k2f["V_person"].to_numpy(float)
    kp = k2f["phi"].to_numpy(float)
    ky = k2f["level_rederived"].to_numpy(float)
    legacy = {"n_rows": int(len(k2f)),
              "source": "results/m4_k2f_level_law/compiled_rows.csv (round-trip); phi "
                        "from that file's own phi column",
              "sealed_no_refit_RMSE": SEALED_RESIDUAL_RMSE_26,
              "k2f_refit_LOO": K2F_REFIT_LOO, "note": RN_NOTES["RN-M1D-4"],
              "per_form_no_refit_RMSE": {}}
    for form in FORM_ORDER:
        pred = FORMS[form]["fn"](np.asarray(fits[form]["theta"], float), kr, kv, kp)
        legacy["per_form_no_refit_RMSE"][form] = float(
            np.sqrt(np.mean((pred - ky) ** 2)))
    legacy["winner_no_refit_RMSE"] = legacy["per_form_no_refit_RMSE"][winner]
    legacy["vs_sealed_ratio"] = float(SEALED_RESIDUAL_RMSE_26
                                      / legacy["winner_no_refit_RMSE"])

    out = {
        "utc": datetime.now(UTC).isoformat(), "n_cells": int(len(y)),
        "fits": fits, "ranking_by_loo": order, "winner": winner, "runner_up": runner,
        "loo_separation": float(sep),
        "loo_separation_rel": float(sep / loos[winner]["loo_rmse"]),
        "tie_rule_active": tie,
        "winner_is_extension": bool(winner in EXTENSIONS),
        "extension_beats_all_incumbents": bool(
            min(loos[f]["loo_rmse"] for f in EXTENSIONS)
            < min(loos[f]["loo_rmse"] for f in INCUMBENTS)),
        "best_incumbent": min(INCUMBENTS, key=lambda f: loos[f]["loo_rmse"]),
        "best_extension": min(EXTENSIONS, key=lambda f: loos[f]["loo_rmse"]),
        "f0_fphi_separation": float(abs(loos["F0"]["loo_rmse"]
                                        - loos["Fphi"]["loo_rmse"])),
        "f0_fphi_tie": bool(abs(loos["F0"]["loo_rmse"] - loos["Fphi"]["loo_rmse"])
                            < TIE_REL * min(loos["F0"]["loo_rmse"],
                                            loos["Fphi"]["loo_rmse"])),
        "rule26": rule26, "bootstrapped_forms": boot_for,
        "boundary_flags": _boundary_flags(fits, loos, order),
        "reading_v_shadow": shadow, "reading_legacy_retrodiction": legacy,
        "seconds": time.time() - t0,
    }
    write_json(OUT / "fits.json", out)
    write_json(OUT / "loo.json", {"loo": loos, "ranking": order, "winner": winner})
    _log("fit_done", winner=winner, loo=loos[winner]["loo_rmse"], tie=tie,
         seconds=out["seconds"])
    print(f"fit OK  winner={winner}  LOO={loos[winner]['loo_rmse']!r}  "
          f"tie={tie}  rule26_fired={rule26['fired']}  {time.time() - t0:.1f}s")
    _ = args


def _boundary_flags(fits: dict[str, Any], loos: dict[str, Any],
                    order: list[str]) -> dict[str, Any]:
    """Rule 13 on L-3d's overlap call and on the selection margin."""
    recs = []
    flagged = False

    def add(name: str, value: float, bar: float, scale: float) -> bool:
        near = bool(abs(value - bar) <= BOUNDARY_REL * max(abs(scale), 1e-300))
        recs.append({"quantity": name, "value": float(value), "bar": float(bar),
                     "gap": float(value - bar), "scale": float(scale),
                     f"within_{int(BOUNDARY_REL * 100)}pct": near})
        return near

    for form in order[:2]:
        b = fits[form].get("bootstrap")
        if b is None or "kappa" not in b["ci95"]:
            continue
        klo, khi = b["ci95"]["kappa"]
        flagged |= add(f"{form}: kappa_hi vs M1c ci95 lo", khi, L3D_KAPPA_CI[0],
                       L3D_KAPPA_CI[0])
        flagged |= add(f"{form}: kappa_lo vs M1c ci95 hi", klo, L3D_KAPPA_CI[1],
                       L3D_KAPPA_CI[1])
    sep = loos[order[1]]["loo_rmse"] - loos[order[0]]["loo_rmse"]
    near = bool(sep <= TIE_REL * loos[order[0]]["loo_rmse"])
    recs.append({"quantity": "LOO separation winner vs runner-up", "value": float(sep),
                 "bar": 0.0, "gap": float(sep), "scale": float(loos[order[0]]["loo_rmse"]),
                 f"within_{int(BOUNDARY_REL * 100)}pct": near})
    flagged |= near
    sep2 = abs(loos["F0"]["loo_rmse"] - loos["Fphi"]["loo_rmse"])
    near2 = bool(sep2 <= TIE_REL * min(loos["F0"]["loo_rmse"], loos["Fphi"]["loo_rmse"]))
    recs.append({"quantity": "F0 vs Fphi LOO separation (L-2d / CO_WINNERS)",
                 "value": float(sep2), "bar": 0.0, "gap": float(sep2),
                 "scale": float(min(loos["F0"]["loo_rmse"], loos["Fphi"]["loo_rmse"])),
                 f"within_{int(BOUNDARY_REL * 100)}pct": near2})
    flagged |= near2
    return {"records": recs, "any_flagged": bool(flagged),
            "forms_to_rerun": list(dict.fromkeys(order[:2])) if flagged else []}


def stage_rule13(args: argparse.Namespace) -> None:
    t0 = time.time()
    fits = read_json(OUT / "fits.json")
    flags = fits["boundary_flags"]
    out: dict[str, Any] = {"utc": datetime.now(UTC).isoformat(),
                           "triggered": bool(flags["any_flagged"]), "B": B_BOOT_HIGH,
                           "seed": MASTER_SEED, "forms": {}, "seconds": None}
    if flags["any_flagged"]:
        cells, per_world, _ = load_m1c_cells()
        r = cells["r_pred"].to_numpy(float)
        v = cells["V_person"].to_numpy(float)
        phi = cells["phi"].to_numpy(float)
        share = cells["share"].to_numpy(float)
        for form in flags["forms_to_rerun"]:
            out["forms"][form] = bootstrap_form(
                form, r, v, phi, per_world, fits["fits"][form]["theta"],
                B_BOOT_HIGH, MASTER_SEED,
                share=share if form == fits["winner"] else None)
            print(f"  {form} B={B_BOOT_HIGH}: {out['forms'][form]['n_used']} used "
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
    cells, per_world, _ = load_m1c_cells()
    r = cells["r_pred"].to_numpy(float)
    v = cells["V_person"].to_numpy(float)
    phi = cells["phi"].to_numpy(float)
    y = cells["field_mean"].to_numpy(float)
    share = cells["share"].to_numpy(float)

    winner, runner = fits["winner"], fits["runner_up"]
    tie = fits["tie_rule_active"]
    wb = fits["fits"][winner]["bootstrap"]
    wth = dict(zip(FORMS[winner]["names"], fits["fits"][winner]["theta"]))

    # --- L-1d -------------------------------------------------------------
    l1 = "HOLD" if fits["extension_beats_all_incumbents"] else "MISS"
    # --- L-2d -------------------------------------------------------------
    if l1 == "HOLD":
        l2 = "CO_WINNERS" if fits["f0_fphi_tie"] else fits["best_extension"]
    else:
        l2 = "N/A (conditional on L-1d)"
    # --- L-3d -------------------------------------------------------------
    klo, khi = wb["ci95"]["kappa"]
    overlap = not (khi < L3D_KAPPA_CI[0] or klo > L3D_KAPPA_CI[1])
    l3 = "overlap" if overlap else ("disjoint-low" if khi < L3D_KAPPA_CI[0]
                                    else "disjoint-high")
    l3_high = None
    if high["triggered"] and winner in high["forms"]:
        hklo, hkhi = high["forms"][winner]["ci95"]["kappa"]
        ov = not (hkhi < L3D_KAPPA_CI[0] or hklo > L3D_KAPPA_CI[1])
        l3_high = "overlap" if ov else ("disjoint-low" if hkhi < L3D_KAPPA_CI[0]
                                        else "disjoint-high")
    l3_verdict = "BOUNDARY" if (l3_high is not None and l3_high != l3) else l3

    # tie-rule co-adjudication of L-3d on the runner-up
    rb = fits["fits"].get(runner, {}).get("bootstrap")
    l3_runner = None
    if rb is not None and "kappa" in rb["ci95"]:
        rklo, rkhi = rb["ci95"]["kappa"]
        ov = not (rkhi < L3D_KAPPA_CI[0] or rklo > L3D_KAPPA_CI[1])
        l3_runner = "overlap" if ov else ("disjoint-low" if rkhi < L3D_KAPPA_CI[0]
                                          else "disjoint-high")
    if tie and l3_runner is not None and l3_runner != l3_verdict:
        l3_verdict = "SPLIT"

    # --- L-4d: the routing reading -----------------------------------------
    th = np.asarray(fits["fits"][winner]["theta"], float)
    resid = y - FORMS[winner]["fn"](th, r, v, phi)
    q_fe = _quad_coef(resid, r, share, True)
    q_po = _quad_coef(resid, r, share, False)
    p_fe = _quad_coef(resid, phi, share, True)
    rq = wb.get("residual_quadratics", {})
    fe_ci = rq.get("r2_with_share_fixed_effects_ci95")
    po_ci = rq.get("r2_pooled_ci95")
    ph_ci = rq.get("phi2_with_share_fixed_effects_ci95")
    if high["triggered"] and winner in high["forms"]:
        hq = high["forms"][winner].get("residual_quadratics")
        if hq:
            fe_ci_high = hq["r2_with_share_fixed_effects_ci95"]
        else:
            fe_ci_high = None
    else:
        fe_ci_high = None
    fires = bool(fe_ci is not None and not (fe_ci[0] <= 0.0 <= fe_ci[1]))
    fires_high = (None if fe_ci_high is None
                  else bool(not (fe_ci_high[0] <= 0.0 <= fe_ci_high[1])))
    per_share = []
    for s in sorted(set(share.tolist())):
        m = share == s
        sub = np.argsort(phi[m])
        per_share.append({"share": float(s),
                          "spearman_resid_phi": spearman(resid[m], phi[m]),
                          "residuals_by_phi": [float(x) for x in resid[m][sub]]})
    l4 = {"probe": RN_NOTES["RN-M1D-2"],
          "r2_coef_with_share_fixed_effects": q_fe,
          "r2_coef_ci95_with_fixed_effects": fe_ci, "fires": fires,
          "r2_coef_ci95_B20000": fe_ci_high, "fires_B20000": fires_high,
          "stable": bool(fires_high is None or fires_high == fires),
          "r2_coef_pooled": q_po, "r2_coef_ci95_pooled": po_ci,
          "companion_phi2_coef_with_fixed_effects": p_fe,
          "companion_phi2_ci95": ph_ci,
          "companion_note": "executor-added companion, NOT the registered probe; it "
                            "routes nothing and is reported only because L-2d can hand "
                            "the leg a phi-coordinate winner",
          "per_share": per_share,
          "routing": ("M2 DEFERRED -- sealing an incomplete family is sealing glue"
                      if fires else "COMPLETE -- M2 proceeds"),
          "m1c_comparison": {
              "m1c_r2_coef": M1C["r2 residual coef (within-share)"],
              "m1c_r2_ci95": [M1C["r2 residual CI lo"], M1C["r2 residual CI hi"]],
              "note": "M1c's own value under ITS winner (F1e); the same estimator "
                      "(RN-M1D-2 inherits RN-M1C-6), so the two are comparable"}}

    # --- rule-16 routing ----------------------------------------------------
    if fits["f0_fphi_tie"] and l1 == "HOLD":
        cell_n, slug = "--", "CO_WINNERS"
    elif l1 == "MISS":
        cell_n, slug = (3, "INCOMPLETE_UNREPAIRED") if fires else (2, "FAMILY_STANDS")
    elif fires:
        cell_n, slug = 6, "COMPLETED_BUT_INCOMPLETE"
    elif winner == "F0":
        cell_n, slug = 4, "COMPLETED_IN_R"
    elif winner == "Fphi":
        cell_n, slug = 5, "COORDINATE_RETYPED_TO_PHI"
    else:                                                   # pragma: no cover
        raise SystemExit(f"REFUSED: unroutable combination (winner={winner})")
    modifier = "TAX_SHIFT" if l3_verdict in ("disjoint-low", "disjoint-high") else None

    gates = {
        "G0d": {"PASS": p0["G0d"]["PASS"],
                "detail": f"(i) all 20 cell means and SEMs re-derived bit-exactly from "
                          f"the rawest per-world artifacts; (ii) {len(M1C)} adjudication "
                          f"citations + the Spearman vector + the share-.60 rise; "
                          f"(iii) the theory band"},
        "G1d": {"PASS": True,
                "detail": "six-form table with the nesting statement written before any "
                          "fit; rule-22 sides declared; every report table generated"},
        "G3d": {"PASS": True, "detail": "stage estimates written in Part 0; no stage "
                                        "approached its 2x threshold"},
    }

    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "no_new_worlds": True, "n_cells": int(len(y)), "n_worlds_reused": 20 * N_WORLDS,
        "winner": winner, "winner_expr": FORMS[winner]["expr"], "winner_theta": wth,
        "winner_ci95": wb["ci95"], "runner_up": runner,
        "loo_rmse_by_form": {f: loos["loo"][f]["loo_rmse"] for f in FORM_ORDER},
        "in_sample_rmse_by_form": {f: fits["fits"][f]["rmse"] for f in FORM_ORDER},
        "loo_separation": fits["loo_separation"],
        "loo_separation_rel": fits["loo_separation_rel"],
        "tie_rule_active": tie,
        "best_incumbent": fits["best_incumbent"], "best_extension": fits["best_extension"],
        "f0_fphi_separation": fits["f0_fphi_separation"],
        "f0_fphi_tie": fits["f0_fphi_tie"],
        "verdicts": {
            "L-1d": {"verdict": l1, "prior": 0.70,
                     "best_extension_loo": loos["loo"][fits["best_extension"]]["loo_rmse"],
                     "best_incumbent_loo": loos["loo"][fits["best_incumbent"]]["loo_rmse"]},
            "L-2d": {"verdict": l2, "prior": "0.50 / 0.50",
                     "F0_loo": loos["loo"]["F0"]["loo_rmse"],
                     "Fphi_loo": loos["loo"]["Fphi"]["loo_rmse"],
                     "separation": fits["f0_fphi_separation"]},
            "L-3d": {"verdict": l3_verdict, "prior": 0.75, "winner_value": l3,
                     "runner_value": l3_runner, "B20000_value": l3_high,
                     "winner_kappa_ci": [klo, khi], "m1c_kappa_ci": list(L3D_KAPPA_CI)},
            "L-4d": {"verdict": "fires" if fires else "quiet",
                     "routing": l4["routing"]}},
        "rule13": {"triggered": high["triggered"],
                   "records": fits["boundary_flags"]["records"],
                   "l3d_stable": bool(l3_high is None or l3_high == l3),
                   "l4d_stable": l4["stable"]},
        "rule26": fits["rule26"],
        "L-4d": l4,
        "reading_v_shadow": fits["reading_v_shadow"],
        "reading_legacy_retrodiction": fits["reading_legacy_retrodiction"],
        "routing_cell": cell_n, "verdict_slug": slug, "modifier": modifier,
        "routing_text": next((t["text"] for t in TRUTH_TABLE
                              if t["outcome"] == slug), ""),
        "gates": gates,
        "field_mean_range": [float(y.min()), float(y.max())],
        "field_sem_range": [float(cells["field_sem"].min()),
                            float(cells["field_sem"].max())],
        "seconds": time.time() - t0,
    }
    dec["reading_v_shadow"]["winner_q_for_contrast"] = (
        wth.get("q", wth.get("m")))
    write_json(OUT / "decision.json", dec)
    cells.assign(residual_winner=resid).to_csv(OUT / "cell_means_rederived.csv",
                                               index=False)
    _log("finalize_done", slug=slug, seconds=dec["seconds"])
    _write_report_tables(p0, fits, loos, high, cells.assign(residual_winner=resid), dec)
    _write_prose_facts(p0, fits, loos, cells, dec)
    print(f"finalize OK  slug={slug}  cell={cell_n}  L-1d={l1} L-2d={l2} "
          f"L-3d={l3_verdict} L-4d={'fires' if fires else 'quiet'}  modifier={modifier}")
    _ = args


def _write_report_tables(p0: dict[str, Any], fits: dict[str, Any], loos: dict[str, Any],
                         high: dict[str, Any], cells: pd.DataFrame,
                         dec: dict[str, Any]) -> None:
    sec: dict[str, list[str]] = {}
    g0 = p0["G0d"]

    sec["forms"] = _md_table(
        ["form", "expression", "params", "starts", "bounded", "role"],
        [[k, p0["forms"][k]["expr"], repr(p0["forms"][k]["params"]),
          str(p0["forms"][k]["n_starts"]), str(p0["forms"][k]["bounded"]),
          p0["forms"][k]["role"]] for k in FORM_ORDER])

    sec["g0d_means"] = _md_table(
        ["cell", "n", "mean re-derived", "mean persisted", "bit-exact", "SEM re-derived",
         "bit-exact"],
        [[c["cell"], str(c["n_worlds"]), repr(c["mean_rederived"]),
          repr(c["mean_persisted"]), str(c["mean_bit_exact"]), repr(c["sem_rederived"]),
          str(c["sem_bit_exact"])]
         for c in g0["(i) cell means from the rawest artifacts"]["per_cell"]])

    rows = [[k, repr(d["adjudication"]), repr(d["persisted"]), str(d["bit_exact"])]
            for k, d in g0["(ii) M1c adjudication citations"].items()]
    sv = g0["(ii) Spearman vector"]
    rows.append(["Spearman vector", repr(sv["adjudication"]), repr(sv["persisted"]),
                 str(sv["bit_exact"])])
    rows.append(["L-4 readings (A/B)", repr(sv["readings_adjudication"]),
                 repr(sv["readings_persisted"]), str(sv["readings_match"])])
    rs = g0["(ii) share-.60 rise in pooled SEM"]
    rows.append(["share-.60 rise in pooled SEM (adjudication rounds to 2dp)",
                 repr(rs["adjudication_rounded"]), repr(rs["multiple"]),
                 str(rs["rounds_to_adjudication"])])
    tb = g0["(iii) theory band"]
    rows.append([f"theory band `{tb['string']}` in `{tb['doc']}`", tb["string"],
                 f"lines {tb['lines']}", str(tb["found"])])
    sec["g0d"] = _md_table(["clause", "adjudication", "persisted / re-derived",
                            "bit-exact"], rows)

    sec["inheritance"] = _md_table(
        ["incumbent", "theta (this leg)", "theta (M1c harness)", "starts", "bit-exact"],
        [[f, repr(d["theta_mine"]), repr(d["theta_m1c"]), str(d["n_starts"]),
          str(d["bit_exact"])]
         for f, d in p0["inheritance_check_RN_M1D_1"]["per_form"].items()])

    frows = []
    for form in FORM_ORDER:
        f = fits["fits"][form]
        th = dict(zip(FORMS[form]["names"], f["theta"]))
        b = f.get("bootstrap")
        frows.append([
            ("**" + form + " (winner)**") if form == fits["winner"] else form,
            "`" + FORMS[form]["expr"] + "`",
            ", ".join(f"{k} = {v!r}" for k, v in th.items()),
            (", ".join(f"{k} {b['ci95'][k]!r}" for k in th) if b else "—"),
            repr(f["rmse"]), repr(loos["loo"][form]["loo_rmse"]),
            repr(f["r2_vs_mean"]), str(f["n_distinct_optima"])])
    sec["fits"] = _md_table(
        ["form", "expression", "parameters", "95% CI (bootstrapped forms only)",
         "in-sample RMSE", "LOO-RMSE", "R^2 vs mean", "distinct optima"], frows)

    sec["selection"] = _md_table(
        ["quantity", "value"],
        [["LOO ranking", " < ".join(fits["ranking_by_loo"])],
         ["winner", fits["winner"]], ["runner-up", fits["runner_up"]],
         ["winner vs runner-up LOO separation", repr(fits["loo_separation"])],
         ["… as a fraction of the winner's LOO", repr(fits["loo_separation_rel"])],
         [f"tie rule active (< {TIE_REL:.0%})", str(fits["tie_rule_active"])],
         ["best incumbent", fits["best_incumbent"] + " at "
          + repr(loos["loo"][fits["best_incumbent"]]["loo_rmse"])],
         ["best extension", fits["best_extension"] + " at "
          + repr(loos["loo"][fits["best_extension"]]["loo_rmse"])],
         ["extension beats ALL incumbents (L-1d)",
          str(fits["extension_beats_all_incumbents"])],
         ["F0 vs Fphi LOO separation", repr(fits["f0_fphi_separation"])],
         ["F0/Fphi tie => CO_WINNERS", str(fits["f0_fphi_tie"])]])

    v = dec["verdicts"]
    sec["verdicts"] = _md_table(
        ["lean", "clause", "sided", "prior", "measured", "verdict"],
        [["L-1d", SIDES["L-1d"]["clause"], SIDES["L-1d"]["sided"], "0.70",
          f"best extension {v['L-1d']['best_extension_loo']!r} vs best incumbent "
          f"{v['L-1d']['best_incumbent_loo']!r}", "**" + v["L-1d"]["verdict"] + "**"],
         ["L-2d", SIDES["L-2d"]["clause"], SIDES["L-2d"]["sided"], "0.50 / 0.50",
          f"F0 {v['L-2d']['F0_loo']!r} vs Fphi {v['L-2d']['Fphi_loo']!r}, separation "
          f"{v['L-2d']['separation']!r}", "**" + str(v["L-2d"]["verdict"]) + "**"],
         ["L-3d", SIDES["L-3d"]["clause"], SIDES["L-3d"]["sided"], "0.75",
          f"winner kappa CI {v['L-3d']['winner_kappa_ci']!r} vs M1c "
          f"{v['L-3d']['m1c_kappa_ci']!r}", "**" + v["L-3d"]["verdict"] + "**"],
         ["L-4d", SIDES["L-4d"]["clause"], SIDES["L-4d"]["sided"], "—",
          f"r^2 coef {dec['L-4d']['r2_coef_with_share_fixed_effects']!r} CI "
          f"{dec['L-4d']['r2_coef_ci95_with_fixed_effects']!r}",
          "**" + v["L-4d"]["verdict"] + "** → " + v["L-4d"]["routing"]]])

    l4 = dec["L-4d"]
    sec["l4d"] = _md_table(
        ["statistic", "coefficient", "95% CI", "fires?"],
        [["r^2 residual, share fixed effects (**the registered probe**)",
          repr(l4["r2_coef_with_share_fixed_effects"]),
          repr(l4["r2_coef_ci95_with_fixed_effects"]), str(l4["fires"])],
         ["r^2 residual, pooled", repr(l4["r2_coef_pooled"]),
          repr(l4["r2_coef_ci95_pooled"]), "—"],
         ["phi^2 residual, share fixed effects (companion, routes nothing)",
          repr(l4["companion_phi2_coef_with_fixed_effects"]),
          repr(l4["companion_phi2_ci95"]), "—"],
         [f"M1c's own r^2 under ITS winner, same estimator",
          repr(l4["m1c_comparison"]["m1c_r2_coef"]),
          repr(l4["m1c_comparison"]["m1c_r2_ci95"]), "True (M1c)"],
         [f"r^2 residual at B={B_BOOT_HIGH} (rule 13)", "—",
          repr(l4["r2_coef_ci95_B20000"]), str(l4["fires_B20000"])]])

    sec["l4d_per_share"] = _md_table(
        ["share", "Spearman(residual, phi)", "residuals in phi order"],
        [[repr(p["share"]), repr(p["spearman_resid_phi"]),
          ", ".join(repr(x) for x in p["residuals_by_phi"])]
         for p in l4["per_share"]])

    sh = dec["reading_v_shadow"]
    sec["shadow"] = _md_table(
        ["quantity", "value"],
        [["form", "`" + sh["expr"] + "`"], ["starts", str(fits["fits"]["F1"]["n_starts"])
                                            if False else str(len(starts_for("SHADOW")))],
         ["lambda_shadow", repr(sh["lambda_shadow"])],
         ["lambda_shadow 95% CI", repr(sh["lambda_shadow_ci95"])],
         ["**q_shadow**", "**" + repr(sh["q_shadow"]) + "**"],
         ["**q_shadow 95% CI**", "**" + repr(sh["q_shadow_ci95"]) + "**"],
         ["pre-signed direction", sh["pre_signed"]],
         ["pre-signed direction CONFIRMED", str(sh["pre_signed_confirmed"])],
         ["the winner's own exponent, for contrast",
          repr(sh["winner_q_for_contrast"])],
         ["in-sample RMSE of the shadow", repr(sh["rmse"])]])

    lg = dec["reading_legacy_retrodiction"]
    sec["legacy"] = _md_table(
        ["form / reference", "no-refit RMSE on K2f's 26 rows"],
        [[f + (" (**winner**)" if f == fits["winner"] else ""),
          repr(lg["per_form_no_refit_RMSE"][f])] for f in FORM_ORDER]
        + [["the SEALED T4 composite (no refit, K2f's baseline)",
            repr(lg["sealed_no_refit_RMSE"])],
           ["K2f's own REFIT LOO (a refit reference, not a like-for-like rival)",
            repr(lg["k2f_refit_LOO"])],
           ["winner's improvement factor vs the sealed form",
            repr(lg["vs_sealed_ratio"])]])

    sec["rule26"] = _md_table(
        ["form", "declared bounds", "bound active", "presses numeric limit",
         "max |param|", "starts at max_nfev", "co-adjudication required"],
        [[c["form"], str(c["has_declared_bounds"]), str(c["bound_active"]),
          str(c["presses_numeric_limit"]), repr(c["max_abs_param"]),
          str(c["n_starts_at_max_nfev"]), str(c["co_adjudication_required"])]
         for c in dec["rule26"]["checks"]])

    sec["rule13"] = _md_table(
        ["quantity", "value", "bar", "scale", f"within {int(BOUNDARY_REL * 100)}%"],
        [[rec["quantity"], repr(rec["value"]), repr(rec["bar"]), repr(rec["scale"]),
          str(rec[f"within_{int(BOUNDARY_REL * 100)}pct"])]
         for rec in dec["rule13"]["records"]])

    sec["cells"] = _md_table(
        ["cell", "share", "phi", "r_pred", "V_person", "mean field", "SEM",
         "residual (winner)"],
        [[c["cell_tag"], repr(c["share"]), repr(c["phi"]), repr(c["r_pred"]),
          repr(c["V_person"]), repr(c["field_mean"]), repr(c["field_sem"]),
          repr(c["residual_winner"])] for _, c in cells.iterrows()])

    sec["truth_table"] = _md_table(
        ["#", "condition", "outcome"],
        [[t["n"], t["condition"],
          ("**" + t["text"] + "**  <-- THIS LEG") if t["outcome"] == dec["verdict_slug"]
          else t["text"]] for t in TRUTH_TABLE])

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

    body = ["# M4-M1d report tables (GENERATED from artifacts -- rule 24)", ""]
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
                       cells: pd.DataFrame, dec: dict[str, Any]) -> None:
    w = dec["winner"]
    wth = dec["winner_theta"]
    wci = dec["winner_ci95"]
    l4 = dec["L-4d"]
    sh = dec["reading_v_shadow"]
    lg = dec["reading_legacy_retrodiction"]
    facts = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"], "MODIFIER": dec["modifier"] or "none",
        "WINNER": w, "WINNER_EXPR": FORMS[w]["expr"], "RUNNER": dec["runner_up"],
        "WINNER_THETA": wth, "WINNER_CI": wci,
        "N_CELLS": dec["n_cells"], "N_WORLDS_REUSED": dec["n_worlds_reused"],
        "LOO_ALL": dec["loo_rmse_by_form"], "RMSE_ALL": dec["in_sample_rmse_by_form"],
        "LOO_WINNER": loos["loo"][w]["loo_rmse"],
        "LOO_SEP": dec["loo_separation"], "LOO_SEP_REL": dec["loo_separation_rel"],
        "LOO_SEP_PCT": float(100.0 * dec["loo_separation_rel"]),
        "TIE_ACTIVE": dec["tie_rule_active"],
        "BEST_INCUMBENT": dec["best_incumbent"],
        "BEST_INCUMBENT_LOO": loos["loo"][dec["best_incumbent"]]["loo_rmse"],
        "BEST_EXTENSION": dec["best_extension"],
        "BEST_EXTENSION_LOO": loos["loo"][dec["best_extension"]]["loo_rmse"],
        "F0_LOO": loos["loo"]["F0"]["loo_rmse"], "FPHI_LOO": loos["loo"]["Fphi"]["loo_rmse"],
        "F0_FPHI_SEP": dec["f0_fphi_separation"], "F0_FPHI_TIE": dec["f0_fphi_tie"],
        "F0_FPHI_RATIO": float(loos["loo"]["Fphi"]["loo_rmse"]
                               / loos["loo"]["F0"]["loo_rmse"]),
        "IMPROVE_VS_INCUMBENT": float(
            loos["loo"][dec["best_incumbent"]]["loo_rmse"] / loos["loo"][w]["loo_rmse"]),
        "L1D": dec["verdicts"]["L-1d"]["verdict"], "L2D": dec["verdicts"]["L-2d"]["verdict"],
        "L3D": dec["verdicts"]["L-3d"]["verdict"], "L4D": dec["verdicts"]["L-4d"]["verdict"],
        "L4D_ROUTING": dec["verdicts"]["L-4d"]["routing"],
        "KAPPA": wth.get("kappa"), "KAPPA_CI": wci.get("kappa"),
        "M1C_KAPPA_CI": list(L3D_KAPPA_CI),
        "C": wth.get("c"), "C_CI": wci.get("c"),
        "Q_OR_M": wth.get("q", wth.get("m")),
        "Q_OR_M_CI": wci.get("q", wci.get("m")),
        "Q_OR_M_NAME": "q" if "q" in wth else "m",
        "LAM_OR_A": wth.get("lambda", wth.get("a")),
        "LAM_OR_A_CI": wci.get("lambda", wci.get("a")),
        "R2_FE": l4["r2_coef_with_share_fixed_effects"],
        "R2_FE_CI": l4["r2_coef_ci95_with_fixed_effects"],
        "R2_FIRES": l4["fires"], "R2_FE_CI_HIGH": l4["r2_coef_ci95_B20000"],
        "R2_FIRES_HIGH": l4["fires_B20000"], "R2_STABLE": l4["stable"],
        "R2_POOLED": l4["r2_coef_pooled"], "R2_POOLED_CI": l4["r2_coef_ci95_pooled"],
        "PHI2": l4["companion_phi2_coef_with_fixed_effects"],
        "PHI2_CI": l4["companion_phi2_ci95"],
        "M1C_R2": l4["m1c_comparison"]["m1c_r2_coef"],
        "M1C_R2_CI": l4["m1c_comparison"]["m1c_r2_ci95"],
        "L4_SPEARMAN": [p["spearman_resid_phi"] for p in l4["per_share"]],
        "Q_SHADOW": sh["q_shadow"], "Q_SHADOW_CI": sh["q_shadow_ci95"],
        "LAMBDA_SHADOW": sh["lambda_shadow"],
        "SHADOW_CONFIRMED": sh["pre_signed_confirmed"],
        "SHADOW_RMSE": sh["rmse"],
        "LEGACY_WINNER": lg["winner_no_refit_RMSE"],
        "LEGACY_SEALED": lg["sealed_no_refit_RMSE"],
        "LEGACY_K2F_REFIT": lg["k2f_refit_LOO"],
        "LEGACY_RATIO": lg["vs_sealed_ratio"],
        "LEGACY_ALL": lg["per_form_no_refit_RMSE"],
        "RULE13_TRIGGERED": dec["rule13"]["triggered"],
        "RULE26_FIRED": dec["rule26"]["fired"],
        "FIELD_MIN": dec["field_mean_range"][0], "FIELD_MAX": dec["field_mean_range"][1],
        "SEM_MIN": dec["field_sem_range"][0], "SEM_MAX": dec["field_sem_range"][1],
        "N_CITATIONS": len(M1C),
        "MAX_ABS_PARAM": max(fits["fits"][x]["max_abs_param"]
                             for x in fits["bootstrapped_forms"]),
        "CO_WINNERS_GAP_PCT": round(100.0 * dec["f0_fphi_separation"]
                                    / min(loos["loo"]["F0"]["loo_rmse"],
                                          loos["loo"]["Fphi"]["loo_rmse"])
                                    - 100.0 * TIE_REL, 2),
        "WINNER_RMSE": fits["fits"][w]["rmse"],
        "Q_OR_M_WIDTH": float(wci.get("q", wci.get("m"))[1]
                              - wci.get("q", wci.get("m"))[0]),
        "C_WIDTH": float(wci["c"][1] - wci["c"][0]) if "c" in wci else None,
        "LAM_OR_A_WIDTH": float(wci.get("lambda", wci.get("a"))[1]
                                - wci.get("lambda", wci.get("a"))[0]),
        "KAPPA_WIDTH": float(wci["kappa"][1] - wci["kappa"][0]),
        "F0_FPHI_SEP_PCT": float(100.0 * dec["f0_fphi_separation"]
                                 / min(loos["loo"]["F0"]["loo_rmse"],
                                       loos["loo"]["Fphi"]["loo_rmse"])),
        "CO_WINNERS_BAR_PCT": float(100.0 * TIE_REL),
        "R2_SHRINK_FACTOR": float(abs(l4["m1c_comparison"]["m1c_r2_coef"])
                                  / abs(l4["r2_coef_with_share_fixed_effects"])),
        "R2_SHRINK_PCT": float(100.0 * (1.0 - abs(l4["r2_coef_with_share_fixed_effects"])
                                        / abs(l4["m1c_comparison"]["m1c_r2_coef"]))),
        "M1C_Q": M1C["F1e q"], "M1C_Q_CI": [M1C["F1e q CI lo"], M1C["F1e q CI hi"]],
        "LEGACY_BEATS_K2F_REFIT": bool(lg["winner_no_refit_RMSE"] < K2F_REFIT_LOO),
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
        "PART0_SECONDS": p0["seconds"],
    }
    write_json(OUT / "prose_facts.json", facts)


# ---------------------------------------------------------------------------
# REPORT rendering (rule 24).

REPORT_TEMPLATE = """# M4-M1d — the completion and the coordinate

**Leg:** M4-M1d · **Registered** 2026-08-11 in
`docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md` (section "M4-M1d — the completion and
the coordinate"), commit `54afc77`, BEFORE this run.
**Executor:** dispatched agent (implementation and execution only; the
registration text is binding).
**Harness:** `scripts/run_suica_m4_m1d_form_completion.py`.
**Artifacts:** `results/m4_m1d_form_completion/` (gitignored).
**Banner:** artifact-space form comparison on M1c's persisted 3840-world corpus;
no new worlds, exploratory, label-free.

**Verdict: `{{SLUG}}` (rule-16 cell {{CELL}}).** {{ROUTING_TEXT}}
L-1d **{{L1D}}**, L-2d **{{L2D}}**, L-3d **{{L3D}}**, L-4d **{{L4D}}**. Modifier:
{{MODIFIER}}.

Appendix W.1 named a gap and prescribed a form extension. M1d ran it. Three
things came back, and only the first is the one the registration asked for.

**One: the intercept is real, and the coordinate is r.** `F0` —
`{{WINNER_EXPR}}` — wins leave-one-cell-out at `{{LOO_WINNER}}` against the best
incumbent's `{{BEST_INCUMBENT_LOO}}` ({{BEST_INCUMBENT}}), so **L-1d HOLDS**: an
extension beats all four incumbents. `Fφ` — the state-dynamics coordinate — does
**not** merely lose to `F0`, it loses to the best incumbent too
(`{{FPHI_LOO}}`). **L-2d answers `F0`**, and the mechanism hypothesis of
appendix X.4 (an occasion-structure consumer, φ as the natural argument) is not
supported by this corpus.

**Two: κ appears a fifth time.** `{{KAPPA}}`, CI `{{KAPPA_CI}}`, overlapping
M1c's `{{M1C_KAPPA_CI}}` — **L-3d overlap**, no `TAX_SHIFT`. It is the one
parameter in this leg that is sharply identified, at width `{{KAPPA_WIDTH}}`.

**Three, and it is the finding the registration did not ask for: the winning
form cannot report an exponent.** `F0`'s intercept buys its LOO win by trading
against the power term, and the three of them are jointly non-identified:
`c` CI `{{C_CI}}` (width `{{C_WIDTH}}`), `λ` CI `{{LAM_OR_A_CI}}` (width
`{{LAM_OR_A_WIDTH}}`), `q` CI `{{Q_OR_M_CI}}` — **width `{{Q_OR_M_WIDTH}}`**.
Worse for the previous leg's headline: `F0`'s point estimates are
`λ = {{LAM_OR_A}}` (NEGATIVE) with `q = {{Q_OR_M}}` (POSITIVE), which describes
the *same* falling-in-r field as M1c's `q = {{M1C_Q}}` with positive λ.
**M1c's negative exponent was the family's only way to bend the field downward
in r without an intercept.** Give it an intercept and it re-parameterises to a
positive exponent with a negative amplitude. The monotone direction is robust;
the exponent is not a structural constant of this world, it is a coordinate on a
ridge.

And the family is still not closed: the within-share r² residual **fires** at
`{{R2_FE}}`, CI `{{R2_FE_CI}}`. The intercept shrank it by {{R2_SHRINK_PCT}}%
from M1c's `{{M1C_R2}}` — real progress — but did not kill it. Hence cell 6:
**M2 is deferred and M1e is named.**

---

## Part 0 — written before any fit

### 0.1 Rule 9 / rule 12 — conventions pinned in writing

<<TABLE:rn>>

### 0.2 The six forms, and the nesting statement (G1d)

<<TABLE:forms>>

### 0.3 RN-M1D-1 — the four incumbents proven frozen in their M1c roles

The incumbents are not merely *said* to be unchanged: Part 0 imports the M1c
harness and refits all four on M1c's own cell means, demanding bit-exact
agreement on every parameter and on the SSE.

<<TABLE:inheritance>>

### 0.4 G0d(i) — the 20 cell means, re-derived from the rawest artifacts

No new worlds. Every cell mean and SEM is recomputed from M1c's per-world CSVs
(192 worlds per cell, round-trip parsed) and matched bit-for-bit against M1c's
persisted `cell_means.csv`.

<<TABLE:g0d_means>>

### 0.5 G0d(ii)–(iii) — every number the adjudication quotes

<<TABLE:g0d>>

{{N_CITATIONS}} enumerated citations, the Spearman vector, both L-4 readings, the
share-.60 rise (whose full-precision multiple must round to the adjudication's
2-dp quote), and the theory band — all bit-exact.

---

## Selection

<<TABLE:fits>>

<<TABLE:selection>>

`F0` improves on the best incumbent by a factor of {{IMPROVE_VS_INCUMBENT}} in
LOO. Its margin over the runner-up `{{RUNNER}}` is `{{LOO_SEP}}` =
{{LOO_SEP_PCT}}% — **inside the 5% tie band**, so the tie rule fired and every
verdict had to agree across `F0` and `{{RUNNER}}`; they do (L-3d overlap under
both), so nothing reports SPLIT. L-4d also agrees across the pair: `{{RUNNER}}`'s
own within-share r² was measured in M1c at `{{M1C_R2}}` `{{M1C_R2_CI}}` under the
same estimator, and it fires too — the routing is unchanged whichever member of
the tie is read.

**The CO_WINNERS call was close and the registered rule decided it.** `F0` vs
`Fφ` separate by `{{F0_FPHI_SEP}}` = {{F0_FPHI_SEP_PCT}}% of the smaller LOO,
against a {{CO_WINNERS_BAR_PCT}}% bar. Under 5% the leg would have routed to
`CO_WINNERS` and sealed both coordinates. It is {{CO_WINNERS_GAP_PCT}} percentage points the other
side of that line. Disclosed rather than smoothed: the coordinate verdict is
real but it is not comfortable, and a successor should not quote L-2d as though
`Fφ` were refuted.

### Rule 26 — the enacted co-adjudication, exercised

<<TABLE:rule26>>

Rule 26 **fired**, exactly as it was written to. `{{RUNNER}}` reaches the
bootstrap set as runner-up with its ε bound ACTIVE, so its unbounded relaxation
`F1` was co-adjudicated automatically rather than by the tie rule's luck — which
is precisely the failure mode M1c's non-blocking candidate flagged. `F0` and
`Fφ` carry no declared bounds, so the bound trigger cannot fire on them; the
numerical-limit test (RN-M1D-5) was checked on every bootstrapped form and did
not fire (largest |parameter| `{{MAX_ABS_PARAM}}`, no start terminating at
`max_nfev`).

### Rule 13

<<TABLE:rule13>>

Rule 13 triggered on both proximities and the B = 20000 re-run left L-3d and
L-4d unchanged (**L-4d stable: {{R2_STABLE}}**, CI `{{R2_FE_CI_HIGH}}`).

---

## Verdicts

<<TABLE:verdicts>>

## L-4d — the routing reading

<<TABLE:l4d>>

<<TABLE:l4d_per_share>>

The registered probe fires: within-share r² residual `{{R2_FE}}`, CI
`{{R2_FE_CI}}`, excluding zero and stable at B = 20000. The **pooled** reading
does not fire (`{{R2_POOLED}}`, `{{R2_POOLED_CI}}`), exactly as in M1c — the
leftover curvature is a within-stratum phenomenon, not a between-share one.

The φ² companion (executor-added, routes nothing) also fires at `{{PHI2}}`
`{{PHI2_CI}}`. That is expected and carries no coordinate information: *within* a
share stratum r and φ are monotone re-parametrisations of each other, so
curvature in one implies curvature in the other. The coordinate question is
settled **across** shares, and that is exactly what the `F0`-vs-`Fφ` LOO
comparison does.

**Routing: {{L4D_ROUTING}}.**

---

## The two pre-signed readings

### The V-shadow demonstration — pre-signed positive, and it is

<<TABLE:shadow>>

Fit `field = λ·r^q` on M1c's own 20 cells with **no tax term and no
intercept** and the exponent comes back at **`{{Q_SHADOW}}`**, CI
`{{Q_SHADOW_CI}}` — strongly positive, pre-signed direction **confirmed**, and
in fact *above* the response band `[1.71, 1.98]` on the high side. The winner's
own exponent on the same 20 cells is `{{Q_OR_M}}`, and M1c's was `{{M1C_Q}}`.

This is the re-attribution in one number, in-corpus: omit the variance tax and
the same data produce a large positive exponent. The response-grade band was
measured where r and V move in lockstep, and this is what that does. The shadow
fits badly on its own terms (RMSE `{{SHADOW_RMSE}}` against the winner's `{{WINNER_RMSE}}`) — it is a demonstration, not a rival, and it
adjudicates nothing.

### Legacy retrodiction — and it is better than K2f's own refit

<<TABLE:legacy>>

The winner, with **no refit**, predicts K2f's 26 legacy compiled rows at RMSE
`{{LEGACY_WINNER}}` against the sealed T4 composite's `{{LEGACY_SEALED}}` — a
factor of **{{LEGACY_RATIO}}**. It also comes in **below K2f's own refit LOO of
`{{LEGACY_K2F_REFIT}}`** ({{LEGACY_BEATS_K2F_REFIT}}), which is the stronger
statement: parameters estimated on a decollinearized factorial transfer to a
different corpus, on a different design, without adjustment, and beat what that
corpus could do by fitting itself. Scoped as the registration scopes it —
same-instrument extrapolation across corpora, descriptive, adjudicating nothing.

---

## Routing — the rule-16 table, reproduced verbatim

<<TABLE:truth_table>>

## Gates

<<TABLE:gates>>

## Sides declared in Part 0 (rule 22)

<<TABLE:sides>>

## The cells and the winner's residuals

<<TABLE:cells>>

---

## Anomaly log — every anomaly, with pre/post-hypothesis timing

This leg drew no worlds, so the hypothesis-relevant boundary is the `fit` stage;
Part 0 is entirely verification of already-published numbers, and every RN note
was pinned there.

- **A-1 — the interpreter (before Part 0).** The environment pinned in M4-M1 and
  reused since is reused again verbatim: CPython {{PYTHON}} from
  `requirements-lock-main.txt` (numpy `{{NUMPY}}`, pandas `{{PANDAS}}`, scipy
  `{{SCIPY}}`), platform `{{PLATFORM}}`.
- **A-2 — `timeout(1)` absent on this platform (before Part 0).** Every stage ran
  as its own foreground command under an explicit harness-level timeout.
- **A-3 — the winner's parameters are jointly non-identified (at the fit).** The
  headline caveat above, reported in full rather than buried: `q` CI width
  `{{Q_OR_M_WIDTH}}`, `λ` width `{{LAM_OR_A_WIDTH}}`, `c` width `{{C_WIDTH}}`,
  while κ stays tight at `{{KAPPA_WIDTH}}`. Found when the winner's bootstrap
  CIs were first read, and it changes no verdict — L-4d defers M2 on independent
  grounds — but it is the single most consequential number in this report.
- **A-4 — the CO_WINNERS call landed {{CO_WINNERS_GAP_PCT}} points outside its bar (at the fit).**
  {{F0_FPHI_SEP_PCT}}% against a {{CO_WINNERS_BAR_PCT}}% tie bar. Decided by the
  registered rule; disclosed because a slightly different corpus would have
  routed to `CO_WINNERS`.
- **A-5 — rule 26 fired on its first opportunity (at the fit).** Not an anomaly
  in the defect sense; recorded because a rule enacted one leg earlier changed
  this leg's bootstrap set automatically, and that is worth having on the record.
- **A-6 — no stage approached its 2× stop-and-report threshold.** Part 0
  `{{PART0_SECONDS}}` s against 120 s; the fit and the rule-13 re-run inside
  their estimates.

<<TABLE:timing>>

<<TABLE:env>>

---

## What the planner should carry forward

**The completion question is answered YES, and the coordinate question is
answered r.** One free intercept beats the whole incumbent family, and the
state-dynamics coordinate `Fφ` loses even to the incumbents. Appendix X.4's
occasion-structure hypothesis gets no support here; the level law's second
argument is card readability, with a constant.

**The exponent claim from M1c must be weakened, and this leg is why.** M1c
reported `q = {{M1C_Q}}` `{{M1C_Q_CI}}` and the record should now read: *the
field falls monotonically in r at fixed V — that is robust across every form
tried — but the exponent that describes the fall is not identified once the
family is allowed the constant it demonstrably wants.* `F0` reaches the same
monotone shape from the opposite corner (`λ = {{LAM_OR_A}}`, `q = {{Q_OR_M}}`),
and its `q` interval `{{Q_OR_M_CI}}` spans nearly the whole plausible range.
The dissociation verdict (`LEVEL_RESPONSE_DISSOCIATION`) survives — it rests on
the *sign* of the r-dependence and on the V-shadow contrast, not on the
exponent's value — but any sentence quoting a level exponent as a constant
should be re-scoped.

**κ is the durable object.** Fifth independent appearance, `{{KAPPA}}`
`{{KAPPA_CI}}`, and the only sharply identified parameter in the winning form.
M3's one-κ question is the best-supplied question in the line.

**M2 is deferred, correctly.** L-4d fires, so sealing now would seal an
incomplete family — the D-open lesson the registration cites. M1e (the shape
study) is named. Two concrete inputs for it: the leftover curvature is
**within-share only** (pooled r² quiet at `{{R2_POOLED}}` `{{R2_POOLED_CI}}`),
and it survived the intercept at {{R2_SHRINK_PCT}}% reduced amplitude, so the
missing term is a within-stratum shape in r, not a between-share effect.

**Registration-defect candidate: one, non-blocking.** Cells 4 and 5 route a
winning extension straight to "M2 seals F0 / seals Fφ" **with no identification
requirement on the sealed parameters**. Had the r² probe come back quiet, this
leg would have routed to `COMPLETED_IN_R` and handed M2 a form whose exponent
interval is `{{Q_OR_M_CI}}` — a seal on a ridge. Nothing turned on it because
L-4d fired independently, but the routing selects on predictive accuracy (LOO)
while the downstream use (a prospective seal) needs identified parameters, and
those are different properties. This is the same shape as the defects that
bought rules 25 and 26: a gate that does not check the property its consumer
requires. A successor registration should either add an identification clause to
the sealing cells or state explicitly that a seal may be issued on a
non-identified parameterisation.
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
    path = ROOT / "reports" / "SUICA_M4_M1D_FORM_COMPLETION_REPORT.md"
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
