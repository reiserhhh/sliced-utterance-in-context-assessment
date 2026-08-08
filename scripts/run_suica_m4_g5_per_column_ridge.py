#!/usr/bin/env python3
"""M4-G5: per-column regularization -- does the named defect have the
obvious fix?

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design
and leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-G5
registration" (2026-08-03, BEFORE run); ledger row M4-G5). Machinery is
IMPORTED and REUSED, not reimplemented: M4-G1/G2/G3/G4's world set, context
builder (`g1._build_world_contexts`), whitening-scale construction
(`g2._whitening_for_c`), basis construction (`leg10._bases_from_whitening`,
UNCHANGED -- none of this leg's arms touch it), M4-G3's parameterized
estimator internals (`g3._fit_logistic_adaptive`, `g3._hazard_probability_adaptive`,
`g3._feedback_derivative_adaptive`), M4-G4's post-whitening statistic and its
persisted calibration (`g4._post_scale_stats`, `g4._resolve_params`, and the
persisted `results/m4_g4_covariant_ridge/calibration.json`), CI helpers
(`g1._paired_world_ci`, `g1._paired_author_ci`) and -- centrally -- M4-G4's
OWN generic lean/gate machinery (`g4._author_level_truth_with_c`,
`g4._paired_author_diff_ci`, `g4._paired_world_diff_ci`, `g4._classify_pair`,
`g4._arm_status_from_pairs`, `g4._c_invariance_check`, `g4._no_loss_check`),
called here UNCHANGED with this leg's own arm names -- these functions take
`author_truth`/`arm`/`worlds` as parameters (or a hardcoded `"g3_raw_scale"`
string this leg's own anchor arm is also named), never anything G4-specific,
so they work correctly on this leg's own data with zero modification. `g4`'s
own module-level `C_LADDER = (0.25, 1.0, 4.0)` and `TRUTH_BUDGETS = (4.0, 8.0)`
and margins (`LEAN_A_MARGIN=0.02`, `LEAN_B_MARGIN=0.02`, `G0_FRACTION_BAR=0.01`)
are IDENTICAL to this leg's own registered values, so no monkeypatching or
redefinition is needed for the gate layer. The only genuinely NEW code is
(i) the column inventory and its empirical verification, (ii) the two
per-column mechanisms (`column_standardized`, `diagonal_ridge`) and their
disclosed near-duplicate fit internals, (iii) this leg's own arm dispatcher,
G2 spread evidence, and the residual-vs-M4-G4 quantitative-improvement
computation lean (c) needs (which no prior leg computed, since no prior leg
compared itself against an earlier leg's own residual).

THE QUESTION (M4-G4's planner adjudication note). M4-G4 named the mechanism:
`_hazard_design` (suica_core/m4_chart_ecology_estimator.py:287-330) mixes
columns built from the whitened basis (which scale with c) with columns
built from raw world data or the unscaled intercept sub-column (which do
not), so a single SCALAR ridge cannot be scale-consistent across the whole
design -- a scalar covariant ridge closed 89.1% of the raw c-dependence, the
residual 10.9% is structural. Does making the regularization PER-COLUMN
complete the repair?

===========================================================================
PART 0 -- REGISTERED COLUMN INVENTORY, COLUMN-SCALE STATISTIC, CALIBRATION
RULE, SPECIFICITY-CONTROL READING, AND THE PRE-COMPUTE MECHANISTIC
PREDICTION (frozen BEFORE any truth-recovery compute).
===========================================================================

--- 0.1 The full `_hazard_design` column inventory, from the code ------------

`_hazard_design(rows, basis, *, model, misalign_gate=False)`
(suica_core/m4_chart_ecology_estimator.py:287-330) builds, for `categories,
width = basis.shape` (`basis` from `leg10._bases_from_whitening`, itself
`column_stack([ones, whitened])` -- leg10.py:356 -- so `basis[:,0]` is
ALWAYS a literal-1 column and `basis[:,1:]` is `whitened_c = c*whitened_1`,
identity (*) from M4-G4's own Part 0):

| block | design columns | source line(s) | value | provenance |
|---|---|---|---|---|
| `intercept` | 1 (index 0) | estimator.py:297 `np.ones((events,categories,1))` | literal 1 | **c-invariant** (never touches basis or c at all) |
| `condition_0..width-1` | `width` (indices 1..width) | estimator.py:298-301, names at :269 `_hazard_names` | `basis[None]` broadcast | `condition_0` = `basis[:,0]` = literal 1 -> **c-invariant**; `condition_1..width-1` = `basis[:,1:]` = `c*whitened_1` -> **c-scaled, exactly linear in c** |
| `generated_current` | 1 (return/feedback/gate only) | estimator.py:306 `rows["generated"][...,None].astype(float)` | raw world data | **c-invariant** |
| `duration` | 1 (return/feedback/gate only) | estimator.py:307 `np.tanh(rows["duration"]/4.0)[...,None]` | raw world data | **c-invariant** |
| `feedback_{p}_{d}` | `width*dimensions` (feedback/gate only) | estimator.py:311-315 `einsum("kp,nd->nkpd", basis, response_next)` | `basis[:,p]*response_next[:,d]` | `p=0` (`dimensions` cols) = `1*response_next[:,d]` -> **c-invariant** (crosses the UNSCALED intercept sub-column with raw `response_next`); `p=1..width-1` ((width-1)*dimensions cols) = `c*whitened_1[:,p-1]*response_next[:,d]` -> **c-scaled, exactly linear in c** |
| `gate_{p}_{d}` | `width*dimensions` (gate only) | estimator.py:317-321 `feedback*gate[:,None,None]`, `gate=(history[:,0]>0).astype(float)` | `feedback_{p,d}*gate_row` | same split as `feedback_{p}_{d}` (raw 0/1 multiplier is c-invariant, doesn't change the degree): `p=0` -> **c-invariant**; `p=1..width-1` -> **c-scaled, exactly linear in c** |

Column counts by `model` (`width = 1 + k_retained`, `k_retained` in
[6,12] empirically across this line's 64 (world,rep) contexts -- see
`calibration_context_rows.csv` in `results/m4_g4_covariant_ridge/`;
`dimensions = response_dimensions = 2`, fixed by `configs/m4_chart_ecology.json`):
`base`: `1+width`. `return`: `1+width+2`. `feedback`: `1+width+2+width*dimensions`.
`gate`: `1+width+2+2*width*dimensions`. Every column, in every model, in every
route ever selected by an author, is **exactly** one of two kinds: literally
constant in c (degree 0), or exactly linear in c (degree 1) -- proved above
directly from the code, no column is ever a mix of both, and no additive
constant term ever appears alongside a c-scaled term within one column.
This binary split (verified EMPIRICALLY too, not just asserted -- see
`--stage inventory`, `column_inventory.csv`) is the structural fact this
leg's two per-column mechanisms exploit.

--- 0.2 Registered column-scale statistic ------------------------------------

Per-column VARIANCE (ddof=1), computed on the assembled, UNWEIGHTED
`_hazard_design` output -- the SAME stacked (calibration+selection) design
`_fit_logistic`'s Gram matrix (`design.T @ diag(weight) @ design`) is built
from -- computed ONCE, before any IRLS iteration, fresh for whatever
`(context, route, rows, c)` a given fit call uses:

    var_j(context, route, rows, c) := Var_ddof1( design(rows, c)[:, j] )

This is a genuine EXTENSION of M4-G4's own S1 "var" statistic (which was
computed on `basis` alone, categories x width, dropping the intercept
column) to the FULL assembled hazard design (events*categories x p,
including `generated_current`/`duration`/`feedback_*`/`gate_*`, which are
not part of `basis` at all) -- required because this leg's own registered
target is "the full `_hazard_design` column inventory", not merely the
basis. Degenerate-column floor: `DESIGN_VAR_FLOOR = 1e-12` (reused, not
invented -- the same floor value appears pervasively in this codebase, e.g.
`leg10._whitening_with_lambda`'s `np.maximum(eigenvalues[retained]+lam,
1e-12)`). Columns with `var_j < DESIGN_VAR_FLOOR` are the two
structurally-constant columns (`intercept`, `condition_0`; verified
empirically, not merely predicted, in `column_inventory.csv`).

--- 0.3 `column_standardized` (registered formula) ---------------------------

For column `j != 0` (the manually-added `intercept`, index 0, is ALREADY
ridge-exempt via `penalty[0,0]=0.0`, estimator.py:342, under every arm
including this one -- it is left untouched, never rescaled): if
`var_j(context,route,rows,c) >= DESIGN_VAR_FLOOR`, `scale_j := sqrt(var_j)`;
else `scale_j := 1.0` (no rescale). This "leave a near-zero-variance column
unscaled" rule is not invented for this leg -- it is the EXACT convention
already present in this same estimator file for the identical purpose
(`fit_m4_chart_ecology_route`, estimator.py:1009-1010: `scale =
np.where(scale > 1e-8, scale, 1.0)`), reused here (floor tightened to
1e-12 for column-level variance, matching this leg's own inventory floor,
rather than the 1e-8 std-level floor of that unrelated call site -- a
disclosed, deliberate choice, not a copy error).

    design_std[:, j] = design[:, j] / scale_j
    beta_std = g3._fit_logistic_adaptive(design_std, target, ridge=ridge_deployed, ...)   # UNCHANGED, reused
    beta = beta_std / scale                                                                # un-rescale

"The single ridge acts in common units": `ridge_deployed` (0.005) is used
UNMODIFIED -- no new calibration constant is introduced for this arm at
all. Downstream (`_hazard_probability`, `_feedback_derivative`) are called
on `beta` against the ORIGINAL, un-standardized basis/design -- byte-
identical to every other arm's own downstream code, reused unchanged.

--- 0.4 `diagonal_ridge` (registered formula) --------------------------------

Design is left **completely untouched** (registration's own words); only
the penalty matrix changes, from `ridge*n*I` (estimator.py:341-342) to
`n*diag(0, ridge_1(c), ..., ridge_{p-1}(c))` (index 0 stays exempt, matching
deployed `penalty[0,0]=0.0`):

    K(context,route,rows) := ridge_deployed / MEAN_{j != 0, var_j(c=1) >= FLOOR}( var_j(context,route,rows,c=1) )
    ridge_j(context,route,rows,c) := K(context,route,rows) * var_j(context,route,rows,c)      for j != 0, var_j(c=1) >= FLOOR
    ridge_j(context,route,rows,c) := ridge_deployed                                            for j != 0, var_j(c=1) < FLOOR  (degenerate fallback, see below)
    ridge_0 := 0

**Degenerate-column fallback, caught by a smoke test and fixed BEFORE any
hypothesis-relevant truth-recovery number existed (disclosed, not silently
patched).** `condition_0` (design index 1, `basis[:,0]`) is ALWAYS a
literal-1 column, structurally identical to the ridge-exempt `intercept`
(index 0) -- its `var_j(c=1)` is exactly 0. The naive formula above (no
fallback line) gives it `ridge_j = K*0 = 0` exactly, which reintroduces the
`intercept`/`condition_0` collinearity the DEPLOYED scalar ridge's own
uniform nonzero value was incidentally preventing, and
`_fit_logistic_diagonal`'s `np.linalg.solve` raises `LinAlgError: Singular
matrix` on the `feedback`/`gate` routes (verified: `base`/`return` routes,
whose Gram block does not otherwise depend on this, did not trip it in the
smoke test, but the fallback applies uniformly to every route on the same
principled ground). Fix: any non-exempt (`j!=0`) but degenerate
(`var_j(c=1) < DESIGN_VAR_FLOOR`) column keeps its ridge at the plain
DEPLOYED value -- exactly mirroring `column_standardized`'s OWN "leave a
degenerate column unscaled" rule (Part 0.3), which likewise keeps such a
column's implicit ridge contribution at `ridge_deployed` (scale factor 1).
This makes the two arms' degenerate-column treatment consistent by
construction, not merely by coincidence.

**Registered ambiguity, both readings disclosed (per the outer task's own
instruction).** `K` could be calibrated (i) GLOBALLY -- a single scalar
across all 64 (world,rep) contexts, mirroring M4-G4's own `alpha_var`
exactly -- or (ii) PER-CALL -- frozen fresh from THAT SAME (context, route,
rows) call's own design at c=1, reused at whatever c that call needs. Both
satisfy the registration's literal requirement ("reproduce the deployed
ridge at c=1 in the homogeneous-column limit": if `var_j(c=1)=V` for every
non-exempt `j`, `ridge_j(1) = ridge_deployed*V/V = ridge_deployed` exactly,
under EITHER reading). They differ in what they do NOT hold fixed: under
(i), `MEAN(var_j(c=1))` is one number shared by every author/route/world;
under (ii), it is recomputed per call, so it exactly matches the SAME
call's own subsequent use at whatever c is requested.

**ADOPTED: (ii), per-call.** Reasons, stated before compute: (a) M4-G4's
own hand-off explicitly named GLOBAL calibration as a source of its own
10.9% residual ("alpha is calibrated globally, not per-context, so some
residual is contributed by cross-context variation... around its population
mean" -- M4-G4 report, Part 0/Verdict). Since this leg exists to test
whether a MORE TARGETED, per-column mechanism can close that residual,
keeping the SAME global-calibration limitation would confound the test: a
MISS could then mean either "per-column doesn't help" or "global
calibration noise, already flagged by M4-G4, was reintroduced" -- and the
two would be indistinguishable. Per-call calibration removes this specific,
already-identified confound, isolating the "per-column" hypothesis
cleanly. (b) "Proportional to each column's own scale statistic"
(registration wording) is most literally read as within that SAME
column's own realized context, not a statistic pooled over 64 unrelated
ones. **Reading (i) is disclosed, not scored as a second arm** (mirroring
M4-G4's own precedent of disclosing its "per-context calibration limit" as
a reference number, not a scored arm): the GLOBAL value that (i) would
have used is recorded in `calibration_source.json`'s
`diagonal_ridge_global_k_disclosed_not_adopted` field, computed for free
from the SAME per-context `var_j(c=1)` statistics this leg already gathers
for its per-call K -- no extra compute stage.

--- 0.5 Pre-registered mechanistic prediction (disclosed BEFORE compute; a
    provable, not merely hoped-for, argument -- exceeding M4-G4's own
    "base-route-only" guarantee) ---------------------------------------------

Every column of `_hazard_design`, in every route, is exactly degree-0 or
exactly degree-1 in c (Part 0.1). Write `D(c) := diag(scale_j(c))` where,
for `column_standardized`, `scale_j(c) = sqrt(var_j(c))`, and for
`diagonal_ridge`'s reparameterization argument, `scale_j(c) := c` for
c-scaled `j`, `:= 1` for c-invariant `j` (both are, up to the degenerate-
column floor, the SAME diagonal reparameterization -- `column_standardized`
applies `D(c)^{-1}` to the DATA and fits with a scalar ridge; `diagonal_ridge`
applies `D(c) (.) D(c)` to the PENALTY and fits on the UNTOUCHED data --
the two are the SAME mathematical idea implemented on opposite sides of the
optimization problem). Substituting `beta = D(c)^{-1} gamma`: for
`column_standardized`, `design(c) = design(1) D(c)` EXACTLY (shown directly
from the column-degree table), so `design(c) beta = design(1) gamma`
regardless of c, and the ridge penalty `0.5 ridge ||beta_std||^2` is, by
definition, already expressed in `gamma = beta_std` coordinates. For
`diagonal_ridge`, `D(c)^{-1} @ penalty(c) @ D(c)^{-1} = n * diag(K*var_j(1))`,
independent of c (direct substitution). **In both cases the reparameterized
IRLS objective -- deviance plus penalty, as a function of `gamma` -- is
EXACTLY c-independent, and so is the reparameterized initial point
(`coefficient[0]` is the intercept, exempt and unscaled at every c;
every other start at exactly 0 regardless of c).** Newton's method / IRLS
is covariant under invertible linear reparameterization, so the ENTIRE
iterate sequence in `gamma`-coordinates -- not merely the fixed point -- is
identical at every c. Consequence: `design(rows,c) @ beta(c) = design(rows,1)
@ beta(1)` EXACTLY, for ANY rows (training or evaluation/probe alike, since
`scale_j(c)` depends only on column identity, not on which rows multiply
it) -- hence `fitted`, `weight`, the clipped logit, and ultimately
`e_arm_true` should be c-invariant up to floating point, for EVERY route
(base/return/feedback/gate), not merely `base` as in M4-G4's own guarantee.

**One disclosed, non-exact channel, flagged before compute, not
discovered after**: the IRLS convergence check (`step = max(abs(updated -
coefficient))`, estimator.py:357, compared against an ABSOLUTE tolerance)
is evaluated in `beta`-space, not `gamma`-space; since `beta(c) =
D(c)^{-1} gamma`, `step(c)` is NOT provably c-invariant (columns with large
`scale_j(c)` have their `gamma`-changes shrunk in `beta`-space), so the
ITERATION COUNT at which IRLS stops can differ slightly by c. This is
exactly M4-G3's own Category A2 ("IRLS convergence tolerance"), already
found CLEANLY, ADEQUATELY-POWERED INERT at both grains in M4-G3's own
test -- reused here as independent, prior evidence that this channel's
practical effect is negligible, not asserted fresh. **Prediction: lean (a)
should HOLD for both arms, likely far inside the ±0.02 margin (not merely
clearing it) -- a stronger result than M4-G4's own 89.1%, falsifiable
directly against Part 1's numbers below.**

--- 0.6 Specificity control: reading adopted, and why -------------------------

**Registered ambiguity, disclosed.** "A specificity control carried over
from M4-G4: the same per-column rule applied where it should do nothing."
M4-G3's four cleanly-inert constants are `tolerance` (mode-switch, not
multiplicative -- excluded, same as M4-G4's own exclusion), `weight_floor`,
`clip_bound`, `probe_epsilon` (the latter two rejected by M4-G4's own
Part 0 for plausible-live-channel risk at the c-ladder's extremes -- reused
here verbatim, not re-litigated). Of the surviving `weight_floor`: it is a
quantity `_fit_logistic` clips PER-OBSERVATION (`fitted*(1-fitted)`,
estimator.py:348) -- it has no design-COLUMN index at all, so there is no
literal "per-column" decomposition of it to construct; that reading is
**rejected as VACUOUS by construction** (not merely difficult) -- there is
no such object in the codebase, for any constant M4-G3/M4-G4 inventoried
(every one of them is a scalar; only `hazard_ridge`, added as `ridge*n*I`
to a per-column Gram structure, ever had a column-indexed form to begin
with). **ADOPTED reading**: "carried over from M4-G4" is read as reusing
M4-G4's OWN control -- same target (`weight_floor`), same mechanism
(`floor_covariant(context,c) = alpha_floor * POST_SCALE_VAR(context,c)`,
`alpha_floor` read from M4-G4's own persisted `calibration.json`) -- as
THIS leg's specificity control, verified to reproduce M4-G4's persisted
`specificity_weight_floor` values at all three c to <=1e-12 (an ADDITIONAL
disclosed anchor, beyond the three the outer task names). Its role is
unchanged from M4-G4: demonstrate that a scale-aware treatment applied to
an M4-G3-confirmed-inert constant does not spuriously produce c-invariance
-- exactly the role "where the rule should do nothing" describes, even
though no literal per-column form of `weight_floor` exists to test instead.

===========================================================================
DESIGN (registered)
===========================================================================
Reuse M4-G4's 8 worlds (`g4.D1_WORLDS`, identical to `g3.D1_WORLDS`/
`g2.D1_WORLDS`) and objective path verbatim. Registered analysis grain:
AUTHOR (n up to 745, M4-G2's valid 6-world subset, degenerate-reference
exclusion, reused verbatim); world-grain numbers are companions only.

Six arms:
  baseline                  -- c=1 only (anchor to M4-G4's persisted value).
  g3_raw_scale               -- c=1 only (anchor to M4-G4's persisted value).
  covariant_var               -- c in {0.25,1,4}, full new compute (anchor to
                                 M4-G4's persisted value AT ALL THREE c, a
                                 stronger anchor than the registration's
                                 literal minimum since M4-G4 itself fully
                                 computed this arm at all three c).
  specificity_weight_floor    -- c in {0.25,1,4}, full new compute (carried-
                                 over control, ALSO anchored at all 3 c to
                                 M4-G4's persisted value -- see 0.6).
  column_standardized          -- c in {0.25,1,4}, full new compute.
  diagonal_ridge               -- c in {0.25,1,4}, full new compute.

No offset/GPA stage: neither `column_standardized` nor `diagonal_ridge`
ever calls `_bases_from_whitening` -- both operate strictly downstream, on
`_hazard_design`'s OUTPUT (design rescale) or on `_fit_logistic`'s PENALTY
(diagonal ridge) -- so offset is identical to baseline's for every arm here
by the same call-graph argument M4-G4 already used, verified structurally
(not merely assumed) via a bit-identical basis check at assembly time.

Chunked execution (this arc's standard workaround): `--stage inventory`
(no `--world`; column inventory + G2 spread evidence + the provable-
invariance spot check; cheap, at most a handful of small IRLS fits, no
IRLS fit at all for the inventory/spread parts) -> `--stage truth --world W`
(one world's full arm x c x budget sweep) -> `--assemble` (reads every
partial, cross-checks completeness, adjudicates).
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
from scipy.special import expit

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
import run_suica_m4_g4_covariant_ridge as g4  # noqa: E402  the leg this extends

from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    HAZARD_MODELS,
    _hazard_design,
    _hazard_names,
)
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
DESIGN_VAR_FLOOR = 1e-12  # reused codebase convention (see Part 0.2)
DEGENERATE_STD_FALLBACK = 1.0  # reused convention (estimator.py:1009-1010), see Part 0.3

MY_ARM_NAMES = (
    "baseline",
    "g3_raw_scale",
    "covariant_var",
    "specificity_weight_floor",
    "column_standardized",
    "diagonal_ridge",
)
ANCHOR_ONLY_C1_ARMS = ("baseline", "g3_raw_scale")  # G4's own compute-scope reduction, carried over
FULL_C_SWEEP_ARMS = ("covariant_var", "specificity_weight_floor", "column_standardized", "diagonal_ridge")
NEW_ARMS = ("column_standardized", "diagonal_ridge")  # this leg's own genuinely new mechanisms
REUSED_SCALAR_ARMS = ("baseline", "g3_raw_scale", "covariant_var", "specificity_weight_floor")

G1_ANCHOR_TOLERANCE = 1e-12
G3_TOLERANCE = 1e-12

G4_CALIBRATION_PATH = ROOT / "results" / "m4_g4_covariant_ridge" / "calibration.json"
G4_TRUTH_PATH = ROOT / "results" / "m4_g4_covariant_ridge" / "truth_recovery_rows.csv"


def _load_g4_calibration() -> dict[str, Any]:
    with G4_CALIBRATION_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


# ---------------------------------------------------------------------------
# Part 0.2-0.4: column-scale statistic, standardization, diagonal ridge
# ---------------------------------------------------------------------------


def _design_column_stats(design: np.ndarray) -> np.ndarray:
    """Per-column variance (ddof=1) of the assembled, UNWEIGHTED hazard
    design -- the SAME stacked array `_fit_logistic`'s Gram matrix is built
    from -- computed once, before any IRLS iteration. Part 0.2."""
    return np.var(design, axis=0, ddof=1)


def _standardize_design(design: np.ndarray, var: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Part 0.3. Column 0 (`intercept`) is never rescaled (already
    ridge-exempt); any other near-zero-variance column (`condition_0`,
    empirically verified degenerate) is also left unscaled, reusing
    estimator.py:1009-1010's own `scale = np.where(scale>eps, scale, 1.0)`
    convention."""
    std = np.sqrt(np.maximum(var, 0.0))
    scale = np.where(std > np.sqrt(DESIGN_VAR_FLOOR), std, DEGENERATE_STD_FALLBACK)
    scale = scale.copy()
    scale[0] = DEGENERATE_STD_FALLBACK  # intercept: never rescaled regardless of its own (zero) variance
    return design / scale[None, :], scale


