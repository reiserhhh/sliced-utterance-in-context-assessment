#!/usr/bin/env python3
"""M4-G6: shape and strength together -- does per-column regularization,
run at strengths WEAKER than deployed, deliver both exact c-invariance AND
`g3_raw_scale`'s recovery gain, or do the two genuinely trade off?

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design
and leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-G6
registration" (2026-08-03, BEFORE run); ledger row M4-G6). Machinery is
IMPORTED and REUSED, not reimplemented: M4-G1/G2/G3/G4/G5's world set,
context builder (`g1._build_world_contexts`), whitening-scale construction
(`g2._whitening_for_c`), basis construction (`leg10._bases_from_whitening`,
UNCHANGED), M4-G3's estimator internals (`g3._fit_logistic_adaptive`,
`g3._forced_route_derivative_adaptive`, `g3._feedback_derivative_adaptive`),
CI helpers (`g1._paired_world_ci`, `g1._paired_author_ci`) and -- centrally
-- M4-G4's own generic gate/lean machinery (`g4._author_level_truth_with_c`,
`g4._paired_author_diff_ci`, `g4._paired_world_diff_ci`, `g4._classify_pair`,
`g4._arm_status_from_pairs`, `g4._c_invariance_check`, `g4._no_loss_check`),
called here UNCHANGED with this leg's own arm names -- these functions take
`author_truth`/`arm`/`worlds` as parameters (or a hardcoded `"g3_raw_scale"`
string this leg's own reference arm is also named), never anything
G4/G5-specific, so they work correctly on this leg's own data with zero
modification. `g4`'s own module-level `C_LADDER=(0.25,1.0,4.0)`,
`TRUTH_BUDGETS=(4.0,8.0)`, and margins (`LEAN_A_MARGIN=0.02`,
`LEAN_B_MARGIN=0.02`, `G0_FRACTION_BAR=0.01`) are reused UNCHANGED -- this
IS "the margin registered in Part 0" the outer task's registration
cross-references: by being told to "reuse M4-G5's ... gate helpers", the
margins are fixed automatically as a consequence of that reuse instruction,
not a fresh, independently-registered choice.

Central to this leg: `g5._forced_route_derivative_columnwise` (M4-G5's own
`column_standardized` mechanism) is imported and called COMPLETELY
UNCHANGED. The only thing that varies across this leg's arms is the scalar
`ridge_deployed` argument passed into it: `ridge_deployed = alpha *
deployed_ridge` for a REGISTERED, FIXED alpha in {0.05, 0.10, 0.20, 0.50,
1.00}. No new per-column mechanism, no new calibration statistic, no new
design/penalty formula, and (per the outer task's own registration text,
which lists no specificity control for this leg) no new specificity
control are introduced. The genuinely NEW code is (i) the alpha-ladder
dispatcher (`_resolve_all_params`/`_forced_route_derivative_for_arm`), (ii)
a cheap pre-flight `--stage smoke` (this leg's analogue of M4-G4's
`--stage calibrate` / M4-G5's `--stage inventory`, adapted since no new
calibration constant or column inventory is introduced here -- instead it
directly verifies the alpha-ridge arithmetic and the alpha=1.00 identity
with the separately-named `column_standardized` anchor, cheaply, before the
full 8-world sweep), (iii) disclosed near-duplicates of G5's own
`_g3_spot_check`/`_truth_rows_for_context`, generalizing the arm-dispatch
set from G5's `{column_standardized, diagonal_ridge}` to this leg's
`{column_standardized} + colstd_alpha_<k> ladder`, and (iv) the assembly
bookkeeping this leg's own three leans (a)/(b)/(c) and PIVOT-IF need,
including the full alpha x c x budget recovery-error surface no prior leg
in this line computed (no prior leg swept a STRENGTH ladder at fixed
SHAPE).

===========================================================================
PART 0 -- THE STRENGTH-INVARIANCE ARGUMENT (a provable extension of M4-G5's
own Part 0.5, disclosed BEFORE compute), THE ALPHA-LADDER READING, AND
REGISTERED-AMBIGUITY RESOLUTIONS.
===========================================================================

--- 0.1 Why lean (a) is expected, a priori, to hold at EVERY alpha ----------

M4-G5's Part 0.5 proved: writing `beta = D(c)^{-1} gamma` (`D(c) :=
diag(scale_j(c))`, `scale_j(c) = sqrt(var_j(c))`, the per-column
standardization scale), `design(c) @ beta = design(1) @ gamma` EXACTLY for
any c (a direct consequence of `design(c) = design(1) D(c)`, itself proved
from `_hazard_design`'s own column-degree table), and the ridge penalty
`0.5 * ridge_deployed * n * ||beta_std||^2` is, by construction, ALREADY
expressed in `gamma = beta_std` coordinates -- so the reparameterized
penalized objective, `deviance(design(1) gamma) + 0.5 * ridge_deployed * n
* ||gamma||^2`, has NO dependence on c anywhere, and Newton/IRLS is
covariant under this reparameterization, so the entire iterate sequence in
gamma-coordinates is identical at every c.

`g3._fit_logistic_adaptive` (verified directly, estimator.py-mirroring
`run_suica_m4_g3_scale_adaptive.py:526-563`) constructs its penalty as
`penalty = ridge * len(y) * np.eye(p)` with `penalty[0,0]=0.0` -- i.e. the
`ridge` argument is a PURE SCALAR multiplying `n*I` (intercept exempt),
with NO other dependence on c anywhere in the penalty. Replacing
`ridge_deployed` with `ridge_used(alpha) := alpha * ridge_deployed` for a
REGISTERED, FIXED (not c-dependent) alpha therefore substitutes one
c-independent scalar constant for another: the reparameterized objective
becomes `deviance(design(1) gamma) + 0.5 * (alpha*ridge_deployed) * n *
||gamma||^2`, which is STILL exactly c-independent, for ANY fixed alpha.
**Consequence: `column_standardized` at ANY fixed alpha should be
c-invariant up to floating point, not merely at alpha=1.0 (deployed).**
This is the mathematical content of lean (a) ("invariance is
strength-free"), stated here as a provable prediction BEFORE compute, not
an outcome asserted after the fact. What this argument does NOT predict:
which alpha gives the LOWEST recovery error -- that is a fact about the
actual loss landscape at each alpha, an open empirical question leans
(b)/(c) exist to answer, with no a priori shortcut.

--- 0.2 The alpha-ladder reading (registered, literal, no disclosed
    ambiguity) --------------------------------------------------------------

"`column_standardized` at an overall-strength ladder alpha/deployed in
{0.05, 0.10, 0.20, 0.50, 1.00}" is read literally: `ridge_used(alpha,
context) := alpha * deployed_ridge(context)`, where `deployed_ridge(context)
:= context["fit_kwargs"]["hazard_ridge"]` (the SAME per-context lookup
every prior leg in this line has used, verified in M4-G4's own `--stage
calibrate` to be a single constant, 0.005, across all 64 (world,rep)
contexts -- re-verified here directly, not merely cited, via
`--stage smoke`, before the full sweep). At alpha=1.00 this is, BY
CONSTRUCTION, the IDENTICAL computation M4-G5's own `column_standardized`
anchor already performs (same function, same `ridge_deployed` value) --
this leg computes BOTH the `column_standardized` anchor (reproducing
M4-G5's persisted values, G1) AND the `colstd_alpha_1.00` ladder point
(a fresh, independent call through the SAME code path) as two SEPARATELY-
NAMED arms, and verifies they are bit-identical (`--stage smoke` and an
assembly-time structural check) -- a free, built-in consistency check, not
a redundant compute mistake.

--- 0.3 Registered-ambiguity resolutions (disclosed, not silently picked) --

(i) SCOPE OF "every arm evaluated across c in {0.25, 1.0, 4.0}". Read as
applying to the SUBSTANTIVE arm family under test -- `column_standardized`
(itself computed at all three c by M4-G5, reproduced here identically) and
the five `colstd_alpha_<k>` ladder arms, since these are exactly what
leans (a)/(c) need swept across c. `baseline` and `g3_raw_scale` retain the
M4-G4/M4-G5-precedented "c=1-only anchor" scope (M4-G4's own docstring:
"`baseline` and `g3_raw_scale` are computed ONLY at c=1 in this leg's own
new compute"; M4-G5 carried this forward verbatim) because NONE of this
leg's three registered leans references either arm at any c other than 1.0
-- lean (b) compares each alpha's c=1 value against `g3_raw_scale`'s OWN
c=1 value; no lean references `baseline` at all except as a descriptive
reference point. Recomputing them at c=0.25/4.0 here would only re-derive
numbers this line has already published and gated (M4-G2/M4-G3's own
persisted values), at real compute cost, touching none of this leg's own
leans -- the identical reasoning M4-G4 itself gave for the same scope
reduction.
(ii) LEAN (b)/(a) COMPUTED UNCONDITIONALLY FOR EVERY ALPHA, not gated on
lean (a) holding first (M4-G4/M4-G5's own convention officially gated lean
(b) on lean (a) holding, computing the ungated version only as a "disclosed
companion"). This leg computes BOTH leans for every one of the five alphas
unconditionally, because the PIVOT-IF condition ("no alpha ... is BOTH
c-invariant AND at least as good") needs the JOINT per-alpha (lean a AND
lean b) status explicitly, for every alpha -- gating would leave that joint
status undefined for any alpha that happened to miss lean (a). Cost is
zero marginal compute either way (both leans are pure post-hoc aggregation
over already-computed truth rows).
(iii) LEAN (c) "recovery error" measured PER BUDGET (primary, ADOPTED)
versus BUDGET-POOLED (secondary, disclosed). Every other lean throughout
this M4-G line (G1-G5) is evaluated "both budgets" separately and never
silently pooled; the ADOPTED reading preserves that convention. The
budget-pooled argmin is reported as a disclosed secondary check (Part 1).
A median-based (vs mean-based) argmin is also reported as a disclosed
robustness check, given this line's own repeated flagging of
`_relative_error`'s near-zero-denominator fragility (mitigated by the
valid-6-world subset, reused verbatim, but not eliminated as a matter of
principle).
(iv) `basis_c1` ARGUMENT TO `g5._forced_route_derivative_columnwise`. That
function's `treatment=="column_standardized"` branch never references its
`basis_c1` parameter at all (verified directly by reading
`scripts/run_suica_m4_g5_per_column_ridge.py:579-591` -- only the
`diagonal_ridge` branch, never invoked by this leg, uses it). This leg
passes the SAME basis object for both positional arguments rather than
building a redundant `c=1` basis every call -- safe (never dereferenced)
and saves one `_bases_from_whitening` call per (context, c) versus a
naively "symmetric" call.

===========================================================================
DESIGN (registered)
===========================================================================
Reuse M4-G5's 8 worlds (`g4.D1_WORLDS`), objective path, and gate helpers
verbatim. Registered analysis grain: AUTHOR (n up to 745, M4-G2's valid
6-world subset, degenerate-reference exclusion, reused verbatim).

Eight arms:
  baseline                -- c=1 only (anchor to M4-G5 persisted value).
  g3_raw_scale             -- c=1 only (anchor to M4-G5 persisted value).
  column_standardized       -- c in {0.25,1,4}, full new compute (anchor to
                               M4-G5 persisted value at all three c --
                               M4-G5 itself computed and persisted this arm
                               at all three c, all identical).
  colstd_alpha_0.05         -- c in {0.25,1,4}, full new compute.
  colstd_alpha_0.10         -- c in {0.25,1,4}, full new compute.
  colstd_alpha_0.20         -- c in {0.25,1,4}, full new compute.
  colstd_alpha_0.50         -- c in {0.25,1,4}, full new compute.
  colstd_alpha_1.00         -- c in {0.25,1,4}, full new compute (expected
                               bit-identical to `column_standardized`, see
                               0.2 -- an internal consistency check, not an
                               independent arm in the statistical sense).

No offset/GPA stage: this leg's only mechanism (`column_standardized`)
never calls `_bases_from_whitening` beyond the plain, unchanged basis
construction every arm in this line already uses; no gate here references
`offset_norm`.

Chunked execution (this arc's standard workaround; also the outer task's
own explicit process rule -- "drive every compute stage yourself in the
FOREGROUND, in chunks"): `--stage smoke` (no `--world`; cheap alpha-ladder
correctness pre-check, no full author/budget sweep) -> `--stage truth
--world W` (one world's full arm x c x budget sweep) -> `--assemble` (reads
every partial, cross-checks completeness, adjudicates).
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_suica_m4_d_dleg_floor_leg4 as leg4  # noqa: E402  bit-exact reuse
import run_suica_m4_d_overspan_control_leg3 as leg3  # noqa: E402
import run_suica_m4_d_direction_anatomy_leg10 as leg10  # noqa: E402
import run_suica_m4_d_perturbation_leg11 as leg11  # noqa: E402
import run_suica_m4_g1_whitening_intervention as g1  # noqa: E402
import run_suica_m4_g2_metric_units as g2  # noqa: E402
import run_suica_m4_g3_scale_adaptive as g3  # noqa: E402
import run_suica_m4_g4_covariant_ridge as g4  # noqa: E402
import run_suica_m4_g5_per_column_ridge as g5  # noqa: E402  the leg this extends

from suica_core.m4_chart_ecology_generator import M4ChartEcologySpec, generate_m4_chart_ecology_world  # noqa: E402

ROLES = leg11.ROLES
FLIP_TOLERANCE = leg4.FLIP_TOLERANCE
D1_WORLDS = g4.D1_WORLDS
VALID_TRUTH_WORLDS = g4.VALID_TRUTH_WORLDS
TRUTH_VALIDITY_THRESHOLD = g4.TRUTH_VALIDITY_THRESHOLD
TRUTH_BUDGETS = g4.TRUTH_BUDGETS
C_LADDER = g4.C_LADDER
assert C_LADDER == (0.25, 1.0, 4.0)
assert TRUTH_BUDGETS == (4.0, 8.0)

DEPLOYED_WEIGHT_FLOOR = g4.DEPLOYED_WEIGHT_FLOOR
DEPLOYED_CLIP_BOUND = g4.DEPLOYED_CLIP_BOUND
DEPLOYED_TOL_VALUE = g4.DEPLOYED_TOL_VALUE
DEPLOYED_PROBE_EPSILON = g4.DEPLOYED_PROBE_EPSILON

ALPHA_LADDER = (0.05, 0.10, 0.20, 0.50, 1.00)  # registered; NOT extendable after seeing results
ALPHA_ARM_NAMES = tuple(f"colstd_alpha_{a:.2f}" for a in ALPHA_LADDER)
ALPHA_BY_ARM = dict(zip(ALPHA_ARM_NAMES, ALPHA_LADDER))

MY_ARM_NAMES = ("baseline", "g3_raw_scale", "column_standardized") + ALPHA_ARM_NAMES
ANCHOR_ONLY_C1_ARMS = ("baseline", "g3_raw_scale")  # G4/G5's own compute-scope reduction, carried over (0.3.i)
COLSTD_FAMILY_ARMS = ("column_standardized",) + ALPHA_ARM_NAMES  # dispatch via g5._forced_route_derivative_columnwise
FULL_C_SWEEP_ARMS = COLSTD_FAMILY_ARMS

G1_ANCHOR_TOLERANCE = 1e-12
G3_TOLERANCE = 1e-12
LEAN_A_MARGIN = g4.LEAN_A_MARGIN  # 0.02, reused (see Part 0 header note)
LEAN_B_MARGIN = g4.LEAN_B_MARGIN  # 0.02, reused
G0_FRACTION_BAR = g4.G0_FRACTION_BAR  # 0.01, reused

G5_TRUTH_PATH = ROOT / "results" / "m4_g5_per_column_ridge" / "truth_recovery_rows.csv"
G5_DECISION_PATH = ROOT / "results" / "m4_g5_per_column_ridge" / "decision.json"


def _load_g5_decision() -> dict[str, Any]:
    with G5_DECISION_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


# ---------------------------------------------------------------------------
# per-context arm parameter resolution (Part 0.2/0.3)
# ---------------------------------------------------------------------------


def _resolve_all_params(
    context: dict[str, Any], ingredients: dict[str, Any], c: float
) -> tuple[dict[str, dict[str, Any]], dict[str, np.ndarray], float, float]:
    deployed_ridge = float(context["fit_kwargs"]["hazard_ridge"])
    raw_scale = float(np.mean(ingredients["eigenvalues"][ingredients["retained"]]))
    whitening = g2._whitening_for_c(ingredients, c)  # unchanged, reused
    basis = leg10._bases_from_whitening(context, ingredients, whitening)  # unchanged, reused
    defaults = {
        "weight_floor": DEPLOYED_WEIGHT_FLOOR, "clip_bound": DEPLOYED_CLIP_BOUND,
        "tol_mode": "absolute", "tol_value": DEPLOYED_TOL_VALUE, "probe_epsilon": DEPLOYED_PROBE_EPSILON,
    }
    resolved: dict[str, dict[str, Any]] = {
        "baseline": {"ridge": deployed_ridge, **defaults},
        "g3_raw_scale": {"ridge": deployed_ridge * raw_scale, **defaults},  # G3's own A1 formula, verbatim
        "column_standardized": {"ridge_deployed": deployed_ridge, "alpha": 1.0, **defaults},
    }
    for arm in ALPHA_ARM_NAMES:
        alpha = ALPHA_BY_ARM[arm]
        resolved[arm] = {"ridge_deployed": float(alpha * deployed_ridge), "alpha": alpha, **defaults}
    return resolved, basis, raw_scale, deployed_ridge


def _forced_route_derivative_for_arm(
    calibration: dict[str, np.ndarray],
    selection: dict[str, np.ndarray],
    basis: dict[str, np.ndarray],
    *,
    arm: str,
    model: str,
    params: dict[str, Any],
    fit_kwargs: dict[str, Any],
    dims: int,
) -> np.ndarray:
    """This leg's own arm dispatcher: every `COLSTD_FAMILY_ARMS` member
    (`column_standardized` and the five `colstd_alpha_<k>` ladder points)
    routes through `g5._forced_route_derivative_columnwise` UNCHANGED,
    varying only the `ridge_deployed` scalar passed in (Part 0.2); every
    other arm (`baseline`, `g3_raw_scale`) routes through
    `g3._forced_route_derivative_adaptive` UNCHANGED, exactly as every
    prior leg in this line has called it. `basis_c1` is passed as the SAME
    `basis` object (Part 0.3.iv) -- never dereferenced by the
    `column_standardized` treatment branch."""
    if arm in COLSTD_FAMILY_ARMS:
        return g5._forced_route_derivative_columnwise(
            calibration, selection, basis, basis, model=model, treatment="column_standardized",
            ridge_deployed=params["ridge_deployed"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
            weight_floor=params["weight_floor"], clip_bound=params["clip_bound"],
            tol_mode=params["tol_mode"], tol_value=params["tol_value"], probe_epsilon=params["probe_epsilon"],
        )
    return g3._forced_route_derivative_adaptive(
        calibration, selection, basis, model=model,
        hazard_ridge=params["ridge"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
        weight_floor=params["weight_floor"], clip_bound=params["clip_bound"],
        tol_mode=params["tol_mode"], tol_value=params["tol_value"], probe_epsilon=params["probe_epsilon"],
    )


# ---------------------------------------------------------------------------
# G3-style truth-path invariance spot check (disclosed near-duplicate of
# G5's own `_g3_spot_check`, generalized to this leg's own arm set).
# ---------------------------------------------------------------------------


def _g3_spot_check(world: str, contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dims = contexts[0]["flat"][("train", 0)][0]["response_next"].shape[1]
    rep_idx = view = author = context = stack = None
    for candidate_rep_idx, candidate_context in enumerate(contexts):
        found = False
        for candidate_view in ("train", "test"):
            for candidate_author in range(candidate_context["authors"]):
                candidate_stack = candidate_context["oracle_stacks"][candidate_view][candidate_author]
                if float(np.linalg.norm(candidate_stack["D"])) >= FLIP_TOLERANCE:
                    rep_idx, view, author, context, stack = (
                        candidate_rep_idx, candidate_view, candidate_author, candidate_context, candidate_stack,
                    )
                    found = True
                    break
            if found:
                break
        if found:
            break
    if context is None:
        raise RuntimeError(f"G3 spot check found NO non-degenerate (rep,view,author) on {world}")

    route = stack["selected_model"]
    fit_kwargs = context["fit_kwargs"]
    calibration_flat, selection_flat, _ = context["flat"][(view, author)]
    d_true = leg4._true_derivative(context["truth"], author)
    calibration_g3 = leg4._flatten_events(context["observed"].ecology.train_calibration, author)
    selection_g3 = leg4._flatten_events(context["observed"].ecology.train_selection, author)

    ingredients = leg10._freeze_ingredients(context)

    rows: list[dict[str, Any]] = []
    for c in C_LADDER:
        resolved, basis, _raw_scale, _deployed_ridge = _resolve_all_params(context, ingredients, c)
        arms_here = MY_ARM_NAMES if c == 1.0 else FULL_C_SWEEP_ARMS
        for arm in arms_here:
            params = resolved[arm]
            d_gapstyle = _forced_route_derivative_for_arm(
                calibration_flat, selection_flat, basis, arm=arm, model=route, params=params, fit_kwargs=fit_kwargs, dims=dims,
            )
            d_truthpath = _forced_route_derivative_for_arm(
                calibration_g3, selection_g3, basis, arm=arm, model=route, params=params, fit_kwargs=fit_kwargs, dims=dims,
            )
            e_gapstyle = leg3._relative_error(d_gapstyle, d_true)
            e_truthpath = leg3._relative_error(d_truthpath, d_true)
            rows.append(
                {
                    "world": world, "arm": arm, "c": c, "repetition": rep_idx, "view": view, "author": author,
                    "e_arm_true_gapstyle": e_gapstyle, "e_arm_true_truthpath_budget1": e_truthpath,
                    "abs_diff": abs(e_gapstyle - e_truthpath),
                }
            )
    return rows


# ---------------------------------------------------------------------------
# stage: smoke (cheap pre-flight; this leg's analogue of G4's "calibrate" /
# G5's "inventory" stage -- verifies the alpha-ridge arithmetic and the
# alpha=1.00 <-> column_standardized identity BEFORE the full 8-world sweep)
# ---------------------------------------------------------------------------


def _run_smoke(config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    rows: list[dict[str, Any]] = []
    for world in D1_WORLDS:
        contexts = g1._build_world_contexts(world, config, spec)
        context0 = contexts[0]
        deployed_ridge = float(context0["fit_kwargs"]["hazard_ridge"])

        g3_rows = _g3_spot_check(world, contexts)
        g3_max = max(row["abs_diff"] for row in g3_rows)
        df = pd.DataFrame(g3_rows)
        c1 = df[df["c"] == 1.0]
        std_val = float(c1[c1["arm"] == "column_standardized"]["e_arm_true_gapstyle"].iloc[0])
        alpha1_val = float(c1[c1["arm"] == "colstd_alpha_1.00"]["e_arm_true_gapstyle"].iloc[0])
        identity_diff = abs(std_val - alpha1_val)

        ridge_arith_max_diff = 0.0
        for arm in ALPHA_ARM_NAMES:
            alpha = ALPHA_BY_ARM[arm]
            expected = alpha * deployed_ridge
            realized = float(_resolve_all_params(context0, leg10._freeze_ingredients(context0), 1.0)[0][arm]["ridge_deployed"])
            ridge_arith_max_diff = max(ridge_arith_max_diff, abs(expected - realized))

        rows.append(
            {
                "world": world, "deployed_ridge": deployed_ridge, "g3_max_abs_diff": g3_max,
                "colstd_vs_alpha1_identity_diff": identity_diff, "ridge_arithmetic_max_diff": ridge_arith_max_diff,
            }
        )
        print(
            f"[m4g6] smoke {world}: g3_max={g3_max:.3e} colstd_vs_alpha1={identity_diff:.3e} "
            f"ridge_arith={ridge_arith_max_diff:.3e} deployed_ridge={deployed_ridge}",
            flush=True,
        )

    df_out = pd.DataFrame(rows)
    output.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(output / "smoke_check.csv", index=False)

    deployed_values = df_out["deployed_ridge"].unique()
    max_g3 = float(df_out["g3_max_abs_diff"].max())
    max_identity = float(df_out["colstd_vs_alpha1_identity_diff"].max())
    max_ridge_arith = float(df_out["ridge_arithmetic_max_diff"].max())

    if len(deployed_values) != 1:
        raise RuntimeError(f"smoke: deployed ridge not constant across contexts: {deployed_values}")
    if max_g3 > G3_TOLERANCE:
        raise RuntimeError(f"smoke: G3 truth-path invariance fails: {max_g3:.3e}")
    if max_identity > G1_ANCHOR_TOLERANCE:
        raise RuntimeError(f"smoke: colstd_alpha_1.00 does not match column_standardized: {max_identity:.3e}")
    if max_ridge_arith > 0.0:
        raise RuntimeError(f"smoke: ridge-arithmetic mismatch: {max_ridge_arith:.3e}")
    print(
        f"[m4g6] smoke check PASS: max_g3={max_g3:.3e} max_identity={max_identity:.3e} "
        f"max_ridge_arith={max_ridge_arith:.3e} deployed_ridge={float(deployed_values[0])}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# stage: truth (per world) -- disclosed near-duplicate of G5's own
# `_truth_rows_for_context`, generalized over this leg's own arm dispatcher.
# ---------------------------------------------------------------------------


def _truth_rows_for_context(
    context: dict[str, Any],
    arm_bases_rep: dict[str, dict[str, np.ndarray]],
    resolved_rep: dict[str, dict[str, Any]],
    spec: M4ChartEcologySpec,
    budget: float,
    c: float,
    *,
    arms: tuple[str, ...],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    world = context["world"]
    repetition = context["repetition"]
    truth = context["truth"]
    fit_kwargs = context["fit_kwargs"]
    dims = context["flat"][("train", 0)][0]["response_next"].shape[1]
    events_b = int(round(spec.events * budget))
    if budget == 1.0:
        observed_b = context["observed"]
        truth_b = truth
    else:
        spec_b = replace(spec, events=events_b)
        observed_b, truth_b = generate_m4_chart_ecology_world(world=world, spec=spec_b, seed=context["seed"])
        for role in ROLES:
            if not np.array_equal(truth_b.oracle_basis[role], truth.oracle_basis[role]):
                raise RuntimeError(f"frozen-world violation at budget {budget}: {world} rep {repetition}")
        for name in ("creation", "gate", "generated_base", "selection"):
            if not np.array_equal(truth_b.author_parameters[name], truth.author_parameters[name]):
                raise RuntimeError(f"frozen-world violation at budget {budget}: {world} rep {repetition}")
    rows: list[dict[str, Any]] = []
    n_cal_rows = n_sel_rows = 0
    for view in ("train", "test"):
        calibration_panel = getattr(observed_b.ecology, f"{view}_calibration")
        selection_panel = getattr(observed_b.ecology, f"{view}_selection")
        for author in range(context["authors"]):
            stack = context["oracle_stacks"][view][author]
            degenerate = bool(float(np.linalg.norm(stack["D"])) < FLIP_TOLERANCE)
            keys = {
                "world": world, "repetition": repetition, "view": view, "author": author,
                "budget": budget, "events": events_b, "degenerate_reference": degenerate,
            }
            if degenerate:
                for arm in arms:
                    rows.append({**keys, "arm": arm, "c": c, "e_arm_true": np.nan, "e_orc_true": np.nan})
                continue
            route = stack["selected_model"]
            calibration_b = leg4._flatten_events(calibration_panel, author)
            selection_b = leg4._flatten_events(selection_panel, author)
            n_cal_rows = len(calibration_b["choice"])
            n_sel_rows = len(selection_b["choice"])
            d_true = leg4._true_derivative(truth, author)
            d_orc_b = leg4._forced_route_derivative(
                calibration_b, selection_b, truth.oracle_basis, model=route,
                hazard_ridge=fit_kwargs["hazard_ridge"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
            )
            e_orc_true = leg3._relative_error(d_orc_b, d_true)
            for arm in arms:
                basis = arm_bases_rep[arm]
                params = resolved_rep[arm]
                d_arm_b = _forced_route_derivative_for_arm(
                    calibration_b, selection_b, basis, arm=arm, model=route, params=params, fit_kwargs=fit_kwargs, dims=dims,
                )
                e_arm_true = leg3._relative_error(d_arm_b, d_true)
                rows.append({**keys, "arm": arm, "c": c, "e_arm_true": e_arm_true, "e_orc_true": e_orc_true})
    gate = {
        "world": world, "repetition": repetition, "budget": budget, "events": events_b,
        "n_cal_rows_last": n_cal_rows, "n_sel_rows_last": n_sel_rows,
    }
    return rows, gate


def _run_truth_stage(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    contexts = g1._build_world_contexts(world, config, spec)

    g3_rows = _g3_spot_check(world, contexts)
    g3_max = max(row["abs_diff"] for row in g3_rows)
    if g3_max > G3_TOLERANCE:
        raise RuntimeError(f"G3 truth-path invariance fails on {world}: {g3_max:.3e}")

    all_rows: list[dict[str, Any]] = []
    per_rep_meta: list[dict[str, Any]] = []
    truth_gates: list[dict[str, Any]] = []
    for rep_idx, context in enumerate(contexts):
        ingredients = leg10._freeze_ingredients(context)
        rep_meta: dict[str, Any] = {
            "world": world, "repetition": rep_idx, "k_retained": int(len(ingredients["retained"])),
        }
        for c in C_LADDER:
            resolved, basis, raw_scale, deployed_ridge = _resolve_all_params(context, ingredients, c)
            rep_meta[f"raw_scale_c{c:g}"] = raw_scale
            rep_meta[f"deployed_ridge_c{c:g}"] = deployed_ridge
            arms_here = MY_ARM_NAMES if c == 1.0 else FULL_C_SWEEP_ARMS
            arm_bases_rep = {arm: basis for arm in arms_here}
            resolved_rep = {arm: resolved[arm] for arm in arms_here}
            for arm in arms_here:
                params = resolved_rep[arm]
                ridge_used = params.get("ridge", params.get("ridge_deployed"))
                rep_meta[f"ridge_used_{arm}_c{c:g}"] = ridge_used
                rep_meta[f"weight_floor_{arm}_c{c:g}"] = params["weight_floor"]
            for budget in TRUTH_BUDGETS:
                started = time.time()
                rows, gate = _truth_rows_for_context(context, arm_bases_rep, resolved_rep, spec, budget, c, arms=arms_here)
                for row in rows:
                    if row["c"] != c:
                        raise RuntimeError(f"c mismatch: expected {c}, row={row}")
                all_rows.extend(rows)
                truth_gates.append(gate)
                print(
                    f"[m4g6] truth c={c:g} b={budget:g} {world} rep={rep_idx} arms={len(arms_here)} ({time.time()-started:.1f}s)",
                    flush=True,
                )
        per_rep_meta.append(rep_meta)

    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(all_rows).to_csv(output / f"partial_truth_{world}.csv", index=False)
    pd.DataFrame(per_rep_meta).to_csv(output / f"partial_context_meta_{world}.csv", index=False)
    pd.DataFrame(g3_rows).to_csv(output / f"partial_g3check_{world}.csv", index=False)
    gates = {"world": world, "truth_gates": truth_gates, "g3_max_abs_diff": g3_max}
    with (output / f"partial_gates_truth_{world}.json").open("w", encoding="utf-8") as handle:
        json.dump(gates, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(f"[m4g6] truth stage done: {world}", flush=True)


# ---------------------------------------------------------------------------
# assemble + adjudicate
# ---------------------------------------------------------------------------


def _pooled_mean_median(author_truth: pd.DataFrame, arm: str, c: float, budget: float, worlds: list[str]) -> tuple[float, float, int]:
    scoped = author_truth[
        (author_truth["arm"] == arm) & (author_truth["c"] == c) & (author_truth["budget"] == budget)
        & (author_truth["world"].isin(worlds))
    ]
    return float(scoped["e_arm_true"].mean()), float(scoped["e_arm_true"].median()), int(len(scoped))


def _assemble(output: Path) -> None:
    worlds = list(D1_WORLDS)
    valid_worlds = list(VALID_TRUTH_WORLDS)

    truth_frames = [pd.read_csv(output / f"partial_truth_{w}.csv") for w in worlds]
    truth_rows = pd.concat(truth_frames, ignore_index=True)
    g3check_frames = [pd.read_csv(output / f"partial_g3check_{w}.csv") for w in worlds]
    g3check_rows = pd.concat(g3check_frames, ignore_index=True)
    meta_frames = [pd.read_csv(output / f"partial_context_meta_{w}.csv") for w in worlds]
    context_meta = pd.concat(meta_frames, ignore_index=True)

    expected_truth_rows = 0
    for c in C_LADDER:
        n_arms = len(MY_ARM_NAMES) if c == 1.0 else len(FULL_C_SWEEP_ARMS)
        expected_truth_rows += len(worlds) * len(TRUTH_BUDGETS) * 8 * 2 * 16 * n_arms
    if len(truth_rows) != expected_truth_rows:
        raise RuntimeError(f"truth rows {len(truth_rows)} != expected {expected_truth_rows}")

    # ---- G3 TRUTH-PATH INVARIANCE -------------------------------------------
    g3_gate = {
        "statement": "truth path at budget=1.0 reproduces gap-stage-style e_arm_true exactly, all (arm,c) combinations tested",
        "max_abs_diff": float(g3check_rows["abs_diff"].max()),
        "n_checks": int(len(g3check_rows)),
        "tolerance": G3_TOLERANCE,
        "pass": bool(g3check_rows["abs_diff"].max() <= G3_TOLERANCE),
    }

    # ---- numerical-validity diagnostic: recompute valid-6-world subset -------
    orc_rows = []
    for budget in TRUTH_BUDGETS:
        scoped = truth_rows[(truth_rows["budget"] == budget) & (~truth_rows["degenerate_reference"]) & (truth_rows["arm"] == "baseline")]
        for w in worlds:
            median_e_orc = float(scoped[scoped["world"] == w]["e_orc_true"].median())
            orc_rows.append({"world": w, "budget": budget, "median_e_orc_true": median_e_orc})
    orc_diag = pd.DataFrame(orc_rows)
    worst_per_world = orc_diag.groupby("world")["median_e_orc_true"].max()
    recomputed_valid_worlds = sorted(worst_per_world[worst_per_world <= TRUTH_VALIDITY_THRESHOLD].index.tolist())
    valid_world_subset_reproduced = recomputed_valid_worlds == sorted(VALID_TRUTH_WORLDS)

    # ---- G1 ANCHOR: baseline@c=1, g3_raw_scale@c=1, column_standardized@{.25,1,4}
    # vs M4-G5's own persisted values -----------------------------------------
    m4g5_truth = pd.read_csv(G5_TRUTH_PATH)
    anchor_rows = []
    anchor_plan = [
        ("baseline", "baseline", (1.0,)),
        ("g3_raw_scale", "g3_raw_scale", (1.0,)),
        ("column_standardized", "column_standardized", C_LADDER),
    ]
    for mine_arm, g5_arm, c_values in anchor_plan:
        mine = truth_rows[(truth_rows["arm"] == mine_arm) & (truth_rows["c"].isin(c_values))]
        theirs = m4g5_truth[(m4g5_truth["arm"] == g5_arm) & (m4g5_truth["c"].isin(c_values))]
        joined = mine.merge(theirs, on=["world", "repetition", "view", "author", "budget", "c"], suffixes=("_mine", "_theirs"), how="inner")
        expected = len(worlds) * len(TRUTH_BUDGETS) * 8 * 2 * 16 * len(c_values)
        if len(joined) != expected:
            raise RuntimeError(f"G1 anchor join size {len(joined)} != expected {expected} for {mine_arm}")
        diff = (joined["e_arm_true_mine"] - joined["e_arm_true_theirs"]).abs()
        anchor_rows.append(
            {"arm": mine_arm, "g5_arm": g5_arm, "c_values": list(c_values), "n_rows": int(len(joined)), "max_abs_diff": float(diff.max(skipna=True))}
        )
    g1_anchor_max = max(row["max_abs_diff"] for row in anchor_rows)
    g1_anchor = {
        "per_arm": anchor_rows, "max_abs_diff": g1_anchor_max, "tolerance": G1_ANCHOR_TOLERANCE,
        "pass": bool(g1_anchor_max <= G1_ANCHOR_TOLERANCE),
        "note": (
            "baseline/g3_raw_scale anchored at c=1 only (M4-G4/M4-G5's own compute-scope reduction, "
            "carried over verbatim, Part 0.3.i). column_standardized anchored at ALL THREE c against "
            "M4-G5's own persisted values (M4-G5 itself fully computed this arm at all three c)."
        ),
    }

    # ---- structural check: colstd_alpha_1.00 vs column_standardized identity -
    std_rows = truth_rows[truth_rows["arm"] == "column_standardized"]
    alpha1_rows = truth_rows[truth_rows["arm"] == "colstd_alpha_1.00"]
    identity_joined = std_rows.merge(
        alpha1_rows, on=["world", "repetition", "view", "author", "budget", "c"], suffixes=("_std", "_alpha1"), how="inner"
    )
    expected_identity = len(worlds) * len(TRUTH_BUDGETS) * 8 * 2 * 16 * len(C_LADDER)
    if len(identity_joined) != expected_identity:
        raise RuntimeError(f"identity join size {len(identity_joined)} != expected {expected_identity}")
    identity_diff = (identity_joined["e_arm_true_std"] - identity_joined["e_arm_true_alpha1"]).abs()
    identity_check = {
        "statement": "colstd_alpha_1.00 (ladder point) vs column_standardized (separately-named anchor) -- same mechanism, same ridge_deployed value, called independently; expected bit-identical (Part 0.2)",
        "n_rows": int(len(identity_joined)), "max_abs_diff": float(identity_diff.max(skipna=True)),
        "tolerance": G1_ANCHOR_TOLERANCE, "pass": bool(identity_diff.max(skipna=True) <= G1_ANCHOR_TOLERANCE),
    }

    author_truth = g4._author_level_truth_with_c(truth_rows)  # unchanged, reused

    # ---- G0 POWER (author grain, vs M4-G5's persisted .051-.062 lean-b gap) --
    g5_decision = _load_g5_decision()
    g5_gaps = []
    for arm_key in ("column_standardized", "diagonal_ridge"):
        for row in g5_decision["lean_b_no_loss"]["disclosed_companion_all_new_arms_regardless_of_lean_a"][arm_key]["rows"]:
            g5_gaps.append(row["author_mean_diff_candidate_minus_g3raw"])
    g5_gap_min, g5_gap_max = float(min(g5_gaps)), float(max(g5_gaps))

    g0_probe_rows = []
    lean_a_by_alpha: dict[str, Any] = {}
    lean_b_by_alpha: dict[str, Any] = {}
    for arm in ALPHA_ARM_NAMES:
        chk_a = g4._c_invariance_check(author_truth, arm, valid_worlds)  # unchanged, reused
        lean_a_by_alpha[arm] = chk_a
        for r in chk_a["rows"]:
            g0_probe_rows.append({**r, "check": "lean_a_strength_free_invariance"})
        chk_b = g4._no_loss_check(author_truth, arm, valid_worlds)  # unchanged, reused
        lean_b_by_alpha[arm] = chk_b
        for r in chk_b["rows"]:
            g0_probe_rows.append({**r, "check": "lean_b_recovery_recovered"})
    # disclosed companion: column_standardized's own lean-a/lean-b (redundant with colstd_alpha_1.00 by 0.2)
    column_standardized_lean_a = g4._c_invariance_check(author_truth, "column_standardized", valid_worlds)
    column_standardized_lean_b = g4._no_loss_check(author_truth, "column_standardized", valid_worlds)

    g0_df = pd.DataFrame(g0_probe_rows)
    g0_underpowered_n = int(g0_df["author_underpowered_vs_g0_bar"].sum())
    g0 = {
        "statement": (
            "AUTHOR-grain (n up to 745) CI half-width vs bar=0.01 (g4.G0_FRACTION_BAR, reused). MDE framing: "
            "this leg's own half-width, at each comparison's own sample size, is the smallest effect that "
            "comparison could distinguish from zero; reported against M4-G5's own persisted lean-b gap "
            f"({g5_gap_min:.4f}-{g5_gap_max:.4f}, both mechanisms/budgets) to state whether this leg has power "
            "to tell 'some alpha closes the gap' apart from 'no alpha closes the gap'."
        ),
        "bar_absolute": G0_FRACTION_BAR,
        "m4g5_persisted_lean_b_gap_min": g5_gap_min,
        "m4g5_persisted_lean_b_gap_max": g5_gap_max,
        "n_comparisons": int(len(g0_df)),
        "n_underpowered_vs_absolute_bar": g0_underpowered_n,
        "half_width_min": float(g0_df["author_half_width"].min()),
        "half_width_max": float(g0_df["author_half_width"].max()),
        "half_width_median": float(g0_df["author_half_width"].median()),
        "mde_vs_g5_gap_max_ratio": float(g0_df["author_half_width"].max() / g5_gap_min),
        "all_comparisons": g0_probe_rows,
    }

    # ---- G2 STRENGTH LIVENESS -------------------------------------------------
    g2_rows = []
    for arm in ALPHA_ARM_NAMES:
        alpha = ALPHA_BY_ARM[arm]
        per_c = {}
        for c in C_LADDER:
            ridge_col = f"ridge_used_{arm}_c{c:g}"
            dep_col = f"deployed_ridge_c{c:g}"
            ridge_mean = float(context_meta[ridge_col].mean())
            ridge_std = float(context_meta[ridge_col].std())
            dep_mean = float(context_meta[dep_col].mean())
            ratio = ridge_mean / dep_mean if dep_mean else float("nan")
            per_c[str(c)] = {
                "mean_ridge_used": ridge_mean, "std_ridge_used_across_contexts": ridge_std,
                "mean_deployed_ridge": dep_mean, "ratio_to_deployed": ratio,
                "registered_alpha": alpha, "abs_diff_ratio_vs_alpha": abs(ratio - alpha),
            }
        moves_as_registered = bool(all(per_c[str(c)]["abs_diff_ratio_vs_alpha"] <= 1e-9 for c in C_LADDER))
        g2_rows.append({"arm": arm, "alpha": alpha, "per_c": per_c, "status": "LIVE" if moves_as_registered else "INERT/VACUOUS"})
    ladder_ratios = [g2_rows[i]["per_c"][str(1.0)]["ratio_to_deployed"] for i in range(len(g2_rows))]
    ladder_span = max(ladder_ratios) / min(ladder_ratios) if min(ladder_ratios) else float("nan")
    g2_liveness = {
        "materiality_margin": "LIVE iff realized ridge_used/deployed_ridge ratio equals the registered alpha to <=1e-9 absolute, at every c (an alpha whose ratio does not move with alpha -- e.g. stuck at 1.0 regardless of alpha -- is INERT/VACUOUS, per the outer task's own wording)",
        "per_alpha": g2_rows,
        "ladder_span_ratio_max_over_min_at_c1": ladder_span,
        "ladder_span_registered_expected": float(max(ALPHA_LADDER) / min(ALPHA_LADDER)),
        "all_alphas_live": bool(all(row["status"] == "LIVE" for row in g2_rows)),
    }

    # ---- leans -----------------------------------------------------------------
    lean_a_held_alphas = [arm for arm, chk in lean_a_by_alpha.items() if chk["held"]]
    lean_a_all_held = bool(len(lean_a_held_alphas) == len(ALPHA_ARM_NAMES))
    lean_a_any_underpowered = bool(any(chk["status"] == "UNDERPOWERED" for chk in lean_a_by_alpha.values()))

    lean_b_held_alphas = [arm for arm, chk in lean_b_by_alpha.items() if chk["held"]]
    lean_b_any_held = bool(len(lean_b_held_alphas) > 0)

    joint_status: dict[str, dict[str, Any]] = {}
    for arm in ALPHA_ARM_NAMES:
        a_stat = lean_a_by_alpha[arm]["status"]
        b_stat = lean_b_by_alpha[arm]["status"]
        if a_stat == "HOLD" and b_stat == "HOLD":
            joint = "BOTH_HOLD"
        elif a_stat == "MISS" or b_stat == "MISS":
            joint = "DECISIVE_NOT_BOTH"
        else:
            joint = "UNDERPOWERED_NOT_RESOLVED"
        joint_status[arm] = {"lean_a_status": a_stat, "lean_b_status": b_stat, "joint": joint}

    alphas_both_hold = [a for a in ALPHA_ARM_NAMES if joint_status[a]["joint"] == "BOTH_HOLD"]
    if alphas_both_hold:
        pivot_status = "DOES_NOT_FIRE"
    elif any(joint_status[a]["joint"] == "UNDERPOWERED_NOT_RESOLVED" for a in ALPHA_ARM_NAMES):
        pivot_status = "UNDERPOWERED"
    elif all(joint_status[a]["joint"] == "DECISIVE_NOT_BOTH" for a in ALPHA_ARM_NAMES):
        pivot_status = "FIRES"
    else:
        pivot_status = "AMBIGUOUS"
    pivot_fires = bool(pivot_status == "FIRES")

    # ---- lean (c): full alpha x c x budget error surface -----------------------
    error_surface = []
    for arm in ALPHA_ARM_NAMES:
        for c in C_LADDER:
            for budget in TRUTH_BUDGETS:
                mean_e, median_e, n = _pooled_mean_median(author_truth, arm, c, budget, valid_worlds)
                error_surface.append(
                    {"arm": arm, "alpha": ALPHA_BY_ARM[arm], "c": c, "budget": budget, "mean_e_arm_true": mean_e, "median_e_arm_true": median_e, "n": n}
                )
    error_surface_df = pd.DataFrame(error_surface)

    argmin_rows = []
    for c in C_LADDER:
        for budget in TRUTH_BUDGETS:
            scoped = error_surface_df[(error_surface_df["c"] == c) & (error_surface_df["budget"] == budget)]
            best = scoped.loc[scoped["mean_e_arm_true"].idxmin()]
            best_median = scoped.loc[scoped["median_e_arm_true"].idxmin()]
            argmin_rows.append(
                {
                    "c": c, "budget": budget, "argmin_alpha_mean": float(best["alpha"]), "min_mean_e_arm_true": float(best["mean_e_arm_true"]),
                    "argmin_alpha_median": float(best_median["alpha"]), "min_median_e_arm_true": float(best_median["median_e_arm_true"]),
                    "mean_median_argmin_agree": bool(float(best["alpha"]) == float(best_median["alpha"])),
                }
            )
    argmin_df = pd.DataFrame(argmin_rows)

    per_budget_same = {}
    for budget in TRUTH_BUDGETS:
        scoped = argmin_df[argmin_df["budget"] == budget]
        alphas_by_c = scoped.set_index("c")["argmin_alpha_mean"].to_dict()
        per_budget_same[str(budget)] = {"argmin_alpha_by_c": alphas_by_c, "same_across_c": bool(len(set(alphas_by_c.values())) == 1)}
    lean_c_holds_primary = bool(all(per_budget_same[str(b)]["same_across_c"] for b in TRUTH_BUDGETS))

    pooled_rows = []
    for c in C_LADDER:
        scoped = error_surface_df[error_surface_df["c"] == c]
        pooled_by_alpha = scoped.groupby("alpha")["mean_e_arm_true"].mean()
        best_alpha = float(pooled_by_alpha.idxmin())
        pooled_rows.append({"c": c, "argmin_alpha_pooled_budgets": best_alpha, "min_pooled_mean_e_arm_true": float(pooled_by_alpha.min())})
    pooled_df = pd.DataFrame(pooled_rows)
    lean_c_holds_secondary_pooled = bool(len(set(pooled_df["argmin_alpha_pooled_budgets"])) == 1)

    median_agree_all = bool(argmin_df["mean_median_argmin_agree"].all())

    lean_c = {
        "statement": "the alpha in {0.05,0.10,0.20,0.50,1.00} minimizing pooled author-level mean e_arm_true (valid 6-world subset, n up to 745) at each (c,budget) cell",
        "error_surface": error_surface,
        "argmin_by_c_and_budget": argmin_rows,
        "primary_reading_per_budget": {
            "adopted": True, "per_budget_same_across_c": per_budget_same, "holds": lean_c_holds_primary,
        },
        "secondary_reading_budget_pooled_disclosed": {
            "adopted": False, "argmin_by_c": pooled_rows, "holds": lean_c_holds_secondary_pooled,
        },
        "median_vs_mean_argmin_agreement_robustness_check": {"all_cells_agree": median_agree_all},
    }

    certified_alpha = None
    if alphas_both_hold:
        surface_at_c1 = error_surface_df[(error_surface_df["c"] == 1.0)]
        pooled_err_by_alpha = surface_at_c1.groupby("alpha")["mean_e_arm_true"].mean()
        candidates = {a: pooled_err_by_alpha.get(ALPHA_BY_ARM[a], float("inf")) for a in alphas_both_hold}
        certified_alpha = min(candidates, key=candidates.get)

    if alphas_both_hold:
        verdict = "SHAPE_AND_STRENGTH_HOLD_AT_SOME_ALPHA"
    elif pivot_fires:
        verdict = "PIVOT_INVARIANCE_AND_RECOVERY_TRADE_OFF"
    elif pivot_status == "UNDERPOWERED":
        verdict = "UNDERPOWERED_NO_ADJUDICATION_AT_REGISTERED_GRAIN"
    else:
        verdict = "AMBIGUOUS_NO_CLEAN_BRANCH"

    # ---- G4 MATERIALITY FORM: explicit per-gate compliance ---------------------
    g4_materiality_form = {
        "G0": "CI-half-width-vs-bar equivalence bound (bar=0.01); underpowered comparisons flagged explicitly via author_underpowered_vs_g0_bar, never silently read as nulls",
        "G1": "degenerate exact-equality check (tolerance 1e-12), not a significance test",
        "G2": "ratio-vs-materiality-margin equivalence check (LIVE iff realized ratio equals registered alpha to <=1e-9), not a binary did-anything-change test",
        "G3": "degenerate exact-equality check (tolerance 1e-12) between two independently-computed derivations of the same quantity",
        "leans_a_b": "three-way WITHIN/OUTSIDE/AMBIGUOUS classification on paired-author CIs against the fixed +/-0.02 margin (g4._classify_pair), never nil-significance",
        "lean_c": "point-estimate argmin identity across c, on the full disclosed error surface, with a median-based and budget-pooled robustness check reported alongside, not substituted for, the adopted per-budget mean reading",
    }

    decision = {
        "estimand_id": "SUICA_M4_G6_SHAPE_AND_STRENGTH",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md M4-G6 registration (2026-08-03, BEFORE run); ledger row M4-G6",
        "worlds": worlds,
        "valid_truth_worlds": valid_worlds,
        "arm_names": list(MY_ARM_NAMES),
        "alpha_ladder": list(ALPHA_LADDER),
        "c_ladder": list(C_LADDER),
        "truth_budgets": list(TRUTH_BUDGETS),
        "gates": {
            "G0_power": g0,
            "G1_anchor": g1_anchor,
            "G2_strength_liveness": g2_liveness,
            "G3_truth_path_invariance": g3_gate,
            "G4_materiality_form": g4_materiality_form,
        },
        "structural_checks": {
            "recomputed_valid_worlds": recomputed_valid_worlds,
            "valid_world_subset_reproduced_from_m4g5": valid_world_subset_reproduced,
            "colstd_alpha_1.00_vs_column_standardized_identity": identity_check,
        },
        "lean_a_strength_free_invariance": {
            "per_alpha": lean_a_by_alpha,
            "held_alphas": lean_a_held_alphas,
            "all_held": lean_a_all_held,
            "any_underpowered": lean_a_any_underpowered,
            "column_standardized_disclosed_companion": column_standardized_lean_a,
        },
        "lean_b_recovery_recovered": {
            "per_alpha": lean_b_by_alpha,
            "held_alphas": lean_b_held_alphas,
            "any_held": lean_b_any_held,
            "column_standardized_disclosed_companion": column_standardized_lean_b,
        },
        "joint_a_and_b_per_alpha": joint_status,
        "pivot": {
            "registered": "no alpha in the registered ladder is both c-invariant and at least as good as g3_raw_scale -> invariance and recovery genuinely trade off",
            "fires": pivot_fires,
            "status": pivot_status,
        },
        "alphas_holding_both": alphas_both_hold,
        "headline_alpha": certified_alpha,
        "lean_c_tuning_scale_free": lean_c,
        "verdict": verdict,
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only (8 D1 worlds, reused verbatim from M4-G2/G3/G4/G5); "
            "truth-recovery statistics use M4-G2's own valid 6-world subset, reused verbatim; "
            "truth-referenced recovery via budget-regenerated (4x/8x events) finite panels from the "
            "frozen world law, compared to the analytic D_true; no natural-text, personality, or "
            "clinical claim; no seal, no independent verification (operator directive 2026-08-01)."
        ),
    }

    output.mkdir(parents=True, exist_ok=True)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    with (output / "gates.json").open("w", encoding="utf-8") as handle:
        json.dump(decision["gates"], handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    truth_rows.to_csv(output / "truth_recovery_rows.csv", index=False)
    author_truth.to_csv(output / "author_level_truth_rows.csv", index=False)
    context_meta.to_csv(output / "context_meta.csv", index=False)
    orc_diag.to_csv(output / "e_orc_true_validity_diagnostic.csv", index=False)
    pd.DataFrame(g0_probe_rows).to_csv(output / "g0_and_lean_pairwise_rows.csv", index=False)
    error_surface_df.to_csv(output / "error_surface_alpha_x_c_x_budget.csv", index=False)
    argmin_df.to_csv(output / "argmin_by_c_and_budget.csv", index=False)

    print(
        json.dumps(
            {
                "verdict": verdict, "pivot_status": pivot_status, "pivot_fires": pivot_fires,
                "lean_a_held_alphas": lean_a_held_alphas, "lean_a_all_held": lean_a_all_held,
                "lean_a_any_underpowered": lean_a_any_underpowered,
                "lean_b_held_alphas": lean_b_held_alphas, "lean_b_any_held": lean_b_any_held,
                "alphas_holding_both": alphas_both_hold, "headline_alpha": certified_alpha,
                "lean_c_holds_primary": lean_c_holds_primary, "lean_c_holds_secondary_pooled": lean_c_holds_secondary_pooled,
                "g1_anchor_pass": g1_anchor["pass"], "g3_pass": g3_gate["pass"],
                "identity_check_pass": identity_check["pass"],
                "valid_world_subset_reproduced": valid_world_subset_reproduced,
            },
            indent=2,
        )
    )


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "m4_chart_ecology.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_g6_shape_and_strength")
    parser.add_argument("--world", type=str, default=None)
    parser.add_argument("--stage", type=str, choices=("smoke", "truth"), default=None)
    parser.add_argument("--assemble", action="store_true")
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    spec = M4ChartEcologySpec(**config["base_spec"])

    if args.assemble:
        _assemble(args.output)
        return

    if args.stage is None:
        raise SystemExit("--stage is required unless --assemble")

    if args.stage == "smoke":
        _run_smoke(config, spec, args.output)
        return

    if args.world is None:
        raise SystemExit("--world is required for --stage truth")
    if args.world not in D1_WORLDS:
        raise SystemExit(f"not a registered D1 world: {args.world}")
    _run_truth_stage(args.world, config, spec, args.output)


if __name__ == "__main__":
    main()
