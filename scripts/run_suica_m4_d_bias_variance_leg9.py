#!/usr/bin/env python3
"""M4-D Leg 9: the bias-variance account of the paired floor + gap anatomy.

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
"Leg 9 -- the bias-variance account of the paired floor + gap anatomy",
2026-08-02 loop cycle 4, commit 0f3ada7, BEFORE this run). All machinery is
IMPORTED from the validated legs -- Leg 4's floor protocol + budget panels,
Leg 5's two-stage, Leg 7's frozen-law realization mechanism and persisted-row
asserts, Leg 8's flexible-penalty lever fits -- nothing is reimplemented.

THE QUESTION. Leg 8 ended with the third consecutive stacking failure:
de-biased D (A_lam1n, oracle-own-error .376 -> .261) DAMAGES paired transport
(.6248 < .7605). Emerging hypothesis: the paired disc-vs-oracle metric REWARDS
the V2 ridge's variance reduction; the loop floor is a BIAS-VARIANCE
EQUILIBRIUM, not a hard limit. If true, the equilibrium must shift with
budget: at 4x the variance term shrinks, the de-biased estimator's penalty
fades, and the two-stage ranking INVERTS.

ARM A (bias-variance decomposition + ranking inversion; registered):
for D estimators {V2 ridge, lam1n, unpen} x budgets {1x, 4x}: R=8 fresh path
realizations of the frozen law per world-rep (Leg 7's offset mechanism,
extended to the 4x event budget). Per cell (world-rep x view x author x
estimator x budget), with per-realization paired difference
delta_r = D_disc_r - D_orc_r (each estimator paired against ITS OWN
oracle-basis twin, Leg-4b semantics) and reference scale ||mean_r D_orc_r||:
  bias_rel  = ||mean_r delta_r|| / ||mean_r D_orc_r||   (R-averaged estimate
              vs the oracle-basis pairing -- the registered bias term)
  var_rel   = mean_r ||delta_r - mean delta||^2 / ||mean_r D_orc_r||^2
  total_rel = mean_r ||delta_r||^2 / ||mean_r D_orc_r||^2
            = bias_rel^2 + var_rel  (exact identity, asserted per cell)
Then the FULL two-stage 5x8 battery with each estimator as the stage-2 refit
at 1x AND 4x (6 batteries; stage 1 is Leg 5's stage 1 bit-exact in all six):
  two_stage           = V2 ridge @ 1x (Leg 5 bit-exact, asserted)
  ts_v2ridge_4x       = V2 semantics refit on the canonical 4x panels
  ts_lam1n_1x         = Leg 8's two_stage_lever bit-exact (asserted)
  ts_lam1n_4x / ts_unpen_1x / ts_unpen_4x = fresh lever refits
The decisive numbers: two-stage pooled loop geometry per estimator per budget.

UNREGISTERED-SECONDARY (coordinator addition, clearly separated, NO
adjudication weight): the paired metric's oracle endpoint is V2-ridge-fitted
and so RETAINS the ridge bias; alongside every registered (V2-paired) number
the same statistic is computed against a LAM1N-FITTED oracle reference
(reusing the lam1n oracle-side fits Arm A produces anyway -- no added
compute): per-cell decomposition columns *_lam1nref, and battery loop
geometry against reference loops D_orc_lam1n @ G_orc @ C_orc at the matching
budget. If the registered inversion fails on the V2-paired column but holds
on the lam1n-paired column, that localizes the floor to REFERENCE BIAS in
the pairing itself; the distinction is recorded in the pivot adjudication
(the registered leans still adjudicate on the registered column only).

ARM B (gap content-swap; registered): in the three high-gap worlds
(expansion / compensation / rotated, per-world estimator-minus-oracle gap
.21-.26 at Leg 8), the .13-pooled basis-mismatch gap is not orientation
(Leg 8's Procrustes alignment INVERTED it), so the remaining factorization of
a basis is row DIRECTIONS (what mixture of conditions each category loads --
"basis content") x row NORMS (how strongly each category participates in the
design and the probes -- "support-weighting"). Swap refits at the
oracle-forced route, V2 estimator semantics, 1x battery panels:
  swap_i  (oracle content + discovered support-weights):
          B_i[role][k,:]  = B_orc[role][k,:] * s_disc[role,k]/s_orc[role,k]
  swap_ii (discovered content + oracle support-weights):
          B_ii[role][k,:] = B_disc[role][k,:] * s_orc[role,k]/s_disc[role,k]
  (s = euclidean row norm per role; rows with s < 1e-12 keep scale 1;
  swap_i has oracle width 7, swap_ii discovered width 12-13 -- width travels
  with the direction source.)
ATTRIBUTION FORMULA (stated here, computed on world-level author-median
gaps): the four corners of the 2x2 factorial {content, weights} are
  gap(disc,disc) = gap_v2, gap(orc,disc) = gap_i, gap(disc,orc) = gap_ii,
  gap(orc,orc) = 0 (the oracle refit is its own reference), where each
  gap_* = median_author(e_*_true - e_orc_true). Symmetric (Shapley) main
  effects:
  content_effect = 0.5 * [(gap_v2 - gap_i) + (gap_ii - 0)]
  weight_effect  = 0.5 * [(gap_v2 - gap_ii) + (gap_i - 0)]
  content_effect + weight_effect = gap_v2 exactly;
  basis_content_share = content_effect / gap_v2.

ARM C (partition reference check; registered): Leg 4's report flagged that
the generator masks generated_next by an exogenous ENVELOPE in
endogenous_source_partition_matched (generated_next &= envelope_next), so the
analytic latent-law derivative OVERSTATES the observable hazard derivative
there (reference gap .645 vs .270-.389 elsewhere). In this world the total
menu IS the envelope (generated = env & B, external = env & ~generated, so
external|generated = env exactly), and the envelope chain
P(env_next) = .24*env + .76*.62 has stationary marginal exactly .62 (fixed
point; initial draw also .62), independent of the response stream. The
envelope-corrected observable reference is therefore
  D_true_env = p_env * D_true,  p_env measured per world-rep as the mean
  menu occupancy of the 1x calibration+selection panels (both views;
  analytic .62 as cross-check),
and the law-level bias is recomputed as
  e_orc_true_env = ||D_orc_est - p_env*D_true|| / (p_env*||D_true||)
for all three estimators at natural 1x (r=0), with 4x companions and a
least-squares scale diagnostic c* = <D_hat, D_true>/||D_true||^2.

REGISTERED LEANS (adjudication statistics pre-coded here):
- (a) the bias-variance signature appears: pooled author-level median
  bias_rel(lam1n) < bias_rel(v2ridge) AND var_rel(lam1n) > var_rel(v2ridge)
  at 1x, the same for unpen, AND the two-stage ranking INVERTS at 4x
  (pooled ts_lam1n_4x >= pooled ts_v2ridge_4x while ts_lam1n_1x <
  two_stage at 1x).
- (b) basis_content_share >= .70 in >= 2 of the 3 high-gap worlds.
- (c) partition's law-level bias at least halves under the corrected
  reference: lam1n natural-1x partition median e_orc_true_env <= .30
  (from .592 latent).
PIVOT-IF (registered): the inversion does NOT appear at 4x (pooled
ts_lam1n_4x < pooled ts_v2ridge_4x) -> the bias-variance account of the
floor DIES (recorded plainly); the paired floor's last layer is the gap
itself; next instrument = the information-operator conditioning profile
already persisted at results/m4_d_bias_anatomy/conditioning_rows.csv,
elevated to a full leg. The unregistered-secondary column may QUALIFY the
death (reference-bias localization) but cannot cancel it.

Chunked execution (this arc's battery-then-stall workaround): --chunk-start/
--chunk-stop [--worlds] run world-rep ranges in the foreground writing
partial CSVs; --assemble concatenates all partials, REFUSES missing or
duplicate cells, and adjudicates from the concatenated rows only.
"""
from __future__ import annotations

import argparse
import glob
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
import run_suica_m4_d_two_stage_leg5 as leg5  # noqa: E402
import run_suica_m4_d_excitation_floor_leg6 as leg6  # noqa: E402
import run_suica_m4_d_realization_averaging_leg7 as leg7  # noqa: E402
import run_suica_m4_d_bias_anatomy_leg8 as leg8  # noqa: E402

from suica_core.m4_chart_ecology_estimator import (  # noqa: E402
    _creation_action,
    _feedback_derivative,
    _fit_hazard_candidate,
    _flatten_events,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)

LOOP_WORLDS = leg3.LOOP_WORLDS
ESTIMATORS = ("v2ridge", "lam1n", "unpen")
LEVER_ARM_OF = {"lam1n": "A_lam1n", "unpen": "A_unpen"}
BUDGETS = (1.0, 4.0)
N_PANELS = 8
REALIZATION_OFFSET = leg7.REALIZATION_OFFSET  # 1_000_000_007
STAGE1_LAMBDA = leg5.STAGE1_LAMBDA  # 0.125
ROW_TOLERANCE = 1e-9
IDENTITY_TOLERANCE = 1e-9
HIGH_GAP_WORLDS = (
    "endogenous_creation_expansion",
    "selection_creation_compensation",
    "source_rotated_feedback",
)
PARTITION_WORLD = "endogenous_source_partition_matched"
ENV_STATIONARY = 0.62
BATTERY_ARMS = (
    "arm2_stage1_125",
    "two_stage",
    "ts_v2ridge_4x",
    "ts_lam1n_1x",
    "ts_lam1n_4x",
    "ts_unpen_1x",
    "ts_unpen_4x",
)
BATTERY_CELLS = {
    # arm -> (estimator, budget); two_stage is the v2ridge @ 1x cell
    "two_stage": ("v2ridge", 1.0),
    "ts_v2ridge_4x": ("v2ridge", 4.0),
    "ts_lam1n_1x": ("lam1n", 1.0),
    "ts_lam1n_4x": ("lam1n", 4.0),
    "ts_unpen_1x": ("unpen", 1.0),
    "ts_unpen_4x": ("unpen", 4.0),
}
LEAN_B_SHARE_BAR = 0.70
LEAN_B_MIN_WORLDS = 2
LEAN_C_BAR = 0.30
LEG8_PARTITION_LAM1N_1X = 0.5921732428072295  # persisted comparator


# ---------------------------------------------------------------------------
# persisted references (refused if absent -- registered comparators)
# ---------------------------------------------------------------------------


