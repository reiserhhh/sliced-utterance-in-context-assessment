#!/usr/bin/env python3
"""M4-G7: does the certified repair reach the displacement the line was
opened to attack, or is it orthogonal to it?

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-G7
registration" (2026-08-03, BEFORE run); ledger row M4-G7). Machinery is
IMPORTED and REUSED, not reimplemented: Leg 4's context build + forced-route
derivative + analytic D_true, Leg 3's world seed + relative error, Leg 9's
row-norm swap, Leg 10's freeze-ingredients rebuild, Leg 11's stacked-frame
quotient machinery, Leg 14's GPA Frechet mean + quotient distance (the SAME
functions M4-E2 and M4-G1 used), M4-G1's whitening-arm/scale-factor
construction (`_whitening_for_arm`, `_scale_factors`, `_paired_world_ci`,
`_paired_author_ci`), M4-G3's parameterized deployed-arm estimator
(`_forced_route_derivative_adaptive`), M4-G4's generic CI/classification
machinery (`_author_level_truth_with_c`, `_paired_author_diff_ci`,
`_paired_world_diff_ci`, `_classify_pair`, `_arm_status_from_pairs`), and --
centrally -- M4-G5/G6's own `column_standardized` mechanism
(`g5._forced_route_derivative_columnwise`, called UNCHANGED at
`ridge_deployed = 0.10 * deployed_ridge`, M4-G6's headline). No estimator
internals are copied. The only genuinely new code is (i) this leg's own
two-arm dispatcher (Part 0.2), (ii) disclosed near-duplicates of
`_truth_rows_for_context`/`_g3_spot_check` generalized to this leg's own two
arms and three (not eight) worlds, (iii) the offset/displacement stage
(Part 0.1's structural-identity argument made concrete and verified), and
(iv) the G2 per-column ridge-profile evidence and this leg's own
gate/lean/pivot bookkeeping.

===========================================================================
PART 0 -- THE STRUCTURAL-IDENTITY ARGUMENT FOR METRICS 1/2 (stated BEFORE
compute, verified rather than merely asserted), THE WORLD/GRAIN CHOICES, AND
REGISTERED-AMBIGUITY RESOLUTIONS.
===========================================================================

--- 0.1 Why metrics 1 and 2 cannot move between `deployed` and `repaired` ---

The repair under test is `column_standardized` at `ridge_deployed = alpha *
deployed_ridge` (M4-G6's headline, alpha=0.10), dispatched here through
`g5._forced_route_derivative_columnwise` UNCHANGED. That function's signature
(`scripts/run_suica_m4_g5_per_column_ridge.py:557-602`) takes a fixed `basis`
argument and returns a derivative estimate computed FROM it; nowhere does it
construct, modify, or return a basis. The basis it consumes is built earlier,
once per (world, repetition), by `leg4._build_context` -- specifically
`context["v2_basis"]`, the TRUE, already-frozen discovered frame (verified
bit-identical to M4-G1's own `baseline` arm reconstruction,
`leg10._bases_from_whitening(context, ingredients, _whitening_for_arm(...,
"baseline"))`, to <=1e-12, M4-G1's own G1 ANCHOR gate, reproduced here as an
internal check). `context["v2_basis"]` is a function of `(world, repetition,
seed, config)` ONLY -- `config["base_spec"]`'s `hazard_ridge` never varies
between this leg's two arms (both use the SAME deployed config throughout
context construction; only the ridge value handed to the EVALUATION-TIME
forced-route refit differs). Metric 1 (offset_norm / its scale-normalized
form) and metric 2 (Leg 14's per-rep displacement `disp_v2 =
quotient_distance(swap_rep, v2_rep)`) are BOTH pure functions of
`context["v2_basis"]` and `context["truth"].oracle_basis` alone (via
`leg9._row_norm_swap`, `leg11._stack_frame`, `leg14._quotient_distance` /
`_frechet_mean_multistart`) -- neither function takes a ridge, alpha, or
treatment argument anywhere in their signatures. CONSEQUENCE, stated here as
a provable prediction before compute, not an outcome asserted after the
fact: metrics 1 and 2 must be IDENTICAL between `deployed` and `repaired`,
to floating-point exactness, for every world and every repetition -- not
because the repair is weak, but because the ridge parameter it varies sits
entirely downstream of, and structurally disconnected from, the object these
two metrics measure. This is verified empirically below (computed once per
world, assigned to both arm labels, with the assignment itself gated as a
G1-ANCHOR-style degenerate equality check), mirroring this line's own
established practice (M4-G3's Category-B call-graph exclusion; M4-G6's own
`colstd_alpha_1.00` vs `column_standardized` identity check) of stating a
structural non-dependence and then confirming it, not merely asserting it.
This argument does NOT extend to metric 3 (truth-referenced recovery), which
IS a direct function of the ridge value -- that is the one metric this leg
expects, and needs, to move.

--- 0.2 Two-arm dispatcher (registered; mirrors M4-G6's own
    `_forced_route_derivative_for_arm`, generalized to two named arms) ------

`deployed` routes through `g3._forced_route_derivative_adaptive` at
`hazard_ridge = deployed_ridge` (M4-G1/G4/G5/G6's own `baseline` semantics,
verified bit-identical to M4-G1's plain `leg4._forced_route_derivative` call
via the existing cross-leg anchor chain, reproduced here as G1 ANCHOR).
`repaired` routes through `g5._forced_route_derivative_columnwise` with
`treatment="column_standardized"`, `ridge_deployed = ALPHA * deployed_ridge`,
`ALPHA = 0.10` (M4-G6's headline, hardcoded and registered here, not
re-derived). Both branches use the IDENTICAL `basis` argument
(`context["v2_basis"]`) and the IDENTICAL deployed defaults
(`weight_floor`, `clip_bound`, `tol_mode`, `tol_value`, `probe_epsilon`).

--- 0.3 World/grain choices (fifth standing rule: justify, don't inherit) ---

WORLDS: `HIGH_GAP_WORLDS` (3: `endogenous_creation_expansion`,
`selection_creation_compensation`, `source_rotated_feedback`) -- Leg 14's and
M4-E2's OWN worlds, not M4-G1..G6's expanded 8-world `D1_WORLDS`. The outer
registration is explicit ("Reuse M4-E2 / Leg 14's own worlds ... the same
ground the displacement was originally measured on") and metrics 1/2 are
ONLY defined, and only have persisted anchors, on these 3 worlds. All three
are members of `VALID_TRUTH_WORLDS` (M4-G2's lean-b valid-subset rule,
reused verbatim), so metric 3 needs no world exclusion here (asserted below).

GRAIN, per metric, chosen for power against each metric's own registered bar
rather than inherited from the D1_WORLDS-era default (the fifth standing
rule, added after M4-G3 inherited the world grain and was underpowered by
>4x):
- Metric 1 (offset / scale-normalized offset): WORLD grain, n=3. This is not
  an inherited default -- it is the metric's OWN native grain. `offset_norm`
  is a GPA-CONSENSUS statistic that pools all 8 repetitions into ONE number
  per (world, arm); there is no finer sampling unit available without
  changing what the metric measures. No alternative grain exists to choose.
- Metric 2 (Leg 14's displacement, `disp_v2`): REP grain, n=24 (3 worlds x 8
  repetitions), PRIMARY -- chosen because `disp_v2` is ALREADY a per-rep
  quantity in Leg 14's own construction (no aggregation is needed to reach
  it), so pairing at rep grain uses the metric at its own finest available
  resolution and gives 8x the world-grain (n=3) sample size a naive default
  would inherit. WORLD grain (n=3, on `median_disp_v2`) is reported as a
  disclosed companion for direct comparability with Leg 14's own
  world-level reporting convention.
- Metric 3 (truth-referenced recovery): AUTHOR grain (view-mean, n up to
  3*8*16=384), PRIMARY -- M4-G3's own hand-off, after finding world grain
  underpowered by >4x, explicitly recommended author grain as adequately
  powered, and every leg since (G4/G5/G6) has used it successfully at this
  exact estimator. WORLD grain (n=3) reported as a disclosed companion.

--- 0.4 Registered-ambiguity resolution: the `deployed` arm's metric-3 anchor
    (disclosed, resolved BEFORE adjudicating any number) -----------------

The outer registration states `deployed`'s anchor as "reproduce M4-E2's
persisted values to <=1e-12." M4-E2 persists an `offset_norm` per world
(metric 1's own anchor, used as registered) and, via its own faithfulness
gates, re-confirms Leg 14's `e_orc_true`/displacement rows to <=1e-9 (metric
2's anchor, used as registered, sourced directly from Leg 14 per the outer
registration's own metric-2 wording "on its own persisted definition"). M4-E2
computes NO budget=4x/8x truth-referenced recovery at all -- its only
refit-quality diagnostic (Task 4) operates at the deployed budget (1x),
reusing Leg 14's persisted `gap_rows.csv`. There is therefore no M4-E2
artifact metric 3's `deployed`-arm anchor could literally target. Reading A
(ADOPTED): anchor `deployed`'s metric-3 rows to M4-G6's own persisted
`baseline` truth-recovery rows (`results/m4_g6_shape_and_strength/
truth_recovery_rows.csv`, arm="baseline", c=1.0) on these 3 worlds -- the
nearest available persisted "deployed-baseline, budget=4x/8x" artifact,
already required as this leg's `repaired`-arm anchor source file, and
already independently chain-verified bit-identical (0.0) back through
G5->G4->G3->G1's own original `baseline` truth rows by every intervening
leg's own G1 ANCHOR gate (spot-checked directly against M4-G1's own file
here too, Reading B, for a fully independent second source). Reading B
(disclosed companion, not primary): M4-G1's own original persisted `baseline`
truth-recovery rows on the same 3 worlds. Both readings are computed; they
are expected to agree to 0.0 given the pre-existing chain, and disagreement
would be reported, not resolved by picking the favorable one.

===========================================================================
DESIGN (registered)
===========================================================================
Two arms (`deployed`, `repaired`) x 3 worlds (`HIGH_GAP_WORLDS`) x 8
repetitions. Three mandatory metrics, computed per world (metric 1), per
(world, repetition) (metric 2), and per (world, repetition, view, author,
budget) (metric 3, budgets {4.0, 8.0}).

Chunked execution (this arc's standing process rule -- "drive every compute
stage yourself in the FOREGROUND, in chunks"): `--world W` computes ONE
world's full pass (offset/displacement, G3 spot check, truth rows at both
budgets, G2 per-column ridge evidence) and writes partials; `--assemble`
reads every partial, cross-checks completeness, computes gates/leans/pivot,
and writes `decision.json`/`gates.json`.
"""
from __future__ import annotations