def _diagonal_ridge_vector(var_c: np.ndarray, var_c1: np.ndarray, ridge_deployed: float) -> np.ndarray:
    """Part 0.4, reading (ii) ADOPTED: K frozen from THIS SAME call's own
    design at c=1, applied to var_c (the design at whatever c is requested).
    `ridge_0 := 0`, matching deployed `penalty[0,0]=0.0` under every arm.

    DEGENERATE-COLUMN FALLBACK (caught by a smoke test on `feedback`/`gate`
    routes BEFORE any hypothesis-relevant number existed -- disclosed here,
    not silently patched): `condition_0` (design index 1, `basis[:,0]`) is
    ALWAYS a literal-1 column, structurally identical to the ridge-exempt
    `intercept` (index 0) -- `var_j(c=1)=0` for it at every context/route.
    A naive `ridge_j = K*var_j` therefore gives `condition_0` ridge EXACTLY
    0, which reintroduces the intercept/condition_0 collinearity the
    DEPLOYED scalar ridge's own uniform nonzero value was (incidentally)
    preventing -- `np.linalg.solve` raises `LinAlgError: Singular matrix`.
    The fix, planned in Part 0.3 for `column_standardized` and mirrored
    here for consistency between the two arms: any NON-EXEMPT (`j!=0`) but
    DEGENERATE (`var_c1[j] < DESIGN_VAR_FLOOR`) column keeps its ridge at
    the plain DEPLOYED scalar value (not 0, not `K*floor`) -- exactly
    matching `column_standardized`'s own "leave a degenerate column
    unscaled" rule (Part 0.3), which likewise keeps such a column's
    IMPLICIT ridge contribution at `ridge_deployed` (scale factor 1, so the
    fit sees the column at its original, unrescaled magnitude with the
    original, unmodified ridge weight)."""
    p = len(var_c1)
    non_exempt = np.arange(p) != 0
    non_degenerate_c1 = var_c1 >= DESIGN_VAR_FLOOR
    reference_mask = non_exempt & non_degenerate_c1
    denom = float(np.mean(var_c1[reference_mask])) if np.any(reference_mask) else DESIGN_VAR_FLOOR
    denom = max(denom, DESIGN_VAR_FLOOR)
    k = ridge_deployed / denom
    ridge_vec = np.where(reference_mask, k * var_c, ridge_deployed)
    ridge_vec = ridge_vec.copy()
    ridge_vec[0] = 0.0  # intercept: always exempt, regardless of the fallback rule
    return ridge_vec


