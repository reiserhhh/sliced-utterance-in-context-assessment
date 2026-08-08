#!/usr/bin/env python3
"""M4-G3: scale-adaptive constants -- can the c-dependence M4-G2 found be
localized in identifiable absolute constants, and does making them relative
to a data-scale statistic deliver the c=4 truth-recovery gain at c=1?

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-G3
registration" (2026-08-03, BEFORE run); ledger row M4-G3). Machinery is
IMPORTED and REUSED, not reimplemented: M4-G1/M4-G2's world set, context
builder (`g1._build_world_contexts`), whitening-scale construction
(`g2._whitening_for_c`), CI helpers (`g1._paired_world_ci`,
`g1._paired_author_ci`), aggregation helpers (`g1._author_level_truth`), the
valid-world-subset rule (M4-G2's lean (b) numerical-validity diagnostic), and
every persisted anchor. The ONLY new code is (i) six PARAMETERIZED
near-duplicates of estimator internals that currently hard-code an absolute
constant (`_fit_logistic_adaptive`, `_hazard_probability_adaptive`,
`_feedback_derivative_adaptive`, `_fit_hazard_candidate_adaptive`,
`_forced_route_derivative_adaptive`, `_bases_from_whitening_adaptive`) --
each is a disclosed structural near-duplicate of an unchanged original
(file+line cited at each definition, mirroring M4-G1/M4-G2's own precedent of
writing a disclosed near-duplicate when the original does not expose what a
leg needs) -- and (ii) this leg's own arm-resolution / gate / lean bookkeeping.

THE QUESTION (M4-G2's planner adjudication note). M4-G2 proved something
downstream of the whitening compares a scale-carrying quantity against a
fixed absolute constant: a PURE change of whitening units (eigenvectors,
relative spectrum, condition number, width all invariant at exactly 0.0)
nonetheless moved truth recovery monotonically, .786 (c=.25) -> .422 (c=4).
This leg's Part 0 (below) enumerates every candidate constant, then tests
whether making each one relative -- alone, and all six together -- at c=1.0
reproduces c=4's gain without moving c at all.

===========================================================================
PART 0 -- REGISTERED CONSTANT INVENTORY (gated: written and frozen BEFORE
any adaptive-arm compute; the diagnostic numbers cited below were measured
from M4-G2's ALREADY-persisted artifacts, or from a single sample context's
`ingredients` dict via the UNCHANGED `leg10._freeze_ingredients` -- neither
is a hypothesis-relevant number for THIS leg's leans, both are cited with
their own provenance).
===========================================================================

Every function reachable from an ARM's basis is enumerated below by walking
the exact call graph M4-G1/M4-G2 use for a c-arm's basis:
  g2._whitening_for_c -> leg10._bases_from_whitening -> {
      OFFSET path:  leg9._row_norm_swap -> leg11._stack_frame ->
                     leg14._frechet_mean_multistart/_gpa_mean/_quotient_distance
      TRUTH path:   leg4._forced_route_derivative ->
                     estimator._fit_hazard_candidate -> estimator._hazard_design /
                     estimator._fit_logistic -> estimator._feedback_derivative ->
                     estimator._hazard_probability -> estimator._hazard_design
  }
and leg3._relative_error (both paths, compares the arm's output to the
world's fixed analytic D_true, itself never touched by c or by any arm).

--- CATEGORY A: constants on the TRUTH-RECOVERY call graph (scored; each
    gets its own `adaptive_<k>` arm) --------------------------------------

A1. `hazard_ridge` -- regularizer.
    File: suica_core/m4_chart_ecology_estimator.py:341-342 (`_fit_logistic`):
        penalty = ridge * len(y) * np.eye(design.shape[1])
        penalty[0, 0] = 0.0
    Deployed value: 0.005 (configs/m4_chart_ecology.json ->
    route_estimator.hazard_ridge). `ridge*n*I` is ADDED directly to
    `design.T @ diag(weight) @ design` (the fit's information/Gram matrix).
    The Gram matrix's "condition_*"/"feedback_*" blocks scale with the
    SQUARE of whatever multiplier the whitening applies to those design
    columns (verified empirically below: whitened columns have ~unit
    variance at baseline BY CONSTRUCTION of whitening, so this is not
    academic -- it is the exact mechanism by which the SAME fixed `ridge*n`
    becomes relatively weaker as the whitening is scaled up). This is a
    provable, not merely suspected, reparameterization-invariance breaker:
    for a DIAGONAL rescaling of covariates (which is exactly what c does --
    see M4-G2's own G2 report, eigenvectors/relative-spectrum/condition-
    number/width all invariant), UNREGULARIZED weighted least squares is
    EXACTLY invariant (coefficient compensates 1:1), but an L2 penalty of
    the form `ridge*n*I` is NOT (the well-known reason ridge/lasso
    implementations standardize features first). Ridge is the single
    strongest a priori candidate in this inventory.

A2. IRLS convergence tolerance -- convergence tolerance.
    File: suica_core/m4_chart_ecology_estimator.py:357 (`_fit_logistic`):
        if np.max(np.abs(updated - coefficient)) < 1e-10:
    An ABSOLUTE bound compared against the raw magnitude of an IRLS
    coefficient UPDATE. Under a compensating reparameterization, updates to
    the coefficients associated with the scaled design blocks shrink as the
    whitening is scaled up; a fixed absolute bar is therefore an
    inconsistent RELATIVE precision target across whitening scales.

A3. IRLS weight floor -- floor.
    File: suica_core/m4_chart_ecology_estimator.py:348 (`_fit_logistic`):
        weight = np.clip(fitted * (1.0 - fitted), 1e-4, None)
    `fitted` is a probability (bounded in [0,1] regardless of design scale
    by the sigmoid), so this floor's bindingness is a SECOND-ORDER
    consequence of how extreme the fit becomes -- included because it
    literally floors a quantity fed by a scale-carrying design, disclosed
    with lower prior confidence than A1.

A4. Logit clip bound -- clip bound.
    File: suica_core/m4_chart_ecology_estimator.py:347 (`_fit_logistic`,
    inside the IRLS loop) AND :438 (`_hazard_probability`, the post-fit
    readout used by `_feedback_derivative`):
        expit(np.clip(design @ coefficient, -20.0, 20.0))
    One literal constant (20.0), two call sites, treated as ONE inventoried
    item (same role, same numeric value). `design @ coefficient` is the
    fitted logit -- under the clean, ridge=0 argument above it would be
    EXACTLY c-invariant, so this clip is a second-order effect (only bites
    once A1/A2 already perturb the fit toward more extreme logits) --
    included for completeness and tested, disclosed as the weakest a priori
    candidate together with A3.

A5. Finite-difference probe epsilon in `_feedback_derivative` -- epsilon
    guard (probe-step variant).
    File: suica_core/m4_chart_ecology_estimator.py:531
    (`_feedback_derivative(..., epsilon: float = 0.05)`), consumed via
    `leg4._forced_route_derivative`
    (scripts/run_suica_m4_d_dleg_floor_leg4.py:441-447 -- calls
    `_feedback_derivative(fit[0], fit[1], basis["evaluation"], dimensions)`
    with NO explicit `epsilon=`, i.e. the arm's estimated derivative always
    uses this literal 0.05 default). The "feedback" design block is
    `einsum("kp,nd->nkpd", basis, response_next)` (estimator.py:311-315) --
    LINEAR in the probe `response_next`, whose magnitude is exactly this
    epsilon; since `basis` carries the whitening's scale, the LOGIT SWING
    PER UNIT EPSILON grows with that scale, so a fixed epsilon probes an
    increasingly large (or small) logit range as the design's own natural
    scale changes. Weaker/more indirect channel than A1; disclosed as such.
    (Coincidentally equal, as a bare number, to `leg4.PROBE_EPSILON`, the
    SEPARATE constant used to build the world's fixed analytic D_true --
    that usage is NOT on the arm-dependent path (D_true never touches an
    arm's basis) and is excluded below.)

A6. Basis intercept constant -- "added to" a scale-carrying quantity.
    File: scripts/run_suica_m4_d_direction_anatomy_leg10.py:356
    (`_bases_from_whitening`):
        bases[role] = np.column_stack([np.ones(len(raw)), whitened])
    The literal `1` is concatenated as the basis's own leading column
    beside `whitened = (raw-center) @ whitening`, which carries the arm's
    full scale (c multiplies `whitening` in `g2._whitening_for_c`). A
    disciplined, provable objection is on record against this one (see
    "Analytical aside" below): UNregularized IRLS is exactly invariant to
    ANY diagonal rescaling of covariates, including one that leaves a
    single column fixed while scaling the rest, so this constant's own
    causal channel to TRUTH RECOVERY is expected, on that argument, to be
    materially weaker than A1's -- included and tested (not asserted
    inert), because the argument only holds in the idealized ridge=0
    limit and this leg's own A1 finding is that ridge is NOT zero here.

--- CATEGORY B: constants on the OFFSET/GPA call graph ONLY -- inventoried
    for completeness, PROVABLY excluded from the scored (truth-recovery)
    hypothesis space by direct call-graph inspection -----------------------

B1. `GPA_TOLERANCE = 1e-11` -- scripts/run_suica_m4_d_displacement_leg14.py:204,
    compared against `residual = ||updated-mean||` inside `_gpa_mean`
    (same file, ~line 335). `mean`/`updated` are GPA Frechet-mean frame
    stacks built from arm bases -- scale-carrying -- but this function is
    called ONLY from the OFFSET computation
    (`leg14._frechet_mean_multistart`, called by `_run_offset_gap_stage` in
    both g1.py and g2.py); `_run_truth_stage`/`_truth_rows_for_context_c`
    never import or call `_frechet_mean_multistart`, `_gpa_mean`,
    `_quotient_distance`, `leg9._row_norm_swap`, or `leg11._stack_frame` at
    all. Zero causal channel to this leg's scored outcome (truth recovery)
    is therefore a call-graph FACT, not merely an empirical expectation --
    strictly stronger evidence than a G2 perturbation could supply, so no
    adaptive arm is built for it (an arm would necessarily reproduce
    baseline's truth-recovery rows bit-for-bit, since nothing on the
    truth-recovery path would change).

B2. `BASIN_RESOLUTION = 1e-6` -- scripts/run_suica_m4_d_displacement_leg14.py:206,
    compared against `_quotient_distance(run["mean"], representative)`
    inside `_frechet_mean_multistart` (~line 375). Same exclusion as B1
    (offset-diagnostic-only call graph; additionally this constant does not
    even affect the ADOPTED GPA mean/offset value, only the disclosed
    `n_distinct_basins` bookkeeping count).

--- CONSIDERED AND EXCLUDED: not scale-carrying w.r.t. c, or not itself a
    magnitude-bearing comparator, or outside the reused call graph --------

- `rank_tolerance=1e-6`, `maximum_rank=12` (leg10._freeze_ingredients,
  ~lines 300-304): determine `retained` from the RAW covariance
  eigenvalues, entirely UPSTREAM of c (c only multiplies the OUTPUT of
  `_whitening_with_lambda`, never touches which directions are retained).
- `1e-12` floor inside `leg10._whitening_with_lambda` (line 334,
  `np.sqrt(np.maximum(eigenvalues[retained] + lam, 1e-12))`): protects the
  RAW eigenvalues (lam=0 always on this leg's arms), upstream of c.
- `1e-12` floor(s) inside `leg9._row_norm_swap` (line 1106,
  `s_dir > 1e-12`, `np.maximum(s_dir, 1e-12)`): `s_dir` is the ORACLE
  basis's own row norm (`direction_basis=truth.oracle_basis` at every call
  site in g1.py/g2.py) -- c-invariant, not the arm's own (scale-carrying)
  row norm `s_norm`, which this function never floors. Also offset-path-only.
- `logistic_iterations=30` (config `route_estimator.logistic_iterations`):
  an iteration COUNT, not itself compared against/added to/thresholding a
  scale-carrying quantity (its INTERACTION with A2's tolerance is disclosed
  under A2; the count itself is not separately scored).
- `penalty[0, 0] = 0.0` (estimator.py:342): a structural exemption (zeroing
  one matrix entry), not a magnitude with a "relative" form to test.
- Laplace-smoothing constants `0.5`, `1.0` in `_fit_logistic`'s intercept
  init (estimator.py:344, `(np.sum(y)+0.5)/(len(y)+1.0)`): operate on `y`,
  the binary observed-outcome target -- never touched by c or by any arm.
- `np.tanh(rows["duration"]/4.0)`'s `4.0`, and the `history[:,0] > 0.0` gate
  threshold (estimator.py:307, 318, inside `_hazard_design`): operate on
  RAW world data (duration/history), never touched by c or by any arm.
- `GPA_MAX_ITERATIONS = 50000` (leg14.py:205): an iteration cap, not itself
  a comparator against a scale-carrying quantity; also offset-path-only.
- `EXPONENT_ANCHOR_TOLERANCE = 5e-4` (leg14.py:207): belongs to a DIFFERENT
  leg-14 function (`_leg11_exponent_recompute`-style checking), never
  imported or called by g1.py/g2.py's reused call graph at all.

--- ANALYTICAL ASIDE (registered before compute; explains the Category A
    formulas below, does not itself score anything) -----------------------

Empirical check on ONE sample context (world=endogenous_creation_expansion,
rep=0, k_retained=12): raw retained eigenvalues range 2.6e-6 to 0.295,
mean(eigenvalues[retained]) = 0.0486, geometric-mean SCALE FACTOR
(1/sqrt(eig), M4-G2's own `geometric_mean_scale` statistic) = 28.43 -- but
the WHITENED design columns this scale factor produces have empirical
variance ~0.79-2.48 per column (overall ~0.84-1.48 across the three roles),
i.e. close to the UNIT variance whitening is mathematically defined to
produce (variance = eigenvalue * (1/sqrt(eigenvalue))^2 = 1, exactly, up to
finite-sample/out-of-distribution noise). This means the whitening's own
per-direction SCALE FACTOR (M4-G2's `geometric_mean_scale`) is NOT a
measure of the resulting feature's magnitude (it is the reciprocal
normalization that PRODUCES unit magnitude) -- so it is the wrong
denominator for a "how big is the design, relative to what ridge/tolerance/
floor/clip/epsilon assume" statistic, and using it (an earlier draft of
this Part 0 did) would have grossly overcorrected. The RAW, PRE-WHITENING
eigenvalue scale is the right one: it measures how far the deployed
constants' implicit assumption of "the design already has unit variance" is
from being true. This is not a new idea in this codebase --
`leg10._freeze_ingredients`'s OWN Arm A (Leg 10's "de-biased discovery"
Tikhonov lever, scripts/run_suica_m4_d_direction_anatomy_leg10.py:309-311)
already computes `lambda_chart = trace(covariance)/p_features/n_reference_rows`,
a closely related raw-covariance-scale statistic, as the natural reference
for a DIFFERENT regularizer in this exact pipeline -- precedent for "mean
raw retained eigenvalue" as a legitimate, already-used "data-scale
statistic" in this codebase, not an invention specific to this leg.

DECLARED DATA-SCALE STATISTIC (registered, used by every Category A arm):
    RAW_SCALE(context) := mean(ingredients["eigenvalues"][ingredients["retained"]])
computed once per (world, repetition) from the UNCHANGED
`leg10._freeze_ingredients` output -- identical regardless of c (upstream of
the whitening entirely) and identical regardless of which Category A
constant is being adapted (none of the six touch the eigendecomposition).

ADOPTED ADAPTIVE FORMULAS (registered; each holds every OTHER Category A
constant, and c, at its deployed/baseline value -- "one arm per inventoried
constant"):
    A1 ridge:      ridge_adaptive      = hazard_ridge_deployed * RAW_SCALE
    A2 tolerance:  switch to a RELATIVE stopping rule,
                   || updated - coefficient ||_inf < 1e-10 * max(1, ||coefficient||_inf)
                   (the standard numerical-methods fix for an absolute
                   tolerance on an iterate of unknown scale; does not need
                   RAW_SCALE, is self-normalizing by construction)
    A3 weight floor: floor_adaptive   = 1e-4 * RAW_SCALE
    A4 clip bound:   bound_adaptive   = 20.0 / RAW_SCALE
    A5 probe epsilon: epsilon_adaptive = 0.05 * RAW_SCALE
    A6 intercept:    value_adaptive   = 1.0 / sqrt(RAW_SCALE)
adaptive_all applies all six simultaneously.

Direction check (disclosed, computed from M4-G2's OWN persisted anchor
before any adaptive-arm compute, NOT tuned to it): reproducing the c=4
ladder point's effective ridge-to-information ratio EXACTLY at c=1 would
require ridge_deployed/16 = 0.0003125 (derived below in the report from a
one-coefficient ridge-regression toy model: `ridge_effective(c) =
ridge_used(c)/c^2`, so matching c=4's naturally-weaker effective ridge at
c=1 needs ridge_used(1) = ridge_deployed/4^2). A1's formula, evaluated on
the ONE sampled context above, gives 0.005*0.0486 = 0.000243 -- same order
of magnitude as 0.0003125, a pre-registered plausibility check (not a
tuned match; A1's formula never references "4" or "c=4" anywhere).

===========================================================================
DESIGN (registered)
===========================================================================
Reuse M4-G2's 8 worlds (`g2.D1_WORLDS`) and objective path verbatim.
  baseline        -- c=1.0, all six constants at deployed value (anchor).
  c4_reference    -- c=4.0, all six constants at deployed value (anchor;
                     must reproduce M4-G2's persisted c=4 recovery <=1e-12).
  adaptive_<A1..A6> -- one arm per Category A constant, that constant alone
                     adaptive, c=1.0, every other constant deployed.
  adaptive_all    -- all six Category A constants adaptive simultaneously, c=1.0.
9 arms total. Both truth budgets (4x, 8x), unchanged from M4-G1/M4-G2.
M4-G2's valid-6-world subset (excludes linear_null_ecology,
fast_return_equal_marginal -- the pre-existing `_relative_error` near-zero-
denominator fragility, unrelated to any manipulation in this leg) is reused
VERBATIM for every truth-recovery statistic; this leg's own arm-invariant
`e_orc_true` diagnostic (identical construction, identical deployed
hazard_ridge, computed once per (context,budget,view,author) and copied into
every arm's row, exactly as in g1.py/g2.py) is recomputed and cross-checked
against the same threshold to confirm the same two worlds are invalid here
too (a structural certainty, since e_orc_true never touches an arm's basis
or any Category A constant -- verified, not merely assumed, below).

OFFSET (GPA) is computed for exactly 4 arms: baseline, c4_reference (both
needed for G1 ANCHOR), adaptive_intercept, and adaptive_all (the only two
arms whose BASIS -- hence whose GPA offset -- can possibly differ from
baseline's, since A1-A5 never touch `_bases_from_whitening` at all; this is
verified structurally below, not merely assumed, by a bit-exact basis
comparison for every A1-A5 arm during the truth stage). The other five
single-constant arms' offset is therefore IDENTICAL to baseline's by
construction and is reported as such (zero marginal GPA compute).

LEAN (c) MARGIN (registered here, Part 0): offset lives on baseline's own
O(5-15) native scale (M4-G1/M4-G2's own tables), not truth-error's [0,1]
scale, so lean (b)'s absolute +/-0.02 band would be a units mismatch if
reused for offset. The registered margin is instead a FRACTION of
baseline's own mean offset: +/-10%, reusing M4-G1's own G2 "10% relative
change" materiality convention
(scripts/run_suica_m4_g1_whitening_intervention.py:253,
`G2_CONDITION_MATERIALITY_RATIO`) rather than inventing a new number.

Chunked execution (this arc's standard workaround, unchanged convention):
`--world` + `--stage {truth, offset}` computes ONE (world, stage) partial;
`--world ... --stage winner_ladder --winner-arm NAME` (used only after the
truth-phase winner, if any, is known) computes that ONE arm's truth recovery
at c in {0.25, 4.0} for lean (b)'s definitional check; `--assemble` reads
every partial, cross-checks completeness, and adjudicates.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
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
import run_suica_m4_d_bias_variance_leg9 as leg9  # noqa: E402
import run_suica_m4_d_perturbation_leg11 as leg11  # noqa: E402
import run_suica_m4_d_displacement_leg14 as leg14  # noqa: E402
import run_suica_m4_g1_whitening_intervention as g1  # noqa: E402
import run_suica_m4_g2_metric_units as g2  # noqa: E402  the leg this extends

from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    _hazard_design,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    _candidate_features,
)

ROLES = leg11.ROLES
FLIP_TOLERANCE = leg4.FLIP_TOLERANCE
D1_WORLDS = g2.D1_WORLDS  # 8 worlds, reused verbatim
TRUTH_BUDGETS = g1.TRUTH_BUDGETS  # (4.0, 8.0), reused verbatim
VALID_TRUTH_WORLDS = (  # M4-G2's lean (b) adopted valid-subset rule, reused verbatim
    "condition_alias_ecology",
    "endogenous_creation_expansion",
    "history_gated_ecology",
    "selection_creation_compensation",
    "source_rotated_feedback",
    "topology_mismatch",
)
TRUTH_VALIDITY_THRESHOLD = 10.0  # M4-G2's own threshold, reused verbatim
assert set(VALID_TRUTH_WORLDS) <= set(D1_WORLDS)
assert len(VALID_TRUTH_WORLDS) == 6

DEPLOYED_RIDGE_CONFIG_PATH = "route_estimator.hazard_ridge"
DEPLOYED_WEIGHT_FLOOR = 1e-4
DEPLOYED_CLIP_BOUND = 20.0
DEPLOYED_TOL_VALUE = 1e-10
DEPLOYED_PROBE_EPSILON = 0.05
DEPLOYED_INTERCEPT = 1.0
assert DEPLOYED_PROBE_EPSILON == leg4.PROBE_EPSILON  # disclosed consistency check, Category A5
RAW_SCALE_FLOOR = 1e-12  # purely defensive (div-by-zero / overflow guard); not scored

G1_ANCHOR_TOLERANCE = 1e-12
G3_TOLERANCE = 1e-12
LEAN_A_FRACTION_BAR = 0.5
LEAN_B_MARGIN = 0.02  # reused from M4-G1/M4-G2's own convention
LEAN_C_MARGIN_FRACTION = 0.10  # registered here (Part 0): offset lives on baseline's own
                                # O(5-15) scale, not truth-error's [0,1] scale, so the
                                # margin is a FRACTION of baseline's own mean offset,
                                # reusing M4-G1's G2 "10% relative change" materiality
                                # convention (scripts/run_suica_m4_g1_whitening_intervention.py:253,
                                # G2_CONDITION_MATERIALITY_RATIO) rather than lean (b)'s
                                # absolute 0.02 (which is calibrated for truth error's
                                # [0,1] scale and would be a units mismatch here).
G2_LIVENESS_MARGIN = 0.02  # reused; "moves" = paired CI outside this band at BOTH budgets
G0_FRACTION_BAR = 0.25  # half of lean (a)'s 50% bar, matching this line's own "half the
                         # actionability threshold" convention (M4-G1: half of 25%;
                         # M4-G2: half the slope 0-vs-1 gap)

ARM_NAMES = (
    "baseline",
    "c4_reference",
    "adaptive_hazard_ridge",
    "adaptive_tolerance",
    "adaptive_weight_floor",
    "adaptive_clip_bound",
    "adaptive_probe_epsilon",
    "adaptive_intercept",
    "adaptive_all",
)
SINGLE_CONSTANT_ARMS = (
    "adaptive_hazard_ridge",
    "adaptive_tolerance",
    "adaptive_weight_floor",
    "adaptive_clip_bound",
    "adaptive_probe_epsilon",
    "adaptive_intercept",
)
CATEGORY_A_CONSTANTS = (
    "hazard_ridge",
    "tolerance",
    "weight_floor",
    "clip_bound",
    "probe_epsilon",
    "intercept",
)
ARM_OF_CONSTANT = dict(zip(CATEGORY_A_CONSTANTS, SINGLE_CONSTANT_ARMS))
ARM_C = {name: (4.0 if name == "c4_reference" else 1.0) for name in ARM_NAMES}
BASIS_IDENTICAL_TO_BASELINE_ARMS = (  # structural fact, verified not assumed (see G3-ish check)
    "adaptive_hazard_ridge",
    "adaptive_tolerance",
    "adaptive_weight_floor",
    "adaptive_clip_bound",
    "adaptive_probe_epsilon",
)
OFFSET_ARMS = ("baseline", "c4_reference", "adaptive_intercept", "adaptive_all")


@dataclass(frozen=True)
class ArmConstants:
    ridge: str = "deployed"
    tol_mode: str = "deployed"
    weight_floor: str = "deployed"
    clip_bound: str = "deployed"
    probe_epsilon: str = "deployed"
    intercept: str = "deployed"


ARM_SPECS: dict[str, ArmConstants] = {
    "baseline": ArmConstants(),
    "c4_reference": ArmConstants(),
    "adaptive_hazard_ridge": ArmConstants(ridge="adaptive"),
    "adaptive_tolerance": ArmConstants(tol_mode="adaptive"),
    "adaptive_weight_floor": ArmConstants(weight_floor="adaptive"),
    "adaptive_clip_bound": ArmConstants(clip_bound="adaptive"),
    "adaptive_probe_epsilon": ArmConstants(probe_epsilon="adaptive"),
    "adaptive_intercept": ArmConstants(intercept="adaptive"),
    "adaptive_all": ArmConstants(
        ridge="adaptive",
        tol_mode="adaptive",
        weight_floor="adaptive",
        clip_bound="adaptive",
        probe_epsilon="adaptive",
        intercept="adaptive",
    ),
}


def _resolve_constants(
    spec: ArmConstants, raw_scale: float, deployed_ridge: float
) -> dict[str, Any]:
    rs = max(float(raw_scale), RAW_SCALE_FLOOR)
    ridge = deployed_ridge * rs if spec.ridge == "adaptive" else deployed_ridge
    weight_floor = DEPLOYED_WEIGHT_FLOOR * rs if spec.weight_floor == "adaptive" else DEPLOYED_WEIGHT_FLOOR
    clip_bound = DEPLOYED_CLIP_BOUND / rs if spec.clip_bound == "adaptive" else DEPLOYED_CLIP_BOUND
    tol_mode = "relative" if spec.tol_mode == "adaptive" else "absolute"
    probe_epsilon = DEPLOYED_PROBE_EPSILON * rs if spec.probe_epsilon == "adaptive" else DEPLOYED_PROBE_EPSILON
    intercept = 1.0 / np.sqrt(rs) if spec.intercept == "adaptive" else DEPLOYED_INTERCEPT
    return {
        "raw_scale": raw_scale,
        "ridge": float(ridge),
        "weight_floor": float(weight_floor),
        "clip_bound": float(clip_bound),
        "tol_mode": tol_mode,
        "tol_value": DEPLOYED_TOL_VALUE,
        "probe_epsilon": float(probe_epsilon),
        "intercept": float(intercept),
    }


# ---------------------------------------------------------------------------
# Category A adaptive estimator internals -- disclosed, parameterized
# near-duplicates of the unchanged originals cited in each docstring.
# ---------------------------------------------------------------------------


def _bases_from_whitening_adaptive(
    context: dict[str, Any],
    ingredients: dict[str, Any],
    whitening: np.ndarray,
    *,
    intercept_value: float = DEPLOYED_INTERCEPT,
) -> dict[str, np.ndarray]:
    """Near-duplicate of leg10._bases_from_whitening (leg10.py:338-357),
    parameterized over the intercept column's constant value (A6). At
    intercept_value=1.0 this is bit-identical to the original."""
    condition = context["observed"].condition
    candidate = ingredients["candidate"]
    center = ingredients["center"]
    bases: dict[str, np.ndarray] = {}
    for role in ROLES:
        values = np.asarray(
            getattr(condition, f"mechanism_{role}").pre_context, dtype=float
        )
        if values.ndim == 4:
            values = np.mean(values, axis=1)
        raw = np.mean(_candidate_features(candidate, values), axis=0)
        whitened = (raw - center) @ whitening
        bases[role] = np.column_stack(
            [np.full(len(raw), float(intercept_value)), whitened]
        )
    return bases


def _fit_logistic_adaptive(
    design: np.ndarray,
    target: np.ndarray,
    *,
    ridge: float,
    iterations: int,
    weight_floor: float = DEPLOYED_WEIGHT_FLOOR,
    clip_bound: float = DEPLOYED_CLIP_BOUND,
    tol_mode: str = "absolute",
    tol_value: float = DEPLOYED_TOL_VALUE,
) -> np.ndarray:
    """Near-duplicate of estimator._fit_logistic
    (suica_core/m4_chart_ecology_estimator.py:333-361), parameterized over
    A1 (ridge), A2 (tol_mode/tol_value), A3 (weight_floor), A4 (clip_bound).
    At every parameter left "deployed" this is bit-identical to the
    original."""
    y = np.asarray(target, dtype=float).reshape(-1)
    penalty = ridge * len(y) * np.eye(design.shape[1])
    penalty[0, 0] = 0.0
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
        if tol_mode == "absolute":
            converged = step < tol_value
        else:
            converged = step < tol_value * max(1.0, float(np.max(np.abs(coefficient))))
        if converged:
            coefficient = updated
            break
        coefficient = updated
    return coefficient


def _fit_hazard_candidate_adaptive(
    datasets: list[tuple[dict[str, np.ndarray], np.ndarray]],
    *,
    model: str,
    ridge: float,
    iterations: int,
    weight_floor: float = DEPLOYED_WEIGHT_FLOOR,
    clip_bound: float = DEPLOYED_CLIP_BOUND,
    tol_mode: str = "absolute",
    tol_value: float = DEPLOYED_TOL_VALUE,
) -> tuple[np.ndarray, tuple[str, ...]]:
    """Near-duplicate of estimator._fit_hazard_candidate (estimator.py:378-407);
    `_hazard_design` itself is REUSED UNCHANGED (no Category A constant lives
    there)."""
    designs = []
    targets = []
    names: tuple[str, ...] | None = None
    for rows, basis in datasets:
        design, current_names = _hazard_design(rows, basis, model=model)  # unchanged
        designs.append(design)
        targets.append(rows["generated_next"].reshape(-1))
        names = current_names
    return (
        _fit_logistic_adaptive(
            np.vstack(designs),
            np.concatenate(targets),
            ridge=ridge,
            iterations=iterations,
            weight_floor=weight_floor,
            clip_bound=clip_bound,
            tol_mode=tol_mode,
            tol_value=tol_value,
        ),
        names or (),
    )


def _hazard_probability_adaptive(
    coefficient: np.ndarray,
    names: tuple[str, ...],
    basis: np.ndarray,
    response: np.ndarray,
    history_gate: np.ndarray,
    *,
    clip_bound: float = DEPLOYED_CLIP_BOUND,
) -> np.ndarray:
    """Near-duplicate of estimator._hazard_probability (estimator.py:410-441),
    parameterized over A4 (clip_bound)."""
    events = len(response)
    categories = len(basis)
    rows = {
        "choice": np.zeros(events, dtype=int),
        "response_next": np.asarray(response, dtype=float),
        "history": np.column_stack(
            [np.asarray(history_gate, dtype=float), np.zeros(events)]
        ),
        "generated": np.zeros((events, categories), dtype=bool),
        "duration": np.zeros((events, categories)),
    }
    model = (
        "gate"
        if any(name.startswith("gate_") for name in names)
        else "feedback"
        if any(name.startswith("feedback_") for name in names)
        else "return"
        if "generated_current" in names
        else "base"
    )
    design, _ = _hazard_design(rows, basis, model=model)  # unchanged
    return expit(np.clip(design @ coefficient, -clip_bound, clip_bound)).reshape(
        events, categories
    )


def _feedback_derivative_adaptive(
    coefficient: np.ndarray,
    names: tuple[str, ...],
    basis: np.ndarray,
    dimensions: int,
    *,
    epsilon: float = DEPLOYED_PROBE_EPSILON,
    clip_bound: float = DEPLOYED_CLIP_BOUND,
) -> np.ndarray:
    """Near-duplicate of estimator._feedback_derivative (estimator.py:525-555),
    parameterized over A5 (epsilon) and (threaded through) A4 (clip_bound)."""
    output = np.empty((len(basis), dimensions))
    for dimension in range(dimensions):
        positive = np.zeros((1, dimensions))
        negative = np.zeros((1, dimensions))
        positive[0, dimension] = epsilon
        negative[0, dimension] = -epsilon
        output[:, dimension] = (
            _hazard_probability_adaptive(
                coefficient, names, basis, positive, np.zeros(1), clip_bound=clip_bound
            )[0]
            - _hazard_probability_adaptive(
                coefficient, names, basis, negative, np.zeros(1), clip_bound=clip_bound
            )[0]
        ) / (2.0 * epsilon)
    return output


def _forced_route_derivative_adaptive(
    calibration: dict[str, np.ndarray],
    selection: dict[str, np.ndarray],
    basis: dict[str, np.ndarray],
    *,
    model: str,
    hazard_ridge: float,
    logistic_iterations: int,
    dimensions: int,
    weight_floor: float = DEPLOYED_WEIGHT_FLOOR,
    clip_bound: float = DEPLOYED_CLIP_BOUND,
    tol_mode: str = "absolute",
    tol_value: float = DEPLOYED_TOL_VALUE,
    probe_epsilon: float = DEPLOYED_PROBE_EPSILON,
) -> np.ndarray:
    """Near-duplicate of leg4._forced_route_derivative (leg4.py:412-436),
    threading every Category A parameter through."""
    fit = _fit_hazard_candidate_adaptive(
        [
            (calibration, basis["calibration"]),
            (selection, basis["selection"]),
        ],
        model=model,
        ridge=hazard_ridge,
        iterations=logistic_iterations,
        weight_floor=weight_floor,
        clip_bound=clip_bound,
        tol_mode=tol_mode,
        tol_value=tol_value,
    )
    return _feedback_derivative_adaptive(
        fit[0],
        fit[1],
        basis["evaluation"],
        dimensions,
        epsilon=probe_epsilon,
        clip_bound=clip_bound,
    )


# ---------------------------------------------------------------------------
# per-context arm setup
# ---------------------------------------------------------------------------


def _arm_bases_and_constants(
    contexts: list[dict[str, Any]],
) -> tuple[
    dict[str, list[dict[str, np.ndarray]]],
    list[dict[str, Any]],
]:
    """For every rep: build the two distinct bases (deployed intercept @ c=1,
    deployed intercept @ c=4, adaptive intercept @ c=1 -- the ONLY 3 distinct
    basis/whitening combinations across all 9 arms, since A1-A5 never touch
    _bases_from_whitening), and resolve every arm's Category A constants."""
    arm_bases: dict[str, list[dict[str, np.ndarray]]] = {name: [] for name in ARM_NAMES}
    per_rep_meta: list[dict[str, Any]] = []
    for context in contexts:
        ingredients = leg10._freeze_ingredients(context)
        raw_scale = float(np.mean(ingredients["eigenvalues"][ingredients["retained"]]))
        whitening_c1 = g2._whitening_for_c(ingredients, 1.0)
        whitening_c4 = g2._whitening_for_c(ingredients, 4.0)
        basis_c1_deployed = leg10._bases_from_whitening(context, ingredients, whitening_c1)  # unchanged
        basis_c4_deployed = leg10._bases_from_whitening(context, ingredients, whitening_c4)  # unchanged
        deployed_ridge = float(context["fit_kwargs"]["hazard_ridge"])
        resolved = {
            arm: _resolve_constants(ARM_SPECS[arm], raw_scale, deployed_ridge)
            for arm in ARM_NAMES
        }
        basis_c1_adaptive_intercept = _bases_from_whitening_adaptive(
            context, ingredients, whitening_c1, intercept_value=resolved["adaptive_intercept"]["intercept"]
        )
        # sanity: adaptive_all's intercept must equal adaptive_intercept's (same formula)
        assert resolved["adaptive_all"]["intercept"] == resolved["adaptive_intercept"]["intercept"]
        basis_lookup = {
            "baseline": basis_c1_deployed,
            "c4_reference": basis_c4_deployed,
            "adaptive_hazard_ridge": basis_c1_deployed,
            "adaptive_tolerance": basis_c1_deployed,
            "adaptive_weight_floor": basis_c1_deployed,
            "adaptive_clip_bound": basis_c1_deployed,
            "adaptive_probe_epsilon": basis_c1_deployed,
            "adaptive_intercept": basis_c1_adaptive_intercept,
            "adaptive_all": basis_c1_adaptive_intercept,
        }
        for arm in ARM_NAMES:
            arm_bases[arm].append(basis_lookup[arm])
        # structural verification (not assumption): every BASIS_IDENTICAL_TO_BASELINE
        # arm's basis must be bit-identical to baseline's, for every role.
        basis_identity_max = 0.0
        for arm in BASIS_IDENTICAL_TO_BASELINE_ARMS:
            for role in ROLES:
                diff = float(np.max(np.abs(basis_lookup[arm][role] - basis_lookup["baseline"][role])))
                basis_identity_max = max(basis_identity_max, diff)
        per_rep_meta.append(
            {
                "world": context["world"],
                "repetition": context["repetition"],
                "raw_scale": raw_scale,
                "k_retained": int(len(ingredients["retained"])),
                "deployed_ridge": deployed_ridge,
                "basis_identity_check_max_abs_diff": basis_identity_max,
                **{f"resolved_{arm}": json.dumps(resolved[arm], default=str) for arm in ARM_NAMES},
            }
        )
    return arm_bases, per_rep_meta