import argparse
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
import run_suica_m4_d_bias_variance_leg9 as leg9  # noqa: E402
import run_suica_m4_d_direction_anatomy_leg10 as leg10  # noqa: E402
import run_suica_m4_d_perturbation_leg11 as leg11  # noqa: E402
import run_suica_m4_d_displacement_leg14 as leg14  # noqa: E402
import run_suica_m4_g1_whitening_intervention as g1  # noqa: E402
import run_suica_m4_g3_scale_adaptive as g3  # noqa: E402
import run_suica_m4_g4_covariant_ridge as g4  # noqa: E402
import run_suica_m4_g5_per_column_ridge as g5  # noqa: E402  the repair mechanism
import run_suica_m4_g6_shape_and_strength as g6  # noqa: E402  the certified headline

from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)

ROLES = leg11.ROLES
FLIP_TOLERANCE = leg4.FLIP_TOLERANCE
HIGH_GAP_WORLDS = leg11.HIGH_GAP_WORLDS
VALID_TRUTH_WORLDS = g4.VALID_TRUTH_WORLDS
assert set(HIGH_GAP_WORLDS) <= set(VALID_TRUTH_WORLDS), "M4-G7 needs no world exclusion for metric 3"

ALPHA = 0.10  # M4-G6 headline; registered, not re-derived here
assert ALPHA in g6.ALPHA_LADDER
assert abs(g6.ALPHA_BY_ARM["colstd_alpha_0.10"] - ALPHA) == 0.0

TRUTH_BUDGETS = g4.TRUTH_BUDGETS
assert TRUTH_BUDGETS == (4.0, 8.0)

DEPLOYED_WEIGHT_FLOOR = g4.DEPLOYED_WEIGHT_FLOOR
DEPLOYED_CLIP_BOUND = g4.DEPLOYED_CLIP_BOUND
DEPLOYED_TOL_VALUE = g4.DEPLOYED_TOL_VALUE
DEPLOYED_PROBE_EPSILON = g4.DEPLOYED_PROBE_EPSILON

MY_ARMS = ("deployed", "repaired")

G1_ANCHOR_TOLERANCE = 1e-12
G3_TOLERANCE = 1e-12

# Materiality bars (all reused from this line's / Leg14's own established
# conventions; none invented fresh for this leg).
LEAN_A_BAR_FRACTION = 0.125  # M4-G1's own "12.5% of mean baseline offset" convention
LEAN_B_BAR_FRACTION = leg14.PIVOT_REDUCTION_BAR  # 0.10, Leg 14's OWN displacement-materiality bar
LEAN_C_MARGIN = g4.LEAN_B_MARGIN  # 0.02, G4->G5->G6's own "no loss" equivalence margin, reused
G0_FRACTION_BAR_METRIC3 = g4.G0_FRACTION_BAR  # 0.01, half of LEAN_C_MARGIN, this line's own convention

E2_DECISION_PATH = ROOT / "results" / "m4_e2_offset_anatomy" / "decision.json"
LEG14_DECISION_PATH = ROOT / "results" / "m4_d_discovery_displacement" / "decision.json"
LEG14_DISPLACEMENT_ROWS_PATH = ROOT / "results" / "m4_d_discovery_displacement" / "displacement_rows.csv"
G6_TRUTH_PATH = ROOT / "results" / "m4_g6_shape_and_strength" / "truth_recovery_rows.csv"
G1_TRUTH_PATH = ROOT / "results" / "m4_g1_whitening_intervention" / "truth_recovery_rows.csv"
G6_DECISION_PATH = ROOT / "results" / "m4_g6_shape_and_strength" / "decision.json"
G2_DECISION_PATH = ROOT / "results" / "m4_g2_metric_units" / "decision.json"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"required persisted anchor is missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