def _fit_logistic_diagonal(
    design: np.ndarray,
    target: np.ndarray,
    *,
    ridge_vector: np.ndarray,
    iterations: int,
    weight_floor: float = DEPLOYED_WEIGHT_FLOOR,
    clip_bound: float = DEPLOYED_CLIP_BOUND,
    tol_mode: str = "absolute",
    tol_value: float = DEPLOYED_TOL_VALUE,
) -> np.ndarray:
    """Disclosed near-duplicate of g3._fit_logistic_adaptive /
    estimator._fit_logistic (estimator.py:333-361), generalizing the
    penalty from a SCALAR `ridge*n*I` to a PER-COLUMN `n*diag(ridge_vector)`
    -- the only structural change; the IRLS loop, weight floor, clip bound,
    and tolerance-mode logic are byte-identical to g3._fit_logistic_adaptive."""
    y = np.asarray(target, dtype=float).reshape(-1)
    penalty = len(y) * np.diag(ridge_vector)
    coefficient = np.zeros(design.shape[1])
    probability = (np.sum(y) + 0.5) / (len(y) + 1.0)
    coefficient[0] = np.log(probability / (1.0 - probability))
    for _ in range(iterations):
        fitted = expit(np.clip(design @ coefficient, -clip_bound, clip_bound))
        weight = np.clip(fitted * (1.0 - fitted), weight_floor, None)
        adjusted = design @ coefficient + (y - fitted) / weight
        system = design.T @ (weight[:, None] * design) + penalty
        updated = np.linalg.solve(system, design.T @ (weight * adjusted))
        step = np.max(np.abs(updated - coefficient))
        converged = step < tol_value if tol_mode == "absolute" else step < tol_value * max(1.0, float(np.max(np.abs(coefficient))))
        if converged:
            coefficient = updated
            break
        coefficient = updated
    return coefficient