# ---------------------------------------------------------------------------
# stage: truth-referenced recovery (near-duplicate of g2._truth_rows_for_context_c,
# parameterized over ARM_NAMES's 9 arms + threaded Category A constants, plus
# an arm-invariant e_orc_true column computed via the UNCHANGED leg4._forced_route_derivative
# at deployed constants -- exactly g1.py/g2.py's own construction)
# ---------------------------------------------------------------------------


def _truth_rows_for_context(
    context: dict[str, Any],
    arm_bases_rep: dict[str, dict[str, np.ndarray]],
    resolved_rep: dict[str, dict[str, Any]],
    spec: M4ChartEcologySpec,
    budget: float,
    *,
    arms: tuple[str, ...] = ARM_NAMES,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    world = context["world"]
    repetition = context["repetition"]
    seed = context["seed"]
    truth = context["truth"]
    fit_kwargs = context["fit_kwargs"]
    dims = context["flat"][("train", 0)][0]["response_next"].shape[1]
    events_b = int(round(spec.events * budget))
    if budget == 1.0:
        observed_b = context["observed"]
        truth_b = truth
    else:
        spec_b = replace(spec, events=events_b)
        observed_b, truth_b = generate_m4_chart_ecology_world(world=world, spec=spec_b, seed=seed)
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
                "world": world,
                "repetition": repetition,
                "view": view,
                "author": author,
                "budget": budget,
                "events": events_b,
                "degenerate_reference": degenerate,
            }
            if degenerate:
                for arm in arms:
                    rows.append({**keys, "arm": arm, "c": ARM_C[arm], "e_arm_true": np.nan, "e_orc_true": np.nan})
                continue
            route = stack["selected_model"]
            calibration_b = leg4._flatten_events(calibration_panel, author)
            selection_b = leg4._flatten_events(selection_panel, author)
            n_cal_rows = len(calibration_b["choice"])
            n_sel_rows = len(selection_b["choice"])
            d_true = leg4._true_derivative(truth, author)
            # e_orc_true: arm-invariant, computed ONCE via the UNCHANGED estimator
            # path at DEPLOYED constants and the ORACLE basis -- identical
            # construction to g1.py/g2.py, never touches any arm's basis or any
            # Category A constant.
            d_orc_b = leg4._forced_route_derivative(
                calibration_b,
                selection_b,
                truth.oracle_basis,
                model=route,
                hazard_ridge=fit_kwargs["hazard_ridge"],
                logistic_iterations=fit_kwargs["logistic_iterations"],
                dimensions=dims,
            )
            e_orc_true = leg3._relative_error(d_orc_b, d_true)
            for arm in arms:
                basis = arm_bases_rep[arm]
                params = resolved_rep[arm]
                d_arm_b = _forced_route_derivative_adaptive(
                    calibration_b,
                    selection_b,
                    basis,
                    model=route,
                    hazard_ridge=params["ridge"],
                    logistic_iterations=fit_kwargs["logistic_iterations"],
                    dimensions=dims,
                    weight_floor=params["weight_floor"],
                    clip_bound=params["clip_bound"],
                    tol_mode=params["tol_mode"],
                    tol_value=params["tol_value"],
                    probe_epsilon=params["probe_epsilon"],
                )
                e_arm_true = leg3._relative_error(d_arm_b, d_true)
                rows.append(
                    {
                        **keys,
                        "arm": arm,
                        "c": ARM_C[arm],
                        "e_arm_true": e_arm_true,
                        "e_orc_true": e_orc_true,
                    }
                )
    gate = {
        "world": world,
        "repetition": repetition,
        "budget": budget,
        "events": events_b,
        "n_cal_rows_last": n_cal_rows,
        "n_sel_rows_last": n_sel_rows,
    }
    return rows, gate


