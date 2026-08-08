#!/usr/bin/env python3
"""M4-G4: the c-covariant ridge, at a grain that can see it.

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-G4
registration" (2026-08-03, BEFORE run); ledger row M4-G4). Machinery is
IMPORTED and REUSED, not reimplemented: M4-G1/G2/G3's world set, context
builder (`g1._build_world_contexts`), whitening-scale construction
(`g2._whitening_for_c`), basis construction (`leg10._bases_from_whitening`,
UNCHANGED -- no arm in this leg touches the intercept/A6), the parameterized
estimator internals G3 already built and disclosed
(`g3._forced_route_derivative_adaptive` and everything it calls), CI helpers
(`g1._paired_world_ci`, `g1._paired_author_ci`), and -- centrally -- G3's own
generic truth-row builder `g3._truth_rows_for_context`, called here with THIS
leg's own arm names/bases/params exactly as it is generic over `arms`. The
only new code is (i) the post-whitening scale statistics and their alpha
calibration (Part 0 below), (ii) a small `_resolve_params` dispatcher mapping
this leg's 5 arm names to ridge/weight_floor values, and (iii) this leg's own
gate/lean bookkeeping.

THE QUESTION (M4-G3's planner adjudication note). M4-G3 localized M4-G2's
proven scale dependence in ONE constant, `hazard_ridge`
(suica_core/m4_chart_ecology_estimator.py:341-342, deployed 0.005), but its
adaptive formula (`ridge_deployed * RAW_SCALE`, RAW_SCALE = mean raw retained
eigenvalue) is computed BEFORE whitening and is therefore c-INVARIANT by
construction -- identical absolute value at every c -- while the quantity the
ridge regularizes lives AFTER whitening and scales with c. Lean (b), built
precisely to certify a genuine repair, MISSED decisively: recovery was an
inverted-U across c, peaking exactly at c=1 (the formula's own, unstated,
calibration point). Does a ridge keyed to a POST-whitening scale statistic --
one that scales with c BY CONSTRUCTION -- deliver c-invariant recovery
without losing the gain?

===========================================================================
PART 0 -- REGISTERED CANDIDATE STATISTICS, ALPHA CALIBRATION RULE, AND
SPECIFICITY CONTROL (frozen BEFORE any truth-recovery compute; the diagnostic
numbers cited below -- raw_scale range, sample sizes -- are read from M4-G3's
ALREADY-persisted `context_meta.csv`, not a hypothesis-relevant number for
THIS leg's leans).
===========================================================================

--- What "the whitened quantity the ridge is actually added to" is ----------

`_bases_from_whitening(context, ingredients, whitening)` builds, per role,
`whitened = (raw - center) @ whitening`, then `bases[role] =
column_stack([ones, whitened])`. `whitening = c * whitening0` (G2's own
`_whitening_for_c`) is a SCALAR multiple of the deployed (c=1) whitening
matrix, so algebraically, for fixed (raw, center, whitening0):

    whitened_c = (raw - center) @ (c * whitening0) = c * whitened_1        (*)

-- an EXACT identity (up to floating point), not an approximation: going from
c=1 to c=c' is a literal UNIFORM SCALAR rescale of every non-intercept basis
column. `hazard_ridge` enters as `penalty = ridge*n*I`, added directly to
`design.T @ diag(weight) @ design`, whose "condition_*"/"feedback_*" blocks
are built from these same whitened columns (`_hazard_design`,
estimator.py:287-330). A statistic "computed on the whitened quantity the
ridge is actually added to" is therefore a statistic of `whitened_c` itself
(or of a design block built from it) -- NOT of the raw, pre-whitening
eigenvalues M4-G3's `RAW_SCALE` used.

--- Registered candidate statistics (S1, S2) ---------------------------------

Both computed from `basis = leg10._bases_from_whitening(context, ingredients,
g2._whitening_for_c(ingredients, c))` (UNCHANGED; deployed intercept; this
leg's arms never touch A6), dropping the intercept column (index 0):

    S1 "var" (centered, the direct post-whitening analogue of RAW_SCALE --
        RAW_SCALE was the mean EIGENVALUE, i.e. the mean per-direction
        VARIANCE, of the raw centered features; S1 is the same construction
        applied to the WHITENED output instead of the raw input):
        POST_SCALE_VAR(context, c) := mean over the 3 roles and all
        non-intercept columns j of Var_over_categories(whitened_c[:, j])
        (ddof=1, matching `_freeze_ingredients`'s own covariance convention).

    S2 "msq" (uncentered, the more literal reading of "the quantity summed
        into the Gram matrix diagonal that ridge is added to" -- that
        diagonal entry is literally `sum_i weight_i * design[i,j]^2`, an
        UNCENTERED second moment, not a variance about the sample mean;
        `center` is built once from a separate prototypes panel, so a given
        role's own `raw - center` need not be zero-mean, and S1/S2 can
        genuinely differ, not merely by a constant factor):
        POST_SCALE_MSQ(context, c) := mean over the 3 roles and all
        non-intercept columns j of Mean_over_categories(whitened_c[:, j]^2).

By identity (*), both are EXACT, algebraic, homogeneous-degree-2 functions of
c: POST_SCALE_k(context, c) = c^2 * POST_SCALE_k(context, 1) for k in
{var, msq}, for every context, not merely on average -- this is what makes
them genuinely COVARIANT (move with c by construction), in direct contrast to
RAW_SCALE, which is IDENTICAL at every c by construction (upstream of
whitening entirely).

--- Alpha calibration rule (registered; NOT tuned on outcomes) --------------

    ridge_covariant_k(context, c) := alpha_k * POST_SCALE_k(context, c)
    alpha_k := hazard_ridge_deployed / MEAN_across_all_64_(world,rep)_contexts(
                   POST_SCALE_k(context, c=1.0) )

-- a single GLOBAL scalar alpha_k (not per-context), computed ONCE from a
dedicated `--stage calibrate` pass over all 64 contexts at c=1 (deployed
intercept basis; no IRLS fit, no truth-recovery number is touched), exactly
mirroring M4-G3's OWN A1 formula structure (a single global multiplier times
a per-context statistic) but with alpha REDERIVED for POST_SCALE's own units
(POST_SCALE sits near unit scale -- G3's own Part 0 empirical check found
whitened-column variance "close to the UNIT variance whitening is
mathematically defined to produce" -- so alpha_k is expected, a priori, to
land close to `hazard_ridge_deployed` itself, NOT close to RAW_SCALE's own
~0.05-0.13 range). This literally implements the registration's own named
example ("matching the deployed ridge at c=1"): by construction,
MEAN_across_contexts(ridge_covariant_k(context, 1.0)) == hazard_ridge_deployed
exactly.

REGISTERED AMBIGUITY, both readings given (per the outer task's own
instruction to disclose, not silently pick). "Matching the deployed ridge at
c=1" could instead mean PER-CONTEXT exact matching (alpha_context :=
hazard_ridge_deployed / POST_SCALE_k(context, 1)). By identity (*) this
COLLAPSES, algebraically and exactly, to
    ridge_covariant(context, c) = alpha_context * POST_SCALE_k(context, c)
                                 = hazard_ridge_deployed * c^2
-- a UNIVERSAL, CONTEXT-FREE, STATISTIC-FREE formula, identical for S1 and S2
alike. This is a clean, disclosed mathematical fact (worth recording in its
own right: the "choose a statistic" question is only substantive under GLOBAL
calibration), but it would make testing "candidate statistics" (plural, as
registered) vacuous -- S1 and S2 would produce IDENTICAL numbers. The GLOBAL
reading is ADOPTED for exactly this reason (preserves genuine, testable
cross-context variation between S1 and S2) and because it is the literal
structural analogue of M4-G3's own A1 (one global multiplier, not a
per-context-recalibrated one). The per-context-calibration limit
(`hazard_ridge_deployed * c^2`, context-free) is reported in the calibration
artifact as a disclosed reference point, not as a scored arm (it is not "a
statistic computed on the whitened quantity" in the registration's own
words -- it is a pure function of c with no data dependence at all).

--- Pre-registered mechanistic prediction (disclosed before compute, not a
    tuned result; mirrors G3's own "Direction check" precedent) -------------

For the model=="base" route (intercept + condition_* columns only, no
feedback/gate cross-terms; see estimator._hazard_names), identity (*) plus
GLOBAL alpha calibration means: a diagonal covariate rescale by scalar c,
compensated by a ridge exactly proportional to c^2, reproduces the SAME
fitted coefficients (mapped through beta_c = beta_1/c) at every c -- because
substituting X_c = c*X_1, beta_c = beta_1/c into the penalized loss gives
`L(X_1,beta_1) + [ridge_used(c)/c^2]*n*||beta_1||^2`, and ridge_used(c)/c^2 is
EXACTLY alpha_k*POST_SCALE_k(context,1) = a c-INDEPENDENT constant under this
construction. So lean (a) (c-invariance) has a genuine, provable-not-merely-
hoped-for mechanism behind it, for the base route. BUT: (i) alpha is
calibrated GLOBALLY, not per-context, so exact invariance holds only up to
how much POST_SCALE_k(context,1) itself varies context-to-context around the
global mean (a real, disclosed, non-tunable design cost, not a tuned
rescue); (ii) for "return"/"feedback"/"gate" routes, `_hazard_design` also
builds columns from `rows["generated"]`/`rows["duration"]` (raw world data,
NEVER touched by c) and from `basis[:,0]` (the UNSCALED intercept sub-column)
crossed with `response_next` (the `feedback_0_d`/`gate_0_d` sub-block) --
these do NOT satisfy identity (*) and are NOT compensated by a c^2 ridge, so
EXACT invariance is a base-route-only guarantee; for other routes this is an
open empirical question, not a foregone conclusion, and is disclosed as such
BEFORE compute. (iii) Because alpha is calibrated to reproduce
`hazard_ridge_deployed` (0.005) AT c=1 -- not `g3_raw_scale`'s own much
WEAKER value at c=1 (0.00023-0.00089, G3's own Part 0) -- the invariant level
this construction settles on, if (i)/(ii) hold well enough, is expected to
resemble BASELINE's OWN (weaker-regularization-free, worse) c=1 performance,
not `g3_raw_scale`'s BETTER c=1 performance. So the a priori expectation
registered here is: lean (a) plausibly HOLDS (a genuine, mechanistically
grounded repair of the INVARIANCE property), lean (b) ("no loss vs
`g3_raw_scale`") is at material risk of MISSING for exactly this reason --
NOT because covariance failed, but because the registered calibration anchor
(deployed, not `g3_raw_scale`) targets a different level than the one that
achieved the gain. Both directions are reported faithfully below regardless
of whether this prediction is confirmed.

--- Specificity control: which INERT constant, and why ----------------------

M4-G3 found FOUR constants cleanly, adequately-powered INERT at both grains:
`tolerance`, `weight_floor`, `clip_bound`, `probe_epsilon` (`intercept` was
INERT at world-grain only, with a small real author-grain negative -- not
"cleanly" inert, excluded). `tolerance`'s adaptive form was a MODE SWITCH
(absolute to relative stopping rule), not a multiplicative "value = alpha *
stat" form, so "the same covariant rule" does not apply to it -- excluded.
Of the remaining three multiplicative candidates, `clip_bound` and
`probe_epsilon` are REJECTED for this leg's specificity control despite
being valid M4-G3 nulls, for a registered, pre-compute reason: applying THIS
leg's covariant rule to them is not obviously safe at c=0.25 (where
POST_SCALE shrinks by 16x). `clip_bound`'s deployed value (20.0) is
generously loose; a covariant clip at c=4 only gets LOOSER (safe), but at
c=0.25 a covariant clip could plausibly TIGHTEN to O(1) on the logit scale --
no longer obviously a no-op, risking a genuinely LIVE (not spuriously live)
channel that would confound the specificity story. `probe_epsilon`
(deployed 0.05) is a finite-difference STEP size; a covariant epsilon at c=4
could grow to O(1), large enough to threaten the small-step approximation
itself -- again a plausible genuine channel, not merely a control question.
`weight_floor` (deployed 1e-4) has neither risk: `fitted*(1-fitted)` is
bounded in [0, 0.25] regardless of design scale (the sigmoid saturates any
c), so covariant floor values across the WHOLE tested ladder (from
~alpha_floor*(0.25)^2*POST_SCALE(1) to ~alpha_floor*16*POST_SCALE(1), i.e.
roughly 6e-6 to 2e-3 given POST_SCALE(1) is near unit scale) stay far below
where the floor could plausibly bind (would need `fitted` within that same
tiny distance of exactly 0 or 1). `weight_floor` is therefore the specificity
control adopted: `floor_covariant(context, c) = alpha_floor *
POST_SCALE_VAR(context, c)`, `alpha_floor := DEPLOYED_WEIGHT_FLOOR /
MEAN_across_contexts(POST_SCALE_VAR(context, 1.0))` (reuses S1; registered
choice, not re-derived separately). `hazard_ridge` and every other constant
stay at DEPLOYED values in this arm -- the ONLY manipulation is applying the
covariant treatment to a constant M4-G3 already showed does not drive
recovery.

===========================================================================
DESIGN (registered)
===========================================================================
Reuse M4-G3's 8 worlds (`g3.D1_WORLDS`, identical to `g2.D1_WORLDS`) and
objective path verbatim. THE REGISTERED ANALYSIS GRAIN IS THE AUTHOR GRAIN
(n up to 745, after M4-G2's valid-6-world subset and degenerate-reference
exclusion, reused verbatim) per the fifth standing rule; world-grain numbers
are a disclosed companion only and adjudicate nothing.

Five arms, each conceptually defined across c in {0.25, 1.0, 4.0}:
  baseline               -- deployed ridge/floor/etc, c=1 only (anchor).
  g3_raw_scale            -- M4-G3's `adaptive_hazard_ridge` formula
                             (ridge = hazard_ridge_deployed * RAW_SCALE,
                             c-independent by construction), computed fresh
                             at c=1 only (anchor + lean (b) reference point);
                             its OWN c=0.25/4.0 values are NOT recomputed --
                             M4-G3 already computed and persisted them
                             (`partial_winner_ladder_*_adaptive_hazard_ridge.csv`,
                             all 8 worlds) and they are reused verbatim for
                             the descriptive per-arm table only (no new
                             compute; NOT independently re-verified at those
                             c-values by this leg -- only c=1.0 is anchored,
                             see G1 ANCHOR; an earlier draft attempted an
                             0.25/4.0 anchor too and correctly failed with a
                             0-row join, exactly the consequence of this
                             scope reduction, disclosed in the report).
  covariant_var           -- ridge = alpha_var * POST_SCALE_VAR(context, c);
                             c in {0.25, 1.0, 4.0}, full new compute.
  covariant_msq            -- ridge = alpha_msq * POST_SCALE_MSQ(context, c);
                             c in {0.25, 1.0, 4.0}, full new compute.
  specificity_weight_floor -- weight_floor covariant (see above), ridge
                             deployed; c in {0.25, 1.0, 4.0}, full new
                             compute.

`baseline` and `g3_raw_scale` are computed ONLY at c=1 in this leg's own new
compute (their other c-values are either identical to already-published
numbers -- baseline@c=4 IS G3's `c4_reference`, baseline@c=0.25 IS G2's
`c_0.25` -- or, for g3_raw_scale, already persisted by G3 itself); no lean
in this registration needs them elsewhere, since lean (b) compares AT c=1
only. This is a disclosed compute-scope reduction from the registration's
literal "each arm evaluated across c", justified because it would otherwise
re-derive numbers this line has already published and gated, at real
compute cost, without touching any of this leg's own leans.

No OFFSET/GPA stage: unlike M4-G1/G2/G3, this registration's own lean (c) is
SPECIFICITY (not a cosmetic-offset-trade check), and no gate here references
`offset_norm` -- M4-G3 already established (structurally, not by assumption)
that none of the constants this leg touches (`hazard_ridge`, `weight_floor`)
reach `_bases_from_whitening` at all, so offset is identical to baseline's
for every arm here by the same call-graph argument, without needing to
recompute it.

Chunked execution (this arc's standard workaround): `--stage calibrate`
(no `--world`, processes all 8 worlds in one pass -- cheap, no IRLS fit,
needed once, before any arm's truth recovery can be resolved) ->
`--stage truth --world W` (one world's full arm x c x budget sweep) ->
`--assemble` (reads every partial, cross-checks completeness, adjudicates).
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
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
import run_suica_m4_g3_scale_adaptive as g3  # noqa: E402  the leg this extends

from suica_core.m4_chart_ecology_generator import M4ChartEcologySpec  # noqa: E402

ROLES = leg11.ROLES
FLIP_TOLERANCE = leg4.FLIP_TOLERANCE
D1_WORLDS = g3.D1_WORLDS
VALID_TRUTH_WORLDS = g3.VALID_TRUTH_WORLDS
TRUTH_VALIDITY_THRESHOLD = g3.TRUTH_VALIDITY_THRESHOLD
TRUTH_BUDGETS = g3.TRUTH_BUDGETS
C_LADDER = (0.25, 1.0, 4.0)

DEPLOYED_WEIGHT_FLOOR = g3.DEPLOYED_WEIGHT_FLOOR
DEPLOYED_CLIP_BOUND = g3.DEPLOYED_CLIP_BOUND
DEPLOYED_TOL_VALUE = g3.DEPLOYED_TOL_VALUE
DEPLOYED_PROBE_EPSILON = g3.DEPLOYED_PROBE_EPSILON

MY_ARM_NAMES = ("baseline", "g3_raw_scale", "covariant_var", "covariant_msq", "specificity_weight_floor")
NEW_COMPUTE_ARMS = ("covariant_var", "covariant_msq", "specificity_weight_floor")  # all 3 c's
ANCHOR_ONLY_ARMS = ("baseline", "g3_raw_scale")  # c=1 only, new compute

# g3._truth_rows_for_context reads a module-level ARM_C[arm] -> c lookup that
# it does not take as a parameter; this leg's arms are evaluated at MULTIPLE
# c per arm name (unlike g3's own fixed one-c-per-arm-name design), so we
# mutate g3.ARM_C immediately before each call, disclosed here as the reuse
# mechanism. Safe: single sequential process per invocation, never read
# concurrently.
for _arm in MY_ARM_NAMES:
    g3.ARM_C.setdefault(_arm, 1.0)

G1_ANCHOR_TOLERANCE = 1e-12
G3_TOLERANCE = 1e-12
LEAN_A_MARGIN = 0.02   # c-invariance, reused from this line's own convention (G1/G2/G3 leans)
LEAN_B_MARGIN = 0.02   # "no loss", one-sided reading of the same convention (see Part 0 margin note below)
G0_FRACTION_BAR = 0.01  # half of LEAN_A_MARGIN/LEAN_B_MARGIN, matching this line's own
                        # "half of my own leaning bar" convention (G1: half of 25%,
                        # G2: half the slope gap, G3: half of 50%)


# ---------------------------------------------------------------------------
# Part 0 statistics
# ---------------------------------------------------------------------------


def _post_scale_stats(context: dict[str, Any], ingredients: dict[str, Any], c: float) -> tuple[float, float]:
    """S1 (var) and S2 (msq), both computed on the deployed-intercept basis at
    this c -- see Part 0. `leg10._bases_from_whitening` is UNCHANGED."""
    whitening = g2._whitening_for_c(ingredients, c)
    basis = leg10._bases_from_whitening(context, ingredients, whitening)  # unchanged
    variances = []
    msqs = []
    for role in ROLES:
        whitened = basis[role][:, 1:]  # drop the intercept column
        if whitened.shape[0] < 2:
            raise RuntimeError(f"role {role} has <2 categories; variance undefined")
        variances.append(np.var(whitened, axis=0, ddof=1))
        msqs.append(np.mean(whitened**2, axis=0))
    var_stat = float(np.mean(np.concatenate(variances)))
    msq_stat = float(np.mean(np.concatenate(msqs)))
    return var_stat, msq_stat, basis


def _resolve_params(
    arm: str,
    deployed_ridge: float,
    raw_scale: float,
    post_scale_var: float,
    post_scale_msq: float,
    alpha: dict[str, float],
) -> dict[str, Any]:
    ridge = deployed_ridge
    weight_floor = DEPLOYED_WEIGHT_FLOOR
    if arm == "baseline":
        pass
    elif arm == "g3_raw_scale":
        ridge = deployed_ridge * raw_scale  # G3's own A1 formula, verbatim
    elif arm == "covariant_var":
        ridge = alpha["var"] * post_scale_var
    elif arm == "covariant_msq":
        ridge = alpha["msq"] * post_scale_msq
    elif arm == "specificity_weight_floor":
        weight_floor = alpha["floor"] * post_scale_var  # reuses S1, registered choice
    else:
        raise ValueError(f"unknown arm: {arm}")
    return {
        "ridge": float(ridge),
        "weight_floor": float(weight_floor),
        "clip_bound": float(DEPLOYED_CLIP_BOUND),
        "tol_mode": "absolute",
        "tol_value": float(DEPLOYED_TOL_VALUE),
        "probe_epsilon": float(DEPLOYED_PROBE_EPSILON),
    }


# ---------------------------------------------------------------------------
# stage: calibrate (all 8 worlds, single pass, no IRLS fit)
# ---------------------------------------------------------------------------


def _run_calibrate(config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    rows: list[dict[str, Any]] = []
    for world in D1_WORLDS:
        contexts = g1._build_world_contexts(world, config, spec)
        for rep_idx, context in enumerate(contexts):
            ingredients = leg10._freeze_ingredients(context)
            raw_scale = float(np.mean(ingredients["eigenvalues"][ingredients["retained"]]))
            deployed_ridge = float(context["fit_kwargs"]["hazard_ridge"])
            var_stat, msq_stat, _ = _post_scale_stats(context, ingredients, 1.0)
            rows.append(
                {
                    "world": world,
                    "repetition": rep_idx,
                    "raw_scale": raw_scale,
                    "deployed_ridge": deployed_ridge,
                    "post_scale_var_c1": var_stat,
                    "post_scale_msq_c1": msq_stat,
                    "k_retained": int(len(ingredients["retained"])),
                }
            )
        print(f"[m4g4] calibrate {world} done", flush=True)

    df = pd.DataFrame(rows)
    output.mkdir(parents=True, exist_ok=True)
    df.to_csv(output / "calibration_context_rows.csv", index=False)

    deployed_ridge_values = df["deployed_ridge"].unique()
    if len(deployed_ridge_values) != 1:
        raise RuntimeError(f"deployed ridge not constant across contexts: {deployed_ridge_values}")
    deployed_ridge = float(deployed_ridge_values[0])

    mean_var = float(df["post_scale_var_c1"].mean())
    mean_msq = float(df["post_scale_msq_c1"].mean())
    median_var = float(df["post_scale_var_c1"].median())
    median_msq = float(df["post_scale_msq_c1"].median())
    mean_of_ratios_var = float((deployed_ridge / df["post_scale_var_c1"]).mean())
    mean_of_ratios_msq = float((deployed_ridge / df["post_scale_msq_c1"]).mean())

    alpha_var = deployed_ridge / mean_var
    alpha_msq = deployed_ridge / mean_msq
    alpha_floor = DEPLOYED_WEIGHT_FLOOR / mean_var

    calibration = {
        "n_contexts": int(len(df)),
        "deployed_ridge": deployed_ridge,
        "deployed_weight_floor": DEPLOYED_WEIGHT_FLOOR,
        "mean_post_scale_var_c1": mean_var,
        "mean_post_scale_msq_c1": mean_msq,
        "median_post_scale_var_c1_disclosed_not_adopted": median_var,
        "median_post_scale_msq_c1_disclosed_not_adopted": median_msq,
        "alpha_var": alpha_var,
        "alpha_msq": alpha_msq,
        "alpha_floor": alpha_floor,
        "alpha_var_mean_of_ratios_reading_disclosed_not_adopted": mean_of_ratios_var,
        "alpha_msq_mean_of_ratios_reading_disclosed_not_adopted": mean_of_ratios_msq,
        "per_context_calibration_limit_disclosed_not_scored": {
            "formula": "ridge_used(c) = deployed_ridge * c^2, context-free (see Part 0)",
            "values_by_c": {str(c): deployed_ridge * c * c for c in C_LADDER},
        },
        "calibration_rule": (
            "alpha_k = deployed_constant / MEAN_across_64_contexts(post_scale_k at c=1); "
            "registered ratio-of-means (population-mean) reading, ADOPTED. "
            "mean-of-per-context-ratios is a disclosed alternative, NOT adopted "
            "(see Part 0 for the reasoning)."
        ),
    }
    with (output / "calibration.json").open("w", encoding="utf-8") as handle:
        json.dump(calibration, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(calibration, indent=2, sort_keys=True), flush=True)


# ---------------------------------------------------------------------------
# G3-style truth-path invariance spot check, generalized over this leg's
# arms x c ladder (disclosed near-duplicate of g3._run_truth_stage's own
# inline G3 block, generalized -- g3's own version is arm-c-fused via ARM_C
# and cannot be called generically without the same mutation this file
# already relies on elsewhere).
# ---------------------------------------------------------------------------


def _g3_spot_check(world: str, contexts: list[dict[str, Any]], calibration: dict[str, Any]) -> list[dict[str, Any]]:
    dims = contexts[0]["flat"][("train", 0)][0]["response_next"].shape[1]
    rep_idx = view = author = context = stack = None
    for candidate_rep_idx, candidate_context in enumerate(contexts):
        found = False
        for candidate_view in ("train", "test"):
            for candidate_author in range(candidate_context["authors"]):
                candidate_stack = candidate_context["oracle_stacks"][candidate_view][candidate_author]
                if float(np.linalg.norm(candidate_stack["D"])) >= FLIP_TOLERANCE:
                    rep_idx, view, author, context, stack = (
                        candidate_rep_idx,
                        candidate_view,
                        candidate_author,
                        candidate_context,
                        candidate_stack,
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
    raw_scale = float(np.mean(ingredients["eigenvalues"][ingredients["retained"]]))
    deployed_ridge = float(fit_kwargs["hazard_ridge"])
    alpha = {"var": calibration["alpha_var"], "msq": calibration["alpha_msq"], "floor": calibration["alpha_floor"]}

    rows: list[dict[str, Any]] = []
    for c in C_LADDER:
        var_stat, msq_stat, basis = _post_scale_stats(context, ingredients, c)
        arms_here = MY_ARM_NAMES if c == 1.0 else NEW_COMPUTE_ARMS
        for arm in arms_here:
            params = _resolve_params(arm, deployed_ridge, raw_scale, var_stat, msq_stat, alpha)
            d_gapstyle = g3._forced_route_derivative_adaptive(
                calibration_flat, selection_flat, basis, model=route,
                hazard_ridge=params["ridge"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
                weight_floor=params["weight_floor"], clip_bound=params["clip_bound"],
                tol_mode=params["tol_mode"], tol_value=params["tol_value"], probe_epsilon=params["probe_epsilon"],
            )
            e_gapstyle = leg3._relative_error(d_gapstyle, d_true)
            d_truthpath = g3._forced_route_derivative_adaptive(
                calibration_g3, selection_g3, basis, model=route,
                hazard_ridge=params["ridge"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
                weight_floor=params["weight_floor"], clip_bound=params["clip_bound"],
                tol_mode=params["tol_mode"], tol_value=params["tol_value"], probe_epsilon=params["probe_epsilon"],
            )
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
# stage: truth (per world)
# ---------------------------------------------------------------------------


def _run_truth_stage(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, calibration: dict[str, Any], output: Path) -> None:
    contexts = g1._build_world_contexts(world, config, spec)
    alpha = {"var": calibration["alpha_var"], "msq": calibration["alpha_msq"], "floor": calibration["alpha_floor"]}

    g3_rows = _g3_spot_check(world, contexts, calibration)
    g3_max = max(row["abs_diff"] for row in g3_rows)
    if g3_max > G3_TOLERANCE:
        raise RuntimeError(f"G3 truth-path invariance fails on {world}: {g3_max:.3e}")

    all_rows: list[dict[str, Any]] = []
    per_rep_meta: list[dict[str, Any]] = []
    truth_gates: list[dict[str, Any]] = []
    for rep_idx, context in enumerate(contexts):
        ingredients = leg10._freeze_ingredients(context)
        raw_scale = float(np.mean(ingredients["eigenvalues"][ingredients["retained"]]))
        deployed_ridge = float(context["fit_kwargs"]["hazard_ridge"])
        rep_meta: dict[str, Any] = {
            "world": world,
            "repetition": rep_idx,
            "raw_scale": raw_scale,
            "deployed_ridge": deployed_ridge,
            "k_retained": int(len(ingredients["retained"])),
        }
        for c in C_LADDER:
            var_stat, msq_stat, basis = _post_scale_stats(context, ingredients, c)
            rep_meta[f"post_scale_var_c{c:g}"] = var_stat
            rep_meta[f"post_scale_msq_c{c:g}"] = msq_stat
            arms_here = MY_ARM_NAMES if c == 1.0 else NEW_COMPUTE_ARMS
            arm_bases_rep = {arm: basis for arm in arms_here}
            resolved_rep: dict[str, dict[str, Any]] = {}
            for arm in arms_here:
                params = _resolve_params(arm, deployed_ridge, raw_scale, var_stat, msq_stat, alpha)
                resolved_rep[arm] = params
                rep_meta[f"ridge_{arm}_c{c:g}"] = params["ridge"]
                rep_meta[f"weight_floor_{arm}_c{c:g}"] = params["weight_floor"]
                g3.ARM_C[arm] = c  # mutate before call; see module-level note
            for budget in TRUTH_BUDGETS:
                started = time.time()
                rows, gate = g3._truth_rows_for_context(
                    context, arm_bases_rep, resolved_rep, spec, budget, arms=tuple(arms_here)
                )
                for row in rows:
                    if row["c"] != c:
                        raise RuntimeError(f"ARM_C mutation mismatch: expected {c}, row={row}")
                all_rows.extend(rows)
                truth_gates.append(gate)
                print(
                    f"[m4g4] truth c={c:g} b={budget:g} {world} rep={rep_idx} "
                    f"arms={arms_here} ({time.time()-started:.1f}s)",
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
    print(f"[m4g4] truth stage done: {world}", flush=True)


# ---------------------------------------------------------------------------
# assemble + adjudicate
# ---------------------------------------------------------------------------


def _author_level_truth_with_c(truth_rows: pd.DataFrame) -> pd.DataFrame:
    """Disclosed near-duplicate of g1._author_level_truth, extended with a
    `c` groupby key: this leg's arms are evaluated across multiple c values
    under the SAME arm name (unlike G1/G2/G3, where c was baked into the arm
    identity itself)."""
    usable = truth_rows[~truth_rows["degenerate_reference"]]
    return (
        usable.groupby(["world", "repetition", "author", "arm", "c", "budget"])[["e_arm_true", "e_orc_true"]]
        .mean()
        .reset_index()
    )


def _world_level_median(author_truth: pd.DataFrame, arm: str, c: float, budget: float, worlds: list[str]) -> pd.Series:
    scoped = author_truth[(author_truth["arm"] == arm) & (author_truth["c"] == c) & (author_truth["budget"] == budget)]
    return scoped.groupby("world")["e_arm_true"].median().reindex(worlds)


def _paired_world_diff_ci(author_truth, arm_lo, c_lo, arm_hi, c_hi, budget, worlds):
    lo = _world_level_median(author_truth, arm_lo, c_lo, budget, worlds)
    hi = _world_level_median(author_truth, arm_hi, c_hi, budget, worlds)
    diffs = (lo - hi).to_numpy()
    return g1._paired_world_ci(diffs)


def _paired_author_diff_ci(author_truth, arm_lo, c_lo, arm_hi, c_hi, budget, worlds):
    scoped = author_truth[(author_truth["budget"] == budget) & (author_truth["world"].isin(worlds))]
    lo_rows = scoped[(scoped["arm"] == arm_lo) & (scoped["c"] == c_lo)].set_index(["world", "repetition", "author"])
    hi_rows = scoped[(scoped["arm"] == arm_hi) & (scoped["c"] == c_hi)].set_index(["world", "repetition", "author"])
    joined = lo_rows.join(hi_rows, lsuffix="_lo", rsuffix="_hi", how="inner")
    diffs = (joined["e_arm_true_lo"] - joined["e_arm_true_hi"]).to_numpy()
    return g1._paired_author_ci(diffs)


def _classify_pair(ci: dict[str, float], margin: float, one_sided: bool) -> str:
    if ci["n"] <= 1 or not np.isfinite(ci["ci_lo"]) or not np.isfinite(ci["ci_hi"]):
        return "AMBIGUOUS"
    if one_sided:
        if ci["ci_hi"] <= margin:
            return "WITHIN"
        if ci["ci_lo"] > margin:
            return "OUTSIDE"
        return "AMBIGUOUS"
    if ci["ci_lo"] >= -margin and ci["ci_hi"] <= margin:
        return "WITHIN"
    if ci["ci_lo"] > margin or ci["ci_hi"] < -margin:
        return "OUTSIDE"
    return "AMBIGUOUS"


def _arm_status_from_pairs(pair_classes: list[str]) -> str:
    if all(p == "WITHIN" for p in pair_classes):
        return "HOLD"
    if any(p == "OUTSIDE" for p in pair_classes):
        return "MISS"
    return "UNDERPOWERED"


def _c_invariance_check(author_truth: pd.DataFrame, arm: str, worlds: list[str]) -> dict[str, Any]:
    rows = []
    for budget in TRUTH_BUDGETS:
        for c_lo, c_hi in itertools.combinations(C_LADDER, 2):
            author_ci = _paired_author_diff_ci(author_truth, arm, c_lo, arm, c_hi, budget, worlds)
            world_ci = _paired_world_diff_ci(author_truth, arm, c_lo, arm, c_hi, budget, worlds)
            author_class = _classify_pair(author_ci, LEAN_A_MARGIN, one_sided=False)
            underpowered_author = bool(author_ci["n"] > 1 and author_ci["half_width"] > G0_FRACTION_BAR)
            rows.append(
                {
                    "arm": arm, "budget": budget, "c_lo": c_lo, "c_hi": c_hi,
                    "author_n": author_ci["n"], "author_mean_diff": author_ci["mean"],
                    "author_ci_lo": author_ci["ci_lo"], "author_ci_hi": author_ci["ci_hi"],
                    "author_half_width": author_ci["half_width"], "author_class": author_class,
                    "author_underpowered_vs_g0_bar": underpowered_author,
                    "world_n": world_ci["n"], "world_mean_diff": world_ci["mean"],
                    "world_ci_lo": world_ci["ci_lo"], "world_ci_hi": world_ci["ci_hi"],
                }
            )
    status = _arm_status_from_pairs([r["author_class"] for r in rows])
    return {"arm": arm, "rows": rows, "status": status, "held": bool(status == "HOLD")}


def _no_loss_check(author_truth: pd.DataFrame, arm: str, worlds: list[str]) -> dict[str, Any]:
    rows = []
    for budget in TRUTH_BUDGETS:
        author_ci = _paired_author_diff_ci(author_truth, arm, 1.0, "g3_raw_scale", 1.0, budget, worlds)
        world_ci = _paired_world_diff_ci(author_truth, arm, 1.0, "g3_raw_scale", 1.0, budget, worlds)
        author_class = _classify_pair(author_ci, LEAN_B_MARGIN, one_sided=True)
        underpowered_author = bool(author_ci["n"] > 1 and author_ci["half_width"] > G0_FRACTION_BAR)
        rows.append(
            {
                "arm": arm, "budget": budget,
                "author_n": author_ci["n"], "author_mean_diff_candidate_minus_g3raw": author_ci["mean"],
                "author_ci_lo": author_ci["ci_lo"], "author_ci_hi": author_ci["ci_hi"],
                "author_half_width": author_ci["half_width"], "author_class": author_class,
                "author_underpowered_vs_g0_bar": underpowered_author,
                "world_n": world_ci["n"], "world_mean_diff": world_ci["mean"],
                "world_ci_lo": world_ci["ci_lo"], "world_ci_hi": world_ci["ci_hi"],
            }
        )
    status = _arm_status_from_pairs([r["author_class"] for r in rows])
    return {"arm": arm, "rows": rows, "status": status, "held": bool(status == "HOLD")}


def _assemble(output: Path) -> None:
    worlds = list(D1_WORLDS)
    valid_worlds = list(VALID_TRUTH_WORLDS)

    with (output / "calibration.json").open("r", encoding="utf-8") as handle:
        calibration = json.load(handle)

    truth_frames = [pd.read_csv(output / f"partial_truth_{w}.csv") for w in worlds]
    truth_rows = pd.concat(truth_frames, ignore_index=True)
    g3check_frames = [pd.read_csv(output / f"partial_g3check_{w}.csv") for w in worlds]
    g3check_rows = pd.concat(g3check_frames, ignore_index=True)
    meta_frames = [pd.read_csv(output / f"partial_context_meta_{w}.csv") for w in worlds]
    context_meta = pd.concat(meta_frames, ignore_index=True)

    expected_truth_rows = 0
    for c in C_LADDER:
        n_arms = len(MY_ARM_NAMES) if c == 1.0 else len(NEW_COMPUTE_ARMS)
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

    # ---- numerical-validity diagnostic: recompute valid-6-world subset from
    # this leg's own arm-invariant e_orc_true (baseline arm carries it, deployed) -
    orc_rows = []
    for budget in TRUTH_BUDGETS:
        scoped = truth_rows[
            (truth_rows["budget"] == budget) & (~truth_rows["degenerate_reference"]) & (truth_rows["arm"] == "baseline")
        ]
        for w in worlds:
            median_e_orc = float(scoped[scoped["world"] == w]["e_orc_true"].median())
            orc_rows.append({"world": w, "budget": budget, "median_e_orc_true": median_e_orc})
    orc_diag = pd.DataFrame(orc_rows)
    worst_per_world = orc_diag.groupby("world")["median_e_orc_true"].max()
    recomputed_valid_worlds = sorted(worst_per_world[worst_per_world <= TRUTH_VALIDITY_THRESHOLD].index.tolist())
    valid_world_subset_reproduced = recomputed_valid_worlds == sorted(VALID_TRUTH_WORLDS)

    # ---- G1 ANCHOR: baseline@c=1, g3_raw_scale@c=1 vs M4-G3 persisted --------
    # (g3_raw_scale is, by this leg's own registered compute-scope reduction,
    # NEVER computed away from c=1 in this leg's new compute -- see Design in
    # the docstring -- so no independent anchor check is possible at c=0.25/4.0;
    # a mid-assembly bug attempted exactly that anchor against G3's own
    # persisted winner-ladder files and failed with a 0-row join, which is the
    # CORRECT/expected consequence of that scope reduction, not a data error;
    # removed here, disclosed in the report rather than silently dropped. The
    # descriptive per-arm table's g3_raw_scale@{0.25,4.0} entries are sourced
    # directly, unverified-by-this-leg, from M4-G3's own already-gated
    # persisted `partial_winner_ladder_*_adaptive_hazard_ridge.csv` files.)
    m4g3_truth = pd.read_csv(ROOT / "results" / "m4_g3_scale_adaptive" / "truth_recovery_rows.csv")
    anchor_rows = []
    for mine_arm, g3_arm in (("baseline", "baseline"), ("g3_raw_scale", "adaptive_hazard_ridge")):
        mine = truth_rows[(truth_rows["arm"] == mine_arm) & (truth_rows["c"] == 1.0)]
        theirs = m4g3_truth[(m4g3_truth["arm"] == g3_arm) & (m4g3_truth["c"] == 1.0)]
        joined = mine.merge(
            theirs, on=["world", "repetition", "view", "author", "budget"], suffixes=("_mine", "_theirs"), how="inner"
        )
        expected = len(worlds) * len(TRUTH_BUDGETS) * 8 * 2 * 16
        if len(joined) != expected:
            raise RuntimeError(f"G1 anchor join size {len(joined)} != expected {expected} for {mine_arm}")
        diff = (joined["e_arm_true_mine"] - joined["e_arm_true_theirs"]).abs()
        anchor_rows.append(
            {"arm": mine_arm, "g3_arm": g3_arm, "c": 1.0, "n_rows": int(len(joined)), "max_abs_diff": float(diff.max(skipna=True))}
        )
    g1_anchor_max = max(row["max_abs_diff"] for row in anchor_rows)
    g1_anchor = {"per_arm": anchor_rows, "max_abs_diff": g1_anchor_max, "tolerance": G1_ANCHOR_TOLERANCE,
                 "pass": bool(g1_anchor_max <= G1_ANCHOR_TOLERANCE),
                 "note": ("g3_raw_scale is independently anchored ONLY at c=1.0 (its only newly-computed "
                          "point in this leg); its c=0.25/4.0 descriptive-table values are read directly "
                          "from M4-G3's own persisted winner-ladder files, not independently re-verified here.")}

    author_truth = _author_level_truth_with_c(truth_rows)

    # ---- G0 POWER ------------------------------------------------------------
    m4g3_decision_path = ROOT / "results" / "m4_g3_scale_adaptive" / "decision.json"
    with m4g3_decision_path.open("r", encoding="utf-8") as handle:
        m4g3_decision = json.load(handle)
    g3_author_gain_by_budget = {}
    for row in m4g3_decision["gates"]["G0"]["per_budget"]:
        g3_author_gain_by_budget[row["budget"]] = row["author_level_gain"]

    g0_probe_rows = []
    for arm in ("covariant_var", "covariant_msq"):
        check = _c_invariance_check(author_truth, arm, valid_worlds)
        for r in check["rows"]:
            g0_probe_rows.append({**r, "check": "lean_a_c_invariance"})
    for arm in ("covariant_var", "covariant_msq"):
        check = _no_loss_check(author_truth, arm, valid_worlds)
        for r in check["rows"]:
            g0_probe_rows.append({**r, "check": "lean_b_no_loss"})
    specificity_check = _c_invariance_check(author_truth, "specificity_weight_floor", valid_worlds)
    for r in specificity_check["rows"]:
        g0_probe_rows.append({**r, "check": "lean_c_specificity"})
    g0_df = pd.DataFrame(g0_probe_rows)
    g0_underpowered_n = int(g0_df["author_underpowered_vs_g0_bar"].sum())
    g0 = {
        "statement": (
            "AUTHOR-grain (n up to 745) CI half-width vs bar=0.01 (half of this leg's own "
            "±0.02 leaning margin, this line's 'half of my own leaning bar' convention). "
            "Also reported: the SAME half-widths as a fraction of M4-G3's own persisted "
            "AUTHOR-level c=4 gain (0.0591@4x / 0.0683@8x) -- the registration's literal "
            "'against the c=4 gain' framing -- as a disclosed second reading; the ABSOLUTE "
            "±0.01 reading is ADOPTED because this leg's own leans (a)/(b) are themselves "
            "stated in absolute (not %-of-gain) terms, unlike M4-G3's lean (a)."
        ),
        "bar_absolute": G0_FRACTION_BAR,
        "m4g3_author_c4_gain_by_budget": g3_author_gain_by_budget,
        "n_comparisons": int(len(g0_df)),
        "n_underpowered_vs_absolute_bar": g0_underpowered_n,
        "half_width_min": float(g0_df["author_half_width"].min()),
        "half_width_max": float(g0_df["author_half_width"].max()),
        "half_width_median": float(g0_df["author_half_width"].median()),
        "half_width_as_fraction_of_g3_gain_min": float(
            (g0_df["author_half_width"] / g0_df["budget"].map(g3_author_gain_by_budget)).min()
        ),
        "half_width_as_fraction_of_g3_gain_max": float(
            (g0_df["author_half_width"] / g0_df["budget"].map(g3_author_gain_by_budget)).max()
        ),
        "all_comparisons": g0_probe_rows,
    }

    # ---- G2 COVARIANCE LIVENESS ----------------------------------------------
    g2_rows = []
    for arm, param_key in (("covariant_var", "ridge"), ("covariant_msq", "ridge"), ("specificity_weight_floor", "weight_floor")):
        vals = {}
        for c in C_LADDER:
            col = f"{param_key}_{arm}_c{c:g}"
            vals[c] = float(context_meta[col].mean())
        ratio_4_1 = vals[4.0] / vals[1.0] if vals[1.0] else float("nan")
        ratio_025_1 = vals[0.25] / vals[1.0] if vals[1.0] else float("nan")
        moves = bool(abs(ratio_4_1 - 1.0) > 0.10 and abs(ratio_025_1 - 1.0) > 0.10)  # not-inert threshold, disclosed
        g2_rows.append(
            {
                "arm": arm, "parameter": param_key,
                f"mean_c0.25": vals[0.25], f"mean_c1": vals[1.0], f"mean_c4": vals[4.0],
                "ratio_c4_over_c1": ratio_4_1, "ratio_c0.25_over_c1": ratio_025_1,
                "theoretical_ratio_c4_over_c1": 16.0, "theoretical_ratio_c0.25_over_c1": 0.0625,
                "status": "LIVE" if moves else "INERT",
            }
        )
    # contrast: g3_raw_scale's own ridge is analytically c-INVARIANT (RAW_SCALE
    # never touches c) -- reported here for direct comparison, no new compute needed.
    g2_rows.append(
        {
            "arm": "g3_raw_scale", "parameter": "ridge",
            "mean_c0.25": float(context_meta["ridge_g3_raw_scale_c1"].mean()),
            "mean_c1": float(context_meta["ridge_g3_raw_scale_c1"].mean()),
            "mean_c4": float(context_meta["ridge_g3_raw_scale_c1"].mean()),
            "ratio_c4_over_c1": 1.0, "ratio_c0.25_over_c1": 1.0,
            "theoretical_ratio_c4_over_c1": 1.0, "theoretical_ratio_c0.25_over_c1": 1.0,
            "status": "INERT (analytic, c-independent by construction, M4-G3's own finding)",
        }
    )
    g2_liveness = {"per_arm": g2_rows}

    # ---- leans -----------------------------------------------------------------
    lean_a_by_arm = {arm: _c_invariance_check(author_truth, arm, valid_worlds) for arm in ("covariant_var", "covariant_msq")}
    lean_a_held_arms = [arm for arm, chk in lean_a_by_arm.items() if chk["held"]]
    lean_a_any_held = bool(len(lean_a_held_arms) > 0)
    lean_a_any_underpowered = bool(any(chk["status"] == "UNDERPOWERED" for chk in lean_a_by_arm.values()))
    lean_a_all_clean_miss = bool(all(chk["status"] == "MISS" for chk in lean_a_by_arm.values()))

    # lean (b) is OFFICIALLY evaluated only for arms that held lean (a) (the
    # registration's "that arm's recovery at c=1"); computed here for BOTH
    # covariant arms regardless, as a disclosed, non-gating companion (cheap:
    # pure aggregation over already-computed rows, zero marginal compute).
    lean_b_by_arm_all = {arm: _no_loss_check(author_truth, arm, valid_worlds) for arm in ("covariant_var", "covariant_msq")}
    lean_b_by_arm = {arm: lean_b_by_arm_all[arm] for arm in lean_a_held_arms}

    lean_c_check = _c_invariance_check(author_truth, "specificity_weight_floor", valid_worlds)
    # lean (c) is CONFIRMED (specificity holds) iff the control does NOT achieve
    # c-invariance, i.e. its own status is MISS (a decisive non-invariance finding,
    # mirroring baseline's/G2's own established non-invariance) -- UNDERPOWERED
    # here would mean specificity is itself unresolved, not confirmed.
    lean_c_confirmed = bool(lean_c_check["status"] == "MISS")
    lean_c_unresolved = bool(lean_c_check["status"] == "UNDERPOWERED")

    if lean_a_any_held:
        pivot_status = "DOES_NOT_FIRE"
    elif lean_a_any_underpowered:
        pivot_status = "UNDERPOWERED"
    elif lean_a_all_clean_miss:
        pivot_status = "FIRES"
    else:
        pivot_status = "AMBIGUOUS"
    pivot_fires = bool(pivot_status == "FIRES")

    if lean_a_any_held and any(chk["held"] for chk in lean_b_by_arm.values()) and lean_c_confirmed:
        certified_arms = [arm for arm in lean_a_held_arms if lean_b_by_arm[arm]["held"]]
        verdict = "CERTIFIED_REPAIR"
    elif lean_a_any_held and not any(chk["held"] for chk in lean_b_by_arm.values()):
        certified_arms = []
        verdict = "COVARIANT_BUT_LOSSY"
    elif pivot_fires:
        certified_arms = []
        verdict = "PIVOT_SCALE_DEPENDENCE_NOT_A_SIMPLE_RIDGE_ISSUE"
    elif pivot_status == "UNDERPOWERED":
        certified_arms = []
        verdict = "UNDERPOWERED_NO_ADJUDICATION_AT_REGISTERED_GRAIN"
    else:
        certified_arms = []
        verdict = "AMBIGUOUS_NO_CLEAN_BRANCH"

    decision = {
        "estimand_id": "SUICA_M4_G4_COVARIANT_RIDGE",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md M4-G4 registration (2026-08-03, BEFORE run); ledger row M4-G4",
        "worlds": worlds,
        "valid_truth_worlds": valid_worlds,
        "arm_names": list(MY_ARM_NAMES),
        "c_ladder": list(C_LADDER),
        "truth_budgets": list(TRUTH_BUDGETS),
        "calibration": calibration,
        "gates": {
            "G0_power": g0,
            "G1_anchor": g1_anchor,
            "G2_covariance_liveness": g2_liveness,
            "G3_truth_path_invariance": g3_gate,
        },
        "structural_checks": {
            "recomputed_valid_worlds": recomputed_valid_worlds,
            "valid_world_subset_reproduced_from_m4g3": valid_world_subset_reproduced,
        },
        "lean_a_c_covariance": {
            "per_arm": {arm: chk for arm, chk in lean_a_by_arm.items()},
            "held_arms": lean_a_held_arms,
            "any_held": lean_a_any_held,
            "any_underpowered": lean_a_any_underpowered,
            "all_clean_miss": lean_a_all_clean_miss,
        },
        "lean_b_no_loss": {
            "per_arm": {arm: chk for arm, chk in lean_b_by_arm.items()},
            "evaluated_for": lean_a_held_arms,
            "disclosed_companion_all_covariant_arms_regardless_of_lean_a": lean_b_by_arm_all,
        },
        "lean_c_specificity": {
            "check": lean_c_check,
            "confirmed": lean_c_confirmed,
            "unresolved": lean_c_unresolved,
        },
        "pivot": {
            "registered": "no covariant candidate achieves c-invariance -> scale dependence not a simple ridge-scaling issue",
            "fires": pivot_fires,
            "status": pivot_status,
        },
        "certified_arms": certified_arms,
        "verdict": verdict,
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only (8 D1 worlds, reused verbatim from "
            "M4-G2/M4-G3); truth-recovery statistics use M4-G2's own valid 6-world "
            "subset, reused verbatim; truth-referenced recovery via budget-regenerated "
            "(4x/8x events) finite panels from the frozen world law, compared to the "
            "analytic D_true; no natural-text, personality, or clinical claim; no seal, "
            "no independent verification (operator directive 2026-08-01)."
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
    pd.DataFrame(g2_rows).to_csv(output / "g2_ridge_vs_c.csv", index=False)
    pd.DataFrame(g0_probe_rows).to_csv(output / "g0_and_lean_pairwise_rows.csv", index=False)

    print(
        json.dumps(
            {
                "verdict": verdict,
                "pivot_status": pivot_status,
                "pivot_fires": pivot_fires,
                "lean_a_held_arms": lean_a_held_arms,
                "lean_a_any_held": lean_a_any_held,
                "lean_a_any_underpowered": lean_a_any_underpowered,
                "lean_b_held": {arm: chk["held"] for arm, chk in lean_b_by_arm.items()},
                "lean_c_confirmed": lean_c_confirmed,
                "certified_arms": certified_arms,
                "g1_anchor_pass": g1_anchor["pass"],
                "g3_pass": g3_gate["pass"],
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
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_g4_covariant_ridge")
    parser.add_argument("--world", type=str, default=None)
    parser.add_argument("--stage", type=str, choices=("calibrate", "truth"), default=None)
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

    if args.stage == "calibrate":
        _run_calibrate(config, spec, args.output)
        return

    if args.world is None:
        raise SystemExit("--world is required for --stage truth")
    if args.world not in D1_WORLDS:
        raise SystemExit(f"not a registered D1 world: {args.world}")
    with (args.output / "calibration.json").open("r", encoding="utf-8") as handle:
        calibration = json.load(handle)
    _run_truth_stage(args.world, config, spec, calibration, args.output)


if __name__ == "__main__":
    main()