def _load_leg8_lever_reference() -> pd.DataFrame:
    """Leg 8 persisted natural lever rows (A_lam1n / A_unpen at 1x and 4x)."""
    rows_path = ROOT / "results" / "m4_d_bias_anatomy" / "lever_rows.csv"
    decision_path = ROOT / "results" / "m4_d_bias_anatomy" / "decision.json"
    if not rows_path.exists() or not decision_path.exists():
        raise RuntimeError(
            "Leg 8 persisted lever artifacts are required references and "
            f"were not found: {rows_path} / {decision_path}"
        )
    stored = pd.read_csv(rows_path)
    stored = stored[
        (stored["panel"] == "natural")
        & (stored["arm"].isin(tuple(LEVER_ARM_OF.values())))
    ].copy()
    with decision_path.open("r", encoding="utf-8") as handle:
        decision = json.load(handle)
    lam1n_1x = float(
        decision["law_level_table"]["natural"]["A_lam1n"]["1x"][
            "pooled_median"
        ]
    )
    if abs(lam1n_1x - 0.2605) > 0.005:
        raise RuntimeError(
            f"Leg 8 persisted A_lam1n natural 1x pooled {lam1n_1x:.4f} is "
            "not the registered ~.2605 comparator; reference battery is not "
            "the one registered"
        )
    return stored


def _load_leg8_stack_reference() -> pd.DataFrame:
    """Leg 8 persisted two_stage_lever rows (the lam1n@1x battery, .6248)."""
    rows_path = (
        ROOT / "results" / "m4_d_bias_anatomy" / "stack_per_loop_metrics.csv"
    )
    decision_path = ROOT / "results" / "m4_d_bias_anatomy" / "decision.json"
    if not rows_path.exists():
        raise RuntimeError(
            "Leg 8 persisted stack rows are a required reference and were "
            f"not found: {rows_path}"
        )
    with decision_path.open("r", encoding="utf-8") as handle:
        decision = json.load(handle)
    pooled = float(
        decision["bias_ledger"]["loop_transport"]["two_stage_lever_pooled"]
    )
    if abs(pooled - 0.6248) > 0.005:
        raise RuntimeError(
            f"Leg 8 persisted two_stage_lever pooled {pooled:.4f} is not "
            "the registered ~.6248 comparator; reference battery is not the "
            "one registered"
        )
    composition_path = (
        ROOT / "results" / "m4_d_bias_anatomy" / "stack_composition.json"
    )
    with composition_path.open("r", encoding="utf-8") as handle:
        composition = json.load(handle)
    if (
        composition["estimator_lever"] != "A_lam1n"
        or composition["frame"] != "v2"
    ):
        raise RuntimeError(
            "Leg 8 stack composition is not lam1n @ v2 frame "
            f"({composition['estimator_lever']} @ {composition['frame']}); "
            "the ts_lam1n_1x reproduction assert would be vacuous"
        )
    stored = pd.read_csv(rows_path)
    return stored[stored["arm"] == "two_stage_lever"].copy()


# ---------------------------------------------------------------------------
# estimator dispatch (forced route, arbitrary basis dict)
# ---------------------------------------------------------------------------


def _estimator_fit(
    estimator: str,
    calibration: dict[str, np.ndarray],
    selection: dict[str, np.ndarray],
    basis: dict[str, np.ndarray],
    *,
    model: str,
    hazard_ridge: float,
    iterations: int,
) -> tuple[np.ndarray, tuple[str, ...], int]:
    """Returns (coefficient, names, lstsq_fallbacks) for one forced fit.

    v2ridge follows the V2 estimator's own path (_fit_hazard_candidate,
    penalty = ridge * n * I intercept-exempt) -- bit-identical to the Leg 4
    floor rows. lam1n / unpen follow Leg 8's flexible-penalty path
    (_lever_fit with penalty_mode 'const' / 'zero') -- bit-identical to the
    Leg 8 lever rows at the oracle basis.
    """
    if estimator == "v2ridge":
        coefficient, names = _fit_hazard_candidate(
            [
                (calibration, basis["calibration"]),
                (selection, basis["selection"]),
            ],
            model=model,
            ridge=hazard_ridge,
            iterations=iterations,
        )
        return coefficient, names, 0
    coefficient, names, family, fallbacks = leg8._lever_fit(
        calibration,
        selection,
        basis,
        model=model,
        arm=LEVER_ARM_OF[estimator],
        hazard_ridge=hazard_ridge,
        iterations=iterations,
    )
    if family != "base":
        raise RuntimeError(
            f"estimator {estimator} resolved to family {family}; only the "
            "base hazard family is registered for Leg 9"
        )
    return coefficient, names, fallbacks


# ---------------------------------------------------------------------------
# 4x realization panels -- frozen law at the enlarged event budget
# ---------------------------------------------------------------------------


def _assert_4x_bridge(
    context: dict[str, Any],
    observed_4x: Any,
    truth_4x: Any,
    spec_4x: M4ChartEcologySpec,
    oracle_basis: dict[str, np.ndarray],
    parameters: dict[str, np.ndarray],
) -> dict[str, Any]:
    """Frozen-law + offset-mechanism gates at the 4x budget.

    (i) the 4x generator draw must keep the law bit-identical (oracle basis
    all roles + all 8 author-parameter arrays); (ii) the offset-0
    _path_panel reassembly at spec_4x must reproduce the full generator's
    4x calibration/selection panels VALUE-EXACTLY on all 8 panel fields
    (both views) -- the bridge that licenses offset realizations r >= 1
    at the 4x budget.
    """
    truth = context["truth"]
    for role in ("calibration", "selection", "evaluation"):
        if not np.array_equal(
            truth_4x.oracle_basis[role], truth.oracle_basis[role]
        ):
            raise RuntimeError(
                "frozen-world violation at 4x: oracle basis "
                f"[{role}] changed on {context['world']} rep "
                f"{context['repetition']}"
            )
    for name in leg7.LAW_PARAMETER_KEYS:
        if not np.array_equal(
            truth_4x.author_parameters[name], truth.author_parameters[name]
        ):
            raise RuntimeError(
                "frozen-world violation at 4x: author parameter "
                f"{name} changed on {context['world']} rep "
                f"{context['repetition']}"
            )
    panels0 = leg7._realization_cal_sel(
        context["world"],
        spec_4x,
        context["seed"],
        0,
        oracle_basis,
        parameters,
    )
    mismatches = []
    for view in ("train", "test"):
        for role in ("calibration", "selection"):
            battery = getattr(observed_4x.ecology, f"{view}_{role}")
            rebuilt = panels0[(view, role)]
            for field in leg7.PANEL_FIELDS:
                if not np.array_equal(
                    getattr(battery, field), getattr(rebuilt, field)
                ):
                    mismatches.append(f"{view}_{role}.{field}")
    if mismatches:
        raise RuntimeError(
            "4x offset-0 bridge gate FAILED on "
            f"{context['world']} rep {context['repetition']}: "
            f"mismatched fields: {mismatches}"
        )
    return {
        "world": context["world"],
        "repetition": context["repetition"],
        "fields_checked": len(leg7.PANEL_FIELDS) * 4,
        "identity_holds": True,
    }


# ---------------------------------------------------------------------------
# Arm A -- per-cell bias-variance decomposition over R = 8 fresh panels
# ---------------------------------------------------------------------------


def _paired_decomposition(
    disc: np.ndarray,
    orc: np.ndarray,
    tag: str,
) -> dict[str, float]:
    """Exact bias^2 + variance split of the paired error over panels.

    disc, orc: stacked per-panel estimates, shape (R, categories, dims).
    Normalization: the squared norm of the panel-averaged oracle-side
    estimate (one fixed reference scale per cell, so the identity
    total = bias^2 + var holds exactly).
    """
    delta = disc - orc
    delta_bar = delta.mean(axis=0)
    orc_bar = orc.mean(axis=0)
    disc_bar = disc.mean(axis=0)
    scale = max(float(np.linalg.norm(orc_bar)), leg3.EPS)
    bias_rel = float(np.linalg.norm(delta_bar)) / scale
    var_rel = float(
        np.mean([np.sum((d - delta_bar) ** 2) for d in delta])
    ) / scale**2
    total_rel = float(np.mean([np.sum(d**2) for d in delta])) / scale**2
    identity_gap = abs(total_rel - (bias_rel**2 + var_rel))
    if identity_gap > 1e-9 * max(1.0, total_rel):
        raise RuntimeError(
            f"bias-variance identity violated ({tag}): "
            f"total {total_rel:.12e} vs bias^2+var "
            f"{bias_rel**2 + var_rel:.12e}"
        )
    mean_paired = float(
        np.mean(
            [
                np.linalg.norm(d)
                / max(float(np.linalg.norm(o)), leg3.EPS)
                for d, o in zip(delta, orc, strict=True)
            ]
        )
    )
    return {
        "bias_rel": bias_rel,
        "var_rel": var_rel,
        "total_rel": total_rel,
        "bias_share": (
            bias_rel**2 / total_rel if total_rel > 0 else float("nan")
        ),
        "mean_paired_per_panel": mean_paired,
        "disc_var_rel": float(
            np.mean([np.sum((d - disc_bar) ** 2) for d in disc])
        )
        / scale**2,
        "orc_var_rel": float(
            np.mean([np.sum((o - orc_bar) ** 2) for o in orc])
        )
        / scale**2,
    }