def _run_truth_stage(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    contexts = g1._build_world_contexts(world, config, spec)
    arm_bases, per_rep_meta = _arm_bases_and_constants(contexts)
    resolved_by_rep = []
    for meta in per_rep_meta:
        resolved_by_rep.append(
            {arm: json.loads(meta[f"resolved_{arm}"]) for arm in ARM_NAMES}
        )

    # ---- G3 spot check: gap-stage-style e_arm_true (via context["flat"]) vs the
    # truth-path's own budget=1.0 short-circuit, searched non-degenerate spot,
    # for EVERY arm (cheap: one (rep,view,author) per world).
    g3_rows: list[dict[str, Any]] = []
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
    calibration, selection, _ = context["flat"][(view, author)]
    d_true = leg4._true_derivative(context["truth"], author)
    calibration_g3 = leg4._flatten_events(context["observed"].ecology.train_calibration, author)
    selection_g3 = leg4._flatten_events(context["observed"].ecology.train_selection, author)
    for arm in ARM_NAMES:
        basis = arm_bases[arm][rep_idx]
        params = resolved_by_rep[rep_idx][arm]
        d_gapstyle = _forced_route_derivative_adaptive(
            calibration, selection, basis, model=route,
            hazard_ridge=params["ridge"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
            weight_floor=params["weight_floor"], clip_bound=params["clip_bound"],
            tol_mode=params["tol_mode"], tol_value=params["tol_value"], probe_epsilon=params["probe_epsilon"],
        )
        e_gapstyle = leg3._relative_error(d_gapstyle, d_true)
        d_truthpath = _forced_route_derivative_adaptive(
            calibration_g3, selection_g3, basis, model=route,
            hazard_ridge=params["ridge"], logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims,
            weight_floor=params["weight_floor"], clip_bound=params["clip_bound"],
            tol_mode=params["tol_mode"], tol_value=params["tol_value"], probe_epsilon=params["probe_epsilon"],
        )
        e_truthpath = leg3._relative_error(d_truthpath, d_true)
        g3_rows.append(
            {
                "world": world, "arm": arm, "repetition": rep_idx, "view": view, "author": author,
                "e_arm_true_gapstyle": e_gapstyle, "e_arm_true_truthpath_budget1": e_truthpath,
                "abs_diff": abs(e_gapstyle - e_truthpath),
            }
        )
    g3_max = max(row["abs_diff"] for row in g3_rows)
    if g3_max > G3_TOLERANCE:
        raise RuntimeError(f"G3 truth-path invariance fails on {world}: {g3_max:.3e}")

    all_rows: list[dict[str, Any]] = []
    truth_gates: list[dict[str, Any]] = []
    for rep_idx2, context2 in enumerate(contexts):
        arm_bases_rep = {arm: arm_bases[arm][rep_idx2] for arm in ARM_NAMES}
        resolved_rep = resolved_by_rep[rep_idx2]
        for budget in TRUTH_BUDGETS:
            started = time.time()
            rows, gate = _truth_rows_for_context(context2, arm_bases_rep, resolved_rep, spec, budget)
            all_rows.extend(rows)
            truth_gates.append(gate)
            print(
                f"[m4g3] truth b={budget} {world} rep={rep_idx2} ({time.time()-started:.1f}s, events={gate['events']})",
                flush=True,
            )

    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(all_rows).to_csv(output / f"partial_truth_{world}.csv", index=False)
    pd.DataFrame(per_rep_meta).drop(
        columns=[f"resolved_{arm}" for arm in ARM_NAMES if arm not in ("adaptive_hazard_ridge",)]
    ).to_csv(output / f"partial_context_meta_{world}.csv", index=False)
    pd.DataFrame(per_rep_meta).to_csv(output / f"partial_context_meta_full_{world}.csv", index=False)
    pd.DataFrame(g3_rows).to_csv(output / f"partial_g3check_{world}.csv", index=False)
    gates = {
        "world": world,
        "truth_gates": truth_gates,
        "g3_max_abs_diff": g3_max,
        "basis_identity_check_max_abs_diff": max(m["basis_identity_check_max_abs_diff"] for m in per_rep_meta),
        "raw_scale_by_rep": {m["repetition"]: m["raw_scale"] for m in per_rep_meta},
    }
    with (output / f"partial_gates_truth_{world}.json").open("w", encoding="utf-8") as handle:
        json.dump(gates, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(f"[m4g3] truth stage done: {world}", flush=True)


# ---------------------------------------------------------------------------
# stage: offset (GPA), only for OFFSET_ARMS
# ---------------------------------------------------------------------------


def _run_offset_stage(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    contexts = g1._build_world_contexts(world, config, spec)
    arm_bases, per_rep_meta = _arm_bases_and_constants(contexts)
    offset_rows = []
    for arm in OFFSET_ARMS:
        v2_frames = []
        swap_frames = []
        for rep_idx, context in enumerate(contexts):
            basis = arm_bases[arm][rep_idx]
            swap_basis = leg9._row_norm_swap(context["truth"].oracle_basis, basis)  # unchanged
            v2_frames.append(leg11._stack_frame(basis))  # unchanged
            swap_frames.append(leg11._stack_frame(swap_basis))  # unchanged
        gpa_v2 = leg14._frechet_mean_multistart(v2_frames)  # unchanged
        gpa_swap = leg14._frechet_mean_multistart(swap_frames)  # unchanged
        offset = leg14._quotient_distance(gpa_v2["mean"], gpa_swap["mean"])  # unchanged
        offset_rows.append(
            {
                "world": world,
                "arm": arm,
                "offset_norm": offset,
                "width": int(v2_frames[0].shape[1]),
                "gpa_v2_basins": int(gpa_v2["n_distinct_basins"]),
                "gpa_swap_basins": int(gpa_swap["n_distinct_basins"]),
            }
        )
        print(f"[m4g3] offset {world} arm={arm} offset={offset:.6f}", flush=True)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(offset_rows).to_csv(output / f"partial_offset_{world}.csv", index=False)
    print(f"[m4g3] offset stage done: {world}", flush=True)


# ---------------------------------------------------------------------------
# stage: winner ladder (lean b definitional check), only for the winning arm
# ---------------------------------------------------------------------------


def _run_winner_ladder_stage(
    world: str, config: dict[str, Any], spec: M4ChartEcologySpec, winner_arm: str, output: Path
) -> None:
    contexts = g1._build_world_contexts(world, config, spec)
    all_rows: list[dict[str, Any]] = []
    for context in contexts:
        ingredients = leg10._freeze_ingredients(context)
        raw_scale = float(np.mean(ingredients["eigenvalues"][ingredients["retained"]]))
        deployed_ridge = float(context["fit_kwargs"]["hazard_ridge"])
        params = _resolve_constants(ARM_SPECS[winner_arm], raw_scale, deployed_ridge)
        for c in (0.25, 4.0):  # 1.0 already computed in the truth stage
            whitening = g2._whitening_for_c(ingredients, c)
            if ARM_SPECS[winner_arm].intercept == "adaptive":
                basis = _bases_from_whitening_adaptive(
                    context, ingredients, whitening, intercept_value=params["intercept"]
                )
            else:
                basis = leg10._bases_from_whitening(context, ingredients, whitening)  # unchanged
            for budget in TRUTH_BUDGETS:
                rows, _ = _truth_rows_for_context(
                    context,
                    {winner_arm: basis},
                    {winner_arm: params},
                    spec,
                    budget,
                    arms=(winner_arm,),
                )
                for row in rows:
                    row["ladder_c"] = c
                all_rows.extend(rows)
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(all_rows).to_csv(output / f"partial_winner_ladder_{world}_{winner_arm}.csv", index=False)
    print(f"[m4g3] winner_ladder stage done: {world} arm={winner_arm}", flush=True)


# ---------------------------------------------------------------------------
# assemble + adjudicate
# ---------------------------------------------------------------------------


def _world_level_median(author_truth: pd.DataFrame, arm: str, budget: float, worlds: list[str]) -> pd.Series:
    scoped = author_truth[(author_truth["arm"] == arm) & (author_truth["budget"] == budget)]
    return scoped.groupby("world")["e_arm_true"].median().reindex(worlds)


def _paired_world_diff_ci(author_truth: pd.DataFrame, arm_lo: str, arm_hi: str, budget: float, worlds: list[str]):
    lo = _world_level_median(author_truth, arm_lo, budget, worlds)
    hi = _world_level_median(author_truth, arm_hi, budget, worlds)
    diffs = (lo - hi).to_numpy()
    return g1._paired_world_ci(diffs), lo, hi


def _paired_author_diff_ci(author_truth: pd.DataFrame, arm_lo: str, arm_hi: str, budget: float, worlds: list[str]):
    scoped = author_truth[(author_truth["budget"] == budget) & (author_truth["world"].isin(worlds))]
    lo_rows = scoped[scoped["arm"] == arm_lo].set_index(["world", "repetition", "author"])
    hi_rows = scoped[scoped["arm"] == arm_hi].set_index(["world", "repetition", "author"])
    joined = lo_rows.join(hi_rows, lsuffix="_lo", rsuffix="_hi", how="inner")
    diffs = (joined["e_arm_true_lo"] - joined["e_arm_true_hi"]).to_numpy()
    return g1._paired_author_ci(diffs)


def _assemble_truth(output: Path) -> dict[str, Any]:
    worlds = list(D1_WORLDS)
    truth_frames = [pd.read_csv(output / f"partial_truth_{w}.csv") for w in worlds]
    truth_rows = pd.concat(truth_frames, ignore_index=True)
    g3_frames = [pd.read_csv(output / f"partial_g3check_{w}.csv") for w in worlds]
    g3_rows = pd.concat(g3_frames, ignore_index=True)
    meta_frames = [pd.read_csv(output / f"partial_context_meta_full_{w}.csv") for w in worlds]
    context_meta = pd.concat(meta_frames, ignore_index=True)
    gate_payloads = []
    for w in worlds:
        with (output / f"partial_gates_truth_{w}.json").open("r", encoding="utf-8") as handle:
            gate_payloads.append(json.load(handle))

    expected_truth_rows = len(worlds) * len(TRUTH_BUDGETS) * 8 * 2 * 16 * len(ARM_NAMES)
    if len(truth_rows) != expected_truth_rows:
        raise RuntimeError(f"truth rows {len(truth_rows)} != expected {expected_truth_rows}")

    # ---- G3 truth-path invariance ------------------------------------------
    g3 = {
        "statement": "truth path at budget=1.0 reproduces gap-stage-style e_arm_true exactly, all 9 arms",
        "max_abs_diff": float(g3_rows["abs_diff"].max()),
        "n_checks": int(len(g3_rows)),
        "tolerance": G3_TOLERANCE,
        "pass": bool(g3_rows["abs_diff"].max() <= G3_TOLERANCE),
    }

    # ---- structural basis-identity check (BASIS_IDENTICAL_TO_BASELINE_ARMS) --
    basis_identity_max = float(context_meta["basis_identity_check_max_abs_diff"].max())

    # ---- numerical-validity diagnostic: recompute e_orc_true valid-world check
    orc_diag_rows = []
    for budget in TRUTH_BUDGETS:
        scoped = truth_rows[
            (truth_rows["budget"] == budget) & (~truth_rows["degenerate_reference"]) & (truth_rows["arm"] == "baseline")
        ]
        for w in worlds:
            median_e_orc = float(scoped[scoped["world"] == w]["e_orc_true"].median())
            orc_diag_rows.append({"world": w, "budget": budget, "median_e_orc_true": median_e_orc})
    orc_diag = pd.DataFrame(orc_diag_rows)
    worst_per_world = orc_diag.groupby("world")["median_e_orc_true"].max()
    recomputed_valid_worlds = sorted(worst_per_world[worst_per_world <= TRUTH_VALIDITY_THRESHOLD].index.tolist())
    valid_world_subset_reproduced = recomputed_valid_worlds == sorted(VALID_TRUTH_WORLDS)

    # ---- G1 ANCHOR: baseline vs c_1.0, c4_reference vs c_4.0 (M4-G2 persisted) -
    m4g2_truth = pd.read_csv(ROOT / "results" / "m4_g2_metric_units" / "truth_recovery_rows.csv")
    anchor_rows = []
    for mine_arm, m4g2_arm in (("baseline", "c_1.0"), ("c4_reference", "c_4.0")):
        mine = truth_rows[truth_rows["arm"] == mine_arm]
        theirs = m4g2_truth[m4g2_truth["arm"] == m4g2_arm]
        joined = mine.merge(
            theirs, on=["world", "repetition", "view", "author", "budget"], suffixes=("_mine", "_theirs"), how="inner"
        )
        expected = len(worlds) * len(TRUTH_BUDGETS) * 8 * 2 * 16
        if len(joined) != expected:
            raise RuntimeError(f"G1 anchor join size {len(joined)} != expected {expected} for {mine_arm}")
        diff = (joined["e_arm_true_mine"] - joined["e_arm_true_theirs"]).abs()
        anchor_rows.append(
            {"arm": mine_arm, "m4g2_arm": m4g2_arm, "n_rows": int(len(joined)), "max_abs_diff": float(diff.max(skipna=True))}
        )
    g1_anchor_truth_max = max(row["max_abs_diff"] for row in anchor_rows)

    author_truth = g1._author_level_truth(truth_rows)  # reused unchanged, generic over "arm"
    valid_worlds = list(VALID_TRUTH_WORLDS)

    # ---- G0 POWER (pre-stated section; recomputed here from THIS leg's own
    # baseline/c4_reference rows for full self-containment, matching the
    # pre-registered numbers computed from M4-G2's persisted CSV in Part 0) --
    g0_rows = []
    for budget in TRUTH_BUDGETS:
        world_ci, base_med, c4_med = _paired_world_diff_ci(author_truth, "baseline", "c4_reference", budget, valid_worlds)
        gain_world = float(base_med.mean() - c4_med.mean())
        author_ci = _paired_author_diff_ci(author_truth, "baseline", "c4_reference", budget, valid_worlds)
        gain_author = float(author_ci["mean"])
        g0_rows.append(
            {
                "budget": budget,
                "n_valid_worlds": len(valid_worlds),
                "world_level_gain": gain_world,
                "world_level_ci": world_ci,
                "world_level_bar_25pct_of_gain": G0_FRACTION_BAR * gain_world,
                "world_level_underpowered": bool(world_ci["half_width"] > G0_FRACTION_BAR * gain_world),
                "author_level_gain": gain_author,
                "author_level_ci": author_ci,
                "author_level_bar_25pct_of_gain": G0_FRACTION_BAR * gain_author,
                "author_level_underpowered": bool(author_ci["half_width"] > G0_FRACTION_BAR * gain_author),
            }
        )
    g0 = {
        "statement": (
            "PRIMARY (decisive, per the registration's literal 'paired-by-world' "
            "wording -- world-level reduction: median e_arm_true over "
            "(repetition,author) per world, then g1._paired_world_ci across the "
            "n=6 valid worlds): CI half-width vs 25% of the c=4 gain (half of "
            "lean (a)'s 50% bar, matching this line's own convention). "
            "SECONDARY (disclosed, non-gating, matching lean (b)'s own author-level "
            "grain, n up to 745 author-reps): CI half-width vs the SAME 25% bar, "
            "computed on the author-level (not world-reduced) gain."
        ),
        "per_budget": g0_rows,
    }

    # ---- LEAN (a): single-constant arms, LOCALIZABLE -------------------------
    # Status logic mirrors M4-G2's own G0/lean-a precedent exactly: a
    # comparison whose world-level CI half-width exceeds the G0 bar cannot
    # honestly be scored MISS just because the CI happens to touch zero --
    # that is the textbook "null at the noise floor" the standing rules
    # require be reported UNDERPOWERED. HOLD is never downgraded by this (a
    # CI that excludes zero DESPITE being wide is, if anything, stronger
    # evidence, not weaker). A disclosed, non-gating AUTHOR-LEVEL companion
    # (same grain lean (b) itself uses, adequately powered per G0 secondary)
    # is computed for every arm alongside the registered world-level test.
    def _arm_vs_baseline(arm: str, budget: float) -> dict[str, Any]:
        world_ci, base_med, arm_med = _paired_world_diff_ci(author_truth, "baseline", arm, budget, valid_worlds)
        _, _, c4_med = _paired_world_diff_ci(author_truth, "baseline", "c4_reference", budget, valid_worlds)
        gain = float(base_med.mean() - c4_med.mean())
        recovered = float(base_med.mean() - arm_med.mean())
        fraction = recovered / gain if gain else float("nan")
        ci_excludes_zero = bool(world_ci["ci_lo"] > 0.0)
        world_bar = G0_FRACTION_BAR * gain
        world_underpowered = bool(world_ci["half_width"] > world_bar)
        author_ci = _paired_author_diff_ci(author_truth, "baseline", arm, budget, valid_worlds)
        author_fraction = float(author_ci["mean"]) / gain if gain else float("nan")
        author_ci_excludes_zero = bool(author_ci["ci_lo"] > 0.0)
        if fraction >= LEAN_A_FRACTION_BAR and ci_excludes_zero:
            status = "HOLD"
        elif world_underpowered:
            status = "UNDERPOWERED"
        else:
            status = "MISS"
        return {
            "budget": budget,
            "gain": gain,
            "recovered": recovered,
            "fraction_of_gain": fraction,
            "paired_world_ci": world_ci,
            "world_level_bar_25pct_of_gain": world_bar,
            "world_level_underpowered": world_underpowered,
            "ci_excludes_zero": ci_excludes_zero,
            "author_level_companion": {
                "statement": "disclosed, non-gating; same grain as lean (b)/G0-secondary",
                "paired_author_ci": author_ci,
                "fraction_of_gain": author_fraction,
                "ci_excludes_zero": author_ci_excludes_zero,
            },
            "status": status,
            "held": bool(status == "HOLD"),
        }

    lean_a_rows = []
    for constant, arm in ARM_OF_CONSTANT.items():
        per_budget = [_arm_vs_baseline(arm, budget) for budget in TRUTH_BUDGETS]
        held_all_budgets = bool(all(b["status"] == "HOLD" for b in per_budget))
        any_underpowered = bool(any(b["status"] == "UNDERPOWERED" for b in per_budget))
        overall_status = "HOLD" if held_all_budgets else ("UNDERPOWERED" if any_underpowered else "MISS")
        lean_a_rows.append(
            {
                "constant": constant, "arm": arm, "per_budget": per_budget,
                "held": held_all_budgets, "status": overall_status,
            }
        )
    lean_a_any_held = any(row["held"] for row in lean_a_rows)
    lean_a_any_underpowered = any(row["status"] == "UNDERPOWERED" for row in lean_a_rows)

    # ---- adaptive_all's own >=50%-of-gain check (feeds the PIVOT, not lean a) -
    all_per_budget = [_arm_vs_baseline("adaptive_all", budget) for budget in TRUTH_BUDGETS]
    adaptive_all_held = bool(all(b["status"] == "HOLD" for b in all_per_budget))
    adaptive_all_underpowered = bool(any(b["status"] == "UNDERPOWERED" for b in all_per_budget))

    # PIVOT can only legitimately FIRE if every single-constant arm AND
    # adaptive_all are CLEANLY MISS (not merely underpowered) -- an
    # underpowered comparison adjudicates nothing (standing rule), so it
    # cannot supply the "fails" half of the registered PIVOT-IF condition.
    all_arms_status = [row["status"] for row in lean_a_rows] + [
        "HOLD" if adaptive_all_held else ("UNDERPOWERED" if adaptive_all_underpowered else "MISS")
    ]
    if any(s == "HOLD" for s in all_arms_status):
        pivot_status = "DOES_NOT_FIRE"
    elif any(s == "UNDERPOWERED" for s in all_arms_status):
        pivot_status = "UNDERPOWERED"
    else:
        pivot_status = "FIRES"
    pivot_fires = bool(pivot_status == "FIRES")

    # winner selection: no arm literally HOLDS the registered world-level
    # test (see decision.json) -- if any did, prefer the highest mean
    # fraction-of-gain among HOLD arms (single-constant preferred over
    # adaptive_all). If none HOLD but the pivot is UNDERPOWERED (not FIRES),
    # the arm with the largest, most consistent author-level companion
    # effect is surfaced as the LEADING CANDIDATE for leans (b)/(c) -- named
    # explicitly as such, never silently promoted to "winner" as if lean (a)
    # had HELD.
    winner = None
    winner_status = "none"
    if lean_a_any_held:
        held_rows = [r for r in lean_a_rows if r["held"]]
        winner = max(held_rows, key=lambda r: np.mean([b["fraction_of_gain"] for b in r["per_budget"]]))["arm"]
        winner_status = "lean_a_hold"
    elif adaptive_all_held:
        winner = "adaptive_all"
        winner_status = "lean_a_hold"
    elif pivot_status == "UNDERPOWERED":
        candidates = lean_a_rows + [
            {"constant": "all", "arm": "adaptive_all", "per_budget": all_per_budget}
        ]
        underpowered_candidates = [
            r for r in candidates
            if any(b["status"] == "UNDERPOWERED" for b in r["per_budget"])
        ]
        if underpowered_candidates:
            best = max(
                underpowered_candidates,
                key=lambda r: np.mean([b["fraction_of_gain"] for b in r["per_budget"]]),
            )
            winner = best["arm"]
            winner_status = "underpowered_leading_candidate"

    # ---- G2 CONSTANT LIVENESS: for EVERY inventoried Category A constant.
    # Three-way classification per (constant, budget), not a binary
    # live/not-live: LIVE (CI entirely outside +/-margin -- moves,
    # decisively), INERT (CI entirely INSIDE +/-margin -- a genuine
    # equivalence-form null, the registered "statistically indistinguishable
    # from no effect" reading), or AMBIGUOUS (CI straddles the margin --
    # neither confirmed, the world-level analogue of lean (a)'s own
    # UNDERPOWERED state; a disclosed author-level companion is reported
    # alongside every world-level read).
    def _g2_classify(arm: str, budget: float) -> dict[str, Any]:
        ci, _, _ = _paired_world_diff_ci(author_truth, "baseline", arm, budget, valid_worlds)
        author_ci = _paired_author_diff_ci(author_truth, "baseline", arm, budget, valid_worlds)
        if ci["ci_lo"] > G2_LIVENESS_MARGIN or ci["ci_hi"] < -G2_LIVENESS_MARGIN:
            status = "LIVE"
        elif ci["ci_lo"] >= -G2_LIVENESS_MARGIN and ci["ci_hi"] <= G2_LIVENESS_MARGIN:
            status = "INERT"
        else:
            status = "AMBIGUOUS"
        author_live = bool(author_ci["ci_lo"] > G2_LIVENESS_MARGIN or author_ci["ci_hi"] < -G2_LIVENESS_MARGIN)
        author_inert = bool(author_ci["ci_lo"] >= -G2_LIVENESS_MARGIN and author_ci["ci_hi"] <= G2_LIVENESS_MARGIN)
        author_status = "LIVE" if author_live else ("INERT" if author_inert else "AMBIGUOUS")
        return {
            "budget": budget, "paired_world_ci": ci, "status": status, "moves": bool(status == "LIVE"),
            "author_level_companion": {"paired_author_ci": author_ci, "status": author_status},
        }

    g2_rows = []
    for constant, arm in ARM_OF_CONSTANT.items():
        per_budget = [_g2_classify(arm, budget) for budget in TRUTH_BUDGETS]
        live = bool(all(b["status"] == "LIVE" for b in per_budget))
        inert = bool(all(b["status"] == "INERT" for b in per_budget))
        overall = "LIVE" if live else ("INERT" if inert else "AMBIGUOUS")
        g2_rows.append({"constant": constant, "arm": arm, "per_budget": per_budget, "live": live, "status": overall})
    g2_all_per_budget = [_g2_classify("adaptive_all", budget) for budget in TRUTH_BUDGETS]
    g2_all_live = bool(all(b["status"] == "LIVE" for b in g2_all_per_budget))
    g2_all_inert = bool(all(b["status"] == "INERT" for b in g2_all_per_budget))
    g2_all_status = "LIVE" if g2_all_live else ("INERT" if g2_all_inert else "AMBIGUOUS")
    g2_liveness = {
        "statement": (
            f"paired-by-world (n={len(valid_worlds)}) CI on (baseline - adaptive_<k>) "
            f"world-level medians; LIVE iff the CI is entirely outside +/-{G2_LIVENESS_MARGIN} "
            "at BOTH budgets, INERT iff entirely inside +/-margin at both budgets "
            "(genuine equivalence-form null), else AMBIGUOUS (CI straddles the "
            "margin -- neither confirmed; a disclosed author-level companion, same "
            "grain as lean (b)/G0-secondary, is reported alongside every row)"
        ),
        "per_constant": g2_rows,
        "adaptive_all": {"per_budget": g2_all_per_budget, "live": g2_all_live, "status": g2_all_status},
    }

    return {
        "worlds": worlds,
        "valid_worlds": valid_worlds,
        "truth_rows": truth_rows,
        "author_truth": author_truth,
        "context_meta": context_meta,
        "g3": g3,
        "basis_identity_max": basis_identity_max,
        "orc_diag": orc_diag,
        "recomputed_valid_worlds": recomputed_valid_worlds,
        "valid_world_subset_reproduced": valid_world_subset_reproduced,
        "g1_anchor_truth_rows": anchor_rows,
        "g1_anchor_truth_max": g1_anchor_truth_max,
        "g0": g0,
        "lean_a_rows": lean_a_rows,
        "lean_a_any_held": lean_a_any_held,
        "lean_a_any_underpowered": lean_a_any_underpowered,
        "adaptive_all_per_budget": all_per_budget,
        "adaptive_all_held": adaptive_all_held,
        "adaptive_all_underpowered": adaptive_all_underpowered,
        "pivot_fires": pivot_fires,
        "pivot_status": pivot_status,
        "winner": winner,
        "winner_status": winner_status,
        "g2_liveness": g2_liveness,
    }


def _assemble(output: Path) -> None:
    truth_phase = _assemble_truth(output)
    worlds = truth_phase["worlds"]
    valid_worlds = truth_phase["valid_worlds"]
    author_truth = truth_phase["author_truth"]

    # ---- offset partials (baseline, c4_reference, adaptive_intercept, adaptive_all)
    offset_frames = [pd.read_csv(output / f"partial_offset_{w}.csv") for w in worlds]
    offset_rows = pd.concat(offset_frames, ignore_index=True)
    expected_offset = len(worlds) * len(OFFSET_ARMS)
    if len(offset_rows) != expected_offset:
        raise RuntimeError(f"offset rows {len(offset_rows)} != expected {expected_offset}")

    m4g2_offset = pd.read_csv(ROOT / "results" / "m4_g2_metric_units" / "offset_rows.csv")
    offset_anchor_rows = []
    for mine_arm, m4g2_arm in (("baseline", "c_1.0"), ("c4_reference", "c_4.0")):
        mine = offset_rows[offset_rows["arm"] == mine_arm].set_index("world")["offset_norm"]
        theirs = m4g2_offset[(m4g2_offset["arm"] == m4g2_arm) & (m4g2_offset["c"] == (4.0 if m4g2_arm == "c_4.0" else 1.0))]
        theirs = theirs.set_index("world")["offset_norm"]
        diff = (mine.reindex(worlds) - theirs.reindex(worlds)).abs()
        offset_anchor_rows.append({"arm": mine_arm, "m4g2_arm": m4g2_arm, "max_abs_diff": float(diff.max())})
    g1_anchor_offset_max = max(row["max_abs_diff"] for row in offset_anchor_rows)

    g1_anchor = {
        "truth": {"per_arm": truth_phase["g1_anchor_truth_rows"], "max_abs_diff": truth_phase["g1_anchor_truth_max"]},
        "offset": {"per_arm": offset_anchor_rows, "max_abs_diff": g1_anchor_offset_max},
        "tolerance": G1_ANCHOR_TOLERANCE,
        "pass": bool(
            truth_phase["g1_anchor_truth_max"] <= G1_ANCHOR_TOLERANCE
            and g1_anchor_offset_max <= G1_ANCHOR_TOLERANCE
        ),
    }

    winner = truth_phase["winner"]
    lean_b = {"statement": "definitional check not reached", "held": None}
    lean_c = {"statement": "materiality check not reached", "held": None}

    if winner is not None:
        # ---- LEAN (b): winner's truth recovery invariant across c in {0.25,1,4} --
        ladder_files = list(output.glob(f"partial_winner_ladder_*_{winner}.csv"))
        if len(ladder_files) != len(worlds):
            lean_b = {
                "statement": f"winner={winner}; winner_ladder partials missing ({len(ladder_files)}/{len(worlds)} worlds present) -- run --stage winner_ladder for the remaining worlds, then re-assemble",
                "winner": winner,
                "held": None,
            }
        else:
            ladder_rows = pd.concat([pd.read_csv(f) for f in ladder_files], ignore_index=True)
            c1_rows = truth_phase["truth_rows"][truth_phase["truth_rows"]["arm"] == winner].copy()
            c1_rows["ladder_c"] = 1.0
            combined = pd.concat([c1_rows, ladder_rows], ignore_index=True)
            # author-level reduce (mean over views), keeping ladder_c as a grouping
            # key -- same reduction g1._author_level_truth applies (drop degenerate,
            # mean over view), done manually here since ladder_c is an extra axis
            # g1._author_level_truth's own groupby does not carry.
            combined2 = combined[~combined["degenerate_reference"]]
            combined2 = (
                combined2.groupby(["world", "repetition", "author", "ladder_c", "budget"])["e_arm_true"]
                .mean()
                .reset_index()
            )
            pair_rows = []
            for budget in TRUTH_BUDGETS:
                for c_lo, c_hi in itertools.combinations((0.25, 1.0, 4.0), 2):
                    scoped = combined2[(combined2["budget"] == budget) & (combined2["world"].isin(valid_worlds))]
                    lo = scoped[scoped["ladder_c"] == c_lo].set_index(["world", "repetition", "author"])
                    hi = scoped[scoped["ladder_c"] == c_hi].set_index(["world", "repetition", "author"])
                    joined = lo.join(hi, lsuffix="_lo", rsuffix="_hi", how="inner")
                    diffs = (joined["e_arm_true_lo"] - joined["e_arm_true_hi"]).to_numpy()
                    ci = g1._paired_author_ci(diffs)
                    within = bool(ci["n"] > 1 and ci["ci_lo"] >= -LEAN_B_MARGIN and ci["ci_hi"] <= LEAN_B_MARGIN)
                    pair_rows.append(
                        {"budget": budget, "c_lo": c_lo, "c_hi": c_hi, "n": ci["n"], "mean_diff": ci["mean"],
                         "ci_lo": ci["ci_lo"], "ci_hi": ci["ci_hi"], "within_margin": within}
                    )
            lean_b_held = bool(all(r["within_margin"] for r in pair_rows))
            lean_b = {
                "statement": f"winner={winner}; all C(3,2)=3 pairwise c-comparisons (0.25,1.0,4.0), both budgets, CI inside +/-{LEAN_B_MARGIN}",
                "winner": winner,
                "per_pair": pair_rows,
                "held": lean_b_held,
            }

        # ---- LEAN (c): winner's scale-normalized offset does not worsen vs baseline
        if winner in ("adaptive_intercept", "adaptive_all"):
            winner_offset = offset_rows[offset_rows["arm"] == winner].set_index("world")["offset_norm"].reindex(worlds)
        else:
            # structurally identical to baseline (verified in truth_phase["basis_identity_max"])
            winner_offset = offset_rows[offset_rows["arm"] == "baseline"].set_index("world")["offset_norm"].reindex(worlds)
        baseline_offset = offset_rows[offset_rows["arm"] == "baseline"].set_index("world")["offset_norm"].reindex(worlds)
        # scale-normalized offset: GM(scale_factors) is IDENTICAL for baseline and
        # every c=1 arm (none of the 6 constants touch the whitening operator), so
        # normalizing both sides by the SAME per-world constant is equivalent to
        # comparing raw offsets directly here; reported both ways for transparency.
        diff = (winner_offset - baseline_offset).to_numpy()
        ci = g1._paired_world_ci(diff)
        lean_c_margin = LEAN_C_MARGIN_FRACTION * float(baseline_offset.mean())
        worsens = bool(ci["ci_lo"] > lean_c_margin)
        lean_c_held = bool(not worsens)
        lean_c = {
            "statement": (
                f"winner={winner} offset vs baseline offset, paired-by-world (n={len(worlds)}), "
                f"equivalence margin +/-{LEAN_C_MARGIN_FRACTION*100:.0f}% of baseline mean offset "
                f"(={lean_c_margin:.4f}); identical-by-construction for non-intercept single-constant winners"
            ),
            "winner": winner,
            "winner_offset_by_world": winner_offset.to_dict(),
            "baseline_offset_by_world": baseline_offset.to_dict(),
            "baseline_mean_offset": float(baseline_offset.mean()),
            "margin_fraction": LEAN_C_MARGIN_FRACTION,
            "margin_value": lean_c_margin,
            "paired_world_ci_winner_minus_baseline": ci,
            "worsens": worsens,
            "held": lean_c_held,
        }

    pivot_status = truth_phase["pivot_status"]
    if pivot_status == "FIRES":
        verdict = "PIVOT_SCALE_DEPENDENCE_NOT_LOCALIZED"
    elif truth_phase["lean_a_any_held"] or truth_phase["adaptive_all_held"]:
        verdict = "LOCALIZED_REPAIR_CANDIDATE"
    elif pivot_status == "UNDERPOWERED":
        verdict = "UNDERPOWERED_NO_ADJUDICATION_AT_REGISTERED_GRAIN"
    else:
        verdict = "AMBIGUOUS_NO_WINNER_PIVOT_DOES_NOT_FIRE"

    decision = {
        "estimand_id": "SUICA_M4_G3_SCALE_ADAPTIVE",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md M4-G3 registration (2026-08-03, BEFORE run); ledger row M4-G3",
        "worlds": worlds,
        "valid_truth_worlds": valid_worlds,
        "arm_names": list(ARM_NAMES),
        "category_a_constants": list(CATEGORY_A_CONSTANTS),
        "arm_of_constant": ARM_OF_CONSTANT,
        "truth_budgets": list(TRUTH_BUDGETS),
        "gates": {
            "G0": truth_phase["g0"],
            "G1_anchor": g1_anchor,
            "G2_constant_liveness": truth_phase["g2_liveness"],
            "G3_truth_path_invariance": truth_phase["g3"],
        },
        "structural_checks": {
            "basis_identical_to_baseline_arms": list(BASIS_IDENTICAL_TO_BASELINE_ARMS),
            "basis_identity_max_abs_diff": truth_phase["basis_identity_max"],
            "recomputed_valid_worlds": truth_phase["recomputed_valid_worlds"],
            "valid_world_subset_reproduced_from_m4g2": truth_phase["valid_world_subset_reproduced"],
        },
        "lean_a": {
            "per_constant": truth_phase["lean_a_rows"],
            "held": truth_phase["lean_a_any_held"],
            "any_underpowered": truth_phase["lean_a_any_underpowered"],
        },
        "adaptive_all_localizable_check": {
            "statement": ">=50% of gain with paired-world CI excluding zero, both budgets (feeds the PIVOT, not lean (a) itself)",
            "per_budget": truth_phase["adaptive_all_per_budget"],
            "held": truth_phase["adaptive_all_held"],
            "underpowered": truth_phase["adaptive_all_underpowered"],
        },
        "pivot": {
            "registered": "no single-constant arm reaches 50% of the gain AND adaptive_all also fails -> scale dependence NOT localized",
            "fires": truth_phase["pivot_fires"],
            "status": pivot_status,
            "note": (
                "FIRES requires every single-constant arm AND adaptive_all to be "
                "cleanly MISS -- an UNDERPOWERED comparison cannot supply the "
                "'fails' half of the registered condition (standing rule: a null "
                "at the noise floor is reported UNDERPOWERED, never as a null)"
            ),
        },
        "winner": winner,
        "winner_status": truth_phase["winner_status"],
        "lean_b": lean_b,
        "lean_c": lean_c,
        "verdict": verdict,
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only (8 D1 worlds; truth-recovery "
            "statistics use M4-G2's own valid 6-world subset, reused verbatim); "
            "truth-referenced recovery via budget-regenerated (4x/8x events) finite "
            "panels from the frozen world law, compared to the analytic D_true; no "
            "natural-text, personality, or clinical claim; no seal, no independent "
            "verification (operator directive 2026-08-01)."
        ),
    }

    output.mkdir(parents=True, exist_ok=True)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    with (output / "gates.json").open("w", encoding="utf-8") as handle:
        json.dump(decision["gates"], handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    truth_phase["truth_rows"].to_csv(output / "truth_recovery_rows.csv", index=False)
    truth_phase["author_truth"].to_csv(output / "author_level_truth_rows.csv", index=False)
    truth_phase["context_meta"].to_csv(output / "context_meta.csv", index=False)
    truth_phase["orc_diag"].to_csv(output / "e_orc_true_validity_diagnostic.csv", index=False)
    offset_rows.to_csv(output / "offset_rows.csv", index=False)
    pd.DataFrame(
        [
            {"constant": row["constant"], "arm": row["arm"], **{f"budget{b['budget']:g}_fraction_of_gain": b["fraction_of_gain"] for b in row["per_budget"]}, "held": row["held"]}
            for row in truth_phase["lean_a_rows"]
        ]
    ).to_csv(output / "lean_a_per_constant.csv", index=False)
    pd.DataFrame(
        [
            {"constant": row["constant"], "arm": row["arm"], **{f"budget{b['budget']:g}_live": b["moves"] for b in row["per_budget"]}, "live": row["live"]}
            for row in truth_phase["g2_liveness"]["per_constant"]
        ]
    ).to_csv(output / "g2_liveness_per_constant.csv", index=False)
    if isinstance(lean_b, dict) and "per_pair" in lean_b:
        pd.DataFrame(lean_b["per_pair"]).to_csv(output / "lean_b_pairwise_equivalence.csv", index=False)

    print(
        json.dumps(
            {
                "verdict": verdict,
                "pivot_status": pivot_status,
                "pivot_fires": truth_phase["pivot_fires"],
                "winner": winner,
                "winner_status": truth_phase["winner_status"],
                "lean_a_any_held": truth_phase["lean_a_any_held"],
                "lean_a_any_underpowered": truth_phase["lean_a_any_underpowered"],
                "adaptive_all_held": truth_phase["adaptive_all_held"],
                "lean_b_held": lean_b.get("held"),
                "lean_c_held": lean_c.get("held"),
                "g1_anchor_pass": g1_anchor["pass"],
                "g3_pass": truth_phase["g3"]["pass"],
                "valid_world_subset_reproduced": truth_phase["valid_world_subset_reproduced"],
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
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_g3_scale_adaptive")
    parser.add_argument("--world", type=str, default=None)
    parser.add_argument("--stage", type=str, choices=("truth", "offset", "winner_ladder"), default=None)
    parser.add_argument("--winner-arm", type=str, default=None)
    parser.add_argument("--assemble", action="store_true")
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    spec = M4ChartEcologySpec(**config["base_spec"])

    if args.assemble:
        _assemble(args.output)
        return

    if args.world is None or args.stage is None:
        raise SystemExit("--world and --stage are required unless --assemble")
    if args.world not in D1_WORLDS:
        raise SystemExit(f"not a registered D1 world: {args.world}")

    if args.stage == "truth":
        _run_truth_stage(args.world, config, spec, args.output)
    elif args.stage == "offset":
        _run_offset_stage(args.world, config, spec, args.output)
    else:
        if args.winner_arm is None:
            raise SystemExit("--winner-arm is required for --stage winner_ladder")
        if args.winner_arm not in ARM_NAMES:
            raise SystemExit(f"not a registered arm: {args.winner_arm}")
        _run_winner_ladder_stage(args.world, config, spec, args.winner_arm, args.output)


if __name__ == "__main__":
    main()