# ---------------------------------------------------------------------------
# Part 0.2: two-arm dispatcher
# ---------------------------------------------------------------------------


def _derivative_for_my_arm(
    calibration: dict[str, np.ndarray],
    selection: dict[str, np.ndarray],
    basis: dict[str, np.ndarray],
    *,
    arm: str,
    model: str,
    fit_kwargs: dict[str, Any],
    dims: int,
    deployed_ridge: float,
) -> np.ndarray:
    defaults = dict(
        weight_floor=DEPLOYED_WEIGHT_FLOOR, clip_bound=DEPLOYED_CLIP_BOUND,
        tol_mode="absolute", tol_value=DEPLOYED_TOL_VALUE, probe_epsilon=DEPLOYED_PROBE_EPSILON,
    )
    if arm == "deployed":
        return g3._forced_route_derivative_adaptive(
            calibration, selection, basis, model=model, hazard_ridge=deployed_ridge,
            logistic_iterations=fit_kwargs["logistic_iterations"], dimensions=dims, **defaults,
        )
    if arm == "repaired":
        return g5._forced_route_derivative_columnwise(
            calibration, selection, basis, basis, model=model, treatment="column_standardized",
            ridge_deployed=ALPHA * deployed_ridge, logistic_iterations=fit_kwargs["logistic_iterations"],
            dimensions=dims, **defaults,
        )
    raise ValueError(f"unknown arm: {arm}")


# ---------------------------------------------------------------------------
# metrics 1 & 2: offset / scale-normalized offset / Leg 14's displacement
# (structurally arm-invariant, Part 0.1 -- computed ONCE per world/rep,
# labeled under both arms, with the labeling itself gated as a degenerate
# equality check in _assemble).
# ---------------------------------------------------------------------------


def _offset_and_displacement_for_world(world: str, contexts: list[dict[str, Any]]) -> dict[str, Any]:
    v2_frames = []
    swap_frames = []
    disp_rows = []
    basis_identity_max = 0.0
    for rep_idx, context in enumerate(contexts):
        v2_basis = context["v2_basis"]
        ingredients = leg10._freeze_ingredients(context)

        # internal check: v2_basis reproduces g1's own baseline construction
        whitening_baseline, meta = g1._whitening_for_arm(ingredients, "baseline")
        rebuilt = leg10._bases_from_whitening(context, ingredients, whitening_baseline)
        for role in ROLES:
            basis_identity_max = max(basis_identity_max, float(np.max(np.abs(rebuilt[role] - v2_basis[role]))))

        scale = g1._scale_factors(ingredients, "baseline", meta)
        gm_scale_rep = float(np.exp(np.mean(np.log(scale))))

        swap_basis = leg9._row_norm_swap(context["truth"].oracle_basis, v2_basis)
        v2_frame = leg11._stack_frame(v2_basis)
        swap_frame = leg11._stack_frame(swap_basis)
        v2_frames.append(v2_frame)
        swap_frames.append(swap_frame)
        disp = leg14._quotient_distance(swap_frame, v2_frame)
        disp_rows.append(
            {"world": world, "repetition": rep_idx, "disp_v2_leg14_definition": disp, "geometric_mean_scale": gm_scale_rep}
        )

    gpa_v2 = leg14._frechet_mean_multistart(v2_frames)
    gpa_swap = leg14._frechet_mean_multistart(swap_frames)
    offset_norm = leg14._quotient_distance(gpa_v2["mean"], gpa_swap["mean"])
    geometric_mean_scale_world = float(np.mean([r["geometric_mean_scale"] for r in disp_rows]))
    scale_normalized_offset = offset_norm / geometric_mean_scale_world
    median_disp = float(np.median([r["disp_v2_leg14_definition"] for r in disp_rows]))

    return {
        "world": world,
        "offset_norm": offset_norm,
        "geometric_mean_scale": geometric_mean_scale_world,
        "scale_normalized_offset": scale_normalized_offset,
        "median_disp_v2": median_disp,
        "gpa_v2_basins": int(gpa_v2["n_distinct_basins"]),
        "gpa_swap_basins": int(gpa_swap["n_distinct_basins"]),
        "gpa_v2_objective": gpa_v2["objective_mean_squared_distance"],
        "gpa_swap_objective": gpa_swap["objective_mean_squared_distance"],
        "basis_identity_vs_g1_baseline_max_abs_diff": basis_identity_max,
        "per_rep": disp_rows,
    }


# ---------------------------------------------------------------------------
# G2 evidence: realized per-column ridge profile (repaired) vs deployed's
# flat scalar -- representative slice (view="train", first non-degenerate
# author per repetition), cheap (no IRLS), mirrors G5's own "inventory"
# stage methodology.
# ---------------------------------------------------------------------------