def _floor_pass_for_world_rep(
    context: dict[str, Any],
    *,
    spec: M4ChartEcologySpec,
    stored_leg4_1x: pd.DataFrame,
    stored_leg4_4x: pd.DataFrame,
    stored_leg8_levers: pd.DataFrame,
) -> dict[str, Any]:
    """R=8 x {1x,4x} x {v2ridge,lam1n,unpen} paired fits + decomposition.

    Returns cells, per-panel rows, faithfulness checks, the lam1n oracle
    reference store (D + creation action at r=0 per budget) for the battery
    secondary column, and the r=0 4x event cache for the battery pass.
    """
    world = context["world"]
    repetition = context["repetition"]
    seed = context["seed"]
    truth = context["truth"]
    v2_basis = context["v2_basis"]
    oracle_basis_native = truth.oracle_basis
    hazard_ridge = context["fit_kwargs"]["hazard_ridge"]
    iterations = context["fit_kwargs"]["logistic_iterations"]
    dimensions = context["flat"][("train", 0)][0]["response_next"].shape[1]

    unit_gap = leg4._true_derivative_unit_check(truth, dimensions)
    if unit_gap > 1e-10:
        raise RuntimeError(
            f"analytic D_true fails the probe unit check on {world} rep "
            f"{repetition}: max abs gap {unit_gap:.3e}"
        )
    true_d = {
        author: leg4._true_derivative(truth, author)
        for author in range(context["authors"])
    }

    # ---- law rebuild + realization-0 (1x) identity gates (Leg 7) ----
    oracle_basis, parameters = leg7._rebuild_law(world, spec, seed)
    leg7._assert_law_identity(context, oracle_basis, parameters)
    panels0 = leg7._realization_cal_sel(
        world, spec, seed, 0, oracle_basis, parameters
    )
    gate_1x = leg7._assert_realization0_panels(context, panels0)
    del panels0

    row_index = [
        (view, author)
        for view in ("train", "test")
        for author in range(context["authors"])
    ]
    forced_routes: dict[tuple[str, int], str] = {}
    degenerate: dict[tuple[str, int], bool] = {}
    for view, author in row_index:
        stack = context["oracle_stacks"][view][author]
        forced_routes[(view, author)] = stack["selected_model"]
        degenerate[(view, author)] = bool(
            float(np.linalg.norm(stack["D"])) < leg4.FLIP_TOLERANCE
        )
        if degenerate[(view, author)] and stack["selected_model"] not in (
            "base",
            "return",
        ):
            raise RuntimeError(
                "degenerate oracle reference with a feedback-carrying "
                f"route on {world} rep {repetition} {view} author "
                f"{author}: {stack['selected_model']}"
            )

    # ---- 4x canonical panels + frozen-law/offset bridge gates ----
    spec_4x = replace(spec, events=int(round(spec.events * 4.0)))
    observed_4x, truth_4x = generate_m4_chart_ecology_world(
        world=world, spec=spec_4x, seed=seed
    )
    gate_4x = _assert_4x_bridge(
        context, observed_4x, truth_4x, spec_4x, oracle_basis, parameters
    )

    events_4x_r0: dict[tuple[str, int], tuple[dict, dict]] = {}
    for view in ("train", "test"):
        calibration_panel = getattr(observed_4x.ecology, f"{view}_calibration")
        selection_panel = getattr(observed_4x.ecology, f"{view}_selection")
        for author in range(context["authors"]):
            events_4x_r0[(view, author)] = (
                _flatten_events(calibration_panel, author),
                _flatten_events(selection_panel, author),
            )
    p_env_4x = float(
        np.mean(
            [
                getattr(observed_4x.ecology, f"{view}_{role}").menu.mean()
                for view in ("train", "test")
                for role in ("calibration", "selection")
            ]
        )
    )
    del observed_4x, truth_4x

    p_env_1x = float(
        np.mean(
            [
                getattr(
                    context["observed"].ecology, f"{view}_{role}"
                ).menu.mean()
                for view in ("train", "test")
                for role in ("calibration", "selection")
            ]
        )
    )

    # ---- per-panel fits: d_store[(estimator, budget, side)][(v,a)][r] ----
    d_store: dict[
        tuple[str, float, str], dict[tuple[str, int], list[np.ndarray]]
    ] = {
        (estimator, budget, side): {
            key: [] for key in row_index if not degenerate[key]
        }
        for estimator in ESTIMATORS
        for budget in BUDGETS
        for side in ("disc", "orc")
    }
    lam1n_ref_store: dict[
        tuple[float, str, int], tuple[np.ndarray, np.ndarray]
    ] = {}
    fallback_total = 0
    for budget in BUDGETS:
        spec_b = spec if budget == 1.0 else spec_4x
        for realization in range(N_PANELS):
            if budget == 1.0 and realization == 0:
                events = {
                    key: context["flat"][key][:2] for key in row_index
                }
            elif budget == 4.0 and realization == 0:
                events = events_4x_r0
            else:
                panels = leg7._realization_cal_sel(
                    world, spec_b, seed, realization, oracle_basis, parameters
                )
                events = {}
                for view in ("train", "test"):
                    calibration_panel = panels[(view, "calibration")]
                    selection_panel = panels[(view, "selection")]
                    for author in range(context["authors"]):
                        events[(view, author)] = (
                            _flatten_events(calibration_panel, author),
                            _flatten_events(selection_panel, author),
                        )
                del panels
            for view, author in row_index:
                if degenerate[(view, author)]:
                    continue
                calibration, selection = events[(view, author)]
                route = forced_routes[(view, author)]
                for estimator in ESTIMATORS:
                    for side, basis in (
                        ("disc", v2_basis),
                        ("orc", oracle_basis_native),
                    ):
                        coefficient, names, fallbacks = _estimator_fit(
                            estimator,
                            calibration,
                            selection,
                            basis,
                            model=route,
                            hazard_ridge=hazard_ridge,
                            iterations=iterations,
                        )
                        fallback_total += fallbacks
                        derivative = _feedback_derivative(
                            coefficient,
                            names,
                            basis["evaluation"],
                            dimensions,
                        )
                        if not np.all(np.isfinite(derivative)):
                            raise RuntimeError(
                                f"non-finite derivative ({estimator}/{side}"
                                f"/{budget}x/r{realization}) on {world} rep "
                                f"{repetition} {view} author {author}"
                            )
                        d_store[(estimator, budget, side)][
                            (view, author)
                        ].append(derivative)
                        if (
                            estimator == "lam1n"
                            and side == "orc"
                            and realization == 0
                        ):
                            lam1n_ref_store[(budget, view, author)] = (
                                derivative,
                                _creation_action(
                                    coefficient,
                                    names,
                                    basis["evaluation"],
                                    dimensions,
                                ),
                            )
            del events

    # ---- faithfulness: r=0 v2ridge rows vs Leg 4 persisted {1x, 4x} ----
    def _v2_r0_rows(budget: float) -> list[dict[str, Any]]:
        rows = []
        events_b = int(round(spec.events * budget))
        for view, author in row_index:
            oracle_stack = context["oracle_stacks"][view][author]
            d_orc_1x = oracle_stack["D"]
            keys = {
                "world": world,
                "repetition": repetition,
                "seed": seed,
                "author": author,
                "view": view,
                "budget": budget,
                "events": events_b,
                "forced_route": forced_routes[(view, author)],
            }
            if degenerate[(view, author)]:
                rows.append(
                    {
                        **keys,
                        "degenerate_reference": True,
                        "e_d_paired": np.nan,
                        "e_d_frozen": np.nan,
                        "e_d_true": np.nan,
                        "e_orc_true": np.nan,
                        "orc_self_drift": np.nan,
                        "reference_gap": np.nan,
                        "d_norm_disc_b": np.nan,
                        "d_norm_orc_b": np.nan,
                        "d_norm_orc_1x": float(np.linalg.norm(d_orc_1x)),
                        "d_norm_true": float(
                            np.linalg.norm(true_d[author])
                        ),
                    }
                )
                continue
            d_disc = d_store[("v2ridge", budget, "disc")][(view, author)][0]
            d_orc = d_store[("v2ridge", budget, "orc")][(view, author)][0]
            d_true = true_d[author]
            rows.append(
                {
                    **keys,
                    "degenerate_reference": False,
                    "e_d_paired": leg3._relative_error(d_disc, d_orc),
                    "e_d_frozen": leg3._relative_error(d_disc, d_orc_1x),
                    "e_d_true": leg3._relative_error(d_disc, d_true),
                    "e_orc_true": leg3._relative_error(d_orc, d_true),
                    "orc_self_drift": leg3._relative_error(d_orc, d_orc_1x),
                    "reference_gap": leg3._relative_error(d_orc_1x, d_true),
                    "d_norm_disc_b": float(np.linalg.norm(d_disc)),
                    "d_norm_orc_b": float(np.linalg.norm(d_orc)),
                    "d_norm_orc_1x": float(np.linalg.norm(d_orc_1x)),
                    "d_norm_true": float(np.linalg.norm(d_true)),
                }
            )
        return rows

    check_1x = leg6._assert_passive_rows(
        _v2_r0_rows(1.0), stored_leg4_1x, world, repetition
    )
    check_4x = leg6._assert_passive_rows(
        _v2_r0_rows(4.0), stored_leg4_4x, world, repetition
    )

    # ---- faithfulness: r=0 lam1n/unpen ORACLE-side vs Leg 8 lever rows ----
    lever_rows_mine = []
    for estimator in ("lam1n", "unpen"):
        for budget in BUDGETS:
            for view, author in row_index:
                if degenerate[(view, author)]:
                    lever_rows_mine.append(
                        {
                            "world": world,
                            "repetition": repetition,
                            "arm": LEVER_ARM_OF[estimator],
                            "budget": budget,
                            "author": author,
                            "view": view,
                            "degenerate_reference": True,
                            "e_orc_true": np.nan,
                        }
                    )
                    continue
                d_orc = d_store[(estimator, budget, "orc")][
                    (view, author)
                ][0]
                lever_rows_mine.append(
                    {
                        "world": world,
                        "repetition": repetition,
                        "arm": LEVER_ARM_OF[estimator],
                        "budget": budget,
                        "author": author,
                        "view": view,
                        "degenerate_reference": False,
                        "e_orc_true": leg3._relative_error(
                            d_orc, true_d[author]
                        ),
                    }
                )
    mine = pd.DataFrame(lever_rows_mine)
    reference = stored_leg8_levers[
        (stored_leg8_levers["world"] == world)
        & (stored_leg8_levers["repetition"] == repetition)
    ]
    keys = ["world", "repetition", "arm", "budget", "author", "view"]
    merged = reference.merge(mine, on=keys, suffixes=("_leg8", "_leg9"))
    if len(merged) != len(mine) or len(merged) != len(reference):
        raise RuntimeError(
            f"lever r=0 rows misaligned with Leg 8 on {world} rep "
            f"{repetition}: {len(merged)} matches vs mine {len(mine)} / "
            f"stored {len(reference)}"
        )
    flags_equal = bool(
        (
            merged["degenerate_reference_leg8"]
            == merged["degenerate_reference_leg9"]
        ).all()
    )
    usable = merged[~merged["degenerate_reference_leg8"]]
    lever_max = float(
        np.max(np.abs(usable["e_orc_true_leg8"] - usable["e_orc_true_leg9"]))
    )
    if lever_max > ROW_TOLERANCE or not flags_equal:
        raise RuntimeError(
            f"lever r=0 replay diverges from Leg 8 persisted rows on "
            f"{world} rep {repetition}: max|diff|={lever_max:.3e} "
            f"flags_equal={flags_equal}"
        )
    lever_check = {
        "world": world,
        "repetition": repetition,
        "rows_compared": int(len(merged)),
        "flags_equal": flags_equal,
        "max_abs_e_orc_true_difference": lever_max,
    }

    # ---- v2ridge oracle r=0 1x identity vs the context oracle stacks ----
    orc_identity_gap = 0.0
    for view, author in row_index:
        if degenerate[(view, author)]:
            continue
        orc_identity_gap = max(
            orc_identity_gap,
            float(
                np.max(
                    np.abs(
                        d_store[("v2ridge", 1.0, "orc")][(view, author)][0]
                        - context["oracle_stacks"][view][author]["D"]
                    )
                )
            ),
        )
    if orc_identity_gap > IDENTITY_TOLERANCE:
        raise RuntimeError(
            f"v2ridge oracle r=0 identity gate failed on {world} rep "
            f"{repetition}: {orc_identity_gap:.3e}"
        )

    # ---- cells: primary decomposition + lam1n-referenced secondary ----
    cells: list[dict[str, Any]] = []
    panel_rows: list[dict[str, Any]] = []
    for estimator in ESTIMATORS:
        for budget in BUDGETS:
            for view, author in row_index:
                keys = {
                    "world": world,
                    "repetition": repetition,
                    "seed": seed,
                    "author": author,
                    "view": view,
                    "estimator": estimator,
                    "budget": budget,
                    "forced_route": forced_routes[(view, author)],
                }
                if degenerate[(view, author)]:
                    cells.append(
                        {
                            **keys,
                            "degenerate_reference": True,
                            **{
                                name: np.nan
                                for name in (
                                    "bias_rel",
                                    "var_rel",
                                    "total_rel",
                                    "bias_share",
                                    "mean_paired_per_panel",
                                    "disc_var_rel",
                                    "orc_var_rel",
                                    "e_orc_true_r0",
                                    "e_orc_true_ravg",
                                    "e_d_true_r0",
                                    "bias_rel_lam1nref",
                                    "var_rel_lam1nref",
                                    "total_rel_lam1nref",
                                    "bias_share_lam1nref",
                                )
                            },
                        }
                    )
                    continue
                disc = np.stack(
                    d_store[(estimator, budget, "disc")][(view, author)]
                )
                orc = np.stack(
                    d_store[(estimator, budget, "orc")][(view, author)]
                )
                orc_lam1n = np.stack(
                    d_store[("lam1n", budget, "orc")][(view, author)]
                )
                primary = _paired_decomposition(
                    disc, orc, f"{world}/r{repetition}/{estimator}/{budget}"
                )
                secondary = _paired_decomposition(
                    disc,
                    orc_lam1n,
                    f"{world}/r{repetition}/{estimator}/{budget}/lam1nref",
                )
                cells.append(
                    {
                        **keys,
                        "degenerate_reference": False,
                        **primary,
                        "e_orc_true_r0": leg3._relative_error(
                            orc[0], true_d[author]
                        ),
                        "e_orc_true_ravg": leg3._relative_error(
                            orc.mean(axis=0), true_d[author]
                        ),
                        "e_d_true_r0": leg3._relative_error(
                            disc[0], true_d[author]
                        ),
                        "bias_rel_lam1nref": secondary["bias_rel"],
                        "var_rel_lam1nref": secondary["var_rel"],
                        "total_rel_lam1nref": secondary["total_rel"],
                        "bias_share_lam1nref": secondary["bias_share"],
                    }
                )
                for realization in range(N_PANELS):
                    panel_rows.append(
                        {
                            **keys,
                            "realization": realization,
                            "degenerate_reference": False,
                            "e_d_paired": leg3._relative_error(
                                disc[realization], orc[realization]
                            ),
                            "e_d_paired_lam1nref": leg3._relative_error(
                                disc[realization], orc_lam1n[realization]
                            ),
                            "e_d_true": leg3._relative_error(
                                disc[realization], true_d[author]
                            ),
                            "e_orc_true": leg3._relative_error(
                                orc[realization], true_d[author]
                            ),
                            "d_norm_disc": float(
                                np.linalg.norm(disc[realization])
                            ),
                            "d_norm_orc": float(
                                np.linalg.norm(orc[realization])
                            ),
                        }
                    )

    # ---- Arm B: gap content-swap (high-gap worlds only, 1x r=0) ----
    swap_rows: list[dict[str, Any]] = []
    if world in HIGH_GAP_WORLDS:
        swap_i_basis = _row_norm_swap(oracle_basis_native, v2_basis)
        swap_ii_basis = _row_norm_swap(v2_basis, oracle_basis_native)
        for view, author in row_index:
            keys = {
                "world": world,
                "repetition": repetition,
                "seed": seed,
                "author": author,
                "view": view,
                "forced_route": forced_routes[(view, author)],
            }
            if degenerate[(view, author)]:
                swap_rows.append(
                    {
                        **keys,
                        "degenerate_reference": True,
                        "e_d_true_v2": np.nan,
                        "e_orc_true": np.nan,
                        "e_i_true": np.nan,
                        "e_ii_true": np.nan,
                        "gap_v2": np.nan,
                        "gap_i": np.nan,
                        "gap_ii": np.nan,
                    }
                )
                continue
            calibration, selection, _ = context["flat"][(view, author)]
            route = forced_routes[(view, author)]
            d_true = true_d[author]
            d_i = leg4._forced_route_derivative(
                calibration,
                selection,
                swap_i_basis,
                model=route,
                hazard_ridge=hazard_ridge,
                logistic_iterations=iterations,
                dimensions=dimensions,
            )
            d_ii = leg4._forced_route_derivative(
                calibration,
                selection,
                swap_ii_basis,
                model=route,
                hazard_ridge=hazard_ridge,
                logistic_iterations=iterations,
                dimensions=dimensions,
            )
            e_d_true_v2 = leg3._relative_error(
                d_store[("v2ridge", 1.0, "disc")][(view, author)][0], d_true
            )
            e_orc_true = leg3._relative_error(
                d_store[("v2ridge", 1.0, "orc")][(view, author)][0], d_true
            )
            e_i = leg3._relative_error(d_i, d_true)
            e_ii = leg3._relative_error(d_ii, d_true)
            swap_rows.append(
                {
                    **keys,
                    "degenerate_reference": False,
                    "e_d_true_v2": e_d_true_v2,
                    "e_orc_true": e_orc_true,
                    "e_i_true": e_i,
                    "e_ii_true": e_ii,
                    "gap_v2": e_d_true_v2 - e_orc_true,
                    "gap_i": e_i - e_orc_true,
                    "gap_ii": e_ii - e_orc_true,
                }
            )

    # ---- Arm C: partition envelope-corrected reference (1x r=0 + 4x) ----
    partition_rows: list[dict[str, Any]] = []
    if world == PARTITION_WORLD:
        for estimator in ESTIMATORS:
            for view, author in row_index:
                keys = {
                    "world": world,
                    "repetition": repetition,
                    "seed": seed,
                    "author": author,
                    "view": view,
                    "estimator": estimator,
                    "forced_route": forced_routes[(view, author)],
                    "p_env_measured_1x": p_env_1x,
                    "p_env_measured_4x": p_env_4x,
                    "p_env_stationary": ENV_STATIONARY,
                }
                if degenerate[(view, author)]:
                    partition_rows.append(
                        {
                            **keys,
                            "degenerate_reference": True,
                            **{
                                name: np.nan
                                for name in (
                                    "e_orc_true_latent_1x",
                                    "e_orc_true_env_1x",
                                    "e_orc_true_env62_1x",
                                    "e_orc_true_latent_4x",
                                    "e_orc_true_env_4x",
                                    "scale_lsq_1x",
                                    "reference_gap_latent",
                                    "reference_gap_env",
                                )
                            },
                        }
                    )
                    continue
                d_true = true_d[author]
                true_norm_sq = float(np.sum(d_true**2))
                d_1x = d_store[(estimator, 1.0, "orc")][(view, author)][0]
                d_4x = d_store[(estimator, 4.0, "orc")][(view, author)][0]
                d_ref_1x = context["oracle_stacks"][view][author]["D"]
                partition_rows.append(
                    {
                        **keys,
                        "degenerate_reference": False,
                        "e_orc_true_latent_1x": leg3._relative_error(
                            d_1x, d_true
                        ),
                        "e_orc_true_env_1x": leg3._relative_error(
                            d_1x, p_env_1x * d_true
                        ),
                        "e_orc_true_env62_1x": leg3._relative_error(
                            d_1x, ENV_STATIONARY * d_true
                        ),
                        "e_orc_true_latent_4x": leg3._relative_error(
                            d_4x, d_true
                        ),
                        "e_orc_true_env_4x": leg3._relative_error(
                            d_4x, p_env_4x * d_true
                        ),
                        "scale_lsq_1x": float(
                            np.sum(d_1x * d_true) / max(true_norm_sq, 1e-300)
                        ),
                        "reference_gap_latent": leg3._relative_error(
                            d_ref_1x, d_true
                        ),
                        "reference_gap_env": leg3._relative_error(
                            d_ref_1x, p_env_1x * d_true
                        ),
                    }
                )

    gates = {
        "world": world,
        "repetition": repetition,
        "true_d_unit_check_max_gap": unit_gap,
        "orc_v2_r0_identity_max_gap_1x": orc_identity_gap,
        "lstsq_fallbacks_total": int(fallback_total),
        "p_env_measured_1x": p_env_1x,
        "p_env_measured_4x": p_env_4x,
        "realization0_gate_1x": gate_1x["identity_holds"],
        "bridge_gate_4x": gate_4x["identity_holds"],
    }
    return {
        "cells": cells,
        "panel_rows": panel_rows,
        "swap_rows": swap_rows,
        "partition_rows": partition_rows,
        "check_1x": check_1x,
        "check_4x": check_4x,
        "lever_check": lever_check,
        "gates": gates,
        "lam1n_ref_store": lam1n_ref_store,
        "events_4x_r0": events_4x_r0,
        "degenerate": degenerate,
    }