def _fit_logistic_columnstd(
    full_design: np.ndarray,
    full_target: np.ndarray,
    *,
    ridge_deployed: float,
    iterations: int,
    weight_floor: float,
    clip_bound: float,
    tol_mode: str,
    tol_value: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Returns `(beta, gamma, var, scale)`: `beta = gamma/scale` is the
    coefficient in ORIGINAL (un-standardized) units, used for every actual
    prediction/derivative downstream (it is what every arm's own
    `_hazard_probability`/`_feedback_derivative` call expects, matched
    against the un-standardized `basis`); `gamma` (= `coefficient_std`, the
    coefficient AS FIT in standardized units) is the reparameterized
    quantity Part 0.5's invariance argument predicts is c-invariant --
    `beta` itself is NOT expected to be c-invariant (it is expressed in
    units that themselves vary with c, `scale(c)`), and an earlier
    diagnostic draft mis-labeled `beta` as `gamma` when spot-checking this,
    apparently finding a large "gamma" difference that was actually just
    `beta`'s own, expected, unit-conversion dependence on c -- caught and
    fixed before any hypothesis-relevant truth-recovery number existed,
    disclosed here rather than silently corrected."""
    var = _design_column_stats(full_design)
    design_std, scale = _standardize_design(full_design, var)
    coefficient_std = g3._fit_logistic_adaptive(  # unchanged, reused
        design_std, full_target, ridge=ridge_deployed, iterations=iterations,
        weight_floor=weight_floor, clip_bound=clip_bound, tol_mode=tol_mode, tol_value=tol_value,
    )
    return coefficient_std / scale, coefficient_std, var, scale


def _fit_hazard_candidate_diagonal(
    datasets_c: list[tuple[dict[str, np.ndarray], np.ndarray]],
    datasets_c1: list[tuple[dict[str, np.ndarray], np.ndarray]],
    *,
    model: str,
    ridge_deployed: float,
    iterations: int,
    weight_floor: float,
    clip_bound: float,
    tol_mode: str,
    tol_value: float,
) -> tuple[np.ndarray, tuple[str, ...], np.ndarray]:
    """`diagonal_ridge`'s own dispatcher: builds the design at the
    requested c AND (separately) at c=1 (for K, Part 0.4 reading (ii)),
    from the SAME rows -- `_hazard_design` reused unchanged both times."""
    designs, targets, names = [], [], None
    for rows, basis in datasets_c:
        design, current_names = _hazard_design(rows, basis, model=model)
        designs.append(design)
        targets.append(rows["generated_next"].reshape(-1))
        names = current_names
    full_design = np.vstack(designs)
    full_target = np.concatenate(targets)
    var_c = _design_column_stats(full_design)

    designs1 = [_hazard_design(rows, basis1, model=model)[0] for (rows, _basis), (_rows1, basis1) in zip(datasets_c, datasets_c1)]
    full_design1 = np.vstack(designs1)
    var_c1 = _design_column_stats(full_design1)

    ridge_vector = _diagonal_ridge_vector(var_c, var_c1, ridge_deployed)
    coefficient = _fit_logistic_diagonal(
        full_design, full_target, ridge_vector=ridge_vector, iterations=iterations,
        weight_floor=weight_floor, clip_bound=clip_bound, tol_mode=tol_mode, tol_value=tol_value,
    )
    return coefficient, (names or ()), ridge_vector


def _forced_route_derivative_columnwise(
    calibration: dict[str, np.ndarray],
    selection: dict[str, np.ndarray],
    basis: dict[str, np.ndarray],
    basis_c1: dict[str, np.ndarray],
    *,
    model: str,
    treatment: str,
    ridge_deployed: float,
    logistic_iterations: int,
    dimensions: int,
    weight_floor: float = DEPLOYED_WEIGHT_FLOOR,
    clip_bound: float = DEPLOYED_CLIP_BOUND,
    tol_mode: str = "absolute",
    tol_value: float = DEPLOYED_TOL_VALUE,
    probe_epsilon: float = DEPLOYED_PROBE_EPSILON,
) -> np.ndarray:
    """This leg's own near-duplicate of g3._forced_route_derivative_adaptive
    (scripts/run_suica_m4_g3_scale_adaptive.py:668-705), dispatching to this
    leg's two per-column fit paths; the probe/derivative step itself
    (`g3._feedback_derivative_adaptive`) is reused UNCHANGED."""
    datasets_c = [(calibration, basis["calibration"]), (selection, basis["selection"])]
    if treatment == "column_standardized":
        full_design_datasets = datasets_c
        designs, targets = [], []
        for rows, b in full_design_datasets:
            design, names = _hazard_design(rows, b, model=model)
            designs.append(design)
            targets.append(rows["generated_next"].reshape(-1))
        full_design = np.vstack(designs)
        full_target = np.concatenate(targets)
        coefficient, _gamma, _var, _scale = _fit_logistic_columnstd(
            full_design, full_target, ridge_deployed=ridge_deployed, iterations=logistic_iterations,
            weight_floor=weight_floor, clip_bound=clip_bound, tol_mode=tol_mode, tol_value=tol_value,
        )
    elif treatment == "diagonal_ridge":
        datasets_c1 = [(calibration, basis_c1["calibration"]), (selection, basis_c1["selection"])]
        coefficient, names, _ridge_vec = _fit_hazard_candidate_diagonal(
            datasets_c, datasets_c1, model=model, ridge_deployed=ridge_deployed, iterations=logistic_iterations,
            weight_floor=weight_floor, clip_bound=clip_bound, tol_mode=tol_mode, tol_value=tol_value,
        )
    else:
        raise ValueError(f"unknown treatment: {treatment}")
    return g3._feedback_derivative_adaptive(  # unchanged, reused
        coefficient, names, basis["evaluation"], dimensions, epsilon=probe_epsilon, clip_bound=clip_bound,
    )


# ---------------------------------------------------------------------------
# per-context arm parameter resolution
# ---------------------------------------------------------------------------


def _resolve_all_params(
    context: dict[str, Any], ingredients: dict[str, Any], c: float, calibration: dict[str, Any]
) -> tuple[dict[str, dict[str, Any]], dict[str, np.ndarray], float, float]:
    raw_scale = float(np.mean(ingredients["eigenvalues"][ingredients["retained"]]))
    deployed_ridge = float(context["fit_kwargs"]["hazard_ridge"])
    var_stat, msq_stat, basis = g4._post_scale_stats(context, ingredients, c)  # unchanged, reused
    alpha = {"var": calibration["alpha_var"], "msq": calibration["alpha_msq"], "floor": calibration["alpha_floor"]}
    resolved: dict[str, dict[str, Any]] = {}
    for arm in REUSED_SCALAR_ARMS:
        resolved[arm] = g4._resolve_params(arm, deployed_ridge, raw_scale, var_stat, msq_stat, alpha)  # unchanged, reused
    for arm in NEW_ARMS:
        resolved[arm] = {
            "ridge_deployed": deployed_ridge,
            "weight_floor": DEPLOYED_WEIGHT_FLOOR,
            "clip_bound": DEPLOYED_CLIP_BOUND,
            "tol_mode": "absolute",
            "tol_value": DEPLOYED_TOL_VALUE,
            "probe_epsilon": DEPLOYED_PROBE_EPSILON,
        }
    return resolved, basis, raw_scale, deployed_ridge


# ---------------------------------------------------------------------------
# stage: inventory (column inventory, empirical provenance check, G2 spread
# evidence, provable-invariance spot check -- all cheap, no/minimal IRLS)
# ---------------------------------------------------------------------------


def _representative_rows(context: dict[str, Any]) -> dict[str, np.ndarray]:
    calibration_panel = context["observed"].ecology.train_calibration
    return leg4._flatten_events(calibration_panel, 0)


def _empirical_provenance(rows: dict[str, np.ndarray], basis_c1: dict[str, np.ndarray], basis_c2: dict[str, np.ndarray], model: str) -> list[dict[str, Any]]:
    design1, names = _hazard_design(rows, basis_c1["calibration"], model=model)
    design2, _ = _hazard_design(rows, basis_c2["calibration"], model=model)
    diff_same = np.max(np.abs(design2 - design1), axis=0)
    diff_double = np.max(np.abs(design2 - 2.0 * design1), axis=0)
    is_zero_at_1 = np.max(np.abs(design1), axis=0) < 1e-12
    out = []
    for j, name in enumerate(names):
        if diff_same[j] < 1e-9:
            provenance = "c_invariant"
        elif diff_double[j] < 1e-9:
            provenance = "c_scaled_degree1"
        elif is_zero_at_1[j]:
            provenance = "AMBIGUOUS_DEGENERATE_ZERO"
        else:
            provenance = "UNEXPECTED"
        out.append(
            {
                "model": model, "column_index": j, "column_name": name,
                "empirical_provenance": provenance,
                "max_abs_diff_from_c_invariant_prediction": float(diff_same[j]),
                "max_abs_diff_from_c_scaled_prediction": float(diff_double[j]),
            }
        )
    return out


def _run_inventory(config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    calibration = _load_g4_calibration()
    output.mkdir(parents=True, exist_ok=True)
    with (output / "calibration_source.json").open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "source": str(G4_CALIBRATION_PATH.relative_to(ROOT)),
                "alpha_var": calibration["alpha_var"],
                "alpha_msq": calibration["alpha_msq"],
                "alpha_floor": calibration["alpha_floor"],
                "deployed_ridge": calibration["deployed_ridge"],
                "deployed_weight_floor": calibration["deployed_weight_floor"],
                "note": (
                    "covariant_var and specificity_weight_floor reuse M4-G4's own alpha_var/alpha_floor "
                    "verbatim (Part 0.6) -- not recomputed here; anchored to <=1e-12 at assembly time instead."
                ),
            },
            handle, indent=2, sort_keys=True,
        )
        handle.write("\n")

    inventory_rows: list[dict[str, Any]] = []
    spread_rows: list[dict[str, Any]] = []
    invariance_rows: list[dict[str, Any]] = []
    global_k_context_rows: list[dict[str, Any]] = []

    for world in D1_WORLDS:
        contexts = g1._build_world_contexts(world, config, spec)
        context = contexts[0]
        ingredients = leg10._freeze_ingredients(context)
        deployed_ridge = float(context["fit_kwargs"]["hazard_ridge"])
        rows = _representative_rows(context)

        whitening_c1 = g2._whitening_for_c(ingredients, 1.0)
        whitening_c2 = g2._whitening_for_c(ingredients, 2.0)
        basis_c1 = leg10._bases_from_whitening(context, ingredients, whitening_c1)
        basis_c2 = leg10._bases_from_whitening(context, ingredients, whitening_c2)

        for model in HAZARD_MODELS:
            for row in _empirical_provenance(rows, basis_c1, basis_c2, model):
                inventory_rows.append({"world": world, **row})

        for c in C_LADDER:
            whitening = g2._whitening_for_c(ingredients, c)
            basis = leg10._bases_from_whitening(context, ingredients, whitening)
            for model in HAZARD_MODELS:
                design, names = _hazard_design(rows, basis["calibration"], model=model)
                var = _design_column_stats(design)
                non_exempt = np.arange(len(var)) != 0
                non_degenerate = var >= DESIGN_VAR_FLOOR
                ref_mask = non_exempt & non_degenerate
                before_spread = (
                    float(np.max(var[ref_mask]) / np.min(var[ref_mask])) if int(np.sum(ref_mask)) >= 2 else float("nan")
                )
                design_std, scale = _standardize_design(design, var)
                var_after_std = _design_column_stats(design_std)
                after_std_spread = (
                    float(np.max(var_after_std[ref_mask]) / np.min(var_after_std[ref_mask])) if int(np.sum(ref_mask)) >= 2 else float("nan")
                )
                design1, _ = _hazard_design(rows, basis_c1["calibration"], model=model)
                var1 = _design_column_stats(design1)
                ridge_vec = _diagonal_ridge_vector(var, var1, deployed_ridge)
                ridge_ref = ridge_vec[ref_mask]
                after_ridge_spread = (
                    float(np.max(ridge_ref) / np.min(ridge_ref)) if int(np.sum(ref_mask)) >= 2 and np.min(ridge_ref) > 0 else float("nan")
                )
                spread_rows.append(
                    {
                        "world": world, "model": model, "c": c, "n_columns": int(len(var)),
                        "n_reference_columns": int(np.sum(ref_mask)),
                        "design_var_spread_before": before_spread,
                        "design_var_spread_after_column_standardized": after_std_spread,
                        "ridge_spread_before_deployed_uniform": 1.0,
                        "ridge_spread_after_diagonal_ridge": after_ridge_spread,
                        "global_k_would_be_denom": float(np.mean(var1[ref_mask])) if int(np.sum(ref_mask)) > 0 else float("nan"),
                    }
                )
        print(f"[m4g5] inventory {world} done", flush=True)

    # provable-invariance spot check (Part 0.5): fit column_standardized and
    # diagonal_ridge on ONE representative (rep=0, route="feedback" forced,
    # the richest column mix short of "gate") context, at every c, and
    # verify the REPARAMETERIZED coefficient (gamma) is c-invariant, plus
    # e_arm_true itself.
    context0 = g1._build_world_contexts(D1_WORLDS[0], config, spec)[0]
    ingredients0 = leg10._freeze_ingredients(context0)
    dims0 = context0["flat"][("train", 0)][0]["response_next"].shape[1]
    d_true0 = leg4._true_derivative(context0["truth"], 0)
    calibration0 = leg4._flatten_events(context0["observed"].ecology.train_calibration, 0)
    selection0 = leg4._flatten_events(context0["observed"].ecology.train_selection, 0)
    deployed_ridge0 = float(context0["fit_kwargs"]["hazard_ridge"])
    logit_iters0 = int(context0["fit_kwargs"]["logistic_iterations"])
    basis_c1_0 = leg10._bases_from_whitening(context0, ingredients0, g2._whitening_for_c(ingredients0, 1.0))
    for treatment in NEW_ARMS:
        gammas = {}
        e_arm_by_c = {}
        for c in C_LADDER:
            basis_c = leg10._bases_from_whitening(context0, ingredients0, g2._whitening_for_c(ingredients0, c))
            d_arm = _forced_route_derivative_columnwise(
                calibration0, selection0, basis_c, basis_c1_0, model="feedback", treatment=treatment,
                ridge_deployed=deployed_ridge0, logistic_iterations=logit_iters0, dimensions=dims0,
            )
            e_arm_by_c[c] = leg3._relative_error(d_arm, d_true0)
            # reparameterized coefficient gamma: refit here explicitly to capture it
            datasets_c = [(calibration0, basis_c["calibration"]), (selection0, basis_c["selection"])]
            designs, targets = [], []
            for rows_, b_ in datasets_c:
                design_, names_ = _hazard_design(rows_, b_, model="feedback")
                designs.append(design_)
                targets.append(rows_["generated_next"].reshape(-1))
            full_design = np.vstack(designs)
            full_target = np.concatenate(targets)
            if treatment == "column_standardized":
                _beta, gamma, var_, scale_ = _fit_logistic_columnstd(
                    full_design, full_target, ridge_deployed=deployed_ridge0, iterations=logit_iters0,
                    weight_floor=DEPLOYED_WEIGHT_FLOOR, clip_bound=DEPLOYED_CLIP_BOUND, tol_mode="absolute", tol_value=DEPLOYED_TOL_VALUE,
                )
                gammas[c] = gamma  # gamma = coefficient_std, the standardized-space fit -- THIS is
                                    # what Part 0.5 predicts is c-invariant, not `_beta` (=gamma/scale,
                                    # in original units that themselves vary with c by construction)
            else:
                datasets_c1 = [(calibration0, basis_c1_0["calibration"]), (selection0, basis_c1_0["selection"])]
                coeff, names_, ridge_vec_ = _fit_hazard_candidate_diagonal(
                    datasets_c, datasets_c1, model="feedback", ridge_deployed=deployed_ridge0, iterations=logit_iters0,
                    weight_floor=DEPLOYED_WEIGHT_FLOOR, clip_bound=DEPLOYED_CLIP_BOUND, tol_mode="absolute", tol_value=DEPLOYED_TOL_VALUE,
                )
                var1_ = _design_column_stats(np.vstack([_hazard_design(r, b, model="feedback")[0] for r, b in datasets_c1]))
                scale_gamma = np.where(var1_ >= DESIGN_VAR_FLOOR, np.sqrt(var1_ / np.maximum(var1_, DESIGN_VAR_FLOOR)), 1.0)
                # gamma = D(c) @ beta; D(c)_jj = c for c-scaled, 1 for c-invariant -- reconstruct via var ratio at THIS c vs c=1
                var_c_ = _design_column_stats(full_design)
                ratio = np.where(var1_ >= DESIGN_VAR_FLOOR, np.sqrt(np.maximum(var_c_, 0.0) / np.maximum(var1_, DESIGN_VAR_FLOOR)), 1.0)
                gammas[c] = ratio * coeff
        for c_lo, c_hi in itertools.combinations(C_LADDER, 2):
            gamma_diff = float(np.max(np.abs(gammas[c_lo] - gammas[c_hi])))
            e_diff = abs(e_arm_by_c[c_lo] - e_arm_by_c[c_hi])
            invariance_rows.append(
                {
                    "treatment": treatment, "c_lo": c_lo, "c_hi": c_hi,
                    "max_abs_gamma_diff": gamma_diff, "e_arm_true_diff": e_diff,
                    "e_arm_true_c_lo": e_arm_by_c[c_lo], "e_arm_true_c_hi": e_arm_by_c[c_hi],
                }
            )
    print(f"[m4g5] provable-invariance spot check done", flush=True)

    pd.DataFrame(inventory_rows).to_csv(output / "column_inventory.csv", index=False)
    pd.DataFrame(spread_rows).to_csv(output / "g2_column_scale_spread_evidence.csv", index=False)
    pd.DataFrame(invariance_rows).to_csv(output / "provable_invariance_spot_check.csv", index=False)
    print("[m4g5] inventory stage complete", flush=True)


# ---------------------------------------------------------------------------
# G3-style truth-path invariance spot check, generalized over this leg's
# arms x c (disclosed near-duplicate of g3._run_truth_stage's inline block /
# g4._g3_spot_check, generalized for this leg's dual dispatch).
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
        resolved, basis, _raw_scale, deployed_ridge = _resolve_all_params(context, ingredients, c, calibration)
        basis_c1 = basis if c == 1.0 else leg10._bases_from_whitening(
            context, ingredients, g2._whitening_for_c(ingredients, 1.0)
        )
        arms_here = MY_ARM_NAMES if c == 1.0 else FULL_C_SWEEP_ARMS
        for arm in arms_here:
            params = resolved[arm]
            if arm in NEW_ARMS:
                d_gapstyle = _forced_route_derivative_columnwise(
                    calibration_flat, selection_flat, basis, basis_c1, model=route, treatment=arm,
                    ridge_deployed=params["ridge_deployed"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
                    weight_floor=params["weight_floor"], clip_bound=params["clip_bound"],
                    tol_mode=params["tol_mode"], tol_value=params["tol_value"], probe_epsilon=params["probe_epsilon"],
                )
                d_truthpath = _forced_route_derivative_columnwise(
                    calibration_g3, selection_g3, basis, basis_c1, model=route, treatment=arm,
                    ridge_deployed=params["ridge_deployed"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
                    weight_floor=params["weight_floor"], clip_bound=params["clip_bound"],
                    tol_mode=params["tol_mode"], tol_value=params["tol_value"], probe_epsilon=params["probe_epsilon"],
                )
            else:
                d_gapstyle = g3._forced_route_derivative_adaptive(
                    calibration_flat, selection_flat, basis, model=route,
                    hazard_ridge=params["ridge"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
                    weight_floor=params["weight_floor"], clip_bound=params["clip_bound"],
                    tol_mode=params["tol_mode"], tol_value=params["tol_value"], probe_epsilon=params["probe_epsilon"],
                )
                d_truthpath = g3._forced_route_derivative_adaptive(
                    calibration_g3, selection_g3, basis, model=route,
                    hazard_ridge=params["ridge"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
                    weight_floor=params["weight_floor"], clip_bound=params["clip_bound"],
                    tol_mode=params["tol_mode"], tol_value=params["tol_value"], probe_epsilon=params["probe_epsilon"],
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
# stage: truth (per world)
# ---------------------------------------------------------------------------


def _truth_rows_for_context(
    context: dict[str, Any],
    arm_bases_rep: dict[str, dict[str, np.ndarray]],
    basis_c1: dict[str, np.ndarray],
    resolved_rep: dict[str, dict[str, Any]],
    spec: M4ChartEcologySpec,
    budget: float,
    c: float,
    *,
    arms: tuple[str, ...],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Disclosed near-duplicate of g3._truth_rows_for_context
    (scripts/run_suica_m4_g3_scale_adaptive.py:784-888), generalized over
    two dispatch paths per arm (reused g3._forced_route_derivative_adaptive
    for scalar-ridge arms; this leg's own _forced_route_derivative_columnwise
    for column_standardized/diagonal_ridge) and taking `c` as an explicit
    parameter."""
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
                if arm in NEW_ARMS:
                    d_arm_b = _forced_route_derivative_columnwise(
                        calibration_b, selection_b, basis, basis_c1, model=route, treatment=arm,
                        ridge_deployed=params["ridge_deployed"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
                        weight_floor=params["weight_floor"], clip_bound=params["clip_bound"],
                        tol_mode=params["tol_mode"], tol_value=params["tol_value"], probe_epsilon=params["probe_epsilon"],
                    )
                else:
                    d_arm_b = g3._forced_route_derivative_adaptive(
                        calibration_b, selection_b, basis, model=route,
                        hazard_ridge=params["ridge"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
                        weight_floor=params["weight_floor"], clip_bound=params["clip_bound"],
                        tol_mode=params["tol_mode"], tol_value=params["tol_value"], probe_epsilon=params["probe_epsilon"],
                    )
                e_arm_true = leg3._relative_error(d_arm_b, d_true)
                rows.append({**keys, "arm": arm, "c": c, "e_arm_true": e_arm_true, "e_orc_true": e_orc_true})
    gate = {
        "world": world, "repetition": repetition, "budget": budget, "events": events_b,
        "n_cal_rows_last": n_cal_rows, "n_sel_rows_last": n_sel_rows,
    }
    return rows, gate


def _run_truth_stage(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    calibration = _load_g4_calibration()
    contexts = g1._build_world_contexts(world, config, spec)

    g3_rows = _g3_spot_check(world, contexts, calibration)
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
        basis_c1 = leg10._bases_from_whitening(context, ingredients, g2._whitening_for_c(ingredients, 1.0))
        for c in C_LADDER:
            resolved, basis, raw_scale, deployed_ridge = _resolve_all_params(context, ingredients, c, calibration)
            rep_meta[f"raw_scale_c{c:g}"] = raw_scale
            rep_meta[f"deployed_ridge_c{c:g}"] = deployed_ridge
            arms_here = MY_ARM_NAMES if c == 1.0 else FULL_C_SWEEP_ARMS
            arm_bases_rep = {arm: basis for arm in arms_here}
            resolved_rep = {arm: resolved[arm] for arm in arms_here}
            for arm in arms_here:
                params = resolved_rep[arm]
                rep_meta[f"ridge_{arm}_c{c:g}"] = params.get("ridge", params.get("ridge_deployed"))
                rep_meta[f"weight_floor_{arm}_c{c:g}"] = params["weight_floor"]
            for budget in TRUTH_BUDGETS:
                started = time.time()
                rows, gate = _truth_rows_for_context(context, arm_bases_rep, basis_c1, resolved_rep, spec, budget, c, arms=arms_here)
                for row in rows:
                    if row["c"] != c:
                        raise RuntimeError(f"c mismatch: expected {c}, row={row}")
                all_rows.extend(rows)
                truth_gates.append(gate)
                print(
                    f"[m4g5] truth c={c:g} b={budget:g} {world} rep={rep_idx} arms={arms_here} ({time.time()-started:.1f}s)",
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
    print(f"[m4g5] truth stage done: {world}", flush=True)


# ---------------------------------------------------------------------------
# assemble + adjudicate
# ---------------------------------------------------------------------------


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

    # ---- G1 ANCHOR: baseline@c=1, g3_raw_scale@c=1, covariant_var@{.25,1,4},
    # specificity_weight_floor@{.25,1,4} vs M4-G4's persisted values ----------
    m4g4_truth = pd.read_csv(G4_TRUTH_PATH)
    anchor_rows = []
    anchor_plan = [
        ("baseline", "baseline", (1.0,)),
        ("g3_raw_scale", "g3_raw_scale", (1.0,)),
        ("covariant_var", "covariant_var", C_LADDER),
        ("specificity_weight_floor", "specificity_weight_floor", C_LADDER),
    ]
    for mine_arm, g4_arm, c_values in anchor_plan:
        mine = truth_rows[(truth_rows["arm"] == mine_arm) & (truth_rows["c"].isin(c_values))]
        theirs = m4g4_truth[(m4g4_truth["arm"] == g4_arm) & (m4g4_truth["c"].isin(c_values))]
        joined = mine.merge(theirs, on=["world", "repetition", "view", "author", "budget", "c"], suffixes=("_mine", "_theirs"), how="inner")
        expected = len(worlds) * len(TRUTH_BUDGETS) * 8 * 2 * 16 * len(c_values)
        if len(joined) != expected:
            raise RuntimeError(f"G1 anchor join size {len(joined)} != expected {expected} for {mine_arm}")
        diff = (joined["e_arm_true_mine"] - joined["e_arm_true_theirs"]).abs()
        anchor_rows.append(
            {"arm": mine_arm, "g4_arm": g4_arm, "c_values": list(c_values), "n_rows": int(len(joined)), "max_abs_diff": float(diff.max(skipna=True))}
        )
    g1_anchor_max = max(row["max_abs_diff"] for row in anchor_rows)
    g1_anchor = {
        "per_arm": anchor_rows, "max_abs_diff": g1_anchor_max, "tolerance": G1_ANCHOR_TOLERANCE,
        "pass": bool(g1_anchor_max <= G1_ANCHOR_TOLERANCE),
        "note": (
            "baseline/g3_raw_scale anchored at c=1 only (M4-G4's own compute-scope reduction, carried "
            "over verbatim). covariant_var anchored at ALL THREE c (stronger than the registration's literal "
            "minimum, since M4-G4 itself fully computed this arm at all three c). specificity_weight_floor "
            "anchored at all three c too -- an ADDITIONAL disclosed anchor beyond the task's three named ones, "
            "required by this leg's adopted reading of 'carried over from M4-G4' (Part 0.6)."
        ),
    }

    author_truth = g4._author_level_truth_with_c(truth_rows)  # unchanged, reused

    # ---- G0 POWER (author grain, vs M4-G4's persisted effects) ---------------
    g0_probe_rows = []
    for arm in NEW_ARMS:
        check = g4._c_invariance_check(author_truth, arm, valid_worlds)  # unchanged, reused
        for r in check["rows"]:
            g0_probe_rows.append({**r, "check": "lean_a_c_invariance"})
    for arm in NEW_ARMS:
        check = g4._no_loss_check(author_truth, arm, valid_worlds)  # unchanged, reused
        for r in check["rows"]:
            g0_probe_rows.append({**r, "check": "lean_b_no_loss"})
    specificity_check = g4._c_invariance_check(author_truth, "specificity_weight_floor", valid_worlds)  # unchanged, reused
    for r in specificity_check["rows"]:
        g0_probe_rows.append({**r, "check": "lean_c_specificity_control_confirmation"})
    g0_df = pd.DataFrame(g0_probe_rows)
    g0_underpowered_n = int(g0_df["author_underpowered_vs_g0_bar"].sum())
    g4_decision_path = ROOT / "results" / "m4_g4_covariant_ridge" / "decision.json"
    with g4_decision_path.open("r", encoding="utf-8") as handle:
        m4g4_decision = json.load(handle)
    g4_author_c4_gain = m4g4_decision["gates"]["G0_power"]["m4g3_author_c4_gain_by_budget"]
    g0 = {
        "statement": (
            "AUTHOR-grain (n up to 745) CI half-width vs bar=0.01, reused verbatim from M4-G4's own "
            "'half of the ±0.02 leaning margin' convention (g4.G0_FRACTION_BAR). Also reported against "
            "M4-G3's persisted author-level c=4 gain (0.0591@4x/0.0683@8x, same reference M4-G4 used) "
            "for continuity across the line; the absolute ±0.01 reading is ADOPTED (matches g4's own "
            "adoption reasoning: this leg's own leans are stated in absolute, not %-of-gain, terms)."
        ),
        "bar_absolute": g4.G0_FRACTION_BAR,
        "m4g3_author_c4_gain_by_budget": g4_author_c4_gain,
        "n_comparisons": int(len(g0_df)),
        "n_underpowered_vs_absolute_bar": g0_underpowered_n,
        "half_width_min": float(g0_df["author_half_width"].min()),
        "half_width_max": float(g0_df["author_half_width"].max()),
        "half_width_median": float(g0_df["author_half_width"].median()),
        "all_comparisons": g0_probe_rows,
    }

    # ---- G2 COLUMN-SCALE LIVENESS (before/after spreads, from the inventory
    # stage's own evidence file, aggregated here) ------------------------------
    spread_path = output / "g2_column_scale_spread_evidence.csv"
    g2_spread_df = pd.read_csv(spread_path)
    g2_liveness_rows = []
    for c in C_LADDER:
        scoped = g2_spread_df[g2_spread_df["c"] == c]
        before = float(scoped["design_var_spread_before"].mean())
        after_std = float(scoped["design_var_spread_after_column_standardized"].mean())
        after_ridge = float(scoped["ridge_spread_after_diagonal_ridge"].mean())
        std_reduction_ratio = after_std / before if before else float("nan")
        std_live = bool(std_reduction_ratio <= 0.10)  # AFTER spread <= 10% of BEFORE spread: materially reduced
        ridge_live = bool(after_ridge > 1.10)  # ridge departs from the deployed-uniform 1.0 by >10%
        g2_liveness_rows.append(
            {
                "c": c, "mean_design_var_spread_before": before,
                "mean_design_var_spread_after_column_standardized": after_std,
                "column_standardized_reduction_ratio": std_reduction_ratio,
                "column_standardized_status": "LIVE" if std_live else "INERT/VACUOUS",
                "mean_ridge_spread_before_deployed_uniform": 1.0,
                "mean_ridge_spread_after_diagonal_ridge": after_ridge,
                "diagonal_ridge_status": "LIVE" if ridge_live else "INERT/VACUOUS",
            }
        )
    g2_liveness = {
        "materiality_margin": "column_standardized: AFTER design-variance spread <= 10% of BEFORE (materially reduced); diagonal_ridge: AFTER ridge-value spread departs from the deployed-uniform 1.0 by more than 10% (registered here, reusing this line's own 10%-relative-change materiality convention, e.g. g1.G2_CONDITION_MATERIALITY_RATIO / g4's own G2 'ratio departs from 1.0 by >10%' rule)",
        "per_c": g2_liveness_rows,
        "raw_evidence_file": "g2_column_scale_spread_evidence.csv",
    }

    # ---- leans -----------------------------------------------------------------
    lean_a_by_arm = {arm: g4._c_invariance_check(author_truth, arm, valid_worlds) for arm in NEW_ARMS}  # unchanged, reused
    lean_a_held_arms = [arm for arm, chk in lean_a_by_arm.items() if chk["held"]]
    lean_a_any_held = bool(len(lean_a_held_arms) > 0)
    lean_a_any_underpowered = bool(any(chk["status"] == "UNDERPOWERED" for chk in lean_a_by_arm.values()))
    lean_a_all_clean_miss = bool(all(chk["status"] == "MISS" for chk in lean_a_by_arm.values()))

    lean_b_by_arm_all = {arm: g4._no_loss_check(author_truth, arm, valid_worlds) for arm in NEW_ARMS}  # unchanged, reused
    lean_b_by_arm = {arm: lean_b_by_arm_all[arm] for arm in lean_a_held_arms}

    lean_c_control_check = g4._c_invariance_check(author_truth, "specificity_weight_floor", valid_worlds)  # unchanged, reused
    lean_c_control_confirmed = bool(lean_c_control_check["status"] == "MISS")

    # ---- lean (c) proper: QUANTITATIVE IMPROVEMENT vs M4-G4's own 10.9% ------
    def _swing(arm: str, budget: float) -> float:
        rows = lean_a_by_arm.get(arm, {}).get("rows") if arm in lean_a_by_arm else None
        if rows is None:
            rows = g4._c_invariance_check(author_truth, arm, valid_worlds)["rows"]
        for r in rows:
            if r["c_lo"] == 0.25 and r["c_hi"] == 4.0 and r["budget"] == budget:
                return abs(r["author_mean_diff"])
        raise RuntimeError(f"no 0.25-vs-4.0 row for {arm} budget {budget}")

    m4g4_residual_fraction = {}
    for row in m4g4_decision["gates"]["G0_power"]["all_comparisons"]:
        if row.get("c_lo") == 0.25 and row.get("c_hi") == 4.0 and row["arm"] == "covariant_var":
            budget = row["budget"]
            control_swing_row = next(
                r for r in m4g4_decision["gates"]["G0_power"]["all_comparisons"]
                if r.get("c_lo") == 0.25 and r.get("c_hi") == 4.0 and r["arm"] == "specificity_weight_floor" and r["budget"] == budget
            )
            m4g4_residual_fraction[budget] = abs(row["author_mean_diff"]) / abs(control_swing_row["author_mean_diff"])

    control_swing = {budget: _swing("specificity_weight_floor", budget) for budget in TRUTH_BUDGETS}
    lean_c_quant = {}
    for arm in NEW_ARMS:
        per_budget = {}
        for budget in TRUTH_BUDGETS:
            my_swing = _swing(arm, budget)
            my_fraction = my_swing / control_swing[budget] if control_swing[budget] else float("nan")
            per_budget[budget] = {
                "my_swing_c025_vs_c4": my_swing,
                "control_swing_c025_vs_c4": control_swing[budget],
                "my_residual_fraction": my_fraction,
                "m4g4_residual_fraction": m4g4_residual_fraction.get(budget),
                "improves_on_m4g4": bool(my_fraction < m4g4_residual_fraction.get(budget, float("inf"))),
            }
        lean_c_quant[arm] = per_budget

    if lean_a_any_held:
        pivot_status = "DOES_NOT_FIRE"
    elif lean_a_any_underpowered:
        pivot_status = "UNDERPOWERED"
    elif lean_a_all_clean_miss:
        pivot_status = "FIRES"
    else:
        pivot_status = "AMBIGUOUS"
    pivot_fires = bool(pivot_status == "FIRES")

    certified_arms = [
        arm for arm in lean_a_held_arms
        if lean_b_by_arm.get(arm, {}).get("held")
        and lean_c_control_confirmed
        and all(lean_c_quant[arm][b]["improves_on_m4g4"] for b in TRUTH_BUDGETS)
    ]
    if certified_arms:
        verdict = "CERTIFIED_REPAIR"
    elif lean_a_any_held:
        verdict = "C_INVARIANT_BUT_LOSSY_OR_NOT_IMPROVED"
    elif pivot_fires:
        verdict = "PIVOT_HETEROGENEITY_NOT_CONFINED_TO_COLUMNS"
    elif pivot_status == "UNDERPOWERED":
        verdict = "UNDERPOWERED_NO_ADJUDICATION_AT_REGISTERED_GRAIN"
    else:
        verdict = "AMBIGUOUS_NO_CLEAN_BRANCH"

    decision = {
        "estimand_id": "SUICA_M4_G5_PER_COLUMN_RIDGE",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md M4-G5 registration (2026-08-03, BEFORE run); ledger row M4-G5",
        "worlds": worlds,
        "valid_truth_worlds": valid_worlds,
        "arm_names": list(MY_ARM_NAMES),
        "c_ladder": list(C_LADDER),
        "truth_budgets": list(TRUTH_BUDGETS),
        "gates": {
            "G0_power": g0,
            "G1_anchor": g1_anchor,
            "G2_column_scale_liveness": g2_liveness,
            "G3_truth_path_invariance": g3_gate,
        },
        "structural_checks": {
            "recomputed_valid_worlds": recomputed_valid_worlds,
            "valid_world_subset_reproduced_from_m4g4": valid_world_subset_reproduced,
        },
        "lean_a_completion": {
            "per_arm": lean_a_by_arm,
            "held_arms": lean_a_held_arms,
            "any_held": lean_a_any_held,
            "any_underpowered": lean_a_any_underpowered,
            "all_clean_miss": lean_a_all_clean_miss,
        },
        "lean_b_no_loss": {
            "per_arm": lean_b_by_arm,
            "evaluated_for": lean_a_held_arms,
            "disclosed_companion_all_new_arms_regardless_of_lean_a": lean_b_by_arm_all,
        },
        "lean_c_quantitative_improvement": {
            "specificity_control_confirmation": {"check": lean_c_control_check, "confirmed": lean_c_control_confirmed},
            "residual_vs_m4g4": lean_c_quant,
        },
        "pivot": {
            "registered": "no per-column arm achieves c-invariance -> heterogeneity not confined to design columns",
            "fires": pivot_fires,
            "status": pivot_status,
        },
        "certified_arms": certified_arms,
        "verdict": verdict,
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only (8 D1 worlds, reused verbatim from M4-G2/G3/G4); "
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

    print(
        json.dumps(
            {
                "verdict": verdict, "pivot_status": pivot_status, "pivot_fires": pivot_fires,
                "lean_a_held_arms": lean_a_held_arms, "lean_a_any_held": lean_a_any_held,
                "lean_a_any_underpowered": lean_a_any_underpowered,
                "lean_b_held": {arm: chk.get("held") for arm, chk in lean_b_by_arm.items()},
                "lean_c_control_confirmed": lean_c_control_confirmed,
                "certified_arms": certified_arms,
                "g1_anchor_pass": g1_anchor["pass"], "g3_pass": g3_gate["pass"],
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
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_g5_per_column_ridge")
    parser.add_argument("--world", type=str, default=None)
    parser.add_argument("--stage", type=str, choices=("inventory", "truth"), default=None)
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

    if args.stage == "inventory":
        _run_inventory(config, spec, args.output)
        return

    if args.world is None:
        raise SystemExit("--world is required for --stage truth")
    if args.world not in D1_WORLDS:
        raise SystemExit(f"not a registered D1 world: {args.world}")
    _run_truth_stage(args.world, config, spec, args.output)


if __name__ == "__main__":
    main()