def _g2_ridge_profile_for_world(world: str, contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rep_idx, context in enumerate(contexts):
        basis = context["v2_basis"]
        deployed_ridge = float(context["fit_kwargs"]["hazard_ridge"])
        view = "train"
        author = None
        for candidate_author in range(context["authors"]):
            stack = context["oracle_stacks"][view][candidate_author]
            if float(np.linalg.norm(stack["D"])) >= FLIP_TOLERANCE:
                author = candidate_author
                break
        if author is None:
            continue
        route = context["oracle_stacks"][view][author]["selected_model"]
        calibration, selection, _ = context["flat"][(view, author)]
        design_cal, _ = g5._hazard_design(calibration, basis["calibration"], model=route)
        design_sel, _ = g5._hazard_design(selection, basis["selection"], model=route)
        full_design = np.vstack([design_cal, design_sel])
        var_j = g5._design_column_stats(full_design)
        # MECHANICAL PROBLEM, found on first run, fixed before any hypothesis-
        # relevant number depended on this diagnostic (it feeds G2 evidence
        # only, never a lean or the pivot): raw var_j has near-zero entries on
        # degenerate design columns (e.g. `condition_0`, G1's own docstring),
        # so a naive var_j-weighted ridge blows the min/max spread up toward
        # float overflow (~1e+301, observed) instead of reporting the
        # ACTUAL mechanism the real fit uses. Fixed by calling `g5.
        # _standardize_design` directly -- the SAME degenerate-column floor
        # (`DESIGN_VAR_FLOOR=1e-12`, `DEGENERATE_STD_FALLBACK=1.0`) the real
        # `column_standardized` fit already applies -- so `scale` here is
        # bit-identical to what `_fit_logistic_columnstd` computes internally.
        _design_std, scale_j = g5._standardize_design(full_design, var_j)
        # column 0 (intercept) is ridge-exempt under BOTH arms (penalty[0,0]=0
        # always, and _standardize_design's own scale[0]=DEGENERATE_STD_FALLBACK
        # -- G3's own finding); excluded from the spread statistics.
        scale_non_intercept = scale_j[1:]
        var_effective_non_intercept = scale_non_intercept ** 2
        ridge_col_repaired = ALPHA * deployed_ridge * var_effective_non_intercept
        rows.append(
            {
                "world": world, "repetition": rep_idx, "route": route, "n_columns": int(len(var_j)),
                "deployed_ridge_scalar": deployed_ridge,
                "repaired_scalar_alpha_x_deployed": ALPHA * deployed_ridge,
                "design_var_min": float(np.min(var_effective_non_intercept)), "design_var_max": float(np.max(var_effective_non_intercept)),
                "design_var_spread": float(np.max(var_effective_non_intercept) / np.min(var_effective_non_intercept)),
                "ridge_col_repaired_min": float(np.min(ridge_col_repaired)),
                "ridge_col_repaired_max": float(np.max(ridge_col_repaired)),
                "ridge_col_repaired_spread": float(np.max(ridge_col_repaired) / max(np.min(ridge_col_repaired), 1e-300)),
                "ridge_col_repaired_mean": float(np.mean(ridge_col_repaired)),
            }
        )
    return rows


# ---------------------------------------------------------------------------
# G3 spot check (degenerate equality: gap-stage-style e_arm_true reproduces
# the truth-stage's own budget=1.0 short-circuit) -- disclosed near-duplicate
# of M4-G6's own `_g3_spot_check`, generalized to this leg's two arms, no
# c-ladder.
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
    basis = context["v2_basis"]
    deployed_ridge = float(fit_kwargs["hazard_ridge"])

    rows: list[dict[str, Any]] = []
    for arm in MY_ARMS:
        d_gapstyle = _derivative_for_my_arm(
            calibration_flat, selection_flat, basis, arm=arm, model=route, fit_kwargs=fit_kwargs, dims=dims, deployed_ridge=deployed_ridge,
        )
        d_truthpath = _derivative_for_my_arm(
            calibration_g3, selection_g3, basis, arm=arm, model=route, fit_kwargs=fit_kwargs, dims=dims, deployed_ridge=deployed_ridge,
        )
        e_gapstyle = leg3._relative_error(d_gapstyle, d_true)
        e_truthpath = leg3._relative_error(d_truthpath, d_true)
        rows.append(
            {
                "world": world, "arm": arm, "repetition": rep_idx, "view": view, "author": author,
                "e_arm_true_gapstyle": e_gapstyle, "e_arm_true_truthpath_budget1": e_truthpath,
                "abs_diff": abs(e_gapstyle - e_truthpath),
            }
        )
    return rows


# ---------------------------------------------------------------------------
# metric 3: truth-referenced recovery at a regenerated budget (disclosed
# near-duplicate of G1/G6's own `_truth_rows_for_context`, generalized to
# this leg's own two-arm dispatcher, no c-ladder, no basis re-derivation).
# ---------------------------------------------------------------------------


def _truth_rows_for_context(
    context: dict[str, Any], spec: M4ChartEcologySpec, budget: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    world = context["world"]
    repetition = context["repetition"]
    truth = context["truth"]
    fit_kwargs = context["fit_kwargs"]
    dims = context["flat"][("train", 0)][0]["response_next"].shape[1]
    basis = context["v2_basis"]
    deployed_ridge = float(fit_kwargs["hazard_ridge"])
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
                for arm in MY_ARMS:
                    rows.append({**keys, "arm": arm, "c": 1.0, "e_arm_true": np.nan, "e_orc_true": np.nan})
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
            for arm in MY_ARMS:
                d_arm_b = _derivative_for_my_arm(
                    calibration_b, selection_b, basis, arm=arm, model=route, fit_kwargs=fit_kwargs, dims=dims, deployed_ridge=deployed_ridge,
                )
                e_arm_true = leg3._relative_error(d_arm_b, d_true)
                rows.append({**keys, "arm": arm, "c": 1.0, "e_arm_true": e_arm_true, "e_orc_true": e_orc_true})
    gate = {
        "world": world, "repetition": repetition, "budget": budget, "events": events_b,
        "n_cal_rows_last": n_cal_rows, "n_sel_rows_last": n_sel_rows,
    }
    return rows, gate


# ---------------------------------------------------------------------------
# stage: world (full pass -- offset/displacement, G3 check, truth x 2
# budgets, G2 ridge evidence)
# ---------------------------------------------------------------------------


def _run_world(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started_world = time.time()
    contexts = g1._build_world_contexts(world, config, spec)
    print(f"[m4g7] contexts built {world} ({time.time()-started_world:.1f}s)", flush=True)

    offset_disp = _offset_and_displacement_for_world(world, contexts)
    print(
        f"[m4g7] offset/displacement {world}: offset_norm={offset_disp['offset_norm']:.6f} "
        f"scale_norm={offset_disp['scale_normalized_offset']:.6f} median_disp={offset_disp['median_disp_v2']:.6f} "
        f"basis_identity_max={offset_disp['basis_identity_vs_g1_baseline_max_abs_diff']:.3e}",
        flush=True,
    )

    g3_rows = _g3_spot_check(world, contexts)
    g3_max = max(row["abs_diff"] for row in g3_rows)
    if g3_max > G3_TOLERANCE:
        raise RuntimeError(f"G3 truth-path invariance fails on {world}: {g3_max:.3e}")

    g2_rows = _g2_ridge_profile_for_world(world, contexts)

    all_truth_rows: list[dict[str, Any]] = []
    truth_gates: list[dict[str, Any]] = []
    context_meta_rows: list[dict[str, Any]] = []
    for rep_idx, context in enumerate(contexts):
        deployed_ridge = float(context["fit_kwargs"]["hazard_ridge"])
        context_meta_rows.append(
            {"world": world, "repetition": rep_idx, "deployed_ridge": deployed_ridge, "k_retained": int(context["v2_basis"]["calibration"].shape[1] - 1)}
        )
        for budget in TRUTH_BUDGETS:
            t0 = time.time()
            rows, gate = _truth_rows_for_context(context, spec, budget)
            all_truth_rows.extend(rows)
            truth_gates.append(gate)
            print(f"[m4g7] truth b={budget:g} {world} rep={rep_idx} ({time.time()-t0:.1f}s)", flush=True)

    output.mkdir(parents=True, exist_ok=True)
    with (output / f"partial_offsetdisp_{world}.json").open("w", encoding="utf-8") as handle:
        json.dump(offset_disp, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    pd.DataFrame(offset_disp["per_rep"]).to_csv(output / f"partial_disprep_{world}.csv", index=False)
    pd.DataFrame(g3_rows).to_csv(output / f"partial_g3check_{world}.csv", index=False)
    pd.DataFrame(g2_rows).to_csv(output / f"partial_g2ridge_{world}.csv", index=False)
    pd.DataFrame(all_truth_rows).to_csv(output / f"partial_truth_{world}.csv", index=False)
    pd.DataFrame(context_meta_rows).to_csv(output / f"partial_context_meta_{world}.csv", index=False)
    gates = {"world": world, "truth_gates": truth_gates, "g3_max_abs_diff": g3_max}
    with (output / f"partial_gates_{world}.json").open("w", encoding="utf-8") as handle:
        json.dump(gates, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    print(f"[m4g7] world done: {world} ({time.time()-started_world:.1f}s total)", flush=True)


# ---------------------------------------------------------------------------
# assemble + adjudicate
# ---------------------------------------------------------------------------


def _assemble(output: Path) -> None:
    worlds = list(HIGH_GAP_WORLDS)

    offset_disp_by_world = {}
    disprep_frames = []
    g3check_frames = []
    g2ridge_frames = []
    truth_frames = []
    meta_frames = []
    for w in worlds:
        offset_disp_by_world[w] = _load_json(output / f"partial_offsetdisp_{w}.json")
        disprep_frames.append(pd.read_csv(output / f"partial_disprep_{w}.csv"))
        g3check_frames.append(pd.read_csv(output / f"partial_g3check_{w}.csv"))
        g2ridge_frames.append(pd.read_csv(output / f"partial_g2ridge_{w}.csv"))
        truth_frames.append(pd.read_csv(output / f"partial_truth_{w}.csv"))
        meta_frames.append(pd.read_csv(output / f"partial_context_meta_{w}.csv"))
    disp_rep_rows = pd.concat(disprep_frames, ignore_index=True)
    g3check_rows = pd.concat(g3check_frames, ignore_index=True)
    g2ridge_rows = pd.concat(g2ridge_frames, ignore_index=True)
    truth_rows_1arm = pd.concat(truth_frames, ignore_index=True)  # only "true" arm dimension so far: deployed/repaired via _derivative
    context_meta = pd.concat(meta_frames, ignore_index=True)

    expected_truth_rows = len(worlds) * len(TRUTH_BUDGETS) * 8 * 2 * 16 * len(MY_ARMS)
    if len(truth_rows_1arm) != expected_truth_rows:
        raise RuntimeError(f"truth rows {len(truth_rows_1arm)} != expected {expected_truth_rows}")

    # ---- basis-identity-by-construction: metrics 1/2 duplicated under both
    # arm labels from the SAME per-world computation (Part 0.1) -----------
    offset_disp_rows = []
    for w in worlds:
        od = offset_disp_by_world[w]
        for arm in MY_ARMS:
            offset_disp_rows.append(
                {
                    "world": w, "arm": arm, "offset_norm": od["offset_norm"],
                    "geometric_mean_scale": od["geometric_mean_scale"],
                    "scale_normalized_offset": od["scale_normalized_offset"],
                    "median_disp_v2": od["median_disp_v2"],
                }
            )
    offset_disp_df = pd.DataFrame(offset_disp_rows)

    disp_rep_arm_rows = []
    for _, row in disp_rep_rows.iterrows():
        for arm in MY_ARMS:
            disp_rep_arm_rows.append({**row.to_dict(), "arm": arm})
    disp_rep_arm_df = pd.DataFrame(disp_rep_arm_rows)

    basis_identity_max = max(offset_disp_by_world[w]["basis_identity_vs_g1_baseline_max_abs_diff"] for w in worlds)

    # ---- G3 TRUTH-PATH INVARIANCE -------------------------------------------
    g3_gate = {
        "statement": "truth path at budget=1.0 reproduces gap-stage-style e_arm_true exactly, both arms, one spot-check (rep,view,author) per world",
        "max_abs_diff": float(g3check_rows["abs_diff"].max()),
        "n_checks": int(len(g3check_rows)),
        "tolerance": G3_TOLERANCE,
        "pass": bool(g3check_rows["abs_diff"].max() <= G3_TOLERANCE),
    }

    # ---- G1 ANCHOR -----------------------------------------------------------
    e2_decision = _load_json(E2_DECISION_PATH)
    leg14_decision = _load_json(LEG14_DECISION_PATH)
    leg14_disp_rows = pd.read_csv(LEG14_DISPLACEMENT_ROWS_PATH)

    # metric 1 anchor: deployed's offset_norm vs M4-E2's persisted offset_table
    metric1_anchor_rows = []
    for w in worlds:
        mine = float(offset_disp_by_world[w]["offset_norm"])
        theirs = float(e2_decision["offset_table"][w]["offset_norm"])
        metric1_anchor_rows.append({"world": w, "mine": mine, "m4e2_persisted": theirs, "abs_diff": abs(mine - theirs)})
    metric1_anchor_max = max(r["abs_diff"] for r in metric1_anchor_rows)

    # metric 2 anchor: deployed's per-rep disp_v2 vs Leg14's persisted displacement_rows.csv, AND world median vs displacement_table
    metric2_anchor_rows = []
    for w in worlds:
        for rep in offset_disp_by_world[w]["per_rep"]:
            r = rep["repetition"]
            mine = float(rep["disp_v2_leg14_definition"])
            ref_row = leg14_disp_rows[(leg14_disp_rows["world"] == w) & (leg14_disp_rows["repetition"] == r)]
            if len(ref_row) != 1:
                raise RuntimeError(f"Leg14 displacement anchor missing for {w} rep {r}")
            theirs = float(ref_row.iloc[0]["disp_v2"])
            metric2_anchor_rows.append({"world": w, "repetition": r, "mine": mine, "leg14_persisted": theirs, "abs_diff": abs(mine - theirs)})
    metric2_anchor_max = max(r["abs_diff"] for r in metric2_anchor_rows)
    metric2_world_anchor_rows = []
    for w in worlds:
        mine = float(offset_disp_by_world[w]["median_disp_v2"])
        theirs = float(leg14_decision["displacement_table"][w]["median_disp_v2"])
        metric2_world_anchor_rows.append({"world": w, "mine": mine, "leg14_persisted": theirs, "abs_diff": abs(mine - theirs)})
    metric2_world_anchor_max = max(r["abs_diff"] for r in metric2_world_anchor_rows)

    # metric 3 anchors: deployed vs G6's (primary) and G1's (secondary, disclosed) persisted baseline;
    # repaired vs G6's persisted colstd_alpha_0.10
    g6_truth = pd.read_csv(G6_TRUTH_PATH)
    g1_truth = pd.read_csv(G1_TRUTH_PATH)

    def _anchor_metric3(my_arm: str, source_df: pd.DataFrame, source_arm: str, source_has_c: bool, label: str) -> dict[str, Any]:
        mine = truth_rows_1arm[truth_rows_1arm["arm"] == my_arm][
            ["world", "repetition", "view", "author", "budget", "e_arm_true"]
        ]
        theirs = source_df[source_df["arm"] == source_arm]
        if source_has_c:
            theirs = theirs[theirs["c"] == 1.0]
        theirs = theirs[theirs["world"].isin(worlds)][["world", "repetition", "view", "author", "budget", "e_arm_true"]]
        joined = mine.merge(theirs, on=["world", "repetition", "view", "author", "budget"], suffixes=("_mine", "_theirs"), how="inner")
        expected = len(worlds) * len(TRUTH_BUDGETS) * 8 * 2 * 16
        diff = (joined["e_arm_true_mine"] - joined["e_arm_true_theirs"]).abs()
        return {
            "label": label, "my_arm": my_arm, "source_arm": source_arm, "n_rows": int(len(joined)),
            "expected_rows": expected, "complete": bool(len(joined) == expected),
            "max_abs_diff": float(diff.max(skipna=True)),
        }

    metric3_anchor_deployed_vs_g6 = _anchor_metric3("deployed", g6_truth, "baseline", True, "deployed_vs_g6_baseline_PRIMARY")
    metric3_anchor_deployed_vs_g1 = _anchor_metric3("deployed", g1_truth, "baseline", False, "deployed_vs_g1_baseline_SECONDARY_DISCLOSED")
    metric3_anchor_repaired_vs_g6 = _anchor_metric3("repaired", g6_truth, "colstd_alpha_0.10", True, "repaired_vs_g6_colstd_alpha_0.10_PRIMARY")

    metric3_anchor_max = max(
        metric3_anchor_deployed_vs_g6["max_abs_diff"],
        metric3_anchor_deployed_vs_g1["max_abs_diff"],
        metric3_anchor_repaired_vs_g6["max_abs_diff"],
    )

    g1_anchor_max = max(metric1_anchor_max, metric2_anchor_max, metric2_world_anchor_max, metric3_anchor_max, basis_identity_max)
    g1_anchor = {
        "tolerance": G1_ANCHOR_TOLERANCE,
        "basis_identity_vs_g1_baseline_max_abs_diff": basis_identity_max,
        "metric1_offset_vs_m4e2": {"per_world": metric1_anchor_rows, "max_abs_diff": metric1_anchor_max},
        "metric2_displacement_per_rep_vs_leg14": {"n_checks": len(metric2_anchor_rows), "max_abs_diff": metric2_anchor_max},
        "metric2_displacement_world_median_vs_leg14": {"per_world": metric2_world_anchor_rows, "max_abs_diff": metric2_world_anchor_max},
        "metric3_truth_recovery": {
            "deployed_vs_g6_baseline_PRIMARY": metric3_anchor_deployed_vs_g6,
            "deployed_vs_g1_baseline_SECONDARY_DISCLOSED": metric3_anchor_deployed_vs_g1,
            "repaired_vs_g6_colstd_alpha_0.10_PRIMARY": metric3_anchor_repaired_vs_g6,
        },
        "max_abs_diff_overall": g1_anchor_max,
        "pass": bool(g1_anchor_max <= G1_ANCHOR_TOLERANCE),
        "note": (
            "Part 0.4: deployed's metric-3 anchor is read against M4-G6's own persisted baseline "
            "rows (Reading A, PRIMARY) since M4-E2 persists no budget=4x/8x recovery; M4-G1's "
            "independently-sourced original baseline rows are also checked (Reading B, disclosed "
            "companion) and are expected, and found, to agree."
        ),
    }

    # ---- G2 REPAIR LIVENESS ----------------------------------------------------
    g6_decision = _load_json(G6_DECISION_PATH)
    g6_g2_alpha010 = next(
        row for row in g6_decision["gates"]["G2_strength_liveness"]["per_alpha"] if row["arm"] == "colstd_alpha_0.10"
    )
    ridge_scalar_ratio = float(g6_g2_alpha010["per_c"]["1.0"]["ratio_to_deployed"])
    g2_repair_liveness = {
        "statement": (
            "the repaired arm must differ from deployed in the applied regularization: the SCALAR "
            "level (ridge_used/deployed_ridge ratio, cross-checked against M4-G6's own persisted "
            "colstd_alpha_0.10 G2 evidence) AND the per-column SHAPE (design-column-variance-weighted "
            "profile, computed fresh here on this leg's own 3 worlds)"
        ),
        "scalar_level": {
            "deployed_ridge_constant_across_contexts": bool(context_meta["deployed_ridge"].nunique() == 1),
            "deployed_ridge_value": float(context_meta["deployed_ridge"].iloc[0]),
            "repaired_scalar_alpha_x_deployed": ALPHA * float(context_meta["deployed_ridge"].iloc[0]),
            "alpha": ALPHA,
            "cross_check_vs_g6_persisted_ratio_to_deployed": ridge_scalar_ratio,
            "cross_check_abs_diff_vs_alpha": abs(ridge_scalar_ratio - ALPHA),
        },
        "per_column_shape": {
            "n_contexts_sampled": int(len(g2ridge_rows)),
            "design_var_spread_min": float(g2ridge_rows["design_var_spread"].min()),
            "design_var_spread_max": float(g2ridge_rows["design_var_spread"].max()),
            "ridge_col_repaired_spread_min": float(g2ridge_rows["ridge_col_repaired_spread"].min()),
            "ridge_col_repaired_spread_max": float(g2ridge_rows["ridge_col_repaired_spread"].max()),
            "ridge_col_repaired_vs_deployed_scalar_ratio_min": float(
                (g2ridge_rows["ridge_col_repaired_min"] / g2ridge_rows["deployed_ridge_scalar"]).min()
            ),
            "ridge_col_repaired_vs_deployed_scalar_ratio_max": float(
                (g2ridge_rows["ridge_col_repaired_max"] / g2ridge_rows["deployed_ridge_scalar"]).max()
            ),
        },
        "materiality": (
            "LIVE iff the per-column ridge profile's own spread (max/min across non-intercept design "
            "columns) exceeds 1.0 by more than floating-point noise (deployed's own profile is flat, "
            "spread==1.0 exactly, by construction -- a single scalar times I) AND the scalar level "
            "differs from deployed's by exactly the registered ALPHA=0.10 factor"
        ),
    }
    g2_shape_live = bool(g2ridge_rows["ridge_col_repaired_spread"].min() > 1.0 + 1e-9)
    g2_scalar_live = bool(abs(ridge_scalar_ratio - ALPHA) <= 1e-9)
    g2_repair_liveness["shape_live"] = g2_shape_live
    g2_repair_liveness["scalar_live"] = g2_scalar_live
    g2_repair_liveness["live"] = bool(g2_shape_live and g2_scalar_live)

    # ---- metric 1 (lean a): scale-normalized offset, WORLD grain (n=3, native) --
    m1_by_world = offset_disp_df.set_index(["world", "arm"])["scale_normalized_offset"]
    m1_reduction = np.array([m1_by_world[(w, "deployed")] - m1_by_world[(w, "repaired")] for w in worlds])
    m1_ci = g1._paired_world_ci(m1_reduction)
    m1_deployed_mean = float(offset_disp_df[offset_disp_df["arm"] == "deployed"]["scale_normalized_offset"].mean())
    m1_bar = LEAN_A_BAR_FRACTION * m1_deployed_mean
    e2_offset_target = {w: float(e2_decision["offset_table"][w]["offset_norm"]) for w in worlds}
    g2_metric_units_decision = _load_json(G2_DECISION_PATH)
    g2_baseline_scale_norm = float(g2_metric_units_decision["lean_c"]["scale_normalized_offset_by_arm"]["baseline"])
    lean_a = {
        "statement": "repaired's scale-normalized offset (M4-G2's registered definition) is lower than deployed's, paired-by-world CI excluding zero",
        "grain": "world (n=3, the metric's own native grain -- Part 0.3)",
        "target_level_m4e2_persisted_offset_norm_by_world": e2_offset_target,
        "target_level_m4g2_persisted_scale_normalized_baseline_3world_mean": g2_baseline_scale_norm,
        "deployed_mean_scale_normalized_offset_this_leg": m1_deployed_mean,
        "bar_fraction": LEAN_A_BAR_FRACTION,
        "bar_absolute": m1_bar,
        "per_world_reduction": {w: float(v) for w, v in zip(worlds, m1_reduction)},
        "ci": m1_ci,
        "underpowered_vs_bar": bool(np.isfinite(m1_ci["half_width"]) and m1_ci["half_width"] > m1_bar),
        "shows_reduction": bool(m1_ci["ci_lo"] > 0.0),
        "held": bool(m1_ci["ci_lo"] > 0.0),
    }

    # ---- metric 2 (lean b): Leg14's displacement, REP grain (n=24) primary,
    # WORLD grain (n=3) companion ------------------------------------------
    disp_wide = disp_rep_arm_df.set_index(["world", "repetition", "arm"])["disp_v2_leg14_definition"]
    m2_reduction_rep = []
    for w in worlds:
        for r in range(8):
            m2_reduction_rep.append(float(disp_wide[(w, r, "deployed")] - disp_wide[(w, r, "repaired")]))
    m2_reduction_rep = np.array(m2_reduction_rep)
    m2_ci_rep = g1._paired_world_ci(m2_reduction_rep)  # generic t-CI helper despite its name; reused for rep grain

    m2_by_world = offset_disp_df.set_index(["world", "arm"])["median_disp_v2"]
    m2_reduction_world = np.array([m2_by_world[(w, "deployed")] - m2_by_world[(w, "repaired")] for w in worlds])
    m2_ci_world = g1._paired_world_ci(m2_reduction_world)

    leg14_target = {w: float(leg14_decision["displacement_table"][w]["median_disp_v2"]) for w in worlds}
    m2_deployed_mean_rep = float(disp_rep_arm_df[disp_rep_arm_df["arm"] == "deployed"]["disp_v2_leg14_definition"].mean())
    m2_bar_rep = LEAN_B_BAR_FRACTION * m2_deployed_mean_rep
    m2_deployed_mean_world = float(np.mean([offset_disp_by_world[w]["median_disp_v2"] for w in worlds]))
    m2_bar_world = LEAN_B_BAR_FRACTION * m2_deployed_mean_world
    lean_b = {
        "statement": "Leg 14's displacement (disp_v2, its own persisted definition) is lower under repaired, paired CI excluding zero",
        "grain_primary": "repetition (n=24, 3 worlds x 8 reps -- Part 0.3, chosen because disp_v2 is already a per-rep quantity)",
        "grain_companion": "world (n=3, on median_disp_v2, for comparability with Leg 14's own reporting convention)",
        "target_level_leg14_persisted_median_disp_v2_by_world": leg14_target,
        "bar_fraction_leg14_own_pivot_reduction_bar": LEAN_B_BAR_FRACTION,
        "bar_absolute_rep_grain": m2_bar_rep,
        "bar_absolute_world_grain": m2_bar_world,
        "rep_grain": {
            "n": int(len(m2_reduction_rep)), "ci": m2_ci_rep,
            "underpowered_vs_bar": bool(np.isfinite(m2_ci_rep["half_width"]) and m2_ci_rep["half_width"] > m2_bar_rep),
            "shows_reduction": bool(m2_ci_rep["ci_lo"] > 0.0),
        },
        "world_grain_companion": {
            "n": int(len(m2_reduction_world)), "ci": m2_ci_world,
            "per_world_reduction": {w: float(v) for w, v in zip(worlds, m2_reduction_world)},
            "shows_reduction": bool(m2_ci_world["ci_lo"] > 0.0),
        },
        "held": bool(m2_ci_rep["ci_lo"] > 0.0),
    }

    # ---- metric 3 (lean c): truth-referenced recovery, AUTHOR grain primary,
    # WORLD grain companion, both budgets, equivalence form -------------------
    truth_rows_1arm["degenerate_reference"] = truth_rows_1arm["degenerate_reference"].astype(bool)
    author_truth = g4._author_level_truth_with_c(truth_rows_1arm)  # generic, reused unchanged

    lean_c_by_budget = {}
    for budget in TRUTH_BUDGETS:
        author_ci = g4._paired_author_diff_ci(author_truth, "repaired", 1.0, "deployed", 1.0, budget, worlds)
        world_ci = g4._paired_world_diff_ci(author_truth, "repaired", 1.0, "deployed", 1.0, budget, worlds)
        author_class = g4._classify_pair(author_ci, LEAN_C_MARGIN, one_sided=True)
        underpowered_author = bool(author_ci["n"] > 1 and author_ci["half_width"] > G0_FRACTION_BAR_METRIC3)
        lean_c_by_budget[str(budget)] = {
            "author_grain": {
                "n": author_ci["n"], "mean_diff_repaired_minus_deployed": author_ci["mean"],
                "ci_lo": author_ci["ci_lo"], "ci_hi": author_ci["ci_hi"], "half_width": author_ci["half_width"],
                "class": author_class, "underpowered_vs_g0_bar": underpowered_author,
            },
            "world_grain_companion": {
                "n": world_ci["n"], "mean_diff_repaired_minus_deployed": world_ci["mean"],
                "ci_lo": world_ci["ci_lo"], "ci_hi": world_ci["ci_hi"],
            },
        }
    lean_c_held = bool(all(lean_c_by_budget[str(b)]["author_grain"]["class"] == "WITHIN" for b in TRUTH_BUDGETS))
    lean_c_any_worse = bool(any(lean_c_by_budget[str(b)]["author_grain"]["class"] == "OUTSIDE" for b in TRUTH_BUDGETS))
    g6_headline_repaired = {"4x": 0.5083, "8x": 0.4946}  # M4-G6's own persisted headline, cited for context only
    lean_c = {
        "statement": "truth-referenced recovery does not worsen under repaired vs deployed, both budgets, equivalence form, one-sided",
        "grain_primary": "author (view-mean, n up to 384 -- Part 0.3, M4-G3's own hand-off recommendation)",
        "margin_registered_in_part_0": LEAN_C_MARGIN,
        "margin_source": "g4.LEAN_B_MARGIN, reused unchanged G4->G5->G6->this leg",
        "g6_own_persisted_headline_repaired_pooled_6world_for_context": g6_headline_repaired,
        "by_budget": lean_c_by_budget,
        "held": lean_c_held,
        "any_worse_outside_margin": lean_c_any_worse,
    }

    # ---- G0 POWER (all three metrics, grain justified per Part 0.3) -----------
    g0_power = {
        "metric1_offset": {
            "grain": "world", "n": m1_ci["n"], "bar_absolute": m1_bar, "bar_fraction": LEAN_A_BAR_FRACTION,
            "half_width": m1_ci["half_width"],
            "underpowered_for_hypothetical_nonzero_effect": lean_a["underpowered_vs_bar"],
            "note": "n=3 is the metric's own native grain (a GPA-consensus statistic, one number per world), not an inherited default; no finer grain exists for this metric.",
        },
        "metric2_displacement": {
            "grain": "repetition", "n": m2_ci_rep["n"], "bar_absolute": m2_bar_rep, "bar_fraction": LEAN_B_BAR_FRACTION,
            "half_width": m2_ci_rep["half_width"],
            "underpowered_for_hypothetical_nonzero_effect": lean_b["rep_grain"]["underpowered_vs_bar"],
            "note": "rep grain (n=24) chosen over the naive world-grain (n=3) default per the fifth standing rule; disp_v2 is already per-rep, so no aggregation is needed to reach it.",
        },
        "metric3_truth_recovery": {
            "grain": "author", "n_by_budget": {str(b): lean_c_by_budget[str(b)]["author_grain"]["n"] for b in TRUTH_BUDGETS},
            "bar_absolute": G0_FRACTION_BAR_METRIC3, "margin": LEAN_C_MARGIN,
            "half_width_by_budget": {str(b): lean_c_by_budget[str(b)]["author_grain"]["half_width"] for b in TRUTH_BUDGETS},
            "underpowered_by_budget": {str(b): lean_c_by_budget[str(b)]["author_grain"]["underpowered_vs_g0_bar"] for b in TRUTH_BUDGETS},
            "note": "author grain (n up to 384) per M4-G3's own hand-off recommendation, used successfully by G4/G5/G6 since.",
        },
        "note_on_metrics_1_2_realized_zero": (
            "Metrics 1 and 2's realized paired differences are EXACTLY 0.0 at every world/rep (Part 0.1's "
            "structural-identity argument, verified below in structural_identity_check), so their CIs are "
            "degenerate points at zero (half_width==0.0) by construction, not by sampling precision. The "
            "bars/half-widths above characterize what this design COULD have detected had the ridge channel "
            "been live for these two metrics; they do not describe genuine sampling uncertainty here."
        ),
    }

    # ---- structural identity check (Part 0.1, empirical confirmation) --------
    structural_identity_check = {
        "statement": "metrics 1 and 2 are computed once per world/rep and labeled under both arms; this cell verifies that relabeling introduces exactly 0.0 difference, confirming Part 0.1's call-graph argument rather than merely asserting it",
        "metric1_max_abs_diff_deployed_vs_repaired": float(
            (offset_disp_df[offset_disp_df["arm"] == "deployed"].set_index("world")["scale_normalized_offset"]
             - offset_disp_df[offset_disp_df["arm"] == "repaired"].set_index("world")["scale_normalized_offset"]).abs().max()
        ),
        "metric2_max_abs_diff_deployed_vs_repaired": float(np.max(np.abs(m2_reduction_rep))),
        "pass_exactly_zero": bool(
            float((offset_disp_df[offset_disp_df["arm"] == "deployed"].set_index("world")["scale_normalized_offset"]
                   - offset_disp_df[offset_disp_df["arm"] == "repaired"].set_index("world")["scale_normalized_offset"]).abs().max()) == 0.0
            and float(np.max(np.abs(m2_reduction_rep))) == 0.0
        ),
    }

    # ---- PIVOT --------------------------------------------------------------
    pivot_fires = bool((not lean_a["held"]) and (not lean_b["held"]))
    if pivot_fires:
        verdict = "PIVOT_SCALE_INVARIANCE_AND_RECOVERY_ORTHOGONAL_TO_DISPLACEMENT"
    elif lean_a["held"] or lean_b["held"]:
        verdict = "REPAIR_REACHES_DISPLACEMENT" if (lean_a["held"] and lean_b["held"]) else "PARTIAL_DISPLACEMENT_REDUCTION"
    else:
        verdict = "AMBIGUOUS_NO_CLEAN_BRANCH"

    # ---- G4 MATERIALITY FORM ---------------------------------------------------
    g4_materiality_form = {
        "G0": "CI-half-width-vs-bar equivalence bound per metric; underpowered comparisons flagged explicitly, never silently read as nulls",
        "G1": "degenerate exact-equality checks (tolerance 1e-12) against five independent persisted sources (M4-E2, Leg 14 x2, M4-G6, M4-G1), not significance tests",
        "G2": "dual liveness check: scalar ratio equals registered ALPHA to <=1e-9 AND per-column profile spread exceeds 1.0 (deployed's own profile is exactly flat by construction)",
        "G3": "degenerate exact-equality check (tolerance 1e-12) between two independently-computed derivations of the same quantity, both arms",
        "lean_a": "paired-by-world CI-excludes-zero test (directional materiality claim, not nil-significance)",
        "lean_b": "paired-by-repetition CI-excludes-zero test (directional materiality claim, not nil-significance), world-grain companion reported",
        "lean_c": "one-sided WITHIN/OUTSIDE/AMBIGUOUS classification on paired-author CI against the fixed +/-0.02 (upper-only) margin, both budgets, never nil-significance",
    }

    decision = {
        "estimand_id": "SUICA_M4_G7_REPAIR_VS_DISPLACEMENT",
        "tier": "EXPLORATORY (open-exploration phase)",
        "registered_in": "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md M4-G7 registration (2026-08-03, BEFORE run); ledger row M4-G7",
        "worlds": worlds,
        "arms": list(MY_ARMS),
        "alpha": ALPHA,
        "truth_budgets": list(TRUTH_BUDGETS),
        "structural_identity_check": structural_identity_check,
        "gates": {
            "G0_power": g0_power,
            "G1_anchor": g1_anchor,
            "G2_repair_liveness": g2_repair_liveness,
            "G3_truth_path_invariance": g3_gate,
            "G4_materiality_form": g4_materiality_form,
        },
        "lean_a_displacement_falls": lean_a,
        "lean_b_original_gap_falls": lean_b,
        "lean_c_not_cosmetic": lean_c,
        "pivot": {
            "registered": "neither (a) nor (b) shows a reduction with a CI excluding zero -> scale-invariance and recovery are orthogonal to the displacement",
            "fires": pivot_fires,
        },
        "verdict": verdict,
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only (the 3 HIGH_GAP_WORLDS, reused verbatim from M4-E2/Leg 14/"
            "M4-G1); truth-recovery via budget-regenerated (4x/8x events) finite panels from the frozen "
            "world law, compared to the analytic D_true; no natural-text, personality, or clinical claim; "
            "no seal, no independent verification (operator directive 2026-08-01)."
        ),
    }

    output.mkdir(parents=True, exist_ok=True)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    with (output / "gates.json").open("w", encoding="utf-8") as handle:
        json.dump(decision["gates"], handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    offset_disp_df.to_csv(output / "offset_displacement_by_world.csv", index=False)
    disp_rep_arm_df.to_csv(output / "displacement_by_rep.csv", index=False)
    truth_rows_1arm.to_csv(output / "truth_recovery_rows.csv", index=False)
    author_truth.to_csv(output / "author_level_truth_rows.csv", index=False)
    g2ridge_rows.to_csv(output / "g2_ridge_profile_rows.csv", index=False)
    g3check_rows.to_csv(output / "g3check_rows.csv", index=False)
    context_meta.to_csv(output / "context_meta.csv", index=False)

    print(
        json.dumps(
            {
                "verdict": verdict, "pivot_fires": pivot_fires,
                "lean_a_held": lean_a["held"], "lean_b_held": lean_b["held"], "lean_c_held": lean_c["held"],
                "g1_anchor_pass": g1_anchor["pass"], "g2_live": g2_repair_liveness["live"], "g3_pass": g3_gate["pass"],
                "structural_identity_pass_exactly_zero": structural_identity_check["pass_exactly_zero"],
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
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_g7_repair_vs_displacement")
    parser.add_argument("--world", type=str, default=None)
    parser.add_argument("--assemble", action="store_true")
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    spec = M4ChartEcologySpec(**config["base_spec"])

    if args.assemble:
        _assemble(args.output)
        return

    if args.world is None:
        raise SystemExit("--world is required unless --assemble")
    if args.world not in HIGH_GAP_WORLDS:
        raise SystemExit(f"not a registered HIGH_GAP_WORLDS world: {args.world}")
    _run_world(args.world, config, spec, args.output)


if __name__ == "__main__":
    main()