def _row_norm_swap(
    direction_basis: dict[str, np.ndarray],
    norm_basis: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Basis with direction_basis's row directions + norm_basis's row norms."""
    output = {}
    for role in ("calibration", "selection", "evaluation"):
        directions = direction_basis[role]
        s_dir = np.linalg.norm(directions, axis=1)
        s_norm = np.linalg.norm(norm_basis[role], axis=1)
        scale = np.where(
            s_dir > 1e-12, s_norm / np.maximum(s_dir, 1e-12), 1.0
        )
        output[role] = directions * scale[:, None]
    return output


# ---------------------------------------------------------------------------
# battery pass -- two-stage with each estimator as the stage-2 refit
# ---------------------------------------------------------------------------


def _loop_geometry_only(
    stacks: dict[str, list[dict[str, Any]]],
    reference: dict[str, list[dict[str, Any]]],
) -> float:
    disc = 0.5 * (
        np.stack([fit["loop"] for fit in stacks["train"]])
        + np.stack([fit["loop"] for fit in stacks["test"]])
    )
    orac = 0.5 * (
        np.stack([fit["loop"] for fit in reference["train"]])
        + np.stack([fit["loop"] for fit in reference["test"]])
    )
    return leg3._geometry(
        disc.reshape(len(disc), -1), orac.reshape(len(orac), -1)
    )


def _battery_pass_for_world_rep(
    context: dict[str, Any],
    *,
    leg4_arm2: pd.DataFrame,
    leg5_rows: pd.DataFrame,
    leg8_stack_rows: pd.DataFrame,
    events_4x_r0: dict[tuple[str, int], tuple[dict, dict]],
    lam1n_ref_store: dict[
        tuple[float, str, int], tuple[np.ndarray, np.ndarray]
    ],
    degenerate: dict[tuple[str, int], bool],
) -> dict[str, Any]:
    world = context["world"]
    repetition = context["repetition"]
    keys_base = {
        "world": world,
        "repetition": repetition,
        "seed": context["seed"],
    }
    v2_basis = context["v2_basis"]
    hazard_ridge = context["fit_kwargs"]["hazard_ridge"]
    iterations = context["fit_kwargs"]["logistic_iterations"]
    dimensions = context["flat"][("train", 0)][0]["response_next"].shape[1]

    # ---- stage 1 (Leg 4a arm exactly) + registered assert ----
    stage1_stacks = leg4._arm2_stacks_for_lambda(context, STAGE1_LAMBDA)
    stage1_rows = [
        leg3._loop_row(
            {**keys_base, "author": author, "view": view},
            "arm2_stage1_125",
            stage1_stacks[view][author],
            context["oracle_stacks"][view][author],
        )
        for view in ("train", "test")
        for author in range(context["authors"])
    ]
    stage1_check = leg7._assert_rows_scaled(
        stage1_rows, leg4_arm2, world, repetition, label="stage-1"
    )

    # ---- two_stage (Leg 5 exactly; the v2ridge @ 1x cell) + assert ----
    two_stage_stacks: dict[str, list[dict[str, Any]]] = {
        "train": [],
        "test": [],
    }
    for view in ("train", "test"):
        for author in range(context["authors"]):
            stack, _ = leg5._two_stage_stack(
                context, view, author, stage1_stacks[view][author]
            )
            two_stage_stacks[view].append(stack)
    two_stage_rows = [
        leg3._loop_row(
            {**keys_base, "author": author, "view": view},
            "two_stage",
            two_stage_stacks[view][author],
            context["oracle_stacks"][view][author],
        )
        for view in ("train", "test")
        for author in range(context["authors"])
    ]
    two_stage_check = leg7._assert_rows_scaled(
        two_stage_rows, leg5_rows, world, repetition, label="two_stage"
    )

    # ---- fresh cells: estimator x budget stage-2 refits ----
    cell_stacks: dict[str, dict[str, list[dict[str, Any]]]] = {
        "two_stage": two_stage_stacks
    }
    fallback_total = 0
    for arm, (estimator, budget) in BATTERY_CELLS.items():
        if arm == "two_stage":
            continue
        stacks: dict[str, list[dict[str, Any]]] = {"train": [], "test": []}
        for view in ("train", "test"):
            for author in range(context["authors"]):
                base = context["base_stacks"][view][author]
                stage2 = two_stage_stacks[view][author]
                route = stage2["selected_model"]
                if budget == 1.0:
                    calibration, selection, _ = context["flat"][
                        (view, author)
                    ]
                else:
                    calibration, selection = events_4x_r0[(view, author)]
                coefficient, names, fallbacks = _estimator_fit(
                    estimator,
                    calibration,
                    selection,
                    v2_basis,
                    model=route,
                    hazard_ridge=hazard_ridge,
                    iterations=iterations,
                )
                fallback_total += fallbacks
                derivative = _feedback_derivative(
                    coefficient, names, v2_basis["evaluation"], dimensions
                )
                action = _creation_action(
                    coefficient, names, v2_basis["evaluation"], dimensions
                )
                stacks[view].append(
                    {
                        "C": base["C"],
                        "G": base["G"],
                        "D": derivative,
                        "loop": derivative @ base["G"] @ base["C"],
                        "choice_action": base["choice_action"],
                        "creation_action": action,
                        "selected_model": route,
                    }
                )
        cell_stacks[arm] = stacks

    # ---- ts_lam1n_1x must reproduce Leg 8's two_stage_lever bit-tight ----
    lam1n_1x_rows = [
        leg3._loop_row(
            {**keys_base, "author": author, "view": view},
            "two_stage_lever",
            cell_stacks["ts_lam1n_1x"][view][author],
            context["oracle_stacks"][view][author],
        )
        for view in ("train", "test")
        for author in range(context["authors"])
    ]
    lam1n_1x_check = leg7._assert_rows_scaled(
        lam1n_1x_rows,
        leg8_stack_rows,
        world,
        repetition,
        label="ts_lam1n_1x",
    )

    # ---- primary rows + world-rep geometries ----
    arm_stacks_all = {"arm2_stage1_125": stage1_stacks, **cell_stacks}
    loop_rows: list[dict[str, Any]] = []
    world_rows: list[dict[str, Any]] = []
    for arm in BATTERY_ARMS:
        stacks = arm_stacks_all[arm]
        if arm == "arm2_stage1_125":
            arm_rows = stage1_rows
        elif arm == "two_stage":
            arm_rows = two_stage_rows
        else:
            arm_rows = [
                leg3._loop_row(
                    {**keys_base, "author": author, "view": view},
                    arm,
                    stacks[view][author],
                    context["oracle_stacks"][view][author],
                )
                for view in ("train", "test")
                for author in range(context["authors"])
            ]
        loop_rows.extend(arm_rows)
        geometries = leg3._arm_geometries(stacks, context["oracle_stacks"])
        estimator, budget = BATTERY_CELLS.get(arm, ("v2ridge", 1.0))
        world_rows.append(
            {
                **keys_base,
                "arm": arm,
                "chart_family": context["chart"].selected_family,
                "stage2_estimator": (
                    estimator if arm in BATTERY_CELLS else "v2_semantics"
                ),
                "stage2_budget": (
                    budget if arm in BATTERY_CELLS else 1.0
                ),
                **geometries,
                "flips": int(sum(row["model_flip"] for row in arm_rows)),
                "route_mismatches": int(
                    sum(row["route_mismatch"] for row in arm_rows)
                ),
                "mean_e_loop": float(
                    np.mean([row["e_loop"] for row in arm_rows])
                ),
                "mean_e_d": float(
                    np.mean([row["e_d_atom"] for row in arm_rows])
                ),
            }
        )

    # ---- UNREGISTERED-SECONDARY: lam1n-referenced loop endpoints ----
    # Reference stacks replace the V2-fitted oracle D with the lam1n-fitted
    # oracle D at the arm's stage-2 budget (r=0), loop = D @ G_orc @ C_orc.
    # Degenerate rows (base/return routes) have D identically zero under
    # every estimator, so their endpoints coincide with the primary ones.
    secondary_refs: dict[float, dict[str, list[dict[str, Any]]]] = {}
    for budget in BUDGETS:
        reference: dict[str, list[dict[str, Any]]] = {
            "train": [],
            "test": [],
        }
        for view in ("train", "test"):
            for author in range(context["authors"]):
                oracle_stack = context["oracle_stacks"][view][author]
                if degenerate[(view, author)]:
                    d_ref = np.zeros_like(oracle_stack["D"])
                else:
                    d_ref = lam1n_ref_store[(budget, view, author)][0]
                reference[view].append(
                    {
                        **oracle_stack,
                        "D": d_ref,
                        "loop": d_ref
                        @ oracle_stack["G"]
                        @ oracle_stack["C"],
                    }
                )
        secondary_refs[budget] = reference

    secondary_world_rows: list[dict[str, Any]] = []
    secondary_loop_rows: list[dict[str, Any]] = []
    for arm in BATTERY_ARMS:
        stacks = arm_stacks_all[arm]
        _, budget = BATTERY_CELLS.get(arm, ("v2ridge", 1.0))
        reference = secondary_refs[budget]
        geometry = _loop_geometry_only(stacks, reference)
        secondary_world_rows.append(
            {
                **keys_base,
                "arm": arm,
                "reference": "oracle_lam1n_r0",
                "reference_budget": budget,
                "loop_action_geometry_lam1nref": geometry,
            }
        )
        for view in ("train", "test"):
            for author in range(context["authors"]):
                stack = stacks[view][author]
                ref = reference[view][author]
                secondary_loop_rows.append(
                    {
                        **keys_base,
                        "arm": arm,
                        "author": author,
                        "view": view,
                        "reference_budget": budget,
                        "e_loop_lam1nref": leg3._relative_error(
                            stack["loop"], ref["loop"]
                        ),
                        "e_d_lam1nref": leg3._relative_error(
                            stack["D"], ref["D"]
                        ),
                    }
                )
    # reference-shift diagnostic: how far the lam1n reference itself moved
    for budget in BUDGETS:
        secondary_world_rows.append(
            {
                **keys_base,
                "arm": f"reference_shift_{int(budget)}x",
                "reference": "oracle_lam1n_r0_vs_oracle_v2",
                "reference_budget": budget,
                "loop_action_geometry_lam1nref": _loop_geometry_only(
                    secondary_refs[budget], context["oracle_stacks"]
                ),
            }
        )

    structure = {
        **keys_base,
        "stage2_lstsq_fallbacks": int(fallback_total),
    }
    return {
        "loop_rows": loop_rows,
        "world_rows": world_rows,
        "secondary_world_rows": secondary_world_rows,
        "secondary_loop_rows": secondary_loop_rows,
        "stage1_check": stage1_check,
        "two_stage_check": two_stage_check,
        "lam1n_1x_check": lam1n_1x_check,
        "structure": structure,
    }


# ---------------------------------------------------------------------------
# chunk execution
# ---------------------------------------------------------------------------


def _world_tag(worlds: list[str]) -> str:
    if list(worlds) == list(LOOP_WORLDS):
        return ""
    indices = "".join(
        str(list(LOOP_WORLDS).index(world)) for world in worlds
    )
    return f"_w{indices}"


def _run_chunk(
    args: argparse.Namespace,
    config: dict[str, Any],
    spec: M4ChartEcologySpec,
    repetitions: tuple[int, ...],
    worlds: list[str],
) -> None:
    stored_leg4, _ = leg8._load_leg4_reference()
    stored_leg4_1x = stored_leg4[stored_leg4["budget"] == 1.0].copy()
    stored_leg4_4x = stored_leg4[stored_leg4["budget"] == 4.0].copy()
    stored_leg8_levers = _load_leg8_lever_reference()
    leg8_stack_rows = _load_leg8_stack_reference()
    leg4_arm2 = leg5._load_leg4_arm2()
    _, leg5_rows = leg7._load_leg5_reference()
    world_index = {
        world: index for index, world in enumerate(config["worlds"])
    }
    expected_for = leg8._expected_geometries_lookup(config)

    collections: dict[str, list] = {
        name: []
        for name in (
            "cells",
            "panel_rows",
            "swap_rows",
            "partition_rows",
            "battery_loop",
            "battery_world",
            "secondary_world",
            "secondary_loop",
            "check_1x",
            "check_4x",
            "lever_check",
            "stage1_check",
            "two_stage_check",
            "lam1n_1x_check",
            "validation",
        )
    }
    gates: list[dict[str, Any]] = []
    structures: list[dict[str, Any]] = []
    for repetition in repetitions:
        for world in worlds:
            seed = leg3._world_seed(
                int(config["seed"]), repetition, world, world_index[world]
            )
            started = time.time()
            context = leg4._build_context(
                world,
                repetition,
                seed,
                spec=spec,
                config=config,
                expected_geometries=expected_for(world, repetition, seed),
            )
            collections["validation"].extend(context["validation_rows"])

            floor = _floor_pass_for_world_rep(
                context,
                spec=spec,
                stored_leg4_1x=stored_leg4_1x,
                stored_leg4_4x=stored_leg4_4x,
                stored_leg8_levers=stored_leg8_levers,
            )
            collections["cells"].extend(floor["cells"])
            collections["panel_rows"].extend(floor["panel_rows"])
            collections["swap_rows"].extend(floor["swap_rows"])
            collections["partition_rows"].extend(floor["partition_rows"])
            collections["check_1x"].append(floor["check_1x"])
            collections["check_4x"].append(floor["check_4x"])
            collections["lever_check"].append(floor["lever_check"])
            gates.append(floor["gates"])

            battery = _battery_pass_for_world_rep(
                context,
                leg4_arm2=leg4_arm2,
                leg5_rows=leg5_rows,
                leg8_stack_rows=leg8_stack_rows,
                events_4x_r0=floor["events_4x_r0"],
                lam1n_ref_store=floor["lam1n_ref_store"],
                degenerate=floor["degenerate"],
            )
            collections["battery_loop"].extend(battery["loop_rows"])
            collections["battery_world"].extend(battery["world_rows"])
            collections["secondary_world"].extend(
                battery["secondary_world_rows"]
            )
            collections["secondary_loop"].extend(
                battery["secondary_loop_rows"]
            )
            collections["stage1_check"].append(battery["stage1_check"])
            collections["two_stage_check"].append(
                battery["two_stage_check"]
            )
            collections["lam1n_1x_check"].append(battery["lam1n_1x_check"])
            structures.append(battery["structure"])

            by_arm = {
                row["arm"]: round(row["loop_action_geometry"], 3)
                for row in battery["world_rows"]
                if row["arm"] in BATTERY_CELLS
            }
            cell_frame = pd.DataFrame(
                [
                    cell
                    for cell in floor["cells"]
                    if not cell["degenerate_reference"]
                ]
            )
            summary_bits = {}
            for estimator in ESTIMATORS:
                sub = cell_frame[
                    (cell_frame["estimator"] == estimator)
                    & (cell_frame["budget"] == 1.0)
                ]
                summary_bits[estimator] = (
                    round(float(sub["bias_rel"].median()), 3),
                    round(float(sub["var_rel"].median()), 4),
                )
            print(
                f"[leg9] rep={repetition} world={world} battery {by_arm} "
                f"bias/var@1x {summary_bits} "
                f"({time.time() - started:.0f}s)",
                flush=True,
            )

    suffix = (
        f"rep{repetitions[0]}-{repetitions[-1]}{_world_tag(worlds)}"
    )
    args.output.mkdir(parents=True, exist_ok=True)
    stems = {
        "cells": "bv_cells",
        "panel_rows": "bv_panel_rows",
        "swap_rows": "swap_rows",
        "partition_rows": "partition_rows",
        "battery_loop": "battery_loop",
        "battery_world": "battery_world",
        "secondary_world": "secondary_world",
        "secondary_loop": "secondary_loop",
        "check_1x": "check_1x",
        "check_4x": "check_4x",
        "lever_check": "lever_check",
        "stage1_check": "stage1_check",
        "two_stage_check": "two_stage_check",
        "lam1n_1x_check": "lam1n_1x_check",
        "validation": "v2_validation",
    }
    for name, stem in stems.items():
        pd.DataFrame(collections[name]).to_csv(
            args.output / f"partial_{stem}_{suffix}.csv", index=False
        )
    with (args.output / f"partial_gates_{suffix}.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(
            {
                "gates": gates,
                "battery_structure": structures,
                "repetitions": list(repetitions),
                "worlds": worlds,
            },
            handle,
            indent=2,
            sort_keys=True,
        )
        handle.write("\n")
    print(f"[chunk done] {suffix}", flush=True)


# ---------------------------------------------------------------------------
# assembly -- refuse missing/duplicate cells, adjudicate from rows only
# ---------------------------------------------------------------------------


def _concat_partials(output: Path, stem: str) -> pd.DataFrame:
    paths = sorted(glob.glob(str(output / f"partial_{stem}_rep*.csv")))
    if not paths:
        raise RuntimeError(f"no partial CSVs found for {stem} under {output}")
    frames = []
    for path in paths:
        frame = pd.read_csv(path)
        if len(frame):
            frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def _refuse_bad_cells(
    frame: pd.DataFrame,
    keys: list[str],
    expected: int,
    label: str,
) -> None:
    duplicated = int(frame.duplicated(subset=keys).sum())
    if duplicated:
        raise RuntimeError(f"{label}: {duplicated} duplicate cells refused")
    if len(frame) != expected:
        raise RuntimeError(
            f"{label}: {len(frame)} rows != expected {expected}; missing "
            "cells refused"
        )


def _author_level(
    frame: pd.DataFrame,
    metrics: list[str],
    extra_keys: list[str],
) -> pd.DataFrame:
    usable = frame[~frame["degenerate_reference"]].copy()
    return (
        usable.groupby(["world", "repetition", "author", *extra_keys])
        .agg(**{name: (name, "mean") for name in metrics})
        .reset_index()
    )


def _scoped_median_table(
    author_frame: pd.DataFrame,
    metrics: list[str],
    cell_keys: list[str],
) -> list[dict[str, Any]]:
    rows = []
    worlds = sorted(author_frame["world"].unique())
    for scope in [*worlds, "POOLED"]:
        scoped = (
            author_frame
            if scope == "POOLED"
            else author_frame[author_frame["world"] == scope]
        )
        for cell_values, group in scoped.groupby(cell_keys):
            if not isinstance(cell_values, tuple):
                cell_values = (cell_values,)
            row: dict[str, Any] = {
                "world": scope,
                **dict(zip(cell_keys, cell_values, strict=True)),
                "n_author_reps": int(len(group)),
            }
            for name in metrics:
                row[f"median_{name}"] = float(group[name].median())
                row[f"iqr_low_{name}"] = float(group[name].quantile(0.25))
                row[f"iqr_high_{name}"] = float(group[name].quantile(0.75))
            rows.append(row)
    return rows


def _assemble(args: argparse.Namespace, config: dict[str, Any]) -> None:
    stored_leg4, leg4_decision = leg8._load_leg4_reference()
    leg5_two_stage, _ = leg7._load_leg5_reference()
    _ = _load_leg8_lever_reference()
    with (
        ROOT / "results" / "m4_d_bias_anatomy" / "decision.json"
    ).open("r", encoding="utf-8") as handle:
        leg8_decision = json.load(handle)

    repetitions = int(config["repetitions"])
    worlds = list(LOOP_WORLDS)
    n_world_reps = len(worlds) * repetitions
    authors = 16
    n_author_views = n_world_reps * 2 * authors

    cells = _concat_partials(args.output, "bv_cells")
    panel_rows = _concat_partials(args.output, "bv_panel_rows")
    swap_rows = _concat_partials(args.output, "swap_rows")
    partition_rows = _concat_partials(args.output, "partition_rows")
    battery_loop = _concat_partials(args.output, "battery_loop")
    battery_world = _concat_partials(args.output, "battery_world")
    secondary_world = _concat_partials(args.output, "secondary_world")
    secondary_loop = _concat_partials(args.output, "secondary_loop")
    validation = _concat_partials(args.output, "v2_validation")
    checks = {
        name: _concat_partials(args.output, name)
        for name in (
            "check_1x",
            "check_4x",
            "lever_check",
            "stage1_check",
            "two_stage_check",
            "lam1n_1x_check",
        )
    }
    gate_payloads = []
    for path in sorted(glob.glob(str(args.output / "partial_gates_rep*.json"))):
        with open(path, "r", encoding="utf-8") as handle:
            gate_payloads.append(json.load(handle))
    gates = [gate for chunk in gate_payloads for gate in chunk["gates"]]
    structures = [
        row for chunk in gate_payloads for row in chunk["battery_structure"]
    ]

    _refuse_bad_cells(
        cells,
        ["world", "repetition", "author", "view", "estimator", "budget"],
        n_author_views * len(ESTIMATORS) * len(BUDGETS),
        "bias-variance cells",
    )
    usable_cells = cells[~cells["degenerate_reference"]]
    _refuse_bad_cells(
        panel_rows,
        [
            "world",
            "repetition",
            "author",
            "view",
            "estimator",
            "budget",
            "realization",
        ],
        int(len(usable_cells)) * N_PANELS,
        "per-panel rows",
    )
    _refuse_bad_cells(
        swap_rows,
        ["world", "repetition", "author", "view"],
        len(HIGH_GAP_WORLDS) * repetitions * 2 * authors,
        "gap swap rows",
    )
    _refuse_bad_cells(
        partition_rows,
        ["world", "repetition", "author", "view", "estimator"],
        repetitions * 2 * authors * len(ESTIMATORS),
        "partition reference rows",
    )
    _refuse_bad_cells(
        battery_loop,
        ["arm", "world", "repetition", "author", "view"],
        len(BATTERY_ARMS) * n_author_views,
        "battery loop rows",
    )
    _refuse_bad_cells(
        battery_world,
        ["arm", "world", "repetition"],
        len(BATTERY_ARMS) * n_world_reps,
        "battery world-rep rows",
    )
    _refuse_bad_cells(
        secondary_loop,
        ["arm", "world", "repetition", "author", "view"],
        len(BATTERY_ARMS) * n_author_views,
        "secondary loop rows",
    )
    _refuse_bad_cells(
        secondary_world,
        ["arm", "world", "repetition"],
        (len(BATTERY_ARMS) + 2) * n_world_reps,
        "secondary world rows",
    )
    for name, frame in checks.items():
        _refuse_bad_cells(
            frame, ["world", "repetition"], n_world_reps, name
        )
    if len(gates) != n_world_reps:
        raise RuntimeError(
            f"gate payloads cover {len(gates)} world-reps != {n_world_reps}"
        )

    # ---- faithfulness maxima (refuse over-tolerance) ----
    faithfulness: dict[str, Any] = {}
    for name, frame in checks.items():
        if name in ("check_1x", "check_4x", "lever_check"):
            column = (
                "max_abs_difference"
                if "max_abs_difference" in frame.columns
                else "max_abs_e_orc_true_difference"
            )
            worst = float(frame[column].max())
        else:
            worst = float(
                np.maximum(
                    frame["max_scaled_e_loop_difference"],
                    frame["max_scaled_e_d_atom_difference"],
                ).max()
            )
        if worst > ROW_TOLERANCE:
            raise RuntimeError(
                f"assembled {name} reproduction max diff {worst:.3e}"
            )
        faithfulness[name] = {
            "world_reps_checked": int(len(frame)),
            "max_difference": worst,
            "all_flags_equal": bool(frame["flags_equal"].all()),
        }
    stage1_flips = int(
        battery_loop[battery_loop["arm"] == "arm2_stage1_125"][
            "model_flip"
        ].sum()
    )
    if stage1_flips != leg5.STAGE1_EXPECTED_FLIPS:
        raise RuntimeError(
            f"stage-1 battery flips {stage1_flips} != "
            f"{leg5.STAGE1_EXPECTED_FLIPS}"
        )
    faithfulness["stage1_flips_total_equals_73"] = True
    faithfulness["gates"] = {
        "realization0_gate_1x_all_hold": bool(
            all(gate["realization0_gate_1x"] for gate in gates)
        ),
        "bridge_gate_4x_all_hold": bool(
            all(gate["bridge_gate_4x"] for gate in gates)
        ),
        "true_d_unit_check_max_gap": float(
            max(gate["true_d_unit_check_max_gap"] for gate in gates)
        ),
        "orc_v2_r0_identity_max_gap_1x": float(
            max(gate["orc_v2_r0_identity_max_gap_1x"] for gate in gates)
        ),
        "lstsq_fallbacks_total": int(
            sum(gate["lstsq_fallbacks_total"] for gate in gates)
        ),
        "v2_validation_max_abs_difference": (
            float(validation["abs_difference"].max())
            if len(validation)
            else float("nan")
        ),
    }

    # ---- Arm A: bias-variance tables ----
    bv_metrics = [
        "bias_rel",
        "var_rel",
        "total_rel",
        "bias_share",
        "mean_paired_per_panel",
        "disc_var_rel",
        "orc_var_rel",
        "e_orc_true_r0",
        "e_orc_true_ravg",
        "e_d_true_r0",
        "bias_rel_lam1nref",
        "var_rel_lam1nref",
        "total_rel_lam1nref",
        "bias_share_lam1nref",
    ]
    author_cells = _author_level(cells, bv_metrics, ["estimator", "budget"])
    bv_summary = _scoped_median_table(
        author_cells, bv_metrics, ["estimator", "budget"]
    )
    bv_summary_frame = pd.DataFrame(bv_summary)

    def _pooled_median(estimator: str, budget: float, metric: str) -> float:
        match = bv_summary_frame[
            (bv_summary_frame["world"] == "POOLED")
            & (bv_summary_frame["estimator"] == estimator)
            & (bv_summary_frame["budget"] == budget)
        ]
        return float(match[f"median_{metric}"].iloc[0])

    signature: dict[str, Any] = {}
    for estimator in ("lam1n", "unpen"):
        signature[estimator] = {
            "bias_1x": _pooled_median(estimator, 1.0, "bias_rel"),
            "bias_v2_1x": _pooled_median("v2ridge", 1.0, "bias_rel"),
            "var_1x": _pooled_median(estimator, 1.0, "var_rel"),
            "var_v2_1x": _pooled_median("v2ridge", 1.0, "var_rel"),
            "lower_bias": bool(
                _pooled_median(estimator, 1.0, "bias_rel")
                < _pooled_median("v2ridge", 1.0, "bias_rel")
            ),
            "higher_variance": bool(
                _pooled_median(estimator, 1.0, "var_rel")
                > _pooled_median("v2ridge", 1.0, "var_rel")
            ),
        }
        signature[estimator]["holds"] = bool(
            signature[estimator]["lower_bias"]
            and signature[estimator]["higher_variance"]
        )
    signature_hold = bool(
        signature["lam1n"]["holds"] and signature["unpen"]["holds"]
    )

    # ---- Arm A: ranking table (the decisive numbers) ----
    arm_summaries = {
        arm: leg4._arm_summary(battery_loop, battery_world, arm)
        for arm in BATTERY_ARMS
    }
    ranking = {
        arm: {
            "estimator": BATTERY_CELLS[arm][0],
            "stage2_budget": BATTERY_CELLS[arm][1],
            "pooled_loop_geometry": float(
                arm_summaries[arm]["pooled_loop_geometry"]
            ),
            "pooled_creation_geometry": float(
                arm_summaries[arm]["pooled_creation_geometry"]
            ),
            "per_world_loop_geometry": arm_summaries[arm][
                "per_world_loop_geometry"
            ],
            "median_e_d": float(arm_summaries[arm]["median_e_d"]),
            "flips_total": int(arm_summaries[arm]["flips_total"]),
        }
        for arm in BATTERY_CELLS
    }
    pooled = {
        arm: ranking[arm]["pooled_loop_geometry"] for arm in BATTERY_CELLS
    }
    below_1x = bool(pooled["ts_lam1n_1x"] < pooled["two_stage"])
    inversion_4x = bool(pooled["ts_lam1n_4x"] >= pooled["ts_v2ridge_4x"])
    inversion_hold = bool(inversion_4x and below_1x)
    lean_a_hold = bool(signature_hold and inversion_hold)
    pivot_triggered = bool(not inversion_4x)

    two_stage_persisted = float(leg5_two_stage["pooled_loop_geometry"])
    if abs(pooled["two_stage"] - two_stage_persisted) > 0.005:
        raise RuntimeError(
            f"two_stage pooled {pooled['two_stage']:.4f} diverges from the "
            f"Leg 5 persisted {two_stage_persisted:.4f}"
        )
    lam1n_1x_persisted = float(
        leg8_decision["bias_ledger"]["loop_transport"][
            "two_stage_lever_pooled"
        ]
    )
    if abs(pooled["ts_lam1n_1x"] - lam1n_1x_persisted) > 0.005:
        raise RuntimeError(
            f"ts_lam1n_1x pooled {pooled['ts_lam1n_1x']:.4f} diverges from "
            f"the Leg 8 persisted {lam1n_1x_persisted:.4f}"
        )

    # ---- UNREGISTERED-SECONDARY: lam1n-referenced ranking ----
    secondary_pooled = {
        arm: float(
            secondary_world[secondary_world["arm"] == arm][
                "loop_action_geometry_lam1nref"
            ].mean()
        )
        for arm in BATTERY_ARMS
    }
    secondary_inversion_4x = bool(
        secondary_pooled["ts_lam1n_4x"] >= secondary_pooled["ts_v2ridge_4x"]
    )
    secondary_below_1x = bool(
        secondary_pooled["ts_lam1n_1x"] < secondary_pooled["two_stage"]
    )
    reference_shift = {
        f"{int(budget)}x": float(
            secondary_world[
                secondary_world["arm"] == f"reference_shift_{int(budget)}x"
            ]["loop_action_geometry_lam1nref"].mean()
        )
        for budget in BUDGETS
    }
    if pivot_triggered and secondary_inversion_4x:
        pivot_qualification = (
            "REFERENCE-BIAS LOCALIZATION: the registered (V2-paired) "
            "inversion is absent at 4x, but the same construction against "
            "the lam1n-fitted oracle reference DOES invert -- the floor "
            "localizes to ridge bias retained by the V2-fitted pairing "
            "endpoint rather than to the estimator side; the registered "
            "pivot still fires (leans adjudicate on the registered column "
            "only), with this localization recorded"
        )
    elif pivot_triggered:
        pivot_qualification = (
            "no reference-bias rescue: the inversion is absent on BOTH the "
            "registered V2-paired column and the lam1n-referenced "
            "secondary column"
        )
    else:
        pivot_qualification = "not applicable (registered inversion holds)"

    # ---- Arm B: gap attribution ----
    swap_author = _author_level(
        swap_rows, ["gap_v2", "gap_i", "gap_ii", "e_d_true_v2",
                    "e_orc_true", "e_i_true", "e_ii_true"], []
    )
    attribution_rows = []
    attribution: dict[str, Any] = {}
    for world in HIGH_GAP_WORLDS:
        scoped = swap_author[swap_author["world"] == world]
        gap_v2 = float(scoped["gap_v2"].median())
        gap_i = float(scoped["gap_i"].median())
        gap_ii = float(scoped["gap_ii"].median())
        content_effect = 0.5 * ((gap_v2 - gap_i) + gap_ii)
        weight_effect = 0.5 * ((gap_v2 - gap_ii) + gap_i)
        share = content_effect / gap_v2 if gap_v2 > 0 else float("nan")
        entry = {
            "world": world,
            "gap_v2": gap_v2,
            "gap_i_oracle_content_disc_weights": gap_i,
            "gap_ii_disc_content_oracle_weights": gap_ii,
            "content_effect": content_effect,
            "weight_effect": weight_effect,
            "basis_content_share": share,
            "leg8_persisted_gap_v2": float(
                leg8_decision["alignment"]["per_world_gap_v2"][world]
            ),
            "n_author_reps": int(len(scoped)),
        }
        attribution_rows.append(entry)
        attribution[world] = entry
    lean_b_worlds = sum(
        1
        for world in HIGH_GAP_WORLDS
        if attribution[world]["basis_content_share"] >= LEAN_B_SHARE_BAR
    )
    lean_b_hold = bool(lean_b_worlds >= LEAN_B_MIN_WORLDS)

    # ---- Arm C: partition verdict ----
    part_metrics = [
        "e_orc_true_latent_1x",
        "e_orc_true_env_1x",
        "e_orc_true_env62_1x",
        "e_orc_true_latent_4x",
        "e_orc_true_env_4x",
        "scale_lsq_1x",
        "reference_gap_latent",
        "reference_gap_env",
    ]
    part_author = _author_level(partition_rows, part_metrics, ["estimator"])
    partition_table = {}
    for estimator in ESTIMATORS:
        scoped = part_author[part_author["estimator"] == estimator]
        partition_table[estimator] = {
            f"median_{name}": float(scoped[name].median())
            for name in part_metrics
        }
    lam1n_latent = partition_table["lam1n"]["median_e_orc_true_latent_1x"]
    if abs(lam1n_latent - LEG8_PARTITION_LAM1N_1X) > 1e-6:
        raise RuntimeError(
            f"partition lam1n latent 1x {lam1n_latent:.6f} diverges from "
            f"the Leg 8 persisted {LEG8_PARTITION_LAM1N_1X:.6f}"
        )
    lam1n_env = partition_table["lam1n"]["median_e_orc_true_env_1x"]
    lean_c_hold = bool(lam1n_env <= LEAN_C_BAR)
    p_env_values = [gate["p_env_measured_1x"] for gate in gates
                    if gate["world"] == PARTITION_WORLD]

    # ---- outcome ----
    leans_held = sum([lean_a_hold, lean_b_hold, lean_c_hold])
    if pivot_triggered:
        outcome = (
            "PIVOT_BIAS_VARIANCE_ACCOUNT_DIES_NO_INVERSION_AT_4X_"
            "NEXT_CONDITIONING_PROFILE_LEG"
        )
        account_verdict = "DEAD"
    elif lean_a_hold:
        outcome = (
            "BIAS_VARIANCE_EQUILIBRIUM_CONFIRMED_RANKING_INVERTS_AT_4X"
        )
        account_verdict = "CONFIRMED"
    else:
        outcome = (
            "RANKING_INVERTS_AT_4X_BUT_SIGNATURE_INCOMPLETE_MIXED_VERDICT"
        )
        account_verdict = "MIXED"

    # ---- persist final artifacts ----
    cells.sort_values(
        ["estimator", "budget", "world", "repetition", "author", "view"]
    ).to_csv(args.output / "bv_cells.csv", index=False)
    panel_rows.sort_values(
        [
            "estimator",
            "budget",
            "world",
            "repetition",
            "author",
            "view",
            "realization",
        ]
    ).to_csv(args.output / "bv_panel_rows.csv", index=False)
    bv_summary_frame.to_csv(args.output / "bv_summary.csv", index=False)
    swap_rows.sort_values(
        ["world", "repetition", "author", "view"]
    ).to_csv(args.output / "gap_swap_rows.csv", index=False)
    pd.DataFrame(attribution_rows).to_csv(
        args.output / "gap_attribution.csv", index=False
    )
    partition_rows.sort_values(
        ["estimator", "repetition", "author", "view"]
    ).to_csv(args.output / "partition_reference_rows.csv", index=False)
    battery_loop.sort_values(
        ["arm", "world", "repetition", "author", "view"]
    ).to_csv(args.output / "battery_per_loop_metrics.csv", index=False)
    battery_world.sort_values(["arm", "world", "repetition"]).to_csv(
        args.output / "battery_world_rep_metrics.csv", index=False
    )
    secondary_world.sort_values(["arm", "world", "repetition"]).to_csv(
        args.output / "battery_secondary_lam1nref_world.csv", index=False
    )
    secondary_loop.sort_values(
        ["arm", "world", "repetition", "author", "view"]
    ).to_csv(args.output / "battery_secondary_lam1nref_rows.csv", index=False)
    validation.to_csv(args.output / "v2_validation.csv", index=False)
    for name, frame in checks.items():
        frame.sort_values(["world", "repetition"]).to_csv(
            args.output / f"{name}_crosscheck.csv", index=False
        )

    decision = {
        "estimand_id": "SUICA_M4_D_LEG9_BIAS_VARIANCE",
        "tier": "EXPLORATORY",
        "config_seed": int(config["seed"]),
        "outcome": outcome,
        "bias_variance_account_verdict": account_verdict,
        "design": {
            "arm_a": (
                "R=8 fresh path realizations of the frozen law per "
                "world-rep (Leg 7 offset mechanism; realization 0 = the "
                "canonical battery panels at each budget, gated) x "
                "estimators {v2ridge (V2 semantics), lam1n (penalty = "
                "hazard_ridge * I, intercept-exempt), unpen (penalty 0; "
                "Leg 8 flex fitter)} x budgets {1x = 120, 4x = 480 "
                "events}; every estimator paired against ITS OWN "
                "oracle-basis twin at the oracle-forced route; per-cell "
                "exact split total = bias^2 + var with reference scale "
                "||mean_r D_orc_r||; then the full two-stage 5x8 battery "
                "with each estimator as the stage-2 refit at both budgets "
                "(stage 1 = Leg 5 stage 1 bit-exact in all six batteries; "
                "stage-2 data = canonical realization-0 panels)"
            ),
            "arm_b": (
                "row-norm content swap at the oracle-forced route, V2 "
                "estimator semantics, 1x battery panels, three high-gap "
                "worlds: swap_i = oracle row directions + discovered row "
                "norms (width 7); swap_ii = discovered row directions + "
                "oracle row norms (width 12-13); attribution = symmetric "
                "two-factor (Shapley) main effects on world-level "
                "author-median gaps: content = .5*((gap_v2 - gap_i) + "
                "gap_ii), weights = .5*((gap_v2 - gap_ii) + gap_i), "
                "content + weights = gap_v2 exactly"
            ),
            "arm_c": (
                "partition envelope correction: generated_next is masked "
                "by an exogenous envelope whose stationary marginal is "
                "exactly .62 (P(env') = .24*env + .4712, fixed point .62; "
                "menu == envelope in this world, so p_env is measured per "
                "world-rep as mean menu occupancy of the 1x cal+sel "
                "panels); corrected reference D_true_env = p_env * D_true"
            ),
            "n_panels": N_PANELS,
            "budgets": list(BUDGETS),
            "battery_cells": {
                arm: {
                    "estimator": BATTERY_CELLS[arm][0],
                    "stage2_budget": BATTERY_CELLS[arm][1],
                }
                for arm in BATTERY_CELLS
            },
        },
        "faithfulness": faithfulness,
        "bias_variance": {
            "pooled_median_table": {
                f"{estimator}_{int(budget)}x": {
                    "bias_rel": _pooled_median(estimator, budget, "bias_rel"),
                    "var_rel": _pooled_median(estimator, budget, "var_rel"),
                    "total_rel": _pooled_median(
                        estimator, budget, "total_rel"
                    ),
                    "bias_share": _pooled_median(
                        estimator, budget, "bias_share"
                    ),
                    "mean_paired_per_panel": _pooled_median(
                        estimator, budget, "mean_paired_per_panel"
                    ),
                }
                for estimator in ESTIMATORS
                for budget in BUDGETS
            },
            "signature_at_1x": signature,
            "signature_hold": signature_hold,
        },
        "ranking": {
            "table": ranking,
            "leg5_two_stage_persisted": two_stage_persisted,
            "leg8_ts_lam1n_1x_persisted": lam1n_1x_persisted,
            "below_at_1x": below_1x,
            "inversion_at_4x": inversion_4x,
            "inversion_hold": inversion_hold,
        },
        "unregistered_secondary_lam1n_reference": {
            "label": (
                "UNREGISTERED-SECONDARY (coordinator addition; no "
                "adjudication weight): every paired statistic recomputed "
                "against the lam1n-fitted oracle reference (same "
                "realizations, same budgets; reuses Arm A's lam1n "
                "oracle-side fits -- no extra compute); battery loop "
                "geometry against reference loops D_orc_lam1n @ G_orc @ "
                "C_orc at the arm's stage-2 budget"
            ),
            "pooled_loop_geometry_lam1nref": secondary_pooled,
            "inversion_at_4x_lam1nref": secondary_inversion_4x,
            "below_at_1x_lam1nref": secondary_below_1x,
            "reference_shift_geometry_vs_v2_oracle": reference_shift,
            "decomposition_columns": (
                "bv_cells.csv: *_lam1nref columns per cell"
            ),
        },
        "gap_attribution": {
            "per_world": attribution,
            "worlds_with_content_share_ge_070": int(lean_b_worlds),
        },
        "partition_reference": {
            "per_estimator_medians": partition_table,
            "p_env_measured_1x_range": [
                float(np.min(p_env_values)),
                float(np.max(p_env_values)),
            ],
            "p_env_stationary_analytic": ENV_STATIONARY,
            "leg8_persisted_lam1n_latent_1x": LEG8_PARTITION_LAM1N_1X,
            "leg4_reference_gap_latent_flagged": 0.645,
        },
        "lean_a": {
            "registered": (
                "unpen/lam1n show lower bias + higher variance than V2 "
                "ridge at 1x AND the two-stage ranking INVERTS at 4x "
                "(two-stage+lam1n >= two-stage+V2 at 4x while below at 1x)"
            ),
            "signature_hold": signature_hold,
            "inversion_hold": inversion_hold,
            "hold": lean_a_hold,
        },
        "lean_b": {
            "registered": (
                "basis-content >= 70% of the gap in >= 2/3 high-gap worlds"
            ),
            "per_world_share": {
                world: attribution[world]["basis_content_share"]
                for world in HIGH_GAP_WORLDS
            },
            "worlds_passing": int(lean_b_worlds),
            "bar": LEAN_B_SHARE_BAR,
            "hold": lean_b_hold,
        },
        "lean_c": {
            "registered": (
                "partition .592 -> <= .30 under corrected reference "
                "(lam1n natural 1x law-level bias)"
            ),
            "latent_value": lam1n_latent,
            "corrected_value": lam1n_env,
            "bar": LEAN_C_BAR,
            "hold": lean_c_hold,
        },
        "leans_held": int(leans_held),
        "pivot_if": {
            "registered": (
                "no inversion at 4x -> the bias-variance account DIES; "
                "next instrument = the conditioning profile persisted at "
                "results/m4_d_bias_anatomy/conditioning_rows.csv elevated "
                "to a full leg"
            ),
            "triggered": pivot_triggered,
            "qualification_unregistered_secondary": pivot_qualification,
            "registered_next_instrument": (
                "information-operator conditioning profile "
                "(results/m4_d_bias_anatomy/conditioning_rows.csv)"
            ),
        },
        "claim_boundary": (
            "Finite synthetic M4-C.2 worlds only; truth-referenced "
            "estimator diagnostics throughout (oracle basis, oracle-forced "
            "routes, generator-law derivatives, generator-privileged fresh "
            "realizations of the frozen law, and the generator's envelope "
            "constant are consumed as references), so nothing here is an "
            "operational rescue of chart transport or a reopened gate; the "
            "lam1n-referenced pairing column is UNREGISTERED-SECONDARY "
            "with no adjudication weight; the V1/V2 and C3.3 NO-GO "
            "decisions stand; no natural-text, personality, emotion, or "
            "clinical claim; EXPLORATORY tier under the 2026-08-01 "
            "open-exploration directive."
        ),
        "battery_structure_totals": {
            "stage2_lstsq_fallbacks": int(
                sum(row["stage2_lstsq_fallbacks"] for row in structures)
            ),
        },
    }
    with (args.output / "decision.json").open("w", encoding="utf-8") as f:
        json.dump(decision, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "outcome": outcome,
                "account_verdict": account_verdict,
                "pooled_ranking": pooled,
                "signature_hold": signature_hold,
                "inversion_at_4x": inversion_4x,
                "lean_a_hold": lean_a_hold,
                "lean_b_hold": lean_b_hold,
                "lean_c_hold": lean_c_hold,
                "pivot_triggered": pivot_triggered,
                "secondary_pooled_lam1nref": secondary_pooled,
                "content_shares": {
                    world: attribution[world]["basis_content_share"]
                    for world in HIGH_GAP_WORLDS
                },
                "partition_lam1n_latent_to_env": [
                    lam1n_latent,
                    lam1n_env,
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m4_chart_ecology.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results" / "m4_d_bias_variance",
    )
    parser.add_argument("--chunk-start", type=int, default=None)
    parser.add_argument("--chunk-stop", type=int, default=None)
    parser.add_argument(
        "--worlds",
        type=str,
        default=None,
        help="comma-separated subset of LOOP_WORLDS (default: all)",
    )
    parser.add_argument("--assemble", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    started = time.time()
    config = leg3._load(args.config)
    spec = M4ChartEcologySpec(**config["base_spec"])

    if args.smoke:
        args.output = ROOT / "results" / "_smoke_m4_d_bias_variance"
        worlds = [PARTITION_WORLD, "endogenous_creation_expansion"]
        _run_chunk(args, config, spec, (0,), worlds)
        print(
            f"[smoke done] partials under {args.output} "
            f"({time.time() - started:.0f}s)",
            flush=True,
        )
        return
    if args.assemble:
        _assemble(args, config)
        print(f"[assembled] total {time.time() - started:.0f}s", flush=True)
        return
    if args.chunk_start is None or args.chunk_stop is None:
        raise SystemExit(
            "provide --chunk-start/--chunk-stop for a run chunk, "
            "--assemble to adjudicate, or --smoke"
        )
    worlds = (
        list(LOOP_WORLDS)
        if args.worlds is None
        else [world.strip() for world in args.worlds.split(",")]
    )
    for world in worlds:
        if world not in LOOP_WORLDS:
            raise SystemExit(f"unknown world {world}")
    repetitions = tuple(range(args.chunk_start, args.chunk_stop))
    _run_chunk(args, config, spec, repetitions, worlds)
    print(f"[done] total {time.time() - started:.0f}s", flush=True)


if __name__ == "__main__":
    main()
